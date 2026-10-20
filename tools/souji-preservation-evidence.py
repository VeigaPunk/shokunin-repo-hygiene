#!/usr/bin/env python3
"""souji-preservation-evidence.py — declared paired-evidence admission gate (r15 / C2).

Purpose
-------
Decide whether a *declared* paired-evidence record is admissible as
preservation evidence for the round-15 Git-config refusal repair. The record
must demonstrate the PASS/FAIL/PASS arc: the pre-harm baseline
(a31642d) passed the benign controls, the harm baseline (cc21683, whose
installed tool is the value-blind r14 refusal build) failed them, and the
changed tool passes every config case while the unchanged r14 namespace
fixture passes 12/12.

This gate does **not** run any recorded command. It re-parses the recorded
fixture stdout (CASE/SUMMARY rows) and reconciles it against the structured
fields, recomputes totals and per-case expectations from its own pinned
literal tables, and re-measures the declared fixture/tool bytes under
`--root`. An `admissible` verdict means "the declaration is internally
consistent, bound to the measured bytes, and discriminating", not "the run
really happened" — declared-record consistency only.

CLI
---
    souji-preservation-evidence.py --root DIR --record JSON
    souji-preservation-evidence.py --frozen DIR
    souji-preservation-evidence.py --selftest

`--record` accepts the literal JSON object text, `@PATH` to read a UTF-8 JSON
file, or a bare filesystem path to a regular JSON file. `--root` is the lane
checkout the declared fixture/tool paths are re-measured against. `--frozen`
reads `DIR/expected.json` and re-measures a pinned snapshot. `--selftest`
builds isolated synthetic roots under `/var/tmp`, re-invokes this CLI as a
subprocess for every case, asserts the exact finding-id set and exit code
literally, and removes its scratch tree.

Exit codes (stable)
-------------------
    0  clean               the record is well formed, every declared byte
                           binding re-measures equal, the case-id multiset in
                           each arm equals the pinned expected universe, and
                           the recorded verdicts discriminate: benign
                           controls FAIL on the harm baseline (exit 1 with a
                           concrete recorded reason, not exit 2/timeout) and
                           PASS on both preharm and changed arms; refusal
                           controls PASS on harm + changed and FAIL on
                           preharm; namespace controls pass 12/12.
    1  failed              the record is well formed and consistent but the
                           evidence does not admit preservation: a missing
                           expected case id, an unexpected case status, a
                           benign failure without a concrete recorded reason,
                           or an arm that cannot serve as red/green evidence
                           (exit 2, timeout, or inconsistent-with-evidence).
    2  could-not-evaluate  the record cannot be trusted or measured:
                           malformed JSON or duplicate keys, invalid schema,
                           missing/unknown arms, absent structured fields,
                           duplicate/unknown/zero case ids, summary or
                           structured-vs-parsed disagreement, a declared
                           digest that differs from the measured bytes, a
                           baseline/preharm/namespace identity that differs
                           from the pinned literals, an
                           unsafe/absolute/escaping/symlink/protected path,
                           an unusable root, a tampered frozen snapshot, or
                           an internal error.

Argparse usage errors also exit 2. An unexpected internal exception is
caught and reported as `internal-error` with exit 2.

Record schema (JSON object; unknown extra keys are tolerated)
-------------------------------------------------------------
    schema                     literal "souji-preservation-record-v1"
    declared_consistency_only  literal true; this record type never claims
                               authenticated execution
    measured_commit            40 lowercase hex; the revision `changed`
                               claims to have measured
    fixture                    {"path": "tests/fixtures/r15-census-config.py",
                                "sha256": 64hex} — measured under --root
    namespace_fixture          {"path": "tests/fixtures/r14-census-boundary.py",
                                "sha256": 64hex} — measured under --root AND
                               equal to the pinned r14 digest
    runs                       object with exactly the arms
                               baseline_preharm / baseline / changed
    namespace_controls         one run object over the R14C2-01..12 universe

Each run object:
    tool        {"commit": 40hex, "sha256": 64hex} — baseline and
                baseline_preharm identities must equal the pinned literals;
                changed.tool.sha256 must equal the measured bytes of
                tools/souji-census.sh under --root and changed.tool.commit
                must equal measured_commit
    exit_code   integer 0..255 (booleans rejected)
    timed_out   JSON boolean; true requires exit 124 or 137 and no cases
    stdout      recorded fixture stdout; the checker re-parses CASE and
                SUMMARY rows itself. Declared structured fields that
                disagree with the parsed transcript are could-not-evaluate.
    cases       list of {"id", "status"} where status is "pass" or "fail";
                optional "detail" string. The declared multiset must equal
                the parsed CASE multiset exactly.
    summary     {"total": int, "failed": int} — must equal the recomputed
                counts from the parsed CASE rows.

Pinned literals (independent oracles, never derived from the record or any
fixture --list/EXPECTED_IDS/CASES/SUMMARY output):
    PREHARM_COMMIT  a31642d14006830ec62edf40b0354c3699728c4a
    PREHARM_SHA256  6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026
    BASELINE_COMMIT cc2168325768d5356a82c039dcdf787377c55784
    BASELINE_SHA256 fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9
    NAMESPACE_SHA256 e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2
    NAMESPACE_IDS   R14C2-01 .. R14C2-12
    CONFIG_BENIGN_IDS / CONFIG_REFUSAL_IDS   the r15 config case universe

Expected per-case status is recomputed, never trusted (r15 matrix):

    benign   (01,04,06,09,10,12,13,15,16): preharm pass, baseline FAIL, changed pass
    refusal  (02,03,07,11,14,17,19):       preharm fail, baseline pass, changed pass
    safety   (08):                         preharm fail, baseline FAIL, changed pass
    preserve (05 pass / 18,20 fail preharm; all pass baseline + changed)
    namespace (R14C2-01..12): pass on changed

A refusal PASS must carry a non-"none" observed_finding token and every
other PASS must carry observed_finding=none, else `case-finding-mismatch`.

Finding ids (stable; emitted as `finding <id>: <detail>`)
---------------------------------------------------------
level 2 (could-not-evaluate):
    root-not-directory, root-symlink, root-protected,
    record-malformed, record-schema, record-unreadable, record-protected,
    commit-invalid, digest-invalid, pinned-mismatch, binding-digest-mismatch,
    run-missing, run-unknown, run-inconsistent, stdout-parse,
    summary-mismatch, case-duplicate, case-unknown, case-set-empty,
    key-alias, key-noncanonical, key-invalid-encoding,
    path-invalid, path-noncanonical, path-absolute, path-escape,
    path-protected, path-symlink, path-not-directory, path-hardlink,
    binding-not-regular, binding-device-escape, binding-too-large,
    binding-unreadable, frozen-unreadable, frozen-malformed, frozen-schema,
    frozen-incomplete, snapshot_tampered, snapshot-verdict-mismatch,
    internal-error
level 1 (failed honest evidence):
    case-missing, case-status-unexpected, case-finding-mismatch,
    baseline-reason-weak, run-not-evaluable, baseline-not-red,
    preharm-not-green, changed-not-green, namespace-incomplete,
    binding-missing

A level-2 finding dominates any level-1 finding.

Root, record and binding-path boundary
--------------------------------------
Before any open, `--root`, `--frozen DIR`, and a filesystem `--record` path
are refused *lexically first*: the `abspath` string is compared against
credential and operator trees before any filesystem access. Only if the
string itself is outside them does a componentwise `lstat` walk begin,
reading each link with `readlink` and checking the link target string
against the same trees before traversal continues. `realpath` is never
called on the full candidate. The walk has a 40-link bound. The walked
result is then opened with a second per-component `O_NOFOLLOW` walk from
`/`; root and record bytes are read only from that fd.

Protected trees are the union of `$HOME` (from the environment), the passwd
home for the current uid, `/root`, `PI_CODING_AGENT_DIR`, each home's
`PI_CONFIG_DIR` directory (default name `.omp`) and its `agent` child, and:
`<home>/.omp/agent`, `<home>/.ssh`, `<home>/.gnupg`,
`<home>/.password-store`, `<home>/.config`, `<home>/.local/share/keyrings`,
`<home>/.aws`, `<home>/.docker`, `<home>/.kube`, `<home>/.netrc`,
`<home>/.git-credentials`, `<home>/.npmrc`, `<home>/.pypirc`,
`<home>/.pgpass`, `<home>/.mozilla`, `<home>/.thunderbird`, `<home>/.pki`,
`<home>/.var/app`, `<home>/.local/share/kwalletd`, plus `/etc`, `/proc`,
`/sys`, `/dev`. A candidate that equals, is inside, or is an ancestor of any
of these is refused, so `--root ~` or `--root /` cannot reach agent state.
Component name patterns also refuse `.git`, `.ssh`, `.gnupg`, `.aws`,
`.kube`, `.password-store`, `.omp`, `.mozilla`, `.thunderbird`, `.pki`,
`.kwalletd`, `.env*`, `*credential*`, `*secret*`, `*token*`, `*oauth*`,
`id_*`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.kdbx`, `auth.json`,
`known_hosts`, `.config/gh`, `.config/gcloud`, `.docker/config.json`,
`.var/app`, `.ufo/state`, and `census/operator-sweep-*`. The list is
name-based and conservative; it can refuse a legitimate file whose name
merely looks secret-shaped. Name patterns apply to every binding path
component but only to the basename of an absolute root/record path.
Refused paths are never opened and their digests are never printed.

Frozen snapshot mode
--------------------
    --frozen DIR --root DIR

DIR contains `expected.json` and the pinned record file:

    {
      "record": "record.json",
      "record_sha256": "<sha256 of DIR/record.json>",
      "verdict": "clean",             # clean | failed | could-not-evaluate
      "files": {                      # pins for paths measured under --root
        "tools/souji-census.sh": "<sha256>",
        "tests/fixtures/r15-census-config.py": "<sha256>",
        "tests/fixtures/r14-census-boundary.py": "<sha256>"
      }
    }

The pins are verified *before* the record is evaluated: the record bytes
under DIR must hash to `record_sha256` and every `files` entry must
resolve under --root through the same fd walk to a regular,
non-hardlinked, same-device file with a matching sha256, or the result is
`snapshot_tampered` (exit 2). Every measured path the record references
(the two fixture paths and `tools/souji-census.sh`) must appear in
`files`, or the result is `frozen-incomplete` (exit 2). Only then is the
record evaluated normally, and a verdict other than could-not-evaluate
must equal `verdict` (`snapshot-verdict-mismatch`, exit 2).
`expected.json` itself is the caller-supplied trust anchor: it is not
self-pinned.

Non-guarantees (deliberate)
---------------------------
- Declared consistency only. A fabricated record whose digests, transcript
  and structured fields all agree can still be a false admission: this gate
  checks binding and discrimination, not that the recorded run executed.
  `declared_consistency_only` is required true so the record itself states
  this.
- Only the two fixture paths and `tools/souji-census.sh` are re-measured
  under `--root`. The baseline tools live outside the checkout and are bound
  by pinned literals only; `measured_commit` is format-checked, never
  resolved against git history.
- Transcript stdout is parsed and reconciled but not authenticated; a
  consistent forgery is indistinguishable from an honest transcript.
- The pinned case universe is this checker's literal table, agreed with the
  fixture author; it is never derived from fixture `--list`, `EXPECTED_IDS`,
  `CASES`, or `SUMMARY` output, so a weakened fixture cannot widen its own
  green.
- Runtime inputs (git version, shell, interpreter, environment) are not
  measured; a digest says nothing about the host that ran it.
- The recorded command is never executed, by design.
- Digest reads are size-bounded but not time-bounded. O_NONBLOCK does not
  bound a regular file on a stalled FUSE/NFS mount, so a hostile or wedged
  mount can still delay evaluation; run the gate under an outer timeout.
- The fd walk refuses symlink redirection for binding reads and for the
  resolved root/record open. It does not bind the protection decision to the
  opened directory inode: a directory renamed or replaced by a different
  real directory between the boundary walk and the open is not detected for
  root/record (bindings re-check nlink/dev). Path validation and output
  emission are not atomic across processes.
- A credential store relocated by a symlink outside the lexical HOME/passwd
  tree is covered only by the name rules above; if the operator moves a
  store to an innocuously named symlink target, that target is not
  discovered.
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

EXIT_CLEAN = 0
EXIT_FAILED = 1
EXIT_COULD_NOT_EVALUATE = 2

STATUS_BY_CODE = {
    EXIT_CLEAN: "clean",
    EXIT_FAILED: "failed",
    EXIT_COULD_NOT_EVALUATE: "could-not-evaluate",
}
VERDICTS = frozenset({"clean", "failed", "could-not-evaluate"})

LEVEL1_FINDINGS = frozenset({
    "case-missing",
    "case-status-unexpected",
    "baseline-reason-weak",
    "run-not-evaluable",
    "baseline-not-red",
    "preharm-not-green",
    "changed-not-green",
    "namespace-incomplete",
    "binding-missing",
    "case-finding-mismatch",
})

SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
COMMIT_RE = re.compile(r"[0-9a-f]{40}\Z")
CASE_ID_RE = re.compile(r"[A-Z0-9][A-Z0-9-]*\Z")
TOOL_LINE_RE = re.compile(r"\tTOOL\t(\S+)\tsha256=([0-9a-f]{64})\Z")
TOOL_KIND_RE = re.compile(r"\tTOOL-KIND\t([^\t]+)\Z")
CASE_LINE_RE = re.compile(r"\tCASE\t([^\t]+)\t(PASS|FAIL)\t(.*)\Z")
SUMMARY_LINE_RE = re.compile(r"\tSUMMARY\ttotal=([0-9]+)\tfailed=([0-9]+)\Z")

MAX_JSON_BYTES = 16 * 1024 * 1024
MAX_BIND_BYTES = 1 << 30
MAX_PINNED_BYTES = 1 << 30
MAX_STDOUT_CHARS = 1 << 22
MAX_DETAIL_CHARS = 512

SCHEMA_ID = "souji-preservation-record-v1"

PREHARM_COMMIT = "a31642d14006830ec62edf40b0354c3699728c4a"
PREHARM_SHA256 = "6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026"
BASELINE_COMMIT = "cc2168325768d5356a82c039dcdf787377c55784"
BASELINE_SHA256 = "fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9"

CONFIG_FIXTURE_PATH = "tests/fixtures/r15-census-config.py"
NAMESPACE_FIXTURE_PATH = "tests/fixtures/r14-census-boundary.py"
NAMESPACE_SHA256 = "e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2"
INSTALLED_TOOL_PATH = "tools/souji-census.sh"

# Independent literal case universe for the r15 config fixture as revised in
# round 16 (tests/fixtures/r15-census-config.py at 0a70bef). Round-16 L1
# re-pin (routed R4): the r15 table predated the fixture's first execution;
# these classes are the per-arm statuses observed in
# census/round-16/c1-matrix-final.json and are pinned here as literals. The
# checker never derives them from fixture --list/EXPECTED_IDS/CASES/SUMMARY.
#
# Four classes (preharm a31642d, harm cc21683; changed is always PASS):
#   benign   preharm PASS, harm FAIL (value-blind r14 refusals restored)
#   refusal  preharm FAIL, harm PASS (namespace guard r14 already had)
#   safety   FAIL on both baselines (guards, degrade rows and oracles neither
#            baseline met)
#   preserve PASS on both baselines
CONFIG_BENIGN_IDS = (
    "R15CFG-01",  # include/includeIf safe targets
    "R15CFG-04",  # hooks/fsmonitor inert; excludes/attributes (and XDG) honored
    "R15CFG-06",  # remote.*.promisor all spellings on a complete repo
    "R15CFG-07",  # invalid promisor booleans: git's own status-unverifiable row
    "R15CFG-09",  # extensions.partialClone false/empty/origin (remote names)
    "R15CFG-10",  # worktreeConfig false + true with benign config.worktree
    "R15CFG-12",  # alternateRefsCommand, any value
    "R15CFG-13",  # unbound filter.* drivers never executed
    "R15CFG-15",  # key-parse false positives stay benign
    "R15CFG-16",  # mixed fleet benign rows unchanged
    "R15CFG-20",  # --compare on the mixed fleet
)
CONFIG_REFUSAL_IDS = (
    "R15CFG-02",  # include/includeIf targets into the store
    "R15CFG-11",  # hostile config.worktree; attributes/excludes into the store
    "R15CFG-17",  # mixed fleet containing one unsafe repo
)
CONFIG_SAFETY_IDS = (
    "R15CFG-03",  # could-not-evaluate config: per-repo error row (degrade)
    "R15CFG-08",  # hooks/fsmonitor sentinels and GIT_NO_LAZY_FETCH pin
    "R15CFG-14",  # bound filter: status skipped, driver never runs
    "R15CFG-18",  # poisoned HOME/.gitconfig + GIT_* env on the mixed fleet
    "R15CFG-19",  # --root store / ancestor refusal without echoing the store
)
# Preserve ids and their pinned preharm (a31642d) statuses; harm and
# changed are both "pass" for every preserve id.
CONFIG_PRESERVE_PREHARM = {
    "R15CFG-05": "pass",  # dirty fidelity predates the overrides
}
CONFIG_PRESERVE_IDS = tuple(sorted(CONFIG_PRESERVE_PREHARM))
CONFIG_IDS = frozenset(CONFIG_BENIGN_IDS) | frozenset(CONFIG_REFUSAL_IDS) \
    | frozenset(CONFIG_SAFETY_IDS) | frozenset(CONFIG_PRESERVE_IDS)
# The exact set that must FAIL on the harm baseline (benign + safety).
CONFIG_HARM_FAILS = frozenset(CONFIG_BENIGN_IDS) | frozenset(CONFIG_SAFETY_IDS)
# Changed-arm PASS rows that must carry a concrete finding token (a
# path-protected refusal, a config-unsupported degrade or a status-skipped
# diagnostic); every other PASS must carry observed_finding=none.
CONFIG_TOKEN_IDS = (
    "R15CFG-02", "R15CFG-03", "R15CFG-11", "R15CFG-14", "R15CFG-17", "R15CFG-19",
)
NAMESPACE_IDS = (
    "R14C2-01", "R14C2-02", "R14C2-03", "R14C2-04", "R14C2-05", "R14C2-06",
    "R14C2-07", "R14C2-08", "R14C2-09", "R14C2-10", "R14C2-11", "R14C2-12",
)

# A recorded baseline FAIL counts as a concrete reason only when its CASE
# detail carries one of the fixture's observed-evidence tokens.
REASON_TOKENS = ("observed_exit=", "observed_finding=")

# Recorded argv tokens that would make an arm a partial (subset) run.
SUBSET_TOKENS = frozenset({"--case", "--list"})

ARM_IDS = ("baseline_preharm", "baseline", "changed")

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
        return EXIT_FAILED
    return EXIT_CLEAN


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
    """Return why a relative binding key must not be read, or None."""
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

    Returns (kind, detail, walked); kind is None on success.
    """
    absolute = os.path.abspath(path)
    trees = _protected_trees()
    reason = _tree_reason(absolute, trees)
    if reason is not None:
        return "protected", reason, None
    return _walk_boundary(absolute, trees)


