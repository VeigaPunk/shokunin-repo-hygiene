# CriticRoundAdmission — round-18 admission attack (§2–§2b + AXES.md)

STATUS: DONE — 3 real defects (2 material), all measured numbers verify, no axis-harm blocker.

Attacked: admission criteria from `/home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-18.md` §2–§2b and `/home/vgpnk/Projects/shokunin/AXES.md`: lowest-axis rule, sourced claim, causal separability, no-harm-on-any-axis (r14 fixture revert, leaked-process ruling), mined-mistakes shown-able-to-fail, SHONEN. Inspected tip `5efb519f00075d958c3d1109ef6fcb24c487eb87` (lane HEAD = tip, jj-colocated).

## Verified — holds

- **Lowest-axis rule: holds.** SCORECARD.md saturation block: coverage 8, operability 8, calibration 7; saturation line 8. Calibration is the lowest non-retired axis and below the line → nudge inapplicable → the lowest-axis claim is required; C2 targets it. Caveat below (all three rows say "Numeric delta 0, legacy-unmapped" — the rule is satisfied by *claim*, not by *score movement*; calibration stays 7).
- **Sourced claim (§2b.4): holds.** S064–S071 committed in `corpus/SOURCES.md:82-89` with URL, access date 2026-10-20, quotes; lesson Gate records them; SCORECARD C1 row cites S064–S066/S070, C2 S071, C3 S068/S069.
- **C1 numbers verify against the committed record** `census/round-18/c1-matrix-worktree.json` (`invalid_suites: []`): changed r18-bounded 8 PASS / r17-base 5 FAIL, r17-hygiene 29/0, r15-config 20/0, r14-namespace 12/0, selftest checks 36/38/49 → 62, session_cleanup.killed 0 in every suite. `set -m` + `setsid` watchdog present at `tools/souji-census.sh:1478-1500`; bound validation 1..86400 at :246-255; `repo-timeout-unreaped` path at :1641. Protected-refusal exit-2 path intact (tool header :88-104, :168).
- **C2 numbers verify.** `census/round-18/gate-pointers-before-b576341.json`: findings=10 — exactly the 7 ddb7347 citations (SKILL.md:163,165; corpus/README.md:216; jj-colocation-receipts.md:2,44,126,148), `census/operator-sweep-20261019/`, `tests/vault/vadv54-run/p/p6repo/.git`, and one LG-FROZEN-MEASURED (`0123456...` placeholder). Exemptions committed in `corpus/pointer-exemptions.tsv` (3 rows, reasons). `gate-replays-r18.json`: `match: true` on all 5 pinned replays.
- **Every pointer the new gate could flag resolves at tip.** I ran `git cat-file -e 5efb519:<path>` on all 31 distinct repo-relative evidence paths cited by the lesson, SCORECARD, and SHONEN — all OK, including the 20 `.ufo/waves/round-18/w1/*.md` names (106 w1 files committed). The "after → 0" claim is *plausible*; the defect is that its record was never committed (finding D2).
- **R1 verifies.** `census/round-18/jj-receipts-r18-baseb576341.txt:45` — `CASE J13 FAIL ... --as souji` for a kama repo; changed record 35 PASS / 0 FAIL. Fix at `tools/souji-quarantine.sh:247-276` (owner from `git config lane.id` → basename → placeholder).
- **r14 fixture revert is byte-exact and the pin claim is true.** sha256 of working `tests/fixtures/r14-census-boundary.py` = `e6a984b1…d14b2` = `b576341:` blob = `5efb519:` blob = `NAMESPACE_SHA256` at `tools/souji-preservation-evidence.py:307`. History: `3f822e8` and `42d9ff3` both carried modified bytes (`6c1c0cfd…`), reverted in `2fc5f33` — a transient mid-round pin violation, discharged before landing.
- **Leaked-process ruling: honest.** `census/round-18/leak-count-live-1721.json`: 65 = 44 r15-census-config + 14 r17-census-hygiene + 7 other; 58 cwd-deleted. These are *inherited* residue, not round-18 product; the lesson's after-66 delta is attributed to a sibling lane's live runner. The 58 are listed-not-reaped, disclosed in Residuals with an L0 pointer — but see D3.
- **Live pairs: as claimed.** `pair1-base` vs `pair1-changed` identical ex-mtime (21 repos); pair2's mado-shokunin delta is disclosed mid-run write.
- **SHONEN: all `[~]` pointers resolve** (`LOG.md:362`, SKILL `## Decision tables`/`## Error patterns`/`## Checklists`/`## Gate registry` at :42,:74,:115,:135, `tests/fixtures/r13-repo-structure.sh`, `census/round-13/verification.json`, `.ufo/waves/round-13/w1/Overlap.md` at tip). No box ticked → no named-verifier requirement triggered.
- **Causal separability: materially holds.** C1's matrix is its own instrument (run-matrix.py:143 `leftover_processes` is in-runner, not C3 code); C2's gate is a file-resolution check; C3's fixture P1–P11 stands alone. Caveat: C1's *ambient* leak metric uses C3's `leak-count.py`, and C2's `after=0` is only meaningful on the integrated tree — the verdicts remain independently checkable.
- **Mined mistakes §2b.3: M1–M5 each carry "Shown able to fail"** and the evidence exists (gate record, J13 FAIL row, matrix red arms, FixtureReap reports).

