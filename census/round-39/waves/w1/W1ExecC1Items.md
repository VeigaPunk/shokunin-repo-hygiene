# W1ExecC1Items — C1 item-predicate decidability audit (r39 w1)

Role: executor (leaf). Scope: audit the 16 frozen rows of `census/round-39/c1-items.tsv` for
decidability at the base revision. Read-only git only; no commit/stash/jj; no lane file other than
this report written. No tool installed or upgraded (none needed; pacman untouched).

Revisions: base `ed30b7f5b77939c9073348d810730bc4f355708d` (lane base), lane `HEAD` at audit time
`bbd9b9746ba9e3c5d640bf095bbad18a00c80e83` (`git merge-base --is-ancestor ed30b7f HEAD` → rc 0).
Scratch root: `/fast/scratch/hyaku/souji-r39/W1ExecC1Items` (3.1 MB, **still on disk** — fixtures
retained as evidence; paths listed in §6).

Predicate as implemented (`census/round-39/c1-counter.py:run`, lines 190-256): per row, `git show
<rev>:<file>`; if absent → `OPEN FILE-ABSENT`; else hits = lines containing `anchor` (plain
substring); a row is CLOSED when ≥1 hit line satisfies every `must` token and no `mustnot` token
under `has_token` (whole-token: the characters immediately before and after the occurrence must be
non-alphanumeric). `mustnot` is evaluated **only on anchor-hit lines**.

## 1. Commands and observed output

### 1.1 Per-row file existence + anchor frequency at base

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && REV=ed30b7f5b77939c9073348d810730bc4f355708d;
awk -F'\t' 'NR>1 && $1!="id" && $1!~/^#/ {printf "%s\t%s\t%s\n",$1,$2,$3}' census/round-39/c1-items.tsv |
while IFS=$'\t' read -r id f a; do git cat-file -e "$REV:$f" 2>/dev/null; ce=$?;
  n=$(git show "$REV:$f" 2>/dev/null | grep -c -F -- "$a");
  printf '%s\t%s\tcatfile_rc=%s\tanchor_hits_at_base=%s\n' "$id" "$f" "$ce" "$n"; done
```

Output (verbatim, 16 lines):

```
R39-C1-01	corpus/lessons/round-38.md	catfile_rc=0	anchor_hits_at_base=0
R39-C1-02	corpus/lessons/round-38.md	catfile_rc=0	anchor_hits_at_base=0
R39-C1-03	census/round-39/records/waves-wait.txt	catfile_rc=128	anchor_hits_at_base=0
R39-C1-04	census/round-39/records/waves-capture.txt	catfile_rc=128	anchor_hits_at_base=0
R39-C1-05	corpus/lessons/round-39.md	catfile_rc=128	anchor_hits_at_base=0
R39-C1-06	SKILL.md	catfile_rc=0	anchor_hits_at_base=0
R39-C1-07	corpus/lessons/round-39.md	catfile_rc=128	anchor_hits_at_base=0
R39-C1-08	census/round-38/preregistration.txt	catfile_rc=0	anchor_hits_at_base=0
R39-C1-09	census/round-38/preregistration.txt	catfile_rc=0	anchor_hits_at_base=0
R39-C1-10	SCORECARD.md	catfile_rc=0	anchor_hits_at_base=0
R39-C1-11	LOG.md	catfile_rc=0	anchor_hits_at_base=0
R39-C1-12	LOG.md	catfile_rc=0	anchor_hits_at_base=0
R39-C1-13	corpus/QUALITY.md	catfile_rc=0	anchor_hits_at_base=0
R39-C1-14	corpus/lessons/round-38.md	catfile_rc=0	anchor_hits_at_base=0
R39-C1-15	corpus/lessons/round-39.md	catfile_rc=128	anchor_hits_at_base=0
R39-C1-16	corpus/lessons/round-36.md	catfile_rc=0	anchor_hits_at_base=0
```

Same table recomputed at `HEAD` (`bbd9b97`) gave identical values (all anchors 0; the same 3 files
absent). Verdict: **PASS** — 10 rows on files present at base, 5 rows on 3 files this round creates
(`census/round-39/records/waves-wait.txt`, `census/round-39/records/waves-capture.txt`,
`corpus/lessons/round-39.md`); every anchor occurs 0 times at base, which is exactly the base-arm
requirement.

### 1.2 Base-arm control reproduction (counter over the frozen items)

```
S=/fast/scratch/hyaku/souji-r39/W1ExecC1Items; mkdir -p "$S/tmp2";
cd /home/vgpnk/Projects/shokunin/souji-shokunin && TMPDIR=$S python3 -B census/round-39/c1-counter.py \
  --root . --rev ed30b7f5b77939c9073348d810730bc4f355708d --items census/round-39/c1-items.tsv \
  --register census/round-39/cells.tsv --scratch "$S/tmp2"
