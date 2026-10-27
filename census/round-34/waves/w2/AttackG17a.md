## Status

W1's executed defect finding is real: G17a is red at base and tip, and its value-drift restatement is rejected by the frozen file-binding rule. I found no honest rule-conforming correction. One important qualification: the frozen counter mechanically accepts a `--keep-only` argv correction, but the route is not honest for G17a because `where=SKILL.md:241` is the neighboring `r21-source-head` row, not the `r21-source-refs` row whose command is being corrected. This is a row-location/provenance trap, not evidence that the remote-only assertion is repaired.

## Evidence

- Frozen row at list revision `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`: `census/round-34/c1-items.tsv:33` records `G17a`, `SKILL.md:241`, expected exit 0, `SUMMARY total=1 pass=1 fail=0`, files `tests/fixtures/r21-source-refs.py,census/round-21/run-acceptance.py`, and the remote-only argv.
- W1 receipt `w1/deliver-c1-G17a.md:9-20` reports counter MISMATCH at base `9c76c7222a8abff027af42e37f0d160d52526bba` and tip `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`, with the same `SUMMARY total=1 pass=0 fail=1` / rc 1. Its manual comparison at `:39-44` records pass at `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`, failure at `98e5203d45b4e419a9e72801733d93303acc7ebd`, and failure at the later runner revisions. W1's attributed cause commit is the direct child of `7a6667cd` and its changed-file list contains neither frozen G17a file (`:48`).
- Frozen counter `census/round-34/c1-counter.py:23-27,254-267,283-300` defines the restatement schema and checks: value-drift (`run=same`) requires the cause to touch a frozen item file and original predicate True at parent/False at cause; argv correction requires the cause to have introduced the frozen `where` line, original argv to fail at cause, and corrected argv to name one of the frozen item's files. The row has no mutable files field.
- `git blame -L 241,242 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 -- SKILL.md` identifies line 241 as `r21-source-head` (introduced by `54eb2d0fb81e9cb5cf5b30430bcfa4b67ddc84ec`) and line 242 as `r21-source-refs` (introduced by `4eb2fda51c9917abd734c7e411f98cbb59c5c0fe`). This independently confirms W1's off-by-one/provenance observation.
- `preregistration.txt:48-53` sets the value-drift / argv-correction requirements; `:55-57` says a prior correction binding makes it AGREE. No prior G17a correction is evidenced in W1's base SCORECARD check (`w1/deliver-c1-G17a.md:22-31`).
- The defect mechanism and outputs above are reported from W1's committed receipts, not rerun by this seat. The only commands I ran were read-only source/revision inspection: `git show <list-rev>:SKILL.md` around lines 238-246, `git blame -L 241,242 <list-rev> -- SKILL.md`, `git log --follow` for both frozen files, and `git show --name-only` / `git rev-parse` for the attributed cause. No execution of the fixture or counter by this seat.

## Findings

1. **Confirmed from W1 evidence:** the defect is reproducible at base and tip; a load/measurement artifact is unlikely because W1 reports identical rc and summary at both revisions and a pass-to-fail transition across the direct parent/cause pair.
2. **Value-drift escape not available:** the actual failing cause `98e5203d...` does not touch either frozen G17a file. Under `c1-counter.py:285-291` it must be rejected as `BAD-ROW(cause touches none of the item files)`, regardless of the truthful corrected statement/exit.
3. **Potential mechanical false-green, not honest correction:** W1 reports an executed row using corrected `--keep-only` argv and cause `54eb2d0f...` that the counter accepted (`w1/deliver-c1-G17a.md:68-72`). This is mechanically consistent with the counter's argv-correction checks, but it binds a correction for the `r21-source-refs` argv to the commit that wrote the *different* `r21-source-head` row at line 241. The actual source-refs row is line 242, written by `4eb2fda...`. The preregistration requires the cause to have written the row being corrected; therefore this is not an honest route and does not cure the remote-only branch. It does expose that the counter checks only line text/position, not semantic identity of the row's command; this is a concrete provenance weakness in the mechanical validator, separate from W1's no-honest-route conclusion.
4. **No alternate value-drift cause established:** W1's receipts show the original passes immediately before `98e5203d...` and fails at that cause; the cause's file set excludes both frozen files. The later run-acceptance writer `a7c35c24...` has a failing parent per W1 (`:41-42`), so it cannot satisfy the required True/False transition. I found no evidence for another honest route.

## Attack log

- Read frozen row and W1 target receipt; inspected counter rules and preregistration clauses.
- Independently inspected line provenance with `git blame`; confirmed line 241 is `r21-source-head`, line 242 is `r21-source-refs`.
- Inspected `98e5203d...` parent (`7a6667cd...`) and changed paths; direct parent confirmed and changed paths do not include either item file.
- No bounded fixture/counter reproduction was run; reproduced outputs cited above are W1's committed evidence, not this seat's execution.

## Deliveries

- `.ufo/waves/round-34/w2/AttackG17a.md`
