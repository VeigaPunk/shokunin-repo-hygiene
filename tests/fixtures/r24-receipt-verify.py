#!/usr/bin/env python3
"""r24-receipt-verify.py -- C3 counter for tools/souji-receipt-run.py `verify` (souji round 24).

Usage:
    python3 -B tests/fixtures/r24-receipt-verify.py --tool tools/souji-receipt-run.py [--lane-root PATH]

Frozen cases (contract: .ufo/waves/round-24/preregistration.txt, C3):
  a  non-durable -- a well-formed receipt whose rev is a full commit reachable from no durable
                    ref -> verify exit 2 RECEIPT-REV-NOT-DURABLE; two instances, both must refuse:
                    a `git commit-tree` object never stored in a ref, and one held only by
                    refs/jj/keep/<x> (refs/jj/* never counts as durable); both share the tree of
                    the receipt's durable rev
  b  label       -- a well-formed receipt whose tool= path (with that path's true digest at rev)
                    does not occur as an argv element of its cmd= -> verify exit 2
                    RECEIPT-TOOL-NOT-IN-ARGV; two instances, both must refuse: a path absent from
                    cmd entirely, and a path that is a substring but not an element of a cmd argv
  c  clean       -- a receipt produced by `run` in a synthetic repo -> verify exit 0 (verify=ok)
  d  regression  -- each of the five committed r23 receipts under
                    <lane-root>/census/round-23/records/ -> verify exit 0 against the lane root;
                    an absent lane root or receipt is a FAIL, never a skip-to-pass

--lane-root defaults to the git toplevel containing --tool. All synthetic git writes stay in one
scratch repo under the caller's scratch root (TMPDIR when set, else /var/tmp), trap-cleaned on
exit, error and signal; the lane root is only read (`verify` reads blobs and refs).

One `case=<id> verdict=PASS|FAIL expect=<...> got=<...>` line per case, then the last line
    cases=C pass=P refusals=R/2 regress=N/5
Exit 0 iff P == C.
"""
from __future__ import annotations

import argparse
import atexit
import hashlib
import os
import shutil
import signal
import subprocess
import sys

sys.dont_write_bytecode = True
import tempfile
import traceback

# The scratch parent is the caller's: TMPDIR when set, else /var/tmp (never a bare /tmp). The
# receipt runner accepts --out under the same root (tools/souji-receipt-run.py scratch_root()).
SCRATCH_PARENT = os.path.abspath(tempfile.gettempdir()) if os.environ.get("TMPDIR") else "/var/tmp"
TOOL_REL = "tools/tiny-counter.py"
OTHER_REL = "tools/other-counter.py"
# a path that is a substring (and suffix) of the TOOL_REL argv element but never an element
SUBSTR_REL = "counter.py"
COUNTER = """#!/usr/bin/env python3
\"\"\"tiny counter (fixture tool): the counts line `verify` insists a receipt carries.\"\"\"
print("assertions=4 resolved=3 skipped=1 mismatches=0")
"""
OTHER = COUNTER.replace("tiny counter", "other counter")
SUBSTR = COUNTER.replace("tiny counter", "root counter")
NOT_DURABLE = "RECEIPT-REV-NOT-DURABLE"
JJ_KEEP_REF = "refs/jj/keep/r24-fixture"
NOT_IN_ARGV = "RECEIPT-TOOL-NOT-IN-ARGV"
REGRESSION = (
    "declared-evidence-after",
    "gate-check-at-first-landing",
    "gate-check-at-lane-base",
    "gate-check-c3",
    "agreement-after",
)

_SCRATCH: list[str] = []


def _cleanup() -> None:
    for path in _SCRATCH:
        shutil.rmtree(path, ignore_errors=True)


def _trap(signum, _frame):
    _cleanup()
    sys.exit(128 + signum)


def fmt(value: object, limit: int = 200) -> str:
    flat = " ".join(str(value).split())
    return flat if len(flat) <= limit else flat[: limit - 3] + "..."


def isolated_env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
                        "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_CEILING_DIRECTORIES")}
    env.update({
        "GIT_AUTHOR_NAME": "souji-fixture",
        "GIT_AUTHOR_EMAIL": "fixture@shokunin.local",
        "GIT_COMMITTER_NAME": "souji-fixture",
        "GIT_COMMITTER_EMAIL": "fixture@shokunin.local",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_TERMINAL_PROMPT": "0",
        "LC_ALL": "C",
        "TZ": "UTC",
    })
    return env


