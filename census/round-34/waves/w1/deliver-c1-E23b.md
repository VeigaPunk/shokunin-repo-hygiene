# C1 slice 10/12 — E23b (SCORECARD.md:304, C2 committed-bytes receipts, v2 arm)

STATUS: BLOCKED (MISMATCH, no valid restatement exists under the frozen contract) — ATTACK, see log.

## Counter reading (base, flock)
```
$ flock .../run.lock python3 -B census/round-34/c1-counter.py --root <lane> \
    --rev 9c76c7222a8abff027af42e37f0d160d52526bba --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 \
    --scratch /fast/scratch/hyaku/souji-r34/RestateC1s10/cnt --only E23b
ITEM	E23b	MISMATCH	original	rc=1 expect_exit=0 predicate holds last=SUMMARY manifests=8 failed=0 uncovered=1 lost=0 fidelity=0 floor_violations=0 tool_unchanged=0 rev=9c76c7222a8abff027af42e37f0d160d52526bba load=5.96
```
`/proc/loadavg` at the line's run: `5.96 …`; start of the serialized run `4.20 3.14 2.10`.
Item: exit 0, pred `lost=0 fidelity=0 floor_violations=0 tool_unchanged=0`,
files `census/round-29/c2-counter-v2.py`, at `{REV}`.
The *predicate* holds at the base; only the frozen exit (0) is stale — the counter's exit rule also
requires `uncovered=0`, and r33 carries `uncovered=1`.

## Prior-correction check (Q76)
No correction row binds the cell at the base (see deliver-c1-E23a.md, same grep): the r30 hits are
prose about `SCORECARD.md:314`, the r33 hit is the enumeration deliverable that sourced the item.

## Cause analysis — three routes executed, all closed by the frozen rule

Instrument history (the item's only file): `git log --follow census/round-29/c2-counter-v2.py`
→ exactly one commit, `8aaacf518d0dc9292d5258abf7d74bdaea1b76e7` (its creation).

Row-line history: line 304's current text was written by
`de874ee86fcaee212bbf4a9bfa4bf49d953ccb8b` and is absent from its parent (verified in E23a).

Executed readings (fresh clone per commit, origin removed, `PATH=/usr/bin:/bin`, fresh TMPDIR,
`GIT_CONFIG_NOSYSTEM=1`, cwd = clone root, flock; command in every case
`python3 -B census/round-29/c2-counter-v2.py --root . --rev <mark> --base-rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e`):

| mark | rc | last line | role |
|---|---|---|---|
| `8aaacf51` | 1 | `SUMMARY manifests=3 failed=152 uncovered=14 lost=0 fidelity=11 floor_violations=0 tool_unchanged=1` | the instrument's creation commit is red |
| `b8620071` (row's "measured at") | 0 | `SUMMARY manifests=3 failed=0 uncovered=0 lost=0 fidelity=0 floor_violations=0 tool_unchanged=0 rev=b8620071…` | green |
| `1dc67850` | 0 | `SUMMARY manifests=3 failed=0 uncovered=0 … tool_unchanged=0 rev=1dc67850…` | green (line-writer's parent) |
| `de874ee8` (line writer) | 0 | `SUMMARY manifests=4 failed=0 uncovered=0 … tool_unchanged=0 rev=de874ee8…` | **still green** |
| `d65a5c43` | 0 | `SUMMARY manifests=8 failed=0 uncovered=0 … rev=d65a5c43…` | green (drift onset's parent) |
| `af7fd250` | 1 | `SUMMARY manifests=8 failed=0 uncovered=1 … rev=af7fd250…` | first red: r33 salvage |
| `9c76c722` (base) | 1 | `SUMMARY manifests=8 failed=0 uncovered=1 … rev=9c76c722…` | red |

Route A — value drift at the true onset `af7fd250c8a862130f88b8f77ad29debf343e54d` (original holds
at `d65a5c43`, fails at `af7fd25`; that commit changes exactly one path,
`census/round-33/waves/w1-results.json`): **rejected** —
`BAD-ROW(cause touches none of the item files)`, because the frozen `files` cell names only
`census/round-29/c2-counter-v2.py`.
Route B — value drift at the only commit that touched that file, `8aaacf51`: **rejected** — the
original fails at the parent too (the script does not exist there; bash rc 2) →
`BAD-CAUSE(original at parent=False at cause=False; need True/False)`.
Route C — argv correction pinned to the row's own revision (`--rev b8620071…`) with cause
`de874ee8` (the only commit that wrote the row's line): **rejected** —
`BAD-CAUSE(the row's own argv held at the cause)`, because v2 was still green in the very commit
that authored the row (only v1 flipped there, when r29's own manifest landed).

## Reproducer for route C (frozen counter, scratch clone, throwaway identity)
Scratch clone of the lane at the list revision with this section appended
(`511323e305f598ace7439b8845c3c11889a0f57f`):
```
### Round 34 registry restatements

| E23b | SCORECARD.md:304 | restated | 0 | `python3 -B census/round-29/c2-counter-v2.py --root . --rev b86200714069022954a3b498cf697d894119b45e --base-rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e` | `SUMMARY manifests=3 failed=0 uncovered=0 lost=0 fidelity=0 floor_violations=0 tool_unchanged=0 rev=b86200714069022954a3b498cf697d894119b45e` | de874ee86fcaee212bbf4a9bfa4bf49d953ccb8b | same revision-scoped scope: the v2 literals hold at the row's measured commit |
```
```
ITEM	E23b	MISMATCH	restated	BAD-CAUSE(the row's own argv held at the cause)
```
Route A reproducer (`af7fd25`, `same` argv, statement = the base run's last line) →
`ITEM	E23b	MISMATCH	restated	BAD-ROW(cause touches none of the item files)`.
Route B reproducer (`8aaacf5`, `same` argv) →
`ITEM	E23b	MISMATCH	restated	BAD-CAUSE(original at parent=False at cause=False; need True/False)`.

## ATTACK (not a proposal to change a frozen predicate)
The frozen item set is unreachable for E23b: every honest cause is either the drift-onset commit
(`af7fd25`, no item file) or the instrument's creation commit (`8aaacf5`, red at both ends), and the
one commit whose row-line the rule accepts (`de874ee8`) is a commit where the item still held. The
corrected argv that makes the cell true (`--rev b8620071…`, rc 0, exact SUMMARY above) is therefore
undeliverable as a row. Consequence: `SUMMARY items=60 agree=60 mismatches=0` cannot be reached for
this item by any rule-conforming row; the honest correction exists but has no legal cause.

Decision belongs to the L1 (SoujiR34a2) — an amendment would have to *loosen* the cause-file binding,
which the round's stricter-only constraint forbids, so the honest outcomes are: (i) leave E23b
MISMATCH and record C1 as missed, or (ii) re-route the item as a named exclusion/defect with this
reproduction. I do not propose either.

## Proposed row
None landed from this seat. The two drafts above are reproductions of the rejection, not deliveries.
