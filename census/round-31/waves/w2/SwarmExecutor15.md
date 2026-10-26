# SwarmExecutor15 — r31 w2 · tip landing gate, rounds 13–30 (base vs tip)

## Status

STATUS: PASS — both gates were run over every round 13–30 at the named revisions, the per-round classes were tabulated, all 56 remaining tip findings were line-listed and spot-checked against committed bytes, and M1 was re-derived independently (26/29/19 appended entries, 0 uncarried at tip). The uncarried set is exactly `{15, 19, 23, 24, 25}` as expected. Four instrument/residual findings and two missing prereg-named receipts are recorded below; none blocks this assignment.

## Evidence

Revisions: lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, tip `2c16d018e40db7c23420a2c3bb546b52957bcc25` (= HEAD, worktree clean), base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`, prereg `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`, M1 landing `c6108301cbf0ca0ad086ff0ece6b76adad6b74b6`.

```
# tip gate, every round
python3 -B tools/souji-landing-gate.py --root <lane> --rev 2c16d018e40db7c23420a2c3bb546b52957bcc25 --round N --fleet-root /home/vgpnk/Projects/shokunin
# base gate blob (sha256 ba37e6bf804db1ad16b2ab53878a6626308bebb854af9bc2e7d230de81cd9056, 2374 lines)
git -C <lane> show 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc:tools/souji-landing-gate.py > base-gate.py
python3 -B base-gate.py --root <lane> --rev 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --round N --fleet-root /home/vgpnk/Projects/shokunin
```

Per-round census (full machine table and the exact SUMMARY lines: `deliver-tip-gate-all-rounds.tsv`, `deliver-tip-gate-evidence.txt`; findings: `deliver-tip-gate-findings.tsv`):

| round | base seat / dang / other | tip seat / dang / other | carry_heading base→tip | checked_reports base→tip |
|---|---|---|---|---|
| 13 | 0/0/0 | 0/0/0 | 0→0 | 32→32 |
| 14 | 0/0/0 | 0/0/0 | 0→0 | 32→32 |
| 15 | **1**/0/0 | **1**/0/0 | 0→0 | 64→64 |
| 16 | 0/0/0 | 0/0/0 | 1→1 | 141→141 |
| 17 | 0/0/0 | 0/0/0 | 1→1 | 122→122 |
| 18 | 0/0/0 | 0/0/0 | 1→1 | 175→175 |
| 19 | 3/**4**/0 | 3/0/0 | 1→1 | 67→67 |
| 20 | 0/**6**/0 | 0/0/0 | 1→1 | 103→103 |
| 21 | 0/0/0 | 0/0/0 | 1→1 | 62→62 |
| 22 | 0/0/0 | 0/0/0 | 1→1 | 248→248 |
| 23 | **10**/2/0 | **10**/2/0 | 1→1 | 75→75 |
| 24 | **17**/**1**/0 | **17**/0/0 | 1→1 | 73→73 |
| 25 | **23**/0/0 | **23**/0/0 | 1→1 | 80→80 |
| 26 | **18**/0/0 | 0/0/0 | **0→1** | **466→495** |
| 27 | **29**/0/0 | 0/0/0 | **0→1** | 94→94 |
| 28 | **19**/**2**/0 | 0/0/0 | **0→1** | 61→61 |
| 29 | 0/0/0 | 0/0/0 | 1→1 | 86→86 |
| 30 | 0/0/0 | 0/0/0 | 1→1 | 90→90 |

- Zero `LG-FROZEN-PIN`, `LG-PARSE-*`, `LG-OPEN-ADMITTED` or `LG-DANGLING-PTR-EXEMPT-STALE` findings in either arm; "other" is 0 at every round.
- Base-gate `LG-DANGLING-PTR` at base content = 13 (r19 4, r20 6, r24 1, r28 2) — the C2 prereg's false-positive set, reproduced exactly. Tip clears all 13 and keeps 2 (r23).
- The 13 cleared are genuinely resolvable: the four `census/round-1{8,9}/...seat-audit...json` ellipsis placeholders each match committed `seat-audit-*.json` blobs; `tools/souji-seat-audit.py:274–277` targets an 801-line file; `corpus/knowledge/process-residue-observations.md:58–59` a 228-line file; `tests/fixtures/r18-proc-census.sh:395–396` a 765-line file; `.../vadv-49/.gitignore:fixture/` resolves to the committed `census/round-26/waves/assimilation/validate/tests/vault/vadv-49/.gitignore.captured`; the other 7 are letters-only prose alternations.
- Union discovery: at base, prereg and tip revs alike r26 wave=466 / capture=495 (union 495, capture-only 29), r27 wave=0/capture=94, r28 wave=0/capture=61. The base gate reads wave-if-non-empty-else-capture (`base-gate.py:475-491`: "When both are committed the wave dir alone is read, so no report is ever counted twice."), so only r26 loses the 29; the 466 suffixes present in both trees have identical blob oids (0 byte divergences).
- M1: base gate at `1d45496a` = r26 18, r27 29, r28 21 (19 seat + 2 dangling) — matches `census/round-31/records/m1-red-before.txt`; at `c6108301` = 0/0/2 (dangling only); tip gate at `c6108301` and at tip = 0/0/0. Appended sections hold 26 / 29 / 19 entries (r26 two carry headings, the appended one at line 105; r27 line 43; r28 line 54), dispositions open=17/13/6, resolved@40hex=9/16/13, every entry carries a token, and all 38 `resolved@` revisions resolve as commits (`git cat-file -e <h>^{commit}`).
- Independent re-derivation (`deliver-tip-gate-indep-carry.py`: own tokenizer, full-paragraph matching with no ellipsis allowance, carry region = first heading to EOF) reproduces the same uncarried set and counts at rounds 15/19/23/24/25 (1/3/10/17/23) and 0 at r26/27/28, i.e. the M1 entries quote whole paragraphs, not prefixes.
- None of the 54 remaining seat failures is quoted in its round's `corpus/lessons/round-N-verifier-spotcheck.md` (probe: first 70 normalized characters of the failure paragraph, 0/54 found).

## Findings

1. **Five rounds still carry uncarried seat failures at tip; no other round has any finding.** r15 1, r19 3, r23 10, r24 17, r25 23 = 54 `LG-SEAT-UNCARRIED` + r23's 2 `LG-DANGLING-PTR` = 56. Each is line-listed in `deliver-tip-gate-findings.tsv`; four were re-read against committed bytes verbatim (e.g. `.ufo/waves/round-15/w1/ConfigRepair.md:7` = `## STATUS: INCOMPLETE — file has an unresolved syntax error`, `.ufo/waves/round-24/w1/CritC3Value.md:4` = `STATUS: PARTIAL — the draft keeps regress=5/5, …`). Axis: calibration (the committed record set still overstates closure) — pre-existing, not introduced by r31. r15 has no carry heading at all (`carry_heading=0`); r19/r23/r24/r25 have one but it carries almost nothing: token-bearing carry bullets 1/9, 10/64, 1/47, 1/17, and r23 still shows 10 of its 11 free markers uncarried.
2. **r23's two remaining dangling pointers are real, not gate noise.** `census/round-3/garbage-census.out` cited at `corpus/lessons/round-23-verifier-spotcheck.md:28` (that lesson states "The source path cannot be reopened: it is absent.") and `tools/__pycache__/` cited at `corpus/lessons/round-23.md:69` ("the directory is a K4 mismatch and the lane has no `.gitignore`") are both absent from the tip tree (`git ls-tree | grep` gives 0 and no `tools/__pycache__` parent). Axis: operability — these are the G8/G9-shaped true positives the new tokenizer must keep, and it does.
3. **Rounds 13–17 are judged by the loose pre-18 carry rule (`WRAP_STRICT_FROM_ROUND = 18`), so "clean" there is weaker than for 18+.** At tip, gate semantics differ from my full-paragraph re-derivation on round 16 only: 7 failure paragraphs (`.ufo/waves/round-16/w2/{ReopenS048.md:102, RerunGateFixture.md:12, RerunSeatAudit.md:157, RevCensusStatusFinal.md:359, RevengeSeatViolations.md:260, ScoutLsFilesPathspec.md:179, ScoutOptionalPrefix.md:238}`) are accepted because the lesson quotes the first physical line as a substring and cuts mid-sentence without an ellipsis, plus 3 fenced probe lines (`MutateGateCarry.md:141,155,190`) never enter the marker count. The same bytes in a round ≥18 would be judged strictly. Axis: operability (reading precision, round-dependent); no frozen target is affected.
4. **The letters-only prose rule is a reproduced recall hole, disclosed by A3 and mandated by fixture leg G8.** `_prose_pointer` accepts any token whose components are letters only ("no trailing `/` and every component is letters only"), so `if _prose_pointer(path): continue` runs after the existence test and silently drops absent all-letters citations. In a throwaway repo under my scratch (`probe2`, round 18, one carried failure) the base gate reported 11 of 11 absent citations and the tip gate 5 of 11: suppressed were `corpus/foo`, `corpus/foo/bar`, `corpus/foo/bar/baz`, `corpus/knowledge/foo`, `tests/probes`, `corpus/ROUND`, while `corpus/foo2`, `corpus/foo-bar`, `corpus/foo_bar`, `census/round-33`, `tools/foo.py` stayed reported. In the real lane's gate sources 10 absent tokens are prose-dropped at tip, all verified prose or grep patterns (the 7 base-gate false positives plus `census/checker`, `census/verify/vault/quarantine`, `tests/probes`), so today's readings are not masked — but an invented letters-only path passes. Axis: operability (attack surface, not a present-day misreading).
5. **Two receipts the frozen contract names are absent at tip.** `census/round-31/records/landing-gate-per-commit.txt` (prereg routed r30 defect 5: "run the landing gate at every record-landing commit"; `git log --all -- <path>` is empty and it is not in the tip tree) and `census/round-31/records/census-end.txt` (prereg frontier step "census before/after in census/round-31/records/census-start.txt and census-end.txt"; `records/` holds only `census-start.txt`). Axis: calibration (bookkeeping-file claims must rest on committed receipts). Integration owner's call, not written by this read-only seat.
6. **A carried-open residual's literal is stale at tip.** `corpus/lessons/round-27.md:63,65` carry the `__pycache__` residual `open` with the check "no tracked file matches __pycache__" FAILS at count 1; the tip tree tracks 5 such blobs — `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc` plus four under `.ufo/waves/round-26/assimilation/validate/{tests/fixtures,tools}/__pycache__/`. Axis: operability (workspace hygiene; the gate's `tools/__pycache__/` finding at r23 is unaffected, that path is absent).

