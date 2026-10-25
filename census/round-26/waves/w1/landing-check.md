# Round 26 — landing-gate re-run recipe

Scope: how to re-run `tools/souji-landing-gate.py` at the round-26 landing tip, what classes it can
emit on this round's changes, and every repo-relative path this round adds, so the gate input is
complete. Tool bytes are unchanged this round (`tools/souji-landing-gate.py` is not in
`0eca7c8..166baa1`).

State was measured at `0c92c2e` (reports uncommitted) and again at `166baa1` (reports committed);
the tip moves as seats land, so **re-run at the tip you are landing and read that run's `--json`,
never this document's numbers**.

## CLI (confirmed from `--help`)

```
usage: souji-landing-gate.py [-h] [--root ROOT] [--rev REV] [--round ROUND_NO]
                             [--base BASE] [--fleet-root FLEET_ROOT]
                             [--json JSON_OUT] [--selftest]
```

Exit contract (`tools/souji-landing-gate.py:32`): `Exit: 0 no findings, 1 findings, 2 could-not-evaluate`.

## The command

Canonical, exactly the shape the contract names:

```bash
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
TIP=$(git -C "$LANE" rev-parse HEAD)      # full 40-hex landing commit, after the wave reports land
python3 -B "$LANE/tools/souji-landing-gate.py" \
  --root "$LANE" --rev "$TIP" --round 26
```

Lane-conventional full run (r18/r21 precedent: changed-script arm, fleet classification, JSON
receipt):

```bash
D=/var/tmp/souji-r26-landing && mkdir -p "$D"
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
TIP=$(git -C "$LANE" rev-parse HEAD)
python3 -B "$LANE/tools/souji-landing-gate.py" \
  --root "$LANE" \
  --rev "$TIP" \
  --round 26 \
  --base 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd \
  --fleet-root /home/vgpnk/Projects/shokunin \
  --json "$D/gate-$TIP.json"
echo "exit=$?"
```

Flag precedent, r18 landing (`corpus/lessons/round-18.md:73`):
`--round 18 --fleet-root /home/vgpnk/Projects/shokunin --json <new>`.

Non-negotiable properties of the run:

1. **Committed bytes only.** The gate enumerates `git ls-tree -r -z --full-tree REV` and reads
   `git cat-file blob`; uncommitted work is invisible. Run it *after* the wave reports are committed
   at the tip you name.
2. **Keep `--base 0eca7c8…`.** Without it `checked_changed=0` and this round's 11 new scripts are
   never syntax-checked (the registry arm cannot see them either — see §B).
3. **Keep `--fleet-root /home/vgpnk/Projects/shokunin`.** Without it the three fleet-only hyaku
   citation tokens are reported as lane findings (2 findings become 5 at 166baa1).
4. **`--json` refuses overwrite** (`tools/souji-landing-gate.py:2288`): use a fresh path per run.
5. Ambient `GIT_*` variables are stripped by the gate, so `--root` alone selects the repository.

## Gate inputs this round changes — complete new-path inventory

134 paths are added/modified in `0eca7c8..166baa1` (A = added, M = modified). Grouped by the gate arm
that consumes each one; the exhaustive list is `git -C "$LANE" diff --name-status <base>..<tip>`.

### A. Authority files the pointer arm reads (LG-DANGLING-PTR)

- `SCORECARD.md` (M) — C1 region and the round-26 measurements block
- `corpus/QUALITY.md` (M) — new Q59 row; `:143` carries the prose token `corpus/knowledge/registry`, which the grammar reads as a path and dangles
- `corpus/README.md` (M) — F1 row names both entries; `:46` frontier line
- `corpus/knowledge/git-auto-maintenance-trigger-set.md` (A) — entry A
- `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md` (A) — entry B
- `corpus/lessons/round-26.md` (A) — the round lesson: pointer source and carry target

Not a pointer source (source set at `tools/souji-landing-gate.py:916-932`): `corpus/SOURCES.md` (M).
Its five new row bodies and `used-by` cells are validated by C2 K3 (`scripts/sources-census.sh`), not
by this gate. `SKILL.md` is unchanged (0 citations of the new tools).

### B. Scripts the `--base` arm parse-checks (LG-PARSE-CHANGED), 11 at 166baa1

