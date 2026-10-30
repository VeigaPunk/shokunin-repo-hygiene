# S44critic48 — C1 historical-corrected falsification

## Result

**Calibration counter defect reproduced; no green bypass demonstrated.** The honest register and the same register with exactly one incorrect derived token receive identical red summaries. Swapping class/stale fields to reach the matching branch crashes the frozen counter. These are mechanical failures, not evidence that token binding semantically rejects the selected false correction. No judgment/admission decision is made here.

Axes: calibration (directly impacted), operability (counter exception is supporting evidence); coverage untouched. Admission remains outside this leaf review. No production/counter changes, tool installs, delegation, or canonical judge invocation.

## Frozen inputs and bounded experiment

Freeze: `d314fd6e85d62565344fa6c4b102f52f62297884`; population base: `55d7af6f5a22340f7a3de1c386e514ababfaa75f`.

Observed SHA256 pins match preregistration:

- `census/round-44/c1-counter.py`: `dde1ae29105ac84c7ce83705547517c501033b0fce38ddbd6a92b4bd0a4b7c51`
- `census/round-44/c1-population.tsv`: `422875449468ae146ef029a4622d8f521f05f570a9b79f90286be03b7b0c1e2c`

Population: 70 occurrences / 66 unique `(line,token,class)` keys. Duplicated occurrences: line 667/c2-after2.txt, 668/c3-after2.txt, 792/c2-after-d.txt, 793/c3-after-d.txt. Classes across occurrences: 66 path-absent, two digest, two rev-unresolved.

A private clone was created at `/fast/scratch/hyaku/souji-r44/S44critic48/fixture`. The fixture driver explicitly asserted its git top-level before mutations, detached at the freeze, and committed only `corpus/lessons/round-44.md` changes. SCORECARD, population and instruments remained inherited unchanged. The counter was executed directly from the read-only lane, not modified or replaced. The three fixture revisions form a sequence; only lesson content differs.

Exact reproducer driver: `probe.py` alongside this report. Invocation:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44critic48/probe.py
```

The driver expects a clone at the fixture path. Initial clone command:

```sh
git clone --quiet --no-hardlinks /home/vgpnk/Projects/shokunin/souji-shokunin /fast/scratch/hyaku/souji-r44/S44critic48/fixture
```

Each measurement used exactly:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-44/c1-counter.py --root /fast/scratch/hyaku/souji-r44/S44critic48/fixture --rev REV --scratch /fast/scratch/hyaku/souji-r44/S44critic48/counter
```

`--emit` at the freeze first supplied the 66 derivations (exit 0). `emit.tsv`, the three candidate lesson files, raw stdout/stderr, exact argv/revisions/exits in `receipts.json`, and hash pins in `pins.json` are preserved here.

## Concrete counterexample and observed outputs

1. **Natural register**, `cb3f4fb9d701e95c86b7f259fb39de96c69ea679`: all 66 unique keys, correct class/stale fields and exact emitted derived values; BASE_REV and nonempty scope; no optional metadata. Exit **1**, stderr empty:

```text
SUMMARY population=70 corrections=66 registered=0 missing=70 junk=0 fenced=0 duplicate=0 retracted=0 rederive=0 rederive_failed=0 new_mismatches=0 instrument_mismatches=66
```

2. **Single-property false candidate**, `345b575165ee0edf1d763154be62c6f474956574`: identical except R44-09 (line 68, token `42259756…`) changes `derived=sha256:bb506469…` to `derived=UNHELD`. No other lesson field changes. Exit **1**, stderr empty; stdout is **exactly the same summary as the natural register** above. Thus the false token is not shown to be rejected *because it is false*: the honest register already fails identically.

3. **Diagnostic swapped register**, `ddbbdbc42980db069fe6a99035064c978b9e9b65`: class/stale fields exchanged for all rows to reach the internal key matcher. This is intentionally not a valid semantic register and is not an admission candidate. Exit **1**, no stdout, traceback:

```text
  File ".../census/round-44/c1-counter.py", line 259, in main
    dval = derived[(key[0], key[1], key[2])]
KeyError: (792, 'c2-after-d.txt', 'mismatch:path-absent')
```

No unrelated suite or guard battery was run.

## Cause and smallest safe correction

Frozen source establishes two independent defects:

- Population rows are `(line, token, class, reason)`; population keys are `(line, token, class)`. Correction `byrow` keys are instead `(sline, scls, stale)` = `(line, class, token)`. Therefore normal corrections never match. `corrections=66` is `len(key_ok)`, not the number of parsed accepted correction lines, making the diagnostic misleading.
- `derived[row]` stores four-component keys, while line 259 retrieves a three-component key. Reaching a one-correction match raises KeyError before the equality comparison.

[INFERENCE from frozen control flow] With this fixed population, any complete natural register remains red; any key that reaches the one-match branch crashes. The current counter cannot produce its target with a lesson present. This is stronger evidence against reachability than a successful cheating register, but **not** a demonstrated green loophole. No actual forged green receipt was observed or alleged.

Smallest safe future repair: consistently use one `(line, token, class)` identity for `byrow`, derivation storage, lookup and population matching, retaining duplicate-occurrence accounting. Re-run the natural and single-wrong-token fixtures: require honest target/exit 0 and wrong token rejection specifically through derivation mismatch. This requires an authorized counter correction/re-freeze; this seat neither edits the frozen counter nor proposes relaxing its kill rule. Current nonzero outcomes remain nonzero.

## Q76 prior-correction audit: selected line-68 failure

Preserved `q76-round42.txt` is **committed** `corpus/lessons/round-42.md` read at the r44 BASE_REV, not mutable current prose. Its lines 58–71 already explain both line-68 digest tokens and register their scoped derived values:

- Line 66: `CORRECTION-DE line=68 token=42259756… derived=sha256=bb506469… rev=bf618f6c5c09d302994871c94903abbea2deb60d`.
- Line 71: the same binding for `71b89eb3…`.
- Surrounding text says `42259756…` belongs to the sibling fixture, not the tool path the instrument paired it with: an instrument false positive, not a historically false SCORECARD value. The `71b89eb3…` tool digest was true historically and subsequently differs from base bytes.

Independent bounded provenance checks succeeded (exact commands/exits/digests in `q76-hashes.json`):

```text
git show 1efe406e7f39b8fe736be2a566053703a571ffc0:tests/fixtures/r24-coverage-agreement.py
sha256 = 42259756a06538a5dfb81cb82fba20737eacdcfd5c06b9b36594071b26f9da44

git show 1efe406e7f39b8fe736be2a566053703a571ffc0:tools/souji-coverage-agreement.py
sha256 = 71b89eb3c7ce417979c5fce2c759dafe023af21d6310fde49197c766b8f28897

git show 55d7af6f5a22340f7a3de1c386e514ababfaa75f:tools/souji-coverage-agreement.py
sha256 = bb506469be860f994f74f4c7d6eb1c949a4931b676cdb60f9f79de041d12f27f
```

Round-42 lines 49–56 and 73–79 also previously explained/corrected the instrument readings for r44 lines 14 and 92 (digest prefixes misclassified as revisions). These reinforce the distinction between mismatch records and uncorrected historical facts.

**Q76 conclusion:** selected R44-09 is already scoped/corrected historically. Re-registering its instrument-derived token cannot be counted as a newly repaired historical fact. That overlap is **not itself a preregistration violation**: r44 expressly claims token-bound registration, not 70 newly uncorrected facts. A green target, even after a legitimate mechanical repair, would prove at most that registration contract, not broad real-world calibration or correction novelty. Keep the existing historical explanation rather than replacing the fixture digest with a tool digest as though the original were wrong.

## Limitations and disposition

The actual one-field false candidate was rejected, but by an indiscriminate unmatched-key failure; token-sensitive rejection is unproved. The diagnostic swapped candidate intentionally violates grammar semantics and only exposes the second bug. No repaired-counter results, numerical axis deltas, admission, or acceptance are claimed. Q76 provenance was independently checked for the selected line-68 failure; no complete prior-correction census of all 70 occurrences is claimed.

Fixtures and receipts are retained in this seat directory; private scratch is removed before terminal handoff. No tool installed/updated. Proposed additional guard batteries were not executed and are not evidence.

Self-evaluation: accuracy 4 (three executed probes plus historical hashes; unreachable-target statement explicitly marked inference); completeness 4 (requested falsification and selected Q76 audit complete, no full-population historical audit claimed); clarity 4 (mechanical failure separated from permitted re-registration); actionability 4 (two precise identity repairs, not applied under freeze); conciseness 4 (raw receipts separate). Overall 4.0. Improvements: authorized owner should re-freeze consistent key plumbing, then use these differential fixtures to establish real token-sensitive rejection. User agreement self-check: evidence supports a counter defect, not a green bypass or a new historical fact repair.