# ---------------------------------------------------------------- paths

def _classify_rel(value):
    """Return (canonical relative key, None) or (None, reason)."""
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
            raise ValueError("bound file exceeded its size bound while being read")
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


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


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


# ---------------------------------------------------------------- transcripts

TOOL_LINE_RE = re.compile(r"TOOL\t(\S+)\tsha256=([0-9a-f]{64})\Z")
TOOL_KIND_RE = re.compile(r"TOOL-KIND\t([^\t]+)\Z")
# The real fixture's detail carries TAB-separated observed_exit/
# observed_finding fields (round-16 fix: the r15 `[^\t]*` made every real
# CASE line unparseable and contradicted the `\tobserved_finding=` token rule).
CASE_LINE_RE = re.compile(r"CASE\t([^\t]+)\t(PASS|FAIL)\t(.*)\Z")
SUMMARY_LINE_RE = re.compile(r"SUMMARY\ttotal=([0-9]+)\tfailed=([0-9]+)\Z")
RECORD_PREFIXES = ("TOOL\t", "TOOL-KIND\t", "CASE\t", "SUMMARY\t")


def _parse_transcript(text):
    """Re-parse a recorded fixture stdout.

    Returns (cases, summary, tool_sha, problems) where cases is a list of
    (id, status, detail) in transcript order and summary is (total, failed)
    or None. problems are consistency violations, not status verdicts.
    """
    cases = []
    summary = None
    tool_sha = None
    problems = []
    seen_summary = False
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    for lineno, line in enumerate(lines, 1):
        if not line or not any(line.startswith(prefix) for prefix in RECORD_PREFIXES):
            problems.append("line %d is not a TOOL/TOOL-KIND/CASE/SUMMARY record" % lineno)
            continue
        match = TOOL_LINE_RE.match(line)
        if match:
            if cases or seen_summary:
                problems.append("TOOL line %d appears after CASE/SUMMARY rows" % lineno)
            if tool_sha is not None:
                problems.append("duplicate TOOL line %d" % lineno)
            else:
                tool_sha = match.group(2)
            continue
        if TOOL_KIND_RE.match(line):
            if cases or seen_summary:
                problems.append("TOOL-KIND line %d appears after CASE/SUMMARY rows" % lineno)
            continue
        match = CASE_LINE_RE.match(line)
        if match:
            if seen_summary:
                problems.append("CASE line %d appears after SUMMARY" % lineno)
            cases.append((match.group(1), match.group(2), match.group(3)))
            continue
        match = SUMMARY_LINE_RE.match(line)
        if match:
            if seen_summary:
                problems.append("duplicate SUMMARY line %d" % lineno)
            seen_summary = True
            summary = (int(match.group(1)), int(match.group(2)))
            continue
        problems.append("line %d does not match a known record shape" % lineno)
    if summary is None:
        problems.append("transcript has no SUMMARY line")
    return cases, summary, tool_sha, problems


