## Status

**Confirmed at source/rule level; no new execution performed.** The W1 blockage for an honest value-drift restatement is valid under the frozen rules and is not explained by Q76 or by the base measurement. W1's separate last-digit-line concern is also consistent with A1(c). I found no evidenced honest correction route. A contrived future/ancestral edit that reintroduced the exact SKILL row could theoretically meet the argv-correction cause shape, but no such qualifying cause is established in the cited W1 history; it is not a demonstrated escape.

## Evidence

- Frozen list: `census/round-34/c1-items.tsv:34` at list revision `2b0171e2071fdc9c16a69bed12b0d040e574d8c8` specifies `SKILL.md:235`, expected exit `0`, `COUNT:^SCENARIO\t[^\t]+\texit=0\tmatched=18/18\t.*$==3`, item files only `census/round-21/run-acceptance.py`, and the replay-matrix argv.
- Frozen base do-nothing receipt: `.ufo/waves/round-34/w1/deliver-c1-do-nothing-check.txt:23` reports `G17b MISMATCH original rc=1 expect_exit=0`, with `last=Note: switching to '9c76c7222a8abff027af42e37f0d160d52526bba'.` The same result appears in the independent Q76 receipt `.ufo/waves/round-34/w1/deliver-q76-honoring.txt:27`.
- W1 target report: `.ufo/waves/round-34/w1/deliver-c1-G17b.md:39-71` records parent `7a6667c...` passing 18/18 for all three scenarios, cause `98e5203...` and base failing 16/18, and identifies the failure mechanism as the bwrap `/var/tmp` rebind affecting the two r20 payload fixtures. Lines 85-96 report the runner history bounds. Lines 98-106 give the candidate row and its recorded rejection: `BAD-ROW(cause touches none of the item files)`.
- Frozen rules: `census/round-34/preregistration.txt:48-57` requires an executed cause, with value-drift parent-holds/cause-fails and cause touching an item file; argv-correction requires the cause to write the registry row and the row's own argv to fail at that cause. Q76 says an already-binding prior correction makes the item AGREE. `census/round-34/preregistration.txt:138-146` records A1's frozen corrected-argv and last-digit-line constraints.
- The actual validator is consistent: `census/round-34/c1-counter.py:273-300` requires the cause to be an ancestor of list revision; for `same`, it rejects causes touching none of the item files and tests parent/cause behavior. For corrected argv, it requires an item-file basename in the argv (`:267-268`), the row's exact source line absent at parent and present at cause (`:293-298`), and the row's own argv failing at cause (`:299-300`). At `:301` onward it evaluates the corrected argv; `:304-313` binds the statement to the collapsed last digit-bearing output line. The W1 measured output's last digit-bearing line is the git checkout advisory, not its `MATRIX` summary (`deliver-c1-G17b.md:108-112`).
- The Q76 receipt reports no prior correction binding the same cell (`.ufo/waves/round-34/w1/deliver-q76-honoring.txt:77-81`); therefore the do-nothing mismatch is not established as a Q76 artifact.

## Findings

1. **The central W1 defect is real under the frozen cause rule.** The observed value drift is attributed to `98e5203d45b4e419a9e72801733d93303acc7ebd`, but the only frozen item file is `census/round-21/run-acceptance.py`; W1 says the cause instead changes the two r20 fixtures and tools, not that runner (`deliver-c1-G17b.md:73-83, 93-96`). Thus the valid `same` correction is rejected by the frozen touched-file gate. The executable evidence for its 16/18 behavior is recorded in W1, not rerun by this reviewer.
2. **The obvious alternative, corrected argv, does not rescue the submitted row.** It must still run the row's own script (an argv naming an item-file basename), have an executed ancestor cause write `SKILL.md:235`, and show the original row argv already fails at that cause. The W1 row instead uses `same` and the value-drift cause; the recorded correction is therefore invalid even if its explanation accurately describes the defect.
3. **No demonstrated alternate cause or Q76 escape found.** A theoretical cause that newly writes the exact source line could satisfy the corrected-argv branch, but the line must be absent in that cause's parent and present in the cause, and the frozen replay-matrix argv must fail there. The supplied W1 history walk is for the runner file (`:85-96`), not a complete proof about all historical SKILL-line edits. Consequently I do not elevate absence of such an unusual cause to an independently executed fact. Q76's same-cell check and frozen receipt provide no relief.
4. **Measurement artifact is not supported by the receipts.** Two committed W1 readings show the same base mismatch and the reported cause/baseline matrix outcomes; load varies, but the decisive mismatch is exit/predicate failure and the recorded matrix counts, not load. This is based on committed receipts, not fresh execution.

## Attack log

- Read `census/round-34/preregistration.txt`, frozen row `census/round-34/c1-items.tsv:34`, `census/round-34/c1-counter.py:243-321`, W1 G17b report, base do-nothing receipt, and Q76 receipt.
- No counter, replay fixture, or clone was run. No files outside the two assigned report paths were written.
- Source/revision inspection commands for candidate SKILL history were attempted with `git log -S` / `git log -G` against `SKILL.md`; they returned no matching output, so they do not establish historical absence. The reported execution outputs below are copied from committed W1 evidence and are not claimed as my reproduction.
- Exact recorded candidate-row evaluation: W1 report `deliver-c1-G17b.md:102-106` records `ITEM G17b MISMATCH restated BAD-ROW(cause touches none of the item files)`.

## Deliveries

- `.ufo/waves/round-34/w2/AttackG17b.md` — scoped adversarial assessment.
- `.ufo/waves/round-34/w2/SwarmReviewer04.md` — same scoped finding for the seat-level delivery.
