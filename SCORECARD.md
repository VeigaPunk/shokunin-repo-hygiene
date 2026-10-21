# souji-shokunin — SCORECARD

Axes (fleet `AXES.md`): the lane owns **calibration, operability,
coverage**. Following the kotodama precedent, rows carry per-axis verdicts
and checkable observations plus a 0–10 score only where a reproducible
mapping from evidence to number exists. Every observation carries its
counting command and the commit it was measured against.

## Axes

| axis | score | verdict / observation | counting command | measured commit | last change |
|---|---|---|---|---|---|
| coverage | 8 | R19 outside closure verifies C3's narrow F5 observation gain (6→7 admitted-marked entries), but the whole round is rejected-harmed. R20 declares no coverage claim: existing F5 precision is corrected, not new coverage or reap authority. Legacy numeric delta 0; old r18/r19 detail remains in their lessons and LOG. | plain committed-tree method in `corpus/lessons/round-19-verifier-spotcheck.md`; full-ID current inventory command `python3 census/round-13/count-claims.py 12516f7dcdd5b165e5ee208d44a38d63b5bd5812` | outside r19 comparison 3ab2c81479f5004c8bc91946eea482caec45408f → e6df080a60cae997bfcd387738a87aa449c85484; r20 current inventory recheck pending | r20 correction |
| calibration | 7 | R19 outside verdict harmed: unconditional sibling suffix grants contradicted the contract. R20 C1 declared on this lowest axis: exact explicit parsed-write grants and byte-bound audit receipts, plus literal scope/precision repairs. No runtime improvement is pre-claimed; numeric delta remains 0, legacy-unmapped. | `python3 tests/fixtures/r20-audit-contract.py --tool tools/souji-seat-audit.py --base-tool <baseline-extraction>`; portable extraction and exact command in `census/round-20/run-acceptance.py` | baseline 12516f7dcdd5b165e5ee208d44a38d63b5bd5812; changed measurement not yet run | r20 declaration |
| operability | 8 | R19 outside verdict harmed/unproved beyond the narrow guard: copied short-ID commands contracted and complete measured inputs were omitted. R20 C2 declared: complete actual caller input boundary and full-ID consumer cutover, independently testable from C1. No runtime improvement is pre-claimed; numeric delta 0, legacy-unmapped. | `python3 tests/fixtures/r20-input-binding.py --baseline 12516f7dcdd5b165e5ee208d44a38d63b5bd5812`; actual full-ID examples in `corpus/README.md` | baseline 12516f7dcdd5b165e5ee208d44a38d63b5bd5812; changed measurement not yet run | r20 declaration |

The earlier author-improved/pending wording is superseded by the independent
`corpus/lessons/round-19-verifier-spotcheck.md` rejected-harmed verdict.
The two current claims are fixed in `.ufo/waves/round-20/preregistration.txt`;
their expected oracles are not observed passes. Certification OFF, K5 HELD.

Correction (r12 post-review, 2026-10-19): coverage C2 reads 0→4 admitted entries (+1 held,
K5) on F1/F3/F4, SOURCES census mined=16 queued=15; calibration C1's 28/52 → 51/53 is a
rule-coverage count, not calibration proof. Details: `corpus/lessons/round-12.md`
`## Post-review fixes`.

Round-14 provenance clarification: the historical r13
`python3 census/round-13/run-verification.py --retry-failed` command is
reproduced at its named measured revision `6f8ee0f`, not against
the current migrated runner. The installed runner now requires explicit
`--round N --output census/round-N/<new>.json`, refuses its default invocation,
and never overwrites existing historical evidence. Its actual C1 reuse
decisions are exercised by `census/round-14/cache-demonstration.py`; no
historical JSON is rewritten. R13's original bounded results remain as
independently adjudicated in `corpus/lessons/round-13-verifier-spotcheck.md`.

