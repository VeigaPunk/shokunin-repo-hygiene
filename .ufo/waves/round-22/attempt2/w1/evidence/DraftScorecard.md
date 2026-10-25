# DraftScorecard — paste-ready bookkeeping text (round 22, attempt 2)

Draft only. Nothing here has been written to `SCORECARD.md` or `corpus/README.md`.
Frozen contract: `.ufo/waves/round-22/attempt2/preregistration.txt` (C1, C2).
Draft base (committed bytes): `d6a75bad8129960bdb96874421298e3bf42aa8c4`
(`SCORECARD.md` sha256 `725e64458916306dfb951380cf3794b8473b7fa8ed740ccb4b884769991c4cc0`).
Base measurement at that revision: `assertions=58 resolved=58 skipped=36 mismatches=0`.
Drafted-text measurement (base + blocks 1, 2 and 4, scratch copy):
`assertions=65 resolved=65 skipped=40 mismatches=0`, exit 0.

Counting command for every number below (from the lane root):

    python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md \
        --rev <paste tip> --format counts

---

## Block 1 — `## Capabilities` row (replace the existing `declared-evidence calibration audit (r22 attempt 2)` row, line 74 at the base revision)

The row already on disk was added at `70af563` and cites `S109–S114`, which are the C2
quarantine-theme registry rows, not C1 evidence. Block 1 is a replacement, not an append.

    | declared-evidence calibration audit (r22 attempt 2) | re-derive three declared-assertion classes in a self-assessment file from committed bytes at a named revision: (a) backticked repo-relative .py/.sh/.json/.tsv/.md/.txt paths, optional :<line> suffix, optional glob over tracked files, must exist in the tree at that revision; (b) bare 7–40-hex tokens in a revision-named cell must resolve with `git cat-file -e <token>^{commit}`; (c) a 64-hex digest beside exactly one backticked path must equal sha256 of that path's bytes at that revision. Read-only, git plumbing only, scratch under /var/tmp. Limits: one file per run (the C1 measurement is SCORECARD.md), those three classes only — other backticked spans are counted as `skipped`, not verified — and it proves neither authorship, command execution, nor the truth of un-tokenised prose, so it says nothing about bytes it does not read | `python3 -B tools/souji-declared-evidence.py --selftest` → 8/8, the always-zero control rejected as `FALSE-GREEN-REJECTED`; receipts `census/round-22/attempt2/declared-evidence-before.tsv` (3 mismatches at 4edb25d) and `SCORECARD.md` (0 mismatches at d6a75ba) | r22 |

Column shape: name | what it can now do | evidence pointer | first-working round. No
universal clause: the sentence names one file, three classes, and three things it does not
prove.

## Block 2 — `## Axes` calibration row (replacement, line 14 at the base revision)

    | calibration | 7 | R22 **attempt 2** C1 declared-evidence calibration (new instrument, bounded): the lane's own SCORECARD assertions are re-derived from committed bytes at a named revision. Before at base 4edb25d: assertions=56 resolved=53 skipped=33 mismatches=3 (a fleet-relative pointer, an unnamed receipt, a path that never existed). After at the paste tip: assertions=65 resolved=65 skipped=40 mismatches=0. Membership differs at both ends: two base spans left the evidence role, the bare receipt was re-pointed to its committed path, and new committed pointers and revision tokens were added; skipped spans are counted, not verified. Limits: SCORECARD.md only, those three assertion classes only, git-only plumbing; no authorship, command-execution or prose-truth claim follows. Attempt 1 was judged rejected-honest-stop for a strict-adequacy claim its evidence could not carry; that claim stays **unproven** and is not re-claimed, re-pinned or reworded, its receipts staying historical. Score move 7→8 proposed, closure decides. | `python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md --rev <paste tip> --format counts` → `assertions=65 resolved=65 skipped=40 mismatches=0`, exit 0; `--selftest` → 8/8 with the always-zero control rejected; before receipt `census/round-22/attempt2/declared-evidence-before.tsv` | before 4edb25dfe262515d0da63224bbba71e02e36cba5; after = the paste commit, the drafted text measured over d6a75bad8129960bdb96874421298e3bf42aa8c4 | r22 attempt 2 |

Q10 notes for this row:
- score column stays 7, so `## Saturation / stagnation` ("calibration 7") stays consistent.
  If closure raises the row to 8, that sentence MUST be changed in the same commit; the row
  text itself already carries "Score move 7→8 proposed, closure decides", so no number in
  the row contradicts the table.
- the counts line appears twice (prose and command cell) with the same seven-figure string;
  change both together or not at all.
