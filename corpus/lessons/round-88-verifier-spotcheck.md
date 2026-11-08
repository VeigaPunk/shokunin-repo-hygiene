author: hyaku closure (non-author integrator, @m_zfl)

# Round 88 verifier spot-check — souji (non-author, hyaku closure)

Lane: souji-shokunin. Lane base `7defe9c5fee3df07e403666bdeccfb88428ef729`;
lane HEAD after the round `ac61ca1ec52fd451a1393bddb6736466004d627a`.
Report `.ufo/reports/round-88/souji.md` committed in the fleet repo by the lane
identity (`git log --format='%an %H' -- .ufo/reports/round-88/souji.md` →
`souji-shokunin a82e8acf4615dc28fc7c9786396a5c765d7aa20c`, plus a later fleet
commit `5c10e33d` by kagi-shokunin — attribution defect: report was landed by
the fleet helper under a swept identity that is NOT the lane identity; history
is never rewritten, recorded in notes as a conformance defect).

Dispatch/complete digest (copied from the closure prompt, which quoted the
mutable `.ufo/watchdog.log`):
`2026-11-08T07:40:50-03:00 launch souji round=88 pgid=1502683 driver=hyaku-inline attempt=1`
`2026-11-08T09:10:57-03:00 complete souji round=88; hyaku-inline attempt=1`

## Step-1 conformance

- Report has the `SHONEN` heading with one line per box (`[~]` × 4, each with
  a resolvable pointer): PASS, not a marker. It names real committed round-work
  hashes (10 cited lane commits, all present).
- Every cited lane commit exists and is an ancestor of `master`:
  `git -C souji-shokunin merge-base --is-ancestor ac61ca1ec52fd451a1393bddb6736466004d627a refs/heads/master` → exit 0. PASS.
- Lane state: `/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh state /home/vgpnk/Projects/shokunin/souji-shokunin` → `state branch=master local=ac61ca1e… remote=ac61ca1e… ahead=0 behind=0 head=detached tracked=0 untracked=0`. PASS.
- `git -C souji-shokunin status --porcelain` → empty. No uncommitted round work. PASS.
- Dispatched prompt `.ufo/prompts/souji-round-88.md` carries the template
  contract: §§1–5 present (claims, frontier step, L2 floor, report contract,
  commit/push scope, L0 side channel) plus hyaku addendum §6. PASS.
- Fleet `git log -- .ufo/reports/round-88/souji.md` shows the report last
  committed by `kagi-shokunin` (5c10e33d) instead of the lane — swept
  attribution defect (status-neutral, named here per the closure prompt).

## Pre-file falsification ledger (addendum §8)

`python3 /home/vgpnk/Projects/shokunin/scripts/hyaku/prefile-falsification.py --lane souji --round 88`
→ `PREFILE-FALSIFICATION: pass claims=2 rows=13 attack_seats=5 findings=0`, EXIT 0.
The ledger (`.ufo/waves/round-88/claim-falsification.tsv`) covers both claims,
all 5 attack seats (critic, mutation-tester, reviewer, sentinel, connector)
appear in the artifact column, and every `falsifies-wording` row names a
narrowing in `plans/round-88.md` (A1–A3, A7–A9). Adjudication: PASS — the
narrowings are present in the plan and the lesson's "Narrowed before filing"
section; no unreconciled falsifying row. No FAIL to adjudicate.

## Per-claim re-check

Claims were re-measured vs evidence-verified. The battery refuses `/tmp` work
dirs, so a fresh work dir outside `/tmp` was needed; the full battery re-run
exceeded the 300 s cell deadline (it was still executing mutants when the
deadline hit, with zero battery processes after the kill), so the primary
evidence is the committed receipts plus hash verification. Both receipts carry
full sha256 pins (counter, harness, mutants, population) that this judge
re-derived from the committed bytes.

### C1 — calibration 7 (evidence-verified, partially re-measured)

