#!/usr/bin/env python3
"""r23-receipt-run.py -- selftest fixture for tools/souji-receipt-run.py (souji round 23, C2).

Builds a throw-away git repo under /var/tmp (never /tmp, never the lane tree), drives the
receipt runner through eight cases and prints one `case=<n> expect=<...> got=<...>` line per
case plus `selftest=<pass>/<total>`. Exit 0 iff every case passes.

Usage:
    python3 r23-receipt-run.py [path/to/souji-receipt-run.py]

Without an argument the runner is located by walking up from this file (and from $PWD) looking
for tools/souji-receipt-run.py, so the fixture works both from .ufo/waves/round-23/w1/ and from
tests/fixtures/. SOUJI_RECEIPT_RUN overrides.

Cases (contract: .ufo/waves/round-23/preregistration.txt, C2):
  1  run a tiny counter at the repo's only commit -> receipt written, v1 header order exact,
     rc=0, stdout present
  2  verify that receipt -> exit 0
  3  tool mutated in a NEW commit, verify the OLD receipt -> RECEIPT-TOOL-DIGEST-MISMATCH
  4  receipt whose rev= is a branch name / 7-char id -> refused with an explicit code, no write
  5  receipt whose tool path is absent at rev -> refused with an explicit code
  6  run with --out under /tmp -> refused (Q4), nothing written there
  7  `git status --porcelain` in the scratch repo empty before and after run (runner read-only)
  8  two runs of one rev -> identical tool_sha256 and cmd, different utc

Refusal codes other than the digest mismatch are matched generically (`RECEIPT-<CODE>`), so the
fixture binds the runner's contract, not its spelling. All git writes stay inside the scratch
repo; the scratch tree is trap-cleaned on exit, error and signal.
"""
from __future__ import annotations

import atexit
import hashlib
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys

sys.dont_write_bytecode = True
import tempfile
import time
import traceback

SCRATCH_PARENT = "/var/tmp"
FORBIDDEN_OUT_PARENT = "/tmp"
TOOL_REL = "tools/tiny-counter.py"
# The counter prints the lane's counts line (what `verify` insists a counter receipt carries)
# and then echoes its argv, so a spaced argument proves cmd= is really shell-quoted.
COUNTER = """#!/usr/bin/env python3
\"\"\"tiny counter (fixture tool): counts line, then an argv echo.\"\"\"
import sys

argv = sys.argv[1:]
label = argv[1] if len(argv) >= 2 and argv[0] == "--label" else "-"
code = int(argv[argv.index("--fail") + 1]) if "--fail" in argv else 0
print("assertions=4 resolved=3 skipped=1 mismatches=0")
print(f"label={label}")
sys.exit(code)
"""

HEADER_KEYS = ("receipt", "rev", "tool", "tool_sha256", "cmd", "rc", "utc")
FENCE_OUT = "--- stdout ---"
FENCE_ERR = "--- stderr ---"
REV_FULL = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
# An explicit refusal code: an upper-case hyphenated token (RECEIPT-TOOL-DIGEST-MISMATCH,
# RECEIPT-REV-NOT-DURABLE, Q4-...). The contract names one code literally (case 3); the rest
# only have to be explicit, so the fixture binds the behaviour, not the runner's spelling.
CODE = re.compile(r"\b[A-Z][A-Z0-9]*-[A-Z0-9][A-Z0-9-]*\b")
DIGEST_MISMATCH = "RECEIPT-TOOL-DIGEST-MISMATCH"
UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:?\d{2})?$")

_SCRATCH: list[str] = []
_STRAY: list[str] = []


def _cleanup() -> None:
    for path in _STRAY:
        try:
            if os.path.isfile(path):
                os.unlink(path)
        except OSError:
            pass
    for path in _SCRATCH:
        shutil.rmtree(path, ignore_errors=True)


def _trap(signum, _frame):
    _cleanup()
    sys.exit(128 + signum)


def fmt(value: str, limit: int = 160) -> str:
    flat = " ".join(str(value).split())
    return flat if len(flat) <= limit else flat[: limit - 3] + "..."


