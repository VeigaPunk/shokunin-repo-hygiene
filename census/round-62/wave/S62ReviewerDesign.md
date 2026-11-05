# Report: round 62 seat S62ReviewerDesign — design attack on C1 (receipt-writer index-flag guard)

Delivered: `.ufo/waves/round-62/w1/S62ReviewerDesign/report.md` (full findings + probe recipes), plus
`candidate-construction.py` and `attack-counter.py` in the same directory. Full report below is the same content;
scratch `/fast/scratch/hyaku/souji-r62/S62ReviewerDesign/` removed at yield.

---

## One-line summary

DESIGN: **admit-with-named-limits** — frozen 7-row matrix, do-nothing control and regression arm all hold; the flag
check is refusal-unconditional, placed before `--allow-dirty`, and covers every flag class git 2.56.0 admits
(skip-worktree, assume-unchanged, gitlink, worktree-deleted, non-cone sparse). Named limits are git-version scope
of the status-blindness and the sparse-checkout cost, both carried into the lesson, not the claim.

## Findings (severity-ordered; full table in report.md)

| id | sev | finding |
|---|---|---|
| A10 | **C** | The class check is load-bearing: a stub passing the full r60 fixture AND refusing flagged rows with `REFUSAL-OTHER: …` must be caught by the counter's literal `RECEIPT-INDEX-FLAG-CONCEALED:` match — no other probe distinguishes it. Keep the frozen class predicate verbatim. |
| A1/A13 | H | Lane index at 16fa821f = 17350 entries, ALL `H` (rc=0, run directly) — the no-honest-run-blocked baseline is direct today and version-scoped only via git's probe-dependent status silence (S291 NOTES). |
| A9 | H | No bypass: `--allow-dirty`, `--max-bytes`, `--style`, `GIT_DIR`/`GIT_WORK_TREE` env, and post-check probing all leave rc=2 with the class constant. Flag block correctly precedes `# behaviour 7` and never reads `ns.allow_dirty`. |
| A2 | L→H | `ls-files -v -z` record layout confirmed by od on git 2.56.0: `tag` then a **space byte**, then raw path (newline preserved, no C-quoting under `-z`). Candidate must parse `rec[0:1]` for tag and `rec[2:]` for path. Cheap amendment to pin in the lesson. |
| A5/A18/A19 | M/H | **Non-cone sparse-checkout IS a live flag-setting mechanism on this host** (`probe-sparse`: both `counter.py` and `tools/instrument.sh` get `S`, status silent). Cone mode does not (all `H`). Lane is unaffected (17350 H), so the claim stays green; the cost must be a **Named-limit**, not a row. |
| A7 | M | Gitlink `skip-worktree` succeeds (rc=0, tag `S`) and hides a submodule HEAD change from `status`. Candidate refuses it unconditionally — no design change, cite in lesson. |
| A3 | M | Skip-worktree on a worktree-deleted path hides **that**: status empty despite the file's absence. Cheapest additional row `D2` would catch a counter that over-relaxes the class check. |
| A8 | M | Row F is a **calibrated refusal, not blanket harm** (lane baseline empty, so no honest lane shape trips it; the manual itself says the bit "does not work as expected"). Falsifier would be a future repo with an honest `S` on its counter at byte-identical committed state — none exists today. |
| A12 | M | The claim is calibration-*labelled* but operability in substance (one instrument hardened against overreach caught in r61 by the reviewer seat). Cannot move calibration 7 alone (AXES.md ≥2 demos); L1 should carry the honest relabel in the lesson, not widen the claim. |
| A4 | H→L | Untracked files CANNOT be flagged (`update-index` refuses, rc=128) on git 2.56.0 — assumption holds exactly. |
| A11 | M | Do-nothing control: base bytes give `new_forgeries=3` (rows D, E, F ACCEPT), exit 1; **G is a legitimate refusal under a different reason** ("differs from committed bytes"), NOT a forgery-accept — the frozen predicate's `new_forgeries=3` should be stated as "3, because G's refusal is legitimate". |
| A14/A16/A20/A21 | L | Failure-mode, honest-receipt byte-identity, r60 regression (`pass=8 fail=0 controls=REJECTED`), selftest (`cases=12 pass=12 fail=0`) all green. |
| A17 | L | Late-ref-loss / one-migration shapes are not a false-green: OUT-exists plus unconditional flag refusal block the second receipt. |

## Most likely false-green still admitted + cheapest catching row

A counter implementation that classifies the refusal by rc==2 alone (or any prose "refuses" reading). My A10 stub
passes the full r60 fixture while producing the wrong refusal message. Cheapest added row: **D2 —
`update-index --skip-worktree <worktree-deleted>`** (A3), which produces a shape whose status is already empty and
whose only signature is the `S` tag the counter must name in the frozen class constant.

## Named limits

1. **git-version scope** — skip-worktree/assume-unchanged status silence is a probe result at git 2.56.0 (S291 NOTES
   explicitly declines to promise it).
2. **Non-cone sparse-checkout** sets `S` as a matter of course; the refusal will block an honest instrumented round
   using it. Constraint, not bug: today's lane is 17350 H (A13), so no honest run is blocked now.
3. **Cone-mode sparse-checkout** leaves `H` tags at rest and is therefore invisible to the flag check — the candidate
   is exactly as blind to it as base; that is the design's declared boundary, not a gap.
4. **Whole-index saturating scan only** — the block refuses any non-`H` tag wherever it lives, so it remains correct
   under whole-index reads; no per-directory refinement is needed or promised.

## Tooling / methods recorded

- No tool installed or upgraded (RULES.md read; not needed).
- Scratch: `/fast/scratch/hyaku/souji-r62/S62ReviewerDesign/` — removed at yield.
- Probes reproducible from `report.md` §2 recipes (exact commands + observed rc + first output line cited per row).
