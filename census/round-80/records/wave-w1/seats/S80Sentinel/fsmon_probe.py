import json, os, subprocess, sys
sys.path.insert(0, "/fast/scratch/hyaku/souji-r80/S80Sentinel")
import probe2 as P

m = P.load_counter()
out = {}
for tag, tool in (("base", os.path.join(P.BASE, "base.sh")), ("cand", P.TOOL)):
    rowdir, fleet, repo, ledger, target = P.new_case(m, "fsmon-" + tag)
    # tracked target so the tool's git status paths see a real tree
    subprocess.run(["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@t",
                    "add", "-A"], check=True)
    subprocess.run(["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@t",
                    "commit", "-qm", "init"], check=True)
    marker = os.path.join(rowdir, "fsmon-marker")
    hook = os.path.join(rowdir, "fsmon.sh")
    with open(hook, "w") as f:
        f.write("#!/bin/sh\nprintf 'RAN %s\\n' \"$*\" >> " + marker + "\nexit 0\n")
    os.chmod(hook, 0o755)
    subprocess.run(["git", "-C", repo, "config", "core.fsmonitor", hook], check=True)
    tmpdir = os.path.join(rowdir, "tmp"); os.makedirs(tmpdir)
    env = P.env_for()
    env.update({"TMPDIR": tmpdir, "SOUJI_VERIFY_BIN": P.STUB_SAFE,
                "SOUJI_Q_SHOKUNIN_ROOT": fleet, "SOUJI_Q_LEDGER": ledger})
    p = subprocess.run(["bash", tool, "--dry-run", repo, target], capture_output=True, env=env,
                       stdin=subprocess.DEVNULL, start_new_session=True, cwd=rowdir)
    out[tag] = {"rc": p.returncode, "marker": P.read_text(marker).strip() or "absent",
                "stdout_head": p.stdout.decode("utf-8", "replace").splitlines()[:3]}
print(json.dumps(out, indent=1))
