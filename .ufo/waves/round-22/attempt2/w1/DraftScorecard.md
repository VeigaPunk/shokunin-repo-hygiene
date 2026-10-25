STATUS: PASS

# DraftScorecard — bookkeeping text for round 22 attempt 2 (scribe seat)

Drafted, not landed. This seat wrote only this report and
`.ufo/waves/round-22/attempt2/w1/evidence/DraftScorecard.md` (plus `/var/tmp` scratch for
measurement). No byte of `SCORECARD.md`, `corpus/README.md`, the lane index, `.ufo/state`,
`MANIFEST.json`, fleet `templates/`/`scripts/`, or any sibling repo was written.

Frozen contract read first: `.ufo/waves/round-22/attempt2/preregistration.txt` — C1's counter,
three assertion classes, five fixtures plus the do-nothing control and kill rule, and C2's
per-entry predicate, slice predicate and kill rule are used exactly as frozen. No axis was
re-scoped, no verdict invented; attempt 1's strict-adequacy claim is treated as unproven
throughout the drafted prose.

---

## 1. Executed measurements

### 1.1 C1 counter across the round's revisions

    python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md \
        --rev <REV> --format counts

    REV        scanner state                              printed line                                      exit
    4edb25d    pre-hardening / pre-split                   assertions=56 resolved=53 skipped=33 mismatches=3  1
    4edb25d    current (65817d0d, post-split)              assertions=55 resolved=52 skipped=33 mismatches=3  1
    70af563    pre-hardening                               assertions=57 resolved=56 skipped=37 mismatches=1  1
    3216c19    pre-hardening                               assertions=56 resolved=56 skipped=36 mismatches=0  0
    d6a75ba    pre-hardening                               assertions=58 resolved=58 skipped=36 mismatches=0  0
    af73b8b    hardened (5fdd5d5), pre-split               assertions=59 resolved=59 skipped=37 mismatches=0  0
    5fdd5d5    current                                     assertions=60 resolved=60 skipped=38 mismatches=0  0
    c9f1fe3    current                                     assertions=60 resolved=60 skipped=38 mismatches=0  0

The scanner itself changed twice inside this round — `5fdd5d5` (instrument hardening: skip
accounting moves by one at unchanged classification) and `4a6ee90` (escaped-pipe cell split).
Consequence worth L1's attention: the committed before receipt
`census/round-22/attempt2/declared-evidence-before.tsv` records `56/53/33/3` and is no longer
reproducible by the current tool, which prints `55/52/33/3` at the same revision; the dropped
token is one class-B `41553adb…` that no longer sits in a revision-named cell after the split.
`mismatches=3` is unchanged, so C1's before condition (`M_before > 0`) holds either way.

At `70af563` the single mismatch was `SCORECARD.md:83`, class A,
`.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md` (`mismatch:path-absent`) — a truthful
"this file is absent" sentence read as an evidence path. Another seat repaired it in `2a130b4`;
`ImplDeclaredA` independently reported the same token and reasoning. This seat did not
duplicate the repair.

    $ python3 -B tools/souji-declared-evidence.py --selftest
    PASS fixture1 all-good -> 0 ...
    PASS fixture5 path only at other rev -> mismatch ...
    PASS control always-zero -> FALSE-GREEN-REJECTED [FALSE-GREEN-REJECTED]
    selftest=8/8                                             exit=0

### 1.2 Drafted text measured (the number Block 2 must carry)

Base = `5fdd5d5:SCORECARD.md`, Blocks 1, 2 and 4 applied to a scratch copy, run against
`c9f1fe3` with the current scanner:

    $ python3 -B tools/souji-declared-evidence.py --root . \
          --file /var/tmp/ds-cand/SCORECARD.md --rev c9f1fe3 --format counts
    assertions=66 resolved=66 skipped=44 mismatches=0        exit=0

tsv filter for `observed != resolved`: no rows. Token delta against the `5fdd5d5` base's 60:
−1 class B (`af73b8ba92…`), +4 class B (`4edb25d`, `5fdd5d5` ×2,
`c9f1fe3caf642dfe3a9e00de94caf1d4bf86503f`), +3 class A (`SCORECARD.md` ×2,
`corpus/README.md`) → 66; skipped 38 → 44.

