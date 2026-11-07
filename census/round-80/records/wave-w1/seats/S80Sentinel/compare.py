import importlib.util, os, pty, select, signal, subprocess, sys, time, json
sys.path.insert(0, "/fast/scratch/hyaku/souji-r80/S80Sentinel")
import probe2 as P

m = P.load_counter()

def run_one(tool, tag):
    rowdir, fleet, repo, ledger, target = P.new_case(m, tag)
    tmpdir = os.path.join(rowdir, "tmp"); os.makedirs(tmpdir)
    env = P.env_for()
    env.update({"TMPDIR": tmpdir, "SOUJI_VERIFY_BIN": P.STUB_SAFE, "SOUJI_Q_SHOKUNIN_ROOT": fleet,
                "SOUJI_Q_LEDGER": ledger})
    p = subprocess.run(["bash", tool, "--dry-run", repo, target], capture_output=True, env=env,
                       stdin=subprocess.DEVNULL, start_new_session=True, cwd=rowdir)
    return {"tag": tag, "rc": p.returncode,
            "out": p.stdout.decode("utf-8", "replace").replace(rowdir, "CASE"),
            "err": p.stderr.decode("utf-8", "replace").replace(rowdir, "CASE"),
            "tmp_after": sorted(os.listdir(tmpdir))}

a = run_one("/fast/scratch/hyaku/souji-r80/S80Sentinel/base.sh", "cmp-base")
b = run_one("/fast/scratch/hyaku/souji-r80/S80Sentinel/tool.sh", "cmp-cand")
print(json.dumps([a, b], indent=1))
print("OUT_IDENTICAL", a["out"] == b["out"], "RC_IDENTICAL", a["rc"] == b["rc"],
      "ERR_IDENTICAL", a["err"] == b["err"])
