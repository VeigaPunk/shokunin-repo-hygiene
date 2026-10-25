# ExecSizeCensusFixture — r24 w1 C1 fixture draft

## Status
STATUS: PASS — the fixture draft implements the frozen 8-case set plus the L1's four pre-data amendments. It scores the scratch reference tool AND the L1-integrated lane tool (`tools/souji-size-census.py`, read-only use) at `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` (exit 0). The case-8 stub scores `pass=4` (exit 1) and does not print the target line.

## Amendments applied (L1, pre-data, stricter only)
- Amendment 1, case 3: plants ONE 2048-byte junk file, `objects/pack/r24-junk` (`b'j' * 2048`), requiring `garbage=1` AND `size_garbage=2`; exit 0; unchanged manifest. Tool `alternates=` counts `alternate:` lines; case 5 unchanged (one valid path gives 1).
- Amendment 2, cases 4 and 5: manifest rooted at the COMMON git dir; both cases assert manifest unchanged across the tool run. Case 5 adds a second manifest over the alternate objects dir (`alt_manifest_changed=0`), resolved per git's alternates rule (each line resolved against its enclosing directory).
- Amendment 3 (CritC1Control):
  - (a) Manifest lists EVERY entry under the common git dir, directories included, with `st_mtime_ns`; the first diff field is root `.` when the root mtime changes.
  - (b) Case 4 reads the raw linked witness AFTER the tool run; the manifest check covers the run.
  - (c) All `GIT_*` variables are stripped from every git/tool subprocess env.
  - (d) Precondition `git --version` >= 2.46.0 else prints `precondition=FAIL git<2.46` and exits 2 (verified with fake git 2.30.0). Not a case failure.
- Amendment 4 (CritPrereg), case 3: BOTH arms required — (main) tool on the main-worktree path with the 2048-byte pack junk; (linked) the same junk in a fresh repo that has a linked worktree, tool run on the LINKED path. Both must report `garbage=1 size_garbage=2` (common-dir figure), exit 0, unchanged manifest. A tool hard-coding `garbage=0` for linked paths fails the linked arm (mut-linkedzero).

