source: S275 — git(1) manual, environment variables, GIT_OPTIONAL_LOCKS (https://git-scm.com/docs/git; anchor ENVIRONMENT, GIT_OPTIONAL_LOCKS; opened 2026-11-03); the census tool tools/souji-fleet-root-census.py
verified-at: 2026-11-03 — capture census/round-52/records/fleet-root-census.tsv (ENTRIES=49, FLEET_HEAD e56cdb33…, TOOL_SHA256 e7e79952…; run receipt census/round-52/records/fleet-root-census-run.txt); tool selftest census/round-52/records/tool-selftest.txt (checks=39 failures=0)
recheck: python3 -B census/round-52/c2-counter.py --root <lane> --rev <full40> (the committed capture verifies: SUMMARY ... receipt=ok, exit 0); python3 -B tools/souji-fleet-root-census.py --selftest

# Fleet-root stray census (read-only, dry-run)

## What it measures

The top-level entries of the fleet root (dotfiles included, `.git` excluded). One row per entry:
name, kind (file | dir | symlink | other, from lstat), tracked, ignored, class, disposition.
The capture is one TSV written outside the root with O_EXCL. Nothing is removed, moved or
proposed for removal; an untracked stray gets the disposition `report-only`.

## The frozen class rule

Copied from `census/round-52/preregistration.txt`, C2 format block (first match wins):
kind=symlink -> symlink; tracked=yes -> tracked; ignored=yes -> ignored; otherwise untracked-stray.
Disposition: `report-only` for untracked-stray; `none` otherwise; no other disposition is permitted.

`tracked` is set when the first path component of any path in `git ls-files --cached` equals
the name. `ignored` is set when `git check-ignore --no-index` on the top-level name reports it
(see the derivation limit below).

## Why every git call sets GIT_OPTIONAL_LOCKS=0

S275 quotes the git manual: "If this Boolean environment variable is set to false, Git will
complete any requested operation without performing any optional sub-operations that require
taking a lock." The census sets the variable to `0`, the same boolean false, on every git call
so that a read-only capture does not take optional locks in the fleet repository. The manual's
own example is `git status` (index refresh); applying the variable to `ls-files` and
`check-ignore` is the lane's reading, not a sentence the manual makes about those commands.
The variable's value `0` is the lane's spelling of the boolean false the quote names; the
spelling itself was not separately located.

## Derivation of `ignored` (named limit, measured)

Round 52 measured two derivations on the same root. (A) a listing of
`git ls-files --others --ignored --exclude-standard --directory` walks into ignored untracked
subtrees, including the operator-protected `.ufo/state/`. (B) `git check-ignore --no-index`
on each top-level name enumerates nothing below the top level. The two disagree on three rows
(`.jj`, `.ruff_cache`, `kumitate-shokinin`). The tool uses (B) so that no protected subtree is
walked. The frozen predicate fixes the class rule over the `ignored` column, not its derivation,
so the capture is bound to the committed tool bytes (TOOL_SHA256), not to a derivation.

## Refusals (exit 2, nothing written)

- fleet-root is a symlink, not a directory, or not its own repository top-level;
- the root lies inside a credential namespace (`~/.omp`, `~/.ssh`, `~/.gnupg`, `~/.aws`,
  `~/.kube`, `~/.docker`, `~/.config/gh`), resolved through the passwd home;
- the repository config carries an `include.*` / `includeIf.*` directive or sets
  `core.worktree` (either can make git read outside the root or walk another tree);
- a top-level name is credential-shaped (`.env*`, `creds`, `credential*`, `secret*`,
  `password*`, `token*`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.kdbx`, `id_rsa`-family,
  `.ssh`, `.gnupg`, `.aws`, `.netrc`, `.kube`, `.docker`); the whole run is refused, so names
  are never printed for such a root (operator ruling pending, see the lesson's Gate);
- `--out` resolves inside the fleet root;
- an entry name contains a tab or newline;
- a git call fails or exceeds its timeout (the whole process group is killed).

Every git call runs with `-c core.fsmonitor=false -c core.hooksPath=/dev/null
-c core.excludesFile=/dev/null` and the frozen GIT_* environment, so repository-local
fsmonitor and hook programs are not executed. The selftest plants a repository-local
fsmonitor and checks that its marker file is not written (`census/round-52/records/discrimination-s1.txt`
shows the same check failing on the pre-hardening candidate).

## What it does not measure

- nested files: only top-level entries are enumerated;
- the race between the directory scan and the git reads: the capture is one point in time;
- FLEET_HEAD resolution: the counter checks its format, not that the fleet repository holds it;
- whether a capture was produced by a run: the counter binds the capture to the committed tool
  bytes and the grammar; a hand-written capture with the right bytes still verifies (round-52
  critic probe). The run receipt `census/round-52/records/fleet-root-census-run.txt` is the
  provenance for this capture;
- the names' sensitivity beyond the refusal rule: names are printed as-is for roots that pass it.

## Limits

- The frozen counter (`census/round-52/c2-counter.py`) checks the sort order of rows not at all;
  rows in reversed order verify (critic probe).
- A `#`-leading data row is read as a comment by the counter (reviewer probe T7b).
- The census is a dry run. Any removal of a flagged entry is an operator decision with its own
  receipt, not a consequence of this entry.
