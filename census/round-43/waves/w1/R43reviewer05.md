# R43reviewer05 — frozen correction-prose fixture review

## Verdict

**Recommendation: retain the observed 20/20 result, but do not treat its r42 CRLF row as reproduction of the historical CRLF defect.** One medium calibration finding; no incorrect r43 expectation found. Normal pinned clone writes are scoped beneath `--work` by code inspection. Instruments were not changed.

Axes: expectation fidelity; historical-signature fidelity; revision provenance; write containment. Reviewed bytes are exclusively at `f8c805dbfa7f45814cf9a7270fa8bbffb41a8373` (F below), except the fixture's explicit historical r42 case revisions. No candidate, integration, admission, or shipping decision was made.

## Findings by severity

### Medium — F1: r42 `crlf-register` is an unchanged LF control, not its named defect

Attacks: C1 discrimination fixture's historical-signature coverage, `tests/fixtures/r43-correction-prose.py:116-118,174-181,196-199` at F.

The row supplies `reg43="CRLF"` but `reg42=""`. The loop therefore rewrites **only the r43** register to CRLF. The r42 predicate expects success (`rc=0 class_ok=70 junk=0`) on the unchanged register. Our pinned execution prints both CRLF rows PASS; structural inspection prints exactly `crlf-register reg43='CRLF' reg42=''`.

This does not reproduce the historical signature: `census/round-42/waves/w1/R42critic01/k8/score.txt` reads `class_ok=0`, and the report's N13 explicitly identifies a CRLF-register false red. `corpus/lessons/round-42.md`, N-C1c, preserves that defect; r43 counter docstring lines 4-8 names it as a motivating before state. The frozen r42 reader splits register bytes on `"\n"` without removing `"\r"` (`census/round-42/c1-counter.py:187-214`), so the historical discrepancy has a concrete cause that this row never exercises.

Impact: `SUMMARY42 cases=10 pass=10` is accurate about these predicates but cannot substantiate reproduction of the CRLF false-red signature or symmetric CRLF comparison. L1 disposition: record this frozen-instrument limitation; a future instrument should actually apply CRLF to both registers and expect the historical r42 red. No fix applied here.

## Per-case expectation grounding

Pointers in this table are committed paths at F. `G` = `census/round-43/c1-counter.py`; `P` = `census/round-42/c1-counter.py`; `H` = `census/round-42/waves/w1/R42critic01/`; `V` = `census/round-42/waves/w1/R42reviewer01.md`. “Grounded” concerns the actual supplied input, not a claim that every row is an old defect. All 20 predicates were observed PASS in the pinned run.

