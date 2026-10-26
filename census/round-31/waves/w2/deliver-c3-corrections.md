# deliver-c3-corrections — append-only corrections for the C3 entry (round 31, wave 2)

Seat SwarmScribe23, read-only. Target entry `corpus/knowledge/jj-dropped-keep-object-lifetime.md`,
landed at `1baf4da02b71b012ee2426ea7c309496c0c3aca0`, byte-unchanged at lane tip
`2c16d018e40db7c23420a2c3bb546b52957bcc25` (base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`).

The block below is ready to append at the end of the entry, after its `- ADMIT:` / `- REJECT:`
lines, exactly as the held entry's `## Round 30 wave-2 corrections (append-only)` was appended.
Eighteen bullets, one per refuted or overstated sentence or provenance line; every bullet quotes
the superseded text in backticks and names its evidence. No frozen target is relaxed, no rule is
proposed: bullets 11 and 13 ask the L1 to record a frozen-format deviation and a missing control.

L10 discipline: no backticked span in this file begins with the record's `RESULT` line prefix; the
record lines are cited by arm/step name and by field, so `census/round-31/c3-counter-v3.py` leg L10
(a backticked span that begins with that prefix must be a whole line of
`census/round-31/records/jj-object-clock-run.txt`) is untouched by the append. No span here
contains a reserved host, and the section sits outside `## Gate`, so L5/L6/L7 read the same bytes as
before.

Grounds (wave-2 attacks, all read this run): `.ufo/waves/round-31/w2/SwarmCritic18.md` findings
1-11 (sentence attack; record reproduced byte-identically by that seat),
`.ufo/waves/round-31/w2/SwarmScout19.md` findings 1-5 (source re-open; three snapshots re-fetched
byte-identical), `.ufo/waves/round-31/w2/deliver-c3-novelty.md` (correction and residuals 3, 5) and
`.ufo/waves/round-31/w2/deliver-docs-review.md` finding 5. Each claim below was checked this run
against `census/round-31/records/jj-object-clock-run.txt`, `tests/fixtures/r31-jj-object-clock.sh`,
`census/round-31/sources/`, `census/round-30/sources/git-gc.adoc` and
`census/round-30/sources/git_backend.rs`; the one quote re-fetched here is named with its sha256.

---

## Round 31 wave-2 corrections (append-only)

The sentences above stand as admitted; these lines supersede them where they disagree. Grounds: the
round-31 wave-2 attacks `.ufo/waves/round-31/w2/SwarmCritic18.md` (findings 1-11) and
`.ufo/waves/round-31/w2/SwarmScout19.md` (findings 1-5), and the novelty and docs reviews recorded at
`.ufo/waves/round-31/w2/deliver-c3-novelty.md` and `.ufo/waves/round-31/w2/deliver-docs-review.md`.

- Supersedes the opening clause `this entry does not restate it`: claim 2 restates the keep-ref write/removal rule the held entry carries (`corpus/knowledge/jj-keep-ref-expiry.md` claim 1, from `git_backend.rs:900-925`) and claim 7 restates that entry's `--prune=@<keep_newer>` shell-out clause (`git_backend.rs:970-987`); both are cited ground here, not re-derivations, and the held entry owns them.
- Supersedes the claim-2 predicate clause `a keep ref survives only when`: `git_backend.rs:925` is `if new_heads.contains(&id) && name_good {`, so the ref name's shape is a second condition (`:924`), and a ref that fails it is still kept when its loose-ref file is newer than `keep_newer` (`git_backend.rs:939-945`); the function runs only from the backend `gc` (`git_backend.rs:1558-1564`). Bytes: `census/round-30/sources/git_backend.rs`, sha256 95147270e5bc2a689e1191256c0f214d8e52ac6d4523756eb6b8ec8113d86c69.
- Supersedes `The record measures the separation` (claim 5) and `The run also measures the independence asserted in step 5`: every reflog entry in the run is seconds old and inside the 90/30-day window (`gc.adoc:115-132`), so `reflog_hits=1` after `git gc --prune=now` is what any gc returns at that age. Wave-2 probe (SwarmCritic18 finding 3): in the same post-deletion state, `git -c gc.reflogExpire=now -c gc.reflogExpireUnreachable=now gc --prune=now` left B absent, so a gc does empty the reflog whenever the window allows. What the record shows is that this invocation left a fresh entry; the two-date separation stays documented (`git-gc.adoc:81-87`, `gc.adoc:115-132`), not measured.
- Supersedes claim 6's `its scope is unpacked unreachable objects, packed ones remain`: the byte behind it is `git-prune.adoc` at tag v2.56.0 line 30, "Note that unreachable, packed objects will remain." (sha256 75185e698450ad8ba72a2b42899071b54f1b20dfb518bbb01db7ffbd26151472, fetched from the tag this run); no S117 snapshot exists in the lane.
- Supersedes claim 6's citation of the loose-object option for `packed or crufted`: `git gc` also runs `repack --cruft --cruft-expiration 2.weeks.ago` for cruft packs (`gc.adoc:97-99`), which is the clause that half rests on; `git-gc.adoc:81-87` is the loose-object option only.
- Corrects claim 7's S220 range: `backend-dependent garbage collection` is `cli-reference@.md.snap:3791`; lines 3793 and 3799-3805 carry the `jj op abandon` advice and the `--expire` option.
- Supersedes Role 1's `first deletes every keep ref naming B` and its `as the only root`: the control deletes every keep ref whose target is B or a strict descendant of B (`tests/fixtures/r31-jj-object-clock.sh:126-135`, applied at `:196-201`; `keep_refs` 8 to 6), and that wider deletion is what leaves one `HEAD` reflog entry as the only remaining root that reaches B. Deleting only the ref named after B leaves 7 keep refs and B present after `git gc --prune=now` (SwarmCritic18 finding 1 probe: `reflog_hits=1 object_present=yes`), so the broader deletion is the mechanism, not an aside.
- Corrects Role 1's `reads the same except for the ref count`: the `drop-keep-refs-naming-target` and `git-gc-prune-now` lines of `census/round-31/records/jj-object-clock-run.txt` carry the same `keep_refs=6`, `target_keep=no`, `reflog_hits=1` and `object_present=yes`; the 8-to-6 change and `target_keep` yes-to-no both happen at the deletion step, before the quoted row, and only the step name differs between the two rows.
- Qualifies `Three independent keepers hold B`: the mtime keeper is sourced from git-gc(1) and isolated in no arm — every prune in the record is `--prune=now` or `jj util gc --expire=now` — so it is the fourth holder that `PROVINCE.md`:224 already calls the one "sourced, not measured", not a measured keeper of this run.
- Supersedes `absence is cheap to establish and presence is expensive`: the record's presence reading is one `git cat-file -e` per step (`tests/fixtures/r31-jj-object-clock.sh:108`, 17 rows), while absence needed every keep ref reaching B deleted (`solo`, `keep_refs` 6 to 1) or the descendant abandoned, then a prune. The corollary is `presence is cheap to observe and absence is the expensive claim`.
- Corrects `The reflog-only arm is a third repository beyond the two arms the preregistration named`: the frozen step-line format (`census/round-31/records/preregistration.txt`:20) enumerates the arm field as `solo` or `descendant`, and the record prints four lines with `arm=reflog-only`, so the third arm is a deviation from a frozen format — to be recorded in `census/round-31/records/amendments.txt` as a stricter-only addition, not only an entry aside.
- Supersedes the novelty clause `a keep ref naming a descendant outranks reflog expiry and every prune (roles 3 and 4)`: that precedence is held text at `corpus/knowledge/jj-keep-ref-expiry.md`:126 (round-30 wave-2); the round-31 addition is the release direction (role 4) and the reflog-only isolation (roles 1-2).
- Qualifies Role 3's `removes further keep refs`: step 2 already ran `git pack-refs --all` (`tests/fixtures/r31-jj-object-clock.sh:150`), so the 6-to-2 drop is measured on packed refs and this fixture has no loose-ref control; the drop coincides with `jj op abandon ..@-` plus a second `jj util gc --expire=now` (`:158-160`), which the run does not separate from the packedness the r30 correction made load-bearing.
- Qualifies Role 3's `still has a keep ref`: B has a keep ref of its own at the `abandon` step (record: `target_keep=yes`, `keep_refs=8`), and `pack-and-util-gc` is the step that drops it (`target_keep=no`, `keep_refs=6`); from then on the survivor the role names is the rewritten working-copy commit's ref, a strict descendant, which an independent assembly reproduced by reading that commit's parent line back to B (`.ufo/waves/round-31/w2/SwarmExecutor17.md` finding 1).
- Corrects the Gate bullet's `§ Git-specific behaviours, section Garbage collection line 52`: `census/round-31/sources/git-compatibility.md` has no such heading — the bullet `Garbage collection: Yes.` sits under `## Supported features` (`:11`) and the quoted sentence spans lines 52-53. The file's registry row is S051 (`corpus/SOURCES.md`:72), raw at tag https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/docs/git-compatibility.md.
- Supersedes the source line's `(placeholder id: the L1 renumbers by document)`: the row landed as S222 at `corpus/SOURCES.md`:167, opened 2026-10-26, 5657 bytes, sha256 59e7f0f15204a8c9f9b058ee62cb26aa2fa726b35dc85c702b75243424d6bf54.
- Names the bytes behind the `git-gc.adoc` anchors of claims 1, 4, 5 and 6: `census/round-30/sources/git-gc.adoc`, sha256 e3dbc4081095faf8d2d760eb4a47a1350f89d0c772f55eaada9cfbcdbeafba8c, re-fetched byte-identical from tag v2.56.0 this round. It is the round-30 capture, not a file under `census/round-31/sources/`, so the Gate's `three snapshots named below` does not cover those quotes.
- Qualifies the S063 citations for the config fragment: S063's registry cell (`corpus/SOURCES.md`:84) scopes the page to `§ NOTES first paragraph`, while `gc.pruneExpire` (`gc.adoc:96-105`), `gc.recentObjectsHook` (`gc.adoc:140-147`) and the config-fragment reflog lines (`gc.adoc:115-132`) come from `Documentation/config/gc.adoc`; S002's cell (`corpus/SOURCES.md`:23) covers `gc.reflogExpire` and `gc.reflogExpireUnreachable` only. S063's cell needs the CONFIGURATION anchor before these Gate bullets are traceable, and `gc.recentObjectsHook` has no Gate quote at all.

---

## What this delivery does not do

- It does not edit the entry, the fixture, the record, `corpus/SOURCES.md`, `amendments.txt` or any
  counter; the L1 is the single integration owner.
- It does not re-run the C3 counters or the fixture; the target readings it relies on are the
  wave-2 seat readings (`legs=11/12/13 fail=0 f1_entries=4`, record reproduced byte-for-byte by
  SwarmCritic18, SwarmReviewer22 and the ReRunC3 seat), not a scribe measurement. Unrun by this
  seat: all three counters, the fixture, `tools/souji-coverage-agreement.py`.
- Two bullets (11, 13) ask for an amendment record and a loose-ref control: neither is a frozen
  target change, and neither is proposed as one.
