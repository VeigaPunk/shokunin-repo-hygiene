author: hyaku closure (non-author integrator, @m_zfl)
round: 66 (souji) — non-author closure spot-check
date: 2026-11-05
report: .ufo/reports/round-66/souji.md (fleet repo, commit dd867c52 by souji-shokunin <souji@shokunin.local>)
lane HEAD before → after: 045e103478fa4a7eff77db2cab5b9e2f26959a0a → b238ab1da21776c2c6e9286a8fd20e0343a14131

## Conformance results

| check | result | evidence |
|---|---|---|
| report committed by lane identity | PASS | `git log --format='%an <%ae> %H' -- .ufo/reports/round-66/souji.md` → `souji-shokunin <souji@shokunin.local> dd867c520cac0256e1a6107ac264df2eee4a9f2d` |
| `SHONEN` heading, one line per box | PASS | report `## SHONEN` + four `[~]` lines, one per SHONEN.md box (4/4); no `[x]` written by the lane |
| every cited lane commit exists and is an ancestor of the branch | PASS | `git -C souji-shokunin merge-base --is-ancestor <h> master` for 045e1034, 4576f101, 4864c01f, 5d17a5de, 01bc1e16, a81280e1, 02cc6609, c13fbb4e, b238ab1d — all ANCESTOR-OK (branch ref, not `@{u}`; HEAD detached, jj-colocated) |
| lane repo clean and pushed | PASS | `scripts/hyaku/jj-lane.sh state` → `local=b238ab1d… remote=b238ab1d… ahead=0 behind=0`; `git status --porcelain` → empty |
| dispatched prompt carries the template contract | PASS | `.ufo/prompts/souji-round-66.md` sections 1–5 render `templates/round-prompt.md` verbatim (diff shows only `{{AXES}}`/path placeholder substitutions); hyaku addendum §6 appended; L2 floor "at least 8 … ONE batched AgentSwarm call" matches `MISSION.md` §L2 concurrency |
| report lands last | PASS | lane HEAD commit 12:26:40 -03:00 (b238ab1d) < report commit 12:28:20 -03:00 (dd867c52) < watchdog complete 12:28:46 |
| dispatch/complete digest | PASS | watchdog.log: `2026-11-05T11:26:04-03:00 launch souji round=66 pgid=343123 driver=hyaku-inline attempt=1` / `2026-11-05T12:28:46-03:00 complete souji round=66; hyaku-inline attempt=1` (copied to MANIFEST notes) |
| marker rule | PASS | real report: two declared claims, committed work, evidence pointers, all six required sections present — not a marker |

## Per-claim re-check (evidence-verified, gates not executed)

Both claims rest on lane-owned registered gates (`c1-counter.py`, `c2-counter.py`, registry rows in lane `SKILL.md`). Per PROTOCOL §Gate standard (Closure consequence) their committed evidence was verified; the gates were not executed by this spot-check.

**C1 — operability (receipt env-route and mode refusal), measured at `c13fbb4e`:**

