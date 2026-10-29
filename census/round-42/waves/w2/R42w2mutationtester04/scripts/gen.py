#!/usr/bin/env python3
"""Generate single-point mutations of the landed C1 lesson + register (r42 w2, seat R42w2mutationtester04)."""
import os, shutil, sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SEAT = os.path.join(LANE, ".ufo/waves/round-42/w2/R42w2mutationtester04")
OUT = os.path.join(SEAT, "mutants")
LESSON_REL = "corpus/lessons/round-42.md"
REG_REL = "census/round-42/c1-register.tsv"

lesson = open(os.path.join(LANE, LESSON_REL), "rb").read()
reg = open(os.path.join(LANE, REG_REL), "rb").read()
lesson_t = lesson.decode()
reg_t = reg.decode()
reg_lines = reg_t.split("\n")
# rows (excluding header) as list of [line, token, class, resolved_to]
reg_rows = [l.split("\t") for l in reg_lines[1:] if l]

muts = []  # (id, target_rel, bytes, description)

def add(mid, rel, data, desc):
    muts.append((mid, rel, data, desc))

def L(mid, newtext, desc):
    add(mid, LESSON_REL, newtext.encode(), desc)

def R(mid, newrows_text, desc):
    add(mid, REG_REL, newrows_text.encode(), desc)

# ---------- lesson edits ----------
corr_lines = {}
for l in lesson_t.split("\n"):
    if l.startswith("CORRECTION-DE "):
        corr_lines[l.split(" ")[1]] = l  # "line=NN"
c14 = corr_lines["line=14"]
c68a = corr_lines["line=68"]

# L1-L5: delete each CORRECTION-DE line
for tag, cl in (("L1", c14), ("L2", c68a)):
    pass

def drop_line(text, line):
    ls = text.split("\n")
    ls.remove(line)
    return "\n".join(ls)

names = list(corr_lines.keys())
for i, key in enumerate(["line=14", "line=68", "line=92", "line=175"], start=1):
    # line=68 has two correction lines
    pass

# enumerate the five correction lines in file order
corr_order = [l for l in lesson_t.split("\n") if l.startswith("CORRECTION-DE ")]
assert len(corr_order) == 5, len(corr_order)

for i, cl in enumerate(corr_order, start=1):
    L("L%d" % i, drop_line(lesson_t, cl), "delete CORRECTION-DE line #%d (the %s one)" % (i, cl.split(" ")[1]))

# L6: alter token in the line=14 correction
L("L6", lesson_t.replace(corr_order[0].split(" ")[2], "token=65817d0e" if False else "token=65817d0e", 1)
  if False else lesson_t.replace("token=65817d0d derived=rev-unresolved", "token=65817d0e derived=rev-unresolved", 1),
  "alter one character of the token in the line=14 CORRECTION-DE line")
# L7: alter derived value of line=14
L("L7", lesson_t.replace("token=65817d0d derived=rev-unresolved", "token=65817d0d derived=path-absent", 1),
  "alter the derived= value of the line=14 CORRECTION-DE line")
# L8: alter one hex char of the sha256 in the first line=68 correction
L("L8", lesson_t.replace("derived=sha256=bb506469", "derived=sha256=bb506468", 1),
  "alter one hex character of the derived sha256 in the first line=68 CORRECTION-DE line")
# L9: alter rev= of the line=14 correction to a different 40-hex
L("L9", lesson_t.replace("rev=bf618f6c5c09d302994871c94903abbea2deb60d\n", "rev=0000000000000000000000000000000000000000\n", 1),
  "alter the rev= revision of the line=14 CORRECTION-DE line")
# L10: alter the line= number of the line=14 correction
L("L10", lesson_t.replace("CORRECTION-DE line=14 token=65817d0d", "CORRECTION-DE line=15 token=65817d0d", 1),
  "alter the line= number of the line=14 CORRECTION-DE line")
# L11: duplicate the line=14 correction
L("L11", lesson_t.replace(corr_order[0] + "\n", corr_order[0] + "\n" + corr_order[0] + "\n", 1),
  "duplicate the line=14 CORRECTION-DE line")
