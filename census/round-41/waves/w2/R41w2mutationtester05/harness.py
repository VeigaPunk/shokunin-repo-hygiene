#!/usr/bin/env python3
# R41w2mutationtester05 harness: mutate census/round-41/c1-counter.py (text substitutions, each asserted
# to match exactly once), run every mutant against frozen inputs (landed, do-nothing, junk control) and
# crafted inputs built in a scratch clone of the lane, and tabulate verdict/evidence differences.
import concurrent.futures as cf
import hashlib
import json
import os
import re
import subprocess
import sys

S = "/fast/scratch/hyaku/souji-r41/R41w2mutationtester05"
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
BASE = "31e4d3e758bb903808a9270018d7e5be99ce38a4"
NOTHING = "6682b98175b995ee4646ffd1ea6bd8a12cd353dd"
MEAS = "bffcc0f660ff36eb8add3f61582748a7af019a5b"
BASE_RC = "7eebc183f2685d1ea9b004b4de22c09a8a4035a7"
C = os.path.join(S, "clone")
ENV = dict(os.environ, TMPDIR=S, GIT_AUTHOR_NAME="fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
           GIT_COMMITTER_NAME="fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid")
CTR = "census/round-41/c1-counter.py"
ITEMS = "census/round-41/c1-items.tsv"
JUNK = "census/round-41/controls/c1-junk-round-41.md"
LESSON = "corpus/lessons/round-41.md"
REG = "corpus/SOURCES.md"
R40 = "corpus/lessons/round-40.md"
SC = "SCORECARD.md"
LOG = "LOG.md"
PIN = {CTR: "8860dc7af55848db3d67d11aec69cd8ee1f5a413964dd32ac7baddcebe49ab63",
       ITEMS: "2d2a548e253b7863cd9679ebe9f1f851a10223e47d3456e33345279b79a036cf"}


def sh(args, inp=None, cwd=None):
    return subprocess.run(args, input=inp, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV, cwd=cwd, check=False)


def G(*a):
    p = sh(["git", "-C", C, *a])
    if p.returncode != 0:
        raise SystemExit("git %r rc=%d: %s" % (a, p.returncode, p.stderr.decode()))
    return p.stdout


def show(path, rev=BASE):
    p = sh(["git", "-C", LANE, "show", "%s:%s" % (rev, path)])
    if p.returncode != 0:
        raise SystemExit("show %s:%s failed" % (rev, path))
    return p.stdout


def sha(b):
    return hashlib.sha256(b).hexdigest()


# ---- pinned bytes ----
ctr_src = show(CTR)
assert sha(ctr_src) == PIN[CTR], "counter at BASE differs from pinned digest"
assert sha(show(ITEMS)) == PIN[ITEMS], "items at BASE differ from pinned digest"
print("pinned: counter and items digests match at BASE", flush=True)

# ---- scratch clone (lane is only read) ----
os.makedirs(S, exist_ok=True)
if not os.path.isdir(C):
    p = sh(["git", "clone", "-q", "--shared", LANE, C])
    assert p.returncode == 0, p.stderr
assert os.path.realpath(G("rev-parse", "--show-toplevel").decode().strip()) == os.path.realpath(C)


def variant(name, edits):
    G("checkout", "-q", "-f", "--detach", BASE)
    for path, data in edits:
        full = os.path.join(C, path)
        if data is None:
            if os.path.exists(full):
                os.remove(full)
        else:
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "wb") as f:
                f.write(data)
    G("add", "-A")
    G("commit", "-q", "--allow-empty", "-m", "r41 mutation probe input: " + name)
    return G("rev-parse", "HEAD").decode().strip()


# ---- lesson helpers ----
PAT = re.compile(r"^CORRECTION (\S+) file=(\S+) filed=(\S+) derived=(\S+) rev=(\S+) source=(\S+)\s*$")
lesson_text = show(LESSON).decode()
assert lesson_text.endswith("\n")
landed_fields = {}
for l in lesson_text.split("\n"):
    m = PAT.match(l)
    if m:
        landed_fields[m.group(1)] = dict(file=m.group(2), filed=m.group(3), derived=m.group(4), rev=m.group(5),
                                         source=m.group(6))
