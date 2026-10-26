# Round 33 w1 — assimilation sweep (SwarmScout41, read-only)

Verdict: **Assimilation: none** — 0 ADMIT-CANDIDATE, all hits REJECT. Nothing in the package serves C1 (capability-table currency) or C2 (scratch-root discipline).

Inputs opened this run (read-only, nothing written under /home/vgpnk/Projects/shokuknow):
- `/home/vgpnk/Projects/shokuknow/merge/souji/MERGE-REPORT.md` (134 rows accepted, 68 knowledge entries, first staged id S109).
- `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/` — `find knowledge -type f | wc -l` = 68.
- Bar: `/home/vgpnk/Projects/shokunin/souji-shokunin/PROVINCE.md` (domain: fleet repository and workspace hygiene), `corpus/QUALITY.md` Q71, Q73, Q74 (scratch root from caller TMPDIR; consumers stay green; refusal guards keep refusals).

## 1. Keyword sweep (case-insensitive, over the 68 staged knowledge files)

Command: `for p in <pat>; do grep -rliE "$p" . | wc -l; done` in `knowledge/corpus/knowledge/`.

| pattern | files | lines |
|---|---|---|
| TMPDIR | 0 | 0 |
| tempfile | 0 | 0 |
| mkdtemp | 0 | 0 |
| mktemp | 0 | 0 |
| gettempdir | 0 | 0 |
| trailing slash | 0 | 0 |
| selftest / self-test | 0 | 0 |
| capabilit | 0 | 0 |
| SCORECARD | 0 | 0 |
| read-only file system / mount / EROFS | 0 | 0 |
| currency | 3 | 4 |
| scratch (case-sensitive, task keyword) | 8 | see §2 |

Same sweep over `SOURCES.append.md` for `pathname resolution|proc_pid_fd|gettempdir|tempfile|mkdtemp|TMPDIR|path_resolution|read-only file` -> 0 lines. C2's three round-33 mechanism sources (POSIX repeated slashes, proc_pid_fd(5), Python tempfile TMPDIR search) are not in the package; the lane opens them itself this round.

## 2. Per-hit verdicts

Every `scratch` hit is a probe recording where its own measurement ran (a bare clone, a synthetic repo), not guidance on how a committed tool picks its scratch root. Every `currency` hit is git-ref freshness, not capability-table currency.

| # | entry : line | hit | verdict | reason | located quote (<=25 words) |
|---|---|---|---|---|---|
| 1 | `fleet-prune-currency-r30.md`:25 | currency | REJECT | git remote-ref freshness of prunable worktree registrations; no SCORECARD or capability-row content; C1 needs rows re-run against named commands | "remote-side currency that round 9 could assert for all 26 can now be asserted for 24" |
| 2 | `fleet-prune-upstream-confirmed-r31.md`:31 | currency | REJECT | same: staleness of a local view of a remote, not tool-output drift | "the local view's currency was never load-bearing" |
| 3 | `fleet-live-exposure-r27.md`:45 | "concurrency" (substring false hit) | REJECT | not a currency hit; prose caveat about copies versus live repos | "the live repos have their own concurrency, reflogs and remotes" |
| 4 | `fleet-prune-durability-complete-r32.md`:3 | scratch | REJECT | a bare clone into the then-lane scratch; wrong domain for C2 (no TMPDIR/tempfile mechanism); a historical measurement of git 2.56.0 | "one bare clone per origin into this lane's scratch directory, and the clones deleted afterwards" |
| 5 | `fleet-prune-upstream-confirmed-r31.md`:3 | scratch | REJECT | same | "a bare clone into this lane's scratch directory for the ancestry test, and the clone deleted afterwards" |
| 6 | `prune-upstream-durability-r36.md`:20 | scratch | REJECT | same | "one bare clone of the origin into this lane's own scratch directory" |
| 7 | `prune-expiry-behaviour-r29.md`:3 | scratch | REJECT | scratch repo cleanup remark for a prune truth table; no root-selection content | "nothing fetched, and the scratch repository removed after the run" |
| 8 | `garbage-false-positive-modes-r25.md`:3 | scratch | REJECT | evidence of a hard-coded `/var/tmp` root — the pattern Q71 forbids; would be negative evidence, not a source for the repair | "scratch /var/tmp/souji-r25-matrix.XXXXXX, no residue" |
| 9 | `garbage-false-positive-modes-r26.md`:3 | scratch | REJECT | same hard-coded `/var/tmp` root | "scratch under /var/tmp, removed by the trap" |
| 10 | `quarantine-staging-no-copy-r24.md`:20 | scratch (`/fast/scratch`) | REJECT | RENAME_NOREPLACE availability per mount; quarantine staging, not scratch-root discipline | "`/dev/shm` (tmpfs), `/fast` (btrfs and xfs), `/fast/scratch` (xfs)" |
| 11 | `fleet-exposure-r24.md`:5 | /var/tmp copy of the fleet .git | REJECT | prune-exposure measurement; hard-coded root; no C2 mechanism | "btrfs-reflink copy of the fleet's .git under /var/tmp, no residue" |
| 12 | `repo-size-census-readonly.md`:62 | /var/tmp write-safety fixture | REJECT | an owed fixture for a size census (F2); names a hard-coded `/var/tmp` root, not a TMPDIR-derived one | "that is exactly what a `/var/tmp` write-safety fixture would have to establish and is still owed" |

