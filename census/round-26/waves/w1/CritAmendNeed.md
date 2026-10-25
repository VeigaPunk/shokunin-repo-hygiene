# CritAmendNeed — does round 26 need amendment 3?

## Status

STATUS: PARTIAL — all three holes are real, and they are not the same kind of hole. (a) R2's
neutral classes are undefined in the contract and the landed rule is unbounded (any unknown token is
neutral), but it **cannot be closed this round** without changing frozen fixture cases 3, 7 and 10,
which is forbidden. (b) net-new rows is the right *direction* (supersede is an appended correction
row, never an edit), but `row count 127 -> 132` is not an append-only predicate: it accepts
delete-1-add-6 and base-row rewrites, and the validator has no base revision. (c) Amendment 2 is
**necessary** and its Axes/Planned treatment is correct, but its enforcement sentence is
unsatisfiable for region 5 because item 5 itself mandates a mid-span edit; it also drops base
170-171 silently, carries no red-arm receipt, and is absent from LOG.md. Amendment 3 (text below)
is proposed for (b), (c) and a C3 scope disclosure; no predicate, target, case set or axis is
relaxed by any clause.

## Evidence

Lane moved throughout this review (`ba8b54b` -> `0c92c2e` -> `9a6e0f1` -> **`166baa1`**,
2026-10-25). Every number below was re-measured at `166baa1`; the tool and fixture blobs are
identical between `9a6e0f1` and `166baa1` (`git diff --stat 9a6e0f1 HEAD -- tools/... tests/...`
is empty), so the R2 probe outputs carry over unchanged.
Every behavioural claim below was produced from the **committed blob at a named revision**,
snapshotted to `/var/tmp/souji-r26-CritAmendNeed/`, never from the live worktree: at one point the
worktree copy of `tools/souji-axis-check.py` was 163 lines and crashed with
`ValueError: too many values to unpack` mid-edit, and `census/round-26/records/c3-after.tsv`
changed under me (three-line stdout with no fixture verdict -> `cases=12 ... FALSE-GREEN-REJECTED`
under a new `rev`). Scratch removed at end; nothing written outside this report.

Base derivation, `git show 0eca7c8:SCORECARD.md | wc -l` -> `254`; headings:
`1:#`, `9:## Axes`, `17:### Round 23 measurements`, `63:## Capabilities`, `95:## Planned`,
`138:## Saturation`, `167:## Retired`, `169:None.`, `170:`+`171:` empty, `172:Insert the table
below...`, `174:` fence open, `175:` fenced `### Round 24 measurements`, `217:Optional
same-landing correction`, `227:` fence close, `229:---`, `231:### Round 25 measurements`,
`241:### Round 25 append-only corrections`, `250:`-`254:` five bare `superseded by` lines.

C1 protected spans, base bytes searched in the tip `SCORECARD.md` as a byte substring:

| base span | what | at tip 166baa1 |
|---|---|---|
| 1-16 | title + `## Axes` table | PRESENT verbatim |
| 17-62 | Round 23 block | PRESENT verbatim |
| 63-94 | Capabilities | **ABSENT** |
| 95-137 | Planned | PRESENT verbatim |
| 138-169 | Saturation .. `None.` | PRESENT verbatim |
| 231-254 | Round 25 block + corrections + 5 `superseded by` lines | PRESENT verbatim |

Why 63-94 is absent (and only it): base line 92 is a byte-prefix of tip line 153 —
`base92_is_prefix_of_head153: True`, tail added = ` *(R3 dated 2026-10-25: the digest binds the
labelled file's committed bytes and the recorded argv label, not the executed program.)*`. Planned
bullets: base 2 lines matching `^- \*\*r2[45]` -> tip 4 (exactly the two payload bullets appended).
C1 counter at tip: `markers=0` / `headings=17 44 78`; C2: `grounded_f1=2` / `registry_rows=132`;
C3 counter: `axis_check_exit=0`, `cases=12 pass=12 control=FALSE-GREEN-REJECTED`, `fixture_exit=0`
(all four run live at `166baa1`).

C2 registry is a pure append at the tip:
`git diff --numstat 0eca7c8 166baa1 -- corpus/SOURCES.md` -> `5	0`; deleted lines `0`; added ids
`S128 S129 S130 S131 S132` in that order. The two admitted entries cite only `S128`-`S132`
(`grep -oE 'S1[0-9]{2}'` over both entry files), so no base row's `used-by` needs to change.