assert set(landed_fields) == {"I1", "I3", "I4"}, landed_fields


def fmt(i, f):
    return "CORRECTION %s file=%s filed=%s derived=%s rev=%s source=%s" % (
        i, f["file"], f["filed"], f["derived"], f["rev"], f["source"])


WRONG = dict(file="corpus/SOURCES.md", filed="wrong-claim", derived="wrong=0", rev=BASE_RC, source="S258")


def lesson_edit(replace=None, drop=(), add=()):
    replace = replace or {}
    out = []
    for l in lesson_text.split("\n")[:-1]:
        m = PAT.match(l)
        if m and m.group(1) in drop:
            continue
        if m and m.group(1) in replace:
            f = dict(landed_fields[m.group(1)])
            f.update(replace[m.group(1)])
            out.append(fmt(m.group(1), f))
            continue
        out.append(l)
    out += list(add)
    return ("\n".join(out) + "\n").encode()


def line_edit(text, idx_pred, fn):
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if idx_pred(l)]
    assert len(hits) == 1, hits
    lines[hits[0]] = fn(lines[hits[0]])
    return "\n".join(lines)


def cells_edit(fn):
    def f(line):
        p = line.split("|")
        fn(p)
        return "|".join(p)
    return f


reg_text = show(REG).decode()
assert len(reg_text.split("| S258 |")) == 2
s258 = [l for l in reg_text.split("\n") if l.startswith("| S258 |")][0]
assert len(s258.split("|")) == 13, len(s258.split("|"))

r40 = show(R40)
sc = show(SC)
log = show(LOG)
items_b = show(ITEMS)
assert r40.count(b"appears in 9 rows") == 1
assert items_b.startswith(b"id\tfile")


def first_line_edit(b):
    return b.replace(b"\n", b" (edited)\n", 1)


# ---- crafted inputs (commits in the scratch clone) ----
INPUTS = {}  # name -> (rev, frozen?)
junk_rev = variant("junk-control", [(LESSON, show(JUNK))])
INPUTS["junk"] = (junk_rev, True)
INPUTS["landed"] = (BASE, True)
INPUTS["nothing"] = (NOTHING, True)

crafted = []
crafted.append(("X01-unknown-id", [(LESSON, lesson_edit(add=["CORRECTION I9 file=corpus/lessons/round-40.md filed=9-rows derived=rows=2,v2.56.0=0 rev=%s source=-" % MEAS]))]))
for i in ("I1", "I3", "I4"):
    for f in ("file", "filed", "derived", "rev"):
        crafted.append(("A-%s-%s" % (i, f), [(LESSON, lesson_edit(add=[fmt(i, dict(landed_fields[i], **{f: WRONG[f]}))]))]))
        crafted.append(("R-%s-%s" % (i, f), [(LESSON, lesson_edit(replace={i: {f: WRONG[f]}}))]))
