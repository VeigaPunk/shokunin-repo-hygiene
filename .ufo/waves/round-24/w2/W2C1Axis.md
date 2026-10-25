# W2C1Axis — C1 axis naming (coverage vs quality), round 24 wave 2

## Status

STATUS: PASS. Verdict: **coverage-move holds**, with a qualification. C1 does move a surface: it adds a new tool, a new operation class (a lane tool that runs `count-objects -v` and `fsck --unreachable`) and a new edge class (the linked-worktree `garbage` false positive). Every one of these is absent at base and present at the tip. But 4 of the 8 frozen cases re-score rules the lane already held at base, or are independent of the tool. Those cases are quality/operability content and must not be counted as coverage. PROVINCE.md, the coverage registry named by AXES, did not move.

## Evidence

Revisions: base `a65fac98964b445758e94c805728c9a19d302ff8`, after-receipts tip `ca7fc1cb6dd1333096c6f3bdbad304686691d126`; lane `master` read as `c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface` (wave-1 reports only, no change to tool/fixture/README/PROVINCE/SCORECARD versus ca7fc1c). git 2.56.0. Scratch `/var/tmp/souji-r24-W2C1Axis/` (git-archive extracts of the tip tool/fixture/stub and the base `tools/souji-repo-structure.sh`) was removed. `ls -d` of the scratch dir and of `/var/tmp/souji-r24-census-*` then printed "No such file or directory".

Contract text (bytes opened this run):
- `.ufo/prompts/souji-round-24.md:374-375` (§9): "Re-scoring a rule the lane already holds on new inputs, or counting rows a sourceless fixture also counts, is quality work, never coverage or depth."
- `AXES.md:12` coverage: "Fraction of the domain's real surfaces the skill governs (repo paths, tools, edge classes)". Its signal column names `PROVINCE.md` as the surface list.
- `preregistration.txt:31`: "Command that would show it unmoved: `git cat-file -e <rev>:tests/fixtures/r24-size-census.py`".
- `corpus/README.md:486-487` (`### Frontier (r23)`, at both revisions): "the `/var/tmp` write-safety fixture that must exclude `git fsck --lost-found` (S116), a lane-bound size/debris".
- `corpus/README.md:516` at ca7fc1c (`## Round 24` table): "| F2 repository size census | frontier; read side (three entries, r13/r23) plus a write-safety debris census (r24 C1".

These are the commands that would show the surface unmoved. Each was run at both revisions; exit 1 or 128 means unmoved.

| # | command | a65fac9 | ca7fc1c |
|---|---|---|---|
| U0 (prereg) | `git cat-file -e <rev>:tests/fixtures/r24-size-census.py` (and the same for `tools/souji-size-census.py`) | exit 128 / 128 | exit 0 / 0 |
| U1 operation class | `git grep -l -E '"count-objects", "-v"\|"fsck", "--unreachable"' <rev> -- tools` | exit 1 (no lane tool runs either) | `tools/souji-size-census.py`, exit 0 |
| U2 edge class | `git grep -l -F 'garbage: 1' <rev> -- corpus/knowledge` | exit 1 | `corpus/knowledge/count-objects-linked-worktree-garbage.md`, exit 0 |
| U3 coverage registry | `git diff --quiet a65fac9 ca7fc1c -- PROVINCE.md SKILL.md SCORECARD.md` | — | exit 0 (**unchanged**) |

