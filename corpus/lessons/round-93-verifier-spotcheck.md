author: hyaku closure (non-author integrator, @m_zfl)

# Round 93 verifier spot-check — souji (non-author, hyaku closure)

Lane: `souji-shokunin`, branch `master`. Lane base `91c9bcb1041b18be154ca466ac3c047ac7862fe1` (r92 closed); lane
HEAD after the round `2794527218c938ebe9d1d1c07073ebe598565616`. Report `.ufo/reports/round-93/souji.md`. Closed
2026-11-09 (UTC 04:1x).

Dispatch/complete digest copied from this round's closure prompt (mutable `.ufo/watchdog.log`; the live log shows
the same two lines):

`2026-11-09T00:32:23-03:00 launch souji round=93 pgid=1493374 driver=hyaku-inline attempt=1`
`2026-11-09T01:08:07-03:00 complete souji round=93; hyaku-inline attempt=1`

## 1. Step-1 conformance

- **Report identity: PASS.** `git log --format='%an %ae %H %cI' -- .ufo/reports/round-93/souji.md` ->
  `souji-shokunin souji@shokunin.local 5ee5b521fa946a4c0916794f25431ba40169d56c 2026-11-09T01:07:48-03:00` (before
  the 01:08:07 complete line). Not a marker: six committed round commits, receipts, a source row, a checkable tip.
- **`SHONEN` heading: PASS.** `grep -c '^## SHONEN'` -> 1; four `[~]` lines each with a pointer; `SHONEN.md` has 4
  boxes, `grep -c '\[x\]' SHONEN.md` -> 0; `SHONEN.md`, `SKILL.md`, `PROVINCE.md`, `tools/` unchanged in
  `git diff --name-status 91c9bcb 2794527`.
- **Cited lane commits: PASS.** `git cat-file -e` and `git merge-base --is-ancestor <h> master` exit 0 for
  `2c82d362`, `0d6442cc`, `9a4ab88f`, `7bdb96b7`, `f268ce22`, `27945272` and the base; `git log --oneline
  91c9bcb..2794527` lists exactly these six, all authored `souji-shokunin`, order P1 -> P2 -> F -> A -> wave spec ->
  wave evidence. F (`9a4ab88f`) touches only `census/round-93/preregistration.txt` (80 insertions).
- **Lane state: PASS.** `scripts/hyaku/jj-lane.sh state` -> `branch=master local=2794527… remote=2794527… ahead=0
  behind=0 head=detached tracked=0 untracked=0`; `git status --porcelain` empty; `ls-remote origin
  refs/heads/master` -> `2794527218c938ebe9d1d1c07073ebe598565616`.
- **Prompt: PASS.** `.ufo/prompts/souji-round-93.md` (committed by `souji-shokunin` in `7592eeb8`, 1002 lines) carries
  §1 mission/axes binding (lowest-axis duty), §2 claims, §2b frontier step, §3 L2 floor, §4 report contract (path,
  SHONEN, hash citation, LOG tie), §5 commit/push scope/L0 channel, §6 hyaku addendum, §7 scratch, §8 Amendment 59.
- **Diff shape.** `git diff --stat 91c9bcb 2794527` -> 249 files, 45266 insertions, 0 deletions (append-only round).

## 2. Per-claim re-check (re-measured, not only evidence-verified)

All instruments exported with `git archive 2794527` into `/fast/scratch/hyaku/souji-r93/CloseSoujiR93/x` (removed
after), `TMPDIR` set there. Pins re-derived with `sha256sum` and all match the preregistration: population
`d6439f65…`, harness `1868a570…`, search `6089260b…`, targets `fedb2653…`, counter `fd0a8e24…`, fixture `ed15094e…`,
tool `fc0e35c2…`, probe `f3c84c49…`. The r93 population's first 67 lines are `cmp`-identical to
`census/round-92/c1-false-rows.tsv`; the three appended lines are one comment, LD5 (`ledger-drop`), LD6
(`ledger-trim`).

### C1 — calibration 7: RE-MEASURED, VERIFIES AS NARROWED (A1-A4)

