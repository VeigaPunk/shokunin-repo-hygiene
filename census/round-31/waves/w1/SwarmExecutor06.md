# SwarmExecutor06 — r31 C2 implementation (landing-gate reading precision)

## Status

STATUS: PARTIAL — the tool is implemented and delivered, and the C2 LANE leg reads the frozen target at base content (`fp=0 real=2 cne=0 r26=495`), with `regress=same` and every preserved fixture unchanged; the remaining C2 legs (`FIXTURE`, `REDARM`) are unmeasurable from my scratch commit because `tests/fixtures/r31-landing-gate-precision.py` is not committed yet (the counter reports `FIXTURE absent fail` / `REDARM absent fail`, exactly as this item predicted until the fixture seat lands it).

## Evidence

Revisions: lane base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`, lane tip read `1b811368461785040e955f41f9c97e62f61fd67c` (working tree clean, 0 porcelain lines before and after). Scratch clone: `git clone -q --no-local` of the lane into `/fast/scratch/hyaku/souji-r31/C2Gate/r.EScj8f/c`, `origin` removed immediately; patched tool committed there as `7c17cfa381a691df29a2b528af79640503e7b93e` (scratch identity `C2Gate seat <c2gate@example.invalid>`, `core.hooksPath=/dev/null`), one file changed, `+128 −24`. Every later git call used `-C` on that clone. Tools: python3 3.14.8 (`python3 -B` throughout), git 2.56.0. No tool installed, upgraded or downgraded this run; pacman not invoked.

### E1. C2 counter at the patched revision (full output)

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-31/c2-counter.py \
  --root /fast/scratch/hyaku/souji-r31/C2Gate/r.EScj8f/c \
  --rev 7c17cfa381a691df29a2b528af79640503e7b93e \
  --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc \
  --fleet-root /home/vgpnk/Projects/shokunin \
  --scratch /fast/scratch/hyaku/souji-r31/C2Gate/cnt
```

```
LANE round=13 rc=0 reports=32 cne=0
LANE round=14 rc=0 reports=32 cne=0
LANE round=15 rc=1 reports=64 cne=0
LANE round=16 rc=0 reports=141 cne=0
LANE round=17 rc=0 reports=122 cne=0
LANE round=18 rc=0 reports=175 cne=0
LANE round=19 rc=1 reports=67 cne=0
LANE round=20 rc=0 reports=103 cne=0
LANE round=21 rc=0 reports=62 cne=0
LANE round=22 rc=0 reports=248 cne=0
LANE round=23 rc=1 reports=75 cne=0
LANE round=24 rc=1 reports=73 cne=0
LANE round=25 rc=1 reports=80 cne=0
LANE round=26 rc=1 reports=495 cne=0
LANE round=27 rc=1 reports=94 cne=0
LANE round=28 rc=1 reports=61 cne=0
LANE round=29 rc=0 reports=86 cne=0
LANE round=30 rc=0 reports=90 cne=0
LANE-REAL round=23 token=census/round-3/garbage-census.out source=corpus/lessons/round-23-verifier-spotcheck.md:28 reported
LANE-REAL round=23 token=tools/__pycache__/ source=corpus/lessons/round-23.md:69 reported
FIXTURE absent fail
REDARM absent fail
REGRESS tools/souji-landing-gate.py base=(0, 'SELFTEST pass=65 fail=0') rev=(0, 'SELFTEST pass=65 fail=0') same
REGRESS tests/fixtures/r16-landing-gate.py base=(0, 'SUMMARY total=15 failed=0') rev=(0, 'SUMMARY total=15 failed=0') same
REGRESS tests/fixtures/r30-landing-gate-discovery.py base=(0, 'cases=7 pass=7 control=FALSE-GREEN-REJECTED') rev=(0, 'cases=7 pass=7 control=FALSE-GREEN-REJECTED') same
REGRESS tests/fixtures/r19-carry-wrap.py base=(0, 'SUMMARY total=4 failed=0 base_discriminating=2') rev=(0, 'SUMMARY total=4 failed=0 base_discriminating=2') same
SUMMARY fp=0 real=2 cne=0 r26=495 fixture=fail redarm=fail regress=same rev=7c17cfa381a691df29a2b528af79640503e7b93e
EXIT=1
```

