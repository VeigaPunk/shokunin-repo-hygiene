# SwarmCritic14 — round 31 wave 2, C2 suppression audit (fleet repo & workspace hygiene)

## Status

STATUS: PARTIAL — the C2 suppressor classes are quantified on real lane content, the LG-DANGLING-PTR diff reproduces at three revisions, and two tokenizer rules are shown to lose true positives with reproduced state; no frozen C2 target is falsified and no axis is harmed at the measured readings.

## Evidence

Contract read first: `census/round-31/records/preregistration.txt` (frozen) and `census/round-31/records/amendments.txt` (A0-A5). A3's disclosure is the sentence "the letters-only prose rule cannot tell `corpus/authority` from a real dangling `census/waves`" (amendments.txt, A1/A3 correction block).

Gates used (byte provenance, `git show <rev>:tools/souji-landing-gate.py`):

- base gate at lane base `9f17a1ef571f…`: sha256 `ba37e6bf804db1ad16b2ab53878a6626308bebb854af9bc2e7d230de81cd9056`; identical to the blob at the preregistration `1d45496ae0e5…` (same digest).
- tip gate: `tools/souji-landing-gate.py` sha256 `577f1387ad51fc554f547a2aa4c40754ad73460db359de3178d40b559f09d8b8`; blob `7bfcb9b5a42ff942843e138de1de9ee1b0d83c9b` is unchanged between the C2 landing commit `8024b540b04d…` and tip, so tip readings hold at the claim's landing commit.

Pointer-set diff, `python3 -B <gate> --root <lane> --rev 2c16d018e40db7c23420a2c3bb546b52957bcc25 --round N --fleet-root /home/vgpnk/Projects/shokunin`, N=13..30, serially, both gates:

- base gate at tip rev: 15 LG-DANGLING-PTR (round 19: 4, 20: 6, 23: 2, 24: 1, 28: 2; 0 elsewhere — the pointer pass is gated at `round_no >= 18`, `tools/souji-landing-gate.py:1249`).
- tip gate at tip rev: 2 (round 23 only). Set is a strict subset: 13 removed, 0 added. Same 15→2 at the C2 landing commit `8024b540b04d…` and at base rev `9f17a1ef…`.
- Base gate at base content: 15 = the preregistration's "13 false dangling pointers across rounds 19, 20, 24 and 28" plus the 2 round-23 pointers, which cite genuinely absent paths (`tools/__pycache__/` as a K4 mismatch; `census/round-3/garbage-census.out` described as "The source path cannot be reopened: it is absent", corpus/lessons/round-23-verifier-spotcheck.md:28).
- Attribution of the 13 removed: 7 letters-only prose, 2 `census/round-{18,19}/...seat-audit...json` (new `"..." in raw` skip, `:921`), 3 en/em-dash line ranges (trim fix, `:877`), 1 `.gitignore:fixture/` (trim plus `.captured` mapping, `:878`, `:987`).

Suppression sweep (`deliver-c2-blind-spots-sweep.py`, imports the tip gate by path and reuses its regexes). Rounds 18-30 / 13-17, occurrences = distinct `source:line:token`: prose 7/7 and 3/3; ellipsis 6/6 and 2/2; `:text` 1/1 and 1/1; printf 0/0.

Fidelity: the sweep reproduces the gate's own `checked_ptrs` for all 13 rounds (e.g. round 20: 1331 = 1331) and its dangling counts (round 23: 2 = 2). Distinct token census, rounds 18-30: 2068 existing paths, 7 prose-suppressed, 2 dangling, 60 distinct whole-token skips, 42 empty, 6 non-root, 4 fleet, 20 exempt.

Judgments (line by line, at tip rev):

- 13 distinct letters-only tokens reach the prose test; 6 resolve to real directories (`corpus/knowledge`), 7 are absent and all 7 read as prose slash alternation or a literal grep pattern (table in the delivery). Zero hidden dangling pointers.
- 8 distinct ellipsis tokens; all are cuts of a real or untracked artifact (the four `census/…/X.txt` resolve to `census/round-22/attempt2/sources/X.txt`; the pyc cut resolves to `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc`). Zero hidden dangling pointers. Only the G4 placeholder is skipped *because of the r31 rule*.
- `:text`: 6 trailing-colon forms already handled by `rstrip(".,;:!?")` at base, 1 G6 case, 1 defect (finding 1).
- printf widening: zero `%d`-shaped tokens on the scanned content; the 36 template skips are the pre-existing `round-` cut at `corpus/QUALITY.md:150` (2 distinct tokens).

Reproductions in scratch (`git clone -q --no-local` of the lane, `origin` removed, throwaway identity, probe lines appended to the always-scanned `corpus/README.md`; commits `39b9f9964477…` and `45009205bb7c…`):

