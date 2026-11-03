# S56mutation01 — mutation tester, C1 kill power (souji round 56, wave w1)

Role: mutation-tester. Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` (read-only).
Measured revision: `cce21b555a617cadda782613ec1e9d3a0c12ac83` (base `fafe371694fea41c5d23f63083865d5ccf3f1d36`).
Seat scratch (deleted before yield): `/fast/scratch/hyaku/souji-r56/S56mutation01/`.
Host: Linux 7.2.11-arch1-1, Python 3.14.8, disk-guard free 405.5G at start (no ENOSPC).

VERDICT: ATTACK-FOUND
VERDICT: SURVIVORS (M1 PAIR-FILING-HIDDEN emission; M7 LF-only numstat parse)

## 1. Frozen pins — all eight verified before any probe

`git -C <lane> show cce21b55:<path> | sha256sum` (full table: `receipts/pins.txt`, all `MATCH`):

| path | observed |
|---|---|
| census/round-56/c1-counter.py | `975d3520…63bcbbf179` |
| census/round-56/c2-counter.py | `56082011…d59c2598cb8` |
| census/round-56/fixtures/build-fixtures.py | `2f26d6aa…da1c30b85a` |
| census/round-56/fixtures/run-matrix.sh | `a7e1a892…112962de3` |
| census/round-56/records/c1-selftest-expected.tsv | `48a7cc0e…aa3f7c5bfb` |
| census/round-56/records/c2-selftest-expected.tsv | `90517c4d…6c926841b3` |
| census/round-55/c1-counter.py | `944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2` |
| census/round-55/c2-counter.py | `e4eb34e6…c994a568c` |

No pin mismatch. Nothing was read from the lane working tree for claim purposes and no frozen
byte was edited anywhere.

## 2. Detector and method

Detector (unchanged for pristine / mutated / restored bytes):

```
python3 -B <counter> --selftest --work <per-run work dir> \
  --builder-sha256 2f26d6aa68ce44cfd9e4afdeaa4ef04837db7622c5ed5213429d8bda1c30b85a \
  --expected-sha256 48a7cc0e869773b493b0b5f01446f70b9016595f1c307602912317aa3f7c5bfb
