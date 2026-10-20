#!/usr/bin/env python3
"""r15-census-config.py — C1 operability fixture for tools/souji-census.sh.

The round-14 guard_git_config refuses every repo-local config that merely
*names* one of the listed keys (include/includeIf, filter.*.clean|smudge|
process, core.hooksPath, core.attributesFile, core.excludesFile,
core.alternateRefsCommand, remote.*.promisor, extensions.partialClone,
extensions.worktreeConfig), regardless of value, and exits 2 for the whole
run. This fixture proves the repaired tool is value/effect-aware: safe
values keep working (green) while unsafe values and every verified
namespace refusal still refuse.

Semantics pinned here (SoujiR15.ConfigRepair lock, reviewer reports):
  * include.path / includeIf.*.path targets are resolved and guarded;
    outside-repo targets that resolve outside the protected boundary are
    admitted; store-reaching, ~user, cyclic, and non-regular targets are
    refused. includeIf conditions are not evaluated for safety: a target
    that reaches the store is refused even behind a condition that cannot
    match (hasconfig pre-pass reads it; gitdir/onbranch/unknown are
    fail-closed). Missing targets are benign. Refused keys inside an
    included file refuse through the same predicates.
  * core.hooksPath and core.fsmonitor are accepted for ANY value: no
    census invocation can trigger a hook event, and every status call
    carries -c core.hooksPath=/dev/null -c core.fsmonitor=false.
    core.attributesFile and core.excludesFile are EFFECT-AWARE: a safe
    (boundary-clean, regular) path is honored so dirty semantics match
    the pre-harm tool; a target reaching the store is refused before any
    read. Repo .gitignore still applies either way.
  * remote.*.promisor is boolean-parsed: on a COMPLETE repository every
    value is inert under GIT_NO_LAZY_FETCH (no missing object can trigger
    a fetch) so all spellings produce accurate rows; invalid booleans
    refuse fail-closed as could-not-evaluate. remote.*.partialCloneFilter
    and extensions.partialClone (a remote NAME, never a boolean — "false"
    names remote "false") are equally benign on a complete repo.
    GIT_NO_LAZY_FETCH=1 is required on every census git call and is
    asserted by the safety case, not by the benign row cases.
  * Execution sentries (hooks/fsmonitor command sentinels) are asserted
    only in the safety case: a correct pre-harm arm may legitimately
    fire them, so they are never carried by a benign restitution row.
  * extensions.worktreeConfig false/off/empty is benign and
    config.worktree must never be opened (inertness control). true is
    accepted only when each reachable config.worktree is guarded: a benign
    config.worktree (incl. a legitimate relative core.worktree) is green;
    a config.worktree carrying include/filter/hostile core.worktree is
    refused. Invalid values refuse fail-closed.
  * core.alternateRefsCommand: empty value is benign; any non-empty
    command value refuses (census never runs a consumer).
  * filter.*.clean|smudge|process: driver keys not selected by any
    attributes source are benign and must never execute; a filter bound
    by a reachable attributes file refuses.
  * Key parsing is exact, not substring: a remote named include.d, a
    remote subsection x.promisor-mirror, a remote+branch pair spanning
    lines, and a filter.x.required/diff.clean.driver line pair must NOT
    trip the refusal.
  * Refusal shape is unchanged: whole-run exit 2, `souji-census:
    path-protected: <reason>` on stderr, no stdout rows (rows print only
    after every repo is measured).

The fixture builds a synthetic HOME under /var/tmp whose agent store
(<home>/.omp/agent) is mode 000 and contains a canary string. Every tool
invocation runs under `strace -f` with PATH spies for
find/du/git/cat/head/tail/readlink/stat/realpath logging cwd, argv and
selected GIT_* environment values. Two independent access checks run on
every invocation:

  * spies: no logged path or environment value names the synthetic store;
    env-poison cases pin the observed values exactly;
  * strace: no open/openat/getdents64/execve/stat/readlink naming the
    store (strict oracle — the store root itself must not be statted).
    The initial execve (the tool itself) is ignored.

Execution sentinels (hook script, fsmonitor command, unbound filter
command, alternateRefsCommand) are scripts that would create a marker
file; the marker must be absent after every census run. The canary must
never appear on stdout or stderr. The fixture exits 2 if strace cannot
trace, if a required tool is absent, or on usage error.

Baseline discrimination, three arms, same command:
  * --tool <r14-harm> (installed r14 tool, sha256 fcff8b05…): every safe
    case FAILs (the recorded harm), every refusal/namespace case PASSes.
    A safe case passing on this digest is itself a failure — the red half
    of the pair is missing.
  * --tool <pre-harm> (a31642d, sha256 6a000c59…): safe cases PASS; the
    new refusal controls FAIL where the guard did not exist yet.
  * --tool <repaired>: all cases PASS.
TOOL-KIND records which arm ran. CASE detail and the --json record carry
observed_exit/observed_finding per case (last invocation) for the C2
paired-preservation checker.

Q4 parity: scratch is /var/tmp only and removed in a finally block.
No /dev/shm, no real credential path, no live census.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HEADER = "repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags"
FINDING = "path-protected"
CANARY = "R15CFG-CANARY-3f7a91c4-do-not-emit"

EXPECTED_IDS = (
    "R15CFG-01",  # benign: safe includes, includeIf variants, missing, ~, out-of-repo
    "R15CFG-02",  # refusal: include/includeIf targets into the store
    "R15CFG-03",  # refusal: include cycle, ~user, FIFO, NUL config
    "R15CFG-04",  # benign: neutralized hooks/fsmonitor; honored attrs/excludes match pre-harm rows
    "R15CFG-05",  # preserve: dirty fidelity (modified+untracked; .gitignore honored)
    "R15CFG-06",  # benign: remote.*.promisor any bool + partialCloneFilter on a
                  # complete repo — accurate rows (GIT_NO_LAZY_FETCH pin lives in 08)
    "R15CFG-07",  # refusal: promisor invalid booleans (could-not-evaluate, fail-closed)
    "R15CFG-08",  # safety: execution sentries — hooks/fsmonitor sentinel scripts must
                  # not fire; GIT_NO_LAZY_FETCH=1 pinned on every observed git call
    "R15CFG-09",  # benign: extensions.partialClone false/empty/origin on a complete
                  # repo — remote-name markers are inert under NO_LAZY_FETCH
    "R15CFG-10",  # benign: worktreeConfig false + hostile stray (unopened), true + benign
    "R15CFG-11",  # refusal: worktreeConfig true + hostile config.worktree; invalid value
    "R15CFG-12",  # benign: alternateRefsCommand empty value
    "R15CFG-13",  # benign: unbound filter.* drivers never executed
    "R15CFG-14",  # refusal: attribute-bound filter.*.clean/process; non-empty altrefs
    "R15CFG-15",  # benign: key-parse false positives
    "R15CFG-16",  # benign: mixed fleet, exact row set/order/fields
    "R15CFG-17",  # refusal: mixed fleet containing one unsafe repo (rc 2, no rows)
    "R15CFG-18",  # preserve: poisoned HOME/.gitconfig + GIT_* env have no effect
    "R15CFG-19",  # refusal: retained namespace (store root / ancestor root)
    "R15CFG-20",  # preserve: --compare identical rc 0, drift rc 3, malformed rc 2
)

# Cases expected to FAIL under the r14 harm tool from OBSERVED behavior
# (value-blind refusal or a missing namespace refusal). Descriptive table
# for the independent admission checker — the fixture applies the
# identical behavioral oracle to every tool identity, no exceptions.
HARM_CASES = frozenset({
    "R15CFG-01", "R15CFG-04", "R15CFG-06", "R15CFG-08", "R15CFG-09",
    "R15CFG-10", "R15CFG-12", "R15CFG-13", "R15CFG-15", "R15CFG-16",
})

# Case class labels for the admission checker (pinned, non-adaptive).
CASE_CLASSES = {
    "R15CFG-01": "benign", "R15CFG-02": "refusal", "R15CFG-03": "refusal",
    "R15CFG-04": "benign", "R15CFG-05": "preserve", "R15CFG-06": "benign",
    "R15CFG-07": "refusal", "R15CFG-08": "safety", "R15CFG-09": "benign",
    "R15CFG-10": "benign", "R15CFG-11": "refusal", "R15CFG-12": "benign",
    "R15CFG-13": "benign", "R15CFG-14": "refusal", "R15CFG-15": "benign",
    "R15CFG-16": "benign", "R15CFG-17": "refusal", "R15CFG-18": "preserve",
    "R15CFG-19": "refusal", "R15CFG-20": "preserve",
}

FORBIDDEN = ("find", "du", "git", "cat", "head", "tail")
SPY_TOOLS = FORBIDDEN + ("readlink", "stat", "realpath")
HARM_SHA = "fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9"
PREHARM_SHA = "6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026"
GIT_ENV = (
    "GIT_DIR",
    "GIT_COMMON_DIR",
    "GIT_WORK_TREE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_CONFIG_GLOBAL",
    "GIT_CONFIG_SYSTEM",
    "GIT_CONFIG_NOSYSTEM",
    "GIT_CONFIG_COUNT",
    "GIT_NO_LAZY_FETCH",
    "GIT_OPTIONAL_LOCKS",
    "GIT_TERMINAL_PROMPT",
)

SCRATCH: Path
HOME: Path
STORE: Path
AGENT: Path
SPYDIR: Path
SPYLOG: Path
TRACELOG: Path
TOOL: Path
REAL: dict[str, str]
ACTIVE_RUNS: list["Result"]

FL_INC_SAFE: Path
FL_NEUTRAL: Path
FL_DIRTY: Path
FL_PROM_SAFE: Path
FL_PC_SAFE: Path
FL_SENTRY: Path
FL_WTC_OFF: Path
FL_WTC_ON: Path
FL_ALTREFS: Path
FL_FILTER_SAFE: Path
FL_KEYPARSE: Path
FL_MIXED: Path
FL_MIXED_UNSAFE: Path
UNSAFE: Path
RECORDS: Path

# Exec sentinels (hooks/fsmonitor) are safety asserts, asserted only in
# refusal/safety-class cases — a correct pre-harm arm may legitimately run
# them, so benign rows must never carry the assertion. Inert sentinels
# (altrefs/filter) can never execute under any census command set and are
# safe to assert anywhere.
SENT_HOOKS: Path
SENT_FSM: Path
SENT_AR: Path
SENT_FL: Path

FINDING_RE = re.compile(r"souji-census:\s*([a-z0-9-]+):\s*([a-z0-9-]+)")


class Result:
    def __init__(
        self,
        rc: int,
        out: str,
        err: str,
        spy: list[str],
        trace: list[str],
        trace_ok: bool,
        args: list[str] | None = None,
    ) -> None:
        self.rc = rc
        self.out = out
        self.err = err
        self.spy = spy
        self.trace = trace
        self.trace_ok = trace_ok
        self.args = args or []

    @property
    def finding(self) -> str:
        m = FINDING_RE.search(self.err)
        return f"{m.group(1)}:{m.group(2)}" if m else "none"


def die(message: str) -> "None":
    print(f"r15-census-config: {message}", file=sys.stderr)
    raise SystemExit(2)


def run_setup(
    command: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
):
    proc = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        env=env,
        capture_output=True,
        text=True,
        errors="replace",
        timeout=60,
    )
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
        "LC_ALL": "C",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_SYSTEM": "/dev/null",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "r15-census-config",
        "GIT_AUTHOR_EMAIL": "r15@example.invalid",
        "GIT_COMMITTER_NAME": "r15-census-config",
        "GIT_COMMITTER_EMAIL": "r15@example.invalid",
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


def sent_script(path: Path, marker: Path, body: str = "") -> None:
    path.write_text(
        f"#!/bin/sh\ntouch {shlex.quote(str(marker))}\n{body}",
        encoding="utf-8",
    )
    path.chmod(0o755)


def build_world() -> None:
    global HOME, STORE, AGENT, SPYDIR, SPYLOG, TRACELOG, REAL
    global FL_INC_SAFE, FL_NEUTRAL, FL_DIRTY, FL_PROM_SAFE, FL_PC_SAFE, FL_SENTRY
    global FL_WTC_OFF, FL_WTC_ON
    global FL_ALTREFS, FL_FILTER_SAFE, FL_KEYPARSE, FL_MIXED, FL_MIXED_UNSAFE
    global UNSAFE, RECORDS
    global SENT_HOOKS, SENT_FSM, SENT_AR, SENT_FL

    REAL = {}
    for name in (*SPY_TOOLS, "strace"):
        found = shutil.which(name)
        if not found:
            die(f"required tool not found: {name}")
        REAL[name] = found

    HOME = SCRATCH / "home"
    STORE = HOME / ".omp"
    AGENT = STORE / "agent"
    AGENT.mkdir(parents=True)
    (AGENT / "config.yml").write_text(
        f"server:\n  token: {CANARY}\n", encoding="utf-8"
    )
    # Store paths a refused config value might name; never legitimately read.
    (AGENT / "secret.gitconfig").write_text("[user]\n\tname = leak\n", encoding="utf-8")
    (AGENT / "hooks").mkdir()
    (AGENT / "attrs").write_text("* -text\n", encoding="utf-8")
    (AGENT / "ignore").write_text("*\n", encoding="utf-8")

    SENT_HOOKS = SCRATCH / "sentinel-hooks"
    SENT_FSM = SCRATCH / "sentinel-fsmonitor"
    SENT_AR = SCRATCH / "sentinel-altrefs"
    SENT_FL = SCRATCH / "sentinel-filter"

    # --- execution-sentry fleet (safety, asserted only in R15CFG-08) -------
    # hooksPath + fsmonitor sentinels in repos whose rows stay clean; the
    # neutralizing -c overrides must keep the marker scripts from firing.
    FL_SENTRY = SCRATCH / "sentry-fleet"
    repo = init_repo(FL_SENTRY / "s-hooks")
    githooks = repo / ".git" / "githooks"
    githooks.mkdir()
    sent_script(githooks / "post-index-change", SENT_HOOKS)
    sent_script(githooks / "pre-index-change", SENT_HOOKS)
    with (repo / ".git" / "config").open("a", encoding="utf-8") as fh:
        fh.write(f"[core]\n\thooksPath = {githooks}\n")
    repo = init_repo(FL_SENTRY / "s-fsm")
    sent_script(repo / ".git" / "fm.sh", SENT_FSM)
    with (repo / ".git" / "config").open("a", encoding="utf-8") as fh:
        fh.write(f"[core]\n\tfsmonitor = {repo}/.git/fm.sh\n")

    # --- benign include fleet ----------------------------------------------
    FL_INC_SAFE = SCRATCH / "inc-safe-fleet"
    FL_INC_SAFE.mkdir()
    (FL_INC_SAFE / "inc-fleet.gitconfig").write_text(
        "[user]\n\tname = fleet\n", encoding="utf-8"
    )
    # In-gitdir include targets stay invisible to `git status`; a worktree
    # root target would be untracked and turn the row dirty.
    repo = init_repo(
        FL_INC_SAFE / "r-inc-rel",
        "[include]\n\tpath = inc-shared.gitconfig\n",
    )
    (repo / ".git" / "inc-shared.gitconfig").write_text(
        "[user]\n\tname = shared\n", encoding="utf-8"
    )
    init_repo(
        FL_INC_SAFE / "r-inc-out",
        "[include]\n\tpath = ../../inc-fleet.gitconfig\n",
    )
    init_repo(
        FL_INC_SAFE / "r-inc-missing",
        "[include]\n\tpath = ../absent.gitconfig\n",
    )
    (HOME / "fleet-tilde.gitconfig").write_text(
        "[user]\n\tname = tilde\n", encoding="utf-8"
    )
    init_repo(
        FL_INC_SAFE / "r-inc-tilde",
        "[include]\n\tpath = ~/fleet-tilde.gitconfig\n",
    )
    repo = init_repo(FL_INC_SAFE / "r-incif")
    for name in ("inc-br.gitconfig", "inc-gd.gitconfig", "inc-hc.gitconfig"):
        (repo / ".git" / name).write_text("[user]\n\tname = inc\n", encoding="utf-8")
    with (repo / ".git" / "config").open("a", encoding="utf-8") as fh:
        fh.write(
            '[includeIf "onbranch:main"]\n\tpath = inc-br.gitconfig\n'
            '[includeIf "gitdir:**/r-incif/**"]\n\tpath = inc-gd.gitconfig\n'
            '[includeIf "hasconfig:remote.*.url:nevermatch"]\n'
            "\tpath = inc-hc.gitconfig\n"
        )

    # --- unsafe repos (each exercised via --root <repo> --include-root) -----
    UNSAFE = SCRATCH / "unsafe-repos"
    store_cfg = str(AGENT / "secret.gitconfig")
    init_repo(UNSAFE / "r-inc-store", f"[include]\n\tpath = {store_cfg}\n")
    init_repo(
        UNSAFE / "r-incif-store",
        f'[includeIf "gitdir:/nonexistent/"]\n\tpath = {store_cfg}\n',
    )
    init_repo(
        UNSAFE / "r-incif-hc-store",
        f'[includeIf "hasconfig:remote.*.url:nomatch"]\n\tpath = {store_cfg}\n',
    )
    init_repo(
        UNSAFE / "r-incif-unknown",
        f'[includeIf "forge:x"]\n\tpath = {store_cfg}\n',
    )
    repo = init_repo(
        UNSAFE / "r-inc-nested",
        "[include]\n\tpath = ../outer.gitconfig\n",
    )
    (repo / "outer.gitconfig").write_text(
        f"[include]\n\tpath = {store_cfg}\n", encoding="utf-8"
    )
    repo = init_repo(UNSAFE / "r-inc-cycle", "[include]\n\tpath = ../a.inc\n")
    (repo / "a.inc").write_text("[include]\n\tpath = b.inc\n", encoding="utf-8")
    (repo / "b.inc").write_text("[include]\n\tpath = a.inc\n", encoding="utf-8")
    init_repo(UNSAFE / "r-inc-tildeuser", "[include]\n\tpath = ~root/x.gitconfig\n")
    repo = init_repo(UNSAFE / "r-inc-fifo", "[include]\n\tpath = ../fifo.inc\n")
    os.mkfifo(repo / "fifo.inc")
    repo = init_repo(UNSAFE / "r-inc-symlink", "[include]\n\tpath = ../link.inc\n")
    os.symlink(AGENT / "secret.gitconfig", repo / "link.inc")
    repo = init_repo(UNSAFE / "r-cfg-nul")
    with (repo / ".git" / "config").open("ab") as fh:
        fh.write(b"[x]\n\ta = b\x00c\n")
    # Invalid promisor booleans refuse fail-closed; valid true-ish markers
    # on a complete repo are benign under GIT_NO_LAZY_FETCH (see safe fleet).
    init_repo(UNSAFE / "r-prom-maybe", '[remote "o"]\n\tpromisor = maybe\n')
    init_repo(UNSAFE / "r-prom-maybe2", '[remote "o"]\n\tpromisor = banana\n')
    # worktreeConfig=true with a hostile config.worktree
    repo = init_repo(
        UNSAFE / "r-wtc-hostile", "[extensions]\n\tworktreeConfig = true\n"
    )
    (repo / ".git" / "config.worktree").write_text(
        f"[include]\n\tpath = {store_cfg}\n", encoding="utf-8"
    )
    repo = init_repo(
        UNSAFE / "r-wtc-cwt", "[extensions]\n\tworktreeConfig = true\n"
    )
    (repo / ".git" / "config.worktree").write_text(
        f"[core]\n\tworktree = {AGENT}/wt\n", encoding="utf-8"
    )
    init_repo(UNSAFE / "r-wtc-maybe", "[extensions]\n\tworktreeConfig = maybe\n")
    # attrs/excludes targets reaching the store refuse before any read
    init_repo(UNSAFE / "r-attrs-store", f"[core]\n\tattributesFile = {AGENT}/attrs\n")
    init_repo(UNSAFE / "r-excl-store", f"[core]\n\texcludesFile = {AGENT}/ignore\n")
    repo = init_repo(UNSAFE / "r-filter-clean")
    (repo / ".gitattributes").write_text("*.bin filter=x\n", encoding="utf-8")
    (repo / "f.bin").write_text("bin\n", encoding="utf-8")
    git(repo, "add", "--", ".gitattributes", "f.bin")
    git(repo, "commit", "-qm", "attr")
    with (repo / ".git" / "config").open("a", encoding="utf-8") as fh:
        fh.write('[filter "x"]\n\tclean = cat\n')
    repo = init_repo(UNSAFE / "r-filter-process")
    (repo / ".gitattributes").write_text("*.dat filter=p\n", encoding="utf-8")
    (repo / "f.dat").write_text("d\n", encoding="utf-8")
    git(repo, "add", "--", ".gitattributes", "f.dat")
    git(repo, "commit", "-qm", "attr")
    with (repo / ".git" / "config").open("a", encoding="utf-8") as fh:
        fh.write('[filter "p"]\n\tprocess = cat\n')
    repo = init_repo(UNSAFE / "r-altrefs-cmd")
    sent_script(repo / ".git" / "altrefs.sh", SENT_AR)
    with (repo / ".git" / "config").open("a", encoding="utf-8") as fh:
        fh.write(f"[core]\n\talternateRefsCommand = {repo}/.git/altrefs.sh\n")
    init_repo(UNSAFE / "r-altrefs-exit", "[core]\n\talternateRefsCommand = exit 0\n")
    init_repo(UNSAFE / "r-altrefs-bare", "[core]\n\talternateRefsCommand\n")
    # mixed fleet with one unsafe repo (unsafe sits between benign children)
    FL_MIXED_UNSAFE = SCRATCH / "mixed-unsafe-fleet"
    init_repo(FL_MIXED_UNSAFE / "a-ok")
    init_repo(FL_MIXED_UNSAFE / "m-unsafe", f"[include]\n\tpath = {store_cfg}\n")
    init_repo(FL_MIXED_UNSAFE / "z-ok")

    # --- neutralized + honored families ------------------------------------
    # hooksPath/fsmonitor: any value is inert (no hook event; -c overrides).
    # attributesFile/excludesFile: a safe boundary-clean path is HONORED so
    # dirty/attrs semantics match the pre-harm tool; store-reaching targets
    # are refused (see the unsafe-repos block).
    FL_NEUTRAL = SCRATCH / "neutral-fleet"
    init_repo(FL_NEUTRAL / "r-hooks-devnull", "[core]\n\thooksPath = /dev/null\n")
    init_repo(FL_NEUTRAL / "r-hooks-store", f"[core]\n\thooksPath = {AGENT}/hooks\n")
    repo = init_repo(FL_NEUTRAL / "r-hooks-marker")
    # Helper files live under .git so they are invisible to status; an
    # untracked worktree helper would make the row dirty. Markers here are
    # presence-only (asserted nowhere): a correct pre-harm arm may run them.
    githooks = repo / ".git" / "githooks"
    githooks.mkdir()
    sent_script(githooks / "post-index-change", SCRATCH / "sentinel-neutral-hooks")
    with (repo / ".git" / "config").open("a", encoding="utf-8") as fh:
        fh.write(f"[core]\n\thooksPath = {githooks}\n")
    init_repo(FL_NEUTRAL / "r-attrs-devnull", "[core]\n\tattributesFile = /dev/null\n")
    repo = init_repo(FL_NEUTRAL / "r-attrs-safe")
    (repo / ".git" / "attrs-local").write_text("*.bin -text\n", encoding="utf-8")
    with (repo / ".git" / "config").open("a", encoding="utf-8") as fh:
        fh.write(f"[core]\n\tattributesFile = {repo}/.git/attrs-local\n")
    repo = init_repo(FL_NEUTRAL / "r-fsm")
    sent_script(repo / ".git" / "fm.sh", SCRATCH / "sentinel-neutral-fsm")
    with (repo / ".git" / "config").open("a", encoding="utf-8") as fh:
        fh.write(f"[core]\n\tfsmonitor = {repo}/.git/fm.sh\n")
    # Honored excludes: /dev/null ignores nothing (untracked counts);
    # ignore-all "*" hides the untracked file (clean) — exactly the
    # pre-harm rows for these repos.
    repo = init_repo(FL_NEUTRAL / "r-excl-devnull", "[core]\n\texcludesFile = /dev/null\n")
    (repo / "u.txt").write_text("untracked\n", encoding="utf-8")
    repo = init_repo(FL_NEUTRAL / "r-excl-all")
    (repo / ".git" / "ignore-all").write_text("*\n", encoding="utf-8")
    (repo / "b.txt").write_text("untracked\n", encoding="utf-8")
    with (repo / ".git" / "config").open("a", encoding="utf-8") as fh:
        fh.write(f"[core]\n\texcludesFile = {repo}/.git/ignore-all\n")

    # --- dirty fidelity -----------------------------------------------------
    FL_DIRTY = SCRATCH / "dirty-fleet"
    repo = init_repo(FL_DIRTY / "r-dirty")
    (repo / "kept.txt").write_text("changed\n", encoding="utf-8")
    (repo / "new.txt").write_text("untracked\n", encoding="utf-8")
    repo = init_repo(FL_DIRTY / "r-ignored")
    (repo / ".gitignore").write_text("*.tmp\n", encoding="utf-8")
    git(repo, "add", "--", ".gitignore")
    git(repo, "commit", "-qm", "ignore")
    (repo / "f.tmp").write_text("ignored\n", encoding="utf-8")

    # --- complete-repo promisor markers: benign under GIT_NO_LAZY_FETCH ----
    # Every value below parses as a boolean or names a remote; on a COMPLETE
    # repository (no missing objects) no lazy fetch can trigger, so the
    # markers are inert and the row must be accurate.
    FL_PROM_SAFE = SCRATCH / "prom-safe-fleet"
    init_repo(FL_PROM_SAFE / "r-prom-false", '[remote "x"]\n\tpromisor = false\n')
    init_repo(FL_PROM_SAFE / "r-prom-empty", '[remote "x"]\n\tpromisor = \n')
    init_repo(FL_PROM_SAFE / "r-prom-off", '[remote "x"]\n\tpromisor = off\n')
    init_repo(FL_PROM_SAFE / "r-prom-zero", '[remote "x"]\n\tpromisor = 0\n')
    init_repo(FL_PROM_SAFE / "r-prom-true", '[remote "x"]\n\tpromisor = true\n')
    init_repo(FL_PROM_SAFE / "r-prom-bare", '[remote "x"]\n\tpromisor\n')
    init_repo(FL_PROM_SAFE / "r-prom-yes", '[remote "x"]\n\tpromisor = yes\n')
    init_repo(FL_PROM_SAFE / "r-prom-two", '[remote "x"]\n\tpromisor = 2\n')
    init_repo(FL_PROM_SAFE / "r-pcf", '[remote "x"]\n\tpartialCloneFilter = blob:none\n')

    # --- partialClone on a complete repo: the value is a remote NAME, not a
    # boolean — "false" names a remote literally. Inert under NO_LAZY_FETCH.
    FL_PC_SAFE = SCRATCH / "pc-safe-fleet"
    # repositoryformatversion=1 keeps the extension contract unambiguous
    # (extensions are honored regardless per the pinned semantics).
    init_repo(FL_PC_SAFE / "r-pc-false",
              "[core]\n\trepositoryformatversion = 1\n[extensions]\n\tpartialClone = false\n")
    init_repo(FL_PC_SAFE / "r-pc-empty",
              "[core]\n\trepositoryformatversion = 1\n[extensions]\n\tpartialClone = \n")
    init_repo(FL_PC_SAFE / "r-pc-origin",
              "[core]\n\trepositoryformatversion = 1\n[extensions]\n\tpartialClone = origin\n")

    # --- worktreeConfig: off + hostile stray (inert); on + benign (guarded) --
    FL_WTC_OFF = SCRATCH / "wtc-off-fleet"
    init_repo(FL_WTC_OFF / "r-wtc-false", "[extensions]\n\tworktreeConfig = false\n")
    init_repo(FL_WTC_OFF / "r-wtc-empty", "[extensions]\n\tworktreeConfig = \n")
    repo = init_repo(FL_WTC_OFF / "r-wtc-inert", "[extensions]\n\tworktreeConfig = off\n")
    # Inertness control: hostile stray config.worktree must never be opened
    # while the extension is off.
    (repo / ".git" / "config.worktree").write_text(
        f"[include]\n\tpath = {store_cfg}\n", encoding="utf-8"
    )
    FL_WTC_ON = SCRATCH / "wtc-on-fleet"
    # On + benign: main config.worktree holds a legitimate relative
    # core.worktree (resolves to the worktree itself); the linked-worktree
    # admin holds a benign absolute core.worktree. worktrees=2.
    repo = init_repo(
        FL_WTC_ON / "r-wtc-on",
        "[core]\n\trepositoryformatversion = 1\n"
        "[extensions]\n\tworktreeConfig = true\n",
    )
    (repo / ".git" / "config.worktree").write_text(
        "[core]\n\tworktree = ..\n\tbare = false\n", encoding="utf-8"
    )
    git(repo, "worktree", "add", "-q", "-b", "wt-linked", str(SCRATCH / "wt-link"))
    (repo / ".git" / "worktrees" / "wt-link" / "config.worktree").write_text(
        f"[core]\n\tworktree = {SCRATCH}/wt-link\n", encoding="utf-8"
    )

    # --- alternateRefsCommand: only the empty value is benign ----------------
    FL_ALTREFS = SCRATCH / "altrefs-fleet"
    init_repo(FL_ALTREFS / "r-altrefs-empty", "[core]\n\talternateRefsCommand = \n")
    init_repo(FL_ALTREFS / "r-altrefs-plain")

    # --- unbound filters (no reachable attributes source selects them) -------
    FL_FILTER_SAFE = SCRATCH / "filter-safe-fleet"
    init_repo(
        FL_FILTER_SAFE / "r-filter-unused",
        '[filter "safe"]\n\tclean = cat\n\tsmudge = cat\n'
        "\tprocess = cat\n\trequired = false\n",
    )
    repo = init_repo(FL_FILTER_SAFE / "r-filter-crypt")
    sent_script(repo / ".git" / "crypt.sh", SENT_FL, "cat\n")
    with (repo / ".git" / "config").open("a", encoding="utf-8") as fh:
        fh.write(f'[filter "crypt"]\n\tclean = {repo}/.git/crypt.sh\n')

    # --- key-parse false positives (exact parsed keys only) ------------------
    FL_KEYPARSE = SCRATCH / "keyparse-fleet"
    init_repo(
        FL_KEYPARSE / "r-remote-include",
        '[remote "include.d"]\n\turl = https://example.invalid/r.git\n',
    )
    init_repo(
        FL_KEYPARSE / "r-branch-prom",
        '[remote "safe"]\n\turl = https://example.invalid/r.git\n'
        '[branch "x.promisor"]\n\tremote = safe\n\tmerge = refs/heads/m\n',
    )
    init_repo(
        FL_KEYPARSE / "r-filter-cross",
        '[filter "x"]\n\trequired = true\n[diff "clean"]\n\tdriver = tee\n',
    )
    init_repo(
        FL_KEYPARSE / "r-remote-pm",
        '[remote "x.promisor-mirror"]\n\turl = https://example.invalid/m.git\n',
    )

    # --- mixed fleet (benign first/last by basename sort order) ---------------
    FL_MIXED = SCRATCH / "mixed-fleet"
    init_repo(FL_MIXED / "a-benign")
    init_repo(FL_MIXED / "m-safe-config", "[core]\n\thooksPath = /dev/null\n")
    init_repo(FL_MIXED / "z-benign")

    RECORDS = SCRATCH / "records.tsv"

    SPYDIR = SCRATCH / "spy"
    SPYDIR.mkdir()
    SPYLOG = SCRATCH / "spy.log"
    TRACELOG = SCRATCH / "strace.log"
    SPYLOG.write_text("", encoding="utf-8")
    for name in SPY_TOOLS:
        make_spy(name, REAL[name])

    # The store root is 000 so any stray access is an EACCES the strace
    # oracle can see. Children were created before chmod deliberately.
    os.chmod(AGENT, 0o000)


def probe_strace() -> None:
    probe = SCRATCH / "strace-probe.log"
    env = {"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": str(HOME), "LC_ALL": "C"}
    try:
        proc = subprocess.run(
            [
                REAL["strace"],
                "-f", "-qq", "-y",
                "-e", "trace=%file,getdents64,execve",
                "-o", str(probe),
                "--", "/bin/sh", "-c", 'cat "$1"', "sh",
                str(AGENT / "config.yml"),
            ],
            env=env,
            capture_output=True,
            text=True,
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
        "-f", "-qq", "-y",
        "-e", "trace=%file,getdents64,execve",
        "-o", str(TRACELOG),
        "--", "bash", str(TOOL), *args,
    ]
    try:
        proc = subprocess.run(
            command,
            cwd=str(SCRATCH),
            env=env,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=90,
        )
    except subprocess.TimeoutExpired:
        res = Result(124, "", "timeout", [], [], TRACELOG.exists() and TRACELOG.stat().st_size > 0, args)
        ACTIVE_RUNS.append(res)
        return res
    except OSError as exc:
        res = Result(127, "", f"exec failed: {exc}", [], [], False, args)
        ACTIVE_RUNS.append(res)
        return res
    spy = SPYLOG.read_text(encoding="utf-8", errors="replace").splitlines()
    trace_ok = TRACELOG.exists() and TRACELOG.stat().st_size > 0
    trace = (
        TRACELOG.read_text(encoding="utf-8", errors="replace").splitlines()
        if trace_ok
        else []
    )
    res = Result(proc.returncode, proc.stdout, proc.stderr, spy, trace, trace_ok, args)
    ACTIVE_RUNS.append(res)
    return res


def trace_access(trace: list[str]) -> list[str]:
    """Store access evidence: EACCES anywhere; a readlink whose path
    argument is the store or below it; an open/getdents/exec naming the
    store; any stat naming the store or a descendant. Stricter than the
    r14 positive oracle: no store stat is expected on any r15 case.
    """
    hits: list[str] = []
    seen_exec = False
    agent = str(AGENT)
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
                if path == agent or path.startswith(agent + "/"):
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
        if any(t in line for t in ("openat(", "open(", "getdents64(")):
            hits.append(line)
            continue
        if any(t in line for t in stat_tokens):
            hits.append(line)
    return hits


def spy_hits(spy: list[str]) -> list[str]:
    return [line for line in spy if str(AGENT) in line]


def spy_git_env(spy: list[str], var: str) -> list[str]:
    """Values of VAR logged during `git` spy invocations."""
    vals: list[str] = []
    in_git = False
    for line in spy:
        if line.startswith("ENV\t"):
            if in_git and line.startswith(f"ENV\t{var}\t"):
                vals.append(line.split("\t", 2)[2])
        else:
            in_git = line.startswith("git\t")
    return vals


def access_problems(res: Result, *, label: str = "") -> list[str]:
    problems: list[str] = []
    if not res.trace_ok:
        problems.append(f"{label}strace log missing or empty")
    if CANARY in res.out + res.err:
        problems.append(f"{label}contract: canary content leaked")
    if str(AGENT) in res.out + res.err:
        problems.append(f"{label}contract: synthetic store path in output")
    hits = spy_hits(res.spy)
    if hits:
        problems.append(f"{label}access: spy recorded store path: " + " | ".join(hits[:2]))
    hits = trace_access(res.trace)
    if hits:
        problems.append(f"{label}access: strace store access: " + " | ".join(hits[:2]))
    return problems


INERT_SENTINELS = (("altrefs", "SENT_AR"), ("filter", "SENT_FL"))
EXEC_SENTINELS = (("hooks", "SENT_HOOKS"), ("fsmonitor", "SENT_FSM"))


def sentinel_problems(groups: tuple = INERT_SENTINELS + EXEC_SENTINELS) -> list[str]:
    problems = []
    for name, attr in groups:
        path = globals().get(attr)
        if path is not None and path.exists():
            problems.append(f"exec: {name} sentinel {path.name} was created")
    return problems


def rows_by_name(out: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in out.splitlines()[1:]:
        if not line.strip():
            continue
        fields = line.split("\t")
        rows[fields[0].rsplit("/", 1)[-1]] = fields
    return rows


CLEAN = ("1", "0", "0", "clean")


def positive_problems(
    res: Result,
    expect: dict[str, tuple[str, str, str, str]],
    *,
    lazy_fetch: bool = False,
    pinned_env: dict[str, str] | None = None,
    no_open: tuple[str, ...] = (),
    ordered: bool = False,
) -> list[str]:
    problems: list[str] = []
    if not res.trace_ok:
        problems.append("strace log missing or empty")
    if res.rc != 0:
        problems.append(f"exit={res.rc} want 0")
        problems.extend(access_problems(res))
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
    if ordered:
        names = [
            l.split("\t", 1)[0].rsplit("/", 1)[-1]
            for l in res.out.splitlines()[1:]
            if l.strip()
        ]
        if names and names != sorted(names):
            problems.append(f"rows {names} not in basename sort order")
        if names and (names[0] != "a-benign" or names[-1] != "z-benign"):
            problems.append(
                f"row order {names} want a-benign first, z-benign last"
            )
    problems.extend(access_problems(res))
    # Inert sentinels only: altrefs/filter command values can never execute
    # under any census command set, so the assertion is arm-independent.
    # Exec sentinels (hooks/fsmonitor) are asserted only in safety-class
    # cases — a correct pre-harm arm may legitimately fire them.
    problems.extend(sentinel_problems(INERT_SENTINELS))
    if lazy_fetch:
        # Safety pin (R15CFG-08 only): every observed git call must carry
        # GIT_NO_LAZY_FETCH=1, and a successful run must show git calls.
        vals = spy_git_env(res.spy, "GIT_NO_LAZY_FETCH")
        if res.rc == 0 and not vals:
            problems.append("env: no git spy invocation observed for lazy-fetch check")
        elif vals and any(v != "1" for v in vals):
            problems.append(f"env: GIT_NO_LAZY_FETCH values {vals} want all 1")
    if pinned_env:
        for var, want_val in pinned_env.items():
            vals = spy_git_env(res.spy, var)
            if vals and any(v != want_val for v in vals):
                problems.append(f"env: {var} values {vals} want all {want_val}")
    if no_open:
        for frag in no_open:
            hits = [
                l for l in res.trace
                if frag in l and ("openat(" in l or " open(" in l)
            ]
            if hits:
                problems.append(
                    f"access: unexpected open of {frag}: " + " | ".join(hits[:2])
                )
    return problems


CONFIG_REASONS = (
    "git-config-unsupported",
    "git-config-unparsed",
    "git-include-nonregular",
    "git-include-hardlink",
    "git-metadata-nonregular",
    "git-metadata-hardlink",
    "root-protected",
    "include-protected",
    "gitdir-protected",
    "core-worktree-protected",
    "config-worktree-protected",
    "protected",
)


def refusal_problems(
    res: Result,
    *,
    reasons: tuple[str, ...] = ("git-config-unsupported",),
    label: str = "",
) -> list[str]:
    problems: list[str] = []
    if not res.trace_ok:
        problems.append(f"{label}strace log missing or empty")
    if res.rc != 2:
        problems.append(f"{label}exit={res.rc} want 2")
    if FINDING not in res.err:
        problems.append(f"{label}finding {FINDING} missing from stderr")
    elif reasons:
        m = FINDING_RE.search(res.err)
        reason = m.group(2) if m else ""
        if reason not in reasons:
            problems.append(
                f"{label}reason {reason or 'none'} want one of {reasons}"
            )
    if res.out.strip():
        problems.append(f"{label}stdout is not empty")
    problems.extend(access_problems(res, label=label))
    problems.extend(sentinel_problems())
    return problems


def unsafe_repo(names: list[str], reasons: tuple[str, ...]) -> list[str]:
    problems: list[str] = []
    for name in names:
        res = run_tool(["--root", str(UNSAFE / name), "--include-root"])
        problems.extend(
            refusal_problems(res, reasons=reasons, label=f"{name}: ")
        )
    return problems


def case_01() -> list[str]:
    expect = {
        "r-inc-rel": CLEAN,
        "r-inc-out": CLEAN,
        "r-inc-missing": CLEAN,
        "r-inc-tilde": CLEAN,
        "r-incif": CLEAN,
    }
    return positive_problems(run_tool(["--root", str(FL_INC_SAFE)]), expect)


def case_02() -> list[str]:
    return unsafe_repo(
        [
            "r-inc-store",
            "r-incif-store",
            "r-incif-hc-store",
            "r-incif-unknown",
            "r-inc-nested",
            "r-inc-symlink",
        ],
        CONFIG_REASONS,
    )


def case_03() -> list[str]:
    return unsafe_repo(
        ["r-inc-cycle", "r-inc-tildeuser", "r-inc-fifo", "r-cfg-nul"],
        CONFIG_REASONS,
    )


def case_04() -> list[str]:
    # hooksPath/fsmonitor neutralized (any value); attributesFile and
    # excludesFile honored when the target is boundary-clean: the
    # r-excl-devnull row counts the untracked file and r-excl-all is clean
    # because "*" is honored — both match the pre-harm rows exactly.
    expect = {
        "r-hooks-devnull": CLEAN,
        "r-hooks-store": CLEAN,
        "r-hooks-marker": CLEAN,
        "r-attrs-devnull": CLEAN,
        "r-attrs-safe": CLEAN,
        "r-fsm": CLEAN,
        "r-excl-devnull": ("1", "0", "1", "dirty"),
        "r-excl-all": CLEAN,
    }
    return positive_problems(run_tool(["--root", str(FL_NEUTRAL)]), expect)


def case_05() -> list[str]:
    expect = {
        "r-dirty": ("1", "0", "2", "dirty"),
        "r-ignored": CLEAN,
    }
    return positive_problems(run_tool(["--root", str(FL_DIRTY)]), expect)


def case_06() -> list[str]:
    # Complete-repo promisor markers: every value is a valid boolean or a
    # remote name; on a complete repo no lazy fetch can trigger so the
    # markers are inert and every row must be accurate. Pure restitution
    # oracle — the GIT_NO_LAZY_FETCH pin lives in R15CFG-08.
    expect = {
        "r-prom-false": CLEAN,
        "r-prom-empty": CLEAN,
        "r-prom-off": CLEAN,
        "r-prom-zero": CLEAN,
        "r-prom-true": CLEAN,
        "r-prom-bare": CLEAN,
        "r-prom-yes": CLEAN,
        "r-prom-two": CLEAN,
        "r-pcf": CLEAN,
    }
    return positive_problems(run_tool(["--root", str(FL_PROM_SAFE)]), expect)


def case_07() -> list[str]:
    # Invalid booleans only: could-not-evaluate refuses fail-closed.
    return unsafe_repo(
        ["r-prom-maybe", "r-prom-maybe2"],
        ("git-config-unsupported", "git-config-unparsed"),
    )


def case_08() -> list[str]:
    # Safety sentries, not restitution: a correct repaired arm proves the
    # neutralizing overrides keep hooks/fsmonitor sentinels from firing and
    # that every observed git call carries GIT_NO_LAZY_FETCH=1. pre-harm
    # may fire the sentinels (expected red there), and the harm arm misses
    # the pcf refusal anyway — this case is safety-classified on purpose.
    problems = positive_problems(
        run_tool(["--root", str(FL_SENTRY)]),
        {"s-hooks": CLEAN, "s-fsm": CLEAN},
        lazy_fetch=True,
    )
    problems.extend(sentinel_problems(EXEC_SENTINELS))
    return problems


def case_09() -> list[str]:
    # partialClone values are remote names, never booleans — benign on a
    # complete repo under NO_LAZY_FETCH.
    expect = {
        "r-pc-false": CLEAN,
        "r-pc-empty": CLEAN,
        "r-pc-origin": CLEAN,
    }
    return positive_problems(run_tool(["--root", str(FL_PC_SAFE)]), expect)


def case_10() -> list[str]:
    # Off: hostile stray config.worktree must never be opened.
    off = positive_problems(
        run_tool(["--root", str(FL_WTC_OFF)]),
        {
            "r-wtc-false": CLEAN,
            "r-wtc-empty": CLEAN,
            "r-wtc-inert": CLEAN,
        },
        no_open=("config.worktree",),
    )
    # On + benign config.worktree (main relative core.worktree=.. and a
    # linked admin config.worktree with an absolute core.worktree): green.
    on = positive_problems(
        run_tool(["--root", str(FL_WTC_ON)]),
        {"r-wtc-on": ("2", "0", "0", "clean")},
    )
    return off + ["on-fleet: " + p for p in on]


def case_11() -> list[str]:
    return unsafe_repo(
        [
            "r-wtc-hostile",
            "r-wtc-cwt",
            "r-wtc-maybe",
            "r-attrs-store",
            "r-excl-store",
        ],
        CONFIG_REASONS,
    )


def case_12() -> list[str]:
    expect = {
        "r-altrefs-empty": CLEAN,
        "r-altrefs-plain": CLEAN,
    }
    return positive_problems(run_tool(["--root", str(FL_ALTREFS)]), expect)


def case_13() -> list[str]:
    expect = {
        "r-filter-unused": CLEAN,
        "r-filter-crypt": CLEAN,
    }
    return positive_problems(run_tool(["--root", str(FL_FILTER_SAFE)]), expect)


def case_14() -> list[str]:
    return unsafe_repo(
        [
            "r-filter-clean",
            "r-filter-process",
            "r-altrefs-cmd",
            "r-altrefs-exit",
            "r-altrefs-bare",
        ],
        ("git-config-unsupported",),
    )


def case_15() -> list[str]:
    expect = {
        "r-remote-include": CLEAN,
        "r-branch-prom": CLEAN,
        "r-filter-cross": CLEAN,
        "r-remote-pm": CLEAN,
    }
    return positive_problems(run_tool(["--root", str(FL_KEYPARSE)]), expect)


def case_16() -> list[str]:
    expect = {
        "a-benign": CLEAN,
        "m-safe-config": CLEAN,
        "z-benign": CLEAN,
    }
    return positive_problems(
        run_tool(["--root", str(FL_MIXED)]), expect, ordered=True
    )


def case_17() -> list[str]:
    return refusal_problems(
        run_tool(["--root", str(FL_MIXED_UNSAFE)]), reasons=CONFIG_REASONS
    )


def case_18() -> list[str]:
    poison = SCRATCH / "poison.gitconfig"
    poison.write_text(
        f"[include]\n\tpath = {AGENT}/secret.gitconfig\n"
        f"[core]\n\thooksPath = {AGENT}/hooks\n"
        '[remote "z"]\n\tpromisor = true\n',
        encoding="utf-8",
    )
    (HOME / ".gitconfig").write_text(
        f"[include]\n\tpath = {AGENT}/secret.gitconfig\n", encoding="utf-8"
    )
    extra = {
        "GIT_CONFIG_GLOBAL": str(poison),
        "GIT_DIR": str(AGENT / "gd"),
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "include.path",
        "GIT_CONFIG_VALUE_0": str(AGENT / "secret.gitconfig"),
    }
    expect = {
        "a-benign": CLEAN,
        "m-safe-config": CLEAN,
        "z-benign": CLEAN,
    }
    return positive_problems(
        run_tool(["--root", str(FL_MIXED)], extra),
        expect,
        pinned_env={"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_DIR": ""},
    )


def case_19() -> list[str]:
    problems: list[str] = []
    for label, root in (("store", str(AGENT)), ("ancestor", str(HOME))):
        res = run_tool(["--root", root])
        problems.extend(refusal_problems(res, reasons=(), label=f"{label}: "))
    return problems


def case_20() -> list[str]:
    problems: list[str] = []
    res = run_tool(["--root", str(FL_MIXED)])
    problems.extend(
        positive_problems(
            res,
            {"a-benign": CLEAN, "m-safe-config": CLEAN, "z-benign": CLEAN},
        )
    )
    if res.rc == 0:
        RECORDS.write_text(res.out, encoding="utf-8")
        same = run_tool(["--root", str(FL_MIXED), "--compare", str(RECORDS)])
        if same.rc != 0:
            problems.append(f"compare-identical exit={same.rc} want 0")
        problems.extend(access_problems(same, label="compare-identical: "))
        (FL_MIXED / "a-benign" / "drift.txt").write_text("drift\n", encoding="utf-8")
        drift = run_tool(["--root", str(FL_MIXED), "--compare", str(RECORDS)])
        if drift.rc != 3:
            problems.append(f"compare-drift exit={drift.rc} want 3")
        problems.extend(access_problems(drift, label="compare-drift: "))
        (FL_MIXED / "a-benign" / "drift.txt").unlink()
        bad = SCRATCH / "bad-records.tsv"
        bad.write_text("garbage\n", encoding="utf-8")
        malformed = run_tool(["--root", str(FL_MIXED), "--compare", str(bad)])
        if malformed.rc != 2:
            problems.append(f"compare-malformed exit={malformed.rc} want 2")
        problems.extend(access_problems(malformed, label="compare-malformed: "))
    return problems


CASES = {
    "R15CFG-01": case_01,
    "R15CFG-02": case_02,
    "R15CFG-03": case_03,
    "R15CFG-04": case_04,
    "R15CFG-05": case_05,
    "R15CFG-06": case_06,
    "R15CFG-07": case_07,
    "R15CFG-08": case_08,
    "R15CFG-09": case_09,
    "R15CFG-10": case_10,
    "R15CFG-11": case_11,
    "R15CFG-12": case_12,
    "R15CFG-13": case_13,
    "R15CFG-14": case_14,
    "R15CFG-15": case_15,
    "R15CFG-16": case_16,
    "R15CFG-17": case_17,
    "R15CFG-18": case_18,
    "R15CFG-19": case_19,
    "R15CFG-20": case_20,
}


def cleanup() -> None:
    try:
        if "AGENT" in globals() and AGENT.exists():
            os.chmod(AGENT, 0o700)
    except OSError:
        pass
    if "SCRATCH" in globals():
        shutil.rmtree(SCRATCH, ignore_errors=False)


def main(argv: list[str]) -> int:
    global SCRATCH, TOOL, ACTIVE_RUNS

    parser = argparse.ArgumentParser(
        prog="r15-census-config.py",
        description="C1 census value-aware config isolation fixture",
    )
    parser.add_argument(
        "--tool",
        help="census tool under test (default: lane tools/souji-census.sh)",
    )
    parser.add_argument(
        "--case", action="append", default=[], metavar="ID",
        help="run one case (repeatable; debugging only, never for admission)",
    )
    parser.add_argument("--list", action="store_true", help="print case ids and exit")
    parser.add_argument(
        "--json", action="store_true",
        help="emit one JSON line with per-case records for the C2 checker",
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
        die("refusing to run as root: mode-000 store would not be denied")

    TOOL = (
        Path(args.tool)
        if args.tool
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
        SCRATCH = Path(tempfile.mkdtemp(prefix="r15-census-config.", dir="/var/tmp"))
    except OSError as exc:
        die(f"cannot create /var/tmp fixture: {exc}")
    records: list[dict] = []
    try:
        try:
            build_world()
            probe_strace()
        except SystemExit:
            raise
        except Exception as exc:
            die(f"setup failed: {exc}")
        digest = hashlib.sha256(TOOL.read_bytes()).hexdigest()
        if digest == HARM_SHA:
            kind = "r14-harm-baseline"
        elif digest == PREHARM_SHA:
            kind = "pre-harm-a31642d"
        else:
            kind = "other"
        print(f"TOOL\t{TOOL}\tsha256={digest}")
        print(f"TOOL-KIND\t{kind}")
        failed = 0
        ran: list[str] = []
        for cid in selected:
            ACTIVE_RUNS = []
            # The oracle is identical for every arm: baseline red is an
            # observed behavioral failure, never a digest-keyed verdict.
            # Non-discrimination on the harm digest is the independent
            # admission checker's refusal, not a fabricated fixture FAIL.
            problems = CASES[cid]()
            status = "PASS" if not problems else "FAIL"
            last = ACTIVE_RUNS[-1] if ACTIVE_RUNS else None
            obs_exit = last.rc if last else -1
            obs_finding = last.finding if last else "none"
            detail = (
                "; ".join(problems) if problems else "ok"
            ) + f"\tobserved_exit={obs_exit}\tobserved_finding={obs_finding}"
            print(f"CASE\t{cid}\t{status}\t{detail}")
            if problems:
                failed += 1
            ran.append(cid)
            records.append(
                {
                    "id": cid,
                    "class": CASE_CLASSES.get(cid, "unknown"),
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
                        "fixture": "r15-census-config",
                        "expected_ids": list(EXPECTED_IDS),
                        "case_classes": CASE_CLASSES,
                        "harm_cases": sorted(HARM_CASES),
                        "tool": {
                            "path": str(TOOL),
                            "sha256": digest,
                            "kind": kind,
                        },
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
