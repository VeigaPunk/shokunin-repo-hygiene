# RevC1BaseCount — C1 base-grounded count falsification

Seat: L1Souji25.RevC1BaseCount (reviewer, wave 2). Lane base a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe; candidate = current lane HEAD commit 6deb53561aace9aa14a399f88cf8150da4d4f4bd (the W1 tool/fixture integration is uncommitted in the worktree; `tools/souji-coverage-agreement.py` sha256 `bb506469be860f994f74f4c7d6eb1c949a4931b676cdb60f9f79de041d12f27f` is byte-identical to the W1 draft `w1/souji-coverage-agreement.py`, and `tests/fixtures/r25-coverage-agreement.py` sha256 `2a65d8c0ad8104889a522570499fc254d1bf725c36485e7a90e8aa8d225a0407` is byte-identical to `w1/r25-coverage-agreement.py`). Scratch `/var/tmp/souji-r25-RevC1BaseCount/` (used, removed at end). No reads, no installs.

## Status
STATUS: PASS — no C1 claim predicate, target or frozen case set is falsified at the candidate. Base a6d2d15 holds exactly **6** front-matter-grounded knowledge entries (4×F2 + 2×F4), so the original frozen after-target literal `kill_tested=4` was factually wrong and amendment 1's correction to `kill_tested=6` is right. The integrated tool re-run passes the frozen fixture 16/16 and the real after-run prints `kill_tested=6` at the candidate, matching the amended target exactly. An F2-only mutant is caught by the fixture (k5) **and** by the real-run target literal (kill_tested=4 ≠ 6); it does not reach the declared target. The 16th case k7 is **not** a post-score case-set deviation: amendment 3 (commit 6deb535, 09:34:20-03:00) committed k5–k7 before any C1 measurement receipt exists (all c1-*.tsv receipts: 09:39:17Z; MutCoverage reports at 09:43/09:47 -03:00). The premise "MutCoverage report says 15 cases" is not supported by either MutCoverage report — both state 16 cases (k1–k7); the only "15 cases" in the wave belong to the separate R17 record-agreement fixture (14/15 → 15/15).

## Evidence

### 1. Independent base-grounded count at a6d2d15 (6 vs 4)
`git ls-tree --name-only a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe corpus/knowledge/` lists 14 children (12 `.md` + `obsidian-ledger.tsv` + none). `git show <rev>:corpus/knowledge/<name>` front-matter (before first `# ` line) carries `ground:` lines in exactly **6** entries:
- F2 (4): `count-objects-garbage-readings-r25.md`, `count-objects-linked-worktree-garbage.md`, `git-repo-structure-readonly.md`, `repo-size-census-readonly.md`
- F4 (2): `quarantine-origin-record-fields-r24.md`, `quarantine-staging-no-copy-r23.md`

