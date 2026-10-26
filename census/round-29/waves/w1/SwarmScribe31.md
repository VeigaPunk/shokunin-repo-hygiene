# SwarmScribe31 — round-report skeleton for `.ufo/reports/round-29/souji.md`

## Status

STATUS: PASS — the skeleton is written at `.ufo/waves/round-29/w1/deliver-report-skeleton.md` with the six required sections in order (claims opening `## Work performed` as C1 calibration, C2 operability, C3 coverage), exactly one `^## SHONEN` heading with one line per SHONEN.md box, and the eight extras; every value I could measure at base is filled with its pointer and every unmeasured value (after-counts, commits, dead seats, verdicts) is a `<...>` placeholder.

## Evidence

All lane paths are under `/home/vgpnk/Projects/shokunin/souji-shokunin`; readings are read-only at lane HEAD `b8cb4b31ce80e2e3314b88e85d40ea9873180804` (branch `master`, branch ref equal to the round base `691dd29211c53d0ef94fa072394cb9c8a69fe92e` + 1 commit).

1. Contract read first: `census/round-29/records/preregistration.txt` (lines 5, 6, 8 raw). Frozen targets carried verbatim into the skeleton:
   - C1 `SUMMARY k1=0 k2=0 mismatches=0`, rc 0, at the C1 landing commit and again at the final tip; base `k1=6 k2=4 mismatches=10` (`controls.tsv`).
   - C2 `manifests=3 failed=0 uncovered=0 floor_violations=0` at landing, `manifests=4` at tip; base `failed=152 uncovered=14`; fixture case count rises from 6.
   - C3 `ground: F3` 0→2, SOURCES rows 139→143, coverage `grounded=15 mapped=15 dangling=0 mismatches=0`, gate `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`.
2. Report contract read: `/home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-29.md:99-125`. Quoted bytes used for the skeleton: line 118, section 4 — "one line per box of your SHONEN.md checklist" (9 words). Marker rule at line 122-123: a contentless report "counts as the round **failed**"; `Sources & frontier` and `Trend verdicts` are conformance items, not marker predicates — both are still present as full sections.
3. `SHONEN.md` holds four `- [~]` boxes (SKILL.md decision tables; end-to-end domain task; instructions executable; no cross-domain bleed), so the skeleton emits four `- [~]` lines with pointer slots and states that a checked box needs a named non-author verifier.
4. House style read: `/home/vgpnk/Projects/shokunin/.ufo/reports/round-28/souji.md` — claim-led `## Work performed` bullets, a commit→LOG.md table, bolded claim measurements with the counter and measured revision, census before/after lines, three trend verdicts, four SHONEN lines, trailing `**Stale-lane:**` line.
5. Wave shape measured from the dispatch, not assumed:
   `python3 -B -c "import json; p=json.load(open('w1-dispatch.json')); print(len(p['taskCall']['tasks']))"` → `68`;
   role counter → `{'executor': 21, 'scribe': 10, 'scout': 7, 'reviewer': 8, 'critic': 8, 'mutation-tester': 6, 'sentinel': 2, 'connector': 3, 'revenger': 1, 'simplifier': 2}`;
   `w1-spec.json` → `wave = souji-r29-w1`, `reportDir = .ufo/waves/round-29/w1`, `maxLanes = 100`.
6. Misroot sweep, read-only, this run: `git -C /home/vgpnk/Projects/shokunin status --porcelain=v1` → 22 entries, 18 ` M` (`.scratch/goal-20261025-hyaku-run7.md`, 16 `.ufo/state/*.report-baseline`, `.ufo/watchdog.log`) and 4 `??` (`.tower/`, `.ufo/reports/round-41/mado.md`, `.ufo/waves/round-30/`, `demo-cwd.txt`); rc 0. `demo-cwd.txt` is 30 bytes, content `/home/vgpnk/Projects/shokunin`. None names souji round 29; nothing copied, moved or classified-for-cleanup.
7. Inherited state: `git -C <lane> rev-parse HEAD` → `b8cb4b31…`; `git status --porcelain=v1 --untracked-files=all` → one line, ` M .ufo/waves/round-26/w1/ScribeGateDraft.md` ("2 insertions(+), 1 deletion(-)" — an inbound round-31 coordination note). `.ufo/waves/round-29/` before this wave held only this attempt's `make-spec.py`, `w1-spec.json`, `w1-dispatch.json`, `w1-run.err`, `w1.ready` (timestamps 20:20–20:21).
8. Skeleton self-check: heading sweep gives `## Work performed`, `## Landed changes`, `## Before → after measurements`, `## Sources & frontier`, `## Trend verdicts`, `## SHONEN`, `## Round shape, waves and seats`, `## Routed-defect disposition (six r28 closure defects)` — one SHONEN heading; four `- [~]` lines, zero `- [x]` lines, zero `- [ ]` lines; every table row now has the header's pipe count (6 for the five-column disposition table, 4 for the three-column changes table).

