# souji-shokunin — SCORECARD

Axes (fleet `/home/vgpnk/Projects/shokunin/AXES.md`): the lane owns **calibration, operability,
coverage**. Following the kotodama precedent, rows carry per-axis verdicts
and checkable observations plus a 0–10 score only where a reproducible
mapping from evidence to number exists. Every observation carries its
counting command and the commit it was measured against.

## Axes

| axis | score | verdict / observation | counting command | measured commit | last change |
|---|---|---|---|---|---|
| coverage | 8 | R21 admitted bounded sink repair: cmd+reason2/2, same27-case oracle6/27→27/27, fabricated leaks19→0/max454→160. R22 preserves exact F5 source/160-byte synthetic-only scope; historical exposure remains unmeasured. Numeric delta0, legacy-unmapped. | Historical `bash tests/fixtures/r21-reason-canary.sh --tool tools/souji-proc-census.sh --base <6ff3413-proc-file>`; r21 reason-before/after receipts; S100/S101 | repair4d5bf78432de7f4afe38e6bf195fd7843bdcb7e3; CloseSouji21 admitted MANIFEST rounds[408] | r21 admitted; r22 no expansion claimed |
| calibration | 7 | R22 **attempt 2** C1 declared-evidence calibration (new instrument, bounded; **record accuracy, not a scored axis move**): SCORECARD assertions are re-derived at a named revision by one instrument pinned in `census/round-22/attempt2/instrument-digests.txt`. Same instrument, both ends: base 4edb25dfe262515d0da63224bbba71e02e36cba5 `assertions=55 resolved=52 skipped=33 mismatches=3`; tip 9301d98c1c689c79741f0f1ba1f171138d20af07 `assertions=63 resolved=63 skipped=40 mismatches=0` (a wider span-inclusive reading of class B scores 67/67/40/0, also 0, per the residual seat). The token set moved with the file (55→63); the multiset delta is instrument-dependent and is not claimed. 2 of 3 repairs address a real path (`census/round-21/reason-after.txt`); the fleet AXES.md repair names an absolute host path and leaves class A rather than resolving inside it; the absent operator scope file is now recorded as absent. Enum limits, named: command-embedded paths skipped, class C structurally empty on this file, skips not itemised, class B proves existence not measurement. Attempt 1's strict-adequacy claim stays rejected-honest-stop, not re-claimed. Critics on record: CritC1Predicate (enum gaps) and CritC1Axis (**bookkeeping-only**, V=0). Score 7 unchanged. | `python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md --rev 9301d98c1c689c79741f0f1ba1f171138d20af07 --format counts` → `assertions=63 resolved=63 skipped=40 mismatches=0`, exit 0, now bound by the receipt `census/round-23/records/declared-evidence-after.tsv` (tool_sha256 65817d0d…, rev 9301d98c…); `--selftest` 8/8 incl. the always-zero control rejected; before receipt `census/round-22/attempt2/declared-evidence-before-final.tsv` at `4edb25dfe262515d0da63224bbba71e02e36cba5` (same pinned instrument, `assertions=55 resolved=52 skipped=33 mismatches=3`; the earlier `census/round-22/attempt2/declared-evidence-before.tsv` is the pre-hardening instrument's 56/53 reading, kept as history) | measured at 4edb25dfe262515d0da63224bbba71e02e36cba5 (before, receipt `census/round-22/attempt2/declared-evidence-before-final.tsv`) and at 9301d98c1c689c79741f0f1ba1f171138d20af07 (after, receipt `census/round-23/records/declared-evidence-after.tsv`) | r22 attempt 2; after-state bound r23 |
| operability | 8 | R21 admitted clone-isolated replay: three source shapes3/3, each18/18 original predicates; remote-ref-only/unborn HEAD18/18; jj-only refused. R22 strengthens result comparisons, not source transport or whole-source integrity. Numeric delta0, legacy-unmapped. | Historical matrix command requires the runner extracted from195715439a08165ed7319ee6348844fcfba60029, NOT the current upgraded runner; original command/output in census/round-21/accepted-matrix.json and final-code-verification.json. Current entrypoint: SKILL.md r21-acceptance row. | r21 final195715439a08165ed7319ee6348844fcfba60029; CloseSouji21 admitted MANIFEST rounds[408] | r21 admitted; r22 no separate operability claim |

