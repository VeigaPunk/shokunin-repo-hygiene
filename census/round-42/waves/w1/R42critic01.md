# R42critic01 — critic on C1 (calibration): frozen-counter attacks

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. Base bf618f6c5c09d302994871c94903abbea2deb60d. Instruments commit b7408095543579ac71b33ecf7b80b0cb8ef45036.
Pins checked: `census/round-42/c1-counter.py` sha256 prefix `0ab07cd3c99e6bbe` (preregistration `0ab07cd3…`); `census/round-42/c1-items.tsv` sha256 prefix `b2601340eb20f70b` (preregistration `b2601340…`). Both match.
Seat directory: `.ufo/waves/round-42/w1/R42critic01/` (candidates `h0 h1 k1…k18`, each with `score.txt`; `evidence/` holds the hex sweep).
Nothing in the lane, tests/, tools/, census/, corpus/, SKILL.md or any tracked file was written. No git commit, push or mutating git command was run. Scratch `/fast/scratch/hyaku/souji-r42/R42critic01/` is removed before yield.
Tools installed: none.

## Method and commands actually run

1. Read `census/round-42/c1-counter.py` in full, the preregistration C1 block, `c1-items.tsv`, `controls/c1-control.txt`, `tools/souji-declared-evidence.py` (classify/evaluate), and the base SCORECARD cells at lines 14, 21, 31, 68, 69, 92, 175, 184, 478, 487, 489, 525, 839.
2. Built 20 candidate directories (`h0`, `h1`, `k1`…`k18`; each a register and lesson, optionally a SCORECARD or extra root file) and scored each with the frozen harness, exactly:
   `TMPDIR=/fast/scratch/hyaku/souji-r42/R42critic01 bash census/round-42/score-candidate.sh c1 $TMPDIR census/round-42/c1-register.tsv=<file> corpus/lessons/round-42.md=<file> [SCORECARD.md=<file>] [c2-after.tsv=<file>]`
   Every run printed its SUMMARY line; the 20 SUMMARY lines are in the table below and in each `candidate/score.txt`.
3. Checked a candidate's substance claims by hand: instrument at base (read-only, lane) and at a candidate commit in a private fixture clone (`git clone --shared`, toplevel asserted equal to the clone dir, identity by environment, clone removed); `sha256sum` of tracked files for the short digest tokens; `git cat-file -t` on the hex tokens; a sweep of 283 distinct hex tokens in base SCORECARD (`evidence/hex-tokens-base.txt`) for those that do not resolve as commits (`evidence/hex-not-commit-base.txt`).

Verification run (control, from my own scoring): `k14` (appended SCORECARD row citing a missing path) → `new_mismatches=1`, rc 1. The new-line check fires when it should.

## Candidate results

Target: `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0`

