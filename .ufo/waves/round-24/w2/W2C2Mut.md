# W2C2Mut — C2 mutation probe (souji r24, wave 2 FALSIFY)

## Status
STATUS: PASS — C2 survives falsification. The fixture kills 11 of 13 mutants; `uncovered=2` (front-matter-past-heading, F-token lookahead-dropped). Both survivors are proven non-equivalent but leave the lane numbers unchanged at base and tip. Every mutant that changes the claim's lane numbers is killed by the fixture.

## Evidence
- Artifacts: `git show ca7fc1cb6dd1333096c6f3bdbad304686691d126:{tools/souji-coverage-agreement.py,tests/fixtures/r24-coverage-agreement.py}` were copied to `/var/tmp/souji-r24-W2C2Mut/pristine/`. Their blob ids are `16c44d7c…`/`add3917e…`, equal to `git hash-object` of the copies. sha256: tool `71b89eb3c7ce417979c5fce2c759dafe023af21d6310fde49197c766b8f28897`, fixture `42259756a06538a5dfb81cb82fba20737eacdcfd5c06b9b36594071b26f9da44`. These equal the `tool_sha256=` values in the committed receipts.
- `git diff --stat ca7fc1cb… master -- tools/souji-coverage-agreement.py tests/fixtures/r24-coverage-agreement.py corpus/README.md` printed nothing. Current master is `c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface`; none of the three files drifted.
- Receipts: `souji-receipt-run.py verify` returns `verify=ok` for `c2-after.tsv` (`grounded=6 mapped=6 dangling=0 mismatches=0`), `c2-control-base.tsv` (`grounded=4 mapped=2 dangling=0 mismatches=2`) and `c2-fixture-after.tsv` (`cases=9 pass=9 control=FALSE-GREEN-REJECTED`).
- Driver: `python3 -B /var/tmp/souji-r24-W2C2Mut/drive.py`. Each mutant gets its own scratch copy, made by an exact-once string replacement (an assert checks the count). The driver then runs the fixture (`--tool <mutant>`) and the mutant at `--root /home/vgpnk/Projects/shokunin/souji-shokunin --rev a65fac98…` and `--rev ca7fc1cb…`, and restores the copy from pristine bytes in `finally`. Tooling: git 2.56.0, Python 3.14.8. Nothing was installed.
- Baseline (pristine) results:
  - Fixture: `cases=9 pass=9 control=FALSE-GREEN-REJECTED`, exit 0.
  - Lane at base: `grounded=4 mapped=2 dangling=0 mismatches=2`, exit 1. The two rows are MISSING-FROM-MAP for `count-objects-garbage-readings-r25.md` and `repo-size-census-readonly.md`.
  - Lane at tip: `grounded=6 mapped=6 dangling=0 mismatches=0`, exit 0.
  - The baseline is green, so verdicts are conclusive.

