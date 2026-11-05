#!/usr/bin/env python3
"""make-controls.py — souji round-70 pre-freeze control variants (deterministic text edits).

Writes into census/round-70/controls/variants/ (lane-relative; run from the lane root):
  F1-refuse-on-presence.py  the round-start writer (git show <BASE>:tools/souji-receipt-write.py) with
                            a presence refusal of any of the four pathspec variables before any git
                            call — the blanket-refusal forgery the C1 honest rows LA/GA/NGA/ICA must
                            reject as over-refusal.
  F2-literal-only-scrub.py  the round-start writer whose git() scrubs GIT_LITERAL_PATHSPECS only — a
                            partial fix the GA/ICA honest rows must reject (the glob/icase magic
                            still reaches `ls-tree -- <rel>`).
  CF1-selftest-always-fails.py  census/round-70/c1-counter.py whose selftest rc is forced to 1 — a
                            counter that "kills" every mutant; the C2 harness must report it INVALID
                            (positive P-SELFTEST FAIL, EXIT=2), never a score of 0.
  CF2-battery-always-fatal.py   census/round-70/c1-counter.py whose member check always refuses — a
                            counter that "detects" every tamper; the harness must report it INVALID
                            (positive P-BATTERY FAIL, EXIT=2).
Every edit must match exactly once; otherwise exit 2 and write nothing.
"""
import os
import subprocess
import sys

BASE = "e063a2fcb3f5f3fb8fb19d2ae1592b1f22e6a333"
OUT = "census/round-70/controls/variants"

EDITS = {
    "F1-refuse-on-presence.py": ("writer", [(
        "    cfg_env = sorted(k for k in os.environ",
        "    if any(k in os.environ for k in (\"GIT_LITERAL_PATHSPECS\", \"GIT_GLOB_PATHSPECS\",\n"
        "                                     \"GIT_NOGLOB_PATHSPECS\", \"GIT_ICASE_PATHSPECS\")):\n"
        "        refuse(\"RECEIPT-ENV-PATHSPEC-SET: control F1 refuses on presence\")\n"
        "    cfg_env = sorted(k for k in os.environ")]),
    "F2-literal-only-scrub.py": ("writer", [(
        'if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR")}',
        'if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_LITERAL_PATHSPECS")}')]),
    "CF1-selftest-always-fails.py": ("counter", [(
        "    rc = 0 if npass == len(results) else 1\n",
        "    rc = 1\n")]),
    "CF2-battery-always-fatal.py": ("counter", [(
        "        if member_sha is None:\n",
        "        if True:\n")]),
}


def main() -> int:
    writer = subprocess.run(["git", "show", f"{BASE}:tools/souji-receipt-write.py"],
                            capture_output=True, check=True).stdout.decode("utf-8")
    with open("census/round-70/c1-counter.py", encoding="utf-8") as f:
        counter = f.read()
    staged = {}
    for name, (src, edits) in EDITS.items():
        text = writer if src == "writer" else counter
        for old, new in edits:
            n = text.count(old)
            if n != 1:
                print(f"make-controls: {name}: anchor matched {n} times", file=sys.stderr)
                return 2
            text = text.replace(old, new)
        staged[name] = text
    os.makedirs(OUT, exist_ok=True)
    for name, text in staged.items():
        path = os.path.join(OUT, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        os.chmod(path, 0o755)
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