### 1.3 C2 counter and registry conformance (inputs to Blocks 3a/3b)

    $ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
        --entries corpus/knowledge/quarantine-staging-no-copy-r23.md \
                  corpus/knowledge/quarantine-origin-record-fields-r24.md \
        --snapshot-dir census/round-22/attempt2/sources \
        --slice census/round-22/attempt2/quarantine-slice \
        --slice-verdicts census/round-22/attempt2/slice-verdicts.tsv
    entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0     exit=0

    $ python3 -B tools/souji-gate-check.py --selftest | tail -2
    PASS control always-green -> FALSE-GREEN-REJECTED
    selftest=9/9                                             exit=0

    $ bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate \
        --root /home/vgpnk/Projects/shokunin souji
    ... W04 duplicate-url lines ...
    souji   ok   .../souji-shokunin/corpus/SOURCES.md        exit=0

Registry rows re-derived: `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`
→ `114`. Source ids the entries cite, read from their frontmatter: S109–S111 (r23),
S112–S114 + existing S022 (r24).

### 1.4 Membership delta (for the row's honesty clause)

Multiset diff of the counter's tsv token sets, `4edb25d` → `5fdd5d5`, current scanner:
55 tokens → 60; 6 retired, 11 added. Retired: the never-existing `.ufo/scopes/…` path,
`AXES.md`, `reason-after.txt`, `census/round-14/verification*.json`, `31984f4`, `b912328…`.
Added: `census/round-14/verification.json`, `census/round-21/reason-after.txt`,
`census/round-22/attempt2/declared-evidence-before.tsv` ×2,
`corpus/lessons/round-22-verifier-spotcheck.md`, `31984f473c…`, `4edb25dfe2…` ×3,
`af73b8ba92…`, `d7266c5`.

---

## 2. Drafted text (paste-ready, in the evidence file)

- **Block 1** — replacement `## Capabilities` row, 4 columns, naming the exact three classes,
  the read-only/git-only surface, and four limits (one file per run; three classes only;
  skipped spans not itemised; class C has no instance on `SCORECARD.md`; class B proves
  existence, not measurement) plus "no authorship, execution or prose truth". No universal
  clause. It replaces the row on disk because that row cites `S109–S114`.
- **Block 2** — replacement calibration `Axes` row: the before receipt's
  `56/53/33/3` **and** the current scanner's `55/52/33/3` at the same revision (with the
  escaped-pipe reason); drafted tip `66/66/44/0`; membership "6 retired / 11 added"; attempt 1
  rejected-honest-stop and **unproven**, not re-claimed; score 7 unchanged with the 8-move left
  to closure; counting command plus full before and after hashes in the measured-commit cell.
- **Block 3a/3b** — `corpus/README.md` coverage-map row and `## Frontier` F4 bullet: both
  adopted entries named with their source ids, the HELD entry marked HELD, and the remaining
  operator decision (record format; `renameat2`/`mv --no-copy` as a tool change; no lane
  deletion authority).
- **Block 4** — one-line `## Planned` pointer for r23.
- **Recompute rule** — the printed line at the paste commit is authoritative; the drafted text
  contributes +6 assertions and +6 skips against the `5fdd5d5` base.

### Q10 self-check

| requirement | drafted state |
|---|---|
| prose numbers equal table numbers | Block 2 prose and command cell carry the identical `66/66/44/0`; the dual before-measurement is labelled by scanner |
| every row carries its counting command | Block 1: `--selftest` invocation; Block 2: full `--format counts` invocation |
| every row carries its measured commit | Block 1: `4edb25d` (3 mismatches) and `5fdd5d5` (0); Block 2: full `4edb25dfe…` before-hash and full `c9f1fe3c…` after-anchor |
| score consistency | score column 7 equals `## Saturation` "calibration 7"; the 8-move is left to closure |
| no unproven claim reused | attempt 1's strict adequacy is called unproven in Blocks 1 and 2 |

---

## 3. Bounded findings

