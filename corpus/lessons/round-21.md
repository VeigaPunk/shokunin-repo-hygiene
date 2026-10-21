# Round 21 — reason privacy and independently replayable evidence

Author: SoujiR21. Original claim base `6ff3413bba9c8430c3b0bc4d2052e21d0407183f`; preregistration landed `544c8358039a07e8b45e6db72312da5c8d965275`. R20 **admitted**, CloseSouji20, MANIFEST rounds[402]; exact closure copied without modification into `census/round-21/r20-closure-excerpt.json` (landed `b2a11849da60479717fd4da6ee95809e2aaa1cb5`). No lane r20 verifier lesson exists because that closure was read-only. This lesson applies its routed defects, not an invented spot-check file.

## Claims

- C1 calibration (lowest axis 7): classify implicit fleet-root-namespace reads as minor V-READ-ROOT; frozen rules and harm guards in `.ufo/waves/round-21/preregistration.txt`, clarified in `clarification-before-measurement.txt`. Classifier/32-case fixture/counter landed `f2248c026bcce5f3a919fa6ac57cd8d9ca18cffa`. Initial same-fixture baseline18/32 versus changed32/32 (14 base-discriminating), `census/round-21/read-fixture-{before,after}.txt`. Truncated calls are unknown, never certified clean.
- C2 operability: isolated committed-tree replay from a non-lane source, independent of source HEAD. Runner + relocatable r16/r18 fixtures landed `8513d6ac97076f34ff94a3fc1979c13e69c2d19a`; first lane-as-source run18/18 at that revision, `census/round-21/acceptance-c2-first.json`. The baseline three-scenario matrix replays0/3, `census/round-21/replay-before.txt`. S102 grounds transport semantics, not an automatic security sandbox.
- C3 coverage of arbitrary-input output sinks: cmd-only1/2 → cmd+reason2/2, not a count of every text field or an axis score rubric. Repair/canary landed `4d5bf78432de7f4afe38e6bf195fd7843bdcb7e3`. Exact original function-body baseline emits19 canary values and two oversized fields; the same27-case oracle is6/27 baseline versus27/27 changed, leaks19→0, max reason454→160 bytes (`census/round-21/reason-oracle-before.txt`, `reason-after.txt`). Eight fabricated cmd probes have byte-equal old/new outputs (`cmd-compatibility.json`). Sources S100/S101.

Each claim's files are disjoint. C2 landed first with the old auditor/proc tool and demonstrated18/18 without C1 or C3; C1's oracle runs without the runner or proc tool; C3's oracle runs without the runner or auditor. Final integrated measurements are appended below after falsification. No score increase is inferred from these counts: the inherited numeric scores remain legacy-unmapped.

## Mistakes

| id | class | evidence | captured-by | fix / shown able to fail |
|---|---|---|---|---|
| R21-M1 | scope | r20 closure: implicit root-namespace reads by 5+ seats; `.ufo/waves/round-21/w1/RevQualityQ45Q46.md` | Q45 covered exact roots, not relative/implicit targets | Q47 + new minor class; same32-case oracle fails14 cases on baseline, passes32/32 changed. Committed real-transcript oracle coverage is separately bounded below. |
| R21-M2 | reference-drift | r20 closure: runner refuses other roots and requires lane HEAD==measured revision | Q37/Q40 did not require external replay | Q48 + clone-at-revision runner. Before three-scenario matrix0/3; exact refusals retained, not suppressed. |
| R21-M3 | scope | r20 closure F5 ruling; `.ufo/waves/round-21/w1/RevClosureF5Lines.md` | Q46 named defect but did not repair it | Q49 shared parser/formatter + synthetic canary; baseline19 leaked fabricated values and two oversized reasons are red controls. No live /proc, credentials or private TSV inspection. |
| R21-M4 | attribution | CloseSouji20: report 'operator explicitly upheld' overstates lesson 'Parent Main confirmed operator/Kagi ownership' | none; now Q50 | Original r20 report remains immutable; that claim is withdrawn here. Ownership/routing acknowledgment is not approval. The quoted mismatch itself fails Q50; no new approval is asserted. |
| R21-M5 | scope | This L1's initial command listed lane/census root names (including the already-known operator-owned directory name), before enforcing named-file seat scope | Q45 | Disclosed coordinator deviation, not a clean round. No operator-sweep contents were opened/copied/staged. Initial discovery listing is void as evidence; all claims derive from named committed files and synthetic fixtures. Seats receive absolute named-path restrictions in both wave contexts. |
| R21-M6 | reference-drift | static call graph: old verify-agreement-pin --check compares an immutable historical tool digest to the upgraded current tool | Q40/Q41 | New runner stages exact original tool/counter bytes at recorded commits, verifies original digests, then calls the unchanged checker. Historical records/runner/checker stay byte-identical; this is not new process agreement. Pre-measurement clarification retained. |
| R21-M7 | provider | wave1 startup: Haiku429 retry-after-ms~10652000, Codex capacity (five retries), later Zai429 type1302 | host routing; no lane repair authority | Dead seats remain dead, no replacements. L1 performs reachable implementation/source work; exact seat outcomes retained. Partial oracle coverage is not claimed as independently complete. |