def _validate_ref(obj, key, findings):
    """Validate a {"path", "sha256"} member. Returns (canonical_rel, sha)."""
    value = obj.get(key)
    if not isinstance(value, dict):
        _add(findings, "record-schema", "%s must be an object" % key)
        return None, None
    rel, reason = _classify_rel(value.get("path"))
    if reason is not None:
        finding = {
            "invalid": "path-invalid",
            "invalid-encoding": "key-invalid-encoding",
            "noncanonical": "path-noncanonical",
            "absolute": "path-absolute",
            "escape": "path-escape",
        }[reason]
        _add(findings, finding, "%s.path %r is %s" % (key, value.get("path"), reason))
        rel = None
    sha = value.get("sha256")
    if not isinstance(sha, str) or not SHA256_RE.fullmatch(sha):
        _add(findings, "digest-invalid",
             "%s.sha256 must be 64 lowercase hex characters" % key)
        sha = None
    if rel is not None:
        protection = _protected_reason(rel.split("/"))
        if protection is not None:
            _add(findings, "path-protected", "%s.path %r: %s" % (key, rel, protection))
            rel = None
    return rel, sha


def _validate_run(arm, value, findings):
    """Validate one arm run object. Returns meta or None."""
    meta = {"cases": [], "summary": None}
    if not isinstance(value, dict):
        _add(findings, "record-schema", "runs.%s must be an object" % arm)
        return None
    tool = value.get("tool")
    if not isinstance(tool, dict):
        _add(findings, "record-schema", "runs.%s.tool must be an object" % arm)
    else:
        commit = tool.get("commit")
        if not isinstance(commit, str) or not COMMIT_RE.fullmatch(commit):
            _add(findings, "commit-invalid",
                 "runs.%s.tool.commit must be 40 lowercase hex" % arm)
        else:
            meta["tool_commit"] = commit
        sha = tool.get("sha256")
        if not isinstance(sha, str) or not SHA256_RE.fullmatch(sha):
            _add(findings, "digest-invalid",
                 "runs.%s.tool.sha256 must be 64 lowercase hex" % arm)
        else:
            meta["tool_sha256"] = sha
    exit_code = value.get("exit_code")
    if not _is_int(exit_code) or not 0 <= exit_code <= 255:
        _add(findings, "record-schema",
             "runs.%s.exit_code must be an integer in 0..255" % arm)
    else:
        meta["exit_code"] = exit_code
    timed_out = value.get("timed_out")
    if not isinstance(timed_out, bool):
        _add(findings, "record-schema", "runs.%s.timed_out must be a boolean" % arm)
    else:
        meta["timed_out"] = timed_out
    stdout = value.get("stdout")
    if not isinstance(stdout, str):
        _add(findings, "record-schema", "runs.%s.stdout must be a string" % arm)
    elif len(stdout) > MAX_STDOUT_CHARS:
        _add(findings, "record-schema", "runs.%s.stdout exceeds %d characters"
             % (arm, MAX_STDOUT_CHARS))
    else:
        meta["stdout"] = stdout
    cases = value.get("cases")
    if not isinstance(cases, list):
        _add(findings, "record-schema", "runs.%s.cases must be a list" % arm)
    else:
        declared = []
        for index, item in enumerate(cases):
            if not isinstance(item, dict):
                _add(findings, "record-schema",
                     "runs.%s.cases[%d] must be an object" % (arm, index))
                continue
            cid = item.get("id")
            status = item.get("status")
            if not isinstance(cid, str) or not cid:
                _add(findings, "record-schema",
                     "runs.%s.cases[%d].id must be a non-empty string" % (arm, index))
                continue
            if status not in ("pass", "fail"):
                _add(findings, "record-schema",
                     "runs.%s.cases[%d].status must be 'pass' or 'fail'" % (arm, index))
                continue
            detail = item.get("detail", "")
            if not isinstance(detail, str) or len(detail) > 4096 or not detail.isprintable() and detail:
                _add(findings, "record-schema",
                     "runs.%s.cases[%d].detail must be printable text" % (arm, index))
                continue
            declared.append((cid, status, detail))
        meta["cases"] = declared
    summary = value.get("summary")
    if not isinstance(summary, dict) \
            or not _is_int(summary.get("total")) \
            or not _is_int(summary.get("failed")) \
            or summary.get("total", 0) < 0 or summary.get("failed", 0) < 0:
        _add(findings, "record-schema",
             "runs.%s.summary must hold nonnegative integer total/failed" % arm)
    else:
        meta["summary"] = (summary["total"], summary["failed"])

    argv = value.get("argv")
    if argv is not None:
        if not isinstance(argv, list) \
                or not all(isinstance(item, str) for item in argv):
            _add(findings, "record-schema",
                 "runs.%s.argv must be a list of strings" % arm)
        else:
            meta["argv"] = argv
    for stream in ("stdout", "stderr"):
        sha_key = stream + "_sha256"
        size_key = stream + "_bytes_total"
        trunc_key = stream + "_truncated"
        if sha_key in value:
            sha = value[sha_key]
            if not isinstance(sha, str) or not SHA256_RE.fullmatch(sha):
                _add(findings, "record-schema",
                     "runs.%s.%s must be 64 lowercase hex" % (arm, sha_key))
            else:
                meta[sha_key] = sha
        if size_key in value:
            size = value[size_key]
            if not _is_int(size) or size < 0:
                _add(findings, "record-schema",
                     "runs.%s.%s must be a nonnegative integer" % (arm, size_key))
            else:
                meta[size_key] = size
        if trunc_key in value:
            truncated = value[trunc_key]
            if not isinstance(truncated, bool):
                _add(findings, "record-schema",
                     "runs.%s.%s must be a boolean" % (arm, trunc_key))
            else:
                meta[trunc_key] = truncated
    if "stderr" in value and not isinstance(value.get("stderr"), str):
        _add(findings, "record-schema", "runs.%s.stderr must be a string" % arm)
    return meta


def _validate_record(obj):
    """Validate record shape. Returns (findings, meta)."""
    findings = []
    meta = {}
    if not isinstance(obj, dict):
        _add(findings, "record-schema", "record is not a JSON object")
        return findings, meta

    if obj.get("schema") != SCHEMA_ID:
        _add(findings, "record-schema",
             "schema must be the literal %r" % SCHEMA_ID)
    if obj.get("declared_consistency_only") is not True:
        _add(findings, "record-schema",
             "declared_consistency_only must be the literal true")
    commit = obj.get("measured_commit")
    if isinstance(commit, str) and COMMIT_RE.fullmatch(commit):
        meta["measured_commit"] = commit
    else:
        _add(findings, "commit-invalid",
             "measured_commit must be 40 lowercase hex characters")

    fixture_rel, fixture_sha = _validate_ref(obj, "fixture", findings)
    if fixture_rel is not None and fixture_rel != CONFIG_FIXTURE_PATH:
        _add(findings, "record-schema",
             "fixture.path must be the literal %r" % CONFIG_FIXTURE_PATH)
        fixture_rel = None
    if fixture_rel is not None and fixture_sha is not None:
        meta["fixture"] = (fixture_rel, fixture_sha)

    ns_rel, ns_sha = _validate_ref(obj, "namespace_fixture", findings)
    if ns_rel is not None and ns_rel != NAMESPACE_FIXTURE_PATH:
        _add(findings, "record-schema",
             "namespace_fixture.path must be the literal %r" % NAMESPACE_FIXTURE_PATH)
        ns_rel = None
    if ns_rel is not None and ns_sha is not None:
        meta["namespace_fixture"] = (ns_rel, ns_sha)
        if ns_sha != NAMESPACE_SHA256:
            _add(findings, "pinned-mismatch",
                 "namespace_fixture.sha256=%s is not the pinned r14 digest %s"
                 % (ns_sha, NAMESPACE_SHA256))

    runs = obj.get("runs")
    if not isinstance(runs, dict):
        _add(findings, "run-missing", "runs must be an object of three arms")
    else:
        unknown = sorted(set(runs) - set(ARM_IDS))
        for arm in unknown:
            _add(findings, "run-unknown", "runs.%s is not a known arm" % arm)
        for arm in ARM_IDS:
            if arm not in runs:
                _add(findings, "run-missing", "runs.%s is absent" % arm)
                continue
            meta[arm] = _validate_run(arm, runs[arm], findings)

    if "namespace_controls" not in obj:
        _add(findings, "run-missing", "namespace_controls is absent")
    else:
        ns = _validate_run("namespace_controls",
                           obj.get("namespace_controls"), findings)
        if ns is not None:
            meta["namespace_controls"] = ns

    return findings, meta


