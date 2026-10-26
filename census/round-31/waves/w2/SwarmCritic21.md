# SwarmCritic21 — C3 novelty attack (r31 wave 2)

Seat: critic, read-only. Lane tip 2c16d018e40db7c23420a2c3bb546b52957bcc25 (branch master), base
9f17a1ef571f3a510a51ac233d7cf50ac0c871fc, C3 landing 1baf4da02b71b012ee2426ea7c309496c0c3aca0.
Deliverable: `.ufo/waves/round-31/w2/deliver-c3-novelty.md`.

## Status

STATUS: PARTIAL — the novelty question is answered (depth, not new coverage) and every source claim
re-derived, but the landed prose over-claims one held proposition and the coverage map's frontier line
it cites is stale; no fabrication found.

## Evidence

Contract read first: `census/round-31/records/preregistration.txt` (C3 on line 20: surface "the
object-prune clock behind a dropped keep ref", fixture contract `arm=<solo|descendant>`, target
`legs=11 fail=0 f1_entries=4`) and `census/round-31/records/amendments.txt` (A0-A5; A1 discloses
"novelty is judged by the reviewers, not by a leg").

Surface named unmeasured before the round — all three at base:

    git -C <lane> show 9f17a1ef...:PROVINCE.md | sed -n '198,220p'
      :208 "the object-prune clock that follows a dropped keep ref is unmeasured here"
    git show 9f17a1ef...:corpus/README.md | awk 'NR>=621 && NR<=627'
      :625-627 "when the commit object behind a dropped keep ref is pruned by git's own clock"
    git show 9f17a1ef...:corpus/knowledge/jj-keep-ref-expiry.md | grep -n 'Ref removal is measured'
      :126 "Ref removal is measured; object removal is not"

