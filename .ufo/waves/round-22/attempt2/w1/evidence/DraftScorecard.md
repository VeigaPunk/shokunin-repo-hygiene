# DraftScorecard — paste-ready bookkeeping text (round 22, attempt 2)

Draft only. Nothing here has been written to `SCORECARD.md` or `corpus/README.md`.
Frozen contract: `.ufo/waves/round-22/attempt2/preregistration.txt` (C1, C2).

Draft base = committed bytes at `5fdd5d54fdf5ca9e203e5ed65bcffb8712572447`; measured at the
lane's then-tip `c9f1fe3caf642dfe3a9e00de94caf1d4bf86503f` with the current scanner
(`tools/souji-declared-evidence.py` sha256 `65817d0d…f21448f4`):

    base SCORECARD.md (c9f1fe3)      assertions=60 resolved=60 skipped=38 mismatches=0
    drafted text over c9f1fe3        assertions=66 resolved=66 skipped=44 mismatches=0   exit 0

Counting command for every number below (from the lane root):

    python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md \
        --rev <paste tip> --format counts

The counter changed twice inside this round: `5fdd5d5` (instrument hardening, skip accounting
moves by one at unchanged classification) and `4a6ee90` (escaped-pipe cell split, which moves
one base class-B token out of a revision-named cell). Numbers are therefore always stated with
the scanner that produced them; see the dual before-measurement in Block 2.

---

## Block 1 — `## Capabilities` row (replace the row named `declared-evidence calibration audit (r22 attempt 2)`, line 74 at the base revision)

The row on disk still reads "parse a self-assessment file ... its fixtures reject the cheapest
always-zero control" and cites `S109–S114`, which are the C2 quarantine-theme registry rows,
not C1 evidence. Block 1 replaces it; it is not an append.

    | declared-evidence calibration audit (r22 attempt 2) | re-derive three declared-assertion classes in a self-assessment file from committed bytes at a named revision: (a) backticked repo-relative .py/.sh/.json/.tsv/.md/.txt paths, optional :<line> suffix, optional glob over tracked files, must exist in the tree at that revision; (b) bare 7–40-hex tokens in a revision-named cell must resolve with `git cat-file -e <token>^{commit}`; (c) a 64-hex digest beside exactly one backticked path must equal sha256 of that path's bytes at that revision. Read-only, git plumbing only, scratch under /var/tmp. Limits: one file per run (the C1 measurement is SCORECARD.md), those three classes only — other backticked spans are counted as `skipped` and not itemised, class C has no instance on that file, class B proves existence rather than measurement — and it proves neither authorship, command execution, nor the truth of un-tokenised prose, so it says nothing about bytes it does not read | `python3 -B tools/souji-declared-evidence.py --selftest` → 8/8, the always-zero control rejected as `FALSE-GREEN-REJECTED`; receipts `census/round-22/attempt2/declared-evidence-before.tsv` (3 mismatches at 4edb25d) and `SCORECARD.md` (0 mismatches at 5fdd5d5) | r22 |

Column shape: name | what it can now do | evidence pointer | first-working round. No universal
clause: one file, three classes, three named things it does not prove.

## Block 2 — `## Axes` calibration row (replacement, line 14 at the base revision)

The row landed at `ee1aef2` keeps its set-membership honesty but (i) quotes only
`mismatches=0` for the tip and `assertions=59 resolved=59 skipped=37` for `af73b8b`, while the
current scanner prints `60/60/38` at that tip, (ii) states "5 base tokens retired, 6 added"
where the measured multiset diff is 6 retired and 11 added under the current scanner, and
(iii) quotes the before receipt `56/53/33/3` without saying the current scanner re-derives
`55/52/33/3` at the same revision (the escaped-pipe fix). Block 2 keeps the row's verified
claims, fixes those three, and restores the explicit unproven wording for attempt 1.

    | calibration | 7 | R22 **attempt 2** C1 declared-evidence calibration (new instrument, bounded): the lane's own SCORECARD assertions are re-derived from committed bytes at a named revision. Base `4edb25dfe262515d0da63224bbba71e02e36cba5`: `assertions=56 resolved=53 skipped=33 mismatches=3` as the committed before receipt records it, `assertions=55 resolved=52 skipped=33 mismatches=3` under the current scanner (one class-B token left a revision-named cell when escaped pipes were split); this tip: `assertions=66 resolved=66 skipped=44 mismatches=0`. The assertion SET moved with the file (6 token occurrences retired, 11 added between the base and 5fdd5d5 under the current scanner), so this is a same-class before/after, not a same-set victory; 1 of the 3 repairs names a fleet file absolutely and therefore leaves class A rather than resolving inside it. Enum limits, named: command-embedded paths are skipped, class C has no instance on this file, skips are not itemised, class B proves existence not measurement. Attempt 1's strict-adequacy claim stays rejected-honest-stop and is **unproven**; it is not re-claimed, re-pinned or reworded. Score 7 unchanged; CritC1Predicate dissent on record. | `python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md --rev <tip> --format counts` → `assertions=66 resolved=66 skipped=44 mismatches=0`, exit 0; `--selftest` 8/8 incl. the always-zero control rejected; before receipt `census/round-22/attempt2/declared-evidence-before.tsv` | before 4edb25dfe262515d0da63224bbba71e02e36cba5; after = the commit carrying this row, the drafted text measured over c9f1fe3caf642dfe3a9e00de94caf1d4bf86503f | r22 attempt 2 |

