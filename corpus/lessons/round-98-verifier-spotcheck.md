author: hyaku closure (non-author integrator, @m_zfl)
# souji round 98 — verifier spot-check (non-author)

Lane: souji. Round: 98. Lane HEAD after round: ec93b642a4b5bdddd7087f0099d5fde37bf0abc0. Lane HEAD before round: d3af1c93416849ed481ec1d6ea3e272fc83f00a1. Report: .ufo/reports/round-98/souji.md. Prompt: .ufo/prompts/souji-round-98.md.

## Conformance (step 1)

- Report landed by lane identity: `git log --format='%an %H' -- .ufo/reports/round-98/souji.md` → `souji-shokunin ea0bf062…` and `souji-shokunin 259a279f…`. OK.
- SHONEN heading: `grep -n "^## SHONEN" .ufo/reports/round-98/souji.md` → line 137; 4 boxes all `[~]` with evidence pointers. OK (asserted, not `[x]` — no promotion claim).
- Cited commits exist and are ancestors of lane branch: `git -C souji-shokunin merge-base --is-ancestor d3af1c93416849ed481ec1d6ea3e272fc83f00a1 ec93b642a4b5bdddd7087f0099d5fde37bf0abc0` → OK (anc-d3af-ok). `merge-base --is-ancestor ca98ad08 ec93b642…` → OK. `merge-base --is-ancestor ff254387… ec93b642…` → OK (ff254387 is lane base).
- Lane pushed, no leftovers: `/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh state /home/vgpnk/Projects/shokunin/souji-shokunin` → `state branch=master local=ec93b642… remote=ec93b642… ahead=0 behind=0`. `git -C souji-shokunin status --porcelain` → empty. OK.
- Prompt carries template contract: `.ufo/prompts/souji-round-98.md` has Mission/AXES binding, claims (1–3), frontier step, L2 floor (≥8 in one batch), report contract with Work performed / Landed changes / Before→after / Sources & frontier / Trend verdicts / SHONEN, commit-then-push, push scope, L0 side channel. OK.
- Wave: `.ufo/waves/round-98/w1-results.json` → 12 seats SETTLED (R98ExecC1, R98ExecC2 partial, R98ExecCensus, R98Reviewer1, R98Reviewer2, R98Critic, R98MutC1, R98MutC2, R98Sentinel, R98Connector, R98ScoutSources, R98Scribe). OK.
- Prefile falsification ledger (addendum §8, Amendment 59): `python3 /home/vgpnk/Projects/shokunin/scripts/hyaku/prefile-falsification.py --lane souji --round 98` → `FINDING claims-missing …souji-shokunin/.ufo/waves/round-98/claims.json`, `FINDING ledger-missing …/claim-falsification.tsv`, `PREFILE-FALSIFICATION: SETUP findings=2`, exit 2. No `claims.json` or `claim-falsification.tsv` exists under `.ufo/waves/round-98/`. This is a conformance defect (absent ledger). Adjudication: the round-97 ledger pattern exists at `census/round-97/wave-evidence/` but was not produced for r98. The wave artifacts do contain falsifying material (R98Critic K2 predicate movability, R98Sentinel FINDING 4 branch-(c) wording) that the lane did reconcile in prose (Mistakes M6, Limits (a)) but did not file as a ledger. Status-neutral defect; does not by itself bar admission, but the underlying wording falsifications do (see claims). Do NOT edit the ledger — none exists.

## Per-claim re-check (step 2)

### C1 (calibration 7) — re-measured

Commands (closure re-measurement, not executed sibling gate — plain counters over committed bytes):
- `python3 -B census/round-98/declared-shapes.py --search census/round-98/c1-survivor-search.py --scripts census/round-98/shapes --work /home/vgpnk/Projects/shokunin/.scratch/closure98-r98` → `SHAPES-SUMMARY shapes=17 mismatched=0` (q1o hooked=70, q1q hooked=70, q1i hooked=0). EXIT 0. Matches report `census/round-98/records/shapes-r98.txt`.
- Control r97: same table with `--search census/round-98/controls/c1-r97-search.py` → `SHAPES-SUMMARY shapes=17 mismatched=3` (q1o/q1q hooked=1, q1i hooked=70). Matches `shapes-r97.txt`.
- Control r95: `--search census/round-98/controls/c1-r95-search.py` → `mismatched=3` (q1i MISMATCH only). Matches report.
- No-harm: `grep "SEARCH-SUMMARY" census/round-98/records/search-r97.log census/round-98/records/search-r98.log` → both `generated=278 ambiguous=9 uncompiled=0 hung=1 scored=268 errored=53 killed=139 survived=76`. Survivor file `survivors-r98.json` holds 76 entries. Identical summary confirmed.