## Delivery
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-24/w1/r24-size-census.py`, sha256 `373ef1f0a02f8ca11fccd4ff32d8511c1eaaf3ede672c37ed11ef2b10968084f`. Supersedes `be45d220…f12f`, `d2635ad7…d060`, `7fc6e68a…aad79`, `4d119cfa…2889`. The L1 copies it to `tests/fixtures/r24-size-census.py`.
- CLI: `python3 -B tests/fixtures/r24-size-census.py --tool <path>`. Prints one `CASE <n> <name> PASS|FAIL <detail>` line per case, then the counts line last. Exit 0 iff P==C and both flags use the first spelling; 1 otherwise; 2 if the precondition fails or `--tool` is not a regular file (no counts line in those cases).
- Each case makes its own `tempfile.mkdtemp(prefix='souji-r24-census-', dir='/var/tmp')`, removed with `shutil.rmtree` in a `finally` block. After all runs, `ls -d /var/tmp/souji-r24-census-*` found nothing left behind.
- Manifest: sorted `(relpath, type d/f/l/o, S_IMODE, size, mtime_ns, sha256-if-regular)`, every node under the resolved common git dir including directories; atime/ctime excluded.
- Case 8 writes `stub-emitter.py` (prints the all-zero counts line, runs no git) to its own scratch, then runs cases 2–5 with the stub; it passes iff at least one fails.

## Evidence
Final runs. Tools: git 2.56.0, Python 3.14.8. Everything ran from `/var/tmp/souji-r24-ExecSizeCensusFixture/` against a byte-identical copy of the delivery (sha256 `373ef1f0…84f` for both). No command targeted the lane or fleet repo except the read-only invocation of the L1 tool by absolute path; the lane repo was never written by this seat.

Command: `python3 -B r24-size-census.py --tool ref-size-census.py; echo exit=$?` (scratch reference implementing the frozen CLI):
```
CASE 1 clean PASS exit=0 counts=0,0,0,0 manifest_changed=0
CASE 2 dangling PASS exit=0 counts=0,0,1,0 manifest_changed=0 lost_found_dir=False
CASE 3 garbage PASS main[exit=0 counts=1,2,0,0 manifest_changed=0] linked[exit=0 counts=1,2,0,0 manifest_changed=0]
CASE 4 linked PASS exit=0 counts=0,0,0,0 manifest_changed=0 raw_linked_garbage=1
CASE 5 alternates PASS exit=0 counts=0,0,3,1 manifest_changed=0 alt_manifest_changed=0
CASE 6 refusal PASS lost_found_argv[exit=2 counts=none manifest_changed=0] partial_clone[exit=2 counts=none manifest_changed=0] promisor_unset[exit=2 counts=none manifest_changed=0]
CASE 7 detector PASS fsck_exit=0 manifest_changed=4 lost_found_other_oid=True
CASE 8 control PASS stub_failed=dangling,garbage,alternates
cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED
exit=0
```
Command: `python3 -B r24-size-census.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-size-census.py; echo exit=$?` (L1-integrated lane tool, read-only use). Identical 8 PASS lines (case 3 `main[...counts=1,2...] linked[...counts=1,2...]`), `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, exit 0. `[INFERENCE]` no lane writes: the tool drops GIT_* and runs only read-only `--git-dir=<common>` subprocesses; manifest checks would have flagged any write.
Command: `python3 -B r24-size-census.py --tool stub-emitter.py; echo exit=$?` (skip-the-work control):
```
CASE 1 clean PASS exit=0 counts=0,0,0,0 manifest_changed=0
CASE 2 dangling FAIL exit=0 counts=0,0,0,0 manifest_changed=0 lost_found_dir=False
CASE 3 garbage FAIL main[exit=0 counts=0,0,0,0 manifest_changed=0] linked[exit=0 counts=0,0,0,0 manifest_changed=0]
CASE 4 linked PASS exit=0 counts=0,0,0,0 manifest_changed=0 raw_linked_garbage=1
CASE 5 alternates FAIL exit=0 counts=0,0,0,0 manifest_changed=0 alt_manifest_changed=0
CASE 6 refusal FAIL lost_found_argv[exit=0 counts=0,0,0,0 manifest_changed=0] partial_clone[exit=0 counts=0,0,0,0 manifest_changed=0] promisor_unset[exit=0 counts=0,0,0,0 manifest_changed=0]
CASE 7 detector PASS fsck_exit=0 manifest_changed=4 lost_found_other_oid=True
CASE 8 control PASS stub_failed=dangling,garbage,alternates
cases=8 pass=4 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED
exit=1
```
Precondition check (fake git 2.30.0 in scratch, `PATH=$PWD/fakebin`):
```
precondition=FAIL git<2.46
exit=2
```
Mutants of the reference tool (hard links, selected by filename; each breaks one behavior), post-amendment-4 failing case(s) and last line:

| mutant | broken behavior | failing case(s) | last line |
|---|---|---|---|
| mut-lostfound | honors `--lost-found`, runs `fsck --lost-found` | 6 (`exit=0 manifest_changed=4 first=.`) | `cases=8 pass=7 ...` exit 1 |
| mut-touch | creates and unlinks `<common>/souji-census.lock` | 1–6 (`manifest_changed=1 first=.`) | `cases=8 pass=2 ...` exit 1 |
| mut-extonly | refuses only on `extensions.partialclone` | 6 (`partial_clone[exit=0 ...] promisor_unset[exit=0 ...]`) | `cases=8 pass=7 ...` exit 1 |
| mut-nocommon | runs `git -C <path> count-objects -v` | 3 linked arm (`counts=2,2`) and 4 (`counts=1,0`) | `cases=8 pass=6 ...` exit 1 |
| mut-nosize | always reports `size_garbage=0` | 3 both arms (`counts=1,0`) | `cases=8 pass=7 ...` exit 1 |
| mut-no_pack | refuses promisor config but skips `.promisor` pack check | 6 (`promisor_unset[exit=0 ...]`) | `cases=8 pass=7 ...` exit 1 |
| mut-linkedzero | on linked paths hard-codes `garbage=0 size_garbage=0` | 3 linked arm (`linked[exit=0 counts=0,0,...]`) | `cases=8 pass=7 ...` exit 1 |

