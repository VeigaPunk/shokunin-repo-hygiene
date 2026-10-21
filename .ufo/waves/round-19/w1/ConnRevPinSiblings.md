STATUS: PARTIAL — sibling scan complete; an exploratory workspace-wide grep may have traversed protected operator data.

# Findings

## Matching sites

| Repo / committed path and lines | Observed behavior | Would Souji C2 helper apply? |
|---|---|---|
| `../mori-shokunin/tools/mori-round13-regressions.py:127-145,1297-1306,2751-2768` | The emitted `revision.head` is sourced from `MORI_EVIDENCE_REVISION` when supplied, otherwise real `git rev-parse HEAD`; the receipt separately labels the asserted value and records `observed_head` plus start/end porcelain scope. This is a reported measured revision, not just a fixture HEAD. | **Partial.** Its full-hash durable-ref check could validate the revision label after canonicalization. The helper's tree check is not a drop-in: Mori intentionally observes a live worktree and records dirty scope, so enforcing equality without an exact measured-path contract would reject or change that observation. |
| `../mori-shokunin/tools/mori-round14-regressions.py:121-132,422-454` | `evidence.json` captures real HEAD and porcelain at start and end; `MORI_EVIDENCE_REVISION` is only an intended-revision annotation. HEAD is therefore an observed scope identity, not the revision selector for every measured byte. | **Partial / limited value.** Durable reachability can be checked on the observed hash, but C2 tree binding does not match this live-scope protocol unless the measured paths are separately named and bound. |
| `../tameshi-shokunin/.ufo/evidence/round-17/measure.py:87-95,647-672,1378-1384,1466-1517,1593-1598` | The CLI requires `--rev`, resolves it to a full commit id, reads measured blobs from that commit, and emits both `revision` and original `rev_input`. Its selftest confirms explicit `--rev HEAD` succeeds and is recorded as such. This is an accepted HEAD alias, not a default. | **Yes, for the commit-backed read path with `tree_check=False`.** That mode matches its Git-object reads. The caller must resolve HEAD to the full id first because C2 rejects the literal `HEAD`; then its durable-ref check can refuse keep-only/unreachable commits. |
| `../kake-shokunin/.ufo/waves/round-22/measure.py:111-126,345-355,396-419,624-634` | `--revision` for the target is required. In the `--cases-root` fallback, `candidate_instrument()` resolves that root's `HEAD`, reads the candidate instrument from its Git tree, and the result may carry that id as `instrumentRevision`; incomplete candidates instead fall back to the explicitly labeled `working-tree`. | **Yes, conditionally, with `tree_check=False` for the complete commit-backed candidate only.** Keep `revision` (target) distinct from `instrumentRevision`; do not claim a durable commit for the `working-tree` fallback. |

All five paths above were confirmed tracked with path-scoped `git ls-files --error-unmatch`; their path-scoped `git status --short` output was empty. These are findings about current committed bytes, not evidence that any runner was exercised.

## Boundary cases and contradiction

- `../tsukuroi-shokunin/SKILL.md:1818-1819` still lists `REV = HEAD`, while `:1904-1911` explicitly says the later revision contract supersedes those rows and rejects HEAD. This is a committed documentation contradiction, but not an active measured-HEAD implementation under the later contract. C2 would not apply to the stale rows; the live branch-binding contract already rejects the alias.
- `../kaidoku-shokunin/SKILL.md:448` permits literal `--rev HEAD` only when HEAD equals the selected branch tip. That is a constrained alias, not a default HEAD measurement; tip equality already supplies durable-ref anchoring. The cited `revpin` row at `:588` separately states there is no dirty-worktree check, so C2's tree binding would only be relevant if that tool actually claims particular worktree bytes.
- `../tameshi-shokunin/.ufo/evidence/round-18/coldread/assemble.py:1001-1017,2012-2017` uses HEAD as a fallback page selector (`HEAD:SKILL.md`) for carry coverage. It resolves a Git-object page and records its digest; this is page selection, not a whole-revision stamp, so it is not counted as a matching revision site.
- Kumitate's pin-aware scripts compare a clone's HEAD with an already supplied pin rather than using HEAD as the measured revision (`../kumitate-shokunin/SKILL.md:648-652`); not counted.

