# S55executor02 — C2 reproduction (round 55, wave w1)

Role: executor. Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Measured revision: `4b10ddd1741a948c89d283358affd1da2ab3fd95`. Lane tip at dispatch/run:
`3ce0ba036275f3bbd7a74bde1fecd7ec60f4c58f` (records + S278 sources only).

Verdict: **AGREE on all four assigned steps.** No frozen byte was edited, no lane file written,
no commit made, nothing installed.

## 0. Pins (verified before and after the whole pass)

All six frozen sha256 values match the assignment byte for byte
(`receipts/pins-and-fixture-revs.txt`):

```
944feafa…d921a2  census/round-55/c1-counter.py
e4eb34e6…94a568c census/round-55/c2-counter.py
e629a2e9…04fa8d62 census/round-55/fixtures/build-fixtures.py
ce13d4ff…0ef8315 census/round-55/fixtures/run-matrix.sh
ca096117…5e7b76e census/round-55/records/c1-selftest-expected.tsv
63391afa…05a8bd2bc census/round-55/records/c2-selftest-expected.tsv
```

Tool pin `e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b` holds both in the
working tree and as the blob at `4b10ddd` (`git show 4b10ddd…:tools/souji-fleet-root-census.py`).
Preregistration read first (`census/round-55/preregistration.txt`).

## 1. Pinned selftest — AGREE

Command (from lane root, `TMPDIR` on my scratch):

```
python3 -B census/round-55/c2-counter.py --selftest --work <scratch>/st \
  --builder-sha256 e629a2e9…04fa8d62 --expected-sha256 63391afa…05a8bd2bc
```

Observed: `SELFTEST pass cases=15`, exit 0. All fifteen arms pass, including the two named
ones: `FA9-WRONG-TOOL-PIN pass rc=1 want_rc=1 finding=TOOL-SHA-ARG-MISMATCH` and
`FB4-PIN-SHAPE pass rc=2 want_rc=2 finding=TOOL-SHA-ARG-MALFORMED`.

Retained evidence (`receipts/selftest.txt`, sha256 `71dcfb9a2a8e8ce0c2d75dc5d2ec42274efa95cbacdfd3504f6790c363e97503`):
the output is **byte-identical** to the committed `census/round-55/records/c2-selftest.txt`
(`diff` empty, rc 0), and two independent runs produced the same sha256.

## 2. Matrix rows under both arms — AGREE

Fixtures were rebuilt by **importing the committed builder module** (`build_one`) in scratch;
the frozen bytes were never edited and nothing was committed anywhere. Rebuilt revs equal the
revs recorded in the committed matrix, which is itself the builder-reproduction check:

| fixture | rebuilt tip | committed rev |
|---|---|---|
| FB1-TAB4-ROW | `25f4d0f38dab1411abd2dae5bda46405f685b14d` | `25f4d0f38dab` |
| FB2-LOWER-KEY | `ddab0ad7bd906b9b8aa576794ac5c3cb4ee58a4a` | `ddab0ad7bd90` |
| FB3-NOSPACE-KEY | `2530c7b6b8a967c126470e8ca02ca9064704fa1f` | `2530c7b6b8a9` |
| FA8-SYMLINK-CLASS | `e5900e5c500019ffdc022b616c278ef62a99f093` | `e5900e5c5000` |

Both arms were run exactly as `run-matrix.sh`'s `c2_arm` does it (v3 `census/round-54/c2-counter.py`,
v4 `census/round-55/c2-counter.py`, `--capture census/round-52/… --receipt census/round-53/…`).

Results — every one of the eight rows (4 fixtures × 2 arms) is **byte-identical** to
`records/c2-matrix-v3.tsv` / `c2-matrix-v4.tsv` (`receipts/matrix-compare.txt`,
`receipts/matrix-4rows-v3.tsv`, `receipts/matrix-4rows-v4.tsv`; order-normalized `diff` empty,
rc 0 both arms):

