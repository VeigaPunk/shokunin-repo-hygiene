# AttackC2J1Timeout — round-34 w2 falsification of the W1 C2 J1 timeout finding

Seat: SwarmReviewer29 (read-only; one bounded probe in seat scratch).
Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. Base 9c76c7222a8abff027af42e37f0d160d52526bba; frozen list/counter/fixture revision 2b0171e2071fdc9c16a69bed12b0d040e574d8c8.

## Status

**CONFIRMED with corrected classification.** The W1 J1-timeout finding is a real, reproduced instrument defect — but it is **not test cost, not deadlock, and not a missed stub failure**:

1. **Structural starvation, not cost or load.** In the frozen/default configuration the control can never complete: the fixture wraps the whole inner counter in a hardcoded 900 s window (`tests/fixtures/r34-sandbox-junk.py:119`) while the inner counter's own junk leg waits up to 900 s (`census/round-34/c2-counter.py:265` default `--timeout`) on a deeper level that itself needs >900 s. With the two budgets equal and positive per-level work, the fixture's window always expires first. W1's cost/load framing (SwarmSentinel37 #7: "budgeted below its own cost … cannot complete at current host load (43-54)") is **falsified**: the five stub legs + guards complete in **13.4 s measured**; host speed changes only per-level seconds, never the ≥900 s dead-wait lower bound.
2. **The five stubs ARE rejected by the frozen counter logic** (bounded probe B, no oversized run): W1/W3/W4/N3 FAIL on the zero-create work-witness clause, W2 FAILs on `CASE=0` vs `SUMMARY total=12`. The timeout masked a would-be **PASS** of the control, not a would-be FAIL. Every committed J1 FAIL is fail-by-exception; before this seat no committed record established the stub verdicts at all.
3. **Root cause is the counter's junk branch discarding the leg argv** (`c2-counter.py:287-288`), re-invoking the real fixture from `--root` — confirming w1 SwarmExecutor17's recursion mechanism and adding the budget-tie as the reason 900 s is consumed rather than seconds.

## Evidence

### A. Frozen bytes and revisions (read-only)

