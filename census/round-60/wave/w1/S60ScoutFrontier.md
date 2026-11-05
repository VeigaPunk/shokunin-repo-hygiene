# S60ScoutFrontier — frontier-step reconnaissance (read-only)

Seat: leaf, read-only. No subagent dispatch, no lane/corpus/production edit, no git or jj mutation.
Lane HEAD at reconnaissance time: `1e8bfd87` = the round's declared base
`1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4`.

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -3
1e8bfd87 round-59 verifier spot-check (integrator, hyaku): non-author admit/reject
24a07fd8 round-59: retain committed measurements and prerequisite honest stop
18c82b53 round-59: correct stable assessment registry and add public selftest

$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --short 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4
1e8bfd87
```

Instrument state at that base (both claims' subjects are not yet in place):

```
$ ls -la tools/souji-freeze-check.py          -> -rwxr-xr-x 20924 Nov  3 14:51  (present)
$ grep -c 'substance' tools/souji-freeze-check.py
0
$ ls -la tools/souji-receipt-write.py
ls: cannot access 'tools/souji-receipt-write.py': No such file or directory
$ ls -la census/round-57/record-receipt.sh    -> -rwxr-xr-x 1596 Nov  3 20:22  (C2 base recorder, present)
```

Working tree at reconnaissance time (read-only observation; the L1 owns integration):

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain
?? census/round-60/
?? corpus/knowledge/freeze-record-substance-binding.md
?? corpus/lessons/round-60.md
```

Three untracked paths. **No `SKILL.md` change** — this matters for Q1's promotion verdict.

---

## 1. Which frontier row do C1 and C2 move (F1 vs F4), and would anything promote to Core?

### The frozen row texts (read, not paraphrased)

```
$ grep -n '^## Frontier' corpus/README.md
44:## Frontier
$ grep -n '^- F[0-9]' corpus/README.md
46:- F1 git-native housekeeping vs receipts — next: … remaining: keep-ref expiry unmeasured, and the r35 record itself is left as filed (its two counting defects are reported, not rewritten).
49:- F4 restorable quarantine — next: the receipt's per-item format and any staging-tool change remain operator decisions; r27 adds a pinned GLib reference writer and mechanism set, not a normative Souji format.
```

PROVINCE.md (`## Core / Frontier / Adjacent`, r12 block) defines the two rows as: **F1** = git's own
deleters (`maintenance --auto` worktree-prune, gc/reflog grace periods) acting on surfaces souji gates;
**F4** = restorable quarantine and file-system semantics (trash layout, same-device rename vs
copy+remove). Promotion rule, same file: "each row moves to Core only with an admitted
`corpus/knowledge/` entry **and a SKILL rule**".

### C1 — `--substance` arm on `tools/souji-freeze-check.py`: **F1 by filing, F1 by zero**

The in-flight entry that C1 would admit files itself under F1:

```
$ sed -n '3,4p' corpus/knowledge/freeze-record-substance-binding.md
ground: F1 — git-native housekeeping vs receipts (the binding a frozen claim's control receipt
needs before its red exit can be read as evidence, and the limit of that binding)
```

What C1 actually touches is the **receipt/gate evidence surface**, not F1's subject:

- F1's remaining item is the r35 record left as filed; its keep-ref expiry limb was measured at
  r30–r32 (`jj-keep-ref-expiry.md`, `jj-dropped-keep-object-lifetime.md`,
  `jj-abandoned-object-mtime-clock.md`). C1 touches neither.
- C1's criteria are the label-vs-bytes receipt rows: QUALITY Q99 (label grammar), Q116/Q117
  (receipt rev + `instrument_sha256` binding), Q120 (prefreeze control chronology). None is an F1 row.
- The one F1-primitive element is the `git merge-base --is-ancestor` strict-ancestor binding
  (S251, held by `corpus/knowledge/git-strict-descendant-relation-r40.md`) — a held F1 primitive
  *applied* to a receipt, not a new F1 measurement. The round-60 lesson draft says the same:
  "Re-opened, cells unchanged: … S251 `git merge-base --is-ancestor`".

**Verdict: C1 moves F1 by zero** (no row step, no new F1 measurement). It is Core gate calibration:
receipts are in `## Owns` ("receipt-gated removal"), and gate calibration is Core-adjacent tool work.
If the L1 keeps the `ground: F1` label, the claim must be stated as *the ancestry binding of a control
receipt*, not as housekeeping — the `os.replace` half of that entry belongs to F4's already-held
mechanism (see C2). The entry is still untracked, so the ground line is correctable before commit.

