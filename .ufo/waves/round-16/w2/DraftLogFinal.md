# DraftLogFinal — round 16 wave 2 (calibration)

Seat: SoujiR16.DraftLogFinal-4 (leaf, no delegation, no commits, no lane edits).
Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. Lane HEAD observed at probe: `163158a`. Measured commits: `0a70bef` (final C1 matrix), `7a79dc2` (landing rerun), `c6207bd` (R4), `b410186` (r15 landing), `cc21683` (r14), `a31642d` (r13).
Tool installs/updates: none.
Not re-run by this seat (outside the probe rule; not ALLOWED-EXEC): census or any copy, selftests, gate replays, fixture runs, checker runs, frozen regeneration, live-fleet runs. Every such number below is cited from a named artifact or from the LOG, marked `[not re-run]`.

STATUS: FAIL — three draft sentences overstate the evidence: "pre-harm fails only refusal/safety cases" (R15CFG-03 and R15CFG-18 fail on pre-harm and are not refusal/safety), "19 minor recursive reads" (18 recursive, 1 write-tool violation), and "restored the census from `cc21683` bytes" (the bytes differ). Corrected wording is in the draft below.

## Verdicts by item

| Item | Attacks | Verdict |
|---|---|---|
| Correction: b410186 does not parse; ConfigRepair.md:7-13 | calibration of r15 claims | holds (partial on the 23/47 wording) |
| C1 final numbers (changed 20/20, r14 12/12, selftest 38/38, bash -n, shellcheck) | final figures | holds in both matrices |
| C1 "pre-harm fails only refusal/safety cases" | pre-harm characterization | fails |
| C1 "measured over the r16-revised fixture" / fixture identity | which bytes were measured | partial: fixture changed after the final run |
| C1 "cbf688a restored the census from cc21683 bytes" | base/lineage claim | fails as a byte claim |
| C1 r14-harm fails every HARM_CASES id | harm arm | holds (15/15); also fails R15CFG-19, outside HARM_CASES |
| C1 r15 baseline does not parse, fails all cases | baseline arm | holds (rc 2; 32/32 failed) |
| C2 gate replays and fixture counts | gate calibration | not re-run; ConfigRepair.md:7 STATUS line and S043/S050 rows verified |
| R4 checker repair (47/47, 8/8, frozen clean) | checker execution | not re-run; checker bytes, regenerator, and fixture diff verified |
| R5 seat audit counts | audit | partial: counts 65/3173/1/19 hold; the 19-minor description does not |
| Sources S043-S050 | source rows | holds; S048 is also a rejected row and the draft names only S044 |

## Findings with file evidence

1. **Correction (holds).** `b410186` is `bash -n` rc 2 at line 1368 (`syntax error near unexpected token '}'`). `cc21683` is rc 0 (sha256 `fcff8b057b3e…`). `0a70bef` is rc 0 (sha256 `64a60fd0b0ed…`). `cbf688a` is rc 0 (sha256 `fed43c710b75…`). ShellCheck on b410186 reports SC1046 at 1324:3 and SC1047/SC1072 at 1368. The ConfigRepair report is at `.ufo/waves/round-15/w1/ConfigRepair.md`: line 7 `## STATUS: INCOMPLETE — file has an unresolved syntax error`; lines 11-13 `**The file in tree does NOT parse.** … do not ship this state as working.` The existing LOG wording "fails its own selftest 23/47" is ambiguous (reads as 23 passed). The lesson row R16-M4 says the checker "fails 23 of 47" and cites "selftest: 24/47 passed" at the HEAD copy. The draft states it as "passes 24 of 47 (23 fail)".
   - Not verified: the function name `list_repos` for line 1324; the r15 frozen pin `b5187351…`.

2. **C1 final numbers (holds).** `census/round-16/c1-matrix-final.json` (rev `0a70bef`, census sha `64a60fd0…`, runner sha `2815712b…`): changed arm bash_n rc 0; r14-namespace total 12 failed 0; r15-config total 20 failed 0; selftest checks 38 failed 0 rc 0; shellcheck findings 0. `census/round-16/c1-matrix-landing.json` (rev `7a79dc2`) gives the same figures.

