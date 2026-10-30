# S44critic47 — C1 scope-forgery falsification

## Result and axes
Calibration is the reviewed axis; operability/coverage were not evaluated. **No green scope-forgery demonstrated: the frozen counter rejects both valid-field and forged-scope registers before evaluating scope.** This is an instrument defect, not evidence that forged scope is detected. No judgment, admission or integration is supplied.

Frozen registration: `d314fd6e85d62565344fa6c4b102f52f62297884`. Derivation base: `55d7af6f5a22340f7a3de1c386e514ababfaa75f`.
Counter SHA256: `dde1ae29105ac84c7ce83705547517c501033b0fce38ddbd6a92b4bd0a4b7c51`.
Population SHA256: `422875449468ae146ef029a4622d8f521f05f570a9b79f90286be03b7b0c1e2c`.
Population: 70 occurrences, 66 distinct `(line,token,class)` keys. Both hashes match preregistration.

## Strongest counterexample
The sandbox register copies all 66 `--emit` derivations exactly, uses correct ids/revision/file, and replaces only scope with 66 fabricated nonempty tokens: alternating `docs/fabricated/R44-scope-ledger-NN.md` and `R44-fake-registry-r44-NN-scope`. None is a tracked BASE path. No accompanying measurement-scope prose is provided. Comparison arm changes these tokens to the real base path `SCORECARD.md`; it is a syntactic reference control, not a claim of full Q101 prose compliance.

Both arms unexpectedly reject with precisely the same summary:
```
SUMMARY population=70 corrections=66 registered=0 missing=70 junk=0 fenced=0 duplicate=0 retracted=0 rederive=0 rederive_failed=0 new_mismatches=0 instrument_mismatches=66
```
Exit 1. Thus there is no green result to interpret as real calibration.

### Root cause, frozen source lines 241–260
- Population rows are `(line,token,class,reason)` (line 171).
- `byrow.setdefault((sline,scls,stale),...)` creates `(line,class,token)` keys (line 244).
- `keys={(r[0],r[1],r[2]) ...}` creates `(line,token,class)` keys (line 249).
- Consequently every canonical correction misses lookup at line 253 and cannot reach token/scope comparison.
- A diagnostic swaps class/stale on only R44-01 to reach this lookup. It exits 1 with **uncaught KeyError**, not a target summary:
```
File ".../census/round-44/c1-counter.py", line 259, in main
  dval = derived[(key[0], key[1], key[2])]
KeyError: (14, '65817d0d', 'mismatch:rev-unresolved')
```
A second defect: `derived` is keyed by the full four-tuple (line 191), but this lookup uses three fields. The diagnostic deliberately violates grammar semantics and is not a proposed lesson.

### Scope-specific finding (static, not an executed green bypass)
`CORRX` requires `scope=(\S+)`; line 234 stores only `bool(sscope)` and line 260 checks that boolean. No scope-to-prose/source binding exists. Even after the key defects are repaired, this source logic cannot distinguish truthful scope from a fabricated nonempty token. This is an inference about repaired behavior; the frozen run never reaches it. Q101 requires measurement tree/path, revision and appropriate exclusions **in prose**, not arbitrary token presence. Do not treat a future green registration target as substantive calibration without that independent content check.

## Bounded controls
| Candidate | Exit | Observation |
|---|---:|---|
| Do nothing at frozen registration | 1 | population=70, corrections=0, registered=0, missing=70, rederive_failed=70, lesson=absent; matches committed do-nothing receipt |
| Full emit-derived register, forged scope | 1 | summary quoted above |
| Same register, scope=SCORECARD.md | 1 | identical summary |
| Remove scope from all 66 lines | 1 | same missing=70, junk=66 |
| Corrupt first derived token, forged scope | 1 | identical to forged arm: derived comparison is unreachable |
| Swap first correction's class/stale | 1 | KeyError shown above |

The printed `corrections=66` is `len(key_ok)`, not a count of accepted corrections: the no-scope arm still prints it. No frozen file was changed.

## Q76 prior-correction audit: selected SCORECARD:14 failure
Frozen BASE's `corpus/QUALITY.md:186` requires the before-state to honour earlier correction/supersession rows. Audit searched the complete BASE SCORECARD for its line anchor and literal `65817d0d`, and inspected earlier lessons at that same revision. Evidence is retained in `receipts/q76-frozen-audit.txt`.