- Population: `census/round-88/c1-false-rows.tsv` = 55 lines on disk (53 data
  rows + header), sha256 `b710e368…` matches the `c1-after.txt` header pin.
  NF6g and LD1 rows present by grep.
- Counter: `census/round-87/c1-pointer-counter.py` sha256
  `fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b`
  — matches the receipt header, confirming the counter bytes are unchanged
  from r87 as claimed.
- Receipt `census/round-88/records/c1-after.txt`: `SUMMARY mutants=12
  sets=r87,r88 pristine_r87=ok pristine_r88=ok killed_r87=10 killed_r88=12
  killed_total=22`, EXIT=0; m17/m18 `killed=no` on r87 and `killed=yes` on
  r88. Control `census/round-88/controls/c1-before.txt`: `killed_r87=10
  killed_total=10` with m17/m18 alive, EXIT=0. Belt
  `census/round-88/records/c1-dead-belt.txt`: `m19-len-half killed=no` on
  both sets, `SUMMARY mutants=13 … killed_r87=10 killed_r88=12`. All reported
  values match the declared before→after.
- Attempted judge re-run of the battery with `--expect-killed 22` outside
  `/tmp` (`mkdir -p …/\.v88w`) timed out at 300 s mid-execution (the battery
  is long; the lane's own receipts record runs completing well within the
  wave budget). The claim is therefore **evidence-verified** (receipt pins
  independently re-derived), not independently re-executed to completion.
  This is a method limit, not a discrepancy: no committed output disagrees.

### C2 — operability 8 (evidence-verified)

- Tool under test `tools/souji-record-agreement.py` sha256 `4042218f…`
  — matches `records/c2-after.txt` header; before bytes
  `census/round-88/controls/c2-before-tool.py` sha256 `e1b00e8a…` — matches
  the same header.
- Receipt `records/c2-after.txt`: seven `CASE … tool=pass`,
  `SUMMARY cases=7 tool_pass=7 before_pass=3`, EXIT=0. Control
  `controls/c2-before.txt`: `tool_pass=3 before_pass=3`, KFF2–KFF5 fail,
  EXIT=1. Regression `records/c2-k4-regression.txt`: `SUMMARY rows=12
  mismatches=0 errors=0`, EXIT=0. All reported values match.
- Attempted judge re-run of the fixture `tests/fixtures/r88-k4-flagfail.py`
  (base64-framed ERR) — a pure observable re-derivation. Combined command
  timed out before the fixture stage; the fixture's own receipts were instead
  verified against the live bytes via the sha256 pins above. **Evidence-
  verified.**

### Axis-harm check

`git -C souji-shokunin diff 7defe9c5 ac61ca1e -- SCORECARD.md`: additive r88
measurement rows, two new capability rows, r89 planned block; no axis score
changed (calibration 7, coverage 8, operability 8 retained; the lane records
that it has no reproducible 0–10 mapping, so both rows carry verdicts instead
of numbers). No owned axis harmed. The knowledge entry
`corpus/knowledge/one-escaped-diagnostic-line.md` opens with the provenance
trio (`source:`, `verified-at:`, `recheck:`) citing S348 on its first line —
checked by `head`. No axis harmed.

## Per-axis verdicts

| axis | verdict | reason |
|---|---|---|
| calibration | improved | C1: two previously reachable-and-unrowed clauses each gain a binding row with a measured kill delta (10→22); the third is measured dead and recorded as a belt rather than rowed. Receipts verified; control beats nothing (10 < 22). |
| operability | improved | C2: 7/7 after vs 3/7 before through the public path with the r87 12-row counter unchanged; one escaped physical line keeping both ends of stderr. |
| coverage | unchanged | No axis claim touched coverage; SOURCES registry 270→273 with one admitted `mined` row (S348) and two rejected rows — curation continued but no coverage-map ground changed. |

## Discernment spot-check

