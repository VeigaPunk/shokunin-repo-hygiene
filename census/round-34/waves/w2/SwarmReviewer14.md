# SwarmReviewer14 — scoped findings, r34 w2 seat AttackE14b

## Status

CONFIRMED-WITH-ADDITION. W1's E14b finding (sha256sum's trailing ` -` defeats the `$`-anchored predicate, `SwarmExecutor13.md:32,54`) is real, deterministic, not load-sensitive, and the base MISMATCH is the required do-nothing behavior. The seat's implicit blockage is only partial: an honest rule-conforming repair route exists and was **executed** through the frozen counter bytes (`2b0171e2071fdc9c16a69bed12b0d040e574d8c8:census/round-34/c1-counter.py`, sha `1ad8c86c…`) — an argv correction that **AGREEs at base and at tip**. Full report: `.ufo/waves/round-34/w2/AttackE14b.md`.

## Evidence

- Probe (executed): `bash -c "git show 778747eb671f8e85ef5387bc3d7023337b30467c:tools/souji-size-census.py | sha256sum"` → `09bb8e0d9906b0dfef44775a9e5cd7c8f8a27d9bcdf559e2d371a3ef7ff1ed6d  -`, rc 0. `frozen_pred` from the frozen bytes: False on that line, True on the bare digest (`c1-counter.py:163-164`).
- Committed record matches: `census/round-34/records/controls-c1-do-nothing.txt:39`.
- Unique cause of the row's line (SCORECARD.md:67 text): `315422ba9970f03c27f8a9184446783b7fcdf0a7` (parent `d3666c3e` lacks the text; commit contains it; touches `tools/souji-size-census.py`; ancestor of list-rev) — passes `c1-counter.py:293-300`. Q76: no prior row binds cell `:67` (base-blob scan; the L33 row at `:398` binds `:174`).
- Route executions (judge() on synthetic append-only SCORECARD text): `same` argv → `BAD-CAUSE(original at parent=False at cause=False)` (value drift unsatisfiable — the argv pins blob 778747eb, output revision-independent); spaced-pipe corrected argv → `BAD-ROW(cells=9)` (`load_restatements` splits cells on literal `" | "`, `c1-counter.py:105`); tight-pipe corrected argv → **AGREE at base and tip** (`rc=0 expect_exit=0 statement is the run's last digit-bearing line`).

## Findings

1. W1's mechanism claim confirmed; no benign alternate explanation (exit 0 as stated; output revision-independent).
2. Honest route W1 left undrafted, executed end-to-end:
   ```
   | E14b | SCORECARD.md:67 | restated | 0 | `bash -c "git show 778747eb671f8e85ef5387bc3d7023337b30467c:tools/souji-size-census.py|sha256sum|cut -d' ' -f1"` | `09bb8e0d9906b0dfef44775a9e5cd7c8f8a27d9bcdf559e2d371a3ef7ff1ed6d` | 315422ba9970f03c27f8a9184446783b7fcdf0a7 | notation fix: sha256sum prints '<digest>  -' on stdin so the frozen ^digest$ anchor cannot match; tight-pipe cut emits the bare digest the row already quotes |
   ```
   Conformance: A1(b) row-file naming (`:267-268`), A1(c) statement binding (`:311-313`), cause full-40 + ancestor + wrote-the-line + own-argv-fails (`:293-300`), append-only (`:374-375`).
3. Traps for the whole 25-row batch (reproduced): `same` rows dead (BAD-CAUSE) for notation-bound items; any `" | "` sequence inside a row cell → `BAD-ROW(cells=N≠7)` — re-parse every delivered row through `load_restatements` before landing.
4. Semantics note, no defect: for notation-bound rows the "row's own argv already failed at the cause" test is trivially true; the writer test carries the evidential force (matches `preregistration.txt:52-53`; same pattern as W1's honest E05 correction).

## Attack log

Condensed (full version in AttackE14b.md): byte-verified frozen counter → probe reproduction → frozen `frozen_pred` replay → geometry checks (SCORECARD/SKILL byte-identical base→list-rev; ancestry) → `-S` cause discovery + membership validation → Q76 scan → judge() routes A/B/C at base and tip → scratch cleaned. Read-only seat; no lane file outside `w2/`; no tool installs.

## Deliveries

- `.ufo/waves/round-34/w2/AttackE14b.md` (full report)
- `.ufo/waves/round-34/w2/SwarmReviewer14.md` (this file)

Gap (labeled): routes were executed against synthetic append-only SCORECARD text via the frozen bytes' own `judge()`/`load_restatements`; no committed landing commit was measured (no lane mutation permitted).
