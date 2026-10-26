# SwarmExecutor15 — r32 w1 — C2 items T20 T21 T22

## Status
STATUS: PASS — the three fixtures now root their scratch at `tempfile.gettempdir()`; T20/T21/T22 were `FAIL` 3/3 at base (rc1, `Read-only file system`) and are `PASS` 3/3 under the frozen counter's bwrap sandbox with `/tmp`, `/var/tmp`, `/dev/shm` read-only and TMPDIR a scratch dir; case counts, selftest/cases lines and exit codes are byte-identical to base.

## Evidence
Contract read first: `census/round-32/records/preregistration.txt`, `census/round-32/c2-items.tsv`, `census/round-32/c2-counter.py` (`normalize()`, `summary_line()`, `creations()`).

Rev pins: lane base `85b61a151923986e7e6b48f7084b9122561b5f3d`; prereg `3ec84fc81b3243429c834a051880b0bcde06291c`; lane tip incl. controls/A0 `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`; my patch commit (scratch clone only) `4676f30702f8a64ec3ce306e41c7098e133e9b1f` on top of `7a6667c`; `git diff 85b61a1 7a6667c -- <the three fixtures>` was empty, so the delivery diff contains only my change.

1. Red-before (counter `--rev 85b61a1…`, i.e. base against base, `--only T20,T21,T22`):
```
ITEM	T20	FAIL	base=rc0:W2436:selftest=15/15	sbox=rc1:W0:tool_sha256=<HEX>	regress work-dropped
ITEM	T21	FAIL	base=rc0:W649:cases=9 pass=9 control=FALSE-GREEN-REJECTED	sbox=rc1:W0:OSError: [Errno 30] Read-only file system: '<TMP>'	regress work-dropped
ITEM	T22	FAIL	base=rc0:W1372:cases=16 pass=16 control=FALSE-GREEN-REJECTED	sbox=rc1:W0:OSError: [Errno 30] Read-only file system: '<TMP>'	regress work-dropped
SUMMARY items=3 pass=0 fail=3 partial=1 rev=85b61a151923986e7e6b48f7084b9122561b5f3d
```
2. After patch (same counter, `--rev 4676f30…`):
```
ITEM	T20	PASS	base=rc0:W2436:selftest=15/15	sbox=rc0:W2437:selftest=15/15	
ITEM	T21	PASS	base=rc0:W649:cases=9 pass=9 control=FALSE-GREEN-REJECTED	sbox=rc0:W650:cases=9 pass=9 control=FALSE-GREEN-REJECTED	
ITEM	T22	PASS	base=rc0:W1372:cases=16 pass=16 control=FALSE-GREEN-REJECTED	sbox=rc0:W1373:cases=16 pass=16 control=FALSE-GREEN-REJECTED	
SUMMARY items=3 pass=3 fail=0 partial=1 rev=4676f30702f8a64ec3ce306e41c7098e133e9b1f
```
   (W counts are strace creations; the sandbox still creates 2437/650/1373 files with `/tmp`, `/var/tmp`, `/dev/shm` read-only, so the work is real and not dropped.)