# L12: wrap the line=14 correction in a ``` fence
L("L12", lesson_t.replace(corr_order[0] + "\n", "```\n" + corr_order[0] + "\n```\n", 1),
  "move the line=14 CORRECTION-DE line inside a triple-backtick fence")
# L13: wrap it in a ~~~ tilde fence
L("L13", lesson_t.replace(corr_order[0] + "\n", "~~~\n" + corr_order[0] + "\n~~~\n", 1),
  "move the line=14 CORRECTION-DE line inside a ~~~ tilde fence")
# L14: wrap it in a four-backtick fence
L("L14", lesson_t.replace(corr_order[0] + "\n", "````\n" + corr_order[0] + "\n````\n", 1),
  "move the line=14 CORRECTION-DE line inside a four-backtick fence")
# L15: prose: 5 -> 6 in the summary sentence
L("L15", lesson_t.replace("and 5 do not", "and 6 do not", 1),
  "prose edit: change 'and 5 do not' to 'and 6 do not' in the C1 summary paragraph")
# L16: prose: swap the two digest meanings in the line=68 section
L("L16", lesson_t.replace("`42259756…` is the sha256 of `tests/fixtures/r24-coverage-agreement.py`",
                           "`42259756…` is the sha256 of `tests/fixtures/r23-coverage-agreement.py`", 1),
  "prose edit: falsify the file name the 42259756 digest is attributed to")
# L17: prose heading line number
L("L17", lesson_t.replace("### SCORECARD.md:14 — `65817d0d`", "### SCORECARD.md:15 — `65817d0d`", 1),
  "prose edit: change the SCORECARD.md line number in a correction heading")
# L18: prose heading of the whole section
L("L18", lesson_t.replace("## Corrections to filed statements (C1)", "## Corrections to filed statements (C1) [DRAFT]", 1),
  "prose edit: change the C1 corrections section heading")
# L19: add a new prose section with false claims
L("L19", lesson_t + "\n## Extra claims\n\nAll 70 items are resolved to committed paths and no correction is required.\n",
  "prose edit: append a false 'all resolved, no correction needed' section")
# L20: CRLF the whole lesson
L("L20", lesson_t.replace("\n", "\r\n").encode().decode(), "convert the whole lesson to CRLF line endings")
# L21: lowercase the marker
L("L21", lesson_t.replace("CORRECTION-DE line=14", "Correction-DE line=14", 1),
  "alter the marker case of the line=14 CORRECTION-DE line")
# L22: leading space before the marker
L("L22", lesson_t.replace(corr_order[0] + "\n", " " + corr_order[0] + "\n", 1),
  "indent the line=14 CORRECTION-DE line by one space")
# L23: trailing space after the line
L("L23", lesson_t.replace(corr_order[0] + "\n", corr_order[0] + " \n", 1),
  "append a trailing space to the line=14 CORRECTION-DE line")
# L24: prose line mentioning the marker
L("L24", lesson_t.replace("The lines below are the counter's `corrected=` population",
                          "The lines below are the counter's `corrected=` population; each is a CORRECTION-DE record",
                          1),
  "prose edit: mention the marker CORRECTION-DE inside a prose sentence")
# L25: move the line=14 correction into the Mistakes section
anchor = "## Mistakes\n"
L("L25", lesson_t.replace(corr_order[0] + "\n", "", 1).replace(anchor, anchor + "\n" + corr_order[0] + "\n", 1),
  "move the line=14 CORRECTION-DE line into the Mistakes section")
# L26: trailing tab after the line
L("L26", lesson_t.replace(corr_order[0] + "\n", corr_order[0] + "\t\n", 1),
  "append a trailing tab to the line=14 CORRECTION-DE line")
# L27: derived=sha256=? in a digest correction
L("L27", lesson_t.replace("derived=sha256=bb506469be860f994f74f4c7d6eb1c949a4931b676cdb60f9f79de041d12f27f",
                           "derived=sha256=?", 1),
  "alter the derived= value of the first line=68 CORRECTION-DE line")
