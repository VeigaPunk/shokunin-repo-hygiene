# SwarmConnector35 — sibling-overlap scan, souji round 31 w1

## Status

STATUS: PASS — all four surface classes swept read-only over 19 sibling lanes
plus `scripts/hyaku/jj-lane.sh`; pruning-class hits enumerated with locations;
jj-lane.sh destructive-command question answered with an empty sweep (it never
runs `git reflog expire` / `git gc` / `jj util gc`); no sibling claims ground
souji would take, so nothing to absorb and no axis harmed.

## Evidence

Surface inventory (this run):
`for d in /home/vgpnk/Projects/shokunin/*-shokunin; do ...` → 19 sibling lanes;
19× PROVINCE.md, 19× SKILL.md, 19× corpus/README.md, 18× corpus/knowledge/
(872 `.md`; revenger-shokunin has none). Terms: `reflog|expire-unreachable|refs/jj/keep|util gc|capture|capability`.

Case-sensitive + case-insensitive sweeps (harness grep tool, explicit paths;
glob-form paths were validated broken via a control pattern and re-run explicitly):

- PROVINCE/SKILL/README: hits only for `capture`/`capability` domain vocabulary
  plus the two instrument-class rows named in Findings 6-8; pruning-class hits
  limited to Findings 1-5,7.
- Knowledge dirs, pruning terms: `util gc|expire-unreachable` → 1 file
  (kumitate `jj-workspace-seat-containment.md:102`); exact-case
  `refs/jj/keep|capture|capability` → `refs/jj/keep` hit only at mado
  `tripwire-precision-r20.md:70` (other captures are domain vocabulary).
- jj-lane.sh: grep `reflog|gc|expire|prune|util` (case-insensitive) → 0 matches;
  `grep -nE 'git (reflog|gc|prune|fsck|repack|pack-refs)|jj util gc|expire'
  scripts/hyaku/jj-lane.sh` → exit 1 (empty sweep).
- jj-lane.sh command inventory from bytes opened this run: `jj git init
  --colocate` (:431), `jj git fetch` (:286), `jj git push` (:357), `jj bookmark
  track/list`, `jj file track/untrack`, `jj config get/list`, `jj status`,
  `jj diff --summary`, `jj new`, `jj commit`, `jj log`; read-only git plumbing
  (`symbolic-ref` :119, `show-ref`, `rev-parse` :172-173, `rev-list --count`
  :410, `cat-file -e` :467, `status`, `diff --cached`).

Lane tip observed during scan: fleet scan only; sibling tips as of 2026-10-26
(~03:3x-03:4x local). No lane repo was mutated; no git/jj commands run against
any sibling or the lane.

## Findings

1. kasegi-shokunin `corpus/knowledge/repo-git-state.md:16` — `git reflog` used as
   a forensic read on a lost working tree; quote: "all Sep 7–15 fleet work (b1k
   overnight, bh* audits, ingestion cycles, bpolish) is working-tree-only". No
   pruning claim; not contested.
2. kasegi-shokunin `corpus/knowledge/source-tree-loss-2026-09-28.md:252` — mirror
   forensics; quote: "reflog holds only the two commits (no clone/fetch entry);
   0 packs, 48 loose". Not contested.
3. kotodama-shokunin `corpus/knowledge/verification/append-only-record-verification.md:59`
   — record-edit detector names history sources; quote: "file the mismatch as a
   finding with whatever history is available (git log, reflog)". Not contested.
4. kumitate-shokunin `corpus/knowledge/jj-workspace-seat-containment.md:102` —
   closest neighbor to souji C3; quotes: "abandoned commits still remain in the
   repository's object store and op log"; "only `jj op abandon` + `jj util gc`
   or a separate clone excludes them from storage". Names the jj removal
   mechanism but covers no keep refs, no post-drop lifetime, no jj 0.45.1/git
   2.56.0 measurement. Adjacent mention; not contested ground.
5. mado-shokunin `corpus/knowledge/tripwire-precision-r20.md:70` — measured
   keep-ref side effect; quotes: "the working copy is snapshotted before the
   dry-run return"; "measured: +1 op, `refs/jj/keep`". Command write-classification,
   not object lifetime. Not contested.
6. mado-shokunin `corpus/knowledge/province-accuracy-selfaudit.md:119` and
   kaidoku-shokunin `SKILL.md:448` — reflog-as-vocabulary only; quotes: "No
   tracked-content, refs, reflog (`logs/` untouched), or `FETCH_HEAD` change
   anywhere in the checkout"; "reflog selectors, ORIG_HEAD/FETCH_HEAD and other
   pseudo-refs) exits 2 before resolution". Not contested.
7. scripts/hyaku/jj-lane.sh — never runs `git reflog expire`, `git gc`, or
   `jj util gc`: both sweeps empty. Only refs/jj/ touch is the branch-detection
   guard at :117: "Prefer an attached HEAD's branch (never anything under
   refs/jj/), else origin/HEAD." The file's own summary (:2):
   "jj-lane.sh — lane-repo VCS writes through Jujutsu (jj) in colocated mode."
   matches the observed inventory (fetch/push/init/bookmark/file/config/commit only).
8. Class 2/3 adjacent instruments, none over wave-report unions or souji's
   SCORECARD cells: chousa `SKILL.md:87` (`research-gate --pin/--drift`, hermetic
   self-capture baseline); kagi `PROVINCE.md:55` (`sources-census.sh` — quote:
   "Checks the citation chain and declared capture/classification records");
   kagi `SKILL.md:47` (`self-counts.py` — quote: "locates ONE current-tense
   number in SKILL.md / PROVINCE.md / `corpus/README.md` / a reviewed
   `corpus/knowledge/*.md` line", bound to rows/ledger/pin observables). Same
   instrument class as C1 but scoped to kagi's own bookkeeping. All `capture`/
   `capability` remaining hits across PROVINCE/SKILL/corpus-README/knowledge are
   domain vocabulary (render/packet/serving/bounty/grader/web-archive capture;
   capability-as-noun rows), enumerated by lane in the delivery file.

Verdict of the scan: zero contested scope; souji's C1/C2/C3 ground is unclaimed
on any swept sibling surface.

## Attack log

Not an attack item; no counter, predicate, target, or case-set dispute. One
method observation reported for the record: the harness grep tool returns zero
matches for glob-form multi-lane paths (validated with a control pattern); all
sweeps were re-run with explicit paths before any claim was made.

## Deliveries

- `.ufo/waves/round-31/w1/deliver-sibling-overlap.md` — full scan deliverable
  (surface inventory, per-hit lane/file:line, quotes, empty sweeps, verdict).

No scratch directory was created (read-only scan; no clones, fixtures, or
downloads), so there is nothing to remove under
/fast/scratch/hyaku/souji-r31/SwarmConnector35. No tools were installed or
upgraded this seat.
