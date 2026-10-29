# R42w2reviewer03 — fact-check of the lesson's named limits, wave-1 outcome and routed-defect table

Seat: R42w2reviewer03 (reviewer, leaf, no subagents). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Lesson checked: `corpus/lessons/round-42.md` at tip `3105a63b23481fccf7df58e74d14a6681e0ea0c8`. Freeze `afe17f416eec04dcf3f480b580a8f928de61d19d`, base `bf618f6c5c09d302994871c94903abbea2deb60d`, landed C2 `133206705f32d785277c1fdf69abd4c73066ba7c`, landed C3 `5ad7046cc…` (full `5ad7046d44c3be81ffdb5b2b448cb95a6b03fc96`).

Scope: the lesson sections `## Named limits of the frozen instruments`, `## Wave 1 outcome` and the routed-defect table at the top. Wave-1 reports are under `census/round-42/waves/w1/`. Read-only: no lane, fleet, frozen or tracked file was written; no git or jj mutation; no tool installed or upgraded (none needed). Scratch `/fast/scratch/hyaku/souji-r42/R42w2reviewer03` was removed. Receipts are under `.ufo/waves/round-42/w2/R42w2reviewer03/receipts/`.

## Verdict

- **Named limits: substantially faithful.** Every limit traces to a wave-1 report and the counts check out (11 wrong triples, 65/65 register agreement, 70 → 68, 6/11 held-out, 31 self-test cases, 3/3 patches). Three wording overstatements and one unevidenced claim need fixing.
- **Wave-1 outcome: two claims are not faithful as written.** (a) "five of six C3 candidates scored the target" is a single-run reading that does not reproduce under host load. (b) "R42executor09 read `equiv_killed=1` in the L1's run" and its attribution to the `old_killed` leg are not evidenced in committed bytes, and the attribution is wrong. The six-C2 result, byte sizes, selection and landed hashes reproduce exactly.
- **Routed-defect table: four of five dispositions faithful.** Two pointers are wrong: the T2 receipt (`controls/c3-control.txt` does not contain T2) and the N1–N4 cross-reference (`see M42-4`, which is a C3 section).
- No finding here changes a frozen verdict. The landed C3 fixture is non-deterministic under load (details §4), which the lesson discloses only partly.

## 1. Commands run (exact) and what they showed

Setup and reads (read-only):

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -20          -> tip 3105a63; 1332067 (C2 landed), 5ad7046 (C3 landed)
git -C … rev-parse 1332067 5ad7046 HEAD                                       -> 133206705f32d785277c1fdf69abd4c73066ba7c / 5ad7046cc… ; HEAD 3105a63b23481fccf7df58e74d14a6681e0ea0c8
python3 -c '…json.load(w1-spec.json)…'                                         -> items 40 (wave souji-r42-w1)
wc -c tools/souji-freeze-check.py tests/fixtures/r42-drift-conditions.py       -> 18550 / 8741
sha256sum <the two landed files>                                              -> 9ddd596b98fb… / 03392c7d75da…
git -C … show 1332067:tools/souji-freeze-check.py | sha256sum                -> 9ddd596b98fb…, 18550 bytes
git -C … show 5ad7046:tests/fixtures/r42-drift-conditions.py | sha256sum     -> 03392c7d75da…, 8741 bytes
git -C … ls-files | grep 'round-42/w2'                                        -> (no output: no committed wave-2 evidence)
git -C … check-ignore: .gitignore:1 `.ufo/waves/`                              -> every `.ufo/waves/…` pointer is untracked
diff .ufo/waves/round-42/audit-candidates.py census/round-42/waves/audit-candidates.py -> IDENTICAL
```

Counters and audits at the tip (frozen counters, unmodified):

```
python3 -B tools/…  (audit) AUDIT c2 findings=0                               EXIT=0   (audit-candidates.py c2 tools/souji-freeze-check.py)
python3 -B audit-candidates.py c3 tests/fixtures/r42-drift-conditions.py --lane … --scratch …
    wrapper run rc=0 cases=13 fail=0 invocations=13
    AUDIT c3 findings=0                                                         EXIT=0
