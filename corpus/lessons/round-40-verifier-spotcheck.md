author: hyaku closure (non-author integrator, @m_zfl)

# Round 40 — non-author closure spot-check (souji)

Lane HEAD measured: `bffcc0f660ff36eb8add3f61582748a7af019a5b` (before: `be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e`). Date: 2026-10-28.
Scope: read-only re-measurement over committed bytes (`git archive bffcc0f` into a scratch tree outside the lane) and live source re-opens. Nothing lane-authored was edited.

## 1. Step-1 conformance

| check | command | observed |
|---|---|---|
| report committed by lane identity | `git log --format='%an %H' -- .ufo/reports/round-40/souji.md` (fleet) | `souji-shokunin 4024919c57562b54171057880649e26166da6b11` |
| `SHONEN` heading, one line per box | read report | present; four `[~]` boxes, each with a pointer |
| every cited lane commit an ancestor of `master` | `git merge-base --is-ancestor <h> master` for all 10 cited hashes | all 10 `ok` (`128e412`, `8a5fbdb`, `6ded124`, `556c24a`, `549d9ec`, `994de3b`, `42e18ed`, `dc8bd47`, `d86ef3e`, `bffcc0f`) |
| lane pushed, clean | `jj-lane.sh state` | `local=remote=bffcc0f… ahead=0 behind=0 tracked=0 untracked=0`; `git status --porcelain` empty |
| fleet L0 correction cited | `git merge-base --is-ancestor a8663a8 HEAD` (fleet) | `anc` |
| prompt carries template contract | not re-opened in depth; status-neutral | no defect found |

Notes (status-neutral): attempts 1 and 2 landed no report (watchdog digest in MANIFEST notes); the report is attempt 3. The report's own disclosure that the two-v2-wave shape is neither canonical shape is a conformance note, not a bar. Attribution: all 11 lane commits in the range are authored `souji-shokunin`.

## 2. Per-claim re-check

All three claims are, by the lane's own report and `corpus/lessons/round-40.md` M40-3…M40-13, declared **unprovable** against their frozen preregistration (population/pair set/base fixture not frozen before seat scoring). I did not re-litigate that; I re-measured what I could and ruled on the better/not question.

Gate rule (PROTOCOL §Gate standard, Closure consequence): the three `census/round-40/*-counter.py` scripts are lane-owned instruments. I did NOT execute them; I verified their committed receipts. I DID run the lane's committed fixtures (they are fixtures over isolated trees, not the sibling gate) from a scratch archive of `bffcc0f`.

| claim | before → after reported | my measurement | re-measured vs evidence-verified |
|---|---|---|---|
| C1 calibration (evidence-bound closure lines, strict-descendant register) | `items=3 open=3` at base → `items=3 open=0 forged=3 forged_open=3 forged_closed=0 register_violations=0`, fixture `cases=11 pass=11` | `git show bffcc0f:census/round-40/records/c1-before.txt` ends `SUMMARY items=3 open=3 … counter exit: 1`; `c1-after-h.txt` ends `SUMMARY cases=11 pass=11 fail=0`; control `c1-control.txt`: r39 counter `ITEM FORGE-TOKEN CLOSED`, r40 counter `ITEM FORGE-TOKEN OPEN EVIDENCE-NOT-BOUND`. Ran `python3 -B tests/fixtures/r40-c1-evidence.py --work <dir>` → `SUMMARY cases=11 pass=11 fail=0` | fixture RE-MEASURED (11/11); counter receipts EVIDENCE-VERIFIED (before/after/control) |
| C2 operability (joined docstring class reader) | one-line `cases=9 pass=6 fail=3` → joined `9/9`, counter `legs=7 pass=7 fail=0 harm=0` | `r40-docstring-joined.py` → `SUMMARY cases=9 pass=9 fail=0`; `--one-line` → `SUMMARY cases=9 pass=6 fail=3`. Receipt `c2-after-h.txt` ends `SUMMARY legs=7 pass=7 fail=0 harm=0`; L6 regression leg lists all seven prior fixtures at base parity (10/10, 12/12, 12/12, 7/7, 16/16, 14/14, 8/8) | fixture RE-MEASURED (9/9 vs 6/9); legs EVIDENCE-VERIFIED |
| C3 coverage (record-branch battery) | base arm kills 0 of 4 new mutants → `mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8` | `r40-drift-record-branches.py` → `SUMMARY cases=8 pass=8 fail=0`; `c3-after-h.txt` ends the reported SUMMARY and attributes M15→total-conflicting-second, M16→4 cases, M17→invalid-utf8-in-repo-name, M18→total-repos-disagrees, each `base_killed=no` | fixture RE-MEASURED (8/8); mutant kill table EVIDENCE-VERIFIED (receipt names measured_at `dc8bd47`, base `0242085`) |

