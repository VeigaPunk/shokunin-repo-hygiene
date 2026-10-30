# S44critic46 — removed-population falsification

Axes: calibration (assigned), operability, coverage (no claimed changes). Admission remains outside this review.

## Result

**Observed rejection, not a demonstrated population-integrity defense. No green target was obtained.** The unchanged frozen counter rejects even the complete syntactically valid 66-correction control because its population and correction keys use different field orders. Removing one duplicate population occurrence also rejects for this unrelated reason. Removing all rows explicitly refuses. Therefore this experiment does not establish that population removal could pass a working counter, nor that rejection demonstrates real calibration.

A green registration target would not itself prove new calibration: preregistration explicitly limits C1 to token-bound registration and preserves already-corrected history. This frozen implementation cannot support that stronger conclusion, and the probes reveal an independent feasibility defect.

## Frozen evidence and fixture isolation

Read `census/round-44/preregistration.txt`; counter SHA256 `dde1ae29105ac84c7ce83705547517c501033b0fce38ddbd6a92b4bd0a4b7c51`, population SHA256 `422875449468ae146ef029a4622d8f521f05f570a9b79f90286be03b7b0c1e2c`, both matched registration. Copies and hashes are preserved here.

Fixture: `/fast/scratch/hyaku/souji-r44/S44critic46/fixture`, cloned shared/no-checkout from the lane, checked out at `d314fd6e85d62565344fa6c4b102f52f62297884`. Before checkout, add, and commit, `git rev-parse --show-toplevel` was asserted equal to that exact fixture path. No lane/domain/index edits occurred. Fixture commits used local per-command identity, disabled signing/hooks and maintenance. Scratch was deleted after receipts were preserved. Existing Python 3.14.8 and git 2.56.0; no installs, pacman transactions, or service changes.

## Construction and exact probe receipts

Setup commands (executed by the fixture driver through subprocess):

```
git clone --shared --no-checkout /home/vgpnk/Projects/shokunin/souji-shokunin /fast/scratch/hyaku/souji-r44/S44critic46/fixture
git rev-parse --show-toplevel
git -c maintenance.auto=false checkout --detach d314fd6e85d62565344fa6c4b102f52f62297884
```

The frozen counter was extracted with `git show d314fd6e85d62565344fa6c4b102f52f62297884:census/round-44/c1-counter.py`. It was never edited. `emit.txt` records the exact successful `--emit` command and 66 emitted records. Each emitted record became:

```
CORRECTION-R44 id=<emitted-id> file=SCORECARD.md line=<emitted-line> class=<emitted-class> stale=<emitted-token> derived=<emitted-derived> rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f scope=frozen-population
```

`candidate-lesson.md` preserves all 66 lines. This was committed as the complete control. The sole mutant change removed one of two identical occurrence records at population line 35 (SCORECARD line 667, token `c2-after2.txt`, class `mismatch:path-absent`). The lesson, SCORECARD, instruments, and counter were unchanged between control and mutant. All 66 unique identities remained; occurrence count fell 70 to 69. `candidate-population.tsv`, `removed-occurrence.txt`, and `candidate.patch` preserve the mutation. A third fixture commit retained only the population header.

Each receipt contains the full exact command including its full-40 fixture revision; `probe-results.json` records revisions, return codes, stdout and stderr. Commands used the preserved unchanged counter, `--root <fixture> --rev <fixture-full40> --scratch /fast/scratch/hyaku/souji-r44/S44critic46/counter`.

`complete-control.txt`:

```
SUMMARY population=70 corrections=66 registered=0 missing=70 junk=0 fenced=0 duplicate=0 retracted=0 rederive=0 rederive_failed=0 new_mismatches=0 instrument_mismatches=66
EXIT=1
```

`removed-population.txt`:

```
SUMMARY population=69 corrections=66 registered=0 missing=69 junk=0 fenced=0 duplicate=0 retracted=0 rederive=0 rederive_failed=0 new_mismatches=0 instrument_mismatches=66
EXIT=1
```

`empty-population.txt`:

```
REFUSAL POPULATION-EMPTY
EXIT=2
```

These were the only scoring probes; no whole-suite validation was run.

## Mechanism and strongest counterexample

Frozen counter lines 159–174 load the population from candidate `--rev`, without checking the frozen digest or exact occurrence count. Lines 281–283 compare `registered` with candidate `len(rows)`, not literal 70. Removing a duplicate occurrence leaves the identity set unchanged, so `new_mismatches` cannot detect this removal. The observed mutant summary confirms `population=69`, `new_mismatches=0`. This is a concrete population-identity weakness, but **not an observed false-green**.

The actual blocking defect is lines 244 versus 249: correction lookup keys are `(line, class, stale)` while population keys are `(line, token, class)`. Valid emitted corrections never match, hence both probes report zero registrations. `corrections=66` is `len(key_ok)` (population unique keys), not proof that 66 correction records were accepted. A second static defect lies behind the first: line 191 stores derivations keyed by four-field population rows, while line 259 looks up a three-field tuple. This second defect was not separately executed or patched.

## Q76 prior-correction audit

`q76-audit.txt` preserves searches over the whole **base** SCORECARD for `SCORECARD.md:667` and the exact literal `c2-after2.txt`, plus base lessons r41/r42/r43 and QUALITY Q76. The sole SCORECARD literal hit is the original line 667, which uses the same bare token twice. No same-cell correction pointer occurs anywhere in base SCORECARD; the three checked lessons contain neither pointer nor literal. Thus no prior same-cell correction was found by the required whole-self-assessment audit. This does not assert exhaustive coverage of every historical document.

The selected failure is loss of one duplicate population occurrence, **not** a newly discovered operability defect in the r38 fixture. Its two occurrences represent one mismatch identity, not two independent calibration facts. Q76 forbids counting an already corrected value as fresh work; absence of a same-cell prior correction in this bounded audit does not convert registration into a new numeric score gain.

## Impact and smallest safe correction

Calibration is impacted: population authority comes from candidate bytes; the exact frozen occurrence target is not enforced, and valid registration is presently unreachable. Operability is impacted only in the narrow sense that the C1 evaluator cannot accept its own emitted correction grammar. Coverage changes were not tested or claimed.

Smallest safe future correction (integration owner only; **not applied here**): canonicalize one `(line, token, class)` key everywhere, use it consistently for derivation lookup, and bind population bytes to the preregistered digest (or exact frozen rows with multiplicity), including literal 70/66 target counts. Preserve the current registration-only claim and Q76 history. Re-freezing and admission are not this seat's authority. A corrected, newly authorized counter would need to rerun the same complete control and removed-duplicate mutant; present rejection is not evidence of that future result.

## Limitations and self-check

No false-green reproduced; rejection is confounded by the unrelated key-order defect. Empty-population refusal is directly observed. The latent derivation-key exception and conditional duplicate-removal escape are static findings, not executed corrected-counter results. No counter or production repairs were attempted.

Self-evaluation: accuracy 4 (conditional escape is explicitly unexecuted); completeness 4 (bounded Q76 search, not all historical documents); clarity 4 (separates actual rejection from conditional loophole); actionability 4 (minimal correction named, no authorized re-freeze performed); conciseness 4 (full commands remain in receipts). Overall 4.0. Improvement priority: an authorized corrected instrument should establish a passing control before interpreting mutant rejection. The user should agree that this report makes no calibration gain or admission claim.
