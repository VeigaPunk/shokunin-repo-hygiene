# W1ExecReportGate — round-39 report gate, before the report exists

Seat: executor, round 39 wave 1 (item W1ExecReportGate). Role: put the round-39 report
under the lane's own report-contract gate *before* it exists, measure the gate on the filed r38
report and on an empty file, and hand the L1 the exact checklist the r39 report must satisfy.
Advisory only: no lane bytes written outside this file.

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` (HEAD observed `c0b007b42af9a03d7edc32533bcac27484223997`
at start, `50972f0d15af0b41bd948f9ddda0440c3d42de16` local at 15:0x — the L1 was landing while I
measured; see Risks).
Scratch: `/fast/scratch/hyaku/souji-r39/W1ExecReportGate` (left on disk, see end).

## Verdict summary

| check | verdict |
|---|---|
| gate selftest, 9 cases | **PASS** — `cases=9 pass=9 fail=0`, rc 0 |
| filed r38 report `/home/vgpnk/Projects/shokunin/.ufo/reports/round-38/souji.md` vs lane `SHONEN.md` | **PASS 7/7**, rc 0 |
| empty file vs lane `SHONEN.md` | **FAIL 7/7**, rc 1 (every predicate fires; no vacuous pass) |
| full pre-report gate, r38 report, `--contract` | `check-report-contract=PASS`; gate rc 1 only from `check-clean` (in-flight sibling bytes) |
| full pre-report gate, empty file, `--contract` | `check-report=FAIL`, `check-shonen=FAIL`, `check-report-contract=FAIL`, rc 1 |
| 30 discriminating probes (below; one early no-op disclosed) | 21 rejected with the right predicate, 9 accepted — 7 intended forms and **2 false acceptances** (blind spots 1-2) |

The r39 report is not written yet and no r39 report bytes exist in the lane; everything below is
the gate's behaviour measured on real and mutated inputs.

## What I read

- `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-report-contract.py` (all 419 lines,
  including `mask`, `split_sections`, the seven predicates, `--selftest`, `main`).
- `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-pre-report-gate.sh:1-110` (checks 1-6;
  `--contract` is opt-in, check 3 is a literal `grep -c '^## SHONEN'`).
- `/home/vgpnk/Projects/shokunin/souji-shokunin/SHONEN.md` (4 boxes).
- `census/round-39/preregistration.txt:90-123` (write scope names `.ufo/reports/round-39/souji.md`).

## Commands run and observed output

### 1. Gate selftest

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
python3 -B tools/souji-report-contract.py --selftest
```
```
case-conforming=PASS observed=[] expected=[]
case-empty-code-span=PASS observed=[] expected=[]
case-missing-section=PASS observed=['sections'] expected=['sections']
case-section-order=PASS observed=['sections'] expected=['sections']
case-shonen-no-box-line=PASS observed=['shonen-boxes'] expected=['shonen-boxes']
case-trend-missing=PASS observed=['trends'] expected=['trends']
case-stale-lane-absent=PASS observed=['sections', 'stale-lane'] expected=['sections', 'stale-lane']
case-no-measured-commit=PASS observed=['measurements'] expected=['measurements']
case-no-evidence-pointer=PASS observed=['measurements', 'evidence'] expected=['measurements', 'evidence']
SUMMARY cases=9 pass=9 fail=0
exit=0
```
Verdict: **PASS** — the checker discriminates its own crafted cases; the r36 receipt claim
`cases=9 pass=9` still holds at this HEAD.

### 2. Filed r38 report (20 890 bytes) against the lane SHONEN.md

```
python3 -B tools/souji-report-contract.py \
  --report /home/vgpnk/Projects/shokunin/.ufo/reports/round-38/souji.md \
  --shonen /home/vgpnk/Projects/shokunin/souji-shokunin/SHONEN.md
```
```
check-sections=PASS
check-shonen-boxes=PASS
check-trends=PASS
check-stale-lane=PASS
check-measurements=PASS
check-claims=PASS
check-evidence=PASS
SUMMARY checks=7 pass=7 fail=0
exit=0
```
Verdict: **PASS 7/7**. The r38 report is a clean model for r39: `## SHONEN` at line 186 with four
box lines (188, 191, 193, 196), `## Before → after measurements` at 98 with three table rows each
carrying a standalone backticked commit and a counting command, `## Stale-lane` at 213 with the
`Stale-lane: no — …` line at 215.

