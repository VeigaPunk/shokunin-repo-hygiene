# SonicSourcesGrep — round 26 w1, mechanical ground/registry greps

## Status

STATUS: PASS — all four assigned commands ran at rev `89e0fceeefcf28db313c94120be6d25e03c60094` (or, for the two file-path commands (c)/(d), against the worktree) and their raw outputs are below. One scope caveat (F4): (c) and (d) are worktree reads and their values belong to HEAD, not to `89e0fce`; the rev-exact values are given beside them.

## Evidence

Lane repo: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Assigned rev resolves:

```
$ git log -1 --format='%H %s' 89e0fceeefcf28db313c94120be6d25e03c60094
89e0fceeefcf28db313c94120be6d25e03c60094 round-26: prereg amendment 1 (C2 K4 literal corrected to base-derived grounded=7/kill_tested=7) + red-before receipts
```

Read first: `.ufo/waves/round-26/preregistration.txt` (full), `.ufo/waves/round-26/preregistration-amendment-1.txt`, `.ufo/waves/round-26/preregistration-amendment-2.txt`.

### (a) per-ground histogram at 89e0fce

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -c '^ground: F' 89e0fceeefcf28db313c94120be6d25e03c60094 -- corpus/knowledge/
89e0fceeefcf28db313c94120be6d25e03c60094:corpus/knowledge/count-objects-garbage-readings-r25.md:1
89e0fceeefcf28db313c94120be6d25e03c60094:corpus/knowledge/count-objects-linked-worktree-garbage.md:1
89e0fceeefcf28db313c94120be6d25e03c60094:corpus/knowledge/git-repo-structure-common-dir.md:1
89e0fceeefcf28db313c94120be6d25e03c60094:corpus/knowledge/git-repo-structure-readonly.md:1
89e0fceeefcf28db313c94120be6d25e03c60094:corpus/knowledge/quarantine-origin-record-fields-r24.md:1
89e0fceeefcf28db313c94120be6d25e03c60094:corpus/knowledge/quarantine-staging-no-copy-r23.md:1
89e0fceeefcf28db313c94120be6d25e03c60094:corpus/knowledge/repo-size-census-readonly.md:1
```

Per-value split (same rev, `grep -h` then `grep -oE '^ground: F[0-9]' | sort | uniq -c`):

```
      5 ground: F2
      2 ground: F4
```

Explicit F1..F5 loop, counting matching files per value:

```
F1=0
F2=5
F3=0
F4=2
F5=0
```

### (b) F1 absence at 89e0fce

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -l 'ground: F1' 89e0fceeefcf28db313c94120be6d25e03c60094 -- corpus/knowledge/
exit=1
```

(no stdout, no stderr; `git grep` exit 1 = no match)

### (c) highest S-id — worktree file

```
$ grep -oE 'S[0-9]+' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md | sort -V | tail -3
S130
S131
S132
```

### (d) knowledge file count — worktree

```
$ ls /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/knowledge/ | wc -l
17
```

### Rev-exact counterparts for (c)/(d)

```
$ git show 89e0fce:corpus/SOURCES.md | grep -oE 'S[0-9]+' | sort -V | uniq | tail -3
S125
S126
S127

$ git ls-tree --name-only 89e0fce -- corpus/knowledge/ | wc -l
15
```

Registry row count (counter's own schema regex `^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|`), per rev, from committed bytes:

```
0eca7c8 127
89e0fce 127
HEAD (d6fe8a1) 132
```

### Receipt cross-check (read-only)

```
census/round-26/records/c2-before.tsv:  rev=89e0fce...  rc=0  grounded_f1=0  registry_rows=127
census/round-26/records/c2-after.tsv:   rev=e0f8dcd...  rc=0  grounded_f1=2  registry_rows=132
census/round-26/records/c2-k4-base.tsv: rev=0eca7c8...  rc=0  grounded=7 mapped=7 dangling=0 mismatches=0 kill_tested=7 kill_violations=0
```

## Findings

1. **(b) empty confirms the C2 K1 red arm.** At `89e0fce`, zero knowledge files carry `ground: F1`; `git grep -l` exits 1 with no output. Location: `corpus/knowledge/` tree at `89e0fceeefcf28db313c94120be6d25e03c60094`. This equals the frozen K1 base literal 0 and matches the committed `c2-before.tsv` at the same rev (`grounded_f1=0`).

2. **Histogram total = 7, which is the K4 base-grounded count.** F2 contributes 5 files and F4 contributes 2, sum 7 — identical to `grounded=7` in `c2-k4-base.tsv` (rev `0eca7c8`) and to amendment 1's corrected literal. Location: same 7 files' front matter, e.g. `corpus/knowledge/repo-size-census-readonly.md:6` and `corpus/knowledge/quarantine-staging-no-copy-r23.md:6`.

3. **F3 and F5 are empty at this rev.** No knowledge entry is grounded on F3 or F5; the lane's grounded population at `89e0fce` is F2-only and F4-only. Location: `corpus/knowledge/` at `89e0fce`. No kill rule in the frozen prereg references F3/F5 counts, so this is context, not a counter result.

4. **`ground` is single-valued per entry at this rev.** `-c` reports exactly 1 for every matching file (7 files, 7 hits); no file carries two `ground:` lines. Location: front matter of the 7 files above.

5. **(c) and (d) are worktree reads, not rev reads — the values are HEAD's.** As assigned, both commands address absolute worktree paths under `corpus/`. At run time HEAD was `d6fe8a1` (it advanced from `ea0bbe66` during this seat's run), so `S132`/`17` describe HEAD. At the assigned rev the same derivations give `S127` as highest id and 15 knowledge files. Location: `corpus/SOURCES.md` and `corpus/knowledge/` — worktree vs `89e0fce` tree. Quoting (c)/(d) as values "at `89e0fce`" would overstate the frozen base by one append (row 127→132) and two entries (15→17).

