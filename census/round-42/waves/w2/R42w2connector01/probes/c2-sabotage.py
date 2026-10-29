# P10 probe: writes three single-logic sabotages of the landed C2 tool into a directory (argv: orig, outdir).
import sys, os
src = open(sys.argv[1], encoding="utf-8").read()
out = sys.argv[2]
cases = {
 "digest-inverted": ("hexdigest()", "hexdigest()[::-1]", None),
 "freeze-none": ("def freeze_rev(repo, rev, prereg):", "def freeze_rev(repo, rev, prereg):\n    return None\n", 1),
 "ancestry-inverted": ('return self.run("merge-base", "--is-ancestor", a, b).returncode == 0',
                       'return self.run("merge-base", "--is-ancestor", a, b).returncode != 0', 1),
}
for name, (old, new, want) in cases.items():
    c = src.count(old)
    if want is not None and c != want:
        raise SystemExit("anchor %s occurs %d times, expected %d" % (name, c, want))
    open(os.path.join(out, name + ".py"), "w", encoding="utf-8").write(src.replace(old, new))
    print("mutant %s anchor-count=%d" % (name, c))