| candidate | SUMMARY (verbatim from score.txt) | reaches target? | the gap |
|---|---|---|---|
| h0 honest: register = wave candidate, 5 correct CORRECTION-DE lines (lines 14, 68×2, 92, 175) | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | yes | baseline honest triple; no gap beyond the named limits below |
| h1 honest + one blank-line-prefixed honest SCORECARD row | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | yes | none new |
| k1 correct lines; prose after them says the line-175 correction "was withdrawn … does not hold" | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | yes (substance wrong) | N1 |
| k2 five correct lines inside a multi-line `<!-- -->` block; prose says "No unresolved item remains" | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | yes (substance wrong) | N2 |
| k3 five correct lines inside a `~~~` fence; prose says "No unresolved item remains" | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | yes (substance wrong) | N3 |
| k4 honest triple + committed root placeholder `c2-after.tsv` | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | yes (substance wrong) | N4 (verified: instrument mismatches at base 70, at candidate commit 68; line 175 `c2-after.tsv` flips to `resolved`) |
| k5 blank-prefixed row with `0c1f9a2` in a no-context cell, and self-citation of `corpus/lessons/round-42.md` (created by the same commit) | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | yes (substance wrong) | N5, N7 |
| k6 blank-prefixed row "the 70 tokens … are superseded … no longer count as declared evidence" | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | yes (meaning rewritten) | N6 |
| k7 honest plain append (no leading blank line) of an honest row | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=1 new_mismatches=0` | **no, honest FALSE RED** | N12 |
| k8 honest triple, register written with CRLF line endings (same data) | `SUMMARY items=70 population=ok registered=70 class_ok=0 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **no, honest FALSE RED** | N13 |
| k9 honest triple; one prose sentence contains the literal `CORRECTION-DE` | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=1 rewritten=0 new_mismatches=0` | **no, honest FALSE RED** | N14 |
| k10 honest triple; the format example is documented inside a ``` fence | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=1 rewritten=0 new_mismatches=0` | **no, honest FALSE RED** | N14 |
| k11 honest triple; register has 3 decoy rows whose keys are not population items (`21 c1-after.txt` resolved to a fake path, `14 65817D0D`, `999 ghost.md`) | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | yes (decoys never read) | N10 |
| k12 honest triple + a line whose marker is `CORRECTION<U+200B>-DE` (zero-width space) asserting line 175 is `resolved` to `census/round-28/records/c2-after.tsv` | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | yes (contradicting correction invisible) | N9 |
| k13 honest triple, lesson with CRLF endings | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | yes (honest) | N13 contrast: CRLF passes in the lesson, fails in the register |
| k14 control: appended row citing missing `census/round-42/c1-after-missing.txt` | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=1` (rc 1) | no (correct red) | none; shows the instrument's new-line check is live |
| k15 blank-prefixed row citing `census/round-28/records/c1-after.tsv` as round-42 evidence | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | yes (wrong-round evidence) | N5 |
| k16 honest triple + prose: "`65817d0d` names revision history that the round-26 rebase rewrote out of the lane" | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | yes (false provenance) | N11 |
| k17 blank-prefixed row "tool sha256 `deadbeef…` identical at `bf618f6c`" | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | yes (false digest) | N7 |
| k18 honest triple, UTF-8 BOM before the register header | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | yes (BOM harmless) | N15 |

Scores: 11 substantively wrong candidates reach target (k1 k2 k3 k4 k5 k6 k11 k12 k15 k16 k17). 4 honest candidates are red (k7 k8 k9 k10). h0, h1, k13 and k18 are honest and reach target.

## Named limits (for the L1 and the round lesson)

