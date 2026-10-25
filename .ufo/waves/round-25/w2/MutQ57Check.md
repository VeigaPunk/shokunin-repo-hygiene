# MutQ57Check — Q57 counter attack (round 25, wave 2, mutation-tester)

## Status

STATUS: PASS — assignment executed; the three named controls each fail, the base is red, and
the **current lane tree is RED, not green** (integration incomplete under the checker's own
contract). Wrong-authority-table acceptance is confirmed as a silent limit. No lane file was
edited; scratch `/var/tmp/souji-r25-MutQ57Check/` created and removed.

## 0. Commands and revisions

- Lane HEAD: `6deb53561aace9aa14a399f88cf8150da4d4f4bd` (branch master). Working tree carries
  uncommitted W1 integration edits (pointer comments in both TSVs; superseded notes in
  round-24.md / SCORECARD.md; no note in LOG.md).
- Base: `a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe` (preregistration base).
- Checker (committed fixture): `tests/fixtures/r25-q57-check.sh`, sha256
  `05685780c7ffbd36891d5cbd1e1ce74309be2a32d1bea8077bc8053390a9021a`.
  Diff vs the W1 draft `q57-check.sh` (sha256 `a975edac…`) is cosmetic only (usage guard,
  `${id:-}`, quoted vars, printf) — no logic change.
- Invocation (frozen shape):
  `bash tests/fixtures/r25-q57-check.sh ROOT census/round-24/records/slice-verdicts.tsv
  .ufo/waves/round-24/assimilation/slice-verdicts.tsv corpus/lessons/round-25.md
  corpus/lessons/round-24.md:240 corpus/lessons/round-24.md:232:S118 LOG.md:1692
  SCORECARD.md:181`

## 1. Base a6d2d15 — RED (confirmed)

Copies of the five files extracted via `git show a6d2d15:<path>` into scratch. Output:

```
recount census/round-24/records/slice-verdicts.tsv: 8 accepted
NO-POINTER census/round-24/records/slice-verdicts.tsv
NO-POINTER .ufo/waves/round-24/assimilation/slice-verdicts.tsv
STALE corpus/lessons/round-24.md:240
STALE corpus/lessons/round-24.md:232:S118
STALE LOG.md:1692
STALE SCORECARD.md:181
q57=FAIL  (rc=1)
```

## 2. Current lane tree — RED (not green) [key finding]

Running the checker against the current working-tree bytes (copied into scratch, no edits):

```
recount census/round-24/records/slice-verdicts.tsv: 8 accepted
POINTS census/round-24/records/slice-verdicts.tsv -> corpus/lessons/round-25.md
POINTS .ufo/waves/round-24/assimilation/slice-verdicts.tsv -> corpus/lessons/round-25.md
STALE corpus/lessons/round-24.md:240
STALE corpus/lessons/round-24.md:232:S118
STALE LOG.md:1692
STALE SCORECARD.md:181
q57=FAIL  (rc=1)
```

Two concrete defects in the current tree (exact bytes):

1. The appended notes do not contain the mapping string `corpus/lessons/round-25.md`, which the
   checker requires (`grep -F "$mapping"` on the note line). Current note bytes:
   - `corpus/lessons/round-24.md:387`: "superseded by corpus/lessons/round-24.md:240; authority
     census/round-24/records/slice-verdicts.tsv; recount 8 accepted"
   - `corpus/lessons/round-24.md:388`: "superseded by corpus/lessons/round-24.md:232; authority
     census/round-24/records/slice-verdicts.tsv; recount S118 accepted"
   - `SCORECARD.md:250`: "superseded by SCORECARD.md:181; authority
     census/round-24/records/slice-verdicts.tsv; recount 8 accepted"
   None contains the mapping literal → `note` is empty → sites fall through to STALE.
