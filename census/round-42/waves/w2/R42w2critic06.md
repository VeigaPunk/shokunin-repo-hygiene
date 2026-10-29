# R42w2critic06 — attack on the C2 patches leg and the landed `--selftest`

Seat: R42w2critic06 (critic, leaf, no subagents). Attacks: the frozen C2 patches leg (`census/round-42/c2-counter.py`, `SITECUSTOMIZE`, `run_selftest`, the `patches` line) and the landed `tools/souji-freeze-check.py --selftest` at tip `3105a63b23481fccf7df58e74d14a6681e0ea0c8` (base `bf618f6c5c09d302994871c94903abbea2deb60d`, freeze `afe17f416eec04dcf3f480b580a8f928de61d19d`).

Landed bytes read by `git show 3105a63b23481fccf7df58e74d14a6681e0ea0c8:tools/souji-freeze-check.py` into scratch: sha256 `9ddd596b98fbf41b67f98a389c488b1e84d2ef4a7b5fdb0c8711451a007acec6`, identical to the working-tree file. Nothing in the lane, the fleet, `.ufo/state`, or any tracked file was written. No tool installed or upgraded (host `python3` 3.14.8, `git` 2.56.0 used as found; no pacman, uv or npm action). Scratch `/fast/scratch/hyaku/souji-r42/R42w2critic06` was removed before this report was written; every number below is in `receipts/` in this seat, and the seat-local scripts (`build-candidates.py`, `probe-patches.py`) rebuild the scratch inputs from `git show 3105a63…:tools/souji-freeze-check.py` into a `landed/` subdirectory.

## Verdict

1. **The patches leg reaches its target with a self-test that is not a self-test.** Three of six new candidates reach `cases=37 pass=37 fail=0 … selftest=ok patches=3/3` (exit 0): T1 runs twelve stdlib known-answer checks and never calls this tool's digest, freeze, ancestry or grammar code; T2 and T3 are presence tripwires (`find_spec("sitecustomize")`, `"sitecustomize" in sys.modules`) that print a literal summary otherwise. The leg counts any non-zero patched exit (`c2-counter.py:410`), so a self-test that exits non-zero because the environment looks patched satisfies it. **C2 patches leg: FAIL as a measure of "the self-test exercises the tool's logic".**
2. **The leg also rejects honest tools by primitive choice.** T4 (git via `subprocess.Popen`, real self-test 31/31, grammar 37/37) reads `patches=1/3`; T5 (ancestry via `git rev-list`, real logic) reads `patches=2/3`; T6 (self-test reloads `hashlib` and `subprocess` to the stdlib originals, then runs the full real self-test 31/31) reads `patches=0/3`. All three exit 1 under the counter.
3. **The landed tool's self-test does detect P4–P7, but for three different reasons.** P4 (constant digest) and P5 (`git cat-file` raises) are caught by the tool's own digest and blob paths. P6 (`os.path.exists` always True) is caught only by the harness's own `os.makedirs` in the fixture writer: the tool never calls `os.path.exists`. P7 (`re.match` → None) is caught by the stdlib `argparse` before any self-test case runs: no `SELFTEST` line is printed. Statement coverage of `--selftest` is 207/224 line events (92.4%); 17 lines are never executed (13 executable, 4 docstrings).
4. **The landed tool does not trip on mere presence.** P0 (an unpatched `sitecustomize` loaded via PYTHONPATH) exits 0 with `SELFTEST cases=31 pass=31 fail=0`; T2 and T3 fail that same control (see Table 1).

## Table 1 — candidates (seat-local; `score-candidate.sh c2 <scratch> tools/souji-freeze-check.py=<cand>`)

Each candidate is the landed bytes with one region replaced (`diffs/<name>.diff`; the grammar is untouched). Receipts: `receipts/score-<name>.txt`.