- **N1 prose unread.** Sentences that retract or contradict a CORRECTION-DE line are not read (k1). L1: read the lesson prose; no sentence may contradict a correction or the register.
- **N2 HTML comments not masked.** A CORRECTION-DE line inside `<!-- … -->` counts as corrected (k2). L1: `grep -n '<!--\|-->' corpus/lessons/round-42.md`; any hit is a finding.
- **N3 tilde fences not masked.** The counter toggles only on lines starting with three backticks, so `~~~` blocks are read (k3). L1: `grep -n '^\s*~~~'` on the lesson.
- **N4 the instrument is not re-run for base rows at rev.** The counter checks only (a) that base lines are byte-identical and (b) new rows beyond the base line count. A committed file can make a base-unresolved token resolve at rev (k4: root `c2-after.tsv`; instrument mismatches 70 at base, 68 at the candidate commit; counter green). L1: run `tools/souji-declared-evidence.py --root <lane> --rev <landed> --file SCORECARD.md --format tsv` and assert the five unresolved items still mismatch; list files the landing commit adds beyond the allowed dests.
- **N5 appended rows are not read for meaning, self-citation or round.** `corpus/lessons/round-42.md` cited by a row of the same commit (k5), and `census/round-28/...` cited as round-42 evidence (k15), pass. L1: read every appended row; every cited path must predate the round and be in the base tree.
- **N6 supersession by appended row.** A row saying base lines 14–832 "no longer count" passes because no base byte changed (k6). L1: read the appended rows as claims.
- **N7 skipped class.** Hex or digest spans with no REV word and no `census/round-N/` in their cell, or with a trailing `…`, are counted `skipped` (780) and never reach population or new_mismatches (k5 `0c1f9a2`; k17 `deadbeef…`). L1: sweep every appended row for hex and `…` spans by hand.
- **N8 unread base tokens (hex sweep).** Of 283 distinct hex tokens in base SCORECARD, 5 do not resolve as commits (`evidence/hex-not-commit-base.txt`): line 14 `65817d0d` (in population), line 92 `09bb8e0d` (in population), line 69 `e13d0c83…` and line 69 `9df0738c…` (not in population), line 184 `20261018` (date-like, not in population). The two line-69 tokens are truncated digests read as `skipped`. `9df0738c` matches `sha256sum` of `tools/souji-receipt-run.py` at commit 778747e (verified; base file sha256 begins `0ed30d44`, so the base cell's `e13d0c83` was not checked against the base tree). Limit: 3 unresolvable-looking tokens are outside the 70.
- **N9 marker match is ASCII-exact.** A line whose marker contains U+200B is neither junk nor corrected (k12). L1: `grep -nP '[^\x00-\x7F]' corpus/lessons/round-42.md`.
- **N10 unmatched register rows are never read.** Decoy rows whose key is not a population item pass (k11). L1: register must have exactly 70 data rows and every key must be a population key.
- **N11 derivation vocabulary has no digest-prefix value.** `65817d0d` is the first eight hex digits of `sha256sum` of `.ufo/waves/round-26/assimilation/validate/tools/souji-declared-evidence.py` (verified: `65817d0d0d4874e8`), so the cell's "tool sha256" is a digest, not a revision. The counter accepts only `rev-unresolved` for it, and prose inventing a rewritten revision passes (k16). The same holds for `09bb8e0d`, which matched no tracked file in my scan (not resolved further). L1: for every `rev-unresolved` token compute prefix sha256 of tracked files and read the cell.
- **N12 false red on an honest plain append.** The base SCORECARD ends with `\n`; the counter splits on `\n`, so base index 839 is the empty string and an honest append without a leading blank line sets `rewritten=1` (k7). A blank-prefixed append passes (h1). L1: a red `rewritten=1` on an append is a counter artifact to be confirmed by a byte comparison, not a candidate fault.
- **N13 false red on CRLF register; inconsistent with CRLF lesson.** The register with CRLF gives `class_ok=0` (k8); the lesson with CRLF passes (k13). L1: LF register is a repo-format fact; check `.gitattributes`.
- **N14 false red on prose or documented format.** Any prose line containing `CORRECTION-DE` (k9), or a documented example in a ``` fence (k10), gives `junk=1`. L1: check the lesson's marker occurrences by hand.
- **N15 header row never read.** The first register line is skipped whatever it contains (k18 BOM). A data row placed first is dropped and goes red, so this gives no green path, but the header's content is unchecked.
- **Finding on the base (not editable).** Base SCORECARD line 839 describes this round's C1 counter as one "that reads correction prose and rejects fenced, duplicate and retracting lines (N1-N4)". The frozen counter reads no prose and rejects no retraction (k1). The L1 should record this overstatement in the round lesson.

## Verdict

The C1 target is mechanical accounting: it is reached by the honest triple h0 and by 11 substantively wrong candidates, and it is missed by 4 honest candidates for format reasons (k7–k10). The counter cannot tell correct substance from wrong substance. Claim C1 holds only if the L1 runs the outside checks in N1–N15 on the landed commit, in particular a re-run of the instrument at the landed revision (N4) and a read of every CORRECTION line and appended row (N1, N5, N6, N11).

## Not done
- No check of the instrument's `c2-after.tsv`-style path claims beyond the counter's rules; no judgment of whether `65817d0d`'s file history was rewritten (not in lane evidence).
- `09bb8e0d` was not traced to a file.
- Attacks on C2/C3 and R1 were out of scope.
