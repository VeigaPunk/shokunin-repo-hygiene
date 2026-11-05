# S68MutTester: mutation test of the round-68 C1 counter

Frozen files were read only. Hashes after the runs: `census/round-68/c1-counter.py` = ab3ac5c7…, `c1-matrix.tsv` = bb56e69c… (unchanged). All mutants were built and run in scratch (`/fast/scratch/hyaku/souji-r68/S68MutTester/`, deleted before yield). The lane was not modified.

## Baseline (pristine scratch copy)
- Copy sha256: counter ab3ac5c78a623c145e768ffb0c233e9f65a892a78431de44790187da3fdb37f0, matrix bb56e69cf…(42 rows). Identical to frozen.
- Selftest of the copy: `SELFTEST cases=8 pass=8 fail=0`, `EXIT=0`, identical to `controls/r68-selftest.txt`.
- Pristine candidate, clean env (`run-r0a-clean.log`): `SUMMARY matrix=42 base_forgeries=2 base_honest=11 new_forgeries=0 new_honest=11 class_mismatches=0 regress=PASS`, `EXIT=0`.
- Pristine candidate, ambient env (`run-r0b-ambient.log`): same SUMMARY, `EXIT=0`. Flips = 0.
- Frozen C1 target and C2 after-arm are met by the unmodified copy.

## Mutants (single edit each; diffs in `mut-*.diff` in this directory)

### (a) remove the W5 cwd rule
```
-        cwd = (os.path.dirname(b_repo) if spec.get("cwd_parent")
-               else os.path.join(b_repo, ".git") if spec.get("cwd_gitdir") else None)
-        cwd_n = (os.path.dirname(n_repo) if spec.get("cwd_parent")
-                 else os.path.join(n_repo, ".git") if spec.get("cwd_gitdir") else None)
+        cwd = os.path.dirname(b_repo) if spec.get("cwd_parent") else None
+        cwd_n = os.path.dirname(n_repo) if spec.get("cwd_parent") else None
```
Commands: `TMPDIR=$S/tmp python3 -B $S/mut-a-counter.py --root <lane> --matrix $S/c1-matrix.tsv --base-rev 3639087917eaeb28719d7603110a6ec22782100e --rev f70da577eb1e1624cc63ab8fd0468565927d9b6a --tool tools/souji-receipt-write.py --work $S/work-r1a` (clean), and the same under `env GIT_COMMON_DIR=/nonexistent-r68-probe GIT_NAMESPACE=r68probe GIT_CEILING_DIRECTORIES=/nonexistent-r68-probe` (ambient).
Observed: clean `EXIT=0`, ambient `EXIT=0`; SUMMARY identical to pristine; `# detail W5` lines identical to pristine (base and new stderr `RECEIPT-ENV-COMMONDIR-MISMATCH` unchanged). Flips 0.
Rows affected: none. W5's writer refusal occurs before any git call, so the writer's cwd has no effect on the verdict.

### (b) remove `mode_change` from the W4 spec
```
-            "repo_name": "main", "cwd_parent": True, "mode_change": True},
+            "repo_name": "main", "cwd_parent": True},
```
Observed: clean `EXIT=1`, ambient `EXIT=1`. `SUMMARY ... new_forgeries=1 ... class_mismatches=1`. Flips 0 (both legs fail identically).
`CASE W4 expect=refuse base=refuse base_findings=- new=accept new_findings=-` (was `new=refuse new_findings=lane worktree is dirty`). Detail: `new_rc` 2→0 with no stderr.
Rows affected: W4 only. Base-side W4 is unchanged (L1, the base refusal is "rev is not a commit object").
Interpretation: the candidate accepts a clean tree. This is the honest result for a fixture without the planted 755->644 change. The counter labels it a "forgery" (a counter fixture artifact, not a writer defect).