# L28: uppercase hex in rev=
L("L28", lesson_t.replace("rev=bf618f6c5c09d302994871c94903abbea2deb60d",
                           "rev=BF618F6C5C09D302994871C94903ABBEA2DEB60D", 1),
  "uppercase the rev= revision hex of the line=14 CORRECTION-DE line")
# L29: double space between fields
L("L29", lesson_t.replace(corr_order[0], corr_order[0].replace(" token=", "  token="), 1),
  "double the space between two fields of the line=14 CORRECTION-DE line")
# L30: delete the prose scope paragraph of the line=14 section but keep the correction line
scope14 = ("The instrument read the token as a revision (class B) and `git cat-file -e 65817d0d^{commit}` fails at the base. The value derived is a statement about that\n"
           "command only. Cause (R42scout01, R42critic01 N11, both reproduced the sweep): `65817d0d` is the first eight hex digits of the sha256 of a\n"
           "`tools/souji-declared-evidence.py` blob (full value `65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4`), a truncated tool digest, not a revision. The SCORECARD cell was\n"
           "not wrong about the tool; the instrument's class-B scanner mistook a digest prefix for a revision.\n")
assert scope14 in lesson_t, "scope14 paragraph not found verbatim"
L("L30", lesson_t.replace(scope14, "", 1),
  "delete the whole prose scope paragraph of the line=14 section, keeping the CORRECTION-DE line")
# L31: alter an attribution in prose
L("L31", lesson_t.replace("(R42scout01, R42critic01 N11, both reproduced the sweep)",
                           "(R42scout01, R42critic01 N11, neither reproduced the sweep)", 1),
  "prose edit: falsify an attribution inside the line=14 scope paragraph")
# L32: falsify the prose that states what the derived value means
L("L32", lesson_t.replace("The derived value\n`path-absent` is a statement about the token as written (no tree path equals it), not about the file the row means.",
                           "The derived value\n`path-absent` is a statement about the r24 artifact `census/round-24/records/c2-after.tsv` itself.",
                           1),
  "prose edit: falsify the scope sentence of the line=175 correction")
# L33: delete the prose paragraph of the line=175 section, keeping its CORRECTION-DE line
prose175 = ("A bare basename that matches five committed paths (`census/round-24..28/records/c2-after.tsv`). The row sits in the Capabilities table whose nearest `Round N` heading is\n"
            "`Round 23`, so the counter's heading-context rule selects none. R42scout02: the cell means the r24 artifact `census/round-24/records/c2-after.tsv`. The derived value\n"
            "`path-absent` is a statement about the token as written (no tree path equals it), not about the file the row means.\n")
assert prose175 in lesson_t, "prose175 not found verbatim"
L("L33", lesson_t.replace(prose175, "", 1),
  "delete the prose paragraph of the line=175 section, keeping its CORRECTION-DE line")
# L34: change the "65 resolve to one committed path, 5 do not" numbers
L("L34", lesson_t.replace("65 resolve to one committed path by the counter's", "64 resolve to one committed path by the counter's", 1),
  "prose edit: change '65 resolve' to '64 resolve'")
# L35: change the counter name in prose
L("L35", lesson_t.replace("The lines below are the counter's `corrected=` population",
                           "The lines below are the counter's `corrected` population", 1),
  "prose edit: remove a backtick pair in a prose sentence")

# ---------- register edits ----------
def reg_text(rows, header="line\ttoken\tclass\tresolved_to"):
    return header + "\n" + "\n".join("\t".join(r) for r in rows) + "\n"

def find_row(line, token, idx=0):
    hits = [list(r) for r in reg_rows if r[0] == str(line) and r[1] == token]
    return hits[idx]

rows = [list(r) for r in reg_rows]

def R_rows(mid, newrows, desc):
    R(mid, reg_text(newrows), desc)

