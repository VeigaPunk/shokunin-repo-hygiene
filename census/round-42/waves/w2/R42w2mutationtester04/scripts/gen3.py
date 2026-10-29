#!/usr/bin/env python3
"""gen3.py — extra probe mutants: leading zeros in line=, uppercase token, four-backtick fence check."""
import os
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SEAT = os.path.join(LANE, ".ufo/waves/round-42/w2/R42w2mutationtester04")
OUT = os.path.join(SEAT, "mutants")
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
def idx(rs, line, token, n=0):
    return [i for i, r in enumerate(rs) if r[0] == line and r[1] == token][n]

# L51: leading zeros in the line= field of a CORRECTION-DE line
L("L51", lesson_t.replace("CORRECTION-DE line=14 token=65817d0d", "CORRECTION-DE line=014 token=65817d0d", 1),
  "write the line= field of the line=14 CORRECTION-DE line with leading zeros (014)")
# L52: four-backtick fence but with the correction outside (control for L14)
L("L52", lesson_t.replace("````\n", "```` \n", 1) if "````\n" in lesson_t else
  lesson_t.replace("CORRECTION-DE line=14 token=65817d0d", "CORRECTION-DE line=14 token=65817d0d", 1),
  "control: no four-backtick fence present in the lesson (no-op check)")
# L53: a markdown blockquote '>' before the marker
L("L53", lesson_t.replace("CORRECTION-DE line=14 token=65817d0d", "> CORRECTION-DE line=14 token=65817d0d", 1),
  "prefix the line=14 CORRECTION-DE line with a markdown blockquote marker")
# L54: move the line=14 correction into an HTML comment
L("L54", lesson_t.replace("CORRECTION-DE line=14 token=65817d0d", "<!-- CORRECTION-DE line=14 token=65817d0d", 1)
  .replace("derived=rev-unresolved rev=bf618f6c5c09d302994871c94903abbea2deb60d",
           "derived=rev-unresolved rev=bf618f6c5c09d302994871c94903abbea2deb60d -->", 1),
  "wrap the line=14 CORRECTION-DE line in an HTML comment")
# R30: leading zeros in the line= field of the register row for the line=14 item
r = cp(); i = idx(r, "14", "65817d0d"); r[i][0] = "014"
emit_reg("R30", r, "write the line= field of the line=14 register row with leading zeros (014)")
# R31: uppercase the token of the line=14 register row
r = cp(); i = idx(r, "14", "65817d0d"); r[i][1] = "65817D0D"
emit_reg("R31", r, "uppercase the token= field of the line=14 register row")
# R32: change the class of the line=14 row to 'unresolved ' (trailing space)
r = cp(); i = idx(r, "14", "65817d0d"); r[i][2] = "unresolved "
emit_reg("R32", r, "add a trailing space to the class= field of the line=14 register row")
# R33: swap the token= fields of two rows that carry the same token
r = cp(); a = idx(r, "667", "c2-after2.txt"); b = idx(r, "667", "c2-after2.txt", 1)
r[a][3] = "census/round-38/records/c3-after2.txt"
emit_reg("R33", r, "point one of the two duplicated 667/c2-after2.txt rows at a different existing path")

for mid, rel, data, desc in muts:
    p = os.path.join(OUT, mid + (".md" if rel.endswith(".md") else ".tsv"))
    open(p, "wb").write(data)
    print("%s\t%s\t%d bytes\t%s" % (mid, rel, len(data), desc))