| candidate (file) | SUMMARY or exit (verbatim) | reaches target / rejected honestly? | what it attacks |
|---|---|---|---|
| landed `3105a63` (baseline, `receipts/score-landed-3105a63.txt`) | `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=9ddd596b98fb` ; exit 0 | target (the landed artifact measures at target) | baseline |
| T1 `cand-T1-kat-stdlib.py` (`score-T1-kat-stdlib.txt`) | `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=5a8f8456f642` ; exit 0 | **reaches target.** `--selftest` prints `SELFTEST cases=12 pass=12 fail=0` from twelve stdlib checks (FIPS 180 sha256 vectors; `git log --diff-filter=A` and `git merge-base --is-ancestor` on a fixture repo, called as `subprocess.run`). It calls none of this tool's digest, freeze, ancestry or grammar functions: coverage `evaluate 0/41`, `check_path_sha 0/20`, `dispatch_findings 0/21`, `parse_claims 0/18`, `freeze_rev 0/3`, `Repo.run 0/3`, `selftest_case 0/28` (`receipts/probe-buckets-candidates.txt`) | patch leg counts any non-zero exit; a stdlib-only self-test is accepted |
| T2 `cand-T2-find-spec-tripwire.py` (`score-T2-find-spec-tripwire.txt`) | `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=9a4cfe253d73` ; exit 0 | **reaches target.** Refuses (`SELFTEST cases=31 pass=0 fail=31`, exit 1) iff `importlib.util.find_spec("sitecustomize") is not None`; otherwise prints `SELFTEST cases=31 pass=31 fail=0`. No case runs; coverage `selftest 4/6`, tool functions 0. It also fails the unpatched-presence control (P0 rc 1, `receipts/probe-sitecustomize-presence.txt`) | presence of the injection module, not the injected effect; no P0 control in the frozen leg |
| T3 `cand-T3-sysmodules-signal.py` (`score-T3-sysmodules-signal.txt`) | `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=bed2ae4ec682` ; exit 0 | **reaches target.** If `"sitecustomize" in sys.modules`, `signal.raise_signal(SIGTERM)` (the counter reads rc −15, which is not 0 or 124, and counts it); otherwise prints the literal 31/31 line. Reads no environment variable. The unpatched-presence control also reads rc −15 (`probe-sitecustomize-presence.txt`) | crash-as-detection (signal exit); presence not effect |
| T4 `cand-T4-popen-honest.py` (`score-T4-popen-honest.txt`) | `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=1/3 tool_sha=708e6f3a200a` ; exit 1 | **rejected honestly.** `Repo.run` uses `subprocess.Popen` + `communicate`. The real self-test runs 31/31 clean and the grammar 37/37. P2 and P3 replace `subprocess.run` only, so the real `git log --diff-filter=A` and `merge-base` results are untouched and the leg sees no effect under P2/P3 (probe: P2 rc 0, P3 rc 0) | leg keyed on the function name `subprocess.run` |
| T5 `cand-T5-revlist-ancestry-honest.py` (`score-T5-revlist-ancestry-honest.txt`) | `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=2/3 tool_sha=e433d1dadd24` ; exit 1 | **rejected honestly.** `is_ancestor` = `git rev-list <b>` membership (no `merge-base`). Real self-test 31/31 clean. P3 (`merge-base` argv) has nothing to replace: rc 0 | leg keyed on the spelling `merge-base` in argv |
| T6 `cand-T6-reload-restore-honest.py` (`score-T6-reload-restore-honest.txt`) | `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=0/3 tool_sha=08fe47f23252` ; exit 1 | **rejected honestly.** The self-test starts with `importlib.reload(hashlib)` and `importlib.reload(subprocess)`, restoring the originals, then runs the full real self-test 31/31. P1–P3 all rc 0 | a self-test that refuses to be patched scores 0/3 |

Scores for the six candidates were taken with `bash census/round-42/score-candidate.sh c2 /fast/scratch/hyaku/souji-r42/R42w2critic06 tools/souji-freeze-check.py=<file>` (exit codes in each receipt: `exit=0` for T1–T3, `exit=1` for T4–T6). The counter's own patch legs on each candidate (P0–P3, `receipts/probe-patches.txt` section C) match the SUMMARY `patches=` figures.

## Table 2 — the landed tool's `--selftest` under patches

