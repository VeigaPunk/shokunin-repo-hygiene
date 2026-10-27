# SwarmExecutor01 — r34 w1, C1 slice 1/12 (G01 G02 G03 G04a G04b)

## Status

STATUS: PASS — all five frozen items measured AGREE at base 9c76c72 (counter exit 0, `agree=5 mismatches=0`), so no restatement row is drafted for any of them; one reproduced defect in the frozen `where` line cells is disclosed as an ATTACK (inert for agreement, material for any argv-correction restatement). L1 follow-up: all 23 SKILL registry items classed; 7 mismatch, none honestly restatable (§L1 follow-up).

## Evidence

Frozen contract read first: `census/round-34/preregistration.txt` at `2b0171e2` (attempt 2 + amendments A1-A6), then
`census/round-34/c1-items.tsv`, then `census/round-34/c1-counter.py`.

Counter run (the only measurement; serialized under my own flock on top of the counter's internal `c1.lock`):

```
export TMPDIR=/fast/scratch/hyaku/souji-r34/RestateC1s1/tmp
flock /fast/scratch/hyaku/souji-r34/RestateC1s1/run.lock \
  python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev 9c76c7222a8abff027af42e37f0d160d52526bba \
  --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 \
  --scratch /fast/scratch/hyaku/souji-r34/RestateC1s1/cnt --only G01,G02,G03,G04a,G04b
```

Output (verbatim; `RC=0`):

```
ITEM	G01	AGREE	original	rc=0 expect_exit=0 predicate holds last=selftest: 69 checks, 0 failed load=4.43
ITEM	G02	AGREE	original	rc=0 expect_exit=0 predicate holds last=selftest: 47/47 passed load=4.47
ITEM	G03	AGREE	original	rc=0 expect_exit=0 predicate holds last=fixture: 8/8 checks passed load=4.36
ITEM	G04a	AGREE	original	rc=0 expect_exit=0 predicate holds last=SELFTEST pass=65 fail=0 load=4.36
ITEM	G04b	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=11 failed=0 load=4.25
SUMMARY items=5 agree=5 mismatches=0 restated=0 partial=1 rev=9c76c7222a8abff027af42e37f0d160d52526bba
```

`cat /proc/loadavg` before: `3.09 2.74 1.90`; after: `4.25 3.10 2.07` (host load < 48, so no re-take needed; the max
recorded inside the counter was 4.47). Counter bytes at `--list-rev`: sha256
`1ad8c86c9d78b79f095661850ca9883994a5d5a9d5ee629cb69e26dcd6ff9a20`. Lane HEAD while reading: `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`
(the run is pinned to `--rev`, and the counter clones from `--rev`, so later lane commits cannot leak into the reading).

Prior-correction sweep (Q76) — run against SCORECARD.md at `--list-rev`:

```
git -C <lane> show 2b0171e2:SCORECARD.md | grep -n 'selftest: 69 checks'        → NO MATCH
git -C <lane> show 2b0171e2:SCORECARD.md | grep -n '47/47'                      → NO MATCH
git -C <lane> show 2b0171e2:SCORECARD.md | grep -n '8/8 checks passed'          → NO MATCH
git -C <lane> show 2b0171e2:SCORECARD.md | grep -n 'SELFTEST pass=65'           → 326, 372, 503  (all bind SCORECARD.md:158)
git -C <lane> show 2b0171e2:SCORECARD.md | grep -n 'total=11 failed=0'          → 331, 388      (bind SCORECARD.md:167, argv souji-rev-pin.py)
git -C <lane> show 2b0171e2:SCORECARD.md | grep -nE '^\| [A-Z][0-9]{2}[a-z]? \| SKILL\.md:' → empty
git -C <lane> show 2b0171e2:SCORECARD.md | grep -n 'Round 34 registry restatements' → NO SECTION (base and list-rev)
```

So none of my five cells is Q76-bound by a prior row (the only same-statement rows bind SCORECARD.md:158 / :167);
all five agreements are direct measurements. Every item is also a genuine "current numeric outcome" row:
- base line 202: `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest` (69/0 at 4800fd7)
- base line 216: (47/47 at r16; 24/47 as landed r15) — current value 47/47
- base line 217: (8/8 at r16)
- base line 218: (65/0 at r19: 61 + four wrap cases) and r18-landing-pointers (11/0)

No restatement cause applies (Q75 machinery not engaged for an AGREE item); no cause full40 is claimed.

## Findings

1. **G01 agrees.** Run at base: rc 0, last digit-bearing line `selftest: 69 checks, 0 failed`, exit 0. Row at
   `SKILL.md:202` (see attack log) pins the same 69/0. Location: `SKILL.md:202`; item `census/round-34/c1-items.tsv` line G01.
2. **G02 agrees.** rc 0, `selftest: 47/47 passed`. Row `SKILL.md:216` states 47/47 at r16. The row also carries the
   historical alternative (24/47 as landed r15); the frozen predicate binds the current line, which is what the run
   prints, so no ambiguity for this cell. Location: `SKILL.md:216`.
3. **G03 agrees.** rc 0, `fixture: 8/8 checks passed`; row `SKILL.md:217` states (8/8 at r16). Location: `SKILL.md:217`.
4. **G04a agrees.** rc 0, `SELFTEST pass=65 fail=0`; row `SKILL.md:218` states (65/0 at r19: 61 + four wrap cases). Location: `SKILL.md:218`.
5. **G04b agrees.** rc 0, `SUMMARY total=11 failed=0`; same row, external-fixture cell (11/0). Location: `SKILL.md:218`.
6. **Frozen `where` line cells for the SKILL.md registry items point one line low (21 of 22)** — the cell names the *previous*
   registry row. Reproduced mapping at base (`git show 9c76c72:SKILL.md`, extracted to scratch, `grep -nF <item file>`):

   | item | frozen where | row actually carrying the item argv |
   |---|---|---|
   | G01 | SKILL.md:201 (`souji-vault-verify`) | 202 (`souji-census`) |
   | G02 | SKILL.md:215 (`r17-jj-receipts`) | 216 (`souji-preservation-evidence`) |
   | G03 | SKILL.md:216 (`souji-preservation-evidence`) | 217 (`r15-preservation-evidence`) |
   | G04a/G04b | SKILL.md:217 (`r15-preservation-evidence`) | 218 (`souji-landing-gate`) |

   Full sweep of all 22 SKILL.md items (row = the table line whose entry/self-test cells carry the item's script(s);
   computed by matching every `files` basename on a row, then disambiguating rows that cite a runner from a neighbour):
   G05 219→220, G07 222→223, G09 230→231, G11 234→235, G12 236→237, G13 237→238, G14 238→239, G15 239→240,
   G16 240→241, G17a 241→242, G17b 235→236, G18 242→243, G19 243→244, G20 244→245, G21 245→246, G23 247→248,
   G26 250→251. **G24 is the single exception**: its cell `SKILL.md:249` matches the `souji-capability-agreement` row
   exactly (`awk 'NR==249'` → `| souji-capability-agreement | gate | python3 -B tools/souji-capability-agreement.py`).
   So the cells are an inconsistent enumeration — 21 of 22 one line low, one exact — not a uniform offset.
   Lines 195-220 are byte-identical at base and `--list-rev`
   (sha256 `a839f7f67223fb295589810ad2c7b9471e8141f2855a8627024b625cbfc749a4`), SKILL.md is 428 lines at both, so the
   shift is not a revision artefact. Location: `census/round-34/c1-items.tsv` `where` column vs `SKILL.md` at base.
7. **Why finding 6 is inert for this slice but not for the claim:** `c1-counter.py:judge()` reads `item["where"]` only
   when a restatement row exists — it must equal the row's `where` cell, and for an argv correction the BAD-CAUSE branch
   pulls `blob(root, list_rev, src_file)[lineno-1]` as "the row's line". With the off-by-one, an argv-correction row on
   any of these cells would test the *neighbouring* row's text, so an honest cause could be rejected and a dishonest one
   accepted when the neighbour happens to fit. AGREE items are unaffected. Location: `census/round-34/c1-counter.py:judge`.
8. **No file was modified.** This seat ran no write in the lane outside its report/deliveries: no `git add/commit/...`,
   no `jj` mutation, no `rm`/`mv`, no signals. The lane's `SCORECARD.md` and `SKILL.md` at base and `--list-rev` were
   read through `git show` only.

## Attack log

**ATTACK-1 (frozen item metadata, not a predicate): the `where` line cells of the SKILL.md registry items are off by one
row.** Reproduced state given in finding 6: at `9c76c7222a8abff027af42e37f0d160d52526bba`, `SKILL.md:201` is the
`souji-vault-verify` row while the G01 argv belongs to line 202; likewise 215/216/217 vs 216/217/218 for G02/G03/G04a+
G04b. Consequence: a Q75 argv-correction row for such a cell is validated against the wrong source line
(`c1-counter.py` BAD-CAUSE branch), which is both a false-reject and a narrow false-accept surface. No change to a frozen
predicate, target, item or counter is proposed by me — repair is the L1's call (stricter-only), and the safest repair is
to make the counter resolve the row by its own script rather than by the frozen line number. Impact on the frozen C1
target: none for the 5 items in this slice (all AGREE without restatement); latent for the remaining 17 SKILL.md items if
any of them needs an argv correction.

## L1 follow-up — C1 mismatch classification (all 23 SKILL registry items)

Prompted by SoujiR34a2 after the first report. I measured every SKILL.md item (not only my slice) at base with the
frozen counter: **16 AGREE, 7 MISMATCH** (G05, G11, G17a, G17b, G21, G23, G24). All seven sit on cells affected by
the one-line-low binding (G24's cell is the exact one — broken for a different reason). Full detail, commands and
outputs: `deliver-c1-mismatch-classification.md`.

| item | mechanism | honest correction | honest cause accepted? |
|---|---|---|---|
| G05 | predicate unattainable — counter collapses whitespace, five `ANYLINE:\t…` conjuncts need tabs; the tool really prints the row's 1/5, 0/0, 0/0, 0/0, 1/29 | none (encoding, not a value) | no |
| G11 | value drift 36→45 at 4f30f23, but the frozen predicate `total=36 pass=36 fail=0` never held (parent 1988860 prints `total=36 pass=32 fail=4`; the row claims only "36 literal cases") | same-value | no — executed `BAD-CAUSE(original at parent=False at cause=False)` |
| G17a | deterministic drift to `matched=16`/18; passes at 7a6667cd (2/2), fails at 98e5203 (2/2) which touches no item file; non-monotonic | same-value needs an item-file cause | no |
| G17b | same runner drift **plus** `COUNT:^SCENARIO\t…` never matches collapsed lines | argv correction only | only via the neighbour cause |
| G21 | row's relative `--tool` resolves under `cwd=/var/tmp/souji-r29-c1-fixture`; with an absolute tool it prints the stated 20/20 | argv correction (`--tool {CLONE}/tools/souji-registry-agreement.py`) | honest cause 1dc6785 **rejected**; neighbour cause 6cb22dc **accepted** |
| G23 | row's `uncovered=0` now false (base: `manifests=8 … uncovered=1`); counter file has one commit, so no post-freeze item-file cause; at b8cb4b3 the row never held (`manifests=3 failed=152 uncovered=14`) | same-value | no |
| G24 | item `at` = 9420341d predates `tools/souji-capability-agreement.py` (added d4928ec), so the checkout cannot contain the script | item/counter repair | n/a |

Consequence: **no honest restatement exists for any of the seven under the frozen rules**, so `agree=60
mismatches=0` is unreachable on the frozen item set (already ≥6 items can never agree, before the 37 E-items).

**ATTACK-2 (executed, confirmed): the off-by-one makes the Q75 cause check exploitable for argv-correction rows.**
In a throwaway clone at base I appended two G21 rows and ran the frozen counter. Honest cause
`1dc678500c92164b0b2bea82b934dd03d1dfbf38` (the commit that wrote the row) → `BAD-CAUSE(cause did not write the
row's line)`; cause `6cb22dc20c9fdb3c7a49eaa1accabca339054c17` (the round-27 commit that wrote SKILL.md line 245, a
row unrelated to this item) → `ITEM G21 AGREE restated`. The item's `where` (`SKILL.md:245`) makes the counter test
the neighbour row's text (the actual row is 246), so a foreign cause passes and the true one fails. Reproduced
state, not a hypothesis.

**ATTACK-3 (construction defect): G24's `at` pin predates its own script.** `git cat-file -e 9420341d:tools/souji-capability-agreement.py`
→ path does not exist; the tool was added at `d4928ec`. The item copied the argv's `--rev` into `at`, so the counter
checks out a clone in which the row's script cannot exist and the argv can never run.

**ATTACK-4 (item predicate stronger than the row): G11.** The row says the default invocation "has 36 literal cases";
the frozen predicate asserts `pass=36 fail=0`, a pass count the row never claimed, and the r20 fixture at that
revision actually reports `pass=32 fail=4`. Same shape for G23 (`manifests=7` hardened from `m ≥ 1`).

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w1/deliver-c1-G01.md`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w1/deliver-c1-G02.md`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w1/deliver-c1-G03.md`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w1/deliver-c1-G04a.md`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w1/deliver-c1-G04b.md`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w1/deliver-c1-mismatch-classification.md` (L1 follow-up: all 23 SKILL items classed)

Scratch `/fast/scratch/hyaku/souji-r34/RestateC1s1/` was removed after the receipts above were copied into these files.

## Risks / out of scope

- The junk control `tests/fixtures/r34-c1-junk.py` (A4/A5) is a C1 claim component but not part of this seat's item slice;
  I neither ran nor edited it.
- My readings are at base only, as assigned; the frozen target's tip reading is the L1's post-integration run.
- Tool installs: none (no tool was installed, upgraded or removed during this seat).
