# r29 scorecard / LOG skeleton — for the L1 to fill after data

Every `<...>` is a placeholder. No after value, receipt count or commit is supplied here.
Before values are quoted from the frozen control file; nothing else numeric is invented.

Sources opened for the shapes: `census/round-29/records/preregistration.txt` (committed at
`b8cb4b31ce80e2e3314b88e85d40ea9873180804`), `census/round-29/records/controls.tsv`,
`SCORECARD.md:17-25` (Round 28 table), `SCORECARD.md:143-175` (Capabilities), `LOG.md:1752-1767`
(Round 28 entry).

## 1. SCORECARD — `### Round 29 measurements` table

Insert directly above `### Round 28 measurements (2026-10-25; base 3a2a80d…)` at
`SCORECARD.md:17`. Column layout copied from `SCORECARD.md:19`: `claim | axis | before | after |
counting command | measured commit`. Keep the axis cell in the Round 28 style (`axis <score>`).
`<AFTER>` is filled only from the counter's own output shape (r28 routed defect 4); a value
read from a different command belongs in a note, not the cell.

```markdown
### Round 29 measurements (2026-10-25; base 691dd29211c53d0ef94fa072394cb9c8a69fe92e)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 declared-record agreement | calibration 7 | `SUMMARY k1=6 k2=4 mismatches=10` at base (`census/round-29/records/controls.tsv`, `C1-do-nothing(base)`) | `<AFTER>` | `python3 -B tools/souji-registry-agreement.py --root <lane> --rev <full40> --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804`; before receipt `census/round-29/records/controls.tsv` | `<MEASURED>`; after receipt `<census/round-29/records/c1-after.tsv>` |
| C2 committed-bytes wave evidence | operability 8 | `SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0` at base (`census/round-29/records/controls.tsv`, `C2-do-nothing(base)`) | `<AFTER>` | `python3 -B census/round-29/c2-counter.py --root <lane> --rev <full40>`; fixture `<bash tests/fixtures/r28-wave-evidence-capture.sh>` | `<MEASURED>`; after receipt `<census/round-29/records/c2-after.tsv>` |
| C3 F3 duplicate-verdict coverage | coverage 8 | `F3_entries=0 rows=139` (`census/round-29/records/controls.tsv`, `C3-do-nothing(base)`) | `<AFTER>` | `git grep -lE '^ground: F3' <rev> -- corpus/knowledge/ \| wc -l`; `git show <rev>:corpus/SOURCES.md \| grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'`; after receipt `<census/round-29/records/c3-after.tsv>` | `<MEASURED>` |
```

Notes for the filler:

- C2's frozen target also names the final tip (`manifests=4`). Add it as its own measurements
  row or as a sentence under the table, at a second `<MEASURED-TIP>`; do not widen the C2 cell.
- C3 also carries the agreement/gate/census readings (`grounded=…`, `entries=2 ok=… fail=…`,
  sources-census rc). Put them in the after cell only if they are the same counter family;
  otherwise a following paragraph, as Round 28 did for its misses.
- Add the Round 28-style closing paragraph only as measured:
  `<no owned score changed (calibration 7, coverage 8, operability 8) | axis change: …>` and
  `<round admission claimed / not claimed: …>`.

## 2. SCORECARD — Capabilities rows

Append after the last Capabilities row, `| coverage-map agreement (r24) | … |`
(`SCORECARD.md:175`, inside the table that starts at `SCORECARD.md:145`). Same four columns:
`name | what it can now do | evidence pointer | first-working round`. Both rows are conditional
on their demonstration passing; delete a row that does not.

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| declared-record agreement audit (r29) | compare two declared self-assessment records with committed bytes at a named revision, read-only git plumbing and never the working tree: K1 flags a SOURCES.md row whose `used-by` path is absent or does not name the row id, and a knowledge entry whose `source:` lines cite an `S###` row that does not list that entry in `used-by`; K2 accepts a frozen stale statement only when its phrase still sits at file:line and the same file carries a later `R29-CORRECTION file:line` line, so an in-place edit is a mismatch. Prints `SUMMARY k1=<a> k2=<b> mismatches=<a+b>`; exit 0 only on mismatches=0 | `tools/souji-registry-agreement.py`; fixture `<tests/fixtures/r29-registry-agreement.py>`; receipt `<census/round-29/records/c1-after.tsv>` | r29 `<enters only if the demonstration passes>` |
| committed-bytes wave-evidence capture (r29) | capture a round's `.ufo/waves/` evidence into `census/round-<N>/waves/` so the receipt verifies over committed bytes rather than the lane disk: nested `.gitignore`/`.gitattributes` stored as `<name>.captured` and recorded in `renames.tsv` so copied rules cannot make the receipt ignore itself; a destination path git ignores is not copied and is recorded in `excluded.tsv` with its source digest and reason; a symlink is copied verbatim, recorded with its exact target in `symlinks.tsv` and carries no manifest record; GNU backslash-escaped records for newline/backslash names; `--verify --rev <full40>` re-checks the manifest against committed blobs. Tamper control still rejected | `tools/souji-wave-evidence-capture.sh`; fixture `tests/fixtures/r28-wave-evidence-capture.sh` (base prints `cases=6 pass=6 control=TAMPER-REJECTED`); receipts `<census/round-26/waves/>`, `<census/round-29/records/c2-after.tsv>` | r29 `<enters only if the demonstration passes>` |

