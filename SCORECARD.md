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
| C1 Q57/Q59 pointer findings | calibration 7 | `findings=2`, `checked_reg=52` | `findings=0`, `checked_reg=52`; gate rc 2 because committed lane bytes cannot carry round-runtime reports | `python3 -B tools/souji-landing-gate.py --root <lane> --rev <full40> --round 28 --fleet-root <fleet>`; target is SUMMARY findings=0 | `census/round-28/records/c1-before.tsv`, `c1-after.tsv`; measured at `de478b483db66a8d8ff2d627cde1ccce6e21a014` |
| C2 F4 origin-record coverage | coverage 8 | SOURCES `135`, grounded F4 `4` | SOURCES `139`, grounded F4 `6`; gate `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`; sources-census rc 0; coverage agreement `grounded=13 mapped=13 dangling=0 mismatches=0` | `grep -cE '^\\|[[:space:]]*S[0-9]{3,}[[:space:]]*\\|' corpus/SOURCES.md`; grounded entry count `grep -lE '^ground: F4' corpus/knowledge/*.md \\| wc -l`; gate-check; sources-census validate; coverage-agreement | `census/round-28/records/c2-before.tsv`, `c2-after.tsv`; measured at `ed270c42161cd62829783a5e5d2ef4e27089331c` |
| C3 evidence capture | operability 8 | dirty `.ufo/waves` `163`; r26/r27 manifests absent | dirty `.ufo/waves` `0`; manifests present; fixture `cases=6 pass=6 control=TAMPER-REJECTED`; r26 `sha256sum -c` warns 2 malformed newline-path records (rc 0), r27 clean | frozen `git status --porcelain ... | awk '$2 ~ /^\\.ufo\\/waves\\// {n++} END{print n+0}'`; manifest tests; `bash tests/fixtures/r28-wave-evidence-capture.sh` | `census/round-28/records/c3-before.tsv`, `c3-after.tsv`; measured at `ed270c42161cd62829783a5e5d2ef4e27089331c` |

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


### R29 append-only correction (round 29, C1)

R29-CORRECTION SCORECARD.md:23 measured at rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e: the r26 receipt has 1382 records, 152 naming paths absent from the committed tree, and 14 committed symlinks with no record; command: python3 -B census/round-29/c2-counter.py --root <lane> --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e → SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0 (rc 1).
R29-CORRECTION SCORECARD.md:23 the "2 malformed newline-path records" reading is superseded, not edited: the 152 absences are the defect — all 152 match ignore rules rebuilt from the committed .gitignore stack (148 nested inside the capture, 4 by root `__pycache__/`) — and the 2 escaped rows are valid GNU escapes whose digests equal the committed blobs, which this host's uutils sha256sum 0.8.0 rejects as improperly formatted.
R29-CORRECTION SCORECARD.md:23 still true at the same rev: r27 (124 records) and r28 (75 records) verify with failed=0 and uncovered=0; the dirty `.ufo/waves` 163→0 count and the fixture line `cases=6 pass=6 control=TAMPER-REJECTED` are working-tree and tool-run claims and are not re-derived here from committed bytes.

### Round 29 measurements (2026-10-25; base 691dd29211c53d0ef94fa072394cb9c8a69fe92e; preregistration b8cb4b31ce80e2e3314b88e85d40ea9873180804)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 registry/record agreement | calibration 7 | `SUMMARY k1=6 k2=4 mismatches=10` rc 1 (do-nothing control identical; junk controls 6/10/68/12) | `SUMMARY k1=0 k2=0 mismatches=0` rc 0 with the frozen v1 and the amended v2 instrument; stale statements corrected append-only | `python3 -B tools/souji-registry-agreement.py --root . --rev <full40> --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804` | `census/round-29/records/controls.tsv`; measured at `8aaacf518d0dc9292d5258abf7d74bdaea1b76e7`, re-run at `1dc678500c92164b0b2bea82b934dd03d1dfbf38` |
| C2 committed-bytes receipts | operability 8 | `manifests=3 failed=152 uncovered=14 floor_violations=0` rc 1; amended v2 `fidelity=11 tool_unchanged=1` | `manifests=3 failed=0 uncovered=0 floor_violations=0` rc 0, r26 `records=1381`; v2 `lost=0 fidelity=0 tool_unchanged=0`; fixture `cases=15 pass=15 control=TAMPER-REJECTED` (base tool 8/15); `--verify --rev` `records=1381 failed=0 uncovered=0` | `python3 -B census/round-29/c2-counter.py --root . --rev <full40>`; `python3 -B census/round-29/c2-counter-v2.py --root . --rev <full40> --base-rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e`; `bash tests/fixtures/r28-wave-evidence-capture.sh` | measured at `b86200714069022954a3b498cf697d894119b45e` |
| C3 F3 duplicate-verdict entries | coverage 8 | F3-grounded entries `0`, SOURCES rows `139`, coverage `grounded=13 mapped=13 dangling=0 mismatches=0` | `2`, `143`, `grounded=15 mapped=15 dangling=0 mismatches=0`; gate `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`; census rc 0; integrity legs 9/9 (4 red at base) | `git grep -lE '^ground: F3' <rev> -- corpus/knowledge/ \| wc -l`; `git show <rev>:corpus/SOURCES.md \| grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'`; `python3 -B tools/souji-coverage-agreement.py --root . --rev <full40>`; `python3 -B census/round-29/c3-integrity.py --root . --rev <full40>`; `sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` | measured at `1dc678500c92164b0b2bea82b934dd03d1dfbf38` |

Owned scores unchanged (calibration 7, coverage 8, operability 8): no reproducible 0-10 mapping exists. All three claims met their frozen headline literals; the stricter-only amendments A1-A4 (`census/round-29/records/amendments.txt`) were added after wave-1 attacks and met as well. Disclosures: K1 is registry self-consistency, not a SCORECARD/SHONEN count; the frozen `0 -> 2` for C3 counts newly tagged entries (the held F3 entry has no `ground:` header); the first capture design preserved `.git` fixtures by digest only before the floor check led to byte-preserving `.git.captured`. No round admission is claimed; the non-author closure rules.

### Round 29 capability rows (appended, not inserted: K2 requires SCORECARD.md to stay append-only since the preregistration commit)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| declared-record agreement audit (r29) | at a full 40-hex revision and a prereg list-rev, read only committed bytes and report every SOURCES `used-by` row that names a missing or non-citing path, every entry `source:` citation whose row does not list the entry, rows deleted or indented out of the registry, and every listed stale statement that is not append-only corrected with the derived facts and a derivation-source path; its fixture rejects the always-zero emitter | `python3 -B tests/fixtures/r29-registry-agreement.py` `cases=20 pass=20 control=FALSE-GREEN-REJECTED` (v1 tool 8/20); base `mismatches=10` -> `0` | r29 |
| committed-bytes wave-evidence capture (r29) | capture a round's `.ufo/waves/round-N/` into a receipt that verifies over the blobs git actually commits: nested `.gitignore`/`.gitattributes`/`.git` stored as `.captured`, ignored names accounted in `excluded.tsv`, symlinks in `symlinks.tsv`, GNU-escaped records for odd names, and `--verify --rev <full40>` over `ls-tree`/`cat-file` | `bash tests/fixtures/r28-wave-evidence-capture.sh` `cases=15 pass=15 control=TAMPER-REJECTED` (base tool 8/15); `census/round-26/waves` `records=1381 failed=0 uncovered=0` | r29 |

### Planned (appended at round 29)

