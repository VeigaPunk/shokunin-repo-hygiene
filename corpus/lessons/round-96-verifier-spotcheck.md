author: hyaku closure (non-author integrator, @m_zfl)
round: souji 96 (lane base 689d1c9570a5df2344e16a5916c49e24b46823ab; lane HEAD 2bbbab6d8c150e92523553d357764a5c185c42fb)
date: 2026-11-09
type: non-author verifier spot-check

# 1. Step-1 conformance

- Report: `.ufo/reports/round-96/souji.md` committed by the lane identity (`souji-shokunin 1957f3b6f3dcee9d2d16412de7bba1984884637b round-96: souji report`). Ancestor of fleet HEAD `22a29619` (`git merge-base --is-ancestor 1957f3b6 HEAD` → ok).
- SHONEN heading present (line 115) with 4 × `[~]` lines citing resolvable pointers (SKILL.md tables, corpus/SOURCES.md S100-S103/S368-S371, corpus/lessons/round-96.md Gate, LOG.md round-96 entry, census/round-96/run-receipt.sh + records/c1-after.txt + records/c2-after.txt, `.ufo/waves/round-96/w1/R96Connector.md` §1). No `[x]` — correctly, per the report's own note (no non-author verifier has checked promotion-relevant claims beyond wave seats).
- Lane commits: `689d1c95..2bbbab6d` = 4 commits (P1 `0656de3f`, P2 `4dd8a103`, F `c1209623`, after `2bbbab6d`), all by `souji-shokunin`. `git -C souji-shokunin merge-base --is-ancestor 689d1c95 master` and `--is-ancestor 2bbbab6d master` both pass.
- Clean/pushed: `souji-shokunin status --porcelain` empty; `jj-lane.sh state` → `ahead=0 behind=0` (pure git, read-only).
- Prompt carries the template contract: MISSION/AXES binding, 1–3 claims with lowest-axis rule, L2 floor (≥8 in one batched swarm), frontier step, report contract with 5 child-lane items, commit-then-push, L0 side channel, run-15 addendum §6. Verified against `templates/round-prompt.md` rendering.
- Wave evidence: `.ufo/waves/round-96/` lives **inside the lane repo** (lane-owned scratch, git-ignored per lane `.gitignore` line 1 `.ufo/waves/`), not at the fleet root. The report's citations to `.ufo/waves/round-96/w1/R96*.md` resolve under `souji-shokunin/` (13 seat reports present; `w1-results.json` 13/13 settled; attack seats 8/13 ≥25%). The w1-spec header says 12 seats but the dispatched count is 13 — dispositioned as A0.2 (prereg line 12 vs item count 13), status-neutral.
- Watchdog digest (closure input): launch `2026-11-09T03:34:35-03:00 launch souji round=96 pgid=2976316 driver=hyaku-inline attempt=1`; complete `2026-11-09T05:50:56-03:00 complete souji round=96; hyaku-inline attempt=1`. Matches the live `.ufo/watchdog.log` for this round.
- Report is not a marker: names real committed work (four cited hashes, counting commands, wave evidence). Minimum-content OK. No marker verdict.

**Conformance defects (status-neutral, named here):** (a) w1-spec header 12 vs 13 seats (A0.2) — prefile/state line count mismatch to fix in the spec writer, routed r97. (b) Wave evidence is git-ignored in the lane, so seat artifacts are durable on disk only — the judge re-opened them from the live checkout; a future archive step (or an explicit lane decision to keep them uncommitted) is routed r97. (c) Report's "Wave evidence … on disk under `.ufo/waves/round-96/`" does not name the lane-repo root prefix — minor path ambiguity, routed r97.

# 2. Pre-file falsification ledger (2b)

`python3 scripts/hyaku/prefile-falsification.py --lane souji --round 96` → `PREFILE-FALSIFICATION: pass claims=2 rows=14 attack_seats=8 findings=0`, exit 0. Recorded directly.

