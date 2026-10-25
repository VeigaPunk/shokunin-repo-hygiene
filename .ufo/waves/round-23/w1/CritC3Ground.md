# CritC3Ground — does the C3 coverage credit sit on ground the lane did not hold?

## Status

STATUS: PARTIAL — entry 1 (repo-size census instruments) is honest and does add ground the lane did
not hold; the *claim* is not: its before-state quotes a row the corpus declares superseded, its
frozen counter names an entry path this round's own dispatch will not produce, and two entries buy
one new surface. Verdict: **credit-overclaimed**, repairable by re-sizing before the after-run.

Revision under test: `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` (lane base, `git rev-parse HEAD`).

## Evidence

E1 — the lane's own counter says F2 has an entry, at base:

```
$ python3 census/round-13/count-claims.py 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd
{"F2_entry": 1, "admitted_entries": 7, ..., "sources": 114, ...}
```
derivation, `census/round-13/count-claims.py:48`:
`F2_entry=int("corpus/knowledge/git-repo-structure-readonly.md" in paths)`

E2 — the row the prereg quotes is dead by the corpus's own declaration:

- `corpus/README.md:40` — the r12 F2 row, status cell "frontier, no entry (r12 candidate deferred ..."
- `corpus/README.md:64` — `## Round 13 current coverage (supersedes the r12 F2 row)`
- `corpus/README.md:68` — "bounded structure-census capability acquired; wider size attribution remains frontier"
- `corpus/README.md:3-4` — "Index rows are claims — write the row when the file exists, not before."
- corroborated independently by a sibling seat, `w1/ScribeReadme.md:257-260`

E3 — F2 already governs a surface in SKILL and PROVINCE:

- `SKILL.md:245` — `## Repository structure census (F2, bounded r13 capability)` (rule, decision table, checklist)
- `PROVINCE.md:66-68` — F2 names `count-objects` among its surfaces; "unreachable-object census remain frontier"
- `corpus/SOURCES.md:176` (`## Leads (unopened)`) already filed "git-rev-list(1) `--disk-usage`; git-count-objects(1) `-vH`"

E4 — the instruments the entries add are absent from `corpus/knowledge/`:

```
$ grep -rnE 'count-objects|fsck|lost-found|garbage' corpus/knowledge/
corpus/knowledge/jj-colocation-receipts.md:84:  ("garbage collection" prose only)
```

E5 — installed-man bytes for entry 1's consequences (host git 2.56.0, `MANWIDTH=2000 man git-fsck`):
line 54 "Write dangling objects into .git/lost-found/commit/ or .git/lost-found/other/, depending on type.";
line 19, under **OPTIONS** for `<object>...`: "If no objects are given, git fsck defaults to using the index file, all SHA-1 references in the refs namespace, and all reflogs".
`man git-prune`: "Note that unreachable, packed objects will remain." and `-n, --dry-run`
"Do not remove anything; just report what it would remove". `man git-count-objects:28`
"the number of files in the object database that are neither valid loose objects nor valid packs".

E6 — entry 2's source-code claim is true; I opened it:
`https://raw.githubusercontent.com/git/git/v2.56.0/path.c` — `common_list[]` at :98,
`{ 1, 1, 1, "logs" }`, `{ 1, 0, 0, "logs/HEAD" }`, `{ 1, 0, 1, "gc.pid" }`, `{ 0, 1, 1, "refs" }`;
`ignore_garbage:1` field at :91, read at :377.

E7 — the staged fleet measurement is real, byte-for-byte (digest matches the staged `c2df19ee…`):

```
$ sha256sum /home/vgpnk/Projects/shokuknow/lanes/souji/round3/evidence/r24-fleet-garbage-census.out
c2df19eebf0506c56d925f1e33e8756d073a232d1cc291b141c633269d432b05
# count: 7988 / size: 112352 / in-pack: 10338 / packs: 1 / size-pack: 13857 / garbage: 0
```