```

Tail: `SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0
items_sha=d892b74f8358`, rc 1. `diff` against `census/round-39/records/c1-before.txt` →
`IDENTICAL-TO-c1-before.txt`. Verdict: **PASS** — the committed control receipt is exactly
reproducible; 16/16 rows read OPEN at base, and 5 of them via `OPEN FILE-ABSENT`.

### 1.3 Lane-wide whole-token counts at base (ambiguity measurement)

One `git grep -F` over all 67 anchor/must/mustnot tokens at `ed30b7f`, then `has_token` applied per
line (the counter's own function, imported from the counter module — no reimplementation):

```
R39-C1-01 anchor_global=0  must:S246=9,SOURCES-rows=170=0,SOURCES-added=8=0,W04=47=0
R39-C1-02 anchor_global=0  must:w1-reports=42/42=0,w2-reports=32/32=0,W2MutBattery=3,dead=0=14,settled-after-closure=0
R39-C1-03 anchor_global=14 must:waves=1=0,dead=0=14
R39-C1-04 anchor_global=7191 must:records==66,failed=0=2104,uncovered=0=313
R39-C1-05 anchor_global=0  must:068f75dc=3,souji-round-38.md=4,erratum=61  mustnot:floor=2=0,known=979
R39-C1-06 anchor_global=0  must:r38-citation-commit=15,r38-drift-write-envelope=20,r38-drift-record=27,r38-drift-mutants=15
R39-C1-07 anchor_global=0  must:5f0dd45=3,cites-a-revision=0  mustnot:/fast/scratch=2060
R39-C1-08 anchor_global=0  must:a7-counter-fixes2.txt=2,r38-counter-arms.py=5
R39-C1-09 anchor_global=0  must:tighter-only=8,A0=556,superseded=1321
R39-C1-10 anchor_global=0  must:fcdecaa=12,measured-revision=4
R39-C1-11 anchor_global=0  must:LOG-line-1855=0,cases=9=199,fail=6=53
R39-C1-12 anchor_global=0  must:LOG-line-1862=0
R39-C1-13 anchor_global=0  must:QUALITY-line-209=0,escapes=9=24
R39-C1-14 anchor_global=0  must:vacuity-operation=mismatches=3=0,three-rows=0
R39-C1-15 anchor_global=0  must:6949319=1,78ea25a=1,f10a3a8=1,20eea73=1,a512efb=1,9b9e2f8=1,cb5737a=1,be66886=1,c5050ea=1
R39-C1-16 anchor_global=0  must:in-place=255,correction=3008,line-23=2
```

(`records==66` is the literal token `records=` counted 66 times lane-wide.)

### 1.4 Reachability: can all 16 rows close at once?

Fixture `$S/soup` — fresh `git init`, `git rev-parse --show-toplevel` asserted equal to the fixture
dir, base bytes of the 10 existing files copied via `git show`, the 3 round-39 files created, one
line appended per row (`<anchor> round-39 record: <must tokens>`; row 04 written `records= ` with a
non-alphanumeric delimiter), `tools/souji-citation-reconcile.py` copied from base, one commit, then
the counter at that commit:

```
--- soup rc=1
ITEM R39-C1-01 CLOSED
...
ITEM R39-C1-16 CLOSED
SUMMARY items=16 open=0 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
```

Verdict: **PASS** — the frozen predicate is decidable and jointly reachable (`open=0`); rc 1 only
because the register file does not exist in the fixture (`cells=0 < min 6`), which is the register
arm, not the item arm.

### 1.5 Falsification arms (the point of this seat)

Fixture `$S/canonical04` — identical to `soup` except row 04's line is the canonical receipt form:

```
ITEM R39-C1-04 OPEN PREDICATE-MISSING census/round-39/records/waves-capture.txt missing=['records='] hits=1
SUMMARY items=16 open=1 ...
```

Fixture `$S/prose` — identical to `soup` except rows 05/10/11/13/16 written in the lane's own
prose conventions (`LOG.md:1855`, "measured revision", ":23", and an erratum sentence using "known"):

```
ITEM R39-C1-05 OPEN PREDICATE-MISSING corpus/lessons/round-39.md missing=[] hits=1
ITEM R39-C1-10 OPEN PREDICATE-MISSING SCORECARD.md missing=['measured-revision'] hits=1
ITEM R39-C1-11 OPEN PREDICATE-MISSING LOG.md missing=['LOG-line-1855'] hits=1
ITEM R39-C1-13 OPEN PREDICATE-MISSING corpus/QUALITY.md missing=['QUALITY-line-209'] hits=1
ITEM R39-C1-16 OPEN PREDICATE-MISSING corpus/lessons/round-36.md missing=['line-23'] hits=1
SUMMARY items=16 open=5 ...
```

Fixture lines used (from the fixture commits): `SUMMARY records=4 failed=0 uncovered=0` (canonical04);
`R39-C1-05 erratum: `068f75dc` added `souji-round-38.md` under the lane; the prompt's author is not known.`;
`R39-C1-10 names `fcdecaa` as the measured revision.`;
`R39-C1-11 correction: `LOG.md:1855` reads `cases=9 pass=3 fail=6`; no r37 receipt carries it.`;
`R39-C1-13 correction: `corpus/QUALITY.md:209` reads "(0)"; the before-control reads `escapes=9`.`;
`R39-C1-16 correction: the in-place rewrite of `corpus/lessons/round-36.md:23` is owed.`

