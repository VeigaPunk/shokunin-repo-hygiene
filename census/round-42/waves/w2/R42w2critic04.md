# R42w2critic04: falsification of the landed C3 fixture (coverage)

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`. Tip `3105a63b23481fccf7df58e74d14a6681e0ea0c8` (read with `git show`; the working tree was not used). Target: `tests/fixtures/r42-drift-conditions.py` (C3, landed). Pinned tool `tools/souji-worktree-drift.py` sha256 `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6` (verified at the tip). Seat R42w2critic04, critic, leaf (no subagents). Scratch `/fast/scratch/hyaku/souji-r42/R42w2critic04` (deleted before yield). Seat scripts and receipts: `.ufo/waves/round-42/w2/R42w2critic04/`.

## Verdict

- **Frozen C3 target still holds at the tip.** The counter run (section 2f) prints `SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok`, exit 0.
- **The landed fixture is not condition-complete.** I generated 77 new single-point condition mutants of the pinned tool and ran each against the landed fixture and the eight prior fixtures (702 runs). The landed fixture kills 10 of the 77 and is the only killer of one (S64). The prior fixtures kill 42 (33 of those are not killed by the landed fixture). **34 survive all nine.**
- **Of the 34 survivors, 17 are equivalent** (11 by code argument plus scenario equality, 2 bytes-only, 1 stderr-text-only, 3 unobservable under the child-environment whitelist). **17 are non-equivalent**: 16 have a deterministic probe, and 1 (S42) is observable only through a timing race. The 17 non-equivalent survivors are the named coverage limits for r43 (section 4).
- **Harness observation (not edited):** under S64 the prior fixture `r38-drift-write-envelope.py` prints a Python traceback (`matrix.json`, crash=true), so the counter's kill rule does not count it as a kill there.

## 1. Method

- **Mutants (`mutants.py`, 77 entries S01–S77).** Each is an exact string replacement. Its `old` string is asserted to occur exactly once in the pinned tool (`matrix.py` exits on any count other than 1). No `ast` edits. Categories: record read and parse, TOTAL arithmetic, comment and blank handling, repo_path and discovery, gitdir containment, `--json` guard, write, hardlink and alias, FIFO and mode, argparse and exit codes, summary accounting, child environment.
- **Overlap with the frozen tables** (`census/round-42/c3-counter.py` MUTANTS and EQUIV): no survey mutant has the same (old, new) pair. Two survey mutants share an anchor with a frozen mutant but make a different change: S66 (`os.ftruncate(fd, 0)` → `1`; frozen M1 removes the call) and S70 (`if args.timeout < 1:` → `< 0`; frozen G2 uses `<= 1`).
- **Matrix (`matrix.py`).** Each mutant against the landed fixture and the eight PRIOR fixtures (the list in `c3-counter.py`), 8 workers. Kill rule is the counter's `killed()`: cases reported, rc 1, failed > 0, no traceback. Per-run raw records in `matrix.json`; per-mutant rows in `matrix.tsv`.
- **Differential probes (`probes.py`).** 46 scenarios run on identical inputs with the pristine tool and with each of the 34 survivors (plus 8 cross-checks that prior fixtures already kill). The compared outcome is rc, stdout, stderr, the `--json` file's mode and parsed content and bytes, the orig-file hash for the hardlink scenario, and a fast/slow timing class. Results: `probes-results.json`, `probes-run.log`.
- **Joined table (`report_table.py`).** Joins the matrix and probe results and writes `table.tsv`. The equivalence reasons are the seat's; each is backed by a scenario or by the matrix.
- **Equivalence standard.** A mutant is equivalent only if no scenario differs and a code argument holds. Bytes-only and stderr-text-only differences count as equivalent and are labelled. Scenarios are finite (46), so equivalence means "no difference observed plus code argument", not a proof for every input.

## 2. Commands run and their output

**2a. Pinned tool at the tip.**
```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 3105a63b23481fccf7df58e74d14a6681e0ea0c8:tools/souji-worktree-drift.py | sha256sum
b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6  -
```

**2b. Pristine baseline, nine fixtures** (`python3 -B <fixture> --tool <pristine> --work <dir>`; receipts in `baseline/`). All clean:
```
r36-worktree-drift:          SUMMARY cases=12 pass=12 fail=0 rc=0
r37-drift-discrimination:    SUMMARY cases=6 pass=6 fail=0 rc=0
r38-drift-record:            SUMMARY cases=10 pass=10 fail=0 rc=0
r38-drift-write-envelope:    SUMMARY cases=12 pass=12 fail=0 rc=0
r39-drift-record-rules:      SUMMARY cases=7 pass=7 fail=0 rc=0
r40-drift-record-branches:   SUMMARY cases=8 pass=8 fail=0 rc=0
r41-drift-record-order:      SUMMARY cases=12 pass=12 fail=0 rc=0
r41-refusal-sites:           SUMMARY probes=21 pass=21 fail=0 rc=0
r42-drift-conditions:        SUMMARY cases=13 pass=13 fail=0 rc=0   (44 s; FIFO timeouts)
```

**2c. Matrix** (`python3 -B .ufo/waves/round-42/w2/R42w2critic04/matrix.py`; log `matrix-run.log`). Last lines:
```
RAN 702 runs in 527.4s
PRISTINE r42-drift-co=clean r36-worktree=clean r37-drift-di=clean r38-drift-re=clean r38-drift-wr=clean r39-drift-re=clean r40-drift-re=clean r41-drift-re=clean r41-refusal-=clean
```
Crash rows: `[('S64', 'r38-drift-write-envelope.py')]`. Timeout rows: none. Pristine runs dirty: none.

**2d. Differential probes** (`python3 -B probes.py S03 S11 … S77`; log `probes-run.log`). Final run, excerpt:
```
PRISTINE scenarios=46 errors=[]
S03 1 big-3000:rc 1->2,stdout,stderr-class
S11 1 total-junk:rc 2->0,stdout,stderr-class
S12 1 space-name:rc 0->2,stdout,stderr-class
S13 1 empty-regs:rc 2->1,stderr-class
S17 1 total-prunable-small:rc 2->1,stdout,stderr-class
S18 0 / S19 0 / S28 0 / S29 0 / S30 0 / S39 0 / S41 0 / S51 0 / S65 0 / S66 0 / S69 0 / S75 0 / S76 0 / S77 0
S67 5 json-sibling-prefix:json-bytes-only; json-mode:json-bytes-only; json-unicode-name:json-bytes-only; json-relative:json-bytes-only; json-overwrite-long:json-bytes-only
S68 5 (same five scenarios, json-bytes-only)
S74 19 (stderr-text-only in 19 refusal scenarios)
S35 1 timeout-fifo-head:timing
S43 3 regs-up:rc 1->0,stdout; stale-worktree:stdout; unrecorded-gitfile:stdout
S44 1 prunable-down:rc 1->0,stdout
S58 4 json-sibling-prefix, json-mode, json-unicode-name, json-relative: json-content/mode
```
Full per-mutant lists are in `probes-run.log`. Scenario-level outcomes for the 17 non-equivalent survivors are in section 4.

**2e. Joined table and counts** (`python3 -B report_table.py`):
```
COUNTS mutants=77 killed_by_landed=10 landed_only=1 prior_only=33 survived_all_nine=34 equivalent=17 non_equivalent=17 (no_deterministic_probe=1)
```

**2f. C3 counter at the tip** (`python3 -B census/round-42/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 3105a63b23481fccf7df58e74d14a6681e0ea0c8 --scratch /fast/scratch/hyaku/souji-r42/R42w2critic04`; exit 0; log `c3-counter-tip-run.log`):
```
SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247
```

**2g. Overlap with the frozen tables** (Python import of `c3-counter.py` MUTANTS + EQUIV, compared with `mutants.py`):
```
survey mutants: 77 exact duplicates of frozen (old,new): []
survey mutants sharing an anchor with a frozen mutant (different new text): [('S66', 'os.ftruncate(fd, 0)'), ('S70', 'if args.timeout < 1:')]
```

**2h. gitdir and prune mechanics** (scratch repositories, git 2.56.0, `env -i` with the tool's child variables; used to classify S35, S39 and S42):
```
FIFO as .git/HEAD:                   rev-parse rc=124 (5 s timeout); worktree list rc=124
FIFO as worktrees/x/gitdir:          worktree list rc=124; worktree prune --dry-run rc=124
FIFO as worktrees/x/locked:          worktree list rc=124; worktree prune --dry-run rc=0
FIFO as the worktree's own .git:     worktree list rc=0; worktree prune --dry-run rc=0
.git file -> symlink (leaf), symlink directory component, relative gitdir:
    rev-parse --absolute-git-dir prints the resolved path (.../outside/gd, .../outside/gd2), rc=0 each