# ---------------------------------------------------------------- bindings

def _measure_binding(root_fd, root_dev, label, rel, findings):
    """Digest one declared binding path under root_fd.

    Returns the observed sha256 or None; appends a finding on failure.
    """
    fd, reason, size = _open_regular_beneath(root_fd, root_dev, rel, MAX_BIND_BYTES)
    if reason == "missing":
        _add(findings, "binding-missing", "%s: %r is absent" % (label, rel))
        return None
    if reason == "symlink":
        _add(findings, "path-symlink", "%s: %r has a symlink component" % (label, rel))
        return None
    if reason == "not-directory":
        _add(findings, "path-not-directory",
             "%s: %r has a non-directory component" % (label, rel))
        return None
    if reason == "not-regular":
        _add(findings, "binding-not-regular", "%s: %r is not a regular file" % (label, rel))
        return None
    if reason == "hardlink":
        _add(findings, "path-hardlink", "%s: %r has more than one hard link" % (label, rel))
        return None
    if reason == "device":
        _add(findings, "binding-device-escape",
             "%s: %r is not on the root filesystem device" % (label, rel))
        return None
    if reason == "too-large":
        _add(findings, "binding-too-large",
             "%s: %r exceeds the %d-byte bound" % (label, rel, MAX_BIND_BYTES))
        return None
    if reason is not None:
        _add(findings, "binding-unreadable", "%s: %r cannot be read (%s)" % (label, rel, reason))
        return None
    try:
        try:
            return _digest_fd(fd, MAX_BIND_BYTES)
        except (OSError, ValueError):
            _add(findings, "binding-unreadable", "%s: %r failed while being read" % (label, rel))
            return None
    finally:
        os.close(fd)


def _check_bindings(meta, findings, root_fd, root_dev):
    """Re-measure declared fixture/tool bytes and check pinned identities."""
    if "fixture" in meta:
        rel, declared = meta["fixture"]
        observed = _measure_binding(root_fd, root_dev, "fixture", rel, findings)
        if observed is not None and observed != declared:
            _add(findings, "binding-digest-mismatch",
                 "fixture: declared=%s observed=%s" % (declared, observed))
    if "namespace_fixture" in meta:
        rel, declared = meta["namespace_fixture"]
        observed = _measure_binding(root_fd, root_dev, "namespace_fixture", rel, findings)
        if observed is not None and observed != declared:
            _add(findings, "binding-digest-mismatch",
                 "namespace_fixture: declared=%s observed=%s" % (declared, observed))
    observed_tool = _measure_binding(
        root_fd, root_dev, "installed-tool", INSTALLED_TOOL_PATH, findings)

    for arm in ("baseline_preharm", "baseline"):
        run = meta.get(arm)
        if run is None:
            continue
        want_commit = PREHARM_COMMIT if arm == "baseline_preharm" else BASELINE_COMMIT
        want_sha = PREHARM_SHA256 if arm == "baseline_preharm" else BASELINE_SHA256
        if run.get("tool_commit") is not None and run["tool_commit"] != want_commit:
            _add(findings, "pinned-mismatch",
                 "runs.%s.tool.commit=%s is not the pinned %s"
                 % (arm, run["tool_commit"], want_commit))
        if run.get("tool_sha256") is not None and run["tool_sha256"] != want_sha:
            _add(findings, "pinned-mismatch",
                 "runs.%s.tool.sha256=%s is not the pinned %s"
                 % (arm, run["tool_sha256"], want_sha))

    changed = meta.get("changed")
    if changed is not None:
        if changed.get("tool_commit") is not None \
                and meta.get("measured_commit") is not None \
                and changed["tool_commit"] != meta["measured_commit"]:
            _add(findings, "run-inconsistent",
                 "runs.changed.tool.commit=%s differs from measured_commit=%s"
                 % (changed["tool_commit"], meta["measured_commit"]))
        if changed.get("tool_sha256") is not None and observed_tool is not None \
                and changed["tool_sha256"] != observed_tool:
            _add(findings, "binding-digest-mismatch",
                 "runs.changed.tool.sha256=%s observed=%s"
                 % (changed["tool_sha256"], observed_tool))
        if changed.get("tool_sha256") in (BASELINE_SHA256, PREHARM_SHA256):
            _add(findings, "pinned-mismatch",
                 "runs.changed binds a pinned baseline digest; "
                 "a repair artifact cannot equal the harm or preharm build")

    ns = meta.get("namespace_controls")
    if ns is not None and ns.get("tool_sha256") is not None \
            and observed_tool is not None \
            and ns["tool_sha256"] != observed_tool:
        _add(findings, "binding-digest-mismatch",
             "namespace_controls.tool.sha256=%s observed=%s"
             % (ns["tool_sha256"], observed_tool))
    if ns is not None and ns.get("tool_commit") is not None \
            and meta.get("measured_commit") is not None \
            and ns["tool_commit"] != meta["measured_commit"]:
        _add(findings, "run-inconsistent",
             "namespace_controls.tool.commit=%s differs from measured_commit=%s"
             % (ns["tool_commit"], meta["measured_commit"]))


# ---------------------------------------------------------------- arms

def _expected_status(arm, cid):
    """Independent oracle: the status a well-formed run must record."""
    if arm == "namespace_controls":
        return "pass"
    if arm == "baseline_preharm":
        if cid in CONFIG_BENIGN_IDS:
            return "pass"
        if cid in CONFIG_PRESERVE_PREHARM:
            return CONFIG_PRESERVE_PREHARM[cid]
        return "fail"
    if arm == "baseline":
        if cid in CONFIG_HARM_FAILS:
            return "fail"
        return "pass"
    return "pass"  # changed


def _expected_universe(arm):
    return NAMESPACE_IDS if arm == "namespace_controls" else CONFIG_IDS


def _eval_arm(arm, run, findings):
    """Reconcile and judge one arm. run is the validated meta dict."""
    label = "namespace_controls" if arm == "namespace_controls" else "runs.%s" % arm
    parsed_cases = []
    parsed_summary = None
    transcript_sha = None
    stdout = run.get("stdout")
    if run.get("argv") is not None:
        bad_tokens = [token for token in run["argv"]
                      if token in SUBSET_TOKENS or token.startswith("--case=")]
        if bad_tokens:
            _add(findings, "run-inconsistent",
                 "%s: recorded argv carries subset selector(s) %s"
                 % (label, ", ".join(sorted(set(bad_tokens)))))
    if stdout is not None and run.get("stdout_sha256") is not None:
        if _sha_text(stdout) != run["stdout_sha256"]:
            _add(findings, "run-inconsistent",
                 "%s: stdout_sha256 does not match stdout bytes" % label)
    if stdout is not None and run.get("stdout_bytes_total") is not None:
        if len(stdout.encode("utf-8")) != run["stdout_bytes_total"]:
            _add(findings, "run-inconsistent",
                 "%s: stdout_bytes_total does not match stdout bytes" % label)
    exit_code = run.get("exit_code")
    timed_out = run.get("timed_out")
    will_eval = (
        exit_code in (0, 1) and timed_out is False
        and run.get("stdout_truncated") is not True
    )
    if stdout is not None:
        parsed_cases, parsed_summary, transcript_sha, problems = _parse_transcript(stdout)
        # Transcript-shape problems are only meaningful on an arm that claims
        # evaluability; a could-not-evaluate or timed-out arm legitimately
        # carries diagnostics without a SUMMARY line.
        if will_eval:
            for problem in problems:
                _add(findings, "stdout-parse", "%s: %s" % (label, problem))
        if transcript_sha is not None and run.get("tool_sha256") is not None \
                and transcript_sha != run["tool_sha256"]:
            _add(findings, "binding-digest-mismatch",
                 "%s: transcript TOOL sha256=%s declared tool.sha256=%s"
                 % (label, transcript_sha, run["tool_sha256"]))

    declared = run.get("cases") or []
    declared_set = {}
    for cid, status, detail in declared:
        if cid in declared_set:
            _add(findings, "case-duplicate",
                 "%s: declared case id %r repeats" % (label, cid))
        declared_set.setdefault(cid, (status, detail))
    parsed_set = {}
    for cid, status, detail in parsed_cases:
        if cid in parsed_set:
            _add(findings, "case-duplicate",
                 "%s: transcript CASE id %r repeats" % (label, cid))
        parsed_set.setdefault(cid, (status.lower(), detail))

    if will_eval:
        if stdout is not None:
            statuses_equal = (
                {cid: row[0] for cid, row in declared_set.items()}
                == {cid: row[0] for cid, row in parsed_set.items()}
            )
            # A declared detail is the printable rendering of the transcript
            # detail: the real fixture separates fields with TABs, which a
            # record stores as single spaces (round-16 R4 alignment).
            details_equal = all(
                not detail
                or (parsed_set.get(cid, (None, None))[1] or "").replace("\t", " ") == detail
                for cid, (_, detail) in declared_set.items()
            )
            if not statuses_equal or not details_equal:
                _add(findings, "run-inconsistent",
                     "%s: declared cases do not equal the parsed transcript" % label)
            if parsed_summary is not None:
                total, failed = parsed_summary
                if total != len(parsed_cases):
                    _add(findings, "summary-mismatch",
                         "%s: SUMMARY total=%d but %d CASE rows" % (label, total, len(parsed_cases)))
                if failed != sum(1 for _, status, _ in parsed_cases if status == "FAIL"):
                    _add(findings, "summary-mismatch",
                         "%s: SUMMARY failed=%d disagrees with CASE rows" % (label, failed))
        if run.get("summary") is not None and parsed_summary is not None:
            if tuple(run["summary"]) != tuple(parsed_summary):
                _add(findings, "summary-mismatch",
                     "%s: declared summary=%s parsed summary=%s"
                     % (label, run["summary"], parsed_summary))
        elif run.get("summary") is not None and stdout is not None \
                and parsed_summary is None:
            _add(findings, "summary-mismatch",
                 "%s: declared summary has no parsed counterpart" % label)
    else:
        # A non-evaluable arm must not carry fabricated structured cases or a
        # nonzero summary: the record cannot hide green inside a dead run.
        if declared_set:
            _add(findings, "run-inconsistent",
                 "%s: non-evaluable arm declares structured CASE entries" % label)
        if run.get("summary") is not None and tuple(run["summary"]) != (0, 0):
            _add(findings, "summary-mismatch",
                 "%s: non-evaluable arm declares summary=%s"
                 % (label, run["summary"]))

    if exit_code is not None and timed_out is not None:
        if timed_out and exit_code not in (124, 137):
            _add(findings, "run-inconsistent",
                 "%s: timed_out=true requires exit 124 or 137, got %d"
                 % (label, exit_code))
        if not timed_out and exit_code in (124, 137):
            _add(findings, "run-inconsistent",
                 "%s: exit %d is a timeout status but timed_out=false"
                 % (label, exit_code))
        if timed_out and parsed_cases:
            _add(findings, "run-inconsistent",
                 "%s: timed_out arm cannot carry CASE rows" % label)
        if exit_code == 2 and parsed_cases:
            _add(findings, "run-inconsistent",
                 "%s: could-not-evaluate exit 2 cannot carry CASE rows" % label)
        if exit_code == 0 and not timed_out:
            if any(status == "FAIL" for _, status, _ in parsed_cases):
                _add(findings, "run-inconsistent",
                     "%s: exit 0 with failing CASE rows" % label)
            if stdout is not None and not parsed_cases:
                _add(findings, "run-inconsistent",
                     "%s: exit 0 with an empty transcript" % label)
        if exit_code == 1 and stdout is not None and parsed_cases \
                and not any(status == "FAIL" for _, status, _ in parsed_cases):
            _add(findings, "run-inconsistent",
                 "%s: exit 1 with no failing CASE row" % label)

    universe = _expected_universe(arm)
    counts = {}
    for cid, _, _ in parsed_cases:
        counts[cid] = counts.get(cid, 0) + 1
    evaluable = will_eval and stdout is not None
    if not evaluable:
        if exit_code is not None and timed_out is not None:
            truncated = " truncated" if run.get("stdout_truncated") else ""
            _add(findings, "run-not-evaluable",
                 "%s: exit=%d timed_out=%s%s cannot serve as evidence"
                 % (label, exit_code, timed_out, truncated))
        return
    if not parsed_cases:
        _add(findings, "case-set-empty",
             "%s: zero CASE rows; a summary alone is not evidence" % label)
        return
    for cid in sorted(counts):
        if cid not in universe:
            _add(findings, "case-unknown",
                 "%s: case id %r is outside the pinned universe" % (label, cid))
    for cid in universe:
        if cid not in counts:
            _add(findings, "case-missing",
                 "%s: expected case id %r is absent (a partial --case run is not evidence)"
                 % (label, cid))
    for cid in sorted(counts):
        if cid not in universe:
            continue
        want = _expected_status(arm, cid)
        got = parsed_set[cid][0]
        detail = parsed_set[cid][1]
        if got != want:
            _add(findings, "case-status-unexpected",
                 "%s: %s recorded %s, expected %s" % (label, cid, got, want))
            continue
        if got != "pass":
            continue  # FAIL rows carry refusal findings legitimately
        if arm == "namespace_controls":
            # The digest-pinned, unchanged r14 fixture emits plain "ok";
            # its own per-case assertions check exits and forbidden access.
            # Do not invent r15-only transcript fields for those records.
            continue
        token = re.search(r"\tobserved_finding=([^\t]+)", detail)
        finding_tok = token.group(1) if token else None
        refusal_ids = CONFIG_TOKEN_IDS
        if cid in refusal_ids:
            if finding_tok is None or finding_tok == "none":
                _add(findings, "case-finding-mismatch",
                     "%s: %s PASS lacks a non-'none' observed_finding token"
                     % (label, cid))
        elif finding_tok != "none":
            _add(findings, "case-finding-mismatch",
                 "%s: %s PASS carries %s observed_finding"
                 % (label, cid,
                    "no token" if finding_tok is None else repr(finding_tok)))
    if arm == "baseline":
        for cid in sorted(CONFIG_HARM_FAILS):
            entry = parsed_set.get(cid)
            if entry is None or entry[0] != "fail":
                continue
            detail = entry[1]
            weak = (
                not detail
                or len(detail) > MAX_DETAIL_CHARS
                or "Traceback" in detail
                or "Exception" in detail
                or not any(token in detail for token in REASON_TOKENS)
            )
            if weak:
                _add(findings, "baseline-reason-weak",
                     "%s: %s fails without a concrete recorded reason" % (label, cid))

    run["_parsed"] = parsed_set


