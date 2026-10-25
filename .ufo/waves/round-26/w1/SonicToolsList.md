# SonicToolsList — r26 w1: tools/ and tests/fixtures/ axis listing + counts

## Status

STATUS: PASS — at pin `89e0fceeefcf28db313c94120be6d25e03c60094` there are **0** `*axis*` entries in `tools/` and `tests/fixtures/`; pinned counts are **tools=134, fixtures=52** (fixtures 51 by plain `ls`, see F3). The working tree carries **2** axis files, both added by round-26 C3 after the pin. Two incidental hygiene defects found and left untouched (read-only seat): unignored `__pycache__` in both directories (F4), and `ls | wc -l` as a census instrument (F3).

## Evidence

E1 — contract read first. `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/preregistration.txt` read in full (218 lines); pin commit is amendment 1:

```
$ git log -1 --format='%h %ad %s' --date=iso 89e0fce
89e0fce 2026-10-25 14:04:30 -0300 round-26: prereg amendment 1 (C2 K4 literal corrected to base-derived grounded=7/kill_tested=7) + red-before receipts
```

Prereg `## MACHINE BLOCK` (line 7) is the section `tools/souji-axis-check.py` parses; C3 artifact names are at lines 157 and 177.

E2 — `*axis*` match + counts at the pin (immutable; `git ls-tree` against the commit, not the working tree):

```
$ git ls-tree --name-only 89e0fce tools/ tests/fixtures/ | grep -ic axis
0
$ git ls-tree --name-only 89e0fce tools/ | grep -i axis            # no output
$ git ls-tree --name-only 89e0fce tests/fixtures/ | grep -i axis   # no output
$ git ls-tree --name-only 89e0fce tools/ | wc -l
134
$ git ls-tree --name-only 89e0fce tests/fixtures/ | wc -l
52
$ git ls-tree 89e0fce tools/ | awk '{print $2}' | sort | uniq -c
    134 blob
$ git ls-tree --name-only 89e0fce tests/fixtures/ | while read -r p; do git cat-file -t 89e0fce:"$p"; done | sort | uniq -c
     39 blob
     13 tree
```

E3 — working tree at the same instant as the counts (`2026-10-25T17:35:59Z`, HEAD `0c92c2e6fbe1` = master tip):

```
$ ls tools | wc -l
136
$ ls tests/fixtures | wc -l
53
$ find tools tests/fixtures -maxdepth 1 -iname '*axis*'
tools/souji-axis-check.py
tests/fixtures/r26-axis-check.py
$ git ls-tree --name-only HEAD tools/ | wc -l          # 135
$ git ls-tree --name-only HEAD tests/fixtures/ | wc -l # 53
$ git diff --name-status 89e0fce HEAD -- tools/ tests/fixtures/
A	tools/souji-axis-check.py
A	tests/fixtures/r26-axis-check.py
```

E4 — context:

```
$ git log --oneline -3
0c92c2e round-26 C3 receipts: c3-before (absent@base) / c3-after (claims=3 flags=0, fixture cases=12 pass=12 FALSE-GREEN-REJECTED, verify ok); obsolete c3-control.tsv removed (control now integrated as fixture case 12)
c594901 round-26 C3: R4 per frozen contract (raw-block scan, only when enumerate absent); adopt wave 12-case fixture (cases=12 pass=12 control=FALSE-GREEN-REJECTED); counter adds fixture arm
ba8b54b round-26 C1: c1-after regenerated at fix tip 07f83e6 (markers=0, headings=17 44 78)
```

Invocations used no tool installs, no scratch repo (no `/var/tmp/souji-r26-SonicToolsList/` was created), no writes outside this report.

## Findings

1. **Axis glob at the pin is empty, as expected.** `tools/` and `tests/fixtures/` at `89e0fce` contain zero paths matching `axis` (case-sensitive and `-i` both 0). Location: trees `tools/`, `tests/fixtures/` at `89e0fceeefcf28db313c94120be6d25e03c60094`.
2. **"Expect none" is a pin-time property only; the working tree shows two.** `tools/souji-axis-check.py` and `tests/fixtures/r26-axis-check.py` were both added after the pin by round-26 C3 (first touched in `0833de9`, refined in `c594901`/`0c92c2e`). They are exactly the two artifacts the frozen prereg names at `.ufo/waves/round-26/preregistration.txt:157` and `:177`. A reviewer grepping the live tree will see 2, not 0 — the two statements are compatible only when the revision is named.
3. **`ls <dir> | wc -l` is an unsound census instrument.** It is dotfile-blind and directory-blind. `tools/` has 134 blobs and no dotfiles (134 either way), but `tests/fixtures/` has 52 tree entries of which 13 are directories and 1 is the dotfile `.gitignore` — a clean checkout of the pin would print **51**, not 52. In the live tree the errors cancel (52 visible tracked + 1 `__pycache__` = 53). Location: `tests/fixtures/` at the pin. Use `git ls-tree --name-only <rev> <dir> | wc -l` for any count that will be scored.
4. **Hygiene defect: unignored Python bytecode inside both scored directories.** `tools/__pycache__/souji-axis-check.cpython-314.pyc` (8951 B, Oct 25 14:25) and `tests/fixtures/__pycache__/r26-axis-check.cpython-314.pyc` (9615 B, Oct 25 14:26) are untracked and reported by `git status` (not `!!`), because `git check-ignore` returns exit 1 and the repo has **no root `.gitignore`** (`grep: .gitignore: No such file or directory`). This is the lane's own `python3 -B` rule leaking into the very directories C3 extends; a later `git add -A` by the integrator would land bytecode. Locations: `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/__pycache__/`, `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/__pycache__/`. Not removed — this seat is read-only.
5. **The pin's tree does contain axis-named files elsewhere (8 paths).** A repo-wide `grep -i axis` over `git ls-tree -r 89e0fce` returns 8, all wave/transcript reports (e.g. `.ufo/waves/round-25/w2/CritC3CoverageAxis.md`, `census/round-18/transcripts/w2/CriticC2Axis.txt`). Scope note only: the empty-set expectation holds for `tools/` + `tests/fixtures/`, not for the whole tree.
6. **Readings drift because the lane is live.** Mid-run `git symbolic-ref -q --short HEAD` printed `DETACHED` and commits advanced under the reader (`ba8b54b` → `c594901` → `0c92c2e`); at the final snapshot HEAD was attached to `master` and both equal `0c92c2e6fbe1` (`git rev-list --left-right --count master...HEAD` = `0 0`). Every count above is therefore labelled with its revision; the pin figures come from `git ls-tree` on the commit and are stable.
7. **Fixture-tree stale probes are intentional and ignored.** `tests/fixtures/case-F7/repo-tree/.scratch/stale-probe-f7.tmp` and the F8 counterpart are `!!` (ignored by the fixture's own `.gitignore`), i.e. fixture payload, not lane debris. Recorded so a later hygiene sweep does not mistake them for the incident's strays.
