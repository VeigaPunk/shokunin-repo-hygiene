#!/usr/bin/env python3
"""r42-drift-conditions.py - condition-level behaviours of tools/souji-worktree-drift.py.

Every case builds its own scenario under --work, runs `python3 -B <tool>` as a subprocess and asserts
only what a caller can observe: exit code, stdout/stderr tokens, the bytes of the --json file, whether
the tool returns at all.  The fixture never opens, hashes or searches the tool's source.

Cases (one per condition):
  record-fifo-not-blocking      a FIFO named as --record is refused, the tool does not hang on open()
  row-sibling-prefix            a record row resolving to a sibling directory that shares the root's
                                name prefix is outside the root
  gitdir-sibling-prefix         a .git file pointing at a sibling directory that shares the root's name
                                prefix is outside the root
  timeout-one-accepted          --timeout 1 is a valid value, --timeout 0 is a usage refusal
  timeout-default-over-one      with no --timeout a git that answers `worktree list` after 5 s is still
                                waited for (the default is well above 1 s)
  list-timeout-reported         a `worktree list` that outlives --timeout is reported as an UNREACHABLE
                                drift row, the tool neither raises nor exits silently
  list-rc-reported              a `worktree list` that exits non-zero is reported as an UNREACHABLE
                                drift row
  root-required / record-required   argparse refuses a missing --root / --record
  discovery-skips-symlink       a symlinked child directory is not reported as an unrecorded repository
  regs-two-digit                `regs=10` in a record row is a valid row
  json-truncates                a longer pre-existing --json target is truncated, not overwritten in place
  record-invalid-utf8           an undecodable byte in a record row name becomes U+FFFD, not a literal
                                backslash escape

Timeout cases (timeout-default-over-one, list-timeout-reported, list-rc-reported) use a PATH shim named
`git`.  Lifetime of the shim: it is written into <case dir>/shim/git (a small Python script whose
shebang is the running interpreter) under --work just before the tool runs, it is put first on the PATH
of that single subprocess only, it forwards every git call except `worktree list` to the real git
(found on the fixture's own PATH before the shim exists), and the whole case directory, shim
included, is removed when the case ends.  Nothing outside --work is written and no real hang is needed:
the shim sleeps (5 s against a 20 s default, 30 s against a 1 s --timeout, so every ratio is >= 4x) or
exits 3.  The record-fifo case is the one place a mutant would hang for real; its subprocess timeout
is 20 s, the pristine tool answers in well under a second.

CLI:
  python3 -B tests/fixtures/r42-drift-conditions.py --tool PATH --work DIR
Output: `case-<name>=PASS|FAIL <detail>` per case and `SUMMARY cases=<n> pass=<p> fail=<f>`.
Exit: 0 all cases pass, 1 any case fails, 2 usage or uid 0.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

REAL_GIT = shutil.which("git")
BASE_PATH = os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin")
ROW_R = "REPO\tr\tregs=1\tprunable=0\n"


def tool_env(tmp, path=None):
    return {"PATH": path or BASE_PATH, "LC_ALL": "C", "TMPDIR": tmp,
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}


def put(path, data):
    with open(path, "wb") as handle:
        handle.write(data if isinstance(data, bytes) else data.encode("utf-8"))
    return path


def git_init(path, tmp, bare=False):
    cmd = [REAL_GIT, "init", "-q"] + (["--bare"] if bare else []) + [path]
    subprocess.run(cmd, env=tool_env(tmp), check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, timeout=60)


def scenario(case_dir):
    """Fresh root with one real repository `r` (regs=1 prunable=0) and a sibling record directory."""
    root, out = case_dir + "/root", case_dir + "/o"
    os.makedirs(root)
    os.makedirs(out)
    git_init(root + "/r", case_dir)
    return root, out


def run_tool(tool, case_dir, args, path=None, cwd=None, timeout=60):
    """Return CompletedProcess (bytes) or None when the subprocess timeout expired."""
    try:
        return subprocess.run(["python3", "-B", tool] + list(args), env=tool_env(case_dir, path),
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd or case_dir,
                              timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return None


def txt(proc):
    return (proc.stdout + b"\n" + proc.stderr).decode("utf-8", "replace")


def describe(proc):
    if proc is None:
        return "tool-timeout"
    return "rc=%d out=%r" % (proc.returncode, txt(proc).replace("\n", " | ")[:240])


def refused(proc, cls):
    return proc is not None and proc.returncode == 2 and ("REFUSAL %s:" % cls) in proc.stderr.decode("utf-8", "replace")


def make_shim(case_dir, mode, seconds=0):
    """Write <case_dir>/shim/git; return the PATH that puts it first.  Removed with the case dir."""
    shim_dir = case_dir + "/shim"
    os.makedirs(shim_dir)
    body = (
        "#!%s\n"
        "import os, sys, time\n"
        "argv = sys.argv[1:]\n"
        "listing = any(argv[i] == 'worktree' and argv[i + 1:i + 2] == ['list'] for i in range(len(argv)))\n"
        "if listing and %r == 'delay':\n"
        "    time.sleep(%r)\n"
        "if listing and %r == 'fail':\n"
        "    sys.stderr.write('fatal: shim refuses worktree list\\n')\n"
        "    sys.exit(3)\n"
        "os.execv(%r, ['git'] + argv)\n"
    ) % (sys.executable, mode, float(seconds), mode, REAL_GIT)
    put(shim_dir + "/git", body)
    os.chmod(shim_dir + "/git", 0o755)
    return shim_dir + os.pathsep + BASE_PATH


# ---------------------------------------------------------------------------------------- cases


def case_record_fifo(tool, d):
    root, out = scenario(d)
    os.mkfifo(out + "/rfifo")
    p = run_tool(tool, d, ["--root", root, "--record", out + "/rfifo", "--skip-unrecorded"], timeout=20)
    return refused(p, "RECORD-MALFORMED"), describe(p)


def case_row_sibling_prefix(tool, d):
    root, out = scenario(d)
    rec = put(out + "/rec", "REPO\t../root2\tregs=1\tprunable=0\n")
    missing = run_tool(tool, d, ["--root", root, "--record", rec, "--skip-unrecorded"])
    os.makedirs(d + "/root2")  # the same row, now naming an existing plain directory (not a repository)
    plain = run_tool(tool, d, ["--root", root, "--record", rec, "--skip-unrecorded"])
    good = refused(missing, "RECORD-OUTSIDE-ROOT") and refused(plain, "RECORD-OUTSIDE-ROOT")
    return good, "missing[%s] plain[%s]" % (describe(missing), describe(plain))


def case_gitdir_sibling_prefix(tool, d):
    root, out = scenario(d)
    os.makedirs(d + "/rootX")
    git_init(d + "/rootX/gd2", d, bare=True)
    os.makedirs(root + "/s")
    put(root + "/s/.git", "gitdir: " + d + "/rootX/gd2\n")
    rec = put(out + "/rec", "REPO\ts\tregs=1\tprunable=0\n")
    p = run_tool(tool, d, ["--root", root, "--record", rec, "--skip-unrecorded"])
    return refused(p, "RECORD-OUTSIDE-ROOT"), describe(p)


def case_timeout_one(tool, d):
    root, out = scenario(d)
    rec = put(out + "/rec", "REPO\ta\tregs=1\tprunable=0\n")  # absent repo: no git call, no timing risk
    one = run_tool(tool, d, ["--root", root, "--record", rec, "--skip-unrecorded", "--timeout", "1"])
    zero = run_tool(tool, d, ["--root", root, "--record", rec, "--skip-unrecorded", "--timeout", "0"])
    good = (one is not None and one.returncode == 1 and "DRIFT\tABSENT\ta" in txt(one)
            and refused(zero, "USAGE"))
    return good, "one[%s] zero[%s]" % (describe(one), describe(zero))


def case_timeout_default(tool, d):
    root, out = scenario(d)
    rec = put(out + "/rec", ROW_R)
    path = make_shim(d, "delay", 5)
    p = run_tool(tool, d, ["--root", root, "--record", rec, "--skip-unrecorded"], path=path)
    good = (p is not None and p.returncode == 0 and "drift_rows=0" in txt(p)
            and "UNREACHABLE" not in txt(p) and "unreachable=0" in txt(p))
    return good, describe(p)


def case_list_timeout(tool, d):
    root, out = scenario(d)
    rec = put(out + "/rec", ROW_R)
    path = make_shim(d, "delay", 30)
    p = run_tool(tool, d, ["--root", root, "--record", rec, "--skip-unrecorded", "--timeout", "1"],
                 path=path, timeout=25)
    good = (p is not None and p.returncode == 1 and "DRIFT\tUNREACHABLE\tr\tUNREACHABLE:list-timeout" in txt(p)
            and "Traceback" not in txt(p))
    return good, describe(p)


def case_list_rc(tool, d):
    root, out = scenario(d)
    rec = put(out + "/rec", ROW_R)
    path = make_shim(d, "fail")
    p = run_tool(tool, d, ["--root", root, "--record", rec, "--skip-unrecorded"], path=path)
    good = (p is not None and p.returncode == 1 and "DRIFT\tUNREACHABLE\tr\tUNREACHABLE:list-rc=" in txt(p)
            and "unreachable=1" in txt(p))
    return good, describe(p)


def case_root_required(tool, d):
    root, out = scenario(d)
    rec = put(out + "/rec", ROW_R)
    empty = d + "/empty"
    os.makedirs(empty)
    p = run_tool(tool, d, ["--record", rec], cwd=empty)
    good = (p is not None and p.returncode == 2 and "required" in p.stderr.decode("utf-8", "replace")
            and "--root" in p.stderr.decode("utf-8", "replace"))
    return good, describe(p)


def case_record_required(tool, d):
    root, out = scenario(d)
    p = run_tool(tool, d, ["--root", root])
    err = p.stderr.decode("utf-8", "replace") if p is not None else ""
    good = p is not None and p.returncode == 2 and "required" in err and "--record" in err
    return good, describe(p)


def case_discovery_symlink(tool, d):
    root, out = scenario(d)
    git_init(root + "/u2", d)
    os.symlink(root + "/u2", root + "/lnk")
    rec = put(out + "/rec", ROW_R)
    p = run_tool(tool, d, ["--root", root, "--record", rec])
    t = txt(p) if p is not None else ""
    good = (p is not None and p.returncode == 1 and "DRIFT\tUNRECORDED\tu2" in t
            and "UNRECORDED\tlnk" not in t)
    return good, describe(p)


def case_regs_two_digit(tool, d):
    root, out = scenario(d)
    rec = put(out + "/rec", "REPO\tr\tregs=10\tprunable=0\n")
    p = run_tool(tool, d, ["--root", root, "--record", rec, "--skip-unrecorded"])
    good = p is not None and p.returncode == 1 and "record=10 live=1" in txt(p)
    return good, describe(p)


def case_json_truncates(tool, d):
    root, out = scenario(d)
    rec = put(out + "/rec", ROW_R)
    target = put(out + "/big.json", b"x" * 100000)
    p = run_tool(tool, d, ["--root", root, "--record", rec, "--skip-unrecorded", "--json", target])
    ok = False
    if p is not None and p.returncode == 0:
        try:
            with open(target, "rb") as handle:
                data = json.loads(handle.read().decode("utf-8"))
            ok = data.get("drift") == [] and data.get("summary", {}).get("live_repos") == 1
        except (ValueError, OSError, AttributeError):
            ok = False
    return ok, describe(p)


def case_invalid_utf8(tool, d):
    root, out = scenario(d)
    rec = put(out + "/rec", b"REPO\tal\xffpha\tregs=1\tprunable=0\n")
    target = out + "/o.json"
    p = run_tool(tool, d, ["--root", root, "--record", rec, "--skip-unrecorded", "--json", target])
    ok = False
    if p is not None and p.returncode == 1:
        try:
            with open(target, "rb") as handle:
                data = json.loads(handle.read().decode("utf-8"))
            rows = data.get("drift")
            ok = (isinstance(rows, list) and len(rows) == 1 and rows[0].get("class") == "ABSENT"
                  and rows[0].get("repo") == u"al\ufffdpha")
        except (ValueError, OSError, AttributeError):
            ok = False
    return ok, describe(p)


def case_clean_control(tool, d):
    root, out = scenario(d)
    rec = put(out + "/rec", ROW_R)
    p = run_tool(tool, d, ["--root", root, "--record", rec, "--skip-unrecorded"])
    good = p is not None and p.returncode == 0 and "drift_rows=0" in txt(p) and "live_repos=1" in txt(p)
    return good, describe(p)


CASES = (
    ("clean-control", case_clean_control),
    ("record-fifo-not-blocking", case_record_fifo),
    ("row-sibling-prefix", case_row_sibling_prefix),
    ("gitdir-sibling-prefix", case_gitdir_sibling_prefix),
    ("timeout-one-accepted", case_timeout_one),
    ("timeout-default-over-one", case_timeout_default),
    ("list-timeout-reported", case_list_timeout),
    ("list-rc-reported", case_list_rc),
    ("root-required", case_root_required),
    ("record-required", case_record_required),
    ("discovery-skips-symlink", case_discovery_symlink),
    ("regs-two-digit", case_regs_two_digit),
    ("json-truncates", case_json_truncates),
    ("record-invalid-utf8", case_invalid_utf8),
)


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    args = ap.parse_args(argv)
    if os.geteuid() == 0:
        sys.stderr.write("r42-drift-conditions: refusing to run as root\n")
        return 2
    if REAL_GIT is None or not os.path.isfile(args.tool) or not os.path.isdir(args.work):
        sys.stderr.write("r42-drift-conditions: need git on PATH, an existing --tool and --work\n")
        return 2
    tool = os.path.realpath(args.tool)
    work = os.path.realpath(args.work)
    bad = 0
    for name, fn in CASES:
        case_dir = os.path.realpath(tempfile.mkdtemp(prefix="r42c-", dir=work))
        try:
            good, detail = fn(tool, case_dir)
        except Exception as exc:  # noqa: BLE001 - a harness error is a failed case, never a traceback
            good, detail = False, "HARNESS-ERROR %s: %s" % (type(exc).__name__, exc)
        finally:
            shutil.rmtree(case_dir, ignore_errors=True)
        bad += not good
        print("case-%s=%s %s" % (name, "PASS" if good else "FAIL", "" if good else detail))
    print("SUMMARY cases=%d pass=%d fail=%d" % (len(CASES), len(CASES) - bad, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
