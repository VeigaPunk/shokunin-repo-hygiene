# S62CriticClaim — round 62 critic report (claim C1: index-flag concealment before a clean-tree receipt)

**CLAIM: declare-with-rewrite.** The round may stand only as the rewrite in §4. As filed (calibration, one claim, weakest sentence in §3) it is a Q59 misattribution and should be refused.

Lane read-only. Lane HEAD `16fa821f`. Lane `git status --porcelain` empty; `git ls-files -v` → 17350 × `H` (re-measured). No tools installed or updated; no pacman; host git 2.56.0. Probe fixtures lived under `/fast/scratch/hyaku/souji-r62/S62CriticClaim/`, removed (`ls` → absent). Probe logs: `probe-log-part2.txt`, `probe-log-part3-midrun.txt` in this directory.

## 1. Findings

| # | sev | finding | citation | evidence |
|---|---|---|---|---|
| F1 | **H** | **Calibration label is a misattribution under Q59.** The claim changes a runnable writer on an input edge class (index flags, the r10 cluster-D edge class) and no self-assessment file. Q59 names exactly this: "a gate/runnable fixture on an input edge class is an operability surface; … a self-assessment-file change is a calibration surface." The claim touches `tools/souji-receipt-write.py` and its fixture only; no SCORECARD/SHONEN/LOG row changes, so the AXES calibration signal ("SHONEN.md/SCORECARD entries match observed repo state") cannot move. The same writer and edge class was classed coverage/operability in r61 M3 and F7, and the critic rejected that attribution then. The test is the same and the answer is the same. | `corpus/QUALITY.md:143` (Q59); `AXES.md` (fleet) calibration row, "Signal" column; `corpus/lessons/round-61.md:46` (M3), `:103` (F7) | claim scope from `w1-spec.json` (`tools/` + fixture only). |
| F2 | **H** | **The lane's own instrument cannot catch F1.** `souji-axis-check.py` R2 has no surface class for "runnable tool on an edge class". `receipt-binding` and `measurement` are NEUTRAL, so a claim whose surface is a receipt writer can declare `surface-class: receipt-binding` on calibration and pass R2 silently. Q59 requires "the check must be an instrument, not a hand review"; the operability half of Q59 is not instrumented. | `tools/souji-axis-check.py` `SURFACE_AXIS` / `NEUTRAL_SURFACES` (lines 31–41), R2 check (lines 118–123) | read; not executed against a claim block (none exists yet). |
| F3 | **H** | **Axis choice is forced by R3, not by the surface.** Calibration (7) is the lowest owned score (coverage 8, operability 8). R3 then requires one claim on calibration. The saturation line is 8 and the stagnation nudge needs every owned axis at or above it, so the nudge does not waive R3. Declaring the true surface (operability) leaves the round with no lowest-axis claim, which the rule refuses. Calibration also has no reproducible 0–10 mapping (SCORECARD, r61 and r62 lines), so a calibration claim cannot verify as a numeric move: its only honest verdicts are `unprovable` or `unprovable-but-better` with a named non-author reviewer. A label that makes the claim unverifiable is itself evidence of misattribution. | `SCORECARD.md:13–15` (axes rows), `:224–226` (saturation 8, window 3), `SCORECARD.md` r61 "no reproducible 0-10 mapping" lines (≈1401, 1435); `AXES.md` "Working the axes" (lowest-axis rule) | — |
| F4 | **H** | **The clean-tree assertion survives in-run flags and in-run edits (overreach in the claim's own wording).** The writer checks the tree once, before the wrapped command (`git status` at line 131; `ls-files -v` in the candidate is inserted before it). The command then runs on the worktree. Probes: a flag set and bytes forged *during* the command → **base rc=0 and candidate rc=0, RECORD written** (H6). A plain edit during the command → base rc=0, candidate rc=0 (H5). The receipt records no tree state, so the only "clean" assertion the writer makes is the start-of-run refusal. The frozen predicate's `new_forgeries=0` covers seven start-of-run rows only, so the sentence "must not survive index flags" is false for H6 and nothing in the matrix or Named limits states the window. The TOCTOU window is named in the brief but not in any filed text. | `tools/souji-receipt-write.py:131–136` (single check); command run after the behaviour-4 block; probes H5/H6 (§2) | executed, base and candidate both. |
| F5 | **M** | **An honest path the matrix lacks is refused by the rule (whole-index scope).** The candidate runs `git ls-files -v -z` over the whole index. A non-H flag on an unrelated, unmodified path refuses an honest receipt. Probe H1: `notes.txt` (not the command, not the instrument) with `--assume-unchanged` → base rc=0, candidate rc=2 `RECEIPT-INDEX-FLAG-CONCEALED: notes.txt carries index flag 'h'`. The seven rows cannot tell whole-index refusal from command/instrument-scoped refusal, so `new_honest=2` does not measure this harm. Precedent is receipt-scoped (r10 cluster-D helpers name flags "in the receipt scope"); the planned SCORECARD item (`SCORECARD.md:1563`) says "refuse skip-worktree or assume-unchanged entries" with no scope, so the whole-index choice is consistent with the plan but unmeasured. Current harm on this lane: none (17350 × H; `core.sparseCheckout` unset). | `SCORECARD.md:1563`; `census/round-26/waves/assimilation/validate/tools/cand-d1-verify.sh:530–573` (receipt-scoped precedent) | H1 (executed). |
| F6 | **M** | **Row F refuses bytes that are honest and avoidably so.** The candidate refuses a flagged, unmodified file (row F). S291 and the host probe justify refusing a *clean-claim* under a flag, but the writer could hash the on-disk bytes against `HEAD`'s blob without trusting `git status`. That would accept F and still refuse D and E (bytes differ). The frozen design does not take that path. The cost is a named false refusal, not a measured one. | `corpus/knowledge/skip-worktree-concealment.md`; matrix row F | design read; no run. |
| F7 | **M** | **Unmerged paths are reported as concealment.** `git ls-files -v -z` on a merge conflict emits `M f.txt` ×3 (merge rc 1; porcelain `UU f.txt`, probe run this round). The candidate's rule (any non-H tag) would refuse with `RECEIPT-INDEX-FLAG-CONCEALED` for a conflict, which is not concealment. The refusal is correct (unmerged is never a clean receipt); the class is wrong. Not in the matrix. | `git ls-files -v` probe (§2) | probe run; candidate on this state **[INFERENCE from the rule and the observed tag; the writer was not executed on it]**. |
| F8 | **M** | **The do-nothing control is meaningful, but its printed line is incomplete.** Base in the candidate slot: D, E, F accepted (`new_forgeries=3`), A, B accepted (`new_honest=2`), G refused for the `differs` reason, so its class does not match RECEIPT-INDEX-FLAG-CONCEALED (`class_mismatches=1`). The `EXIT=1` therefore has two sources. A refuse-everything tool fails: `new_forgeries=0` but `new_honest=0` (A, B refused). A tool that refuses only command/instrument-scoped flags passes the seven rows exactly as the candidate does, so the rows do not test the scope decision (see F5). The predicted `new_forgeries=3` was reproduced in my probe (not the executor's counter); the do-nothing receipt should pin `class_mismatches=1` too, or it repeats the r61 M2 pattern (prediction in the brief, not checked against a run). | probe rows A–G (§2); `corpus/lessons/round-61.md:45` (M2) | executed (my reimplementation of the candidate, identical block). |
| F9 | **M** | **The class check is a stderr substring.** The counter binds the class to a substring of the writer's stderr. A traceback containing that string counts as a refusal of that class. Named in the brief; not in the filed text. | `tests/fixtures/r60-receipt-write.py` (controls, lines 39–40); counter (executor) | read. |
| F10 | **M** | **The r60 fixture and writer selftest are non-regression only.** Both pass on base and candidate (`SUMMARY cases=8 pass=8 fail=0 control=ALWAYS-WRITE-REJECTED,ALWAYS-REFUSE-REJECTED`, rc 0; `SELFTEST cases=12 pass=12 fail=0`, rc 0). Neither has a flag row, so they cannot show kill power for F4 or F5. The claim should not cite them as evidence for the flag refusal. | probe (§2) | executed both. |
| F11 | **M** | **Frontier: S292 is not yet a sourced row, and S291's "re-open" is a read, not a re-fetch.** `corpus/SOURCES.md` has S290 (line 250) and S291 (line 251) and no S292. The scout's `S62ScoutSources/captures/` was empty at check time (scout still running). I opened `https://git-scm.com/docs/git-ls-files` myself (HTTP 200). It contains the tag definitions the candidate depends on: `H` "tracked file that is not either unmerged or skip-worktree"; `S` "tracked file that is skip-worktree"; `-v` "Similar to -t, but use lowercase letters for files that are marked as assume unchanged". The manual also lists `R` and `C` tags, but `ls-files -v -z` (no `-d`/`-m`) showed `H` for a deleted and a modified tracked file (probe), so the sourced row must scope the invocation. S291 was read from the committed capture (`census/round-61/sources/s291-git-update-index.html`, NOTES paragraph) this round; a live re-fetch with a hash is not evidenced. | `corpus/SOURCES.md:250–251`; `corpus/lessons/round-61.md` Gate; probes (§2) | executed (manual read; capture read). |
| F12 | **L** | **S291 is cited for more than it says.** Its NOTES sentence ("This does not work as expected, since Git may still check working tree files against the index…") supports "the bits are not an ignore mechanism". It does not say `git status` is blind to them. The blindness is the host probe (row D base ACCEPT), which the claim should cite as host evidence (the r61 lesson already says so). | `census/round-61/sources/s291-git-update-index.html` (NOTES) | read. |
| F13 | **L** | **Lesson requirement.** The round lesson needs `## Mistakes` and `## Named limits` with the Q121 disposition of every C/H wave finding. F1–F4 are H and must be carried by number; a `captured-by` of "critic (wave seat)" is the trivial answer Q121 rejects. The fix for F1 must be an instrument (R2 surface class for operability-on-edge-class), not prose. | `QUALITY.md` Q121 (line 322); `corpus/lessons/round-61.md` Mistakes table | — |

## 2. Executed probes (commands and exit codes)

Candidate = base bytes + the frozen block (`ls-files -v -z`, refuse on any tag ≠ `H` with `RECEIPT-INDEX-FLAG-CONCEALED:`), inserted before `# behaviour 7`. Each row uses a fresh `git init` fixture, `rev-parse --show-toplevel` asserted equal to the fixture, throwaway identity, `--allow-outside`, `--instrument tools/instr.sh`, command `python3 -B <fixture>/tools/counter.py`.

| row | base | candidate |
|---|---|---|
| A honest-clean | rc=0 RECORD | rc=0 RECORD |
| B honest-allow-dirty (visible notes edit, `--allow-dirty`) | rc=0 | rc=0 |
| C dirty-visible | rc=2 `refused: lane worktree is dirty` | rc=2 same |
| D skip-worktree + forged counter | **rc=0 (forgery)** | rc=2 `RECEIPT-INDEX-FLAG-CONCEALED: tools/counter.py carries index flag 'S'` |
| E assume-unchanged + forged | **rc=0** | rc=2 `… flag 'h'` |
| F skip-worktree, unmodified | **rc=0** | rc=2 `… flag 'S'` |
| G instrument skip-worktree + forged | rc=2 `worktree tools/instr.sh differs from committed bytes` | rc=2 `RECEIPT-INDEX-FLAG-CONCEALED: tools/instr.sh … 'S'` |

Derived: base `new_forgeries=3` (D,E,F), `new_honest=2`, `class_mismatches=1` (G). Candidate `new_forgeries=0`, `new_honest=2`, `class_mismatches=0`, G refused. Predicate as frozen holds on these rows.

Extra rows (base / candidate):

| probe | base | candidate |
|---|---|---|
| H1 `--assume-unchanged notes.txt`, unmodified, unrelated | rc=0 | rc=2 `… notes.txt … 'h'` (**false refusal**, F5) |
| H2 tracked file deleted, unstaged | rc=2 dirty | rc=2 dirty (`-v` shows `H`; porcelain `D notes.txt`) |
| H3 `git add -N new.txt` | rc=2 dirty | rc=2 dirty (`-v` shows `H`) |
| H4 staged modification | rc=2 dirty | rc=2 dirty (`-v` shows `H`; porcelain `M  notes.txt`) |
| H5 plain edit **during** the command | rc=0 RECORD | rc=0 RECORD (**accepted**, F4) |
| H6 flag **and** forged bytes **during** the command | rc=0 RECORD | rc=0 RECORD (**accepted**, F4) |
| merge conflict (unmerged) `ls-files -v -z` | — | `M f.txt` ×3 (candidate class wrong, F7; candidate not executed on this state) |

Other runs:
- `python3 -B tests/fixtures/r60-receipt-write.py --tool <tool> --work <dir>`: base and candidate both `SUMMARY cases=8 pass=8 fail=0 control=ALWAYS-WRITE-REJECTED,ALWAYS-REFUSE-REJECTED`, rc=0.
- `python3 -B <tool> --selftest --work <dir>`: base and candidate both `SELFTEST cases=12 pass=12 fail=0`, rc=0.
- Lane: `git ls-files -v | awk '{print $1}' | sort | uniq -c` → `17350 H`; `git status --porcelain` → empty.
- Manual: `https://git-scm.com/docs/git-ls-files` → HTTP 200; tag and `-v` text as quoted in F11.

## 3. Answers to the seven attack points

**(a) Axis attribution.** Against the calibration row ("gaps named honestly, confidence graded, overreach caught"; signal "SCORECARD entries match observed repo state") the claim does not survive. Its surface is a runnable writer on an input edge class, which Q59 places on operability; the SCORECARD/SHONEN signal does not move. The same test that rejected r61 C2 (M3, F7) applies here. "Overreach caught" is the rationale for the claim, not a surface class. See F1–F3.

**(b) Blanket refusal.** Refusing row F is the fail-closed side and matches S291's caveat. The honest cases the matrix lacks are: H1 (unrelated flagged path, refused by a whole-index scan), out-of-cone sparse-checkout flags (same mechanism; not present on this lane), F7 (conflict mislabelled as concealment), and the avoidable F refusal (F6). Only H1 and F7 are concrete harms; F6 is a named cost.

**(c) Thin claim.** One claim is legal (1–3 claims, AXES). Under the calibration label it is thin: no SCORECARD/SHONEN movement, and the calibration score cannot move (no reproducible mapping). Relabelled operability it is a real claim with a falsifiable matrix. The R3 obligation then needs a second claim on calibration, or the round fails R3 (F3). The one-claim shape is therefore not honest as filed.

**(d) Frontier.** S292 is not a registry row and its capture did not exist at check time (F11). S291 was read, not re-fetched; "re-opened this round" is not evidenced by a live fetch. The lesson needs `## Mistakes` with F1–F4 carried by number and an instrument-backed captured-by for F1 (F13).

**(e) Do-nothing.** Meaningful: new_honest=2 and class_mismatches=0 defeat refuse-everything. Not sufficient to test scope (F5, F8). Pin `class_mismatches=1` in the do-nothing line.

**(f) Named limits.** Honest but incomplete. The start-of-run TOCTOU must be stated as "start-of-run only" with H5/H6 named, not just "TOCTOU window" in the brief (F4). The class check is by substring (F9). Seven rows only; no whole-index, unmerged, or in-run row (F5, F7, F4). The r60 fixture is non-regression only (F10).

## 4. Weakest sentence and rewrite

**As filed (weakest):** "the receipt writer's clean-tree assertion must not survive index flags that hide worktree divergence."
Refuted by H6 (in-run flag and forgery accepted by base and candidate). "Assertion" is also wrong: the receipt holds no tree state; the only clean check is the start-of-run refusal.

**Rewrite (same claim, narrower wording):** "The writer refuses to start a receipt while any index entry carries a non-H `git ls-files -v` tag, so a `git status`-clean start cannot hide worktree bytes behind an index flag. Changes made while the wrapped command runs are not checked (named limit; probes H5, H6)."

**Second weak sentence:** "S291 … a silent `git status` cannot certify concealment-free content." Rewrite: "S291 NOTES: the bits are not an ignore mechanism (`does not work as expected`); concealment under a flag is host evidence (row D base ACCEPT, git 2.56.0)."

**Axis and shape (required for CLAIM: declare-with-rewrite):**
- C1: axis **operability**; surface class recorded as runnable fixture on an input edge class (Q59); counter and matrix as frozen; the do-nothing line pins `new_forgeries=3` and `class_mismatches=1`; named limits: in-run window (H5/H6), whole-index scope (H1), unmerged class (F7), stderr-substring class (F9).
- C2 (required by R3 once C1 is operability): **calibration**, self-assessment surface only. Before→after: the count of self-assessment statements that describe the writer's flag behaviour as open or routed (`SKILL.md:828–830`, `SCORECARD.md:1563`, the r61 lesson's C2 named-limit text). After the commit, the count is 0 or each remaining statement names the in-run limit. Verifiable by grep at a named revision; no numeric score.
- If the L1 keeps a single calibration claim on the writer surface, the verdict is **refuse** (F1, F2, F3).

**Refuse-form summary for the filed round:** CLAIM: refuse as filed (calibration on a runnable writer; Q59 misattribution; R3-forced). CLAIM: declare-with-rewrite as in §4.
