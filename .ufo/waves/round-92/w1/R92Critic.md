# R92Critic report

## 1. Do-nothing reach

C1: a no-work run cannot reach the after predicate. The committed control
`census/round-92/controls/c1-control-r91-population.txt` (P2) records the 47
frozen targets scored on the r91 63-row population under the r92 harness:

```
SEARCH-SUMMARY generated=47 ambiguous=0 uncompiled=0 hung=0 scored=47 killed=0 survived=47
EXIT=0
```

with every one of the 47 lines `killed=no rc=0`. I did not re-run the 47-way
search (the after-arm is the expensive run); instead I re-ran the pristine
harness arm on the r91 population, which is the do-nothing reach for the
second half of the predicate: `sep-c1-pristine-r91pop.txt` prints

```
SUMMARY rows=63 mismatches=0 accepted=0 refused_true=0 errors=0
EXIT=0
```

That is, without LD4r no row asserts the success exit code, so the
`h-exit-always-1` mutant — the most trivial member of the target set — and
every other target survive. The control number (killed=0, survived=47) is
the no-work ceiling for C1.

C2: a no-work run cannot reach the after predicate. The committed control
`census/round-92/controls/c2-control-r91-tool-both-arms.txt` and my re-run
`c2-control-rerun.txt` agree byte-for-byte on the numbers:

```
SUMMARY cases=20 tool_pass=16 before_pass=16
EXIT=1
```

(KFF14/KFF15/KFF16/KFF18 red, KFF17 green; KFF18 unfaithful=28.) Re-run of
the after arm (`c2-after-rerun.txt`) gives `tool_pass=20 before_pass=16`
EXIT 0 with KFF18 unfaithful=0 for the filed tool and 28 for the before tool.
The forgery probe re-run (`c2-forgery-rerun.txt`) reproduces the pre-freeze
receipt exactly: `FORGERY-SUMMARY forgeries=5 rejected=5 positive=pass`
EXIT 0 (F1 18/20, F2 19/20, F3 18/20, F4 18/20, N0 16/20). The r87 K4
regression re-run (`c2-k4-rerun.txt`): `SUMMARY rows=12 mismatches=0
errors=0` EXIT 0.

## 2. Target selection / falsifiability of C1

The 47 targets were chosen after the feasibility run on the r92 population
(`census/round-92/controls/c1-feasibility-r92-prefreeze.txt`:
`SEARCH-SUMMARY generated=124 ambiguous=0 uncompiled=0 scored=124 killed=47
survived=77` over the 124 pre-freeze survivors). Targets + residual =
survivors exactly and disjointly (verified in this seat: targets subset of
the 124 survivors, residual subset, union = survivors, intersection empty).

