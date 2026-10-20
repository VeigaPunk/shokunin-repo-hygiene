# Round 13 — bounded operations and evidence integrity

Declared claims and independent before states: `census/round-13/claims.json`, baseline `31984f473ce4bdab61a99b16cca194b28108cb81`, observed starting metadata and source census `census/round-13/before.json`.

- C1 calibration (lowest non-retired axis): an executable consistency gate for declared installed-byte evidence, not a declaration that the receipt tools are safe.
- C2 operability: fail-closed bounds for quarantine staging and digest operations, including special-file refusals.
- C3 coverage: a sourced F2 structure-census entry and isolated empirical write-safety fixture.

Scores stay 7/8/8 (calibration/operability/coverage), legacy-unmapped; an integrity-test count is not a calibrated 0–10 score. The claims are causally separable: C1 uses its own manifest fixtures; C2 uses receipt fixtures without C1; C3 uses an isolated Git repository without either tool.

## Mistakes

| id | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| R13-M1 | reference-drift: prose claimed a committed fixture that did not exist | `corpus/lessons/round-12-verifier-spotcheck.md`, K5 reject/hold; `corpus/lessons/round-12.md`, Post-review fixes item 2 | Q17 added this round; prior Q4 did not mechanically resolve the path | Missing-evidence and path-escape negative cases in the evidence gate; committed F2 fixture path is resolved separately at admission. K5 stays HELD. |
| R13-M2 | attribution / wrong-byte certification: a shared relay was overwritten and verdicts referred to non-installed bytes | `corpus/lessons/round-11.md:12-20`, M40/M41 in `round-12.md` | Q6 existed; Q18 now separates integrity from actual safety | Each declared fragment binds artifact bytes, evidence bytes, author label, command, class and exit status. Adversarial selftests reject inconsistent records. Labels are not authenticated identities; this is not proof that commands ran or class coverage is complete. Certification stays OFF. |
| R13-M3 | operability: staging hung to a driver timeout | `LOG.md:432-437`; round-12 M43 | Q8 existed but was unenforced | Per-target move and digest bounds, diagnostics and fail-closed regression fixture. A timeout never authorizes stage-5 deletion. Partial staging may leave recoverable quarantine residue. |
| R13-M4 | operability: FIFO digest readers hung for hours | round-12 M44; `LOG.md:403` | Q8 existed but was unenforced | Reject special files and special descendants before digesting; bound digest readers as a second line of defense. |
| R13-M5 | circular criterion: Q15 was written to excuse the very candidate it admitted | `corpus/lessons/round-12.md`, Post-review fixes item 3; QUALITY Q16 | non-author r12 review caught it | Q16 remains in force. No `/dev/shm` exception is reintroduced. New criteria cite distinct historical failures and runnable falsifiers, not their own admission as justification. |
| R13-M6 | stale-premise: the overwritten historical relay remains committed with a candidate CERTIFIED claim | `census/round-10/cert-16.json:10,20,2618-2620` (candidate census `60aef4c0…`); `.ufo/waves/round-13/w1/AttackCalibration.md` | Q6/Q18; earlier round summaries did not explicitly supersede the stored claim | This entry explicitly supersedes that relay's certification claim as authority for installed tools. Preserve historical bytes, replay the candidate digest against installed census bytes through the new gate, and record the rejection. All installed-tool deletion certification remains OFF. |
| R13-M7 | scope: optional locks were mistaken for a sufficient no-write guard | `.ufo/waves/round-13/w1/AttackCoverage.md`, observed partial-clone lazy fetch despite optional locks off and maintenance disabled | Q1/Q2; original bounded fixture did not cover promisor repos | Always disable lazy fetch, refuse partial/promisor configuration before enumeration, reject stderr/nonzero outcomes, and document refs-rooted/incomplete-accounting limits with S037. The original attack is not rerun merely to confirm it. |

A fix counts only after its red or discriminating-negative observation is committed. The actual commands, exit codes, findings and measured revision are recorded in `census/round-13/verification.json`; a test name or criterion row alone is not proof of capture.

## Gate

