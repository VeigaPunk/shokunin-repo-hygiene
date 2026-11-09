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
| receipt index-flag refusal (r62) | the receipt writer refuses, before its dirty check and regardless of `--allow-dirty`, any tracked index entry whose `git ls-files -v` tag is not `H`, with `RECEIPT-INDEX-FLAG-CONCEALED:`; start-of-run only (flags set or edits made during the wrapped command are not checked) | `python3 -B census/round-62/c1-counter.py --root . --matrix census/round-62/c1-matrix.tsv --base-rev 16fa821fdce00e709d6895ccfc7aaffa465af195 --rev a0b396cdd4f9c75bc2f0e117399916a2279cddd1 --tool tools/souji-receipt-write.py --work DIR` → `new_forgeries=0 new_honest=2 class_mismatches=0 regress=PASS`, EXIT 0 (`census/round-62/records/c1-after.txt`); do-nothing `census/round-62/controls/c1-do-nothing.txt` (`new_forgeries=3`, EXIT 1) | r62 |
| receipt env-route and mode refusal (r66) | the receipt writer refuses, before any git call, the presence of `GIT_CONFIG_COUNT`, `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_KEY_*`, `GIT_CONFIG_VALUE_*` (`RECEIPT-ENV-CONFIG-SET`) and of `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_REPLACE_REF_BASE` (`RECEIPT-ENV-REDIRECT-SET`), names only; pins `GIT_CONFIG_GLOBAL` and `core.excludesFile` to the null device on every git call; records full permission bits (setuid, setgid, sticky) in the in-run snapshot. Ignore routes and `GIT_COMMON_DIR` remain open (named limits) | `python3 -B census/round-66/c1-counter.py --root . --matrix census/round-66/c1-matrix.tsv --base-rev 045e103478fa4a7eff77db2cab5b9e2f26959a0a --rev c13fbb4e1b563a78278ddc14316c20252e9a6d8d --tool tools/souji-receipt-write.py --work DIR` → `new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS`, EXIT 0 (`census/round-66/records/c1-after.txt`); do-nothing `census/round-66/controls/c1-do-nothing.txt` (`new_forgeries=8`, EXIT 1) | r66 |
| writer mutant battery with outcome split (r68) | regenerates 14 single-edit writer mutants from the candidate blob (`census/round-68/mutate-writer.py`, sha-pinned in `census/round-68/battery/SHA256SUMS`) and refutes each with the frozen round-68 counter; each refutation is classified as forgery, over-refusal or label-only from the receipt's `CASE` rows; a red do-nothing receipt (base writer) shows the counter is not silent | `python3 -B census/round-68/c1-counter.py --root . --matrix census/round-68/c1-matrix.tsv --base-rev 3639087917eaeb28719d7603110a6ec22782100e --new-tool <mutant> --work DIR`; `census/round-68/records/c1-after/summary.tsv` (14 of 14 refuted; candidate `EXIT=0`); `census/round-68/controls/c1-do-nothing.txt` (`EXIT=1`) | r68 |
| battery outcome-class split and declared-coverage table (r69) | runs the writer battery once per manifest mutant and classifies each refutation as forgery, echo-violation, over-refusal, label-only, survived or error; only forgery counts as a declared-protection kill; a green receipt requires every observed class to match its manifest expectation; a do-nothing and ambient receipt stay red and clean | `python3 -B census/round-69/c1-counter.py --root . --matrix census/round-69/c1-matrix.tsv --base-rev 3639087917eaeb28719d7603110a6ec22782100e --work <scratch> --battery-manifest census/round-69/battery-manifest.tsv --battery-dir census/round-69/battery` → `census/round-69/records/c1-after-battery.txt` (`BATTERY mutants=26 kills=18 label_only=5 over_refusal=2 echo_violation=1 survived=0 error=0`, EXIT=0); `census/round-69/records/declared-coverage.tsv` (12 mutant, 2 limit); S302, S303 | r69 |
| pathspec-variable hermetic writer reads (r70) | the receipt writer keeps its verdict when the caller exports GIT_LITERAL_PATHSPECS, GIT_GLOB_PATHSPECS, GIT_NOGLOB_PATHSPECS or GIT_ICASE_PATHSPECS (no forged receipt over skip-worktree, subdirectory-scope, gitlink or absent rows; no over-refusal of an honest tree); the wrapped command still sees the variables | `python3 -B census/round-70/c1-counter.py --root . --matrix census/round-70/c1-matrix.tsv --base-rev e063a2fcb3f5f3fb8fb19d2ae1592b1f22e6a333 --rev 93a051b2c936ff6eafca8e8b31d918e3d20fd3da --tool tools/souji-receipt-write.py --work <scratch>` → `census/round-70/records/c1-after.txt` (`new_forgeries=0 new_honest=15 class_mismatches=0`, EXIT=0); writer selftest case 38 | r70 |
| counter self-check harness and pointer-existence check (r70) | scores a counter on whether its own selftest kills four frozen instrument mutants and whether its battery arm detects a swapped member (positives required; a blanket-failing counter is invalid, EXIT=2); resolves every lane path a lesson or prereg cites at a revision | `census/round-70/c2-harness.py` → `census/round-70/records/c2-after.txt` (`score=0`, EXIT=0; r69 counter `score=5`); `python3 -B tools/souji-pointer-check.py --root . --rev FULL40 FILE...` → `census/round-70/records/pointer-check-r69.txt` (5 missing, EXIT=1), `pointer-check-r70.txt` (0 missing, EXIT=0) | r70 |
| clean-tree witness against attributes and stat settings (r71) | the receipt writer scrubs GIT_ATTR_SOURCE, pins core.fileMode/checkStat/trustctime, and refuses RECEIPT-FILTER-DRIVER-SET (a tracked path's filter with a configured clean/process driver, checked before the pre- and post-run status reads) and RECEIPT-CHECKIN-CONVERSION-SET (ident, working-tree-encoding); honest no-driver, unused-driver and fileMode=false trees still accepted. Same-second in-place edits remain invisible (named limit) | `python3 -B census/round-71/c1-counter.py --root . --matrix census/round-71/c1-matrix.tsv --base-rev 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0 --rev FULL40 --tool tools/souji-receipt-write.py --work <scratch>` → `census/round-71/records/c1-after.txt` (`new_forgeries=0 new_honest=19`, EXIT=0; do-nothing `new_forgeries=7`, EXIT=1); repaired tip `records/c1-at-repair.txt`; writer selftest 42/42 `records/writer-selftest-repair.txt`; `records/repair-canfail.txt` | r71 |
| counter mutant harness over prior-round survivors; pointer-check self-test (r71) | scores a counter's own selftest against the five r70-surviving counter mutants (frozen exact edits, authored by an r70 seat) plus the four r70 harness mutants; label-validated, cleans its run dir; the pointer check has a 4-case `--selftest` that two mutants fail | `census/round-71/c2-harness.py` → `records/c2-after.txt` (`x_killed=5 score=0`, EXIT=0; r70 counter `score=5`, EXIT=1); `records/pointer-check-selftest.txt` | r71 |
| base-slot bound counter verdict (r72) | the r72 counter's verdict requires every row's base-slot verdict to equal its frozen `base_expect` (reference-weak writer at 8b9345b1), prints `base_mismatches`, and its own selftest kills the six r71 seat survivors (Y1 Y4 Y6 Y9 Y10 Z1) plus X6-X10 and CM1-CM4 | `python3 -B census/round-71/c2-harness.py --label L --counter census/round-72/c1-counter.py --matrix census/round-72/c1-matrix.tsv --root . --base-rev 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0 --mutants census/round-72/c1-mutants.json --work <scratch>` → `census/round-72/records/c1-after.txt` (`x_killed=11 score=0`, EXIT=0; r71 counter `score=6`, EXIT=1); Y6 main arm `records/c1-Y6-main-arm.txt` (`base_mismatches=10`, EXIT=1) | r72 |
| filter-witness protections as matrix rows (r72) | five writer protections (pre-run witness, post-run witness, process-driver lookup, worktree attribute read, no boolean-value exemption) each have a frozen row that a single-edit writer mutant forges; the honest writer stays EXIT=0 | battery `python3 -B census/round-72/c1-counter.py --root . --matrix census/round-72/c1-matrix.tsv --base-rev 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0 --work <scratch> --battery-manifest census/round-72/battery-manifest.tsv --battery-dir census/round-72/battery` → `records/c2-after-battery.txt` (`kills=5 survived=0`, EXIT=0; r71 counter `survived=5`, EXIT=1); `records/c2-honest-writer.txt` (EXIT=0) | r72 |
| receipt byte truth against the index stat cache (r73) | the receipt writer re-hashes every status-clean stage-0 tracked file (`git hash-object --stdin-paths`, the check-in conversion git status applies) and symlink (link target as a blob) against the object id the index records, before and after the wrapped command, and re-compares the instrument after it; a stat-rewritten forgery refuses `RECEIPT-WORKTREE-STAT-CONCEALED`, an honest stale-stat or autocrlf tree still writes; on the lane itself (18987 tracked files) a receipt takes ~2 s | `python3 -B census/round-73/c1-counter.py --root . --matrix census/round-73/c1-matrix.tsv --base-rev 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0 --rev b84ff90bff05fb057c5a8c4b0661a9ec41d9e4a2 --tool tools/souji-receipt-write.py --work <scratch>` → `census/round-73/records/c1-after.txt` (`new_forgeries=0 new_honest=21`, EXIT=0; lane-base writer `controls/c1-K-a-do-nothing.txt` `new_forgeries=3`, EXIT=1); writer selftest `records/writer-selftest.txt` (44/44) | r73 |
| counter forgery witness (r73) | the r73 counter credits a refuse row the base slot accepts as a base forgery only when the fixture worktree differs from the row revision before or after the run (tree_divergence: no git status, stat cache or filter); `base_unwitnessed` enters the verdict and the battery classifier scores an unwitnessed accept as `error` | five defanged fixtures (`census/round-73/c2-defang.json`) → `records/c2-after-D1..D5.txt` (`base_unwitnessed=1`, `base_witness=no` on the edited row; r72 counter with the same edits EXIT=0, `controls/c2-before-r72-D*.txt`); unmutated `controls/c1-K-a-do-nothing.txt` `base_unwitnessed=0 base_forgeries=15` | r73 |
| pre-report gate byte truth (r74) | `tools/souji-pre-report-gate.sh` check 4 no longer takes an empty `git status` as clean: it re-hashes every status-clean stage-0 tracked path against the object name its index entry records through the receipt writer's `_truth_refusal` (imported from beside the gate), so an index stat-cache forgery of a file, a symlink or a size-changing file fails `clean`; a missing writer or failed read fails closed; ~2.7 s over a 19144-file clone | `python3 -B census/round-74/c1-gate-counter.py --gate tools/souji-pre-report-gate.sh --work <empty scratch>` → `records/c1-after.txt` `SUMMARY rows=9 mismatches=0 errors=0`, EXIT=0 (lane-base gate mismatches=3, `controls/c1-K-a-do-nothing.txt`) | r74 |
| row-specific counter witness (r74) | the r74 counter credits an accepted refuse row as a forgery only when the divergence lies on the row's declared forged paths (`forge_paths`/`row_scope`), so a set-up-only divergence (`.gitattributes`) no longer witnesses a defanged row; `base_forgeries` counts witnessed rows only; the claim also needs `new_unwitnessed=0`; its selftest kills the four r73 survivors (failed witness read, symlink target, gitlink skip, new-slot pre-only) | defanged FWw/FC1/FC2 → `census/round-74/records/c2-after-D6.txt`, `c2-after-D7.txt`, `c2-after-D8.txt` `base_unwitnessed=1` (r73 counter 0 of 3); `records/c2-after-pristine.txt` `base_unwitnessed=0 base_forgeries=15` EXIT=0; survivors `records/c2-after-M08-selftest.txt` … `c2-after-M17-selftest.txt` EXIT=1 each | r74 |
| pre-report gate ignore-source rule (r75) | `tools/souji-pre-report-gate.sh` check 4 refuses untracked content git hides only through a repository-local exclude source: it lists ignored untracked paths under `--exclude-standard` and under `--exclude-per-directory=.gitignore` alone and fails `clean` on a non-empty difference (S318, S319); committed `.gitignore` hiding passes; a work tree git resolves anywhere but the lane fails (wave repair) | `python3 -B census/round-75/c1-evade-counter.py --gate-dir <gate+writer dir> --work <empty scratch>` → `census/round-75/records/c1-after.txt` `SUMMARY rows=25 mismatches=0 errors=0`, EXIT=0 (lane-base gate mismatches=2, `controls/c1-K-a-do-nothing.txt`); repaired gate `records/wave-repair/c1-at-repair.txt` 0, core.worktree route `records/wave-repair/coreworktree-W.txt` PASS → `-R.txt` FAIL | r75 |
| witness-counter selftest second detectors (r75) | the r75 counter's selftest kills X09 (new slot not row-scoped) and X15∘M17 (new slot pre-run only, with the (9a) count check weakened), keeping M08/M14/M15/M17 killed; no verdict code changed | `python3 -B census/round-75/c2-kill-counter.py ...` → `census/round-75/records/c2-after.txt` `SUMMARY mutants=6 killed=6 survived=0 unread=0 pristine=PASS`, EXIT=0 (r74 counter killed=4, `controls/c2-K-do-nothing-r74.txt`) | r75 |
| pre-report gate ignore-source attribution (r76) | `tools/souji-pre-report-gate.sh` check 4 attributes every ignored untracked path with `git -c core.excludesFile=/dev/null check-ignore -v -n -z --stdin` (S320) and refuses it unless its deciding pattern comes from a `.gitignore` tracked at HEAD in an ancestor directory (self-ignoring untracked `.gitignore` = lane change); tracked set from HEAD's tree | `python3 -B census/round-76/c1-evade-counter.py --gate-dir DIR --work WORK` → `SUMMARY rows=30 mismatches=0 errors=0` (`census/round-76/records/c1-after.txt`, `records/wave-repair/c1-at-repair.txt`); repair probes 8/8 (`records/wave-repair/repair-probes.txt`) | r76 (closure-gated) |
| receipt-bound mutant-kill tally (r76) | the r76 tally refuses a kill receipt that names another instrument, an unknown mutant id, a pristine receipt of another counter, a duplicate digest or id, or EXIT lines that disagree; it derives every mutant's expected counter sha256 from the frozen edit sets | `python3 -B census/round-76/c2-binding-counter.py --tally census/round-76/c2-kill-tally.py` → `SUMMARY cases=10 mismatches=0 errors=0` (`census/round-76/records/c2-after.txt`); tally probes 8/8 (`records/wave-repair/tally-probes.txt`) | r76 (closure-gated) |
| pre-report gate non-regular-source refusal (r77) | `tools/souji-pre-report-gate.sh` check 4 refuses `RECEIPT-NONREGULAR-SOURCE` when any existing exclude/attribute source (`--git-path` info/exclude, info/attributes, index, info/sparse-checkout; core.excludesFile/attributesFile or XDG defaults, `/dev/null` allowed; every work-tree `.gitignore`/`.gitattributes` by target) is not a regular file, before git reads it (S321); check-4 git calls under a timeout | `python3 -B census/round-77/c1-nonreg-counter.py --gate-dir DIR --work WORK` → `SUMMARY rows=16 mismatches=0 errors=0 hangs=0` (`census/round-77/records/c1-after.txt`, `records/wave-repair/c1-at-repair.txt`); lane-base gate 9 mismatches, 8 hangs; repair probes 10/10 (`records/wave-repair/repair-probes.txt`) | r77 (closure-gated) |
| self-assessment pointer resolution census (r77) | resolves every MISSING evidence pointer of the six self-assessment files to a verified class (CAPTURED at its own path with the frozen digest, MOVED byte-equal, LOCAL-POLICY, QUARANTINED, FLEET, TOKEN, ABSENT) and refuses blanket-absent, local-instead-of-capture, stub-capture and name-only-move ledgers | `python3 -B census/round-77/c2-pointer-counter.py --root LANE --rev REV --fleet-root FLEET --ledger census/round-77/c2-pointer-ledger.tsv` → `SUMMARY items=35 resolved=35 …` (`census/round-77/records/c2-after.txt`); pointer check missing 35 → 31 | r77 (closure-gated) |

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
- **r67 (planned r66):** (a) operability: a frozen route sweep of git's environment surface (git(1) ENVIRONMENT VARIABLES, including `GIT_COMMON_DIR`, `GIT_NAMESPACE`, `GIT_CEILING_DIRECTORIES`) with a do-nothing control and a mode-hiding fixture for `GIT_COMMON_DIR` and repository-local `core.fileMode=false`; operator ruling needed on whether repository-local keys are in scope. (b) calibration: a new frozen counter (not an amendment) whose selftest binds the M10 line and fails on the reverted repair (round-66 M4); a population row that can fail on scope (M5); the stale s4 note (M7); the frozen docstring (M6). (c) operability: kill-power fixtures for the redundant pins K3, K4, K6, K7 or a recorded decision that they are defence in depth. (d) operator rulings: the honest-run refusal under `git -c` (round-66 W3, the GIT_CONFIG_PARAMETERS trade) and the E3 wording (round-66 M8).
- **r67 (planned r66) — done, attempt 1 (see `corpus/lessons/round-67.md`, `## Routed to round 68`):** C1 operability (receipt-binding) — the writer value-checks a caller-injected `GIT_COMMON_DIR` (frozen target met at `f70da577`); C2 calibration — the corrected statement counter and population flag the round-66 `s5` class overreach at the pinned state and kill the reverted-rule and enum-weakened mutants (frozen target met). Routed items: K3/K4/K6/K7 kill fixtures (PK3, PK4, PK6, PK7, proposed, `fixture-proposed`); repository-local `core.fileMode` and `GIT_NAMESPACE`/`GIT_CEILING_DIRECTORIES` rows; relative-value rule (operator L0 question); counter scrub of `GIT_COMMON_DIR` and `GIT_NO_REPLACE_OBJECTS`; L0 360 (`git -c` refusal) still awaiting the operator.
- **r68 (planned r67):** (a) operability: a frozen counter (not an amendment) for the proposed fixtures PK3, PK4, PK6, PK7 (repository-local `core.excludesFile`, caller-named global and system configs with `core.fileMode=false`, a repository replace ref forging HEAD's instrument), each with its honest control; (b) operability: the relative `GIT_COMMON_DIR` row for writer cwd ≠ root, after the operator ruling on the fail-closed trade; (c) calibration: the counter's `clean_env` and the C2 read scrub `GIT_COMMON_DIR`, `GIT_NAMESPACE`, `GIT_CEILING_DIRECTORIES` and `GIT_NO_REPLACE_OBJECTS`, and the C2 receipt records `git replace -l` (sentinel M1, M2); (d) corpus: the `knowledge/common-dir-route-receipt-writer.md` entry gets its non-author spot-check.
- **r69 (planned r68):** (a) calibration: a successor frozen predicate that counts forgery-based refutations as declared-protection kills and reports label-only and over-refusal refutations on their own line (QUALITY Q131); rebuild fixture W4 at `repo/main/.git` with its own kill row (Q132). (b) operability: the counter's clean environment also scrubs or pins `HOME` and `XDG_CONFIG_HOME` (sentinel MEDIUM-1) and `GIT_TRACE*`; the counter selftest runs `main()` on a two-row matrix (round-68 M2). (c) coverage: the 14 declared writer protections with no battery mutant (`S68ScoutDeclared` inventory: D02, D03, D04, D18, D19, D21, D29, D30 and the rest) get a mutant each or a named limit. (d) the C2 counter `census/round-67/c2-counter.py` gets the replace/redirect scrub and the replace-list record (r67 sentinel M2). (e) operator rulings: the kill-rule split (Q131), the relative-value trade, and the writer receipt verifier gap (`S68ExecTrial` MEDIUM).
- **r68 (planned r67) — done, attempt 1 (see `corpus/lessons/round-68.md`):** C1 calibration: battery refutations 7 of 14 → 14 of 14 on the 42-row counter with the candidate `EXIT=0`; verified on its frozen predicate with attack qualifications (10 forgery-based, 2 over-refusal, 2 label-only). C2 operability: ambient-environment flips 35 → 0 with both runs `EXIT=0` and the do-nothing still red; verified on its three-variable tuple. No writer byte changed. Routed from the r67 plan: the relative value stays the operator's ruling; the counter scrub covers the three ambient variables; `git replace -l` recording and the C2 counter are routed to r69.
- **r69 (planned r68) — done, attempt 1 (see `corpus/lessons/round-69.md`):** C1 calibration: the outcome split over the writer battery (`census/round-69/`), 26 mutants, 18 forgery kills, 0 survived, EXIT=0 (before: no outcome lines exist in the r68 records). C2 operability: ambient-environment flips of the counter under the wider tuple 6 → 0 (both EXIT=0; do-nothing stays EXIT=1). C3 coverage: declared writer protections with a battery row 0 of 14 → 12 of 14, with 2 named limits (D18, D29). Qualifications and the wave verdicts are in the round lesson and report. Routed to r70: the operator rulings on the relative-value trade and the writer verifier remain open (L0); the lane has no writer `verify` subcommand.
- **r70 (planned r69) — done, attempt 1 (see `corpus/lessons/round-70.md`):** C1 operability: the writer scrubs the four pathspec variables from its `git()` helper; frozen r70 counter `new_forgeries` 4 → 0, `new_honest` 13 → 15 of 15, `class_mismatches` 5 → 0, EXIT 1 → 0, regress PASS (refuse-on-presence and literal-only controls stay red); the NOGLOB scrub is unmeasured (no row depends on it). C2 calibration: the counter's own selftest now kills four frozen instrument mutants (the r69 precedence-swap, expectation-gate and echo-judge blind spots plus a survived gate) and its battery arm refuses a swapped member; harness score 5 (r69 counter) → 0 (r70 counter). Not closed: S69MutTester's e2/e4 survivors (a selftest that weakens its own assertion), a structural limit. r69 routed D1 (wave evidence mirror), D2 (committed selftest receipts), D3 (SKILL registry row) closed; D4 corrected in the r70 lesson; D5 open. Routed to r71: see the lesson's Routed list.
- **r71 (planned r70) — done, attempt 1 (see `corpus/lessons/round-71.md`):** C1 operability: writer filter-driver / core.fileMode hardening; frozen r71 counter `new_forgeries` 7 → 0, `class_mismatches` 7 → 0, `new_honest` 19/19 kept, EXIT 1 → 0 (blanket-refusal and partial-fix controls stay red); the wave forged the frozen candidate on three unmeasured filter-class routes and one stat route, all repaired in-round with selftest cases shown able to fail (M4). C2 calibration: the counter's own selftest kills the five r70-surviving mutants X6-X10; harness score 5 → 0. Routed r72: base-slot binding in `claim_upheld`, AS-row discrimination, over-refusal row, W8 cached-attribute row.
- **r72 (planned r71) — done, attempt 1 (see `corpus/lessons/round-72.md`):** C1 calibration: the counter's verdict binds the base slot (`base_expect` column, `base_mismatches`) and its selftest kills the six r71 seat survivors; harness `x_killed` 5 → 11 of 11 (score 6 → 0), Y6 main arm EXIT 0 → 1. C2 coverage: five writer filter-witness protections get forging matrix rows (FWr FWi FWp FWw FWs); battery kills 0 → 5 of 5, honest writer EXIT=0. No writer byte changed.
- **r73 (planned r72) — done, attempt 2 (attempt 1 landed F/I/K/W/A and died before the report; see `corpus/lessons/round-73.md`):** C1 operability: the receipt writer re-hashes status-clean tracked files and symlinks against the index object id before and after the run (S315 S316); frozen r73 counter `new_forgeries` 3 → 0 with `new_honest` 21/21, EXIT 1 → 0 (blanket refusal and forger controls red). C2 calibration: the counter credits a base forgery only with an observed worktree divergence; defanged fixtures detected 0 → 5 of 5, honest `base_unwitnessed=0`. Wave repair after measurement (lesson M1): writer selftest 44 → 45 cases; the symlink-target and pre-run protections now each fail their mutant (`census/round-73/records/wave-repair/`). Routed: see the lesson's "Routed to round 74".
- **r74 (planned):** row-specific forgery witness (FWw, FC1, FC2 unwitnessable today, S73ExecC2) and the S73MutCounter survivors M08/M14/M15/M17 (calibration); the lane's own clean-tree gates that trust `git status` (`tools/souji-pre-report-gate.sh`, `tools/souji-verify.sh`, S73Connector HIGH) (operability).
- **r74 (planned r73) — done, attempt 1 (see `corpus/lessons/round-74.md`):** C1 operability: the pre-report gate re-hashes status-clean tracked paths through the writer's `_truth_refusal` (S317); frozen gate counter mismatches 3 → 0, EXIT 1 → 0 (blanket and regular-only controls red); the wave forged the stage-W gate on six routes outside the frozen rows, repaired in-round with each route shown able to fail (lesson M4). C2 calibration: row-specific counter witness; defanged FWw/FC1/FC2 detected 0 → 3 of 3 (D1..D5 kept 5/5, pristine `base_unwitnessed=0 base_forgeries=15`), r73 survivors M08/M14/M15/M17 killed 0 → 4 of 4.
- **r75 (planned):** calibration: derive the witness path set from the fixture builders and key it on the forging step (S74ExecC2 X4 SY2 credited defang, S74CriticDiscern M3), detect new-slot scoping and give M17 a second detector (S74MutCounter X09, X15), bind the writer hash and refusal class in the gate counter (S74MutGate F2/F3), the `souji-freeze-check.py` prereg grammar (Q99, failing since r72); operability: the remaining status-trusting tools `tools/souji-guard.r9-s18.sh:175`, `tools/souji-record-agreement.py:351`, `tools/souji-idx-repair.py` (S74Connector), writer survivor M03.
- **r75 (planned r74) — done, attempt 1 (see `corpus/lessons/round-75.md`):** C1 operability: the pre-report gate refuses untracked content hidden only by info/exclude or core.excludesFile (S318, S319); frozen 25-route counter mismatches 2 → 0, EXIT 1 → 0 (blanket ignored-refusal control red); the wave forged the W gate through a repository-local core.worktree and red the r36 fixture's honest cases (its harness symlink hidden by info/exclude) — both repaired after measurement, each shown able to fail (lesson M5). C2 calibration: the witness counter's selftest gains two detectors; mutant kills 4 → 6 of 6 (X09, X15∘M17 added), pristine 64/64. Q99 freeze grammar met (findings=0 with `--substance --chronology`).
- **r76 (planned):** calibration: the new-slot post-only witness and a row_fate aliased to the base witness survive the r75 selftest (S75ExecC2 Y4/Y5); the kill tally's EXIT=2/`fail=0 EXIT=1` classes have no committed receipt (S75MutCounter M1/M2) and it does not bind a receipt to its mutant (S75Reviewer O2); witness path set from the builders (r74 M3); operability: the gate's ls-files failure branch and refusal class are unmeasured (S75MutGate F3/F4); the other status-trusting lane tools and nine sibling gates (S75Connector); writer survivor M03.
- **r76 (planned r75) — done, attempt 1 (see `corpus/lessons/round-76.md`):** C1 operability: the pre-report gate attributes each ignored untracked path to its deciding pattern (S320) and refuses one an untracked `.gitignore` decides; frozen 30-route counter mismatches 4 → 0, EXIT 1 → 0 (blanket and naive controls red, r27/r36 green). C2 calibration: the kill tally binds every receipt to its mutant; frozen 10-case counter mismatches 5 → 0 (blanket red, honest set killed=6). Wave repairs after measurement: a repository fsmonitor hook forged the C1 candidate (tracked set now from HEAD), `GIT_EXEC_PATH`, unanchored `.jj/`, the tally's substring `--selftest` test; kill-power gaps (one-path threshold M09, filename-separable C2 population, binding-counter K03/K04) recorded, not re-scored.
- **r77 (planned r76) — done, attempt 1 (see `corpus/lessons/round-77.md`):** C1 operability: the pre-report gate refuses non-regular exclude/attribute sources instead of hanging (S321); frozen 16-row counter mismatches 9 → 0, hangs 8 → 0 (K-b/K-c/K-d red; r76 30/30, r36 21/21, r27 4/4); wave repair `844b2d70` (common dir, symlink by target, fail-closed scan; probes 10/10). C2 calibration: the 35 MISSING evidence pointers of the self-assessment files resolve to verified classes (4 captured at their own path, 10 moved, 21 classified); resolved 0 → 35 (four forgery controls red); pointer check missing 35 → 31. Qualifications: n8 policy row; 31/35 reachable by a mechanical ledger; C2 counter controls aggregate-red.
- **r78 (planned):** calibration: a successor pointer-resolution counter with per-row forged-ledger expectations (QUARANTINED bound to the token, TOKEN bound to the named template/revision, R0 exercised, population digest pinned) and a do-nothing control at the mechanical-ledger ceiling; then extend the census to LOG.md (25 MISSING at r77 base). operability: one timeout over checks 1-3 and the pre-check, a TERM trap, frozen rows for XDG/relative/backstop. Carried: r76 binding counter K03/K04; status-trusting tools (`souji-verify.sh:550,594`, `souji-census.sh`, writer).
- **r78 (planned r77) — done, attempt 1 (see `corpus/lessons/round-78.md`):** C1 operability: the pre-report gate refuses non-regular git discovery sources (HEAD, commondir, packed-refs, config files and their includes; S323, S324) before its first git call and bounds check 1 with a 45 s timeout; frozen 17-row counter mismatches 12 → 0, hangs 12 → 0 (K-b/K-c/K-d red; r77 16/16, r76 30/30, r36 21/21, r27 4/4). C2 calibration: the 22 MISSING LOG.md evidence pointers resolve under a location-bound successor counter (3 captured at their own path, 19 classified); resolved 0 → 22 against a 19-of-22 mechanical ceiling; 12 LOG forgeries and the 7 r77 forgeries refused; pointer check missing 22 → 19. Not taken: SIGTERM, the 300 s check-4 backstop row, r76 K03/K04, status-trusting tools.
- **r79 (planned):** operability: the SIGTERM path (a TERM/EXIT trap that kills the gate's git children; run git calls as background jobs so `wait` is interruptible) with a frozen row, and the check-4 backstop row; the r78 wave's routes (see `corpus/lessons/round-78.md` `## Routed to round 79`). calibration: a lost-versus-prose discrimination for ABSENT items, or extend the pointer census to corpus/lessons. Carried: r76 binding counter K03/K04; status-trusting tools (`souji-verify.sh:550,594`, `souji-census.sh`, writer).
- **r79 (planned r78) — done, attempt 1 (see `corpus/lessons/round-79.md`):** C1 operability: the pre-report gate runs every child as an asynchronous job and answers a caller's TERM/INT/HUP by killing the child's process group (S325, S326); frozen 11-row counter mismatches 10 → 1 at A (row s4 INT red: the receipt was launched with `&`, so SIGINT was ignored on entry and untrappable — lesson M2/M3; C1 FAILS its frozen kill rule at A), 10 → 0 in 3 of 3 foreground runs of the same counter at the same gate bytes; K-b/K-c red; r78 17/17, r77 16/16, r76 30/30, r36 21/21, r27 4/4. A repair aimed at a race that was not the cause (R1) was reverted. C2 calibration: the successor pointer counter refuses the five false ledger rows the r78 wave found; harness accepted 5 → 0 (K-b refuse-all 9/9 but 3/22 on the regression; each ablation accepts 1-2); r78 22/22 + 12/12, r77 35/35 + 7/7.
- **r80 (planned):** calibration or operability: a C1 counter successor that resets inherited signal dispositions and asserts where each row blocks (lesson M1-M3); the check-4 300 s backstop row; r78 routed (a) duration bound and timeout's group; carried: r76 K03/K04 and the status-trusting tools (`souji-verify.sh:550,594`, `souji-census.sh`, writer).
- **r80 (planned r79) — done, attempt 1 (see `corpus/lessons/round-80.md`):** C1 calibration: the successor pointer counter `census/round-80/c1-pointer-counter.py` refuses the three false ledger rows the r79 wave found (range member a directory, MOVED copy under another tree, declaration matched only as path prefixes; S327); frozen 18-row harness accepted 3 → 0 (K-b red on the r78 regression, three ablations 1 each; r78 22/22, r77 35/35, r79 harness 9/9). C2 operability: `tools/souji-quarantine.sh` runs as a front shell and a `setsid` worker and kills the worker session on a caller's TERM/INT/HUP (S328, S075); frozen 15-row counter (the r79 instrument fixes: launch line, disposition reset, asserted hang point, row bound) mismatches 12 → 0, orphans 12 → 0 (K-b/K-c 12 each; r13 5/5, r17 35/0, selftest 108/0 on the committed file after a first replay on a mode-0644 copy read 81/51 — M1; domain trial v3 identical after a vacuous v1 and a location-skewed v2 — M2). Not taken: re-measuring the r79 gate (defect 2), the check-4 backstop row, `tools/souji-vault-verify.sh`.
- **r81 (planned):** calibration: the r80 wave's C1 counter rows (NF12 decoy under `census/round-<N>/` — bind the capture root to its capture subtrees and re-derive the 14 real MOVED rows; NF14; detector rows for the mode arm, the before-check, the punctuation allowance, `fleet:` symlinks; `_regular` pathspec). operability: freeze the post-wave quarantine rows (launch mode, worker killed, the intro-blob digest site) as a successor population and re-measure the repaired front; `tools/souji-vault-verify.sh:213`. Carried: the r79 gate re-measurement (r79 defect 2), the check-4 300 s backstop row, r76 K03/K04, status-trusting tools.
- **r81 (planned r80) — done, attempt 1 (see `corpus/lessons/round-81.md`):** C1 calibration: the successor pointer counter `census/round-81/c1-pointer-counter.py` binds a MOVED target under `census/round-<N>` to a wave capture subtree that keeps the token's own path suffix, grounded on the 14 real MOVED rows; frozen 25-row harness accepted 3 → 0, refused_true 0 (K-b refused_true 3, K-c accepted 1; r78 22/22, r77 35/35, r79 9/9, r80 18/18). C2 operability (sourced on S329): `tools/souji-vault-verify.sh` runs its advisory CLI call as an asynchronous job with `<&0`, traps TERM/INT/HUP while it waits and kills timeout's group; frozen 12-row counter mismatches 8 → 0, orphans 8 → 0 (K-b 8, K-c p3; selftest 57/0, r17 37/0/0, trial identical). Wave harm at W2 repaired behind probe D (private file under a vault path) at R `ef76a14f`. Qualifications: launch-dependent (SHELLOPTS=monitor: 2 orphan rows, M4); decoys NF12c/NF12d L1-built; own-tree decoys unseen. V1: r80 front re-measured green, one monitor-tail flake by a seat. Registry K1 7 → 1 (not a claim).
- **r82 (planned r81) — done, attempt 1 (see `corpus/lessons/round-82.md`):** C1 calibration: the successor pointer counter binds a MOVED target in the token's own round tree by the same subtree-plus-suffix rule (NF-F/NF-G) and carries the wave's M8 killer row NF-H; frozen 32-row harness accepted 2 → 0, refused_true 0, PF-1 shape-true. C2 operability (C2 successor counter): `tools/souji-vault-verify.sh` kills the CLI's whole descendant tree under job control and drops the stale `$!`; frozen 16-row counter (the m1/m2 monitor rows, v9/v10 term-ignoring rows) mismatches 4 → 0 under `SHELLOPTS=monitor` (Base tool default-launch 16/16, the bounded baseline) and 0 mismatches under the default launch; probe D successor 6/6. Wave hours carried to round-79-gate and V1.

### Round 78 measurements (2026-11-07, Linux; lane base `a8558d410e9855a9d990d6542a24a9a3a365ab6c`; controls `a0dcfa8d7da794e821b22a421584ac2a03c611c0`; freeze `007404ea363461a76ff23afcf6173b3281532dd3`; gate `ed22dc9cb7a6b61a7d0bd150db4a95191b1333aa`; captures `d90740fec1862556ed504aafcd21e89d5dece0f0`; ledger `a0f3b91fe59129802c48f7e4db750960ddeaa408` repaired `87d456179668738ca59e607c3176de056e6a9991`; after-arms `319109b0ddc836c6cf3364fdde3ab99796f21f32`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 gate git discovery sources | operability 8 | `census/round-78/controls/c1-K-a-do-nothing.txt` `SUMMARY rows=17 mismatches=12 errors=0 hangs=12` EXIT=1 | `census/round-78/records/c1-after.txt` `rows=17 mismatches=0 errors=0 hangs=0` EXIT=0; K-b 14, K-c 10, K-d 11 red; r77 16/16, r76 30/30, r36 21/21, r27 4/4 | `python3 -B census/round-78/c1-gitsrc-counter.py --gate-dir DIR --work WORK` | `ed22dc9cb7a6b61a7d0bd150db4a95191b1333aa` (gate blob `b746bd9d…4eef`) |
| C2 LOG.md pointer resolution | calibration 7 | `census/round-78/controls/c2-K-a-no-ledger.txt` `resolved=0 unresolved=22` EXIT=1; mechanical ledger 19 (`c2-K-b-mechanical.txt`) | `census/round-78/records/c2-after.txt` `resolved=22 unresolved=0 refused=0 mismatched=0 errors=0`, `FORGE-SUMMARY forged=12 matched=12 accepted=0` EXIT=0; r77 population 35/35, 7/7; pointer check missing 22 → 19 | `python3 -B census/round-78/c2-pointer-counter.py --root LANE --rev REV --fleet-root FLEET --population census/round-78/c2-population.tsv --ledger census/round-78/c2-pointer-ledger.tsv --forge census/round-78/c2-forge-r78.tsv` | `87d456179668738ca59e607c3176de056e6a9991` (after-arm commit `319109b0`) |

No owned axis score changed (calibration 7, coverage 8, operability 8). Wave qualifications are in `corpus/lessons/round-78.md` `## Wave`.

### Capabilities (round 78 rows)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| git discovery-source refusal | refuse, before the first git call, a FIFO or other non-regular HEAD, commondir, packed-refs, system/global/XDG/repository/worktree config or any file their includes name, and time-bound the remote call | `census/round-78/records/c1-after.txt` (17/17, hangs 0) | r78 (closure-gated) |
| location-bound pointer ledger verification | verify an evidence-pointer ledger against pinned populations with location-bound MOVED/QUARANTINED/TOKEN rules and a frozen per-row forgery set | `census/round-78/records/c2-after.txt`, `census/round-78/records/c2-regress-r77.txt` | r78 (closure-gated) |

### Round 79 measurements (2026-11-07, Linux; lane base `e65538e73c7f1a8f7570bc24a2215da8a90043f3`; controls `d7f40f764e6b25e32662384761d82d3032714eb1`; freeze `e98cd0c55b1d8aaec8af8ff3402a5856263923ed`; gate `c8c3fbca5ac44184feac3a01ee964139f86c02a4`; counter `17009fa1f9d335a1bdde1e22ff3894c5d571c250`; after-arms `b8d094299e06bc66352f5232cd7a75d1f503c0fa`; R1 `4a9bbb303db7f1508e24f60d4b9feff80bcbc079` reverted at `feebf2ba6f120903e45d31cf322751c052f2feb9`; foreground re-measurement `92cab9c782457c4256acc6f099375caf4056fca3`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 gate signal handling | operability 8 | `census/round-79/controls/c1-K-a-do-nothing.txt` `SUMMARY rows=11 mismatches=10 errors=0 orphans=10` EXIT=1 | A `census/round-79/records/c1-after.txt` `rows=11 mismatches=1 errors=0 orphans=1` EXIT=1 (s4, background launch, M2); foreground `census/round-79/records/foreground/c1-at-W1-fg-run1..3.txt` `mismatches=0 orphans=0` EXIT=0 ×3; K-b 10, K-c 10 red; r78 17/17, r77 16/16, r76 30/30, r36 21/21, r27 4/4 | `python3 -B census/round-79/c1-signal-counter.py --gate-dir DIR --work WORK` | `c8c3fbca5ac44184feac3a01ee964139f86c02a4` (gate blob sha256 `ae5022c5…7e1c`) |
| C2 false ledger rows refused | calibration 7 | `census/round-79/controls/c2-K-a-r78-counter.txt` `SUMMARY rows=9 mismatches=5 accepted=5 errors=0` EXIT=1 | `census/round-79/records/c2-after.txt` `rows=9 mismatches=0 accepted=0 errors=0` EXIT=0; K-b 9/9 but 3/22 regression; ablations 2/1/1/1; r78 22/22 12/12, r77 35/35 7/7 | `python3 -B census/round-79/c2-false-row-harness.py --counter census/round-79/c2-pointer-counter.py --lane LANE --fleet-root FLEET --work WORK` | `17009fa1f9d335a1bdde1e22ff3894c5d571c250` |

No owned axis score changed (calibration 7, coverage 8, operability 8): C1 fails its frozen kill rule at A (1 mismatch, 1 orphan); the foreground runs are a post-measurement re-run of the same counter under a launch the prereg did not name, reported for the closure to rule on, not counted as the claim; C2 verifies on its frozen predicate. Wave qualifications are in `corpus/lessons/round-79.md` `## Wave`.

### Capabilities (round 79 rows)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| signal-safe gate children | stop the pre-report gate on a caller's TERM/INT/HUP within 5 s with every child group killed and the gate's scratch removed, verified by a survivor census | `census/round-79/records/foreground/c1-at-W1-fg-run1.txt` (11/11, 0 orphans) | r79 (closure-gated) |
| false-ledger-row harness | score any pointer-resolution counter against the previous wave's false ledger rows in a reproducible fixture (rev 6436db6a) | `census/round-79/records/c2-after.txt`, `census/round-79/controls/c2-K-a-r78-counter.txt` | r79 (closure-gated) |

### Round 81 measurements (2026-11-07, Linux; lane base `b15279bbc3f11ec10fc375a05a08b19cac460d0c`; controls `804f132ef717d96157c107e219a254286644b706`; freeze `0b1aeaf1c1bb11605bb9e139116323f5680b1a1c`; C1 counter `308bc77bddc725aa8f302e4f62746bde3f843f56`; C2 tool `7076ed2d12faf82e9c762f49d627b84ae549fbd1`; after-arms `cb14eae71c02d51d2e071628ac4c882f01daf844`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 census decoys refused, true captures kept | calibration 7 | `census/round-81/controls/c1-K-a-r80-counter.txt` `SUMMARY rows=25 mismatches=3 accepted=3 refused_true=0 errors=0` EXIT=1 (NF12, NF12c, NF12d) | `census/round-81/records/c1-after.txt` `rows=25 mismatches=0 accepted=0 refused_true=0 errors=0` EXIT=0; K-b refuse-all refused_true=3, K-c without-suffix accepted=1; r78 22/22 12/12, r77 35/35 7/7, r79 harness 9/9, r80 harness 18/18 | `python3 -B census/round-81/c1-false-row-harness.py --counter census/round-81/c1-pointer-counter.py --lane LANE --fleet-root FLEET --work WORK` | `308bc77bddc725aa8f302e4f62746bde3f843f56` |
| C2 vault CLI signal handling | operability 8 | `census/round-81/controls/c2-K-a-do-nothing.txt` `SUMMARY rows=12 mismatches=8 errors=0 orphans=8` EXIT=1 | `census/round-81/records/c2-after.txt` `rows=12 mismatches=0 errors=0 orphans=0` EXIT=0; K-b 8/8, K-c p3 red; selftest 57/0 (committed file), r17 37/0/0, domain trial identical 3/3 | `python3 -B census/round-81/c2-vault-signal-counter.py --tool FILE --work WORK` | `7076ed2d12faf82e9c762f49d627b84ae549fbd1` (tool blob sha256 `ba61e912…aa13`) |

No owned axis score changed (calibration 7, coverage 8, operability 8): both claims are instrument- and tool-level moves the closure rules on. Registry agreement (not a claim): K1 7 → 1 by five used-by repairs; K1 S146 and K2 SCORECARD recorded accepted-red with reasons (`corpus/lessons/round-81.md` `## Registry agreement`).

### Capabilities (round 81 rows)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| signal-safe vault CLI call | stop `tools/souji-vault-verify.sh`'s advisory CLI call on a caller's TERM/INT/HUP (to its pid or its process group) within 5 s with timeout's group killed and its private output file removed, the CLI keeping the caller's stdin | `census/round-81/records/c2-after.txt` (12/12, 0 orphans; default and `&` launches — under `SHELLOPTS=monitor` 10/12, `records/launch/c2-at-W2-monitor.txt`; repaired R `records/repair/c2-at-R.txt` 12/12) | r81 (closure-gated) |
| location-bound census capture check | refuse a MOVED pointer whose target sits under `census/round-<N>` outside a wave capture subtree or without the token's own path suffix, while keeping flattened and records/wave-<w>/ captures | `census/round-81/records/c1-after.txt` (25/25, refused_true 0) | r81 (closure-gated) |

### Round 80 measurements (2026-11-07, Linux; lane base `f80f9368a8a20679438b1dffd72d0faab0ccf194`; controls `515d57c8c559d64d0c071cc25b07df0b815bd77a`; freeze `aaad410f4de2c1b0e98f1a7f305736dfcee5c5ab`; C1 counter `bd263c3f7d376e617c2fde5b99793622b0908b53`; C2 tool `836dac3e336863c57d9d7125837ed22b22d8d044`; after-arms `a4aa888037922b7b5ccfac7150f156f92af5916e`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 r79-wave false ledger rows refused | calibration 7 | `census/round-80/controls/c1-K-a-r79-counter.txt` `SUMMARY rows=18 mismatches=3 accepted=3 errors=0` EXIT=1 | `census/round-80/records/c1-after.txt` `rows=18 mismatches=0 accepted=0 errors=0` EXIT=0; K-b 18/18 but 3/22 regression; ablations 1/1/1; r78 22/22 12/12, r77 35/35 7/7, r79 harness 9/9 | `python3 -B census/round-80/c1-false-row-harness.py --counter census/round-80/c1-pointer-counter.py --lane LANE --fleet-root FLEET --work WORK` | `bd263c3f7d376e617c2fde5b99793622b0908b53` |
| C2 quarantine signal handling | operability 8 | `census/round-80/controls/c2-K-a-do-nothing.txt` `SUMMARY rows=15 mismatches=12 errors=0 orphans=12` EXIT=1 | `census/round-80/records/c2-after.txt` `rows=15 mismatches=0 errors=0 orphans=0` EXIT=0; K-b 12, K-c 12 red; r13 5/5, r17 35/0, selftest 108/0 (`c2-regress-selftest-committed-mode.txt`; first replay on a 0644 copy 81/51, `c2-regress-selftest.txt`, M1), domain trial v3 identical (`c2-domain-trial.txt`; v1/v2 in `records/diagnosis/`, M2) | `python3 -B census/round-80/c2-signal-counter.py --tool-dir DIR --work WORK` | `836dac3e336863c57d9d7125837ed22b22d8d044` (tool blob sha256 `67ec160b…7181`) |

No owned axis score changed (calibration 7, coverage 8, operability 8): both claims are instrument- and tool-level moves the closure rules on; C2's selftest and domain-trial conjuncts were first measured with defective replays (lesson M1, M2) and re-measured on the committed object and a symmetric layout, which the report states for the closure to rule on. Wave qualifications are in `corpus/lessons/round-80.md` `## Wave`. After the wave the tool was repaired twice behind failing-before probes (job-control launch harm M4, env spoof, post-worker signals, worker-killed sweep): R `8ba93218`, R2 `97289f81`, R3 `4a499e9a` (a newline in a comm hid a process from the session scan), receipts `census/round-80/records/repair/`, `repair2/`, `repair3/` (15/15 also with SHELLOPTS=monitor, every probe passing); these are not the claim's measurement.

### Capabilities (round 80 rows)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| signal-safe quarantine dry-run | stop `tools/souji-quarantine.sh` on a caller's TERM/INT/HUP within 5 s with every process it started killed (its worker session) and its private TMPDIR removed, verified by a nonce survivor census with asserted hang points | `census/round-80/records/c2-after.txt` (15/15, 0 orphans) | r80 (closure-gated) |
| disposition-controlled signal counter | measure a tool's signal handling under any launch: children start with INT/QUIT/TERM/HUP reset, the row prints the tool's SigIgn at delivery, the hang point is asserted from the shim's mark | `census/round-80/c2-signal-counter.py`; `census/round-80/records/c2-after.txt` (launched with `&`, every INT row trappable) | r80 (closure-gated) |

### Round 77 measurements (2026-11-07, Linux; lane base `d4f515637884695b3aa016da169d859d3ece6ac4`; controls `43822328ec27b429b68c21d9c3a995e0a09b9d77`; freeze `a9979807fd5d9f80851c0f1fc6481e9bf0334644`; gate `9b496b0883b255573175726f1463ce5634960a04`; capture `6690cb5ad96d11a7b528a62a98ba42fad7783d35`; ledger `8bf42fc6233cc4fee28c170d57e5d38a80f6d2bc`; after-arms `ef04ca6c66af02b98bc061290b8028c6c0654a4b`; wave repair `844b2d70afebad97ba68c620c0d486c76cd84c2b`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 gate non-regular sources | operability 8 | `controls/c1-K-a-do-nothing.txt` `SUMMARY rows=16 mismatches=9 errors=0 hangs=8` EXIT=1 (8 hang rows + n8 policy row) | `records/c1-after.txt` `rows=16 mismatches=0 errors=0 hangs=0` EXIT=0; K-b 7, K-c 11, K-d 7 red; r76 30/30, r36 21/21, r27 4/4; at the repair identical | `python3 -B census/round-77/c1-nonreg-counter.py --gate-dir DIR --work WORK` | `9b496b0883b255573175726f1463ce5634960a04` (gate blob `28a51355…16be`); repair `844b2d70` |
| C2 self-assessment pointer resolution | calibration 7 | `controls/c2-K-a-no-ledger.txt` `resolved=0 unresolved=35` EXIT=1 | `records/c2-after.txt` `resolved=35 unresolved=0 refused=0 mismatched=0 errors=0` EXIT=0; K-b/K-c/K-d/K-e red; pointer check missing 35 → 31 | `python3 -B census/round-77/c2-pointer-counter.py --root LANE --rev REV --fleet-root FLEET --ledger census/round-77/c2-pointer-ledger.tsv` | `8bf42fc6233cc4fee28c170d57e5d38a80f6d2bc` |

No owned axis score changed (calibration 7, coverage 8, operability 8). Wave qualifications are in `corpus/lessons/round-77.md` `## Wave`.

### Round 76 measurements (2026-11-06, Linux; lane base `ee59aa4da358d38850ccace194f7cd558ee45ce9`; controls `6c9c2a8eaad2ee570e4f43517d1f437567bb9873`; freeze `2ed6b179ef4aeb106488806b9f3dcacca29e2e60`; tally `2c7c1ce6f91062f497ffbbc7fcc9e9c19e2511ce`; gate `e827d2bf53f71470bfc1fce6aa4633549b018270`; after-arms `113b007202d79275ca2debaaaa719551eaa35198`; wave repair `9cbfd29630f04799cb72b17a53df860c1f503275`, receipts `1a6eaea8acc14c23e13269429ab2699dde8e112f`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 pre-report gate refuses content an untracked `.gitignore` hides (S320) | operability 8 (not re-scored) | `census/round-76/controls/c1-K-a-do-nothing.txt`: `SUMMARY rows=30 mismatches=4 errors=0` (f7 f9 f10 f14 `clean=PASS`), EXIT=1; blanket K-b mismatches=4, naive K-c mismatches=1, both EXIT=1 | `census/round-76/records/c1-after.txt`: `SUMMARY rows=30 mismatches=0 errors=0`, EXIT=0; r36 21/21, r27 4/4 (`records/c1-regress-*.txt`); at the repair `records/wave-repair/c1-at-repair.txt` identical | `grep -E '^(SUMMARY\|EXIT=)' census/round-76/records/c1-after.txt` | `113b007202d79275ca2debaaaa719551eaa35198` (gate blob of `e827d2bf`; repair `9cbfd296`) |
| C2 kill tally binds each receipt to its mutant | calibration 7 (not re-scored) | `census/round-76/controls/c2-K-do-nothing-r75.txt`: `SUMMARY cases=10 mismatches=5 errors=0` (five b-* forgeries accepted), EXIT=1; blanket reject-all mismatches=2, EXIT=1 | `census/round-76/records/c2-after.txt`: `SUMMARY cases=10 mismatches=0 errors=0`, EXIT=0; h-honest `killed=6`; at the repair `records/wave-repair/c2-at-repair.txt` identical | `grep -E '^(SUMMARY\|EXIT=)' census/round-76/records/c2-after.txt` | `113b007202d79275ca2debaaaa719551eaa35198` (tally of `2c7c1ce6`; repair `9cbfd296`) |

No owned axis score changed (calibration 7, coverage 8, operability 8). Qualifications (wave): a repository-local fsmonitor hook forged the C1 candidate through its index read (S76Sentinel HIGH-1) and was repaired after measurement (tracked set from HEAD, `records/wave-repair/repair-probes.txt`); the frozen C1 rows each carry two undeclared paths, so a gate refusing only above one survives them (S76MutGate M09; killed by the repair probe's one-path arm); the frozen C2 population is separable by file name (S76CriticClaims) and the binding counter compares exit codes only (S76MutTally K03/K04: a counter accepting every rejection reads 0 on the r75 control). Routed to r77.

### Round 75 measurements (2026-11-06, Linux; lane base `52d3f07d08422689464598f8be7e2c957fcf0805`; controls `7ba5217d6fc754201615e04e8dfc88cf07c33fd3`; freeze `be599cbb02854b9d669a1a2699f15657fd70b336`; counter `f6ec0d7140e0976b8128af803520b895a14a64e0`; gate `1ad737b4a9ac71bd44b6ac849f73387fdc3ab9c5`; after-arms `5d10e09ed7749f5706eade39ac9a0ae2355aa1f3`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 pre-report gate refuses locally hidden untracked content (S318, S319) | operability 8 (not re-scored) | `census/round-75/controls/c1-K-a-do-nothing.txt`: `SUMMARY rows=25 mismatches=2 errors=0` (f-info-exclude, f5-info-exclude-dir `clean=PASS`), EXIT=1; blanket control mismatches=3, EXIT=1 | `census/round-75/records/c1-after.txt`: `SUMMARY rows=25 mismatches=0 errors=0`, EXIT=0; at the wave repair `records/wave-repair/c1-at-repair.txt` identical | `grep -E '^(SUMMARY\|EXIT=)' census/round-75/records/c1-after.txt` | `5d10e09ed7749f5706eade39ac9a0ae2355aa1f3` (gate blob of `1ad737b4`) |
| C2 witness-counter selftest kills X09 and X15∘M17 | calibration 7 (not re-scored) | `census/round-75/controls/c2-K-do-nothing-r74.txt`: `SUMMARY mutants=6 killed=4 survived=2 unread=0 pristine=PASS` (X09, P1 SURVIVED), EXIT=1 | `census/round-75/records/c2-after.txt`: `SUMMARY mutants=6 killed=6 survived=0 unread=0 pristine=PASS`, EXIT=0 | `grep -E '^(SUMMARY\|EXIT=)' census/round-75/records/c2-after.txt` | `5d10e09ed7749f5706eade39ac9a0ae2355aa1f3` (counter of `f6ec0d71`) |

No owned axis score changed (calibration 7, coverage 8, operability 8). Qualifications (wave): C1's core.excludesFile arm was already refused at base by the writer's pinned status (S75MutGate F2, S75CriticClaims), so the measured move is the info/exclude arm; a repository-local core.worktree forged both the base and W gates and was repaired after measurement; the original r36 fixture reads 18/21 on the W gate because it hid its harness symlink with info/exclude — amended to a committed rule (21/21 on base, W-repaired). C2's detectors are selftest units, not fixture probes; post-only and aliased witnesses survive (routed r76).

### Round 74 measurements (2026-11-06, Linux; lane base `43cd74bba84bb498b57a74377ccb0567d10864d5`; reference-weak base `8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0`; freeze `bcdf2d16f8158c9faf8b60e6bb1b98c1f4f25dce`; counter `ac57303295371f34befc36d34f78c6715f7341a0`; gate `ec13ba7fac9085005dca2e69ee12a2933d2c22a5`; after-arms `8fe48c863d353da8e26140b132afba00de71ba61`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 pre-report gate byte truth against the index stat cache (S317, S315, S316) | operability 8 (not re-scored) | `census/round-74/controls/c1-K-a-do-nothing.txt`: `SUMMARY rows=9 mismatches=3 errors=0` (GF1 GF2 GF3 `clean=PASS`), EXIT=1; blanket refusal mismatches=4, regular-files-only mismatches=1, both EXIT=1 | `census/round-74/records/c1-after.txt`: `SUMMARY rows=9 mismatches=0 errors=0`, EXIT=0; unchanged at the wave repair (`records/wave-repair/c1-at-repair.txt`) | `grep -E '^(SUMMARY\|EXIT=)' census/round-74/records/c1-after.txt` | `8fe48c863d353da8e26140b132afba00de71ba61` |
| C2 row-specific counter witness + r73 survivor kills | calibration 7 (not re-scored) | `census/round-74/controls/c2-before-r73-D6.txt` (and D7, D8): `base_unwitnessed=0`, EXIT=0 each (0 of 3); `controls/c2-before-r73-M08-selftest.txt` (and M14, M15, M17): `SELFTEST cases=52 pass=52 fail=0` EXIT=0 each (0 of 4 killed) | `census/round-74/records/c2-after-D6.txt` (and D7, D8): `base_unwitnessed=1`, edited row `base_witness=no` (3 of 3); D1..D5 5 of 5; `records/c2-after-pristine.txt` `base_unwitnessed=0 base_forgeries=15` EXIT=0; `records/c2-after-M08-selftest.txt` (and M14, M15, M17) fail>=1 EXIT=1 (4 of 4); `records/counter-selftest.txt` 62/62 | `for k in 6 7 8; do grep -cE '^SUMMARY .*base_unwitnessed=1( \|$)' census/round-74/records/c2-after-D$k.txt; done`; `for m in M08 M14 M15 M17; do grep -E '^SELFTEST' census/round-74/records/c2-after-$m-selftest.txt; done` | `8fe48c863d353da8e26140b132afba00de71ba61` |

No owned axis score changed (calibration 7, coverage 8, operability 8). Qualifications (wave): the frozen C1 rows did not cover the gate wrapper's own surface — six evasion routes, three code-injection routes and two report hangs forged or stalled the stage-W gate and were repaired after measurement (lesson M4); C2's witness is path-keyed and declared beside the builders (S74ExecC2 X4 credits an SY2 defang; S74MutCounter X09/X15 survive), routed to r75 (lesson M3).

### Round 73 measurements (2026-11-06, Linux; lane base `a789486d8d5d5e0f91145ad70282956f2cb6fda0`; reference-weak base `8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0`; freeze `23ecd0700be05a78b71ad88ae6fca2d2d8f5468b`; counter `1eac307f7cc8d1e30df009eabb693875ace97976`; C1 controls `aaacba3378d8b8160f4c86c142182c0ddbcad81a`; writer `b84ff90bff05fb057c5a8c4b0661a9ec41d9e4a2`; after-arms `312e8f29d42eac0fd91327d65a6b43a0ba9cc64e`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 writer byte truth against the index stat cache (S315 S316) | operability 8 (not re-scored) | `controls/c1-K-a-do-nothing.txt`: `new_forgeries=3 new_honest=21 class_mismatches=3`, EXIT=1 (FX1 FX2 FX3 `new=accept`); blanket refusal `new_honest=0`, forger `new_forgeries=15`, both EXIT=1 | `records/c1-after.txt`: `SUMMARY matrix=80 base_forgeries=15 base_honest=21 base_mismatches=0 base_unwitnessed=0 new_unwitnessed=0 new_forgeries=0 new_honest=21 class_mismatches=0 new_echo=0 errors=0 regress=PASS`, EXIT=0; `records/writer-selftest.txt` `SELFTEST cases=44 pass=44 fail=0` | `grep -E '^(SUMMARY\|EXIT=)' census/round-73/records/c1-after.txt census/round-73/controls/c1-K-a-do-nothing.txt` | writer `b84ff90bff05fb057c5a8c4b0661a9ec41d9e4a2` |
| C2 counter forgery witness (defanged fixtures detected) | calibration 7 (not re-scored) | `controls/c2-before-r72-D1..D5.txt`: r72 counter with each edit `base_forgeries=12 base_mismatches=0`, EXIT=0 each (0 of 5 detected) | `records/c2-after-D1..D5.txt`: `base_unwitnessed=1` and `base_witness=no` on the edited row, each (5 of 5); positive `controls/c1-K-a-do-nothing.txt` `base_unwitnessed=0 base_forgeries=15`; `records/counter-selftest.txt` 52/52 | `for k in 1 2 3 4 5; do grep -cE '^SUMMARY .*base_unwitnessed=1( \|$)' census/round-73/records/c2-after-D$k.txt; done` | counter `1eac307f7cc8d1e30df009eabb693875ace97976` |

No owned axis score changed (calibration 7, coverage 8, operability 8).

### Round 72 measurements (2026-11-06, Linux; lane base `0bf098dde7e6eafb62a9ce62b7c16a6291ee1e8e`; reference-weak base `8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0`; freeze `23372f362c71931494e170efdceb28e3b1735e84`; candidate counter `06df4f97c531a05ff2139368f70660c3044f71a6`; after-arms `2ec8b63dfda8fdf88cd240487c5d1325de13b501`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 counter self-check of the r71 survivors + base-slot binding | calibration 7 (not re-scored) | `controls/c1-before-r71.txt`: `x_killed=5 x_survived=6 score=6`, EXIT=1; `controls/c1-Y6-main-arm-r71.txt`: EXIT=0 | `records/c1-after.txt`: `SUMMARY label=c1-after-r72 positive_selftest=PASS x_mutants=11 x_killed=11 x_survived=0 cm_mutants=4 cm_killed=4 cm_survived=0 score=0`, EXIT=0; `records/c1-Y6-main-arm.txt`: `base_mismatches=10`, EXIT=1 | `grep -E '^(SUMMARY\|EXIT=)' census/round-72/records/c1-after.txt census/round-72/records/c1-Y6-main-arm.txt` | counter `06df4f97c531a05ff2139368f70660c3044f71a6` |
| C2 filter-witness protections as matrix rows (S312-S314) | coverage 8 (not re-scored) | `controls/c2-before-r71-battery.txt`: `kills=0 survived=5`, EXIT=1 | `records/c2-after-battery.txt`: `BATTERY mutants=5 kills=5 label_only=0 over_refusal=0 echo_violation=0 survived=0 error=0 all_match=true`, EXIT=0; `records/c2-honest-writer.txt`: `new_forgeries=0 new_honest=19 class_mismatches=0 … regress=PASS`, EXIT=0 | `grep -E '^(BATTERY\|SUMMARY\|EXIT=)' census/round-72/records/c2-after-battery.txt census/round-72/records/c2-honest-writer.txt` | counter `06df4f97c531a05ff2139368f70660c3044f71a6`, writer at `0bf098dd` |

No owned axis score changed (calibration 7, coverage 8, operability 8).

### Round 71 measurements (2026-11-06, Linux; base `8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0`; freeze `aa91d1cad89200ec733edd3475461010a372923d`; candidate writer `a1db6c8514771c0a0321c29741831606d09cc2a5`; after-arms `52e8c3faf678b0f3d2f18cc6d41a365dc91123f7`; wave repairs `45a94c83`, `f13d575e`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 filter-driver / core.fileMode witness hardening (S306-S308) | operability 8 (not re-scored) | `controls/c1-do-nothing.txt`: `new_forgeries=7 new_honest=19 class_mismatches=7`, EXIT=1 | `records/c1-after.txt`: `SUMMARY matrix=70 base_forgeries=7 base_honest=19 new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS`, EXIT=0 | `grep -E '^(SUMMARY\|EXIT=)' census/round-71/records/c1-after.txt` | `a1db6c8514771c0a0321c29741831606d09cc2a5` (re-run at `f13d575e`: same, `records/c1-at-repair.txt`) |
| C2 counter selftest vs the five r70-surviving mutants X6-X10 | calibration 7 (not re-scored) | `controls/c2-before-r70.txt`: `x_killed=0 x_survived=5 score=5`, EXIT=1 | `records/c2-after.txt`: `SUMMARY label=c2-after-r71 positive_selftest=PASS x_mutants=5 x_killed=5 x_survived=0 cm_mutants=4 cm_killed=4 cm_survived=0 score=0`, EXIT=0 | `grep -E '^(SUMMARY\|EXIT=)' census/round-71/records/c2-after.txt` | counter frozen at `aa91d1ca` |

No owned axis score changed (calibration 7, coverage 8, operability 8). Qualifications (wave): C1's predicate scores 7 routes; three further filter-class routes and a stat route forged the candidate and were repaired after measurement (lesson M4); the counter's rc does not bind the base slot (S71MutCounter F1, routed). C2 is mutant-set-specific (S71CriticClaims).

R70-D1 correction (appended r71; the capability row above is not edited): the r70 row "counter self-check harness and pointer-existence check (r70)" says `pointer-check-r69.txt (5 missing, EXIT=1)`; the committed receipt reads `missing=8` (`SUMMARY files=2 checked=59 missing=8`), EXIT=1. Lesson round-71 M2.

### Round 70 measurements (2026-11-06, Linux; base `e063a2fcb3f5f3fb8fb19d2ae1592b1f22e6a333`; freeze `0243af04bbcd422302b4efc3473612073c9aa962`; candidate writer `93a051b2c936ff6eafca8e8b31d918e3d20fd3da`; after-arms `e84f691b9b022425449e2aecc2e7ae308aee4ffe`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 pathspec-variable scrub in every writer git call (S304) | operability 8 (not re-scored) | `controls/c1-do-nothing.txt`: `new_forgeries=4 new_honest=13 class_mismatches=5`, EXIT=1 (LD LN4 LG1 LA9 forged; LU1 wrong class; GA ICA over-refused) | `records/c1-after.txt`: `SUMMARY matrix=59 base_forgeries=4 base_honest=13 new_forgeries=0 new_honest=15 class_mismatches=0 new_echo=0 errors=0 regress=PASS`, EXIT=0; controls F1 `new_honest=11` EXIT=1, F2 `new_honest=13` EXIT=1 | `grep -E '^(SUMMARY\|EXIT=)' census/round-70/records/c1-after.txt` | candidate `93a051b2c936ff6eafca8e8b31d918e3d20fd3da` |
| C2 counter self-check: frozen instrument mutants surviving the counter's own selftest + undetected member tamper | calibration 7 (not re-scored) | `controls/c2-before-r69.txt`: r69 counter `killed=0 survived=4 tamper=undetected score=5`, EXIT=1 | `records/c2-after.txt`: `SUMMARY label=c2-after-r70 positive_selftest=PASS positive_battery=PASS mutants=4 killed=4 survived=0 tamper=detected score=0`, EXIT=0; controls CF1, CF2 EXIT=2 (invalid) | `grep -E '^(SUMMARY\|EXIT=)' census/round-70/records/c2-after.txt` | counter at freeze `0243af04bbcd422302b4efc3473612073c9aa962`, run at `e84f691b` |

No owned axis score changed (calibration 7, coverage 8, operability 8): no reproducible 0–10 mapping exists for either move. Wave verdicts are recorded in `corpus/lessons/round-70.md` and in the report.

### Round 69 measurements (2026-11-05, Linux; base `893b8ef4e73b3fde45f712df3437a032b1d92d42`; writer unchanged; freeze `1412037c9fac1cd18381075d22fefbac06ae5bac`; after-arm `89fea6be`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 outcome-class split of the writer battery | calibration 7 (bookkeeping file; not re-scored) | r68 records carry 0 `MUTANT`/`BATTERY` outcome lines (`grep -rc '^MUTANT \\|^BATTERY ' census/round-68/records/c1-after/` total 0); hand classification 10 forgery, 2 over-refusal, 2 label-only | `BATTERY mutants=26 kills=18 label_only=5 over_refusal=2 echo_violation=1 survived=0 error=0`, EXIT=0; each observed class equals its manifest expectation | `grep -c '^MUTANT .* outcome=forgery' census/round-69/records/c1-after-battery.txt` = 18; `grep -c 'outcome=label-only'` = 5; `grep -c 'outcome=over-refusal'` = 2; `grep -c 'outcome=echo-violation'` = 1; `grep '^EXIT='` = 0 | `census/round-69/records/c1-after-battery.txt` at `89fea6be` (counter bytes frozen at `1412037c`) |
| C1 W4 base arm (Q132 rebuild) | calibration (rides in C1) | r68 candidate `CASE W4 … base=refuse` ×1 (`base_stderr=refused: rev is not a commit object`, an unrelated fixture failure) | `CASE W4 … base=accept` ×26 (one per battery run); candidate W4 `new=refuse` `lane worktree is dirty` unchanged | `grep -c '^CASE W4 .* base=accept' census/round-69/records/c1-after-battery.txt` = 26; `grep -c '^CASE W4 .* base=refuse' census/round-68/records/c1-after/CAND.txt` = 1 | `89fea6be`; fixture build `census/round-69/c1-counter.py` `mutate()` |
| C2 ambient environment, clean vs the frozen tuple (HOME, XDG_CONFIG_HOME, GIT_TRACE*, GIT_TRACE2_*; env -i); tuple-scoped, not ambient immunity (wave S69ExecAmbient: GIT_ATTR_SOURCE, GIT_EXEC_PATH, GIT_TEMPLATE_DIR unscrubbed, 100 flips each under the wider tuple, routed to r70) | operability (bookkeeping file) | r68 counter under the tuple: 6 differing `CASE`/`SUMMARY`/`REGRESS`/`EXIT=` lines, ambient EXIT=1, REGRESS=FAIL (`census/round-69/probes/c2-before-r68-ambient.txt`) | r69 counter: 0 differing lines; clean EXIT=0, ambient EXIT=0 (`census/round-69/records/c2-clean.txt`, `c2-ambient.txt`); do-nothing ambient EXIT=1 (`controls/c2-do-nothing-ambient.txt`) | `diff <(grep -E '^(CASE\|SUMMARY\|REGRESS\|EXIT=)' census/round-69/records/c2-clean.txt) <(grep -E '^(CASE\|SUMMARY\|REGRESS\|EXIT=)' census/round-69/records/c2-ambient.txt) \| grep -c '^[<>]'` = 0 | `89fea6be`; scrub tuple `census/round-69/c1-counter.py` `clean_env()` |
| C3 declared writer protections with a battery row (S68ScoutDeclared U-rows) | coverage 8 (bookkeeping table; not re-scored) | 0 of 14 U-rows name a battery mutant (`awk -F'\t' 'NR>1 && $5=="none"' census/round-68/records/wave-w1/seats/S68ScoutDeclared/declared-protections.tsv \| wc -l` = 14; `controls/c3-do-nothing.txt`) | 12 mutant rows, 2 limits (D18, D29; `controls/d18-limit-battery.txt`, `controls/d29-limit-battery.txt`, both `survived`) | `awk -F'\t' 'NR>1{print $5}' census/round-69/records/declared-coverage.tsv \| sort \| uniq -c` = 12 mutant, 2 limit | `89fea6be`; table `census/round-69/records/declared-coverage.tsv` |

No owned axis score changed (calibration 7, coverage 8, operability 8); the writer did not change. Wave verdicts (attacks on C1, C2, C3 and the sources) are recorded in `corpus/lessons/round-69.md` `## Gate` and in the report; a broken attack is a named defect, not a score change.

### Round 68 measurements (2026-11-05, Linux; base `3639087917eaeb28719d7603110a6ec22782100e`; candidate `f70da577eb1e1624cc63ab8fd0468565927d9b6a`, writer unchanged; pre-freeze instruments and controls `8e4e84cc`, `485e370d`; freeze `8b393b1911558932eab29e74635361256afdd6e3`; prereg `census/round-68/preregistration.txt`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 writer mutant battery refuted by the frozen counter (14 mutants; declared-protection mismatches = unrefuted mutants) | calibration 7 (bookkeeping file) | frozen r67 counter: 7 of 14 refuted; survivors K3, K4, K6, K7, M-CD-EMPTY, M-CD-NCABS, M-CD-ROOTREL (`census/round-68/controls/r67-counter-battery/index.txt`); mismatches 7 | frozen r68 counter: 14 of 14 refuted, each exit 1 with zero error rows; candidate `SUMMARY matrix=42 base_forgeries=2 base_honest=11 new_forgeries=0 new_honest=11 class_mismatches=0 regress=PASS`, `EXIT=0`; mismatches 0 (`census/round-68/records/c1-after/summary.tsv`); L1 recheck of CAND, K1 and M-CD-SCRUB reproduced the seat's lines | `python3 -B census/round-68/c1-counter.py --root . --matrix census/round-68/c1-matrix.tsv --base-rev 3639087917eaeb28719d7603110a6ec22782100e --rev f70da577eb1e1624cc63ab8fd0468565927d9b6a --tool tools/souji-receipt-write.py --work DIR`, and `--new-tool <mutant>` per battery member | `f70da577` (candidate); instruments `8e4e84cc`; freeze `8b393b19` |
| C2 counter verdict under ambient `GIT_COMMON_DIR`, `GIT_NAMESPACE`, `GIT_CEILING_DIRECTORIES` (clean vs ambient flips) | operability (bookkeeping file; not re-scored) | frozen r67 counter: 35 differing `CASE`/`SUMMARY`/`REGRESS`/`EXIT=` lines; ambient run `EXIT=2` ("Stopping at filesystem boundary"; `census/round-68/controls/ambient/`) | frozen r68 counter: 0 flips; clean `EXIT=0`, ambient `EXIT=0`, both `SUMMARY matrix=42 … new_forgeries=0 … class_mismatches=0 regress=PASS` (`census/round-68/records/c2-after/`); do-nothing (base writer) under ambient still `EXIT=1` (`census/round-68/controls/c2-do-nothing-ambient.txt`) | diff of the `^(CASE\|SUMMARY\|REGRESS\|EXIT=)` lines between the clean and the ambient run, `grep -c '^[<>]'` | `f70da577`; freeze `8b393b19` |

Scores: none changed (calibration 7, coverage 8, operability 8). Both verdicts are measured moves on the counter, not 0–10 changes. Qualifications, not counted as passes: 4 of the 14 refutations are label-only or over-refusal (K1, M-CD-ROOTREL; M-CD-NCABS, M-CD-NCRAW; the critic rates the kill rule BROKEN on that point, QUALITY Q131); W4 is built at the wrong path (Q132, routed); 14 of 30 declared writer protections have no battery mutant (`S68ScoutDeclared`, HIGH); `HOME` and `XDG_CONFIG_HOME` are outside the C2 tuple (sentinel MEDIUM-1).
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

### R39 finality correction (round 39, appended; the blocks above stand as written)

R39-C1-10 — the r38 pointer blocks carry three finality labels and their last one names `99efe06`; the measured-revision of all three r38 claims and of every consumer is `fcdecaa`, because the instruments are byte-identical from `99efe06` to `fcdecaa` and only the additive SCORECARD/lesson bytes differ. Where a block says "Final tip `99efe06`", read it as two commits behind `fcdecaa`, and read the vacuity and eight-consumer arms as carried by the block that names `cb5737a`.

### Round 39 register cells (appended; every row's commit is later than its receipt_rev)

R39-REG-01 — the `legs=6` field of `census/round-39/records/c2-after.txt` (receipt_rev 5230a34, re-verified at a8e6d75); the stale reading `legs=2` belongs to the pre-repair bytes.

R39-REG-02 — the `harm=0` field of `census/round-39/records/c2-after.txt` (receipt_rev 5230a34, re-verified at a8e6d75); the stale reading `harm=3` belongs to the pre-repair bytes.

R39-REG-03 — the `fail=0` field of `census/round-39/records/c2-after.txt` (receipt_rev 5230a34, re-verified at a8e6d75); the stale reading `fail=4` belongs to the pre-repair bytes.

### Round 39 register cells, second set (appended; the first set names its own stale token and so cannot serve as a register row)

R39-REG-07 — `legs=6` in `census/round-39/records/c2-after.txt`, receipt committed at 5230a34 and present at a8e6d75.

R39-REG-08 — `harm=0` in `census/round-39/records/c2-after.txt`, receipt committed at 5230a34 and present at a8e6d75.

R39-REG-09 — `fail=0` in `census/round-39/records/c2-after.txt`, receipt committed at 5230a34 and present at a8e6d75.

### Round 39 measurements (2026-10-28; base `ed30b7f5b77939c9073348d810730bc4f355708d`; preregistration `b769bfb84a264d8b284c09bc211d99f39a3e9126`; amendment A1 `bbd9b9746ba9e3c5d640bf095bbad18a00c80e83`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 routed-defect closure | calibration 7 | `SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0` rc 1 (`census/round-39/records/c1-before.txt`) | `SUMMARY items=16 open=0 register_cells=6 register_mismatches=0 commit_distinct=6` rc 0 (`c1-after.txt`): 16 anchored correction lines plus a six-row register whose every row names a later commit | `python3 -B census/round-39/c1-counter.py --root <lane> --rev <full40> --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv --scratch <dir>` | 2f6e981a105fc759205767d2a749a5f7d4fd0b8a |
| C2 tool contracts | operability 8 | `SUMMARY legs=6 pass=2 fail=4 harm=0` rc 1 (`c2-before.txt`) | `SUMMARY legs=6 pass=6 fail=0 harm=0` rc 0 (`c2-after.txt`): unresolvable `--rev` and a blob id are `REFUSAL REV-UNRESOLVED` exit 2 (base: rc 1 with 20 findings); drift docstring class map agrees with behaviour; new fixture 8/8 vs 4 failures on the base blob; five consumers green | `python3 -B census/round-39/c2-counter.py --root <lane> --rev <full40> --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch <dir>` | 2f6e981a105fc759205767d2a749a5f7d4fd0b8a |
| C3 record-rule mutation coverage | coverage 8 | `SUMMARY mutants=4 killed=0 survived=4 pristine=ok base_killed=0 cases=10` rc 1 (`c3-before.txt`, r38 fixture) | `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7` rc 0 (`c3-after.txt`): new fixture kills all four; every mutant still survives the r38 fixture | `python3 -B census/round-39/c3-counter.py --root <lane> --rev <full40> --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch <dir>` | 2f6e981a105fc759205767d2a749a5f7d4fd0b8a |

Owned score values unchanged (calibration 7, operability 8, coverage 8): the lane still has no reproducible 0-10 mapping, so the rows carry measurements and verdicts rather than numbers. No axis is harmed: the frozen predicates were not relaxed (A1 tightened one case class), the r36/r37/r38 fixtures and the r35 census record are byte-identical, and every consumer stayed green.

### Round 39 capability rows (appended)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| routed-defect closure counter (r39) | re-derive 16 anchored self-assessment predicates over committed bytes and, beside them, a citation register that requires every row's `commit` to be a later ancestor carrying the same receipt token; prints `items_sha=` so the instrument list travels with the reading | `python3 -B census/round-39/c1-counter.py --root <lane> --rev <full40> --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv` -> `items=16 open=0 ... commit_distinct=6` (`census/round-39/records/c1-after.txt`) | r39 |
| revision-resolution contract counter (r39) | compare two tool revisions over six legs: unresolvable `--rev`, blob `--rev`, `--register-rev` harm, the drift docstring's class map against the classes actually raised, a 8-case revision fixture's discrimination, and five consumer fixtures with a harm check | `python3 -B census/round-39/c2-counter.py --root <lane> --rev <full40> --base-rev <base40>` -> `legs=6 pass=6 fail=0 harm=0` (`c2-after.txt`) | r39 |
| record-rule mutation battery (r39) | apply four single-defect mutants (trailing-space tolerance, CRLF splitting, outside-root guard, indented comments) and score them against a candidate and a base fixture, refusing a kill without the fixture's own `fail>0` | `python3 -B census/round-39/c3-counter.py --root <lane> --rev <full40> --base-rev <base40>` -> `mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7` (`c3-after.txt`) | r39 |
| revision fixture (r39) | eight cases that separate `REV-UNRESOLVED`/`USAGE` from findings for absent, blob, tree, short and tag revisions, plus a clean run and two `--register-rev` shapes | `python3 -B tests/fixtures/r39-citation-rev.py --tool tools/souji-citation-reconcile.py` -> `cases=8 pass=8 fail=0`; base blob `pass=4` | r39 |
| record-rules fixture (r39) | seven cases for four documented parse behaviours no earlier fixture asserted, plus a TOTAL-before-rows ordering case and the comments-only `RECORD-EMPTY` case | `python3 -B tests/fixtures/r39-drift-record-rules.py --tool tools/souji-worktree-drift.py` -> `cases=7 pass=7 fail=0` | r39 |

### Planned (appended at round 39)

- **r40 (planned r39):** calibration: bind the C1 items to *evidence* rather than token presence (a line that quotes the right tokens but cites nothing passes today; `W1RevC1Forge` demonstrates it) and give the register a row whose `commit` is older than its `receipt_rev` to exercise the other direction. Operability: the C2 L4 analyser still reads one docstring line per class (a wrapped trigger reads False by construction), and the `EISDIR` class the wave found unreachable is now dropped — carry the remaining class-to-trigger pairs the wave listed. Coverage: the parser branches M11-M14 leave uncovered (multiple TOTAL rows, `--skip-unrecorded`, non-UTF-8 records) — mutation-score them next round. Certification OFF, K5 HELD.

### Round 40 closure cells (bound before measurement)

- R40-CLAIM-D1 / R40-CELL-01 — the r40 source census receipt `census/round-40/records/census-after.txt` (committed at `6ded1248b6d0005ac31ff2e1c867ecb0a075ab39`) carries `rows=178` and `W04=49` with exit 0; the instrument commit is `8a5fbdbddaab24c5ba43fc6a133499efb405f214` and this block's verified commit is `556c24a5cacf208c5144c459838712594a43e1f2`.
- R40-CLAIM-D2 / R40-CELL-02 — the C2 leg receipt `census/round-40/records/c2-after.txt` (committed at `6ded1248b6d0005ac31ff2e1c867ecb0a075ab39`) carries `legs=7` and names the revision it measured, `8a5fbdbddaab24c5ba43fc6a133499efb405f214`; this block's verified commit is `556c24a5cacf208c5144c459838712594a43e1f2`.
- R40-CLAIM-D3 / R40-CELL-03 — the r40 C1 counter prints the register's row count and its distinct-commit count as two fields, `commit_rows=` and `commit_hashes=`, so the r39 row-count label cannot recur; the counter bytes are `census/round-40/c1-counter.py` at instrument commit `8a5fbdbddaab24c5ba43fc6a133499efb405f214`, the receipt `census/round-40/records/c3-after.txt` (committed at `6ded1248b6d0005ac31ff2e1c867ecb0a075ab39`) carries `killed=4`, and this block's verified commit is `556c24a5cacf208c5144c459838712594a43e1f2`.

### Round 40 measurements (2026-10-28; base `0242085909fb6a4ee041c5443d76316ac6d59d4b`; instrument `8a5fbdbddaab24c5ba43fc6a133499efb405f214`; closure `549d9ec53a1f5932337ff14438fcd22b0621828d`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 evidence-bound closures + strict-descendant register | calibration 7 | `SUMMARY items=3 open=3 register_cells=6 ...` rc 1 at the frozen base (`census/round-40/records/c1-before.txt`); r39 control closes the token-only line (`ITEM FORGE-TOKEN CLOSED`, `census/round-40/records/c1-control.txt) | `SUMMARY items=3 open=0 forged=3 forged_open=3 forged_closed=0 register_cells=3 register_mismatches=0 register_violations=0 commit_rows=3 commit_hashes=1` rc 0; equal/backwards and unbound-pointer controls remain OPEN/rejected (`c1-after-d.txt`) | `python3 -B census/round-40/c1-counter.py --root . --rev <full40> --items census/round-40/c1-items.tsv --forged census/round-40/c1-forged.tsv --register census/round-40/cells.tsv --min-cells 3 --min-commit-rows 3 --scratch <scratch>`; fixture `python3 -B tests/fixtures/r40-c1-evidence.py --work <scratch>` -> `cases=8 pass=8 fail=0` | `549d9ec53a1f5932337ff14438fcd22b0621828d` (`c1-after-d.txt`) |
| C2 joined docstring reading | operability 8 | r39 one-line reading of the synthetic + tool probes: `SUMMARY cases=9 pass=6 fail=3` (`fixtures-after.txt`; the r39 control misses `--root` on the continuation line) | candidate instrument: `SUMMARY legs=7 pass=7 fail=0 harm=0` (`c2-after-d.txt`); fixture joined `9/9`, one-line control `6/9` | `python3 -B census/round-40/c2-counter.py --root . --rev <full40> --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch <scratch>`; `python3 -B tests/fixtures/r40-docstring-joined.py [--one-line]` | `549d9ec53a1f5932337ff14438fcd22b0621828d` (`c2-after-d.txt`) |
| C3 record-branch mutation battery | coverage 8 | r39 base fixture has no cases for the declared branches; the r40 battery's base arm reads `base_killed=0` for M15-M18 | `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8` rc 0 (`c3-after-d.txt`); M15→`total-conflicting-second`, M16→four skip-flag cases, M17→`invalid-utf8-in-repo-name`, M18→`total-repos-disagrees` | `python3 -B census/round-40/c3-counter.py --root . --rev <full40> --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch <scratch>` | `549d9ec53a1f5932337ff14438fcd22b0621828d` (`c3-after-d.txt`) |

The frozen C1 instrument demonstrated the named three routed-defect rows; it does not re-derive the prior round's 16-item list in full. The round-40 wave-1 falsifiers also show the C2 pair set and C3 base-fixture identity were not pinned in the frozen preregistration. The output values above are measured, but those claim-scope/freeze gaps are reported as **unprovable** in this round; they are not admission credit. Owned axis values remain unchanged (calibration 7, operability 8, coverage 8): there is no reproducible 0–10 mapping, and no score delta is claimed.

### Round 40 capability rows

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| evidence-bound closure counter | require an anchored line to cite a resolvable ancestor revision, the exact backticked evidence path, and evidence bytes carrying the claimed tokens; reject equal/backwards commits and require a nonempty forged-control set | `python3 -B tests/fixtures/r40-c1-evidence.py --work <scratch>` -> `SUMMARY cases=11 pass=11 fail=0`; `census/round-40/records/c1-after-h.txt` | r40 |
| joined docstring class reader | join indented continuation lines into a class entry and expose the one-line reading as a discriminating control | `census/round-40/records/c2-after-h.txt` -> `legs=7 pass=7 fail=0 harm=0`; fixture joined `9/9`, one-line `6/9` | r40 |
| record-branch mutation battery | score duplicate/multiple TOTAL, `--skip-unrecorded`, invalid UTF-8 and TOTAL-count behavior with per-mutant failing-case attribution | `census/round-40/records/c3-after-h.txt` -> `mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8` | r40 |

### Planned (appended at round 40)

- **r41:** calibration: carry the prior 16 routed predicates forward with per-item evidence pointers and a population-bound counter; operability: freeze the complete class/trigger pair list and its probe names before data, then require class-entry ownership and stable unprivileged errno observations; coverage: freeze the intended base fixture explicitly, retain all r39 record-rule mutants as regression controls, and add first-disagreeing / last-agreeing TOTAL order plus the root-repo discovery case. Certification OFF, K5 HELD, NAMESPACE hold unchanged.

### Round 40 finality correction (measured at the path-bound instrument revision)

The C1 instrument was tightened after the first counter receipt: an evidence pointer now closes only when the anchored line cites BOTH the revision and exact backticked path, the evidence blob carries all claimed `must` tokens and none of the `mustnot` tokens, and a nonempty forged-control set is present. Earlier C1 receipts remain history; the final committed instrument is measured at `dc8bd47c693097a69ccaa39b514ce9689a642edc`: `census/round-40/records/c1-after-h.txt` (`items=3 open=0 forged=3 forged_open=3 forged_closed=0 register_violations=0`, fixture `cases=11 pass=11`), `c2-after-h.txt` (`legs=7 pass=7 fail=0 harm=0`), and `c3-after-h.txt` (`mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8`). The claim-population, cross-claim, source-quote, source-scope and frozen-predicate defects listed in `corpus/lessons/round-40.md` M40-3–M40-13 remain **unprovable**; these finality receipts do not retroactively freeze them.

### Round 40 final SOURCES census (after W2 source corrections)

`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` -> `souji ok`, exit 0; final registry `rows=181`, `W04=52` (`census/round-40/records/census-final.txt`). The C1 D1 cell still names the earlier 178-row/49-warning receipt at its measured revision; because S255-S257 were appended after that measurement, D1 is not a measurement of the final registry and remains unprovable (lesson M40-10).

### Round 41 measurements (2026-10-28; base `7eebc183f2685d1ea9b004b4de22c09a8a4035a7`; preregistration `e2a74312af4233963e44e4dbb38838ece07b8bd2`; instruments `6682b98175b995ee4646ffd1ea6bd8a12cd353dd`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 corrections of three filed r40 statements | calibration 7 | `items=3 mismatched=3 corrected=0 uncorrected=3 junk=0` (do-nothing), junk lesson `junk=3` (`controls/c1-control.txt`) | `items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1` rc 0 | `python3 -B census/round-41/c1-counter.py --root . --rev <full40>` | `31e4d3e758bb903808a9270018d7e5be99ce38a4`; tip `716eaa9e35ffc2643b5cb28981ee474b81b58bf8` |
| C2 runnable freeze check | operability 8 | tool absent: `pass=0`; always-clean stub `pass=2` of 21 (`controls/c2-control.txt`) | `cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red` rc 0 (first landing `119c26f`, hardened final `72e8a0b`) | `python3 -B census/round-41/c2-counter.py --root . --rev <full40> --scratch <dir>` | `119c26fa3bbb85e215824de9538bd2eb34e9f874`, `72e8a0b637ca6243857571d0433fcf7329fe4615` |
| C3 refusal-site battery | coverage 8 | fixture absent; all-PASS stub survives 19/19 (`controls/c3-control.txt`) | `sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10` rc 0 | `python3 -B census/round-41/c3-counter.py --root . --rev <full40> --scratch <dir>` | `a1144120611b00091ac4839559d8ebf38aa9a83a` |
| R1 residual (not a claim) | coverage | fixture absent; stub kills 8, new 0/3 | `mutants=11 killed=11 survived=0 pristine=ok regress=8/8 new_killed=3/3 old_fixtures_killed_new=0 prior=6/6` | `python3 -B census/round-41/r1-counter.py --root . --rev <full40> --scratch <dir>` | `97eeb01e73a9baa3e4191b9052fed9e505c70215` |

Owned scores unchanged (calibration 7, operability 8, coverage 8); no reproducible score mapping. Wave-2 attacks (lesson N1-N19, E1) show the counters score shape; C3 is class-level coverage; the C2 tool was hardened after landing (E1). No admission is claimed by the lane.

### Round 41 capability rows (appended)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| freeze check | read a preregistration at a revision and report missing keys, digest mismatches, a non-red control, frozen-file edits and pre-freeze dispatch files | `census/round-41/records/c2-after-hardened.txt`; `tip-remeasure.txt` | r41 |
| refusal-site battery | probe each of the drift tool's 19 refusal sites with a class-asserting probe, scored by per-site label mutation | `census/round-41/records/c3-after.txt` | r41 |
| record-order fixture | refuse a first-disagreeing TOTAL and cover root-repository discovery | `census/round-41/records/r1-after.txt` | r41 |
| corrections counter | bind CORRECTION lines to values re-derived at a measured revision | `census/round-41/records/c1-after.txt` | r41 |

### Planned (appended at round 41)

- **r42:** calibration: a counter that reads correction prose and rejects fenced, duplicate and retracting lines (N1-N4); operability: freeze-check duplicate keys, malformed headings and unlisted dispatch names (N13) with the hidden-case audit as a frozen leg; coverage: condition-level mutants of the refusal sites (N14), M40-12 decoder mutant, R39-D1/D2 receipts; tool defect N10 (`--json` leaf symlink). Certification OFF, K5 HELD.

### Round 42 measurements (2026-10-28; base `bf618f6c5c09d302994871c94903abbea2deb60d`; instruments `b7408095543579ac71b33ecf7b80b0cb8ef45036`; freeze `afe17f416eec04dcf3f480b580a8f928de61d19d`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 declared-evidence accounting | calibration 7 | the instrument reads `assertions=474 resolved=404 skipped=780 mismatches=70` over `SCORECARD.md` at the base; do-nothing control `registered=0 class_ok=0 corrected=0`, forged all-resolved register `class_ok=42` (`census/round-42/controls/c1-control.txt`) | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` rc 0 (`census/round-42/records/c1-after.txt`); 65 items resolve to one committed path, 5 do not and carry a scoped correction line (`corpus/lessons/round-42.md`) | `python3 -B census/round-42/c1-counter.py --root . --rev <full40> --scratch <dir>`; instrument `python3 -B tools/souji-declared-evidence.py --root . --rev <full40> --file SCORECARD.md --format counts` | `34e33a662cd0d6931e5aa006bd90364e7852c0d5` |
| C2 freeze check hardened | operability 8 | r41 tool: `cases=37 pass=24 fail=13 ... selftest=FAIL patches=0/3` (`census/round-42/controls/c2-control.txt`) | `cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3` rc 0 (`census/round-42/records/c2-after.txt`); self-test 31 cases | `python3 -B census/round-42/c2-counter.py --root . --rev <full40> --scratch <dir>` | `5ad7046d44c3be81ffdb5b2b448cb95a6b03fc96` (tool landed at `133206705f32d785277c1fdf69abd4c73066ba7c`) |
| C3 condition-level drift fixture | coverage 8 | fixture absent: `survived=13`; always-pass stub `survived=13`; byte-sniffing stub `equiv_killed=6` (`census/round-42/controls/c3-control.txt`) | `mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok` rc 0 (`census/round-42/records/c3-after.txt`) | `python3 -B census/round-42/c3-counter.py --root . --rev <full40> --scratch <dir>` | `5ad7046d44c3be81ffdb5b2b448cb95a6b03fc96` |
| R1 landing-gate pointers (residual, not a claim) | calibration | plain-mode gate `findings=3`, fleet-root mode `findings=0` at the base | frozen counter `findings=0 deleted=2 rows_added=0 stale=0` = red by its letter; both gate modes `findings=0` after the repoint (`census/round-42/records/gate-both-modes.txt`); the frozen exemption repair was found to trade modes (lesson M42-2) | `python3 -B census/round-42/r1-counter.py --root . --rev <full40> --scratch <dir>`; `python3 -B tools/souji-landing-gate.py --root . --rev <full40> --round 41 [--fleet-root <fleet>]` | `51f204fb7c633b691a3ca9cd8c0bf025f6e0a093` |

Owned scores unchanged (calibration 7, operability 8, coverage 8); no reproducible 0-10 mapping exists, so no score delta is claimed. The frozen counters score shape: the C1 triple, C2 case table and C3 fixture
reach their targets by wrong artifacts the wave built (lesson N-C1a, N-C2a/b, N-C3a); the lane's compensating checks (five-reader register verification, independent re-derivation, execution-count audit of the landed fixture, static audit of the landed tool) are listed there.
Frontier: `corpus/SOURCES.md` 182 -> 183 rows (S259, tier A, Python `site`, sourced claim C2), census exit 0 both ends (`census/round-42/records/census-before.txt`). Plan-vs-actual against the r41 plan sentence: three of nine planned items done as written (lesson, CORRECTION-SC at line 839).
No axis is claimed harmed; none of the three claims was verified by a non-author on its own substance yet (the round's closure is the non-author check).

### Round 42 capability rows (appended)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| declared-evidence register | account for every unresolvable declared-evidence token of a self-assessment file at a base revision by fixed derivation rules and fail a SCORECARD append that adds a new mismatch or rewrites a base line | `census/round-42/records/c1-after.txt` | r42 |
| freeze-check self-test | build synthetic repositories and exercise the freeze checker's own digest, freeze-detection and ancestry logic, exiting non-zero when any is patched at runtime | `census/round-42/records/c2-after.txt` | r42 |
| condition-level drift battery | observe thirteen single-defect condition mutants of the drift tool that no earlier fixture kills, while killing none of six behaviour-equivalent mutants | `census/round-42/records/c3-after.txt` | r42 |

### Planned (appended at round 42)

- **r43:** calibration: a counter that reads correction prose and rejects fenced, duplicate and retracting lines (the r41 plan sentence, N1-N4, not done in r42), plus the r42 C1 counter's own defects (blank-line sentinel, `> 840` threshold, extra register rows, tilde and four-backtick fences); operability: the hidden-case audit as a frozen leg and the C2 expectation readings (first-wins duplicate key, malformed heading closing a block, a missing `Round:` line, dispatch names at depth); coverage: R39-D1/D2 receipts, N10 (`--json` leaf-symlink tool defect) and a fixture that forwards the tool's traceback without a false red (N-C3b). Certification OFF, K5 HELD.

### Round 42 honest-stop errata (appended; operator wrap-up, run 11)

Wave 2 was stopped by the operator before its seats settled; the lane lands what it verified (see `corpus/lessons/round-42.md` `## Wave 2 errata and honest-stop record`). Corrections to the Round 42 section above: the C3 reading `13/13` is a reading on an idle host and flips under load (1 of 3 tip runs `killed=9`, one loaded run `killed=5`; lesson E-1), so C3 is reported as met on an idle-host reading with a load-sensitivity limit, not as a stable value; the R1 note "the frozen exemption repair was found to trade modes" is wrong: that repair is unsatisfiable by the gate's exemption grammar and the frozen R1 counter ignores the gate's exit status (lesson E-2); no end-of-round source census receipt landed before the stop beyond `census/round-42/records/census-before.txt`. No claim is admitted by the lane; the verdicts are the closure's.

### Round 42 resume (run 12, 2026-10-29; appended)

The honest-stop state above is superseded by completion: the round was re-dispatched (run 12), the inherited landed work re-verified at the final tip `6a3f75941d3604e3459011d599c2c16f3a97b44c`, and the two genuinely stopped wave-2 items (the axis-harm audit and the fixture mutation) completed by a residual wave of 4 attack seats (reports `census/round-42/waves/w3/`). Erratum E-11 (lesson): the stopped set was two seats, not three — `R42w2mutationtester01`'s report landed before the run-11 filing and is in the receipt.

- **Axis-harm audit (R42w3critic01): no durable calibration, operability or coverage regression**; declared-evidence mismatches stayed 70; C2 r41 behaviour retained with the new legs green; C3 read 13/13; the three pre-r42 gate-row differences are each explained in the report (expected: new r42 rows are tip-only; the landing-gate 3→0 is the favourable R1 repoint). The "no axis harmed" side of admission now carries a completed non-L1 audit.
- **Fixture mutation (R42w3mutationtester02): the landed C3 fixture is mutation-robust for its frozen target** (1050 cells; wave-2 partial grid confirmed at 0 disagreements over 634 shared cells; G3 kill reproduced serially under load; coverage findings F1-F4 recorded, no defect).
- **Tool part-A mutation (R42w3mutationtester01): 136 mutants, 67 survivors = 35 equivalent + 30 gaps + 2 real-leg-only** — the 30 gaps extend C2's named part-A coverage limits (r43 list); the frozen target itself is untouched (the counter's case table still reads 37/37 on the honest tool).
- **Independent re-measurement (R42w3reviewer01 + the L1's own run, `census/round-42/records/resume-remeasure-l1.txt`): every SUMMARY field of c1/c2/c3 identical to the committed receipts at the tip**; landing gate `findings=0` both modes with `--round 42`; census `souji ok` rc 0 (rows=183, W04=52).

Owned scores unchanged (calibration 7, operability 8, coverage 8); no reproducible 0-10 mapping, no score delta claimed. No claim is admitted by the lane; the verdicts are the closure's.

### Round 43 measurements (attempt 2, 2026-10-30)

Base `619a75034dd6324e1a725f73034c59f7bf9558ef`; inherited instrument revision
`f8c805dbfa7f45814cf9a7270fa8bbffb41a8373`; formal registration
`8dfad888d7b7673de41cdcd92f30244c16e38519` (late relative to handoff, disclosed).
Measurements below are at `d1954ced70eca671e63684386452cf99fdabea87`.

| claim | axis | before | after | counting command | verdict |
|---|---|---|---|---|---|
| C1 three historical self-assessment corrections | calibration 7 | required=3 registered=0 missing=3, exit 1 (`census/round-43/controls/c1-resume-before.txt`, measured revision in receipt) | required=3 registered=3 missing=0 rederived=3 rederive_failed=0 new_mismatches=0, exit 0 (`census/round-43/records/c1-landed.txt`) | `python3 -B census/round-43/c1-counter.py --root LANE --rev FULL40 --scratch DIR` | counter target met; timing conformance defect remains |
| C2 defensive freeze-check grammar | operability 8 | newtable=2/9 r42table=ok hidden=RED real=RED, exit 1 (`census/round-43/controls/c2-resume-before.txt`) | newtable=9/9 r42table=ok hidden=RED real=ok selftest=ok tmpdir=ok, exit 1 (`census/round-43/records/c2-landed.txt`); self-test 41/41 | `python3 -B census/round-43/c2-counter.py --root LANE --rev FULL40 --scratch DIR` | target unmet: hidden audit h4/h6 contradict the grammar (lesson M43-1); no relaxed target |
| C3 drift-survivor coverage plus leaf-symlink refusal | coverage 8 | killed=0 survived=16 cases=0, exit 1 (`census/round-43/controls/c3-resume-before.txt`) | killed=0 survived=16 cases=0, exit 1 (`census/round-43/records/c3-landed.txt`); production drift tool unchanged | `python3 -B census/round-43/c3-counter.py --root LANE --rev FULL40 --scratch DIR` | target unmet: legacy fixture requires symlink resolution while the new contract requires refusal; candidate not installed (lesson M43-2) |

No numeric score increase: the existing 0–10 labels lack a reproducible mapping. No new capability
row is entered on partial work. Whole-round admission is not claimed: C2/C3 miss and outside
verification is not supplied by lane seats. Certification OFF, K5 HELD, NAMESPACE hold unchanged.

### Planned (appended at round 43)

- Calibration: resolve remaining S259 discovery-channel overstatement using the primary cmdline source and a scoped correction; retain historical append-only records.
- Operability: a newly frozen hidden-audit version must expand class multiplicities and account for post-freeze preregistration edits before any scoring.
- Coverage: explicitly decide the leaf-symlink contract, updating its legacy consumer and new fixture together under a new freeze; do not reinterpret this round's missed target.

### Round 44 frozen attribution and admission limits

Base `55d7af6f5a22340f7a3de1c386e514ababfaa75f`; formal freeze
`d314fd6e85d62565344fa6c4b102f52f62297884`, before ready handoff. Inherited
implementation commits precede that formal freeze, as disclosed in the lesson.
Counter commands are `python3 -B census/round-44/c1-counter.py --root LANE --rev FULL40 --scratch DIR`,
with `census/round-44/c2-counter.py` and `census/round-44/c3-counter.py` substituted for the other claims.

- C1 calibration: before missing=70 means missing r44-format registrations, not
  outstanding factual corrections. The Q76 audit finds 70/70 already accounted
  for, 0 newly unaccounted self-assessment mismatches (`census/round-44/waves/w1/S44reviewer61/report.md`).
  A natural 66-key register stays red because tuple identities disagree in the
  frozen counter; target unmet. No new calibration score or capability claimed.
- C2 operability: repaired hidden oracle 10/10 at freeze, retention preserves the
  old oracle's red; exact first reading in `census/round-44/records/c2-first.txt`.
  This is an oracle repair over unchanged production checker behavior, not a
  new checker capability. Source S264 grounds multiplicity, not oracle truth.
  A size-branching fake audit survives the counter; substance reviews are
  separate evidence, never authentication.
- C3 coverage: joint leaf-symlink cutover and r38 consumer were inherited.
  The finite target covers five prior fixture invocations, not every historical
  suite. Reviewer-found parent-path traceback regressions were repaired;
  `census/round-44/records/c3-parent-before.txt` is 6/8 red and
  `census/round-44/records/c3-parent-after.txt` is 8/8 green.

Scores remain calibration 7, operability 8, coverage 8; delta 0, no reproducible
0–10 mapping. No capability row is entered on these limited results. C1's frozen
miss bars whole-round admission; do not relax its target or repair its counter
after scoring. Certification OFF, K5 HELD, NAMESPACE hold unchanged.

### Round 44 committed measurements

| claim | before | after | measured commit | evidence |
|---|---|---|---|---|
| C1 calibration registration | missing=70, lesson absent, exit 1 at formal freeze | population=70 corrections=66 registered=0 missing=70 new_mismatches=0, exit 1; target unmet, already-accounted population | `c14d20a679bf8edd6dd796c303272f7f14da4145` | `census/round-44/records/c1-final.txt`; before `census/round-44/records/c1-before.txt` |
| C2 operability oracle repair | historical r43 audit 8/10, exit 1; distinct oracle baseline | population=ok retention=ok hidden_v2=10/10 clean_stub=REJECTED findings_stub=REJECTED controls_ran=ok selftest=ok tmpdir=ok, exit 0 | `395552194348873622b39651c971fa909af0d939` | `census/round-44/records/c2-after.txt`; control `census/round-44/controls/c2-donothing.txt` |
| C3 defensive coverage cutover | surface=RED tool_class=RED legacy_case=RED battery=RED, exit 1 at base | surface=ok tool_class=ok legacy=ok legacy_case=ok legacy_base=ok battery=ok both stubs REJECTED prior=5/5, exit 0; operator provenance open | `395552194348873622b39651c971fa909af0d939` | `census/round-44/records/c3-after.txt`; base `census/round-44/waves/w1/S44executor65/missing-fixture.stdout.txt` |

Commands are the three explicit round-44 counter commands above; `--rev` is
the measured commit and `--scratch` an explicit private directory. Source census
exit 0 before/after: `census/round-44/records/census-before.txt`,
`census/round-44/records/census-after.txt`. Captured wave evidence verifies
405 records, failed=0 uncovered=0 at the C1 measured commit
(`census/round-44/records/capture-committed.txt`).

### Planned (appended at round 44)

- Calibration: a newly frozen feasible honest-register counter with consistent
  tuple identities and a Q76-honouring population; do not double-credit r42.
- Operability: execution-bound audit attribution and a non-memorizer substance
  check; fixed output alone remains insufficient.
- Coverage: preserve the finite five-suite scope and route the operator's
  symlink-contract disposition without treating technical green as approval.

### Round 45 bounded measurement repair

One declared claim C1, calibration capability: feasible historical register verification.
Freeze and measured instrument revision `019bccc9ac97f3cec1a1dea574cc2f81f57fc967`.
The old counter on base `ddccb2000e9d6e7963da723cc0548750bb0d6c15` reads
registered=0, missing=70, instrument_mismatches=66, exit 1
(`census/round-45/controls/before.txt`). The new instrument reads population=70,
unique=66, registered=66, missing=0, derived_mismatches=0, historical_credit=0,
exit 0 (`census/round-45/records/c1-after.txt`). This compares different instruments,
not a before/after reduction in false historical beliefs. Numeric delta 0;
calibration 7, operability 8, coverage 8 unchanged. Axis-fit admission remains
the independent closure's decision; no new factual correction credit asserted.

Counting command: `python3 -B census/round-45/c1-counter.py --root LANE --rev FULL40 --scratch EXTERNAL_DIR`.
External discrimination: `python3 -B tests/fixtures/r45-register-feasibility.py --root LANE --rev FULL40 --scratch EXTERNAL_DIR`
reads cases=12 pass=12 fail=0 (`census/round-45/records/fixture-after.txt`).
Honest pre-freeze register passes three times; a single false token reads
derived_mismatches=1, missing=0, exit 1 (`census/round-45/controls/wrong.txt`).
The already-accounted 70 occurrences are not re-credited (Q76).

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| feasible historical register verification | re-derive the filed 66-key R44 register against declared historical blobs using consistent identities, with single-wrong-token discrimination; no historical correction or execution credit | census/round-45/records/c1-after.txt; census/round-45/records/fixture-after.txt; command above | r45 |

### Planned after round 45

- Retain independent closure's axis-fit decision. Execution-bound audit attribution
  remains open; it was not declared as a second claim. The operator symlink-contract
  disposition remains open. Do not enlarge the historical five-suite scope or infer
  approval from technical green. Certification OFF, K5 HELD, NAMESPACE unchanged.

### Round 45 operator honest-stop disposition

C1 exact finite target met, but calibration axis improvement is unprovable:
the new counter already accepts the base register, so different-instrument
0-to-66 is not a reduction in outstanding false beliefs. The capability row
above records first working execution only, not admission or a score gain.
Operator wrap-up releases the validated 64-seat plan WITHOUT dispatch:
dispatched=0, completed=0, dead=0. No WAVE-DONE is fabricated; L2 floor
was not met. No closure this run; next round unchanged.
Evidence: census/round-45/records/operator-stop.json and the lesson's
Admission distinction section. Certification and all holds unchanged.


### Round 46 landing (frozen claims executed on the Windows host; base 7f8fa3cad0685a8822198b04f2a424bae44b140b)

Frozen preregistration `census/round-46/preregistration.txt` (2026-10-30,
before any wave dispatch; the freeze session died before after-data). This
session lands the claims with one disclosed host adaptation (Amendment 1,
prereg-appended) committed before the after-measurements.

| claim | axis | before -> after | counting command | measured commit |
|---|---|---|---|---|
| C1 tip landing-suite receipt | calibration 7 | frozen counter on this host: exit 2 could-not-evaluate (`census/round-46/records/c1-host-before.txt`; Amendment 1) -> `SUMMARY assertions=522 mismatches=70 registered=70 corrected=0 exempted=0 unfiled=0`, exit 0; do-nothing control (freeze, committed pre-after): unfiled=70 FAILS; pin kill-rule mutation witness exit 2 on r28 rev ed270c4 | `python -B census/round-46/c1-counter.py --root LANE --rev FULL40 --work SCRATCH` (recorded in the receipt) | receipts committed this round; counter bytes 3144c16bde21380bcbedcb783897d01bc2ee3602, green run re-taken at the round's final tip (see LOG.md round-46) |
| C2 register-verifier selftest | operability 8 | base: `--selftest` exits 2 unrecognized-argument (frozen r45 bytes) -> `SUMMARY cases=11 pass=11 fail=0`, exit 0; default path byte-identical to frozen r45 bytes: after-receipt and wrong-token receipts reproduce SUMMARY+exit exactly | `python -B census/round-45/c1-counter.py --selftest --scratch SCRATCH`; `python -B census/round-45/c1-counter.py --root LANE --rev 019bccc9ac97f3cec1a1dea574cc2f81f57fc967 --scratch SCRATCH [--register-file WRONG]` | bytes bc50661fc72522356625c53043959e7df915f56f; receipts `census/round-46/records/c2-selftest.txt`, `census/round-46/records/c2-repro-after.txt`, `census/round-46/records/c2-repro-wrong.txt`, expected table `census/round-46/records/c2-selftest-expected.tsv` |
| C3 F4 restore-collision entry | coverage 8 | grounded F4 `8` -> `9`; gate-check `entries=1 ok=1 fail=0`; sources-census exit 0 rows 191 -> 193; coverage-agreement at the measured rev (see LOG) | `grep -lE '^ground: F4' corpus/knowledge/*.md | wc -l`; `python -B tools/souji-gate-check.py --root . --round-date 2026-10-30 --entries corpus/knowledge/quarantine-restore-path-reoccupied.md --snapshot-dir census/round-46/sources` | entry + S268/S269 landed; measured at the round's final content tip (see LOG.md round-46) |

Numeric axis scores unchanged (calibration 7, operability 8, coverage 8): C1
re-derives already-committed dispositions (no new corrected beliefs); C2
closes a disclosed interface debt (capability-adjacent, recorded in the r45
registry row's self-test cell, not a new capability row); C3 adds one entry
on existing frontier ground (no Core promotion). Host corrections recorded:
lane conf path absent on this host (PROVINCE.md, lesson); six
control-char-named HEAD paths uncheckoutable here (Amendment 1 tolerance;
probe receipt `census/round-46/records/c1-host-uncheckoutable.txt`). Session-workspace dry-run
census landed read-only (`census/round-46/workspace-census.tsv`): 17 lane
clones (14 pushed, 3 no-origin-master), 15 foreign live scratch dirs
untouched, no removal proposed. L2 floor: no wave surface on this host;
dispatched=0 (lesson L2 note; L0 question filed).

### Planned (r47, appended 2026-10-31)

- Convert the r46 workspace dry-run census into per-artifact receipts for the
  three `no-origin-master` lane clones and the foreign `helpers-r74/` root
  (coverage; quarantine-before-delete discipline, operator approval first).
- Close the L0 question on the L2 floor for this host (whatever the operator
  rules: dispatch surface or standing waiver) (operability).
- Re-run the whole-suite tip receipt at the next round's tip (calibration;
  keeps the landing-suite claim a standing instrument, not a one-off).

### R46 carry-in corrections (round 47, appended 2026-10-31; the base bytes above stand as written)

R46-CORRECTION SCORECARD.md:1012 C1 cell: the stale literal assertions=522 is superseded by the measured value assertions=533. census/round-46/records/c1-tip-green.txt prints SUMMARY assertions=533 mismatches=70 registered=70 corrected=0 exempted=0 unfiled=0 at the round-46 final tip 32f48da04846489aeb8f6c5662e9bacd742bf245, the round-46 non-author verifier re-derived 533 independently (corpus/lessons/round-46-verifier-spotcheck.md section 3, C1), and this lane re-ran the same frozen counter at e469084b6b5630d0c248574fdd980775deeb1efd with the identical SUMMARY, exit 0 (census/round-47/records/c1-base-green.txt). The cell above stays as written.

R46-CORRECTION round-46 report prose: "56 W04 duplicate-url warnings" is superseded by 57. grep -c W04 over census/round-46/records/census-after.txt reads 57, and the round-47 before-census re-run of the explicit-lane-directory validator reproduces 57 (census/round-47/records/census-before.txt, rc 0). Erratum recorded here, in the round-47 LOG entry and in the round-47 report.

R46-CORRECTION round-46 report before-census citation: naming records/census-before.txt as the new-host before state is imprecise — that file is the old-host conf-name receipt (its last line reads souji ok /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md, unchanged since the freeze base). The host-valid new-host before evidence is records/census-conf-name-host.txt (conf-name form, rc 2, souji missing) plus an explicit-lane-directory receipt; this round commits one at census/round-47/records/census-before.txt (rc 0, 57 W04), which the round-47 report cites as the base.

### Round 47 measurements (2026-10-31; base e469084b6b5630d0c248574fdd980775deeb1efd; freeze 0027c977452e06d041a750a5a8c33b1fd5de57db; preregistration census/round-47/preregistration.txt, freeze-check claims=2 findings=0 exit 0)

| claim | axis | before -> after | counting command | measured commit |
|---|---|---|---|---|
| C1 r46 carry-in corrections + standing landing-suite receipt | calibration 7 | append-only correction rows 0 -> 3 (each row starts with the correction marker); at base all three defects live with no committed correction (census/round-47/controls/c1-control-donothing.txt, EXIT=1) -> each carried by an append-only row citing a receipt blob and a resolvable revision; frozen r46 counter green at base (assertions=533 unfiled=0, records/c1-base-green.txt) -> green re-derived at the round-47 tip (unfiled=0; the tip receipt lands in the round's final end-receipts commit) | grep -c "^R46-CORRECTIO[N]" SCORECARD.md (0 at base -> 3 at tip; the [N] class keeps the command pasteable without embedding the marker literal in this file); python -B census/round-46/c1-counter.py --root . --rev TIP --work SCRATCH; python -B tools/souji-freeze-check.py --root . --prereg census/round-47/preregistration.txt --rev 0027c977452e06d041a750a5a8c33b1fd5de57db -> claims=2 findings=0 | content tip of this round (see LOG.md round-47); SCORECARD bytes unchanged after the content commit, so the same SUMMARY re-derives at the final tip |
| C2 per-artifact receipts for the four r46 census candidates | coverage 8 | receipt rows for the 4 targets: absent at base (control rc=128) -> 4 VERDICT rows, every verdict NOT-SAFE (kotodama secrets-refusal; binary-forensics dirty unpushed=0 dirty=153; reverse-engineering secrets-refusal; helpers-r74 none) ; frozen counter at the tip: RECEIPTS rows=4 targets=4 findings=0, exit 0 | python -B census/round-47/c2-counter.py --root . --rev TIP; raw invocation receipt census/round-47/records/per-artifact-receipts.tsv with provenance index records/receipt-commands.txt | content tip of this round (see LOG.md round-47) |

Numeric axis scores unchanged (calibration 7, operability 8, coverage 8): C1
lands the bookkeeping corrections the r46 closure routed (calibration of the
record — the verifier had already re-derived both values; no new corrected
beliefs). C2 converts census classifications into per-artifact receipts on
live/protected targets — every verdict NOT-SAFE, nothing moved, deleted, or
proposed for removal (receipts advisory, certification OFF). No capability
row: no new capability is demonstrated; C2 runs the installed tool over new
targets. Enabling host work this round, disclosed and mined: (1) targeted
index repair after the e469084 landing drift (lesson round-47 ## Mistakes
row 1); (2) tools/souji-verify.sh find_repo_for termination repair for
artifacts outside any repository on this host — base-vs-candidate selftest
identical (exit 1, 47 checks, same 8 pre-existing host failures;
records/verify-selftest-base.txt vs -repaired.txt), the registered
r17-jj-receipts gate is could-not-evaluate here because the fixture
hard-codes /var/tmp and this host cannot create it
(records/r17-jj-receipts-repaired.txt). L2 floor: no dispatch surface on
this host; dispatched=0 (standing L0 question, routed around; nothing
assumed answered).

### Planned (r48, appended 2026-10-31)

- Carry the C2 receipts to dispositions the operator owns: binary-forensics
  has live unpushed work (do nothing), kotodama/reverse-engineering carry
  secret-shaped descendants (route findings to kagi/operator, never read
  them), helpers-r74 stays a stale-candidate pending operator approval
  (quarantine-before-delete; no removal proposed this round).
- Re-run the standing landing-suite receipt at the r48 tip and the r46
  counter's Amendment-1 precondition check (porcelain == exactly the six
  tolerated rows) after every landing, per the round-47 lesson practice.
- Whole-suite tip receipt again (calibration, standing); sources-census
  before/after with the explicit-lane-directory form on this host.

### Round 48 landing (carry-in closures; base 8e17a4b1a8f8bd81dd5a978e698e447bd4253b3e; freeze 21ec27361c1ded8d93842b2e89239e874e30f875; Amendment 1 5ca5001b358eca55b70f1da63f8c0c5c3b27b945 — both before any claim receipt; prereg blob byte-unchanged, freeze-check claims=2 findings=0 exit 0 at freeze, amendment, and tip)

| claim | axis | before -> after | counting command | measured commit |
|---|---|---|---|---|
| C1 standing landing-suite receipt restored without manual repair (capability acquisition) | calibration 7 | the frozen r46 counter at the round base B: exit 2 could-not-evaluate, "dirty worktree at run time: 2 unexpected rows" (the r47 mistake-1 class recurring; control census/round-48/controls/c1-control-donothing.txt, EXIT=2) -> exit 0 at B AND at the round's content tip T: SUMMARY assertions=538 mismatches=70 registered=70 corrected=0 exempted=0 unfiled=0; every host-index restoration performed by the committed fail-closed tool (base drift receipt: BEFORE 38 rows tolerated=6 repairable-paths=16 -> AFTER rows=6 unexpected=0; the tool's own landings repaired by itself in -content.txt and -end.txt; the terminal landing's repair receipt stages in session scratch and is quoted in the round report); Amendment-1 six-path set not widened (NTFS base/tip re-checks read exactly 6); selftest cases=5 pass=5 fail=0 | python -B census/round-46/c1-counter.py --root . --rev 8e17a4b1a8f8bd81dd5a978e698e447bd4253b3e --work SCRATCH (base, after the receipted repair: census/round-48/records/c1-base-green.txt); python -B tools/souji-idx-repair.py --root . --rev <full40> --receipt <path outside the repo>; python -B tools/souji-idx-repair.py --selftest (census/round-48/records/idx-repair-selftest.txt) | content tip of this round (see LOG.md round-48); SCORECARD bytes unchanged after the content commit, so the same SUMMARY re-derives at the final tip |
| C2 census conf-name host adapter (the contract's census command, runnable on this host) | operability 8 | at base B the adapter is absent (control: git cat-file -e rc 128) and the contract conf-name census form exits 2 "souji missing" (census/round-48/records/census-confname-before.txt) -> the committed adapter runs the contract command end-to-end: its raw receipt records the conf form's rc-2 verdict verbatim beside the explicit-lane-directory form's rc-0 shokunin-repo-hygiene ok line and exits 0 (CENSUS-RUN lane=souji conf_rc=2 dir_rc=0); the frozen r48 counter at T reads CENSUS-RUN forms=2 findings=0, exit 0; selftest cases=3 pass=3 fail=0 (arm A1 reproduces the host condition synthetically with the real fleet script) | bash tools/souji-census-run.sh --fleet-root FLEET --lane souji (receipt census/round-48/records/census-runner-output.txt); python -B census/round-48/c2-counter.py --root . --rev TIP; bash tools/souji-census-run.sh --selftest | content tip of this round (see LOG.md round-48) |

Numeric axis scores unchanged (calibration 7, operability 8, coverage 8): C1
re-derives the standing receipt with the same frozen instrument and adds a
repair capability — no corrected beliefs about the corpus; C2 makes a
documented host correction runnable without changing the census verdicts
(before 58 W04 / rows 194; after receipt lands with the end receipts, exit 0
required). No knowledge entry, no Core promotion. Enabling host work this
round, disclosed and mined: the Amendment-1-prereg blob stays byte-identical
(the amendment lives beside it, so freeze-check reads findings=0 at every
revision); the receipt-staging discipline (a receipt written into the repo
pollutes the next run's porcelain) is named in SKILL.md and the lesson. L2
floor: no dispatch surface on this host; dispatched=0 (standing L0 question,
routed around; nothing assumed answered).

### Round 48 capability rows (appended)

| host-index repair (receipted, fail-closed) | restore the worktree to the frozen Amendment-1 tolerance after any index-free-helper or integrator landing, without a manual step; repair only sha256-proven stale-landing paths with the rev's own mode+blob (S271); refuse — repairing nothing — any row it cannot prove; never widen the six-path set | `python -B tools/souji-idx-repair.py --selftest` (census/round-48/records/idx-repair-selftest.txt, cases=5 pass=5 fail=0); real drift receipt `census/round-48/records/idx-repair-base.txt`; the pre-amendment refusal it supersedes: `census/round-48/records/idx-repair-base-refused-plain-porcelain.txt` | r48 |
| census conf-name host adapter | run the round contract's census command on this host end-to-end (exit 0) while recording the conf form's raw rc-2 `souji missing` verdict — disclosed, never masked — with the fleet script's sha256 for provenance | `bash tools/souji-census-run.sh --selftest` (census/round-48/records/census-runner-selftest.txt, cases=3 pass=3 fail=0); real receipt `census/round-48/records/census-runner-output.txt` (CENSUS-RUN lane=souji conf_rc=2 dir_rc=0); frozen counter `python -B census/round-48/c2-counter.py --root . --rev <tip>` | r48 |

### Planned (r49, appended 2026-11-01)

- Carry the r48 receipts to their operator-owned dispositions: the four r47
  per-artifact receipt targets keep their r47 dispositions (binary-forensics
  live unpushed work: do nothing; kotodama/reverse-engineering
  secret-shaped descendants: route to kagi/operator, never read;
  helpers-r74: stale-candidate pending operator approval).
- Re-run the standing landing-suite receipt at the r49 tip with the r48
  repair practice after every landing (calibration, standing); the r48
  adapter as the census form (operability, standing).
- Whole-suite tip receipt again (calibration); sources-census before/after
  via the r48 adapter (the conf-form receipt travels with the dir-form
  verdict).

### Round 49 landing (r48-closure routed defects; base 5a26fbfd5b0f94b0d8283908a0f4b876b2857bfc; freeze attempt 1 ebebc44c0ccd8941dd4cc1fc4dd71452ab9027fa superseded before any after-data, attempt 2 445321aa61cfafb95b623a5fe1c0126c0a60186f operative; prereg blob byte-unchanged, freeze-check claims=1 findings=0 exit 0 at the attempt-2 freeze)

| claim | axis | before -> after | counting command | measured commit |
|---|---|---|---|---|
| C1 the freeze-check selftest re-derivable on this host (r48 routed defect 1; instrument repair, not a capability) | calibration 7 | at base B the committed tool bytes read SELFTEST cases=41 pass=4 fail=37 EXIT=1 (census/round-49/controls/freeze-selftest-base-red.txt) and the digest-pinned r49 counter over the same bytes reads selftest=FAIL (41, 4, 37) patches=0/3 real=ok retro=red retro_clean=ok, exit 1 (controls/c1-control-donothing-r2.txt) — the r42 registry gate r42-freeze-check-selftest had no obtainable green on this host -> after the fixture writer is ported to binary mode (verdict code byte-identical; diff receipt census/round-49/records/tool-diff-base-to-fix.txt: exactly the writer hunk + its docstring line), the raw selftest at the content tip T reads cases=41 pass=41 fail=0 EXIT=0 (records/freeze-selftest-fixed-green.txt, taken on the fixed bytes pre-landing) and the SAME counter at T re-derives the gate green: selftest=ok patches=3/3 real=ok retro=red retro_clean=ok, exit 0 (the committed-bytes receipt lands with the end receipts; patches=3/3 proves the repaired selftest still discriminates) | python -B tools/souji-freeze-check.py --selftest (raw; base vs fixed receipts above); python -B census/round-49/c1-counter.py --root . --rev <full40> --scratch DIR (base receipt committed at freeze; tip receipt in the end receipts); the legs real/retro/retro_clean are identical at B and T — the verdict path is unchanged | content tip of this round (see LOG.md round-49); the end receipts re-derive the counter at the final tip |

Numeric axis scores unchanged (calibration 7, operability 8, coverage 8): C1
repairs one inherited instrument's fixture harness to its own registered
semantics — a self-assessment gate now matches observed host state; no new
surface, no new capability row, no corrected corpus belief. The sweep receipt
(census/round-49/records/fixture-hazard-sweep.txt) classifies the rest of the
inventory: one digest-bound writer in tools/ (repaired), frozen census
counters carry the class as named limits, never edited.

### Planned (r50, appended 2026-11-01)

- Re-run the standing landing-suite receipt at the r50 tip with the r48/r49
  repair practice after every landing (calibration, standing); the r48 census
  adapter as the census form (operability, standing).
- Carry any r49-closure routed defects as claims; if none, a coverage move
  from the PROVINCE frontier (F1/F2/F4) with a committed counter, or the
  frozen-counter named limits (r42 c2 counter unrunnable here: no python3
  interpreter name + its own text-mode fixture class) turned into a
  documented host-execution contract if the operator asks for one.
- Whole-suite tip receipt again (calibration); sources-census before/after
  via the r48 adapter (the conf-form receipt travels with the dir-form
  verdict).

### Round 50 landing (r49-closure routed items; base 5f921fe261770b68266793c767d35a56758536c5 = the r49 non-author spot-check commit, verdict ok/admitted; freeze 3cc69c455d000c4d6fc71031e081f15882a97ffd before any claim receipt; preregistration census/round-50/preregistration.txt, freeze-check claims=2 findings=0 exit 0 at the freeze)

| claim | axis | before -> after | counting command | measured commit |
|---|---|---|---|---|
| C1 the S267 token readings re-derivable by committed command | calibration 7 | at base B none of the claim's blobs exist: PRISTINE FAIL TOOL-ABSENT, exit 1 (control census/round-50/controls/c1-control-donothing.txt) -> at the content tip T the frozen counter prints `SUMMARY reading=ok footer=ok body=ok erratum=ok sourced=ok selftest=ok content_histor=0 raw_histor=1 content_factual=0 raw_factual=0 tool_sha=5923b315fe6f`, exit 0: the r49 record's "zero occurrences of histor*" is re-derived as a content-scope zero with the raw-scope footer occurrence (1) disclosed beside it; the append-only `S267-COUNT-ERRATUM` line lands in corpus/lessons/round-50.md; the SAME counter bytes measure both ends (r45 limit structurally avoided; feasibility receipts: the counters' synthetic-tip green runs and the two counter defects they exposed are in the lesson's Mistakes) | `python -B census/round-50/c1-counter.py --root LANE --rev FULL40 --scratch DIR` | content tip of this round (see LOG.md round-50) |
| C2 census receipts that verify (capability acquisition) | operability 8 | at base B the tool is absent: PRISTINE FAIL TOOL-ABSENT, exit 1 (control census/round-50/controls/c2-control-donothing.txt) -> at T the frozen counter prints `SUMMARY receipts=1 verified=1 selftest=ok before=ok tool_sha=1d092142eb73`, exit 0 over the before-receipt alone; at the round's FINAL tip `receipts=2 verified=2` (the after-receipt lands with the end receipts) — every verify check green including adapter-sha and fleet-script-sha; the tool's selftest refuses five tamper/malform arms each at its named class | `python -B census/round-50/c2-counter.py --root LANE --rev FULL40 --scratch DIR`; `python -B tools/souji-census-receipt.py verify --receipt census/round-50/records/census-before-receipt.txt --fleet-root FLEET` | content tip (before-receipt leg) and the final tip (both receipts; see LOG.md round-50) |

Numeric axis scores unchanged (calibration 7, operability 8, coverage 8): C1
re-derives readings the record already stated (a record-accuracy instrument —
no new factual correction credit; the underlying S267 rejection was already
right and stays right); C2 upgrades the artifact class the round contract
mandates every round — no new census verdicts, no widening (the conf form's
rc-2 host state stays disclosed inside every receipt). No knowledge entry, no
Core promotion. The sourced claim is C1 (S273, html.parser
convert_charrefs contract, opened live 2026-11-01). L2 floor: no dispatch
surface on this host; dispatched=0 (standing L0 questions routed around;
nothing assumed answered). Assimilation: none (no considerthese/ directory;
shokuknow unreachable).

### Round 50 capability row (appended)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| verifiable census receipts (r50) | capture the r48 census adapter's run into a digest-bound v1 receipt (the adapter's raw output embedded verbatim; fleet-script and adapter sha256 recorded; the conf form's raw rc-2 verdict disclosed inside) and verify one later by re-deriving every header value from the embedded raw output and re-hashing both scripts; five tamper/malform shapes each refused at a named class | `TMPDIR=<scratch> python -B tools/souji-census-receipt.py --selftest` (cases=6 pass=6 fail=0, census/round-50 records receipts at the landing); `python -B tools/souji-census-receipt.py verify --receipt census/round-50/records/census-before-receipt.txt --fleet-root <fleet>` (VERIFY ok, checks=grammar,digest,raw-section,rc,w04,result,adapter-sha,fleet-script-sha); frozen counter `python -B census/round-50/c2-counter.py --root LANE --rev FULL40 --scratch DIR` | r50 |

### Planned (r51, appended 2026-11-01)

- Re-run the standing landing-suite receipt at the r51 tip with the
  r48-r50 repair practice after every landing (calibration, standing); the
  census before→after lands in the v1 receipt form at both ends
  (operability, standing now that the r50 receipts made it verifiable).
- Carry any r50-closure routed defects as claims; the census conf-form
  question stays operator-owned (the r50 consolidated L0 proposal line is
  on file; routed around until ruled).
- Whole-suite tip receipt again (calibration); if the operator rules on
  the r48/r50 census-form questions, adapt the standing receipt flow to the
  ratified form in the same round.

### Round 51 landing (r50-closure routed items + the live workspace census; base d1b8734d835171c7329225fdaab249c5c6799de8 = the r50 non-author spot-check commit, verdict ok/admitted; freeze 851093b670e3fd1416df326d0479168222959ed1 before any claim receipt; preregistration census/round-51/preregistration.txt, freeze-check claims=2 findings=0 exit 0 at the freeze)

| claim | axis | before -> after | counting command | measured commit |
|---|---|---|---|---|
| C1 the r50-closure routed record-accuracy corrections land append-only + the standing landing-suite receipt green at the final tip | calibration 7 | at base B both corrections are absent: the counter is red, exit 1 (`SUMMARY corr=FAIL dup=ok ntfs=FAIL listing=ok corr_lines=0`, control census/round-51/controls/c1-control-donothing.txt) -> at the content tip T the frozen counter prints `SUMMARY corr=ok dup=ok ntfs=ok listing=ok corr_lines=1 dup_base=2 dup_tip=2`, exit 0: the duplicated "Reject sample" bullet stays verbatim twice at BOTH revs (append-only proven) beside exactly one `R51-CORRECTION` line naming it, and the r50 NTFS tip receipt gains exactly one `quoted_d_rows=6` line with its six-path listing byte-identical to base; PLUS the standing suite receipt: the r50 tip-state receipt read `COULD-NOT-EVALUATE dirty worktree … 31 unexpected rows` exit 2 (census/round-50/records/c1-suite-tip-50.txt, the r50 closure's directed ordering fix) -> the r46 frozen counter green (exit 0, `unfiled=0`) at the content tip and at the FINAL tip after the terminal idx-repair (receipts in the end receipts; the final-tip receipt quoted in the round report) | `python -B census/round-51/c1-counter.py --root LANE --rev FULL40 --base-rev d1b8734d835171c7329225fdaab249c5c6799de8 --scratch DIR`; suite: `python -B census/round-46/c1-counter.py --root LANE --rev FULL40 --work SCRATCH` | content tip of this round (see LOG.md round-51); SCORECARD bytes unchanged after the content commit |
| C2 the session-workspace live census refresh with per-artifact receipts and a derivable r46->r51 drift receipt (sourced on S274) | coverage 8 | at base B the r51 census blobs do not exist: `PRISTINE FAIL WORKSPACE-CENSUS-ABSENT`, exit 1 (control census/round-51/controls/c2-control-donothing.txt) -> at T the frozen counter prints `SUMMARY shape=ok drift=ok receipts=ok limit=ok rows=126 added=79 removed=2`, exit 0 over the committed capture census/round-51/workspace-census.tsv (the live 2026-11-01 dry-run census: 17 lane clones = 14 pushed + the same 3 no-origin-master as r46; 89 active-foreign-scratch rows vs r46's 19; new top-level candidate scratch-r80v), the drift receipt census/round-51/records/ws-drift-vs-r46.tsv (every COUNT line and ADDED/REMOVED key row re-derives from the two committed captures, header rows excluded), per-artifact receipts census/round-51/records/per-artifact-receipts.tsv (helpers-r74: NOT-SAFE, disposition unchanged pending operator approval; scratch-r80v: NOT-SAFE secrets-refusal — foreign, active, untouched; nothing moved, nothing deleted, no removal proposed), and the S274-grounded pushed-receipt limit named in census/round-51/workspace-census.txt (no r51 lane row is in the copied-history state; disclosed, not exercised) | `python -B census/round-51/c2-counter.py --root LANE --rev FULL40 --base-rev d1b8734d835171c7329225fdaab249c5c6799de8 --scratch DIR`; `grep -c -P "\tin-use/pushed\t" census/round-51/workspace-census.tsv` (14); `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78); `grep -c "^| S274 |" corpus/SOURCES.md` (1) | content tip of this round (see LOG.md round-51) |

Numeric axis scores unchanged (calibration 7, operability 8, coverage 8): C1
repairs the two routed record defects append-only and restores the standing
receipt ordering the closure directed (no new corrected beliefs about the
corpus); C2 re-censuses the round contract's census surface on the live
workspace — installed tools over live targets (the r47 precedent, no
capability row), dry-run, no removal proposed, no authority taken. SOURCES
197 -> 198 (S274, opened live 2026-11-01, the sourced claim is C2). Three
counter defects caught pre-freeze by the feasibility/receipt review and mined
(corpus/lessons/round-51.md ## Mistakes); the discarded first census take
(`.zcode` scope) disclosed there too. L2 floor: no dispatch surface on this
host; dispatched=0 (standing L0 questions routed around; nothing assumed
answered). Assimilation: none (no considerthese/ directory; shokuknow
unreachable).

### Planned (r52, appended 2026-11-01)

- Carry any r51-closure routed defects as claims; the census conf-form
  question stays operator-owned (r50 consolidated L0 proposal; routed around
  until ruled).
- Standing receipts again (calibration, standing): the landing-suite receipt
  at the r52 tip after the terminal repair; census before→after in the v1
  receipt form at both ends; NTFS exclusion re-check at both ends (6 paths,
  not widened).
- Workspace census cadence: if the operator rules on a standing cadence for
  the session-workspace census (r51 was a 5-round refresh after r46), adopt
  the ruled cadence; otherwise refresh again when the workspace surface
  drifts (new top-level entries or clone-state changes vs the r51 capture),
  keeping the dry-run/no-removal discipline.
- helpers-r74 and scratch-r80v keep their NOT-SAFE receipts and
  operator-owned dispositions (quarantine-before-delete; no removal
  proposed); re-receipt them only if their state changes.

### Round 52 measurements (2026-11-03; base f778b9d131574d3ff09c0cc8a077643c0fc84bb4; freeze df7d1300cbc5443b748682598e35b29347bfa930; prereg census/round-52/preregistration.txt)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 declared-count annotations agree (enumerated sites S1 = SCORECARD.md:1196, S2 = census/round-51/preregistration.txt:125; the r51 ADDED-count command states 78, recomputes 79) | calibration 7 | `SUMMARY sites=2 mismatches=2 filed=0 unfiled=2`, exit 1 (census/round-52/controls/c1-control-donothing.txt) | `SUMMARY sites=2 mismatches=2 filed=2 unfiled=0`, exit 0 at the commit whose subject begins "round-52: C1 corrections" (both sites filed; the stale text stays in place, append-only) | `python3 -B census/round-52/c1-counter.py --root LANE --rev FULL40 --scratch DIR` | base f778b9d1; after = the "round-52: C1 corrections" commit (named in the round report) |
| C2 fleet-root census capture verifies (capability acquisition) | coverage 8 | `PRISTINE FAIL FLEET-CENSUS-ABSENT`, exit 1 (census/round-52/controls/c2-control-donothing.txt) | `SUMMARY entries=49 rows=49 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok`, exit 0 | `python3 -B census/round-52/c2-counter.py --root LANE --rev FULL40 --scratch DIR` | measured at 8ec412c64d73d8c5e339f1d15d11cfc5b6e702d0 (the capture commit) |

C1 verifies by the frozen counter. Its named limits (first-annotation reading, unpinned recompute source, fenced corrections accepted, in-place rewrite accepted at one revision, an inert correction exits 0 where the prereg text says it kills) are recorded in corpus/lessons/round-52.md `## Wave findings`; each was checked by hand at the tip, with the commands in the round report. C2 verifies by the frozen counter. Its named limits (a hand-written capture with the right tool bytes verifies; sort order and `#`-leading names are not instrumented; the derivation of `ignored` is not pinned by the predicate) are recorded in the knowledge entry and the lesson. No owned axis score changed (calibration 7, coverage 8, operability 8): C1 is a record-accuracy instrument and C2 a capability on an owned surface; no reproducible 0-10 mapping is asserted. The lane claims no round admission; the non-author closure decides.

### Round 52 corrections (append-only; C1 filing)

The stale annotations at the two enumerated sites stay in place. Each is filed by one line:

R52-CORRECTION SCORECARD.md:1196 stale=78 recomputed=79

R52-CORRECTION census/round-51/preregistration.txt:125 stale=78 recomputed=79

### Round 52 capability row (appended)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| fleet-root census (read-only) | list the fleet root's top-level entries with kind, tracked, ignored, class and report-only disposition into a capture outside the root; refuses repo configs that could execute or read outside the root, credential-shaped names, credential namespaces and in-root output | `python3 -B tools/souji-fleet-root-census.py --selftest` (census/round-52/records/tool-selftest.txt: checks=39 failures=0); `python3 -B census/round-52/c2-counter.py --root LANE --rev FULL40 --scratch DIR` (SUMMARY ... receipt=ok) | r52 |

### Planned (r53, appended)

- C1 counter amendment as a new frozen version: exactly one annotation per site line; the recompute source pinned by sha256 in the prereg; an inert correction kills; an append-only check across base→tip (zero deleted lines); fenced corrections refused. Axis: calibration.
- C2 counter amendment: rows sorted by name are checked; `#`-leading names resolved by an escaping rule or refused; a capture verifies only against its run receipt. Axis: coverage.
- Operator rulings routed (l0-questions.md): credential-shaped names (refuse vs redact); the derivation of `ignored` (check-ignore vs listing).
- Standing: the landing-suite receipt (census/round-46/c1-counter.py) at the r53 tip; the census before→after in the v1 receipt form.

### Round 53 corrections (append-only; found after the wave)

Two r52 annotations state a SOURCES row count of "274 -> 275"; the census command
`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` recomputes 198 at
f778b9d1 and 199 at 9bf9234a (200 with S276, landed r53). The 274/275 figures are the
last row's S-ids (S274/S275) misread as a row count. Each site is filed by one line (the
pair form: the annotation stated a before→after pair; both of its numbers are S-ids):

R53-CORRECTION LOG.md:2527 stale=274->275 recomputed=198->199

R53-CORRECTION corpus/README.md:870 stale=274->275 recomputed=198->199

### Round 53 measurements (2026-11-03; base 9bf9234ae4d11c7b31706354302a9e95ad0d1f81; freeze 61838b54112354acae5ae0534425f366c14e658c; prereg census/round-53/preregistration.txt)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 the annotation-agreement counter is amended to v2 (five named r52 limits become five checks, shown able to fail) | calibration 7 | v1 arm exit 0 on ALL SIX fixtures including the five attack states (`census/round-53/records/c1-matrix-v1.tsv`); do-nothing control `PRISTINE FAIL C1V2-COUNTER-ABSENT` exit 1 (census/round-53/controls/c1-control-donothing.txt) | v2 arm exit 1 with the named finding on F2–F6 (MULTIPLE-ANNOTATIONS / INERT-CORRECTION / CORRECTION-IN-FENCE / DELETED-LINES / RECORD-SHA-MISMATCH) and exit 0 on F1 (`c1-matrix-v2.tsv`); real lane exit 0 `unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0` (`c1-tip.txt`); independent reproduction AGREE 12/12 (seat S53executor01) | `python3 -B census/round-53/c1-counter.py --root LANE --rev FULL40 --base 9bf9234ae4d11c7b31706354302a9e95ad0d1f81 --record-sha256 2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30 --scratch DIR`; fixtures `python3 -B census/round-53/fixtures/build-fixtures.py --work DIR` | instruments frozen at 61838b54112354acae5ae0534425f366c14e658c; tip receipts at a1156d8579847dccc9185cc677c4e23e277e7123 |
| C2 the capture counter is amended to v2 (sort order, `#`-leading names, RECEIPT_VERSION=1 receipt binding, shown able to fail) | coverage 8 | v1 arm exit 0 on ALL FOUR fixtures including the three attack captures (`census/round-53/records/c2-matrix-v1.tsv`); do-nothing control `PRISTINE FAIL FLEET-CENSUS-ABSENT` exit 1 (census/round-53/controls/c2-control-donothing.txt) | v2 arm exit 1 with the named finding on FA1–FA3 (ROWS-UNSORTED / COMMENT-AMBIGUOUS-NAME / CAPTURE-RECEIPT-MISMATCH) and exit 0 on FH (`c2-matrix-v2.tsv`); committed round-53 capture exit 0 `receipt=ok sorted=ok` (`c2-tip.txt`); independent reproduction PASS (seat S53executor02) | `python3 -B census/round-53/c2-counter.py --root LANE --rev FULL40 --capture census/round-53/records/fleet-root-census.tsv --receipt census/round-53/records/fleet-root-census-run.txt --scratch DIR` | capture at 1a53bcabc91d97b1a930abeb0d9d23ffbae19b81; tip receipts at a1156d8579847dccc9185cc677c4e23e277e7123 |

No owned score changed (calibration 7, coverage 8, operability 8): both claims are
instrument amendments — the kill-power over committed attack fixtures is the measured
move; the honest states (the r52 filing, the r53 capture) were already green and stay
green (no-harm). The routed defects R1–R13 (fence grammar, zone edge, recomputed
validation, `#`-shape width, receipt extras, tool pin, fixture coverage, builder
hardening, oracle pinning, rev determinism, path binding, exit-code ambiguity, wording
drifts) are named limits of the frozen bytes, consolidated in corpus/lessons/round-53.md
and routed to r54.

### Planned (r54, appended)

- C1 candidate (calibration): counter v3 — tilde/HTML fence grammar; zone-edge grammar
  (refuse a token that straddles the zone edge instead of truncating it); validate a
  correction's `recomputed=` against the record count; enumerate LOG/README count
  annotations (the 274→275 class) as sites.
- C2 candidate (coverage): counter v3 — widen the `#`-shape refusal (space-in-name rows);
  refuse unknown receipt keys; name the CRLF finding; add `--tool-sha256`; add fixtures
  for the receipt-ENTRIES and symlink branches (M-F1/M-F2); pin GIT_*_DATE in the
  builder; digest-pin the selftest oracle/builder in the prereg.
- Operator rulings still open (routed around, never assumed answered): credential-shaped
  names refuse-vs-redact (r52); `ignored`-column derivation (r52); r46 mass id drift
  (assimilation held); r48 census conf-form.
- Standing: the landing-suite receipt (census/round-46/c1-counter.py) at the r54 tip;
  the census before→after in the v1 receipt form.

### Round 54 measurements (2026-11-03; base fe12daad2549f534650d406ebdbac9113d59313f; freeze 3c394cab0cd406bbab72b8d365e0f3deed4ef98a; prereg census/round-54/preregistration.txt; real-lane measured commit bfdbb336329e6afba3ab1ca83cbd6d9759271062)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 the annotation-agreement counter v3 instruments the r53 routed filing surfaces (tilde/parity/HTML-comment hidden lines, zone-edge straddle, bogus-recomputed, LOG/README SOURCES-pair scan) | calibration 7 | v2 arm kills 5 of 13 matrix rows (F2–F6); F7–F12 exit 0 (`census/round-54/records/c1-matrix-v2.tsv`) | v3 kills 11 of 13 rows, each with its named finding (F7–F9 CORRECTION-IN-FENCE, F10 ZONE-TOKEN-STRADDLES-EDGE, F11 BOGUS-RECOMPUTED, F12 UNFILED-SOURCES-ANNOTATION); F1 and F12b green; real lane exit 0 `unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0` (`census/round-54/records/c1-matrix-v3.tsv`, `c1-tip.txt`) | `awk -F'\t' 'NR>1 && $5==1{n++} END{print n+0}' census/round-54/records/c1-matrix-v2.tsv` → 5; the same on c1-matrix-v3.tsv → 11; `python3 -B census/round-54/c1-counter.py --root . --rev bfdbb336329e6afba3ab1ca83cbd6d9759271062 --base fe12daad2549f534650d406ebdbac9113d59313f --record-sha256 2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30 --sources-rev-before f778b9d131574d3ff09c0cc8a077643c0fc84bb4 --sources-rev-after 9bf9234ae4d11c7b31706354302a9e95ad0d1f81` → exit 0 | real lane bfdbb336; fixture matrix from the deterministic builder (revs pinned) |
| C2 the capture counter v3 instruments the widened `#`-row shape, unknown receipt keys, CAPTURE-CRLF, the `--tool-sha256` pin, and the FA7/FA8/FH2 branch fixtures | coverage 8 | v2 arm kills 6 of 10 (FA1, FA2, FA3, FA6, FA7, FA8); FA4 and FA5 exit 0; FA6's first finding is a spurious CAPTURE-RECEIPT-MISMATCH (`census/round-54/records/c2-matrix-v2.tsv`); the pin argument does not exist | v3 kills 8 of 10 (FA4 COMMENT-AMBIGUOUS-NAME, FA5 RECEIPT-UNKNOWN-KEY, FA6 CAPTURE-CRLF first); FH and FH2 green; real lane exit 0 `receipt=ok sorted=ok tool_pin=ok` over the fresh capture; wrong pin → TOOL-SHA-ARG-MISMATCH rc 1 (`census/round-54/records/c2-matrix-v3.tsv`, `c2-tip.txt`) | `awk -F'\t' 'NR>1 && $5==1{n++} END{print n+0}' census/round-54/records/c2-matrix-v2.tsv` → 6; the same on c2-matrix-v3.tsv → 8; `python3 -B census/round-54/c2-counter.py --root . --rev bfdbb336329e6afba3ab1ca83cbd6d9759271062 --capture census/round-54/records/fleet-root-census.tsv --receipt census/round-54/records/fleet-root-census-run.txt --tool-sha256 e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b` → exit 0 | real lane bfdbb336; base fe12daad has no capture (control rc 128) |

C1 and C2 both verify by their frozen predicates over the committed bytes (the critic seat's
falsification: both SURVIVE; the v2 arm is not vacuous on the new fixtures; the real lanes are
green at the measured commits). Named limits and routed defects are in corpus/lessons/round-54.md
`## Wave findings` and `## Named limits carried into r55`: reviewer01 R1–R6 (hidden-correction
swallow, dual-anchor aliasing, pair-filing stale drop, rows-word dodge, fence over-hide, pair-scan
fence false positive); reviewer02 NL-1–NL-5; critic N1, N5, N6; mutation01 M2, M7, M11. No owned
score changed (calibration 7, coverage 8, operability 8): both claims are instrument amendments,
and the kill-power over committed attack fixtures is the measured move. No capability row enters
the table: both claims amend existing instruments and no new repertoire is demonstrated.

### Round 54 corrections (append-only; see corpus/lessons/round-54.md ERRATUM-R54-1 to -3)

R54-CORRECTION census/round-54/preregistration.txt C2 kill rule: the wrong-pin refusal is shown on the real lane, not in the selftest (no `--tool-sha256` selftest arm; routed FA9).

R54-CORRECTION census/round-54/preregistration.txt C1 F11 mechanism clause: v2 prints `mismatches=1 filed=1 unfiled=0`, not `mismatches=0/unfiled=0`.

R54-CORRECTION census/round-54/controls/c1-control-donothing.txt "filed=no is not printed": the v2 arm on F11 prints `filed=no` on the SCORECARD SITE line.

### Planned (r55, appended)

- FIRST (HIGH, L0-pending on C1's admission): counter v4 with one line model for the hidden set and the correction numbering (sentinel01 S1; L1 reproduction `census/round-54/records/s1-formfeed-reproduction.txt`); red-before fixture F7-FF (two form-feed lines above a `~~~` fence) committed and shown exit 0 under v3 before the fix; then the fix shown exit 1. Also MEDIUM: ASCII-only pair scan (S2), uppercase-only receipt key (S3, as NL-3), path-unscoped pointer exemption (PTR, connector01).
- C1 candidate (calibration): counter v4 — prefix-tolerant correction lexing audited against hidden lines (R1); every anchor occurrence on a site line judged (R2); pair-form filings with a stale pair differing from the annotation refused (R3); the unit word `rows` optional in the pair scan (R4); fence start conditions per CommonMark 0.31.2 (R5); PAIR_SITES hide-fenced lines (R6); fixtures reproducing each as a red-before, shown able to fail, plus F8b-BT4-SHORT-RUN (M2), F12c-LOG-POINTER-EXEMPT (M7) and the SOURCES-RECOMPUTE-MISMATCH arm (N5). Prereg amendments quote summary lines verbatim (ERRATUM-R54-2 class).
- C2 candidate (coverage): counter v4 — `#`-leading rows with four tabs refused (NL-1); unknown-key detection case- and whitespace-insensitive (NL-3, NL-4); pin-shape errors refused by name (NL-5); FA9-WRONG-TOOL-PIN selftest arm so the pin branch is covered by the selftest (M11), with the prereg's citation corrected to the arm that runs.
- Operator rulings still open (routed around, never assumed): credential-shaped names refuse-vs-redact (r52); `ignored`-column derivation (r52); r46 mass id drift (assimilation held); r48 census conf-form (recorded, this host rc 0).
- Standing: the landing-suite receipt (census/round-46/c1-counter.py) at the r55 tip; the census before→after in the v1 receipt form; the r52/r53 counters unchanged at the r55 tip.
- Integrator (not this lane): the r53 verifier §6.2 wave-results pointer (fleet-side wave artifacts not durable).

### Round 55 measurements (2026-11-03; base f056aaa031bb65de27e7fa5daa38b0d4a443aedc; freeze e8f338674dea386c186aa7657ef2142cbb4b6d48; preregistration census/round-55/preregistration.txt; real-lane measured revision 4b10ddd1741a948c89d283358affd1da2ab3fd95)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 the annotation-agreement counter v4 instruments the r54 routed filing surfaces (S1 one LF line model, R1 prefix lexing, R2 anchor occurrences, R3 pair-filing INERT, R4/S2 pair grammar, R5 CommonMark fence starts, R6 pair-scan hide-fence, PTR narrowing, M2/M7/N5 fixtures) | calibration 7 | v3 exit 0 on 8 of 8 acceptance attacks (`census/round-55/records/c1-matrix-v3.tsv`: F7-FF, F13, F14, F15, F16, F20, F21, F22 — the claimed work is not vacuous); v3 exit 1 on the 3 honest over-hide states F17, F18, F19; 27-row exit-0 count 11 | v4 exit 1 on 8 of 8 acceptance attacks with the named findings; v4 exit 0 on F17, F18, F19; carry-over 13 rows identical; 27-row exit-0 count 6; real lane exit 0 `unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0` | `awk -F'\t' 'NR>1 && $5==0{n++} END{print n+0}' census/round-55/records/c1-matrix-v3.tsv census/round-55/records/c1-matrix-v4.tsv`; `bash census/round-55/fixtures/run-matrix.sh SCRATCH OUTDIR`; `python3 -B census/round-55/c1-counter.py --root LANE --rev 4b10ddd1741a948c89d283358affd1da2ab3fd95 --base f056aaa031bb65de27e7fa5daa38b0d4a443aedc --record-sha256 2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30 --sources-rev-before f778b9d131574d3ff09c0cc8a077643c0fc84bb4 --sources-rev-after 9bf9234ae4d11c7b31706354302a9e95ad0d1f81 --scratch DIR` | measured at 4b10ddd1741a948c89d283358affd1da2ab3fd95; receipts `census/round-55/records/c1-tip.txt`, `census/round-55/records/c1-matrix-v3.tsv`, `census/round-55/records/c1-matrix-v4.tsv` |
| C2 the capture counter v4 instruments the NL-1/NL-3/NL-4/NL-5 surfaces and the FA9/FB4 selftest pin arms | coverage 8 | v3 exit 0 on FB1-TAB4-ROW, FB2-LOWER-KEY, FB3-NOSPACE-KEY (the claimed work is not vacuous); 13-row exit-0 count 5 (FH, FH2, FB1, FB2, FB3) | v4 exit 1 on FB1, FB2, FB3 with COMMENT-AMBIGUOUS-NAME and RECEIPT-UNKNOWN-KEY; FA8 finding named CLASS-MISMATCH (was the unnamed token `class`); FH, FH2 and FA1–FA7 identical exits; 13-row exit-0 count 2; selftest `cases=15` (FA9 rc 1, FB4 rc 2); real lane exit 0 `receipt=ok sorted=ok tool_pin=ok`; wrong pin rc 1 `TOOL-SHA-ARG-MISMATCH` | `awk -F'\t' 'NR>1 && $5==0{n++} END{print n+0}' census/round-55/records/c2-matrix-v3.tsv census/round-55/records/c2-matrix-v4.tsv`; `python3 -B census/round-55/c2-counter.py --root LANE --rev 4b10ddd1741a948c89d283358affd1da2ab3fd95 --capture census/round-55/records/fleet-root-census.tsv --receipt census/round-55/records/fleet-root-census-run.txt --tool-sha256 e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b --scratch DIR` | measured at 4b10ddd1741a948c89d283358affd1da2ab3fd95; receipts `census/round-55/records/c2-tip.txt`, `c2-matrix-v{3,4}.tsv` |

Numeric axis scores unchanged (calibration 7, coverage 8, operability 8): both claims are instrument
amendments; the kill-power over committed attack fixtures is the measured move, and the honest states
(the r54 filing, the r55 capture, the carry-over rows) stay green. No capability row enters the table: no
new repertoire is demonstrated. Verdicts are the non-author closure's to give; the lane claims none.

Routed-defect scope: the frozen v4 bytes carry one named limit that the round found by construction
(ERRATUM-R55-1 for the F7-FF byte label; the repository-local `core.quotePath=false` numstat limit,
receipt `census/round-55/records/probe-numstat-quotepath.txt`). Both are in the lesson's named limits.

### Planned (r56, appended)

- Counter v5 (calibration): numstat parsed on `\n` only (the repository-local quotePath limit), red-before
  fixture carrying a path with U+0085 under `core.quotePath=false`, shown exit 1 under v4 and green under v5.
- Fixture for the exact form-feed S1 shape: a new frozen fixture version with its own prereg (ERRATUM-R55-1);
  F7-FF stays as frozen (vertical tab).
- Operator ruling still open: the r54 C1-admission L0 is answered by the closure's admission; the lane keeps
  the named limits on the record and does not reopen the admission.
- Standing (no-harm): the landing-suite receipt (`census/round-46/c1-counter.py`) at the r56 tip; the census
  before→after in the v1 receipt form; the r53/r54 counters at the r56 tip.
- Operator rulings still open (routed around, never assumed answered): credential-shaped names refuse-vs-
  redact (r52); the `ignored`-column derivation (r52); r46 mass id drift (assimilation held).

### Round 55 no-harm findings (appended after the wave; the frozen predicates are unchanged)

| claim | finding | evidence | verdict consequence |
|---|---|---|---|
| C2 coverage 8 | RD-A: a shape the frozen v3 counter refuses as an unknown receipt key (leading digit or underscore: `1KEY=x`, `_KEY=x`, `2=x`) now exits 0 under v4, because the v4 key pattern requires a letter first. The cause is a regex narrowing without a differential against v3's shapes. The frozen kill list does not name these shapes. | `census/round-55/wave/w1/S55reviewer02/receipt-key-differential.txt`; `census/round-55/wave/w1/S55reviewer02/receipts/A28.txt`; lesson `## Mistakes` row 1 | the predicate holds; the no-harm rule is not met on this shape; the admission is the operator's ruling (L0 line filed); r56 first-character class `[A-Za-z0-9_]` |
| C1 calibration 7 | no frozen-verdict harm found: the carry-over rows keep exit and finding; N11 changes the F10 SUMMARY counts only. N1 (a pair filing inside a fence or a comment counts as filed, carried from v3) is a named limit, not a regression. | `census/round-55/wave/w1/S55critic01/S55critic01-report.md` §2–§4; `census/round-55/wave/w1/S55reviewer01/S55reviewer01-report.md` D14/D15 | verifies on its literal predicate; N1 is the first r56 item |

Both verdicts stand on the committed bytes; no frozen byte was edited to change them.

### Round 55 corrections (append-only; the no-harm table above is corrected here)

R55-CORRECTION SCORECARD.md "C1 calibration 7" row, no-harm column: the statement "no frozen-verdict harm found" is superseded. Sentinel01 S55-S2 (MEDIUM, confirmed by the L1: `census/round-55/records/probe-s2-pair-indent-comment.txt`, v3 exit 1 UNFILED-SOURCES-ANNOTATION, v4 exit 0) is a v3→v4 regression: a four-space-indented `<!--` line hides a real overstatement from the pair scan, introduced by the R6 change. C1 verifies on its frozen predicate; the no-harm rule is not met on this shape.

R55-CORRECTION C2 row: the RD-A regression stands as recorded above; the operator's ruling on both harms (C1 S55-S2, C2 RD-A) is the admission decision. Neither claim is admitted by the lane.

### Round 55 wave dispositions (appended after WAVE-DONE; all 12 seats returned output; none dead)

- Routed to r56 (counter v5 candidates, each red-before with a v3 differential): RD-A key first-character class;
  S55-S2 comment-branch indent rule; N1/D14/D15 pair filings in fences and comments; S55-S1 binary-numstat refusal;
  A09–A13 closer exotic whitespace; E09/E10 list-item fences; C04/C07 first-anchor INERT; N4 ratio exemption;
  S55-S3 unlexed corrections as a named limit; S55-S5 empty-value receipt keys; P1 hyphenated receipt keys;
  selftest harness assertion of every expected row (mutation01 C2-17/18); ERRATUM-R55-1 form-feed fixture.
- Sibling routing (not edited here): kaidoku-shokunin's tools/round-59/annotation-audit.py and
  chousa-shokunin's tools/corpus/evidence/round50/stale-count-check.py use splitlines on the S1 defect class (connector01).

### Round 56 measurements (2026-11-03; base fafe371694fea41c5d23f63083865d5ccf3f1d36; freeze cce21b555a617cadda782613ec1e9d3a0c12ac83; preregistration census/round-56/preregistration.txt; real-lane measured revision cce21b555a617cadda782613ec1e9d3a0c12ac83)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 correction-filing counter v5 | calibration 7 | 33-fixture v4 matrix: exit-0 count 9; F24/F26/F28 silent passes; F29 honest filing refused | v5 exit-0 count 7; F24/F26/F28 refused; F29 accepted; F27 named binary refusal; F7-FF2 retained. Selftest 33/33; real lane EXIT=0, unfiled=0 and pairhidden=0. Finite predicate holds but B4/C4 harm calibration; not admitted | `awk -F'\t' 'NR>1 && $5==0{n++} END{print n+0}' census/round-56/records/c1-matrix-v{4,5}.tsv`; full real-lane argv in census/round-56/preregistration.txt | cce21b555a617cadda782613ec1e9d3a0c12ac83; `census/round-56/records/c1-tip.txt`, `census/round-56/records/c1-selftest.txt`, `census/round-56/records/probe-real-scorecard-hidden-tail.txt` |
| C2 capture counter v5 | coverage 8 | 16 repository fixtures: exit-0 count 5; FC1/FC2/FC3 silent passes | exit-0 count 2; FC1/FC2/FC3 refused RECEIPT-UNKNOWN-KEY; 13 carry-over rows unchanged. Selftest 18/18 including two pin arms; real lane EXIT=0 receipt=ok sorted=ok tool_pin=ok | `awk -F'\t' 'NR>1 && $5==0{n++} END{print n+0}' census/round-56/records/c2-matrix-v{4,5}.tsv`; full real-lane argv in census/round-56/preregistration.txt | cce21b555a617cadda782613ec1e9d3a0c12ac83; `census/round-56/records/c2-tip.txt`, `census/round-56/records/c2-selftest.txt` |

Both post-freeze matrices are byte-identical to the pre-freeze dry-run matrices
(`census/round-56/records/matrix-dryrun/`). The official receipts' EXIT lines are recorded at the bottom of each file.
Owned score values unchanged (calibration 7, coverage 8, operability 8): the lane still has no reproducible 0-10 mapping. No capability row enters the table (instrument amendments, no new repertoire). No round admission is claimed; the non-author closure rules.

### Round 56 wave-attack disposition (appended after WAVE-DONE; detail in corpus/lessons/round-56.md ## Wave findings)

WAVE-DONE received from Main: 12/12 seats settled, all returned results, no dead seat reported.
C1's finite predicate holds, but calibration is **harmed**: reviewer01 B4 (NBSP prefix)
and C4 (closed multiline inline comment) hide real filings in CommonMark while v5
passes them and v4 refuses. C1 is not admitted; whole-round verdict is rejected-harmed.
C2's finite predicate holds; reviewer02's 75-shape differential found zero narrowing
harms, eight repair-direction cases and three relabels. Coverage improved on this
finite receipt surface; score 8 unchanged. Operability unchanged.
Evidence: `census/round-56/wave/w1/S56reviewer01/S56reviewer01-report.md`,
`census/round-56/wave/w1/S56reviewer02/S56reviewer02-report.md`,
and `census/round-56/wave/w1-results.json`.

### Planned (r57)

- Calibration first: distinguish raw inline comments from HTML-block starts. Pin B4/C4
  and benign F29 before data; a block-only parser is not a visibility parser.
- Retain every r55/r56 accepted/refused shape as a differential, including the
  five mechanical narrowing rows. Do not relax the frozen r56 predicate.
- Selftest coverage: assert all finding ids or summary fields, not only the first
  finding (M1); mutation-test the row-set assertion itself (N3).
- Operability/security: linear line-number calculation, escaped diagnostic strings,
  symlink-safe scratch roots; finite reproductions in the sentinel report.
- Carry the revenger's 41-row disposition table; unresolved items remain explicit.

### Round 57 measurements (2026-11-03; base b4ef0bc84ada3fb3aefd6a0b1a841a6517b84acd; freeze d749f7ee081ec1b382b2f92577eb22bfba1c7761; preregistration census/round-57/preregistration.txt)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 correction-filing counter v6 (inline HTML-comment class + all-findings selftest) | calibration 7 | v5 arm over the 36-fixture set: exit-0 count 10; B4-INLINE-NBSP-OPENER and C4-INLINE-CLOSED-COMMENT exit 0 (the r56 harm: hidden filings counted as filed) | v6 arm: exit-0 count 8; B4 and C4 exit 1 with `CORRECTION-IN-FENCE,CORRECTION-IN-FENCE` and `hidden_by=inline` in both details; C6-INLINE-SAME-LINE, F29, F17, F18, F19 exit 0 under both arms; all 33 carry-over rows identical in exit and full finding list; selftest `pass cases=36`; real lane exit 0 `unfiled=0 … fenced=0` | `awk -F'\t' 'NR>1 && $5==0{n++} END{print n+0}' census/round-57/records/c1-matrix-v5.tsv census/round-57/records/c1-matrix-v6.tsv` (10, 8); full argv in the prereg C1 section | `census/round-57/records/c1-matrix-v5.tsv`, `census/round-57/records/c1-matrix-v6.tsv`, `census/round-57/records/c1-selftest.txt`, `census/round-57/records/c1-tip.txt` (rev `d749f7ee`) |
| C2 receipt revision binding (gate + recorder) | operability 8 | over `census/round-57/manifests/before.tsv` the gate exits 1 with `findings=1 RECEIPT-REV-MISSING` (the r56 standing receipt names no revision) | over `census/round-57/manifests/after.tsv` the gate exits 0 with `SUMMARY receipts=3 findings=0`; each receipt carries `rev=<full40>`, `instrument_sha256=` matching the committed blob and an `EXIT=` line; selftest `pass cases=8`, `control=FALSE-GREEN-REJECTED` | `python3 -B census/round-57/c2-counter.py --root . --manifest census/round-57/manifests/before.tsv` (and `census/round-57/manifests/after.tsv` after the receipts land); `TMPDIR=DIR python3 -B census/round-57/c2-counter.py --selftest --work DIR` | `census/round-57/records/c2-before.txt`, `census/round-57/records/c2-selftest.txt`, `census/round-57/manifests/after.tsv` |

No owned score value changed (calibration 7, coverage 8, operability 8): the lane still has no
reproducible 0–10 mapping and the closure rules. C1 is an instrument amendment; C2 is a capability
acquisition whose row is in the capabilities table only if the closure confirms its demonstration.
Named limits are in `corpus/lessons/round-57.md`; no round admission is claimed.

### Capabilities (round 57 candidate row)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| receipt revision binding | refuse a measurement receipt that does not name the durable full-40 revision it was measured at, with an instrument digest bound to that revision's committed bytes; produce such receipts | `python3 -B census/round-57/c2-counter.py --root . --manifest census/round-57/manifests/after.tsv` → `findings=0`; selftest 8/8 `control=FALSE-GREEN-REJECTED`; receipts `census/round-57/records/c1-tip.txt`, `census/round-57/records/c2-before.txt`, `census/round-57/records/c2-selftest.txt` | r57 (closure-gated) |

### Planned (r58, appended)

- Calibration: close the r57 named limits that a fixture can reach — WHATWG-invalid comment text with
  a later closer (renderer vs authoring grammar), `<!-->`/`<!--->` adjacency, and a partially covered
  line; keep both directions pinned in one frozen set (Q115). Carry the N3 capture-counter row-set
  meta-test the r56 closure routed.
- Operability: apply the r57 receipt gate to the remaining standing receipts (r53/r54 name no
  revision); decide with the operator whether `census/round-57/record-receipt.sh` is the only writer of
  the round receipts (L0), and close the r56 sentinel MEDIUM/LOW items (correction-line
  quadratic lookup, control-byte escaping in diagnostics, symlink scratch roots).
- Coverage: an entry for the HTML block types the counter does not model (CDATA, processing
  instructions, declarations) only if a round's claim needs them; otherwise leave the frontier note.
- Operator rulings still open (routed around, never assumed): credential-shaped names refuse-vs-redact
  (r52); the `ignored`-column derivation (r52); r46 mass id drift (assimilation held); r48 census
  conf-form; whether the recorder should replace ad-hoc receipt writing.

### Round 58 calibration corrections (append-only)

R58-CALIBRATION carry_identical=34 supersedes the r57 SCORECARD claim "all 33 carry-over rows".
R58-CALIBRATION exit_zero=10,8 counted separately per matrix; the r57 two-file awk command emits the combined total 18, not the pair.

Authority: `census/round-57/records/c1-matrix-v5.tsv` and `census/round-57/records/c1-matrix-v6.tsv`; instrument `census/round-58/c1-counter.py`. These corrections repair two assessment statements, not the rejected visibility counter. Numeric scores remain calibration 7 / coverage 8 / operability 8.

### Round 58 measurements — C1

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 two r57 assessment statements | calibration 7, delta 0 (legacy scale unmapped) | assertions=2 mismatches=2, unchanged base control fails | assertions=2 mismatches=0 carry_identical=34 exit_zero=10,8; bounded record accuracy, not visibility-parser repair | `python3 -B census/round-58/c1-counter.py --root LANE --rev FULL40` | before input 83d3813257648e99fb4ab2ddef217124f39cf324; after dccdc469f4c2e0415e1a1dcc317364e1b4d3191e; receipts `census/round-58/c1-control-binding.txt`, `census/round-58/c1-after.txt` |

### Round 58 measurements — C2 and final remeasurement

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C2 bounded receipt interface | operability 8, delta 0 (legacy scale unmapped) | unchanged r57 scores 3/8: five incorrect clean results, three honest passes | 8/8: five named refusals, three honest passes; always-clean and always-refuse controls rejected; gate selftest 17/17 | `python3 -B census/round-58/c2-acceptance.py --tool census/round-58/c2-gate.py --root LANE --work DIR --selftest` | 5e4b8f14572d7051537b167dece4541bed7d2bab; `census/round-58/c2-after.json`, `census/round-58/c2-selftest.txt`; before `census/round-58/before-arm.json` at oracle freeze 1880343ed04337379c5478f91408c30c8fbd4b77 |
| C1 final code-revision replay | calibration 7, delta 0 | mismatches=2 unchanged base | assertions=2 mismatches=0 carry_identical=34 exit_zero=10,8, EXIT=0 | `python3 -B census/round-58/c1-counter.py --root LANE --rev 5e4b8f14572d7051537b167dece4541bed7d2bab` | 5e4b8f14572d7051537b167dece4541bed7d2bab; `census/round-58/c1-final.txt` |

The finite predicates verify; independent non-author closure still decides admission. No new capability acquisition or frontier promotion; existing receipt capability repaired on the eight-case surface. Prior rejected claims remain rejected, historical counters untouched, certification OFF.

### Planned (r59)

- Address the still-open visibility-parser harms only with independently rendered controls in both directions; never interpret this round's two assessment notes as that repair.
- Preserve Q117 raw identity/path/header boundaries. Scope any atomic-read/resource-bound or recorder dirty-tree/overwrite repair as a separate falsifiable claim; do not infer it from eight static cases.
- Keep historical receipt-binding debt, capture row-set meta-test, control-byte diagnostics, and operator holds explicit.

### Round 59 bounded calibration measurement

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 R58-KIND assessment registry classification | calibration7, numeric delta0 (legacy scale unmapped) | assertions=1 mismatches=1 REGISTRY-KIND-MISMATCH EXIT1 | assertions=1 mismatches=0 EXIT0; direct stable r58 row kind=gate, rows=1, shadow r59 rows=0; actual public assessment selftest5/5 and independent production acceptance4/4 | `python3 -B census/round-59/c1-counter.py --root LANE --rev FULL40`; separate production commands in census/round-59/assessment-production.txt, assessment-selftest.txt and acceptance-final.txt | before da5af55b5ea0a2a38edea05635a13416c698e6e7; after18c82b5302a398065e55539e73648c1fc329c4d4; before.txt, after.txt, direct-registry.txt |

Finite classification target holds, but the whole admission predicate remains **unprovable / honest-stop**: frozen classification controls do not reject kind-only/no-substance states, fenced decoys or nonexistent instruments. The separate actual gate/selftest is now working, but cannot retroactively supply a prefreeze relevant substance-forgery control. Q99 freeze checker also remains red FIELD-MISSING Round (census/round-59/freeze-check.txt). No frozen byte/predicate changed and no earlier rejected admission is repaired. Counter limitations are explicit in SKILL.md and corpus/lessons/round-59.md.

Classification is corrected on the SAME frozen R58-KIND row; no population-shadow substitution was landed. Public successor preserves exact r58 note derivations (production assertions=2 mismatches=0 carry_identical=34 exit_zero=10,8), with stable refusal id and actual isolated self-invocation. No new capability or frontier promotion. Coverage8 and operability8 unchanged.

### Planned (r60, only if operator authorizes progression)

- Do not re-declare this bounded classification repair or infer broader correctness. Before any new freeze, exercise and commit actual public-path substance-forgery controls, not merely kind/summary labels; include readable Round header and replayable fixed-date fixture identities.
- Carry all parser visibility, recorder dirty-tree/overwrite, receipt atomicity/resource bounds, diagnostics, historical receipt binding and capture row-set meta-test debts OPEN. Existing safety and operator holds remain.

### Round 60 measurements (2026-11-04, Linux; base `1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4`; controls committed `3b5525099356e15ff9d17b7fbd2835c2d3512eee`; freeze `2670e96af1b81c7aa793acc34d40361b4beecff8`; prereg `census/round-60/preregistration.txt`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 freeze-record substance arm (capability acquisition) | calibration 7 | `new_forgeries=5 new_honest=3`, `EXIT=1` on the same counter with `--new-arm plain` (base tool bytes; accepts all five forgery controls) | `new_forgeries=0 new_honest=3 stubs=REJECTED`, `EXIT=0`; the arm is byte-identical without `--substance` (three-revision diff, selftest 41/41 unchanged) and the round's own freeze record scores `SUMMARY claims=2 findings=0` under it | `python3 -B census/round-60/c1-counter.py --root . --matrix census/round-60/c1-matrix.tsv --base-tool-rev 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4 --rev <full40> --work DIR --new-tool tools/souji-freeze-check.py` | `census/round-60/records/c1-after.txt` at `2670e96af1b81c7aa793acc34d40361b4beecff8`; before `census/round-60/controls/c1-do-nothing.txt` at `3b5525099356e15ff9d17b7fbd2835c2d3512eee` |
| C2 atomic receipt writer (operability) | operability 8 | base recorder `census/round-57/record-receipt.sh`: `pass=4 fail=4` (`atomic-in-flight`, `kill-residue`, `rev-short`, `instrument-absent`), `EXIT=1` | `pass=8 fail=0 control=ALWAYS-WRITE-REJECTED,ALWAYS-REFUSE-REJECTED`, `EXIT=0`; writer selftest 12/12 | `python3 -B tests/fixtures/r60-receipt-write.py --tool tools/souji-receipt-write.py --work DIR` | `census/round-60/records/c2-after.txt` at `2670e96af1b81c7aa793acc34d40361b4beecff8`; before `census/round-60/controls/c2-do-nothing.txt` at `3b5525099356e15ff9d17b7fbd2835c2d3512eee` |

Both frozen predicates hold on the frozen bytes. Numeric axis scores are unchanged (calibration 7,
operability 8, coverage 8): the lane still has no reproducible 0–10 mapping, and the closure rules
admission. C2 is a successor to the rejected r57 C2 *on a different surface*: r57 bound a receipt's
revision text and checked receipts; this claim writes them (atomic publish, overwrite refusal, capture
bound, worktree and commit-object refusal), and its base recorder passes 4/8, not the 3/8 the wave
prompt assumed (critic finding 1; the frozen prereg uses the measured 4).

Pre-freeze amendments, each made before any after-data and recorded here: (1) the counter summary now
prints both arms (`new_forgeries`/`new_honest`) so the claim's after-state is readable on the same line
as the control; (2) the substance arm refuses conflicting duplicate `instrument=`/`instrument_sha256=`/
`rev=`/`command=` lines and matches the counter as an argv token rather than a substring (reviewer
S60ReviewerFreeze g2/g3/g4/f); (3) the writer publishes with `link(2)` instead of `os.replace` after an
existence check (TOCTOU clobber), refuses an `--out` directory resolving outside `--root` unless
`--allow-outside`, requires `rev` to name a commit object (a tag OID is refused), and sweeps its own
stale `<out>.*.tmp` siblings (reviewer S60ReviewerRecorder a1/a2, b1, i1, c-c1).

### Capabilities (round 60 row)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| freeze-record substance binding | refuse a freeze record whose control receipt is not bound to the declared counter's committed bytes, a strict-ancestor full-40 revision and a command naming that counter, while leaving the default checker output byte-identical | `python3 -B tools/souji-freeze-check.py --root . --prereg census/round-60/preregistration.txt --rev 2670e96af1b81c7aa793acc34d40361b4beecff8 --substance` → `SUMMARY claims=2 findings=0`; `--selftest --substance` 12/12; `census/round-60/records/c1-after.txt` | r60 |
| atomic receipt writing | publish a receipt through a same-directory temp file, `fsync` and `link(2)`, refusing an existing output, a racing creator, a dirty worktree, an over-bound capture, a short or non-commit revision, an absent instrument and an out-of-root target | `python3 -B tests/fixtures/r60-receipt-write.py --tool tools/souji-receipt-write.py` → `pass=8 fail=0`; writer `--selftest` 12/12; `census/round-60/records/c2-after.txt` | r60 |

### Planned (r61)

- C1's matrix does not assert the *finding class* it expects and its `forgery-rev-at-freeze` case names
  the freeze commit through a tag (a receipt inside the freeze commit cannot name that commit); a
  successor round can pin classes and add an orphan-commit non-ancestor arm.
- C2's fixture does not observe the atomic publish directly (it observes in-flight absence and kill
  residue) and cannot kill a mutant that hashes the worktree file instead of the committed blob; the
  writer's own selftest covers the latter.
- Carry every r56–r59 debt open: visibility-parser second-opener/code-span/escape/link/TAB, capture
  row-set meta-test, historical receipt binding, diagnostic escaping, recorder dirty-tree semantics for
  ignored files. Certification OFF, K5 HELD.

### Round 61 measurements (2026-11-05; base `c7228424c3919ecf142bab1aec8181722d86467b`; instruments and do-nothing control `da7ceba3950fc3ac946a611791f56e12174272bd`; freeze `9849e71851e28d5f1e88ef658418d3c136f94692`; predicate `census/round-61/preregistration.txt`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 content-bound control chronology (`--substance`) | calibration 7, numeric delta 0 (no reproducible 0–10 mapping) | do-nothing (base bytes, new slot): `new_forgeries=2 class_mismatches=2 stubs=REJECTED EXIT=1` on the 12-case matrix (`census/round-61/controls/c1-do-nothing.txt`); real r60 freeze record: `findings=0` EXIT=0 | `new_forgeries=0 new_honest=4 class_mismatches=0 stubs=REJECTED EXIT=0` (`census/round-61/records/c1-after.txt`); real r60 freeze record under the candidate: two `CONTROL-ADDED-NOT-BEFORE-FREEZE` EXIT=1 (`real-r60-prereg-candidate.txt`); real r61 freeze record: `findings=0` EXIT=0 | `python3 -B census/round-61/c1-counter.py --root . --matrix census/round-61/c1-matrix.tsv --base-tool-rev c7228424c3919ecf142bab1aec8181722d86467b --rev 9849e71851e28d5f1e88ef658418d3c136f94692 --work DIR --new-tool tools/souji-freeze-check.py` | candidate `da7ceba3950fc3ac946a611791f56e12174272bd` (tool sha256 `5794ab27…1c5`); freeze `9849e718` |

Harm check: the base-vs-candidate sweep over all 37 lane preregistrations (`census/round-61/records/substance-sweep.txt`) finds zero plain-path differences and zero base findings removed; the substance differences are added `CONTROL-ADDED-NOT-BEFORE-FREEZE` findings on eleven records (rounds 41–55 and 60; round 60 flips pass to fail, rounds 41–55 were already red). The axis score is unchanged because the lane has no reproducible 0–10 mapping; the closure rules admission.

Named limits and routed debts are in `corpus/lessons/round-61.md`. C2 (receipt-writer fixture and mutant kill-power) was **not declared**: the critic classed its axis as coverage, and the reviewer's HIGH-1 (skip-worktree concealment accepted by the honest writer) is routed to round 62 with `corpus/knowledge/skip-worktree-concealment.md`.

### Round 60 erratum (append-only, round 61 report)

R61-ERRATUM-R60: the r60 preregistration's prose "Controls were executed and committed at `3b5525099356e15ff9d17b7fbd2835c2d3512eee`" is wrong. Both control receipts are added by the freeze commit `2670e96af1b81c7aa793acc34d40361b4beecff8` (`git log --diff-filter=A --no-renames --full-history --format=%H -- census/round-60/controls/c1-do-nothing.txt` → `2670e96a`); `git cat-file -e 3b552509…:census/round-60/controls/c1-do-nothing.txt` fails (EXIT=128). Evidence: `.ufo/waves/round-61/w1/S61ExecRealRecord/erratum-evidence.txt`. The frozen bytes are unchanged; the r60 SCORECARD measurement row is not rewritten.

### Planned (r62)

- Receipt writer: refuse any worktree file whose bytes differ from the committed blob at `rev`, and refuse skip-worktree or assume-unchanged entries (`git ls-files -v`), per `corpus/knowledge/skip-worktree-concealment.md` (reviewer HIGH-1). Declare only with a red-before control committed strictly before freeze (Q120, Q122).
- Freeze checker: add a `## MACHINE BLOCK` requirement for new preregistrations (critic F13 item 2) once `souji-axis-check.py` is confirmed to run on the lane's preregistrations.
- Q121 sweep: carry the r61 wave's critic/reviewer C/H findings into the r62 lesson before the report lands (the r61 lesson carries F2, F3, F5, F7, F8, F9, F10, F12 by number).
- Carry every r56–r60 debt open: visibility-parser, capture row-set meta-test, historical receipt binding, diagnostic escaping, recorder dirty-tree semantics for ignored files. Certification OFF, K5 HELD.

### Round 62 measurements (2026-11-05, Linux; base `16fa821fdce00e709d6895ccfc7aaffa465af195`; freeze `c5af0e0abad41e4e08558e994959def277b7f19f` (`census/round-62/preregistration-freeze3.txt`); controls `71471699fc31ff30e396305537a6a6afe7eb6711`, `57a8581799b1d29ab12cf068824dab521930ec4c`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 receipt index-flag refusal (operability) | operability 8, numeric delta 0 (no reproducible 0–10 mapping) | do-nothing (base bytes): `new_forgeries=3`, `new_honest=2`, EXIT 1 (rows D, E, F accepted: forged receipts) | `new_forgeries=0 new_honest=2 class_mismatches=0 regress=PASS`, EXIT 0 | `python3 -B census/round-62/c1-counter.py --root . --matrix census/round-62/c1-matrix.tsv --base-rev 16fa821fdce00e709d6895ccfc7aaffa465af195 --rev a0b396cdd4f9c75bc2f0e117399916a2279cddd1 --tool tools/souji-receipt-write.py --work DIR` | `a0b396cdd4f9c75bc2f0e117399916a2279cddd1` (receipt `census/round-62/records/c1-after.txt`) |
| C2 stale index-flag statements (calibration) | calibration 7, numeric delta 0 (no reproducible 0–10 mapping) | `stale_open=4 landed=0` (`SKILL.md`, `corpus/README.md`, `corpus/knowledge/skip-worktree-concealment.md` ×2), EXIT 1 | `stale_open=0 landed=3`, EXIT 0 | `python3 -B census/round-62/c2-counter.py --root . --rev 918bb4238f428c3cb93337619910a56dec2164b2` | `918bb4238f428c3cb93337619910a56dec2164b2` (receipt `census/round-62/records/c2-after.txt`) |

Lane index non-`H` count is recorded in the report. No owned score changed: the lane has no reproducible 0–10 mapping (routed to the operator, `.ufo/l0-questions.md` lines 324–325). Frontier: S292 added (`corpus/SOURCES.md:252`); F1 stays `frontier, entries held`. Named limits: `corpus/lessons/round-62.md`. No round admission is claimed; the non-author spot-check is pending.

### Planned (r63)

- Non-author verification of S292 and of both r62 claims (the closure reviewer), before any promotion.
- In-run TOCTOU for the writer (sentinel probes 27–29): bind the receipt to a second index and worktree read after the command, or refuse changes during the run. Not claimed in r62.
- Concealment rows beyond the seven: unmerged, gitlink, deleted-worktree and sparse-checkout paths, with mutants; the r60 fixture's dirty-block kill-power gap (M4, M6).
- Class check as a structured field, not a stderr substring.
- Operator rulings still open: `## MACHINE BLOCK` for preregistrations; numeric axis mapping.

### Round 63 measurements (2026-11-05; base 728ab685617e412172a8e5cb6260f7098b486aec; NO PREREGISTRATION FROZEN; both claims NOT ADMITTED)

Diagnostic only: the candidate writer was scored before any predicate froze (lesson `corpus/lessons/round-63.md` M2), and
the C1 H4 row and the C2 population were changed after seat-scored runs (M1, M3). Owned scores unchanged (calibration 7,
coverage 8, operability 8). No round admission is claimed.

| claim | axis | before (do-nothing, base bytes) | after (candidate `eba4f7e0`, diagnostic) | counting command | measured commit |
|---|---|---|---|---|---|
| C1 in-run refusal and edge classes, 9-row matrix | operability 8 (not moved) | `new_forgeries=4 class_mismatches=4`, EXIT 1 (`census/round-63/controls/c1-do-nothing.txt`) | `new_forgeries=0 new_honest=3 class_mismatches=0 regress=PASS`, EXIT 0 (`census/round-63/records/c1-after-candidate-eba4f7e0.txt`) | `python3 -B census/round-63/c1-counter.py --root . --matrix census/round-63/c1-matrix.tsv --base-rev 728ab685617e412172a8e5cb6260f7098b486aec --new-tool .ufo/waves/round-63/w1/S63ExecWriter/souji-receipt-write.py --work <dir>` | candidate `eba4f7e0`; controls `d7bd4ff2` |
| C2 edge-class refusals (H1 H2 H3), 5-row matrix | (same claim as C1; not separately scored) | `base_class_mismatches=3`, EXIT 1 (`census/round-63/controls/c2-do-nothing.txt`) | `new_class_mismatches=0`, EXIT 0 (`census/round-63/records/c2-after-candidate-eba4f7e0.txt`) | `python3 -B census/round-63/c2-counter.py --root . --matrix census/round-63/c2-matrix.tsv --base-rev 728ab685617e412172a8e5cb6260f7098b486aec --rev 728ab685617e412172a8e5cb6260f7098b486aec --tool .ufo/waves/round-63/w1/S63ExecWriter/souji-receipt-write.py --work <dir>` | candidate `eba4f7e0`; controls `d7bd4ff2` |
| C3 statement/writer agreement (SKILL-only, 3 rows) | calibration 7 (not moved) | `findings=1` (`s2` overreach), EXIT 1 (`census/round-63/controls/c3-do-nothing.txt`); kind-only forgery `findings=4` EXIT 1 (`census/round-63/controls/c3-kind-only-forgery.txt`) | not measured (no after-wording landed) | `python3 -B census/round-63/c3-counter.py --root . --rev 728ab685617e412172a8e5cb6260f7098b486aec --tsv-rev d7bd4ff2743b4e1cb84217301c95340ebfda7634` | controls `d7bd4ff2` and the forgery control built from `728ab685` |

### Round 63 capability rows

None entered: the candidate writer is not landed and its behaviour is not admitted.

### Planned (appended at round 63)

- **r64 (planned r63):** freeze first (preregistration committed before any candidate commit or score); probe each frozen
  matrix row's fixture against base and candidate before declaration (M1); content-bearing snapshot for `--allow-dirty`
  and its matrix row (F1); `:(top)` pathspec and `GIT_INDEX_FILE` scrub (reviewer H4, H5); correct SKILL.md:830 overreach
  (round-62 spot-check R1, calibration); refresh knowledge-entry `verified-at` (R3). Operator L0 questions open: MACHINE
  BLOCK, numeric axis mapping, edge-class axis tie-break. Certification OFF, K5 HELD.

### Round 64 measurements (2026-11-05, Linux; base `ae2f4ece2c936ecd8c4260632ad7330c84f7882d`; NO PREREGISTRATION FROZEN; both claims NOT ADMITTED)

Honest stop, no freeze. Scores unchanged (calibration 7, coverage 8, operability 8). Diagnostic numbers below were produced by seats on pre-freeze bytes and are not admission evidence (lesson `corpus/lessons/round-64.md` M2). The one reproducible base-side measurement is the C2 do-nothing control, bound to the committed population `04bc2769`.

| claim | axis | before (do-nothing, base bytes) | after (candidate `46a9388b`, diagnostic, pre-freeze) | counting command | measured commit |
|---|---|---|---|---|---|
| C1 in-run snapshot, env refusal, toplevel scope (operability) | operability 8 (not moved; not admitted) | `census/round-64/controls/c1-do-nothing.txt`: `base_forgeries=8 base_honest=3 new_forgeries=8 class_mismatches=8 regress=PASS`, EXIT 1 (N4 base=accept in the counter's fixture; disputed row, M1) | seat-run only: selftest 26/26; `new_forgeries=0 new_honest=3 class_mismatches=0 regress=PASS` (seat `S64ExecWriter`, not a freeze-bound receipt) | `python3 -B census/round-64/c1-counter.py --root . --matrix census/round-64/c1-matrix.tsv --base-rev ae2f4ece2c936ecd8c4260632ad7330c84f7882d --new-tool <candidate> --work <dir> --receipt <file>` | base `ae2f4ece`; candidate not landed |
| C2 SKILL.md statement/writer agreement (calibration) | calibration 7 (not moved; not admitted) | `census/round-64/controls/c2-do-nothing.txt`: `findings=1 verdict=FAIL` (`SCOPE-OVERREACH s2`), EXIT 1, bound to population `04bc2769` | not measured (after-wording not landed) | `python3 -B census/round-64/c2-counter.py --root . --tsv census/round-64/c2-statements.tsv --tsv-rev 04bc2769e14c5c5050a0c8b93a439e13adb8b69b --rev <full40>` | base `ae2f4ece`; population `04bc2769` |

Frontier: S295 (git(1) `GIT_INDEX_FILE`) and S296 (gitglossary(7) PATHSEC `top`) added, tier A, `mined` (`corpus/SOURCES.md`). Registry 217 → 219 rows; S294 `used-by` duplicate removed (D2). Round-63 S294 offsets corrected by appended section (D1). Capability rows: none entered (no demonstrated capability). Assimilation: none.

### Planned (r65)

- Re-probe the N4 fixture against both writers before any declaration (lesson M1); drop or re-shape the row, and settle N2's empty-directory fixture (M5) and the symlink-in-untracked rule.
- Land `tools/souji-freeze-check.py --chronology` (candidate `.ufo/waves/round-64/w1/S64ExecFreeze/`) with its historical sweep before any freeze (M2).
- Build every control as a lane commit strictly before the freeze; regenerate the C1 stub receipts from the fixed command builder (M3, M4).
- C2: add a green/decoy control and a row-presence pin; cover the s3 unmerged clause; after-literals `S2_AFTER`, `S3_AFTER` in `census/round-64/c2-counter.py`.
- Untracked visibility (`status.showUntrackedFiles`) as its own claim with a do-nothing control (named limit, sentinel S64-F1).
- Carried: SKILL.md:830 overreach (R1), knowledge-entry `verified-at` refresh (R3), operator L0 lines (MACHINE BLOCK, numeric mapping, edge-class tie-break, planner seat).
- Code-kind registry row for `pathspec.c` `parse_long_magic` (S296 named limit), if the operator accepts code rows.

### Round 66 measurements (2026-11-05, Linux; base `045e103478fa4a7eff77db2cab5b9e2f26959a0a`; instruments `4576f101a9200206de00ef00923dd38a7b2dbc7d`; controls `4864c01f112c9f423def430d9b6e01bdc0e21f36`; freeze `02cc660965e027c6c6390604e50702bb06377b2e` (attempt 2; attempt 1 `5d17a5de` superseded); prereg `census/round-66/preregistration-attempt2.txt`; measured revision `c13fbb4e1b563a78278ddc14316c20252e9a6d8d`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 caller-injected env routes and mode bits (E1–E6, MOD2, MOD3, SY3) | operability 8 (not re-scored: no reproducible 0–10 mapping) | do-nothing (base writer): `base_forgeries=8 new_forgeries=8 class_mismatches=8`, EXIT 1 (`census/round-66/controls/c1-do-nothing.txt`) | `SUMMARY matrix=28 base_forgeries=8 base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS`, EXIT 0 (`census/round-66/records/c1-after.txt`); forgeries 8 → 0; honest 5/5 kept | `python3 -B census/round-66/c1-counter.py --root . --matrix census/round-66/c1-matrix.tsv --base-rev 045e103478fa4a7eff77db2cab5b9e2f26959a0a --rev c13fbb4e1b563a78278ddc14316c20252e9a6d8d --tool tools/souji-receipt-write.py --work DIR` | `c13fbb4e` |
| C2 SKILL statement population s1–s5 and M-ENV kill | calibration 7 (not re-scored) | do-nothing: `SUMMARY rows=5 findings=1 verdict=FAIL`, EXIT 1 (s5 absent at base); round-65 counter on M-ENV: `findings=0` (M10 survival) | landed: `SUMMARY rows=5 findings=0 verdict=PASS`, EXIT 0 (`census/round-66/records/c2-after.txt`); round-66 counter on M-ENV: `findings=1 verdict=FAIL` (`records/c2-mutant-m-env.txt`) | `python3 -B census/round-66/c2-counter.py --root . --tsv census/round-66/c2-statements.tsv --tsv-rev 4576f101a9200206de00ef00923dd38a7b2dbc7d --rev c13fbb4e1b563a78278ddc14316c20252e9a6d8d`; M-ENV: `python3 -B census/round-66/c2-mutate.py --writer tools/souji-receipt-write.py --out DIR/m-env.py` committed in a scratch clone | `c13fbb4e` (mutant scratch commit `0c8c5f4b`, not in the lane) |

Axis scores unchanged (calibration 7, coverage 8, operability 8). Both claims meet their frozen predicates. Neither is admitted as harm-free: C1 carries a named open route (`GIT_COMMON_DIR`, measured on the landed candidate, `census/round-66/probes/w2-w3-env-probe.txt`), a named honest-run refusal cost (the `git -c` child, same probe, rc 2 candidate vs rc 0 base) and an unmeasured setgid row; C2's s5 wording overreaches the scope the population can check (lesson M5). Both verdicts are for the operator to rule.


### Round 65 measurements (2026-11-05, Linux; base `4a43a4d919c5b51ae9be859a1266ce4b11337b0b`; instruments `2761f0aa4d2431b4b9abb4aa997dd3116b0b25b8`; controls `3c5bfdc0db50785cb7b2ec60e509facf2d7e9f25`; freeze `d2850b3eb160ae65c1c65b93753dfec7f4153b45`; prereg `census/round-65/preregistration.txt`; measured revision `40a371d8232e89e4f50d3ece4ff8779f44c0ee4c`)

| claim | axis | before (do-nothing, base bytes, controls `3c5bfdc0`) | after (landed bytes, measured rev `40a371d8`) | counting command | measured commit |
|---|---|---|---|---|---|
| C1 writer concealment refusals, 19-row matrix | operability 8, numeric delta 0 (no reproducible 0–10 mapping) | `new_forgeries=12 new_honest=5 class_mismatches=12`, EXIT 1 (`census/round-65/controls/c1-do-nothing.txt`) | `new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS`, EXIT 0 (`census/round-65/records/c1-after.txt`) | `python3 -B census/round-65/c1-counter.py --root . --matrix census/round-65/c1-matrix.tsv --base-rev 4a43a4d919c5b51ae9be859a1266ce4b11337b0b --rev 40a371d8232e89e4f50d3ece4ff8779f44c0ee4c --tool tools/souji-receipt-write.py --work DIR` | `40a371d8232e89e4f50d3ece4ff8779f44c0ee4c` |
| C2 live-marker statement agreement, 4 statements | calibration 7, numeric delta 0 (no reproducible 0–10 mapping) | `findings=2 verdict=FAIL` (s2 SCOPE-OVERREACH, s4 GOVERNED-STATEMENT-UNRESOLVED), EXIT 1 (`census/round-65/controls/c2-do-nothing.txt`) | `findings=0 verdict=PASS`, EXIT 0 (`census/round-65/records/c2-after.txt`); dead-token second-polarity mutant produces findings (selftest 13/13) | `python3 -B census/round-65/c2-counter.py --root . --tsv census/round-65/c2-statements.tsv --tsv-rev 2761f0aa4d2431b4b9abb4aa997dd3116b0b25b8 --rev 40a371d8232e89e4f50d3ece4ff8779f44c0ee4c` | `40a371d8232e89e4f50d3ece4ff8779f44c0ee4c` |

Freeze chronology: freeze-check `--substance` at the freeze commit → `SUMMARY claims=2 findings=0`
(`census/round-65/records/freeze-check-substance-at-freeze.txt`). Realizability probes committed pre-freeze
(`census/round-65/probes/`): the r64 M1 N4 dispute resolved mechanically (dual-seed fixture is the realizable
shape: base=accept, candidate refuses; the no-dual-seed shape fails instrument resolution for BOTH slots), the
r64 M5 N2 shapes probed (empty and non-empty pre-run dirs both realizable in-run; pre-run-file polarity arms
accept on both slots). Named limits frozen in the prereg: env redirects beyond `GIT_INDEX_FILE` unread; the C2
live read is lexical and does not prove reachability (an `if False:` refusal is the C1 matrix's kill); N4
depends on the dual-seed fixture shape. The chronology arm landed post-freeze (`16da2445`) — the intended
pre-freeze working-tree copy was missed; disclosed, closure rules. Owned score values unchanged (calibration 7,
coverage 8, operability 8); the lane still has no reproducible 0–10 mapping and the closure rules admission.

### Capabilities (round 65 row)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| freeze chronology binding | refuse a preregistration whose control receipts' `rev=` is not a strict ancestor of the freeze commit or whose `After:` measurement receipts do not bind strict descendants (`--chronology`, composing with `--substance`); default output byte-identical over 33 committed preregistrations | `python3 -B tools/souji-freeze-check.py --selftest --chronology` → `cases=52 pass=52` (`census/round-65/records/freeze-check-selftest-chronology.txt`); landed `16da2445088ccca15aa32c66841d878ee57a8706` | r65 (closure-gated) |

### Round 65 corrections and wave-close dispositions (append-only)

R65-ERRATUM-PREREG (SCORECARD, round 65): `census/round-65/preregistration.txt` says `tools/souji-freeze-check.py --chronology` "landed pre-freeze" and its selftest "stays 52/52 with --chronology". Both are false at the freeze `d2850b3e` (the arm first exists at `16da2445`; the freeze-check selftest there is 41/41). The prereg is frozen and is not amended. Recorded as lesson M7.

R65-KILL-POWER (wave close; the frozen predicates are unchanged, the counts are as measured):
- C1 kill-power: a same-content symlink retarget is not a matrix row and survives a read-through symlink mutant (M11); setuid, setgid and sticky bits are masked (M12).
- C2 kill-power: the emission token `return` matches `returncode`; a deleted env refusal (mutant m4) gives `findings=0` (M10).
- Both claims verify on their frozen predicates and are reported with these HIGH gaps; the closure judge rules on admission. No owned score changed.

### Round 67 measurements (2026-11-05, Linux; base `3639087917eaeb28719d7603110a6ec22782100e`; instruments `05eb2cee2794e42559c5ba15c3ebfdf7caecfee5`; controls `d544e75a` (C1), `832a4d43` (C2); freeze `4c61efcbe8c4e7586590c76965e5b1b29a1fa9a7` (attempt 4; attempts 1–3 superseded); prereg `census/round-67/preregistration-attempt4.txt`; measured revisions `f70da577eb1e1624cc63ab8fd0468565927d9b6a` (C1) and `c13fbb4e1b563a78278ddc14316c20252e9a6d8d` (C2, pinned historical))

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 value-checked caller `GIT_COMMON_DIR` (W1–W3 on the 31-row matrix) | operability (receipt-binding; Q59 neutral) | base: `base_forgeries=2 base_honest=6` (W1, W2 accept); do-nothing `new_forgeries=2`, `EXIT=1` (`census/round-67/controls/c1-do-nothing.txt`) | `SUMMARY matrix=31 base_forgeries=2 base_honest=6 new_forgeries=0 new_honest=6 class_mismatches=0 regress=PASS`, `EXIT=0` (`census/round-67/records/c1-after.txt`); operability score unchanged at 8 (no reproducible 0–10 mapping for a receipt-binding row); named trade: relative value with cwd ≠ root refused (base rc 0, candidate rc 2) | `env -u GIT_COMMON_DIR -u GIT_NO_REPLACE_OBJECTS python3 -B census/round-67/c1-counter.py --root . --matrix census/round-67/c1-matrix.tsv --base-rev 3639087917eaeb28719d7603110a6ec22782100e --rev f70da577eb1e1624cc63ab8fd0468565927d9b6a --tool tools/souji-receipt-write.py --work DIR` | `f70da577eb1e1624cc63ab8fd0468565927d9b6a` |
| C2 statement counter with redirect-claim marker check (s1–s5) | calibration 7 (bookkeeping file) | round-66 counter at `c13fbb4e`: `SUMMARY rows=5 findings=0 verdict=PASS`, `EXIT=0` (`census/round-67/controls/c2-do-nothing-r66.txt`); M4 selftest case bound to the wrong row (vacuous) | `FINDING SCOPE-OVERREACH s5`, `SUMMARY rows=5 findings=1 verdict=FAIL`, `EXIT=1` at `c13fbb4e` (`census/round-67/records/c2-after.txt`); reverted-rule mutant `m10-s5-assertion-line-not-live: findings=0 want=1 MISMATCH`, `EXIT=1` (`records/c2-mutant-reverted-selftest.txt`); enum-weakened mutant `findings=0` (`records/c2-mutant-enumweak.txt`); declared selftest `SELFTEST pass cases=17 fail=0`, `EXIT=0` (`records/c2-selftest.txt`; the prereg's literal `cases=17 pass=17` is not the printed format, lesson M8). `REDIRECT_ENUM` is not iterated by the counter (lesson M7). Calibration score unchanged at 7: the flag detects a historical overreach, it is not a 0–10 movement. | `env -u GIT_NO_REPLACE_OBJECTS -u GIT_COMMON_DIR python3 -B census/round-67/c2-counter.py --root . --tsv census/round-67/c2-statements.tsv --tsv-rev 05eb2cee2794e42559c5ba15c3ebfdf7caecfee5 --rev c13fbb4e1b563a78278ddc14316c20252e9a6d8d` | `05eb2cee2794e42559c5ba15c3ebfdf7caecfee5` (instruments); measured at `c13fbb4e` |

Trend-visible score changes: none (calibration 7, coverage 8, operability 8). C1 and C2 both verify on their frozen predicates; C1's named relative-value trade is routed to the operator and not counted as an improvement without that ruling.

### Round 82 measurements (2026-11-07, Linux; lane base `488956c45166ed6edc21567e8588a8134413949e`; instruments `a45a9022…`;
freeze P `1cb7c7d11aaac36a1ac757f339d77875ea4b192b` (freeze-check findings=3, lesson M1 — the prereg landed in P alongside the
controls), F corrective `d302b4f33`, `28fd32c03`, W1 C1 counter `f5bc4197`, W2 C2 tool `73110f6f`, A records below)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 own-tree binding | calibration 7 | `census/round-82/controls/c1-K-a-r81-counter.txt` `SUMMARY rows=32 mismatches=2 accepted=2 refused_true=0` EXIT=1 (NF-F, NF-G) | `census/round-82/records/c1-after.txt` `rows=32 mismatches=0 accepted=0 refused_true=0` EXIT=0; K-b 2 accepted, K-c 2 accepted [NF12c, NF-I] red; r78 22/22 + 12/12, r77 35/35 + 7/7, r79 harness 9/9, r80 harness 18/18, r81 harness 25/25 | `python3 -B census/round-82/c1-false-row-harness.py --counter census/round-82/c1-pointer-counter.py --lane <lane> --fleet-root <fleet> --work <scratch>` | `f5bc4197d426527adc6f5d52f2d7834c0f021f2e` |
| C2 descendant-tree kill | operability 8 | Base `census/round-82/controls/c2-K-a-do-nothing.txt` under `env SHELLOPTS=monitor`: `rows=16 mismatches=4 errors=0 orphans=4` EXIT=1 (v7/v8 + m1/m2 each `survivors=1`); default launch Base 16/16 (`records/prefreeze/c2-base-default.txt`) | `census/round-82/records/c2-after.txt` and `c2-after-monitor.txt` both `rows=16 mismatches=0 errors=0 orphans=0` EXIT=0; K-b 12 orphans, K-c p3 red; selftest 57/0, r17 37/0/0, probe D successor 6/6 `records/probe-d-successor.txt` | `python3 -B census/round-82/c2-vault-signal-counter.py --tool tools/souji-vault-verify.sh --work <scratch>` (and the same under `env SHELLOPTS=monitor`) | `73110f6fe56f2a8383baed0ea7dc77f8b7f6ba5e` |

No owned axis score changed (calibration 7, coverage 8, operability 8). Registry agreement at W2 `k1=1 k2=1`
(`census/round-82/records/registry-agreement-at-W2.txt`); the two remaining findings are K1 `cited-no-row S146` and K2
`rewrote-not-appended SCORECARD.md`, both accepted-red with the r81 reasons (append-only discipline).

**Append-only addendum after wave `w1` (Amendment 59, before filing).** Both rows above were frozen and re-derived
by non-author seats (`S82ExecC1`, `S82Connector` §0, `S82Sentinel`, `S82MutTool`, `S82Connector2`,
`S82MutCounter`: 32/0/0/0 and 16/0/0/0 both launches, all five C1 regressions, selftest/r17/probe D). The wave then
falsified six sentences of the frozen wording, and the round files the narrowed claims, not the wider ones:

- C1: the own-tree binding runs **after** the last-component test (`c1-pointer-counter.py:349` then `:353`), the
  own-tree rule binds only the identity path and a `waves/`/`wave/`/`records/wave-<w>/` capture shape — so a genuine
  own-tree move into a real `wN/` dir is **refused** while the harness's planted shape is kept — and the
  census-in-tree full-suffix branch changes no frozen verdict. `plans/round-82.md` A1/A2/A3/A5; Q150, Q151.
- C2: the `m1/m2` row ids carry no monitor of their own (the counter's `m-` prefix test is dead code); the monitor
  matrix is the counter's second launch. The empty-`CLI_PID` window W2 opened (signal between `timeout … &` and
  `CLI_PID=$!` → "stopped it, no verdict" with the subtree alive; base 0/150 vs W2 1/150) is **repaired** by R1
  before filing. `plans/round-82.md` A6/A7/A8/A9.
- Repair re-measurement on the filed bytes (tool sha256 `dd6d440e…`, `census/round-82/records/repair-w3/`):
  `rows=16 mismatches=0 errors=0 orphans=0` EXIT=0 under the default **and** the monitor launch,
  `selftest: 57 checks, 0 failed`, r17 `total=37 failed=0 skipped=0`, probe D `arms=6 failed=0`.
- Stated limits carried, not claimed: own-tree `wN/` over-refusal; identity clause inseparable from a suffix-only
  rule on this population; per-node `pgrep -P` cost (≥12 descendants exceeds the 5 s settle); snapshot→KILL reuse
  window; `before = 4` is the modal value of a noisy control; every C2 receipt reproduces only untraced.
  Ledger: `.ufo/waves/round-82/claim-falsification.tsv` (8 attack seats reconciled, 2 claims).

### Round 83 measurements (2026-11-08, Linux; lane base `1e870403c5d806a5cf9ac93b00da7a928359608f`; instruments P `1014143d`, C2-instrument correction `51b50c94`, freeze F `fbf0ae5e`; candidates W1 `bbffe6a0`, W2 `9994af61`, C1 cleanup after the first score)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 own-tree real wave shapes + per-branch remainder | calibration 7 (no reproducible 0–10 mapping; verdict calibration improved) | `census/round-83/controls/c1-K-a-r82-counter.txt` `SUMMARY rows=36 mismatches=2 accepted=0 refused_true=2 errors=0` EXIT=1 — the two refusals are TF6 (`w2/`) and TF7 (`w1/`) | `census/round-83/records/c1-after.txt` `SUMMARY rows=36 mismatches=0 accepted=0 refused_true=0 errors=0` EXIT=0 at counter sha256 `052c4f3f…`; TF6/TF7 kept, NF-J/NF-K refused; regressions r77 35/35 + 7/7, r78 22/22 + 12/12, r79 9/9, r80 18/18, r81 25/25, r82 32/32 | `python3 -B census/round-83/c1-false-row-harness.py --counter census/round-83/c1-pointer-counter.py --lane <lane> --fleet-root <fleet> --work <empty>` | W1 `bbffe6a0` + cleanup commit; C1 receipts regenerated on the final bytes (`052c4f3f…`) |
| C2 one-pass fork-free descendant walk with starttime re-check | operability 8 (no reproducible 0–10 mapping; verdict operability improved) | load-dependent race, no fixed count: `controls/c2-K-a-r82-tool.txt` `mismatches=4 orphans=4` (load1≈250), `records/c2-before-pgrep.txt` `mismatches=1 orphans=1` (load1≈56), five reviewer executions 0,2,2,2,4 (idle host GREEN, deep rows 1.8/2.0/3.8/4.6 s); structural before: `pgrep` 106–108 invocations, N=24 3.8–5.0 s at the settle | `census/round-83/records/c2-after.txt`, `c2-after-run2.txt`, `c2-after-pgrep.txt` all `SUMMARY rows=20 mismatches=0 errors=0 orphans=0` EXIT=0 at tool sha256 `72a405f2…` (whole-file stat read + arity guard); deep rows 1.2–1.6 s, 0 survivors, both launches; `pgrep` 0 (106–108 before); selftest 57/0, r17 37/0, probe D 4/4; the non-author run `S83ExecC2/c2-lane-b0a5b66.txt` is green on the guarded intermediate bytes while a short-remainder pid was live (the `9994af61` bytes `d4826cce…` scored `mismatches=2 orphans=2` there — the `${20}` abort, repaired); S83Sentinel F1 (comm newline) took the parse to a whole-file read | `python3 -B census/round-83/c2-tree-walk-counter.py --tool tools/souji-vault-verify.sh --work <empty>` | W2 `9994af61` (tool) + `802a41e7` (arity guard) + A10 (whole-file read; receipts bind `72a405f2…`) |

No owned axis score changed (calibration 7, coverage 8, operability 8): the lane still has no reproducible 0–10
mapping. Both claims meet their frozen predicates on the final bytes; the wording was narrowed before filing
(`plans/round-83.md` A1–A8), because the wave falsified parts of the frozen sentences: the six-shape list is
over-specified (a `w[0-9]+/`-only list meets the target, three alternates are dead as decisions), the full-suffix
clause is exercised one component deep only, the identity disjunct is unreachable (deleted), no recorded ledger move
has used the `wN/` layout, the C2 control's mismatch count is host-load dependent (4/2/1 on the same bytes), and the
starttime re-check / as-discovered order carry no row (mutants survive 20/20). Named limits carried: `records/` and
the other non-wave own-tree dirs refused; any `w[0-9]+/` accepted; non-atomic `/proc` (one read-then-signal window per
pid); no pidfd; setsid escape; the foreground fallback keeps no traps; `pgrep` counted by an external shim.

### Round 83 capability row

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| deep-tree signal kill inside a settle | kill an N=24 descendant CLI tree on a caller's signal in 0.3–0.4 s (from a one-pass `/proc` ppid map, kill-as-discovered, starttime re-check) with 0 survivors and no leftover private file, under both the default and the job-control launch | `python3 -B census/round-83/c2-tree-walk-counter.py --tool tools/souji-vault-verify.sh --work <empty>` → `rows=20 mismatches=0 errors=0 orphans=0` (`census/round-83/records/c2-after.txt`); control `controls/c2-K-a-r82-tool.txt` red | r83 |

### Planned (r84)

- C1: a deep-token pair (token two components below its wave dir → kept `…/w2/sub/X`, flattened `…/w2/X` refused),
  true rows for `a2w1/` and `assimilation/`, and the `NF-L`/`NF-L2`/`NF-M`/`NF-L3` rows the mutants (m6/m7/m8,
  critic A1–A3, MutCounter survivors) showed are missing; ground or delete the census-in-tree branch.
- C2: a pid-reuse row that separates the starttime re-check from a plain kill (MutTool m1 survives today), a
  parent-before-child row, the `termign-fork` and `p5-late-term` rows, and a `strace`-robust settle.
- Carried unchanged from the r81 spot-check list: `_regular` pathspec framing, the quarantine intro-blob digest row,
  the fork-tail row, the r79 gate re-measurement, the check-4 300 s backstop, r76 K03/K04, status-trusting lane
  tools, r17 240 s runners.
- Report/registry hygiene: the r82 spot-check's LOG correction is in the r83 LOG entry; S330 now exists as a row;
  the r82 report's missing `51a5e7fa` row is named in the r83 report.

### Round 84 measurements (2026-11-08, Linux; lane base `54709d0db92d9dcd95504a34173c1f6a3fd88ec1`; instruments P `bd2bbb12`, freeze F `35d87842`; C2 repair `1f49b3a7`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 the false-row population binds five counter clauses | calibration 7 (no reproducible 0–10 mapping; verdict calibration improved) | the same counter (`052c4f3f…`) and the same five mutants on the r83 36-row population: pristine `rows=36 mismatches=0`, every mutant `killed=no`, `SUMMARY mutants=5 sets=r83 pristine_r83=ok killed_r83=0 killed_total=0`, EXIT 0 (`census/round-84/controls/c1-before-r83-population.txt`) | r84 44-row population: pristine `rows=44 mismatches=0 errors=0`, `killed_r84=5` (m6↔NF-L, m7↔NF-L2, m8↔TF9/TF10, m9↔TF8/TF9/TF10/NF-P, m10↔NF-M), EXIT 0 (`census/round-84/records/c1-after.txt`); r83 36-row regression stays green | `python3 -B census/round-84/c1-clause-battery.py --counter census/round-84/c1-pointer-counter.py --work <empty dir outside /tmp> --only r84 --expect-killed 5` (after) / `--only r83` (before) | after measured on `1f49b3a7`; before on `bd2bbb12` |
| C2 the vault CLI's signal path freezes the tree before terminating it | operability 8 (no reproducible 0–10 mapping; verdict operability improved) | r83 tool bytes `72a405f2…` (control `census/round-84/controls/c2-K-a-r83-tool.sh`): `rows=22 mismatches=2 errors=0 orphans=2`, one surviving `setsid sleep 600` per late row, EXIT 1 (`census/round-84/controls/c2-before-r83-tool.txt`) | filed tool `030fa10d…`: `rows=22 mismatches=0 errors=0 orphans=0`, l1 0.7 s / l2 0.6 s, 0 survivors, EXIT 0 (`census/round-84/records/c2-after.txt`); selftest 57/0, r17 37/0/0, probe D 4/0; clause mutants on the filed bytes: STOP→TERM killed, no-KILL-sweep killed, single-pass and first-line-recheck survive (unrowed belts, A1/A2) | `python3 -B census/round-84/c2-late-fork-counter.py --tool tools/souji-vault-verify.sh --work <empty dir outside /tmp>` | after measured on `1f49b3a7`; before on `bd2bbb12` |

No owned axis score changed (calibration 7, coverage 8, operability 8): the lane still has no reproducible 0–10
mapping. Both claims meet their frozen predicates on the filed bytes. The wave narrowed two sentences before filing
(`plans/round-84.md` A1/A2: the second map pass and the whole-file re-check carry no row) and recorded the substrate
of two seats' findings (A5). Named limits carried: the population proves discrimination on its own rows; NF rows are
byte-equal copies by construction; five hand-written mutants are not a generated battery; a kill is a non-zero harness
exit; a child forked in the read→STOP window, a comm-with-newline row, a re-forking CLI and a daemonizing CLI are
unrowed; the STOP→KILL pair widens the pid-reuse window the r83 tool disclosed.

### Round 84 capability rows

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| clause-kill battery over two pinned populations | measure which clauses of a pointer counter a population actually binds: five frozen single-edit mutants scored on the r83 36-row and the r84 44-row population, with a pristine arm on each and an INVALID verdict when an edit does not apply exactly once | `python3 -B census/round-84/c1-clause-battery.py --counter census/round-84/c1-pointer-counter.py --work <empty> --only r84 --expect-killed 5` → `killed_r84=5` (`census/round-84/records/c1-after.txt`) | r84 |
| freeze-then-kill for a descendant tree | stop a CLI descendant tree before any trappable signal reaches it (SIGSTOP on discovery, second map pass, SIGKILL sweep with a starttime re-check), so a CLI that traps the caller's signal and forks a `setsid`'d child leaves nothing behind | `python3 -B census/round-84/c2-late-fork-counter.py --tool tools/souji-vault-verify.sh --work <empty>` → `rows=22 mismatches=0 errors=0 orphans=0` (`census/round-84/records/c2-after.txt`); control `census/round-84/controls/c2-before-r83-tool.txt` red | r84 |

### Planned (r85)

- C1: `NF-L3` (a token whose first below-round component is not a wave dir), a `census/round-<N>/`-token item to
  ground or delete the census-in-tree branch, and rows for the token-on-line/unknown-class refusals
  (S84MutCounter survivors).
- C2: a row for the second map pass (an observable read→STOP-window fork), a comm-with-newline row for the
  whole-file re-check (r83 D5), a pid-reuse row, a parent-before-child row, `termign-fork`/`p5-late-term`, and a
  `strace`-robust settle.
- Carried unchanged: the r81 list (`_regular` pathspec framing, quarantine intro-blob digest row, fork-tail row, r79
  gate re-measurement, check-4 300 s backstop, r76 K03/K04, status-trusting lane tools, r17 240 s runners) and the
  r83 list's C2 items not built this round.

### Round 85 measurements (2026-11-08, Linux; lane base `705fa1385c4ccec23811cfa57104046ec6587258`; controls `5bd5a0ce`; freeze `43c630eb`; C1 counter `91b4ffde`; after-arms `43c630eb` + the wave commit)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 class-enum guard bound by the population | calibration 7 | `census/round-85/controls/c1-before-r84-population.txt` `ARM pristine pop=r84 rows=44 mismatches=0`, `m11-class-enum killed=no`, `SUMMARY mutants=6 sets=r84 pristine_r84=ok killed_r84=5`, EXIT 0 | `census/round-85/records/c1-after.txt` `ARM pristine pop=r85 rows=47 mismatches=0 errors=0 exit=0`, six `killed=yes`, `SUMMARY mutants=6 sets=r85 pristine_r85=ok killed_r85=6`, EXIT 0; shadow probe `census/round-85/records/a1-c7-shadow.txt` `killed_r84=0 killed_r85=0` with both arms green | `python3 -B census/round-85/c1-clause-battery.py --counter census/round-85/c1-pointer-counter.py --work WORK --only r85 --expect-killed 6` (after) and `--only r84 --expect-killed 5` (before) | `91b4ffdea534acdc23683a8dd8d0f698e4672f739bcc31cee53286425ddd7304` (counter), measured at the P commit `5bd5a0ce` |
| C2 record-agreement K4 byte truth | operability 8 | `census/round-85/controls/c2-before-base-tool.txt` (base blob `ec5b809d`) `SUMMARY rows=7 mismatches=3 errors=0`, KF1/KF2/KF3 `k4=0 match=no`, EXIT 1 | `census/round-85/records/c2-after.txt` `SUMMARY rows=7 mismatches=0 errors=0`, three forged rows `k4=1 named=yes`, honest rows unchanged, EXIT 0 | `python3 -B census/round-85/c2-k4-counter.py --tool tools/souji-record-agreement.py --work WORK` | filed tool `ed1ada73…d382` at the C2 commit |

No owned axis score changed (calibration 7, coverage 8, operability 8 — the lane has no reproducible 0–10 mapping);
both rows carry the verdict, the counting command and the measured commit instead. The census-in-tree branch is
reported as REACHABLE and unbound: its mutant survives both populations (`records/a1-c7-shadow.txt`) but the branch
refuses a directly driven row and one added row (NF-W) kills it (`.ufo/waves/round-85/w1/S85Scribe.md` F1); the row
and the 48-row population are routed to r86 and nothing was deleted. The same measurement on the last-component
basename check gives the same verdict (unbound, reachable; its first probe crashed rather than killed, F4 second
run), and the own-tree belt is bound (7/7). No clause the round examined is shadowed.

### Capabilities (round 85 rows)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| clause-shadow classification | tell an unbound clause from a shadowed branch by scoring a single-edit mutant of ONLY that clause on every pinned population and attributing its survival (reachable → unbound, needs a row; a belt above refuses every input → shadowed, no row can bind it) | `python3 -B census/round-85/c1-clause-battery.py --counter census/round-85/c1-pointer-counter.py --mutants census/round-85/probes/c7-shadow.json --work WORK --only r84,r85 --expect-killed 0` → `killed_r84=0 killed_r85=0` (`census/round-85/records/a1-c7-shadow.txt`) | r85 |
| stat-cache-forgery counter over a tool's clean verdict | score any lane tool that reports a clean/unchanged verdict against seven frozen rows (same-size file forge, symlink retarget, size-changing forge, honest stale stat, plain edit, untracked, clean), running the tool as a subprocess on its public CLI path | `python3 -B census/round-85/c2-k4-counter.py --tool TOOL --work WORK` → `rows=7 mismatches=0` on the filed bytes, `mismatches=3` on the base blob | r85 |

### Planned (r86)

- C1 (calibration/operability): delete the shadowed census-in-tree branch (r85 A1 measured it unreachable) with both
  pinned populations green and the six mutants still killed; carry the r84 C1 list the wave left open (NF-L3, the
  token-on-line / unknown-class rows the S85MutCounter survivors name, the last-component shadow probe).
- C2 (operability): the S85ExecK4 / S85Sentinel escapes (stage-2 and intent-to-add entries, gitlinks, newline paths,
  a stub writer beside a copied tool) become frozen rows; the r83/r84 C2 carried list (pid-reuse row,
  parent-before-child, termign-fork/p5-late-term, strace-robust settle) unchanged.
- Carried: `_regular` pathspec framing, quarantine intro-blob digest row, r79 gate re-measurement, check-4 300 s
  backstop, r76 K03/K04, the remaining status-trusting tools (`souji-verify.sh:713,883`, `souji-census.sh`,
  `souji-idx-repair.py`), r17 240 s runners, `souji-freeze-check.py` prereg grammar (Q99).


### Round 86 measurements (2026-11-08, Linux; lane base `89d02c907d40cc09fedc9d420cf9509df685e143`; instruments P `47602fa6`, freeze F `d77b4258`, C2 repair `2acbbfc8`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 the two r85-measured reachable-and-unrowed clauses get their rows | calibration 7 | `census/round-86/controls/c1-before-r85-population.txt` (same counter, same eight mutants, the r85 47-row population) `ARM pristine pop=r85 rows=47 mismatches=0 errors=0 exit=0`, `c7-census-in-tree killed=no`, `m14-short-shape killed=no`, `SUMMARY mutants=8 sets=r85 pristine_r85=ok killed_r85=6 killed_total=6`, EXIT 0 | `census/round-86/records/c1-after.txt` `ARM pristine pop=r85 rows=47 mismatches=0 errors=0 exit=0`, `ARM pristine pop=r86 rows=49 mismatches=0 errors=0 exit=0`, eight `killed=yes` on r86, `SUMMARY mutants=8 sets=r85,r86 pristine_r85=ok pristine_r86=ok killed_r85=6 killed_r86=8 killed_total=14`, EXIT 0 | `python3 -B census/round-86/c1-clause-battery.py --counter census/round-86/c1-pointer-counter.py --work WORK --only r85,r86 --expect-killed 14` (after) and `--only r85 --expect-killed 6` (before) | counter `census/round-86/c1-pointer-counter.py`, harness `census/round-86/c1-false-row-harness.py`, population `census/round-86/c1-false-rows.tsv` sha256 `79db70f6…`, items `census/round-86/c1-items.tsv` sha256 `5abf3b01…`, mutants `census/round-86/c1-mutants.json`; all at P `47602fa6` |
| C2 K4 carries the writer's index-flag sweep and keeps a record path on one line | operability 8 | `census/round-86/controls/c2-before-base-tool.txt` on the lane-base tool bytes `0ade0751…`: `SUMMARY rows=9 mismatches=2 errors=0`, KG1 `k4=0` (a gitlink commit concealed under skip-worktree emits no row), KG2 `named=no` (newline path space-joined out of the record), EXIT 1 | `census/round-86/records/c2-after.txt` on the filed tool sha256 `cf875367…` (the sentinel's env route repaired in `f5e196a2`, `records/c2-env-route.txt` `k4_rows_with_env` 0 → 1): `SUMMARY rows=9 mismatches=0 errors=0`, KG1 `k4rows=['.|index-flag-concealed']`, KG2 `named=yes`, the seven r85 rows unchanged, EXIT 0 | `python3 -B census/round-86/c2-k4-counter.py --tool tools/souji-record-agreement.py --work WORK` (after) and `--tool census/round-86/controls/c2-before-base-tool.py` (before) | repair commit `2acbbfc8`; counter `census/round-86/c2-k4-counter.py` |

No owned axis score changed (calibration 7, coverage 8, operability 8 — the lane still has no reproducible 0–10
mapping); both rows carry the verdict, the counting command and the measured commit instead. The wave narrowed five
sentences before filing (`plans/round-86.md` A1–A5): a flagged regular file with changed bytes is refused by the truth
check first; the sweep reads a gitlink entry, not submodule state; each new row binds one arm of its clause, not the
whole clause (S86Critic C1-c measured two strictly weaker counters scoring 8/8); the lane's own record-agreement run
still carries the inherited K3 tally row; and the `FLAGFAIL` branch is not the corrupt-index row.

### Round 86 capability rows

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| clause-grounding with a row pair | turn a clause a population leaves unrowed into certified coverage: one frozen row per clause plus one single-edit mutant, with the do-nothing control (same mutants, old population) proving the delta is the row and not the rule | `python3 -B census/round-86/c1-clause-battery.py --counter census/round-86/c1-pointer-counter.py --work WORK --only r85,r86 --expect-killed 14` → `killed_r85=6 killed_r86=8` (`census/round-86/records/c1-after.txt`, control `controls/c1-before-r85-population.txt`) | r86 |
| index-flag sweep in an audit verdict | answer for the index-flag classes a status-based truth check cannot see (a gitlink entry, an unmerged entry, a flagged path) by running the receipt writer's own `ls-files -v -z` sweep, and keep a record's path name on one physical line | `python3 -B census/round-86/c2-k4-counter.py --tool tools/souji-record-agreement.py --work WORK` → `rows=9 mismatches=0` (`census/round-86/records/c2-after.txt`; before arm `mismatches=2`) | r86 |

### Planned (r87)

- C1 (calibration): the arms A3 leaves unrowed — the `len(got) < 2` half of the short-shape guard, a non-wave target
  under a census root reaching the census-in-tree `_capture_ok` suffix rule, and the four r85-measured survivors
  (m12 token-on-line, m16 punctuation, m17 duplicate id, plus a positive QUARANTINED row); then the basename clause,
  which S86Critic's trace shows cannot flip a verdict while the suffix rules stand (shadowed-for-verdict), recorded
  as a definition rather than a row.
- C2 (operability): the r85 A2/T-item residuals the wave left open — the writer's 200-character stderr truncation
  that hides `AttributeError` (S86ExecK4 §2b), a pinned writer digest so the delegation limit stops being
  load-bearing (S86ExecK4 §3b2), and the `status --porcelain -z` switch that would make the status arm's quoting
  depend on the tool.
- Carried: the r85 list's C2 items (pid-reuse row, parent-before-child, termign-fork/p5-late-term, strace-robust
  settle), `_regular` pathspec framing, the quarantine intro-blob digest row, the r79 gate re-measurement, check-4
  300 s backstop, r76 K03/K04, the r17 240 s runners, the inherited K3 tally row (A4).

### Round 87 measurements (2026-11-08, Linux; lane base `5e288bb3152328f371325d0bf4fee7309d629991`; instruments P `77ccef7c`, freeze F `6ed2d368`, C2 repair `6e502c5c`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 the two r86-measured reachable-and-unrowed clauses get their rows; a third candidate is measured already bound | calibration 7 | `census/round-87/controls/c1-before.txt` (same counter, same ten mutants, the r86 49-row population) `ARM pristine pop=r86 rows=49 mismatches=0 errors=0 exit=0`, `m12-token-on-line killed=no`, `m16-nf6b-punct killed=no`, `SUMMARY mutants=10 sets=r86 pristine_r86=ok killed_r86=8 killed_total=8`, EXIT 0 | `census/round-87/records/c1-after.txt` `ARM pristine pop=r86 rows=49 mismatches=0 errors=0 exit=0`, `ARM pristine pop=r87 rows=51 mismatches=0 errors=0 exit=0`, ten `killed=yes` on r87, `SUMMARY mutants=10 sets=r86,r87 pristine_r86=ok pristine_r87=ok killed_r86=8 killed_r87=10 killed_total=18`, EXIT 0 | `python3 -B census/round-87/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py --work WORK --only r86,r87 --expect-killed 18` (after) and `--only r86 --expect-killed 8` (before) | C1 instruments P `77ccef7c5de2ad015f28da70fd58e1156c0f5b73`; population sha256 `b066fa0f…` (51 rows), mutants `9368b342…` (10 members) |
| C2 K4 reads NUL status records, names its writer delegation and keeps the exception line | operability 8 | `census/round-87/controls/c2-before.txt` on the lane-base tool bytes `cf875367…` with its byte-identical writer `70bbf1c2…`: `SUMMARY rows=12 mismatches=3 errors=0`, KN1/KN2/KN3 `named=no` (KN3's record `"bad\nname2.txt"` in git's quoted spelling), EXIT 1 | `census/round-87/records/c2-after.txt` on the filed tool sha256 `0ad9e3bf…` (header names writer `70bbf1c2…`, one appended comment byte changes the printed digest to `1b8ecf32…`): `SUMMARY rows=12 mismatches=0 errors=0`, KN1 `named=yes` (AttributeError line), KN2 `named=yes`, KN3 record exactly `bad\nname2.txt`/`uncommitted-path`/`??`, the nine r85/r86 rows unchanged, EXIT 0 | `python3 -B census/round-87/c2-k4-counter.py --tool tools/souji-record-agreement.py --work WORK` (before: `--tool census/round-87/controls/c2-before-base-tool.py`) | C2 repair `6e502c5c05fd3ca4193883921ef0c9b79a7d36a7`; counter sha256 `4e2b7c06…` |

No owned axis score changed (calibration 7, coverage 8, operability 8 — the lane still has no reproducible 0–10
mapping); both rows carry the verdict, the counting command and the measured commit instead. A third planned row
(`_capture_ok`'s suffix comparison) was measured **already bound** by the r86 row NF12c and was not added
(`census/round-87/records/c1-c8-measured.txt`): the population carries 51 rows, not 52, and the mutant set ten
members, not eleven. The wave then measured that each new row binds ONE spelling of its clause: `S87MutCounter`'s p2
(basename granularity) and p3 (the punctuation lookahead half) survive both populations, so they stay
reachable-and-unrowed and are carried (`plans/round-87.md` A4).

### Round 87 capability rows

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| diagnostic-class rows that bind a guard without a resolution row | bind a diagnostic guard (`ERROR` for an item whose token is off its declared line) by expecting the diagnostic class in a forged row, instead of asserting it | `python3 -B census/round-87/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py --work WORK --only r86,r87 --expect-killed 18` → NE1 kills m12 on r87 and not on r86 (`records/c1-after.txt`, control `controls/c1-before.txt`) | r87 |
| NUL-record status arm with a named delegation | read `git status --porcelain -z`, escape the record path for the reader, and print the writer's path+sha256 header plus the last stderr line on a failed delegation | `python3 -B census/round-87/c2-k4-counter.py --tool tools/souji-record-agreement.py --work WORK` → `rows=12 mismatches=0`, KN1/KN2/KN3 `named=yes` (`records/c2-after.txt`; before arm `mismatches=3`) | r87 |

### Planned (r88)

- C1 (calibration): the clauses the r87 population still leaves unrowed — m17 (`_ledger` duplicate id, which needs a
  population-arm ledger detector rather than a forged row), the `_whole` before-byte half, and
  `_capture_ok`'s `len(want) <= len(have)` half — with the r87 `S87Simplifier`/`S87MutCounter` dead-arm findings
  landed as deletions or documented belts.
- C2 (operability): the r86 routed debt the wave leaves open (the writer's 200-character `FLAGFAIL` cut in the
  embedded bootstrap, a pinned writer digest if the reviewer still wants it load-bearing), plus any sentinel finding
  from `S87Sentinel` that names a reader-misleading path.
- Carried: the r85/r86 C2 list (pid-reuse row, parent-before-child, termign-fork/p5-late-term, strace-robust
  settle), `_regular` pathspec framing, the quarantine intro-blob digest row, the r79 gate re-measurement, check-4
  300 s backstop, r76 K03/K04, the r17 240 s runners, the inherited K3 tally row (r86 A4).

### Round 88 measurements (2026-11-08; lane base `7defe9c5`; instruments/controls P `e60ea25f`; prereg alone F `f74092b2`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 the two r87-carried reachable-and-unrowed clauses get one binding each; the third is measured dead and recorded as a belt | calibration 7 | `census/round-88/controls/c1-before.txt` (same battery, same twelve mutants, the r87 51-row population) `ARM pristine pop=r87 rows=51 mismatches=0 errors=0 exit=0`, `m17-duplicate-id killed=no`, `m18-whole-before killed=no`, `SUMMARY mutants=12 sets=r87 pristine_r87=ok killed_r87=10 killed_total=10`, EXIT 0 | `census/round-88/records/c1-after.txt` `ARM pristine pop=r87 rows=51 mismatches=0 errors=0 exit=0`, `ARM pristine pop=r88 rows=53 mismatches=0 errors=0 exit=0`, twelve `killed=yes` on r88, `SUMMARY mutants=12 sets=r87,r88 pristine_r87=ok pristine_r88=ok killed_r87=10 killed_r88=12 killed_total=22`, EXIT 0; belt `records/c1-dead-belt.txt` `SUMMARY mutants=13 … killed_total=22` with `m19-len-half killed=no` on both sets, EXIT 0 | `python3 -B census/round-88/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py --work WORK --only r87,r88 --expect-killed 22` (before `--only r87 --expect-killed 10`; belt `--mutants census/round-88/c1-mutants-dead.json --expect-killed 22`) | `486826df9da614bb6619e90748b7e9014bf266b1` (records); instruments at `e60ea25f` |
| C2 the K4 delegation's index-flag failure detail is one escaped physical line that keeps both ends of the writer's stderr | operability 8 | `census/round-88/controls/c2-before.txt` on the r87 tool bytes `e1b00e8a…` as both arms: `SUMMARY cases=7 tool_pass=3 before_pass=3`, KFF2/KFF3/KFF4/KFF5 fail, EXIT 1 | `census/round-88/records/c2-after.txt` on the filed tool sha256 `c0604b4a…` with the before bytes as the control: seven `CASE … tool=pass`, `SUMMARY cases=7 tool_pass=7 before_pass=3`, EXIT 0; the r87 12-row counter on the same tool reads `SUMMARY rows=12 mismatches=0 errors=0`, EXIT 0 (`records/c2-k4-regression.txt`) | `python3 -B tests/fixtures/r88-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-88/controls/c2-before-tool.py --work WORK` | `01a2fa559a0d900e28b4b3dda8a504ca935b584c` (tool + after/regression receipts) |

No owned axis score changed (calibration 7, coverage 8, operability 8 — the lane still has no reproducible 0–10
mapping); both rows carry the verdict, the counting command and the measured commit instead. The C1 counter's bytes
are unchanged from r87 (only the population, mutants and harness changed); the `_capture_ok` `len(want) <= len(have)`
arm is a belt by measurement (m19 survives both sets), not a row, and the four clauses the r87 wave named as
reachable-and-unrowed with other spellings (p2 basename granularity, p3 the punctuation lookahead, p7 `_regular`'s
symlink leg, p8 `token_ok`'s hyphen marker) stay carried.

### Round 88 capability rows

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| a ledger-level refusal bound as a population row | bind a clause that lives in the ledger reader (a duplicate id) by adding a row type that builds the duplicate-ledger input and parses the counter's own `LEDGER-REFUSED` line, instead of editing the counter | `python3 -B census/round-88/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py --work WORK --only r87,r88 --expect-killed 22` → `m17-duplicate-id killed=yes` on r88 and `killed=no` on r87 (`records/c1-after.txt`, control `controls/c1-before.txt`) | r88 |
| a delegated failure channel framed, escaped and bounded in one place | ship a child's raw stderr base64-framed and render it through the parent's single escaping rule, so the detail is one physical line and a long exception keeps both its type name and its message | `python3 -B tests/fixtures/r88-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-88/controls/c2-before-tool.py --work WORK` → `cases=7 tool_pass=7 before_pass=3` (`records/c2-after.txt`; before arm `tool_pass=3`) | r88 |

### Round 89 measurements (2026-11-08; lane base `a2cef94a`; instruments P `c9329534`, freeze F `d8bc7484`, harness fix `a3c7cb1f`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 four F1–F4 bindings (NF6h/NF6i/LD1b/LD2) | calibration 7 | `controls/c1-before.txt` (same battery, same sixteen mutants, the r88 53-row population) `m18b/m17b/m17c/m18d killed=no`, `SUMMARY mutants=16 sets=r88 pristine_r88=ok killed_r88=12 killed_total=12`, EXIT 0 | `records/c1-after.txt` `ARM pristine pop=r88 rows=53 mismatches=0 errors=0 exit=0`, `ARM pristine pop=r89 rows=57 mismatches=0 errors=0 exit=0`, `m17c-no-malformed killed=no` on r89, `SUMMARY mutants=16 sets=r88,r89 pristine_r88=ok pristine_r89=ok killed_r88=12 killed_r89=15 killed_total=27`, battery EXIT 1 | `python3 -B census/round-89/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py --work WORK --only r88,r89 --expect-killed 28` | `755a46cbdf0525d2bded60f211d4483c0903bdfe` |
| C2 FLAGFAIL injective decode + raw-first bound | operability 8 | `controls/c2-before.txt` on the r88 tool bytes `4042218f…` (both arms) `SUMMARY cases=10 tool_pass=8 before_pass=8`, KFF6/KFF8 fail, EXIT 1 | `records/c2-after.txt` on the filed tool sha256 `f6fce6d1…` `SUMMARY cases=10 tool_pass=10 before_pass=8`, EXIT 0; r87 12-row counter `rows=12 mismatches=0 errors=0` (`S89ExecC2` §2) | `python3 -B tests/fixtures/r89-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-89/controls/c2-before-tool.py --work WORK` | `755a46cbdf0525d2bded60f211d4483c0903bdfe` |

C1's frozen target (**16/28/EXIT 0**) was **not met**: three of its four bindings verify (`NF6h` kills `m18b`,
`LD1b` kills `m17b`, `NF6i` kills `m18d`), and the fourth (`LD2` for `m17c`) is falsified by the round's own
artifacts — LD2's appended `P02` is already in the frozen r77 ledger, so `m17c` refuses it on the duplicate leg
and survives (`S89MutCounter` F1, `S89Sentinel` F-1, `S89Reviewer` §1, `S89Simplifier` F1). The narrowed true
sentence, the measured binding row `LD2b` (append `ZZ9\tABSENT`) and the carry list are in `plans/round-89.md`
A1; the four new mutants deliver three kills, not four. C2's enumerated kill rule passes (10/10/8, EXIT 0) but
its headline "injective on the bytes" is narrowed: raw `0x85` and the UTF-8 NEL render identically, and the
truncated raw window is 202 bytes, not 200 (`plans/round-89.md` A2, `S89ExecC2` §6, `S89Scribe` F1). No owned
axis score changed (calibration 7, coverage 8, operability 8 — the lane still has no reproducible 0–10 mapping);
C1 carries the falsification verdict and C2 the kill-rule pass with a narrowed headline.

### Round 89 capability rows

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| SUPERSEDED r90 — a malformed-row binding whose id is absent from the ledger (measured, not landed; the landed r90 row is under `### Round 90 capability rows`) | bind the `_ledger` `len(r) < 3` guard by appending a 2-column row under a NEW id (`ZZ9`), so the guard is the only leg that can refuse it | `python3 -B .ufo/waves/round-89/w1/S89Sentinel/probe_ld1.py --work WORK` (ZZ9 control: pristine marker rc 1, `m17c` IndexError) + `S89MutCounter.md` F1 | r89 (design) |
| a raw-first excerpt that keeps the type name on control-heavy input | bound the raw bytes before escaping so 25 leading control bytes no longer consume the head | `python3 -B tests/fixtures/r89-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-89/controls/c2-before-tool.py --work WORK` → KFF8 pass, tool_pass=10 (`records/c2-after.txt`; before arm KFF8 fail) | r89 |

### Planned (r89)

- C1 (calibration): the four carried single-spelling survivors (p2 basename granularity, p3 the punctuation
  lookahead, p7 `_regular`'s symlink leg, p8 `token_ok`'s hyphen marker), the `_whole` after-byte lookahead's other
  spelling, and the quarantine intro-blob digest row; each candidate mutant is scored before its row is added (Q162).
- C2 (operability): the wave residuals the r88 seats leave open (S88ExecC2's attack cases, S88Sentinel's probes,
  S88Simplifier's deletion patches) plus the r85/r86 C2 carry list.
- Carried: the r85/r86 C2 list (pid-reuse row, parent-before-child, termign-fork/p5-late-term, strace-robust
  settle), `_regular` pathspec framing, the quarantine intro-blob digest row, the r79 gate re-measurement, check-4
  300 s backstop, r76 K03/K04, the r17 240 s runners, the inherited K3 tally row (r86 A4).

### Planned (r90, as filed in r89 — historical)

- C1 (calibration): `LD2b` (append `ZZ9\tABSENT`) binds `m17c`; `LD1c` (same-class duplicate) and `LD1d` (identical
  duplicate) bind the class-conflict readers; `NF6i2` binds the other occurrence order; `NF6j` binds the six
  remaining PATHCH predecessors.
- C2 (operability): spell U+0085 as `\u0085` in `_escape_text` (the 0x85/NEL collision) or add a KFF9 row;
  delete the dead `_one_line` (zero-risk, S89Simplifier #5); the forged-`CLEAN` fail-open (S88Sentinel F3)
  stays carried.
- Carried: p2 basename granularity, p3 the punctuation lookahead, p7 `_regular`'s symlink leg, p8 `token_ok`'s
  hyphen marker, the `fleet:` symlink leg, the battery `--only`/`--expect-killed` stale defaults.

### Round 90 measurements (2026-11-08; lane base `bd760432df2cc3ba6c5f1ccc540b050fe2ac09e2`; instruments P1 `1952c1c7`, P2 `e2a11c73`, freeze F `fd25bfc5`, C2 repair `4cb3a06f`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 the last unrowed clause of the r89 mutant set gets its row | calibration 7 (no reproducible 0–10 mapping; verdict calibration improved) | `census/round-90/controls/c1-before-r89-population.txt` (the same battery and 16 mutants on the r89 57-row population alone): `SUMMARY mutants=16 sets=r89 pristine_r89=ok killed_r89=15 killed_total=15`, `m17c-no-malformed pop=r89 killed=no`, EXIT 0 — no work reaches 16/31 | `census/round-90/records/c1-after.txt`: both pristine arms green (`pop=r89 rows=57`, `pop=r90 rows=58`, 0 mismatches), `m17c-no-malformed pop=r89 killed=no … pop=r90 killed=yes`, `SUMMARY … killed_r89=15 killed_r90=16 killed_total=31`, EXIT 0 | `python3 -B census/round-90/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py --work WORK --only r89,r90 --expect-killed 31` | `census/round-90/records/c1-after.txt`; row `LD2b` in `census/round-90/c1-false-rows.tsv` (58 rows, sha `d64d7695…`); measured at the C1 after run on F `fd25bfc5`, filed at the r90 round commit |
| C2 the byte/character pair gets distinct spellings and the dead helper is deleted | operability 8 (no reproducible 0–10 mapping; verdict operability improved) | `census/round-90/records/prefreeze-c2-control.txt` (the r89 tool bytes as BOTH arms): `SUMMARY cases=12 tool_pass=10 before_pass=10`, KFF9/KFF10 fail, EXIT 1 | `census/round-90/records/c2-after.txt` on the filed tool `d095b52f…`: `SUMMARY cases=12 tool_pass=12 before_pass=10`, EXIT 0; the r87 12-row K4 counter `rows=12 mismatches=0 errors=0`, EXIT 0; `grep -c 'def _one_line('` = 0 | `python3 -B tests/fixtures/r90-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-90/controls/c2-before-tool.py --work WORK` | `census/round-90/records/c2-after.txt`, `prefreeze-c2-k4-regression.txt`; tool commit `4cb3a06f`; filed at the r90 round commit |

No owned axis score changed (calibration 7, coverage 8, operability 8 — the lane still has no reproducible 0–10
mapping): both rows carry the verdict, the counting command and the measured commit instead. The wave narrowed four
C2 sentences before filing and one C1 evidence sentence (`plans/round-90.md` A1, A4, A5): the fixture's substring
counts do not bind the word "injective" (a doubled-backslash mutant survives 12/12, S90Sentinel H1); a window cut
inside U+0085's encoding renders the surviving byte `\x85` (S90Reviewer2); the "one physical line" clause is not
enforced; the deletion is measured by grep+load, not by the fixture; and the battery does not print its own hash.
The C2 tool wording stands (probe6 brute force: zero collisions among single characters and 2-char strings); what
was narrowed is the instrument's certifying power. The r89 capability row "a malformed-row binding whose id is
absent from the ledger (measured, not landed)" is superseded by the landed r90 row below. The L1 held the planner
seat (validator-frozen); the wave carries 3 executors and no planner seat, recorded here per the r89 spot-check's
role-split defect.

### Round 90 capability rows

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| a malformed-ledger guard bound by an absent-id population row | bind the `_ledger` `len(r) < 3` guard through a 2-column row under an id the frozen ledger does not know (`ZZ9<TAB>ABSENT`), so the duplicate leg cannot mask the malformed leg; the sole surviving clause of a 16-member mutant set is killed and the row is shown to bind the dropped-guard spelling only | `python3 -B census/round-90/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py --work WORK --only r89,r90 --expect-killed 31` → `killed_r89=15 killed_r90=16 killed_total=31` (`census/round-90/records/c1-after.txt`; control `controls/c1-before-r89-population.txt` red on m17c) | r90 |
| a byte/character spelling pair measured through the public path with a symmetric pair check | spell the character U+0085 `\u0085` and the raw byte `0x85` `\x85`, and score the pair on BOTH fixture arms so a repair that merely swaps spellings still fails | `python3 -B tests/fixtures/r90-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-90/controls/c2-before-tool.py --work WORK` → `cases=12 tool_pass=12 before_pass=10` (`census/round-90/records/c2-after.txt`; control 10/10 red) | r90 |

### Planned (r91)

- C1 (calibration): the Q162 probes the r90 wave measured alive on all eight pinned populations — `ld1c-class-keyed`,
  `ld1d-conflict-keyed` (one identical-duplicate row binds both spellings), `nf6i2-last-occurrence` (a fixture R13
  line with the whole occurrence FIRST), `nf6j-pathch-narrow` (a declaration with the token after each of `. _ @ + ~ -`);
  plus the 1-column ledger row and the `!=3` grammar (S90MutCounter §3–§5).
- C2 (operability): the missing doubled-spelling conjuncts in KFF9/KFF10 (`count(bs*2+"u0085")==0`,
  `count(bs*2+"x85")==0`), a boundary row for the raw-window cut (A4), a "one physical line" row, a fixture row for
  the `_one_line` deletion (A5c), the battery self-pin (A5b), the forged-`CLEAN` fail-open (S88Sentinel F3) and the
  K4-record-level arms H2a–H2c (FORGED/REFUSED/no-verdict) as a readability debt.
- Carried: p2 basename granularity, p3 the punctuation lookahead, p7 `_regular`'s symlink leg, p8 `token_ok`'s
  hyphen marker, the `fleet:` symlink leg, the battery `--only`/`--expect-killed` stale defaults, the r85/r86 C2
  list (pid-reuse row, parent-before-child, termign-fork/p5-late-term, strace-robust settle), `_regular` pathspec
  framing, the quarantine intro-blob digest row, the r79 gate re-measurement, check-4 300 s backstop, r76 K03/K04,
  the r17 240 s runners.

### Round 91 measurements (2026-11-08; lane base `681f6c72b242d410d0e8654efadb2a1553fb111d`; instruments P1 `7fb865d8`, P2 `d287d3de`, freeze F `a703bcb7`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 five rows bind the six surviving clauses (LD1c identical duplicate, LD3 one column, LD4 ledger-resolve, NF6i2 whole-first, NF6j PATHCH predecessors) | calibration 7 (no reproducible 0–10 mapping; verdict calibration improved) | `census/round-91/controls/c1-control-r90.txt` (the 22-member set on the r90 58-row population): `SUMMARY mutants=22 sets=r90 pristine_r90=ok killed_r90=16 killed_total=16`, the six new members each `killed=no`, EXIT 0 — no work reaches 38 | `census/round-91/records/c1-after.txt`: both pristine arms green (`pop=r90 rows=58`, `pop=r91 rows=63`, 0 mismatches), the six new members `killed=no` on r90 and `killed=yes` on r91, `SUMMARY mutants=22 sets=r90,r91 pristine_r90=ok pristine_r91=ok killed_r90=16 killed_r91=22 killed_total=38`, EXIT 0 | `python3 -B census/round-91/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py --mutants census/round-91/c1-mutants.json --work WORK --only r90,r91 --expect-killed 38` (control `--only r90 --expect-killed 16`) | `census/round-91/records/c1-after.txt`, `controls/c1-control-r90.txt`, measured at `28368806c17d8af4a6b9e7930df3bcd786a3df47` |
| C2 the excerpt cut lands on UTF-8 sequence boundaries (valid payloads) and the r91 fixture binds the four claimed clauses; residuals named | operability 8 (no reproducible 0–10 mapping; verdict operability improved) | the r90 tool on the r91 fixture: `SUMMARY cases=15 tool_pass=14 before_pass=14`, KFF11 fails on both arms, EXIT 1; the three variants on the r90 fixture: `SUMMARY variants=3 fixture=r90 detected=0` (each passes 12/12); `census/round-91/controls/c2-variants-r90-control.txt` | `census/round-91/records/c2-after.txt` on the filed tool `21e5c740…`: `SUMMARY cases=15 tool_pass=15 before_pass=14`, EXIT 0; `census/round-91/records/c2-variants-r91.txt`: `SUMMARY variants=3 fixture=r91 detected=3`, EXIT 0; `census/round-91/records/c2-k4-regression.txt`: `SUMMARY rows=12 mismatches=0 errors=0`, EXIT 0 | `python3 -B tests/fixtures/r91-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-91/controls/c2-before-tool.py --work WORK`; `python3 -B census/round-91/c2-variant-probe.py --fixture r91 --work WORK` (control `--fixture r90`); `python3 -B census/round-87/c2-k4-counter.py --tool tools/souji-record-agreement.py --work WORK` | `census/round-91/records/c2-after.txt`, `c2-variants-r91.txt`, `c2-k4-regression.txt`, measured at `28368806c17d8af4a6b9e7930df3bcd786a3df47` |

No owned axis score changed (calibration 7, coverage 8, operability 8 — the lane still has no reproducible 0–10
mapping): both rows carry the verdict, the counting command and the measured commit instead. The wave narrowed
STATED LIMITS (iii) of C1 and two C2 sentences before filing (`plans/round-91.md` A1/A2): the LD4 base run is
all-resolved (35/35, rc 0), so its missing rc assertion was a choice; `_cut_tail` over-advances on a
truncated/invalid lead before the tail cut and can re-create the byte/character collision on such payloads (the
valid-payload rule stands, 1137-row sweep, 0 splits); and KFF13 enforces the literal substrings only (a spaced
`def _one_line (` and call pass 15/15; a docstring mention false-fails). The C1 predicate and both C2 predicate
numbers re-derive exactly on committed bytes.

### Round 91 capability rows

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| a six-clause population binding whose five rows are each load-bearing | bind both duplicate-keyed spellings (one identical-duplicate row), the one-column ledger shape, the 4-column width acceptance, the occurrence order and the six PATHCH predecessors, with each row shown to be the killer of at least one surviving mutant (a row deletion lets its mutant survive) | `python3 -B census/round-91/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py --mutants census/round-91/c1-mutants.json --work WORK --only r90,r91 --expect-killed 38` → `killed_r90=16 killed_r91=22 killed_total=38` (`census/round-91/records/c1-after.txt`; control `controls/c1-control-r90.txt`; row-deletion probe `R91ExecC1Battery.md` § Kill-power) | r91 |
| a UTF-8 sequence-boundary excerpt cut with a before/after cell pair | place the excerpt's head and tail cuts on UTF-8 sequence boundaries, so a valid U+0085 straddling the tail cut renders neither spelling while a lone raw 0x85 keeps its `\xNN`, measured on both the repaired and the r90 tool | `python3 -B tests/fixtures/r91-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-91/controls/c2-before-tool.py --work WORK` → `cases=15 tool_pass=15 before_pass=14` (`records/c2-after.txt`); the variant probe → `detected=3`/`detected=0` | r91 |

### Planned (r92)

- C1 (calibration): LD4 asserts `rc=0` as well (A1); the battery's `--expect-killed` split grip and the `new`-string
  absence check (R91ReviewerC1 §8.1–§8.3); the alternative-edit survivor search the r91 mutation-tester never ran
  (R91MutCounter died, `.ufo/waves/round-91/w1/dead-seats/R91MutCounter.json`);
  the r91 population header names the r90/r91 rows (R91Connector F3).
- C2 (operability): `_cut_tail` validates the whole declared sequence before moving the cut, the C0/C1/F5-F7 range
  checks, head-cut and invalid-lead fixture rows, the `_cut_head` annotation (A2, R91ExecC2Tool, R91Scribe,
  R91Connector F1); KFF13 via `ast` with both directions as cases (R91ReviewerC2, R91ExecC2Fixture).
- Carried: p2 basename granularity, p3 the punctuation lookahead, p7 `_regular`'s symlink leg, p8 `token_ok`'s
  hyphen marker, the `fleet:` symlink leg, the battery `--only`/`--expect-killed` stale defaults, the r85/r86 C2
  list (pid-reuse row, parent-before-child, termign-fork/p5-late-term, strace-robust settle), `_regular` pathspec
  framing, the quarantine intro-blob digest row, the r79 gate re-measurement, check-4 300 s backstop, r76 K03/K04,
  the r17 240 s runners.

### Round 92 measurements (2026-11-08/09; lane base `5339b2ac79f81aa446f6a2cd4700321cf4982fd3`; instruments P1 `44d45b44`, P2 `1d015a2d`, freeze F `e8d31f06`, after receipts `e5059168`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 one exit-polarity row (LD4r = LD4 + expect_rc 0) makes the harness exit 1 (row mismatch, no crash) on 47 of the 124 single-token survivors of the frozen r87 counter (narrowed A3: the edits, not their clauses) | calibration 7 (no reproducible 0–10 mapping; verdict calibration improved) | `census/round-92/controls/c1-control-r91-population.txt` (the 47 targets on the r91 63-row population, r92 harness): `SEARCH-SUMMARY generated=47 ambiguous=0 uncompiled=0 hung=0 scored=47 killed=0 survived=47`, EXIT 0 — no work reaches 47; census `records/c1-search-r91-full.txt`: `generated=270 ambiguous=9 uncompiled=0 hung=1 scored=260 killed=136 survived=124` | `census/round-92/records/c1-after.txt`: `SEARCH-SUMMARY generated=47 ambiguous=0 uncompiled=0 hung=0 scored=47 killed=47 survived=0`, EXIT 0; `records/c1-pristine-after.txt`: `SUMMARY rows=64 mismatches=0 accepted=0 refused_true=0 errors=0`, LD4r `rc=0 match=yes`, EXIT 0 | `python3 -B census/round-92/c1-survivor-search.py --counter census/round-87/c1-pointer-counter.py --harness census/round-92/c1-false-row-harness.py --population census/round-92/c1-false-rows.tsv --lane . --fleet-root /home/vgpnk/Projects/shokunin --work WORK --jobs 8 --ids census/round-92/c1-targets.json` | `e5059168` (instruments `44d45b44`/`1d015a2d`, F `e8d31f06`) |
| C2 the excerpt cut moves only across a well-formed UTF-8 sequence (Table 3-7, S355); the fixture certifies the A/B pair, the overlong and head cases and a 29,700-payload prefix/suffix sweep (narrowed A1: over-moving forgeries pass) | operability 8 (no reproducible 0–10 mapping; verdict operability improved) | `census/round-92/controls/c2-control-r91-tool-both-arms.txt` (the r91 tool as both arms): `SUMMARY cases=20 tool_pass=16 before_pass=16`, KFF14/15/16/18 red, EXIT 1 | `census/round-92/records/c2-after.txt` on the filed tool `fc0e35c2…`: `SUMMARY cases=20 tool_pass=20 before_pass=16`, EXIT 0; `records/c2-forgery-after.txt`: `FORGERY-SUMMARY forgeries=5 rejected=5 positive=pass`, EXIT 0; `records/c2-k4-regression.txt`: `SUMMARY rows=12 mismatches=0 errors=0`, EXIT 0 | `python3 -B tests/fixtures/r92-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work WORK` | `e5059168` |

No owned axis score changed (calibration 7, coverage 8, operability 8 — the lane still has no reproducible 0–10
mapping): both rows carry the verdict, the counting command and the measured commit instead. The wave narrowed one C2
sentence before filing (`plans/round-92.md` A1): three one-edit forgeries that move a cut too far (surrogatepass, a
multi-character span, a forward head move) pass the frozen fixture 20/20, so "moves a cut only across ONE well-formed
sequence" rests on source reading and a 200,000-payload wave sweep, not on the frozen predicate. C1's "kills" is
narrowed to the 47 listed edits (A3: an alternative edit of line 552 survives; the kill rule cannot tell a crash from a
verdict change, and none of the 47 is a crash); R92ExecC1Cause attributes 14/14 sampled kills to LD4r alone (7 exit-polarity, 7 resolution). The L1 held
the planner seat (validator-frozen); the planning data-walk rode R92Connector.

### Round 92 capability rows

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| a bounded single-token mutation census of a frozen counter | enumerate every comparison flip, and/or swap, `not` deletion, True/False and 0/1 swap of a counter (plus hand edits), score each once on a pinned population with per-mutant cleanup and a process-group timeout, and print killed/survived/ambiguous/hung per mutant, so unbound clauses are found by search instead of by hand | `python3 -B census/round-92/c1-survivor-search.py --counter census/round-87/c1-pointer-counter.py --harness census/round-91/c1-false-row-harness.py --population census/round-91/c1-false-rows.tsv --lane . --fleet-root /home/vgpnk/Projects/shokunin --work WORK --jobs 10 --timeout 240` → `generated=270 ambiguous=9 uncompiled=0 hung=1 scored=260 killed=136 survived=124` (`census/round-92/records/c1-search-r91-full.txt`); cleanup able to fail (`records/m1-cleanup-fail-check.txt`: 44 KB vs 369,072 KB without it) | r92 |
| a well-formed-sequence excerpt cut | move the K4 excerpt's head/tail cut only across a single strictly-decodable UTF-8 sequence (every Unicode Table 3-7 row), so an ill-formed lead never absorbs a later well-formed sequence and the excerpt's head/tail stay a prefix/suffix of the whole rendering | `python3 -B tests/fixtures/r92-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work WORK` → `cases=20 tool_pass=20 before_pass=16` (`records/c2-after.txt`); forgery probe 5/5; wave sweep 0/200,000 (`.ufo/waves/round-92/w1/R92ExecC2Sweep.md`) | r92 |

### Planned (r93)

- C1 (calibration): classify or bind the 77 residual survivors (`census/round-92/records/c1-residual-survivors.json`)
  and name the equivalent mutants; bind the forge return (stated limit ii) through a separate exit-expectation
  channel, not a row; make exit polarity a required field of resolving rows (R92Connector §6); search robustness:
  try/finally cleanup on kill, SIGINT cancel, the bare-`/tmp` guard (R92Sentinel M1/L1/L2).
- C2 (operability): a maximality case so a cut that moves too far goes red (R92MutC2 C/D/E, A1); an ill-formed lead
  before the HEAD cut (R92Connector §3); retire or re-point the r91 variant tools (R92Connector §2 C).
- Carried: p2 basename granularity, p3 the punctuation lookahead, p7 `_regular`'s symlink leg, p8 `token_ok`'s
  hyphen marker, the `fleet:` symlink leg, the battery `--only`/`--expect-killed` stale defaults, the r85/r86 C2
  list (pid-reuse row, parent-before-child, termign-fork/p5-late-term, strace-robust settle), `_regular` pathspec
  framing, the quarantine intro-blob digest row, the r79 gate re-measurement, check-4 300 s backstop, r76 K03/K04,
  the r17 240 s runners, the r85-r87 K4 counters' print-only `rc=`.

### Round 93 measurements (2026-11-09; lane base `91c9bcb1041b18be154ca466ac3c047ac7862fe1`; instruments P1 `2c82d362`, controls P2 `0d6442cc`, freeze F `9a4ab88f`, after receipts A `7bdb96b7`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 two ledger-edit rows (LD5 `ledger-drop`, LD6 `ledger-trim`) make the harness exit 1 with a row mismatch on two counter edits that survive every r92 row: `h-ok-admits-one` and `a491c22-<-to-<=` (narrowed A1-A3: no r92 row asserts an outcome either edit changes; the edits, not their clauses; an uncaught counter exception would also score killed — both kills read `got=UNRESOLVED` on their own target row) | calibration 7 (no reproducible 0–10 mapping; verdict calibration improved) | `census/round-93/controls/c1-control-r92-population.txt` (r92 population, r93 harness and search): `SEARCH-SUMMARY generated=2 ambiguous=0 uncompiled=0 hung=0 scored=2 errored=0 killed=0 survived=2`, EXIT 0 | `census/round-93/records/c1-after.txt`: `… scored=2 errored=0 killed=2 survived=0`, EXIT 0; `records/c1-pristine-after.txt`: `SUMMARY rows=66 mismatches=0 accepted=0 refused_true=0 errors=0`, LD5 `rc=1 match=yes`, LD6 `rc=0 match=yes`, EXIT 0 | `python3 -B census/round-93/c1-survivor-search.py --counter census/round-87/c1-pointer-counter.py --harness census/round-93/c1-false-row-harness.py --population <POP> --lane . --fleet-root /home/vgpnk/Projects/shokunin --work WORK --jobs 2 --ids census/round-93/c1-targets.json` | `7bdb96b74401d75b459d026c079a3e6e7bb209ff` |
| C2 the K4 excerpt's cut-POSITION edge class: KFF19 (exact equality with a reference cut written from the WHATWG UTF-8 decoder, S356, on 14,586 boundary-class payloads) and KFF20 (overlong across the head cut) reject the three one-edit forgeries the r92 fixture passed 20/20 (narrowed A5: KFF18 was the r92 cut-position case; the reference is independent of the tool's code and Python's codec, not of the excerpt constants) | coverage 8 (edge class moved; 8/8 is a count over a chosen forgery set, not a fraction — no score change, A6) | `census/round-93/controls/c2-control-r92-fixture-probe.txt`: `FORGERY-SUMMARY forgeries=8 rejected=5 positive=pass` (F5/F6/F7 20/20), EXIT 1 | `census/round-93/records/c2-forgery-after.txt`: `FORGERY-SUMMARY forgeries=8 rejected=8 positive=pass`, EXIT 0; `records/c2-after.txt`: `SUMMARY cases=22 tool_pass=22 before_pass=16`, EXIT 0; K4 `records/c2-k4-regression.txt` `rows=12 mismatches=0 errors=0` | `python3 -B census/round-93/c2-forgery-probe.py --fixture <FIXTURE> --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work WORK` | `7bdb96b74401d75b459d026c079a3e6e7bb209ff` |

No owned axis score changed (calibration 7, coverage 8, operability 8 — the lane still has no reproducible 0–10
mapping). The wave narrowed four sentences before filing (`plans/round-93.md` A1, A3, A5; A2/A4/A6 are readings and a
stated limit): see `.ufo/waves/round-93/claim-falsification.tsv`. Reported, not claimed: the 78-id residual set
(the 77 r92 residual survivors, a491c22 among them, plus h-ok-admits-one; `census/round-93/c1-residual-plus-e1.json`) reads `killed=0
survived=78` on the r92 population and `killed=2 survived=76` on r93 — only the two targets differ
(`.ufo/waves/round-93/w1/R93ExecResidual/receipt-r92.txt`, `receipt-r93.txt`).

### Round 93 capability rows

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| ledger-edit false rows | build a scratch copy of a population's frozen ledger with ONE item's own row removed (`ledger-drop`) or cut to three columns (`ledger-trim`), run the counter on it and assert that item's status and the exit code, so a success test's equality and a width guard's lower edge are asserted | `python3 -B census/round-93/c1-false-row-harness.py --counter census/round-87/c1-pointer-counter.py --lane . --fleet-root /home/vgpnk/Projects/shokunin --work WORK --population census/round-93/c1-false-rows.tsv` → `rows=66 mismatches=0`, LD5 `rc=1 match=yes`, LD6 `rc=0 match=yes` (`census/round-93/records/c1-pristine-after.txt`) | r93 |
| exact-position excerpt check | compare the K4 excerpt with the cell from a reference cut written from the WHATWG UTF-8 decoder (no codec call) on a 14,586-payload boundary-class sweep, so a cut that lands in the wrong place is refused even when it stays prefix/suffix-faithful | `python3 -B tests/fixtures/r93-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work WORK` → `cases=22 tool_pass=22 before_pass=16` (`census/round-93/records/c2-after.txt`); forgery probe 8/8 vs 5/8 on the r92 fixture | r93 |
| interruptible survivor search | stop a running mutation search on SIGINT/SIGTERM with exit 130, killing every live harness process group and deleting every per-mutant work tree | `.ufo/waves/round-93/w1/R93Labrat.md` (4/4 arms: exit 130 in ~0.5 s, 0 `m*/w` trees, no live process; SIGKILL still strands) | r93 |

### Planned (r94)

- C1 (calibration): kill rule scores a `got=-` row or a counter traceback as `errored` (A3, Q170) and re-scores the
  r93 targets under it; bind the clauses rather than two spellings — m5/m6 (`len(pop) - len(unknown)` forms) and g2
  (`len(r) not in (3, 4)`) survive (R93MutC1 R1/R2 row shapes); assert LD5's `SUMMARY unresolved=1`; make the harness
  reproducible from committed bytes (two gitignored lane-disk inputs, A4).
- C2 (coverage): KFF19 at a second payload length and a non-`a` filler (h_filler_a survives); catch in-process
  exceptions in the fixture's scorer (R93Sentinel M2); KFF20 mirrors for `ED A0 80` / `F4 90 80 80` across the head
  cut; retire or re-point the r91 variant tools.
- Carried: the forge-return channel (r92 limit ii), the 76 residual survivors' classification, p2 basename
  granularity, p3 the punctuation lookahead, p7 `_regular`'s symlink leg, p8 `token_ok`'s hyphen marker, the `fleet:`
  symlink leg, the battery `--only`/`--expect-killed` stale defaults, the r85/r86 C2 list, `_regular` pathspec
  framing, the quarantine intro-blob digest row, the r79 gate re-measurement, check-4 300 s backstop, r76 K03/K04,
  the r17 240 s runners, the r85-r87 K4 counters' print-only `rc=`.

### Round 94 measurements (2026-11-09; lane base `eddb1be6c34c2e0bef8c1e8ae6ea2f4b381c5536`; instruments P1 `24cd67b0`, controls P2 `39d4163a`, freeze F `4ad74b9d`, after receipts A `b065b7f0`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 crash fixtures the survivor search scores killed: the r93 rule scores a mutant whose counter raises an uncaught exception as killed; the r94 search (crash sentinel exit 70, S358; rule rc=70 → errored, S357) scores both crash fixtures `errored`, keeps the two r93 semantic kills killed and the survivor surviving | calibration 7 (no reproducible 0–10 mapping; verdict calibration improved) | `census/round-94/controls/c1-control-r93-rule.txt` (r93 rule, same five targets): `SEARCH-SUMMARY generated=5 ambiguous=0 uncompiled=0 hung=0 scored=5 errored=0 killed=4 survived=1`, both crash fixtures `killed=yes`, EXIT 0 — 2 mis-scored | `census/round-94/records/c1-after.txt`: `SEARCH-SUMMARY generated=5 ambiguous=0 uncompiled=0 hung=0 scored=5 errored=2 killed=2 survived=1`, h-crash-late/h-crash-index `killed=errored`, EXIT 0 — 0 mis-scored; forgeries FA/FB refused 2/2 (`controls/c1-forgery-controls.txt`) | `python3 -B census/round-94/c1-survivor-search.py --counter census/round-87/c1-pointer-counter.py --harness census/round-93/c1-false-row-harness.py --population census/round-93/c1-false-rows.tsv --lane . --fleet-root /home/vgpnk/Projects/shokunin --work WORK --jobs 5 --ids census/round-94/c1-targets.json` | `b065b7f036b32aa2114f3dedd9d0ec88b43dfcb2` |
| C2 forgery-probe arms whose exit code matches its meaning: the r93 probe exits 1 ("a forgery survived") on 7 of 8 setup arms; the r94 probe runs on an existing empty `--work`, refuses the other setup arms with exit 2 + `C2-FORGERY-FATAL:`, and keeps verdict exits 0/1 | operability 8 (no reproducible 0–10 mapping; verdict operability improved) | `census/round-94/controls/c2-control-r93-probe.txt`: `ARMS-SUMMARY arms=10 conform=3`, EXIT 1 | `census/round-94/records/c2-after.txt`: `ARMS-SUMMARY arms=10 conform=10`, EXIT 0; forgeries GA/GB conform=9 each, refused 2/2 (`controls/c2-forgery-controls.txt`) | `python3 -B census/round-94/c2-setup-arms.py --probe census/round-94/c2-forgery-probe.py --fixture-pass tests/fixtures/r93-k4-flagfail.py --fixture-fail tests/fixtures/r92-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work WORK` | `b065b7f036b32aa2114f3dedd9d0ec88b43dfcb2` |

No owned axis score changed (calibration 7, coverage 8, operability 8 — the lane still has no reproducible 0–10
mapping): both rows carry the verdict, the counting command and the measured commit. The wave narrowed sentences
before filing (`plans/round-94.md` A1, A2, A4; A3/A5 are readings of predicate strength): C1's stated limit (ii)
omitted SystemExit and atexit/`__del__` exceptions (S359 added); the r94 probe docstring's "every setup failure exits
2" is false for a non-UTF-8 tool, a file-parent `--work` and a mid-run write failure (claim scoped to the ten arms
holds); see `.ufo/waves/round-94/claim-falsification.tsv`. Reported, not claimed: the full r93-population census
(R94ExecCensus) reads `killed=167` under the r93 rule and `killed=139 errored=48` under r94 — 28 crash kills, all with
`rc=70` rows; survivors identical. The L1 held the planner seat (validator-frozen); the planning data-walk rode
R94Connector.

### Round 94 capability rows

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| crash-aware mutation verdicts | score a mutant whose counter raises an uncaught exception as `errored` instead of killed: every harness run inherits a `sitecustomize` excepthook that exits 70, the search checks the hook fires in a child before scoring, and any `rc=70` row makes the verdict `errored` | `python3 -B census/round-94/c1-survivor-search.py … --ids census/round-94/c1-targets.json` → `errored=2 killed=2 survived=1` (`census/round-94/records/c1-after.txt`); the r93 rule on the same ids `errored=0 killed=4` | r94 |
| setup-vs-verdict exit discipline for the forgery probe, with an arms counter | refuse an unusable `--work`, a missing fixture/tool/before and a fixture that prints no summary with exit 2 and a named FATAL line, run on an existing empty `--work`, and keep exit 1 for "a forgery survived"; a ten-arm counter scores any probe on this contract | `python3 -B census/round-94/c2-setup-arms.py --probe census/round-94/c2-forgery-probe.py …` → `conform=10` (`census/round-94/records/c2-after.txt`); r93 probe `conform=3` | r94 |

### Planned (r95)

- C1 (calibration): SystemExit, atexit and `__del__` crash fixtures (today scored `yes`/`no`: R94ScoutSources,
  R94Sentinel F1/F2); a harness-side crash target binding the exit-70 disjunct (R94MutC1 M2, R94Sentinel F3); a
  truthful precondition line (M8) and the `endswith(' match=no')` position (M6); bare `got=-` rows; carried: C1
  harness reproducibility from committed bytes (r93 routed 1), m5/m6/g2 clause shapes and LD5 `unresolved=1` (r93
  routed 3), the 76 residual survivors, the r84-r91 clause-battery docstring that calls a harness error a kill.
- C2 (operability/coverage): catch decode and write exceptions in the probe as exit 2; a fixture timeout (R94ReviewerC2
  T9, R94Sentinel F5); `--work` TOCTOU and `/tmp` itself (F7, F9); arms binding edit-once and the /tmp guard
  (R94MutC2 M10/M11); randomized arm names (R94Critic); the arms counter's own uncaught exceptions; KFF19 second
  length/filler, fixture scorer exceptions, KFF20 mirrors, the r91 variant tools (r93 routed 4).
- Carried: the forge-return channel (r92 limit ii), p2 basename granularity, p3 the punctuation lookahead, p7
  `_regular`'s symlink leg, p8 `token_ok`'s hyphen marker, the `fleet:` symlink leg, the battery `--only`/
  `--expect-killed` stale defaults, the r85/r86 C2 list, `_regular` pathspec framing, the quarantine intro-blob
  digest row, the r79 gate re-measurement, check-4 300 s backstop, r76 K03/K04, the r17 240 s runners, the r85-r87 K4
  counters' print-only `rc=`.

### Round 95 measurements (2026-11-09; lane base `93c3ef13a9eb9678483518562f3692124db714c2`; instruments P1 `d79bc3fe`, controls P2 `48c5efe9`, freeze F `59fd7be0`, after receipts A `dd520684`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 crash-channel fixtures the survivor search scores other than errored: the r94 sentinel replaces only `sys.excepthook`, so h-sysexit/h-osexit/h-sigkill read `killed=yes` and h-atexit/h-thread `killed=no`; the r95 search (exit 70 also on `sys.unraisablehook`, `threading.excepthook`, any `os._exit`, a SystemExit first raised in a main-script function via a `sys.monitoring` RAISE callback, S360-S362, S364; negative rc → errored, S363) scores all five `errored` and keeps the five r94 targets' verdicts | calibration 7 (no reproducible 0–10 mapping; verdict calibration improved) | `census/round-95/controls/c1-control-r94-rule.txt` (frozen r94 search, same ten targets): `SEARCH-SUMMARY generated=10 ambiguous=0 uncompiled=0 hung=0 scored=10 errored=2 killed=5 survived=3`, EXIT 0 — 5 mis-scored | `census/round-95/records/c1-after.txt`: check line `excepthook=70 sysexit=70 atexit=70 thread=70 osexit=70 declared=1 argparse=2`, `SEARCH-SUMMARY generated=10 ambiguous=0 uncompiled=0 hung=0 scored=10 errored=7 killed=2 survived=1`, EXIT 0 — 0 mis-scored; forgeries FA/FB/FC refused 3/3 (`controls/c1-forgery-controls.txt`) | `python3 -B census/round-95/c1-survivor-search.py --counter census/round-87/c1-pointer-counter.py --harness census/round-93/c1-false-row-harness.py --population census/round-93/c1-false-rows.tsv --lane . --fleet-root /home/vgpnk/Projects/shokunin --work WORK --jobs 5 --ids census/round-95/c1-targets.json`; mis-scored = `grep -cE '^SEARCH h-(sysexit\|atexit\|thread\|osexit\|sigkill) ' FILE` minus `grep -cE '^SEARCH h-(sysexit\|atexit\|thread\|osexit\|sigkill) .*killed=errored' FILE` | `dd5206842fcead3b1e7301d3dbaaec42b625dd54` |
| C2 forgery-probe arms whose exit code matches its meaning, of 16: the r94 probe exits 1 on a non-UTF-8 `--tool`/`--before` and a file-parent `--work` and never ends on a hanging fixture; the r95 probe refuses all four with exit 2 + `C2-FORGERY-FATAL:` and conforms on the twelve arms the r94 probe conforms on | operability 8 (no reproducible 0–10 mapping; verdict operability improved) | `census/round-95/controls/c2-control-r94-probe.txt`: `ARMS-SUMMARY arms=16 conform=12` (S9-S11 exit=1, S12 exit=hung), EXIT 1 | `census/round-95/records/c2-after.txt`: `ARMS-SUMMARY arms=16 conform=16`, EXIT 0; forgeries GA/GB/GC conform 15/14/15, refused 3/3 (`controls/c2-forgery-controls.txt`) | `python3 -B census/round-95/c2-setup-arms.py --probe census/round-95/c2-forgery-probe.py --fixture-pass tests/fixtures/r93-k4-flagfail.py --fixture-fail tests/fixtures/r92-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work WORK` | `dd5206842fcead3b1e7301d3dbaaec42b625dd54` |

No owned axis score changed (calibration 7, coverage 8, operability 8 — the lane still has no reproducible 0–10
mapping): both rows carry the verdict, the counting command and the measured commit. The wave narrowed sentences
before filing (`plans/round-95.md` A1-A3, A5, A6; A4 a scope limit; A7 this round's own rows): the SystemExit leg also
scores `sys.exit(...)` in `main` and a SystemExit caught at module level as errored (R95Labrat; declared-shape table
`census/round-95/records/declared-shapes.txt` `mismatched=6`); a finalizer raising after a SystemExit exit is not seen;
`os._exit(0)` reads 70 and the crash path can hang when the stderr lock is held; S13 does not isolate the /tmp guard;
an escaping grandchild hangs the probe past `--timeout`; see `.ufo/waves/round-95/claim-falsification.tsv`. Reported,
not claimed: the full generated population changes no verdict between the r94 and r95 searches (R95ExecCensus: 263
ids, killed 139, survived 76; errored 48 → 53 = the five new fixtures). The L1 held the planner seat
(validator-frozen); the planning data-walk rode R95Connector; the prereg's labrat seat ran as a reviewer (A0.2).

### Round 95 capability rows

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| five-channel crash sentinel with a per-channel precondition | score a mutant whose counter dies through SystemExit raised in a main-script function, an atexit/unraisable exception, a thread exception, `os._exit` or a signal as `errored`; the search refuses to score unless a check script exits 70 on each channel and keeps status 1 and 2 for two declared exits | `python3 -B census/round-95/c1-survivor-search.py … --ids census/round-95/c1-targets.json` → check line + `errored=7 killed=2 survived=1` (`census/round-95/records/c1-after.txt`); frozen r94 search `errored=2 killed=5 survived=3` | r95 |
| forgery-probe refusals for undecodable inputs, an uncreatable work dir and a hanging fixture, with a sixteen-arm counter | refuse a non-UTF-8 `--tool`/`--before`, a `--work` that cannot be created, a write failure after the checks, a fixture run past `--timeout` (process group killed) and any internal exception with exit 2 + a named FATAL line; the arms counter kills a hung arm at `--arm-timeout` and scores it | `python3 -B census/round-95/c2-setup-arms.py --probe census/round-95/c2-forgery-probe.py …` → `conform=16` (`census/round-95/records/c2-after.txt`); r94 probe `conform=12` | r95 |

### Planned (r96)

- C1 (calibration): decide the SystemExit leg on the terminating exception (EXCEPTION_HANDLED or a top-level record)
  and make the declared-shape table (`census/round-95/records/declared-shapes.txt`, Q172) a precondition with
  `mismatched=0`; a signal-safe crash path (`os.write(2, …)` + the real `os._exit(70)`, R95Sentinel F1); scope the
  hook to the counter and use ids 3-4 only (F3/F4); a CHECK that asserts each channel's `SOUJI-R95-CRASH` reason
  (R95MutC1 m02/m03); a finalization-time `__del__` fixture (A2); the harness-side crash target binding the harness
  exit-70 disjunct (r94 routed 2); setup refusals for the search's own `--counter`/`--ids` reads; carried: r93 routed 1
  (harness reproducibility from committed bytes), m5/m6/g2 clause shapes and LD5 `unresolved=1`, the 76 residual
  survivors, the r84-r91 clause-battery docstring that calls a harness error a kill.
- C2 (operability/coverage): arms that assert the FATAL reason text (S13, R95MutC2 PM9); reap escaped descendants and
  stop waiting on held pipes (R95ReviewerC2 `Q1-pipe-holder`, R95Sentinel F2); arms for a write failure after the
  checks, an internal exception, `--timeout 0` and the positive-control conjunct (PM3/PM5/PM6/PM7); `--work` TOCTOU;
  randomized arm names; per-run deadlines in the forgery runners and the c1-false-row-harness family; setup-refusal
  reads in the older probes and the counter (R95Connector §2); KFF19 second length/filler, fixture scorer exceptions,
  KFF20 mirrors, the r91 variant tools (r93 routed 4).
- Carried: the forge-return channel (r92 limit ii), p2 basename granularity, p3 the punctuation lookahead, p7
  `_regular`'s symlink leg, p8 `token_ok`'s hyphen marker, the `fleet:` symlink leg, the battery `--only`/
  `--expect-killed` stale defaults, the r85/r86 C2 list, `_regular` pathspec framing, the quarantine intro-blob digest
  row, the r79 gate re-measurement, check-4 300 s backstop, r76 K03/K04, the r17 240 s runners, the r85-r87 K4
  counters' print-only `rc=`.

### Round 96 measurements (2026-11-09; lane base `689d1c9570a5df2344e16a5916c49e24b46823ab`; instruments P1 `0656de3f`, controls P2 `4dd8a103`, freeze F `c1209623`, after receipts A = the r96 census/controls re-run, see the report)

| claim | axis | before | after | counting command | verdict |
|---|---|---|---|---|---|
| C1 SystemExit leg: a top-level-caught SystemExit scores declared (t1/t4) | calibration 7 (no 0–10 mapping; unchanged) | `census/round-96/controls/` r95-hook shape table `SHAPES-SUMMARY shapes=12 mismatched=2` (t1/t4 70) | r96 hook `SHAPES-SUMMARY shapes=12 mismatched=0` (`python3 -B census/round-96/declared-shapes.py --search census/round-96/c1-survivor-search.py --scripts census/round-96/shapes --work <empty>`) | as left; measured commit `0656de3f` | **harmed (trade).** The same frame-name clear turns two terminating module-level shapes from errored (r95 70) to declared (r96 1): plans/round-96.md A1. Not admitted; score stays 7; operator rules. |
| C1 check line and the ten r95 targets | calibration 7 | frozen r95 search on the r96 ids `errored=7 killed=2 survived=1` | r96 search `errored=7 killed=2 survived=1`, check line `check=pass … declared=1 argparse=2` (`census/round-96/records`) | `python3 -B census/round-96/c1-survivor-search.py --counter census/round-87/c1-pointer-counter.py --harness census/round-93/c1-false-row-harness.py --population census/round-93/c1-false-rows.tsv --lane . --fleet-root /home/vgpnk/Projects/shokunin --work <empty> --jobs 5 --ids census/round-96/c1-targets.json` | unchanged (no target moves; the ten targets do not discriminate the EH fix) |
| C2 T1 pipe-holder arm: exit 2 + FATAL within the probe timeout, not `hung` | operability 8 (no 0–10 mapping; unchanged) | r95 probe under the twenty-arm counter `ARM T1 exit=hung`, `ARMS-SUMMARY arms=20 conform=19`, EXIT 1 | r96 probe `ARM T1 exit=2 want=2 line=yes conform=yes`, `ARMS-SUMMARY arms=20 conform=20`, EXIT 0 (on rerun 2; run 1 had an unattributed S12 SIGTERM, plans/round-96.md A8) | `python3 -B census/round-96/c2-setup-arms.py --probe census/round-96/c2-forgery-probe.py --fixture-pass tests/fixtures/r93-k4-flagfail.py --fixture-fail tests/fixtures/r92-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work <empty>` | **verified, narrowed.** Counted quantity certifies exit-code discipline, not the mechanism (A7); grandchild not reaped (A4). |

No owned axis score changed (calibration 7, operability 8, coverage 8). The C1 row is a harm verdict and is reported as
such; the C2 row is an improvement on a narrowed reading.

### Round 96 capability rows

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| pipe-holder refusal within the timeout | refuse a fixture whose escaped `setsid()` grandchild holds the probe's pipes: the probe exits 2 with one `C2-FORGERY-FATAL:` line at its own `--timeout`, not `hung` (the grandchild is not reaped; plans/round-96.md A4) | `python3 -B census/round-96/c2-setup-arms.py --probe census/round-96/c2-forgery-probe.py …` → `ARM T1 exit=2 … conform=yes` (`census/round-96/controls/` and `.ufo/waves/round-96/w1/R96ExecC2/c2-after-arms-rerun2.txt`) | r96 |

### Planned (r97)

- C1 (calibration, trade to resolve): distinguish "handled at the top level" from "passed through a module-level frame"
  (a RERAISE-aware rule, or the exception's own state after the frame) so t1/t4 stay declared AND the module-level
  `finally` and re-raise shapes stay errored (plans/round-96.md A1, measured both ways). Add those two shapes and the
  module-level `finally` to the declared-shape table before any calibration claim on the EH leg is re-attempted.
  Fix the no-free-id fallback to restore fd 2's blocking mode (A3); route the excepthook and thread channels' blocking
  traceback print past the raw crash write (A2, E10). Predicate binding for the per-channel reason assertion (MutC1
  M04/M14).
- C2 (operability): reap the T1 grandchild by an identity other than the process group (per-arm absolute fixture path,
  verified at act time) and report the surviving-grandchild count per run as a number (A4). Cap the captured fixture
  output so an unbounded flood is refused within the timeout (A5). Record a signal exit (-15) distinctly in the counter
  (A8). Correct the counter's docstrings (sixteen-arm line; the non-integer `--timeout` class; T2's mechanism) (A6).
- Sources: supersede S365–S367 teaches with S369–S371 (done here); S368 (setsid(2)) supports the process-group claim.
- Carried: the forge-return channel (r92 limit ii), p2 basename granularity, p3 the punctuation lookahead, p7
  `_regular`'s symlink leg, p8 `token_ok`'s hyphen marker, the `fleet:` symlink leg, the battery `--only`/
  `--expect-killed` stale defaults, the r85/r86 C2 list, `_regular` pathspec framing, the quarantine intro-blob digest
  row, the r79 gate re-measurement, check-4 300 s backstop, r76 K03/K04, the r17 240 s runners, the r85-r87 K4
  counters' print-only `rc=`.
