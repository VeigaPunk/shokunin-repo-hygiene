#!/usr/bin/env python3
"""souji-evidence-cache.py — digest-bound cache-eligibility gate (r14 / C1).

Purpose
-------
Decide whether a *retained* souji measurement may be reused, using only the
dependency digests recorded with that result. Eligibility is bound to the
current bytes of the declared dependencies; an earlier green result is never
reused because it was green once.

This gate does **not** run any recorded command. It reads no command field,
and it cannot prove that the retained result was ever actually executed, or
that it was executed at the declared revision. It only answers: does the
record have the shape required for reuse, are its declared dependency bytes
unchanged, and is the retained outcome a success? A `reusable` verdict means
"no declared dependency moved at the moment of evaluation", not "the work was
verified".

CLI
---
    souji-evidence-cache.py --root DIR --record JSON
    souji-evidence-cache.py --root DIR --record JSON --require REL ...
    souji-evidence-cache.py --frozen DIR
    souji-evidence-cache.py --selftest

`--record` accepts the literal JSON object text, `@PATH` to read a UTF-8 JSON
file, or a bare filesystem path to a regular JSON file. `--root` is the
directory every dependency path is resolved against. `--require REL` is
repeatable and fixes a caller-chosen minimum dependency set: a required path
that the record does not declare is refused (`dependency-undeclared`) so the
record cannot silently narrow what is measured. `--frozen` reads
`DIR/expected.json` and re-measures a pinned snapshot. `--selftest` builds
isolated fixtures under `/var/tmp`, re-invokes this CLI as a subprocess for
every case, asserts the exact finding-id set and exit code literally, and
removes its scratch tree.

Exit codes (stable)
-------------------
    0  reusable            matched is true, dependencies are present and
                           non-empty, every declared digest is well formed,
                           every dependency resolves safely to a regular file
                           on the root's device, and every current digest
                           equals its declaration.
    1  stale / failed      the record is well formed and reusable in shape, but
                           at least one declared dependency is missing or its
                           bytes changed, and/or `matched` is false. Never
                           reuse.
    2  could-not-evaluate  the record cannot be trusted or measured: malformed
                           JSON or duplicate keys, invalid schema, a non-boolean
                           `matched`, malformed or absent
                           `measured_commit`, legacy (absent) or empty
                           dependencies, malformed declared digest,
                           non-canonical/aliased/encoded dependency key,
                           unsafe/absolute/escaping/symlink/hardlinked/
                           cross-device/non-regular/oversized/protected
                           dependency path, an unusable or protected root, an
                           undeclared required dependency, or a tampered frozen
                           snapshot.

Argparse usage errors also exit 2 (before any finding is emitted). An
unexpected internal exception is caught and reported as `internal-error` with
exit 2, never as an uncaught non-zero Python exit.

Record schema (JSON object; unknown extra keys are tolerated)
-------------------------------------------------------------
    name            non-empty string with no surrounding whitespace and no
                    non-printable characters; a label only
    matched         JSON boolean, exactly true or false. Integers are rejected
                    (so `1` cannot stand in for `true`).
    measured_commit 40 lowercase hex characters (the revision the retained
                    result claims to have measured). Required: absent, null,
                    inherited-from-HEAD, or malformed values are refused
                    rather than defaulted. The record's own value is echoed
                    unchanged in the output whenever it is well formed, so
                    every result keeps its measured revision explicit.
    dependencies    object mapping a canonical relative POSIX path to its
                    recorded sha256 (64 lowercase hex characters). Required
                    and non-empty: a legacy record with no dependencies, or
                    an empty object, has no byte binding and is refused
                    rather than treated as fresh.

Optional recognized keys `exit_code` and `expected_exit` must be integers
(booleans rejected). When present, `matched` must agree: a true match with a
nonzero exit, or a false match with a zero exit, is `verdict-false-pass` /
`verdict-false-fail` (exit 2). Any other exit_code/expected_exit
disagreement on a true match is also `verdict-false-pass`.

Dependency paths are resolved against `--root` with an fd walk:
`os.open(root, O_RDONLY|O_DIRECTORY|O_NOFOLLOW)`, then one
`os.open(part, O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC, dir_fd=current)`
per intermediate component and
`os.open(leaf, O_RDONLY|O_NOFOLLOW|O_NONBLOCK|O_CLOEXEC, dir_fd=current)` for
the leaf. The leaf fd is fstat-verified as a regular file, link count 1, and
on the root's device before any byte is read. No dependency path is reopened
by name after the walk, so a swapped ancestor cannot redirect the read.
Keys must be canonical: no leading/trailing slash, no empty component, no
`.` or `..`, no backslash, and no surrounding whitespace. A defensive
`key-alias` refuses two keys that compare equal after canonicalization
(unreachable once non-canonical keys and duplicate JSON keys are rejected).
Lone surrogates are refused (`key-invalid-encoding`). A missing dependency is
stale (`dependency-missing`, exit 1): the record is well formed and the
declared bytes are gone. A digest that differs on a present regular file is
also exit 1 (`dependency-digest-mismatch`).

Root and record-path boundary
-----------------------------
Before any open, `--root`, `--frozen DIR`, and a filesystem `--record` path
are refused *lexically first*: the `abspath` string is compared against
credential and operator trees before any filesystem access. Only if the
string itself is outside them does a componentwise `lstat` walk begin,
reading each link with `readlink` and checking the link target string against
the same trees before traversal continues. `realpath` is never called on the
full candidate, so a link that resolves into a store is refused without
resolving the rest of the path inside that store. The walk has a 40-link
bound and distinguishes protected, unreadable, non-directory, and loop
failures. The walked result is then opened with a second per-component
`O_NOFOLLOW` walk from `/`; root and record bytes are read only from that fd
(a single `lstat` of the original path detects a final symlink). A component
swapped to a symlink after the check fails closed.

Protected trees are the union of `$HOME` (from the environment), the passwd
home for the current uid, `/root`, `PI_CODING_AGENT_DIR`, each home's
`PI_CONFIG_DIR` directory (default name `.omp`) and its `agent` child, and:
`<home>/.omp/agent`, `<home>/.ssh`, `<home>/.gnupg`,
`<home>/.password-store`, `<home>/.config`, `<home>/.local/share/keyrings`,
`<home>/.aws`, `<home>/.docker`, `<home>/.kube`, `<home>/.netrc`,
`<home>/.git-credentials`, `<home>/.npmrc`, `<home>/.pypirc`,
`<home>/.pgpass`, `<home>/.mozilla`, `<home>/.thunderbird`, `<home>/.pki`,
`<home>/.var/app`, `<home>/.local/share/kwalletd`, plus `/etc`, `/proc`,
`/sys`, `/dev`. A candidate that
equals, is inside, or is an ancestor of any of these is refused, so
`--root ~` or `--root /` cannot reach agent state. A root that is itself a
symlink is refused (`root-symlink`). Component name patterns also refuse
`.git`, `.ssh`, `.gnupg`, `.aws`, `.kube`, `.password-store`, `.omp`,
`.mozilla`, `.thunderbird`, `.pki`, `.kwalletd`, `.env*`, `*credential*`,
`*secret*`, `*token*`, `*oauth*`, `id_*`, `*.pem`,
`*.key`, `*.p12`, `*.pfx`, `*.kdbx`, `auth.json`, `known_hosts`,
`.config/gh`, `.config/gcloud`, `.docker/config.json`, `.var/app`,
`.ufo/state`, and `census/operator-sweep-*`. The list is name-based and
conservative: it prevents obvious credential reads, it is not a data-loss
classifier, and it can refuse a legitimate file whose name merely looks
secret-shaped. Name patterns apply to every dependency key component but only
to the basename of an absolute root/record path, so a root such as
`/var/tmp/token-audit` is conservatively refused while a checkout beneath an
innocuous ancestor is allowed. Refused paths are never opened and their
digests are never printed.

Finding ids (stable; emitted as `finding <id>: <detail>`)
---------------------------------------------------------
level 2 (could-not-evaluate):
    root-not-directory, root-symlink, root-protected,
    record-malformed, record-schema, record-unreadable, record-protected,
    matched-false-type, measured_commit-invalid,
    dependencies-legacy, dependencies-invalid, dependencies-empty,
    dependency-digest-invalid, key-alias,
    key-noncanonical, key-invalid-encoding,
    path-invalid, path-absolute, path-escape, path-protected,
    path-symlink, path-not-directory, path-hardlink,
    dependency-not-regular, dependency-device-escape, dependency-too-large,
    dependency-unreadable, dependency-undeclared, require-invalid,
    verdict-false-pass, verdict-false-fail,
    frozen-unreadable, frozen-malformed, frozen-schema, frozen-incomplete,
    snapshot_tampered, snapshot-verdict-mismatch, internal-error
level 1 (stale / failed):
    dependency-missing, dependency-digest-mismatch, matched-false

`matched-false-type` is a `matched` value that is not a JSON boolean (for
example `1` or `"true"`). `matched-false` is a retained result that honestly
reports failure; it is well formed but never reusable. A digest mismatch or a
missing dependency is stale: the declaration is valid, the bytes no longer
match. A legacy (absent) or empty dependency map is malformed for eligibility:there is nothing to bind to, so it exits 2 rather than guessing. A level-2
finding dominates any level-1 finding.

Per-dependency evaluation is deterministic: declared keys are visited in
sorted order. Observed digests are printed only for a dependency whose bytes
were read after all path/protection/device checks passed.

Frozen snapshot mode
--------------------
    --frozen DIR

DIR contains `expected.json`:

    {
      "record": "record.json",
      "verdict": "reusable",          # reusable | stale | failed |
                                      # could-not-evaluate
      "files": {
        "record.json": "<sha256>",
        "dependency.txt": "<sha256>"
      }
    }

The input pins are verified *before* the record is evaluated: every listed
file must resolve under DIR through the same fd walk to a regular,
non-hardlinked, same-device file with a matching sha256, or the result is
`snapshot_tampered` (exit 2). The record path and every canonical dependency
path it declares must appear in `files`, or the result is `frozen-incomplete`
(exit 2). Only then is the record evaluated normally, and the resulting status
must equal `verdict` (`snapshot-verdict-mismatch`, exit 2). `expected.json`
itself is the caller-supplied trust anchor: it is not self-pinned.

Caller precondition (load-bearing)
----------------------------------
The `dependencies` digests must have been captured by the runner at
measurement time and stored inside the result. If a caller recomputes them at
retain time from the current tree, this gate will return `reusable` over
laundered bytes; it cannot detect that. Likewise `measured_commit` must be the
revision the result itself recorded: it is never defaulted from a top-level
field, HEAD, or any previous attempt, and an absent value is refused.

Non-guarantees (deliberate)
---------------------------
- `matched` is a recorded claim. A record whose digests and paths all match can
  still be a false green; this gate checks binding and consistency, not truth,
  and never proves the retained command ran.
- Only declared dependencies are measured. A record that omits a relevant file
  binds only what it declares; this is not a completeness proof and has no
  transitivity: a measured script that implicitly runs another tool or reads
  another fixture does not bind that tool or fixture. `--require` lets the
  caller raise the floor, but only the caller's list is enforced.
- Out-of-root inputs are always outside eligibility: dependency keys must be
  relative, so absolute toolchains or scripts (for example a git/shellcheck
  binary, an interpreter, or a script elsewhere in the operator tree) can
  never be declared or measured by this gate.
- The dependency digests must come from the *same execution* that produced
  `matched` and `measured_commit`. Backfilling them from a run-level field
  (such as a later `installed_sha256`) pairs a digest with a revision that was
  never measured together, and this gate cannot detect that synthesis.
- Runtime inputs (git version, shell, interpreter, environment) are not
  measured; a dependency digest says nothing about the host that ran it.
- The recorded command is never executed, by design.
- The verdict is point-in-time at evaluation. Bytes may change immediately
  after; no lock is held and no historical execution is attested.
- Digest reads are size-bounded but not time-bounded. O_NONBLOCK does not
  bound a regular file on a stalled FUSE/NFS mount, so a hostile or wedged
  mount can still delay evaluation; run the gate under an outer timeout.
- The fd walk refuses symlink redirection for dependency reads and for the
  resolved root/record open. It does not bind the protection decision to the
  opened directory inode: a directory renamed or replaced by a different real
  directory between the boundary walk and the open is not detected for
  root/record (dependencies re-check nlink/dev). Path validation and output
  emission are not atomic across processes.
- A credential store relocated by a symlink outside the lexical HOME/passwd
  tree is covered only by the name rules above; if the operator moves a store
  to an innocuously named symlink target, that target is not discovered.
"""

