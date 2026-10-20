# ReviewScore — SCORECARD mapping review (round 13, wave w1)

Seat: `SoujiR13.ReviewScore` (reviewer, leaf). Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Scope: `SCORECARD.md` planned section and axis rows; design of a reproducible before/after mapping for the three declared r13 claims (C1 calibration, C2 operability, C3 coverage); legacy count discrepancies; r13 correction text. No score gain is proposed.

## 0. Snapshot and method

- HEAD: `31984f4` (`git -C <lane> rev-parse --short HEAD`). Working tree is **not clean**: sibling seats are editing while this review ran (observed 02:12 on 2026-10-20). Uncommitted at observation time: `M corpus/QUALITY.md` (adds Q17, Q18), `M corpus/SOURCES.md` (S005 and S006 `queued`→`mined`), `?? corpus/knowledge/git-repo-structure-readonly.md`. Every number below is labelled **HEAD** or **WT** (working tree). Only HEAD numbers are stable evidence for a closing commit.
- Measured by read-only commands only: `grep`/`awk`/`sed` counts, `git show <rev>:<path>`, `git log`, `git status`, and one run of `census/round-12/sources-census.sh` (a read-only grep/awk census). The first run of that script was from the wrong cwd and failed on `corpus/SOURCES.md` (no such file); the second run was from the lane root. No build, lint, test, fixture, or r13 tool was executed. Nothing was installed or upgraded (tool channel: none used). Nothing outside `.ufo/waves/round-13/w1/ReviewScore.md` was written.
- Not read: `census/operator-sweep-20261019/` (protected, untracked; not inspected).
- `census/round-13/` holds only `before.json` at the time of reading. The drafts named in `.ufo/waves/round-13/w1-spec.json` (`baseline-measures.md`, `final-checks.md`, `registry-draft.md`, etc.) did not yet exist.

## 1. Axes

| axis | recorded score | r12 delta (SCORECARD) | saturation reading |
|---|---|---|---|
| calibration | 7 (`SCORECARD.md:14`) | 0 (stated) | below the 8 line |
| operability | 8 (`SCORECARD.md:15`) | 0 (stated) | at the 8 line |
| coverage | 8 (`SCORECARD.md:13`) | 0 (stated) | at the 8 line |

- `SCORECARD.md:61-62`: "Saturation line: 8 per axis; stagnation window 3 rounds."
- The only recorded score delta is r12, and it is 0 on all three axes. `LOG.md` records verdicts in prose ("improved", "holds") and holds no per-round numeric series. A stagnation count therefore cannot be reproduced from the repo. [limitation]
- Reading of the saturation line as applied to coverage and operability: a verdict can read "improved" with the score held at 8. [INFERENCE on how the line is meant to be applied]
- Label defect: rows read "improved … score delta 0" (`SCORECARD.md:13-15`). "Improved" is a verdict and "0" is a score delta; they should be written as two separate fields.

## 2. Before/after mapping for the three declared r13 claims

Claim sources: `SCORECARD.md:51-57` (Planned r13 items 1, 2, 4); `.ufo/waves/round-13/w1-spec.json` (file names: `tools/souji-cert-evidence.py`, `tests/fixtures/r13-quarantine-bounds.sh`, `tests/fixtures/r13-repo-structure.sh`, `tools/souji-repo-structure.sh`); `census/round-13/before.json` (measured at `31984f4`: `cert_evidence_gate: 0`, `bounded_staging_calls: 0`, `F2_entry: 0`).

Each row gives the HEAD "before", the command that counts the "after", and what the count does not prove. "Score delta" is 0 for every row because no reproducible mapping from these counts to a 0–10 number exists in the repo; the r12 rows already state the same limit.

### C1 calibration — executable evidence validator

