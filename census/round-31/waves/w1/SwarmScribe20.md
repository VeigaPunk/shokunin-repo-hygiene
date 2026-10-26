## Status

STATUS: PASS — M1 for round 28 is delivered as a byte-exact append-only block: the base
landing gate at lane base `9f17a1e` reports 19 `LG-SEAT-UNCARRIED` for round 28 and 0 after the
block is applied in a scratch clone, with the other five findings unchanged and two precision
controls showing the block is not a blanket waiver.

## Evidence

Lane base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc` (branch master, worktree clean); tip read
read-only at `1b811368461785040e955f41f9c97e62f61fd67c`. Scratch clone
`/fast/scratch/hyaku/souji-r31/M1CarryR28/r.TojxNb/c`, cloned `--no-local` with `origin` removed
and a throwaway identity set through `git -C`; `git -C <clone> rev-parse --show-toplevel` printed
the clone. `TMPDIR` exported under the scratch root.

1. Red before — base content, base tool:

```
$ python3 -B tools/souji-landing-gate.py --root <clone> --rev 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --round 28 --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc
SUMMARY	findings=24	checked_reg=62	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=19	status_lines=58	carry_heading=0	checked_reports=61
```

Class split: `19 LG-SEAT-UNCARRIED` + `5 LG-DANGLING-PTR` (rc 1). The 19 markers are the failure
lines of the 19 committed reports under `census/round-28/waves/w1/`; every one of their paragraphs
is a single physical line, so no ellipsis cut was needed.

2. After — block appended to `corpus/lessons/round-28.md` and committed in scratch as
`152f8af33a12a6ddcaa54ae35e492a9b0d215c1f` (1 file changed, 29 insertions; prefix byte-identical,
checked with `diff` against the pre-append copy):

```
$ python3 -B tools/souji-landing-gate.py --root <clone> --rev 152f8af33a12a6ddcaa54ae35e492a9b0d215c1f --round 28 --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc
SUMMARY	findings=5	checked_reg=62	checked_changed=5	checked_pins=13	checked_measured=3	checked_markers=19	status_lines=58	carry_heading=1	checked_reports=61
```

0 `LG-SEAT-UNCARRIED`; the same 5 `LG-DANGLING-PTR` as red-before (sources
`corpus/README.md:217` twice, `corpus/knowledge/jj-colocation-receipts.md:148`,
`corpus/lessons/round-28-verifier-spotcheck.md:71` and `:36`), so the block adds no pointer
surface. `markers=19` and `checked_reports=61` are unchanged.

3. Controls (scratch commits, both from `152f8af`):

```
# ctl1 3a95d115f48ad2f354d7e2953f94e5abbd7daf8e — 20th report with an uncarried FAIL line
LG-SEAT-UNCARRIED	census/round-28/waves/w1/ControlSeat20.md	line 3: STATUS: FAIL — control probe: this failure paragraph has no carry bullet anywhere.
SUMMARY	findings=6 ... checked_markers=20 ... carry_heading=1	checked_reports=62
# ctl2 f3eae0e4313136ee53521365e486e775a1f44534 — one bullet's `open` token replaced by `noted`
LG-SEAT-UNCARRIED	census/round-28/waves/w1/SwarmCritic45.md	line 2: STATUS: PARTIAL — Causality is structurally separable, but control receipts do not establish per-claim no-op failure; L2 floor cannot be certified from opened evidence.
SUMMARY	findings=6 ... checked_markers=19 ... carry_heading=1	checked_reports=61
```

4. Quote fidelity — all 19 bullets compared against the report line in the base blob:
`bullets=19 byte-exact=19 bad=0`.

## Findings

1. The carry is complete and minimal: 19 bullets, one per failure paragraph, 13
   `resolved@<full40>` and 6 `open`. Resolved commits named: `765fe8bd602ac679d01e7a0790711485209ab8bd`
   (9 bullets), `ed270c42161cd62829783a5e5d2ef4e27089331c` (3), `fec846dd1781a414ae3a7d71d2d8fa2fb17900eb` (1),
   `691dd29211c53d0ef94fa072394cb9c8a69fe92e` (1). Location:
   `corpus/lessons/round-28.md` (block), `.ufo/waves/round-31/w1/deliver-m1-carry-r28.append.md` (bytes).
2. Placement constraint for the L1: the base tool's `failures_section_lines`
   (`tools/souji-landing-gate.py:391`) collects a single heading-delimited section and stops at the
   next heading, and `check_carry` (`:475`) reads `.ufo/waves/round-N/` first and only falls back to
   `census/round-N/waves/` when that tree is empty. The block must therefore stay the last section
   and no heading may be inserted between it and end of file. Any later `### R31-CORRECTION` heading
   appended *after* the bullets is harmless.
3. Six dispositions stay `open` and are findings, not noise:
   `census/round-28/sources/SHA256SUMS` still lists only `open.html`, `rename.html`, `fsync.html`
   and omits `git-fetch-zh-HANS-CN.html` (Reviewer33); `corpus/lessons/round-28.md` bodies no
   counting command of its own (Reviewer39 — the only `command:` in the file is inside the R29
   correction block, line 49); `SwarmCritic42`, `SwarmCritic45`, `SwarmMutationTester47`,
   `SwarmMutationTester49` name defects with no resolving commit at HEAD.
4. Residual: the S215 anchor pin was corrected in the row at `ed270c4`, but the same garbled digest
   survives in the round-28 search prose, `corpus/SOURCES.md:186` (`...1811a1abd830...` against the
   file's real `a7f4742d99fd515f1811aabd830a61840939ebe3e12cf1e6792662181b574042`). It is outside
   the 19 paragraphs and outside this item's write scope, so it is reported, not fixed.
5. Residual: `3015` paths under `.ufo/waves/` are still tracked at HEAD although `.gitignore:1`
   ignores `.ufo/waves/` — the ignore rule masks, it does not untrack (Critic43's second clause).
   Their bytes are clean: `git diff --name-only 0c96332 1b81136 -- .ufo/waves/round-26` is empty,
   so the 11 tracked r26 wave modifications seen at wave time are restored.

## Deliveries

- `.ufo/waves/round-31/w1/deliver-m1-carry-r28.md` — what to append, gate pastes, controls, disposition table.
- `.ufo/waves/round-31/w1/deliver-m1-carry-r28.append.md` — the byte-exact block (29 lines, 8392 bytes,
  sha256 `a36739dac77b754341d80b60cdb0af803ac70edec3ec25ea9356fd0dc34ab184`).
- `.ufo/waves/round-31/w1/SwarmScribe20.md` — this report.

## Out of scope / not done

- Mined mistake M1 names rounds 26, 27 and 28; this seat's item names round 28 only. No carry block
  for rounds 26 or 27 was written, and their markers were not enumerated beyond the red-before
  count that this run needed.
- The fixed reading of the C2 instrument (`census/round-31/c2-counter.py`) was not run against the
  scratch clone: its lane leg reads base content by contract, so it cannot see this append.
- No tool was installed or upgraded (`pacman` untouched); no lane git or jj mutation; no credential or
  `op://` material read. Scratch `/fast/scratch/hyaku/souji-r31/M1CarryR28` removed after the
  delivery files were copied into the lane.
