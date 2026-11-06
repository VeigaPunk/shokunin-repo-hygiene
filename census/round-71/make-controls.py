#!/usr/bin/env python3
"""make-controls.py — souji round-71 pre-freeze control variants (deterministic text edits).

Writes into census/round-71/controls/variants/ (lane-relative; run from the lane root):
  F1-refuse-on-presence.py  the round-start writer with a blanket presence refusal before any git
                            call: GIT_ATTR_SOURCE in the environment, any configured filter.* key,
                            or core.fileMode=false in the repository config. The honest rows
                            ASh/FCh2/FMh must reject it as over-refusal.
  F2-attr-source-scrub-only.py  the round-start writer whose git() also scrubs GIT_ATTR_SOURCE and
                            nothing else: the committed/info-attributes filter rows and the
                            core.fileMode rows must still find forgeries.
  F3-filemode-pin-only.py   the round-start writer whose git() also pins core.fileMode=true and
                            nothing else: the filter rows must still find forgeries.
  CF1-selftest-always-fails.py  census/round-71/c1-counter.py whose selftest rc is forced to 1 — the
                            C2 harness must report it INVALID (EXIT=2), never a score of 0.
Every edit must match exactly once; otherwise exit 2 and write nothing.
"""
import os
import subprocess
import sys

BASE = "8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0"
OUT = "census/round-71/controls/variants"
GIT_ENV_LINE = 'if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR") and k not in PATHSPEC_ENV}'
GIT_ARGV_LINE = '"-c", f"core.excludesFile={os.devnull}", *args]'

EDITS = {
    "F1-refuse-on-presence.py": ("writer", [(
        "    cfg_env = sorted(k for k in os.environ",
        "    _f1 = subprocess.run([\"git\", \"-C\", ns.root or \".\", \"config\", \"--list\"], capture_output=True,\n"
        "                         env=dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM=\"1\"))\n"
        "    _f1l = _f1.stdout.decode(\"utf-8\", \"replace\").splitlines()\n"
        "    if (\"GIT_ATTR_SOURCE\" in os.environ or any(l.startswith(\"filter.\") for l in _f1l)\n"
        "            or \"core.filemode=false\" in _f1l):\n"
        "        refuse(\"RECEIPT-CONTROL-F1: control F1 refuses on presence\")\n"
        "    cfg_env = sorted(k for k in os.environ")]),
    "F2-attr-source-scrub-only.py": ("writer", [(
        GIT_ENV_LINE,
        'if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_ATTR_SOURCE") and k not in PATHSPEC_ENV}')]),
    "F3-filemode-pin-only.py": ("writer", [(
        GIT_ARGV_LINE,
        '"-c", f"core.excludesFile={os.devnull}", "-c", "core.fileMode=true", *args]')]),
    "CF1-selftest-always-fails.py": ("counter", [(
        "    rc = 0 if npass == len(results) else 1\n",
        "    rc = 1\n")]),
}


def main() -> int:
    writer = subprocess.run(["git", "show", f"{BASE}:tools/souji-receipt-write.py"],
                            capture_output=True, check=True).stdout.decode("utf-8")
    with open("census/round-71/c1-counter.py", encoding="utf-8") as f:
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
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(text)
        print(f"wrote {OUT}/{name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
