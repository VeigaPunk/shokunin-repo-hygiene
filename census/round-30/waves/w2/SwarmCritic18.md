# SwarmCritic18 — r30 w2 — C3 coverage credit (attack)

## Status

STATUS: PASS — the attack ran: every proposition in `corpus/knowledge/jj-keep-ref-expiry.md` was
classified NEW/HELD against the base tree, and the coverage-vs-quality call is answered. Verdict:
coverage **HOLDS narrowly** (the measured run is a new evidence class and is what the frontier
predicate names), with two sentences inside the entry that committed bytes refute — both invisible
to C3's four legs.

## Evidence

- Lane clone (scratch, origin dropped) tip `9dcd367655fc28ba73d679a0e2cadaff96d2bcb8`, base
  `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`. Read-only; no lane write outside this report and
  `SwarmCritic18-receipts.txt`. Scratch `/fast/scratch/hyaku/souji-r30/SwarmCritic18/` removed.
- Cited bytes copied to `.ufo/waves/round-30/w2/SwarmCritic18-receipts.txt` (199 lines, sha256
  `c2f8fe450c8cb0da536e7629de2ccfab4f809525713ee4e17dbbb4a31ee4d0bd`).
- Tooling: nothing installed or upgraded (no pacman, no uv, no npm); no pacman transaction attempted.
- Held text at base `9420341`: `git show 9420341:corpus/SOURCES.md` line 75 (row S054) and
  `corpus/knowledge/jj-colocation-receipts.md` lines 12, 30, 31, 86, 108, 122.
  S054 row, teaches cell: "only `jj util gc` removes non-head keep refs older than its threshold
  (default 2 weeks)". Scope cell: "creation and removal of `refs/jj/keep/*` in jj 0.45.1".
  `jj-colocation-receipts.md:30`: "Keep refs for current heads are kept. Other keep refs are deleted
  when their loose-ref file is older than the threshold." Same line: "`jj util gc` uses a 14-day
  threshold by default". `:31`: "a commit hidden by a rewrite keeps its keep ref until its operation
  is abandoned". `:86`: "jj's `util gc` runs `git gc --prune=@<keep_newer>`" and "the two prune
  clocks are linked". `:12`: "Commits created by `jj` have a ref starting with `refs/jj/` to prevent
  GC." `:108` (Limits): "Keep-ref lifetime. The docs read do not state it." and "The timing in §3 is
  an inference from source and from observed keep-ref counts."
- Base-tree absence checks (`git grep` at `9420341`, scope `corpus/knowledge` + `corpus/README.md`):
  no hit for `only accepts`; no keep-ref hit for `packed`; no hit for `operation log`.
- Measured record `census/round-30/records/jj-keep-expiry-run.txt:6`
  `RESULT step=4-util-gc-expire-now keep_refs=6 object_present=yes note=target_keep=no cmd=jj-util-gc-expire-now`;
  `:7` `RESULT step=5-op-abandon-util-gc-expire-now keep_refs=2 ... op_range=..@- ops_naming_target=1`;
  `:9` `RESULT step=7-default-expire-control keep_refs=8 object_present=yes note=target_keep=yes`.
- Wave-1 mechanism receipt `.ufo/waves/round-30/w1/receipt-SwarmExecutor06-keepref-mechanism.txt`,
  output block: `Number of heads: 2`, `e39cae3c92dd hidden=true`,
  `refs/jj/keep/e39cae3c92dd00b931fd07f3c200fa557b4b7095 B_ancestor=yes`, `after-reindex keep_refs=2
  B_present=yes`.
- `git diff 9420341..9dcd367 -- corpus/README.md`: 46 insertions, 1 deletion; the single deleted line
  is the `:39` map row. Thus `:46`, `:216`, `:228-231` are byte-identical to base.

## Findings

### 1. Fact ledger — NEW vs HELD (18 propositions read from the entry's bytes)