Defect found in report prose: the report's C1 "before" cell reads `SUMMARY items=3 open=3` (matches `c1-before.txt`), but `c1-before.txt` and `c1-after-h.txt` ran with different register files (`census/round-39/cells.tsv` vs `census/round-40/cells.tsv`, `register_cells=6` vs 3); the before→after on the register arm is therefore not like-for-like. The lane's own M40-5/M40-6 already say the three-row measure is bounded and coupled (D2 cites `6ded124`, which carries the C2/C3 receipts). Agreed.

Admission rule: "admitted only if every claim verifies". The lane declares all three frozen claims unprovable and my re-measurements confirm the gaps they name (population, pair set, base-fixture identity are not in `preregistration.txt`; its C1 paragraph says "each anchored item line" with no item-table digest). Verdict: **not admitted**, honest stop. No axis harmed.

## 3. Per-axis verdicts

`git diff be4cb61 bffcc0f -- SCORECARD.md` is pure append (+36 lines, 0 deletions): Round 40 closure cells, measurements, capability rows, plan, finality correction, final census. Owned scores unchanged (calibration 7, operability 8, coverage 8); no score mapping is claimed. `corpus/QUALITY.md` +18 lines, `tools/` unchanged (no tool edit this round).

| axis | verdict | reasons |
|---|---|---|
| calibration | **unprovable-but-better** | Frozen claim not verifiable (M40-5/6). But a real, controlled improvement is observable: the r39 counter closes a token-only forged line, the r40 counter rejects it as `EVIDENCE-NOT-BOUND` (`c1-control.txt`); the fixture proves wrong-value/non-ancestor/equal/backwards commit rejection, 11/11 re-run by me. Hardening landed after wave data, so no retroactive admit. No existing check regressed. |
| operability | **unprovable-but-better** | Frozen pair set/join grammar unfrozen (M40-3), counter tests 3 of 10 refusal classes. The joined reader does read wrapped refusal-class entries the one-line reader misses (9/9 vs 6/9, re-run by me); the L6 leg shows no prior fixture regressed. |
| coverage | **unprovable-but-better** | Frozen "r39 base fixture" ambiguous (M40-4); fixture under-asserts U+FFFD (M40-12) and omits first-disagreeing/last-agreeing TOTAL order. Still, branches that had no case (multiple TOTAL, `--skip-unrecorded`, invalid UTF-8) now have load-bearing cases with per-mutant attribution (8/8 re-run; 4/4 kill receipt vs `base_killed=0`). Net coverage strictly higher than base; known gaps are disclosed, not hidden. |

No `harmed`: no scored axis lost an observable it had. "Could not re-open" was not needed anywhere.

## 4. Discernment spot-check (LEARNING.md)