E8 — the frozen counter's blindnesses, read from `tools/souji-gate-check.py`: `:126-129` rejects only
`check5-dangling-source` when `sid not in known` — a colliding id resolving to a *different document*
passes; `:42,:88` accept any `LOCATOR_RE` token without checking the quote is in that section;
`:116` counts `quote_rows` only from Gate lines, so body-prose attributions are untested. Census half
is green before data: `bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
→ `souji ok .../corpus/SOURCES.md`, rc=0 at base (only pre-existing `W04` duplicate-url warnings).

E9 — registry state at base: 114 rows, max `S114`; `S112`=gio(1), `S113`=GLib `g_file_trash`,
`S114`=statx(2) — the r22 quarantine-origin rows.

E10 — the round's dispatch and its drafts, as landed in `w1/`:

- `w1-spec.json` item 12 → draft at `corpus/knowledge/count-objects-garbage-readings-r25.md`; rule
  "this lane holds no measured fleet garbage census of its own, so the entry must NOT claim one"
  and "the staged S134 own-work row is not adoptable (the evidence lives outside this repo)".
- `w1-spec.json` item 13 mints "S115 git-count-objects(1), S116 git-fsck(1), S117 git-prune(1)",
  plus `S118`/`S119` tier B for the JA/ZH pages.
- `w1/ScribeEntryRepoSize.md:1-4` cites S115/S116/S117; `w1/ScribeEntryGarbage.md` cites S118/S119 and
  its Gate REJECTs S134 and the staged "same reading" sentence.
- `w1/ScribeEntryGarbage.md` Finding 1 records "a path conflict between this item's filename and the frozen C3 counter".

## Findings

1. **The claim's before-state is a stale quote of a superseded row** (`preregistration.txt` C3 theme:
   "the lane's only frontier row with NO entry (corpus/README.md F2: 'frontier, no entry')").
   `README.md:64` declares that row superseded, `README.md:68` is the live status, and the lane's own
   counter reports `F2_entry: 1` at base (E1). Calibration-class defect on the round's *lowest*
   non-retired axis — the axis C1 exists to repair — and no frozen key covers it: K2 scans `LOG.md`
   Round22 attempt2 4-tuples, K3 scans README/lesson slice tallies, so a claim premise quoting a dead
   README row passes C1's instrument silently.

2. **(1) Does the lane already hold this ground?** Split, and the split is the whole claim.
   - The *ground* (F2) is held: `corpus/knowledge/git-repo-structure-readonly.md:1-46`, `README.md:68`,
     `SKILL.md:245`, `PROVINCE.md:66-68`.
   - The *sub-surface* is not: E4 (zero `count-objects`/`fsck`/`lost-found` hits in `corpus/knowledge/`),
     and `PROVINCE.md:68` names it frontier. `SOURCES.md:176` had already filed `git-count-objects -vH`
     as an unopened lead, so entry 1 closes a lead the lane itself named.
   - Honest delta: F2 entries **1 → 3**, admitted entries **7 → 9** — not "no entry → entries".

3. **(2) Consequence, or restatement?** Entry 1 adds actable consequences the held entry does not
   carry: `git fsck --lost-found` writes blob *contents* under `.git/lost-found/` (E5); the
   `prune --dry-run` set is narrower than `fsck --unreachable` and narrower than what `gc` eventually
   frees; `alternate` must be read or shared-object bytes are double-counted. These fence exactly
   `README.md:47`'s named next step ("the /var/tmp write-safety fixture for git repo structure").
   Not a restatement.
   Entry 2, *as the round will land it*, adds **no new surface**: it is a community-corrobation note
   (tier B) that explicitly rejects the fleet figure and the staged "both languages read it the same
   way" sentence (`w1/ScribeEntryGarbage.md` Gate). Its remaining delta is a unit distinction
   (size vs count) and one negative finding. So two entries buy **one** new surface — under
   `AXES.md` coverage ("Fraction of the domain's real surfaces the skill governs (repo paths, tools, edge classes)")
   the second entry is adjacency, not coverage.

4. **(3) Is `garbage`-semantics ground held elsewhere?** No for `process-residue-observations.md` —
   that entry is F5 pid residue; `grep -niE 'garbage|count-objects|fsck|lost-found|unreachable'` over it
   returns nothing. Partially for `git-repo-structure-readonly.md`: `:19`
   "Use a separate read-only object census; reachable totals do not count unreachable objects."
   holds the *decision to need* an unreachable census and `:42-43` holds the boundary, but the token
   `garbage` appears nowhere in it. Field semantics new; the need held.

5. **(4) Does it draw credit from a frontier row without moving it to core?** Yes, and that is not what
   AXES.md's coverage definition credits. `AXES.md` signal: "PROVINCE.md lists every surface; none
   unexplored without reason". `PROVINCE.md:59-60`: "each row moves to Core only with an admitted
   `corpus/knowledge/` entry and a SKILL rule". C3 lands entries and **no SKILL rule, no tool**, so the
   row stays frontier and the surface stays ungoverned — an admission precondition, not a governed
   surface. The in-lane precedent that earned "capability acquired" (`README.md:68`) landed all three:
   entry + `tools/souji-repo-structure.sh` + `SKILL.md:245`.

6. **The frozen counter names an artifact this round will not produce** (`preregistration.txt` C3
   counter: `--entries ... corpus/knowledge/count-objects-garbage-semantics-r24.md`). The dispatch
   drafts `count-objects-garbage-readings-r25.md` and forbids the fleet claim the r24 artifact makes
   (E10). As frozen, C3's own predicate cannot pass: gate-check would report a missing entry. Either
   the round lands the re-scoped text at the prereg's pathname, or the substitution is disclosed
   **before** the after-run and both runs are recorded. Editing the counter after data is forbidden;
   reconciling now is pre-data and legitimate.

7. **The prereg's id re-pointing list is wrong in both directions.** It names `S134/S138/S139` for
   entry 2. `S134` is now *rejected* by the round's own Gate, and the ids actually adopted are
   `S118/S119` (E10); entry 1 adopts `S115/S116/S117`. The residual risk is narrow but real: if any
   staged text is landed as-is, `S113` (staged git-fsck) resolves in this lane to `S113`=GLib
   `g_file_trash` (E9), and gate-check cannot see it (E8) — the "wrong-source citation" class r22
   already recorded once. Derive the set by grepping each landed entry for `S\d{3}`, not from a list.

8. **Entry 1's landed draft carries a wrong-section locator.** `w1/ScribeEntryRepoSize.md:27`:
   "§ DESCRIPTION fixes the default head set: the index file, all SHA-1 references in the `refs`
   namespace, and all reflogs." On 2.56.0 that sentence is in OPTIONS under `<object>...` (E5 line 19);
   DESCRIPTION is one line. No Gate ADMIT quotes it, so check4 never tests it (E8) — it lands
   unchallenged. Fix: cite "§ OPTIONS, `<object>...`".

9. **Freshness ambiguity introduced, not repaired.** `git-repo-structure-readonly.md:2` is
   `verified-at: ... host Git 2.55.0` and `:46` still says "Treat it as pending recheck (routed to
   r17), not as re-confirmed"; the new entry is verified at 2.56.0 (`w1/ScribeEntryRepoSize.md:4`)
   with no mention of the older entry's debt. Two F2 authorities, divergent verified versions. No
   axis may be harmed; the fix is one disclosure line.

10. **No false provenance in the artifacts.** E7 (digest and numbers), E6 (path.c), and entry 1's
    quote of `README.md:47` all check out, and the drafts reject the two staged claims that do not
    (fleet figure, "same reading"). The overclaim is in the claim's sizing, not in the entries.

## Attack log

- **A1 — frozen C3 premise.** "the lane's only frontier row with NO entry" is contradicted by
  `F2_entry: 1` at the base revision from the lane's own committed counter (E1) and by `README.md:64`.
  Impacted axis: calibration. Correction: re-word the before-state to "F2 entry 1 → 3 on the
  frontier-named unreachable/size census"; predicate, target and key set stay frozen.
- **A2 — the frozen counter cannot falsify the claim it carries.** gate-check proves file admission
  and quote-verbatim, not added ground: it cannot see a colliding id resolving to another document
  (`:126-129`), cannot see a wrong-section locator (`:42,:88`), and ignores body prose (`:116`); the
  census half is rc=0 at base, i.e. non-discriminating (E8). A control that appends two entries
  restating `git-repo-structure-readonly.md` would pass. Not edited.
- **A3 — "two entries" is sized as a zero-base.** True counts 1 → 3 entries and 7 → 9 admitted; and
  one of the two entries (post-redraft) adds no surface. The claim inflates both the base and the
  surface count.
- **A4 — contract/dispatch identity divergence.** The frozen `--entries` path (`...garbage-semantics-r24.md`)
  will not exist; the dispatch produces `...garbage-readings-r25.md` (E10). The frozen counter and the
  round's own instruction cannot both be satisfied without a pre-data reconciliation. Not edited.

## Smallest safe correction

1. **Before the after-run**, reconcile the entry-2 path: land the re-scoped text at the prereg's
   pathname, or record the substitution explicitly with both gate-check invocations. Disclosing after
   data would be a counter change.
2. Re-word C3's before-state and record the true counts (F2 entries 1 → 3, admitted 7 → 9) from
   `count-claims.py` at base and at tip.
3. State in the lesson/report that C3 buys **one** new F2 surface (the read-only size/reachability
   instrument set) plus one community-reading note, and that the row stays frontier with no SKILL
   rule — do not let the report imply a Core move.
4. Fix the two locator/id items: `w1/ScribeEntryRepoSize.md:27` "§ DESCRIPTION" → "§ OPTIONS,
   `<object>...`"; and re-point by document over every `S\d{3}` token in the landed entries (S115-S119),
   never `S112-S114`.
5. Add the freshness reconciliation line for the 2.55.0 entry (`git-repo-structure-readonly.md:2,:46`).
6. If the round wants coverage credit on AXES.md's own definition, the SKILL rule is the missing half
   (`PROVINCE.md:59-60`); without it the honest verdict for C3 is admission-precondition, not coverage.

## Verdict

**credit-overclaimed.** The artifacts are honest and entry 1 adds ground the lane did not hold
(the count-objects/fsck/prune instrument set, and the `--lost-found` write trap the named write-safety
fixture must fence). The *claim* is not: it asserts a from-zero acquisition on a row the corpus
declares superseded, its own counter reports `F2_entry: 1` at base, it counts two entries as two
surfaces when the round's own Gate reduces the second to a source-reading note, its frozen counter
names a path the dispatch will not produce, and its counter can pass on restatement alone. Repair by
re-sizing and re-pointing before the after-run; no axis is harmed by the repair, and calibration is
repaired by it.

## Tooling

No installs or upgrades performed (pacman transactions paused host-wide; none needed — `git 2.56.0`
and its man pages were already present). No shell scratch directory created; no file written outside
this report. Read-only commands only: `git rev-parse`, `count-claims.py`, `sources-census.sh validate`,
`man`, `sha256sum`, `curl` (raw.githubusercontent.com). No subagent dispatched (leaf seat).
