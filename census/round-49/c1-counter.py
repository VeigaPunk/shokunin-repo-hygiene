#!/usr/bin/env python3
"""census/round-49/c1-counter.py — r49 C1 (calibration): the freeze-check selftest re-derivable on this host.

Claim. The r48 non-author closure routed defect 1: `tools/souji-freeze-check.py --selftest`
fails 37/41 on this Windows host because the selftest's fixture writer uses text mode
(`open(..., "w")`), so platform newline translation corrupts the three literal LF digests
(SHA_C/SHA_P/SHA_P1 = sha256 of LF-terminated bytes). The r42 registry gate
`r42-freeze-check-selftest` ("0 iff SELFTEST ... fail=0 with n >= 12") therefore has no green
verdict on this host: the lane's standing self-assessment of its own freeze instrument does
not match observed state. The repair (this round's content commit) ports the fixture writes
to binary mode. This counter must read, at the round tip (exit 0):

  SUMMARY selftest=ok patches=3/3 real=ok retro=red retro_clean=ok tool_sha=<12hex>

and `selftest=FAIL` (exit 1) at the round base, where the committed tool bytes still carry
the text-mode writer — the do-nothing control
`census/round-49/controls/c1-control-donothing.txt`. The SAME counter measures both ends;
the world (the tool's committed bytes) moves, not the instrument — the r45
different-instrument limit does not apply.

The counter itself is binary-clean: it writes no digest-bound fixture bytes at all, and it
launches the extracted tool with `sys.executable`, so it carries no `python3` interpreter-name
dependency (this host has no `python3`; r45's frozen r42 counter cannot even produce its
verdict here for that same reason — a named limit of that instrument, not of this claim).

Legs over the lane's committed bytes at --rev (git object store only, never the work tree):
  selftest     the tool's --selftest exits 0 printing `SELFTEST cases=N pass=N fail=0`, N >= 12
  patches      the same selftest under P1 (hashlib digests reversed), P2 (`git log
               --diff-filter=A` returns nothing) and P3 (`git merge-base` fails) — injected
               through a sitecustomize on PYTHONPATH, the r42 counter's technique — must each
               exit non-zero (3/3): a self-test that cannot fail under a broken instrument is
               rejected. A patch arm only counts when the unpatched selftest is ok (r42 rule).
  real         the tool over `census/round-48/preregistration.txt` at --rev: exit 0,
               `SUMMARY claims=2 findings=0` (the verdict path is unchanged by the repair)
  retro        the tool over `census/round-40/preregistration.txt` at --rev: exit 1 with >= 3
               findings (pre-grammar bytes stay red)
  retro_clean  the tool over `census/round-41/preregistration.txt` at --rev: exit 0,
               `SUMMARY claims=3 findings=0`

CLI:
  python -B census/round-49/c1-counter.py --root LANE --rev FULL40 --scratch DIR
Exit: 0 target met; 1 target unmet; 2 could-not-evaluate. All scratch (the extracted tool,
patch sitecustomizes, per-run TMPDIR) lives under --scratch; nothing is written inside the
repo. Python stdlib only.
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

REV = re.compile(r"^[0-9a-f]{40}$")
TOOL_PATH = "tools/souji-freeze-check.py"
REAL_PATH = "census/round-48/preregistration.txt"
RETRO_PATH = "census/round-40/preregistration.txt"
CLEAN_RETRO_PATH = "census/round-41/preregistration.txt"
SELFTEST_RE = re.compile(r"^SELFTEST cases=(\d+) pass=(\d+) fail=(\d+)\s*$", re.M)
SUMMARY_RE = re.compile(r"^SUMMARY claims=(\d+) findings=(\d+)\s*$", re.M)
FINDING_RE = re.compile(r"^FINDING (\S+) (\S+)", re.M)

SITECUSTOMIZE = (
    "import os, sys\n"
    "_p = os.environ.get('SOUJI_R49_PATCH', '')\n"
    "if _p == 'P1':\n"
    "    import hashlib\n"
    "    _orig = hashlib.sha256\n"
    "    class _Rev(object):\n"
    "        def __init__(self, *a, **k):\n"
    "            self._h = _orig(*a, **k)\n"
    "        def update(self, b):\n"
    "            self._h.update(b)\n"
    "        def hexdigest(self):\n"
    "            return self._h.hexdigest()[::-1]\n"
    "        def digest(self):\n"
    "            return self._h.digest()[::-1]\n"
    "    hashlib.sha256 = _Rev\n"
    "elif _p in ('P2', 'P3'):\n"
    "    import subprocess\n"
    "    _run = subprocess.run\n"
    "    def _patched(args, *a, **k):\n"
    "        try:\n"
    "            argv = [str(x) for x in args]\n"
    "        except TypeError:\n"
    "            argv = []\n"
    "        if _p == 'P2' and argv[:1] == ['git'] and '--diff-filter=A' in argv:\n"
    "            return subprocess.CompletedProcess(args, 0, b'', b'')\n"
    "        if _p == 'P3' and argv[:1] == ['git'] and 'merge-base' in argv:\n"
    "            return subprocess.CompletedProcess(args, 1, b'', b'')\n"
    "        return _run(args, *a, **k)\n"
    "    subprocess.run = _patched\n"
)


def env(work):
    e = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": work,
         "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
         "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}
    return e


def git(root, args, envp):
    return subprocess.run(["git", "-C", root] + args, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, env=envp, check=False)


def run_tool(tool, root, rev, prereg, work):
    p = subprocess.run([sys.executable, "-B", tool, "--root", root, "--prereg", prereg,
                        "--rev", rev], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       text=True, check=False, env=env(work), timeout=600)
    findings = sorted(set(FINDING_RE.findall(p.stdout)))
    summ = SUMMARY_RE.findall(p.stdout)
    crash = "Traceback (most recent call last)" in p.stderr
    return p.returncode, findings, (tuple(int(x) for x in summ[-1]) if summ else None), crash


def run_selftest(tool, scratch, patch=None):
    work = tempfile.mkdtemp(prefix="st.", dir=scratch)
    e = env(work)
    if patch:
        pdir = os.path.join(scratch, "patch-" + patch)
        os.makedirs(pdir, exist_ok=True)
        # sitecustomize is interpreter source, not a digest-bound fixture; written
        # binary anyway so the bytes are identical on every platform
        with open(os.path.join(pdir, "sitecustomize.py"), "wb") as h:
            h.write(SITECUSTOMIZE.encode("utf-8"))
        e["PYTHONPATH"] = pdir
        e["SOUJI_R49_PATCH"] = patch
    try:
        p = subprocess.run([sys.executable, "-B", tool, "--selftest"], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True, check=False, env=e, timeout=900)
    except subprocess.TimeoutExpired:
        return 124, None, True
    finally:
        shutil.rmtree(work, ignore_errors=True)
    m = SELFTEST_RE.findall(p.stdout)
    crash = "Traceback (most recent call last)" in p.stderr
    return p.returncode, (tuple(int(x) for x in m[-1]) if m else None), crash


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--tool", default=TOOL_PATH)
    ap.add_argument("--scratch", required=True)
    args = ap.parse_args(argv)
    if not REV.match(args.rev):
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --rev must be a full 40-hex commit id\n")
        return 2
    if not os.path.isdir(args.root) or not os.path.isdir(args.scratch):
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --root and --scratch must name directories\n")
        return 2
    envp = env(args.scratch)
    chk = git(args.root, ["cat-file", "-e", args.rev + "^{commit}"], envp)
    if chk.returncode != 0:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --rev does not resolve in %s\n" % args.root)
        return 2
    blob = git(args.root, ["show", "%s:%s" % (args.rev, args.tool)], envp)
    if blob.returncode != 0:
        print("PRISTINE FAIL TOOL-ABSENT %s at %s" % (args.tool, args.rev))
        print("SUMMARY selftest=FAIL patches=0/3 real=FAIL retro=FAIL retro_clean=FAIL tool_sha=absent")
        return 1
    scratch = tempfile.mkdtemp(prefix="souji-r49-c1.", dir=args.scratch)
    try:
        tool = os.path.join(scratch, "tool.py")
        # the tool's own bytes, byte-exact from the object store; written binary
        with open(tool, "wb") as h:
            h.write(blob.stdout)
        st_rc, st_sum, st_crash = run_selftest(tool, scratch)
        selftest = "ok" if (st_rc == 0 and st_sum and st_sum[0] >= 12 and st_sum[1] == st_sum[0]
                            and st_sum[2] == 0 and not st_crash) else "FAIL"
        patches = 0
        for patch in ("P1", "P2", "P3"):
            p_rc, _ps, p_crash = run_selftest(tool, scratch, patch)
            patches += 1 if (selftest == "ok" and p_rc not in (0, 124)) else 0
        r_rc, r_find, r_summ, r_crash = run_tool(tool, args.root, args.rev, REAL_PATH, scratch)
        real = "ok" if (r_rc == 0 and not r_find and r_summ == (2, 0) and not r_crash) else "FAIL"
        t_rc, t_find, _ts, t_crash = run_tool(tool, args.root, args.rev, RETRO_PATH, scratch)
        retro = "red" if (t_rc == 1 and len(t_find) >= 3 and not t_crash) else "FAIL"
        c_rc, c_find, c_summ, c_crash = run_tool(tool, args.root, args.rev, CLEAN_RETRO_PATH, scratch)
        retro_clean = "ok" if (c_rc == 0 and not c_find and c_summ == (3, 0) and not c_crash) else "FAIL"
        print("selftest %s rc=%d summary=%r" % (selftest, st_rc, st_sum))
        print("real %s rc=%d findings=%d summary=%r" % (real, r_rc, len(r_find), r_summ))
        print("retro %s rc=%d findings=%d" % (retro, t_rc, len(t_find)))
        print("retro_clean %s rc=%d findings=%d summary=%r" % (retro_clean, c_rc, len(c_find), c_summ))
        print("SUMMARY selftest=%s patches=%d/3 real=%s retro=%s retro_clean=%s tool_sha=%s"
              % (selftest, patches, real, retro, retro_clean,
                 hashlib.sha256(blob.stdout).hexdigest()[:12]))
        met = (selftest == "ok" and patches == 3 and real == "ok" and retro == "red"
               and retro_clean == "ok")
        return 0 if met else 1
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
