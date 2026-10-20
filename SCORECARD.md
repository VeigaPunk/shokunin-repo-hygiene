# souji-shokunin — SCORECARD

Axes (fleet `AXES.md`): the lane owns **calibration, operability,
coverage**. Following the kotodama precedent, rows carry per-axis verdicts
and checkable observations plus a 0–10 score only where a reproducible
mapping from evidence to number exists. Every observation carries its
counting command and the commit it was measured against.

## Axes

| axis | score | verdict / observation | counting command | measured commit | last change |
|---|---|---|---|---|---|
| coverage | 8 | r18 C3 (author: improved, outside admission pending): process residue becomes an observed, list-only surface (PROVINCE work surface + F5 frontier, QUALITY Q32, S068/S069): `tools/souji-proc-census.sh` governs 3 residue classes (cwd-deleted, argv-path-gone, fd-path-gone; 0 before — no tool at b576341); fixture `tests/fixtures/r18-proc-census.sh` 11/0 on the tool, a header-only stub (the no-capability state) fails P1/P2; live 65 rows = blind counter `census/round-18/leak-count.py` 65, symmetric pid difference 0 (`census/round-18/proc-census-live-1721.tsv`). No knowledge entry, so F5 stays frontier; residue is listed, not reaped. Numeric delta 0, legacy-unmapped. Prior: r17 C3 (author: improved; admitted by the r17 closure): jj-colocated repositories became a governed edge class (`corpus/knowledge/jj-colocation-receipts.md`, S051–S063); fixture `tests/fixtures/r17-jj-receipts.sh` 5fa6017 tools 33/13 fail → 35/0 at 4f48343 | `bash tests/fixtures/r18-proc-census.sh --tool tools/souji-proc-census.sh`; `bash tools/souji-proc-census.sh` vs `python3 census/round-18/leak-count.py` | 3f822e8 | r18 |
| calibration | 7 | r18 C2 (author: improved, outside admission pending): authority files may cite only evidence that exists at the landing revision — landing gate `LG-DANGLING-PTR` (round ≥ 18) and unresolvable `measured_commit` as `LG-FROZEN-MEASURED` (Q31, S071); at b576341 round 18 the changed gate reports 10 findings: 7 citations of two never-committed records (`gate-replays-ddb7347.json`, `jj-receipts-ddb7347.txt` — 5 of the 7 not routed by the r17 closure), 2 deliberate non-files and 1 synthetic placeholder (now committed exemptions with reasons); after: 0 at the round tip (Gate in `corpus/lessons/round-18.md`); gate selftest 33 → 53 incl. the CLI totality fix (R18-M5), `tests/fixtures/r18-landing-pointers.py` 11/0. Numeric delta 0, legacy-unmapped. Prior: r17 C2 (admitted): `tools/souji-seat-audit.py` severity-exact selftest 20 → 66; r16 w2 majors 3 → 1 on the committed transcripts; precision on fresh transcripts unmeasured | `python3 tools/souji-landing-gate.py --root . --rev <rev> --round 18 --fleet-root <fleet> --json <f>`; `census/round-18/gate-pointers-before-b576341.json` | b576341 (before); round tip (after) | r18 |
| operability | 8 | r18 C1 (author: improved, outside admission pending): no single repository can hang the fleet census — per-repository process-group watchdog (`--repo-timeout`, default 600 s; list-phase guards and `census_one`); r18 bounded fixture b576341 8/5 fail (B1–B4, B8 hang to the deadline) → 8/0; r17-hygiene 29/0, r15-config 20/0, r14-namespace 12/0 kept; selftest 49 → 62 (`census/round-18/c1-matrix-worktree.json`); fixtures kill their whole session on timeout (r15 forced hang 2 → 0 leftover, r17 4 → 0); live fleet pair identical on 21 repositories (`census/round-18/live-fleet-pairs/`). R1: the quarantine recipe names the owning lane (J13 b576341 FAIL → PASS). Not no-harm vs pre-harm a31642d (inherited residuals unchanged). Numeric delta 0, legacy-unmapped. Prior: r17 C1 (admitted): census D1 explicit `--untracked-files=normal`, D2 per-repo degrade of a hardlinked/non-regular `info/attributes`; r17 hygiene 29/14 → 29/0; live fleet paired rows identical on 21 repositories (r18 correction, closure R3: r17 said "22 repos" — 22 rows including the header) | `python3 census/round-18/run-matrix.py --changed <rev> --output <new.json>`; `python3 tests/fixtures/r18-census-bounded.py --census <census>` | worktree integrated at 3f822e8 (census sha256 7e6a92d4…) | r18 |

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
| bounded fleet census (r18) | no single repository can hang the census: each repository (list-phase guards and `census_one`) runs in its own process group under `--repo-timeout`; a post-guard FIFO swap or a static work-tree FIFO yields an `error` row and `repo-timeout` diagnostic while the rest of the fleet is measured | `python3 tests/fixtures/r18-census-bounded.py --census tools/souji-census.sh` 8/0 (b576341: 5 fail); `census/round-18/c1-matrix-worktree.json`; S064–S066, S070 | r18 |
| evidence-pointer gate (r18) | flag authority-file citations of repo paths that do not exist at the landing revision, with fleet-only paths listed apart and committed, reasoned exemptions; non-resolving `measured_commit` flagged | `python3 tools/souji-landing-gate.py --selftest` 53/0; `python3 tests/fixtures/r18-landing-pointers.py --tool tools/souji-landing-gate.py` 11/0; `census/round-18/gate-pointers-before-b576341.json`; S071 | r18 |
| process-residue census (r18) | list own-uid processes left behind with a deleted cwd or a vanished scratch argv/fd path, with an identity binder (starttime, boot_id), redacted argv, never signalling | `bash tests/fixtures/r18-proc-census.sh --tool tools/souji-proc-census.sh` 11/0; live 65 = blind counter 65 (`census/round-18/proc-census-live-1721.tsv`, `census/round-18/leak-count-live-1721.json`); S068, S069 | r18 |

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
