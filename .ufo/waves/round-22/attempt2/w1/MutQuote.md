STATUS: PASS

# MutQuote — C2 gate-check mutation probe (souji round 22, attempt 2)

Full transcript: `.ufo/waves/round-22/attempt2/w1/evidence/MutQuote.md`.

## Subject and detector

- Subject: `tools/souji-gate-check.py`, sha256
  `d85c269624f4ade5c4ce5a1328c33e7a8f5169c9c14ec71f7f62f74612486b00`, working
  tree clean (`git status --porcelain -- tools/` empty).
- Tasking named `.ufo/waves/round-22/attempt2/w1/evidence/impl-gate/souji-gate-check.py`
  as the copy source; that directory **does not exist** (checked twice, minutes
  apart). I copied the committed counter at the lane root instead and recorded the
  hash, so the probe is pinned to identifiable bytes either way.
- Detector: the frozen fixture set, `python3 -B <file> --selftest`
  (preregistration C2 kill rule, fixtures 1-7 + always-green control).
- Baseline on the unmutated copy: `selftest=9/9`, rc=0 — the fixtures themselves
  pass, so mutant red lines are attributable.

## Results (one mutation per run, each in its own isolated copy)

| Mutant | sha256 (prefix) | Expected kill | Observed | Verdict |
|---|---|---|---|---|
| M1 check 4 = substring-of-anything (`squash(q) not in squash(q)`) | `09410e61…` | fixture `quote-absent` | `FAIL fixture quote-absent [entries=1 ok=1 … fail=0]`, `selftest=8/9`, rc=1 | KILLED |
| M2 check 6 accepts zero REJECT rows (`and False`) | `f3917cf4…` | fixture `no-reject` | `FAIL fixture no-reject [entries=1 ok=1 … fail=0]`, `selftest=8/9`, rc=1 | KILLED |
| M3 missing verdict row counted as verified (`verified = len(ids)`, missing-row failure removed) | `efa5bb79…` | fixture `partial-verdicts` | `FAIL fixture partial-verdicts [entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0]`, `selftest=8/9`, rc=1 | KILLED |

Survivors: none — so no fixture is owed for a survivor.

M3 detail worth carrying: the mutant's inner `run()` returned rc=0 with
`slice_verdicts=2 slice_total=2 fail=0` on the partial TSV, i.e. the counter's own
output would have been reported as green. The kill comes from the fixture harness
asserting `slice_verdicts=1` and rc=1. That is the intended construction — the
harness, not the counter's exit status, is the detector.

## Restoration evidence

The lane repo and `tools/souji-gate-check.py` were never written. Post-probe:
`sha256sum tools/souji-gate-check.py` = `d85c2696…` (unchanged), its own
`--selftest` = `9/9`, rc=0, and `git status --porcelain -- tools/` empty. The three
mutant copies and the pristine copy were deleted after this report and the evidence
file were written; `evidence/mutquote-work/` was removed.

## Bounded finding (coverage, source-inferred)

[INFERENCE] The frozen fixture set has no case isolating `check4-snapshot-outside-dir`,
`check4-snapshot-missing`, `check4-no-snapshot-named`, `check3-no-locator`, or
`check6-reject-without-reason`, and every fixture supplies exactly one entry
(`entries=1`). Mutating those branches alone would leave all 9 fixture lines green.
Not a survivor of this probe and not a change to any frozen predicate: a candidate
for a later fixture-set revision if those branches are load-bearing for C2.

## Non-actions

No installs/upgrades (nothing to record under the tooling directive). No git/jj
writes, no commits, no index or `.ufo/state` writes, no process signalling, no
deletion authority, no writes outside the evidence directory and this report.
