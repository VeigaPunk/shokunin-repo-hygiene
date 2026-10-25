STATUS: PARTIAL

Slice: `SCORECARD.md` lines 9–45 — the three `## Axes` rows (coverage, calibration,
operability) and the correction/notes prose between `## Axes` and `## Capabilities`.
Evidence: `.ufo/waves/round-22/attempt2/w1/evidence/AuditAxes.tsv` (45 rows + header,
sha256 `7eb118c1b3fb046750c3e05018367de58fc907d9ad9550eeb18be3492b2c4936`).

PARTIAL, not PASS: the coverage/mismatch target of C1 holds at the tip
(`mismatches=0`, exit 0) and no token is fabricated, but the calibration row's
literal counter does **not** reproduce at the tip I measured (declared 56, measured 58),
and its "same 56 assertions" wording asserts a population identity that is false.
Not FAIL: every class-A/B token in the slice except one rev-scoped receipt resolves,
and that one resolves at the tip.

---

## 1. What was measured, at which bytes

Measured revision for class A: **`4edb25dfe262515d0da63224bbba71e02e36cba5`** (lane base,
frozen in the preregistration).

Text audited: `SCORECARD.md` lines 9–45. The slice is byte-identical across the tips that
landed during this audit (verified, `SLICE_IDENTICAL`):

```
$ diff <(git show 3216c19:SCORECARD.md | awk 'NR>=9 && NR<=45') \
       <(git show 5ff5041:SCORECARD.md | awk 'NR>=9 && NR<=45') && echo SLICE_IDENTICAL
SLICE_IDENTICAL
```

`SCORECARD.md` sha256 per revision (`git show <rev>:SCORECARD.md | sha256sum`):

| rev | sha256 | note |
|---|---|---|
| `4edb25d` | `b3cecc977b1cdc716c2bef030007983b5100498782cb307c46a69d6eb9682530` | frozen base |
| `70af563` | `469a0bc714920a4dc401c37661f4409e9dc89aad47078f15435976dd28f2fbb3` | before last repair |
| `3216c19` | `71507c608d3ea54b22378fd98bb6b5e4c98d7f946715e9eda471e0b80178e2a0` | counts recorded |
| `5ff5041` | `725e64458916306dfb951380cf3794b8473b7fa8ed740ccb4b884769991c4cc0` | Capabilities edits |
| `d6a75ba` | same as `5ff5041` | SCORECARD untouched by this commit |
| `af73b8b` | `60366781d0e21ecf4b5ddd17b2663981c186bc08f1d55e68578c81ffb1dba055` | last tip measured; worktree clean at it |

The file moved through six SCORECARD revisions during this audit
(`4edb25d` → `70af563` → `2a130b4` → `3216c19` → `5ff5041` → `af73b8b`); every claim below
names the revision it was observed at.

## 2. Exact command per class

All read-only git plumbing; no jj, no writes.

- **A — backticked repo-relative path (optional `:line`, optional `*`):**
  `git -C <lane> cat-file -e <rev>:<path>` and, for globs,
  `git -C <lane> ls-tree -r --name-only <rev>` + `fnmatch`. Membership set:
  `git ls-tree -r --name-only 4edb25dfe262515d0da63224bbba71e02e36cba5`.
- **B — 7..40-hex revision token:** `git -C <lane> cat-file -e <tok>^{commit}`.
- **C — 64-hex digest with exactly one backticked path in the cell:**
  `git -C <lane> show <rev>:<path> | sha256sum`.
- Cross-check of the lane's own instrument (read-only):
  `python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md --rev <REV> --format counts`
  and `--selftest`.

## 3. Slice census (the TSV)

45 candidate tokens in lines 9–45: **7 class A, 5 class B, 0 class C, 33 skipped**.
Every skipped token carries its reason (counts, dates, command spans, non-backticked paths,
source ids, placeholders); nothing was silently dropped. Targets of class C: none — the
slice contains no 64-hex token (`git show <rev>:SCORECARD.md | awk 'NR>=9&&NR<=45' |
grep -oE '[0-9a-f]{64}'` → empty).

Class A/B verdicts at `4edb25d`: 11 resolved, **1 `mismatch:path-absent`** (F4 below).
At the tip: 12/12 resolve.

Instrument rows for the same slice at the tip (9 assertions, all `resolved`):
lines 14 (×2: the before receipt and `4edb25d…`), 20, 24, 26, 33, 38, 42, 44.

Whole-file counter, one command, five revisions:

```
--rev 4edb25d  -> assertions=56 resolved=53 skipped=33 mismatches=3  (rc=1)
--rev 70af563  -> assertions=57 resolved=56 skipped=37 mismatches=1  (rc=1)
--rev 3216c19  -> assertions=56 resolved=56 skipped=36 mismatches=0  (rc=0)
--rev 5ff5041  -> assertions=58 resolved=58 skipped=36 mismatches=0  (rc=0)
--rev af73b8b  -> assertions=59 resolved=59 skipped=36 mismatches=0  (rc=0)   [last tip measured]
```