crafted.append(("Z-drop-I4", [(LESSON, lesson_edit(drop=("I4",)))]))
crafted.append(("Z-drop-I1", [(LESSON, lesson_edit(drop=("I1",)))]))
crafted.append(("R-I1-source-S999", [(LESSON, lesson_edit(replace={"I1": {"source": "S999"}}))]))
crafted.append(("X02-trailing-text-I1", [(LESSON, lesson_edit(add=[]).replace(fmt("I1", landed_fields["I1"]).encode(), (fmt("I1", landed_fields["I1"]) + " trailing").encode()))]))
crafted.append(("W-a-prefix-edit-r40", [(R40, first_line_edit(r40))]))
assert r40.count(b"appears in 9 rows") == 1
crafted.append(("W-b-anchor-removed-r40", [(R40, r40.replace(b"appears in 9 rows", b"appears in nine rows", 1))]))
crafted.append(("W-c-append-r40-harmless", [(R40, r40 + b"\nAppended probe line.\n")]))
lr = r40.split(b"\n")
k = [i for i, l in enumerate(lr) if b"appears in 9 rows" in l][0]
lr2 = list(lr)
lr2[k + 1] = lr2[k + 1] + b" (edited)"
crafted.append(("W-d-after-anchor-r40", [(R40, b"\n".join(lr2))]))
crafted.append(("W-e-head-scorecard", [(SC, first_line_edit(sc))]))
crafted.append(("W-f-head-log", [(LOG, first_line_edit(log))]))
crafted.append(("W-g-r40-deleted", [(R40, None)]))
crafted.append(("T-a-items-header", [(ITEMS, items_b.replace(b"id\tfile", b"ID\tfile", 1))]))
crafted.append(("S-a-tier-B", [(REG, reg_text.replace(s258, cells_edit(lambda p: p.__setitem__(4, " B "))(s258)).encode())]))
crafted.append(("S-b-status-pending", [(REG, reg_text.replace(s258, cells_edit(lambda p: p.__setitem__(8, " pending "))(s258)).encode())]))
crafted.append(("S-c-opened-2026-10-27", [(REG, reg_text.replace(s258, cells_edit(lambda p: p.__setitem__(9, " 2026-10-27 "))(s258)).encode())]))
crafted.append(("S-d-no-v2.56.0-anywhere", [(REG, reg_text.replace(s258, s258.replace("v2.56.0", "v2.55.0")).encode())]))
crafted.append(("S-e-no-worktree.c-anywhere", [(REG, reg_text.replace(s258, s258.replace("worktree.c", "worktree.h")).encode())]))
crafted.append(("S-f-ten-cells", [(REG, reg_text.replace(s258, cells_edit(lambda p: p.pop(11))(s258)).encode())]))
crafted.append(("S-h-cell1-no-v2.56.0", [(REG, reg_text.replace(s258, cells_edit(lambda p: p.__setitem__(2, p[2].replace("v2.56.0", "v2.55.0")))(s258)).encode())]))

for name, edits in crafted:
    INPUTS[name] = (variant(name, edits), False)

G("checkout", "-q", "--detach", BASE)
INPUTS["rev-abbrev"] = (BASE[:7], False)
INPUTS["rev-HEAD"] = ("HEAD", False)
INPUTS["rev-zero"] = ("0" * 40, False)
print("inputs: %d (frozen 3, crafted %d)" % (len(INPUTS), len(INPUTS) - 3), flush=True)

