import os, sys, time, hashlib, subprocess
a = sys.argv[1:]
root, rev, instr, out = (a[a.index(k) + 1] for k in ("--root", "--rev", "--instrument", "--out"))
cmd = a[a.index("--") + 1:]
p = subprocess.run(cmd, capture_output=True)
sha = hashlib.sha256(subprocess.run(["git", "-C", root, "show", rev + ":" + instr], capture_output=True).stdout).hexdigest()
f = open(out, "w")                        # truncate-in-place, NOT atomic: no temp, no rename
f.write("instrument=%s\ninstrument_sha256=%s\nrev=%s\n" % (instr, sha, rev)); f.flush()
time.sleep(0.6)                           # partial OUT is visible during this window
f.write("command=%s\n%sEXIT=%d\n" % (" ".join(cmd), p.stdout.decode(), p.returncode)); f.close()
sys.exit(p.returncode)
