# Round 26 — landing-gate re-run recipe

Scope: how to re-run `tools/souji-landing-gate.py` at the round-26 landing tip, what classes it
can emit on this round's changes, and every repo-relative path this round adds, so the gate input
is complete. Tool bytes are unchanged this round (`tools/souji-landing-gate.py` is not in
`0eca7c8..e0f8dcd`).

## CLI (confirmed from `--help` at e0f8dcd)

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
TIP=$(git -C "$LANE" rev-parse HEAD)      # full 40-hex landing commit, after reports + lesson land
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
   at the tip you name. The lesson is committed as of `ea0bbe6`, but without a
   `## Seat-reported failures` section the carry match has no target.
2. **Keep `--base 0eca7c8…`.** Without it `checked_changed=0` and this round's six new scripts are
   never syntax-checked (the registry arm cannot see them either — see §B).
3. **Keep `--fleet-root /home/vgpnk/Projects/shokunin`.** Without it three fleet-only hyaku
   citation tokens are reported as lane findings (5 findings instead of 2 at e0f8dcd; 4 instead of
   1 at 0c92c2e).
4. **`--json` refuses overwrite** (`tools/souji-landing-gate.py:2288`): use a fresh path per run.
5. Ambient `GIT_*` variables are stripped by the gate, so `--root` alone selects the repository.

## Gate inputs this round changes — complete new-path inventory

41 paths are added/modified in `0eca7c8..0c92c2e` (A = added, M = modified; 40 of them at
e0f8dcd, plus the round lesson at `ea0bbe6`); the wave report set lands on top. Grouped by the gate
arm that consumes each one.

### A. Authority files the pointer arm reads (LG-DANGLING-PTR)

- `SCORECARD.md` (M) — C1 region; two new planned bullets and the r24 payload moved above `### Round 23 measurements`
- `corpus/README.md` (M) — F1 row now names both entries; `:46` frontier line
- `corpus/knowledge/git-auto-maintenance-trigger-set.md` (A) — entry A
- `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md` (A) — entry B
- `corpus/lessons/round-26.md` (A, `ea0bbe6`) — the round lesson: a pointer source and the carry target

Not a pointer source (verified against the source set at `tools/souji-landing-gate.py:916-932`):
`corpus/SOURCES.md` (M). Its five new row bodies and `used-by` cells are validated by C2 K3
(`scripts/sources-census.sh`), not by this gate. `SKILL.md` is unchanged.

### B. Scripts the `--base` arm parse-checks (LG-PARSE-CHANGED), 6

- `census/round-26/c1-counter.sh`
- `census/round-26/c2-counter.sh`
- `census/round-26/c3-counter.sh`
- `tools/souji-axis-check.py`
- `tests/fixtures/r26-axis-check.py`
- `.ufo/waves/round-26/make-spec.py`

None is cited in `SKILL.md`, so `checked_reg` stays 50 and the registry arm gives the new tools
**zero** coverage: `--base` is the only parse coverage this round.

### C. Receipts / records (9) — no gate arm; listed so the landing checklist is complete

- `census/round-26/records/c1-before.tsv`, `c1-after.tsv`
- `census/round-26/records/c2-before.tsv`, `c2-k4-base.tsv`
- `census/round-26/records/c3-before.tsv`, `c3-after.tsv`, `c3-control.tsv`
- `census/round-26/records/empty-slice`, `census/round-26/records/empty-verdicts`

At 0c92c2e `c2-after.tsv` is present; `c2-k4-after.tsv` and `c2-gate.tsv` (named by prereg C2)
are still absent. The gate does not check these; the C2 owner does.

### D. Source snapshots (8) — cited by the entries, therefore pointer-resolved

- `census/round-26/sources/SHA256SUMS`
- `census/round-26/sources/git-builtin-am.c`, `git-builtin-commit.c`, `git-builtin-fetch.c`,
  `git-builtin-merge.c`, `git-builtin-pull.c`, `git-builtin-rebase.c`
- `census/round-26/sources/git-fetch.1.txt`

Entry A cites `census/round-26/sources/git-builtin-{fetch,merge,rebase,am,commit}.c` and
`git-fetch.1.txt`; all resolve at e0f8dcd (brace expansion exercised, 0 findings on them).

### E. Wave dir — 13 committed, plus the report set at commit time

Committed at e0f8dcd:

- `.ufo/waves/round-26/preregistration.txt`, `preregistration-amendment-1.txt`,
  `preregistration-amendment-2.txt`
- `.ufo/waves/round-26/make-spec.py`, `census-before.txt`, `w1-spec.json`,
  `w1-dispatch.json`, `w1/swarm-registry.json`, `w1.ready`, `w1-validate.out`, `w1-validate.err`
- `.ufo/waves/round-26/assimilation/quarantine-slice`,
  `.ufo/waves/round-26/assimilation/slice-verdicts-r26.tsv`

Landing must additionally commit, or the carry arm cannot evaluate:

- every `.md` under `.ufo/waves/round-26/` (all untracked while the wave runs; 54 at the last read
  of this seat, still growing) — the gate's `checked_reports` is exactly the committed count, so
  resolve it at commit time with
  `git -C "$LANE" ls-tree -r --name-only "$TIP" -- .ufo/waves/round-26 | grep -c '\.md$'`;
- `corpus/lessons/round-26.md` — committed at `ea0bbe6` with `## Gate`, `## Findings`, `## Residuals`,
  `## Receipts`; still missing `## Seat-reported failures`, the carry target (§F);
- a round-26 section in `LOG.md` (absent at 0c92c2e: 0 matches for `round 26`, no LOG.md diff from
  base; the gate scans the LOG arm's round-N section, and the prereg amendment rule requires LOG.md
  logging).

