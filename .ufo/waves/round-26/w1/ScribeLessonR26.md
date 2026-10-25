# ScribeLessonR26 — round-26 lesson draft (r25 shape) with counter-state report

## Status

STATUS: PARTIAL — the r25-shaped lesson draft is delivered at `.ufo/waves/round-26/w1/lesson-r26.md`, but two of the round's frozen counter arms do not hold at the tip revision I read: C2's K2 exits 1 (`check1-no-gate` on both admitted entries) and C3's K2 prints `cases=11 pass=11` against a frozen `cases=12 pass=12 control=FALSE-GREEN-REJECTED`. I drafted the verdicts from measured bytes instead of asserting the prereg's after-values.

## Evidence

All commands run from `/home/vgpnk/Projects/shokunin/souji-shokunin`; after-values read at lane revision
`ba8b54b85814dd980aa96050fe111c7cbfd4956a` unless the receipt names another candidate.

```
$ git log --oneline -7            # tip pinned for this draft
ba8b54b round-26 C1: c1-after regenerated at fix tip 07f83e6 (markers=0, headings=17 44 78)
07f83e6 round-26 C1 fix: append the two r24 capability rows ... spans re-verified byte-equal
d6fe8a1 round-26 C1: append-only mapping note at SCORECARD EOF
ea0bbe6 round-26: lessons file (Gate decision, findings, residuals) + Entry B enriched citations
d6c13b0 round-26 C2 receipts ...     e0f8dcd round-26 C3 receipts ...     d2e6253 round-26 C3 ...

$ bash census/round-26/c1-counter.sh
markers=0
headings=17 44 78
$ grep -c 'debris census (r24)\|coverage-map agreement (r24)' SCORECARD.md      -> 2  (lines 155-156)
$ grep -n '^## Capabilities\|^## Planned\|^## Saturation' SCORECARD.md          -> 124, 158, 204
$ grep '^rev=' census/round-26/records/c1-after.tsv                             -> rev=07f83e69979b1032f9de4fe876739a8dccc7242b
$ cat census/round-26/records/c1-before.tsv   -> rev=12fd90b…; markers=2; headings=17 175 231

$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
souji   ok   /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md          (exit 0; W04 duplicate-url warnings only)
$ grep -cE '^\| S[0-9]{3} ' corpus/SOURCES.md                                   -> 132
$ git show <rev>:corpus/SOURCES.md | awk … tier/status counts
base 0eca7c8: rows=127 tier A=120 B=5 C=2 status mined=103 queued=15 rejected=9
HEAD:         rows=132 tier A=125 B=5 C=2 status mined=108 queued=15 rejected=9

$ python3 -B tools/souji-coverage-agreement.py --root . --rev ba8b54b… --base-rev 0eca7c8…
grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0             (rc 0)

$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries corpus/knowledge/git-auto-maintenance-trigger-set.md \
              corpus/knowledge/git-auto-maintenance-trigger-set-r23.md \
    --snapshot-dir census/round-26/sources \
    --slice census/round-26/records/empty-slice --slice-verdicts census/round-26/records/empty-verdicts
FAIL corpus/knowledge/git-auto-maintenance-trigger-set.md check1-no-gate
FAIL corpus/knowledge/git-auto-maintenance-trigger-set-r23.md check1-no-gate
entries=2 ok=0 slice_verdicts=0 slice_total=0 fail=2                                     (rc 1)

$ python3 -B tools/souji-axis-check.py --prereg .ufo/waves/round-26/preregistration.txt --scorecard SCORECARD.md
claims=3 flags=0                                                                          (rc 0)

$ python3 -B tests/fixtures/r26-axis-check.py --tool tools/souji-axis-check.py | tail -2
cases=11 pass=11                                                                          (rc 0)
$ cat census/round-26/records/c3-control.tsv   -> cases=11 pass=4 / control=FALSE-GREEN-REJECTED / rc=1

$ sha256sum tests/fixtures/r26-axis-check.py tools/souji-axis-check.py
2ffc18289fc82b9075ad3580cb9bec6a80384061c7d294b5aa17dbf9ca93c8da  tests/fixtures/r26-axis-check.py
14bc9632e88ef58f18108011f6645bd970cd825d0ffc1664369dc60b0d579332  tools/souji-axis-check.py

$ (scratch world /var/tmp/souji-r26-ScribeLessonR26, lane SCORECARD copied, synthetic replica)
$ python3 -B tools/souji-axis-check.py --prereg replica.txt --scorecard scorecard.md
FLAG C2 R2 surface-class 'fixture-expansion' declared on 'operability'; allowed only on 'coverage'
FLAG - R3 no claim declares the lowest-scoring non-retired axis 'calibration' ({'coverage': 8, 'calibration': 7, 'operability': 8})
claims=1 flags=2                                                                          (rc 1)

$ cd census/round-26/sources && sha256sum -c SHA256SUMS   -> 7/7 OK
$ ls -d considerthese -> No such file or directory
$ grep -c '^| Q59' corpus/QUALITY.md -> 0     $ grep -c 'round-26\|Round 26' LOG.md -> 0
```

