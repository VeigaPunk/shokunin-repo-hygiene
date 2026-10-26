# deliver-c3-novelty — does C3 move F1 coverage or restate held ground?

Seat SwarmCritic21, wave 2, read-only. Judged at lane tip 2c16d018e40db7c23420a2c3bb546b52957bcc25
(C3 landing 1baf4da02b71b012ee2426ea7c309496c0c3aca0), base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc.
All quotes below are verbatim from bytes opened this run, <=25 words, no pipe character.

## Verdict

**DEPTH, not new coverage; not a pure restatement either.**

- The surface was named unmeasured before the round, so this is a legitimate frontier step:
  `PROVINCE.md:208` at base — "the object-prune clock that follows a dropped keep ref is unmeasured here";
  `corpus/README.md:625-627` at base — "when the commit object behind a dropped keep ref is pruned by
  git's own clock"; `corpus/knowledge/jj-keep-ref-expiry.md:126` — "Ref removal is measured; object
  removal is not".
- But every proposition the entry states is either held text or an instance of a held rule, except three
  items (N1-N3 below). The measured increment is instrumentation on an already-named gap: the coverage
  map's "unmeasured" was a measurement gap, not an unknown surface.
- The entry's own summary sentence over-claims by one proposition (descendant precedence, already held
  at `jj-keep-ref-expiry.md:126`).

## Proposition ledger

