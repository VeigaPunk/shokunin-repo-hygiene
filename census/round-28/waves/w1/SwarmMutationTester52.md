# SwarmMutationTester52 — round 28 w1 mutation probe

## Status
STATUS: PASS — kill-rule enforcement verified: a NEW dangling pointer added to SCORECARD.md's Round 28 measurements table is flagged by the landing gate as LG-DANGLING-PTR and counted by the frozen SUMMARY `findings=N` counter (2→3), so any remaining finding fails claim C1; bytes restored exactly and detector output returned byte-identical to baseline.

## Evidence

Probe environment: isolated scratch repo `/var/tmp/souji-r28-SwarmMutationTester52/wt` (`git init`; `git -C … rev-parse --show-toplevel` = that path; verified before first commit). Snapshot = all 5612 lane-tracked files with current worktree bytes; SCORECARD.md 46063 bytes, sha256 `378604924ff6da56d08e28da4244ded97945c6bf3e038cc125b5a0f533092dc0`, byte-identical to the lane file (same sha). Commits: base `b5595ed14e39be4376351d34fd68cded2cf98861`, mutant `7eb35d2648dedae9eff960b251a2dfab2154bb8f`, restored `cb45ee97608c682b602ef8858093c56d81fbed92`.

Detector (frozen counter): `python3 -B tools/souji-landing-gate.py --root <lane> --rev <full40> --round 28 --fleet-root /home/vgpnk/Projects/shokunin`.

Baseline (pristine `b5595ed`), rc 2:
```
LG-DANGLING-PTR	census/round-28/q57-sites.txt	corpus/QUALITY.md:141 cites path absent at b5595ed14e39
LG-FROZEN-MEASURED	tests/fixtures/r15-preservation-frozen/expected.json	measured_commit '005f3d376e5b421c57c4405be37fb10e7ab49381' does not resolve to a commit
SUMMARY	findings=2	checked_reg=52	checked_changed=0	checked_pins=13	checked_measured=0	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=0
COULD-NOT-EVALUATE	no .md reports under .ufo/waves/round-28/ at b5595ed14e39be4376351d34fd68cded2cf98861
```

Mutation (smallest behavior-bearing point): appended to SCORECARD.md a Round 28 measurements table row citing `census/round-28/records/nonexistent.tsv` (file absent in tree; no exemption row matches — verified `corpus/pointer-exemptions.tsv`). sha256 `deadafb5462477a04ae3af05337ab4dcefc22e8dc4354a824cb21867a91826d9`.

Mutant gate run (`7eb35d2`), rc 2:
```
LG-DANGLING-PTR	census/round-28/q57-sites.txt	corpus/QUALITY.md:141 cites path absent at 7eb35d2648de
LG-DANGLING-PTR	census/round-28/records/nonexistent.tsv	SCORECARD.md:287 cites path absent at 7eb35d2648de
LG-FROZEN-MEASURED	tests/fixtures/r15-preservation-frozen/expected.json	measured_commit '005f3d376e5b421c57c4405be37fb10e7ab49381' does not resolve to a commit
SUMMARY	findings=3	checked_reg=52	checked_changed=0	checked_pins=13	checked_measured=0	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=0
COULD-NOT-EVALUATE	no .md reports under .ufo/waves/round-28/ at 7eb35d2648dedae9eff960b251a2dfab2154bb8f
```

Restored gate run (`cb45ee9`): sha256 back to `378604924ff6da56d08e28da4244ded97945c6bf3e038cc125b5a0f533092dc0`; output byte-identical to baseline (`findings=2`, same rows, same SUMMARY).

Verdict: MUTANT KILLED (gate flags the new dangling pointer; frozen counter counts it; findings ≥1 → claim fails per frozen kill rule). Restoration evidence: exact byte hash match + identical baseline output.

## Findings

1. Kill rule enforced at `tools/souji-landing-gate.py` lines 905-992 (`check_pointers`): SCORECARD.md is in the scanned source set (line 920) and a `census/` pointer absent from the tree yields `LG-DANGLING-PTR` (line 985-991); the mutant row at SCORECARD.md:287 (`census/round-28/records/nonexistent.tsv`) was flagged, findings 2→3. Adding any such row to the Round 28 measurements table fails C1.
2. Baseline snapshot `b5595ed` (current lane worktree bytes, 2026-10-25) already carries 2 pre-existing findings: `corpus/QUALITY.md:141` cites `census/round-28/q57-sites.txt` absent (C1 fix mid-flight — file not yet present in worktree) and r15 `tests/fixtures/r15-preservation-frozen/expected.json` has an unresolved `measured_commit`. Both are independent of the probe and do not affect the kill verdict; they are expected to resolve at landing (C1 target findings 2→0).
3. No pointer exemption covers `census/round-28/records/nonexistent.tsv` (`corpus/pointer-exemptions.tsv` holds 4 exact rows; none matches). The mutant is a genuine new finding, not an exempted one.
4. Detector determinism: same bytes → same output (baseline vs restored identical incl. SUMMARY); detector is read-only over the tree (git plumbing only) and never executed repo code.

## Attack log
None — this item is a mutation probe, not an attack. Pre-existing baseline findings are reported as observations, not amendment proposals.
