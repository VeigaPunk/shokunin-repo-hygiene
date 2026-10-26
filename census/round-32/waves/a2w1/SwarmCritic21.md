# SwarmCritic21 — attack on the landed C3 fixture (r32 a2w1)

## Status
STATUS: PARTIAL — the fixture's record reproduces byte-identically and three of my four design
doubts hold, but a one-variable rerun falsifies the C3 entry's causal claim (and its description of
arm `old`): backdate exactly what the entry says arm `old` backdates ("B's own commit, tree and blob
files") and B **survives** in a cruft pack. The drop needs the whole unreachable island — including
the jj-created working-copy commit that descends from B — to be old. The measurement is sound; the
claim scope is wrong and is fixable in prose.

## Evidence

Lane tip at review: `4e56c48b8fc828f9aba2746e324dc46aa538bdbf`; C3 landed at `a92e1aae91dbf46c2d7eff713932cfc820186970`.
Fixture/entry/record blobs are identical at `a92e1aa` and at tip (`git rev-parse` triples printed
`cd62dbc3…`, `cb7e3634…`, `6de8f4b8…`), so the line anchors below address the tip too.

1. **Record reproduces.** `TMPDIR=/fast/scratch/hyaku/souji-r32/AttackC3Fixture/tmp bash
   /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r32-jj-mtime-clock.sh` → exit 0;
   `sha256sum run1.txt` = `01cf6dc0011ae8f22d16922846b6834641df5dbce6e3a26cd0c267ede97e8254`; all 22
   `RESULT` lines `diff`-identical to `census/round-32/records/jj-mtime-clock-run.txt`.

2. **What git reads as a loose object's age** (git v2.56.0, tag commit `a018953`, shallow clone of
   `https://github.com/git/git.git`): loose prune `if (st.st_mtime > expire)` (builtin/prune.c:98);
   loose mtime reported to cruft enumeration `*oi->mtimep = st.st_mtime;` (odb/source-loose.c:155);
   loose objects added to a cruft pack with `st.st_mtime` (builtin/pack-objects.c:4556-4561
   `add_loose_object`). Sweep for a ctime path: `grep -c st_ctime` over builtin/prune.c,
   odb/source-loose.c, builtin/pack-objects.c, reachable.c, packfile.c, pack-mtimes.c,
   builtin/repack.c, repack-cruft.c, odb/source-files.c = 0. So `touch -d` on the loose file is
   exactly the clock git consults.

3. **Old arm, one variable changed** (fixture functions 1-236 sourced into scratch; same
   `arm_begin/make_A/make_B/abandon_wc/seal`, then one gc):

   | backdated set | B after plain `git gc` |
   |---|---|
   | `backdate_commit "$ID_B"` = B's commit, tree, blob (entry's description of arm old) | `present=yes where=cruft` (`CASE c_all sel=all`) |
   | `backdate_island "$ID_B"` = B **plus the empty-subject WC commit whose parent is B** (fixture line 255) | `present=no where=absent` (`exp5`) |
   | island commit objects only | `present=no where=absent` (`i_commit_only`) |
   | island trees/blobs only, commits recent | `present=yes where=cruft` (`i_treeblob_only`) |
   | recent-island member old, B recent | `present=yes where=cruft` (`i_descendant_only`) |
   | B old, recent island member's commit object deleted | `present=no where=absent` (`i_b_only_drop_desc`) |

   Island membership was printed each run; e.g. `island(B): 689a80fb… subject= (parent 6bcdf593…),
   6bcdf593… subject=B`, and after `backdate_island` both commit files show `2026-09-26` while now is
   `2026-10-26`.

4. **Consequence of a recent island member** (`exp6`: `backdate_commit "$ID_B"` only). After `git gc`
   the cruft pack's `.mtimes` records B at `age=14.000 days`, **not** its touched 30 days
   (`B index_pos=1 mtime=1791810404 age=14.000 days`; C in the `mixed` control, exp2, keeps its real
   clock: `B=… mtime=1790427826 => 2592000 s ago`, `C=… => 0 s ago`). A second identical `git gc`
   leaves B `present=yes where=cruft`: a recent unreachable descendant re-seeds B each cycle and
   pack-objects stamps traversed ancestors with the gc expiry date
   (builtin/pack-objects.c:4215-4221, traversal at :4294 and :4315; recent test `if (mtime >
   data->timestamp)` reachable.c:186).

5. **`where=cruft` agrees with git's own classifier.** git marks a pack cruft by the `.mtimes`
   sibling (`p->is_cruft = 1;` packfile.c:754) and reads per-object mtimes from it
   (packfile.c:1375). Control (`exp4`): B packed alone into a plain pack → `where=pack`; adding an
   empty `.mtimes` sibling → `where=cruft`. The else-branch is live and the `cruft` label cannot be
   produced by a plain pack.