Q10 notes:
- score column stays 7, so `## Saturation / stagnation` ("calibration 7") stays consistent.
  Raising it to 8 requires changing that sentence in the same commit.
- the counts line appears twice (prose and command cell) with the same string; change both or
  neither.
- "6 retired / 11 added" is a historical statement about two immutable revisions under a named
  scanner; it does not need updating when the tip moves again. The `66/66/44` line does.

## Block 3a — `corpus/README.md` coverage-map row (replacement, line 42 at the base revision)

Current text at the base revision:

    | F4 restorable quarantine, file-system semantics | frontier; layout held, staging primitive + record read side admitted r22 (see § Round22 attempt 2) | `knowledge/trash-spec-restorable-quarantine.md`, `knowledge/quarantine-same-filesystem-rename.md`, `knowledge/quarantine-staging-no-copy-r23.md`, `knowledge/quarantine-origin-record-fields-r24.md` |

`layout held` contradicts the same file's own r12 correction ("F4 still holds an admitted entry
(`knowledge/trash-spec-restorable-quarantine.md`)", lines 59–61) and its r12 ledger lines
88–90: the HELD entry is `quarantine-same-filesystem-rename.md`, not the layout entry.
Replacement:

    | F4 restorable quarantine, file-system semantics | frontier; layout entry admitted, r22 staging primitive and origin-record read side admitted, same-filesystem semantics entry HELD, record format + any staging tool change operator-owned (see § Round22 attempt 2) | `knowledge/trash-spec-restorable-quarantine.md` (layout, admitted), `knowledge/quarantine-staging-no-copy-r23.md` (S109–S111, no-clobber staging), `knowledge/quarantine-origin-record-fields-r24.md` (S112–S114 + S022, origin-record read side), `knowledge/quarantine-same-filesystem-rename.md` (HELD, no committed fixture) |

## Block 3b — `corpus/README.md` `## Frontier` F4 bullet (replacement, line 49 at the base revision)

Current text still presents the origin records as un-staged work:

    - F4 restorable quarantine — next: per-item origin records (trashinfo-style) and `mv --no-copy` staging are tool changes for the operator.

Replacement:

    - F4 restorable quarantine — next: staging is grounded by the two r22 entries (the no-clobber primitive; the record's original-path field), so what remains is the operator's decision on the record format and on adopting `renameat2`/`mv --no-copy` staging as a tool change; the lane holds no deletion authority.

Adoption facts behind blocks 3a/3b (measured this round):
`entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`, exit 0, for
`corpus/knowledge/quarantine-staging-no-copy-r23.md` (S109–S111) and
`corpus/knowledge/quarantine-origin-record-fields-r24.md` (S112–S114 + existing S022);
`--selftest` 9/9; registry `sources-census.sh validate` exit 0 with duplicate-URL warnings only;
registry rows `114` by the frozen `grep -cE` count.

## Block 4 — `## Planned` one-line pointer (append after the `r22 — declared calibration` bullet)

    - **r23 — starting point:** C1 covers `SCORECARD.md` only, so the next move is either the operator-owned F4 piece (origin-record format, any `mv --no-copy` staging tool change) if the operator rules, or the same counter extended to the lane's next declared surface, `corpus/README.md`, with its own before receipt. Certification stays OFF, K5 HELD.

---

## Recompute rule (mandatory before the paste commit)

Drafting is not measurement, and other seats edit the same file. Against the `5fdd5d5` base the
drafted text contributes +6 assertions (60 → 66: +7 token occurrences, −1 for the `af73b8b`
tip hash it replaces) and +6 skipped (38 → 44). Every token it adds resolves at any tip that
contains the cited paths and commits, so mismatches stay 0.

After pasting, run the counting command at the paste commit and put the printed line into both
places in Block 2. If it differs from `66/66/44/0`, another row or another scanner revision
changed the arithmetic: take the printed line, do not adjust by hand, and never leave a count
the counter does not print.

## Scratch provenance

`66/66/44/0` was produced by running the counter over a scratch copy of
`5fdd5d5:SCORECARD.md` with Blocks 1, 2 and 4 applied
(`/var/tmp/ds-cand/SCORECARD.md`, sha256 `b55034dbe962e73446373ffe5ce9ddbca571dcd1bef71b1b2d2191be8b2b410c`).
That path is scratch and may vanish; the four blocks above are the durable artifact.
