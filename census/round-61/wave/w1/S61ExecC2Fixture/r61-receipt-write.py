#!/usr/bin/env python3
"""r61 C2 fixture: 10-case matrix for a hardened receipt writer (souji-receipt-write.py)
with census/round-57/record-receipt.sh as the base comparator (frozen claim: base = 3/8).

Usage:
  python3 -B r61-receipt-write.py --tool PATH --work DIR [--style auto]

The fixture builds one throwaway git repo per case under DIR. Fixture rule honoured:
`git -C D init -q`, `git -C D rev-parse --show-toplevel` must equal D before the first
commit, and a throwaway identity is configured repo-locally only. Cases are independent
(fresh repo each) and re-runnable (case dirs are wiped at start). The fixture writes
only under --work and never touches the tool's own tree.

Invocation forms (--style auto: *.sh -> positional, anything else -> options):
  positional: TOOL LANE REV INSTR OUT --max-bytes 65536 -- CMD...
  options:    TOOL --root LANE --rev REV --instrument INSTR --out OUT \
              --max-bytes 65536 -- CMD...

--max-bytes 65536 is passed ONLY on case 5 (the bound is that case's subject),
between OUT and `--`: a flag-form tool parses it there; a positional tool shows
its unbounded behaviour (it execs `--max-bytes` as the wrapped command).

Receipt contract scored (case 1): lines instrument=<INSTR>,
instrument_sha256=<sha256 of the committed instrument bytes at REV, i.e. the same
digest the base computes via `git show REV:INSTR | sha256sum`>, rev=<REV40>,
command=<wrapped argv>, then the command's combined output, last line EXIT=0.
Any refusal: exit 2, OUT never created or modified, no *.tmp*/*.partial* sibling.

Cases:
  1 clean-write         honest write: all fields, correct digest, exit 0, no temp left
  2 overwrite           OUT pre-exists -> exit 2, OUT byte-identical, no temp
  3 atomic-in-flight    command sleeps 1s; OUT absent at ~0.3s; complete after
  4 kill-residue        SIGKILL tool process group at ~0.4s; OUT absent, no temp
  5 bound               ~2 MiB output vs --max-bytes 65536 -> exit 2, OUT absent
  6 rev-short           12-hex rev -> exit 2, OUT absent
  7 instrument-absent   instrument not in rev -> exit 2, OUT absent
  8 dirty-tree          untracked file in repo -> exit 2, OUT absent
  9 concealed-divergence
                        skip-worktree conceals a modified tracked instrument;
                        git status looks clean but worktree bytes differ from
                        the committed blob -> exit 2, OUT absent
  10 partial-visibility  command emits 5x200KB chunks over ~2s; a 20ms poller
                        sampling OUT from before the tool starts must never
                        observe a size other than the final size

Controls: an always-write stub must fail cases {2,4,5,6,7,8} (ALWAYS-WRITE-REJECTED);
an always-refuse stub must fail case 1 (ALWAYS-REFUSE-REJECTED).
Exit 0 iff all 10 cases pass and both controls are rejected.
"""

import argparse
import fnmatch
import hashlib
import json
import os
import shlex
import shutil
import signal
import subprocess
import sys
import time

MAX_BYTES = "65536"
INSTRUMENT_REL = "tools/instrument.sh"
INSTRUMENT_BODY = "#!/bin/sh\necho instrument-ok\n"
ABSENT_INSTRUMENT_REL = "tools/absent-instrument.sh"
KNOWN_BYTES = b"R60-KNOWN-BYTES-DO-NOT-OVERWRITE\n"
GIT_IDENTITY = [("user.name", "R60 C2 Fixture"), ("user.email", "r60-fixture@invalid")]
TEMP_PATTERNS = ("*.tmp*", "*.partial*")

# ---- r61 additions (cases 9-10) ----
# different bytes AND different length vs INSTRUMENT_BODY
CONCEALED_BODY = "#!/bin/sh\necho instrument-concealed\n"
# 5 x 200000 body bytes must not trip the bound
CASE_10_MAX_BYTES = "2097152"
CASE_10_CMD = "for i in 1 2 3 4 5; do head -c 200000 /dev/zero; sleep 0.4; done"
# Continuous OUT poller: samples (time, size, exists) every ~20ms from
# before the tool starts (ready file handshake) until the stop file exists.
READER_SRC = """\
import json, os, sys, time
out_path, samples_path, stop_path, ready_path = sys.argv[1:5]
samples = []
with open(ready_path, "wb") as f:
    f.write(b"ready")
while True:
    try:
        st = os.stat(out_path)
        samples.append([time.time(), st.st_size, True])
    except OSError:
        samples.append([time.time(), -1, False])
    if os.path.exists(stop_path):
        break
    time.sleep(0.02)
with open(samples_path, "wb") as f:
    f.write(json.dumps(samples).encode("ascii"))
"""

