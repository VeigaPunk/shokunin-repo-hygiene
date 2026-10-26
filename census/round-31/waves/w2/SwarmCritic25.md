# SwarmCritic25 — wave-2 audit of the M1 round-27 carry

## Status

STATUS: PARTIAL — the 29 carried paragraphs are byte-exact and the carry is recognized by the gate (`findings=0`, `checked_markers=29`), but 3 of 29 dispositions are wrong (one substantive: a stated defect still stands), so the M1 carry is not honest per entry as claimed.

## Evidence

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`; base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`, prereg `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`, M1 commit `c6108301cbf0ca0ad086ff0ece6b76adad6b74b6`, tip `2c16d018e40db7c23420a2c3bb546b52957bcc25`. Scratch clone with `origin` removed under
`/fast/scratch/hyaku/souji-r31/w2-SwarmCritic25/c` (removed before yield). Every lane call named `-C`.

1. Object: `git -C <lane> diff 9f17a1ef c6108301 -- corpus/lessons/round-27.md` = +41 lines, one append-only section (`corpus/lessons/round-27.md:43-82`), 29 bullets. Tip file is the same plus nothing.
2. Quote exactness: parsed the 29 bullets, read each report at the M1 commit, compared the paragraph at the cited line with the quote under the gate's own `norm_line` (`tools/souji-landing-gate.py:354-363`: NFC, drop `*` and backticks, collapse whitespace, strip). **29/29 equal, 0 diff**; U+2026 count in the section 0, so no bullet uses the ellipsis carry arm.
3. Report bytes stable: `git -C <lane> diff --stat 9f17a1ef 2c16d018 -- census/round-27/waves/w1` empty; `census/round-27/waves/records` also unchanged base..tip.
4. Carry recognition, tip gate in the clone:
   `python3 -B tools/souji-landing-gate.py --root <clone> --rev 2c16d018… --round 27 --fleet-root /home/vgpnk/Projects/shokunin` → `SUMMARY findings=0 … checked_markers=29 status_lines=79 carry_heading=1 checked_reports=94`.
   Base: same gate `--rev 9f17a1ef…` → `findings=32` = 29 `LG-SEAT-UNCARRIED` + 3 `LG-DANGLING-PTR` (three pre-existing fleet pointers, `corpus/README.md:217` ×2, `corpus/knowledge/jj-colocation-receipts.md:148`); without `--fleet-root` 32, with it 29. The preamble's numbers are exact.
5. Disposition checks (full table + per-entry evidence in `deliver-m1-audit-r27.md`): 26 OK, 3 WRONG-RESOLVED, 0 SHOULD-BE-RESOLVED, 0 MISQUOTED.
   - `git cat-file -e 6cb22dc:census/round-27/records/c3-after.tsv` → "exists on disk, but not in '6cb22dc…'"; added in `c973d1a` (`git show --stat`).
   - `git show 2c16d018:census/round-27/waves/records/c1-before.tsv` → `gate_sha256` `e67810d130817879fddd71c5ceeb5d5fd37e6ea8`; `git rev-parse e78ac7c:tools/souji-landing-gate.py` → same value (a SHA-1); added in `765fe8b`, unchanged at tip.
   - `python3 -B tools/souji-axis-check.py --prereg census/round-27/records/preregistration.txt --scorecard SCORECARD.md` in a clone checked out at `6cb22dc` → `claims=3 flags=0`, rc 0.
   - `git show --stat 6cb22dc -- SKILL.md` → 1 insertion, 1 deletion; the row sits at `SKILL.md:226`.
   - `LOG.md:1743` and `SCORECARD.md:223` (r28 planned bullet) verified at tip numbering; `PENDING` count in `SCORECARD.md` at `c973d1a` = 0.

## Findings

