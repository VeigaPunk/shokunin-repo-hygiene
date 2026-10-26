# SwarmCritic22 — souji r30 w2: registry changes at 76c94eb4 (C3, F1 keep-ref expiry)

## Status

STATUS: PASS — the attack ran end-to-end; all four registry rows hold their contract obligations, and two registry-hygiene defects are located (search log absent; round lesson Gate/log not committed), neither fatal to C3's counter.

## Evidence

Target: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 76c94eb41fc38093d7143a016006b6275e102d5d:corpus/SOURCES.md` (base 9420341d, lane tip 9dcd367; SOURCES.md unchanged after C3 — `git -C lane diff --stat 76c94eb4 9dcd367 -- corpus/SOURCES.md` is empty). Receipts: `.ufo/waves/round-30/w2/SwarmCritic22-receipts.txt` (§R0–R13), `SwarmCritic22-val-base.txt`, `SwarmCritic22-val-c3.txt`, `SwarmCritic22-val-live-root.txt`.

- Diff: 4 insertions, 2 deletions. S054 and S063 change **only** the `used-by` cell (cell-level compare, receipts R2); S220/S221 are new rows at lines 165-166 after S219.
- Schema: 145 registry rows, every row 11 cells, 0 rows with `NF!=13`; no pipes inside cells; ids unique; S220/S221 are the next unused after S219.
- Anchors, opened in the committed snapshots: `census/round-30/sources/cli-reference@.md.snap` 4038 lines, §`jj operation abandon` at :2411, :2415, §`jj util gc` at :3789, :3793, :3801, :3803; `census/round-30/sources/operation-log.md` 65 lines, §Introduction :3, :47-56 §"Loading an old version of the repo", `grep -c abandon` = 0. All four `SHA256SUMS` entries reproduce from the C3 blobs.
- Independent refetch this run: `cli-reference@.md.snap` sha256 `b330694348c2a6fb21b637425c711d48ac9fa41d0b3596b4ca2955f7a9333554` / 154561 bytes; `operation-log.md` sha256 `2a48dab85483f8bed666ccc1aebd458d70f4ff57ece1a122aee8889b3209ce18` / 65 lines — both equal the receipts and `SHA256SUMS`.
- Served-page clause: `https://docs.jj-vcs.dev/v0.45.1/cli-reference/` fetched (390031 bytes) contains "jj util gc" (9 lines) and "only obsolete objects and operations older than 2 weeks" (1 line), "jj file delete" (0), "jj util diff" (0) — the row's negative pin holds.
- Host binary `jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5`: `jj util gc --help` and `jj op abandon --help` reproduce every taught sentence; in a scratch colocated repo `--expire=tomorrow` and `--expire=2026-01-01` both exit 1 with `Error: --expire only accepts 'now'`, `--expire=now` exits 0.
- Validator: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → `souji ok …/corpus/SOURCES.md`, rc 0, 36 W04 (same-URL-across-scopes) notices, no E-code. Run again on a scratch clone at BASE and at C3: byte-identical 37-line output, so C3 adds no finding and removes none.
- Frozen census on the live registry: rows=145, malformed=0, duplicate ids none, enum/tier-inflation none, mined `used-by` paths all exist.

Source quotes (each ≤25 words, from bytes opened this run):
- CORPUS.md, contract rule 1: "The round lesson's `## Gate` records, for every new row, the URL, the access date, and a ≤25-word quote".
- CORPUS.md, contract rule 5: "**Search log.** PRISMA-inspired, not PRISMA-compliant: question/query, where searched, date, identified / screened / included / excluded counts".
- CORPUS.md, rule 2: "Only `status`, `recheck` and `used-by` change in place, and each change is logged old→new in the round lesson."
- S054 scope: "creation and removal of `refs/jj/keep/*` in jj 0.45.1 (tag commit 7c41cdeb = host binary); not later releases".
- S051 scope: "`refs/jj/` GC refs, hooks, attributes, git gc; not keep-ref lifetime".
- `corpus/knowledge/jj-colocation-receipts.md:108`: "Keep-ref lifetime. The docs read do not state it."
- `cli-reference@.md.snap:3803`: "Only the string "now" can be passed to this parameter."
- `cli-reference@.md.snap:3801`: "By default, only obsolete objects and operations older than 2 weeks are pruned."

## Findings

