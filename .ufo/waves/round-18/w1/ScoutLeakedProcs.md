STATUS: DONE — 58 residue processes confirmed, 24 scratch-dir families, all souji-origin, all under /var/tmp; baseline pid set reproduced exactly (0 new, 0 reaped); no other-lane residue on this host.

# ScoutLeakedProcs — read-only host residue census (C3 premise + adjacency)

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin, base b5763415cc67ecff1e8fe56c58c39a6fb106d7a3.
Method: `ps` + `/proc/<pid>/{stat,cmdline,cwd,wchan}` only. **No signal was sent to any process; no `environ` was read; no tool was run against any real directory.** Nothing was written outside this report and four scratch JSON files under /var/tmp (removed at end).

Scan timestamps: 2026-10-20T19:53:20Z … 19:56:54Z (local 16:53–16:57, TZ −03).

## 1. Headline counts (observed)

| quantity | value |
|---|---|
| host processes total | 963 |
| current-uid (1000) processes | 208 |
| uid-1000 processes with **deleted cwd** | **58** |
| uid-1000 processes whose **argv names a missing /var/tmp, /tmp or /dev/shm path** | **58** (identical pid set) |
| residue split | 44 r15-family + 14 r17-family |
| distinct scratch families (`mkdtemp` dirs) | **24** (22 × `r15-census-config.*`, 2 × `r17-census-hygiene.*`) |
| distinct (pgid,sid) process groups | 24 — **all 24 group leaders already dead** |
| age range | **3 229 s … 21 726 s** (0.90 h … 6.03 h) |
| process state / wchan | 58/58 state `S`; wchan = `wait_for_partner` ×26 (every git), `do_wait` ×26 (22 r15 runners + 4 r17 middle bashes), `anon_pipe_read` ×6 (r17 outer bashes) |
| residues rooted at /tmp or /dev/shm | **0** (all 58 are /var/tmp; /tmp and /dev/shm arms of C3 have no positive fixture today) |
| parent | every top-level residue process has ppid **1497 = `/usr/lib/systemd/systemd --user`** (orphan/reparented) |

Commands (exact):

```
ps -eo pid,ppid,pgid,sid,etimes,stat,wchan:20,args      # 963 lines
ps -o pid=,etimes=,stat=,wchan:18=,ppid=,pgid=,sid= -p <58 pids>
python3 -c '<walk /proc: stat, cmdline, readlink cwd, wchan, uid; test existence of every /var/tmp|/tmp|/dev/shm token>'
```

Predicate result: **cwd-deleted set == argv-missing-path set, 58 == 58, set-equal.**

## 2. Families, counts, ages, wchan, parent

"runner" = the bash leading the tree, "git" = the FIFO-blocked git; ages are `ps -o etimes` at 19:53–19:57Z.

### 2a. `r15-census-config.<rand>` — 22 families × 2 = 44 processes

Every family has exactly this shape:

```
bash <FROZEN-CLONE>/tools/souji-census.sh --root /var/tmp/r15-census-config.<rand>/unsafe-repos/r-inc-fifo --include-root   (state S, wchan do_wait, ppid 1497)
  └ /usr/bin/git -C /var/tmp/r15-census-config.<rand>/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree               (state S, wchan wait_for_partner)
```

| family | age (s) | family | age (s) |
|---|---|---|---|
| r15-census-config.7tgaqhd1 | 21 726 | r15-census-config.xcfjf9ps | 17 553 |
| r15-census-config.tf977fa2 | 21 098 | r15-census-config.s8n_rh15 | 11 637 |
| r15-census-config.9lkl1cdg | 20 687 | r15-census-config.rxdxzqi8 | 11 374 |
| r15-census-config.muz4452a | 20 512 | r15-census-config.otdn8qgj | 11 212 |
| r15-census-config.2tbuivzx | 19 240 | r15-census-config.prl783jh | 9 746 |
| r15-census-config.wwwcjof5 | 19 099 | r15-census-config.upcupkw1 | 9 212 |
| r15-census-config.x7las1fv | 19 075 | r15-census-config._17e3yjp | 8 846 |
| r15-census-config.f8u_yo2f | 18 899 | r15-census-config.7yc1yrcp | 6 572 |
| r15-census-config.9bktk3rl | 18 793 | r15-census-config.1hkjbmmt | 3 492 |
| r15-census-config.su2st6_0 | 18 353 | r15-census-config.ujpcunsx | 3 229 |
| r15-census-config.q4lgeupp | 18 195 | r15-census-config.x8xy7rf3 | 18 011 |

