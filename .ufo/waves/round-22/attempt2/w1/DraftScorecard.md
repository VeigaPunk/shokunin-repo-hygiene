STATUS: PASS

# DraftScorecard — bookkeeping text for round 22 attempt 2 (scribe seat)

Drafted, not landed. No byte of `SCORECARD.md`, `corpus/README.md`, the lane index,
`.ufo/state`, MANIFEST or any sibling repo was written by this seat. The two deliverables are
this report and `.ufo/waves/round-22/attempt2/w1/evidence/DraftScorecard.md`.

Frozen contract read before any verdict:
`.ufo/waves/round-22/attempt2/preregistration.txt`. C1 = declared-evidence calibration audit;
its counter, three assertion classes, five fixtures + do-nothing control, and kill rule are
used as written. C2 = assimilation of the restorable-quarantine-staging theme, 2 entries +
one verdict per absent-defect-register row. Neither claim is re-scoped here; attempt 1's
strict-adequacy claim is treated as unproven throughout the drafted prose.

---

## 1. Executed measurements (all read-only, git plumbing only)

### C1 — declared-evidence counter

    $ python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md \
          --rev 4edb25d --format counts
    assertions=56 resolved=53 skipped=33 mismatches=3        exit=1

That equals the committed receipt `census/round-22/attempt2/declared-evidence-before.tsv`
(last line), so the before receipt reproduces from committed bytes.

    $ ... --rev 70af563c3086d5799a7fdaf988ba3b687f3b128c ...
    assertions=57 resolved=56 skipped=37 mismatches=1        exit=1

The single surviving mismatch at that tip was `SCORECARD.md:83`, class A,
`.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md` (`mismatch:path-absent`). Another
seat repaired it in `2a130b4` before this seat could carry it; I did not duplicate the repair.

    $ ... --rev 3216c1998fe04d7e23793ffd4e135bd37c3a11f4 ...
    assertions=56 resolved=56 skipped=36 mismatches=0        exit=0

    $ ... --rev d6a75bad8129960bdb96874421298e3bf42aa8c4 ...
    assertions=58 resolved=58 skipped=36 mismatches=0        exit=0

    $ python3 -B tools/souji-declared-evidence.py --selftest
    PASS fixture1 all-good -> 0 ...
    PASS fixture5 path only at other rev -> mismatch ...
    PASS control always-zero -> FALSE-GREEN-REJECTED [FALSE-GREEN-REJECTED]
    selftest=8/8                                             exit=0

### C1 — drafted text measured (the number Block 2 must carry)

Base = committed `d6a75ba` bytes (`SCORECARD.md` sha256
`725e64458916306dfb951380cf3794b8473b7fa8ed740ccb4b884769991c4cc0`) with drafted Blocks 1,
2 and 4 applied to a scratch copy:

    $ python3 -B tools/souji-declared-evidence.py --root . \
          --file /var/tmp/ds-cand/SCORECARD.md --rev d6a75ba --format counts
    assertions=65 resolved=65 skipped=40 mismatches=0        exit=0

    per-row tsv filter for observed != resolved: no rows

Assertion delta, base → drafted text (enumerated by diffing the two tsv token sets):
+3 class A (`corpus/README.md`, `SCORECARD.md` ×2), +4 class B (`4edb25d` ×2, `d6a75ba`,
`d6a75bad8129960bdb96874421298e3bf42aa8c4`); +4 skipped (three non-path spans in Block 1,
`mv --no-copy` in Block 4). 58+7=65, 36+4=40.

### C2 — gate counter and registry conformance (inputs to Blocks 3a/3b)

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
    souji   ok   /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md   exit=0

Registry row count re-derived: `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`
→ `114`. Adopted rows the two entries cite: S109–S111 (r23 entry frontmatter) and
S112–S114 + existing S022 (r24 entry frontmatter) — read from the entry files, not inferred.

---

## 2. Drafted text (paste-ready, in the evidence file)

- **Block 1** — replacement `## Capabilities` row, 4 columns, describing exactly the frozen
  three classes, the read-only/git-only surface, and four explicit limits (one file, three
  classes, skipped-not-verified, no authorship/execution/prose truth). No universal clause.
  It replaces the row already on disk because that row cites `S109–S114`, which are C2
  registry rows, not C1 evidence.
- **Block 2** — replacement calibration `Axes` row: before `4edb25d` →
  `assertions=56 resolved=53 skipped=33 mismatches=3`; after the paste tip →
  `assertions=65 resolved=65 skipped=40 mismatches=0`; membership (not identity) stated;
  score column stays 7 with the move to 8 left to closure; attempt 1 explicitly **unproven**
  and not re-claimed, re-pinned or reworded; counting command + both measured revisions in
  the measured-commit cell.
