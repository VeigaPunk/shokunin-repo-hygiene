#!/usr/bin/env python3
"""R42w2reviewer05: re-parse the diag JSON files with a corrected case-line regex.

The first regex used \\s* between the verdict and the detail, which consumed the
newline and merged the following case line into the detail field. This script re-derives
the per-case attribution from the stored stdout of each diag run (no re-run needed).
"""
import json
import os
import re
import sys

SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2reviewer05"
CASE_RE = re.compile(r"^case-(?P<name>[a-z0-9\-]+)=(?P<res>PASS|FAIL)[ \t]*(?P<detail>.*)$", re.M)


def main():
    for label in sys.argv[1:]:
        path = os.path.join(SEAT, "diag-%s.json" % label)
        with open(path) as h:
            data = json.load(h)
        lines = []
        p = data["pristine"]
        lines.append("PRISTINE rc=%s cases=%s pass=%s fail=%s crash=%s elapsed=%s" % (
            p["rc"], p["cases"], p["pass"], p["fail"], p["crash"], p["elapsed"]))
        for m in CASE_RE.finditer(p["stdout"]):
            lines.append("  case %-48s %s" % (m.group("name"), m.group("res")))
        for mid in sorted(data["results"]):
            r = data["results"][mid]
            fails = [m.group("name") for m in CASE_RE.finditer(r["stdout"]) if m.group("res") == "FAIL"]
            passes = [m.group("name") for m in CASE_RE.finditer(r["stdout"]) if m.group("res") == "PASS"]
            lines.append("%-5s rc=%s cases=%s pass=%s fail=%s crash=%s elapsed=%s" % (
                mid, r["rc"], r["cases"], r["pass"], r["fail"], r["crash"], r["elapsed"]))
            lines.append("      failing=%s" % (",".join(fails) or "-"))
            if r["stderr"].strip():
                lines.append("      stderr: %s" % r["stderr"].strip().replace("\n", " | ")[-300:])
            if not r["stdout"].strip():
                lines.append("      stdout: <EMPTY>")
        text = "\n".join(lines) + "\n"
        with open(os.path.join(SEAT, "attrib-%s.txt" % label), "w") as h:
            h.write(text)
        print("=== %s ===" % label)
        print(text)


if __name__ == "__main__":
    main()