from __future__ import annotations

import argparse
import errno
import fnmatch
import hashlib
import json
import os
import pwd
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

EXIT_REUSABLE = 0
EXIT_STALE = 1
EXIT_COULD_NOT_EVALUATE = 2

STATUS_BY_CODE = {
    EXIT_REUSABLE: "reusable",
    EXIT_STALE: "stale",
    EXIT_COULD_NOT_EVALUATE: "could-not-evaluate",
}
VERDICTS = frozenset({"reusable", "stale", "failed", "could-not-evaluate"})
LEVEL1_FINDINGS = frozenset({
    "dependency-missing",
    "dependency-digest-mismatch",
    "matched-false",
})
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
COMMIT_RE = re.compile(r"[0-9a-f]{40}\Z")
MAX_JSON_BYTES = 16 * 1024 * 1024
MAX_DEPENDENCY_BYTES = 1 << 30
MAX_PINNED_BYTES = 1 << 30

PROTECTED_DIRS = frozenset({
    ".git", ".ssh", ".gnupg", ".aws", ".kube", ".password-store", ".omp",
    ".mozilla", ".thunderbird", ".pki", ".kwalletd",
})
PROTECTED_NAME_PATTERNS = (
    ".netrc", ".git-credentials", ".npmrc", ".pypirc", ".pgpass",
    ".env", ".env.*", "*.env", ".envrc",
    "*credential*", "*secret*", "*token*", "*oauth*",
    "id_*", "*.pem", "*.key", "*.p12", "*.pfx", "*.kdbx",
    "auth.json", "known_hosts",
)
PROTECTED_PAIRS = (
    (".config", "gh"),
    (".config", "gcloud"),
    (".config", "sops"),
    (".docker", "config.json"),
    (".ufo", "state"),
    (".var", "app"),
)
PROTECTED_ABSOLUTE = (
    ".omp/agent", ".ssh", ".gnupg", ".password-store", ".config",
    ".local/share/keyrings", ".aws", ".docker", ".kube",
    ".netrc", ".git-credentials", ".npmrc", ".pypirc", ".pgpass",
    ".mozilla", ".thunderbird", ".pki", ".var/app", ".local/share/kwalletd",
)
PROTECTED_SYSTEM = ("/etc", "/proc", "/sys", "/dev")


# ---------------------------------------------------------------- findings

def _add(findings, finding_id, detail):
    level = 1 if finding_id in LEVEL1_FINDINGS else 2
    findings.append({"id": finding_id, "level": level, "detail": detail})


def _status_for(findings):
    if any(item["level"] >= 2 for item in findings):
        return EXIT_COULD_NOT_EVALUATE
    if findings:
        return EXIT_STALE
    return EXIT_REUSABLE


def _status_name(status, findings):
    if status != EXIT_STALE:
        return STATUS_BY_CODE[status]
    if any(item["id"] == "matched-false" for item in findings):
        return "failed"
    return "stale"


# ---------------------------------------------------------------- protection

def _protected_components(parts):
    """Refuse protected directory names and operator pairs anywhere."""
    lowered = [part.lower() for part in parts]
    for part in lowered:
        if part in PROTECTED_DIRS:
            return "credential or repository metadata component %r" % part
    for index in range(len(lowered) - 1):
        pair = (lowered[index], lowered[index + 1])
        if pair in PROTECTED_PAIRS:
            return "operator or credential path %r" % "/".join(pair)
        if pair[0] == "census" and pair[1].startswith("operator-sweep-"):
            return "operator sweep path"
    return None


