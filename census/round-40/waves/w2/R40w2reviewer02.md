# R40w2reviewer02 — C1 strict-descendant falsification

Attack target: `census/round-40/c1-counter.py`, `register_leg` (lines 179–235; equal check line 221, descendant predicate line 225, audited-rev check line 229). Frozen claim: `census/round-40/preregistration.txt:5` requires strict-descendant `commit` relative to `receipt_rev`.

## Evidence and commands

The committed instrument was inspected at landed revision `128e412b0ced3c243dc27c3dd3332054a611bc2e`; its code checks `commit == receipt_rev` at line 221, then `is_ancestor(root, receipt_rev, commit)` at line 225, then separately verifies `is_ancestor(root, commit, rev)` at line 229. The committed fixture builds a planted receipt and explicitly includes equal and backwards rows (`tests/fixtures/r40-c1-evidence.py:77–99`); its assertions test rejection at lines 177–189.

Exact attempted run:

```sh
S=/fast/scratch/hyaku/souji-r40/w2/R40w2reviewer02; mkdir -p "$S"; trap 'rm -rf -- "$S"' EXIT; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 128e412b0ced3c243dc27c3dd3332054a611bc2e:tests/fixtures/r40-c1-evidence.py > "$S/fixture.py"; python3 "$S/fixture.py" --counter /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/c1-counter.py --work "$S/work"
```

Real output:

```text
usage: unreadable counter /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/c1-counter.py / /fast/scratch/hyaku/souji-r40/census/round-39/c1-counter.py

Command exited with code 2
```

The fixture’s default base-counter path is derived from its `--work` layout; the attempted invocation did not provide a readable base counter. Consequently no requested equal/ancestor/reverse-direction rows were evaluated by running the counter against scratch data. The reverse-direction case (strict descendant of receipt but not ancestor of `--rev`) is directly rejected by the code at line 229 as `REGISTER ... NOT-ANCESTOR-OF-REV` and counted as a violation at line 235; equal and older-than-receipt are reported as `REGISTER ... BACKWARDS ...` at lines 221 and 225 respectively.

## Verdict

INCONCLUSIVE for the requested executed scratch attack: the committed fixture could not start because its base-counter prerequisite was unreadable, and I did not obtain actual class/output for each case. Source inspection predicts equal and ancestor-of-receipt failures as `BACKWARDS`, and a strict-descendant but non-ancestor-of-audit-rev as `NOT-ANCESTOR-OF-REV`; this is not substituted for the requested runtime evidence. No tool installs. Scratch directory removed by the registered EXIT trap.