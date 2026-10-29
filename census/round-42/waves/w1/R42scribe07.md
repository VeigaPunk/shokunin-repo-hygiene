# R42scribe07 — round 42 scribe report (draft bookkeeping for the L1)

Seat: R42scribe07 (role scribe, item "Draft bookkeeping text the L1 will apply"). Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`. Freeze commit `afe17f416eec04dcf3f480b580a8f928de61d19d` (HEAD of the lane at the time of this report). Base `bf618f6c5c09d302994871c94903abbea2deb60d`. Instruments commit `b7408095543579ac71b33ecf7b80b0cb8ef45036`.

No tracked file was edited. No git or jj mutation was run in the lane. Everything written is under this seat directory, `.ufo/waves/round-42/w1/R42scribe07/`, which `.gitignore:1` ignores (`.ufo/waves/`). No candidate was scored with `score-candidate.sh` (none was assigned). No tool was installed or upgraded.

## 1. Files and lesson pointers

| file | content | lesson pointers cited |
|---|---|---|
| `.ufo/waves/round-42/w1/R42scribe07/QUALITY-draft.md` | `### Round 42 criteria`, rows Q103-Q105 in the Q98-Q102 table shape (`corpus/QUALITY.md:250-258`), plus three lesson rows the L1 must file (`## Pointer targets`) | Q103 cites `round-42 M42-1`; Q104 cites `round-42 M42-2`; Q105 cites `round-42 M42-3` |
| `.ufo/waves/round-42/w1/R42scribe07/SKILL-rows-draft.md` | six Gate registry rows, eight columns as `SKILL.md:199` and the r41 rows (`SKILL.md:282-286`): `r42-c1-counter`, `r42-c2-counter`, `r42-freeze-check-selftest`, `r42-c3-counter`, `r42-drift-conditions`, `r42-r1-counter` | none (gate rows; each verdict map copied from the counter docstring, `(code)` marks source-only facts) |
| `.ufo/waves/round-42/w1/R42scribe07/README-map-draft.md` | one coverage-map row for the C3 ground, `F1 … condition-level coverage`, status "frontier, unchanged" | none (ground cell starts `F1`, so Q56 reads it as an F1 row) |
| `.ufo/waves/round-42/w1/R42scribe07.md` | this report | — |
| `.ufo/waves/round-42/w1/R42scribe07/receipts/gate-r41-*.out`/`.err`, `gate-r40-716eaa9-nofleet.out` | raw landing-gate outputs (copied from the scratch clone before deletion) | cited by M42-1 |
| `.ufo/waves/round-42/w1/R42scribe07/receipts/pinned-digests-afe17f4.txt` | raw `git show <tip>:<path> \| sha256sum` for the pinned files | cited by the SKILL rows |
| `.ufo/waves/round-42/w1/R42scribe07/receipts/declared-base-tip.txt` | transcription of the two `souji-declared-evidence.py` runs (base and tip), output verbatim | cited by M42-2 |
| `.ufo/waves/round-42/w1/R42scribe07/receipts/python-startup-probe.txt` | transcription of the interpreter-flag probe, output verbatim; the probe directory was deleted | cited by M42-3 and Q105 |

Every `.ufo/waves/...` pointer in the drafts is seat-local. The drafts state the capture rule: the L1 copies each cited receipt to `census/round-42/waves/R42scribe07/` in the landing commit and repoints the pointer (QUALITY Q65). The rows do not resolve until that is done.

## 2. Commands actually run and their observed output

All git calls were read-only. The lane was cloned with `git clone --shared` into `/fast/scratch/hyaku/souji-r42/R42scribe07/clone-tip`; `git -C <clone> rev-parse --show-toplevel` printed the clone dir (TOP_OK). All tool runs used that clone, with `TMPDIR=/fast/scratch/hyaku/souji-r42/R42scribe07`.

