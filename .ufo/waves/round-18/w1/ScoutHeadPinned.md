STATUS: DONE — both HEAD pins confirmed; both resolve HEAD to `b576341` (detached at, and durable via, `refs/heads/master`) if run now; no SKILL/SCORECARD claim depends on re-running either; smallest fix stated below.

# Scout: HEAD-pinned evidence consumers (r13/r14 residual)

Question: `census/round-13/run-verification.py:384` and
`census/round-14/cache-demonstration.py:166` pin `HEAD`; in this jj-colocated
lane HEAD is detached after helper commits. What would they measure now, does
any SKILL/SCORECARD claim depend on re-running them, and what is the smallest
fix? No execution of either script (forbidden).

## 1. The two sites (observed source)

| site | call | disposition |
|---|---|---|
| r13 | `run-verification.py:384` `revision = git("rev-parse", "HEAD")`; `:385` `CURRENT_REV = revision` | Freshly executed results are stamped from this one value at `:238` (`item["measured_commit"] = CURRENT_REV`); `--retry-failed` retained results keep their own prior `measured_commit` (returned before `:238`); the top-level record carries the run-start value at `:435` |
| r14 | `cache-demonstration.py:163-178` `git_head()` → `git -C LANE rev-parse --verify HEAD` | Read **three** ways: per gate invocation at `:264` (`invoke_gate` evidence), per producer execution at `:410` (`producer`), and once at start `:1107` (`initial_commit`); recorded as `measured_commit`/`harness_revision` at `:961-962` and `:973` |

Neither site checks that the resolved commit is contained in a durable ref
(`refs/heads|tags|remotes`), that it is not detached, or that the bytes the
runner is about to execute equal the commit's blobs. `git rev-parse --verify HEAD`
proves only resolution; it accepts a keep-ref-only commit. The r13 CLI has no
`--rev` (`argparse` at `:343-351`: `--round`, `--output`, `--retry-failed`,
`--previous`); the r14 demo CLI has only `--gate` and `--keep`
(`:1075-1087`).

## 2. Current HEAD state (observed, read-only)

```
.git/HEAD                       b5763415cc67ecff1e8fe56c58c39a6fb106d7a3
rev-parse --symbolic-full-name HEAD   HEAD        # detached
rev-parse HEAD                  b5763415cc67ecff1e8fe56c58c39a6fb106d7a3
refs/heads/master               b5763415cc67ecff1e8fe56c58c39a6fb106d7a3
refs containing HEAD            refs/heads/master, refs/remotes/origin/HEAD,
                                refs/remotes/origin/master
git diff --quiet HEAD -- <both scripts, both verification JSONs, tools/>
                                CLEAN
git diff --stat 2cfc6c0 b576341  1 file changed, 157 insertions(+)
                                (corpus/lessons/round-17-verifier-spotcheck.md)
```

So *right now* HEAD is detached but is exactly the master tip, is also the
pushed `origin/master` tip, and the tracked working tree equals its tree. If
either script were invoked now, it would record `b576341`, which is durable and
contains the tracked bytes being measured. The round-17 reflog entries for HEAD
are `export from jj`, and the commit is a real, non-empty round-17 integrator
commit on the master tip. The round-17 lane observation plus
`corpus/knowledge/jj-colocation-receipts.md:19-23` put that detached head at the
just-committed change — the working-copy parent `@-` — and the entry labels the
`@-` mapping as `[INFERENCE]`; the non-empty commit is consistent with a real
commit rather than an empty placeholder.

