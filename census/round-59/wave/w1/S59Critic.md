# S59Critic — bounded falsification of the r59 registry-kind claim

Seat: critic (S59Critic). Read-only over the lane; no production, fleet, sibling, commit, push or jj
mutation was made. All git calls in this seat's fixtures name an explicit `-C <fixture>` path and the
fixture toplevel was asserted before the first commit. Scratch root: `/fast/scratch/hyaku/souji-r59/S59Critic/`.

## Scope of this review

The frozen claim (`census/round-59/preregistration.txt` at `19f44552378d333f401ff2f0864c4e8b9c59ab1f`)
declares ONE bounded calibration claim: the unique current assessment-comparison registry row's kind
cell is `evidence` where it should be `gate`, counted by `census/round-59/c1-counter.py`, target
`assertions=1 mismatches=0`. This seat attacks the *move/no-harm and bounds* of that claim: whether
the axis move is genuine bounded calibration or thin bookkeeping, whether the instrument can be
fooled, and whether the round silently closes inherited debts.

## Verdict in one line

**The classification correction is genuine and the r58 defect it repairs is real — but the frozen
counter is a one-cell, one-row, string-equality instrument whose green state is reachable by edits
that skip every piece of claimed substance, and the preregistration is grammar-red under the lane's
own Q99 freeze gate. Admission should therefore hinge on the kill rule (an actually-landed, actually
executable assessment gate with a committed public selftest), not on `mismatches=0` alone.**

## Findings

### F1 — The frozen counter's target is reachable by a one-cell edit that skips all claimed substance (BLOCKING for using the counter as the sole admission predicate)

`census/round-59/c1-counter.py:9-14` selects the row by prefix, splits on `|`, and tests exactly one
string: `row[2] != 'gate'`. Nothing else in the row is read. Therefore:

| probe | landed SKILL.md state | counter |
|---|---|---|
| A | **only** the r58 row's kind cell `evidence`→`gate`; no r59 row, no gate file, no selftest | `assertions=1 mismatches=0` rc=0 |
| B | r58 row left `evidence` + a new r59 row `gate` | `assertions=1 mismatches=0` rc=0 |
| H | r59 row `gate` citing `census/round-59/NONEXISTENT-gate.py` and a nonexistent pinned-value path | `assertions=1 mismatches=0` rc=0 |
| I | r59 row `gate` **inside a fenced code block** | `assertions=1 mismatches=0` rc=0 |
| J | r59 row `gate` **inside an HTML comment** | `assertions=1 mismatches=0` rc=0 |
| O | r59 row `gate` with entry command, verdict map, self-test, pinned path and write scope **all blank** | `assertions=1 mismatches=0` rc=0 |
| N | r59 row with trailing whitespace | rc=0 |

Receipt: `.ufo/waves/round-59/w1/S59Critic/probe-rows.txt` (script `probe-rows.py`, same directory).

Consequences, stated precisely:

1. **The cheapest do-nothing control reaches the target.** §9 of the round prompt requires "the
   cheapest control that skips the claimed work" to be built, scored and committed *before* freezing,
   and forbids a target such a control can reach. Probe A is exactly that control for the *kind
   correction* and it is green. The committed `controls.json` positive case
   (`'| evidence |'`→`'| gate |'` on the r58 row) is the same shape and is also green — so the frozen
   control set does not separate "kind cell edited" from "kind cell edited *and* a real assessment
   gate landed with a committed selftest". The preregistration's own `Kill:` line already compensates
   ("missing actual assessment gate/self-invocation repair … rejects admission"), and its `Before:`
   line says the counter "is not execution authentication". That compensation is the correct
   architecture, but it means **`mismatches=0` is not the claim's admission predicate; the conjunction
   (counter green AND assessment gate with public selftest landed) is.** The round report must say so
   explicitly and must present the conjunction, not the counter alone, as the admission evidence.

