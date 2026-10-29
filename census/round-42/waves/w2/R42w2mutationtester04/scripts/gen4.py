#!/usr/bin/env python3
"""gen4.py — final probes: unbalanced fence, fence after corrections, derived= spelling, decoy row."""
import os
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
OUT = os.path.join(LANE, ".ufo/waves/round-42/w2/R42w2mutationtester04/mutants")
lesson_t = open(os.path.join(LANE, "corpus/lessons/round-42.md"), encoding="utf-8").read()
reg_t = open(os.path.join(LANE, "census/round-42/c1-register.tsv"), encoding="utf-8").read()
reg_lines = reg_t.split("\n")
HEADER = reg_lines[0]
rows = [l.split("\t") for l in reg_lines[1:] if l]
muts = []
def L(mid, t, d): muts.append((mid, "corpus/lessons/round-42.md", t.encode(), d))
def emit_reg(mid, newrows, d, header=HEADER):
    muts.append((mid, "census/round-42/c1-register.tsv",
                 (header + "\n" + "\n".join("\t".join(r) for r in newrows) + "\n").encode(), d))
def cp(): return [list(r) for r in rows]

anchor = "## Corrections to filed statements (C1)\n"
# L55: one unbalanced ``` inserted BEFORE the corrections section
L("L55", lesson_t.replace(anchor, "```\n" + anchor, 1),
  "insert one unbalanced ``` fence before the corrections section (mask every later correction)")
# L56: one unbalanced ``` inserted at the END of the lesson (after every correction)
L("L56", lesson_t + "\n```\n",
  "append one unbalanced ``` fence at the END of the lesson (after every correction)")
# L57: spell the derived= value differently on the line=175 correction
L("L57", lesson_t.replace("token=c2-after.tsv derived=path-absent", "token=c2-after.tsv derived=path_absent", 1),
  "change the derived= value of the line=175 CORRECTION-DE line (path-absent -> path_absent)")
# L58: change the rev= of the line=175 correction to the tip revision
L("L58", lesson_t.replace(
    "CORRECTION-DE line=175 token=c2-after.tsv derived=path-absent rev=bf618f6c5c09d302994871c94903abbea2deb60d",
    "CORRECTION-DE line=175 token=c2-after.tsv derived=path-absent rev=3105a63b23481fccf7df58e74d14a6681e0ea0c8", 1),
  "change the rev= revision of the line=175 CORRECTION-DE line to the tip revision")
# R34: a decoy row for a non-population key with a WRONG field count
emit_reg("R34", cp() + [["998", "decoy"]], "append a decoy register row with only two fields")
# R35: a decoy row for a non-population key with four fields and a bogus class
emit_reg("R35", cp() + [["997", "decoy2", "resolved", "corpus/knowledge/nope.md"]], "append a four-field decoy row for a non-population key")
# R36: change the class of the line=14 row to 'unresolved' but leave the row's resolved_to as '-'
r = cp()
r[[i for i, x in enumerate(r) if x[0] == "14" and x[1] == "65817d0d"][0]][2] = "unresolved"
emit_reg("R36", r, "restate the line=14 register row (control: class unresolved, resolved_to '-')")
# R37: change the token of the line=175 correction in the lesson to a RESOLVED item's token
L("R37", lesson_t.replace("CORRECTION-DE line=175 token=c2-after.tsv derived=path-absent",
                           "CORRECTION-DE line=175 token=c1-after.tsv derived=path-absent", 1),
  "change the token= of the line=175 CORRECTION-DE line to a resolved item's token")

for mid, rel, data, desc in muts:
    p = os.path.join(OUT, mid + (".md" if rel.endswith(".md") else ".tsv"))
    open(p, "wb").write(data)
    print("%s\t%s\t%d bytes\t%s" % (mid, rel, len(data), desc))