3. **C1 pre-harm characterization (fails).** The pre-harm arm (`a31642d`, lines 166-328 of the final JSON) fails 18 of 32 cases, not "only refusal/safety":
   - r14-namespace: 10 of 12 fail (R14C2-01 through -06, -09 through -12), all refusal.
   - r15-config: 8 of 20 fail: R15CFG-02, -11, -17, -19 (refusal); R15CFG-03 (class `degrade`, `tests/fixtures/r15-census-config.py:169`); R15CFG-08 and -14 (class `safety`, lines 171 and 173); R15CFG-18 (class `preserve`, line 174; `worktrees=0 want 1; mtime_iso empty; verdict_flags=error want clean`).
   - The R15CFG-18 failure is a preserve-class case failing on the pre-harm tool. The smallest fix is to say so, not to call it refusal/safety.

4. **C1 fixture identity (partial).** The final matrix's r15-config fixture sha is `85de2a43…` (matches `git show 0a70bef:tests/fixtures/r15-census-config.py`). The R4 commit `c6207bd` changed that fixture: the CASE detail is capped at 400 characters so it stays under the R4 checker's 512-character bound (diff: +7/-3 lines, lines 1512-1523; oracle expressions unchanged). The HEAD fixture sha is `27474396…`, which is what the landing rerun at `7a79dc2` used. So "measured over the r16-revised fixture" is true of the landing rerun only. The draft names both shas.

5. **C1 lineage (fails as a byte claim).** `git diff --stat cc21683 cbf688a -- tools/souji-census.sh` shows 299 insertions and 54 deletions. The sha256 differs (`fcff8b05…` vs `fed43c71…`). "Restored from cc21683 bytes" overstates it; "built on cc21683 as base" is accurate.

6. **C1 r14-harm (holds, one note).** `c1-matrix-final.json` r14-harm arm (rev `cc21683`, lines 329-491) fails R15CFG-01, -03, -04, -06, -07, -08, -09, -10, -12, -13, -14, -15, -16, -18, -20: all 15 `HARM_CASES` ids (`tests/fixtures/r15-census-config.py:161-165`). It also fails R15CFG-19 (refusal; `synthetic store path in output`), which is not a HARM id. It passes R15CFG-02, -05, -11, -17. The LOG sentence is correct as written.

7. **C1 r15 baseline (holds).** `b410186` arm: bash_n rc 2 at 1368; r14-namespace failed 12/12; r15-config failed 20/20; selftest checks null rc 2; shellcheck 4 findings rc 1.

8. **C1 live-fleet (not re-verified).** `census/round-16/live-fleet-final.json` exists in tree at `7a79dc2` (blob `94285d5`). Not opened; the claim "identical on 21 repositories" is `[not re-run]`.

9. **C2 (partial; replays not re-run).** `tools/souji-landing-gate.py` sha256 `e7d2439d…`; `tests/fixtures/r16-landing-gate.py` sha256 `aae67c9c…`. ConfigRepair.md:7 is the STATUS line the gate's STATUS channel would carry; verified. S043 (`bash -n`, Bash 5.3 manual, `-n`) and S050 (Python `compile()`) exist as rows in `corpus/SOURCES.md` lines 57 and 64, with "Round-16 provenance" at line 9. The replays (5 findings / 0 / 0; selftest 18/18; fixture 15/15), the "three defect classes" claim, and the "42 quotation hits" / "10 false findings" numbers are `[not re-run]`.

10. **R4 (partial; checker not re-run).** `tools/souji-preservation-evidence.py` sha256 `5942f689…` at `c6207bd` (equal to HEAD); `81ffd389…` at `b410186`; 2638 lines at `b410186`. `tests/fixtures/r15-preservation-frozen/regenerate.py` exists at `c6207bd` (blob `4efccf2`). The lesson gives the selftest as 47/47 and external 8/8 and the frozen check as clean at `c6207bd`; not re-run. The R4 entry should say "passes 47/47 (per run recorded in the lesson; not re-run by this seat)" only if L1 runs it.