2. **The counter is a subject-drifting instrument, and the drift is not visible in its output.** The
   counter prefers any `| r59 assessment comparison |` row and *ignores* the r58 row entirely when one
   exists (`c1-counter.py:9-11`). Probe B: with the r58 row still `evidence` — i.e. the frozen
   population item `R58-KIND` (`census/round-59/population.tsv:2`) still wrong — the counter is green.
   Probe C is the mirror: r58 row `gate` plus an r59 row `evidence` is **red**. So the same pair of
   facts scores green or red depending only on which prefix the counter happens to prefer, and the
   counter's single `SUMMARY` line cannot report which row it scored. `population.tsv` enumerates the
   population as the **r58** surface (`R58-KIND | SKILL.md r58 assessment comparison`), while the
   counter's fallback branch prefers the **r59** row. The before/after pair therefore measures two
   different subjects across the transition unless the landing keeps the r58 row's kind cell correct
   too. This is exactly the r56/r57 pattern the lane keeps re-learning: the finite instrument holds
   while the enumerated surface is wrong.

3. **The counter has no Markdown model.** Probes I and J show a row inside a fenced block or an HTML
   comment satisfies it, because the scan is a raw line-prefix match over `git show rev:SKILL.md`
   text. This is the same class of defect as the lane's inherited visibility debts (second opener,
   code-span, escape, link, TAB) and it is *not* repaired by this round — it is inherited into the
   r59 instrument, not closed. Probe M (row as a list item) and probe K (row name with different
   case) are not selected at all, so a near-miss spelling silently falls back to the r58 branch.

4. **The counter's row-shape guard is brittle in a way that will bite the landing.** `len(rows[0]) != 10`
   (`c1-counter.py:12`) counts pipe-separated parts, so a verdict-map cell containing a literal `|`
   (probe F) or a missing cell (probe E, probe G-9-cells) yields `REGISTRY-ROW-SHAPE` rc=2 instead of
   a kind verdict. The `preregistration.txt` `Target:`/`Kill:` do not name a column count, so the
   landing author must discover the 8-column shape requirement from the counter's source. This is a
   documentation gap, not a claim defect, but it should be in the round report.

### F2 — The positive control is a marker-only forgery with no gate behind it (real, and disclosed — but it must not be the only positive)