- base gate at probe rev: `LG-DANGLING-PTR .ufo/waves/round-16/w1-spec.json:.ufo/waves/round-16/w2-missing.json corpus/README.md:704`, `LG-DANGLING-PTR tools/souji-missing-tool.py corpus/README.md:706`, `LG-DANGLING-PTR tools/missingprobe corpus/README.md:707` (plus the 4 known round-19 false positives).
- tip gate at the same rev: none of the three (0 dangling).
- patched tip implementing both corrections (sha256 `792c53ee5949…`): the pair and the ellipsis path are reported, the G4 placeholder and the prose token are still suppressed; finding sets on rounds 18-30 at rev `2c16d018e40d` and rev `9f17a1ef571f` are byte-identical to the tip gate (26 round-runs, diff empty).

## Findings

1. **Colon-joined pair silently drops its second path.** `_trim_pointer_token` strips `:(?![0-9])[^:\s]*$` (`tools/souji-landing-gate.py:878`) under the docstring's reading that the suffix "names something inside the cited path". For `A:B` with B rooted, B is not inside A and is never resolved. Real occurrence: `corpus/lessons/round-17.md:7` (`--specs .ufo/waves/round-16/w1-spec.json:.ufo/waves/round-16/w2-spec.json`; both elements exist today). Probe shows the tip gate passes `.ufo/waves/round-16/w2-missing.json` that base reported. Harmed axis if a future lesson cites this shape: operability. Not disclosed in A0-A5.
2. **Trailing sentence ellipsis suppresses a complete citation.** `or "..." in raw` (`tools/souji-landing-gate.py:921`) skips any token containing three dots, while G4's class is the interior placeholder. Base handled trailing dots correctly via `rstrip(".,;:!?")`. Probe: `tools/souji-missing-tool.py...` is reported by base and silently skipped by tip. Harmed axis: operability. Not disclosed.
3. **Whole-token skips have no counter.** `_pointer_paths` (`:915-926`) continues before yielding, and `checked_ptrs` increments only for yielded paths (`:1109`). 60 distinct tokens are skipped whole on rounds 18-30 (64 class hits: 38 angle/star, 19 round-placeholder, 5 single ellipsis, 1 triple ellipsis, 1 unbalanced brace; classes overlap) and appear in no SUMMARY field, so `fp=0 real=2` cannot distinguish "nothing cited" from "citation skipped". Harmed axis: operability (instrument transparency); the prose skip at `:1118` is likewise counted but never broken out.
4. **The counter's SHIFT oracle cannot see findings 1-2.** `census/round-31/c2-counter-v3.py:186-189` draws FP probes of the shapes interior-dot placeholder, dash and hyphen line specs, `tools/x.py:<word>`, `round-%02d`, `round-%d`, a `.captured` name and `corpus/<word>/<word>`; `:190-191` draws the four real probes. Neither a colon-joined pair nor a trailing ellipsis on a complete path is generated, and `tests/fixtures/r31-landing-gate-precision.py` tests no such shape either. So `shift=ok` and `fixture=ok` are not evidence that these classes are checked; the residual is undisclosed, unlike the letters-only one.

## Attack log

1. Read the frozen preregistration, A0-A5, the tip gate's pointer scanner, the base-to-tip gate diff (236 lines), the SHIFT leg of `c2-counter-v3.py`, and the r31 precision fixture.
2. Ran base and tip gates for rounds 13-30 at tip rev, diffed both finding sets per round (base-only 13, tip-only 0), repeated at the C2 landing commit and at base rev.
3. Built an instrumented classifier that replays `check_pointers` with the gate's own primitives and reconciled `checked_ptrs` and dangling counts against the gate for all 13 rounds (exact on both).
4. Wrote an independent sweep (delivered) that enumerates the three suppressed classes plus the printf widening, and judged every suppressed token against the cited line and the tree at rev.
5. Probed the two defects with base, tip and patched gates on scratch commits; verified the patch is verdict-neutral on all measured content.
6. Checked the counter's SHIFT probe list and the fixture for both shapes (absent from both).
7. No lane writes beyond the report and delivery files; no counter run in this seat (serial discipline); no `git`/`jj` mutation in the lane; scratch removed after the delivery copy.

## Deliveries

- `.ufo/waves/round-31/w2/deliver-c2-blind-spots.md` — class tables, per-token judgments, defect reproductions, correction and commands.
- `.ufo/waves/round-31/w2/deliver-c2-blind-spots-sweep.py` — reproducible sweep (sha256 `e3c1628abaf8948a8767c2e97b96f4e2be85d78bfd77f2ccefca42e9bfb8f8f3`); rerun with `--root <lane> --rev 2c16d018e40db7c23420a2c3bb546b52957bcc25 --gate <lane>/tools/souji-landing-gate.py`.
