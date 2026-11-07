#!/usr/bin/env python3
"""S78ExecEvade (r78): routes OUTSIDE the 17 frozen rows vs W gate (ed22dc9c) and base gate (a8558d41).
Runs both gates per route, own session, 60 s row bound, kill group on expiry.
"""
import argparse, concurrent.futures, importlib.util, os, signal, subprocess, sys, time

sys.dont_write_bytecode = True
PROBE = "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-74/records/wave-repair/probes/evade-probe.py"
spec = importlib.util.spec_from_file_location("souji_r74_evade_probe", PROBE)
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
CLASSES = ("RECEIPT-NONREGULAR-GITSOURCE", "RECEIPT-GIT-TIMEOUT", "RECEIPT-NONREGULAR-SOURCE")


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def fifo(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path) or os.path.islink(path):
        os.remove(path)
    os.mkfifo(path)


def cfg(c, *args):
    P.git(c, "config", *args)


# ---- route mutators (c=clone, w=rowdir) ----
def r_adv_alt(c, w):
    p = os.path.join(c, ".git", "objects", "info", "alternates")
    fifo(p)


def r_adv_loose_ref(c, w):
    import shutil
    shutil.rmtree(os.path.join(c, ".git", "refs", "heads"))
    fifo(os.path.join(c, ".git", "refs", "heads", "master"))


def r_adv_shallow(c, w):
    fifo(os.path.join(c, ".git", "shallow"))


def r_adv_gitfile_fifo_cfg(c, w):
    real = os.path.join(w, "realgit")
    import shutil
    if os.path.exists(real): shutil.rmtree(real)
    os.rename(os.path.join(c, ".git"), real)
    write(os.path.join(real, "commondir"), b"\n")
    fifo(os.path.join(real, "config"))
    write(os.path.join(c, ".git"), b"gitdir: " + real.encode() + b"\n")


def r_adv_gitfile_fifo(c, w):
    import shutil
    shutil.rmtree(os.path.join(c, ".git"))
    fifo(os.path.join(c, ".git"))


def r_adv_worktree_common_cfg(c, w):
    # lane becomes a linked worktree; FIFO in the COMMON dir config
    wt = os.path.join(w, "linked")
    P.git(c, "worktree", "add", "-q", wt, "-b", "linkedbranch")
    common = P.git(wt, "rev-parse", "--git-common-dir").stdout.strip().decode()
    if not os.path.isabs(common):
        common = os.path.normpath(os.path.join(wt, common))
    fifo(os.path.join(common, "config"))


def r_adv_incl_tilde(c, w):
    f = os.path.join(w, "inc.cfg")
    write(f, b"[include]\n\tpath = ~/inc-secret.cfg\n")
    fifo(os.path.join(w, "home", "inc-secret.cfg"))
    cfg(c, "include.path", f)


def r_adv_incl_leading_space(c, w):
    f = os.path.join(w, "inc.cfg")
    write(f, b'[include]\n\tpath = " /abs-fifo-placeholder"\n')
    # git resolves " /abs-fifo-placeholder" to <dir>/ /abs-fifo-placeholder = <dir>/<space>/abs-fifo-placeholder
    space_dir = os.path.join(w, " ")
    os.makedirs(space_dir, exist_ok=True)
    fifo(os.path.join(space_dir, "abs-fifo-placeholder"))
    cfg(c, "include.path", f)


def r_adv_incl_newline(c, w):
    f = os.path.join(w, "inc.cfg")
    p = os.path.join(w, "abs-fifo-placeholder2")
    write(f, ('[include]\n\tpath = "x\n%s"\n' % p).encode())
    fifo(p)
    cfg(c, "include.path", f)


def r_adv_incl_cycle(c, w):
    a = os.path.join(w, "a.cfg"); b = os.path.join(w, "b.cfg")
    write(a, ("[include]\n\tpath = %s\n" % b).encode())
    write(b, ("[include]\n\tpath = %s\n" % a).encode())
    cfg(c, "include.path", a)


def r_adv_incl_chain12(c, w):
    cur = os.path.join(w, "c0.cfg")
    write(cur, ("[include]\n\tpath = %s\n" % os.path.join(w, "c1.cfg")).encode())
    for i in range(1, 12):
        nxt = os.path.join(w, "c%d.cfg" % (i + 1)) if i < 12 else None
        write(os.path.join(w, "c%d.cfg" % i),
              (("[include]\n\tpath = %s\n" % nxt) if nxt else "").encode())
    write(os.path.join(w, "c12.cfg"), b"")
    fifo(os.path.join(w, "c12.cfg")) if False else None
    # final level: c11 points at FIFO at c12 position — replace c12 with fifo
    os.remove(os.path.join(w, "c12.cfg")); fifo(os.path.join(w, "c12.cfg"))
    cfg(c, "include.path", cur)


def r_adv_incl_onbranch(c, w):
    f = os.path.join(w, "fifo-onbranch")
    fifo(f)
    cfg(c, "includeIf.onbranch:master.path", f)


def r_adv_incl_hasconfig(c, w):
    f = os.path.join(w, "fifo-hasconfig")
    fifo(f)
    cfg(c, "includeIf.hasconfig:remote.*.url.path", f)


