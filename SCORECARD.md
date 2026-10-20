# souji-shokunin — SCORECARD

Axes (fleet `AXES.md`): the lane owns **calibration, operability,
coverage**. Following the kotodama precedent, rows carry per-axis verdicts
and checkable observations plus a 0–10 score only where a reproducible
mapping from evidence to number exists. Every observation carries its
counting command and the commit it was measured against.

## Axes

| axis | score | verdict / observation | counting command | measured commit | last change |
|---|---|---|---|---|---|
| coverage | 8 | unchanged r14; r13 C3 improved and admitted by CloseSoujiR13 (`corpus/lessons/round-13-verifier-spotcheck.md`); numeric delta 0, legacy-unmapped. Admitted knowledge remains 5, HELD 1; no new coverage-map ground claimed | `python3 census/round-14/count-claims.py a31642d`; same command `552cae4`; `census/round-14/counts.json` | a31642d → 552cae4 | r13 |
| calibration | 7 | r16 C2 (author: improved, outside admission pending): `tools/souji-landing-gate.py` detects all three r15 closure-found landing defect classes on the historical r15 landing (5 findings) with 0 findings on the r13 and r14 landings; selftest 18/18, held-out fixture 15/15. r15 C2 checker executed for the first time and repaired (selftest 24/47 → 47/47; frozen record regenerated from real runs, `--frozen` clean at c6207bd). Numeric delta 0, legacy-unmapped | `python3 tools/souji-landing-gate.py --root . --rev b410186 --round 15` (exit 1) and `--rev a31642d --round 13` / `--rev cc21683 --round 14` (exit 0); `python3 tests/fixtures/r16-landing-gate.py`; `python3 tools/souji-preservation-evidence.py --selftest`; `corpus/lessons/round-16.md` | a6ec781 (gate); c6207bd (checker, frozen) | r16 |
| operability | 8 | r16 C1 (author: improved, outside admission pending): census parses again and its config guard is value/effect-aware — changed 20/20 on the r16 config fixture, 12/12 namespace, 38/38 selftest, parse/ShellCheck clean; r14-harm fails all 15 HARM_CASES ids; r15 baseline does not parse. Live fleet paired rows identical (21 repos). Residual contractions vs pre-harm a31642d disclosed and routed to the operator. Correction: the r15 row's "numeric delta 0" was wrong — r15 harmed operability (b410186 does not parse). Numeric delta 0, legacy-unmapped | `python3 census/round-16/run-matrix.py --changed <rev> --output <new.json>`; `census/round-16/c1-matrix-final.json`, `c1-matrix-landing.json`, `live-fleet-final.json` | 0a70bef (census bytes 64a60fd0…; unchanged at landing) | r16 |

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
| protected-namespace census, value/effect-aware config (r16) | refuse only config-named paths overlapping a protected root (whole run, exit 2); degrade unevaluable config to one `error` row; skip status where a filter driver is bound; neutralize hooks/fsmonitor and lazy fetch on every git call; honor boundary-clean excludes/attributes; keep the r14 namespace refusals. Not a no-harm claim against pre-harm: residual contractions are listed in `corpus/lessons/round-16.md` | `census/round-16/c1-matrix-final.json`; S045–S047, S049; outside admission pending | r16 (r14 bounded demonstration, not net-admitted) |
| landing-claim gate | flag, at a named revision, registry-cited scripts that do not parse, frozen pins or measured commits that disagree with committed bytes, and contract STATUS failure lines not carried into the round lesson; never executes repository code | `python3 tools/souji-landing-gate.py --selftest` 18/18; `python3 tests/fixtures/r16-landing-gate.py` 15/15; replays in `corpus/lessons/round-16.md` Gate; S043, S050 | r16 |
| seat transcript audit | classify every recorded seat tool call against the wave contract (forbidden-surface paths, live census, out-of-scope writes, unauthorized execution, recursive reads); lower bound only | `python3 tools/souji-seat-audit.py --selftest` 20/20; `census/round-16/seat-audit-w1.json` | r16 |

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
