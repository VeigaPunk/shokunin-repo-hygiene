# RevCensusSchema — append block vs SOURCES-CONTRACT-v1

## Status

STATUS: PASS — all five planned rows S128–S132 conform to the contract v1 column definitions on every enumerated check (kind enum, tier A/B/C, status enum, opened ISO, recheck cadence, used-by format/existence, 11 columns, no pipes, unique next-free ids, no URL+scope duplicates). Two non-schema observations flagged for L1 (findings 3–4).

## Evidence

Contract read (frozen): `/home/vgpnk/Projects/shokunin/CORPUS.md:86-108` (v1 carried in full from `/.ufo/waves/kaika/SOURCES-CONTRACT-v1.md:19-41`).
Column rules applied:
- `kind` enum (CORPUS.md:91-92): `spec · docs · paper · code · tool · dataset · talk · book · community · own-work`
- `tier` (CORPUS.md:93-97): A/B/C letters only; `community` never A
- `status` (CORPUS.md:103-104): `queued | mined | rejected`
- `opened` / `recheck` (CORPUS.md:105-106): ISO date; recheck ISO date or cadence `90d`, `180d`, `on-release`
- `used-by` (CORPUS.md:107-108): repo-relative paths, comma-separated, or `—`
- no `|` inside any cell (CORPUS.md:89); 11 columns => NF=13

Checks run (lane at tip `166baa18f808071bc385187691713044a26bd663`, base `0eca7c8` resolved; clean tree — `git status --porcelain` empty for all five files):
1. Planned block (`sources-append-block.md` markers) vs landed registry (`corpus/SOURCES.md:149-153`): per-id byte compare → `S128 IDENTICAL S129 IDENTICAL S130 IDENTICAL S131 IDENTICAL S132 IDENTICAL` (5/5).
2. Field counts: every row `NF=13`; escaped-pipe scan `0`; duplicate ids within marked block `0`.
3. Vocab matrix (awk): per row `kind=ok tier=ok status=ok opened=ok recheck=ok`.
   - S128 docs/A, S129 code/A, S130 code/A, S131 own-work/A, S132 own-work/A — all in enum, no tier inflation (no community row).
   - status `mined` ×5; opened `2026-10-25` ×5 (ISO); recheck `on-release` ×3, `90d` ×2 (contract cadences).
4. used-by existence: `corpus/knowledge/git-auto-maintenance-trigger-set.md` and `...-triggerger-set-r23.md` both exist; every planned cell's path resolves.
5. E04 URL+scope: for the three URLs (`git-fetch`, `builtin/fetch.c`, `builtin/pull.c`) the only registry hits are rows S128/S129/S130 themselves (no pre-existing duplicate).
6. Citation matrix: entry A front matter cites S128/S129/S130; entry B cites S131/S129/S130/S128/S132 — matches used-by cells exactly (S128–S130 both entries; S131/S132 entry B only).

## Findings

1. **All five planned cells pass every schema check** (S128: docs/A/mined/2026-10-25/on-release/both-entries; S129: code/A/.../on-release/both; S130: code/A/.../on-release/both; S131: own-work/A/.../90d/entry B; S132: own-work/A/.../90d/entry B). 11 columns each, no literal/escaped `|`, ids S128–S132 unique and next-free after S127, registry order matches frozen renumber map (S109→S128, S110→S129, S111→S130, S123→S131, S131→S132).
2. **Planned = landed byte-identically** (evidence 1): reviewing the block reviews the deployed state; no drift between draft and commit.
3. **Observation (L1 decision, not a violation):** entry A body line 45 carries a literal `(S131)` — `the sibling entry `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md` (S131), not here.` Planned S131 `used-by` lists entry B only (entry A's front matter cites S128/S129/S130, not S131). If a literal id mention in an admitted entry counts as "citing the row" (prereg: `used-by = exactly the admitted entries citing it`), S131's cell under-counts by one; otherwise it is exact. Matches `ExecRenumberMap.md` F6.
4. **Observation (no validator failure):** entry A's S129 source line cites `https://github.com/git/git/tree/v2.56.0/builtin` while row S129's source URL is `.../blob/v2.56.0/builtin/fetch.c` (also noted in `ExecRenumberMap.md` F8). Row cell is unaffected.
5. **Editorial note:** the append file's `## Staged rows (verbatim)` section reproduces a second literal `| S131 |` row (staged S123→S131); automated consumers must parse only the `<!-- BEGIN/END S128-S132 APPEND -->` markers (the mirror run correctly parsed 5 rows).

## Attack log

None — review seat; no predicate/target/case-set amendment proposed.
