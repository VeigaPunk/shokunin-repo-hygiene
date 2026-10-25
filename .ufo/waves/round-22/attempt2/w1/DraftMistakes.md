# DraftMistakes — attempt-2 `## Mistakes` block (draft, report-only)

Seat `L1Souji22.DraftMistakes` (scribe, leaf). Item: draft the attempt-2
`## Mistakes` block for `corpus/lessons/round-22.md`. Per the item rule ("write
the block in your report only") and the lane read-only contract, nothing was
written to `corpus/` — `corpus/lessons/round-22.md` is unchanged by this seat.

STATUS: PASS

Frozen contract read before any verdict:
`.ufo/waves/round-22/attempt2/preregistration.txt` (fields
`class · evidence pointer · captured-by · fix`; "a fix counts only when a
fixture shows it can fail"; base revision `4edb25d`). Observed lane HEAD at work
time `3216c1998fe04d7e23793ffd4e135bd37c3a11f4`.

## Executed evidence

| # | command | observed |
|---|---|---|
| 1 | `git cat-file -e 4edb25d:AXES.md` / `:reason-after.txt` / `:.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md` | ABSENT / ABSENT / ABSENT; `census/round-21/reason-after.txt` PRESENT; `ls -d .ufo/scopes` → No such file or directory |
| 2 | `python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md --rev 4edb25d… --format counts` | `assertions=56 resolved=53 skipped=33 mismatches=3`, exit 1 |
| 3 | same at `--rev HEAD` | `assertions=56 resolved=56 skipped=36 mismatches=0`, exit 0 |
| 4 | `python3 -B tools/souji-declared-evidence.py --selftest` | 8/8; fixtures 2–5 each `mismatches=1`; `control always-zero -> FALSE-GREEN-REJECTED` |
| 5 | `python3 -B tools/souji-gate-check.py --selftest`, re-run as `git show HEAD:tools/souji-gate-check.py \| python3 -B - --selftest` (worktree copy was mid-edit) | 9/9 from both; `quote-absent -> fail [fail=2]`; `partial-verdicts -> fail [slice_verdicts=1 slice_total=2 fail=1]`; `control always-green -> FALSE-GREEN-REJECTED` |
| 6 | preregistered C2 counter on the live lane (committed blob and worktree, identical) | `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`, exit 0 |
| 7 | same with `--slice-verdicts /dev/null` (negative control, no file created) | `slice_verdicts=0 slice_total=8 fail=8`, exit 1 |
| 8 | `man git-worktree \| col -b \| sed -n '10,14p'` and `'214,222p'` | line 12 `git worktree prune [-n] [-v] [--expire <expire>]`; line 217 `-n, --dry-run`, line 218 `With prune, do not remove anything; just report what it would remove.` |
| 9 | `man 2 rename \| col -b \| sed -n '88,96p'` | line 91 `RENAME_NOREPLACE`; 92–93 `Don't  overwrite newpath of the rename.  Return an error if newpath already exists.` |
| 10 | `grep -cF` of each claimed quote in the register's cited artifact (shokuknow, read-only) | `0`, `0`, `0`, `0`; `dry-run` → 3 hits, all command labels (`r23-worktree-census.out:3,20,27`) |
| 11 | `git diff 4edb25d HEAD -- SCORECARD.md` | 15 insertions/6 deletions: `AXES.md` → absolute fleet path; `reason-after.txt` → `census/round-21/reason-after.txt`; scope-file sentence reworded to state the file is absent |
| 12 | `git cat-file -e 4edb25d:tools/souji-declared-evidence.py` vs `HEAD:` | ABSENT vs PRESENT (audit-TSV revision check, Finding F1) |

Full command log with untrimmed output: `.ufo/waves/round-22/attempt2/w1/evidence/DraftMistakes.md`.

## Draft block

```markdown
## Mistakes

Frozen fields (`.ufo/waves/round-22/attempt2/preregistration.txt`, written before
measurement): `class · evidence pointer · captured-by · fix`. A fix counts only
when a check can fail.

- **M13 — calibration: an unproven adequacy claim was filed as an admitted
  result.** *Evidence:* `corpus/lessons/round-22-verifier-spotcheck.md`
  §"Decision and safety boundary" — "**Not admitted; rejected-honest-stop.**
  Retain the finite recorded calibration gains, but original
  independent-oracle/strict-adequacy proof is not complete"; "A positive counter,
  author-selected mutant saturation or retained VOID PASS cannot replace that
  missing authority"; of the credited reproduction basis, "Its "compliant" label
  is not adopted"; and the report's own strict-full-adequacy warning "remains
  controlling". *Captured-by:* `corpus/QUALITY.md:29` Q5 — a published verdict
  table "is re-derived by an independent blind seat before admission" — read
  with `:65` Q26 (a confirmed read-only violation voids the seat's evidence) and
  `:122` Q53 ("state adequacy "of N listed mutants", never exhaustive). All three
  existed as prose criteria and none was executable at filing, so the
  overstatement was caught by the non-author spot-check instead of being refused
  by the lane. *Fix:* the adequacy claim is retired for the round rather than
  narrowed (the preregistration holds attempt 1's C1 "NOT re-claimed … re-pinned,
  re-worded or regenerated"), and every claim of this attempt must name a
  command that re-derives it from committed bytes. *Failure witness:* a claim
  cannot be completed by assertion —
  `tools/souji-gate-check.py --selftest` fixture `partial-verdicts` →
  `slice_verdicts=1 slice_total=2 fail=1`, the live empty-verdicts control
  (`--slice-verdicts /dev/null`) → `slice_verdicts=0 slice_total=8 fail=8`,
  exit 1, and `tools/souji-declared-evidence.py --selftest` → `FALSE-GREEN-REJECTED`
  for a counter that prints zeros without reading bytes. Were the fix absent, an
  asserted positive would reach V==T and the always-zero/always-green controls
  would be admitted.

- **M14 — citation class: man-page prose cited as a local probe output.**
  *Evidence:* `/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md`
  (HEAD `8b94c5c`, tracked): `:172` souji S123 cites
  `lanes/souji/round2/evidence/r23-trigger-prune.out` for
  `git worktree prune [-n] [-v] [--expire <expire>]`; `:175` S131 cites
  `r23-worktree-census.out` for `-n, --dry-run With prune, do not remove
  anything; just report what it would remove.`; `:176` S133 cites
  `r24-renameat2-probe.out` for `RENAME_NOREPLACE Don't overwrite newpath of the
  rename.`; `:173` S124 cites `noreplace-probe.out`, whose second fragment
  `Don't overwrite newpath of the rename. Return an error if newpath already
  exists.` is the same class beside a genuine probe line. All four artifacts
  exist and none contains the quoted prose (`grep -cF` → 0; the three `dry-run`
  hits in the census output are command labels at `:3`, `:20`, `:27`). The real
  homes, read from the installed manuals, are `git-worktree(1):12`,
  `git-worktree(1):217-218` and `rename(2):91-93`. *Captured-by:* the fleet floor
  restated at `corpus/QUALITY.md:7-8` — "a quote its location" — with Q17
  (`:41`, a claimed committed fixture "must resolve … at the measured
  revision"). Both were prose-only for register rows: nothing resolved a claimed
  quote against the artifact it was attributed to, so the register classed the
  rows `payload-absent` instead of naming the man page. *Fix:* gate-check check 4
  requires every quoted span to appear verbatim (whitespace-collapsed) in the
  committed snapshot the Gate names, and the frozen slice predicate forces one
  class per row (`present|accepted|unverifiable|refused`); a man-page quote is
  `accepted` only with the correction stated, otherwise `refused`
  (`census/round-22/attempt2/slice-verdicts.tsv`: S123 refused, S124/S131/S133
  accepted with corrections). *Failure witness:*
  `tools/souji-gate-check.py --selftest` → `quote-absent -> fail [fail=2]`, 9/9,
  and the live counter `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`
  versus the empty-verdicts control `fail=8`, exit 1. Were the fix absent, a
  quote missing from its named artifact would pass check 4 and a row could stand
  without a verdict class.

- **M15 — calibration: SCORECARD presented three assertions that do not resolve
  at its measured revision.** *Evidence:* at `4edb25d`,
  `census/round-22/attempt2/declared-evidence-before.tsv:3,63,77` are
  `mismatch:path-absent` for `AXES.md`, `reason-after.txt` and
  `.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md`, with the receipt's own
  line `assertions=56 resolved=53 skipped=33 mismatches=3`; this seat's re-run
  reproduces the same counts at exit 1. The three were a fleet file written as a
  lane-relative path (`/home/vgpnk/Projects/shokunin/AXES.md`), a path with its
  directory dropped (the file is `census/round-21/reason-after.txt`, present at
  the base revision), and a path on no tree (`ls -d .ufo/scopes` → No such file
  or directory). Audit seats, exact paths and status at read:
  `.ufo/waves/round-22/attempt2/w1/evidence/AuditCap1.tsv` READ (declares
  `measured_revision=4edb25d…`, base lines 45-49, 0 mismatches);
  `…/evidence/AuditCap2.tsv` READ (base lines 50-54, 0 mismatches);
  `…/evidence/AuditCap5.tsv` READ — 0 mismatches but **measured on the repaired
  table, not the base**: it reports `SCORECARD.md:74
  tools/souji-declared-evidence.py resolved`, while that file is absent at
  `4edb25d` and present at HEAD, and base lines 70-74 are `## Planned` prose
  (base row 25 is line 63, outside its slice);
  `…/evidence/AuditAxes.tsv`, `…/evidence/AuditCap3.tsv`,
  `…/evidence/AuditCap4.tsv`, `…/evidence/AuditSkillShonen.tsv` —
  **PENDING-SEAT** (absent at read). `…/evidence/AuditReadme.tsv` is read and
  separate: 9 `mismatch:unresolved-either-base` rows, all in `corpus/README.md`,
  a different self-assessment file. *Captured-by:* `corpus/QUALITY.md:41` Q17 (a
  claimed evidence fragment must resolve at the measured revision; prose naming
  a fixture is not the file) with `:34` Q10 (bookkeeping matches the repo at the
  closing commit). Both prose; SCORECARD had no executable self-audit before this
  round. *Fix:* `tools/souji-declared-evidence.py` with the frozen before receipt
  (base M=3) and the closing count (M=0): the repaired cells either name the file
  that really holds the claim or stop presenting the token as evidence. *Failure
  witness:* the tool's selftest emits `mismatches=1` for absent path, dangling
  revision, wrong digest and path-present-only-at-another-revision, and rejects
  the always-zero control (`FALSE-GREEN-REJECTED`), 8/8. Were the fix absent, the
  closing tip would still print `mismatches=3` and exit 1.
```

### Landing note (verified conflict, not part of the block)

`corpus/lessons/round-22.md` at HEAD `3216c19` already carries attempt-2 rows
**M13–M16**, landed by `70af563` ("round-22: bookkeeping, lesson gates and LOG for
attempt 2"); `git show HEAD:corpus/lessons/round-22.md | grep -n 'M13\|M16'` →
lines 288 and 317. The frozen "number yours from M13" predates that landing, so
append-only uniqueness makes this block land as **M17–M19**. Two verified
differences from the landed rows: landed M13 records *captured-by* as `none`
(Q5/Q26/Q53 exist and apply), and landed M14 says "7 of 8 rows" (7 of 8 rows are
`payload-absent`, but the man-page-cited-against-a-local-artifact class is 3 rows
plus the S124 fragment). Landed M15's three tokens and counts reproduce exactly.
The canonical judge should resolve the numbering, not this seat.

## Findings

- **F1 — execution.** `AuditCap5.tsv` does not measure the revision its own
  prompt fixes (`4edb25d`). Executed proof: it reports
  `SCORECARD.md:74 tools/souji-declared-evidence.py` as `resolved`, but
  `git cat-file -e 4edb25d:tools/souji-declared-evidence.py` is ABSENT and the
  same at HEAD is PRESENT; `git show 4edb25d:SCORECARD.md | sed -n '70,74p'` is
  `## Planned` prose. Its `mismatches=0` is a post-repair measurement and is
  cited with that caveat only. It neither changes nor corroborates C1's counts
  (those are carried by the committed before receipt and rows 2–3 above).
- **F2 — coverage.** Four of the eight named audit TSVs were unread at write
  time (`AuditAxes`, `AuditCap3`, `AuditCap4`, `AuditSkillShonen`), each marked
  `PENDING-SEAT` in the block. Their slices are therefore not covered by this
  draft.
- **F3 — append-only conflict.** M13–M16 already exist at HEAD; this block lands
  as M17–M19 unless the integrator decides otherwise. Reported, not resolved
  here.
- **F4 — provenance.** The register lives in `/home/vgpnk/Projects/shokuknow`
  (HEAD `8b94c5c`, tracked; last touched `d4ab45f2`), read only. No row was
  rewritten and no admission is derived from it; the lane's own
  `slice-verdicts.tsv` is the verdict surface.
- **F5 — not re-verified here.** The web-sourced rows of the slice (S114, S126,
  S138) are taken from the register and the lane verdict TSV; this seat fetched
  no page. Nothing in this report is a natural-language judgment of the
  spot-check itself — it is read evidence, clearly distinct from rows 1–12 of the
  executed table.
- **F6 — moving worktree, pinned evidence.** At 03:52 `git status --porcelain`
  showed ` M SCORECARD.md`, ` M tools/souji-gate-check.py`,
  ` M corpus/lessons/round-22.md` and ` M census/round-22/attempt2/slice-verdicts.tsv`
  from sibling seats. Rows 5–7 were therefore re-taken from the committed blob
  (`git show HEAD:…`) with identical output, and
  `tools/souji-declared-evidence.py` (unmodified) reads its declaration via
  `git show` at `--rev`, so rows 2–4 describe committed bytes rather than the
  dirty worktree. The block's `PENDING-SEAT` statuses and the
  `slice-verdicts.tsv` rows quoted are as read at 03:52 and may have changed
  since; the committed-blob re-run is the durable receipt.

## Touched surfaces and out-of-scope

Written (2 files, both named by the item):
`.ufo/waves/round-22/attempt2/w1/DraftMistakes.md` (this report) and
`.ufo/waves/round-22/attempt2/w1/evidence/DraftMistakes.md` (evidence log).
Unchanged: `corpus/` (including `corpus/lessons/round-22.md`), `census/`,
`tools/`, `.ufo/state`, `.ufo/watchdog.log`, `MANIFEST.json`, the fleet root's
`templates/` and `scripts/`, and every sibling repo; shokuknow was read only
(no write, commit, fetch, push, campaign tool). No cleanup, signal, deletion
authority or subagent dispatch. No tool installed or upgraded, so no
version/channel to record.
