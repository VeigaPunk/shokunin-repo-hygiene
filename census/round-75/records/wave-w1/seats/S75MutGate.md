# S75MutGate — W gate r75 C1 block (rev 1ad737b) mutation test
BLIND (all re-hashed): gate 620ed97e…, writer 70bbf1c2…, counter 9ed4a97b…, pop 85257260…, probe 09e18d8a…; gate@base 062b6d39….
C1 on W blob: `SUMMARY rows=25 mismatches=0 errors=0` EXIT=0 (c1-after.txt reproduced). K-a replay: `mismatches=2` [f-info-exclude f5-info-exclude-dir] EXIT=1; K-b blanket replay: `mismatches=3` [f2 f6 f7] EXIT=1. 2->0 and blanket-red hold.
Mutants: 15 single-edit (each 1–2 hunks vs pristine, once-only substitution asserted); 9 KILLED, 6 SURVIVED.
| id | edit | SUMMARY | verdict |
|---|---|---|---|
| W01 | swap subtraction operands | mismatches=2 | KILLED |
| W02 | `if hidden:` -> `if not hidden:` | mismatches=7 | KILLED |
| W03 | drop `--ignored` | mismatches=2 | KILLED |
| W04 | drop `--others` | mismatches=5 | KILLED |
| W05 | call1 standard -> per-directory | mismatches=2 | KILLED |
| W06 | call2 per-directory -> standard | mismatches=2 | KILLED |
| W07 | rc!=0 -> `return set()` | mismatches=0 EXIT=0 | SURVIVED |
| W08 | `sys.exit(1)` -> `sys.exit(0)` on hidden | mismatches=2 | KILLED |
| W09 | block moved before witness/truth loop | mismatches=0 EXIT=0 | SURVIVED |
| W10 | drop `-z`, split on `\n` | mismatches=0 EXIT=0 | SURVIVED |
| W11 | drop `-c core.fsmonitor=false` | mismatches=0 EXIT=0 | SURVIVED |
| W12 | `-C lane` -> `-C "."` | mismatches=2 | KILLED |
| W13 | refusal token renamed | mismatches=0 EXIT=0 | SURVIVED |
| W14 | rc!=0 -> message + `sys.exit(0)` | mismatches=0 EXIT=0 | SURVIVED |
| W15 | `-` -> `|` (union) | mismatches=3 | KILLED |
HIGH F1 regression: W gate reds the documented r36 fixture — `SUMMARY cases=21 pass=17 fail=4` EXIT=1 vs base gate `pass=21 fail=0` EXIT=0 (SKILL.md:258 freezes 21/21). Failing cases are exactly the four rc=0 cases; every one prints `detail-clean: byte truth: RECEIPT-UNTRACKED-LOCAL-EXCLUDE: 1 untracked path(s)…`. Cause: the fixture hides its untracked `tools` symlink in `.git/info/exclude` (tests/fixtures/r36-report-gate.py:125-131, called for every case at :302); the new rule calls that forgery. Not covered by the stated f7 limit; no r75 r27/r36 receipt exists.
MEDIUM F2 f3-repo-excludesfile is a pass-through, not evidence for the new block: `clean=FAIL match=yes` at the base gate without the block (K-a) and byte-identical in all 15 mutant runs. The refusal is the writer's pinned excludesFile (`core.excludesFile={os.devnull}`, tools/souji-receipt-write.py:160), which fires before the heredoc block (gate:80 truth loop precedes gate:98); repro on both gates prints `pinned git status (core.fsmonitor=false, core.fileMode=true) lists 1 record(s)`. The core.excludesFile arm of the claim has no counter evidence.
MEDIUM F3 fail-open rc branch unmeasured: W07/W14 survive because no route makes `ls-files` fail (the branch at gate:94-96 becomes a silent accept). Injections tried (chmod-000 info/exclude, chmod-000 core.excludesFile, core.excludesFile=directory) all fail earlier at the outer `git status` (rc=128 or dirty), so no exploit was demonstrated; the branch remains fail-open.
LOW F4 detector reads only `check-clean=`: refusal class (W13) and block ordering (W09) are unmeasured — this is exactly why F2 stayed invisible. Equivalent survivors: W10 (git's non-`-z` output always C-quotes control chars; a newline path prints as `"a\nb"` even with core.quotePath=false, so both listings stay comparable and both gates still FAIL that fixture) and W11 (`ls-files` output identical with and without the fsmonitor pin under a repo hook).
Regressions: r27 @ W gate `cases=4 pass=4 control=FALSE-GREEN-REJECTED` EXIT=0 PASS. r36 @ W gate 17/21 EXIT=1; same fixture @ base gate 21/21 EXIT=0 (see HIGH F1).
Commands: `git show 1ad737b…:tools/souji-pre-report-gate.sh` and `…:tools/souji-receipt-write.py` into one dir D; `python3 -B census/round-75/c1-evade-counter.py --gate-dir D --work <empty>`; mutants: `python3 -B <seat>/build-mutants.py` then counter per `gates/<id>`; `env TMPDIR=<scratch> bash tests/fixtures/r27-pre-report-gate.sh`; `python3 -B tests/fixtures/r36-report-gate.py --work <scratch>` (and `--gate <base copy>`); replay commands are the `command=` line of each receipt.
Restoration: pristine gate/writer digests 620ed97e/70bbf1c2 unchanged before/after all mutants; final pristine re-run `mismatches=0 errors=0` EXIT=0. No lane file written; lane worktree shows only peers' pre-existing `M corpus/SOURCES.md`, `M corpus/knowledge/filter-filemode-witness.md`, `?? corpus/lessons/round-75.md`.
C2 selftest kills (X09, P1): not exercised by this seat — outside its target, owned by the C2 mutant seats.
Files written: .ufo/waves/round-75/w1/S75MutGate.md; .ufo/waves/round-75/w1/S75MutGate/mutants.tsv; .ufo/waves/round-75/w1/S75MutGate/build-mutants.py; .ufo/waves/round-75/w1/S75MutGate/receipts/{W01…W15}.txt and {pristine,replay-base,replay-Kb,pristine-restore,regress-r27-W,regress-r36-W,regress-r36-base,f3-repro-base,f3-repro-pristine,w10-newline-both,rc-injections,fsmonitor-pin}.txt.
Tool installs: none.