CASE_NAMES = {
    1: "clean-write",
    2: "overwrite",
    3: "atomic-in-flight",
    4: "kill-residue",
    5: "bound",
    6: "rev-short",
    7: "instrument-absent",
    8: "dirty-tree",
    9: "concealed-divergence",
    10: "partial-visibility",
}


def die(msg):
    sys.stderr.write("fixture error: %s\n" % msg)
    sys.exit(64)


def run_git(repo, argv, binary=False):
    proc = subprocess.run(
        ["git", "-C", repo] + argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if proc.returncode != 0:
        die("git %s failed rc=%d: %s" % (" ".join(argv), proc.returncode,
                                         proc.stderr.decode(errors="replace").strip()))
    return proc.stdout if binary else proc.stdout.decode().strip()


def spawn_args(style, repo, rev, instr, out, cmd, max_bytes=False):
    """Per-case minimal argv: --max-bytes is passed only where the bound is the
    subject (case 5), between OUT and `--` so a flag-form tool parses it while a
    positional tool shows its unbounded behaviour."""
    if style == "positional":
        args = [repo, rev, instr, out]
        if max_bytes:
            args += ["--max-bytes", MAX_BYTES]
        return args + ["--"] + list(cmd)
    args = ["--root", repo, "--rev", rev, "--instrument", instr, "--out", out]
    if max_bytes:
        args += ["--max-bytes", MAX_BYTES]
    return args + ["--"] + list(cmd)


def temp_siblings(out_dir):
    return sorted(f for f in os.listdir(out_dir)
                  if any(fnmatch.fnmatch(f, p) for p in TEMP_PATTERNS))


def last_nonempty_line(path):
    with open(path, "rb") as f:
        lines = [l for l in f.read().decode(errors="replace").splitlines() if l.strip()]
    return lines[-1] if lines else None


def run_tool(argv, timeout=30):
    return subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          timeout=timeout)


def tail(b, n=160):
    s = (b or b"").decode(errors="replace").strip().replace("\n", " | ")
    return s[-n:]


def _safe_shlex(s):
    try:
        return shlex.split(s)
    except ValueError:
        return None


class Matrix:
    def __init__(self, tool_path, style, work):
        self.tool = tool_path
        self.style = style
        self.work = work
        self.launch = ([sys.executable, "-B", tool_path]
                       if tool_path.endswith(".py") else [tool_path])
        self.results = {}   # case number -> (passed, detail)

    def build_case(self, n):
        tag = "case-%d" % n
        case_dir = os.path.join(self.work, tag)
        if os.path.isdir(case_dir):
            shutil.rmtree(case_dir)
        os.makedirs(case_dir)
        repo = os.path.join(case_dir, "repo")
        subprocess.run(["git", "init", "-q", "-b", "main", repo], check=True)
        top = run_git(repo, ["rev-parse", "--show-toplevel"])
        if os.path.realpath(top) != os.path.realpath(repo):
            die("toplevel %r != repo %r before first commit" % (top, repo))
        for key, val in GIT_IDENTITY:
            run_git(repo, ["config", key, val])
        os.makedirs(os.path.join(repo, "tools"))
        with open(os.path.join(repo, INSTRUMENT_REL), "w") as f:
            f.write(INSTRUMENT_BODY)
        run_git(repo, ["add", INSTRUMENT_REL])
        run_git(repo, ["commit", "-q", "-m", "r60 c2 fixture instrument"])
        rev = run_git(repo, ["rev-parse", "HEAD"])
        blob = run_git(repo, ["show", "%s:%s" % (rev, INSTRUMENT_REL)], binary=True)
        digest = hashlib.sha256(blob).hexdigest()
        out = os.path.join(repo, "receipt.txt")
        return {"repo": repo, "rev": rev, "rev12": rev[:12], "digest": digest,
                "out": out, "instr": INSTRUMENT_REL, "case_dir": case_dir}

    def argv(self, ctx, rev=None, instr=None, cmd=("echo", "ok"), max_bytes=False):
        return self.launch + spawn_args(self.style, ctx["repo"],
                                        rev or ctx["rev"], instr or ctx["instr"],
                                        ctx["out"], cmd, max_bytes=max_bytes)


