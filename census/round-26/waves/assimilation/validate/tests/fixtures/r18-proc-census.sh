#!/usr/bin/env bash
# r18-proc-census.sh — C3 process-residue census fixture.
#
# Cases:
#   P1 deleted-cwd FIFO reader -> cwd-deleted, with FIFO-ish wchan recorded
#   P2 live-cwd process with a deleted /var/tmp argv path -> argv-path-gone
#   P3 live control -> absent
#   P4 --prefix selects P2 and excludes P6
#   P5 --min-age excludes fresh residue workers
#   P6 secret-shaped password argv is redacted
#   P7 strace observes no kill/tkill/tgkill/pidfd_send_signal syscall
#   P8 invalid usage exits 2
#   P9 clean-argv worker with stdout on a deleted fd path
#   P10 deleted /var/tmp/<top>/sub while <top> lives -> absent
#   P11 starttime equals /proc/<pid>/stat field 22
#   P12 live cwd literally ending in ` (deleted)` -> absent
#   P13 live fd literally ending in ` (deleted)` -> absent
#   P14/P15/P16 fake Bearer/AWS/Slack secrets are redacted
#   P17 similarly prefixed sibling root does not match --prefix
#   P18 cwd > argv > fd precedence
#   P19 argv > fd precedence
#
# Census output is a `# boot_id <id>` comment, then the 10-column TSV header;
# the fixture maps rows by the header names.
# The orphan workers and every census invocation start in private process
# groups. A timed-out census invocation has its entire group SIGKILLed; cleanup
# likewise kills only groups created by this fixture. All fixture state is
# confined to /var/tmp and removed by the EXIT trap.
#
# Usage: r18-proc-census.sh [--tool PATH]
#   --tool PATH  census executable/script under test (default tools/ in lane)
#
# Output: one CASE<TAB>Pn<TAB>PASS|FAIL<TAB>detail line per case, followed by
# SUMMARY. Exit 0 when every case passes, 1 on assertion failure, 2 on setup or
# usage failure.
set -euo pipefail
export LC_ALL=C

FIXTURE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
LANE_ROOT="$(cd -- "$FIXTURE_DIR/../.." && pwd -P)"
TOOL="${SOUJI_PROC_CENSUS_BIN:-$LANE_ROOT/tools/souji-proc-census.sh}"

usage() {
  printf 'usage: %s [--tool PATH]\n' "${0##*/}" >&2
  exit 2
}

while (($#)); do
  case "$1" in
    --tool)
      (($# >= 2)) || usage
      TOOL=$2
      shift 2
      ;;
    --tool=*)
      TOOL=${1#*=}
      shift
      ;;
    -h|--help)
      usage
      ;;
    *)
      usage
      ;;
  esac
done

[[ -n $TOOL && -r $TOOL ]] || {
  printf 'r18-proc-census: tool not readable: %s\n' "$TOOL" >&2
  exit 2
}

SCRATCH="$(mktemp -d /var/tmp/souji-r18-proc-census.XXXXXX)" || {
  printf 'r18-proc-census: cannot create scratch under /var/tmp\n' >&2
  exit 2
}
case "$SCRATCH" in
  /var/tmp/souji-r18-proc-census.*) ;;
  *) printf 'r18-proc-census: unsafe scratch path: %s\n' "$SCRATCH" >&2; exit 2 ;;
esac
trap 'rm -rf -- "$SCRATCH"' EXIT