- **Block 3a/3b** — `corpus/README.md` coverage-map row and `## Frontier` F4 bullet, naming
  the two adopted entries with their source ids and the remaining operator decision
  (record format; `renameat2`/`mv --no-copy` staging as a tool change; no lane deletion
  authority).
- **Block 4** — one-line `## Planned` pointer for r23 (F4's operator-owned piece, else the
  same counter on the lane's next declared surface `corpus/README.md`).
- **Recompute rule** — drafting is not measurement: assertions = base+7, skipped = base+4,
  mismatches = 0, and the printed line must be pasted into both places in Block 2.

### Q10 self-check on the drafted rows

| requirement | drafted state |
|---|---|
| prose numbers equal table numbers | Block 2's prose and command cell carry the same `65/65/40/0`; score column 7 equals `## Saturation` "calibration 7" |
| every row carries its counting command | Block 1: `--selftest`; Block 2: full `--format counts` invocation |
| every row carries its measured commit | Block 1: `4edb25d` (3 mismatches) and `d6a75ba` (0); Block 2: before `4edb25dfe…`, after anchored to the drafted text over `d6a75bad…` plus the paste commit |
| no dependence on an unmade claim | attempt 1's strict-adequacy claim is described as unproven in both Block 1 and Block 2 |

---

## 3. Bounded findings

1. **[measured] Mis-citation in the landed capability row.** `SCORECARD.md:74` at `d6a75ba`
   attributed C1 to `S109–S114`, which are the rows the C2 quarantine entries cite
   (`corpus/SOURCES.md:129–134`). C1 has no registry row of its own; Block 1 drops the S-ids
   instead of inventing them.
2. **[measured] Coverage-map contradiction.** `corpus/README.md:42` says "layout held" while
   the same file says F4 holds an admitted layout entry and the HELD entry is
   `quarantine-same-filesystem-rename.md` (lines 59–61, 88–90). Block 3a fixes the status
   cell and marks the HELD entry inside the entries cell.
3. **[measured] An "after" count is not a free addition to the row.** Each revision token
   written into the row becomes a class-B assertion. My own draft went 62 → 63 → 65 as I
   added the paste-tip anchor; the landed row's earlier `56/56/36` was correct only for
   `3216c19` and would have been stale prose at the next tip. This is why Block 2 states the
   numbers it was measured with and carries a recompute rule.
4. **[measured] "the same 56 assertions" was numerically true, membership-false.** Base →
   `3216c19` dropped three class-A spans (`AXES.md` → absolute fleet path, `reason-after.txt`
   → `census/round-21/reason-after.txt`, the never-existing `.ufo/scopes/…` path) and two
   class-B tokens, and added four class-A pointers plus one class-B token; the totals
   coincided at 56. Block 2 says membership differs and names the three kinds of change.
5. **[measured] The lane moved three times during this seat.** `4edb25d` → `70af563` →
   `3216c19` → `d6a75ba`, and working-tree edits continue (`SCORECARD.md` working hash
   `99dbc5d3…` vs committed `725e6445…` at `d6a75ba`). Every number in the drafts is pinned
   to committed `d6a75ba` bytes; pasting onto a later tree requires the recompute rule.
6. **[source-inferred, not executed] `report`-only limits.** The audit cannot show
   authorship, that a cited command was ever run, or that un-tokenised prose is true; Block 1
   says so in the row itself. C1 covers `SCORECARD.md` only, so nothing is claimed for
   `corpus/README.md` or `SKILL.md` (the reason Block 4 makes README the next surface rather
   than an already-audited one).

## 4. Process, deviations, out-of-scope

- Tooling: none installed, none upgraded, no `pacman` transaction attempted.
- Writes: this report; the named evidence file; and scratch under `/var/tmp` used by the
  counter (`/var/tmp/ds-cand/SCORECARD.md`, sha256
  `3581b87a6da3961e66070b29b7436ca23fbdfc2e5ea0a6bb414df6119e411c4d`) plus tsv dumps in
  `/var/tmp`. The scratch copy is not evidence — the drafted blocks in the evidence file are.
- Deviation, disclosed: one scratch-copy string replacement (62 → 65 in the two count
  positions) was done with a scripted replace instead of the per-edit tool. It touched only
  the `/var/tmp` candidate, never the lane repo; the result was re-verified by the counter
  (`65/65/40/0`) and by a token-set diff against the frozen base.
- Out of scope, untouched: both target files remain unedited by this seat; no git/jj write,
  no commit, no index/state/watchdog/MANIFEST change, no sibling repo, no `/proc`, no
  credentials, no operator-sweep census content, no mutating cleanup, no process signalling.
- Not claimed: any admission or closure verdict, any score change, any resolution of attempt
  1's adequacy claim, any statement about files the audit does not read.

## 5. Artifacts

- Report: `.ufo/waves/round-22/attempt2/w1/DraftScorecard.md`
- Evidence / paste-ready drafts: `.ufo/waves/round-22/attempt2/w1/evidence/DraftScorecard.md`