def _arm_verdicts(meta, findings):
    """Emit aggregate per-arm verdict findings for the admissible claim."""
    labels = {
        "baseline_preharm": "preharm-not-green",
        "baseline": "baseline-not-red",
        "changed": "changed-not-green",
        "namespace_controls": "namespace-incomplete",
    }
    for arm, aggregate in labels.items():
        run = meta.get(arm)
        if run is None:
            continue
        label = "namespace_controls" if arm == "namespace_controls" else "runs.%s" % arm
        parsed = run.get("_parsed") or {}
        exit_code = run.get("exit_code")
        timed_out = run.get("timed_out")
        if exit_code not in (0, 1) or timed_out or not parsed \
                or run.get("stdout_truncated"):
            continue  # run-not-evaluable already emitted
        bad = []
        for cid in _expected_universe(arm):
            entry = parsed.get(cid)
            if entry is None:
                bad.append("%s absent" % cid)
                continue
            want = _expected_status(arm, cid)
            if entry[0] != want:
                bad.append("%s=%s want %s" % (cid, entry[0], want))
        if bad:
            _add(findings, aggregate,
                 "%s: %s" % (label, "; ".join(bad[:12])))


# ---------------------------------------------------------------- evaluate

def evaluate(root, root_fd, root_dev, record_text):
    """Evaluate record text. Returns (status, findings, meta)."""
    findings = []
    obj, error = _json_or_error(record_text)
    if error is not None:
        _add(findings, "record-malformed", error)
        return EXIT_COULD_NOT_EVALUATE, findings, {"root": str(root)}
    schema_findings, meta = _validate_record(obj)
    meta["root"] = str(root)
    findings.extend(schema_findings)
    if any(item["level"] >= 2 for item in schema_findings):
        return EXIT_COULD_NOT_EVALUATE, findings, meta

    _check_bindings(meta, findings, root_fd, root_dev)
    for arm in ARM_IDS:
        run = meta.get(arm)
        if run is None:
            continue
        _eval_arm(arm, run, findings)
        if run.get("stdout") is not None:
            parsed_cases, _s, _t, _p = _parse_transcript(run["stdout"])
            run["_parsed"] = {cid: (status.lower(), detail)
                              for cid, status, detail in parsed_cases}
    ns = meta.get("namespace_controls")
    if ns is not None:
        _eval_arm("namespace_controls", ns, findings)
        if ns.get("stdout") is not None:
            parsed_cases, _s, _t, _p = _parse_transcript(ns["stdout"])
            ns["_parsed"] = {cid: (status.lower(), detail)
                             for cid, status, detail in parsed_cases}
    _arm_verdicts(meta, findings)

    status = _status_for(findings)
    return status, findings, meta


# ---------------------------------------------------------------- frozen

def _frozen_schema_check(obj):
    """Return (normalized expected, reason)."""
    if not isinstance(obj, dict):
        return None, "expected.json is not a JSON object"
    allowed = {"record", "record_sha256", "verdict", "files"}
    extra = set(obj) - allowed
    if extra:
        return None, "unknown expected.json key(s): %s" % ", ".join(sorted(extra))
    record, reason = _classify_rel(obj.get("record"))
    if reason is not None:
        return None, "record path is %s" % reason
    protection = _protected_reason(record.split("/"))
    if protection is not None:
        return None, "record path is %s" % protection
    record_sha = obj.get("record_sha256")
    if not isinstance(record_sha, str) or not SHA256_RE.fullmatch(record_sha):
        return None, "record_sha256 must be 64 lowercase hex characters"
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
    return {"record": record, "record_sha256": record_sha,
            "verdict": verdict, "files": pins}, None


def _record_bound_paths(parsed):
    """Measured relative paths a well-formed record must pin in frozen mode."""
    paths = {CONFIG_FIXTURE_PATH, NAMESPACE_FIXTURE_PATH, INSTALLED_TOOL_PATH}
    if isinstance(parsed, dict):
        for key in ("fixture", "namespace_fixture"):
            value = parsed.get(key)
            if isinstance(value, dict):
                rel, reason = _classify_rel(value.get("path"))
                if rel is not None:
                    paths.add(rel)
    return paths


def evaluate_frozen(frozen_dir, measure_root):
    """Verify snapshot pins, then evaluate. Returns (status, findings, meta).

    `frozen_dir` holds expected.json and the pinned record; `measure_root`
    supplies the live bytes the record binds to. Both are validated with
    the same boundary machinery.
    """
    findings = []
    meta = {}
    frozen, frozen_fd, frozen_dev, frozen_findings = _resolve_root(frozen_dir)
    findings.extend(frozen_findings)
    if frozen is None:
        return EXIT_COULD_NOT_EVALUATE, findings, meta
    meta["frozen"] = str(frozen)
    try:
        root, root_fd, root_dev, root_findings = _resolve_root(measure_root)
        findings.extend(root_findings)
        if root is None:
            return EXIT_COULD_NOT_EVALUATE, findings, meta
        meta["root"] = str(root)
        try:
            expected_fd, reason, _ = _open_regular_beneath(
                frozen_fd, frozen_dev, "expected.json", MAX_JSON_BYTES)
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

            for rel in sorted(pins):
                declared = pins[rel]
                fd, reason, size = _open_regular_beneath(
                    root_fd, root_dev, rel, MAX_PINNED_BYTES)
                if reason is not None:
                    _add(findings, "snapshot_tampered",
                         "%r: pin cannot be verified under --root (%s)" % (rel, reason))
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
                frozen_fd, frozen_dev, record_rel, MAX_JSON_BYTES)
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
            if _sha_text(record_text) != expected["record_sha256"]:
                _add(findings, "snapshot_tampered",
                     "%r: pinned record sha256=%s observed=%s"
                     % (record_rel, expected["record_sha256"],
                        _sha_text(record_text)))
                return EXIT_COULD_NOT_EVALUATE, findings, meta

            parsed, error = _json_or_error(record_text)
            if error is None:
                unpinned = sorted(_record_bound_paths(parsed) - set(pins))
                if unpinned:
                    _add(findings, "frozen-incomplete",
                         "measured paths not pinned in expected.json: %s"
                         % ", ".join(repr(rel) for rel in unpinned))
                    return EXIT_COULD_NOT_EVALUATE, findings, meta

            status, record_findings, record_meta = evaluate(
                root, root_fd, root_dev, record_text)
            findings.extend(record_findings)
            meta.update(record_meta)
            meta["frozen"] = str(frozen)
            if status != EXIT_COULD_NOT_EVALUATE:
                observed_verdict = STATUS_BY_CODE[status]
                if observed_verdict != expected["verdict"]:
                    _add(findings, "snapshot-verdict-mismatch",
                         "expected=%s observed=%s"
                         % (expected["verdict"], observed_verdict))
                    status = EXIT_COULD_NOT_EVALUATE
            meta["frozen_files"] = len(pins)
            return status, findings, meta
        finally:
            os.close(root_fd)
    finally:
        os.close(frozen_fd)


