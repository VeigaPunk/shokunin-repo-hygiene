# R40w2reviewer03 — C1 exit-code contract

Attacked the landed C1 counter at commit `128e412b0ced3c243dc27c3dd3332054a611bc2e` (invocation at `census/round-40/c1-counter.py:263-358`; usage/evaluation classifications at lines 265-299 and 320-325; argument parsing at 346-358; item parsing at 119-155; register parsing at 158-176). Commands below ran against committed counter bytes with Python `-B`; root was the lane. `REV=128e412b0ced3c243dc27c3dd3332054a611bc2e`; baseline `ITEM=census/round-40/records/c1-control.txt`, `REG=census/round-39/cells.tsv`. Scratch `S=/fast/scratch/hyaku/souji-r40/w2/R40w2reviewer03`, explicitly passed as `--scratch` and `TMPDIR`, removed by EXIT trap.

## Real command outputs

Each command used `python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <value> --items <value> --register <value> --scratch /fast/scratch/hyaku/souji-r40/w2/R40w2reviewer03`.

* unresolvable `--rev 0000000000000000000000000000000000000000`: `REFUSAL COULD-NOT-EVALUATE: --rev 0000000000000000000000000000000000000000 does not resolve to a commit`; exit 2.
* blob `--rev 1a9d8c951078bc7d9b60ff12580a949dc8a5994f` (obtained by `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse 128e412b0ced3c243dc27c3dd3332054a611bc2e:census/round-40/c1-counter.py`): same COULD-NOT-EVALUATE class, `--rev ... does not resolve to a commit`; exit 2.
* malformed items: `printf 'malformed\\n' > /fast/scratch/hyaku/souji-r40/w2/R40w2reviewer03/bad-items`, then override `--items` with that path. Output `REFUSAL USAGE: items /fast/scratch/hyaku/souji-r40/w2/R40w2reviewer03/bad-items has no header before line 1`; exit 2.
* malformed register: override `--register /fast/scratch/hyaku/souji-r40/w2/R40w2reviewer03/bad-register`, whose bytes were `bad\\n`. Output `REFUSAL USAGE: items /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/records/c1-control.txt has no header before line 5`; exit 2. This is a concrete defect: malformed register is routed through `parse_items` on baseline items at `c1-counter.py:281-290`; the register parser at 158-176 is never reached. It is mislabeled USAGE and reports the wrong input file.
* unknown evidence revision: custom one-row items, evidence `LOG.md@0000000000000000000000000000000000000000`. Output `ITEM X OPEN EVIDENCE-REV-UNRESOLVED 0000000000000000000000000000000000000000`, then `REGISTER cells=6 mismatches=0 commit_rows=6 commit_hashes=1 violations=0 ok`, summary with `items=1 open=1`; exit 1 (no REFUSAL).
* missing evidence path: custom one-row items, evidence `missing-evidence@128e412b0ced3c243dc27c3dd3332054a611bc2e`. Output `ITEM X OPEN EVIDENCE-PATH-ABSENT missing-evidence@128e412b0ced3c243dc27c3dd3332054a611bc2e`, same register line, summary `items=1 open=1`; exit 1 (no REFUSAL).

## Verdict

FALSIFIED for malformed-register classification/diagnostics: exit 2 is emitted as `REFUSAL USAGE`, but the attempted register is not identified; the counter parses the *items* file twice, never validates malformed register bytes (lines 281-290), despite the expected register parse implementation (158-176). Usage error is distinguishable textually from COULD-NOT-EVALUATE in the normal preflight cases (lines 265-299), although both use exit code 2; hence exit status alone does not distinguish them. Unknown evidence revision and missing evidence path are ordinary evaluation failures, not refusal classes: item OPEN and exit 1. The run therefore distinguishes them from usage and could-not-evaluate by output class and status.

Scratch directory removed by the EXIT trap. No tools installed. No verification beyond the reported runs.