Held propositions the entry restates (base = tip; `git diff base..tip -- corpus/knowledge/jj-keep-ref-expiry.md
corpus/knowledge/git-grace-periods-and-expire-to.md` is empty):

    corpus/knowledge/jj-keep-ref-expiry.md:126
      "because a surviving keep ref names a descendant whose parent is B"
      "even `git reflog expire --expire=now --all` followed by `git gc --prune=now` left B present"
    corpus/SOURCES.md:84 (S063 cell at base)
      "gc keeps objects referenced by branches, tags, index, remote-tracking branches, reflogs and
       anything else under refs/*"
    corpus/knowledge/repo-size-census-readonly.md:26-27
      "`--no-reflogs` refuses to treat reflog-only commits as reachable"
    corpus/knowledge/git-grace-periods-and-expire-to.md:9
      "Reflog entries: `gc.reflogExpire` defaults to 90 days"
    corpus/SOURCES.md:138 (S117 cell at base)
      "prune removes unpacked objects unreachable from the given heads, leaves packed ones"
    corpus/knowledge/jj-keep-ref-expiry.md claim 3
      "The backend then calls git with `--prune=@<keep_newer>`"

Source claims re-derived from live bytes (four fetches this run; all hashes equal the entry,
`census/round-31/sources/SHA256SUMS` and `census/round-31/records/fetch-receipts.tsv`):

    r.adoc 59e7f0f15204a8c9f9b058ee62cb26aa2fa726b35dc85c702b75243424d6bf54  5657
    g.adoc 0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a  7753
    c.md   0fb71f992b0ed05d547e597d3f5f1cd33ed9e5d56a4e4e4cb851ba30c766c641 12284
    gc.rs  9c4d6a3704abb6f3afbb63cfd44153437b83d7e68d0f2426f84f8cdbbb0b4b9b  2235

Line anchors verified in the committed snapshots: `census/round-31/sources/gc.adoc` 96-97
(`gc.pruneExpire`), 115-119, 124-128, 140-147 (`gc.recentObjectsHook`, "Interpret their output as
object IDs which Git will consider as"); `census/round-30/sources/git-gc.adoc` 81-87 (`--prune`),
141-146, 144-146, 148-151, 160-161; `census/round-31/sources/git-reflog.adoc` 66-68, 111-127;
`census/round-31/sources/git-compatibility.md:52-53`; `census/round-30/sources/git_backend.rs:900`
and `:925`. Every anchor lands on the sentence the entry attributes to it.

Record and spans: `census/round-31/records/jj-object-clock-run.txt` has 17 `RESULT ` lines; the six
backticked `RESULT ` spans in the entry (lines 94, 98, 104, 105, 109, 110) are each a whole line of it.

Novelty instrumentation: `grep -rn recentObjectsHook corpus/` → only the new entry (lines 48, 137);
`grep -rn 'presence is not\|not a receipt\|cat-file' corpus/knowledge/` → only the new entry.
`grep -ln '^ground: F1' corpus/knowledge/*.md` → 4 at tip, 3 at base. r30 wave-2 receipts show the
reflog was never isolated before: `census/round-30/waves/w2/SwarmReviewer15-receipts.txt:78` reports
`--no-reflogs` unreachable count 0, i.e. the descendant keep ref still rooted B.

Fixture shape: `tests/fixtures/r31-jj-object-clock.sh:151-153` runs `git pack-refs --all` then
`jj util gc --expire=now` as step `pack-and-util-gc`; the third arm's rooting test is
`merge-base --is-ancestor` (fixture `target_or_desc_keep_refs`), not the name test, so role 1's
"only root" is a rooting claim and not a `target_keep` artefact.

## Findings

1. **Novelty overclaim — descendant precedence.** `corpus/knowledge/jj-dropped-keep-object-lifetime.md:133-137`
   lists "a keep ref naming a descendant outranks reflog expiry and every prune (roles 3 and 4)" as what
   the entry adds; the base held entry already states it: "because a surviving keep ref names a
   descendant whose parent is B" and "even `git reflog expire --expire=now --all` followed by
   `git gc --prune=now` left B present" (`jj-keep-ref-expiry.md:126`). Claim 2 of the same entry credits
   r30 for the observation, so the entry contradicts itself. Axis: coverage (novelty accounting).
2. **"Closes the object-prune question" vs a sourced-only clock.** `corpus/README.md:672` says "the entry
   closes the object-prune question", while the entry's claim 4 leaves the mtime keeper sourced and its
   does-not list says "no arm waits out a default window"; the r30 bullet it supersedes asked exactly for
   "when the commit object behind a dropped keep ref is pruned by git's own clock"
   (`corpus/README.md:625-627` at base). Axis: calibration (honesty of the closure statement).
3. **Stale pointer in the entry's own Lane link.** `corpus/knowledge/jj-dropped-keep-object-lifetime.md:192-194`
   cites `corpus/README.md`:46 as "F1's remaining work" and says the frontier line is the L1's to update;
   at the tip `:46` still reads "remaining: keep-ref expiry unmeasured". The row at `:39` was updated, the
   frontier line was not, and the entry points readers at the un-updated one. Axis: coverage (map
   bookkeeping).
4. **New sourced item without a quote or a row anchor.** `gc.recentObjectsHook` is called "the one new
   sourced item" (entry:137) but has no `## Gate` quote, and the row it is attributed to, S063, still
   records only "§ NOTES first paragraph" in its anchor cell while the entry cites the config fragment at
   `gc.adoc:96-147` and names the new snapshot. Axis: coverage (provenance).
5. **Record arm outside the frozen fixture contract.** `preregistration.txt:20` fixes the RESULT shape as
   `arm=<solo|descendant>`; the record carries `arm=reflog-only` for 4 of 17 lines, and the entry discloses
   the addition (entry:125-126). The most novel measured content lives entirely in the non-contracted arm,
   and no counter leg (`c3-counter.py` L8-L10) checks arm names, so the deviation is invisible to the
   instrument. Axis: calibration (contract fidelity of the frozen record shape).
6. **Keep-ref drop attributed to `--expire=now` without excluding packedness.** Entry role 3 says
   "`jj op abandon ..@-` plus `jj util gc --expire=now` removes further keep refs (`keep_refs` 6 to 2)",
   but every ref is packed at step 2 (`pack-and-util-gc`), which is the lever the r30 wave-2 correction
   identified ("the measured lever at steps 4 and 8 is packedness", `jj-keep-ref-expiry.md`), and the r31
   fixture has no loose-ref control. The entry defers the mechanism to held ground elsewhere, so this is
   an attribution gap, not a wrong result. Axis: coverage.
7. **Minor: dropped conjunct.** Entry claim 2 renders `git_backend.rs:925` as a keep ref surviving when
   `new_heads.contains(&id)`; the line reads `if new_heads.contains(&id) && name_good`, so a keep ref whose
   name does not match its id is deleted even when it names a head. Axis: coverage (precision).

## Attack log

1. Try to find `gc.recentObjectsHook` anywhere in the held corpus — FAILED to find it; it is genuinely new
   (sourced only, never measured). Supports N1 in the delivery.
2. Try to show the reflog-only result was already measured in r30 wave 2 — FAILED: the r30 receipts hold
   the reflog present but the descendant keep ref still roots B (`--no-reflogs` count 0), so no committed
   text isolates the reflog as sole keeper. Roles 1-2 are a real measurement increment.
3. Try to falsify the six quoted `RESULT` spans as whole lines — FAILED; each matches a record line exactly.
4. Try to catch false provenance — FAILED: all four live re-fetches hash to the committed digests, and
   every cited line range lands on its sentence. The one live-fetched source with no snapshot
   (`cli/src/commands/util/gc.rs`) is disclosed in the entry and its hash reproduces.
5. Try to show the surface was not named unmeasured before the round (which would make the round a
   restatement) — FAILED: named at `PROVINCE.md:208`, base `corpus/README.md:625-627` and
   `jj-keep-ref-expiry.md:126`. The frontier step is legitimate.
6. Try to show the descendant-precedence result is new — FAILED: held verbatim at `jj-keep-ref-expiry.md:126`.
   This is the one overclaim; it is fixable by one sentence and does not touch the frozen target.
7. Try to show role 4 is held — FAILED: the held text covers the presence direction only; the jj-side
   release (abandon the descendant, `jj op abandon`, `jj util gc`) is new. So the verdict is depth, not
   restatement.

Not run in this seat: the C3 counter (`c3-counter.py`/v2/v3) — claim verification belongs to other wave-2
seats, and the instrument cannot judge novelty by design (A1 disclosure). No tools installed.

## Deliveries

- `.ufo/waves/round-31/w2/SwarmCritic21.md` — this report.
- `.ufo/waves/round-31/w2/deliver-c3-novelty.md` — proposition ledger (NEW vs HELD with held lines),
  verdict `DEPTH`, smallest safe correction, and five residuals for the L1.

Scratch `/fast/scratch/hyaku/souji-r31/w2-SwarmCritic21` removed after the deliveries were copied.
