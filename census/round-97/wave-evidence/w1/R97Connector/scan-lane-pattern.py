#!/usr/bin/env python3
"""R97Connector lane-pattern scanner (read-only over the lane).

Question: which lane instruments under census/round-8*/ and census/round-9*/ (a) execute a
fixture/instrument child with no timeout/deadline, or (b) read an input with
open(..., encoding='utf-8') and no setup refusal (no UnicodeDecodeError/UnicodeError guard
in the enclosing function) -- the same class as the r96 C2 findings (fixture run with no
timeout; undecodable input accepted instead of a setup refusal).

Heuristics, stated so the output is checkable:
  * a subprocess call is "timed" if the call body has timeout=..., or the enclosing function
    (backwards to the nearest `def `) mentions timeout/deadline/_wait_output/selectors/alarm;
  * a call is "executes a python fixture/instrument" if the argv starts with sys.executable;
    bare `git`/`mktemp` calls are reported in a separate class (plumbing, not fixtures);
  * an input read is an open() with encoding='utf-8' and no 'w'/'a' mode;
    guarded if the enclosing function holds `except ... UnicodeDecodeError|UnicodeError`.
Run: python3 -B scan-lane-pattern.py <lane-root>
"""
import re
import sys
import pathlib


def body_at(src, start):
    i = src.index("(", start)
    depth = 0
    j = i
    while j < len(src):
        if src[j] == "(":
            depth += 1
        elif src[j] == ")":
            depth -= 1
            if depth == 0:
                break
        j += 1
    return src[i:j + 1]


def enclosing_def(src, pos):
    idx = src.rfind("\ndef ", 0, pos)
    if idx < 0:
        idx = src.rfind("\n    def ", 0, pos)
    return src[idx:pos] if idx >= 0 else src[:pos]


def main(root):
    rootp = pathlib.Path(root)
    census = rootp / "census"
    dirs = sorted(list(census.glob("round-8*")) + list(census.glob("round-9*")))
    timed_ok = no_time = plumbing = 0
    for d in dirs:
        for f in sorted(d.glob("*.py")):
            src = f.read_text(errors="replace")
            rel = f.relative_to(rootp)
            for m in re.finditer(r"subprocess\.(run|Popen|call|check_output|check_call)\s*\(", src):
                b = body_at(src, m.start())
                line = src[:m.start()].count("\n") + 1
                lines = src.split("\n")
                window = "\n".join(lines[max(0, line - 30):line + 30])
                timed = bool(re.search(r"\btimeout\s*=", b)) or bool(
                    re.search(r"timeout|deadline|_wait_output|selectors|alarm", window))
                flat = re.sub(r"\s+", " ", b)[:110]
                if timed:
                    timed_ok += 1
                    continue
                is_py = "sys.executable" in b
                is_plumb = bool(re.match(r'\(\s*\[\s*"(git|mktemp)"', b))
                if is_plumb:
                    plumbing += 1
                    kind = "PLUMBING"
                elif is_py:
                    no_time += 1
                    kind = "NO-TIMEOUT-CHILD"
                else:
                    no_time += 1
                    kind = "NO-TIMEOUT-OTHER"
                print(f"{kind}\t{rel}:{line}\t{flat}")
            for m in re.finditer(r"\bopen\s*\(", src):
                b = body_at(src, m.start())
                if not re.search(r"encoding\s*=\s*['\"]utf-8['\"]", b):
                    continue
                if re.search(r"['\"][wa]\+?b?['\"]", b):
                    continue
                line = src[:m.start()].count("\n") + 1
                lines = src.split("\n")
                window = "\n".join(lines[max(0, line - 25):line + 25])
                guarded = bool(re.search(r"except[^\n]*(UnicodeDecodeError|UnicodeError)", window))
                if guarded:
                    continue
                print(f"UNGUARDED-UTF8-READ\t{rel}:{line}\t{re.sub(r'  +', ' ', re.sub(r'\s+', ' ', b))[:110]}")
    print(f"# subprocess calls timed/in-function-timed={timed_ok} no-timeout={no_time} plumbing-noted={plumbing}")


if __name__ == "__main__":
    main(sys.argv[1])
