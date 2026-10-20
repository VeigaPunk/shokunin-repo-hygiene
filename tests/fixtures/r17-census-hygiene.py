#!/usr/bin/env python3
"""r17-census-hygiene.py — C1 operability fixture for tools/souji-census.sh.

Round 17 hygiene cases, built fresh under a private /var/tmp directory per
run; HOME/XDG/GIT_CONFIG_* are pinned so host config can never leak in.

D1 (untracked-visibility): a repo-local/included/config.worktree
`status.showUntrackedFiles` suppression must not yield a false clean row —
the repaired census pins `--untracked-files=normal` so the untracked
collapse matches git's default `normal` mode exactly. Covered vectors:
repo-local config (`no`, `false`, `0`, `off`), include.path to a benign
file inside .git, extensions.worktreeConfig + config.worktree (own repo
and a linked worktree's admin), `all` vs `normal` collapse equality, an
invalid value (status fails eagerly even with the pinned flag: honest
status-unverifiable on every arm), and honest-clean controls (no
untracked file; only ignored files).
D2 (attributes kind guard): a hardlinked or non-regular (FIFO, socket,
device, symlink-to-nonregular) $GIT_DIR/info/attributes degrades to a
per-repository `error` row with exit 0, a `git-metadata-unsupported`
stderr diagnostic naming the repo or the bad path, and no `git -C` call
into that repository; neighbours' rows are byte-identical to a run
without the bad repo. Pinned outcomes: a directory or an in-gitdir
dangling symlink at info/attributes is a NORMAL row (git reads it as
absent); every other guard_git_files entry and every protected-namespace
or git-metadata-symlink refusal keeps whole-run exit 2 — including when a
degraded info/attributes sits in the same repository (hardlinked config,
hardlinked alternates, protected include.path, escaping symlink).

Callsites covered: main .git (:831), linked-worktree .git file (:873),
registered-worktree admin (:790), gitfile admin commondir (:891); the
commondir branch of a .git-dir repo (:849) is covered by the divergent
commondir case. A linked worktree child is never a fleet row
(census :1371-1374); it is exercised through --root <wt> --include-root
and through its main repo's wt-dirty flag.

A git spy on PATH records every git invocation; the no-read oracle is a
spy check plus completion inside a 60s process-group timeout (a git that
opens a writer-less FIFO blocks; the run is killed as rc 124 = FAIL,
never SKIP, and every fixture FIFO is unblocked afterwards). Every D2
repo carries a stat-dirty provoker so guardless arms actually reach the
attribute open. RLIMIT_AS=1G caps the /dev/zero arm.

Each CASE detail names its expected class (preserve|repair|refuse).

Usage: python3 r17-census-hygiene.py --census <souji-census.sh>
(--tool is accepted as a matrix-harness alias for --census.)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import socket as socket_mod
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HEADER = "repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags"
FINDING = "path-protected"
SOFT_FINDING = "git-metadata-unsupported"
CONFIG_SOFT = "config-unsupported"
CANARY = "R17HYG-CANARY-8c2e5f41-do-not-emit"
FINDING_RE = re.compile(r"souji-census:\s*([a-z0-9-]+):\s*([a-z0-9-]+)")

EXPECTED_IDS = (
    "R17-01", "R17-02", "R17-03", "R17-04", "R17-05", "R17-06",
    "R17-07", "R17-08", "R17-09", "R17-10", "R17-11", "R17-12",
    "R17-13", "R17-14", "R17-15", "R17-16", "R17-17", "R17-18",
    "R17-19", "R17-20", "R17-21", "R17-22", "R17-23", "R17-24",
    "R17-25", "R17-26", "R17-27", "R17-28", "R17-29",
)

# Pinned, non-adaptive case classes: preserve = unchanged correct
# behaviour, repair = D1/D2 behaviour the claim adds, refuse = kept
# whole-run exit-2 surfaces. Asserted in every CASE detail.
CASE_CLASSES = {
    "R17-01": "repair", "R17-02": "repair", "R17-03": "repair",
    "R17-04": "repair",
    "R17-05": "preserve", "R17-06": "preserve",
    "R17-07": "repair", "R17-08": "repair", "R17-09": "repair",
    "R17-10": "refuse", "R17-11": "preserve",
    "R17-12": "refuse", "R17-13": "refuse",
    "R17-14": "repair", "R17-15": "repair", "R17-16": "repair",
    "R17-17": "preserve",
    "R17-18": "refuse", "R17-19": "refuse",
    "R17-20": "repair",
    "R17-21": "preserve", "R17-22": "preserve", "R17-23": "refuse",
    "R17-24": "repair", "R17-25": "refuse",
    "R17-26": "repair",
    "R17-27": "preserve", "R17-28": "preserve", "R17-29": "refuse",
}
# R17-17 is preserve, not repair: git parses an invalid repo-config value
# eagerly, so `git status` fails even with the pinned --untracked-files
# flag (verified on the host: rc 128 both ways). The honest row is
# status-unverifiable on every arm; the repair must not rescue or refuse
# it.
GIT_ENV = (
    "GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM", "GIT_CONFIG_NOSYSTEM",
    "GIT_TERMINAL_PROMPT", "GIT_NO_LAZY_FETCH", "HOME", "XDG_CONFIG_HOME",
)

SCRATCH: Path
HOME: Path
AGENT: Path
SPYDIR: Path
SPYLOG: Path
TOOL: Path
REAL: dict[str, str]
ACTIVE_RUNS: list["Result"]
FIFOS: list[Path]

CLEAN = ("1", "0", "0", "clean")


class Result:
    def __init__(
        self,
        rc: int,
        out: str,
        err: str,
        spy: list[str],
        args: list[str] | None = None,
    ) -> None:
        self.rc = rc
        self.out = out
        self.err = err
        self.spy = spy
        self.args = args or []

    @property
    def finding(self) -> str:
        m = FINDING_RE.search(self.err)
        return f"{m.group(1)}:{m.group(2)}" if m else "none"


def die(message: str) -> "None":
    print(f"r17-census-hygiene: {message}", file=sys.stderr)
    raise SystemExit(2)


# Kill the launched session: bash job control can put a blocked child in a
# different process group while retaining the same session ID.
def kill_session(session: int) -> None:
    try:
        with os.scandir("/proc") as entries:
            for entry in entries:
                if not entry.name.isdecimal():
                    continue
                try:
                    stat = Path(entry.path, "stat").read_text(encoding="utf-8")
                    fields = stat[stat.rfind(")") + 2:].split()
                    # After pid and comm, state/ppid/pgrp/session are fields 0–3.
                    if int(fields[3]) == session:
                        os.kill(int(entry.name), signal.SIGKILL)
                except (OSError, IndexError, ValueError):
                    continue
    except OSError:
        pass
    try:
        os.killpg(session, signal.SIGKILL)
    except OSError:
        pass


# Keep the bounded subprocess lifecycle in one place. `subprocess.run` kills
# only its direct child on timeout, not descendants holding captured pipes.
def run_process_group(
    command: list[str],
    *,
    env: dict[str, str] | None = None,
    cwd: str | None = None,
    timeout: int = 60,
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        errors="replace",
        start_new_session=True,
    )
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        kill_session(proc.pid)
        out, err = proc.communicate()
        raise subprocess.TimeoutExpired(
            command, timeout, output=out, stderr=err
        ) from exc
    return subprocess.CompletedProcess(command, proc.returncode, out, err)


def run_setup(command: list[str], env: dict[str, str] | None = None):
    proc = run_process_group(command, env=env)
    if proc.returncode != 0:
        die(
            f"setup command failed ({proc.returncode}): "
            f"{' '.join(command)}: {proc.stderr.strip()}"
        )
    return proc


def git_env() -> dict[str, str]:
    return {
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "HOME": str(HOME),
        "XDG_CONFIG_HOME": str(HOME / ".config"),
        "LC_ALL": "C",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_SYSTEM": "/dev/null",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "r17-census-hygiene",
        "GIT_AUTHOR_EMAIL": "r17@example.invalid",
        "GIT_COMMITTER_NAME": "r17-census-hygiene",
        "GIT_COMMITTER_EMAIL": "r17@example.invalid",
    }


def git(repo: Path, *args: str) -> str:
    proc = run_setup(
        [REAL["git"], "-c", "maintenance.auto=false", "-C", str(repo), *args],
        env=git_env(),
    )
    return proc.stdout


def init_repo(path: Path, extra_config: str = "") -> Path:
    path.mkdir(parents=True)
    git(path, "init", "-q", "--initial-branch", "master")
    (path / "kept.txt").write_text("kept\n", encoding="utf-8")
    git(path, "add", "--", "kept.txt")
    git(path, "commit", "-qm", "c1")
    head = git(path, "rev-parse", "HEAD").strip()
    git(path, "update-ref", "refs/remotes/origin/master", head)
    if extra_config:
        with (path / ".git" / "config").open("a", encoding="utf-8") as fh:
            fh.write(extra_config)
    return path


def provoke(repo: Path) -> None:
    """Stat-dirty provoker: identical content, bumped mtime. git's status
    content-checks the file, which runs the attribute bootstrap and opens
    $GIT_COMMON_DIR/info/attributes on guardless arms — without it a
    stat-clean repo can pass vacuously."""
    f = repo / "kept.txt"
    t = time.time() + 7
    os.utime(f, (t, t))


def mkfifo(path: Path) -> None:
    os.mkfifo(path)
    FIFOS.append(path)


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
    global HOME, AGENT, SPYDIR, SPYLOG, REAL, FIFOS

    REAL = {}
    for name in ("git", "bash"):
        found = shutil.which(name)
        if not found:
            die(f"required tool not found: {name}")
        REAL[name] = found

    FIFOS = []

    HOME = SCRATCH / "home"
    HOME.mkdir()
    # Protected store: the census guards every ancestor of
    # $HOME/.omp/agent; the canary must never appear in output.
    AGENT = HOME / ".omp" / "agent"
    AGENT.mkdir(parents=True)
    (AGENT / "config.yml").write_text(
        f"server:\n  token: {CANARY}\n", encoding="utf-8"
    )
    (AGENT / "secret.gitconfig").write_text(
        "[user]\n\tname = leak\n", encoding="utf-8"
    )

    SPYDIR = SCRATCH / "spy"
    SPYDIR.mkdir()
    SPYLOG = SCRATCH / "spy.log"
    SPYLOG.touch()
    for name in ("find", "du", "git", "cat", "head", "tail", "readlink",
                 "stat", "realpath", "awk"):
        found = shutil.which(name)
        if found:
            make_spy(name, found)


def run_tool(args: list[str], timeout: int = 60,
             extra_env: dict[str, str] | None = None) -> Result:
    SPYLOG.write_text("", encoding="utf-8")
    env = {
        "PATH": f"{SPYDIR}:/usr/local/bin:/usr/bin:/bin",
        "HOME": str(HOME),
        "XDG_CONFIG_HOME": str(HOME / ".config"),
        "TMPDIR": "/var/tmp",
        "LC_ALL": "C",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_SYSTEM": "/dev/null",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_NO_LAZY_FETCH": "1",
        # Caps the /dev/zero arm: an unguarded git reading NULs unboundedly
        # dies ENOMEM instead of exhausting the host.
        "RLIMIT_AS": "1073741824",
    }
    if extra_env:
        env.update(extra_env)
    command = ["bash", str(TOOL), *args]
    try:
        proc = run_process_group(
            command,
            cwd=str(SCRATCH),
            env=env,
            timeout=timeout,
        )
    except OSError as exc:
        res = Result(127, "", f"exec failed: {exc}", [], args)
        ACTIVE_RUNS.append(res)
        return res
    except subprocess.TimeoutExpired:
        unblock_fifos()
        res = Result(124, "", "timeout", [], args)
        ACTIVE_RUNS.append(res)
        return res
    spy = SPYLOG.read_text(encoding="utf-8", errors="replace").splitlines()
    res = Result(proc.returncode, proc.stdout, proc.stderr, spy, args)
    ACTIVE_RUNS.append(res)
    return res


def unblock_fifos() -> None:
    for p in FIFOS:
        try:
            fd = os.open(str(p), os.O_WRONLY | os.O_NONBLOCK)
        except OSError:
            continue
        os.close(fd)


def rows_by_name(out: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in out.splitlines()[1:]:
        if not line.strip():
            continue
        fields = line.split("\t")
        rows[fields[0].rsplit("/", 1)[-1]] = fields
    return rows


def git_calls_into(res: Result, repo: Path) -> list[str]:
    """Spy-logged git invocations whose -C targets REPO or below — calls
    that could open that repository's info/attributes. Matches the path
    both as spelled and resolved (realpath)."""
    hits: list[str] = []
    bases = {str(repo), os.path.realpath(str(repo))}
    in_git = False
    for line in res.spy:
        if line.startswith("ENV\t"):
            continue
        in_git = line.startswith("git\t")
        if not in_git:
            continue
        fields = line.split("\t", 2)
        if len(fields) < 3:
            continue
        toks = fields[2].split()
        for i, tok in enumerate(toks[:-1]):
            if tok != "-C":
                continue
            tgt = toks[i + 1]
            for base in bases:
                if tgt == base or tgt.startswith(base + "/"):
                    hits.append(line)
                    break
            else:
                continue
            break
    return hits


def contract_problems(res: Result, *, label: str = "") -> list[str]:
    problems: list[str] = []
    if CANARY in res.out + res.err:
        problems.append(f"{label}contract: canary content leaked")
    return problems


def positive_problems(
    res: Result,
    expect: dict[str, tuple[str, str, str, str]],
) -> list[str]:
    problems: list[str] = []
    if res.rc != 0:
        problems.append(f"exit={res.rc} want 0")
        problems.extend(contract_problems(res))
        return problems
    if not res.out.startswith(HEADER + "\n"):
        problems.append("census header missing")
    rows = rows_by_name(res.out)
    want = set(expect)
    got = set(rows)
    if got != want:
        problems.append(f"row set {sorted(got)} want exactly {sorted(want)}")
    for name, (wt, unp, dirty, verdict) in expect.items():
        if name not in rows:
            continue
        fields = rows[name]
        if len(fields) != 7:
            problems.append(f"{name}: row has {len(fields)} columns, want 7")
            continue
        if fields[1] != wt:
            problems.append(f"{name}: worktrees={fields[1]} want {wt}")
        if fields[2] != unp:
            problems.append(f"{name}: unpushed={fields[2]} want {unp}")
        if fields[3] != dirty:
            problems.append(f"{name}: dirty={fields[3]} want {dirty}")
        if fields[4] != "0":
            problems.append(f"{name}: scratch_bytes={fields[4]} want 0")
        if not fields[5]:
            problems.append(f"{name}: mtime_iso empty")
        if fields[6] != verdict:
            problems.append(f"{name}: verdict_flags={fields[6]} want {verdict}")
    problems.extend(contract_problems(res))
    return problems


def refusal_problems(res: Result, *, label: str = "") -> list[str]:
    """Whole-run refusal oracle: exit 2, path-protected finding, empty
    stdout."""
    problems: list[str] = []
    if res.rc != 2:
        problems.append(f"{label}exit={res.rc} want 2")
    if FINDING not in res.err:
        problems.append(f"{label}finding {FINDING} missing from stderr")
    if res.out.strip():
        problems.append(f"{label}stdout is not empty")
    problems.extend(contract_problems(res, label=label))
    return problems


def component_re(name: str) -> "re.Pattern[str]":
    return re.compile(r"(?:^|[/\s(])" + re.escape(name) + r"(?:[/\s):]|$)")


def finding_names(res: Result, alts: list[str]) -> bool:
    """True when a SOFT_FINDING stderr line names one of ALTS as a path
    component."""
    lines = [l for l in res.err.splitlines() if SOFT_FINDING in l]
    return any(component_re(n).search(l) for n in alts for l in lines)


def error_row_problems(fields: list[str] | None, name: str) -> list[str]:
    if fields is None:
        return []
    if len(fields) != 7:
        return [f"{name}: row has {len(fields)} columns, want 7"]
    if fields[1:] != ["0", "0", "0", "0", "", "error"]:
        return [
            f"{name}: row {fields[1:]} want zero counts, empty mtime + error"
        ]
    return []


def degrade_diag_problems(
    res: Result, alts: list[str], expected_diag: int = 1, label: str = ""
) -> list[str]:
    problems: list[str] = []
    n_lines = len([l for l in res.err.splitlines() if SOFT_FINDING in l])
    if n_lines != expected_diag:
        problems.append(
            f"{label}{SOFT_FINDING} line count {n_lines} want {expected_diag}"
        )
    if n_lines and not finding_names(res, alts):
        problems.append(
            f"{label}{SOFT_FINDING} lines name none of {alts}"
        )
    if FINDING in res.err:
        problems.append(
            f"{label}unexpected {FINDING} finding (whole-run refusal)"
        )
    return problems


def degraded_fleet_problems(
    fleet: Path,
    bads: list[str],
    cleans: list[str] | None = None,
    name_alts: dict[str, list[str]] | None = None,
    also_stderr: tuple[str, ...] = (),
) -> list[str]:
    """D2 oracle: run --root on a fleet, then on the same fleet with the
    bad repos parked OUTSIDE it. Exit 0 both times; each bad repo is one
    `error` row with zero counts and empty mtime; clean rows are
    byte-identical across the runs; stderr carries exactly one
    git-metadata-unsupported line per degraded repo naming the repo or the
    bad path (never path-protected); no git -C call enters a degraded
    repo."""
    if cleans is None:
        cleans = [n for n in ("a", "c") if (fleet / n).is_dir()]
    if name_alts is None:
        name_alts = {b: [b] for b in bads}
    problems: list[str] = []

    res = run_tool(["--root", str(fleet)])
    if res.rc == 124:
        problems.append("fleet run timed out (blocked on non-regular metadata)")
        return problems
    if res.rc != 0:
        problems.append(f"exit={res.rc} want 0")
        return problems + contract_problems(res)
    if not res.out.startswith(HEADER + "\n"):
        problems.append("census header missing")
    rows = rows_by_name(res.out)
    want_set = sorted(cleans + bads)
    got = sorted(rows)
    if got != want_set:
        problems.append(f"row set {got} want exactly {want_set}")
    for bad in bads:
        problems.extend(error_row_problems(rows.get(bad), bad))
    for name in cleans:
        fields = rows.get(name)
        if fields is not None and len(fields) == 7 and fields[6] == "error":
            problems.append(f"{name}: degraded to error by neighbour")
    problems.extend(
        degrade_diag_problems(res, [a for b in bads for a in name_alts[b]],
                              expected_diag=len(bads))
    )
    for needle in also_stderr:
        if needle not in res.err:
            problems.append(f"{needle} missing from stderr")
    for bad in bads:
        hits = git_calls_into(res, fleet / bad)
        if hits:
            problems.append(
                f"git call could read degraded metadata ({bad}): "
                + " | ".join(hits[:2])
            )

    # Second run without the bad repos (parked OUTSIDE the fleet): clean
    # rows must be byte-identical.
    park = SCRATCH / f"parked-{fleet.name}"
    park.mkdir()
    for bad in bads:
        (fleet / bad).rename(park / bad)
    try:
        res2 = run_tool(["--root", str(fleet)])
    finally:
        for bad in bads:
            (park / bad).rename(fleet / bad)
    if res2.rc != 0:
        problems.append(f"without-bad exit={res2.rc} want 0")
        return problems + contract_problems(res)
    rows2 = rows_by_name(res2.out)
    if sorted(rows2) != sorted(cleans):
        problems.append(f"without-bad row set {sorted(rows2)} want {sorted(cleans)}")
    for name in cleans:
        r1, r2 = rows.get(name), rows2.get(name)
        if r1 is not None and r2 is not None and r1 != r2:
            problems.append(f"{name}: row changed when bad repos removed: {r1} vs {r2}")
    problems.extend(contract_problems(res))
    return problems


def degraded_root_problems(repo: Path, alts: list[str]) -> list[str]:
    """D2 oracle for one --include-root row (a gitfile linked worktree):
    exit 0, exactly one `error` row, one git-metadata-unsupported line
    naming the repo or the bad path, no git -C into it."""
    problems: list[str] = []
    res = run_tool(["--root", str(repo), "--include-root"])
    if res.rc == 124:
        problems.append(f"{repo.name}: run timed out (blocked)")
        return problems
    if res.rc != 0:
        problems.append(f"{repo.name}: exit={res.rc} want 0")
        return problems + contract_problems(res)
    if not res.out.startswith(HEADER + "\n"):
        problems.append(f"{repo.name}: census header missing")
    rows = rows_by_name(res.out)
    if sorted(rows) != [repo.name]:
        problems.append(f"{repo.name}: row set {sorted(rows)} want [{repo.name}]")
    problems.extend(error_row_problems(rows.get(repo.name), repo.name))
    problems.extend(degrade_diag_problems(res, alts))
    hits = git_calls_into(res, repo)
    if hits:
        problems.append(
            f"{repo.name}: git call could read degraded metadata: "
            + " | ".join(hits[:2])
        )
    problems.extend(contract_problems(res))
    return problems


def d2_fleet(name: str, mutate) -> Path:
    """a/b/c fleet where b's .git/info/attributes is mangled by mutate."""
    fleet = SCRATCH / name
    init_repo(fleet / "a")
    repo_b = init_repo(fleet / "b")
    init_repo(fleet / "c")
    info = repo_b / ".git" / "info"
    info.mkdir(exist_ok=True)
    mutate(info / "attributes", repo_b)
    return fleet


