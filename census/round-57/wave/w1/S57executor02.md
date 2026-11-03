# S57executor02 — independent C2 reproduction

Verdict: AGREE with C2 selftest, before-state discrimination, receipt binding, and the L1-adjusted two-row evidence manifest. Standing receipt is a **dirty-tree refusal, not a pass**. No frozen files changed. No tools installed. Axes: fidelity, traceability, speed, clean teardown.

Read preregistration before execution. Observed lane HEAD was 805482129d022b13db672654f5478952def607a6; measurements explicitly used freeze d749f7ee081ec1b382b2f92577eb22bfba1c7761. Initial porcelain count was 0; the standing suite subsequently observed 6 unexpected rows during the concurrent wave. No cleanup of external lane state or standing retry attempted.

## Exact command bindings

The commands below use these literal absolute-path bindings (each executed shell supplied its own needed values):

```sh
L=/home/vgpnk/Projects/shokunin/souji-shokunin
S=/fast/scratch/hyaku/souji-r57/S57executor02
E=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-57/w1/S57executor02
R=d749f7ee081ec1b382b2f92577eb22bfba1c7761
```

Each RC below is the observed process exit status, printed immediately after the command, not inferred from its SUMMARY.

## 1. AGREE — selftest

```sh
TMPDIR=$S python3 -B $L/census/round-57/c2-counter.py --selftest --work $S/c2
```

Observed full output:

```text
SELFTEST-CASE ABSENT pass rc=1 want_rc=1 findings=RECEIPT-REV-ABSENT want_findings=RECEIPT-REV-ABSENT
SELFTEST-CASE DIGEST-MISMATCH pass rc=1 want_rc=1 findings=RECEIPT-INSTRUMENT-DIGEST-MISMATCH want_findings=RECEIPT-INSTRUMENT-DIGEST-MISMATCH
SELFTEST-CASE KEEP-ONLY pass rc=1 want_rc=1 findings=RECEIPT-REV-KEEP-ONLY want_findings=RECEIPT-REV-KEEP-ONLY
SELFTEST-CASE MISSING-REV pass rc=1 want_rc=1 findings=RECEIPT-REV-MISSING want_findings=RECEIPT-REV-MISSING
SELFTEST-CASE NO-EXIT pass rc=1 want_rc=1 findings=RECEIPT-EXIT-MISSING want_findings=RECEIPT-EXIT-MISSING
SELFTEST-CASE NOT-FULL40 pass rc=1 want_rc=1 findings=RECEIPT-REV-NOT-FULL40 want_findings=RECEIPT-REV-NOT-FULL40
SELFTEST-CASE REV-OK pass rc=0 want_rc=0 findings=- want_findings=-
SELFTEST-CASE SHORT-REV pass rc=1 want_rc=1 findings=RECEIPT-REV-SHORT want_findings=RECEIPT-REV-SHORT
SELFTEST control=FALSE-GREEN-REJECTED stub_meets=1 cases=8
SELFTEST pass cases=8
RC=0
```

## 2. AGREE — before state and false-green control

```sh
python3 -B $L/census/round-57/c2-counter.py --root $L --manifest $L/census/round-57/manifests/before.tsv
```

```text
FINDING RECEIPT-REV-MISSING census/round-56/records/landing-suite-final.txt
SUMMARY receipts=1 findings=1
RC=1
```

```sh
python3 -B $L/census/round-57/controls/c2-stub.py
```

```text
SUMMARY receipts=0 findings=0
RC=0
```

The stub's zero findings cannot meet the before target: that target requires exactly the missing-revision finding and rc=1 on the existing receipt. An always-clean stub only resembles the after half, and even reports receipts=0 rather than evaluating the population.

## 3. AGREE — exact original recorder commands and retained bytes

```sh
bash $L/census/round-57/record-receipt.sh $L $R census/round-57/c1-counter.py $S/r-c1.txt -- python3 -B $L/census/round-57/c1-counter.py --root $L --rev $R --base b4ef0bc84ada3fb3aefd6a0b1a841a6517b84acd --record-sha256 2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30 --sources-rev-before f778b9d131574d3ff09c0cc8a077643c0fc84bb4 --sources-rev-after 9bf9234ae4d11c7b31706354302a9e95ad0d1f81 --scratch $S
bash $L/census/round-57/record-receipt.sh $L $R census/round-57/c2-counter.py $S/r-c2.txt -- python3 -B $L/census/round-57/c2-counter.py --root $L --manifest $L/census/round-57/manifests/before.tsv
bash $L/census/round-57/record-receipt.sh $L $R census/round-46/c1-counter.py $S/r-standing.txt -- python3 -B $L/census/round-46/c1-counter.py --root $L --rev $R --work $S
```

Recorder output (in the same order):

```text
RECORD /fast/scratch/hyaku/souji-r57/S57executor02/r-c1.txt rev=d749f7ee081ec1b382b2f92577eb22bfba1c7761 instrument=census/round-57/c1-counter.py rc=0
RC=0
RECORD /fast/scratch/hyaku/souji-r57/S57executor02/r-c2.txt rev=d749f7ee081ec1b382b2f92577eb22bfba1c7761 instrument=census/round-57/c2-counter.py rc=1
RC=1
RECORD /fast/scratch/hyaku/souji-r57/S57executor02/r-standing.txt rev=d749f7ee081ec1b382b2f92577eb22bfba1c7761 instrument=census/round-46/c1-counter.py rc=2
RC=2
```

All three original receipts were copied without editing into E. Exact retained r-c1.txt:

```text
instrument=census/round-57/c1-counter.py
instrument_sha256=e18872d6584bdf7252a695a7ba19da875e2d7b53f1c5b46e5b524c70fcdf78d4
rev=d749f7ee081ec1b382b2f92577eb22bfba1c7761
SITE path=SCORECARD.md line=1196 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=125 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=d749f7ee081e base=b4ef0bc84ada
EXIT=0
```

Exact retained r-c2.txt:

```text
instrument=census/round-57/c2-counter.py
instrument_sha256=174d7b8a3c105875f1757f9137f26ed54e38ac11c963a134015bce8a9dd16ec2
rev=d749f7ee081ec1b382b2f92577eb22bfba1c7761
FINDING RECEIPT-REV-MISSING census/round-56/records/landing-suite-final.txt
SUMMARY receipts=1 findings=1
EXIT=1
```

Exact retained r-standing.txt:

```text
instrument=census/round-46/c1-counter.py
instrument_sha256=5455fb46084d081a6d48de39fb8a89bba4de0ce48e002d95f65eec0e6f893bf6
rev=d749f7ee081ec1b382b2f92577eb22bfba1c7761
COULD-NOT-EVALUATE dirty worktree at run time: 6 unexpected rows
EXIT=2
```

DISAGREE with interpreting the standing receipt as a suite pass: its status is dirty-tree refusal, not a pass. It remains a genuinely revision-bound receipt with the real nonzero EXIT. Main explicitly instructed keeping this result and not retrying.

Digest verification commands, run independently of the recorder:

```sh
git -C $L show $R:census/round-57/c1-counter.py | sha256sum
git -C $L show $R:census/round-57/c2-counter.py | sha256sum
git -C $L show $R:census/round-46/c1-counter.py | sha256sum
```

Observed outputs:

```text
e18872d6584bdf7252a695a7ba19da875e2d7b53f1c5b46e5b524c70fcdf78d4  -
174d7b8a3c105875f1757f9137f26ed54e38ac11c963a134015bce8a9dd16ec2  -
5455fb46084d081a6d48de39fb8a89bba4de0ce48e002d95f65eec0e6f893bf6  -
```

Each equals its receipt's pin; each receipt visibly has instrument=, instrument_sha256=, the full freeze rev=, and EXIT=.

## 4–5. AGREE — L1-adjusted two-row evidence manifest

The original three-row manifest was evaluated once before Main's adjustment: `SUMMARY receipts=3 findings=0`, RC=0. This establishes binding only, not success of the underlying standing suite. The harness automatically backgrounded that in-flight invocation for an incoming message; no background execution was requested.

Main then explicitly replaced steps 4–5 with a TWO-row evidence manifest: C1-tip plus a fresh receipt of C2 evaluating only C1-tip. The final after.tsv here is that adjusted evidence, NOT the canonical frozen-population three-row after manifest. Main owns the final clean-tree standing receipt and canonical integration.

Wrote E/c1-only.tsv with header `receipt<TAB>instrument` and one row:

```text
.ufo/waves/round-57/w1/S57executor02/r-c1.txt	census/round-57/c1-counter.py
```

Then ran:

```sh
TMPDIR=$S bash $L/census/round-57/record-receipt.sh $L $R census/round-57/c2-counter.py $S/r-c2-after.txt -- python3 -B $L/census/round-57/c2-counter.py --root $L --manifest $E/c1-only.tsv
cp $S/r-c2-after.txt $E/
```

Observed recorder RC=0 and retained r-c2-after.txt:

```text
instrument=census/round-57/c2-counter.py
instrument_sha256=174d7b8a3c105875f1757f9137f26ed54e38ac11c963a134015bce8a9dd16ec2
rev=d749f7ee081ec1b382b2f92577eb22bfba1c7761
SUMMARY receipts=1 findings=0
EXIT=0
```

Its digest matches the independently derived C2 committed blob digest above. Final E/after.tsv (actual separators are tabs):

```text
receipt	instrument
.ufo/waves/round-57/w1/S57executor02/r-c1.txt	census/round-57/c1-counter.py
.ufo/waves/round-57/w1/S57executor02/r-c2-after.txt	census/round-57/c2-counter.py
```

```sh
python3 -B $L/census/round-57/c2-counter.py --root $L --manifest $E/after.tsv
```

```text
SUMMARY receipts=2 findings=0
RC=0
```

## Retained evidence, limits, and handoff

Files added exclusively in the assigned seat area: r-c1.txt, r-c2.txt, r-standing.txt, r-c2-after.txt, c1-only.tsv, after.tsv; this report is the separately assigned advisory path. No counter/fixture/expected/control/preregistration or external substrate changed.

C2 binds receipt metadata and committed instrument bytes, not successful counter execution. The EXIT=1 before-gate receipt and EXIT=2 refusal demonstrate why a clean binding gate alone must not be advertised as a successful standing-suite run. The three-row canonical after deliverable is intentionally superseded by Main's explicit two-row instruction; its clean-tree finalization belongs to Main.

No further checks requested from this seat; Main owns post-integration validation. Scratch deletion is performed before terminal handoff. No tool installation, LSP symbol operation, build, lint, or formatter was needed.

Self-evaluation (1–5): accuracy 4 (exact outputs retained, standing failure distinguished; initial run overlaps wave writes); completeness 4 (all assigned measurements completed, canonical three-row integration explicitly transferred by Main); clarity 4 (full command bindings retained, but report is long); actionability 4 (two-row manifest consumable immediately, final standing pass requires Main's clean tree); conciseness 3 (verbatim evidence deliberately repeated for audit). Overall 3.8. Improvement priority: consume retained receipts rather than treating the metadata-gate green as suite success; preserve Main's canonical/evidence distinction. Would the user agree? Expected yes on scope and evidence; report length is the main usability tradeoff.