R2 probe on the tip blob (a second claim on `calibration` with `bookkeeping-file` is present in each
prereg so R3 is satisfied and only R2 can fire):

```
surface-class: measurement       => claims=2 flags=0 rc=0
surface-class: receipt-binding   => claims=2 flags=0 rc=0
surface-class: bookkeeping-filez => claims=2 flags=0 rc=0   (unknown token)
surface-class: fixture-expansion => FLAG A R2 ... rc=1       (declared class still works)
duplicate lines (bookkeeping-file then measurement, axis operability)
                                 => claims=2 flags=0 rc=0
```
`git show 9a6e0f1:tools/souji-axis-check.py | grep -c NEUTRAL_SURFACES` -> `1`: the constant is
declared at `:41` and **never referenced**. The operative rule is `:122-123`:
`elif sc in SURFACE_AXIS and axis in OWNED_AXES and axis != SURFACE_AXIS[sc]`.

Frozen fixture at the tip: `cases=12 pass=12 control=FALSE-GREEN-REJECTED`, rc 0. K2 is met; the
`cases=11` reading belongs to `ba8b54b` and is void.

Prereg anchors: R2 `preregistration.txt:164-171`; fixture CLI and 12 cases `:177-191`; C1 kill rule
`:48-56`; C2 K3 `:110-113` and kill rule `:130-136`; amendment rules `:216-219`
("No predicate, target, case set or axis may be relaxed after any seat has scored", `:218-219`).

Amendment 2 (`preregistration-amendment-2.txt`, committed `965b869` 14:17:59, before the first
after receipt at 14:29:52 - ordering is satisfied). Its commit contains exactly three files —
the amendment text, `assimilation/quarantine-slice`, `assimilation/slice-verdicts-r26.tsv` — and
**no receipt**. `LOG.md` has no round-26 section at all; only
`corpus/lessons/round-26.md:42` mentions it.

## Findings

1. **C3 R2 has an undefined, unbounded neutral namespace.** `preregistration.txt:164-171` names
   four classes and no neutral set. The tool ships `NEUTRAL_SURFACES = {"receipt-binding",
   "measurement"}` at `tools/souji-axis-check.py:41` (dead: one occurrence in the file) and instead
   treats *every* token outside `SURFACE_AXIS` as neutral (`:122`). Location of the defect: the
   predicate is nowhere pinned, so the artifact defines it, and the artifact is mid-flight editable.
2. **The primary reason (1) cannot be fixed now: the frozen case set depends on it.** Fixture cases
   3, 7 and 10 (`tests/fixtures/r26-axis-check.py:144,196,198,232`) use `surface-class: measurement`
   as filler and assert `exact_rules {R1}`, `exact_rules {R3}` and `flags=0` respectively. Any rule
   that flags an undeclared class adds an R2 to each and fails K2 (`12/12`). Closing the vocabulary
   is therefore a *case-set* change, forbidden post-data. This is the hole (a) asks about, and it is
   frozen in, not merely undefined.
3. **Duplicate `surface-class:` lines are silently last-wins.** `parse_prereg` assigns into a dict
   (`souji-axis-check.py:72`), so `bookkeeping-file` followed by `measurement` is checked as
   `measurement`. Probe above: `claims=2 flags=0`. A prereg can therefore look fully declared and
   still clear R2. No frozen case declares two `surface-class:` lines on one claim (scanned all 11
   base cases), so a duplicate-line flag would be strictly additive and case-compatible.
4. **C2 K3's row count is not an append-only predicate.** `preregistration.txt:111-112` fixes
   `127 -> 132`, and `census/round-26/c2-counter.sh` counts lines matching `^| S[0-9]{3,} |`. That
   count is unchanged by deleting one base row and adding six, and by rewriting any base row's
   cells. `sources-census.sh` accepts only `--root`, `--file`, `--today`
   (`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:10,72-73`); it has no `--rev`, so it
   cannot compare against `0eca7c8` either. The kill rule (`:130-136`) contains no base-bytes clause.