No `LANE-FP` line is printed: every one of the base's 13 false dangling pointers is gone, and both REAL members are still reported. Exit 1 is entirely the absent fixture (exit condition lists `fixture`/`redarm`).

### E2. Same counter at the base revision (control, unchanged tool, unchanged content)

```
SUMMARY fp=13 real=2 cne=0 r26=466 fixture=fail redarm=fail regress=same rev=9f17a1ef571f3a510a51ac233d7cf50ac0c871fc
```

The 13 `LANE-FP` lines it prints are the measured set the tokenizer fix removes:

```
round=19 census/round-18/...seat-audit...json                 corpus/lessons/round-19-verifier-spotcheck.md:49
round=19 census/round-19/...seat-audit...json                 corpus/lessons/round-19-verifier-spotcheck.md:49
round=19 tools/souji-seat-audit.py:274–277                    corpus/lessons/round-19-verifier-spotcheck.md:66
round=19 tools/tests/census/corpus                            corpus/lessons/round-19-verifier-spotcheck.md:154
round=20 corpus/authority                                     LOG.md:1106
round=20 corpus/helper                                        corpus/lessons/round-20.md:153
round=20 corpus/knowledge/process-residue-observations.md:58–59  corpus/lessons/round-20.md:370
round=20 corpus/source/QUALITY                                LOG.md:1436
round=20 tests/fixtures/r18-proc-census.sh:395–396            corpus/lessons/round-20.md:370
round=20 tools/kill/killpg                                    LOG.md:1123
round=24 corpus/census/tools                                  corpus/lessons/round-24.md:145
round=28 census/round-26/waves/assimilation/validate/tests/vault/vadv-49/.gitignore:fixture/  corpus/lessons/round-28-verifier-spotcheck.md:71
round=28 corpus/knowledge/registry                            corpus/lessons/round-28-verifier-spotcheck.md:36
```

### E3. Preserved selftest and fixtures, run directly

```
python3 -B .ufo/waves/round-31/w1/deliver-souji-landing-gate.py --selftest | tail -1
SELFTEST	pass=65	fail=0
```
Base blob at the same command: `SELFTEST pass=65 fail=0` (identical last line). Direct runs of the three fixtures against base blob and delivered artifact: `r16 SUMMARY total=15 failed=0`, `r19 SUMMARY total=4 failed=0 base_discriminating=2`, `r30 cases=7 pass=7 control=FALSE-GREEN-REJECTED` — identical on both tools. No selftest case was added.

### E4. G1-G10 read from the frozen contract text (independent mirror, scratch only)

The real fixture was absent, so I wrote a throwaway harness in scratch that builds the ten worlds described in `census/round-31/records/preregistration.txt:8-18` and judges each exactly by its stated PASS condition (G9 compared by containment, since the base tool prints `corpus/knowledge/missing.md:12–14` with its line spec). Verdicts:

```
CASE G1 FAIL base (reports=1)            CASE G1 PASS rev (reports=2, one LG-SEAT-UNCARRIED naming census/round-24/waves/w1/B.md)
CASE G2 PASS base                         CASE G2 PASS rev (reports=1, no LG-SEAT-UNCARRIED)
CASE G3 FAIL base (Y uncarried)           CASE G3 PASS rev
CASE G4 FAIL base                         CASE G4 PASS rev
CASE G5 FAIL base (tools/x.py:274–277)    CASE G5 PASS rev
CASE G6 FAIL base (3 pointers)            CASE G6 PASS rev
CASE G7 FAIL base (round-%d, round-%02d)  CASE G7 PASS rev
CASE G8 FAIL base (3 prose tokens)        CASE G8 PASS rev
CASE G9 PASS base (6)                     CASE G9 PASS rev (6, line spec removed)
CASE G10 PASS base (Z)                    CASE G10 PASS rev (Z)
REDARM base_fails_red=True base_passes_green=True rev_passes_all=True
```

