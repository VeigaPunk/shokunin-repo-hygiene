# ReviewSHONEN — souji-shokunin SHONEN.md (round 13, w1)

Scope: read-only review of `SHONEN.md` against the canonical seed. No file edited. Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Baseline HEAD `31984f4`.

## 1. Canonical source

- Seed: `/home/vgpnk/Projects/shokunin/PROTOCOL.md:439-451` ("The canonical `SHONEN.md` seed (verbatim — `<name>` is the only substitution)"), indented 4 spaces; de-indented block sha256 `f18b9bcc163308dbd21a9ca2f487e24d97544723929ff58db2dd04028e882d48` for `<name>=souji-shokunin`.
- Gate text: `PROTOCOL.md:59-73` (Promotion gates: `[x] <id>` only for a non-author verifier; "the seed below changes only with this gate text").
- File contract: `PROTOCOL.md:432` (byte-identical modulo `<name>`; marks confined to the box character plus one indented evidence line per box).
- Appendix: `PROTOCOL-APPENDIX.md:30` ("Canonical form", r8, historical incident row).
- Lane-side rules: `AGENTS.md`, `corpus/lessons/round-12-verifier-spotcheck.md`.

## 2. Current boxes and named verifiers

| Line | Box | Mark | Evidence line (SHONEN.md) | Named verifier |
|---|---|---|---|---|
| 5 | SKILL.md contains real decision tables, error patterns, checklists, cited sources | `[~]` | 6: `SKILL.md:28`, `:60`, `:85`; `corpus/SOURCES.md` | none |
| 7 | At least one end-to-end domain task executed and logged in LOG.md | `[~]` | 8: `LOG.md:362` | none |
| 9 | Instructions executable by an agent without oral context | `[~]` | 10: `SKILL.md:85-108`; `tests/fixtures/r12-maintenance-guard.sh --selftest` | none |
| 11 | No cross-domain bleed (PROVINCE.md still accurate) | `[~]` | 12: `PROVINCE.md:47-69`; `census/round-12/connector.md §1` | none |

- Named non-author verifiers: **zero**. No `[x]` exists at HEAD, so there is no valid non-author mark to preserve.
- The round-12 spot-check (`corpus/lessons/round-12-verifier-spotcheck.md:12-13`, verifier `W3ReviewSouji`) covers K1–K4 corpus admissions and K5 hold. It names no SHONEN box, so it cannot back a `[x]` on any of the four boxes. Keep all four `[~]`.

## 3. Mechanical conformance

Probe (read-only; temp dir under `/var/tmp`, removed by trap):

- Seed extraction: `sed -n '441,451p' PROTOCOL.md | sed -e 's/^    //' -e 's/<name>/souji-shokunin/g'`.
- SHONEN normalization: delete two-space evidence lines; set each box to `- [ ]`.
- `diff seed.md norm.md` → rc 0, no differences.

Findings:

- **No mechanically noncanonical text found.** Title (`:1`, em dash bytes `E2 80 94`), intro (`:3`), box wording (`:5,7,9,11`), blank-line layout, and `Marks:` paragraph (`:14-15`) match the seed. The file has no CR, no tabs, no trailing whitespace on structural lines, and no whitespace-only lines. Line-end is LF. `git status` shows SHONEN.md clean; last commit `d7266c5`.
- Evidence lines (`:6,8,10,12`) are exactly one per box, two-space indented, and begin with a pointer. This satisfies PROTOCOL.md:432.
- Non-fatal observation: `:8` carries a parenthetical narrative (`operator sweep: 96 pushed-receipt artifacts quarantined, second-checked, removed`). PROTOCOL.md:432 says "no other prose". The pointer resolves, so this is borderline, not a defect. Box 2 must stay `[~]`: the cited sweep was operator-directed (LOG.md:362-366), not a lane-executed task that a non-author has checked.

## 4. Pointer resolution (at HEAD `31984f4`)

| Pointer | Result |
|---|---|
| `SKILL.md:28` `## Decision tables` | resolves (SKILL.md unmodified) |
| `SKILL.md:60` `## Error patterns` | resolves |
| `SKILL.md:85` `## Checklists` | resolves; `:102-106` gate registry; `:108` sources |
| `corpus/SOURCES.md` | present (working tree modified by another seat: `M`) |
| `LOG.md:362` `## 2026-10-19 — operator sweep (execution)` | resolves (LOG.md unmodified) |
| `tests/fixtures/r12-maintenance-guard.sh` | present; SKILL.md:82-83, :106 cite `--selftest` |
| `PROVINCE.md:47-69` | resolves at HEAD: `:47` section header, `:68-69` connector sentence |
| `census/round-12/connector.md §1` | present; §1 "Zero contested scope" (line 15) |