After helper commits the same structure applies: `jj commit` moves HEAD to the
just-created commit (the new working copy's parent), and
`scripts/hyaku/jj-lane.sh:653-655` then sets `refs/heads/master` to that same
hash. A *successful* helper therefore leaves HEAD detached at the branch tip;
three other states are not durable:
1. the window between `jj commit` and `bookmark set` (`:641` vs `:653`), or a
   helper that fails a sweep guard before `bookmark set`, leaves HEAD at an
   unbookmarked commit (knowledge §8: a refused attempt still leaves a
   keep-held commit; the knowledge entry records four such phantom-deletion
   commits in this lane);
2. a seat's direct unbookmarked `jj commit`/`jj describe`/`jj new` — recorded in
   `JjAuditSouji.md:103-104` (as cited at `jj-colocation-receipts.md:32`) to
   leave `refs/jj/keep/<sha>` as the only containing ref;
3. any working-copy changes in `@` that have not been committed: HEAD stays at
   `@-` and its tree does not contain the bytes the scripts execute.

## 3. What they would measure now

The HEAD pin in both would resolve to `b576341` if invoked today (for r13,
freshly executed results and the top-level record; retained results keep their
prior commit; for r14, every recorded read). That value currently satisfies the
r17 rule (`jj-colocation-receipts.md:79-80`: pin an explicit commit on
`refs/heads`, `refs/tags` or `refs/remotes`, or refuse), and the tracked working
tree is clean against it (`git diff HEAD -- .` empty; the seven artifact
digests at `:390-394` match their blobs). So a run now would be replayable and honest for tracked inputs; the
residual is **latent, not currently triggered**.

The defect remains real for the next run: the scripts never bind
`measured_commit` to the measured tree, and they accept either an off-branch
keep-only commit (states 1–2 above) or a commit that predates uncommitted
working-copy changes (state 3). A future r13/r14 record created in any of those
states would name a commit that either is not durably reachable or does not
contain the bytes it claims to measure.

## 4. Callers

- `census/round-14/run-verification.py:54` and `census/round-14/run-targeted.py:23`
  independently `git("rev-parse", "HEAD")` and stamp `measured_commit=revision`
  on their own records (`run-verification.py:85`, `run-targeted.py:45-46`).
  They invoke `census/round-14/cache-demonstration.py` with no args (expect 0)
  and `census/round-13/run-verification.py` with no args (expect 2)
  (`run-verification.py:69-70`, `run-targeted.py:35-36`). Both refuse to
  overwrite `census/round-14/verification.json` (`:52` / `:21`), so they have
  no live re-run path as committed; their HEAD pins are the same defect class
  if either is ever re-run against a new target.
- `census/round-14/cache-demonstration.py:337-338` imports
  `census/round-13/run-verification.py` read-only and pins its
  `CURRENT_REV=initial_commit` at `:672`; the baseline arm is separately pinned
  at `a31642d` (`:74-75`). The demo's own `head-changed-between-gate-invocations`
  advisory (`:955`) is live — it compares the three gate-invocation evidence
  records, each of which re-read HEAD at `:264` — but it does not cover the
  producer reads or the initial read.
- `tools/souji-landing-gate.py` has no `run-verification`/`cache-demonstration`
  reference (grep: none). The only in-tree references found from the exact
  files read are the r14 wrappers, SKILL/SCORECARD prose and the r17 lesson;
  `tests/` was not recursively scanned, so a fixture caller is not excluded.

## 5. Historical evidence and SKILL/SCORECARD dependency

- `census/round-13/verification.json`: `measured_commit`
  `6f8ee0f38a14a3cb599ee606c486a55ec64e8ae6`, a commit that is an ancestor of
  both `refs/heads/master` and `refs/remotes/origin/master`.
- `census/round-14/verification.json`: top-level `measured_commit`
  `552cae4204b3ab818419ad8adbfef3a4da29a3e0`; the nested
  `cache-consumer-red-green` stdout records the same value as
  `measured_commit`/`harness_revision`. That commit is also an ancestor of
  `refs/heads/master` and `refs/remotes/origin/master`.
- Therefore neither historical record is dangling today, and the C2 rule
  "a frozen record whose `measured_commit` does not resolve is
  LG-FROZEN-MEASURED" does not fire on them. Note the limits of that rule:
  `tools/souji-landing-gate.py:544-600` checks resolution only
  (`git rev-parse --verify <measured>^{commit}`), so a keep-only commit passes
  while it resolves and can later be pruned; the durable-ref check below is
  stronger and should be the HEAD fix, not merely resolution.
- SKILL.md:229-235 describes the consumer and demo as capabilities but states
  no live measured commit. SCORECARD.md:23-30 is a historical-provenance note
  (`--retry-failed` reproduced at `6f8ee0f`, not against the migrated runner);
  SCORECARD.md:42 and :45 cite the committed JSONs, not a re-run; SCORECARD.md:81
  lists "HEAD-pinned consumers r13/r14" as an r18 planned residual.
- **Verdict: no SKILL/SCORECARD claim depends on re-running either script.**
  Both historical measured commits resolve and are reachable from the local
  remote-tracking `refs/remotes/origin/master` (not re-fetched); the r13 runner
  requires a new `--output` and the r14 wrappers refuse to overwrite. If a
  required `--rev` is added, the prose that enumerates the runner's required
  arguments (SKILL.md:230-232, SCORECARD.md:25-27) needs one sentence updated,
  but no measurement claim changes.

Adjacent observation (not the HEAD question, same authority files):
SCORECARD.md:37 and :39 call the r13 record's digests "current installed
digest". Today `tools/souji-verify.sh` hashes `f88fed23…` (record `9adb1764…`),
`tools/souji-vault-verify.sh` `5cb0fb13…` (record `f9e778ca…`); quarantine
(`83cc3ce1…` vs `df407511…`) and census (`006b9823…` vs `6a000c59…`) also
differ; cert-evidence (`943d664c…`) and repo-structure (`80025137…`) match.
The record was written at `6f8ee0f` with six artifact paths; the current runner
covers seven (evidence-cache was added later). So "current" is already stale
for those rows irrespective of HEAD, and the historical record cannot vouch for
the current script's seven-artifact set. Reword to "digest recorded at
`6f8ee0f`" (or refresh with a new explicit-rev record); no re-run is needed
merely to see this.

## 6. Smallest fix

Recommended (matches the lane's own rule and closes ambient identity):

1. `run-verification.py`: add a required `--rev <commit-ish>`; resolve once with
   `git rev-parse --verify <rev>^{commit}`; reject `HEAD`; require the resolved
   SHA to be contained in `refs/heads`, `refs/tags` or `refs/remotes`
   (`git for-each-ref --contains`). Replace `:384` with that value and record a
   `measured_commit_basis` string. Because the runner executes the **working
   tree**, add the one missing binding: before running, refuse (exit 2) when
   `git diff --quiet <rev> -- <the seven artifacts at :390-394>` is nonzero.
   Without that guard, an explicit `--rev` can still name a commit that does not
   contain the measured bytes.
2. `cache-demonstration.py`: same required `--rev`, resolved once and
   durable-ref-checked; use the captured SHA for `initial_commit`
   (`:1107`), `producer()` (`:410`) and `invoke_gate()` (`:264`) instead of
   re-reading HEAD (or keep HEAD only as a drift check, recording both). Change
   the basis string at `:962` to `--rev`.
3. If the r14 wrappers are ever made re-runnable, pass their already-resolved
   revision as `--rev` and update the demo command in their lists; the
   `historical-runner-default-refusal` expectation (exit 2) stays valid.

Absolute minimum alternative (no interface change): after
`git rev-parse HEAD`, require
`git for-each-ref --format=%(refname) --contains <sha> refs/heads refs/tags refs/remotes`
to be non-empty, else exit 2 / emit the r14 blocked payload. About four lines
per site; it closes the keep-only case (states 1–2) and preserves the current
CLI, but it leaves the ambient HEAD identity, the working-tree-ahead case
(state 3), and the demo's multiple reads unfixed. Prefer the `--rev` form.

## Commands run (read-only; no script executed)

```
git -C <lane> rev-parse HEAD
  b5763415cc67ecff1e8fe56c58c39a6fb106d7a3
git -C <lane> rev-parse --symbolic-full-name HEAD
  HEAD
cat <lane>/.git/HEAD
  b5763415cc67ecff1e8fe56c58c39a6fb106d7a3
git -C <lane> for-each-ref --format='%(refname) %(objectname:short)'   (head)
  refs/heads/master b576341
  refs/jj/keep/... (round-17 commits)
git -C <lane> diff --stat 2cfc6c0 b576341
  corpus/lessons/round-17-verifier-spotcheck.md | 157 ++++++++++++++++++++++++++
git -C <lane> diff --quiet HEAD -- census/round-13/run-verification.py \
  census/round-14/cache-demonstration.py census/round-13/verification.json \
  census/round-14/verification.json tools/ && echo CLEAN
  CLEAN
git -C <lane> for-each-ref --format='%(refname)' --contains HEAD refs/heads refs/tags refs/remotes
  refs/heads/master
  refs/remotes/origin/HEAD
  refs/remotes/origin/master
git -C <lane> cat-file -t 6f8ee0f... ; merge-base --is-ancestor 6f8ee0f... master
  commit ; yes
git -C <lane> cat-file -t 552cae4... ; merge-base --is-ancestor 552cae4... master
  commit ; yes
sha256sum census/round-13/run-verification.py census/round-14/cache-demonstration.py
  01fc18dd1e849f8268c07f057c947b82236d54abff47f5d9c5984591fba2a9db
  aa36d332bf37bf14d5031990b27644fa1982e71b504f0d2bce2983fc9540d8e7
```

## Remaining unknowns / limits

- The `@-` identification is supported by the docs (S051) and the round-17 lane
  observation (`jj-colocation-receipts.md:19-22`); it was not re-measured with
  `jj` here (only read-only git).
- Neither script was run; this is source-level evidence plus read-only git.
- The round-18 goal C1–C3 does not schedule a new r13/r14 record, and the
  committed r14 wrappers cannot re-run without a code/new-target change; whether
  a later round needs a fresh runner record is outside this question.
- The landing gate's LG-FROZEN-MEASURED check tests resolution, not durable-ref
  containment (`souji-landing-gate.py:544-600`); if the C2 fix relies on it to
  catch this class, it will miss a still-resolvable keep-only `measured_commit`.