class Ctx:
    """Scratch repo plus the runner invocation shape."""

    def __init__(self, runner: str) -> None:
        self.runner = runner
        self.scratch = tempfile.mkdtemp(prefix="souji-r23-receipt-", dir=SCRATCH_PARENT)
        _SCRATCH.append(self.scratch)
        self.repo = os.path.join(self.scratch, "repo")
        self.receipts = os.path.join(self.scratch, "receipts")
        self.hooks = os.path.join(self.scratch, "no-hooks")
        os.makedirs(self.repo)
        os.makedirs(self.receipts)
        os.makedirs(self.hooks)
        self.env = dict(os.environ)
        self.env.update(
            {
                "GIT_AUTHOR_NAME": "souji-fixture",
                "GIT_AUTHOR_EMAIL": "fixture@shokunin.local",
                "GIT_COMMITTER_NAME": "souji-fixture",
                "GIT_COMMITTER_EMAIL": "fixture@shokunin.local",
                "GIT_CONFIG_NOSYSTEM": "1",
                "GIT_CONFIG_GLOBAL": os.devnull,
                "GIT_TERMINAL_PROMPT": "0",
                "LC_ALL": "C",
                "TZ": "UTC",
            }
        )
        self.gitbase = [
            "git",
            "-c",
            f"core.hooksPath={self.hooks}",
            "-c",
            "commit.gpgsign=false",
            "-c",
            "tag.gpgsign=false",
            "-c",
            "init.defaultBranch=main",
        ]

    # -- git ---------------------------------------------------------------
    def git(self, *args: str) -> subprocess.CompletedProcess:
        proc = subprocess.run(
            [*self.gitbase, "-C", self.repo, *args],
            capture_output=True,
            text=True,
            errors="replace",
            env=self.env,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"git {' '.join(args)} failed rc={proc.returncode}: "
                f"{fmt(proc.stderr or proc.stdout)}"
            )
        return proc

    def git_out(self, *args: str) -> str:
        return self.git(*args).stdout.strip()

    def status(self) -> str:
        return self.git_out("status", "--porcelain")

    def blob_sha256(self, rev: str, rel: str) -> str:
        proc = subprocess.run(
            [*self.gitbase, "-C", self.repo, "cat-file", "blob", f"{rev}:{rel}"],
            capture_output=True,
            env=self.env,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"cat-file {rev}:{rel} failed")
        return hashlib.sha256(proc.stdout).hexdigest()

    def commit(self, message: str, paths: list[str] | None = None) -> str:
        """Commit. With `paths`, stage only those pathspecs -- so a runner that dirties the
        repo cannot have its droppings swept into the commit and hidden from case 7."""
        if paths:
            self.git("add", "-A", "--", *paths)
        else:
            self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return self.git_out("rev-parse", "HEAD")

    def write(self, rel: str, text: str) -> None:
        path = os.path.join(self.repo, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)

    # -- runner ------------------------------------------------------------
    def run_runner(self, args: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, self.runner, *args],
            capture_output=True,
            text=True,
            errors="replace",
            env=self.env,
        )

    def receipt_run(self, rev: str, out: str, cmd: list[str]) -> subprocess.CompletedProcess:
        return self.run_runner(
            [
                "run",
                "--root",
                self.repo,
                "--rev",
                rev,
                "--tool",
                TOOL_REL,
                "--out",
                out,
                "--",
                *cmd,
            ]
        )

    def counter_cmd(self) -> list[str]:
        # repo-relative: the runner executes the command in a checkout of <rev>, so the receipt
        # re-derives against the named revision's own bytes, not this working tree.
        return [sys.executable, TOOL_REL, "--label", "two words"]


def combined(proc: subprocess.CompletedProcess) -> str:
    return f"{proc.stdout or ''}\n{proc.stderr or ''}"


def codes(proc: subprocess.CompletedProcess) -> str:
    found = sorted(set(CODE.findall(combined(proc))))
    return ",".join(found) if found else "-"


def parse_header(text: str) -> tuple[list[str], list[str], list[str]]:
    lines = text.splitlines()
    out_at = lines.index(FENCE_OUT) if FENCE_OUT in lines else -1
    err_at = lines.index(FENCE_ERR) if FENCE_ERR in lines else -1
    header = lines[: out_at if out_at >= 0 else min(len(lines), len(HEADER_KEYS))]
    stdout = lines[out_at + 1 : err_at] if out_at >= 0 and err_at > out_at else []
    stderr = lines[err_at + 1 :] if err_at >= 0 else []
    return header, stdout, stderr