### C2 — `tools/souji-receipt-write.py`: **F4 by mechanism, F4 by zero**

The mechanism set is exactly what F4 already holds, and the round says so itself:

```
$ grep -n 'claims no new file-system ground' corpus/lessons/round-60.md
13: … This round applies held knowledge in a tool; it claims no new file-system ground.
$ sed -n '/S110/,+2p' corpus/lessons/round-60.md   # re-opened, cells unchanged
  S110 `rename(2)` (man-pages 6.19), S213 POSIX `rename()`, S214 POSIX `fsync()` — the three
  primitives F4's `origin-record-exclusivity-r28.md` already holds
```

Atomic temp-beside-output + `rename` + exclusive publish is F4's ground
(`origin-record-exclusivity-r28.md`, `quarantine-staging-no-copy.md`, S110/S213/S214). But F4's row's
*next* item is "the receipt's per-item format and any staging-tool change remain operator decisions".
C2 is a **receipt publish path** — not a quarantine layout, not an origin record, not a staging tool —
so the operator-decision item is untouched and no F4 knowledge entry is admitted.

**Verdict: C2 moves F4 by zero.** It is Core receipt-surface operability (`## Owns`: receipt-gated
removal), not quarantine ground.

### Promotion to Core: **none, and structurally impossible this round**

1. PROVINCE requires *entry + SKILL rule*; `git status --porcelain` shows no `SKILL.md` change.
2. The F1 map row's status is `frontier, entries held`; the r30/r31/r32 precedent is explicit —
   adding a measured F1 entry did not promote F1 ("One entry does not promote F1 to Core").
3. No F4 entry is written, and the round re-opens F4 primitives without adding a cell.
4. r56–r59 all closed with "no frontier promotion" (`corpus/lessons/round-58.md:32,67`;
   `corpus/lessons/round-59.md:10,55`); r60 is the same class of calibration/operability round.

Recommended wording for the round's lesson/report: *"C1 is Core gate calibration on the receipt
surface and C2 is Core receipt-surface operability; neither moves F1 or F4. No promotion, no new
file-system ground, no new F1 measurement."*

---

## 2. SOURCES census

```
$ bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji ; echo EXIT=$?
…
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
EXIT=0
```

- **Exit code: 0.** Output 67 lines = **1 `ok` row + 66 `W04` rows**, 0 `E*` error rows.
  Full output: `S60ScoutFrontier/census-validate.txt` (67 lines,
  sha256 `318cc45a8d20cbe5177294e21cdb0eef1127b69cf947a709ea1ffdebaea7cf04`).
- Every `W04` is the same class: `duplicate url … across scopes` (repeated primary URLs under
  different scopes, e.g. `git-scm.com/docs/git` for S049/S089/S125/S236/S237/S275). This is the
  known warning floor, not a schema error; r59 recorded 66 at its end, so the count is unchanged.
- **Registry rows: 211**, by both shapes, and 211 unique ids:

```
$ grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md
211
$ grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md
211
$ grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md | grep -oE 'S[0-9]+' | LC_ALL=C sort -u | wc -l
211
$ grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md | grep -oE 'S[0-9]+' | LC_ALL=C sort -u | tail -3
S285
S286
S287
```

- **Next free S-id: S288.** It is unregistered (`grep -c 'S288' corpus/SOURCES.md` → `0`;
  `S289` → `0`), and the round's own lesson draft already allocates it:
  "Rows added: A1 (S288) / B0 / C0; one rejection (S289). Registry 211 → 213 rows."
  So: **S288 is free now and is this round's admit; S289 is this round's reject; the first id free
  after round 60 is S290.**
- The in-flight entry already cites the id before the registry row exists
  (`corpus/knowledge/freeze-record-substance-binding.md:5` `source: S288 — Python os.replace
  atomicity (opened r60)`). That is index-row-before-file in reverse (entry before registry row);
  the L1 must land S288/S289 in the same commit as the entry, or the entry cites an unregistered id.

---

## 3. Mistake sweep (r56–r59 `## Mistakes`) — one class not captured by a QUALITY row

QUALITY currently holds **120 rows (Q1–Q120)**; the next row id is **Q121**.

```
$ grep -oE '^\| Q[0-9]+ ' corpus/QUALITY.md | grep -oE 'Q[0-9]+' | tail -8
Q113
Q114
Q115
Q116
Q117
Q118
Q119
Q120
$ grep -cE '^\| Q[0-9]+ ' corpus/QUALITY.md
120
```

