## Status
STATUS: PASS — both jj 0.45.1 reference pages opened (HTTP 200 each); gc/op-abandon text quoted with locations; docs state no keep-ref expiry; host jj is 0.45.1 (with a build-hash suffix).

## Evidence
Commands run (scratch /fast/scratch/hyaku/souji-r30/SwarmScout08, 2026-10-26; nothing written in any repo):
- `curl -sS -L -o ... -w '%{http_code} %{size_download}' https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/cli/tests/cli-reference@.md.snap` -> `200 154561` (4038 lines; call it SNAP).
- `curl ... https://jj-vcs.github.io/jj/v0.45.1/cli-reference/` -> `200 390031` (HTML page exists; call it SITE).
- `jj --version` -> `jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5`.
- Keep-ref sweep, run over SNAP and over SITE (the bytes opened):
  `grep -n -i -E 'keep ref|keep-ref|refs/jj|jj/keep|keep/|expir|2 weeks|two weeks' <file>`
  SNAP hits: only line 3799 and 3801 (the `jj util gc --expire` option). SITE hits: only lines 11389-11390 (same text, HTML). Zero hits for `keep ref`, `keep-ref`, `refs/jj`, `jj/keep`, `keep/`.

## Findings
1. `jj util gc` full description (SNAP lines 3789-3805, heading `## jj util gc`). Full text, verbatim from the snap: "Run backend-dependent garbage collection." / "To garbage-collect old operations and the commits/objects referenced by them, run `jj op abandon ..<some old operation>` before `jj util gc`." Usage `jj util gc [OPTIONS]`. Only one option. Located quote (SNAP:3791): "Run backend-dependent garbage collection." Located quote (SNAP:3793): "run `jj op abandon ..<some old operation>` before `jj util gc`." SITE has the same heading at line 11382 (`id="jj-util-gc"`).
2. `--expire` option text (SNAP:3799-3803, heading `## jj util gc`, Options). Quoted whole: "`--expire <EXPIRE>` — Time threshold"; "By default, only obsolete objects and operations older than 2 weeks are pruned." (SNAP:3801); "Only the string "now" can be passed to this parameter. Support for arbitrary absolute and relative timestamps will come in a subsequent release." (SNAP:3803). SITE:11389-11390 carries the same first two sentences.
3. `jj op abandon` description (heading `## jj operation abandon`, SNAP:2411-2425; `op` is the alias; SITE:10267 `id="jj-operation-abandon"`). Description lines: SNAP:2413 "Abandon operation history"; SNAP:2415 "To discard old operation history, use `jj op abandon ..<operation ID>`. It will abandon the specified operation and all its ancestors. The descendants will be reparented onto the root operation."; SNAP:2417 "To discard recent operations, use `jj op restore <operation ID>` followed by `jj op abandon <operation ID>..@-`." Usage `jj operation abandon <OPERATION>`; argument (SNAP:2425): "The operation or operation range to abandon".
4. How `op abandon` treats the operations it removes (SNAP:2419): "Previous versions of a change (or predecessors) are also discarded if they become unreachable from the operation history. The abandoned operations, commits, and other unreachable objects can later be garbage collected by using `jj util gc` command." So per docs: abandon drops the operation records (descendants reparented onto the root operation, SNAP:2415); the objects become unreachable and are only reclaimed later by `jj util gc`.
5. Default expiry for keep refs: NOT stated. Sweep above (grep over SNAP 4038 lines and SITE) finds no mention of keep refs or `refs/jj` at all. The only expiry statement is the generic gc one: "older than 2 weeks" applies to "obsolete objects and operations" (SNAP:3801), not to Git `refs/jj/keep/*` refs. Any claim linking the 2-week default to keep refs would be inference `[INFERENCE]`, to be settled by the source at tag v0.45.1 and the measured fixture, not by these docs. This confirms the lesson-limit "The docs read do not state it".
6. Host version: `jj --version` prints `jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5` — version 0.45.1 plus a `-<git sha>` suffix (a build from commit 7c41cdeb…, not necessarily the v0.45.1 tag commit). Flag for the fixture: record the full string, not just "0.45.1". Whether commit 7c41cdeb equals the tag commit was not checked.
7. Note for C3 entry: SNAP is a generated snapshot of `--help` text from tag v0.45.1, so it is the same bytes as the CLI help of that version; SITE is the rendered page of the same.

## Deliveries
None beyond this report. Scratch dir /fast/scratch/hyaku/souji-r30/SwarmScout08 removed at the end (two downloaded pages, 540 KB; no repos created).
