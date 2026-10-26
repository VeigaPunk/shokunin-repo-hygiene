# SwarmScout08 — S220 quote re-open (round 30 wave 2)

## Status
STATUS: PASS — S220 re-fetched live from tag v0.45.1, sha256 equals the SHA256SUMS line, every quote attributed to S220 found verbatim at the stated line(s), each <=25 words, no pipe.

## Evidence
- Fetched `https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/cli/tests/cli-reference@.md.snap` (curl, own run): sha256 `b330694348c2a6fb21b637425c711d48ac9fa41d0b3596b4ca2955f7a9333554` == `census/round-30/sources/SHA256SUMS:1` (`cli-reference@.md.snap`). `cmp` against the committed snapshot census/round-30/sources/cli-reference@.md.snap: identical. 4038 lines (matches SOURCES.md S220 anchor "4038 lines").
- `git ls-remote` tag v0.45.1 -> `7c41cdeb16b6b321c64e789a966b6adf723816a5` (matches the row's `7c41cdeb`).
- Section headings found: `## \`jj operation abandon\`` line 2411; `## \`jj util gc\`` line 3789 (next section 3807).
- Matching: whitespace-normalized substring search per line; word counts by whitespace split. Python used was `python3 -B` over my scratch copy only.

## Findings
Per quote (words / found line):
Gate (jj-keep-ref-expiry.md:109-111):
1. FOUND line 2419 — "Previous versions of a change (or predecessors) are also discarded if they become unreachable from the operation history." (18w; stated 2419)
2. FOUND line 2419 — "The abandoned operations, commits, and other unreachable objects can later be garbage collected by using `jj util gc` command." (19w; stated 2419)
3. FOUND line 3793 — "To garbage-collect old operations and the commits/objects referenced by them, run `jj op abandon ..<some old operation>` before `jj util gc`." (21w; stated 3793)
4. FOUND line 3801 — "By default, only obsolete objects and operations older than 2 weeks are pruned." (13w; stated range 3801-3805, in range)
5. FOUND line 3803 — "can be passed to this parameter." (6w; in 3801-3805) — a sentence fragment of "Only the string "now" can be passed to this parameter."
6. FOUND line 3803 — "Support for arbitrary absolute and relative timestamps will come in a subsequent release." (13w; in 3801-3805)
Header line 1 / claim step 3 / step 4 ranges:
7. FOUND — header `lines 2419`, `3793`: text at 2419 and 3793 as above. `3799-3805` / step 3 `[S220, jj util gc lines 3799-3805]`: `* --expire <EXPIRE>` option at 3799, default-2-weeks at 3801, "now"-only at 3803; the paraphrase "default prunes only obsolete objects and operations older than two weeks" and "single literal now" are supported at 3801/3803. Step 4 `[S220, line 2419]`: both clauses at 2419.
SOURCES.md S220 row (corpus/SOURCES.md:165):
8. teaches cell: quoted tokens `"now"` FOUND at 3803 (`Only the string "now" can be passed to this parameter.`); default 2 weeks = 3801; "discards the named operation with all its ancestors and reparents the descendants" supported at line 2415 (`It will abandon the specified operation and all its ancestors. The descendants will be reparented onto the root operation.`) — inside the anchor's :2411-2421 window. The cell is paraphrase, not a verbatim quote.
9. anchor cell: `:2411-2421 § jj operation abandon` (heading 2411, Usage at 2421) and `:3789-3803 § jj util gc` (heading 3789, last text 3803) correct; `4038 lines` correct; `7c41cdeb` correct; "no `jj file delete`, no `jj util diff`" — neither string occurs in the file (grep empty).
Defects (not fatal):
10. DEFECT-NOT-FATAL — Gate line 111 `lines 3801-3805` and claim step 3 / header `3799-3805`: line 3805 is a blank line (text ends at 3803); range overstates by 2 blank lines. Quotes themselves are located in-range. Cosmetic.
11. DEFECT-NOT-FATAL — Gate quote 5 is a 6-word fragment ("can be passed to this parameter.") that without its sentence head carries no meaning; verbatim, but weak evidence on its own.

## Attack log
- sha256 binding of S220 to SHA256SUMS: HOLDS.
- Committed snapshot == live bytes: HOLDS.
- Each Gate quote verbatim/line/<=25 words/no pipe (6 quotes): HOLDS.
- Header + claim-step line citations (2419, 3793, 3799-3805): HOLDS (range loose by blank lines, finding 10).
- SOURCES.md S220 teaches/anchor cells: HOLDS (teaches is paraphrase; tokens and line windows check out).
- Tag/commit pin 7c41cdeb: HOLDS.
- Not attacked: S054/S063/S221 quotes; the fixture; the counters; "served page /v0.45.1/ carries no 0.46-only subcommand" beyond grep of the raw snap (docs.jj-vcs.dev reachable, HTTP/2 200, body not checked).

## Deliveries
None beyond this report. Scratch /fast/scratch/hyaku/souji-r30/SwarmScout08 removed. No tool installs.