5. **Net-new is nonetheless the correct direction — verified.** The registry forbids edit-supersede
   in the immutable cells: "Original rows are immutable; S072–S078 supersede them with narrower
   claims" (`corpus/lessons/round-18.md:55`), and mutable cells are only `status`/`recheck`/`used-by`
   ("No old status/recheck/used-by changed.", same file). So a staged row cannot legitimately
   supersede by editing; a correction must be an appended row. The predicate is right in shape and
   insufficient in strength.
6. **Amendment 2's enforcement sentence is unsatisfiable for region 5.** It requires "the diff of
   each protected span against its counterpart in the post-edit file must be empty", while item 5
   itself mandates that the `blob-bound receipts (r23)` row carry "one appended dated R3 note" —
   an edit inside base line 92, i.e. inside span 63-94. Observed: 63-94 is the *only* protected span
   absent at the tip, and only because of that note. The seat that did the check already worked
   around it by excluding line 92 (`.ufo/waves/round-26/w1/c1-verify.md:52`, "line 92 carries R3
   note"). The workaround is right; the frozen sentence is wrong.
7. **Amendment 2 silently drops base lines 170-171.** Item 1-7 protect base 1-16, 17-62, 63-94,
   95-137 and 138-169, and the closing sentence calls "base lines 170-230" scaffold and deleted.
   Lines 170-171 are the two empty lines after `None.`; the claim's own background calls the
   scaffold "lines 172-228" (`preregistration.txt:30-32`). Content-neutral, but it is a narrowing of
   the original `1-171` protected region that the amendment does not declare as such.
8. **Amendment 2's Axes / Planned treatment is correct** (the question (c) actually asks). The Axes
   table lives entirely in protected region 1-16 (present verbatim); Planned additions are bounded
   to "exactly the two fenced r24/r25 planned bullets appended (fenced lines 225-226, verbatim)",
   the base Planned span 95-137 is present verbatim, and the bullet count moved 2 -> 4. Forbidding
   Axes changes and allowing the two planned bullets both hold mechanically.
9. **Amendment 2 carries no red-arm receipt and is not logged in LOG.md.** `:216-218` requires both.
   The nearest artifact to a red arm is a wave-report table row (`c1-verify.md:69`, literal recipe ->
   `17 50 204` FAIL), which is not a receipt and postdates the first green receipt `4453128`.
10. **Closure condition, not an amendment defect:** all three after receipts predate the landing tip
    (`c1-after` `rev=07f83e6`, `c2-after` `rev=e0f8dcd`, `c3-after` `rev=c5949013`, tip `166baa1`).
    Each must be re-issued at the final landing tip: their outputs are already identical there
    (`markers=0` / `headings=17 44 78`; `grounded_f1=2` / `registry_rows=132`;
    `claims=3 flags=0` / `cases=12 pass=12 control=FALSE-GREEN-REJECTED`).

## Attack log

Impacted axes:

- (a) **operability** (the instrument's measured capability) and **calibration** (the r25 misattribution
  class C3 was built to catch). No score move is claimed; the harm is that C3's counters can pass
  while the instrument is bypassable, so the claim's asserted coverage is wider than the artifact.
- (b) **coverage**: a row-count-only gate can lose or rewrite a registry row and still print 132 —
  exactly the history loss the coverage axis measures.
- (c) **calibration**: an enforcement sentence that cannot be satisfied converts C1's byte-diff claim
  into an unfalsifiable one — the C1 surface itself.

Attack 1 (a): declare `surface-class: measurement` on a claim whose changed bytes are a bookkeeping
file and whose issue is an operability reading; `claims=2 flags=0`. Even a fully declared draft can
be bypassed by repeating the line (`bookkeeping-file` then `measurement`). Not fixable this round
(finding 2). Smallest safe correction **is not an amendment**: the C3 claim must disclose the limit
(A3-3), and the vocabulary + cases 3/7/10 must be re-frozen together before data next round.

Attack 2 (b): delete base row `S109`, append `S128`-`S133`. Row count `127 - 1 + 6 = 132`; ids unique;
no malformed row; used-by paths still exist; `validate` exit 0. K3 passes while a base row is gone.
Smallest safe correction: A3-1, which is additive, has no case set, and is already green on the
present bytes (`5	0`, ids `S128`-`S132` in order).

Attack 3 (c): apply amendment 2 literally to the landed file — the enforcement step fails on region 5
by construction, so the only way to "pass" is to ignore the note item 5 demands. Smallest safe
correction: A3-2, which states the check the verifier actually ran.

## Proposed amendment 3 (text; stricter-only, to be committed before the final-tip receipts)

```
Souji round 26 — preregistration amendment 3 (2026-10-25, post-data, stricter/precision only)

Rule: no predicate, target, case set or axis is relaxed; every clause below is either an
added kill condition or a statement of the check already performed. Red-arm receipts
committed before any green after-data scored under this amendment; logged in LOG.md and
corpus/lessons/round-26.md.

A3-1 (C2, added kill condition). Append to C2's KILL RULE: "... or the registry diff
against the base is not a pure append: `git diff --numstat 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd
<tip> -- corpus/SOURCES.md` must print exactly two fields `5` and `0`; the deleted-line count
(`git diff -U0 <base> <tip> -- corpus/SOURCES.md`, lines beginning with a single `-`) must be
0; and the five added registry lines must be the rows S128, S129, S130, S131, S132 in
ascending id order, each a well-formed 11-column row. No base row line may be removed,
reordered or rewritten. Because both admitted entries cite only S128-S132, no base row's
mutable status/recheck/used-by cell may change this round either."
Basis: K3's count alone accepts delete-1-add-6 and base-row rewrites (finding 4); append-only
cannot be delegated to sources-census.sh, whose CLI has no base revision.

A3-2 (C1, precision; replaces amendment 2's final enforcement sentence). Regions are unchanged;
only the check is stated: "(i) regions 1, 2, 3, 4, 6 and 7 each occur exactly once,
contiguously and in the listed order. (ii) Region 5 is checked as base lines 63-91 plus base
lines 93-94, each occurring exactly once contiguously and in order, with base line 92
required to be a byte-prefix of exactly one tip line (the appended dated R3 note authorised
by item 5), and with exactly the two payload rows (base lines 213-214) immediately after
base line 94's tip occurrence and no other line between them and `## Planned`. (iii) The
deletion bound is the scaffold block base lines 172-227 and the separator base line 229;
base lines 170-171, 228 and 230 are empty lines whose presence is not constrained."
Basis: amendment 2 as written cannot be satisfied (finding 6) and leaves the 170-171 narrowing
undeclared (finding 7). No region is added or removed.

A3-3 (C3, claim-scope disclosure; counters and case set unchanged). Add to CLAIM C3:
"Recorded scope limit: `surface-class` tokens outside the five declared classes (including
`receipt-binding` and `measurement`) are axis-neutral, and a second `surface-class:` line on
one claim is overwritten by the last, so a claim can relabel its surface and clear R2. C3
does not claim to detect axis misattribution for undeclared class names, and the round
report must state this limit. Closing it requires re-freezing R2's class vocabulary together
with fixture cases 3, 7 and 10, which currently rely on `measurement` being axis-neutral,
BEFORE data in a later round."
Basis: findings 1-3. This narrows what C3 asserts; K1 (`claims=3 flags=0`) and K2 (12/12)
are unaffected and were re-measured at the tip.

A3-4 (evidence). Amendment 3 carries: a red receipt showing today's K3 accepts a rewritten
registry row (`a3-red-c2-append.tsv`), a red receipt showing region 5 fails the literal
amendment-2 sentence on the landed bytes (`a3-red-c1-span.tsv`), and green receipts for the
same two checks at the landing tip (`a3-green-c2-append.tsv`, `a3-green-c1-span.tsv`), plus
re-issued c1-after/c2-after/c3-after at the landing tip.

Amended by: L1 (SoujiR26).
```

Nothing here may be executed by this seat (read-only); the receipts are named for the L1.

## Threads

- (a) is reported as an ATTACK, not an amendment of the predicate, because every strengthening
  available breaks the frozen case set (finding 2). A3-3 is the honest mitigation.
- Implementation defects to fix next round, not this one: the dead `NEUTRAL_SURFACES` constant
  (`tools/souji-axis-check.py:41`) and the last-wins duplicate parse (finding 3).
- No tools installed or upgraded this run; no network access; no writes outside this file and
  `/var/tmp/souji-r26-CritAmendNeed/` (removed).