Single-row reproduction of row 04 against the canonical line, before the aggregate fixture:

```
ITEM R39-C1-04 OPEN PREDICATE-MISSING census/round-39/records/waves-capture.txt missing=['records='] hits=1
ITEM R39-C1-04 CLOSED                       # same row, same commit shape, line "SUMMARY records= 4 ..."
```

## 2. Per-row verdicts

| row | file | cat-file -e | anchor hits @base | must tokens individually satisfiable | verdict |
|---|---|---|---|---|---|
| R39-C1-01 | corpus/lessons/round-38.md | rc 0 | 0 | yes (`S246` grounded at `corpus/SOURCES.md:193`; `SOURCES-rows=170` verified = 170 rows at base; `W04=47` from the spot-check) — all three literals are novel lane-wide | DECIDABLE |
| R39-C1-02 | corpus/lessons/round-38.md | rc 0 | 0 | yes; `w2-reports=32/32` matches the 32 w2 reports now on disk (31 at the spot-check); `W2MutBattery`/`dead=0` have precedent | DECIDABLE |
| R39-C1-03 | census/round-39/records/waves-wait.txt | rc 128 | 0 | yes (`waves=1 dead=0`, k=v record style) | DECIDABLE — **generic anchor** (see F3) |
| R39-C1-04 | census/round-39/records/waves-capture.txt | rc 128 | 0 | **no, not in the canonical form**: `records=` needs a non-alnum character right after `=` | **FLAGGED F1** |
| R39-C1-05 | corpus/lessons/round-39.md | rc 128 | 0 | yes (`erratum` 61, `068f75dc` 3, `souji-round-38.md` 4); mustnot `floor=2` inert (0), mustnot `known` live and self-blocking | **FLAGGED F2** |
| R39-C1-06 | SKILL.md | rc 0 | 0 | yes; all four fixture stems have precedent in-file | DECIDABLE |
| R39-C1-07 | corpus/lessons/round-39.md | rc 128 | 0 | yes, but `cites-a-revision` is a novel hyphenated literal (0 lane-wide); mustnot `/fast/scratch` (2060) is the intended prohibition | DECIDABLE — literal-form note |
| R39-C1-08 | census/round-38/preregistration.txt | rc 0 | 0 | yes (`a7-counter-fixes2.txt` 2, `r38-counter-arms.py` 5) | DECIDABLE |
| R39-C1-09 | census/round-38/preregistration.txt | rc 0 | 0 | yes (`tighter-only` 8, `A0` 556, `superseded` 1321; the tag gates the line) | DECIDABLE |
| R39-C1-10 | SCORECARD.md | rc 0 | 0 | only as the **hyphenated** literal `measured-revision` (4 in-file) — "measured revision" (240 lane-wide) fails | **FLAGGED F3** |
| R39-C1-11 | LOG.md | rc 0 | 0 | only as `LOG-line-1855` (0 lane-wide); the lane's correction convention is `LOG.md:1855` (e.g. `LOG.md:1771` `R29-CORRECTION LOG.md:1758`) | **FLAGGED F3** |
| R39-C1-12 | LOG.md | rc 0 | 0 | `must` == `anchor`, so any line carrying the tag closes the row | DECIDABLE — **vacuous must set, F4** |
| R39-C1-13 | corpus/QUALITY.md | rc 0 | 0 | only as `QUALITY-line-209` (0 lane-wide); convention is `QUALITY.md:209` | **FLAGGED F3** |
| R39-C1-14 | corpus/lessons/round-38.md | rc 0 | 0 | only as the exact compound `vacuity-operation=mismatches=3` (spaces around `=` break it) + `three-rows` | DECIDABLE — strict literal |
| R39-C1-15 | corpus/lessons/round-39.md | rc 128 | 0 | yes; nine 7-hex tokens, each occurring exactly once lane-wide (`…verifier-spotcheck.md:207`) — all nine on one line, **7-hex abbreviation mandatory** (a 40-hex SHA would not match) | DECIDABLE — abbreviation-strict |
| R39-C1-16 | corpus/lessons/round-36.md | rc 0 | 0 | `in-place` (255) and `correction` (3008) are generic but gated by the tag; `line-23` (2 lane-wide, r34) is not the routed text's form (`…round-36.md:23`) | **FLAGGED F3** |