- `census/round-26/c1-counter.sh`, `c2-counter.sh`, `c3-counter.sh`
- `tools/souji-axis-check.py`, `tests/fixtures/r26-axis-check.py`
- `.ufo/waves/round-26/make-spec.py`
- `.ufo/waves/round-26/w1/mirror-build.py`, `r26-axis-check.py`, `results-count.py`,
  `souji-axis-check.py`, `verify-loop.sh`

One of them fails today: `verify-loop.sh` → `bash -n rc=2`, unexpected EOF at line 320. Any w1
scratch script that lands is parsed; do not commit a broken one.

### C. Receipts / records — no gate arm; listed so the landing checklist is complete

`census/round-26/records/`: `c1-before.tsv`, `c1-after.tsv`, `c2-before.tsv`, `c2-k4-base.tsv`,
`c2-after.tsv`, `c3-before.tsv`, `c3-after.tsv`, `c3-control.tsv`, `empty-slice`, `empty-verdicts`.
Absent at 166baa1 though named by prereg C2: `c2-k4-after.tsv`, `c2-gate.tsv`. The gate does not
check these; the C2 owner does.

### D. Source snapshots (8) — cited by the entries, therefore pointer-resolved

`census/round-26/sources/SHA256SUMS`, `git-builtin-{am,commit,fetch,merge,pull,rebase}.c`,
`git-fetch.1.txt`. Entry A cites `census/round-26/sources/git-builtin-{fetch,merge,rebase,am,commit}.c`
and `git-fetch.1.txt`; all resolve (brace expansion exercised, 0 findings on them).

### E. Wave dir — reports and scratch

Committed at 166baa1: `preregistration.txt`, `preregistration-amendment-{1,2}.txt`, `make-spec.py`,
`census-before.txt`, `w1-spec.json`, `w1-dispatch.json`, `w1/swarm-registry.json`, `w1.ready`,
`w1-validate.{out,err}`, `assimilation/quarantine-slice`,
`assimilation/slice-verdicts-r26.tsv`, plus the `w1/` report set (`checked_reports=84` at 166baa1).

Landing must also carry:

- `corpus/lessons/round-26.md` — present, with `## Gate`, `## Findings`, `## Residuals`,
  `## Receipts`; still missing `## Seat-reported failures` (`carry_heading=0`), the carry target;
- a round-26 section in `LOG.md` — absent at 166baa1 (0 matches for `round 26`, no `LOG.md` diff from
  base); the gate scans the LOG arm's round-N section and the prereg amendment rule requires it.

### F. Carry burden already committed (18 markers, none carried)

Measured by the gate at 166baa1: `checked_reports=84`, `status_lines=63`, **`checked_markers=18`**,
`carry_heading=0`, so all 18 are `LG-SEAT-UNCARRIED`. Each needs a matching paragraph under
`## Seat-reported failures`, quoted whole or cut at one of the SOURCE's physical line ends and
followed by an ellipsis (mid-line ellipsis never carries):

- `.ufo/waves/round-26/w1/CritAmendNeed.md:5` (PARTIAL)
- `.ufo/waves/round-26/w1/CritCoverageCredit.md:5` (FAIL)
- `.ufo/waves/round-26/w1/CritQ54Gate.md:3` (PARTIAL)
- `.ufo/waves/round-26/w1/CritSourcedClaim.md:5` (FAIL)
- `.ufo/waves/round-26/w1/ExecC1Surgery.md:4` (PARTIAL)
- `.ufo/waves/round-26/w1/LabReceiptVerify.md:5` (FAIL)
- `.ufo/waves/round-26/w1/LabSourcesCensus.md:9` (PARTIAL)
- `.ufo/waves/round-26/w1/RevC1Counter.md:2` (PARTIAL)
- `.ufo/waves/round-26/w1/RevC3Design.md:4` (FAIL)
- `.ufo/waves/round-26/w1/RevEntryDrafts.md:2` (PARTIAL)
- `.ufo/waves/round-26/w1/RevQ59Text.md:7` (PARTIAL)
- `.ufo/waves/round-26/w1/RevR25Residuals.md:2` (PARTIAL)
- `.ufo/waves/round-26/w1/ScribeAxisDocs.md:5` (PARTIAL)
- `.ufo/waves/round-26/w1/ScribeGateDraft.md:5` (PARTIAL)
- `.ufo/waves/round-26/w1/ScribeLessonR26.md:5` (PARTIAL)
- `.ufo/waves/round-26/w1/ScribeLogR26.md:8` (PARTIAL)
- `.ufo/waves/round-26/w1/ScribeScorecardR26.md:5` (PARTIAL)
- `.ufo/waves/round-26/w1/SentBounds.md:3` (PARTIAL)