## Gate

### Opened source decisions (2026-10-21)

All four sources below were opened by L1 through the reader this round after the source scribe seats died; no claim that those seats opened them. Four identified/screened, three mined, one retained rejection; all tier A within their stated scopes. Registry99→103. No existing status/recheck/used-by cell changed (old→new none). No new knowledge pathname: seven admitted-marked paths remain seven; this deepens the existing F5 entry.

- **S100 mined:** https://cwe.mitre.org/data/definitions/532.html — accessed2026-10-21; CWE4.20, page last updated2026-04-30, Potential Mitigations (Architecture and Design; Implementation): “Do not write secrets into the log files.” (9 words). Supports output-sink review, not a confirmed live privacy incident.
- **S101 mined:** https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html — accessed2026-10-21; unversioned live page, Event collection: “Perform sanitization on all event data to prevent log injection attacks” (12 words). Data to exclude separately lists access tokens, authentication passwords and file paths (special treatment); control sanitation alone is not masking.
- **S102 mined:** https://git-scm.com/docs/git-clone — accessed2026-10-21; documentation last updated2.54.0, unchanged through2.56.0; OPTIONS local/no-local: “Specifying --no-local will override the default when /path/to/repo is given, using the regular Git transport instead.” (19 words). The runner also uses no-checkout and a private detached checkout; source worktree state is not measured.
- **S103 rejected for the attempted scope:** https://reproducible-builds.org/docs/definition/ — accessed2026-10-21; Explanations/Artifacts: “They would not usually include build logs or similar ancillary outputs.” (12 words). Equal18-step outcomes are not a bit-identical reproducible-build proof. Flip: declare actual build artifacts/environment and compare their bytes. The source itself is authoritative; the proposed inference is rejected.

Outside spot-check on this round's admit and reject is **pending**, not provided by our dispatched seats. S103 is the explicit reject available to that reviewer.

### Boundaries and teaching

- F5 reason repair was routed for synthetic-only work by CloseSouji20 and this round's assignment. Historical exposure remains unmeasured and under operator/Kagi ownership; no inspection of old private census data is implied.
- Existing r18 live-proc selftest and fixture were **not run**. Their ordinary path expectations are reviewed statically; synthetic reason tests do not certify the whole process scanner.
- Certification OFF; K5 HELD; inherited reap and NAMESPACE pin requests remain held. No signals, cleanup or history rewrite authorized.
- Sibling overlap: `.ufo/waves/round-21/w1/ConnSiblingOverlap.md`, ScoutKagiRedaction.md and ScoutTameshiFixture.md. Souji owns its own output/acceptance gates; credential handling stays Kagi, reusable fixture method Tameshi, host/fleet health Mori. No sibling code was changed.
- No tools installed or upgraded.

## Seat-reported failures

Only completed seat reports with genuine STATUS paragraphs are carried here after the final wave; provider-dead seats have no report and are counted in the outcome registry, not silently omitted. Final dispositions are appended below.

