# corpus/README.md coverage-map row — round 42 C3 ground (seat R42scribe07, draft only)

Placement: the L1 appends this as a row of a three-column coverage table under a new `## Round 42 frontier update` section, after the `## Round 41 frontier update` bullets (`corpus/README.md:806`), following the precedent of the r17 table at `corpus/README.md:214-217`. Header to use (same as `corpus/README.md:214` and `:515`):

| ground | status | entries / runnable evidence |
|---|---|---|

Row (one line in the file):

| F1 git-native housekeeping vs receipts: worktree-drift tool, condition-level coverage (r42 C3: the refusal, containment, discovery, write and exit conditions of `tools/souji-worktree-drift.py` observed by a fixture, tool behaviour not bytes) | frontier, unchanged: a runnable condition battery and its counter, no knowledge entry added, no entry un-grounded; F1 stays frontier, expansion is unchanged, nothing is promoted to Core; the claim is coverage of the tool's behaviour at the pinned bytes (sha256 `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6`), not of the frontier | `../tests/fixtures/r42-drift-conditions.py`; `../census/round-42/c3-counter.py`; `../census/round-42/c3-mutants.tsv`; `../census/round-42/controls/c3-control.txt`; `../tools/souji-worktree-drift.py` |

Notes for the L1:

- The ground cell starts with the token `F1`, so Q56 reads it as an F1 row. The row names no `knowledge/` path, so the Q56 entries check (every grounded `corpus/knowledge/*.md` entry named in an F1 row) is unchanged; the F1 row at `corpus/README.md:39` already names `docstring-class-continuation-lines-r40` and `drift-record-invalid-utf8-r40`.
- Q31 resolves `../`-relative tokens at the landing revision. The row must land in the same commit as `tests/fixtures/r42-drift-conditions.py` and `census/round-42/c3-counter.py` (both exist at the freeze tip only as the counter; the fixture is the C3 candidate). If the C3 claim misses, do not land this row: it describes a battery that did not earn its target.
- The status cell says "frontier, unchanged"; it does not say "held" or "Core", which the F1 row at `corpus/README.md:39` uses for entries. A coverage row for a runnable battery is not an entry.
- Do not add the row to the F1 ground row at `corpus/README.md:39` (that row's entries column is the knowledge-entry list the Q56 check reads).
