# Round 26 — staged to lane renumber map (C2 data deliverable)

Source package: `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md` (read-only, 140 lines, 134 staged rows S109–S242).
Lane registry: `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md`.
Lane base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`: 127 rows, S001–S127, next free id S128.
Lane HEAD at read time `44531281914ddd200432cdc7dae8ad958c5447e3`: committed registry still 127 rows; working tree carries the 5 appended rows (lines 149–153) as an uncommitted modification.
Frozen contract: `.ufo/waves/round-26/preregistration.txt` — map order fixed at :94, no predicate or case set changed here.

## 1. The five staged rows, verbatim

Extracted with `awk 'NR==7||NR==8||NR==9||NR==21||NR==29' SOURCES.append.md`; reproduced byte-for-byte (verified by `cmp` against the source extract, sha256 `3a1002bbf7a21e0b3690…`).

```text
| S109 | git-fetch(1) — https://git-scm.com/docs/git-fetch | docs | A | git 2.56.0 fetch's own auto-maintenance switch, not whether it prunes worktree registrations | § OPTIONS "--auto-maintenance, --no-auto-maintenance, --auto-gc, --no-auto-gc"; installed man page git 2.56.0 (2026-09-27) | fetch ends by running `git maintenance run --auto`; the operator can disable that run per invocation with `--no-auto-maintenance` / `--no-auto-gc` | mined | 2026-10-23 | on-release — host `git --version` is 2.56.0 | corpus/knowledge/git-auto-maintenance-trigger-set.md, corpus/knowledge/git-auto-maintenance-trigger-set-r23.md |
| S110 | git/git v2.56.0 builtin/fetch.c, builtin/merge.c, builtin/rebase.c, builtin/am.c, builtin/commit.c — https://github.com/git/git/blob/v2.56.0/builtin/fetch.c | code | A | the set of porcelain commands that call `run_auto_maintenance` at tag v2.56.0; call sites only, not a behavioural proof that any of them prunes | tag v2.56.0: builtin/fetch.c:2926, builtin/merge.c:509, builtin/rebase.c:572, builtin/am.c:1942, builtin/commit.c:1965 | fetch, merge, rebase, am and commit each call `run_auto_maintenance`; the calls sit after the work completes and ignore errors from `git maintenance run --auto` | mined | 2026-10-23 | on-release — re-grep call sites at the next host git tag | corpus/knowledge/git-auto-maintenance-trigger-set.md, corpus/knowledge/git-auto-maintenance-trigger-set-r23.md |
| S111 | git/git v2.56.0 builtin/pull.c — https://github.com/git/git/blob/v2.56.0/builtin/pull.c | code | A | how `git pull` reaches fetch's auto-maintenance: it spawns `git fetch` as a child process, so the trigger is inherited rather than duplicated | tag v2.56.0: builtin/pull.c:392 `strvec_pushl(&cmd.args, "fetch", "--update-head-ok", NULL);` | `git pull` runs `git fetch` as a child, so pull's auto-maintenance exposure is fetch's, reached by process spawn rather than a second `run_auto_maintenance` call | mined | 2026-10-23 | on-release — re-read builtin/pull.c at the next host git tag | corpus/knowledge/git-auto-maintenance-trigger-set.md, corpus/knowledge/git-auto-maintenance-trigger-set-r23.md |
| S123 | souji round-2 fixture r23-trigger-prune.sh — lanes/souji/round2/fixtures/r23-trigger-prune.sh | own-work | A | whether `git fetch`/`merge`/`rebase`/`pull` auto-maintenance actually prunes a worktree registration on git 2.56.0; measured on this host, not inferred from call sites | fixture r23-trigger-prune.sh, cases SOUJI-R23-TRIGGER-{fetch,fetch-auto-off,pull,merge,rebase,locked,fresh}; git 2.56.0 (2026-10-23), kernel 7.2.11-arch1-1; evidence lanes/souji/round2/evidence/r23-trigger-prune.out (sha256 510722c1…); scratch /var/tmp/souji-r23-trigger.XXXXXX, no residue | fetch, pull, merge and rebase each take a stale worktree registration 2 -> 1 with no souji receipt; `maintenance.auto=false` and `git worktree lock` each hold it at 2; a fresh (un-aged) registration is spared at 2, so the task ran and the expiry protected it | mined | 2026-10-23 | 90d — re-run `bash fixtures/r23-trigger-prune.sh` (expect 7 PASS and exit 0) | corpus/knowledge/git-auto-maintenance-trigger-set-r23.md |
| S131 | souji round-2 census r23-worktree-census — lanes/souji/round2/evidence/r23-worktree-census.out | own-work | A | whether the fleet's own `git worktree` set holds registrations today's git would prune; a read-only census of the live fleet, not the round-12 point-in-time figure | evidence/r23-worktree-census.out (sha256 1ac71c4f…), 2026-10-23, git 2.56.0; `worktree list` and `worktree prune --dry-run` only, never `worktree prune` | the fleet repo has **5 registrations, 0 prunable and 0 locked** — `prune --dry-run` reports nothing even at `--expire=now` — so the round-12 "0 prunable, 3 locked" figure is stale: the count grew to 5 while the locked count fell to 0 | mined | 2026-10-23 | 90d — re-run the read-only census (expect 5 registrations, 0 prunable) | corpus/knowledge/count-objects-garbage-semantics-r23.md |
```

Row shape: 11 columns, `NF=13` (two boundary pipes), no literal or escaped pipe inside any cell.

## 2. Within-scope duplicate check (E04)

### 2a. Prereg collision extractor

```
$ grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' SOURCES.append.md | tr -d ' |' | sort > staged_ids
$ grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md | tr -d ' |' | sort > lane_ids
$ comm -12 staged_ids lane_ids
S109 S110 S111 S112 S113 S114 S115 S116 S117 S118 S119 S120 S121 S122 S123 S124 S125 S126 S127 S128 S129 S130 S131 S132
```

Against the committed HEAD registry (127 ids, S001–S127) the intersection is `S109 … S127` only. The `S128–S132` tail appears in the intersection only because the working tree already carries the appended rows 149–153; those five ids are the target of this map, not pre-existing collisions.

### 2b. URL / own-work-path grep against the lane registry

Each staged source, searched literally in `git show HEAD:corpus/SOURCES.md` and in the working-tree registry:

| staged id | document key | HEAD (127 rows) | worktree (132 rows) |
|---|---|---|---|
| S109 | `https://git-scm.com/docs/git-fetch` | no match | line 149 = S128 (this row) |
| S110 | `https://github.com/git/git/blob/v2.56.0/builtin/fetch.c` | no match | line 150 = S129 (this row) |
| S111 | `https://github.com/git/git/blob/v2.56.0/builtin/pull.c` | no match | line 151 = S130 (this row) |
| S123 | `lanes/souji/round2/fixtures/r23-trigger-prune.sh` | no match | line 152 = S131 (this row) |
| S131 | `lanes/souji/round2/evidence/r23-worktree-census.out` | no match | line 153 = S132 (this row) |