python3 - "$TOOL" "$SCRATCH" <<'PY'
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HEADER_COLUMNS = (
    "pid", "ppid", "pgid", "sid", "age_s", "starttime",
    "state", "wchan", "reason", "cmd",
)
HEADER = "\t".join(HEADER_COLUMNS)
COLUMNS = len(HEADER_COLUMNS)
TOOL_TIMEOUT = 12
FRESH_LIMIT = 60
FIFO_WCHAN = re.compile(r"(?:fifo|pipe|partner|wait)", re.IGNORECASE)
REDACTION = re.compile(r"(?:redact(?:ed|ion)?|\*{3,})", re.IGNORECASE)
SIGNAL_SYSCALL = re.compile(r"\b(?:kill|tkill|tgkill|pidfd_send_signal)\s*\(")
CANARY = "R18_SYNTHETIC_PASSWORD_CANARY_NOT_A_CREDENTIAL"
BEARER_CANARY = "R18_FAKE_BEARER_NOT_A_CREDENTIAL"
AWS_CANARY = "AKIA0000000000000000"
SLACK_CANARY = "xoxb-r18-fake-not-a-token"
STRACE_BIN = shutil.which("strace")
CHILDREN = []
EXTRA_DIRS = []
FAILURES = 0


class SetupError(Exception):
    pass


def emit(case_id, passed, detail):
    global FAILURES
    status = "PASS" if passed else "FAIL"
    if not passed:
        FAILURES += 1
    print("CASE\t{}\t{}\t{}".format(case_id, status, detail))


def spawn_worker(argv, cwd, stdout=subprocess.DEVNULL):
    proc = subprocess.Popen(
        argv,
        cwd=str(cwd),
        stdin=subprocess.DEVNULL,
        stdout=stdout,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    CHILDREN.append(proc)
    return proc


def read_wchan(pid):
    try:
        return Path("/proc/{}/wchan".format(pid)).read_text(encoding="ascii").strip()
    except (OSError, UnicodeError):
        return ""


def wait_for_fifo_block(proc, seconds=8):
    deadline = time.monotonic() + seconds
    seen = ""
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise SetupError("FIFO worker exited before blocking")
        seen = read_wchan(proc.pid)
        if FIFO_WCHAN.search(seen):
            return seen
        time.sleep(0.02)
    raise SetupError("FIFO reader did not expose a FIFO-ish wchan (observed {!r})".format(seen))


def make_deleted_path(root, name):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("fixture-only deleted target\n", encoding="utf-8")
    path.unlink()
    return str(path)

def make_gone_root(label, name):
    root = Path(tempfile.mkdtemp(prefix="souji-r18-proc-argv-{}.".format(label), dir="/var/tmp"))
    EXTRA_DIRS.append(root)
    return root, make_deleted_path(root / "sub", name)


def spawn_deleted_stdout(argv, cwd, label):
    root = Path(tempfile.mkdtemp(prefix="souji-r18-proc-fd-{}.".format(label), dir="/var/tmp"))
    EXTRA_DIRS.append(root)
    path = root / "stdout"
    path.touch()
    with path.open("wb") as stream:
        proc = spawn_worker(argv, cwd, stdout=stream)
    path.unlink()
    root.rmdir()
    try:
        link = os.readlink("/proc/{}/fd/1".format(proc.pid))
    except OSError as exc:
        raise SetupError("could not verify deleted stdout fd: {}".format(exc))
    if not link.endswith(" (deleted)"):
        raise SetupError("stdout fd target was not deleted")
    return proc, str(path)


def inode_matches(left, right):
    try:
        left_stat = os.stat(left)
        right_stat = os.stat(right)
    except OSError:
        return False
    return left_stat.st_dev == right_stat.st_dev and left_stat.st_ino == right_stat.st_ino

def signal_syscalls(trace_path):
    try:
        lines = trace_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    return [line for line in lines if SIGNAL_SYSCALL.search(line)]


def result_context(result, parse_error):
    stderr = result["err"].strip().replace("\n", "\\n")[:160]
    return "rc={} timed_out={} table={} stderr={!r}".format(
        result["rc"], result["timed_out"], parse_error, stderr
    )


def command_for(tool, args):
    if os.access(tool, os.X_OK):
        return [tool] + list(args)
    return ["bash", tool] + list(args)


def run_tool(tool, args, trace_path=None):
    command = command_for(tool, args)
    if trace_path is not None:
        command = [
            STRACE_BIN,
            "-f",
            "-qq",
            "-e",
            "trace=kill,tkill,tgkill,pidfd_send_signal",
            "-o",
            str(trace_path),
            "--",
        ] + command
    try:
        proc = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            start_new_session=True,
        )
    except OSError as exc:
        return {"rc": 127, "out": "", "err": str(exc), "timed_out": False}
    try:
        out, err = proc.communicate(timeout=TOOL_TIMEOUT)
        return {"rc": proc.returncode, "out": out, "err": err, "timed_out": False}
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = proc.communicate()
        return {"rc": 124, "out": out, "err": err, "timed_out": True}


