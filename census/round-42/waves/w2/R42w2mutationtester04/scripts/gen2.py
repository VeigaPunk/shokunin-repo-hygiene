#!/usr/bin/env python3
"""gen2.py — regenerate the register mutants correctly (find_row must mutate the emitted rows)
and add extra lesson mutants. Seat R42w2mutationtester04."""
import os

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SEAT = os.path.join(LANE, ".ufo/waves/round-42/w2/R42w2mutationtester04")
OUT = os.path.join(SEAT, "mutants")
LESSON_REL = "corpus/lessons/round-42.md"
REG_REL = "census/round-42/c1-register.tsv"

lesson_t = open(os.path.join(LANE, LESSON_REL), encoding="utf-8").read()
reg_t = open(os.path.join(LANE, REG_REL), encoding="utf-8").read()
reg_lines = reg_t.split("\n")
HEADER = reg_lines[0]
rows = [l.split("\t") for l in reg_lines[1:] if l]

corr_order = [l for l in lesson_t.split("\n") if l.startswith("CORRECTION-DE ")]
assert len(corr_order) == 5

muts = []


def emit_reg(mid, newrows, desc, header=HEADER):
    body = header + "\n" + "\n".join("\t".join(r) for r in newrows)
    muts.append((mid, REG_REL, (body + "\n").encode(), desc))


def emit_reg_raw(mid, text, desc):
    muts.append((mid, REG_REL, text.encode(), desc))


def idx(rows_, line, token, n=0):
    hits = [i for i, r in enumerate(rows_) if r[0] == line and r[1] == token]
    return hits[n]


def cp():
    return [list(r) for r in rows]


# R1: class unresolved -> resolved on the line=14 row
r = cp(); r[idx(r, "14", "65817d0d")][2] = "resolved"
emit_reg("R1", r, "change the register class of the line=14 row from unresolved to resolved")
# R2: resolved_to '-' -> real path on the line=14 row
r = cp(); r[idx(r, "14", "65817d0d")][3] = "census/round-42/c1-items.tsv"
emit_reg("R2", r, "change the resolved_to field of the line=14 row from '-' to a real path")
# R3: one character of a resolved_to path
r = cp(); r[idx(r, "21", "c1-after.tsv")][3] = "census/round-29/records/c1-after.tsv"
emit_reg("R3", r, "change one character of a resolved_to path (round-28 -> round-29)")
# R4: delete the line=14 row
r = cp(); i = idx(r, "14", "65817d0d"); del r[i]
emit_reg("R4", r, "delete the register row for the line=14 item")
# R5: delete one of the two identical rows of a duplicated key (667 c2-after2.txt)
r = cp(); i = idx(r, "667", "c2-after2.txt"); del r[i]
emit_reg("R5", r, "delete one of the two identical register rows for the duplicated key 667/c2-after2.txt")
# R6: duplicate the row for the line=21 item
r = cp(); i = idx(r, "21", "c1-after.tsv"); r.insert(i + 1, list(r[i]))
emit_reg("R6", r, "duplicate the register row for the line=21 item")
# R7: rewrite the header row
emit_reg("R7", cp(), "rewrite the register header row (header content is unread by the counter)",
         header="ln\ttok\tkind\tpath")
# R8: append an extra row for a key absent from the population
r = cp(); r.append(["999", "bogus-token", "resolved", "corpus/knowledge/nonexistent.md"])
emit_reg("R8", r, "append an extra register row for a key absent from the 70-item population")
# R9: swap two rows (order change)
r = cp(); a = idx(r, "21", "c1-after.tsv"); b = idx(r, "22", "c2-after.tsv")
r[a], r[b] = r[b], r[a]
emit_reg("R9", r, "swap two register rows (order change only)")
# R10: CRLF the register
emit_reg_raw("R10", (HEADER + "\n" + "\n".join("\t".join(x) for x in rows) + "\n").replace("\n", "\r\n"),
             "convert the whole register to CRLF line endings")