| # | entry line | proposition | verdict |
|---|---|---|---|
| P1 | 19-22 | `recreate_no_gc_refs` keeps refs for the heads it is given, deletes the rest, one ref transaction | HELD — `jj-colocation-receipts.md:30` "Keep refs for current heads are kept. Other keep refs are deleted when their loose-ref file is older than the threshold." |
| P2 | 22-23 | heads are `index.all_heads_for_gc()` inside backend `gc(index, keep_newer)` | HELD — same line: "`gc` (`git_backend.rs:1558-1564`) calls `recreate_no_gc_refs` (`:902-953`) with `all_heads_for_gc()`" |
| P3 | 23-24 | ref set is a function of jj's views and a caller instant, "not of git" | HELD — S054 teaches cell "only `jj util gc` removes non-head keep refs" |
| P4 | 25-27 | a would-be-deleted ref is kept when its loose file is newer than `keep_newer` | HELD — `:30` "deleted when their loose-ref file is older than the threshold" (same fact, inverted) |
| P5 | 26-27 | source comment calls the check racy on re-import (`:929-937`) | HELD — `:30` "The source comment calls that timestamp check "still racy on re-import"" |
| P6 | 27-28 | an existing packed ref is not demoted to loose (source `:931`) | **NEW** — base has no packed-ref statement for keep refs |
| P7 | 28-30 | packed keep ref has no loose mtime, so the ref goes regardless of age ([INFERENCE]) | **NEW**, inference |
| P8 | 31-33 | `--expire` default prunes only what is older than two weeks | HELD twice — S054 teaches "default 2 weeks"; `:30` "14-day threshold by default". The CLI wording is new bytes, not new fact |
| P9 | 33-35 | v0.45.1 accepts only the literal `now`; arbitrary timestamps deferred | **NEW** — no base hit for "only accepts"; new row S220 |
| P10 | 35-36 | `--expire=tomorrow` rejected rc=1 | **NEW**, measured |
| P11 | 36-37 | jj calls git with `--prune=@<keep_newer>`; one instant | HELD — `:86` "jj's `util gc` runs `git gc --prune=@<keep_newer>`" |
| P12 | 38-41 | `jj op abandon` does not delete the ref; doc says run it before `jj util gc` | HELD — `:30` "its doc says to run `jj op abandon ..<some old operation>` first" |
| P13 | 41-42 | the operation object's view holds the set of heads [S221] | **NEW** row/fact (base has no operation-log text) |
| P14 | 42-43 | "Abandoning is therefore the precondition that lets a keep ref fail the current-heads test" | **NEW**, and BROKEN (Finding 2) |
| P15 | 44-47 | git gc removes unreachable objects; `--prune` default two weeks; keeps newer and reachable-from-them | HELD — `:86` plus S063, a base row |
| P16 | 47-49 | a keep ref makes the named commit reachable ([INFERENCE]) | HELD-SOURCED — `:12` "Commits created by `jj` have a ref starting with `refs/jj/` to prevent GC" |
| P17 | 51-60 | measured counts plus `object_present=yes` at every step, replay-identical | **NEW**, measured |
| P18 | 64-65 | after the ref goes "the object is unreachable and a later prune can drop it" | **NEW**, and BROKEN (Finding 3) |

Ten held, six new-and-solid, two new-and-refuted. No false provenance found: every cited line range
was checked against the captured snapshot and holds (`git_backend.rs` 900, 929/931, 941, 977, 1558;
`cli-reference@.md.snap` 2419, 3793, 3801; `git-gc.adoc` 18, 82, 160) — see Finding 5 for the one
line range that is off.

### 2. Coverage or quality? — coverage, narrowly, by the frozen claim's own currency

The frontier obligation is a measurement status, not a fact gap: `corpus/README.md:46` "remaining:
keep-ref expiry unmeasured", and `jj-colocation-receipts.md:108` "The timing in §3 is an inference
from source and from observed keep-ref counts". The frozen C3 text fixes the same currency —
"measured with real jj 0.45.1 in a scratch fixture repo". So the axis moves only if a measurement
landed, and it did: the run is differential in both dimensions, actor (step 3 `git gc --prune=now`
leaves 8 refs, `target_keep=yes`; steps 4 and 8 `jj util gc --expire=now` leave 6, `no`) and
threshold (step 7 default two weeks leaves 8, `yes`). No held sentence carries that; `:108` says the
timing is inference, and `:30` held the source path only.

Counterexample for the "quality" reading, which is real but not fatal: the answer sentence already
existed at base in the S054 row — "only `jj util gc` removes non-head keep refs older than its
threshold (default 2 weeks)". So marginal *fact* coverage is near zero; what is new is evidential
class. Consequence: the credit must be booked as **"measured" upgrade of an already-held claim**,
not as new mechanism knowledge, and it must not be read as covering (a) the object-prune clock or
(b) op-abandon causality. Ten of eighteen propositions are restatement and should cite `:30`/`:86`
instead of re-deriving S054 — a quality defect of the entry, not of the claim.

Verdict: **coverage, HOLDS**, scope-limited to "a non-head keep ref older than `keep_newer` is
deleted inside the next backend gc; `git gc` alone deletes neither the ref nor the object". Quality
would be the correct label for P1-P5, P8, P11, P12, P15, P16.

### 3. BROKEN — the "unreachable" consequence is refuted by the entry's own cited probe

`corpus/knowledge/jj-keep-ref-expiry.md:64-65`: "after which the object is unreachable and a later
prune can drop it". The receipt the entry itself cites shows the opposite for this fixture: the kept
ref `refs/jj/keep/e39cae3c92dd…` names the hidden pre-abandon working-copy commit and
`B_ancestor=yes`, so B stays reachable from a kept head after steps 4, 5 and 8; `B_present=yes`
after a reindex and a further `jj util gc --expire=now`. The entry's own "What this does NOT
establish" (lines 83-88) also understates the probe — it calls the hidden-head arm "not measured
deterministically" while the receipt measured exactly that. This is the paragraph that carries the
souji import, so the import is asserted on a step the evidence does not take.

