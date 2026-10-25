# ScoutRegroundOwnwork — round 26 w1, re-ground of the two own-work staged rows

## Status

STATUS: PASS — both own-work staged rows re-ground from the campaign bytes this run; the
7 fixture case ids and the 2->1 / 2->2 outcome lines reproduce exactly, the census's
5 / 0 / 0 figures are the figures the evidence file records, and the one-case partial
re-run names the registration. One **material drift** in the census's `gitdir_target_exists`
column (F3) is reported as a finding for L1, not as a change to any frozen counter.

## Evidence

### E1 — staged S123 fixture, 7 case ids, sha256 of both files

Read-only, campaign repo (read-only source; nothing written there):

```
$ sha256sum /home/vgpnk/Projects/shokuknow/lanes/souji/round2/fixtures/r23-trigger-prune.sh \
            /home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-trigger-prune.out
11c136aa71066733d50d226d344df9125401780aa81836f8ca9ca68a9997e65a  .../fixtures/r23-trigger-prune.sh
510722c11a97f6bca8f93e49b8a279f1f109d0222e40f675d001058768e069b4  .../evidence/r23-trigger-prune.out
```

Both prefixes match the staged row's own citations verbatim
(`/home/vgpnk/Projects/shokuknow/lanes/souji/round2/KNOWLEDGE-PROPOSED.md:13`, quote:
"evidence sha256 510722c1…; fixture sha256 11c136aa…") and the SOURCES-PROPOSED S123 row
(`/home/vgpnk/Projects/shokuknow/lanes/souji/round2/SOURCES-PROPOSED.md:15`, quote:
"evidence lanes/souji/round2/evidence/r23-trigger-prune.out (sha256 510722c1…)").

The 7 case ids, read from `evidence/r23-trigger-prune.out` lines 2-8 with their before/after
pairs, in file order:

```
2:id=SOUJI-R23-TRIGGER-fetch case=fetch before=2 after=1 expect=1 verdict=PASS
3:id=SOUJI-R23-TRIGGER-fetch-auto-off case=fetch-auto-off before=2 after=2 expect=2 verdict=PASS
4:id=SOUJI-R23-TRIGGER-pull case=pull before=2 after=1 expect=1 verdict=PASS
5:id=SOUJI-R23-TRIGGER-merge case=merge before=2 after=1 expect=1 verdict=PASS
6:id=SOUJI-R23-TRIGGER-rebase case=rebase before=2 after=1 expect=1 verdict=PASS
7:id=SOUJI-R23-TRIGGER-locked case=locked before=2 after=2 expect=2 verdict=PASS
8:id=SOUJI-R23-TRIGGER-fresh case=fresh before=2 after=2 expect=2 verdict=PASS
9:id=SOUJI-R23-TRIGGER-SUMMARY verdict=PASS
```

All 7 ids named in the assignment — `fetch`, `fetch-auto-off`, `pull`, `merge`, `rebase`,
`locked`, `fresh` — are present exactly once, `verdict=PASS` each, plus a SUMMARY PASS.
4 cases go **2 -> 1** (fetch, pull, merge, rebase); 3 cases stay **2 -> 2** (fetch-auto-off,
locked, fresh). Case order in the evidence file is identical to the fixture's `run_case`
invocation order (`fixtures/r23-trigger-prune.sh:193-199`).

Fixture-side gate properties re-verified from bytes:
- `grep -c 'TMPDIR:-/tmp' fixtures/r23-trigger-prune.sh` -> `0` (QUALITY Q4 holds).
- scratch root `/var/tmp/souji-r23-trigger.XXXXXX`, HOME `/var/tmp/souji-r23-home.XXXXXX`,
  `trap` removes both (`fixtures/r23-trigger-prune.sh:53-54`).
- `find /var/tmp -maxdepth 1 -name 'souji-r23-trigger.*'` / `souji-r23-home.*` -> no such
  file: the fixture left no residue (the 17 `souji-r23-*` entries under /var/tmp are other
  seats' round-23 report artifacts, mtimes 2026-10-25 05:05-05:35, not fixture scratch).

### E2 — staged S131 census, 5 / 0 / 0 figures, sha256

```
$ sha256sum /home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-worktree-census.out
1ac71c4f7199a134c204b45f339aadfc7e90c84b2d640cbed181b3577b9392fd  .../evidence/r23-worktree-census.out
```

Matches the staged S131 row's own citation (`SOURCES-PROPOSED.md:23`, quote:
"evidence/r23-worktree-census.out (sha256 1ac71c4f…), 2026-10-23, git 2.56.0") and
`KNOWLEDGE-PROPOSED.md:203` (quote: "source: S131 — lanes/souji/round2/evidence/r23-worktree-census.out — sha256 1ac71c4f…; 2026-10-23; read-only census").