Landed bytes `9ddd596b98fb…` (sha256 `9ddd596b…acec6`). P1–P3 are the counter's own (`run_selftest(tool, scratch, patch)`, `receipts/probe-patches.txt` A2). P4–P7 are written here: `sitecustomize` on PYTHONPATH, `SOUJI_R42W2_PATCH` selects one, and the module appends `loaded <P>` to a marker file, so each run is proven to have loaded its patch (`receipts/probe-patches.txt` A1, `receipts/p7-mark.txt`). Each run is `python3 -B <tool> --selftest` with a whitelisted environment and a private TMPDIR.

| patch on the landed `--selftest` | exit | last stdout line | what fails | detected by |
|---|---|---|---|---|
| P0 control (sitecustomize loaded, no patch) | 0 | `SELFTEST cases=31 pass=31 fail=0` | none | — |
| P1 sha256 digests reversed (counter) | 1 | `SELFTEST cases=31 pass=3 fail=28` (counter summary `(31, 3, 28)`) | digest cases | the tool's `hashlib.sha256` in `check_path_sha` (line 166) |
| P2 `git log --diff-filter=A` returns nothing (counter) | 1 | `(31, 2, 29)` | freeze cases → `Refusal` | `freeze_rev` |
| P3 `git merge-base` always fails (counter) | 1 | `(31, 5, 26)` | ancestry cases | `is_ancestor` |
| **P4** `hashlib.sha256` returns a constant `0`*64 (seat) | 1 | `SELFTEST cases=31 pass=3 fail=28` | `selftest FAIL clean`, `dispatch-after`, `notes-before`, …, `counter-digest`, `population-digest` | the tool's digest (line 166) |
| **P5** `subprocess.run` raises `OSError` for every `git … cat-file` (seat) | 1 | `SELFTEST cases=31 pass=2 fail=29` | `selftest FAIL clean`, `base-unresolved`, `base-not-ancestor`, `counter-missing`, … | `Repo.blob` → `Repo.run` `except OSError` → `Refusal` (line 72) |
| **P6** `os.path.exists` always True (seat) | 1 | `SELFTEST cases=31 pass=25 fail=6` | `selftest dispatch-after: FileNotFoundError …/.ufo/waves/round-7` (and `notes-before`, `dispatch-before`, …) | **not the tool**: the tool never calls `os.path.exists` (grep of the landed file: none). The harness's `os.makedirs(…, exist_ok=True)` skips parent creation and the fixture write fails |
| **P7** `re.match` always None (seat) | **2** | *(none: no `SELFTEST` line)* | `usage: souji-freeze-check.py … error: argument --selftest: expected 0 arguments` (`receipts/p7-stderr.txt`) | **not the tool**: stdlib `argparse` calls `_re.match` (`/usr/lib/python3.14/argparse.py:2398`, `:2424`); no self-test case runs |

Reading: P4 and P5 measure the self-test's own logic. P6 and P7 exit non-zero for reasons outside the tool's code; under the frozen leg's rule (`p_rc not in (0, 124)`) P7 would count as a detection exactly like a real logic failure. The seat run of the same P1–P3 through the counter returns the same codes as its SUMMARY.

## Table 3 — how much of the landed tool the self-test executes

Statement line-events of the landed tool in-process under `sys.settrace`, `--selftest` only (`receipts/probe-patches.txt` B; per-bucket table `receipts/probe-buckets-candidates.txt`; hit/total per bucket):

| bucket | landed | T1 | T2 | T3 | T4 | T5 | T6 |
|---|---|---|---|---|---|---|---|
| `main` | 29/33 | 8/33 | 8/33 | 8/33 | 29/33 | 29/33 | 29/33 |
| `selftest` (own body) | 11/14 | 40/40 (own body) | 4/6 | 4/5 | 11/14 | 11/14 | 14/17 |
| `selftest_case` | 28/28 | 0/28 | 0/28 | 0/28 | 28/28 | 28/28 | 28/28 |
| `evaluate` | 41/41 | 0/41 | 0/41 | 0/41 | 41/41 | 41/41 | 41/41 |
| `check_path_sha` | 17/20 | 0/20 | 0/20 | 0/20 | 17/20 | 17/20 | 17/20 |
| `dispatch_findings` | 19/21 | 0/21 | 0/21 | 0/21 | 19/21 | 19/21 | 19/21 |
| `parse_claims` | 17/18 | 0/18 | 0/18 | 0/18 | 17/18 | 17/18 | 17/18 |
| `freeze_rev` | 3/3 | 0/3 | 0/3 | 0/3 | 3/3 | 3/3 | 3/3 |
| `Repo.run` | 2/3 | 0/3 | 0/3 | 0/3 | 5/6 | 2/3 | 2/3 |
| `Repo.blob` / `Repo.commit` | 3/4, 3/4 | 0/4, 0/4 | 0 | 0 | 3/4, 3/4 | 3/4, 3/4 | 3/4, 3/4 |
| `Repo.is_ancestor` | 1/1 | 0/1 | 0 | 0 | 1/1 | 2/2 | 1/1 |
| **total** | **207/224** | **77/250** | **41/216** | **41/215** | 210/227 | 208/225 | 210/227 |

