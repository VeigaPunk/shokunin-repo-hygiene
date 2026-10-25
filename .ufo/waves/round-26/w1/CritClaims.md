# CritClaims — round-26 claim-set falsification (C1/C2/C3)

Seat: read-only critic. Reviewed revision: **0833de9591a7db81cdfa4efda2cdad2e75606f58** (lane `master`, ahead of base 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd by 6 commits). Preregistration read at the working tree (frozen landing commit 89e0fce per assignment; amendment 1 and 2 read). Scratch `/var/tmp/souji-r26-CritClaims/`, removed after the run. No installs.

## Status

STATUS: PASS — review complete. Verdict: the three claims are **separable at the counter-file level but overlapping at the declaration/attribution level**; C2's frozen K2 is **red at the reviewed tip**; C3's frozen K2 literal is **unsatisfiable by the landed fixture** and the fixture's case set is a substitution, not the frozen 12; C1's axis call is **right by the R2 taxonomy, thin by the AXES definition**; C3's operability call is **right** (not calibration-dressed).

## Evidence

All commands run from `/home/vgpnk/Projects/shokunin/souji-shokunin`; lane Python via `python3 -B`.

1. Lane state, rev 0833de9:
   `git log --oneline 0eca7c8..HEAD` →
   `0833de9 round-26 C3: tools/souji-axis-check.py + 11-case fixture (real 11/11, stub control FALSE-GREEN-REJECTED)…`,
   `4453128 … C1: green receipt at landing tip a529c76`, `a529c76 … C1: integrate r24 scaffold payloads…`,
   `965b869 … amendment 2`, `bd6588c … wave evidence`, `89e0fce … amendment 1`, `12fd90b … preregistration freeze`.

2. C1 counters at tip (also `census/round-26/records/c1-after.tsv`, `rev=a529c762c81272d398727e6a623c801a230ac157`, `rc=0`):
   `bash census/round-26/c1-counter.sh` → `markers=0` / `headings=17 44 78 ` (n25 < n24 < n23).
   Red end (`c1-before.tsv`) → `markers=2` / `headings=17 175 231 `. Both K1/K2 green.

3. C1 landing surface: `git show --stat a529c76` → `SCORECARD.md | 151 +++---` only; `4453128` → `census/round-26/records/c1-after.tsv` only. No tool, no fixture touched by C1's landing.

4. C2 counters at tip:
   `bash census/round-26/c2-counter.sh` → `grounded_f1=2` / `registry_rows=132`.
   `python3 -B tools/souji-coverage-agreement.py --root . --rev 0833de9… --base-rev 0eca7c8…` → `grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0`, rc 0.
   Registry rows S128–S132 parse as 11 columns, status `mined`, `used-by` exactly the two admitted entries (S128–S130 both; S131/S132 entry B only).

5. **C2 K2 red at tip** — the frozen command verbatim:
   `python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries corpus/knowledge/git-auto-maintenance-trigger-set.md corpus/knowledge/git-auto-maintenance-trigger-set-r23.md --snapshot-dir census/round-26/sources --slice census/round-26/records/empty-slice --slice-verdicts census/round-26/records/empty-verdicts`
   → `FAIL … check1-no-gate` ×2, `entries=2 ok=0 slice_verdicts=0 slice_total=0 fail=2`, **rc=1**. Frozen after-literal is `entries=2 ok=2 fail=0`, exit 0 (prereg:107-108).
   Sanity arm (tool is not globally broken): same tool on `corpus/knowledge/count-objects-linked-worktree-garbage.md` → `entries=1 ok=1 … fail=0`, rc 0.
   Cause: `tools/souji-gate-check.py:56` requires a literal `\n## Gate` inside the entry; neither new entry has one (`grep -n "^## " ` shows Claim / What this does NOT establish / Lane link / Freshness only). The lesson Gate exists (`corpus/lessons/round-26.md:9`), but K2 inspects the entries.

