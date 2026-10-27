# C1 delivery — G11 (SKILL.md:234 as frozen, `tests/fixtures/r20-input-binding.py`)

Verdict: **MISMATCH at base and at the tip → genuine value drift → `same`-argv restatement.**
Row to append: `### Round 34 registry restatements` with the single row at the end of this file
(validated against the frozen counter in a scratch clone).

## Counter ITEM line (verbatim)

```
ITEM	G11	MISMATCH	original	rc=0 expect_exit=0 predicate fails last=SUMMARY total=45 pass=45 fail=0 blocked=0 inventory=exact baseline_mismatches=not-requested load=7.91
```

At the tip `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`:

```
ITEM	G11	MISMATCH	original	rc=0 expect_exit=0 predicate fails last=SUMMARY total=45 pass=45 fail=0 blocked=0 inventory=exact baseline_mismatches=not-requested load=13.60
```

## Command (executed)

```
export TMPDIR=/fast/scratch/hyaku/souji-r34/RestateC1s2/tmp
flock /fast/scratch/hyaku/souji-r34/RestateC1s2/ser.lock \
  python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev 9c76c7222a8abff027af42e37f0d160d52526bba \
  --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 \
  --scratch /fast/scratch/hyaku/souji-r34/RestateC1s2/cnt --only G05,G07,G09,G11,G12
```

Exit 1; `SUMMARY items=5 agree=3 mismatches=2 restated=0 partial=1`. Load before `2.84 2.72 1.92`,
after `7.83 4.61 2.74`. Counter sha256 at `--list-rev`
`1ad8c86c9d78b79f095661850ca9883994a5d5a9d5ee629cb69e26dcd6ff9a20`.

## Prior-correction / supersession grep (base `9c76c72:SCORECARD.md`)

```
grep -c -F 'G11' sc-base.md                                -> 0
grep -c -F 'SKILL.md:234' sc-base.md                       -> 0
grep -c -F 'input-binding' sc-base.md                      -> 0
grep -c -F 'Round 34 registry restatements' sc-base.md     -> 0
```

No correcting/superseding/binding row exists for this cell; not AGREE under Q76.

## Cause (executed, parent vs cause)

Fixture history is exactly three commits:

```
1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1  round-20: exact auditor grants and complete caller inputs
4f30f23e26bff29dfc18807298300402bc148cae  round-20: close final grant and caller falsifiers
98e5203d45b4e419a9e72801733d93303acc7ebd  round-32: C2 scratch discipline …
```

Cause full40 **4f30f23e26bff29dfc18807298300402bc148cae**; its first parent is
`1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1` (`git rev-parse 4f30f23^1`). `git diff --stat` of the
cause over the fixture: `1 file changed, 265 insertions(+), 11 deletions(-)`.

Readings executed in a scratch clone (`--no-local`, origin removed, `checkout -qf --detach <rev>`,
cwd = clone root, `env -i PATH=/usr/bin:/bin TMPDIR=<fresh> GIT_CONFIG_NOSYSTEM=1`):

| rev | role | rc | last lines | frozen predicate |
|---|---|---|---|---|
| `1988860e…` | cause^1 | 0 | `INVENTORY exact expected=36 observed=36 missing=- unexpected=- duplicates=0` / `SUMMARY total=36 pass=36 fail=0 blocked=0 inventory=exact baseline_mismatches=not-requested` | holds |
| `4f30f23e…` | cause | 0 | `INVENTORY exact expected=45 observed=45 …` / `SUMMARY total=45 pass=45 fail=0 blocked=0 inventory=exact baseline_mismatches=not-requested` | fails |
| `98e5203d…` | later | 0 | `SUMMARY total=45 …` | fails |
| `9c76c722…` | base | 0 | `SUMMARY total=45 …` | fails (counter ITEM line above) |
| `51acb5fb…` | tip | 0 | `SUMMARY total=45 …` | fails (counter ITEM line above) |

Loads recorded beside those runs: `6.94` (base counter run), `13.60` (tip counter run); the four
direct fixture runs were serialized under the same `flock` at load `2.84`–`7.83`.

## Proposed row (exact text, validated)

```
| G11 | SKILL.md:234 | restated | 0 | same | `SUMMARY total=45 pass=45 fail=0 blocked=0 inventory=exact baseline_mismatches=not-requested` | 4f30f23e26bff29dfc18807298300402bc148cae | The round-20 close commit 4f30f23 extended the fixture from 36 to 45 caller-helper cases (its parent runs INVENTORY expected=36 observed=36, the cause runs expected=45 observed=45), so the default invocation SUMMARY now reports 45; the landed row carried the 36-case reading. |
```

Validation: appended under a fresh `### Round 34 registry restatements` heading in a scratch clone on
top of the lane tip (`51acb5f`), committed with a throwaway identity, then measured with the frozen
counter at the scratch revision `9d220d05b2887ca7ef77bc69ab892b9501638b94`:

```
ITEM	G11	AGREE	restated	rc=0 expect_exit=0 statement is the run's last digit-bearing line last=SUMMARY total=45 pass=45 fail=0 blocked=0 inventory=exact baseline_mismatches=not-requested load=57.62
SUMMARY items=1 agree=1 mismatches=0 restated=1 partial=1 rev=9d220d05b2887ca7ef77bc69ab892b9501638b94
EXIT=0
```

Mechanics checked by that run: `where` equals the frozen cell; `same` argv; statement is the run's
collapsed LAST digit-bearing line; cause is an ancestor of `--list-rev`, touches
`tests/fixtures/r20-input-binding.py`, and the original (exit, predicate) was executed True at its
parent and False at the cause inside the counter's own `judge`.

Note for the L1: `where` is frozen as `SKILL.md:234`, but the r20-input-binding row actually sits on
line 235 (`SKILL.md:234` is the r20-audit-contract row). The `same`-argv path does not read that
line, so the row above is unaffected; the frozen value must still be copied verbatim.
