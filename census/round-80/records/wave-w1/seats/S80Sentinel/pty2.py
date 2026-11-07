import json, os, pty, select, sys, time
sys.path.insert(0, "/fast/scratch/hyaku/souji-r80/S80Sentinel")
import probe2 as P

m = P.load_counter()
rowdir, fleet, repo, ledger, target = P.new_case(m, "pty-interactive2")
tmpdir = os.path.join(rowdir, "tmp"); os.makedirs(tmpdir)
log = os.path.join(rowdir, "stub.log")
env = P.env_for()
env.update({"TMPDIR": tmpdir, "SOUJI_VERIFY_BIN": P.STUB_HANG, "SOUJI_S80_STUB_LOG": log,
            "SOUJI_Q_SHOKUNIN_ROOT": fleet, "SOUJI_Q_LEDGER": ledger,
            "PS1": "@@@ ", "TERM": "dumb"})
open(os.path.join(rowdir, "case.env"), "w").write("")
pid, master = pty.fork()
if pid == 0:
    os.chdir(rowdir)
    os.execvpe("bash", ["bash", "--norc", "--noprofile", "-i"], env)
os.set_blocking(master, False)
buf = b""
def pump(t):
    global buf
    end = time.time() + t
    while time.time() < end:
        r, _, _ = select.select([master], [], [], 0.05)
        if r:
            try:
                c = os.read(master, 65536)
            except OSError:
                return False
            if not c:
                return False
            buf += c
    return True

pump(1.5)
os.write(master, b"echo SHELLOPTS=$SHELLOPTS; set -o | grep '^monitor'\n")
pump(1.0)
os.write(master, ("bash " + P.TOOL + " --dry-run " + repo + " " + target + "; echo RC=$?\n").encode())
pump(6.0)
snap_tool = P.tool_pids()
snap_tmp = sorted(os.listdir(tmpdir))
snap_tree = []
for x in snap_tool:
    f = P.stat_fields(x)
    if f:
        snap_tree.append({"pid": x, "state": f[0].decode(), "ppid": int(f[1]), "pgrp": int(f[2]),
                          "sid": int(f[3]), "argv": P.argv_of(x)[:80]})
snap_stub = [x for x in P.tool_pids() if "stub-hang" in P.argv_of(x)]
os.write(master, b"exit\n")
pump(1.0)
try:
    os.waitpid(pid, 0)
except ChildProcessError:
    pass
pump(0.5)
time.sleep(0.5)
res = {"shellopts_line": [l for l in buf.decode("utf-8", "replace").splitlines() if "SHELLOPTS" in l or "monitor" in l],
       "rc_lines": [l for l in buf.decode("utf-8", "replace").splitlines() if l.startswith("RC=")],
       "tool_pids_at_6s": snap_tree, "tmp_at_6s": snap_tmp, "stub_reached": os.path.exists(log),
       "tmp_after_shell_exit": sorted(os.listdir(tmpdir)),
       "tool_pids_final": P.tool_pids(), "output_tail": buf.decode("utf-8", "replace")[-900:]}
res["killed_at_cleanup"] = P.cleanup()
res["tool_pids_after_cleanup"] = P.tool_pids()
print(json.dumps(res, indent=1))
