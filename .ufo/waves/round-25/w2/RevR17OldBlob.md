# RevR17OldBlob — old-blob post-stderr shadow check

STATUS: PASS

## Axes
- **Calibration (7):** reproduced the false green on the pre-fix blob and its rejection by current tool.
- **Operability (8):** exercised the existing committed fixture cases unchanged; fixture exits are meaningful (old=1, current=0).
- **Coverage (8):** verified all three appended case IDs, including the R17 witness; R15 remains disclosed open.

## Evidence
Executed in isolated `/var/tmp/souji-r25-RevR17OldBlob/` using `python3 -B` and a byte-identical fixture copy with only `SCRATCH_ROOT` redirected into that scratch. Old bytes were extracted with `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show c872eec:tools/souji-record-agreement.py`.

SHA-256:
- committed fixture `tests/fixtures/r23-record-agreement.py`: `8b4c23e5a75fc6a9f7ab927b20712fd447f39a16557ef93d17be1d6f15665e20`
- scratch fixture copy (scratch-root-only change): `991016a0f2ee551acbb6b10c2918b4cbf8028e814d9ebbd9e2db90dd4c612221`
- old c872eec tool: `dd53c228b8cca68cfe6dd51630c4ed3473a7c20db36a0effcf5a18259049bb0f`
- current `tools/souji-record-agreement.py`: `ec5b809d5e21134b38340d7e200463cdcc5ae5eb3cffcfc90ba088ace788d32c`

Commands:
- `python3 -B /var/tmp/souji-r25-RevR17OldBlob/fixture.py --tool /var/tmp/souji-r25-RevR17OldBlob/old.py` → **selftest=14/15**, case 13 `post-stderr-shadow` failed; case produced `rc=0 mismatches=0 keys=4` despite stdout `mismatches=0` and the case's expected K1 disagreement with the true fenced stdout tuple. Final `control=FALSE-GREEN-REJECTED`; exit 1.
- `python3 -B /var/tmp/souji-r25-RevR17OldBlob/fixture.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-record-agreement.py` → **selftest=15/15**, case 13 gives `rc=1 mismatches=1 keys=4 [K1/value-disagree]`; final `control=FALSE-GREEN-REJECTED`; exit 0.

Cases 1–12 are the same committed fixture cases and pass in both runs. The three appended IDs, confirmed in `tests/fixtures/r23-record-agreement.py:539-541`, are: 13 `post-stderr-shadow`, 14 `stdout-two-line`, 15 `receipt-rev-object`. Case 14 passes green in both; case 15 rejects the bad receipt revision in both. No difference in expected behavior was observed for the original twelve cases; the W1 execution record independently reports byte-identical committed-12 outcomes (12/12 each; `.ufo/waves/round-25/w1/ExecR17-2.md:34-44`).

**R15 remains open:** `SCORECARD.md:247` explicitly says “R15 cross-revision K1 decoy anchoring remains open.” W1's probe evidence also documents the decoy false-green (`.ufo/waves/round-25/w1/RevR17-2.md:53-56`). The R17 trailing-shadow pass does not establish R15 closure.

## Findings
1. The named old c872eec blob exhibits the post-stderr shadow false green; current tool rejects that case. This supports the requested R17 discrimination, not a broader record-agreement correctness claim.
2. R15 remains an explicit residual; no R15 closure is claimed.

## Attack log
1. Ran old and current tool against the full 15-case fixture in private scratch; preserved output during comparison, then removed the scratch directory.
2. Compared original twelve case IDs/outcomes against W1's recorded committed-fixture matrix; no changed case predicate or outcome reported (12/12 each).
3. LSP semantic checks unavailable: no LSP device/route was mounted for this seat. Used direct fixture definitions and W1 reports as literal evidence, not semantic proof. No tools installed.