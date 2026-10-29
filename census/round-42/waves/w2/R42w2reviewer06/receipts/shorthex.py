import subprocess, re, sys
TIP = "3105a63b23481fccf7df58e74d14a6681e0ea0c8"
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
ranges = {"LOG.md": (1922, 1933), "SCORECARD.md": (840, 865), "SKILL.md": (287, 292),
          "corpus/QUALITY.md": (259, 266), "corpus/README.md": (811, 821), "corpus/SOURCES.md": (213, 213)}
hx = re.compile(r'(?<![0-9A-Za-z_/.\-])[0-9a-f]{7,40}(?![0-9A-Za-z_/.\-])')
n = 0
for f, (a, b) in ranges.items():
    out = subprocess.run(["git", "-C", LANE, "show", f"{TIP}:{f}"], capture_output=True, text=True)
    lines = out.stdout.split("\n")
    for ln in range(a, b + 1):
        for h in sorted(set(hx.findall(lines[ln - 1]))):
            if h.isdigit():
                continue
            n += 1
            r = subprocess.run(["git", "-C", LANE, "rev-parse", "--verify", "-q", h + "^{commit}"],
                               capture_output=True, text=True).stdout.strip()
            print(f"{f}:{ln} {h} -> {'commit ' + r[:12] if r else 'NO-COMMIT'}")
print("tokens checked:", n)
sys.stdout.flush()
