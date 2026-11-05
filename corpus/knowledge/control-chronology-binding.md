source: S290 — git-log(1) path-limited history (https://git-scm.com/docs/git-log, DESCRIPTION; accessed 2026-11-05; located quote in `corpus/SOURCES.md` S290 row); S251 — git-merge-base(1) `--is-ancestor` exit contract (`knowledge/git-strict-descendant-relation-r40.md`)
verified-at: 2026-11-05 (round 61; instrument `census/round-61/c1-counter.py` at freeze `9849e71851e28d5f1e88ef658418d3c136f94692`)
recheck: `python3 -B census/round-61/c1-counter.py --root . --matrix census/round-61/c1-matrix.tsv --base-tool-rev c7228424c3919ecf142bab1aec8181722d86467b --rev 9849e71851e28d5f1e88ef658418d3c136f94692 --work DIR --new-tool tools/souji-freeze-check.py` must print `new_forgeries=0 new_honest=4 class_mismatches=0 stubs=REJECTED` and exit 0

# A control receipt's bytes must already exist at a strict ancestor of the freeze

ground: F1 — git-native housekeeping vs receipts (the chronology a frozen claim's `Control:` receipt must have before its red exit can be read as prefreeze evidence; extends `knowledge/freeze-record-substance-binding.md`)

## Claim

QUALITY Q120 requires a successor claim's executed controls to be committed strictly before its predicate
freeze. The round-60 substance arm bound the revision a receipt NAMES (`rev=`) but not when the receipt
FILE's bytes entered history. The r60 critic found both control receipts added by the freeze commit itself
(`census/round-60/wave/w1/S60CriticRound/S60CriticRound.md`, Finding 1); the r60 arm scored that record clean.

## Rule (round 61, `--substance` only)

For each claim whose `Control:` receipt is present at freeze, not a symlink, and red there: the receipt's
blob at FREEZE must equal the blob at some commit in `git rev-list --no-renames --full-history <parents of
FREEZE> -- <receipt path>`. Otherwise the class is `CONTROL-ADDED-NOT-BEFORE-FREEZE`.

Why content and not the adding commit: an add-commit rule (`git log --diff-filter=A ... | tail -1`) sees
only the first green add. A receipt added green in an ancestor and rewritten red at the freeze commit is
accepted by that rule (matrix row `rewritten-at-freeze`: base and add-commit candidate both accept it; the
content rule refuses it). A receipt deleted and re-added at freeze with new bytes is refused for the same
reason; re-added with bytes that already existed before freeze is accepted, correctly.

## Measured (round 61)

- Frozen 12-case matrix, `census/round-61/records/c1-after.txt`: base `new_forgeries=2` (`chrono-at-freeze`,
  `rewritten-at-freeze`), candidate `new_forgeries=0 new_honest=4 class_mismatches=0`.
- Real record, `census/round-61/records/real-r60-prereg-candidate.txt`: `CONTROL-ADDED-NOT-BEFORE-FREEZE` on
  both r60 control receipts (base `findings=0`, `real-r60-prereg-base.txt`).
- Lane history sweep (`census/round-61/records/`, base vs candidate, full-40 revision): the candidate only adds
  findings; it never removes one. Round 60 flips pass to fail. Rounds 41–55 were already red at base and gain the
  same class on their control receipts, so the defect is not confined to round 60.

## What this does not prove

- Bytes are not execution: a receipt committed before freeze may still be fabricated. The rule proves ORDER of
  the receipt's bytes against the freeze, not that a command produced them (round-57 recorder doctrine).
- History simplification: a commit that dropped a path can hide an ancestor; the check then refuses (fail closed).
- The `rev=` binding (`CONTROL-REV-NOT-BEFORE-FREEZE`) and the instrument digest are separate checks, unchanged.
