# souji-shokunin corpus

Memory of the fleet's hygiene state. Index rows are claims — write the row
when the file exists, not before.

## knowledge/

- `obsidian-ledger.tsv` — the Obsidian-preservation ledger. Columns:
  `source_path`, `source_sha256`, `vault_path`, `vault_sha256`,
  `exported_at`, `note`. A removal qualifies as `moved-to-obsidian` only
  with a matching row (both hashes). Rows enter only when the operator
  records an export; nothing automated writes here.
- (census tables land here from r1 onward) — wrong; corrected r12 below

## lessons/

- per-round training lessons, one file per round, each with a `## Gate`
  section (candidates / admitted / rejected / spot-check) — held from r12 only; corrected below

## Known gaps

- No census data yet (r1). — stale; corrected r12 below
- No gate tool yet (r2). — stale; corrected r12 below
- Numeric rubric: axis scores start at 0 with explicit counting commands;
  a calibrated numeric rubric is a standing gap, per the kotodama precedent.

## r12 additions (2026-10-19 — appended; sections above stand, corrections below)

### Admission and sources

- `QUALITY.md` — the admission bar (Q1–Q15), each criterion citing its lesson.
- `SOURCES.md` — where souji learns (contract v1): 33 rows — `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` 2026-10-19 (full census: `bash census/round-12/sources-census.sh`) — plus `## Paths`, `## Search log`.

### Coverage map

| ground | status | entries |
|---|---|---|
| receipts: pushed / moved-to-obsidian / stale | core (SKILL.md, tools/) | `knowledge/obsidian-ledger.tsv` (operator-fed, header-only) |
| F1 git-native housekeeping vs receipts | frontier, entries held | `knowledge/git-auto-maintenance-prunes-worktrees.md`, `knowledge/git-grace-periods-and-expire-to.md` |
| F2 repository size census | frontier, no entry (r12 candidate deferred, `lessons/round-12.md` `## Gate`; sweep: `ls corpus/knowledge \| grep -ciE 'size\|structure\|sizer'` → 0, 2026-10-19) | — |
| F3 duplicate verdicts | frontier, entry held | `knowledge/dupe-finders-detect-then-act.md` |
| F4 restorable quarantine, file-system semantics | frontier, entries held | `knowledge/trash-spec-restorable-quarantine.md`, `knowledge/quarantine-same-filesystem-rename.md` |

## Frontier

- F1 git-native housekeeping vs receipts — next: does `fetch`/`merge`/`rebase` auto-maintenance prune on the fleet's live repos (exposure census, `census/round-12/scout-surfaces.md` §a: 0 prunable, 3 locked today).
- F2 repository size census — next: the /var/tmp write-safety fixture for `git repo structure`.
- F3 duplicate verdicts — next: a `duplicate` receipt class is an operator decision (taxonomy change).
- F4 restorable quarantine — next: per-item origin records (trashinfo-style) and `mv --no-copy` staging are tool changes for the operator.

### Corrections (r12)

- "No census data yet (r1)" and "No gate tool yet (r2)" under Known gaps are stale: census tables exist from r1 (`census/round-1/census.tsv`) and verdict tools from r2 (`tools/souji-verify.sh`).
- "census tables land here from r1 onward" (knowledge/) is wrong: census tables land in `census/round-<N>/` (r2's evidence is in `tests/results/`).
- "each with a `## Gate` section" under lessons/ held for none of rounds 1–11 (`grep -c '^## Gate' corpus/lessons/round-{1..11}.md` → 0 each); `lessons/round-12.md` is the first to carry it.

### Corrections (r12 post-review, 2026-10-19)

- F4's `knowledge/quarantine-same-filesystem-rename.md` is HELD, not admitted (no committed
  fixture; its `/dev/shm` device relied on QUALITY Q15, withdrawn by Q16). F4 still holds an
  admitted entry (`knowledge/trash-spec-restorable-quarantine.md`).
- `QUALITY.md` now runs Q1–Q16 (Q16 withdraws Q15).
