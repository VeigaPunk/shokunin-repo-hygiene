# Round 86 verifier spot-check — non-author closure

author: hyaku closure (non-author integrator, @m_zfl)
closure date: 2026-11-08; lane souji round 86; base 89d02c907d40cc09fedc9d420cf9509df685e143; tip 1c3a1d417302bb2c5e3db6e924390ca9b1e7ddf9

## Step-1 conformance

| check | result |
|---|---|
| report committed in fleet repo by lane identity | pass — `souji-shokunin c9e4fd5d55c09242ba6e539bae867749727c1275` (final), `3b6fccba` draft; `git log --format='%an %H' -- .ufo/reports/round-86/souji.md` |
| SHONEN heading, one line per box | pass — `## SHONEN` at report line 158; 4×`[~]` lines with evidence pointers, none asserted `[x]` |
| every cited lane commit exists; merge-base ancestor vs branch | pass — `47602fa6 d77b4258 2acbbfc8 f5e196a2 12d320dc 90afc14a 1c3a1d41` all exist; `git merge-base --is-ancestor 89d02c90 1c3a1d41` ok; `1c3a1d41` ancestor of `master` ok (head detached, branch-tested) |
| lane clean + pushed | pass — `jj-lane.sh state`: `local=remote=1c3a1d41 ahead=0 behind=0 tracked=0 untracked=0`; `git status --porcelain` empty |
| prompt carries template contract | pass — `.ufo/prompts/souji-round-86.md` has MISSION/AXES binding, 1–3 claims, L2 floor, report contract with SHONEN/commit-hash items, commit-then-push + push scope + L0 channel, `Assimilation: none` line |
| marker vs report | not a marker — report names real committed work, work performed, evidence pointers, LOG-tied landed changes, commit-hash citations |
| dispatched prompt window | watchdog lines captured in manifest notes (launch 2026-11-08T05:35:40-03:00, complete 06:20:51-03:00) |

Defects (status-neutral): see Routed below.

## Per-claim re-check

### C1 — calibration 7 (clause-grounding with row pair)

Counting command (frozen, one per end):
`python3 -B census/round-86/c1-clause-battery.py --counter census/round-86/c1-pointer-counter.py --work WORK --only r85,r86 --expect-killed 14` (after);
same with `--only r85 --expect-killed 6` (before).

Observed vs reported:

| end | receipt | observed (cross-read byte-for-byte + independent harness re-derivation) | exit | verdict |
|---|---|---|---|---|
| before (do-nothing: 8 mutants on r85 47 rows) | `controls/c1-before-r85-population.txt` | `ARM pristine pop=r85 rows=47 mismatches=0 errors=0`; six `killed=yes`; `c7-census-in-tree killed=no`; `m14-short-shape killed=no`; `SUMMARY mutants=8 sets=r85 pristine_r85=ok killed_r85=6 killed_total=6` | 0 | AGREE — independently re-ran `--only r85 --expect-killed 6`: `SUMMARY mutants=8 sets=r85 pristine_r85=ok killed_r85=6 killed_total=6`, exit 0 |
| after (49 rows, r85+r86) | `records/c1-after.txt` | `ARM pristine pop=r85 rows=47 mismatches=0 errors=0`; `ARM pristine pop=r86 rows=49 mismatches=0 errors=0`; eight `killed=yes` on r86; `c7`/`m14` kill only on r86; `SUMMARY mutants=8 sets=r85,r86 pristine_r85=ok pristine_r86=ok killed_r85=6 killed_r86=8 killed_total=14` | 0 | AGREE — re-ran `--only r85,r86 --expect-killed 14` on committed bytes: same SUMMARY, `killed_r85=6 killed_r86=8 killed_total=14`, exit 0 |

Pinned digests cross-read: counter `8278ea4d…`, harness `2dac2e81…`, mutants `6f055ede…`, populations `1468236c…` (r85 47) / `79db70f6…` (r86 49), items `5abf3b01…` — all match receipt headers. Regressions: `c1-regress-r83-r84.txt` green, `killed_r84=5` unchanged baseline (cross-read). Pin refusals: both pin paths refuse rc 2 (`records/pin-refusals.txt`). Each new row is sole killer of its clause; neither row red for any r85 mutant; every kill is mismatch with `errors=0` (S86MutCounter §6–7, independently consistent with receipts).

Axis: calibration 7 — improved (verdict, not numeric delta; SCORECARD correctly carries verdict+counting command+measured commit, no 0–10 mapping change).