The 5 / 0 / 0 figures, read from the evidence file:
- **5 registrations** — `evidence/r23-worktree-census.out:8` (`--- git worktree list (count) ---`
  then `5`), and 5 `worktree` lines at lines 11-15 (1 primary + 4 under `/fast/scratch/hyaku/`).
- **0 prunable** — lines 21-23, all three expiry settings report
  "(no output — none prunable)"; line 29 post-check `worktree list count after: 5`.
- **0 locked** — lines 16-19, each extra registration carries `locked=no`.
- Summary line 31, quote: "today: 0 prunable, 0 locked, 5 registrations".

The campaign repo arm also matches: line 26 `worktree list count: 1`, line 27
"prune --dry-run --expire now:        (no output — none prunable)".

### E3 — lane's own `git --version`, re-verified

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin --version
git version 2.56.0
```
Identical to the git that produced the evidence (`r23-trigger-prune.out:1`, quote:
"git_version=git version 2.56.0"). The lane's own repo is a distinct git dir
(`/home/vgpnk/Projects/shokunin/souji-shokunin/.git`), so this is the host git, not a
lane-vendored build.

### E4 — partial re-run of the fixture logic (EXTRA EVIDENCE ONLY, never the admission basis)

Per the assignment, in `/var/tmp/souji-r26-ScoutRegroundOwnwork/`, one case of the fixture
logic re-created from scratch: repo -> `git worktree add` linked worktree -> remove its
directory -> **age nothing** -> `git -c gc.worktreePruneExpire=now worktree prune --dry-run`.

```
$ git init -q $D/repo && git commit --allow-empty -m base
$ git worktree add -q --detach $D/wt-linked HEAD && rm -rf $D/wt-linked
$ git -c gc.worktreePruneExpire=now worktree prune --dry-run
Removing worktrees/wt-linked: gitdir file points to non-existent location
rc=0
```

**The registration IS named.** `git worktree list` shows the linked worktree as
`prunable`; the admin dir `wt-linked` survives; no prune was executed (dry-run only).

Discriminating variants run in the same scratch, to locate the mechanism (all `--dry-run`):

| variant | aging | command | named? |
|---|---|---|---|
| A | none | `worktree prune --dry-run` | YES |
| B | none | `-c gc.worktreePruneExpire=now worktree prune --dry-run` | YES |
| C | index aged 4mo | `worktree prune --dry-run` | YES |
| E | admin dir aged 4mo | `worktree prune --dry-run` | YES |
| G | admin dir aged 4mo | `--expire=never` | no |
| H | nothing aged | `--expire=never` | no |
| I | worktree dir PRESENT, admin aged | `--expire=never` | no |
| J | index aged 4mo | `--expire=3.months.ago` | YES |
| K | nothing aged | `--expire=3.months.ago` | no |
| L | gitdir file aged 4mo | `--expire=3.months.ago` | no |
| M | HEAD aged 4mo | `--expire=3.months.ago` | no |
| N | index aged 4mo | `--expire=never` | no |
| O | index aged 2 days | `--expire=3.months.ago` | no |
| S | none | `-c gc.worktreePruneExpire=never worktree prune --dry-run` | YES |
| T | index aged 4mo | `-c gc.worktreePruneExpire=never git gc` | no (2 left) |
| U | none | `-c gc.worktreePruneExpire=now worktree prune --dry-run` | YES |
| V | none | `-c gc.worktreePruneExpire=now git gc` | pruned (1 left) |
| W | none | `-c gc.worktreePruneExpire=3.months.ago git gc` | no (2 left) |
| X | none (target gone) | `worktree prune --dry-run` | YES |
| Y | worktree dir PRESENT | `worktree prune --dry-run` | no |
| Z | dir shell present, `.git` file removed | `worktree prune --dry-run` | YES |

### E5 — full 7-case replica, re-run from campaign bytes

The fixture's own per-case logic was copied verbatim from
`/home/vgpnk/Projects/shokuknow/lanes/souji/round2/fixtures/r23-trigger-prune.sh:70-206`
into `/var/tmp/souji-r26-ScoutRegroundOwnwork/replica7.sh` (the source fixture hard-codes
its own scratch root `/var/tmp/souji-r23-trigger.XXXXXX`, which this seat may not use) and
run with the identical `GIT_FG` flags, `GIT_CONFIG_GLOBAL=/dev/null`,
`GIT_CONFIG_NOSYSTEM=1`:

```
git_version=git version 2.56.0
id=SOUJI-R23-TRIGGER-fetch case=fetch before=2 after=1 expect=1 verdict=PASS
id=SOUJI-R23-TRIGGER-fetch-auto-off case=fetch-auto-off before=2 after=2 expect=2 verdict=PASS
id=SOUJI-R23-TRIGGER-pull case=pull before=2 after=1 expect=1 verdict=PASS
id=SOUJI-R23-TRIGGER-merge case=merge before=2 after=1 expect=1 verdict=PASS
id=SOUJI-R23-TRIGGER-rebase case=rebase before=2 after=1 expect=1 verdict=PASS
id=SOUJI-R23-TRIGGER-locked case=locked before=2 after=2 expect=2 verdict=PASS
id=SOUJI-R23-TRIGGER-fresh case=fresh before=2 after=2 expect=2 verdict=PASS
id=SOUJI-R23-TRIGGER-SUMMARY verdict=PASS
EXIT=0
```

All 7 cases reproduce the recorded before/after pairs exactly, byte-for-byte in the
verdict fields, on the same git 2.56.0. This is corroboration of the recorded evidence,
not a substitute for it.

### E6 — upstream mechanism, located in git v2.56.0 source

Fetched this run to `/var/tmp/souji-r26-ScoutRegroundOwnwork/` (sha256 recorded):
`worktree.c` `da5c259a2c78724ac776ad4c21a493f24008ac24d3023f33d30034269b353ff2`,
`builtin/gc.c` `17a03f6f413a82f9a532596b0b3bf5c43119c1d9e8209149dff8d5f69e41e21d`,
`builtin/worktree.c` `af2bd523e1c89e33d5e370941321fa3c3567c50cf44104e2b502f009e298babc`.

- `worktree.c:1016` (the expiry test the fixture exploits), quote:
  "if (stat(file.buf, &st) || st.st_mtime <= expire) {"
- `worktree.c:1017` (the reason string the dry-run prints), quote:
  "strbuf_addstr(reason, _(\"gitdir file points to non-existent location\"));"
- `builtin/gc.c:344` (auto-maintenance invokes the prune with the expiry), quote:
  "strvec_pushl(&prune_worktrees_cmd.args, \"worktree\", \"prune\", \"--expire\", NULL);"
- `builtin/gc.c:144` (the default expiry), quote:
  ".prune_worktrees_expire = xstrdup(\"3.months.ago\"), \\"
- `builtin/worktree.c:259` (standalone `git worktree prune` default), quote:
  "expire = TIME_MAX;"

So the fixture ages the **admin-dir index file's mtime** (`$repo/.git/worktrees/wt-<n>/index`),
which is exactly the `stat(file.buf, &st)` + `st.st_mtime <= expire` test at `worktree.c:1016`
— the fixture targets the right clock, and the `fresh` control (un-aged index, 2 -> 2) is
the control that separates "the trigger did not fire" from "the expiry spared it". This
corroborates the fixture's own header claim at
`fixtures/r23-trigger-prune.sh:60-61` (quote: "PASS requires before==2 exactly AND after==expect; anything else is FAIL.").

### E7 — the lane's own snapshots cross-check byte-identical against upstream v2.56.0

Independent of the staged campaign rows, the lane's `census/round-26/sources/` snapshots
were re-fetched from upstream and compared (`/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-26/sources/`):

```
git-builtin-fetch.c      upstream=f14e15ebdb57 lane=f14e15ebdb57 MATCH
git-builtin-pull.c       upstream=538aa964818a lane=538aa964818a MATCH
git-builtin-merge.c      upstream=b6f5b6637b29 lane=b6f5b6637b29 MATCH
git-builtin-rebase.c     upstream=72b4d35130db lane=72b4d35130db MATCH
git-builtin-am.c         upstream=aa5ac1ce0266 lane=aa5ac1ce0266 MATCH
git-builtin-commit.c     upstream=e566f2092ed5 lane=e566f2092ed5 MATCH
```
(`git-fetch.1.txt` is the installed man page, not the upstream `.txt` doc, so its digest
is not expected to match `Documentation/git-fetch.txt` — not a defect.)

### E8 — upstream prune-expiry semantics, isolated

`git worktree prune` standalone defaults to `expire = TIME_MAX`
(`builtin/worktree.c:259`), i.e. it does **not** consult `gc.worktreePruneExpire`; only the
auto-maintenance path passes `--expire` explicitly (`builtin/gc.c:344`). Confirmed
empirically: variant S (`-c gc.worktreePruneExpire=never` + standalone prune) still named
the registration, while variant T (same config + `git gc`) did not prune. This is why the
fleet census reports "0 prunable" at `--expire=3.months.ago` while a bare
`git worktree prune --dry-run` names entries — see F3.

## Findings

**F1 — S123 (fixture row) re-grounds clean.** All 7 case ids present exactly once with
`verdict=PASS`; 4 cases 2 -> 1, 3 cases 2 -> 2; case order matches the fixture's
`run_case` order; fixture sha256 `11c136aa…` and evidence sha256 `510722c1…` match the
staged row's own citations verbatim; `TMPDIR:-/tmp` count 0; no scratch residue.
**Location:** `/home/vgpnk/Projects/shokuknow/lanes/souji/round2/fixtures/r23-trigger-prune.sh`
(full file read), `/home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-trigger-prune.out`
lines 1-15, `SOURCES-PROPOSED.md:15`, `KNOWLEDGE-PROPOSED.md:9,13`.
**Confidence: high** (bytes read this run; full logic replica reproduced all 7).

**F2 — S131 (census row) re-grounds clean as to the figures the evidence file records.**
5 registrations, 0 prunable at all three expiry settings, 0 locked, campaign repo 1 / 0;
sha256 `1ac71c4f…` matches the staged row's citation verbatim; the file is internally
consistent (post-check count after = 5).
**Location:** `/home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-worktree-census.out`
lines 1-32, `SOURCES-PROPOSED.md:23`, `KNOWLEDGE-PROPOSED.md:203`.
**Confidence: high** for the 2026-10-23 record.

**F3 — MATERIAL DRIFT in the census's `gitdir_target_exists` column; the live fleet now has
4 prunable registrations. The staged row's `teaches` cell ("0 prunable") is now stale.**
Re-running the census method read-only against the live fleet repo
`/home/vgpnk/Projects/shokunin` today (2026-10-25):

```
git worktree list (count)          -> 5
prune --dry-run (default)          -> 4 prunable
prune --dry-run --expire=now       -> 4 prunable
prune --dry-run --expire=never     -> (none)
prune --dry-run --expire=3.months.ago -> (none)
git worktree list --porcelain      -> 4 lines: "prunable gitdir file points to non-existent location"
post-check                         -> 5 registrations, 4 admin dirs intact, nothing pruned
```

Cause, established from upstream `worktree.c:1013-1021`: a registration is prunable when
its `gitdir` file points to a non-existent location **and** the admin index mtime is at or
before `expire`. The census recorded `gitdir_target_exists=yes` for all 4 extras
(`r23-worktree-census.out:16-19`); today **all 4 targets are gone** — `/fast/scratch/hyaku/`
still exists but no longer contains `native-mutation-proof`, `root-closure-null-round`,
`s3-nonauthor64`, `s3-ready66` (existence check only; no contents read). The admin index
mtimes are unchanged (2026-10-21 19:24:02 / 17:37:44 / 15:58:38 / 17:49:14), identical to
the census, so the registrations were not aged — their *targets* were removed.

Consequence for the round: the census's "0 prunable" holds at the **effective** expiry
(`gc.worktreePruneExpire` unset -> default `3.months.ago`, `builtin/gc.c:144`), which is
what auto-maintenance actually uses — which is why `--expire=3.months.ago` still reports
none. But at the standalone `git worktree prune` default (`expire = TIME_MAX`,
`builtin/worktree.c:259`) and at `--expire=now`, all 4 are prunable **today**.
The staged row's `teaches` cell, as drafted at
`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/sources-append-block.md:31`
and `entry-git-auto-maintenance-trigger-set-r23.md:79-83,95,110`, asserts "0 prunable" and
"the fleet is currently *not* exposed". The first is now false at two of three expiry
settings; the second is true only under the `3.months.ago` default, and it is a
point-in-time statement about a fleet that other seats are actively mutating.
**This is a finding for L1, not a proposed change to any frozen counter** — C2's counters
(K1 `ground: F1` count, K2 gate-check, K3 registry row count, K4 coverage agreement) are
not the ones at issue, and no predicate/target/case set may change after data. The
honest handling is inside the **cells and prose** the round already controls: the census
row's `teaches` cell and the entry body's "currently not exposed" phrasing should be
qualified as a 2026-10-23 observation with its expiry basis stated, rather than asserted
as a live fleet state. The `recheck` cell `90d` already asks for exactly this
re-census.
**Location:** `/home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-worktree-census.out:16-19,21-23,31`;
`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/sources-append-block.md:31,82-87`;
`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/entry-git-auto-maintenance-trigger-set-r23.md:5,79-83,95,110`;
upstream `worktree.c:1013-1021`, `builtin/gc.c:144`, `builtin/worktree.c:259`.
**Confidence: high** (both the upstream code and the live probe re-run this run; the
fleet probe was strictly read-only — `worktree list` / `worktree prune --dry-run` only,
post-check confirms 5 registrations and 4 intact admin dirs).

**F4 — the id-collision renumber holds, and the S132 `used-by` correction is required.**
The lane's own registry at base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd` ends at **S127**
(rows S001-S127 present; S123 present, S131 and S132 absent), so the staged ids S123 and
S131 both collide and the renumber S123->S131 / S131->S132 is needed and free. The staged
S131 row's `used-by` names `corpus/knowledge/count-objects-garbage-semantics-r23.md`, which
**does not exist** in the lane (`ls corpus/knowledge/` lists `count-objects-garbage-readings-r25.md`
and `count-objects-linked-worktree-garbage.md`; the `-semantics-r23.md` file is absent).
The drafted correction at `sources-append-block.md:85-87` (used-by ->
`corpus/knowledge/git-auto-maintenance-trigger-set-r23.md`) is therefore necessary, and the
two admitted entry files **do** exist in the lane working tree
(`corpus/knowledge/git-auto-maintenance-trigger-set.md`,
`corpus/knowledge/git-auto-maintenance-trigger-set-r23.md`). Consistent with C2's K3
"mined used-by paths missing 0".
**Location:** `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd:corpus/SOURCES.md`
(rows S001-S127); `sources-append-block.md:11-12,82-87`;
`/home/vgpnk/Projects/shokuknow/lanes/souji/round2/SOURCES-PROPOSED.md:23` (used-by cell).
**Confidence: high.**