# ---- mutants ----
MUT = [
    ("P00", "pristine", "no change (reference)", []),
    ("D1", "digest", "items digest check deleted", [('if table is None or hashlib.sha256(table).hexdigest() != ITEMS_SHA256:', 'if table is None:')]),
    ("D2", "digest", "items digest check inverted", [('if table is None or hashlib.sha256(table).hexdigest() != ITEMS_SHA256:', 'if table is None or hashlib.sha256(table).hexdigest() == ITEMS_SHA256:')]),
    ("D3", "digest", "absent table digested as b'' (refusal kept)", [('if table is None or hashlib.sha256(table).hexdigest() != ITEMS_SHA256:', 'if hashlib.sha256(table or b"").hexdigest() != ITEMS_SHA256:')]),
    ("D4", "digest", "items header row not skipped", [('.splitlines()[1:]:', '.splitlines():')]),
    ("D5", "digest", "blank-line skip deleted", [('if line.strip():', 'if True:')]),
    ("R1", "rev", "full-hex REV regex removed from rev gate", [('ok_rev = REV.match(args.rev) and subprocess.run(', 'ok_rev = subprocess.run(')]),
    ("R2", "rev", "REV regex loosened to 4-40 hex", [('REV = re.compile(r"^[0-9a-f]{40}$")', 'REV = re.compile(r"^[0-9a-f]{4,40}$")')]),
    ("R3", "rev", "MEASURED-resolve clause dropped from refusal", [('if not ok_rev or show(args.root, MEASURED, REGISTRY) is None:', 'if not ok_rev:')]),
    ("R4", "rev", "rev-resolve clause dropped (MEASURED kept)", [('if not ok_rev or show(args.root, MEASURED, REGISTRY) is None:', 'if show(args.root, MEASURED, REGISTRY) is None:')]),
    ("A1", "anchor", "base anchor presence check deleted", [('present = base is not None and anchor.encode("utf-8") in base', 'present = base is not None')]),
    ("A2", "anchor", "base anchor presence forced true", [('present = base is not None and anchor.encode("utf-8") in base', 'present = True')]),
    ("A3", "intact", "tip anchor clause removed from intact", [('anchor.encode("utf-8") in tip and ', '')]),
    ("A4", "intact", "prefix (startswith) clause removed from intact", [('and tip.startswith(base)', 'and True')]),
    ("A5", "intact", "tip None guard removed from intact", [('intact = tip is not None and', 'intact = True and')]),
    ("A6", "intact", "rewritten sign inverted", [('rewritten += 0 if intact else 1', 'rewritten += 1 if intact else 0')]),
    ("A7", "intact", "rewritten never counted", [('rewritten += 0 if intact else 1', 'rewritten += 0')]),
    ("V1", "derive", "I1 predicate inverted (== 9)", [('[1 for l in rows if "worktree.c" in l]) != 9', '[1 for l in rows if "worktree.c" in l]) == 9')]),
    ("V2", "derive", "I1 v2.56.0 count replaced by worktree.c count", [('sum("v2.56.0/worktree.c" in l for l in rows)', 'sum("worktree.c" in l for l in rows)')]),
    ("V3", "derive", "I1 row filter widened to any pipe-led line", [('rows = [l for l in text.splitlines() if ROW.match(l)]', 'rows = [l for l in text.splitlines() if l.startswith("|")]')]),
    ("V4", "derive", "I1 predicate constant 9 -> 3", [('[1 for l in rows if "worktree.c" in l]) != 9', '[1 for l in rows if "worktree.c" in l]) != 3')]),
    ("V5", "derive", "I3 predicate inverted", [('vals[0] != vals[1]', 'vals[0] == vals[1]')]),
    ("V6", "derive", "I3 missing-value fallback changed (dead branch)", [('vals.append(m.group(1) if m else "?")', 'vals.append(m.group(1) if m else "0")')]),
    ("V7", "derive", "I3 receipt order swapped", [('("census/round-40/records/c1-before.txt", "census/round-40/records/c1-after-h.txt")', '("census/round-40/records/c1-after-h.txt", "census/round-40/records/c1-before.txt")')]),
    ("V8", "derive", "I4 predicate inverted", [('return "occurrences=%d" % n, n == 0', 'return "occurrences=%d" % n, n != 0')]),
    ("V9", "derive", "I4 search prefix widened to census/round-40/", [('tree_files(root, MEASURED, "census/round-40/waves/")', 'tree_files(root, MEASURED, "census/round-40/")')]),
    ("V10", "derive", "I4 phrase shortened", [('"flagged as potentially")', '"flagged as")')]),
    ("V11", "derive", "I4 empty-path guard removed", [('            if path:\n', '            if True:\n')]),
    ("V12", "derive", "MEASURED constant moved to base 7eebc18", [('MEASURED = "bffcc0f660ff36eb8add3f61582748a7af019a5b"', 'MEASURED = "7eebc183f2685d1ea9b004b4de22c09a8a4035a7"')]),
    ("G1", "good", "fine forced True (every item corrected)", [('fine = bool(good)', 'fine = True')]),
    ("G2", "good", "rev equality dropped from good filter", [(' and m.group(5) == MEASURED]', ']')]),
    ("G3", "good", "file equality dropped from good filter", [(' and m.group(2) == path', '')]),
    ("G4", "good", "filed equality dropped from good filter", [('m.group(3) == claimed and ', '')]),
    ("G5", "good", "id equality dropped from good filter", [('m.group(1) == iid and ', '')]),
    ("G6", "good", "corrected counts every item", [('corrected += 1 if fine else 0', 'corrected += 1')]),
    ("G7", "good", "I1 source test any -> all", [('src_ok = any(sourced(args.root, args.rev, m.group(6)) for m in good)', 'src_ok = all(sourced(args.root, args.rev, m.group(6)) for m in good)')]),
    ("J1", "junk", "unknown-id correction not counted as junk", [('        if spec is None:\n            junk += 1\n            continue', '        if spec is None:\n            continue')]),
    ("J2", "junk", "spec mismatch not counted as junk", [('                and m.group(5) == MEASURED):\n            junk += 1', '                and m.group(5) == MEASURED):\n            pass')]),
    ("J3", "junk", "junk: file check dropped", [('if not (m.group(2) == spec[0] and m.group(3)', 'if not (m.group(3)')]),
    ("J4", "junk", "junk: filed check dropped", [('if not (m.group(2) == spec[0] and m.group(3) == spec[2] and m.group(4) == derived', 'if not (m.group(2) == spec[0] and m.group(4) == derived')]),
    ("J5", "junk", "junk: derived check dropped", [(' and m.group(4) == derived\n                and m.group(5) == MEASURED):', '\n                and m.group(5) == MEASURED):')]),
    ("J6", "junk", "junk: rev check dropped", [(' and m.group(5) == MEASURED):', '):')]),
    ("J7", "junk", "junk loop disabled", [('    for m in corrections:\n        spec', '    for m in []:\n        spec')]),
    ("J8", "junk", "LINE regex trailing-field tolerance", [(r'source=(\S+)\s*$', r'source=(\S+).*$')]),
    ("S1", "sourced", "I1-only gate removed (source test on every item)", [('if iid == "I1":', 'if True:')]),
    ("S2", "sourced", "tier-A check dropped", [('return (cells[3] == "A" and cells[7]', 'return (cells[7]')]),
    ("S3", "sourced", "status-mined check dropped", [('cells[7] == "mined" and ', '')]),
    ("S4", "sourced", "opened-date check dropped", [(' and cells[8] == "2026-10-28"', '')]),
    ("S5", "sourced", "v2.56.0 blob check dropped", [('and "v2.56.0" in blob and "worktree.c" in blob)', 'and "worktree.c" in blob)')]),
    ("S6", "sourced", "worktree.c blob check dropped", [('and "worktree.c" in blob)', ')')]),
    ("S7", "sourced", "blob reads cell 1 only", [('blob = cells[1] + " " + cells[5]', 'blob = cells[1]')]),
    ("S8", "sourced", "11-cell length guard dropped", [('            if len(cells) != 11:\n                return False\n', '')]),
    ("S9", "sourced", "sourced count incremented unconditionally", [('sourced_n += 1 if src_ok else 0', 'sourced_n += 1')]),
    ("S10", "sourced", "fine-and-source leg dropped", [('            fine = fine and src_ok', '            pass')]),
    ("S11", "sourced", "met sourced_n==1 clause dropped", [(' and sourced_n == 1)', ')')]),
    ("S12", "sourced", "S10 and S11 together (sourced leg removed)", [('            fine = fine and src_ok', '            pass'), (' and sourced_n == 1)', ')')]),
    ("M1", "verdict", "items==3 clause dropped", [('met = (len(items) == 3 and', 'met = (True and')]),
    ("M2", "verdict", "mismatched==3 clause dropped", [('mismatched == 3 and', 'True and')]),
    ("M3", "verdict", "junk==0 clause dropped", [('junk == 0 and', 'True and')]),
    ("M4", "verdict", "rewritten==0 clause dropped", [(' and rewritten == 0', '')]),
    ("M5", "verdict", "corrected==3 relaxed to >=1", [('corrected == 3 and', 'corrected >= 1 and')]),
]