Re-measure after every report rewrite; a report changed to `STATUS: PASS` removes its marker.

## Expected classes at the landing tip

| class | fires when | measured at 166baa1 | required at landing |
|---|---|---|---|
| LG-DANGLING-PTR | any authority-file citation resolves to no tree path at REV | 2: inherited `corpus/QUALITY.md:141` → `corpus/lessons/round-24.md:232:S118`; round-caused `corpus/QUALITY.md:143` → `corpus/knowledge/registry`. 5 without `--fleet-root` | round-caused = 0 |
| LG-SEAT-UNCARRIED | a committed round-26 report line in the STATUS failure channel is not carried in the lesson's `## Seat-reported failures` | 18, all uncarried (`carry_heading=0`) | 0 |
| LG-OPEN-ADMITTED | a carried failure says `open` while the lesson declares `admitted: true` | 0 (nothing carried yet) | 0 |
| LG-PARSE-CHANGED | any changed script fails `bash -n` / `compile()` | 1: `.ufo/waves/round-26/w1/verify-loop.sh` (rc=2, EOF at line 320); 11 checked | 0 |
| LG-PARSE-REG / LG-MISSING-REG | a `SKILL.md`-cited script fails to parse or is absent | 50 checked, 0 findings | 0 |
| LG-FROZEN-PIN / LG-FROZEN-MEASURED | pinned bytes or `measured_commit` disagree | 13 pins / 3 measured, 0 findings | 0 |
| LG-DANGLING-PTR-EXEMPT-STALE | an exemption row suppresses nothing | 4 rows, all used (`ptr_exempt=4`) | 0 |

Full measured run at 166baa1:

```
SUMMARY  findings=21  checked_reg=50  checked_changed=11  checked_pins=13  checked_measured=3  checked_markers=18  status_lines=63  carry_heading=0  checked_reports=84
EXIT=1
```

History of the round's own pointer delta: at `e0f8dcd` entry A's citation of
`corpus/lessons/round-26.md` dangled (lesson not yet committed, 2 findings); `ea0bbe6` landed the
lesson and closed it (1 finding at `0c92c2e`); `166baa1` added the Q59 row whose prose token
`corpus/knowledge/registry` dangles (2 findings). The Q59 wording needs a real path (or none) before
landing.

## Exit-2 preconditions — a could-not-evaluate run is not a pass

- `no .md reports under .ufo/waves/round-26/ at <rev>` — wave reports not committed yet. Pointer
  findings are still printed with exit 2 (r18+), so read both lines.
- unknown rev / `--root` not a repo / missing `SKILL.md` / malformed `pointer-exemptions.tsv` /
  git failure — fix the invocation, do not report the findings as a verdict.

## Reading the SUMMARY

`checked_*` zeros mean unexercised, never passed: `checked_reg`=50 (SKILL.md registry),
`checked_changed`=11 only with `--base`, `checked_pins`=13, `checked_measured`=3,
`checked_markers`=STATUS failure-channel lines in committed reports, `status_lines`=all STATUS lines,
`carry_heading`=1 only if the lesson has `## Seat-reported failures`, `checked_reports`=committed
round-26 `.md` count. Bind the actual numbers from the run's `--json`.

## Triage of a finding

1. path under `../.ufo/waves/hyaku/` or `.ufo/waves/hyaku/` that exists under
   `/home/vgpnk/Projects/shokunin` → classified `fleet` (only with `--fleet-root`); not a lane finding.
2. `corpus/QUALITY.md:141` → inherited r25 token; needs the L1 repair/exemption decision (an unused
   exemption becomes `LG-DANGLING-PTR-EXEMPT-STALE`).
3. `corpus/QUALITY.md:143` → round-caused by Q59; reword the prose so it names a real path.
4. `.ufo/waves/round-26/w1/verify-loop.sh` → round-caused parse failure; fix or do not commit it.
5. any uncarried STATUS line → carry the paragraph in the lesson, or rewrite the report to `PASS`.
6. anything else → round-caused; fix before the landing commit, then re-run at the new tip.