**F5 — one caveat in the staged evidence's own framing, now visible.** The fixture's header
says the expected `after` value is "OBSERVED truth" and that the "fresh" case shows "the
task RAN but the expiry protected it". Re-run confirms this is exactly right, but only
because `fetch`/`merge`/`rebase`/`pull` reach `run_auto_maintenance` and the *maintenance*
path passes `--expire 3.months.ago` (`builtin/gc.c:344`), while a bare
`git worktree prune` uses `TIME_MAX` and would prune regardless of age (variant X/Y above).
The staged rows already scope themselves to "auto-maintenance", so this is a precision
note for the lesson Gate, not a defect in either row.
**Location:** `fixtures/r23-trigger-prune.sh:10-14,165-172`; upstream `builtin/gc.c:338-347`,
`builtin/worktree.c:259`.
**Confidence: high.**

**F6 — campaign repo arm re-verified.** `/home/vgpnk/Projects/shokuknow` has 1
registration and 0 prunable at `--expire=now` today (read-only `worktree list` /
`worktree prune --dry-run` only, HEAD `8b94c5c1`), matching census line 26-27.
**Location:** `/home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-worktree-census.out:25-27`.
**Confidence: high.**

## Attack log

No attack seat: this item is a re-ground, not an attack, and no frozen counter, predicate,
target or case set is proposed for change. F3 is reported as a finding with a
cells-and-prose handling path that the round already owns (the row's `teaches`/`recheck`
cells and the entry body prose); changing a counter after data would itself be a
preregistration violation.

