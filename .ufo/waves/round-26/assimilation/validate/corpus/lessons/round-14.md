# Round 14 — retained evidence and credential-store census boundaries

Declared claims: C1 calibration (lowest non-retired axis), digest-bound eligibility of retained green observations; C2 operability, pre-access protected-path refusal in the metadata census. Baseline `a31642d14006830ec62edf40b0354c3699728c4a`; declarations and exact counting commands: `census/round-14/claims.json`. Scores remain legacy-unmapped 7/8/8, numeric delta 0. No comprehensive deletion recertification is claimed.

## Mistakes

| id | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| R14-M1 | stale-green evidence retention can retain an old success after the measured tool changes | round-13-verifier-spotcheck.md, Routed findings item 3; census/round-13/run-verification.py retention branch | Q6/Q18 bound individual evidence, not retention eligibility | New digest-bound eligibility gate and current-round consumer preserve the original measured revision and refuse stale/legacy inputs; discriminating observations are recorded in census/round-14/verification.json, not inferred from source. |
| R14-M2 | citation-location drift: correct quote assigned incorrect installed-manual line numbers | round-13-verifier-spotcheck.md, Routed findings item 1; SOURCES S034; round-13.md Opened sources S034 | CORPUS quote names its location | S038 supersedes immutable S034; the named erratum below corrects the prior lesson without rewriting it. |
| R14-M3 | arbitrary census input can point at the credential store or an ancestor and reach metadata/content readers | baseline tools/souji-census.sh main/emit_census/emit_compare; round-14 boundary fixture baseline observation in verification.json | Never credentials boundary existed but arbitrary --root/--compare lacked a pre-access enforcement rule | Pre-access lexical/component boundary checks plus isolated synthetic-HOME command-spy cases; real credential store is never probed. |
| R14-M4 | integration fallthrough returned a retained source despite a correctly red eligibility decision | verification-attempt-1.json, cache-consumer-red-green at 48f8945: migrated stale has exit 1 / dependency-digest-mismatch but retained=true; 32 other assertions true | Q20's real-consumer stale case caught it; gate-only green did not prove caller enforcement | Return no retained source whenever eligibility is nonzero; do not weaken the fixture. Corrected exact-command observation is recorded separately. |

A criterion is not a demonstrated fix by itself. The final measured decisions below bind any admission to committed red/discriminating evidence.

## Gate

Candidate decisions: admit only demonstrated declared-dependency cache eligibility and bounded credential-namespace census protection; reject broad certification, complete dependency inference, authenticated historical execution, universal race-free filesystem sandboxing, or deletion authority. K5 stays HELD; Q4/Q16 remain in force. A fresh outside admit/reject sample remains the orchestrator's independent closure duty, not any lane-dispatched seat's authority.

### Named erratum: round-13 S034 located quote

This corrects `corpus/lessons/round-13.md`, Opened sources S034, and its immutable registry anchor without editing historical bytes. L1 opened installed `/usr/share/info/coreutils.info.gz` using Python gzip on 2026-10-20, GNU coreutils 9.11 (`timeout --version`). Node timeout invocation / --kill-after quote is at **15319–15320**, not 15316–15317: “Ensure the monitored COMMAND is killed by also sending a ‘KILL’ signal.” Exit 124 is at **15365**, not 15349. Source URL: https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html; installed vendor source, not an assertion of successful web access. S038 appends the corrected anchor. Quote length is below 25 words.

### Opened sources

- S038: installed GNU coreutils 9.11 vendor documentation and URL above, accessed 2026-10-20, located quote in the named erratum. Its teaches text supersedes S034's anchor; it does not broaden timeout safety claims.
- S039: repo source `tools/souji-evidence-cache.py`, accessed 2026-10-20, round-14 source SHA-256 `dd279ba95eebd13a6674f79983cec286fd856aa6d7e0719bf551ae0fc08939d6`, `_evaluate_dependencies` docstring lines 929–930: “Measure every declared dependency in sorted order.” `_emit` line 1211 expressly says no command execution or historical proof. C1 cites this primary implementation source; observed capability still requires the separate final run, not this quote.
- S040: https://docs.python.org/3/library/pathlib.html#pathlib.Path.resolve, accessed 2026-10-20, Python 3.15.0 online documentation / Path.resolve: “Make the path absolute, resolving any symlinks.” Pure paths introduction separately states purely computational operations without I/O. Resolution itself can access filesystem metadata; this supports checking lexical/component boundaries before resolution, not a claim that resolve is a sandbox. C2 cites this source.

