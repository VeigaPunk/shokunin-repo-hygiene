STATUS: PARTIAL — C2 is falsifiable in principle, but its before/after measurement is not yet an independent, reproducible oracle: the scenario driver, compared result projection, and source/output boundary are not pinned sufficiently to determine one outcome from the frozen text.

# C2 preregistration review

## Findings by severity

### High — The replay measure does not freeze a runnable scenario protocol

C2:19 gives scenario descriptions and expected outcomes, but no exact driver command, invocation argv, source construction commands, or unambiguous `--rev` value for each phase. In particular, “After: r21 runner at the r21 measured rev” does not say whether the runner is launched from the measured checkout or another checkout, or identify the exact measured commit. “Before: … runner at rev 5ff…” could mean the runner's source revision, the `--rev` argument, or both. The three `SRC` descriptions are not a construction recipe.

The S3 condition is not deterministic: “HEAD may differ from rev” allows equality. The routed defect is specifically the old runner's HEAD-equality restriction (C2:16); if S3's HEAD equals the before `--rev`, S3 no longer exercises that restriction and the stated before result need not be 0/3. The inspected r20 runner also gates on exact lane root and HEAD equality (`census/round-20/run-acceptance.py:506-519`), so S1/S2 can refuse due to the path gate rather than the behavior C2 purports to measure. That can be a valid baseline failure, but the oracle must not treat it as evidence about HEAD behavior.

**Counterexample:** S3 is the lane root with HEAD=`5ff75657427c4793fbf1f124d794f1c99359d74e`, and before `--rev` is that same commit. This satisfies “HEAD may differ” and can pass the old HEAD check if its measured tree is clean. It contradicts the preregistered expected refusal in all three scenarios. A second counterexample is an S1 source cloned from a revision that does not contain the after measured commit: the after runner cannot check it out, although the scenario description does not require the constructed source to contain that commit.

**Exact wording fix:** “The measure is run by `census/round-21/measure-acceptance-replay.py` with a recorded full `--before-rev 5ff75657427c4793fbf1f124d794f1c99359d74e` and the exact full `--after-rev <integration commit>`; both must be commits available from the refs of each phase's `SRC`. The harness creates and records S1, S2, and S3 with fixed commands, invokes the runner from the corresponding measured checkout, and supplies that phase's `--rev` explicitly. Before each invocation, assert and record `git rev-parse HEAD != --rev` for every scenario; if any equality holds, reconstruct the source so the assertion holds rather than counting that run. Use a fresh output path outside every source and clone. The harness records each argv, source HEAD, source kind, and exit code.” Pin the S1 clone origin/revision and S2 mirror command in the harness contract, not merely “fresh clone”/“bare mirror.”

### High — Output safety does not fully enforce “never writes into SRC”

C2:17 refuses an existing output and an output “inside the temp clone or a measured input directory,” then says the runner never writes into `SRC`. Those are not equivalent unless “measured input directory” is explicitly the whole source repository. The output argument's relative-path base and symlink handling are also unspecified.

**Counterexample:** with `SRC=/tmp/mirror.git` (a bare repository), `--output=acceptance.json` is new and is neither inside the temp checkout nor necessarily inside a named measured input directory. An implementation that anchors a relative output under `SRC` writes into the mirror, violating the no-write guarantee. Likewise, a new output under `SRC/.git/` can evade a guard that checks only the measured working-tree inputs.

**Exact wording fix:** “`--output` MUST be an absolute, absent file path whose resolved parent already exists and is not a symlink. Resolve source, clone, and output-parent paths canonically; refuse if the output equals or is beneath either `realpath(SRC)` or `realpath(temp_clone)`, or is beneath any separately named measured-input directory. The runner MUST NOT create parent directories or write any result, temporary file, or metadata under `SRC`.” If relative outputs are desired instead, name their single fixed base and still reject all paths under `SRC`.

The no-write assertion is itself not reproducible as written: “SRC digest/status before == after” does not define the digest or what “status” includes. A `git status` comparison misses ignored/untracked files and `.git` metadata. **Counterexample:** a runner writes `SRC/.cache/replay.log` where `.cache/` is ignored; ordinary git status is unchanged. **Exact wording fix:** “Compare a deterministic pre/post inventory of every entry under SRC, including hidden, ignored and untracked entries and VCS metadata, using relative path, entry type, mode, symlink target, and regular-file content digest; omit atime only. Any difference falsifies the run.” State explicitly that this is the persistence check, in addition to the output-path prohibition.

### High — “Same 18 commands” and “identical per-step summaries” lack a comparison oracle

The contract requires “the same fixed 18-command inventory as r20” (C2:17), but does not pin which r20 inventory revision or how exact inventory identity is verified. “Identical per-step summaries” (C2:19) does not define the compared fields or path normalization. Thus two independent implementations can disagree while both report 18/18.

This is observable in the inspected r20 implementation: `make_steps` constructs argv values with the checkout root (`census/round-20/run-acceptance.py:272-331`), and `summarize_result` stores `argv`, `command`, raw stdout/stderr, and their hashes (`:351-369`). Across S1/S2/S3, whole per-step records naturally contain different temp-root paths and can produce different raw output hashes. Conversely, comparing only a `SUMMARY` line could ignore differences in the command, output, or auxiliary checks. Replacing a step while retaining 18 passing steps could also satisfy the count if the changed inventory's expectations are changed with it.

**Counterexample:** S1 uses clone path `/tmp/a/lane`, S2 `/tmp/b/lane`; the step argv and `command` include those different paths. One oracle compares full JSON and reports mismatch, while another compares only `observed_summary` and reports equality. Another implementation swaps one step for a trivial passing command and adjusts its local expected summary; it can still produce `all_matched=18/18` without exercising the r20 inventory.

