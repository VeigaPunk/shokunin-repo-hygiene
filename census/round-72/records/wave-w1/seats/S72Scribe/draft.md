# Draft material for `corpus/lessons/round-72.md` — seat S72Scribe

Written 2026-11-06 by S72Scribe. Material only: the L1 owns the lesson, the report and the integration
commit. Every path below is relative to `/home/vgpnk/Projects/shokunin/souji-shokunin`; every number was
re-derived from committed bytes at the after-arms commit `2ec8b63dfda8fdf88cd240487c5d1325de13b501`
unless the row says "re-executed". Round commits: freeze `23372f36`, candidate `06df4f97`, after-arms
`2ec8b63`; lane base `0bf098dd`; reference-weak base `8b9345b1`.

## 1. Routed-item closure

### 1a. r71 spot-check D1–D5 (`corpus/lessons/round-71-verifier-spotcheck.md`, "Routed defects")

| item | r72 status | evidence (committed) |
|---|---|---|
| D1 report wording (LOW): controls committed "before any candidate bytes existed" must be stated per claim | **partly**: the freeze freezes the candidate's non-existence; the report does not exist yet | `census/round-72/preregistration.txt:22-23` ("the r72 counter and matrix do NOT exist at this commit; it is committed after it"); `.ufo/reports/round-72/` absent at `2ec8b63`; the four controls drive the frozen r71 harness (`6c7bf41d…`), the frozen r71 counter (`7e5a694a…`), its committed Y6 variant (`2e38ca9d…`) and the committed battery members — none reads an r72 counter/matrix byte (`controls/*.txt:1-3`), so the sentence is true for them |
| D2 calibration, carried: `claim_upheld` ignores the base slot (Y6/Y10 7→2 with EXIT=0) | **CLOSED** | `census/round-72/c1-counter.py:1238-1239` (per-row base compare), `:1291-1299` (`claim_upheld` requires `base_mismatches==0`), `:1301-1305` (SUMMARY prints it); `census/round-72/records/c1-Y6-main-arm.txt:164-165` (`base_mismatches=10`, `EXIT=1`); **re-executed**: the committed variant `records/variants/r72-Y6-counter.py` reproduces that SUMMARY byte-for-byte and `EXIT=1`; the honest main arm reproduces `c2-honest-writer.txt:164-165` (`base_mismatches=0`, `EXIT=0`) |
| D3 operability, measurement gap: over-refusal; AS1/AS2 scrub-vs-unfiltered; the three repaired filter-class routes and the stat routes should become rows | **PARTIAL**: two of three repaired filter routes now have rows (post-run `FWi`/WM4, in-run `FWr`/WM3 on the pre-side, driver named `set` `FWs`/WM6), plus process `FWp`/WM5 and worktree-attribute `FWw`/WM8; the **ident/working-tree-encoding route** and the **checkStat/trustctime pins** still have no row and no battery member; over-refusal is still row-less | rows `census/round-72/c1-matrix.tsv:72-76`; `census/round-72/records/c2-after-battery.txt:159,312,465,618,771` (each member forges exactly its FW row — re-derived by parsing the receipt blocks: WM3→FWr, WM4→FWi, WM5→FWp, WM6→FWs, WM8→FWw), `:772` BATTERY; **but** `grep -in 'ident\|encoding\|checkStat\|trustctime' census/round-72/c1-matrix.tsv census/round-71/c1-matrix.tsv` → 0 rows; `census/round-72/battery-manifest.tsv` = WM3,WM4,WM5,WM6,WM8 only; `tools/souji-receipt-write.py:143-147` (stat pins), `:155,1771` (`RECEIPT-CHECKIN-CONVERSION-SET`); limits at `preregistration.txt:115-121` name only WM7, over-refusal, smudge-only |
| D4 calibration: the neighbouring `clean_env` (ambient `GIT_DIR`) defect passes the r71 selftest | **CLOSED** | `census/round-72/records/c1-after.txt:19` (`MUTANT Z1 … fate=killed`); `census/round-72/c1-counter.py:1792` (`clean_env: every scrub-tuple name is removed`); `records/counter-selftest.txt:48,49` (`kept=[]`, `cases=44 pass=44`) |
| D5 cross-lane: 13 sibling clean-tree gates (kaidoku, kama, mori, tameshi, audio) need routing | **OPEN** | `grep -ril 'kaidoku\|kama\|mori\|tameshi\|audio' census/round-72` → 0 files; out of this lane's write scope |

### 1b. `corpus/lessons/round-71.md:85` "Routed to round 72"

