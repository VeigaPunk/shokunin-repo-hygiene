# R41w2scout01 — Misroot & residue sweep (read-only)

- Seat: R41w2scout01 (souji round 41, wave 2, scout). Sweep window opened 2026-10-28T20:16:23-03:00.
- Identity: `whoami` → `vgpnk`, `id -u` → `1000` (never root). Read-only sweep: nothing moved, nothing deleted except my own scratch dir at the end. Only writes: this report + `/fast/scratch/hyaku/souji-r41/R41w2scout01/` (deleted before yield). No tools installed (none needed).
- Round start reference: 2026-10-28 18:30.

## 1. Fleet-root status, untracked paths naming souji / round 41

Command (no pathspec):
```
git -C /home/vgpnk/Projects/shokunin status --porcelain
git -C /home/vgpnk/Projects/shokunin status --porcelain -uall
```
Observed: 39 index-adds (` A`: `.scratch/closure-mado-r50.json`, 23× `.scratch/closure-r54/work-c*/**`, 5× `.scratch/kasegi-r44/R44Critic5/**`, `.scratch/source-routing-queue.md`, `o.bin`, `oldrep1.out`, `oldrep2.out`), 1 worktree-modified (` M .scratch/goal-20261028-hyaku-run11.md`), and exactly 4 untracked entries:
```
?? .scratch/closure-r54/lane/
?? .scratch/closure-r54/work-c2-base/clone/
?? .scratch/closure-r54/work-c2/clone/
?? lane3/
```
`-uall` output is identical: each dir contains its own `.git`, so git treats them as embedded repos and does not descend. Fleet `.gitignore:1` is `*-shokunin/` (why lanes are invisible to tracking; `git ls-files -- souji-shokunin` → 0 files).

Content scan (`souji|round[ -]41`, case-insensitive, grep tool over each untracked dir):

1. **`/home/vgpnk/Projects/shokunin/lane3/`** — a full **kengaku-shokunin** checkout at fleet root (misrooted sibling lane). Evidence: `lane3/LOG.md:1` "# kengaku-shokunin — Iteration Log"; `git -C lane3 log --oneline -1` → `297e179 round-50: receipt notes — the scratch FENCE path is not load-bearing…`; `git -C lane3 status --porcelain | wc -l` → 0 (clean tree); NOT registered in fleet `git worktree list` (shows only the fleet root, detached HEAD 1486cf93). Created 2026-10-28 14:59; `.git` mtime 2026-10-28 19:44 (touched during this round). **527+ files name souji/round-41**, but all are kengaku's own material: LOG.md:1231 "## Round 41 (hyaku run 9, 2026-10-26)" (kengaku's KengakuR41 freeze `8ef8b4fc`, landing `74513c06`, `corpus/lessons/round-41.md`), and kengaku's sibling scans OF souji (e.g. `.ufo/waves/round-25/build/ConnSoujiKaidoku.md` reviewing souji `tools/souji-landing-gate.py:31-34/:217-221`, `census/round-12/sources-census.sh`, `census/round-13/count-claims.py`). **No souji round-41 candidate bytes.** Not touched.
2. **`.scratch/closure-r54/lane/`** — tameshi-shokunin working copy (`LOG.md:1` "# tameshi-shokunin — Iteration Log"), 23,983 files, dated 2026-10-28 12:28. 701+ match files across the three closure dirs; all historical evidence copies (e.g. `.ufo/evidence/round-16/Overlap1/manifest-replay.txt:29` "souji-shokunin/PROVINCE.md: OK", round-18 `coldread/ledger.json` souji-shokunin vault-path hashes). Not touched.
3. **`.scratch/closure-r54/work-c2/clone/`** (15,750 files, 12:29) and **`.scratch/closure-r54/work-c2-base/clone/`** (14,377 files, 12:30) — same tameshi closure clones; same character of matches. Not touched.

**Verdict (1):** no untracked FILE at fleet root carries souji round-41 candidate material; the four untracked dirs are sibling lanes' embedded-repo workspaces whose content merely *references* souji/round 41. `lane3/` is the notable misroot (a clean, ~50-round kengaku lane parked at fleet root, git-active as recently as 19:44 today) — reported, untouched per instructions.

Context (observation only, not untracked): the fleet index holds 39 never-committed adds; none souji-named. `o.bin`, `oldrep1.out`, `oldrep2.out` sit at fleet ROOT (not under `.scratch/`) — misroot-flavored but not souji; content not inspected (out of scope).

## 2. Residue older than round start (2026-10-28 18:30) belonging to souji seats

