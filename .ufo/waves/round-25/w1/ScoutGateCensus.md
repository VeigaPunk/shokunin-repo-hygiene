# ScoutGateCensus — round 25 w1, SOURCES census before (seat L1Souji25.ScoutGateCensus-2)

## Status
STATUS: PASS — at base a6d2d15 the validator exits 0, the registry has 123 well-formed rows S001–S123 (contiguous, no duplicate ids, no violations), and the next free id is S124.

## Evidence
Revisions: lane HEAD 6e4737eab43d8fde1b85eb9f57023d29046705b4. Base a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe. `git diff --stat a6d2d15 HEAD -- corpus/` is empty. `git status --porcelain -- corpus/` is empty.
`corpus/SOURCES.md` has the same blob at base, at HEAD and in the worktree: `dd413ff2ce136fdf18d2bbc2a1d5b6f8c531e24f` (sha256 `59befea66c744b72fe72b94c076062225aeaba52cd43b36b30dfe29361bfe7de`). The last commit touching the file is 315422ba (round-24 final).
Validator: `scripts/sources-census.sh` sha256 `3fb72615…4e30`, last fleet commit f47ad6ba, clean in the fleet worktree. Tooling: git 2.56.0 (per prereg), gawk, coreutils. No installs.

### 1. Validate (live lane)
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → **EXIT=0**. Full output (32 lines):
```
souji	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
souji	W04	S036 duplicate url git-scm.com/docs/git across scopes
souji	W04	S038 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
souji	W04	S049 duplicate url git-scm.com/docs/git across scopes
souji	W04	S057 duplicate url git-scm.com/docs/git-config across scopes
souji	W04	S058 duplicate url git-scm.com/docs/git-worktree across scopes
souji	W04	S059 duplicate url git-scm.com/docs/gitattributes across scopes
souji	W04	S063 duplicate url git-scm.com/docs/git-gc across scopes
souji	W04	S065 duplicate url www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html across scopes
souji	W04	S072 duplicate url www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html across scopes
souji	W04	S073 duplicate url man7.org/linux/man-pages/man2/kill.2.html across scopes
souji	W04	S075 duplicate url man7.org/linux/man-pages/man5/proc_pid_stat.5.html across scopes
souji	W04	S076 duplicate url man7.org/linux/man-pages/man5/proc_pid_exe.5.html across scopes
souji	W04	S077 duplicate url man7.org/linux/man-pages/man2/open.2.html across scopes
souji	W04	S086 duplicate url man7.org/linux/man-pages/man5/proc_pid_fd.5.html across scopes
souji	W04	S087 duplicate url man7.org/linux/man-pages/man5/proc_pid_wchan.5.html across scopes
souji	W04	S088 duplicate url man7.org/linux/man-pages/man5/proc_pid_status.5.html across scopes
souji	W04	S089 duplicate url git-scm.com/docs/git across scopes
souji	W04	S090 duplicate url git-scm.com/docs/git-filter-branch across scopes
souji	W04	S091 duplicate url git-scm.com/docs/git-rev-parse across scopes
souji	W04	S092 duplicate url git-scm.com/docs/git-for-each-ref across scopes
souji	W04	S093 duplicate url git-scm.com/docs/git-diff across scopes
souji	W04	S094 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
souji	W04	S095 duplicate url man7.org/linux/man-pages/man5/proc_pid_fd.5.html across scopes
souji	W04	S096 duplicate url man7.org/linux/man-pages/man5/proc_pid_fd.5.html across scopes
souji	W04	S097 duplicate url git-scm.com/docs/git-filter-branch across scopes
souji	W04	S098 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
souji	W04	S099 duplicate url git-scm.com/docs/git-rev-parse across scopes
souji	W04	S106 duplicate url docs.python.org/3/library/json.html across scopes
souji	W04	S108 duplicate url docs.python.org/3/builtins/exceptions.html across scopes
souji	W04	S123 duplicate url git-scm.com/docs/git-worktree across scopes
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
```
There are 31 W04 lines and 0 E-codes. W04 does not count as a failure. Script header (`scripts/sources-census.sh:33`): "W04 same URL across scopes (warnings do not affect clean lanes)". Exit semantics (`:16`): "exit:   0 clean or warnings · 1 E/overdue findings (or census missing)".