# R1: class unresolved -> resolved on the line=14 row
nr = [list(r) for r in rows]; r = find_row("14", "65817d0d"); r[2] = "resolved"
R_rows("R1", nr, "change the register class of the line=14 row from unresolved to resolved")
# R2: resolved_to '-' -> a real path on the line=14 row
nr = [list(r) for r in rows]; r = find_row("14", "65817d0d"); r[3] = "census/round-42/c1-items.tsv"
R_rows("R2", nr, "change the resolved_to field of the line=14 row from '-' to a real path")
# R3: one character of a resolved_to path
nr = [list(r) for r in rows]; r = find_row("21", "c1-after.tsv"); r[3] = "census/round-28/records/c1-after.tsv".replace("round-28", "round-29")
R_rows("R3", nr, "change one character of a resolved_to path (round-28 -> round-29)")
# R4: delete the line=14 row
nr = [list(r) for r in rows if not (r[0] == "14" and r[1] == "65817d0d")]
R_rows("R4", nr, "delete the register row for the line=14 item")
# R5: delete one of the two identical rows for (668, c2-after2.tsv)
nr = [list(r) for r in rows]; rm = False; out = []
for r in nr:
    if r[0] == "668" and r[1] == "c2-after2.tsv" and not rm:
        rm = True; continue
    out.append(r)
R_rows("R5", out, "delete one of the two identical register rows for the line=668 c2-after2.tsv item")
# R6: duplicate the row for the line=21 item
nr = [list(r) for r in rows]
ins = [i for i, r in enumerate(nr) if r[0] == "21" and r[1] == "c1-after.tsv"][0]
nr.insert(ins + 1, list(nr[ins]))
R_rows("R6", nr, "duplicate the register row for the line=21 item")
# R7: rewrite the header row
R_rows("R7", rows, "rewrite the header row (header content is unread by the counter)") if False else None
nr = [list(r) for r in rows]
R("R7", reg_text(nr, header="ln\ttok\tkind\tpath"), "rewrite the register header row")
# R8: append an extra row for a key that is not in the population
nr = [list(r) for r in rows]; nr.append(["999", "bogus-token", "resolved", "corpus/knowledge/nonexistent.md"])
R_rows("R8", nr, "append an extra register row for a key absent from the 70-item population")
# R9: swap two rows (order change)
nr = [list(r) for r in rows]
i1 = [i for i, r in enumerate(nr) if r[0] == "21"][0]
i2 = [i for i, r in enumerate(nr) if r[0] == "22"][0]
nr[i1], nr[i2] = nr[i2], nr[i1]
R_rows("R9", nr, "swap two register rows (order change only)")
# R10: CRLF the register
R("R10", reg_text(rows).replace("\n", "\r\n"), "convert the whole register to CRLF line endings")
# R11: trailing tab on a row (5 fields)
nr = [list(r) for r in rows]; nr[1] = nr[1] + [""]
R_rows("R11", nr, "append a trailing tab to a register row (a fifth field)")
# R12: change the line number of a row
nr = [list(r) for r in rows]; r = find_row("21", "c1-after.tsv"); r[0] = "22"
R_rows("R12", nr, "change the line= field of the line=21 register row")
# R13: change the token of a row
nr = [list(r) for r in rows]; r = find_row("21", "c1-after.tsv"); r[1] = "c1-afterX.tsv"
R_rows("R13", nr, "change the token= field of the line=21 register row")
# R14: class resolved -> unresolved on a resolved row
nr = [list(r) for r in rows]; r = find_row("21", "c1-after.tsv"); r[2] = "unresolved"
R_rows("R14", nr, "change the register class of the line=21 row from resolved to unresolved")
# R15: remove the trailing newline of the register
R("R15", reg_text(rows).rstrip("\n"), "remove the trailing newline of the register")
# R16: prefix a resolved_to path with ./
nr = [list(r) for r in rows]; r = find_row("21", "c1-after.tsv"); r[3] = "./" + r[3]
R_rows("R16", nr, "prefix a resolved_to path with './'")
# R17: add a comment line
R("R17", reg_text(rows).replace("line\ttoken\tclass\tresolved_to\n", "line\ttoken\tclass\tresolved_to\n# register for r42 C1\n", 1),
  "insert a '#' comment line into the register")
# R18: blank line in the middle
R("R18", reg_text(rows).replace("22\tc2-after.tsv", "\n22\tc2-after.tsv", 1),
  "insert a blank line into the register")