### 2a. `/fast/scratch/hyaku/souji-r41` — clean of pre-round residue
- `du -sh` → **1011M** (at 20:16:23); 33 top-level entries (32 dirs + `base-tool.py`).
- `find /fast/scratch/hyaku/souji-r41 -not -newermt '2026-10-28 18:30'` over the **whole tree** → **0 entries**. Oldest entry is `base-tool.py` at 18:45:10 (its header: "souji-worktree-drift.py — F1 fleet worktree-registration drift detector (r36 C3)" — a current-round copy of the frozen tool). All seat dirs are dated 20:10–20:16 today.
- Per-seat sizes (du, ~20:18, tree actively growing): R41w2executor03 430M, R41w2executor04 381M, R41w2critic06 219M, R41w2mutationtester06 189M, R41w2executor02 38M (dir appeared after the first `ls -la`), R41w2sentinel02 14M, R41w2critic01 9.5M, others ≤5M. Caveat: per-dir du ran ~2 min after the 1011M total and sums to ≈1.29G — tree growth plus git-clone hardlink double-counting across per-dir invocations; both numbers are as-observed.

### 2b. `/tmp` and `/var/tmp` souji-named leftovers OLDER than round start — 15 paths, ≈209M total
Command: `find /tmp /var/tmp -maxdepth 1 -name 'souji*' -not -newermt '2026-10-28 18:30' -printf '%T+ %p\n'` + `du -sh`:

| path | size | mtime |
|---|---|---|
| `/var/tmp/souji-r21-replay-eq45dano` | **202M** | 2026-10-26 14:06 |
| `/var/tmp/souji-census-selftest.XXl2r7` | 2.2M | 2026-10-27 09:06 |
| `/var/tmp/souji-census-selftest.uFAiOl` | 1.7M | 2026-10-28 08:48 |
| `/var/tmp/souji-r18-FixtureR18Bounded.6bewdtxp` | 1.2M | 2026-10-26 14:07 |
| `/var/tmp/souji-r18-FixtureR18Bounded.du6kpc_5` | 1.2M | 2026-10-26 16:26 |
| `/var/tmp/souji-r16-lgfixture-vnbltez6` | 720K | 2026-10-26 14:07 |
| `/tmp/souji-r36-closure-entry.json` | 8.0K | 2026-10-28 12:11 |
| `/var/tmp/souji-r37-closure.json` | 8.0K | 2026-10-28 13:23 |
| `/tmp/souji-r34-closure.json` | 4.0K | 2026-10-27 12:31 |
| `/tmp/souji-round-35-closure.json` | 4.0K | 2026-10-28 09:59 |
| `/var/tmp/souji-r34-canary` | 0B | 2026-10-27 05:13 |
| `/var/tmp/souji-r34-recon.133mcm` | 12B | 2026-10-27 08:40 |
| `/var/tmp/souji-r34-recon.k8WP2k` | 12B | 2026-10-27 08:40 |
| `/var/tmp/souji-r34-n3b-canary.oYZTiC` | 15B | 2026-10-27 08:53 |
| `/tmp/souji-r29-wave-capture-fixture` | 0B | 2026-10-26 13:57 |

The single dominant item is `/var/tmp/souji-r21-replay-eq45dano` (202M, round-21 replay fixture). **None of this was touched by me** — cleanup belongs to an owner seat.

Post-round-start souji tmp (for completeness): `/var/tmp/souji-r29-c1-fixture` (0B, 18:45:52), `/var/tmp/souji-r29-wave-capture-fixture` (0B, 18:47:33). `/var/tmp/souji-census-now.{052bgx,IKhjqJ}` were seen by `ls` at 20:16 and gone at `stat` minutes later — transient sibling activity.

Adjacent r41-named leftovers outside the `souji*` glob (all pre-round; ownership not proven to souji seats — flagged, untouched): `/tmp/r41-c1-counter.py` (169,155B, 2026-10-26 18:50), `/tmp/r41-landed.txt` (478B, 10-27 05:33), `/tmp/r41-closure-entry.json` (1,998B, 10-28 08:59), `/tmp/closure-kasegi-r41.json` (3,679B, 10-27 10:07, kasegi project), `/tmp/kasegi_r41_outside_probe` (6B, 10-27 08:43), `/tmp/closure-souji-r38.json` (5,607B, 10-28 14:32).

**Verdict (2):** zero pre-round residue under the round's own scratch root; ≈209M of genuine pre-round souji residue sits in `/tmp`+`/var/tmp` (15 paths, table above), dominated by one 202M round-21 replay dir.

## 3. chmod-000 / unreadable leftovers under `/fast/scratch/hyaku/souji-r41`

Command: `find /fast/scratch/hyaku/souji-r41 ! -readable -printf '%M %u:%g %s %p\n'` (final pass with `! -type l` to drop symlink false positives).

- **PERSISTENT cleanup blockers — 2 directories, mode `d---------` (000):**
  - `/fast/scratch/hyaku/souji-r41/R41w2executor03/tmp/base-12/r15-census-config.pgiq4cz4/home/.omp/agent`
  - `/fast/scratch/hyaku/souji-r41/R41w2executor03/tmp/tip-12/r15-census-config.uh_9v0ff/home/.omp/agent`
  Both 88B, mtime 2026-10-28 20:16:37, owner vgpnk. find's own stderr: "Permission denied (os error 13)" on both — children cannot be enumerated, so `rm -rf` of `R41w2executor03/tmp` **will fail** until the owner seat `chmod u+rwx`es them. They are census-config test fixtures (r15-census-config mktemp trees) with a deliberately 000-mode `.omp/agent`. Flagged to R41w2executor03 via peer message.