Registry additions: S038 absent→mined / lesson used-by, S039 absent→mined / lesson used-by, S040 absent→mined / lesson used-by; all tier A for their narrow scopes. Existing S001–S037 status/recheck/used-by cells are unchanged. No old immutable cell is rewritten.

### Routed prior-round limitations

R13 C2 proved five named cases, not cross-device refusal, stalled tracked git mv, directory-digest, find/receipt/special-scan timeout, or index-lock residue. Those remain unproved implementation observations; this round does not rebrand them as acquired capabilities. K5 remains held and certification OFF. The r13 retained-run evidence was independently digest-compared by its closure; this round does not retract those bounded historical observations or rewrite that evidence.

### Scope and dispatch

One campaign-policy-validated 32-seat leaf wave, taskCall unchanged, under `.ufo/waves/round-14/`; L1 holds canonical planner seat because the validator excludes planner as a swarm role. Baseline sole untracked path `census/operator-sweep-20261019/` is OPERATOR-authored and excluded from all reads/staging. No inherited lane-authored work. Never probe the real credential store, never launch separate omp processes. No live deletion, quarantine, sibling write, history rewrite, or runtime mutation.

## First integrated measurement and corrections

At committed source `48f8945780adeb259cff0ef7dd9b7efbf1544ec7`,
`python3 -B census/round-14/run-verification.py` exited 1. Complete
observations are preserved in `census/round-14/verification-attempt-1.json`.
The following are not described as green:

- The consumer demonstration had one failed assertion,
  `migrated_caller_refuses_stale`: the gate correctly returned exit 1 and
  `dependency-digest-mismatch`, but `attempt_reuse` still returned the prior
  source. R14-M4 fixes the return value, not the expected finding.
- Both census paired runs were could-not-evaluate, exit 2, because fixture
  setup tried to update an alternate-backed ref before its commit object was
  available. This is not baseline-red proof or a census safety verdict.
- Warning-level ShellCheck failed on the unquoted hyphenated literal
  `PROTECTED_FINDING=path-protected` (SC2100). Quote the constant; do not
  suppress the warning or lower severity.

Actual passing first observations: cache selftest 48/48; external fixture
22/22; frozen snapshot reusable with two pins; historical runner default
refusal exit 2; census embedded selftest 38 checks / zero failures; exact
source-anchor probe S034 exits 1 and S038 exits 0; required source census
exit 0. Canonical artifacts and historical r13 JSON were unchanged during
the run. These remain observations at 48f8945, never relabelled as later
executions. The targeted runner repeats only failed checks plus green checks
whose subject bytes changed.

## Final measured gate decisions

Source snapshot `48f8945780adeb259cff0ef7dd9b7efbf1544ec7`;
correction snapshot `552cae4204b3ab818419ad8adbfef3a4da29a3e0`.
`python3 -B census/round-14/run-targeted.py` exited 0. It did not rerun
unchanged passing gate/fixture/frozen/source-anchor checks or relabel their
old revision. `verification-attempt-1.json` and `verification.json` together
are the complete measured record.

| candidate | final decision | measured evidence and limit |
|---|---|---|
| C1 declared-dependency eligibility plus migrated consumer | ADMIT within declared-byte scope | gate `--selftest` 48/48; external fixture 22/22; two-pin frozen input clean at 48f8945; corrected consumer 33/33 at 552cae4. Authentic baseline retains the stale green without invoking the producer; new policy invokes the harmless producer again, and actual migrated stale decision returns no retained source. |
| C2 credential-namespace census fence | ADMIT within the tested namespace cases | identical corrected `python3 tests/fixtures/r14-census-boundary.py --tool <path>` at 552cae4: baseline `total=12 failed=10`, exit 1; installed `total=12 failed=0`, exit 0. Baseline failures carry contract and forbidden-access evidence, not just missing marker strings. Safe ordinary/scratch controls pass both. |
| S038 source locator correction | ADMIT correction, no historical rewrite | same `python3 census/round-14/check-timeout-anchor.py <row>` command: S034 `anchor=mismatch`, exit 1; S038 `anchor=match`, exit 0, at 48f8945. |
| Historical execution proof / authenticated authors / complete dependencies | REJECT | digest eligibility checks declarations; omitted dependencies, external runtimes/environment and fabricated provenance remain outside its proof. |
| Universal race-free no-credential-access or deletion certification | REJECT | finite synthetic fixtures, namespace and filesystem-alias limitations; certification stays OFF. |
| K5 re-admission / Q15 revival | REJECT / retain HELD | no admitted cross-device fixture or lesson-grounded exception; Q4/Q16 remain unchanged. |