def header_map(header: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in header:
        if "=" in line:
            key, value = line.split("=", 1)
            out.setdefault(key, value)
    return out


def doctored(text: str, key: str, value: str) -> str:
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            return "\n".join(lines) + "\n"
    raise RuntimeError(f"receipt has no {key}= line to doctor")


# ---------------------------------------------------------------------------
# cases
# ---------------------------------------------------------------------------
def case1(ctx: Ctx, st: dict) -> tuple[bool, str, str]:
    rev = st["rev1"]
    out = os.path.join(ctx.receipts, "c1.receipt")
    cmd = ctx.counter_cmd()
    proc = ctx.receipt_run(rev, out, cmd)
    st["rev1_out"] = out
    st["rev1_cmd"] = cmd
    expect = (
        "rc=0 + receipt written + v1 header order + rc=0 + stdout present + rc=3 recorded as 3"
    )
    if proc.returncode != 0:
        return False, expect, f"runner rc={proc.returncode} codes={codes(proc)} {fmt(proc.stderr)}"
    if not os.path.isfile(out):
        return False, expect, "no receipt file at --out"
    text = open(out, encoding="utf-8", errors="replace").read()
    header, stdout, _stderr = parse_header(text)
    problems: list[str] = []

    def need(cond: bool, msg: str) -> None:
        if not cond:
            problems.append(msg)

    need(len(header) == len(HEADER_KEYS), f"header lines={len(header)} want={len(HEADER_KEYS)}")
    need(bool(header) and header[0] == "receipt=v1", f"line1={fmt(header[0] if header else '')}")
    for i, key in enumerate(HEADER_KEYS):
        if i >= len(header):
            break
        name = header[i].split("=", 1)[0]
        need(name == key, f"line{i + 1} key={name} want={key}")
    need(FENCE_OUT in text.splitlines(), "no stdout fence")
    need(FENCE_ERR in text.splitlines(), "no stderr fence")
    hm = header_map(header)
    need(hm.get("rev") == rev, f"rev={fmt(hm.get('rev', ''))}")
    need(bool(REV_FULL.match(hm.get("rev", ""))), "rev not 40 hex")
    need(hm.get("tool") == TOOL_REL, f"tool={fmt(hm.get('tool', ''))}")
    want_sha = ctx.blob_sha256(rev, TOOL_REL)
    need(bool(SHA256.match(hm.get("tool_sha256", ""))), "tool_sha256 not 64 hex")
    need(hm.get("tool_sha256") == want_sha, f"tool_sha256={fmt(hm.get('tool_sha256', ''))}")
    need(hm.get("rc") == "0", f"receipt rc={fmt(hm.get('rc', ''))}")
    need(bool(UTC.match(hm.get("utc", ""))), f"utc={fmt(hm.get('utc', ''))}")
    try:
        quoted = shlex.split(hm.get("cmd", ""))
    except ValueError as exc:
        quoted = []
        problems.append(f"cmd not shell-parseable ({exc})")
    need(quoted == cmd, f"cmd round-trip={fmt(quoted)}")
    # Presence, not layout: the runner may normalize control characters in the captured output,
    # so the section is matched with whitespace collapsed (a runner that dropped the output, or
    # the spaced argv element, still fails).
    stdout_text = " ".join(" ".join(stdout).split())
    need("mismatches=0" in stdout_text, f"stdout={fmt(stdout)}")
    need("label=two words" in stdout_text, "stdout lost the spaced argv element")
    # rc fidelity: a hard-coded rc=0 would make a failed counter look green, so the same rev is
    # also run through a command that exits 3 and the receipt must record 3.
    fail_out = os.path.join(ctx.receipts, "c1-rc3.receipt")
    proc_fail = ctx.receipt_run(rev, fail_out, [sys.executable, TOOL_REL, "--fail", "3"])
    if proc_fail.returncode != 0 or not os.path.isfile(fail_out):
        problems.append(f"rc-probe run rc={proc_fail.returncode} codes={codes(proc_fail)}")
    else:
        fhead, _fout, _ferr = parse_header(
            open(fail_out, encoding="utf-8", errors="replace").read()
        )
        frc = header_map(fhead).get("rc")
        need(frc == "3", f"rc-probe recorded rc={fmt(frc or '')} want=3")
    if problems:
        return False, expect, "; ".join(problems)
    return (
        True,
        expect,
        f"rc=0 header=v1/7 sha256={want_sha[:12]}... stdout={fmt(stdout_text, 60)} rc_probe=3",
    )


def case2(ctx: Ctx, st: dict) -> tuple[bool, str, str]:
    out = st["rev1_out"]
    proc = ctx.run_runner(["verify", "--root", ctx.repo, out])
    expect = "verify rc=0"
    got = f"rc={proc.returncode} codes={codes(proc)} {fmt(proc.stderr)}"
    return proc.returncode == 0, expect, got


def case3(ctx: Ctx, st: dict) -> tuple[bool, str, str]:
    """A new commit that mutates the tool cannot invalidate a receipt bound to an older rev.

    The old receipt names rev=A, and rev=A's blob is immutable, so a blob-bound verifier must
    still accept it (3a). What must fire is the D3 shape the round exists to close: the OLD
    digest re-filed against the NEW rev (3b) -- the recorded digest is then not the committed
    blob at the named revision, and only RECEIPT-TOOL-DIGEST-MISMATCH is an acceptable answer.
    """
    expect = (
        "old receipt still valid at its own rev after the mutation commit; stale digest at the "
        "new rev -> RECEIPT-TOOL-DIGEST-MISMATCH"
    )
    if "rev2" not in st:
        ctx.write(TOOL_REL, COUNTER + "# mutated after the bound receipt\n")
        st["rev2"] = ctx.commit("mutate counter", [TOOL_REL])
    problems: list[str] = []
    old = open(st["rev1_out"], encoding="utf-8", errors="replace").read()
    proc_old = ctx.run_runner(["verify", "--root", ctx.repo, st["rev1_out"]])
    if proc_old.returncode != 0:
        problems.append(
            f"immutable rev rejected rc={proc_old.returncode} codes={codes(proc_old)}"
        )
    stale = os.path.join(ctx.receipts, "c3-stale-digest.receipt")
    with open(stale, "w", encoding="utf-8") as handle:
        handle.write(doctored(old, "rev", st["rev2"]))
    proc_stale = ctx.run_runner(["verify", "--root", ctx.repo, stale])
    if proc_stale.returncode == 0:
        problems.append("stale digest accepted (rc=0)")
    elif DIGEST_MISMATCH not in combined(proc_stale):
        problems.append(f"stale digest rc={proc_stale.returncode} codes={codes(proc_stale)}")
    if problems:
        return False, expect, "; ".join(problems)
    return (
        True,
        expect,
        f"old_at_rev1=rc0 stale_at_rev2=rc{proc_stale.returncode}/{codes(proc_stale)}",
    )


def case4(ctx: Ctx, st: dict) -> tuple[bool, str, str]:
    expect = "rev=<branch> and rev=<7hex> both refused with RECEIPT-* code, no file written"
    base = open(st["rev1_out"], encoding="utf-8", errors="replace").read()
    branch = ctx.git_out("symbolic-ref", "--short", "HEAD")
    short = st["rev1"][:7]
    results: list[str] = []
    problems: list[str] = []
    for label, value in (("branch", branch), ("short7", short)):
        path = os.path.join(ctx.receipts, f"c4-{label}.receipt")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(doctored(base, "rev", value))
        before_dir = sorted(os.listdir(ctx.receipts))
        before_bytes = open(path, "rb").read()
        proc = ctx.run_runner(["verify", "--root", ctx.repo, path])
        after_dir = sorted(os.listdir(ctx.receipts))
        after_bytes = open(path, "rb").read()
        ok = proc.returncode != 0 and bool(CODE.findall(combined(proc)))
        if not ok:
            problems.append(f"{label}(rev={value}) rc={proc.returncode} codes={codes(proc)}")
        if before_bytes != after_bytes:
            problems.append(f"{label}: receipt rewritten by verify")
        if before_dir != after_dir:
            problems.append(f"{label}: verify created files {set(after_dir) - set(before_dir)}")
        results.append(f"{label}:rc={proc.returncode}/{codes(proc)}")
    if problems:
        return False, expect, "; ".join(problems)
    return True, expect, " ".join(results)


def case5(ctx: Ctx, st: dict) -> tuple[bool, str, str]:
    expect = "tool absent at rev refused with RECEIPT-* code"
    base = open(st["rev1_out"], encoding="utf-8", errors="replace").read()
    path = os.path.join(ctx.receipts, "c5-absent-tool.receipt")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(doctored(base, "tool", "tools/absent-at-rev.py"))
    proc = ctx.run_runner(["verify", "--root", ctx.repo, path])
    ok = proc.returncode != 0 and bool(CODE.findall(combined(proc)))
    return ok, expect, f"rc={proc.returncode} codes={codes(proc)}"


def case6(ctx: Ctx, st: dict) -> tuple[bool, str, str]:
    expect = "run with --out under /tmp refused (Q4), nothing written there"
    out = os.path.join(
        FORBIDDEN_OUT_PARENT, f"souji-r23-should-not-exist-{os.getpid()}-{int(time.time())}.receipt"
    )
    if os.path.exists(out):
        os.unlink(out)
    _STRAY.append(out)
    proc = ctx.receipt_run(st["rev1"], out, ctx.counter_cmd())
    wrote = os.path.exists(out)
    ok = proc.returncode != 0 and bool(CODE.findall(combined(proc))) and not wrote
    got = f"rc={proc.returncode} codes={codes(proc)} wrote_under_tmp={wrote}"
    return ok, expect, got


def case7(ctx: Ctx, st: dict) -> tuple[bool, str, str]:
    expect = "git status --porcelain empty before and after run"
    before = ctx.status()
    out = os.path.join(ctx.receipts, "c7-readonly.receipt")
    proc = ctx.receipt_run(st["rev2"], out, ctx.counter_cmd())
    after = ctx.status()
    ok = before == "" and after == "" and proc.returncode == 0 and os.path.isfile(out)
    got = (
        f"before={fmt(before) or 'empty'} after={fmt(after) or 'empty'} "
        f"runner_rc={proc.returncode}"
    )
    return ok, expect, got


def case8(ctx: Ctx, st: dict) -> tuple[bool, str, str]:
    expect = "same tool_sha256 + same cmd, different utc"
    rev = st["rev2"]
    paths = [os.path.join(ctx.receipts, f"c8-{i}.receipt") for i in (1, 2)]
    procs = []
    for i, path in enumerate(paths):
        procs.append(ctx.receipt_run(rev, path, ctx.counter_cmd()))
        if i == 0:
            time.sleep(1.2)  # ISO8601 second granularity: utc must be able to differ
    if any(p.returncode != 0 for p in procs) or not all(os.path.isfile(p) for p in paths):
        return (
            False,
            expect,
            f"runner rc={[p.returncode for p in procs]} codes={[codes(p) for p in procs]}",
        )
    maps = []
    for path in paths:
        text = open(path, encoding="utf-8", errors="replace").read()
        header, _out, _err = parse_header(text)
        maps.append(header_map(header))
    same_sha = maps[0].get("tool_sha256") == maps[1].get("tool_sha256")
    same_cmd = maps[0].get("cmd") == maps[1].get("cmd")
    diff_utc = maps[0].get("utc") != maps[1].get("utc")
    ok = same_sha and same_cmd and diff_utc
    got = (
        f"sha_equal={same_sha} cmd_equal={same_cmd} utc_equal={not diff_utc} "
        f"utc=[{fmt(maps[0].get('utc', ''), 40)}, {fmt(maps[1].get('utc', ''), 40)}]"
    )
    return ok, expect, got


CASES = (
    (1, case1),
    (2, case2),
    (3, case3),
    (4, case4),
    (5, case5),
    (6, case6),
    (7, case7),
    (8, case8),
)


def find_runner(explicit: str | None) -> str | None:
    cands: list[str] = []
    if explicit:
        cands.append(explicit)
    env = os.environ.get("SOUJI_RECEIPT_RUN")
    if env:
        cands.append(env)
    for base in (os.path.dirname(os.path.abspath(__file__)), os.getcwd()):
        here = base
        for _ in range(6):
            cands.append(os.path.join(here, "tools", "souji-receipt-run.py"))
            parent = os.path.dirname(here)
            if parent == here:
                break
            here = parent
    for cand in cands:
        if cand and os.path.isfile(cand):
            return os.path.abspath(cand)
    return None


def main(argv: list[str]) -> int:
    atexit.register(_cleanup)
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(sig, _trap)

    explicit = argv[1] if len(argv) > 1 else None
    runner = find_runner(explicit)
    if runner is None:
        print("case=0 expect=<runner tools/souji-receipt-run.py> got=<not found>")
        print("selftest=0/1")
        return 1
    print(f"runner={runner}")

    ctx = Ctx(runner)
    ctx.git("init", "-q")
    ctx.write(TOOL_REL, COUNTER)
    ctx.write("README.md", "fixture repo for the C2 receipt runner\n")
    st: dict = {}
    st["rev1"] = ctx.commit("fixture commit")

    passed = 0
    for number, case in CASES:
        try:
            ok, expect, got = case(ctx, st)
        except Exception as exc:  # a crash is a failure, never a pass
            ok, expect, got = (
                False,
                f"case {number}",
                f"error={fmt(exc)} at {fmt(traceback.extract_tb(exc.__traceback__)[-1].lineno)}",
            )
        passed += 1 if ok else 0
        print(f"case={number} expect=<{fmt(expect)}> got=<{fmt(got)}>")
    print(f"selftest={passed}/{len(CASES)}")
    return 0 if passed == len(CASES) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