Sample from `corpus/lessons/round-40.md` `## Gate`.

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| staged `origin-record-format-gvfs-r26.md` → lane S254 (+S257 narrowing) | ADMIT | live `https://raw.githubusercontent.com/GNOME/gvfs/1.62.0/daemon/trashlib/trashitem.c` (fetched now; sha256 `3a8f8cbb…25b` equals the lane's `SHA256SUMS` row); lines 158, 173, 180, 182, 193, 176 read | **agree** | Quoted line 158 `trashinfo = g_strdup_printf ("%s/info/%s.trashinfo", …)` is verbatim; 173 reads `"Trash Info", "Path"`, 180 `g_uri_unescape_string`, 182 `g_path_is_absolute`, 193 `"Trash Info", "DeletionDate"`; line 176 `if (orig == NULL)` confirms S257's correction that the reader tolerates a missing Path. Admit is sound as corroborative F4 ground; the lane correctly claims no expansion credit. |
| staged `near-duplicate-operating-point-r28.md` (S172 Manku et al.) | REJECT | lane `PROVINCE.md` "Round 29 boundary note" lines 183-187, plus package `SOURCES.append.md` row S172 | **agree** | PROVINCE explicitly excludes a near-duplicate threshold ("document-similarity ground sits outside this frontier's byte-identical scope"); S172's own scope says "NOT a threshold for souji (that is an operator ruling)". Reject reason is grounded and the flip condition is named. |
| staged `fleet-prune-safety-r28.md` (S160 git v2.56.0 `worktree.c`) | REJECT ("lane already holds git's prune gate: `worktree.c` appears in 9 rows") | lane `corpus/SOURCES.md` at `bffcc0f`; package `SOURCES.append.md` S160 | **disagree in part** | The decision may be defensible but the stated reason does not reproduce: `git show bffcc0f:corpus/SOURCES.md \| grep -c 'worktree\.c'` = 3 (only S009 actually cites `worktree.c`; S033/S058/S232 match as worktrees pages), and `grep -c 'v2.56.0/worktree.c'` = 0. The lane holds the gate only at v2.55.0 (S009: `worktree.c:954-956, :1001-1008`), whereas staged S160 is explicitly a v2.56.0 RE-PIN "because S009 … carries a pending-recheck note for v2.56.0". That is a freshness gain on held ground, not a duplicate. Rejecting on an unreproducible count with no check of the re-pin purpose is an uncalibrated gate call. |
| newly written `corpus/SOURCES.md` row S255 (supersedes S252) | quote check | live `https://docs.python.org/3/library/inspect.html`, tag-stripped text | **agree** | "Any leading whitespace that can be uniformly removed from the second line onwards is removed." is present verbatim (15 words ≤ 25). The superseded S252 quote ("Any whitespace that can …") is confirmed ABSENT from the page, so the correction was warranted. |
| newly written row S256 (supersedes S253) | quote check | live `https://docs.python.org/3/library/codecs.html` | **agree** | "On decoding, use � (U+FFFD, the official REPLACEMENT CHARACTER)." present verbatim (9 words). |
| row S251 | quote check | installed `man git-merge-base` (git 2.56.0) lines 41-43 | **agree** | "Check if the first <commit> is an ancestor of the second <commit>, and exit with status 0 if true, or with status 1 if not" present (whitespace-folded). |

Census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → exit 0, `souji ok …/corpus/SOURCES.md`, 52 `W04` duplicate-url lines (equals the reported W04=52). Row count at `bffcc0f`: `git show bffcc0f:corpus/SOURCES.md | grep -c '^| S[0-9]'` = 181 (base `be4cb61`: 174). Seven rows added (S251-S257), matching the report.

## 5. Trend verdicts

- **expansion — unchanged.** Seven rows were added, but the lane concedes (and I agree) that GVFS read-side material is corroborative on held F4 ground; no coverage-map ground moved to Core; no admitted entry fails its bar.
- **quality — improved.** Two source quotes (S252, S253) were non-verbatim; W2 found them, and the exact superseding rows S255/S256 plus S257 (narrowing S254's "mandatory field" overclaim) were appended without rewriting history. I re-opened both quotes live (§4). QUALITY Q89-Q97 exist at `bffcc0f` (`grep -n 'Q9[0-7]\|Q89'`), each citing a lesson. The TOTAL docstring/runtime discrepancy is disclosed, not hidden.
- **discernment — unprovable-but-better.** Outside check: 1 admit agree, 1 reject agree, 1 reject disagree-in-part, 3 quote re-opens agree. The lane's wave findings became lessons M40-3…M40-13 and grounded criteria Q93-Q97 (the table's `improved` path). But the one reject whose count I could not reproduce has not yet become a lesson, so I cannot grade `improved` on this round's evidence alone; the disagreement is routed below.

## 6. Routed defects (lane must fix next round)

1. **R40-D-PRUNE (discernment, own-repo).** `corpus/lessons/round-40.md` § Assimilation gate states `worktree.c` "appears in 9 rows"; measured 3 lines contain the string `worktree.c` (1 row, S009, actually cites the file; 0 at v2.56.0). Append a correction entry (never rewrite) re-deciding the staged S160/`fleet-prune-safety-r28.md` item as a v2.56.0 re-pin of the recheck-pending S009, with the counting command; add a QUALITY criterion that a reject by "already held" cites a reproducible count and compares version/scope, citing this spot-check.
2. **R40-D-C1-BEFORE.** Report/SCORECARD C1 before→after compares `c1-before.txt` (register `census/round-39/cells.tsv`, 6 cells) with `c1-after-h.txt` (register `census/round-40/cells.tsv`, 3 cells); state per-arm like-for-like inputs or run the before arm on the same register file.
3. **R40-D-FREEZE (carried by the lane's own plan, confirmed).** The r41 plan must commit, in `preregistration.txt` before dispatch: the C1 item inventory + digest, the full C2 class/trigger/probe list and join grammar, and the exact C3 base fixture path+digest including TOTAL ordering and U+FFFD value assertions (Q93-Q96).
4. **R40-D-TOTAL.** The `tools/souji-worktree-drift.py` TOTAL-handling discrepancy against its docstring (M40-4/M40-13) is a tool defect awaiting a separately frozen repair; keep it on the routed queue until a correction lands.

## 7. Notes for the operator

SHONEN boxes in the report are all `[~]`; none is fully checkable by a non-author from this round's evidence. I wrote no `[x]`, promoted nothing, minted nothing, touched no other lane.