# ---------------------------------------------------------------- output

def _emit(status, findings, meta):
    print("souji-preservation-evidence: %s" % STATUS_BY_CODE[status])
    print("scope: declared-record consistency only; no command execution or execution proof")
    if meta.get("root") is not None:
        print("root: %r" % str(meta["root"]))
    if meta.get("measured_commit") is not None:
        print("measured_commit: %s" % meta["measured_commit"])
    arms = [arm for arm in ARM_IDS if meta.get(arm) is not None]
    if meta.get("namespace_controls") is not None:
        arms.append("namespace_controls")
    if arms:
        print("arms: %s" % ",".join(arms))
    if meta.get("frozen_files") is not None:
        print("frozen_files: %d" % meta["frozen_files"])
    for item in findings:
        print("finding %s: %s" % (item["id"], item["detail"]))
    return status


# ---------------------------------------------------------------- selftest

SELFTEST_COMMIT = "0123456789abcdef0123456789abcdef01234567"

BENIGN = sorted(CONFIG_BENIGN_IDS)
REFUSAL = sorted(CONFIG_REFUSAL_IDS)
NS_IDS = list(NAMESPACE_IDS)


def _write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path, obj):
    _write_text(path, json.dumps(obj, indent=2, sort_keys=True) + "\n")


def _sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _sha_text(text):
    return _sha_bytes(text.encode("utf-8"))


def _default_detail(cid, status):
    """Fixture-shaped detail text for a case row: the real r15 fixture emits
    TAB-separated detail fields (`ok<TAB>observed_exit=0<TAB>observed_finding=none`)."""
    if status == "FAIL":
        return "contract difference\tobserved_exit=2\tobserved_finding=path-protected"
    if cid in CONFIG_TOKEN_IDS or cid in NAMESPACE_IDS:
        # A refusal PASS must record the concrete finding token it produced.
        return "guard held\tobserved_exit=2\tobserved_finding=path-protected"
    return "ok\tobserved_exit=0\tobserved_finding=none"


def _transcript(tool_path, tool_sha, rows, detail_map=None):
    """rows: list of (id, status). Builds fixture-shaped stdout."""
    lines = ["TOOL\t%s\tsha256=%s" % (tool_path, tool_sha),
             "TOOL-KIND\tother"]
    total = len(rows)
    failed = 0
    for cid, status in rows:
        failed += status == "FAIL"
        detail = (detail_map or {}).get(cid, _default_detail(cid, status))
        lines.append("CASE\t%s\t%s\t%s" % (cid, status, detail))
    lines.append("SUMMARY\ttotal=%d\tfailed=%d" % (total, failed))
    return "\n".join(lines) + "\n"


def _arm(tool_commit, tool_sha, statuses, *, tool_path="/var/tmp/tool.sh",
         exit_code=None, timed_out=False, detail_map=None, argv=None):
    rows = [(cid, status.upper()) for cid, status in statuses]
    if exit_code is None:
        exit_code = 0 if all(status == "PASS" for _, status in rows) else 1
    cases = []
    for cid, status in rows:
        detail = (detail_map or {}).get(cid, _default_detail(cid, status))
        cases.append({"id": cid, "status": status.lower(),
                      "detail": detail.replace("\t", " ")})
    failed = sum(1 for _, status in rows if status == "FAIL")
    stdout = _transcript(tool_path, tool_sha, rows, detail_map)
    arm = {
        "tool": {"commit": tool_commit, "sha256": tool_sha},
        "argv": argv if argv is not None else
            ["timeout", "300", "python3", "-B", "fixture.py", "--tool", tool_path],
        "exit_code": exit_code,
        "timed_out": timed_out,
        "stdout": stdout,
        "stdout_sha256": _sha_text(stdout),
        "stdout_bytes_total": len(stdout.encode("utf-8")),
        "stdout_truncated": False,
        "stderr": "",
        "cases": cases,
        "summary": {"total": len(rows), "failed": failed},
    }
    return arm


def _good_statuses(arm):
    return [(cid, "pass" if _expected_status(arm, cid) == "pass" else "fail")
            for cid in sorted(CONFIG_IDS)]


def _ns_statuses():
    return [(cid, "pass") for cid in NS_IDS]


def _record(root, changed_sha):
    fixture_sha = _sha_bytes((root / CONFIG_FIXTURE_PATH).read_bytes())
    ns_sha = _sha_bytes((root / NAMESPACE_FIXTURE_PATH).read_bytes())
    return {
        "schema": SCHEMA_ID,
        "declared_consistency_only": True,
        "measured_commit": SELFTEST_COMMIT,
        "fixture": {"path": CONFIG_FIXTURE_PATH, "sha256": fixture_sha},
        "namespace_fixture": {"path": NAMESPACE_FIXTURE_PATH, "sha256": ns_sha},
        "runs": {
            "baseline_preharm": _arm(PREHARM_COMMIT, PREHARM_SHA256,
                                     _good_statuses("baseline_preharm")),
            "baseline": _arm(BASELINE_COMMIT, BASELINE_SHA256,
                             _good_statuses("baseline")),
            "changed": _arm(SELFTEST_COMMIT, changed_sha,
                            _good_statuses("changed"),
                            tool_path=str(root / INSTALLED_TOOL_PATH)),
        },
        "namespace_controls": _arm(
            SELFTEST_COMMIT, changed_sha, _ns_statuses(),
            tool_path=str(root / INSTALLED_TOOL_PATH)),
    }


def _selftest_root(base, name, lane):
    root = base / name
    (root / "tools").mkdir(parents=True)
    (root / "tests/fixtures").mkdir(parents=True)
    _write_text(root / INSTALLED_TOOL_PATH, "#!/bin/sh\n# synthetic installed tool\n")
    _write_text(root / CONFIG_FIXTURE_PATH, "# synthetic r15 config fixture\n")
    real = lane / NAMESPACE_FIXTURE_PATH
    if real.is_file():
        shutil.copyfile(real, root / NAMESPACE_FIXTURE_PATH)
        (root / NAMESPACE_FIXTURE_PATH).chmod(0o644)
    else:
        # Deterministic fallback keeps the frozen input evaluable only when
        # the record's declared digest is edited to match; the pinned check
        # still fails, which the green cases below must not rely on.
        _write_text(root / NAMESPACE_FIXTURE_PATH, "# synthetic namespace fixture\n")
    return root


def _lane_fixture_available(lane):
    real = lane / NAMESPACE_FIXTURE_PATH
    try:
        return real.is_file() and _sha_bytes(real.read_bytes()) == NAMESPACE_SHA256
    except OSError:
        return False


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


def _frozen_expected(record_dir, root, record_path="record.json", verdict="clean"):
    files = {}
    for rel in (CONFIG_FIXTURE_PATH, NAMESPACE_FIXTURE_PATH, INSTALLED_TOOL_PATH):
        files[rel] = _sha_bytes((root / rel).read_bytes())
    return {
        "record": record_path,
        "record_sha256": _sha_bytes((record_dir / record_path).read_bytes()),
        "verdict": verdict,
        "files": files,
    }