Decidability summary: **16/16 rows are decidable** (the predicate is total and jointly reachable —
`open=0` demonstrated in §1.4). **5 rows carry a must/mustnot form hazard** that makes a faithful,
convention-following line read OPEN (F1, F2, F3 ×3), and 2 rows have weak anchors or a vacuous must
set (F3, F4).

## 3. Flags (ambiguity findings, in severity order)

**F1 — R39-C1-04 `must` token `records=` cannot be satisfied by the canonical receipt form.** The
token ends in `=`; `has_token` requires the following character to be non-alphanumeric, so
`SUMMARY records=4 failed=0 uncovered=0` → `missing=['records=']` (measured twice, §1.5). Only
`records= <n>`, `records=(<n>)`, `records=` + EOL, etc. close the row. The anchor `SUMMARY` is the
weakest in the set (7 191 lane-wide whole-token lines) and provides no gating; in a capture file
that quotes several counters, a different `SUMMARY … failed=0 uncovered=0` line carrying
`records= ` would close the row on the wrong bytes (false CLOSED). **Recommendation to the writer:
emit `records= <n>` with a space (or `records=(<n>)`), never `records=<n>`.**

**F2 — R39-C1-05 `mustnot` token `known` is a live English word that the intended erratum
naturally contains.** `floor=2` is inert (0 lane-wide), but `known` occurs on 979 lane-wide lines and
fires on any anchored line using it — demonstrated: the erratum sentence "…the prompt's author is
not known." reads the row OPEN (§1.5). The failure is reported as `missing=[]`, which names no
cause. **Recommendation: write the erratum without the standalone word `known` (e.g. "unevidenced").**

**F3 — rows 10/11/13/16 key on hyphenated pointer literals that the lane does not use.** Measured
0 lane-wide occurrences each for `LOG-line-1855`, `LOG-line-1862`, `QUALITY-line-209`; the lane's own
correction convention is `LOG.md:<n>` / `QUALITY.md:<n>` (e.g. `LOG.md:1771`
`R29-CORRECTION LOG.md:1758 measured at rev …`), and the routed text for R16 names
`corpus/lessons/round-36.md:23`. `measured-revision` occurs 4 times against 240 occurrences of
"measured revision". Four rows read OPEN when written in the lane's conventions (§1.5). These rows
are decidable but their literal form is counter-intuitive; **the fix is documentation, not a
contract change: the writer must emit `LOG-line-1855`, `LOG-line-1862`, `QUALITY-line-209`,
`line-23`, `measured-revision` verbatim.**

**F4 — R39-C1-12's `must` set is the anchor itself.** `anchor == must == LOG-line-1862`, so the row
closes on any line that merely contains the tag, even a table cell or an index row that says nothing
about `LOG.md:1862`. The row adds zero constraint beyond tag presence; it is the one row a
"tag-only" write satisfies. Not undecidable, but its calibration value is the lowest of the 16.

**F5 — generic anchors (rows 03, 04).** Every other anchor is a unique `R39-C1-NN` tag (0 lane-wide).
`dead=0` occurs on 14 lane-wide lines and `SUMMARY` on 7 191; in both cases the anchor supplies no
selectivity outside the new file, so the `must` set is the only discriminator — acceptable for 03
(`waves=1` ∧ `dead=0` is the intended line), risky for 04 (F1).