```

The detector asserts, per fixture, `(exit code, first FINDING id)` against the committed 33-row
TSV and prints `SELFTEST pass|fail cases=33`.

Scratch mirror for every run (`HERE` = the run dir, so `HERE/fixtures/build-fixtures.py` and
`HERE/records/c1-selftest-expected.tsv` are what the counter resolves):

```
<run>/c1-counter.py
<run>/fixtures/build-fixtures.py     (committed bytes, unchanged)
<run>/records/c1-selftest-expected.tsv (committed bytes, unchanged)
```

**Pin handling.** The task allowed bypassing the builder pin by passing the pin of the copied
builder, and allowed dropping the pin args if the expected-TSV pin was an obstacle. Neither was
needed: both files were copied **byte-identical**, so the committed pins `2f26d6aa…` and
`48a7cc0e…` verify inside the selftest on every run. No run emitted a `CANNOT-EVALUATE` status: all
21 selftest logs (10 mutant, 10 restored, 1 baseline), the two full-differential logs and the three
probe logs are clean. The only occurrence of that string in the receipt pack is source context
inside `mutant-diffs.txt`.

**Mutation-run-revert.** For each mutant: hash the run dir → save the mutant bytes to
`mutants/<M>-mutant.py` → run → `cp` the committed bytes back over the run dir → re-hash and
compare to `975d3520…` → re-run the same detector on the restored bytes. Every mutant is one
hunk against the committed file (`diff -u | grep -c '^@@'` = 1 for all ten).

**Baseline (pristine bytes).** `SELFTEST pass cases=33`, rc 0 — so a mutant failure is
attributable to the mutation, not to the harness
(`receipts/logs/baseline-selftest.txt`).

## 3. Mutant table

| # | Target check | Minimal change (one hunk) | mutant sha256 | Detector | Killing fixture → observed |
|---|---|---|---|---|---|
| M1 | pair-filing hidden (F24) | delete the `if any(…)/pairhidden += 1/finding('PAIR-FILING-HIDDEN', …)` block | `c725de89…aa971b7` | **SURVIVED** rc=0, 33/33 pass | none — see §4.1 |
| M2 | pair filter drops hidden filings | `fil = [f for f in fil_all if f[4] not in hidden]` → `fil = list(fil_all)` | `7b4c0d6a…3bbc1074` | **KILLED** | `F24-PAIR-HIDDEN-FILING` rc 1→0, first finding `UNFILED-SOURCES-ANNOTATION` lost |
| M3 | four-space comment opener (S55-S2) | `if indent <= 3 and stripped.startswith('<!--')` → `if '<!--' in ln` (any indent) | `4e0be28f…4bb8f9e8fd` | **KILLED** (2 cases) | `F26-INDENT4-COMMENT-OPENER` rc 1→0; `F29-PROSE-COMMENT-MENTION` rc 0→1 `CORRECTION-IN-FENCE` |
| M4 | over-hide repair (F29) | same line → `if indent <= 3 and '<!--' in ln` (mid-line match) | `494476e7…c1cbe268` | **KILLED** | `F29-PROSE-COMMENT-MENTION` rc 0→1 `CORRECTION-IN-FENCE` |
| M5 | NUL correction file (S55-S1 silent) | delete the `if b'\x00' in corr_b:` / `CORRECTION-FILE-BINARY` block | `85dca3af…f3af3c8c3c9` | **KILLED** | `F28-NUL-CORRECTION-UNCHANGED` rc 1→0, finding lost |
| M6 | binary numstat (S55-S1 changed) | `None if dels == '-'` → `0 if dels == '-'` (binary read as 0 deletions) | `fd434943…054a9fa185` | **KILLED** | `F27-BINARY-NUMSTAT` rc 1→0, `DELETIONS-UNREADABLE-BINARY` lost |
| M7 | LF-only numstat parse | `.split('\n')` → `.splitlines()` in `numstat_deletions` | `83fb26a4…d481316168` | **SURVIVED** rc=0, 33/33 pass | none — see §4.2 |
| M8 | hidden correction (CORRECTION-IN-FENCE) | `if corr_no in hidden:` → `if False:` and drop the `CORRECTION-IN-FENCE` finding | `3d06629c…12f1c55e40` | **KILLED** (7 cases) | `F4-FENCE`, `F7-TILDE-FENCE`, `F8-BT4-PARITY`, `F9-HTML-COMMENT`, `F7-FF`, `F8b-BT4-SHORT-RUN`, `F7-FF2`: expected `CORRECTION-IN-FENCE`, got no finding (rc stays 1 via `unfiled>0`) |
| M9 | zone edge (r54/R1) | `ZONE = 32` → `ZONE = 64` | `63c143f1…005f24f5cf` | **KILLED** | `F10-STRADDLE` first finding `ZONE-TOKEN-STRADDLES-EDGE` → `MULTIPLE-ANNOTATIONS` |
| M10 | recomputed check | delete the `elif m_val != recomputed:` / `BOGUS-RECOMPUTED` block | `2b2cf9fe5ce9007ddacf234833cf67ab3544ddfeb874f87f897489170255b746` | **KILLED** (3 cases) | `F11-BOGUS-RECOMP` rc 1→0; `F20-R1-INDENT-SWALLOW` rc 1→0; `F21-R1-ONELINE-SWALLOW` finding → `CORRECTION-IN-FENCE` |

M9 and M10 are the seat-chosen mutants (zone edge; recomputed check). M1–M8 are the eight
required ones. Full diffs: `receipts/mutant-diffs.txt`; per-run logs:
`receipts/logs/M*-selftest.txt`; machine index: `receipts/mutants-index.tsv`.

## 4. The two survivors — findings, not contract changes

### 4.1 M1 (PAIR-FILING-HIDDEN emission removed) — live mutant, structurally invisible to the detector

Full-output differential of pristine vs M1 over **all 33** fixtures in measure mode
(`receipts/logs/diffall-M1.txt`):

```
FIXTURES-WHOSE-OUTPUT-CHANGED=1 ['F24-PAIR-HIDDEN-FILING']
CHANGED-BUT-INVISIBLE-TO-DETECTOR=1 ['F24-PAIR-HIDDEN-FILING']
```

The only difference on F24 (`receipts/logs/probe-M1-F24-summary.txt`):

```
pristine: FINDING PAIR-FILING-HIDDEN LOG.md:2 matching filing sits in a hidden line (fence or comment); it does not file
          SUMMARY … logunfiled=1 logrecomp=0 alias=0 pairinert=0 pairhidden=1 …
