# R40 W2 C3 counter mutation probe

Verdict: **SAFE for these five counter-level mutants**: none survived a valid executed probe. One probe (skip base arm) was malformed and inconclusive; it is not counted as killed. No tool installs.

Claim attacked: `census/round-40/preregistration.txt:10-11` (C3 coverage requirement). Landed bytes at `128e412b0ced3c243dc27c3dd3332054a611bc2e`.

Counter mutation sites (landed `census/round-40/c3-counter.py`): crash-marker source check `:115`; anchor-count guard `:187`; base fixture score `:196`; summary-required branch in `score()` `:108-110`; pristine floor `:179`. Mutations were generated only in scratch from `git show REV:census/round-40/c3-counter.py`, then the resulting counter was executed against the committed candidate fixture.

## Exact pristine command and output

```sh
S=/fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester04; mkdir -p "$S" && trap 'rm -rf -- "$S"' EXIT && export TMPDIR="$S" && python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch "$S"
```

```text
MUTANT M15 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-conflicting-second base:rc=0 fails=0 crash=False failing=-
MUTANT M16 killed=yes base_killed=no rc=1 fails=4 crash=False failing=good,total-duplicate-identical,skip-unrecorded-suppresses,invalid-utf8-in-comment base:rc=0 fails=0 crash=False failing=-
MUTANT M17 killed=yes base_killed=no rc=1 fails=1 crash=False failing=invalid-utf8-in-repo-name base:rc=0 fails=0 crash=False failing=-
MUTANT M18 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-repos-disagrees base:rc=0 fails=0 crash=False failing=-
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e
```

## Mutants run against candidate fixture

The runner commands for each mutation had the exact form below, with the indicated mutated temporary counter filename:

```sh
python3 -B /fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester04/<mutation>.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch /fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester04
```

Actual outputs:

- `crash-marker-stdout` (changed `score()` line 115 to inspect `proc.stdout`): rc 0; all four M15-M18 `killed=yes base_killed=no`; summary `mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8`.
- `ignore-anchor-count` (changed line 187 guard to `if False`): rc 0; all four M15-M18 `killed=yes base_killed=no`; same summary.
- `accept-kill-without-summary` (changed lines 108-110 no-summary return to accept rc 1): rc 0; all four M15-M18 `killed=yes base_killed=no`; same summary.
- `lower-pristine-floor` (changed line 179 from `cases >= 8` to `cases >= 0`): rc 0; all four M15-M18 `killed=yes base_killed=no`; same summary.
- `skip-base-arm` (intended to bypass base scoring at line 196): **inconclusive**, generated replacement had a 3-tuple assigned to 2 variables. Actual rc 1 and stderr: `ValueError: too many values to unpack (expected 2, got 3)` at temporary counter line 196. This is a defect in my probe construction, not evidence against the counter; not labeled killed/survived.

Why the executed mutants were killed: the candidate fixture still emits the expected `SUMMARY cases=...` and records real branch failures for the four tool mutants (specific cases shown above), so changing the crash marker source, anchor handling, summary-required fallback, or pristine case threshold does not hide failures in this observed run. These probes test counter defects, not each fixture-contract edge. The skip-base-arm mutant remains untested owing to malformed replacement; no survivor is observed among valid probes.

Scratch `/fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester04` was removed (`SCRATCH_REMOVED True`).