## Capabilities

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| fleet census (receipt taxonomy) | classify every fleet artifact into pushed / moved-to-obsidian / stale / none with per-row command evidence, at 64-seat parallelism, dry-run | `census/round-1/census-summary.json`, `census/round-1/census.tsv` (246 rows) | r1 |
| souji-verify | per-artifact SAFE/NOT-SAFE verdict from receipts, read-only, secrets-refusal; advisory while certification is OFF | `tools/souji-verify.sh`, current installed digest in `census/round-13/verification.json`; historical evidence `tests/results/INSTALL.json`, `tests/results/parent-harness-live.json` | r2 |
| worktree metadata prune | selective prune with lock-preserve of pinned registrations; receipts re-verified at act time | `census/round-3/seat-61.json` (plan), `census/round-3/seat-62.json` (lore assertions), LOG r3 | r3 |
| ledger-verify (moved-to-obsidian receipt) | verify a ledger row's source + vault sha256 pairs read-only; refuses self-referential rows; --ledger override; Obsidian integration remains operator-waived | `tools/souji-vault-verify.sh`, current installed digest in `census/round-13/verification.json`; historical evidence `tests/results/parent-vault-battery.json`, LOG r4 | r4 |
| sources registry | curate opened, scoped sources and retained rejections; counts re-derived at r13, not copied from stale r12 output | `corpus/SOURCES.md`; `census/round-13/verification.json` source census and histograms; baseline 33 rows, mined=16 queued=15 rejected=2 at 31984f4 | r12 |
| maintenance-guard gate | prove on the host git that a plain commit can prune expired unlocked worktree metadata and that `-c maintenance.auto=false`, `worktree lock` and a fresh index prevent it | `bash tests/fixtures/r12-maintenance-guard.sh --selftest` → 6/6 PASS, exit 0; `tests/results/r12-maintenance-guard.txt` | r12 |
| declared-evidence integrity | reject inconsistent declared artifact/evidence digests, ownership labels, missing files, false success and tampered frozen inputs; not complete certification | `python3 tools/souji-cert-evidence.py --selftest` → 36/36; external fixture 5/5; frozen input pins and actual historical replays in `census/round-13/verification.json` | r13 |
| bounded quarantine operations | bounded move/digest/inspection with explicit refusal/abort and residue diagnostics; stable special-file refusals; no new deletion authority | `bash tests/fixtures/r13-quarantine-bounds.sh` → 5/5; same corrected fixture baseline red, `census/round-13/verification.json` | r13 |
| repository structure census | emit versioned refs-rooted object metrics on the bounded complete-repository surface; reject marked partial/promisor repos; report common-store identity | `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` → 5/5; `corpus/knowledge/git-repo-structure-readonly.md` (S035/S036/S037) | r13 |
| declared-dependency cache eligibility | refuse stale/legacy/malformed declared records and preserve original revision; actual attempt_reuse decision honors refusal on synthetic records only; no historical execution proof, full dispatch or positive production retention | `census/round-14/verification*.json`; S039; bounded outside verification `corpus/lessons/round-14-verifier-spotcheck.md` C1 | r14 |
| protected-namespace census, value/effect-aware config (r16) | config: refuse the whole run (exit 2) only for config-named paths overlapping a protected root; degrade unevaluable config to one `error` row; skip status where a filter driver is bound; neutralize hooks/fsmonitor and lazy fetch on every git call; honor boundary-clean excludes/attributes. Kept r14 git-metadata guards (symlinked/hardlinked metadata, alternates) and the new `info/attributes` guard also exit 2 for the whole run. Not a no-harm claim against pre-harm: residual contractions are listed in `corpus/lessons/round-16.md` | `census/round-16/c1-matrix-final.json`; S045–S047, S049; outside admission pending | r16 (r14 bounded demonstration, not net-admitted) |
| landing-claim gate | flag, at a named revision, registry-cited scripts that do not parse, frozen pins or measured commits that disagree with committed bytes, and contract STATUS failure lines not carried into the round lesson; never executes repository code | `python3 tools/souji-landing-gate.py --selftest` 18/18; `python3 tests/fixtures/r16-landing-gate.py` 15/15; replays in `corpus/lessons/round-16.md` Gate; S043, S050 | r16 |
| seat transcript audit | classify every recorded seat tool call against the wave contract (forbidden-surface paths, live census, out-of-scope writes, unauthorized execution, recursive reads); neither complete (no probe class, truncated arguments) nor precise (4 of 20 wave-1 rows were not violations) | `python3 tools/souji-seat-audit.py --selftest` 20/20; `census/round-16/seat-audit-w1.json`, `seat-audit-w2.json` | r16 |
| census untracked/attributes hygiene (r17) | dirty counts immune to repo-local/included/config.worktree `status.showUntrackedFiles`; a hardlinked or non-regular `info/attributes` degrades only its repository; empty metadata files and non-C message locales stay accepted | `python3 tests/fixtures/r17-census-hygiene.py --census tools/souji-census.sh` 29/0; `census/round-17/c1-matrix-4f48343.json` | r17 |
| jj-aware receipts (r17) | treat `refs/jj/*` as non-durable roots and refuse a keep-only commit that introduces novel content at the target, with byte-identical output on plain repositories | `bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` 35/0 (5fa6017 tools: 13 fail); `census/round-17/jj-receipts-*.txt`; S054, S060 | r17 |
| reproducible seat audit (r17) | replay the auditor over committed, digest-checked transcripts into one record binding auditor, specs and manifest; severity-exact classes incl. `V-WRITE-RELATIVE` | `python3 census/round-17/seat-audit-replay.py …`; `census/round-17/transcript-manifest.py --check census/round-16/transcripts` | r17 |
| bounded repository-content census (r18) | after discovery, bound FIFO/special-reader stalls in preflight and measurement; preserve neighbour rows and disclose unmeasured/surviving groups, including interruption handling; no filesystem/PID sandbox guarantee | `census/round-18/c1-matrix-4800fd7.json` (12/9 failed →12/0); census selftest 69/0; S064, S072–S075, S077 | r18 |
| evidence-pointer gate (r18) | flag missing authority-file citations within the declared grammar, exact synthetic exemptions, fleet collisions, and dangling measured commits; keep total CLI early-error behavior | `census/round-18/final-verification-4800fd7.json` (selftest 61/0, pointer fixture 11/0, r16 fixture 15/0); S078 | r18 |
| process-residue observations (r18) | list own-uid cwd/argv/fd residue with redacted argv and identity metadata, never signalling inherited processes; literal live deleted-suffix names distinguished by inode | proc fixture 19/0; two 66=66 pid-identical pairs in `census/round-18/proc-agreement-counterfix.json`; S075, S076 | r18 |
| paragraph-aware carry gate (r19) | flag an unmarked cut at a source physical-line end and accept boundary-marked, complete and wrapped-bullet carries; strict branch keeps five pinned replay verdicts | `tests/fixtures/r19-carry-wrap.py` 4/0 base-discriminating; `census/round-19/c1-carry.txt` | r19 |
| durable revision stamps (r19) | refuse HEAD/branch/short/keep-only/dirty-tree revisions before a record and verify tracked measured bytes | `tools/souji-rev-pin.py --selftest` 11/0; `tests/fixtures/r19-rev-pin.py` 13/0 | r19 |
| seat-audit delivery and signal classes (r19) | allow exact sibling delivery artifacts, major a signal-shaped call, keep tools/ writes major | `tools/souji-seat-audit.py --selftest` 73/0; `tests/fixtures/r19-seat-audit-shapes.py` 5/0 | r19 |
| agreement digest pin (r19) | emit and check a record pinning tool, counter and r18 agreement digests without editing the r18 records | `census/round-19/verify-agreement-pin.py --selftest` 5/0; `--check` exit 0 | r19 |