### Round 23 measurements (2026-10-25, lane base 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 record agreement | calibration 7 | `keys=4 records=3 occurrences=13 mismatches=6` at the base revision, revision-scoped keys (`census/round-23/records/agreement-control-base.txt`); `mismatches=29` with the live-worktree K4 arm (`…-worktree.txt`) | `mismatches=0` at the landing tip (`census/round-23/records/agreement-after.tsv`, `rev=eb1aa49783ae4a0d42e062aa5a61e49a91b0f76a`) with `--no-worktree`; with the live-worktree K4 arm the number is whatever the tree holds at the moment of the run, which is why the claim's evidence uses the revision-scoped arm and the tree arm is reported separately | `python3 -B tools/souji-record-agreement.py --rev <full40> --no-worktree` | tool `tools/souji-record-agreement.py` sha256 `dd53c228b8cca68cfe6dd51630c4ed3473a7c20db36a0effcf5a18259049bb0f`; fixture `tests/fixtures/r23-record-agreement.py` 11/11 with `control=FALSE-GREEN-REJECTED` |
| C2 blob-bound receipts | operability 8 | 0 receipts carrying `tool_sha256=` under `census/` | 5 bound receipts, every one `verify=ok` | `grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ \| wc -l`, then `python3 tools/souji-receipt-run.py verify --root . <receipt>` for each | `census/round-23/records/{declared-evidence-after,gate-check-at-first-landing,gate-check-at-lane-base,gate-check-c3,agreement-after}.tsv`; fixture `tests/fixtures/r23-receipt-run.py` 8/8 |
| C3 F2 read side | coverage 8 | registry 114 rows; F2 held one entry (`git-repo-structure-readonly.md`) | registry 119 rows (S115–S119), F2 holds three entries, gate `entries=2 ok=2 fail=0`, census exit 0 | `sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`; `python3 tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries corpus/knowledge/repo-size-census-readonly.md corpus/knowledge/count-objects-garbage-readings-r25.md --snapshot-dir census/round-23/sources --slice census/round-23/records/empty-slice --slice-verdicts census/round-23/records/empty-verdicts` | snapshots `census/round-23/sources/*` with sha256; entries `corpus/knowledge/repo-size-census-readonly.md`, `corpus/knowledge/count-objects-garbage-readings-r25.md` |

C1's four keys and C2's runner are the round's instruments; both were repaired pre-data in
response to wave-1 attacks (K1's tuple-to-revision binding, K2's filed-occurrence list, K3's
per-record class presence, K4's exact exemption allowlist; the runner's clone-derived digest,
`GIT_NO_REPLACE_OBJECTS`, argv refusal list, redaction and newline-preserving capture). The final
bytes are the ones pinned above; every number in this table was produced by those bytes. The
counter's named limits: K4 is a live-worktree observation, not a revision snapshot; a receipt
binds bytes, not execution; the C3 gate's slice arm is inert this round (no register rows were
quarantined) so its entry arm carries the verdict.