class Ctx:
    def __init__(self, runner: str) -> None:
        self.runner = runner
        self.env = isolated_env()
        self.scratch = tempfile.mkdtemp(prefix="souji-r24-receipt-verify-", dir=SCRATCH_PARENT)
        _SCRATCH.append(self.scratch)
        self.repo = os.path.join(self.scratch, "repo")
        self.receipts = os.path.join(self.scratch, "receipts")
        self.hooks = os.path.join(self.scratch, "no-hooks")
        for path in (self.repo, self.receipts, self.hooks):
            os.makedirs(path)
        self.gitbase = ["git", "-c", f"core.hooksPath={self.hooks}", "-c", "commit.gpgsign=false",
                        "-c", "init.defaultBranch=main", "-c", "maintenance.auto=false"]

    def git(self, *args: str) -> str:
        proc = subprocess.run([*self.gitbase, "-C", self.repo, *args], capture_output=True,
                              text=True, errors="replace", env=self.env)
        if proc.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)} rc={proc.returncode}: "
                               f"{fmt(proc.stderr or proc.stdout)}")
        return proc.stdout.strip()

    def blob_sha256(self, rev: str, rel: str) -> str:
        proc = subprocess.run([*self.gitbase, "-C", self.repo, "cat-file", "blob", f"{rev}:{rel}"],
                              capture_output=True, env=self.env)
        if proc.returncode != 0:
            raise RuntimeError(f"cat-file {rev}:{rel} rc={proc.returncode}")
        return hashlib.sha256(proc.stdout).hexdigest()

    def write(self, rel: str, text: str) -> None:
        path = os.path.join(self.repo, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)

    def runner_call(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-B", self.runner, *args], capture_output=True,
                              text=True, errors="replace", env=self.env)

    def verify(self, receipt: str, root: str | None = None) -> subprocess.CompletedProcess:
        return self.runner_call("verify", "--root", root or self.repo, receipt)

    def run(self, rev: str, out: str) -> subprocess.CompletedProcess:
        return self.runner_call("run", "--root", self.repo, "--rev", rev, "--tool", TOOL_REL,
                                "--out", out, "--", sys.executable, TOOL_REL)


def outcome(proc: subprocess.CompletedProcess) -> str:
    text = f"{proc.stdout}\n{proc.stderr}".strip()
    return f"rc={proc.returncode} out={fmt(text, 140) or '-'}"


def refused(proc: subprocess.CompletedProcess, code: str) -> bool:
    return (proc.returncode == 2 and code in proc.stderr
            and "verify=ok" not in proc.stdout)


def doctored(text: str, edits: dict[str, str]) -> str:
    lines = text.splitlines()
    seen: set[str] = set()
    for i, line in enumerate(lines):
        key = line.split("=", 1)[0]
        if key in edits and key not in seen and "=" in line:
            lines[i] = f"{key}={edits[key]}"
            seen.add(key)
        if line == "--- stdout ---":
            break
    missing = set(edits) - seen
    if missing:
        raise RuntimeError(f"receipt header lacks {sorted(missing)}")
    return "\n".join(lines) + "\n"