3. Patched commands, run in the clone with TMPDIR unset and with TMPDIR set (`(rc, last line)`; last line verbatim, T20's last line carries no digit — the counter scores the last digit-bearing line `selftest=15/15`):
```
T20	unset	rc=0	last=control=FALSE-GREEN-REJECTED
T20	set  	rc=0	last=control=FALSE-GREEN-REJECTED
T21	unset	rc=0	last=cases=9 pass=9 control=FALSE-GREEN-REJECTED
T21	set  	rc=0	last=cases=9 pass=9 control=FALSE-GREEN-REJECTED
T22	unset	rc=0	last=cases=16 pass=16 control=FALSE-GREEN-REJECTED
T22	set  	rc=0	last=cases=16 pass=16 control=FALSE-GREEN-REJECTED
```
4. Placement proof, r23 with `TMPDIR=/fast/scratch/hyaku/souji-r32/C2Fix23/tmp/fixtmp`:
   `scratch=/fast/scratch/hyaku/souji-r32/C2Fix23/tmp/fixtmp/souji-r23-ExecFixtureAgreement`, `selftest=15/15`, 15 `case=` lines, rc=0.
5. Leftover sweep after the TMPDIR-unset runs: `ls -d /tmp/souji-r23-* /tmp/souji-r24-* /tmp/souji-r25-*` → `none` (fixtures clean up after themselves).
6. Delivered files sha256-identical to the patched clone blobs:
   r23 `d6f8cfb60d01f734016e45eabfce9f66faabcdcf42f6a8b0da6cc93d4467cbc3`;
   r24 `65d2d681813f5c093ed31e29981ea817763d563d454f9f3ebac532099c17f669`;
   r25 `b8dc6e147f21e4c6fd5a94cd735730ee83d991c016f2b685cfe446791faf14e6`.
7. The diff is 7 hunks over 3 files (r23 three, r24 two, r25 two), 17 insertions / 14 deletions, no case, regex, path-constant or exit-code change:
   `SCRATCH_ROOT = os.path.join(tempfile.gettempdir(), "souji-r23-ExecFixtureAgreement")`,
   `SCRATCH_PARENT = tempfile.gettempdir()  # honours TMPDIR; never a hard-coded /tmp or /var/tmp` (r24, r25), plus the module docstrings and r23's `--keep` help text (all previously asserted `/var/tmp` as the location).

## Findings
1. r23 had exactly one scratch site, `SCRATCH_ROOT` (`deliver-r23-record-agreement.py:68`, base `:67`), consumed at `:106` (cleanup), `:398` (`build`), `:585` (`makedirs`), `:591` (per-case json) and printed at `:582` (`scratch=`). It is a fixed leaf name, not an mkdtemp, so it is now `<TMPDIR>/souji-r23-ExecFixtureAgreement`.
2. r23 had no `tempfile` import; the constant-only patch would have raised `NameError`, so `import tempfile` is added at `:64` (delivered file).
3. r24 (`deliver-r24-coverage-agreement.py:51` value, `:338` the sole `tempfile.mkdtemp(dir=SCRATCH_PARENT)`) and r25 (`:66` value, `:501` the sole `mkdtemp`) had no other literal-root creation; child envs in both (`git_env()` at `:78` r24 and `:104` r25) inherit the caller's environment, so TMPDIR already reached every git child and no env had to change.
4. Remaining `/var/tmp` and `/tmp` tokens in the three files are prose only (module docstrings at r23 `:12`, r24 `:17`, r25 `:20`, and the `SCRATCH_PARENT` trailing comments at r24 `:51`, r25 `:66`), each stating the literal is *not* used; no code path creates files there. `grep -n "/var/tmp\|/tmp"` over the three delivered files returns only those five lines.
5. r23's `--keep` flag never kept anything at base either: `arm_traps()` registers `atexit.register(cleanup)` unconditionally (`:110`) and fires after `if not args.keep: cleanup()` (`:609-610`). The flag's behaviour is preserved as-is; only its help text (`:571`) no longer claims `/var/tmp`.
6. [INFERENCE] The counter's `normalize()` replaces the counter work dir and any `/var|/tmp/<path>` token with `<TMP>`, so r23's changed `scratch=` value cannot create a spurious mismatch; the observed scored lines are `selftest=15/15` on both sides, which is the measurement this rests on.
7. Risk (unchanged by me): r23 keeps a deterministic scratch leaf, so two concurrent r23 fixture runs sharing one TMPDIR still collide; r24/r25 are mkdtemp-isolated. Making r23 mkdtemp-based would change the `scratch=` line and is out of this item's behaviour-identical bound.
8. Observation, outside this seat's write scope and left untouched: `/var/tmp` still holds ~40 pre-existing `souji-r23-*`/`souji-r24-*`/`souji-r25-*` residue entries from earlier rounds (e.g. `/var/tmp/souji-r23-receipts`, `/var/tmp/souji-r25-ScribeScorecard`). None was created by this run and none was removed, moved or classified (lane hygiene scope is `/home/vgpnk/Projects/shokunin/souji-shokunin/` only).

## Attack log
Not an attack seat: no counter predicate, target or item set was challenged, and no reproduced gameable state was found. The counter discriminates correctly on my items (base red 3/3, patched green 3/3, creations not dropped).

## Deliveries
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/w1/deliver-r23-record-agreement.py`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/w1/deliver-r24-coverage-agreement.py`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/w1/deliver-r25-coverage-agreement.py`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/w1/deliver-C2Fix23.diff` (`git -C <clone> diff 85b61a151923986e7e6b48f7084b9122561b5f3d -- tests/fixtures/r23-record-agreement.py tests/fixtures/r24-coverage-agreement.py tests/fixtures/r25-coverage-agreement.py`)
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/w1/SwarmExecutor15.md` (this report)

Integration note for the L1: paths are `tests/fixtures/<basename>`; no other file, tool or record was touched. Post-integration check to run at the lane tip: the full counter, `python3 -B census/round-32/c2-counter.py --root <lane> --rev <integrated full40> --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c`, where T20/T21/T22 must stay `PASS` (my run is `--only`-scoped and reports `partial=1`).

Tooling: no install or upgrade performed (python3, git, bwrap, strace used as present). Scratch `/fast/scratch/hyaku/souji-r32/C2Fix23/` removed after delivery.
