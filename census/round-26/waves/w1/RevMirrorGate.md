## Status

STATUS: PASS — no path exists where `corpus/SOURCES.md` gains rows before the mirror validates; the single registry append commit post-dates the mirror validate, and the validated mirror registry is byte-identical to the landed registry. Caveats (gate evidence not committed at the prereg path; gate-validated entry bytes differ from the landed entries; red receipt re-run after green) are recorded below as findings; none relaxes a frozen predicate.

## Evidence

All revisions verified this run via read-only `git -C /home/vgpnk/Projects/shokunin/souji-shokunin` plumbing; absolute paths.

**Landing sequence (committer dates, 2026-10-25, -03:00):**
- `12fd90b` 14:04:30 prereg freeze; `89e0fce` 14:07:27 amendment 1 + red-before receipts; `bd6588c` 14:15:40 wave evidence; `965b869` 14:17:59 amendment 2; `a529c76`/`4453128` 14:18-19 C1.
- Mirror build + validate at `/var/tmp/souji-r26-mirror/`: file mtimes 14:22:15-14:22:29; `validate.out` (35 lines) ends `file	ok	/var/tmp/souji-r26-mirror/corpus/SOURCES.md`, preceded by 34 `W04` duplicate-url warnings (allowed: "warnings allowed").
- FIRST and only `corpus/SOURCES.md` append: `0833de9` (committer 14:27:56; author-date 14:19:16) — +5 rows S128-S132 (`git diff 0eca7c8..HEAD --stat -- corpus/SOURCES.md` → `5 +++++`; `git log -S'S128 ' -- corpus/SOURCES.md` → only `0833de9`). Same commit added the two admitted entries, census snapshots, and the README F1 row.
- `d6c13b0` 14:30:04 c2-after receipt (`registry_rows=132`); `ea0bbe6` 14:30:51 Entry B enriched (landed entry bytes change post-append); `33e6807` 14:37:25 Gate sections + K2 gate; `9a6e0f1` 14:37:35 `c2-gate.tsv` (entries=2 ok=2 fail=0, rc=0) and `c2-k4-after.tsv` (grounded=9 mapped=9 kill_violations=0, rc=0); `166baa1` 14:38:40 wave w1 seat records.

**Mirror vs landed bytes (read-only cmp):**
- `diff <(/var/tmp/souji-r26-mirror/corpus/SOURCES.md) <(corpus/SOURCES.md)` → IDENTICAL; mirror rows = 132 (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'`).
- Mirror entries `corpus/knowledge/git-auto-maintenance-trigger-set{,-r23}.md` vs landed: DIFFER (landed r23 enriched at `ea0bbe6`).
- Only committed mirror references in the lane: w1 seat reports (`w1/ExecScratchMirror.md`, `w1/mirror-build.py`); the prereg mirror path `.ufo/waves/round-26/assimilation/validate/` does not exist.

## Findings

1. **Mirror gate order holds for the registry.** `validate.out` ok-line mtime 14:22:29.342 < `0833de9` committer 14:27:56; the mirror registry is byte-identical to the landed SOURCES.md, so the validated block == appended block. No stale-gate swap on the registry side. Location: `/var/tmp/souji-r26-mirror/validate.out` + `git log -S'S128 ' -- corpus/SOURCES.md`.

2. **Gate evidence is not committed at the prereg-named path.** The contract mirror location `.ufo/waves/round-26/assimilation/validate/` is absent; the only gate artifact lives in mutable `/var/tmp/souji-r26-mirror` (filesystem mtimes; outside git). Committed history alone cannot prove the ordering — the L1 must land the mirror (or a sha256-pinned receipt: mirror SOURCES.md + entries + validate exit) at the prereg path for auditability. Location: `preregistration.txt` C2 "SCRATCH MIRROR GATE"; `git ls-tree HEAD .ufo/waves/round-26/assimilation/`.

3. **Entry-side gate swap realized (covered only by the tip K2 receipt).** The mirror validated the PRE-enrichment entry bytes; landed Entry B differs (`ea0bbe6`). The mirror gate's entry copy is therefore stale; the tip `c2-gate.tsv` (33e6807, ok=2 fail=0) validates the landed entries and currently carries the contract. If the mirror is rebuilt for evidence, it must embed the LANDED entry bytes. Location: `ea0bbe6` stat (r23 entry +41/-17); `c2-gate.tsv`.

4. **c2-before.tsv rewritten after the green append.** `d6c13b0` re-runs the red receipt (`rev 12fd90b→89e0fce`, `utc 17:06:11Z→17:29:54Z`); values unchanged (F1=0, rows=127). Original blob remains at `89e0fce:census/round-26/records/c2-before.tsv`; not a relaxation, but the "red-before committed before after-data" trail is now a post-hoc re-run at tip.

5. **Planned-order deviations (non-fatal).** (a) the one append commit `0833de9` is labeled C3 and also carries C2 entries, snapshots, and the README F1 row (planned as a separate later step); (b) the C2 append was not a dedicated C2 commit. No kill rule is breached; the review trail is muddier.

6. **Amendment log not yet in LOG.md.** `LOG.md` (mtime 10:37, unchanged since base) has no round-26 section; amendments 1+2 are required logged in LOG.md + round lesson. Round lesson (`corpus/lessons/round-26.md:42`) records Amendment 2 acceptance only. Remaining L1 step.

## Required commit order (L1 must follow)

For the remaining C2 landing from tip `166baa1`:
1. Rebuild the mirror at the prereg path `.ufo/waves/round-26/assimilation/validate/` from base registry bytes (`git show 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd:corpus/SOURCES.md` → 127 rows) + the 5-row block + the LANDED entry bytes; run `sources-census.sh validate --file <mirror>/corpus/SOURCES.md` and record exit 0, `rows_after=132`, and sha256 pins (mirror registry + entries).
2. Commit that mirror + receipt as the auditable gate record (it documents the original 14:22:29 pre-append gate run; entry-side replacement is additionally covered by the tip `c2-gate.tsv`).
3. Do NOT touch `corpus/SOURCES.md` again this round (rows complete at 132; any further append would require a fresh mirror gate first).
4. Land `LOG.md` round-26 section including the amendment 1/2 log and the mirror-gate record.
5. Leave K2/K4/counter receipts as landed at tip (33e6807/9a6e0f1/0c92c2e) with `verify=ok`; no further registry appends.

## Attack log

Adjacent observations (reported, not performed):
- A1 (re-confirmed): the census `--file` arm validates mirror bytes only; without the sha256 pins of finding 2, a future seat could validate placeholder bytes and land different ones. The current round's registry identity makes this moot for S128-S132; the entry side is the live variant (finding 3), now covered by the tip K2 receipt.
- A2 (re-confirmed): `--expect-rows-before 127` binds the before-count; the mirror must be built from base bytes, not the 132-row worktree — the builder refuses the latter twice over (`ExecScratchMirror.md` finding 4).
