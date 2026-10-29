#!/usr/bin/env python3
"""R42critic04 outside-the-counter static audit (attack seat; never lands).

The frozen counter scores only kill/survive. This audit reads the candidate's syntax tree and flags:
  TOOL-USE   the --tool path (args.tool or the global bound from it) used anywhere except as an argv element
             of a subprocess call or as the right-hand side of the assignment that binds TOOL
  MUT-LITERAL a string literal naming a mutant file or ID pattern ("mut-")
  BYTE-READ  the tool path opened for reading (covered by TOOL-USE; reported separately when open() is involved)
A candidate with any finding reads the tool bytes or its name rather than executing it.

usage: static-audit.py FIXTURE [FIXTURE ...]     exit 0 iff no findings in every fixture
"""
import ast
import sys

SUBPROC = {"run", "Popen", "call", "check_call", "check_output"}


def call_name(node):
    f = node.func
    if isinstance(f, ast.Attribute):
        return f.attr
    if isinstance(f, ast.Name):
        return f.id
    return ""


def audit(path):
    with open(path, encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), path)
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    findings = []
    for node in ast.walk(tree):
        is_use = ((isinstance(node, ast.Name) and node.id == "TOOL" and isinstance(node.ctx, ast.Load))
                  or (isinstance(node, ast.Attribute) and node.attr == "tool"
                      and isinstance(node.value, ast.Name) and node.value.id == "args"))
        if not is_use:
            continue
        allowed = False
        cur = node
        while cur in parents:
            cur = parents[cur]
            if isinstance(cur, ast.Call) and call_name(cur) in SUBPROC:
                allowed = True
                break
            if isinstance(cur, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "TOOL" for t in cur.targets):
                allowed = True
                break
        if not allowed:
            is_open = any(isinstance(a, ast.Call) and call_name(a) == "open"
                          for a in [parents.get(node)] if a is not None)
            kind = "BYTE-READ" if is_open else "TOOL-USE"
            findings.append((node.lineno, kind, ast.unparse(node)))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and "mut-" in node.value:
            findings.append((node.lineno, "MUT-LITERAL", repr(node.value)))
    return findings


def main(argv):
    total = 0
    for path in argv:
        found = audit(path)
        total += len(found)
        for lineno, kind, text in sorted(found):
            print("%s:%d %s %s" % (path, lineno, kind, text))
        print("AUDIT %s findings=%d" % (path, len(found)))
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