def linked_fleet(name: str, bad_in_admin: bool) -> Path:
    """Fleet a/c/x-main where x-main has a registered linked worktree b
    (a fleet child with a .git FILE — never a row, census :1371-1374).
    bad_in_admin: hardlinked attributes in x-main/.git/worktrees/b/info
    (callsites :790 registration, :873 gitfile); else in x-main/.git/info
    (the common dir: callsites :831 and :891)."""
    fleet = SCRATCH / name
    init_repo(fleet / "a")
    init_repo(fleet / "c")
    x_main = init_repo(fleet / "x-main")
    bdir = fleet / "b"
    git(x_main, "worktree", "add", "-b", "wt-b", str(bdir))
    admin = x_main / ".git" / "worktrees" / "b"
    if bad_in_admin:
        info = admin / "info"
    else:
        info = x_main / ".git" / "info"
    info.mkdir(exist_ok=True)
    attrs = info / "attributes"
    attrs.write_text("* -text\n", encoding="utf-8")
    os.link(attrs, info / "attributes.twin")
    return fleet


def case_01() -> list[str]:
    # repair: repo-local `no`/`false`/`0`/`off` + one untracked file must
    # stay dirty — every false spelling git accepts.
    fleet = SCRATCH / "d1-local-no"
    for name, val in (
        ("r-suf-no", "no"), ("r-suf-false", "false"),
        ("r-suf-zero", "0"), ("r-suf-off", "off"),
    ):
        repo = init_repo(
            fleet / name, f"[status]\n\tshowUntrackedFiles = {val}\n"
        )
        (repo / "untracked.txt").write_text("u\n", encoding="utf-8")
    return positive_problems(
        run_tool(["--root", str(fleet)]),
        {n: ("1", "0", "1", "dirty")
         for n in ("r-suf-no", "r-suf-false", "r-suf-zero", "r-suf-off")},
    )