def no_out_and_no_temp(ctx):
    out_dir = os.path.dirname(ctx["out"])
    if os.path.exists(ctx["out"]):
        return "OUT exists"
    temps = temp_siblings(out_dir)
    if temps:
        return "temp siblings: %s" % ", ".join(temps)
    return None


def case_1(m, ctx):
    proc = run_tool(m.argv(ctx))
    if proc.returncode != 0:
        return False, "tool rc=%d out=%r" % (proc.returncode, tail(proc.stdout))
    if not os.path.exists(ctx["out"]):
        return False, "receipt missing"
    lines = open(ctx["out"], "rb").read().decode(errors="replace").splitlines()
    want_command = "command=" + " ".join(["echo", "ok"])
    command_ok = any(
        l == want_command or
        (l.startswith("command=") and _safe_shlex(l[8:]) == ["echo", "ok"])
        for l in lines)
    problems = []
    if "instrument=%s" % ctx["instr"] not in lines:
        problems.append("instrument= line missing/wrong")
    if "instrument_sha256=%s" % ctx["digest"] not in lines:
        problems.append("instrument_sha256= != committed digest %s" % ctx["digest"])
    if "rev=%s" % ctx["rev"] not in lines:
        problems.append("rev= line missing/wrong")
    if not command_ok:
        problems.append("command= line missing/wrong")
    if last_nonempty_line(ctx["out"]) != "EXIT=0":
        problems.append("last line != EXIT=0")
    temps = temp_siblings(os.path.dirname(ctx["out"]))
    if temps:
        problems.append("temp siblings: %s" % ", ".join(temps))
    return (not problems), "; ".join(problems) or "ok"


def case_2(m, ctx):
    with open(ctx["out"], "wb") as f:
        f.write(KNOWN_BYTES)
    proc = run_tool(m.argv(ctx))
    if proc.returncode != 2:
        return False, "tool rc=%d (want 2)" % proc.returncode
    if open(ctx["out"], "rb").read() != KNOWN_BYTES:
        return False, "OUT bytes changed"
    temps = temp_siblings(os.path.dirname(ctx["out"]))
    if temps:
        return False, "temp siblings: %s" % ", ".join(temps)
    return True, "ok"


def case_3(m, ctx):
    proc = subprocess.Popen(m.argv(ctx, cmd=("sleep", "1")),
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            start_new_session=True)
    time.sleep(0.3)
    in_flight = os.path.exists(ctx["out"])
    try:
        rc = proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()
        return False, "tool still running after 15s"
    if in_flight:
        return False, "OUT already exists at ~0.3s"
    if rc != 0:
        return False, "tool rc=%d" % rc
    if not os.path.exists(ctx["out"]):
        return False, "OUT missing after completion"
    if last_nonempty_line(ctx["out"]) != "EXIT=0":
        return False, "last line != EXIT=0"
    return True, "ok"


def case_4(m, ctx):
    proc = subprocess.Popen(m.argv(ctx, cmd=("sleep", "1")),
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            start_new_session=True)
    time.sleep(0.4)
    if proc.poll() is None:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
    proc.wait(timeout=15)
    time.sleep(0.3)  # settle: catch late writes/residue
    problem = no_out_and_no_temp(ctx)
    if problem:
        return False, problem
    return True, "ok"


def case_5(m, ctx):
    cmd = ("sh", "-c", "head -c 2097152 /dev/zero")
    proc = run_tool(m.argv(ctx, cmd=cmd, max_bytes=True), timeout=30)
    if proc.returncode != 2:
        return False, "tool rc=%d (want 2)" % proc.returncode
    problem = no_out_and_no_temp(ctx)
    if problem:
        return False, problem
    return True, "ok"


def case_6(m, ctx):
    proc = run_tool(m.argv(ctx, rev=ctx["rev12"]))
    if proc.returncode != 2:
        return False, "tool rc=%d (want 2)" % proc.returncode
    problem = no_out_and_no_temp(ctx)
    if problem:
        return False, problem
    return True, "ok"


