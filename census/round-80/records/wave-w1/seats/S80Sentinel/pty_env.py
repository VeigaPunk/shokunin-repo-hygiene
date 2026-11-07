import json, os, pty, select, time
env = {"PATH": os.environ["PATH"], "PS1": "@@@ ", "TERM": "dumb"}
pid, master = pty.fork()
if pid == 0:
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
                return
            if not c:
                return
            buf += c
pump(1.0)
os.write(master, b"env | grep '^SHELLOPTS='; echo MARK-END\n")
pump(1.0)
os.write(master, b"exit\n")
pump(0.5)
try: os.waitpid(pid, 0)
except ChildProcessError: pass
txt = buf.decode("utf-8", "replace")
print(json.dumps({"exported_shellopts": [l for l in txt.splitlines() if l.startswith("SHELLOPTS=")],
                  "raw_tail": txt[-300:]}, indent=1))