# R19: change the class of a resolved row to 'resolved ' (trailing space)
nr = [list(r) for r in rows]; r = find_row("21", "c1-after.tsv"); r[2] = "resolved "
R_rows("R19", nr, "add a trailing space to the class= field of the line=21 register row")
# R20: swap the resolved_to of two resolved rows
nr = [list(r) for r in rows]
ra = find_row("21", "c1-after.tsv"); rb = find_row("22", "c2-after.tsv")
ra[3], rb[3] = rb[3], ra[3]
R_rows("R20", nr, "swap the resolved_to values of the line=21 and line=22 register rows")

# L36: prose edit - falsify the claim that the register agrees with the SCORECARD cell
L("L36", lesson_t.replace("R42scribe01-05 each read 13 rows against the SCORECARD cell and the file: 65 agree, 0 disagree",
                           "R42scribe01-05 each read 13 rows against the SCORECARD cell and the file: 61 agree, 4 disagree", 1),
  "prose edit: falsify the reader agreement count (65 agree -> 61 agree)")
# L37: prose edit - falsify the rev of the whole lesson
L("L37", lesson_t.replace("Base revision: `bf618f6c5c09d302994871c94903abbea2deb60d`",
                           "Base revision: `bf618f6c5c09d302994871c94903abbea2deb60e`", 1),
  "prose edit: alter the base revision quoted in the lesson header")
# L38: prose edit - delete the five-line correction list summary sentence
L("L38", lesson_t.replace("The lines below are the counter's `corrected=` population; the prose around each says what the value does and does not mean.\n", "", 1),
  "prose edit: delete the sentence that declares what the correction lines are")
# L39: move a CORRECTION-DE line into a markdown list item (leading '- ')
L("L39", lesson_t.replace(corr_order[1] + "\n", "- " + corr_order[1] + "\n", 1),
  "turn the first line=68 CORRECTION-DE line into a markdown list item")
# L40: prose edit - swap the two digests' correction prose
L("L40", lesson_t.replace("- `71b89eb3…` is the sha256 of `tools/souji-coverage-agreement.py` as it was at `1efe406…` (r24 bytes).",
                           "- `71b89eb3…` is the sha256 of `tools/souji-size-census.py` as it was at `1efe406…` (r24 bytes).", 1),
  "prose edit: attribute the 71b89eb3 digest to a different tool")
# R21: add a second row for a key that already has one, with a DIFFERENT class (multiplicity check)
nr = [list(r) for r in rows]
ins = [i for i, r in enumerate(nr) if r[0] == "14"][0]
nr.insert(ins + 1, ["14", "65817d0d", "resolved", "-"])
R_rows("R21", nr, "add a second register row for the line=14 key with a different class")
# R22: change the class of every unresolved row to resolved
nr = [list(r) for r in rows]
for r in nr:
    if r[2] == "unresolved":
        r[2] = "resolved"
R_rows("R22", nr, "change the class of every unresolved register row to resolved")
# R23: delete every unresolved row (5 of them)
nr = [list(r) for r in rows if r[2] != "unresolved"]
R_rows("R23", nr, "delete all five unresolved register rows")
# R24: change the class word of the line=14 row to UNRESOLVED (case)
nr = [list(r) for r in rows]; r = find_row("14", "65817d0d"); r[2] = "UNRESOLVED"
R_rows("R24", nr, "uppercase the class= field of the line=14 register row")
# R25: rewrite the resolved_to of the line=14 row to the empty string
nr = [list(r) for r in rows]; r = find_row("14", "65817d0d"); r[3] = ""
R_rows("R25", nr, "empty the resolved_to field of the line=14 register row")

os.makedirs(OUT, exist_ok=True)
manifest = []
for mid, rel, data, desc in muts:
    path = os.path.join(OUT, mid + (".md" if rel.endswith(".md") else ".tsv"))
    with open(path, "wb") as h:
        h.write(data)
    manifest.append("%s\t%s\t%s" % (mid, rel, desc))
with open(os.path.join(OUT, "MANIFEST.tsv"), "w") as h:
    h.write("id\tdest\tdescription\n" + "\n".join(manifest) + "\n")
print("mutants written: %d" % len(muts))
for mid, rel, data, desc in muts:
    print("%s\t%s\t%d bytes\t%s" % (mid, rel, len(data), desc))