Do not claim a case count above six unless the extended fixture's own run prints it at a
`<MEASURED>` revision.

## 3. LOG.md entry

Append after the current last line (`LOG.md:1767`), in the Round 28 style
(`LOG.md:1752`). Heading fixed as below; body lines are placeholders.

```markdown
## 2026-10-25 — Round 29 attempt 1: declared-record agreement, committed-bytes wave evidence, F3 duplicate verdicts

Three claims were frozen in `census/round-29/records/preregistration.txt` at base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`; the preregistration, counters, stale-statement list and controls were committed at `b8cb4b31ce80e2e3314b88e85d40ea9873180804`.

- C1 calibration: `tools/souji-registry-agreement.py` prints `SUMMARY k1=6 k2=4 mismatches=10` at base (`census/round-29/records/controls.tsv`); after `<AFTER>` at `<MEASURED>` and again at the tip `<MEASURED-TIP>`. The four frozen stale statements (`LOG.md:1758`, `SCORECARD.md:23`, `corpus/lessons/round-28.md:22` and `:40`) were corrected append-only with `R29-CORRECTION` markers (`<marker locations>`); `<n>` `used-by`/`status` cell changes are logged old→new in `corpus/lessons/round-29.md`.
- C2 operability: `census/round-29/c2-counter.py` prints `SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0` at base; after `<AFTER>` at `<MEASURED>`; final tip `<AFTER-TIP>` (`manifests=<m>`). Capture tool and fixture changed as recorded in SCORECARD's r29 capability row; r26 re-captured to `<records/failed/uncovered>`; the superseded r26 receipt stays in git history and the supersession is logged at `<location>`.
- C3 coverage: F3-grounded entries `0`→`<AFTER>`, SOURCES rows `139`→`<AFTER>`; gate `<entries=2 ok=? slice_verdicts=? slice_total=8 fail=?>`; coverage agreement `<grounded=? mapped=? dangling=0 mismatches=?>`; fleet sources census `<rc>`. Admitted `corpus/knowledge/duplicate-verdict-identity.md` and `corpus/knowledge/duplicate-verdict-byte-equality.md` on rows S216-S219; Gate reject `<entry> — <reason>`.
- Frontier: S216 (statx), S217 (link), S218 (cmp), S219 (Broder via the author-hosted PDF because the DOI landing page returned 202/0 bytes); S118 re-check `<verdict>`; collision guard proved on a scratch indented row at `<location>`; snapshots in `census/round-29/sources/` `<n>` files, `<verification>`.
- Mistake mined: `<one-line mistake>`; `corpus/lessons/round-29.md` `## Mistakes`; captured-by none; the counter pair at base shows it red-before (`<receipt>`).
- Wave: one v2 wave; frozen sizing 68 seats (executor 21, reviewer 8, critic 8, mutation-tester 6, scout 7, scribe 10, connector 3, sentinel 2, simplifier 2, revenger 1) per the preregistration; L1 held the planner seat; seat reports on disk `<n>`; dispatcher results `<location>`.
- Axis verdict: `<no owned score changed (calibration 7, coverage 8, operability 8) | …>`; `<round admission claimed / not claimed: …>`.
- Tools installed/updated: `<none | tool version channel reason>`; certification OFF, K5 HELD, F5 reap and NAMESPACE holds unchanged. Assimilation: F3 duplicate-verdict theme from `/home/vgpnk/Projects/shokuknow/merge/souji/` (read-only); `considerthese/` absent in this lane. No unrelated fleet file was swept.
```

## 4. SCORECARD — Planned bullet for r30

Append after the r28 bullet (`SCORECARD.md:223`, the last bullet before `## Saturation /
stagnation` at `SCORECARD.md:224`). `SCORECARD.md` is committed, so cite only committed
paths; a `.ufo/waves/` receipt path is not a valid pointer once `.ufo/waves/` is gitignored.

```markdown
- **r30 (planned r29):** operability: close the r28 routed defect 3 — `tools/souji-landing-gate.py`
  looks for round reports under the now-gitignored `.ufo/waves/`, so its report check can never
  evaluate committed reports and the gate stays at permanent rc 2 `COULD-NOT-EVALUATE`; point it
  at the committed `census/round-<N>/waves/` capture instead. Calibration: sweep the
  stale-statement remainder the four frozen r29 rows do not cover, i.e. the further disagreeing
  and unverifiable statements in the same round-28 record — `LOG.md:1748` (r26 leftover count with
  no committed receipt), `LOG.md:1758` (r26 capture described as verified), `corpus/lessons/round-28.md:21`
  (`grounded=11 mapped=11` under an unnamed revision) and `:22` (r26 capture and the "two malformed
  records" limitation) — append-only, counted by the r29 K2 instrument and recorded in
  `<census/round-29/records/<stale-sweep receipt>.tsv>`; `<n>` statements remain after r29.
```

The same bullet may carry the C3/C1 residuals only with a committed pointer each; leave
`<...>`-free text out of the committed file.
