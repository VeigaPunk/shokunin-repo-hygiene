# W2C2Rerun — attack on C2 after-state (souji round 24, wave 2)

## Status
STATUS: PASS — C2 survives every check: tool reruns, three receipts verify, amended fixture 9/9, and the per-entry kill rule holds (4/4 base-grounded entries present at tip with the same F<k>). One attack finding (F3) is about how the rule is enforced, not a falsification.

## Evidence
Host: git 2.56.0, Python 3.14.8. Lane `master` = `c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface`, which is NOT `ca7fc1cb` (see F1). Tool/fixture sha256 `71b89eb3…`/`42259756…` are identical in the working tree and at 1efe406, 778747e, ca7fc1cb and c3ca7ad. `tools/` is clean in `git status`.

| # | Check | Command (cwd = lane) | Output excerpt | Verdict |
|---|---|---|---|---|
| 1 | Tool at tip | `python3 -B tools/souji-coverage-agreement.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev ca7fc1cb6dd1333096c6f3bdbad304686691d126` | `grounded=6 mapped=6 dangling=0 mismatches=0`, exit 0 | survives |
| 2 | Tool at base | same, `--rev a65fac98964b445758e94c805728c9a19d302ff8` | 2× `MISMATCH MISSING-FROM-MAP` (count-objects-garbage-readings-r25.md, repo-size-census-readonly.md, `ground=F2 map_rows_F2=3`); `grounded=4 mapped=2 dangling=0 mismatches=2`, exit 1 | survives (matches control receipt) |
| 2b | Tool at 778747e and master | same, both revs | `grounded=6 mapped=6 dangling=0 mismatches=0`, exit 0 at both | survives |
| 3 | Verify `c2-after.tsv` | `python3 -B tools/souji-receipt-run.py verify --root /home/vgpnk/Projects/shokunin/souji-shokunin census/round-24/records/c2-after.tsv` | `verify=ok rev=778747eb… tool=tools/souji-coverage-agreement.py tool_sha256=71b89eb3…`, exit 0; recorded stdout = check 1 bytes | survives |
| 4 | Verify `c2-control-base.tsv` | same | `verify=ok rev=1efe406e…`, exit 0; cmd `--rev a65fac98…`, rc=1, stdout = check 2 bytes | survives |
| 5 | Verify `c2-fixture-after.tsv` | same | `verify=ok rev=778747eb… tool=tests/fixtures/r24-coverage-agreement.py`, exit 0 | survives |
| 6 | Amended fixture at tip | `python3 -B tests/fixtures/r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py` | `cases=9 pass=9 control=FALSE-GREEN-REJECTED`, exit 0; all 9 control cases FAIL | survives (meets the amendment's verdict requirement) |
| 7 | Control-before-after order | `git log --diff-filter=A` per receipt | c2-control-base added in ce5971c (06:29:45 -0300); c2-after and c2-fixture-after added in ca7fc1c (06:34:57 -0300) | survives |
| 8 | Per-entry kill rule (amendment 1) | for each path from `git ls-tree -r --name-only <rev> corpus/knowledge/`, `git show <rev>:<path>` piped to `grep -nE '^[[:space:]]*ground[[:space:]]*:'`, at both revs | table below | survives |
| 9 | Deleted or renamed entries | `git diff --name-status -M a65fac98 ca7fc1cb -- corpus/` | `M corpus/README.md`, `M corpus/SOURCES.md`, `A …/count-objects-linked-worktree-garbage.md`, `M …/git-repo-structure-readonly.md`; no D/R | survives |
| 10 | Independent map parser | inline `python3 -B -c` over `git show <rev>:corpus/README.md` (own regexes for table headers, ground token, backticked `knowledge/<name>` spans in entries cells) | base: grounded 4, missing = the same 2, dangling []; tip: grounded 6, missing [], dangling []. Tip has 6 map tables (header lines 36, 66, 214, 238, 272, 514) | survives (agrees with the tool at both revs) |

Per-entry `ground: F<k>` table (header lines at column 0):

| entry | base a65fac98 | tip ca7fc1cb | status |
|---|---|---|---|
| count-objects-garbage-readings-r25.md | F2 (line 5) | F2 (line 5) | kept, same F<k> |
| quarantine-origin-record-fields-r24.md | F4 (line 7) | F4 (line 7) | kept, same F<k> |
| quarantine-staging-no-copy-r23.md | F4 (line 6) | F4 (line 6) | kept, same F<k> |
| repo-size-census-readonly.md | F2 (line 6) | F2 (line 6) | kept, same F<k> |
| count-objects-linked-worktree-garbage.md | absent (file added by C1) | F2 (line 8) | new |
| git-repo-structure-readonly.md | no header line (only body line 7, `Coverage-map ground: F2 repository size census.`) | F2 (line 4); body line now line 8 | newly grounded |

A case-insensitive search for `ground…F<digit>` across `corpus/knowledge/` at both revs found no other ground-like lines. `obsidian-ledger.tsv` is the only non-`.md` file and has no ground line. Even under the loosest reading, where base counts the body line in git-repo-structure-readonly.md, that entry is still F2 at tip. No reading produces a kill.

## Findings
1. **Tip identity drift (info).** Lane `master` = `c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface`, not the stated after-receipt tip `ca7fc1cb`. `git merge-base --is-ancestor ca7fc1cb master` succeeds. `git diff --stat 778747e master -- corpus/ tools/souji-coverage-agreement.py tests/fixtures/r24-coverage-agreement.py` is empty, so C2's measured state is identical at 778747e, ca7fc1cb and c3ca7ad (check 2b). Location: lane HEAD, commit c3ca7ad ("wave-1 seat reports, drafts and registry").
2. **Base grounding changed by format, not by the corpus (info, not a deviation).** git-repo-structure-readonly.md went from body-only text at base (line 7, after the `#` title) to a header `ground: F2` line at tip. This adds to the grounded count and removes no base entry. The frozen text defines MISSING-FROM-MAP over a "front-matter line `ground: F<k>`" (preregistration.txt:82-83), so excluding the body line at base is consistent. Location: `git show a65fac98:corpus/knowledge/git-repo-structure-readonly.md` line 7; `git show ca7fc1cb:…` line 4.
3. **ATTACK: the per-entry kill rule is enforced only by hand (medium; does not falsify this tip).** Mutations M3 and M4 below show that the tool, the fixture and the frozen count rule all stay green when a base-grounded entry is deleted. M3 deletes one base entry and its map mentions: the tip goes to `grounded=5 … mismatches=0`. Because the after-state added 2 grounded entries, grounded(tip)=5 ≥ grounded(base)=4, so the frozen rule (preregistration.txt:91 "grounded(tip) < grounded(base) -> C2 fails") passes. Up to 2 base entries could be deleted unseen. Only amendment-1:28-29 ("C2 fails if ANY entry grounded at base is absent at tip or carries a different F<k>") catches this, and no committed tool or fixture implements it: a grep in tools/ and tests/ for any of the three strings `per-entry`, `different F<k>` or `grounded at base` hits only unrelated tools/impl-06.sh:724 and tools/souji-gate-check.py:4. The verdict therefore depends on a seat running this comparison, as this report does. The fix that preserves the frozen predicates is a seat-run receipt of the per-entry diff. Changing the counter would be a deviation.
4. **The tool reads committed bytes only (confirmed).** M1 (uncommitted README edit) leaves the output unchanged; the same edit committed gives MISSING-FROM-MAP. This matches fixture case 7.

## Attack log
Scratch: `/var/tmp/souji-r24-W2C2Rerun/lane` (`git clone --no-hardlinks` of the lane, detached at ca7fc1cb, local commits only; removed afterwards, and `ls` confirms it is gone). The tool used is the lane's committed `tools/souji-coverage-agreement.py` with `--root <scratch> --rev $(git rev-parse HEAD)`.

| id | mutation (committed in scratch unless noted) | tool output | caught by |
|---|---|---|---|
| M0 | none | `grounded=6 mapped=6 dangling=0 mismatches=0` exit 0 | — |
| M1 | drop linked-worktree entry from r24 F2 map row, worktree only | unchanged, exit 0 | correct (rev-bound) |
| M1c | same, committed | `MISSING-FROM-MAP …count-objects-linked-worktree-garbage.md ground=F2 map_rows_F2=4`, `mismatches=1` exit 1 | tool |
| M2 | repo-size-census-readonly `ground: F2`→`F3` | `MISSING-FROM-MAP … ground=F3 map_rows_F3=1`, exit 1 | tool + per-entry rule |
| M3 | delete count-objects-garbage-readings-r25.md + its map span | `grounded=5 mapped=5 dangling=0 mismatches=0` exit 0 | per-entry rule only (5 ≥ 4 passes the count rule) |
| M4 | delete the same entry, add a grounded and mapped `zz-new.md` | `grounded=6 mapped=6 dangling=0 mismatches=0` exit 0 | per-entry rule only |
| M5 | indent `ground: F4` in quarantine-staging-no-copy-r23.md (un-ground) | `grounded=5 … mismatches=0` exit 0 | per-entry rule only |
| M6 | add `` `knowledge/ghost.md` `` to F3 row | `DANGLING-MAP-PATH corpus/knowledge/ghost.md corpus/README.md:41`, exit 1 | tool |

Residual risk: the per-entry rule (F3) is not mechanized. The tool counts only column-0 header `ground:` lines, so an entry un-grounded by formatting (M5) disappears from every count. That is consistent with the frozen definition, but only a per-entry diff catches it.
Tooling installs: none.