def case_7(m, ctx):
    proc = run_tool(m.argv(ctx, instr=ABSENT_INSTRUMENT_REL))
    if proc.returncode != 2:
        return False, "tool rc=%d (want 2)" % proc.returncode
    problem = no_out_and_no_temp(ctx)
    if problem:
        return False, problem
    return True, "ok"


def case_8(m, ctx):
    stray = os.path.join(ctx["repo"], "stray-untracked.txt")
    with open(stray, "w") as f:
        f.write("dirty\n")
    status = run_git(ctx["repo"], ["status", "--porcelain"])
    if not status.strip():
        return False, "fixture setup: repo not dirty"
    proc = run_tool(m.argv(ctx))
    if proc.returncode != 2:
        return False, "tool rc=%d (want 2)" % proc.returncode
    problem = no_out_and_no_temp(ctx)
    if problem:
        return False, problem
    return True, "ok"


def case_9(m, ctx):
    instr_path = os.path.join(ctx["repo"], *INSTRUMENT_REL.split("/"))
    run_git(ctx["repo"], ["update-index", "--skip-worktree", INSTRUMENT_REL])
    with open(instr_path, "w") as f:
        f.write(CONCEALED_BODY)
    status = run_git(ctx["repo"], ["status", "--porcelain"])
    if status.strip():
        return False, "fixture setup: skip-worktree failed to conceal the modification"
    proc = run_tool(m.argv(ctx))
    if proc.returncode != 2:
        return False, "tool rc=%d (want 2)" % proc.returncode
    problem = no_out_and_no_temp(ctx)
    if problem:
        return False, problem
    return True, "ok"


