# Round 43 verifier spot-check — souji

author: hyaku closure (non-author integrator, @m_zfl)
Round: 43, lane souji. Report: `.ufo/reports/round-43/souji.md` (fleet commit `edf24077`, author `souji-shokunin <souji@shokunin.local>`).
Lane branch `master` before round: `619a75034dd6324e1a725f73034c59f7bf9558ef`; after: `a637122161afb0ee257aba4335312a50378cb7c9`.
Verification limited to documentary/source grounding and defensive correctness. Provider-denied seats were not probed, bypassed or routed around; they stay unverified.

## Conformance (step 1)

| check | command | observed | result |
|---|---|---|---|
| report committed by lane identity | `git log --format='%an <%ae> %H' -- .ufo/reports/round-43/souji.md` | `souji-shokunin <souji@shokunin.local> edf24077b891abe86e342e57fbdef0e1092888e9`, commit in fleet HEAD | pass |
| SHONEN heading + boxes | `grep -n "## SHONEN"` / checkbox grep | heading at report line 179; 4 `[~]` lines; 27068 B (>400 B) | pass |
| cited lane commits exist and are ancestors of `master` | `git -C <lane> merge-base --is-ancestor <h> master` for all 9 report hashes | all 9 ANCESTOR-OK (`41e69c38`…`a6371221`); round base `619a7503` is ancestor of `a6371221` | pass |
| lane pushed, no uncommitted round work | `scripts/hyaku/jj-lane.sh state <lane>`; `git status --porcelain` | `ahead=0 behind=0 local=remote=a6371221`, porcelain empty; `ls-remote origin refs/heads/master` = `a6371221` | pass |
| prompt carries template contract | read `.ufo/prompts/souji-round-43.md` | §1 mission/axes binding, §2 claims (falsifiable before→after, lowest-axis rule), §2b frontier step, §3 L2 ≥8 one batched call (matches `MISSION.md` §L2 concurrency), §4 report path/sections + SHONEN + marker rule, §5 commit-then-push, push scope, L0 channel, §6 hyaku addendum verbatim | pass |
| round scope | `.ufo/watchdog.log` digest | attempt 1 `lane-dead-no-report` 02:44:08-03:00, retry attempt 2 launch 02:44:10, complete 03:17:31 — one round, no mislabeled/extra rounds | pass (attempt-1 no-report defect in notes) |

## Per-claim re-check (step 2)

Method: committed receipts were read (never re-executed as gates); each claim was additionally re-derived with plain measurements over committed bytes run by this verifier. All commands below run in `/home/vgpnk/Projects/shokunin/souji-shokunin`.

### C1 — calibration (three historical self-assessment corrections)

Committed evidence (receipts, not re-executed): `census/round-43/controls/c1-resume-before.txt` `required=3 registered=0 missing=3 EXIT=1` at `13de0e84`; `census/round-43/records/c1-landed.txt` `required=3 registered=3 missing=0 junk=0 fenced=0 duplicate=0 retracted=0 rederived=3 rederive_failed=0 new_mismatches=0 EXIT=0` at `d1954ced`; discrimination fixture `records/c1-discrimination.txt` r43 10/10, r42 signatures 10/10 EXIT=0. Report values match.

Independent re-derivations (my own commands):

- D1 rows: `git show 0242085909fb6a4ee041c5443d76316ac6d59d4b:corpus/SOURCES.md | grep -cE '^\|\s*S[0-9]{3,}\s*\|'` → **174** (matches `derived=rows=174`; stale receipt `census/round-39/records/census-after.txt` footer reads `W04=47`, `rows` line carries the stale 173 per correction row).
- D3 measured revision: `git show 02420859…:census/round-39/records/final-tip-measure.txt | head -3` → `# final-tip re-measure at 544104503a3ad70687ba399fcafd12bd30648169` — confirms the header names the later measured revision, i.e. D3 is a measured-versus-carrier clarification, exactly as the report states.
- Correction lines present only after: `git show 13de0e84…:corpus/lessons/round-43.md | grep -c CORRECTION-R39` → 0; same at `a6371221` → 3.
- D2 W04=48: stale side confirmed in committed bytes (`W04=47` footer); derived side confirmed by the instrument's committed rederivation (`rederive_failed=0` in `c1-landed.txt`) and the wave reviewer `census/round-43/waves/w1/R43rederiveR43D2.md` (independent count, method shown, `match=yes`). This verifier's own awk reimplementation of the census W04 cross-scope rule did not replicate the validator (calibration at HEAD: awk 82 vs validator 54), so my recount is not comparable evidence either way — recorded, not a disagreement.