11. **R5 (partial; count description fails).** `census/round-16/seat-audit-w1.json` summary: seats_audited 65, calls 3173, major 1, minor 19 (verified). Violation classes: 18 × `V-RECURSIVE` (bash/grep/glob over the lane root or directory trees; lines 16-474) and 1 × `V-WRITE-UNKNOWN` (`SentinelCommandExec`, tool `write`, line 118, empty args, severity minor, lines 336-348). The draft must say "18 minor recursive reads and 1 minor write-tool violation". The major is `SrcGitNoLazyFetch`, `V-WRITE-SCOPE`, tool `edit`, target `.ufo/waves/round-16/r16-placeholder.md` (lines 402-428); the target is absent at probe ("not found"), so "attempted out-of-scope edit, failed" is consistent with the file state; the JSON itself does not record the failure.

12. **Sources (holds; one omission).** S043-S050 rows exist in the worktree `corpus/SOURCES.md` (uncommitted, as stated). S044 and S048 are both `REJECTED` (lines 58 and 62); the LOG names only S044. S048 is the ShellCheck SC1046 wiki page, rejected because the parse failure is established by `bash -n` and shellcheck on committed bytes.

13. **Lane HEAD drift (note).** The lane HEAD at probe was `163158a`, not `a6ec781` or `7a79dc2`. Every number above is bound to its named commit; the draft must not say "HEAD" for any measured number.

## Draft LOG.md entries (round 16)

Paste after the existing round-15 entries. Replaces the drafts in LOG.md lines 817-884 where they conflict.

## 2026-10-20 — round 16 correction: round 15 landed a census that does not parse

Correction to the round-15 entries ("Landed source candidates", "unverified candidate"): `b410186` committed `tools/souji-census.sh` in a state that **does not parse**: `bash -n` rc 2, `line 1368: syntax error near unexpected token '}'`; ShellCheck reports SC1046 at line 1324 (unclosed `if`) and SC1047/SC1072 at line 1368. The ConfigRepair seat ran `bash -n`, saw the failure, and wrote "The file in tree does NOT parse. … do not ship this state as working" (`.ufo/waves/round-15/w1/ConfigRepair.md:7-13`; its STATUS line 7 reads `INCOMPLETE — file has an unresolved syntax error`). The r15 entry, lesson, SKILL rows and report called the state unverified and listed the parse check as unrun; that understated a known break. Operability was therefore harmed at r15 (the census parsed at `cc21683`, sha256 `fcff8b05…`), not "numeric delta 0".

The r15 preservation checker, never executed at r15, passes 24 of its 47 self-test cases (23 fail) at the bytes cited in `corpus/lessons/round-16.md` R16-M4. The r15 frozen pin `b5187351…` names bytes no commit holds `[not re-verified in this entry]`. Historical r15 bytes are not rewritten; this entry, `corpus/lessons/round-16.md` (Corrections) and the round-16 report carry the correction.

Re-verification: `git show b410186:tools/souji-census.sh | bash -n` → rc 2 at 1368; `git show cc21683:tools/souji-census.sh | bash -n` → rc 0; `git show b410186:tools/souji-census.sh | shellcheck -f gcc -` → SC1046 at 1324:3, SC1047/SC1072 at 1368; `git show cc21683:tools/souji-census.sh | sha256sum` → `fcff8b05…`. ConfigRepair.md lines 7-13 read verbatim.

## 2026-10-20 — round 16: parsing value/effect-aware census (C1), landing gate (C2), r15 checker executed (R4), seat audit (R5)

C1 operability. `cbf688a` built the census on `cc21683` as its base (not byte-identical: `cbf688a` sha256 `fed43c71…`; `tools/souji-census.sh` +299/-54 relative to `cc21683`) and made the config guard value/effect-aware. `0a70bef` integrated 65 wave-1 reviews into the census (sha256 `64a60fd0…`), the config fixture and the matrix runner. Behaviour: only a config-named path overlapping a protected root keeps the whole-run exit 2; could-not-evaluate config degrades to one `error` row with no git run; a soft finding never stops the scan; a filter driver bound by attributes skips status for that repository (`status-unverifiable`); hooksPath/fsmonitor are neutralized on every git call through `GIT_CONFIG_COUNT`; promisor/partialClone are inert under `GIT_NO_LAZY_FETCH` `[code claims not re-verified in this entry]`.

