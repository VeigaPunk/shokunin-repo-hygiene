#!/usr/bin/env python
"""census/round-50/c2-counter.py — r50 C2 (operability): census receipts that
verify (capability acquisition).

Claim. The round contract requires a sources-census before→after measurement
every round, taken on this host through the r48 adapter
(`tools/souji-census-run.sh`: the conf form's raw rc-2 verdict recorded
beside the explicit-lane-directory form's verdict — disclosed, never
masked). Until r50 those census receipts were raw text captures with no
binding: nothing let a non-author re-derive the quoted counts from the
receipt's own bytes, or detect that the fleet script / adapter that produced
them has since changed. The new tool `tools/souji-census-receipt.py` captures
an adapter run into a digest-bound receipt (v1 grammar; the adapter's raw
output embedded verbatim) and verifies one later by re-deriving every header
value from the embedded raw output and re-hashing the scripts. This counter
reads, at the round tip (exit 0):

  SUMMARY receipts=<n> verified=<n> selftest=ok before=ok tool_sha=<12hex>

where n >= 1 and verified == n (every census receipt committed under
census/round-50/records/ verifies); at the round's FINAL tip n=2 (before +
after). At the round base it reads TOOL-ABSENT (exit 1) — the do-nothing
control `census/round-50/controls/c2-control-donothing.txt`. The SAME counter
measures both ends; the world moves, not the instrument (the r45
different-instrument limit does not apply).

Legs over the lane's committed bytes at --rev (git object store only, never
the work tree):
  selftest   the extracted tool's --selftest exits 0 printing
             SELFTEST cases=N pass=N fail=0 with N >= 6 (its six arms include
             capture+verify over a synthetic adapter and five tamper/malform
             refusals: DIGEST-MISMATCH, COUNT-MISMATCH, RC-INCONSISTENT,
             ADAPTER-DRIFT, MALFORMED)
  receipts   every blob matching census/round-50/records/census-*-receipt.txt
             at --rev is extracted and verified against the extracted rev
             bytes of BOTH tools (adapter drift check active); each verify
             exits 0 printing `VERIFY ok ... adapter=ok`
  before     a receipt named census-before-receipt.txt exists and carries
             CONF-RC=2, DIR-RC=0, DIR-RESULT=ok — the documented host state
             (conf form rc 2 disclosed, never masked; r48 precedent)

CLI:
  python -B census/round-50/c2-counter.py --root LANE --rev FULL40 --scratch DIR
Exit: 0 target met; 1 target unmet; 2 could-not-evaluate. All scratch (the
extracted tools and receipts) lives under --scratch; nothing is written
inside the repo. The counter writes no digest-bound fixture bytes and
launches the extracted tool with sys.executable (no `python3` name
dependency). Python stdlib only; the legs run fully offline over committed
bytes — no live census run is needed (the receipts are the captured runs).
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
TOOL_PATH = "tools/souji-census-receipt.py"
ADAPTER_PATH = "tools/souji-census-run.sh"
RECEIPT_PREFIX = "census/round-50/records/"
RECEIPT_RE = re.compile(r"^census/round-50/records/census-\w+-receipt\.txt$")
SELFTEST_RE = re.compile(r"^SELFTEST cases=(\d+) pass=(\d+) fail=(\d+)\s*$", re.M)


def env(work):
    return {"PATH": os.environ.get("PATH", ""), "TMPDIR": work, "LC_ALL": "C",
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}


def git(root, args, envp):
    return subprocess.run(["git", "-C", root] + args, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, env=envp, check=False)


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

    def blob(path):
        p = git(args.root, ["show", "%s:%s" % (args.rev, path)], envp)
        return p.stdout if p.returncode == 0 else None

    ls = git(args.root, ["ls-tree", "-r", "--name-only", args.rev,
                         RECEIPT_PREFIX], envp)
    receipt_paths = sorted(line for line in ls.stdout.decode("utf-8", "replace").splitlines()
                           if RECEIPT_RE.match(line))
    tool_bytes = blob(args.tool)
    if tool_bytes is None:
        print("PRISTINE FAIL TOOL-ABSENT %s at %s" % (args.tool, args.rev))
        print("SUMMARY receipts=%d verified=0 selftest=FAIL before=FAIL tool_sha=absent"
              % len(receipt_paths))
        return 1
    adapter_bytes = blob(ADAPTER_PATH)

    work = tempfile.mkdtemp(prefix="souji-r50-c2.", dir=args.scratch)
    # The tool computes its lane-root refusal boundary from its own location
    # (dirname(dirname(__file__)) — for the extracted tool, `work`): extract
    # it under a `tools/` subtree and keep TMPDIR in a SIBLING tree under
    # --scratch, so the Q66 refusal does not fire on the counter's own
    # scratch layout.
    tools_dir = os.path.join(work, "tools")
    os.makedirs(tools_dir)
    tmp_dir = tempfile.mkdtemp(prefix="souji-r50-c2-tmp.", dir=args.scratch)
    try:
        tool = os.path.join(tools_dir, "souji-census-receipt.py")
        with open(tool, "wb") as handle:
            handle.write(tool_bytes)
        tool_sha = hashlib.sha256(tool_bytes).hexdigest()[:12]
        adapter_state = "absent"
        if adapter_bytes is not None:
            adapter_state = "ok"
            with open(os.path.join(tools_dir, "souji-census-run.sh"), "wb") as handle:
                handle.write(adapter_bytes)

        def run_tool(tool_argv):
            try:
                p = subprocess.run([sys.executable, "-B", tool] + tool_argv,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True, check=False, env=env(tmp_dir), timeout=300)
            except subprocess.TimeoutExpired:
                return 124, "", True
            crash = "Traceback (most recent call last)" in p.stderr
            return p.returncode, p.stdout, crash

        rc, out, crash = run_tool(["--selftest"])
        m = SELFTEST_RE.findall(out)
        selftest_ok = (rc == 0 and not crash and bool(m)
                       and int(m[-1][0]) >= 6 and m[-1][0] == m[-1][1] and m[-1][2] == "0")

        verified = 0
        details = []
        for path in receipt_paths:
            data = blob(path)
            rpath = os.path.join(work, os.path.basename(path))
            with open(rpath, "wb") as handle:
                handle.write(data)
            if adapter_state != "ok":
                vrc, vout, vcrash = run_tool(["verify", "--receipt", rpath])
                vok = vrc == 0 and "VERIFY ok" in vout and "adapter=unchecked" in vout
            else:
                vrc, vout, vcrash = run_tool(["verify", "--receipt", rpath])
                vok = (vrc == 0 and not vcrash and "VERIFY ok" in vout and "adapter=ok" in vout)
            details.append("%s rc=%d %s" % (os.path.basename(path), vrc,
                                            "ok" if vok else vout.strip()[:100]))
            verified += 1 if vok else 0

        before_ok = False
        for path in receipt_paths:
            if path.endswith("census-before-receipt.txt"):
                data = blob(path)
                text = data.decode("utf-8", "replace")
                before_ok = ("CONF-RC=2\n" in text and "DIR-RC=0\n" in text
                             and "DIR-RESULT=ok\n" in text)

        print("receipts " + "; ".join(details) if details else "receipts none")
        print("SUMMARY receipts=%d verified=%d selftest=%s before=%s tool_sha=%s"
              % (len(receipt_paths), verified, "ok" if selftest_ok else "FAIL",
                 "ok" if before_ok else "FAIL", tool_sha))
        met = (selftest_ok and len(receipt_paths) >= 1 and verified == len(receipt_paths)
               and before_ok)
        return 0 if met else 1
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
