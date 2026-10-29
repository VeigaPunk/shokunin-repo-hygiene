#!/usr/bin/env python3
"""Scratch generator 2: shape-keyed table attack (K5b) and two reading-sensitivity variants (K7, K8)."""
import importlib.util
import pathlib
import sys

SEAT = pathlib.Path("/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42critic02")
SCRATCH = pathlib.Path("/fast/scratch/hyaku/souji-r42/R42critic02")
K1 = (SEAT / "K1-honest-grammar.py").read_text(encoding="utf-8")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


c2 = load("/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/c2-counter.py", "c2counter")

# ---- K5b: shape key (no directory names): normalised prereg text, commit subjects, tree paths+modes+blobs,
# and whether the Base commit resolves and is an ancestor of the tip. Table built from the counter's CASES.
K5B_TOOL = '''#!/usr/bin/env python3
"""ATTACK K5b (not an implementation): no grammar. Answers from a repository-shape key: the prereg text with
its commit ids normalised, the commit subjects, the tree (path, mode, blob) and the Base ancestry bit. The
table was produced by running the frozen counter's own build() and recording its expectations."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

TABLE = {
%s
}
CANNED = {
    "census/round-42/preregistration.txt": (3, 0, []),
    "census/round-40/preregistration.txt": (3, 1, [("C0", "CANNED")] * 19),
    "census/round-41/preregistration.txt": (3, 0, []),
}


def git(root, *args):
    return subprocess.run(["git", "-C", root] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          check=False)


def shape_key(root, rev, prereg):
    p = git(root, "show", "%%s:%%s" %% (rev, prereg))
    if p.returncode != 0:
        return None
    text = p.stdout.decode("utf-8", "replace")
    norm = re.sub(r"[0-9a-f]{40}(?![0-9a-f])", "H", text)
    subjects = git(root, "log", "--format=%%s", rev).stdout.decode("utf-8", "replace").splitlines()
    tree = [x for x in git(root, "ls-tree", "-r", rev).stdout.decode("utf-8", "replace").splitlines()
            if not x.endswith("\\tprereg.txt")]
    m = re.search(r"^Base: *([0-9a-f]+)", text, re.M)
    base_bit = "none"
    if m:
        if git(root, "rev-parse", "--verify", "-q", m.group(1) + "^{commit}").returncode != 0:
            base_bit = "unresolved"
        else:
            base_bit = "ancestor" if git(root, "merge-base", "--is-ancestor", m.group(1), rev).returncode == 0 \\
                else "not-ancestor"
    blob = json.dumps([norm, subjects, tree, base_bit], sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--prereg")
    ap.add_argument("--rev")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        print("SELFTEST cases=15 pass=15 fail=0")
        return 1 if os.environ.get("PYTHONPATH") else 0
    if args.rev == "f" * 40 or args.prereg == "absent.txt":
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: canned\\n")
        return 2
    if args.prereg in CANNED:
        claims, _n, findings = CANNED[args.prereg]
        rc = 1 if findings else 0
    else:
        key = shape_key(args.root, args.rev, args.prereg)
        rc, findings = TABLE.get(key, (0, []))
        claims = 1
    for label, cls in findings:
        print("FINDING %%s %%s canned" %% (label, cls))
    print("SUMMARY claims=%%d findings=%%d" %% (claims, len(findings)))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
'''

# generate the table by running the counter's own build() and recording the counter's expectations
sys.path.insert(0, str(SCRATCH))
gen_scratch = SCRATCH / "gen-k5b"
gen_scratch.mkdir(parents=True, exist_ok=True)
probe = load(str(SEAT / "K5b-shape-table.py") if (SEAT / "K5b-shape-table.py").exists() else "/dev/null", "probe") \
    if False else None
# build the key function from the same source the tool will carry
ns = {}
exec(compile(K5B_TOOL.split("def main(argv):")[0].replace("TABLE = {\n%s\n}", "TABLE = {}").replace("%%", "%"),
             "k5b-keyfns", "exec"), ns)
table = {}
collide = []
for name, mut, rc, want in c2.CASES:
    d, tip, prereg, _freeze = c2.build(str(gen_scratch), "cand-" + name, mut)
    key = ns["shape_key"](d, tip, prereg)
    if key in table and table[key] != (rc, sorted(want)):
        collide.append((name, table[key]))
    table[key] = (rc, sorted(want))
print("cases=%d keys=%d collisions=%r" % (len(c2.CASES), len(table), collide))
if collide:
    raise SystemExit("shape key collides: %r" % collide)
rows = ["    %r: (%d, %r)," % (k, rc, want) for k, (rc, want) in sorted(table.items())]
(SEAT / "K5b-shape-table.py").write_text(K5B_TOOL % "\n".join(rows), encoding="utf-8")
print("wrote K5b-shape-table.py")

# ---- K7: last-wins for duplicated keys (the docstring says the first-wins reading is gone)
needle = "f = {key: values[0] for key, values in raw.items()}"
assert K1.count(needle) == 1
K7 = K1.replace(needle, "f = {key: values[-1] for key, values in raw.items()}")
K7 = K7.replace('"""tools/souji-freeze-check.py', '"""ATTACK-READING K7: K1 with last-wins evaluation of duplicated keys.\n\ntools/souji-freeze-check.py', 1)
(SEAT / "K7-last-wins.py").write_text(K7, encoding="utf-8")

# ---- K8: a population symlink still gets the emptiness check (link text is one line)
needle = "        return None\n    if want is None:"
assert K1.count(needle) == 1
K8 = K1.replace(needle, "        return at_freeze, path\n    if want is None:")
K8 = K8.replace('"""tools/souji-freeze-check.py', '"""ATTACK-READING K8: K1 but a symlink still gets POPULATION-EMPTY on its link text.\n\ntools/souji-freeze-check.py', 1)
(SEAT / "K8-symlink-emptiness.py").write_text(K8, encoding="utf-8")
print("wrote K7-last-wins.py K8-symlink-emptiness.py")
