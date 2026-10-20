#!/usr/bin/env python3
"""r14-census-boundary.py — C2 isolation fixture for tools/souji-census.sh.

The fixture builds a synthetic HOME under /var/tmp whose agent store
(<home>/.omp/agent) contains a small real repository, a valid compare TSV,
a fake gitdir, and a canary string. It never touches the real ~/.omp tree.

Each case invokes the tool under `strace -f` with PATH spies for
find/du/git/cat/head/tail that log the cwd, argv, and selected GIT_*
environment values. Two independent access checks are applied:

  * spies: no forbidden tool invocation on a refusal case; on a positive
    case, no logged path or environment value contains the synthetic store;
  * strace: no open/openat/getdents64 below the synthetic store on a
    refusal or positive case. The initial execve (the tool itself, whose
    argv carries the user-supplied path) is ignored; later execve lines
    are checked for the store string.

The canary content must never appear on stdout or stderr. The fixture
exits 2 if strace cannot trace, if a required tool is absent, or on usage
error. Baseline discrimination: pass `--tool /var/tmp/<baseline>.sh`
(a31642d's tools/souji-census.sh). Red cases fail on baseline because the
baseline follows aliases/roots and its exit/finding are not the guarded
contract; green controls (safe normal, scratch symlink) pass on both.

Q4: scratch is /var/tmp only and is removed in a finally block. No
/dev/shm, no real credential path, no live census.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shlex
import signal
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HEADER = "repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags"
FINDING = "path-protected"
CANARY = "R14C2-CANARY-6b1f9d2e-do-not-emit"
EXPECTED_IDS = (
    "R14C2-01",
    "R14C2-02",
    "R14C2-03",
    "R14C2-04",
    "R14C2-05",
    "R14C2-06",
    "R14C2-07",
    "R14C2-08",
    "R14C2-09",
    "R14C2-10",
    "R14C2-11",
    "R14C2-12",
)
FORBIDDEN = ("find", "du", "git", "cat", "head", "tail")
SPY_TOOLS = FORBIDDEN + ("readlink", "stat", "realpath")
BASELINE_SHA = "6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026"
GIT_ENV = (
    "GIT_DIR",
    "GIT_COMMON_DIR",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_CONFIG_COUNT",
    "GIT_CONFIG_KEY_0",
    "GIT_CONFIG_VALUE_0",
)

SCRATCH: Path
HOME: Path
STORE: Path
AGENT: Path
SESSIONS: Path
LEAK: Path
GD: Path
RECORDS: Path
SAFE_FLEET: Path
NORMAL: Path
SCRATCH_FLEET: Path
SCRATCH_REPO: Path
GF_REPO: Path
GS_REPO: Path
GC_REPO: Path
SAFE_GD: Path
WT_OWNER: Path
WT_BAD: Path
ALT_REPO: Path
SAFE_ALT: Path
SYMLINK_FLEET: Path
NORMAL2: Path
SPYDIR: Path
SPYLOG: Path
TRACELOG: Path
TOOL: Path
REAL: dict[str, str]


class Result:
    def __init__(
        self,
        rc: int,
        out: str,
        err: str,
        spy: list[str],
        trace: list[str],
        trace_ok: bool,
    ):
        self.rc = rc
        self.out = out
        self.err = err
        self.spy = spy
        self.trace = trace
        self.trace_ok = trace_ok


def die(message: str) -> "None":
    print(f"r14-census-boundary: {message}", file=sys.stderr)
    raise SystemExit(2)


def run_isolated(
    command: list[str],
    *,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    timeout: int,
    errors: str | None = None,
):
    proc = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        errors=errors,
        start_new_session=True,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            kill_session(proc.pid)
        finally:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.communicate()
        raise
    return subprocess.CompletedProcess(command, proc.returncode, stdout, stderr)


def kill_session(session_id: int) -> None:
    members = []
    try:
        with os.scandir("/proc") as entries:
            for entry in entries:
                if not entry.name.isdecimal():
                    continue
                try:
                    # After `(comm)`, field 3 is state and field 6 is session.
                    stat = Path(entry.path, "stat").read_bytes()
                    fields = stat.rsplit(b")", 1)[1].split()
                    if int(fields[3]) == session_id:
                        members.append(int(entry.name))
                except (OSError, IndexError, ValueError):
                    continue
    except OSError:
        pass
    for pid in sorted(members):
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass


def run_setup(command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None):
    proc = run_isolated(
        command,
        cwd=str(cwd) if cwd else None,
        env=env,
        timeout=60,
        errors="replace",
    )
    if proc.returncode != 0:
        die(f"setup command failed ({proc.returncode}): {' '.join(command)}: {proc.stderr.strip()}")
    return proc


def git_env() -> dict[str, str]:
    return {
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "HOME": str(HOME),
        "LC_ALL": "C",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_SYSTEM": "/dev/null",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "r14-census-boundary",
        "GIT_AUTHOR_EMAIL": "r14@example.invalid",
        "GIT_COMMITTER_NAME": "r14-census-boundary",
        "GIT_COMMITTER_EMAIL": "r14@example.invalid",
    }


def git(repo: Path, *args: str) -> str:
    proc = run_setup(
        [REAL["git"], "-c", "maintenance.auto=false", "-C", str(repo), *args],
        env=git_env(),
    )
    return proc.stdout


def init_repo(path: Path) -> None:
    path.mkdir()
    git(path, "init", "-q", "--initial-branch", "master")
    (path / "kept.txt").write_text("kept\n", encoding="utf-8")
    (path / ".gitignore").write_text(".scratch\n", encoding="utf-8")
    git(path, "add", "--", "kept.txt", ".gitignore")
    git(path, "commit", "-qm", "c1")
    head = git(path, "rev-parse", "HEAD").strip()
    git(path, "update-ref", "refs/remotes/origin/master", head)


def make_spy(name: str, real: str) -> None:
    spy = SPYDIR / name
    log = shlex.quote(str(SPYLOG))
    lines = [
        "#!/bin/sh\n",
        f"printf '%s\\t%s\\t' {shlex.quote(name)} \"$PWD\" >> {log}\n",
        f"printf '%s ' \"$@\" >> {log}\n",
        f"printf '\\n' >> {log}\n",
    ]
    for var in GIT_ENV:
        lines.append(f"printf 'ENV\\t{var}\\t%s\\n' \"${{{var}-}}\" >> {log}\n")
    lines.append(f"exec {shlex.quote(real)} \"$@\"\n")
    spy.write_text("".join(lines), encoding="utf-8")
    spy.chmod(0o755)


def build_world() -> None:
    global HOME, STORE, AGENT, SESSIONS, LEAK, GD, RECORDS
    global SAFE_FLEET, NORMAL, SCRATCH_FLEET, SCRATCH_REPO
    global GF_REPO, GS_REPO, GC_REPO, SAFE_GD, SPYDIR, SPYLOG, TRACELOG, REAL
    global WT_OWNER, WT_BAD, ALT_REPO, SAFE_ALT
    global SYMLINK_FLEET, NORMAL2

    REAL = {}
    for name in (*SPY_TOOLS, "strace"):
        found = shutil.which(name)
        if not found:
            die(f"required tool not found: {name}")
        REAL[name] = found

    HOME = SCRATCH / "home"
    STORE = HOME / ".omp"
    AGENT = STORE / "agent"
    SESSIONS = AGENT / "sessions"
    LEAK = AGENT / "leak-repo"
    GD = AGENT / "gitdir"
    RECORDS = AGENT / "records.tsv"
    AGENT.mkdir(parents=True)
    SESSIONS.mkdir()
    (AGENT / "config.yml").write_text(f"server:\n  token: {CANARY}\n", encoding="utf-8")
    (SESSIONS / "session.json").write_text('{"token": "' + CANARY + '"}\n', encoding="utf-8")
    RECORDS.write_text(
        HEADER + "\n" + f"{LEAK}\t0\t0\t0\t0\t2026-10-20T00:00:00+00:00\tclean\n",
        encoding="utf-8",
    )
    (GD / "refs" / "heads").mkdir(parents=True)
    (GD / "objects").mkdir()
    (GD / "HEAD").write_text("ref: refs/heads/master\n", encoding="utf-8")
    (GD / "config").write_text(
        "[core]\n\trepositoryformatversion = 0\n\tbare = true\n", encoding="utf-8"
    )

    # A real repo inside the synthetic store: baseline ancestor/root runs
    # git/find there; the guarded tool refuses before the store root.
    init_repo(LEAK)

    SAFE_FLEET = SCRATCH / "safe-fleet"
    SAFE_FLEET.mkdir()
    NORMAL = SAFE_FLEET / "normal-shokunin"
    init_repo(NORMAL)

    SCRATCH_FLEET = SCRATCH / "scratch-fleet"
    SCRATCH_FLEET.mkdir()
    SCRATCH_REPO = SCRATCH_FLEET / "scratch-shokunin"
    init_repo(SCRATCH_REPO)
    os.symlink(AGENT, SCRATCH_REPO / ".scratch")

    GF_REPO = SCRATCH / "gitfile-alias"
    GF_REPO.mkdir()
    (GF_REPO / ".git").write_text(f"gitdir: {GD}\n", encoding="utf-8")

    GS_REPO = SCRATCH / "gitsymlink-alias"
    GS_REPO.mkdir()
    os.symlink(GD, GS_REPO / ".git")

    SAFE_GD = SCRATCH / "safe-gitdir"
    SAFE_GD.mkdir()
    (SAFE_GD / "commondir").write_text(f"{GD}\n", encoding="utf-8")
    (SAFE_GD / "HEAD").write_text("ref: refs/heads/master\n", encoding="utf-8")
    (SAFE_GD / "objects").mkdir()
    (SAFE_GD / "refs" / "heads").mkdir(parents=True)
    GC_REPO = SCRATCH / "commondir-alias"
    GC_REPO.mkdir()
    (GC_REPO / ".git").write_text(f"gitdir: {SAFE_GD}\n", encoding="utf-8")

    WT_OWNER = SCRATCH / "wt-owner"
    init_repo(WT_OWNER)
    WT_BAD = SCRATCH / "wt-bad"
    WT_BAD.mkdir()
    wt_admin = WT_OWNER / ".git" / "worktrees" / "wt-bad"
    wt_admin.mkdir(parents=True)
    (wt_admin / "HEAD").write_text("ref: refs/heads/master\n", encoding="utf-8")
    (wt_admin / "commondir").write_text(f"{GD}\n", encoding="utf-8")
    (wt_admin / "gitdir").write_text(str(WT_BAD / ".git") + "\n", encoding="utf-8")
    (WT_BAD / ".git").write_text(f"gitdir: {wt_admin}\n", encoding="utf-8")

    SAFE_ALT = SCRATCH / "safe-alt"
    (SAFE_ALT / "info").mkdir(parents=True)
    (SAFE_ALT / "info" / "alternates").write_text(f"{GD / 'objects'}\n", encoding="utf-8")
    alt_src = SCRATCH / "alt-src"
    init_repo(alt_src)
    for entry in (alt_src / ".git" / "objects").iterdir():
        if entry.name == "info":
            continue
        dest = GD / "objects" / entry.name
        if entry.is_dir():
            shutil.copytree(entry, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(entry, dest)
    ALT_REPO = SCRATCH / "alt-repo"
    ALT_REPO.mkdir()
    git(ALT_REPO, "init", "-q", "--initial-branch", "master")
    alt_head = git(alt_src, "rev-parse", "HEAD").strip()
    (ALT_REPO / ".git" / "objects" / "info").mkdir(parents=True, exist_ok=True)
    (ALT_REPO / ".git" / "objects" / "info" / "alternates").write_text(
        f"{SAFE_ALT}\n", encoding="utf-8"
    )
    (ALT_REPO / ".git" / "refs" / "heads").mkdir(parents=True, exist_ok=True)
    (ALT_REPO / ".git" / "refs" / "heads" / "master").write_text(
        alt_head + "\n", encoding="utf-8"
    )

    SYMLINK_FLEET = SCRATCH / "symlink-fleet"
    SYMLINK_FLEET.mkdir()
    NORMAL2 = SYMLINK_FLEET / "normal2-shokunin"
    init_repo(NORMAL2)
    os.symlink(LEAK, SYMLINK_FLEET / "alias-child")

    os.symlink(AGENT, SCRATCH / "root-alias")
    os.symlink(RECORDS, SCRATCH / "compare-alias.tsv")
    os.symlink(LEAK, HOME / "agent-alias")

    SPYDIR = SCRATCH / "spy"
    SPYDIR.mkdir()
    SPYLOG = SCRATCH / "spy.log"
    TRACELOG = SCRATCH / "strace.log"
    SPYLOG.write_text("", encoding="utf-8")

    for name in SPY_TOOLS:
        make_spy(name, REAL[name])

    # The store root is 000, so any stray access is an EACCES the strace
    # oracle can see; sessions is unreadable as a second sentinel. Chmod
    # children first: lookups through AGENT would fail after 000.
    os.chmod(SESSIONS, 0o000)
    os.chmod(LEAK, 0o755)
    os.chmod(AGENT, 0o000)


def probe_strace() -> None:
    probe = SCRATCH / "strace-probe.log"
    env = {
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "HOME": str(HOME),
        "LC_ALL": "C",
    }
    try:
        proc = run_isolated(
            [
                REAL["strace"],
                "-f",
                "-qq",
                "-y",
                "-e",
                "trace=%file,getdents64,execve",
                "-o",
                str(probe),
                "--",
                "/bin/sh",
                "-c",
                'cat "$1"',
                "sh",
                str(AGENT / "config.yml"),
            ],
            env=env,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        die(f"strace could not be executed: {exc}")
    if not probe.exists():
        die("strace probe produced no log")
    text = probe.read_text(encoding="utf-8", errors="replace")
    if proc.returncode == 0 or "EACCES" not in text or str(AGENT) not in text:
        die("strace probe did not observe a denied read of the synthetic store")


def run_tool(args: list[str], extra_env: dict[str, str] | None = None) -> Result:
    SPYLOG.write_text("", encoding="utf-8")
    if TRACELOG.exists():
        TRACELOG.unlink()
    env = {
        "PATH": f"{SPYDIR}:/usr/local/bin:/usr/bin:/bin",
        "HOME": str(HOME),
        "TMPDIR": "/var/tmp",
        "LC_ALL": "C",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_SYSTEM": "/dev/null",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_TERMINAL_PROMPT": "0",
    }
    if extra_env:
        env.update(extra_env)
    command = [
        REAL["strace"],
        "-f",
        "-qq",
        "-y",
        "-e",
        "trace=%file,getdents64,execve",
        "-o",
        str(TRACELOG),
        "--",
        "bash",
        str(TOOL),
        *args,
    ]
    try:
        proc = run_isolated(
            command,
            cwd=str(SCRATCH),
            env=env,
            timeout=90,
            errors="replace",
        )
    except subprocess.TimeoutExpired:
        return Result(124, "", "timeout", [], [], TRACELOG.exists() and TRACELOG.stat().st_size > 0)
    except OSError as exc:
        return Result(127, "", f"exec failed: {exc}", [], [], False)
    spy = SPYLOG.read_text(encoding="utf-8", errors="replace").splitlines()
    trace_ok = TRACELOG.exists() and TRACELOG.stat().st_size > 0
    trace = (
        TRACELOG.read_text(encoding="utf-8", errors="replace").splitlines()
        if trace_ok
        else []
    )
    return Result(proc.returncode, proc.stdout, proc.stderr, spy, trace, trace_ok)


def quoted_abs_paths(line: str) -> list[str]:
    parts = line.split('"')
    return [parts[i] for i in range(1, len(parts), 2) if parts[i].startswith("/")]


def trace_access(
    trace: list[str], *, allow_root_stat: bool = True, follow_open_symlinks: bool = False
) -> list[str]:
    """Store access evidence: EACCES anywhere; readlink whose path argument
    is the store or below it; an open/getdents/exec naming the store; or a
    stat naming the store (descendant always, the bare root only when
    allow_root_stat is false). The lenient root-stat mode keeps the legacy
    scratch-symlink control green, where baseline `-e` stats the store root.
    """
    hits: list[str] = []
    seen_exec = False
    agent = str(AGENT)
    descendant = agent + "/"
    stat_tokens = ("newfstatat(", "statx(", "lstat(", "stat(", "access(", "faccessat(")
    for line in trace:
        if "EACCES" in line:
            hits.append(line)
            continue
        if "readlink(" in line:
            start = line.find('readlink("')
            if start >= 0:
                start += len('readlink("')
                end = line.find('"', start)
                path = line[start:end] if end >= 0 else ""
                if path == agent or path.startswith(descendant):
                    hits.append(line)
            continue
        if "execve(" in line:
            if not seen_exec:
                seen_exec = True
                continue
            if agent in line:
                hits.append(line)
            continue
        if agent not in line:
            continue
        if any(token in line for token in ("openat(", "open(", "getdents64(")):
            if agent in line:
                hits.append(line)
                continue
            if follow_open_symlinks:
                for path in quoted_abs_paths(line):
                    real = os.path.realpath(path)
                    if real == agent or real.startswith(descendant):
                        hits.append(line)
                        break
            continue
        if any(token in line for token in stat_tokens):
            if descendant in line or not allow_root_stat:
                hits.append(line)
    return hits


def spy_hits(spy: list[str]) -> list[str]:
    return [line for line in spy if str(AGENT) in line]





def refusal_problems(res: Result, *, empty_stdout: bool = True) -> list[str]:
    problems: list[str] = []
    if not res.trace_ok:
        problems.append("contract: strace log missing or empty")
    if res.rc != 2:
        problems.append(f"contract: exit={res.rc} want 2")
    if FINDING not in res.err:
        problems.append("contract: finding path-protected missing from stderr")
    if CANARY in res.out + res.err:
        problems.append("contract: canary content leaked")
    if empty_stdout and res.out.strip():
        problems.append("contract: stdout is not empty")
    if str(AGENT) in res.out:
        problems.append("contract: synthetic store path in stdout")
    forbidden = spy_hits(res.spy)
    if forbidden:
        problems.append("access: spy recorded store path: " + " | ".join(forbidden[:2]))
    hits = trace_access(
        res.trace, allow_root_stat=False, follow_open_symlinks=True
    )
    if hits:
        problems.append("access: strace store access: " + " | ".join(hits[:2]))
    return problems


def positive_problems(res: Result, repo: Path, *, scratch: bool = False) -> list[str]:
    problems: list[str] = []
    if not res.trace_ok:
        problems.append("strace log missing or empty")
    if res.rc != 0:
        problems.append(f"exit={res.rc} want 0")
    if not res.out.startswith(HEADER + "\n"):
        problems.append("census header missing")
    rows = [line for line in res.out.splitlines() if line.startswith(str(repo) + "\t")]
    if len(rows) != 1:
        problems.append(f"row count {len(rows)} for {repo.name}, want 1")
    else:
        fields = rows[0].split("\t")
        if len(fields) != 7:
            problems.append(f"row has {len(fields)} columns, want 7")
        else:
            if fields[1] != "1":
                problems.append(f"worktrees={fields[1]} want 1")
            if fields[2] != "0":
                problems.append(f"unpushed={fields[2]} want 0")
            if fields[3] != "0":
                problems.append(f"dirty={fields[3]} want 0")
            if fields[6] != "clean":
                problems.append(f"verdict_flags={fields[6]} want clean")
            if scratch and fields[4] != "0":
                problems.append(f"scratch_bytes={fields[4]} want 0 for a symlink")
    if CANARY in res.out + res.err:
        problems.append("contract: canary content leaked")
    if str(AGENT) in res.out + res.err:
        problems.append("contract: synthetic store path in output")
    hits = spy_hits(res.spy)
    if hits:
        problems.append("access: spy recorded store path: " + " | ".join(hits[:2]))
    trace = trace_access(res.trace, allow_root_stat=scratch)
    if trace:
        problems.append("access: strace store access: " + " | ".join(trace[:2]))
    return problems


def case_01() -> list[str]:
    return refusal_problems(run_tool(["--root", str(AGENT)]))


def case_02() -> list[str]:
    return refusal_problems(run_tool(["--root", str(SESSIONS)]))


def case_03() -> list[str]:
    return refusal_problems(run_tool(["--root", str(HOME)]))


def case_04() -> list[str]:
    problems = []
    for label, root in (
        ("alias", str(SCRATCH / "root-alias")),
        ("dotdot", str(SCRATCH / "root-alias" / "..")),
    ):
        res = run_tool(["--root", root])
        problems.extend(f"{label}: {item}" for item in refusal_problems(res))
    return problems


def case_05() -> list[str]:
    problems = []
    for label, compare in (
        ("direct", str(RECORDS)),
        ("alias", str(SCRATCH / "compare-alias.tsv")),
        ("proc-fd", "/proc/self/fd/999"),
    ):
        res = run_tool(["--root", str(SAFE_FLEET), "--compare", compare])
        problems.extend(f"{label}: {item}" for item in refusal_problems(res))
    return problems


def case_06() -> list[str]:
    problems = []
    for label, root in (
        ("gitfile", GF_REPO),
        ("git-symlink", GS_REPO),
        ("commondir", GC_REPO),
    ):
        res = run_tool(["--root", str(root), "--include-root"])
        problems.extend(f"{label}: {item}" for item in refusal_problems(res))
    return problems


def case_07() -> list[str]:
    return positive_problems(run_tool(["--root", str(SAFE_FLEET)]), NORMAL)


def case_08() -> list[str]:
    return positive_problems(
        run_tool(["--root", str(SCRATCH_FLEET)]), SCRATCH_REPO, scratch=True
    )


def case_09() -> list[str]:
    extra = {
        "GIT_DIR": str(GD),
        "GIT_COMMON_DIR": str(GD),
        "GIT_OBJECT_DIRECTORY": str(GD / "objects"),
        "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(GD / "objects"),
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "core.worktree",
        "GIT_CONFIG_VALUE_0": str(GD),
    }
    problems = ["base: " + item for item in positive_problems(run_tool(["--root", str(SAFE_FLEET)], extra), NORMAL)]
    poisoned = run_tool(["--root", str(SAFE_FLEET)], {"HOME": str(AGENT)})
    problems.extend("home-store: " + item for item in positive_problems(poisoned, NORMAL))
    return problems


def case_10() -> list[str]:
    return refusal_problems(run_tool(["--root", str(WT_OWNER), "--include-root"]))


def case_11() -> list[str]:
    return refusal_problems(run_tool(["--root", str(ALT_REPO), "--include-root"]))


def case_12() -> list[str]:
    return positive_problems(run_tool(["--root", str(SYMLINK_FLEET)]), NORMAL2)


CASES = {
    "R14C2-01": case_01,
    "R14C2-02": case_02,
    "R14C2-03": case_03,
    "R14C2-04": case_04,
    "R14C2-05": case_05,
    "R14C2-06": case_06,
    "R14C2-07": case_07,
    "R14C2-08": case_08,
    "R14C2-09": case_09,
    "R14C2-10": case_10,
    "R14C2-11": case_11,
    "R14C2-12": case_12,
}


def cleanup() -> None:
    try:
        if "AGENT" in globals() and AGENT.exists():
            os.chmod(AGENT, 0o700)
        if "SESSIONS" in globals() and SESSIONS.exists():
            os.chmod(SESSIONS, 0o700)
    except OSError:
        pass
    if "SCRATCH" in globals():
        shutil.rmtree(SCRATCH, ignore_errors=True)


def main(argv: list[str]) -> int:
    global SCRATCH, TOOL

    parser = argparse.ArgumentParser(
        prog="r14-census-boundary.py",
        description="C2 census protected-boundary isolation fixture",
    )
    parser.add_argument("--tool", help="census tool under test (default: lane tools/souji-census.sh)")
    parser.add_argument("--case", action="append", default=[], metavar="ID", help="run one case (repeatable)")
    parser.add_argument("--list", action="store_true", help="print case ids and exit")
    args = parser.parse_args(argv)

    if args.list:
        for cid in EXPECTED_IDS:
            print(cid)
        return 0

    selected = list(args.case) if args.case else list(EXPECTED_IDS)
    unknown = [cid for cid in selected if cid not in CASES]
    if unknown:
        die(f"unknown case id: {', '.join(unknown)}")
    if os.geteuid() == 0:
        die("refusing to run as root: mode-000 store would not be denied")

    TOOL = Path(args.tool) if args.tool else Path(__file__).resolve().parents[2] / "tools" / "souji-census.sh"
    TOOL = TOOL.resolve()
    if not TOOL.is_file():
        die(f"tool not readable: {TOOL}")
    try:
        TOOL.read_bytes()
    except OSError as exc:
        die(f"tool not readable: {TOOL}: {exc}")

    try:
        SCRATCH = Path(tempfile.mkdtemp(prefix="r14-census-boundary.", dir="/var/tmp"))
    except OSError as exc:
        die(f"cannot create /var/tmp fixture: {exc}")
    try:
        try:
            build_world()
            probe_strace()
        except SystemExit:
            raise
        except Exception as exc:
            die(f"setup failed: {exc}")
        digest = hashlib.sha256(TOOL.read_bytes()).hexdigest()
        is_baseline = digest == BASELINE_SHA
        print(f"TOOL\t{TOOL}\tsha256={digest}")
        print("TOOL-KIND\tbaseline-a31642d" if is_baseline else "TOOL-KIND\tother")
        failed = 0
        ran: list[str] = []
        for cid in selected:
            problems = CASES[cid]()
            if (
                is_baseline
                and cid not in ("R14C2-07", "R14C2-08")
                and not any("access:" in item for item in problems)
            ):
                problems.append("access: baseline red case has no observed store access")
            if problems:
                failed += 1
                print(f"CASE\t{cid}\tFAIL\t" + "; ".join(problems))
            else:
                print(f"CASE\t{cid}\tPASS\tok")
            ran.append(cid)
        if not args.case and tuple(ran) != EXPECTED_IDS:
            failed += 1
            print(
                "CASE\tid-set\tFAIL\t"
                f"ran={','.join(ran)} expected={','.join(EXPECTED_IDS)}"
            )
        print(f"SUMMARY\ttotal={len(ran)}\tfailed={failed}")
        return 0 if failed == 0 else 1
    finally:
        cleanup()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