## Bound compliance

- Nothing was written, moved, deleted or quarantined outside
  `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/` (this report).
  No `git add/commit/push/stash/checkout/reset`, no `jj` mutation, no signals.
- `/home/vgpnk/Projects/shokuknow` was read only (read, grep, sha256sum, `git worktree
  list`, `git worktree prune --dry-run`); no write, commit, fetch, push or campaign tool.
- The fleet repo `/home/vgpnk/Projects/shokunin` was probed read-only: `worktree list`,
  `worktree prune --dry-run` (dry-run only — the mutating form was never run), `config
  --get`, `rev-parse`, `ls`, `stat`, `cat` of admin `gitdir` files. Post-check confirms
  5 registrations and 4 intact admin dirs. `.scratch/`, `.ufo/state/`, `.ufo/watchdog.log`,
  `MANIFEST.json`, fleet `scripts/` and `templates/` were not touched; no
  `census/operator-sweep-*` contents read; no live `/proc` census.
- `/fast/scratch/hyaku/` was checked for **existence only** (directory listing + `test -e`),
  never contents; the 4 hyaku worktree targets were found absent.
- Scratch lived only in `/var/tmp/souji-r26-ScoutRegroundOwnwork/` and was removed at the
  end of the run. `git -C "$D" rev-parse --show-toplevel` was confirmed to print `$D` before
  the first commit in that scratch.
- Tooling: no install was needed or performed; `git 2.56.0`, `coreutils sha256sum 0.8.0`,
  `curl 8.23.0` were already present.