`census/round-59/controls.json` case `"positive"` replaces `| evidence |` with `| gate |` on the r58
row and expects rc=0. There is no gate file, no selftest and no executable artifact in that fixture;
the "positive" is a text substitution. That is a legitimate *classification* control and the
preregistration says so ("Counter counts classification only: a truthful kind edit legitimately
passes"). But it means the committed control set contains **no** case where a genuine assessment gate
with a public selftest is what makes the target true, and **no** case where a fabricated gate name
(probe H) is rejected. The frozen controls discriminate prose forgery and duplicate rows well
(`prose-forgery` rc=1, `duplicate-forgery` rc=2 — both independently reproduced), but they cannot
discriminate "real gate" from "text says gate". The new gate delivered by S59ExecGate does carry that
discrimination (`SELFTEST control=FALSE-GREEN-REJECTED stub_meets=1 discriminated=4 cases=5`,
reproduced by this seat at rc=0), but it is not yet committed, so it is not part of any frozen
control set.

### F3 — The frozen preregistration is grammar-red under the lane's own Q99 gate (fixable, reportable)

`corpus/QUALITY.md:255` (Q99) binds the *grammar* of the freeze and names the checker:
`python3 -B tools/souji-freeze-check.py --root <lane> --prereg census/round-<N>/preregistration.txt --rev <full40>`
"must exit 0 and print `SUMMARY claims=<k> findings=0` at the report tip". Run against the frozen r59
preregistration at its own freeze commit:

```
FINDING C0 FIELD-MISSING Round
SUMMARY claims=1 findings=1
EXIT=1
```

Receipt: `.ufo/waves/round-59/w1/S59Critic/freeze-check-evidence.txt`.

Facts: the `## C1` block carries all six Q99 block keys (`Base:`, `Counter:`, `Population:`,
`Control:`, `Target:`, `Kill:`), all digests match the freeze commit, `Base:` is a strict ancestor,
and `Control:` (`census/round-59/before.txt`) ends in `EXIT=1` (red). The **only** failing clause is
the file-level `Round:` key line, which `tools/souji-freeze-check.py` needs to evaluate the
dispatch-before-freeze clause. A one-line simulation confirms the diagnosis exactly: prepending
`Round: 59` to the frozen text yields `claims=1 findings=[]`.

Precedent and bounds: the same gate is red on the two prior rounds' preregs for the *same* `Round:`
clause plus more (`round-57` → 11 findings; `round-58` → `FIELD-MISSING Round` + `NO-CLAIMS`), so
this is a recurring lane-wide grammar gap rather than an r59-introduced regression — but r59 is the
first round where the preregistration otherwise satisfies every block clause, so it is the first
where the single missing line is the whole gap. Because Q99 binds the grammar of the freeze and the
dispatch clause cannot be evaluated without `Round:`, the round's own `before.txt`/`controls.json`
chronology (which *is* verifiably compliant — controls commit `74455b72` at 15:33:00 is a strict
ancestor of freeze `19f44552` at 15:33:21, and `git merge-base --is-ancestor` returns 0) is
nevertheless unevaluated by the lane's own gate. **Smallest safe correction:** the L1 adds a
column-0 `Round: 59` line to the preregistration and re-freezes (the preregistration is not in the
"counter/population/controls remain byte-identical" freeze rule, so a re-freeze is permitted) — or,
if the freeze commit is already treated as immutable, records the C0 finding explicitly in the round
report and the lesson as a known open grammar debt, and does **not** claim the freeze is
Q99-conformant. What must not happen is a silent omission.

### F4 — Prior r56–r58 rejections and the inherited debt list: no silent closure observed (no-harm holds, with one watch item)

Read in full: `census/round-59/preregistration.txt` `Inherited debts:` line; `corpus/lessons/round-59.md`
`## Preserved debts and boundaries`; `corpus/lessons/round-58-verifier-spotcheck.md:62-68` (the three
routed defects) and `corpus/lessons/round-58.md` `## Scope and residuals`.

- r56 verdict `rejected-harmed`, r57 `rejected-harmed`, r58 `admitted=false / rejected-honest-stop`
  — none is re-admitted or re-declared by r59. r59's claim is a *different* surface (registry kind
  cell), not a re-run of any rejected predicate. **No silent closure.**
