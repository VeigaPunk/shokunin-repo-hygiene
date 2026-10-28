# R40executor61 — C1 stale-evidence grounding attack

## Axis and named edge case

**Calibration; edge case: an invented `stale` token is treated as evidence.** This is distinct from the frozen token-only forged-line case and from commit/receipt revision ordering: it tests whether the *negative/stale side* of the citation has historical support at all. A resolvable citation and receipt do not establish that the claimed stale reading existed.

## Evidence pointers

- Frozen claim: `census/round-40/preregistration.txt:4-5` requires evidence-bound anchored item lines and a strict-descendant commit-vs-`receipt_rev`; control is r39's token predicate.
- The r39 reconciler contract: `tools/souji-citation-reconcile.py:13-18,20-36`. The citation needs anchor, expected token, receipt path, and absence of stale token on that line; commit validation checks resolvability, ancestry to audit revision, citation naming, and expected token in the receipt at commit. It does **not** establish that `stale` ever occurred in prior bytes.
- Committed r39 attack record: `census/round-39/waves/w1/W1RevC1Register.md:208-222`. It records `stale=legs=3`, reports no `legs=3` hit in any citation/receipt blob across fixture history (command shown at lines 210-215; `rc=1`), yet the counter summary remained clean (`cells=6 mismatches=0 commit_distinct=6`, `rc=0`, lines 217-222). This is a direct positive control that the old predicate can accept a fabricated stale token even when other register checks succeed.
- The same report distinguishes its behavior from the absent-register/zero-count issue at `W1RevC1Register.md:224-281`; this finding is specifically about unsupported stale claims, not a no-evaluation state.

## Commands and observed evidence

No new commands were run against the lane or fixtures. Exact already-committed commands/output retained in `census/round-39/waves/w1/W1RevC1Register.md:208-222`:

```text
$ git -C $D grep -n 'legs=3' $(git -C $D rev-list --all) -- census/r.txt SCORECARD.md LOG.md SIDE.md
rc=1     (no match in any citation or receipt blob at any revision)
Counter: SUMMARY items=1 open=0 register_cells=6 register_mismatches=0 commit_distinct=6 ... rc=0.
```

The fixture control is recorded at `W1RevC1Register.md:77-85`: baseline register yields `cells=6 mismatches=0 commit_distinct=6`, `rc=0`. Thus the fabricated-stale result is not explained by a generally failing harness.

## Verdict

**Confirmed legacy failure mode; no direct verdict on an unobserved r40 implementation.** r39 accepts an ungrounded stale claim while returning success. Consequently, evidence-bound C1 should be measured not only with token-only anchor prose, but also with a citation whose positive receipt and commit checks all pass while its declared stale token is absent from every prior candidate source. If r40 claims evidence-bound stale claims yet accepts this case, that claim is falsified. This does not imply the frozen r40 predicate explicitly requires historical stale-token validation; the stated predicate requires resolvable evidence pointers, so this is a bounded calibration probe of what those pointers actually substantiate.

## Bounded measurement plan

Use an isolated git fixture and the explicit r40 base/candidate revisions. Establish a green baseline with an evidenced stale value. Then create a single-defect arm: retain the same valid anchor, expected value, receipt pointer, receipt revision, and strict-descendant commit; replace only the stale token with a unique value absent from every prior committed citation/receipt blob. Run the r40 counter against both arms and preserve exact revisions, command lines, output and exit status. Expected discriminant: baseline passes; unsupported-stale arm is rejected if r40 evidence semantics include historical support for stale claims. Record that arm separately from forged token-only and equal/backwards commit arms. Use a fresh fixture verified by `git rev-parse --show-toplevel`; explicit scratch/TMPDIR; no lane mutations.

## Scope and housekeeping

Only this assigned report was written. No installs, git/jj/index mutations, tests, or checks were performed; no scratch was created, so there is no scratch cleanup. Risk: r40 implementation and receipt are not yet available in the committed evidence inspected here, so acceptance/rejection by r40 remains unmeasured. Blockers: none for the bounded fixture measurement once the r40 counter and register schema are available.
