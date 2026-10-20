#!/usr/bin/env python3
"""Round-18 C1 falsifier for per-repository census timeouts.

Builds isolated repositories and injects writer-less FIFOs only after the
census has passed its metadata guard. Every census invocation has a private
session, a 40-second fixture deadline, and post-run session/FIFO cleanup
checks. Fixture deadline expiration is rc 124 and always fails.
"""

from __future__ import annotations

import argparse
import hashlib
import errno
import json
import os
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

HEADER = (
    "repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\t"
    "verdict_flags"
)
EXPECTED_IDS = (
    "B1", "B2", "B3", "B4", "B5", "B6",
    "B7", "B8", "B9", "B10", "B11", "B12",
)
FIXTURE_TIMEOUT = 40
DEFAULT_REPO_TIMEOUT = 8
SEAT_TMP = Path("/var/tmp")
SYSTEM_PATH = "/usr/local/bin:/usr/bin:/bin"
REAL_GIT = "/usr/bin/git"
REAL_BASH = "/usr/bin/bash"
REAL_CMP = "/usr/bin/cmp"


@dataclass
class CensusRun:
    label: str
    argv: list[str]
    rc: int
    stdout: str
    stderr: str
    elapsed: float
    session_id: int
    fixture_timed_out: bool
    isolated_session: bool
    leaked_before_cleanup: list[dict[str, int | str]] = field(default_factory=list)
    session_after_cleanup: list[dict[str, int | str]] = field(default_factory=list)

    def rows(self) -> dict[str, list[str]]:
        return rows_by_name(self.stdout)

    @staticmethod
    def trigger_log(path: Path) -> list[dict]:
        if not path.exists():
            return []
        records = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                records.append({"malformed": line})
        return records


@dataclass
class CaseResult:
    case_id: str
    expected_exit: int | None
    expected_rows: dict[str, str]
    problems: list[str]
    runs: list[CensusRun] = field(default_factory=list)
    notes: dict = field(default_factory=dict)