Smallest safe correction (entry prose only; the frozen C3 counter reads tokens, record lines and
snapshot hashes, so nothing frozen moves): delete "the object is unreachable and a later prune can
drop it" and state the measured shape — the ref goes, the object stays present, and B remains an
ancestor of a kept hidden-head ref, so a prune drops it only when no kept head descends from it.

### 4. BROKEN — the op-abandon attribution is contradicted by the record

Entry:42-43, in a paragraph whose subject is `jj op abandon`: "Abandoning is therefore the
precondition that lets a keep ref fail the current-heads test". Record line 6 shows the tracked ref
already gone (`target_keep=no`, 8 to 6 refs) after `jj util gc --expire=now` with **no** op abandon
performed; op abandon comes after, on line 7, and takes 6 to 2. The wave-1 receipt states it
bluntly: "The kept ref for the abandoned commit is deleted by the gc threshold, not by `jj op
abandon`". At best the sentence conflates commit-level `jj abandon` with operation-level
`jj op abandon`; at worst it inverts the cause.

Smallest safe correction: name the abandon. Commit-level `jj abandon '@-'` removes B from the index
heads, so its keep ref fails the head test at the next backend gc (record step 4); `jj op abandon`
is required only for the refs that abandoned operations alone kept (6 to 2 here).

### 5. DEFECT-NOT-FATAL — three "unmeasured/unrun" statements survive at tip, and the r30 text misreads `:46`

`git diff 9420341..9dcd367 -- corpus/README.md` is 46 insertions and one deletion (the `:39` map
row), so the r30 landing left three base statements byte-identical while appending "F1 — keep-ref
expiry is now measured": `:46` "remaining: keep-ref expiry unmeasured, fleet exposure numerator
re-census"; `:216` "F1 itself stays frontier; keep-ref expiry unmeasured"; `:228-231` "a keep-ref
expiry measurement ... — unrun". Worse, the r30 bullet says "Remaining: the fleet exposure numerator
re-census named at `:46`" while the entry's own Lane link says the opposite — "corpus/README.md:46
names keep-ref expiry as the remaining F1 item". One of the two misdescribes committed bytes; the
entry is right (`:46` still names it). Append-only history arguably excuses `:216`/`:228` (r17
sections), but the r30 bullet's phrasing is a live overclaim about `:46`, and C1's enumerated set of
18 rows plus 10 pointers does not include README prose, so no frozen counter sees it.

Smallest safe correction: reword one clause — "Remaining: the fleet exposure numerator re-census
(also listed at `:46`, whose r12 wording still says keep-ref expiry unmeasured and is left as
history)" — and leave `:46`, `:216`, `:228` untouched.

### 6. DEFECT-NOT-FATAL — S221 line range in the Gate

Entry Gate cites "section Introduction, lines 5-8" for S221; the second quote, "as well as the set
of heads in the repo", is `operation-log.md:9`. The A2 E4 leg hashes snapshots and cannot see a
line-range drift. Correction: 6-9.

### 7. Axis impact

Coverage +1 in the narrow measured sense. Calibration: net neutral in the frozen set (C1 does not
enumerate README prose), but the entry plus README now hold two mutually exclusive statements about
`:46` and two prose claims their own committed record refutes — bookkeeping residue for the next
calibration move, not a C1 target. Operability: unchanged (fixture added, not a gate; A2 E3 replays
it). No axis harmed.

## Attack log

| attacked item | verdict |
|---|---|
| C3 credit is coverage of F1 "keep-ref expiry unmeasured" | HOLDS, scope-limited to the measured ref-removal (Findings 1-2) |
| C3 credit is really quality (restatement of S054 teaches + `:30`/`:86`) | DEFECT-NOT-FATAL — 10 of 18 propositions restate; measurement is the only new class |
| Entry step 4: op abandon as precondition | BROKEN (record line 6, wave-1 receipt finding 1) |
| Entry consequence: "the object is unreachable and a later prune can drop it" | BROKEN (cited probe: `B_ancestor=yes`, `B_present=yes`) |
| Held-entry overlap denial ("this entry does not restate it") | BROKEN for the receipt rule only in the Consequence paragraph, which restates `:12`/`§4` while marking reachability an inference |
| Frontier pointer consistency (`:46`/`:216`/`:228` vs r30 section) | DEFECT-NOT-FATAL |
| Gate line ranges against captured snapshots | HOLDS except S221 (5-8 vs 6-9) |
| Provenance: are the cited bytes really the quoted ones | HOLDS (git_backend.rs 900/929/931/941/977/1558; cli-ref 2419/3793/3801; git-gc 18/82/160) |
| No axis harmed | HOLDS |

## Deliveries

- `.ufo/waves/round-30/w2/SwarmCritic18.md` — this report.
- `.ufo/waves/round-30/w2/SwarmCritic18-receipts.txt` — cited bytes (base S054 row, base
  `jj-colocation-receipts.md` lines 12/30/31/86/108/122, tip README 39/46/216/228-231 and 598-645,
  tip entry 14-92 and 115-121, the whole run record, the wave-1 probe output block, sha256s, README
  diff stat). Scratch removed; no tooling installed.