- Ledger `souji-shokunin/.ufo/waves/round-96/claim-falsification.tsv`: 14 data rows (7 per claim), verdicts `falsifies-wording` 7 / `neutral` 7. Every row names a narrowing amendment (A1–A11) or `-` for `neutral` rows where the schema requires it; every `falsifies-wording` row names a narrowing amendment, per addendum §8. All 8 attack-role artifacts are read (Reviewer×3 + Critic + Mut×2 + Sentinel + Connector = 8 seats: R96ReviewerC1, R96ReviewerC2, R96ReviewerShapes, R96Critic, R96MutC1, R96MutC2, R96Sentinel, R96Connector).
- Adjudication of the 7 falsifies-wording rows:
  - C1-A1 (ReviewerC1 q1e + ScoutSources §3, finally): **real and reconciled** — matches the L1 A1 table and the judge's own re-derivation (§3). The narrowing (1247df0) is a worsened predicate (t1/t4 70→0 vs modfin/reraise 70→1). Claim does not verify on its own terms; recorded as `harmed` on calibration, not silently amended up.
  - C1-A2/A3 (Sentinel F-1/F-2): **real and reconciled** — crash-path wording over-claimed "cannot block"/"momentarily". Narrowed to the write-only truth and the fallback limit; the corrected corpus entry is the current text. No count moves (treatment drained). Not a claim predicate; a wording correction, correctly applied pre-filing.
  - C1-A9 (ReviewerShapes §3, label): **real, cosmetic** — "r94-rule mismatched=6" was the r95 receipt. Re-derived: r94-rule-as-search gives `mismatched=4` (r96 kind logic) / `0` (plain-vs-hooked), never 6. Label corrected, counts unchanged. Counted quantity unaffected.
  - C2-A4 (Sentinel F-4 + Scribe reapcheck): **real and reconciled** — stated limit (iv) "the counter kills it" falsified by measurement; narrowed before filing and withdrawn from `deadline-owned-reaping.md`. T1 predicate unaffected, as narrowly scoped.
  - C2-A5 (ReviewerC2 Q1a): **real and reconciled** — limit (i) mechanism wrong (unbounded output → RSS exhaustion 27.3 GB, SIGTERM at 36 s, no FATAL, not a blocked pipe). Narrowed to memory exhaustion; the probe's characterization is now correct. T1 predicate unaffected (T1 arm exercised separately).
  - No row is spurious; each named narrowing is the honest narrowing in `plans/round-96.md` A1–A11. The ledger "pass" aligns with the substantive verdicts: C1 honest-stop `harmed`; C2 exits on a narrowed reading (A4/A5/A7).

# 3. Claim re-derivation (independent measurements)

Every instrument was re-run by the judge on the committed bytes at `2bbbab6d8c150e92523553d357764a5c185c42fb`, writing only to `/fast/scratch/hyaku/v96*` (the shapes runner refuses `/tmp` writes; no lane bytes were touched).

## C1 — calibration (re-measured; verdict: harmed)

