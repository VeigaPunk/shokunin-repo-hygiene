# Souji round 31 w1 — sibling-overlap scan (SwarmConnector35)

Read-only scan of sibling-lane frontier surfaces for overlap with souji r31 axes
(C1 capability-cell calibration, C2 landing-gate/report discovery over committed
wave captures, C3 jj keep-ref object lifetime). souji-shokunin excluded;
nothing outside this report was written. No clones/fixtures were needed; no
scratch directory was created.

## Surfaces swept (all bytes opened this run)

- 19 sibling lanes' `PROVINCE.md` (19 files), `SKILL.md` (19), `corpus/README.md` (19),
  `corpus/knowledge/` (18 dirs, 872 `.md`; revenger-shokunin has no knowledge dir):
  audio, chousa, game-dev-2d, game-dev-3d, kagi, kaidoku, kake, kama, kasegi,
  kengaku, kotoba, kotodama, kumitate, lore, mado, mori, revenger, tabi, tameshi,
  tsukuroi.
- `/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh` (38.1K).
- Terms per class: `reflog`, `expire-unreachable`, `refs/jj/keep`, `util gc`,
  `capture`, `capability` — case-sensitive pass plus a case-insensitive pass for
  the pruning-class terms.

Method note: the harness grep tool silently returns no matches for glob-form
paths (`*/SKILL.md` etc.) — validated with a control pattern (`git` over
`*/SKILL.md` → 0 hits while the same pattern on an explicit path matches). All
sweeps below were re-run with explicit per-file/per-dir paths; counts carry
their commands in the report Evidence section.

## Class 1 — git reflog expiry / object pruning / jj keep refs

Hits (each: lane, file:line, characterization):

1. kasegi-shokunin `corpus/knowledge/repo-git-state.md:16` — lost-tree forensics;
   quote: "all Sep 7–15 fleet work (b1k overnight, bh* audits, ingestion cycles, bpolish) is working-tree-only" (`git reflog` cited as the forensic read). Does not claim pruning ground.
2. kasegi-shokunin `corpus/knowledge/source-tree-loss-2026-09-28.md:252` — mirror
   forensics; quote: "reflog holds only the two commits (no clone/fetch entry); 0 packs, 48 loose". Forensic observation only.
3. kotodama-shokunin `corpus/knowledge/verification/append-only-record-verification.md:59` — append-only-record detector; quote: "file the mismatch as a finding with whatever history is available (git log, reflog)". Reflog as a history source, not a pruning claim.
4. kumitate-shokunin `corpus/knowledge/jj-workspace-seat-containment.md:102` — **closest
   neighbor to souji C3**: "abandoned commits still remain in the repository's object store and op log"; "only `jj op abandon` + `jj util gc` or a separate clone excludes them from storage". Names the jj removal mechanism, but the entry's question is workspace-seat containment: no keep-ref coverage (nothing on what keeps an object present after its own keep ref is dropped — descendant keep refs, reflog entries), no jj 0.45.1/git 2.56.0 scratch measurement. Adjacent mechanism mention, **not contested ground**; souji C3 sources its claims from registry rows opened this round per its frozen contract, not from this entry.
5. mado-shokunin `corpus/knowledge/tripwire-precision-r20.md:70` — write-tripwire
   classification; quotes: "the working copy is snapshotted before the dry-run return"; "measured: +1 op, `refs/jj/keep`" (for `jj git push --dry-run`). A measured keep-ref side effect; different question (command write-classification vs object lifetime after ref removal). Not contested.
6. mado-shokunin `corpus/knowledge/province-accuracy-selfaudit.md:119` — install-checkout
   audit; quote: "No tracked-content, refs, reflog (`logs/` untouched), or `FETCH_HEAD` change anywhere in the checkout". Reflog-as-untouched-evidence vocabulary.
7. kaidoku-shokunin `SKILL.md:448` — citation-drift gate; quote: "reflog selectors, ORIG_HEAD/FETCH_HEAD and other pseudo-refs) exits 2 before resolution". Reflog selectors are named only to be refused as mutable revisions. Not contested.

Empty sweeps: `expire-unreachable` — 0 hits on any surface. `refs/jj/keep` — the
mado row above is the only hit. `util gc` — the kumitate row above is the only hit.

## scripts/hyaku/jj-lane.sh — destructive-command question