def _protected_name(part):
    lowered = part.lower()
    for pattern in PROTECTED_NAME_PATTERNS:
        if fnmatch.fnmatchcase(lowered, pattern):
            return "secret-shaped name %r" % part
    return None


def _protected_reason(parts):
    """Return why a relative dependency key must not be read, or None."""
    reason = _protected_components(parts)
    if reason is not None:
        return reason
    for part in parts:
        reason = _protected_name(part)
        if reason is not None:
            return reason
    return None


def _protected_absolute_reason(parts):
    """Absolute paths: directory/pair rules anywhere, name rules on basename.

    Applying the secret-shaped fnmatch patterns to every ancestor would
    refuse an ordinary checkout under a directory named e.g. `token-audit`.
    The store boundaries and directory/pair rules still cover the ancestors.
    """
    reason = _protected_components(parts)
    if reason is not None:
        return reason
    if parts:
        return _protected_name(parts[-1])
    return None


def _common(child, parent):
    try:
        return os.path.commonpath([child, parent]) == parent
    except ValueError:
        return False


def _tree_reason(candidate, trees):
    """Pure-string check: equal to, inside, or an ancestor of a protected tree."""
    for tree in trees:
        if candidate == tree or _common(candidate, tree):
            return "inside or at %s" % tree
        if _common(tree, candidate):
            return "an ancestor of %s" % tree
    return None


def _protected_trees():
    """Protected absolute trees: system paths plus every known home/store."""
    trees = list(PROTECTED_SYSTEM)
    homes = set()
    env_home = os.path.abspath(os.path.expanduser("~"))
    if os.path.isabs(env_home) and env_home != "/":
        homes.add(env_home)
    try:
        passwd_home = pwd.getpwuid(os.getuid()).pw_dir
        if passwd_home and os.path.isabs(passwd_home):
            homes.add(os.path.normpath(passwd_home))
    except (ImportError, KeyError, OSError):
        pass
    homes.add("/root")
    config = os.environ.get("PI_CONFIG_DIR")
    for home in homes:
        if os.path.isabs(home) and home != "/":
            trees.extend(os.path.join(home, rel) for rel in PROTECTED_ABSOLUTE)
            if config and not os.path.isabs(config):
                trees.append(os.path.join(home, config))
                trees.append(os.path.join(home, config, "agent"))
    if config:
        if os.path.isabs(config):
            trees.append(os.path.normpath(config))
            trees.append(os.path.join(os.path.normpath(config), "agent"))
    agent_dir = os.environ.get("PI_CODING_AGENT_DIR")
    if agent_dir:
        trees.append(os.path.abspath(agent_dir))
    seen = set()
    unique = []
    for tree in trees:
        tree = os.path.normpath(tree)
        if tree not in seen:
            seen.add(tree)
            unique.append(tree)
    return unique


def _walk_boundary(absolute, trees, depth=0):
    """Resolve one component at a time without following a link blindly.

    A link is read with readlink; its target string is checked against the
    protected trees *before* traversal continues. Recursion is bounded. This
    never calls realpath. Returns (kind, detail, walked); kind is None on
    success, otherwise one of protected / unreadable / not-directory / loop.
    """
    if depth > 40:
        return "loop", "symlink chain exceeds 40 levels", None
    parts = [part for part in absolute.split("/") if part not in ("", ".")]
    resolved = "/"
    for index, part in enumerate(parts):
        candidate = os.path.join(resolved, part)
        try:
            info = os.lstat(candidate)
        except FileNotFoundError:
            return None, None, os.path.join(resolved, *parts[index:])
        except OSError as exc:
            return "unreadable", "path cannot be traversed safely: %r (%s)" % (
                candidate, _errno_reason(exc)), None
        if stat.S_ISLNK(info.st_mode):
            try:
                target = os.readlink(candidate)
            except OSError as exc:
                return "unreadable", "symlink cannot be read: %r (%s)" % (
                    candidate, _errno_reason(exc)), None
            if os.path.isabs(target):
                target_path = os.path.normpath(target)
            else:
                target_path = os.path.normpath(os.path.join(resolved, target))
            reason = _tree_reason(target_path, trees)
            if reason is not None:
                return "protected", "symlink target %r is %s" % (
                    target_path, reason), None
            protection = _protected_absolute_reason(
                [piece for piece in target_path.split("/") if piece])
            if protection is not None:
                return "protected", "symlink target %r is %s" % (
                    target_path, protection), None
            rest = parts[index + 1:]
            return _walk_boundary(os.path.join(target_path, *rest), trees, depth + 1)
        if not stat.S_ISDIR(info.st_mode) and index != len(parts) - 1:
            return "not-directory", "path component is not a directory: %r" % candidate, None
        resolved = candidate
    return None, None, resolved


def _resolve_boundary(path):
    """Refuse protected paths lexical-first, then by a no-follow component walk.

    The lexical check happens before any filesystem access. Only if the path
    string itself is outside every protected tree is the component walk
    started, and it refuses as soon as one symlink resolves into a protected
    tree rather than resolving the full path inside it. Returns
    (kind, detail, walked); kind is None on success.
    """
    absolute = os.path.abspath(path)
    trees = _protected_trees()
    reason = _tree_reason(absolute, trees)
    if reason is not None:
        return "protected", reason, None
    return _walk_boundary(absolute, trees)


# ---------------------------------------------------------------- paths

def _classify_rel(value):
    """Return (canonical relative key, None) or (None, reason).

    Canonical means: UTF-8 encodable, no surrounding whitespace, no control
    characters, no backslash, relative, and every `/`-separated component
    non-empty and neither `.` nor `..`.
    """
    if not isinstance(value, str) or not value:
        return None, "invalid"
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        return None, "invalid-encoding"
    if value != value.strip():
        return None, "invalid"
    if any(ord(char) < 0x20 or ord(char) == 0x7F for char in value):
        return None, "invalid"
    if "\\" in value:
        return None, "noncanonical"
    if value.startswith("/"):
        return None, "absolute"
    if value.endswith("/"):
        return None, "noncanonical"
    parts = value.split("/")
    if any(part == "" for part in parts):
        return None, "noncanonical"
    if any(part == "." for part in parts):
        return None, "noncanonical"
    if any(part == ".." for part in parts):
        return None, "escape"
    return value, None


def _errno_reason(exc):
    if isinstance(exc, UnicodeEncodeError):
        return "invalid-encoding"
    number = getattr(exc, "errno", None)
    if number == errno.ELOOP:
        return "symlink"
    if number == errno.ENOTDIR:
        return "not-directory"
    if number == errno.ENOENT:
        return "missing"
    if number in (errno.EACCES, errno.EPERM):
        return "unreadable"
    if number == errno.ENAMETOOLONG:
        return "invalid"
    return "unreadable"


def _open_dir_component(directory_fd, part):
    """Open one real directory component, refusing a symlink component."""
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NOCTTY
    try:
        return os.open(part, flags, dir_fd=directory_fd), None
    except (OSError, ValueError) as exc:
        reason = _errno_reason(exc)
        if reason == "not-directory":
            try:
                info = os.stat(part, dir_fd=directory_fd, follow_symlinks=False)
            except (OSError, ValueError):
                pass
            else:
                if stat.S_ISLNK(info.st_mode):
                    reason = "symlink"
        return None, reason


def _open_leaf_checked(directory_fd, leaf, want_directory):
    """Stat a leaf without following it, then open it with O_NOFOLLOW."""
    try:
        info = os.stat(leaf, dir_fd=directory_fd, follow_symlinks=False)
    except (OSError, ValueError) as exc:
        return None, _errno_reason(exc)
    if stat.S_ISLNK(info.st_mode):
        return None, "symlink"
    if want_directory:
        if not stat.S_ISDIR(info.st_mode):
            return None, "not-directory"
    elif not stat.S_ISREG(info.st_mode):
        return None, "not-regular"
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC | os.O_NOCTTY
    if want_directory:
        flags |= os.O_DIRECTORY
    try:
        return os.open(leaf, flags, dir_fd=directory_fd), None
    except (OSError, ValueError) as exc:
        return None, _errno_reason(exc)