- r96 hook table: `python3 -B census/round-96/declared-shapes.py --search census/round-96/c1-survivor-search.py --scripts census/round-96/shapes --work /fast/scratch/hyaku/v96` → `SHAPES-SUMMARY shapes=12 mismatched=0`, EXIT 0. Matches `records/shapes-after.txt`.
- Frozen r95 hook on the same scripts: `--search census/round-95/c1-survivor-search.py` → `SHAPES-SUMMARY shapes=12 mismatched=2` (t1/t4 `hooked=70 MISMATCH`), EXIT 1. Matches the report's claim (t1/t4 70 under r95). The report's "r94-rule mismatched=6" label is the r95 receipt as A9 admits; the reviewer reproduction (4 on r96 kind logic, 0 plain-vs-hooked) is consistent with this second observation.
- Ten-target search (r96 search): `python3 -B census/round-96/c1-survivor-search.py --counter census/round-87/c1-pointer-counter.py --harness census/round-93/c1-false-row-harness.py --population census/round-93/c1-false-rows.tsv --lane . --fleet-root /home/vgpnk/Projects/shokunin --work /fast/scratch/hyaku/v96d --jobs 5 --ids census/round-96/c1-targets.json` → `SEARCH-SUMMARY generated=10 ambiguous=0 uncompiled=0 hung=0 scored=10 errored=7 killed=2 survived=1` with `check=pass … declared=1 argparse=2`. Matches `records/c1-after.txt` and the P2 control line `errored=7 killed=2 survived=1` — the ten targets do not discriminate the EH fix, as the report states.
- The shape table is **blind to its own regression**: it has no terminating module-level-finally or re-raise shape, so `mismatched=0` is compatible with the A1 harm. The judge confirmed against the corpus entry's own measured tables (`r95's shape rows: t1 70? t4 70?` — the table reports 2 under r95 — and the L1's modfin/reraise reproducer: r95 hook 70 / r96 hook 1). The 12-shape table undercounts the true surface by omitting the shapes that break the fix. The report's headline ("mismatched=0, r95 hook 2") is accurate on the table; the A1 section records the off-table harm. This is precisely why C1 cannot be graded `improved` — the predicate as frozen does not bind the counterexample the wave found.
- Grade: **harmed**. Dominant: the measured regression (two terminating module-level shapes 70→1 wrong) outweighs the gains (t1/t4 70→0 right) on the same calibration axis. Verdict matches the report and `plans/round-96.md` A1; score stays 7 in SCORECARD.

## C2 — operability (re-measured; verdict: improved on the narrowed reading)

- Twenty-arm counter (r96 probe): `python3 -B census/round-96/c2-setup-arms.py --probe census/round-96/c2-forgery-probe.py --fixture-pass tests/fixtures/r93-k4-flagfail.py --fixture-fail tests/fixtures/r92-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work /fast/scratch/hyaku/v96c` → `ARM T1 exit=2 want=2 line=yes conform=yes`, `ARMS-SUMMARY arms=20 conform=20`, EXIT 0 (bg_2778, 165.9 s). Matches `records/c2-after.txt`. Re-measured, **not** evidence-verified: the predicate is the judge's own run, and it closes on the third consecutive execution (lane after-run 1: S12 `exit=-15`, EXIT 1; rerun 2: conform 20; judge run: conform 20). The A8 disclosure covers the first-run failure; the judge's clean run does not erase it — it shows the failure is transient, not deterministic.
- Before (frozen r95 probe): `controls/c2-control-r95-probe.txt` records `ARM T1 exit=hung`, `ARMS-SUMMARY arms=20 conform=19`, EXIT 1. Δ = +1 arm (T1 hung → exit 2 + `C2-FORGERY-FATAL:`).
- Narrowed reading (A4/A5/A7): the 20/20 counts exit-code/EOF discipline (the Critic's basename cheat reaches 20/20, M3/M5 mutate-survive) and does **not** certify reaping. The narrowed capability claim — "refuse a fixture whose escaped `setsid()` grandchild holds the probe's pipes: exit 2 with one `C2-FORGERY-FATAL:` line at its own `--timeout`, not `hung`" — is true as the judge measured. The capability row in SCORECARD (`pipe-holder refusal within the timeout`) states exactly this; the grandchild-survives limit is on the same row. This is a real capability, honestly scoped.
- Grade: **improved**. Operability 8 → 8 (no 0–10 mapping on this lane; the +1 arm gain is measured). The S12 first-run anomaly is disclosed, not grade-affecting.

## Sourced / frontier step (re-measured)

- Census before→after: `git show 689d1c95:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` → 286; current `grep -cE …` → 293. `git diff --numstat 689d1c95 -- corpus/SOURCES.md` → `7 0` (additions only, no existing cell touched — rule 2 PASS for the claim period).
- New tier-A rows: S368 (new, setsid(2)), S369–S371 (supersede S365–S367 teaches). All four quotes verified in the judge's re-opens (§5): S368 in the normalized man-page text and the local capture (`52cbc190…`, occurrence 1); S369 in `monitoring.txt` ("An exception is handled."); S370 in `os.txt` ("Set the blocking mode of the specified file descriptor."); S371 in `subprocess.txt` (22-word start_new_session sentence). All ≤25 words and located.
- `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → EXIT 0 (94 W04 cross-scope duplicate-URL warnings, all pre-existing and expected).
- Knowledge entries: `deadline-owned-reaping.md` (new, S367/S368) and `crash-channels-beyond-excepthook.md` (r96 audit) cite S368/S369–S371 correctly and withdraw the two false clauses. The `write(2)` EAGAIN candidate is screened with a flip condition — candidate admission discipline held.

