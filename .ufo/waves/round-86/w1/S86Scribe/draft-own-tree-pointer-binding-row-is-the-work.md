# DRAFT for the L1 — a new section for `corpus/knowledge/own-tree-pointer-binding.md`

Seat: `S86Scribe`. Lane: `souji` (`/home/vgpnk/Projects/shokunin/souji-shokunin`). Draft only: the L1 integrates.
Nothing here is filed; the lane's `corpus/` files are unchanged.

**This draft APPENDS a section to `corpus/knowledge/own-tree-pointer-binding.md`; it replaces nothing.** The file's
last section is "A shadowed clause is not an unbound clause (r85)"; the new section continues its r83 → r84 → r85
sequence. It answers the r86 routed item ("the row is an r86 item") by naming the row, the clause it binds, and the
measurement that shows the clause is now bound.

Evidence this draft cites — every pointer is a committed path and line number at lane base `2acbbfc8` unless stated:

- `census/round-86/c1-pointer-counter.py` — `OWNTREE_WAVE` (`:351`), `_owntree_ok` (`:354`), the short-shape guard
  (`:366-367`), the `_capture_ok` fallback (`:368-369`), the wave-directory comparison (`:370-371`), `judge()` (`:374`),
  the own-tree belt (`:405-409`), the census-capture belt (`:413-416`), the census-in-tree branch (`:417-425`), the
  no-round belt (`:426-429`), the r86 pin entry (`:136-140`).
- `census/round-86/c1-false-rows.tsv` — the two new rows, NF-W (`:49`) and NF-Y (`:50`).
- `census/round-86/c1-items.tsv` — item I86S (`:5`).
- `census/round-86/c1-mutants.json` — members `c7-census-in-tree` and `m14-short-shape`.
- `census/round-86/c1-false-row-harness.py` — `POP_PINS` (`:94-97`), `I86S_PIN` (`:101`), the `POPS` item table
  (`:102-105`).
