import sys
sys.path.insert(0, "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-41/w1/R41sentinel02")
import attack_fixtures as A
ctl = "/fast/scratch/hyaku/souji-r41/R41sentinel02/control/naive_worktree_control.py"
cases = {c["name"]: c for c in [{"name": "trav-counter-rel", "dir": A.FX + "/trav-counter-rel", "arg": "prereg.txt", "tip": A.git(A.FX + "/trav-counter-rel", "rev-parse", "HEAD").stdout.decode().strip(), "accept": A.ANY}]}
import json
r = A.run_candidate("naive-control", ctl, cases["trav-counter-rel"], "positive")
print(json.dumps({k: r[k] for k in ("rc", "escape_opens", "worktree_opens", "shell_execs", "verdict", "stdout_head")}, indent=1))
