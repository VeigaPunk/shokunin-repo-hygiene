STATUS: FAIL

Axes: calibration (7), coverage (8).

1. Candidate C1 does not pass the frozen cross-claim probe: the draft tool correctly counts the new C3 F2 entry, but removing C3’s F2 map row produces MISSING-FROM-MAP. This is asymmetric coupling: C1’s measurement is valid only with C3’s map row present, so the claims are not independently verifiable under the literal separability promise (“each verifiable without the others’ files”).

Evidence (all commands used python3 -B; candidate snapshot is a scratch-only commit made from the actual W1 working-tree README and new entry):
- Candidate worktree HEAD was 6deb53561aace9aa14a399f88cf8150da4d4f4bd; that committed snapshot excludes untracked C3 draft files, so it is not a valid C3 candidate. The actual W1 integration draft had modified README.md and untracked corpus/knowledge/git-repo-structure-common-dir.md.
- Scratch candidate revision 91ffd7ebf088b989be2079982f8475b2ae28a6c8 included those actual draft bytes. `python3 -B <W1 draft tool> --root . --rev 91ffd7ebf088b989be2079982f8475b2ae28a6c8` → `grounded=7 mapped=7 dangling=0 mismatches=0` (rc 0). With `--base-rev a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe` → `grounded=7 mapped=7 dangling=0 mismatches=0 kill_tested=6 kill_violations=0` (rc 0). Thus the C3 entry increments grounded and mapped by one; it is not base-grounded and kill_tested remains six.
- In scratch only, removed the appended F2 row and committed as 287ae9ab9617a463e2774b5c99819be3870d4a08. Same tool with `--rev 287ae9ab9617a463e2774b5c99819be3870d4a08` produced `MISMATCH MISSING-FROM-MAP corpus/knowledge/git-repo-structure-common-dir.md ground=F2 map_rows_F2=4` and `grounded=7 mapped=6 dangling=0 mismatches=1` (rc 1). The base-aware command gave same map mismatch plus `kill_tested=6 kill_violations=0` (rc 1).
- Tool reads committed revision bytes (`tools/souji-coverage-agreement.py` lines 54-55; 141, 166-170), so uncommitted README deletion was correctly invisible; scratch commits made probe inputs durable without changing lane state.

2. Scope nuance: C3’s own fixture runs independently of C1 files, but the preregistration explicitly says C1’s real after-run depends on map consistency and that C3’s new entry raises C1 grounded. That acknowledged dependency is real, not just counting noise: removing the C3 row causes C1 to fail. On the stated strict “verifiable without the others” test, this fails separability; the claim scopes overlap via the shared README map.

Smallest safe correction: do not reinterpret or narrow frozen claims. L1 should record C1/C3 as non-separable under the preregistered criterion and avoid counting either as independently admitted on this evidence; any future claim design must isolate C1’s target/input from C3 map edits or preregister the shared-input dependency explicitly before scoring.

Attack log:
- Read preregistration + amendments 1–3 and W1 draft tool, entry, and README map bytes.
- Ran both frozen tool modes against the valid scratch candidate revision.
- Removed only the C3 F2 map row in scratch, committed it there, reran both modes, and observed the frozen MISSING-FROM-MAP failure.
- Removed /var/tmp/souji-r25-CritC1Separability before completion.