- `git cat-file blob 2b0171e2071fdc9c16a69bed12b0d040e574d8c8:census/round-34/c2-counter.py | cmp - census/round-34/c2-counter.py` → identical (`COUNTER_FROZEN_EQ_WORKTREE`); same for `tests/fixtures/r34-sandbox-junk.py` (`FIXTURE_FROZEN_EQ_WORKTREE`). All line citations below are the frozen bytes.
- Lane master/HEAD at seat time: `adac8bbc79a7ed77b632b309e70fd2a91b45dbd9` (moved past w1's tip 51acb5f; the two frozen files are unchanged since the freeze per the cmp above).

### B. Recursion mechanism (source)

- `c2-counter.py:287-288`: for `kind == "junk"` the counter runs `[sys.executable, os.path.join(root, "tests/fixtures/r34-sandbox-junk.py"), "--counter", os.path.abspath(__file__), "--scratch", scratch]` — the leg's `argv` cell is discarded; the counter's own abspath and its **inherited scratch** are passed.
- The fixture's stub legs file keeps a `J1 junk` row whose argv names a **no-op leaf** `tests/fixtures/r34-junk-noop.py` (`r34-sandbox-junk.py:105`, quoted in w1 `deliver-c2-j1guards.txt` §3); the stub clone retains the real `r34-sandbox-junk.py` (the fixture only rewrites `census/round-34/c2-legs.tsv` and adds the noop). So the inner counter's J1 leg re-enters the real fixture → counter → fixture → …  Frozen J1 row `c2-legs.tsv:40` (`--scratch {SCRATCH}/j1`) is equally decorative.
- `c2-counter.py:56-63` (`validate_legs`): a legs file with **no junk row is refused**. The anti-false-green contract therefore guarantees the re-entry in every compliant inner reading.
- Budgets: fixture waits `timeout=900` around the entire inner counter (`r34-sandbox-junk.py:119`, hardcoded); the inner counter is launched **without** `--timeout`, so its junk-leg wait defaults to 900 (`c2-counter.py:265`).

### C. Committed execution evidence (w1 / records)

- `census/round-34/records/junk-c2-final.txt:22`: `TimeoutExpired … '--root', '…/junk-final/r34-junk.d0ocd2me/c', … '--scratch', '…/r34-junk.d0ocd2me/inner'' timed out after 900 seconds` — depth-1 fixture→counter invocation, frozen bytes.
- w1 `deliver-c2-j1guards.txt`: 13-leg run `LEG J1 FAIL … timed out after 900 seconds`; separate fixture run traceback at `r34-sandbox-junk.py:117`, loadavg `36.69 38.04 29.33 21/8349` afterwards; §3 marker proof (J1 argv named a marker script; `MARKER_RAN` absent → argv discarded) and §3(b) an observed **12-deep nested chain** `r34-junk.X/inner/r34-junk.Y/inner/…` within one 900 s window.
- `census/round-34/records/controls.txt`: "C2 junk control … ended with a TimeoutExpired after 900 seconds …; no pass is claimed."

### D. Probe B — the five stub verdicts, bounded (REPRODUCED)

Design: replicate the fixture's stub-clone construction byte-for-byte in seat scratch (same `STUBBED` five, same `DOC_LINES`, same `capture_line` procedure, same 12-row stub legs incl. the J1 noop-argv row — the fixture omits N4), then neutralize **only** the recursion by replacing `tests/fixtures/r34-sandbox-junk.py` inside the scratch clone with an instant leaf (`PROBE_FAKE_J1_LEAF`), and run the real frozen counter bytes against the clone. Lane untouched; per-level budget small; whole process group killable; scratch cleaned to 8 KB afterwards.

Command (driver: `/fast/scratch/hyaku/souji-r34/AttackC2J1Timeout/probe_b.py`):
```
python3 -B /fast/scratch/hyaku/souji-r34/AttackC2J1Timeout/probe_b.py
# builds S/probeB/c (clone of lane tip, stub commit 1293440fad0f518d0bd851354d539b2cc75125ea),
# runs: python3 -B <lane>/census/round-34/c2-counter.py --root S/probeB/c --rev 1293440f… \
#   --base adac8bbc… --list-rev 1293440f… --scratch S/probeB/inner --timeout 240
```
Output (verbatim; wall 13.4 s, load 2.30 → 5.82, host otherwise idle, 32 cores):
```
LEG	W1	FAIL	work witness failed creates=0/0 target=False	load=6.06
LEG	W2	FAIL	CASE=0 summary=SUMMARY	total=12	failed=0	load=6.06
LEG	W3	FAIL	work witness failed creates=0/0 target=False	load=6.06
LEG	W4	FAIL	work witness failed creates=0/0 target=False	load=5.82
LEG	N3	FAIL	work witness failed creates=0/0 target=False	load=5.82
LEG	J1	PASS	cases=5 pass=5 control=STUB-REJECTED PROBE_FAKE_J1_LEAF	load=5.82
LEG	G1	PASS	r33 diff	load=5.82
LEG	G2	PASS	unexpected paths=	load=5.82
LEG	G3	PASS	SELFTEST pass witness-required rejected junk-only rejected	load=5.82
LEG	G4	PASS	bwrap+strace available	load=5.82
LEG	G5	PASS	overlap commits=	load=5.82
LEG	G6	PASS	namespace fixture pin	load=5.82
SUMMARY legs=12 pass=7 fail=5 harm=0 rev=1293440fad0f518d0bd851354d539b2cc75125ea
```
Captured stub lines used by the probe (fixture's own `capture_line` procedure): W1 `selftest: 48/48 passed`, W2/W3/N3 documented lines, W4 `selftest: 49 checks, 2 failed` (incidental tip observation of the verify selftest; no claim made here).

### E. Orphan / load hygiene

- Before probe: `pgrep -af 'r34-sandbox-junk|c2-counter'` → no matches; `/proc/loadavg` `1.64 1.43 2.02`. After probe: no matches. No live recursion processes at seat start or end; my probe left none.
- Scratch `/fast/scratch/hyaku/souji-r34/AttackC2J1Timeout` reduced to 8 KB (driver only) after the run; probe work dir removed. Well under the 50 MB ceiling.

## Findings

1. **[REPRODUCED + structural] The J1 timeout is budget-tie starvation caused by self-recursion — not test cost, not host load, not deadlock.** The fixture grants the whole inner counter 900 s (`r34-sandbox-junk.py:119`) while the inner counter's junk leg waits up to 900 s on the next level (`c2-counter.py:265,288`). Since every level's completion time exceeds 900 s (its junk wait alone consumes the child's ≥900 s lifetime — the chain never unwinds), the fixture's window always expires first, at every level, at any host speed. This falsifies SwarmSentinel37 #7's cost/load reading ("cannot complete at current host load (43-54)"): the control still cannot complete on an idle host (this seat's checks at load 1.6-2.3). Conversely, a pure budget change (fixture window > counter `--timeout` + level work) would produce a verdict after ~915+ s in which ≥900 s is pure dead recursion wait — the "cost" is recursion dead-time; the control's actual work is 13.4 s (measured, probe B). Severity HIGH for the C2 gate: J1 is unfalsifiable as instrumented.
2. **[REPRODUCED, bounded probe] Not a missed failure: the frozen counter logic rejects all five stubs.** W1/W3/W4/N3 fail the work-witness clause (`creates=0/0 target=False` — an echo stub creates nothing), W2 fails `CASE=0` ≠ `SUMMARY total=12`. With re-entry broken, the fixture's assertion inputs are satisfied (five stub ids among `LEG … FAIL` rows, rc≠0), so from the verified output plus the fixture's string assertion (`r34-sandbox-junk.py:121-132`) the control would print `cases=5 pass=5 control=STUB-REJECTED` and exit 0 — that print itself is **derived**, not executed end-to-end with the real fixture (doing so requires the oversized run this seat was told not to repeat). The J1 FAIL lines in every committed reading are therefore fail-by-exception that masked a would-be PASS.
3. **[CONFIRMED] Root cause: the junk branch discards the leg argv** (`c2-counter.py:287-288`). The fixture's own stub J1 row names a no-op leaf (`r34-sandbox-junk.py:105`); honoring argv would complete the control in seconds. Confirms w1 SwarmExecutor17's recursion claim (and its argv-ignored marker proof) and SwarmSentinel37 #6; adds that G3's junk-row-required rule (`c2-counter.py:62-63`) makes the re-entry unavoidable in every compliant legs set.
4. **[CONFIRMED] Not a deadlock.** Each level's `flock` is on a distinct nested file (`<work>/inner/c2.lock`); no wait cycle exists — processes actively progress (w1's committed 12-deep work-dir chain; probe B levels complete in seconds).
5. **[SOURCE + receipts, LOW/operational] Timeout kills are direct-child-only.** Each timed-out `subprocess.run` kills only its direct child, orphaning deeper levels that keep running up to their own 900 s windows (bounded cascade; unwinds once the scratch root is removed or a level errors). This explains the 30-55 load readings w1 seats recorded after their runs and the subsequent "host load" attributions — a measurement-artifact feedback loop. No orphans were live at this seat's start or end.
6. **[CONFIRMED, secondary] No structured failure receipt.** `r34-sandbox-junk.py:117-119` has no handler for `TimeoutExpired`; the exception bypasses the `cases=` assertion block → traceback, rc 1 (corroborates w1 SwarmReviewer27 finding 1). The discarded pipe output is exactly where the five-stub verdicts were; probe B shows they are available within 13 s of counter time.

## Attack log

1. Read w1 receipts (`deliver-c2-j1guards.txt`, `SwarmExecutor17.md`, `SwarmReviewer27.md`, `deliver-junk-fixture-review.txt`, `SwarmSentinel37.md` #6-7, `SwarmScribe35.md`) — found W1's classifications conflict (recursion vs cost/load vs inconclusive).
2. Read frozen sources: `tests/fixtures/r34-sandbox-junk.py` (full), `census/round-34/c2-counter.py:1-330`, `census/round-34/c2-legs.tsv`, `census/round-34/preregistration.txt:50-123`; committed records `junk-c2-final.txt`, `controls.txt`.
3. Verified frozen-byte identity (`cmp` vs blobs at 2b0171e2) and lane tip; checked live orphans (`pgrep`) and load; sized `.git` (77 MB) to bound clone cost per recursion level.
4. Designed and ran probe B (13.4 s, no recursion, no oversized run): stub clone per the fixture's exact construction; recursion neutralized by a disclosed scratch-local leaf; real frozen counter bytes evaluated the five stubs.
5. Cleaned scratch to 8 KB; verified no orphan processes remained.

## Deliveries

- `.ufo/waves/round-34/w2/AttackC2J1Timeout.md` — this report.
- `.ufo/waves/round-34/w2/SwarmReviewer29.md` — seat-scoped findings (same verdicts, condensed).
- `/fast/scratch/hyaku/souji-r34/AttackC2J1Timeout/probe_b.py` — probe driver; output embedded above; work dir removed.

**Residual risk / gaps:** the end-to-end `cases=5 pass=5` print with the real fixture remains unexecuted by design (would repeat the 900 s cascade); probe B's J1 PASS line is the disclosed scratch leaf, not the real fixture. Probe B used `--base` = current tip `adac8bbc` (the fixture itself resolves `master`); both frozen files verified byte-identical to 2b0171e2. No frozen artifact, predicate, or lane file was modified.
