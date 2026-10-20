STATUS: DONE — The re-pointed receipt references resolve to the claimed rows, and the permitted landed-tool recheck matches `35/0/2`.

# Attacked claim
Calibration of `corpus/README.md` Round 18 and the corrected citations in `corpus/knowledge/jj-colocation-receipts.md`.

# Findings
None. No actionable documentation defect found in the scoped claims.

# Evidence and verdict
- `corpus/README.md:236-249`: the Round 18 rows retain “outside admission pending” for C1/C2 and keep F5 in the frontier. The linked C1 matrix record marks B1–B8 PASS, `failed=0`, and no leftover processes (`census/round-18/c1-matrix-worktree.json:364-410`). Its recorded census-tool, fixture, and runner hashes (`:428`, `:1752-1756`, `:1764`) match the corresponding files at `5efb519`. The pointer record linked from README row 241 is explicitly a pre-change baseline and records 10 findings (`gate-pointers-before-b576341.json:1-4, 78-90`); the README does not misstate it as a clean post-change result. The lesson independently identifies the 58 round-start souji fixture orphans and leaves their reaping to operator decision (`corpus/lessons/round-18.md:28,75`), consistent with README `:246-248`.
- `corpus/knowledge/jj-colocation-receipts.md:2,3,44,126,148`: both cited record files exist. Line 44’s J3 base/landed pointers resolve to the relevant rows. Line 126’s explicit row citations are correct:
  - `jj-receipts-base5fa6017.txt:15-16` = J1/J1-vault; `:19-21` = J3/J3-vault/J3-quarantine; `:28-29` = J9-file/J9-worktree.
  - `jj-receipts-4f48343.txt:18-19` = J1/J1-vault; `:22-24` = J3/J3-vault/J3-quarantine; `:31-32` = J9-file/J9-worktree.
  Line 148’s brace-expanded filenames match the two committed records.
- The committed base record’s summary is `total=33 failed=13 skipped=2` (`jj-receipts-base5fa6017.txt:51`); the landed record includes J6 PASS under its paired-baseline invocation (`jj-receipts-4f48343.txt:12-13`) and has `total=35 failed=0 skipped=0` (`:54`). That does not conflict with line 3’s separate no-`--baseline-dir` expectation.
- Executed the permitted fixture exactly once from a clone checked out at `5efb519`:
  ```text
  git clone --quiet --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r18w2-RevReadmeKnowledge/lane && git -C /var/tmp/souji-r18w2-RevReadmeKnowledge/lane checkout --quiet --detach 5efb519f00075d958c3d1109ef6fcb24c487eb87
  # no output (quiet clone/checkout)
  cd /var/tmp/souji-r18w2-RevReadmeKnowledge/lane
  bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools
  ```
  Observed J6-verify and J6-vault SKIP for missing `--baseline-dir`; J9-file and J9-worktree PASS using jj 0.45.1; final output: `SUMMARY total=35 failed=0 skipped=2`. The fixture exits 0 when `failed=0` (`tests/fixtures/r17-jj-receipts.sh:1159-1162`). The temporary clone was removed afterward.
- `git diff --exit-code 5efb519f00075d958c3d1109ef6fcb24c487eb87 -- corpus/README.md corpus/knowledge/jj-colocation-receipts.md` produced no output, confirming the reviewed worktree documents matched the assigned tip.

**Verdict: HOLDS.** The line-3 behavior recheck is true at the assigned tip. No baseline-arm rerun or external source fetch was performed; the base failure count was checked against its committed record.

# Residual risk / verification gaps
- `c1-matrix-worktree.json:378-380` records B4’s six expected row labels but only one observed `a/b/c` map. The fixture implementation separately checks both `.gitignore` and `.gitattributes` measured runs (`tests/fixtures/r18-census-bounded.py:969-979`) before marking B4 successful, so this is a retained-detail limitation, not evidence that the README claim is false.
- No `lsp` device was exposed in the available tool inventory. Exact-file grep was used only to locate the B4 serializer; the conclusions above rely on the subsequent source reads and recorded outputs, not grep as semantic proof.
- No tools were installed or updated.