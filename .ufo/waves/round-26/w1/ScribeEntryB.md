# ScribeEntryB — entry B draft (git-auto-maintenance-trigger-set-r23)

## Status
STATUS: PASS — entry B draft written at `.ufo/waves/round-26/w1/entry-git-auto-maintenance-trigger-set-r23.md` (111 lines); all four measured claims re-grounded from campaign bytes whose sha256 match the S131/S132 registry literals; every citation re-pointed to lane ids S128-S132; the unadmitted file name appears 0 times; the draft's Gate passes `souji-gate-check.py` (entries=1 ok=1 fail=0, exit 0).

## Evidence

Contract and revisions (read-only):
- `cat .ufo/waves/round-26/preregistration.txt` — C2 admit set: Entry B = `git-auto-maintenance-trigger-set-r23.md`, staged rows S123/S110/S111/S109, mapping S109→S128, S110→S129, S111→S130, S123→S131, S131→S132.
- `cat .ufo/waves/round-26/preregistration-amendment-1.txt` — K4 literal corrected at base; no predicate, case set or axis changed.
- `git rev-parse HEAD` → `d6c13b0f00066cbb342fdc50167849a5f1c726e5` (head moved during the run: 4453128 → d6c13b0 by sibling seats).
- `git rev-parse 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd` → base as named. `git log --oneline -1 89e0fce` → `round-26: prereg amendment 1 ... + red-before receipts`.
- Host: `git --version` → `git version 2.56.0`; `python3 -V` → `Python 3.14.8`. All lane Python run as `python3 -B`.

Campaign evidence re-grounded (read-only, under `/home/vgpnk/Projects/shokuknow/`):
- `sha256sum fixtures/r23-trigger-prune.sh evidence/r23-trigger-prune.out evidence/r23-worktree-census.out` →
  `11c136aa71066733d50d226d344df9125401780aa81836f8ca9ca68a9997e65a` / `510722c11a97f6bca8f93e49b8a279f1f109d0222e40f675d001058768e069b4` / `1ac71c4f7199a134c204b45f339aadfc7e90c84b2d640cbed181b3577b9392fd`. These equal the S131/S132 `sha256 11c136aa… / 510722c1… / 1ac71c4f…` cells in `corpus/SOURCES.md`.
- `cat evidence/r23-trigger-prune.out` (lines 2-8): `fetch before=2 after=1`, `fetch-auto-off 2/2`, `pull 2/1`, `merge 2/1`, `rebase 2/1`, `locked 2/2`, `fresh 2/2`, every `verdict=PASS`, `SUMMARY verdict=PASS`.
- `cat evidence/r23-worktree-census.out` (lines 8-14, 16-19, 21-25): `5` registrations, every row `locked=no`, dry-run at `3.months.ago`, `--expire=now` and `--expire=never` reports `none prunable`; post-check count still `5`; campaign repo count `1`.
- Fixture mechanism lines: `125` skips the age step only for `fresh`; `126` `touch -d '4 months ago' .../index`; `129` `worktree lock --reason r23-trigger`; `141` `-c maintenance.auto=false`; `149` comment "A real, non-fast-forward merge so the merge actually updates HEAD"; `168` comment quoted in the entry; `193-199` the seven `run_case` expectations. `grep -c receipt fixture` → `0`; `wc -l` → `206`.

