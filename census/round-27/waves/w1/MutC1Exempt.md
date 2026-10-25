# MutC1Exempt — mutation test of C1 exemption approach

## Status
STATUS: PASS — all four mutations of the two proposed exemption rows are detected by the
landing gate; pristine (base + two rows) and restored states both yield `findings=0`
(rc 0). The two exact rows are the minimal correct fix: exemption matching is exact
(`path in exemptions`), so a broader/truncated row neither suppresses the real token nor
silently clears a true defect.

## Evidence
Detector (same command shape as the frozen C1 counter): `python3 -B
tools/souji-landing-gate.py --root <scratch> --rev <full40> --round 27 --fleet-root
/home/vgpnk/Projects/shokunin`.

Scratch: /var/tmp/souji-r27-MutC1Exempt/scratch (git init; verified
`rev-parse --show-toplevel` == scratch; populated from lane `git archive e78ac7c`;
lane object store copied so measured-commit `005f3d3…` resolves). Commits (scratch):
B=e02dbe439ee0d6fae9d41ba448237e3e36d93f80 (base), P=8be9f8282328695552731ca08fc1d06e77a3cf11
(pristine = B + the two rows from w1/exemptions-add.tsv + a probe report under
.ufo/waves/round-27/w1/ so carry evaluates, mirroring the tip environment),
Ma=e6be33cf125cb158c08b81410a679ad60d3a15b7, Mb=8e579b1c86452448399ce218d96163543d457783,
Mc=92bc7dbe0cf66515cf7f393c7b53d64d13190e9b, Md=264106a1b3af6e9c26bf7e9702e82d7435f0f46c.

- base B (no rows): `LG-DANGLING-PTR corpus/knowledge/registry corpus/QUALITY.md:143` and
  `LG-DANGLING-PTR corpus/lessons/round-24.md:232:S118 corpus/QUALITY.md:141`; `SUMMARY
  findings=2` — reproduces the frozen before-counter (rc 2: no round-27 reports at base).
- pristine P: `SUMMARY findings=0` rc 0.
- mutant (a) row1 -> `corpus/knowledge/` + fabricated real dangling citation
  `corpus/knowledge/nonexistent.md` in corpus/knowledge/fabrication-probe.md (committed):
  rc 1, `findings=3` — `LG-DANGLING-PTR corpus/knowledge/nonexistent.md
  corpus/knowledge/fabrication-probe.md:1`, `LG-DANGLING-PTR corpus/knowledge/registry`,
  `LG-DANGLING-PTR-EXEMPT-STALE corpus/knowledge/`. The fabricated real defect is CAUGHT
  (not silently cleared); the original finding reopens; the broadened row self-reports as
  stale.
- mutant (b) row1 tab dropped: rc 2, `COULD-NOT-EVALUATE
  corpus/pointer-exemptions.tsv:5 malformed exemption row (expected unique path<TAB>reason)`.
- mutant (c) row1 empty reason: rc 2, same malformed-row error at line 5.
- mutant (d) row2 -> `corpus/lessons/round-24.md` only: rc 1, `findings=2` —
  `LG-DANGLING-PTR corpus/lessons/round-24.md:232:S118 corpus/QUALITY.md:141` and
  `LG-DANGLING-PTR-EXEMPT-STALE corpus/lessons/round-24.md`.
- restored (git reset --hard P; tsv sha256 17fc4d2da2fc94c7638bcefb156c2c5cacbed126b2f23d100e936d206739452b
  == pristine; probe file gone; worktree clean): `SUMMARY findings=0` rc 0.

Exemption loader (tools/souji-landing-gate.py:876-902) rejects len(fields)!=2, empty
fields[1].strip(), non-unique rows via EvalError (exit 2). Pointer check (lines 955-961)
uses exact membership: `if path in exemptions: used_exemptions.add(path); continue`.
Unused exemptions become LG-DANGLING-PTR-EXEMPT-STALE findings (lines 1106-1114).

Source verbatim (base e78ac7c): corpus/QUALITY.md:143 Q59 prose contains
"a corpus/knowledge/registry change is a coverage surface"; corpus/QUALITY.md:141 Q57 row
begins "For each explicitly enumerated citation of the Round 24 slice tally or row class";
corpus/lessons/round-24.md:232 S118 row contains "DOI → IEEE 202, 0 bytes, twice".

## Findings
1. Exact-match semantics make prefix-broadening inert-but-harmful: mutant (a) left
   `corpus/knowledge/registry` finding, caught the fabricated `corpus/knowledge/nonexistent.md`
   defect, and flagged the broadened row STALE. No over-match/ silent-clear hazard exists,
   so the kill rule's over-match branch is safe by construction.
2. Row 2 must carry the full composite token `corpus/lessons/round-24.md:232:S118`
   (file:line:row): shortening it to `corpus/lessons/round-24.md` reopens the Q57 finding
   (mutant (d)) — `_trim_pointer_token` only strips trailing `:digits` suffixes, so the
   `:232:S118` token resolves as one path.
3. The TSV shape is enforced hard: a missing tab or empty reason aborts the whole gate with
   exit 2 (mutants (b)/(c)) — malformed rows cannot silently disable a check.
4. Both rows are needed and sufficient: with exactly these two rows (pristine), findings drop
   2→0 and every other gate family stays green (checked_reg=50, checked_pins=13,
   checked_measured=3, checked_reports=1); no other dangling pointer exists.