6. C3 fixture, real arm: `python3 -B tests/fixtures/r26-axis-check.py --tool tools/souji-axis-check.py` →
   `cases=11 pass=11`, **rc 0**, and **no `control=` token on the last line**.
   Stub arm: `… --stub` → `cases=11 pass=4 control=FALSE-GREEN-REJECTED`, **rc 1**.
   Frozen K2 literal (prereg:199) is `cases=12 pass=12 control=FALSE-GREEN-REJECTED`, exit 0. No single invocation of the landed fixture can print that.

7. C3 self-host: `python3 -B tools/souji-axis-check.py --prereg .ufo/waves/round-26/preregistration.txt --scorecard SCORECARD.md` → `claims=3 flags=0`, rc 0.

8. Frozen red-before command, verbatim (prereg:61):
   `python3 -B tools/souji-receipt-run.py run --root . --rev 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd --label census/round-26/c1-counter.sh -- bash census/round-26/c1-counter.sh`
   → `error: the following arguments are required: --tool, --out` (the CLI at `tools/souji-receipt-run.py:344-352` has no `--label`).
   With the correct flag, same rev: `--tool census/round-26/c1-counter.sh` → `TOOL-ABSENT … does not exist at 0eca7c8…` (the counter enters at 12fd90b; `git ls-tree 0eca7c8 census/round-26/` is empty).
   The committed `c1-before.tsv` therefore records `rev=12fd90bc…`, not the named base. Value honesty holds only because `git diff 0eca7c8 12fd90b -- SCORECARD.md` is empty (byte-identical).

9. R2/R4/R3 probes against the landed tool (synthetic preregs/scorecard in scratch):
   - `axis: operability` + `surface-class: measurement` (second claim on calibration) → `claims=2 flags=0`, rc 0.
   - `surface-class: fixture-expansion` then `surface-class: measurement` (duplicate key, last wins) → `claims=2 flags=0`, rc 0; this duplicate-line shape is landed **fixture case 10** (`tests/fixtures/r26-axis-check.py:160-169, rc=0`).
   - `axis: operability` + `surface-class: fixture-expansion` (the r25-C2 shape) → `FLAG C1 R2 … allowed only on 'coverage'`, rc 1. The rule works; the fixture never tests it.
   - claim body (outside the machine block) with `EVERY row … no row` plus `enumerate: the files` → `claims=1 flags=0`, rc 0.
   - `enumerate: grep -c no SCORECARD.md` (a real counting command) → `FLAG C1 R4 … contains the universal quantifier 'no'`, rc 1.
   - scorecard coverage 7 / calibration 7 / operability 8, single claim on calibration → `FLAG - R3 … lowest … 'coverage'`, rc 1 (tie broken by table row order).

## Findings

1. **C3's frozen K2 is unsatisfiable as written and does not match the landed artifact.** Prereg:199 demands one run printing `cases=12 pass=12 control=FALSE-GREEN-REJECTED` with exit 0; `tests/fixtures/r26-axis-check.py:219-224` prints `control=` only when `--stub` is set and then returns 1, and the case list is 11 (`:4`, `CASES` at `:72-176`). The landed commit message states "11-case fixture" — the divergence was known at landing. Impacted: operability (C3's own gate is red by its frozen rule).