- **r30 (planned r29):** calibration: bind SCORECARD and SHONEN statements (each capability row's stated count re-run, not only registry used-by) to an observable and count the mismatches; operability: point `tools/souji-landing-gate.py` report discovery at the committed `census/round-<N>/waves/` capture (r28 routed defect 3, not addressed in r29); coverage: choose a frontier surface from `corpus/README.md ## Frontier` (F1/F2/F4) with a counter that names the surface moved. Carry the stale-sweep remainder (`census/round-29/waves/w1/deliver-stale-sweep.tsv`, 5 disagreeing rows) and the Reviewer43 F7 literal-shape defects. Certification OFF, K5 HELD.

### R30 append-only corrections (round 30, C1: capability-table literals vs committed output)

Measured at base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b by `python3 -B tools/souji-capability-agreement.py --root <lane> --rev <full40> --base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --list-rev d4928ec86b667e3d1ed0adb07fb088e500cf1631` (v1 bytes at d4928ec; stricter amendment A3 in the current file). The capability cells above stay as written; each line below records what the named command prints at the measured revision. Of the 13 base mismatches, 7 are notation (the stated numbers equal the printed numbers, in another shape: R03 R06 R07 R08 R09 R10 R11), 4 are counts that grew after the row was written (R04 5 -> 7 ids at r25; R05 18 -> 65 selftest checks by r19; R14 9 -> 15 cases at r25; R15 8 -> 12 cases at r25), R16's cell omits the required `--tool` argument (the r24 invocation, `census/round-24/records/c2-fixture-after.tsv`, still prints 9 of 9), and R18 is a v1 counter artifact: its stdout ends `cases=15 pass=15 control=TAMPER-REJECTED` (`census/round-30/records/d3-green-r28-wave-evidence-capture.txt`) but v1 reads the concatenated stdout+stderr, whose last digit-bearing line is a usage banner the fixture provokes on purpose. Literal provenance per row: `.ufo/waves/round-30/w1/deliver-c1-literal-history.tsv` (SwarmRevenger34: all 13 literals were accurate when written).

R30-CORRECTION SCORECARD.md:154 R03 rc=0 observed=SUMMARY total=5 failed=0 hung=0
R30-CORRECTION SCORECARD.md:155 R04 rc=0 observed=selftest=PASS ids=7/7
R30-CORRECTION SCORECARD.md:158 R05 rc=0 observed=SELFTEST pass=65 fail=0
R30-CORRECTION SCORECARD.md:158 R06 rc=0 observed=SUMMARY total=15 failed=0
R30-CORRECTION SCORECARD.md:160 R07 rc=0 observed=SUMMARY total=29 failed=0
R30-CORRECTION SCORECARD.md:161 R08 rc=0 observed=SUMMARY total=35 failed=0 skipped=2
R30-CORRECTION SCORECARD.md:166 R09 rc=0 observed=SUMMARY total=4 failed=0 base_discriminating=2
R30-CORRECTION SCORECARD.md:167 R10 rc=0 observed=SUMMARY total=11 failed=0
R30-CORRECTION SCORECARD.md:167 R11 rc=0 observed=SUMMARY total=13 failed=0 base_discriminating=6
R30-CORRECTION SCORECARD.md:173 R14 rc=0 observed=selftest=15/15
R30-CORRECTION SCORECARD.md:174 R15 rc=0 observed=cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED
R30-CORRECTION SCORECARD.md:175 R16 cmd=python3 -B tests/fixtures/r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py rc=0 observed=cases=9 pass=9 control=FALSE-GREEN-REJECTED
R30-CORRECTION SCORECARD.md:314 R18 rc=0 observed=Usage: bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> [--verify [--rev <full40>]]

The R18 line satisfies only the frozen v1 reading; under A3 the row matches on its stdout line and the banner is refused as an observation. R08's `skipped=2` is the documented invocation without `--baseline-dir` (`corpus/knowledge/jj-colocation-receipts.md` recheck line).

### Round 30 measurements (2026-10-26; base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b; preregistration d4928ec86b667e3d1ed0adb07fb088e500cf1631; amendments 02aea483b4366da8705342657995a310cd21a708)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 capability-row literal agreement | calibration 7 | `SUMMARY k1=13 k2=0 mismatches=13 rows=18 pointers=10` (v1; A3 reads `k1=12`, R18 matching on stdout) | `SUMMARY k1=0 k2=0 mismatches=0 rows=18 pointers=10` under v1 and A3: **met** | `python3 -B tools/souji-capability-agreement.py --root <lane> --rev <full40> --base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --list-rev d4928ec86b667e3d1ed0adb07fb088e500cf1631` (v1 = the blob at d4928ec) | `census/round-30/records/c1-before.txt`, `census/round-30/records/c1-after-v1.txt`, `census/round-30/records/c1-after-a3.txt`; landing 7b16731fcd8ab9b95220b50603314aa8dc92b2ec |
| C2 committed-capture report discovery | operability 8 | `SUMMARY reports=0 cne=1 dangling=3 other=0 fixture=fail redarm=fail regress=same` | at the C2 landing commit `reports=86 cne=0 dangling=1 other=7 fixture=ok redarm=ok regress=same` (v1) and v2 `bind=fail regress_full=differs`: **missed** by the frozen kill rule (the one dangling pointer is the C1 block's uncaptured wave path; the v2 regress leg has a regex defect) | `python3 -B census/round-30/c2-counter.py --root <lane> --rev <full40> --base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --fleet-root /home/vgpnk/Projects/shokunin`; `census/round-30/c2-counter-v2.py` same args | `census/round-30/records/controls.tsv`, `census/round-30/records/c2-after-v1.txt`, `census/round-30/records/c2-after-v2.txt`; landing 68447afef62e4761249af55a2467657f04046537 |
| C3 F1 keep-ref expiry entry | coverage 8 | `SUMMARY legs=9 fail=8 f1_entries=2`; v2 `e1..e4=fail f1_exact=2` | `SUMMARY legs=9 fail=0 f1_entries=3`; v2 `e1=ok e2=ok e3=ok e4=ok f1_exact=3`: **met** (five sentences of the entry corrected append-only after wave-2 attacks) | `python3 -B census/round-30/c3-counter.py --root <lane> --rev <full40>`; `census/round-30/c3-counter-v2.py` same args | `census/round-30/records/c3-after-v1.txt`, `census/round-30/records/c3-after-v2.txt`; landing 76c94eb41fc38093d7143a016006b6275e102d5d |

Owned scores unchanged (calibration 7, coverage 8, operability 8): no reproducible 0-10 mapping exists, and C2 missed. The final-tip re-measurement of all three claims is committed in the records directory right after this table lands (final-tip-measure.txt). No round admission is claimed; the non-author closure rules.

### Round 30 capability rows (appended)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| capability-literal agreement audit (r30) | re-run every enumerated capability-row command from committed bytes in a private clone and report each stated count that the command no longer prints, accepting only append-only `R30-CORRECTION` lines whose rc and observed line reproduce (A3: stdout-first, digit-boundary match, `cmd=` may only extend the row argv, banners refused) | `census/round-30/records/c1-before.txt` (`k1=13`) -> `census/round-30/records/c1-after-a3.txt` (`k1=0`); `census/round-30/records/controls-amended.tsv` (bypass and banner corrections refused) | r30 |
| committed-capture report discovery (r30) | the landing gate evaluates a round whose reports exist only in the committed `census/round-N/waves/` capture, resolves `.ufo/waves/round-N/` pointers through it and ignores template tokens; it surfaced round 29's seven uncarried seat failures | `python3 -B tests/fixtures/r30-landing-gate-discovery.py --tool tools/souji-landing-gate.py` `cases=7 pass=7 control=FALSE-GREEN-REJECTED` (base gate 3/7, `census/round-30/records/c2-fixture-red-before.txt`); `census/round-30/records/m1-r29-carry-red-before.txt` | r30 (claim C2 missed its frozen kill rule; the capability runs) |

### Planned (appended at round 30)

- **r31 (planned r30):** calibration: widen the capability-literal enumeration to count-bearing rows without a command beside them (SCORECARD.md:164 and :168, SwarmCritic24 F7) and add a sentence-to-record check for admitted entries (the r30 entry shipped five refuted sentences); operability: discovery precedence (one force-added wave file hides the capture), the `round-` cut rule, `%d` templates, `.captured` names, A1's regress regex, and a concurrency-safe C1 scratch; coverage: the object-prune clock behind a dropped keep ref (reflogs and descendant keep refs kept B present) or the F1 fleet exposure numerator re-census. Certification OFF, K5 HELD.

### Round 31 capability-cell supersessions (C1, appended; base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc)

Each row below supersedes one count literal of a capability cell above (item ids and base lines from `census/round-31/c1-cells.tsv`); the cell text stays as written. `run:` re-runs the named command and states what it prints now; `record:` names the unchanged record of the row's own round that shows the count, restated in that record's notation with the same integers. Counter: `python3 -B tools/souji-capability-cells.py --root <lane> --rev <full40> --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`. L29 (`remote-source-after.json18/18`, SCORECARD.md:170) has no row: its record states the count only as separate scalar fields (`"matched_command_count": 18`), so no honest binding exists under the frozen rule and the item stays UNBOUND (wave-1 SwarmExecutor04).

| item | base line | literal | binding | reason |
|---|---|---|---|---|
| L01 | SCORECARD.md:152 | 6/6 | run: bash tests/fixtures/r12-maintenance-guard.sh --selftest | Written at d7266c5 together with `tests/results/r12-maintenance-guard.txt`, whose selftest run records `selftest=PASS ids=6/6`, and the same command re-run at the revision still prints ids=6/6. |
| L02 | SCORECARD.md:153 | 36/36 | run: python3 tools/souji-cert-evidence.py --selftest | Written at 23014d4 with the `evidence-selftest` entry of `census/round-13/verification.json`, and the same command re-run at the revision still prints 36/36 passed. |
| L03 | SCORECARD.md:153 | 5/5 | record: census/round-13/verification.json | Written at 23014d4, whose `evidence-external-fixture` entry runs `tests/fixtures/r13-cert-evidence.py` and records the stdout line `fixture: 5/5 checks passed` that the cell's "external fixture 5/5" restates. |
| L04 | SCORECARD.md:154 | total=5 failed=0 | run: bash tests/fixtures/r13-quarantine-bounds.sh | Written at 23014d4 citing the `quarantine-bounds` entry of `census/round-13/verification.json`, and the same command re-run at the revision prints `SUMMARY total=5 failed=0`, the fixture's own notation for the cell's 5/5. |
| L05 | SCORECARD.md:155 | ids=7/7 | run: bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh | Written at 23014d4 citing the `structure-selftest` entry of `census/round-13/verification.json` as ids=5/5, and the same command re-run at the revision prints ids=7/7, the grown count restated in the fixture's notation. |
| L06 | SCORECARD.md:158 | pass=65 fail=0 | run: python3 tools/souji-landing-gate.py --selftest | Written at 163158a as 18/18; the only committed round-16 mentions of that count are under census/round-16/transcripts/, which the record rule excludes, so the re-run at the revision that prints `SELFTEST pass=65 fail=0` is the row observable. |
| L07 | SCORECARD.md:158 | total=15 failed=0 | run: python3 tests/fixtures/r16-landing-gate.py | Written at 163158a as 15/15; the count appears in no committed census/round-16 record outside transcripts/, and the same command re-run at the revision prints `SUMMARY total=15 failed=0`, the fixture's own notation for the unchanged 15/15. |
| L08 | SCORECARD.md:159 | total=32	pass=32 | record: census/round-21/read-fixture-after.txt | r21 read-fixture-after.txt is the read-fixture run capture whose SUMMARY states total=32 pass=32, the cell's read32/32. |
| L09 | SCORECARD.md:159 | total=32	pass=18 | record: census/round-21/read-fixture-before.txt | r21 read-fixture-before.txt runs that same fixture against the base auditor named in its COMMAND line and states total=32 pass=18, the cell's base18/32. |
| L10 | SCORECARD.md:159 | total=4	pass=4 | record: census/round-21/render-edges-after.txt | r21 render-edges-after.txt is the renderer-fixture capture whose SUMMARY states total=4 pass=4, the cell's renderer4/4. |
| L11 | SCORECARD.md:160 | total=29 failed=0 | run: python3 tests/fixtures/r17-census-hygiene.py --census tools/souji-census.sh | Re-running the base cell command at the measured revision prints SUMMARY total=29 failed=0, restating the cell's 29/0 in the fixture's own notation. |
| L12 | SCORECARD.md:161 | total=35 failed=0 | run: bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools | Re-running the base cell command at the measured revision prints SUMMARY total=35 failed=0 skipped=2, restating the cell's 35/0 in the fixture's own notation. |
| L13 | SCORECARD.md:163 | 12/9 | record: census/round-18/final-verification-4800fd7.json | The r18 final-verification record holds the matrix-final run whose command wrote the cited c1-matrix-4800fd7.json, and its r17-base stdout row prints r18-bounded=12/9fail. |
| L14 | SCORECARD.md:163 | 12/0 | record: census/round-18/final-verification-4800fd7.json | The same record's changed-arm stdout row prints r18-bounded=12/0fail at 4800fd7, the post-fix 12/0 the cell states. |
| L15 | SCORECARD.md:163 | 69/0 | record: census/round-18/final-verification-4800fd7.json | The same changed-arm row prints selftest=69/0fail, the census selftest 69/0 the cell states. |
| L16 | SCORECARD.md:164 | pass=61\tfail=0 | record: census/round-18/final-verification-4800fd7.json | The record's gate-selftest check prints SELFTEST\tpass=61\tfail=0, so 61 cases and 0 failed are restated in the record's own JSON-escaped notation. |
| L17 | SCORECARD.md:164 | total=11\tfailed=0 | record: census/round-18/final-verification-4800fd7.json | The record's gate-r18-fixture check prints SUMMARY\ttotal=11\tfailed=0, the pointer fixture 11/0 restated in the record's own JSON-escaped notation. |
| L18 | SCORECARD.md:164 | total=15\tfailed=0 | record: census/round-18/final-verification-4800fd7.json | The record's gate-r16-fixture check prints SUMMARY\ttotal=15\tfailed=0, the r16 fixture 15/0 restated in the record's own JSON-escaped notation. |
| L19 | SCORECARD.md:165 | total=27	pass=27 | record: census/round-21/reason-after.txt | The cited r21 reason-canary receipt's SUMMARY line prints total=27 pass=27 fail=0 leaks=0 base_leaks=19, the synthetic 27/27 the cell states. |
| L20 | SCORECARD.md:165 | total=27	pass=6 | record: census/round-21/reason-oracle-before.txt | The r21 pre-repair oracle receipt of the same 27-case canary against the old tool prints total=27 pass=6 fail=21 leaks=19, the old emissions 6/27. |
| L21 | SCORECARD.md:166 | total=4 failed=0 | run: python3 tests/fixtures/r19-carry-wrap.py | The named fixture still prints 4 cases and 0 failures (2 base-discriminating) at this revision, so the cell's 4/0 is restated in the SUMMARY notation the command emits. |
| L22 | SCORECARD.md:167 | total=11 failed=0 | run: python3 tools/souji-rev-pin.py --selftest | The named helper still prints 11 cases and 0 failures at this revision, so the cell's 11/0 is restated in the SUMMARY notation the command emits. |
| L23 | SCORECARD.md:167 | total=13 failed=0 | run: python3 tests/fixtures/r19-rev-pin.py | The named fixture still prints 13 cases and 0 failures (6 base-discriminating) at this revision, so the cell's 13/0 is restated in the SUMMARY notation the command emits. |
| L24 | SCORECARD.md:168 | 118/0 | record: census/round-21/r20-closure-excerpt.json | The r20 closure recheck retained in r21 states the auditor selftest at 118/0, and no run row is possible because the auditor's file stem does not occur on the base line. |
| L25 | SCORECARD.md:168 | total=17 failed=0 | run: python3 tests/fixtures/r19-seat-audit-shapes.py | The named fixture still prints 17 cases and 0 failures (12 base-discriminating) at this revision, so the cell's 17/0 is restated in the SUMMARY notation the command emits. |
| L26 | SCORECARD.md:168 | 78/0 | record: census/round-21/r20-closure-excerpt.json | The same closure recheck states the r20 oracle at 78/0 with 11 base-discriminating, while the fixture alone prints 66 cases because its 12 baseline cases need an uncommitted baseline auditor copy. |
| L27 | SCORECARD.md:170 | scenarios=3\treplayed=3 | record: census/round-21/final-code-verification.json | The record's matrix stdout for the accepted run states 3 scenarios replayed, with the field tab stored as the two bytes backslash t. |
| L28 | SCORECARD.md:170 | matched=18/18 | record: census/round-21/final-code-verification.json | The same record's matrix stdout states matched=18/18 for each of the three accepted source shapes. |
| L30 | SCORECARD.md:171 | 8/8 | run: python3 tools/souji-declared-evidence.py --selftest | Re-running the base cell command at the measured revision prints selftest=8/8, so the cell literal is shown by a run. |
| L31 | SCORECARD.md:172 | 8/8 | run: python3 tests/fixtures/r23-receipt-run.py | Re-running the base cell fixture at the measured revision prints selftest=8/8, so the cell literal is shown by a run. |
| L32 | SCORECARD.md:173 | 15/15 | run: python3 tests/fixtures/r23-record-agreement.py | The fixture has grown to fifteen cases and prints selftest=15/15, restating the cell's stale 9/9 as the observed count. |
| L33 | SCORECARD.md:174 | cases=12 pass=12 | run: python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py | The debris-census fixture now prints cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED, restating the stale 8/8. |
| L34 | SCORECARD.md:174 | cases=8 pass=4 | record: census/round-24/records/c1-control-stub.tsv | The round-24 lesson cites this stub-control receipt, whose own notation cases=8 pass=4 restates the cell's stub control 4/8. |
| L35 | SCORECARD.md:175 | cases=9 pass=9 | run: python3 -B tests/fixtures/r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py | The fixture requires --tool and prints cases=9 pass=9 control=FALSE-GREEN-REJECTED, so the cell count is shown by a run. |
| L36 | SCORECARD.md:313 | cases=20 pass=20 | run: python3 -B tests/fixtures/r29-registry-agreement.py | Re-running the base cell command at the measured revision prints cases=20 pass=20 control=FALSE-GREEN-REJECTED. |
| L37 | SCORECARD.md:313 | cases=20 pass=8 | record: census/round-29/records/c1-fixture-red-before.txt | The round-29 lesson cites this v1 red-before receipt, whose cases=20 pass=8 restates the cell's v1 tool 8/20. |
| L38 | SCORECARD.md:314 | cases=15 pass=15 | run: bash tests/fixtures/r28-wave-evidence-capture.sh | Re-running the base cell command at the measured revision prints cases=15 pass=15 control=TAMPER-REJECTED. |
| L39 | SCORECARD.md:314 | cases=15 pass=8 | record: census/round-29/records/c2-fixture-red-before.txt | The round-29 lesson cites this base-tool red-before receipt, whose cases=15 pass=8 restates the cell's base tool 8/15. |
| L40 | SCORECARD.md:355 | cases=7 pass=7 | run: python3 -B tests/fixtures/r30-landing-gate-discovery.py --tool tools/souji-landing-gate.py | Re-running the base cell command at the measured revision prints cases=7 pass=7 control=FALSE-GREEN-REJECTED. |
| L41 | SCORECARD.md:355 | cases=7 pass=3 | record: census/round-30/records/c2-fixture-red-before.txt | The cell names this red-before receipt, whose cases=7 pass=3 restates the base gate's 3/7. |

### Round 31 measurements (2026-10-26; base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc; preregistration 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525; amendments ed17ff6d95cc35d95038fdaef0e7e51c8e5d6bfc, 26153a421374db2497e451230f33b2af78b3d128, 6fdd69673e3aec5ef64ce4f9f25f452c4f4447d3, 2c16d018e40db7c23420a2c3bb546b52957bcc25)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 capability-cell literal binding | calibration 7 | `SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34` (22 UNBOUND + 12 RUN-MISMATCH) | at the landing commit and again at the tip `SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1` under v1 and under A2+A4 alike: **missed** the frozen target `unbound=0 mismatches=0` by one item — L29 (`remote-source-after.json18/18`, `SCORECARD.md:170`) states its count only as scalar fields, so no honest binding exists and the row was left out (40 of 41 items carry a row) | `python3 -B tools/souji-capability-cells.py --root <lane> --rev <full40> --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`; v1 = the blob at 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525, same args | `census/round-31/records/c1-before.txt`, `census/round-31/records/c1-after-v1.txt`, `census/round-31/records/c1-after-a4.txt`; landing 24f343c8ffc820c0f89b4252cbdc94ab9a673aab |
| C2 landing-gate reading precision | operability 8 | `SUMMARY fp=13 real=2 cne=0 r26=466 fixture=fail redarm=fail regress=same` (the v3 counter's base control adds `shift=fail`) | at the landing commit and again at the tip `fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same` under v1 and v2, `shift=ok` under v2 and two v3 runs with fresh random probes: **met** (fixture G1-G10 `cases=10 pass=10 control=FALSE-GREEN-REJECTED`; base tool `cases=10 pass=3`, failing G1 G3 G4 G5 G6 G7 G8) | `python3 -B census/round-31/c2-counter.py --root <lane> --rev <full40> --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --fleet-root /home/vgpnk/Projects/shokunin`; `census/round-31/c2-counter-v2.py` (A3 SHIFT) and `census/round-31/c2-counter-v3.py` (A5 random SHIFT), same args | `census/round-31/records/c2-after-v1.txt`, `census/round-31/records/c2-after-v2.txt`, `census/round-31/records/c2-after-v3.txt`; landing 8024b540b04d677d47cf51a0d1132ec8705ef14a |
| C3 F1 dropped-keep-ref object lifetime entry | coverage 8 | v1 `SUMMARY legs=11 fail=10 f1_entries=3`; v2 `SUMMARY legs=12 fail=11 f1_entries=3` | at the landing commit and again at the tip v1 `legs=11 fail=0 f1_entries=4`, v2 `legs=12 fail=0 f1_entries=4`, v3 `legs=13 fail=0 f1_entries=4` (L13's two remover-subtraction mutants differ from the record with strictly fewer `object_present=no` lines): **met** under v1, A0 and A1 | `python3 -B census/round-31/c3-counter.py --root <lane> --rev <full40> --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`; `census/round-31/c3-counter-v2.py` (A0 L12) and `census/round-31/c3-counter-v3.py` (A1 L13), same args | `census/round-31/records/c3-after-c3-counter.txt`, `census/round-31/records/c3-after-c3-counter-v2.txt`, `census/round-31/records/c3-after-c3-counter-v3.txt`; landing 1baf4da02b71b012ee2426ea7c309496c0c3aca0 |

Owned scores unchanged (calibration 7, coverage 8, operability 8): C1 misses its frozen target by one item, so no calibration evidence accrued, and no reproducible 0-10 mapping exists. C2 and C3 hold at their landing commits and at the tip; C1's failure is the round's only unmet target. No round admission is claimed; the non-author closure rules. The final-tip re-measurement of all three claims is committed in the records directory right after this table lands (final-tip-measure.txt) (this seat's tip readings: C1 `unbound=1 mismatches=1`, C2 v1/v2/v3 as above at `2c16d018e40d`, C3 v1/v2/v3 as above at `2c16d018e40d`).

### Round 31 capability rows (appended)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| capability-cell binding audit (r31) | reads the SCORECARD capability cells themselves (not an append-only correction block) and binds each of the 41 enumerated count literals to a run whose command it re-executes from the base blob in a private clone, or to an unchanged record of the row's own round outside `waves/`, `transcripts/`, `sources/` and code suffixes; 40 of 41 cells now carry such a row and the one refusal is reported, not hidden | `python3 -B tools/souji-capability-cells.py --root <lane> --rev 24f343c8ffc820c0f89b4252cbdc94ab9a673aab --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525` -> `SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1` (`census/round-31/records/c1-after-a4.txt`; base `census/round-31/records/c1-before.txt` `unbound=22 mismatches=34`); `census/round-31/c1-cells.tsv` (41 items) | r31 (claim missed: L29 unbound) |
| landing-gate reading precision (r31) | the landing gate reads the committed record as written: it unions `.ufo/waves/round-N/` with `census/round-N/waves/`, reads every `## Seat-reported failures` section including append-only carries (fenced headings are text), and keeps ellipsis placeholders, en-dash and hyphen line ranges, `:text` suffixes, `.captured` capture names, printf templates and prose slash alternations out of the dangling set while a real missing path is still flagged | `python3 -B tests/fixtures/r31-landing-gate-precision.py --tool tools/souji-landing-gate.py` -> `cases=10 pass=10 control=FALSE-GREEN-REJECTED`; the same fixture against the base tool prints `cases=10 pass=3` (`census/round-31/records/c2-after-v1.txt`, its `REDARM` line: G1 G3 G4 G5 G6 G7 G8 FAIL, G2 G9 G10 PASS); reading at the landing commit `fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same` (`census/round-31/records/c2-after-v1.txt`), `shift=ok` in `census/round-31/records/c2-after-v2.txt` and `census/round-31/records/c2-after-v3.txt` | r31 |
| jj dropped-keep-ref object-clock fixture (r31) | a real jj 0.45.1 + git 2.56.0 fixture measuring what keeps an abandoned commit's object present after its own keep ref is gone (a descendant's keep ref, a HEAD reflog entry) and what removes it; the record's 17 `RESULT` lines replay identically, a PATH shim logs 26 jj and 111 git calls including `abandon`, `util gc`, `reflog expire`, `gc` and `cat-file -e`, and neutering either remover changes the outcome | `TMPDIR=<scratch> bash tests/fixtures/r31-jj-object-clock.sh` -> `jj-version: jj 0.45.1-…`, `git-version: git version 2.56.0`, 17 `RESULT arm=… step=… object_present=yes|no` lines byte-identical to `census/round-31/records/jj-object-clock-run.txt`; counter readings v1 `legs=11 fail=10` -> `legs=11 fail=0` (`census/round-31/records/c3-after-c3-counter.txt`), v2 `fail=11` -> `legs=12 fail=0` (`c3-after-c3-counter-v2.txt`), v3 `legs=13 fail=0` (`c3-after-c3-counter-v3.txt`) | r31 |

### Planned (appended at round 31)

- **r32 (planned r31):** calibration: L29's count stays unbound because its record states scalars only (`SCORECARD.md:170`), and the 41-item enumeration is notation-selected — at least two dozen count statements in the same cells stay outside it (`SCORECARD.md:147` `(246 rows)`, `:151` `baseline 33 rows, mined=16 queued=15`, `:161` `tools: 13 fail`, `:168` `(base12)`, `:170` `3/3 each18/18`), while the record rule stays file-granular and cannot tell a supporting sentence from a contradicting one; operability: the gate's tokenizer cannot tell an extension-less prose alternation from a really dangling one (a scratch commit citing `corpus/knowledge/absentdir` and `census/waves` reports neither, while a control `.md` path is reported), its LANE reading counts dangling pointers only and leaves the 54 uncarried seat-failure lines of rounds 15 (1), 19 (3), 23 (10), 24 (17) and 25 (23) to the fixture, and its parse snapshot and selftest still write under `/var/tmp` ignoring `TMPDIR` (`tools/souji-landing-gate.py:1182` and `:1499`, disclosed by wave 1); the dangling pair the never-committed round-3 `garbage-census.out` and the ignored tools `__pycache__` directory stays accepted at the tip by the frozen `real=2`. Certification OFF, K5 HELD.

### Round 32 capability-count bindings (C1, appended; base 85b61a151923986e7e6b48f7084b9122561b5f3d; items `census/round-32/c1-items.tsv`)

| item | base line | literal | binding | reason |
|---|---|---|---|---|
| L29 | SCORECARD.md:170 | 18/18 remote-source-after.json | field: census/round-21/remote-source-after.json expected_command_count=18 matched_command_count=18 | The record's own two command counters are 18 and 18, exactly the 18/18 this cell states. |
| N01 | SCORECARD.md:147 | 246 rows | field: census/round-1/census-summary.json rows_total=246 | r1 commit ab7f2f706f35f466b515b474fc9c76e0ddd71ae2 wrote the cell and its own census-summary.json records rows_total 246 for the 246-row census.tsv. |
| N02 | SCORECARD.md:151 | 33 rows | withdrawn: no cited record holds the baseline 33 rows because verification.json prints the ending census rows 37 | r13 commit 6ed10a7cd6c7b26f8068dd6e02497e860f9c4317 wrote the baseline counts from census/round-13/baseline-measures.md:15, which the cell does not cite; corpus/SOURCES.md at 31984f473ce4bdab61a99b16cca194b28108cb81 still holds 33 rows. |
| N03 | SCORECARD.md:151 | 16 mined | withdrawn: no cited record holds 16 mined since verification.json prints the ending census mined 20 | the same r13 commit took mined 16 from the uncited baseline-measures.md:15 and the cell's pointer verification.json records sources.statuses.mined 20 for its 37-row ending census. |
| N04 | SCORECARD.md:151 | 15 queued | field: census/round-13/verification.json sources.statuses.queued=15 | the cell's own r13 pointer records its sources status histogram queued 15, the value the 31984f473ce4bdab61a99b16cca194b28108cb81 baseline shows. |
| N05 | SCORECARD.md:151 | 2 rejected | field: census/round-13/verification.json sources.statuses.rejected=2 | the same pointer records rejected 2 in that status histogram, matching the 31984f473ce4bdab61a99b16cca194b28108cb81 baseline. |
| N06 | SCORECARD.md:159 | oracle2372 keys | field: census/round-21/oracle-acceptance.json oracle.labelled=2372 | The r21 commit 4eb2fda wrote both this cell and census/round-21/oracle-acceptance.json from one count-read-root.py run, and oracle.labelled is the 2372 independently labelled read-call keys the cell quotes. |
| N07 | SCORECARD.md:159 | files 192 | field: census/round-21/oracle-acceptance.json files=192 | The same r21 JSON top-level files counter is the 192 corpus files the cell quotes over, from the same count-read-root.py measurement. |
| N08 | SCORECARD.md:159 | tp 3 | field: census/round-21/oracle-acceptance.json oracle.tp=3 | The cell's tp3 is the oracle true-positive count recorded in the same r21 JSON (oracle.tp=3) for the same 2372-key measurement. |
| N09 | SCORECARD.md:159 | fp 0 | field: census/round-21/oracle-acceptance.json oracle.fp=0 | The cell's fp0 is the oracle false-positive count recorded in the same r21 JSON (oracle.fp=0), a measured zero rather than an unmeasured absence. |
| N10 | SCORECARD.md:159 | fn 0 | field: census/round-21/oracle-acceptance.json oracle.fn=0 | The cell's fn0 is the oracle false-negative count recorded in the same r21 JSON (oracle.fn=0), same run and key set. |
| N11 | SCORECARD.md:159 | 401 tuples | withdrawn: No observable in the cited census/round-21/oracle-acceptance.json holds 401 as a JSON integer; the 401 old tuples survive only as the length of the prior_verdicts list plus a sha256 digest, while the text record that prints count=401 is oracle-acceptance.txt, a basename the base line does not cite. |
| N12 | SCORECARD.md:161 | failed=0 | run: bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools | Line 161 quotes that exact command; re-run now its SUMMARY prints failed=0, the 13 being the same SUMMARY's failed count with the 5fa6017 tool dir, so the count is restated. |
| N13 | SCORECARD.md:165 | 19 leaks | withdrawn: the only cited occurrence base_leaks=19 sits on reason-after.txt line 29, which N14 already binds, and the counter forbids a shared occurrence |
| N14 | SCORECARD.md:165 | leaks=0 | record: census/round-21/reason-after.txt:29 | reason-after.txt is the record line 165 cites, and its SUMMARY reports the repaired count leaks=0 beside base_leaks=19, the 19 to 0 the cell states. |
| N15 | SCORECARD.md:168 | 18 step | withdrawn: the 18 steps live in census/round-21/step-inventory.json, whose basename line 168 never cites, and no line-named script prints them |
| N16 | SCORECARD.md:168 | base_discriminating=12 | run: python3 -B tests/fixtures/r19-seat-audit-shapes.py | Line 168's r19-seat-audit-shapes17/0 (base12) is this fixture's own SUMMARY, and re-running it now prints base_discriminating=12. |
| N17 | SCORECARD.md:168 | 11 base | withdrawn: the 11 needs the pre-r20 auditor passed as --base-tool, no committed copy of it exists, and line 168 cites no round-20 record |
| N18 | SCORECARD.md:175 | 2 base | withdrawn: census/round-24/records/c2-control-base.tsv line 11 holds mismatches=2 but never the word base, so the A0(b) adjacency the unit demands cannot hold |
| N19 | SCORECARD.md:175 | mismatches=0 | run: python3 -B tools/souji-coverage-agreement.py --root . --rev 778747eb671f8e85ef5387bc3d7023337b30467c | Line 175's c2-after.tsv (0) is this tool's counts line at that rev, and re-running that same argv now prints mismatches=0. |
| N20 | SCORECARD.md:313 | mismatches=10 | withdrawn: the cell cites only the r29 fixture, which prints cases/pass and not this count, and names no record; the sole blob holding mismatches=10 is census/round-29/records/controls.tsv line 2, refused by A0(a) as uncited | line 313 states the r29 C1 before-value as base mismatches=10 but names no record path holding it, so no cited observable exists |
| N21 | SCORECARD.md:313 | mismatches=0 | withdrawn: the cell cites only the r29 fixture, which prints cases/pass and not this count, and names no record; the sole blob holding the after value is census/round-29/records/final-tip-measure-2.txt line 4, refused by A0(a) as uncited | the same row's after value mismatches=0 has no record named on the line |
| N22 | SCORECARD.md:314 | records=1381 | withdrawn: the row names census/round-26/waves, a waves component that record paths forbid, and the blobs holding records=1381 are census/round-29/records/final-tip-measure.txt line 5 and amendments.txt line 35, neither cited on the row | line 314 states records=1381 for the r26 capture but names the captured corpus directory, not the verify record that prints it |
| N23 | SCORECARD.md:314 | failed=0 | withdrawn: the only blobs holding failed=0 for this capture are census/round-29/records/final-tip-measure.txt and amendments.txt, neither cited on the row, and the cited fixture prints cases/pass only | the verify failure count failed=0 is observable only in records the row does not name |
| N24 | SCORECARD.md:314 | uncovered=0 | withdrawn: the only blobs holding uncovered=0 for this capture are census/round-29/records/final-tip-measure.txt and amendments.txt, neither cited on the row, and the cited fixture prints cases/pass only | the uncovered count uncovered=0 is observable only in records the row does not name |
| N25 | SCORECARD.md:354 | k1=13 | withdrawn: the cited blob census/round-30/records/c1-before.txt line 29 does hold k1=13, but no literal can contain the unit k1 and exactly one integer because the unit token itself carries the digit run 1 | the honest literal k1=13 is refused by the literal rule (two digit runs), reproduced as BAD-ROW(literal) |
| N26 | SCORECARD.md:354 | k1=0 | withdrawn: the cited blob census/round-30/records/c1-after-a3.txt line 30 does hold k1=0, but no literal can contain the unit k1 with exactly one integer equal to 0 at all, since k1 carries digit run 1 and any glued form reads 10 | the honest literal k1=0 is refused by the literal rule, reproduced as BAD-ROW(literal) |
| N27 | SCORECARD.md:422 | items=41 | record: census/round-31/records/c1-after-a4.txt:43 | The cell's own post-state record commits this command's SUMMARY at line 43, where items=41 is the item count the cell states. |
| N32 | SCORECARD.md:422 | unbound=22 | record: census/round-31/records/c1-before.txt:43 | The cell names this baseline record, whose SUMMARY line 43 carries unbound=22 for the do-nothing control. |
| N35 | SCORECARD.md:423 | cases=10 | record: census/round-31/records/c2-after-v1.txt:22 | Line 22 is the r31 C2 counter's FIXTURE leg recording the cell's own fixture run, whose cases=10 the cell states. |
| N36 | SCORECARD.md:423 | pass=10 | record: census/round-31/records/c2-after-v2.txt:22 | The v2 run's FIXTURE line records the same fixture output, including pass=10. |
| N37 | SCORECARD.md:423 | cases=10 | record: census/round-31/records/c2-after-v3.txt:22 | The case total is arm-independent and the v3 FIXTURE line records cases=10 for that same fixture. |
| N38 | SCORECARD.md:423 | pass=3 | withdrawn: the base-gate arm's 3 is recorded only in census/round-31/records/c2-fixture-red-before.txt, which this base line does not cite, and that arm exits 1 | No A0-admissible observable shows this base-arm reading. |
| N39 | SCORECARD.md:423 | fp=0 | record: census/round-31/records/c2-after-v1.txt:28 | Line 28 is the r31 C2 counter's landing SUMMARY, whose fp=0 is the false-positive count this cell states. |
| N40 | SCORECARD.md:423 | real=2 | record: census/round-31/records/c2-after-v2.txt:29 | The v2 run's landing SUMMARY line records the same measurement with the SHIFT leg added, including real=2. |
| N41 | SCORECARD.md:423 | cne=0 | record: census/round-31/records/c2-after-v3.txt:30 | The v3 run's first landing SUMMARY line records cne=0 for that same measurement. |
| N42 | SCORECARD.md:423 | 495 | withdrawn: the item's only unit r26 contains a digit, so any literal naming that unit holds two digit runs and the frozen literal rule rejects it, leaving no representable observable | The counter cannot express this item's literal for any binding kind. |
| N43 | SCORECARD.md:424 | 17 RESULT | withdrawn: the 17 is a count of RESULT lines and no cited round-31 record puts 17 adjacent to a result word, so no A0-admissible observable shows it | The record measures this count, but the frozen adjacency rule cannot read it. |

### Round 32 measurements (2026-10-26; base 85b61a151923986e7e6b48f7084b9122561b5f3d; preregistration 3ec84fc81b3243429c834a051880b0bcde06291c; amendments 7a6667cd27652baf8d704b5cdb8e3200bd6e27a1 (A0), a92e1aae91dbf46c2d7eff713932cfc820186970 (A1); attempt 2 after the attempt-1 L1 died, salvage 4e56c48b8fc828f9aba2746e324dc46aa538bdbf)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 capability-count literal binding (44 items: N01-N43 plus r31's L29) | calibration 7 | `SUMMARY items=44 bound_run=0 bound_record=0 bound_field=0 withdrawn=0 unbound=44 mismatches=44` (do-nothing control, v1 and A0 v2) | `SUMMARY items=44 bound_run=3 bound_record=9 bound_field=9 withdrawn=17 unbound=6 mismatches=6` under v1 and v2 at the landing commit and at 4e56c48b8fc828f9aba2746e324dc46aa538bdbf: **missed** (`unbound=0 mismatches=0 withdrawn<=8`); N28-N31, N33, N34 unbound and 17 withdrawals over a cap of 8 — a rule-level miss, the cell integers are correct | `python3 -B census/round-32/c1-counter.py --root <lane> --rev <full40> --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c`; `census/round-32/c1-counter-v2.py` same args | `census/round-32/records/controls.tsv`, `census/round-32/records/c1-after-v1.txt`, `census/round-32/records/c1-after-v2.txt`, `census/round-32/records/a2-l1-salvage-tip-measure.txt`; landing 9e8982b7a6ac57dffa415f9db43cf7cd6e829c93 |
| C2 lane-tool scratch discipline (27 items over 22 files) | operability 8 | `SUMMARY items=27 pass=1 fail=26` | landing record `pass=26 fail=1` (T18), not reproduced: two wave a2w1 full runs at the landing commit and the L1 at 4e56c48b8fc828f9aba2746e324dc46aa538bdbf read `pass=25 fail=2` (T12, T18): **missed** (`fail=0`); T18's anchor counts closure files changed since a pinned revision, T12's base flips under load | `python3 -B census/round-32/c2-counter.py --root <lane> --rev <full40> --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c` | `census/round-32/records/c2-after-v1.txt`, `census/round-32/records/a2-l1-salvage-tip-measure.txt`, `.ufo/waves/round-32/a2w1/SwarmExecutor08.md`; landing 98e5203d45b4e419a9e72801733d93303acc7ebd |
| C3 F1 abandoned-object mtime clock entry | coverage 8 | `SUMMARY legs=14 fail=13 f1_entries=4` | v1 `SUMMARY legs=14 fail=0 f1_entries=5`, A1 v2 `SUMMARY legs=17 fail=0 f1_entries=5` at the landing commit and at 4e56c48b8fc828f9aba2746e324dc46aa538bdbf: **met**; 15 append-only correction bullets in the entry after wave a2w1 | `python3 -B census/round-32/c3-counter.py --root <lane> --rev <full40> --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c`; `census/round-32/c3-counter-v2.py` same args | `census/round-32/records/c3-after-v1.txt`, `census/round-32/records/c3-after-v2.txt`, `census/round-32/records/a2-l1-salvage-tip-measure.txt`; landing a92e1aae91dbf46c2d7eff713932cfc820186970 |

Owned scores unchanged (calibration 7, coverage 8, operability 8): C1 and C2 missed, so no calibration or operability evidence accrued, and no reproducible 0-10 mapping exists. C2's landing also harmed three committed gate surfaces and one write-scope guard; attempt 2 repaired all four before integration (`census/round-32/records/a2-repairs.txt`), reverting `tools/souji-evidence-cache.py` and so C2 item T08. The final-tip readings of all three claims are committed in `census/round-32/records/final-tip-measure.txt` right after the integration. No round admission is claimed; the non-author closure rules.

### Round 32 capability rows (appended)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| sandboxed scratch-discipline counter (r32) | runs a lane command at a base revision and, from a private clone at a measured revision, under bwrap with `/tmp`, `/var/tmp` and `/dev/shm` read-only and `TMPDIR` a fresh scratch dir, both under `strace -f`; passes an item only when the sandboxed run prints the base exit code and last digit-bearing line and keeps at least half of base's file-creating syscalls. It does not see consumers that pin a tool's digest, and a clone-local scratch passes it (w1 `SwarmCritic34.md`) | `census/round-32/c2-counter.py`; base `SUMMARY items=27 pass=1 fail=26` (`census/round-32/records/controls.tsv`) | r32 |
| jj mtime-clock fixture (r32) | real jj 0.45.1 + git 2.56.0 arms recent, old, mixed, never and nocruft that measure where an abandoned commit's object survives a `git gc` (loose, cruft pack, absent) as its island's mtime and `gc.pruneExpire` / `gc.cruftPacks` vary; the record replays byte-identically and a PATH shim proves the binaries ran | `TMPDIR=<scratch> bash tests/fixtures/r32-jj-mtime-clock.sh` -> 22 `RESULT` lines equal to `census/round-32/records/jj-mtime-clock-run.txt`; `census/round-32/records/c3-after-v2.txt` | r32 |
| record-contract check (r32, M1) | checks every record line under a contract's prefix for exact keys in order and values in enumerated sets; fails the r31 record's `arm=reflog-only` lines. Literal-prefix: a mixed record with a `RESULT:` line passes (a2w1 `SwarmCritic26.md`) | `python3 -B tools/souji-record-contract.py --record census/round-31/records/jj-object-clock-run.txt --contract census/round-32/m1-r31-contract.txt` -> `lines=17 bad=4`, exit 1 (`census/round-32/records/m1-red-before.txt`) | r32 |
| receipt out-guard under TMPDIR (r32 attempt 2) | `tools/souji-receipt-run.py` refuses the scratch root itself as `--out` and, with `TMPDIR` set, a scratch root or receipt directory inside a git work tree (`OUT-IN-GIT-TREE`), after every base refusal | `census/round-32/records/a2-repairs.txt` R1 (old tool rc 0 into the fleet root, new rc 2; receipt fixtures unchanged) | r32 |

### Planned (appended at round 32)

- **r33 (planned r32):** calibration: rebuild the capability-count enumeration per count statement with digit-free unit words and shared lines, prove a pre-freeze feasibility leg (QUALITY Q70) before data, and re-derive the 6 unbound and 17 withdrawn r32 items under it; operability: close the C2 predicate gaps (clone-local scratch, zero-case runs, digest-pinned consumers per Q73), restage `census/round-21/run-acceptance.py`'s cache-tool pin so `tools/souji-evidence-cache.py` can take `TMPDIR`, fix the trailing-slash `TMPDIR` regressions, the two remaining literal `/var/tmp` scripts and M1's literal-prefix scope; coverage: F1's unread `.mtimes` contents or the cruft call's argv, or another frontier surface. Certification OFF, K5 HELD.

### Round 33 capability currency (C1, appended; base 6017a482e7068d5afb7617640198fbb0fe743357; items `census/round-33/c1-items.tsv`; rules and cause execution in `census/round-33/c1-counter.py`)

Each row restates one capability row whose named command no longer produces (or never produced) its stated outcome; the original row above stays as written. Drafted and proved by wave-1 seats RestateK04, RestateK05, RestateK16, RestateK17 and RestateK18 (their receipts are part of the round-33 wave capture); all five changes are growth or a documentation defect, none a lost capability.

| id | row | status | exit | run | statement | cause | reason |
|---|---|---|---|---|---|---|---|
| K04 | SCORECARD.md:155 | restated | 0 | same | `selftest=PASS ids=7/7` | 728b2ce71acbe574ae3036b456724d0a3d6f8f08 | selftest grew from 5 to 7 cases at 728b2ce: round-25 added the linked-common-dir and colocated-vs-plain probe cases, all PASS |
| K05 | SCORECARD.md:158 | restated | 0 | same | `SELFTEST pass=65 fail=0` | ddb73474433977ff54b015ac3e77669ff2537353 | selftest grew from 18 to 28 cases at ddb7347 (round-17 D6 gate exact ids and replays; the fenced-and-table-ignored case was renamed benign-status-words with a stricter status_lines count), and to 65 cases by 2d9bca55, all passing |
| K16 | SCORECARD.md:173 | restated | 0 | same | `selftest=15/15` | 1dd8b1e30a971e662480b49bedf1000667fbddea | selftest grew from 9 to 11 cases at 1dd8b1e (K3 class-missing and K2 tally-stale-log fixtures added; r25 growth took the base run to 15), all 15 pass and the control line still reads FALSE-GREEN-REJECTED |
| K17 | SCORECARD.md:174 | restated | 0 | same | `cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` | 679e2d02f46ec06447d679d9395d6592c5e35f5c | selftest grew from 8 to 12 cases at the round-25 bare and refusal edge-case commit: cases 9-12 added, all pass |
| K18 | SCORECARD.md:175 | restated | 0 | `python3 -B tests/fixtures/r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py` | `cases=9 pass=9 control=FALSE-GREEN-REJECTED` | 07f83e69979b1032f9de4fe876739a8dccc7242b | the r26 row wrote the fixture without its required --tool argument; with the tool the fixture prints its 9/9 summary |

### Round 33 measurements (2026-10-26; base 6017a482e7068d5afb7617640198fbb0fe743357; preregistration 2d9bca55a9f042a2c9ed60a797a8069e74c41f46; controls 3aec290ea5c4f3fe7f12a54e5b18e8072826ff92; no amendment)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 capability-table currency (24 items K01-K08, K11-K26) | calibration 7 | `SUMMARY items=24 agree=19 mismatches=5 restated=0` (do-nothing, `census/round-33/records/controls.txt`) | `SUMMARY items=24 agree=24 mismatches=0 restated=5` at the landing commit and at the C2 repair commit: **met on the frozen counter**; the five cells were already restated at r30 (R04 R05 R14 R15 R16) and r31 (L05 L06 L32 L33 L35), so the gain is executed cause provenance, not a new correction (lesson M3, Q76); tip reading in `census/round-33/records/final-tip-measure.txt` | `flock <scratch>/c1.lock python3 -B census/round-33/c1-counter.py --root <lane> --rev <full40> --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --scratch <dir>` | a416d0b26495ce78b76ea82316533bd8a9ef368c (`census/round-33/records/c1-at-landing.txt`); a7c35c24bdd8bae5cff9766ace02a81915756701 (`c1-at-c2-repair.txt`) |
| C2 routed scratch-discipline repairs (O1-O5, guards G1-G6) | operability 8 | `SUMMARY legs=11 pass=0 fail=5 harm=0` | `SUMMARY legs=11 pass=3 fail=2 harm=0` at the C2 landing commit: **missed** (target `pass=5 fail=0 harm=0`); O3 needs the NAMESPACE-held r14 fixture repaired (lesson M5, Q78), O4's census selftest anchor flips run to run | `python3 -B census/round-33/c2-counter.py --root <lane> --rev <full40> --base 6017a482e7068d5afb7617640198fbb0fe743357 --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --scratch <dir>` | 756d77f0ccba35585055cc5cb4468028a6fbff5f (`census/round-33/records/c2-at-landing.txt`); repair commit a7c35c24bdd8bae5cff9766ace02a81915756701 (`c2-at-repair.txt`) |

Owned scores unchanged (calibration 7, coverage 8, operability 8): C2 missed, and C1's met reading moves cells the lane had already corrected, so no calibration evidence accrued that a reproducible 0-10 mapping could credit. Score delta 0 on every axis. No round admission is claimed; the non-author closure rules.

### Round 33 capability rows (appended)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| capability-table currency counter (r33) | re-runs 24 capability-row commands at a measured revision in private clones and checks each row's stated outcome, or an appended restatement whose cause commit it executes (value drift: original holds at the cause's parent and fails at the cause; argv correction: the cause wrote the row and its argv already failed); the statement may be any digit-bearing output line and `--only` prints a partial pass (wave-1 `SwarmCritic26`), so a reading needs the quoted lines checked | `python3 -B census/round-33/c1-counter.py --root <lane> --rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --scratch <dir>` -> `SUMMARY items=24 agree=19 mismatches=5 restated=0` (`census/round-33/records/controls.txt`); at a416d0b26495ce78b76ea82316533bd8a9ef368c `mismatches=0 restated=5` (`census/round-33/records/c1-at-landing.txt`) | r33 |

### Planned (appended at round 33)

- **r34 (planned r33):** calibration: a before-state that honours the lane's own correction rows (Q76) — e.g. the gate-registry and non-capability rows wave-1 `SwarmScout25` found stating runnable outcomes outside any correction (67 rows classified); harden the C1 counter (statement tied to the row's summary line, exit fixed, no vacuous `RESULTS`, argv correction runs the row's own script); operability: an operator ruling (or a held-pin-respecting design) for the r14 namespace fixture's literal `/var/tmp` root behind O3, a load-stable anchor for the census selftest (O4), a work witness and junk control for `sandbox-nt`; run the 37 unrun wave-2 attack items (`.ufo/waves/round-33/make-spec-w2.py`). Certification OFF, K5 HELD, NAMESPACE hold unchanged.

### Round 34 registry restatements

| E04 | SCORECARD.md:21 | restated | 1 | `python3 -B tools/souji-landing-gate.py --root . --rev de478b483db66a8d8ff2d627cde1ccce6e21a014 --round 28 --fleet-root /home/vgpnk/Projects/shokunin` | `SUMMARY findings=19 checked_reg=52 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=19 status_lines=58 carry_heading=0 checked_reports=61` | fec846dd1781a414ae3a7d71d2d8fa2fb17900eb | r30 made the pinned r28 gate resolve its wave reports; it now exits 1 with 19 uncarried reports rather than the pre-r30 CNE |
| E18 | SCORECARD.md:71 | restated | 0 | same | `selftest=PASS ids=7/7` | 728b2ce71acbe574ae3036b456724d0a3d6f8f08 | r25 added two passing repo-structure probes, so the same argv prints 7/7 while the r24 recheck cell kept 5/5 |
| E23a | SCORECARD.md:304 | restated | 0 | `python3 -B census/round-29/c2-counter.py --root . --rev b86200714069022954a3b498cf697d894119b45e` | `SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0 rev=b86200714069022954a3b498cf697d894119b45e` | de874ee86fcaee212bbf4a9bfa4bf49d953ccb8b | the row was written with r29's own waves manifest, making manifests 4 at its cause; pinning the row's named revision preserves its stated reading |
| G23 | SKILL.md:247 | restated | 1 | `python3 -B census/round-29/c2-counter.py --root . --rev 9c76c7222a8abff027af42e37f0d160d52526bba` | `SUMMARY manifests=8 failed=0 uncovered=1 floor_violations=0 rev=9c76c7222a8abff027af42e37f0d160d52526bba` | 1dc678500c92164b0b2bea82b934dd03d1dfbf38 | the row's authoring commit wrote both its own r29-c2-counter entry and the preceding SKILL row named by the frozen where cell; pin the argv to base and disclose the one-line-low cell |
| E05 | SCORECARD.md:23 | restated | 0 | `bash tests/fixtures/r28-wave-evidence-capture.sh 2>/dev/null` | `cases=15 pass=15 control=TAMPER-REJECTED` | fec846dd1781a414ae3a7d71d2d8fa2fb17900eb | the r28 fixture writes expected negative-case diagnostics after stdout; redirecting stderr preserves the same script and binds its current 15-case summary |

### Round 34 measurements

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 registry/outcome agreement (60 frozen items) | calibration 7 | `SUMMARY items=60 agree=35 mismatches=25 restated=0` at base 9c76c72 (`census/round-34/records/controls.txt`) | **MISSED / no full landing read claimed.** Five individually validated corrections E04/E05/E18/E23a/G23 landed; W2 independently validated E05 and G23, while W1/W2 reproduced unreachable frozen rows/predicates (G05/G17b/G24/E23b/E26) and false-cause acceptances (G17a/G21), so `agree=60` is not claimable. Counter attack and remaining mismatch receipts are in the committed wave capture. | `python3 -B census/round-34/c1-counter.py --root <lane> --rev <full40> --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 --scratch <dir>`; `--only` is diagnostic, never a full pass | five targeted restatements individually validated in W1/W2 scratch probes; no full landing measurement or C1 target |
| C2 sandboxed operability (13 frozen legs) | operability 8 | CNE exit 2 at base because `census/round-34` legs absent at base (`controls.txt`) | **MISSED:** repaired feasibility at rev 60def78 reported `SUMMARY legs=13 pass=9 fail=4 harm=0` (W2/W3/N3/J1 fail); no final-tip pass is claimed. | `python3 -B census/round-34/c2-counter.py --root <lane> --rev <full40> --base 9c76c7222a8abff027af42e37f0d160d52526bba --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 --scratch <dir>` | repair/re-pin 2b0171e2071fdc9c16a69bed12b0d040e574d8c8; feasibility rev 60def78 |

Scores unchanged (calibration 7, operability 8, coverage 8): no frozen claim target was met; the five C1 restatements are partial corrections, not a score increase. No C2 passing outcome is claimed.

### Planned (appended at round 34)

- **r35:** repair the C1 enumerator/counter binding defects before data (tab-aware predicate matching, exact row-line binding, reachable item revisions/files, and a wildcard-exit mutation); re-preregister and dry-run every item to target under the final counter. Rework C2's W2/W3/N3/J1 legs so the actual sandbox contract, fixture case count, scratch normalization, witness and junk timeout are feasible under load, then run the full feasibility and mutation controls before freezing. Carry all unrun/failed W2 attacks and all unresolved r34 C1 mismatches. Certification OFF, K5 HELD, NAMESPACE hold unchanged.
 
### Round 35 measurements (wave closure pending)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 registry/outcome agreement (60 items) | calibration 7 | `SUMMARY items=60 agree=37 unresolved=23 mismatches=23 withdrawn=0 restated=5` (do-nothing, instrument rev) | Pending final wave integration; no target/pass claimed | `python3 -B census/round-35/c1-counter.py --root . --rev <landing> --list-rev 4e9c295e9339cc2b13f7a0dd5ec9fc8213a9e18e --scratch <dir>` | pending |
| C2 sandboxed operability (13 legs) | operability 8 | CNE rc 2 at pre-instrument tip | Pending final wave integration; feasibility W1/N4 pass, N3 and W2 fail; no target/pass claimed | `python3 -B census/round-35/c2-counter.py --root . --rev <landing> --base 1e9cad0b553891c41fe5b7ad1686decc147d76d4 --list-rev 4e9c295e9339cc2b13f7a0dd5ec9fc8213a9e18e --scratch <dir>` | pending |
| C3 F1 fleet exposure numerator | coverage 8 | no r35 entry / prior dated numerator | Frozen counter mechanically reported `SUMMARY entries=1 legs=6 fail=0` at `fedfa4068801164ac2e189029137ebe87a1d94d3`, but W1/W2 falsified its data: direct-root replay gives 22 repos, 23 registrations, 1 prunable; original record has four phantom paths and counts dry-run stdout instead of stderr. L5 accepts mismatched figures by substring. Substantive target **missed**; mechanical PASS is not evidence of the frozen figures. | `python3 -B census/round-35/c3-counter.py --root . --rev fedfa4068801164ac2e189029137ebe87a1d94d3 --list-rev 4e9c295e9339cc2b13f7a0dd5ec9fc8213a9e18e` | `fedfa4068801164ac2e189029137ebe87a1d94d3` |

No round-level admission or score increase is declared while W1/W2 remain unsettled; owned scores remain calibration 7, operability 8, coverage 8 pending non-author closure.

### Round 36 measurements (2026-10-28; base 94b5e96ab72b40622449af2dfe7c5b6d73118176; preregistration + instruments + controls frozen at 42ea92e999cd8f1a01d2c28f5f7c9b884321ef78)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 coverage-map binding | calibration 7 | `grounded=19 mapped=18 dangling=0 mismatches=1`, rc 1 — MISSING-FROM-MAP `corpus/knowledge/fleet-prune-numerator-r35.md` ground=F1 map_rows_F1=2 (`census/round-36/records/c1-control-base.txt`) | `grounded=19 mapped=19 dangling=0 mismatches=0 kill_tested=19 kill_violations=0`, rc 0 (`census/round-36/records/c1-after.txt`): the F1 map row names the r35 entry and the F1 frontier bullet records the numerator held and re-runnable | `python3 -B tools/souji-coverage-agreement.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <full40> --base-rev 94b5e96ab72b40622449af2dfe7c5b6d73118176` | after `af7d51a180eaf2424e064e8e9f19085beff3637e` |
| C2 report-contract gate | operability 8 | base revision has no `tools/souji-report-contract.py` (`git cat-file -e` rc 128) and the base gate scores the new fixture `cases=11 pass=0 fail=11`, rc 1 (`census/round-36/records/c2-control-base.txt`) | `SUMMARY cases=11 pass=11 fail=0 control=STUB-REJECTED`, rc 0; r27 regression `cases=4 pass=4 control=FALSE-GREEN-REJECTED`, rc 0; checker selftest `cases=8 pass=8` (`census/round-36/records/c2-after.txt`). The checker flags the r35 filed report 4/7 predicates (sections, trends, stale-lane, measurements) exactly as the r35 spot-check found (`census/round-36/records/c2-filed-reports.txt`) | `python3 -B tests/fixtures/r36-report-gate.py`; `bash tests/fixtures/r27-pre-report-gate.sh` | after `42ea92e999cd8f1a01d2c28f5f7c9b884321ef78` (instruments) |
| C3 F1 worktree-drift surface | coverage 8 (capability acquisition) | tool absent at base (`git cat-file -e 94b5e96:tools/souji-worktree-drift.py` rc 128, `census/round-36/records/c3-control-base.txt`) | `SUMMARY cases=9 pass=9 fail=0 control=STUB-REJECTED`, rc 0; live run `record_repos=26 record_regs=27 record_prunable=0 live_repos=22 live_regs=23 live_prunable=1 drift_rows=5 unreachable=0`, the ABSENT set exactly `ok,research,scripts,templates` = the r35 spot-check's four phantom paths (`census/round-36/records/c3-after.txt`) | `python3 -B tests/fixtures/r36-worktree-drift.py`; `python3 -B tools/souji-worktree-drift.py --root /home/vgpnk/Projects/shokunin --record census/round-35/records/prune-census.tsv --timeout 20` | after `42ea92e999cd8f1a01d2c28f5f7c9b884321ef78` (instruments) |

Owned score values are unchanged (calibration 7, operability 8, coverage 8): the lane still has no
reproducible 0–10 mapping from a verdict to a number, so these rows carry the measurements and the
verdict rather than a number. No axis is harmed: no predicate, counter or record was weakened, the
r27 gate regression is unchanged, and the r35 census record is left as filed.

### Round 36 capability rows (appended)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| report-contract gate (r36) | refuse to file a round report that lacks the canonical section order, one SHONEN line per SHONEN.md box, one verdict line per learning trend, a stale-lane line, a measurement row with a counting command and a measured commit, 1–3 claim ids, or an evidence pointer; without `--contract` the run prints `check-report-contract=SKIPPED` so the omission is visible | `python3 -B tools/souji-report-contract.py --report <filed report> --shonen <lane>/SHONEN.md` and `python3 -B tests/fixtures/r36-report-gate.py` -> `SUMMARY cases=11 pass=11 fail=0 control=STUB-REJECTED` (`census/round-36/records/c2-after.txt`); discrimination on filed reports `census/round-36/records/c2-filed-reports.txt` | r36 |
| F1 worktree-drift detector (r36) | re-measure every repository a committed census record names, read-only (`worktree prune` only with `--dry-run -v`, candidates counted from stderr), and report REGS-CHANGED / PRUNABLE-CHANGED / ABSENT / UNREACHABLE / UNRECORDED drift against the record; refuses a malformed or empty record with a typed exit 2 | `python3 -B tools/souji-worktree-drift.py --root /home/vgpnk/Projects/shokunin --record census/round-35/records/prune-census.tsv` -> `SUMMARY ... drift_rows=5 unreachable=0` (`census/round-36/records/c3-after.txt`); `python3 -B tests/fixtures/r36-worktree-drift.py` 9/9 with a rejected always-equal stub | r36 |

### Planned (appended at round 36)

- **r37 (planned r36):** calibration: give the coverage-map counter a written 0–10 mapping (what
  each mismatched row costs) before citing a number, then test the four rejected-row `used-by`
  findings the r36 wave reported; operability: retire or tighten the `--contract` opt-in (the
  wave tests whether a caller can silently skip it), and repair whatever the wave's predicate and
  mutation probes falsify; coverage: move the drift tool's live numerator into a dated record of
  its own so F1 has a current reading rather than a record plus a drift report. Certification OFF,
  K5 HELD, NAMESPACE hold unchanged.

### Round 36 amendment supersessions (appended 2026-10-28; the rows above stand as written)

The Round 36 measurement rows recorded the targets frozen before wave 1. Four tighter-only
amendments (A1–A4, each named in `census/round-36/preregistration.txt` with the wave seat that
produced it) changed what the fixtures carry, never what they require:

| claim | superseded target | current target | why | receipt |
|---|---|---|---|---|
| C2 | `cases=11 pass=11 fail=0 control=STUB-REJECTED` | `cases=21 pass=21 fail=0 control=STUB-REJECTED` (+ `control=VACUOUS-CHECKER-REJECTED`) | A1 guarded an empty code span; A2 bound the gate verdict on rc AND the absence of a printed `=FAIL` and forwarded diagnostics; A3 made `sections` fence/comment-aware and exact-normalized and added isolated `evidence-*` cases that kill five measured mutants (SwarmMutationTester13/14); A5 refused a vacuous checker and namespaced forwarded lines (SwarmExecutor15); A7 reads the trend verdict as the first token after its label (SwarmConnector39). The checker's selftest grew 8 -> 9 cases. | `census/round-36/records/c2-after.txt` |
| C3 | `cases=9 pass=9 fail=0 control=STUB-REJECTED` | `cases=12 pass=12 fail=0 control=STUB-REJECTED` | A2 refused `--json` inside the measured root and scrubbed `GIT_TRACE*`/`GIT_FLUSH` (SwarmSentinel24); A4 fixed the `live_repos` arithmetic that could go negative (SwarmExecutor22 F1) | `census/round-36/records/c3-after.txt` |
| C1 | counter alone (`mismatches=0`) | counter **plus** the strict path probe (`distinct=27 missing=0 nested_entries=0`) | SwarmCritic07's W2/W3 showed the counter's resolution check is basename-only; the claim's resolution clause is carried by the probe and the counter's limit is reported (QUALITY Q80) | `census/round-36/records/c1-strict-paths.txt` |

Every current target was met at the round landing revision; the earlier rows' numbers remain as
measured at the freeze. Owned scores unchanged (calibration 7, operability 8, coverage 8).

### Round 37 receipt reconciliation (appended 2026-10-28)

The r36 non-author spot-check routed self-assessment cells whose after-values never lived in a
committed receipt (`corpus/lessons/round-36-verifier-spotcheck.md`, Routed defects 1). The r36
measurement rows above stand byte-verbatim (append-only); these rows carry the receipt-backed
value, its receipt path and a commit at which that receipt exists. No r36 predicate was relaxed.

| row | names | corrected value | receipt (commit) |
|---|---|---|---|
| R37-C1-1 | SCORECARD.md:563 (r36 C2 after cell) | `SUMMARY cases=21 pass=21 fail=0 control=STUB-REJECTED` | `census/round-36/records/c2-after.txt` @ `1e771ed59301ed10f68e22d4edf35d5218bacf1a` |
| R37-C1-2 | SCORECARD.md:564 (r36 C3 after cell) | `SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED` | `census/round-36/records/c3-after.txt` @ `1e771ed59301ed10f68e22d4edf35d5218bacf1a` |
| R37-C1-3 | SCORECARD.md:575 (report-contract capability row) | `SUMMARY cases=21 pass=21 fail=0 control=STUB-REJECTED` | `census/round-36/records/c2-after.txt` @ `1e771ed59301ed10f68e22d4edf35d5218bacf1a` |
| R37-C1-4 | SCORECARD.md:576 (drift-detector capability row) | `SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED` | `census/round-36/records/c3-after.txt` @ `1e771ed59301ed10f68e22d4edf35d5218bacf1a` |
| R37-C1-10 | SCORECARD.md:563 (r36 C2 after cell, checker selftest arm) | `SUMMARY cases=9 pass=9`, rc 0 | `census/round-36/records/c2-after.txt` @ `1e771ed59301ed10f68e22d4edf35d5218bacf1a` |
| R37-C1-11 | SKILL.md:247 (report-contract selftest count, corrected in place) | `cases=9 pass=9` | `census/round-36/records/c2-after.txt` @ `1e771ed59301ed10f68e22d4edf35d5218bacf1a` |

The two measured-commit cells in the r36 C2/C3 rows name `42ea92e` (the freeze commit), where
neither receipt exists (`git cat-file -e` rc 128 for both). The receipts first exist at `007ab53`
(20/20 and 12/12) and are current at `1e771ed` (21/21 and 12/12, after amendment A7 refreshed
C2); the reconciliation rows above name the current one.

### Round 37 measurements (2026-10-28; base 0d974ffcb7dfb70617947531cab2d7e96cd8f9fd; preregistration + counters frozen at d5c6498c5f72a63c9df32b26ee143e8d775eebbd)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 receipt-citation reconciliation | calibration 7 | `SUMMARY cells=11 mismatches=11`, rc 1 — the receipts resolve at the base revision but no correction line exists (`census/round-37/records/c1-before.txt`) | `SUMMARY cells=11 mismatches=0`, rc 0 — eleven register rows: each anchored line carries the receipt-backed value and names its receipt, and the receipt blob at `1e771ed` carries the same token (`census/round-37/records/c1-after.txt`) | `python3 -B tools/souji-citation-reconcile.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <full40> --register census/round-37/citation-cells.tsv --register-rev <full40>`; fixture `python3 -B tests/fixtures/r37-citation-reconcile.py` -> `cases=16 pass=16 fail=0 control=FALSE-GREEN-REJECTED` (`census/round-37/records/c1-fixture-after.txt`), register pinned with `--register-rev` | 0be9bd0bf0c8143483bc4da609a6225b2c47ab64 |
| C2 drift-tool write envelope | operability 8 | the r36 tool bytes reproduce six escapes: `cases=12 pass=3 fail=9 base_fail=9 escapes=9`, rc 1 (`census/round-37/records/c2-before.txt`) | `cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED`, rc 0 (`census/round-37/records/c2-after.txt`); consumers stay green: r36 drift fixture 12/12, r36 report-gate fixture 21/21, r27 gate 4/4 (`census/round-37/records/consumers-after.txt`) | `python3 -B tests/fixtures/r37-drift-escapes.py --base-tool <1e771ed blob>`; `python3 -B tools/souji-worktree-drift.py --root /home/vgpnk/Projects/shokunin --record census/round-35/records/prune-census.tsv --timeout 20` | 0be9bd0bf0c8143483bc4da609a6225b2c47ab64 |
| C3 drift fixture discrimination | coverage 8 | the battery against the r36 fixture blob: `mutants=6 killed=4 survived=2` — the routed `live_repos` survivor and the `drift_rows` mutant pass 12/12 (`census/round-37/records/c3-before.txt`) | `mutants=6 killed=6 survived=0`, rc 0 against `tests/fixtures/r37-drift-discrimination.py` (`census/round-37/records/c3-after.txt`); the r36 fixture stays byte-identical and 12/12 | `python3 -B tests/fixtures/r37-drift-mutants.py --fixture tests/fixtures/r37-drift-discrimination.py` | 0be9bd0bf0c8143483bc4da609a6225b2c47ab64 |

Owned score values are unchanged (calibration 7, operability 8, coverage 8): the lane still has no
reproducible 0–10 mapping from a verdict to a number, so these rows carry the measurements and the
verdict rather than a number. No axis is harmed: no predicate, counter or record was weakened, the
r36 fixture files are byte-identical, and the r35 census record is left as filed.

### Round 37 capability row (appended)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| self-assessment receipt reconciliation (r37) | read a register of quoted self-assessment cells at a named revision and re-derive both arms — one anchored line carrying the receipt-backed value and not the stale token, and the receipt blob at a commit where it exists carrying the same token; refuses malformed registers and non-40-hex revisions; read-only git plumbing | `python3 -B tools/souji-citation-reconcile.py --root <lane> --rev <full40> --register census/round-37/citation-cells.tsv --register-rev <full40>` -> `cells=11 mismatches=0` (`census/round-37/records/c1-after.txt`); `python3 -B tests/fixtures/r37-citation-reconcile.py` -> `cases=16 pass=16 fail=0 control=FALSE-GREEN-REJECTED` | r37 |

### Round 38 receipt reconciliation (appended 2026-10-28)

The round-37 non-author spot-check routed receipt/revision pairings (defects 2 and 7) and residual
stale counts (defect 3) in the lane's own self-assessment cells, and the r37 lesson named the missing
commit arm. The r37 rows above stay byte-verbatim (append-only); each row below names the receipt, a
commit at which that receipt carries the value, and the r38 counter that now binds both
(`tools/souji-citation-reconcile.py` with the optional eighth `commit` cell). The r37 report's own
cells are fleet-repo bytes outside this lane's write scope: they are carried as an errata section in
the round-38 report, not claimed here.

| row | route | corrected value, receipt at a named commit |
|---|---|---|
| R38-C1-1 | r37 C2 after cell | `census/round-37/records/c2-after.txt` @ `02b4339` carries `escapes=9`; the before column's "six escapes" phrasing and the four-case draft are superseded |
| R38-C1-2 | r37 C2 before cell | `census/round-37/records/c2-after.txt` @ `02b4339` carries `base_fail=9`, the final fixture's base arm rather than the six-case draft's |
| R38-C1-3 | r37 C3 after cell | `census/round-37/records/c3-after.txt` @ `bbefcee` carries `killed=6` |
| R38-C1-4 | r37 C3 before cell | `census/round-37/records/c3-after.txt` @ `bbefcee` carries `survived=0`, the after value the before column's pair is read against |
| R38-C1-5 | r37 C1 after cell | `census/round-37/records/c1-fixture-after.txt` @ `b491596` carries `cases=16`, the grown fixture count the row's twelve-case reading predates |
| R38-C1-6 | r37 C1 after cell | `census/round-37/records/c1-after.txt` @ `02b4339` carries `mismatches=0` |

### Round 38 measurements (2026-10-28; base `ca4369a9296011644636711a624da6a8074e8e2a`; preregistration `4090ee5b04ca3205d61c044b89fd9f318cf9850c`; landing `2843805d4631b040219ed1ba60053035b5a86f07`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 commit-arm citation reconciliation | calibration 7 | `SUMMARY cells=10 mismatches=10`, rc 1 — no correction line exists at the base (`census/round-38/records/c1-before.txt`) | `SUMMARY cells=10 mismatches=0`, rc 0: ten anchored lines name their receipt and a commit where the receipt carries the value; the vacuity control reads `mismatches=9`, rc 1 (`c1-vacuity2.txt`) | `python3 -B tools/souji-citation-reconcile.py --root . --rev <full40> --register census/round-38/cells.tsv --register-rev 4090ee5b04ca3205d61c044b89fd9f318cf9850c`; fixture `python3 -B tests/fixtures/r38-citation-commit.py` -> `cases=14 pass=14 fail=0 control=FALSE-GREEN-REJECTED` | `2843805d4631b040219ed1ba60053035b5a86f07` (`c1-after2.txt`) |
| C2 drift write envelope | operability 8 | the r37 blob hangs on a FIFO `--json` (rc 124 under `timeout 8`), overwrites its own record with JSON and exits 0, and documents four fewer classes; the fixture's base arm itemises the six failing cases (`census/round-38/records/c2-before.txt`) | `SUMMARY cases=12 pass=12 fail=0 base_cases=12 base_fail=6`, rc 0: `O_NONBLOCK` open with an `S_ISREG` refusal, `JSON-IS-RECORD` by path and inode, and a docstring enumeration read through `ast` + comment-stripped code (`c2-after2.txt`) | `python3 -B tests/fixtures/r38-drift-write-envelope.py --base-tool <git show ca4369a:tools/souji-worktree-drift.py>` | `2843805d4631b040219ed1ba60053035b5a86f07` (`c2-after2.txt`) |
| C3 record-validation discrimination | coverage 8 | the r37 discrimination fixture kills none of the four record mutants: `mutants=4 killed=0 survived=4 pristine=ok` (`c3-before.txt`) | `cases=10 pass=10 fail=0` and `mutants=4 killed=4 survived=0 pristine=ok base_killed=0`, rc 0 (`c3-after2.txt`) | `python3 -B tests/fixtures/r38-drift-mutants.py --fixture tests/fixtures/r38-drift-record.py --base-fixture tests/fixtures/r37-drift-discrimination.py` | `2843805d4631b040219ed1ba60053035b5a86f07` (`c3-after2.txt`) |

Owned score values are unchanged (calibration 7, operability 8, coverage 8): the lane still has no
reproducible 0-10 mapping, so the rows carry measurements and verdicts rather than numbers. No axis
is harmed: no predicate was relaxed, the r36/r37 fixtures and the r35 census record are byte-identical,
and every consumer stayed green (`consumers-after2.txt`: 16/16, 14/14, 12/12, 6/6, 12/12 with
`base_fail=9 escapes=9`, 21/21, 10/10).

### Round 38 capability rows (appended)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| measured-commit citation arm (r38) | bind a self-assessment cell to a concrete revision: the commit must resolve, be an ancestor of the audited revision, be named on the anchored line, and the cited receipt blob at that commit must carry the expected token; seven-column registers stay valid | `python3 -B tools/souji-citation-reconcile.py --root <lane> --rev <full40> --register census/round-38/cells.tsv --register-rev <freeze>` -> `cells=10 mismatches=0`; `python3 -B tests/fixtures/r38-citation-commit.py` -> `cases=14 pass=14 fail=0 control=FALSE-GREEN-REJECTED` | r38 |
| non-blocking output envelope (r38) | refuse a `--json` target that is not a regular file without blocking (FIFO/socket/directory), and refuse an output that is the input by resolved path or inode, so a run can neither hang on nor destroy its input | `python3 -B tests/fixtures/r38-drift-write-envelope.py --base-tool <r37 blob>` -> `cases=12 pass=12 fail=0 base_cases=12 base_fail=6` | r38 |
| record-validation discrimination (r38) | a ten-case record fixture plus a four-mutant battery with a pristine control that scores the tool's TOTAL cross-checks and duplicate-name refusal, and a base-fixture arm that proves the gap on the previous fixture | `python3 -B tests/fixtures/r38-drift-record.py` -> `cases=10 pass=10 fail=0`; `python3 -B tests/fixtures/r38-drift-mutants.py --fixture tests/fixtures/r38-drift-record.py --base-fixture tests/fixtures/r37-drift-discrimination.py` -> `mutants=4 killed=4 survived=0 pristine=ok base_killed=0` | r38 |

### Planned (appended at round 38)

- **r39 (planned r38):** calibration: give at least two register rows a `commit` different from
  `receipt_rev` so the live register, not only the fixture, exercises the arm's revision
  discrimination (this round's ten rows are all `commit == receipt_rev`, disclosed); sweep the
  remaining stale cells the wave found outside the register. Operability: make the docstring case
  read the real module docstring through `ast` only (variant b1 is now caught only by the docstring
  token removal, and the one-way phantom limit is named), and cover `argparse`'s own exit 2.
  Coverage: mutation-score the fixture's other record rules (comment/blank skipping, optional
  TOTAL) and the drift classes, which the four frozen mutants do not touch. Certification OFF, K5 HELD.

### Round 38 receipt pointer update (appended after wave 1, 2026-10-28)

Wave 1 falsified five instrument premises; the repairs are prereg amendments A4-A7 and every final
receipt was re-measured at `78ea25a963f2d2ba93b6049dc2787b7020e2fd80`:
`census/round-38/records/c1-after5.txt` (`cells=10 mismatches=0`), `c1-vacuity4.txt` (`mismatches=9`),
`c2-after4.txt` (`cases=12 pass=12 fail=0 base_cases=12 base_fail=6 behavioral_fail=3`),
`c3-after3.txt` (`cases=10 pass=10 fail=0` and `mutants=4 killed=4 survived=0 pristine=ok base_killed=0`),
`consumers-after4.txt` and `a7-counter-fixes.txt`. The earlier receipts (`c1-after2`, `c2-after3`,
`c3-after2`, `a1-docstring-variants`, `a2-anchor-isolation`) record the pre-amendment bytes and stay
as filed; none of their values is claimed as the final state.

### Round 38 final receipt pointers (appended after wave 2)

Every claim was re-measured at `4bda5f6759bd4a6c1c965bbd052351fcf69f1bb5` with the post-wave-2
instruments: `census/round-38/records/c1-after6.txt` (`cells=10 mismatches=0`), `c1-vacuity5.txt`
(`mismatches=9`), `c2-after5.txt` (`cases=12 pass=12 fail=0 base_cases=12 base_fail=6
behavioral_fail=3`), `c2-base-composition2.txt` (the composition line, measured at a revision that
contains it), `c3-after4.txt` (`cases=10 pass=10 fail=0`; `mutants=4 killed=4 survived=0 pristine=ok
base_killed=0`) and `consumers-after5.txt` (all eight consumer fixtures green). Receipts from
earlier commits (`c1-after2`…`c2-after4`) stay as filed and describe the pre-amendment bytes; the
`c2-after3`/`c2-base-composition` labels name a revision that predates the A3 line (`W2RevC2` F5)
and are superseded by these.

### Round 38 measured-revision block (appended 2026-10-28, final)

All three claims and every consumer are measured at `cb5737a63a704a7a52a1b97dada3fe5634fea32b`:
`census/round-38/records/c1-after7.txt` (`cells=10 mismatches=0`, rc 0), `c1-vacuity6.txt`
(`mismatches=9`, rc 1), `c2-after6.txt` (`cases=12 pass=12 fail=0 base_cases=12 base_fail=6
behavioral_fail=3`, rc 0), `c3-after5.txt` (`cases=10 pass=10 fail=0`; `mutants=4 killed=4
survived=0 pristine=ok base_killed=0`, rc 0), `consumers-after6.txt` (eight consumers green) and
`a7-counter-fixes2.txt` (the three counter first-falsifications refused at this revision). The
earlier pointer blocks stay as filed; where they disagree with this one, this block is later and
measures the final instruments.

### Round 38 filed-state measurement (appended 2026-10-28)

Final tip `99efe0676f439309a52f001b71bf0ba2ed8af47f`: `c1-after8.txt` (`cells=10 mismatches=0`, rc 0),
`c2-after7.txt` (`cases=12 pass=12 fail=0 base_cases=12 base_fail=6 behavioral_fail=3`, rc 0) and
`c3-arms-filed.txt` (`cases=10 pass=10 fail=0`; `mutants=4 killed=4 survived=0 pristine=ok
base_killed=0`; counter-arms `cases=6 pass=6 fail=0 control=FALSE-GREEN-REJECTED`; rcs 0/0/0).
Where an earlier block disagrees with this one, this is later and measures the filed instruments.