Verdict: the numbers re-derive. HOWEVER, the predicate is movable: R98Critic K2 / Mistake M6 show the r97 hook reaches `mismatched=0` under three relabelled rows (`q1o=declared, q1q=declared, q1i=crash`) with zero hook change, because `declared-shapes.py` hard-codes `SHAPES` and `declared-shapes.expected` is prose no instrument reads. The lane already concedes this (M6 routed to r99: freeze labels in a file the runner reads). Per the prompt's falsification rule, a claim whose stated wording a wave artifact falsifies while the counter stays green does not verify as written. C1's wording claims a 17-shape table with q1o/q1q at 70 and mismatched=0 — true on committed bytes, but the do-nothing control does not bind those labels. The lane's own A0.1 pins q1i `declared` (correct: plain 0) and admits the control is movable. Closure grades C1 **improved** on the measured numbers but carries the M6 defect as routed; the improvement is real (latch fixes q1o/q1q by construction — object-keyed stamp, q1o RAISE leg, q1q cross-object flush) and the no-harm holds. C1 verifies as a measured improvement; the label-freeze fix is routed, not a harm.

### C2 (operability 8) — evidence-verified, not re-executed

Per §Gate standard this claim rests on a lane-owned instrument (arms counter + decoy test). Closure does NOT re-run the 83-decoy sleeper run (sibling gate); it verifies committed evidence:

- `census/round-98/records/decoy-r98-final.txt` → `ARMS-SUMMARY arms=20 conform=20`, `ARM T1 … survivors=0`, `DECOY-PLANTED n=83 dead=0 alive=83 counter_exit=0`, `DECOY-SUMMARY verdict=spared`.
- `decoy-r97-final.txt` → `conform=20`, `dead=60 alive=23`, `verdict=killed`.
- `decoy-cm8-final.txt` → `conform=20`, `dead=82 alive=1`, `verdict=killed`.
- Counter receipts `decoy-*-counter.out` show `ARM T1 exit=2 want=2 line=yes conform=yes survivors=0` in all three.

The decoy predicate discriminates in all three directions on the corrected driver (`--arm-timeout 200 --plant-delay 2`, lane fixtures for non-T1 arms). The lane report honestly marks C2 **measured, not admitted** — agreeing with closure.

But C2's frozen wording ("reaps only the pid the arm recorded at spawn and its ppid-chain descendants") is falsified by _reap_owned branch (c): `elif _is_descendant(pid, os.getpid()): pass` — any counter descendant carrying the token is signalled, including sibling-arm carriers (R98Sentinel FINDING 4, MEDIUM; `cross_arm_probe.py` reaches a P1-arm carrier by T1's reap). Branch (c) is needed for the escapee via PR_SET_CHILD_SUBREAPER, but the claim sentence does not name it. The lane already carries this as Limit (a) and L0 (operator decision open). Until the wording names branch (c) or the code narrows, **C2 does not verify as written**. The decoy measurement is real; the sentence is wider than the code in the un-stated direction and narrower than the code in the stated direction. Grade: **unprovable** (wording-to-code gap) — or more precisely, measured improvement on the foreign-decoy leg (r98 spares where r97/CM8 kill — that leg re-derives from records) but the claim as a whole cannot be admitted. The prompt's verdict set for axes is improved|harmed|unchanged|unprovable-but-better|unprovable; for the axis I grade operability **unprovable** because the claim wording fails, not because the leg fails. The round is therefore **not admitted** (admitted only if every claim verifies).

No axis was harmed: `git diff d3af1c93…ec93b642 -- SCORECARD.md` shows calibration 7, operability 8, coverage 8 unchanged; no score moves either way. Knowledge diffs only append r98 corrections superseding withdrawn r97 sentences (crash-channels-beyond-excepthook, deadline-owned-reaping); QUALITY Q175/Q176 added from M7/M8. No axis harmed.

## Per-axis verdicts

- calibration: **improved** (C1: 3→0 on 17 shapes, q1o/q1q 1→70, q1i 70→0, no-harm byte-identical; M6 routing does not erase the improvement).
- operability: **unprovable** (C2: decoy leg improves — foreign sparing discriminates — but claim sentence falsified by branch (c); wording-to-code gap left open pending operator decision; not admitted).
- coverage: **unchanged** (no new surface; SOURCES 294→294).

## Discernment spot-check (step 3, LEARNING.md)

Gate in `corpus/lessons/round-98.md` `## Gate` lists re-verified rows and mistakes, not a classic admits-vs-rejects table. I sample: (A) S372 re-verification (admit-type: re-verified live, byte-identical capture) and (B) S330 rejected row (reject-type: kept with reason/flip, grounds no entry). Both re-opened live by closure (ledger + live curls); plus the S075 quote check via the scout receipt and committed capture.

