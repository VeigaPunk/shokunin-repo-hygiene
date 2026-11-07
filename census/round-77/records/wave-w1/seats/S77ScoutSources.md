# S77ScoutSources — round-77 source falsification (read-only seat)

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, base `d4f51563`. No lane tracked file edited; no
mutating git/jj. Tooling: none installed/upgraded (nothing needed). Scratch: `/fast/scratch/hyaku/souji-r77/S77ScoutSources` (removed at end).

## Verdicts per item

**1. sha256 of the two new sources — MATCH (both).** Independent of the lane copy.
`curl -sSL` of `v2.56.0/dir.c` → `53e5ed2b3b65409331021ec0075d9405fdd690598ba96cc5ec8077c03b6220a6` =
`census/round-77/srcs/git-dir.c-v2.56.0` = `git clone --depth 1 --branch v2.56.0` checkout `dir.c` (HEAD `a018953688f1`).
`v2.56.0/Documentation/git-add.adoc` → `42089b80b378a7e9711dde024b7ec94a6863378164ea434a34c6af07632e65db` =
`srcs/git-add.adoc-v2.56.0` = clone checkout. `diff -q` on both pairs: identical. Host git 2.56.0.

**2. dir.c add_patterns — HOLDS on open/fstat; the "plain open" half is imprecise (LOW).**
`census/round-77/srcs/git-dir.c-v2.56.0:1164-1167` (13 words, matches S321's quote verbatim):
`if (flags & PATTERN_NOFOLLOW) fd = open_nofollow(fname, O_RDONLY); else fd = open(fname, O_RDONLY);`
`:1169` `if (fd < 0 || fstat(fd, &st) < 0) {` — fstat runs only after open returns. **BUT**: `:1154-1230`
contains **no** `S_ISREG`/`S_ISFIFO`/`S_ISDIR` at all; the only `st.` use is `:1182 size = xsize_t(st.st_size)`.
So git never *checks the type* — it reads a size. The claim "checks its type only afterwards" is wrong in
kind: there is no type check at any point. The operational conclusion (a FIFO source blocks git inside
open(2) before git can act) HOLDS — verified empirically, §Evidence.
`PATTERN_NOFOLLOW` callers: **only** `dir.c:1778-1779` (inside `prep_exclude`, the per-directory
`.gitignore` read). `info/exclude` (`dir.c:3500-3503`) and `core.excludesFile` (`dir.c:3494-3496`) go
through `add_patterns_from_file_1` → `dir.c:1323 add_patterns(fname, "", 0, pl, NULL, 0, oid_stat)` —
flags = 0, **no** `PATTERN_NOFOLLOW`. Tree-wide grep over the v2.56.0 clone: `PATTERN_NOFOLLOW` occurs only
at `dir.c:1143,1164,1779`. `open_nofollow` = `wrapper.c:828-861`: `open(path, flags | O_NOFOLLOW)`;
**O_NOFOLLOW affects only symlinks, not FIFOs** — so a FIFO `.gitignore` still blocks (verified). S321's
"per-directory .gitignore with O_NOFOLLOW, info/exclude and core.excludesFile without" HOLDS exactly.

**3. attr.c — HOLDS for the mechanism; the S064 quote's line anchors are off (LOW).**
`attr.c:693-733 read_attr_from_file`; `:702-705` `if (flags & READ_ATTR_NOFOLLOW) fd = open_nofollow(path, O_RDONLY);
else fd = open(path, O_RDONLY);`; `:712 if (fstat(fd, &st))` — fstat after open, and no `S_IS*` test
anywhere in 693-733. Callers: `READ_ATTR_NOFOLLOW` passed only at `:937` (root `.gitattributes`) and
`:1028` (per-directory `.gitattributes`); **not** at `:942` (`info/attributes`), `:932`
(`core.attributesFile`/global), `:926` (system-wide). Lane row **S064** (`corpus/SOURCES.md:99`) cites
"read_attr_from_file :699-718, bootstrap_attr_stack :940-948" and says info/attributes "is opened with a
plain blocking open(path, O_RDONLY)". The mechanism HOLDS (verified), but S064's cited line ranges are
**wrong**: at v2.56.0 the function is `:693-733` and `bootstrap_attr_stack` is `:910-948` (its
`info/attributes` read is `:942`, not 940-948). Its "no pre-open guard in git" HOLDS. It also omits that
`.gitattributes` *is* NOFOLLOW-guarded while `info/attributes` is not — the asymmetry that decides n5 vs n6.

**4. git-add.adoc — HOLDS.** "Allow adding otherwise ignored files." at
`srcs/git-add.adoc-v2.56.0:78` (5 words ≤ 25), under OPTIONS `-f`/`--force`. Context `:40-43`:
"The `git add` command will not add ignored files by default. You can use the `--force` option to add
ignored files." It grounds the capture of an ignored file at its own path. git-scm.com/docs/git-add
serves the **same sentence** and the same version: the page carries "git-add last updated in 2.56.0" and
a `git-add/2.56.0` anchor. **Caveat (MEDIUM):** the lane helper does not use `git add -f` — it uses
`jj file track --include-ignored` (`/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh:658`), and jj
0.45.1's own help says "--include-ignored: Track paths even if they're ignored or too large". S322's
"knows" cell asserts git-add(1) "semantics" for a **jj** flag; git-add(1) does not describe jj. The
behaviour is true (jj help confirms it) but the citation grounds a different tool's semantics.
`git add -f` on an ignored path was separately verified to work in a fixture (`ADD_F_OK`/`COMMIT_OK`).

**5. Duplicate check — REJECT duplicate concern; ADMIT both rows.** At base `d4f51563`,
`corpus/SOURCES.md` has `grep -c 'dir\.c'` = 1 (a prose mention inside S319's "knows" cell, **not** a dir.c
row) and `grep -c 'git-add'` = 0 — the lesson's figures at `corpus/lessons/round-77.md:79-80` reproduce
exactly. `grep -c 'attr\.c'` = 1 (S064 itself). So S321 (dir.c/add_patterns open+type) and S322
(git-add --force) are both **within-scope, non-duplicate** rows; admit both.

## Findings

- **MEDIUM** — S322's "knows" cell (`corpus/SOURCES.md:281`) attributes to git-add(1) the semantics of
  `jj file track --include-ignored`, which git-add(1) does not state. Fix: cite jj's own docs/help for
  the jj flag, and keep git-add(1) only for the git-side equivalence.
- **MEDIUM** — the frozen C1 rule says "a symlink counts by its target", but the candidate gate
  (`tools/souji-pre-report-gate.sh` at `9b496b08`) implements that only on its `$GIT_DIR`/config branch
  (`[[ -e $f && ! -f $f ]]`, which follows symlinks). Its work-tree branch uses
  `find … ! -type f -print` **without** `-L`, so a symlink→regular-file `.gitignore` is counted as
  non-regular (find-count=1) while the same symlink on the `$GIT_DIR` branch is not counted. Verified in
  a fixture: symlink→regular `.gitignore` ⇒ find-count=1 but the git-dir test says "not counted". The two
  branches disagree about the same file. Note git itself reads such a symlink with ELOOP
  ("Too many levels of symbolic links"), so the work-tree branch is the stricter one — but the rule text
  and the implementation disagree, and the r77 population has no row pinning it (n10 is a symlink→FIFO on
  the `$GIT_DIR` branch only).
- **LOW** — the preregistration/counter wording "checks its type only afterwards" (and S321's "the fstat
  type read follows at line 1169") mis-describes the code: `add_patterns` never tests `S_ISREG`; the
  fstat feeds `st.st_size`. The blocking claim is unaffected.
- **LOW** — S064's line anchors (`read_attr_from_file :699-718`, `bootstrap_attr_stack :940-948`) do not
  match v2.56.0 (`:693-733`, `:910-948`). Also S064 omits the `READ_ATTR_NOFOLLOW` asymmetry that
  separates `.gitattributes` from `info/attributes`.
- **LOW** — the lane's S321/S322 rows are still **uncommitted** at `ef04ca6c` (`git show HEAD:corpus/SOURCES.md |
  grep -c '^| S32[12] '` = 0; both rows live only in the working tree, `git diff corpus/SOURCES.md`).
  They are also dated `2026-11-07`, one day ahead of the local date of the `23:0x` capture.
- **LOW** — the prereg's C1 surface says a FIFO `.gitattributes` "blocks the lane-base gate"; empirically
  a FIFO `.gitattributes` blocks `git status` only when the work tree has tracked files (git consults
  attributes when it must compare index entries); with an empty index `git status` returns clean and only
  the writer's `check-attr` blocks. The hang is real for the counter's rows (which have tracked files).

## Evidence (commands + deciding output)

FIFO blocking (git 2.56.0, real fixtures, `os.killpg` on expiry, 8 s bound; `rc=HUNG` = blocked):
```
A fifo .gitignore: rc=HUNG t=8.0s      B fifo info/exclude: rc=HUNG t=8.0s
n4 FIFO core.excludesFile: rc=HUNG      n4b symlink core.excludesFile->FIFO: rc=HUNG
n5 git status w/ FIFO sub/.gitattributes: rc=HUNG   n6 FIFO info/attributes: git STATUS rc=HUNG, check-attr rc=HUNG
n7 FIFO core.attributesFile: git STATUS rc=HUNG, check-attr rc=HUNG
D symlink .gitignore -> FIFO (PATTERN_NOFOLLOW): rc=0 err="warning: unable to access 'sub/.gitignore': Too many levels of symbolic links"
E symlink info/exclude -> FIFO (no NOFOLLOW): rc=HUNG
G4 symlink .gitattributes->FIFO: rc=0 err="Too many levels of symbolic links"   G5 symlink info/attributes->FIFO: rc=HUNG
n8 FIFO .gitignore in ignored dir: rc=0   (git does not descend — the policy row, not a hang row)
C regular info/exclude: rc=0 out='?? sub/file.txt'
```
O_NOFOLLOW does not exempt FIFOs: `os.open(fifo, O_RDONLY|O_NOFOLLOW)` under `timeout -k 1 3` → rc 124
(blocked); the same call on a regular file → rc 0 `OPENED`.
Gate branch divergence: symlink→regular `.gitignore` ⇒ `find … ! -type f -print` prints it (count=1);
`[[ -e $f && ! -f $f ]]` ⇒ "not counted".
`open_nofollow` = `wrapper.c:828-861` `open(path, flags | O_NOFOLLOW)`; tree-wide `PATTERN_NOFOLLOW`
grep → `dir.c:1143,1164,1779` only; tree-wide `add_patterns(` → `dir.c:1266,1323,1778` only.
`git clone --depth 1 --branch v2.56.0` HEAD `a018953688f1b10bddf91bff8747068f5f4746a4`; `git describe` = v2.56.0.

## Files written
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-77/w1/S77ScoutSources.md` (this report).
- Scratch only (removed before yield): `/fast/scratch/hyaku/souji-r77/S77ScoutSources/` (upstream fetches,
  a v2.56.0 clone, throwaway fixtures). No lane file outside my seat directory was written.
