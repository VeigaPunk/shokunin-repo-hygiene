# Sources append block — S128–S132 (round 26, claim C2)

Prepared for L1 (the only integrator). Read-only draft: nothing here is committed.

Provenance: staged package `SOURCES.append.md` under
`/home/vgpnk/Projects/shokuknow/merge/souji/` (opened read-only this run, 5 rows read
verbatim). Target schema: `corpus/SOURCES.md` § Registry — 11 cells per row, no literal
or escaped `|`, `status` mined, `recheck` a cadence, `used-by` exactly the admitted
entries citing the row.

Mapping is by document, not by number: staged S109 → S128, S110 → S129, S111 → S130,
S123 → S131, S131 → S132. Cells changed from staged: `anchor` (round-26 snapshot
reference added where the snapshot exists), `teaches` (row-specific tightening, each
diffed below), `opened` (2026-10-25, the lane's re-open date), `recheck` (cadence only,
after-cadence prose removed to the lesson Gate), `used-by` (admitted entries only).
`source`, `kind`, `tier`, `scope` and `status` are carried from the staged row.

## Append block

Insert the five lines between the markers directly after the S127 row in
`corpus/SOURCES.md` § Registry. The registry header and separator already exist there;
reproduced below only so this block reads as a table on its own — do not append them.

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
<!-- BEGIN S128-S132 APPEND -->
| S128 | git-fetch(1) — https://git-scm.com/docs/git-fetch | docs | A | git 2.56.0 fetch's own auto-maintenance switch, not whether it prunes worktree registrations | § OPTIONS "--auto-maintenance, --no-auto-maintenance, --auto-gc, --no-auto-gc"; installed man page git 2.56.0; snapshot census/round-26/sources/git-fetch.1.txt | fetch ends by running `git maintenance run --auto`; the operator can disable that run per invocation with `--no-auto-maintenance` / `--no-auto-gc`; the switch is default-on | mined | 2026-10-25 | on-release | corpus/knowledge/git-auto-maintenance-trigger-set.md, corpus/knowledge/git-auto-maintenance-trigger-set-r23.md |
| S129 | git/git v2.56.0 builtin/fetch.c, builtin/merge.c, builtin/rebase.c, builtin/am.c, builtin/commit.c — https://github.com/git/git/blob/v2.56.0/builtin/fetch.c | code | A | the set of porcelain commands that call `run_auto_maintenance` at tag v2.56.0; call sites only, not a behavioural proof that any of them prunes | tag v2.56.0: builtin/fetch.c:2926, builtin/merge.c:509, builtin/rebase.c:572, builtin/am.c:1942, builtin/commit.c:1965; snapshots census/round-26/sources/git-builtin-{fetch,merge,rebase,am,commit}.c | fetch, merge, rebase, am and commit each call `run_auto_maintenance`; the calls sit after the work completes and merge/rebase ignore errors from `git maintenance run --auto` | mined | 2026-10-25 | on-release | corpus/knowledge/git-auto-maintenance-trigger-set.md, corpus/knowledge/git-auto-maintenance-trigger-set-r23.md |
| S130 | git/git v2.56.0 builtin/pull.c — https://github.com/git/git/blob/v2.56.0/builtin/pull.c | code | A | how `git pull` reaches fetch's auto-maintenance: it spawns `git fetch` as a child process, so the trigger is inherited rather than duplicated | tag v2.56.0: builtin/pull.c:392 `strvec_pushl(&cmd.args, "fetch", "--update-head-ok", NULL);`; snapshot census/round-26/sources/git-builtin-pull.c | `git pull` runs `git fetch` as a child, so pull's auto-maintenance exposure is fetch's, reached by process spawn rather than a second `run_auto_maintenance` call | mined | 2026-10-25 | on-release | corpus/knowledge/git-auto-maintenance-trigger-set.md, corpus/knowledge/git-auto-maintenance-trigger-set-r23.md |
| S131 | souji round-2 fixture r23-trigger-prune.sh — lanes/souji/round2/fixtures/r23-trigger-prune.sh | own-work | A | whether `git fetch`/`merge`/`rebase`/`pull` auto-maintenance actually prunes a worktree registration on git 2.56.0; measured on this host, not inferred from call sites | fixture r23-trigger-prune.sh, cases SOUJI-R23-TRIGGER-{fetch,fetch-auto-off,pull,merge,rebase,locked,fresh}; git 2.56.0 (2026-10-23), kernel 7.2.11-arch1-1; evidence lanes/souji/round2/evidence/r23-trigger-prune.out (sha256 510722c1…); fixture sha256 11c136aa…; scratch /var/tmp/souji-r23-trigger.XXXXXX, no residue | fetch, pull, merge and rebase each take a stale worktree registration 2 to 1 with no souji receipt; `maintenance.auto=false` and `git worktree lock` each hold it at 2; a fresh (unaged) registration survives, showing the expiry not the trigger is what spares it | mined | 2026-10-25 | 90d | corpus/knowledge/git-auto-maintenance-trigger-set-r23.md |
| S132 | souji round-2 census r23-worktree-census — lanes/souji/round2/evidence/r23-worktree-census.out | own-work | A | whether the fleet's own `git worktree` set holds registrations today's git would prune; a read-only census of the live fleet, not the round-12 point-in-time figure | evidence/r23-worktree-census.out (sha256 1ac71c4f…), 2026-10-23, git 2.56.0; `worktree list` and `worktree prune --dry-run` only, never `worktree prune` | the fleet repo has 5 registrations, 0 prunable and 0 locked — `prune --dry-run` reports nothing even at `--expire=now` — so the round-12 "0 prunable, 3 locked" figure is stale: the count grew to 5 while the locked count fell to 0 | mined | 2026-10-25 | 90d | corpus/knowledge/git-auto-maintenance-trigger-set-r23.md |
<!-- END S128-S132 APPEND -->