No hit for the C1 words (capability, SCORECARD) or for selftest, tempfile, mkdtemp, TMPDIR or trailing slash. Package scope is git-reclamation/prune safety, near-duplicate literature, origin-record mechanics and community records. None touches capability-row currency or scratch-root discipline.

Other package-level facts (for the lesson's Assimilation line):
- 10 staged knowledge paths already exist in the lane's `corpus/knowledge/` at 2d9bca55: `duplicate-verdict-identity.md git-auto-maintenance-trigger-set-r23.md git-auto-maintenance-trigger-set.md origin-record-durability-r28.md origin-record-exclusivity-r28.md origin-record-mechanism-set-r33.md origin-record-writer-r27.md quarantine-origin-record-fields-r24.md quarantine-staging-no-copy-r23.md repo-size-census-readonly.md` (loop: `git cat-file -e 2d9bca55:corpus/knowledge/$f`; existing-paths=10).
- 2 dangling citations (S022 from the r23/r24 quarantine-origin-record-fields entries) are in MERGE-REPORT.md.

## 3. Id-collision check (round prompt §10, scratch run)

Pattern (0-3 leading spaces): `^ {0,3}\|[[:space:]]*S[0-9]{3,}`. Registry = `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 2d9bca55a9f042a2c9ed60a797a8069e74c41f46:corpus/SOURCES.md` (sha256 bfe894586d81b30bbb3097f133c2d6f74c748e93463089651ecbc3153fc88fe5); staged = `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md` (sha256 1510052ee7ca2b6fa3d6e2b89c397011865b07dec0fa1c8e097945cfa6b9f7d6). Scratch dir `/fast/scratch/hyaku/souji-r33/AssimSweep/A/`, exact §10 command lines (`grep -oE ... | grep -oE 'S[0-9]+' | sort`, `comm -12`).

```
wc -l reg-ids staged-ids collisions
  147 reg-ids
  134 staged-ids
   39 collisions
```
- reg-ids unique 147, range S001..S223 (76 ids of S001..S223 absent; the registry is not contiguous, max S223).
- staged-ids unique 134, range S109..S242; 95 staged ids do not collide.
- Column-zero-only control `grep -oE '^\|[[:space:]]*S[0-9]{3,}'` over the registry also counts 147; indented registry rows `^ {1,3}\|...S[0-9]{3,}` = 0, so the real registry has no indented rows and the 0-3 pattern and the old pattern agree on this input.

Collisions (39): `S109-S132` (24), `S152`, `S210-S223` (14).
Full reg-ids: S001-S132 (all 132 contiguous), S152, S210-S223.
Full staged-ids: S109-S242 (all 134 contiguous).

Compared with round 32 (`lane 146 ids, staged 134 ids, 38 collisions (S109-S132, S152, S210-S222)`, `corpus/lessons/round-32.md:49`): the registry gained S223 (+1 id, 146 -> 147), collisions 38 -> 39.

Guard proof (prompt §10: an indented registry row the staged set collides with must give a nonempty `collisions`). Fixture: the pinned registry with the `S002` row re-indented by 2 spaces (awk), staged fixture rows `| S002 | x |` and `| S109 | y |`:
- 0-3-space pattern -> collisions `S002 S109` (nonempty, S002 caught).
- column-zero-only pattern -> `S109` only (S002 missed: false green).
So the guard is not broken. No append performed.

Renumber map: not produced — no row is adopted (Assimilation: none), so nothing is appended and no id is re-pointed. If a later round adopts a row, ids continue from S224 and each citation is re-pointed by document, not arithmetic.

## 4. Suggested lesson line

`Assimilation: none adopted. 68 staged entries swept for TMPDIR, tempfile, mkdtemp, mktemp, scratch, trailing slash, capability, SCORECARD, currency, selftest; 12 hits (all scratch or currency in git-prune probes), all REJECT; the other keywords return 0. Id-collision guard run in scratch: reg 147 ids, staged 134 ids, 39 collisions (S109-S132, S152, S210-S223), no append.`
