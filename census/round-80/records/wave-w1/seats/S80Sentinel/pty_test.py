import os, pty, select, signal, sys, time, json
sys.path.insert(0, "/fast/scratch/hyaku/souji-r80/S80Sentinel")
import probe2 as P

m = P.load_counter()
rowdir, fleet, repo, ledger, target = P.new_case(m, "pty-int")
tmpdir = os.path.join(rowdir, "tmp"); os.makedirs(tmpdir)
log = os.path.join(rowdir, "stub.log")
env = P.env_for()
env.update({"TMPDIR": tmpdir, "SOUJI_VERIFY_BIN": P.STUB_HANG, "SOUJI_S80_STUB_LOG": log,
            "SOUJI_Q_SHOKUNIN_ROOT": fleet, "SOUJI_Q_LEDGER": ledger})
argv = ["bash", P.TOOL, "--dry-run", repo, target]
pid, master = pty.fork()
if pid == 0:
    os.chdir(rowdir)
    os.execvpe(argv[0], argv, env)
os.set_blocking(master, False)
buf = b""
stub = None
t0 = time.time()
while time.time() - t0 < 20:
    r, _, _ = select.select([master], [], [], 0.05)
    if r:
        try:
            buf += os.read(master, 65536)
        except OSError:
            break
    if os.path.exists(log) and os.path.getsize(log) > 0:
        stub = int(P.read_text(log).splitlines()[0].split("\t")[0])
        break
fg = None
try:
    fg = os.tcgetpgrp(master)
except OSError:
    pass
res = {"pty_fg_pgid": fg, "child_pid": pid, "stub": stub,
       "front_sid": P.proc_sid(pid), "front_is_fg": fg == pid}
if stub:
    time.sleep(0.3)
    os.write(master, b"\x03")   # ^C -> SIGINT to the pty's foreground process group
t1 = time.time()
while time.time() - t1 < 10:
    print_status = os.waitpid(pid, os.WNOHANG)
    if print_status != (0, 0):
        break
    r, _, _ = select.select([master], [], [], 0.05)
    if r:
        try:
            buf += os.read(master, 65536)
        except OSError:
            break
try:
    _, status = os.waitpid(pid, 0)
except ChildProcessError:
    status = None
time.sleep(0.3)
try:
    while True:
        chunk = os.read(master, 65536)
        if not chunk:
            break
        buf += chunk
except OSError:
    pass
res.update({"status": status, "rc": os.waitstatus_to_exitcode(status) if status is not None else None,
            "output": buf.decode("utf-8", "replace")[-800:],
            "stub_alive_after": bool(stub and P.alive(stub)),
            "tmp_after": sorted(os.listdir(tmpdir)),
            "tool_pids_after": P.tool_pids()})
res["killed_at_cleanup"] = P.cleanup()
print(json.dumps(res, indent=1))