R19's rejected-harmed verdict remains in its immutable verifier lesson.
R22 is a **retry of an already-filed round**: attempt 1 was judged
`rejected-honest-stop` by the non-author spot-check
(`corpus/lessons/round-22-verifier-spotcheck.md`) for an unproven strict
adequacy claim. Attempt 2 does not re-claim it; it lands a bounded
calibration instrument (C1) and one assimilation theme (C2).
R20 is now independently **admitted** (CloseSouji20, MANIFEST rounds[402];
closure excerpt `census/round-21/r20-closure-excerpt.json`), superseding the
old pending wording below. R21 is independently **admitted** (CloseSouji21,
MANIFEST rounds[408]; `census/round-22/r21-closure-excerpt.json`).
Original red receipts/scope violations remain historical evidence; r21
repairs current reason output but not unmeasured historical exposure.
Certification OFF, K5 HELD; inherited reap/NAMESPACE holds unchanged.

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
| souji-verify | per-artifact SAFE/NOT-SAFE verdict from receipts, read-only, secrets-refusal; advisory while certification is OFF | `tools/souji-verify.sh`, r13-era digest (superseded: committed tool bytes at 4edb25dfe262515d0da63224bbba71e02e36cba5 hash differently) in `census/round-13/verification.json`; historical evidence `tests/results/INSTALL.json`, `tests/results/parent-harness-live.json` | r2 |
| worktree metadata prune | selective prune with lock-preserve of pinned registrations; receipts re-verified at act time | `census/round-3/seat-61.json` (plan), `census/round-3/seat-62.json` (lore assertions) measured at d7266c5, LOG r3 | r3 |
| ledger-verify (moved-to-obsidian receipt) | verify a ledger row's source + vault sha256 pairs read-only; refuses self-referential rows; --ledger override; Obsidian integration remains operator-waived | `tools/souji-vault-verify.sh`, r13-era digest (superseded: committed tool bytes at 4edb25dfe262515d0da63224bbba71e02e36cba5 hash differently) in `census/round-13/verification.json`; historical evidence `tests/results/parent-vault-battery.json`, LOG r4 | r4 |
| sources registry | curate opened, scoped sources and retained rejections; counts re-derived at r13, not copied from stale r12 output | `corpus/SOURCES.md`; `census/round-13/verification.json` source census and histograms; baseline 33 rows, mined=16 queued=15 rejected=2 at 31984f473ce4bdab61a99b16cca194b28108cb81 | r12 |
| maintenance-guard gate | prove on the host git that a plain commit can prune expired unlocked worktree metadata and that `-c maintenance.auto=false`, `worktree lock` and a fresh index prevent it | `bash tests/fixtures/r12-maintenance-guard.sh --selftest` → 6/6 PASS, exit 0; `tests/results/r12-maintenance-guard.txt` | r12 |
| declared-evidence integrity | reject inconsistent declared artifact/evidence digests, ownership labels, missing files, false success and tampered frozen inputs; not complete certification | `python3 tools/souji-cert-evidence.py --selftest` → 36/36; external fixture 5/5; frozen input pins and actual historical replays in `census/round-13/verification.json` | r13 |
| bounded quarantine operations | bounded move/digest/inspection with explicit refusal/abort and residue diagnostics; stable special-file refusals; no new deletion authority | `bash tests/fixtures/r13-quarantine-bounds.sh` → 5/5; same corrected fixture baseline red, `census/round-13/verification.json` | r13 |
| repository structure census | emit versioned refs-rooted object metrics on the bounded complete-repository surface; reject marked partial/promisor repos; report common-store identity | `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` → 5/5; `corpus/knowledge/git-repo-structure-readonly.md` (S035/S036/S037) | r13 |
| declared-dependency cache eligibility | refuse stale/legacy/malformed declared records and preserve original revision; actual attempt_reuse decision honors refusal on synthetic records only; no historical execution proof, full dispatch or positive production retention | `census/round-14/verification.json`; S039; bounded outside verification `corpus/lessons/round-14-verifier-spotcheck.md` C1 | r14 |
| protected-namespace census, value/effect-aware config (r16) | config: refuse the whole run (exit 2) only for config-named paths overlapping a protected root; degrade unevaluable config to one `error` row; skip status where a filter driver is bound; neutralize hooks/fsmonitor and lazy fetch on every git call; honor boundary-clean excludes/attributes. Kept r14 git-metadata guards (symlinked/hardlinked metadata, alternates) and the new `info/attributes` guard also exit 2 for the whole run. Not a no-harm claim against pre-harm: residual contractions are listed in `corpus/lessons/round-16.md` | `census/round-16/c1-matrix-final.json`; S045–S047, S049; outside admission pending | r16 (r14 bounded demonstration, not net-admitted) |
| landing-claim gate | flag, at a named revision, registry-cited scripts that do not parse, frozen pins or measured commits that disagree with committed bytes, and contract STATUS failure lines not carried into the round lesson; never executes repository code | `python3 tools/souji-landing-gate.py --selftest` 18/18; `python3 tests/fixtures/r16-landing-gate.py` 15/15; replays in `corpus/lessons/round-16.md` Gate; S043, S050 | r16 |
| seat transcript audit | classify parsed tool calls against explicit wave contracts; visible relative/implicit fleet-root reads supplement absolute-root recursion. Truncated targets and arbitrary Bash writes remain limits | r21 read32/32 (base18/32), renderer4/4; oracle2372 keys over192 files, tp3/fp0/fn0; all401 old tuples identical; `census/round-21/oracle-acceptance.json` | r16; r20 admitted repair; r21 measured extension |
| census untracked/attributes hygiene (r17) | dirty counts immune to repo-local/included/config.worktree `status.showUntrackedFiles`; a hardlinked or non-regular `info/attributes` degrades only its repository; empty metadata files and non-C message locales stay accepted | `python3 tests/fixtures/r17-census-hygiene.py --census tools/souji-census.sh` 29/0; `census/round-17/c1-matrix-4f48343.json` | r17 |
| jj-aware receipts (r17) | treat `refs/jj/*` as non-durable roots and refuse a keep-only commit that introduces novel content at the target, with byte-identical output on plain repositories | `bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` 35/0 (5fa6017 tools: 13 fail); `census/round-17/jj-receipts-*.txt`; S054, S060 | r17 |
| reproducible seat audit (r17) | replay the auditor over committed, digest-checked transcripts into one record binding auditor, specs and manifest; severity-exact classes incl. `V-WRITE-RELATIVE` | `python3 census/round-17/seat-audit-replay.py …`; `census/round-17/transcript-manifest.py --check census/round-16/transcripts` | r17 |
| bounded repository-content census (r18) | after discovery, bound FIFO/special-reader stalls in preflight and measurement; preserve neighbour rows and disclose unmeasured/surviving groups, including interruption handling; no filesystem/PID sandbox guarantee | `census/round-18/c1-matrix-4800fd7.json` (12/9 failed →12/0); census selftest 69/0; S064, S072–S075, S077 | r18 |
| evidence-pointer gate (r18) | flag missing authority-file citations within the declared grammar, exact synthetic exemptions, fleet collisions, and dangling measured commits; keep total CLI early-error behavior | `census/round-18/final-verification-4800fd7.json` (selftest 61/0, pointer fixture 11/0, r16 fixture 15/0); S078 | r18 |
| process-residue observations (r18; r21 synthetic repair) | list-only historical scanner; current cmd/reason output share secret patterns and160-byte bounds; reason retains selected secret-bearing argv provenance. No live measurement, unknown-pattern or historical-exposure proof; never signal inherited processes | r21 synthetic27/27 (old emissions6/27, leaks19→0), `census/round-21/reason-after.txt`, S100/S101; r18 live-proc fixture not run | r18; r21 reason repair |
| paragraph-aware carry gate (r19) | flag an unmarked cut at a source physical-line end and accept boundary-marked, complete and wrapped-bullet carries; strict branch keeps five pinned replay verdicts | `tests/fixtures/r19-carry-wrap.py` 4/0 base-discriminating; `census/round-19/c1-carry.txt` | r19 |
| durable revision stamps (r19) | refuse HEAD/branch/short/keep-only/dirty-tree revisions before a record and verify tracked measured bytes | `tools/souji-rev-pin.py --selftest` 11/0; `tests/fixtures/r19-rev-pin.py` 13/0 | r19 |
| seat-audit delivery and signal classes (r19, current r21 counts) | exact explicit delivery grants; signal-shaped calls remain major; tools writes remain major | final r21 18-step receipts: auditor selftest118/0; r19-seat-audit-shapes17/0 (base12); r20-audit-contract78/0 (base11) | r19; r20 admitted grant repair |
| agreement digest pin (r19) | immutable r18 agreement artifact binding; current upgraded proc tool is not expected to match the old digest | r21 runner agreement-pin-check stages original revision bytes and checks original digests; old CLI requires an original-byte input tree, not the current source tree | r19; r21 historical replay |
| clone-isolated acceptance replay | replay18 frozen r20 predicates from local clone/bare sources, independent of source HEAD; source remote roots preserved privately, jj-only roots not promoted | `census/round-21/accepted-matrix.json`3/3 each18/18; remote-source-after.json18/18; keep-only refusal in final-code-verification.json; S102 | r21 |
| declared-evidence calibration audit (r22 attempt 2) | parse a self-assessment file at a named revision and re-derive its backticked-path, revision-token and sha256 assertions from committed bytes; read-only, git plumbing only, /var/tmp scratch; its fixtures reject the cheapest always-zero control | `python3 tools/souji-declared-evidence.py --selftest` 8/8; `census/round-22/attempt2/declared-evidence-before.tsv`; S109–S114 | r22 |
| blob-bound receipts (r23) | re-derive a counter at a full durable revision in a private `--no-local` clone and emit a receipt binding rev, tool path, tool sha256 of the bytes the command ran against, argv, exit code and redacted output; `verify` refuses a digest that is not the committed blob at the receipt's rev, and refuses a `git -C`/mutating/lost-found command. Not a proof of execution and not a sandbox | `tools/souji-receipt-run.py`; `tests/fixtures/r23-receipt-run.py` 8/8; `census/round-23/records/*.tsv` | r23 |
| record agreement audit (r23) | re-derive four declared-vs-observed keys over committed bytes (receipt-bound after-state, append-only superseded numbers, register-slice tally, uncommitted round work) and reject an always-zero emitter on eight of nine fixture cases | `python3 -B tools/souji-record-agreement.py --rev <full40>`; `tests/fixtures/r23-record-agreement.py` 9/9 `control=FALSE-GREEN-REJECTED` | r23 |