### F. Carry burden already in the work tree (gate input the moment the reports commit)

Measured at this read with the gate's own `status_line_count` / `seat_failure_lines`: 54 reports,
39 STATUS lines, **12 failure markers**. `corpus/lessons/round-26.md` at 0c92c2e has no
`## Seat-reported failures` heading (`carry_heading=0`), so committing the reports as they stand
would emit 12 `LG-SEAT-UNCARRIED` findings. Each needs a matching paragraph in
that lesson under `## Seat-reported failures`, quoted whole or cut at one of the
SOURCE's physical line ends and followed by an ellipsis (mid-line ellipsis never carries):

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
- `.ufo/waves/round-26/w1/ScribeLogR26.md:8` (PARTIAL)
- `.ufo/waves/round-26/w1/SentBounds.md:3` (PARTIAL)

These are work-tree bytes: they enter the gate only if committed at the named `--rev`. Re-measure
after every report rewrite; a report changed to `STATUS: PASS` removes its marker.

## Expected classes at the landing tip

| class | fires when | measured at 0c92c2e (tip at this read) | required at landing |
|---|---|---|---|
| LG-DANGLING-PTR | any authority-file citation resolves to no tree path at REV | 1 inherited only at 0c92c2e (round-caused cleared by ea0bbe6); was 2 at e0f8dcd, 5 without `--fleet-root` | round-caused = 0 |
| LG-SEAT-UNCARRIED | a committed round-26 report line in the STATUS failure channel is not carried in the lesson's `## Seat-reported failures` | unexercised at 0c92c2e (`checked_reports=0`, `carry_heading=0`, exit 2); the work tree holds 54 reports, 39 STATUS lines, 12 failure markers (measured with the gate's own `seat_failure_lines`) | 0 uncarried; every one of the 12 carried or the seat's report rewritten |
| LG-OPEN-ADMITTED | a carried failure says `open` while the lesson declares `admitted: true` | unevaluated | 0 |
| LG-PARSE-CHANGED | any of the 6 new scripts fails `bash -n` / `compile()` | 6 checked, 0 findings | 0 |
| LG-PARSE-REG / LG-MISSING-REG | a `SKILL.md`-cited script fails to parse or is absent | 50 checked, 0 findings | 0 |
| LG-FROZEN-PIN / LG-FROZEN-MEASURED | pinned bytes or `measured_commit` disagree | 13 pins / 3 measured, 0 findings | 0 |
| LG-DANGLING-PTR-EXEMPT-STALE | an exemption row suppresses nothing | 4 rows, all used (`ptr_exempt=4`) | 0 |

The round-caused pointer this round produced, now closed:

```
LG-DANGLING-PTR  corpus/lessons/round-26.md  corpus/knowledge/git-auto-maintenance-trigger-set.md:52 cites path absent at e0f8dcd12b1d
```

Measured at e0f8dcd (lesson not yet committed); gone at 0c92c2e, where `ea0bbe6` committed
`corpus/lessons/round-26.md` with a `## Gate` section, which is the locator
`corpus/knowledge/git-auto-maintenance-trigger-set.md:52` ("this round — see") points at. What the
lesson still lacks at 0c92c2e is `## Seat-reported failures` (`carry_heading=0`) — see §F.

The inherited pointer, present at base 0eca7c8, at the r25 landing 728b2ce, and still at the r26 tip:

```
LG-DANGLING-PTR  corpus/lessons/round-24.md:232:S118  corpus/QUALITY.md:141 cites path absent at …
```

`corpus/QUALITY.md:141` (Q57) carries the token `corpus/lessons/round-24.md:232:S118`; the pointer
grammar trims only a trailing `:N` or `:N-M`, so the `:line:id` form floats. It arrived with the r25
integration `728b2ce` (`git log -S` on the token). **Consequence: a findings=0 landing is impossible
unless the L1 either repairs that token or adds a reasoned `corpus/pointer-exemptions.tsv` row**
(and an exemption that suppresses nothing becomes LG-DANGLING-PTR-EXEMPT-STALE). Report the
inherited class explicitly rather than claiming a clean gate.

## Exit-2 preconditions — a could-not-evaluate run is not a pass

- `no .md reports under .ufo/waves/round-26/ at <rev>` — wave reports not committed yet (the
  current tip state). Pointer findings are still printed with exit 2 (r18+), so read both lines.
- unknown rev / `--root` not a repo / missing `SKILL.md` / malformed `pointer-exemptions.tsv` /
  git failure — fix the invocation, do not report the findings as a verdict.

## Reading the SUMMARY

Field meanings that matter here (`checked_*` zeros mean unexercised, never passed):
`checked_reg`=50 (SKILL.md registry), `checked_changed`=6 only with `--base`, `checked_pins`=13,
`checked_measured`=3, `checked_markers`=STATUS failure-channel lines in the committed reports (the
work tree stands at 39 status lines / 12 markers), `status_lines` counts all
STATUS lines in committed reports, `carry_heading`=1 only if the lesson has
`## Seat-reported failures`, `checked_reports`=committed round-26 `.md` count. Bind the actual numbers
from the run's `--json`, never from this document.

## Triage of a finding

1. path under `../.ufo/waves/hyaku/` or `.ufo/waves/hyaku/` that exists under
   `/home/vgpnk/Projects/shokunin` → classified `fleet` (only with `--fleet-root`); not a lane finding.
2. `corpus/QUALITY.md:141` → inherited r25 token; pre-existing, needs the L1 repair/exemption decision.
3. any `corpus/knowledge/*.md` citing `corpus/lessons/round-26.md` → round-caused; land the lesson.
4. anything else → round-caused; fix before the landing commit, then re-run at the new tip.