### C2 — operability 8 (index-flag sweep in K4 + one-line record paths)

Counting command (frozen):
`python3 -B census/round-86/c2-k4-counter.py --tool tools/souji-record-agreement.py --work WORK` (after);
`--tool census/round-86/controls/c2-before-base-tool.py` (before).

| end | receipt | observed | exit | verdict |
| before (lane-base tool `0ade0751…`) | `controls/c2-before-base-tool.txt` | `SUMMARY rows=9 mismatches=2 errors=0`; KG1 `k4=0 named=no match=no detail=''`; KG2 `named=no match=no`; seven r85 rows unchanged | 1 | AGREE |
| after (filed tool `cf875367…`) | `records/c2-after.txt` | `SUMMARY rows=9 mismatches=0 errors=0`; KG1 `k4rows=['.|index-flag-concealed']`; KG2 `named=yes`; seven r85 rows unchanged | 0 | AGREE — independently re-ran counter on filed tool: `SUMMARY rows=9 mismatches=0 errors=0`, KG1 `index-flag-concealed`, KG2 `named=yes`, exit 0 |

Writer `70bbf1c2…` byte-identical beside control (verified via receipt header). Wave repair: `c2-env-route.txt` `k4_rows_with_env` 0→1 on filed bytes (base bytes stay 0), `GIT_INDEX_FILE`/`GIT_OBJECT_DIRECTORY`/`GIT_ALTERNATE_OBJECT_DIRECTORIES`/`GIT_REPLACE_REF_BASE` stripped + `core.sparseCheckout=false` pinned — repair measured outside frozen counter whose `ENV` strips `GIT_*`, correctly disclosed. Real-lane: `--shared` clone at `2acbbfc8` reports no K4 row, only inherited K3 row (`c2-real-lane.txt`), S86ExecK4 §4 independently green.


Axis: operability 8 — improved.

## Pre-file falsification ledger (Amendment 59)

`python3 scripts/hyaku/prefile-falsification.py --lane souji --round 86` → `PREFILE-FALSIFICATION: pass claims=2 rows=14 attack_seats=5 findings=0`, exit 0. Ledger: 17 rows committed at `90afc14a` in the lane repo (`.ufo/waves/round-86/claim-falsification.tsv`, 209 wave paths durable at HEAD), covers both claims, reads all 11 seat artifacts, every `falsifies-wording` row names its narrowing in `plans/round-86.md` (A1–A11). No failing row; no unreconciled wording falsification. Attack seats present: S86Critic, S86Sentinel, S86MutCounter, S86Reviewer, S86Connector (connector neutral×2, falsifies-wording×1 — all accounted).

### No owned axis harmed

`git diff 89d02c90 1c3a1d41 -- SCORECARD.md`: no score change (calibration 7, coverage 8, operability 8 stand; lane has no reproducible 0–10 mapping). `git diff … -- PROVINCE.md`: 0 lines. Coverage axis untouched (no new surface claimed); no owned axis harmed on either claim. SCORECARD capability rows (two) each carry `what it can now do → evidence pointer → first-working round`, demonstrated in-round.

## Pre-file falsification ledger (Amendment 59)

`python3 scripts/hyaku/prefile-falsification.py --lane souji --round 86` → `PREFILE-FALSIFICATION: pass claims=2 rows=14 attack_seats=5 findings=0`, exit 0. Ledger: 17 rows committed at `90afc14a` (`.ufo/waves/round-86/claim-falsification.tsv`), covers both claims, reads all 11 seat artifacts, every `falsifies-wording` row names its narrowing in `plans/round-86.md` (A1–A11). No failing row; no unreconciled wording falsification. Attack seats present: S86Critic, S86Sentinel, S86MutCounter, S86Reviewer, S86Connector (connector neutral×2, falsifies-wording×1 — all accounted).

## Discernment spot-check (LEARNING.md)

Lesson `corpus/lessons/round-86.md` `## Gate` sampled: 3 admits, 2 rejects; each re-opened at its cap.