MD = os.path.join(S, "mutants")
os.makedirs(MD, exist_ok=True)
for mid, grp, desc, pairs in MUT:
    src = ctr_src.decode()
    for old, new in pairs:
        n = src.count(old)
        assert n == 1, "%s: pattern occurs %d times: %r" % (mid, n, old)
        src = src.replace(old, new)
    compile(src, mid, "exec")
    with open(os.path.join(MD, mid + ".py"), "w") as f:
        f.write(src)
print("mutants written: %d" % len(MUT), flush=True)


def run_one(mpath, rev):
    p = sh([sys.executable, "-B", mpath, "--root", C, "--rev", rev, "--scratch", S], cwd=S)
    return dict(rc=p.returncode, out=p.stdout.decode(), err=p.stderr.decode())


jobs = [(m[0], os.path.join(MD, m[0] + ".py"), name, rev) for m in MUT for name, (rev, _) in INPUTS.items()]
results = {}
with cf.ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(run_one, mp, rev): (mid, name) for mid, mp, name, rev in jobs}
    for fu in cf.as_completed(futs):
        results[futs[fu]] = fu.result()
print("runs: %d" % len(results), flush=True)

FROZEN = [n for n, (_, fr) in INPUTS.items() if fr]
CRAFT = [n for n, (_, fr) in INPUTS.items() if not fr]
EXP = {"landed": (0, "SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1"),
       "nothing": (1, "SUMMARY items=3 mismatched=3 corrected=0 uncorrected=3 junk=0 rewritten=0 sourced=0"),
       "junk": (1, "SUMMARY items=3 mismatched=3 corrected=0 uncorrected=3 junk=3 rewritten=0 sourced=0")}


