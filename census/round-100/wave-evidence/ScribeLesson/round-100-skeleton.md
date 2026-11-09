# Round 100 — {{TITLE_C1_CLAIM}} (C1 {{C1_VERDICT_WORD}}); {{TITLE_C2_CLAIM}} (C2 {{C2_VERDICT_WORD}})

Lane base `a662bb0d7e033cc5ceccd70b52eb234404300845`. Plan with frozen predicates: `plans/round-100.md`
(A0.1 frozen predicates). Wave: one v1 wave, 14 seats (`w1`; evidence copied to `census/round-100/wave-evidence/`).
Attack share 7/14 (50 %); connector 1.

## Claims and verdicts

- **C1 (operability 8; Q177).** {{C1_CLAIM_SENTENCE}} Verdict: **{{C1_VERDICT_WORD}}** (L1 measurement; the
  non-author closure decides). Measured on committed bytes at `{{C1_COMMIT}}`, receipt `{{C1_RECEIPT_PATH}}`:
  {{C1_NUMBER}}. Controls on the same probe and fixtures: r99 counter (do-nothing) `{{C1_CONTROL_R99}}`;
  CM8 argv-only mutant `{{C1_CONTROL_CM8}}`; `m_noppid` mutant (session key removed) `{{C1_CONTROL_MNOPPID}}`.
- **C2 (calibration 7; correction-class).** {{C2_CLAIM_SENTENCE}} Verdict: **{{C2_VERDICT_WORD}}** (L1
  measurement; the non-author closure decides). Measured on committed bytes at `{{C2_COMMIT}}`, receipt
  `{{C2_RECEIPT_PATH}}`: {{C2_NUMBER}}. Leg 1 (the entry cites its row) `{{C2_LEG1}}`; leg 2 (the row names the
  entry) `{{C2_LEG2}}`. No new SOURCES row: `{{C2_ROW_COUNT}}`.

## Gate

Source rows re-opened live this round ({{SCOUT_SEAT}}; URL · access date · located quote, ≤25 words · location).
Each live fetch is HTTP 200 and byte-identical to its committed capture; each quote occurs exactly once in the live
fetch and in the capture:

| row | URL | access | located quote | location |
|---|---|---|---|---|
| S075 (re-verified; grounds C1's session key, stat field 6, and the field-22 starttime) | {{S075_URL}} | {{S075_ACCESS}} | {{S075_QUOTE}} | {{S075_LOCATION}} |
| S332 (re-verified; grounds C2's field-4 ppid wording) | {{S332_URL}} | {{S332_ACCESS}} | {{S332_QUOTE}} | {{S332_LOCATION}} |
| S368 (re-verified; grounds the setsid new session that makes the T1 escapee) | {{S368_URL}} | {{S368_ACCESS}} | {{S368_QUOTE}} | {{S368_LOCATION}} |

Capture-verified quotes for the L1's cross-check (measured by this seat on the COMMITTED captures only — NOT a live
re-open, which is the scout seat's duty): S075 field 6 "The session ID of the process." (occurrence 1 in
`census/round-98/srcs/proc_pid_stat.5.html`, sha256 `0f04d789…`); S075 field 22 "The time the process started after
system boot." (occurrence 1, same capture); S075 field 4 "The PID of the parent of this process." (occurrence 1, same
capture — S332 is the kernel emission-order attribution for this wording); S368 "The calling process also becomes the
process group leader of a new process group in the session" (occurrence 1 in
`census/round-96/srcs/setsid.2.html`, sha256 `52cbc190…`).

{{GATE_SOURCES_CENSUS_LINE}}

Non-author discernment: {{GATE_NON_AUTHOR_LINE}}

Assimilation: none this round (no `merge/souji/` theme taken). considerthese: the lane has no `considerthese/` dir.

## Mistakes

- **M{{MISTAKE_NUMBER}} — {{MISTAKE_TITLE}} (class: {{MISTAKE_CLASS}}).** Evidence: {{MISTAKE_EVIDENCE}}.
  Captured-by: {{MISTAKE_CAPTURED_BY}}. Fix: {{MISTAKE_FIX}}. **Shown able to fail:** {{MISTAKE_SHOWN_ABLE_TO_FAIL}}.

## Wave findings (summary; full verdicts in `census/round-100/wave-evidence/`)

{{WAVE_FINDINGS_SUMMARY}}

## Trend verdicts (lane)

- expansion: **{{TREND_EXPANSION_VERDICT}}**. {{TREND_EXPANSION_NOTE}}
- quality: **{{TREND_QUALITY_VERDICT}}**. {{TREND_QUALITY_NOTE}}
- discernment: **{{TREND_DISCERNMENT_VERDICT}}**. {{TREND_DISCERNMENT_NOTE}}

## Frontier

{{FRONTIER_LINE}}