| candidate | decision | reason / evidence |
|---|---|---|
| C1 declared-fragment integrity validator | admit only within the consistency-checking scope | `tools/souji-cert-evidence.py`, negative/positive self-invocation fixtures, digest-pinned frozen inputs; actual outcome in verification evidence |
| F2 `knowledge/git-repo-structure-readonly.md` | bounded domain entry | S035/S036 correct opened S005/S006, with tagged S037; committed `tests/fixtures/r13-repo-structure.sh` compares isolated repository metadata/content before and after |
| C2 bounded quarantine operations | bounded safety improvement, not broad certification | Same `tests/fixtures/r13-quarantine-bounds.sh --tool <path>` command runs against baseline and changed bytes; output records the reason for the red-before failure |
| Grant deletion certification from C1 success | REJECT | Fragment consistency cannot prove command execution, independent identity, comprehensive class coverage, or absence of unsafe deletion. Tool certification stays OFF. |
| Re-admit K5 or revive Q15 | REJECT / retain hold | No new committed cross-device fixture or independently lesson-grounded exception was supplied. QUALITY Q4/Q16 still bind. |
| Treat structure size as recoverable disk space | REJECT | Structure describes reachable Git objects; it is not a per-artifact receipt or filesystem-space estimate. |

Outside spot-check: the previous round's non-author admit/reject sample is `round-12-verifier-spotcheck.md` (W3ReviewSouji). Its K5 disagreement becomes Q17 and R13-M1; its certification/timeout debts are addressed without treating lane-dispatched reviewers as independent non-authors. This round's fresh outside admit/reject sample is reserved for the orchestrator's closure; the lane does not invent it or mark SHONEN `[x]`.

### Opened sources and located quotes

- **S035 (supersedes S005)**: https://git-scm.com/docs/git-repo, accessed 2026-10-20, web Git 2.56.0 / installed 2.55.0. COMMANDS / structure / table: “This format may change and is not intended for machine parsing.” Opening report: `.ufo/waves/round-13/w1/SourceRepo.md`. Delimited output is not a promise of stability or no writes.
- **S036 (supersedes S006)**: https://git-scm.com/docs/git, accessed 2026-10-20, web Git 2.56.0 / installed 2.55.0. OPTIONS / no-optional-locks: “Do not perform optional operations that require locks.” Opening report: `.ufo/waves/round-13/w1/SourceLocks.md`. Mandatory writes and lazy fetching are not optional lock-taking.
- **S034**: https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html, attempted 2026-10-20; web connection timed out. Installed vendor source `/usr/share/info/coreutils.info.gz`, coreutils 9.11-2, node timeout invocation / --kill-after, lines 15316-15317 opened instead: “Ensure the monitored COMMAND is killed by also sending a ‘KILL’ signal.” Opening report: `.ufo/waves/round-13/w1/SourceTimeout.md`. This is not a claim of a successful web fetch.
- **S037**: https://raw.githubusercontent.com/git/git/v2.55.0/builtin/repo.c and https://raw.githubusercontent.com/git/git/v2.55.0/path-walk.c, opened 2026-10-20, tag v2.55.0. `structure_count_references` line 744: `refs_for_each_ref(get_main_ref_store(repo), count_references, &data);`. `count_objects` lines 798-801 skips failed object-info reads; `cmd_repo_structure` ends `return 0;`. The tree walker calls `repo_parse_tree_gently`; the observed lazy-fetch counterexample is `.ufo/waves/round-13/w1/AttackCoverage.md`, not inferred from a source comment.

### Registry changes

No existing row has a net in-place change. Original `opened` dates stay 2026-10-19. Mid-flight S005/S006 `queued → mined` and `— → F2 path` edits were reverted (`mined → queued`, `F2 path → —`) after review found overbroad source wording. Corrections are new rows, not forbidden teaches/anchor rewrites.

| row | decision | old → new |
|---|---|---|
| S005/S006 | preserve historical rows, corrected by new rows | queued/— → queued/— (net unchanged) |
| S034 | add opened timeout source cited by this lesson | absent → mined, used-by corpus/lessons/round-13.md |
| S035 | add correction superseding S005 | absent → mined, used-by corpus/knowledge/git-repo-structure-readonly.md |
| S036 | add correction superseding S006 | absent → mined, same F2 used-by |
| S037 | add tagged implementation failure boundary | absent → mined, same F2 used-by |