- "before" numbers are historical and already committed as a receipt
  (`assertions=56 resolved=53 skipped=33 mismatches=3` at `4edb25d`).
- the "after" numbers are measured on the drafted text, because any revision token added to
  the row creates one more class-B assertion: the same row measured 62 on the `3216c19` base,
  63 once the paste-tip hash was added, and 65 on the `d6a75ba` base, which already carries
  two more class-B tokens from other seats. Do not copy a count from an earlier draft.

## Block 3a — `corpus/README.md` coverage-map row (replacement, line 42 at the base revision)

Current text at the base revision:

    | F4 restorable quarantine, file-system semantics | frontier; layout held, staging primitive + record read side admitted r22 (see § Round22 attempt 2) | `knowledge/trash-spec-restorable-quarantine.md`, `knowledge/quarantine-same-filesystem-rename.md`, `knowledge/quarantine-staging-no-copy-r23.md`, `knowledge/quarantine-origin-record-fields-r24.md` |

`layout held` contradicts the same file's own r12 correction ("F4 still holds an admitted
entry (`knowledge/trash-spec-restorable-quarantine.md`)", lines 59–61) and its r12 ledger
lines 88–90: the HELD entry is `quarantine-same-filesystem-rename.md`, not the layout entry.
Replacement:

    | F4 restorable quarantine, file-system semantics | frontier; layout entry admitted, r22 staging primitive and origin-record read side admitted, same-filesystem semantics entry HELD, record format + any staging tool change operator-owned (see § Round22 attempt 2) | `knowledge/trash-spec-restorable-quarantine.md` (layout, admitted), `knowledge/quarantine-staging-no-copy-r23.md` (S109–S111, no-clobber staging), `knowledge/quarantine-origin-record-fields-r24.md` (S112–S114 + S022, origin-record read side), `knowledge/quarantine-same-filesystem-rename.md` (HELD, no committed fixture) |

## Block 3b — `corpus/README.md` `## Frontier` F4 bullet (replacement, line 49 at the base revision)

Current text at the base revision is stale — it still presents the origin records as
un-staged work:

    - F4 restorable quarantine — next: per-item origin records (trashinfo-style) and `mv --no-copy` staging are tool changes for the operator.

Replacement:

    - F4 restorable quarantine — next: staging is grounded by the two r22 entries (the no-clobber primitive; the record's original-path field), so what remains is the operator's decision on the record format and on adopting `renameat2`/`mv --no-copy` staging as a tool change; the lane holds no deletion authority.

Adoption facts behind blocks 3a/3b (measured this round, gate counter below):
`entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`, exit 0, for
`corpus/knowledge/quarantine-staging-no-copy-r23.md` (S109–S111) and
`corpus/knowledge/quarantine-origin-record-fields-r24.md` (S112–S114 + existing S022).

## Block 4 — `## Planned` one-line pointer (append after the `r22 — declared calibration` bullet)

    - **r23 — starting point:** C1 covers `SCORECARD.md` only, so the next move is either the operator-owned F4 piece (origin-record format, any `mv --no-copy` staging tool change) if the operator rules, or the same counter extended to the lane's next declared surface, `corpus/README.md`, with its own before receipt. Certification stays OFF, K5 HELD.

---

## Recompute rule (mandatory before the paste commit)

Drafting is not measurement. If any other seat changes `SCORECARD.md` between this draft and
the paste, the base counts move and the row's two strings go stale. The drafted text adds a
fixed assertion set, so the invariant is:

- assertions: base + 7 (three class-A pointers: `corpus/README.md`, `SCORECARD.md` ×2;
  four class-B tokens: `4edb25d` ×2, `d6a75ba`, `d6a75bad8129960bdb96874421298e3bf42aa8c4` — all
  of which resolve at any tip that contains the cited paths);
- skipped: base + 4 (three non-path spans in block 1, one in block 4);
- mismatches: 0, exit 0 — unless the paste differs from these blocks.

At the base revision that yields `65/65/40/0` (measured, exit 0). After pasting, run the
counting command at the paste commit and put the printed line into both places in block 2.
If the printed line differs from the arithmetic above, the pasted bytes differ from this
draft: fix the text, do not adjust the numbers.

## Scratch provenance

The 65/65/40/0 line was produced by running the counter over a scratch copy of the base
revision's `SCORECARD.md` with blocks 1, 2 and 4 applied
(`/var/tmp/ds-cand/SCORECARD.md`, sha256 `3581b87a6da3961e66070b29b7436ca23fbdfc2e5ea0a6bb414df6119e411c4d`).
That path is scratch and may vanish; the drafted bytes are the four blocks above, and the
counter output is reproducible from them.
