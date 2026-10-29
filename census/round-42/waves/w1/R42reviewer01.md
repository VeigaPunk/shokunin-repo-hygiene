# R42reviewer01 — independent re-derivation for C1 (calibration)

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin · base bf618f6c5c09d302994871c94903abbea2deb60d · lane HEAD afe17f416eec04dcf3f480b580a8f928de61d19d (freeze)
Frozen inputs verified: `census/round-42/c1-items.tsv` sha256 b2601340…8d39 (matches preregistration); `census/round-42/c1-counter.py` sha256 0ab07cd3…dcd46aa (matches).

## 0. Independence disclosure

The first read of `census/round-42/c1-counter.py` was `sed -n '1,200p' | head -c 20000`, which displayed the `derive()` body before I had written my implementation. I did not consult it again. `derive.py` was written from the docstring rules R1–R4 and the context rule only. The register agreement below is therefore a behavioural check against the rules, and it also agrees with the frozen counter's own `class_ok=70`. It is not a pure blind derivation.

## 1. Independent derivation vs candidate register

Artifacts (seat dir, committed-or-seat only):
- `.ufo/waves/round-42/w1/R42reviewer01/derive.py` (sha256 12bffa62…75f96)
- `.ufo/waves/round-42/w1/R42reviewer01/derived.tsv` (70 rows, my classes, rule that fired, ctx round, result)

Command:
```
TMPDIR=/fast/scratch/hyaku/souji-r42/R42reviewer01 python3 -B .ufo/waves/round-42/w1/R42reviewer01/derive.py
→ items=70
→ Counter({'resolved': 65, 'unresolved': 5}) Counter({'R2': 52, 'R4': 7, 'rev/digest': 4, 'R3': 4, 'R1': 2, 'none': 1})
```
Row-by-row diff (line, token, class, resolved_to) of derived.tsv vs `.ufo/waves/round-42/w1/inputs/c1-register-candidate.tsv` (70 data rows, header identical):
```
70 70
disagreements 0
```
Derived unresolved rows: 14/65817d0d (rev-unresolved), 92/09bb8e0d (rev-unresolved), 68/42259756… and 68/71b89eb3… (digest), 175/c2-after.tsv (path-absent, no `round-23/` candidate, five `round-24..28` candidates exist and R2 needs `round-23/`).
R2 with several matches: none in this population (checked: `R2 multi-match rows: 0`), so the `/waves/` non-waves filter in R2 is never exercised. R1 fires for lines 478 and 525.

Context-round sensitivity: I compared the counter's heading regex (`^#{1,4}\s.*?\bRound\s+(\d+)\b`) with my `^#{1,4} .*Round (\d+)\b` over all 839 base lines: 0 differences. No item line is a heading line, so "heading on own line" does not change any context.

## 2. Frozen counter run on the candidate register (scratch clone only)

```
bash census/round-42/score-candidate.sh c1 /fast/scratch/hyaku/souji-r42/R42reviewer01 census/round-42/c1-register.tsv=<candidate>
→ SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=0 junk=0 rewritten=0 new_mismatches=0   (rc=1, expected: no lesson in this test)
```
`class_ok=70` agrees with my derivation.

## 3. Population reproduction (base tool, base tree)

```
git -C $L show bf618f6c…:tools/souji-declared-evidence.py > tool-base.py   (sha256 a332491607129195f59d289b431cc29fb4c8dc21e10859d552700697a3b09831)
python3 -B tool-base.py --root $L --rev bf618f6c… --file SCORECARD.md --format tsv   → exit 1, 475 rows incl. resolved rows
```
The `mismatch` rows: 70, and they are equal to `census/round-42/c1-items.tsv` both sorted and in order (`sorted equal: True`, `ordered equal: True`). Receipt: `receipts/population-base-tool.tsv`. Population = ok.

## 4. CORRECTION-DE derived values (from the result column and the detail column)

| line | token | result | derived D | source |
|---|---|---|---|---|
| 14 | 65817d0d | mismatch:rev-unresolved | `rev-unresolved` | `git cat-file -t 65817d0d` → fatal: not a valid object name |
| 92 | 09bb8e0d | mismatch:rev-unresolved | `rev-unresolved` | `git cat-file -t 09bb8e0d` → fatal |
| 68 | 42259756a06538a5dfb81cb82fba20737eacdcfd5c06b9b36594071b26f9da44 | mismatch:digest | `sha256=bb506469be860f994f74f4c7d6eb1c949a4931b676cdb60f9f79de041d12f27f` | detail "sha256 is bb506469…" |
| 68 | 71b89eb3c7ce417979c5fce2c759dafe023af21d6310fde49197c766b8f28897 | mismatch:digest | `sha256=bb506469be860f994f74f4c7d6eb1c949a4931b676cdb60f9f79de041d12f27f` | same detail |
| 175 | c2-after.tsv | mismatch:path-absent | `path-absent` | not in tree at base |

Checks on the digest: `git show bf618f6c…:tools/souji-coverage-agreement.py | sha256sum` → `bb506469be86…27f`, which is the digest the detail reports. Line 68 cites that tool as `71b89eb3…` (wrong) and cites `tests/fixtures/r24-coverage-agreement.py` as `42259756…`. The fixture's own base digest is `65d2d681813f5c09…f669`. So the detail for the second token reports the tool's digest, not the fixture's. The instrument binds both digests to the first path on the line. The counter's rule (D = detail digest) yields `bb50…` for both, which is consistent with the rule. Semantically, the `4225…` correction records the digest of the tool file, not of the fixture it names. This is a limit for the L1 to record, not something to edit.

