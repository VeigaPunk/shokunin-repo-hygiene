# R42w2mutationtester06 — frontier mutation survey of `tools/souji-worktree-drift.py` (round 42, wave 2)

Seat: R42w2mutationtester06 (mutation-tester, leaf, no subagents). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Target: `tools/souji-worktree-drift.py`, pinned sha256 `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6`
(checked: working tree and `git show 3105a63b23481fccf7df58e74d14a6681e0ea0c8:tools/souji-worktree-drift.py` both give that digest).
Base `bf618f6c5c09d302994871c94903abbea2deb60d`, freeze `afe17f416eec04dcf3f480b580a8f928de61d19d`, tip under attack `3105a63b23481fccf7df58e74d14a6681e0ea0c8`.
Scope: read-only lane. Nothing committed, nothing landed, no frozen file read as a candidate, no lane file written. All scratch was under `/fast/scratch/hyaku/souji-r42/R42w2mutationtester06` and was deleted before this report.

## Verdict

- **75 single-point mutants** (requirement: at least 60) across `measure`, `discover`, `repo_path`, `open_nofollow`, the JSON writer, the drift accounting in `run()`, and the exit-code mapping in `main()`. None reuses a frozen C3 anchor string or id (checked: anchor-string overlap `set()`, id overlap `set()`).
- Each mutant was scored against **all nine drift fixtures** (the eight prior, plus the landed `tests/fixtures/r42-drift-conditions.py`). **36 killed, 39 survived all nine.** A kill uses the lane's own predicate (`c3-counter.py` `killed()`: rc 1, a SUMMARY line, `fail>0`, no traceback).
- The 39 survivors were put through a **dual differential oracle** (68 scenarios, each run on the pristine tool and the mutant). It separates behaviour from format and label:
  - **16 non-equivalent**: observable behaviour differs (stdout DRIFT rows or SUMMARY, exit code, refusal class token, traceback, the parsed `--json` document, or the `--json` file mode).
  - **23 equivalent**: 19 equivalent by code reasoning, format-only or label-only; 4 equivalent only under a precondition this battery does not construct (EQP: a race, a cross-device inode clash, or a host with `/.git`).
- The landed r42 fixture is among the killers of **17 of the 36 killed mutants**, and is the **only** killer of **MJ05** (line 430; the `--json` drift array dropped). It kills none of the 16 non-equivalent survivors.
- **The 16 non-equivalent survivors are the r43 coverage population**: edge classes the landed fixture and the eight prior fixtures do not observe (table in section 3).

## 1. Survivor-by-function table

Mutation counts are from `receipts/score.log` (75 `MUTANT` lines). Equivalence counts are from the dual oracle (`receipts/diff-shard-*.log`). `survived (non-equivalent / equivalent)`; the equivalent column includes the 4 EQP mutants.

| function | mutants | killed | survived (non-equivalent / equivalent) |
|---|---|---|---|
| `measure` (L189-205) | 10 | 3 | 7 (5 / 2) |
| `discover` (L217-235) | 10 | 3 | 7 (4 / 3) |
| `repo_path` (L208-214) | 6 | 3 | 3 (2 / 1) |
| `open_nofollow` (L238-280) | 12 | 5 | 7 (2 / 5) |
| JSON writer (L419-435, plus guard L319-348) | 14 | 5 | 9 (0 / 9) |
| drift accounting in `run()` (L352-392) | 13 | 10 | 3 (3 / 0) |
| exit-code mapping, `main()` and `run()` tail (L436-458) | 10 | 7 | 3 (0 / 3) |
| **total** | **75** | **36** | **39 (16 / 23)** |

Mutant ids and anchor lines are in `mutants.py` (this seat directory). The line number is the first line of each mutant's anchor in the pinned tool (`receipts/report.txt`).

## 2. Survivors (all 39), with class and line

Class: **NE** non-equivalent; **EQ** equivalent (code-proved, format-only or label-only); **EQP** equivalent under a stated precondition the battery does not construct.