Verdict: **improved** — the registered numeric target is met and the substance (three wrong historical readings corrected with grounding) was re-derived independently for D1/D3 and evidence-verified for D2. Disclosed limits are real and accepted: the counter does not bind the captured derived token (wave documentary finding, retained); D3 does not repair a false header (none existed); no exhaustive correction-language coverage (fixture mutation 10/19 killed, `waves/w1/R43mutationtester01.md`); r42 CRLF-signature case never writes CRLF (`waves/w1/R43reviewer05.md`). SCORECARD keeps calibration 7 (no reproducible 0-10 mapping; no score delta claimed).

### C2 — operability (defensive freeze-check grammar)

Evidence-verified (lane-owned gate; not executed): `records/c2-landed.txt` `newtable=9/9 r42table=ok hidden=RED real=ok selftest=ok tmpdir=ok EXIT=1` at `d1954ced` (before `controls/c2-resume-before.txt` `newtable=2/9 … real=RED EXIT=1` at `13de0e84`); `records/c2-selftest.txt` `SELFTEST cases=41 pass=41 fail=0 EXIT=0`; `records/c2-hidden-full.txt` scenarios=10 pass=8 fail=2, h4 failing on a literal `C2:FIELD-MISSING*4` expectation vs four actual entries, h6 omitting its own post-freeze `C0:FROZEN-EDITED` finding — exactly the two oracle conflicts the lesson M43-1 documents. Plain check: the only `tools/` delta in the round is `tools/souji-freeze-check.py` (the C2 deliverable); no hidden case or fake finding class added (receipts show honest RED).

Verdict: **unchanged** — declared frozen target unmet (hidden=RED), not redefined; exercised behavior (real counter, newtable, 41-case self-test) improved but the claim does not verify its target. SCORECARD keeps operability 8.

### C3 — coverage (sixteen drift-survivor classes plus leaf-symlink refusal)

Evidence-verified: `records/c3-landed.txt` `killed=0 survived=16 cases=0 EXIT=1` before and after (identical); `records/c3-contract-conflict.txt` — independent candidate run over the legacy fixture `tests/fixtures/r38-drift-write-envelope.py`: cases=12 pass=11 fail=1, sole failure `case-json-symlink-resolved rc=2 resolved_written=False`, i.e. the requested refusal contradicts the legacy required resolution/write. Plain check: `git diff --name-status 619a7503 a6371221 -- tools/ tests/` shows only `tools/souji-freeze-check.py` modified and `tests/fixtures/r43-correction-prose.py` added — production drift tool and legacy fixture unchanged, no partial fixture installed.

Verdict: **unchanged** — target unmet, honestly reported as not landed as a capability; no capability row entered.

### No-axis-harm

`git diff 619a7503 a6371221 -- SCORECARD.md`: append-only round-43 measurements block; owned scores unchanged (calibration 7, operability 8, coverage 8); no axis decreased. `corpus/README.md` change is an appended frontier note explicitly disclaiming knowledge entries, Core promotion, and N10 closure.

## Non-author spot-check (step 3) — Gate sample

