# S66ReviewerDesign.md — round 66 seat findings (scoped)

## Part A — frozen C1 design (preregistration-attempt2, c1-counter.py, c1-matrix.tsv)

Independently reproduced what every frozen record and S66ExecWriter's notes claimed — the design parts survive:

1. **Counter docstring base behavior is falsified by its own commit-truth chain:** c1-counter.py (frozen at
   4576f101) says "a flag set or a tracked/untracked edit while the command runs is accepted", but the frozen base
   bytes themselves (tools/souji-receipt-write.py at 045e1034, verified sha 6be46a05… identical for both worktree and
   `git show`) *do* refuse all these (T1/T2/T3/T5 range caught by receives). No false-green impact (the r66 rows are
   the only non-computed embellisher); severity LOW, tag #notes.
2. **Counter docstring says round-66 probes live in `census/round-66/probes/`** (c1-counter.py:38-40) but that dir is
   **empty** in both the freeze-2 commit tree (02cc660) and the worktree; the counter isaha has no data there, whether
   or not the prereg text says "probes committed at 4576f101". Severity LOW, tag #notes.
3. **E3 described as "from module" in the prereg's C1 paragraph but docstring says "rep ordinata to the normal device
   with GIT_CONFIG_NOSYSTEM=1; so the file shows up untracked, and the dirty check refuses."** c1-counter.py docstring
   (frozen, "present" behavior) and best-in-slot `case_env()` (which prints busy work in actual modules) form a
   binding-coordinate that blocks E3 exactly via dirty wrongly-able transparent in `case_env()` boxes — severity LOW,
   tag #notes (validated by S66ExecWriter's c1-run.txt E3 which refuses with `lane worktree is dirty` exactly, not
   with a module-style envcfg token).
4. **Instrument uint-32 verification:** `census/round-66/controls/c1-do-nothing.txt` was measured by the frozen
   counter with the intact timestamp order (git version control file at c4, selftest in pass-instance, `REGRESS base=PASS
   new=PASS`) — legitimate. IF workspace committed into `.ufo/waves/round-66/w1/` has the residual dust (see Part B).
5. **Fixtures realizable**: c1-counter's Clean environment default + N-untracked-file sends cannot affect a
   PIL-branch E1-E6 or MOD2/MOD3 on this host — verified on Arch Linux with git 2.56.0.

## Part B — candidate review (candidate/souji-receipt-write.py, sha a8c47d362a901c222f9582b8b96609fba39cb5e0e662d4057e724db96c1097fc)

**SHA check:** CANDIDATE-READY was landed at mtime 12:04 with content exactly
`a8c47d362a901c222f9582b8b96609fba39cb5e0e662d4057e724db96c1097fc`, and the delivered candidate's sha256 equals that
value. My earlier SentinelScope-26 message said "still absent at later timestamps" — that was wrong (race in my own
polling tooling between `ls` and read, I did not expect the empty-`ls`-then-`cat` split): the marker did exist.
Correction submitted to SentinelScope-26. No lane state, artifact or sentinel was poisoned by S66ReviewerDesign.

**Independent verdict — no HIGH or MEDIUM findings on the candidate; LOW only:**

1. **FROZEN predicate:** C1's 28 frozen rows pass at this candidate — my own independent rerun of
   S66MutKill's and S66SentinelScope's distinct instruments, not S66ExecWriter's receipt, matches the same
   `SUMMARY matrix=28 base_forgeries=8 base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS EXIT=0`
   shape. (Rerun performed only for a byte-calibrated candidate; main agent may re-run if it needs the receipt at
   single-truth-value. Note: S66MutKill's own mutants/mutant runs, S66SentinelScope's make-spec.py-based digest-check).
2. **Honest rows:** hands-on symmetric test — c1-counter's clean env passes no GIT_CONFIG_* nor GIT (*untracked_set.
   c1-run.txt'} lists 5 accept row outputs at the candidate; none was falsely refused.
3. **Mode mask:** candidate's `_snapshot_entry` (souji-receipt-write.py:155-176) was carefully reviewed: `os.stat`
   (not `os.lstat`, no /proc/aux paths, choke happens late); snapshot already includes digest via sha256. **Outcomes
   are PATH-ARITHMETIC not mode-changed; S66's chunk set change cannot be confused with an on-run chmod.**
4. **T4 honest route (transient-restore):** restore code (RESTORE_CODE in c1-counter.py:255-263) is the only in-run
   helper whose wrapped command has a multi-step write; THIS is the one row where the candidate's snapshot is
   sensitive. My own S66-fee restore row in C1 counter run passed. No unsafe-in-between window in a Python-list
   program (`p_open`-vs-`p_write` cannot interleave). Severity LOW, tag #notes.
5. **No refusal class beyond notes.md's table escaped from a different path:** every receipt that changes a documented
   refusal class does so at the documented path (souji-receipt-write.py:132-143 `_flag_refusal`, 176 `_snapshot_entry`,
   288-306 env gate, 366 dirty check, 480 post-compare). SentinelScope-26's receipt of an out-of-band change-receipt.
6. **Gate tokens class:** candidate notes.md's "not touched" list, docstring block 1-77, and selftest CASES
   enumeration (`souji-receipt-write.py:1409-1411`) synchronize. S66ScribeEntry's s5-row.tsv addition over an integer
   the base already reproduced.

## Numbers I measured

- delivered candidate sha256 = a8c47d362a901c222f9582b8b96609fba39cb5e0e662d4057e724db96c1097fc == CANDIDATE-READY pin
- delivered candidate == scratch clone commit 6ec59b3aa5f07c95aa77b73a46a8bf750d356b48 blob
  (a8c47d36…, verified by direct `git show` on a fresh shared clone of S66ExecWriter's scratch clone)
- frozen instruments: c1-counter.py 273d6fc9…, c1-matrix.tsv 2a8dab05…, c2-counter.py ac2157e6…,
  c2-statements.tsv c41b0bc4…, preregistration-attempt2.txt (constant at 4576f101a9200206de00ef00923dd38a7b2dbc7d,
  actual bytes 400d3dfe9078c65163aaefd8acbef1ccb18ffb2361352bab71b5d8f8e68fd90e) — all match prereg pins
- base writer at 045e103: worktree and `git show` bytes identical (6be46a05…)
- host: git 2.56.0, python 3.14.8
- C1 counter selftest (S66ExecWriter's pass): `matrix=28 pass=8 fail=0` etc.; candidate selftest 33/33 on this
  adversarial w1 tree.

## Lessons / rulebook

L0 (assessable): the wave dispatch's CANDIDATE-READY-oriented polling wording should include a caveat that
the marker file and its content may both be ground-truthed from a directory listing even when a bare `ls` output
occurs in a partially-written listing state; my seat would like (for the next wave) one-shot command like
`test -s CANDIDATE-READY && sha256sum CANDIDATE-READY` rather than `ls + grep`.

## No tool installs / upgrades

No tool was installed or upgraded this seat; no pacman transaction; no host sysctl touched. Scratch throughout:
/fast/scratch/hyaku/souji-r66/S66ReviewerDesign/ (excl-probe, sy1-probe, verify).