(22 families × 2 = 44 procs; both members of a family share the same age ±1 s. Frozen-clone parents, all now deleted from disk: `souji-r16-matrix.{p74cclr3,jku4qe9z,sc9ho6nz,hy6ocfc4,9az4qh_i,9zgl_8hd,6m58cnsu,v6lm0rcz}`, `souji-r16-repin.{z0t4kl7c,v12xk2yg,t4vqobh_,sf2f30d9,qucgbnxl,scjidogf,_i36vtux}`, `souji-r16-PreservationRepin`, `souji-r16` (via `preharm.sh`), `souji-r17-matrix.{qmxy_npd,pmzb8vuw,8cxpl2lv,ccednztz}`. `stat` on each of those dirs: `No such file or directory`.)

Leaked bash cwd = the **scratch root** (`/var/tmp/r15-census-config.<rand> (deleted)`); git cwd = `<root>/unsafe-repos/r-inc-fifo (deleted)` (git `-C` chdirs).

### 2b. `r17-census-hygiene.<rand>` — 2 families, 14 processes, 4 trees

| family | case (argv `--root`) | tree (pid chain) | ages (s) | wchan chain |
|---|---|---|---|---|
| r17-census-hygiene.e80b0xqe | `d2-fifo` | 562276 → 562277 → 562279 | 11 722 | anon_pipe_read → do_wait → wait_for_partner |
| r17-census-hygiene.e80b0xqe | `d2-symlink-fifo` | 596478 → 596479 → 596480 | 11 661 | idem |
| r17-census-hygiene.lwka_g_w | `d2-fifo` | 574643 → 574984 → 574987 → 574989 | 11 720 | anon_pipe_read → anon_pipe_read → do_wait → wait_for_partner |
| r17-census-hygiene.lwka_g_w | `d2-symlink-fifo` | 597162 → 597357 → 597358 → 597359 | 11 660 | idem |

All four top bashes: `bash /var/tmp/souji-r17-FixtureR17Census/{a31642d,cc21683}.sh --root <scratch>/<case>`, ppid 1497. The blocked git in every tree is real `/usr/bin/git` (not a spy/shim):

```
git -C /var/tmp/r17-census-hygiene.<rand>/d2-fifo/b --no-optional-locks [-c core.fsmonitor=false -c core.hooksPath=/dev/null …] status --porcelain -- . :(exclude).ufo/state …
```

The two cases inside one scratch share one pgid (558610 / 558608) and the two waves are exactly 59–60 s apart — one seat shell ran case 08 then case 09.

## 3. Why they are blocked, and why they are unreleasable today (observed + kernel-level inference)

- All 58 are state `S` (interruptible), not `D`: `SIGKILL` would end them immediately; nothing ever signalled them.
- `wait_for_partner` = git's `open(2)` blocked on a **writer-less FIFO** (`info/attributes`). The FIFO's directory is already gone (`os.path.exists` → False, cwd marker `(deleted)`), so opening the path for write to release the reader is **no longer possible** — `unblock_fifos()`-style release only works *before* `rmtree`. The only remaining release path is `SIGKILL` to task pid / process group. This is the strongest argument that C3 must be read-only *detection* and C1's process-group watchdog must *prevent*, not repair.
- Every group leader is dead, so `killpg(pgid)` is the natural cleanup unit, but the 24 groups no longer map to live parents.

## 4. Provenance: which families are souji, which are other lanes/tools

