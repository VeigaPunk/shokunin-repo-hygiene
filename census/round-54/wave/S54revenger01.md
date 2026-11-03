# souji round 54, wave w1 — seat S54revenger01 (revenger)

Role: reproduce the routed defects this round inherits, as receipts the L1 can cite.
Lane: /home/vgpnk/Projects/shokunin/souji-shokunin (read-only to this seat; nothing in the
lane's tracked tree was written or modified by this seat).
Scratch: /fast/scratch/hyaku/souji-r54/S54revenger01/ (deleted before yield; verified absent).
Lane tip at measurement: bfdbb336329e6afba3ab1ca83cbd6d9759271062.
R54 freeze commit read: 3c394cab0cd406bbab72b8d365e0f3deed4ef98a. R54 base: fe12daad2549f534650d406ebdbac9113d59313f.
Frozen sense checked first: census/round-54/preregistration.txt (whole file read; claim headings at
lines 27 and 91, instrument pins at 146-151, pin-gate sentence at 152-155). Neither counter was edited; both are cited by digest.

## Verdict summary

| # | routed item | verdict | resolution |
|---|---|---|---|
| 1 | r53 verifier §6.1: report says Mistakes has "six rows" | **RED — reproduced** | actual table body rows = **7**; report's count is wrong by one; counting command proposed below |
| 2 | r53 prereg wording ("close the five…", "do-nothing control" double duty) | GREEN | r54 avoids the "closes" pattern; control referents named distinctly, residual file label noted |
| 3 | r53 sentinel S4: oracle/builder unpinned | GREEN — fix works | r54 pins all instruments; pins verified **before exec**; wrong-pin refusals exit 2 with nothing built |
| 4 | R53-CORRECTION resolution at tip | GREEN | all four lines match; pairs re-derive 198→199; v3 refuses both sites pre-filing (red) and passes at tip (green) |
| 5 | r53 misroot: fleet-root LOG.md contamination | GREEN | fleet LOG.md at HEAD has zero round-53 matches; worktree clean; lane LOG carries the entry |
| 6 | §6 items not covered by 1/3 | **1 unresolved** | §6.2 (non-durable wave-results pointer) is **not** covered by the frozen r54 claims; still open, integrator-owned |

Resolved: 5 of 6. Unresolved: 1 of 6 (§6.2, not this round's claim scope).

---

## Item 1 — r53 report's "six rows" claim vs the actual `## Mistakes` table

### r53 report's claim (verbatim, .ufo/reports/round-53/souji.md:193-195, fleet repo, read-only)

```
- Mistake mined: corpus/lessons/round-53.md `## Mistakes` — six rows (instrument
  narrower than title; oracle/builder unpinned; fixture rev determinism; builder
  hardening; the 274→275 annotation class; the control-design correction), each with
  class · evidence · captured-by · fix.
```

### Count (exact commands, verbatim output)

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin
$ grep -c '^| ' corpus/lessons/round-53.md
8

$ awk 'NR>=184 && NR<=192 {printf "%d\t%s\n", NR, substr($0,1,40)}' corpus/lessons/round-53.md
184	| class | evidence | captured-by | fix |
185	|---|---|---|---|
186	| an instrument's kill-power is n
187	| the selftest oracle and builder
188	| fixture commit ids are wall-cloc
189	| the fixture builder's subprocess
190	| a pasteable count annotation in
191	| the round's own LOG entry was ap
192	| the first do-nothing-control des
```

`grep -c '^| '` = 8: **one header row (184) plus seven body rows (186-192)**. The separator
row (185) is *not* counted by that pattern — it has no space after the leading pipe:

```
$ sed -n '185p' corpus/lessons/round-53.md | od -c
0000000   |   -   -   -   |   -   -   -   |   -   -   -   |   -   -   -
0000020   |  \n
```

So "minus header/separator" (the hint in this seat's assignment) double-subtracts: the
separator never entered the `^| ` count. `8 - 1 = 7` body rows; `8 - 2 = 6` is the report's
wrong number.

Cross-checks:

```
$ sed -n '186,193p' corpus/lessons/round-53.md | grep -c '^| '
7
$ awk '/^\|/ && $0 !~ /^\|[-: |]+\|$/ {n++} END{print n-1}' corpus/lessons/round-53.md
7
```

### Divergence

- Report: "six rows", parenthetical enumerating six classes.
- Table: seven body rows. The row the count omits is **line 191**, the misroot row
  ("the round's own LOG entry was appended twice to the fleet root's LOG.md"), which the
  same report narrates at lines 253-258 ("both times the fleet diff showed exactly the 52
  appended lines"). The count excludes a row the report itself discloses.
- The r53 spot-check's §6.1 got this right (quoted under item 6): "the committed table
  carries **seven**".
- Norm that failed: a count carried without its command (spot-check §6.1: "Counts carry
  their command"). Nothing in the frozen instruments measures report prose, so the r54
  claims cannot catch this class (see item 6).

### Proposed counting command for the r54 report's own `## Mistakes` table

```
awk '$0 ~ /^\|/ && $0 !~ /^\|[-: |]+\|$/ {n++} END{printf "body_rows=%d\n", n-1}' corpus/lessons/round-54.md
```

- `n-1` drops the header; the alignment row is excluded by the regex, so it is never
  subtracted blindly.
- Tested against the r53 table: `body_rows=7` (matches the enumeration above).
- Tested against a synthetic table with a **spaced** separator (`| --- | --- |`) and two
  body rows: `body_rows=2`; the same file gives `grep -c '^| '` = 4, i.e. the grep form
  minus 2 would report 2 (right) but minus 1 would report 3 (wrong) — the grep arithmetic
  depends on an unseen separator convention.
- Report the command verbatim next to the number; if `grep` is used instead, pin the
  convention: `expr $(grep -c '^| ' F) - 1` only when `sed -n '<header+1>p' F` proves the
  separator is compact (`|---|`).

---

## Item 2 — r53 prereg wording; r54 avoidance

### The two r53 patterns (verbatim)

```
$ awk 'NR==19||NR==54||NR==55||NR==60||NR==110||NR==116 {printf "%d:%s\n", NR, $0}' census/round-53/preregistration.txt
19:### C1 — calibration 7 (lowest-scoring axis): the annotation-agreement counter is amended to close the five named r52 limits
54:  (exit 0) — the v1 arm is the do-nothing control.
55:Before (v1 arm, do-nothing control instrument): v1 exit 0 on F2–F6 (five accepts),
60:Do-nothing control (committed with this freeze): census/round-53/controls/
110:  capture (exit 0) — the v1 arm is the do-nothing control.
116:Do-nothing control (committed with this freeze): census/round-53/controls/
```

Note on the exact string: the prereg's literal is "amended to **close** the five named r52
limits" (line 19); the critic's phrasing "closes the five named limits" is quoted at
corpus/lessons/round-53.md:126. The defeasible claim is the same at both sites, and the
r53 C2 heading (line 74) already used "instrument", so the drift is C1-specific.

Double duty: "do-nothing control" names the **v1 arm** (lines 54-55, 110) and the
**committed control file** (lines 60, 116) — the critic R13 and spot-check §6.3 objection.

### r54 avoidance (greps, verbatim)

```
$ grep -n -i "clos" census/round-54/preregistration.txt
23:"closes" them wholesale; the two control artifacts are named distinctly — the
157:## Named limits carried into v3 (disclosed, not fixed)
185:  tilde fences, the closing-fence length rule, HTML comment blocks — the

$ grep -n "^## C[12]" census/round-54/preregistration.txt
27:## C1 — calibration 7 (lowest axis): the annotation-agreement counter v3 instruments the r53 routed filing surfaces
91:## C2 — coverage 8: the capture counter v3 instruments receipt grammar, CR naming, and argument pinning
```

- **"closes" pattern: avoided.** The only occurrence in a claim sense is line 23, which is
  the *prohibition* ("claim titles say the counter \"instruments\"/\"adds\" the named
  surfaces, never \"closes\" them wholesale"). Line 157 is the limits heading; line 185 is
  the technical term "closing-fence". Both claim headings (27, 91) say "instruments".
- **Control double duty: resolved by distinct naming, label retained.**

```
78:Do-nothing control: census/round-54/controls/c1-control-donothing.txt
79:(absent-instrument control: PRISTINE FAIL C1V3-COUNTER-ABSENT at base; plus
80:the v2-arm acceptance rows F7-F12 exit 0, and the wrong-pin refusal that
...
134:Do-nothing control: census/round-54/controls/c2-control-donothing.txt
135:(absent-instrument control: PRISTINE FAIL C2V3-COUNTER-ABSENT at base; the
136:v2-arm acceptance rows FA4/FA5 exit 0; the FA6 v2-cascade receipt; the
137:wrong-expected-pin refusal; final line EXIT=1).
```

and the naming rule itself at lines 21-25:

```
Wording discipline (r53 critic R13 and the r53 verifier §6 item 3, routed):
claim titles say the counter "instruments"/"adds" the named surfaces, never
"closes" them wholesale; the two control artifacts are named distinctly — the
absent-instrument control and the v2-arm acceptance control — because they
are different objects.
```

Verdict: **GREEN** — the referents are disambiguated in every claim block (the v1/v2 arm is
now "v2-arm acceptance rows/control"; the committed file is "absent-instrument control").
Residual: the section label "Do-nothing control:" still appears twice (78, 134), matching
the committed filename. It is a label, not a second referent. Noted, not a defect.

---

## Item 3 — r53 sentinel S4 (oracle/builder unpinned) and the r54 fix

### r53 pin block (verbatim, census/round-53/preregistration.txt:156-162)

```
## Counter pins (sha256 of the bytes frozen with this file)
- census/round-53/c1-counter.py  a7928d05df794f14d5d0213ddb78d042f62819b52f5c49b3c838a1b96da1ed15
- census/round-53/c2-counter.py  6515b97553dd6f6d207d638de2520c4367a56a1a37ff7329b9d914c329a349b7
- census/round-53/fixtures/build-fixtures.py  d5ce557ebdc715a0e2ec2cb8c8ae4c726dbd78e123eb11fedc4892f27a68339b
- record pin (census/round-51/records/ws-drift-vs-r46.tsv at base)
  2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30
```

Two counters + builder + record. **No digest for either selftest-expected TSV** — the
oracle files are only named, never pinned:

```
$ grep -n "selftest-expected" census/round-53/preregistration.txt
47:census/round-53/records/c1-selftest-expected.tsv and the selftest asserts them.
104:census/round-53/records/c2-selftest-expected.tsv.
```

(no `sha256=` on either line). That confirms S4 as filed.

### r54 pins (verbatim)

```
$ awk 'NR==29||NR==30||NR==93||NR==94 {printf "%d:%s\n", NR, $0}' census/round-54/preregistration.txt
29:Counter: census/round-54/c1-counter.py sha256=f45d3d8f4eced147b7e2c4127bf5fefe6d080f2f0fd0c637cfd44f8d41fccf7e
30:Population: census/round-54/records/c1-selftest-expected.tsv sha256=4e73c495b6a7d1db1ef8dc5506ac874a167720a48e7618d2a41ccec55af2a1c7
93:Counter: census/round-54/c2-counter.py sha256=84b05295d5b84af23079c8fade6f7e640454ac25c56c842fb0233ea779735e09
94:Population: census/round-54/records/c2-selftest-expected.tsv sha256=e32f793468cf370781a860f8b642b6a42e1d589f70c0b7f575ded130263fc00d

$ sed -n '/## Instrument pins/,/^## /p' census/round-54/preregistration.txt | head -20
## Instrument pins (sha256 of the bytes frozen with this file)
- census/round-54/fixtures/build-fixtures.py  ae5881f850ba5f5895fc27e6e3185658af372535ae7ccf971476175be118b1ba
- census/round-54/fixtures/run-matrix.sh  f9d277636d6642de7b287678a145e8916f84f0c9cba00f4768aa16feaca80799
- census/round-54/records/c1-selftest-expected.tsv  4e73c495b6a7d1db1ef8dc5506ac874a167720a48e7618d2a41ccec55af2a1c7
- census/round-54/records/c2-selftest-expected.tsv  e32f793468cf370781a860f8b642b6a42e1d589f70c0b7f575ded130263fc00d
- census/round-51/records/ws-drift-vs-r46.tsv at base  2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30
- tools/souji-fleet-root-census.py at base  e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b
The counters' selftests verify --builder-sha256/--expected-sha256 pins
BEFORE exec (the r53 sentinel S4 routed fix; the pre-freeze receipts
records/c1-selftest.txt and c2-selftest.txt carry the pinned runs, and the
wrong-pin refusals sit in the two control files).
```

All pins re-derived from the bytes (verbatim):

```
$ sha256sum census/round-54/c1-counter.py census/round-54/c2-counter.py \
    census/round-54/fixtures/build-fixtures.py census/round-54/fixtures/run-matrix.sh \
    census/round-54/records/c1-selftest-expected.tsv census/round-54/records/c2-selftest-expected.tsv
f45d3d8f4eced147b7e2c4127bf5fefe6d080f2f0fd0c637cfd44f8d41fccf7e  census/round-54/c1-counter.py
84b05295d5b84af23079c8fade6f7e640454ac25c56c842fb0233ea779735e09  census/round-54/c2-counter.py
ae5881f850ba5f5895fc27e6e3185658af372535ae7ccf971476175be118b1ba  census/round-54/fixtures/build-fixtures.py
f9d277636d6642de7b287678a145e8916f84f0c9cba00f4768aa16feaca80799  census/round-54/fixtures/run-matrix.sh
4e73c495b6a7d1db1ef8dc5506ac874a167720a48e7618d2a41ccec55af2a1c7  census/round-54/records/c1-selftest-expected.tsv
e32f793468cf370781a860f8b642b6a42e1d589f70c0b7f575ded130263fc00d  census/round-54/records/c2-selftest-expected.tsv

$ git cat-file blob fe12daad2549f534650d406ebdbac9113d59313f:census/round-51/records/ws-drift-vs-r46.tsv | sha256sum
2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30  -
$ git cat-file blob fe12daad2549f534650d406ebdbac9113d59313f:tools/souji-fleet-root-census.py | sha256sum
e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b  -
```

Six artifact pins (builder, run-matrix, two oracle TSVs, record, tool) plus the two counter
pins in the claim blocks — all eight match the bytes on disk / at base. That is all four
instrument classes S4 named: counter, builder, oracle, plus the frozen record and the tool.

### Pin verified BEFORE exec (code + behavior)

```
$ awk 'NR>=379 && NR<=388 {printf "%d:%s\n", NR, $0}' census/round-54/c1-counter.py
379:def run_selftest(work: Path, expected_path: Path, out, builder_sha=None, expected_sha=None):
380:    if builder_sha is not None and sha256(BUILDER.read_bytes()) != builder_sha:
381:        out.append('CANNOT-EVALUATE PIN-MISMATCH builder sha256 %s != pinned %s'
382:                   % (sha256(BUILDER.read_bytes()), builder_sha))
383:        return 2
384:    if expected_sha is not None and sha256(expected_path.read_bytes()) != expected_sha:
385:        out.append('CANNOT-EVALUATE PIN-MISMATCH expected sha256 %s != pinned %s'
386:                   % (sha256(expected_path.read_bytes()), expected_sha))
387:        return 2
388:    mod = load_builder()
```

`census/round-54/c2-counter.py:308-317` is the same shape (`def run_selftest` at 308, both
checks return 2 before `load_builder()` at 317). The checks precede fixture construction,
and the empty work dirs after refusal prove it behaviorally.

### Red receipts (the fix shown able to fail)

```
$ mkdir -p $S/pin-c1
$ python3 -B census/round-54/c1-counter.py --selftest --work "$S/pin-c1" \
    --builder-sha256 0000000000000000000000000000000000000000000000000000000000000000
CANNOT-EVALUATE PIN-MISMATCH builder sha256 ae5881f850ba5f5895fc27e6e3185658af372535ae7ccf971476175be118b1ba != pinned 0000000000000000000000000000000000000000000000000000000000000000
EXIT=2
entries=0

$ python3 -B census/round-54/c2-counter.py --selftest --work "$S/pin-c2" \
    --builder-sha256 1111111111111111111111111111111111111111111111111111111111111111
CANNOT-EVALUATE PIN-MISMATCH builder sha256 ae5881f850ba5f5895fc27e6e3185658af372535ae7ccf971476175be118b1ba != pinned 1111111111111111111111111111111111111111111111111111111111111111
EXIT=2
entries_c2=0

$ python3 -B census/round-54/c1-counter.py --selftest --work "$S/pin-exp" \
    --expected-sha256 deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef
CANNOT-EVALUATE PIN-MISMATCH expected sha256 4e73c495b6a7d1db1ef8dc5506ac874a167720a48e7618d2a41ccec55af2a1c7 != pinned deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef
EXIT=2
entries=0
```

`entries=0` in all three: no fixture was built after the refusal, so the pin gate is before
exec, not after. Verdict **GREEN**: the S4 routed defect is fixed and the fix is falsifiable.
The red receipts above are exactly the rows the r54 control file names ("the wrong-pin
refusal that shows the r53 sentinel-S4 fix able to fail").

---

## Item 4 — R53-CORRECTION resolution at the current tip

### The four lines (verbatim, with line numbers)

```
$ awk 'NR==1268||NR==1270{printf "%d:%s\n", NR, $0}' SCORECARD.md
1268:R53-CORRECTION LOG.md:2527 stale=274->275 recomputed=198->199
1270:R53-CORRECTION corpus/README.md:870 stale=274->275 recomputed=198->199

$ awk 'NR==2527{printf "%d:%s\n", NR, $0}' LOG.md
2527:- S275 admitted (git(1) GIT_OPTIONAL_LOCKS, located quote 25 words, capture census/round-52/sources/); knowledge entry corpus/knowledge/fleet-root-stray-census.md. corpus/SOURCES.md 274 -> 275 rows.

$ awk 'NR==870{printf "%d:%s\n", NR, $0}' corpus/README.md
870:- SOURCES 274 -> 275 rows (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`); census exit 0 (conf form, this host). Assimilation: none (open L0 on mass id drift, r46). considerthese/: no such directory.
```

The filings' stale pairs (`274->275`) match the lines' pairs (`274 -> 275`) at the same
`path:line` pointers; both lines still carry `corpus/SOURCES.md` (LOG:2527 by name,
README:870 inside its command string and as "SOURCES").

### The pair re-derives

```
$ grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md
200
$ for r in f778b9d131574d3ff09c0cc8a077643c0fc84bb4 9bf9234ae4d11c7b31706354302a9e95ad0d1f81; do printf "%s -> " "$r"; git show $r:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'; done
f778b9d131574d3ff09c0cc8a077643c0fc84bb4 -> 198
9bf9234ae4d11c7b31706354302a9e95ad0d1f81 -> 199
```

### Instrument evidence: red before the filing, green at the tip

At the pre-filing revision (r52 content commit, before the R53-CORRECTION lines landed), the
v3 counter refuses both sites — real lane bytes, no fixture:

```
$ git rev-parse 9c0f128152f2299948d48f775642a7d29a1fc976^
8ec412c64d73d8c5e339f1d15d11cfc5b6e702d0
$ python3 -B census/round-54/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 9c0f128152f2299948d48f775642a7d29a1fc976 --base 8ec412c64d73d8c5e339f1d15d11cfc5b6e702d0 \
    --record-sha256 2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30 \
    --scratch $S/c1-red
FINDING UNFILED-SOURCES-ANNOTATION LOG.md:2527 claims 274 -> 275 rows but the registry holds 199; no pair-form filing names it
FINDING UNFILED-SOURCES-ANNOTATION corpus/README.md:870 claims 274 -> 275 rows but the registry holds 199; no pair-form filing names it
SITE path=SCORECARD.md line=1196 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=125 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=2 logrecomp=0 recomputed=79 rev=9c0f128152f2 base=8ec412c64d73
EXIT=1
```

At the lane tip, the same instrument accepts them:

```
$ python3 -B census/round-54/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev bfdbb336329e6afba3ab1ca83cbd6d9759271062 --base fe12daad2549f534650d406ebdbac9113d59313f \
    --record-sha256 2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30 \
    --sources-rev-before f778b9d131574d3ff09c0cc8a077643c0fc84bb4 \
    --sources-rev-after 9bf9234ae4d11c7b31706354302a9e95ad0d1f81 --scratch $S/c1-tip
SITE path=SCORECARD.md line=1196 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=125 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=bfdbb336329e base=fe12daad2549
EXIT=0
```

(The pre-existing `SITE … status=mismatch filed=yes` rows are the r51 annotations filed by
the R52-CORRECTION lines; they are unrelated to this item and are green in the filed sense.)

Verdict **GREEN**: the resolution holds at the tip — the filing pointers still name the
lines, the pairs match, the recomputed pair is 198→199, and the v3 instrument independently
distinguishes the filed state (exit 0) from the pre-filing state (exit 1, two findings).

---

## Item 5 — r53 misroot: fleet-root LOG.md at HEAD

```
$ git -C /home/vgpnk/Projects/shokunin log --oneline -3 -- LOG.md
f47ad6ba repair: restore fleet tree deleted by stray commit 35b91714 (author t <t@t>, 09:21:14 -03)
35b91714 t
c87cb300 session: preserve final measured checkpoint and pause unfinished training

$ git -C /home/vgpnk/Projects/shokunin show HEAD:LOG.md | grep -n -iE "round[ -]53|r53"
$ echo $?
1

$ git -C /home/vgpnk/Projects/shokunin show HEAD:LOG.md | grep -n -iE "round 53|round-53|S276|fleet-root-capture"
$ echo $?
1

$ git -C /home/vgpnk/Projects/shokunin status --porcelain -- LOG.md
(no output)
```

Fleet HEAD: `dd05b55cbb159f07d9e70472dc37175a5177fcc4`; fleet `HEAD:LOG.md` blob
`d40e27be092893af51b3bdd8466dcfc66cd7f19a`. The only "souji" hit in the whole fleet LOG.md
is an unrelated roster line (1253-1257: "…added: tameshi, mado, tsukuroi, tabi and souji.
Souji's actual remote is `VeigaPunk/shokunin-repo-hygiene`…"). Zero round-53/r53/S276
matches; the worktree copy is byte-identical to HEAD.

The entry lives where it belongs:

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -3 -- LOG.md
a1156d85 round-53: content — S276 registry row … + lesson round-53 …; LOG round 53; README frontier note
9c0f1281 round-52: C1 corrections — R52-CORRECTION lines …
e004ee1a souji round 51: end receipts — …
```

and the lane LOG carries the heading at `LOG.md:2537`:
`## Round 53 (2026-11-03, Linux omp host; base 9bf9234a…; freeze 61838b54… before any claim receipt …)`.

Verdict **GREEN**: no round-53 souji contamination remains in the fleet root's LOG.md, and
the duplication was restored byte-exact (clean status against HEAD).

---

## Item 6 — other spot-check §6 items routed to souji

`corpus/lessons/round-53-verifier-spotcheck.md` §6 has four items:

1. report count inaccuracy — reproduced under item 1 (RED, count is 7);
2. non-durable wave-results pointer (routed to the **protocol integrator**);
3. prereg wording (critic R13 echo) — covered under item 2;
4. sentinel S4 oracle/builder pinning — covered under item 3.

**The only item not covered by 1/3 is §6.2.** Its text:

```
2. **Non-durable wave-results pointer (routed to the protocol integrator, same item the r52
   verifier raised):** the report cites `.ufo/waves/round-53/w1-results.json` on the fleet repo; the
   fleet-side round-53 wave dir was never committed and is absent at closure, so the pointer does
   not resolve. … The lane-local wave dir being gitignored is declared and fine; the fleet-side copy
   is the integrator-owned durability gap.
```

Live re-check (read-only):

```
$ ls /home/vgpnk/Projects/shokunin/.ufo/waves/round-53/
ls: cannot access '/home/vgpnk/Projects/shokunin/.ufo/waves/round-53/': No such file or directory
$ ls /home/vgpnk/Projects/shokunin/.ufo/waves/round-54/
ls: cannot access '/home/vgpnk/Projects/shokunin/.ufo/waves/round-54/': No such file or directory
$ grep -n "ufo" /home/vgpnk/Projects/shokunin/souji-shokunin/.gitignore
1:.ufo/waves/
$ grep -n -i "wave" census/round-54/preregistration.txt
75:with their v2 findings); any finding the wave attacks raise that the counter
131:the selftest); any finding the wave attacks raise that the counter does not
192:- L2 floor: one v1 wave of 12 seats under ufo-wave-policy.json (band 8-16);
200:  wave context.
```

Verdict **UNRESOLVED**: not covered by the frozen r54 claims. Both claim blocks (C1 lines
27-89, C2 lines 91-143) scope only the two counters; the sole "wave" mentions are the kill
rule (75, 131), the L2 floor (192) and the scratch sentence (200). No receipt-durability
requirement exists anywhere in the r54 prereg, and the fleet-side round-54 wave dir is
absent while this wave is live — the same class will recur unless the integrator commits the
wave results. Assigned to the protocol integrator, not to this lane's claims.

---

## Named limits observed (disclosed; no edits — the counters are byte-frozen)

1. **C1 v3 SUMMARY carries no positive annotation count.** `logunfiled=0 logrecomp=0` at
   the tip is indistinguishable, in the printed output, from a scan that matched no
   annotation at all; non-vacuity is only inferable from the F12/F12b fixtures. Observed in
   `census/round-54/c1-counter.py:299-334` (counters increment only on violations). Routed
   as a next-round limit; the tip run above (exit 0) plus the pre-filing run (exit 1,
   `logunfiled=2`) does establish that the scan reaches the real sites today.
2. **Counting-command class.** `grep -c '^| '` counts body+header only while the separator
   is compact, and body+header+separator when the separator is spaced; report counts must
   carry a command whose separator assumption is stated (or use the awk form proposed in
   item 1). This is the same class the r53 spot-check filed, and it bit the assignment hint
   itself.
3. **"Do-nothing control" label survives in r54** (lines 78, 134) as the section/file label
   while the referents are disambiguated in the parentheticals. Naming is correct; the
   reader still has to read the parenthetical.
4. **oracle/builder now pinned, but the pin is opt-in**: `--builder-sha256`/`--expected-sha256`
   default to `None` (`c1-counter.py:434-435`), so an unpinned selftest invocation is still
   accepted; the r54 control files embed the pinned runs, and the prereg's own pin sentence
   is what carries the obligation. Named limit (the bytes are frozen; do not edit).
5. **§6.2 recurrence** (item 6): fleet-side wave dirs absent for round 53 and round 54.

## Tooling and scratch

- No tool installed, upgraded, or removed by this seat (nothing needed).
- Scratch `/fast/scratch/hyaku/souji-r54/S54revenger01/` used only for `--work`/`--scratch`
  dirs and one synthetic table; deleted before yield (verified `ls` → absent).
- No git/jj mutation anywhere: every call was `log`, `show`, `rev-parse`, `cat-file`,
  `status --porcelain`; the lane tree had the same 8 untracked census/round-54/records
  entries before and after my runs (other seats' in-flight receipts), and `SCORECARD.md`,
  `LOG.md`, `corpus/README.md`, `census/**`, `tools/**` were only read.

## Key lines for the L1

1. `grep -c '^| ' corpus/lessons/round-53.md` → 8 = header + **7 body rows**; the report's
   "six rows" is off by one; the omitted row is the misroot row (lesson line 191).
2. r54 pre-registration says "instruments" in both claim headings (lines 27, 91); the only
   "closes" is the prohibition itself (line 23).
3. Both r54 counters refuse a wrong builder/expected pin with `CANNOT-EVALUATE PIN-MISMATCH`,
   exit 2, and build nothing (pins before exec).
4. R53-CORRECTION: four lines match; pairs re-derive 198→199; v3 exits 1 with two
   `UNFILED-SOURCES-ANNOTATION` findings at 9c0f1281 and exits 0 with `logunfiled=0` at
   bfdbb336.
5. Fleet LOG.md at HEAD `d40e27be`: no round-53/r53/S276 match, clean worktree.
6. §6.2 (wave-results durability) is the one routed item the frozen r54 claims do not cover.