6. **The 17-vs-15 delta is exactly the two C2 admitted entries**, added after `89e0fce`: `git diff --name-status 89e0fce..HEAD -- corpus/knowledge/` prints `A corpus/knowledge/git-auto-maintenance-trigger-set-r23.md` and `A corpus/knowledge/git-auto-maintenance-trigger-set.md`. The SOURCES.md append (127→132) landed in `0833de9`. Location: commits `0833de9`, `ea0bbe6` on branch master.

7. **At HEAD the K1/K3 values are the prereg's after-literals.** `git grep -l '^ground: F1' HEAD -- corpus/knowledge/` lists exactly the two admitted entries (F1=2; F2=5, F4=2 unchanged), and `bash census/round-26/c2-counter.sh` (read-only) prints `grounded_f1=2` / `registry_rows=132`. Location: repo HEAD `d6fe8a1`; `corpus/SOURCES.md`.

8. **Missing after-receipt: `census/round-26/records/c2-k4-after.tsv` does not exist** at HEAD `d6fe8a1` (`find . -name 'c2-k4-after*'` empty), although the C2 KILL RULE and RECEIPTS text require it and `c2-gate.tsv`. Location: `census/round-26/records/` (only `c1-before`, `c1-after`, `c2-before`, `c2-after`, `c2-k4-base`, `c3-before`, `c3-after`, `c3-control` present). Recording only — receipt authorship is the integrator's, not this seat's item.

9. **Tree is not clean at HEAD for `census/round-26/records/c1-after.tsv`.** `git status --porcelain` prints ` M census/round-26/records/c1-after.tsv` (not written by this seat — the seat made no writes inside `census/`). C1's K1 binding (`.ufo/waves/round-26/preregistration.txt`, CLAIM C1 K1 bullet: "run at the landing tip in a clean tree") means the modified receipt must be committed or reverted by its author before C1's green arm is scored. Also untracked and therefore outside any committed tree: `census/operator-sweep-20261019/`, `tests/fixtures/__pycache__/`, `tools/__pycache__/`. Location: lane worktree at HEAD `d6fe8a1`.

10. **No writes by this seat.** Every lane command was `git grep`/`git show`/`git ls-tree`/`git log`/`git diff`/`git status`/`git rev-parse`, `grep`, `ls`, `wc`, or reads. No scratch was created (nothing under `/var/tmp/souji-r26-SonicSourcesGrep/` was needed), so nothing to remove. `/home/vgpnk/Projects/shokuknow` and everything outside `souji-shokunin/` was untouched.

## Attack log

Item was mechanical; two observations offered for attack review, neither a kill.

- **A1 (inert divergence, verified).** The bound counter `census/round-26/c2-counter.sh` counts `corpus/knowledge/*.md` (a shell glob, `.md` only), while the frozen K1 command counts the whole `corpus/knowledge/` pathspec. Divergence would appear if a non-`.md` file ever carried a `ground:` line. Today it does not: the only non-`.md` member is `corpus/knowledge/obsidian-ledger.tsv`, which has no `ground` line, and glob=2 equals rev-pathspec=2 at HEAD. Inert; a future non-`.md` ground carrier would silently escape the counter. Location: `census/round-26/c2-counter.sh` (line with the `grep -l '^ground: F1' corpus/knowledge/*.md` pipeline).

- **A2 (checked, not a defect).** The counter `cd`s to the repo root and reads the worktree, so a `--rev`-bound receipt would mis-measure unless the runner materialises the rev. `tools/souji-receipt-run.py` does materialise it: it clones `--no-local --no-checkout` into a private tree and checks out detached at `<rev>` (docstring at `tools/souji-receipt-run.py:44`). The `c2-before.tsv` values (rev `89e0fce`, `grounded_f1=0`, `registry_rows=127`) agree with this seat's independent rev-byte derivations, so no rev/worktree contamination is visible in that receipt.
