#!/usr/bin/env python3
"""Round-15 bounded verification runner.

Measures the r15 claims end to end and writes an exclusively-created JSON
record under census/round-15/. Output is evidence for L1's acceptance
run, never deletion certification.

Checks (every one stamps the measured commit and its tool commit):
  * extracts the harm baseline census tool at BASELINE_HARM and the
    pre-harm tool at BASELINE_PREHARM into a /var/tmp scratch dir;
  * runs tests/fixtures/r15-census-config.py --tool for preharm, harm and
    installed arms (same fixture, same command shape);
  * runs the unchanged r14 namespace fixture tests/fixtures/
    r14-census-boundary.py --tool <installed> (installed retention arm
    only; historical baseline arms are r14 closure ground truth);
  * bash tools/souji-census.sh --selftest (legacy);
  * shellcheck -S warning tools/souji-census.sh;
  * python3 tools/souji-preservation-evidence.py --selftest,
    --record <paired JSON> --root <lane root>, and
    --frozen tests/fixtures/r15-preservation-frozen --root <lane root>;
  * python3 tests/fixtures/r15-preservation-evidence.py (external C2
    fixture; registry two-evidence gate);
  * census/round-15/count-claims.py on BASELINE_HARM and HEAD.

Boundaries honored by construction:
  * every subprocess is wrapped in `timeout --kill-after=K T`; rc 124 or
    137 is recorded as could-not-evaluate and can never satisfy an
    evaluator (a red/baseline arm needs real CASE-contract failures);
  * captured stdout/stderr are capped at STREAM_CAP bytes; bytes_total
    and sha256 of the full stream plus truncated:true|false are stored;
  * dependency digests are stamped before and after the suite and each
    committed dependency is bound to `git show HEAD:<path>` bytes;
    HEAD is re-read at the end;
  * the output file is created with O_CREAT|O_EXCL; a historical JSON is
    never overwritten;
  * scratch lives under /var/tmp and cleanup happens only after every
    child process group is reaped (communicate() returns first);
  * the C2 record is a *declared* paired-evidence document synthesized
    verbatim from captured stdout/stderr/exit codes; the checker proves
    internal declared consistency only — the L1 measured run captures
    observed execution and is not authenticated historical provenance.

Baseline-red semantics: exit 1 alone never counts as red. A red
classification requires parsed `CASE\t<ID>\tFAIL` rows with a consistent
SUMMARY line; rc 2, 124, 137, 126/127 or a traceback are
could-not-evaluate, not red.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
ROUND_DIR = ROOT / "census/round-15"
BASELINE_HARM = "cc2168325768d5356a82c039dcdf787377c55784"
BASELINE_PREHARM = "a31642d14006830ec62edf40b0354c3699728c4a"
TOOL_REL = "tools/souji-census.sh"
CONFIG_FIXTURE = "tests/fixtures/r15-census-config.py"
NAMESPACE_FIXTURE = "tests/fixtures/r14-census-boundary.py"
CHECKER = "tools/souji-preservation-evidence.py"
PRESERVATION_FIXTURE = "tests/fixtures/r15-preservation-evidence.py"
FROZEN_DIR = "tests/fixtures/r15-preservation-frozen"
COUNT_CLAIMS = "census/round-15/count-claims.py"
SELF = "census/round-15/run-verification.py"
HISTORICAL = ROOT / "census/round-14/verification.json"
STREAM_CAP = 262144
TIMEOUT_KILL_AFTER = 10

# Pinned starting snapshot at BASELINE_HARM (r15 claims baseline = r14 end).
EXPECTED_SOURCE_SNAPSHOT = {
    "source_rows": 40,
    "tiers": {"A": 36, "B": 3, "C": 1},
    "statuses": {"mined": 23, "queued": 15, "rejected": 2},
}

DEPENDENCIES = [
    TOOL_REL,
    CONFIG_FIXTURE,
    NAMESPACE_FIXTURE,
    CHECKER,
    PRESERVATION_FIXTURE,
    FROZEN_DIR,
    SELF,
    "census/round-15/claims.json",
]

CASE_RE = re.compile(r"^CASE\t([^\t]+)\t(PASS|FAIL)\t?(.*)$")
SUMMARY_RE = re.compile(r"^SUMMARY\ttotal=([0-9]+)\tfailed=([0-9]+)$")
OBSERVED_EXIT_RE = re.compile(r"(?:^|[; \t])observed_exit=([0-9]+)")
OBSERVED_FINDING_RE = re.compile(r"(?:^|[; \t])observed_finding=([A-Za-z0-9_.-]+)")

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(
    TMPDIR="/var/tmp",
    PYTHONDONTWRITEBYTECODE="1",
    LC_ALL="C",
    GIT_CONFIG_NOSYSTEM="1",
    GIT_CONFIG_GLOBAL="/dev/null",
    GIT_TERMINAL_PROMPT="0",
    GIT_AUTHOR_NAME="souji-r15-fixture",
    GIT_AUTHOR_EMAIL="fixture@example.invalid",
    GIT_COMMITTER_NAME="souji-r15-fixture",
    GIT_COMMITTER_EMAIL="fixture@example.invalid",
)
NAMESPACE_FIXTURE_PINNED_SHA256 = "e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2"
# Fixture-pinned tool identities (ConfigFixture contract): the r15
# config fixture emits TOOL-KIND tags against these digests.
EXPECTED_TOOL_DIGESTS = {
    "preharm": "6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026",
    "harm": "fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9",
}
# Pinned fixture universe (ConfigFixture confirmation, revised): 20
# cases, of which these TEN must fail under the harm baseline.
# R15CFG-09 was reclassified refusal->benign (extensions.partialClone
# false/empty accepted) and joined the harm set; R15CFG-06 covers all
# valid promisor markers + partialCloneFilter green; R15CFG-07 invalid
# booleans only; R15CFG-08 is the safety class (sentries + no-lazy pin).
EXPECTED_CONFIG_CASES = frozenset("R15CFG-%02d" % i for i in range(1, 21))
EXPECTED_HARM_CASES = frozenset(
    ("R15CFG-01", "R15CFG-04", "R15CFG-06", "R15CFG-08", "R15CFG-09",
     "R15CFG-10", "R15CFG-12", "R15CFG-13", "R15CFG-15", "R15CFG-16")
)
# Benign restoration set: cases that prove pre-harm support was
# restored. R15CFG-08 is deliberately EXCLUDED — it is a NEW safety
# refusal gain, not a benign key. The set is pinned literally, never
# inferred from the harm run's observed failed ids.
BENIGN_RESTORATION_IDS = EXPECTED_HARM_CASES - {"R15CFG-08"}
# Pre-harm expected failure matrix (AdmissionChecker pinned, fixture
# author revised): the a31642d tool lacks the new refusal and safety
# guards, does not clear inherited GIT_* env (R15CFG-18), and lacks the
# strict malformed-compare contract (R15CFG-20); R15CFG-05 stays PASS.
EXPECTED_PREHARM_FAILS = frozenset(
    ("R15CFG-02", "R15CFG-03", "R15CFG-07", "R15CFG-08", "R15CFG-11",
     "R15CFG-14", "R15CFG-17", "R15CFG-18", "R15CFG-19", "R15CFG-20")
)
# Pinned r14 namespace universe: the unchanged r14 boundary fixture
# emits exactly these twelve case ids; the installed arm must pass all.
# Historical pre-harm/baseline r14 outcomes are established closure
# ground truth (census/round-14/verification.json) and are NOT rerun.
EXPECTED_NAMESPACE_CASES = frozenset("R14C2-%02d" % i for i in range(1, 13))
TOOL_KIND_RE = re.compile(r"^TOOL-KIND\t([^\t]+)$")
TOOL_LINE_RE = re.compile(r"^TOOL\t([^\t]+)\tsha256=([0-9a-f]{64})$")


def git(*args):
    return subprocess.check_output(
        ["git", "-C", str(ROOT), *args], env=ENV, text=True
    ).strip()


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha_or_none(path):
    try:
        return sha_bytes(path.read_bytes())
    except OSError:
        return None


def parse_cases(stdout):
    """Parse TOOL/TOOL-KIND/CASE/SUMMARY rows. Returns ids, statuses,
    observations and a summary-consistency flag. `id-set` pseudo-rows
    are excluded from the case set but flagged."""
    cases = {}
    detail = {}
    observed = {}
    duplicates = []
    summary = None
    id_set_row = False
    tool_kind = None
    tool_line = None
    for line in stdout.split("\n"):
        m = CASE_RE.match(line)
        if m:
            cid, status, rest = m.group(1), m.group(2), m.group(3)
            if cid == "id-set":
                id_set_row = status == "FAIL"
                continue
            if cid in cases:
                duplicates.append(cid)
            cases[cid] = status
            detail[cid] = rest
            om = OBSERVED_EXIT_RE.search(rest)
            fm = OBSERVED_FINDING_RE.search(rest)
            observed[cid] = {
                "observed_exit": int(om.group(1)) if om else None,
                "observed_finding": fm.group(1) if fm else None,
            }
            continue
        sm = SUMMARY_RE.match(line)
        if sm:
            summary = {"total": int(sm.group(1)), "failed": int(sm.group(2))}
            continue
        km = TOOL_KIND_RE.match(line)
        if km:
            tool_kind = km.group(1)
            continue
        tm = TOOL_LINE_RE.match(line)
        if tm:
            tool_line = {"path": tm.group(1), "sha256": tm.group(2)}
            continue
        if line.startswith("JSON\t"):
            try:
                payload = json.loads(line[5:])
            except ValueError:
                payload = None
            if isinstance(payload, dict):
                for rec in payload.get("cases") or []:
                    if not isinstance(rec, dict) or "id" not in rec:
                        continue
                    observed.setdefault(rec["id"], {})
                    observed[rec["id"]]["observed_exit"] = rec.get("exit")
                    observed[rec["id"]]["observed_finding"] = rec.get("finding")
    failed_ids = sorted(c for c, s in cases.items() if s == "FAIL")
    consistent = (
        summary is not None
        and summary["total"] == len(cases)
        and summary["failed"] == len(failed_ids)
    )
    return {
        "cases": cases,
        "detail": detail,
        "observed": observed,
        "summary": summary,
        "summary_consistent": consistent,
        "failed_ids": failed_ids,
        "id_set_row": id_set_row,
        "tool_kind": tool_kind,
        "tool_line": tool_line,
        "duplicate_ids": sorted(set(duplicates)),
    }


def run(name, command, seconds, tool_commit):
    """Bounded invocation: `timeout --kill-after=K T` wraps the real
    command, streams capped at STREAM_CAP bytes in memory. rc 124/137 is
    recorded as could-not-evaluate and can never be a red/pass verdict."""
    wrapped = ["timeout", "--kill-after=%d" % TIMEOUT_KILL_AFTER, str(seconds)] + [
        str(part) for part in command
    ]
    started = time.monotonic()
    try:
        child = subprocess.Popen(
            wrapped,
            cwd=ROOT,
            env=ENV,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
    except OSError as exc:
        return {
            "name": name,
            "command": wrapped,
            "exit_code": 127,
            "timed_out": False,
            "could_not_evaluate": True,
            "classification": "spawn-failure",
            "stdout": "",
            "stderr": "spawn failed: %r" % (exc,),
            "stdout_bytes_total": 0,
            "stderr_bytes_total": 0,
            "stdout_sha256": sha_bytes(b""),
            "stderr_sha256": sha_bytes(b""),
            "stdout_truncated": False,
            "stderr_truncated": False,
            "measured_commit": CURRENT_REV,
            "tool_commit": tool_commit,
            "seconds": round(time.monotonic() - started, 3),
            "matched": False,
        }
    timed_out = False
    try:
        out, err = child.communicate(timeout=seconds + TIMEOUT_KILL_AFTER + 30)
        code = child.returncode if child.returncode is not None else 137
    except subprocess.TimeoutExpired:
        # The `timeout` wrapper should have fired first; this is the outer
        # failsafe. Kill the whole group and keep the partial streams.
        timed_out = True
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        out, err = child.communicate()
        code = 137
    raw_out, raw_err = out, err
    out_s = raw_out[:STREAM_CAP].decode("utf-8", "replace")
    err_s = raw_err[:STREAM_CAP].decode("utf-8", "replace")
    could_not_evaluate = timed_out or code in (124, 126, 127, 137)
    if code in (124, 137):
        classification = "timeout-not-red"
    elif code in (126, 127):
        classification = "wrapper-failure-not-red"
    elif timed_out:
        classification = "outer-timeout-not-red"
    elif "Traceback (most recent call last)" in err_s and code != 0:
        classification = "traceback-not-red"
    else:
        classification = "observed"
    result = {
        "name": name,
        "command": wrapped,
        "exit_code": code,
        "timed_out": timed_out or code in (124, 137),
        "could_not_evaluate": could_not_evaluate,
        "classification": classification,
        "stdout": out_s,
        "stderr": err_s,
        "stdout_bytes_total": len(raw_out),
        "stderr_bytes_total": len(raw_err),
        "stdout_sha256": sha_bytes(raw_out),
        "stderr_sha256": sha_bytes(raw_err),
        "stdout_truncated": len(raw_out) > STREAM_CAP,
        "stderr_truncated": len(raw_err) > STREAM_CAP,
        "measured_commit": CURRENT_REV,
        "tool_commit": tool_commit,
        "seconds": round(time.monotonic() - started, 3),
    }
    print(
        "%s: exit=%s classification=%s" % (name, code, classification),
        flush=True,
    )
    return result


def eval_exact(expected):
    def judge(item):
        item["expected_exit"] = expected
        return (
            not item["could_not_evaluate"] and item["exit_code"] == expected
        )

    return judge


def eval_fixture_red(item):
    """Red requires observed CASE-contract failures: rc 1 with a
    consistent SUMMARY and at least one FAIL row. Setup failures, rc 2,
    timeouts, tracebacks and unparseable output can never be red."""
    item["expected_exit"] = 1
    parsed = parse_cases(item["stdout"])
    item["parsed"] = parsed
    item["expected_failed_set"] = sorted(EXPECTED_HARM_CASES)
    item["observed_failed_set"] = sorted(parsed["failed_ids"])
    item["observed_failed_set_match"] = set(parsed["failed_ids"]) == EXPECTED_HARM_CASES
    # Reason details: every failed case must carry an observed refusal
    # (observed_exit 2 or a finding token), not a bookkeeping problem.
    reason_details = {
        cid: parsed["observed"].get(cid) for cid in parsed["failed_ids"]
    }
    item["failed_reason_details"] = reason_details
    reasons_ok = bool(parsed["failed_ids"]) and all(
        isinstance(detail, dict)
        and (detail.get("observed_exit") == 2 or detail.get("observed_finding"))
        for detail in reason_details.values()
    )
    item["failed_reason_details_ok"] = reasons_ok
    if item["could_not_evaluate"] or item["exit_code"] != 1:
        item["classification"] = (
            item["classification"]
            if item["classification"] != "observed"
            else "not-red-exit"
        )
        return False
    if not parsed["summary_consistent"]:
        item["classification"] = "unparseable-not-red"
        return False
    if not item["observed_failed_set_match"]:
        item["classification"] = "wrong-failed-set-not-red"
        return False
    if not reasons_ok:
        item["classification"] = "missing-reason-details-not-red"
        return False
    item["classification"] = "red-benign-config"
    return True


def eval_fixture_green(item):
    item["expected_exit"] = 0
    parsed = parse_cases(item["stdout"])
    item["parsed"] = parsed
    item["expected_case_set"] = sorted(EXPECTED_CONFIG_CASES)
    item["observed_case_set"] = sorted(parsed["cases"])
    if set(parsed["cases"]) != EXPECTED_CONFIG_CASES:
        item["classification"] = "wrong-case-universe"
        return False
    if item["could_not_evaluate"] or item["exit_code"] != 0:
        return False
    return parsed["summary_consistent"] and not parsed["failed_ids"]


def eval_fixture_all_pass(item, universe=None):
    """Retention arm: rc 0 with every parsed case PASS, a consistent
    summary, and — when a pinned universe is supplied — the emitted case
    set must equal it exactly (no narrowing, no extras)."""
    item["expected_exit"] = 0
    parsed = parse_cases(item["stdout"])
    item["parsed"] = parsed
    if universe is not None:
        item["expected_case_set"] = sorted(universe)
        item["observed_case_set"] = sorted(parsed["cases"])
        if set(parsed["cases"]) != universe:
            item["classification"] = "wrong-case-universe"
            return False
    if item["could_not_evaluate"] or item["exit_code"] != 0:
        return False
    return bool(parsed["cases"]) and all(
        s == "PASS" for s in parsed["cases"].values()
    ) and parsed["summary_consistent"]


def eval_preharm(item):
    """Pre-harm arm: benign restoration proof against the LITERAL pinned
    matrix. Matched only when the observed failed set equals
    EXPECTED_PREHARM_FAILS exactly (unsafe/safety classes) AND every
    BENIGN_RESTORATION_IDS case passed. Any actual benign failure
    admits no restoration proof -> unmatched. Zero-case or unparseable
    output is not evidence."""
    parsed = parse_cases(item["stdout"])
    item["parsed"] = parsed
    item["benign_restoration_ids"] = sorted(BENIGN_RESTORATION_IDS)
    item["expected_failed_set"] = sorted(EXPECTED_PREHARM_FAILS)
    item["observed_failed_set"] = sorted(parsed["failed_ids"])
    item["expected_exit"] = None
    if item["could_not_evaluate"]:
        return False
    benign_fails = sorted(set(parsed["failed_ids"]) & BENIGN_RESTORATION_IDS)
    item["benign_case_failures"] = benign_fails
    item["non_benign_failures"] = sorted(
        set(parsed["failed_ids"]) - BENIGN_RESTORATION_IDS
    )
    item["matrix_match"] = set(parsed["failed_ids"]) == EXPECTED_PREHARM_FAILS
    if benign_fails:
        # A real benign failure on the pre-harm arm admits nothing: the
        # restoration half of the pair is absent.
        item["classification"] = "benign-failure-no-restoration"
        return False
    if (
        item["exit_code"] == 1
        and item["matrix_match"]
        and parsed["summary_consistent"]
        and set(parsed["cases"]) == EXPECTED_CONFIG_CASES
    ):
        # Exact pinned matrix: only the unsafe/safety classes refused
        # pre-harm; every benign preservation case passed.
        item["classification"] = "preharm-matrix-benign-preserved"
        return True
    item["classification"] = "observed-unclassified"
    return False


def eval_counts_snapshot(item, snapshot):
    item["expected_exit"] = 0
    try:
        payload = json.loads(item["stdout"])
    except ValueError:
        payload = None
    item["snapshot_expected"] = snapshot
    item["snapshot_observed"] = (
        {k: payload.get(k) for k in snapshot} if isinstance(payload, dict) else None
    )
    item["snapshot_match"] = item["snapshot_observed"] == snapshot
    return (
        not item["could_not_evaluate"]
        and item["exit_code"] == 0
        and item["snapshot_match"]
    )




def validate_output(argument):
    if not argument:
        return ROUND_DIR / "verification.json"
    candidate = Path(argument)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    candidate = Path(os.path.abspath(str(candidate)))
    if candidate.parent != ROUND_DIR or candidate.suffix != ".json":
        raise RuntimeError(
            "output must live in census/round-15/ and end .json: %s" % candidate
        )
    return candidate


def tree_digest(absolute):
    """Deterministic digest over a directory's regular files: sorted
    relative paths plus each file's sha256. Missing dir -> None."""
    if not absolute.is_dir():
        return None
    h = hashlib.sha256()
    for child in sorted(absolute.rglob("*")):
        if not child.is_file():
            continue
        h.update(str(child.relative_to(absolute)).encode() + b"\0")
        h.update(child.read_bytes())
    return h.hexdigest()


