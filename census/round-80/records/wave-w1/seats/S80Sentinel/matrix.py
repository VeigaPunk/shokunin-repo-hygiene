import json, os, signal, sys, time
sys.path.insert(0, "/fast/scratch/hyaku/souji-r80/S80Sentinel")
import probe2 as P

m = P.load_counter()
MON = {"SHELLOPTS": "braceexpand:hashall:interactive-comments:monitor"}
variants = [("plain", False, {}), ("new_nomon", True, {}), ("new_mon", True, MON),
            ("plain_mon", False, MON)]
res = []
for tag, ns, extra in variants:
    rowdir, fleet, repo, ledger, target = P.new_case(m, "mx-" + tag)
    tmpdir = os.path.join(rowdir, "tmp"); os.makedirs(tmpdir)
    log = os.path.join(rowdir, "stub.log")
    env = P.env_for()
    env.update({"TMPDIR": tmpdir, "SOUJI_VERIFY_BIN": P.STUB_HANG, "SOUJI_S80_STUB_LOG": log,
                "SOUJI_Q_SHOKUNIN_ROOT": fleet, "SOUJI_Q_LEDGER": ledger})
    env.update(extra)
    outp = os.path.join(rowdir, "out"); errp = os.path.join(rowdir, "err")
    with open(outp, "wb") as fo, open(errp, "wb") as fe:
        p = P.subprocess.Popen(["bash", P.TOOL, "--dry-run", repo, target], stdout=fo, stderr=fe,
                               stdin=P.subprocess.DEVNULL, env=env, start_new_session=ns, cwd=rowdir)
    time.sleep(0.6)
    tree = []
    for x in P.tool_pids():
        f = P.stat_fields(x)
        if f:
            tree.append({"pid": x, "ppid": int(f[1]), "pgrp": int(f[2]), "sid": int(f[3])})
    stub = os.path.exists(log) and os.path.getsize(log) > 0
    priv = [x for x in os.listdir(tmpdir) if x.startswith("souji-quarantine.")]
    if p.poll() is None:
        try:
            os.kill(p.pid, signal.SIGTERM)
        except OSError:
            pass
    try:
        p.wait(timeout=8)
    except P.subprocess.TimeoutExpired:
        p.kill(); p.wait()
    out = P.read_text(outp); err = P.read_text(errp)
    res.append({"variant": tag, "new_session": ns, "monitor_env": bool(extra),
                "front": p.pid, "rc": p.returncode,
                "tree_at_0.6s": tree, "stub_reached_0.6s": stub, "priv_at_0.6s": priv,
                "out_lines": len(out.splitlines()), "out_first": out.splitlines()[:1],
                "signal_line": [l for l in out.splitlines() if l.startswith("SIGNAL\t")],
                "err_tail": err[-200:], "tmp_after": sorted(os.listdir(tmpdir))})
    P.cleanup()
print(json.dumps(res, indent=1))
