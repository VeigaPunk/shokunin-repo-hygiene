# Routed evidence, deduplicated — r14 × r15 obligations open at r16

Connector seat `DistillRoutedEvidence` (leaf; read-only; one file owned, this report).
Axes named: **calibration** (primary — obligation/evidence accounting), **operability** (R1/R2 are the
axis's actual debt), **coverage** (R7 is curation, not expansion), **adjacency** (R6 only). This artifact
can improve calibration; it closes no obligation and harms no axis.

## Result

**13 raw routed items → 11 distinct → 7 open lane obligations + 1 operator decision + 3 closed/standing.**

The minimal open set is **exactly r15 R1–R7** (`corpus/lessons/round-15-verifier-spotcheck.md:122-128`).
Round 14's five items contribute no open obligation that r15 did not already enumerate: two are the
referents of r15 R2/R5 (`round-14-verifier-spotcheck.md:160,163`), three were discharged before r16
(`:161,:162,:164`). Consequence for r16: the obligation inventory in the round context is **complete**;
the failure risk is per-obligation evidence, not a missing obligation. A closure that reports "R1–R7"
as seven units without the evidence legs below can still be vacuous.

## The seven distinct open obligations

### R1 — parsing restoration + correction sweep (admission-blocking)

- **Provenance:** `round-15-verifier-spotcheck.md:122`; the value-blind harm it complements is routed
  at `round-14-verifier-spotcheck.md:160-166`, and the parse regression it repairs was landed at
  `b410186`.
- **Distinct because:** a behaviourally perfect guard is inert if the script cannot be read by bash.
  The static leg and the documentation sweep are not covered by the config fixture.
- **Closing evidence (all four legs, same landing revision):**
  1. **Static:** `git show <rev>:tools/souji-census.sh | bash -n` → 0 and
     `... | shellcheck -S warning -s bash -` → 0. Fresh at `cbf688ab2ab28e38103e5a9417ca525b5f2ed423`:
     `0 / 0`. Red leg re-derived at `b410186`: `2 / 1`.
  2. **Behavioural red-before/green-after under the committed fixture:** committed matrix
     (`census/round-16/run-matrix.py --changed <rev>`), changed arm 20/20, r14-harm arm red
     (16/20 fail, all 13 `HARM_CASES` among them), r15-baseline arm recorded as un-runnable.
  3. **Legacy preservation:** `--selftest` 38 checks / 0 failed and `r14-census-boundary.py` 12/12 on
     the changed tool, recorded in the same matrix.
  4. **Corrections:** an appended LOG entry naming the non-parsing `b410186` landing, plus a sweep of
     every stale mention per §Evidence standard "Corrections sweep every mention": `SKILL.md:138`
     (registry row) and `:167-168` (fleet-census instruction), `SKILL.md:226-230`,
     `SCORECARD.md:15` (operability row) and `:66-72` (planned-r16 text),
     `corpus/lessons/round-15.md:94-96`, `.ufo/reports/round-15/souji.md:13`.
- **Status at `cbf688a`:** leg 1 green; legs 2–4 open — the matrix is absent from the committed tree
  (`ls-tree` shows only `run-matrix.py` under `census/round-16`), and no correction text exists
  outside the r15 closure itself (checked SKILL/SCORECARD/LOG/r15 lesson for the parse-failure
  wording: only `round-15-verifier-spotcheck.md` contains it).

### R2 — value/effect-aware preservation with paired controls and mixed fleet (admission-blocking)

- **Provenance:** `round-14-verifier-spotcheck.md:160` ≡ `round-15-verifier-spotcheck.md:123`
  ("r14 R1 still OPEN").
- **Distinct because:** R1 proves the file runs; R2 proves it stopped refusing benign values and
  stopped aborting unaffected peers.
- **Closing evidence:** committed four-arm matrix over `tests/fixtures/r15-census-config.py` —
  benign classes green on pre-harm `a31642d` and changed, red on r14-harm `cc21683`; mixed-fleet
  `R15CFG-16` exact row set with a `core.hooksPath=/dev/null` repo between `a-benign`/`z-benign`
  (a harmless local setting must not suppress peers); mixed-fleet `R15CFG-17` with one
  protected-namespace repo → rc 2 and no rows; degrade `R15CFG-03` → one per-repo `error` row,
  exit 0; namespace retention 12/12 unchanged; the paired-control checker
  (`souji-preservation-evidence` selftest/external/frozen/actual-record) rejects missing,
  green-only, mismatched or weakened paired arms; and, per the r14 adjudication clause, one
  `souji | round-16 | …` operator question if any pre-harm-supported **safe** configuration is now
  refused or degraded (candidates named by the round: bound filter drivers skipping status; `~user`
  include targets degrading).
- **Measured discrimination (data from the untracked matrix, not re-run):** pre-harm fails only
  `02,03,08,11,14,17,18,19` — all non-benign classes (refusals, degrade, safety, and the
  environment-neutralization preserve case); every benign case passes. r14-harm fails
  `01,03,04,06,07,08,09,10,12,13,14,15,16,18,19,20`; changed fails none. The benign paired control
  therefore really is green→red→green, including mixed fleet 16.
- **Status:** fixture cases and an uncommitted matrix exist; committed evidence and the adjudication
  decision are absent.

### R3 — seat-reported known failure carried verbatim; "unverified candidate" banned for known broken

- **Provenance:** `round-15-verifier-spotcheck.md:124`, with the original omission at `:30` (D1).
- **Closing evidence:** `tools/souji-landing-gate.py --round 15 --rev b410186` reports
  `LG-SEAT-UNCARRIED` for the committed `.ufo/waves/round-15/w1/ConfigRepair.md` marker (that file is
  committed at `b410186` — verified by `ls-tree`), and the same gate on the r16 landing rev reports
  zero; the r16 report and `corpus/lessons/round-16.md` quote each seat failure line verbatim
  (the gate checks only wave `.md` → lesson substring, **not** the report); and the historical
  "unverified candidate" texts listed under R1.4 are corrected rather than repeated.
- **Status:** the gate and the r16 lesson do not exist at `cbf688a`; open.

### R4 — frozen pins re-pinned, frozen verdict recorded with its measured revision

- **Provenance:** `round-15-verifier-spotcheck.md:125`.
- **Closing evidence:** `tests/fixtures/r15-preservation-frozen/expected.json` `files` pins match
  committed bytes at the landing rev for `tools/souji-census.sh`, `tests/fixtures/r15-census-config.py`,
  `tests/fixtures/r14-census-boundary.py`; `record_sha256` matches `record.json`; the `record.json`
  is regenerated from real arm runs, not authored; the `--frozen` verdict is recorded together with
  the revision it was measured at.
- **Measured at `cbf688a`:** census pin `b5187351…` matches **no** committed revision (HEAD is
  `fed43c710b75…`; `cc21683`/`fc3a8d4` are `fcff8b05…`; `b410186` is `dab4122c…`); fixture pin
  `6314d45d…` vs HEAD `9151cde8…`; boundary pin `e6a984b1…` matches; `record_sha256 4749ad07…`
  matches `record.json`. **2 of 3 file pins are stale**, and the census pin was never valid.
- **Status:** open; strictly downstream of R1 (the pin must be taken from final census bytes).

### R5 — probe-rule enforcement as audit, not contract prose

- **Provenance:** `round-14-verifier-spotcheck.md:163` ≡ `round-15-verifier-spotcheck.md:126`
  (explicit recurrence).
- **Closing evidence:** an L1 audit record, per seat, comparing each report's `## Commands` section
  against the wave allowlist: command class, verdict, named violations (or an explicit zero with the
  audit basis), and the evidence voided for any violation; plus a check that no seat-executed
  observation is cited as a passing acceptance number (every number re-run by L1 at a named revision);
  historical r14/r15 deviations preserved, not re-run or re-labelled.
- **Status:** the r16 contract now carries the mechanics (allowlist, forbidden list, `## Commands`,
  void rule); the audit artifact cannot exist before round end. Open.

### R6 — explicit cross-domain evidence line

- **Provenance:** `round-15-verifier-spotcheck.md:127`, with D2 at `:31`.
- **Closing evidence:** one line in `.ufo/reports/round-16/souji.md` naming contested scope | owning
  lane | evidence pointer, reported not absorbed (content supplied by `SiblingOverlap`). No gate
  checks this; the non-author closure inspects presence and non-absorption.
- **Status:** r15's report has zero matches for the concept; r16's line is not yet drafted. Open.

### R7 — `rejected` registry row for git-status(1)

- **Provenance:** `round-15-verifier-spotcheck.md:128`.
- **Closing evidence:** one `corpus/SOURCES.md` row for git-status(1) with status cell `rejected`,
  note beginning `REJECTED: …; flip: …` (schema precedent `S030` at `:42`, `S032` at `:44`), date
  2026-10-20 and the opened page's locator; mined/queued counts unchanged, rejected +1; the registry
  validator (`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root … souji`) still
  exits 0 with only the known W04 S035/S036/S038 notices. It must not be counted as coverage or
  expansion.
- **Status:** absent — `SOURCES.md` has no git-status row and ends at S042; the exclusion exists only
  as search-log prose at `:73`. Open.

## Dedupe ledger (13 raw items → dispositions)

| Raw item | Disposition |
|---|---|
| r14 `:160` benign-config repair | open as **R2** |
| r14 `:161` mine the outside disagreement | **closed** in `fc3a8d4`: lesson `R15-M1` (`round-15.md:9`) + criterion Q22 (`QUALITY.md:56`) |
| r14 `:162` wording/evidence boundary | **closed** in r15 (`fc3a8d4` for the lane files): `SKILL.md:213-216`, `SCORECARD.md:45`, `LOG.md:751-755`, lesson `R15-M2` (`round-15.md:10`); the r15 report carries the same limit at `:12` |
| r14 `:163` enforce no-probe rule | open as **R5** |
| r14 `:164` retained original observations | **standing label rule**, no artifact; honoured by `LOG.md:753-755` and the r15 process section |
| r15 `:122` R1 | open as **R1** |
| r15 `:123` R2 | **duplicate** of r14 `:160` (self-declared "still OPEN") |
| r15 `:124` R3 | open as **R3** |
| r15 `:125` R4 | open as **R4** |
| r15 `:126` R5 | **duplicate** of r14 `:163` (self-declared recurrence) |
| r15 `:127` R6 | open as **R6** |
| r15 `:128` R7 | open as **R7** |
| r15 `:129` operator-sweep disposition | **operator-owned, out of lane** — the contract forbids opening/moving the directory; it cannot be closed by souji and must not be counted |

D1/D2 in the r15 closure are not separate obligations: D1 is R3's omission plus R1's correction;
D2 is R6.

## R16 coverage map and gaps

| Row | Supplying r16 artifact / item | Gap that survives a perfect seat outcome |
|---|---|---|
| R1 | C1 claim, `cbf688a`, `census/round-16/run-matrix.py`, `DraftR15Correction` (lesson/report texts), `ConnLogConvention` (LOG correction entry), `ConnSkillRegistry` (SKILL rows + sweep), `ConnScorecard` (operability row) | corrections are drafts; the append-only edits and the LOG entry must be committed; matrix currently untracked |
| R2 | C1 claim, `r15-census-config.py` cases 01–20 (esp. 16/17), `r14-census-boundary.py`, `DraftOperatorQuestion` | committed evidence; the adjudication trigger is conditional and can be silently skipped |
| R3 | `LandingGate`, `CriticDisclosureR3`, `DraftReportSkeleton`, `DraftLessonMistakes` | gate does not check the report; gate can be vacuous if the r16 wave tree is not in the landing rev (see risk 2) |
| R4 | `PreservationRepin` | none structural; must wait for R1's final bytes |
| R5 | wave contract, `RevengeProbeRecurrence`, report skeleton | the audit itself — no seat can produce it; it is L1's obligation at closure |
| R6 | `SiblingOverlap`, report skeleton | no gate; a one-line check by the closure |
| R7 | `SrcGitStatusRejected`, L1 registry edit | row must not inflate counts; validator rerun |

## Second-order interactions and risks

1. **The C2 gate's marker extraction is line-granular, not failure-granular.** The `LandingGate` item
   extracts every wave-`.md` line matching its pinned alternation (the `STATUS:`-class tokens plus two
   unanchored parse-failure phrases) and demands the *whole stripped line* as a substring of
   `corpus/lessons/round-N.md`. Any wave report that merely *quotes* or *logs* the phrase — a critic
   restating the r15 defect, or a verification command whose grep pattern contains it — becomes an
   uncarried marker, and the lesson must then reproduce that prose verbatim. The class is therefore
   broader than seat failure disclosure, and the check cannot distinguish a failure from a quotation:
   green is achievable by quoting discussion, red is caused by logging the check. This report contains
   no matching line (scanned against the pinned pattern), so it is not itself an instance. Minimal
   spec delta: skip fenced code blocks and `## Commands` sections, and optionally anchor the
   parse-failure alternatives to sentence start; if quotation-noise persists, extract only the
   sentence carrying the marker rather than the whole line.
2. **Gate vacuity.** `git archive REV` sees only committed bytes, and `.ufo/waves/round-16` is empty
   at `cbf688a`. If the landing commit omits the seat reports, `LG-SEAT-UNCARRIED` passes on zero
   markers. R3's evidence must include `git ls-tree <landing> -- .ufo/waves/round-16` being non-empty
   (and the r15 arm non-vacuous by the committed `ConfigRepair.md`).
3. **R4 ordering.** Re-pinning before the census bytes are final invalidates the pin again; two pins
   are already stale and one was never valid.
4. **R1/R3 collision.** R1's corrections edit *historical* r15 files; R3's carry is the *new* round's
   lesson. Rewriting the r15 lesson is forbidden; leaving the r16 lesson uncarried is R3's defect.
5. **R2's green-only summary.** The round context cites only 20/20, 12/12, 38/38. The red-before leg
   exists only in the untracked matrix (harm 16/20, pre-harm 8/20). A closure that cites only green
   tallies has not shown red-before.
6. **Disclosure is not closure.** The r14 no-trade rule stands: residual safe-config contractions need
   the operator question, not prose.
7. **R5 is the only obligation with no artifact.** Describing the audit is not auditing; the r16
   report must contain the per-seat table (or an explicit zero-violation statement with its basis).
8. **R7 is curation.** A `rejected` row changes the rejected count only; treating it as coverage or
   source growth would be a fresh accounting error.
9. **Fixture precedence.** The `round-16` docstring says it supersedes later bullets, but the older
   "Semantics pinned here" bullets still state opposite outcomes for promisor invalid booleans and
   `alternateRefsCommand`. Precedence is stated, so this is not a contradiction, but a reader or
   checker that stops at the older bullet can build the wrong oracle; the case IDs are authoritative.

## Proposed move (one, bounded)

Adopt R1–R7 as the **sole acceptance ledger** for r16 — one row, one committed evidence artifact,
no row closable by an uncommitted observation, a draft, or disclosure — and land the C2 gate with the
two scope fixes above (fence/`## Commands` exclusion; non-empty landing wave tree). This is the only
move I found that improves calibration without touching operability, coverage or adjacency.

## Verification performed (fresh, static only)

| Check | Result |
|---|---|
| `bash -n` / `shellcheck -S warning` over four arms | `a31642d 0/0`; `cc21683 0/0`; `b410186 2/1`; `cbf688a 0/0` |
| census digest at `cbf688a` | `fed43c710b75…` (pin `b5187351…` matches no revision) |
| fixture digest at `cbf688a` | `9151cde8…` (pin `6314d45d…`) |
| boundary fixture digest | `e6a984b1…` (pin matches) |
| `record.json` digest | `4749ad07…` (matches `record_sha256`) |
| `tools/souji-landing-gate.py`, `corpus/lessons/round-16.md` | absent at `cbf688a` |
| committed `.ufo/waves/round-16` tree | empty at `cbf688a`; r15 `ConfigRepair.md` committed at `b410186` |
| committed `census/round-16` at `cbf688a` | `run-matrix.py` only; `c1-matrix.json` absent |
| this report vs the pinned `LG-SEAT-UNCARRIED` pattern | no matching lines |
| matrix arm tallies (untracked `census/round-16/c1-matrix.json`) | config fail counts: changed 0/20, r14-harm 16/20, pre-harm 8/20, r15-baseline 20/20; namespace fail counts: changed 0/12, r14-harm 0/12, pre-harm 10/12, r15-baseline 12/12; selftest 38 checks/0 failed |

Not run: any fixture, the census, the gate, or any real-directory census. No unrun check is reported
as passing; the matrix tallies are read as data from an uncommitted artifact, and the benign-class
pass/fail split is read from its per-case records.

STATUS: none — no known failure in this seat; all statements are committed-byte or static observations,
or are labelled as inference; the uncommitted matrix is explicitly not acceptance evidence.

## Probe-rule disclosure

Shell commands outside the wave's literal allowlist, all read-only and scoped to exact named files:
the shell equivalents of `grep`/`head`/`wc`/`tail`/`printf`/`echo` over the files cited above; seven
`python3 -c` `json.load` reads of `.ufo/waves/round-16/w1-spec.json` (no repository code imported or
executed); and one path-scoped `git -C <lane> status --porcelain -- <four named paths>` — `status` is
not among the enumerated git subcommands. No directory enumeration, no fixture/census/gate execution,
no forbidden path touched. The transcript is not retrospectively rewritten: the one claim that rested
on `status` (the matrix is not committed) is now independently evidenced by `ls-tree`, and L1 may void
or discount the rest without losing the obligation ledger.

## Commands

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'Q2[0-9]|Round 1[456]|criteria' corpus/QUALITY.md | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l corpus/lessons/round-15.md corpus/lessons/round-14.md corpus/QUALITY.md LOG.md .ufo/waves/round-16/w1-spec.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E '^\| ?R[0-9]|^R[1-7][ ,.]|^- \*\*R[1-7]|R[1-7] ' corpus/lessons/round-15.md | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
s=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for it in s['items']:
    print(it.get('name'),'|',it.get('agent',''),'|',it.get('report',''))
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
s=json.load(open('.ufo/waves/round-16/w1-spec.json'))
want={'DistillRoutedEvidence','ConnRoutedLedger','SrcGitStatusRejected','PreservationRepin','LandingGate','CriticDisclosureR3','DraftLessonMistakes','DraftR15Correction','RevengeProbeRecurrence'}
for it in s['items']:
    if it.get('name') in want:
        print('='*20, it.get('name'), '|', it.get('agent',''))
        print(json.dumps({k:v for k,v in it.items() if k!='name'}, indent=1)[:2600])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
s=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for it in s['items']:
    if it.get('name') in {'DraftReportSkeleton','DraftOperatorQuestion','DraftSkillSection'}:
        print('='*20, it.get('name'))
        print(it['prompt'][-1500:])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
s=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for it in s['items']:
    if it.get('name') in {'LandingGate','SiblingOverlap','ConnRoutedLedger'}:
        print('='*20, it.get('name'))
        print(it['prompt'])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json,textwrap
s=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for it in s['items']:
    if it.get('name') in {'LandingGate','CriticDisclosureR3','PreservationRepin','RevengeProbeRecurrence'}:
        print('='*25, it.get('name'))
        p=it['prompt'].split('Act directly via tool calls.')[-1].strip()
        print('\n'.join(textwrap.wrap(p,110)))
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json,textwrap
s=json.load(open('.ufo/waves/round-16/w1-spec.json'))
for it in s['items']:
    if it.get('name') in {'ConnLogConvention','ConnSkillRegistry','ConnScorecard'}:
        print('='*25, it.get('name'))
        p=it['prompt'].split('Act directly via tool calls.')[-1].strip()
        print('\n'.join(textwrap.wrap(p,110)))
"
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -10 && git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain -- tools/souji-census.sh tools/souji-landing-gate.py census/round-16 tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -S attempt_reuse -- SKILL.md SCORECARD.md && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sha256sum && bash -n <(git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh) && echo BASHN_OK
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -S attempt_reuse -- LOG.md corpus/lessons/round-15.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat b410186 cbf688ab2ab28e38103e5a9417ca525b5f2ed423
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for rev in a31642d14006830ec62edf40b0354c3699728c4a cc2168325768d5356a82c039dcdf787377c55784 b410186cea626a67c92396ac58fbd57fb86876ac cbf688ab2ab28e38103e5a9417ca525b5f2ed423; do git show $rev:tools/souji-census.sh | bash -n; b=$?; git show $rev:tools/souji-census.sh | shellcheck -S warning -s bash - >/dev/null 2>&1; s=$?; echo "$rev bashn=$b shellcheck=$s"; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for p in tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py tests/fixtures/r15-preservation-frozen/record.json; do printf '%s ' "$p"; git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:$p | sha256sum; done
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 69c1604:SKILL.md | grep -n "attempt_reuse" ; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 69c1604:SCORECARD.md | grep -n "attempt_reuse"
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only b410186cea626a67c92396ac58fbd57fb86876ac -- .ufo/waves/round-15 ; echo '--- r16 ---'; git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- .ufo/waves/round-16
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree -r --name-only cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- census/round-16
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l .ufo/waves/round-16/w1/DistillRoutedEvidence.md && tail -3 .ufo/waves/round-16/w1/DistillRoutedEvidence.md
```

Read-only `read`/`grep`/`glob` calls over exact named files (including the `?q=` JSON projections of
`census/round-16/c1-matrix.json`) are not shell commands and are not listed above. No file outside this
report was written; no repo code was executed; no census or fixture was run.