def bound_dependency(path_rel):
    """Working-tree digest plus, when the path is committed at the captured
    revision, the committed digest. Directories get a deterministic tree
    digest (worktree) against a `git ls-tree` listing digest (committed).
    Absent or untracked dependencies are stated, never fabricated."""
    absolute = ROOT / path_rel
    if absolute.is_dir():
        worktree = tree_digest(absolute)
        entry = {
            "path": path_rel,
            "worktree_sha256": worktree,
            "exists": worktree is not None,
            "kind": "directory",
        }
        try:
            listing = subprocess.check_output(
                ["git", "-C", str(ROOT), "ls-tree", "-r", CURRENT_REV, "--", path_rel],
                env=ENV,
            )
            entry["committed_sha256"] = sha_bytes(listing) if listing.strip() else None
        except subprocess.CalledProcessError:
            entry["committed_sha256"] = None
        # Listing-vs-content digests differ in kind; equality is only
        # meaningful when both sides measure the same bytes, so record
        # presence parity instead of pretending a match.
        entry["committed_present"] = entry["committed_sha256"] is not None
        entry["matches_head"] = None
        return entry
    worktree = sha_or_none(absolute)
    entry = {"path": path_rel, "worktree_sha256": worktree, "exists": worktree is not None}
    try:
        entry["committed_sha256"] = sha_bytes(
            subprocess.check_output(
                ["git", "-C", str(ROOT), "show", CURRENT_REV + ":" + path_rel], env=ENV
            )
        )
    except subprocess.CalledProcessError:
        entry["committed_sha256"] = None
    entry["matches_head"] = (
        entry["committed_sha256"] is not None
        and entry["committed_sha256"] == worktree
    )
    return entry


