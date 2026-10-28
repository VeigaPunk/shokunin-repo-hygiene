# R41w2critic07 — falsification of the L1's process (round 41, wave 2)

Seat: R41w2critic07 (role critic, leaf, read-only). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. Tip checked: 1d41c13574db80fdd9a4bde490b712da7ce2a85f (= origin/master, `jj-lane.sh state` → `ahead=0 behind=0`).
Tools installed: none. Lane writes: none (`git status --short` empty after every counter run). Receipts copied to `.ufo/waves/round-41/w2/R41w2critic07/receipts/`; own scratch `/fast/scratch/hyaku/souji-r41/R41w2critic07` deleted.

## Verdict

**PASS with findings. No landed claim is falsified and no axis is harmed by the process.**
- Calibration (C1): the frozen `c1-counter.py` re-run at the final tip reproduces the three CORRECTION values exactly.
- Operability (C2): the frozen `c2-counter.py` re-run at the final tip reproduces `SUMMARY cases=21 pass=21 fail=0 … real=ok retro=red`. The real-lane run cannot witness the dispatch clause (F4) and the retro red is grammar-only (F5); both are named limits, not failures.
- Coverage (C3): re-run at the final tip reproduces `SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10`.
- R1: re-run at the final tip reproduces `SUMMARY mutants=11 killed=11 survived=0 pristine=ok regress=8/8 new_killed=3/3 old_fixtures_killed_new=0 prior=6/6`.
- Selection: L1 chose the smallest all-target candidate in each family (recomputed below).
- Open items the L1 must close before its report lands: F1 (end census receipt missing), F3 (commit message mislabel), F6 (L1 scratch still present; L1 still running at check time).

## Commands actually run (all read-only against the lane; outputs quoted)

1. `git cat-file`/`git rev-parse` of the 13 frozen paths at 6682b98 (instruments), e2a7431 (freeze), HEAD. Result: every counter, population, control, tool and `score-candidate.sh` blob identical at all three revs (`c1-counter.py` c89bc1a7…, `c2-counter.py` 17ee2fd2…, `c3-counter.py` 6df2642f…, `r1-counter.py` 655dfa88…, `tools/souji-worktree-drift.py` fd72b2bb…, `records/census-before.txt` 3aae7265…). Preregistration and the four control files exist only from e2a7431 (blob cbacc776…, same at HEAD).
2. `sha256sum` of the working files against digests written in the prereg: c1-counter 8860dc7a…, c1-items 2d2a548e…, c2-counter 85ffe263…, c2-cases 4854335a…, c3-counter 9ef99e8f…, c3-sites be363c0d…, r1-counter 8352eed4…, tools/souji-worktree-drift.py b2a603cf…. All eight match the prereg text.
3. `git diff --stat e2a7431 HEAD -- <all frozen paths>` → empty (no frozen file changed after freeze).
4. `git diff --stat 7eebc18 HEAD` → 32 files; the only pre-existing paths touched are `corpus/SOURCES.md` (append-only: S258 row line 212 and one Round-41 bullet) and `tools/souji-worktree-drift.py` (e9dc38d, pre-freeze). Round-40 lesson and round-40 census untouched.
5. Landing chain (`git show --name-status`, author/committer times via `git log --date=iso-strict`):
   - e9dc38d instruments 18:53:47 (counters, populations, drift-tool TOTAL fix)
   - 6682b98 18:54:12 (c1-counter `--scratch`, 1 line)
   - e2a7431 freeze 18:55:17 (prereg, controls)
   - a1144120 C3 fixture (committer 20:07:59)
   - 97eeb01 R1 fixture (20:08:01)
   - 119c26fa C2 tool (20:10:54)
   - 31e4d3e C1 lesson + S258 + snapshots + c2/c3/r1 receipts + shim-audit (20:11:43)
   - 1d41c13 c1 receipt (20:13:41), last commit.