def case_02() -> list[str]:
    # repair: `no` reached through include.path to a benign file inside the
    # repo's own .git must stay dirty.
    fleet = SCRATCH / "d1-include-no"
    repo = init_repo(
        fleet / "r-suf-inc", "[include]\n\tpath = uf.gitconfig\n"
    )
    (repo / ".git" / "uf.gitconfig").write_text(
        "[status]\n\tshowUntrackedFiles = no\n", encoding="utf-8"
    )
    (repo / "untracked.txt").write_text("u\n", encoding="utf-8")
    return positive_problems(
        run_tool(["--root", str(fleet)]),
        {"r-suf-inc": ("1", "0", "1", "dirty")},
    )


def case_03() -> list[str]:
    # repair: `no` in config.worktree under extensions.worktreeConfig=true
    # must stay dirty.
    fleet = SCRATCH / "d1-worktree-no"
    repo = init_repo(
        fleet / "r-suf-wtc", "[extensions]\n\tworktreeConfig = true\n"
    )
    (repo / ".git" / "config.worktree").write_text(
        "[status]\n\tshowUntrackedFiles = no\n", encoding="utf-8"
    )
    (repo / "untracked.txt").write_text("u\n", encoding="utf-8")
    return positive_problems(
        run_tool(["--root", str(fleet)]),
        {"r-suf-wtc": ("1", "0", "1", "dirty")},
    )


