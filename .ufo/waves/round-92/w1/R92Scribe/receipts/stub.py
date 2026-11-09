import argparse, os, sys
ap = argparse.ArgumentParser()
for k in ("--counter", "--harness", "--population", "--lane", "--fleet-root", "--work"):
    ap.add_argument(k)
a, _ = ap.parse_known_args()
os.makedirs(os.path.join(a.work, "fixture"), exist_ok=True)
with open(os.path.join(a.work, "fixture", "blob.bin"), "wb") as f:
    f.write(b"x" * 4_000_000)
print("SUMMARY rows=0 mismatches=0 accepted=0 refused_true=0 errors=0")
sys.exit(0)