def _open_dir_beneath(root_fd, key):
    """Open a directory chain beneath root_fd. Returns (fd, reason)."""
    current = os.dup(root_fd)
    try:
        for part in key.split("/"):
            following, reason = _open_dir_component(current, part)
            if reason is not None:
                return None, reason
            os.close(current)
            current = following
        result, current = current, None
        return result, None
    finally:
        if current is not None:
            os.close(current)


def _open_no_symlink(path, want_directory):
    """Open an absolute path with a per-component O_NOFOLLOW walk."""
    parts = [part for part in path.split("/") if part not in ("", ".")]
    try:
        current = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    except OSError as exc:
        return None, _errno_reason(exc)
    try:
        for index, part in enumerate(parts):
            if index == len(parts) - 1:
                return _open_leaf_checked(current, part, want_directory)
            following, reason = _open_dir_component(current, part)
            if reason is not None:
                return None, reason
            os.close(current)
            current = following
        return os.dup(current), None
    finally:
        if current is not None:
            os.close(current)


def _open_regular_beneath(root_fd, root_dev, key, limit):
    """Open a regular, same-device, single-link file beneath root_fd.

    Returns (fd, reason, size). The caller owns the fd and must close it.
    """
    if "/" in key:
        directory, leaf = key.rsplit("/", 1)
        directory_fd, reason = _open_dir_beneath(root_fd, directory)
        if reason is not None:
            return None, reason, None
    else:
        directory_fd, leaf = os.dup(root_fd), key
    try:
        fd, reason = _open_leaf_checked(directory_fd, leaf, want_directory=False)
    finally:
        if directory_fd != root_fd:
            os.close(directory_fd)
    if reason is not None:
        return None, reason, None
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            os.close(fd)
            return None, "not-regular", None
        if info.st_nlink > 1:
            os.close(fd)
            return None, "hardlink", None
        if info.st_dev != root_dev:
            os.close(fd)
            return None, "device", None
        if info.st_size > limit:
            os.close(fd)
            return None, "too-large", info.st_size
        return fd, None, info.st_size
    except OSError:
        os.close(fd)
        return None, "unreadable", None


def _digest_fd(fd, limit):
    digest = hashlib.sha256()
    total = 0
    while True:
        block = os.read(fd, 1 << 20)
        if not block:
            break
        total += len(block)
        if total > limit:
            raise ValueError("dependency exceeded its size bound while being read")
        digest.update(block)
    return digest.hexdigest()


def _read_fd_text(fd, limit):
    chunks = []
    total = 0
    while True:
        block = os.read(fd, 1 << 20)
        if not block:
            break
        total += len(block)
        if total > limit:
            return None, "too-large"
        chunks.append(block)
    try:
        return b"".join(chunks).decode("utf-8"), None
    except UnicodeDecodeError:
        return None, "invalid-utf8"


def _read_path_text(path, limit):
    """Read a standalone regular file, resolved once and opened no-follow."""
    absolute = os.path.abspath(path)
    parts = [part for part in Path(absolute).parts if part not in ("/", "")]
    protection = _protected_absolute_reason(parts)
    if protection is not None:
        return None, "protected", protection
    kind, detail, walked = _resolve_boundary(absolute)
    if kind == "protected":
        return None, "protected", detail
    if kind is not None:
        return None, "unreadable", detail
    walked_parts = [part for part in walked.split("/") if part]
    protection = _protected_absolute_reason(walked_parts)
    if protection is not None:
        return None, "protected", protection
    try:
        info = os.lstat(absolute)
    except FileNotFoundError:
        return None, "missing", None
    except PermissionError:
        return None, "unreadable", None
    except OSError:
        return None, "unreadable", None
    if stat.S_ISLNK(info.st_mode):
        return None, "symlink", None
    fd, reason = _open_no_symlink(walked, want_directory=False)
    if reason is not None:
        return None, reason, None
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            return None, "not-regular", None
        if info.st_nlink > 1:
            return None, "hardlink", None
        if info.st_size > limit:
            return None, "too-large", None
        text, reason = _read_fd_text(fd, limit)
        if reason is not None:
            return None, reason, None
        return text, None, None
    except OSError:
        return None, "unreadable", None
    finally:
        os.close(fd)


# ---------------------------------------------------------------- JSON

class _DuplicateKey(ValueError):
    pass


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey(key)
        result[key] = value
    return result


def _json_or_error(text):
    try:
        return json.loads(text, object_pairs_hook=_reject_duplicate_keys), None
    except _DuplicateKey as exc:
        return None, "duplicate object key %r" % (str(exc),)
    except json.JSONDecodeError as exc:
        return None, "invalid JSON: line %d column %d: %s" % (
            exc.lineno, exc.colno, exc.msg)
    except ValueError as exc:
        return None, "invalid JSON: %s" % (exc,)


# ---------------------------------------------------------------- root

def _resolve_root(value):
    """Validate --root. Returns (resolved Path, root_fd, root_dev, findings)."""
    findings = []
    absolute = os.path.abspath(value)
    protection = _protected_absolute_reason(
        [part for part in Path(absolute).parts if part not in ("/", "")])
    if protection is not None:
        _add(findings, "root-protected", "--root is %s" % protection)
        return None, None, None, findings
    kind, detail, walked = _resolve_boundary(value)
    if kind == "protected":
        _add(findings, "root-protected", "--root is %s" % detail)
        return None, None, None, findings
    if kind is not None:
        _add(findings, "root-not-directory", "--root is not usable: %s" % detail)
        return None, None, None, findings
    try:
        info = os.lstat(absolute)
    except OSError:
        _add(findings, "root-not-directory", "--root does not exist or is inaccessible")
        return None, None, None, findings
    if stat.S_ISLNK(info.st_mode):
        _add(findings, "root-symlink", "--root is a symlink")
        return None, None, None, findings
    if not stat.S_ISDIR(info.st_mode):
        _add(findings, "root-not-directory", "--root is not a directory")
        return None, None, None, findings
    resolved = Path(walked)
    protection = _protected_absolute_reason(
        [part for part in resolved.parts if part not in ("/", "")])
    if protection is not None:
        _add(findings, "root-protected", "--root is %s" % protection)
        return None, None, None, findings
    root_fd, reason = _open_no_symlink(str(resolved), want_directory=True)
    if reason is not None:
        _add(findings, "root-not-directory",
             "--root could not be opened: %s" % reason)
        return None, None, None, findings
    try:
        info = os.fstat(root_fd)
        if not stat.S_ISDIR(info.st_mode):
            _add(findings, "root-not-directory", "--root is not a directory")
            os.close(root_fd)
            return None, None, None, findings
        return resolved, root_fd, info.st_dev, findings
    except OSError:
        os.close(root_fd)
        _add(findings, "root-not-directory", "--root could not be measured")
        return None, None, None, findings


# ---------------------------------------------------------------- record

def _record_payload(value):
    """Resolve --record. Returns (text, reason, detail)."""
    if value.lstrip().startswith("{"):
        return value, None, None
    raw = value[1:] if value.startswith("@") else value
    text, reason, detail = _read_path_text(raw, MAX_JSON_BYTES)
    if reason is not None:
        tag = "record-protected" if reason == "protected" else "record-unreadable"
        return None, tag, detail or reason
    return text, None, None


