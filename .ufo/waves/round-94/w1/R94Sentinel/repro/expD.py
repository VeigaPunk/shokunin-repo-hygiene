import importlib.util, os, subprocess, sys
LANE="/home/vgpnk/Projects/shokunin/souji-shokunin"
spec=importlib.util.spec_from_file_location("c1s", os.path.join(LANE,"census/round-94/c1-survivor-search.py"))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
S="/fast/scratch/hyaku/souji-r94/R94Sentinel"

# The r93 harness's rc==2 error-row format, verbatim (census/round-93/c1-false-row-harness.py:467):
#   ROW {rid} ... got=- rc=2 match=error detail={p.stderr.decode()[:200]!r}
# The r94 verdict() keys on the SUBSTRING " rc=70 match=" inside any ROW line.
def row(detail):
    return (f"ROW LD6 where=ledger-trim rev=BASE item=P04 class=- expect=MOVED/0 got=- rc=2 match=error "
            f"detail={detail!r}\nROW NF1 where=lane rev=BASE item=P19 class=TOKEN expect=REFUSED/- got=REFUSED "
            f"rc=1 match=no\nSUMMARY rows=66 mismatches=1 accepted=0 refused_true=0 errors=1\n").encode()
benign = "C2-COUNTER-FATAL: population is not 5 well-formed rows"
injected = "harmless rc=70 match=no text"
print("baseline  (rc=2 row, no injection) ->", m.verdict(1, row(benign)))
print("INJECTED  (counter stderr carries ' rc=70 match=') ->", m.verdict(1, row(injected)))
print()
# can a real counter's stderr carry it? the r87 counter's stderr texts:
src=open(os.path.join(LANE,"census/round-87/c1-pointer-counter.py")).read()
import re
for t in re.findall(r'print\(f?"([^"]*C2-COUNTER-FATAL[^"]*)"', src):
    print("counter stderr text:", t)
