#!/usr/bin/env python3
"""souji-rev-pin — durable revision resolution for lane evidence runners.

Round 19 introduced full durable IDs. Round 20 additionally compares the
exact owned regular-file/directory input set to committed blob bytes,
including additions and omissions. Durable roots remain refs/heads,
refs/tags and refs/remotes, never refs/jj. Callers recheck the same input
boundary before writing; external runtimes and filesystem races stay outside it.

A revision that fails any check is refused with exit 2 and a typed message;
callers must refuse before writing a record. This tool is a resolution
helper, not a verdict: it never decides whether a measurement is sufficient.

Sources (opened 2026-10-21):
  S089 git(1) — repository-selection environment can override -C.
  S091 git-rev-parse(1) — verifies an object, not its durability.
  S092 git-for-each-ref(1) — selects namespaces; durability is lane policy.
  S093 git-diff(1) — quiet status covers only selected paths. The r20
       snapshot compares raw blobs and enumerates bounded directories.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile

COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
DURABLE_NAMESPACES = ("refs/heads", "refs/tags", "refs/remotes")
GIT_CONFIG = [
    "-c", "maintenance.auto=false",
    "-c", "core.fsmonitor=false",
    "-c", "core.hooksPath=/dev/null",
]


class Refusal(ValueError):
    """A revision the runner must not record."""


def _env():
    # Repository selection/configuration belongs to the supplied root, never
    # an inherited GIT_DIR, GIT_WORK_TREE, alternate object store or index.
    env = {key: value for key, value in os.environ.items()
           if not key.startswith("GIT_")}
    env.update({
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_NO_LAZY_FETCH": "1",
        "GIT_NO_REPLACE_OBJECTS": "1",
        "LC_ALL": "C",
    })
    return env


def _git(root, *args, check=True):
    proc = subprocess.run(
        ["git", "-C", root, *GIT_CONFIG, *args],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=_env(),
    )
    if check and proc.returncode != 0:
        raise Refusal(
            "git %s failed: %s"
            % (args[0], proc.stderr.decode("utf-8", "replace").strip()[:200])
        )
    return proc


def durable_tips(root):
    """Commit tips of refs/heads, refs/tags and refs/remotes (peeled tags)."""
    proc = _git(
        root, "for-each-ref",
        "--format=%(objectname) %(*objectname) %(refname)",
        *DURABLE_NAMESPACES,
    )
    tips = []
    for line in proc.stdout.decode("utf-8", "replace").splitlines():
        parts = line.split(" ", 2)
        if len(parts) < 2:
            continue
        obj, peeled = parts[0], parts[1]
        tips.append(peeled or obj)
    return [tip for tip in tips if COMMIT_RE.match(tip)]


def input_snapshot(root, rev, paths):
    """Bind a bounded owned file/directory set to exact committed blob bytes.

    Re-enumerate the directories on every invocation, including untracked and
    ignored files: an added counted entry must not disappear behind git diff.
    This is not a filesystem sandbox or an external-runtime attestation.
    """
    root = os.path.abspath(root)
    selected = []
    for path in paths:
        if not isinstance(path, str) or not path or os.path.isabs(path):
            raise Refusal("invalid measured path %r" % path)
        parts = path.split("/")
        if any(part in ("", ".", "..") for part in parts):
            raise Refusal("measured path %r escapes or is ambiguous" % path)
        if parts[0] in (".git", ".jj") or (
                parts[0] == "census" and (len(parts) == 1
                or parts[1].startswith("operator-sweep-"))):
            raise Refusal("protected measured path %r" % path)
        selected.append(path)
    if not selected:
        raise Refusal("no measured paths supplied")
    tree = _git(root, "ls-tree", "-r", "-z", "--full-tree", rev, "--",
                *selected).stdout
    expected = {}
    for row in tree.split(b"\0"):
        if not row:
            continue
        metadata, name = row.split(b"\t", 1)
        mode, kind, oid = metadata.split()
        relative = os.fsdecode(name)
        if kind != b"blob" or mode not in (b"100644", b"100755"):
            raise Refusal("nonregular committed measured input %s" % relative)
        expected[relative] = hashlib.sha256(
            _git(root, "cat-file", "blob", oid.decode("ascii")).stdout
        ).hexdigest()
    actual = {}

    def capture(relative):
        absolute = os.path.join(root, relative)
        # Check every parent without following a symlink into another surface.
        current = root
        for component in relative.split("/"):
            current = os.path.join(current, component)
            if stat.S_ISLNK(os.lstat(current).st_mode):
                raise Refusal("symlink measured input %s" % relative)
        fd = os.open(absolute, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
        with os.fdopen(fd, "rb") as handle:
            if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
                raise Refusal("nonregular measured input %s" % relative)
            actual[relative] = hashlib.file_digest(handle, "sha256").hexdigest()

    def walk_error(exc):
        raise exc

    try:
        for relative in selected:
            absolute = os.path.join(root, relative)
            current = root
            for component in relative.split("/"):
                current = os.path.join(current, component)
                if stat.S_ISLNK(os.lstat(current).st_mode):
                    raise Refusal("symlink measured input %s" % relative)
            mode = os.lstat(absolute).st_mode
            if stat.S_ISLNK(mode):
                raise Refusal("symlink measured input %s" % relative)
            if stat.S_ISDIR(mode):
                for parent, dirs, files in os.walk(absolute, followlinks=False,
                                                   onerror=walk_error):
                    for name in dirs:
                        if os.path.islink(os.path.join(parent, name)):
                            raise Refusal("symlink measured directory %s" % relative)
                    for name in files:
                        capture(os.path.relpath(os.path.join(parent, name), root))
            else:
                capture(relative)
    except OSError as exc:
        raise Refusal("unreadable measured input: %s" % exc) from exc
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        added = sorted(set(actual) - set(expected))
        changed = sorted(path for path in actual.keys() & expected.keys()
                         if actual[path] != expected[path])
        raise Refusal("measured inputs differ from %s (missing=%s added=%s changed=%s)"
                      % (rev, missing, added, changed))
    return dict(sorted(actual.items()))


def resolve_durable(root, rev, measured_paths=None, tree_check=True):
    """Return the verified 40-hex revision or raise Refusal.

    tree_check=True (default) is for runners that execute or measure the
    working tree: the tracked measured paths must equal the revision's
    bytes. tree_check=False is for consumers that read every byte from the
    revision itself (e.g. count-claims); only the full-id and durable-ref
    rules apply.
    """
    measured_paths = list(measured_paths or [])
    if not isinstance(rev, str) or not rev.strip():
        raise Refusal("empty revision")
    rev = rev.strip()
    if not COMMIT_RE.match(rev):
        raise Refusal(
            "revision %r is not a full 40-hex commit id (HEAD, branch names, "
            "abbreviated ids and symrefs are refused)" % rev
        )
    proc = _git(root, "rev-parse", "--verify", "--quiet", rev + "^{commit}", check=False)
    if proc.returncode != 0:
        raise Refusal("revision %s does not resolve to a commit" % rev)
    resolved = proc.stdout.decode("utf-8", "replace").strip()
    if resolved != rev:
        raise Refusal("revision %s resolved unexpectedly to %s" % (rev, resolved))
    if tree_check and not measured_paths:
        raise Refusal("no measured paths supplied; a record must name what it measured")

    tips = durable_tips(root)
    if not tips:
        raise Refusal("repository has no durable refs (refs/heads|tags|remotes)")
    durable = False
    for tip in tips:
        anc = _git(root, "merge-base", "--is-ancestor", rev, tip, check=False)
        if anc.returncode == 0:
            durable = True
            break
    if not durable:
        raise Refusal(
            "revision %s is not reachable from refs/heads|refs/tags|refs/remotes "
            "(refs/jj is never a durable root)" % rev
        )
    if not tree_check:
        return rev

    input_snapshot(root, rev, measured_paths)
    return rev


def _mkrepo(path):
    os.makedirs(path)
    subprocess.run(["git", "init", "-q", "-b", "master", path], check=True, env=_env())
    subprocess.run(["git", "-C", path, "-c", "user.name=t", "-c", "user.email=t@t",
                    "config", "commit.gpgsign", "false"], check=True, env=_env())
    return path


def _commit(path, message):
    subprocess.run(["git", "-C", path, "add", "-A"], check=True, env=_env())
    subprocess.run(
        ["git", "-C", path, "-c", "user.name=t", "-c", "user.email=t@t",
         "commit", "-q", "-m", message],
        check=True, env=_env(),
    )
    return subprocess.check_output(
        ["git", "-C", path, "rev-parse", "HEAD"], env=_env()
    ).decode().strip()


def run_selftest():
    top = tempfile.mkdtemp(prefix="souji-rev-pin-selftest-", dir="/var/tmp")
    passed = failed = 0

    def case(name, fn):
        nonlocal passed, failed
        try:
            fn()
            passed += 1
            print("CASE\tpass\t%s" % name)
        except Exception as exc:  # noqa: BLE001 - selftest reports the reason
            failed += 1
            print("CASE\tFAIL\t%s\t%s: %s" % (name, type(exc).__name__, exc))

    def expect_refusal(fn, needle):
        try:
            fn()
        except Refusal as exc:
            if needle not in str(exc):
                raise AssertionError("refusal %r lacks %r" % (str(exc), needle))
            return
        raise AssertionError("expected a refusal containing %r" % needle)

    try:
        repo = _mkrepo(os.path.join(top, "world"))
        with open(os.path.join(repo, "tool.sh"), "w") as handle:
            handle.write("#!/bin/sh\ntrue\n")
        with open(os.path.join(repo, "record.json"), "w") as handle:
            handle.write("{}\n")
        clean = _commit(repo, "base")

        case("durable-clean-accept", lambda: (
            resolve_durable(repo, clean, ["tool.sh", "record.json"]) == clean
        ) or (_ for _ in ()).throw(AssertionError("wrong revision")))

        # A detached commit held only by refs/jj/keep is not durable.
        subprocess.run(["git", "-C", repo, "checkout", "-q", "--detach"], check=True, env=_env())
        with open(os.path.join(repo, "tool.sh"), "a") as handle:
            handle.write("# keep-only\n")
        keep_only = _commit(repo, "keep-only")
        subprocess.run(
            ["git", "-C", repo, "update-ref", "refs/jj/keep/keep-only", keep_only],
            check=True, env=_env(),
        )
        subprocess.run(["git", "-C", repo, "checkout", "-q", "master"], check=True, env=_env())
        case(
            "keep-only-refuse",
            lambda: expect_refusal(
                lambda: resolve_durable(repo, keep_only, ["tool.sh"]),
                "not reachable",
            ),
        )

        # Dirty tracked path: the revision does not contain the bytes measured.
        with open(os.path.join(repo, "tool.sh"), "a") as handle:
            handle.write("# uncommitted\n")
        case(
            "dirty-tree-refuse",
            lambda: expect_refusal(
                lambda: resolve_durable(repo, clean, ["tool.sh"]),
                "differ from",
            ),
        )
        subprocess.run(["git", "-C", repo, "checkout", "-q", "--", "tool.sh"],
                       check=True, env=_env())

        case(
            "head-symref-refuse",
            lambda: expect_refusal(
                lambda: resolve_durable(repo, "HEAD", ["tool.sh"]), "40-hex"
            ),
        )
        case(
            "branch-name-refuse",
            lambda: expect_refusal(
                lambda: resolve_durable(repo, "master", ["tool.sh"]), "40-hex"
            ),
        )
        case(
            "short-id-refuse",
            lambda: expect_refusal(
                lambda: resolve_durable(repo, clean[:12], ["tool.sh"]), "40-hex"
            ),
        )
        case(
            "no-measured-paths-refuse",
            lambda: expect_refusal(
                lambda: resolve_durable(repo, clean, []), "no measured paths"
            ),
        )
        case(
            "path-escape-refuse",
            lambda: expect_refusal(
                lambda: resolve_durable(repo, clean, ["../x"]), "escapes"
            ),
        )
        case(
            "unknown-rev-refuse",
            lambda: expect_refusal(
                lambda: resolve_durable(repo, "0" * 40, ["tool.sh"]),
                "does not resolve",
            ),
        )

        # A consumer that reads every byte from the revision may name a
        # historical commit whose bytes differ from the working tree.
        with open(os.path.join(repo, "tool.sh"), "a") as handle:
            handle.write("# second\n")
        _commit(repo, "second")
        case(
            "historical-no-tree-check-accept",
            lambda: resolve_durable(repo, clean, [], tree_check=False) == clean,
        )
        case(
            "historical-tree-check-refuse",
            lambda: expect_refusal(
                lambda: resolve_durable(repo, clean, ["tool.sh"]), "differ from"
            ),
        )
    finally:
        shutil.rmtree(top, ignore_errors=True)

    print("SUMMARY total=%d failed=%d" % (passed + failed, failed))
    return 0 if failed == 0 else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--rev")
    parser.add_argument("--path", action="append", default=[])
    parser.add_argument("--no-tree-check", action="store_true",
                        help="consumer reads all bytes from the revision; skip "
                             "the working-tree comparison")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if not args.rev:
        print("souji-rev-pin: --rev is required (usage exit 2)", file=sys.stderr)
        return 2
    try:
        resolved = resolve_durable(
            os.path.abspath(args.root), args.rev, args.path,
            tree_check=not args.no_tree_check,
        )
    except Refusal as exc:
        print("souji-rev-pin: refused: %s" % exc, file=sys.stderr)
        return 2
    print(resolved)
    return 0


if __name__ == "__main__":
    sys.exit(main())