**Exact wording fix:** “The required inventory is the exact ordered list of `(name, argv with the checkout root replaced by <ROOT>, kind, expected_summary, pass_pattern, pass_count, record_checks)` produced by `census/round-20/run-acceptance.py` at `5ff75657427c4793fbf1f124d794f1c99359d74e`; the after runner MUST match that list exactly. Define a comparable per-step summary as `(name, returncode, matched, observed_summary, observed_auxiliary_lines, matched_counts)`, replacing each run's source and temp-clone paths with fixed `<SRC>` and `<CLONE>` tokens before comparison. Compare all 18 summaries in order, and separately require `all_matched` true.” Preserve raw records separately; do not leave “summary” to interpretation.

### Medium — The literal-lane-path refusal has two plausible scopes

“Executed step programs contain the literal absolute lane path” (C2:17) does not specify whether “programs” means command argv, directly invoked script bytes, imported code, or all files read at runtime. Literal matching also does not specify whether comments count or whether normalized spellings count.

**Counterexample:** a step is `python3 tools/check.py`; `tools/check.py` contains `ROOT = "/home/vgpnk/Projects/shokunin/souji-shokunin"` but the argv does not. An argv-only checker accepts while a source-byte checker refuses. Conversely, a comment containing that literal is rejected by a byte scan even if unused.

**Exact wording fix:** “For each of the 18 steps, reject if the exact byte sequence `/home/vgpnk/Projects/shokunin/souji-shokunin` occurs in any argv element or in the raw bytes of the directly invoked in-repository script named by that step. This is a literal check only: comments count; path aliases, computed strings, and transitive imports are outside this check.” If the intent includes imported code, name and define the complete file set instead; do not leave “executed step programs” as the boundary.

### Medium — “No output” and refusal failure semantics are ambiguous

C2:17 says certain refusals are “exit 2, no output” without saying whether that means no result file or zero bytes on both streams. This distinction is observable: the inspected r20 runner returns 2 while printing refusal diagnostics to stderr (`census/round-20/run-acceptance.py:522-524, 587-589`). It also leaves unspecified the outcome for other preflight failures such as SRC not being a repository, missing/unfetchable rev, failed detached checkout, or dirty clone status.

**Counterexample:** an invalid rev returns 2 and emits `refused: rev not found` on stderr, but creates no result file. One oracle treats this as “no output”; another rejects it.

**Exact wording fix:** “For every preflight refusal, exit 2, leave the requested output absent, and write zero bytes to stdout and stderr. Any SRC validation, clone, checkout, HEAD, clean-status, or policy-check failure is a preflight refusal. A completed run with one or more mismatches writes the record and exits 1; a complete all-matched run writes the record and exits 0.” If diagnostics are wanted, explicitly allow stderr and define “no output” to mean “no result file.”

### Medium — “Full40/non-durable” should bind to the existing revision rule

C2:17 says `FULL40` and “short/non-durable revs” but does not explicitly define durability. The existing `tools/souji-rev-pin.py` defines lowercase `[0-9a-f]{40}`, commit-only resolution, and reachability from `refs/heads`, `refs/tags`, or `refs/remotes`, excluding `refs/jj` (`:36-37,79-94,184-224`). Unless C2 binds to that rule, an implementer could accept a revision held only by `refs/jj/keep`, while an oracle applying the existing helper rejects it.

**Counterexample:** the requested commit is reachable only from `refs/jj/keep/x`, not a head/tag/remote. It is a full 40-hex commit object but is not durable under the existing helper.

**Exact wording fix:** “Validate `--rev` with `souji-rev-pin.py`'s `resolve_durable` semantics: lowercase 40-hex commit ID, reachable from `refs/heads`, `refs/tags`, or `refs/remotes`; `refs/jj` alone is not durable. Reject before creating the result file.”

## Harm guard assessment

The 18-command runner includes the r18/r16 fixtures with expected pass counts 11 and 15 (`census/round-20/run-acceptance.py:303-307`), so those fixture behaviors are guarded if (and only if) the new runner preserves the exact frozen inventory and expectations. The inspected fixture files already derive their lane root from `__file__` (`tests/fixtures/r18-landing-pointers.py:30-31`; `tests/fixtures/r16-landing-gate.py:64-65`). The missing independent guard is exact inventory identity; `all_matched=18/18` alone does not establish that the same cases ran. Pin the ordered inventory as above.

The before/after measure can fail in principle: refusals, mismatches, non-identical normalized summaries, or source mutations are falsifiers. It is not yet sound as a repeatable count because S3's inequality condition, source construction, comparison projection, and complete SRC/output boundary are underspecified.

## Verification gaps and evidence

- Static review only; no runner, tests, build, lint, formatter, or other target code was executed (read-only seat requirement).
- LSP is unavailable in the mounted tools: `read xd://lsp` returned “No such tool: xd://lsp”; no semantic references/definition/diagnostics were available, and no grep was used as semantic proof.
- Read-only command executed: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 5ff75657427c4793fbf1f124d794f1c99359d74e:census/round-20/run-acceptance.py | sha256sum` (exit 0) and the corresponding `show 544c8358039a07e8b45e6db72312da5c8d965275:... | sha256sum` (exit 0); both emitted `6d38a3d0590e9c44480ae19e3abaa8669d7399737397297fd1e0fde363699a10  -`. The before runner's bytes therefore match the inspected runner whose gates are cited above.
- No tools were installed or updated.

Report: .ufo/waves/round-21/w1/RevPreregC2.md