C2 preservation observations at 552cae4: the actual legacy census
`--selftest` has 38 checks / zero failures, including linked worktree
dirty/absent flags, identical comparison exit 0 and changed comparison exit
3. `shellcheck -S warning tools/souji-census.sh` exits 0. Both canonical
tool/fixture maps and historical r13 JSON remain unchanged during each run.
No live census or real credential-store probe occurred.

Explicit C2 restrictions: repositories with include/includeIf, local filters,
hooksPath, attributes/excludes configuration, alternateRefsCommand, promisor/
partial clone or worktreeConfig refuse as unsupported. This is not a claim
of unchanged support for every Git configuration. Hardlinked object files,
work-tree content symlinks, bind/mount replacement and symlink-relocated
stores are not universally authenticated by the namespace fence. The
observed no-harm claim is bounded to the preserved ordinary/linked/comparison
controls; these restrictions are exposed to the independent closure, not
silently described as universal operability.

Inventory commands `python3 census/round-14/count-claims.py a31642d` and
the same command on `552cae4` (full output `counts.json`): gate/fixtures
0→1, sources 37→40, A/B/C 33/3/1→36/3/1, mined/queued/rejected
20/15/2→23/15/2, admitted knowledge 5→5 and HELD 1→1. Added tiers:
three A, no B/C. No original source row has an in-place status/recheck/used-by
change. Two demonstrated capabilities enter SCORECARD; source-row growth
alone is not knowledge growth.

Author verdicts: calibration improved, operability improved within declared
cases, coverage/depth/freshness/adjacency unchanged; numeric delta 0 throughout.
Expansion improved by demonstrated repertoire acquisition, quality unchanged
under the existing-admitted-knowledge recheck bar, discernment improved because
the prior outside retention/citation findings become grounded Q20/Q21 and
discriminating evidence. Fresh outside admit/reject sampling remains the
non-author closure duty; no lane-dispatched seat is counted as outside.

### Process deviations and advisory disagreements

SafetyCredential and BoundaryAttack ran synthetic bash/git/strace probes
mid-flight, and SafetyCache ran a synthetic kernel symlink-open probe,
despite the wave prohibition. Their reports preserve the observations and
explicit process-deviation notes; L1 did not rerun those probes to confirm
them or use them as acceptance. The final committed fixtures are separate
L1 acceptance. All three report no real store or operator-sweep access.
Other syntax/source inspections are not runtime acceptance.

Early reviewer reports that files were absent describe concurrent design
review, not dead authors. Proposed counts of 17 cases were unexercised
design suggestions; actual final counts above supersede them. Connector
claims of statistical independence or 100% legacy preservation are not
admitted: causal separability and bounded measured controls do not prove
either assertion. VerdictAttack's output-overwrite concern was fixed by
explicit round/output plus exclusive creation, and its root-binding concern
was fixed before the measured run. No tool was installed or upgraded.

## Required source census before and after

Command, both times:
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`.
Start at a31642d, exit 0 (`census/round-14/before.json`):

```text
souji	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
souji	W04	S036 duplicate url git-scm.com/docs/git across scopes
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
```

End at `42d0b7b177b05889589009d94314cb3d7231ac25`, exit 0
(`census/round-14/end-sources.json`, source bytes SHA-256
`312a028ab7077fa04445d22d605c822ac187477561017da4da5edc7a2d49ba8d`):

```text
souji	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
souji	W04	S036 duplicate url git-scm.com/docs/git across scopes
souji	W04	S038 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
```

W04 is advisory for retained append-only correction rows, not a failed
required exit condition; no stdout notice is hidden. No frontier
coverage-map ground advanced this round; repertoire acquisition, sourced
local calibration and credential-boundary operability are the measured moves.