# R11: trailing tab on a row (5 fields)
r = cp(); r[1] = r[1] + [""]
emit_reg("R11", r, "append a trailing tab to a register row (a fifth field)")
# R12: change the line= field of a row
r = cp(); r[idx(r, "21", "c1-after.tsv")][0] = "22"
emit_reg("R12", r, "change the line= field of the line=21 register row")
# R13: change the token= field of a row
r = cp(); r[idx(r, "21", "c1-after.tsv")][1] = "c1-afterX.tsv"
emit_reg("R13", r, "change the token= field of the line=21 register row")
# R14: class resolved -> unresolved on a resolved row
r = cp(); r[idx(r, "21", "c1-after.tsv")][2] = "unresolved"
emit_reg("R14", r, "change the register class of the line=21 row from resolved to unresolved")
# R15: remove the trailing newline
emit_reg_raw("R15", HEADER + "\n" + "\n".join("\t".join(x) for x in rows), "remove the trailing newline of the register")
# R16: prefix a resolved_to path with ./
r = cp(); i = idx(r, "21", "c1-after.tsv"); r[i][3] = "./" + r[i][3]
emit_reg("R16", r, "prefix a resolved_to path with './'")
# R17: comment line
emit_reg_raw("R17", (HEADER + "\n# register for r42 C1\n" + "\n".join("\t".join(x) for x in rows) + "\n"),
             "insert a '#' comment line into the register")
# R18: blank line in the middle
emit_reg_raw("R18", (HEADER + "\n" + "\n".join("\t".join(x) for x in rows) + "\n").replace(
    "22\tc2-after.tsv", "\n22\tc2-after.tsv", 1), "insert a blank line into the register")
# R19: trailing space in the class= field
r = cp(); r[idx(r, "21", "c1-after.tsv")][2] = "resolved "
emit_reg("R19", r, "add a trailing space to the class= field of the line=21 register row")
# R20: swap the resolved_to of two resolved rows
r = cp(); a = idx(r, "21", "c1-after.tsv"); b = idx(r, "22", "c2-after.tsv")
r[a][3], r[b][3] = r[b][3], r[a][3]
emit_reg("R20", r, "swap the resolved_to values of the line=21 and line=22 register rows")
# R21: second row for the line=14 key with a different class
r = cp(); i = idx(r, "14", "65817d0d"); r.insert(i + 1, ["14", "65817d0d", "resolved", "-"])
emit_reg("R21", r, "add a second register row for the line=14 key with a different class")
# R22: every unresolved row relabelled resolved
r = cp()
for x in r:
    if x[2] == "unresolved":
        x[2] = "resolved"
emit_reg("R22", r, "change the class of every unresolved register row to resolved")
# R23: delete all five unresolved rows
r = cp()
r = [x for x in r if x[2] != "unresolved"]
emit_reg("R23", r, "delete all five unresolved register rows")
# R24: uppercase the class= field
r = cp(); r[idx(r, "14", "65817d0d")][2] = "UNRESOLVED"
emit_reg("R24", r, "uppercase the class= field of the line=14 register row")
# R25: empty the resolved_to field of the line=14 row
r = cp(); r[idx(r, "14", "65817d0d")][3] = ""
emit_reg("R25", r, "empty the resolved_to field of the line=14 register row")
# R26: trailing whitespace after a resolved_to path
r = cp(); i = idx(r, "21", "c1-after.tsv"); r[i][3] = r[i][3] + " "
emit_reg("R26", r, "append a trailing space to the resolved_to path of the line=21 register row")
# R27: point a resolved row at another existing committed file
r = cp(); i = idx(r, "21", "c1-after.tsv"); r[i][3] = "census/round-38/records/c2-after2.txt"
emit_reg("R27", r, "point the line=21 register row at a different existing committed path")
# R28: move the whole register's rows under a wrong header (header unread)
emit_reg("R28", cp(), "relabel the header to 'a b c d' (any header content is unread)",
         header="a\tb\tc\td")