2. **The frozen case set was substituted, and the discriminator is the case that vanished.** Frozen case 1 `r25-C2-replica … flagged on its frozen operability axis [discriminator]` has no landed twin; landed case 1 is "axis not owned (freshness)" (`:74-82`). Frozen case 4 (fixture-expansion **on operability**) → landed case 3 tests fixture-expansion **on calibration** (`:92-100`). Frozen case 9 (universal clause **with** enumerate passes) and frozen case 12 (control as a case) are absent; frozen case 8 (claim-text scan) is replaced by "quantifier inside the enumerate value" (`:142-150`). Net: 11 cases with substitutions, presented against a 12-case frozen literal. Impacted: operability (prevention of R26-M1 is untested), calibration (the round's stated mistake-fix is unproven).

3. **R4's implementation is not R4's frozen text.** Prereg:174-176: flag a *claim text* containing a whole-word `all/every/complete/none/no` without a same-claim `enumerate:` line *naming its counting command*. `tools/souji-axis-check.py` (`check()`, R4 branch) never reads claim text; it flags a universal word **inside the enumerate value**, and otherwise only checks presence. Demonstrated: claim body with `EVERY … no` + `enumerate: the files` → 0 flags; `enumerate: grep -c no SCORECARD.md` → false flag. Impacted: operability (instrument contract), calibration (false assurance).

4. **R2 has two silent bypasses, one of them fixture-blessed.** `NEUTRAL_SURFACES={"receipt-binding","measurement"}` means any claim can self-declare `measurement` on any axis and escape R2 (verified 0 flags); duplicate `surface-class:` lines overwrite, last-wins, so appending `surface-class: measurement` after a prohibited class escapes (verified 0 flags), and landed fixture case 10 certifies that duplicate shape as a *pass*. Also exact-string matching means the prereg's own body spelling `knowledge-entry + registry-append` would be silently neutral if it reached the machine block. Impacted: operability (gate has a hole), calibration (the simplest way to pass the new gate is to mis-declare the surface class — the very defect it targets).

5. **C2's frozen K2 is red at 0833de9.** Both admitted entries lack `## Gate`; `entries=2 ok=0 fail=2`, rc 1 against a required `ok=2 fail=0`. The evidence is at `corpus/knowledge/git-auto-maintenance-trigger-set.md` (Gate only referenced at :52) and `…-r23.md` (no Gate at all). Impacted: coverage (the round's sourced/assimilation claim cannot be scored green on its own frozen counter as landed).