| Entry proposition | Class | Held location and verbatim line |
|---|---|---|
| 1 git gc keeps objects reachable from roots (branches, tags, index, remote-tracking, reflogs, refs/*) | HELD | `corpus/SOURCES.md:84` (S063 cell, base) — "gc keeps objects referenced by branches, tags, index, remote-tracking branches, reflogs and anything else under refs/*" |
| 2 a keep ref naming a descendant holds B after B's own ref goes | HELD | `corpus/knowledge/jj-keep-ref-expiry.md:126` — "because a surviving keep ref names a descendant whose parent is B" |
| 2b reflog expiry plus gc --prune=now still left B present | HELD | same line — "even `git reflog expire --expire=now --all` followed by `git gc --prune=now` left B present" |
| 3 a reflog entry is a root; reflog-only commits count as reachable | HELD (rule) | `corpus/knowledge/repo-size-census-readonly.md:26-27` — "`--no-reflogs` refuses to treat reflog-only commits as reachable"; S063 cell also names "reflogs" |
| 3b 90-day / 30-day reflog windows, `all` and `never` sentinels | HELD | `corpus/knowledge/git-grace-periods-and-expire-to.md:9` — "Reflog entries: `gc.reflogExpire` defaults to 90 days" |
| 4 object mtime inside the prune date keeps it, two weeks by default | HELD | `corpus/knowledge/jj-keep-ref-expiry.md` claim 5, :46 — "keeping objects newer than that date and everything reachable from them" |
| 4b `gc.recentObjectsHook` overrides true age | **NEW (sourced only)** | no other occurrence in `corpus/` (grep: only the new entry, lines 48 and 137) |
| 5 prune is a loose-object date, reflog dates come from `gc.reflogExpire`, so a prune is not reflog evidence | HELD as distinction, NEW as measured instance | `git-grace-periods-and-expire-to.md:18` — "Git's object, reflog, worktree-metadata, and rerere expiries are distinct mechanisms and config values" |
| 6 `git prune` removes unpacked only; `gc --prune=now` is the total remover; expiry before prune is necessary not sufficient | HELD | `corpus/SOURCES.md:138` (S117 cell, base) — "prune removes unpacked objects unreachable from the given heads, leaves packed ones"; the not-sufficient half is `jj-keep-ref-expiry.md:126` |
| 7 jj's `util gc` passes `--prune=@<keep_newer>`, so reflog dates are untouched | HELD | `jj-keep-ref-expiry.md` claim 3 — "The backend then calls git with `--prune=@<keep_newer>`" |
| 7b jj documents `git gc` as safe but untested | HELD at row level | S051 covers that file and its "git gc" sentence (row scope cell, `corpus/SOURCES.md:72`); the exact sentence had no prior quote |
| 8 **measured**: a HEAD reflog entry jj's export wrote is the sole keeper across `git gc --prune=now`, and expiry then prune removes B (roles 1-2) | **NEW measurement** of a held rule | not isolated anywhere before: r30 wave-2 receipt `census/round-30/waves/w2/SwarmReviewer15-receipts.txt:78` shows `--no-reflogs` unreachable count 0, i.e. the descendant keep ref still rooted B |
| 9 measured: no assigned lever removes B; a keep ref naming a descendant holds it (role 3) | HELD observation, re-measured | `jj-keep-ref-expiry.md:126` |
| 9b **measured**: abandoning the descendant plus `jj op abandon` plus `jj util gc` releases B with no ref surgery (role 4) | **NEW measurement** | held text covers the presence direction only; the jj-side release direction is not in any held entry |
| 10 **presence is not a receipt**; a deletion receipt must name the prune date, the reflog state and the keep-ref state | **NEW framing** (derived) | no other occurrence of "presence is not" or "cat-file" in `corpus/knowledge/` besides this entry |

New to the corpus: N1 = `gc.recentObjectsHook` (sourced, unmeasured); N2 = the reflog-only isolation and
the jj-side release (two measured instances of held rules); N3 = the receipt consequence. The entry
itself concedes the sourcing ledger at line 137: "`gc.recentObjectsHook` (claim 4) is the one new
sourced item."

## Why not "coverage"

The named gap was a *clock* question — when does git's own prune remove the object. The entry measures
precedence among keepers under forced-now levers and discloses that the clock itself is not measured:
"no arm waits out a default window" (entry, What this does NOT establish), and PROVINCE's r31 note says
the fourth holder is "sourced, not measured". So the map's unmeasured line is closed as *mechanism and
receipt vocabulary*, not as the timing question it posed.

## Why not "restatement"

Roles 1-2 measure something no committed text states as a measurement (r30 receipts had the reflog
present but never as the sole root), role 4 measures a positive release path, and N3 is the receipt
consequence the ground F1 exists for. That is an increment, and the entry correctly cites held ground
for claims 1, 3-windows, 4-mtime and 7 rather than re-claiming it.

## Correction C3 should carry (smallest safe)

One sentence: strike "a keep ref naming a descendant outranks reflog expiry and every prune (roles 3
and 4)" from "What this entry adds" and replace it with a pointer to `jj-keep-ref-expiry.md:126`, keeping
role 4's release direction as the addition. Nothing else in the entry needs to move.

## Residuals for the L1

1. `corpus/README.md:46` still says "keep-ref expiry unmeasured" at the tip; the entry's Lane link cites
   that line as "F1's remaining work" and says the frontier line is the L1's to update. Not updated.
2. `corpus/README.md:672` says "the entry closes the object-prune question", while the object's own
   two-week window is sourced only — the r30 bullet it supersedes asked for the clock.
3. `gc.recentObjectsHook` has no Gate quote, and S063's anchor cell still records only "§ NOTES first
   paragraph" although the entry cites the config fragment at `gc.adoc:96-147` under S063.
4. The record's third arm `reflog-only` is outside the frozen fixture contract's enumeration
   `arm=<solo|descendant>` (`census/round-31/records/preregistration.txt:20`); the entry discloses the
   addition, and no counter leg checks arm names, so the deviation is invisible to the instrument.
5. Role 3 attributes the 6-to-2 keep-ref drop to `jj op abandon` plus `jj util gc --expire=now`, but the
   fixture packs every ref at step 2 (`git pack-refs --all`), so the packedness lever the r30 wave-2
   correction identified is not excluded; the r31 fixture has no loose-ref control.
