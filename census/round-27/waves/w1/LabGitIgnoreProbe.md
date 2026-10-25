# LabGitIgnoreProbe — round 27 w1 (gitignore probe)

## Status
STATUS: PARTIAL — probe executed end-to-end; rule mechanics verified in a mirror repo; the assignment's lane criterion "no tracked lane file matches `__pycache__` (count → 0)" is FALSIFIED by lane data: count = 1. Read-only seat: no lane writes (only this report).

## Evidence
Lane (read-only; HEAD `e78ac7c4837b81b634db4a927605a751a7f006ba`):
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-files | grep -c '__pycache__'` → `1`.
- Sole match: `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc` (tracked; `git ls-files` lists it; draft says committed at e879ba0).
- `git ls-files tools/__pycache__ tests/fixtures/__pycache__` → empty (both dirs fully untracked).
- Dir contents: `tools/__pycache__` → souji-axis-check.cpython-314.pyc, souji-gate-check.cpython-314.pyc; `tests/fixtures/__pycache__` → r26-axis-check.cpython-314.pyc; `census/round-10/__pycache__` → S13-candidate-battery.cpython-314.pyc.
- Lane `.gitignore` absent (`read` → "Path not found"); must be created, not appended.

Mini-repo mirror (`/var/tmp/souji-r27-LabGitIgnoreProbe/mini`, git init; `rev-parse --show-toplevel` printed the repo before first commit):
- Before rule: `git status --porcelain` → `?? app/__pycache__/`, `?? notes.txt`, `?? tests/`, `?? tools/`; `git ls-files` → `app/main.py`, `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc` (tracked, mirrors lane).
- Wrote `.gitignore` (bytes `__pycache__/\n*.pyc\n`; od -c confirms 23 octal = 19 bytes).
- After rule: `git status --porcelain` → only `?? .gitignore`, `?? notes.txt` (all pycache entries hidden; `grep -c '__pycache__'` on status → 0); `git ls-files` unchanged (`grep -c '__pycache__'` → 1, tracked unaffected).
- `git check-ignore -v` → rule `__pycache__/` (line 1) matches `app/__pycache__/main.cpython-314.pyc`, `tools/__pycache__/tool.cpython-314.pyc`, `tests/fixtures/__pycache__/fixture.cpython-314.pyc` (rc 0); `notes.txt` not ignored (rc 1).

## Findings
1. Rule mechanics verified: `__pycache__/` hides untracked pycache dirs at any depth; `*.pyc` additionally covers loose pyc; non-pycache untracked files stay visible; tracked files are unaffected (ls-files unchanged). Source of rule bytes: `.ufo/waves/round-27/w1/gitignore-draft.md` lines 11–12.
2. Lane criterion falsified: `ls-files | grep -c '__pycache__'` = 1, not 0. The tracked `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc` matches the pattern; gitignore does not untrack committed files (status stays clean for it regardless). Hiding it requires `git rm --cached` (outside this read-only seat).
3. "Three real dirs clean" holds by two mechanisms: `tools/__pycache__/` and `tests/fixtures/__pycache__/` (zero tracked files) become ignored by the rule; `census/round-10/__pycache__/` is clean because tracked. Draft's line-15 caveat is correct.
4. No lane `.gitignore` exists; the two-line draft is complete and sufficient for the untracked dirs.

## Attack log
None (probe item, not an attack). Premise correction corroborates w1/ExecPycacheFix.md: the "no tracked file matches" check cannot pass at base without untracking the census pyc.