| step | command (run from lane root) | before (HEAD 31984f4) | after target |
|---|---|---|---|
| validator exists | `git -C <lane> ls-files tools/souji-cert-evidence.py` → empty; `test -f tools/souji-cert-evidence.py; echo $?` | `1` (absent at HEAD; `before.json` `cert_evidence_gate:0`) | `0` |
| validator self-test | `python3 tools/souji-cert-evidence.py --selftest; echo $?` | not runnable | `0`, with one passing case id per class below |
| class coverage | count of passing case ids among: wrong installed bytes, shared fragment, missing evidence path (Q17), false success — wrong command/exit or untested class (Q18) | 0/4 | 4/4 |
| calibration rows that become check-backed | rows whose `captured-by` names the case id: M40 (shared relay, verdict bytes) — only the shared-fragment and wrong-bytes parts | 0 | M40 at most |

Limits to state in the report and the lesson:
- M41 (candidate-selection rule contradicts the class under test, `corpus/lessons/round-11.md:16`) is **not** a validator class. It must stay rule-only.
- `QUALITY.md` Q17 and Q18 (WT only, uncommitted) name `python3 tools/souji-cert-evidence.py --selftest` as their check and cite `corpus/lessons/round-13.md` `## Mistakes`. Neither the tool nor that lesson file exists (`ls corpus/lessons | grep round-13` → empty). Until both exist, Q17/Q18 are criteria with dangling checks and must not be counted as check-backed.
- A passing self-test tests the validator's own fixtures. It is not a catch on a live incident. Q18 itself says "a passing integrity gate never grants deletion authority". Certification stays OFF (`SCORECARD.md:72-77`).

### C2 operability — bounded per-target staging and digest in `tools/souji-quarantine.sh`

| step | command | before (HEAD) | after target |
|---|---|---|---|
| per-target bound present | `grep -cE 'timeout [0-9]+[smh]? .*(mv\|sha256sum)' tools/souji-quarantine.sh` (Q8 test pattern) | `0` (`grep -c timeout tools/souji-quarantine.sh` → `0`) | ≥1 |
| FIFO / non-regular rule | `grep -nE 'test -f\|\[ -f ' tools/souji-quarantine.sh` → 15 matches at HEAD; read by line: `file_sha()` (`tools/souji-quarantine.sh:184`) and the sha256 call at `:724` run `sha256sum --` with no regular-file test and no `timeout` on their own line; the `-L` checks at `:197,469,473,477,700` are symlink guards, not FIFO guards | guard that accepts regular, non-symlink files only, on each digest reader, under the bound |
| stall/FIFO selftest | `bash tests/fixtures/r13-quarantine-bounds.sh --selftest; echo $?` | fixture absent (`ls tests/fixtures \| grep -c r13` → `0`) | `0`, including a stalled-target case and a FIFO case, each asserting fail-closed exit code and a diagnostic |
| calibration rows | M43 (`LOG.md:373`) and M44 (`LOG.md:403`) | captured-by is `QUALITY.md Q8` (rule-only) | check-backed only when the bound grep and the selftest both pass |

Limits:
- A `timeout` wrapper proves the call is wrapped, not that a hang aborts fail-closed. The assertion must be on exit status and on the diagnostic.
- Operability registry: `SKILL.md:102-106` has one gate row (`r12-maintenance-guard`). `SCORECARD.md:53-55` item (3) (registry rows for the four installed tools) is not done and is not part of this claim. Do not cite registry rows for C2.
- The row "executable Pre-quarantine guard rows 0→3" (`SCORECARD.md:15`) counts lines of SKILL.md checklist prose (`SKILL.md:94-100`, `- [ ]` items). No tool runs them. "Executable" is wrong; see §3 item 8.

### C3 coverage — F2 entry and `/var/tmp` repo-structure fixture