## First-wave falsifier dispositions (before final replay)

- RevPreregC2 reported: “STATUS: PARTIAL — C2 is falsifiable in principle, but its before/after measurement is not yet an independent, reproducible oracle: the scenario driver, compared result projection, and source/output boundary are not pinned sufficiently to determine one outcome from the frozen text.”
  Fixed actual source-output defect in `ff425ab835614f38205426330b9cdb93fd267045`:
  output must be canonical, absolute and outside SRC. New8-case boundary
  oracle old4/8→8/8 (`replay-boundaries-before.txt`, `replay-boundaries.txt`).
  The first C2-only receipt requested its output inside the lane source;
  its `source_unchanged` covered HEAD/tracked status only, not all filesystem
  writes. It is retained as an earlier measurement, NOT evidence for the
  final outside-SRC output guarantee. Final matrix outputs are external.
  No broad source inventory is run (it would violate the protected untracked
  subtree boundary). Source state comparisons mean HEAD/tracked status/refs,
  not ignored/untracked files or whole-filesystem immutability.
  `step-inventory.json` pins the ordered18 commands and all expected fields
  from the r20 runner at5ff7565 (source SHA2566d38a3d0590e9c44480ae19e3abaa8669d7399737397297fd1e0fde363699a10).
  Projection normalizes only Python/root/baseline/revision; the historical
  agreement-root substitution is explicitly documented. Relative-output,
  source/.git and symlink-ancestor refusals were shown able to fail before
  repair. No-result means no JSON file; stderr refusal diagnostics remain.
- RevengeReasonOmission reported: “STATUS: PARTIAL — The source-level reconstruction below is complete, but I made one scope error: an early pinned `git grep` included `census/round-18` alongside the named source paths, and its output included committed census snapshot/TSV rows. I do not use, cite, or reproduce any of those rows. This was not a live `/proc` scan or fixture run; the search nonetheless violated the historical-snapshot prohibition.”
  Scope violation is disclosed, not retroactively authorized. That search
  output is excluded from all findings/evidence, never exported into this
  round's transcripts. L1 notified Main. The report's named-code-only
  reconstruction is advisory; C3's evidence is the synthetic canary, not
  historical process data. This means the round is NOT process-scope-clean.
- ScoutRunnerStepsA's r20 wrapper refusal is repaired by the r21 private
  clone, root-derived fixtures and final matrix. Static dormant literals in
  transitive modules are outside the direct-program literal preflight;
  no claim of a complete transitive path-independence proof.
- ScoutAuditExistingCases F1 is resolved by the pre-measurement historical
  `grep(pattern in PATH)` clarification (visible absolute path); no
  existing selftest want list changed. Its F2 is covered by32 new literal
  synthetic cases,14 discriminating from baseline.
- ScoutProcSelftestExpect confirms statically that all inherited ordinary
  reason expectations stay below160 bytes (maximum91) and contain no
  inherited secret patterns. Classification is per selected argv element,
  not the whole cmdline, so an unrelated secret does not redact its path.
  This is static compatibility evidence, not a run of the live-proc suite.
- RevSourcesTail proposes tool paths in used-by. Contract v1 defines
  used-by as knowledge/lesson paths, so those rows are not changed to tool
  paths. The helper's citations may include S089/S092/S093/S099; historical
  lesson wording is not silently rewritten. No source-cell changes.

## Integrated measurements before second-wave attacks

At final code `ff425ab835614f38205426330b9cdb93fd267045`, the three-source
matrix replays3/3 (each18/18, identical projected signatures), source
HEAD/status/refs unchanged; `census/round-21/replay-final.txt` and
`final-out-S{1,2,3}.json`, `final-matrix.json`. This supersedes the earlier
4b826a5 matrix as final code evidence without rewriting its receipts.
The32-case read oracle and27-case reason oracle remain independent of the
runner and each other; old class totals in the128-transcript census are
identical, with only2 new V-READ-ROOT rows. Full independent per-call oracle
accounting is reported after the second wave, not assumed from provider-dead
label seats.