6. **jj does not re-reference B.** After `seal`, B is `reachable: no`; `jj log --no-graph -r all()`
   and `jj st` leave the six `refs/jj/keep/*` refs and B's reachability unchanged (identical ref
   listing, `reachable: no` after each). `jj op log` names the abandoned commit
   (`abandon commit 7c79fcfb…`) but git's roots are refs, reflogs and the index (git-gc.adoc:141-146,
   cited in the held entry), not jj's op store, and no keep ref for B or a descendant is
   recreated by a read.

## Findings

1. **The C3 entry's law is false as written, and its description of arm `old` omits what the fixture
   actually backdates.** Location: `corpus/knowledge/jj-abandoned-object-mtime-clock.md:22-23`
   ("an unreachable object whose mtime is inside the window survives … and one whose mtime is outside
   it does not") and `:26` ("backdates B's own commit, tree and blob files"). The fixture calls
   `backdate_island "$ID_B"` (tests/fixtures/r32-jj-mtime-clock.sh:255), which walks
   `island_commits` (:214-220) — every commit with B as ancestor, including the pre-abandon
   working-copy commit jj leaves parented on B — and touches each (:231-236). With only B's own three
   objects backdated, B stays in a cruft pack (Evidence 3, row 1). So the record's `old`/`mixed`/
   `never`/`nocruft` drops are attributable to the **island's** clock, not to B's own; the entry's
   stated converse has a live counterexample inside its own fixture's construction family (jj
   0.45.1 left that descendant in each of the twelve arms I built). The fixture's own comment
   already says this — "the old arm
   backdates the whole island" (tests/fixtures/r32-jj-mtime-clock.sh:213) — so code and prose
   disagree. Smallest safe correction: (a) rewrite :26 to name
   `island_commits`/`backdate_island` as the backdated set; (b) qualify :22-23 — an object whose mtime
   is outside the window is dropped only when no unreachable descendant is inside it, and that
   descendant's recency also re-stamps the ancestor's cruft mtime (Evidence 4). Both are
   stricter-only prose edits, logged like the r31 defect-2 corrections; no contract, counter, item or
   target changes, so `legs=14 fail=0 f1_entries=5` is unaffected. Impacted axis: coverage (the
   entry is the coverage artifact); calibration and operability untouched.

2. **"The clock is the object's own mtime" needs one exception stated; the record itself is not
   affected.** Location: entry `:19` and the held entry it defers to
   (`corpus/knowledge/jj-dropped-keep-object-lifetime.md:49-50`, "for as long as its own mtime is").
   The entry's law duplicates held-entry claim 4 while adding a converse the held entry never made;
   the duplicate should point at the held rule instead of restating it. Measured exception: objects
   reached only from a recent unreachable island member are packed with `cruft_expiration` as their
   mtime (builtin/pack-objects.c:4215-4221), so their own 30-day clock is lost — `14.000 days` in
   Evidence 4. None of the five landed arms enters that path (arm `old` excludes the island whole;
   `never`/`mixed` run `--prune=never`, which reaches repack as `--cruft-expiration=never`,
   odb/source-files.c:493, and preserves real stat mtimes — Evidence 4's mixed control), so the
   record's 22 lines and every `mtime=` label stand.

## Attack log

- **Doubt 1 — does `touch -d` set the age git compares?** Confirmed. Loose prune and cruft
  enumeration both use the loose file's `st_mtime` (builtin/prune.c:98, odb/source-loose.c:155,
  builtin/pack-objects.c:4561); `touch` succeeded in every arm (a non-loose file dies at fixture
  :227). No ctime/pack-mtime substitution: non-cruft packs use `p->mtime` (packfile.c:1377), which
  the fixture never relies on.
- **Doubt 2 — is `where=cruft` correctly derived?** Confirmed. git's `is_cruft` is exactly "a
  `.mtimes` sibling exists" (packfile.c:752-754); the fixture's `where` (fixture :107-120) uses the
  same rule, and the `pack` branch is reachable (exp4). One cosmetic asymmetry: the loop returns
  `cruft` in preference to `pack` if an object were in both, which cannot occur in these arms.
- **Doubt 3 — could jj's op log or index re-reference B?** No, measured (Evidence 6). The op log
  names B, but git consults only refs/reflogs and jj does not re-add a keep ref for an abandoned
  commit on a read; `seal`'s `rev-list --all --reflog` sweep is sound for this state.
- **Doubt 4 — is the old-object deletion attributable to the clock and not to a shared backdated
  tree/blob?** Partly, and this is the finding: it is attributable to the clock, but to the **island's**
  clock, not B's alone. Shared trees/blobs are not a confound (B's tree is still reachable — it is
  listed by `rev-list --objects --all`, count 1 — and `i_treeblob_only` keeps B while
  `i_commit_only` drops it), the recent-island
  descendant is the confound, and a second gc under that descendant never drops B (Evidence 4).

## Deliveries

- `.ufo/waves/round-32/a2w1/SwarmCritic21.md` (this report). No other lane file written; scratch
  `/fast/scratch/hyaku/souji-r32/AttackC3Fixture/` removed after the run. No tool installed or
  upgraded.
