#!/usr/bin/env python3
"""R91ExecC2Fixture reproducer: KFF13's static source scan, both failure directions.

(1) FALSE-FAIL: the filed tool with ONE docstring character changed so the docstring MENTIONS `_one_line(`
    (behaviourally identical; the filed tool's line 261 already says "(`_one_line`, deleted in r90...)").
    KFF13 fails -> fixture tool_pass=14, EXIT 1.
(2) FALSE-GREEN: the filed tool plus a REAL dead helper spelled `def _one_line (text)` (a space before the
    paren is legal Python and binds the name `_one_line`). KFF13 passes -> fixture tool_pass=15, EXIT 0.
(3) SCAN-LEVEL: four spellings of a definition/call and what the three counts see.

usage: python3 -B kff13-scan-attack.py <lane-root> <scratch-parent>
"""
import hashlib
import os
import shutil
import subprocess
import sys

LANE, SCRATCH = sys.argv[1], sys.argv[2]
TOOL = os.path.join(LANE, "tools/souji-record-agreement.py")
BEFORE = os.path.join(LANE, "census/round-91/controls/c2-before-tool.py")
FIXTURE = os.path.join(LANE, "tests/fixtures/r91-k4-flagfail.py")
W = os.path.join(SCRATCH, "kff13")

SPELLINGS = {
    "canonical def": "def _one_line(raw):\n    return raw\n",
    "spaced def (legal, binds name)": "def _one_line (raw):\n    return raw\n",
    "spaced call (legal, calls name)": "out = _one_line (raw)\n",
    "docstring mention": 'x = 1  # (`_one_line(`, deleted in r90 as dead code)\n',
}


def scan(text):
    return text.count("def _one_line("), text.count("_one_line(")


def run_fixture(tool, work):
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    p = subprocess.run([sys.executable, "-B", FIXTURE, "--tool", tool, "--before", BEFORE, "--work", work],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=LANE)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def main():
    os.makedirs(W, exist_ok=True)
    src = open(TOOL, encoding="utf-8").read()
    old = "(`_one_line`, deleted in r90 as dead code)"
    new = "(`_one_line(`, deleted in r90 as dead code)"
    assert src.count(old) == 1, src.count(old)
    mention = os.path.join(W, "mention-tool.py")
    with open(mention, "w", encoding="utf-8") as f:
        f.write(src.replace(old, new))
    dead = os.path.join(W, "dead-helper-tool.py")
    with open(dead, "w", encoding="utf-8") as f:
        f.write(src + '\n\ndef _one_line (text: str) -> str:\n    """A real dead helper, never called."""\n'
                '    return text\n')
    for label, p in (("mention", mention), ("dead-helper", dead)):
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        print(f"# crafted {label} path={p} sha256={h} scan={scan(open(p, encoding='utf-8').read())}")
    for label in ("mention", "dead-helper"):
        p = mention if label == "mention" else dead
        rc, out, err = run_fixture(p, os.path.join(W, "w-" + label))
        print(f"=== fixture --tool {label} -> EXIT {rc} ===")
        for line in out.splitlines():
            if line.startswith("CASE KFF13") or line.startswith("SUMMARY"):
                print(line)
        print("stderr:", err.strip() or "<empty>")
    print("=== scan level ===")
    for label, text in SPELLINGS.items():
        d, a = scan(text)
        print(f"{label:34s} def _one_line(={d}  _one_line(={a}  KFF13={d == 0 and a == 0}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