| item | lane decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S341 git-ls-files(1) `-t` tag legend | ADMIT `mined`, tier A | `census/round-86/srcs/git-ls-files.1.gz` capture, `zcat … \| grep -n` → roff line 193 “tracked file that is not either unmerged or skip-worktree” (rendered line 119) | AGREE | quote byte-exact (9 words ≤25); grounds the sweep's non-`H` decision rule — a real scoped teaching, source is the installed official man page |
| S342 git-update-index(1) skip-worktree bit | ADMIT `mined`, tier A | same capture → “Tell git to avoid writing the file to the working directory … and treat the file as unchanged …” (rendered lines 325–326) | AGREE | byte-exact (11 words); the flag's own contract makes the worktree change invisible to status — exactly the fail-open the repair closes |
| S343 gitsubmodules(7) gitlink entry | ADMIT `mined`, tier A | `census/round-86/srcs/gitsubmodules.7.gz` → “The gitlink entry contains the object name of the commit …” (roff grep) | AGREE | byte-exact (10 words); gitlink content is a commit id, not bytes, so no worktree hash can decide it — motivates the flag read |
| S344 git-ls-files(1) `--stage` | REJECTED (flip stated: unmerged stage triples/resolve-undo teaching) | same S341 capture → “Show staged contents' mode bits, object name and stage number …” | AGREE | quote accurate but scoped teaching restates S317 (index stat/object fields) + S327 (tree mode/type), stage number excluded by lane receipts — rejection is taste, counterexample (S317+S327) confirms |
| S345 git-update-index(1) `--assume-unchanged` promise (taken as admit) | ADMIT-scope B-side row, full row committed | same capture → “the user promises not to change the file and allows Git to assume …” (roff line 121) | AGREE (with anchor note) | quote ≤25 words, byte-exact modulo tail “in the index”; lane's S345 cell honestly marks “rounded lines 79-80 … justified spacing normalised” — anchor "rendered page lines" differ from roff line 121, a citation-precision nit, not a falsity |

Census: `grep -cE '^\| *S[0-9]{3,}' corpus/SOURCES.md` → 268 (263→268, +5: S341–S345, zero removed); `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → `souji ok`, exit 0, no `E0x` (87 pre-existing `W04` cross-scope duplicate-URL warnings, unchanged before→after).

## Per-axis verdicts

| axis | verdict | evidence |
|---|---|---|
| calibration | improved | C1 proven unexplained-by-rule: population freeze with do-nothing control, kills 6→8 with r85 kills retained, errors=0, frozen prior-art function audit (S86Connector §1) |
| operability | improved | C2 turns an invisible fail-open into a measured row (KG1 0→row), path-escape keeps records parseable, sentinel env-route closed and re-measured (0→1) |
| coverage | unchanged | No PROVINCE move, no frontier row to Core, curation-not-breadth (sources + instrument power); two knowledge sections extend held ground |

Trends: expansion unchanged (5 source rows + 1 frontier paragraph are curation; `grep -c 'r86' corpus/README.md` = 1 frontier block; PROVINCE 0-line diff) · quality improved (concealed class now refused; every kill a mismatch, errors=0; limits stated not claimed) · discernment improved (wave falsified 7 frozen sentences A1–A5/A9–A11, each narrowed in `plans/round-86.md` with killing artifact; 2 proposals withdrawn on measurement; r85 "literal LF" wording corrected to space-join). Trend verdicts in report agree with this table.

Claims: both re-measured independently (receipts cross-read + harness runs); neither claim rests on an unexecuted lane gate; A11 repair evidenced by `c2-env-route.txt`, not by the frozen counter. Any exploratory claim: none this round (both claims counted, neither exploratory).

## Routed defects (status-neutral, for r87)

5. Battery pin-exit/docstring drift (lesson M6): pin path exits 1 while docstring says 2 — fix exit code + docstring together and re-file receipts.
6. Dead arms/effective narrowing: c7 suffix test dead, guard `len(got) < 2` half dead (A3/A8 + `a6-len-got.txt`); delete or document as belts.
7. Carried population gaps: `NF-L3`/m12/m16/m17 half-clauses, NX3 int-round case, `w0/` wave-dir decision, five-path naming cap (A9), `FLAGFAIL` reachability (A5), writer 200-char stderr truncation (A7), pinned writer digest.
8. Inherited K3 tally row on lane's own tree (A4); r83/r84 C2 carried list (pid-reuse, parent-before-child, termign-fork/p5-late-term, strace settle).
9. Citation-precision nits: S345 "rendered lines 79-80" vs roff line 121; S343 "rendered lines 26-27" semantic not physical — prefer roff line anchors.
10. Lesson text A0–A5 vs plans A0–A11 count mismatch (truncated corner, no claim impact).

Conclusion: verifier independently confirms the round's before→after evidence; every claim verifies under Amendment 59's falsification surface, no axis harmed, sources census-clean, spot-check agrees on all 5 gate decisions (3 admits + 1 reject + 1 reject-taken). **admitted**.