| step | command | before (HEAD) | after target |
|---|---|---|---|
| F2 row status | `grep -nE '^\| F2 ' corpus/README.md` | `frontier, no entry` (`corpus/README.md:40`) | `frontier, entry admitted` |
| F2 knowledge entry | `ls corpus/knowledge \| grep -ciE 'size\|structure\|sizer'` (the command written into README:40) | `0` | `1` |
| admitted entries (held excluded) | `for f in corpus/knowledge/*.md; do grep -q '^## Admission status — HELD' "$f" && continue; head -3 "$f" \| grep -cE '^(source\|verified-at\|recheck):'; done \| grep -c '^3$'` | `4` (K1–K4; K5 is HELD) | `5` |
| frontier rows holding an admitted entry | `grep -cE '^\| F[0-9] .*\| frontier, entr(y\|ies) admitted' corpus/README.md` | not yet valid (README says "held", see §3) | `4` (F1, F2, F3, F4) |
| S005 and S006 status | `awk -F'\|' '/^\| S00[56] /{print $2,$9,$12}' corpus/SOURCES.md` | `queued`, used-by `—` (HEAD) | `mined`, used-by resolves to the entry path |
| recheck paths resolve (Q17) | `for f in corpus/knowledge/*.md; do grep -q 'Admission status — HELD' "$f" && continue; grep -oE 'tests/fixtures/[A-Za-z0-9_.-]+' "$f" \| sort -u \| while read -r p; do { test -f "$p" && ! test -L "$p"; } \|\| echo "unresolved $f $p"; done; done` | prints nothing (K1–K4 HEAD) | prints nothing |

Current WT state that blocks admission (observed, uncommitted):
- `corpus/knowledge/git-repo-structure-readonly.md` line 3 reads `recheck: bash tests/fixtures/r13-repo-structure.sh --selftest`. That fixture does not exist (`ls tests/fixtures | grep -c r13` → `0`). This is the same defect class as r12 K5 (a recheck naming a fixture that was never committed; `corpus/knowledge/quarantine-same-filesystem-rename.md:51-58`). The entry must not be admitted until the fixture is committed and resolves under the Q17 command above.
- The entry header reads `verified-at: 2026-10-20 … census/round-13/verification.json`. That file was not present when I read `census/round-13/`. [to-verify]
- The F2 entry must carry S005's own limits: `git repo structure` is EXPERIMENTAL and its format "may change and is not intended for machine parsing" (`corpus/lessons/round-12.md:184-187`, S005 quote). A claim of stable output would fail Q2.
- No live deletion: the fixture must write only under `mktemp -d /var/tmp/...` with a trap (Q4).

## 3. Legacy count discrepancies (observed)

Each item cites the line where the value appears and the command that reproduces the correct value.

1. **Coverage knowledge count includes the held entry.** `SCORECARD.md:13` reads "knowledge entries … 0→5", measured by the command that does not exclude HELD. HEAD: 5 files with three headers; `corpus/knowledge/quarantine-same-filesystem-rename.md` contains `## Admission status — HELD` (line 51), so the admitted count is 4. The SCORECARD's own correction (`SCORECARD.md:17-20`) already says "0→4 admitted (+1 held, K5)", but the table cell was not changed. Same drift class as M37 (`census/round-12/mistakes.md`, row M37).
2. **README calls admitted entries "held".** `corpus/README.md:39` (F1 "entries held"), `:41` (F3 "entry held"), `:42` (F4 "entries held"). Per `corpus/lessons/round-12.md:351-375` (post-review item 2) and `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md` (no HELD heading), K1, K2, K3 and K4 are admitted. Only K5 is held. The coverage map therefore contradicts the SCORECARD.
3. **Frontier-row regex does not separate admitted from held.** `grep -cE '^\| F[0-9] .*\| frontier, entr' corpus/README.md` → `3` matches both "entries held" and "entry held". Once item 2 is fixed, use `frontier, entr(y|ies) admitted`.
4. **SOURCES status values are stale in the capability row, the census artifacts, and the after-file.**
   - `SCORECARD.md:30` (capability row): `mined=18 queued=13 rejected=2`.
   - HEAD census, run from lane root: `mined=16 queued=15 rejected=2`. Histogram at HEAD: `mined` 16, `queued` 15, `rejected` 2 (S030, S032). The `SCORECARD.md:19-20` correction and `corpus/lessons/round-12.md:375` both say 16/15.
   - `census/round-12/sources-census.txt` (tracked) and `census/round-12/after.txt` (tracked) both still say `mined=18 queued=13` (pre-post-review, `d7266c5`).
   - The WT census now reads `mined=18 queued=13` because a sibling is changing S005 and S006 to `mined` (uncommitted). The capability row's value is therefore reproduced only by uncommitted work, not by the committed state.
   - The row's own counting command (`SCORECARD.md:30`) run at HEAD gives 16/15, so the cell contradicts its command.
