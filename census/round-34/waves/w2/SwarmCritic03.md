## Status

G17a's stale remote-only result is supported by W1's executed evidence; I found no honest rule-conforming correction. The counter's mechanically accepted `--keep-only` argv correction is a provenance false-green: it cites the writer of adjacent SKILL.md:241 `r21-source-head`, whereas the G17a command is the `r21-source-refs` row at line 242.

## Evidence

Frozen row: `census/round-34/c1-items.tsv:33` at list revision `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`. W1 receipt `w1/deliver-c1-G17a.md:9-20,39-48,56-72` records base/tip mismatch, the pass-to-fail cause, the file-binding rejection, and the mechanically accepted but misattributed keep-only row. Counter rules: `census/round-34/c1-counter.py:23-27,254-300`; preregistration: `census/round-34/preregistration.txt:48-57`.

Read-only `git blame -L 241,242 <list-rev> -- SKILL.md` confirms line 241 is `r21-source-head`, authored by `54eb2d0fb81e9cb5cf5b30430bcfa4b67ddc84ec`; line 242 is `r21-source-refs`, authored by `4eb2fda51c9917abd734c7e411f98cbb59c5c0fe`. No fixture/counter execution was performed by this seat; W1 outputs are cited as W1 evidence, not my reproduction.

## Findings

The true value-drift cause `98e5203d45b4e419a9e72801733d93303acc7ebd` does not touch either frozen G17a file, so the required value-drift route is barred. The `--keep-only` route passes the counter mechanically but is not an honest correction of G17a: its purported cause wrote the neighboring source-head row, not the source-refs command. This is a counter provenance weakness, not a valid fix. No alternate honest route found.

## Attack log

Read frozen item, W1 report, counter, preregistration; independently inspected SKILL.md line provenance and the drift cause's parent/file list with read-only git queries. No execution performed.

## Deliveries

- `.ufo/waves/round-34/w2/AttackG17a.md`
- `.ufo/waves/round-34/w2/SwarmCritic03.md`
