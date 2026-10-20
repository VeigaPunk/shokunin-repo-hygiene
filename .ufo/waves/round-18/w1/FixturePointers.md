STATUS: DONE — Added the round-18 dangling-pointer external fixture; its 11 assertions passed against a temporary contract stub.

## Axes

- **Calibration:** exact exit codes and LG-DANGLING-PTR path multisets for dangling, resolved, expanded, exempted, skipped, and out-of-scope citations; historical assertions pin all six requested source locations.
- **Coverage:** all requested synthetic scenarios plus malformed-TSV exit 2 and a silent-tool vacuity failure.
- **Operability:** each case uses a disposable `/var/tmp` git repo removed in `finally`; no real gate was run against the live lane.

## Files and behavior

- `tests/fixtures/r18-landing-pointers.py` (new, 334 lines): `--tool PATH`; isolated synthetic git repos; exact expected exits and finding-id/path multisets. The historical case calls the selected tool with `--root /home/vgpnk/Projects/shokunin/souji-shokunin --rev b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 --round 18`, requiring the two specified target-path counts and line-location details. See cases at lines 198–205, 216–245, 247–280, and 282–303; vacuity assertion is at 305–324.
- Delivery patch: `.ufo/waves/round-18/w1/FixturePointers.patch`.

## Retained evidence

- Read the pinned baseline with:
  `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b5763415cc67ecff1e8fe56c58c39a6fb106d7a3:tools/souji-landing-gate.py`
  The returned source identifies the baseline as the round-16 landing gate; this was a read only, not a gate execution.
- Ran the fixture against `/var/tmp/souji-r18-FixturePointers/lg-pointer-stub.py`. Final output:
  ```text
  CASE	PASS	skill-uncommitted-target	exit=1 findings=Counter({('LG-DANGLING-PTR', 'census/round-18/x.json'): 1})
  CASE	PASS	knowledge-committed-target	exit=0 findings=Counter()
  CASE	PASS	lesson-line-suffix-resolves	exit=0 findings=Counter()
  CASE	PASS	brace-one-missing	exit=1 findings=Counter({('LG-DANGLING-PTR', 'census/round-18/b.json'): 1})
  CASE	PASS	round-range-expands	exit=0 findings=Counter()
  CASE	PASS	placeholder-skipped	exit=0 findings=Counter()
  CASE	PASS	exemption-honored	exit=0 findings=Counter()
  CASE	PASS	malformed-exemption-exit2	exit=2 findings=Counter()
  CASE	PASS	round-17-no-pointer-finding	exit=0 findings=Counter()
  CASE	PASS	historical-b576341-round-18	exit=1 findings=Counter({('LG-DANGLING-PTR', 'census/round-17/jj-receipts-ddb7347.txt'): 4, ('LG-DANGLING-PTR', 'census/round-17/gate-replays-ddb7347.json'): 2})
  CASE	PASS	vacuity-stub	stub rc=0 stdout_bytes=0; required finding assertion failed: yes
  SUMMARY	total=11	failed=0
  ```
  The temporary stub was removed. Two earlier fixture runs exposed defects in that stub’s TSV/brace parsing; after correcting the stub, the final run above passed. Those runs did not execute the real landing gate.
- Scoped diff command:
  `git -C /var/tmp/souji-r18-FixturePointers/lane diff b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 -- tests/fixtures/r18-landing-pointers.py`
  Observed: `1 file changed, 334 insertions(+), 0 deletions(-)`.
- An extra syntax-only command was inadvertently run before the fixture harness: `python3 -m py_compile /var/tmp/souji-r18-FixturePointers/lane/tests/fixtures/r18-landing-pointers.py`; it produced no output. Its generated cache was removed. This is not counted as an acceptance result.
- No tools were installed or updated.

## Risk / integration boundary

The passing run validates fixture assertions and the stated output contract only: the temporary stub supplied the synthetic findings and the historical rows. The actual gate was not invoked on the live lane or historical revision. After GatePointers integrates, the parent should run `python3 tests/fixtures/r18-landing-pointers.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py` to validate actual behavior, especially the historical replay. No scoped implementation blocker remains.