### 2. Validate pinned to the base tree
Steps: `git archive a6d2d15 | tar -x -C /var/tmp/souji-r25-ScoutGateCensus/root/souji-shokunin`, copy the fleet `shokunin.conf` into the scratch root, then run `validate --root <scratch root> souji`.
Result: **BASE_EXIT=0**, 31 W04 lines, last line `souji	ok	…/corpus/SOURCES.md`. After normalizing the root path, the output is byte-identical to the live run (`diff` empty).
Two failed attempts happened first, and both were scratch setup errors, not registry findings:
- No conf in the scratch root gave rc 2 (`ERROR: config not found`).
- A `corpus/`-only export gave rc 1 with `E11 S120/S122 missing used-by tools/souji-size-census.py`, because `tools/` was absent from the export.

### 3. Frozen manual census (CORPUS.md:131–147, run from the lane root)
| check | command | output |
|---|---|---|
| row count (task regex) | `grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` | `123` |
| row count (frozen CORPUS.md:135, column-zero) | `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` | `123` |
| indented rows (1–3 spaces) | `grep -cE '^ {1,3}\|…'` | `0` |
| malformed NF!=13 (:137) | awk `NF!=13` | `0` |
| tier histogram (:139) | awk `$5` | `A=117 B=5 C=1` |
| status histogram (:141) | awk `$9` | `mined=100 queued=15 rejected=8` |
| duplicate ids (:143) | awk `$2` \| sort \| uniq -d | (empty) |
| enum / tier-inflation (:145) | awk tier/status/kind/A+community | (empty) |
| mined used-by missing (:147) | awk `$12` split on `[,;]` + `[ -e ]` | (empty); 109 paths checked |
| same, on the base export | same | (empty) |

The tier and status sums are 117+5+1 = 123 and 100+15+8 = 123. Census mode (`sources-census.sh census --root … souji`, rc 0) reports the same numbers: `rows 123`, `tier.A 117`, `tier.B 5`, `tier.C 1`, `status.mined 100`, `status.queued 15`, `status.rejected 8`, `tier.invalid 0`, `status.invalid 0`, `missing 0`.

### 4. Registry tail and next id
`sort -V` of the row ids gives `S119 S120 S121 S122 S123`, and the maximum numeric id is 123. A contiguity check prints `rows=123 S001..S123 contiguous in order`. `grep -nE 'S12[4-9]' corpus/SOURCES.md` finds nothing. Line 143 is `| S123 | git-worktree(1) § REFS and § DETAILS — https://git-scm.com/docs/git-worktree | docs | A |`. **The next unused lane id is S124**, which matches the prereg C3 plan (S124/S125 opened this round).

## Findings
1. Gate baseline: validate rc 0 at base and at HEAD (both have the same SOURCES blob `dd413ff2`). There are 31 W04 warnings and 0 errors (`scripts/sources-census.sh`, run above). For a round-end comparison, the W04 count of 31 is the before figure.
2. The registry is well formed: 123 rows, NF=13 throughout, no duplicate ids, no enum or tier-inflation violations, and every mined used-by path exists (`corpus/SOURCES.md`; frozen commands at `/home/vgpnk/Projects/shokunin/CORPUS.md:131-147`).
3. Next free id: S124 (tail S123 at `corpus/SOURCES.md:143`).
4. Before-figure for C3 landing: the row count goes 123 → 125 if S124 and S125 are appended. If the S124 git-worktree or git-repo-structure family reuses a URL already in the registry (S058/S123 git-worktree; S035 git-repo), each reused URL will add W04 lines. That does not affect rc, but the count will move [INFERENCE].
5. Id-namespace collision risk: base-tracked `.ufo/waves/round-22/attempt2/assimilation/staged-ids` (134 lines, starting `S109`) lists `S124`…`S133`, and `ResSliceVerdicts.md:50` reads "S124   `payload-absent`". These are campaign staged-register ids, not lane SOURCES rows. `corpus/lessons/round-22.md:363` also names "(S123, S124, S131, S133)" in that other namespace. A bare "S124" written this round has the same ambiguity D5 is fixing for bare "S123". Recommendation: write "SOURCES S124" or the row anchor in the C3 knowledge entry and the SCORECARD.

## Attack log
- ATTACK (minor, completeness of the C3 sourced claim): see Finding 5. The prereg says "source cites SOURCES rows S124/S125". If the knowledge entry writes bare `S124`, a reader resolving through the round-22 staged-ids or slice-verdicts gets a different object. This is a disambiguation duty, not a predicate change.
- No attack on the census predicates: the task's ` {0,3}` regex and the frozen column-zero regex agree (123/123, 0 indented rows).

Scratch `/var/tmp/souji-r25-ScoutGateCensus/` was created for the base export and has been removed.