```
Tool installs: none. Lane writes: none (only read-only `git show`; all fixtures and probes under scratch; seat outputs in the seat directory).

## 3. What the landed fixture does and does not kill

- Among the 77 survey mutants, the landed fixture's unique kill is S64 (the `--json` envelope loses its `summary` key), caught by `case-longer-old-json-is-truncated-on-write`. Its other 9 kills (S02, S27, S31, S32, S36, S37, S38, S49, S72) are also killed by at least one prior fixture.
- The 33 mutants killed only by prior fixtures are fully covered by prior fixtures and are not limits of the landed fixture.
- The landed fixture was written for the 13-mutant population, which is what the counter measures. Its coverage of the wider condition space is narrow (section 4).

## 4. Named coverage limits: non-equivalent survivors of all nine fixtures (r43 population)

Tool lines are for `tools/souji-worktree-drift.py` at the tip. "Pristine → mutant" gives the outcome from `probes-results.json`.

| id | tool line | change | probe scenario | pristine → mutant |
|---|---|---|---|---|
| S03 | 147 (read loop 143–147) | record read stops after the first 64 KiB chunk | `big-3000` (3000 REPO rows) | rc 1 (3000 DRIFT ABSENT rows) → rc 2 `RECORD-MALFORMED: line 2260` |
| S11 | 89 | TOTAL regex loses its end anchor | `total-junk` (`prunable=0x`) | rc 2 MALFORMED → rc 0 |
| S12 | 88 | REPO name excludes spaces | `space-name` (`my repo`) | rc 0 → rc 2 MALFORMED |
| S13 | 88 | REPO regs accepts an empty field | `empty-regs` (`regs=`) | rc 2 MALFORMED → rc 1 uncaught `ValueError` |
| S17 | 181 | TOTAL prunable compared one-sidedly (`>`) | `total-prunable-small` | rc 2 MALFORMED → rc 1 (PRUNABLE-CHANGED) |
| S22 | 212 | root-as-repo match skips the root `.git` test | `root-not-repo-named` | DRIFT ABSENT root → DRIFT UNREACHABLE root `list-rc=128` |
| S25 | 220–222 | unreadable root raises instead of returning no names | `root-unreadable` (chmod 000) | DRIFT ABSENT r, rc 1 → uncaught `PermissionError`, rc 1 |
| S33 | 287 | `root_real` not realpath-resolved | `root-symlink` (`--root` through a symlink) | rc 0 → rc 2 RECORD-OUTSIDE-ROOT |
| S34 | 284 | `--root` not abspath-resolved | `rel-root-named` (`--root .`, root named by its basename) | rc 0 → rc 1 DRIFT ABSENT root |
| S34 | 284 | (same) | `rel-root-discover` | `UNRECORDED root` → `UNRECORDED .` |
| S35 | 307 | gitdir probe ignores `--timeout` (fixed 20 s) | `timeout-fifo-head` (`--timeout 1`, FIFO HEAD) | fast (<10 s) → not fast (about 20 s); same stdout |
| S42 | 201 | prune-timeout re-raised instead of reported | none deterministic (section 2h shows the list call blocks first on every input prune reads) | race only |
| S43 | 373 | REGS-CHANGED one-sided (`<`) | `regs-up` (record 1, live 2) | rc 1 REGS-CHANGED → rc 0 |
| S44 | 375 | PRUNABLE-CHANGED one-sided (`>`) | `prunable-down` (record 1, live 0) | rc 1 PRUNABLE-CHANGED → rc 0 |
| S53 | 344 | `--json` guard uses commonprefix | `json-sibling-prefix` (`rootX` beside `root`) | rc 0, file written → rc 2 JSON-INSIDE-MEASURED-TREE |
| S58 | 264 | `--json` created mode 0600 | `json-mode` | 0o644 → 0o600 |
| S63 | 320 | `--json ''` treated as set | `json-empty` | rc 0 → rc 2 JSON-NOT-REGULAR (cwd) |
| S73 | 443 | `--timeout` parsed as float | `timeout-float` (`--timeout 1.5`) | rc 2 argparse "invalid int value" → rc 0 |

Named limits for the r43 population: the 16 with a probe in this table, and S42 as a race-only limit that needs a race-tolerant harness.

The 17 equivalent survivors (S18, S19, S28, S29, S30, S39, S41, S51, S65, S66, S67, S68, S69, S74, S75, S76, S77) are listed with reasons in the table in section 5.

## 5. Findings for the L1 (reported, not edited)

- **F1 (coverage, C3):** The landed fixture adds one unique kill among 77 survey mutants (S64). The 17 non-equivalent survivors in section 4 are the coverage limits for r43.
- **F2 (harness):** Under S64 the prior fixture `r38-drift-write-envelope.py` exits through a Python traceback (`matrix.json`, crash=true). The counter's kill rule therefore records no kill for it. The frozen counter is not changed.
- **F3 (name hygiene):** S34's description in `mutants.py` was edited after the matrix run to replace a wrong pre-run guess ("equivalent") with the measured result. The table uses the corrected text. No measurement depends on the text.

## 6. Scope limits and caveats

- **S42 is race-only.** Every deterministic input I built makes `worktree list` (which runs first) block on exactly what `prune --dry-run` reads. The prune-timeout branch is therefore unreachable by a deterministic probe. It is classed non-equivalent because a timing race distinguishes it, with no deterministic probe.
- **S39 is equivalent on git 2.56.0** only: `rev-parse --absolute-git-dir` already resolves the gitdir (section 2h). A git version that returned an unresolved path would make S39 non-equivalent, and the `gitdir-symlink` scenario would then differ.
- **S75 (`GIT_CONFIG_GLOBAL`), S76 (`GIT_OPTIONAL_LOCKS`), S77 (`GIT_ATTR_NOSYSTEM`)** are equivalent by argument (whitelisted child environment without HOME or XDG; `--no-optional-locks` also passed; worktree list and prune consult no attributes; no `/etc/gitattributes` on this host). No scenario observes them.
- **S28, S29, S30, S41, S51, S65, S66, S69** are equivalent by code argument plus no difference across the 46 scenarios.
- The frozen 13-mutant population and its six EQUIV entries were re-scored only by the counter run in section 2f.

## 7. Table (77 mutants)

Killed by: `landed:<failed case>` where the landed fixture kills, `prior:<fixture>` for prior kills, `none` when no fixture kills. Equivalent column: `no (killed)` where a fixture kills it; `equivalent`; or `non-equivalent`.

| mutant | change | killed by (landed / prior / none) | equivalent? | probe |
|---|---|---|---|---|
| S01 | record ENOENT class inverted (missing record reported as RECORD-MISSING) | prior:r38-drift-record,r41-refusal-sites | no (killed) | fixture: prior:r38-drift-record,r41-refusal-sites |
| S02 | regular-file guard on the record removed (fstat check dead) | landed:fifo-record-is-refused-not-blocked prior:r41-refusal-sites | no (killed) | fixture: landed:fifo-record-is-refused-not-blocked; prior:r41-refusal-sites |
| S03 | record read stops after the first 64 KiB chunk | none | non-equivalent | probes: big-3000 = record cut at 64 KiB: rc 1->2 (partial row refused) |
| S04 | comment lines (leading #) no longer skipped | prior:r38-drift-record,r39-drift-record-rules,r40-drift-record-branches,r41-refusal-sites | no (killed) | fixture: prior:r38-drift-record,r39-drift-record-rules,r40-drift-record-branches,r41-refusal-sites |
| S05 | blank lines no longer skipped | prior:r38-drift-record,r41-refusal-sites | no (killed) | fixture: prior:r38-drift-record,r41-refusal-sites |
| S06 | record split on newline only (CR kept on each line) | prior:r39-drift-record-rules | no (killed) | fixture: prior:r39-drift-record-rules |
| S07 | duplicate REPO name check removed | prior:r38-drift-record,r41-refusal-sites | no (killed) | fixture: prior:r38-drift-record,r41-refusal-sites |
| S08 | RECORD-EMPTY check removed (zero REPO rows accepted) | prior:r36-worktree-drift,r38-drift-record,r39-drift-record-rules,r41-refusal-sites | no (killed) | fixture: prior:r36-worktree-drift,r38-drift-record,r39-drift-record-rules,r41-refusal-sites |
| S09 | non-schema record line skipped instead of refused | prior:r36-worktree-drift,r38-drift-record,r39-drift-record-rules,r41-refusal-sites | no (killed) | fixture: prior:r36-worktree-drift,r38-drift-record,r39-drift-record-rules,r41-refusal-sites |
| S10 | REPO row regex: end anchor removed (trailing junk accepted) | prior:r39-drift-record-rules | no (killed) | fixture: prior:r39-drift-record-rules |
| S11 | TOTAL regex: end anchor removed (trailing junk accepted) | none | non-equivalent | probes: total-junk = TOTAL with 'prunable=0x' accepted: rc 2->0 |
| S12 | REPO name excludes spaces (names with a space refused as malformed) | none | non-equivalent | probes: space-name = REPO name with a space refused: rc 0->2 |
| S13 | REPO regs accepts an empty field (int of empty string) | none | non-equivalent | probes: empty-regs = 'regs=' empty field: rc 2->1 (uncaught ValueError traceback) |
| S14 | TOTAL rows collected but never checked | prior:r36-worktree-drift,r38-drift-record,r40-drift-record-branches,r41-drift-record-order,r41-refusal-sites | no (killed) | fixture: prior:r36-worktree-drift,r38-drift-record,r40-drift-record-branches,r41-drift-record-order,r41-refusal-sites |
| S15 | TOTAL repos compared with > (a TOTAL smaller than the row count accepted) | prior:r40-drift-record-branches,r41-drift-record-order | no (killed) | fixture: prior:r40-drift-record-branches,r41-drift-record-order |
| S16 | TOTAL regs compared with < (a TOTAL larger than the row sum accepted) | prior:r38-drift-record,r41-drift-record-order,r41-refusal-sites | no (killed) | fixture: prior:r38-drift-record,r41-drift-record-order,r41-refusal-sites |
| S17 | TOTAL prunable compared with > (a TOTAL smaller than the row sum accepted) | none | non-equivalent | probes: total-prunable-small = TOTAL prunable smaller than the row sum accepted: rc 2->1 |
| S18 | parse_record returns None for the TOTAL (run never reads it) | none | equivalent | probes: no difference in 46 scenarios \| return value of parse_record's TOTAL is never read by run() |
| S19 | record read chunk size 1 byte (performance only) | none | equivalent | probes: no difference in 46 scenarios \| 1-byte reads concatenate to the same bytes (big-3000 identical) |
| S20 | repo_path ignores .git files (linked worktrees) | prior:r36-worktree-drift,r37-drift-discrimination | no (killed) | fixture: prior:r36-worktree-drift,r37-drift-discrimination \| probes differ on: unrecorded-gitfile,record-gitfile |
| S21 | repo_path root-name match inverted | prior:r41-drift-record-order | no (killed) | fixture: prior:r41-drift-record-order |
| S22 | repo_path root-name match skips the root .git test | none | non-equivalent | probes: root-not-repo-named = root named by its basename, not a repo: ABSENT becomes UNREACHABLE |
| S23 | discovery: .git files not discovered (linked worktrees invisible to UNRECORDED) | prior:r36-worktree-drift,r37-drift-discrimination | no (killed) | fixture: prior:r36-worktree-drift,r37-drift-discrimination \| probes differ on: unrecorded-gitfile |
| S24 | discovery: the root itself is never reported as a repository | prior:r41-drift-record-order | no (killed) | fixture: prior:r41-drift-record-order \| probes differ on: rel-root-discover,unrecorded-root-repo |
| S25 | discovery: unreadable root raises instead of returning no names | none | non-equivalent | probes: root-unreadable = unreadable root: DRIFT ABSENT becomes a traceback (stdout lost) |
| S26 | discovery: recorded repositories also reported UNRECORDED | prior:r36-worktree-drift,r37-drift-discrimination,r38-drift-record,r38-drift-write-envelope,r39-drift-record-rules,r41-drift-record-order | no (killed) | fixture: prior:r36-worktree-drift,r37-drift-discrimination,r38-drift-record,r38-drift-write-envelope,r39-drift-record-rules,r41-drift-record-order |
| S27 | skip-unrecorded flag inverted (discovery skipped by default) | landed:invalid-utf8-in-record-becomes-replacement-char,symlinked-child-is-not-discovered prior:r36-worktree-drift,r37-drift-discrimination,r40-drift-record-branches,r41-drift-record-order | no (killed) | fixture: landed:invalid-utf8-in-record-becomes-replacement-char,symlinked-child-is-not-discovered; prior:r36-worktree-drift,r37-drift-discrimination,r40-drift-record-branches,r41-drift-record-order |
| S28 | discovery order unsorted (drift is re-sorted on output: equivalent) | none | equivalent | probes: no difference in 46 scenarios \| discovery order is erased: drift is sorted before printing |
| S29 | root repository name appended, not inserted first (drift re-sorted: equivalent) | none | equivalent | probes: no difference in 46 scenarios \| root-name position is erased by the same sort |
| S30 | discovered repository check for an existing .git: the isdir guard dropped (equivalent) | none | equivalent | probes: no difference in 46 scenarios \| a .git entry implies a directory, so the isdir guard is redundant |
| S31 | discovery: directories filter inverted (only non-directories considered) | landed:symlinked-child-is-not-discovered prior:r36-worktree-drift,r37-drift-discrimination,r40-drift-record-branches | no (killed) | fixture: landed:symlinked-child-is-not-discovered; prior:r36-worktree-drift,r37-drift-discrimination,r40-drift-record-branches |
| S32 | row path resolved without realpath (symlinked row escapes --root by name) | landed:root-sibling-prefix-is-outside prior:r38-drift-write-envelope,r39-drift-record-rules,r41-refusal-sites | no (killed) | fixture: landed:root-sibling-prefix-is-outside; prior:r38-drift-write-envelope,r39-drift-record-rules,r41-refusal-sites |
| S33 | root_real without realpath (a symlinked --root refuses every row) | none | non-equivalent | probes: root-symlink = symlinked --root refuses every row: rc 0->2 RECORD-OUTSIDE-ROOT |
| S34 | relative --root not abspath-resolved (pre-run guess: equivalent; measured non-equivalent, basename of '.') | none | non-equivalent | probes: rel-root-named = --root . names the root repo '.', not its basename: rc 0->1 ABSENT |
| S35 | gitdir probe ignores --timeout (fixed 20 s) | none | non-equivalent | probes: timeout-fifo-head = --timeout ignored by the gitdir probe: fast (<10 s) becomes slow (~20 s) |
| S36 | gitdir return code test inverted (gitdir only read when rev-parse fails) | landed:gitdir-sibling-prefix-is-outside,list-nonzero-rc-is-reported-unreachable prior:r37-drift-discrimination,r41-refusal-sites | no (killed) | fixture: landed:gitdir-sibling-prefix-is-outside,list-nonzero-rc-is-reported-unreachable; prior:r37-drift-discrimination,r41-refusal-sites |
| S37 | gitdir return code test dropped (failed rev-parse still containment-tested) | landed:list-nonzero-rc-is-reported-unreachable prior:r37-drift-discrimination | no (killed) | fixture: landed:list-nonzero-rc-is-reported-unreachable; prior:r37-drift-discrimination |
| S38 | gitdir containment not enforced | landed:gitdir-sibling-prefix-is-outside prior:r41-refusal-sites | no (killed) | fixture: landed:gitdir-sibling-prefix-is-outside; prior:r41-refusal-sites |
| S39 | gitdir not realpath-resolved (symlinked gitdir escapes --root unseen) | none | equivalent | probes: gitdir-symlink identical \| git 2.56 rev-parse --absolute-git-dir already returns the resolved gitdir (gitdir-symlink identical) |
| S40 | measure: prune stdout counted instead of stderr | prior:r36-worktree-drift,r37-drift-discrimination | no (killed) | fixture: prior:r36-worktree-drift,r37-drift-discrimination \| probes differ on: stale-worktree |
| S41 | measure: worktree line test without the trailing space (equivalent on porcelain grammar) | none | equivalent | probes: no difference in 46 scenarios \| porcelain worktree lines are the only lines beginning 'worktree' |
| S42 | measure: prune-timeout re-raised instead of reported UNREACHABLE | none | non-equivalent (race only) | none deterministic: prune-timeout re-raise needs prune to block where list does not; none found |
| S43 | drift: REGS-CHANGED only when live count is lower | none | non-equivalent | probes: regs-up = record 1, live 2: REGS-CHANGED dropped, rc 1->0 |
| S44 | drift: PRUNABLE-CHANGED only when live count is higher | none | non-equivalent | probes: prunable-down = record prunable 1, live 0: PRUNABLE-CHANGED dropped, rc 1->0 |
| S45 | drift class token misspelt (REGS-CHANGD) | prior:r36-worktree-drift,r37-drift-discrimination,r41-drift-record-order | no (killed) | fixture: prior:r36-worktree-drift,r37-drift-discrimination,r41-drift-record-order |
| S46 | summary: live_repos never incremented | prior:r36-worktree-drift,r37-drift-discrimination,r38-drift-write-envelope,r41-drift-record-order | no (killed) | fixture: prior:r36-worktree-drift,r37-drift-discrimination,r38-drift-write-envelope,r41-drift-record-order |
| S47 | summary: live_regs overwritten, not accumulated | prior:r36-worktree-drift,r37-drift-discrimination | no (killed) | fixture: prior:r36-worktree-drift,r37-drift-discrimination |
| S48 | summary: unreachable count not incremented | prior:r37-drift-discrimination | no (killed) | fixture: prior:r37-drift-discrimination |
| S49 | the record-alias check: stat failure treated as alias (new --json files refused) | landed:invalid-utf8-in-record-becomes-replacement-char prior:r36-worktree-drift,r38-drift-write-envelope,r41-refusal-sites | no (killed) | fixture: landed:invalid-utf8-in-record-becomes-replacement-char; prior:r36-worktree-drift,r38-drift-write-envelope,r41-refusal-sites |
| S50 | the record-alias inode check dropped (hardlink to the record allowed) | prior:r38-drift-write-envelope | no (killed) | fixture: prior:r38-drift-write-envelope \| probes differ on: alias-hardlink-record |
| S51 | record path not realpath-resolved in the alias check (equivalent: inode check still fires) | none | equivalent | probes: no difference in 46 scenarios \| inode check in the alias test still fires for a symlinked record (json-is-record-symlink identical) |
| S52 | JSON-IS-RECORD refusal removed | prior:r38-drift-write-envelope,r41-refusal-sites | no (killed) | fixture: prior:r38-drift-write-envelope,r41-refusal-sites |
| S53 | json guard: commonprefix instead of commonpath (sibling prefix counted inside) | none | non-equivalent | probes: json-sibling-prefix = --json in sibling rootX counted inside root: rc 0->2 |
| S54 | JSON-INSIDE-MEASURED-TREE refusal removed | prior:r36-worktree-drift,r38-drift-write-envelope,r41-refusal-sites | no (killed) | fixture: prior:r36-worktree-drift,r38-drift-write-envelope,r41-refusal-sites \| probes differ on: json-inside-root,json-under-root-nonrepo |
| S55 | measured list without the root (JSON under --root but outside any repository allowed) | prior:r41-refusal-sites | no (killed) | fixture: prior:r41-refusal-sites \| probes differ on: json-inside-root,json-under-root-nonrepo |
| S56 | --json target not realpath-resolved (symlink to a measured path accepted) | prior:r38-drift-write-envelope | no (killed) | fixture: prior:r38-drift-write-envelope |
| S57 | hardlink refusal threshold: more than two links allowed | prior:r38-drift-write-envelope,r41-refusal-sites | no (killed) | fixture: prior:r38-drift-write-envelope,r41-refusal-sites \| probes differ on: json-hardlink-outside |
| S58 | --json file created mode 0600 instead of 0644 | none | non-equivalent | probes: json-mode = --json file mode 0600 instead of 0644 (mode differs) |
| S59 | --json open without O_NONBLOCK (a FIFO with no reader blocks) | prior:r38-drift-write-envelope,r41-refusal-sites | no (killed) | fixture: prior:r38-drift-write-envelope,r41-refusal-sites |
| S60 | --json fstat regular-file test removed | prior:r38-drift-write-envelope,r41-refusal-sites | no (killed) | fixture: prior:r38-drift-write-envelope,r41-refusal-sites |
| S61 | EISDIR not mapped to JSON-NOT-REGULAR | prior:r38-drift-write-envelope,r41-refusal-sites | no (killed) | fixture: prior:r38-drift-write-envelope,r41-refusal-sites |
| S62 | JSON write OSError re-raised unwrapped (traceback, no REFUSAL) | prior:r38-drift-write-envelope,r41-refusal-sites | no (killed) | fixture: prior:r38-drift-write-envelope,r41-refusal-sites |
| S63 | --json empty string treated as set | none | non-equivalent | probes: json-empty = --json '' treated as a path (cwd): rc 0->2 JSON-NOT-REGULAR |
| S64 | --json envelope loses its summary key | landed:longer-old-json-is-truncated-on-write | no (killed) | fixture: landed:longer-old-json-is-truncated-on-write |
| S65 | --json write encoding ascii (ensure_ascii output: equivalent) | none | equivalent | probes: no difference in 46 scenarios \| json.dump defaults to ensure_ascii, so the output is ASCII under either encoding |
| S66 | --json truncate to one byte before write (write restores the length: equivalent) | none | equivalent | probes: no difference in 46 scenarios \| a 1-byte truncate is followed by a write that sets the length (json-overwrite-long identical) |
| S67 | --json written without trailing newline (bytes only: equivalent) | none | equivalent | probes: bytes only \| bytes only: the trailing newline; parsed JSON identical (json-bytes-only) |
| S68 | --json indent removed (bytes only: equivalent) | none | equivalent | probes: bytes only \| bytes only: indentation; parsed JSON identical (json-bytes-only) |
| S69 | open_nofollow: absolute-path guard weakened (equivalent: json target is always realpath) | none | equivalent | probes: no difference in 46 scenarios \| json_target is always absolute (realpath of abspath) |
| S70 | --timeout accepts zero | prior:r41-refusal-sites | no (killed) | fixture: prior:r41-refusal-sites |
| S71 | USAGE refusal exits 1, not 2 | prior:r41-refusal-sites | no (killed) | fixture: prior:r41-refusal-sites |
| S72 | refusal exits 0, not 2 | landed:fifo-record-is-refused-not-blocked,gitdir-sibling-prefix-is-outside,root-sibling-prefix-is-outside prior:r36-worktree-drift,r38-drift-record,r38-drift-write-envelope,r39-drift-record-rules,r40-drift-record-branches,r41-drift-record-order,r41-refusal-sites | no (killed) | fixture: landed:fifo-record-is-refused-not-blocked,gitdir-sibling-prefix-is-outside,root-sibling-prefix-is-outside; prior:r36-worktree-drift,r38-drift-record,r38-drift-write-envelope,r39-drift-record-rules,r40-drift-record-branches,r41-drift-record-order,r41-refusal-sites |
| S73 | --timeout parsed as float (1.5 accepted) | none | non-equivalent | probes: timeout-float = --timeout 1.5 accepted: argparse rc 2 -> 0 |
| S74 | REFUSAL line without newline (text only: equivalent) | none | equivalent | probes: stderr text only \| stderr text only: the trailing newline of the REFUSAL line (stderr-text-only; class token kept) |
| S75 | child git environment: GIT_CONFIG_GLOBAL dropped (equivalent under the whitelist: no HOME) | none | equivalent | argument only (env whitelist); no scenario can observe it \| whitelisted child env has no HOME/XDG, so no global config can be read either way |
| S76 | child git environment: GIT_OPTIONAL_LOCKS dropped (equivalent: --no-optional-locks is also passed) | none | equivalent | argument only (env whitelist); no scenario can observe it \| --no-optional-locks is also passed, so the env variable is redundant |
| S77 | child git environment: GIT_ATTR_NOSYSTEM dropped (equivalent on a host with no system gitattributes) | none | equivalent | argument only (env whitelist); no scenario can observe it \| worktree list/prune consult no attributes; no /etc/gitattributes on this host |

## 8. Counts

- Mutants: 77 (S01–S77). Survey mutants are new and do not repeat the frozen ids.
- Killed by the landed fixture: 10 (landed-only: 1, S64).
- Killed by prior fixtures only (landed does not kill): 33. Killed by prior fixtures in total: 42.
- Killed by none (survive all nine): 34.
- Survivors of all nine, equivalent: 17 (11 by code argument plus scenario equality; 2 bytes-only S67 S68; 1 stderr-text-only S74; 3 unobservable under the child-environment whitelist S75 S76 S77).
- Survivors of all nine, non-equivalent: 17 (16 with a deterministic probe; 1 race-only, S42).
- Frozen C3 target at the tip: `SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok` (exit 0).
- Verdict: the landed C3 fixture meets its frozen target but leaves 17 non-equivalent condition-level survivors (16 deterministic) as named coverage limits for r43.