(U1's pipe is written as `\|` only because it sits inside a table cell. The command itself uses a plain regex alternation.)

Fixture runs with the frozen counter at the tip bytes (`python3 -B tests/fixtures/r24-size-census.py --tool <T>`, cwd = tip extract):

| --tool | last line | exit | per-case PASS |
|---|---|---|---|
| tip `tools/souji-size-census.py` | `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` | 0 | 1–8 |
| base's nearest F2 tool `tools/souji-repo-structure.sh@a65fac9` (python exec wrapper) | `cases=8 pass=2 …` | 1 | 7, 8 only; in case 6, the `lost_found_argv` and `partial_clone` arms already return exit 2, and only the `promisor_unset` arm fails (exit 0) |
| committed stub `census/round-24/controls/stub-size-census.py` | `cases=8 pass=4 …` | 1 | 1, 4, 7, 8 |
| scratch mutant: tip tool with `--git-dir=<common>` replaced by `-C <path>` for `count-objects` (no linked-worktree discount) | `cases=8 pass=6 …` | 1 | case 3 fails because its linked arm gives `counts=2,2,0,0`; case 4 fails with `counts=1,0,0,0 … raw_linked_garbage=1` |

## Findings

1. **The surface moved, so it is coverage and not mislabelled.**
   - U1 goes from 0 to 1. Before C1, no lane tool ran `count-objects -v` or `fsck --unreachable` (see U1 above). That is a new tool and a new operation class, both of which §9 names as coverage surfaces.
   - The base corpus itself names the gap. `corpus/knowledge/git-repo-structure-readonly.md:19@a65fac9` says "Use a separate read-only object census; reachable totals do not count unreachable objects."
   - Base `PROVINCE.md:68` lists "unreachable-object census remain frontier".
   - The base nearest tool scores 2/8, and its two passes are the tool-independent cases. So the operation was not covered at base.

2. **New edge class, and it is pinned.**
   - U2 goes from 0 to 1: the linked-worktree `garbage` false positive. No base knowledge entry carries it.
   - The no-discount mutant fails cases 3 and 4. So the fixture can detect the loss of the edge class.
   - Caveat: the always-zero stub passes case 4 on its own. The edge class is pinned only jointly with case 3's linked arm (`garbage=1 size_garbage=2` on the linked path).

3. **Counterexample: half the case set re-scores held rules or is independent of the tool, which is quality/operability content, not coverage.** All of the following were held at base:
   - **Common-dir resolution for linked worktrees:** `tools/souji-repo-structure.sh:32-34@a65fac9` ("common object store … reports the resolved common dir; the object store is shared").
   - **Promisor/partial-clone refusal:** `tools/souji-repo-structure.sh:74@a65fac9` ("a promisor/partial clone (`extensions.partialClone` set or a").
   - **`--lost-found` as a runnable refusal:** `tools/souji-receipt-run.py:101-102@a65fac9` ("WRITE-SIDE-EFFECT: git fsck --lost-found writes into the repository").
   - **The `--lost-found` write rule and the alternates-must-be-read rule:** `corpus/knowledge/repo-size-census-readonly.md:29-33@a65fac9` ("`git fsck --lost-found` WRITES. … This is the write-safety trap the F2 fixture must fence").

   How each case maps to those rules:
   - **Case 6:** the `lost_found_argv` and `partial_clone` arms re-score held refusals, and the base tool passes both. Only the `objects/pack/*.promisor` arm (`promisor_unset`) is new.
   - **Case 5** applies the held alternates rule.
   - **Case 7** passes with every `--tool` tried: tip tool, base tool, stub and mutant. It witnesses git and re-witnesses the held entry rule 3.
   - **Case 8** scores the stub, not the tool.

   The coverage move therefore rests on cases 1–4, the `.promisor`-pack arm, the tool and the new entry. Neither `lost_found=WRITE-DETECTED` nor "a refused --lost-found" (preregistration C1 "New operation class" sentence) is new coverage.
   - Impacted axes: coverage (overstated breadth of the move) and calibration (narrative overreach). The axis label of C1 itself is not impacted.

4. **The prereg's unmoved command is an artifact-existence check, not a surface check.**
   - U0 is `git cat-file -e` on a fixture path. Any fixture file at that path flips it, including one holding only the tool-independent cases 7 and 8.
   - Only its second disjunct (the target line) depends on the tool.
   - This is a fixable defect in wording, not a reason to reject C1, because the frozen target line does discriminate: the stub scores 4/8 and the base tool 2/8.
   - Under §9, the honest unmoved commands are U1 (operation class) and U2 (edge class).

5. **No frontier→core move, and the coverage registry is stale.**
   - U3: PROVINCE.md is byte-identical between base and tip. `PROVINCE.md:67-68` (unchanged at ca7fc1c) still reads "isolated write-safety fixture acquired r13; whole-workspace size attribution and unreachable-object census remain frontier".
   - Meanwhile the tip has a single-repo unreachable census tool, and README:516 keeps F2 at `frontier`.
   - C1 must therefore be reported as "new tool + operation + edge class within F2 frontier", never as "frontier → core".
   - Missing SCORECARD r24 rows at ca7fc1c are a round-end item and are not scored here.

## Attack log

| attack | command (run this seat) | result |
|---|---|---|
| A1 the surface is unmoved (C1 is only a re-scoring) | U1, U2 at both revisions; tip fixture with the base nearest tool | **falsified**: both surfaces go from 0 to 1; base tool 2/8 |
| A2 the edge class is not pinned by the counter | tip fixture against the scratch no-discount mutant | **falsified**: mutant 6/8, fails cases 3 and 4 |
| A3 part of the case set re-scores held rules (§9 quality clause) | tip fixture against the base tool and the stub; `git show a65fac9:` reads of receipt-run.py, repo-structure.sh and repo-size-census-readonly.md | **holds for cases 5, 6 (two of three arms), 7 and 8**; a fixable over-claim in the narrative, not a mislabel of the axis |
| A4 the prereg unmoved command is gameable | reading `preregistration.txt:31`; U0 | **holds** as a weak witness; the frozen target line still discriminates |
| A5 the move is presented as frontier→core | U3; README:516; PROVINCE:67-68 | no move in PROVINCE; the registry is stale against the tip tool |

Smallest safe correction (report wording only; no predicate, target or case set changes):
- **In the round report and SCORECARD C1 row:**
  - Credit coverage to U1 and U2: the new tool, the `count-objects`/`fsck --unreachable` operation class and the linked-worktree edge class.
  - Label cases 5, 6 (the `lost_found_argv` and `partial_clone` arms), 7 and 8 as held-rule or independent-of-the-tool checks.
  - Keep F2 at frontier.
- **PROVINCE.md:** append an r24 boundary line saying that the unreachable census exists for a single repo only, via `tools/souji-size-census.py`, while F2 stays frontier.

Tools installed or updated: none.