So: base-grounded total = **6**; the F2-only subset = **4**. This matches the committed base receipt `census/round-25/records/coverage-agreement-at-base.tsv` (`. `grounded=6 mapped=6 dangling=0 mismatches=0`, rc 0, tool_sha256 `71b89eb3…` = old tool, no `--base-rev`). Amendment 1 (`preregistration-amendment-1.txt` line 10): "the expected after-run literal is corrected to `kill_tested=6 kill_violations=0`" — the original prereg target (line 53) `kill_tested=4` corresponds exactly to the F2-only count. `ScoutC1KillRule.md` A1 (line 7) independently documented the same: "An F2-only mutant that narrows scope hits 4 exactly and passes all frozen k1–k4 cases."

### 2. Frozen fixture re-run at the candidate (integrated worktree bytes)
`python3 -B tests/fixtures/r25-coverage-agreement.py --tool tools/souji-coverage-agreement.py` (from lane root) → **rc 0**, last line `cases=16 pass=16 control=FALSE-GREEN-REJECTED`. Matches the after-target fixture literal (prereg line 54; amendment 3 line 14) and the W1 green-arm receipt `w1/ExecC1/c1-green-arm.tsv` (line 43, `rev=6deb535…`, utc 2026-10-25T12:39:17Z).

### 3. Real after-run at the candidate
`python3 -B tools/souji-coverage-agreement.py --root . --rev 6deb53561aace9aa14a399f88cf8150da4d4f4bd --base-rev a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe` → **rc 0**, stdout `grounded=6 mapped=6 dangling=0 mismatches=0 kill_tested=6 kill_violations=0`. Identical at `--rev 6e4737eab43d8fde1b85eb9f57023d29046705b4` (freeze commit) and to `w1/ExecC1/c1-real-tip-vs-base.tsv`. Exact match to the amended after-target literal (amendment-1 line 10).

### 4. F2-only mutant
Mutant `/var/tmp/souji-r25-RevC1BaseCount/f2-only.py` = candidate tool with `kill_rule` base restricted to F2-grounded entries and F2 grounds only (`base = {n: ks & {2} for n, ks in base.items() if 2 in ks}`).
- Real after-run: `grounded=6 mapped=6 dangling=0 mismatches=0 kill_tested=4 kill_violations=0`, rc 0 → **kill_tested=4 ≠ 6**: does not reach the declared (amended) target. It reproduces the original erroneous literal verbatim.
- Frozen fixture: `cases=16 pass=15 control=FALSE-GREEN-REJECTED`, rc 1 — **k5 (partial-removal) fails**: expects `kill_tested=1 kill_violations=1 rows=[KILL-RULE:e.md] exit=nonzero`, got `kill_violations=0 rows=[none] exit=0` (fixture lines 16). So the fixture does discriminate the F2-only *scope* narrowing; the *count* narrowing is pinned only by the real-run target literal.
- Note (residual): a count-only F2 variant (base filtered for counting but ground sets compared in full) passes the fixture 16/16 while printing `kill_tested=4` on the real lane — the fixture has no case whose base entry lacks F2, so counting scope is not independently asserted by the fixture; the amended after-target literal is what catches it. This is a disclosed coverage note, not a predicate failure: the frozen case set and target are unchanged and, together, still reject the under-scoped tool.

### 5. k7 / 16th case — post-score deviation check
- Integrated fixture case set: 16 (r24's nine + k1..k6 + k7), k7 = `veto-less-control` scored as case 16 (fixture lines 389–409; main() lines 518–524; docstring line 45 "C=16 = 9 r24 + k1..k6 + k7"). `w1/r25-coverage-agreement.py` is byte-identical (same sha256) and declares the same 16 cases.
- Prereg text (frozen at 6e4737e) listed only k1–k4; amendment 3 (`preregistration-amendment-3.txt` lines 5–16) added k5, k6 and the k7 veto-less control, with the target line "cases=16 pass=16 (r24's nine + k1..k6 + k7 control)", written "before any claim was measured".
- Chronology (git commit dates and file mtimes, all -03:00): amendment 3 commit 6deb535 = 09:34:20; final 16-case fixture `w1/r25-coverage-agreement.py` mtime 09:38:08; all C1 receipts (`w1/ExecC1/c1-*.tsv`) utc 2026-10-25T12:39:17Z = 09:39:17 and reference `rev=6deb535…`; `ExecC1.md` 09:39:25; `MutCoverageAgreement.md` 09:43:40; `MutCoverageAgreement-2.md` 09:47:41. The only pre-amendment-3 C1 seat artifact, `ScoutC1KillRule.md` (09:32:09), predates the final fixture and used its own scratch harness (its k5/k6/k7 were scout extras, not the frozen set; it notes the ExecC1 fixture draft was "mid-write"). No C1 scoring artifact exists before 09:34:20.
- Both MutCoverage reports state 16 cases with k1–k7: `MutCoverageAgreement.md` line 5 ("draft r25 fixture (16 cases incl. k1–k7)") and line 23 ("`cases=16 pass=16 control=FALSE-GREEN-REJECTED`"); `MutCoverageAgreement-2.md` line 4 and line 8. **No statement of "15 cases" exists in either report.** The wave's only 15-case fixtures are the R17 record-agreement counter (14/15 → 15/15, a different tool/fixture).

## Findings
1. Base count confirmed: 6 grounded entries (4×F2, 2×F4) at a6d2d15; the frozen prereg literal `kill_tested=4` was factually wrong (it equals the F2-only subset) and amendment 1's `kill_tested=6` correction is correct; the candidate run matches 6.
2. Candidate green arm holds: fixture `cases=16 pass=16 control=FALSE-GREEN-REJECTED` (rc 0) and real after-run `kill_tested=6 kill_violations=0` (rc 0) — both exactly per the amended frozen target.
3. The F2-only mutant does **not** reach the declared target: fixture rejects it on k5 (15/16, rc 1) and the real-run counts line contradicts the target (`kill_tested=4` vs 6). The counter's kill rule is therefore not exploitable by F2-scoping at the candidate.
4. `7 is not a post-score case-set deviation: amendment 3 added it before any C1 measurement receipt (all receipts postdate commit 6deb535 and the final 16-case fixture mtime); both MutCoverage reports cover the 16-case set including k7. The assignment premise "MutCoverage report says 15 cases" is unsupported by the artifacts (the only 15-case fixtures in the wave are R17's, unrelated to C1).
5. Residual coverage note (not a predicate change): the fixture cannot see *counting* scope (no k-case base entry lacks F2); only the amended real-run target literal pins `kill_tested=6`. A count-only F2 mutant passes 16/16 but still fails the real target — so the C1 admission test (fixture + after-target literal together) remains sound.

## Attack log
- ATTACK 1 (F2-only, check scope): killed by fixture k5; real-run counts mismatch amended target. No predicate change.
- ATTACK 2 (F2-only, count scope): fixture false-green 16/16 (disclosed residual), but real-run `kill_tested=4` fails the amended after-target literal. No predicate change.
- ATTACK 3 (k7 post-score deviation): not sustained — amendment 3 precedes all scoring evidence (commit time 09:34:20 vs first receipt 09:39:17Z; fixture mtime 09:38:08); k7 is a frozen, pre-scoring case.
- No lane files edited; scratch `/var/tmp/souji-r25-RevC1BaseCount/` removed.