## Planned

- **r4 — AMENDED by operator mid-round:** the Obsidian-CLI integration
  claim was withdrawn ("forget the obsidian integration for now"); closed
  instead on the standalone ledger-verify capability
  (`tools/souji-vault-verify.sh`, installed r4). Finding: no usable CLI
  entry point on this host. The r4 note said the finding was banked in
  the operator scope file .ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md;
  that file is absent (checked 2026-10-25, ls -> "No such file or directory"),
  so the finding is not retrievable from committed bytes and is no longer
  presented as a banked artifact. Completion-criterion obsidian-row
  requirement waived by the operator.
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
- **r20 (planned r19) — admitted:** CloseSouji20 admitted C1/C2, coverage unchanged; MANIFEST rounds[402]. Actual audit flags, scope deviations and historical exposure remain disclosed.
- **r21 — admitted:** CloseSouji21, MANIFEST rounds[408], independently remeasured all three bounded claims. Exact closure is in `census/round-22/r21-closure-excerpt.json`; source-scope violations remain actual debt, not erased by admission.
- **r23 — done (record agreement, blob-bound receipts, F2 read side):** C1/C2/C3 as measured in the Round 23 table above; D1–D8 dispositions in `LOG.md` `Round23` and `corpus/lessons/round-23.md`.
- **r24 — planned:** carry the F2 actable remainder (the `/var/tmp` write-safety fixture that must exclude `git fsck --lost-found`), re-run the r23 counters at the new tip, and close the residual C1/C2 limits named above.
- **r22 — declared calibration:** repair the three inherited OPEN acceptance-predicate gaps, measured by the same synthetic result oracle over baseline and changed code, retaining all18 real positive outputs. Preregistration `29c1f7e8df849be8ee1b2d62d2351e17ec9d21a8`. F5 bytes/160-byte scope and all operator holds unchanged.

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