def case_04() -> list[str]:
    # repair: `all` would list the 3-file untracked dir as 3 lines; the
    # pinned `normal` mode must collapse it to one — the same dirty count a
    # `normal` repo gives. Both repos sit in one fleet.
    fleet = SCRATCH / "d1-all-vs-normal"
    repo_all = init_repo(
        fleet / "r-suf-all", "[status]\n\tshowUntrackedFiles = all\n"
    )
    repo_norm = init_repo(fleet / "r-suf-normal")
    for repo in (repo_all, repo_norm):
        d3 = repo / "d3"
        d3.mkdir()
        for leaf in ("a", "b", "c"):
            (d3 / leaf).write_text("x\n", encoding="utf-8")
    res = run_tool(["--root", str(fleet)])
    problems = positive_problems(
        res,
        {"r-suf-all": ("1", "0", "1", "dirty"),
         "r-suf-normal": ("1", "0", "1", "dirty")},
    )
    rows = rows_by_name(res.out)
    a, n = rows.get("r-suf-all"), rows.get("r-suf-normal")
    if a and n and len(a) == 7 and len(n) == 7 and a[3] != n[3]:
        problems.append(
            f"dirty count under `all` ({a[3]}) != `normal` ({n[3]})"
        )
    return problems


def case_05() -> list[str]:
    # preserve: key=no with no untracked file is honestly clean.
    fleet = SCRATCH / "d1-no-clean"
    init_repo(fleet / "r-suf-quiet", "[status]\n\tshowUntrackedFiles = no\n")
    return positive_problems(
        run_tool(["--root", str(fleet)]),
        {"r-suf-quiet": CLEAN},
    )