## Findings

1. **Wave still in flight, so five skeleton values cannot be filled.** `w1-results.json` does not exist beside the dispatch (`.ufo/waves/round-29/`), and of 68 seats only the 21 executor reports plus the delivery files were on disk (`w1/` listing, 47 entries). Dead seats, the "seats returned result payloads" count, and every after-measurement stay `<...>`. Location: `souji-shokunin/.ufo/waves/round-29/w1-results.json` (absent).
2. **Seat arithmetic is filled and consistent with the frozen sizing.** 68 seats; flash roles 44/68 (executor 21 + scribe 10 + simplifier 2 + critic 8 + revenger 1 + sentinel 2); attack roles 22/68 = 32%, above the §6 ≥25% share. Location: `.ufo/waves/round-29/w1-dispatch.json`.
3. **One inherited dirty tracked path needs an explicit landing decision.** `.ufo/waves/round-26/w1/ScribeGateDraft.md` is modified in the worktree and cannot be cleared by a read-only seat; the skeleton carries it as `<kept as-is / committed through the helper / restored from master:>` under inherited-state naming. Location: `souji-shokunin/.ufo/waves/round-26/w1/ScribeGateDraft.md`.
4. **Routed defect 3 has no claim behind it.** Defects 1, 2, 5 map to C2, C1-K2 and C1-K1; defects 4 and 6 map to lesson/QUALITY items; defect 3 (`.ufo/waves/` gitignored, so the landing gate's report check is a permanent rc 2) is not named in the preregistration, so the skeleton leaves its disposition cell `<not claimed this round / item>` and defers to `SwarmReviewer45.md`. Location: `corpus/lessons/round-28-verifier-spotcheck.md` Routed defects 3; `census/round-29/records/preregistration.txt` (no mention).
5. **The disposition table deliberately mixes measured and unmeasured cells.** Rows 1 and 2 carry the frozen post-state commands (`c2-counter` zeros; `k2=0` plus the `R29-CORRECTION ` anchors) but status stays a placeholder, so the table cannot be read as a closure claim before the L1 lands the evidence. Location: `.ufo/waves/round-29/w1/deliver-report-skeleton.md` disposition table.
6. **SHONEN.md's own pointers are round-21 era.** `SHONEN.md` boxes cite `LOG.md:362`, `census/round-21/…`, `S100-S103`; the skeleton therefore keeps the r28 habit of pointing each line at this round's evidence slot instead of re-asserting the checklist file's older pointers. Location: `souji-shokunin/SHONEN.md:5-13`.
7. **No `[x]` box is offered.** The marker rule allows `[x]` only with a named non-author verifier; no such verifier exists at draft time, so the skeleton ships four `[~]` lines. Location: `.ufo/prompts/souji-round-29.md:118-119`.
8. **Misroot context is not souji's to clean.** The 4 untracked fleet entries (`.tower/`, `.ufo/reports/round-41/mado.md`, `.ufo/waves/round-30/`, `demo-cwd.txt`) belong to the fleet and other lanes; the hard bound forbids action, so the skeleton records the sweep shape only, and the end-of-round recheck is a placeholder. Location: `/home/vgpnk/Projects/shokunin` (read-only).

## Deliveries

- `.ufo/waves/round-29/w1/deliver-report-skeleton.md` — fill-in report skeleton: six required sections in order, four SHONEN lines, round shape/seat mix at 68, Stale-lane line, tool-install line, misroot sweep, inherited-state naming, and the six-defect disposition table.

No tool installed or upgraded. Scratch: none created (all work was reads plus the two writes above). No `git add/commit/push/stash/checkout/reset`, no `jj`, no `rm`/`mv`, no signals, no `agent://all`.