- Receipts: `census/round-66/controls/c1-do-nothing.txt` `SUMMARY matrix=28 base_forgeries=8 base_honest=5 new_forgeries=8 new_honest=5 class_mismatches=8 regress=PASS` EXIT=1; `census/round-66/records/c1-after.txt` `new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS` EXIT=0. Both carry rev/instrument/instrument_sha256/command headers; instrument sha256 `273d6fc9…f1490` matches the committed `census/round-66/c1-counter.py` byte hash (`sha256sum`). Counter-internal stub control tallies committed inside both receipts (`# regress-detail … cases=8 pass=8 fail=0`).
- Plain measurements run by this spot-check: matrix `wc -l` 29 = header + 28 rows (23 refuse / 5 accept); `git show c13fbb4e:tools/souji-receipt-write.py | sha256sum` = `a8c47d36…97fc` = working-tree bytes = the report's cited candidate sha; writer bytes grep-verified: presence-based name-only refusals of `GIT_CONFIG_COUNT`, `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_KEY_*`, `GIT_CONFIG_VALUE_*` (`RECEIPT-ENV-CONFIG-SET`) and `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_REPLACE_REF_BASE` (`RECEIPT-ENV-REDIRECT-SET`); `GIT_CONFIG_GLOBAL` pinned to `os.devnull` and `core.excludesFile` pinned via `-c` on every git call; in-run mode snapshot `st_mode & 0o7777`; `GIT_COMMON_DIR` absent from the refusal list (the W2 named limit is real, not an oversight).
- Writer selftest receipt committed: `SELFTEST cases=33 pass=33 fail=0` (r66 cases env-config, env-redirect, mode-bits included).
- Frozen target met. Held-out defects (lane's own committed probe `census/round-66/probes/w2-w3-env-probe.txt`): W2 `GIT_COMMON_DIR` route open on the candidate (rc 0 with a tracked 755→644 change hidden); W3 honest-run refusal trade (writer under `git -c`: candidate rc 2 `RECEIPT-ENV-CONFIG-SET` vs base rc 0). Setgid row unmeasured (lesson named limit). Receipt-grammar defect disclosed: `c1-after.txt` first line is the base revision, so `tools/souji-freeze-check.py --chronology` reports `RECEIPT-MEASURED-BEFORE-FREEZE` (rc 1) at `b238ab1d` — a red lane-owned check, status-neutral, routed r67.

**C2 — calibration (SKILL statement population s1–s5 + M-ENV kill), measured at `c13fbb4e`:**

- Receipts: `census/round-66/controls/c2-do-nothing.txt` `rows=5 findings=1 verdict=FAIL` EXIT=1 (s5 absent at base); `census/round-66/records/c2-after.txt` `rows=5 findings=0 verdict=PASS` EXIT=0; instrument sha256 `ac2157e6…25c67` matches committed `c2-counter.py`; `records/c2-selftest.txt` `cases=14 pass=14`.
- M-ENV kill receipts: `records/c2-mutant-m-env.txt` — round-66 counter on scratch mutant `0c8c5f4b` `findings=1 verdict=FAIL` (`SCOPE-OVERREACH s2`, `env=0`) EXIT 1; round-65 counter on the same mutant `findings=0 verdict=PASS` EXIT 0. The round-65 M10 blind spot is genuinely closed.
- SKILL s5 present in landed bytes (SKILL.md r66 section, "Env routes, round 66 …"); population `census/round-66/c2-statements.tsv` 5 rows s1–s5.
- Claim defects (disclosed by the round itself): M4 the `m10-returncode-line-not-live` selftest case binds row s3 and is vacuous (repair-reverted selftest still 14/14); M5 s5's universal wording ("closed for the caller-injected config and object-redirect routes") is overreach the lexical counter cannot falsify — the W2 route is the falsifier; critic: C2 not separable from C1. Q129's correction exists only as the lesson append; `corpus/QUALITY.md` still cites the vacuous case and must reflect the correction by r67 (LEARNING.md operator-teaching/correction duty).

No owned axis harmed in SCORECARD: `git diff 045e1034 b238ab1d -- SCORECARD.md` is additions-only (registry row, Round 66 measurements, planned r67); axis scores unchanged (calibration 7, coverage 8, operability 8). `corpus/README.md` diff empty (no coverage-map ground moved).

## Per-axis verdicts

| axis | verdict | reason |
|---|---|---|
| operability | harmed | The frozen 28-row predicate verifies (8→0 forgeries, honest 5/5 kept, receipts + byte hash + static refusal list all verified). But the round's own held-out probe shows a refusal cost on honest runs (`git -c` child: candidate rc 2 vs base rc 0) and an open `GIT_COMMON_DIR` route that hides a tracked mode change — a measured trade on the axis's own surface; AXES.md: a trade anywhere is not an improvement (chousa-r47 precedent shape: frozen predicate verifies, held-out trade → axis not improved). |
| calibration | unprovable | The M-ENV kill receipts verify and the s1–s5 lexical agreement verifies, but the claim's guard is vacuous (M4: the selftest case binds s3, not the M10 line) and the landed statement s5 overreaches its falsifiable scope (M5; the W2 route falsifies the universal wording; critic's would-reject stands; not separable from C1). The lane itself files it "not admitted as scope-correct". |
| coverage | unchanged | No coverage-map row moved (`corpus/README.md` diff empty); no frontier row advanced; axis score 8 unchanged. |

Round admission: every frozen predicate verifies, but a measured trade on operability and the calibration scope defects bar admission ("no axis harmed" fails); the lane stopped honestly (all defects disclosed in the report, lesson named limits, L0 rulings 360–362 filed, remedies routed r67).

