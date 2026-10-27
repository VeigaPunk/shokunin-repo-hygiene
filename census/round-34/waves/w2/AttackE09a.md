## Status

Finding is real as an observed base mismatch; no honest correction route is identified under the frozen rules. This conclusion is based on the committed base record and source-level rule analysis; no fresh fixture/counter execution was performed.

## Evidence

- Frozen list row `census/round-34/c1-items.tsv:50` (list revision `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`): E09a binds `SCORECARD.md:33`, exit 128, predicate `path .* does not exist`, file `tools/souji-pre-report-gate.sh`, pin `{REV}`, argv `bash -c "git cat-file -e e78ac7c4837b81b634db4a927605a751a7f006ba:tools/souji-pre-report-gate.sh"`.
- Base do-nothing receipt `census/round-34/records/controls-c1-do-nothing.txt:34` records `ITEM E09a MISMATCH original rc=128 expect_exit=128`; actual final diagnostic says the path exists on disk but not in the specified commit, so it does not satisfy the frozen `path .* does not exist` predicate.
- W1 `deliver-c1-mismatch-classification.md:52` identifies this literal diagnostic-vs-predicate mismatch; its Q76 scan at lines 28-31 says only E05 had a same-cell correction binding, not E09a. `SCORECARD.md:33` is the historic row documenting the tool's later presence at `6cb22dc20c9fdb3c7a49eaa1accabca339054c17`.
- Preregistration `census/round-34/preregistration.txt:48-57` requires an appended restatement with the original line/exit, same or corrected argv running the row's own script, exact digit-bearing output, ancestor cause, and reason; cause must be executed as value drift or argv correction. Its amendment A1 is in the same file lines 138-146.
- Counter source `census/round-34/c1-counter.py:243-321`: corrected argv must mention one of the item files (267-268); same-argv correction needs cause touching an item file and original predicate true at parent/false at cause (284-291); argv correction requires cause to newly write the bound row (293-300); final restated statement must equal collapsed last digit-bearing line (306-313).

## Findings

W1's blockage reasoning survives this adversarial review. The frozen run is a `git cat-file -e` existence check at the fixed historic commit. The repository history establishes the intended state transition (tool absent at E09a's historical measured commit, later present at the Round 27 measured commit), but that does not make the existing predicate match Git's actual fatal wording. No source evidence shows an alternate legitimate route:

- `same` preserves the frozen argv and predicate; the base failure is the predicate text, not a transient error. A cause producing a value drift in this check would have to touch a listed item file, and the historical SCORECARD claim cannot make the tool-object check yield text `path ... does not exist` at its asserted commit. W1's broader report states none of the other 24 mismatches has an E09a binding row.
- Corrected argv must still name the row's own file and would be checked against the unchanged frozen predicate. A different invocation could conceivably emit the expected wording, but preregistration also requires an executed cause that wrote the row text and the row's original argv to fail at that cause. The row's text is a historical observation in SCORECARD, not an E09a-specific newly authored restatement; absent such a cause, choosing a command merely to manufacture matching text would not qualify as an honest correction.
- Q76 only rescues a prior correction row binding this exact item; the W1 check found none. Neighboring correction rows do not bind E09a.

Thus classify as a genuine frozen measurement/predicate mismatch, not a load artifact or unreachable-by-other-clause escape. Whether the cause history could support any unforeseen row-writing correction is a source-level inference; it was not exhaustively executed here.

## Attack log

1. Read frozen E09a row, base control receipt, preregistration rules, W1 mismatch classification, and C1 counter's `judge` implementation.
2. Compared recorded exit/predicate/diagnostic and checked the permitted restatement branches, file-name constraint, cause attribution conditions, statement binding, and Q76 condition.
3. No fresh commands against a fixture, clone, or counter were run. No execution claims beyond the committed receipts above.

## Deliveries

- `.ufo/waves/round-34/w2/AttackE09a.md`
- W1 frozen list revision: `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`; base: `9c76c7222a8abff027af42e37f0d160d52526bba`.