6. **Amendment 2 relaxes a kill predicate while claiming it changed none.** The original C1 kill rule forbids "any byte change inside the base SCORECARD.md lines 1-171 … other than the planned-bullet additions inside `## Planned`". Base line 92 is the `blob-bound receipts (r23)` row (base 63-94 = Capabilities), and the landed R3 note sits on it (`SCORECARD.md:153`), plus two capability rows land at tip `:155-156` (also inside base 63-94). Under the frozen wording these are kills; amendment 2 item 5 authorizes them ("56 lines … no predicate … changed" notwithstanding). This is a **pre-data relaxation**, not a clarification. Impacted: calibration (the round's own contract integrity), operability (precedent for amending a predicate after freeze).

7. **The red-before receipts are not the frozen commands, and the frozen commands cannot run.** `--label` is not an option (`--tool`/`--out` required), and a counter at rev 0eca7c8 is refused `TOOL-ABSENT`. `c1-before.tsv` is a 12fd90b-tree run; `c3-before.tsv` the same (`rev=12fd90bc…`). The base literal is truthful only by the verified byte-identity of SCORECARD.md across 0eca7c8→12fd90b. Impacted: calibration (provenance of the do-nothing control), operability (a frozen command that no seat can execute).

8. **R3's tie-break is SCORECARD row order, and it inverts at saturation.** `min(scores, key=…)` over parse order: with coverage 7 and calibration 7 tied, a calibration claim is flagged demanding `coverage` (verified). The lane's saturation line is 8 (`SCORECARD.md` § Saturation); once calibration reaches 8 all three tie and R3 permanently demands the first row. Impacted: calibration (a brittle "lowest axis" obligation), coverage (the rule collapses to one axis name).

9. **C1 counts file layout, not self-assessment-vs-observed-state.** `census/round-26/c1-counter.sh` runs `grep`/`awk` on `SCORECARD.md` alone; no command reads any other repo path to compare an entry against observed state. AXES.md defines calibration as "Self-assessment quality … SHONEN.md/SCORECARD entries match observed repo state". C1 repairs a real self-assessment-file defect (a measurements table unreachable by heading scan, a stale generation scaffold), so the axis family is right — but the measurement is a format lint, and with score movement forbidden the claim is indistinguishable from tidying. Impacted: calibration (claim substance, not axis label).

## Attack log

A1 — **C3 frozen K2 unsatisfiable.** Counterexample: `cases=11 pass=11` rc0 (no control token) vs `cases=11 pass=4 control=FALSE-GREEN-REJECTED` rc1; the frozen literal requires both facts in one rc0 run. Evidence: `tests/fixtures/r26-axis-check.py:219-224`; prereg:199. Axes: operability (primary), calibration (a red gate counted as a capability). Smallest safe correction: split the counter into two receipts (real arm `cases=12 pass=12` rc0; stub arm `control=FALSE-GREEN-REJECTED` rc1) and restore the 12th case, or record a pre-scoring amendment that restates K2 as two commands — the count must go **up** (12), never down.

A2 — **Frozen discriminator replaced.** Counterexample: the r25-C2 shape (`fixture-expansion` on `operability`) is flagged by the tool (verified `FLAG … R2`) yet appears nowhere in the fixture; the landed case 1 is an unrelated R1 case. Evidence: fixture `:74-100`; frozen cases 1 and 4 (prereg:178-186). Axes: operability (the instrument's stated purpose), calibration (R26-M1's fix is asserted, not tested). Smallest safe correction: add the replica case and the fixture-expansion-on-operability case; keep both in the stub arm.

A3 — **R4 scans the wrong field.** Counterexample: claim text `EVERY … no` + `enumerate: the files` → rc0; `enumerate: grep -c no SCORECARD.md` → rc1 false positive. Evidence: tool R4 branch vs prereg:174-176. Axes: operability, calibration. Smallest safe correction: scan the claim's own text (machine block plus body up to the next `CLAIM`/`END`), require the enumerate value to contain a command token, and never scan the command string for quantifiers.

A4 — **R2 neutral-class and duplicate-line bypass.** Counterexamples: `operability`+`measurement` → 0 flags; `fixture-expansion` then `measurement` → 0 flags; fixture case 10 blesses the duplicate form. Evidence: `SURFACE_AXIS`/`NEUTRAL_SURFACES` in `tools/souji-axis-check.py`; fixture `:160-169`. Axes: operability (gate hole), calibration (mis-declaration is the cheapest pass). Smallest safe correction: reject multi-line `surface-class` and unknown/neutral classes in a claim that also declares a governed class; treat a second `surface-class` line as an R2 flag, not a pass.

A5 — **C2 K2 red.** Counterexample: the frozen K2 command returns `ok=0 fail=2` rc1 at the reviewed tip while the claim's own K4 and registry counters are green. Evidence: §Evidence 4-5. Axes: coverage. Smallest safe correction: add `## Gate` to both entries carrying the ≤25-word located quote + 2026-10-25 access date already written in `corpus/lessons/round-26.md:9-32`, then re-run K2 at the same tip used for the after receipt.

A6 — **Amendment 2 relaxes, and says it does not.** Counterexample: the R3 note at tip `SCORECARD.md:153` and capability rows at `:155-156` are byte changes inside base lines 63-94, which the frozen kill rule forbids outside `## Planned` (base 95-137). Evidence: base line map (`## Capabilities` 63, `blob-bound` row 92, `## Planned` 95); amendment 2 item 5. Axes: calibration, operability. Smallest safe correction: record amendment 2 in LOG.md and the round lesson as a **pre-data predicate relaxation** with its own red-arm receipt, not as a clarification; a freeze-time byte-span contract with an explicit `## Capabilities` allowance would have avoided it.

A7 — **Frozen red-before command not executable.** Counterexample: verbatim run → argparse error; corrected `--tool` at the named base → `TOOL-ABSENT`. Evidence: `tools/souji-receipt-run.py:344-352`, `c1-before.tsv`/`c3-before.tsv` `rev=12fd90bc…`, empty `git ls-tree 0eca7c8 census/round-26/`. Axes: calibration (the instrument-binding claim), operability. Smallest safe correction: bind the base literal with a command that exists at the base (`git grep -c` at 0eca7c8, as the claim text already does) and state the counter's first-appearance rev rather than pretending the counter ran at base.

A8 — **R3 tie/order dependence.** Counterexample: coverage 7 / calibration 7, claim on calibration → `FLAG … 'coverage'`. Evidence: `min(scores, key=…)`; lane saturation line 8. Axes: calibration, coverage. Smallest safe correction: `min` over the set of tied axes and accept any claim declaring one of them; make R3 inert when every owned axis is at or above the saturation line (the stagnation nudge).

A9 — **C1 axis label vs C1 substance.** Counterexample: both frozen counters are satisfiable by deleting the scaffold and reordering headings; no counter compares a SCORECARD entry to repo bytes, so "SCORECARD entries match observed repo state" is untested. Evidence: `census/round-26/c1-counter.sh`; AXES.md calibration row. Axes: calibration (substance), and it is *not* a coverage or operability claim, so no other axis is harmed. Smallest safe correction: keep the axis call, and state in the claim row that the measured predicate is file-layout integrity (not record accuracy), or add one assertion-re-derivation to the counter.

### Direct answers to the assigned questions

- **Causally separable?** Separable per AXES' letter ("each verifiable without the others having landed"): C1 reads only `SCORECARD.md`; C2 reads only corpus + registry + coverage map; C3's K1/K2 read the frozen prereg and its own tool. **Overlap, not violation:** C3's K1 (`claims=3 flags=0`) is defined over C1's and C2's machine-block declarations, so C3's green depends on their *declaration* correctness (not their landing); and C2's entire corpus landing is bundled into C3's commit 0833de9, so a receipt at that rev cannot attribute bytes to a claim. Fix the second by landing C2 and C3 in separate commits.

- **C1 axis: right or bookkeeping-without-axis?** Axis call **right by the R2 table and by AXES' "self-assessment quality" family** (it repairs the lane's own self-assessment file: a measurement table unreachable by heading scan, a stale scaffold, a lost capability/planned payload — all three payload items are present at tip `:153,:155-156,:201-202`). **Substance is thin:** the counters are a format lint, never a self-assessment-vs-observed-state re-derivation, and no score may move. It is not bookkeeping on a non-calibration axis; it is calibration claimed at its cheapest observable.