def r_adv_hooks_in_included(c, w):
    f = os.path.join(w, "inc.cfg")
    write(f, b"[core]\n\thooksPath = %s\n\tfsmonitor = %s\n" % (
        os.path.join(w, "hooks").encode(), os.path.join(w, "fsmonitor-pipe").encode()))
    fifo(os.path.join(w, "fsmonitor-pipe"))
    cfg(c, "include.path", f)


def r_adv_xdg_attr(c, w):
    fifo(os.path.join(w, "xdg", "git", "attributes"))
def r_adv_remote_head_fifo(c, w):
    os.remove(os.path.join(w, "origin.git", "HEAD"))
    fifo(os.path.join(w, "origin.git", "HEAD"))


# ---- runner ----
BOUND = int(os.environ.get("BOUND", "60"))
def run_gate(gate, lane, report, prereg, extra, bound=None):
    bound = bound or BOUND
    env = P.env_clean(extra)
    t0 = time.monotonic()
    p = subprocess.Popen(["bash", gate, "--lane", lane, "--branch", "master",
                          "--report", report, "--prereg", prereg],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         stdin=subprocess.DEVNULL, env=env, start_new_session=True,
                         cwd=None)
    try:
        out, err = p.communicate(timeout=bound)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        p.communicate()
        return ("HANG", -1, "-", time.monotonic() - t0, "")
    text = out.decode("utf-8", "replace") + err.decode("utf-8", "replace")
    fails = [l for l in text.splitlines() if l.startswith("check-") and l.endswith("=FAIL")]
    if p.returncode == 0 and not fails:
        verdict = "PASS"
    elif p.returncode == 1 and fails:
        verdict = "FAIL"
    else:
        verdict = "ODD"
    cls = "-"
    for x in CLASSES:
        if x in text:
            cls = x
            break
    return (verdict, p.returncode, cls, time.monotonic() - t0, text)


ROUTES = [
    ("a-alternates-fifo", r_adv_alt, (), "clone"),
    ("b-loose-ref-fifo", r_adv_loose_ref, (), "clone"),
    ("c-shallow-fifo", r_adv_shallow, (), "clone"),
    ("d-gitfile-fifo-config", r_adv_gitfile_fifo_cfg, (), "clone"),
    ("d2-gitfile-itself-fifo", r_adv_gitfile_fifo, (), "clone"),
    ("e-worktree-common-config-fifo", r_adv_worktree_common_cfg, (), "linked"),
    ("f1-include-tilde", r_adv_incl_tilde, ("HOMEENV",), "clone"),
    ("f2-include-leading-space", r_adv_incl_leading_space, (), "clone"),
    ("f3-include-newline", r_adv_incl_newline, (), "clone"),
    ("g1-include-cycle", r_adv_incl_cycle, (), "clone"),
    ("g2-include-chain12", r_adv_incl_chain12, (), "clone"),
    ("h1-includeIf-onbranch", r_adv_incl_onbranch, (), "clone"),
    ("h2-includeIf-hasconfig", r_adv_incl_hasconfig, (), "clone"),
    ("i-hooks-fsmonitor-in-included", r_adv_hooks_in_included, (), "clone"),
    ("j-xdg-attributes-fifo-no-home", r_adv_xdg_attr, ("XDGENV",), "clone"),
    ("k-remote-head-fifo", r_adv_remote_head_fifo, (), "clone"),
]


def one(job):
    rid, mutate, extra_keys, lane_kind, gates, work = job
    rowdir = os.path.join(work, rid)
    try:
        clone, report, prereg = P.build(rowdir)
        envm = {}
        for k in extra_keys:
            if k == "HOMEENV":
                envm["HOME"] = os.path.join(rowdir, "home")
            elif k == "XDGENV":
                envm["XDG_CONFIG_HOME"] = os.path.join(rowdir, "xdg")
        os.makedirs(os.path.join(rowdir, "home"), exist_ok=True)
        os.makedirs(os.path.join(rowdir, "xdg"), exist_ok=True)
        mutate(clone, rowdir)
        lane = clone
        if lane_kind == "linked":
            lane = os.path.join(rowdir, "linked")
        res = {}
        for tag, gate in gates:
            res[tag] = run_gate(gate, lane, report, prereg, envm)
        return (rid, res, None)
    except Exception as e:  # noqa
        import traceback
        return (rid, None, traceback.format_exc()[-600:])


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--gate-w", required=True)
    ap.add_argument("--gate-base", required=True)
    ap.add_argument("--only", default=None)
    a = ap.parse_args(argv)
    os.makedirs(a.work, exist_ok=True)
    jobs = []
    for rid, mutate, extra, kind in ROUTES:
        if a.only and rid != a.only:
            continue
        jobs.append((rid, mutate, extra, kind, [("W", a.gate_w), ("B", a.gate_base)], a.work))
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        for rid, res, err in ex.map(one, jobs, chunksize=1):
            if err:
                print(f"{rid}\tBUILD-ERROR\t{err}", flush=True)
                continue
            for tag in ("W", "B"):
                v, rc, cls, secs, text = res[tag]
                checks = ",".join(l for l in text.splitlines() if l.startswith("check-"))
                print(f"{rid}\t{tag}\tverdict={v}\trc={rc}\tclass={cls}\tsecs={secs:.1f}\t{checks}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