Gate quote locations opened this run (`<=25` words each, no literal or escaped pipe): `census/round-26/sources/git-fetch.1.txt:3195-3197`;
`census/round-26/sources/git-builtin-fetch.c:2926`; `census/round-26/sources/git-builtin-pull.c:385,392`;
`/home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-trigger-prune.out:2`;
`/home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-worktree-census.out:31`;
staged refusal rows `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md:17-19`;
search-log quote `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md:25`.

Tooling: none installed or upgraded. Scratch `/var/tmp/souji-r26-ScribeLessonR26/` removed before yield.

## Findings

1. **C2's frozen K2 cannot pass as landed.** `tools/souji-gate-check.py:gate_section()` searches the *entry file* text for `\n## Gate`; neither `corpus/knowledge/git-auto-maintenance-trigger-set.md` nor `…-r23.md` carries one (entry A `:52` only points at `corpus/lessons/round-26.md ## Gate`). Result at `ba8b54b`: `entries=2 ok=0 fail=2`, rc 1. The w1 entry drafts *do* carry Gate blocks (`.ufo/waves/round-26/w1/entry-git-auto-maintenance-trigger-set.md`, `…-r23.md`, one each), so the repair is a copy into the corpus entries. Conflicting record: commit `d6c13b0`'s message and `corpus/lessons/round-26.md` § Receipts both say "real gate rc=0"; I could not reproduce rc 0 with the frozen command, and
   `git show d6c13b0:corpus/knowledge/…-trigger-set.md | grep -c '^## Gate'` prints `0` for both entries. No `c2-gate.tsv` receipt exists under `census/round-26/records/`.