- **C3 axis: operability or calibration-dressed-as-tooling?** **Operability is right.** AXES: "Runnable artifacts … commands that exist, scripts that run"; the claim lands a CLI with refuses/exit codes and a fixture. The *defect class* it addresses (axis misattribution) belongs to discernment/calibration, but R25-M1 was caused by conflating a defect's axis with the surface's axis; declaring this instrument calibration would put `instrument-acquisition` on calibration and its own R2 would flag it. What is wrong is not the axis label but the **frozen-counter mismatch (A1)** and the **missing discriminator (A2)**: it earns less operability than it claims.

- **C2 axis:** **right** — `knowledge-entry` + `registry-append` → coverage, 5 net new registry rows, both entries `ground: F1`; its failure is execution (A5), not classification.

- **Does C1's axis survive its own R2 table?** Yes. Machine block: `axis: calibration` / `surface-class: bookkeeping-file` (prereg:9-10) → R2-clean; the landing touches only `SCORECARD.md` and one census receipt (no tool, no fixture), so the declared surface class is honest. It also relies on a counter committed at the freeze — measurement apparatus, not the changed surface.

- **Does the checker flag this prereg?** **No** — `claims=3 flags=0`, rc 0 (run, not inferred). Applying the *frozen* R4 by hand also yields 0 flags, because all three claims carry an `enumerate:` line; but that is the rule's weakness: C1's body contains the quoted literal `"None."` (Retired), C2's body contains `No staged row … every row … Every cited source`, C3's body contains `every declared axis`, and presence alone suppresses them. Note also that the machine block under-declares C2's surface (`knowledge-entry` only, while the body says `knowledge-entry + registry-append`); with exact-string matching, quoting the body form would have silently escaped R2 too. So the self-hosting 0 is partly an artifact of under-declaration.