1. Lane history (read-only): `git -C <lane> log --oneline -1` → `afe17f4 round-42: preregistration freeze`. `git log --oneline -4 -- corpus/lessons/round-41.md` → `716eaa9`, `31e4d3e`. `git log --oneline -3 -- corpus/QUALITY.md` → `716eaa9`, `832b7bb`, `d86ef3e`.
2. Landing gate at the r41 landing, no fleet root: `python3 -B tools/souji-landing-gate.py --root <clone> --rev 716eaa9 --round 41` → exit 1; 4 findings: `LG-DANGLING-PTR ../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md` (corpus/README.md:217), `…JjTrialSouji.md` (corpus/README.md:217), `.ufo/waves/hyaku/jj-w1/reports/` (corpus/knowledge/jj-colocation-receipts.md:148), `census/round-41/records/census-final.txt` (corpus/lessons/round-41.md:213); `SUMMARY findings=4`.
3. Same rev, `--fleet-root /home/vgpnk/Projects/shokunin` → exit 1; `LG-DANGLING-PTR census/round-41/records/census-final.txt` only; `SUMMARY findings=1`.
4. Freeze tip, no fleet root: `… --rev afe17f416eec04dcf3f480b580a8f928de61d19d --round 41` → exit 1; the three jj-w1 findings; `SUMMARY findings=3`.
5. Freeze tip, `--fleet-root /home/vgpnk/Projects/shokunin` → exit 0; `SUMMARY findings=0`.
6. Round 40 at 716eaa9, no fleet root: exit 1, `SUMMARY findings=3` (`gate-r40-716eaa9-nofleet.out`).
7. Census-file history: `git cat-file -e 716eaa9:census/round-41/records/census-final.txt` → "exists on disk, but not in '716eaa9'"; `git log --oneline -- census/round-41/records/census-final.txt` → `0c9581a round-41: LOG, SCORECARD, README, final census and tip re-measurement`; `git merge-base --is-ancestor 0c9581a 716eaa9` → not an ancestor; `… 0c9581a afe17f4` → ancestor. `git ls-files --error-unmatch` on the path lists it (tracked at the lane index tip).
8. Declared-evidence instrument: `python3 -B tools/souji-declared-evidence.py --root <clone> --file SCORECARD.md --rev bf618f6c5c09d302994871c94903abbea2deb60d` → `assertions=474 resolved=404 skipped=780 mismatches=70`, exit 1. Same at `--rev afe17f416eec04dcf3f480b580a8f928de61d19d` → identical line, exit 1. `git show bf618f6:SCORECARD.md | wc -l` → 839.
9. Pinned digests (`git show afe17f4:<path> | sha256sum`): c1-counter `0ab07cd3…`, c1-items `b2601340…`, c2-counter `fa44392d…`, c2-cases `148b7b87…`, c3-counter `bf0ebf4f…`, c3-mutants `2f6f8df3…`, r1-counter `f2dcbd06…`, pinned drift tool `b2a603cf…`. Each equals the prereg value (full list in `receipts/pinned-digests-afe17f4.txt`).
10. Interpreter probe (Python 3.14.8): with PYTHONPATH on a directory holding `sitecustomize.py`: `python3 -B` → injected line printed; `-s` → printed; `-I`, `-E`, `-S` → not printed. A parent with PYTHONPATH spawning `sys.executable -I` → child not patched (`receipts/python-startup-probe.txt`).
11. Existence of every path the drafts cite, `git cat-file -e afe17f4:<path>`: present for all census/round-42 counters, populations, controls, tools/souji-{declared-evidence,landing-gate,worktree-drift,freeze-check}.py, corpus/{pointer-exemptions.tsv,README.md,QUALITY.md,SOURCES.md}, corpus/lessons/round-{30,31-verifier-spotcheck,41}.md, SKILL.md, SCORECARD.md. Absent, as expected for pending claims: `census/round-42/c1-register.tsv`, `tests/fixtures/r42-drift-conditions.py`, `corpus/lessons/round-42.md`.
12. `git check-ignore -v .ufo/waves/round-42/w1/R42scribe07/QUALITY-draft.md` → `.gitignore:1 .ufo/waves/`.

Not run: no frozen counter (`c1/c2/c3/r1-counter.py`) and no `score-candidate.sh`. No candidate exists to score, and the drafts make no score claim. The SKILL rows quote the counters' targets from their docstrings and the preregistration; they are not measured by this seat.

## 3. Findings the L1 must read before applying the drafts

**F-1 (Q103, M42-1): the r41 "3 without, 0 with" reading holds at the freeze tip only.** The frozen r1 docstring and the prereg's "Mistake to mine" say the same gate printed 3 findings without `--fleet-root` and 0 with it. Measured: true at `afe17f4` (commands 4 and 5) and at the instruments commit (the do-nothing control `census/round-42/controls/r1-control.txt` records `findings=3` at `b740809`). At the r41 landing `716eaa9` the two modes print 4 and 1; the extra finding is `census/round-41/records/census-final.txt` at `corpus/lessons/round-41.md:213`, which lands at `0c9581a`, not an ancestor of `716eaa9`. The r41 N18 text (`corpus/lessons/round-41.md:236-237`) names no mode, and the r41 spot-check (`corpus/lessons/round-41-verifier-spotcheck.md:27`) says "at the tip prints 3" with no mode. The N18 text's own named set (an untracked round-40 file, the ignored round-41 waves) matches none of the sets measured here; I did not reproduce it at any revision [INFERENCE: it describes a different revision or a different fleet state]. The R1 target needs `census-final` to resolve at its landing revision; at `afe17f4` it does.

