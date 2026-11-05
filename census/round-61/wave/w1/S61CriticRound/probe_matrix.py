import os, subprocess, sys
S = os.environ["S"]
sys.path.insert(0, S)
import importlib.util
spec = importlib.util.spec_from_file_location("p", os.path.join(S, "probe_chrono.py"))
src = open(os.path.join(S, "probe_chrono.py")).read().split("results = []")[0]
ns = {"S": S}
exec(compile(src, "probe_chrono_head", "exec"), ns)
literal_rule, fixed_rule, ancestor = ns["literal_rule"], ns["fixed_rule"], ns["ancestor"]
for case in ["honest-1", "honest-2", "honest-3", "forgery-kind-only", "forgery-digest", "forgery-rev-at-freeze", "forgery-rev-missing", "forgery-command-other"]:
    d = os.path.join(S, "build60", "repos", case)
    freeze = subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    ctls = [f for f in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "deliv60", "matrix", case)) if f.startswith("ctl") and f.endswith(".txt")]
    for c in sorted(ctls):
        print("%-24s %-14s literal=%-60s F''=%s" % (case, c, literal_rule(d, freeze, freeze, c), fixed_rule(d, freeze, c)))
