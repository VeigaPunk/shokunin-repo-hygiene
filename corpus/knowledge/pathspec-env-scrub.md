source: S304 (git(1), https://git-scm.com/docs/git, OPTIONS dt --literal-pathspecs, page "git last updated in 2.56.0", sha256 534c674f…f9d1, accessed 2026-11-06); S296 (gitglossary(7) magic word `top`, the reader side); host probe census/round-70/probes/lp-ls-files-probe.txt (git 2.56.0); controls census/round-70/controls/c1-do-nothing.txt; counter census/round-70/c1-counter.py frozen at 0243af04bbcd422302b4efc3473612073c9aa962
verified-at: 93a051b2c936ff6eafca8e8b31d918e3d20fd3da (writer candidate; 2026-11-06, git 2.56.0 on this host)
recheck: `python3 -B census/round-70/c1-counter.py --root . --matrix census/round-70/c1-matrix.tsv --base-rev e063a2fcb3f5f3fb8fb19d2ae1592b1f22e6a333 --rev <tip> --tool tools/souji-receipt-write.py --work <scratch>` must print `SUMMARY matrix=59 base_forgeries=4 base_honest=13 new_forgeries=0 new_honest=15 class_mismatches=0 new_echo=0 errors=0 regress=PASS` and `EXIT=0` (census/round-70/records/c1-after.txt); on every git release, re-run the probe and re-fetch S304 against its sha256

# A caller's pathspec variables can empty a read-only safety check

git(1) documents four global pathspec switches, each with an environment equivalent:
`--literal-pathspecs` ("no globbing, no pathspec magic"; `GIT_LITERAL_PATHSPECS=1`), `--glob-pathspecs`,
`--noglob-pathspecs` and `--icase-pathspecs` (S304). A cleanup or receipt tool that reads the index
through a pathspec inherits whichever of them the caller exported.

| variable set by the caller | effect on the receipt writer before round 70 (git 2.56.0) | verdict class |
|---|---|---|
| `GIT_LITERAL_PATHSPECS=1` | `:(top)` (S296's `top` magic) is read as a literal path because the variable removes all pathspec magic (S304); `git ls-files -v -z ':(top)'` prints nothing (probe), the base writer goes on (`base_rc=0` on LD, `controls/c1-do-nothing.txt`), every index-flag check over the empty output passes, and receipts were written over skip-worktree, subdirectory-scope, gitlink and absent rows (LD LN4 LG1 LA9) | forgery (4 rows) |
| `GIT_LITERAL_PATHSPECS=1`, unmerged entry | the flag read is empty, but the dirty check still refuses (LU1) | right verdict, wrong class |
| `GIT_GLOB_PATHSPECS=1` or `GIT_ICASE_PATHSPECS=1` | `git ls-tree -- <path>` fails ("pathspec magic not supported by this command"), so an honest clean tree is refused (GA, ICA) | over-refusal (2 rows) |
| `GIT_NOGLOB_PATHSPECS=1` | no verdict changed on the 59-row matrix | — |

Rule (writer, round 70): scrub all four variables from the environment of the writer's `git()` helper (every git call on the receipt path; the selftest's own fixture calls do not go through it),
and leave them in the wrapped command's environment. Two partial designs fail the frozen matrix:
refusing whenever a variable is present over-refuses the four honest rows (control F1,
`new_honest=11`), and scrubbing only `GIT_LITERAL_PATHSPECS` leaves the GLOB/ICASE over-refusals
(control F2, `new_honest=13`).

General lesson for this domain: an empty result from a pathspec-limited read is not evidence of "no
entries" when the caller controls the environment. A tool that decides "safe to delete" or "clean"
from such a read must pin the pathspec semantics (scrub the four variables from its own git calls)
before trusting an empty answer.

## What this does not cover

- Per-pattern magic (`:(attr)`, `:(exclude)`) and its own environment inputs (for example
  `GIT_ATTR_SOURCE`); only the four global switches are measured.
- git releases other than 2.56.0; the probe must be re-run on upgrade.
- The `GIT_NOGLOB_PATHSPECS` scrub is not measured: no matrix row changes its verdict with or
  without it (wave S70MutWriter mutant W3 survived the frozen matrix and the writer selftest), so
  its presence in the scrub is a design choice, not an observed protection.