- v3 arm, four rows sorted, sha256 `38cda0c7beb4487bcb5ea853a33cf9753a4443e20a94b309ec81bfc41bc93316`
  (committed file's four rows: same hash).
- v4 arm, four rows sorted, sha256 `965d402c4da210053096b500007d6738ed8eae9dbe58747fc9f0a36ad8c7eedd`
  (committed file's four rows: same hash).

Behaviour reproduced: FB1/FB2/FB3 exit 0 under v3 and exit 1 under v4 with
`COMMENT-AMBIGUOUS-NAME` / `RECEIPT-UNKNOWN-KEY` / `RECEIPT-UNKNOWN-KEY`; FA8 exit 1 in both
arms but the finding name changes from v3's `class` to v4's `CLASS-MISMATCH` (the r54 verifier
§5.2 unnamed-kill-row repair). SUMMARY field values are identical across arms on every row.

## 3. Real-lane leg and the two refusals — AGREE

Real lane, measured revision (`receipts/real-lane-4b10ddd.txt`):

```
SUMMARY entries=49 rows=49 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok \
removal_proposed=0 receipt=ok sorted=ok tool_pin=ok rev=4b10ddd1741a
```

exit 0 — `receipt=ok sorted=ok tool_pin=ok` exactly as required. The output is **byte-identical**
to the committed `census/round-55/records/c2-tip.txt` (sha256
`14160696f8c06f0dd77ac9188a84c9def4f709171be2369de1fe0b1e738618ef`), stable across three runs.
At the lane tip `3ce0ba03…` the same field values hold (only `rev=` changes), so the later
records/S278 commits do not move the measurement.

Wrong-pin refusal (64-hex, all zeros) — `receipts/wrong-pin-refusal.txt`:

```
FINDING TOOL-SHA-ARG-MISMATCH pinned=000000000000 observed=e7e79952f783
SUMMARY … receipt=ok sorted=ok tool_pin=FAIL rev=4b10ddd1741a
```

exit 1, as required.

Malformed-pin refusal (uppercase digest) — `receipts/malformed-pin-refusal.txt`:

```
CANNOT-EVALUATE TOOL-SHA-ARG-MALFORMED --tool-sha256 must be lowercase 64-hex
```

exit 2, as required. A 12-hex short pin takes the same named refusal (exit 2).

## 4. Extra probes (beyond the assigned steps; each cheap, each receipted)

- **r54 capture non-regression** (`receipts/r54-capture-nonregression.txt`): the committed r54
  pair (`census/round-54/records/fleet-root-census.tsv` + its `-run.txt`) is exit 0 with
  `receipt=ok sorted=ok tool_pin=ok` at both `f056aaa031bb` and `4b10ddd…`; the `f056aaa` run is
  **byte-identical** to `records/c2-r54-capture-preflight.txt`. The v3 counter is also exit 0 on
  that pair at `4b10ddd`, so no carry-over regression on the real lane.
- **Selftest pin refusals**: a wrong `--builder-sha256` and a wrong `--expected-sha256` both give
  `CANNOT-EVALUATE PIN-MISMATCH` exit 2 (pin checked before exec, r53 sentinel-S4 fix holds).

## Named observations (no frozen byte edited; routed, not fixed)

1. **Finding text cannot distinguish a near-miss pin.** With only the last nibble flipped the
   counter prints `FINDING TOOL-SHA-ARG-MISMATCH pinned=e7e79952f783 observed=e7e79952f783` —
   both digests truncated to 12 chars at `c2-counter.py:155-156`, so the two sides print
   identically. Behaviour is correct (`tool_pin=FAIL`, exit 1); only the reportability of the
   message is limited. Receipt: `receipts/extra-probes.txt` §pin-shape variants.
2. **`run-matrix.sh`'s cross-round path pair is a fixture-only construct.** `c2_arm` passes
   `--capture census/round-52/… --receipt census/round-53/…`. In the real lane that pair is a
   `CAPTURE-RECEIPT-MISMATCH` (receipt declares the r53 capture's sha `922112361cdd`, observed
   `215bf849f318`; same in v3 and v4). It is sound in the matrix only because fixture repos
   carry a self-consistent pair (verified in FB1: fixture capture sha `93801e28…` equals the
   fixture receipt's `CAPTURE_SHA256`, `ENTRIES=3`). Consequence for readers: a matrix row's
   `receipt=ok` is a fixture-internal property and must not be cited as real-lane receipt
   evidence. Receipt: `receipts/extra-probes.txt` §cross-round pairing probe.
3. **The r52 capture cannot be checked by the RECEIPT_VERSION=1 grammar.** With its own r52
   receipt it yields `RECEIPT-MALFORMED` under **both** v3 and v4 (identical text, exit 1) — a
   pre-existing boundary of the frozen grammar, not a v4 change. The r52 standing check therefore
   rests on the r52 instrument, not on v4.
4. **Selftest pin arguments are equality-checked, not shape-checked.** A malformed
   `--builder-sha256 ABC` reports `PIN-MISMATCH` (exit 2) rather than a named shape refusal.
   NL-5 names only the real-lane `--tool-sha256`, so this is outside the claimed surface and is
   disclosed only.

## Hygiene

- Writes: only `/fast/scratch/hyaku/souji-r55/S55executor02/` (deleted before yield) and this
  seat directory. No file inside the lane was created or modified (`find census tools -newer`
  over my scratch marker: empty); the lane porcelain carries only sibling seats' in-flight edits
  (`SKILL.md`, `corpus/QUALITY.md`, `corpus/SOURCES.md`, `corpus/knowledge/splitlines-line-model.md`,
  `corpus/lessons/round-55.md`) — none of them mine. No git mutation anywhere; every fixture git
  action happened inside a scratch fixture whose `rev-parse --show-toplevel` was asserted to be
  that fixture dir.
- Counters read committed bytes only (`git show <rev>:<path>` via `git_show_bytes`,
  `c2-counter.py:106-113`); the only writes the counter performs are under `--scratch`
  (`c2-counter.py:344`).
- Tooling: nothing installed or upgraded. Disk guard run before the pass: 408.7 G free on
  `/fast/scratch/hyaku`, 95.6 G on `/tmp`; scratch peaked at 2.8 M.

## Blocker

None. All assigned work is reachable and complete.