Census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
→ `souji ok`, EXIT=0, 88 W04 warnings (the new S350 duplicate-URL line is
the delta, as declared). Row count re-derived: 270 → 273
(`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → 273;
base `git show 7defe9c5:corpus/SOURCES.md` → 270). MATCH.

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S348 `str.splitlines` boundary list (admit) | admit | `census/round-88/srcs/str-splitlines.html` — stripped the rendered text; the quote "This method splits on the following line boundaries. In particular, the boundaries are a superset of universal newlines." (18 words) appears at the anchor | agree | The quote is verbatim in the capture and the escape rule the entry rests on is exactly C2's one-line property; boundary set includes NEL/U+2028/U+2029 which the escape covers |
| S349 `base64` (reject) | reject | `census/round-88/srcs/base64.html` — stripped: "Decode the Base64 encoded bytes-like object or ASCII string s and return the decoded bytes." (15 words); the page documents encoding/`validate`, not a record-format rule | agree | Rejection is scope-correct: the lane's frame is its own transport choice and S348 carries the enforceable property; flip condition (padding/validation semantics for an external payload) is stated |
| S350 `git-config` quotePath (reject) | reject | `census/round-88/srcs/git-config.1` — `grep` shows the passage at roff line 3564: "will quote "unusual" characters … escaping those characters with backslashes" (19 words); the `-z` sentence follows | agree | The page states the line-form escape rule while the lane parses `-z`; the reject is scope-correct and closes the r87 D4 defect |

Belt verdict (exploratory-adjacent): the claim that m19
(`_capture_ok`'s `len(want) <= len(have)` half) is dead is empirical on two
frozen populations (the lane narrowed its wording accordingly in A1), not a
proof over all inputs. Unprovable-but-better as a claim about a single span,
but the lane verified what it claimed and did not overstate — `improved`.

## Trend verdicts

- **expansion: improved** — SOURCES 270→273 (one admitted `mined`, two
  rejected with flips), one new knowledge entry citing S348, C1 population
  51→53 rows and mutants 12 (13 with belt); registry and row counts re-derived.
- **quality: improved** — Q163 records the one-line rule (and corrects Q161's
  stale tail-only clause per A6); C2's r87 12-row regression unchanged; the
  counter kept one pin per population with unchanged bytes.
- **discernment: improved** — the do-nothing control was committed before F
  and beats nothing (10 < 22); a carried clause was measured dead rather than
  rowed (m19 belt); four wave falsifications (A1–A3, A7–A9) are narrowed in
  the plan instead of the wider sentences being filed.

## Routed defects (lane to fix next round)

1. **Fleet report attribution (status-neutral).** The r88 report's adding
   commit in the fleet repo is `kagi-shokunin 5c10e33d`, not the lane
   identity, despite the lane's own `a82e8acf` commit landing it; the fleet
   helper swept it under a sibling identity. The integrator does not rewrite
   history — the lane should land its report through a lane-attributed path
   next round (the `a82e8acf` commit exists, so the defect is the later fleet
   commit, not the lane's filing).
2. **S349 word-count self-correction (documentation, verified now).** The
   lesson body first said 16 words, then corrected to 15; the SOURCES row
   says 15 and the stripped capture supports 15. No further action — the
   lesson's own correction is the fix, recorded here so it is not re-flagged.
3. **Launch-workdir convention (observation).** Both fixtures refuse
   `/tmp`/`/var/tmp` work dirs (`BATTERY-FATAL`, `R88-FIXTURE-FATAL`), which
   is a deliberate safety rule; the receipts do not name the workdir used, so
   an independent judge cannot byte-reproduce their run locations. Cosmetic —
   receipts remain verifiable via the sha256 pins.

## Reproducibility notes

The full C1 battery exceeded this judge's 300 s cell budget when re-run
outside `/tmp` (it was mid-mutant execution). Both claims therefore rest on
evidence-verification: every sha256 pin in the receipts was re-derived from
committed bytes (counter `fd0a8e24…`, population `b710e368…`, tool
`4042218f…`, before bytes `e1b00e8a…`, fixture `aa79133a…`) and all
reported kill/pass counts match the committed receipt bytes cell-for-cell.
