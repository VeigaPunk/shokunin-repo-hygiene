# R42w3critic01 — axis-harm audit

**Verdict:** no durable harmful regression found on calibration, operability, or coverage. Strict printed-result equality is not perfect: the r41 counter exposes the expected new tool digest, the registry check echoes the revision argument, and the landing-gate result improves from three findings to zero. The one volatile live-process mismatch passed three serial rechecks per revision.

## Method and scope

Read first: `census/round-42/preregistration.txt`, then `corpus/lessons/round-42.md`. Audited base `bf618f6c5c09d302994871c94903abbea2deb60d` vs tip `6a3f75941d3604e3459011d599c2c16f3a97b44c`; no lane/fleet writes. Base and tip were `git clone --shared --no-checkout` checkouts under the seat scratch; both `git -C <checkout> rev-parse --show-toplevel` values equaled their checkout directories. Gate execution used explicit `TMPDIR` under seat scratch, four workers, 120 s per case, with `ROUND=41` for both revisions. The 61 prior cases use the command list in committed `census/round-41/waves/w2/R41w2executor03/run-gates.py:14-77`; four rows already present at the r42 base were added using their `SKILL.md` entries. New r42 rows were run tip-only, sequentially.

Search `souji-freeze-check.py` in `SKILL.md`, `tests/`, and `census/`: `tests/` had no matches; `SKILL.md:282-283,288-289` names the entry, r41 counter, r42 counter and selftest; executable counter consumers are `census/round-41/c2-counter.py:69` and `census/round-42/c2-counter.py:68`. The C2 rows were run at both revisions where present.

## Registry comparison — exact observed results

The first pass had 61/61 rows in the N19 battery plus four r41 rows (65 base/tip pairs); six r42 rows are tip-only. `identical?` compares exit code and the reported summary/output line exactly. The table records the primary pair; row 25 also records its serial repeats. On N19's semantic comparison (ignoring only echoed revision identity), the first run matched 59/61: the two deltas were the live-process r18 leak counter and the round-41 landing gate. After the r18 leak row's three serial retries at each revision, 60/61 semantic matches remained; the durable row-60 difference is favorable (base findings=3, tip findings=0). Across all 65 pre-r42 rows, strict exact equality was 61/65 initially and 62/65 after the leak rechecks; the remaining strict differences are identity metadata or that favorable gate repair.