1. `corpus/lessons/round-27.md:74` (entry 21, ScoutScorecardState) — **WRONG-RESOLVED**: clause (ii) stands at tip. `census/round-27/waves/records/c1-before.tsv` puts a 40-hex git blob SHA-1 in `gate_sha256`; the basis recomputed the different file `census/round-27/records/c1-before.tsv` (`02b58f81…`). Axis harmed: calibration.
2. `corpus/lessons/round-27.md:60` and `:75` (entries 7, 22) — **WRONG-RESOLVED by hash scope**: both bases rely on `census/round-27/records/c3-after.tsv`, which does not exist at `6cb22dc` and was added at `c973d1a`. Axis harmed: calibration.
3. `deliver-m1-carry-r27.md` basis row 2 (`:55` entry in the lesson) — same artifact swap as finding 1 while the entry stays `open` ("the false-`gate_sha256` clause is gone" is false of the wave receipt). Axis: calibration.
4. `tests/fixtures/r27-pre-report-gate.sh:76-78` — the frozen success line keys on `passes == 4`, not case identity: replacing the case-2 block with a duplicate of case 1 still prints `cases=4 pass=4 control=FALSE-GREEN-REJECTED` rc 0. Entry 16 stays OK for the defect it stated (deleting case 2 now fails). Axis: operability (round-27 C3 evidence is count-based). Not introduced by round 31.
5. Basis rows for entries 4, 5, 20 — false statements: `corpus/pointer-exemptions.tsv` has four rows (not three) at `1b811368` and at tip; the wave-shape/planner record is in the lane at `corpus/lessons/round-27.md:37` ("one v2 wave, 79 seats … L1 performed the planner seat"), not only in the fleet report. Axis: calibration.
6. Entries 13 vs 21 — inconsistent application of the carry's own "any clause" rule: 13 stays `open` with one clause fixed; 21 is `resolved` with one clause standing. Axis: calibration.

Net: no axis target is moved — the C2 lane leg reads base content, and the M1 gate readings reproduce — but the M1 claim's disposition layer is overstated by 3/29 and three of its bases are factually wrong.

## Attack log

- Misquote hunt: normalized every bullet against its report paragraph, including the 716-byte truncated-looking `RevReportIntegrity` line — exact; the "…" seen in terminal output was the tool's 768-byte display cut, not file bytes. No ellipsis prefixes anywhere.
- Ellipsis carry arm abuse: checked `U+2026`/`...` presence in the section (0 U+2026); the gate's `carries()` clause (b) is unused by these bullets.
- Wrong-line-number abuse: 29 cited lines each start their paragraph (29/29 match), so no citation points at a neighbouring paragraph.
- Cross-report carry: 29 bullets, 29 distinct paths, 29 gate markers — no bullet carries two reports, no report carried twice.
- "Should be resolved" hunt: re-read `corpus/lessons/round-28.md` (findings/mistakes/residuals) for later discharges of the 13 `open` items (`__pycache__`, DOI/S118, `census-after`, `[PENDING]` enforcement, spec 80-item, removals) — none found; every `open` retains at least one standing clause. Verified `git ls-tree -r <tip>` still tracks 5 `__pycache__` blobs and `w1-spec.json` still contains `80-item`.
- Defended reading tried and rejected: "clause (ii) meant `census/round-27/records/c1-before.tsv`" — rejected because that file did not exist at the seat's base `e78ac7c` and the seat wrote "the wave's own c1-before.tsv", whose committed copy carries exactly the SHA-1 the seat named.
- Gate false-PASS probe (confirms entry 17's `open`): `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.excludesFile GIT_CONFIG_VALUE_0=<excl>` against an untracked `stray.txt` gave `check-clean=PASS`, rc 0; the same run without the env gave `check-clean=FAIL`, rc 1.
- Fixture mutation probes (entry 16): whole case-2 deletion → `pass=3`, rc 1 (fix holds); case-2 replaced by a duplicate case 1 → `pass=4`, rc 0 (residual, finding 4).
- Preregistration replay at `6cb22dc` (`axis-check` rc 0) to test entry 25 at its own revision; `c3-after.tsv` existence tested per commit (`cat-file -e`) rather than inferred from HEAD.

## Deliveries

- `.ufo/waves/round-31/w2/deliver-m1-audit-r27.md` — 29-row verdict table (OK / WRONG-RESOLVED / SHOULD-BE-RESOLVED / MISQUOTED) with per-entry commands and outputs, quote-exactness method and result, findings F1-F6, limits.
- `.ufo/waves/round-31/w2/SwarmCritic25.md` — this report.

Installs/upgrades this run: none (bash, coreutils, git, python3 stdlib only). Lane writes: none except these two files. Scratch `/fast/scratch/hyaku/souji-r31/w2-SwarmCritic25/` removed after copying deliveries.