The seat brief says "(a)–(e)"; the committed paragraph carries **(a)–(h)**. All eight are listed.

| item | r72 status | evidence |
|---|---|---|
| (a) HIGH F1/S71Scribe: base slot ignored | **CLOSED** | same as D2: `c1-counter.py:1238-1239,1291-1299`; `records/c1-Y6-main-arm.txt:164-165`; re-executed variant `base_mismatches=10`, `EXIT=1` |
| (b) HIGH F2: AS1/AS2 cannot tell a `GIT_ATTR_SOURCE` scrub from an unfiltered dirty tree (Y4 survives) | **CLOSED as a survivor** (the fixture-level ambiguity is unchanged and is still stated in the r71 knowledge table) | `c1-after.txt:15` (`Y4 … fate=killed`); `counter-selftest.txt:44` (`base witness … rows=7 mismatches=[]`), built at `c1-counter.py:1746`; Y4 without `GIT_ATTR_SOURCE` makes the base refuse where `base_expect=accept` |
| (c) MEDIUM F3/F4: no selftest pins `FORGED_SAMESIZE`/`FILTER_CLEAN`/`chmod_notes`; Y1/Y9 survive | **CLOSED** | `c1-after.txt:14,17` (`Y1`, `Y9` killed); `counter-selftest.txt:46-47`; `c1-counter.py:1759` (`sub/M1`), `:1769` (dot-file line); Y6/Y10 killed via the 9a base witness (`c1-after.txt:16,18`) |
| (d) HIGH W8 + W3/W4/W5/W6/W7 survive the matrix | **W3/W4/W5/W6/W8 CLOSED; W7 OPEN** (named limit); WM7 reachability was not probed in r72 | `c2-after-battery.txt:159,312,465,618,771` (5/5 forgery, one row each), `:772-773`; WM7 named at `preregistration.txt:36` ("no reachable failure was found in r71"); no WM7 file/member exists in `census/round-72` and no r72 artifact probes reachability; note the matrix row `W7` (`c1-matrix.tsv:48`, `git-dir-redirect-hides-mode`) is **not** the mutant WM7 |
| (e) MEDIUM over-refusal of an honest repo with a configured driver on a tracked path (needs a row + operator view) | **OPEN** | no row in `c1-matrix.tsv`; `preregistration.txt:119-121` names it unmeasured; no operator view in the round |
| (f) LOW harness: no TMPDIR check, uncaught timeout, symlinked label dir; dead `CLASS_*`; receipts' `rev=` has three referents | **OPEN** (harness frozen, unchanged) and the `rev=` ambiguity is repeated: three committed receipts bind three different objects | harness sha `6c7bf41d…` at `c1-after.txt:3`; `c1-after.txt:1 rev=8b9345b1` (base writer), `c1-Y6-main-arm.txt:1 rev=0bf098dd` (candidate writer), `counter-selftest.txt:1 rev=06df4f97` (counter commit, a commit the command line never names) |
| (g) open from r70: NOGLOB row, battery regeneration, case 38 independence, r69 D5 items | **not addressed** (no r72 artifact; audit limited to the strings above) | — |
| (h) cross-lane, documented only: 13 sibling gates | **OPEN** (same as D5) | — |

## 2. Two candidate `## Mistakes` rows