- Before (control), `c1-survivor-search.py … --population census/round-92/c1-false-rows.tsv --lane <lane repo> …
  --jobs 2 --ids census/round-93/c1-targets.json` -> `SEARCH-SUMMARY generated=2 ambiguous=0 uncompiled=0 hung=0
  scored=2 errored=0 killed=0 survived=2`, EXIT 0. Matches `controls/c1-control-r92-population.txt`.
- After, same with `census/round-93/c1-false-rows.tsv` -> `… scored=2 errored=0 killed=2 survived=0`, EXIT 0
  (`a491c22-<-to-<= line=491 killed=yes rc=1`, `h-ok-admits-one line=552 killed=yes rc=1`). Matches
  `records/c1-after.txt`.
- Pristine harness on r93 population -> `ROW LD5 … expect=UNRESOLVED/1 got=UNRESOLVED rc=1 match=yes`, `ROW LD6 …
  expect=MOVED/0 got=MOVED rc=0 match=yes`, `SUMMARY rows=66 mismatches=0 accepted=0 refused_true=0 errors=0`, EXIT 0.
- A3 check (is either kill a crash?): I hand-applied each edit to a copy of the counter (line 491 `len(r) < 3` ->
  `<= 3`; line 552 `counts["resolved"] == len(pop)` -> `>= len(pop) - 1`) and ran the pristine harness: a491c22 ->
  only `ROW LD6 … got=UNRESOLVED rc=1 match=no`, `mismatches=1`, EXIT 1; h-ok -> only `ROW LD5 … got=UNRESOLVED rc=0
  match=no`, `mismatches=1`, EXIT 1. Both kills are semantic and each is made by exactly its own target row.
- A4 confirmed independently: with `--lane` pointing at the plain `git archive` export (not a repo, gitignored inputs
  copied in) both targets read `errored rc=2` and the pristine harness exits 2 (`git clone --shared` of `--lane`
  fails). The numbers hold only against the lane checkout, as A4 states.
- Narrowings A1 (survival, not reachability), A2 (two edits, not clauses), A3 (uncaught exception still scores
  killed) are consistent with what I observed; no widened sentence found.

### C2 — coverage 8: RE-MEASURED, VERIFIES AS NARROWED (A5; no score move, A6)

- Before (control), `c2-forgery-probe.py --fixture tests/fixtures/r92-k4-flagfail.py --tool
  tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work <new>` ->
  F5/F6/F7 `exit=0 tool_pass=20/20 rejected=no`, `FORGERY-SUMMARY forgeries=8 rejected=5 positive=pass`, EXIT 1.
- After, same with `tests/fixtures/r93-k4-flagfail.py` -> F5/F6/F7 `tool_pass=21/22 rejected=yes failed=KFF19`,
  `FORGERY-SUMMARY forgeries=8 rejected=8 positive=pass`, EXIT 0.
- Fixture -> `# KFF19 tool=… payloads=14586 inexact=0`, `# KFF19 … c2-before-tool.py payloads=14586 inexact=3096`,
  `SUMMARY cases=22 tool_pass=22 before_pass=16`, EXIT 0.
- Independence (A5): `_ref_len` (fixture line 370-377) encodes the §8.1.1 boundaries (`0xA0 if b == 0xE0`, `0x9F if
  b == 0xED`); no `.decode(`/`codecs` call in the reference path (the only `.decode` hits are git/subprocess stdout
  at lines 154, 155, 188). Shares excerpt constants with the tool's contract, as A5 says.
- K4 regression evidence-verified (not re-run): `records/c2-k4-regression.txt` `SUMMARY rows=12 mismatches=0
  errors=0`, EXIT 0. Tool bytes unchanged across the round.

### Pre-file falsification ledger (Amendment 59)

`python3 scripts/hyaku/prefile-falsification.py --lane souji --round 93` -> `PREFILE-FALSIFICATION: pass claims=2
rows=23 attack_seats=8 findings=0`, EXIT 0. Every `falsifies-wording` row points at `plans/round-93.md`; the rows I
re-derived (R93ReviewerC1 receipts, R93Sentinel `h-crash3.out`, R93Critic) are the ones the A1/A3/A5 narrowings
answer. No unreconciled row.

### Axis verdicts