All four `## Gate` decisions of `corpus/lessons/round-43.md` re-opened; sources fetched fresh 2026-10-30 (no cache).

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S260 symlink(2) | admit | https://man7.org/linux/man-pages/man2/symlink.2.html (fetched) | agree | quote verified verbatim in DESCRIPTION ("A symbolic link (also known as a soft link) may point to an existing file or to a nonexistent one", 20 words); grounds refusal not depending on target existence; tier A scoped, no deletion-authority claim |
| S261 Python subprocess | admit | https://docs.python.org/3/library/subprocess.html (fetched) | agree | both quotes verified (env replacement "…used instead of the default behavior of inheriting the current process' environment"; `CompletedProcess.stderr` "Captured stderr from the child process."); scope correctly notes env replacement is not a sandbox |
| S262 preservation-authority inference | reject | same symlink(2) page, NOTES | agree | quote verified ("No checking of *target* is done."); rejecting link-existence-as-preservation-authority is the correct reading; flip condition stated |
| S263 PYTHONPATH discovery | admit | https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH (fetched) | agree | quote verified ("Augment the default search path for module files."); correctly separates the discovery channel from S259's sitecustomize-import fact; `teaches` opens `supersedes S259 …` per contract rule 2 |
| S260 registry row | row re-open | `corpus/SOURCES.md:214` | agree | tier/kind/scope/anchor/status/used-by all conform; used-by path resolves |

Census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → exit 0, `souji ok`, 54 W04 rows (S261/S262 added to the inherited 52), matching the report; rows 183 → 187 re-counted at both revisions (`grep -cE '^\|\s*S[0-9]{3,}\s*\|'`). Search-log entry present with counts. Q106 present in `corpus/QUALITY.md:272` citing lesson M43-1 and the committed red scenarios — grounded criterion from a real oracle disagreement.

## Per-axis verdicts (this verifier)

calibration **improved** · operability **unchanged** · coverage **unchanged** (depth/freshness/adjacency not claimed, not graded).

## Trend verdicts (this verifier)

- **expansion: unchanged** — no admitted knowledge entry, no capability row, no frontier-to-Core move (README note + SCORECARD diff concur).
- **quality: unchanged** — no knowledge entry re-verified/superseded; C2/C3 full targets unmet; S263 is a source-row supersession, not a knowledge-entry move.
- **discernment: improved** — non-author closure agrees with the gate on the sampled admits and the reject (table above), and a real oracle disagreement (M43-1) became a grounded criterion (Q106). This is the outside evidence the lane's own lesson said was still missing when it graded unchanged.

## Routed defects — lane must address next round

1. C1 counter does not compare its captured derived token (`R43critic03`); next freeze must bind the token in the target or scope the target to registration-presence explicitly.
2. C2 negative memorizer control crashes on a missing import — its REJECTED is not discriminating evidence; fix before relying on it.
3. C3 wrapper has uninterpolated doubled percent operators (fails compilation) and the sniff control's required positive kill is zero (EQUIV substitutions preserve MUTANTS anchors); n10-before lacks a candidate-specific before run; 9-vs-8 old-fixture scope discrepancy.
4. C1 discrimination fixture: 9/19 mutation survivors; r42 CRLF-signature case never actually writes CRLF — green column is not attribution proof.
5. Leaf-symlink contract conflict (refusal vs legacy r38 resolution/write) needs the operator-level contract decision and a joint cutover under a new freeze (as planned in SCORECARD).
6. Timing defect: formal preregistration landed after ready handoff (`8dfad888`) — irreversible this round, disclosed; never repeat.
7. 35 terminal provider-error seats (21 MiniMax quota, 11 Cursor pricing, 2 hardware-auth/cyber-policy denials, 1 Devin permission) recorded with exact evidence in `records/seat-terminal-evidence.json`; none supplies review clearance, none was bypassed — unverified work stays unverified.

Wave bookkeeping spot-checked: `records/wave-summary.json` seats=68, returned_outputs=33, terminal_errors=35, role mix and attack 34/68 match the report; `seat-terminal-evidence.json` has 68 rows. Capture verifier re-run by this verifier at the cited revision: `records=228 failed=0 uncovered=0, exit 0`.

All four SHONEN boxes are `[~]` with resolvable pointers; none is fully non-author-verified, so no `[x]` — promotion remains operator-owned.