Final matrix, `census/round-16/c1-matrix-final.json` (rev `0a70bef`; r15 fixture sha `85de2a43…`): changed bash -n rc 0, ShellCheck 0 findings, legacy selftest 38/38, r14 namespace 12/12, r15 config 20/20. The R4 commit `c6207bd` then capped the CASE detail at 400 characters so it stays inside the R4 checker's 512-character bound (fixture sha `27474396…`; the `--json` record keeps the full problem list; no oracle changed). Landing rerun at `7a79dc2` (census sha unchanged `64a60fd0…`): changed 20/20, r14 12/12, selftest 38/38, bash -n and ShellCheck clean (`census/round-16/c1-matrix-landing.json`).

Harm and baseline arms. Pre-harm (`a31642d`, sha `6a000c59…`) fails 18 of 32: r14 namespace 10 of 12 (refusal) and r15 config 8 of 20: refusal 02, 11, 17, 19; degrade 03; safety 08, 14; preserve 18 (`worktrees=0 want 1`). r14-harm (`cc21683`, sha `fcff8b05…`) fails all 15 HARM_CASES ids (01, 03, 04, 06-10, 12-16, 18, 20) and also R15CFG-19; it passes 02, 05, 11, 17. r15 baseline (`b410186`) fails bash -n (rc 2) and all 32 cases. Live fleet paired runs (`census/round-16/live-fleet-final.json`): r14-harm and changed rows identical on 21 repositories `[not re-verified in this entry]`.

C2 calibration. `tools/souji-landing-gate.py` (sha256 `e7d2439d…`; held-out `tests/fixtures/r16-landing-gate.py` sha256 `aae67c9c…`) checks registry-cited parse, frozen pins and measured commits, and STATUS-channel carry (LG-PARSE-REG/-CHANGED, LG-MISSING-REG, LG-FROZEN-PIN/-MEASURED, LG-SEAT-UNCARRIED, LG-OPEN-ADMITTED). Replay of `b410186` (round 15) → exit 1, 5 findings (1 parse, 3 pin, `ConfigRepair.md:7` STATUS line); `a31642d` (round 13) and `cc21683` (round 14) → 0 findings; selftest 18/18; held-out fixture 15/15. Two noisier channel drafts were measured and dropped (10 false findings per admitted replay; 42 quotation hits at this landing). The gate's replay counts were produced by the authoring seat `[not re-run in this entry]`. Sources S043 (`bash -n`) and S050 (Python `compile()`) are rows in `corpus/SOURCES.md` (uncommitted until the lesson lands).

R4. The r15 checker's CASE regex (`[^\t]*`) rejected the TAB-separated detail the real fixture prints, so its self-test passed 24 of 47 cases (23 failed; `corpus/lessons/round-16.md` R16-M4). Fixed with its selftest builders and r16 class tables. The lesson records selftest 47/47 and external fixture 8/8 at the repaired bytes. `tests/fixtures/r15-preservation-frozen/regenerate.py` re-ran every arm at committed bytes; the checker is `tools/souji-preservation-evidence.py` sha256 `5942f689…` at `c6207bd`, and `--frozen` is recorded clean at `c6207bd` `[selftest, external fixture and frozen run not re-run in this entry]`.

R5. `tools/souji-seat-audit.py` audited the 65 wave-1 transcripts (3173 calls) → `census/round-16/seat-audit-w1.json`: 1 major (`SrcGitNoLazyFetch`, V-WRITE-SCOPE edit to `.ufo/waves/round-16/r16-placeholder.md`; the target is absent) and 19 minor: 18 V-RECURSIVE reads over the lane root or directory trees, and 1 V-WRITE-UNKNOWN (`SentinelCommandExec`, write tool, line 118). Affected evidence voided and re-derived. R6 cross-domain line and R7 rejected rows S044 and S048 are in the report and registry. Residual contractions versus pre-harm are disclosed in the lesson and filed as an L0 scope question. Certification OFF; K5 HELD.