python3 -B tools/souji-freeze-check.py --selftest                              -> SELFTEST cases=31 pass=31 fail=0   EXIT=0
python3 -B census/round-42/c1-counter.py --root . --rev 3105a63…               -> SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0  EXIT=0
python3 -B census/round-42/r1-counter.py --root . --rev 3105a63…               -> SUMMARY findings=0 deleted=2 rows_added=0 stale=0  EXIT=1 (red by letter, as the lesson says)
python3 -B census/round-42/c3-counter.py --root . --rev 5ad7046… (tip re-run)   -> rc=0; SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13
                                                                                 (EQUIV B4 candidate=survived prior=r36-worktree-drift.py; not a SUMMARY leg)
```

Independent re-scoring of wave-1 candidates in my scratch clone (`bash census/round-42/score-candidate.sh <claim> <scratch> tools/souji-freeze-check.py=<cand>` or `tests/fixtures/r42-drift-conditions.py=<cand>`):

C2, six candidates (sha256 and byte counts match each seat report):

| candidate | bytes | sha256 (12) | SUMMARY (verbatim) | rc |
|---|---|---|---|---|
| executor01 | 19728 | f32b4eba4bbf | `SUMMARY cases=37 pass=37 fail=0 … selftest=ok patches=3/3 tool_sha=f32b4eba4bbf` | 0 |
| executor02 | 20753 | 3aa202014291 | `… selftest=ok patches=3/3 tool_sha=3aa202014291` | 0 |
| executor03 | 32697 | b15f0f69b55e | `… selftest=ok patches=3/3 tool_sha=b15f0f69b55e` | 0 |
| executor04 | 32767 | ed35b51f48dd | `… selftest=ok patches=3/3 tool_sha=ed35b51f48dd` | 0 |
| executor05 | 21509 | d97ab2e252db | `… selftest=ok patches=3/3 tool_sha=d97ab2e252db` | 0 |
| executor06 | 18550 | 9ddd596b98fb | `… selftest=ok patches=3/3 tool_sha=9ddd596b98fb` (run twice; the first batch was cut by a batch timeout) | 0 |

C3, five target-claimed candidates (plus executor09), run one at a time with `--root` = scratch clone; full output in `receipts/executor{07,08,10,11,12}-score.txt`:

| candidate | bytes | sha256 (12) | SUMMARY (verbatim) | rc | seat report said |
|---|---|---|---|---|---|
| executor07 | 10387 | 3a0ea605356a | `SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=15` | 0 | target |
| executor08 | 13098 | aca10eff0819 | `… prior=8/8 old_killed=2 equiv=6 equiv_killed=0 anchors=ok cases=14` (MUTANT G5, M1 killed by r36) | 1 | target |
| executor10 (landed bytes) | 8741 | 03392c7d75da | `… prior=8/8 old_killed=2 equiv=6 equiv_killed=0 anchors=ok cases=13` (MUTANT H1, H2 killed by r36) | 1 | target |
| executor11 | 14344 | 3e5232ed5eb2 | `… prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=14` | 0 | target |
| executor12 | 10477 | fcb89e398d96 | `… pristine=ok prior=7/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=14` | 1 | target |
| executor09 (3 runs) | 12042 | 9d6e81658019 | run 1: `… old_killed=0 … equiv_killed=2` (`EQUIV E9 candidate=KILLED`, second kill not captured by my `tail -3`); run 2: `… equiv_killed=0`; run 3: `… equiv_killed=0` | 1 (run 1) | `equiv_killed=0` (score-final.txt) |

Host load during the C3 batch: `/proc/loadavg` = `113.06 127.64 130.12` on 32 CPUs. Tip re-run at `111.33 126.78 129.82` before and `93.60 110.10 122.73` after: rc=0. Other fleet seats were running.

## 2. Named limits (`## Named limits…`, lesson lines 169–198)