def _selftest():
    try:
        base = Path(tempfile.mkdtemp(prefix="souji-r15-preservation-selftest.", dir="/var/tmp"))
    except OSError as exc:
        print("selftest-unavailable: %s" % (exc,))
        return 2
    results = []
    try:
        lane = Path(__file__).resolve().parents[1]
        if not _lane_fixture_available(lane):
            print("selftest-unavailable: %s missing or differs from the pinned r14 digest"
                  % (lane / NAMESPACE_FIXTURE_PATH))
            return 2
        home = base / "home"
        home.mkdir()
        (home / ".ssh").mkdir()
        (home / ".config").mkdir()
        _write_text(home / ".ssh/id_ed25519", "synthetic home, never read\n")
        _write_text(home / ".config/rec.json", '{"schema":"synthetic"}\n')
        env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "LC_ALL": "C",
            "TMPDIR": "/var/tmp",
            "HOME": str(home),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        cases = []

        root = _selftest_root(base, "positive", lane)
        changed_sha = _sha_bytes((root / INSTALLED_TOOL_PATH).read_bytes())
        record = _record(root, changed_sha)
        cases.append((
            "positive",
            ["--root", str(root), "--record", json.dumps(record)],
            0, [],
            ["souji-preservation-evidence: clean",
             "measured_commit: " + SELFTEST_COMMIT,
             "arms: baseline_preharm,baseline,changed,namespace_controls"],
        ))

        # green-only: changed is all-pass and the harm baseline arm is absent.
        root = _selftest_root(base, "green-only-missing-arm", lane)
        record = _record(root, changed_sha)
        del record["runs"]["baseline"]
        cases.append((
            "green-only-missing-arm",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["run-missing"], ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # missing-config-arm per parent directive: changed arm absent.
        root = _selftest_root(base, "missing-config-arm", lane)
        record = _record(root, changed_sha)
        del record["runs"]["changed"]
        cases.append((
            "missing-config-arm",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["run-missing"], ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # weakened red: harm baseline reports benign controls as passing.
        root = _selftest_root(base, "weakened-red", lane)
        record = _record(root, changed_sha)
        weakened = [(cid, "pass") for cid in sorted(CONFIG_IDS)]
        record["runs"]["baseline"] = _arm(
            BASELINE_COMMIT, BASELINE_SHA256, weakened)
        cases.append((
            "weakened-red",
            ["--root", str(root), "--record", json.dumps(record)],
            1,
            ["baseline-not-red"] + ["case-status-unexpected"] * len(CONFIG_HARM_FAILS),
            ["souji-preservation-evidence: failed"],
        ))

        # baseline failure without a concrete recorded reason.
        root = _selftest_root(base, "weak-reason", lane)
        record = _record(root, changed_sha)
        record["runs"]["baseline"] = _arm(
            BASELINE_COMMIT, BASELINE_SHA256,
            [(cid, "fail" if _expected_status("baseline", cid) == "fail" else "pass")
             for cid in sorted(CONFIG_IDS)],
            detail_map={cid: "" for cid in sorted(CONFIG_HARM_FAILS)})
        cases.append((
            "weak-reason",
            ["--root", str(root), "--record", json.dumps(record)],
            1, ["baseline-reason-weak"] * len(CONFIG_HARM_FAILS),
            ["souji-preservation-evidence: failed"],
        ))

        # changed arm has a red case: green is not demonstrated.
        root = _selftest_root(base, "changed-not-green", lane)
        record = _record(root, changed_sha)
        rows = _good_statuses("changed")
        rows[0] = (rows[0][0], "fail")
        record["runs"]["changed"] = _arm(
            SELFTEST_COMMIT, changed_sha, rows,
            tool_path=str(root / INSTALLED_TOOL_PATH))
        cases.append((
            "changed-not-green",
            ["--root", str(root), "--record", json.dumps(record)],
            1, ["case-status-unexpected", "changed-not-green"],
            ["souji-preservation-evidence: failed"],
        ))

        # changed arm bound to the harm digest: no repair was measured.
        root = _selftest_root(base, "changed-is-baseline", lane)
        record = _record(root, changed_sha)
        record["runs"]["changed"] = _arm(
            SELFTEST_COMMIT, BASELINE_SHA256, _good_statuses("changed"),
            tool_path=str(root / INSTALLED_TOOL_PATH))
        cases.append((
            "changed-is-baseline",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["binding-digest-mismatch", "pinned-mismatch"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # namespace controls incomplete: 11/12.
        root = _selftest_root(base, "namespace-incomplete", lane)
        record = _record(root, changed_sha)
        record["namespace_controls"] = _arm(
            SELFTEST_COMMIT, changed_sha, _ns_statuses()[:-1],
            tool_path=str(root / INSTALLED_TOOL_PATH))
        cases.append((
            "namespace-incomplete",
            ["--root", str(root), "--record", json.dumps(record)],
            1, ["case-missing", "namespace-incomplete"],
            ["souji-preservation-evidence: failed"],
        ))

        # baseline could-not-evaluate is not red evidence.
        root = _selftest_root(base, "baseline-exit2", lane)
        record = _record(root, changed_sha)
        record["runs"]["baseline"] = {
            "tool": {"commit": BASELINE_COMMIT, "sha256": BASELINE_SHA256},
            "exit_code": 2, "timed_out": False, "stdout": "",
            "cases": [], "summary": {"total": 0, "failed": 0},
        }
        cases.append((
            "baseline-exit2",
            ["--root", str(root), "--record", json.dumps(record)],
            1, ["run-not-evaluable"],
            ["souji-preservation-evidence: failed"],
        ))

        # baseline timeout is not red evidence either.
        root = _selftest_root(base, "baseline-timeout", lane)
        record = _record(root, changed_sha)
        record["runs"]["baseline"] = {
            "tool": {"commit": BASELINE_COMMIT, "sha256": BASELINE_SHA256},
            "exit_code": 124, "timed_out": True, "stdout": "",
            "cases": [], "summary": {"total": 0, "failed": 0},
        }
        cases.append((
            "baseline-timeout",
            ["--root", str(root), "--record", json.dumps(record)],
            1, ["run-not-evaluable"],
            ["souji-preservation-evidence: failed"],
        ))

        # unknown case id in the transcript.
        root = _selftest_root(base, "unknown-id", lane)
        record = _record(root, changed_sha)
        rows = _good_statuses("changed") + [("R15CFG-99", "pass")]
        record["runs"]["changed"] = _arm(
            SELFTEST_COMMIT, changed_sha, rows,
            tool_path=str(root / INSTALLED_TOOL_PATH))
        cases.append((
            "unknown-id",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["case-unknown"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # duplicate CASE row in the transcript.
        root = _selftest_root(base, "duplicate-id", lane)
        record = _record(root, changed_sha)
        dup = record["runs"]["changed"]["stdout"].replace(
            "SUMMARY\t", "CASE\tR15CFG-01\tPASS\tok\nSUMMARY\t")
        record["runs"]["changed"]["stdout"] = dup
        cases.append((
            "duplicate-id",
            ["--root", str(root), "--record", json.dumps(record)],
            # r16: with TAB details parseable, the first (token-bearing) row
            # wins and the duplicate shows as declared/parsed disagreement.
            2, ["case-duplicate", "run-inconsistent", "run-inconsistent",
                "summary-mismatch"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # declared structured fields disagree with the transcript.
        root = _selftest_root(base, "structured-disagree", lane)
        record = _record(root, changed_sha)
        record["runs"]["changed"]["cases"][0]["status"] = "fail"
        cases.append((
            "structured-disagree",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["run-inconsistent"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # declared digest does not match the measured bytes.
        root = _selftest_root(base, "digest-mismatch", lane)
        record = _record(root, changed_sha)
        record["fixture"]["sha256"] = "0" * 64
        cases.append((
            "digest-mismatch",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["binding-digest-mismatch"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # pinned baseline identity differs.
        root = _selftest_root(base, "pinned-mismatch", lane)
        record = _record(root, changed_sha)
        record["runs"]["baseline"]["tool"]["sha256"] = "1" * 64
        cases.append((
            "pinned-mismatch",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["pinned-mismatch", "binding-digest-mismatch"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # malformed JSON record.
        root = _selftest_root(base, "malformed", lane)
        cases.append((
            "malformed",
            ["--root", str(root), "--record", "{bad json\n"],
            2, ["record-malformed"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # duplicate JSON key.
        root = _selftest_root(base, "duplicate-key", lane)
        record = _record(root, changed_sha)
        duplicate = json.dumps(record, sort_keys=True)
        duplicate = duplicate[:-1] + ', "measured_commit": "%s"}' % SELFTEST_COMMIT
        cases.append((
            "duplicate-key",
            ["--root", str(root), "--record", duplicate],
            2, ["record-malformed"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # wrong schema id.
        root = _selftest_root(base, "schema-id", lane)
        record = _record(root, changed_sha)
        record["schema"] = "souji-evidence-cache-v1"
        cases.append((
            "schema-id",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["record-schema"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # declared_consistency_only false is refused.
        root = _selftest_root(base, "consistency-flag", lane)
        record = _record(root, changed_sha)
        record["declared_consistency_only"] = False
        cases.append((
            "consistency-flag",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["record-schema"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # bool-as-int exit_code.
        root = _selftest_root(base, "bool-exit", lane)
        record = _record(root, changed_sha)
        record["runs"]["changed"]["exit_code"] = True
        cases.append((
            "bool-exit",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["record-schema"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # historical namespace-only r14-shaped record is refused.
        root = _selftest_root(base, "legacy-record", lane)
        legacy = {
            "name": "census-boundary",
            "matched": True,
            "measured_commit": SELFTEST_COMMIT,
            "dependencies": {"tools/souji-census.sh": changed_sha},
        }
        cases.append((
            "legacy-record",
            ["--root", str(root), "--record", json.dumps(legacy)],
            2, ["record-schema"] * 4 + ["run-missing"] * 2,
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # protected binding path.
        root = _selftest_root(base, "protected", lane)
        _write_text(root / ".ssh/id_ed25519", "synthetic, never read\n")
        record = _record(root, changed_sha)
        record["fixture"] = {"path": ".ssh/id_ed25519", "sha256": "0" * 64}
        cases.append((
            "protected",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["path-protected"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # absolute binding path.
        root = _selftest_root(base, "absolute-path", lane)
        record = _record(root, changed_sha)
        record["fixture"] = {"path": "/etc/hostname", "sha256": "0" * 64}
        cases.append((
            "absolute-path",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["path-absolute"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # escaping binding path.
        root = _selftest_root(base, "escape", lane)
        record = _record(root, changed_sha)
        record["fixture"] = {"path": "../escape.txt", "sha256": "0" * 64}
        cases.append((
            "escape",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["path-escape"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # protected root.
        root = _selftest_root(base, "root-protected", lane)
        protected_root = root / ".ssh"
        protected_root.mkdir()
        record = _record(root, changed_sha)
        cases.append((
            "root-protected",
            ["--root", str(protected_root), "--record", json.dumps(record)],
            2, ["root-protected"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # home root is protected.
        root = _selftest_root(base, "home-boundary", lane)
        record = _record(root, changed_sha)
        cases.append((
            "home-root-protected",
            ["--root", str(home), "--record", json.dumps(record)],
            2, ["root-protected"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # record path inside a protected dir.
        root = _selftest_root(base, "record-protected", lane)
        _write_text(root / ".ssh/record.json", json.dumps(record))
        cases.append((
            "record-protected",
            ["--root", str(root), "--record", str(root / ".ssh/record.json")],
            2, ["record-protected"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # missing record file.
        root = _selftest_root(base, "record-unreadable", lane)
        cases.append((
            "record-unreadable",
            ["--root", str(root), "--record", str(root / "absent.json")],
            2, ["record-unreadable"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # root is not a directory.
        root = _selftest_root(base, "root-not-directory", lane)
        plain = base / "plain-root.txt"
        _write_text(plain, "not a directory\n")
        record = _record(root, changed_sha)
        cases.append((
            "root-not-directory",
            ["--root", str(plain), "--record", json.dumps(record)],
            2, ["root-not-directory"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # symlink root.
        root = _selftest_root(base, "root-symlink", lane)
        os.symlink(root, base / "root-symlink-link")
        record = _record(root, changed_sha)
        cases.append((
            "root-symlink",
            ["--root", str(base / "root-symlink-link"), "--record", json.dumps(record)],
            2, ["root-symlink"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # symlinked fixture path under the root.
        root = _selftest_root(base, "binding-symlink", lane)
        real_target = root / "tests/fixtures/real.py"
        _write_text(real_target, "# real\n")
        (root / CONFIG_FIXTURE_PATH).unlink()
        os.symlink(real_target, root / CONFIG_FIXTURE_PATH)
        record = _record(root, changed_sha)
        cases.append((
            "binding-symlink",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["path-symlink"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # hardlinked installed tool.
        root = _selftest_root(base, "binding-hardlink", lane)
        os.link(root / INSTALLED_TOOL_PATH, root / "tools/alias.sh")
        record = _record(root, changed_sha)
        cases.append((
            "binding-hardlink",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["path-hardlink"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # missing installed tool: binding-missing is honest failure evidence.
        root = _selftest_root(base, "binding-missing", lane)
        (root / INSTALLED_TOOL_PATH).unlink()
        record = _record(root, changed_sha)
        cases.append((
            "binding-missing",
            ["--root", str(root), "--record", json.dumps(record)],
            1, ["binding-missing"],
            ["souji-preservation-evidence: failed"],
        ))

        # frozen clean: record+expected.json under DIR, payloads under --root.
        root = _selftest_root(base, "frozen-clean", lane)
        frozen_dir = base / "frozen-clean-dir"
        frozen_dir.mkdir()
        _write_json(frozen_dir / "record.json", _record(root, changed_sha))
        _write_json(frozen_dir / "expected.json", _frozen_expected(frozen_dir, root))
        cases.append((
            "frozen-clean",
            ["--frozen", str(frozen_dir), "--root", str(root)],
            0, [],
            ["souji-preservation-evidence: clean", "frozen_files: 3",
             "measured_commit: " + SELFTEST_COMMIT],
        ))

        # frozen tampered payload: a measured file differs from its pin.
        root = _selftest_root(base, "frozen-tampered", lane)
        frozen_dir = base / "frozen-tampered-dir"
        frozen_dir.mkdir()
        _write_json(frozen_dir / "record.json", _record(root, changed_sha))
        _write_json(frozen_dir / "expected.json", _frozen_expected(frozen_dir, root))
        _write_text(root / CONFIG_FIXTURE_PATH, "# tampered fixture\n")
        cases.append((
            "frozen-tampered",
            ["--frozen", str(frozen_dir), "--root", str(root)],
            2, ["snapshot_tampered"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # frozen tampered record: record.json differs from record_sha256.
        root = _selftest_root(base, "frozen-record-tampered", lane)
        frozen_dir = base / "frozen-record-tampered-dir"
        frozen_dir.mkdir()
        _write_json(frozen_dir / "record.json", _record(root, changed_sha))
        _write_json(frozen_dir / "expected.json", _frozen_expected(frozen_dir, root))
        _write_text(frozen_dir / "record.json", "{}\n")
        cases.append((
            "frozen-record-tampered",
            ["--frozen", str(frozen_dir), "--root", str(root)],
            2, ["snapshot_tampered"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # frozen incomplete: pin set misses a measured path.
        root = _selftest_root(base, "frozen-incomplete", lane)
        frozen_dir = base / "frozen-incomplete-dir"
        frozen_dir.mkdir()
        _write_json(frozen_dir / "record.json", _record(root, changed_sha))
        expected = _frozen_expected(frozen_dir, root)
        del expected["files"][INSTALLED_TOOL_PATH]
        _write_json(frozen_dir / "expected.json", expected)
        cases.append((
            "frozen-incomplete",
            ["--frozen", str(frozen_dir), "--root", str(root)],
            2, ["frozen-incomplete"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # frozen verdict mismatch: expected verdict wrong for a clean record.
        root = _selftest_root(base, "frozen-verdict-mismatch", lane)
        frozen_dir = base / "frozen-verdict-mismatch-dir"
        frozen_dir.mkdir()
        _write_json(frozen_dir / "record.json", _record(root, changed_sha))
        _write_json(frozen_dir / "expected.json",
                    _frozen_expected(frozen_dir, root, verdict="failed"))
        cases.append((
            "frozen-verdict-mismatch",
            ["--frozen", str(frozen_dir), "--root", str(root)],
            2, ["snapshot-verdict-mismatch"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # frozen malformed expected.json.
        root = _selftest_root(base, "frozen-malformed", lane)
        frozen_dir = base / "frozen-malformed-dir"
        frozen_dir.mkdir()
        _write_text(frozen_dir / "expected.json", "{bad\n")
        cases.append((
            "frozen-malformed",
            ["--frozen", str(frozen_dir), "--root", str(root)],
            2, ["frozen-malformed"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # frozen missing expected.json.
        root = _selftest_root(base, "frozen-unreadable", lane)
        frozen_dir = base / "frozen-unreadable-dir"
        frozen_dir.mkdir()
        cases.append((
            "frozen-unreadable",
            ["--frozen", str(frozen_dir), "--root", str(root)],
            2, ["frozen-unreadable"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # frozen schema: wrong verdict word.
        root = _selftest_root(base, "frozen-schema", lane)
        frozen_dir = base / "frozen-schema-dir"
        frozen_dir.mkdir()
        _write_json(frozen_dir / "expected.json",
                    {"record": "record.json",
                     "record_sha256": "0" * 64,
                     "verdict": "bogus", "files": {"a": "0" * 64}})
        cases.append((
            "frozen-schema",
            ["--frozen", str(frozen_dir), "--root", str(root)],
            2, ["frozen-schema"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # --frozen without --root is a usage error (exit 2, no findings).
        root = _selftest_root(base, "frozen-no-root", lane)
        cases.append((
            "frozen-no-root",
            ["--frozen", str(root)],
            2, [], [],
        ))

        # subset argv is could-not-evaluate.
        root = _selftest_root(base, "argv-subset", lane)
        record = _record(root, changed_sha)
        record["runs"]["changed"]["argv"] = [
            "python3", "-B", "fixture.py", "--tool", str(root / INSTALLED_TOOL_PATH),
            "--case", "R15CFG-01"]
        cases.append((
            "argv-subset",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["run-inconsistent"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # declared stdout_sha256 disagrees with stdout.
        root = _selftest_root(base, "stdout-sha-mismatch", lane)
        record = _record(root, changed_sha)
        record["runs"]["changed"]["stdout_sha256"] = "0" * 64
        cases.append((
            "stdout-sha-mismatch",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["run-inconsistent"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # truncated stdout cannot prove the id universe.
        root = _selftest_root(base, "stdout-truncated", lane)
        record = _record(root, changed_sha)
        record["runs"]["changed"]["stdout_truncated"] = True
        cases.append((
            "stdout-truncated",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["run-inconsistent", "run-not-evaluable", "summary-mismatch"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))

        # refusal PASS without an observed_finding token is weak evidence.
        root = _selftest_root(base, "finding-mismatch", lane)
        record = _record(root, changed_sha)
        detail_map = {cid: "ok observed_exit=0 observed_finding=none"
                      for cid in sorted(CONFIG_TOKEN_IDS)}
        record["runs"]["changed"] = _arm(
            SELFTEST_COMMIT, changed_sha, _good_statuses("changed"),
            tool_path=str(root / INSTALLED_TOOL_PATH), detail_map=detail_map)
        cases.append((
            "finding-mismatch",
            ["--root", str(root), "--record", json.dumps(record)],
            1, ["case-finding-mismatch"] * len(CONFIG_TOKEN_IDS),
            ["souji-preservation-evidence: failed"],
        ))

        # exit 0 arm with an empty transcript is could-not-evaluate.
        root = _selftest_root(base, "zero-cases", lane)
        record = _record(root, changed_sha)
        record["runs"]["changed"] = {
            "tool": {"commit": SELFTEST_COMMIT, "sha256": changed_sha},
            "exit_code": 0, "timed_out": False, "stdout": "",
            "cases": [], "summary": {"total": 0, "failed": 0},
        }
        cases.append((
            "zero-cases",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["case-set-empty", "run-inconsistent", "stdout-parse",
                "summary-mismatch"],
            ["souji-preservation-evidence: could-not-evaluate"],
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
        description="Declared paired-evidence admission gate (r15 / C2).")
    parser.add_argument("--root",
                        help="checkout every measured path resolves against; "
                             "required with --record and --frozen")
    parser.add_argument("--record",
                        help="record JSON text, @PATH, or a regular file path")
    parser.add_argument("--frozen",
                        help="snapshot directory containing expected.json and the "
                             "pinned record; measured paths resolve under --root")
    parser.add_argument("--selftest", action="store_true", help="run isolated self-checks")
    args = parser.parse_args(argv)

    if args.selftest:
        if args.root or args.record or args.frozen:
            parser.error("--selftest takes no other mode arguments")
        return _selftest()
    if args.frozen:
        if not args.root:
            parser.error("--frozen DIR requires --root DIR for measured paths")
        if args.record:
            parser.error("--frozen supplies its own pinned record; do not pass --record")
        status, findings, meta = evaluate_frozen(args.frozen, args.root)
        return _emit(status, findings, meta)
    if not (args.root and args.record):
        parser.error("choose exactly one mode: --selftest, "
                     "--frozen DIR --root DIR, or --root DIR --record JSON")

    root, root_fd, root_dev, findings = _resolve_root(args.root)
    if root is None:
        return _emit(EXIT_COULD_NOT_EVALUATE, findings, {})
    try:
        value = args.record
        if value.lstrip().startswith("{"):
            record_text = value
        else:
            raw = value[1:] if value.startswith("@") else value
            record_text, reason, detail = _read_path_text(raw, MAX_JSON_BYTES)
            if record_text is None:
                tag = "record-protected" if reason == "protected" else "record-unreadable"
                _add(findings, tag, "--record could not be read: %s" % (detail or reason))
                return _emit(EXIT_COULD_NOT_EVALUATE, findings, {})
        status, record_findings, meta = evaluate(root, root_fd, root_dev, record_text)
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
        print("souji-preservation-evidence: could-not-evaluate")
        print("finding internal-error: %s: %s" % (type(exc).__name__, exc))
        sys.exit(EXIT_COULD_NOT_EVALUATE)
