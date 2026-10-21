# FinalSeatAccounting — round 20 recovery seat accounting (read-only, pinned)

STATUS: PARTIAL — the pinned round-20 record does not state one consistent account of the 64 inherited orphan handles or the round total, and it omits the 25 provider-dead recovery seats from the lesson and LOG. The census JSON carries the counts; the narrative authorities do not. This is a real defect in the accounting record; it is not a product-code finding and it is not an admission claim.

Author-side advisory only. No build, test, lint, formatter, smoke, target-code execution, process census, signal, install or update was performed. No operator-sweep path was opened, listed or searched.

Pin: `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`. Every file below was read through `git show` or `git grep` at that commit.

Files read: `census/round-20/recovery-seat-outcomes.json`, `census/round-20/recovery-status-catalog.json`, `census/round-20/coordinator-start-excerpt.txt`, `census/round-20/coordinator-scope-deviation.json`, `corpus/lessons/round-20.md`, `corpus/knowledge/process-residue-observations.md`, `LOG.md` (round-20 entries via `git grep` and lines 1098–1122), `.ufo/waves/round-20/recovery/ConsumerSkill.md`, `census/round-20/transcripts/recovery/ConsumerSkill.txt`, `SKILL.md:296-318`, `corpus/README.md:299-315`, `tools/souji-rev-pin.py:34,182-190`. Not read: the wave registry, other recovery reports, and the 39 completed-seat reports.

## Finding (adversarial): the orphan handles and the 25 dead seats are recorded inconsistently

Attack: check whether the pinned authorities agree on (a) whether the 64 inherited handles are dead seats, (b) whether they consume round budget, (c) the round total, and (d) the recovery wave's dead and completed counts.

1. **Orphans, ruling A.** `census/round-20/coordinator-start-excerpt.txt:103` (parent IRC): "Treat all 64 as dead seats: record them in the report's dead-seat count (they still consume the ≤200 round budget, so fresh waves have ≤136 seats left)."

2. **Orphans, ruling B.** Same file, `:155` (parent IRC): "Report the cap episode in the dead-seats section honestly (0 dead, N refused pre-spawn — they never started)."

3. **Orphans, lesson and LOG.** `corpus/lessons/round-20.md:97-100` and `LOG.md:1106-1108`: "64 registered, 0 started, 0 consumed (dead-session orphans), not 64 completed or provider-dead seats." Ruling A and this disposition cannot both be the account. Ruling A puts the 64 in the dead count; the lesson and LOG exclude them from it.

4. **Round total.** The wave brief for this assignment states "Original dead-session64 handles consumed0 … Round total with this wave128, under200." 128 = 64 recovery + 64 final, so it excludes the orphans. Ruling A says they consume the ≤200 budget, which gives 64 + 64 + 64 = 192 with this wave. The "≤136 seats left" figure equals 200 − 64, so it is only consistent if the orphans count. No pinned file states a round total. [INFERENCE] The brief and ruling A conflict on whether the orphans count toward the budget.

5. **Cap episode, not evidenced.** `census/round-20/recovery-seat-outcomes.json` `pre_spawn_refusals`: attempts [1,2,3], `each_items` 64, `starts` 0, reason "Background job limit reached (100)". `inherited_pending_handles`: registered 64, started 0, consumed 0. No pinned record gives the observed job count at attempts 1–4. The inherited note at `coordinator-start-excerpt.txt:174` says "reservation released", but that is an assertion. [INFERENCE] If the 64 registered handles held job slots, a further 64-item call would exceed 100, which is what attempts 1–3 hit. Attempt 4, with the same 64 items, succeeded. That is consistent with release, but the record does not show it. "0 consumed" and "refused calls consumed zero seats" are therefore unverified as stated.

6. **Dead-seat omission.** `recovery-seat-outcomes.json` lists `dead_count` 25 and `completed` 39. Neither figure appears in `corpus/lessons/round-20.md` (its recovery section, lines 97–104, gives no counts and names no dead seat) or in `LOG.md:1109-1113` ("Failed provider seats are not replaced" — no count). The JSON's own `rendered_history_limit` says provider failures are omitted from `history://`, so the native auto-delivery strings in the JSON are the only error record, and the narrative does not reproduce them.

   I counted the 25 dead entries by error class (names match the JSON):
   - Cursor `RATE_LIMITED_CHANGEABLE` (3): SourceCuration, RejectionLearning, WaveAccounting.
   - Codex `turn_rate_limit_exceeded` capacity (4): GrantSymlinkLimits, ReceiptDrift, ErrataBinding, InputGitEnv.
   - zai `429 … type=1302` (18): GrantScratchW2, GrantJson, ConsumerScorecard, Counter14, GrantReport, GrantOwnOnly, InputR13History, ConsumerLog, SourceRevParse, InputHelper, SignalClassification, InputR13Corpus, RelativeTargets, ClaimNoTrade, SourceAdmit, InputRevision, GrantTsv, Counter13.

   Total 25. All 25 are provider capacity or rate-limit failures. None is a seat-content result. The lesson should say that rather than leave the dead seats out.

