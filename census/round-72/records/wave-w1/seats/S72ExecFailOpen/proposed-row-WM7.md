# Proposed matrix row for a future round (NOT added to the frozen r72 matrix)

Row name: FWc
expect: refuse
expected_class: cannot read filter attributes
base_expect: accept

Why: the r72 writer refuses when `git check-attr` fails (tools/souji-receipt-write.py:169-170 at
0bf098dde7e6eafb62a9ce62b7c16a6291ee1e8e). r71 recorded WM7 as unreachable; this row makes the branch
reachable with a repository-controlled index entry whose path escapes the worktree.

Fixture steps (counter CASE_SPECS mutation kind + build):
1. Base repo: tracked f.txt = "AAAA\n", g.txt = "instrument\n", .gitattributes = "*.txt filter=evil\n";
   commit all three. Repository-local config filter.evil.clean = "sed s/BBBB/AAAA/".
2. Forge worktree f.txt to "BBBB\n" (same 5 bytes). `git status --porcelain` is empty (the clean driver
   maps BBBB back to AAAA).
3. Inject a crafted index entry: duplicate the f.txt entry as "../ev" (same 5-byte path length, same blob,
   mode 100644, stat fields zeroed), entry count +1, drop optional extensions, recompute the SHA-1 trailer
   (helper: add-index-entry.py). `git update-index --cacheinfo`, `git mktree` (slash path) and
   `git read-tree` all reject this path; writing .git/index directly is required.
4. Create <parent-of-top>/ev with the committed f.txt bytes so `git status --porcelain` is exactly
   "A  ../ev" (staged add; no worktree deletion).
5. Run the writer with --allow-dirty (the staged add is the caller-accepted dirty state).

Observed on git 2.56.0 (scratch run, wm7-demo.txt):
- `git ls-files -z :(top)` rc 0, paths include "../ev"; `git ls-files -v -z` rc 0, all H.
- `git check-attr --stdin -z filter ident working-tree-encoding` rc 128,
  stderr "fatal: '../ev' is outside repository at '<top>'" (setup.c:147-155 prefix_path die).
- r72 writer (0bf098dd) rc 2, "refused: cannot read filter attributes of <top>: fatal: ...".
- reference-weak base writer (8b9345b1, sha256 118597e0b537d104a54ac5206f038a364905f65ff8267725457d06ff8952e71f)
  rc 0, writes a receipt (base_expect=accept).
- WM7 mutant (single edit: the refusal replaced by `return out`; sha256
  12882b81a05b84f7c27bdb1cbce775417af42112f6fe43df2964d6cbca5e1d9f) rc 0, writes a receipt over the
  forged f.txt (forgery).

Battery: add WM7 to battery-manifest.tsv with expectation `forgery`; FWc is the only row that makes WM7
forge (the other five members keep their own rows). The WM7 mutant file is the lane-base writer with the
single edit shown in wm7-mutant.diff.
