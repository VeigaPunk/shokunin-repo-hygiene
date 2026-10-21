# SimpRunnerDup — source-only C2 review

## Axes and disposition

Axes: operability across arbitrary local repositories; immutable historical provenance; unchanged acceptance strength; implementation weight. Judged axis: operability.

No code deletions or production edits made. Recommend copying the r20 runner into the new r21 runner and changing its repository acquisition boundary, not rewriting its acceptance engine or factoring historical r20 into a shared module. Historical runner and result bytes remain immutable. This is author-side advisory, not execution evidence or closure.

## What stays verbatim

From `census/round-20/run-acceptance.py` at `544c8358039a07e8b45e6db72312da5c8d965275`:

- `BASELINE`, `EXPECTED_COMMANDS = 18`, all five `COUNTER_EXPECTATIONS`, and the exact `make_steps` inventory, names, order, arguments relative to the measured root, expected summaries, pass patterns/counts, and cache-demo expectations. `make_steps` already takes a root: pass the private clone, not SRC. Do not add r21/C3 commands to this fixed acceptance inventory.
- `R13_MEASURED`, `R14_MEASURED`, the existing measured input paths, and `INPUT_DIRS`. Add the new r21 runner to `INPUT_PATHS`; retaining the r20 runner entry preserves the old measured boundary and historical bytes. Do not globally replace round-20 paths with round-21 paths.
- `Refusal`, hashing/decoding/regular-file checks, baseline extraction and its byte hashes, external baseline binding, failure recognition, numeric-leaf handling, and `summarize_result`. These enforce exact summaries, auxiliary inventory lines, reported baseline-mismatch counts, historical JSON records, cache checks, and unexpected failure rejection. They are not duplicate policy authorities.
- Per-step initial/before/after/final snapshots, drift refusals, fixed inventory guards, subprocess byte capture, exclusive output writing, and exit distinction (0 matched; 1 completed mismatches; 2 refusal). Keep raw stdout/stderr, hashes and before/after evidence. Removing these would reduce acceptance strength.
- The restricted child environment for acceptance steps. Extend the acquisition operations with explicit Git hook/config suppression; do not assume this environment alone disables repository hooks.

The same engine is intentionally duplicated into the new historical generation. Moving it out of r20, importing mutable r20 policy as a replacement for the copy, rewriting prior records, or weakening an expected summary is not a simplification compatible with this claim.

## Minimal diff shape in the new r21 file only

1. Update the new file's descriptive round label, private temporary-directory prefix, module-loading label and output schema identity to r21. Leave historical identifiers/expected data untouched. Bind `combined_snapshot` runtime bytes against `root / 'census/round-21/run-acceptance.py'`, and add that path to the measured set. The existing self-byte check cannot remain pointed at r20.
2. Delete the runner's `LANE = Path(...)` authority and `root != LANE.resolve()` refusal. Keep the literal lane path only as the required forbidden-byte sentinel for executed step programs; it must not select SRC, resolve runtime root, or authorize a repository. Do not scan every measured historical record for this sentinel: historical data can legitimately contain it.
3. Replace source-root execution with two explicit roles: resolved `source_root` for clone acquisition, and `root` for the detached private worktree. Create the latter with the frozen `git clone --quiet --no-local --no-checkout` contract and hooks disabled, detach-check out the full revision, then verify private clone HEAD and clean status. Execute and snapshot exclusively there. Do not check out, configure, repair, update refs in, or run acceptance programs from SRC. A bare mirror has no source worktree from which to load helper files.
4. Remove the SOURCE HEAD probe and its equality refusal, not all HEAD verification. The existing `head_text != args.rev` condition belongs to the private clone after checkout. Any recorded `head_equals_revision` assertion must clearly refer to that clone. No source-HEAD prerequisite survives.
5. Keep full-ID/durable-ref validation and exact measured-tree validation, but apply tree comparisons to the checked-out clone. `resolve_durable(..., tree_check=True)` on SRC before cloning would still reject a different source worktree and cannot work for a bare mirror. The helper's `tree_check=False` is the existing revision-only mode; do not invent a weaker revision checker. A detached checkout alone is not a durable ref under that helper's rules: retain clone refs and validate reachability from its allowed namespaces.
6. Refuse literal lane-path bytes in the executed step programs before executing them. Preregistration separately requires changing only root discovery in `tests/fixtures/r16-landing-gate.py` and `tests/fixtures/r18-landing-pointers.py` to their own file location; preserve their replay IDs, assertions and case counts. Those fixture roots have actual replay callers and cannot simply be deleted.
7. Adapt `output_path` rather than delete it: resolve the destination independently of disposable clone lifetime; preserve exclusive/non-symlink safeguards and measured-directory overlap refusal; add refusal for any output in the private clone. Normalize containment robustly so `..` or parent symlinks cannot bypass it. Never create output on a refused invocation. Keep publication outside SRC as required by the no-write-to-SRC contract, including when the requested output is an otherwise unmeasured path there.
8. Retain baseline extraction inside the private temporary area, acceptance execution and output capture there, then write the validated new external result. Update root provenance so consumers can distinguish source location from measured clone location without interpreting a clone HEAD assertion as a source HEAD requirement.

Bounded counterexample: merely deleting `LANE` and the SOURCE HEAD equality block while preserving `load_pin_helper(SRC)` plus `resolve_durable(SRC, ..., tree_check=True)` still fails C2. A bare mirror lacks `tools/souji-rev-pin.py` as a worktree file; a clone at another revision can fail the input snapshot before any step. Therefore clone-first root separation is the smallest correct boundary change, not just two deletions.

## Evidence and limits

Read the frozen preregistration first; C2 lines 15–19 are the oracle. Read the godspeed skill. Executed these source-inspection commands only, each returned exit 0:

- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 544c8358039a07e8b45e6db72312da5c8d965275:census/round-20/run-acceptance.py`
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 544c8358039a07e8b45e6db72312da5c8d965275:tools/souji-rev-pin.py`

The committed helper shows `resolve_durable` enforcing full 40-hex IDs, durable namespace reachability and optional working-tree snapshots. The committed runner shows the live lane-equality guard, source HEAD guard, exact 18-step construction and self-byte check against the r20 file.

Requested `read xd://lsp`; tool discovery answered `No such tool: xd://lsp`. No semantic-reference server/device was available, so no semantic absence claim is made and no cold empty reference result was used. Literal `grep` fallback on the exact runner/helper/two fixture files found the runner LANE definition/guard, `head_text` guard and record assertion; fixture LANE values feed default-tool selection and historical replay calls. Another exact-file grep inspected r20-input-binding round-20 references. Those working-file searches are literal corroboration only, not semantic proof or committed-byte provenance.

No target code, tests, builds, checks, clone, installs, live /proc, signals, or VCS mutations executed. No observed acceptance summary or 3/3 replay pass is claimed. Only this authorized report was written; production-byte identity was not independently measured. No scratch tree was needed for source-only review.

## Tradeoff / stopping boundary

Keep one small r21 acquisition boundary and the existing acceptance engine. The copy costs another historical runner but avoids changing old provenance or introducing a second acceptance convention. Further deletion of snapshots, runtime-runner binding, baseline extraction, summary matching or clone HEAD validation would harm acceptance strength. The executor must demonstrate S1/S2/S3 with identical per-step summaries and unchanged SRC digest/status; this review supplies no replacement for that evidence.
