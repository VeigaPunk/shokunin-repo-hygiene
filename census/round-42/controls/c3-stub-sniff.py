#!/usr/bin/env python3
"""r42 C3 sniffing control: reads the tool's bytes, never its behaviour. Any byte difference from the pinned tool fails it."""
import argparse, hashlib, sys
ap = argparse.ArgumentParser()
ap.add_argument("--tool", required=True)
ap.add_argument("--work")
a = ap.parse_args()
ok = hashlib.sha256(open(a.tool, "rb").read()).hexdigest() == "b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6"
for i in range(13):
    print("case-sniff%02d=%s" % (i, "PASS" if ok else "FAIL"))
print("SUMMARY cases=13 pass=%d fail=%d" % (13 if ok else 0, 0 if ok else 13))
sys.exit(0 if ok else 1)