| axis | verdict | basis |
|---|---|---|
| calibration | improved | 0/2 -> 2/0 kills re-measured; semantic kills confirmed by hand-applied mutants; score held at 7 (no mapping) |
| coverage | improved | cut-position edge class: forgeries rejected 5/8 -> 8/8 re-measured; score held at 8 (A6) |
| operability | unchanged | not claimed; SCORECARD diff adds only r93 rows, no owned axis value changed |

No owned axis harmed: `git diff 91c9bcb 2794527 -- SCORECARD.md` is append-only (r93 measurement rows, capability
rows, `### Planned (r94)`), no `-` lines; zero deletions repo-wide.

## 3. Discernment spot-check (`corpus/lessons/round-93.md` `## Gate`)

Re-opened source: `curl -sSL https://encoding.spec.whatwg.org/` -> HTTP 200, 591022 bytes, sha256
`e1421f1791b202717883c452a6267129ce5fb3ca13652e5022a2b6d2a11fc262` (byte-identical to the S356 capture); anchor
`id="utf-8-decoder"` present; quotes counted in whitespace-normalized tag-stripped text.

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S356 WHATWG Encoding §8.1.1 UTF-8 decoder | ADMIT (spec, A, mined) | live page, sha256 identical | agree | quote "If byte is 0xE0, then set UTF-8 lower boundary to 0xA0. If byte is 0xED, then set UTF-8 upper boundary to 0x9F." found once, 22 words (<=25); these exact boundaries are what `_ref_len` encodes, so the row grounds C2's reference cut |
| §8.1.1 BOM-precedence sentence | REJECT (not filed) | same live page | agree | quote found, 21 words, 2 occurrences as the lesson says; it governs label/BOM precedence at the decode entry, which no r93 claim reads; flip condition stated |
| Python `codecs` `surrogatepass` | REJECT (no new row; S351 covers the URL) | `corpus/SOURCES.md` S351 row | agree | S351 already registers docs.python.org/3/library/codecs.html; a second row would only add a W04 duplicate |

New `SOURCES.md` row re-opened: S356 (the only `+` line in `git diff --numstat 91c9bcb 2794527 -- corpus/SOURCES.md`
-> `1 0`); its quote is the 22-word line above, verified present. Row count `grep -cE
'^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` -> 277 at base, 278 at tip.
`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` -> `souji ok`, EXIT 0 (W04 duplicate
URL warnings only, pre-existing).

## 4. Trend verdicts

- **expansion: improved.** One admitted tier-A spec row (S356, live byte-identical) and a knowledge entry
  (`corpus/knowledge/utf8-cut-position-reference.md`) on ground the lane did not hold (exact cut position vs r92's
  prefix/suffix faithfulness).
- **quality: improved.** Two counter edits that survived every r92 row are now bound by semantic row mismatches, and
  three forgeries the r92 fixture accepted are refused — all re-measured by me on committed bytes.
- **discernment: improved.** The admit/reject sample above agrees on all three items; the lane narrowed four sentences
  its own wave falsified (A1, A3, A5 + A4 limit) before filing instead of defending them, and held both scores.

## 5. Routed defects (lane fixes next round)

1. C1 harness is not reproducible from committed bytes (A4; independently confirmed: plain export -> `errored rc=2`).
   Make the two gitignored inputs committed or pinned, or fail with a named precondition error.
2. Kill rule still scores an uncaught counter exception (exit 1, `got=-`) as killed (A3, Q170); re-score r93 targets
   under the corrected rule.
3. Clauses, not spellings: m5/m6/g2 survive the r93 population (A2); 76 residual survivors still unclassified.
4. KFF19 is one payload length (230) and one filler (`a`); add a second length/filler and catch in-process
   exceptions in the fixture scorer (R93Sentinel M2).
5. `c2-forgery-probe.py` aborts with a traceback (`FileExistsError`, exit 1) when `--work` already exists — an exit 1
   indistinguishable from "a forgery survived"; make it accept an empty existing dir or exit with a distinct code.

Operator note: SHONEN boxes remain `[~]` (author-asserted); the four pointers are checkable by a non-author, but
promotion is operator-owned and not acted on here.
