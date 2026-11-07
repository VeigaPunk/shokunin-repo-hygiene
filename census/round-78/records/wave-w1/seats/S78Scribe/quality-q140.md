# S78Scribe — draft QUALITY criterion Q140

Placement note: Q138/Q139 sit in `corpus/QUALITY.md` § `## Round 66 criteria` (5 columns:
`id | criterion | applies to | check | motivating evidence`). Q140 continues that table; the L1 owns the
placement and the section.

Verified before drafting: the gate blob at `87d45617…` and at `319109b0…` both hash to
`b746bd9da677aefe67116a192626151685a8b9f23e7bfee96987e04e645b4eef`; the counter over the frozen population
reads `SUMMARY rows=17 mismatches=12 errors=0 hangs=12` at the lane base and `rows=17 mismatches=0 errors=0
hangs=0` with the candidate (`census/round-78/records/c1-after.txt`); the three mutant controls read
mismatches=14, 10 and 11 with EXIT=1.

Row to append:

| Q140 | A lane gate that runs git in a repository it does not own checks git's discovery sources before its first git call — every source that exists must be a regular file (a symlink counts by its target), include targets are followed, and a refusal fails closed with a class and a count and skips the git-dependent checks — and it time-bounds the remote calls whose repository config it cannot pre-check (S323, S324, S062). The population carries positive controls so that refusing everything is not mistaken for a gain: a regular include, a missing include and a non-regular path git never reads at discovery all pass. Limits it states: SIGTERM to the gate, a git built with another system-config path, include conditions not evaluated, and a source swapped after the pre-check. | the lane's own pre-report gate (`tools/souji-pre-report-gate.sh`, `gitsrc_scan()` before check 1, and check 1's `timeout`) | frozen counter `census/round-78/c1-gitsrc-counter.py` (17 routes: 11 FIFO discovery sources, 1 origin-side FIFO, 5 positive controls; 75 s row bound, process-group kill): lane-base gate mismatches=12 hangs=12 (`controls/c1-K-a-do-nothing.txt`), candidate 0/0 (`records/c1-after.txt`); mutants refuse-any-include 14, config-only 10, timeout-only 11 (K-b, K-c, K-d); regression r77 16/16, r76 30/30, r36 21/21, r27 4/4 | `census/round-78/records/c1-after.txt`, `census/round-78/controls/c1-K-a-do-nothing.txt`, `corpus/knowledge/git-discovery-sources.md`, `corpus/lessons/round-78.md` Gate |