def _validate_record(obj, root):
    """Validate record shape. Returns (findings, meta)."""
    findings = []
    meta = {}
    if not isinstance(obj, dict):
        _add(findings, "record-schema", "record is not a JSON object")
        return findings, meta

    name = obj.get("name")
    if isinstance(name, str) and name and name == name.strip() and name.isprintable():
        meta["name"] = name
    else:
        _add(findings, "record-schema",
             "name must be non-empty, printable, and without surrounding whitespace")

    matched = obj.get("matched")
    if not isinstance(matched, bool):
        _add(findings, "matched-false-type",
             "matched must be a JSON boolean, got %s" % type(matched).__name__)
        matched = None
    else:
        meta["matched"] = matched

    commit = obj.get("measured_commit")
    if isinstance(commit, str) and COMMIT_RE.fullmatch(commit):
        meta["measured_commit"] = commit
    else:
        _add(findings, "measured_commit-invalid",
             "measured_commit must be 40 lowercase hex characters")

    exit_code = None
    expected_exit = None
    if "exit_code" in obj:
        exit_code = obj["exit_code"]
        if isinstance(exit_code, bool) or not isinstance(exit_code, int):
            _add(findings, "record-schema", "exit_code must be an integer, not a boolean")
            exit_code = None
        else:
            meta["exit_code"] = exit_code
    if "expected_exit" in obj:
        expected_exit = obj["expected_exit"]
        if isinstance(expected_exit, bool) or not isinstance(expected_exit, int):
            _add(findings, "record-schema",
                 "expected_exit must be an integer, not a boolean")
            expected_exit = None
        else:
            meta["expected_exit"] = expected_exit
    if matched is True and exit_code is not None and exit_code != 0:
        _add(findings, "verdict-false-pass",
             "matched=true with exit_code=%d" % exit_code)
    if matched is True and exit_code is not None and expected_exit is not None \
            and exit_code != expected_exit:
        _add(findings, "verdict-false-pass",
             "matched=true with exit_code=%d but expected_exit=%d"
             % (exit_code, expected_exit))
    if matched is False and exit_code == 0:
        _add(findings, "verdict-false-fail", "matched=false with exit_code=0")

    if "dependencies" not in obj:
        _add(findings, "dependencies-legacy",
             "record has no dependencies object; a legacy result cannot be bound to bytes")
        return findings, meta
    dependencies = obj["dependencies"]
    if not isinstance(dependencies, dict):
        _add(findings, "dependencies-invalid", "dependencies must be a JSON object")
        return findings, meta
    if not dependencies:
        _add(findings, "dependencies-empty",
             "dependencies is empty; a result with no bound dependency is not reusable")
        return findings, meta

    meta["dependencies"] = len(dependencies)
    meta["declared"] = dependencies
    meta["root"] = root
    return findings, meta


def _evaluate_dependencies(meta, findings, root_fd, root_dev):
    """Measure every declared dependency in sorted order."""
    seen = set()
    for rel in sorted(meta["declared"]):
        declared = meta["declared"][rel]
        if not isinstance(declared, str):
            _add(findings, "dependency-digest-invalid",
                 "%r: declared digest is not a string" % (rel,))
            continue
        if not SHA256_RE.fullmatch(declared):
            _add(findings, "dependency-digest-invalid",
                 "%r: declared digest is not 64 lowercase hex characters" % (rel,))
            continue
        key, reason = _classify_rel(rel)
        if reason == "invalid-encoding":
            _add(findings, "key-invalid-encoding",
                 "%r: dependency key is not UTF-8 encodable" % (rel,))
            continue
        if reason == "noncanonical":
            _add(findings, "key-noncanonical",
                 "%r: dependency key is not a canonical relative path" % (rel,))
            continue
        if reason == "absolute":
            _add(findings, "path-absolute", "%r: dependency path is absolute" % (rel,))
            continue
        if reason == "escape":
            _add(findings, "path-escape", "%r: dependency path escapes --root" % (rel,))
            continue
        if reason is not None:
            _add(findings, "path-invalid", "%r: dependency path is invalid" % (rel,))
            continue
        if key in seen:
            _add(findings, "key-alias",
                 "%r: dependency key aliases an earlier key" % (rel,))
            continue
        seen.add(key)
        protection = _protected_reason(key.split("/"))
        if protection is not None:
            _add(findings, "path-protected", "%r: %s" % (rel, protection))
            continue
        fd, reason, size = _open_regular_beneath(root_fd, root_dev, key,
                                                 MAX_DEPENDENCY_BYTES)
        if reason == "missing":
            _add(findings, "dependency-missing",
                 "%r: declared dependency is absent" % (rel,))
            continue
        if reason == "symlink":
            _add(findings, "path-symlink",
                 "%r: a path component is a symlink" % (rel,))
            continue
        if reason == "not-directory":
            _add(findings, "path-not-directory",
                 "%r: an intermediate path component is not a directory" % (rel,))
            continue
        if reason == "not-regular":
            _add(findings, "dependency-not-regular",
                 "%r: dependency is not a regular file" % (rel,))
            continue
        if reason == "hardlink":
            _add(findings, "path-hardlink",
                 "%r: dependency has more than one hard link" % (rel,))
            continue
        if reason == "device":
            _add(findings, "dependency-device-escape",
                 "%r: dependency is not on the root filesystem device" % (rel,))
            continue
        if reason == "too-large":
            _add(findings, "dependency-too-large",
                 "%r: dependency exceeds the %d-byte bound" % (rel, MAX_DEPENDENCY_BYTES))
            continue
        if reason == "unreadable":
            _add(findings, "dependency-unreadable",
                 "%r: dependency cannot be read" % (rel,))
            continue
        if reason is not None:
            _add(findings, "path-invalid", "%r: dependency path is %s" % (rel, reason))
            continue
        try:
            observed = _digest_fd(fd, MAX_DEPENDENCY_BYTES)
        except ValueError:
            _add(findings, "dependency-too-large",
                 "%r: dependency grew past the %d-byte bound"
                 % (rel, MAX_DEPENDENCY_BYTES))
            continue
        except OSError:
            _add(findings, "dependency-unreadable",
                 "%r: dependency failed while being read" % (rel,))
            continue
        finally:
            os.close(fd)
        if observed != declared:
            _add(findings, "dependency-digest-mismatch",
                 "%r: declared=%s observed=%s" % (rel, declared, observed))


def _check_required(required, meta, findings):
    declared = meta.get("declared") or {}
    for rel in required:
        key, reason = _classify_rel(rel)
        if reason is not None:
            _add(findings, "require-invalid", "%r: required path is %s" % (rel, reason))
            continue
        protection = _protected_reason(key.split("/"))
        if protection is not None:
            _add(findings, "require-invalid", "%r: required path is %s" % (rel, protection))
            continue
        if key not in declared:
            _add(findings, "dependency-undeclared",
                 "%r: required dependency is not declared by the record" % (rel,))


def evaluate(root, root_fd, root_dev, record_text, required=()):
    """Evaluate record text. Returns (status, findings, meta)."""
    findings = []
    obj, error = _json_or_error(record_text)
    if error is not None:
        _add(findings, "record-malformed", error)
        return EXIT_COULD_NOT_EVALUATE, findings, {"root": str(root)}
    schema_findings, meta = _validate_record(obj, root)
    meta["root"] = str(root)
    findings.extend(schema_findings)
    if any(item["level"] >= 2 for item in schema_findings):
        return EXIT_COULD_NOT_EVALUATE, findings, meta
    _evaluate_dependencies(meta, findings, root_fd, root_dev)
    if required:
        _check_required(required, meta, findings)
    if meta.get("matched") is False:
        _add(findings, "matched-false", "retained result reports matched=false")
    status = _status_for(findings)
    return status, findings, meta


# ---------------------------------------------------------------- frozen