7. **Completed count unverified.** The 39 completed seats have no per-seat list in the named census files. The lesson's assertion that "every attempt response is preserved under `.ufo/waves/round-20/`" is outside the named read set, so I did not check it.

Falsification test used: if the lesson's "not dead" disposition holds, the round dead count is 25, and ruling A's "record them in the dead-seat count" was not followed. If ruling A holds, the dead count is 89 and the lesson's disposition is wrong. The pinned record supports neither reading without the omissions above.

Required repair (for L1; not applied here): choose one ruling and state it in the lesson and LOG; state the round total with arithmetic; add the 25 dead / 39 completed split and the three error classes; either record the observed job count at attempts 1–4 or label the cap explanation as unobserved.

## Secondary calibration items (native record accuracy)

- **Catalog disposition is uniform.** `census/round-20/recovery-status-catalog.json` says its "conservative catalogue preserves every visible STATUS paragraph independently". All 26 entries carry the identical disposition `open; source/limit retained pending pinned runtime and independent closure`. That includes SourceTimeout, whose paragraph reads "STATUS: no blocker. S094 verified as claimed". The lesson repeats the label: `corpus/lessons/round-20.md` lists SourceTimeout under "Seat-reported failures" as "open" beside "STATUS: no blocker". The paragraph text is accurate; the disposition label misstates it.

- **Truncation: not a defect.** Some tool renders of the catalog and lesson showed a trailing `…`. I checked the raw artifact for ReceiptAuditor (catalog line 7 paragraph) and the lesson's status lines. The pinned text is complete. I am not counting truncation as a finding.

- **ConsumerSkill self-disclosure is incomplete.** `.ufo/waves/round-20/recovery/ConsumerSkill.md` says it "issued one recursive `grep` rooted at the repository". Its transcript (`census/round-20/transcripts/recovery/ConsumerSkill.txt:47-50`) shows a lane-root `glob(/home/vgpnk/Projects/shokunin/souji-shokunin)` (129 lines) at line 47 and a lane-root `grep` (415 lines) at line 50, with two more greps at lines 48–49 and one at line 66 whose path is truncated in the transcript. The scope forbids bare glob/search of lane roots. The lesson's pointer (R20-M14, lines 47–50) is more accurate than the seat's report, so the seat report should not be cited as the complete disclosure.

- **ConsumerSkill snapshot is not the pinned build.** The report's working-byte hashes are `SKILL.md` 2d33b871…, `corpus/README.md` 91c9a77a…, `tools/souji-rev-pin.py` d3e9111b…. The pinned blobs are `SKILL.md` 28d80b78…, `corpus/README.md` f634b4dd…, and `tools/souji-rev-pin.py` d3e9111b… (match). Its `HEAD` was 12516f7d, not the pin. Its substantive pointers do hold at the pin: `corpus/README.md:299-315` gives five full 40-hex counter commands (304–308); `tools/souji-rev-pin.py:34` is `^[0-9a-f]{40}$`; `SKILL.md:303-316` has the round-20 full-40 index. The claim survives; the byte identity it cites does not.

## Agreed checks

- `dead_count` 25 equals the number of `dead[]` entries; `role_mix` sums to 64; no duplicate dead names.
- The pre-spawn refusal reason string matches between the JSON and `LOG.md`/lesson text.
- The lesson's and LOG's "not replaced" and "no respawn" statements match the JSON `replacements: 0`.

## Not checked / limits

- No runtime execution, no tests, no process census, no signals, no installs or updates.
- The 39 completed reports and `.ufo/waves/round-20/` registry were not opened.
- The job count at each attempt is not in any named file; the cap explanation above is inference.
- Author-side advisory only. Not non-author closure, promotion, or a SHONEN mark.

Stop after this report.