| # | gate row/check | base result | tip result | identical? |
|---:|---|---|---|:---:|
| 0 | souji-verify selftest | `rc=0; selftest: 49 checks, 0 failed` | `rc=0; selftest: 49 checks, 0 failed` | yes |
| 1 | souji-vault-verify selftest | `rc=0; selftest: 57 checks, 0 failed` | `rc=0; selftest: 57 checks, 0 failed` | yes |
| 2 | souji-census selftest | `rc=0; selftest: 69 checks, 0 failed` | `rc=0; selftest: 69 checks, 0 failed` | yes |
| 3 | souji-quarantine selftest | `rc=1; selftest: 108 checks, 58 failed` | `rc=1; selftest: 108 checks, 58 failed` | yes |
| 4 | r12-maintenance-guard --selftest | `rc=0; selftest=PASS ids=6/6` | `rc=0; selftest=PASS ids=6/6` | yes |
| 5 | souji-cert-evidence selftest | `rc=0; selftest: 36/36 passed` | `rc=0; selftest: 36/36 passed` | yes |
| 6 | r13-cert-evidence | `rc=0; fixture: 5/5 checks passed` | `rc=0; fixture: 5/5 checks passed` | yes |
| 7 | r13-repo-structure | `rc=0; selftest=PASS ids=7/7` | `rc=0; selftest=PASS ids=7/7` | yes |
| 8 | r13-quarantine-bounds | `rc=0; SUMMARY	total=5	failed=0	hung=0` | `rc=0; SUMMARY	total=5	failed=0	hung=0` | yes |
| 9 | souji-evidence-cache selftest | `rc=0; selftest: 48/48 passed` | `rc=0; selftest: 48/48 passed` | yes |
| 10 | r14-evidence-cache | `rc=0; fixture: 22/22 checks passed` | `rc=0; fixture: 22/22 checks passed` | yes |
| 11 | r14-census-boundary | `rc=0; SUMMARY	total=12	failed=0` | `rc=0; SUMMARY	total=12	failed=0` | yes |
| 12 | r15-census-config | `rc=0; SUMMARY	total=20	failed=0` | `rc=0; SUMMARY	total=20	failed=0` | yes |
| 13 | r17-census-hygiene | `rc=0; SUMMARY	total=29	failed=0` | `rc=0; SUMMARY	total=29	failed=0` | yes |
| 14 | r17-jj-receipts | `rc=0; SUMMARY	total=35	failed=0	skipped=2` | `rc=0; SUMMARY	total=35	failed=0	skipped=2` | yes |
| 15 | souji-preservation-evidence selftest | `rc=0; selftest: 47/47 passed` | `rc=0; selftest: 47/47 passed` | yes |
| 16 | r15-preservation-evidence | `rc=0; fixture: 8/8 checks passed` | `rc=0; fixture: 8/8 checks passed` | yes |
| 17 | souji-landing-gate selftest | `rc=0; SELFTEST	pass=65	fail=0` | `rc=0; SELFTEST	pass=65	fail=0` | yes |
| 18 | r18-landing-pointers | `rc=0; SUMMARY	total=11	failed=0` | `rc=0; SUMMARY	total=11	failed=0` | yes |
| 19 | r16-landing-gate | `rc=0; SUMMARY	total=15	failed=0` | `rc=0; SUMMARY	total=15	failed=0` | yes |
| 20 | souji-seat-audit selftest | `rc=0; SELFTEST	pass=118	fail=0` | `rc=0; SELFTEST	pass=118	fail=0` | yes |
| 21 | r17-transcript-manifest --check | `rc=0; check OK: 144 files verified` | `rc=0; check OK: 144 files verified` | yes |
| 22 | r18-census-bounded | `rc=124; TIMEOUT 120s` | `rc=124; TIMEOUT 120s` | yes |
| 23 | souji-proc-census selftest | `rc=0; souji-proc-census: selftest PASS (newline comm parser, live literal cwd/fd, age identity, all redactions, prefix boundary/scope, mixed precedence, isolated cleanup)` | `rc=0; souji-proc-census: selftest PASS (newline comm parser, live literal cwd/fd, age identity, all redactions, prefix boundary/scope, mixed precedence, isolated cleanup)` | yes |
| 24 | r18-proc-census | `rc=1; SUMMARY	total=19	failed=17` | `rc=1; SUMMARY	total=19	failed=17` | yes |
| 25 | r18-leak-count selftest | `rc=0; JSON selftest=pass (before=112, after=113); serial reruns: rc=0/pass ×3` | `rc=1; deleted FIFO reader mismatch (before=112, after=114); serial reruns: rc=0/pass ×3` | no (primary pair; serial reruns pass both) |
| 26 | souji-rev-pin selftest | `rc=0; SUMMARY total=11 failed=0` | `rc=0; SUMMARY total=11 failed=0` | yes |
| 27 | r19-rev-pin | `rc=0; SUMMARY total=13 failed=0 base_discriminating=6` | `rc=0; SUMMARY total=13 failed=0 base_discriminating=6` | yes |
| 28 | r19-carry-wrap | `rc=0; SUMMARY total=4 failed=0 base_discriminating=2` | `rc=0; SUMMARY total=4 failed=0 base_discriminating=2` | yes |
| 29 | probe-carry-invariants | `rc=0; SUMMARY paragraphs=400 boundary_cuts=562 midline_cuts=842 violations=0` | `rc=0; SUMMARY paragraphs=400 boundary_cuts=562 midline_cuts=842 violations=0` | yes |
| 30 | r19-seat-audit-shapes | `rc=0; SUMMARY total=17 failed=0 base_discriminating=12` | `rc=0; SUMMARY total=17 failed=0 base_discriminating=12` | yes |
| 31 | verify-agreement-pin selftest | `rc=0; SUMMARY total=5 failed=0` | `rc=0; SUMMARY total=5 failed=0` | yes |
| 32 | r20-audit-contract | `rc=0; SUMMARY	total=66	pass=66	fail=0	base_discriminating=0` | `rc=0; SUMMARY	total=66	pass=66	fail=0	base_discriminating=0` | yes |
| 33 | r21-read-root | `rc=0; SUMMARY	total=32	pass=32	fail=0	base_discriminating=14` | `rc=0; SUMMARY	total=32	pass=32	fail=0	base_discriminating=14` | yes |
| 34 | r21-reason-canary | `rc=0; SUMMARY	total=27	pass=27	fail=0	leaks=0	base_leaks=19	max_reason_bytes=160` | `rc=0; SUMMARY	total=27	pass=27	fail=0	leaks=0	base_leaks=19	max_reason_bytes=160` | yes |
| 35 | r21-read-render-edges | `rc=0; SUMMARY	total=4	pass=4	fail=0` | `rc=0; SUMMARY	total=4	pass=4	fail=0` | yes |
| 36 | r21-replay-boundaries | `rc=0; SUMMARY	total=8	pass=8	fail=0	base_discriminating=4` | `rc=0; SUMMARY	total=8	pass=8	fail=0	base_discriminating=4` | yes |
| 37 | r21-source-head | `rc=0; SUMMARY	total=3	pass=3	fail=0	base_discriminating=1` | `rc=0; SUMMARY	total=3	pass=3	fail=0	base_discriminating=1` | yes |
| 38 | r22-result-oracle | `rc=0; JSON total=258 (schema souji-r22-result-oracle-receipt-v1)` | `rc=0; JSON total=258 (schema souji-r22-result-oracle-receipt-v1)` | yes |
| 39 | r22-mutation-adequacy | `rc=0; JSON mutants=59 killed=52 survived=7 disagreeing=[]` | `rc=0; JSON mutants=59 killed=52 survived=7 disagreeing=[]` | yes |
| 40 | r27-pre-report-gate fixture | `rc=0; cases=4 pass=4 control=FALSE-GREEN-REJECTED` | `rc=0; cases=4 pass=4 control=FALSE-GREEN-REJECTED` | yes |
| 41 | souji-report-contract selftest | `rc=0; SUMMARY cases=9 pass=9 fail=0` | `rc=0; SUMMARY cases=9 pass=9 fail=0` | yes |
| 42 | r36-report-gate | `rc=0; SUMMARY cases=21 pass=21 fail=0 control=STUB-REJECTED` | `rc=0; SUMMARY cases=21 pass=21 fail=0 control=STUB-REJECTED` | yes |
| 43 | r36-worktree-drift | `rc=0; SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED` | `rc=0; SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED` | yes |
| 44 | r37-citation-reconcile | `rc=0; SUMMARY cases=16 pass=16 fail=0 control=FALSE-GREEN-REJECTED` | `rc=0; SUMMARY cases=16 pass=16 fail=0 control=FALSE-GREEN-REJECTED` | yes |
| 45 | r38-counter-arms | `rc=0; SUMMARY cases=6 pass=6 fail=0 control=FALSE-GREEN-REJECTED` | `rc=0; SUMMARY cases=6 pass=6 fail=0 control=FALSE-GREEN-REJECTED` | yes |
| 46 | r37-drift-escapes | `rc=0; SUMMARY cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED` | `rc=0; SUMMARY cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED` | yes |
| 47 | r37-drift-discrimination | `rc=0; SUMMARY cases=6 pass=6 fail=0` | `rc=0; SUMMARY cases=6 pass=6 fail=0` | yes |
| 48 | r37-drift-mutants | `rc=0; SUMMARY mutants=6 killed=6 survived=0` | `rc=0; SUMMARY mutants=6 killed=6 survived=0` | yes |
| 49 | r29-registry-agreement fixture | `rc=1; cases=20 pass=0 control=FALSE-GREEN-REJECTED` | `rc=1; cases=20 pass=0 control=FALSE-GREEN-REJECTED` | yes |
| 50 | r28-wave-evidence-capture | `rc=0; cases=15 pass=15 control=TAMPER-REJECTED` | `rc=0; cases=15 pass=15 control=TAMPER-REJECTED` | yes |
| 51 | r30-landing-gate-discovery | `rc=0; cases=7 pass=7 control=FALSE-GREEN-REJECTED` | `rc=0; cases=7 pass=7 control=FALSE-GREEN-REJECTED` | yes |
| 52 | r31-landing-gate-precision | `rc=0; cases=10 pass=10 control=FALSE-GREEN-REJECTED` | `rc=0; cases=10 pass=10 control=FALSE-GREEN-REJECTED` | yes |
| 53 | r38-citation-commit | `rc=0; SUMMARY cases=14 pass=14 fail=0 control=FALSE-GREEN-REJECTED` | `rc=0; SUMMARY cases=14 pass=14 fail=0 control=FALSE-GREEN-REJECTED` | yes |
| 54 | r38-drift-write-envelope | `rc=0; SUMMARY cases=12 pass=12 fail=0 base_cases=12 base_fail=6 behavioral_fail=3` | `rc=0; SUMMARY cases=12 pass=12 fail=0 base_cases=12 base_fail=6 behavioral_fail=3` | yes |
| 55 | r38-drift-record | `rc=0; SUMMARY cases=10 pass=10 fail=0` | `rc=0; SUMMARY cases=10 pass=10 fail=0` | yes |
| 56 | r38-drift-mutants | `rc=0; SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0` | `rc=0; SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0` | yes |
| 57 | r39-citation-rev | `rc=0; SUMMARY cases=8 pass=8 fail=0` | `rc=0; SUMMARY cases=8 pass=8 fail=0` | yes |
| 58 | r39-drift-record-rules | `rc=0; SUMMARY cases=7 pass=7 fail=0` | `rc=0; SUMMARY cases=7 pass=7 fail=0` | yes |
| 59 | souji-registry-agreement (lane check) | `rc=1; SUMMARY k1=1 k2=0 mismatches=1 rev=bf618f6c5c09d302994871c94903abbea2deb60d` | `rc=1; SUMMARY k1=1 k2=0 mismatches=1 rev=6a3f75941d3604e3459011d599c2c16f3a97b44c` | no |
| 60 | souji-landing-gate (lane check) | `rc=1; SUMMARY	findings=3	checked_reg=107	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=165` | `rc=0; SUMMARY	findings=0	checked_reg=113	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=165` | no |
| 61 | r41-freeze-check-cases | `rc=0; SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=8131847bcfc5` | `rc=0; SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=9ddd596b98fb` | no |
| 62 | r41-refusal-sites | `rc=0; SUMMARY probes=21 pass=21 fail=0` | `rc=0; SUMMARY probes=21 pass=21 fail=0` | yes |
| 63 | r41-drift-record-order | `rc=0; SUMMARY cases=12 pass=12 fail=0` | `rc=0; SUMMARY cases=12 pass=12 fail=0` | yes |
| 64 | r41-c1-corrections | `rc=0; SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1` | `rc=0; SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1` | yes |
| 65 | r42-c1-counter | `N/A (SKILL row absent at base)` | `rc=0; SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | expected tip-only |
| 66 | r42-c2-counter | `N/A (SKILL row absent at base)` | `rc=0; SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=9ddd596b98fb` | expected tip-only |
| 67 | r42-freeze-check-selftest | `N/A (SKILL row absent at base)` | `rc=0; SELFTEST cases=31 pass=31 fail=0` | expected tip-only |
| 68 | r42-c3-counter | `N/A (SKILL row absent at base)` | `rc=0; SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247` | expected tip-only |
| 69 | r42-drift-conditions | `N/A (SKILL row absent at base)` | `rc=0; SUMMARY cases=13 pass=13 fail=0` | expected tip-only |
| 70 | r42-r1-counter | `N/A (SKILL row absent at base)` | `rc=1; SUMMARY findings=0 deleted=2 rows_added=0 stale=0` | expected tip-only |

**R1 row 70:** tip `r42-r1-counter` remains rc1 with `findings=0 deleted=2 rows_added=0 stale=0`, the preregistered predicate miss already recorded as red by its letter in the round lesson; R1 is a residual repair, not one of the three owned axes.

**Volatile row 25 details:** primary base `rc=0`, JSON `selftest=pass` (`before=112 after=113`); primary tip `rc=1`, `deleted FIFO reader was not counted exactly once (before=112, after=114)`. Then three serial runs at each revision all returned `rc=0`, JSON `selftest=pass`, `before=94 after=95`. Tool bytes were unchanged; this is not a reproducible tip regression.

**Pre-r42 deltas:** row 59 keeps `k1=1 k2=0 mismatches=1` at both revisions; only its echoed `rev=` differs. Row 60 `--round 41` is base `rc=1`, three `LG-DANGLING-PTR` findings, versus tip `rc=0`, `findings=0`; `--round 40` likewise went from those same three findings/rc1 to findings0/rc0. `corpus/README.md:217` and `corpus/knowledge/jj-colocation-receipts.md:148` show the R1 repoint to byte-exact lane report copies; this is a favorable repair, not a trade. Row 61 remains 21/21 at both revisions; its exact `SUMMARY` differs only in `tool_sha` (`8131847bcfc5` → `9ddd596b98fb`), consistent with the changed tool blob. The registry row 49 selftest is red at both revisions (`cases=20 pass=0`): its documented relative `--tool tools/...` is resolved from the fixture's fixed `/var/tmp` working tree. Source `tests/fixtures/r29-registry-agreement.py:18-20,181-200` hardcodes that base, ignores TMPDIR, and removes only its child workdir. This command therefore violated the scratch-only boundary; I did not delete the fixed directory outside my scratch because its ownership/preexistence is unknown. Treat this row as a test-wiring limitation, not as valid scratch-isolated evidence. No R42-dependent delta was observed there. Rows 3, 22 and 24 also remain identically red/timeout (quarantine 58 failures; census-bounded 120 s timeout; proc-census 17 failures). `souji-proc-census` has an extra transient `/proc/.../status` stderr line at tip but the same rc0 and selftest summary.

Initial row-62/63 invocations omitted the required existing `--work` directory and failed at setup; both were rerun with per-revision scratch directories created first. The table shows only the corrected runs: r41 refusal-sites 21/21 and r41 drift-record-order 12/12 at both revisions. A first R42 C1 counter attempt used the bare shared clone as `--root` and returned `population=DRIFT` because the declared-evidence tool refused a bare root (`not the root of a git repository`); it was discarded. Re-running with the checked-out tip as `--root` returned the green result shown above.

## Literal command record

Variables for the explicit commands below: `L=/home/vgpnk/Projects/shokunin/souji-shokunin`, `BASE=bf618f6c5c09d302994871c94903abbea2deb60d`, `TIP=6a3f75941d3604e3459011d599c2c16f3a97b44c`. The 61 inherited command bodies are exactly those in `census/round-41/waves/w2/R41w2executor03/run-gates.py:14-77`; the runner call was `TMPDIR="$S/tmp" JOBS=4 python3 -B "$S/run_compare.py"`, where `S=/fast/scratch/hyaku/souji-r42/R42w3critic01`. It ran each body from the base and tip checkouts with the revision substituted and a distinct existing `$S/tmp/{base,tip}-NN` `TMPDIR`. The four added r41 command bodies were:

```sh
python3 -B census/round-41/c2-counter.py --root "$S/clone.git" --rev "$REV" --scratch "$SCR"
python3 -B tests/fixtures/r41-refusal-sites.py --tool tools/souji-worktree-drift.py --work "$SCR/refusal-work"
python3 -B tests/fixtures/r41-drift-record-order.py --tool tools/souji-worktree-drift.py --work "$SCR/order-work"
python3 -B census/round-41/c1-counter.py --root "$S/clone.git" --rev "$REV"
```
The refusal/drift fixtures were rerun with their `--work` directories created first; the table records those corrected runs. Tip-only runner call: `TMPDIR="$S/tmp/r42" python3 -B "$S/run_r42.py"`; its six commands appear as the r42 rows below. For exact C2 consumer runs, `S=/fast/scratch/hyaku/souji-r42/R42w3critic01`, `BASE=bf618f6c5c09d302994871c94903abbea2deb60d`, `TIP=6a3f75941d3604e3459011d599c2c16f3a97b44c`:

```sh
(cd "$S/base" && TMPDIR="$S/tmp/direct-base" python3 -B tools/souji-freeze-check.py --root "$S/base" --prereg census/round-41/preregistration.txt --rev "$BASE")
(cd "$S/tip" && TMPDIR="$S/tmp/direct-tip" python3 -B tools/souji-freeze-check.py --root "$S/tip" --prereg census/round-41/preregistration.txt --rev "$TIP")
(cd "$S/base" && TMPDIR="$S/tmp/selftest-base" python3 -B tools/souji-freeze-check.py --selftest)
(cd "$S/tip" && TMPDIR="$S/tmp/selftest-tip" python3 -B tools/souji-freeze-check.py --selftest)
```
The analogous two commands used `--prereg census/round-42/preregistration.txt`; base returned the absent-at-revision refusal and tip was clean. The C2 counters were run as `python3 -B census/round-41/c2-counter.py --root "$S/clone.git" --rev "$REV" --scratch "$SCR"` at both revisions and `python3 -B census/round-42/c2-counter.py --root "$S/tip" --rev "$TIP" --scratch "$S/tmp/r42/c2"` at tip. Tip-only C1/C3/R1 counter/fixture commands used the `SKILL.md` entries with `--root "$S/tip"`, their full revisions, and existing per-row scratch directories; observed output is reproduced verbatim in the table. Scratch paths here are command arguments only, not evidence pointers.

Discarded C1 setup command: `python3 -B census/round-42/c1-counter.py --root "$S/clone.git" --rev "$TIP" --scratch "$S/tmp/r42/c1"` (bare-root refusal; not the reported result). The corrected command uses `--root "$S/tip"`.

Audit commands were run literally as specified: `git -C "$L" diff --stat "$BASE" "$TIP" -- tests tools census/round-41`; `git -C "$L" diff --name-status "$BASE" "$TIP" -- tests tools census/round-41`; `git -C "$L" diff --numstat "$BASE" "$TIP" -- SCORECARD.md LOG.md`; `git -C "$L" diff --unified=0 "$BASE" "$TIP" -- SCORECARD.md LOG.md`; and the exact declared-evidence commands `python3 -B "$L/tools/souji-declared-evidence.py" --root "$L" --rev bf618f6c5c09d302994871c94903abbea2deb60d --file SCORECARD.md --format counts` and `python3 -B "$L/tools/souji-declared-evidence.py" --root "$L" --rev 6a3f75941d3604e3459011d599c2c16f3a97b44c --file SCORECARD.md --format counts`. Errata commands were `git -C "$L" log --oneline --reverse 3105a63b23481fccf7df58e74d14a6681e0ea0c8..6a3f75941d3604e3459011d599c2c16f3a97b44c`, plus `diff --name-status`, `diff --numstat`, and `show --format=fuller --unified=0` scoped to SCORECARD/LOG/round-42 lesson.

## C2 direct-consumer checks

| consumer/check | base | tip | identical? |
|---|---|---|:---:|
| `--prereg census/round-41/preregistration.txt --rev <revision>` | `rc=0 SUMMARY claims=3 findings=0` | `rc=0 SUMMARY claims=3 findings=0` | yes |
| `--selftest` | `rc=2`, old CLI requires `--root --prereg --rev` | `rc=0 SELFTEST cases=31 pass=31 fail=0` | expected new mode |
| `--prereg census/round-42/preregistration.txt --rev <revision>` | `rc=2 REFUSAL ... absent at bf618f6...` | `rc=0 SUMMARY claims=3 findings=0` | expected new prereg |
| r41 counter's consumer run | `rc=0`, 21/21, real ok, retro red, tool_sha `8131847bcfc5` | `rc=0`, 21/21, real ok, retro red, tool_sha `9ddd596b98fb` | behavior yes; exact digest differs |

Commands used for the direct rows were `python3 -B tools/souji-freeze-check.py --root <checkout> --prereg census/round-41/preregistration.txt --rev <revision>`, the same with `--selftest`, and the same with r42 prereg. `python3 -B census/round-41/c2-counter.py --root <shared clone> --rev <revision> --scratch <existing scratch>` exercised the 21 retained cases at both revisions. At tip, `python3 -B census/round-42/c2-counter.py --root <tip checkout> --rev 6a3f75941d3604e3459011d599c2c16f3a97b44c --scratch <existing scratch>` returned 37/37, both stubs rejected, real/retro/retro_clean ok/red/ok, selftest ok, patches 3/3.

## Calibration

Commands actually run:

- `python3 -B tools/souji-declared-evidence.py --root <lane> --rev bf618f6c5c09d302994871c94903abbea2deb60d --file SCORECARD.md --format counts` → `assertions=474 resolved=404 skipped=780 mismatches=70`, exit 1.
- Same command at `--rev 6a3f75941d3604e3459011d599c2c16f3a97b44c` → `assertions=492 resolved=422 skipped=814 mismatches=70`, exit 1.
- `git diff --numstat <base> <tip> -- SCORECARD.md LOG.md` → `LOG.md 12 0`; `SCORECARD.md 30 0`. The `--unified=0` diff contains only insertion hunks (`LOG.md @@ -1921,0 +1922,12`; `SCORECARD.md @@ -839,0 +840,30`); **no removed/base line**.
- Correct-root tip `r42-c1-counter`: exit 0, `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0`.

## Coverage and scoped file diff

Exact command: `git diff bf618f6c5c09d302994871c94903abbea2deb60d 6a3f75941d3604e3459011d599c2c16f3a97b44c --stat -- tests tools census/round-41`, followed by `--name-status`:

```text
 tests/fixtures/r42-drift-conditions.py | 223 +++++++++++++++++++++++++++++++++
 tools/souji-freeze-check.py            | 209 +++++++++++++++++++++++++-----
 2 files changed, 402 insertions(+), 30 deletions(-)
