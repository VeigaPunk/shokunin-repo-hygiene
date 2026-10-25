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

### Round 28 measurements (2026-10-25; base 3a2a80d0d18940a5e352ebc526da22a57dad83c4)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 Q57/Q59 pointer findings | calibration 7 | `findings=2`, `checked_reg=52` | `findings=0`, `checked_reg=52`; gate rc 2 because no committed round-28 reports under `.ufo/waves/round-28/` | `python3 -B tools/souji-landing-gate.py --root <lane> --rev <full40> --round 28 --fleet-root <fleet>`; target is SUMMARY findings=0 | `census/round-28/records/c1-before.tsv`; after at `765fe8bd602ac679d01e7a0790711485209ab8bd` |
| C2 F4 origin-record coverage | coverage 8 | SOURCES `135`, grounded F4 `4` | SOURCES `139`, grounded F4 `6`; gate `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`; sources-census rc 0; coverage agreement `grounded=13 mapped=13 dangling=0 mismatches=0` | `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`; grounded entry count `grep -lE '^ground: F4' corpus/knowledge/*.md \| wc -l`; gate-check; sources-census validate; coverage-agreement | `census/round-28/records/c2-before.tsv`; after at `765fe8bd602ac679d01e7a0790711485209ab8bd` |
| C3 evidence capture | operability 8 | dirty `.ufo/waves` `163`; r26/r27 manifests absent | dirty `.ufo/waves` `0`; manifests present; fixture `cases=6 pass=6 control=TAMPER-REJECTED`; r26 `sha256sum -c` warns 2 malformed newline-path records (rc 0), r27 clean | frozen `git status --porcelain ... | awk '$2 ~ /^\.ufo\/waves\// {n++} END{print n+0}'`; manifest tests; `bash tests/fixtures/r28-wave-evidence-capture.sh` | `census/round-28/records/c3-before.tsv`; after at `765fe8bd602ac679d01e7a0790711485209ab8bd` |

No owned score changed (calibration 7, coverage 8, operability 8). C1 reaches findings=0 but the gate's unqualified exit remains 2; C2 misses its frozen 138-row counter at 139 and its 6/6 coverage-agreement literal differs from the tool's global output; C3 has an independently unverifiable pair of newline-path manifest rows. No round admission is claimed.

### Round 27 measurements (2026-10-25; base e78ac7c4837b81b634db4a927605a751a7f006ba)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 pointer finding count | calibration 7 | `findings=2`, rc 2 | `findings=2`, rc 2; target 0 not met, no exemptions landed | `python3 -B tools/souji-landing-gate.py --root . --rev <full40> --round 27 --fleet-root /home/vgpnk/Projects/shokunin` | `census/round-27/records/c1-before.tsv`, `c1-after.tsv`; after at `6cb22dc20c9fdb3c7a49eaa1accabca339054c17` |
| C2 F4 origin-record coverage | coverage 8 | SOURCES `132`, grounded F4 `2` | SOURCES `135`, grounded F4 `4`; gate 2/2, slice 8/8, census rc 0 | row grep, `grep -rlE '^ground: F4' corpus/knowledge/ | wc -l`, `python3 -B tools/souji-gate-check.py`, `sources-census.sh validate` | `census/round-27/records/c2-after.tsv`, measured at `6cb22dc20c9fdb3c7a49eaa1accabca339054c17` |
| C3 pre-report gate | operability 8 | tool absent at base | tool present; fixture `cases=4 pass=4 control=FALSE-GREEN-REJECTED`, rc 0 | `bash tests/fixtures/r27-pre-report-gate.sh`; `git cat-file -e e78ac7c4837b81b634db4a927605a751a7f006ba:tools/souji-pre-report-gate.sh` | `census/round-27/records/c3-after.tsv`, measured at `6cb22dc20c9fdb3c7a49eaa1accabca339054c17` |