That is the frozen REDARM shape (`preregistration.txt:18`: "REDARM requires the base tool to FAIL G1 G3 G4 G5 G6 G7 G8 and PASS G2 G9 G10."). It is a mirror of the contract text, not the fixture: the fixture seat's worlds may place citations differently, so this is corroboration, `[INFERENCE]` about the eventual `FIXTURE`/`REDARM` legs.

### E5. Patched gate at lane tip content, rounds 26-30

```
python3 -B <deliver> --root <clone> --rev 1b811368461785040e955f41f9c97e62f61fd67c --round R --fleet-root /home/vgpnk/Projects/shokunin
26 SUMMARY findings=26 checked_reg=62 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=26 status_lines=94 carry_heading=0 checked_reports=495
27 SUMMARY findings=29 checked_reg=62 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=29 status_lines=79 carry_heading=0 checked_reports=94
28 SUMMARY findings=19 checked_reg=62 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=19 status_lines=58 carry_heading=0 checked_reports=61
29 SUMMARY findings=0 checked_reg=62 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=7 status_lines=69 carry_heading=1 checked_reports=86
30 SUMMARY findings=0 checked_reg=62 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=2 status_lines=72 carry_heading=1 checked_reports=90
```

Round 26 with the base tool at the same revision: `findings=18 checked_markers=18 status_lines=69 checked_reports=466`; round 28: `findings=21`. Rounds 27, 29, 30 are byte-identical to the base tool's SUMMARY.

### E6. Per-round behavior delta at base content (disclosure)

Same command, base blob vs delivered artifact, `--rev 9f17a1ef…`: rounds 13-18, 21-23, 25, 27, 29, 30 print identical SUMMARY. Differences: r19 `7→3`, r20 `6→0`, r24 `18→17`, r28 `21→19` (all dangling-pointer false positives, carry counts unchanged), r26 `18→26` with `checked_reports 466→495` and `status_lines 69→94` (the 29 capture-only reports now read; their STATUS failure lines are visible and uncarried, which is the M1 carry move's input, not this item's).

## Findings

1. **Report discovery is a union, not a first-tree preference.** `_report_paths` (delivered `tools/souji-landing-gate.py:501`) collects `.md` under `census/round-N/waves/` and `.ufo/waves/round-N/` keyed by relative suffix; the `.ufo` copy wins a shared suffix, so nothing is counted twice. `check_carry` (`:525`) now raises the same `no .md reports under …` could-not-evaluate only when the union is empty. Effect: round 26 `checked_reports=466→495`; base bytes read one tree alone (base docstring, `tools/souji-landing-gate.py:391`-era: "Raw lines under `## Seat-reported failures` until the next heading.").

2. **Every carry section is read.** `failures_section_lines` (`:407`) collects lines under every `## Seat-reported failures` heading instead of breaking at the first heading after the first section, and inserts a blank separator at each section end so `carry_entries` cannot merge a bullet of one section into the previous entry. Behavior-neutral at base content: no lesson of rounds 13-30 has two such sections (counted per round: 1 for 16-25 and 29-30, 0 elsewhere), so the rule bites only through G3/G10 and any appended carry section.

3. **Ellipsis placeholders.** `_pointer_paths` (`:913`) now skips a token containing ASCII `...` as well as `…`; the two round-19 `...seat-audit...json` tokens stop being pointers.

4. **Line specs and `:<text>` suffixes.** `_trim_pointer_token` (`:860`) removes a trailing `:N`, `:N-M`, `:N–M` (en dash) / `:N—M`, `:N,M` before resolution, then a trailing `:<non-digit>` suffix (`census/…/vadv-49/.gitignore:fixture/` → `.gitignore`). This clears 4 of the 13 false positives (r19 ×1, r20 ×2, r28 ×1).