class Fixture:
    def __init__(self, tool: Path) -> None:
        self.tool = tool.resolve()
        self.scratch: Path | None = None
        self.home: Path | None = None
        self.agent: Path | None = None
        self.spy_dir: Path | None = None
        self.spy_log: Path | None = None
        self.gitshim: Path | None = None
        self.cmp_dir: Path | None = None
        self.cmp_log: Path | None = None
        self.cmpshim: Path | None = None
        self.runs: list[CensusRun] = []
        self.fifos: list[Path] = []
        self.case_results: list[CaseResult] = []
        self.real_git = REAL_GIT

    def setup(self) -> None:
        if os.geteuid() == 0:
            die("refusing to run as root")
        if not self.tool.is_file():
            die(f"census tool not readable: {self.tool}")
        self.tool.read_bytes()
        if (
            not Path(self.real_git).is_file()
            or not Path(REAL_BASH).is_file()
            or not Path(REAL_CMP).is_file()
        ):
            die("required system Git, Bash, or cmp executable is missing")
        self.scratch = Path(
            tempfile.mkdtemp(
                prefix="souji-r18-FixtureR18Bounded.", dir=SEAT_TMP
            )
        )
        self.home = self.scratch / "home"
        self.home.mkdir()
        self.agent = self.home / ".omp" / "agent"
        self.agent.mkdir(parents=True)
        self.spy_dir = self.scratch / "git-shim"
        self.spy_dir.mkdir()
        self.spy_log = self.scratch / "git-shim.jsonl"
        self.spy_log.touch()
        self.gitshim = self.spy_dir / "git"
        self.cmp_dir = self.scratch / "cmp-shim"
        self.cmp_dir.mkdir()
        self.cmp_log = self.scratch / "cmp-shim.jsonl"
        self.cmp_log.touch()
        self.cmpshim = self.cmp_dir / "cmp"

    @property
    def root(self) -> Path:
        assert self.scratch is not None
        return self.scratch

    @property
    def home_path(self) -> Path:
        assert self.home is not None
        return self.home

    @property
    def agent_path(self) -> Path:
        assert self.agent is not None
        return self.agent

    @property
    def shim_dir(self) -> Path:
        assert self.spy_dir is not None
        return self.spy_dir

    @property
    def shim_log_path(self) -> Path:
        assert self.spy_log is not None
        return self.spy_log

    @property
    def cmp_dir_path(self) -> Path:
        assert self.cmp_dir is not None
        return self.cmp_dir

    @property
    def cmp_log_path(self) -> Path:
        assert self.cmp_log is not None
        return self.cmp_log

    def setup_env(self) -> dict[str, str]:
        return {
            "PATH": SYSTEM_PATH,
            "HOME": str(self.home_path),
            "XDG_CONFIG_HOME": str(self.home_path / ".config"),
            "TMPDIR": str(self.root),
            "LC_ALL": "C",
            "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_CONFIG_SYSTEM": "/dev/null",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_NO_LAZY_FETCH": "1",
            "GIT_AUTHOR_NAME": "r18-census-bounded",
            "GIT_AUTHOR_EMAIL": "r18@example.invalid",
            "GIT_COMMITTER_NAME": "r18-census-bounded",
            "GIT_COMMITTER_EMAIL": "r18@example.invalid",
        }

    def run_setup(self, argv: list[str]) -> subprocess.CompletedProcess[str]:
        try:
            result = subprocess.run(
                argv,
                cwd=str(self.root),
                env=self.setup_env(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                errors="replace",
                timeout=45,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            die(f"setup command failed: {argv!r}: {exc}")
        if result.returncode != 0:
            die(
                f"setup command exit={result.returncode}: {argv!r}: "
                f"{result.stderr.strip()}"
            )
        return result

    def git(self, repo: Path, *args: str) -> str:
        result = self.run_setup(
            [self.real_git, "-c", "maintenance.auto=false", "-C", str(repo), *args]
        )
        return result.stdout

    def init_repo(self, repo: Path) -> Path:
        repo.mkdir(parents=True)
        self.git(repo, "init", "-q", "--initial-branch=main")
        (repo / "kept.txt").write_text("kept\n", encoding="utf-8")
        self.git(repo, "add", "--", "kept.txt")
        self.git(repo, "commit", "-qm", "initial")
        head = self.git(repo, "rev-parse", "HEAD").strip()
        self.git(repo, "update-ref", "refs/remotes/origin/main", head)
        info = repo / ".git" / "info"
        info.mkdir(exist_ok=True)
        attrs = info / "attributes"
        if not attrs.exists():
            attrs.write_text("", encoding="utf-8")
        return repo

    def fleet(self, name: str, repo_names: tuple[str, ...] = ("a", "b", "c")) -> tuple[Path, dict[str, Path]]:
        fleet_root = self.root / name
        fleet_root.mkdir()
        repos = {repo_name: self.init_repo(fleet_root / repo_name) for repo_name in repo_names}
        return fleet_root, repos

    def touch_tracked(self, repo: Path) -> None:
        tracked = repo / "kept.txt"
        old = tracked.stat()
        # Preserve bytes but force Git's index refresh to hash the tracked file.
        os.utime(tracked, (old.st_atime, max(time.time(), old.st_mtime) + 30))

    def add_bound_filter(self, repo: Path) -> None:
        self.git(repo, "config", "filter.r18.clean", "cat")
        (repo / ".gitattributes").write_text("kept.txt filter=r18\n", encoding="utf-8")
        self.git(repo, "add", "--", ".gitattributes")
        self.git(repo, "commit", "-qm", "bind clean filter")
        head = self.git(repo, "rev-parse", "HEAD").strip()
        self.git(repo, "update-ref", "refs/remotes/origin/main", head)

    def install_git_shim(self) -> Path:
        code = '''#!/usr/bin/python3
import json
import os
import signal
import sys
import time
from pathlib import Path

args = sys.argv[1:]
real = os.environ["R18_REAL_GIT"]
trigger = os.environ.get("R18_TRIGGER", "")
target_repo = os.path.realpath(os.environ.get("R18_TARGET_REPO", ""))
fifo_raw = os.environ.get("R18_FIFO_PATH", "")
fifo_path = Path(fifo_raw) if fifo_raw else None
marker = Path(os.environ.get("R18_TRIGGER_MARKER", "/nonexistent"))
hang_mode = os.environ.get("R18_HANG_MODE", "")
hang_pid_raw = os.environ.get("R18_HANG_PID_FILE", "")
hang_pid_file = Path(hang_pid_raw) if hang_pid_raw else None
term_file_raw = os.environ.get("R18_TERM_FILE", "")
term_file = Path(term_file_raw) if term_file_raw else None
log = Path(os.environ["R18_SHIM_LOG"])
delay = float(os.environ.get("R18_DELAY_SECONDS", "0"))
command = next((arg for arg in args if arg in {"status", "check-attr"}), "")
repo = ""
for index, arg in enumerate(args[:-1]):
    if arg == "-C":
        repo = os.path.realpath(args[index + 1])
        break
triggered = False
trigger_error = ""
hang_started = None
if trigger and command == trigger and repo == target_repo and not marker.exists():
    try:
        if fifo_path is not None:
            fifo_path.unlink(missing_ok=True)
            os.mkfifo(fifo_path)
        if hang_mode:
            if hang_pid_file is None:
                raise OSError("hang pid file was not provided")
            hang_started = time.monotonic()
            hang_pid_file.write_text(
                json.dumps({"pid": os.getpid(), "started": hang_started}),
                encoding="utf-8",
            )
        marker.write_text("triggered\\n", encoding="utf-8")
        triggered = True
    except OSError as exc:
        trigger_error = str(exc)
record = {
    "argv": args,
    "command": command,
    "repo": repo,
    "triggered": triggered,
    "trigger_error": trigger_error,
    "delayed": delay > 0,
    "hang_mode": hang_mode,
}
with log.open("a", encoding="utf-8") as stream:
    stream.write(json.dumps(record, sort_keys=True) + "\\n")
if triggered and hang_mode:
    if hang_mode == "ignore-term":
        def record_term(_signum, _frame):
            if term_file is not None:
                try:
                    term_file.write_text(str(time.monotonic()), encoding="ascii")
                except OSError:
                    pass
        signal.signal(signal.SIGTERM, record_term)
    else:
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
    while True:
        signal.pause()
if delay:
    time.sleep(delay)
os.execv(real, [real, *args])
'''
        assert self.gitshim is not None
        self.gitshim.write_text(code, encoding="utf-8")
        self.gitshim.chmod(0o755)
        return self.gitshim

    def install_cmp_shim(self) -> Path:
        code = '''#!/usr/bin/python3
import json
import os
import sys
from pathlib import Path

args = sys.argv[1:]
real = "/usr/bin/cmp"
trigger = os.environ.get("R18_CMP_TRIGGER", "")
target_config = os.path.realpath(os.environ.get("R18_CMP_TARGET_CONFIG", ""))
fifo_path = Path(os.environ.get("R18_CMP_FIFO_PATH", "/nonexistent"))
marker = Path(os.environ.get("R18_CMP_TRIGGER_MARKER", "/nonexistent"))
log = Path(os.environ["R18_CMP_LOG"])
candidate = os.path.realpath(args[-1]) if args else ""
triggered = False
trigger_error = ""
if trigger and candidate == target_config and not marker.exists():
    try:
        fifo_path.unlink(missing_ok=True)
        os.mkfifo(fifo_path)
        marker.write_text("triggered\\n", encoding="utf-8")
        triggered = True
    except OSError as exc:
        trigger_error = str(exc)
record = {
    "argv": args,
    "candidate": candidate,
    "target_config": target_config,
    "trigger": trigger,
    "triggered": triggered,
}
with log.open("a", encoding="utf-8") as stream:
    stream.write(json.dumps(record, sort_keys=True) + "\\n")
'''
        assert self.cmpshim is not None
        self.cmpshim.write_text(code, encoding="utf-8")
        self.cmpshim.chmod(0o755)
        return self.cmpshim

    def write_cmp_options(self) -> None:
        self.cmp_log_path.write_text("", encoding="utf-8")
        (self.root / "cmp-triggered").unlink(missing_ok=True)

    def census_env(
        self,
        repo_timeout: int,
        *,
        use_shim: bool = False,
        trigger: str = "",
        target_repo: Path | None = None,
        fifo_path: Path | None = None,
        delay_seconds: int = 0,
        use_cmp_shim: bool = False,
        hang_mode: str = "",
        hang_pid_file: Path | None = None,
        term_file: Path | None = None,
    ) -> dict[str, str]:
        path_dirs = []
        if use_shim:
            path_dirs.append(str(self.shim_dir))
        if use_cmp_shim:
            path_dirs.append(str(self.cmp_dir_path))
        env = {
            "PATH": ":".join([*path_dirs, SYSTEM_PATH]),
            "HOME": str(self.home_path),
            "XDG_CONFIG_HOME": str(self.home_path / ".config"),
            "TMPDIR": str(self.root),
            "LC_ALL": "C",
            "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_CONFIG_SYSTEM": "/dev/null",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_NO_LAZY_FETCH": "1",
            # Compatibility input only: the base census ignores it.
            "SOUJI_CENSUS_REPO_TIMEOUT": str(repo_timeout),
        }
        if use_shim:
            env.update(
                {
                    "R18_REAL_GIT": self.real_git,
                    "R18_SHIM_LOG": str(self.shim_log_path),
                    "R18_TRIGGER": trigger,
                    "R18_TARGET_REPO": str(target_repo or ""),
                    "R18_FIFO_PATH": str(fifo_path or ""),
                    "R18_TRIGGER_MARKER": str(self.root / "shim-triggered"),
                    "R18_DELAY_SECONDS": str(delay_seconds),
                    "R18_HANG_MODE": hang_mode,
                    "R18_HANG_PID_FILE": str(hang_pid_file or ""),
                    "R18_TERM_FILE": str(term_file or ""),
                }
            )
        if use_cmp_shim:
            env.update(
                {
                    "R18_CMP_TRIGGER": trigger,
                    "R18_CMP_TARGET_CONFIG": (
                        str(target_repo / ".git" / "config") if target_repo else ""
                    ),
                    "R18_CMP_FIFO_PATH": str(fifo_path or ""),
                    "R18_CMP_TRIGGER_MARKER": str(self.root / "cmp-triggered"),
                    "R18_CMP_LOG": str(self.cmp_log_path),
                }
            )
        return env

    @staticmethod
    def process_snapshot() -> dict[int, dict[str, int | str]]:
        snapshot: dict[int, dict[str, int | str]] = {}
        proc_root = Path("/proc")
        try:
            entries = list(proc_root.iterdir())
        except OSError:
            return snapshot
        for entry in entries:
            if not entry.name.isdigit():
                continue
            try:
                raw = (entry / "stat").read_text(encoding="ascii")
                close = raw.rfind(")")
                if close < 0:
                    continue
                fields = raw[close + 1 :].split()
                if len(fields) < 4:
                    continue
                snapshot[int(entry.name)] = {
                    "state": fields[0],
                    "ppid": int(fields[1]),
                    "pgid": int(fields[2]),
                    "session": int(fields[3]),
                }
            except (OSError, ValueError):
                continue
        return snapshot

    @classmethod
    def session_members(cls, session_id: int) -> list[dict[str, int | str]]:
        snapshot = cls.process_snapshot()
        return [
            {"pid": pid, **values}
            for pid, values in snapshot.items()
            if values["session"] == session_id
        ]

    @classmethod
    def kill_session(
        cls,
        session_id: int,
        members: list[dict[str, int | str]],
        *,
        root_group_killed: bool = False,
    ) -> None:
        # Never signal the fixture's own process group/session. Census runs
        # get a distinct session from Popen(start_new_session=True).
        protected_groups = {os.getpgrp(), os.getsid(0)}
        if session_id in protected_groups:
            return
        del members
        root_was_killed = root_group_killed
        # /proc stat fields after comm begin with state: pgrp is field 5 and
        # session is field 6. Re-scan the private SID after every sweep so
        # children moved by bash `set -m` cannot survive in another PGID.
        for _ in range(40):
            current = cls.session_members(session_id)
            if not current:
                return
            groups = {int(member["pgid"]) for member in current}
            if not root_was_killed and session_id in groups:
                try:
                    os.killpg(session_id, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                except PermissionError:
                    return
                root_was_killed = True
            groups.discard(session_id)
            groups.difference_update(protected_groups)
            for group in sorted(groups):
                try:
                    os.killpg(group, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                except PermissionError:
                    continue
            time.sleep(0.05)

    @classmethod
    def wait_session_empty(
        cls, session_id: int, seconds: float = 2.0
    ) -> list[dict[str, int | str]]:
        deadline = time.monotonic() + seconds
        members = cls.session_members(session_id)
        while members and time.monotonic() < deadline:
            time.sleep(0.05)
            members = cls.session_members(session_id)
        return members

    def census(
        self,
        label: str,
        root: Path,
        *,
        repo_timeout: int = DEFAULT_REPO_TIMEOUT,
        use_shim: bool = False,
        trigger: str = "",
        target_repo: Path | None = None,
        fifo_path: Path | None = None,
        delay_seconds: int = 0,
        use_cmp_shim: bool = False,
        hang_mode: str = "",
        hang_pid_file: Path | None = None,
        term_file: Path | None = None,
        compare_path: Path | None = None,
        include_root: bool = False,
    ) -> CensusRun:
        argv = [REAL_BASH, str(self.tool)]
        if compare_path is None:
            argv.extend(["--root", str(root)])
        else:
            argv.extend(["--root", str(root), "--compare", str(compare_path)])
        if include_root:
            argv.append("--include-root")
        proc = subprocess.Popen(
            argv,
            cwd=str(self.root),
            env=self.census_env(
                repo_timeout,
                use_shim=use_shim,
                trigger=trigger,
                target_repo=target_repo,
                fifo_path=fifo_path,
                delay_seconds=delay_seconds,
                use_cmp_shim=use_cmp_shim,
                hang_mode=hang_mode,
                hang_pid_file=hang_pid_file,
                term_file=term_file,
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            start_new_session=True,
        )
        started = time.monotonic()
        fixture_timed_out = False
        try:
            isolated_session = (
                os.getsid(proc.pid) == proc.pid
                and os.getpgid(proc.pid) == proc.pid
            )
        except ProcessLookupError:
            # Popen used start_new_session=True; an already-exited process
            # needs no signal sweep.
            isolated_session = True
        try:
            stdout, stderr = proc.communicate(timeout=FIXTURE_TIMEOUT)
        except subprocess.TimeoutExpired as exc:
            fixture_timed_out = True
            members = self.session_members(proc.pid)
            leader = self.process_snapshot().get(proc.pid)
            verified_session = bool(
                (leader and leader["session"] == proc.pid and leader["pgid"] == proc.pid)
                or (members and all(member["session"] == proc.pid for member in members))
            )
            isolated_session = isolated_session and verified_session
            root_group_present = any(member["pgid"] == proc.pid for member in members)
            if isolated_session:
                # Signal the original private session group only while a
                # member proves its PGID has not been recycled.
                if root_group_present:
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                self.kill_session(
                    proc.pid, members, root_group_killed=root_group_present
                )
            else:
                proc.kill()
            try:
                stdout, stderr = proc.communicate(timeout=5)
            except subprocess.TimeoutExpired as final_exc:
                proc.kill()
                proc.wait(timeout=5)
                stdout = final_exc.output or exc.output or ""
                stderr = final_exc.stderr or exc.stderr or ""
                if isinstance(stdout, bytes):
                    stdout = stdout.decode("utf-8", "replace")
                if isinstance(stderr, bytes):
                    stderr = stderr.decode("utf-8", "replace")
                if proc.stdout:
                    proc.stdout.close()
                if proc.stderr:
                    proc.stderr.close()
            rc = 124
        else:
            rc = proc.returncode if proc.returncode is not None else -1
        elapsed = time.monotonic() - started
        members = self.session_members(proc.pid)
        leaked_before_cleanup = list(members)
        if members:
            isolated_session = isolated_session and all(
                member["session"] == proc.pid for member in members
            )
            if isolated_session:
                root_group_present = any(member["pgid"] == proc.pid for member in members)
                if root_group_present:
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                self.kill_session(
                    proc.pid, members, root_group_killed=root_group_present
                )
        after = self.wait_session_empty(proc.pid)
        run = CensusRun(
            label=label,
            argv=argv,
            rc=rc,
            stdout=stdout,
            stderr=stderr,
            elapsed=elapsed,
            session_id=proc.pid,
            fixture_timed_out=fixture_timed_out,
            isolated_session=isolated_session,
            leaked_before_cleanup=leaked_before_cleanup,
            session_after_cleanup=after,
        )
        self.runs.append(run)
        return run

    def interrupt_census(
        self,
        label: str,
        root: Path,
        target_repo: Path,
        *,
        signal_number: int,
        repo_timeout: int = DEFAULT_REPO_TIMEOUT,
    ) -> tuple[CensusRun, list[str], dict]:
        marker = self.root / f"{label}-git.json"
        term_file = self.root / f"{label}-term.txt"
        marker.unlink(missing_ok=True)
        term_file.unlink(missing_ok=True)
        argv = [REAL_BASH, str(self.tool), "--root", str(root)]
        proc = subprocess.Popen(
            argv,
            cwd=str(self.root),
            env=self.census_env(
                repo_timeout,
                use_shim=True,
                trigger="status",
                target_repo=target_repo,
                hang_mode="default-term",
                hang_pid_file=marker,
                term_file=term_file,
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            start_new_session=True,
        )
        started = time.monotonic()
        problems: list[str] = []
        try:
            isolated = (
                os.getsid(proc.pid) == proc.pid and os.getpgid(proc.pid) == proc.pid
            )
        except ProcessLookupError:
            isolated = True

        marker_deadline = started + 15.0
        while not marker.exists() and proc.poll() is None and time.monotonic() < marker_deadline:
            time.sleep(0.02)
        marker_record = {}
        if marker.exists():
            try:
                marker_record = json.loads(marker.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                problems.append(f"invalid Git hang marker: {exc}")
        else:
            problems.append("Git hang shim did not reach the selected status call")

        signal_sent = time.monotonic()
        try:
            os.kill(proc.pid, signal_number)
        except ProcessLookupError:
            problems.append(f"census parent exited before signal {signal.Signals(signal_number).name}")
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            problems.append("census parent did not exit after external signal")
            proc.kill()
            proc.wait(timeout=5)

        if signal_number == signal.SIGTERM:
            # TERM must synchronously reap the worker and timer before the
            # parent exits; allow only a short scheduling grace.
            deadline = time.monotonic() + 0.75
        else:
            # SIGKILL cannot run cleanup. The detached watchdog must still
            # expire at the repo bound and kill after its two-second grace.
            worker_started = float(marker_record.get("started", signal_sent))
            deadline = max(
                signal_sent,
                worker_started + repo_timeout + 2.5,
            )
        while time.monotonic() < deadline:
            time.sleep(min(0.05, max(0.0, deadline - time.monotonic())))
        leftovers = self.session_members(proc.pid)
        expected_returncode = -signal_number
        if proc.returncode != expected_returncode:
            problems.append(
                f"parent returncode={proc.returncode} expected {expected_returncode}"
            )
        if leftovers:
            problems.append(
                f"session still contains worker/watchdog after signal window: {leftovers}"
            )

        worker_pid = marker_record.get("pid")
        snapshot = self.process_snapshot()
        if worker_pid is not None:
            worker = snapshot.get(int(worker_pid))
            if worker is not None and worker.get("session") == proc.pid:
                problems.append(f"stalled Git PID {worker_pid} survived signal window")

        if leftovers and isolated:
            root_group_present = any(member["pgid"] == proc.pid for member in leftovers)
            if root_group_present:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            self.kill_session(
                proc.pid, leftovers, root_group_killed=root_group_present
            )
        after = self.wait_session_empty(proc.pid)
        if after:
            problems.append(f"session remains after fixture cleanup: {after}")
        try:
            stdout, stderr = proc.communicate(timeout=3)
        except subprocess.TimeoutExpired as exc:
            problems.append("census pipes stayed open after session cleanup")
            stdout = exc.output or ""
            stderr = exc.stderr or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", "replace")
            if isinstance(stderr, bytes):
                stderr = stderr.decode("utf-8", "replace")
            if proc.stdout:
                proc.stdout.close()
            if proc.stderr:
                proc.stderr.close()
        elapsed = time.monotonic() - started
        run = CensusRun(
            label=label,
            argv=argv,
            rc=proc.returncode if proc.returncode is not None else -1,
            stdout=stdout,
            stderr=stderr,
            elapsed=elapsed,
            session_id=proc.pid,
            fixture_timed_out=False,
            isolated_session=isolated,
            leaked_before_cleanup=leftovers,
            session_after_cleanup=after,
        )
        self.runs.append(run)
        return run, problems, {
            "signal": signal.Signals(signal_number).name,
            "parent_returncode": run.rc,
            "marker": marker_record,
            "term_file": str(term_file) if term_file.exists() else None,
            "signal_to_parent_seconds": round(signal_sent - started, 3),
            "elapsed_seconds": round(elapsed, 3),
            "session_after_window": leftovers,
            "session_after_cleanup": after,
            "stdout": stdout,
            "stderr": stderr.splitlines(),
        }

    @staticmethod
    def expected_row_problems(
        row: list[str] | None,
        repo_name: str,
        kind: str,
    ) -> list[str]:
        if row is None:
            return [f"{repo_name}: row missing; expected {kind}"]
        if len(row) != 7:
            return [f"{repo_name}: row has {len(row)} columns, expected 7"]
        if kind == "error":
            if row[1:] != ["0", "0", "0", "0", "", "error"]:
                return [
                    f"{repo_name}: row fields {row[1:]} expected "
                    "['0', '0', '0', '0', '', 'error']"
                ]
            return []
        if row[1] != "1":
            return [f"{repo_name}: worktrees={row[1]} expected 1"]
        if row[2] != "0":
            return [f"{repo_name}: unpushed={row[2]} expected 0"]
        if row[4] != "0":
            return [f"{repo_name}: scratch_bytes={row[4]} expected 0"]
        if not row[5]:
            return [f"{repo_name}: mtime_iso is empty"]
        if kind == "clean":
            if row[3] != "0" or row[6] != "clean":
                return [
                    f"{repo_name}: dirty/flags={row[3]}/{row[6]} "
                    "expected 0/clean"
                ]
            return []
        if kind == "dirty":
            if row[3] != "1" or row[6] != "dirty":
                return [
                    f"{repo_name}: dirty/flags={row[3]}/{row[6]} "
                    "expected 1/dirty"
                ]
            return []
        if kind == "status-unverifiable":
            if row[3] != "0" or row[6] != "status-unverifiable":
                return [
                    f"{repo_name}: dirty/flags={row[3]}/{row[6]} "
                    "expected 0/status-unverifiable"
                ]
            return []
        return [f"{repo_name}: unknown expected row kind {kind}"]

    @classmethod
    def census_problems(
        cls,
        run: CensusRun,
        expected_exit: int,
        expected_rows: dict[str, str],
    ) -> list[str]:
        problems: list[str] = []
        if not run.isolated_session:
            problems.append("census subprocess session was not verified private")
        if run.rc != expected_exit:
            problems.append(f"exit={run.rc} expected {expected_exit}")
        if run.fixture_timed_out:
            problems.append("fixture timeout rc 124 is FAIL, never SKIP")
        if run.leaked_before_cleanup:
            problems.append(
                "processes survived census completion before fixture cleanup: "
                + repr(run.leaked_before_cleanup)
            )
        if run.session_after_cleanup:
            problems.append(
                "census session remains after cleanup: "
                + repr(run.session_after_cleanup)
            )
        if expected_exit == 2:
            if run.stdout.strip():
                problems.append("protected refusal produced stdout")
            if "path-protected" not in run.stderr:
                problems.append("protected refusal lacks path-protected stderr")
            if rows_by_name(run.stdout):
                problems.append("protected refusal produced repository rows")
            return problems
        if expected_exit != 0:
            return problems
        if not run.stdout.startswith(HEADER + "\n"):
            problems.append("census header missing")
        rows = run.rows()
        if set(rows) != set(expected_rows):
            problems.append(
                f"row names={sorted(rows)} expected {sorted(expected_rows)}"
            )
        for name, kind in expected_rows.items():
            problems.extend(cls.expected_row_problems(rows.get(name), name, kind))
        return problems

    def clean_fifo_problems(self) -> list[str]:
        problems: list[str] = []
        for fifo in self.fifos:
            try:
                mode = fifo.stat().st_mode
            except OSError as exc:
                problems.append(f"FIFO missing/unstatable after case: {fifo}: {exc}")
                continue
            if not stat.S_ISFIFO(mode):
                problems.append(f"expected FIFO after injection: {fifo}")
                continue
            try:
                fd = os.open(str(fifo), os.O_WRONLY | os.O_NONBLOCK)
            except OSError as exc:
                if exc.errno != errno.ENXIO:  # No reader is the required result.
                    problems.append(f"FIFO writer probe for {fifo}: errno={exc.errno} {exc}")
                continue
            else:
                os.close(fd)
                problems.append(f"FIFO still has a reader: {fifo}")
        return problems

    def resource_problems(self) -> list[str]:
        problems: list[str] = []
        for run in self.runs:
            members = self.session_members(run.session_id)
            if members:
                problems.append(
                    f"{run.label}: census session still has processes: {members}"
                )
        problems.extend(self.clean_fifo_problems())
        return problems

    def case_resources(self, case_id: str) -> list[str]:
        return [f"{case_id}: {problem}" for problem in self.resource_problems()]

    def check_control(
        self,
        run: CensusRun,
        expected_rows: dict[str, str],
    ) -> list[str]:
        return self.census_problems(run, 0, expected_rows)

    def assert_neighbors_equal(
        self,
        control: CensusRun,
        injected: CensusRun,
        names: tuple[str, ...] = ("a", "c"),
    ) -> list[str]:
        problems: list[str] = []
        before, after = control.rows(), injected.rows()
        for name in names:
            if name not in before or name not in after:
                problems.append(f"{name}: missing from no-shim control or injected run")
            elif before[name] != after[name]:
                problems.append(
                    f"{name}: row differs from no-shim control: "
                    f"{before[name]!r} != {after[name]!r}"
                )
        return problems

    def add_fifo(self, path: Path) -> None:
        try:
            is_fifo = stat.S_ISFIFO(path.stat().st_mode)
        except OSError:
            return
        if is_fifo and path not in self.fifos:
            self.fifos.append(path)

    def write_shim_options(self) -> None:
        self.shim_log_path.write_text("", encoding="utf-8")
        marker = self.root / "shim-triggered"
        marker.unlink(missing_ok=True)

    def require_trigger(self, trigger: str, repo: Path) -> list[str]:
        records = []
        if self.shim_log_path.exists():
            for line in self.shim_log_path.read_text(encoding="utf-8", errors="replace").splitlines():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    return ["Git shim wrote malformed JSON log"]
        matched = [
            record for record in records
            if record.get("triggered") and record.get("command") == trigger
            and record.get("repo") == os.path.realpath(repo)
        ]
        if not matched:
            return [f"Git shim did not trigger on {trigger} in {repo}"]
        if any(record.get("trigger_error") for record in records):
            return [f"Git shim FIFO swap error: {records!r}"]
        return []

    def require_cmp_trigger(self, trigger: str, repo: Path) -> list[str]:
        records = CensusRun.trigger_log(self.cmp_log_path)
        expected_config = os.path.realpath(repo / ".git" / "config")
        matched = [
            record for record in records
            if record.get("triggered")
            and record.get("trigger") == trigger
            and record.get("candidate") == expected_config
        ]
        if not matched:
            return [f"cmp shim did not trigger on {expected_config}"]
        if any(record.get("trigger_error") for record in records):
            return [f"cmp shim FIFO swap error: {records!r}"]
        return []

    @staticmethod
    def require_timeout_diag(run: CensusRun, repo: Path, seconds: int) -> list[str]:
        expected = f"souji-census: repo-timeout {seconds}s {repo}"
        if expected not in run.stderr.splitlines():
            return [f"timeout diagnostic missing: {expected!r}"]
        return []

    def case_b1(self) -> CaseResult:
        problems: list[str] = []
        fleet, repos = self.fleet("b1-status-fifo")
        repo_b = repos["b"]
        self.touch_tracked(repo_b)
        control = self.census("B1-control", fleet)
        problems.extend(self.check_control(control, {"a": "clean", "b": "clean", "c": "clean"}))
        fifo = repo_b / ".git" / "info" / "attributes"
        self.install_git_shim()
        self.write_shim_options()
        injected = self.census(
            "B1",
            fleet,
            use_shim=True,
            trigger="status",
            target_repo=repo_b,
            fifo_path=fifo,
        )
        self.add_fifo(fifo)
        expected_rows = {"a": "clean", "b": "error", "c": "clean"}
        problems.extend(self.census_problems(injected, 0, expected_rows))
        problems.extend(self.assert_neighbors_equal(control, injected))
        problems.extend(self.require_trigger("status", repo_b))
        problems.extend(self.require_timeout_diag(injected, repo_b, DEFAULT_REPO_TIMEOUT))
        problems.extend(self.case_resources("B1"))
        return CaseResult(
            "B1", 0, expected_rows, problems, [control, injected],
            {
                "control_exit": 0,
                "control_rows": control.rows(),
                "injected_fifo": str(fifo),
                "shim_events": injected.trigger_log(self.shim_log_path),
            },
        )

    def case_b2(self) -> CaseResult:
        problems: list[str] = []
        fleet, repos = self.fleet("b2-check-attr-fifo")
        repo_b = repos["b"]
        self.add_bound_filter(repo_b)
        fifo = repo_b / ".git" / "info" / "attributes"
        control = self.census("B2-control", fleet)
        control_rows = {"a": "clean", "b": "status-unverifiable", "c": "clean"}
        problems.extend(self.check_control(control, control_rows))
        self.install_git_shim()
        self.write_shim_options()
        injected = self.census(
            "B2",
            fleet,
            use_shim=True,
            trigger="check-attr",
            target_repo=repo_b,
            fifo_path=fifo,
        )
        self.add_fifo(fifo)
        expected_rows = {"a": "clean", "b": "error", "c": "clean"}
        problems.extend(self.census_problems(injected, 0, expected_rows))
        problems.extend(self.assert_neighbors_equal(control, injected))
        problems.extend(self.require_trigger("check-attr", repo_b))
        problems.extend(self.require_timeout_diag(injected, repo_b, DEFAULT_REPO_TIMEOUT))
        problems.extend(self.case_resources("B2"))
        return CaseResult(
            "B2", 0, expected_rows, problems, [control, injected],
            {
                "control_exit": 0,
                "control_rows": control.rows(),
                "injected_fifo": str(fifo),
                "filter_driver": "filter.r18.clean=cat; kept.txt filter=r18",
                "shim_events": injected.trigger_log(self.shim_log_path),
            },
        )

    def case_b3(self) -> CaseResult:
        # The base census stats .git/config in guard_git_files, scans it in
        # guard_git_config, then later invokes `git status` in count_dirty.
        # Swapping config at that status invocation is therefore post-guard;
        # Git status reopens the config. The base run below must demonstrate
        # the blocked status path, not merely rely on a source-level guess.
        problems: list[str] = []
        fleet, repos = self.fleet("b3-config-fifo")
        repo_b = repos["b"]
        self.touch_tracked(repo_b)
        control = self.census("B3-control", fleet)
        problems.extend(self.check_control(control, {"a": "clean", "b": "clean", "c": "clean"}))
        fifo = repo_b / ".git" / "config"
        self.install_git_shim()
        self.write_shim_options()
        injected = self.census(
            "B3",
            fleet,
            use_shim=True,
            trigger="status",
            target_repo=repo_b,
            fifo_path=fifo,
        )
        self.add_fifo(fifo)
        expected_rows = {"a": "clean", "b": "error", "c": "clean"}
        problems.extend(self.census_problems(injected, 0, expected_rows))
        problems.extend(self.assert_neighbors_equal(control, injected))
        problems.extend(self.require_trigger("status", repo_b))
        problems.extend(self.require_timeout_diag(injected, repo_b, DEFAULT_REPO_TIMEOUT))
        problems.extend(self.case_resources("B3"))
        return CaseResult(
            "B3", 0, expected_rows, problems, [control, injected],
            {
                "control_exit": 0,
                "control_rows": control.rows(),
                "injected_fifo": str(fifo),
                "post_guard_status_hung": injected.fixture_timed_out,
                "shim_events": injected.trigger_log(self.shim_log_path),
            },
        )

    def case_b4(self) -> CaseResult:
        problems: list[str] = []
        ignore_fleet, ignore_repos = self.fleet("b4-worktree-ignore-fifo")
        ignore_b = ignore_repos["b"]
        control_ignore = self.census("B4-ignore-control", ignore_fleet)
        problems.extend(
            self.check_control(
                control_ignore, {"a": "clean", "b": "clean", "c": "clean"}
            )
        )
        ignore_fifo = ignore_b / ".gitignore"
        os.mkfifo(ignore_fifo)
        self.add_fifo(ignore_fifo)
        (ignore_b / "untracked-r18.txt").write_text("untracked\n", encoding="utf-8")
        self.touch_tracked(ignore_b)

        attr_fleet, attr_repos = self.fleet("b4-worktree-attributes-fifo")
        attr_b = attr_repos["b"]
        control_attrs = self.census("B4-attributes-control", attr_fleet)
        problems.extend(
            self.check_control(
                control_attrs, {"a": "clean", "b": "clean", "c": "clean"}
            )
        )
        attrs_fifo = attr_b / ".gitattributes"
        os.mkfifo(attrs_fifo)
        self.add_fifo(attrs_fifo)
        self.touch_tracked(attr_b)

        # Both static work-tree metadata FIFOs are independent read-side
        # falsifiers. Run concurrently so each retains the same 40s fixture
        # deadline without serially doubling the case duration.
        with ThreadPoolExecutor(max_workers=2) as pool:
            ignore_future = pool.submit(
                self.census, "B4-ignore", ignore_fleet, fifo_path=ignore_fifo
            )
            attrs_future = pool.submit(
                self.census, "B4-attributes", attr_fleet, fifo_path=attrs_fifo
            )
            measured_ignore = ignore_future.result()
            measured_attrs = attrs_future.result()

        expected_repo_rows = {"a": "clean", "b": "error", "c": "clean"}
        problems.extend(self.census_problems(measured_ignore, 0, expected_repo_rows))
        problems.extend(self.assert_neighbors_equal(control_ignore, measured_ignore))
        problems.extend(
            self.require_timeout_diag(measured_ignore, ignore_b, DEFAULT_REPO_TIMEOUT)
        )
        problems.extend(self.census_problems(measured_attrs, 0, expected_repo_rows))
        problems.extend(self.assert_neighbors_equal(control_attrs, measured_attrs))
        problems.extend(
            self.require_timeout_diag(measured_attrs, attr_b, DEFAULT_REPO_TIMEOUT)
        )
        if measured_ignore.fixture_timed_out:
            problems.append("base census hung on static .gitignore FIFO until rc 124")
        if measured_attrs.fixture_timed_out:
            problems.append("base census hung on static .gitattributes FIFO until rc 124")
        problems.extend(self.case_resources("B4"))
        expected_rows = {
            "ignore/a": "clean",
            "ignore/b": "error",
            "ignore/c": "clean",
            "attributes/a": "clean",
            "attributes/b": "error",
            "attributes/c": "clean",
        }
        return CaseResult(
            "B4",
            0,
            expected_rows,
            problems,
            [control_ignore, control_attrs, measured_ignore, measured_attrs],
            {
                "control_ignore_rows": control_ignore.rows(),
                "control_attributes_rows": control_attrs.rows(),
                "ignore_fifo": str(ignore_fifo),
                "attributes_fifo": str(attrs_fifo),
                "base_hangs_on_ignore_fifo": measured_ignore.fixture_timed_out,
                "base_hangs_on_attributes_fifo": measured_attrs.fixture_timed_out,
                "shim": "none",
            },
        )

    def case_b5(self) -> CaseResult:
        problems: list[str] = []
        fleet, _ = self.fleet("b5-slow-git", ("slow",))
        self.install_git_shim()
        self.write_shim_options()
        measured = self.census(
            "B5",
            fleet,
            repo_timeout=30,
            use_shim=True,
            # Match B5's measured two-second delay on every Git invocation.
            delay_seconds=2,
        )
        expected_rows = {"slow": "clean"}
        problems.extend(self.census_problems(measured, 0, expected_rows))
        records = measured.trigger_log(self.shim_log_path)
        delayed = [record for record in records if record.get("delayed")]
        if not delayed:
            problems.append("slow Git shim was not invoked")
        if len(delayed) != len(records):
            problems.append("not every Git shim call slept")
        if measured.elapsed >= 30:
            problems.append(f"slow repo elapsed {measured.elapsed:.2f}s, expected <30s")
        if measured.fixture_timed_out:
            problems.append("slow but finite repo was killed by fixture timeout")
        problems.extend(self.case_resources("B5"))
        return CaseResult(
            "B5", 0, expected_rows, problems, [measured],
            {
                "repo_timeout_seconds": 30,
                "shim_delay_seconds_per_call": 2,
                "git_calls": len(records),
                "elapsed_seconds": round(measured.elapsed, 3),
                "rows": measured.rows(),
            },
        )

    def case_b6(self) -> CaseResult:
        fleet, _ = self.fleet("b6-residue-check", ("residue",))
        run = self.census("B6-residue-census", fleet)
        expected_rows = {"residue": "clean"}
        problems = self.census_problems(run, 0, expected_rows)
        problems.extend(self.resource_problems())
        return CaseResult(
            "B6", 0, expected_rows, problems, [run],
            {
                "census_runs_checked": len(self.runs),
                "fifo_paths_checked": [str(path) for path in self.fifos],
                "fifo_probe": "O_WRONLY|O_NONBLOCK must fail with ENXIO",
            },
        )

    def case_b7(self) -> CaseResult:
        run = self.census("B7", self.agent_path)
        expected_rows: dict[str, str] = {}
        problems = self.census_problems(run, 2, expected_rows)
        problems.extend(self.case_resources("B7"))
        return CaseResult(
            "B7", 2, expected_rows, problems, [run],
            {"protected_root": str(self.agent_path), "rows": run.rows()},
        )

    def case_b8(self) -> CaseResult:
        problems: list[str] = []
        fleet, repos = self.fleet("b8-list-config-fifo")
        repo_b = repos["b"]
        control = self.census("B8-control", fleet)
        problems.extend(
            self.check_control(control, {"a": "clean", "b": "clean", "c": "clean"})
        )
        fifo = repo_b / ".git" / "config"
        self.install_cmp_shim()
        self.write_cmp_options()
        injected = self.census(
            "B8",
            fleet,
            use_cmp_shim=True,
            trigger="config-read",
            target_repo=repo_b,
            fifo_path=fifo,
        )
        self.add_fifo(fifo)
        expected_rows = {"a": "clean", "b": "error", "c": "clean"}
        problems.extend(self.census_problems(injected, 0, expected_rows))
        problems.extend(self.assert_neighbors_equal(control, injected))
        problems.extend(self.require_cmp_trigger("config-read", repo_b))
        problems.extend(self.require_timeout_diag(injected, repo_b, DEFAULT_REPO_TIMEOUT))
        problems.extend(self.case_resources("B8"))
        return CaseResult(
            "B8", 0, expected_rows, problems, [control, injected],
            {
                "control_exit": 0,
                "control_rows": control.rows(),
                "injected_fifo": str(fifo),
                "list_phase": "guard_git_config config-byte cmp after stat guard",
                "cmp_shim_events": CensusRun.trigger_log(self.cmp_log_path),
            },
        )


    def case_b9(self) -> CaseResult:
        fleet, repos = self.fleet("b9-term-ignoring-git", ("target",))
        repo = repos["target"]
        self.touch_tracked(repo)
        self.install_git_shim()
        self.write_shim_options()
        hang_marker = self.root / "b9-git.json"
        term_file = self.root / "b9-term.txt"
        started = time.monotonic()
        measured = self.census(
            "B9",
            fleet,
            repo_timeout=DEFAULT_REPO_TIMEOUT,
            use_shim=True,
            trigger="status",
            target_repo=repo,
            hang_mode="ignore-term",
            hang_pid_file=hang_marker,
            term_file=term_file,
        )
        finished = time.monotonic()
        expected_rows = {"target": "error"}
        problems = self.census_problems(measured, 0, expected_rows)
        problems.extend(self.require_trigger("status", repo))
        marker_record = {}
        try:
            marker_record = json.loads(hang_marker.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"Git hang marker missing or invalid: {exc}")
        term_to_kill_seconds = None
        if term_file.exists():
            try:
                term_at = float(term_file.read_text(encoding="ascii"))
                term_to_kill_seconds = finished - term_at
                if not 1.5 <= term_to_kill_seconds <= 4.0:
                    problems.append(
                        f"SIGTERM-to-SIGKILL grace={term_to_kill_seconds:.3f}s "
                        "expected about 2s"
                    )
            except (OSError, ValueError) as exc:
                problems.append(f"cannot read SIGTERM receipt: {exc}")
        else:
            problems.append("TERM-ignoring Git shim did not record SIGTERM")
        hang_started = marker_record.get("started")
        if hang_started is not None and term_file.exists():
            try:
                term_at = float(term_file.read_text(encoding="ascii"))
                to_term = term_at - float(hang_started)
                if not DEFAULT_REPO_TIMEOUT - 2 <= to_term <= DEFAULT_REPO_TIMEOUT + 3:
                    problems.append(
                        f"repo timeout before TERM={to_term:.3f}s "
                        f"expected near {DEFAULT_REPO_TIMEOUT}s"
                    )
            except (OSError, ValueError):
                pass
        worker_pid = marker_record.get("pid")
        snapshot = self.process_snapshot()
        if worker_pid is not None:
            worker = snapshot.get(int(worker_pid))
            if worker is not None and worker.get("session") == measured.session_id:
                problems.append(f"TERM-ignoring Git PID {worker_pid} survived watchdog")
        if finished - started >= FIXTURE_TIMEOUT:
            problems.append("TERM-ignoring repo reached the outer fixture deadline")
        problems.extend(self.case_resources("B9"))
        return CaseResult(
            "B9", 0, expected_rows, problems, [measured],
            {
                "repo_timeout_seconds": DEFAULT_REPO_TIMEOUT,
                "expected_term_grace_seconds": 2,
                "git_hang": marker_record,
                "term_to_kill_seconds": term_to_kill_seconds,
                "elapsed_seconds": round(finished - started, 3),
                "rows": measured.rows(),
            },
        )

    def case_b10(self) -> CaseResult:
        self.install_git_shim()
        problems: list[str] = []
        runs: list[CensusRun] = []
        observations: dict[str, dict] = {}
        for mode, signal_number in (
            ("TERM", signal.SIGTERM),
            ("KILL", signal.SIGKILL),
        ):
            fleet, repos = self.fleet(f"b10-parent-{mode.lower()}", ("target",))
            repo = repos["target"]
            self.touch_tracked(repo)
            self.write_shim_options()
            run, run_problems, notes = self.interrupt_census(
                f"B10-{mode}",
                fleet,
                repo,
                signal_number=signal_number,
            )
            problems.extend(run_problems)
            problems.extend(self.require_trigger("status", repo))
            if run.stdout.strip():
                problems.append(f"B10-{mode}: interrupted parent emitted a partial TSV")
            if run.rc != -signal_number:
                problems.append(
                    f"B10-{mode}: parent exit={run.rc}, expected {-signal_number}"
                )
            problems.extend(self.case_resources(f"B10-{mode}"))
            runs.append(run)
            observations[mode.lower()] = notes
        return CaseResult(
            "B10", None, {}, problems, runs,
            {
                "repo_timeout_seconds": DEFAULT_REPO_TIMEOUT,
                "parent_signals": ["SIGTERM", "SIGKILL"],
                "observations": observations,
            },
        )

    def case_b11(self) -> CaseResult:
        problems: list[str] = []
        sibling_root, _ = self.fleet("b11-root-prefix", ("sibling",))
        raw_root = Path(str(sibling_root) + "\n")
        root_run = self.census("B11-root-newline", raw_root)
        problems.extend(self.census_problems(root_run, 2, {}))

        compare_root, _ = self.fleet("b11-compare-current", ("compare-target",))
        compare_prefix = self.root / "b11-compare-prefix.tsv"
        compare_prefix.write_text(HEADER + "\n", encoding="utf-8")
        raw_compare = Path(str(compare_prefix) + "\n")
        compare_run = self.census(
            "B11-compare-newline",
            compare_root,
            compare_path=raw_compare,
        )
        problems.extend(self.census_problems(compare_run, 2, {}))
        problems.extend(self.case_resources("B11"))
        return CaseResult(
            "B11", 2, {}, problems, [root_run, compare_run],
            {
                "root_input_with_trailing_newline": str(raw_root),
                "root_sibling_that_must_not_be_selected": str(sibling_root),
                "compare_input_with_trailing_newline": str(raw_compare),
                "compare_sibling_that_must_not_be_selected": str(compare_prefix),
                "sibling_baseline": HEADER,
            },
        )

    def case_b12(self) -> CaseResult:
        problems: list[str] = []
        fleet = self.root / "b12-linked-gitfile"
        fleet.mkdir()
        repo_a = self.init_repo(fleet / "a")
        repo_c = self.init_repo(fleet / "c")
        # The owner is deliberately hidden from the top-level census, while
        # b remains a real registered worktree with a regular .git gitfile.
        owner = self.init_repo(fleet / ".owner" / "repo-owner")
        linked_b = fleet / "b"
        self.git(owner, "worktree", "add", "--detach", str(linked_b))
        gitfile = linked_b / ".git"
        (fleet / "plain").mkdir()

        control = self.census("B12-gitfile-control", fleet)
        control_rows = {"a": "clean", "c": "clean"}
        problems.extend(self.check_control(control, control_rows))
        self.install_cmp_shim()
        self.write_cmp_options()
        injected = self.census(
            "B12-gitfile",
            fleet,
            use_cmp_shim=True,
            trigger="config-read",
            target_repo=repo_a,
            fifo_path=gitfile,
        )
        self.add_fifo(gitfile)
        gitfile_rows = {"a": "clean", "b": "error", "c": "clean"}
        problems.extend(self.census_problems(injected, 0, gitfile_rows))
        problems.extend(self.assert_neighbors_equal(control, injected))
        problems.extend(self.require_cmp_trigger("config-read", repo_a))
        problems.extend(self.require_timeout_diag(injected, linked_b, DEFAULT_REPO_TIMEOUT))
        actual_gitfile_names = raw_repo_names(injected.stdout)
        if len(actual_gitfile_names) != len(set(actual_gitfile_names)):
            problems.append(f"gitfile preflight emitted duplicate rows: {actual_gitfile_names}")
        if set(actual_gitfile_names) != set(gitfile_rows):
            problems.append(
                f"gitfile preflight rows={actual_gitfile_names}, expected exactly "
                f"{sorted(gitfile_rows)}"
            )
        gitfile_events = CensusRun.trigger_log(self.cmp_log_path)

        included_root = self.init_repo(self.root / "b12-include-root")
        control_included = self.census(
            "B12-include-control", included_root, include_root=True
        )
        included_name = included_root.name
        problems.extend(
            self.check_control(control_included, {included_name: "clean"})
        )
        config_fifo = included_root / ".git" / "config"
        self.install_cmp_shim()
        self.write_cmp_options()
        injected_included = self.census(
            "B12-include-root",
            included_root,
            include_root=True,
            use_cmp_shim=True,
            trigger="config-read",
            target_repo=included_root,
            fifo_path=config_fifo,
        )
        self.add_fifo(config_fifo)
        included_rows = {included_name: "error"}
        problems.extend(self.census_problems(injected_included, 0, included_rows))
        problems.extend(
            self.require_cmp_trigger("config-read", included_root)
        )
        problems.extend(
            self.require_timeout_diag(
                injected_included, included_root, DEFAULT_REPO_TIMEOUT
            )
        )
        actual_included_names = raw_repo_names(injected_included.stdout)
        if actual_included_names != [included_name]:
            problems.append(
                "included repo timeout must produce exactly one row, got "
                f"{actual_included_names}"
            )
        problems.extend(self.case_resources("B12"))
        expected_rows = {
            "gitfile/a": "clean",
            "gitfile/b": "error",
            "gitfile/c": "clean",
            f"include-root/{included_name}": "error",
        }
        return CaseResult(
            "B12", 0, expected_rows, problems,
            [control, injected, control_included, injected_included],
            {
                "gitfile": str(gitfile),
                "gitfile_fleet_control_rows": control.rows(),
                "gitfile_timeout_rows": injected.rows(),
                "gitfile_cmp_events": gitfile_events,
                "plain_candidate": str(fleet / "plain"),
                "included_root": str(included_root),
                "included_root_timeout_rows": injected_included.rows(),
                "included_root_cmp_events": CensusRun.trigger_log(self.cmp_log_path),
            },
        )
    def cases(self, selected: tuple[str, ...]) -> list[CaseResult]:
        case_functions = {
            "B1": self.case_b1,
            "B2": self.case_b2,
            "B3": self.case_b3,
            "B4": self.case_b4,
            "B5": self.case_b5,
            "B6": self.case_b6,
            "B7": self.case_b7,
            "B8": self.case_b8,
            "B9": self.case_b9,
            "B10": self.case_b10,
            "B11": self.case_b11,
            "B12": self.case_b12,
        }
        return [case_functions[case_id]() for case_id in selected]

    @staticmethod
    def row_labels(rows: dict[str, list[str]]) -> dict[str, str]:
        labels = {}
        for name, fields in rows.items():
            labels[name] = fields[6] if len(fields) == 7 else f"columns={len(fields)}"
        return labels

    def serialize_case(self, result: CaseResult) -> dict:
        return {
            "id": result.case_id,
            "status": "pass" if not result.problems else "fail",
            "expected_exit": result.expected_exit,
            "expected_rows": result.expected_rows,
            "problems": result.problems,
            "notes": result.notes,
            "runs": [
                {
                    "label": run.label,
                    "exit": run.rc,
                    "fixture_timed_out": run.fixture_timed_out,
                    "isolated_session": run.isolated_session,
                    "elapsed_seconds": round(run.elapsed, 3),
                    "rows": run.rows(),
                    "stderr": run.stderr.splitlines(),
                    "session_id": run.session_id,
                    "leaked_before_cleanup": run.leaked_before_cleanup,
                    "session_after_cleanup": run.session_after_cleanup,
                    "argv": run.argv,
                }
                for run in result.runs
            ],
        }

    def run_all(self, json_output: bool, selected: tuple[str, ...]) -> int:
        digest = hashlib.sha256(self.tool.read_bytes()).hexdigest()
        print(f"TOOL\t{self.tool}\tsha256={digest}", flush=True)
        self.case_results = self.cases(selected)
        failed = 0
        for result in self.case_results:
            status = "PASS" if not result.problems else "FAIL"
            if result.problems:
                failed += 1
            actual_runs = result.runs
            observed_exit = actual_runs[-1].rc if actual_runs else "none"
            row_state = (
                self.row_labels(actual_runs[-1].rows()) if actual_runs else {}
            )
            detail = {
                "expected_exit": result.expected_exit,
                "observed_exit": observed_exit,
                "expected_rows": result.expected_rows,
                "observed_rows": row_state,
                "problems": result.problems,
            }
            print(
                f"CASE\t{result.case_id}\t{status}\t"
                + json.dumps(detail, sort_keys=True, separators=(",", ":")),
                flush=True,
            )
        if tuple(result.case_id for result in self.case_results) != selected:
            failed += 1
            print("CASE\tid-set\tFAIL\tfixture cases differ from selected ids", flush=True)
        print(f"SUMMARY\ttotal={len(self.case_results)}\tfailed={failed}", flush=True)
        if json_output:
            print(
                "JSON\t"
                + json.dumps(
                    {
                        "fixture": "r18-census-bounded",
                        "expected_ids": list(EXPECTED_IDS),
                        "selected_ids": list(selected),
                        "fixture_timeout_seconds": FIXTURE_TIMEOUT,
                        "default_repo_timeout_seconds": DEFAULT_REPO_TIMEOUT,
                        "tool": {"path": str(self.tool), "sha256": digest},
                        "cases": [self.serialize_case(case) for case in self.case_results],
                        "summary": {"total": len(self.case_results), "failed": failed},
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
        return 0 if failed == 0 else 1

    def cleanup(self) -> None:
        # Only census sessions created by this fixture are ever signalled.
        for run in self.runs:
            members = self.session_members(run.session_id)
            if run.isolated_session and members:
                self.kill_session(run.session_id, members)
                self.wait_session_empty(run.session_id)
        if self.scratch is not None and self.scratch.exists():
            shutil.rmtree(self.scratch)


def raw_repo_names(stdout: str) -> list[str]:
    lines = stdout.splitlines()
    if not lines or lines[0] != HEADER:
        return []
    names = []
    for line in lines[1:]:
        if line:
            names.append(Path(line.split("\t", 1)[0]).name)
    return names

def rows_by_name(stdout: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    lines = stdout.splitlines()
    if not lines or lines[0] != HEADER:
        return rows
    for line in lines[1:]:
        if not line:
            continue
        fields = line.split("\t")
        if len(fields) == 7:
            rows[Path(fields[0]).name] = fields
    return rows


def die(message: str) -> None:
    print(f"r18-census-bounded: {message}", file=sys.stderr)
    raise SystemExit(2)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="r18-census-bounded.py",
        description="Round-18 C1 bounded-repository watchdog falsifier",
    )
    parser.add_argument(
        "--census",
        help="census tool under test (default: lane tools/souji-census.sh)",
    )
    parser.add_argument("--list", action="store_true", help="print stable case ids and exit")
    parser.add_argument("--json", action="store_true", help="emit one JSON record after the summary")
    parser.add_argument(
        "--case",
        action="append",
        choices=EXPECTED_IDS,
        metavar="ID",
        help="run selected cases for debugging (repeatable)",
    )
    args = parser.parse_args(argv)
    if args.list:
        print("\n".join(EXPECTED_IDS))
        return 0
    selected = tuple(args.case) if args.case else EXPECTED_IDS
    if len(set(selected)) != len(selected):
        die("--case ids must not repeat")
    tool = (
        Path(args.census)
        if args.census
        else Path(__file__).resolve().parents[2] / "tools" / "souji-census.sh"
    )
    fixture = Fixture(tool)
    try:
        fixture.setup()
        return fixture.run_all(args.json, selected)
    finally:
        fixture.cleanup()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
