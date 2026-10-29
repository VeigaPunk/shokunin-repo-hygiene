# P2 probe: token-by-token diff of each frozen Target line against the counter's printed SUMMARY (receipts/<n>.out).
import re, sys, os
lane, rdir = sys.argv[1], sys.argv[2]
pre = open(os.path.join(lane, "census/round-42/preregistration.txt"), encoding="utf-8").read().splitlines()
pairs = {20: "01-c1-tip", 30: "02-c2-tip", 41: "03-c3-tip", 51: "04-r1-tip"}
for ln, rn in sorted(pairs.items()):
    tgt = re.match(r"^Target: (.*)$", pre[ln - 1]).group(1)
    lines = open(os.path.join(rdir, rn + ".out"), encoding="utf-8", errors="replace").read().splitlines()
    summ = [l for l in lines if l.startswith("SUMMARY ")]
    actual = summ[-1] if summ else ""
    tt = tgt.replace(" over the landed lane tip", "").split()
    at = actual.split()
    print("prereg:%d Target=%r" % (ln, tgt))
    print("  printed=%r" % actual)
    print("  Target tokens the counter did not print: %s" % [t for t in tt if t not in at])
    print("  printed tokens absent from Target: %s" % [t for t in at if t not in tt])