### 3. Empty file against the same SHONEN.md

```
: > /fast/scratch/hyaku/souji-r39/W1ExecReportGate/empty.md
python3 -B tools/souji-report-contract.py \
  --report /fast/scratch/hyaku/souji-r39/W1ExecReportGate/empty.md \
  --shonen /home/vgpnk/Projects/shokunin/souji-shokunin/SHONEN.md
```
```
check-sections=FAIL
detail-sections: work performed headings=0 expected 1
check-shonen-boxes=FAIL
detail-shonen-boxes: ## SHONEN sections=0 expected 1
check-trends=FAIL
detail-trends: no trend verdicts section body
check-stale-lane=FAIL
detail-stale-lane: no stale-lane line
check-measurements=FAIL
detail-measurements: no row with a measured commit and a counting command
check-claims=FAIL
detail-claims: claim ids=0 expected 1-3
check-evidence=FAIL
detail-evidence: no evidence pointer
SUMMARY checks=7 pass=0 fail=7
exit=1
```
Verdict: **FAIL 7/7, correctly** — a report that does not exist yet cannot pass; each predicate
names its own reason, so the r39 report can be grown predicate by predicate.

Related: `grep -c '^## SHONEN' empty.md` prints `0` and exits **1** (grep's no-match status), which
the gate maps to `check-shonen=FAIL`.

### 4. Full pre-report gate (`--contract`), both inputs

```
bash tools/souji-pre-report-gate.sh \
  --lane /home/vgpnk/Projects/shokunin/souji-shokunin --branch master \
  --report /home/vgpnk/Projects/shokunin/.ufo/reports/round-38/souji.md \
  --prereg /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/preregistration.txt \
  --contract --shonen /home/vgpnk/Projects/shokunin/souji-shokunin/SHONEN.md
```
```
check-tip=PASS
check-report=PASS
check-shonen=PASS
check-clean=FAIL
detail-clean:  M corpus/lessons/round-39.md
?? census/round-39/records/c2-after.txt
?? census/round-39/records/c3-after.txt
?? census/round-39/records/census-after.txt
?? census/round-39/records/census-before.txt
check-prereg=PASS
contract-check-sections=PASS
contract-check-shonen-boxes=PASS
contract-check-trends=PASS
contract-check-stale-lane=PASS
contract-check-measurements=PASS
contract-check-claims=PASS
contract-check-evidence=PASS
contract-SUMMARY checks=7 pass=7 fail=0
check-report-contract=PASS
gate_exit=1
```
Same command with `--report …/empty.md`:
```
check-report=FAIL
check-shonen=FAIL
detail-shonen: found 0 headings, expected 1
check-clean=FAIL
…
check-report-contract=FAIL
detail-report-contract: checker missing (/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-report-contract.py) or report empty
gate_exit=1
```
Verdicts: contract predicate **PASS** on r38, **FAIL** on empty. Gate rc 1 on both runs comes from
`check-clean`, which fails only because wave-1 seats have bytes in flight at measure time — that is
a filing-time precondition, not a report defect. Note the conflated detail message: the checker
*does* exist; the empty report alone triggers the `missing … or report empty` wording (operability
nit, not my edit scope).

### 5. Discriminating probe battery (mutations of the r38 report, written only to scratch)

Driver: python in `/fast/scratch/hyaku/souji-r39/W1ExecReportGate`, each case written to
`probe-<name>.md` and run as `python3 -B tools/souji-report-contract.py --report <probe> --shonen <lane>/SHONEN.md`.

| probe (mutation of the r38 bytes) | rc | failing predicate and detail |
|---|---|---|
| `base-control` (unmutated) | 0 | — `checks=7 pass=7` |
| `dup-shonen-heading` (second `## SHONEN`) | 1 | shonen-boxes: `## SHONEN sections=2 expected 1`; `grep -c` → 2 |
| `shonen-3-boxes` (one box line deleted) | 1 | shonen-boxes: `box lines=3 expected 4` |
| `shonen-5-boxes` (one added) | 1 | shonen-boxes: `box lines=5 expected 4` |
| `indented-shonen-heading` (` ## SHONEN`) | **0** | tool PASS, but `grep -c '^## SHONEN'` → **0** → gate `check-shonen=FAIL` |
| `shonen-only-in-fence` (heading inside a fence) | 1 | shonen-boxes: `## SHONEN sections=0 expected 1`; `grep -c` → 1 |
| `shonen-prefix-extra-word` (`## SHONEN checklist`) | 0 | accepted by both tool and grep |
| `box-line-inside-fence` | 1 | shonen-boxes: `box lines=3 expected 4` (masked out) |
| `plus-bullet-box` (`+ [~] …`) | 1 | shonen-boxes: `box lines=3 expected 4` |
| `star-bullet-box` (`* [~] …`) | 0 | accepted |
| `box-with-x-cap` (`- [X] …`) | 0 | accepted |
| `heading-suffix-work-performed` (`## Work performed (C1–C3)`) | 1 | sections: `work performed headings=0 expected 1` |
| `heading-before-slash-after` (`## Before/after measurements`) | 1 | sections: `before -> after measurements headings=0 expected 1` |
| `arrow-single-hyphen` (`## Before - after measurements`) | 1 | sections: same detail |
| `arrow-dashes` (`## Before --> after measurements`) | 0 | accepted (normalizer collapses `-->`) |
| `sources-and-frontier` (`## Sources and frontier`) | 1 | sections: `sources & frontier headings=0 expected 1` |
| `stale-lane-space-heading` (`## Stale lane`) | 0 | accepted (heading alias) |
| `stale-lane-empty` (heading, empty body, no line) | 1 | stale-lane: `no stale-lane line` |
| `stale-lane-line-no-heading` (line kept, heading removed) | 1 | sections + stale-lane both FAIL |
| `stale-line-only-kept` (heading removed, `Stale-lane:` line kept) | 1 | sections: `stale-lane headings=0 expected 1`; `check-stale-lane=PASS` — the line form satisfies only that predicate |
| `trend-hyphen-sep` (`- expansion - unchanged`) | 1 | trends: `missing verdicts: expansion` |
| `trend-negated` (`- quality: not improved`) | 1 | trends: `quality line opens with 'not', not a verdict token` |
| `duplicate-trend-line` | 1 | trends: `duplicate expansion verdict` |
| `claims-C4` (one `C4` sentence in Work performed) | 1 | claims: `claim ids=4 expected 1-3` |
| `work-performed-empty` | 1 | claims: `claim ids=0 expected 1-3` |
| `shonen-splits-measurements` (`## SHONEN` before the table) | 1 | measurements: `no row with a measured commit and a counting command` |
| `measured-commit-unbackticked` (one commit de-backticked) | 0 | still passes — a second standalone hex span remained in the row |
| `only-40hex-register-rev` (pure-hex spans removed from the row) | 1 | measurements: `no row …` (a hex inside the command span does not count) |
| `noncommit-64hex-as-commit` (`measured at \`3f1c0a77…d4e\``) | **0** | **PASS with a fabricated digest**: `git cat-file -t` → `fatal: Not a valid object name` |

Disclosure: one early probe named `shonen-before-measurements-table` was a no-op mutation (it left
the original `## SHONEN` in place) and passed rc 0; the corrected probe `shonen-splits-measurements`
is the real measurement and is the one tabulated.

## Blind spots found (advisory, for the L1 to route)

1. **`measurements` cannot tell a commit from a digest.** `COMMIT = ^[0-9a-f]{7,64}$` and
   `check_measurements` only requires one *pure* backticked 7-64 hex span plus any second span in a
   table row of the measurements section. `noncommit-64hex-as-commit` passes with
   `3f1c0a77…d4e`, which `git cat-file` rejects. The predicate is *shape*, not `commit`-ness.
   Consequence for r39: a green `check-measurements` is not evidence that a commit was measured;
   the receipt/commit pairing still has to be read by a human seat (this is also exactly the r37
   routed defect-2 class the round is closing in C1).
2. **`grep -c '^## SHONEN'` and the tool disagree at the edges.** An indented ` ## SHONEN` (the
   contract tool allows 0-3 leading spaces) passes the tool but greps 0 → gate `check-shonen=FAIL`;
   a heading quoted inside a fence greps 1 but the tool sees 0 sections. Only the exact literal
   `## SHONEN` at column 0, exactly once, anywhere in the file, satisfies both.
3. **Section bodies end at the next `##`.** Any `##` heading inserted inside a section (e.g. a
   `## SHONEN` placed above the measurement table) truncates that section's body, so the predicate
   for the *enclosing* section fails even though its content is present. Keep `## SHONEN` after
   all six canonical sections.
4. **Claims regex counts any `C1`-`C9`.** `\bC([1-9])\b` over the Work-performed body: naming
   `C4`…`C9` there fails `claims` with `claim ids=4 expected 1-3`. r39's C1/C2/C3 fit exactly;
   do not mention a C4+ phrase in that section.

## The exact checklist the round-39 report must satisfy

Target path (prereg write scope): `/home/vgpnk/Projects/shokunin/.ufo/reports/round-39/souji.md`.
Pre-filing check (the gate the L1 must run before filing):

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
bash tools/souji-pre-report-gate.sh \
  --lane /home/vgpnk/Projects/shokunin/souji-shokunin --branch <filed-branch> \
  --report /home/vgpnk/Projects/shokunin/.ufo/reports/round-39/souji.md \
  --prereg /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/preregistration.txt \
  --contract --shonen /home/vgpnk/Projects/shokunin/souji-shokunin/SHONEN.md
```
Required result: `check-tip=PASS check-report=PASS check-shonen=PASS check-clean=PASS
check-prereg=PASS check-report-contract=PASS`, exit 0; and directly
`python3 -B tools/souji-report-contract.py --report … --shonen …/SHONEN.md` → `SUMMARY checks=7
pass=7 fail=0`, exit 0.

**A. Headings — exactly these strings, at column 0, each exactly once, in this order** (a
duplicate fails `sections`; any extra suffix such as `(C1–C3)` fails it; the arrow form is the only
accepted one for measurements except `-->`):

1. `## Work performed`
2. `## Landed changes`
3. `## Before → after measurements`
4. `## Sources & frontier`   (literal `&`, not `and`)
5. `## Trend verdicts`
6. `## Stale-lane`   (`## Stale lane` also accepted)

**B. `## SHONEN` — `grep -c '^## SHONEN'` must be exactly `1`**, the heading at column 0, not
quoted inside any fence or HTML comment, and placed after the six sections above. Its body must
carry **exactly 4** box lines (`- [x]`, `- [~]` or `- [ ]`; `*` bullets accepted, `+` bullets are
not; box lines inside fences do not count) — one per box of the lane's `SHONEN.md`, verbatim
labels:

1. `- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources — <backticked lane pointer(s)>`
2. `- [~] At least one end-to-end domain task executed and logged in LOG.md — <backticked LOG.md/round anchor>`
3. `- [~] Instructions executable by an agent without oral context — <backticked counter/fixture paths>`
4. `- [~] No cross-domain bleed (PROVINCE.md still accurate) — <backticked PROVINCE.md / boundary evidence>`

(`~` if partially demonstrated, `x` only if the r39 bytes actually discharge the box; the gate
counts lines, not marks, so a wrong mark still passes — the mark must be honest.)

**C. Trend verdicts — exactly one line per trend, label then `:` (or em dash) then a verdict token
as the first word.** Tokens: `improved`, `harmed`, `unchanged`, `unprovable-but-better`. A hyphen
separator (`- expansion - improved`) fails; a negated token (`quality: not improved`) fails; a
duplicate line fails.

```
- expansion: <token> — <evidence>
- quality: <token> — <evidence>
- discernment: <token> — <evidence>
```

**D. Stale-lane — a `## Stale-lane` heading with a non-empty body, and preferably also the
single-line form** `Stale-lane: no — …` (the line form alone passes `stale-lane` but the heading is
still required by `sections`; heading with empty body and no line fails).

**E. Measurements — at least one table row inside `## Before → after measurements`** with ≥2
backticked spans, one of them a **standalone** backticked hex of 7-64 lowercase chars (a hex inside
a longer command span does not count; a 40-hex digest *does*, see blind spot 1, so the hex must
genuinely be the measured commit). For r39 the contract wants three rows; the frozen counter
strings to quote are:

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| `C1` | calibration 7 | `open=16` (`census/round-39/records/c1-before.txt`) | `items=16 open=0 register_cells>=6 register_mismatches=0 commit_distinct>=2` | `python3 -B census/round-39/c1-counter.py …` | `<sha>` |
| `C2` | operability 8 | `pass=2 fail=4` (`c2-before.txt`) | `legs=6 pass=6 fail=0 harm=0` | `python3 -B census/round-39/c2-counter.py …` | `<sha>` |
| `C3` | coverage 8 | `killed=0 survived=4` (`c3-before.txt`) | `mutants=4 killed=4 survived=0 pristine=ok base_killed=0` | `python3 -B census/round-39/c3-counter.py …` | `<sha>` |

**F. Claims — `## Work performed` names 1-3 distinct `C1..C3` ids** (r39: C1, C2, C3). Do not
write `C4`…`C9` in that section; a 4th distinct id fails with `claim ids=4 expected 1-3`. An empty
Work-performed body fails with `claim ids=0`.

**G. Evidence — at least one backticked repo-relative pointer** beginning `census/`, `corpus/`,
`tools/`, `tests/` or `.ufo/`, anywhere outside fences (or a bare 40-64 hex commit id). Fenced
blocks are masked, so evidence quoted inside a fence does not count.

**H. Filing preconditions from the same gate** (not report text): lane tip full SHA equals
`origin/<branch>` (`check-tip`), lane worktree has no modified/untracked paths (`check-clean`), and
the preregistration is non-empty (`check-prereg`).

**I. Keep-out**: `##` headings inside fenced examples are safe (masked), but any real `##` heading
between the six canonical ones truncates the enclosing section's body — do not insert
`## SHONEN`, `## Errata`, a ledger or a note between `## Before → after measurements` and its
table, or between `## Trend verdicts` and its three lines.

## Risks and limits

- **`check-tip` is live.** Between my two gate runs the lane local tip moved from
  `c0b007b4…` (equal to remote) to `50972f0d…` (ahead), so the second run printed
  `check-tip=FAIL detail-tip: local=50972f0d… remote=c0b007b4…`. The r39 report must be gated after
  the L1 has landed and pushed, not while a wave is in flight.
- **`check-clean` fails today** for sibling in-flight bytes (`M corpus/lessons/round-39.md`, four
  `census/round-39/records/*` files). Again a timing artefact; it must be re-run at filing.
- My probes are text mutations of the r38 report; they measure the predicate, not the r39 numbers.
  No r39 claim is verified here — C1/C2/C3 receipts are other seats' work.
- The gate reads `SHONEN.md` at run time: the required box count is whatever that file carries
  (4 now). If a box is added mid-round, the report needs 5 box lines.
- I installed and upgraded nothing; `python3`, `git`, `grep` sufficed.

## Scratch

`/fast/scratch/hyaku/souji-r39/W1ExecReportGate/` still on disk (27 `probe-*.md` inputs plus
`empty.md`), deliberately left so the L1 can re-run any row of the probe table verbatim; safe to
`rm -rf`.