## Attack log

- **A1 — masking differential on the cleared set.** Tried to show the tip gate hides a real dangling pointer while clearing the 13. All 13 resolve to existing blobs or verified prose; the two it still reports are genuinely absent. Attack failed → C2's lane leg survives my reading.
- **A2 — prose-rule probe (reproduced).** Built a minimal round-18 repo in scratch: one carried `STATUS: FAIL`, 12 absent citations. Base gate 11 findings (rc 1), tip gate 5 (rc 1). `corpus/nonexistent` was reported by the base gate and cleared by the tip gate. Reproduced state, finding 4.
- **A3 — look for a present-day masking instance.** Scanned every gate source at tip with the gate's own tokenizer and did my own resolution bookkeeping: 10 absent tokens prose-dropped across rounds 15/17/19/20/24/28; read all 10 in context — each is an alternation, an adjective compound or a `grep` pattern. No live citation is masked today.
- **A4 — union byte differential.** For every round, compared the oids of suffixes committed in both `.ufo/waves/round-N/` and `census/round-N/waves/`: r26 both=466, bytediff=0; every other round has one tree only (r13–25 wave only, r27–30 capture only). Preferring the wave copy cannot change checked bytes.
- **A5 — findings vs bytes.** Re-read 4 finding lines from committed blobs; the gate's `line N: …` text matched byte-for-byte.
- **A6 — hidden elsewhere?** Checked whether the 54 uncarried failures are quoted in the round's verifier-spotcheck lesson (0/54), i.e. the gate is not over-reporting something the lane already recorded.
- **A7 — M1 dispositions.** All 38 `resolved@<40hex>` revisions exist as commits; entry counts 26/29/19 match the claim; no entry lacks a token.
- **A8 — round-28 base residual.** Confirmed the base gate still reports r28's 2 dangling pointers at the M1 landing commit (`m1-after.txt` matches my run exactly: findings=2, rc=1), so M1 fixed the seat class only, as claimed.
- Not run (not my lane): C1/C2/C3 counters, gate `--selftest`, lane fixtures — wave-1 and the L1 own those; nothing here is claimed as passed.

## Deliveries

All under `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-31/w2/`:
- `deliver-tip-gate-all-rounds.tsv` — per-round base vs tip classes (seat / dangling / other), carry heading, checked reports, verdict.
- `deliver-tip-gate-findings.tsv` — all 56 remaining tip findings: round, class, path or token, detail with line.
- `deliver-tip-gate-evidence.txt` — exact commands, every SUMMARY line for both arms, cleared-pointer resolution, union counts, M1 re-derivation, residuals.
- `deliver-tip-gate-indep-carry.py` — the independent carry census used above (scratch instrument, not a lane tool; not installed into `tools/`).

No lane file was written outside this wave directory; no git or jj mutation, no deletions, no signals; no package installs were needed (python3 and git sufficed, no pacman).