5. **Calibration parenthetical is reversed.** `corpus/lessons/round-12.md:57` reads "After (this file): 51/53 (… before M27 was set back to `none`, which then read 52/53)". Measured: with M27's captured-by treated as captured, the awk count is `52/53`; with M27 set to `none` (current text, `round-12.md` line 89), it is `51/53`. Setting a row to `none` can only lower the captured count, so "51/53 before, 52/53 after" cannot hold. The correct order is 52/53 before set-back, 51/53 after. The headline 51/53 (HEAD and WT agree) is the right value for the current file.
6. **Calibration denominators differ.** Before is `census/round-12/mistakes.md` with 52 rows (no M53); after is `corpus/lessons/round-12.md` with 53 rows. M53 was added in r12 and is captured by a rule written in r12 (QUALITY Q7, Q13). Same-population comparison (M01–M52 in the after file, using the same awk): `50/52` (M27 and M39 are the only `none` rows, both inside M01–M52). The SCORECARD row (`SCORECARD.md:14`) should show the same-population value next to the headline.
7. **"Captured" counts rule-only pointers.** The census header (`census/round-12/mistakes.md`, "Conventions") defines captured-by as "an existing artifact … a tool check, a tool selftest case id, or a `tests/` fixture"; a rule with no check is `no-check`. The headline awk (`$6 !~ /^[[:space:]]*none/`) counts any non-`none` cell. Heuristic check-backed count (cell matches `tools/|tests/|selftest|fixture`):
   - before (`census/round-12/mistakes.md`): 10 of 52 check-backed; 18 rule-only; 24 none.
   - after (`corpus/lessons/round-12.md`): 12 of 53 check-backed; 39 rule-only; 2 none.
   - The 12 after-rows matched: M02, M03, M08, M14, M15, M29, M32, M33, M34, M38, M43, M51. Manual review: M03 (cell is prose naming `tests/**` as an excluded path), M08 (cell is `tests/results/INSTALL.json:5`, a recorded decision rule, not a check) and M43 (cell cites `grep -c timeout … → 0`, a *missing* fix) are false positives. M14 (`tools/souji-verify.sh:157`, a code fix line) and M32 ("tools only, partial") need a judgment. Clear check-backed rows are therefore at most about 9.
   - The lesson's M43 cell (`corpus/lessons/round-12.md`, row M43, captured-by) describes its own fix as "still open". Under the census definition M43 is rule-only; the headline counts it as captured.
8. **"Executable" guard rows.** `SCORECARD.md:15`: "executable Pre-quarantine guard rows 0→3". The count (`grep -cE 'maintenance\.auto=false|rev-parse --show-toplevel|worktree lock --reason' SKILL.md` → `3`) is correct as a line count. The rows are unchecked `- [ ]` prose items (`SKILL.md:94-100`). The `dcc8b9e` value 0 is reproduced (`git show dcc8b9e:SKILL.md | grep -cE …` → `0`). Only the wording "executable" is wrong.
9. **QUALITY row count and README admission bar.** `corpus/README.md:31` says "admission bar (Q1–Q15)"; `corpus/README.md:62` says "now runs Q1–Q16". `census/round-12/after.txt` says `QUALITY rows: 15` (`d7266c5`). HEAD has 16 rows (`git show HEAD:corpus/QUALITY.md | grep -cE '^\| Q[0-9]+ \|'` → 16). WT has 18 (Q17, Q18 uncommitted). The README contradicts itself within the same file.
10. **"Measured commit" cells point at the wrong commit.** `SCORECARD.md:13-15` says every cell was measured at `d7266c5`. For QUALITY (15 vs 16) and SOURCES (18/13 vs 16/15) the value at HEAD `31984f4` differs. Either re-measure at the closing commit or state each cell's commit separately.
11. **Planned section has no status per item.** `SCORECARD.md:51-57` lists r13 items (1)–(5) with no state. Per `census/round-12/mistakes.md` M52 (and the r12 closing rule), the closing commit must set each item's state. Items outside this review's three claims: (3) registry rows for four tools and (5) kotodama `.scratch` re-sweep (M47; scheduled ≈2026-10-20; tree age not measured here).