## Staged rows (verbatim)

One row per staged id, bytes copied from the staged file.

### staged S109 → S128
| S109 | git-fetch(1) — https://git-scm.com/docs/git-fetch | docs | A | git 2.56.0 fetch's own auto-maintenance switch, not whether it prunes worktree registrations | § OPTIONS "--auto-maintenance, --no-auto-maintenance, --auto-gc, --no-auto-gc"; installed man page git 2.56.0 (2026-09-27) | fetch ends by running `git maintenance run --auto`; the operator can disable that run per invocation with `--no-auto-maintenance` / `--no-auto-gc` | mined | 2026-10-23 | on-release — host `git --version` is 2.56.0 | corpus/knowledge/git-auto-maintenance-trigger-set.md, corpus/knowledge/git-auto-maintenance-trigger-set-r23.md |

### staged S110 → S129
| S110 | git/git v2.56.0 builtin/fetch.c, builtin/merge.c, builtin/rebase.c, builtin/am.c, builtin/commit.c — https://github.com/git/git/blob/v2.56.0/builtin/fetch.c | code | A | the set of porcelain commands that call `run_auto_maintenance` at tag v2.56.0; call sites only, not a behavioural proof that any of them prunes | tag v2.56.0: builtin/fetch.c:2926, builtin/merge.c:509, builtin/rebase.c:572, builtin/am.c:1942, builtin/commit.c:1965 | fetch, merge, rebase, am and commit each call `run_auto_maintenance`; the calls sit after the work completes and ignore errors from `git maintenance run --auto` | mined | 2026-10-23 | on-release — re-grep call sites at the next host git tag | corpus/knowledge/git-auto-maintenance-trigger-set.md, corpus/knowledge/git-auto-maintenance-trigger-set-r23.md |

### staged S111 → S130
| S111 | git/git v2.56.0 builtin/pull.c — https://github.com/git/git/blob/v2.56.0/builtin/pull.c | code | A | how `git pull` reaches fetch's auto-maintenance: it spawns `git fetch` as a child process, so the trigger is inherited rather than duplicated | tag v2.56.0: builtin/pull.c:392 `strvec_pushl(&cmd.args, "fetch", "--update-head-ok", NULL);` | `git pull` runs `git fetch` as a child, so pull's auto-maintenance exposure is fetch's, reached by process spawn rather than a second `run_auto_maintenance` call | mined | 2026-10-23 | on-release — re-read builtin/pull.c at the next host git tag | corpus/knowledge/git-auto-maintenance-trigger-set.md, corpus/knowledge/git-auto-maintenance-trigger-set-r23.md |

### staged S123 → S131
| S123 | souji round-2 fixture r23-trigger-prune.sh — lanes/souji/round2/fixtures/r23-trigger-prune.sh | own-work | A | whether `git fetch`/`merge`/`rebase`/`pull` auto-maintenance actually prunes a worktree registration on git 2.56.0; measured on this host, not inferred from call sites | fixture r23-trigger-prune.sh, cases SOUJI-R23-TRIGGER-{fetch,fetch-auto-off,pull,merge,rebase,locked,fresh}; git 2.56.0 (2026-10-23), kernel 7.2.11-arch1-1; evidence lanes/souji/round2/evidence/r23-trigger-prune.out (sha256 510722c1…); scratch /var/tmp/souji-r23-trigger.XXXXXX, no residue | fetch, pull, merge and rebase each take a stale worktree registration 2 -> 1 with no souji receipt; `maintenance.auto=false` and `git worktree lock` each hold it at 2; a fresh (un-aged) registration is spared at 2, so the task ran and the expiry protected it | mined | 2026-10-23 | 90d — re-run `bash fixtures/r23-trigger-prune.sh` (expect 7 PASS and exit 0) | corpus/knowledge/git-auto-maintenance-trigger-set-r23.md |