The registry census commands and outputs before/after, histogram counts and source additions are carried in `census/round-13/verification.json`. The old r12 census `mined=18 queued=13` predates the post-review S024/S025 holds; the round-13 starting registry is `mined=16 queued=15 rejected=2`, as recorded by the baseline scribe. Counts are re-derived in this round rather than copied from that stale output.

## Routed previous-round items

- K5 nonexistent-fixture claim: held, never silently re-admitted; Q17/R13-M1 address recurrence.
- Q15 circular exception: Q16 retained; fixtures stay under `/var/tmp`.
- S030 missing recheck: prior landed `365d` correction retained; no row rewrite.
- K2 wrapped-man recheck: prior `MANWIDTH=2000` correction retained; unrelated facts are not rerun as if new knowledge.
- C1 r12 rule-coverage count: explicitly not proof of demonstrated catches; current integrity fixtures are a different measurement.
- Quarantine timeout: C2, with red-before evidence required.
- Certification: OFF. The existing r9-class toolchain suites have not been replaced by the integrity validator. No-relay comprehensive certification remains a separately bounded class-suite decision.

## Scope, wave and inherited state

One campaign-policy-validated wave of 32 leaf seats, unchanged validator taskCall; L1 holds the canonical planner seat (validator excludes planner swarm role). Specs, dispatch payload, assigned registry and each independent report live under `.ufo/waves/round-13/`. No author is an outside verifier.

Initial lane state had no lane-authored leftovers. The sole initial untracked path, `census/operator-sweep-20261019/`, is OPERATOR-authored: not edited, moved, committed or deleted. L1 did not inspect its contents. BaselineMeasures disclosed an overbroad read-only search that emitted some matching sweep lines before it narrowed its search; this was a seat process deviation, not authorization to touch the sweep. No live artifact removal, history rewrite, credential handling, sibling write, or operator runtime mutation was performed. Tool installs and other seat process deviations, if any, are reported in the landed round report.

## Adjudication of wave disagreements

- ReviewSHONEN initially included unindented PROTOCOL commentary in its seed
  extraction, then withdrew that verdict in its appended report §8. The actual
  seed is the indented block, independently matching
  `/home/vgpnk/Projects/kimi-shokunin/templates/mint/SHONEN.md`. The extraneous
  `Marks:` paragraph is removed; all four marks remain author `[~]`.
- ReviewEvidence correctly identifies that declared-fragment consistency is
  weaker than complete certification. The admitted C1 scope excludes complete
  class coverage, actual execution provenance and authenticated author identity;
  no comprehensive certification or deletion authority is inferred.
- ReviewSize's universal write-safety design is not the C3 claim. C3 is bounded
  to the normal isolated fixture's persistent Git-directory state on the observed
  host version. Bare/linked/shallow/alternate/concurrent configurations and
  transient writes are explicitly not proved.
- BaselineMeasures and SourceBookkeeping found stale r12 histogram output.
  The before count is re-derived from baseline commit 31984f4, not from the
  pre-correction r12 result. Mid-flight working-tree additions are not inherited
  state: the only initial untracked path was the protected operator sweep.


Historical M43's exact cause is not established by this round: serial
450-second hold windows could also exceed a driver timeout (SafetyPaths
SP-Q3, inference). The installed baseline already refuses a stable FIFO
inside its later helper definitions, but can exit without a per-target
diagnostic. C2 claims explicit operation bounds and diagnostic fail-closed
behavior, not proof that it would cure every historical timeout or that all
FIFO refusal is newly acquired.

## First integrated verification and corrections

The first run at source commit `6ed10a7cd6c7b26f8068dd6e02497e860f9c4317`
is preserved verbatim in `census/round-13/verification-attempt-1.json`.
It is not reported as green:

- Evidence gate: 35/36; the actual tamper finding/exit were correct, but the
  embedded finding-id regex excluded `_` and missed `snapshot_tampered`.
  The correction accepts underscore ids without changing expected findings.
- External gate fixture: 4/5, solely because it invokes that embedded selftest.
- Structure probe fixture: 5/5 PASS, including detector controls, persistent
  manifest equality, exact metrics, invalid-repo and partial/promisor refusal.
- Baseline bounds fixture: one PASS, four failures including two outer-bound
  hangs. Changed tool: four PASS, one failure; a broad SHA shim intercepted
  the receipt engine rather than isolating the intended pin digest. The
  fixture must be corrected and the baseline/fixed pair rerun on identical
  corrected fixture bytes; a wrong-reason failure is not a demonstrated fix.