## No owned axis harmed (other than the graded trade)

- `git diff 689d1c95 2bbbab6d -- SCORECARD.md` touches only the r96 measurement rows, the one capability row, and `Planned (r97)`. No other axis row rewritten. Scores unchanged: calibration 7, operability 8, coverage 8.
- No exploratory claim was declared; the "exploratory" clause does not arise.

# 4. Per-axis grades and verdict

| axis | grade | basis (re-measured) |
|---|---|---|
| calibration | **harmed** | Trade measured by judge: t1/t4 70→0 (right) vs modfin/reraise 70→1 (wrong). Admission rule (no axis harmed) fails; report and SCORECARD agree. |
| operability | **improved** | T1 hung→exit 2 + FATAL; conform 19→20/20 re-measured by judge (165 s). Narrowed reading A4/A5/A7 honored. |
| coverage | **unchanged** | Registry 286→293 is a frontier/source delta, not a coverage move; no coverage gain or loss measured this round. |

**Verdict: rejected-harmed.** C1 `harmed` (trade) is the dominant verdict; C2 verifies on the narrowed reading. Per PROTOCOL admission: "a trade anywhere is not an improvement" and "every claim verifies **and** no axis is harmed" — the calibration harm alone bars admission; the operability gain is real but does not cure the trade in the same round. The round is astringent honest-stop evidence of the defect, not a failure of honesty: the lane predicted the trade, measured it in both directions, and requested an operator ruling (Open L0 #1).

# 5. Discernment spot-check (LEARNING.md)

Re-opened ≥1 admit and ≥1 reject from `corpus/lessons/round-96.md ## Gate`, plus ≥1 newly written SOURCES row.

| item | lane decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| Admit — S368 (setsid(2), tier A) | opened + mined; teaches the process-group fact | `https://man7.org/linux/man-pages/man2/setsid.2.html` § DESCRIPTION, live re-open 2026-11-09 (judge) | **agree** | Quote matches byte-for-byte in the normalized page ("The calling process also becomes the process group leader of a new process group in the session", 17 words, DESCRIPTION). Capture sha256 `52cbc190…` matches the committed `census/round-96/srcs/setsid.2.html`. Teaches cell is now accurate. |
| Admit — S369/S370/S371 superseding rows | S365–S367 teaches corrected; rows authored to what the quotes carry | `corpus/SOURCES.md` S369–S371 & lesson Gate table | **agree** | Each quote located in its capture (monitoring/os/subprocess `.txt` verified above). The supersessions correct prior over-claims (S365's "finally does not stop termination" was the claim predicate, not the page's text) — a genuine discernment act: the lane admitted its own prior over-claim. |
| Reject/screen — `write(2)` EAGAIN candidate | screened, not rowed; flip condition stated | Lesson Gate lines 27–30 + `write.2.html` (pledged); capture not landed because the row was not written | **agree** | Reason is specific and checkable: "the corpus has no row that needs its scope this round"; flip names the claim that would need it. A rejection grounded in current need, not in topic avoidance. |
| (corroboration) Reject-arms Ga/GB/GC | forgeries refused 3/3 | P2 `controls/c2-forgery-controls.txt` + probe code | **agree** | Each arm's control receipt exists and the refusals are the frozen strings (`GA conform=19 exit 2`, `GB S9 exit 1 / S10 exit 0`, `GC S12+T1 exit 2 hung arms`). The S12 GC refusal is the same transient as A8; the control table is intact. |

Discernment overall: **improved**. The spot-check agrees with the gate on both an admit and a reject, and the S369–S371 supersessions are cases where the gate's own prior teaching was corrected by new evidence — the Lern-style evidence that discernment is exercised. No disagreement audit outstanding; the r97 routed items name concrete QUALITY criteria (RERAISE-aware predicate, traceback-print path, fd-2 restore) that need grounding in r97 evidence, not grounding-less rules.

# 6. Trend verdicts (matching the lane's where independent)

- **expansion: improved.** New knowledge entry `deadline-owned-reaping.md` on previously uncovered reaping ground, citing mined tier-A row S368; registry 286→293 with quote-verified S369–S371 corrections. Frontier rows advanced, not just row-count.
- **quality: improved.** C2 moved T1 from `hung` to exit 2 + FATAL (19→20 conforming arms, re-measured by judge). Two false corpus clauses and the "cannot block"/"momentarily" wordings withdrawn. No admitted entry fails its re-check (the withdrawn entries are superseded, not left false).
- **discernment: harmed** (agreeing with the lane). C1 calibration is a measured trade; the discernment being harmed is the same fact grading calibration. The verdict matches the lane's trend row; the harm is fixed or routed at r97 (RERAISE-aware rule + table shapes), not left unlearned.

# 7. Routed defects and r97 items

1. C1 trade to resolve (plans/round-96.md A1, report Open L0 #1): r97 attempts the RERAISE-aware rule plus the two terminating shapes added to the table before any calibration claim on the EH leg. Operator ruling requested on "admit as harmed-not-admitted vs require the r97 fix".
2. Reaping authority (report Open L0 #2, PROVINCE F5 HOLD): may the lane kill its own arm grandchildren by identity (per-arm absolute fixture path)? Routed to r97 as an L0 item; the two orphan kills this round (PIDs 2085368, 2254969, SIGKILLed by the L1) are on the record.
3. Host signal (report Open L0 #3): unattributed SIGTERM on S12 in three first runs (post-arms, r95 control, MutC2 baseline). Flagged for the fleet operator; no lane action until answered.
4. Spec-writer seat-count line (12 vs 13, A0.2) — fix the count, not the seats, next round.
5. Wave evidence durability (`.ufo/waves/` git-ignored in the lane) — recommend a committed capture step or an explicit retention decision; the judge re-opened the live checkout, but a cold restart loses the audit trail.
6. r97 claim shaping (plans/round-96.md Planned (r97)): A2 excepthook/thread traceback routing, A3 fd-2 restoration, A4 identity-based reaping + survivor count, A5 output cap, A8 signal-exit recording with distinct handling. None is a claim acceptance; they are technique improvements that need the same pre/post controls.

# 8. Artefact and promotion notes

- SHONEN boxes: all `[~]`. No box is `[x]`. Correct on the record: no non-author has verified the promotion claims (wave seats are conductor seats, not the protocol's non-author for promotion). Promotion is operator-owned; the judge records that the boxes look verifiable by a non-author when the axes settle (the C1/C2 instruments already print checkable before→after numbers, and the wave's attack seats exercised them). This is not a promotion recommendation — the C1 trade bars rights-admission this round, and promotion (shokunin → jin'i-ryū) requires its own gate plus an artifact-certified improvement recorded in LOG.md.
- `census/round-96/run-receipt.sh` is committed at `0656de3f` (tracked) and present at `2bbbab6d` (verified via `git show 2bbbab6d:census/round-96/run-receipt.sh`); the per-claim scratch outputs and receipt headers are the cited evidence. The report is `ok`, not `failed`; it is not a marker.
- The awarded claim is C2 verification on the narrowed reading; rejected-harmed is the round verdict because C1 is a true trade. The lane's severity is self-assessed and confirmed by this judge’s re-derivation.