### 4a. Fixture prefixes cross-check (exact files, read in place)

- `tests/fixtures/r15-census-config.py:1481` — `SCRATCH = Path(tempfile.mkdtemp(prefix="r15-census-config.", dir="/var/tmp"))`; cleanup `shutil.rmtree(SCRATCH, ignore_errors=False)` at `:1430`, called from `finally:` at `:1568`. Case `r-inc-fifo` built at `:496` (`[include] path = ../fifo.inc`), driven with `--include-root` at `:1044`, `:1082`, `:1090`.
  **`run_tool` `:773-800` is the leak source:** `subprocess.run(..., timeout=90)` with **no `start_new_session`**, and on `TimeoutExpired` it returns rc 124 at `:788-791` **without killing anything**. The direct child is `strace`, so on timeout only strace dies; its `bash tools/souji-census.sh` child and the FIFO-blocked `git` survive, are reparented to systemd --user, and then `cleanup()` (:1568 → :1430) deletes the scratch under them. Decisive corroboration: the leaked bash's **cwd is the scratch root**, which is exactly `run_tool`'s `cwd=str(SCRATCH)`, and its argv is the fixture's `--root <SCRATCH>/unsafe-repos/r-inc-fifo --include-root` shape; the only divergence is that `TOOL` resolved inside the frozen clone (fixture lives at `<clone>/tests/fixtures/…`, `parents[2]/tools/souji-census.sh`). ⇒ **44/58 are directly attributable to the committed r15 fixture's timeout path, executed from frozen pre-harm clones.**
- `tests/fixtures/r17-census-hygiene.py:1222` — `mkdtemp(prefix="r17-census-hygiene.", dir="/var/tmp")`; case worlds `d2_fleet("d2-fifo", fifo)` `:757` and `d2_fleet("d2-symlink-fifo", symlink_fifo)` `:769` (`mkfifo` registers into `FIFOS` at `:213-216`); cleanup `:1169` calls `unblock_fifos()` `:328-334` **before** rmtree, from `finally:` `:1295`; `run_tool` `:291-315` uses `start_new_session=True` and `os.killpg(proc.pid, SIGKILL)` plus `unblock_fifos()`.
  ⇒ the r17 **fixture itself provably cannot produce these 14 leaks** (its tree is `bash tools/souji-census.sh`, which appears nowhere in the 14). The 14 run a seat-authored wrapper `<clone-root>/{a31642d,cc21683}.sh` (deleted; content unrecoverable) that drove the fixture's case dirs by hand and skipped the fixture's killpg/unblock. `[INFERENCE]` on authorship (wrapper file absent); observed facts are the argv path, the missing census tool in the tree, and the fixture's own reaping code.

### 4b. Other lanes / tools — none as residue; adjacency notes (report only, nothing acted on)

| pid | lane/tool | why it must NOT be flagged |
|---|---|---|
| 422005, 436924 | **mado** lane (`/tmp/mado-verify-regression.Q3pjTX/case/sweep/mutant-R1…sh --selftest`, cwd `/tmp/mado-r20-HarmWatch20-3`) | **live**, all referenced paths exist; `/tmp/mado-*` dirs present. A naive "under /tmp + long-lived" heuristic would false-positive here |
| 1865 | `uwsm aux app-daemon` | wchan `wait_for_partner` **with no missing path** → wchan alone is not a valid residue predicate |
| 2758 | zombie (`Z`, empty cmdline) | reaped by parent; not residue |
| 1 999, 2 083 034, 2 083 039 | 1Password / chromium crashpad | cwd `/home/…` exists; leaderless pgid only |
| 863 272 | `python` in `kama-shokunin` (cmdline `import argparse `) | cwd exists |
| 820 root-owned procs | other uids | invisible to a same-uid census by design (C3 scope = current uid) |

## 5. Comparison with `census/round-18/leaked-procs-before-1631.txt`

