# S65ConnectorOverlap — round 65 w1 seat report (read-only scan)

Seat: S65ConnectorOverlap (leaf, no subagent dispatch). Deliver directory: `.ufo/waves/round-65/w1/S65ConnectorOverlap/` (files: `sibling-overlap.md`, `shokuknow-merge.md`, `considerthese.md`, `polarity-sweep.md`). No lane, sibling, fleet, or state file was written. No mutating git or jj command was run. Scratch root `/fast/scratch/hyaku/souji-r65/S65ConnectorOverlap/` was created empty and removed before yield. Nothing was installed.

## Axes (named before work)

1. Overlap with souji's C1 visibility/env class (status flags, GIT_* routing). 2. Overlap with the r55 line-model defect. 3. Shokuknow merge theme fit. 4. Polarity/needle-presence exposure in sibling counters. 5. The considerthese/ fact.

## Findings

**1. Sibling overlap (sibling-overlap.md).** Explicit untracked-visibility flags (`--untracked-files=all`, `-uall`) appear in kaidoku, mori, and tabi code and match souji's V1 fix; these are the same mechanism, correct, no defect. Two sibling gates use a bare `git status --porcelain` with no explicit flag and are config-sensitive: kaidoku `tools/round-29/prefile-check.sh:22` and kumitate `scripts/round-gate.mjs:91`. Mori `mori-index-clean.sh` uses `--untracked-files=no` deliberately for its tracked-only scope. No `skip-worktree`, `assume-unchanged`, or `allow-dirty` hits in scanned code. Env routing: kaidoku `round-25/instrument-custody.py` drops all GIT_* (names GIT_OBJECT_DIRECTORY and GIT_ALTERNATE_OBJECT_DIRECTORIES that souji's prereg lists as unread); kotodama `check-claim-separability.py` lists the same redirects. Prior overlaps confirmed: kaidoku `tools/round-59/annotation-audit.py:116` and chousa `corpus/evidence/round50/stale-count-check.py` (26/37/69) use `splitlines` in the r55 class. Note: the chousa stale-count file sits under `corpus/evidence/`, not `tools/`; kumitate and tabi have no `tools/` directory, so their `scripts/` was searched instead.

**2. Shokuknow merge (shokuknow-merge.md).** Theme: `fleet-config-scope-resolved-r26` is the one adjacent row (config scope bears on `status.showUntrackedFiles`). Verdict: name it as adjacency only; do not adopt. Staleness: the report says 108 lane rows and first id S109; the lane now has 219 rows (tail S294–S296), so staged ids collide. Nothing was run in shokuknow.

**3. considerthese/ (considerthese.md).** `ls -d …/souji-shokunin/considerthese` → does not exist, exit **2**; `test -e` exit 1. Report line: `considerthese/ does not exist in the souji lane (ls exit 2).`

**4. Polarity sweep (polarity-sweep.md).** Needle-presence checks without a liveness anchor, named by path for their lanes: tsukuroi `tools/check-adjacency-table-r50.py:146–150`; chousa `tools/claims-audit.py` (98–101, 161–164, 183) and `claims-audit-v2.py` (115–118, 178–179, 200); chousa `tools/quarantine-check.py:57–58`; tabi round-62 counter family (`.ufo/waves/round-62/counters/`), the source of record for the r62 M5 / v21 false-green lesson. Caveat: the mapping of the lesson's "v21" to `c1-adjacency-host-v21.mjs` is inferred from the filename, not confirmed. These are source-based inferences; no sibling counter was run.

## Affected axes

- Souji C1 (V1/V2 visibility, P13 env refusal): context only; the sibling set shows the same mechanism elsewhere; no contradiction with the frozen claims.
- Souji C2 (live-marker): the polarity sweep confirms the class C2's live-marker rule targets.
- Lane docs/merge: no change.

## Risks / limits

- Grep was used over the listed paths only; `corpus/knowledge/` prose was not exhaustively classified.
- "Could false-green" is an inference from source for siblings; not demonstrated.
- The round-59 and round-50 line-model hits are not shown to produce a wrong number on real receipts.

## Verification to run (for main agent, once)

- `grep -c '^| S[0-9]\{3\} |' corpus/SOURCES.md` → 219 (already observed by this seat; re-check after integration if rows land).
- `test -e considerthese; echo $?` → 1 (already observed).
- No counter was run; no verification of C1/C2 was attempted by this seat.

## Install record

None. No tool was installed or upgraded.