def case_06() -> list[str]:
    # preserve: key=no with only an ignored file is honestly clean.
    fleet = SCRATCH / "d1-no-ignored"
    repo = init_repo(
        fleet / "r-suf-ign", "[status]\n\tshowUntrackedFiles = no\n"
    )
    (repo / ".git" / "info" / "exclude").write_text(
        "ignored.log\n", encoding="utf-8"
    )
    (repo / "ignored.log").write_text("x\n", encoding="utf-8")
    return positive_problems(
        run_tool(["--root", str(fleet)]),
        {"r-suf-ign": CLEAN},
    )


def case_07() -> list[str]:
    # repair: hardlinked info/attributes degrades b only; b carries real
    # dirt (untracked file + one unpushed commit) so the degrade cannot be
    # a clean-repo shortcut.
    def hardlink(attrs: Path, repo_b: Path) -> None:
        attrs.write_text("* -text\n", encoding="utf-8")
        os.link(attrs, repo_b / ".git" / "info" / "attributes.twin")
        (repo_b / "untracked.txt").write_text("u\n", encoding="utf-8")
        (repo_b / "new.txt").write_text("n\n", encoding="utf-8")
        git(repo_b, "add", "--", "new.txt")
        git(repo_b, "commit", "-qm", "c2")
    fleet = d2_fleet("d2-hardlink", hardlink)
    return degraded_fleet_problems(fleet, ["b"])


def case_08() -> list[str]:
    # repair: FIFO info/attributes degrades b only; the run must finish —
    # a census that opens it blocks (writer-less FIFO open), caught by the
    # 60s process-group kill (rc 124). Stat-dirty provoker forces the
    # attribute consult on guardless arms.
    def fifo(attrs: Path, repo_b: Path) -> None:
        mkfifo(attrs)
        provoke(repo_b)
    fleet = d2_fleet("d2-fifo", fifo)
    return degraded_fleet_problems(fleet, ["b"])


def case_09() -> list[str]:
    # repair: symlink info/attributes -> FIFO inside the gitdir degrades b
    # only (the link itself stays inside its gitdir; the target is
    # non-regular), and the run finishes within the timeout.
    def symlink_fifo(attrs: Path, repo_b: Path) -> None:
        mkfifo(repo_b / ".git" / "info" / "attrs.fifo")
        os.symlink("attrs.fifo", attrs)
        provoke(repo_b)
    fleet = d2_fleet("d2-symlink-fifo", symlink_fifo)
    return degraded_fleet_problems(fleet, ["b"])


def case_10() -> list[str]:
    # refuse: a hardlinked `config` keeps the whole-run exit-2 refusal —
    # the degrade covers info/attributes only.
    fleet = SCRATCH / "d2-config-hardlink"
    init_repo(fleet / "a")
    repo_b = init_repo(fleet / "b")
    init_repo(fleet / "c")
    os.link(repo_b / ".git" / "config", repo_b / ".git" / "config.twin")
    res = run_tool(["--root", str(fleet)])
    return refusal_problems(res)


def case_11() -> list[str]:
    # preserve: plain regular info/attributes leaves all rows normal. The
    # provoker makes git open it for real (a guard that over-degraded a
    # readable regular file would show as an error row).
    fleet = SCRATCH / "d2-regular"
    init_repo(fleet / "a")
    repo_b = init_repo(fleet / "b")
    init_repo(fleet / "c")
    attrs = repo_b / ".git" / "info" / "attributes"
    attrs.write_text("* -text\n", encoding="utf-8")
    provoke(repo_b)
    return positive_problems(
        run_tool(["--root", str(fleet)]),
        {"a": CLEAN, "b": CLEAN, "c": CLEAN},
    )


def case_12() -> list[str]:
    # refuse: a degraded info/attributes must not skip the config scan —
    # an include.path reaching ~/.omp/agent in the SAME repo still refuses
    # the whole run (guard order F3/F8 falsifier).
    def bad_attrs_plus_include(attrs: Path, repo_b: Path) -> None:
        attrs.write_text("* -text\n", encoding="utf-8")
        os.link(attrs, repo_b / ".git" / "info" / "attributes.twin")
        with (repo_b / ".git" / "config").open("a", encoding="utf-8") as fh:
            fh.write("[include]\n\tpath = ~/.omp/agent/secret.gitconfig\n")
    fleet = d2_fleet("d2-attrs-plus-protected-include", bad_attrs_plus_include)
    res = run_tool(["--root", str(fleet)])
    return refusal_problems(res)


def case_13() -> list[str]:
    # refuse: a degraded info/attributes must not end the guard loop —
    # a hardlinked objects/info/alternates in the SAME repo (checked later
    # in guard_git_files) still refuses the whole run (F1 falsifier).
    def bad_attrs_plus_alternates(attrs: Path, repo_b: Path) -> None:
        attrs.write_text("* -text\n", encoding="utf-8")
        os.link(attrs, repo_b / ".git" / "info" / "attributes.twin")
        oi = repo_b / ".git" / "objects" / "info"
        oi.mkdir(parents=True, exist_ok=True)
        alt = oi / "alternates"
        alt.write_text("/nonexistent\n", encoding="utf-8")
        os.link(alt, oi / "alternates.twin")
    fleet = d2_fleet("d2-attrs-plus-hardlink-alternates", bad_attrs_plus_alternates)
    res = run_tool(["--root", str(fleet)])
    return refusal_problems(res)