2. `LOG.md` has no superseded note for its site at all: `grep -n 1692 LOG.md` → no matches.
   Site text (LOG.md:1692): "only), 4 rejected. Quarantine slice 8 rows: 7 accepted, 1
   unverifiable".

Implication: with the current bytes, Q57 is NOT green; the W1 scribe's green arm was run
against a constructed scratch copy, not against the lane tree. L1 must land compliant notes
(naming the mapping) and a LOG.md note before Q57 can be claimed green.

## 3. Compliant green construct — PASS (checker works when its contract is met)

Scratch copy of current bytes + mapping literal appended to the three notes + one LOG.md note
("superseded by LOG.md:1692; authority census/round-24/records/slice-verdicts.tsv; recount 8
accepted; mapping corpus/lessons/round-25.md"):

```
recount census/round-24/records/slice-verdicts.tsv: 8 accepted
POINTS ... -> corpus/lessons/round-25.md   (both TSVs)
SUPERSEDED corpus/lessons/round-24.md:240
SUPERSEDED corpus/lessons/round-24.md:232:S118
SUPERSEDED LOG.md:1692
SUPERSEDED SCORECARD.md:181
q57=PASS  (rc=0)
```

## 4. Controls — all three fail as designed

| Control | Mutant (sha256 before → after) | Detector result | Verdict |
|---|---|---|---|
| (a) remove one mapping pointer | table TSV line 11 drops `corpus/lessons/round-25.md` (`576fde11…` → `d0ac3e19…`) | `NO-POINTER census/round-24/records/slice-verdicts.tsv`, q57=FAIL | KILLED |
| (b) change S114 class | table TSV row S114 `accepted`→`refused` (`576fde11…` → `0fd41812…`) | recount `7 accepted, 1 refused`; STALE on 240/1692/181 (S118 site still SUPERSEDED, unaffected) | KILLED |
| (c) omit superseded citation | LOG.md note deleted (`d5ca59f7…` → `4c26e148…`) | `STALE LOG.md:1692`, q57=FAIL | KILLED |

## 5. Authority-table and explicit-site checks

- **Wrong authority table is silently accepted.** An impostor table (8 rows × class
  `accepted`, carrying the pointer comment) recounted `8 accepted` and the identical run
  printed `q57=PASS` (rc=0). The checker verifies agreement between the quoted sites and
  WHATEVER file is passed as TABLE; it never verifies the TABLE is the authority. A wrong
  table with the same recount and pointer passes. (Disclosed in the draft: "verifies
  agreement, not correctness".)
- **Swapping TABLE and DETAIL** (detail file as TABLE) fails — but only incidentally, because
  the detail file's column 2 recounts to `7 payload-absent, 1 register_class, 1 the`, which
  no site matches. There is no identity check.
- **Explicit sites only.** The SITE list is a manual enumeration. Sweep for other stale slice
  tallies found a second, unlisted stale quote in the same file as a covered site:
  `SCORECARD.md:182` "slice 7 accepted + 1 unverifiable (S118)" — no note, not on the SITE
  list. Adding `SCORECARD.md:182` to the sites makes even the compliant green construct fail
  (`STALE SCORECARD.md:182`). A new stale quote is missed until its site is added.

## 6. Other limits observed

- Note matching requires the exact `file:line` spelling and the mapping literal on the SAME
  note line; notes without the mapping are silently ignored (the current red cause).
- Sites are line-number positions (`awk NR==n`); if file lines shift, sites silently point at
  different text — no content anchor.
- Row-level sites (`file:line:ID`) can never AGREE when the quoted line retains a token of
  another class (e.g. S118 row mentions both `unverifiable` and `accepted`); they pass only
  via SUPERSEDED, by design.
- The checker does not verify the mapping text is consistent with the detail table (separate
  cross-table instrument).

## 7. Hygiene

No lane/sibling/fleet writes. Scratch `/var/tmp/souji-r25-MutQ57Check/` removed (verified).
No tools installed.