Landed statements never executed by `--selftest` (line numbers of `tools/souji-freeze-check.py` at 3105a63): L72 `Repo.run` `raise Refusal` (the OSError path, reached only by P5); L82 `Repo.blob` `return None` (NUL path); L128 `dispatch_findings` `FIELD-MISSING Round` (no Round line); L133 `return []` (git log failure); L156 `check_path_sha` `return None` (empty path); L165 `no sha256=<64 hex>` finding; L326, L327, L329 the self-test failure branch; L347 `ap.error`; L350, L352, L362 the three `Refusal` branches of `main`. Docstrings not executed: L75, L95, L152, L234 (counted as statements by the AST walk).

## Table 4 — the frozen leg's own gate (what it accepts and why)

- `c2-counter.py:410` `patches += 1 if (selftest == "ok" and p_rc not in (0, 124)) else 0`: the patched run need not print a SELFTEST line, need not run a case, and need not fail for the patch's reason. Any exit except 0 or 124 counts, and `selftest == "ok"` is read from the unpatched run only. P7 (rc 2, no output) and T3 (rc −15, no output) are counted as detections.
- `c2-counter.py:298-328` `SITECUSTOMIZE`: P1 patches the name `hashlib.sha256`; P2 and P3 patch `subprocess.run` and match the argv tokens `'--diff-filter=A'` and `'merge-base'`. Anything that uses another function (`Popen`, `check_output`, `os.popen`), another spelling (`rev-list`), or restores the stdlib (`reload`) is invisible to the patch: T4, T5, T6.
- No P0 control exists in the frozen leg, so a presence-only tripwire is indistinguishable from a patch-effect detector (T2, T3 vs the landed tool, Table 1 and `probe-sitecustomize-presence.txt`).

## Commands actually run (all in this seat, from the lane root, `S=/fast/scratch/hyaku/souji-r42/R42w2critic06`)

1. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --show-toplevel` → the lane root; `git show 3105a63b23481fccf7df58e74d14a6681e0ea0c8:tools/souji-freeze-check.py > $S/landed/souji-freeze-check.py`; `sha256sum` of it and of the working-tree file → both `9ddd596b98fbf41b67f98a389c488b1e84d2ef4a7b5fdb0c8711451a007acec6`.
2. `bash census/round-42/score-candidate.sh c2 $S tools/souji-freeze-check.py=$S/landed/souji-freeze-check.py` → `SUMMARY cases=37 pass=37 … selftest=ok patches=3/3 tool_sha=9ddd596b98fb` (17 s). Re-run with exit captured: `receipts/score-landed-3105a63.txt` ends `exit=0`.
3. `python3 -B build-candidates.py` → six candidates, `ast.parse` ok for each; `diffs/*.diff` line counts: T1 73, T2 31, T3 30, T4 18, T5 12, T6 12.
4. Six parallel `score-candidate.sh c2 $S tools/souji-freeze-check.py=<cand>` (`receipts/score-T1…T6`, 50 s wall for the batch).
5. `python3 -B probe-patches.py cand-T1…T6.py > receipts/probe-patches.txt` (72 s): the landed patch table, coverage, and each candidate under P0–P3.
6. P7 and the argparse reference: `env -i PATH=/usr/bin:/bin LC_ALL=C TMPDIR=$W HOME=$W PYTHONPATH=$S/p7 SOUJI_R42W2_PATCH=P7 SOUJI_R42W2_MARK=$S/p7/mark.txt python3 -B $S/landed/souji-freeze-check.py --selftest` → rc 2, `error: argument --selftest: expected 0 arguments`; the same environment with `P0` → `SELFTEST cases=31 pass=31 fail=0`, rc 0; `grep -n "_re.match" /usr/lib/python3.14/argparse.py` → lines 2398, 2424.
7. Per-bucket coverage (`receipts/probe-buckets-candidates.txt`) and the presence control (`receipts/probe-sitecustomize-presence.txt`) by importing `probe-patches.py` with `importlib` (`-B`).
8. `rm -rf -- /fast/scratch/hyaku/souji-r42/R42w2critic06` (scratch removed; `test ! -e` confirmed).

Limits of this measurement: `probe-patches.py` coverage is line events (not branch coverage) of the in-process `--selftest` run; the `selftest` bucket differs in size between landed (14 statements) and T1 (a different body), so its row is not a like-for-like comparison. P6 and P7 are single-shot runs; they were not repeated under load (`R42executor09` records load-sensitive kills elsewhere in this round).

## Named limits for the round lesson (C2; none edits a frozen file)

- **N-C2d (new):** the patches leg has no P0 (presence-only) control. Presence tripwires reach `selftest=ok patches=3/3` (T2 `find_spec`, T3 `sys.modules` + SIGTERM). The landed tool passes the same P0 control (rc 0), so the landed tool is not a presence tripwire; the leg cannot tell the two apart.
- **N-C2e (new):** a stdlib known-answer self-test reaches the target and runs none of the tool's grammar, digest, freeze or ancestry functions except the `main` argv dispatch (T1: `evaluate 0/41`, `check_path_sha 0/20`, `freeze_rev 0/3`). The leg does not require any tool function to run.
- **N-C2f (new, honest rejections):** a correct tool using `subprocess.Popen` for git (T4: `patches=1/3`), `git rev-list` for ancestry (T5: `patches=2/3`), or a self-test that restores the stdlib before it runs (T6: `patches=0/3`) is rejected while its self-test is real and passes 31/31. The leg keys on the name `hashlib.sha256`, the function `subprocess.run`, and the argv tokens `--diff-filter=A` and `merge-base`.
- **N-C2g (new):** on the landed tool, P6 and P7 are detected outside the tool. P6 by the harness's `os.makedirs`; P7 by `argparse` before the self-test starts (no `SELFTEST` line, no case run). The frozen leg counts both (`p_rc` 2 and 1 are not 0/124), so the patch table does not show that the tool's own logic detects them.
- **N-C2h (new, coverage):** landed `--selftest` executes 207/224 statement line events (92.4%). The never-executed statements are the Refusal branches of `main`, the OSError path of `Repo.run`, the no-Round branch, the no-`sha256=` branch, and the self-test's own failure branch (Table 3 list).
- **N-C2b extended (sentinel's env tripwire):** the presence of the injection module is enough: T2 and T3 need no env var and no patch effect; the signal exit is a detection by the leg's rule.

## Mistakes and fixes (for the L1, not applied)

- The C2 counter is frozen; none of the above edits it. The named limits are the answer for the lesson, and the landed tool is not changed.
- Table 2 is the landed tool's patch table. The counter's own P1–P3 are measured there on the landed bytes (A2); those figures are only a re-measurement and are not compared against the lane's `census/round-42/records/c2-after.txt`.

## Verdict

**FAIL (falsified) for the patches leg as a measure of self-test strength.** Evidence: T1, T2, T3 reach `selftest=ok patches=3/3` with exit 0 and exercise none or almost none of the tool's logic (Table 1, Table 3); T4, T5, T6 are honest and rejected 1/3, 2/3, 0/3 (Table 1); on the landed tool, P4 and P5 are caught by the tool's own logic, while P6 and P7 are caught by the harness and `argparse` (Table 2). The landed tool itself passes its own P0 presence control (rc 0).

Checks for the main agent after all subagents land: `python3 -B census/round-42/c2-counter.py --root . --rev 3105a63b23481fccf7df58e74d14a6681e0ea0c8 --scratch <scratch>` (expect target, unchanged); this seat's candidates are not to be landed.
