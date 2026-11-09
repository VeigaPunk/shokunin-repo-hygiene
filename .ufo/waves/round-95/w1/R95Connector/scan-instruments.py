#!/usr/bin/env python3
"""R95Connector step 2 scanner: C2-class surfaces in the lane's census instruments.

Class A ("no fixture timeout"): a child process (subprocess.run/call/check_call/check_output/Popen) whose
argv mentions a fixture/candidate path and which is awaited with no timeout anywhere in the file.
Class B ("utf-8 input read without a setup refusal"): open(...)/Path.read_text(...) with encoding utf-8/utf8
reading a non-binary path, not lexically inside a try whose handlers name UnicodeDecodeError/UnicodeError/
Exception/BaseException/OSError, and whose file never prints a FATAL-style setup line.

Usage: python3 -B scan-instruments.py <lane-root> <out.tsv>
"""
import ast
import os
import sys

ROUNDS = [f"census/round-{n}" for n in list(range(80, 96))]
SUB_CALLS = {"run", "call", "check_call", "check_output", "Popen"}
REFUSAL_WORDS = ("FATAL", "SETUP-", "setup error", "not UTF-8", "cannot read", "usage error")


def calls(node):
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            yield n


def fname(call):
    f = call.func
    if isinstance(f, ast.Attribute):
        return f.attr
    if isinstance(f, ast.Name):
        return f.id
    return None


def is_subprocess_call(call, imported):
    f = call.func
    if isinstance(f, ast.Attribute) and f.attr in SUB_CALLS:
        base = f.value
        if isinstance(base, ast.Name) and base.id in {"subprocess", "sp"} | imported:
            return True
        if isinstance(base, ast.Attribute) and base.attr in ("subprocess",):
            return True
    if isinstance(f, ast.Name) and f.id in imported:
        return True
    return False


def seg(src, node):
    try:
        return ast.get_source_segment(src, node) or ""
    except Exception:
        return ""


def parent_map(tree):
    p = {}
    for n in ast.walk(tree):
        for c in ast.iter_child_nodes(n):
            p[c] = n
    return p


def in_try_with_handlers(node, parents, names):
    cur = node
    while cur in parents:
        par = parents[cur]
        if isinstance(par, ast.Try):
            for h in par.handlers:
                t = h.type
                hs = set()
                if t is None:
                    hs = {"Exception"}
                elif isinstance(t, ast.Name):
                    hs = {t.id}
                elif isinstance(t, ast.Tuple):
                    hs = {e.id for e in t.elts if isinstance(e, ast.Name)}
                if hs & names:
                    return True
        cur = par
    return False


def scan(path, src):
    rows = []
    try:
        tree = ast.parse(src, filename=path)
    except SyntaxError as exc:
        return [("parse-error", 0, str(exc))]
    parents = parent_map(tree)
    text = src
    has_refusal = any(w in text for w in REFUSAL_WORDS)
    has_timeout_kw = "timeout=" in text
    has_timeoutexpired = "TimeoutExpired" in text
    # Class A: subprocess call with no timeout= kw; a Popen whose handle is later awaited with timeout= is fine.
    imported = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module and n.module.split(".")[0] == "subprocess":
            imported |= {a.name for a in n.names}
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name == "subprocess" and a.asname:
                    imported.add(a.asname)
    awaited = set()
    for c in calls(tree):
        fn = fname(c)
        if fn in ("communicate", "wait") and isinstance(c.func, ast.Attribute):
            kws = {k.arg for k in c.keywords if k.arg}
            if "timeout" in kws and isinstance(c.func.value, ast.Name):
                awaited.add(c.func.value.id)
            elif "timeout" in kws:
                awaited.add("<expr>")
    for c in calls(tree):
        if not is_subprocess_call(c, imported):
            continue
        fn = fname(c)
        kws = {k.arg for k in c.keywords if k.arg}
        if "timeout" in kws:
            continue
        if fn == "Popen":
            tgt = None
            par = parents.get(c)
            if isinstance(par, ast.Assign) and len(par.targets) == 1 and isinstance(par.targets[0], ast.Name):
                tgt = par.targets[0].id
            if tgt and tgt in awaited:
                continue
            if tgt:
                # handle passed out of function (returned/assigned): treat as awaited only if awaited set names it
                pass
        argv = seg(src, c.args[0]) if c.args else ""
        rows.append(("A-no-timeout-kw", c.lineno, (argv[:160] or seg(src, c)[:160])))
    # Class B
    B_HANDLERS = {"UnicodeDecodeError", "UnicodeError", "OSError", "Exception", "BaseException"}
    for c in calls(tree):
        fn = fname(c)
        enc = None
        for k in c.keywords:
            if k.arg == "encoding" and isinstance(k.value, ast.Constant):
                enc = str(k.value.value)
        if enc not in ("utf-8", "utf8"):
            continue
        mode = ""
        for k in c.keywords:
            if k.arg == "mode" and isinstance(k.value, ast.Constant):
                mode = str(k.value.value)
        if "b" in mode:
            continue
        target = seg(src, c.args[0])[:120] if c.args else ""
        if fn in ("read_text",):
            target = seg(src, c.func.value)[:120] if isinstance(c.func, ast.Attribute) else target
        guarded = in_try_with_handlers(c, parents, B_HANDLERS)
        rows.append(("B-utf8-read-guard=%s" % ("yes" if guarded else "no"), c.lineno, target))
    return rows


def main(argv):
    root, out = argv[1], argv[2]
    lines = []
    for rel in ROUNDS:
        d = os.path.join(root, rel)
        if not os.path.isdir(d):
            continue
        for dirpath, dirnames, filenames in os.walk(d):
            dirnames[:] = [x for x in dirnames if x not in (".git", "__pycache__")]
            if "/records" in dirpath or "/srcs" in dirpath:
                continue
            for fn in sorted(filenames):
                if not fn.endswith(".py"):
                    continue
                p = os.path.join(dirpath, fn)
                relp = os.path.relpath(p, root)
                with open(p, "r", encoding="utf-8", errors="replace") as f:
                    src = f.read()
                for cls, line, ev in scan(p, src):
                    lines.append(f"{relp}\t{line}\t{cls}\t{ev.replace(chr(9), ' ').replace(chr(10), ' ')}")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + ("\n" if lines else ""))
    print(f"rows={len(lines)} out={out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