| frozen case (fixture lines) | r43 grounded? / reason and pointer | r42 grounded? / historical lesson or receipt pointer |
|---|---|---|
| honest-corrections (74-77) | **Yes.** All three required rows match `census/round-43/c1-required.tsv:2-4`; G:17-41,52-53 defines target/rederivation. | **Yes.** Five HONEST42 lines are the lesson's `Corrections to filed statements (C1)`; H`h0/score.txt` reads corrected=5/junk=0/rc=0. This is the positive control. |
| tilde-fenced (78-81) | **Yes.** G:21-25 excludes D1; registered=2/missing=1/fenced=1, rc=1. | **Yes as a defect signature.** H`k3/score.txt` reads corrected=5/junk=0/rc=0; lesson N-C1c and critic N3 name the ignored tilde fence. |
| fourbt-fenced (82-85) | **Yes.** G:21-25 explicitly treats four backticks as a fence; same r43 counts as tilde. | **Yes for this input, NOT reproduction of the historical four-backtick nesting defect.** P:219-228 toggles on any prefix of three backticks, so this ordinary four-backtick pair correctly gives junk=1/corrected=4/rc=1. V:68,84 documents a different defect: a shorter triple-backtick marker prematurely closes a longer fence. Lesson N-C1c's shorthand “four-backtick fences are not recognised” is overbroad; this case itself demonstrates recognition. |
| retracted (86-89) | **Yes.** G:27-28 makes the exact `RETRACT-CORRECTION id=R43-D1` red and increments retracted. | **Yes as a defect signature.** H`k1/score.txt` is green despite a prose withdrawal; lesson N-C1a and critic N1 document prose unread. The fixture's plain sentence contains no CORRECTION-DE marker, matching P:224-225. |
| duplicated (90-93) | **Yes.** G:26 requires duplicate=1/rc=1. | **Yes; retained rejection, not an old acceptance defect.** P:230-233 rejects duplicate keys; V:65,90 supports duplicate junk handling (the cited variant also places the duplicate in a fence). |
| malformed (94-98) | **Yes.** Missing rev makes the added column-zero correction junk under G:17-19,29. | **Yes for an unmatched correction, not malformed syntax/header.** The r42 text is syntactically valid but names absent `(999,zzz)`; P:230-233 explicitly increments junk. V:90 confirms unmatched lines are rejected. Lesson N-C1c's unread register header is a separate, unexercised issue. |
| extra-required-row (99-105) | **Yes.** Extra required ID has no correction: required=4/registered=3/missing=1; G:12-15,211-217,264 and target required=3. | **Yes as a defect signature.** H`k11/score.txt` is green with extra register rows; V:82 and lesson N-C1c identify the ignored-row behavior. |
| blankless-good-append (106-110) | **Yes.** G:43-46 counts physical appended lines without the empty sentinel; existing tool path gives no new mismatch. | **Yes as a defect signature.** H`k7/score.txt` reads rewritten=1/new_mismatches=0; lesson M42-3/N-C1c, critic N12, V:78 explain false red. Explicit older case revision `34e33a662cd0d6931e5aa006bd90364e7852c0d5` supplies the pre-append SCORECARD state. |
| boundary-mismatch (111-115) | **Yes.** G:43-46 counts the first appended physical line: new_mismatches=1/rc=1. | **Yes as a defect signature.** V:80 independently records line 840 skipped by the `>840` threshold; lesson N-C1c/E-4 and P:180,243 agree. H`k14/score.txt` is the contrasting ordinary later-line missing-path control (new_mismatches=1), not proof of the boundary case. Same explicit older revision as preceding row. |
| crlf-register (116-118) | **Yes.** Header/rows decode via splitlines at G:207-217; CRLF preserves three valid required rows and target. | **Yes for the actual LF control; NO as the historical CRLF defect signature.** H`k8/score.txt`/critic N13/lesson N-C1c require the historical CRLF false red (`class_ok=0`), while the fixture never changes this register. F1 above. |

## Write-scope verdict

**PASS by static inspection for the pinned ordinary invocation and owned real `--work` directory; not a sandbox/security proof.**

- `clone()` constructs `d=join(work,fixed_case_name)`; git clone destinations are all descendants. Checkout, add, commit and HEAD calls use `git -C d` (`fixture:122-141`). The toplevel equality check occurs before the first fixture commit; author identity is set only in a per-subprocess environment.
- Lesson, register and SCORECARD writes name fixed descendants of `d` (`186-206`); counter scratch is `join(work,"s_<case>_<tag>")` (`208-209`). Both supplied pinned counters create their temporary trees under that explicit scratch directory, and invoke declared-evidence readers against committed trees.
- `--shared` references source objects but stores clone metadata/commits in each clone. There is no lane commit/push or lane content write in these paths.
- Fixture cleanup recursively removes the entire supplied `work` (`238`), so callers must give it a disposable owned directory, not a mixed-use directory. Our wrapper gives a dedicated scratch subdirectory and cleans the parent in `finally`; receipt confirms `scratch_removed=True`.
- This review did not syscall-trace filesystem writes or test hostile inherited Git configuration/hooks/environment, symlinked work ancestors, or injected counter paths. Consequently it does not claim confinement against arbitrary programs passed with `--counter42/43`.