- Legacy selftests: fixture commits lacked author identity because the main
  runner deliberately disabled global Git config. The runner now supplies
  synthetic author/committer environment values, without writing host config.
- Warning-level ShellCheck found redundant patterns, unused assignments,
  an unquoted string and a masked local assignment in the changed tool.
  These are corrected, not suppressed; warning severity is not weakened.

Passing checks are retained with their own measured commit; only failed
checks are retried after corrections, plus the paired baseline because its
fixture changes. `verification.json` records the final per-check revisions.
Historical wrong-byte and candidate substitutions already rejected with
the exact expected findings and exit 2. Source census already exited 0:
37 rows, A=33/B=3/C=1, mined=20/queued=15/rejected=2.

Integration rejected extra stage-5 deletion timeouts from the implementation
seat: killing a deletion can leave partial residue, so “copy kept” would
be false. Q8 is limited to staging/digest/inspection bounds; deletion remains
behind the existing successful second-check gate. A failed deletion now
honestly names potentially partial residue rather than promising preservation.


## Final measured gate decisions

The corrected failed-check run at
`6f8ee0f38a14a3cb599ee606c486a55ec64e8ae6` completed successfully.
`census/round-13/verification.json` retains unchanged passing observations
at `6ed10a7cd6c7b26f8068dd6e02497e860f9c4317` and names each result's
actual revision; no retained check is described as rerun.

- **C1 admitted within declared-consistency scope**: embedded selftest
  `36/36 passed`, external black-box fixture `5/5`, frozen input run clean
  with seven input pins, historical wrong-byte and candidate substitutions
  reject with `artifact-digest-mismatch` / `artifact-candidate`, exit 2.
- **C2 admitted within bounds scope**: the same corrected fixture at 6f8ee0f
  has baseline `total=5 failed=4 hung=2`, exit 1, and changed-tool
  `total=5 failed=0 hung=0`, exit 0. Target-specific shims avoid the receipt-
  engine confound. Built-in verify/vault/quarantine/census suites:
  40/51/91/36 checks, zero failures. Warning-level ShellCheck exits 0.
- **C3/F2 entry admitted**: structure fixture `selftest=PASS ids=5/5` at
  6ed10a7, including persistent-manifest detector controls and partial/promisor
  refusal. Revision-bound census `count-claims.py 31984f4` versus
  `count-claims.py 6f8ee0f` shows admitted entries 4→5 and F2 entry 0→1.
- **Rejects retained**: deletion certification from integrity evidence,
  K5 re-admission/Q15 revival, universal no-write and reclaimable-space
  interpretations of structure metrics.

Registry: 33→37 rows; A=29→33, B=3→3, C=1→1;
mined=16→20, queued=15→15, rejected=2→2. Exact counting commands and
outputs: `census/round-13/counts.json`. Start/end contract census stdout
is `souji<TAB>ok<TAB>/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md`,
exit 0 both times (`before.json`, `verification.json`, sources-contract).
New rows by tier: four A, zero B/C. One newly admitted knowledge entry,
not four rows, is the expansion gain.

Author trend verdicts: expansion **improved** (sourced F2 entry and bounded
capability); quality **unchanged** under the strict existing-admitted-
knowledge recheck/supersession bar (operability improves, but no separate
stale-entry sweep is claimed); discernment **improved** (outside K5
disagreement becomes Q17, executable missing-evidence rejection, and
committed fixture resolution). All three claimed axes improve on their
bounded measurements; other axes are unchanged. These are author verdicts,
not an invented outside spot-check or promotion.


### Ending census output correction

The ending census was executed again after the source introduction received
its provenance correction, at `23014d40e48e52031939f124ce0ed215ca932c6f`.
The earlier final-gate paragraph quoted only the ok line and omitted
advisory stdout. Complete observed ending stdout is in
`census/round-13/end-sources.json`: W04 for S035 duplicate git-repo URL,
W04 for S036 duplicate git URL, then the ok line; exit 0. These same-URL
rows are deliberate append-only corrections superseding S005/S006, not
unopened duplicates. The starting census had no W04 lines, exit 0.