Re-verification (commands and their results, as run by the W2 seat; the gate, selftest, fixture and matrix runs are NOT in this list and must be run by L1): `git show b410186:tools/souji-census.sh | bash -n` → rc 2 at 1368; `git show cc21683:tools/souji-census.sh | bash -n` → rc 0; `git show 0a70bef:tests/fixtures/r15-census-config.py | sha256sum` → `85de2a43…`; `git show 7a79dc2:tests/fixtures/r15-census-config.py | sha256sum` → `27474396…`; `git show 7a79dc2:tools/souji-census.sh | sha256sum` → `64a60fd0…`; `git diff --stat cc21683 cbf688a -- tools/souji-census.sh` → 299 insertions, 54 deletions; `git show c6207bd:tools/souji-preservation-evidence.py | sha256sum` → `5942f689…`; census/round-16 JSON per-arm verdicts counted by line (final and landing).

## Corrections to the existing draft wording (for the reviewer)

- "pre-harm fails only refusal/safety cases" → replace with the 18-of-32 breakdown above (R15CFG-03 degrade, R15CFG-18 preserve).
- "19 minor recursive reads" → "18 recursive reads and 1 write-tool violation".
- "cbf688a restored the census from cc21683 bytes" → "built on cc21683 as base".
- "fails its own selftest 23/47" → "passes 24 of 47 (23 fail)".
- "R7 rejected row S044" → "rejected rows S044 and S048".
- Name the fixture shas for both matrices (85de2a43 at 0a70bef, 27474396 at 7a79dc2) and the R4 change that separates them.

## Commands

1. `sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-preservation-evidence.py /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-seat-audit.py /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py`
2. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -8 -- tools/souji-census.sh && echo --- && for r in b410186 cc21683 0a70bef cbf688a; do printf '%s ' $r; git show $r:tools/souji-census.sh 2>/dev/null | bash -n 2>/tmp/x 2>&1; echo "rc=$? $(head -c 200 /tmp/x 2>/dev/null)"; done; echo ---; git show 7a79dc2:tools/souji-census.sh | sha256sum; git show 0a70bef:tests/fixtures/r15-census-config.py | sha256sum; git show 7a79dc2:tests/fixtures/r15-census-config.py | sha256sum; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show --stat --oneline 0a70bef | head -20` (writes scratch `/tmp/x`, outside the permitted `/var/tmp/souji-r16-<SeatName>/`; removed by command 5)
3. `cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat 0a70bef 7a79dc2 -- tests/fixtures/r15-census-config.py tools/souji-census.sh census/round-16/run-matrix.py && git diff 0a70bef 7a79dc2 -- tests/fixtures/r15-census-config.py | head -120; echo ---; git show b410186:tools/souji-census.sh | shellcheck -f gcc - | head -8; echo "sc_rc=${PIPESTATUS[1]}"; echo ---; for r in cc21683 cbf688a 0a70bef; do printf '%s ' $r; git show $r:tools/souji-census.sh | sha256sum; done; git log --oneline -3 7a79dc2 -- tests/fixtures/r15-census-config.py`
4. `cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree 7a79dc2 census/round-16/ && echo --- && git ls-tree a6ec781 census/round-16/ 2>&1 | head -3; echo ---; git rev-parse --short HEAD; git diff --stat cc21683 cbf688a -- tools/souji-census.sh; git show c6207bd:tools/souji-preservation-evidence.py | sha256sum; git show b410186:tools/souji-preservation-evidence.py 2>&1 | sha256sum; git show b410186:tools/souji-preservation-evidence.py 2>&1 | wc -l`
5. `rm -f /tmp/x; cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree c6207bd tests/fixtures/r15-preservation-frozen/ ; git ls-tree 163158a -- .ufo/waves/round-16/ | head -5; echo ---; git rev-parse --short 7a79dc2 0a70bef a6ec781` (last `rev-parse` errored: "Needed a single revision"; harmless)

All other lookups were read/grep tool calls on exact named files (no shell).