6. `jj --ignore-working-copy op log -n 200` (read-only). Every op since 18:55:17 is `commit` / `track paths` / `snapshot working copy` / `point bookmark master to commit` / `push bookmark master to git remote origin`, with `snapshot.auto-track="none()"` and `user.name=souji-shokunin`. This is the exact sequence `cmd_commit` and `cmd_push` in `scripts/hyaku/jj-lane.sh` issue (lines 658–702, 714, 824). No wave-seat git or jj mutation appears; `git reflog` shows only `export from jj`.
7. `git ls-remote origin master` → `1d41c13574db80fdd9a4bde490b712da7ce2a85f refs/heads/master` (equals HEAD). `bash scripts/hyaku/jj-lane.sh state …/souji-shokunin` → `state branch=master local=1d41c13… remote=1d41c13… ahead=0 behind=0 … tracked=0 untracked=0`, exit 0.
8. Candidate byte recount: `wc -c` on every `w1/R41executor*/` candidate file, and `sha256sum`, compared with the byte/sha claims in each executor report (`grep -o`). All 15 byte counts and all 15 sha claims match the disk.
9. Selection (all-target from `L1/scores.txt`, copied to `receipts/l1-scores-copy.txt`; every row shows killed=19/survived=0 for C3, pass=21/fail=0 for C2, killed=11/survived=0 for R1):
   - C3: 01=6859, 02=9714, 03=10166, **04=3725 (chosen, smallest)**, 05=13417, 06=11321.
   - C2: **07=9447 (chosen, smallest)**, 08=9558, 09=9561, 10=11178, 11=10460, 12=13231.
   - R1: **13=8226 (chosen, smallest)**, 14=10387, 15=9370.
   - Landed blob sha = candidate sha: `a1144120:tests/fixtures/r41-refusal-sites.py` = f32022e2… (04); `119c26fa:tools/souji-freeze-check.py` = 3c3e80ba… (07); `97eeb01e:tests/fixtures/r41-drift-record-order.py` = a2880a91… (13).
10. Shim audit check: `wc -l L1/shim/R41executor0{1..6}.log` → 21 each (one tool invocation per probe, matching `shim-audit.txt`).
11. Four frozen counters re-run at the final tip, scratch under my seat's scratch (deleted after copy), `python3 -B census/round-41/<c>-counter.py --root . --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f --scratch …`:
   - c1: `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1`, EXIT=0
   - c2: `SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=3c3e80baedd8`, EXIT=0
   - c3: `SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=f32022e28fe2`, EXIT=0
   - r1: `SUMMARY mutants=11 killed=11 survived=0 pristine=ok regress=8/8 new_killed=3/3 old_fixtures_killed_new=0 prior=6/6 cases=12 tool_sha=b2a603cf4247 fixture_sha=a2880a914106`, EXIT=0
   Receipts: `receipts/tip-c1.out` … `tip-r1.out`. `git status --short` empty afterwards.