- File: 58 rows, mtime `2026-10-20 16:36:56 -0300` (19:36:56Z).
- **Column layout decoded:** `pid ppid pgid ETIMES lstart args` — column 4 is **`etimes`**, not `sid`. Proof: row for 185592 has col4=7631, while `/proc/185592/stat` session is **184726** (verified by `ps -o sid=`). Cross-check of the etimes reading: 185592 `7631 → 9195` and 2650283 `20144 → 21708` — both deltas **exactly 1 564 s**, i.e. one common capture instant ≈ 19:29–19:31Z, matching the `1631` (=16:31 local) in the filename.
- **Pid-set diff vs my census: extra = [], gone = []**, so:
  - no new residue appeared in the ~26 min (1 564 s) between the baseline capture and my scan (round-18 seats are already running fixtures; nothing leaked in that window);
  - nothing has been reaped; the 58 are static.
- Every baseline row's pid/ppid/pgid matches my `/proc` reading, so the baseline is a faithful `ps` capture and is safe to use as C3's `before` artifact.

## 6. Consequences for C3 / C1 (smallest fixes, advisory)

1. **C3 field set is sufficient on this host**: pid, ppid, pgid, etimes, state, wchan, reason, cwd/argv path all readable as uid 1000 without privilege. Use `reason = cwd-deleted` and/or `argv-path-missing` (both fire on 58/58); do **not** use `wchan==wait_for_partner` (27 uid-1000 procs match, 1 benign) and do **not** use "leaderless pgid" (5 benign procs) as the predicate.
2. **Grouping key for the report/tool**: `(pgid, sid)` → 24 groups for 58 procs; the family (first path segment under /var/tmp) gives the human-meaningful 24 families. A `--json` row set should carry both.
3. **Regression fixtures must be bounded**: the r15 fixture leaks by construction (`run_tool` :773-800). Mirror `r17-census-hygiene.py:291-315` (`start_new_session=True` + `os.killpg(SIGKILL)` on `TimeoutExpired` + FIFO unblock before rmtree) or reuse the same helper. The r17 case-by-case `unblock_fifos()` must stay *before* the rmtree — after unlink it is unreachable (see §3).
4. **Seat-level wrappers are the residual risk**: the 14 r17-family procs came from a hand-rolled `.sh`, which bypassed all fixture reaping. If C1/C3's acceptance wants "a red arm leaves 0 blocked processes", the arms should be driven only through the committed fixtures (or a wrapper that itself uses the same process-group discipline).
5. **Boundary of the census**: 820/963 host procs are other-uid; a same-uid tool cannot (and per spec should not) see them. Also the residue currently has **no /tmp or /dev/shm positives**, so those arms are unexercised on this host.

## 7. Verdict

- C3 premise **holds**: residue is real, countable, 58 processes / 24 families, all state `S` blocked in FIFO `open(2)`, all cwd-deleted, all reparented to systemd --user, ages 0.90–6.03 h.
- The goal's "all from souji fixtures" **holds by family prefix**, with one refinement: 44 are the r15 fixture's own `run_tool` timeout children (fixture code at `tests/fixtures/r15-census-config.py:773-800`), 14 are seat-wrapper leaks over r17 fixture case dirs (`r17-census-hygiene.py:757,769`), not the r17 fixture's `run_tool`.
- **No other lane or tool** contributes residue; `mado` is live in /tmp and must stay out of any "residue" list.
- Baseline artifact confirmed identical (pid-for-pid), so any post-fix run should show a strict drop from 58 → 0.

## 8. Remaining unknowns

- Contents of `a31642d.sh` / `cc21683.sh` (deleted with `/var/tmp/souji-r17-FixtureR17Census`); authorship is inference from argv + absence of the census tool in the tree.
- Which actor deleted the two `r17-census-hygiene.*` scratch dirs after the wrapper died (fixture `cleanup()` vs harness reaper) — both are consistent with the evidence.
- Exact baseline capture second (bounded to 19:29–19:31Z by the 1 564 s etimes delta).
- Whether any of the 58 predates the r15 scratch they point at (mtime of the deleted dirs is unreadable by definition).