### staged S131 → S132
| S131 | souji round-2 census r23-worktree-census — lanes/souji/round2/evidence/r23-worktree-census.out | own-work | A | whether the fleet's own `git worktree` set holds registrations today's git would prune; a read-only census of the live fleet, not the round-12 point-in-time figure | evidence/r23-worktree-census.out (sha256 1ac71c4f…), 2026-10-23, git 2.56.0; `worktree list` and `worktree prune --dry-run` only, never `worktree prune` | the fleet repo has **5 registrations, 0 prunable and 0 locked** — `prune --dry-run` reports nothing even at `--expire=now` — so the round-12 "0 prunable, 3 locked" figure is stale: the count grew to 5 while the locked count fell to 0 | mined | 2026-10-23 | 90d — re-run the read-only census (expect 5 registrations, 0 prunable) | corpus/knowledge/count-objects-garbage-semantics-r23.md |

## Per-row normalization notes

- S128 ← S109 (docs, A). `anchor`: staged `installed man page git 2.56.0 (2026-09-27)`
  became `installed man page git 2.56.0; snapshot census/round-26/sources/git-fetch.1.txt`
  (snapshot present, sha256 78324905…). `teaches`: appended `; the switch is default-on`;
  grounded in the opened snapshot `census/round-26/sources/git-fetch.1.txt:3197`
  ("This is enabled by default."). `recheck`: `on-release — host git --version is 2.56.0`
  became `on-release`; the host-version prose goes to the lesson Gate. `used-by`: both
  admitted entries (staged already named both).
- S129 ← S110 (code, A). `anchor`: snapshot list `census/round-26/sources/git-builtin-` plus the
  five builtin basenames (fetch, merge, rebase, am, commit) added; the five call-site line
  numbers are unchanged and all five were re-found in the opened snapshots
  (fetch.c:2926, merge.c:509, rebase.c:572, am.c:1942, commit.c:1965).
  `teaches`: staged `and ignore errors from git maintenance run --auto` narrowed to
  `merge/rebase ignore errors ...`, which is what the snapshots support — the comment
  appears at merge.c:506-507 and rebase.c:569-570 only, not at the fetch, am or commit
  call sites. `recheck`: re-grep prose removed, cadence `on-release` kept.
- S130 ← S111 (code, A). `anchor`: snapshot `census/round-26/sources/git-builtin-pull.c`
  added; `builtin/pull.c:392` re-found in the snapshot with the same `strvec_pushl` line.
  `teaches`, `scope`, `source` unchanged. `recheck`: re-read prose removed, cadence
  `on-release` kept. `used-by`: both admitted entries.
- S131 ← S123 (own-work, A). `recheck`: the `90d` cadence with its re-run instruction
  became plain `90d`; the re-run instruction is Gate material, not a cadence cell.
  `teaches`: same measured facts, prose tightened — the `2 -> 1` arrow became `2 to 1`,
  `(un-aged)` became `(unaged)`, and the trailing clause became
  `a fresh (unaged) registration survives, showing the expiry not the trigger is what spares it`;
  no new claim and no weakened claim. `used-by`: entry B only (staged row already named it).
  The staged id collides with the lane's existing S123 (git-worktree(1)); the object is the
  same fixture, so the renumber is by document as the prereg prescribes.
- S132 ← S131 (own-work, A). `recheck`: the `90d` cadence with its re-run instruction
  became plain `90d`. `teaches`: only the `**` emphasis markers were dropped; the 5 / 0 / 0
  figures, the `--expire=now` observation and the round-12 staleness statement are
  unchanged. `used-by`: corrected from the staged
  `corpus/knowledge/count-objects-garbage-semantics-r23.md` (a file this round does not
  admit) to the admitting entry `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md`.
- Cell hygiene: all five block rows split on the row delimiter into exactly 11 non-empty
  cells, contain no literal `|` and no escaped `\|`; `opened` is `2026-10-25` and
  `status` is `mined` in every row.

## Limits

- The teaches edits in S128 and S129 are source-supported tightenings, not verbatim staged
  text; if L1 prefers zero teaches drift, revert those two cells to the staged wording and
  keep the snapshot anchors, opened, recheck and used-by changes.
- The `|`-free check covers the block rows written here; the verbatim staged rows above are
  reproduced as read and were also confirmed pipe-free in their cells.
- Snapshot digests quoted here are the lane's `census/round-26/sources/SHA256SUMS` entries
  as opened this run; the files were not re-hashed.
- No lane validator was run from this seat; the K3 census check remains L1's.