## 4. Proposed r13 correction text (for the L1 closing commit; not applied by this seat)

Replace `SCORECARD.md:13` cell (coverage) with:

> improved (r12 C2 post-review: 4 admitted entries + 1 held K5 on F1/F3/F4; self-verdict pending non-author; score delta 0). knowledge entries with source/verified-at/recheck headers, HELD excluded: 0→4 admitted (+1 held K5) at 31984f4. r13 C3 adds the F2 entry: 4→5 [only when admitted with a committed recheck fixture]. frontier rows holding ≥1 admitted entry 0→3 (F1, F3, F4). SOURCES registry 0→33 rows; mined=16 queued=15 rejected=2 at 31984f4. | `for f in corpus/knowledge/*.md; do grep -q '^## Admission status — HELD' "$f" && continue; head -3 "$f" \| grep -cE '^(source\|verified-at\|recheck):'; done \| grep -c '^3$'` → 4 at 31984f4 ; `grep -cE '^\| F[0-9] .*\| frontier, entr(y\|ies) admitted' corpus/README.md` → 3 ; `bash census/round-12/sources-census.sh` (from lane root) → 33 / 0 / A=29 B=3 C=1 / mined=16 queued=15 rejected=2 | <measured commit> |

Replace `SCORECARD.md:14` cell (calibration) with:

> improved (r12 C1, self-verdict pending non-author; score delta 0). Mapped-criteria coverage (rule-coverage count, not catches): 28/52 (before, `census/round-12/mistakes.md`) → 51/53 (after, `corpus/lessons/round-12.md`); same population M01–M52: 50/52. Check-backed under the census definition (heuristic, not manually confirmed): 10/52 → 12/53. r13 C1 adds `tools/souji-cert-evidence.py` (integrity validator; not a deletion authority); it changes a count only when its selftest passes and each class row names its case id. | the awk on each file as in `SCORECARD.md:14`; heuristic check-backed command `sed 's/\\|/%7C/g' <file> \| awk -F'|' '/^\| M[0-9]+ \| (defect\|process\|honest-stop\|caught) \|/{n++; x=$6; if (x !~ /^[[:space:]]*none/ && x ~ /tools\/\|tests\/\|selftest\|fixture/) c++} END{print c"/"n}'` | <measured commit> |

Replace `SCORECARD.md:15` cell (operability) with:

> improved (r12 C3, self-verdict pending non-author; score delta 0): registered gates 0→1 (`r12-maintenance-guard`, `SKILL.md:106`); checklist rows that name a gate in SKILL.md 0→3 (prose, not executed by any tool). r13 C2 adds a bounded per-target staging call in `tools/souji-quarantine.sh` only if the Q8 grep and `tests/fixtures/r13-quarantine-bounds.sh --selftest` both pass. | `bash tests/fixtures/r12-maintenance-guard.sh --selftest; echo $?` → 0 ; `grep -cE 'maintenance\.auto=false|rev-parse --show-toplevel|worktree lock --reason' SKILL.md` → 3 (0 at dcc8b9e) ; `grep -cE 'timeout [0-9]+[smh]? .*(mv|sha256sum)' tools/souji-quarantine.sh` → 0 at 31984f4 | <measured commit> |

Replace `SCORECARD.md:30` (capability row, SOURCES):