| function | id | line | class | behaviour | reason / evidence |
|---|---|---|---|---|---|
| measure | MM01 | 197 | EQ | `worktree ` prefix loses its trailing space | git porcelain has no other line starting `worktree` |
| measure | MM03 | 202 | NE | a nonzero `prune --dry-run` return is no longer UNREACHABLE; a failed prune reads as zero prunable | `s_prune_rc_nonzero`: stdout differs |
| measure | MM04 | 204 | NE | blank or whitespace stderr lines counted as prunable candidates | `s_prune_whitespace_line`: rc 0 vs 1, stdout differs |
| measure | MM05 | 201 | NE | prune timeout reported under the list-timeout class string | `s_prune_hangs`: stdout class differs |
| measure | MM06 | 200 | NE | prune `TimeoutExpired` not caught: the run crashes instead of reporting UNREACHABLE | `s_prune_hangs`: traceback vs DRIFT row |
| measure | MM09 | 205 | EQ | success returns `""` instead of `None` in the error slot | `if error:` treats both as false |
| measure | MM10 | 197 | NE | worktree-list output decoded strictly: a non-UTF-8 path crashes the run | `s_list_output_invalid_utf8`: rc 0 vs traceback rc 1 |
| discover | MD01 | 220 | NE | root listing unsorted: the `--json` drift array follows filesystem order | `s_json_many_unrecorded`: `--json` document differs (fs-order dependent, XFS here) |
| discover | MD02 | 229 | EQ | child "is a directory" guard dropped | a regular-file child has no `.git` entry, so the `.git` test already rejects it |
| discover | MD04 | 234 | NE | root basename appended instead of inserted first: `--json` drift order changes | `s_json_root_repo_unrecorded_child`: `--json` document differs |
| discover | MD05 | 221 | NE | listing `OSError` swallowed: a NameError crash instead of an empty discovery | `s_unreadable_root`: stdout and traceback differ |
| discover | MD06 | 234 | EQ | root basename without `rstrip('/')` | `--root` is `os.path.abspath()`'d, which already strips the slash |
| discover | MD07 | 234 | EQP | nameless-root fallback `root` dropped | reachable only for `--root /` with a `/.git` directory; this host has none |
| discover | MD10 | 233 | NE | a root with a `.git` FILE also contributes its basename: a same-named child is measured twice | `s_root_gitfile_child_same_name`: stdout differs |
| repo_path | MR02 | 212 | NE | root self-name branch no longer requires `--root/.git`: a non-repository root is measured | `s_root_basename_row_other`: stdout differs |
| repo_path | MR04 | 212 | EQ | root self-name comparison without `rstrip('/')` | root is abspath'd before `repo_path()` |
| repo_path | MR05 | 212 | NE | root self-name branch accepts a `.git` FILE (a linked-worktree root) | `s_root_git_is_a_file_self_named`: stdout differs |
| open_nofollow | MO01 | 252 | NE | relative-path guard removed; reachable only by `--json /`: JSON-UNWRITABLE becomes an IndexError traceback | `s_json_root_slash`, `s_json_root_slash_only`: rc 2 vs 1 plus traceback |
| open_nofollow | MO02 | 251 | EQ | `.` components kept in the walk | `--json` target is `realpath()`'d, so `.` never reaches the walk |
| open_nofollow | MO03 | 257 | EQP | ancestor opened without `O_NOFOLLOW` | `--json` target is `realpath()`'d; only a symlink swapped between `realpath` and `open` reaches it (race, not constructed) |
| open_nofollow | MO04 | 263 | EQP | leaf opened without `O_NOFOLLOW` | the target is `realpath()`'d, so the leaf is never a symlink; only a race reaches it (not constructed) |
| open_nofollow | MO09 | 254 | EQ | root directory fd without `O_DIRECTORY` | `/` is a directory; the flag is redundant |
| open_nofollow | MO11 | 264 | NE | created `--json` file mode 0600, not 0644 | `s_json_plain` and five more: file mode differs (0o644 vs 0o600) |
| open_nofollow | MO12 | 276 | EQ | comment appended to a refusal line | comment only |
| json-writer | MJ02 | 430 | EQ | JSON written without `sort_keys` | format only: bytes differ, parsed document identical |
| json-writer | MJ03 | 430 | EQ | JSON written with `indent=None` | format only: bytes differ, parsed document identical |
| json-writer | MJ04 | 431 | EQ | trailing newline after the JSON dropped | format only: bytes differ, parsed document identical |
| json-writer | MJ07 | 425 | EQ | JSON-HARDLINKED message drops the link count | label only: the `REFUSAL JSON-HARDLINKED:` token is unchanged |
| json-writer | MJ08 | 344 | EQ | containment loop compares `commonpath` to root instead of each base | the root iteration (`measured[0]`) refuses every path the per-base test would, with the same message |
| json-writer | MJ10 | 337 | EQP | alias check compares inodes only | needs two devices with equal inode numbers; not constructed |
| json-writer | MJ11 | 332 | EQ | path-equality alias check dropped | a same-path target has the same inode, so the inode check catches it |
| json-writer | MJ12 | 341 | EQ | JSON-IS-RECORD message reworded | label only: class token unchanged |
| json-writer | MJ13 | 348 | EQ | JSON-INSIDE-MEASURED-TREE message reworded | label only: class token unchanged |
| drift-accounting | MA02 | 375 | NE | PRUNABLE-CHANGED emitted only when live exceeds the record | `s_prunable_changed`: rc 1 vs 0, stdout differs |
| drift-accounting | MA10 | 391 | NE | drift rows printed in record order, not sorted | `s_two_drift_rows_reversed`, `s_json_root_repo_unrecorded_child`: stdout differs |
| drift-accounting | MA11 | 363 | NE | ABSENT row loses its recorded-figure detail | `s_absent` and six more: stdout differs |
| exit-code-mapping | MX04 | 448 | EQ | USAGE refusal message reworded | label only: `REFUSAL USAGE:` token unchanged |
| exit-code-mapping | MX07 | 326 | EQ | `--json` `realpath` without `abspath` | `realpath()` of a relative path resolves against the cwd anyway |
| exit-code-mapping | MX08 | 331 | EQ | record path compared without `realpath` in the alias check | `os.stat` follows the symlink, so the inode check catches it |

