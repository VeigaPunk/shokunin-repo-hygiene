# R42w2reviewer10 — SKILL.md `r42-*` gate rows and bookkeeping against reality

Seat: R42w2reviewer10 (role: reviewer, leaf, no subagent dispatch). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Base `bf618f6c5c09d302994871c94903abbea2deb60d`; freeze `afe17f416eec04dcf3f480b580a8f928de61d19d`; attacked tip `3105a63b23481fccf7df58e74d14a6681e0ea0c8` (`git status --porcelain` empty before and after my work; no git mutation by this seat).
Judged on: operability. Milestone: r42 falsify the landed artifacts.

Receipts (captured by me, inside this seat directory): `.ufo/waves/round-42/w2/R42w2reviewer10/receipts/`. Files named below as `receipts/<name>.txt`.
Scratch: `/fast/scratch/hyaku/souji-r42/R42w2reviewer10/` (deleted before yield). No tool was installed or upgraded (python3 stdlib, `git`, `sha256sum`, `tar` only).

Method: each row's entry command was run at the tip (serially, to keep the C3 counter free of host load) and its exit code and SUMMARY compared with the row's verdict map. Controls were re-scored with `census/round-42/score-candidate.sh` in a scratch clone. Write scope was checked by watching the scratch root and `/tmp` while each counter ran (`TMPDIR` set, `--scratch` unset). The `../` pointers in `corpus/README.md` were resolved from `corpus/`.

## 1. Gate rows (`SKILL.md:287-292`)

