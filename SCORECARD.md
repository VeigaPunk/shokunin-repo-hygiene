# souji-shokunin — SCORECARD

Axes (fleet `AXES.md`): the lane owns **calibration, operability,
coverage**. Following the kotodama precedent, rows carry per-axis verdicts
and checkable observations plus a 0–10 score only where a reproducible
mapping from evidence to number exists. Every observation carries its
counting command and the commit it was measured against.

## Axes

| axis | score | verdict / observation | counting command | measured commit | last change |
|---|---|---|---|---|---|
| coverage | 8 | r19 C3 (author improved; outside admission pending): F5 gains its first admitted entry `corpus/knowledge/process-residue-observations.md` from S082–S085 (S075/S076 rechecked), with SKILL rule, README Core row and Q36–Q38; admitted 6→7, sources 78→85 (mined 59→66), start and end source censuses exit 0; list-only, no reap authority, 58 orphans still unreaped. Numeric delta 0, legacy-unmapped. r18 C3 (author improved; outside admission pending): 0→3 observed residue classes (cwd/argv/fd), F5 remains frontier and list-only, no knowledge entry or reap authority. Proc fixture 19/0 including literal deleted-suffix negatives, fake credential redaction and no-signal tracing; first 11-case fixture/stub controls remain historical evidence. Final two-window snapshots 66=66 twice, pid sets equal (`census/round-18/proc-agreement-counterfix.json`); initial dated snapshot was 65=65. Counter ancestor exclusion falsely hid the compositor under a GUI-launched parent chain; L1 repaired it and retained the failed pre-fix observation. Numeric delta 0, legacy-unmapped. Prior r17 C3 admitted (jj receipts) | `python3 census/round-13/count-claims.py <rev>` (`census/round-19/counts-start.json`, `census/round-19/counts-end.json`); `bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`; `bash tests/fixtures/r18-proc-census.sh --tool tools/souji-proc-census.sh`; paired proc census / blind counter; `census/round-18/final-verification-4800fd7.json` | 3ab2c81 baseline → 005f3d376e5b421c57c4405be37fb10e7ab49381 end; admitted 6→7, sources 78→85; 4800fd7 tool/fixture; 2d4c7f8 counter fix | r19 |
| calibration | 7 | r19 C1 (author improved; outside admission pending): paragraph-aware carry (unmarked cut at a source physical-line end → LG-SEAT-UNCARRIED; ellipsis exactly at the boundary carries; complete paragraph carries; wrapped lesson bullet joins; strict branch gated --round>=18 so the five pinned replays stay match); 4-case fixture base-discriminating, gate selftest 61→65, invariant probe 0 violations over 1,404 cuts; auditor exact delivery shapes + V-SIGNAL, selftest 66→73, r18 re-audit w1 139→134 major (8 delivery false rows removed, 3 real signal calls surfaced), w2 92→92. Numeric delta 0, legacy-unmapped. r18 C2 (author improved; outside admission pending): final grammar b576341 11 findings →0 at 74f9adb (7 actual bad-name citations repaired, 3 deliberate nonfiles and 1 synthetic placeholder bound to exact reasoned exceptions); old grammar 10→0 retained as history. Landing-gate selftest 33→61; pointer fixture 11/0, r16 fixture 15/0, five historical replay exit/finding-multiset matches. Source rows 63→78 include seven append-only teaches corrections, not 15 knowledge entries. Raw seat audits are nonzero and adjudicated. Numeric delta 0, legacy-unmapped | `python3 tests/fixtures/r19-carry-wrap.py`; `python3 tests/fixtures/r19-seat-audit-shapes.py`; `python3 tools/souji-landing-gate.py --root <lane> --rev <rev> --base b576341 --round 18 --fleet-root <fleet> --json <new>`; `census/round-18/gate-pointers-before-finalgrammar-b576341.json`, `census/round-18/gate-pointers-after-final.json`; lesson Gate | 005f3d376e5b421c57c4405be37fb10e7ab49381 tools; gate 65/0, carry fixture 4/0, audit fixture 5/0, auditor selftest 73/0; b576341 before; 74f9adb489fcf1393bbd479425acf5545ded9908 after | r19 |
| operability | 8 | r19 C2 (author improved; outside admission pending): `tools/souji-rev-pin.py` refuses HEAD/branch/short-id/keep-only/dirty-tree stamps with exit 2 before any record and verifies the tracked measured bytes; wired into the r13/r14 runners and both count-claims consumers; helper 11/0, fixture 13/0 with six base discriminators; the r13 runner refused on the dirty lane and wrote nothing; cache-demo blocked while dirty, clean after the code commit. Numeric delta 0, legacy-unmapped. r18 C1 (author improved; outside admission pending): repository-content reads after enumeration are bounded, including list-phase gitfile reads; interruption no longer disarms the detached timer. Final bounded fixture 12/9 failures at b576341 →12/0 at 4800fd7; r17 hygiene 29/0, r15 config 20/0, unchanged pinned r14 namespace fixture 12/0 retained; census selftest 49→69. Session-kill helper mutants activated with different-PGID/same-SID blocked children leave 2 members under the mutant and 0 under original/restored helpers. Final matrix has no new per-suite residue; inherited orphans are recorded separately. Live pair 1 identical excluding mtime on 21 repositories, pair 2 differs in mado dirty 10→13. R1 J13 fails on b576341; final quarantine 108/0, jj fixture 37/0/0 with baseline identity controls. Limits: discovery/unresponsive filesystems, escaping descendants, D-state survivors and the frozen r14 runner remain explicit, not universal containment. Not no-harm vs a31642d. Numeric delta 0, legacy-unmapped; r17's “22 repos” was 21 repositories + header | `python3 tests/fixtures/r19-rev-pin.py`; `python3 census/round-18/run-matrix.py --changed 4800fd7 --output <new.json>`; `census/round-18/c1-matrix-4800fd7.json`; `census/round-18/final-verification-4800fd7.json` | 005f3d376e5b421c57c4405be37fb10e7ab49381 tools; helper 11/0, fixture 13/0, D5 fixtures r15 20/0 and r17 29/0; 4800fd79488e5f2c11a18117958f104171d85dc8 | r19 |

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