def case_14() -> list[str]:
    # repair: hardlinked attributes in the LINKED worktree's admin dir.
    # The main repo's registration guard (:790) degrades x-main; the
    # worktree itself degrades when it is a row (:873, --include-root).
    # Inert to git, degraded conservatively (pinned policy).
    fleet = linked_fleet("d2-linked-admin", bad_in_admin=True)
    problems = degraded_fleet_problems(
        fleet, ["x-main"], ["a", "c"], {"x-main": ["x-main", "b"]}
    )
    problems.extend(
        degraded_root_problems(fleet / "b", ["b", "x-main"])
    )
    return problems


def case_15() -> list[str]:
    # repair: hardlinked attributes in the COMMON gitdir degrade x-main
    # (:831) and the linked worktree b, reached through the admin's
    # commondir (:891, --include-root).
    fleet = linked_fleet("d2-linked-common", bad_in_admin=False)
    problems = degraded_fleet_problems(
        fleet, ["x-main"], ["a", "c"], {"x-main": ["x-main"]}
    )
    problems.extend(
        degraded_root_problems(fleet / "b", ["x-main", "b"])
    )
    return problems


def case_16() -> list[str]:
    # repair: a linked worktree whose admin config.worktree sets `no`
    # (extensions.worktreeConfig in the common config) must still make the
    # main row wt-dirty. b is a fleet child with a .git file — never a row.
    fleet = SCRATCH / "d1-linked-uno"
    x_main = init_repo(
        fleet / "x-main", "[extensions]\n\tworktreeConfig = true\n"
    )
    bdir = fleet / "b"
    git(x_main, "worktree", "add", "-b", "wt-b", str(bdir))
    admin = x_main / ".git" / "worktrees" / "b"
    (admin / "config.worktree").write_text(
        "[status]\n\tshowUntrackedFiles = no\n", encoding="utf-8"
    )
    (bdir / "untracked.txt").write_text("u\n", encoding="utf-8")
    res = run_tool(["--root", str(fleet)])
    return positive_problems(
        res,
        {"x-main": ("2", "0", "0", "clean,wt-dirty")},
    )


def case_17() -> list[str]:
    # preserve: an invalid repo-config showUntrackedFiles value fails
    # git status eagerly — the pinned --untracked-files flag cannot
    # rescue it (host git: rc 128 with and without -u). The honest row
    # is status-unverifiable on every arm.
    fleet = SCRATCH / "d1-invalid-value"
    repo = init_repo(
        fleet / "r-suf-bogus", "[status]\n\tshowUntrackedFiles = bogus\n"
    )
    (repo / "untracked.txt").write_text("u\n", encoding="utf-8")
    return positive_problems(
        run_tool(["--root", str(fleet)]),
        {"r-suf-bogus": ("1", "0", "0", "status-unverifiable")},
    )


def case_18() -> list[str]:
    # refuse: gitfile→gitdir repo (linked worktree) whose ADMIN
    # info/attributes is degraded must still reach the commondir guard —
    # a hardlinked config in the COMMON dir refuses the whole run.
    n_common = init_repo(SCRATCH / "d2-gitfile-common" / "n")
    g = SCRATCH / "d2-gitfile-common" / "g"
    git(n_common, "worktree", "add", "-b", "wt-g", str(g))
    admin = n_common / ".git" / "worktrees" / "g"
    info = admin / "info"
    info.mkdir(exist_ok=True)
    attrs = info / "attributes"
    attrs.write_text("* -text\n", encoding="utf-8")
    os.link(attrs, info / "attributes.twin")
    os.link(n_common / ".git" / "config", n_common / ".git" / "config.twin")
    res = run_tool(["--root", str(g), "--include-root"])
    return refusal_problems(res)


def case_19() -> list[str]:
    # refuse: an admin info/attributes symlink escaping the gitdir
    # (→/dev/zero) passes the softened file check but must still hit the
    # link guard and refuse the whole run (F2 falsifier).
    n_common = init_repo(SCRATCH / "d2-admin-escape" / "n")
    g = SCRATCH / "d2-admin-escape" / "g"
    git(n_common, "worktree", "add", "-b", "wt-g", str(g))
    admin = n_common / ".git" / "worktrees" / "g"
    info = admin / "info"
    info.mkdir(exist_ok=True)
    os.symlink("/dev/zero", info / "attributes")
    res = run_tool(["--root", str(g), "--include-root"])
    return refusal_problems(res)


def case_20() -> list[str]:
    # repair: a degraded info/attributes PLUS a soft config (harmless
    # ~user include) in the same repo → error row with BOTH the
    # config-unsupported and git-metadata-unsupported diagnostics (the
    # channels must not mask each other, F3 falsifier).
    def bad_attrs_plus_soft(attrs: Path, repo_b: Path) -> None:
        attrs.write_text("* -text\n", encoding="utf-8")
        os.link(attrs, repo_b / ".git" / "info" / "attributes.twin")
        with (repo_b / ".git" / "config").open("a", encoding="utf-8") as fh:
            fh.write("[include]\n\tpath = ~nobody/x.gitconfig\n")
    fleet = d2_fleet("d2-attrs-plus-soft-config", bad_attrs_plus_soft)
    return degraded_fleet_problems(
        fleet, ["b"], also_stderr=(CONFIG_SOFT,)
    )


def case_21() -> list[str]:
    # preserve: a directory at info/attributes is read by git as empty
    # (EISDIR → absent); it cannot block or alias. Pinned: normal row.
    def as_dir(attrs: Path, repo_b: Path) -> None:
        attrs.mkdir()
        provoke(repo_b)
    fleet = d2_fleet("d2-attrs-dir", as_dir)
    return positive_problems(
        run_tool(["--root", str(fleet)]),
        {"a": CLEAN, "b": CLEAN, "c": CLEAN},
    )


def case_22() -> list[str]:
    # preserve: an in-gitdir DANGLING symlink at info/attributes is absent
    # to git (ENOENT); it must stay a normal row, not degrade or refuse.
    def dangling(attrs: Path, repo_b: Path) -> None:
        os.symlink("no-such-attrs", attrs)
        provoke(repo_b)
    fleet = d2_fleet("d2-attrs-dangling", dangling)
    return positive_problems(
        run_tool(["--root", str(fleet)]),
        {"a": CLEAN, "b": CLEAN, "c": CLEAN},
    )