# R29: append a duplicate of the LAST row (a duplicated key keeps multiplicity 2 -> still ok?)
r = cp(); r.append(list(r[-1]))
emit_reg("R29", r, "append a duplicate of the last register row (duplicating an already-duplicated key)")

# ---- extra lesson mutants ----
def L(mid, newtext, desc):
    muts.append((mid, LESSON_REL, newtext.encode(), desc))

# L41: reorder the five correction lines (move the line=175 one to the top of the section)
lines = lesson_t.split("\n")
i175 = lines.index(corr_order[4])
sec = lines.index("## Corrections to filed statements (C1)")
del lines[i175]
lines.insert(sec + 2, corr_order[4])
L("L41", "\n".join(lines), "move the line=175 CORRECTION-DE line to the top of the corrections section")
# L42: change the line= number of the line=92 correction to 175
L("L42", lesson_t.replace("CORRECTION-DE line=92 token=09bb8e0d", "CORRECTION-DE line=175 token=09bb8e0d", 1),
  "change the line= number of the line=92 CORRECTION-DE line to 175")
# L43: change the derived= of the path-absent correction
L("L43", lesson_t.replace("token=c2-after.tsv derived=path-absent", "token=c2-after.tsv derived=rev-unresolved", 1),
  "change the derived= value of the line=175 CORRECTION-DE line")
# L44: change the token of the line=92 correction
L("L44", lesson_t.replace("CORRECTION-DE line=92 token=09bb8e0d", "CORRECTION-DE line=92 token=09bb8e0e", 1),
  "change the token= of the line=92 CORRECTION-DE line")
# L45: delete the C1 corrections section heading
L("L45", lesson_t.replace("## Corrections to filed statements (C1)\n", "", 1),
  "delete the '## Corrections to filed statements (C1)' section heading")
# L46: append a CORRECTION-DE line for a RESOLVED item
L("L46", lesson_t + "\nCORRECTION-DE line=21 token=c1-after.tsv derived=path-absent rev=bf618f6c5c09d302994871c94903abbea2deb60d\n",
  "append a CORRECTION-DE line for a resolved item (line=21)")
# L47: give the line=14 correction a trailing comma after the token
L("L47", lesson_t.replace("token=65817d0d derived=rev-unresolved", "token=65817d0d, derived=rev-unresolved", 1),
  "append a comma to the token= field of the line=14 CORRECTION-DE line")
# L48: change the second line=68 correction's derived sha256
L("L48", lesson_t.replace(
    "CORRECTION-DE line=68 token=71b89eb3c7ce417979c5fce2c759dafe023af21d6310fde49197c766b8f28897 derived=sha256=bb506469be860f994f74f4c7d6eb1c949a4931b676cdb60f9f79de041d12f27f",
    "CORRECTION-DE line=68 token=71b89eb3c7ce417979c5fce2c759dafe023af21d6310fde49197c766b8f28897 derived=sha256=0000000000000000000000000000000000000000000000000000000000000000", 1),
  "change the derived sha256 of the second line=68 CORRECTION-DE line")
# L49: put the line=14 correction inside an indented code block (4 spaces)
L("L49", lesson_t.replace(corr_order[0] + "\n", "    " + corr_order[0] + "\n", 1),
  "indent the line=14 CORRECTION-DE line by four spaces (indented code block)")
# L50: two consecutive corrections on one line
L("L50", lesson_t.replace(corr_order[0] + "\n", corr_order[0] + " " + corr_order[1] + "\n", 1),
  "join two CORRECTION-DE lines onto one physical line")

os.makedirs(OUT, exist_ok=True)
for mid, rel, data, desc in muts:
    path = os.path.join(OUT, mid + (".md" if rel.endswith(".md") else ".tsv"))
    with open(path, "wb") as h:
        h.write(data)
    print("%s\t%s\t%d bytes\t%s" % (mid, rel, len(data), desc))
print("TOTAL %d" % len(muts))