12. Census end-state (frontier step), read-only per the script header: `bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → exit 0, 53 TSV lines (W04 warnings and `souji ok`). `diff` against `records/census-before.txt` with the lane path normalised: only the trailing `exit 0` line differs. Receipt: `receipts/validate-end.tsv`.
13. Freeze-check, read-only: `python3 -B tools/souji-freeze-check.py --root . --prereg census/round-41/preregistration.txt --rev 1d41c13…` → `SUMMARY claims=3 findings=0`, rc=0. Same tool with `--prereg census/round-40/preregistration.txt` → rc=1, 18 lines, all `FIELD-MISSING`. Receipts: `receipts/fc-r41-head.txt`, `receipts/fc-r40-head.txt`. (The first attempt with `--rev HEAD` was refused with `REFUSAL COULD-NOT-EVALUATE: --rev must be a full 40-hex commit id`, exit 2, which is correct behaviour.)
14. Claim-source spot check (S258): row opened 2026-10-28, tier A, status mined, recheck on-release, used-by `corpus/lessons/round-41.md` (exists). Snapshot `census/round-41/sources/git-v2.56.0-builtin-worktree.c` = 1541 lines, sha af2bd523… (matches row and `SHA256SUMS`; `sha256sum -c` → OK for both snapshots). Cited lines: :171–177 = `prune_worktree()`, :212 = `prune_worktrees()` start, :229 = `should_prune_worktree(the_repository, …)` call, :254–255 = `--expire` option, :259 = `expire = TIME_MAX`. The lesson's CORRECTION values match the counter: I1 `rows=2,v2.56.0=0`, I3 `before=6,after=3`, I4 `occurrences=0`.
15. Timing: `stat` of receipts vs landing times — `c3-after` 20:08:35 after a1144120 (20:07:59); `r1-after` 20:08:47 after 97eeb01 (20:08:01); `c2-after` 20:10:58 after 119c26f (20:10:54); `c1-after` 20:11:45 after 31e4d3e (20:11:43). Wave files: first is `w1-spec.json` 18:57:58; first dispatch `w1-dispatch.json` 18:58:04; no wave file dated before the freeze epoch (`find … | awk` empty).
16. Scratch inventory: `ls -la` and `du -sh` of `/fast/scratch/hyaku/souji-r41` and `/tmp` (see F6).
17. Executor reports grepped for `/tmp|install|pacman|sudo|git (commit|push|add|reset|checkout)|jj |frozen|amend|scratch`: no installs, no git/jj mutation, no frozen edits claimed; every seat reports its scratch removed (confirmed: no `R41executor*`, `R41critic*`, `R41scout*`, `R41reviewer0*` directories remain in the fast scratch root).

## Findings

**F1 — open process gap: the end census receipt is missing.** The prereg's frontier step says "Census command (start and end)" with start receipt `census/round-41/records/census-before.txt`. `census/round-41/records/` holds `c1-after.txt`, `c2-after.txt`, `c3-after.txt`, `r1-after.txt`, `census-before.txt`, `shim-audit.txt`; there is no end receipt. The end state is clean (command 12), so this is a missing record, not a failed check. Not a claim; L1 should land the end receipt as the last commit (report-lands-last).

**F2 — wording only: receipts name measurement revisions, the Target says "over the landed lane tip".** c1 measured 31e4d3e, c2 119c26f, c3 a1144120, r1 97eeb01; the final tip is 1d41c13. Command 11 re-runs all four at 1d41c13 and each SUMMARY matches its receipt exactly, so no value changes. L1 should state the tip equivalence (or cite the tip re-run) in the lesson.

**F3 — commit message accuracy (low).** Commit 1d41c13 is titled "measurement receipts for C1, C2, C3, R1" but its only path is `census/round-41/records/c1-after.txt`. The c2/c3/r1 receipts and `shim-audit.txt` landed inside 31e4d3e, whose title names only "C1 corrections lesson, S258 registry row and pinned snapshots, shim audit". Content is correct; the history is hard to read.

**F4 — named limit, C2 operability: the DISPATCH-BEFORE-FREEZE clause is unreachable in this lane for round 41.** `.gitignore` line 1 ignores `.ufo/waves/`; `jj-lane.sh` line 30 says `.ufo` is never committable; the tool's `dispatch_findings()` reads only `git log --diff-filter=A -- .ufo/waves/round-41/`, which is empty (`git ls-files .ufo/waves/round-41 | wc -l` → 0). So the real-lane `findings=0` cannot witness dispatch timing. Timing is evidenced only by file mtimes: `w1-dispatch.json` 18:58:04.98 and `w1.ready` 18:58:09.98, both after freeze e2a7431 (18:55:17). The clause is exercised only by history (60 tracked `*-dispatch.json`/`*.ready` under older rounds such as `.ufo/waves/round-13/w1-dispatch.json`) and by the synthetic case in `c2-cases.tsv` line 19 (`dispatch-before-freeze` → `C0:DISPATCH-BEFORE-FREEZE`), which passes. The lesson should say so. The C2 predicate as written is met.

**F5 — named limit, C2 retro: the red is grammar-only.** `census/round-40/preregistration.txt` has `## C1…` headings but no column-0 `Base:`/`Counter:`/`Population:`/`Control:`/`Target:`/`Kill:` key lines (`git show 1d41c13…:census/round-40/preregistration.txt | grep -n` shows only the three `## C` headers). So its 18 findings are all `FIELD-MISSING`, and no freeze-class finding (`FROZEN-EDITED`, `COUNTER-DIGEST`, `DISPATCH-BEFORE-FREEZE`, …) is exercised by a real input. "retro=red" is true as written but says less than it appears to; the freeze-class coverage rests on the 19 synthetic cases.