def case_23() -> list[str]:
    # refuse: an out-of-gitdir symlink at info/attributes stays a
    # git-metadata-symlink whole-run refusal even when it dangles.
    def dangling_escape(attrs: Path, repo_b: Path) -> None:
        os.symlink(SCRATCH / "no-such-attrs", attrs)
    fleet = d2_fleet("d2-attrs-dangling-escape", dangling_escape)
    res = run_tool(["--root", str(fleet)])
    return refusal_problems(res)


def case_24() -> list[str]:
    # repair: a unix socket at info/attributes is non-regular; git would
    # get ENXIO but the census must degrade, never open it.
    def as_socket(attrs: Path, repo_b: Path) -> None:
        s = socket_mod.socket(socket_mod.AF_UNIX, socket_mod.SOCK_STREAM)
        s.bind(str(attrs))
        s.close()
        provoke(repo_b)
    fleet = d2_fleet("d2-attrs-socket", as_socket)
    return degraded_fleet_problems(fleet, ["b"])


def case_25() -> list[str]:
    # refuse: symlink → /dev/zero escapes the gitdir and stays a
    # git-metadata-symlink whole-run refusal (load-bearing: the refusal is
    # what keeps git from reading NULs without bound). Tool runs under
    # RLIMIT_AS=1G so an unguarded arm dies ENOMEM, not the host.
    def dev_zero(attrs: Path, repo_b: Path) -> None:
        os.symlink("/dev/zero", attrs)
        provoke(repo_b)
    fleet = d2_fleet("d2-attrs-devzero", dev_zero)
    res = run_tool(["--root", str(fleet)])
    return refusal_problems(res)


def case_26() -> list[str]:
    # repair: linked worktree whose ADMIN's commondir is divergent —
    # W/.git → admin A; A/commondir → N/.git (a different repo, inside the
    # fleet) whose info/attributes is bad. Every row of that common store
    # degrades: N's own row errors, W's status is skipped so M carries
    # wt-dirty, and no git -C W call runs. One diagnostic per row, naming
    # the common path.
    fleet = SCRATCH / "d2-divergent-common"
    init_repo(fleet / "a")
    init_repo(fleet / "c")
    n_common = init_repo(fleet / "n-common")
    m_main = init_repo(fleet / "m-main")
    w_dir = SCRATCH / "w-divergent"
    git(m_main, "worktree", "add", "-b", "wt-w", str(w_dir))
    admin = m_main / ".git" / "worktrees" / "w-divergent"
    (admin / "commondir").write_text(str(n_common / ".git") + "\n",
                                     encoding="utf-8")
    info = n_common / ".git" / "info"
    info.mkdir(exist_ok=True)
    mkfifo(info / "attributes")
    provoke(w_dir)

    problems: list[str] = []
    res = run_tool(["--root", str(fleet)])
    if res.rc == 124:
        return ["fleet run timed out (blocked on divergent common attributes)"]
    if res.rc != 0:
        problems.append(f"exit={res.rc} want 0")
        return problems + contract_problems(res)
    rows = rows_by_name(res.out)
    want = {"a": CLEAN, "c": CLEAN, "n-common": None,
            "m-main": ("2", "0", "0", "clean,wt-dirty")}
    got = sorted(rows)
    if got != sorted(want):
        problems.append(f"row set {got} want {sorted(want)}")
    problems.extend(error_row_problems(rows.get("n-common"), "n-common"))
    for name, row in want.items():
        if row is None:
            continue
        fields = rows.get(name)
        if fields is None or len(fields) != 7:
            continue
        if fields[1:4] != list(row[:3]) or fields[6] != row[3]:
            problems.append(f"{name}: row {fields[1:]} want {row}")
    problems.extend(
        degrade_diag_problems(res, ["n-common"], expected_diag=2)
    )
    hits = git_calls_into(res, w_dir)
    if hits:
        problems.append(
            "git call could read divergent common attributes: "
            + " | ".join(hits[:2])
        )
    problems.extend(contract_problems(res))
    return problems

def case_27() -> list[str]:
    # preserve (wave-2 SentinelCensusD2 F1): zero-length metadata files are
    # `regular empty file` under %F — not non-regular. Empty
    # info/attributes, info/exclude, packed-refs, config and
    # objects/info/alternates must all stay normal rows on every arm.
    fleet = SCRATCH / "d2-empty-files"
    for name, rel in (
        ("r-empty-attrs", "info/attributes"),
        ("r-empty-exclude", "info/exclude"),
        ("r-empty-packed-refs", "packed-refs"),
        ("r-empty-config", "config"),
        ("r-empty-alternates", "objects/info/alternates"),
    ):
        repo = init_repo(fleet / name)
        (repo / ".git" / rel).write_text("", encoding="utf-8")
    return positive_problems(
        run_tool(["--root", str(fleet)]),
        {n: CLEAN
         for n in ("r-empty-attrs", "r-empty-exclude", "r-empty-packed-refs",
                   "r-empty-config", "r-empty-alternates")},
    )


def case_28() -> list[str]:
    # preserve (wave-2 SentinelCensusD2 F2): GNU stat %F is gettext-
    # translated; under LANGUAGE=de a `*)` arm on 'regular file' would
    # refuse every config. A benign fleet under LANGUAGE=de must give
    # rc 0 with all rows clean. Vacuity: when no de catalog is installed,
    # stat stays English and the case records that instead of judging.
    probe = SCRATCH / "locale-probe"
    probe.write_text("x\n", encoding="utf-8")
    # Probe through bash so gettext resolution matches the tool's own
    # exec environment exactly (a bare stat may resolve differently).
    kind = run_process_group(
        ["bash", "-c", 'stat -L -c %F -- "$1"', "_", str(probe)],
        env={
            "PATH": "/usr/local/bin:/usr/bin:/bin",
            "LANGUAGE": "de", "LC_ALL": "en_US.UTF-8",
        },
        timeout=30,
    ).stdout.strip()
    vacuous = kind.startswith("regular")
    fleet = SCRATCH / "d1-locale-de"
    init_repo(fleet / "a")
    init_repo(fleet / "b")
    init_repo(fleet / "c")
    problems = positive_problems(
        run_tool(
            ["--root", str(fleet)],
            extra_env={"LANGUAGE": "de", "LC_ALL": "en_US.UTF-8"},
        ),
        {"a": CLEAN, "b": CLEAN, "c": CLEAN},
    )
    if vacuous:
        problems.append(
            f"note: stat %F under LANGUAGE=de is '{kind}' (no de catalog "
            "installed); locale discrimination is vacuous on this host"
        )
    return problems


