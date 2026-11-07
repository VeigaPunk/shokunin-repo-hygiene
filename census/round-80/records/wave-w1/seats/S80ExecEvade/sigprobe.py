#!/usr/bin/env python3
"""S80ExecEvade r80 W2 probes: attack the souji-quarantine.sh front/worker split
outside the 15 frozen rows. Fixtures reuse the frozen C2 counter's own fixture
builders (imported read-only), shaped per census/round-80/c2-signal-counter.py.
Scratch: /fast/scratch/hyaku/souji-r80/S80ExecEvade/probes/<id>-<n>/
Run serialized; each probe cleans its nonce-tagged children (reap).
"""
import importlib.util
import os
import secrets
import signal
import subprocess
import sys
import time

SEAT = os.path.dirname(os.path.abspath(__file__))
SCRATCH = "/fast/scratch/hyaku/souji-r80/S80ExecEvade"
CAND = os.path.join(SCRATCH, "tools-cand", "souji-quarantine.sh")
BASE = os.path.join(SCRATCH, "tools-base", "souji-quarantine.sh")
ENGINE = os.path.join(SCRATCH, "tools-cand", "souji-verify.sh")
PROOT = os.path.join(SCRATCH, "probes")

_spec = importlib.util.spec_from_file_location(
    "c2c", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-80/c2-signal-counter.py")
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

RESET = (signal.SIGINT, signal.SIGQUIT, signal.SIGTERM, signal.SIGHUP)


def _preexec():
    for s in RESET:
        signal.signal(s, signal.SIG_DFL)
    signal.pthread_sigmask(signal.SIG_UNBLOCK, RESET)


def fresh(pid_s):
    os.makedirs(PROOT, exist_ok=True)
    rd = os.path.join(PROOT, f"{pid_s}-{secrets.token_hex(3)}")
    fleet, repo, ledger, target = C.build(rd, "file")
    os.makedirs(os.path.join(rd, "tmp"))
    return rd, repo, ledger, target


def base_env(rd, nonce, shimdir=None, engine=ENGINE, extra=None, target=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SOUJI_"))}
    env.update({"LC_ALL": "C", "TMPDIR": os.path.join(rd, "tmp"),
                "SOUJI_R80_NONCE": nonce,
                "SOUJI_Q_SHOKUNIN_ROOT": os.path.join(rd, "fleet"),
                "SOUJI_Q_LEDGER": os.path.join(rd, "ledger.tsv"),
                "SOUJI_VERIFY_BIN": engine,
                "SOUJI_R80_MARK": os.path.join(rd, "hang.mark"),
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    if shimdir:
        env["PATH"] = shimdir + os.pathsep + os.environ["PATH"]
    if target is not None:
        env["SOUJI_R80_TARGET"] = target
    if extra:
        env.update(extra)
    return env


def write_shim(shimdir, name, body):
    os.makedirs(shimdir, exist_ok=True)
    p = os.path.join(shimdir, name)
    tail = "" if name.startswith("engine-") else f'exec {C.which(name)} "$@"\n'
    with open(p, "w", encoding="utf-8") as f:
        f.write("#!/bin/bash\n" + C.MARK_FN + body + tail)
    os.chmod(p, 0o755)
    return p


HANG_ON_TARGET = ('last=; for last in "$@"; do :; done\n'
                  'if [[ $last == "$SOUJI_R80_TARGET" ]]; then r80_mark sha256sum "$@"; exec sleep 600; fi\n')


def launch(tool, rd, args, env, new_session=True, engine_unused=None):
    outp = os.path.join(rd, "tool.out")
    errp = os.path.join(rd, "tool.err")
    nonce = env["SOUJI_R80_NONCE"]
    argv = ["bash", tool] + args
    fo = open(outp, "wb")
    fe = open(errp, "wb")
    t0 = time.monotonic()
    p = subprocess.Popen(argv, stdout=fo, stderr=fe, stdin=subprocess.DEVNULL, env=env,
                         start_new_session=new_session, cwd=rd, preexec_fn=_preexec)
    return p, fo, fe, outp, errp, t0, nonce


def out_lines(outp):
    try:
        with open(outp, "rb") as f:
            return f.read().decode("utf-8", "replace")
    except OSError:
        return ""


def wait_mark(mark, p, t0, bound=60.0):
    while not os.path.exists(mark) and p.poll() is None and time.monotonic() - t0 < bound:
        time.sleep(0.02)
    return os.path.exists(mark)


def survivors(nonce, settle=1.0):
    time.sleep(settle)
    out = []
    for pid in C.nonce_pids(nonce):
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                cl = f.read().replace(b"\0", b" ").decode(errors="replace")[:60]
        except OSError:
            cl = "?"
        out.append(f"{pid}:{cl}")
    return out


def tmp_left(rd):
    out = []
    for dp, dns, fns in os.walk(os.path.join(rd, "tmp")):
        out += [os.path.join(dp, n) for n in dns] + [os.path.join(dp, n) for n in fns]
    return out


def reap(p, nonce):
    C.reap(nonce)
    if p.poll() is None:
        p.kill()
    p.wait()


def report(pid_s, d):
    keys = ("rc", "secs", "sigline", "nsig", "survivors", "tmpleft", "src", "qdir", "qpath",
            "verdicts", "extra")
    print("PROBE " + pid_s + " " + " ".join(f"{k}={d.get(k, '-')}" for k in keys), flush=True)


def sig_of(rc):
    return -rc if isinstance(rc, int) and rc < 0 else None


# ---------------- scenarios ----------------

def p_baseline():
    rd, repo, ledger, target = fresh("baseline")
    env = base_env(rd, secrets.token_hex(8))
    p, fo, fe, outp, errp, t0, nonce = launch(CAND, rd, ["--dry-run", repo, target], env)
    try:
        rc = p.wait(timeout=60)
        secs = round(time.monotonic() - t0, 2)
        txt = out_lines(outp)
        report("baseline", {"rc": rc, "secs": secs, "sigline": "y" if "SIGNAL\t" in txt else "n",
                            "survivors": survivors(nonce, 0.5), "tmpleft": tmp_left(rd),
                            "verdicts": [l for l in txt.splitlines() if l.startswith("RESULT")]
                            or [l for l in txt.splitlines() if l.startswith("SUMMARY")], "extra": ""})
    finally:
        reap(p, nonce)


def p_between_targets():
    rd, repo, ledger, t1 = fresh("between")
    t2 = os.path.join(repo, ".scratch", "aged2.dat")
    with open(t2, "w", encoding="utf-8") as f:
        f.write("r80 aged2 payload\n")
    C.aged(t2)
    C.aged(os.path.join(repo, ".scratch"))
    sd = os.path.join(rd, "shim")
    eng = write_shim(sd, "engine-hang2.sh", 'last=; for last in "$@"; do :; done\n'
                     'if [[ $last == "$SOUJI_R80_TARGET2" ]]; then r80_mark engine "$@"; exec sleep 600; fi\n'
                     f'exec {ENGINE} "$@"\n')
    nonce = secrets.token_hex(8)
    env = base_env(rd, nonce, shimdir=sd, engine=eng, extra={"SOUJI_R80_TARGET2": t2})
    p, fo, fe, outp, errp, t0, nonce = launch(CAND, rd, ["--dry-run", repo, t1, t2], env)
    try:
        hit = wait_mark(env["SOUJI_R80_MARK"], p, t0)
        if not hit:
            report("between-targets", {"rc": "NO-MARK rc=%s" % p.poll(), "extra": "engine for t2 never hung"})
            return
        time.sleep(0.3)
        t1s = time.monotonic()
        os.kill(p.pid, signal.SIGTERM)
        try:
            rc = p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            rc = "ALIVE"
        secs = round(time.monotonic() - t1s, 2)
        txt = out_lines(outp)
        sigl = [l for l in txt.splitlines() if l.startswith("SIGNAL\t")]
        report("between-targets", {"rc": rc, "secs": secs,
                                   "sigline": "y" if sigl else "n", "nsig": len(sigl),
                                   "survivors": survivors(nonce), "tmpleft": tmp_left(rd),
                                   "verdicts": [l for l in txt.splitlines() if l.startswith("RESULT")],
                                   "extra": "t1-result-before-sig=%s t2-never-finished=%s" % (
                                       "RESULT\t%s\tDRY-RUN-PASS" % t1 in txt, ("RESULT\t%s" % t2) not in txt)})
    finally:
        reap(p, nonce)


def p_double(first, second, gap, tag):
    rd, repo, ledger, target = fresh(tag)
    sd = os.path.join(rd, "shim")
    write_shim(sd, "sha256sum", HANG_ON_TARGET)
    nonce = secrets.token_hex(8)
    env = base_env(rd, nonce, shimdir=sd, target=target)
    p, fo, fe, outp, errp, t0, nonce = launch(CAND, rd, ["--dry-run", repo, target], env)
    try:
        if not wait_mark(env["SOUJI_R80_MARK"], p, t0):
            report(tag, {"rc": "NO-MARK rc=%s" % p.poll(), "extra": ""})
            return
        time.sleep(0.3)
        t1s = time.monotonic()
        os.kill(p.pid, first)
        time.sleep(gap)
        try:
            os.kill(p.pid, second)
        except ProcessLookupError:
            pass
        try:
            rc = p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            rc = "ALIVE"
        secs = round(time.monotonic() - t1s, 2)
        txt = out_lines(outp)
        sigl = [l for l in txt.splitlines() if l.startswith("SIGNAL\t")]
        report(tag, {"rc": rc, "secs": secs, "sigline": "y" if sigl else "n", "nsig": len(sigl),
                     "survivors": survivors(nonce), "tmpleft": tmp_left(rd),
                     "verdicts": sigl, "extra": ""})
    finally:
        reap(p, nonce)


def p_early():
    rd, repo, ledger, target = fresh("early")
    nonce = secrets.token_hex(8)
    env = base_env(rd, nonce)
    seen = {}
    for delay in (0.002, 0.005, 0.010, 0.030, 0.060, 0.120):
        for rep in range(8):
            p, fo, fe, outp, errp, t0, _ = launch(CAND, rd, ["--dry-run", repo, target], env)
            try:
                time.sleep(delay)
                try:
                    os.kill(p.pid, signal.SIGTERM)
                    sent = "y"
                except ProcessLookupError:
                    sent = "n"
                try:
                    rc = p.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    rc = "ALIVE"
                    p.kill(); p.wait()
                txt = out_lines(outp)
                surv = C.nonce_pids(nonce)
                if surv:
                    C.reap(nonce)
                key = (str(rc), "sig" if "SIGNAL\t" in txt else "nosig", sent, "ORPHANS=%d" % len(surv) if surv else "clean")
                seen[key] = seen.get(key, 0) + 1
            finally:
                C.reap(nonce)
                if p.poll() is None:
                    p.kill()
                p.wait()
                fo.close(); fe.close()
    report("early-term-burst", {"rc": ";".join(f"rc={k[0]},{'SIGNAL-line' if k[1]=='sig' else 'no-line'},sent={k[2]},{k[3]}x{v}"
                                               for k, v in sorted(seen.items())), "extra": ""})


def p_post_completion():
    rd, repo, ledger, target = fresh("postc")
    nonce = secrets.token_hex(8)
    env = base_env(rd, nonce)
    hits, misses, gone = [], 0, 0
    saved = {"n": 0}
    for rep in range(30):
        p, fo, fe, outp, errp, t0, _ = launch(CAND, rd, ["--dry-run", repo, target], env)
        try:
            hit = False
            while p.poll() is None:
                try:
                    with open(outp, "rb") as f:
                        if b"SUMMARY\t" in f.read():
                            hit = True
                            break
                except OSError:
                    pass
                time.sleep(0.0005)
            if hit:
                try:
                    os.kill(p.pid, signal.SIGTERM)
                except ProcessLookupError:
                    gone += 1
                try:
                    rc = p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    rc = "ALIVE"; p.kill(); p.wait()
                txt = out_lines(outp)
                hits.append((rc, "SIGNAL" if "SIGNAL\t" in txt else "nosig"))
                if rc == 143 and "SIGNAL\t" in txt and saved["n"] < 1:
                    saved["n"] += 1
                    for src, dst in ((outp, os.path.join(rd, "hit.out")), (errp, os.path.join(rd, "hit.err"))):
                        with open(src, "rb") as a, open(dst, "wb") as b:
                            b.write(a.read())
            else:
                misses += 1
                p.wait(timeout=15)
        finally:
            C.reap(nonce)
            if p.poll() is None:
                p.kill()
            p.wait()
            fo.close(); fe.close()
    from collections import Counter
    report("post-completion-term", {"rc": "%d/30 SUMMARY-seen; outcomes=%s" % (
        len(hits), dict(Counter(hits))), "extra": "tool-gone-before-kill=%d" % gone})


def p_escape(kind):
    rd, repo, ledger, target = fresh("escape-" + kind)
    sd = os.path.join(rd, "shim")
    if kind == "setsid":
        body = ('last=; for last in "$@"; do :; done\n'
                'if [[ $last == "$SOUJI_R80_TARGET" ]]; then r80_mark sha256sum "$@"\n'
                '  setsid sleep 600 </dev/null >/dev/null 2>&1 &\n'
                '  exec sleep 600\nfi\n')
    elif kind == "dfork":
        body = ('last=; for last in "$@"; do :; done\n'
                'if [[ $last == "$SOUJI_R80_TARGET" ]]; then r80_mark sha256sum "$@"\n'
                '  ( sleep 600 </dev/null >/dev/null 2>&1 & )\n'
                '  exec sleep 600\nfi\n')
    else:
        body = ('last=; for last in "$@"; do :; done\n'
                "if [[ $last == \"$SOUJI_R80_TARGET\" ]]; then r80_mark sha256sum \"$@\"\n"
                "  python3 -c 'import os; os.setpgid(0,0); os.execvp(\"sleep\", [\"sleep\", \"600\"])' "
                '</dev/null >/dev/null 2>&1 &\n'
                '  exec sleep 600\nfi\n')
    write_shim(sd, "sha256sum", body)
    nonce = secrets.token_hex(8)
    env = base_env(rd, nonce, shimdir=sd, target=target)
    p, fo, fe, outp, errp, t0, nonce = launch(CAND, rd, ["--dry-run", repo, target], env)
    try:
        if not wait_mark(env["SOUJI_R80_MARK"], p, t0):
            report("escape-" + kind, {"rc": "NO-MARK rc=%s" % p.poll(), "extra": ""})
            return
        time.sleep(0.3)
        t1s = time.monotonic()
        os.kill(p.pid, signal.SIGTERM)
        try:
            rc = p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            rc = "ALIVE"
        secs = round(time.monotonic() - t1s, 2)
        txt = out_lines(outp)
        sigl = [l for l in txt.splitlines() if l.startswith("SIGNAL\t")]
        surv = survivors(nonce)
        report("escape-" + kind, {"rc": rc, "secs": secs, "sigline": "y" if sigl else "n",
                                  "nsig": len(sigl), "survivors": surv, "tmpleft": tmp_left(rd),
                                  "verdicts": sigl, "extra": ""})
    finally:
        reap(p, nonce)


def p_spoof(kind):
    rd, repo, ledger, target = fresh("spoof-" + kind)
    sd = os.path.join(rd, "shim")
    write_shim(sd, "sha256sum", HANG_ON_TARGET)
    nonce = secrets.token_hex(8)
    extra = {}
    if kind == "worker-inline":
        extra["SOUJI_Q_WORKER"] = "1"
    elif kind == "worker-setsid":
        extra["SOUJI_Q_WORKER"] = "1"
    elif kind == "session":
        extra["SOUJI_Q_SESSION"] = str(os.getsid(0))
    env = base_env(rd, nonce, shimdir=sd, extra=extra, target=target)
    new_session = kind in ("worker-setsid",)
    p, fo, fe, outp, errp, t0, nonce = launch(CAND, rd, ["--dry-run", repo, target], env,
                                              new_session=new_session)
    try:
        errtxt = ""
        if kind == "worker-inline":
            rc = p.wait(timeout=30)
            with open(errp, "rb") as f:
                errtxt = f.read().decode("utf-8", "replace")[:200]
            report("spoof-" + kind, {"rc": rc, "extra": "stderr=%r" % errtxt.splitlines()[:1]})
            return
        if not wait_mark(env["SOUJI_R80_MARK"], p, t0):
            report("spoof-" + kind, {"rc": "NO-MARK rc=%s" % p.poll(), "extra": ""})
            return
        time.sleep(0.3)
        t1s = time.monotonic()
        os.kill(p.pid, signal.SIGTERM)
        try:
            rc = p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            rc = "ALIVE"
        secs = round(time.monotonic() - t1s, 2)
        txt = out_lines(outp)
        sigl = [l for l in txt.splitlines() if l.startswith("SIGNAL\t")]
        surv = survivors(nonce, settle=6.0)
        report("spoof-" + kind, {"rc": rc, "secs": secs, "sigline": "y" if sigl else "n",
                                 "nsig": len(sigl), "survivors": surv, "tmpleft": tmp_left(rd),
                                 "verdicts": sigl, "extra": ""})
    finally:
        reap(p, nonce)


MV_GATE = 'if [[ ${1:-} == --no-copy && $4 == "$SOUJI_R80_TARGET" ]]; then\n'


def p_stage2(phase):
    rd, repo, ledger, target = fresh("stage2-" + phase)
    sd = os.path.join(rd, "shim")
    real_mv = C.which("mv")
    if phase == "before":
        body = MV_GATE + '  r80_mark mv "$@"\n  exec sleep 600\nfi\n'
    else:
        mark2 = os.path.join(rd, "mv2.mark")
        body = (MV_GATE + '  r80_mark mv "$@"\n  %s "$@"\n'
                '  { printf "prog=mv-post\\n"; } > "$SOUJI_R80_MARK2"\n'
                "  exec sleep 600\nfi\n") % real_mv
    write_shim(sd, "mv", body)
    nonce = secrets.token_hex(8)
    env = base_env(rd, nonce, shimdir=sd, extra={"SOUJI_QUARANTINE_ALLOW_LIVE": "1"}, target=target)
    if phase == "after":
        env["SOUJI_R80_MARK2"] = os.path.join(rd, "mv2.mark")
    p, fo, fe, outp, errp, t0, nonce = launch(CAND, rd, ["--hold", "0", repo, target], env)
    try:
        mark = env["SOUJI_R80_MARK2"] if phase == "after" else env["SOUJI_R80_MARK"]
        if not wait_mark(mark, p, t0):
            report("stage2-sleep-" + phase, {"rc": "NO-MARK rc=%s" % p.poll(), "extra": ""})
            return
        time.sleep(0.3)
        t1s = time.monotonic()
        os.kill(p.pid, signal.SIGTERM)
        try:
            rc = p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            rc = "ALIVE"
        secs = round(time.monotonic() - t1s, 2)
        txt = out_lines(outp)
        sigl = [l for l in txt.splitlines() if l.startswith("SIGNAL\t")]
        qroot = os.path.join(repo, ".ufo-quarantine")
        qtree = []
        for dp, dns, fns in os.walk(qroot):
            qtree += [os.path.join(dp, n) for n in dns] + [os.path.join(dp, n) for n in fns]
        surv = survivors(nonce)
        report("stage2-sleep-" + phase, {
            "rc": rc, "secs": secs, "sigline": "y" if sigl else "n", "nsig": len(sigl),
            "survivors": surv, "tmpleft": tmp_left(rd),
            "src": "present" if os.path.exists(target) else "GONE",
            "qdir": str(len([q for q in qtree if os.path.isdir(q)])) + "dirs",
            "qpath": "present" if any(fns for dp, dns, fns in os.walk(qroot)) else "absent",
            "verdicts": sigl or ["(no SIGNAL)"],
            "extra": "qtree=%s last-out=%r" % (qtree, txt.splitlines()[-1:] )})
    finally:
        reap(p, nonce)


def p_stage3_hold():
    rd, repo, ledger, target = fresh("stage3-hold")
    nonce = secrets.token_hex(8)
    env = base_env(rd, nonce, extra={"SOUJI_QUARANTINE_ALLOW_LIVE": "1"})
    p, fo, fe, outp, errp, t0, nonce = launch(CAND, rd, ["--hold", "30", repo, target], env)
    try:
        hit = False
        while p.poll() is None and time.monotonic() - t0 < 60:
            if "QSTAGE\tstage3" in out_lines(outp):
                hit = True
                break
            time.sleep(0.02)
        if not hit:
            report("stage3-hold-signal", {"rc": "NO-STAGE3 rc=%s" % p.poll(), "extra": out_lines(outp)[-200:]})
            return
        t1s = time.monotonic()
        os.kill(p.pid, signal.SIGTERM)
        try:
            rc = p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            rc = "ALIVE"
        secs = round(time.monotonic() - t1s, 2)
        txt = out_lines(outp)
        sigl = [l for l in txt.splitlines() if l.startswith("SIGNAL\t")]
        qroot = os.path.join(repo, ".ufo-quarantine")
        qfiles = [os.path.join(dp, f) for dp, dns, fns in os.walk(qroot) for f in fns]
        report("stage3-hold-signal", {
            "rc": rc, "secs": secs, "sigline": "y" if sigl else "n", "nsig": len(sigl),
            "survivors": survivors(nonce), "tmpleft": tmp_left(rd),
            "src": "present" if os.path.exists(target) else "GONE",
            "qpath": "present" if qfiles else "absent",
            "verdicts": [l for l in txt.splitlines() if l.startswith(("RESULT", "QSTAGE\tstage3"))],
            "extra": ""})
    finally:
        reap(p, nonce)


SCENARIOS = {
    "baseline": p_baseline,
    "between": p_between_targets,
    "term-int": lambda: p_double(signal.SIGTERM, signal.SIGINT, 0.001, "term-then-int"),
    "term-term": lambda: p_double(signal.SIGTERM, signal.SIGTERM, 0.001, "term-then-term"),
    "early": p_early,
    "postc": p_post_completion,
    "esc-setsid": lambda: p_escape("setsid"),
    "esc-dfork": lambda: p_escape("dfork"),
    "esc-setpgid": lambda: p_escape("setpgid"),
    "spoof-worker-inline": lambda: p_spoof("worker-inline"),
    "spoof-worker-setsid": lambda: p_spoof("worker-setsid"),
    "spoof-session": lambda: p_spoof("session"),
    "stage2-before": lambda: p_stage2("before"),
    "stage2-after": lambda: p_stage2("after"),
    "stage3-hold": p_stage3_hold,
}

if __name__ == "__main__":
    for name in sys.argv[1:]:
        SCENARIOS[name]()