## Defects

### D1 — Calibration defect at the round's own target: authority files overstate the r14 fix (material, fixable)

Counterexample: `tests/fixtures/r14-census-boundary.py` at tip is byte-identical to `b576341` (sha256 `e6a984b1…`), and its timeouts use `subprocess.run(timeout=)` (:125,:330,:392) — the exact direct-child-only kill M2 documents as the leak mechanism. If an r14 namespace case ever hangs, it still leaks its session. Yet:

- `corpus/lessons/round-18.md:16` (Mistakes R18-M2 fix column): "session-wide SIGKILL on timeout in the **r14**/r15/r17 fixtures and the r18 runner" — false for r14.
- `LOG.md:951`: "session-wide kill on timeout in the **r14**/r15/r17 fixtures" — false for r14, and LOG is append-only (precedent: correction lands in a later entry, the wrong line stays).
- `corpus/QUALITY.md` Q30 (:79) gets this right — its fixture list is `r15-census-config, r17-census-hygiene, r18-census-bounded, r18 matrix` — so the lesson and LOG are internally inconsistent with the lane's own quality gate row.
- C1's declared premise (lesson :3) "no lane fixture leaves a blocked process behind" is not delivered for r14: the pinned bytes retain the defect class. The lesson discloses the revert in the measurement line (:6), so this is overstated wording, not concealment — but in a round whose axis claim is *authority files must not assert what does not exist at the landing revision*, two authority files assert a fix that does not exist at the landing revision.

