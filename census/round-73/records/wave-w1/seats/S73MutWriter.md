# S73MutWriter — mutation test of the stage-W writer byte-truth additions (souji r73, wave 1)

Verdict: C1's frozen detectors reproduce on my bytes (writer selftest 44/44; main arm SUMMARY matrix=80 base_forgeries=15 base_honest=21 base_mismatches=0 new_forgeries=0 new_honest=21 class_mismatches=0 new_echo=0 errors=0 regress=PASS, EXIT=0) and again on restored bytes. But 5 of 14 single-edit mutants keep BOTH detectors green, and 3 of them are reachable: a receipt over a stat-concealed symlink retarget (P5), a receipt over an in-run-forged instrument (P2), and the wrapped command running on an already-concealed forgery (P1). The claim is not falsified as written; its coverage is narrower than its text.

Bytes: stage-W writer blob ab8fb69f… at b84ff90, sha256 d1ad5c79…f7c39; lane file sha256 before=after (never written); mutants exist only in scratch.

Commands (lane root; <S>=/fast/scratch/hyaku/souji-r73/S73MutWriter):
  python3 -B <S>/writer-w.py --selftest --work <S>/base-ws
  python3 -B census/round-73/c1-counter.py --root <lane> --matrix census/round-73/c1-matrix.tsv --base-rev 8b9345b1… --new-tool <S>/<m>.py --work <S>/<m>-main
  python3 -B <S>/probes.py p1|p2|p5

id | edit | selftest | main arm | verdict
M01 | pre-run _truth_refusal dropped | 44/44 | EXIT=0 new_forgeries=0 | SURVIVOR
M02 | post-run _truth_refusal dropped | 43/44 | EXIT=1 new_forgeries=1 cm=2 | killed
M03 | instrument re-compare dropped | 44/44 | EXIT=0 | SURVIVOR
M04 | hash-object --no-filters | 43/44 | EXIT=1 new_honest=20 | killed
M05 | symlink target compare dropped | 44/44 | EXIT=0 | SURVIVOR
M06 | missing path treated clean | 44/44 | EXIT=0 | SURVIVOR
M07 | _porcelain_paths returns empty | 38/44 | EXIT=1 new_honest=20 cm=4 | killed
M08 | _cquote unquoted | 43/44 | EXIT=0 (matrix blind) | killed
M09 | first file only | 43/44 | EXIT=1 new_forgeries=2 cm=3 | killed
M10 | oid != -> == | 15/44 | EXIT=1 new_honest=0 regress=FAIL | killed
M11 | refuse only len(bad)>1 | 43/44 | EXIT=1 new_forgeries=2 cm=3 | killed
M12 | non-regular type check dropped | 44/44 | EXIT=0 | SURVIVOR
M13 | dirty paths hashed too | 38/44 | EXIT=1 new_honest=20 cm=4 | killed
M14 | every index entry skipped | 43/44 | EXIT=1 new_forgeries=2 cm=3 | killed

HIGH S73MutWriter-1 symlink arm unmeasured (tools/souji-receipt-write.py:289-296): no matrix row uses a symlink (only G1/LG1 gitlink); case 44 (:1976) only accepts a stable symlink. P5: stat-concealed retarget, status clean -> pristine rc=2 RECEIPT-WORKTREE-STAT-CONCEALED, M05 rc=0 receipt written.
MEDIUM S73MutWriter-2 pre-run truth call unmeasured (:610-612): case 43's "pre-run" subcase (:1952-1960) passes on the post-run refusal (same class). P1: pristine rc=2 marker=False; M01 rc=2 marker=True -> the wrapped command ran on an already-concealed forgery; the claim's "before the run" is unmeasured.
MEDIUM S73MutWriter-3 post-run instrument re-compare unmeasured (:735-745), shadowed by the truth check: FX3 is refused by the re-compare when the truth check is skipped (M14 FX3 new=refuse new_findings=-) and by the truth check when the re-compare is dropped (M03 EXIT=0). P2 (instrument at rev, absent from index, ignored, --allow-dirty): pristine rc=2; M03 rc=0 with instrument_sha256=f1cc… while worktree instrument=b'forged\n'.
LOW S73MutWriter-4 missing-path branch (:286-288) unreachable in a stable state: status always lists a missing tracked path and listed paths are skipped (:289); only a TOCTOU race reaches it.
LOW S73MutWriter-5 non-regular type branch (:297) unreachable: a directory/FIFO replacement cannot read clean (probe: status=' D tracked.txt').
Note: M08 keeps the main arm at EXIT=0 — the 80-row matrix has no newline/quote/backslash path; only case 44 discriminates _cquote (:227-241).

Files: .ufo/waves/round-73/w1/S73MutWriter.md, .ufo/waves/round-73/w1/S73MutWriter/evidence.txt (mutant hashes, all SUMMARY/EXIT lines, probe output, FX rows), .ufo/waves/round-73/w1/S73MutWriter/mutants/ (pristine writer copy, probes.py, the 14 mutant sources). Scratch /fast/scratch/hyaku/souji-r73/S73MutWriter removed.
Tools installed: none.