def case_10(m, ctx, _retry=True):
    out = ctx["out"]
    argv = m.launch + ["--root", ctx["repo"], "--rev", ctx["rev"],
                       "--instrument", ctx["instr"], "--out", out,
                       "--max-bytes", CASE_10_MAX_BYTES, "--",
                       "sh", "-c", CASE_10_CMD]
    samples_path = os.path.join(ctx["case_dir"], "reader-samples.json")
    stop_path = os.path.join(ctx["case_dir"], "reader-stop")
    ready_path = os.path.join(ctx["case_dir"], "reader-ready")
    reader = subprocess.Popen([sys.executable, "-B", "-c", READER_SRC,
                               out, samples_path, stop_path, ready_path],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.time() + 5
    while not os.path.exists(ready_path) and time.time() < deadline:
        time.sleep(0.005)
    if not os.path.exists(ready_path):
        reader.kill()
        reader.wait(timeout=10)
        return False, "reader never became ready (no samples)"
    proc = run_tool(argv, timeout=30)
    with open(stop_path, "wb") as f:
        f.write(b"stop")
    try:
        reader.wait(timeout=10)
    except subprocess.TimeoutExpired:
        reader.kill()
        return False, "reader did not stop after the tool exited"
    try:
        with open(samples_path, "rb") as f:
            samples = json.loads(f.read().decode("ascii"))
    except Exception:
        samples = []
    if not samples:
        if _retry:
            fresh = m.build_case(10)
            return case_10(m, fresh, _retry=False)
        return False, "reader observed no samples; cannot demonstrate atomic publish"
    if proc.returncode != 0:
        return False, "tool rc=%d out=%r" % (proc.returncode, tail(proc.stdout))
    if not os.path.exists(out):
        return False, "OUT missing after completion"
    if last_nonempty_line(out) != "EXIT=0":
        return False, "last line != EXIT=0"
    final_size = os.stat(out).st_size
    partial = [s for s in samples if s[2] and s[1] != final_size]
    if partial:
        return False, ("OUT observed in partial state: %d/%d samples non-final "
                       "(e.g. size=%d)" % (len(partial), len(samples), partial[0][1]))
    return True, "ok (samples=%d final_size=%d)" % (len(samples), final_size)


CASE_FUNCS = {1: case_1, 2: case_2, 3: case_3, 4: case_4,
              5: case_5, 6: case_6, 7: case_7, 8: case_8,
              9: case_9, 10: case_10}


def run_matrix(tool_path, style, work):
    """Run all 10 cases against tool_path; returns dict n -> (passed, detail)."""
    m = Matrix(tool_path, style, work)
    out = {}
    for n in range(1, 11):
        ctx = m.build_case(n)
        try:
            passed, detail = CASE_FUNCS[n](m, ctx)
        except Exception as exc:  # harness-level failure counts as case failure
            passed, detail = False, "exception: %r" % (exc,)
        out[n] = (passed, detail)
    return out


def write_stub(path, kind):
    if kind == "always-write":
        body = (
            "#!/usr/bin/env python3\n"
            "import subprocess, sys\n"
            "a = sys.argv[1:]\n"
            "out = a[a.index('--out') + 1] if '--out' in a else (a[3] if len(a) > 3 else None)\n"
            "if not out:\n"
            "    sys.exit(3)\n"
            "cmd = a[a.index('--') + 1:] if '--' in a else []\n"
            "open(out, 'wb').close()  # OUT appears immediately\n"
            "if cmd:\n"
            "    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)\n"
            "    with open(out, 'ab') as f:\n"
            "        f.write(p.stdout)\n"
            "with open(out, 'a') as f:\n"
            "    f.write('EXIT=0\\n')\n"
            "sys.exit(0)\n"
        )
    else:
        body = "#!/usr/bin/env python3\nimport sys\nsys.exit(2)\n"
    with open(path, "w") as f:
        f.write(body)
    os.chmod(path, 0o755)
    return path


def control_failset(stub_path, style, work):
    """Run the matrix against a control stub; return the set of failed case numbers."""
    results = run_matrix(stub_path, style, work)
    return {n for n, (passed, _) in results.items() if not passed}


def main():
    ap = argparse.ArgumentParser(description="r61 C2 receipt-writer 10-case fixture")
    ap.add_argument("--tool", required=True, help="tool under test (PATH)")
    ap.add_argument("--work", required=True, help="directory for fixture repos (created)")
    ap.add_argument("--style", default="auto", choices=["auto", "positional", "options"],
                    help="argv form; auto: *.sh -> positional, else options")
    args = ap.parse_args()

    tool = os.path.abspath(args.tool)
    work = os.path.abspath(args.work)
    os.makedirs(work, exist_ok=True)
    if not os.path.isfile(tool):
        die("tool not found: %s" % tool)
    if not os.access(tool, os.R_OK):
        die("tool not readable: %s" % tool)
    style = args.style
    if style == "auto":
        style = "positional" if tool.endswith(".sh") else "options"
    if style == "positional" and not os.access(tool, os.X_OK):
        die("positional style needs an executable tool: %s" % tool)

    print("# r61-receipt-write C2 fixture")
    print("# tool=%s" % tool)
    print("# style=%s" % style)
    print("# work=%s" % work)

    results = run_matrix(tool, style, work)
    for n in range(1, 11):
        passed, detail = results[n]
        print("CASE %d %s %s" % (n, CASE_NAMES[n], "pass" if passed else "fail"))
        if not passed:
            print("#   case %d detail: %s" % (n, detail))

    stubs_dir = os.path.join(work, "stubs")
    if os.path.isdir(stubs_dir):
        shutil.rmtree(stubs_dir)
    os.makedirs(stubs_dir)

    aw = write_stub(os.path.join(stubs_dir, "always-write.py"), "always-write")
    ar = write_stub(os.path.join(stubs_dir, "always-refuse.py"), "always-refuse")

    aw_failed = control_failset(aw, style, os.path.join(work, "control-always-write"))
    ar_failed = control_failset(ar, style, os.path.join(work, "control-always-refuse"))

    aw_rejected = {2, 4, 5, 6, 7, 8} <= aw_failed
    ar_rejected = 1 in ar_failed

    print("# control always-write failed cases %s -> ALWAYS-WRITE-%s"
          % (sorted(aw_failed), "REJECTED" if aw_rejected else "ACCEPTED"))
    print("# control always-refuse failed cases %s -> ALWAYS-REFUSE-%s"
          % (sorted(ar_failed), "REJECTED" if ar_rejected else "ACCEPTED"))

    p = sum(1 for n in range(1, 11) if results[n][0])
    f = 10 - p
    print("SUMMARY cases=10 pass=%d fail=%d control=ALWAYS-WRITE-%s,ALWAYS-REFUSE-%s"
          % (p, f, "REJECTED" if aw_rejected else "ACCEPTED",
             "REJECTED" if ar_rejected else "ACCEPTED"))
    return 0 if (p == 10 and aw_rejected and ar_rejected) else 1


if __name__ == "__main__":
    sys.exit(main())