**F-2 (Q104, M42-2): "no round ran it at its tip" is not what the record shows.** The prereg's `## Frontier step` says the 70 accumulated because no round ran the r22 instrument at its tip. The record: `corpus/lessons/round-30.md:45` reports the counter "went 21 -> 22 at the C1 landing", and `corpus/lessons/round-31-verifier-spotcheck.md:120` reports "21 mismatches at both base and tip". The instrument was run at tips and the nonzero count was recorded as pre-existing and not gated. The draft's wording is the accurate one. Also: the total count is 70 at base and at tip, so a zero-total gate cannot pass without rewriting base lines; the only satisfiable gate is the added-line test (`new_mismatches=0`). The draft says so.

**F-3 (Q105, M42-3): the patch leg reaches fewer classes than "3/3" suggests.** Measured on Python 3.14.8: a `sitecustomize` injected through PYTHONPATH runs under plain and `-s` interpreters; it does not run under `-I`, `-E` or `-S`. A child started with `-I` is unpatched though its parent was patched (`receipts/python-startup-probe.txt`). `c2-counter.py:46-48` and `:337-339` inject through PYTHONPATH and run `python3 -B <tool> --selftest` with that environment, so the patch reaches the self-test's own interpreter only. What the tool itself does with `subprocess` children is unknown until the candidate exists; the draft requires the receipt to say so.

**F-4 (SKILL row for R1): the R1 gate runs with no `--fleet-root` by code, and the R1 control's `r1-control.txt` header records the instruments commit.** The SKILL row states both facts. The control's `EXIT=1` and `rc=1` agree with the counter's exit map.

**F-5 (README row): the status cell must stay "frontier, unchanged".** The F1 row at `corpus/README.md:39` already names the two r40 F1 entries (`docstring-class-continuation-lines-r40`, `drift-record-invalid-utf8-r40`, one hit each), so Q56's entries check is not affected by the new row. The new row names no knowledge entry and must land with its fixture (Q31).

## 4. Named limits of this seat's work

- Only the first 80 lines of each counter were read for docstrings. Exit maps are copied from those docstrings; the R1 exit-2 causes marked `(code)` are from the R1 source (`census/round-42/r1-counter.py`, `main`).
- The pinned digests are the blob digests at `afe17f4`. The prereg's C2 `tools/souji-freeze-check.py` and the C3 fixture do not exist yet; the SKILL rows say so.
- The `declared-base-tip.txt` and `python-startup-probe.txt` receipts are transcriptions of observed output, not raw captures. The probe directory and the scratch clone are deleted. The gate and digest receipts are raw copies.
- No frozen instrument was edited, scored or re-run by this seat.

## 5. Verdict

- **Calibration (drafts):** complete for the three QUALITY rows, each with a lesson pointer that resolves once the L1 files `round-42 M42-1..3`; the SKILL rows and README row are drafted from the docstrings and the measured revisions. F-1 and F-2 correct wording the prereg and the r41 record would otherwise carry into the lesson; the drafts use the measured readings.
- **Operability (drafts):** the six SKILL rows name commands the counters accept as written (`--root`, `--rev`, `--round`, `--scratch` as their docstrings show); the rows for the not-yet-landed fixture and `--selftest` are marked pending. The landing-gate invocation for the R1 row is the one the counter's code runs.
- **Pass/fail of the drafts as text:** not measured. The drafts are not applied; the L1 applies them, runs the frozen counters at the landing commit and quotes their SUMMARY lines with the mode and revision (Q103).

## 6. Checks the L1 should run after applying

1. `python3 -B tools/souji-landing-gate.py --root <lane> --rev <landing> --round 42` and again with `--fleet-root /home/vgpnk/Projects/shokunin`; quote both with their flags (Q103).
2. `python3 -B tools/souji-declared-evidence.py --root <lane> --file SCORECARD.md --rev <landing>` and `python3 -B census/round-42/c1-counter.py --root <lane> --rev <landing>` (Q104).
3. For each SKILL row, run its command as written at the landing revision.
4. `git cat-file -e <landing>:census/round-42/waves/R42scribe07/<name>` for each receipt the drafts cite after the capture copy (Q65).

## 7. Cleanup

The scratch directory `/fast/scratch/hyaku/souji-r42/R42scribe07` (scratch clone, probe directory, gate outputs) is removed before the seat yields. Receipts needed by this report were copied into `receipts/` first.