def main(argv=None):
    global CURRENT_REV
    parser = argparse.ArgumentParser(
        description="Round-15 bounded verification; evidence only."
    )
    parser.add_argument(
        "--output",
        default=None,
        help="verification JSON name inside census/round-15/ (created exclusively)",
    )
    args = parser.parse_args(argv)
    target = validate_output(args.output)

    for commit in (BASELINE_HARM, BASELINE_PREHARM):
        try:
            subprocess.check_output(
                ["git", "-C", str(ROOT), "cat-file", "-e", commit + "^{commit}"],
                env=ENV,
            )
        except subprocess.CalledProcessError:
            raise RuntimeError("pinned commit not resolvable: %s" % commit)

    CURRENT_REV = git("rev-parse", "HEAD")

    # Claim the output name exclusively up front. A historical or
    # previously-exercised JSON is never overwritten.
    try:
        out_fd = os.open(str(target), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except FileExistsError:
        raise RuntimeError(
            "Refuse overwriting exercised evidence; pick a new attempt name: %s"
            % target.name
        )

    dependencies_before = {p: bound_dependency(p) for p in DEPENDENCIES}
    historical_before = sha_or_none(HISTORICAL)
    head_before = CURRENT_REV

    results = []

    def evaluate(item, judge):
        item["matched"] = bool(judge(item))
        print(
            "%s -> matched=%s classification=%s"
            % (item["name"], item["matched"], item["classification"]),
            flush=True,
        )
        return item

    with tempfile.TemporaryDirectory(
        prefix="souji-r15-verification-", dir="/var/tmp"
    ) as temp:
        tempdir = Path(temp)
        # Extract both pinned tool snapshots into exclusively-created
        # /var/tmp files (mkstemp uses O_EXCL).
        tools = {}
        for label, commit in (("preharm", BASELINE_PREHARM), ("harm", BASELINE_HARM)):
            fd, name = tempfile.mkstemp(
                prefix="souji-census-%s-" % label, suffix=".sh", dir=temp
            )
            with os.fdopen(fd, "wb") as handle:
                handle.write(
                    subprocess.check_output(
                        ["git", "-C", str(ROOT), "show", commit + ":" + TOOL_REL],
                        env=ENV,
                    )
                )
            os.chmod(name, 0o700)
            tools[label] = Path(name)
        tools["installed"] = ROOT / TOOL_REL
        tool_digests = {label: sha_or_none(path) for label, path in tools.items()}

        # (name, command, seconds, tool_commit, tool_label, judge)
        # tool_label keys label_digests; a wrong label mislabels evidence.
        order = [
            (
                "config-fixture-preharm",
                ["python3", "-B", CONFIG_FIXTURE, "--tool", str(tools["preharm"])],
                240,
                BASELINE_PREHARM,
                "preharm",
                eval_preharm,
            ),
            (
                "config-fixture-harm-baseline",
                ["python3", "-B", CONFIG_FIXTURE, "--tool", str(tools["harm"])],
                240,
                BASELINE_HARM,
                "harm",
                eval_fixture_red,
            ),
            (
                "config-fixture-installed",
                ["python3", "-B", CONFIG_FIXTURE, "--tool", str(tools["installed"])],
                240,
                CURRENT_REV,
                "installed",
                eval_fixture_green,
            ),
            # Only the installed namespace arm runs: pre-harm/baseline
            # r14 boundary outcomes are established closure ground truth
            # (census/round-14/verification.json) and are not rerun.
            (
                "namespace-boundary-installed",
                ["python3", "-B", NAMESPACE_FIXTURE, "--tool", str(tools["installed"])],
                300,
                CURRENT_REV,
                "installed",
                lambda item: eval_fixture_all_pass(item, EXPECTED_NAMESPACE_CASES),
            ),
            (
                "census-legacy-selftest",
                ["bash", TOOL_REL, "--selftest"],
                300,
                CURRENT_REV,
                "installed",
                eval_exact(0),
            ),
            (
                "census-shellcheck-warning",
                ["shellcheck", "-S", "warning", TOOL_REL],
                120,
                CURRENT_REV,
                "installed",
                eval_exact(0),
            ),
            (
                "preservation-checker-selftest",
                ["python3", "-B", CHECKER, "--selftest"],
                240,
                CURRENT_REV,
                "checker",
                eval_exact(0),
            ),
            (
                "preservation-checker-fixture",
                ["python3", "-B", PRESERVATION_FIXTURE],
                240,
                CURRENT_REV,
                "preservation-fixture",
                eval_exact(0),
            ),
            (
                "preservation-checker-frozen",
                ["python3", "-B", CHECKER, "--frozen", FROZEN_DIR, "--root", str(ROOT)],
                240,
                CURRENT_REV,
                "checker",
                eval_exact(0),
            ),
            (
                "count-claims-baseline",
                ["python3", "-B", COUNT_CLAIMS, BASELINE_HARM],
                60,
                CURRENT_REV,
                "count",
                lambda item: eval_counts_snapshot(item, EXPECTED_SOURCE_SNAPSHOT),
            ),
            (
                "count-claims-head",
                ["python3", "-B", COUNT_CLAIMS, "HEAD"],
                60,
                CURRENT_REV,
                "count",
                eval_exact(0),
            ),
        ]
        label_digests = dict(tool_digests)
        label_digests["checker"] = sha_or_none(ROOT / CHECKER)
        label_digests["count"] = sha_or_none(ROOT / COUNT_CLAIMS)
        label_digests["preservation-fixture"] = sha_or_none(ROOT / PRESERVATION_FIXTURE)
        # Frozen input pins: every file present under the frozen dir is
        # digested; expected.json (the declared manifest) is read and
        # embedded so pin mismatches are auditable post-run.
        frozen_input_digests = {}
        frozen_dir = ROOT / FROZEN_DIR
        if frozen_dir.is_dir():
            for child in sorted(frozen_dir.rglob("*")):
                if child.is_file():
                    frozen_input_digests[str(child.relative_to(frozen_dir))] = sha_or_none(child)
        try:
            frozen_expected = json.loads((frozen_dir / "expected.json").read_text())
        except (OSError, ValueError):
            frozen_expected = None

        ran = {}
        for name, command, seconds, tool_commit, label, judge in order:
            item = run(name, command, seconds, tool_commit)
            item["tool_sha256"] = label_digests.get(label)
            if name == "preservation-checker-frozen":
                item["frozen_input_digests"] = frozen_input_digests
                item["frozen_expected_json"] = frozen_expected
            evaluate(item, judge)
            ran[name] = item
            results.append(item)

        # Synthesize the C2 declared paired-evidence record verbatim from
        # captured runs, in the schema AdmissionChecker enforces
        # (souji-preservation-record-v1). The checker proves internal
        # declared consistency only — the L1 measured run captures
        # observed execution, not authenticated historical provenance.
        # Raw stdout/stderr/argv are included so the checker can
        # independently reparse CASE/SUMMARY rows instead of trusting
        # producer-parsed fields.
        def record_run(run_item, commit, tool_sha):
            parsed = run_item.get("parsed") or parse_cases(run_item["stdout"])
            cases = [
                {"id": cid, "status": parsed["cases"][cid].lower()}
                for cid in sorted(parsed["cases"])
            ]
            return {
                "tool": {"commit": commit, "sha256": tool_sha},
                "argv": run_item["command"],
                "exit_code": run_item["exit_code"],
                "timed_out": bool(run_item.get("timed_out")),
                "stdout": run_item["stdout"],
                "stdout_bytes_total": run_item["stdout_bytes_total"],
                "stdout_sha256": run_item["stdout_sha256"],
                "stdout_truncated": run_item["stdout_truncated"],
                "stderr": run_item["stderr"],
                "stderr_bytes_total": run_item["stderr_bytes_total"],
                "stderr_sha256": run_item["stderr_sha256"],
                "stderr_truncated": run_item["stderr_truncated"],
                "cases": cases,
                "summary": {
                    "total": len(cases),
                    "failed": sum(1 for c in cases if c["status"] == "fail"),
                },
            }

        record = {
            "schema": "souji-preservation-record-v1",
            "declared_consistency_only": True,
            "measured_commit": CURRENT_REV,
            "fixture": {
                "path": CONFIG_FIXTURE,
                "sha256": sha_or_none(ROOT / CONFIG_FIXTURE),
            },
            "namespace_fixture": {
                "path": NAMESPACE_FIXTURE,
                "sha256": sha_or_none(ROOT / NAMESPACE_FIXTURE),
            },
            "runs": {
                "baseline_preharm": record_run(
                    ran["config-fixture-preharm"],
                    BASELINE_PREHARM,
                    tool_digests["preharm"],
                ),
                "baseline": record_run(
                    ran["config-fixture-harm-baseline"],
                    BASELINE_HARM,
                    tool_digests["harm"],
                ),
                "changed": record_run(
                    ran["config-fixture-installed"],
                    CURRENT_REV,
                    tool_digests["installed"],
                ),
            },
            "namespace_controls": record_run(
                ran["namespace-boundary-installed"],
                CURRENT_REV,
                tool_digests["installed"],
            ),
        }
        record_path = tempdir / "r15-paired-evidence.json"
        record_path.write_text(json.dumps(record, indent=2) + "\n")

        checker_item = run(
            "preservation-checker-record",
            [
                "python3",
                "-B",
                CHECKER,
                "--record",
                str(record_path),
                "--root",
                str(ROOT),
            ],
            240,
            CURRENT_REV,
        )
        checker_item["tool_sha256"] = label_digests["checker"]
        checker_item["record_path_scratch"] = str(record_path)
        checker_item["record_sha256"] = sha_or_none(record_path)
        checker_item["record"] = record
        evaluate(checker_item, eval_exact(0))
        results.append(checker_item)

        measured_digests = {
            "preharm_tool_sha256": tool_digests["preharm"],
            "preharm_tool_matches_pin": tool_digests["preharm"] == EXPECTED_TOOL_DIGESTS["preharm"],
            "harm_tool_sha256": tool_digests["harm"],
            "harm_tool_matches_pin": tool_digests["harm"] == EXPECTED_TOOL_DIGESTS["harm"],
            "installed_tool_sha256": tool_digests["installed"],
            "namespace_fixture_sha256": sha_or_none(ROOT / NAMESPACE_FIXTURE),
            "namespace_fixture_matches_pin": sha_or_none(ROOT / NAMESPACE_FIXTURE)
            == NAMESPACE_FIXTURE_PINNED_SHA256,
        }

    dependencies_after = {p: bound_dependency(p) for p in DEPENDENCIES}
    historical_after = sha_or_none(HISTORICAL)
    head_after = git("rev-parse", "HEAD")

    data = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "round": 15,
        "measured_commit": CURRENT_REV,
        "head_before": head_before,
        "head_after": head_after,
        "head_stable": head_before == head_after,
        "baseline_commit": BASELINE_HARM,
        "baseline_preharm_commit": BASELINE_PREHARM,
        "tool_digests": measured_digests,
        "dependencies_before": dependencies_before,
        "dependencies_after": dependencies_after,
        "dependencies_unchanged_during_run": dependencies_before == dependencies_after,
        "historical_evidence": "census/round-14/verification.json",
        "historical_evidence_sha256_before": historical_before,
        "historical_evidence_sha256_after": historical_after,
        "historical_evidence_unchanged": historical_before == historical_after,
        "expected_source_snapshot": EXPECTED_SOURCE_SNAPSHOT,
        "results": results,
        "scope": (
            "All scratch under /var/tmp; synthetic fixture homes only; no real "
            "credential-store probe, no live census, no operator-sweep access. "
            "Evidence for admission review, never deletion certification."
        ),
    }
    payload = json.dumps(data, indent=2) + "\n"
    with os.fdopen(out_fd, "w") as handle:
        handle.write(payload)

    ok = (
        all(item["matched"] for item in results)
        and dependencies_before == dependencies_after
        and historical_before == historical_after
        and head_before == head_after
    )
    return 0 if ok else 1


CURRENT_REV = ""

if __name__ == "__main__":
    raise SystemExit(main())