`--tool nope.py` (pre-amendment run) printed `r24-size-census: could-not-evaluate: tool not a regular file or no /var/tmp` and exited 2.

## Findings
1. git 2.56.0 writes no `extensions.partialClone` key on a partial clone. `git clone --no-checkout --filter=blob:none file://<src>` (source with `uploadpack.allowFilter true`) yields `remote.origin.promisor = true`, `partialclonefilter = blob:none`, `repositoryformatversion = 1`, and a `pack-<id>.promisor` file. Case 6 builds a real blobless clone (arm B) plus an arm with `remote.origin.promisor` unset (arm C), expecting exit 2 in both. Refusing only on `extensions.partialClone` fails (mut-extonly); skipping the `.promisor` pack check fails arm C (mut-no_pack). Location: `r24-size-census.py` `case_refusal`.
2. For the tool writer: with `objects/info/alternates` set, `git fsck --unreachable --no-reflogs` reports the alternate store's objects as unreachable (`counts=0,0,3,1` in case 5; 3 objects from the alternate repo). Case 5 checks `alternates=1` and that the alternate objects dir is unchanged; the L1 tool keeps this measurement, so the lane-bound figure overstates `unreachable` when alternates exist. `[INFERENCE]` A tool fix is fsck with `GIT_ALTERNATE_OBJECT_DIRECTORIES` unset, or per-store accounting; not tested.
3. Interpretations the L1 should ratify (none changes a predicate):
   - **Exit 0 for cases 2–5.** These cases require tool exit 0 before their counts line is read; only case 1 says it explicitly.
   - **Case 6, `--lost-found` repo.** The arm uses a repo holding a dangling blob so a tool honoring the flag would write `lost-found/` (mut-lostfound shows this). argv: `--repo PATH --lost-found`.
   - **Scrubbed environment.** Non-`GIT_*` variables are inherited; `GIT_*` are removed; `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=/dev/null`, `LC_ALL=C`, `HOME=<scratch>/home`.
   - **Missing tool path.** Non-regular `--tool` exits 2 with no counts line; otherwise Python's own exit 2 for a missing script would pass case 6.
4. Case 4's witness depends on git behavior: it passes only if raw `git -C <linked> count-objects -v` prints `garbage: 1`, observed on git 2.56.0; a git without the false positive turns case 4 into FAIL (kill rule applies, not a respec).

## Attack log
- A1. Before amendment 2, cases 4 and 5 did not assert an unchanged manifest; mut-touch now fails them too (pass=2).
- A2. The stub passes case 1 (all zeros, no writes) and case 4 (`garbage=0`, the raw witness comes from git). Expected: line 60 requires only that it fail at least one of cases 2–5; it fails 2, 3, 5.
- A3. Before amendment 1, a zero `size_garbage` passed case 3; mut-nosize now fails it. Before amendment 4, a tool hard-coding linked-path `garbage=0` passed case 3; mut-linkedzero now fails the linked arm.
- A4. Not found: a cheap tool reaching 8/8 without running git. Cases 2, 3, 5 need nonzero counts tracking case setup; case 6 needs selective refusal.

## Sources (opened this run)
- Preregistration `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-24/preregistration.txt` line 50: "2 dangling   — one unreferenced blob: unreachable=1; manifest unchanged; no .git/lost-found."
- Same file, line 51: "3 garbage    — one junk file in objects/pack: garbage=1; manifest unchanged." Amended pre-data: 2048-byte junk, `size_garbage=2`, main+linked arms.
- Same file, line 56: "6 refusal    — extra argv `--lost-found` -> exit 2; partialClone repo -> exit 2; manifest"
- Same file, line 60: "alternates=0` and exits 0 without running git, run through cases 2-5, must fail"
- L1-integrated tool `tools/souji-size-census.py` (read-only), lines 61–90: `refuse_promisor` refuses on `extensions.partialClone`, any `remote.*.promisor` true, and any `objects/pack/*.promisor` file.

## Tooling
No installs or upgrades. Scratch `/var/tmp/souji-r24-ExecSizeCensusFixture/` was removed (`ls` reports "No such file or directory"). The only lane writes are the two w1 files above.