Result: **0 within-scope duplicates.** Every staged document is new to the lane registry at base and at HEAD.

### 2c. What E04 actually tests, and why the own-work rows need the manual check

`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:646-649` raises E04 on a same normalized URL plus same scope, non-rejected, without `supersedes S[0-9]{3}` in `teaches`; the emitted finding is `duplicate url … within scope`. The URL is derived from the source cell by a `https?://` regex (`:599-603`), with normalization `sub(/#[^ ]*$/,"",u); sub(/\/$/,"",u);` (`:602`). An own-work row whose source cell carries no `http` URL yields an empty key, so E04 and W04 are silent for it — the two own-work rows therefore rest on the path grep in 2b above, which is empty.

### 2d. ID collision is numeric only (documents differ)

| staged id | lane row with that number at HEAD | same document? |
|---|---|---|
| S109 | `souji round-2 RENAME_NOREPLACE probe, vendored — lanes/souji/round2/evidence/noreplace_probe.py …` | no (different file, same campaign round) |
| S110 | `rename(2), man-pages 6.19` | no |
| S111 | `mv(1), GNU coreutils` | no |
| S123 | `git-worktree(1) § REFS and § DETAILS` (https://git-scm.com/docs/git-worktree) | no |
| S131 | (does not exist at HEAD; max id S127) | — |

## 3. Renumber map (prereg order)

| staged | lane | document | kind | tier | status | used-by after normalization |
|---|---|---|---|---|---|---|
| S109 | **S128** | git-fetch(1) § OPTIONS switch | docs | A | mined | trigger-set.md, trigger-set-r23.md |
| S110 | **S129** | git/git v2.56.0 builtin call sites (fetch, merge, rebase, am, commit) | code | A | mined | trigger-set.md, trigger-set-r23.md |
| S111 | **S130** | git/git v2.56.0 builtin/pull.c child spawn | code | A | mined | trigger-set.md, trigger-set-r23.md |
| S123 | **S131** | own-work fixture `lanes/souji/round2/fixtures/r23-trigger-prune.sh` | own-work | A | mined | trigger-set-r23.md (see F6) |
| S131 | **S132** | own-work census `lanes/souji/round2/evidence/r23-worktree-census.out` | own-work | A | mined | trigger-set-r23.md |

Prereg literal (`.ufo/waves/round-26/preregistration.txt:94`): `staged S109->S128, S110->S129, S111->S130, S123->S131, S131->S132.`

Cells that must change when staging becomes a registry row (prereg C2 normalization rules, applied in the live append):

- `opened` 2026-10-23 -> 2026-10-25 (re-opened this round).
- `recheck`: cadence kept, trailing prose moved out of the cell (`on-release`; `90d`).
- `anchor`: snapshot references added for the three docs/code rows (`census/round-26/sources/…`); own-work rows keep campaign paths.
- `used-by`: staged S109/S110/S111 already name only admitted entries; staged S123 already names only trigger-set-r23.md; staged S131 must be rewritten — its cell names `corpus/knowledge/count-objects-garbage-semantics-r23.md`, which does not exist in this lane (see F4).

## 4. Own-work evidence paths exist

Paths in the rows are campaign-root-relative (`/home/vgpnk/Projects/shokuknow/…`), not relative to `merge/souji`; under `merge/souji` all three are MISSING.

```
$ ls -l /home/vgpnk/Projects/shokuknow/lanes/souji/round2/{fixtures/r23-trigger-prune.sh,evidence/r23-trigger-prune.out,evidence/r23-worktree-census.out}
-rwxr-xr-x 7597 Oct 23 18:27 fixtures/r23-trigger-prune.sh
-rw-r--r-- 1043 Oct 23 18:27 evidence/r23-trigger-prune.out
-rw-r--r-- 1672 Oct 23 18:28 evidence/r23-worktree-census.out
$ sha256sum … | cut -c1-24
11c136aa71066733d50d226d  fixtures/r23-trigger-prune.sh
510722c11a97f6bca8f93e49  evidence/r23-trigger-prune.out
1ac71c4f7199a134c204b45f  evidence/r23-worktree-census.out
```

All three exist. `510722c1…` and `1ac71c4f…` match the prefixes in the staged rows; `11c136aa…` matches the fixture digest the live S131 row adds. Neither file is tracked in the lane repo (no `lanes/` tree here), so the row's evidence is campaign-side and not lane-re-derivable — same class as the round-24 own-work slice.

## 5. Cross-check against the live appended rows (working tree, uncommitted)

`git diff -- corpus/SOURCES.md` adds exactly 5 lines after S127. Field-by-field comparison with section 1: S128<-S109, S129<-S110, S130<-S111, S131<-S123, S132<-S131; documents, kind, tier, scope and teaches unchanged; only the normalization cells of section 3 differ, plus S131's used-by rewrite and S129's `merge/rebase ignore errors` narrowing. The map in section 3 agrees with the landed data.