Lesson variants scored with the frozen counter (`score-candidate.sh`, register = candidate, lesson = variant):

| variant | SUMMARY | expected |
|---|---|---|
| A_good (5 correct CORRECTION-DE lines) | `items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | target string matches (rc not captured in this run) |
| B_fenced_dup (5 lines + one duplicate inside ``` fence) | `... corrected=5 junk=1 ...` | junk=1 (fenced) |
| C_prose_mention (5 lines + prose sentence containing "CORRECTION-DE") | `... corrected=5 junk=1 ...` | junk=1 (malformed; consistent with docstring) |
| D_tilde_fence (line 14 inside `~~~` fence, other four outside) | `... corrected=5 junk=0 ...` | junk=1 and corrected=4 under the docstring ("outside code fences") |
| E_fourtick_fence (`````text` block containing a ``` line, then five valid lines) | `... corrected=0 junk=5 ...` | corrected=5 junk=0 under CommonMark |

Receipts: `receipts/A_good.md` … `receipts/E_fourtick_fence.md`.

## 5. Fence handling, rewritten, new_mismatches: docstring vs code

Code (counter `main` tail, read after `derive`): `fenced` toggles on any line whose `lstrip()` starts with three backticks; a CORRECTION-DE line is junk if `fenced`, unmatched, or malformed; `rewritten` is an index comparison of `base_lines` with `rev_lines`; `new_mismatches` counts tool rows with `line > len(base_lines)`.

Findings (each reproduced by a command, not just read):

F1 `rewritten` counts a pure append. `base_lines = score_b.split("\n")` has 840 elements for an 839-newline file (trailing `''` sentinel). A fixture commit that only appends `appended ordinary text line for round 42 fixture` gives `rewritten=1` (command: `counter --rev <appendA>` → `rewritten=1 new_mismatches=0`). Docstring: "keeps every BASE line byte-identical (`rewritten=0`)". A base line is not preserved only if it changes, so the docstring supports 0. Code disagrees. Consequence: any appended SCORECARD row fails C1 even when it is append-only. The current lane tip leaves SCORECARD unchanged (`git diff --quiet bf618f6c… HEAD -- SCORECARD.md` → unchanged), so the target is not affected today.

F2 `new_mismatches` off by one. Threshold is `r[0] > 840`, but the docstring says "beyond the BASE line count", i.e. `> 839`. Fixture appendB appends copies of lines 21 and 22; the base tool at that rev reports `840 c1-after.tsv A mismatch:path-absent` and `841 c2-after.tsv A mismatch:path-absent`. Counter: `new_mismatches=1` (should be 2). Docstring supports `> 839`; code disagrees.

F3 Extra register rows are not rejected. Docstring: register "holds exactly one row per item". Code only looks up item keys. Candidate plus a `999 not-an-item` row: `SUMMARY items=70 population=ok registered=70 class_ok=70 ...` unchanged. Docstring supports rejection; code does not check.

F4 Fence recognition. Docstring: "outside code fences". Code recognises only three-backtick lines. Tilde fence (variant D) is not recognised, so a junk line inside `~~~` counts as corrected. A four-backtick fence (variant E) is closed by the first ``` inside it, so the valid lines after the real close are marked fenced and junked (corrected=0 junk=5). Docstring supports CommonMark-style fences; code disagrees.

F5 (not a current defect, noted) CORRECTION keys are unique per (line, token), so a duplicated unresolved item would need only one line. None exists now (5 unresolved items, 5 unique keys).

## 6. Do the docstring and the code say the same thing?

Partly. Same: the population check, the R1–R4 class rules as exercised here (behavioural agreement, §1–2), the derived CORRECTION value by result, the heading-context rule (0 diffs), and the junk check for duplicates and unmatched lines. Different: F1 (`rewritten`), F2 (`new_mismatches`), F3 (extra register rows), F4 (fences). In each case the docstring is the authority I would follow, and the code is the defect. None of F1–F4 is triggered by the register or by the five correct CORRECTION-DE lines, so C1 is reachable without touching the counter. The conditions the L1 must respect: do not append to SCORECARD (F1), and do not use tilde or four-backtick fences in `corpus/lessons/round-42.md` (F4).

## 7. Verdict

- Register: candidate `c1-register-candidate.tsv` agrees with my independent derivation on all 70 rows. `disagreements (register) = 0`.
- Population: reproduced exactly (70 rows, ordered).
- CORRECTION-DE: five derived values as in §4; variant A reproduces the target SUMMARY string.
- Counter legs: four docstring/code disagreements (F1–F4), each reproduced. They are findings for the L1, not edits (frozen).

Tooling: no installs or upgrades. Scratch `/fast/scratch/hyaku/souji-r42/R42reviewer01` removed after copying receipts into `.ufo/waves/round-42/w1/R42reviewer01/receipts/`. No git mutations in the lane. No writes outside the seat directory.

disagreements=0
(register rows: none. Docstring-vs-code disagreements in the other legs: F1 rewritten sentinel, F2 new_mismatches threshold, F3 extra register rows not rejected, F4 fence recognition.)
