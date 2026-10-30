# S44reviewer61 — C1/Q76 source and correction scope

Axes: calibration / operability / coverage. This review measures calibration only. Frozen revision: `d314fd6e85d62565344fa6c4b102f52f62297884`.

## Findings, by severity

**Medium — counting registrations as new corrections would overstate calibration.** The 70 r44 population occurrences are exactly the r42 population, including multiplicity: **65 previously accounted-for path occurrences + 5 previously scoped correction occurrences; 0 newly unaccounted self-assessment mismatches under Q76**. There are **66 unique keys**, not 70 distinct defects. Duplicate excess is four: `(667,c2-after2.txt)`, `(668,c3-after2.txt)`, `(792,c2-after-d.txt)`, `(793,c3-after-d.txt)` each appears twice.

Evidence: `census/round-44/c1-population.tsv:2-71`, `census/round-42/c1-register.tsv:2-71`, and the exact frozen multiset join in `audit.py`. `classification.tsv` identifies the prior evidence for every occurrence. Q76 (`corpus/QUALITY.md:186`) explicitly excludes/counts as agreeing a before-state erased by existing correction/binding rows. The r44 counter never reads the r42 register or lesson: it instead requires new `CORRECTION-R44` lines (`census/round-44/c1-counter.py:204-260`). Thus `missing=70` means missing r44-format registration, not 70 outstanding semantic corrections. The frozen preregistration already acknowledges this distinction (`census/round-44/preregistration.txt:4`); retain that constraint and zero numerical score delta. No actionable change to the frozen counter is requested.

### The five previously corrected/scoped occurrences

| SCORECARD line / token | Existing evidence in `corpus/lessons/round-42.md` | Honest interpretation |
|---|---|---|
| 14 / `65817d0d` | lines 49-56 | Tool sha256 prefix mistaken for a revision; not a false tool assertion. |
| 68 / `42259756…` | lines 58-66 | Fixture digest paired with sibling tool path; cross-cell false positive. |
| 68 / `71b89eb3…` | lines 68-71 | Actual historical tool digest, stale against later bytes; already corrected with revision scope. |
| 92 / `09bb8e0d` | lines 73-79 | Historical tool sha256 prefix mistaken for a revision. |
| 175 / `c2-after.tsv` | lines 81-87 | Heading-context ambiguity; prose already identifies `census/round-24/records/c2-after.tsv`. |

The other 65 occurrences are already bound to committed paths by the r42 register. Its frozen derivation honors round-heading context, canonical knowledge paths and archived wave mappings (`census/round-42/c1-counter.py:25-34,98-121`). R44's basename candidate lists/UNHELD tokens are different syntactic derivations, not evidence that those bindings stopped being valid. This is registration hardening, not 70 new fact repairs.

## Exact bounded commands and observed output

From `/fast/scratch/hyaku/souji-r44/S44reviewer61`:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44reviewer61/audit.py
```

The retained driver reads all inputs with `git -C <lane> show <frozen>:<path>`, compares population multisets, emits per-occurrence prior bindings, and runs the two independent C1 counters concurrently. Exact stdout/exit receipts are in `audit.txt`, `r42-counter.py.txt`, `r44-counter.py.txt`.

```text
population_occurrences=70 unique_keys=66 duplicate_excess=4
prior_population_identical_keys_and_multiplicity=True
new_population_occurrences=0
already-accounted-path=65
already-corrected-scoped=5
remaining_new_self_assessment_mismatches_under_Q76=0
```

Executed commands (counter source extracted unchanged from the frozen revision into seat scratch):

```sh
python3 -B /fast/scratch/hyaku/souji-r44/S44reviewer61/r42-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev d314fd6e85d62565344fa6c4b102f52f62297884 --scratch /fast/scratch/hyaku/souji-r44/S44reviewer61
# SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0
# EXIT=0
python3 -B /fast/scratch/hyaku/souji-r44/S44reviewer61/r44-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev d314fd6e85d62565344fa6c4b102f52f62297884 --scratch /fast/scratch/hyaku/souji-r44/S44reviewer61
# SUMMARY population=70 corrections=0 registered=0 missing=70 junk=0 fenced=0 duplicate=0 retracted=0 rederive=0 rederive_failed=70 new_mismatches=0 instrument_mismatches=66 lesson=absent
# EXIT=1
```

R44's `instrument_mismatches=66` is the dictionary-deduplicated count (`instrument_rows`, lines 104-111), not the occurrence count of 70. Its failure at the freeze is expected: the round44 lesson is absent, while r42 accounting still passes unchanged. Counter/population hashes matched the frozen preregistration; full hashes are in `audit.txt`.

## Residual risk and verification gaps

- Zero is the **new/unaccounted count for this fixed population under Q76**, not proof that every SCORECARD sentence is true or the raw scanner is clean. Raw historical spellings remain append-only; the r42 counter still reports five formally unresolved tokens, all five corrected with explicit scope.
- No post-freeze candidate, round admission, score increase, runtime routing, resume continuity, saturation, or C2/C3 behavior was evaluated; those are outside this seat's assigned C1 scope. Recommendation only; admission remains non-author closure.
- `xd://lsp` is unavailable (device returned “No such tool”), so semantic status/references/definition/diagnostics could not run. Source reading and literal searches are fallback evidence, not LSP semantic proof.
- No tools installed/upgraded; no production edits, commits, index/jj changes, delegation, fleet writes, or whole-suite checks. Scratch is removed before yield; reproducible driver and receipts remain only in this seat output.

Self-check: accuracy 4 (frozen multiset plus canonical r42 run; not a full prose truth audit), completeness 4 (all 70 classified; no later candidate assigned), clarity 4 (separates occurrence/key/semantic counts), actionability 4 (retained exact driver and receipts; integration is L1-only), conciseness 4 (per-row detail externalized). Overall 4.0. Main improvement: preserve this count distinction in closure rather than claiming a fresh mismatch reduction.
