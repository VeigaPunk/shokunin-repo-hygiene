# SwarmCritic42 — round-28 C2 falsification review

## Status
STATUS: FAIL — the C2 claim, as currently drafted and per its own frozen enumerate, cannot pass its own gates today; two defects are intrinsic to the approach and require amendment or execution changes, not just re-running.

## Evidence

- Frozen preregistration `census/round-28/records/preregistration.txt` (read first): C2 counters = grounded F4 4→6; registry rows 135→138 (three POSIX rows; S119 row if appended not counted); gate ok=2; sources-census validate exit 0; coverage-agreement grounded/mapped=6/6 dangling=0 mismatches=0.
- `grep -cE '^ground: F4' corpus/knowledge/*.md` = 4 today (`origin-record-writer-r27.md`, `origin-record-mechanism-set-r33.md`, `quarantine-origin-record-fields-r24.md`, `quarantine-staging-no-copy-r23.md`), matching the "before" snapshot `census/round-28/records/c2-before.tsv` (grounded_f4=4 rows=135).
- `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` = 135; rows S212–S214 are NOT present yet (`grep -nE '^\| S(212|213|214)'` → empty).
- SOURCES.append.md (shokuknow merge package) numbers S212/S213/S214 as DIFFERENT sources: S212=round-13 fleet-prune probe, S213=HAL metadata, S214=Gitea v1.15.0 cheat sheet.
- Draft entries `.ufo/waves/round-28/w1/origin-record-exclusivity-r28.md` / `origin-record-durability-r28.md` carry `ground: F4`, `## Gate` with ≥1 ADMIT + ≥1 REJECT, and `opened: 2026-10-25`; snapshot pins match `w1/snapshots/*.html` sha256 (`57b77091…` open, `06671610…` rename, `5c2975ab…` fsync).
- Mirror gate run (snapshots placed at `census/round-28/sources/`): `entries=2 ok=0 fail=6`, including `check4-quote-absent-from-snapshot` (exclusivity gate line 10, durability gate line 7) and `check5-dangling-source: S212/S213/S214`.
- Quote byte-match: rename.html body contains `any file named by <i>new</i> shall be unaffected`; fsync.html body contains `<i>fsync</i>() call is recorded on the disk`. Gate-check squashes whitespace only — it does not strip HTML tags — so the drafted quotes `any file named by new shall be unaffected` and `all data up to the time of the fsync() call is recorded on the disk` do not appear verbatim in the squashed snapshot bodies.
- Current `census/round-28/sources/SHA256SUMS` lists only `git-fetch-zh-HANS-CN.html`; the three POSIX snapshots are not yet at the committed path.
- Coverage agreement at HEAD: `grounded=11 mapped=11 dangling=0 mismatches=0` (global totals; 6/6 literal does not match tool output semantics).

## Findings

1. **Gate failure today (falsifies C2 as drafted).** Mirror run with correct snapshot layout: `entries=2 ok=0`; two ADMIT quotes fail `check4-quote-absent-from-snapshot` because the snapshot HTML wraps quote words in `<i>…</i>` tags and the checker matches squashed *bytes*, not rendered text. Fixable (choose tag-free spans or strip markup), but it is a required change, not a re-run.
2. **S212–S214 rows do not exist yet; rows are not "opened this round" in the registry.** Access dates in drafts are 2026-10-25 and snapshots exist under `w1/snapshots/` with matching pins, but the lane's `corpus/SOURCES.md` has no S212–S214 rows, and the census snapshot dir lacks the three files. `check5-dangling-source` will keep firing until rows are appended.
3. **Numbering collision with the staged package.** Shokuknow `SOURCES.append.md` uses S212/S213/S214 for different sources (probe/HAL/Gitea). The lane renumbers S212=open(), S213=rename(), S214=fsync(). Same numbers, different identity across packages — provenance risk if any merge later conflates them.
4. **Exclusivity ground is partially already held.** S022 (FreeDesktop spec, admitted in trash-spec entry) already establishes `opening with O_EXCL`/atomic info creation; r33/S210 already admit `O_EXCL` + `g_rename`. The new exclusivity entry raises authority (POSIX.1-2024) but restates the same claim; durability (fsync) is genuinely new (`grep -rli fsync corpus/knowledge/` → only the `do_fsync` flag in r33). Counting both as +2 fresh ground overstates novelty.
5. **S119 disposition is entangled with the registry-row counter (attack).** Frozen counter literal is 135→138; if S119 is ADMITed a row S215 is appended and `grep -cE '^\| S[0-9]{3,}'` would return 139 — the parenthetical "S119 row, if appended, is not counted" cannot be honored by the enumerated command, which counts every S### row. Only REJECT keeps 138. The dispose branch is therefore not counter-independent.
6. **Coverage-agreement literal 6/6 does not match the tool.** Tool prints global `grounded=11 mapped=11` (13/13 after adding two entries); it has no F4 filter. The frozen numerator/denominator is not reproducible from the enumerated command.
7. **Census hygiene currently clean.** Malformed=0, duplicate ids none, enum violations none, missing used-by paths none (sources-census checks); coverage agreement rc=0. No axis harm observed so far.

## Attack log
- ATTACK (C2 counter fidelity): the frozen registry-row target 138 is incompatible with the ADMIT branch of its own S119 disposition (append S215 → 139). The "not counted" parenthetical is unenforceable by the frozen grep. Either disposition must be pinned to REJECT, or the counter literal must be amended (stricter-only), or the ADMIT outcome must be excluded by counting the append after the counter snapshot — none of which the frozen text permits.
- ATTACK (C2 enumerate reproducibility): `check4` quote matching against HTML bytes is too brittle; the drafts as written fail it. If the executor instead copy-pastes tag-free quote text, the proof is silently weakened unless snapshot bodies are also normalized/e.

## Verdicts (per assignment)
1. Two entries on F4 map: durability = new ground; exclusivity = restates already-held O_EXCL/rename ground at higher authority — partially held before.
2. S212–S214 genuinely opened this round: access-date/snapshot pins in place, but registry rows and census snapshots not yet present — claim not yet satisfied.
3. Reduction to row-counting: counters alone are line/row counts, but gate+coverage checks add substance; currently the substance gate FAILS on byte-level quote mismatch.
4. S119 disposition independent of counters: NO — ADMIT breaks the frozen 138 literal.
5. No axis harmed: census checks pass now; coverage agreement rc=0, no enum drift seen; run must complete at tip.