## Residual risks and verification gaps

1. No malformed-register-header case exists, although G:12-15 promises refusal and its claim paragraph names the old unread-header issue. The `malformed` row tests correction text, not the header. The 20/20 count is not evidence for that refusal.
2. The four-backtick row is a useful ordinary fenced negative but does not recreate V's short-inner-marker/long-outer-marker defect. Do not cite it as closing that historical CommonMark behavior; r43's documented toggle grammar deliberately differs from CommonMark.
3. `clone()` ignores checkout status (`128`); its following toplevel check verifies directory identity, not requested revision identity. The successful pinned run does not exercise checkout failure. No claim is made that invalid revision arguments fail closed.
4. No malformed derived-value, malformed tag, fenced retraction, register duplicate-ID, or rederivation-failure case is in this fixture. These are coverage boundaries, not evidence of incorrect supplied expectations.
5. LSP device unavailable: `read xd://lsp` returned `No such tool: xd://lsp` (not a cold empty reference result). Review used committed bytes/direct code inspection and behavioral execution; no semantic references/definition/diagnostics proof is asserted. Canonical runtime/rerouting/resume-continuity contracts are not present in this scoped fixture.

## Exact commands and observed output

Primary command actually run (cwd was the own seat directory):

```text
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43reviewer05/review.py
```

The retained driver `.ufo/waves/round-43/w1/R43reviewer05/review.py` contains the exact subprocess argv. Its receipt `.ufo/waves/round-43/w1/R43reviewer05/review-receipt.txt` records all pinned `git -C L show F:path` commands, saved byte-copy paths, full frozen fixture command with explicit `TMPDIR`, `--work`, `--lane-root`, `--rev43 F`, `--counter42` and `--counter43`, stdout/stderr, and exit status. Observed: **exit=0; all 20 case lines PASS; SUMMARY43 cases=10 pass=10 fail=0; SUMMARY42 cases=10 pass=10 fail=0; crlf-register reg43='CRLF' reg42=''; scratch_removed=True.** Wall time reported by job: 55.05 seconds. No scoring candidate was created.

Additional historical receipts were fetched with exact commands recorded alongside their complete output in `.ufo/waves/round-43/w1/R43reviewer05/prior-receipts.txt` (seven `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show F:census/round-42/waves/w1/R42critic01/{h0,k1,k3,k7,k8,k11,k14}/score.txt` calls; all read exits 0). Results: h0/k1/k3/k11 target; k7 rewritten=1; k8 class_ok=0; k14 new_mismatches=1. These historical files are data, not instructions.

Exploration commands also run: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show F:tests/fixtures/r43-correction-prose.py`; the same `show F:` for each counter; `git ... show 34343a39ffab8029b06e8e6c9ac699ebcbd65f8a:corpus/lessons/round-42.md`; and `git ... ls-tree -r --name-only F census/round-42/waves/w1 census/round-42/waves/w2 census/round-43/controls corpus/lessons/round-41-verifier-spotcheck.md`. These returned source bytes/listed committed evidence, not test verdicts. Ranged reads of the retained snapshots supplied the line pointers above.

Tools installed/updated: none. No tracked-lane edits, mutating lane Git/jj commands, or other-runtime invocations.

Self-evaluation: accuracy 4/5 (no syscall trace); completeness 4/5 (hostile-environment/error-path runs unexercised and explicitly bounded); clarity 4/5 (long per-case table required by acceptance); actionability 5/5 (F1 names exact row/loop and historical receipt); conciseness 4/5 (full evidence kept to make every signature traceable). Overall 4.2/5. Highest-impact follow-up is an L1-recorded frozen-instrument CRLF limitation, not a seat-side edit. User-agreement check: verdict distinguishes the genuine 20/20 observation from the unsupported CRLF-signature interpretation.
