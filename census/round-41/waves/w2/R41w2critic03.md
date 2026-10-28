# R41w2critic03 — falsification of the landed C3 fixture (tests/fixtures/r41-refusal-sites.py)

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. Tip 1d41c13574db80fdd9a4bde490b712da7ce2a85f.
Fixture: tests/fixtures/r41-refusal-sites.py at a1144120611b00091ac4839559d8ebf38aa9a83a (R41executor04).
Tool under test: tools/souji-worktree-drift.py, sha256 b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6 (matches the frozen value in the item).
Method: behavioural mutants of the tool (condition, errno, or refusal-path changes), each run through the unmodified fixture. No lane file, census file or tracked file was written. Mutant copies lived only in /fast/scratch/hyaku/souji-r41/R41w2critic03 (deleted before yield). Diffs, fixture logs and supplementary outputs are in `R41w2critic03/mutants/`.

## Environment
- uid 1000 (non-root, required by P02a/P18), Python 3.14.8, git 2.56.0. Nothing installed or upgraded.
- Read-only checks on the lane: `git -C` not used; `git log --oneline -3` and `git rev-parse --show-toplevel` at the lane root (output: lane root path, tip 1d41c13 / 31e4d3e / 119c26f).

## Baseline (committed tool, unmodified)
Command:
`TMPDIR=$S/work/base python3 -B tests/fixtures/r41-refusal-sites.py --tool $S/base/tool.py --work $S/work/base`
Output (copy at `mutants/base-fixture.txt`):
```
probe-P01=PASS rc=2 ... probe-P19=PASS rc=2
SUMMARY probes=21 pass=21 fail=0
rc=0
```
Baseline is green: 21 probes map onto the 19 sites in census/round-41/c3-sites.tsv (S02 and S10 each have two probes).