**F6 — counter diagnostics (observed, not a predicate defect).** A `mustnot` kill prints
`OPEN PREDICATE-MISSING … missing=[]`, indistinguishable from an unexplained failure; and
`--scratch <absent-dir>` dies with a `FileNotFoundError` traceback (rc 1) instead of a
`REFUSAL USAGE` line, because `tempfile.mkdtemp` requires the parent to exist
(`mkdtemp() → /…/tmp1/souji-r39-c1._h7cegkb`). Both are operability observations for C2/C3 owners;
the C1 predicate itself is unaffected. Reproduce the crash with any `--scratch` path that does not
exist.

## 4. Content grounding spot-checks (context for F1-F5; not a re-adjudication of the defects)

- `corpus/SOURCES.md` at base holds exactly **170** `^| S<n> |` rows → `SOURCES-rows=170` agrees with
  the base bytes; `SOURCES-added=8` and `W04=47` come from the spot-check's R1 measurement
  (`corpus/lessons/round-38-verifier-spotcheck.md`, Routed defects R1), not independently
  re-measured here (W04 is a sources-census warning
  code, not a literal in `SOURCES.md`).
- Every value quoted by rows 02, 05, 07, 08, 09, 10, 11, 13, 14, 15, 16 appears verbatim in
  `corpus/lessons/round-38-verifier-spotcheck.md` (R1-R16), including the nine-commit list of row 15
  at line 207 and `068f75dc`/`5f0dd45` in R5/R7. Rows are grounded in the routed text, not invented.
- Rows 05, 07, 15 share one file the round must create (`corpus/lessons/round-39.md`); rows 01, 02, 14
  share `corpus/lessons/round-38.md`; rows 08, 09 share `census/round-38/preregistration.txt`;
  rows 11, 12 share `LOG.md`. Each shared file needs **one distinct line per row** (the counter
  matches per line, and a single line carrying two tags would close both — permissible but weaker).

## 5. Verdicts

| check | verdict |
|---|---|
| File existence at base (`git cat-file -e`, per row) | **PASS** — 10 rc 0; 5 rows on 3 round-created files rc 128, which the base arm reports as `OPEN FILE-ABSENT` |
| Anchor occurs <1 time at base | **PASS** — 16/16 rows, 0 hits at both `ed30b7f` and `bbd9b97` |
| Anchor distinctiveness | **PASS with flags** — 14/16 are unique tags; 03 (`dead=0`) and 04 (`SUMMARY`) are generic (F5) |
| `must` tokens individually satisfiable | **PASS with flags** — all tokens are emit-able; 04 fails in its canonical form (F1); 10/11/13/16 fail in the lane's own conventions (F3); 14 and 15 are strict literals |
| `mustnot` tokens not self-blocking | **FAIL for row 05** — `known` fires on a natural erratum sentence (F2); `floor=2` is inert |
| Predicate reachable / joint closure | **PASS** — fixture `soup` reads `open=0` with the frozen counter and items bytes (`items_sha=d892b74f8358`) |
| Base-arm control reproducibility | **PASS** — byte-identical to `census/round-39/records/c1-before.txt` (`open=16`) |

## 6. Risks, retained evidence, blockers

Risks to the landing: (a) the five rows above can read OPEN on honest work unless the exact literals
(`records= `, no standalone `known`, `LOG-line-1855`, `LOG-line-1862`, `QUALITY-line-209`,
`line-23`, `measured-revision`, `vacuity-operation=mismatches=3`, 7-hex SHAs) are emitted — the fix is
a write-time checklist, not an amendment; (b) rows 03/04's anchors give no selectivity, so a
`waves-capture.txt` that quotes several `SUMMARY` lines can close 04 on unrelated bytes (a false
CLOSED, the direction the counter cannot detect); (c) `corpus/lessons/round-39.md` must exist at the
landing revision or rows 05/07/15 read `FILE-ABSENT` regardless of content.

Retained scratch (still on disk, 3.1 MB): `/fast/scratch/hyaku/souji-r39/W1ExecC1Items/{soup,canonical04,
prose,fixture}` — four throwaway git repos, each `git init`'d with `rev-parse --show-toplevel`
asserted, plus `scratch-*/`, `tmp1`, `tmp2` and `items-04.tsv`. Nothing under `/tmp`, nothing in the
fleet repo, no clone of the lane.

Blockers: none.