What would have refuted the claim, given its wording ("kills the 47
survivors listed in census/round-92/c1-targets.json"): (a) the after-arm
re-derivation showing killed < 47 — i.e. non-reproducibility of the
feasibility kills, e.g. a kill that depended on lane state at feasibility
time; (b) the pristine LD4r line not reading `rc=0 match=yes`, which would
mean the row does not pass on the unmutated counter; (c) the do-nothing
control showing killed > 0 on the r91 population, which would mean the row
is not what binds them. All three are checkable and none is tautological:
(a) is an empirical reproducibility claim, (b) pins the row to the pristine
counter, (c) separates the new row from the old population.

What the claim does not say beyond its construction: the number 47 is
derived, not predicted. Stated limit (vi) says so openly: "the claim is that
one exit-polarity row binds them, not that the row was predicted to." Any
second rc-asserting row would satisfy the same wording with a different
target set, and the wording would still be true. So the claim has falsifiable
content only through (a)-(c) above; it does not test ex-ante prediction of
which mutants die. The honest, non-tautological remainder is the residual
77 (`census/round-92/records/c1-residual-survivors.json`), which the claim
leaves unclassified and unbound — it is a stated limit, not a hidden gap.

The strongest counterexample I can construct — an LD4r variant that kills a
different subset — does not falsify any sentence of the claim as written,
because the claim names the frozen file, not a property of all rc-rows. I
judge that a weakness of certifying power, not a wording falsification.

One mechanism check: 43 of the 47 targets lie off the exit path (lines
214-468, the judgement logic) and 4 on it (545/552/574 + h-exit-always-1).
LD4r kills off-exit mutants through `ok = counts["resolved"] == len(pop)`
(line 552): any mutant that turns a resolved item unresolved flips the
counter to exit 1, and LD4r is the only row that observes it. This is the
calibration content: the population previously could not see a whole class
of self-assessment failures.

After-arm verification in this seat: the first 41 targets scored
`killed=yes rc=1` with zero survivors (`search-r92-47-partial.txt`), and the
remaining 6 scored in the tail rerun (`search-tail6.txt`):
`SEARCH-SUMMARY generated=6 ambiguous=0 uncompiled=0 hung=0 scored=6 killed=6
survived=0`. Together: 47/47. The pristine harness on the r92 population
(`harness-r92-out.txt`) prints `SUMMARY rows=64 mismatches=0 accepted=0
refused_true=0 errors=0`, LD4r `rc=0 match=yes`, EXIT 0. The combined
47-target after arm therefore reads killed=47, survived=0, EXIT 0 — the
predicate holds as frozen.

## 3. Separability

Static: no file in the C1 predicate (search, harness, counter) mentions the
C2 tool, fixture, or probe, and no file in the C2 predicate (tool, fixture,
probe, k4 counter) mentions the C1 search, harness, targets, counter, or
LD4r. Both directions false across every checked token.

Dynamic (counts as "r91 tool restored" vs "r91 population restored"):

- C1 after-arm with the r91 tool restored: the C1 instruments never read
  `tools/souji-record-agreement.py`. `git diff 5339b2ac HEAD -- tools/
  tests/ census/round-87/` touches only `tools/souji-record-agreement.py`
  (the C2 change) and the new C2 fixture. The counter is frozen
  (sha256 fd0a8e24…, unchanged), the harness's lane inputs are the frozen
  round trees. The verified 47/47 after arm above ran against the working
  tree that contains the r92 C2 tool; since no C1 code path reads that
  file, restoring the r91 tool cannot move the result. The separability
  holds by code path, not by trust.
- C2 after-arm with the r91 population restored: the C2 fixture reads only
  `--tool` and `--before` bytes; nothing in it names a C1 file. Running it
  with the r91 tool as both arms (the exact restored state,
  `sep-c2.txt`) reproduces the do-nothing control: `tool_pass=16
  before_pass=16` EXIT 1, and the filed-tool after arm (`c2-after-rerun.txt`)
  gives `tool_pass=20 before_pass=16` EXIT 0. The C2 claim needs no C1
  file to reach its target. Separability holds.

## 4. Axis naming

AXES.md: calibration is "self-assessment quality: gaps named honestly,
confidence graded, overreach caught — SCORECARD entries match observed repo
state"; coverage is "fraction of the domain's real surfaces the skill
governs (repo paths, tools, edge classes)"; operability is "runnable
artifacts: checklists that are executable, commands that exist, scripts that
run — a checklist item can be run and produces the stated outcome".

C1 — calibration. The object under test is not a domain surface; it is the
lane's own self-assessment counter (the frozen r87 pointer counter that
re-derives the lane's evidence-pointer claims). The gap it names — no r91
row asserts the success exit code, so a counter exiting 1 on success
survived — is overreach caught: the lane's self-assessment instrument
admitted a whole class of failures it could not see. Lane precedent
(SCORECARD): r25 C1 "coverage-map kill-rule tool row" (kill_tested=6,
kill_violations=0) is scored as calibration 7, and the same shape (a
kill-rule/battery binding of a self-assessment instrument) is what C1 does.
Coverage would be the mislabel here: AXES.md counts domain surfaces
(repo paths, tools, edge classes the skill governs), not the internal
mutation coverage of one counter; the counter is a self-assessment tool,
not a domain surface. "Quality" is not an AXES.md axis (it appears only in
LEARNING.md as the trend that operability/depth/freshness serve). The
prereg's axis (calibration 7, "the lane's lowest owned, non-retired axis")
matches both the definition and the lane's r25 precedent.

C2 — operability. The move is that the excerpt tool now runs and produces
its stated outcome: the excerpt's head is a prefix and its tail a suffix of
the tool's own whole rendering (KFF18, 29,700 payloads, unfaithful=0 vs 28).
What changes is a printed cell, not an audit verdict: the r87 K4 regression
still reads rows=12 mismatches=0, i.e. the record-agreement assessment is
unchanged. Calibration would require the self-assessment to change; it
does not. The fixture's KFF14-KFF18 cases test that the artifact's output
is faithful — operability ("produces the stated outcome"), not coverage
(no new domain surface is governed; the Utf8-window knowledge entry is
sourced from S355 but the claim adds no new surface, only a correct
rendering of the existing one). The r25 precedent even warns against
relabelling a coverage move as operability ("W2 reviewer found the move is
coverage of four edge classes, not operability; the frozen axis is not
relabeled"); C2 is the converse shape — a runnability/output-fidelity fix,
which is operability. The axis stands.

## Verdict

NO-FALSIFICATION. I tried: re-running both do-nothing controls (C1 via the
pristine r91-population harness arm, C2 via the both-arms fixture, each
matching the committed numbers); re-running the C1 after arm 41/47 and the
tail 6/6 (all killed=yes rc=1, zero survivors) plus the pristine r92
harness (rows=64 mismatches=0, LD4r rc=0 match=yes); re-running the C2
after arm, forgery probe, and K4 regression (all matching the frozen
predicates); and the static + restored-arm separability runs above. No
artifact of this seat falsifies any sentence of either claim as written.
The identified weakness is certifying power, not wording: C1's 47 is
derived from the row that kills them (openly stated in limit (vi)), so the
claim is reproducible-or-fail, not predictive. That is a tradeoff the
falsifiability analysis records, not a defect the canonical judge must
reject. No FALSIFIES-WORDING heading is warranted.

Tool installs: none. Scratch under /fast/scratch/hyaku/souji-r92/R92Critic/
deleted; receipts (text only) copied to .ufo/waves/round-92/w1/R92Critic/.