**Drift risk (box 4):** the working tree of `PROVINCE.md` is modified (`M`, +12/-1, uncommitted, outside this seat's write set). The connector sentence moved to `:69-70`. So `PROVINCE.md:47-69` is one line short in the working tree. It also no longer describes F2 as wholly frontier: `:55` now mentions `tools/souji-repo-structure.sh` and the `## Round 13 boundary refinement` section (`:72-80`). Re-point box 4 at integration, not now.

## 5. Proposed change

- Boxes: no change. Keep `:5,7,9,11` as `[~]`.
- Evidence lines: no change at HEAD. At integration, if the PROVINCE edit lands, change `:12` `PROVINCE.md:47-69` to the post-edit range that covers the connector sentence (e.g. `PROVINCE.md:47-70`, verified by reading the file at that time). Do not do this before the PROVINCE edit is committed.
- No new prose, boxes, or verifier names.

## 6. Final checks for L1

1. Seed diff (must be rc 0):
   `R=/home/vgpnk/Projects/shokunin/souji-shokunin; P=/home/vgpnk/Projects/shokunin; T=$(mktemp -d /var/tmp/shonen-check.XXXXXX); trap 'rm -rf "$T"' EXIT; sed -n '441,451p' "$P/PROTOCOL.md" | sed -e 's/^    //' -e 's/<name>/souji-shokunin/g' > "$T/seed.md"; sed -E -e '/^  /d' -e 's/^- \[[ x~]\]/- [ ]/' "$R/SHONEN.md" > "$T/norm.md"; diff "$T/seed.md" "$T/norm.md"`
2. Mark whitelist: `grep -nE '^- \[' SHONEN.md` must show only `[~]`, or `[x] <non-author-id>` with a non-author ID; `[ ]` only if untouched.
3. Evidence count: exactly four lines matching `^  [^ ]`, one after each box.
4. Pointer check: for each evidence path:line, `sed -n 'N p'` must be non-empty; re-verify `PROVINCE.md:47-69` vs working tree before integration.
5. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain -- SHONEN.md` must be empty after L1 integration (no seat writes this file).

## 7. Limitations and tooling

- No non-author verifier exists; this report makes no `[x]` claim. "Canonical" here means text-level conformance only.
- The seed is enforced only by PROTOCOL.md prose. `.ufo/gates/` contains only `root-ledgers`; `scripts/shokunin-watchdog.sh:140-164` (`report_of`) checks for a SHONEN heading, not seed diffs. The `shonen` gate referenced in other lanes' notes is not present in this tree.
- Not verified: content of `census/operator-sweep-20261019/` (excluded by scope); the sourced claims in SKILL.md, LOG.md, and PROVINCE.md beyond pointer resolution; whether `tests/fixtures/r12-maintenance-guard.sh --selftest` passes (not run, per assignment).
- Tools: none installed or updated. Shell utilities only (`sed`, `diff`, `grep`, `od`, `sha256sum`, `git status`).

## 8. Erratum (appended after L1 challenge; prior sections not rewritten)

- **Marks is outside the seed.** PROTOCOL.md:450-451 (`Marks: ...` / `non-author verifier per **Promotion gates**.`) are unindented, outside the indented seed block at PROTOCOL.md:441-448. Sections §1, §3 and §6 above treat those two lines as seed; that is wrong. The canonical seed is PROTOCOL.md:441-448 only, with `<name>` substituted. My earlier "seed diff rc 0" included the Marks lines through a `sed -n '441,451p'` range error; the claim that Marks matches the seed is withdrawn.
- **Prior canonical verdict withdrawn.** The §3 finding "No mechanically noncanonical text found" is not established for the Marks lines; it is established only for the four boxes, the title, and the intro against PROTOCOL.md:441-448. Retract the "Marks paragraph (:14-15) match the seed" statement.
- **Canonical mint template** is at `/home/vgpnk/Projects/kimi-shokunin/templates/mint/SHONEN.md` (per L1). I did not read it; my earlier statement that `templates/mint/SHONEN.md` was absent referred only to the shokunin root path and is correct for that path only.
- **Box marks:** unchanged. All four boxes remain author `[~]`; no `[x]` or non-author verifier is named.
- **Not run:** no further checks were performed in this erratum. The §6 check commands still include Marks in their expected output and should be re-derived from the canonical seed before use.