- Routed defect 1 (r58's missing pre-freeze control) is genuinely repaired this round and the repair
  is verifiable, not asserted: controls commit `74455b72` precedes freeze `19f44552` as a strict
  ancestor, and the freeze commit's diff adds only `population.tsv` + `preregistration.txt`. That is a
  real no-harm improvement over r58.
- Routed defect 2 (the `evidence`-kind row) is the subject of this claim — genuinely addressed, and
  the r58 row's `evidence` cell is still a *measurement producer* per the lane's own `SKILL.md:206`
  glossary ("`evidence` rows are measurement producers, not gates … a row whose self-test cannot
  fail is a `probe` or an `evidence` row, never a `gate`"). The r58 comparator *does* return a verdict
  and *does* compare against persisted expectations, so the `evidence` cell was wrong under the
  lane's own glossary and under PROTOCOL's Gate standard. Classification correction: **genuine, not
  bookkeeping**.
- Routed defect 3 (keep inherited debts OPEN) is honoured: `census/round-59/preregistration.txt`
  `Inherited debts:` lists parser visibility/second opener/code-span/escape/link/TAB, recorder
  dirty/overwrite, receipt-confinement atomicity/resource bounds, capture row-set meta-test,
  historical receipt bindings and diagnostic escaping as OPEN, with `Certification OFF`. The r59
  lesson repeats the same list. No debt is claimed closed. **No harm established.**
- Watch item: the r59 delivered gate (S59ExecGate) reproduces the r58 counter's note derivations
  exactly and adds a public subprocess selftest; this seat independently confirmed clean-path stdout
  parity at both `da5af55b` and `19f44552` (byte-identical) and the 5-case selftest (rc=0). It is
  also read-only over committed Git blobs. It does **not** repair the parser/recorder/confinement
  debts, and its own report says so. No conflict.

### F5 — The claim is one bounded axis move on the right axis; §9 sizing and "do-nothing control" are the weak points (§9)

- Axis naming: §9 requires naming the axis "by the surface the round changes". The surface is the
  SKILL.md registry row; the lane's own owned axis for "self-assessment quality / entries match
  observed repo state" is **calibration**, the lane's lowest owned legacy score (7). The preregistration
  names calibration and leaves the numeric score unmapped — consistent with the lane's
  legacy-unmapped convention and with §9's "no invented scale". The routed defect is a *status-neutral
  conformance* defect in the lane's own registry home, which is calibration-shaped. **Axis choice
  holds.**
- §9 "Prefer 2 claims": r59 declares one. The preregistration is explicit that this is one bounded
  claim and not a batch, and the one claim is falsifiable with one command over committed bytes.
  One claim is a deviation from the *preference*, not a rule breach. Acceptable, and the low claim
  count is what keeps the counter's weakness from being multiplied.
- §9 "Never narrow a target after landing" / "the claim is judged on the counter, kill rule and
  predicate declared before data": the counter, kill rule and population were all committed at
  `19f44552` and are byte-identical at the tip (verified: `c1-counter.py` and `controls.json`/
  `controls.py` sha256 unchanged; `population.tsv` sha256 `c2e24c99…` matches the freeze). **Frozen
  before any candidate score.** The executor's `precondition.txt` records the lane head at
  `19f44552` at record time, and the wave dispatch/ready files were written at 15:34:01–15:34:40,
  *after* the 15:33:21 freeze. Good chronology.
- §9 "the cheapest control that skips the claimed work … if it meets the target, the counter or target
  is wrong — fix it before data": **this is where the frozen instrument fails the rule** — see F1. The
  cheapest control (probe A) reaches the target. The preregistration anticipated this in prose
  ("Counter counts classification only") but the *frozen control set* does not contain the
  cheap-skip-work case as a **red** arm, only as the **green positive**. That is the smallest safe
  correction available: the missing control is not a new counter but a **committed control case**
  scoring probe-A-shaped state, which is red under the intended conjunction (counter green AND a real
  landed gate with a committed selftest). Since the counter is frozen, the corrected control belongs
  to the *conjunction* predicate, i.e. to the new gate's own frozen expected set — which S59ExecGate
  already supplies in `assessment-selftest-expected.tsv` (5 independent cases + a
  `FALSE-GREEN-REJECTED` stub control).

## Bound verdict on the axis move

- **Genuine bounded calibration: yes.** The r58 row's `evidence` cell misclassified a verdict-returning
  comparator under both PROTOCOL's Gate standard and the lane's own `SKILL.md:206` glossary. Correcting
  it, and registering the *current* row once, is a real self-description repair, externally routed by
  the r58 outside closure (routed defect 2), one row, one cell, one command. It is not a parser
  repair and the preregistration correctly refuses to claim one.
- **Thin bookkeeping: no — but the measured evidence is thinner than the claim.** The counter proves a
  *label* changed. It does not prove a gate exists, is executable, self-invokes, or is the current
  interface. The claim's substance therefore rests on the kill-rule conjunct and on the delivered
  gate's own selftest — not on `mismatches=0`.
- **No-harm: holds.** No axis is newly harmed; inherited debts are listed OPEN and remain OPEN;
  certification OFF; prior rejections untouched; the new gate is byte-identical to the r58 counter on
  the clean path and adds only a stable `ASSESSMENT-MISMATCH` id plus rc2 mapping (independently
  confirmed, including a live one-note-omission fixture returning rc=1 with
  `FINDING ASSESSMENT-MISMATCH` and `mismatches=1`).

## Smallest safe corrections (for L1 integration, in priority order)

1. **Do not present `mismatches=0` alone as the admission evidence.** Present the conjunction:
   frozen counter green at the measured revision **and** a committed, executable assessment gate with
   a committed public selftest whose expected set is committed and independent. State plainly that the
   counter is classification-only and that a one-cell kind edit satisfies it (probe A) — the preregistration
   already says this; the report must carry it into the admission paragraph, not only the preregistration.
2. **Land the gate and its expected TSV under `census/round-59/` (tracked), not only in the gitignored
   wave directory.** Today `git log --all -- census/round-59/assessment-gate.py` and
   `…/assessment-selftest-expected.tsv` are empty and `git ls-files .ufo/waves/round-59/` is 0 — the
   delivered gate exists only in an ignored path. The gate's `--selftest` resolves its expected TSV
   relative to its own file (`HERE / 'assessment-selftest-expected.tsv'`), so a moved gate without a
   moved TSV returns `CANNOT-EVALUATE expected unreadable` rc=2 (reproduced). Also note
   `tools/souji-landing-gate.py`'s `LG-MISSING-REG` check extracts `census/round-<n>/…py` paths cited in
   SKILL.md and fails if the cited file is absent at the measured rev — so a registry row citing
   `census/round-59/assessment-gate.py` is only conformant once that path is committed.
3. **Register exactly one current row, and keep the r58 row's kind cell correct.** The counter prefers
   the r59 prefix and ignores r58, so a landing that adds a r59 row while leaving the r58 row
   `evidence` makes the frozen population item `R58-KIND` still-wrong *and* the counter green (probe B).
   Either the r58 row is corrected too (as the preregistration's "classify r58 comparator as historical
   gate" intends) or the population entry must be reconciled with what the counter actually measures.
   Confirm after landing that exactly one `| r59 assessment comparison |` line exists and that the r58
   row no longer reads `evidence`.
4. **Record the Q99 `C0 FIELD-MISSING Round` finding.** Either add the column-0 `Round: 59` line and
   re-freeze, or disclose the red grammar gate and the recurring precedent in the round report and
   lesson. Do not let the report claim a Q99-conformant freeze without running the tool.
5. **Carry the counter's raw-line/no-Markdown-model limit into the report** (probes I/J) alongside the
   inherited visibility debts, so the r59 instrument is not mistaken for a Markdown-aware check.

## What would change this verdict

A committed, revision-bound after-state in which the *conjunction* is red under the cheapest
skip-work control — i.e. a control case where the kind cell says `gate` but no landed gate/selftest
exists and the conjunction still rejects it — plus a Q99-green freeze and a committed gate+TSV under
`census/round-59/`, would move F1 and F3 from blocking to closed and leave only the disclosed
instrument limits.

## Deliverables (own delivery directory only)

| Path | Role |
|---|---|
| `.ufo/waves/round-59/w1/S59Critic/probe-rows.py` | 16 read-only probes (cases A–P) of the frozen counter over isolated git fixtures; frozen counter bytes never modified |
| `.ufo/waves/round-59/w1/S59Critic/probe-rows.txt` | probe output with per-case intent (F1 evidence) |
| `.ufo/waves/round-59/w1/S59Critic/independent-replication.txt` | independent replications: frozen counter at base+freeze, counter `--selftest` 4/4, delivered-gate clean-path parity, delivered-gate `--selftest` 5/5, gate-without-TSV rc=2, committed-history state of the delivered artifacts (F2/F4 evidence) |
| `.ufo/waves/round-59/w1/S59Critic/freeze-check-evidence.txt` | the lane's own Q99 freeze-grammar gate on the frozen r59 preregistration, the two prior preregs for precedent, and the `Round: 59` simulation (F3 evidence) |

Scratch `/fast/scratch/hyaku/souju-r59/S59Critic/` was removed after these receipts were retained.

Report: .ufo/waves/round-59/w1/S59Critic.md