1. **[measured] The landed row's counts no longer match the counter.** The row landed at
   `ee1aef2` quotes `assertions=59 resolved=59 skipped=37` (that is `af73b8b`) and only
   `mismatches=0` for the tip; the current scanner prints `60/60/38/0` at `5fdd5d5` and at
   `c9f1fe3`. Block 2 supplies the tip line and the full numbers.
2. **[measured] The landed row's membership count is wrong.** It says "5 base tokens retired,
   6 added"; the measured multiset diff at the current scanner is 6 retired and 11 added
   (55 − 6 + 11 = 60). Block 2 states the measured pair.
3. **[measured] The before receipt is scanner-stamped and no longer reproducible.** The
   committed receipt and the row both quote `56/53/33/3` at `4edb25d`; the current tool prints
   `55/52/33/3` there. `mismatches=3` is unchanged, so the claim survives, but a row that
   quotes the receipt without saying so is not reproducible by the tool it names. Block 2
   quotes both with attribution.
4. **[measured] Mis-citation survives in the capability row.** `SCORECARD.md:74` still
   attributes C1 to `S109–S114`, the rows the C2 quarantine entries cite
   (`corpus/SOURCES.md:129–134`). C1 has no registry row; Block 1 drops the S-ids rather than
   inventing one.
5. **[measured] Coverage-map contradiction.** `corpus/README.md:42` says "layout held" while
   lines 59–61 and 88–90 say F4 holds an admitted layout entry and the HELD entry is
   `quarantine-same-filesystem-rename.md`. Block 3a fixes the status cell and marks HELD in the
   entries cell; Block 3b replaces a Frontier bullet that still calls the origin records
   un-staged work.
6. **[measured] A counts line in this file is not free.** Each revision token written into the
   row becomes a class-B assertion, and skip accounting moves with the scanner. My own draft
   measured 62 → 63 → 65 → 66 as the base and the text changed, and 40 → 41 → 43 → 44 skipped
   across scanner revisions. That is why Block 2 carries a recompute rule instead of a copied
   number.
7. **[measured] The lane moved four times during this seat** (`70af563` → `3216c19` →
   `d6a75ba` → `5fdd5d5` → `c9f1fe3`), including a rewrite of the row this seat drafts, a
   hardening of the counter and a cell-splitting fix. Drafts target the current bytes; a
   further rewrite of line 14 or of the tool invalidates the `66/66/44` line only, not the
   wording.
8. **[source-inferred, not executed] Audit scope.** C1 reads `SCORECARD.md` and nothing else, so
   no claim is made here for `corpus/README.md`, `SKILL.md` or `LOG.md`; that is why Block 4
   names README as the next surface rather than an already-audited one.

## 4. Process, deviations, out-of-scope

- Tooling: none installed or upgraded; no `pacman` transaction attempted.
- Writes: this report, the named evidence file, and `/var/tmp/ds-cand/SCORECARD.md`
  (sha256 `b55034dbe962e73446373ffe5ce9ddbca571dcd1bef71b1b2d2191be8b2b410c`) plus tsv dumps in
  `/var/tmp`. The scratch copy is measurement scaffolding, not evidence; the blocks in the
  evidence file are the durable artifact.
- Deviation, disclosed: two count substitutions on that scratch copy were done with scripted
  replacements instead of the per-edit tool; one produced a duplicated `mismatches=0` tail that
  I removed with the edit tool. Only `/var/tmp` was affected, never the lane repo; the final
  line was re-verified by the counter (`66/66/44/0`) and by a token-set diff.
- Out of scope, untouched: both target files unedited by this seat; no git/jj write, commit,
  index, `.ufo/state`, watchdog log, MANIFEST, fleet templates/scripts, sibling repo, `/proc`,
  credentials, private TSVs, `.tower`, operator-sweep census content; no mutating cleanup; no
  process signalling; no deletion authority created.
- Not claimed: admission, closure, any score change, any resolution of attempt 1's adequacy
  claim, or any statement about bytes the audit does not read.

## 5. Artifacts

- Report: `.ufo/waves/round-22/attempt2/w1/DraftScorecard.md`
- Evidence / paste-ready drafts: `.ufo/waves/round-22/attempt2/w1/evidence/DraftScorecard.md`