def summ(r):
    ls = [l for l in r["out"].splitlines() if l.startswith("SUMMARY")]
    return ls[0] if ls else "NO-SUMMARY"


P = {n: results[("P00", n)] for n in INPUTS}
for n in FROZEN:
    assert P[n]["rc"] == EXP[n][0] and summ(P[n]) == EXP[n][1], ("pristine does not reproduce control", n, P[n])
print("pristine reproduces all three frozen controls", flush=True)

rows = []
for mid, grp, desc, _ in MUT:
    R = {n: results[(mid, n)] for n in INPUTS}
    ctrl_ok = all(R[n]["rc"] == EXP[n][0] and summ(R[n]) == EXP[n][1] for n in FROZEN)
    fv = [n for n in FROZEN if R[n]["rc"] != P[n]["rc"]]
    fe = [n for n in FROZEN if R[n]["rc"] == P[n]["rc"] and R[n]["out"] != P[n]["out"]]
    cv = [n for n in CRAFT if R[n]["rc"] != P[n]["rc"]]
    ce = [n for n in CRAFT if R[n]["rc"] == P[n]["rc"] and R[n]["out"] != P[n]["out"]]
    crash = [n for n in INPUTS if "Traceback" in R[n]["err"]]
    if mid == "P00":
        cls = "reference"
    elif fv:
        cls = "CHANGES EXIT CODE on frozen control"
    elif not ctrl_ok:
        cls = "exit code unchanged on frozen controls; SUMMARY differs from pinned control text"
    elif fe:
        cls = "evidence-only change on frozen control (verdict unchanged)"
    elif cv:
        cls = "invisible to frozen controls; verdict flips on crafted input"
    elif ce:
        cls = "invisible to frozen verdict; evidence-only on crafted input"
    else:
        cls = "INVISIBLE to every input"
    rows.append(dict(id=mid, group=grp, desc=desc, ctrl_ok=ctrl_ok, frozen_verdict=fv, frozen_evidence=fe,
                     crafted_verdict=cv, crafted_evidence=ce, crash=crash, cls=cls))

with open(os.path.join(S, "results.json"), "w") as f:
    json.dump(dict(inputs={n: r for n, (r, _) in INPUTS.items()}, frozen=FROZEN, rows=rows,
                   raw={"%s|%s" % k: v for k, v in results.items()}), f, indent=1)

with open(os.path.join(S, "table.md"), "w") as f:
    f.write("| id | group | mutation | frozen controls match | frozen verdict flips | frozen evidence-only | crafted verdict flips | crafted evidence-only | tracebacks | class |\n")
    f.write("|---|---|---|---|---|---|---|---|---|---|\n")
    for r in rows:
        f.write("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |\n" % (
            r["id"], r["group"], r["desc"], "yes" if r["ctrl_ok"] else "NO", ",".join(r["frozen_verdict"]) or "-",
            ",".join(r["frozen_evidence"]) or "-", ",".join(r["crafted_verdict"]) or "-",
            ",".join(r["crafted_evidence"]) or "-", ",".join(r["crash"]) or "-", r["cls"]))
    f.write("\n## pristine per input\n\n| input | rev | rc | SUMMARY |\n|---|---|---|---|\n")
    for n, (rev, fr) in INPUTS.items():
        f.write("| %s | %s | %d | %s |\n" % (n, rev[:12], P[n]["rc"], summ(P[n])))
print(open(os.path.join(S, "table.md")).read())