def parse_table(out, expected_boot_id):
    lines = out.splitlines()
    if len(lines) < 2 or lines[0] != "# boot_id " + expected_boot_id:
        return None, "boot_id comment mismatch"
    columns = lines[1].split("\t")
    if columns != list(HEADER_COLUMNS):
        return None, "header mismatch"
    rows = {}
    for line in lines[2:]:
        fields = line.split("\t", len(columns) - 1)
        if len(fields) != len(columns):
            return None, "malformed row"
        row = dict(zip(columns, fields))
        try:
            pid = int(row["pid"])
        except ValueError:
            return None, "non-numeric pid"
        if pid in rows:
            return None, "duplicate pid {}".format(pid)
        rows[pid] = row
    return rows, "ok"


def process_starttime(pid):
    try:
        stat_line = Path("/proc/{}/stat".format(pid)).read_text(encoding="ascii")
        close = stat_line.rfind(") ")
        if close < 0:
            return None
        fields = stat_line[close + 2:].split()
        return int(fields[19]) if len(fields) > 19 else None
    except (OSError, UnicodeError, ValueError):
        return None


def complete_record(row):
    if row is None:
        return False
    try:
        int(row["ppid"])
        int(row["pgid"])
        int(row["sid"])
        float(row["age_s"])
        int(row["starttime"])
    except ValueError:
        return False
    return all(row[key] for key in ("state", "wchan", "reason", "cmd"))


def redacted_argv_row(row, path, secret):
    if row is None:
        return False
    command = row["cmd"]
    return (
        complete_record(row)
        and row["reason"] == "argv-path-gone:" + path
        and secret not in command
        and bool(REDACTION.search(command))
    )

def base_ok(result, rows):
    return result["rc"] == 0 and rows is not None and not result["timed_out"]


