#!/usr/bin/env python3
"""souji-rev-pin — durable revision resolution for lane evidence runners.

Round 19 (C2). A record's `measured_commit` is only honest when the revision
it names is (a) a full 40-hex commit id, (b) reachable from a durable ref —
`refs/heads`, `refs/tags` or `refs/remotes`, explicitly never `refs/jj/*`
(the r17 receipt-root rule) — and (c) the tracked paths the record claims to
measure have the same bytes at that revision as in the working tree.

A revision that fails any check is refused with exit 2 and a typed message;
callers must refuse before writing a record. This tool is a resolution
helper, not a verdict: it never decides whether a measurement is sufficient.

Sources (opened 2026-10-21):
  S079 git-rev-parse(1) — a revision may be named by a symbolic ref; the
       durable check therefore rejects HEAD and branch names.
  S080 git-for-each-ref(1) — refnamespaces can be selected explicitly, which
       is how refs/jj is excluded by construction.
  S081 git-diff(1) — `--quiet` exits 1 on differences and 0 otherwise.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
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


class Refusal(Exception):
    """A revision the runner must not record."""


def _env():
    env = dict(os.environ)
    env.update({
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_CONFIG_NOSYSTEM": "1",
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

    abs_paths = []
    for path in measured_paths:
        norm = os.path.normpath(path)
        if os.path.isabs(norm) or norm.startswith(".."):
            raise Refusal("measured path %r escapes the repository" % path)
        abs_paths.append(norm)
    diff = _git(root, "diff", "--quiet", rev, "--", *abs_paths, check=False)
    if diff.returncode == 1:
        raise Refusal(
            "tracked measured paths differ from %s (a record must not claim "
            "bytes the revision does not contain)" % rev
        )
    if diff.returncode != 0:
        raise Refusal(
            "git diff failed for measured paths: %s"
            % diff.stderr.decode("utf-8", "replace").strip()[:200]
        )
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
