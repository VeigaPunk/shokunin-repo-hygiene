# S84Reviewer — souji r84 independent re-derivation (C1 calibration, C2 operability)

Seat: S84Reviewer. Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. Scratch: /fast/scratch/hyaku/souji-r84/S84Reviewer/ (removed after copies below). Report: `.ufo/waves/round-84/w1/S84Reviewer.md` (this file). Tool installs: none (no new tools; python3/bash/git only, pre-existing). Read-only on the lane (no lane tracked file edited; two files under `census/round-84/records/` untracked during review: `c1-after.txt`, `c2-after-integration.txt` — see F8).

Methods: every number below is from a command this seat ran (all commands in §Evidence). Where a number was also already on disk (receipts, sibling seats), the file is cited and the re-run is shown separately.

## Frozen claims under review

- C1 (calibration 7): the 44-row population `census/round-84/c1-false-rows.tsv` (r83 36 rows byte-for-byte + TF8/TF9/TF10 TRUE + NF-P/NF-L/NF-L2/NF-M/NF-Q false, all R7) makes the unchanged counter `c1-pointer-counter.py` green on both populations (36/0, 44/0) and kills all five mutants m6–m10 on r84 (`killed_r84=5`) while the 36-row population kills 0/5. Counting commands: after `--only r84 --expect-killed 5`, before `--only r83`.
- C2 (operability 8): `cli_kill_tree` in `tools/souji-vault-verify.sh` freezes the CLI descendant tree (fork-free `/proc` map, SIGSTOP each, second map pass, SIGKILL sweep) so the 22-row counter reports `rows=22 mismatches=0 errors=0 orphans=0` EXIT 0 with l1/l2 `survivors=0`; control K-a (r83 bytes, sha256 `72a405f2…`) reports `mismatches=2`, 1 survivor each on l1/l2, EXIT 1.

## Findings (numbered, by severity)

### [info] C1 — verified on committed bytes (no defect)

Re-ran both frozen commands in this seat (full output §Evidence):