| # | lesson claim (line) | source report line | faithful? |
|---|---|---|---|
| 1 | N-C1a: `R42critic01` built **11** substantively wrong triples the counter scores at target (174) | `census/round-42/waves/w1/R42critic01.md` rows k1,k2,k3,k4,k5,k6,k11,k12,k15,k16,k17 (lines 27–32, 37–43), each marked `yes` | **Yes** (count 11 exact) |
| 2 | N-C1a: "five-reader verification of the register (65/65 agree)" (176) | `R42scribe01.md:44`, `R42scribe02.md:47`, `R42scribe03.md:102`, `R42scribe04.md:47`, `R42scribe05.md:58` (each `agree=13 disagree=0`) | **Yes** (5×13=65) |
| 3 | N-C1a: "the **independent** re-derivation (0 disagreements)" (176) | `R42reviewer01.md:8`: "The first read of `census/round-42/c1-counter.py` … displayed the `derive()` body before I had written my implementation … It is not a pure blind derivation." `:6` heading "Independence disclosure". Count 0 disagreements is at `R42reviewer01.md` §7 | **Overstated.** Count is right; "independent" is not. The seat disclosed it read the counter's `derive()` first. |
| 4 | N-C1a: "the L1's instrument re-run at the landed revision (`records/c1-after.txt`)" (176) | `census/round-42/records/c1-after.txt`: `SUMMARY items=70 … class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0`, header says measured at `34e33a6` | **Yes**, with a minor point: the receipt is at `34e33a6`, not the landed tip. My re-run at `3105a63` gives the same SUMMARY (§1). |
| 5 | N-C1b: "70 → 68 in R42critic01 k4"; `e13d0c83…`, `9df0738c…` on line 69; `20261018` on line 184 (177–178) | `R42critic01.md:30` (k4 row, "verified: … 70, at candidate commit 68"); `:57` (N8) | **Yes** |
| 6 | N-C1c: `rewritten` blank-line sentinel defect (M42-3) (179) | `R42reviewer01.md:78` (F1); `R42critic01.md:61` (N12). Code: `census/round-42/c1-counter.py:180` (`base_lines = …split("\n")`), `:237–241` | **Yes** (code confirms the trailing-sentinel mechanism) |
| 7 | N-C1c: `new_mismatches` thresholds at `> 840`, docstring says `> 839` (179) | `R42reviewer01.md:80` (F2). Code `census/round-42/c1-counter.py:243`: `r[0] > len(base_lines)`, `len` = 840 (`:180`). Docstring `c1-counter.py:22` "beyond the BASE line count" | **Yes** (confirmed in code) |
| 8 | N-C1c: extra register rows not rejected; tilde and four-backtick fences not recognised; ASCII-exact marker; CRLF register false red; header content unread; prose line with marker is junk (179–180) | `R42reviewer01.md:82` (F3), `:84` (F4); `R42critic01.md:52` (N3), `:58` (N9), `:62` (N13), `:63` (N14), `:64` (N15) | **Yes** |
| 9 | (not in lesson) HTML-comment masking: a CORRECTION-DE line inside `<!-- … -->` counts as corrected (k2) | `R42critic01.md:28` (k2 row), `:51` (N2) | **Omitted.** A named limit of the same instrument. |
| 10 | (not in lesson) prose retraction unread: a sentence that retracts a correction passes (k1) | `R42critic01.md:27` (k1), `:50` (N1) | **Partly omitted.** The lesson's CORRECTION-SC line for SCORECARD:839 covers a different sentence. |
| 11 | N-C2a: K5 and K5b reach `cases=37 pass=37` with no grammar; held-out 6/11 each; K1 honest 37/37 and 11/11 (181) | `R42critic02.md:9` (item 1), `:21` (K1 row, 11/11), `:25`–`:26` (K5, K5b, held-out 6/11) | **Yes** |
| 12 | N-C2a: "The landed tool was audited (`.ufo/waves/round-42/audit-candidates.py` …)" (182) | My run `AUDIT c2 findings=0`. The cited path is **untracked** (`.gitignore:1` `.ufo/waves/`); the committed copy `census/round-42/waves/audit-candidates.py` is identical | **Content yes; pointer wrong.** Cite the committed path. |
| 13 | N-C2a: "… and by the **held-out audit in wave 2**" (182) | No committed wave-2 evidence (`git ls-files | grep round-42/w2` empty). The section header says "found in wave 1" | **Unevidenced.** Wave-2 reports were not committed when the lesson was written. |
| 14 | N-C2b: env-aware stub reaches `selftest=ok patches=3/3`; control B unconditional and does not test it; P1 only through `hashlib.sha256`; patch does not reach `-I`/`-E`/`-S`; children resolve `python3` via PATH (183–186) | `R42sentinel02.md:30` (row 1), `:35` (row 6, `hashlib.new` → 2/3), row 15 (PATH), Q105 | **Yes** |
| 15 | N-C2c: `dup-base-differs` requires FIRST occurrence (last-wins 36/37, K7); `population-symlink` POPULATION-EMPTY suppression (K8 36/37) (187) | `R42critic02.md` K7 and K8 rows (§1 table); `R42critic03.md:48` (D1) | **Yes** |
| 16 | N-C2c: "a malformed heading's effect on the open block, the dispatch check at depth and a missing `Round:` line are not exercised (`R42reviewer02` A1/A2/N1, `R42critic03` D1–D5)" (188) | `R42reviewer02.md:58` (N1, block boundary: correct). A1 (`:50`) and A2 (`:53`) are **ambiguous expectations** that ARE exercised by cases, not "not exercised". `R42critic03.md:50` (D2 depth), `:52` (D3 Round): correct. D1, D4, D5 are not "not exercised" items. | **Mis-cited.** Keep N1, D2, D3; drop A1/A2 and D1/D4/D5 from this sentence. |
| 17 | N-C2c: `run_tool` has no timeout handler (`R42sentinel02` row 17) (189) | `R42sentinel02.md:46` (row 17) | **Yes** |
| 18 | N-C2c: candidate writes caller cwd and absolute paths; hostile `GIT_DIR` reaches decoy (189) | `R42sentinel02.md` rows 8, 9, 18 (`:47`) | **Yes** |
| 19 | N-C3a: `R42critic04` K2 reads tool source for the 13 defects, survives the six equivalents, reaches target (190) | `R42critic04.md:16` (K2 row) | **Yes**, but **incomplete** (row 20) |
| 20 | (not in lesson) `R42critic06` A2 — a C3 byte-presence fixture reaches the **full** C3 Target with `equiv_killed=0`; critic06 calls it "Admission-changing defect: **one**" | `R42critic06.md:46` (A2 row), `:83` (§5 verdict) | **Omitted.** The most direct statement of the admission risk is missing. |
| 21 | (not in lesson) `R42critic05` K1 (basename-keyed dispatch) and K2 (sibling-bytes) reach the C3 target | `R42critic05.md:28`, `:29` | **Omitted.** |
| 22 | N-C3a: landed fixture passes the L1 audit: logging wrapper green, one invocation per case, no anchor, hash or tool read (191) | My run: `wrapper run rc=0 cases=13 fail=0 invocations=13`, `AUDIT c3 findings=0` | **Yes** (path pointer as row 12) |
| 23 | N-C3b: `killed()` reads stderr for a traceback; honest fixture forwarding stderr is a false red (K6) (192) | `R42critic04.md:20` (K6 row), `:4.2` | **Yes** |
| 24 | N-C3b: "the **`old_killed` leg** is timing-sensitive under load" (192) | `R42critic04.md:59` (§4.3: 3 of 8 runs), `R42critic05.md:38`, `:40`, `:41`; my re-scores: `old_killed=2` for executor08 and executor10 (§1) | **Yes** for the leg; see row 25 for the example |
| 25 | N-C3b: "`R42executor09`'s fixture read `equiv_killed=1` in the L1's run and `0` in the seat's" (192) | Seat: `census/round-42/waves/w1/R42executor09/score-final.txt` `equiv_killed=0` (**yes**). L1 run: **no committed receipt** (census/round-42/records holds only c1/c2/c3-after, gate, survey). My three re-runs: `equiv_killed=2`, `0`, `0` (§1). | **Mis-attributed and unevidenced.** `equiv_killed` is the candidate-kill leg on EQUIV mutants, not the `old_killed` leg. The flake is real (run 1 read 2 in my scratch), but the "1 in the L1's run" is not on disk. |
| 26 | N-C3b: `EQUIV` "not re-proven beyond counting (29 + 15 varied scenarios found no observable difference, `R42reviewer04`, `R42critic05`)" (193) | `R42reviewer04.md:15`, `:38`, `:47` (29 scenarios, no EQUIV observable, `{0: 10, 1: 4, 2: 15}`); `R42critic05.md` §4 (15 probes, `diffprobe2`) | **Faithful, but the wording understates.** `R42reviewer04` did re-prove equivalence over 29 scenarios; the honest limit is "not exhaustive". |
| 27 | (not in lesson) prior-clean leg flake: a prior fixture not clean on pristine turns `prior=7/8` (executor12) and EQUIV prior kills (`EQUIV B4 … prior=r36`) | My re-score: executor12 `prior=7/8` (§1); tip re-run `EQUIV B4 candidate=survived prior=r36-worktree-drift.py` (§1); `R42critic05.md:41` (same class) | **Omitted.** The lesson names only `old_killed`; the same load-dependence reaches `prior=8/8` and the EQUIV prior column. |
| 28 | N-H: `score-candidate.sh` accepted any destination (sentinel01 N9a–d); "The L1 closed the destination: allowlist; refuses symlinked destinations" (194–195) | `R42sentinel01.md` table rows F1–F4 (lines 19–22). Code `census/round-42/score-candidate.sh` lines 27–35 (allowlist, symlink refusal) | **Yes** for the destination |
| 29 | N-H: an unconfined hook/tool with an **origin push** is named as a threat; only the destination is said to be closed (194–195) | `R42sentinel01.md:23` (F5, push into the lane through origin, demonstrated). Code `score-candidate.sh:23` `git clone -q --shared "$LANE"` still sets origin = lane; no remote removal | **Open limit under-reported.** The lesson should say the origin push is still open. |
| 30 | N-H: counters leave entries under `--scratch` after KILL/TERM (195–196) | `R42sentinel01.md` F8 (§table) | **Yes** |
| 31 | N-adj (connector01): `freeze-check` name clash with chousa; FROZEN-EDITED compares blobs only (edit-then-restore passes; kaidoku `restored` arm); empty-pin family M31-2; tameshi no EQUIV (197–198) | `R42connector01.md` §2 table rows 1–4, §4 F1–F4, §1 item 8 (`restored` arm) | **Yes** |