### (c) remove GIT_COMMON_DIR from the clean_env exclusion tuple
```
-                      "GIT_NO_REPLACE_OBJECTS", "GIT_COMMON_DIR", "GIT_NAMESPACE",
+                      "GIT_NO_REPLACE_OBJECTS", "GIT_NAMESPACE",
```
Observed clean (no ambient vars): `EXIT=0`, SUMMARY identical to pristine.
Observed ambient (`run-r3-ambient.log`): `EXIT=2` only, no CASE rows. Stderr: `C1-COUNTER-FATAL: candidate bytes unreadable: f70da577…:tools/souji-receipt-write.py: fatal: not a git repository`. C2 flips against the clean run: 46 (the 42 CASE + SUMMARY + REGRESS + EXIT=0 lines of the clean run are all removed or changed).
Rows affected: all 42 (the counter never reaches `evaluate`; exit 2 = could not evaluate).

### (d) W6 expectation accept -> refuse (matrix copy, counter pristine)
```
-W6	accept	-
+W6	refuse	RECEIPT-ENV-COMMONDIR-MISMATCH
```
Run: the frozen counter `census/round-68/c1-counter.py` against `$S/mut-d-matrix.tsv` (matrix is read by path; the counter is pristine).
Observed clean `EXIT=1`, ambient `EXIT=1`. `SUMMARY matrix=42 base_forgeries=3 base_honest=10 new_forgeries=1 new_honest=10 class_mismatches=1 regress=PASS`. `CASE W6 expect=refuse base=accept new=accept`.
Rows affected: W6 only (its expectation).

## Noticed / not noticed by the frozen predicates

C1 kill rule (candidate run must exit 0 with the frozen SUMMARY). C2 kill rule (either leg exits non-zero, or flips > 0).

| Mutant | Edit | C1 noticed? (candidate, clean shell) | C2 noticed? (clean vs ambient) | Evidence |
|---|---|---|---|---|
| a | remove W5 cwd rule | NOT noticed (EXIT=0, SUMMARY identical) | NOT noticed (flips 0, both EXIT=0) | run-r1a-clean.log, run-r1b-ambient.log |
| b | remove mode_change from W4 | noticed (EXIT=1, new_forgeries=1) | noticed (both legs EXIT=1, kill clause) | run-r2a-clean.log, run-r2b-ambient.log |
| c | remove GIT_COMMON_DIR from scrub | NOT noticed in a clean shell (EXIT=0) | noticed (ambient EXIT=2, flips=46) | run-r3-clean.log, run-r3-ambient.log |
| d | W6 accept -> refuse | noticed (EXIT=1, new_forgeries=1) | noticed (both legs EXIT=1, kill clause) | run-r4-clean.log, run-r4-ambient.log |

Named limits and findings

- HIGH: none.
- MEDIUM (L-W5): the W5 cwd rule (mutant a) is observationally inert under the current writer. The W5 row cannot detect removal of its cwd branch. The row measures the empty-value refusal only.
- MEDIUM (L-C1-scrub): C1 runs in the operator's shell with no scrub, so removing the GIT_COMMON_DIR scrub (mutant c) is not noticed by C1. Only C2's ambient leg notices it. The scrub is covered by C2 alone.
- LOW (W4 fixture): the W4 refusal depends on the tracked mode change (mutant b). With the change removed the candidate accepts, while the poisoned `main/main/.git` copy is still present. W4 therefore does not isolate the relative-poison route. [INFERENCE from one mutant; the poison itself was not mutated, as the tasking specified four mutants.]
- LOW (C2 kill clause coupling): for mutants b and d, C2 fires through "either run exits non-zero" while flips = 0. C2's kill clause therefore reports correctness failures as operability failures. Named limit of the predicate, not of the scrub.
- Mutant (c) is the only one C2 catches through the scrub itself.

## Deviations from the frozen command
- `--root` was given as the absolute lane path (equivalent to `.`) and `--receipt` was omitted. The logs in this directory are the evidence; no receipt was written under census/.
- The counter's `--work` directories were created in scratch before each run (the counter refuses a missing dir).

## Files written (this seat)
- mutation-report.md (this file); mut-a.diff, mut-b.diff, mut-c.diff, mut-d.diff
- run-r0a-clean.{log,rc,stderr}, run-r0b-ambient.{log,rc,stderr}, run-r1a-clean.*, run-r1b-ambient.*, run-r2a-clean.*, run-r2b-ambient.*, run-r3-clean.*, run-r3-ambient.*, run-r4-clean.*, run-r4-ambient.*
- selftest-scratch-copy.log

No tools installed. Scratch removed.