| row | command run | observed | matches the row? |
|---|---|---|---|
| r42-c1-counter | `python3 -B census/round-42/c1-counter.py --root LANE --rev 3105a63b23481fccf7df58e74d14a6681e0ea0c8 --scratch <dir>` (receipt `receipts/c1-tip.txt`) | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0`, `EXIT=0` | **yes**. Verdict-0 line matches exactly with K=5. Control at instruments commit (`receipts/c1-base-control.txt`): `registered=0 class_ok=0 corrected=0`, `EXIT=1`, as the row's control cell says. Forged register via `score-candidate.sh c1 … census/round-42/c1-register.tsv=census/round-42/controls/c1-forged-register.tsv`: `registered=70 class_ok=42`, `EXIT=1`, matches. Refusal: bad rev → `COULD-NOT-EVALUATE`, exit 2; `TMPDIR` unset/`--scratch` absent → exit 2 (`receipts/refusal-exits.txt`, plus transcript). |
| r42-c2-counter | `python3 -B census/round-42/c2-counter.py --root LANE --rev 3105a63… --scratch <dir>` (receipt `receipts/c2-tip.txt`) | `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=9ddd596b98fb`, `EXIT=0` | **yes**. Control A (r41 tool, from `git show bf618f6…:tools/souji-freeze-check.py`, scored in a scratch clone): `cases=37 pass=24 fail=13 … selftest=FAIL patches=0/3`, `EXIT=1`. Control B (`controls/c2-stub-tool.py`): `selftest ok … patches=0/3`, `EXIT=1`. Both match the row's control cell. Absent tool path → `PRISTINE FAIL TOOL-ABSENT`, SUMMARY `fail=37`, `EXIT=1` (row lists absent tool under 1). Bad rev → exit 2. Scratch scope: one `souji-r42-c2.*` entry created under TMPDIR, none left, nothing new in `/tmp` (`receipts/c2-scratch-scope.txt`). |
| r42-freeze-check-selftest | `python3 -B tools/souji-freeze-check.py --selftest` (receipt `receipts/freeze-selftest.txt`) | `SELFTEST cases=31 pass=31 fail=0`, `EXIT=0` | **partly**. Exit and SUMMARY match (`n>=12`). Patched run matches the non-zero clause: `PYTHONPATH` with the C2 `sitecustomize` (P1), no `-I`: `SELFTEST cases=31 pass=3 fail=28`, `EXIT=1`. The Q105 scope statement also matches: the same patch with `-I` reads `pass=31 fail=0`, `EXIT=0` (`receipts/patched-selftest-probe.txt`). **Mismatch on write scope:** the row says "synthetic git repositories under TMPDIR". With `TMPDIR` valid, they are created under it. With `TMPDIR` unset or pointing at a missing directory, `tempfile.mkdtemp()` falls back to `/tmp`. Observed `/tmp/freeze-selftest-jvt5_2d_` (TMPDIR unset) and `/tmp/freeze-selftest-6zvrh0am` (TMPDIR missing), both removed at the end; the valid-TMPDIR case is `…/tmpok/freeze-selftest-2rx08p10` (`receipts/freeze-selftest-tmpdir.txt`). |
| r42-c3-counter | `python3 -B census/round-42/c3-counter.py --root LANE --rev 3105a63… --scratch <dir>` (receipt `receipts/c3-tip-1.txt`) | `SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247`, `EXIT=0` | **partly**. The target matches on this run and on four further tip runs (transcript, runs c3b, c3c, c3r4-6: all `EXIT=0`, `old_killed=0`). **But the verdict is not stable on identical bytes:** the first tip run (transcript only; no receipt file) gave `MUTANT E4 candidate=killed prior=r36-worktree-drift.py`, `old_killed=1`, `EXIT=1`. Mechanism: `killed()` counts any prior-fixture exit 1 with `fail>0` as a kill, so a load-sensitive r36 case failure is counted as a prior kill (see §3, F2). The row's verdict map ("0 / 1 target unmet") and its control cells say nothing about re-run stability. **Mismatch on `--survey`:** the row says "`--survey` prints which prior fixtures kill each mutant and is never a verdict". The flag is inert (`census/round-42/c3-counter.py:226` reads `if args.survey or True:`), and the printed prior-kill data is the `prior`/`old_killed` legs of the verdict. Controls cited in the row: always-pass stub `… survived=13 … prior=8/8 … equiv_killed=0 EXIT=1` (reproduced via `score-candidate.sh`, matches); byte-sniff stub `killed=13 … equiv_killed=6` (reproduced, matches on `equiv_killed=6`; that run also read `old_killed=1`, not mentioned in the row). Fixture-absent control: taken from `controls/c3-control.txt`, not re-run. Refusals: bad rev → exit 2; scratch not a directory → exit 2; tool absent at the root commit → `tool absent or sha256 differs`, exit 2. uid 0 not tested (seat is not root). |
| r42-drift-conditions | `python3 -B tests/fixtures/r42-drift-conditions.py --tool tools/souji-worktree-drift.py --work <dir>` (receipt `receipts/fixture-tip.txt`) | `SUMMARY cases=13 pass=13 fail=0`, `EXIT=0` | **partly**. Exit 0 and SUMMARY match. Kill path (exit 1 with `fail>0`) exercised through the C3 counter's 13 kills and the always-pass / sniff controls. **Mismatch on the pinned-value column:** the row says the sha256 is "recorded at landing". No record in the row or in `census/round-42/records/` pins it. The only place it appears is the wave-1 report `census/round-42/waves/w1/R42executor10.md:4` (`03392c7d…`). Observed `sha256sum tests/fixtures/r42-drift-conditions.py` = `03392c7d75daaec14f7ac03f8074dd489d8ac7c7efe1d17eb340d13c7f353f45`, which equals that report. **Verdict-map gap:** with `--work` missing, the fixture crashes with `FileNotFoundError` and exits **1**. The row's "1 = any case FAIL" does not cover this. Write scope otherwise holds: the work dir is `mkdtemp(dir=--work)`, `TMPDIR`/`HOME` are set to it, and it is removed (`receipts/fixture-tip.txt`; no `r42dc.*` left under `/tmp`). |
| r42-r1-counter | `python3 -B census/round-42/r1-counter.py --root LANE --rev 3105a63… --scratch <dir>` (receipt `receipts/r1-tip.txt`) | `SUMMARY findings=0 deleted=2 rows_added=0 stale=0`, `EXIT=1` | **yes (as stated red).** The verdict-0 line (`deleted=0 rows_added=3`) is not reached at the tip, and the row says so ("red by its letter"). Matches the row's own reading. Gate in both modes at the tip, `receipts/gate-plain.txt` and `receipts/gate-fleet.txt`: `SUMMARY findings=0 …`, `EXIT=0`. Base control (`receipts/r1-base-control.txt`): `findings=3 deleted=0 rows_added=0 stale=0`, `EXIT=1`, matches the R1 control. `corpus/pointer-exemptions.tsv` has zero diff between base and tip (`git diff --numstat` empty), so `rows_added=0` is the real state. Bad rev → exit 2 (transcript). |

## 2. Pinned sha256 values (`sha256sum` at the tip)

| path | row value | observed | matches? |
|---|---|---|---|
| `census/round-42/c1-items.tsv` | `b2601340eb20f70b0298542806acd47ef6e60586eacac92efdf94b1b231a8d39` | `b2601340eb20f70b0298542806acd47ef6e60586eacac92efdf94b1b231a8d39` | yes |
| `census/round-42/c1-counter.py` | `0ab07cd3c99e6bbe26220d9e36672b6a7acd45150b96fff1868d0e082dcd46aa` | same | yes |
| `census/round-42/c2-cases.tsv` | `148b7b87411eb282e0207cf5471d55be81e03d4a26ffafd96df37b4db4fd4511` | same | yes |
| `census/round-42/c2-counter.py` | `fa44392d11338daa73b3b4b9b2fc8f89879c099e9bf278d7b45fa55dea5d0ac1` | same | yes |
| `census/round-42/c3-mutants.tsv` | `2f6f8df39ed6dd66cda22806012b68db9e12712e5572931286daed60a4bab205` | same | yes |
| `census/round-42/c3-counter.py` | `bf0ebf4fef0cf0070daf2dd89184e83575bfabe4e4e82fa50511b3c6c8585d76` | same | yes |
| `tools/souji-worktree-drift.py` (pinned tool) | `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6` | same | yes |
| `census/round-42/r1-counter.py` | `f2dcbd06eecdb864e5ca215154aa82e564f7dbba586f617ad5543c0a811cc1bb` | same | yes |
| `census/round-42/sources/SHA256SUMS` (S259 snapshot) | `620581fe5440952a9b62554526f6fe613b030b2c7a1521e1e57495f22e5d546a` (lesson, S259 row) | `sha256sum -c` → `python-3-library-site.html: OK` | yes |
| `tests/fixtures/r42-drift-conditions.py` | no pin in row ("recorded at landing") | `03392c7d75daaec14f7ac03f8074dd489d8ac7c7efe1d17eb340d13c7f353f45` | **no pin** (see §1) |
| `tools/souji-freeze-check.py` | no pin ("not pinned at freeze") | `9ddd596b98fbf41b67f98a389c488b1e84d2ef4a7b5fdb0c8711451a007acec6` | consistent with row |

## 3. Controls paths, write scope, pointers

- **Controls exist at the tip:** `census/round-42/controls/{c1-control.txt, c1-forged-register.tsv, c2-control.txt, c2-stub-tool.py, c3-control.txt, c3-stub-allpass.py, c3-stub-sniff.py, r1-control.txt}`: all present. Every control cell's numbers were reproduced except the C3 fixture-absent control (not re-run; it is taken from `controls/c3-control.txt`).
- **Write scope:** all four counters refuse without a scratch directory (exit 2). With `--scratch` (or TMPDIR), every counter's scratch is created under it: C1 (`receipts/c1-tip.txt`, plus watch run), C2 (`receipts/c2-scratch-scope.txt`), C3 (scratch empty after all runs), R1 (`mkdtemp(dir=scratch)`, removed). Nothing left in `/tmp` attributable to any counter. The **exception** is the freeze-check selftest (§1, F1).
- **`corpus/README.md` `../` pointers:** 100 `../` pointers in total; 99 resolve from `corpus/`. The round-42 rows resolve: line 217 (`../census/round-42/jj-w1-reports/{JjTrialSouji.md, JjAuditSouji.md, SHA256SUMS}`) and line 819 (`../tests/fixtures/r42-drift-conditions.py`, `../census/round-42/c3-counter.py`, `../census/round-42/c3-mutants.tsv`, `../census/round-42/controls/c3-control.txt`, `../tools/souji-worktree-drift.py`). The one unresolved pointer is pre-existing, from round 21: line 365, `../census/round-21/read-count-{before,after}.json` (a brace pattern, not a literal path). See `receipts/survey-and-readme.txt`.
- **Bookkeeping command** (`SCORECARD.md` round-42 table, instrument at the tip, Q104): `python3 -B tools/souji-declared-evidence.py --root . --rev 3105a63… --file SCORECARD.md --format counts` → `assertions=490 resolved=420 skipped=810 mismatches=70`, `EXIT=1` (`receipts/declared-evidence-tip-and-measured-commit.txt`). The 70 base items are still present and are accounted by the register, with `new_mismatches=0` from C1. The base command (`--rev bf618f6…`) reads `assertions=474 resolved=404 skipped=780 mismatches=70` (`receipts/declared-evidence-base.txt`), matching the SCORECARD's stated base. Matches.
- **SCORECARD "measured at `5ad7046`" for C2/C3:** the landed bytes did not change between `5ad7046` and the tip for `tools/souji-freeze-check.py`, `tests/fixtures/r42-drift-conditions.py`, `tools/souji-worktree-drift.py`, `census/round-42/c2-counter.py` or `census/round-42/c3-counter.py` (`git diff --quiet` all no). The table's measured commit is accurate.

## 4. Findings, by severity

Each finding names the artifact it attacks. None edits a frozen file; each is a defect for the L1.

**F2 (high, operability). The C3 gate is non-deterministic on identical bytes, and the row says nothing about it.** Attacks: `r42-c3-counter` verdict map and the frozen counter's `prior=8/8` / `old_killed=0` legs.
- Pristine r36 under 12-way concurrency (no tamper, no mutant): batch A, 4×12 = 48 runs, two printed `case-read-only=FAIL changed=1` (runs `pr_2_10`, `pr_4_9`). Their exit lines are missing from my log (the log holds 46 lines, all `0`). Batch B, 5×12 = 60 runs, one run `r2_10` printed the same FAIL and recorded `rc=1` (`receipts/r36-probe/rc.txt` line `23:rc=1 run=2_10`; output in `receipts/r36-probe/r2_10-out.txt`). A mutant batch of 4×8 had one `case-read-only=FAIL` (`e4_4_8`, exit line missing from my log, 31 of 32 logged).
- Consequence on the tip: one of six counter runs with identical bytes gave `old_killed=1` and exit 1 (`MUTANT E4 … prior=r36-worktree-drift.py`). The row's target is exit-code based, so one run is a false red and the next a green.
- [INFERENCE] The mechanism is one cause, the read-only envelope case of r36 (`tests/fixtures/r36-worktree-drift.py:215`: `snapshot(fleet)` changes under concurrent load). The counter's `killed()` (`c3-counter.py`, `killed(res)`: `rc==1 and failed>0 and not crash`) counts any r36 case failure during a mutant run as a kill. The cause of the snapshot change is not identified.
- The C3 byte-sniff control also read `old_killed=1` (`score-candidate.sh c3 … c3-stub-sniff.py`, `EXIT=1`), so the flake reaches the controls too.
- Lesson N-C3b names the timing sensitivity. This seat adds the rate (about 2 in 48 and 1 in 60 under 12-way load; 1 of 6 tip runs) and the reproduction on the pristine tool.

**F1 (medium, operability). The freeze-check selftest's write-scope claim is false when TMPDIR is unset or missing.** Attacks: `r42-freeze-check-selftest` write-scope column; `tools/souji-freeze-check.py:319` (`tempfile.mkdtemp(prefix="freeze-selftest-")`, no `dir=`).
- Observed (`receipts/freeze-selftest-tmpdir.txt`): TMPDIR unset → `/tmp/freeze-selftest-jvt5_2d_`; TMPDIR missing → `/tmp/freeze-selftest-6zvrh0am`; TMPDIR existing → inside it. Each run cleans up, so nothing is left behind, but the write leaves TMPDIR. The row's "under TMPDIR" should read "under TMPDIR when it names an existing directory; otherwise `/tmp`".
- Every other counter refuses instead of falling back (exit 2); this one does not. Inconsistent with the C1/C2/C3/R1 counters.

**F3 (medium-low, operability). `--survey` is inert and the row mis-describes it.** Attacks: `r42-c3-counter` row (`[--survey] … never a verdict`); `census/round-42/c3-counter.py:226` (`if args.survey or True:`).
- The prior-fixture survey always runs and always prints. Its data is the `prior=` column and `old_killed`, which are verdict legs. Calling it "informational, never a verdict" is inaccurate in substance. Either the flag gates nothing, or the prior-kill data is a verdict leg; the row says the second, the code does the first.

**F4 (low, operability). The fixture's pinned-value cell is not a pin.** Attacks: `r42-drift-conditions` row (`sha256 (recorded at landing …)`).
- The value (`03392c7d…`) appears only in the wave-1 report `census/round-42/waves/w1/R42executor10.md:4`. Nothing in `census/round-42/records/` or the row pins it, so a later edit to the fixture would not show as a change to the pin.

**F5 (low, operability). The fixture's verdict map omits its own crash exit.** Attacks: `r42-drift-conditions` row (`1 any case FAIL`).
- `--work` missing (`/fast/…/NOPE`) gives `FileNotFoundError` and exit 1 (`r42dc` mkdtemp in a missing dir). The counter's `killed()` requires no traceback, so the crash is not a kill, but the row's exit-1 reading is wrong for this path.

**F6 (info). The R1 row's verdict-0 line is unreachable at the tip, and the row says so.** Attacks: `r42-r1-counter` verdict map. Observed `deleted=2 rows_added=0`. The row's own red reading is accurate. Not a defect of the row; listed so the L1 sees that the frozen R1 target is red.

**F7 (info). Pre-existing unresolved pointer.** Attacks: `corpus/README.md:365` (`../census/round-21/read-count-{before,after}.json`, brace pattern). Not a round-42 row, present since round 21.

**F8 (info). Count drift in the gate receipt.** Attacks: `census/round-42/records/gate-both-modes.txt` (`checked_reg=107` at `51f204f`). At the tip the same gate reads `checked_reg=113`, `findings=0` in both modes. The receipt names its own revision, so nothing is misstated, but a count quoted without the revision would drift.

## 5. Row verdicts

| row | verdict |
|---|---|
| r42-c1-counter | matches (command, exit, SUMMARY, controls, refusals, write scope, pins) |
| r42-c2-counter | matches (command, exit, SUMMARY, both controls, refusals, write scope, pins) |
| r42-freeze-check-selftest | partial: exit/SUMMARY/patched non-zero/Q105 scope match; write-scope claim false when TMPDIR is unset or missing (F1) |
| r42-c3-counter | partial: target and exit match on 5 of 6 tip runs; the verdict is not stable on identical bytes (F2); `--survey` is not a no-verdict option (F3) |
| r42-drift-conditions | partial: exit/SUMMARY match; no pin in the pinned-value cell (F4); crash exit not in verdict map (F5) |
| r42-r1-counter | matches its stated red reading; the verdict-0 line is not reached (F6) |

Unrun: C3 fixture-absent control (cited from its control file only); uid 0 refusal (seat is not root). Not forced: the counter's 300 s per-fixture timeout path, and loads above the 12-way concurrency used here.

Verdict: operability of the six rows is sound for the commands, exit codes, SUMMARY lines, controls and pins that are checkable. Three things are wrong and should go to the L1: the C3 target flips on identical bytes under load (F2), the freeze-check selftest's write-scope claim is not true when TMPDIR is absent (F1), and the `--survey` flag and its description disagree with the code (F3). The fixture's pin is absent from the row (F4).

## 6. Residual risk and verification gaps

- F2 is measured with a small sample (6 tip runs, 1 flake; 2+1 failures in 108 concurrent pristine r36 runs). A longer serial/parallel sweep would tighten the rate; I did not run one.
- The cause of the r36 read-only snapshot change is not identified (F2 mechanism is an inference).
- The first tip-run receipt (old_killed=1) is quoted from the session transcript, not a file in `receipts/`.
- No count in this report was re-measured by the L1; the counters' scores are advice, per the preregistration rule 2.

## 7. Cleanup

Scratch `/fast/scratch/hyaku/souji-r42/R42w2reviewer10/` removed before yield. Two of my own `/tmp` files were removed (`/tmp/watch_selftest.py`). Three pre-existing `/tmp/st.{err,out,txt}` files predate this session and are not mine; left alone.