def _frozen_schema_check(obj):
    """Return (normalized expected, reason)."""
    if not isinstance(obj, dict):
        return None, "expected.json is not a JSON object"
    allowed = {"record", "verdict", "files"}
    extra = set(obj) - allowed
    if extra:
        return None, "unknown expected.json key(s): %s" % ", ".join(sorted(extra))
    record, reason = _classify_rel(obj.get("record"))
    if reason is not None:
        return None, "record path is %s" % reason
    protection = _protected_reason(record.split("/"))
    if protection is not None:
        return None, "record path is %s" % protection
    verdict = obj.get("verdict")
    if verdict not in VERDICTS:
        return None, "verdict must be one of %s" % ", ".join(sorted(VERDICTS))
    files = obj.get("files")
    if not isinstance(files, dict) or not files:
        return None, "files must be a non-empty JSON object"
    pins = {}
    for rel, declared in files.items():
        key, reason = _classify_rel(rel)
        if reason is not None:
            return None, "pinned path %r is %s" % (rel, reason)
        protection = _protected_reason(key.split("/"))
        if protection is not None:
            return None, "pinned path %r is %s" % (rel, protection)
        if key in pins:
            return None, "pinned path %r duplicates a normalized path" % (rel,)
        if not isinstance(declared, str) or not SHA256_RE.fullmatch(declared):
            return None, "pin %r is not 64 lowercase hex characters" % (rel,)
        pins[key] = declared
    return {"record": record, "verdict": verdict, "files": pins}, None


def evaluate_frozen(directory):
    """Verify snapshot pins, then evaluate. Returns (status, findings, meta)."""
    findings = []
    meta = {}
    root, root_fd, root_dev, root_findings = _resolve_root(directory)
    findings.extend(root_findings)
    if root is None:
        return EXIT_COULD_NOT_EVALUATE, findings, meta
    meta["root"] = str(root)

    try:
        expected_fd, reason, _ = _open_regular_beneath(
            root_fd, root_dev, "expected.json", MAX_JSON_BYTES)
        if reason is not None:
            _add(findings, "frozen-unreadable", "expected.json: %s" % reason)
            return EXIT_COULD_NOT_EVALUATE, findings, meta
        try:
            text, reason = _read_fd_text(expected_fd, MAX_JSON_BYTES)
        finally:
            os.close(expected_fd)
        if reason is not None:
            _add(findings, "frozen-unreadable", "expected.json: %s" % reason)
            return EXIT_COULD_NOT_EVALUATE, findings, meta
        obj, error = _json_or_error(text)
        if error is not None:
            _add(findings, "frozen-malformed", error)
            return EXIT_COULD_NOT_EVALUATE, findings, meta
        expected, error = _frozen_schema_check(obj)
        if error is not None:
            _add(findings, "frozen-schema", error)
            return EXIT_COULD_NOT_EVALUATE, findings, meta
        meta["frozen_files"] = len(expected["files"])

        pins = expected["files"]
        record_rel = expected["record"]
        if record_rel not in pins:
            _add(findings, "frozen-incomplete",
                 "record %r is not pinned in expected.json" % (record_rel,))
            return EXIT_COULD_NOT_EVALUATE, findings, meta

        for rel in sorted(pins):
            declared = pins[rel]
            fd, reason, size = _open_regular_beneath(
                root_fd, root_dev, rel, MAX_PINNED_BYTES)
            if reason is not None:
                _add(findings, "snapshot_tampered",
                     "%r: pin cannot be verified (%s)" % (rel, reason))
                continue
            try:
                observed = _digest_fd(fd, MAX_PINNED_BYTES)
            except (OSError, ValueError):
                _add(findings, "snapshot_tampered",
                     "%r: pin failed while being read" % (rel,))
                continue
            finally:
                os.close(fd)
            if observed != declared:
                _add(findings, "snapshot_tampered",
                     "%r: pinned=%s observed=%s" % (rel, declared, observed))
        if findings:
            return EXIT_COULD_NOT_EVALUATE, findings, meta

        record_fd, reason, size = _open_regular_beneath(
            root_fd, root_dev, record_rel, MAX_JSON_BYTES)
        if reason is not None:
            _add(findings, "record-unreadable", "%r: %s" % (record_rel, reason))
            return EXIT_COULD_NOT_EVALUATE, findings, meta
        try:
            record_text, reason = _read_fd_text(record_fd, MAX_JSON_BYTES)
        finally:
            os.close(record_fd)
        if reason is not None:
            _add(findings, "record-unreadable", "%r: %s" % (record_rel, reason))
            return EXIT_COULD_NOT_EVALUATE, findings, meta

        parsed, error = _json_or_error(record_text)
        if error is None and isinstance(parsed, dict):
            dependencies = parsed.get("dependencies")
            if isinstance(dependencies, dict):
                pinned = set(pins)
                unpinned = []
                for rel in sorted(dependencies):
                    key, key_reason = _classify_rel(rel)
                    if key is not None and key not in pinned:
                        unpinned.append(rel)
                if unpinned:
                    _add(findings, "frozen-incomplete",
                         "dependencies not pinned in expected.json: %s"
                         % ", ".join(repr(rel) for rel in unpinned))
                    return EXIT_COULD_NOT_EVALUATE, findings, meta

        status, record_findings, record_meta = evaluate(
            root, root_fd, root_dev, record_text)
        findings.extend(record_findings)
        meta.update(record_meta)
        if status != EXIT_COULD_NOT_EVALUATE:
            observed_verdict = _status_name(status, record_findings)
            if observed_verdict != expected["verdict"]:
                _add(findings, "snapshot-verdict-mismatch",
                     "expected=%s observed=%s"
                     % (expected["verdict"], observed_verdict))
                status = EXIT_COULD_NOT_EVALUATE
        meta["frozen_files"] = len(pins)
        return status, findings, meta
    finally:
        os.close(root_fd)


# ---------------------------------------------------------------- output

def _emit(status, findings, meta):
    print("souji-evidence-cache: %s" % _status_name(status, findings))
    print("scope: declared dependency bytes only; no command execution or historical proof")
    if meta.get("root") is not None:
        print("root: %r" % str(meta["root"]))
    if meta.get("name") is not None:
        print("record_name: %s" % meta["name"])
    if meta.get("measured_commit") is not None:
        print("measured_commit: %s" % meta["measured_commit"])
    if meta.get("dependencies") is not None:
        print("dependencies: %d" % meta["dependencies"])
    if meta.get("frozen_files") is not None:
        print("frozen_files: %d" % meta["frozen_files"])
    for item in findings:
        print("finding %s: %s" % (item["id"], item["detail"]))
    return status


# ---------------------------------------------------------------- selftest

SELFTEST_COMMIT = "0123456789abcdef0123456789abcdef01234567"
SELFTEST_COMMIT_ALT = "89abcdef0123456789abcdef0123456789abcdef"


def _write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_record(path, record):
    _write_text(path, json.dumps(record, indent=2, sort_keys=True) + "\n")


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _case_root(base, name):
    root = base / name
    root.mkdir()
    _write_text(root / "src/a.txt", "alpha dependency\n")
    _write_text(root / "src/b.txt", "beta dependency\n")
    _write_text(root / "notes/unrelated.txt", "not a dependency\n")
    return root


def _record_for(root, dependencies=None, matched=True, commit=SELFTEST_COMMIT):
    if dependencies is None:
        dependencies = {
            "src/a.txt": _sha((root / "src/a.txt").read_text(encoding="utf-8")),
            "src/b.txt": _sha((root / "src/b.txt").read_text(encoding="utf-8")),
        }
    return {
        "name": "selftest",
        "matched": matched,
        "measured_commit": commit,
        "dependencies": dependencies,
    }


def _run_tool(arguments, env):
    return subprocess.run(
        [sys.executable, os.path.abspath(__file__), *arguments],
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )


def _ids(stdout):
    return sorted(re.findall(r"(?m)^finding ([a-z0-9_-]+):", stdout))


def _frozen_expected(root, record_path="record.json", verdict="reusable",
                     dependencies=("src/a.txt", "src/b.txt")):
    files = {
        "record.json": _sha((root / "record.json").read_text(encoding="utf-8")),
    }
    for rel in dependencies:
        files[rel] = _sha((root / rel).read_text(encoding="utf-8"))
    return {"record": record_path, "verdict": verdict, "files": files}


