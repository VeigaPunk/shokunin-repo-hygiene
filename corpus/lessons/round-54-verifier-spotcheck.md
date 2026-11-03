# round-54 verifier spot-check

author: hyaku closure (non-author integrator, @m_zfl)
date: 2026-11-03
scope: non-author closure of souji round 54 (report `.ufo/reports/round-54/souji.md`; lane base `fe12daad2549f534650d406ebdbac9113d59313f` → tip `8fb6fbc651f1f1d31f77f944a2e3389bb4a9e894`). This file is written by the closure judge only; no lane-authored file was edited.

## 1. Step-1 conformance — PASS

- Report committed in the fleet repo by the lane identity: `git log --format='%an <%ae> %H' -- .ufo/reports/round-54/souji.md` → `souji-shokunin <souji@shokunin.local> fd4b364885bc27558bf727f2032d6f1d427ad082 round-54: souji report (+ L0 question: C1 admission ruling)`.
- `## SHONEN` heading present with one `[~]` line per box: `grep -cE '^- \[.\] ' .ufo/reports/round-54/souji.md` → 4; SHONEN.md has exactly 4 boxes (`grep -cE '^\- \[.\] ' SHONEN.md` → 4). All `[~]` (asserted, correct for an author report; no `[x]` self-attestation).
- Cited lane commits exist and are ancestors of the branch ref (jj-colocated; tested against `master`, not `@{u}`): `fe12daad…`, `3c394cab…` (freeze), `bfdbb336…` (capture), `0fada8b3…` (content), `8fb6fbc6…` (wave close) — all `git merge-base --is-ancestor <h> master` → OK.
- Clean and pushed: `git status --porcelain` → empty; `scripts/hyaku/jj-lane.sh state` → `state branch=master local=8fb6fbc6… remote=8fb6fbc6… ahead=0 behind=0 head=detached`.
- Prompt fidelity: `.ufo/prompts/souji-round-54.md` is the canonical template rendering + hyaku addendum §6 and carries the full round contract — mission/axes binding (§1), 1–3 falsifiable claims with lowest-axis rule (§2), L2 floor ≥8 in one batched call (§3, matching `MISSION.md` §L2 concurrency verbatim), report contract with report path, five required sections, SHONEN heading requirement and commit-hash citation rule (§4), commit-then-push ordering and push scope (§4–5), L0 side channel (§5), lane write scope (§3). No `model` argument recorded (report: "Routing: no model argument passed").
- Dispatch evidence: `.ufo/watchdog.log` carries exactly the digest lines `2026-11-03T17:16:51-03:00 launch souji round=54 pgid=3519769 driver=hyaku-inline attempt=1` and `2026-11-03T18:11:59-03:00 complete souji round=54; hyaku-inline attempt=1`.
- The report is a real report (work performed, evidence pointers, LOG-tied landed changes, checkable commit citations), not a marker → lane-round status `ok`.

## 2. Claims — re-check

Split per PROTOCOL §Gate standard (Closure consequence): the kill-power numbers were **re-measured** by me with plain awk over the committed matrix TSVs; the gate selftests, frozen-run verdicts and real-lane gate verdicts were **evidence-verified** from committed receipts (the lane-owned counters were never executed by closure).

### C1 — calibration 7 (annotation-agreement counter v3) → **improved**

