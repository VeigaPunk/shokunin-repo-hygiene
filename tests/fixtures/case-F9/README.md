# case-F9 — origin/HEAD missing, single origin branch ref (D1 fallback)

Fixture for `tools/souji-verify.sh --selftest`. Exercises the D1 default-branch
fallback: a repo whose `refs/remotes/origin/HEAD` does not exist but which has
exactly one `refs/remotes/origin/*` ref, `refs/remotes/origin/master`.

## Target and expectation

| field | value |
| --- | --- |
| artifact | `repo/pushed-file.txt` |
| expected verdict | `SAFE` |
| expected receipt | `pushed` |
| verdict line | `VERDICT<TAB><case>/repo/pushed-file.txt<TAB>SAFE<TAB>pushed<TAB>...` |

## Repo shape (`repo/`, built by `build.sh`)

- `refs/remotes/origin/master` -> `7d8acd5c74164329b432b93ace772287afeb2374` (tip)
- `refs/heads/main` -> same tip; `HEAD` -> `refs/heads/main`; tree clean, 0 unpushed
- **no** `refs/remotes/origin/HEAD` — `git symbolic-ref --quiet --short
  refs/remotes/origin/HEAD` fails, so the primary D1 resolution returns nothing
- **no** `refs/heads/master` — the later fallback (local `master`) cannot
  rescue a resolver that skips the single-origin-ref fallback
- `pushed-file.txt` introduced by `f16d67eb723343d8a5f99a32a0aa188087919cf1`,
  an ancestor of `refs/remotes/origin/master`
- no remote is configured; the checks must work off existing refs only (the
  spec forbids `git fetch`)

## Resolution the tool must implement

1. `git symbolic-ref --quiet --short refs/remotes/origin/HEAD` -> empty
   (origin/HEAD is absent);
2. fallback: exactly one ref matches `refs/remotes/origin/*`
   (`refs/remotes/origin/master`), so the default branch is `master` and the
   default-branch ref for ancestry is `refs/remotes/origin/master`;
3. introducing commit of `pushed-file.txt` is an ancestor of that ref
   -> receipt `pushed` -> `SAFE(pushed)`.

A resolver limited to step 1 lands on `NOT-SAFE(pushed-unverifiable)` (step 1
empty, `refs/heads/master` absent) and the selftest must FAIL on this case —
that is the D1 regression this fixture exists to catch.

## Rebuild

```
bash build.sh [dest-dir]     # default dest = this case directory
```

The builder is deterministic (fixed identities/dates, no user or system git
config, no hooks, no reflogs); re-running reproduces the same SHAs. It uses
only plumbing (`init`, `add`, `write-tree`, `commit-tree`, `update-ref`) —
never `git fetch/push/commit/branch/checkout/reset/rebase` — and asserts the
fixture invariants above, exiting non-zero if any fails.

NOTE for enclosing-repo integration: `repo/` contains a live `.git`, which a
parent repo cannot track as plain files (git would record a dangling gitlink).
If that matters, track only `build.sh`/`expected.json`/`README.md` and
materialize the repo with `bash build.sh <mktemp-dir>`.