### 2a. Non-equivalent survivors (the r43 population), one line each

1. **MM03** (L202) — a failed `git worktree prune --dry-run` is read as zero prunable instead of UNREACHABLE.
2. **MM04** (L204) — blank or whitespace stderr lines count as prunable candidates.
3. **MM05** (L201) — a prune timeout is reported under the list-timeout class string.
4. **MM06** (L200) — a prune `TimeoutExpired` is uncaught; the run crashes instead of reporting UNREACHABLE.
5. **MM10** (L197) — non-UTF-8 `worktree list` output crashes the run (strict decode).
6. **MD01** (L220) — unsorted root listing; the `--json` drift array follows filesystem order (fs-order dependent).
7. **MD04** (L234) — root basename appended instead of inserted; the `--json` drift order changes.
8. **MD05** (L221) — listing `OSError` swallowed; a NameError crash replaces the empty discovery.
9. **MD10** (L233) — a root with a `.git` FILE contributes its own basename, so a same-named child is measured twice.
10. **MR02** (L212) — the root self-name branch drops the `--root/.git` requirement; a non-repository root is measured.
11. **MR05** (L212) — the root self-name branch accepts a `.git` FILE (a linked-worktree root).
12. **MO01** (L252) — the relative-path guard is gone; reachable only by `--json /`, where JSON-UNWRITABLE becomes an IndexError traceback.
13. **MO11** (L264) — the created `--json` file is mode 0600 instead of 0644.
14. **MA02** (L375) — PRUNABLE-CHANGED fires only when live exceeds the record, so an over-counted record gets no drift row.
15. **MA10** (L391) — drift rows printed in record order, not sorted.
16. **MA11** (L363) — the ABSENT row loses its recorded-figure detail.

Per-fixture status: each of these 16 survives all nine fixtures (`receipts/score.log`). `receipts/scores.json` holds the per-fixture rc, case and failure counts.

### 2b. Equivalent survivors (23): why each is equivalent

- **Code-proved (12):** MM01, MM09, MD02, MD06, MR04, MO02, MO09, MO12, MJ08, MJ11, MX07, MX08. Each reduces to the same expression or the same refusal on every input the tool can receive. Two examples: `--json` is `realpath(abspath(...))`, so `.` and symlinks never reach `open_nofollow`; the root iteration of the containment loop already refuses every path a per-base test would.
- **Format-only or label-only (7):** MJ02, MJ03, MJ04 (JSON bytes; the parsed document is identical), and MJ07, MJ12, MJ13, MX04 (message text after an unchanged `REFUSAL <CLASS>:` token). This follows the lane's C3 rule that labels and bytes are not behaviour.
- **Precondition only (4, EQP):** MD07 (needs `--root /` with a `/.git`), MJ10 (needs two devices with equal inode numbers), MO03 and MO04 (need a symlink swapped between `realpath` and `open`). The battery constructs none of these. They are named limits, not claims of equivalence on every host.

## 3. Coverage gap statement (for the r43 population)

The landed fixture is among the killers of 17 of the 36 killed mutants. MJ05 (L430) is the only mutant it kills alone. It does not observe any of the 16 non-equivalent survivors in section 2a. The most important unobserved classes are:

- **Prune-side failures** (MM03, MM04, MM05, MM06): a failed or hung `git worktree prune`. The landed fixture observes the list-side timeout only.
- **Drift-row semantics** (MA02, MA10, MA11): the PRUNABLE-CHANGED threshold, the printed order, and the ABSENT detail.
- **Discovery and root handling** (MD01, MD04, MD05, MD10, MR02, MR05): listing errors, root-as-repository, and `.git` FILE roots.
- **`--json` edge cases** (MO01, MO11): the `/` target and the created file's mode.

## 4. Commands run and their output

All commands ran as uid 1000 with Python 3.14.8, with `TMPDIR` set to the seat scratch directory (now deleted). Exact copies of the outputs are in `receipts/`.

1. Digest of the pinned tool at the tip and in the working tree:
   `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 3105a63b23481fccf7df58e74d14a6681e0ea0c8:tools/souji-worktree-drift.py | sha256sum` → `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6  -`. `sha256sum tools/souji-worktree-drift.py` gives the same digest.
2. Nine-fixture baseline on the pristine tool (`receipts/score.log`, nine PRISTINE lines): every fixture `rc=0`, `fail=0`. Totals: 12, 6, 10, 12, 7, 8, 12, 21 (probes), 13.
3. Anchor check of all 75 mutants: `python3 -B harness.py check --scratch <S>` → `MUTANTS total=75 problems=0` (`receipts/spot-and-check.txt`). Anchor overlap with the frozen `c3-counter.py` tables was checked in Python: anchor-string overlap `set()`, id overlap `set()`.
4. Scoring: `python3 -B harness.py score --scratch <S> --workers 8 --timeout 180` ran the nine fixtures against each of the 75 mutants (`receipts/score.log`, 75 `MUTANT` lines; `receipts/scores.json`). Result: 36 KILLED, 39 SURVIVED.
5. Dual oracle on the 39 survivors: `python3 -B equivalence.py --scratch <S> --mutants <six shards of the 39> --out diff-shard-N.json` (six shards in parallel; `receipts/diff-shard-*.log` and `.json`). Output `DIFF <id> SEMANTIC:...`, `BYTE-ONLY:...` or `EQUIVALENT`.
6. Report merge: `python3 -B report.py --scratch <S> --out report.txt` → `receipts/report.txt`. It reports `CLASS-vs-ORACLE mismatches: none` (every NE class has a semantic oracle diff; no EQ class has one).
7. Direct spot-checks of the landed fixture (`receipts/spot-and-check.txt`):
   - pristine: `SUMMARY cases=13 pass=13 fail=0`, fixture rc 0.
   - MJ05 (mutant): `SUMMARY cases=13 pass=11 fail=2`, fixture rc 1.
   - MA10 (mutant): `SUMMARY cases=13 pass=13 fail=0`, fixture rc 0.
   - r41-refusal-sites against MA10: `SUMMARY probes=21 pass=21 fail=0`, rc 0.
   - The seven other prior fixtures against MA10 (run during the investigation, not in the receipt): all pass, so MA10 survives all nine.

## 5. Limits of this survey

- **Equivalence is battery-bounded.** The oracle has 68 scenarios. "EQUIVALENT" means no difference in any of them, and the EQ classes also rest on code reasoning. EQP classes name the precondition the battery does not construct.
- **Filesystem dependence.** MD01 depends on the filesystem's `listdir` order (the scratch and lane host is XFS). On a filesystem that lists in sorted order it would survive.
- **Time-based fixture cases.** r42's `default-timeout` and `list-timeout` cases depend on wall time. The baseline was clean in this run, but the kill table is one run and was not repeated under load.
- **The `--json` leaf/parent symlink and race classes (MO03, MO04)** would need a runtime race construction. This is an edge class the lane's fixtures cannot observe and this survey does not construct.
- **The seat's own scenario `s_unreadable_root`** leaves a directory at mode 000 after the run. Scratch cleanup needed a chmod on my own path. This is a defect in the seat's oracle, not in the lane.
- **Destructive mutant.** MM08 drops `--dry-run`, which makes the tool run a real `git worktree prune`. It was run only against fixture-built repositories under scratch, never against the lane or the fleet.

## 6. Tooling and lane state

- Tools installed or upgraded: none. Python 3.14.8 (host) and git on PATH were used unchanged.
- Lane writes: none. The lane was read through `git show` and `sha256sum`. The only files written are in `.ufo/waves/round-42/w2/R42w2mutationtester06/` (`mutants.py`, `harness.py`, `equivalence.py`, `report.py`, `lines.py`, `receipts/`) and this report.
- No git or jj mutation anywhere. No frozen file, population, counter, control or fixture was edited or copied as a candidate.
- Scratch `/fast/scratch/hyaku/souji-r42/R42w2mutationtester06` removed after receipts were copied.