A tests/fixtures/r42-drift-conditions.py
M tools/souji-freeze-check.py
```

Judgment: the new r42 fixture is the intended C3 coverage addition; the modified freeze checker is the intended C2 operability addition; **no census/round-41 file and no prior drift fixture changed**. (The path filter does not include `census/round-42`.) Tip `r42-drift-conditions` returned `rc=0 SUMMARY cases=13 pass=13 fail=0`; tip `r42-c3-counter` returned `rc=0 SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247`. The lesson's existing N-C3c/E-1 load-sensitivity caveat still applies; this is one successful run, not a stability claim.

## Post-landing errata

`git log --oneline --reverse 3105a63b23481fccf7df58e74d14a6681e0ea0c8..6a3f75941d3604e3459011d599c2c16f3a97b44c` returned exactly `d39e3453` (honest-stop capture/errata) and `6a3f7594` (C1 marker wording). Scoped `--name-status`/`--numstat` over `SCORECARD.md LOG.md corpus/lessons/round-42.md`: SCORECARD `4 0`, lesson `25 0`, LOG absent; no base line changed. The last commit changes one line inside the newly appended lesson errata (“five CORRECTION-DE derived values” → “five correction lines' derived values”), not an older line. No non-errata base-line change was found in SCORECARD/LOG.

## Per-axis verdict

| axis | harmed or unchanged | evidence |
|---|---|---|
| calibration | unchanged | 70 mismatches at both revisions; SCORECARD/LOG append-only; corrected-root C1 counter green |
| operability | unchanged functionally; strict metadata equality differs | all 21 r41 cases pass both; all 37 r42 cases and 31 selftests pass; `tool_sha` is the expected changed tool identity |
| coverage | unchanged on prior fixtures | no prior fixture changes; old battery summaries match except noted non-harm differences; new 13-condition fixture/counter pass |

**Smallest safe correction:** none to the landed files. Keep the changed `tool_sha` and revision echoes as provenance; when auditing strict equality, compare these identity fields separately from findings. The only durable behavioral delta is the R1 pointer repair changing the landing-gate result from three findings to zero, which is favorable and does not trade away an owned axis.

Report: `.ufo/waves/round-42/w3/R42w3critic01.md`