Base slice only (lines 9–40, `## Capabilities` is at line 41 in the base text): 8 assertions,
all resolved — **the slice's before-state had zero mismatches**. The three base mismatches
sit outside it, at base lines 3 (`AXES.md`), 63 (`reason-after.txt`), 77
(`.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md`).

---

## 4. Findings

### F1 — High — the calibration row's counter does not reproduce at the tip
`SCORECARD.md:14` declares, verbatim:
`` `assertions=56 resolved=56 skipped=36 mismatches=0`, exit 0 ``, described as the output at
"the final tip". Measured with the row's own command:

```
$ python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md --rev af73b8b --format counts
assertions=59 resolved=59 skipped=36 mismatches=0
rc=0
```

56 is reproducible **only at `3216c19`**. The counter moved with each commit that changed
assertions elsewhere in the file: `70af563` 57 → `3216c19` 56 (the absent-path repair) →
`5ff5041` 58 → `af73b8b` 59, while the row's literal stayed 56. Causes are outside the slice —
`70af563` still had the backticked absent `.ufo` path; `5ff5041` added `4edb25d…` twice in the
Capabilities table; `af73b8b` added `measured at d7266c5` (line 51, and
`git cat-file -e d7266c5^{commit}` resolves). `LOG.md:1484-1486` records only the before side
(`assertions=56 resolved=53 skipped=33 mismatches=3`); the after side has no committed receipt.

The C1 *target* (`mismatches=0`, exit 0) still holds; the *literal number* is false at the
revision it is presented as describing.

Minimal truth-preserving repair (do not delete the capability claim): bind the literal to
the revision that produced it and let the tip be re-measured, e.g.
`→ assertions=56 resolved=56 skipped=36 mismatches=0 at 3216c19; re-run at this tip prints
58/58/36/0, recomputed at closure` — or replace the literal with the counters file/receipt
and state the property (`mismatches=0, exit 0`) only. A literal that is re-derived after the
declaration changes can never be stable; that is the structural defect.

### F2 — Medium — "the same 56 assertions" is a cardinality coincidence, not identity
Measured at `3216c19`: base 56 and tip 56 — but 5 assertions left and 5 entered
(`LC_ALL=C comm` over the two rows sets):

```
base only: .ufo/scopes/…/obsidian-cli-probe.md | 41553adb… | AXES.md | b912328d… | reason-after.txt
tip only:  4edb25d… | census/round-21/reason-after.txt | declared-evidence-before.tsv (×2)
           | corpus/lessons/round-22-verifier-spotcheck.md
```

51 of 56 are literally unchanged. Of the three former mismatches only one (`reason-after.txt`
→ `census/round-21/reason-after.txt`) re-entered the checked population as a resolvable
assertion; `AXES.md` became a host-absolute pointer and the absent `.ufo` file was de-evidenced
(plain text, with the absence now stated at lines 83–86). Both are legitimate — the prose no
longer presents a banked artifact — but `mismatches=0` is partly reached by *shrinking the
checked population*, not only by fixing pointers.

Repair: replace "repaired to 0 mismatches over the same 56 assertions" with
"56 before / 56 after, 5 replaced and 51 unchanged; one former mismatch now resolves, two
left the frozen grammar (host-absolute pointer, de-evidenced absent file)". No claim needs
to be withdrawn.

### F3 — Medium — `resolved=58 mismatches=0` is narrower than "the lane's own SCORECARD assertions"
In this slice the instrument enumerates 9 assertions. My census of the same 37 lines finds
45 candidates, and all the ones it cannot see resolve when checked directly:

- 5 word-glued revision tokens — `6ff3413` (`--base <6ff3413-proc-file>`), `4d5bf784…`
  (`repair4d5bf…`), `195715439a…` (twice: `from1957154…`, `final1957154…`) — all
  `resolved` by `cat-file -e <tok>^{commit}`. `HEX_B_RE`'s
  `(?<![A-Za-z0-9_.-])` boundary excludes them, so they are neither asserted nor counted as
  skipped.
- 8 backticked command spans (5 embedded paths: `tests/fixtures/r21-reason-canary.sh`,
  `tools/souji-proc-census.sh`, `SCORECARD.md`, `tools/souji-declared-evidence.py`,
  `census/round-13/run-verification.py`) plus 3 bare non-backticked paths
  (`census/round-21/accepted-matrix.json`, `final-code-verification.json`, `SKILL.md`).

All of these resolve at base or tip except `tools/souji-declared-evidence.py`, which is absent
at `4edb25d` and present from `a211e4d` — i.e. the row's own counting-command tool is not
covered by the count it reports. No false green; the claim is simply wider than the counter.

Repair: scope the sentence — "re-derived over the 58 strictly-enumerated backticked-path and
bare-hex assertions; command-span paths, word-glued revision tokens and non-backticked paths
are outside the frozen grammar" — or quote the glued tokens so the grammar covers them.

