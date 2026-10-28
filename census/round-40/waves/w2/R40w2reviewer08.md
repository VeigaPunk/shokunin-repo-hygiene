# R40w2reviewer08 — C3 kill attribution

## Attack and verdict: FALSIFIED (partial attribution)

I attacked the claim that the r40 C3 counter's printed failing case names establish branch-specific coverage, particularly whether every mutant has a dedicated case. Landed target: commit `128e412b0ced3c243dc27c3dd3332054a611bc2e`. The committed counter reports kills and names failing fixture cases, but it does not enforce or print a mutant-to-dedicated-case mapping (counter lines 195–199 only prints `score`'s failing list; lines 200–205 only counts kills). In the real run M16 fails four cases, including cases unrelated to `--skip-unrecorded`; the counter still counts that as an unqualified kill. This output therefore does not substantiate a one-mutant/one-dedicated-case attribution contract. M15, M17, and M18 each happen to have one plausibly relevant reported case; M16 is not a dedicated attribution.

Fixture case mapping based on the declared single-defect mutations and asserted behavior (fixture lines 98–120; mutant anchors counter lines 55–68):

- M15 (keep first TOTAL instead of last): `total-conflicting-second` is the dedicated failure; it supplies conflicting second TOTAL and expects malformed. `total-duplicate-identical` passes either implementation; `total-repos-disagrees` exercises the separate repo-count guard.
- M16 (always scan despite `--skip-unrecorded`): intended dedicated case is `skip-unrecorded-suppresses` (fixture lines 110–112). Actual failures also include `good`, `total-duplicate-identical`, and `invalid-utf8-in-comment` because these all invoke the tool with `--skip-unrecorded` (lines 100–103, 118–120). These extra failures show the shared flag effect, not distinct branch cases; the report contains no case-level discriminant proving which assertion caused failure.
- M17 (decode invalid UTF-8 with `ignore` instead of `replace`): `invalid-utf8-in-repo-name` is the dedicated case (lines 114–116); comment invalid-byte case is tolerated under either decoder (lines 118–120).
- M18 (disable repos-count guard): `total-repos-disagrees` is the dedicated case (lines 107–109). The other TOTAL conflict case should be rejected by the duplicate-TOTAL rule irrespective of this guard.

Thus each mutant has a plausible dedicated fixture case by source inspection, but M16's observed kill attribution is broad and includes unrelated baseline scenarios; the counter only labels the aggregate set, with no rule asserting its intended dedicated case appears or other cases remain unaffected. The acceptance subquestion “whether every mutant has a dedicated case”: yes, structurally M15/M16/M17/M18 map respectively to `total-conflicting-second` / `skip-unrecorded-suppresses` / `invalid-utf8-in-repo-name` / `total-repos-disagrees`; however the instrument does not establish dedicated attribution, so the overall kill-attribution claim is falsified.

## Exact command and real output

```sh
S=/fast/scratch/hyaku/souji-r40/w2/R40w2reviewer08; mkdir -p "$S" && trap 'rm -rf -- "$S"' EXIT && export TMPDIR="$S" && python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch "$S"
```

```text
MUTANT M15 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-conflicting-second base:rc=0 fails=0 crash=False failing=-
MUTANT M16 killed=yes base_killed=no rc=1 fails=4 crash=False failing=good,total-duplicate-identical,skip-unrecorded-suppresses,invalid-utf8-in-comment base:rc=0 fails=0 crash=False failing=-
MUTANT M17 killed=yes base_killed=no rc=1 fails=1 crash=False failing=invalid-utf8-in-repo-name base:rc=0 fails=0 crash=False failing=-
MUTANT M18 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-repos-disagrees base:rc=0 fails=0 crash=False failing=-
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e
```

## Evidence locations

- Frozen predicate/control: `census/round-40/preregistration.txt:10-11`.
- Mutant definitions: `census/round-40/c3-counter.py:55-68`.
- Attribution parser and qualification: `census/round-40/c3-counter.py:96-120`; it collects all case failures and treats any `rc=1`, positive failure count, and no stderr traceback as a kill. It does not require a particular case name.
- Counter aggregation/output: `census/round-40/c3-counter.py:195-205`.
- Case bodies and expectations: `tests/fixtures/r40-drift-record-branches.py:98-120`; emitted names/summary: `:140-146`.

Scratch path `/fast/scratch/hyaku/souji-r40/w2/R40w2reviewer08` was removed by the command's EXIT trap. No tools were installed. LSP device unavailable in this runtime (`read xd://lsp` returned “No such tool”); findings use direct source lines and runtime output, not grep as semantic proof.
