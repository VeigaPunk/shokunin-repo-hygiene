STATUS: DONE — HEAD stamping served revision provenance for measured observations, not merely argument avoidance.

# Findings

The evidence favors this reading: the runners resolved HEAD to identify the code revision associated with a run, then stamped that identity on the record and its individual observations. The lessons and records treat each observation's revision as material provenance: retained results keep their original revision and are not relabelled as if rerun. That is stronger evidence of intent than the incidental fact that the runners exposed no `--rev` option. The source does not state the original design rationale verbatim, so the conclusion about why HEAD was selected is an inference from the execution flow and the later explicit preservation rules.

A durable-revision change stays faithful if it preserves that revision-to-observation binding:

- For a fresh run, resolve and record the exact revision whose tracked bytes the runner measured; record its full commit identity on the run and each newly executed result.
- Do not stamp a convenient newer revision onto retained results. Keep each retained result's own original revision and retention provenance; do not rewrite or backfill historical evidence.
- Admit a revision only when it is reachable from durable `refs/heads`, `refs/tags`, or `refs/remotes` (not `refs/jj`) and the tracked measurement paths match the selected revision's tree. If that proof fails, refuse with exit 2 before writing a record.
- Keep the baseline revision distinct from the measured revision, and preserve historical explicit 40-hex replay commands.

# Evidence

- Historical r13 runner source at commit `6f8ee0f`: it recognizes `--retry-failed` directly from `sys.argv` (no `--rev` parser), captures `git rev-parse HEAD`, sets the result stamp for newly executed checks, and writes both per-result and top-level `measured_commit` fields. The same code preserves a retained result's own revision instead of replacing it with the current one (`census/round-13/run-verification.py@6f8ee0f:31-37,48-54,71-82,127-133`).
- Round-13 lesson says actual commands, exit codes, findings, and measured revision are evidence; passing checks remain at their own measured commit, only failed checks are retried, and the final record names each result's actual revision (`corpus/lessons/round-13.md:23,128-130,144-148`). In the committed record, the top-level/fresh result revision is `6f8ee0f…`, while retained results still name `6ed10a7…` and their `retained_from` source (`census/round-13/verification.json:3-4,29-46,60-78`).
- Historical r14 `run-verification.py` captures HEAD once, passes it into each run result, and uses it for the top-level record; `run-targeted.py` likewise uses HEAD for newly executed checks while documenting that unchanged results remain only in the prior record without revision backfill (`census/round-14/run-verification.py@552cae4:28-48,50-57,79-91`; `census/round-14/run-targeted.py@552cae4:23-27,42-52`).
- Round-14 lesson names stale-green retention as the failure and says the consumer must preserve the original measured revision; after correction, unchanged passes were not rerun or relabelled, and the two committed records together are the complete measurement (`corpus/lessons/round-14.md:9,63-74`). The attempt record stamps `48f8945…`; the targeted record stamps `552cae4…` for its new checks (`census/round-14/verification-attempt-1.json:3-4,32-47`; `census/round-14/verification.json:3-6,31-47`).
- The round-19 preregistration states the durable-ref, measured-tree, refusal/no-record, and historical-40-hex requirements (`.ufo/waves/round-19/preregistration.txt:33-48`).

# Commands run

- Read the round-13/14 lessons, records, round-19 preregistration, and requested report destination.
- Read-only historical source inspection: `git show 6f8ee0f:census/round-13/run-verification.py | nl -ba`, `git show 552cae4:census/round-14/run-verification.py | nl -ba`, and `git show 552cae4:census/round-14/run-targeted.py | nl -ba` (from the lane root).
- No LSP device/server was exposed in the available tool inventory; inspected the committed source snapshots directly instead. No grep fallback was used.
- No tests, runner, live census, or other runtime were invoked; no tools were installed.

# Contract compliance

Only this scoped report was written. No lane implementation, tests, census, corpus, scorecard, log, or protected path was changed; no git/jj mutation, subagent dispatch, signal, scratch file, or installation was used.