def case_29() -> list[str]:
    # refuse (wave-2 SentinelCensusD2 F4): a dot-named worktree admin dir
    # (`.git/worktrees/.wtdot`) escapes the non-dotglob `worktrees/*` glob,
    # so every admin guard is skipped and `git worktree list` opens a FIFO
    # HEAD — an unbounded hang. The dot-admin glob must see it: rc 2
    # git-metadata-nonregular, and never a timeout (60s = FAIL).
    fleet = SCRATCH / "d2-dot-admin"
    init_repo(fleet / "a")
    init_repo(fleet / "c")
    x_main = init_repo(fleet / "x-main")
    bdir = fleet / "wtdot"
    git(x_main, "worktree", "add", "-b", "wt-dot", str(bdir))
    admin = x_main / ".git" / "worktrees" / "wtdot"
    dot_admin = x_main / ".git" / "worktrees" / ".wtdot"
    admin.rename(dot_admin)
    (bdir / ".git").write_text(
        f"gitdir: {dot_admin}\n", encoding="utf-8"
    )
    (dot_admin / "HEAD").unlink()
    mkfifo(dot_admin / "HEAD")
    res = run_tool(["--root", str(fleet)])
    return refusal_problems(res)



CASES = {
    "R17-01": case_01, "R17-02": case_02, "R17-03": case_03,
    "R17-04": case_04, "R17-05": case_05, "R17-06": case_06,
    "R17-07": case_07, "R17-08": case_08, "R17-09": case_09,
    "R17-10": case_10, "R17-11": case_11, "R17-12": case_12,
    "R17-13": case_13, "R17-14": case_14, "R17-15": case_15,
    "R17-16": case_16, "R17-17": case_17, "R17-18": case_18,
    "R17-19": case_19, "R17-20": case_20, "R17-21": case_21,
    "R17-22": case_22, "R17-23": case_23, "R17-24": case_24,
    "R17-25": case_25, "R17-26": case_26, "R17-27": case_27,
    "R17-28": case_28, "R17-29": case_29,
}


def cleanup() -> None:
    unblock_fifos()
    if "SCRATCH" in globals():
        shutil.rmtree(SCRATCH, ignore_errors=False)


def main(argv: list[str]) -> int:
    global SCRATCH, TOOL, ACTIVE_RUNS

    parser = argparse.ArgumentParser(
        prog="r17-census-hygiene.py",
        description="C1 census hygiene fixture: D1 untracked visibility, "
        "D2 info/attributes kind guard",
    )
    # --tool is the matrix-harness alias for --census (same value).
    parser.add_argument(
        "--census", "--tool", dest="census",
        help="census tool under test (default: lane tools/souji-census.sh)",
    )
    parser.add_argument(
        "--case", action="append", default=[], metavar="ID",
        help="run one case (repeatable; debugging only, never for admission)",
    )
    parser.add_argument("--list", action="store_true", help="print case ids and exit")
    parser.add_argument(
        "--json", action="store_true",
        help="emit one JSON line with per-case records",
    )
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
        die("refusing to run as root")

    TOOL = (
        Path(args.census)
        if args.census
        else Path(__file__).resolve().parents[2] / "tools" / "souji-census.sh"
    )
    TOOL = TOOL.resolve()
    if not TOOL.is_file():
        die(f"tool not readable: {TOOL}")
    try:
        TOOL.read_bytes()
    except OSError as exc:
        die(f"tool not readable: {TOOL}: {exc}")

    try:
        SCRATCH = Path(tempfile.mkdtemp(prefix="r17-census-hygiene.", dir="/var/tmp"))
    except OSError as exc:
        die(f"cannot create /var/tmp fixture: {exc}")
    records: list[dict] = []
    try:
        try:
            build_world()
        except SystemExit:
            raise
        except Exception as exc:
            die(f"setup failed: {exc}")
        digest = hashlib.sha256(TOOL.read_bytes()).hexdigest()
        print(f"TOOL\t{TOOL}\tsha256={digest}")
        failed = 0
        ran: list[str] = []
        for cid in selected:
            ACTIVE_RUNS = []
            # The oracle is identical for every arm: baseline red is an
            # observed behavioral failure, never a digest-keyed verdict.
            problems = CASES[cid]()
            status = "PASS" if not problems else "FAIL"
            last = ACTIVE_RUNS[-1] if ACTIVE_RUNS else None
            obs_exit = last.rc if last else -1
            obs_finding = last.finding if last else "none"
            cls = CASE_CLASSES.get(cid, "unknown")
            summary = "; ".join(problems) if problems else "ok"
            if len(summary) > 400:
                summary = summary[:397] + "..."
            detail = (
                f"class={cls}\t{summary}"
                f"\tobserved_exit={obs_exit}\tobserved_finding={obs_finding}"
            )
            print(f"CASE\t{cid}\t{status}\t{detail}")
            if problems:
                failed += 1
            ran.append(cid)
            records.append(
                {
                    "id": cid,
                    "class": cls,
                    "status": status.lower(),
                    "exit": obs_exit,
                    "finding": obs_finding,
                    "problems": problems,
                    "runs": [
                        {"args": r.args, "exit": r.rc, "finding": r.finding}
                        for r in ACTIVE_RUNS
                    ],
                }
            )
        if not args.case and tuple(ran) != EXPECTED_IDS:
            failed += 1
            print(
                "CASE\tid-set\tFAIL\t"
                f"ran={','.join(ran)} expected={','.join(EXPECTED_IDS)}"
            )
        print(f"SUMMARY\ttotal={len(ran)}\tfailed={failed}")
        if args.json:
            print(
                "JSON\t"
                + json.dumps(
                    {
                        "fixture": "r17-census-hygiene",
                        "expected_ids": list(EXPECTED_IDS),
                        "case_classes": CASE_CLASSES,
                        "tool": {"path": str(TOOL), "sha256": digest},
                        "cases": records,
                        "summary": {"total": len(ran), "failed": failed},
                    },
                    sort_keys=True,
                )
            )
        return 0 if failed == 0 else 1
    finally:
        cleanup()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