**F6 — scratch residue (L1 still running at check time; must be cleared before L1 yields).**
- `/fast/scratch/hyaku/souji-r41/L1/` 180 KB: `score_all.sh`, `scores.txt`, `shim/` (shim.py, per-candidate logs with 21 lines each), `wt255.c` (42566 B), `wt256.c` (44631 B).
- `/fast/scratch/hyaku/souji-r41/build/` 56 KB: `mk_w1.py` (28538 B, 18:57), `mk_w2.py` (27413 B, 20:13).
- `/fast/scratch/hyaku/souji-r41/base-tool.py` 19699 B (18:45).
- All w1 seat scratch directories are gone (verified). Other w2 seats' dirs present (not mine to list).
- `/tmp`: no landed artifact cites `/tmp` (grep of `corpus/lessons/round-41.md`, `census/round-41/records/*.txt`, the two fixtures, the tool, and the four counters). Name-colliding files `/tmp/c1_at_freeze.out`, `/tmp/c2_freeze.txt|json`, `/tmp/claims_freeze.md`, `/tmp/worktree.c`, `/tmp/git-worktree.{adoc,txt}`, `/tmp/r41-c1-counter.py` hold other rounds' content (`"counter": "round-48-c1"`, `"round-48-c2"`, `# Round 52 — frozen claims (kengaku…)`), and `/tmp/r41-c1-counter.py` sha bbabbfec… ≠ frozen 8860dc7a…. These are not round-41 evidence and no receipt uses them. Unattributed round-window items: `/tmp/map_hash_before|after` (17 B, 19:02/19:03), `/tmp/sources-round40-final.txt`, `sources-round40-end.txt`, `sources-I.txt` (4375 B each, 18:05–18:19), `/tmp/x` (a SOURCES.md copy, changing at 20:21). Top-level `/tmp` items modified since 17:30 total 28.4 MB (<50 MB).

**F7 — gitignored lane residue (no effect).** `census/round-41/__pycache__/c2-counter.cpython-314.pyc` (18:53), written by a non-`-B` import before freeze; ignored by `.gitignore` line 3; not committed.

**F8 — pre-freeze tool edit (within the rules; noted).** e9dc38d (18:53:47) changes `tools/souji-worktree-drift.py` (+11/−2, the TOTAL repair: every TOTAL row is checked, not only the last) 88 s before freeze (18:55:17). Prereg rule 1 pins the post-repair bytes (b2a603cf…) and says so. The R1 "routed-defect repair" therefore has an unmeasured tool half (pre-freeze, not a candidate) and a measured fixture half. Nothing is amended after freeze.

## Non-findings (checked, no deviation)
- No frozen file, control, prereg, or pinned tool changed after e2a7431 (command 3); all eight digests match the prereg (command 2).
- No amendment: the prereg blob is identical at freeze and tip (`cbacc776…`).
- Freeze precedes all wave files (command 15).
- Selection follows the rule: all 15 candidates reached target; the smallest in each family was chosen (command 9). Executors' reported bytes and shas match disk (command 8).
- Landings only through jj-lane.sh's command sequence; authorship `souji-shokunin <souji@shokunin.local>` matches `--as souji`; remote tip = local tip (command 6–7).
- Report-lands-last holds for the claim measurements: each receipt is dated after the commit it measures, and the last commit is the c1 receipt (command 15). F1 is the only missing piece.
- Scratch of w1 seats deleted; no tool installed by any w1 seat (command 17).
- SOURCES.md changes are append-only; no round-40 row or lesson changed.

## Recommended handling
- L1: land the end census receipt as the last commit (F1); cite the tip re-run or state the revision equivalence (F2); correct the 1d41c13 title or add a receipt-index line (F3); delete `/fast/scratch/hyaku/souji-r41/{L1,build,base-tool.py}` before yield (F6).
- Round lesson: name F4 (dispatch clause vacuous in lane because `.ufo/waves/` is ignored) and F5 (retro red is grammar-only) as limits, not as coverage.

## Receipts (seat directory)
`.ufo/waves/round-41/w2/R41w2critic07/receipts/`: `validate-end.tsv`/`.err`, `fc-r41-head.txt`/`.err`, `fc-r40-head.txt`/`.err`, `tip-c1.out`, `tip-c2.out`, `tip-c3.out`, `tip-r1.out`, `l1-scores-copy.txt`.
