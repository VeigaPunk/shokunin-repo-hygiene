# S70Scribe — draft material for `corpus/lessons/round-70.md`

Read at lane tip `20c117ce160db5c5fc2b88663404b161a8b3c68a` (the assignment names `feb283ee`; two
commits landed after it: `9167e02d` lesson + `tools/souji-pointer-check.py`, `20c117ce` pointer-check
`:line`-suffix strip + regenerated r69 receipt + M1 wording). Every line below was re-derived from
committed bytes: `git show <rev>:<path>`, `git ls-tree -r`, `git cat-file -e`, and the tools run
read-only. Numbers the L1 states were not taken on trust; where I quote a number it is one I read.

## 1. r69 routed items — status at round 70

| item | status | evidence (committed bytes) |
|---|---|---|
| D1 (MEDIUM) mirror `.ufo/waves/round-69/w1/` into `census/round-69/records/wave-w1/` | **closed** | `0d8ce29a`; `git ls-tree -r --name-only HEAD census/round-69/records/wave-w1/` = 71 files = the 66 live `w1/` files (all 12 seat `.md`, `swarm-registry.json`, the receipts and `.logs` trees) under `seats/` + `w1-spec.json`/`w1-dispatch.json`/`w1-results.json`/`w1-run.stderr`/`w1.ready` at the mirror root. Per-file `sha256sum` of each mirrored `seats/<x>` against live `w1/<x>`: **0 differences**; `comm -23 live mirror` (LC_ALL=C): **0 live files unmirrored**. Caveat: paths are restructured (live root → mirror `seats/`), so "byte-identical" holds per file, not per path |
| D2 (MEDIUM) commit the r69 L1 selftest receipt | **closed** | the mirror carries `census/round-69/records/wave-w1/seats/S69MutTester.logs/selftest-orig.txt`, whose last two lines are `SELFTEST cases=16 pass=16 fail=0` / `EXIT=0` — the exact frozen C2 tally, now resolvable from a clone. r70's own receipt `census/round-70/records/counter-selftest.txt` (`SELFTEST cases=29 pass=29 fail=0`, EXIT=0) covers the r70 counter |
| D3 (LOW) SKILL.md row for the r69 counter battery mode | **closed** | `SKILL.md:916` (`\| r69 battery outcome split (C1 calibration) \| gate \| …`); `git show e063a2fc:SKILL.md \| grep -c 'r69 battery outcome split'` = **0**, so the row landed this round (`feb283ee`) |
| D4 (LOW) "6 flips" unit | **partial** | the phrase is gone (`grep -rn '6 flips' SCORECARD.md LOG.md corpus/lessons/round-69.md` → 0), but `SCORECARD.md:253` now says "6 differing `CASE`/`SUMMARY`/`REGRESS`/`EXIT=` lines"; my own re-measure `diff <(grep -E '^(CASE\|SUMMARY\|REGRESS\|EXIT=)' census/round-69/probes/c2-before-r68-clean.txt) <(… -ambient.txt) \| grep -c '^[<>]'` = **6 markers = 3 changed lines**. The unit is now "lines" while the number is still the two-sided marker count (should read 3 lines / 6 diff sides) |
| D5 (LOW) the ambient receipt should log the tuple applied | **open** | `census/round-69/records/c2-ambient.txt` header is `rev=`/`instrument=`/`instrument_sha256=`/`command=`/`# c1-counter root=…`/`# slot …` — `grep -c 'XDG\|HOME=\|GIT_TRACE' census/round-69/records/c2-ambient.txt` = **0**. No r70 receipt adds it (r70's C2 is a different claim) |
| D6 (conformance) report filed before WAVE-DONE | **pending, not closable yet** | the r70 wave is in flight: `.ufo/waves/round-70/w1/` holds only `S70Connector/` and `swarm-registry.json` on disk; `git ls-files .ufo/waves/round-70/` is empty (`.gitignore:1` covers the wave tree), so the WAVE-DONE-before-report order can only be judged at closure |
| (a) HIGH writer scrubs the pathspec routes + successor counter rows + C2 tuple | **closed** | `tools/souji-receipt-write.py` `PATHSPEC_ENV = ("GIT_LITERAL_PATHSPECS", "GIT_GLOB_PATHSPECS", "GIT_NOGLOB_PATHSPECS", "GIT_ICASE_PATHSPECS")` and `git()` filters `k not in PATHSPEC_ENV` (`93a051b2`); selftest case 38 asserts flag-row refuse + honest accept + wrapped command still sees the variable; rows `LA LD LN4 LU1 LG1 LA9 GA GD NGA NGD ICA ICD` in `census/round-70/c1-matrix.tsv:49-60`; the counter's `clean_env` drops `PATHSPEC_VARS` (`c1-counter.py:392`) |
| (b) scrub `GIT_ATTR_SOURCE`, `GIT_EXEC_PATH`, `GIT_TEMPLATE_DIR`, `GIT_QUARANTINE_PATH` (last fails closed) | **partial** | `census/round-70/c1-counter.py:394` drops `GIT_TEMPLATE_DIR`, `GIT_ATTR_SOURCE`, `GIT_EXEC_PATH`, `GIT_DEFAULT_HASH`; `grep -rn 'GIT_QUARANTINE' census/round-70/ tools/souji-receipt-write.py` = **0 hits** — the fails-closed item is untouched |
| (c) selftest must catch a precedence-swap mutant, a battery-branch mutant, and have an echo-judge row | **closed** | `census/round-70/records/c2-after.txt`: CM1 precedence swap `fate=killed`, CM2 expectation gate `killed`, CM3 echo judge `killed`, CM4 survived-gate (battery branch) `killed`; the selftest's battery-verdict and member-binding checks are `c1-counter.py:1378-1390` |
| (d) D06 needs an isolating content-only row | **open** | `grep -rn 'D06' census/round-70/` = **0 hits**; the 12 appended rows are all pathspec rows |
| (e) D29: a subdirectory or `GIT_LITERAL_PATHSPECS` row | **closed (as rows, not by name)** | `c1-counter.py:278` `"LN4": {"name": "subdirectory-root-scope-literal-pathspecs"}` plus the literal-pathspec flag/gitlink/absent/unmerged rows (`LD LU1 LG1 LA9`) and the GLOB/NOGLOB/ICASE accept+refuse pairs. `grep -rn 'D29' census/round-70/` = 0, so the connector's proposal is met without the D29 label |
| (f) registry check: teaches cell vs located quote | **open** | the only new checker, `tools/souji-pointer-check.py`, resolves path existence (`cat-file -e`); it reads no `corpus/SOURCES.md` cell and no quote |
| (g) writer `verify` subcommand (open since r68) | **open** | `grep -n 'verify' tools/souji-receipt-write.py` = 0 |
| (h) the battery EXIT should also gate per-mutant `regress` | **open** | the MUTANT line prints `regress={res['regress']}` (`c1-counter.py:1535`) but `battery_verdict()` (`:1125-1136`) gates only `obs != exp`, `survived`, `error` |
| sentinel F-1 HIGH ambient `GIT_TEMPLATE_DIR` | **closed** | `c1-counter.py:394` |
| sentinel F-2 MEDIUM `GIT_DEFAULT_HASH=sha256` (all rows error) | **closed by scrub, not re-measured** | `c1-counter.py:394`; no r70 receipt exercises `GIT_DEFAULT_HASH` |
| sentinel F-3 MEDIUM battery members unchecked; receipt binds no member hash | **closed** | `verify_members()` (`c1-counter.py:1139`) reads `battery/SHA256SUMS` before any run; every MUTANT line carries `sha256=`; `TAMPER T1 … member D01.py sha256 8c1ecef2bd30 != listed 913f6a611d6a fate=detected` |
| sentinel F-4 MEDIUM base-writer forgeries not attributed per mutant | **open** | MUTANT line fields are `forgeries= echo= honest= label= errors= regress=` — all new-slot; no `base_*` field |
| sentinel F-5 LOW `--receipt` truncates any path | **open** | `write_receipt()` (`c1-counter.py:1219`) is `open(path, "w")` with no existence refusal |
| sentinel LOW recorded `command=` replays only from the lane | **open** | `census/round-70/records/c2-after.txt` `command=` carries `--root .` |
| S69Scribe HIGH D18 is a harness artefact (`clean_env` pins `GIT_OPTIONAL_LOCKS=0`) | **open** | `c1-counter.py:395` still pins `GIT_OPTIONAL_LOCKS=0` for every slot; no PK7-style caller override was added for a D18 row (and no D18 row exists) |

Cross-check on the round's own numbers that I re-derived: `c1-after.txt` = 59 `CASE` lines, 15
`new=accept` / 44 `new=refuse` (so `new_honest=15` is the whole accept population, not a subset);
`c2-after.txt` `killed=4 survived=0 tamper=detected score=0`; writer `CASES` tuple length 38;
`corpus/SOURCES.md` S-rows 226 at `e063a2fc` → **228** at HEAD (the lesson's "+2" reproduces).

## 2. Two draft `## Mistakes` rows (lane format: # | class | evidence pointer | captured-by | fix)

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M4 (draft) | dead pointer in the round's own lesson (the r69 M14 class recurring inside the round that built the pointer check): the landed lesson cites a round-end registry receipt that exists in no commit, and the new checker is structurally blind to it | `corpus/lessons/round-70.md:53` ("… and at round end (`records/census-after.txt`)"); `git cat-file -e HEAD:census/round-70/records/census-after.txt` → **rc 128** (`does not exist in 'HEAD'`); `git ls-tree -r --name-only HEAD census/round-70/records/` lists six receipts and none is `census-after.txt`; `tools/souji-pointer-check.py:65-68` drops every `probe/ probes/ records/ controls/ battery/` token whose file is not under `census/round-*`, so `python3 -B tools/souji-pointer-check.py --root . --rev <HEAD40> corpus/lessons/round-70.md` prints `SUMMARY files=1 checked=14 missing=1` where the only MISSING line is the untracked `pointer-check-r70.txt` — the dead `records/` citation is never tested (the same run over `census/round-69/preregistration.txt` does report its five dead pointers, which is what hides the gap in the lesson path) | none — the pointer check ran this round but was never a gate on the lesson it belongs to, and its silent `continue` for lesson-relative tokens produced no counter | commit the round-end `census-after.txt` receipt (or cite `records/census-before.txt` only); make the checker resolve local prefixes against the citation's own directory for non-`census/round-*` files too, and make it count dropped tokens so `checked` cannot hide them |
| M5 (draft) | evidence durability (the r69 M15 class recurring): the lesson's pointer-check evidence existed on disk only at the tip, so the cited receipt cannot be resolved by any clone and the lane tree was left dirty | `corpus/lessons/round-70.md:28` cites `census/round-70/records/pointer-check-r70.txt` as the `missing=0` evidence; at tip `git status --porcelain` → `?? census/round-70/records/pointer-check-r70.txt` and ` M SCORECARD.md`; `git cat-file -e HEAD:census/round-70/records/pointer-check-r70.txt` → **rc 128**. A dirty tree is also what the writer's dirty-check refuses on, so the same bytes would block a receipt written after them | the pointer check itself, whose single MISSING line for `round-70.md` is exactly this file (`EXIT=1`) — the instrument caught it, the run was not a gate | commit the receipt together with the lesson that cites it, or leave the citation out until it is committed; add "cited receipts are `git cat-file -e`-able at HEAD" to the pre-commit sweep |

## 3. Missing repo-relative paths (checked at tip `20c117ce`, `git cat-file -e <tip>:<path>`)

Method: every path-shaped token in `corpus/lessons/round-69.md` and `census/round-69/preregistration.txt`
was tested at the lane root, and — for tokens with a bare `probe/ probes/ records/ controls/ battery/`
prefix — also against the citing file's own directory (`census/round-69/`). 22 tokens in the lesson,
21 in the preregistration.

**Dead (exist under no resolution):**

| path | cited at | note |
|---|---|---|
| `probe/full-battery-out.txt` | `corpus/lessons/round-69.md` (M2 fix cell, P4 row); `census/round-69/preregistration.txt:40`, `:125` | never existed; committed as `census/round-69/probes/battery-probe-27-prefix.txt` (r69 M14 names it) |
| `probe/fsm` | `census/round-69/preregistration.txt:38` | never existed; committed as `census/round-69/probes/fsmonitor-hook-probe.txt` (r69 M14 does **not** list it; r70 M1 does) |
| `probe/c2-ambient` | `census/round-69/preregistration.txt:41`, `:92` | never existed; the r69 counter's run is `probes/c2-ambient.txt`, the r68 before-arm is `probes/c2-before-r68-ambient.txt` |
| `records/c1-candidate.txt` | `corpus/lessons/round-69.md` M7 | cited **only as the discarded wrong name** ("the candidate receipt path `records/c1-candidate.txt` (written at `probes/`)"); not a live citation, listed for completeness |

`git cat-file -e HEAD:census/round-69/{probe/full-battery-out.txt,probe/fsm,probe/c2-ambient}` → rc 128
each; `records/c1-candidate.txt` → rc 128 at both resolutions.

**Not dead, but unresolvable at the lane root (shorthand for `census/round-69/…`; a reader who
resolves from the repo root fails):** `controls/d18-limit-battery.txt`, `probes/battery-probe-27-prefix.txt`,
`probes/c2-ambient.txt`, `probes/c2-before-r68-clean.txt`, `probes/c2-before-r68-ambient.txt`,
`records/c1-after-battery.txt`, `records/declared-coverage.tsv` — all `OK` under `census/round-69/`.
The new checker silently drops exactly these tokens in a lesson (`tools/souji-pointer-check.py:65-68`),
which is why `round-69.md` scores `missing=0`.

**Not lane paths (excluded):** `tools/notes-copy.txt`, `../notes-copy.txt`, `tools/extra/link` are
fixture-internal paths inside the counter's mirror repository; `census/round-68/records/c1-after/CAND.txt`
and `…/M-CD-SCRUB.txt` are `OK`.

Also dead in the r70 files (same class, outside the task-4 file list): `records/census-after.txt`
(`corpus/lessons/round-70.md:53`) and `census/round-70/records/pointer-check-r70.txt`
(`corpus/lessons/round-70.md:28`; exists on disk, absent from HEAD).

## 4. LOW finding on committed knowledge (not a lesson row)

`corpus/knowledge/pathspec-env-scrub.md` says `git ls-files -v -z ':(top)'` under
`GIT_LITERAL_PATHSPECS=1` "matches the literal path `:(top)`, prints nothing". The committed probe
(`census/round-70/probes/lp-ls-files-probe.txt`: `env=GIT_LITERAL_PATHSPECS=1 ls-files-out=[] rc=0`)
supports "the pattern is compared as a literal pathname and therefore matches nothing"; "matches the
literal path `:(top)`" reads as if a file of that name were matched. One-word precision fix:
"treats `:(top)` as a literal pathname, which matches no tracked file".