mutant  : (line absent)
          SUMMARY … logunfiled=1 logrecomp=0 alias=0 pairinert=0 pairhidden=0 …
```

rc (1) and first finding (`UNFILED-SOURCES-ANNOTATION`) are identical, so the detector passes.

**Why no fixture can kill it.** `PAIR-FILING-HIDDEN` is emitted inside `if not fil or not match:`
*after* `finding('UNFILED-SOURCES-ANNOTATION', …)` on the same annotation. Therefore it can never
be the first `FINDING` line and can never change the exit code. The detector's whole assertion is
`(rc, first finding)`, and the expected TSV has exactly three columns
(`name`, `expect_exit`, `expect_finding`). A fixture that kills M1 is therefore **impossible under
the frozen row grammar** — the missing piece is a detector column, not a fixture.

Consequence for C1: target **T1** includes "F24 also prints PAIR-FILING-HIDDEN" and the SUMMARY
carries `pairhidden=`, but the committed selftest cannot falsify the removal of either. On pristine
bytes both are present (probe above), so T1 holds; the *kill power* for that clause is zero and
rests on a hand-run measure-mode probe. `run-matrix.sh` does record the whole `SUMMARY` line, so the
post-freeze matrix diff would expose it — but the matrix only ever runs the frozen counter bytes,
so it is a byte-comparison of receipts, not a mutation detector.

Named limit, routed to r57 (no edit of frozen bytes): *the C1 selftest asserts one finding id per
fixture; secondary findings and every SUMMARY counter are unasserted.* Suggested repair shape for
r57: a fourth expected column (`expect_all_findings` or `expect_summary`) so F24 asserts
`pairhidden=1`, which makes M1 killable without a new fixture.

### 4.2 M7 (LF-only numstat parse reverted) — live mutant, but outside the frozen fixture population

Full-output differential pristine vs M7 over all 33 fixtures: **zero** changed fixtures
(`receipts/logs/diffall-M7.txt`: `FIXTURES-WHOSE-OUTPUT-CHANGED=0 []`).

The mutation is nevertheless live, not equivalent. `probe-m7-nel.py` builds a scratch repo with a
file named `a\u0085b.txt` and repo-local `core.quotePath=false`, then calls **both**
`numstat_deletions` implementations on the identical git bytes
(`receipts/logs/probe-M7-nel.txt`):

```
numstat raw: '1\t0\ta\x85b.txt\n'     raw_has_nel: true
records split on LF: 1                records splitlines(): 2
pristine → [['a\u0085b.txt', 0]]       mutant → [['a', 0]]
```

i.e. `splitlines()` tears the record and the mutant reports a truncated path `a`, silently dropping
the real one from the deletion check.

Why no fixture covers it: the only paths passed to `numstat_deletions` are the module constants
`RECORD`, `SITES`, `CORR_FILE`, `PAIR_SITES` — four fixed ASCII names. No repo-level fixture can
introduce a NEL-bearing monitored path, and no committed fixture does. The missing fixture is a
**parser** fixture (a synthetic repo + `quotePath=false` call of `numstat_deletions`), not a repo
fixture — the shape this seat's probe demonstrates is buildable.

This survivor is **already disclosed and de-claimed** by the frozen preregistration: "numstat LF-only
parse: not a reachable lane verdict (the monitored paths are fixed ASCII names); recorded as a
hardening differential … not a claim", and the counter's own named-limits paragraph says the same.
So M7's survival is consistent with the frozen scope; it is a coverage note (the hardening
differential is a receipt, not an assertion), not a claim defect.

## 5. Observation OBS-1 — frozen docstring contradicts frozen behaviour (r57, no edit)

The v5 counter's "Named limits" paragraph states: *"a line whose prose merely mentions `<!--`
still opens a region — the real lane's own SCORECARD.md hides its tail this way, disclosed"*.
That is v4 text left in place: v5 requires the opener to begin the line, so it cannot happen.
Measured with the frozen `hidden_lines()` (`receipts/logs/probe-OBS1-docstring.txt`):

```
a) F29 prose line (mid-line mention)            hidden = []
b) exact SCORECARD.md line 1378 at cce21b55     hidden = []      ← the line the docstring claims hides the tail
c) a line that truly begins with `<!--`         hidden = [1, 2, 3]
```

Behaviour is the repaired one and matches C1 T4 and F29; only the prose is stale. No C1 target is
falsified by this. Routed to r57 as a documentation correction binding (never an edit of frozen
bytes).

## 6. Restoration evidence

`receipts/restore.tsv` — for every mutant, after restoring from the committed bytes: 

```
M1  restored_sha=975d35201075b71affcd106b46341c7300e87e200b04c6c44864d636bcbbf179 matches_pin=OK rc=0 pass=33 fail=0 SELFTEST pass cases=33
… M2 … M10 identical (all ten rows: matches_pin=OK, pass=33, fail=0)
```

So the pristine detector leg (33/33), the mutated leg (per §3) and the restored leg (33/33, pin
verified) all ran on the same bounded detector. Mutant bytes are preserved under
`receipts/mutants/`; the run dirs hold committed bytes again.

## 7. Scope / bounds compliance

- Lane writes: **only** `.ufo/waves/round-56/w1/S56mutation01/**` (this report and `receipts/`).
  No lane file, no `.ufo/state/`, no sibling seat, no fleet-root tracked file was touched.
- Read-only git only, always with `-C <absolute path>`: `show`, `rev-parse`, `status`. No mutating
  git/jj command was run in the lane. The only `git init/add/commit` calls were the committed
  fixture builder's own, inside scratch fixture repos, and `init_repo` asserts
  `git rev-parse --show-toplevel` equals that fixture dir (the NEL probe asserts the same before
  its first commit). The L1's mid-run bounds clarification (fixture init/config/add/commit allowed
  only inside an asserted `/fast/scratch/hyaku/souji-r56/S56mutation01/` root, toplevel verified
  before commit) describes exactly this procedure; no contradiction, no instruction defect.
- Observation (not mine): at the time of writing the lane worktree showed
  `M SCORECARD.md`, `M census/round-56/records/landing-suite-standing.txt` and `HEAD 148f39a6…`
  (ahead of the measured `cce21b55`). All claim evidence here was read from committed bytes at
  `cce21b55`, so the moved tip and those working-tree edits do not affect this seat.
- Counters read committed bytes only; no counter or fixture byte was edited. Scratch removed after
  the receipt pack was written. No tool installed or upgraded (nothing needed; recorded per the
  2026-10-19 authorization rule).
- Disk guard checked before the heavy pass: `/fast/scratch/hyaku` 50% used, 405.5G free.

## 8. Receipt index

| file | content |
|---|---|
| `receipts/pins.txt` | eight pin verifications at `cce21b55` (all MATCH) |
| `receipts/logs/baseline-selftest.txt` | pristine detector: `SELFTEST pass cases=33`, rc 0 |
| `receipts/logs/M1..M10-selftest.txt` | per-mutant detector output, `EXIT=<rc>` stamped |
| `receipts/logs/M1..M10-restored-selftest.txt` | detector on restored bytes, 33/33 pass each |
| `receipts/mutants-index.tsv` | mutant sha256, pre-run sha, diff line count, rc, pass/fail, restored sha |
| `receipts/mutant-diffs.txt` | the ten one-hunk unified diffs against committed bytes |
| `receipts/restore.tsv` | pin check + detector result after every restore |
| `receipts/logs/diffall-M1.txt`, `diffall-M7.txt` | full-output differentials over all 33 fixtures |
| `receipts/logs/probe-M1-F24-summary.txt`, `probe-M1-F24.json` | M1 measure-mode F24 evidence |
| `receipts/logs/probe-M7-nel.txt` | NEL/quoted-path numstat differential for M7 |
| `receipts/logs/probe-OBS1-docstring.txt` | docstring-vs-behaviour measurement |
| `receipts/mutants/*.py` | the ten mutant sources (audit copies) |
| `receipts/sha256sums.txt` | sha256 of every receipt file |

VERDICT: ATTACK-FOUND
VERDICT: SURVIVORS (M1 PAIR-FILING-HIDDEN emission, structurally unkillable under the frozen row
grammar; M7 LF-only numstat parse, disclosed and de-claimed, no fixture can reach it)