def proc_alive(proc):
    if proc.poll() is not None:
        return False
    try:
        os.kill(proc.pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return False
    return True


def cleanup_children():
    for proc in reversed(CHILDREN):
        if proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()

    for extra_dir in EXTRA_DIRS:
        shutil.rmtree(extra_dir, ignore_errors=True)


def run():
    if len(sys.argv) != 3:
        raise SetupError("internal argument count")
    tool = os.path.abspath(sys.argv[1])
    scratch = Path(sys.argv[2]).resolve()
    if not os.path.isfile(tool):
        raise SetupError("tool is not a file")
    if not str(scratch).startswith("/var/tmp/souji-r18-proc-census."):
        raise SetupError("scratch escaped the private /var/tmp root")

    try:
        boot_id = Path("/proc/sys/kernel/random/boot_id").read_text(encoding="ascii").strip()
    except (OSError, UnicodeError) as exc:
        raise SetupError("could not read kernel boot_id: {}".format(exc))
    if not boot_id:
        raise SetupError("kernel boot_id is empty")
    if STRACE_BIN is None:
        raise SetupError("strace not found; P7 requires syscall tracing")

    live = scratch / "live"
    live.mkdir()
    p1_cwd = scratch / "deleted-cwd"
    p1_cwd.mkdir()
    os.mkfifo(p1_cwd / "reader")

    fifo_code = 'import os,time; os.open("reader", os.O_RDONLY); time.sleep(300)'
    p1 = spawn_worker([sys.executable, "-c", fifo_code], p1_cwd)
    fifo_wchan = wait_for_fifo_block(p1)
    shutil.rmtree(p1_cwd)
    try:
        p1_cwd_link = os.readlink("/proc/{}/cwd".format(p1.pid))
    except OSError as exc:
        raise SetupError("could not verify deleted FIFO cwd: {}".format(exc))
    if not p1_cwd_link.endswith(" (deleted)"):
        raise SetupError("FIFO worker cwd was not deleted")

    sleeper_code = "import time; time.sleep(300)"
    p2_prefix, p2_path = make_gone_root("argv-p2", "gone-argv-p2")
    p2 = spawn_worker([sys.executable, "-c", sleeper_code, p2_path], live)
    p3 = spawn_worker([sys.executable, "-c", sleeper_code], live)

    p6_prefix, p6_path = make_gone_root("argv-p6", "gone-argv-p6")
    p6 = spawn_worker(
        [sys.executable, "-c", sleeper_code, "--workspace=" + p6_path, "--password=" + CANARY],
        live,
    )
    shutil.rmtree(p2_prefix)
    shutil.rmtree(p6_prefix)

    boundary_sub = scratch / "sub"
    boundary_sub.mkdir()
    p10_path = str(boundary_sub)
    p10 = spawn_worker([sys.executable, "-c", sleeper_code, p10_path], live)
    shutil.rmtree(boundary_sub)

    p9, fd_path = spawn_deleted_stdout(
        [sys.executable, "-c", sleeper_code], live, "p9"
    )

    p12_path = scratch / "literal-cwd" / "x (deleted)"
    p12_path.mkdir(parents=True)
    p12 = spawn_worker([sys.executable, "-c", sleeper_code], p12_path)
    try:
        p12_cwd_link = os.readlink("/proc/{}/cwd".format(p12.pid))
    except OSError as exc:
        raise SetupError("could not verify live literal cwd: {}".format(exc))
    if p12_cwd_link != str(p12_path) or not inode_matches(
        "/proc/{}/cwd".format(p12.pid), p12_path
    ):
        raise SetupError("literal cwd suffix was not a live inode match")

    p13_dir = scratch / "fd-literal" / "top"
    p13_dir.mkdir(parents=True)
    p13_path = p13_dir / "x (deleted)"
    p13_path.touch()
    with p13_path.open("wb") as p13_stream:
        p13 = spawn_worker([sys.executable, "-c", sleeper_code], live, stdout=p13_stream)
    if not inode_matches("/proc/{}/fd/1".format(p13.pid), p13_path):
        raise SetupError("literal fd suffix was not a live inode match")

    bearer_prefix, bearer_path = make_gone_root("redact-bearer", "gone-bearer")
    p14 = spawn_worker(
        [
            sys.executable, "-c", sleeper_code, "-H", "Authorization:", "Bearer",
            BEARER_CANARY, "--workspace=" + bearer_path,
        ],
        live,
    )
    shutil.rmtree(bearer_prefix)

    aws_prefix, aws_path = make_gone_root("redact-aws", "gone-aws")
    p15 = spawn_worker(
        [sys.executable, "-c", sleeper_code, AWS_CANARY, "--workspace=" + aws_path],
        live,
    )
    shutil.rmtree(aws_prefix)

    slack_prefix, slack_path = make_gone_root("redact-slack", "gone-slack")
    p16 = spawn_worker(
        [sys.executable, "-c", sleeper_code, SLACK_CANARY, "--workspace=" + slack_path],
        live,
    )
    shutil.rmtree(slack_prefix)

    prefix_root = scratch / "prefix-boundary"
    prefix_root.mkdir()
    sibling_root = Path(str(prefix_root) + "-sibling")
    p17_path = make_deleted_path(sibling_root / "sub", "gone-sibling")
    p17 = spawn_worker(
        [sys.executable, "-c", sleeper_code, "--workspace=" + p17_path], live
    )
    shutil.rmtree(sibling_root)

    mixed_cwd = scratch / "mixed-precedence-cwd"
    mixed_cwd.mkdir()
    p18_prefix, p18_path = make_gone_root("precedence-all", "gone-precedence-all")
    p18, p18_fd_path = spawn_deleted_stdout(
        [sys.executable, "-c", sleeper_code, "--workspace=" + p18_path],
        mixed_cwd,
        "precedence-all",
    )
    shutil.rmtree(mixed_cwd)
    try:
        p18_cwd_link = os.readlink("/proc/{}/cwd".format(p18.pid))
    except OSError as exc:
        raise SetupError("could not verify mixed-precedence deleted cwd: {}".format(exc))
    if not p18_cwd_link.endswith(" (deleted)"):
        raise SetupError("mixed-precedence cwd was not deleted")
    shutil.rmtree(p18_prefix)

    p19_prefix, p19_path = make_gone_root("precedence-argv", "gone-precedence-argv")
    p19, p19_fd_path = spawn_deleted_stdout(
        [sys.executable, "-c", sleeper_code, "--workspace=" + p19_path],
        live,
        "precedence-argv",
    )
    shutil.rmtree(p19_prefix)

    fixture_workers = (
        p1, p2, p3, p6, p9, p10, p12, p13, p14, p15, p16, p17, p18, p19,
    )
    for proc in fixture_workers:
        if proc.poll() is not None:
            raise SetupError("fixture worker exited during setup")
    if not os.path.isdir("/proc/{}/cwd".format(p2.pid)):
        raise SetupError("argv worker proc entry disappeared")
    if not os.path.isdir(live) or not scratch.is_dir() or not prefix_root.is_dir():
        raise SetupError("live control or prefix boundary directory disappeared")

    default = run_tool(tool, [])
    rows, table_error = parse_table(default["out"], boot_id)
    usable = base_ok(default, rows)

    p1_row = rows.get(p1.pid) if rows is not None else None
    p1_age_ok = False
    if p1_row is not None:
        try:
            age = float(p1_row["age_s"])
            p1_age_ok = 0 <= age < FRESH_LIMIT
        except ValueError:
            pass
    p1_wchan = p1_row["wchan"] if p1_row else ""
    p1_ok = (
        usable
        and complete_record(p1_row)
        and p1_row["reason"] == "cwd-deleted"
        and int(p1_row["pgid"]) == p1.pid
        and int(p1_row["sid"]) == p1.pid
        and bool(p1_wchan)
        and bool(FIFO_WCHAN.search(p1_wchan))
        and p1_age_ok
    )
    emit(
        "P1",
        p1_ok,
        "cwd-deleted wchan={!r} setup-wchan={!r}".format(p1_wchan, fifo_wchan)
        if p1_row
        else "missing FIFO reader row ({})".format(table_error),
    )

    p2_row = rows.get(p2.pid) if rows is not None else None
    p2_ok = (
        usable
        and complete_record(p2_row)
        and p2_row["reason"] == "argv-path-gone:" + p2_path
        and int(p2_row["pgid"]) == p2.pid
        and int(p2_row["sid"]) == p2.pid
    )
    emit(
        "P2",
        p2_ok,
        "argv-path-gone row present" if p2_ok else "missing or wrong argv-path-gone row",
    )

    p3_ok = usable and p3.pid not in rows
    emit("P3", p3_ok, "live control absent" if p3_ok else "live control listed or census unusable")

    prefix = run_tool(tool, ["--prefix", str(p2_prefix)])
    prefix_rows, prefix_error = parse_table(prefix["out"], boot_id)
    prefix_ok = (
        prefix["rc"] == 0
        and not prefix["timed_out"]
        and prefix_rows is not None
        and p2.pid in prefix_rows
        and p6.pid not in prefix_rows
    )
    emit(
        "P4",
        prefix_ok,
        "prefix retained P2 and excluded P6"
        if prefix_ok
        else "--prefix did not select P2/exclude P6 ({})".format(
            result_context(prefix, prefix_error)
        ),
    )

    aged = run_tool(tool, ["--min-age", str(FRESH_LIMIT)])
    aged_rows, aged_error = parse_table(aged["out"], boot_id)
    fresh_pids = (
        p1.pid, p2.pid, p6.pid, p9.pid, p14.pid, p15.pid, p16.pid, p17.pid,
        p18.pid, p19.pid,
    )
    aged_ok = (
        aged["rc"] == 0
        and not aged["timed_out"]
        and aged_rows is not None
        and all(pid not in aged_rows for pid in fresh_pids)
    )
    emit(
        "P5",
        aged_ok,
        "fresh residue workers excluded"
        if aged_ok
        else "--min-age retained a fresh worker ({})".format(aged_error),
    )

    p6_row = rows.get(p6.pid) if rows is not None else None
    p6_ok = usable and redacted_argv_row(p6_row, p6_path, CANARY)
    emit(
        "P6",
        p6_ok,
        "password argv redacted" if p6_ok else "missing P6 row or secret not redacted",
    )

    signal_trace_path = scratch / "signal-syscalls.trace"
    signal_trace_path.touch()
    traced = run_tool(tool, [], trace_path=signal_trace_path)
    traced_rows, traced_error = parse_table(traced["out"], boot_id)
    observed_signals = signal_syscalls(signal_trace_path)
    workers_alive = all(proc_alive(proc) for proc in fixture_workers)
    p7_ok = (
        base_ok(traced, traced_rows)
        and observed_signals == []
        and workers_alive
    )
    if observed_signals is None:
        p7_detail = "strace output unreadable"
    elif observed_signals:
        p7_detail = "strace observed signal syscall: {}".format(observed_signals[0])
    elif not workers_alive:
        p7_detail = "fixture worker exited during traced census"
    elif not base_ok(traced, traced_rows):
        p7_detail = "traced census failed ({})".format(result_context(traced, traced_error))
    else:
        p7_detail = "strace observed no signal syscalls; fixture workers alive"
    emit("P7", p7_ok, p7_detail)

    bad = run_tool(tool, ["--r18-invalid-option"])
    p8_ok = bad["rc"] == 2 and not bad["timed_out"]
    emit("P8", p8_ok, "invalid usage exited 2" if p8_ok else "bad usage rc={}".format(bad["rc"]))

    p9_row = rows.get(p9.pid) if rows is not None else None
    expected_fd_reason = "fd-path-gone:" + str(fd_path)
    p9_reason = p9_row["reason"] if p9_row else ""
    p9_ok = (
        usable
        and complete_record(p9_row)
        and p9_reason in (expected_fd_reason, expected_fd_reason + " (deleted)")
        and os.path.isdir("/proc/{}/cwd".format(p9.pid))
    )
    emit("P9", p9_ok, "deleted stdout fd reported" if p9_ok else "missing or wrong fd-path-gone row")

    p10_ok = usable and p10.pid not in rows and scratch.is_dir()
    emit("P10", p10_ok, "deleted nested boundary omitted" if p10_ok else "nested boundary was listed")

    expected_starttime = process_starttime(p2.pid)
    try:
        reported_starttime = int(p2_row["starttime"]) if p2_row else None
    except ValueError:
        reported_starttime = None
    p11_ok = (
        usable
        and expected_starttime is not None
        and reported_starttime == expected_starttime
    )
    emit(
        "P11",
        p11_ok,
        "starttime matches /proc field 22"
        if p11_ok
        else "starttime mismatch reported={!r} stat={!r}".format(reported_starttime, expected_starttime),
    )


    p12_ok = (
        usable
        and p12.pid not in rows
        and inode_matches("/proc/{}/cwd".format(p12.pid), p12_path)
    )
    emit("P12", p12_ok, "live literal cwd suffix omitted" if p12_ok else "live literal cwd suffix listed")

    p13_result = run_tool(tool, ["--prefix", str(p13_dir)])
    p13_rows, p13_error = parse_table(p13_result["out"], boot_id)
    p13_ok = (
        p13_result["rc"] == 0
        and not p13_result["timed_out"]
        and p13_rows is not None
        and p13.pid not in p13_rows
        and inode_matches("/proc/{}/fd/1".format(p13.pid), p13_path)
    )
    emit(
        "P13",
        p13_ok,
        "live literal fd suffix omitted"
        if p13_ok
        else "literal fd listed or custom-prefix census failed ({})".format(
            result_context(p13_result, p13_error)
        ),
    )

    p14_row = rows.get(p14.pid) if rows is not None else None
    p14_ok = usable and redacted_argv_row(p14_row, bearer_path, BEARER_CANARY)
    emit("P14", p14_ok, "Authorization Bearer argv redacted" if p14_ok else "Bearer value not redacted")

    p15_row = rows.get(p15.pid) if rows is not None else None
    p15_ok = usable and redacted_argv_row(p15_row, aws_path, AWS_CANARY)
    emit("P15", p15_ok, "AWS-shaped argv redacted" if p15_ok else "AWS-shaped value not redacted")

    p16_row = rows.get(p16.pid) if rows is not None else None
    p16_ok = usable and redacted_argv_row(p16_row, slack_path, SLACK_CANARY)
    emit("P16", p16_ok, "Slack-shaped argv redacted" if p16_ok else "Slack-shaped value not redacted")

    sibling = run_tool(tool, ["--prefix", str(prefix_root)])
    sibling_rows, sibling_error = parse_table(sibling["out"], boot_id)
    p17_ok = (
        sibling["rc"] == 0
        and not sibling["timed_out"]
        and sibling_rows is not None
        and p17.pid not in sibling_rows
        and not Path(p17_path).exists()
        and prefix_root.is_dir()
    )
    emit(
        "P17",
        p17_ok,
        "similarly prefixed sibling excluded"
        if p17_ok
        else "sibling prefix matched ({})".format(result_context(sibling, sibling_error)),
    )

    p18_row = rows.get(p18.pid) if rows is not None else None
    p18_ok = (
        usable
        and complete_record(p18_row)
        and p18_row["reason"] == "cwd-deleted"
        and p18_cwd_link.endswith(" (deleted)")
        and not Path(p18_path).exists()
        and not Path(p18_fd_path).exists()
    )
    p18_detail = (
        "cwd wins over argv and fd"
        if p18_ok
        else "wanted=cwd-deleted got={!r} argv_gone={} fd_gone={} cwd_deleted={}".format(
            p18_row["reason"] if p18_row else None,
            not Path(p18_path).exists(),
            not Path(p18_fd_path).exists(),
            p18_cwd_link.endswith(" (deleted)"),
        )
    )
    emit("P18", p18_ok, p18_detail)

    p19_row = rows.get(p19.pid) if rows is not None else None
    p19_ok = (
        usable
        and complete_record(p19_row)
        and p19_row["reason"] == "argv-path-gone:" + p19_path
        and not Path(p19_fd_path).exists()
        and os.path.isdir("/proc/{}/cwd".format(p19.pid))
    )
    p19_detail = (
        "argv wins over fd"
        if p19_ok
        else "wanted=argv-path-gone got={!r} fd_gone={} cwd_live={}".format(
            p19_row["reason"] if p19_row else None,
            not Path(p19_fd_path).exists(),
            os.path.isdir("/proc/{}/cwd".format(p19.pid)),
        )
    )
    emit("P19", p19_ok, p19_detail)
    print("SUMMARY\ttotal=19\tfailed={}".format(FAILURES))
    return 1 if FAILURES else 0


try:
    exit_code = run()
except SetupError as exc:
    print("SETUP\tFAIL\t{}".format(exc), file=sys.stderr)
    exit_code = 2
finally:
    cleanup_children()

sys.exit(exit_code)
PY