## Planned

- **r4 — AMENDED by operator mid-round:** the Obsidian-CLI integration
  claim was withdrawn ("forget the obsidian integration for now"); closed
  instead on the standalone ledger-verify capability
  (`tools/souji-vault-verify.sh`, installed r4). Finding: no usable CLI
  entry point on this host — banked in
  `.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md` for the operator.
  Completion-criterion obsidian-row requirement waived by the operator.
- **r5 (verification round, all axes):** audit rounds 1–4 verdicts and
  outputs for correctness and missed items, folded into the round's own
  claims (scheduled model: gpt-6-luna-max). Carry-overs: the 96-row
  approval list awaits operator sign-off; the 3 pinned gd2d registrations
  await that lane's push; `/tmp` fixture residue routed to
  tsukuroi/operator.
- **r6–r11 (appended r12):** this section was not updated for rounds 6–11
  (STATE dossier §5.4; lesson row M52). Their claims and verdicts are in
  LOG.md and `corpus/lessons/round-{6..11}.md`.
- **r16 (planned r15) — done, see `corpus/lessons/round-16.md`:** census
  repaired and measured (C1), landing gate (C2), r15 checker executed and
  frozen record regenerated (R4), seat audit (R5).
- **r17 (planned r16):** first act on the outside r16 closure. Then either
  (a) operability: narrow the residual r14 contractions that need no
  operator ruling (git-metadata symlinks resolving inside the gitdir,
  hardlink/alternates refusals → per-repo degrade, `~user` expansion), each
  with a pre-harm/changed pair, or (b) coverage/frontier: F2 size
  attribution. Certification stays OFF, K5 HELD.
