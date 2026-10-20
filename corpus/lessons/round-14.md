# Round 14 — retained evidence and credential-store census boundaries

Declared claims: C1 calibration (lowest non-retired axis), digest-bound eligibility of retained green observations; C2 operability, pre-access protected-path refusal in the metadata census. Baseline `a31642d14006830ec62edf40b0354c3699728c4a`; declarations and exact counting commands: `census/round-14/claims.json`. Scores remain legacy-unmapped 7/8/8, numeric delta 0. No comprehensive deletion recertification is claimed.

## Mistakes

| id | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| R14-M1 | stale-green evidence retention can retain an old success after the measured tool changes | round-13-verifier-spotcheck.md, Routed findings item 3; census/round-13/run-verification.py retention branch | Q6/Q18 bound individual evidence, not retention eligibility | New digest-bound eligibility gate and current-round consumer preserve the original measured revision and refuse stale/legacy inputs; discriminating observations are recorded in census/round-14/verification.json, not inferred from source. |
| R14-M2 | citation-location drift: correct quote assigned incorrect installed-manual line numbers | round-13-verifier-spotcheck.md, Routed findings item 1; SOURCES S034; round-13.md Opened sources S034 | CORPUS quote names its location | S038 supersedes immutable S034; the named erratum below corrects the prior lesson without rewriting it. |
| R14-M3 | arbitrary census input can point at the credential store or an ancestor and reach metadata/content readers | baseline tools/souji-census.sh main/emit_census/emit_compare; round-14 boundary fixture baseline observation in verification.json | Never credentials boundary existed but arbitrary --root/--compare lacked a pre-access enforcement rule | Pre-access lexical/component boundary checks plus isolated synthetic-HOME command-spy cases; real credential store is never probed. |

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
