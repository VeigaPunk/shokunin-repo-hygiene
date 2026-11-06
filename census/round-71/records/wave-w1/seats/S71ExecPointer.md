# S71ExecPointer — r71 D3: pointer-check selftest (proposed replacement, lane file untouched)

Verdict: DELIVERED — proposed tool passes its own 4-case selftest (exit 0); two mutants make it fail (exit 1 each); normal mode reproduces both committed receipts byte for byte and is identical to the lane tool's output on the same inputs. Lane `tools/souji-pointer-check.py` not edited (sha256 2d325079…19d65, 92 lines); proposal sha256 8987a95c…ab822, 234 lines.

## Commands and deciding output
1. `python3 -B .ufo/waves/round-71/w1/S71ExecPointer/souji-pointer-check.py --selftest --work /fast/scratch/hyaku/souji-r71/S71ExecPointer/wst`
   → `CASE missing_path_detected PASS` / `CASE code_span_counted PASS` / `CASE clean_file_exit0 PASS` / `CASE bad_rev_exit2 PASS` / `SELFTEST cases=4 pass=4 fail=0`, rc=0.
2. Mutant `mutants/M1-invert-missing.py` (`elif not exists` → `elif exists`, one occurrence): selftest → `SELFTEST cases=4 pass=2 fail=2`, rc=1 (`missing_path_detected FAIL rc=1 EXIT=1 [SUMMARY files=1 checked=3 missing=2 …]`, `clean_file_exit0 FAIL` rc=1).
3. Mutant `mutants/M2-exit-always-zero.py` (`rc = 0 if missing == 0 else 1` → `rc = 0`): selftest → `SELFTEST cases=4 pass=3 fail=1`, rc=1 (`missing_path_detected FAIL rc=0 EXIT=0 [SUMMARY … missing=1]`).
4. Normal mode, r69 receipt inputs at `e063a2fcb3f5f3fb8fb19d2ae1592b1f22e6a333`: `corpus/lessons/round-69.md census/round-69/preregistration.txt` → `SUMMARY files=2 checked=59 missing=8 skipped=1 dead_declared=0` / `EXIT=1`; equals `census/round-70/records/pointer-check-r69.txt` (all 8 MISSING lines equal; `diff` empty).
5. Normal mode, r70 receipt inputs at `faac34e6d608df28504a7a584b661a4dcbd36588`: `corpus/lessons/round-70.md census/round-70/preregistration.txt corpus/knowledge/pathspec-env-scrub.md` → `SUMMARY files=3 checked=73 missing=0 skipped=3 dead_declared=3` / `EXIT=0`; equals `census/round-70/records/pointer-check-r70.txt`.
   Inputs were reconstructed: the receipts carry no invocation header; files=2/3 and checked=59/73 match only this file set, revs come from commit `3b7cce81`'s message.
6. Lane tool on the same inputs: identical stdout to items 4–5 (diff empty); the proposal changes no grammar.

## Selftest design (evidence in the file)
- Fixture per the fixture rule: `tempfile.mkdtemp(dir=--work)`, non-empty/dir check, `git init -q`, `rev-parse --show-toplevel` == fixture realpath, explicit `-c user.name/user.email` identity, every call `git -C <fixture>`; repo removed after the run unless `--keep`.
- Grammar read, not changed: backticks are not excluded by `TOKEN` (only `[A-Za-z0-9_./-]` lookbehind and the delimiter class), so the code-span path IS checked; `code_span_counted` pins `checked=3`, it does not assume exclusion. `:selftest` reaches `check()` via `sys.executable -B <self>`, so the asserted rc values are real process exits.
- Case set: mixed file (existing + missing + code-span existing) → missing=1/EXIT=1/rc=1 and `MISSING … missing.txt`; clean file → missing=0/EXIT=0/rc=0; `--rev abc123` → EXIT=2/rc=2, no SUMMARY.

## Findings
- **MEDIUM** `SCORECARD.md:181` says `pointer-check-r69.txt` shows "(5 missing, EXIT=1)". The committed receipt says `missing=8 checked=59` (and pre-final `3b7cce81^` already said 8). 5 missing/checked=49 is what the older checker bytes at `9167e02d` and `20c117ce` print on those inputs; the cell kept the pre-fix number after receipt regeneration and was not corrected by `170ecb65`.
- **LOW** Neither pointer receipt records `--rev` or the file list, so replay needs SUMMARY-count matching plus the commit message; add an invocation header (as `census/round-71/records/*` do).
- **LOW (hygiene, not D3)** The lane worktree changed under the wave (L1 activity, not mine): early snapshot ` M corpus/lessons/round-70.md`, `?? census/round-71/probes/attr-filemode-probe-sizechange.txt`; at close `?? corpus/lessons/round-71.md`. My writes are only under gitignored `.ufo/`.

## Risk
Selftest freezes today's grammar, including "code spans are counted"; if the L1 ever excludes fenced/code spans the assertion must move with the grammar, not silently.

## Files written (all under .ufo/waves/round-71/w1/S71ExecPointer/)
souji-pointer-check.py (proposal), selftest.txt, mutant-M1.txt, mutant-M2.txt, normal-r69.txt, normal-r70.txt, mutants/M1-invert-missing.py, mutants/M2-exit-always-zero.py. No installs; scratch `/fast/scratch/hyaku/souji-r71/S71ExecPointer` removed after copying.
