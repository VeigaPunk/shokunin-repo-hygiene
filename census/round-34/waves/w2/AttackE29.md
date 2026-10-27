# AttackE29 — r34 w2 adversarial falsification of W1's E29 finding

Seat: SwarmCritic23. Target: C1 item E29. Base `9c76c7222a8abff027af42e37f0d160d52526bba`; frozen list `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`; C2 repair/re-pin `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`.

## Status

**W1's E29 finding is CONFIRMED, not falsified.** The do-nothing mismatch reproduces byte-for-byte under an independent re-run (`rc=1`, last digit-bearing line `SUMMARY legs=11 fail=4 f1_entries=5 rev=9c76c7222a8abff027af42e37f0d160d52526bba`), the failure is deterministic committed-text drift (not a measurement artifact, not load- or environment-sensitive), and W1's "no prior correction row" Q76 sweep independently re-verifies.

Additional seat finding beyond W1: **under the frozen counter's restatement-cause rules, E29 admits no honest Q76 restatement route** — the unique True→False transition commit `a92e1aae91dbf46c2d7eff713932cfc820186970` touches none of the item's files (`census/round-31/c3-counter.py`), and the only commit that wrote the bound line (`f950267…`) is the r31 measurement commit where the frozen argv demonstrably holds. Flagged for the canonical judge as a frozen-rules tradeoff (see Findings 4).

## Evidence

Frozen item (c1-items.tsv:74 at `2b0171e2`):
`E29 | SCORECARD.md:414 | exit 0 | SUMMARY legs=11 fail=0 f1_entries=4 | census/round-31/c3-counter.py | {REV} | python3 -B census/round-31/c3-counter.py --root . --rev {REV} --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`

The bound cell is the Round-31 measurements C3 row; line 414 at base equals line 414 at list-rev byte-for-byte (append-only holds):

```
$ git show 9c76c722…:SCORECARD.md | sed -n '414p' | cut -c1-120
| C3 F1 dropped-keep-ref object lifetime entry | coverage 8 | v1 `SUMMARY legs=11 fail=10 f1_entries=3`; v2 `SUMMARY legs=12 fail=11 f1_entries=3` | at the landing commit and again at the tip v1 `legs…
```

W1 readings being tested:
- `.ufo/waves/round-34/w1/deliver-c1-do-nothing-check.txt:63` — `ITEM E29 MISMATCH original rc=1 expect_exit=0 predicate fails last=SUMMARY legs=11 fail=4 f1_entries=5 rev=9c76c72… load=42.31`
- `.ufo/waves/round-34/w1/SwarmExecutor13.md` mismatch table — E29 = "value drift", prior correction row: none
- committed L1 record `census/round-34/records/controls-c1-do-nothing.txt:58` — identical verdict line (load=10.25)

Independent reproduction (this seat, actually executed; lane repo read-only, scratch `/fast/scratch/hyaku/souji-r34/E29`):

```
$ cd /fast/scratch/hyaku/souji-r34/E29 && python3 -B …/census/round-31/c3-counter.py \
    --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 9c76c7222a8abff027af42e37f0d160d52526bba \
    --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --scratch …/E29/cnt