- `corpus/lessons/round-42.md:49–56` already names `SCORECARD.md:14` and explains that `65817d0d` is the prefix of tool digest `65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4`, not a revision. It carries `CORRECTION-DE line=14 token=65817d0d derived=rev-unresolved rev=bf618f6c5c09d302994871c94903abbea2deb60d`.
- BASE `SCORECARD.md:845` explicitly carries forward the round-42 C1 outcome and the five scoped correction lines in that lesson. The historical cell is therefore not a newly uncorrected fact simply because the instrument still reports its literal token.
- Q101 already exists at BASE `corpus/QUALITY.md:257`; the r42 lesson's scoped correction predates r44. This audit does not claim that its prose is flawless or that it fixes the r44 counter's key bugs.
- r44 preregistration correctly labels C1 registration rather than 70 newly corrected facts. Keep that distinction: this probe earns no numerical calibration delta and does not erase the prior correction.

## Exact reproduction and retained evidence
All commands used a fixture under `/fast/scratch/hyaku/souji-r44/S44critic47/`; production was read-only. Setup:
```
git clone --quiet --shared --no-hardlinks /home/vgpnk/Projects/shokunin/souji-shokunin /fast/scratch/hyaku/souji-r44/S44critic47/fixture
git -C <fixture> rev-parse --show-toplevel
# asserted exactly the fixture path before fixture mutations
git -C <fixture> checkout --quiet --detach 55d7af6f5a22340f7a3de1c386e514ababfaa75f
python3 -B <lane>/census/round-44/c1-counter.py --root <fixture> --rev d314fd6e85d62565344fa6c4b102f52f62297884 --scratch <seat-scratch>/cnt-emit --emit
```
Each candidate tip contains only the unchanged frozen population plus its candidate lesson on BASE. Population is absent at BASE itself: the initial lesson-only fixture tips correctly refused `POPULATION-ABSENT` (exit 2); population was then added byte-identically, not fabricated or weakened.

Reproduce a final candidate using its retained `receipts/<variant>.patch`: apply in the explicitly asserted fixture, add `corpus/lessons/round-44.md` and `census/round-44/c1-population.tsv`, commit there using `git -c user.name=S44critic47 -c user.email=s44critic47@fixture commit --quiet -m 'fixture candidate'`, then run:
```
python3 -B <lane>/census/round-44/c1-counter.py --root <fixture> --rev <full40-candidate> --scratch <seat-scratch>/cnt-<variant>
```
Each `receipts/variant-*.txt` contains the actual full candidate revision, stdout/stderr and exit code. `lesson-*.md` preserves every complete candidate; patches preserve the full candidate tree delta. `emit.txt`, `setup.txt`, frozen counter/population copies and the Q76 audit preserve source/provenance. Fixture-only git commits/resets were used, never lane/index mutations.

## Smallest safe correction and limitations
Do not change this frozen instrument under the existing claim. Record its target as not reached by these probes. For a separately registered repair, use one canonical three-field key consistently in population, correction and derivation maps; retain the complete reason only as metadata. Require a separate Q101 scope/source/prose review or a specified source-bound scope schema; a nonempty token is insufficient. Preserve Q76 authority and do not relabel registration as fresh historical correction.

No green bypass is claimed; no independent judgment is supplied. Only C1 bounded probes ran. No production changes, tool installs/upgrades, package transactions, sibling edits, shared bookkeeping edits, or other runtime invocation. Scratch was removed after preserving receipts.

## Review self-evaluation
Accuracy 4/5: distinguishes observed rejection from inferred scope weakness; semantic green remains untested because frozen key handling prevents it. Completeness 4/5: all assigned probe/audit evidence retained, but the requested green discrimination is unreachable. Clarity 4/5: primary rejection and latent flaw separated; reproduction includes setup-specific population caveat. Actionability 4/5: patches and raw outputs retained; repaired-schema design belongs to a new registration. Conciseness 4/5: detailed commands retained for reproducibility. Overall 4.0/5; highest-impact next work is a separately frozen key-consistency repair, not more scope mutants against this unreachable target. The report states the limitation rather than implying an achieved forgery.