1. **`corpus/SOURCES.md` `## Search log` has no Round-30 note** (C3 blob lines 182-240; `grep -c Round-30` = 0 at C3 and at tip). Contract rule 5 needs one prose note per bounded search; C3 opened four sources (2 admitted as rows, 2 mapped to held rows, 5 staged entries rejected). The r29 precedent landed its note in the same rows commit (1dc6785). Impact: the round's screening record lives only in a wave delivery, not in the registry. Fix: append a `**Round-30 F1 keep-ref source search (2026-10-26)**` note with identified/screened/included/excluded counts and stop rationale. Append-only, touches no target. Severity: DEFECT-NOT-FATAL.
2. **No committed round lesson means rules 1-2 logging is unbacked at the landing commit — and still unbacked at the lane tip.** `corpus/lessons/round-30.md` is absent from both 76c94eb4 and 9dcd367 (`git ls-tree` → 0 files); the Gate for S220/S221 and the old→new `used-by` table exist only in committed `census/round-30/waves/w1/deliver-lesson-gate.md` and in an untracked 38-line working-tree draft (another seat's, R9). Precedent (r29 lesson in de874ee) shows the lesson lands late, so this is *owed at round close*, not a C3 mislanding; if the round closes without it, S220/S221 have no contract-required Gate and the S054/S063 edits violate rule 2. Severity: DEFECT-NOT-FATAL with a close-time condition.
3. **Scope overlap S220/S054 is declared on one side only.** S054's scope claims the whole "creation and removal" topic with no docs carve-out; S220 excludes only "the keep-ref code path (S054)". Both `teaches` cells assert the same "2 weeks" default, so those two rows are not independent corroboration for that number. Append-only forbids editing S054's scope; the entry does not double-count (it attributes the default to S220 alone at its step 3), and the URLs differ so W04 cannot fire. Severity: DEFECT-NOT-FATAL (curation note for the round lesson).
4. **Entry Gate under-grounds the row's strongest clause** (routed; registry rows unaffected): `corpus/knowledge/jj-keep-ref-expiry.md` quotes `--expire` as the fragment "can be passed to this parameter." and drops "Only the string "now"", which is the fact S220's scope and teaches assert; its S221 bullet cites "lines 5-8" for a clause at line 9. Both facts hold from :3803 and :9, which I opened. Fix in the entry, not the row.
5. **Stale cross-entry premise:** `corpus/knowledge/jj-colocation-receipts.md:108` still reads "The docs read do not state it. The timing in §3 is an inference", and a grep of that file at tip finds no reference to `jj-keep-ref-expiry.md`, while the new entry claims "its Limits first bullet is the gap closed here". Two entries now speak about keep-ref lifetime with no forward pointer. Smallest safe correction: append one pointer sentence to that Limits bullet; do not rewrite the r17 claim. Severity: DEFECT-NOT-FATAL (coverage/stale-premise risk).
6. **Provenance observation, no claim harm:** the snapshot's abandon usage line is `jj operation abandon <OPERATION>` (:2421) while the host binary prints `jj operation abandon [OPTIONS] <OPERATION>`; all three taught facts are byte-equal in both. The row anchors the repo artifact and says so, so tier A and the taught scope are unaffected.

## Attack log

| attacked item | attack | verdict |
|---|---|---|
| schema / 11 columns | parse every `S` row at C3; count cells; frozen awk census | HOLDS — 145 rows, 0 malformed, no pipes, ids unique, S220/S221 = next unused |
| S220 tier A | contract tier text + tier-rules L1/L2/L9/L10 lowering cases | HOLDS — official repo artifact at tag v0.45.1 with commit 7c41cdeb, sha256 and HTTP receipt; revision pinned; URL resolves |
| S221 tier A | same | HOLDS — official jj `docs/` at tag v0.45.1, pinned revision, URL resolves |
| S220 anchor + revision | line-by-line against committed snapshot and against the host binary's own help | HOLDS — tag+commit at :2411/:2415/:3789/:3793/:3801/:3803 all exact; taught sentences identical on jj 0.45.1 |
| S221 anchor + revision | line-by-line; `grep -c abandon`; line count | HOLDS — :5-12 and :47-56 exact, 65 lines, abandon absent as claimed |
| `opened` / `recheck` | compare with fetch receipts, refetch this run, allowed cadence list | HOLDS — opened 2026-10-26 matches receipts and refetch; `on-release` is an allowed cadence |
| append-only on S054/S063 | cell-by-cell BASE vs C3 compare | HOLDS — only `used-by` differs; mined paths exist; validator E11 clean |
| scope overlap with S051 | read S051's scope | HOLDS — S051 explicitly excludes keep-ref lifetime and S220 claims nothing about colocation |
| scope overlap with S054 (duplicate evidence) | compare scope and teaches cells | DEFECT-NOT-FATAL — removal topic overlaps; carve-out stated only on S220's side; "2 weeks" is one fact in two rows (finding 3) |
| `validate --root ... souji` | live-root run, plus BASE-vs-C3 scratch runs | HOLDS — rc 0, `ok`, 36 pre-existing W04, output byte-identical before/after, no S220/S221 warning |
| false provenance in row claims | live refetch of both sources; served-page probes; host-binary help; `--expire` execution | HOLDS — hashes match; served page pins hold; only `now` accepted (rc 1 for tomorrow and an absolute date) |
| search-log completeness (rule 5) | grep Round-30 in C3 and tip blobs; compare r29 landing | DEFECT-NOT-FATAL — no Round-30 note anywhere in the registry |
| lesson Gate and old→new log (rules 1-2) | ls-tree at C3 and tip; git status; r29 precedent | DEFECT-NOT-FATAL — content exists only in a wave delivery and an uncommitted draft; must land before close |
| C3's own after-measurement | not re-run (not my seat; C3 counter is another reviewer's target) | no verdict claimed |

Row verdicts: **S220 HOLDS**, **S221 HOLDS**, **S054 HOLDS**, **S063 HOLDS**. No frozen predicate, target or counter was changed or proposed.

## Deliveries

- `.ufo/waves/round-30/w2/SwarmCritic22.md` (this report)
- `.ufo/waves/round-30/w2/SwarmCritic22-receipts.txt` (R0–R13, all cited commands and outputs)
- `.ufo/waves/round-30/w2/SwarmCritic22-val-base.txt`, `SwarmCritic22-val-c3.txt`, `SwarmCritic22-val-live-root.txt` (validator evidence)
- Scratch `/fast/scratch/hyaku/souji-r30/SwarmCritic22/` removed after the copies; no writes outside this directory and the designated report path, no lane git/jj mutation, no pacman, no installs (host `jj 0.45.1-7c41cdeb…`, `git 2.56.0`, `python3 -B`, `curl`, `gawk`).
