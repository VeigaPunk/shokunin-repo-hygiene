# R40scribe16 — C1 calibration attack

## Explicit edge case: `commit_distinct` conflates row count with distinct commit identity

**Verdict: Concrete falsifier of the r39 C1 instrument's advertised field meaning; bounded support for the r40 strict-descendant predicate, not evidence that r40 satisfies it.**

### Evidence and commands actually run

1. Read `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt` first. Lines 4–5 freeze the C1 requirements: revision-bound evidence pointers and strict-descendant `commit` vs `receipt_rev`; forged token-only line remains open. No claim was changed.
2. Read committed R39 counter source `census/round-39/c1-counter.py` at lane revision `0242085909fb6a4ee041c5443d76316ac6d59d4b` (working lane HEAD reported as `be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e`). Relevant source lines 136–152: `parse_register` docstring says it returns row count and rows whose commit differs from receipt_rev; lines 187–259 consume/report this quantity. The counter's help confirms the option name `--min-commit-distinct`:

```text
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c1-counter.py --help
```

Observed: `--min-commit-distinct MIN_COMMIT_DISTINCT`.
3. Inspected the committed register with:

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 0242085909fb6a4ee041c5443d76316ac6d59d4b:census/round-39/cells.tsv
```

Observed six rows, all commit `a8e6d75b3183849129fca01f959dbe5a69cf066c`; five receipt revisions are `5230a3414d062152aa76f141ab45afb62bcfcc4c`, one is `f8ba3f3b4fdac9669182f8e` (full exact value in source is `f8ba3f3b4fdac9669182af1c2829d79c1658f314`).
4. Independently counted the committed TSV rows and identities:

```sh
python3 -B -c 'import csv,subprocess; p="/home/vgpnk/Projects/shokunin/souji-shokunin"; s=subprocess.check_output(["git","-C",p,"show","0242085909fb6a4ee041c5443d76316ac6d59d4b:census/round-39/cells.tsv"],text=True); r=list(csv.DictReader(s.splitlines(),delimiter="\t")); print("rows",len(r),"distinct commit hashes",len({x["commit"] for x in r}),"distinct receipt_rev hashes",len({x["receipt_rev"] for x in r}),"commit != receipt_rev rows",sum(x["commit"]!=x["receipt_rev"] for x in r)); print("unique commit/receipt_rev pairs",len({(x["commit"],x["receipt_rev"]) for x in r})); print("receipt_rev to commit pairs",sorted({(x["receipt_rev"],x["commit"]) for x in r}))'
```

Observed output: `rows 6 distinct commit hashes 1 distinct receipt_rev hashes 2 commit != receipt_rev rows 6`; `unique commit/receipt_rev pairs 2`. Thus the committed R39 receipt `census/round-39/records/c1-after.txt` lines 19–20 (`REGISTER cells=6 mismatches=0 commit_distinct=6`) reports a field value of 6 even though there is only one distinct commit hash. This is independently documented by the committed non-author spot-check `corpus/lessons/round-39-verifier-spotcheck.md` lines 44–52 and routed defect D3 at lines 147–150.

### Calibration implication / limits

This is a falsifier for interpreting the old `commit_distinct=6` / `--min-commit-distinct` as distinct commit identities: it counts differing rows, not distinct commits. It specifically motivates treating r40's strict-descendant relation as a per-register-row comparison and reporting row count separately from distinct commit identities (or naming the measure unambiguously). It does **not** falsify the frozen r40 goal, prove that an r40 implementation exists, or demonstrate the forged-token case: no r40 counter, fixture, or forged-token input was executed in this scoped attack. The R39 row data shows six `commit != receipt_rev` comparisons, but strict ancestry itself was not re-tested here. Those checks remain unrun, not pass.

### Scope / provenance

Read-only inspection of committed R39 artifacts; no production files, git/jj/index state, or fixtures were modified. No tests/counters were run beyond `--help` and the explicit data-count command above. No tools were installed.