- Re-measured: `awk -F'\t' 'NR>1 && $5==1{n++} END{print n+0}' census/round-54/records/c1-matrix-v2.tsv` → **5**; same on `c1-matrix-v3.tsv` → **11**. Matches the reported 5 → 11 of 13.
- Row readback of `c1-matrix-v3.tsv`: F1-HONEST-TIP exit 0, F12b-LOG-FILED exit 0 (green); every exit-1 row carries its named finding (F7–F9 CORRECTION-IN-FENCE, F10 ZONE-TOKEN-STRADDLES-EDGE, F11 BOGUS-RECOMPUTED, F12 UNFILED-SOURCES-ANNOTATION; F2–F6 keep their v2 findings — no carry-over regression). Matches the frozen kill rule in `census/round-54/preregistration.txt`.
- Not vacuous: the v2 arm kills 0 of the new attack fixtures F7–F12 (v2's 5 kills are F2–F6), so the new kills are real work.
- Selftest evidence-verified: `census/round-54/records/c1-selftest.txt` → `SELFTEST pass cases=13`, `EXIT=0`; expected verdicts pinned in `c1-selftest-expected.tsv` (sha256 `4e73c495…`, byte-identical at freeze `3c394cab` and tip `8fb6fbc6`).
- Instruments byte-frozen: sha256 of `census/round-54/c1-counter.py` = `f45d3d8f…` and `c2-counter.py` = `84b05295…` at freeze, unchanged at tip (never edited in-round).
- Real-lane verdict evidence-verified: committed receipts `c1-tip.txt` (rev `bfdbb336`) and `c1-content-tip.txt` (rev `0fada8b3`) exit 0 with the frozen SUMMARY `unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0`; the frozen predicate's real-lane leg names the content tip.
- HIGH named limit S1 (sentinel01; L1 reproduction committed at `census/round-54/records/s1-formfeed-reproduction.txt`): two form-feed lines above a `~~~` fence turn the F7 shape exit 1 → exit 0 (`str.splitlines()` vs `\n` count divergence). The frozen kill rule names committed fixtures only, so this is a named limit of the instrument's kill-power, not a breach of the predicate: **C1 verifies**. Routed as the first r55 item (counter v4 + red-before F7-FF); operator L0 ruling filed (default recorded in the L0 line: admit with the limit recorded).

### C2 — coverage 8 (capture counter v3) → **improved**

- Re-measured: `awk -F'\t' 'NR>1 && $5==1{n++} END{print n+0}' census/round-54/records/c2-matrix-v2.tsv` → **6**; same on `c2-matrix-v3.tsv` → **8**. Matches the reported 6 → 8 of 10.
- Row readback of `c2-matrix-v3.tsv`: FH-HONEST and FH2-SYMLINK-HONEST exit 0; FA4 → COMMENT-AMBIGUOUS-NAME, FA5 → RECEIPT-UNKNOWN-KEY, FA6 → CAPTURE-CRLF as its first finding — exactly the frozen kill rule's named conditions. FA7/FA8 are prereg-declared branch coverage ("not a new kill"); the v2 arm exits 0 on FA4/FA5, so the claim is not vacuous.
- Selftest evidence-verified: `c2-selftest.txt` → `SELFTEST pass cases=10`, `EXIT=0`, expected TSV pinned `e32f7934…` byte-identical freeze→tip.
- Real-lane verdict evidence-verified: `c2-tip.txt` (rev `bfdbb336`) and `c2-content-tip.txt` (rev `0fada8b3`) exit 0 `receipt=ok sorted=ok tool_pin=ok` with the `--tool-sha256 e7e79952…` pin; the wrong-pin able-to-fail demonstration is honestly qualified by ERRATUM-R54-1 (shown on the real lane, not in the selftest; the missing FA9 selftest arm is mutation survivor M11, routed to r55).

### No owned axis harmed

`git diff fe12daad 8fb6fbc6 -- SCORECARD.md` is purely additive (round-54 measurements, corrections, r55 plan): calibration 7, coverage 8, operability 8 all unchanged; no capability row enters the table (correct — both claims amend existing instruments, no new repertoire demonstrated). PROVINCE.md unchanged; SKILL.md +24 lines (r54 gate rows/registry + limit line); corpus/README.md +17 lines.

**Verdict: both claims verify; admission holds** (every claim verifies, no axis harmed). The C1 HIGH named limit is recorded and routed; the operator's L0 ruling on C1's admission remains open and is carried, not assumed.

## 3. Discernment spot-check (LEARNING.md, from outside)

Sampled from `corpus/lessons/round-54.md` `## Gate`: the one admit (S277) and the round's zero-reject claim.

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S277 CommonMark spec 0.31.2 (§4.5 fenced code blocks, §4.6 HTML blocks), tier A docs, status mined | admit | live `curl https://spec.commonmark.org/0.31.2/` (2026-11-03) | **agree** | Live fetch: HTTP 200, no redirect, 514698 bytes, sha256 `c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d` — byte-exact match to the pinned capture `census/round-54/sources/s277-commonmark-spec.html`. All five located quotes re-checked as verbatim substrings under the recorded recipe (strip script/style, strip tags, `html.unescape`, collapse whitespace): word counts 17/25/13/14/15, all ≤25, all `substring=True`; page heading "Version 0.31.2 (2024-01-28)" present. The row's `teaches` (fence opener choice + closing-fence parity) is grounded by the quotes; the admit is sound. |
| "Rejected this round: none" (Gate; sweep-honesty line: exactly one page opened) | (no reject sampled — claim re-verified) | `git diff fe12daad 8fb6fbc6 -- corpus/SOURCES.md` | **agree** | The registry diff base→tip contains exactly two row changes (S276 used-by old→new, S277 new row); `grep -ciE 'reject'` over the changed row lines → 0. No row entered `rejected` and no `REJECTED:` row was added, matching the lane's claim. The negative claim carries its sweep. |
| Census gate (frontier step, round-end) | — | `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` | conforms | Exit 0; final line `ok …/corpus/SOURCES.md`. Findings are warnings-only (pre-existing W04 duplicate-URL-across-scopes rows, ~60, none created this round); warnings are allowed at exit 0. |

Registry counts re-measured: `git show fe12daad:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` → 200; same at tip → 201. Matches the reported 200 → 201 (S277 added, tier A, mined by its citing entry in the same commit).

## 4. Trend verdicts (closure agreement with the report)

- **expansion: unchanged** — agreed. The one admitted knowledge entry (`corpus/knowledge/correction-filing-fence-grammar.md`, provenance trio first) sits on Core ground the lane already holds (PROVINCE Owns, correction-filing grammar); no frontier row advanced; no capability row. One new registry row (S277) is mined by that entry, so no uncited row was appended.
- **quality: improved** — agreed, with the HIGH caveat as reported. Kill-power over committed attack fixtures rose on both counters (C1 5→11, C2 6→8, re-measured); the r53 routed surfaces are instrumented; the r51/r52/r53 standing receipts are green at the tip; no admitted entry failed a re-check (the S277 entry was qualified with the S1/S2/PTR limits, not falsified). S1 shows the C1 instrument is not robust against exotic separators — recorded as a named limit with v2 carrying the same hole, so not a regression.
- **discernment: unchanged** — agreed. The round's non-author attacks produced four errata/mistakes (r53 "six rows" miscount, prereg F11 mechanism clause, control `filed=no` line, selftest-pin citation) plus S1/S2/S3/PTR, all recorded with evidence — but no grounded `QUALITY.md` criterion was added ("none is yet shown able to fail"), and the round has no reject-side sample, so per LEARNING.md neither improved condition is met. My spot-check agreeing with the sole admit does not by itself make the trend improved.

## 5. Routed defects (status-neutral; the lane fixes these next round)

1. **Unreceipted measured-revision claim.** The report's measurement-table note says "The real-lane recomputes were run at `8fb6fbc6` (final)", but no receipt for a run at `8fb6fbc6` is committed — the committed real-lane receipts measure `bfdbb336` (`c1-tip.txt`/`c2-tip.txt`) and `0fada8b3` (`*-content-tip.txt`). The frozen C1 predicate's real-lane leg names the content tip, so both claims verify without it; the defect is the evidence standard (a re-run offered as evidence must carry its committed observed output). Fix: commit a receipt for every revision a report cites as measured, or cite only receipted revisions.
2. **Unnamed kill row.** `c2-matrix-v3.tsv` counts FA8-SYMLINK-CLASS as a kill (exit 1) with finding `-`, while `c2-selftest.txt` prints `finding=class` for the same fixture. The prereg classes FA7/FA8 as branch coverage rather than named kills, so the frozen predicate holds, but a counted kill row should name its finding. Fix: name the finding in the matrix or mark branch-coverage kills explicitly.
3. **Carrier (integrator-owned, still open):** r53 verifier §6.2 — round-53 fleet-side wave artifacts are not durable. Carried on the integrator queue; the lane correctly routed it out of its scope (r54's wave evidence is committed under `census/round-54/wave/`).
4. **Pre-existing (not a round-54 defect):** ~60 W04 duplicate-URL-across-scopes census warnings in `corpus/SOURCES.md` (warnings-only, exit 0). Candidate for a future registry-cleanup round.

## 6. SHONEN observation for the operator (promotion is operator-owned)

All four SHONEN boxes look fully checkable by a non-author on the committed bytes: box 1 — SKILL.md `## Round 54 contracts` gate registry rows with entry commands, verdict maps, self-tests, pinned digests and write scope; box 2 — LOG.md `## Round 54` (+ addendum) with end-to-end capture, instrument amendments, wave, measurements and the S1 reproduction; box 3 — the round-54 gate commands run from committed bytes, independently reproduced 13/13 and 10/10 by wave executor seats; box 4 — PROVINCE.md unchanged with connector01 NO-OVERLAP across 20 sibling lanes (`census/round-54/wave/S54connector01.md`). The report correctly leaves all boxes `[~]` pending non-author verification.