### F4 — Low — the only `mismatch:*` in the TSV (class A, rev scoping)
`SCORECARD.md:14` cites `census/round-22/attempt2/declared-evidence-before.tsv`. At the
assigned revision:

```
$ git cat-file -e 4edb25d:census/round-22/attempt2/declared-evidence-before.tsv
fatal: path '…' exists on disk, but not in '4edb25d'      -> mismatch:path-absent
$ git cat-file -e d6a75ba:census/round-22/attempt2/declared-evidence-before.tsv
(resolves)
```

Not a false claim: the receipt records a base measurement and was committed later. I validated
it — 57 lines (56 assertion rows + counts line), sha256
`e9d29a663081a21aaa88b9fa090c26b13a58f3cf8fe9efca741a742de661bf97`, last line
`assertions=56 resolved=53 skipped=33 mismatches=3`, and its rows are identical to a fresh
`--rev 4edb25d` run (`diff` → `RECEIPT_MATCHES_BASE_RUN`).

Minimal repair (keep the receipt): name the revision that holds it — "before receipt
`census/round-22/attempt2/declared-evidence-before.tsv` (committed at a211e4d)". A reader who
resolves at the revision the cell names (`4edb25d`, the *measured* side) then gets a clean hit,
and the artifact keeps its evidence role.

### F5 — Low — ambiguous bare pointer on the operability row
`SCORECARD.md:15` cites `final-code-verification.json` with no directory. As written it does
not resolve at base; only `census/round-21/final-code-verification.json` does (verified
`cat-file -e`). Not class A (not backticked), so no `mismatch:*`, but a human auditor cannot
resolve the bare filename. Repair: prefix the directory, optionally backtick it so class A
covers it. Do not drop it — the receipt exists.

### F6 — Info — the AXES pointer repair is real but no longer machine-checked
Line 3 now reads `/home/vgpnk/Projects/shokunin/AXES.md`; the target exists
(`-rw-r--r-- 5160`, 2026-10-16 15:54). It is host-absolute and outside the repo, so the frozen
class A can never check it. That is a truthful de-evidenting of a lane-relative pointer whose
real home is the fleet root, not a mismatch. Residual risk only: C1's `mismatches=0` says
nothing about this pointer.

### F7 — Info — claims in the slice that do reproduce (verified, not inferred)
- Base `56 assertions / 3 mismatches` with exactly the three named causes — reproduced, and
  the causes match by name and path (`AXES.md` lane-relative; bare `reason-after.txt`;
  absent `.ufo/scopes/…/obsidian-cli-probe.md`).
- `--selftest` **8/8**, rc=0: the five frozen kill-rule fixtures (all-good, absent path,
  dangling revision, wrong digest, path-at-other-rev), the correct-digest fixture, the
  command-span fixture (`skipped, not asserted`) and
  `PASS control always-zero -> FALSE-GREEN-REJECTED`.
- The line-83 repair is the step that took `70af563` (57/56/37/1) to `3216c19` (56/56/36/0):
  the absent `.ufo` path was de-backticked and the prose now records the absence.
- All hex tokens in the slice resolve: `4d5bf78`, `1957154`, `6ff3413`, `6f8ee0f`, `4edb25d`.
- `S100/S101` resolve to `corpus/SOURCES.md:120-121`.

---

## 5. Residual risk and verification gaps

- **Live target.** Six SCORECARD revisions during the audit; the worktree also carried
  uncommitted table edits between commits (it was clean again at `af73b8b`). Any literal counter
  in this row rots on the next commit that changes any table. Bind numbers to revisions, or
  record them in a receipt that the row cites instead of inlining them.
- **Instrument cannot audit an uncommitted declaration.** `read_declaration()` prefers the
  committed blob at `--rev`, so a "final tip" claim is only measurable after the commit that
  contains it; a row drafted before that commit cannot be self-verified.
- **Enum vs implementation (class B).** The frozen enum says "inside a table cell"; the tool
  treats a non-table line as one cell, so the prose token `6f8ee0f` (line 38) is asserted.
  Broader, not narrower — no false green, but the two texts differ.
- **Not checked here (out of slice):** `## Capabilities`, `## Planned`, `## Saturation`,
  `## Tool certification`, `## Retired`; class C for the file (none in the slice); the
  correctness of the numbers the axis rows inherit from r21 (27/27, 3/3, 18/18), which the
  enum cannot reach.
- **Executed vs inferred.** Executed: all git plumbing above, sha256 over `git show` output,
  five instrument runs (`counts` at `4edb25d`, `70af563`, `3216c19`, `5ff5041`, `af73b8b`),
  `--format tsv` per revision, one `--selftest`, receipt content diff, `comm` set diffs,
  `AXES.md` stat. Inferred: nothing in the findings — every verdict cites a command output.
- **Scope discipline.** No mutating cleanup, no process signalling, no jj/git writes, no
  deletion authority created. Wrote only this report and
  `.ufo/waves/round-22/attempt2/w1/evidence/AuditAxes.tsv`; the instrument's `--selftest`
  created and removed its own `/var/tmp` fixture. No tools installed or upgraded.
