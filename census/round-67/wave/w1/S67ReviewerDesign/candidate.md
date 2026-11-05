# S67ReviewerDesign — candidate.md (attack line 6: candidate byte review)

Candidate: `.ufo/waves/round-67/w1/S67ExecWriter/candidate/souji-receipt-write.py`
sha256 `b811ee2a7a67d8d3ea6d00fb3a44780ccb807113b9eeaf28f09e01448715a725` (1478 → 1591 lines).
Base: `a8c47d362a901c222f9582b8b96609fba39cb5e0e662d4057e724db96c1097fc` (1478 lines).

## Delta inventory (diff vs base; verified hunk-by-hunk; ONLY spec deltas)

| # | location | delta | spec clause bound |
|---|---|---|---|
| 1 | module docstring | new r67 paragraph (words only) | C1 predicate prose |
| 2 | `git()` env scrub | adds `GIT_COMMON_DIR` to the scrub tuple | C1 "every git call scrubs the variable" |
| 3 | new `_check_env_commondir(root)` + one call site before other git-touching steps | refuses `RECEIPT-ENV-COMMONDIR-MISMATCH` on empty value, unresolvable common dir, or `os.path.realpath(value) != os.path.realpath(os.path.join(root, rev-parse output))`; resolution call runs through the scrubbed `git()` so the caller value is never read back; prints the variable name only | C1 "mismatching or empty value refuses … before any git call reads caller env; equal value accepted (W3)" |
| 4 | writer selftest | four new cases c34-c37 (mismatch refused + value-not-echoed; match accepted absolute AND relative; empty refused; unresolvable refused) + SELFTEST CASES registration | W1/W2/W3 shapes + empty/unresolvable classes |

No other hunks exist (diff line total 124, all accounted for by the four regions above plus their registrations).

## r66 behavior preservation (E1-E6, MOD2/MOD3, SY3, T-rows)

- The only modifications to pre-existing lines are the docstring paragraph and the single scrub-tuple line;
  every refusal list, snapshot computation, in-run diff, symlink record, index-flag scan and env gate of the
  r60-r66 surface is byte-identical in both files.
- The writer selftest grew from 33 cases to 37; all 33 pre-existing cases re-run green in the delivered bytes
  (`SELFTEST cases=37 pass=37 fail=0` — receipt `receipts/candidate-selftest-37.log`,
  sha256 `a9de94337e3fcd0a228586ab2b5ecefba3fb33c88b6207a764063151f7422180`).

## Vectors checked and closed

- **Value echo**: refusal message names ONLY the variable ("value not shown"), and the selftest asserts the
  common-dir copy path does not appear in stderr (case_34).
- **Env read-back trap**: because GIT_COMMON_DIR is scrubbed on every git() call, `rev-parse --git-common-dir`
  cannot echo the forged value; a scrub-less implementation would compare env against env and vacuously accept
  every redirect — the candidate avoids this (byte review item 3).
- **Relative-form acceptance**: `rev-parse` prints `.git` relative; candidate joins root and realpaths before
  comparing, and its selftest exercises the relative `.git` value from cwd=d (case_35).
- **Empty-value honesty**: presence is the test; case_36 refuses empty; git 2.56.0 itself fails under empty
  (scratch-probed), so no honest-run trade is introduced.
- **Unresolvable common dir**: case_37 covers GIT_COMMON_DIR set with --root outside any repository.

## Residual gaps for the operator/L1

- The 31-row counter run against the candidate (the C1 after arm) is the L1's landing-run job; this seat did
  not duplicate it (do-nothing control stands as matrix evidence; candidate review here is byte- and
  selftest-level).
- The candidate byte set is delivered under the executor's seat dir; L1 integration (copy into tools/,
  commit, receipts) is exclusively L1-owned per the wave contract.
