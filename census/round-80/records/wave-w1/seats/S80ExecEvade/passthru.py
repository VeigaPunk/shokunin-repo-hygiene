#!/usr/bin/env python3
"""S80ExecEvade r80 W2 pass-through probes: base (f80f9368) vs candidate (836dac3e)
exit codes / output for no-signal invocations, TMPDIR variants, stdin, guard, selftest.
"""
import hashlib
import os
import secrets
import signal
import subprocess
import sys
import time

SCRATCH = "/fast/scratch/hyaku/souji-r80/S80ExecEvade"
CAND = os.path.join(SCRATCH, "tools-cand", "souji-quarantine.sh")
BASE = os.path.join(SCRATCH, "tools-base", "souji-quarantine.sh")
ENGINE = os.path.join(SCRATCH, "tools-cand", "souji-verify.sh")

import importlib.util
_spec = importlib.util.spec_from_file_location(
    "c2c", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-80/c2-signal-counter.py")
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

RESET = (signal.SIGINT, signal.SIGQUIT, signal.SIGTERM, signal.SIGHUP)
FIX = os.path.join(SCRATCH, "passthru-fixture")


def _preexec():
    for s in RESET:
        signal.signal(s, signal.SIG_DFL)


def build_fixtures():
    import shutil
    shutil.rmtree(FIX, ignore_errors=True)
    rd = FIX
    fleet, repo, ledger, ftarget = C.build(rd, "file")
    dird = os.path.join(rd, "d")
    _, _, _, dtarget = C.build(dird, "dir")
    os.makedirs(os.path.join(rd, "tmp"))
    os.makedirs(os.path.join(dird, "tmp"))
    return rd, dird, repo, ftarget, dtarget


def env_for(rd, extra=None, drop_tmp=False, tmp=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SOUJI_"))}
    env.update({"LC_ALL": "C", "TMPDIR": os.path.join(rd, "tmp"),
                "SOUJI_Q_SHOKUNIN_ROOT": os.path.join(rd, "fleet"),
                "SOUJI_Q_LEDGER": os.path.join(rd, "ledger.tsv"),
                "SOUJI_VERIFY_BIN": ENGINE,
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    if drop_tmp:
        env.pop("TMPDIR", None)
    if tmp is not None:
        env["TMPDIR"] = tmp
    if extra:
        env.update(extra)
    return env


def run(tool, args, env, stdin_bytes=None, timeout=120):
    p = subprocess.run(["bash", tool] + args, capture_output=True, env=env,
                       input=stdin_bytes, timeout=timeout, preexec_fn=_preexec)
    return p.returncode, p.stdout, p.stderr


def line1(b):
    ls = b.decode("utf-8", "replace").splitlines()
    return ls[0][:110] if ls else "(empty)"


def tokens(b):
    out = []
    for l in b.decode("utf-8", "replace").splitlines():
        if l.startswith(("RESULT\t", "SUMMARY\t", "GUARD\t")):
            out.append(l[:100])
    return out


def pt(label, rc, out, err, extra=""):
    print(f"PT {label} rc={rc} out1={line1(out)!r} err1={line1(err)!r} {extra}", flush=True)


def main():
    rd, dird, repo, ftarget, dtarget = build_fixtures()
    pairs = {}
    for toolname, tool in (("base", BASE), ("cand", CAND)):
        rc, out, err = run(tool, ["--bogus-flag"], env_for(rd))
        pt(f"usage-bad/{toolname}", rc, out, err)
        rc, out, err = run(tool, [], env_for(rd))
        pt(f"noargs/{toolname}", rc, out, err)
        rc, out, err = run(tool, ["--hold", "0", repo, ftarget], env_for(rd))
        pt(f"guard4/{toolname}", rc, out, err, extra="tokens=%s" % tokens(out))
        rc, out, err = run(tool, ["--dry-run", repo, ftarget], env_for(rd))
        pt(f"p1-file/{toolname}", rc, out, err, extra="tokens=%s" % tokens(out))
        pairs[f"p1/{toolname}"] = (rc, out, err)
        rc, out, err = run(tool, ["--dry-run", repo, dtarget], env_for(dird))
        pt(f"p2-dir/{toolname}", rc, out, err, extra="tokens=%s" % tokens(out))
        pairs[f"p2/{toolname}"] = (rc, out, err)
        rc, out, err = run(tool, ["--dry-run", repo, ftarget], env_for(rd, drop_tmp=True))
        pt(f"tmpdir-unset-p1/{toolname}", rc, out, err, extra="tokens=%s" % tokens(out))
        rc, out, err = run(tool, ["--dry-run", repo, ftarget], env_for(rd, tmp="/nonexistent-S80xyz/deep"))
        pt(f"tmpdir-bad-p1/{toolname}", rc, out, err)
        rc, out, err = run(tool, ["--bogus-flag"], env_for(rd, tmp="/nonexistent-S80xyz/deep"))
        pt(f"tmpdir-bad-usage/{toolname}", rc, out, err)
        spaced = os.path.join(SCRATCH, "has space")
        os.makedirs(spaced, exist_ok=True)
        rc, out, err = run(tool, ["--dry-run", repo, ftarget], env_for(rd, tmp=spaced))
        pt(f"tmpdir-space-p1/{toolname}", rc, out, err, extra="tokens=%s" % tokens(out))
        rc, out, err = run(tool, ["--dry-run", repo, ftarget], env_for(rd), stdin_bytes=b"stdin data\n")
        pt(f"stdin-pipe-p1/{toolname}", rc, out, err)
        assert rc == pairs[f"p1/{toolname}"][0]
    for kind in ("p1", "p2"):
        rb, ob, eb = pairs[f"{kind}/base"]
        rn, on, en = pairs[f"{kind}/cand"]
        same = "EQUAL" if (rb == rn and ob == on and eb == en) else "DIFF"
        print(f"PT byte-compare/{kind}: rc base={rb} cand={rn}; stdout={same}", flush=True)
        if ob != on:
            bl, nl = ob.splitlines(), on.splitlines()
            for i in range(max(len(bl), len(nl))):
                a = bl[i] if i < len(bl) else b"<eof>"
                b2 = nl[i] if i < len(nl) else b"<eof>"
                if a != b2:
                    print(f"PT   first stdout diff line {i}: base={a[:120]!r} cand={b2[:120]!r}", flush=True)
                    break
        if eb != en:
            print(f"PT   stderr differs: base={eb[:120]!r} cand={en[:120]!r}", flush=True)
    left = [p for p in os.listdir("/tmp") if p.startswith("souji-quarantine.")]
    print(f"PT tmp-leftovers-in-/tmp after cand runs: {left}", flush=True)


if __name__ == "__main__":
    main()
