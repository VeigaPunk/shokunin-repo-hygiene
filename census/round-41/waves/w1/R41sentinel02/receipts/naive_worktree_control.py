# positive control for the strace harness: a deliberately naive worktree reader (scratch only)
import argparse, hashlib, os, re
ap = argparse.ArgumentParser()
for flag in ("--root", "--prereg", "--rev"):
    ap.add_argument(flag, required=True)
a = ap.parse_args()
text = open(os.path.join(a.root, a.prereg), "rb").read().decode("utf-8", "replace")
for key in ("Counter", "Population", "Control"):
    for m in re.finditer(r"^%s:[ \t]*(.*)$" % key, text, re.M):
        path = m.group(1).split(" sha256=")[0].strip()
        try:
            data = open(os.path.join(a.root, path), "rb").read(1 << 20)
            print("READ %s sha=%s" % (path, hashlib.sha256(data).hexdigest()[:12]))
        except Exception as e:
            print("EXC %s %s" % (type(e).__name__, path))
print("SUMMARY claims=1 findings=0")