- **r17 (planned r16) — done, see `corpus/lessons/round-17.md`:** C1 census D1/D2, C2 seat-audit precision + committed transcripts, C3 jj-colocated receipts (operator jj directive replaced option (b) F2 size attribution).
- **r18 (planned r17):** the routed r16/r17 residuals in `corpus/lessons/round-17.md` Residuals (census TOCTOU timeout on status/check-attr, `:(optional)` core.worktree, nested-layout pathspec excludes, carry-gate wrap truncation, HEAD-pinned consumers r13/r14); a keep-ref lifetime measurement if the operator rules on `jj util gc`. Certification stays OFF, K5 HELD.
- **r18 (planned r17) — done, see `corpus/lessons/round-18.md`:** C1 bounded census (the TOCTOU item, widened to every per-repo open and the list phase) + fixture session kill, C2 evidence-pointer gate, C3 process-residue census; routed R1–R4. `:(optional)` core.worktree, nested-layout pathspec excludes, carry-gate wrap truncation and the HEAD-pinned r13/r14 runners stay open.
- **r19 (planned r18):** (a) calibration: carry-gate wrap truncation (rule drafted in `.ufo/waves/round-18/w1/ScoutCarryWrap.md`) and the seat-audit r18 contract shapes (patch delivery, clone writes) measured on the committed round-18 transcripts — fresh-transcript precision; (b) coverage: an F5 knowledge entry and, if the operator rules, an approved reap protocol for the listed fixture orphans; (c) operability: HEAD-pinned r13/r14 runners refuse `HEAD`. Certification stays OFF, K5 HELD.
- **r19 (planned r18) — done, see `corpus/lessons/round-19.md`:** C1 carry/audit truthfulness, C2 durable revision stamps, C3 F5 entry; D2 and D5 repaired; D1/D3 receipts and labels. `census/round-19/final-verification-63bb887.json` is the 18-command acceptance record (all matched). Certification stays OFF, K5 HELD.
- **r20 (planned r19):** (a) calibration: adjudicate every wave-2 attack and route any surviving carry/audit defect; (b) operability: disclose the D5 recheck's residual pid-recycle window and re-check the historical r13/r14 replay commands under the helper; (c) coverage: the operator ruling on F5 reap and the r14 NAMESPACE pin remains outstanding; F2 size attribution unchanged.

## Saturation / stagnation

Saturation line: 8 per axis; stagnation window 3 rounds. Scores per the
rows above: coverage 8, operability 8, calibration 7 (this prose formerly
said 6/7 — corrected r9 after the judges caught the drift).

## Tool certification (r9)

The verdict tools are PATCHED (r9 S17: 40/51/91 selftest checks) but NOT
certified for deletion authorization: r9 red-team replays still reproduce
unsafe deletions (>=16 open defect classes; see corpus/lessons/round-9.md).
Receipts are advisory until the r10 hardening closes the classes.

Correction (r13): r10 and r11 ran; r11's certification evidence was
compromised (shared relay, verdicts on non-installed bytes). The historical
`census/round-10/cert-16.json` still carries a candidate CERTIFIED claim;
the appended r13 lesson and LOG explicitly supersede its authority for
installed tools without rewriting those bytes. The r13 integrity gate
checks declared evidence only. It cannot prove author identity, command
execution, or full defect-class coverage. Deletion authorization stays OFF.

Round-14 outside disposition: **rejected-harmed**, not a net operability
improvement (`corpus/lessons/round-14-verifier-spotcheck.md`). Namespace gains
and bounded C1 eligibility verify, but benign-config support contracted.
The r15 first claim attempts that routed repair, but operator wrap-up
stopped integration before acceptance. R14 harm is not discharged by source
changes alone. Certification stays OFF, K5 HELD, and unexercised r13 sites
unproved. Source-row growth is not knowledge growth.

## Retired

None.