- **TRANSIENT chmod-000 FILES named `denied`** (25B, `----------`): observed in find at 20:16:37 under `R41w2critic03/work/M17/tmphqgc8grj/o/` and `R41w2critic04/K-SIGKILL-4p5-991058/tmpq6ublwji/o/`; both gone at 20:18 `stat`; new instances reappeared under fresh parents at 20:19:01 (`R41w2critic04/F3 shared-kill work/tmpx35rt7xe/o/denied`) and 20:19:15 (`R41w2sentinel02/work/term-refusal-sites/tmpfvh35ndz/o/denied`). These are sibling seats' per-run refusal-test artifacts; their parent dirs stay rwx, so they do **not** block deletion — any fixed list of them is stale within minutes.
- **Non-issues excluded:** ~17 `! -readable` hits are dangling-by-design symlinks (`…/tests/vault/vadv54-run/q/led-dangling.tsv`, 11B targets) inside seat clones (R41w2executor03/04 base+tip, R41w2scribe04, R41w2connector01) — committed vault fixtures, harmless for `rm -rf`. One ENOENT race during the walk (`R41w2executor04/w/tip-r37-drift-mutants/.../packed-refs.lock` vanished mid-find — sibling mid-write).

**Verdict (3):** exactly two persistent mode-000 paths exist, both directories under `R41w2executor03/tmp/*-12/r15-census-config.*/home/.omp/agent`; they are the only real cleanup blockers. Everything else unreadable is either a by-design dangling symlink or a churning `denied` fixture.

## Commands actually run (all read-only except mkdir/rm of my own scratch)
1. `mkdir -p /fast/scratch/hyaku/souji-r41/R41w2scout01` ; `whoami` ; `id -u` ; `date -Ins`
2. `git -C /home/vgpnk/Projects/shokunin status --porcelain` ; `… status --porcelain -uall | wc -l` ; `… rev-parse --show-toplevel`
3. `ls -la /fast/scratch/hyaku/souji-r41` ; `du -sh /fast/scratch/hyaku/souji-r41` ; `du -sh /fast/scratch/hyaku/souji-r41/*/ …`
4. `find /fast/scratch/hyaku/souji-r41 -mindepth 1 -maxdepth 1 -printf '%T+ %M %u:%g %p\n' | sort`
5. `find /fast/scratch/hyaku/souji-r41 -not -newermt '2026-10-28 18:30' -printf '%T+ %s %p\n'` (→ 0 lines)
6. `ls -la /tmp/souji* /var/tmp/souji*` ; `du -sh /tmp/souji* /var/tmp/souji*` ; `find /tmp /var/tmp -maxdepth 1 -name 'souji*' -not -newermt '2026-10-28 18:30' -printf …` ; `ls -d /tmp/*souji* /tmp/*[Rr]41* /var/tmp/*souji* /var/tmp/*[Rr]41*`
7. `find /fast/scratch/hyaku/souji-r41 ! -readable -printf …` (twice; final pass `! -type l`), stderr captured to my scratch
8. `stat -c '%A %a %10s %y %n' <the four 000-mode paths>` ; `stat -c '%y %10s %n' <six r41-named tmp leftovers>`
9. `ls -la` + `find -type f | wc -l` on the four untracked dirs; `sed -n '1,3p'` of their LOG.md; `head -5 lane3/AGENTS.md`; `find lane3 -maxdepth 1 -name '*shokunin*'`
10. `git -C lane3 log --oneline -1` ; `git -C lane3 status --porcelain | wc -l` ; `git -C /home/vgpnk/Projects/shokunin worktree list` ; `git -C /home/vgpnk/Projects/shokunin ls-files -- souji-shokunin | wc -l` ; `git … check-ignore -v souji-shokunin`
11. grep tool (read-only): pattern `souji|round[ -]41` over `lane3/`, `lane3/LOG.md`, and the three closure dirs; pattern `souji` over the closure LOG/AGENTS files
12. `sed -n '1,5p' /fast/scratch/hyaku/souji-r41/base-tool.py` (identification only)

## Final verdict
- **Misroot:** 4 untracked embedded-repo dirs at fleet root; only `lane3/` (kengaku-shokunin, clean, round-50 tip, git-active 19:44 today) is a substantive misroot — it references souji/round-41 extensively but contains no souji round-41 candidate material. No untracked souji/round-41 candidate file anywhere at fleet root. Nothing moved, nothing deleted.
- **Residue:** `/fast/scratch/hyaku/souji-r41` holds zero pre-round entries (1011M, all current-round, growing). `/tmp`+`/var/tmp` hold 15 souji-named pre-round leftovers ≈209M (`/var/tmp/souji-r21-replay-eq45dano` = 202M) plus 6 adjacent r41-named strays — all flagged for an owner seat, untouched.
- **Cleanup blockers:** exactly 2 mode-000 directories under `R41w2executor03/tmp` (census-config `.omp/agent` fixtures) will break `rm -rf`; owner notified. Transient `denied` 000-files and dangling vault symlinks are non-blockers.