## Spot-check table (LEARNING.md — gate decisions vs outside re-open)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S298 git(1) § ENVIRONMENT VARIABLES | admit, tier A, `mined` | live https://git-scm.com/docs/git (HTTP 200, 244227 bytes — byte-count identical to the committed capture `census/round-66/sources/git-environment.html`) | agree | Quote `If the object storage directory is specified via this` (9 words ≤25) present on the live page and byte-exact at capture offset 30753 (`git-environment.txt`); capture sha256 `624e85ef…8035` matches the SOURCES row. |
| S299 git-config(1) § ENVIRONMENT/FILES/SCOPES | admit, tier A, `mined` | live https://git-scm.com/docs/git-config (HTTP 200, 830605 bytes — identical to committed capture) | agree | Quote `If GIT_CONFIG_COUNT is set to a positive number, all environment pairs` (11 words ≤25) present on the live page and byte-exact at offset 20918 in `git-config.txt`; sha256 `dfc44574…6054` matches the row; core.excludesFile quote verified at offset 103037. |
| "GIT_CONFIG_PARAMETERS is a documented variable" (rejected inside the entry) | reject | live re-open of both pages plus committed captures | agree | `GIT_CONFIG_PARAMETERS`: 0 hits on both live pages today and 0 hits in both committed captures — the rejection reason holds. |
| newly written SOURCES row S298 quote check | (row audit) | `corpus/SOURCES.md` line 257 + `census/round-66/sources/quotes.tsv` | agree | Located quote with UTF-8 byte offset, line number, section and access date present; 9 words ≤25; offset slices byte-exact (all 9 round quotes re-sliced MATCH). |

New SOURCES row census: 220 → 222 rows re-measured (`grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}'` at base vs head); `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → rc 0, final line `ok` (pre-existing W04 duplicate-URL warnings continue; S298/S299 add two more in the same pre-existing class — status-neutral).

## Trend verdicts

- **expansion: unchanged.** `corpus/README.md` diff base→head is empty (no coverage-map ground moved); 220→222 registry rows; one knowledge entry (`corpus/knowledge/caller-env-routes-receipt-writer.md`, F4-adjacent, provenance trio present citing S298/S299); no frontier row advanced. Matches the lane.
- **quality: improved, with a disclosed trade.** Frozen-matrix forgeries 8→0 with honest accepts kept 5/5 (evidence-verified); no admitted entry failed a re-check; the honest-run refusal cost and the open `GIT_COMMON_DIR` route are disclosed in committed artifacts (probe, lesson named limits, SCORECARD gate row, L0), not hidden. The trade blocks round admission but the writer's refusal capability deepened on committed evidence. Matches the lane.
- **discernment: unchanged.** This spot-check agrees with the gate on the sampled admits and reject, but the round's own guard for its kill-power claim was vacuous (M4) and the s5 overreach was caught by the critic, not by a criterion (`captured-by: none`); no grounded QUALITY criterion landed from a disagreement this round; M4/M5 routed. Matches the lane.

## Routed defects (lane must fix in round 67)

1. New frozen counter (not an amendment) fixing M4: a selftest row bound to the M10 line that fails on the reverted repair; corrected C1 docstring (M6) and s4 note (M7).
2. Route sweep of git's environment surface as a frozen enumeration with do-nothing control and a `GIT_COMMON_DIR` / repository-local `core.fileMode=false` mode-hiding fixture (W2).
3. Population row that can fail on scope (M5); s5's SKILL wording — operator ruling pending (L0 362).
4. Operator rulings: honest-run refusal under `git -c` (W3, L0 360); repository-local key scope (L0 361); E3 `GIT_CONFIG_GLOBAL` "refuses" vs repoint wording (M8).
5. Receipt grammar in `c1-counter.py` (after-receipt names the base revision first, tripping `freeze-check --chronology` RECEIPT-MEASURED-BEFORE-FREEZE rc 1 at `b238ab1d`) — disclosed, red lane-owned check, status-neutral.
6. Kill-power fixtures for surviving mutants K3, K4, K6, K7 or a recorded defence-in-depth decision.
7. QUALITY.md must reflect the Q129 correction (lesson append) by r67, citing the lesson (LEARNING.md correction duty); it still cites the vacuous selftest case.

## Notes for the operator

- SHONEN.md boxes (4) all carry `[~]` with resolvable pointers; they look fully checkable by a non-author verifier (promotion remains operator-owned). No `[x]` was written by the lane or by this spot-check.
- Wave w1 role mix (10 seats, attack 5/10, band 8–16) runs one executor and holds the planner with the L1 ("validator refuses planner") — standing disclosed practice, below the template's 3× executor / 1× planner minimum split; status-neutral, recorded for the route-map owner.
- Report wording says "SCORECARD round-66 table and capability row": no `## Capabilities` repertoire row was added; the new row is a gate-registry row. Minor wording note, artifact exists.
- Route map quoted in the dispatched prompt (run-15 restored split, zai-quota failover lines) is an addendum carrier; the L2 floor matches MISSION.md's ≥8 one-batched-call bucket.