**Uncaptured class → should become Q121.** r56 `## Mistakes` row 3
(`corpus/lessons/round-56.md:61`):

> "the shell's `set -e` and `set -x` persisted across tool calls and aborted a later cell, leaving a
> half-written absent-control file" — evidence: the cell's `+ git -C … cat-file …` trace inside the
> `controls/c1-absent`-precursor text; captured-by: "the trace itself in the cell output";
> fix: "shell options reset with `set +e +x` before each measurement cell".

Sweep showing no QUALITY row covers it:

```
$ grep -cE 'set -[ex]|shell option|half-written|option state|across tool calls' corpus/QUALITY.md
0
rc=1
```

The nearest rows are Q54 (snapshot locators) and Q119 (persisted expectations) — both match the word
"persist" in an unrelated sense; neither speaks to shell-option state crossing a measurement boundary.
Q113/Q120 cover *what a control receipt must say*, not *what state the measuring shell carries into
the next cell*. r57–r59 did not re-raise it.

Proposed row shape (for the L1 to author, not written here):

> **Q121** — Each measurement cell starts from an explicit shell state: `set +e +x` (and no inherited
> `errexit`/`xtrace`) before the command, so a failing earlier cell cannot abort or trace into the next
> one. A control artifact is accepted only if its bytes are the command's own stderr/rc, never a
> shell-trace prefix. | measurement cells, control files | re-run the cell with `set -e -x` left armed
> and require the artifact to be unchanged; the r56 trace (`controls/c1-absent` precursor) must not
> reappear | `corpus/lessons/round-56.md` Mistakes row 3 |

**Second uncaptured class (candidate Q122, lower priority).** r56 Mistakes row 4: "a matrix runner
dry-run failed with `manifest missing` because the fixture builder was not run into the runner's
`selftest/` subdirectory".

```
$ grep -cE 'manifest missing|selftest/ subdirectory|builder was not run|builder must be run' corpus/QUALITY.md
0
rc=1
```

Q118 is the only row that mentions a builder, and it is a different class (no deletion of a caller
subtree). This one is a *runner precondition* class — cheap to capture, but it is a seat-local
invocation slip rather than a corpus-wide hazard, so Q121 is the stronger first row.

Captured classes confirmed for contrast: r56 row 1 over-hide → Q111/Q114; r56 row 2 relabel →
Q112/Q113; r57 row 1 miscount → Q109; r58 row 1 awk-per-file counter → Q10 (the lesson's own
`captured-by`); r59 row 1 comparator-as-evidence → Q119; r59 row 2 vacuous chronology → Q120.
One partial capture, disclosed rather than counted: r57 row 2 (a `--file` source census over a
corpus-only snapshot produced two false `E11` rows) is *adjacent* to Q103's "a count taken in one mode
is not a count of the other", but Q103 is scoped to landing-gate receipts naming `--round`/`--rev`/
`--fleet-root`, not to a census over an unextracted tree — so the r57 class is only half-captured and
is the third candidate row, behind Q121/Q122.

---

## 4. `shokuknow/merge/souji/` and `considerthese/` presence, and what a future round could adopt

```
$ ls -la /home/vgpnk/Projects/shokuknow/merge/souji/
MERGE-REPORT.json   MERGE-REPORT.md   SOURCES.append.md   knowledge/     (all Oct 24 23:33)
$ ls -d /home/vgpnk/Projects/shokunin/souji-shokunin/considerthese/
ls: cannot access '…/considerthese/': No such file or directory        (rc 2)
$ ls -d /home/vgpnk/Projects/shokunin/considerthese
ls: cannot access '…': No such file or directory                       (rc 2)
```

- **`considerthese/` is absent** from the lane root and from the fleet root (rc 2 both) — consistent
  with r58/r59 ("considerthese/ does not exist in this lane"). Nothing to adopt from it.
- **`/home/vgpnk/Projects/shokuknow/merge/souji/` is present** (a staged `corpus-expansion-1` bundle;
  it wrote nothing into the lane). Not adopted this round (r46 mass-id-drift hold retained;
  `corpus/lessons/round-60.md` Gate states the same).

Bundle inventory:

```
$ python3 -c "… MERGE-REPORT.json …"
lane 'souji'
accepted 134
refused list 0
entries list 68
existing_rows 108
renumbered list 0
first_id 'S109'
$ ls …/merge/souji/knowledge/corpus/knowledge/ | wc -l
68
$ grep -cE '^\| *S[0-9]{3,} *\|' …/merge/souji/SOURCES.append.md
134
$ grep -oE '^\| *S[0-9]{3,}' …/SOURCES.append.md | grep -oE 'S[0-9]+' | LC_ALL=C sort -u | sed -n '1p;$p'
S109
S242
```

**What a future round could adopt (three items, in cost order):**

1. **58 knowledge entries the lane never integrated** — bundle-only files:

```
$ LC_ALL=C comm -23 <(ls …/merge/souji/knowledge/corpus/knowledge/ | LC_ALL=C sort) \
                     <(ls souji-shokunin/corpus/knowledge/ | LC_ALL=C sort) | wc -l
58
$ … by round suffix: r23:2 r24:5 r25:4 r26:5 r27:3 r28:9 r29:4 r30:4 r31:3 r32:2 r33:4 r34:4 r35:3 r36:5
                     + quarantine-staging-no-copy.md (unsuffixed)
```

Rough ground split of those 58: 31 name git/prune/fleet/reclamation/count-objects (F1-shaped),
4 name quarantine/origin-record/trash (F4-shaped), the rest are duplicate/near-duplicate (F3) and
community-literature rows. Full list: `S60ScoutFrontier/merge-not-in-lane.txt`
(58 lines, sha256 `fa7a36cb99f4778ee06cc7a3619d4b3925e2983f51bee9e73e520065fddb97d7`).
**Caveat a future round must handle:** these are r1–r11-era entries; several restate ground the lane
has since re-measured (e.g. `duplicate-verdict-identity.md` exists in both trees but the bundle copy is
the r1 draft). Adoption is *review-then-append with supersession*, never a bulk copy.

2. **The 134 staged SOURCES rows — but they cannot be appended as-is.** The bundle's id space
   `S109–S242` now collides with the live registry (211 rows through S287). `renumbered` is empty
   and `first_id` is S109, so a future round must renumber all 134 rows into S290+ (or re-derive the
   ids) before appending. The row *shape* is compatible — both sides are 11 columns:

```
$ grep -E '^\| *S28[0-9] ' corpus/SOURCES.md | head -1 | awk -F'|' '{print NF-2" columns"}'   -> 11 columns
$ grep -E '^\| *S1[0-9]{2} ' …/SOURCES.append.md | head -1 | awk -F'|' '{print NF-2" columns"}' -> 11 columns
```

3. **`MERGE-REPORT.md`/`.json` as the audit trail** — `accepted 134 / refused 0` means there are no
   curated rejections to inherit, so the bundle carries no rejection knowledge; a future round must
   re-open at least the F1/F4-shaped rows against current sources rather than trust the staging verdict.

**Do not adopt this round.** Round 60's Gate already records the non-adoption; this section is the
inventory for a later operator-authorized round only.

---

## Deliverables and limits

Delivered (this seat, absolute paths):

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-60/w1/S60ScoutFrontier.md` (this file)
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-60/w1/S60ScoutFrontier/census-validate.txt`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-60/w1/S60ScoutFrontier/merge-not-in-lane.txt`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-60/w1/S60ScoutFrontier/SHA256SUMS`

Nothing was written to `tools/`, `tests/`, `census/`, `corpus/`, `SKILL.md`, `SCORECARD.md`, `LOG.md`,
`PROVINCE.md`, the fleet repo or a sibling lane. No git or jj mutation was run; every git call was
`log`/`rev-parse`/`status`/`cat-file` read-only. No `agent://all` message. No subagent dispatched.
Scratch `/fast/scratch/hyaku/souji-r60/S60ScoutFrontier/` removed after the receipts were copied.

Named limits of this reconnaissance:

- The F1/F4 verdict is a **reading of the map rows and PROVINCE text at `1e8bfd87`**, not a measurement.
  It says where the claims land, not whether they are true.
- The `ground: F1` line I quote is from an **untracked draft**; it can change before the L1 commits it.
  My verdict is conditional on that line only for the *label*, not for the zero-step finding.
- The census validates the registry's internal consistency; a `W04` warning is not a claim that the
  duplicate URL is wrong for its scope, and `ok` is not a source-quality verdict.
- The 58-file adoption list is a **name diff against the lane tree**; it does not establish that a
  bundle entry is uncited, superseded or still true.
- The Q121/Q122 proposals are unrun: no fixture exists and no counter was written. They are row
  candidates, not captured criteria.