- `census/round-86/c1-clause-battery.py` — the frozen battery and its `PINS` table.
- `census/round-86/records/c1-after.txt` and `census/round-86/controls/c1-before-r85-population.txt` — the two arms.
- `census/round-86/preregistration.txt` — the frozen C1 wording (committed alone at `d77b4258`).
- `.ufo/waves/round-86/w1/S86Scribe/probe-row-decides-clause.py` and
  `.ufo/waves/round-86/w1/S86Scribe/receipts/` — my own re-derivation (this seat's own files).

---

## Grounding an unbound clause: the row is the work (r86)

r85 ended with two clauses measured REACHABLE and UNBOUND — a row could bind each, and the population had no such
row. The r85 section says what that means for the claim language ("a clause with no row is not certified whether or
not it is reachable, and a claim that counts a clause as coverage must carry its row") and leaves the work open: it
routes the census-in-tree branch's row to r86 and names the own-tree short-shape guard alongside it. r86 does that
work. The population grows by two rows and the mutant set by two members, and the two clauses stop being clauses
nobody has measured.

**The population.** `census/round-86/c1-false-rows.tsv` (sha256 `79db70f6…f561`) is the r85 47-row population
(sha256 `1468236c…8d42`) byte-for-byte, in order, plus two rows at the new fixture revision R9. The two rows differ in
what they carry INTO the rule, not in what they assert about the rule:

| row | line | item | token (below its round) | target (below its round) |
|---|---|---|---|---|
| NF-W | `:49` | I85R | `records/c1-after.txt` | `w1/c1-after.txt` |
| NF-Y | `:50` | I86S | `c1-pointer-counter.py` | `waves/c1-pointer-counter.py` |

(The two targets are paths inside the HARNESS FIXTURE, not paths in the lane: the fixture is a clone of the lane at
base `705fa138` with the harness's own commits on top, and a fixture row's target is planted there at revision R9. The
full fixture-relative forms are `census/round-84/w1/c1-after.txt` for NF-W and
`census/round-83/waves/c1-pointer-counter.py` for NF-Y; neither is a file in the lane, and a reader looking for them
there will not find them.)

NF-W's token is the census-rooted item I85R (`census/round-84/records/c1-after.txt` — a lane path, the item's token)
moved into a WAVE DIRECTORY under its own round (fixture target `census/round-84/w1/c1-after.txt`): two components on
each side, so the short-shape guard does not fire, and the target's own-tree prefix equals the token's. NF-Y's token is
the new item I86S (`census/round-83/c1-pointer-counter.py`, `census/round-86/c1-items.tsv:5`, frozen digest
`f:052c4f3f…d79` — a lane path) — the first population item whose token sits ONE component below its round — moved
into a wave capture under the same round (fixture target `census/round-83/waves/c1-pointer-counter.py`).

**How each row reaches exactly one clause.** This is the part that has to be measured rather than read off the branch
order, because a belt's guard is a conjunction and the clause that looks necessary for it may be vetoed by the next
conjunct. The counter's own refusal message names the deciding clause, and the mutants name the row.

The two branches that matter, quoted from `census/round-86/c1-pointer-counter.py`:

```
351: OWNTREE_WAVE = re.compile(r"^(?:w[0-9]+|a2w1|assimilation)/")
352:
353:
354: def _owntree_ok(token, kr, target, tr):
...
362:     tt = target[tr.end(0):].rstrip("/")
363:     tk = token[kr.end(0):].rstrip("/")
364:     want = [c for c in tk.split("/") if c]
365:     got = [c for c in tt.split("/") if c]
366:     if len(want) < 2 or len(got) < 2:
367:         return False
368:     if _capture_ok(token, kr, target, tr):
369:         return True
370:     m = OWNTREE_WAVE.match(tt + "/")
371:     return bool(m) and got[1:] == want[1:]
```

and, in `judge()`:

```
374: def judge(root, rev, fleet, item, entry, blob):
...
405:         elif kr and target[:tr.start(0)] == token[:kr.start(0)] and not _owntree_ok(token, kr, target, tr):
406:             # r82 (S81MutCounter NF-F/NF-G): the token-prefixed branch also requires a true capture shape; only
407:             # the identical token path (the true move) or a wave subtree passes, so byte-equal own-tree decoys
408:             # (`.ufo/waves/round-N/decoy/...`) fail here.
409:             why = "own-round-tree target is neither the token's own path nor a wave capture keeping the token's suffix"
...
417:         elif kr and target[:tr.start(0)] == "census" and token[:kr.start(0)] == "census" \
418:                 and not _capture_ok(token, kr, target, tr):
...
425:             why = "census-in-tree target is not a wave capture keeping the token's full path suffix"
```

NF-W is decided by the census-in-tree branch at `:417-425`. Note what does NOT decide it: the own-tree belt at `:405`
does not fire, because `_owntree_ok` returns True for it — `OWNTREE_WAVE` (`:351`) matches `w1/`, and the wave
comparison at `:371` (`got[1:] == want[1:]`) holds because both sides carry `c1-after.txt` as their second component.
The belt at `:405` is vetoed by the `not _owntree_ok(...)` conjunct, exactly as the r85 section's own worked example
(r85 A1 / S85Scribe F1) established for the branch order. The prefix-equality condition `target[:tr.start(0)] ==
token[:kr.start(0)]` is NECESSARY for the belt to fire and NOT SUFFICIENT. So control reaches `:417`, where the
census-rooted token and the census-rooted target meet, `_capture_ok` is False (`w1/` is not a capture shape —
`CAPTURE` is `^(?:waves/|wave/|records/wave-[^/]+/)(.+)$`, `:337`), and the row is refused with that branch's own
reason.

NF-Y is decided by the short-shape guard inside `_owntree_ok`, at `:366-367`. Here the refusal REASON the counter
prints is the own-tree belt's (`:409`), because that belt is where `_owntree_ok`'s False is consumed — but the CLAUSE
that decides the row is the guard, and the distinction is measured, not asserted: dropping only the guard lets
`_capture_ok` (`:368-369`) accept the one-component remainder `c1-pointer-counter.py` — the token's whole path below its
round is one component, so `want` is `["c1-pointer-counter.py"]` and the capture's suffix is the same single
component — `_owntree_ok` then returns True, the belt at `:405` stands down, and the row resolves as MOVED. A reader
who takes the printed reason as the clause would bind the belt; a reader who takes the mutant as the clause binds the
guard. The mutant is the right witness, because the belt is a caller of the guard, not the guard.

**The check: a row kills its mutant on the new population and not on the old one.** Scored with the frozen battery
(`census/round-86/c1-clause-battery.py`) over the two pinned populations, same counter, same eight mutants:

- after: `ARM pristine pop=r85 rows=47 mismatches=0 errors=0 exit=0`; `ARM pristine pop=r86 rows=49 mismatches=0
  errors=0 exit=0`; `c7-census-in-tree` `pop=r85 killed=no` | `pop=r86 killed=yes mismatches=1 errors=0`;
  `m14-short-shape` `pop=r85 killed=no` | `pop=r86 killed=yes mismatches=1 errors=0`; the six r85 mutants `killed=yes`
  on both; `SUMMARY mutants=8 sets=r85,r86 pristine_r85=ok pristine_r86=ok killed_r85=6 killed_r86=8
  killed_total=14` (`census/round-86/records/c1-after.txt`).
- before (the do-nothing control, same battery and same eight mutants, r85 47-row population alone): the six r85
  mutants `killed=yes`, `c7-census-in-tree killed=no mismatches=0 errors=0`, `m14-short-shape killed=no mismatches=0
  errors=0`, `SUMMARY killed_r85=6` (`census/round-86/controls/c1-before-r85-population.txt`).

The delta is the population, not the rule: the r86 counter differs from the r85 counter by ONE `POPS` entry (`:136-140`,
the r86 item population `census/round-86/c1-items.tsv`) and its docstring. No resolution rule, guard, branch or
message changed.

**Which row kills which mutant, and that the other row is untouched.** This is the "one row per clause" measurement,
and it is the one the r85 section's own procedure asks for: author the single-edit mutant, score it on every pinned
population, and read the killing row. My re-derivation, on the committed bytes, with the mutants applied by the frozen
`census/round-86/c1-mutants.json` edits (each applied exactly once, verified):

```
== 1. the deciding clause, quoted from the counter's own refusal message ==
   (the forge expectation is deliberately wrong, so the counter prints `why`)
   FORGE NF-W item=I85R class=MOVED expect=MISMATCH got=REFUSED match=no class=MOVED why=census-in-tree target is not a wave capture keeping the token's full path suffix
   FORGE NF-Y item=I86S class=MOVED expect=MISMATCH got=REFUSED match=no class=MOVED why=own-round-tree target is neither the token's own path nor a wave capture keeping the token's suffix
== 2. one row per clause: which mutant turns which row green ==
   FORGE NF-W item=I85R class=MOVED expect=REFUSED got=MOVED match=no      <- under c7-census-in-tree
   FORGE NF-Y item=I86S class=MOVED expect=REFUSED got=REFUSED match=yes
   FORGE NF-W item=I85R class=MOVED expect=REFUSED got=REFUSED match=yes  <- under m14-short-shape
   FORGE NF-Y item=I86S class=MOVED expect=REFUSED got=MOVED match=no
== 3. the same mutants on the r85 47-row population: neither row is there ==
   SUMMARY rows=47 mismatches=0 accepted=0 refused_true=0 errors=0        <- c7-census-in-tree
   SUMMARY rows=47 mismatches=0 accepted=0 refused_true=0 errors=0        <- m14-short-shape
== 3b. and on the r86 49-row population, where both rows are ==
   ROW NF-W where=fixture rev=R9 item=I85R class=MOVED expect=REFUSED/- got=MOVED rc=1 match=no
   SUMMARY rows=49 mismatches=1 accepted=1 refused_true=0 errors=0        <- c7-census-in-tree
   ROW NF-Y where=fixture rev=R9 item=I86S class=MOVED expect=REFUSED/- got=MOVED rc=1 match=no
   SUMMARY rows=49 mismatches=1 accepted=1 refused_true=0 errors=0        <- m14-short-shape
```

Each mutant turns exactly one row green and leaves the other refused, and each is a no-op on the r85 population. That
is the sense in which each row reaches EXACTLY ONE clause: NF-W is bound to the census-in-tree branch and to nothing
else in the mutant set; NF-Y is bound to the short-shape guard and to nothing else.

**What this does and does not certify.** It does what the r85 section said a row must do: it binds one clause of the
counter's rule, and the binding is now measured rather than asserted. It does not certify the counter's whole rule.
The population gains two rows and the mutant set two members; the five guards r85 A4 named as still unrowed (m12, the
m14 neighbours, m16, m17) stay unrowed and are carried again, and the r86 preregistration's own stated limits say so.
NF-W and NF-Y are synthetic fixture rows: the lane really holds the shapes (r85 S85ScoutShapes) but no real ledger
row moves those two files, so the rows prove the rule's verdict, not that the lane ever made the move.

## Gate

- Destination: `corpus/knowledge/own-tree-pointer-binding.md`, a NEW section appended after "A shadowed clause is not
  an unbound clause (r85)". It replaces nothing; the r85 section stands as written.
- The heading is "Grounding an unbound clause: the row is the work (r86)", continuing the file's r83 → r84 → r85
  sequence. The r85 section's own conclusion ("a clause with no row is not certified whether or not it is reachable")
  is the premise this section discharges, and the two rows are named with the clause each binds.
- The file's front matter (`source:`, `verified-at:`, `recheck:`) is the L1's to update: this draft does not touch it,
  and it names no new source row. The sources the section leans on (S315/S316/S317 for the stat-cache ground, S337 and
  S340 for the mutation-testing ground) are already admitted in `corpus/SOURCES.md`; the C1 section needs no new row.
- Every pointer resolves to a committed path and line number at lane base `2acbbfc8`, except the two files under this
  seat's own directory (`.ufo/waves/round-86/w1/S86Scribe/`), which are this seat's draft instruments. I audited this
  mechanically: 45 `path:line` references, 0 unresolved. The two paths that do not exist in the lane
  (`census/round-84/w1/c1-after.txt`, `census/round-83/waves/c1-pointer-counter.py`) are FIXTURE-relative target paths
  and are labelled as such in the body.
- Pointer note for the L1, measured on the committed bytes: the r86 counter's lines are NOT the r85 counter's. In
  `census/round-86/c1-pointer-counter.py` the short-shape guard is at `:366-367` (`:351` is `OWNTREE_WAVE`), the
  basename clause is at `:401-402` (`:387` is `else "digest differs")`), the own-tree belt is at `:405-409`, the
  census-in-tree branch is at `:417-425`, and `_owntree_ok` is defined at `:354`. The r85 counter's numbers are `:352`
  (guard), `:387-388` (basename), `:391` (own-tree belt), `:403-411` (census-in-tree) and `:340` (`_owntree_ok`). A
  section whose `verified-at:`/`recheck:` name the r86 counter must cite the r86 counter's lines.
- The L1 landed its own r86 section for this file in the working tree while I was measuring; this draft was written
  against the committed bytes and is a draft for the L1 to merge, not a replacement for what the L1 has written.
- No claim here exceeds what the round's own receipts carry: the two arms are `census/round-86/records/c1-after.txt`
  and `census/round-86/controls/c1-before-r85-population.txt`; the per-ROW attribution (which row kills which mutant,
  and which clause decides each row) is not in either receipt, and is supplied here by this seat's own re-derivation,
  quoted above and reproducible with `probe-row-decides-clause.py`.
- Nothing outside the seat's own directory was written. The lane's `corpus/` files are unchanged.
