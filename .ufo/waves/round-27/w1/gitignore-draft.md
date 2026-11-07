# .gitignore hygiene draft — souji-shokunin (round 27, w1)

State verified at lane HEAD `e78ac7c` (base):
- `tools/__pycache__/` and `tests/fixtures/__pycache__/` — untracked (`??` in `git status --porcelain`).
- `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc` — **tracked** (committed at e879ba0, round-10); sole `git ls-files` match for `__pycache__`.
- `.gitignore` — does not exist at lane root; file must be created (not appended to).

Exact two lines to append (create `.gitignore` at lane root with these):

```
__pycache__/
*.pyc
```

Caveat: gitignore applies only to untracked files; the committed `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc` will remain tracked until untracked via `git rm --cached` (outside this read-only seat) — the pattern does not hide it post-hoc.