2. **C3's frozen K2 is unreachable by the landed fixture.** Frozen: `cases=12 pass=12 control=FALSE-GREEN-REJECTED`. Landed `tests/fixtures/r26-axis-check.py` (sha256 `2ffc1828…`) prints `cases=11 pass=11` and only emits the `control=` field when invoked with `--stub`. The 12-case delivery is `.ufo/waves/round-26/w1/r26-axis-check.py` (per `.ufo/waves/round-26/w1/ExecAxisFixture.md`, which reports 12/12 there and names this exact 11-case blob as the file that must be overwritten). The commit `0833de9` message states the 11-case result; no amendment records the reduction.
3. **C3's discriminator case is present but not in the frozen position and not counted.** The committed fixture contains r25-C2-replica shapes at `tests/fixtures/r26-axis-check.py:106,115` (`axis: operability` + `surface-class: fixture-expansion`), but its docstring maps case 1 to "axis not owned by souji (freshness)" — the frozen set's case 1. The instrument itself flags the replica (Evidence, synthetic run), so R26-M1's SHOWN witness is the direct run, not a fixture case.
4. **C1's landing initially failed an amendment MUST while scoring green.** `a529c76` satisfied K1=0 and K2 `17 44 78` yet omitted the two r24 capability rows amendment 2 item 5 requires (witness: `git show a529c76:SCORECARD.md | grep -c 'debris census (r24)'` → `0`; report `.ufo/waves/round-26/w1/ExecC1Verify.md` finding 3). Repaired at `07f83e6`; the rows are at `SCORECARD.md:155-156` now and `c1-after.tsv` is re-bound to `07f83e6`. The frozen kill rule has no arm for this MUST.
5. **C1's reorder leaves five position-literal cross-references stale.** `SCORECARD.md:36-40` still cite `:181`, `:180`, `:92`, `:224`, `:225`; at `ba8b54b` those lines are unrelated prose. `d6fe8a1` appended `mapping corpus/lessons/round-25.md § …` to each of the five lines, which gives an authority path but does not correct the numeric references. Amendment 2 protects those bytes from editing, so the defect is displaced, not closed. Location: `SCORECARD.md:36-40`.
6. **C2 receipts are incomplete against the prereg's own list.** Present: `c2-before.tsv`, `c2-after.tsv`, `c2-k4-base.tsv`. Missing: `c2-k4-after.tsv` and `c2-gate.tsv`. K4's after-value is nonetheless reproducible (§ Evidence, the `souji-coverage-agreement` run: `grounded=9 … kill_tested=7`, rc 0); K2's is not (Finding 1).
7. **LOG.md has no round-26 amendment entry.** `grep -c 'round-26\|Round 26' LOG.md` → `0` at the tip, while the prereg's AMENDMENT RULES require the amendment "logged in LOG.md + the round lesson". Amendment files 1 and 2 exist; the LOG half is unrecorded.
8. **The lane's own hygiene residue is untracked Python bytecode.** `git status --porcelain` lists `?? tests/fixtures/__pycache__/` and `?? tools/__pycache__/` — produced by lane Python run without `-B`, despite the contract's `python3 -B` rule. Also `?? census/operator-sweep-20261019/` (not opened) and a modified `census/round-26/records/c3-before.tsv` in the worktree. I did not delete anything; the owner must.
9. **Prereg hero literals all re-derive at their named bases.** C1 base `markers=2`, `headings=17 175 231`; C2 base `grounded_f1=0`, `rows=127`, K4 `grounded=7 kill_tested=7`; C3 base tool absent. Amendments 1 and 2 both carry pre-data red receipts as their rule demands.
10. **Q59 is proposed, not landed.** `.ufo/waves/round-26/w1/axis-check-docs.md` drafts the criterion row (placement note argues for a new `## Round 26 criteria` heading rather than insertion into the r25 table); `corpus/QUALITY.md` has no Q59 row at the tip. The lesson's R26-M1 `captured-by` cell therefore reads `none → Q59 (proposed)` and must not be upgraded until the row lands.

## Attack log

ATTACK 1 — **the frozen C3 case set was replaced by the landed artifact, and the substitute is verified by the same seat that changed it.** Frozen (`preregistration.txt`, CLAIM C3, cases 1–12): case 1 is the r25-C2 replica discriminator and case 12 is the always-green control arm, with K2's target `cases=12 pass=12 control=FALSE-GREEN-REJECTED`. Landed `tests/fixtures/r26-axis-check.py`: 11 cases, discriminator not case 1, control arm outside the counted set and printed only under `--stub`. This is a post-freeze relaxation of a kill-rule target in the claim's favour: the landed artefact scores `cases=11 pass=11` rc 0 while the frozen literal is unsatisfiable, and the `--stub` receipt (`c3-control.tsv`) is a second, differently-labelled run. Under the prereg's own AMENDMENT RULES this needed a stricter-only amendment with red receipts before the green; none exists. Remedy is mechanical: land the 12-case delivery and re-run K1 and K2 on the landed bytes, or amend with the red 11-case arm recorded first.

ATTACK 2 — **"real gate rc=0" is asserted by record without a reproducible command.** Commit `d6c13b0` and `corpus/lessons/round-26.md` § Receipts both claim a green gate for C2, and the prereg names `c2-gate.tsv` as the receipt; the file is absent and the frozen command returns rc 1 with `check1-no-gate` at both the receipt's own revision and the tip. Either the green was measured with different arguments (undisclosed) or the claim is unearned. Locate the exact argv and file it, or strike the sentence.
