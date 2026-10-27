## Status

**Confirmed at source/rule level; no new execution performed.** W1's value-drift blockage is valid under the frozen rules. No evidenced honest route or Q76 escape found; absence of a contrived SKILL-line rewrite cause is not independently proved.

## Evidence

- `census/round-34/c1-items.tsv:34` at frozen list revision `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`: G17b is `SKILL.md:235`, exit 0, COUNT of three scenario lines each matching `exit=0 matched=18/18`, item file only `census/round-21/run-acceptance.py`, replay-matrix argv.
- Base reading: `.ufo/waves/round-34/w1/deliver-c1-do-nothing-check.txt:23` and `.ufo/waves/round-34/w1/deliver-q76-honoring.txt:27` both record G17b MISMATCH, rc=1 vs expected 0; last digit-bearing line is the checkout advisory.
- W1 source/report evidence: `.ufo/waves/round-34/w1/deliver-c1-G17b.md:39-71` records parent `7a6667c...` passing and cause `98e5203d45b4e419a9e72801733d93303acc7ebd` / base failing 16/18; `:73-96` attributes loss to r20 fixture bwrap staging and says the cause touched neither runner nor the runner's item-file history. `:98-112` records rejection of the proposed row and the statement binding issue.
- Frozen requirements: `census/round-34/preregistration.txt:48-57,138-146`; executable rules: `census/round-34/c1-counter.py:267-300,301-313`.

## Findings

W1's `same`/value-drift route is invalid for the attributed cause: the frozen cause test requires a value-drift cause to touch an item file, while the only item file is `census/round-21/run-acceptance.py`; W1 attributes the behavior flip to fixture/tool changes outside it. The candidate was recorded as `BAD-ROW(cause touches none of the item files)` (`deliver-c1-G17b.md:102-106`). Its honest measurement statement `MATRIX scenarios=3 replayed=0 summaries_equal=True` also is not the run's last digit-bearing line under A1(c); the base receipt's last such line is the git advisory.

Corrected argv is not a demonstrated escape: it must name the row's own item script, and its executed ancestor cause must write the exact `SKILL.md:235` line where that line was absent in the cause's parent; additionally the original argv must fail at that cause. W1 did not establish such a source-line cause. I cannot prove from the runner-only history walk that no unusual qualifying SKILL-line edit exists. Q76 is not an alternative explanation: the cited Q76 audit found no prior correction binding this cell (`deliver-q76-honoring.txt:77-81`). The two committed do-nothing receipts agree; no fresh run was done, so there is no new reproduction.

## Attack log

Read the frozen preregistration, G17b TSV row, C1 validator, W1 G17b report, base do-nothing and Q76 receipts. Attempted `git log -S` / `-G` searches for SKILL row history returned no matching output and are not treated as proof. No fixture/counter run, clone, or lane mutation performed. See `AttackG17b.md` for fuller rule-by-rule analysis.

## Deliveries

- `.ufo/waves/round-34/w2/AttackG17b.md`
- `.ufo/waves/round-34/w2/SwarmReviewer04.md`
