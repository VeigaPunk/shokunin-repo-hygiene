# SonicReadmeRows — r26 raw byte extraction (README coverage map + staged rows)

## Status

STATUS: PASS — all requested bytes are pasted verbatim below, read this run from the lane tip `ba8b54b85814dd980aa96050fe111c7cbfd4956a` and from the read-only staged package; the only correction is that the coverage-map header row sits at line 36, not 37 (slice given as requested *and* with the header included).

## Evidence

Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`, tip `ba8b54b85814dd980aa96050fe111c7cbfd4956a` (`round-26 C1: c1-after regenerated at fix tip 07f83e6 (markers=0, headings=17 44 78)`).

```
$ sha256sum corpus/README.md
b9f5283865e00f0f7d2c4a185be12797b8571402ac209520d59bbab8df967195  corpus/README.md
$ wc -l corpus/README.md
558 corpus/README.md
$ git diff --stat -- corpus/README.md          # empty (rc=0)
$ git cat-file -p HEAD:corpus/README.md | sha256sum
b9f5283865e00f0f7d2c4a185be12797b8571402ac209520d59bbab8df967195  -
$ grep -n '^| ground ' corpus/README.md
36:| ground | status | entries |
66:| ground | status | entries / runnable evidence |
...
$ sha256sum /home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md
1510052ee7ca2b6fa3d6e2b89c397011865b07dec0fa1c8e097945cfa6b9f7d6  /home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md
$ wc -l /home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md
140 /home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md
```

### corpus/README.md lines 36-41 (line 36 = header; 37-41 = the requested slice)

```text
| ground | status | entries |
|---|---|---|
| receipts: pushed / moved-to-obsidian / stale | core (SKILL.md, tools/) | `knowledge/obsidian-ledger.tsv` (operator-fed, header-only) |
| F1 git-native housekeeping vs receipts | frontier, entries held | `knowledge/git-auto-maintenance-prunes-worktrees.md`, `knowledge/git-grace-periods-and-expire-to.md`, `knowledge/git-auto-maintenance-trigger-set.md`, `knowledge/git-auto-maintenance-trigger-set-r23.md` |
| F2 repository size census | frontier, no entry (r12 candidate deferred, `lessons/round-12.md` `## Gate`; sweep: `ls corpus/knowledge \| grep -ciE 'size\|structure\|sizer'` → 0, 2026-10-19); superseded by Round 24 F2 row (:517) | — |
| F3 duplicate verdicts | frontier, entry held | `knowledge/dupe-finders-detect-then-act.md` |
```

### corpus/README.md lines 37-41 exactly as requested (no header row inside the slice)

```text
|---|---|---|
| receipts: pushed / moved-to-obsidian / stale | core (SKILL.md, tools/) | `knowledge/obsidian-ledger.tsv` (operator-fed, header-only) |
| F1 git-native housekeeping vs receipts | frontier, entries held | `knowledge/git-auto-maintenance-prunes-worktrees.md`, `knowledge/git-grace-periods-and-expire-to.md`, `knowledge/git-auto-maintenance-trigger-set.md`, `knowledge/git-auto-maintenance-trigger-set-r23.md` |
| F2 repository size census | frontier, no entry (r12 candidate deferred, `lessons/round-12.md` `## Gate`; sweep: `ls corpus/knowledge \| grep -ciE 'size\|structure\|sizer'` → 0, 2026-10-19); superseded by Round 24 F2 row (:517) | — |
| F3 duplicate verdicts | frontier, entry held | `knowledge/dupe-finders-detect-then-act.md` |
```

### /home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md — staged rows, full lines

Line numbers are the file's own (`grep -n '^\| S(109|110|111|123|131) \|'` → 7, 8, 9, 21, 29).

S109 (line 7):

```text
| S109 | git-fetch(1) — https://git-scm.com/docs/git-fetch | docs | A | git 2.56.0 fetch's own auto-maintenance switch, not whether it prunes worktree registrations | § OPTIONS "--auto-maintenance, --no-auto-maintenance, --auto-gc, --no-auto-gc"; installed man page git 2.56.0 (2026-09-27) | fetch ends by running `git maintenance run --auto`; the operator can disable that run per invocation with `--no-auto-maintenance` / `--no-auto-gc` | mined | 2026-10-23 | on-release — host `git --version` is 2.56.0 | corpus/knowledge/git-auto-maintenance-trigger-set.md, corpus/knowledge/git-auto-maintenance-trigger-set-r23.md |
```

S110 (line 8):

```text
| S110 | git/git v2.56.0 builtin/fetch.c, builtin/merge.c, builtin/rebase.c, builtin/am.c, builtin/commit.c — https://github.com/git/git/blob/v2.56.0/builtin/fetch.c | code | A | the set of porcelain commands that call `run_auto_maintenance` at tag v2.56.0; call sites only, not a behavioural proof that any of them prunes | tag v2.56.0: builtin/fetch.c:2926, builtin/merge.c:509, builtin/rebase.c:572, builtin/am.c:1942, builtin/commit.c:1965 | fetch, merge, rebase, am and commit each call `run_auto_maintenance`; the calls sit after the work completes and ignore errors from `git maintenance run --auto` | mined | 2026-10-23 | on-release — re-grep call sites at the next host git tag | corpus/knowledge/git-auto-maintenance-trigger-set.md, corpus/knowledge/git-auto-maintenance-trigger-set-r23.md |
```

S111 (line 9):

```text
| S111 | git/git v2.56.0 builtin/pull.c — https://github.com/git/git/blob/v2.56.0/builtin/pull.c | code | A | how `git pull` reaches fetch's auto-maintenance: it spawns `git fetch` as a child process, so the trigger is inherited rather than duplicated | tag v2.56.0: builtin/pull.c:392 `strvec_pushl(&cmd.args, "fetch", "--update-head-ok", NULL);` | `git pull` runs `git fetch` as a child, so pull's auto-maintenance exposure is fetch's, reached by process spawn rather than a second `run_auto_maintenance` call | mined | 2026-10-23 | on-release — re-read builtin/pull.c at the next host git tag | corpus/knowledge/git-auto-maintenance-trigger-set.md, corpus/knowledge/git-auto-maintenance-trigger-set-r23.md |
```

S123 (line 21):

```text
| S123 | souji round-2 fixture r23-trigger-prune.sh — lanes/souji/round2/fixtures/r23-trigger-prune.sh | own-work | A | whether `git fetch`/`merge`/`rebase`/`pull` auto-maintenance actually prunes a worktree registration on git 2.56.0; measured on this host, not inferred from call sites | fixture r23-trigger-prune.sh, cases SOUJI-R23-TRIGGER-{fetch,fetch-auto-off,pull,merge,rebase,locked,fresh}; git 2.56.0 (2026-10-23), kernel 7.2.11-arch1-1; evidence lanes/souji/round2/evidence/r23-trigger-prune.out (sha256 510722c1…); scratch /var/tmp/souji-r23-trigger.XXXXXX, no residue | fetch, pull, merge and rebase each take a stale worktree registration 2 -> 1 with no souji receipt; `maintenance.auto=false` and `git worktree lock` each hold it at 2; a fresh (un-aged) registration is spared at 2, so the task ran and the expiry protected it | mined | 2026-10-23 | 90d — re-run `bash fixtures/r23-trigger-prune.sh` (expect 7 PASS and exit 0) | corpus/knowledge/git-auto-maintenance-trigger-set-r23.md |
```

S131 (line 29):

```text
| S131 | souji round-2 census r23-worktree-census — lanes/souji/round2/evidence/r23-worktree-census.out | own-work | A | whether the fleet's own `git worktree` set holds registrations today's git would prune; a read-only census of the live fleet, not the round-12 point-in-time figure | evidence/r23-worktree-census.out (sha256 1ac71c4f…), 2026-10-23, git 2.56.0; `worktree list` and `worktree prune --dry-run` only, never `worktree prune` | the fleet repo has **5 registrations, 0 prunable and 0 locked** — `prune --dry-run` reports nothing even at `--expire=now` — so the round-12 "0 prunable, 3 locked" figure is stale: the count grew to 5 while the locked count fell to 0 | mined | 2026-10-23 | 90d — re-run the read-only census (expect 5 registrations, 0 prunable) | corpus/knowledge/count-objects-garbage-semantics-r23.md |
```

### corpus/knowledge/ filenames matching `*maintenance*` or `*trigger*`

```
$ find corpus/knowledge -maxdepth 1 \( -name '*maintenance*' -o -name '*trigger*' \) -type f -printf '%f\n' | sort
git-auto-maintenance-prunes-worktrees.md
git-auto-maintenance-trigger-set.md
git-auto-maintenance-trigger-set-r23.md
```

## Findings

1. **Line drift in the requested slice.** The coverage-map header `| ground | status | entries |` is line 36 of `corpus/README.md`, not inside the requested 37-41 range; 37 is the `|---|---|---|` separator, 38 the receipts row, 39 F1, 40 F2, 41 F3. Both the requested slice and the header-inclusive 36-41 slice are pasted above so no byte is lost. Location: `corpus/README.md:36-41` (sha256 `b9f52838…`).
2. **F1 row already maps both r26 admitted entries.** The F1 `entries` cell names `knowledge/git-auto-maintenance-trigger-set.md` and `knowledge/git-auto-maintenance-trigger-set-r23.md` at the tip, i.e. the map side of C2 K4 (`grounded=9 mapped=9`) is already satisfied in the working tree; the counter side (K1 `ground: F1` = 2) is what the entries' front matter must add. Location: `corpus/README.md:39`.
3. **F2 row carries two escaped pipes (`\|`) plus a colon-prefixed in-document ref `(:517)`.** Not a defect for the K4 instrument: `tools/souji-coverage-agreement.py:35` splits cells with `re.compile(r"(?<!\\)\|")`, so escaped pipes stay inside the cell; the row parses as 3 cells. Note only — the `:517` reference is a bare line pointer that will drift if the file is edited above it. Location: `corpus/README.md:40`, `tools/souji-coverage-agreement.py:35,70-71`.
4. **Staged rows are pre-renumber and carry the collision the prereg predicts.** Staged ids present are S109/S110/S111/S123/S131, all below the lane registry's existing S109-S127 range; the prereg maps S109→S128, S110→S129, S111→S130, S123→S131, S131→S132. S131's staged `used-by` names `corpus/knowledge/count-objects-garbage-semantics-r23.md`, which is the "unadmitted staged knowledge file" sentence the prereg says must be reworded to cite the row only. Locations: `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md:7,8,9,21,29`.
5. **Staged rows use `…`-elided hashes** (`sha256 510722c1…`, `1ac71c4f…`), so a normalized append cannot verify the digest from the row itself; it must come from the campaign evidence files. Location: `SOURCES.append.md:21,29`.
6. **Odd substring in S131's expected recheck**: "expect 5 registrations, 0 prunable" — while the prereg's C2 text describes the same census as "0 prunable", the fleet-wide S155 row later reports 16 prunable across 6 repos, so "the fleet repo" here means the single fleet repo, not all lane repos. Location: `SOURCES.append.md:29` vs prereg C2 / stamped row S155.
7. **Read-only discipline held.** `git diff --stat -- corpus/README.md` empty and the working-tree hash equals `HEAD:corpus/README.md` (`b9f52838…`); the only lane modification at read time is `M tools/souji-axis-check.py`, not mine. No write, fetch, push or campaign tool ran against `/home/vgpnk/Projects/shokuknow`; no scratch directory was needed and none was created.

## Attack log

Not an attack item — the assignment is byte extraction; findings 3-6 are observations handed to the integrator, not scored attacks.
