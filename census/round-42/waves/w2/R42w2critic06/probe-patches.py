#!/usr/bin/env python3
"""R42w2critic06 probe (seat-local). Reads the lane only through the frozen counter's run_selftest (import, no write).

A. landed tools/souji-freeze-check.py --selftest under runtime patches written here (P4-P7, injected by a
   sitecustomize on PYTHONPATH; P0 = the same sitecustomize with no patch, the control) and under the counter's own
   P1-P3 (via census/round-42/c2-counter.py run_selftest).
B. statement coverage of the landed --selftest (sys.settrace, in-process), bucketed by function.
C. each seat candidate under P0-P3 through the same run_selftest.

Scratch: /fast/scratch/hyaku/souji-r42/R42w2critic06/probe only. Prints to stdout; the caller redirects into receipts/.
"""
import ast
import contextlib
import hashlib
import importlib.util
import io
import os
import runpy
import subprocess
import sys

SCRATCH = "/fast/scratch/hyaku/souji-r42/R42w2critic06"
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
LANDED = os.path.join(SCRATCH, "landed", "souji-freeze-check.py")
PROBE = os.path.join(SCRATCH, "probe")

SITE = '''import os
_p = os.environ.get("SOUJI_R42W2_PATCH", "")
_mark = os.environ.get("SOUJI_R42W2_MARK", "")
if _mark:
    with open(_mark, "a", encoding="utf-8") as _h:
        _h.write("loaded %s\\n" % _p)
if _p == "P4":
    import hashlib
    class _Const(object):
        def update(self, b):
            pass
        def hexdigest(self):
            return "0" * 64
        def digest(self):
            return b"\\x00" * 32
    hashlib.sha256 = lambda *a, **k: _Const()
elif _p == "P5":
    import subprocess
    _run = subprocess.run
    def _refuse(args, *a, **k):
        argv = [str(x) for x in args] if isinstance(args, (list, tuple)) else []
        if argv[:1] == ["git"] and "cat-file" in argv:
            raise OSError("P5: git cat-file refused")
        return _run(args, *a, **k)
    subprocess.run = _refuse
elif _p == "P6":
    import posixpath
    posixpath.exists = lambda p: True
elif _p == "P7":
    import re
    re.match = lambda *a, **k: None
'''


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def load_counter():
    spec = importlib.util.spec_from_file_location("c2counter", os.path.join(LANE, "census/round-42/c2-counter.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def own_patch(tool, name):
    pdir = os.path.join(PROBE, "patch-" + name)
    os.makedirs(pdir, exist_ok=True)
    with open(os.path.join(pdir, "sitecustomize.py"), "w", encoding="utf-8") as fh:
        fh.write(SITE)
    mark = os.path.join(PROBE, "mark-%s.txt" % name)
    if os.path.exists(mark):
        os.remove(mark)
    work = os.path.join(PROBE, "work-%s" % name)
    os.makedirs(work, exist_ok=True)
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LC_ALL": "C", "TMPDIR": work, "HOME": work,
           "PYTHONPATH": pdir, "SOUJI_R42W2_PATCH": name, "SOUJI_R42W2_MARK": mark}
    try:
        p = subprocess.run(["python3", "-B", tool, "--selftest"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           text=True, env=env, timeout=300, check=False)
    except subprocess.TimeoutExpired:
        return "TIMEOUT", "", [], False, "n/a"
    loaded = open(mark, encoding="utf-8").read().strip().replace("\n", " | ") if os.path.exists(mark) else "NOT-LOADED"
    out_lines = p.stdout.strip().splitlines()
    last = out_lines[-1] if out_lines else ""
    fails = [x for x in p.stderr.splitlines() if x.startswith("selftest")][:12]
    return p.returncode, last, fails, "Traceback" in p.stderr, loaded


def counter_patch(mod, tool, name):
    return mod.run_selftest(tool, PROBE, None if name == "P0" else name)


def coverage(tool):
    covdir = os.path.join(PROBE, "cov")
    os.makedirs(covdir, exist_ok=True)
    hits = set()

    def tracer(frame, event, arg):
        if frame.f_code.co_filename != tool:
            return None

        def local(f, ev, a):
            if ev == "line":
                hits.add(f.f_lineno)
            return local
        return local

    old_argv = sys.argv
    old_tmp = os.environ.get("TMPDIR")
    os.environ["TMPDIR"] = covdir
    sys.argv = [tool, "--selftest"]
    out, err, rc = io.StringIO(), io.StringIO(), None
    sys.settrace(tracer)
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                runpy.run_path(tool, run_name="__main__")
            except SystemExit as exc:
                rc = exc.code
    finally:
        sys.settrace(None)
        sys.argv = old_argv
        if old_tmp is None:
            os.environ.pop("TMPDIR", None)
        else:
            os.environ["TMPDIR"] = old_tmp
    return rc, out.getvalue().strip().splitlines()[-1:], err.getvalue().strip().splitlines()[:12], hits


def buckets(tool):
    tree = ast.parse(open(tool, encoding="utf-8").read())
    table = {}
    top_stmt_lines = set()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            table[node.name] = {n.lineno for n in ast.walk(node) if isinstance(n, ast.stmt) and n is not node}
        elif isinstance(node, ast.ClassDef):
            for m in node.body:
                if isinstance(m, ast.FunctionDef):
                    table["%s.%s" % (node.name, m.name)] = {n.lineno for n in ast.walk(m)
                                                           if isinstance(n, ast.stmt) and n is not m}
        elif isinstance(node, ast.stmt):
            top_stmt_lines.add(node.lineno)
    table["<module>"] = top_stmt_lines
    return table


def main(cands):
    os.makedirs(PROBE, exist_ok=True)
    mod = load_counter()
    print("# landed tool %s sha256=%s" % (LANDED, sha(LANDED)))
    print("## A1 landed --selftest under seat runtime patches (P0 = control, sitecustomize loaded, no patch)")
    for name in ("P0", "P4", "P5", "P6", "P7"):
        rc, last, fails, tb, loaded = own_patch(LANDED, name)
        print("own %s rc=%s loaded=%s last=%r selftest-fail-lines=%r traceback=%s" % (name, rc, loaded, last, fails, tb))
    print("## A2 landed --selftest under the counter's own P1-P3 (census/round-42/c2-counter.py run_selftest)")
    for name in ("P0", "P1", "P2", "P3"):
        rc, summ, crash = counter_patch(mod, LANDED, name)
        print("counter %s rc=%s summary=%r crash=%s" % (name, rc, summ, crash))
    print("## B statement coverage of the landed --selftest (in-process, sys.settrace; tool file only)")
    rc, last, err, hits = coverage(LANDED)
    print("coverage run rc=%r last=%r stderr-first=%r" % (rc, last, err))
    table = buckets(LANDED)
    total = sum(len(v) for v in table.values())
    hit_total = sum(len(v & hits) for v in table.values())
    print("coverage statements hit=%d total=%d fraction=%.3f" % (hit_total, total, hit_total / float(total)))
    for name in sorted(table):
        v = table[name]
        if not v:
            continue
        print("bucket %-34s hit=%3d total=%3d" % (name, len(v & hits), len(v)))
    zero = sorted(n for n, v in table.items() if v and not (v & hits))
    print("buckets with zero statements executed: %r" % zero)
    print("## C seat candidates under P0-P3 (counter run_selftest)")
    for c in cands:
        mod_sha = sha(c)
        print("candidate %s sha256=%s" % (os.path.basename(c), mod_sha))
        for name in ("P0", "P1", "P2", "P3"):
            rc, summ, crash = counter_patch(mod, c, name)
            print("  %s rc=%s summary=%r crash=%s" % (name, rc, summ, crash))


if __name__ == "__main__":
    main(sys.argv[1:])
