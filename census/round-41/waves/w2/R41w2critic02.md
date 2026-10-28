# R41w2critic02: git-plumbing attack on the C2 freeze check (operability)

Lane tip 1d41c13574db80fdd9a4bde490b712da7ce2a85f. Tool `tools/souji-freeze-check.py` at 1d41c13 is the same blob as 119c26f (`178be89870b3ce156120e8f779489d7ba486ae4e`), sha256 `3c3e80baedd8774848fb9ac786bbda0c07c47250a14884abf1409f328fc3340b`, matching the L1 receipt `tool_sha=3c3e80baedd8`. Counter `census/round-41/c2-counter.py` sha256 `85ffe2638a5ed0c83438ce96224f6dad07b2c99567d3d1a71e76e9316a1d1e11`, matching the prereg C2 line. Freeze of `census/round-41/preregistration.txt` is e2a74312 (its only add; lane `rev-parse --is-shallow-repository` = false). git 2.56.0, Python 3.14.8.

Documented behaviour sources: tool docstring `tools/souji-freeze-check.py:1-17`; counter docstring `census/round-41/c2-counter.py:12-47` (grammar, the exact finding classes, FROZEN-EDITED scope at line 37, DISPATCH rule at lines 38-40). Code paths: `freeze_rev` 81-85, `dispatch_findings` 88-111 (Round gate 89-91, endswith test 103-104), `parse_claims` 64-78 (first key wins, line 76), `check_path_sha` 114-133, `evaluate` 136-179 (Base 148-155, Control blob read at freeze only, line 169), refusals 195-202.

## Commands actually run (all read-only on the lane)

1. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --is-shallow-repository` -> `false`
2. `git -C LANE log --oneline --diff-filter=A --no-renames --format='%H %s' -- census/round-41/preregistration.txt` -> `e2a74312... round-41: freeze preregistration and do-nothing controls`
3. `git -C LANE show 1d41c13:tools/souji-freeze-check.py | sha256sum` -> `3c3e80baedd8774848fb9ac786bbda0c07c47250a14884abf1409f328fc3340b`
4. `git -C LANE show 1d41c13:census/round-41/c2-counter.py | sha256sum` -> `85ffe2638a5ed0c83438ce96224f6dad07b2c99567d3d1a71e76e9316a1d1e11`
5. Real leg, tool run on the committed bytes:
   - `python3 -B tool.py --root LANE --prereg census/round-41/preregistration.txt --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f` -> `SUMMARY claims=3 findings=0`, EXIT=0
   - same with `--rev e2a74312af4233963e44e4dbb38838ece07b8bd2` -> `SUMMARY claims=3 findings=0`, EXIT=0
   - `--prereg census/round-40/preregistration.txt --rev 1d41c13...` -> 18 findings (`FINDING C3 FIELD-MISSING Population`, `... Target`, ...), `SUMMARY claims=3 findings=18`. The EXIT=0 printed here is `tail`'s status, not the tool's; the tool's exit is 1 (the counter's `retro red rc=1` confirms).
6. Attack probe, 31 scenarios over synthetic repos under scratch (every git call `-C`, toplevel asserted, identity only via env): `python3 -B .ufo/waves/round-41/w2/R41w2critic02/probe.py --tool <scratch>/tool.py --scratch <scratch>/probe --out .ufo/waves/round-41/w2/R41w2critic02/probe-results.txt`. Full rows, with observed rc, freeze subject and FINDING lines: `w2/R41w2critic02/probe-results.txt`. The freeze column is the tool's own `freeze_rev()` result, observed by importing the pinned file.
7. Non-ASCII quoting check: `git log --name-only --format=%x01%H -- .ufo/waves/round-41` in the R2 fixture -> `".ufo/waves/round-41/w\303\251-dispatch.json"` (quoted, so the `endswith('-dispatch.json')` test at tool line 104 fails). The ASCII control lists `.ufo/waves/round-41/w1-dispatch.json` unquoted.
8. Committed counter re-run on the lane tip (independent of the L1 receipt): `python3 -B census/round-41/c2-counter.py --root LANE --rev 1d41c13... --scratch <scratch>/c2` -> `case-*=PASS` for 21 cases, `real ok rc=0 findings=0 summary=(3, 0)`, `retro red rc=1 findings=18 summary=(3, 18)`, `SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=3c3e80baedd8`, exit 0. Saved as `w2/R41w2critic02/c2-counter-rerun.txt`.

Scratch `/fast/scratch/hyaku/souji-r41/R41w2critic02` deleted after copying the receipts above. No tool was installed. No git mutation was run in the lane.

## Attack table (documented vs observed)

| # | Attack (probe case) | Documented behaviour (source) | Observed | Verdict |
|---|---|---|---|---|
| 1 | Prereg first added on a branch, then merged (G1) | Freeze = oldest commit reachable from --rev that adds PATH (docstring 12; counter 22) | freeze = branch add commit; rc0 clean | As documented |
| 2 | Prereg git-mv'd after freeze, Counter edited and digest restamped in the rename commit (I2) | Freeze = oldest add of PATH, `--no-renames` (tool 82-83; counter 22) | freeze reset to the rename commit; rc0 clean. The original freeze (I1) correctly gives FROZEN-EDITED | As documented, but a **silent pass** on rule 1 of the prereg (renames not followed) |
| 3 | Prereg deleted then re-added, Target changed (J1) | Freeze = oldest add (documented) | freeze = first add; rc0 clean. Prereg text never compared with the freeze blob | As documented; **silent pass** on rule 1 (Target edit) |
| 4 | Deleted then re-added, Counter edited and restamped (K1) | Digests checked against the freeze blob | COUNTER-DIGEST + FROZEN-EDITED against the first add | As documented |
| 5 | Prereg Base set to freeze itself (B1) | Base must be a strict ancestor of freeze (docstring 13; counter 29) | BASE-NOT-ANCESTOR | As documented |
| 6 | Base edited post-freeze to another ancestor (C1) | Only Counter/Population blobs are checked against the freeze (counter 37) | rc0 clean | Named scope in the docstring, but **silent pass** on rule 1 |
| 7 | Target edited post-freeze (D1) | Same as 6 (Target/Kill are not frozen) | rc0 clean | Same as 6 |
| 8 | Control turned green post-freeze (E1) | Control read at freeze only (tool 169; counter 36) | rc0 clean | Same as 6; the do-nothing control can be edited after freeze unseen |
| 9 | Two `Counter:` lines; the second points at the edited counter (F1) | Undocumented; the grammar only says "a key line is Key: value" (docstring 10-11). Code: first key wins (tool 76) | rc0 clean; the edited counter is never checked. Control F2 (single line) gives FROZEN-EDITED + COUNTER-DIGEST | **Defect**: silent false negative on the Counter check |
| 10 | Prereg with no `Round:` line and a dispatch file added before freeze (S1) | DISPATCH rule is keyed on the Round line (counter 39) | dispatch check silently skipped (tool 89-91 returns []); rc0 clean. No refusal, no finding | **Defect**: silent skip of a named finding class |
| 11 | CRLF prereg with `Round: 41` and an earlier dispatch file (S2) | Not documented | ROUND regex `^Round:...$` cannot match a line ending in `\r`; silent skip; rc0 clean | **Defect**, same class as 10 |
| 12 | Dispatch file with non-ASCII name added before freeze (R2) | DISPATCH class covers `*-dispatch.json` (docstring 15, counter 38) | git quotes the path (`"...w\303\251-dispatch.json"`), so the endswith test fails; rc0 clean. The ASCII control (R1) is flagged | **Defect**: silent false negative on a named class |
| 13 | Symlink Counter whose stated sha256 is of the link text (N2) | Counter is "a repo path sha256=" (docstring 16); the blob read is `cat-file blob`, which returns the link text, not the target | rc0 clean after `census/real.py` is edited post-freeze, i.e. the executed counter changed unseen | **Defect**: symlink is not followed; the honest digest gives a false COUNTER-DIGEST (N1) |
| 14 | Counter (or Population) is a directory (M1) | Missing blob -> COUNTER-MISSING / POPULATION-MISSING (counter 30-35) | both classes reported; message says "not present at freeze", which is misleading but the class is right | As documented (minor message issue) |
| 15 | Counter is a gitlink/submodule entry (O1) | As 14 | COUNTER-MISSING with the same misleading message | As documented (minor message issue) |
| 16 | Dispatch file added in the same commit as the prereg (P1) | Documented as "FREEZE-REV or an ancestor" (counter 38-40); tool 108 uses `c == freeze` | DISPATCH-BEFORE-FREEZE, detail "first added at X, not after freeze X" | As documented |
| 17 | Dispatch file on a side branch, merged after freeze (Q1) | Documented strict-ancestry test (counter 40) | rc0 clean (the side commit is not an ancestor of freeze) | As documented, but ancestry is not wall-clock order; a limit to name |
| 18 | Dispatch linear before freeze (R1, positive control) | Documented | DISPATCH-BEFORE-FREEZE | As documented |
| 19 | rev = freeze (A2); rev before freeze (A3); clean linear (A1) | Documented (--rev unresolved or PATH absent -> exit 2) | rc0 / rc0 / rc2 "absent at ..." | As documented |
| 20 | Shallow clone, depth 1, 2, 3 of a history where the add is at commit 2 (L-d1..d3) | Not documented anywhere (no shallow clause) | Freeze silently moves to the boundary commit (`L 4` at d1, `L counter edited and restamped` at d2, `L 2` at d3); all rc1 only because `BASE-UNRESOLVED` (the Base commit is missing). At d2 the FROZEN-EDITED and COUNTER-DIGEST classes are hidden entirely. At d4 the freeze is correct (`L freeze`) | **Defect**: undocumented; red for the wrong reason and the class set is wrong. Fail-closed only through Base, not through the freeze check |
| 21 | Full history of the same repo (L1) | Documented | COUNTER-DIGEST + FROZEN-EDITED against `L freeze` | As documented |

Rows 2, 3, 6, 7, 8, 9, 10, 11, 12, 13, 20 are the failures. Rows 2, 3, 6-8 are the prereg's own rule 1 ("No Counter, Population, Control, pinned tool, or this file changes after the freeze commit") not being enforced by the tool; the tool only enforces it for the Counter and Population blobs. Rows 9-13 are silent passes on grammar or DISPATCH inputs the tool claims to check. Row 20 is an undocumented shallow-clone failure.

None of the 21 counter cases (`census/round-41/c2-counter.py` CASES 193-213) exercises rows 2, 3, 6-13 or 20, so the claim's own target (21/21, real ok, retro red) cannot detect them.

## Verdict

**C2 (operability): the stated predicate reproduces, but the attack succeeds on 10 of the 31 scenarios.**

- Verified as predicated: the committed counter re-run gives 21/21, `real ok`, `retro red`, both stubs REJECTED. Kill conditions do not fire (receipt row 8).
- Falsified against the rules the tool is meant to enforce: 10 silent passes (rows 2, 3, 6, 7, 8, 9, 10, 11, 12, 13), plus one undocumented shallow-clone misattribution (row 20). The clearest are row 9 (a duplicate Counter line hides an edited counter), row 12 (a non-ASCII dispatch file is invisible to DISPATCH), rows 10-11 (no Round line or CRLF silently disables DISPATCH), and row 13 (a symlinked Counter is never followed).
- Operability is therefore not harmed in the sense the claim tests (the command runs and its target reproduces), but the claim should not be admitted as "freeze checklist sound". Admission needs these recorded as named limits in the round-41 lesson (rows 2, 3, 6-8, 17, 20 as scope limits; rows 9-13 as defects), or a successor candidate that fixes them and is re-measured by the frozen counter. A successor must add the rows as cases, because the frozen 21-case counter cannot see them.
- Minor: the COUNTER-MISSING message for directories and gitlinks says "not present at freeze", which is inaccurate (row 14-15).

Tooling: none installed or updated. No pacman or git mutation run. Scratch removed.