No owned axis score changed (calibration 7, coverage 8, operability 8). C1 failed its frozen target; C2 and C3 passed. No round admission is claimed.
### Round 25 measurements (2026-10-25; base a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 coverage-map kill-rule tool row | calibration 7 | Base tool rejects `--base-rev` (rc 2); base receipt `grounded=6` | At the independent C1 candidate `7e4dbef94061578fca2f58621f87908c886cc431`, `grounded=6 mapped=6 dangling=0 mismatches=0 kill_tested=6 kill_violations=0`, rc 0; fixture `cases=16 pass=16 control=FALSE-GREEN-REJECTED`. **Verified**; measured before C3's new F2 entry/map row, so the C1 counter does not depend on C3 landing. | `python3 -B tests/fixtures/r25-coverage-agreement.py --tool tools/souji-coverage-agreement.py`; `python3 -B tools/souji-coverage-agreement.py --root . --rev 7e4dbef94061578fca2f58621f87908c886cc431 --base-rev a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe` | `census/round-25/records/c1-after.tsv` |
| C2 size-census refusal surfaces | operability 8 (frozen axis; **unprovable on this axis**) | Existing fixture `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` | Extended fixture `cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, rc 0; old 1efe406 blob 11/12, regression 778747e 10/12. W2 reviewer found the move is coverage of four edge classes, not operability; the frozen axis is not relabeled. | `python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py` | `census/round-25/records/c2-after.tsv`, measured rev 679e2d02f46ec06447d679d9395d6592c5e35f5c |
| C3 common-dir structure envelope and colocated/plain precondition | coverage 8 | `selftest=PASS ids=5/5` | At candidate `728b2ce71acbe574ae3036b456724d0a3d6f8f08`, `selftest=PASS ids=7/7`, rc 0; common/private manifests unchanged; refs/jj/keep simulation yields `references.others.count=2` vs 0. The candidate carries the F2 entry and same-commit README map row; no F2/Core promotion. | `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` | `census/round-25/records/c3-after.tsv` |

Score delta: 0 for the owned score values; no reproducible 0–10 mapping exists. C1 verifies calibration; C2 is unprovable on operability and its coverage interpretation would collide with C3; calibration is harmed by that axis misattribution. No admission is claimed.

### Round 25 append-only corrections

- R24-M25: C3's old title "receipt verify/run symmetry" overclaimed. At r24, R1 closed and R2 narrowed (label present in argv); general symmetry remains unproved.
- R24-M22: the old r24 slice sentence at :181 is superseded by the authoritative count `8 accepted / 0 present / 0 unverifiable / 0 refused` in `census/round-24/records/slice-verdicts.tsv`, mapped in `corpus/lessons/round-25.md`.
- R3 (dated 2026-10-25): `tool_sha256` binds the labelled committed file bytes and argv text, not the executed program. At base a6d2d15 there were 21 tracked grep candidates, 19 verify=ok and 2 malformed non-receipts; reproduced by W2 report `w2/RevR3Counter.md` and the candidate-pinned verify loop.
- R24-M2: `corpus/README.md:40` status now has an appended marker naming the superseding F2 row at :517; the row itself was not deleted or moved.
- `corpus/lessons/round-23.md`'s K1 last-wins sentence is superseded by an appended r25 correction; the r24 code fix remains r24 work. R15 cross-revision K1 decoy anchoring remains open.
- Sources S124–S127 are opened this round. New F2 knowledge on existing frontier ground does not promote F2 to Core.

superseded by SCORECARD.md:181; mapping corpus/lessons/round-25.md § Quarantine-slice vocabulary; authority census/round-24/records/slice-verdicts.tsv; recount 8 accepted
superseded by SCORECARD.md:180; correction in corpus/lessons/round-25.md § R24-M25: R1 closed, R2 narrowed to recorded argv-text presence; no general symmetry claim.
superseded by SCORECARD.md:92; correction in corpus/lessons/round-25.md § R3: tool_sha256 binds labelled committed file bytes, not the executed program.
superseded by SCORECARD.md:224; correction in corpus/lessons/round-25.md § R24-M25: R1 closed, R2 narrowed; general verify/run symmetry remains unproven.
superseded by SCORECARD.md:225; the r25 work and remaining planned items are adjudicated in corpus/lessons/round-25.md.

---

### Round 24 measurements (2026-10-25, lane base a65fac98964b445758e94c805728c9a19d302ff8)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 F2 debris census (write-safety fixture) | coverage 8 | at base the fixture and tool are absent (`git cat-file -e a65fac9:tests/fixtures/r24-size-census.py` fails), so `cases=0 pass=0` by the frozen definition; skip-the-work control (the case-8 stub as `--tool`, fixture bytes of `1efe406`): `cases=8 pass=4 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, rc 1 — the stub fails cases 2 dangling, 3 garbage, 5 alternates, 6 refusal (`census/round-24/records/c1-control-stub.tsv`, `rev=1efe406e7f39b8fe736be2a566053703a571ffc0`) | `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, rc 0 (`census/round-24/records/c1-after.tsv`, `rev=778747eb671f8e85ef5387bc3d7023337b30467c`); case 3 reads `garbage=1 size_garbage=2` on the main and the linked path, case 4 reads `garbage=0` while raw `git -C <linked> count-objects -v` reads `garbage: 1`, case 7 sees `fsck --lost-found` change the manifest | `python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py` | fixture `tests/fixtures/r24-size-census.py` sha256 `373ef1f0a02f8ca11fccd4ff32d8511c1eaaf3ede672c37ed11ef2b10968084f` (bound by both receipts); tool `tools/souji-size-census.py` at 778747e sha256 `09bb8e0d9906b0dfef44775a9e5cd7c8f8a27d9bcdf559e2d371a3ef7ff1ed6d` (not bound by the receipt; `git show 778747e:tools/souji-size-census.py \| sha256sum`) |
| C2 coverage-map agreement | calibration 7 | `grounded=4 mapped=2 dangling=0 mismatches=2`, rc 1, at base `a65fac9` with the tool bytes of `1efe406`: `count-objects-garbage-readings-r25.md` and `repo-size-census-readonly.md` were MISSING-FROM-MAP (named only in a status cell) (`census/round-24/records/c2-control-base.tsv`) | `grounded=6 mapped=6 dangling=0 mismatches=0`, rc 0 (`census/round-24/records/c2-after.tsv`, `rev=778747eb671f8e85ef5387bc3d7023337b30467c`); fixture `cases=9 pass=9 control=FALSE-GREEN-REJECTED` (`census/round-24/records/c2-fixture-after.tsv`); per-entry kill rule (amendment 1): all 4 base-grounded entries present at the tip with the same F<k> (`git diff a65fac9 778747e -- corpus/knowledge/` adds two `ground:` lines and removes none) | `python3 -B tools/souji-coverage-agreement.py --root . --rev <full40>`; `python3 -B tests/fixtures/r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py` | tool `tools/souji-coverage-agreement.py` sha256 `71b89eb3c7ce417979c5fce2c759dafe023af21d6310fde49197c766b8f28897`; fixture sha256 `42259756a06538a5dfb81cb82fba20737eacdcfd5c06b9b36594071b26f9da44` |
| C3 receipt verify/run symmetry | operability 8 | base runner (`tools/souji-receipt-run.py` sha256 `e13d0c83…`, identical at `a65fac9` and `1efe406`): `cases=8 pass=6 refusals=0/2 regress=5/5`, rc 1 — case a (non-durable rev, no-ref and `refs/jj/keep`-only) and case b (`tool=` not in argv) both `verify=ok` (`census/round-24/records/c3-control-base-runner.tsv`) | `cases=8 pass=8 refusals=2/2 regress=5/5`, rc 0 (`census/round-24/records/c3-after.tsv`, `rev=778747eb671f8e85ef5387bc3d7023337b30467c`): `RECEIPT-REV-NOT-DURABLE` for both case-a instances, `RECEIPT-TOOL-NOT-IN-ARGV` for the absent and substring-only labels, the five r23 receipts still `verify=ok` | `python3 -B tests/fixtures/r24-receipt-verify.py --tool tools/souji-receipt-run.py --lane-root .` | fixture sha256 `f8c4c391097ee9745b72cbf5eef51aec235a89946c22831d10a1db7badc708b2`; runner at 778747e sha256 `9df0738c…` (not bound by the receipt) |
| assimilation (rides inside C1; no claim slot) | coverage 8 | F2 grounded entries 2 (`ground: F2` lines at `a65fac9`); quarantine slice not yet checked | gate `entries=1 ok=1 slice_verdicts=8 slice_total=8 fail=0` (`census/round-24/records/gate-check-r24-entry.tsv`); entry `corpus/knowledge/count-objects-linked-worktree-garbage.md` (S120–S123), 2 staged packages admitted (r27 re-sourced, r25 matrix only), 4 rejected; slice 7 accepted + 1 unverifiable (S118) | `python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries corpus/knowledge/count-objects-linked-worktree-garbage.md --snapshot-dir census/round-24/sources --slice census/round-24/records/quarantine-slice --slice-verdicts census/round-24/records/slice-verdicts.tsv` | gate tool sha256 `d5ed0805b10f283fcc240a2daa628681a9c76bec7df1fe1cbc7e204754ecdc9d`; snapshots `census/round-24/sources/*` (`sha256sum -c SHA256SUMS` 6/6) |
| r13 structure entry recheck (freshness; not a claim) | — | `git-repo-structure-readonly.md` verified on git 2.55.0 only, r16 note "pending recheck" | `selftest=PASS ids=5/5` on git 2.56.0 (`census/round-24/records/r13-recheck-receipt.tsv`) | `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` | fixture sha256 `b6bf52056d037b2251632b409be3d31852588480c392ddc50ca8f8dbf101179f` |

Each round-24 counter scored the amended (amendment 1, stricter-only, written before any control
or after receipt) bytes pinned above. Controls were committed in `ce5971c` before any after-data. A
disclosed deviation: the L1 ran sanity executions of the C2 tool and C3 fixture before the
amendment; those runs are not claim evidence. Named limits:

- **C1.** The no-write envelope is a `/var/tmp` fixture claim over 8 frozen cases on git 2.56.0.
  The manifest excludes atime/ctime, so a tool that restores directory mtimes after a write is
  invisible to it. The stderr contract (`census.warning=` lines, exit 1 on other stderr) and the
  not-a-repository exit 2 have no case. No case plants hostile config or environment: the tool
  carries `-c core.fsmonitor=false -c core.hooksPath=/dev/null` and a scrubbed env, but no counter
  exercises them. Cases 7 and 8 pass for any `--tool`.
- **C2.** C2 covers the 6 grounded entries out of 13 `.md` entries. The per-entry kill rule was
  checked by `git diff`, not by the tool. `mismatches=0` does not retire the stale
  "frontier, no entry" F2 row at `corpus/README.md:40`.
- **C3.** Argv membership binds the label to recorded text, not to the executed program. A tool
  named as an operand while another program runs still verifies. Of the 20 r23 residuals, C3
  closes 1 and narrows 6.

The lane-bound figure `census/round-24/size-census-lane.txt` (`garbage=0 size_garbage=0
unreachable=1093 alternates=0`, tool sha256 `09bb8e0d…`) describes this repository at the moment of
the run (jj keep refs plus a cruft pack). It is not a fleet figure and not a plain-clone figure. It
is a measurement file, not a v1 receipt: `verify` returns `RECEIPT-MALFORMED`. Registry 119 → 123
(S120–S123) is a grep count over committed bytes, not a receipt.

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
| blob-bound receipts (r23) | re-derive a counter at a full durable revision in a private `--no-local` clone and emit a receipt binding rev, tool path, tool sha256 of the bytes the command ran against, argv, exit code and redacted output; `verify` refuses a digest that is not the committed blob at the receipt's rev, and refuses a `git -C`/mutating/lost-found command. Not a proof of execution and not a sandbox | `tools/souji-receipt-run.py`; `tests/fixtures/r23-receipt-run.py` 8/8; `census/round-23/records/*.tsv` | r23 | *(R3 dated 2026-10-25: the digest binds the labelled file's committed bytes and the recorded argv label, not the executed program.)*
| record agreement audit (r23) | re-derive four declared-vs-observed keys over committed bytes (receipt-bound after-state, append-only superseded numbers, register-slice tally, uncommitted round work) and reject an always-zero emitter on eight of nine fixture cases | `python3 -B tools/souji-record-agreement.py --rev <full40>`; `tests/fixtures/r23-record-agreement.py` 9/9 `control=FALSE-GREEN-REJECTED` | r23 |
| debris census (r24) | read `count-objects -v` garbage / size-garbage / alternates against the resolved common git dir (so a linked worktree's private-gitdir `garbage: 1` is not reported) and count `fsck --unreachable --no-reflogs` lines, under a scrubbed environment with `core.fsmonitor=false` and `core.hooksPath=/dev/null`; refuse `--lost-found`, promisor/partialClone repositories (including a leftover `objects/pack/*.promisor`) and non-repositories with exit 2. The no-write envelope is a `/var/tmp` fixture claim over 8 frozen cases (manifest excludes atime/ctime); unreachable includes alternates when alternates>0; one lane-bound figure, no fleet figure, no deletion authority | `tools/souji-size-census.py`; `python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py` 8/8 `control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` (`census/round-24/records/c1-after.tsv`); stub control 4/8 (`c1-control-stub.tsv`); `corpus/knowledge/count-objects-linked-worktree-garbage.md`, S120–S123 | r24 |
| coverage-map agreement (r24) | at a full 40-hex revision, from committed bytes only, flag every `ground: F<k>` knowledge entry not named by a backticked `knowledge/<name>` in the entries column of a coverage-map row whose ground cell starts with F<k> (status-column mentions never map), and every backticked entries-column `knowledge/` path absent at that revision; its fixture fails the always-zero emitter on all nine cases. Scope: grounded entries only (6 of 13 at 778747e); the per-entry kill rule is not mechanized | `python3 -B tools/souji-coverage-agreement.py --root . --rev <full40>`; `census/round-24/records/c2-control-base.tsv` (2 at base), `c2-after.tsv` (0); `tests/fixtures/r24-coverage-agreement.py` 9/9 (`c2-fixture-after.tsv`) | r24 |

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
- **r25 — attempted, honest stop; C1 verified at independent candidate; C2 unprovable on frozen operability axis (W2 shows the change is coverage of four edge classes); C3 bounded fixture claim measured at `728b2ce`.** Axis misattribution harms calibration; no owned-axis score changes, no admission. Certification OFF, K5 HELD.

- **r24 (planned r23) — done, see `corpus/lessons/round-24.md`:** C1 F2 debris census with a `/var/tmp` write-safety fixture that refuses `--lost-found` (8/8), C2 coverage-map agreement (2 → 0 mismatches), C3 receipt verify/run symmetry (refusals 0/2 → 2/2, regress 5/5), as measured in the Round 24 table; one assimilated F2 entry (S120–S123), `git-repo-structure-readonly.md` re-verified on git 2.56.0. Of the planned "re-run the r23 counters": C3 case d re-verifies the five r23 receipts at the tip; the r23 record-agreement counter has no r24 receipt. Of "close the residual C1/C2 limits": 1 of 20 closed (verify durability), 6 narrowed, 12 open, 1 open by design (`.ufo/waves/round-24/w1/RevR23Residuals.md`). Certification OFF, K5 HELD.
- **r25 (planned r24):** (a) calibration: make C2's per-entry kill rule (base-grounded entry absent or re-grounded at tip) a tool row instead of a hand `git diff`; retire or mark superseded the stale F2 "frontier, no entry" row at `corpus/README.md:40`; turn `census/round-24/size-census-lane.txt` into a v1 receipt or relabel it; replace the r23 `tool_sha256=` grep counter with a count of `verify=ok` receipts; receipt the r23 record-agreement counter at the tip; carry the open r23 residuals R3, R7 (counts read from stderr), R15 (K1 decoy) and R17 (K1 trailing shadow). (b) coverage: put `tools/souji-repo-structure.sh` under the r24 common-dir manifest envelope, then the colocated/plain byte-comparison precondition (README `### Frontier (r24)`); add the untested C1 contract parts — `census.warning=` and exit 1 on other stderr, not-a-repository exit 2, hostile `core.fsmonitor`/env cases, and a ctime or read-only-`.git` arm against mtime-restore writes; re-verify the two remaining git-2.55.0 entries (`git-auto-maintenance-prunes-worktrees.md`, `git-grace-periods-and-expire-to.md`) on 2.56.0. (c) operability: bind the receipt label to the program position (interpreter's first script argument), not just argv membership. Fleet route: the LEARNING.md expansion predicate (capability vs entry-on-uncovered-ground) is unresolved. Certification stays OFF, K5 HELD; F5 reap and NAMESPACE holds unchanged.

- **r28 (planned r27):** calibration: correct Q57's stale composite-site citation and measure SCORECARD/SHONEN mismatches against observed lane state (the r27 landing-gate count was not a valid calibration counter); coverage: re-run the F4 source recheck and disposition the routed S119 edition only with a decision-time pin; operability: retain the tested pre-report gate and resolve the r26 `.ufo` evidence leftovers through an approved committable evidence path. C1 r27 target remains failed; no admission inferred.
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

---

### Round 26 append-only corrections

The five bare `superseded by SCORECARD.md:<n>` lines above are r25 output computed at the
r25-base layout (`a6d2d15`, 228 lines) and are left byte-verbatim (append-only). The r25
landing `728b2ce` inserted the `- **r25 — attempted, honest stop …` planned bullet at
SCORECARD.md:136, so four of the five numbers already resolved one line early at this
round's frozen base; the r26 C1 integration `a529c76` then removed the generation scaffold
and re-ordered the file (254 → 233 lines, Round 25 measurements above Round 24), moving all
five targets. Mapping (old = the number as written; pre-cleanup = the same content at
`0eca7c8`; post-C1 = `a529c76`):

| cited | content it names | r25 base `a6d2d15` | pre-cleanup `0eca7c8` | post-C1 `a529c76` |
|---|---|---|---|---|
| `SCORECARD.md:181` | r24 assimilation row: quarantine-slice sentence | 181 | 182 | 51 |
| `SCORECARD.md:180` | r24 C3 receipt verify/run symmetry row (the overclaiming title) | 180 | 181 | 50 |
| `SCORECARD.md:92` | r23 blob-bound receipts row: `tool_sha256` sentence | 92 | 92 | 153 |
| `SCORECARD.md:224` | r24 "planned → done" bullet: C3 verify/run claim | 224 | 225 | 199 |
| `SCORECARD.md:225` | r25 "planned" bullet | 225 | 226 | 200 |

The five superseded-by lines themselves moved from `0eca7c8` lines 250-254 to lines 36-40;
their bytes are unchanged. Re-derivation per cell:
`git show <rev>:SCORECARD.md | sed -n '<n>p'`.

---

### Round 26 measurements (2026-10-25; lane base 89e0fceeefcf28db313c94120be6d25e03c60094)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 r24 scaffold integration + R3 note + capability rows | calibration | markers=2, headings `17 175 231` (r23, r24-fenced, r25-last) at base | markers=0, headings `17 44 78` (r25 < r24 < r23); byte-spans of all seven amendment-2 regions re-verified | census/round-26/c1-counter.sh, receipt c1-after.tsv | 07f83e6 |
| C2 grounded F1 knowledge entries (S128-S132) | coverage | grounded_f1=0, registry rows=127 at base | grounded_f1=2, rows=132; gate entries=2 ok=2 fail=0; coverage agreement grounded=9 mapped=9, kill_violations=0 | census/round-26/c2-counter.sh, c2-gate.tsv, c2-k4-{base,after}.tsv | 9a6e0f1 |
| C3 prereg axis-of-surface checker | operability | tool absent at base | claims=3 flags=0 self-hosted; fixture cases=12 pass=12 control=FALSE-GREEN-REJECTED | census/round-26/c3-counter.sh, receipts c3-before/after.tsv | 0c92c2e |