| mutant | edit | fixture | failing cases | lane base (G/M/D/X) | lane tip (G/M/D/X) |
|---|---|---|---|---|---|
| M1a entries col +1 | `row[2]`→`row[3]` | KILLED 1/9 | 1–8 | 4/0/0/**4** | 6/0/0/**6** |
| M1b entries col −1 | `row[2]`→`row[1]` | KILLED 1/9 | 1–8 | 4/0/0/**4** | 6/0/0/**6** |
| M2 status column counted | entries = `" ".join(row[1:3])` | KILLED 7/9 | 3, 5 | 4/2/0/2 | 6/6/0/0 |
| M3a F-token prefix (F21 row also serves F2) | names added to every decimal prefix of k | KILLED 8/9 | 6 | 4/2/0/2 | 6/6/0/0 |
| M3b F-token lookahead dropped | `^F([0-9]+)(?=[ \-]\x7C$)`→`^F([0-9]+)` | **SURVIVED 9/9** | — | 4/2/0/2 | 6/6/0/0 |
| M3c F-token single digit | →`^F([0-9])` | KILLED 8/9 | 6 | 4/2/0/2 | 6/6/0/0 |
| M4 front matter read past first heading | `# ` break removed | **SURVIVED 9/9** | — | 4/2/0/2 | 6/6/0/0 |
| M5a working-tree read (`show`) | `show()` opens `<root>/<path>` | KILLED 8/9 | 7 | **5/5/1/1** | 6/6/0/0 |
| M5b working-tree read (`show` + tree) | also `os.listdir` | KILLED 7/9 | 1, 7 | **6/6/0/0** | 6/6/0/0 |
| M6 dangling check off | `if False and …` | KILLED 8/9 | 5 | 4/2/0/2 | 6/6/0/0 |
| M7 escaped `\|` split | `(?<!\\)\|`→`\|` | KILLED 1/9 | 1–8 | 4/2/0/2 | 6/6/0/0 |
| M8a only first map table read | `return` when a map table ends | KILLED 1/9 | 1–8 | 4/2/0/2 (F2 rows=1) | 6/2/0/**4** |
| M8b only first table of any kind | `return` when any table ends | KILLED 1/9 | 1–8 | 4/2/0/2 (F2 rows=1) | 6/2/0/**4** |

(`\x7C` stands for the literal pipe in the regex.) "Fixture" shows the verdict and how many cases passed out of 9. In the lane columns, G/M/D/X are grounded/mapped/dangling/mismatches. The control was `FALSE-GREEN-REJECTED` in every run.

- Restoration: for every mutant the sha256 sequence was before `71b89eb3c7ce4179` → mutated (a distinct value per mutant) → restored `71b89eb3c7ce4179`, and the driver printed `restored==pristine: True`. The driver's closing line was `pristine hashes unchanged: True`.
- Non-equivalence of the two survivors, checked with a synthetic repo built in scratch. It contains `a-f2.md` (`ground: F2`) mapped only by a row whose ground cell is `F2: size census`, and `late.md`, whose only `ground: F9` line comes after `# body`:
  - Pristine: `grounded=1 mapped=0 dangling=0 mismatches=1`, exit 1.
  - M3b: `grounded=1 mapped=1 dangling=0 mismatches=0`, exit 0. This is a false green.
  - M4: `grounded=2 mapped=0 dangling=0 mismatches=2`, exit 1. `grounded` is inflated.

## Findings
1. **Uncovered: front-matter boundary (M4).** The fixture's `entry()` never places a `ground:` line after the heading. The frozen definition reads `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-24/preregistration.txt:82`: "an entry corpus/knowledge/<n>.md at rev carrying a front-matter line". A tool that reads body text passes 9/9. It inflates `grounded`, the quantity the kill rule compares (`grounded(tip) < grounded(base)`, line 91). Neither lane revision has a post-heading `ground:` line (awk scan of every `.md` at both revs printed nothing), so the claim's numbers are unaffected. Coverage finding only.
2. **Uncovered: F-token terminator (M3b).** Prereg lines 84–85: "starts with the token F<k> (F<k> followed / by a space, `-`, or end of cell)". Case 6 pins `F21` against `F2`, and `F1-jj`, but not a non-space, non-hyphen terminator (`F2:`, `F2,`, `F2.`). The mutant maps such a row and turns a real mismatch into exit 0, a false green. No ground cell at either lane revision matches `^\| *F[0-9]+[^0-9 -]` (grep printed nothing), so the claim's numbers are unaffected.
3. **Mutants that change the claim's numbers** are M1a, M1b, M8a, M8b (the tip misses target 0: X=6, 6, 4, 4) and M5a, M5b (the base control changes: X=1 with a DANGLING row instead of 2 MISSING rows, and X=0). M5b erases the before→after delta altogether (base 0 = tip 0). Each of these is killed by the fixture: M1/M8 by cases 1–8, M5 by case 7, and M5b also by case 1. None produces a false PASS that the fixture accepts.
4. **Killed but lane-invisible:** M2, M3a, M3c, M6, M7 leave both lane counts lines identical to pristine. At these revisions the lane's README offers no instance of the defect: its only `\|` cell (line 40, F2 status) has entries `—`, and no status cell names a `knowledge/` path that is not also in an entries cell of its row. These defects are guarded only by the fixture, not by the claim data.
5. **M5 lane figures depend on the checkout, not on the revision.** The lane worktree is at `c3ca7ad3…` with `M corpus/QUALITY.md` (`git --no-optional-locks status --porcelain -- corpus/`). M5a's base `DANGLING-MAP-PATH … count-objects-linked-worktree-garbage.md` (`corpus/README.md:516`) comes from reading the current README against base's `ls-tree`. Rerunning later would give different figures; the pristine tool is immune (it reads `git show <rev>:` only, tool lines 47–48).

## Attack log
- Hypothesis: a plausible single defect in column selection, token matching, front-matter scope, read source, dangling detection, cell splitting or table scope passes the fixture and/or moves `mismatches` at base or tip. Result: two defects pass the fixture (M3b, M4), but neither moves the lane numbers. Every number-moving defect is killed. Verdict on C2: **survives**; fixture coverage gap `uncovered=2` (1 of the 8 named classes: front matter).
- Not attacked: `mapped` semantics (the fixture header says it is deliberately unasserted), the rev-refusal path (case 9), and the receipt runner.
- Scratch `/var/tmp/souji-r24-W2C2Mut/` was removed after the run. No lane write other than this report.