> SOURCES registry (contract v1): 33 rows; census `mined=16 queued=15 rejected=2` at 31984f4 (r12 post-review; the earlier `18/13` was pre-post-review).

Replace the `corpus/README.md` coverage-map rows (`:39`, `:41`, `:42`) "entries held" text with "entries admitted (K1, K2)", "entry admitted (K3)", "entry admitted (K4) + K5 held" respectively; and `corpus/README.md:31` "Q1–Q15" with "Q1–Q16 at 31984f4 (Q17–Q18 pending commit)". Both corrections are in the r13 closing commit's write set and not this seat's.

Add to `SCORECARD.md` under the table: one line per axis stating "verdict: improved; score: unchanged (N)" so verdict and score are separate fields.

Replace the word "executable" in the operability row with "checklist" (see item 8).

## 5. Proposed final checks for L1 (run after all subagents land, at the closing commit, from lane root)

1. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --short HEAD` and `git -C … status --short` (expect only expected r13 paths).
2. Admitted-knowledge count (HELD excluded) — command in §2 C3. Expect 5 if F2 is admitted, 4 if not.
3. Recheck-path resolution (Q17) — command in §2 C3. Must print nothing.
4. Frontier regex (admitted form) — expect 4 with F2 admitted, else 3.
5. SOURCES census: `bash census/round-12/sources-census.sh` from lane root. Expect `33 / 0 / …` and the status line matching the final SCORECARD cell; also regenerate `census/round-12/sources-census.txt` only if the closing commit owns it (it is a tracked r12 artifact; decide explicitly).
6. Calibration: the headline awk and the heuristic check-backed awk on `corpus/lessons/round-12.md` and `census/round-12/mistakes.md`, plus the same-population awk excluding M53.
7. QUALITY dangling check: `grep -oE 'QUALITY\.md Q[0-9]+' corpus/lessons/round-1[23].md | sort -u | while read -r _ q; do grep -qE "^\| $q \|" corpus/QUALITY.md || echo "dangling $q"; done` — must print nothing. Also confirm `corpus/lessons/round-13.md` exists if Q17/Q18 cite it.
8. C1: `python3 tools/souji-cert-evidence.py --selftest; echo $?` → 0; `grep -c` of each class's case id; confirm the validator checks `sha256sum` of the installed file against the verdict fragment (Q6) and rejects a shared fragment (Q18).
9. C2: `grep -nE 'timeout [0-9]+[smh]? .*(mv|sha256sum)' tools/souji-quarantine.sh` ≥ 1; `bash tests/fixtures/r13-quarantine-bounds.sh --selftest; echo $?` → 0, with the stalled and FIFO case ids.
10. C3: `test -f tests/fixtures/r13-repo-structure.sh && bash tests/fixtures/r13-repo-structure.sh --selftest; echo $?` → 0; `test -f tools/souji-repo-structure.sh` if the entry cites it.
11. Operability regression: `bash tests/fixtures/r12-maintenance-guard.sh --selftest; echo $?` → 0 (`SKILL.md:106` pins its ids).
12. Certification stays OFF: `grep -n 'certification' SCORECARD.md` shows the OFF statement unchanged.

## 6. Limitations

- The working tree changed during the review. HEAD and WT numbers above are separate; none of the WT numbers is evidence until committed.
- The check-backed count is a text heuristic on the `captured-by` cell. Manual review (M03, M08, M43) shows it over-counts. It is a sizing aid, not a score.
- There is no per-round numeric score history in the repo; stagnation and saturation cannot be computed from it.
- No r13 artifact exists yet (no validator, no quarantine bound, no r13 fixture, no r13 lesson). Every "after" value is a target, not a measurement.
- This seat is a lane-internal leaf reviewer. It does not claim non-author status.
- Two uncommitted sibling edits (`corpus/QUALITY.md`, `corpus/SOURCES.md`) and one untracked entry (`corpus/knowledge/git-repo-structure-readonly.md`) are not this seat's write set and were not modified.