## Mutants and fixture verdicts (29 mutants; 21 killed, 8 survive)
Each mutant = copy of the committed tool with one line changed (exact diffs: `mutants/all-diffs.txt`; per-mutant fixture logs `mutants/Mxx.fixture`; table `mutants/summary.txt`). Run as:
`python3 -B tests/fixtures/r41-refusal-sites.py --tool $S/mut/Mxx.py --work $S/work/Mxx` (25 runs in parallel; M17 hit the fixture's 30 s subprocess timeout).

Killed (fixture reports FAIL):
| Mutant | Site / behaviour changed | Fixture FAIL set |
|---|---|---|
| M01 | parse_record: EACCES on record open returns empty record (swallowed) | P02a |
| M02 | parse_record: ENOENT branch condition changed to EPERM | P01 |
| M04 | parse_record: non-regular check inverted | P03 P06 P10a P10b P11 P13 P14 P15 P16 P17 P18 |
| M05 | parse_record: fstat non-regular refusal removed | P03 |
| M06 | duplicate REPO row check removed | P04 |
| M08 | TOTAL regs check removed | P08 |
| M09 | empty-record check removed | P06 |
| M11 | row containment check removed | P13 |
| M12 | gitdir containment check replaced by True | P14 |
| M14 | JSON guard drops root from the measured list | P16 |
| M15 | JSON guard checks no measured tree | P16 |
| M16 | hardlink threshold nlink > 2 | P17 |
| M17 | open_nofollow drops O_NONBLOCK (FIFO --json hangs) | P10a (timeout, 30 s) |
| M18 | ENXIO/EISDIR tuple reduced to ENXIO | P10b |
| M19 | open_nofollow non-regular check removed | P11 |
| M20 | JSON write EACCES swallowed (exit 1, no write) | P18 |
| M21 | --timeout check off by one | P19 |
| M22 | --root is-a-directory check removed | P12 |
| M27 | TOTAL prunable check removed | P09 |
| M28 | non-schema line silently skipped | P05 |
| M29 | TOTAL repos check removed | P07 |

Survived (fixture still SUMMARY fail=0, rc=0):
| Mutant | Change | Why the battery misses it |
|---|---|---|
| M03 | record open without O_NONBLOCK | No FIFO-record probe. Base refuses at once (`RECORD-MALFORMED ... is not a regular file`, rc 2); M03 blocks forever on a FIFO record (rc 124 after `timeout 5`). |
| M07 | TOTAL loop checks only the last TOTAL row (`totals[-1:]`) | This is the r40 M40-4 regression the tool's own comment (lines 167-170) names. No probe has two TOTAL rows. Base: `REFUSAL RECORD-MALFORMED: TOTAL repos=2 but 1 REPO rows`; M07: rc 0. |
| M10 | containment via `startswith` instead of commonpath | No sibling-prefix probe (P13 uses `../sib`, which shares no prefix). Base: `RECORD-OUTSIDE-ROOT` rc 2; M10 with a non-repo sibling: `DRIFT ABSENT ../rootx-plain`, rc 1 (class changed). With a repo sibling the gitdir check still catches it, so only the non-repo case escapes. |
| M13 | JSON-IS-RECORD inode-identity arm removed | No hardlink-alias probe. Base: `JSON-IS-RECORD: ... alias.json is the record file`; M13: `JSON-HARDLINKED ... has 2 links`. Same rc 2, different class. |
| M23 | ancestor-walk O_NOFOLLOW removed | Not observable without a race: json_target is already realpath'ed before open_nofollow, so symlink components are resolved, never refused. Base writes through a symlinked directory with rc 0 (`supp-base.txt` H). See finding 4. |
| M24 | JSON write refused whenever nlink >= 1 | No positive write probe. P17 still passes because the hardlink is refused either way. Supplementary A: base writes `out_good.json` rc 0; M24 refuses a plain write `JSON-HARDLINKED ... has 1 links` rc 2. |
| M25 | summary `unreachable` forced to 0 (stdout and JSON) | No output-content probe. Supplementary I: base `"unreachable": 1` and `SUMMARY ... unreachable=1`; M25 `"unreachable": 0` and `unreachable=0`. |
| M26 | JSON guard drops repo entries, keeps root (`measured[:1]`) | Equivalent under containment: every measured path is checked under root_real first, so the root arm subsumes the repo arm. See finding 3. |

Supplementary runs (`mutants/supp.sh`, outputs `mutants/supp-<variant>.txt`) confirm each survivor's behaviour change directly with inputs the fixture lacks. Relevant rows:
- base A: `[base] A-good-json-write rc=0 ... drift_rows=0 unreachable=0`; M24 A: `rc=2 ... REFUSAL JSON-HARDLINKED: .../out_good.json has 1 links`.
- base B: `rc=2 RECORD-MALFORMED ... fifo.rec is not a regular file`; M03 B: `rc=124 stderr=none` (hang until the 5 s timeout).
- base C: `rc=2 RECORD-MALFORMED: TOTAL repos=2 but 1 REPO rows`; M07 C: `rc=0`.
- base E: `rc=2 REFUSAL JSON-IS-RECORD: .../alias.json is the record file`; M13 E: `rc=2 REFUSAL JSON-HARDLINKED: .../alias.json has 2 links`.
- base F/G: `JSON-INSIDE-MEASURED-TREE: .../root/o.json is under .../root` and `.../root/a/o.json is under .../root`; M26 identical.
- base I: `"unreachable": 1`; M25 I: `"unreachable": 0`.
- D2 (non-repo sibling `../rootx-plain`): base `rc=2 RECORD-OUTSIDE-ROOT`; M10 `rc=1 DRIFT ABSENT ../rootx-plain`.

## Findings
1. Sites are covered by class, not by condition. Each of the 19 sites has at least one mutant that the fixture kills, but 8 of 29 behavioural mutants survive. The battery asserts only rc 2 plus a class substring. It cannot tell a changed condition or errno path from the original when the class label stays the same.
2. Probe gaps the survivors expose: no FIFO record (M03), no two-TOTAL record (M07, the documented r40 regression), no sibling-prefix row (M10), no hardlink alias of the record (M13), no positive `--json` write (M24), no output-content check (M25).
3. P16 is mis-wired. It is labelled "--json lies under a measured repository" (c3-sites.tsv S16), but its record argument is `ok`, whose only row is `REPO a`. Repository `r` is never measured, so P16 exercises the root arm only (base stderr says `is under .../root`, and the same for scenario G, which is under repo `a`). The repo arm is therefore untested, and it is also redundant under containment (M26). Killing M14 and M15 shows P16 covers the root arm.
4. The symlink claim is not reachable. The JSON-UNWRITABLE docstring says a "symlinked path component" is "refused by the O_NOFOLLOW walk". Base never refuses it: realpath resolves the component before open_nofollow, and scenario H wrote `x.json` into the real directory with rc 0. Only a race could reach the walk, and the fixture has no race probe. The S18 wording (EACCES only) is accurate, but the docstring claim is not.
5. Dead scaffold: tests/fixtures/r41-refusal-sites.py line 46 creates `W/rr`, which no probe uses. It looks like a dropped sibling-prefix probe.
6. Not checked: the committed counters (c1/c2/c3-counter) were not run; this report covers only the mutant battery.

## Verdict
C3 as a condition-level coverage claim is falsified: 8 of 29 behavioural mutants survive, including a hang (M03), a documented regression (M07), two class changes (M10, M13), an absent success path (M24) and output corruption (M25). P16 does not prove the S16 site it is labelled for. C3 as a class-level claim holds: the 21 probes return the labelled class for the base tool (baseline 21/21), and every site's refusal branch is reached by at least one killed mutant.
Fix candidates for the owner (not applied here): add probes for a FIFO record, a two-TOTAL pair with the first disagreeing, a sibling-prefix row, a hardlink alias of the record, a positive `--json` write checked for content, and a P16 that uses a record naming repo `r`; reword the docstring symlink claim. Not done: no tracked file was edited.

## Commands actually run
- `git -C` not used. Read-only: `git log --oneline -3`, `git rev-parse --show-toplevel` at lane root.
- `sha256sum tools/souji-worktree-drift.py` (matches b2a603cf...).
- Baseline fixture run and 25 mutant fixture runs in parallel (`for m in ...; do ... python3 -B .../r41-refusal-sites.py --tool $S/mut/Mxx.py --work $S/work/Mxx & done; wait`), then M26, M27, M28, M29 (sequential). Each log in `mutants/Mxx.fixture`.
- `ast.parse` on every mutant (all parse). `diff -u base/tool.py mut/Mxx.py` for each mutant (`mutants/all-diffs.txt`).
- `bash supp.sh <tool> <variant>` for base, M03, M07, M10, M13, M23, M24, M25, M26 (`mutants/supp-*.txt`); plus the D2 sibling-non-repo check (inline; output above).
- Not run: committed counters, score-candidate.sh, jj-lane.sh; no installs; no git mutation.
