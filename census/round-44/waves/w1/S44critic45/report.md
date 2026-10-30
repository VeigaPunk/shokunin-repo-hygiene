# S44critic45 — extra-register-row falsification

## Result and axes

Axes: **calibration / operability / coverage**. Assigned judgment surface: calibration. No admission decision is made here.

**No green counter result was observed. The frozen counter rejects both the valid 66-entry control and the otherwise identical 67-entry extra-row candidate. This is not evidence that it detects extra register rows: an independent key-order defect prevents every normal population correction from matching.** Static inspection also exposes an uncounted-extra-row blind spot, currently masked by that defect. These are fixable instrument defects, not a demonstrated axis tradeoff.

## Frozen inputs and bounded method

Source revision: `d314fd6e85d62565344fa6c4b102f52f62297884`; population base: `55d7af6f5a22340f7a3de1c386e514ababfaa75f`.

The driver retrieved counter, population and declared-evidence instrument from the frozen revision with `git show`. It asserted the preregistered SHA-256 values:

- counter: `dde1ae29105ac84c7ce83705547517c501033b0fce38ddbd6a92b4bd0a4b7c51`
- population: `422875449468ae146ef029a4622d8f521f05f570a9b79f90286be03b7b0c1e2c`

A private `git clone --shared --no-checkout` under this seat's output directory supplied read-only access to historical source objects. Before each fixture git mutation, the driver asserted `git rev-parse --show-toplevel` equaled that fixture directory. Source index, refs and worktree were not mutated. The counter was not edited.

`--emit` produced 66 unique corrections for the 70 occurrence rows. The baseline lesson contains exactly those entries, with their emitted derived tokens, correct file, base revision and nonempty scope. The sole mutant difference is one additional syntactically valid, unique, unfenced row:

```text
CORRECTION-R44 id=R44-67 file=SCORECARD.md line=999999 class=mismatch:path-absent stale=synthetic-extra-register-row derived=UNHELD rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=base-SCORECARD-token-referents
```

It has no optional capture/register/disposition fields and no duplicate or retraction. Its single intended fault is absence from the frozen population. SCORECARD and population were unchanged between candidates.

## Commands and observed outputs

Full exact subprocess argv, stdout, stderr and exits are preserved in `commands.txt`; replay construction is in `probe.py`. The executed driver command was:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44critic45/probe.py
```

Each counter invocation was:

```sh
/usr/bin/python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44critic45/frozen-c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44critic45/fixture --rev REV --scratch /fast/scratch/hyaku/souji-r44/S44critic45
```

- Baseline REV: `a51fb17330fb7e791e45107743bbcf765c6549b7`; syntactic entries 66; exit **1**.
- Extra-row REV: `e95d05f9212cfb81250f21f056e6646235305810`; syntactic entries 67; exit **1**.

Both printed exactly:

```text
SUMMARY population=70 corrections=66 registered=0 missing=70 junk=0 fenced=0 duplicate=0 retracted=0 rederive=0 rederive_failed=0 new_mismatches=0 instrument_mismatches=66
```

Receipts: `baseline.txt`, `extra-register-row.txt`, `results.json`, `derivations.tsv`; lesson candidates: `baseline-lesson.md`, `extra-register-row-lesson.md`.

## Counterexample mechanism and smallest safe correction

In frozen `c1-counter.py`:

1. Line 244 indexes corrections by `(sline, scls, stale)`.
2. Line 249 constructs population keys as `(line, token, class)`.
3. Line 253 looks up that incompatible population key in `byrow`. For this population, classes are `mismatch:*` strings and stale tokens are different strings; therefore no normal correction can match. The two observed red results are explained by this defect. An unchanged frozen counter with this unchanged population cannot reach its stated registration target through ordinary grammar-conforming lesson entries.
4. Independently, no comparison rejects `set(byrow) - population_keys`. Line 278 reports `len(key_ok)` as `corrections`, not `len(corrections)`, so the 67th parsed entry is hidden in the displayed count. The observed identical summaries demonstrate that this particular extra row changes no reported field. **Inference, not executed green bypass:** after key-order repair alone, an otherwise valid extra unmatched entry would still be ignored by the population-only matching loop.

Smallest safe correction for the integration owner: use one consistent `(line, token, class)` key throughout; then explicitly reject out-of-population correction keys and count actual parsed corrections. Preserve the intended four duplicate occurrence mappings, so 70 registered occurrences correspond to exactly 66 unique correction entries. A new instrument freeze should pair a passing valid control with a failing one-extra-row control. Do not silently reinterpret these frozen red receipts or claim a green bypass was reproduced.

## Q76 prior-correction audit

The driver searched the **entire SCORECARD blob at the population base**, using both explicit row references and literal tokens, preserving results in `q76-base-audit.txt` and the full blob in `base-SCORECARD.md`.

For the selected real population failure `SCORECARD.md:174`, stale `c1-control-stub.tsv`:

- Base line **399**, L34, already binds `record: census/round-24/records/c1-control-stub.tsv` and restates `cases=8 pass=4` as the original cell's stub-control reading.
- Base line **334**, R30 R15, and line **398**, L33, already correct/restate that cell's runtime fixture count to `cases=12 pass=12`; line **505**, K17, supplies executed-cause provenance.
- Thus a missing bare token referent in the original row is not proof that the lane still believes the old runtime value. Registering its base-tree path is token bookkeeping, not a newly corrected calibration fact.

The synthetic `SCORECARD.md:999999` and `synthetic-extra-register-row` have **no matches** in the whole base SCORECARD. They cannot represent a previously carried self-assessment error or a legitimate new correction.

**Does green prove real calibration? No.** No green was obtained here; even a repaired registration target would only demonstrate the finite token-binding contract, not 70 newly corrected beliefs, correct handling of all prior corrections, or a numeric calibration gain. This limitation agrees with the preregistration's explicit zero-delta and prior-correction caveats. The Q76 audit above is scoped to the selected real failure, not an audit claiming all 70 items were still uncorrected.

## Limits, environment and cleanup

Only the assigned emit, baseline and one-extra-row probes ran. No whole-suite checks, production changes, counter edits, sibling writes, installs, package transactions or service restarts occurred. Existing tools: Python **3.14.8**, git **2.56.0**. Scratch `/fast/scratch/hyaku/souji-r44/S44critic45` was explicitly created and removed; candidate objects and receipts remain in the owned output directory. `probe.py` preserves its construction recipe; a replay needs that scratch directory recreated and a fresh fixture destination.

Self-review: accuracy 4/5 (green bypass deliberately not claimed); completeness 4/5 (extra-row isolation blocked by the frozen key-order defect, with both observed controls retained); clarity 4/5 (separates observations from conditional inference); actionability 4/5 (specific minimal key and set corrections, not applied); conciseness 4/5 (full command transcript is external). Overall 4.0/5. Highest-impact improvement is a newly frozen corrected counter with a passing valid control; this seat is not authorized to change it. The user should agree that unchanged red output is not proof of extra-row detection.