Lane format: `# | class | evidence pointer | captured-by | fix`. Both are absent from
`corpus/lessons/round-71.md` M1–M4 and from the r68/r69/r70 tables.

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | **receipt provenance is not bound to the executed bytes**: `instrument=` and `command=` are the compiled-in constant `COUNTER_REL`, and `rev=` names a different object in each receipt, so a committed receipt's own command is not a replay of it (and a variant run's receipt names the unmutated counter) | `census/round-72/records/c1-Y6-main-arm.txt:1-4` (`rev=0bf098dd…`, `instrument=census/round-72/c1-counter.py`, `instrument_sha256=45f3afdb…`, `command=… census/round-72/c1-counter.py …`); `sha256sum census/round-72/c1-counter.py` = `7578447d…`, while `45f3afdb…` is `records/variants/r72-Y6-counter.py`; `census/round-72/c1-counter.py:191` (`COUNTER_REL`), `:1477-1484` (`write_receipt`), `:1481`, `:1935,1976` (command rebuilt with `COUNTER_REL`); `census/round-72/records/counter-selftest.txt:1-4` (`rev=06df4f97…` not in the command; `--work <scratch>` is not a path; the counter's `--selftest` returns at `c1-counter.py:1852` before any `write_receipt`); three `rev=` referents: `c1-after.txt:1`=8b9345b1, `c1-Y6-main-arm.txt:1`=0bf098dd, `counter-selftest.txt:1`=06df4f97 | S72Scribe (this seat), by replay; the envelope class was already noted at `census/round-71/records/wave-w1/seats/S71ExecC2.md:18` (LOW) and was not routed into the r72 mutant set | emit `instrument=<realpath(__file__), lane-relative>`, a distinct `measured=base-rev\|candidate-rev\|counter-commit` field, and the real argv (including `--work`); add a replay case that runs the recorded command and compares SUMMARY. **Shown able to fail now**: replaying the recorded Y6 command without `--receipt` prints `SUMMARY matrix=75 … base_mismatches=0 … EXIT=0` (not the receipt's `base_mismatches=10`, `EXIT=1`), while `records/variants/r72-Y6-counter.py` reproduces the receipt byte-for-byte; replaying the recorded selftest command verbatim exits `2` (`C1-COUNTER-FATAL: work directory does not exist: …/<scratch>`) |
| M2 | **closure declared wider than the measured set**: the round's limits list three unmeasured protections but not the routed ident/working-tree-encoding conversion or the `core.checkStat`/`core.trustctime` pins — and neither has a matrix row or battery member, so C2's 5/5 cannot see a revert of those repairs | `grep -in 'ident\|encoding\|checkStat\|trustctime' census/round-72/c1-matrix.tsv census/round-71/c1-matrix.tsv` → 0 rows in both; `census/round-72/battery-manifest.tsv` (5 members, none for the conversion/stat checks); `tools/souji-receipt-write.py:143-147` (stat pins), `:155,1771` (`CONVERSION_CLASS`); `census/round-72/preregistration.txt:115-121` (limits); `census/round-71/records/wave-w1/seats/S71CriticClaims/ident-transcript.txt:1-4` (the ident route forges the pre-repair writer: `CANDIDATE rc=0`); `census/round-71/records/repair-canfail.txt:13-18` (R3a/R3b/R4) | none in r72 (the prereg lists D3 as an input, but the limits sentence does not name these routes); r71 spot-check D3 and r71 M4 name them | add FW-style rows for ident/working-tree-encoding and for the stat pins (the r71 fixtures and the R3a/R3b/R4 reverts exist), or name both in the limits sentence. **Shown able to fail only at writer-selftest granularity today**: `repair-canfail.txt:12,15,18` — R3a, R3b and R4 each print `SELFTEST cases=42 pass=41 fail=1` (R4's failing case: `checkin-conversions: ident and working-tree-encoding …`), so the fixtures are refutable; the missing piece is the row that lets the counter see them. Note also `repair-canfail.txt:5,8,11,14`: R1/R2/R3a/R3b all fail the *same* single case 41, so the writer selftest cannot localize which of the four repairs broke |

## 3. Pointer check (frozen command, seat task item 4)

```
python3 -B tools/souji-pointer-check.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev 2ec8b63dfda8fdf88cd240487c5d1325de13b501 \
  census/round-72/preregistration.txt corpus/knowledge/filter-filemode-witness.md corpus/README.md
```
Observed (EXIT=1):
```
MISSING corpus/README.md:81 census/operator-sweep-20261019
MISSING corpus/README.md:764 .ufo/waves/round-32/a2w1/SwarmCritic20.md
MISSING corpus/README.md:770 .ufo/waves/round-32/a2w1/SwarmReviewer27.md
MISSING corpus/README.md:985 .ufo/waves/round-62/w1/S62ConnectorOverlap
SUMMARY files=3 checked=134 missing=4 skipped=9 dead_declared=0
EXIT=1
```
Baseline: the same four are already missing at the lane base (`--rev 0bf098dd`, `corpus/README.md`
alone: `SUMMARY files=1 checked=88 missing=4 skipped=3 dead_declared=0`, `EXIT=1`), so r72 did not
introduce them; r72's README hunk is `:1011-1015` and touches none of the four lines. The gate is
registered with pass condition `missing=0` at `SKILL.md:930`, and `census/round-72/records/` carries no
pointer receipt.

## 4. Re-derivation ledger (what I re-derived, and what I did not re-execute)

Verified from committed bytes (all at `2ec8b63` unless stated):
- Input pins: counter `7578447d…`, matrix `cd8490b4…`, mutants `cfc40608…`, harness `6c7bf41d…`,
  battery manifest `99c9a55f…`, `battery/SHA256SUMS` `cfd51315…`, five member shas
  `27daa4b3/b88c8471/b21ccdd2/a9c1fa16/798f9344`, base writer `118597e0…`, lane-base writer
  `b7790001…` (no `tools/` byte changed `0bf098dd..2ec8b63`), srcs html `6fe0df4e…`/`0a1e8015…`.
- `mk-counter.py` re-run in a scratch mirror reproduces `c1-counter.py` and `c1-matrix.tsv`
  byte-for-byte (both `cmp` clean).
- Matrix: 75 rows; `expect` 19 accept / 56 refuse; `base_expect` 31 accept / 44 refuse; the 12
  base-forgery rows and the 19 base-honest rows are exactly the count pair the receipts print; all 70
  carried rows' `base_expect` equal the r71 receipt's `CASE … base=` field (70/70); FW rows at `:72-76`.
- Mutants: 11 (`X6-X10,Y1,Y4,Y6,Y9,Y10,Z1`), each anchor occurs exactly once in both counters; the six
  r71-seat mutants reproduce their committed seat files 6/6 byte-for-byte; the Y6 edit of the r72
  counter is byte-identical to `records/variants/r72-Y6-counter.py`, and of the r71 counter to
  `controls/variants/r71-Y6-counter.py`.
- Battery: `make-battery.py`'s five edits replayed from `0bf098dd:tools/souji-receipt-write.py` are
  byte-identical to the five committed members; `SHA256SUMS` and the manifest reproduce exactly.
- Probe: 35 PROBE lines, 10 accept, `EXIT=0`; base accepts all five shapes, the lane-base writer
  refuses all five, and each member accepts exactly one (WM3→FWr, WM4→FWi, WM5→FWp, WM8→FWw, WM6→FWs).
- Receipts vs frozen predicates: `c1-after.txt:24-25`, `c1-Y6-main-arm.txt:164-165`,
  `c2-after-battery.txt:772-773`, `c2-honest-writer.txt:164-165`, `counter-selftest.txt:49-50`,
  controls `:24-25`, `:154-155`, `:722-723` all read as the prereg states; the battery blocks confirm
  each member's forged row.

Re-executed (not read): the honest main arm (`EXIT=0`, `base_mismatches=0`) and the committed Y6
variant (`EXIT=1`, `base_mismatches=10`), 57 s total; the selftest-command replay (`EXIT=2`). **Not
re-executed by this seat**: the 9-minute C1 harness run and the 4-minute battery run; their receipts
bind the committed input hashes above and the executor seats own those re-runs. Nothing in this draft
upgrades an unexecuted number to an observed one.

## 5. Findings

- **MEDIUM — D3 is only half closed and the gap is undeclared.** The ident/working-tree-encoding route
  and the `core.checkStat`/`core.trustctime` pins have no matrix row and no battery member in r72 (grep
  above), while `preregistration.txt:115-121` names only WM7, over-refusal and smudge-only as
  unmeasured. A reader of the r72 limits would take the r71 conversion/stat repairs as matrix-covered;
  they are not (only the writer selftest, `repair-canfail.txt`, refutes their reverts).
- **LOW/MEDIUM — receipt provenance.** Cf. Mistake M1: the Y6 receipt's own command would print
  `EXIT=0`; the selftest receipt's command is not replayable (`EXIT=2`) and the counter cannot emit
  that envelope; `rev=` has three referents across three receipts (`round-71.md:85 (f)` carried it).
- **LOW — pointer gate red at the round's own revision** with four pre-existing dead pointers
  (`corpus/README.md:81,764,770,985`; `EXIT=1`), and no r72 pointer receipt. Pre-existing, but the
  round extends `corpus/README.md` and `corpus/knowledge/filter-filemode-witness.md`.
- **LOW — the seat brief quotes the round-71 lesson as "(a)–(e)"**; the committed paragraph carries
  (a)–(h) (`round-71.md:85`). Falsified premise of the assignment, not of the round.
- **LOW — id collision between a matrix row and a battery mutant**: `census/round-72/c1-matrix.tsv:48`
  is the row `W7` (`git-dir-redirect-hides-mode`), while `preregistration.txt:36` "WM7" is the
  *writer* mutant (check-attr failure fail-open) that the battery omits. No r72 artifact probes WM7's
  reachability, so milestone item "WM7 reachability" has no r72 evidence beyond the r71 conclusion.
- Confirmed, no finding: C1 (i) receipt and C2 (i) receipt match their frozen predicates byte-for-byte,
  their instrument/matrix/mutant/member hashes bind the committed bytes, and the frozen inputs are
  unchanged from the freeze to the after-arms commit (`git diff --stat 23372f36 2ec8b63` over
  mutants/battery/probe/controls/prereg is empty).
