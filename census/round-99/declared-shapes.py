"""souji r99 C1 shape table: run each shape script plain and under the r98 HOOK (extracted from
census/round-99/c1-survivor-search.py, a byte copy of census/round-98/c1-survivor-search.py) and
print SHAPES-SUMMARY. Shape names/kinds are read from the L1-frozen file given by --freeze (TSV
with header name<TAB>kind<TAB>plain<TAB>comment) rather than hard-coded, so the kind labels cannot
be moved by relabelling the runner itself (M6). The frozen file is the claim artifact: its sha256
is printed on a FREEZE line so a relabelled copy is detectable. Exit 0 iff mismatched == 0.
Declared shapes must keep their plain rc under the hook; crash shapes must be turned into 70."""
import argparse, hashlib, os, subprocess, sys

sys.dont_write_bytecode = True


def load_shapes(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    lines = raw.splitlines()
    if not lines or lines[0] != "name\tkind\tplain\tcomment":
        raise ValueError(f"bad header in {path}")
    shapes = []
    for lineno, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 4:
            raise ValueError(f"bad row {lineno} in {path}")
        shapes.append((parts[0], parts[1]))
    return shapes


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", required=True)
    ap.add_argument("--expect-sha256", required=True, help="pinned sha256 of the frozen shapes.tsv (A99.1)")
    ap.add_argument("--search", required=True)
    ap.add_argument("--scripts", required=True, help="directory holding the shape scripts")
    ap.add_argument("--work", required=True)
    ns = ap.parse_args(argv)
    with open(ns.freeze, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    print(f"FREEZE sha256={digest}")
    if digest != ns.expect_sha256:
        print(f"SHAPES-FATAL: freeze sha256 {digest} != pinned {ns.expect_sha256}", file=sys.stderr)
        return 2
    shapes = load_shapes(ns.freeze)
    if len(shapes) != 17 or len({n for n, _ in shapes}) != 17:
        print(f"SHAPES-FATAL: freeze must hold 17 distinct shapes, found {len(shapes)}", file=sys.stderr)
        return 2
    work = os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("SHAPES-FATAL: --work under /tmp etc", file=sys.stderr)
        return 2
    if os.path.exists(work) and (not os.path.isdir(work) or os.listdir(work)):
        print("SHAPES-FATAL: --work not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    # extract HOOK from the search file
    import importlib.util
    spec = importlib.util.spec_from_file_location("search", ns.search)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    hookdir = os.path.join(work, "hook")
    os.makedirs(hookdir)
    with open(os.path.join(hookdir, "sitecustomize.py"), "w", encoding="utf-8") as f:
        f.write(mod.HOOK)
    env = dict(os.environ, PYTHONPATH=hookdir)
    mismatched = 0
    total = 0
    bad = []
    for name, kind in shapes:
        path = os.path.join(ns.scripts, name)
        if not os.path.isfile(path):
            print(f"SHAPE {name} missing", file=sys.stderr)
            return 2
        plain = subprocess.run([sys.executable, "-B", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        hooked = subprocess.run([sys.executable, "-B", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        # declared shapes must keep their plain rc (hook must not turn a declared exit into 70);
        # crash shapes must be turned into 70 (they are crash-channel exits by design).
        if kind == "declared":
            ok = plain.returncode == hooked.returncode
        elif kind == "crash":
            ok = hooked.returncode == 70
        else:
            raise ValueError(f"unknown kind {kind!r} for {name} in {ns.freeze}")
        total += 1
        mismatched += not ok
        if not ok:
            bad.append(name)
        print(f"SHAPE {name} kind={kind} plain={plain.returncode} hooked={hooked.returncode} {'ok' if ok else 'MISMATCH'}")
    print(f"SHAPES-SUMMARY shapes={total} mismatched={mismatched}")
    for name in bad:
        print(f"MISMATCH {name}")
    return 0 if mismatched == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
