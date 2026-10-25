# W2C1MutTool — C1 tool mutation probe (souji r24, wave 2 FALSIFY)

## Status
STATUS: PARTIAL — fixture is green on pristine (8/8, exit 0) and kills 4/11 clause mutants; 7 survive (`uncovered=7`), each confirmed non-equivalent by an out-of-fixture witness except core.fsmonitor (equivalent on every input tried).

## Evidence
- Revision: tool blob `a710dfa35833dc28601c23a8b00617a3a6c8275a`, fixture blob `fe08f3aa06ca530630322c125b508f1b12e2a6dc` at `ca7fc1cb6dd1333096c6f3bdbad304686691d126` (`git ls-tree`); lane `master` = `c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface`, and `git diff --stat ca7fc1cb..master` on both files is empty. git 2.56.0, Python 3.14.8.
- Copies: `git show ca7fc1cb:<path> > /var/tmp/souji-r24-W2C1MutTool/pristine/…`; `git hash-object` on the copies = the ls-tree blob ids above.
- Detector (same bytes, every run): `python3 -B /var/tmp/souji-r24-W2C1MutTool/pristine/r24-size-census.py --tool <tool>`.
- Baseline (pristine tool): `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, `exit=0`. Case 5 detail: `counts=0,0,3,1`.
- Each mutant is a separate file `mut/mNN.py` (copy of pristine, edited via exact string replace); pristine was never edited.

| # | Clause (contract) | Mutant (diff) | Fixture result | Verdict |
|---|---|---|---|---|
| m01 | count-objects on resolved COMMON dir | `count_objects(env, path)` + `git(env, "-C", common, "count-objects", "-v")` | `pass=6`; CASE 3 FAIL `linked[… counts=2,2,0,0]`, CASE 4 FAIL `counts=1,0,0,0` | KILLED by garbage(linked arm), linked |
| m02 | alternates = git's resolved `alternate:` lines | `a` = non-blank lines of `objects/info/alternates` | `pass=8`, exit 0 | SURVIVED |
| m03 | refuse on `objects/pack/*.promisor` | `if False and name.endswith(".promisor"):` | `pass=7`; CASE 6 FAIL `promisor_unset[exit=0 counts=0,0,1,0]` | KILLED by refusal |
| m04 | PATH must be top level | `if False:` replaces realpath(path) != realpath(top) | `pass=8`, exit 0 | SURVIVED |
| m05 | child env is an allowlist | `git_env()` returns `dict(os.environ)` | `pass=8`, exit 0 | SURVIVED |
| m06 | 900 s timeout on every git call | `subprocess.run(..., capture_output=True)` (no `timeout=`) | `pass=8`, exit 0 | SURVIVED |
| m07 | `-c core.fsmonitor=false` | removed from CONFIG | `pass=8`, exit 0 | SURVIVED (equivalent on tried inputs) |
| m08 | size_garbage from count-objects | `size_garbage=0` literal | `pass=7`; CASE 3 FAIL `main[… counts=1,0,0,0]` | KILLED by garbage |
| m09 | unreachable = `fsck --unreachable` lines | `fsck --dangling`, count `dangling ` lines | `pass=8`, exit 0 (CASE 5 shows `counts=0,0,1,1` vs baseline `0,0,3,1`, not asserted) | SURVIVED |
| m10 | `warning: garbage found:` passes through | count-objects `if rc != 0 or err:` | `pass=7`; CASE 3 FAIL `main[exit=1 …] linked[exit=1 …]` | KILLED by garbage |
| m11 | any other stderr is a failure | `or err` dropped in `checked`, `resolve`, both `refuse_promisor` checks, and count-objects warning filter | `pass=8`, exit 0 | SURVIVED |

killed=4 survived=7 inconclusive=0 **uncovered=7**
- Re-run on final bytes (same detector, `out/recheck/`): baseline `cases=8 pass=8` exit 0; m01/m03/m08/m10 fail exactly the cases above; all seven survivors `pass=8` exit 0. Case 5 figure difference re-observed: baseline `counts=0,0,3,1` vs m09 `0,0,1,1`. Pristine sha256 (`sha256sum -c`) unchanged: tool `09bb8e0d…`, fixture `373ef1f0…`.

Out-of-fixture witnesses (`/var/tmp/souji-r24-W2C1MutTool/witness.sh`, own mkdtemp repos, same input to pristine and mutant):
- m02: alternates file `# comment line` + one real path → pristine `alternates=1`, mutant `alternates=2`.
- m04: `--repo <repo>/sub` → pristine `exit=2` (refused), mutant `exit=0 garbage=0 size_garbage=0 unreachable=0 alternates=0`.
- m05: caller `GIT_TRACE=1` → pristine `exit=0`, mutant `exit=1 … git failure` (trace on stderr). Caller `GIT_OBJECT_DIRECTORY=<other>/objects` → pristine `exit=0`, mutant `exit=1 error: … invalid sha1 pointer in cache-tree`.
- m06: objects/info/alternates FIFO with no writer (git blocks on open): pristine `exit=1` at 900 s (“… timed out after 900s”); mutant still running at 1000 s, killed by the run's external `timeout -k 5 1000` (`exit=124`, no stderr). Script `witness-timeout.sh`, output `out/witness-timeout.txt`, wall ~1000 s.
- m07: repo `core.fsmonitor=<script that appends a marker>` → pristine and mutant both `exit=0 marker=absent`; direct `git -C <repo> status` and `git -C <repo> fsck --unreachable --no-reflogs --no-progress` each `marker=2`. The tool runs fsck as `--git-dir=<common>` and that invocation never launched the hook here, so the override is masked by the common-dir read.
- m09: unreferenced tree holding one blob → pristine `unreachable=2`, mutant `unreachable=1`.
- m11: alternates naming a nonexistent dir → pristine `exit=1 … git failure`, mutant `exit=0 … alternates=0` (missing alternate silently dropped).

Restoration: pristine sha256 before and after all runs (`sha256sum -c hashes-before.txt` → both `OK`): tool `09bb8e0d9906b0dfef44775a9e5cd7c8f8a27d9bcdf559e2d371a3ef7ff1ed6d`, fixture `373ef1f0a02f8ca11fccd4ff32d8511c1eaaf3ede672c37ed11ef2b10968084f`. Mutants were separate files, so no restore step was needed; the lane was not written except this report. `/var/tmp/souji-r24-census-*` (fixture-owned mkdtemp, hard-coded `SCRATCH_PARENT = '/var/tmp'`) left nothing behind (`ls` → no such file). Scratch `/var/tmp/souji-r24-W2C1MutTool/` removed at end.

## Findings
1. **uncovered=7** — the fixture's 8 cases pin the counts line for main/linked/garbage/refusal paths, but 7 of 11 tool clauses can be broken with the fixture staying `cases=8 pass=8`, exit 0. Location: `tests/fixtures/r24-size-census.py` @ca7fc1cb, CASES list (line 262).
2. **m09 unreachable semantics unpinned.** Case 2 uses one lone blob, where `--dangling` and `--unreachable` agree; case 5 produces a differing figure (3 vs 1) but asserts only alternates. Fixture line 207: "ok = (code == 0 and counts is not None and counts[3] == 1 and not delta". The frozen prereg names "fsck unreachable count" as the census quantity, so a dangling-only count would pass C1.
3. **m06 timeout clause is untestable as built.** Fixture line 29 "TIMEOUT = 120" vs tool line 74 "TIMEOUT_S = 900": any hang case kills the pristine tool at 120 s too, so the fixture cannot tell a 900 s timeout from none. Tool docstring line 22: "every git call has a 900 s timeout (a FIFO in include.path, fsck.skipList or alternates hangs git; no -c override exists)".
4. **m05 env allowlist unpinned.** The fixture strips every `GIT_*` from the tool's env (`Scratch.__init__`: "if not key.startswith('GIT_')"), so the allowlist's purpose (caller `GIT_*` must not reach git) is never exercised; a passthrough env passes 8/8 while `GIT_OBJECT_DIRECTORY`/`GIT_TRACE` change the result (witness above).
5. **m04 top-level refusal unpinned.** No case passes a subdirectory or a non-repo nested under a repo; prereg line 38 lists "not a repository" as an exit-2 refusal and the tool docstring makes top-level a refusal condition.
6. **m11 stderr-is-failure unpinned.** No case produces non-warning stderr with git exit 0; the contract says "any other stderr is a failure" (prereg line 41–42). A missing alternate is silently dropped (`alternates=0`, exit 0) under the mutant.
7. **m02 alternates source unpinned.** Case 5's alternates file has exactly one valid line, so raw-line counting equals git's resolved list; amendment line 23 "alternates= counts `alternate:` output lines" is not distinguished.
8. **m07 equivalent-in-practice** [INFERENCE from witness]: with every census command on `--git-dir=<common>`, git 2.56.0 did not launch a repo `core.fsmonitor` hook, so `-c core.fsmonitor=false` is defense in depth; no fixture can kill it while m01's clause holds. Not a fixture gap so much as a redundant guard; it becomes live if m01's clause regresses.
9. Killed clauses: common-dir read (cases 3 linked arm, 4), .promisor-pack refusal (case 6 promisor_unset arm: the blobless clone has no `extensions.partialClone`, only the pack), size_garbage (case 3), warning pass-through (case 3).

## Attack log
- A1 common-dir → KILLED (3, 4).
- A2 alternates-from-file → SURVIVED; witness comment line 1→2.
- A3 no .promisor-pack refusal → KILLED (6).
- A4 no top-level check → SURVIVED; witness subdir exit 2→0.
- A5 env passthrough → SURVIVED; witness GIT_TRACE exit 0→1.
- A6 no timeout → SURVIVED; witness FIFO-alternates hang: pristine self-times-out at 900 s (exit 1), mutant runs on until the 1000 s external kill (exit 124).
- A7 no core.fsmonitor override → SURVIVED; no behavioral witness found (masked by `--git-dir`).
- A8 size_garbage=0 → KILLED (3).
- A9 `--dangling` → SURVIVED; witness unreferenced tree 2→1.
- A10 warnings as failures → KILLED (3).
- A11 stderr ignored → SURVIVED; witness missing alternate exit 1→0.

No tools installed or updated.
