## Status
STATUS: PARTIAL — draft delivered (w1/gitignore-draft.md), but the assignment's stated check "no tracked file matches `__pycache__`" FAILS: `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc` is tracked (commit e879ba0); the other two `__pycache__/` dirs are untracked.

## Evidence
- `git -C souji-shokunin ls-files | grep __pycache__` → `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc` (1 match; tracked total 4462). Revision: lane HEAD `e78ac7c4837b81b634db4a927605a751a7f006ba` (base, matches contract).
- `git ls-files --error-unmatch census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc` → succeeds (tracked). `git log -1 -- <that file>` → `e879ba0 round-10: REJECTED on O1 ...`.
- `git status --porcelain | grep -i pycache` → `?? tests/fixtures/__pycache__/` and `?? tools/__pycache__/` (census absent → tracked, clean).
- `ls -A` confirms each dir has one `.cpython-314.pyc`; `read` of `souji-shokunin/.gitignore` → "Path not found" (no .gitignore exists).

## Findings
1. One tracked file matches the proposed pattern: `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc`, committed at e879ba0 (round-10 merge). `git ls-files | grep __pycache__` is NOT empty, so the assignment's confirmation criterion is falsified.
2. `tools/__pycache__/` and `tests/fixtures/__pycache__/` are untracked — the other two of the three dirs check out.
3. `.gitignore` is absent at the lane root; "append" = create with the two lines.
4. Gitignore does not untrack already-tracked files; hiding the census pyc requires `git rm --cached` (outside read-only seat; not performed).

## Attack log
The sub-task premise ("confirming no tracked file matches the pattern") is contradicted by data at base: a tracked `__pycache__` file exists. Not a countable counter in the frozen C1/C2/C3 set — flagged as an assignment premise correction, not a gameable target. No counter/predicate changes proposed.