**jj-lane.sh never runs `git reflog expire`, `git gc`, or `jj util gc`** (nor any
gc/expire/prune/fsck/repack command). Empty sweep, two ways:

- harness grep (case-insensitive) `reflog|gc|expire|prune|util` over the file → 0 matches;
- shell grep -nE `git (reflog|gc|prune|fsck|repack|pack-refs)|jj util gc|expire` → exit 1.

What it does run (inventory from bytes opened this run): `jj git init --colocate` (:431),
`jj git fetch --remote origin` (:286), `jj git push --remote origin --bookmark` (:357),
`jj bookmark track/list`, `jj file track/untrack`, `jj config get/list`, `jj status`,
`jj diff --summary`, `jj new`, `jj commit`, `jj log`; plus read-only git plumbing
(`symbolic-ref` :119, `show-ref`, `rev-parse` :172-173, `rev-list --count` :410,
`cat-file -e` :467, `status`, `diff --cached`). Its only refs/jj/ mention is a
branch-detection guard, :117: "Prefer an attached HEAD's branch (never anything
under refs/jj/), else origin/HEAD." — not a keep-ref claim.

## Class 2 — landing gates / report discovery over committed wave captures / pointer tokenizers

No sibling surface claims this ground. `capture`/`capability` hits in PROVINCE /
SKILL / corpus-README are domain vocabulary, per lane:

- game-dev-3d `PROVINCE.md:62`, `corpus/README.md:163` — Godot/Blender render capture, visual regression.
- kaidoku `PROVINCE.md:53,200-201,284-297`, `SKILL.md:61,685`, `corpus/README.md:36-37,73,121,135,153,179,231` — REA packet-capture / scenario-capture verbs and saved-capture envelopes.
- kake `PROVINCE.md:67`, `SKILL.md:647-650` — live GET capture / sanitized capture representations of web properties.
- kama `SKILL.md:227-243,307-308,448-463` — llama-serving capture snapshots/replays (registry/history).
- kasegi `SKILL.md:60-144`, `PROVINCE.md:64-72` — bounty scope-snapshot captures (`source-snapshots/round-31/S048.txt`).
- kengaku `PROVINCE.md:14,234-309` — captured TB2 grader functions replayed in sandboxes.
- tabi `PROVINCE.md:9-13` — CDP evidence-capture discipline. tsukuroi `PROVINCE.md:46-58` — adjacency-packet "Capture time" fields. kotoba `PROVINCE.md:64-68`, mado `PROVINCE.md:30-31`, mori `PROVINCE.md:24-36`, kagi `corpus/README.md:146-228`, kake `corpus/README.md:172-338`, lore/kotodama/tameshi/audio — capability-as-vocabulary rows; chousa corpus-README — web-archive "capture" of cited source pages plus its gate's hermetic `--pin` capture.

Adjacent instrument class, same broad family as C2 but scoped to each lane's own
corpus (none scans a committed `.ufo/waves/round-N/` ∪ `census/round-N/waves/`
report union or pointer tokenizers):

- chousa-shokunin `SKILL.md:87` — `research-gate --pin/--drift`: hermetic capture of its own gate invocation, normalized baseline, byte-compare drift.
- kagi-shokunin `PROVINCE.md:55` — `corpus/sources-census.sh`: quote: "Checks the citation chain and declared capture/classification records" over its own `corpus/SOURCES.md`.
- kaidoku-shokunin `SKILL.md:448` — citation-drift pointer-table gate (pointer pins, not report discovery).

## Class 3 — capability-table count agreement

One same-class instrument, scoped to its own lane:

- kagi-shokunin `SKILL.md:47` — `corpus/self-counts.py` + `corpus/self-counts.tsv`;
  quote: "locates ONE current-tense number in SKILL.md / PROVINCE.md / `corpus/README.md` / a reviewed `corpus/knowledge/*.md` line" and binds each to a rows/ledger/pin observable. Same instrument class as souji C1 (stated count ↔ observable binding), but over kagi's bookkeeping files; souji's SCORECARD capability cells are untouched. Adjacent, not contested.

## Verdict

Zero contested scope across all three classes. No sibling claims souji r31 ground;
nothing to absorb. Two mechanism-adjacent notes for the C3 builder (kumitate
`jj-workspace-seat-containment.md:102` util-gc sentence; mado
`tripwire-precision-r20.md:70` keep-ref measurement) are consistent with, but not
substitutes for, C3's required registry-sourced measurement in scratch.
