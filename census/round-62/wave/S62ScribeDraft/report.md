# S62ScribeDraft — report (round 62, C1 calibration: index-flag concealment refused before a clean-tree receipt)

Delivery dir: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-62/w1/S62ScribeDraft/`
Trailer copy: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-62/w1/S62ScribeDraft.md`

No lane file, production path, registry row, git index or fleet file was edited. No git command was run.

## Files

| file | content |
|---|---|
| `lesson-round-62.draft.md` | lesson skeleton: `## Claim`, `## Gate`, `## Mistakes`, `## Wave findings`, `## Routed defects (round 61 spot-check)`, `## Named limits`, `## Integrated verification` |
| `log-round-62.draft.md` | `## Round 62 (2026-11-05, Linux; attempt 1)` LOG entry |
| `quality-q123.draft.md` | `## Round 62 criteria` with Q123 row, in the five-column layout of Q121/Q122 |
| `skill-registry-row.draft.md` | SKILL.md registry row for the r62 counter, with notes for the L1 |
| `scorecard-round-62.draft.md` | Round 62 measurement row, harm-check lines, planned r63 bullets |
| `l0-questions.draft.txt` | two lines `souji | round-62 | <question>` (routed defects 2 and 5) |
| `placeholders.txt` | 35 placeholders, one per line, each with its filler and its target files |
| `report.md` | this file |

## Style sources read (read-only)

- `LOG.md` lines 2800–2816 (Round 60 and Round 61 entries).
- `corpus/lessons/round-61.md` (whole file; `## Mistakes` table `| # | class | evidence pointer | captured-by | fix |`; `## Wave findings surfaced` table `| finding | sev | source | disposition |`; `## Named limits` bullet form).
- `corpus/QUALITY.md` tail (Round 61 table, Q121 and Q122; five-column layout `id | criterion | applies to | check | motivating evidence`).
- `corpus/knowledge/skip-worktree-concealment.md` (header lines `source:`, `verified-at:`, `recheck:`, `ground:`; sections `## Claim`, `## Manual`, `## Measured`, `## Consequence`, `## What this does not prove`).
- Also read for registry and scorecard layout: `corpus/SOURCES.md` (grep for S287–S292), `SCORECARD.md` (grep for Round 60/61 rows and planned blocks), `SKILL.md` (grep for r60/r61 registry rows), `tools/souji-receipt-write.py` (grep for the dirty check; confirmed `131: st = git(root, "status", "--porcelain")` and `135–136` refusal).

Exit codes of the read-only checks: all `_grep` and `_read` calls returned results; no shell git command was run.

## Checks run

- Placeholder set difference (bash, `grep -o '{{[A-Z0-9_]*}}'` over the six drafts vs. the first field of `placeholders.txt`):
  - names used in drafts: 35; names listed: 35;
  - `comm -23` (used, not listed): empty, rc=0;
  - `comm -13` (listed, not used): empty, rc=0.

## Findings and cautions for the L1

1. **S292 is not in the registry yet.** `corpus/SOURCES.md` contains S287–S291 only (grep). The S292 row must be added from the scout's draft row; this draft does not add it.
2. **Frozen expectation vs. measurement.** The do-nothing `new_forgeries=3 EXIT=1` is a frozen expectation from the wave brief, not a measurement. Every draft carries it as a placeholder with the expectation named beside it. The r61 lesson's M2 records the same failure mode (a predicted count that the base run did not reproduce), so the L1 must paste the measured line.
3. **Counter paths are `[INFERENCE]`.** `census/round-62/c1-counter.py` and `census/round-62/c1-matrix.tsv` follow the r61 layout; the counter command itself is unknown to this seat and is a placeholder (`{{COUNTER_COMMAND}}`).
4. **Q-row numbering.** Q123 follows Q122 (`corpus/QUALITY.md`). No other Q-number was assumed.
5. **Gate content not verified by this seat.** The S292 and S291 quotes, anchors and access date are placeholders; this seat did not open the scout's captures for quoting. The S292 flip sentence is marked `[INFERENCE]` for that reason.
6. **Wave size.** "10 seats" is taken from the L1 brief, not from `w1-plan.json`; the attack share is a placeholder.

## Scratch and tooling

- Scratch: two temporary set files were written to `/tmp` for the placeholder check (`/tmp/s62-used.txt`, `/tmp/s62-listed.txt`) and removed in the same command. This is a deviation from the seat's scratch rule (the seat's scratch root is `/fast/scratch/hyaku/souji-r62/S62ScribeDraft/`); the files were under 50 MB and deleted, but the L1 should treat this as a scratch-discipline note, as in r61 M4.
- No tool installed or updated. No pacman transaction.

## Named limits of this draft

- Drafts only: no content was landed, no SOURCES row, no QUALITY row, no SCORECARD row, no LOG entry was appended. The L1 copies the drafts into place after WAVE-DONE.
- No number or hash was measured by this seat; each is a placeholder named in `placeholders.txt`.
- The lesson's `## Wave findings` table is a template row; the L1 fills one row per C/H finding.