def _selftest():
    try:
        base = Path(tempfile.mkdtemp(prefix="souji-r14-cache-selftest.", dir="/var/tmp"))
    except OSError as exc:
        print("selftest-unavailable: %s" % (exc,))
        return 2
    results = []
    try:
        home = base / "home"
        home.mkdir()
        (home / ".ssh").mkdir()
        (home / ".config").mkdir()
        (home / "sub").mkdir()
        _write_text(home / ".ssh/id_ed25519", "synthetic home, never read\n")
        _write_text(home / ".config/rec.json", '{"name":"synthetic"}\n')
        env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "LC_ALL": "C",
            "TMPDIR": "/var/tmp",
            "HOME": str(home),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        cases = []

        root = _case_root(base, "positive")
        record = _record_for(root)
        cases.append((
            "positive",
            ["--root", str(root), "--record", json.dumps(record)],
            0, [],
            ["souji-evidence-cache: reusable", "measured_commit: " + SELFTEST_COMMIT,
             "dependencies: 2"],
        ))

        root = _case_root(base, "unrelated-change")
        record = _record_for(root)
        _write_text(root / "notes/unrelated.txt", "edited after the record\n")
        cases.append((
            "unrelated-change",
            ["--root", str(root), "--record", json.dumps(record)],
            0, [], ["souji-evidence-cache: reusable"],
        ))

        root = _case_root(base, "changed-dependency")
        record = _record_for(root)
        _write_text(root / "src/a.txt", "changed after the record\n")
        cases.append((
            "changed-dependency",
            ["--root", str(root), "--record", json.dumps(record)],
            1, ["dependency-digest-mismatch"],
            ["souji-evidence-cache: stale", "measured_commit: " + SELFTEST_COMMIT],
        ))

        root = _case_root(base, "missing-dependency")
        record = _record_for(root)
        (root / "src/b.txt").unlink()
        cases.append((
            "missing-dependency",
            ["--root", str(root), "--record", json.dumps(record)],
            1, ["dependency-missing"],
            ["souji-evidence-cache: stale"],
        ))

        root = _case_root(base, "symlink-dependency")
        target = root / "src/real.txt"
        _write_text(target, "alpha dependency\n")
        (root / "src/a.txt").unlink()
        os.symlink(target, root / "src/a.txt")
        record = _record_for(root, dependencies={
            "src/a.txt": _sha("alpha dependency\n"),
            "src/b.txt": _sha("beta dependency\n"),
        })
        cases.append((
            "symlink-dependency",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["path-symlink"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "symlink-ancestor")
        os.symlink(root / "src", root / "linkdir")
        record = _record_for(root, dependencies={
            "linkdir/a.txt": _sha("alpha dependency\n"),
        })
        cases.append((
            "symlink-ancestor",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["path-symlink"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "malformed-hash")
        record = _record_for(root, dependencies={
            "src/a.txt": "A" * 64,
            "src/b.txt": _sha("beta dependency\n"),
        })
        cases.append((
            "malformed-hash",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["dependency-digest-invalid"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "escape")
        _write_text(base / "escape.txt", "outside the root\n")
        record = _record_for(root, dependencies={
            "src/a.txt": _sha("alpha dependency\n"),
            "../escape.txt": _sha("outside the root\n"),
        })
        cases.append((
            "escape",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["path-escape"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "absolute-path")
        record = _record_for(root, dependencies={
            "src/a.txt": _sha("alpha dependency\n"),
            "/etc/hostname": "0" * 64,
        })
        cases.append((
            "absolute-path",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["path-absolute"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "failed")
        record = _record_for(root, matched=False)
        cases.append((
            "failed",
            ["--root", str(root), "--record", json.dumps(record)],
            1, ["matched-false"],
            ["souji-evidence-cache: failed", "measured_commit: " + SELFTEST_COMMIT],
        ))

        root = _case_root(base, "legacy")
        record = _record_for(root)
        del record["dependencies"]
        cases.append((
            "legacy",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["dependencies-legacy"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "empty-deps")
        record = _record_for(root, dependencies={})
        cases.append((
            "empty-deps",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["dependencies-empty"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "bool-int")
        record = _record_for(root)
        record["matched"] = 1
        cases.append((
            "bool-int",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["matched-false-type"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "duplicate-key")
        record = _record_for(root)
        duplicate = json.dumps(record, sort_keys=True)
        duplicate = duplicate[:-1] + ', "matched": false}\n'
        cases.append((
            "duplicate-key",
            ["--root", str(root), "--record", duplicate],
            2, ["record-malformed"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "measured-commit")
        record = _record_for(root, commit="abc123")
        cases.append((
            "measured-commit",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["measured_commit-invalid"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "not-regular")
        (root / "src/dir").mkdir()
        record = _record_for(root, dependencies={
            "src/a.txt": _sha("alpha dependency\n"),
            "src/dir": "0" * 64,
        })
        cases.append((
            "not-regular",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["dependency-not-regular"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "hardlink")
        record = _record_for(root)
        os.link(root / "src/a.txt", root / "notes/alias.txt")
        cases.append((
            "hardlink",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["path-hardlink"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "protected")
        _write_text(root / ".ssh/id_ed25519", "synthetic, never read\n")
        record = _record_for(root, dependencies={
            "src/a.txt": _sha("alpha dependency\n"),
            ".ssh/id_ed25519": "0" * 64,
        })
        cases.append((
            "protected",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["path-protected"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "record-protected")
        _write_text(root / ".ssh/record.json", json.dumps(_record_for(root)))
        cases.append((
            "record-protected",
            ["--root", str(root), "--record", str(root / ".ssh/record.json")],
            2, ["record-protected"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "root-protected")
        protected_root = root / ".ssh"
        protected_root.mkdir()
        record = _record_for(root)
        cases.append((
            "root-protected",
            ["--root", str(protected_root), "--record", json.dumps(record)],
            2, ["root-protected"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "root-symlink")
        os.symlink(root, base / "root-symlink-link")
        record = _record_for(root)
        cases.append((
            "root-symlink",
            ["--root", str(base / "root-symlink-link"), "--record", json.dumps(record)],
            2, ["root-symlink"], ["souji-evidence-cache: could-not-evaluate"],
        ))
        cases.append((
            "root-symlink-trailing-slash",
            ["--root", str(base / "root-symlink-link") + "/", "--record", json.dumps(record)],
            2, ["root-symlink"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "home-boundary")
        record = _record_for(root)
        cases.append((
            "home-root-protected",
            ["--root", str(home), "--record", json.dumps(record)],
            2, ["root-protected"], ["souji-evidence-cache: could-not-evaluate"],
        ))
        os.symlink(home, base / "home-alias")
        cases.append((
            "home-alias-root-protected",
            ["--root", str(base / "home-alias/sub"), "--record", json.dumps(record)],
            2, ["root-protected"], ["souji-evidence-cache: could-not-evaluate"],
        ))
        os.symlink(home / ".config", base / "config-alias")
        cases.append((
            "home-alias-record-protected",
            ["--root", str(root), "--record", str(base / "config-alias/rec.json")],
            2, ["record-protected"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "noncanonical-key")
        record = _record_for(root, dependencies={
            "./src/a.txt": _sha("alpha dependency\n"),
        })
        cases.append((
            "noncanonical-key",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["key-noncanonical"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "invalid-encoding")
        record_text = (
            '{"name":"surrogate","matched":true,"measured_commit":"%s",'
            '"dependencies":{"\\ud800":"%s"}}' % (SELFTEST_COMMIT, "0" * 64)
        )
        cases.append((
            "invalid-encoding",
            ["--root", str(root), "--record", record_text],
            2, ["key-invalid-encoding"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "false-pass")
        record = _record_for(root)
        record["exit_code"] = 1
        cases.append((
            "false-pass",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["verdict-false-pass"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "expected-exit-mismatch")
        record = _record_for(root)
        record["exit_code"] = 0
        record["expected_exit"] = 1
        cases.append((
            "expected-exit-mismatch",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["verdict-false-pass"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "false-fail")
        record = _record_for(root, matched=False)
        record["exit_code"] = 0
        cases.append((
            "false-fail",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["verdict-false-fail"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "too-large")
        big = root / "src/big.bin"
        with big.open("wb") as handle:
            handle.truncate((1 << 30) + 1)
        record = _record_for(root, dependencies={
            "src/a.txt": _sha("alpha dependency\n"),
            "src/big.bin": "0" * 64,
        })
        cases.append((
            "too-large",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["dependency-too-large"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "require-declared")
        record = _record_for(root)
        cases.append((
            "require-declared",
            ["--root", str(root), "--record", json.dumps(record),
             "--require", "src/a.txt"],
            0, [], ["souji-evidence-cache: reusable"],
        ))

        root = _case_root(base, "require-undeclared")
        record = _record_for(root)
        cases.append((
            "require-undeclared",
            ["--root", str(root), "--record", json.dumps(record),
             "--require", "notes/unrelated.txt"],
            2, ["dependency-undeclared"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "dependencies-invalid")
        record = _record_for(root)
        record["dependencies"] = []
        cases.append((
            "dependencies-invalid",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["dependencies-invalid"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "require-invalid")
        record = _record_for(root)
        cases.append((
            "require-invalid",
            ["--root", str(root), "--record", json.dumps(record),
             "--require", "../escape.txt"],
            2, ["require-invalid"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "root-not-directory")
        plain = base / "plain-root.txt"
        _write_text(plain, "not a directory\n")
        record = _record_for(root)
        cases.append((
            "root-not-directory",
            ["--root", str(plain), "--record", json.dumps(record)],
            2, ["root-not-directory"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "record-unreadable")
        record = _record_for(root)
        cases.append((
            "record-unreadable",
            ["--root", str(root), "--record", str(root / "absent.json")],
            2, ["record-unreadable"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "path-invalid")
        record = _record_for(root, dependencies={
            "src/a\u0001b": "0" * 64,
        })
        cases.append((
            "path-invalid",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["path-invalid"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "path-not-directory")
        record = _record_for(root, dependencies={
            "src/a.txt/child": "0" * 64,
        })
        cases.append((
            "path-not-directory",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["path-not-directory"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "frozen-unreadable")
        _write_record(root / "record.json", _record_for(root))
        cases.append((
            "frozen-unreadable",
            ["--frozen", str(root)],
            2, ["frozen-unreadable"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "frozen-malformed")
        _write_text(root / "expected.json", "{bad\n")
        cases.append((
            "frozen-malformed",
            ["--frozen", str(root)],
            2, ["frozen-malformed"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "frozen-schema")
        _write_text(root / "expected.json", "{}\n")
        cases.append((
            "frozen-schema",
            ["--frozen", str(root)],
            2, ["frozen-schema"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "alt-commit")
        record = _record_for(root, commit=SELFTEST_COMMIT_ALT)
        cases.append((
            "per-result-commit",
            ["--root", str(root), "--record", json.dumps(record)],
            0, [], ["measured_commit: " + SELFTEST_COMMIT_ALT],
        ))

        root = _case_root(base, "record-path")
        record = _record_for(root)
        _write_record(root / "record.json", record)
        cases.append((
            "record-path",
            ["--root", str(root), "--record", str(root / "record.json")],
            0, [], ["measured_commit: " + SELFTEST_COMMIT],
        ))

        root = _case_root(base, "frozen-clean")
        _write_record(root / "record.json", _record_for(root))
        _write_record(root / "expected.json", _frozen_expected(root))
        cases.append((
            "frozen-clean",
            ["--frozen", str(root)],
            0, [],
            ["souji-evidence-cache: reusable", "frozen_files: 3",
             "measured_commit: " + SELFTEST_COMMIT],
        ))

        root = _case_root(base, "frozen-tampered")
        _write_record(root / "record.json", _record_for(root))
        _write_record(root / "expected.json", _frozen_expected(root))
        _write_text(root / "src/a.txt", "tampered dependency\n")
        cases.append((
            "frozen-tampered",
            ["--frozen", str(root)],
            2, ["snapshot_tampered"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "frozen-incomplete")
        _write_record(root / "record.json", _record_for(root))
        _write_record(root / "expected.json",
                      _frozen_expected(root, dependencies=()))
        cases.append((
            "frozen-incomplete",
            ["--frozen", str(root)],
            2, ["frozen-incomplete"], ["souji-evidence-cache: could-not-evaluate"],
        ))

        root = _case_root(base, "frozen-verdict-mismatch")
        _write_record(root / "record.json", _record_for(root))
        _write_record(root / "expected.json", _frozen_expected(root, verdict="stale"))
        cases.append((
            "frozen-verdict-mismatch",
            ["--frozen", str(root)],
            2, ["snapshot-verdict-mismatch"],
            ["souji-evidence-cache: could-not-evaluate"],
        ))

        for name, arguments, want_code, want_ids, needles in cases:
            proc = _run_tool(arguments, env)
            problems = []
            if proc.returncode != want_code:
                problems.append("rc=%r want %d" % (proc.returncode, want_code))
            observed = _ids(proc.stdout)
            if observed != sorted(want_ids):
                problems.append("findings=%r want %r" % (observed, sorted(want_ids)))
            for needle in needles:
                if re.search(r"(?m)^%s$" % re.escape(needle), proc.stdout) is None:
                    problems.append("stdout missing exact line %r" % (needle,))
            results.append((name, problems, proc))
    finally:
        shutil.rmtree(base, ignore_errors=True)

    failures = 0
    for name, problems, proc in results:
        if not problems:
            continue
        failures += 1
        print("FAIL %s: %s" % (name, "; ".join(problems)))
        if proc is not None:
            if proc.stdout:
                print("  stdout:\n    " + proc.stdout.strip().replace("\n", "\n    "))
            if proc.stderr:
                print("  stderr:\n    " + proc.stderr.strip().replace("\n", "\n    "))
    print("selftest: %d/%d passed" % (len(results) - failures, len(results)))
    return 0 if failures == 0 else 1


# ---------------------------------------------------------------- main

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Digest-bound evidence-cache eligibility gate (r14 / C1).")
    parser.add_argument("--root", help="directory every dependency path resolves against")
    parser.add_argument("--record", help="record JSON text, @PATH, or a regular file path")
    parser.add_argument("--require", action="append", default=[], metavar="REL",
                        help="dependency path the record must declare (repeatable)")
    parser.add_argument("--frozen", help="snapshot directory containing expected.json")
    parser.add_argument("--selftest", action="store_true", help="run isolated self-checks")
    args = parser.parse_args(argv)

    modes = sum((bool(args.selftest), bool(args.frozen),
                 bool(args.root) or bool(args.record) or bool(args.require)))
    if modes != 1:
        parser.error("choose exactly one mode: --selftest, --frozen DIR, "
                     "or --root DIR --record JSON")
    if args.selftest or args.frozen:
        if args.require:
            parser.error("--require applies only to --root/--record evaluation")
        if args.selftest and args.frozen:
            parser.error("--selftest and --frozen are mutually exclusive")
    elif not (args.root and args.record):
        parser.error("--root and --record are required together")

    if args.selftest:
        return _selftest()

    if args.frozen:
        status, findings, meta = evaluate_frozen(args.frozen)
        return _emit(status, findings, meta)

    root, root_fd, root_dev, findings = _resolve_root(args.root)
    if root is None:
        return _emit(EXIT_COULD_NOT_EVALUATE, findings, {})
    try:
        record_text, tag, detail = _record_payload(args.record)
        if record_text is None:
            _add(findings, tag, "--record could not be read: %s" % detail)
            return _emit(EXIT_COULD_NOT_EVALUATE, findings, {})
        status, record_findings, meta = evaluate(
            root, root_fd, root_dev, record_text, tuple(args.require))
        findings.extend(record_findings)
        return _emit(status, findings, meta)
    finally:
        os.close(root_fd)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - fail closed with a stable id
        print("souji-evidence-cache: could-not-evaluate")
        print("finding internal-error: %s: %s" % (type(exc).__name__, exc))
        sys.exit(EXIT_COULD_NOT_EVALUATE)