- After: `python3 -B census/round-84/c1-clause-battery.py --counter census/round-84/c1-pointer-counter.py --work <scratch> --only r84 --expect-killed 5` → `ARM pristine pop=r84 rows=44 mismatches=0 errors=0 exit=0`; `m6 killed=yes mismatches=1`, `m7 killed=yes mismatches=1`, `m8 killed=yes mismatches=2`, `m9 killed=yes mismatches=4`, `m10 killed=yes mismatches=1` (all `errors=0`, `exit=1`); `SUMMARY mutants=5 sets=r84 pristine_r84=ok killed_r84=5 killed_total=5`; printed `EXIT=0` (exit code of echoed subshell chain — caveat F6; the battery's own SUMMARY and per-mutant `exit=1` match).
- Before: `--only r83` → `ARM pristine pop=r83 rows=36 mismatches=0 errors=0 exit=0`; all five `MUTANT … killed=no mismatches=0 errors=0 exit=0`; `SUMMARY mutants=5 sets=r83 pristine_r83=ok killed_r83=0 killed_total=0`; `EXIT=0`.

Kill attribution (adversarial §3 demand): I re-ran the harness directly per mutant (`c1-false-row-harness.py --counter <mutant>.py --population census/round-84/c1-false-rows.tsv`, full ROW output copied to `hm6.txt…hm10.txt`), because the battery pipes harness stdout and discards row-level detail (battery `run()` keeps only the SUMMARY regex). Result — every kill is a genuine row mismatch (`match=no`), none is a harness error (`errors=0` everywhere):

| mutant | killing row(s) (got vs expect) | mismatch count |
|---|---|---|
| m6 digest-blind | NF-L got=MOVED (expect REFUSED) | 1 |
| m7 round-blind | NF-L2 got=MOVED (expect REFUSED) | 1 |
| m8 w-only | TF9 got=REFUSED, TF10 got=REFUSED (expect MOVED) | 2 |
| m9 basename-only | TF8 got=REFUSED, TF9 got=REFUSED, TF10 got=REFUSED (expect MOVED); NF-P got=MOVED (expect REFUSED) | 4 |
| m10 records-as-wave | NF-M got=MOVED (expect REFUSED) | 1 |

This is exactly the prereg's clause story (prereg lines 23–27: one FALSE row per clause + TRUE rows for a2w1/assimilation shapes). `old` occurs exactly once per mutant in the filed counter (seat check via `src.count`: all 1 — see §Evidence), so battery EXIT 2 cannot fire. Population pins: r84 `4795f009…` (44 rows), r83 `c9a6d58c…` (36 rows) — both match the battery's `PINS` and the harness `POP_PINS`; the 36-row prefix is byte-identical (`R84[:36]==R83`, extra ids exactly `[TF8, TF9, TF10, NF-P, NF-L, NF-L2, NF-M, NF-Q]`).

Kill-rule attack (§3): "killed" is `rc != 0 or mism > 0 or errs > 0` (battery line 118). A harness error (rc≠0) with `mism=0` would count as killed. **No such case occurred in the observed output** (every mutant has `mism≥1, errs=0`), so the ambiguity is real (disclosed in prereg line 41) but not load-bearing — the m8 kill is in fact the "worst" case: the mutant refuses TRUE rows TF9/TF10 (prima-facie an *acceptance* loss on true rows, which a strict reading of "false-row population" might discount), yet it is a forward-direction mismatch in the harness's own accounting (`refused_true=2`). Fairness concern is therefore methodological, not numeric: if the claim were read as "kills by accepting false rows only," m8 would fail (it never accepts a false row; it rejects two true rows). The frozen battery counts it, the prereg counts it, and the receipt discloses the rule; verdict stays verified, but the L1 should keep the m8→TF9/TF10 direction visible in the report (see R1, low).

Verdict C1: **verified** (36/0 + 44/0 pristine green, 5/5 killed on r84, 0/5 on r83 — all reproduced).

### [info] C2 — control reproduced; candidate comparison (chronology finding F4/F5 below)

- Control K-a, re-run twice in this seat (`--tool census/round-84/controls/c2-K-a-r83-tool.sh`): `SUMMARY rows=22 mismatches=2 errors=0 orphans=2`, `EXIT=1` both runs (first run's `C2-R83-EXIT=0` was a `tee`-pipeline exit-code artifact — see F6; bg_13371's capture of the second run shows `EXIT=1`). l1 (`secs=0.4`) and l2 (`secs=0.4`) both `survivors=1 tmpleft=0 match=no`, the other 20 rows all `match=yes`. Byte-identical to the filed receipt `census/round-84/controls/c2-before-r83-tool.txt` (same rows incl. secs scale, same 1 survivor each) and to `git show 54709d0d:tools/souji-vault-verify.sh | sha256sum = 72a405f2…` (base bytes).
- Survivor is the late setsid child: `latefork` (`STUBS` lines 127–130) traps TERM/INT/HUP, runs `setsid sleep 600 &` on first signal, then busy-loops. The counter's `nonce_pids` (lines 202–217) scans `/proc/*/environ` for `SOUJI_R81_NONCE=<nonce>` excluding zombies; `reap()` SIGKILLs them after the sweep floor. One survivor per late row = the `setsid`'d `sleep 600`, which the r83 single-pass read + TERM + group fallback cannot reach (its parent finished in the read→signal window and it left the process group). No leftover TMPDIR files (`tmpleft=0`) — cleanup works; the miss is precisely the kill, not the settle bookkeeping.

Candidate comparison (the finding that matters):

| candidate bytes | sha256 | counter result (this seat) |
|---|---|---|
| r83 control | `72a405f2…` | mismatches=2 (l1,l2), EXIT=1 |
| `.ufo/waves/round-84/w1/S84ExecC2/souji-vault-verify.sh` (seat S84ExecC2 final) | `a33038e9…` | **mismatches=0, EXIT=0** (l1 `secs=0.8 survivors=0`, l2 `secs=0.8 survivors=0`, all 22 match=yes) — receipt `S84ExecC2/c2-after-receipt.txt` binds the same hash, re-derived |
| `.ufo/waves/round-84/w1/RefC2/souji-vault-verify.sh` (RefC2 pre-freeze reference) | `a810acaf…` (moved from `66f53527…` mid-review, §F4) | **mismatches=5, EXIT=1**: m1, m2, d24-monitor-group, l1, l2 all `survivors=1` (d24-group `survivors=24`) |
| L1 integ scratch `/fast/scratch/hyaku/souji-r84/integ/souji-vault-verify.sh` | `030fa10d…` | untracked `records/c2-after-integration.txt` claims 22/0 — **not re-run by this seat** (violates host-guard scratch rule? integ dir is outside my scratch and I was told to re-run the candidate path if it exists; I used S84ExecC2/RefC2 instead — see F9). |

So on the seat's own frozen command, S84ExecC2's final bytes pass and RefC2's *current* bytes fail five rows, not two. The prereg freezes the candidate path as `.ufo/waves/round-84/w1/S84ExecC2/souji-vault-verify.sh` only to fall back ("if it exists … otherwise the r83 tool"); it exists and is still mutating (F5). Verdict below reflects this.

### [medium] F1 — RefC2 bytes were edited after its pre-freeze receipt bound them; the bound hash is gone

`census/round-84/records/c2-reference-prefreeze.txt` binds `# tool path=…/w1/RefC2/souji-vault-verify.sh sha256=66f535273bc1523175c11cdace36a7de189c98dc50ac016a3e591c04fbbf5e73 mode=0o644` and shows 22/0 green. The current RefC2 file is `a810acaf438cd6deee83a98f0db5b9697a5b5029f3126c207929c391f1130b25` (m 03:19) and fails 5 rows including **both late rows** (l1 `secs=2.7`, l2 `secs=2.8`, survivors=1 each) plus m1/m2/d24-monitor-group in my run (`c2-ref-repro.txt`; earlier partial capture in the same seat showed l1/l2 only failing — wave-machine load shifts `secs`, but the survivors=1 is stable). Any claim that cites `66f53527…` cannot be re-derived by a later reader: the bytes it bound no longer exist on disk, and the replacement bytes do not reproduce the receipt. Reviewer reproducer: the frozen C2 command on the RefC2 path (before my `chmod 644` revert; mode was `0o644` at receipt and at first read). The implementation *differs in a behaviorally relevant way* from the passing candidate: RefC2 clears `ppid_of/start_of/kids_of` on **every** map pass (`ppid_of=() start_of=() kids_of=()` inside `for pass in 1 2`), so `start_of` keeps only the last pass's stamps; S84ExecC2 keeps the first write across passes (seat spec §2 / diff comment: "first write wins across both passes"), so a pid recycled between passes never passes the re-check. Both stop with starttime re-check; the NCLR/start-stamp retention is what keeps monitor-launch children (reparented across passes) reachable. Reproducer to inspect: `diff -u` the two candidates' `cli_kill_tree` (one hunk each), then run the frozen counter on each.

### [medium] F2 — `kill -STOP` coverage (which exact kill, and a timing caveat)

RefC2 signals `-STOP` to descendants **in discovered order** (DFS from the root, per pass; line 277 `kill -STOP "$k"` after `start_of` re-check), never to the root, then `-KILL` sweep. S84ExecC2's comment (diff) says the same ("every descendant found by a fork-free /proc pass is SIGSTOPped (with its starttime re-read right before the STOP)"). A stopped process can neither fork nor run a trap — correct. **Caveat**: no pass ever SIGSTOPs an *already stopped* parent's *unseen* child in the general case — pass 2 only helps when pass 1 stopped the parent *in* its window **before the child forks** (the observed latefork case: parent stopped first, so `setsid` never runs, or the child stays a child and is seen). If the CLI runs its trap *before* the first STOP lands (e.g. a fork that happened pre-freeze but whose parent then died between passes), the prereg's stopped-parent invariant fails — prereg line 81 discloses exactly this ("a child that setsids AND whose parent died in that window does not" survive / is not claimed). My reads confirm the limit is real and accurately stated; do not over-claim "leaves nothing behind" beyond the frozen population.

### [info] F3 — chronology and scope verified; two scope anomalies (both benign, recorded for the report)

- `git show --name-only 35d87842` (F) = **`census/round-84/preregistration.txt` ALONE** (1 file, 90 lines). PASS.
- `git show --name-only bd2bbb12` (P) = 13 census files (battery, harness, counter, mutants, populations, both counters, both controls/receipts, three records files) + `corpus/QUALITY.md` (+2 lines: "## Round 23 criteria" heading, i.e. a criteria-table header rather than a Q-row). All 8 hashes I re-derived from `bd2bbb12:` bytes (`c1-false-rows 4795f009…`, `counter 052c4f3f…`, `harness 51b30dbd…`, `mutants b71cf3d8…`, `c2-population 31422477…`, `battery 86d31be7…`, `c2-counter 43078272…`, `K-a tool 72a405f2…`) match disk *now*, and P→F (`git diff --stat bd2bbb12 35d87842`) is the preregistration alone. No edge into `MANIFEST`/`.ufo/state`/`.scratch` in either commit.
- **P is parented on base `54709d0d`**, matching the prereg's stated "Lane base" line — but the head's `git log` shows `35d87842`→`bd2bbb12`→`54709d0d` on `master`/`origin/master`, i.e. the current `master` tip *is* F (verified `branch --contains`). Hash identity: `git show 54709d0d:tools/souji-vault-verify.sh | sha256sum = 72a405f2…` = the K-a/control bytes. (The task prompt's "Lane base: 35d87842… (r83 closed admitted)" is the *F commit*, not the r83-close commit `54709d0d`; prereg line 2 (`54709d0d… r83 closed admitted`) is the correct one — same file set either way, no action needed, but the L1 should not propagate the prompt's mislabel.)
- You will see stray commits in `git log --all` (e.g. `1ae2465a`, `61ad4c84`, `757bc678`, `e46d4cab`, …): these are **fleet-level protocol/hook commits** (author `protocol-shokunin`, `__pycache__/*.pyc` in the stat — the protocol-shokunin lane, not the soulji-lane commits). Only `54709d0d`/`bd2bbb12`/`35d87842` are on the lane's `master` ancestry. No finding, recorded so nobody re-opens it.
- **Untracked `records/c1-after.txt` + `records/c2-after-integration.txt` on disk** (mtime 03:26/03:29, after P 03:00 and after F 03:18): `git status --porcelain -- census/` = `?? census/round-84/records/c1-after.txt` and `?? census/round-84/records/c2-after-integration.txt`. These are *after-arm receipts* that postdate F. `c1-after.txt` re-derives my battery (same 5 lines + `C1-AFTER-EXIT=0`); `c2-after-integration.txt` claims 22/0 for a tool at `/fast/scratch/hyaku/souji-r84/integ/…` (sha256 `030fa10d…`) that is **not a frozen command target** and was not from the S84ExecC2 path. They are untracked (not committed bytes), so F/P chronology is clean, but an "after-arm receipt" on disk before integration is exactly what check (2) asks about: **no after-arm receipt predates F** holds (both mtimes are after F's 03:18:20), and neither is in `git log`. Acceptable; flagging so the L1 states in the report that the integrated receipt binds a *new* hash (`030fa10d…`) and is an integration artifact, not a frozen wave receipt.

### [low] F4 — candidate tool bytes are not stable; every receipt must bind a hash

S84ExecC2's `souji-vault-verify.sh` hash was `72a405f2…` (== r83, i.e. *no candidate yet*) when this seat first read it, then became `a33038e9…` (mtime 03:22:38, size 81,069) before my C2-on-candidate run; `sha256sum` now re-reads `a33038e9…` and the seat's receipt `S84ExecC2/c2-after-receipt.txt` binds the same `a33038e9…` and matches my re-run (`c2-s84exec-repro.txt` 22/0 EXIT=0, l1/l2 `secs=0.8 survivors=0`). Good — the binding survived. But `RefC2`'s bytes moved (`66f53527…`→`a810acaf…`) *after* its pre-freeze receipt. Lesson for the integration commit: bind the integrated `sha256` into `c2-after-integration.txt` (it does — its header prints `sha256=030fa10d…`) and regenerate the pre-freeze record or drop RefC2 from the evidence chain. Review verdict (C2 "after" target) is on S84ExecC2's `a33038e9…`.

### [low] F5 — timeout artifact on `secs`/exit codes (measurement caveat, no numeric impact)

Two early runs measured `C2-R83-EXIT=0` and battery tail lines were truncated at the 300 s bash deadline because I piped through `tee` and the first C1 batteries ran under fleet load (six concurrent `c1-clause-battery.py` invocations from other seats). Exit codes from the *captured* `bg_*` jobs (`bg_13371`, `bg_13280`, `bg_13281`, `bg_13282`, `bg_13283`) are the authoritative ones used above (all `EXIT=1` for the r83 control, `EXIT=0` where green); my own `echo EXIT=$?` after a `tee` pipeline reported the *tee* status (0). This seat's C1 after/before and C2 control numbers above come from those captured jobs, and from a later wait-free read of `c1-after2.txt/c1-before2.txt/c2-r83b.txt` whose `SUMMARY`/`EXIT` fields match the receipts. The numbers themselves reproduce; the artifact was tooling, not the claims.

### [info] F6 — kill rule, indirect branches, and m8/m9 fairness (exact answer to §3)

- "Does `killed_r84=5` mean killed by ANY red row including harness error?" — By code: yes, `killed = rc!=0 or mism>0 or errs>0` (battery L118). By observation: **no kill in the 5/5 was an error**; each was a real `match=no` row mismatch (see table in C1 section), all `errors=0`. So the sentence means what the prereg says.
- "Is a kill fair when the mutant changes a branch the row exercises only indirectly?" — The five rows that kill each mutant exercise the **exact** clause the mutant edits, with the new-row comments in the population and the runnable `old→new` single edit: m6→NF-L (digest branch — mutant replaces `elif rev_digest(...) != frozen` with `elif False`); m7→NF-L2 (round branch — `elif kr and (not tr or tr.group(1)!=kr.group(1))`); m8→TF9/TF10 (the `OWNTREE_WAVE` alternation itself); m10→NF-M (the same `OWNTREE_WAVE` alternation widened); m9→TF8/TF9/TF10+NF-P (the `got[1:]==want[1:]` suffix-depth branch). There is no single-edit mutant in the battery that reaches only indirectly-exercised branches in the observed output. The deep `rev_digest`/`rev_target` machinery around m6/m7 is still fully exercised per row (harness forges one row at a time under a pinned fixture rev with a byte-source pin check), so a kill is a clause kill, not a harness-construction kill.
- m8/m9 wrinkle (recorded for the L1): m8 and m9 kill by **refusing true rows and (m9) accepting one false row**. If the C2-in-prereg phrasing is ever read as "the population certifies the counter *does not accept false rows*," m8's contribution is a *completeness* loss (TF9/TF10 false refusals) rather than a *correctness* gain. Numbers unchanged; methodologically the L1 should phrase the C1 finding as "the fuller population discriminates the five clause mutants (acceptance direction: NF-L, NF-L2, NF-P, NF-M; refusal direction: TF8–TF10)" — the receipts' `accepted/refused_true` columns already carry this.

### [info] F7 — C2 late rows: mutant/battery attack table

| probe | observed (this seat) |
|---|---|
| mismatches=2 on l1/l2 reproducible? | Yes — twice (c2-r83b: 2/2, secs 0.4/0.4, EXIT=1; plus the committed receipt). |
| survivor really the late setsid child? | Yes — the only nonce-carrying, non-zombie process at the settle sweep is the `setsid sleep 600` (nonce_pids finds it by `SOUJI_R81_NONCE`, and `reap` kills it; the counter's `tmpleft=0` shows no runaway). Under the r83 tool the CLI's trap runs inside the read→TERM window and forks after the map pass; with `setsid` it also leaves the group TERM/KILL fallback. |
| S84ExecC2 bars (prereg kill rule, line 79) | `--selftest` 57/0 (seat evidence, and re-derived for RefC2's bytes: 57/0 once `souji-round9-selftest.sh` was present in the same dir; RefC2's solo run failed R9 only because the runner was absent in that dir — environment, not bytes). Fork-free: `cli_kill_tree.diff` is one hunk, no `pgrep`/`ps` outside comment text (checked); r17/dummy-D (tmpdir probe) claimed by S84ExecC2 via `c2-after` collection — **not re-run in this seat** (residual risk, see below). |

### [info] F8 — residual risks / verification gaps (what this seat did NOT do)

1. I did **not** re-run `r17` (`tests/fixtures/r17-jj-receipts.sh`) or `probe D` (`tmpdir-in-vault.py`) against the S84ExecC2 candidate; S84ExecC2's evidence claims 35/0/2-skipped and 4/0, and I verified its counter receipt binds the same `a33038e9…` hash. The L1/integration should attach those two numbers to the integrated file (`030fa10d…`), not to S84ExecC2's path.
2. I did **not** run `c2-late-fork-counter.py` against integ bytes `030fa10d…` (outside my scratch, mutable between reads; hash stability across the integration window is the L1's to assert).
3. My RefC2-run numbers vary in *which* extra rows fail (`m1/m2/d24` in `c2-ref-repro.txt`, different `secs`) under fleet load; survivors=1 is stable but the exact mismatch count (5 vs 2) depends on wall time. Honest range: **RefC2 current bytes fail ≥2 (l1/l2), and 5 in my captured run**; nobody should quote "5" as frozen.
4. LSP/`references/definition/diagnostics` check: unavailable in this environment (no `lsp` device advertised in the tool inventory). Verification was done by code reading (battery `run()` L48–61 / `killed` L106–129; harness `main()` L248–317; counter `run_row` L248–335, `nonce_pids` L202–217), text search, and by re-executing every frozen command. Unavailability recorded here; **grep output is not presented as semantic proof** — every semantic claim above cites a file line or a re-run.

## Overall verdict

- **C1 (calibration): verified.** Re-derived: pristine 36/0 (r83) and 44/0 (r84), `killed_r84=5` (`m6=NF-L`, `m7=NF-L2`, `m8=TF9/TF10`, `m9=TF8/TF9/TF10/NF-P`, `m10=NF-M`), `killed_r83=0`, all `errors=0`, all `old` counts = 1. No harness-error kills, no indirect-branch kills.
- **C2 (operability): verified for the control and for S84ExecC2's final bytes; not verified for RefC2's current bytes.** Re-derived: r83 control `mismatches=2` on exactly l1/l2 (1 survivor each, the late setsid `sleep 600`), EXIT=1. S84ExecC2 `a33038e9…` passes 22/0 EXIT=0 (integrated candidate is a different hash `030fa10d…` — integration must re-run). RefC2's current bytes `a810acaf…` fail 5 rows (l1/l2 included) and do **not** reproduce their pre-freeze receipt (`66f53527…` is gone from disk).
- **Chronology: verified.** F (`35d87842`) = preregistration alone; P (`bd2bbb12`) = instruments/controls/before-receipts (+ QUALITY heading); P→F diff = preregistration only; all 8 pinned hashes match between P bytes and disk; no after-arm receipt predates F (the two untracked after-arm receipts on disk postdate F by 8–11 min); no `MANIFEST`/`.ufo/state`/`.scratch` writes in either commit.

## Evidence — every command this seat ran (scratch under /fast/scratch/hyaku/souji-r84/S84Reviewer/)

```
# C1 after (full battery)
python3 -B census/round-84/c1-clause-battery.py --counter census/round-84/c1-pointer-counter.py --work /fast/scratch/hyaku/souji-r84/S84Reviewer/c1-after2 --only r84 --expect-killed 5
# -> ARM pristine pop=r84 rows=44 mismatches=0 errors=0 exit=0
#    MUTANT m6/m7 killed=yes mismatches=1, m8 killed=yes mismatches=2, m9 killed=yes mismatches=4, m10 killed=yes mismatches=1 (all errors=0 exit=1)
#    SUMMARY mutants=5 sets=r84 pristine_r84=ok killed_r84=5 killed_total=5; captured EXIT=0 (bg_13280)
# C1 before (full battery)
python3 -B census/round-84/c1-clause-battery.py --counter census/round-84/c1-pointer-counter.py --work /fast/scratch/hyaku/souji-r84/S84Reviewer/c1-before2 --only r83
# -> ARM pristine pop=r83 rows=36 mismatches=0 errors=0 exit=0; all 5 MUTANT killed=no mismatches=0 errors=0 exit=0
#    SUMMARY mutants=5 sets=r83 pristine_r83=ok killed_r83=0 killed_total=0; captured EXIT=0 (bg_13281)
# C1 kill mapping (harness per mutant, --population census/round-84/c1-false-rows.tsv, 44 rows each)
python3 -B census/round-84/c1-false-row-harness.py --counter <scratch>/c1-after2/mut/m{6,7,8,9,10}-*.py --lane <lane> --fleet-root /home/vgpnk/Projects/shokunin --work <scratch>/hm{6..10}
# -> hm6: NF-L match=no (got=MOVED); hm7: NF-L2 match=no; hm8: TF9+TF10 match=no; hm9: TF8+TF9+TF10+NF-P match=no; hm10: NF-M match=no; all errors=0
# C2 counter on r83 control (twice)
python3 -B census/round-84/c2-late-fork-counter.py --tool census/round-84/controls/c2-K-a-r83-tool.sh --work <scratch>/c2-r83[b]
# -> SUMMARY rows=22 mismatches=2 errors=0 orphans=2; l1/l2 survivors=1 match=no; EXIT=1
# C2 counter on S84ExecC2 candidate
python3 -B census/round-84/c2-late-fork-counter.py --tool .ufo/waves/round-84/w1/S84ExecC2/souji-vault-verify.sh --work <scratch>/c2-s84exec
# -> tool sha256=a33038e9…; SUMMARY rows=22 mismatches=0 errors=0 orphans=0; EXIT=0
# C2 counter on RefC2 candidate (current bytes)
python3 -B census/round-84/c2-late-fork-counter.py --tool .ufo/waves/round-84/w1/RefC2/souji-vault-verify.sh --work <scratch>/c2-ref
# -> tool sha256=a810acaf…; SUMMARY rows=22 mismatches=5 errors=0 orphans=5; EXIT=1 (m1,m2,d24-monitor-group,l1,l2)
# Commits / pins
git -C <lane> show --name-only --pretty=format:'%H %P %ad %s' 35d87842 bd2bbb12; git -C <lane> show --stat 35d87842 | cat; git -C <lane> diff --stat bd2bbb12 35d87842
git -C <lane> show 54709d0d:tools/souji-vault-verify.sh | sha256sum; git -C <lane> show bd2bbb12:<8 censuses files> | sha256sum  # all match disk
sha256sum census/round-84/c1-false-rows.tsv census/round-83/c1-false-rows.tsv census/round-84/controls/c2-K-a-r83-tool.sh census/round-84/c1-pointer-counter.py census/round-84/c1-false-row-harness.py census/round-84/c1-mutants.json census/round-84/c2-population.tsv census/round-84/c2-late-fork-counter.py census/round-84/c1-clause-battery.py
python3 prefix check: r84[:36]==r83 (extra ids TF8,TF9,TF10,NF-P,NF-L,NF-L2,NF-M,NF-Q); C2 rows 22, last2 l1-late-setsid-pid,l2-late-setsid-group
bash -n <candidates>; bash <candidate> --selftest  # 57 checks, 0 failed (with runner present)
```

## Files written (this seat only; originals untouched)

- `.ufo/waves/round-84/w1/S84Reviewer.md` — this file
- `.ufo/waves/round-84/w1/S84Reviewer/c1-after-repro.txt` (copy of `c1-after2.txt`)
- `.ufo/waves/round-84/w1/S84Reviewer/c1-before-repro.txt` (copy of `c1-before2.txt`)
- `.ufo/waves/round-84/w1/S84Reviewer/c2-r83-repro.txt` (r83 control run)
- `.ufo/waves/round-84/w1/S84Reviewer/c2-s84exec-repro.txt` (S84ExecC2 `a33038e9…` run)
- `.ufo/waves/round-84/w1/S84Reviewer/c2-ref-repro.txt` (RefC2 `a810acaf…` run)
- `.ufo/waves/round-84/w1/S84Reviewer/hm6.txt … hm10.txt` (per-mutant harness ROW output)

(Scratch `/fast/scratch/hyaku/souji-r84/S84Reviewer/` was removed after these copies, per the binding scratch rule. No `MANIFEST.json`, `.ufo/state/*`, `.scratch/*`, `.ufo/watchdog.log`, fleet-root, or sibling-lane file was touched. One temporary `chmod +x` on RefC2 during probing was reverted to `0644`; a stray `souji-round9-selftest.sh` copied into RefC2 for a selftest probe was deleted.)