L1 FAIL f1_entries=5
L2 FAIL coverage="grounded=18 mapped=18 dangling=0 mismatches=0"
L3 PASS … L4 PASS … L5 FAIL quotes=12 bad=['recent', 'now']
L6 FAIL cited=[… S222] missing=[] new_opened_today=['S222'] url_unbound=['https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config/gc.adoc,']
L7 PASS … L8 PASS run_record=present results=17
L9 PASS replays=[(0, 17, True), (0, 17, True)]
L10 PASS … L11 PASS sources-census rc=0
SUMMARY legs=11 fail=4 f1_entries=5 rev=9c76c7222a8abff027af42e37f0d160d52526bba   (RC=1)
```

Environment ruling out artifact readings (actually executed): `jj --version` = `jj 0.45.1-…`, `git --version` = `git version 2.56.0` — both match the RUN record's required prefixes; L9's two fixture replays both exit 0 and match the committed RUN's 17 RESULT lines exactly; wall time 1.77 s at low load reproduces W1's load=42.31 reading exactly, so the verdict is load-invariant.

Drift provenance (actually executed):
- `git grep -lE '^ground: F1\b' 9c76c72… -- corpus/knowledge/` → 5 files; at `a92e1aa^` → 4 files (original holds at the parent).
- `git log 2c16d018e40d..9c76c72 -- census/round-31/c3-counter.py` → **empty** (the instrument file was untouched post-r31).
- `git show a92e1aa -- corpus/knowledge/jj-dropped-keep-object-lifetime.md` adds the Gate quotes containing `"recent"` and `"now"` (verbatim git-gc quotes, 1 word each → L5) and the prose URL `…/gc.adoc,` with trailing comma, not present in any cited row's cell (L6). The same commit adds the mtime-clock F1 entry (L1) and its S223 row (coverage 17→18, L2).
- Ancestry (all `git merge-base --is-ancestor` returned 0): `2c16d018e40d… ≤ a92e1aae91dbf46c2d7eff713932cfc820186970 ≤ 9c76c72…` and `a92e1aa… ≤ 2b0171e2…` (a valid potential cause ancestor).
- Q76 sweep re-run: `git show 9c76c72…:SCORECARD.md | grep -nE 'SCORECARD\.md:414([^0-9]|$)'` → no hits; `grep -n 'E29'` → no hits. No prior correction row; no SKILL.md pointer.
- Line-414 writer: `git log -S 'C3 F1 dropped-keep-ref object lifetime entry' -- SCORECARD.md` → `f950267` (`f950267893340096964ae8ceb7116f6789d7c87b`, "round-31: … SCORECARD r31 measurements …"). Frozen-argv probe at that commit (actually executed):
  `SUMMARY legs=11 fail=0 f1_entries=4 rev=f950267893340096964ae8ceb7116f6789d7c87b`, RC=0 — the original holds at the line's author commit.

## Findings

1. **W1's E29 verdict reproduces exactly; classification ("value drift") is correct.** Independent run at base yields `rc=1`, `fail=4 f1_entries=5`, identical to W1 (`.ufo/waves/round-34/w1/deliver-c1-do-nothing-check.txt:63`), the committed record (`census/round-34/records/controls-c1-do-nothing.txt:58`), and L1's reading. The frozen predicate `SUMMARY legs=11 fail=0 f1_entries=4` is a bare regex over the collapsed last digit-bearing line (`census/round-34/c1-counter.py:141-169` `frozen_pred`); the observed line fails it on both `fail=0` and `f1_entries=4`.
2. **The drift is real committed-text drift with a single identified cause.** All four failing legs (L1 f1_entries 4→5; L2 coverage 17/17→18/18; L5 new 1-word Gate quotes "recent"/"now"; L6 unbound gc.adoc URL) trace to round-32 commit `a92e1aae91dbf46c2d7eff713932cfc820186970`, which extended the very ENTRY the r31-v1 counter measures. Not a counter bug, not env, not load: the replay legs L8–L10 pass and versions match the frozen record.
3. **W1's Q76 sweep is confirmed.** No pointer row `SCORECARD.md:414` and no `E29` mention exist in base SCORECARD.md; the E29 cell is genuinely un-restatement-bound.
4. **No honest rule-conforming route exists for E29 under the frozen judge (seat finding beyond W1).** Two mechanical paths, both blocked by execution-verified facts:
   - `same`-kind value-drift restatement (`census/round-34/c1-counter.py:288-297`) requires a cause that touches one of the item's files (`item["files"] = ["census/round-31/c3-counter.py"]`, c1-items.tsv:74). The only True→False transition commit is `a92e1aa` (original verified to hold at `a92e1aa^` with f1=4; fails from `a92e1aa` through base), and `git log 2c16d018..base -- census/round-31/c3-counter.py` is empty, so no eligible cause exists. Any row citing `a92e1aa` returns BAD-ROW(cause touches none of the item files).
   - argv-correction kind (`c1-counter.py:298-310`) requires the cause to have written the bound line with the row's own argv already failing at the cause. The only line-414 author is `f950267…`, where the frozen argv demonstrably **holds** (probe above: `fail=0 f1_entries=4`, RC=0), so BAD-CAUSE.
   Hence E29 cannot be moved to AGREE by any honest r34 restatement; only lane-content reverts (dishonest: they would falsify r32's landed C3 v2 work, which E33's own frozen statement `legs=14 fail=0 f1_entries=5` legitimately depends on) or a judge-level rule interpretation could change the verdict. This is a frozen-rules reachability tradeoff for the canonical judge, not a defect in W1's finding.
5. **No duplicate finding.** Sibling w2 seats cover E27/E31/E25/E23b/etc.; this report is the sole E29 seat report in `.ufo/waves/round-34/w2/` at write time.

## Attack log

Adversarial attempts against W1's reasoning, each actually executed:
1. *Measurement-artifact hypothesis* (high load during W1's run, E29 ran at load=42.31): **falsified** — my low-load run (load≈1, wall 1.77 s) reproduces the identical SUMMARY and rc.
2. *Environment-drift hypothesis* (fixture replay legs could fail on jj/git version drift): **falsified** — jj 0.45.1 / git 2.56.0 installed; L9 replays both equal the committed RUN's 17 RESULT lines; L8/L10/L11 pass.
3. *Instrument-misresolution hypothesis* (counter reading working tree or wrong rev): **falsified** — c1-counter runs items from a detached clone at `--rev` (`c1-counter.py:194-231` `run_item`), and my direct `--root lane --rev base` run gives byte-identical output; f1 count at base confirmed by independent `git grep`.
4. *Benign-alternate-explanation hypothesis* (W1's "value drift" is really counter staleness): **falsified as an alternate to drift, confirmed as drift** — the instrument is unchanged since r31 (empty path log); the measured corpus/SOURCES.md content changed under it.
5. *Missed-honest-route hypothesis* (W1 may have overlooked a Q76-conforming correction): **tested both restatement kinds against `judge()` with git archaeology; both blocked** (Findings 4). W1's "no prior correction / value drift" report stands, and additionally no honest future restatement route exists under the frozen rules.
6. *Predicate-interpretation probe*: frozen statement matched against the run's last digit-bearing line per `frozen_pred`; the observed `fail=4 f1_entries=5` line cannot satisfy the `fail=0 … f1_entries=4` regex — no notation escape (contrast E25's KINDS line case, which does not apply here).

No frozen artifact, lane file, or git/jj state was modified; no tools installed. Scratch confined to `/fast/scratch/hyaku/souji-r34/E29/` (counter self-cleans its tmp; probe output `f950267.out` ~1 KB retained).

## Deliveries

- `.ufo/waves/round-34/w2/AttackE29.md` — this report.
- `.ufo/waves/round-34/w2/SwarmCritic23.md` — seat report (same scoped findings).
- Retained scratch evidence: `/fast/scratch/hyaku/souji-r34/E29/f950267.out` (frozen-argv probe at the line-414 author commit).

Checks main may re-run: the Evidence commands above (counter probe at base; `git log` path queries; Q76 grep; `merge-base --is-ancestor` chain). Expected: identical outputs.