## 3. Routed-defect table (lesson lines 12–17)

| routed defect | lesson disposition (line) | evidence | faithful? |
|---|---|---|---|
| R41-D-REJECT-REASON (12) | positive ground in `## Gate` | `census/round-42/…` not needed; the Gate text quotes `corpus/knowledge/fleet-prune-numerator-r35.md` line 6: "The fleet's live prune numerator is 27 registrations, 0 prunable (2026-10-28)" (verified by read) | **Yes** |
| R41-D-C3-CONDITION (13) | T2 is killed by `r40-drift-record-branches.py` and `r41-drift-record-order.py`; cites `census/round-42/controls/c3-control.txt` then `census/round-42/records/survey-prior.txt` | `survey-prior.txt`: `MUTANT T2 killed-by-prior-fixtures=r40-drift-record-branches.py,r41-drift-record-order.py` (**yes**). But `controls/c3-control.txt` has **no** T2 line (`grep -c T2` = 0); its MUTANT lines are the 13 population mutants and 6 EQUIV only | **Kill claim yes; first pointer wrong.** Cite `survey-prior.txt` only. |
| R41-D-C2-SELFTEST (14) | `--selftest` at landed bytes, 31 cases | My run: `SELFTEST cases=31 pass=31 fail=0`, EXIT=0 | **Yes** |
| R41-D-LG-DANGLING (15) | repointed, not exempted; `## Mistakes` M42-2 | `census/round-42/records/gate-both-modes.txt`: both modes `findings=0`; my r1 run `findings=0 deleted=2 rows_added=0 stale=0` EXIT=1 (red by letter) | **Yes** (byte equality with fleet originals is reviewer08's item; not checked here) |
| N1–N4 (C1 correction prose) (16) | "routed forward … see M42-4" | M42-4 (lesson line ~ 96–104) is about the C3 prior-fixture survey, not C1 prose. The routed item is the CORRECTION-SC line for SCORECARD:839 in `## Corrections` | **Wrong cross-reference.** Point to the CORRECTION-SC line 839. |
| N10, N11, M40-12 R39-D1/D2 (17) | routed forward; M40-12 = C3 mutant D4 | `census/round-42/c3-mutants.tsv` row D4 description "record decoded with backslashreplace instead of replace (M40-12)" | **Yes** |

## 4. Wave-1 outcome (`## Wave 1 outcome`, lesson lines 200–203)

| claim | evidence | faithful? |
|---|---|---|
| "Wave 1 (`census/round-42/waves/w1-spec.json`, 40 seats)" | My count: 40 items | **Yes** |
| "Six C2 candidates (`R42executor01`-`06`) all scored `cases=37 pass=37 … selftest=ok patches=3/3` **at the L1's scoring**" | Seat reports `census/round-42/waves/w1/R42executor01.md:21` and the others. My independent re-score: 6/6 at target (§1). **No committed L1 scoring receipt for any candidate** (`census/round-42/records/` holds only the landed c1/c2/c3-after, gate, survey) | **Numbers yes; "at the L1's scoring" unevidenced.** Say "seat scores; independently re-scored 6/6". |
| "five of six C3 candidates scored the target (`R42executor07`, `08`, `10`, `11`, `12`)" | Seat reports say target for 07, 08, 10, 11, 12 (`R42executor07.md:15` etc.). My single rescore (load ≈113): **07 ✓, 11 ✓; 08 ✗ (old_killed=2), 10 ✗ (old_killed=2), 12 ✗ (prior=7/8)**. Tip re-run of the landed bytes: ✓ once. | **Overstated.** Presented as a settled count; it is a one-run reading and not reproducible under load. The lesson must say so. |
| "`R42executor09` read `equiv_killed=1` in the L1's run" | No committed L1 receipt. My runs: `equiv_killed=2`, `0`, `0` (E9 KILLED in run 1) | **Unevidenced number; flake real.** |
| "Selection by the preregistered rule (all-target first, then smaller bytes), after the L1 audit" | C2: smallest of the six is 06 at 18550 (others 19728, 20753, 32697, 32767, 21509). C3: target set by seat reports is 07 (10387), 08 (13098), 10 (8741), 11 (14344), 12 (10477); smallest 10 at 8741. Audits: C2 `findings=0`; C3 wrapper green, 13 invocations for 13 cases (my runs) | **Yes**, on the seat-report readings. The C3 selection rests on a reading I could not reproduce for 10 under load (§1). |
| "C2 R42executor06 (18 550 bytes; `audit-candidates.py c2` findings 0)" | `wc -c` 18550; `git show 1332067:… | sha256sum` = `9ddd596b98fb…`; `AUDIT c2 findings=0` | **Yes** |
| "C3 R42executor10 (8 741 bytes; wrapper audit green, 13 invocations for 13 cases)" | `wc -c` 8741; `git show 5ad7046:…` = `03392c7d75da…`; my wrapper run `invocations=13 cases=13 rc=0` | **Yes** |
| "Landed at `133206705f32d785277c1fdf69abd4c73066ba7c` (C2) and `5ad7046cc…` (C3); measurements `records/c2-after.txt`, `c3-after.txt`" | `git rev-parse` confirms both; both receipts exist with EXIT=0 and target SUMMARY lines | **Yes** |

## 5. Overstatements and errors to fix (consolidated)

1. **C3 target count (Wave-1 outcome).** "Five of six C3 candidates scored the target" is a one-run reading that does not reproduce under host load (executor08, 10, 12 read red on re-score; the landed bytes read rc=1 once and rc=0 once). Restate as: seat scores 5/6; L1 run 5/6 (receipt not committed); independent re-score under load 2/5 (07, 11).
2. **executor09 attribution (N-C3b, line 192).** "`old_killed` leg … (executor09's fixture read `equiv_killed=1`)" puts an EQUIV-kill on the `old_killed` leg. Fix the leg name. The "1 in the L1's run" has no committed receipt; my reruns read 2, 0, 0.
3. **Landed C3 non-determinism not disclosed as such.** Identical bytes gave rc=1 (score under load) and rc=0 (tip re-run, load ~100). N-C3b should say the landed fixture's target is load-sensitive and cite the `old_killed` and prior-clean legs (executor12 `prior=7/8`), not only `old_killed`.
4. **"independent re-derivation" (N-C1a, line 176).** The seat read the counter's `derive()` before implementing it (`R42reviewer01.md:8`). Say "re-derivation (read-first, not blind)".
5. **"held-out audit in wave 2" (N-C2a, line 182).** No committed evidence; the section is described as wave-1 findings. Remove or cite a committed receipt.
6. **"at the L1's scoring" (Wave-1 outcome, line 202).** No committed L1 candidate score exists. Cite the seat receipts and the independent re-score.
7. **Origin push (N-H, lines 194–195).** Still open (`score-candidate.sh:23`, `R42sentinel01.md:23`). The lesson lists it as a threat and does not say it remains open.
8. **Pointer errors.** (a) T2 receipt `controls/c3-control.txt` (line 13) has no T2; cite `survey-prior.txt`. (b) N1–N4 routed item says `see M42-4` (line 16); the correct target is the CORRECTION-SC line for SCORECARD:839. (c) `.ufo/waves/round-42/audit-candidates.py` (lines 182, 191) is untracked; cite `census/round-42/waves/audit-candidates.py`.
9. **Mis-citation (N-C2c, line 188).** A1, A2 and D1, D4, D5 are not "not exercised" items; keep N1, D2, D3.
10. **Omissions.** (a) `R42critic06` A2 (byte-presence fixture reaches full C3 target; "admission-changing") and `R42critic05` K1/K2 are not named in N-C3a. (b) `R42critic01` N1 (prose retraction unread) and N2 (HTML comments not masked) are not in N-C1c. (c) prior-clean and EQUIV-prior flakes are not in N-C3b.

Adjacent, outside my sections but reached by the routed table (M42-4, lines ~96–104): "of the 17 G-class mutants … D3 and F2 … H3 and N1 … J5 … T2 … The 13 left survive all eight." Arithmetic: 17 − 5 = 12 (T2 outside the 17) or 17 − 6 = 11 (T2 inside); neither gives 13. Also "F1 … was killed by r36 in the L1's first survey run" has no committed receipt; `survey-prior.txt` shows `F1 killed-by-prior-fixtures=-`.

## 6. Verified as stated (no finding)

- All 11 wrong-triple counts, 65/65 register agreement, 70 → 68, 6/11 and 11/11 held-out, 31 self-test cases, 37 cases, 3/3 patches (§2 rows 1–2, 5, 11, 13 counts, 14, 22).
- All six C2 candidates reach `cases=37 pass=37 fail=0 … selftest=ok patches=3/3` on independent re-score (§1).
- Byte sizes 18550 and 8741; landed blobs equal the executor06 and executor10 bytes; landed commits exist.
- Selection rule outcome (C2 06, C3 10) on the seat-report target sets (§4).
- C1 counter at the tip: `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0`, EXIT 0.
- R1 red-by-letter (`deleted=2`, EXIT 1), as the routed row and the lesson say.

## 7. Limits of this check

- The C3 re-scores ran under host load ≈113 on 32 CPUs (other seats running). They show the flake exists; they do not give a quiet-host rate. The tip re-run is one sample.
- The executor01–05 C2 batch and the executor09 run 1 were read from tool output; full text is in this report, not a separate file. Files: `receipts/c3-tip-run1.txt`, `receipts/executor06-score.txt`, `receipts/executor{07,08,10,11,12}-score.txt`.
- The "L1's run" numbers in the lesson (executor09 `equiv_killed=1`, the six C2 scores "at the L1's scoring") were not reproducible from committed bytes; I did not have the L1's scratch output.
- I did not check reviewer08's byte-for-byte repoint claim (M42-2) or the S259 row (Gate section).

## 8. Tools

None installed or upgraded. Scratch removed. No lane or fleet tracked file written.