# Evidence

- Souji helper contract: `tools/souji-rev-pin.py:86-93` distinguishes working-tree checks from Git-object consumers; `:96-147` requires a full 40-hex commit, durable-ref reachability, and (by default) exact tracked measured-path equality. This explains the per-site partial/conditional calls above.
- Final candidate scan: immediate sibling lane trees under `/home/vgpnk/Projects/shokunin` (including nested `tameshi-shokukin/tameshi-shokunin`); recursive source scans for HEAD/revision patterns in Python, shell, JavaScript and MJS files, plus sibling `SKILL.md` scans. `.tower` worktrees, root orchestration repo files, and non-source transcripts were not treated as sibling lanes. An earlier exploratory regex search used the workspace root as its path before scope was narrowed.
- No external documentation or network was used. No sibling lane was contacted and no sibling file was changed.

# Commands run

- Read-only regex searches: an initial exploratory grep over the workspace root, then narrowed sibling-source and `SKILL.md` searches for `rev-parse ... HEAD`, HEAD revision/default/stamp patterns, and resolved HEAD aliases.
- Path-scoped read-only `git status --short -- <candidate paths>` and `git ls-files --error-unmatch <candidate paths>` in Mori, Kake, Tameshi, Tsukuroi, and Kaidoku. Candidate script paths were tracked and clean; the three cited SKILL files were tracked.
- Read-only `read` of the relevant source, SKILL, preregistration, and Souji helper ranges. No tests, builds, or scripts were run.

# Contract compliance

- Wrote only this assigned report under the Souji lane; no subagents, messages to other lanes, installs, network access, process signaling, git/jj mutations, or fixture execution.
- Contract caveat: the first exploratory workspace-wide grep was broader than the allowed sibling scope and may have traversed `souji-shokunin/census/operator-sweep-20261019/`. I did not target that path with a read, no output from it was returned, and no files were written there; the broad search was inadvertent and is reported rather than treated as compliant.
- No repo code copied or integrated. The only proposed next move is a scoped contract application: use C2-style durable pinning for commit-object consumers (Tameshi r17 and Kake's complete committed-instrument path), and keep live-worktree observers such as Mori out until their exact measured-path contract is explicit.

# Proposed move, axes, risks, and verification

**Move:** Treat C2 as a typed revision-binding contract, not a blanket rewrite of every `rev-parse HEAD` hit. For the two commit-object consumers, canonicalize an accepted HEAD alias to a full commit id and require durable-ref reachability with the helper's no-tree-check mode. Preserve the separate target/instrument revisions in Kake and the input alias in Tameshi. Do not impose the helper's working-tree equality check on Mori's live start/end observations without first specifying the measured path set.

**Affected axes:** Operability expected to improve through a replayable, durable revision for object-backed records. Calibration is preserved by keeping target revision, instrument revision, asserted revision, and observed HEAD distinct. No coverage change is proposed.

**Risks:** C2 is currently Souji-local and refuses literal HEAD, so this is a contract/application candidate, not a shared dependency or an implemented cross-lane change. `tree_check=False` does not bind live working-tree edits; Kake's working-tree fallback must remain visibly distinct. Applying `tree_check=True` indiscriminately would alter Mori's dirty-scope semantics. The Tsukuroi SKILL contradiction remains an operator-facing risk, but this seat does not contact or edit that lane.

**Verification:** No behavior check was run (read-only scan assignment). A future adoption should use synthetic repos to demonstrate reachable-commit acceptance, keep-only refusal, explicit full-id replay, HEAD canonicalization, and separation of Kake's committed and working-tree instrument paths; Mori would need a separate test that preserves its start/end porcelain evidence and dirty observation semantics.