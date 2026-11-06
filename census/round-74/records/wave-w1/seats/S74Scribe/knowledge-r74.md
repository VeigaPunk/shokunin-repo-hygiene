## r74: the lane's own pre-report gate, and a witness scoped to the row (appended 2026-11-06)

**The gate trusted the stat cache too.** `tools/souji-pre-report-gate.sh` check 4 passed `clean` when
`git status --porcelain` printed nothing — the same stat-cache verdict r73 removed from the receipt
writer (S315). One index entry records stat(2) fields, an object type ("4-bit object type valid values
in binary are 1000 (regular file), 1010 (symbolic link) and 1110 (gitlink)", gitformat-index(5), S317)
and the object name side by side; status compares the stat fields, so rewriting them over forged bytes
while keeping the object id reads clean. The frozen gate counter (`census/round-74/c1-gate-counter.py`,
9 rows) over the lane-base gate: a same-size regular-file forge, a retargeted symlink and a
size-changing subdirectory forge each pass `clean` (`census/round-74/controls/c1-K-a-do-nothing.txt`,
mismatches=3 EXIT=1), while the plain edit, untracked file and four honest rows already classify.

**What the gate now does.** After an empty status, check 4 imports the `souji-receipt-write.py` beside
the gate and calls its `_truth_refusal` on the lane: every stage-0 tracked path status did not list is
compared with the object name its entry records — regular files through `git hash-object --stdin-paths`
(which applies check-in conversion, S316), each symlink's target hashed as a blob, gitlinks and
non-stage-0 entries skipped. A missing path, failed read, missing writer or any mismatch fails `clean`.
Measured: `census/round-74/records/c1-after.txt` has GF1-GF3 `expect=FAIL clean=FAIL rc=1 match=yes`,
GH1-GH4 `match=yes`, `SUMMARY rows=9 mismatches=0 errors=0`, EXIT=0. Blanket refusal (mismatches=4,
GH1-GH4) and regular-files-only re-hash (mismatches=1, GF2) stay red
(`controls/c1-K-b-blanket-refusal.txt`, `controls/c1-K-c-regular-only.txt`).

**The counter's witness now reads the row's own paths.** r73's witness credited a row with any worktree
divergence; FWw, FC1 and FC2 always write `.gitattributes` during set-up, so with the forgery removed
they still read witnessed (r73 S73ExecC2). The r74 counter scopes the pre- and post-run divergence
lists to the row's declared forged paths before deciding the witness (`forge_paths`: the row's
`target`, else the path its in-run kind, `chmod_notes` or `index_stat` writes; a row with no declared
path is unwitnessed, fail closed). Pre-freeze probe: all 15 base-accepted refuse rows diverge on their
forged path (`census/round-74/probes/row-scope-pristine.txt`, row_witness=yes 15/15), and each defanged
row diverges only on `.gitattributes` with row_witness=no (`row-scope-D6/D7/D8.txt`, tree_witness=yes).
Measured: D6 FWw, D7 FC1, D8 FC2 each print `base_unwitnessed=1` and `base_witness=no` on the edited
row with EXIT=1 (`records/c2-after-D6..D8.txt`); D1..D5 stay flagged (`records/c2-after-D1..D5.txt`);
the unmutated counter prints `base_unwitnessed=0 base_forgeries=15` EXIT=0
(`records/c2-after-pristine.txt`), where the r73 counter's blanket-unwitnessed forger control prints
`base_unwitnessed=15` EXIT=1 (`controls/c2-before-r73-Kblanket.txt`). On the same three defangs the r73
counter printed `base_unwitnessed=0 base_witness=yes` (`controls/c2-before-r73-D6..D8.txt`).

**The r73 counter survivors are killed by the counter's own selftest.** M08 (a failed witness read
counted as witnessed), M14 (dead symlink-target compare), M15 (dead gitlink skip) and M17 (new-slot
witness reads the pre-run divergence only) are the four r73 mutants that survived. Applied singly to
the r74 counter they print `SELFTEST cases=62 pass=61 fail=1` (M08, M14, M17) and `fail=2` (M15), each
EXIT=1 (`records/c2-after-M08/M14/M15/M17-selftest.txt`); under the r73 counter each printed 52/52
pass, EXIT=0 (`controls/c2-before-r73-M08..M17-selftest.txt`). The unmutated r74 counter prints
`SELFTEST cases=62 pass=62 fail=0` EXIT=0 (`records/counter-selftest.txt`).

**Still not covered.** The counter's forged-path set is a declaration, not an observation of which
bytes the forging step wrote, so a forgery moved to an undeclared path reads unwitnessed (an
under-witness, never a false kill); its witness reads the worktree only, at two points. The gate
inherits whatever conversion `hash-object` applies, so a lying clean filter still fools it (the receipt
writer refuses those; the gate does not); gitlinks and paths status lists are not re-hashed by the gate;
the gate reads the tree once before filing. The lane's other clean-tree tools still trust `git status`
and are named, not claimed here: `tools/souji-verify.sh`, `tools/souji-vault-verify.sh`,
`tools/cand-*-verify.sh`, `tools/souji-record-agreement.py`, `tools/souji-guard.r9-s18.sh`. git 2.56.0 only.