def write_receipt(ctx: Ctx, name: str, text: str) -> str:
    path = os.path.join(ctx.receipts, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


# ---------------------------------------------------------------------------
# cases: each returns (ok, expect, got); a raised exception is a FAIL
# ---------------------------------------------------------------------------
def case_c(ctx: Ctx, st: dict) -> tuple[bool, str, str]:
    expect = "run at a durable rev writes a receipt; verify rc=0 verify=ok"
    out = os.path.join(ctx.receipts, "clean.receipt")
    proc = ctx.run(st["rev"], out)
    if proc.returncode != 0 or not os.path.isfile(out):
        return False, expect, f"run {outcome(proc)} receipt_written={os.path.isfile(out)}"
    st["clean"] = open(out, encoding="utf-8").read()
    ver = ctx.verify(out)
    ok = ver.returncode == 0 and "verify=ok" in ver.stdout
    return ok, expect, f"run rc=0; verify {outcome(ver)}"


def case_a(ctx: Ctx, st: dict) -> tuple[bool, str, str]:
    expect = (f"rev -> commit with the same tool bytes held by no ref, and one held only by "
              f"{JJ_KEEP_REF}: verify rc=2 {NOT_DURABLE} for both")
    rev = st["rev"]
    tree = ctx.git("rev-parse", f"{rev}^{{tree}}")
    want = ctx.blob_sha256(rev, TOOL_REL)
    got: list[str] = []
    ok = True
    for label, holder in (("no-ref", None), ("jj-keep-only", JJ_KEEP_REF)):
        commit = ctx.git("commit-tree", tree, "-p", rev, "-m", f"r24 fixture: {label}")
        if holder:
            ctx.git("update-ref", holder, commit)
        # preconditions: the only defect is durability (a refusal for any other reason is not case a)
        holders = ctx.git("for-each-ref", "--format=%(refname)", "--contains", commit).split()
        if holders != ([holder] if holder else []):
            raise RuntimeError(f"precondition: {label} {commit} is held by {holders}")
        if commit == rev or len(commit) != 40:
            raise RuntimeError(f"precondition: commit-tree gave {commit!r}")
        if ctx.blob_sha256(commit, TOOL_REL) != want:
            raise RuntimeError(f"precondition: {label} tree does not hold the same tool bytes")
        path = write_receipt(ctx, f"non-durable-{label}.receipt",
                             doctored(st["clean"], {"rev": commit}))
        ver = ctx.verify(path)
        # symmetry witness (informational, not scored): `run` on the same rev
        sym = ctx.run(commit, os.path.join(ctx.receipts, f"non-durable-{label}-run.receipt"))
        ok = ok and refused(ver, NOT_DURABLE)
        got.append(f"{label}(rev={commit[:12]} refs={','.join(holders) or '-'} digest_equal=True) "
                   f"verify {outcome(ver)}; run_same_rev rc={sym.returncode}")
    return ok, expect, "; ".join(got)


def case_b(ctx: Ctx, st: dict) -> tuple[bool, str, str]:
    expect = (f"tool= with its true digest at rev, not an argv element of cmd=: verify rc=2 "
              f"{NOT_IN_ARGV} (absent path and substring-only path)")
    rev = st["rev"]
    got: list[str] = []
    ok = True
    cmd_line = next(l for l in st["clean"].splitlines() if l.startswith("cmd="))
    for label, rel in (("absent", OTHER_REL), ("substring", SUBSTR_REL)):
        if label == "absent" and rel in cmd_line:
            raise RuntimeError(f"precondition: {rel} occurs in {cmd_line}")
        if label == "substring" and rel not in cmd_line:
            raise RuntimeError(f"precondition: {rel} is not a substring of {cmd_line}")
        sha = ctx.blob_sha256(rev, rel)
        path = write_receipt(ctx, f"label-{label}.receipt",
                             doctored(st["clean"], {"tool": rel, "tool_sha256": sha}))
        ver = ctx.verify(path)
        ok = ok and refused(ver, NOT_IN_ARGV)
        got.append(f"{label}(tool={rel}) {outcome(ver)}")
    return ok, expect, "; ".join(got)


def make_case_d(name: str, lane_root: str | None):
    def case(ctx: Ctx, _st: dict) -> tuple[bool, str, str]:
        expect = f"r23 {name}.tsv: verify --root <lane-root> rc=0 verify=ok"
        if not lane_root or not os.path.isdir(lane_root):
            return False, expect, f"lane-root absent ({lane_root or 'unresolved'})"
        receipt = os.path.join(lane_root, "census", "round-23", "records", f"{name}.tsv")
        if not os.path.isfile(receipt):
            return False, expect, f"receipt absent: {receipt}"
        ver = ctx.verify(receipt, lane_root)
        return ver.returncode == 0 and "verify=ok" in ver.stdout, expect, outcome(ver)
    return case


def resolve_lane_root(explicit: str | None, runner: str | None) -> str | None:
    if explicit:
        return os.path.abspath(explicit)
    if not runner:
        return None
    proc = subprocess.run(["git", "-C", os.path.dirname(runner), "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True, env=isolated_env())
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def main(argv: list[str]) -> int:
    atexit.register(_cleanup)
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(sig, _trap)
    ap = argparse.ArgumentParser(description="souji r24 C3 receipt verify/run symmetry counter")
    ap.add_argument("--tool", required=True, help="path to souji-receipt-run.py")
    ap.add_argument("--lane-root", default=None)
    args = ap.parse_args(argv)

    runner = os.path.abspath(args.tool) if os.path.isfile(args.tool) else None
    lane_root = resolve_lane_root(args.lane_root, runner)
    cases = [("c", case_c), ("a", case_a), ("b", case_b)]
    cases += [(f"d-{name}", make_case_d(name, lane_root)) for name in REGRESSION]
    print(f"tool={runner or args.tool} lane_root={lane_root or '-'}")

    results: dict[str, bool] = {}
    ctx = None
    st: dict = {}
    if runner is not None:
        try:
            ctx = Ctx(runner)
            ctx.git("init", "-q")
            ctx.write(TOOL_REL, COUNTER)
            ctx.write(OTHER_REL, OTHER)
            ctx.write(SUBSTR_REL, SUBSTR)
            ctx.git("add", "-A")
            ctx.git("commit", "-q", "-m", "r24 fixture commit")
            st["rev"] = ctx.git("rev-parse", "HEAD")
        except Exception as exc:
            ctx = None
            print(f"setup=FAIL error={fmt(exc)}")
    for cid, case in cases:
        if ctx is None:
            ok, expect, got = False, f"case {cid}", f"tool unusable ({args.tool})"
        elif cid in ("a", "b") and "clean" not in st:
            ok, expect, got = False, f"case {cid}", "no clean receipt from run (case c failed)"
        else:
            try:
                ok, expect, got = case(ctx, st)
            except Exception as exc:  # a crash is a failure, never a pass
                line = traceback.extract_tb(exc.__traceback__)[-1].lineno
                ok, expect, got = False, f"case {cid}", f"error={fmt(exc)} at line {line}"
        results[cid] = ok
        print(f"case={cid} verdict={'PASS' if ok else 'FAIL'} expect=<{fmt(expect)}> "
              f"got=<{fmt(got, 400)}>")

    passed = sum(results.values())
    refusals = sum(results[c] for c in ("a", "b"))
    regress = sum(results[f"d-{n}"] for n in REGRESSION)
    print(f"cases={len(results)} pass={passed} refusals={refusals}/2 regress={regress}/{len(REGRESSION)}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