5. **Capture storage names.** `_captured_pointer_path` (`:979`) maps `.git` at any depth to `.git.captured` and a last component `.gitignore`/`.gitattributes` to `<name>.captured`, matching `tools/souji-wave-evidence-capture.sh:219-223` ("Receipt-relative stored path: `.git` components -> `.git.captured`"). `_pointer_candidates` (`:1005`) tries the cited path, its `census/round-N/waves/` capture mapping (r30 rule) and the `.captured` form of either; `check_pointers` (`:1104`) resolves through that list. This clears the round-28 `.gitignore` false positive, and G6's three citations resolve.

6. **Printf templates.** `TEMPLATE_POINTER_RE` (`:160`) now covers printf conversions (`%d`, `%0Nd`, `%02d`, `%.3f`, `%%`, …) besides `%s`, `<N>` and `{N}`, so `census/round-%d/waves/` and `corpus/lessons/round-%02d.md` are templates, not paths (G7).

7. **Prose alternations.** `_prose_pointer` (`:874`) classifies a token with no trailing `/` whose components are all letters only as prose; `check_pointers` (`:1110`) suppresses it before classification and reporting. This clears 7 of the 13 false positives, including `corpus/authority`, `tools/kill/killpg`, `tools/tests/census/corpus`, `corpus/census/tools`, `corpus/helper`, `corpus/source/QUALITY`, `corpus/knowledge/registry`. Disclosed placement: the suppression sits after the exemption bookkeeping, so a letters-only token is still enumerated in `checked_ptrs` and can still consume an exemption row. I put it there rather than in the tokenizer because the frozen selftest case `pointer-exemption-prefix` requires `corpus/runtime` to be enumerated and to consume its exemption (`checked_ptrs=6`, `ptr_exempt=1`, one `LG-DANGLING-PTR` for `corpus/runtime-extra`), and `--selftest` must stay `pass=65 fail=0` for the REGRESS leg. No exemption row in the lane is a letters-only token, so this is not observable in the LANE leg (E1/E2).

8. **Real pointers stay loud.** Both REAL members are still reported (E1), and G9's six absent paths are still six findings with the line spec removed (E4). Nothing was exempted in `corpus/pointer-exemptions.tsv`; the file was not touched.

## Attack log

Not an attack item; no attack filed. Two observations, each with its location, for the L1 rather than as a counter attack:

- The prose rule is a deliberate one-way relaxation of the gate: a genuinely absent letters-only path (`corpus/nowhere`) can no longer be reported. That is what G8 freezes ("a token ... is prose, not a pointer"); it is disclosed, not hidden.
- The union rule pulls `census/round-26/waves/assimilation/**/*.md` into the round-26 report set, so 8 non-seat STATUS failure lines become `LG-SEAT-UNCARRIED` at base content (E6). The counter's own `r26=495` requires reading those paths, so this follows from the frozen contract; it is M1's carry move that disposes of them.

## Deliveries

- `.ufo/waves/round-31/w1/deliver-souji-landing-gate.py` — whole patched tool, 2478 lines, sha256 `7961f68bd398f0c8c38fefec1608d2eda366b2e51ffbb7c3a04571602b3f4e85` (byte-equal to the committed scratch blob `7c17cfa`).
- `.ufo/waves/round-31/w1/deliver-souji-landing-gate.diff` — `diff -u --label a/tools/souji-landing-gate.py --label b/tools/souji-landing-gate.py` from the base blob, 228 lines; `patch -p1` on the base blob reproduces the delivery byte-for-byte (same sha256) and compiles.

Scratch `/fast/scratch/hyaku/souji-r31/C2Gate` (clone, base blob, counter scratch, harness, world repos) was removed after the two files were copied. The lane working tree was not written by me outside the delivery directory, no `git add/commit/stash/checkout/reset` and no jj command ran in the lane, and no path outside `souji-shokunin/` was touched.