| item | decision sampled | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S372 RERAISE re-verified (Gate row 2) | admit (re-verified live this round; grounds C1) | https://docs.python.org/3/library/sys.monitoring.html (curl HTTP 200, 74653 bytes, sha256 2b281793…; `grep -c "An exception is re-raised"` live = 1 after tag-strip; committed `census/round-98/srcs/monitoring.html` sha256 matches) | agree | Quote "An exception is re-raised, for example at the end of a finally block." is 13 words (≤25) and present verbatim in the live body (href splits "finally block." but text is continuous in capture). Byte-identical capture claim holds. |
| S330 REJECTED (corpus/SOURCES.md) | reject (kept with reason/flip, grounds no entry) | /usr/share/man/man1/pgrep.1.gz + SOURCES row text; scout receipt `reopen-sources.out` covers S075/S372/S368 (S330 is an older reject) | agree | Rejection reason states S075 governs identity and the tool's own -P mechanism is proven by running it; flip names a needed scope. Consistent with corpus contract (reject kept, not deleted). |
| S075 quote (new-row check analogue: re-verified row) | re-verified (no new row; 294→294) | https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html (curl 200, 20647 bytes, sha256 0f04d789…; `grep -c "The PID of the parent of this process"` = 1; committed `census/round-98/srcs/proc_pid_stat.5.html` sha256 matches) | agree | Quote "(4) ppid %d — The PID of the parent of this process" is 8 words and present. Lane already corrects scope: field-4 wording is kernel-side S332, S075 scopes fields 5/6/22 — honest attribution. |
| S368 quote | re-verified | https://man7.org/linux/man-pages/man2/setsid.2.html (curl 200, 11555 bytes, sha256 52cbc190…; phrase opens "The calling process also becomes the process group leader of" in live HTML; full 17-word quote present in committed `census/round-96/srcs/setsid.2.html`) | agree | 17 words (≤25), byte-identical capture. Quote serviceable for C2's new-session escape leg. |

Sources-census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → `souji ok …corpus/SOURCES.md`, exit 0. Row count `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → 294 before and after. No new `corpus/SOURCES.md` row was written this round, so no new-row ≤25-word quote to verify beyond the re-verified rows above. Gitiles base64 caveat does not apply (man7/docs.python.org pages fetched as HTML, not ?format=TEXT).

## Trend verdicts (with evidence)

- expansion: **unchanged** — SOURCES 294→294, no new admitted knowledge entry on uncovered ground; two knowledge appends cite only re-verified rows.
- quality: **unchanged** — Q175/Q176 add grounded criteria from M7/M8 (with lesson behind each); knowledge corrections supersede the withdrawn r97 sentences; no falsified sentence left standing in touched entries. Not `improved` because C1's predicate remains movable (M6) — the gate still relies on claimant labels.
- discernment: **harmed** — pre-freeze gate missed all three: decoy-token mismatch (M7, Scribe + Connector C-4), survivor metric defect (M8, Scout F3 + Connector C-5), kind-swap movability (M6, Critic K2). All caught by attack seats. Late driver defects (pipe-holder fixtures → conform=13, counter killed at 420 s → false `spared`, T1 timeout race) also caught only after WAVE-DONE. Lane honestly grades harmed.

## Routed defects (lane must fix next round)

1. **M6 / Q173 gate** (from R98Critic K2): freeze kind label + plain code per shape in a file the runner reads (not `declared-shapes.py` hard-code + unread `declared-shapes.expected`); quote the three specific mismatch rows, not just a count. Routed to r99 in SCORECARD.
2. **C2 branch (c) wording** (R98Sentinel FINDING 4): either widen the C2 sentence to name branch (c) (any counter-descendant carrier) or narrow `_reap_owned` to the subreaper net explicitly (record escapee pid+starttime at counter-child observation). Open L0 stays until operator rules. Routed: SCORECARD r99 "name reap branch (c) in the C2 sentence or remove it".
3. **Prefile ledger absent**: produce `.ufo/waves/round-N/claims.json` + `claim-falsification.tsv` and run `prefile-falsification.py` <exit 0> before filing, covering every claim and every attack seat. r98 had neither file (exit 2 SETUP). Status-neutral conformance defect, not bars admission by itself; the underlying wording falsifications (1,2) do bar C2.
4. **survivors as witness** (Scout F3, Sentinel FINDING 5): `survivors` counts the spawn-pid chain; the escapee reparents to the counter. Keep decoy predicate as the C2 witness, not survivors. Already noted in r99 plan.
5. **/tmp guard accepts bare /tmp** (Sentinel FINDING 3, MEDIUM, carried from r97): fix or record as known limit. Not filed as a claim defect.

## Notes on digest and operator

Dispatch/complete digest (from closure prompt, copied): `2026-11-09T09:25:53-03:00 launch souji round=98 pgid=2802941 driver=hyaku-inline attempt=1`; `2026-11-09T09:28:36-03:00 lane-dead-no-report souji round=98; retry same round (hyaku-inline attempt=1: L1 ended without a landed report…)`; `2026-11-09T09:28:38-03:00 launch souji round=98 … attempt=2`; `2026-11-09T10:56:24-03:00 complete souji round=98; hyaku-inline attempt=2`.
Defects summary: missing prefile ledger (conformance defect, §8); C2 branch-(c) wording falsification (claim fails); C1 predicate movability (M6, routed). SHONEN boxes remain `[~]` asserted-by-author — promotion is operator-owned; boxes look checkable by a non-author only after the M6 freeze and C2 wording fix land.
