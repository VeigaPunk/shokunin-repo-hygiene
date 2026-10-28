# R40scribe52 — C1 independent calibration attack

- Seat: scribe (leaf; no dispatch)
- Scope: distinct item 52, **temporal-direction false positive: a non-equal commit that is older than its receipt revision**.
- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
- Frozen contract read first: `census/round-40/preregistration.txt:5`.
- Claim under attack: C1 requires all item lines evidence-bound, token-only forgery OPEN, and register `commit` a strict descendant of `receipt_rev`.
- Installs/updates: none; pacman untouched.

## Evidence and commands

Executed repository reads:

```text
read /home/vgpnk/.omp/agent/RULES.md
read skill://godspeed
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt
read /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-39/w1/W1RevC1Register.md:177-207
read /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-39/w1/W1RevC1Forge.md:128-175
```

Exact prior-generation evidence pointer: `.ufo/waves/round-39/w1/W1RevC1Register.md:179-196` records six register rows with `receipt_rev=B commit=A`, where A is B's parent; the report records ancestor direction checks (`A` ancestor of `B` rc=0, reverse rc=1), identical receipt blob SHA-256 at both revisions, and counter output `REGISTER cells=6 mismatches=0 commit_distinct=6`, `SUMMARY ... open=0 ...`, rc=0. Lines 198-206 explicitly conclude the old counter/reconciler never compare commit with receipt revision. This is a sharper distinct case than equality: inequality-based counting treats all six older commits as “distinct” despite the temporal order being opposite the intended strict-descendant direction.

Independent evidence pointer for the other C1 subpredicate: `.ufo/waves/round-39/w1/W1RevC1Forge.md:131-153,163-175` records two bare anchored token lines lacking receipt/revision/path/commit, yet old counter output closes both (rc=0); this is prior-generation control evidence only.

No counter replay, fixture creation, scratch use, or git/jj mutation was performed.

## Verdict

**Concrete falsifier of the r39 control's temporal-order adequacy; r40 C1 NOT MEASURED.** The committed A5 case demonstrates that mere `commit != receipt_rev` does not establish strict-descendant order: all six backwards pairs passed the prior counter and yielded its maximum `commit_distinct=6`, notwithstanding equal receipt bytes. It supports the need for r40's explicit strict-descendant predicate but does not show whether the r40 candidate implements it. The r39 token-only forgery independently establishes the old control's vulnerability, not r40 behavior. No claim of r40 pass/failure is warranted without executing its named counter.

Bounded measurement plan: on the exact candidate revision and explicit scratch path, test register rows in three states: valid strict descendant; equal commit/revision; and parent/older commit with `commit != receipt_rev`. Require only the first state accepted (including a mix of rows to ensure the predicate is row-level), then run the evidence-free anchored token-only item and require OPEN. Preserve stdout, exit codes, and base/candidate revision identifiers. This isolates temporal direction from non-equality and covers the frozen token-only criterion.

## Gates, surfaces, limits

- Gates observed: preregistration contract and committed r39 attack reports; no execution gate.
- Touched surface: this report only, `.ufo/waves/round-40/w1/R40scribe52.md`.
- Out of scope: production files, frozen claims, counters/fixtures, git/jj/index mutation, C2/C3.
- Known limit: cited r39 measurements are reproduced as recorded, not rerun; r40 candidate behavior remains unobserved. No scratch or installs used.