Lane registry state (working tree, other seats' append already present):
- `grep -c '^| S' corpus/SOURCES.md` → `132`; rows S128/S129/S130/S131/S132 exist with `used-by` containing `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md` on all five.
- Row cadences used in front matter: S128/S129/S130 `on-release`, S131/S132 `90d`.

Draft gate verification (read-only, writes nothing):
- `python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries .ufo/waves/round-26/w1/entry-git-auto-maintenance-trigger-set-r23.md --snapshot-dir census/round-26/sources --slice census/round-26/records/empty-slice --slice-verdicts census/round-26/records/empty-verdicts` → `entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=0`, exit 0.
- Every body quote re-checked contiguous against squashed bytes: `call sites only — whether each prunes was not fixture-run` (10 words, `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md`); `receipt-gated removal of stale, duplicate, and already-preserved artifacts` (8, `PROVINCE.md:3`); `Git deletes without a receipt` (5, `SKILL.md:95`); `repository maintenance if needed. This is enabled by default.` (9, `census/round-26/sources/git-fetch.1.txt` lines 3194-3196, `§ OPTIONS` heading at line 2995); `Registration whose index is NOT aged: the 3.months.ago expiry protects` (10, campaign `fixtures/r23-trigger-prune.sh:168`).
- `grep -c 'count-objects-garbage-semantics' <draft>` → `0`; `grep -c '|' <draft>` → `0`.

## Findings

1. **Draft delivered.** `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/entry-git-auto-maintenance-trigger-set-r23.md`. Front matter cites S131 (fixture), S129 (builtin call sites), S130 (`pull.c:392`), S128 (git-fetch docs), S132 (census); `verified-at: 2026-10-25` with the three sha256 literals; `recheck: 90d` + the campaign re-run command; `ground: F1` verbatim from the staged package. Body keeps the four measured claims and all five NOT-establish bullets.
2. **Staged-S131 citation re-pointed.** Both places that named a second knowledge file as the census source (NOT-establish bullet 4, and "Lane link and consequence") now cite lane row S132 and state the measured `5 registrations, 0 prunable, 0 locked`; the unadmitted filename does not occur in the draft (`grep -c` = 0).
3. **Claim re-grounding locations.** (a) prune 2→1: `evidence/r23-trigger-prune.out:2-6`; (b) no receipt: `PROVINCE.md:3` + § Owns "only with a receipt", `SKILL.md:95`, and 0 `receipt` matches in the fixture; (c) off-switches: fixture `:129` and `:141` plus evidence `:3` and `:7`; (d) expiry control: fixture `:125` and `:168` plus evidence `:8`.
4. **Staged locator corrected.** The staged package said `PROVINCE.md` § Refuses makes removal receipt-gated. The bytes put receipt gating in the domain line (`PROVINCE.md:3`) and in § Owns ("Lane-repo hygiene surfaces, per-lane and only with a receipt"); § Refuses is the refusal list and does not carry that sentence. The draft now cites the two actual locations instead of § Refuses.
5. **Staged quantifier corrected.** "five trigger commands ... of which four reach the prune path" is loose — the five builtins are fetch, merge, rebase, am, commit (S129), while the four measured pruners are fetch, merge, rebase and pull, with pull inheriting fetch (S130). The draft states both sets separately.
6. **Quote-hygiene correction.** The fresh-control comment is a two-line `#` comment; squashing keeps the `#`, so a cross-line quote of it is not contiguous (`...spared the # registration...`). The draft uses the single-line verbatim span at fixture `:168` (10 words) and paraphrases lines 171-172 without quoting. Relevant to any other seat quoting shell comments.
7. **Integration gap observed (not mine to fix).** `corpus/knowledge/git-auto-maintenance-trigger-set.md` (14:20) and `...-r23.md` (14:21) are pre-Gate copies: `grep -c '^## Gate'` → 0 on both, while the w1 drafts (entry A 14:30, entry B this file) each carry one. C2's K2 `entries=2 ok=2` therefore cannot pass until the L1 copy lands both drafts. Also absent at this revision: `census/round-26/records/c2-gate.tsv`, `c2-k4-after.tsv` (present: c1/c2/c3 before/after, c2-k4-base, c3-control, empty-slice/empty-verdicts).
8. **Tree-hygiene observation.** Untracked `tools/__pycache__/` and `tests/fixtures/__pycache__/` exist in the lane from other seats' runs. Not created by this seat (only `python3 -B` was used) and not deleted (read-only seat).

## Out of scope / not touched
No registry append, README, SCORECARD, entry A, mirror, receipts, `git add/commit/push/stash/checkout/reset`, no `jj` mutation, no `rm`/`mv`, no signals. `/home/vgpnk/Projects/shokuknow` opened read-only. No tool install or upgrade. This seat created no scratch directory (no `/var/tmp/souji-r26-ScribeEntryB/` exists); other seats' `/var/tmp/souji-r26-*` dirs were left untouched.

## Attack log
None — this is a drafting seat, not an attack seat; no counter, predicate or case-set defect was raised. Limits: the fixture was not re-executed (prereg admits it as campaign own-work); the result stands for one host on git 2.56.0 and the census is a 2026-10-23 point-in-time read.