Axis harmed: calibration (the round's own). Smallest fix: append a one-line LOG correction and amend the M2 row to "r15/r17 fixtures and the r18 runner; r14 stays pinned (leak class latent, no timeout path measured)".

### D2 — C2's "after" measurement has no committed record (material, fixable)

Counterexample: the counting command's *before* artifact is committed (`census/round-18/gate-pointers-before-b576341.json`), but `ls census/round-18/` contains no after-run record and `git cat-file` finds none; the lesson (:7) resolves "After: the same command at the round tip — see Gate", and the Gate section contains no artifact path or output — only the verdict line. The claim "at 5efb519 round 18 → 0" is therefore unverifiable-as-recorded: the falsifiable before→after pair exists on paper but only one side is an artifact. (I verified every cited path exists at tip, so a re-run will very likely produce 0; the point is the report must carry it.) §2.4 requires "a counting command you can paste into the report, before and after" — paste-able, and the *result* must be evidenced like every other claim in this lane.

Smallest fix: run the same command at `5efb519` (or the final tip), commit `census/round-18/gate-pointers-after-*.json`, cite it in the lesson Gate and report.

### D3 — The declared L0 question about the 58 orphans was never appended (moderate, fixable)

Counterexample: `corpus/lessons/round-18.md` Residuals (:75) routes "58 souji fixture orphans listed, not reaped" as an **(L0 question)**, and C3's Gate (:28) repeats "(L0 question)". `/home/vgpnk/Projects/shokunin/.ufo/l0-questions.md` contains `souji | round-16` and `souji | round-17` entries and no `souji | round-18` line at all (verified by grepping `souji`, `round-18`, `reap|orphan|residue|fixture`). §5 requires any routed operator decision to be appended as `<lane> | round-<N> | <question>`.

Smallest fix: append `souji | round-18 | Disposition of the 58 inherited fixture orphan processes (44 r15 + 14 r17, all cwd-deleted, listed by tools/souji-proc-census.sh): reap under a re-verify-(pid,starttime,boot_id) protocol, or leave as observed residue?` — exactly the shape of the round-17 line.

### D4 — R18-M6 is not "shown able to fail" (minor)

The M6 fix ("session-only cleanup in the runner") has no failing demonstration; its `captured-by` is "the seat's own disclosure", i.e. `none` in the row's own vocabulary. §2b.3's requirement is satisfied by M1–M5, so this is a row-honesty nit, not an admission defect — but the round's stated fix-currency is *demonstrated failure*, and M6's row quietly mints an unshown fix.

### D5 — r14-namespace arm measured unshipped bytes (minor, disclosed)

`c1-matrix-worktree.json` `fixtures_dirty` lists `M tests/fixtures/r14-census-boundary.py`: the recorded r14-namespace 12/0 was measured on the patched copy, later reverted for the pin. The lesson discloses this and FixtureReapR14 measured the patch dead (no timeout triggered), so verdicts are almost certainly identical under pinned bytes — but the shipped claim's evidence ran bytes that are not the shipped bytes. One matrix re-run at tip closes it (bundles with D1's correction).

## Blockers for admission

None that the judge must reject on. D1 and D2 are fixable in-place (LOG correction + lesson edit; one committed after-run record) and are the two items a strict judge should require before closure; D3 needs one l0-questions append (fleet-root write, allowed by §5). Everything else — lowest-axis, sourced claim, separability, no-harm, mined mistakes, SHONEN — verifies against committed evidence.

## Commands run (probe-rule scope: read/grep/sha256sum/git-reads only)

- `git rev-parse HEAD` → `5efb519`; `git log --oneline -6` (above).
- `sha256sum tests/fixtures/r14-census-boundary.py` vs `git show b576341:…` and `git show 5efb519:…` → all `e6a984b1…d14b2`; `git show 3f822e8:…`/`42d9ff3:…` → `6c1c0cfd…`.
- `git log --follow tests/fixtures/r14-census-boundary.py` → modified `3f822e8`, reverted `2fc5f33`.
- python3 JSON dumps of `c1-matrix-worktree.json` (arm × suite verdict counters — all claims match), `gate-pointers-before-b576341.json` (10 findings enumerated), `gate-replays-r18.json` (match:true ×5), `leak-count-live-1721.json` (65 = 44+14+7).
- `git cat-file -e 5efb519:<path>` ×31 → all OK; `git ls-files .ufo/waves/round-18/w1 | wc -l` → 106.
- greps: `corpus/SOURCES.md` S064–S071 rows; `LOG.md:362,949-951`; `corpus/QUALITY.md` Q29–Q32; `tools/souji-census.sh` watchdog sites; `tools/souji-quarantine.sh:247-276`; `.ufo/l0-questions.md` (fleet) for souji r18 → absent; `tests/fixtures/r14-census-boundary.py` timeout sites; `tests/fixtures/r15-census-config.py:269-308` and `tests/fixtures/r17-census-hygiene.py:149-195` session-kill present.
- `awk END NR` on `proc-census-live-1721.tsv` → 67 lines = boot_id + header + 65 rows.

## Tool installs/updates

None.
