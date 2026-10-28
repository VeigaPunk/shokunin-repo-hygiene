# R40w2simplifier03 — YAGNI review of the landed C3 fixture and counter

Role: simplifier (leaf, read-only on the lane). Judged on: coverage.
Landed revision: `128e412b0ced3c243dc27c3dd3332054a611bc2e`. Base: `0242085909fb6a4ee041c5443d76316ac6d59d4b`.
The lane HEAD has since moved to `549d9ec`; every C3 byte below was read at the landed revision (`git show` / `git archive`), not from the working tree.

Landed bytes (sha256, first 12 hex):
- `tools/souji-worktree-drift.py` e48ed08e6728 (unchanged by round 40)
- `tests/fixtures/r40-drift-record-branches.py` a6ec36f0ce9e (150 lines)
- `tests/fixtures/r39-drift-record-rules.py` 567c37a679f5 (141 lines)
- `census/round-40/c3-counter.py` 7bdde9f6b205 (211 lines)

## Verdict

- **Simplification premise ("every landed case is load-bearing and every counter arm can fail"): FALSIFIED.** Two removable items with evidence:
  1. Fixture case `skip-unrecorded-suppresses` (`tests/fixtures/r40-drift-record-branches.py:110-111`) is the same invocation as `good` (`:100-101`), with fewer expected tokens. Dropping it changes no kill (leave-one-out below). Dropping it also trips the counter's own size floor, so it cannot be removed alone (see gate run).
  2. Counter `crash` term (`census/round-40/c3-counter.py:115`, used at `:118`) never evaluates True: `crash=False` in every run, including a tool that raises on every invocation.
- **C3 predicate (declared kills, pristine pass, base survival): SAFE** on the landed bytes. The counter reports `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8`.
- Single-case deletions that are *not* candidates: `total-conflicting-second`, `total-repos-disagrees`, `invalid-utf8-in-repo-name`, `unrecorded-without-flag`, `total-duplicate-identical`, `good` (reasons below).

## Commands and real output

Setup (scratch removed at the end; see last section):
```
S=/fast/scratch/hyaku/souji-r40/w2/R40w2simplifier03; LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
R=128e412b0ced3c243dc27c3dd3332054a611bc2e; B=0242085909fb6a4ee041c5443d76316ac6d59d4b
mkdir -p "$S/c3" "$S/landed" "$S/work"
git -C "$LANE" archive --format=tar "$R" | tar -x -C "$S/landed"
git -C "$LANE" rev-parse --verify -q "$R^{commit}"
sha256sum tools/souji-worktree-drift.py tests/fixtures/r40-drift-record-branches.py tests/fixtures/r39-drift-record-rules.py census/round-40/c3-counter.py   # run inside $S/landed
```
Output: `128e412b0ced3c243dc27c3dd3332054a611bc2e` (resolves); sha values as listed above.

### 1. Real counter at the landed revision (read-only on the lane)
```
python3 -B "$LANE/census/round-40/c3-counter.py" --root "$LANE" --rev "$R" --base-rev "$B" --scratch "$S/c3"; echo rc=$?
```
```
MUTANT M15 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-conflicting-second base:rc=0 fails=0 crash=False failing=-
MUTANT M16 killed=yes base_killed=no rc=1 fails=4 crash=False failing=good,total-duplicate-identical,skip-unrecorded-suppresses,invalid-utf8-in-comment base:rc=0 fails=0 crash=False failing=-
MUTANT M17 killed=yes base_killed=no rc=1 fails=1 crash=False failing=invalid-utf8-in-repo-name base:rc=0 fails=0 crash=False failing=-
MUTANT M18 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-repos-disagrees base:rc=0 fails=0 crash=False failing=-
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e
rc=0
```
(The same output was reproduced from a `git` fixture repo whose commit is the landed bytes; `failing=` attribution was empty in one earlier control run and non-empty in all later runs — see Anomalies.)

### 2. Leave-one-case-out kill matrix (undeclared probes added)
Driver: `.ufo/waves/round-40/w2/R40w2simplifier03-loo-driver.py` (copied out of scratch; sha256 `aa231f9227df…562dd26`). It imports the landed fixture and counter as modules, runs the fixture's own `run_cases` with one case filtered, and applies the four declared mutants (`c3.MUTANTS`) plus probes P1, P2, P3, P6, P7 (all undeclared; each is a branch behaviour the fixture docstring claims to cover):
- P1 inverted skip (`if args.skip_unrecorded:`), P2 strict decode, P3 refuse any second TOTAL, P6 never scan (`if False:`), P7 tool that raises on every run.

Command: `python3 -B "$S/driver.py"` (driver expects `$S/landed` from the setup above).
```
CASES_IN_FULL_FIXTURE=8 names=good,total-duplicate-identical,total-conflicting-second,total-repos-disagrees,skip-unrecorded-suppresses,unrecorded-without-flag,invalid-utf8-in-repo-name,invalid-utf8-in-comment
pristine: SURVIVED failing=[]
M15                          KILLED    failing=total-conflicting-second
M16                          KILLED    failing=good,total-duplicate-identical,skip-unrecorded-suppresses,invalid-utf8-in-comment
M17                          KILLED    failing=invalid-utf8-in-repo-name
M18                          KILLED    failing=total-repos-disagrees
P1-inverted-skip             KILLED    failing=good,total-duplicate-identical,skip-unrecorded-suppresses,unrecorded-without-flag,invalid-utf8-in-comment
P2-strict-decode             KILLED    failing=invalid-utf8-in-repo-name,invalid-utf8-in-comment
P3-refuse-any-second-total   KILLED    failing=total-duplicate-identical
P6-never-scan                KILLED    failing=unrecorded-without-flag
P7-tool-always-raises        KILLED    failing=good,total-duplicate-identical,total-conflicting-second,total-repos-disagrees,skip-unrecorded-suppresses,unrecorded-without-flag,invalid-utf8-in-repo-name,invalid-utf8-in-comment
== leave-one-case-out (K=killed, S=survived)
drop good                       pristine=SURVIVED  kill changes vs full: none
drop total-duplicate-identical  pristine=SURVIVED  kill changes vs full: P3-refuse-any-second-total:KILLED->SURVIVED
drop total-conflicting-second   pristine=SURVIVED  kill changes vs full: M15:KILLED->SURVIVED
drop total-repos-disagrees      pristine=SURVIVED  kill changes vs full: M18:KILLED->SURVIVED
drop skip-unrecorded-suppresses pristine=SURVIVED  kill changes vs full: none
drop unrecorded-without-flag    pristine=SURVIVED  kill changes vs full: P6-never-scan:KILLED->SURVIVED
drop invalid-utf8-in-repo-name  pristine=SURVIVED  kill changes vs full: M17:KILLED->SURVIVED
drop invalid-utf8-in-comment    pristine=SURVIVED  kill changes vs full: none
```
Reading: "pristine=SURVIVED" means the pristine tool produced no failing case (the driver's label for "not killed"). The driver's full-fixture failing lists match the real counter's lists for M15–M18 exactly.

### 3. The size floor blocks any deletion that is made alone
Fixture repo (scratch, `git -C "$F"` with `rev-parse --show-toplevel` verified before the first commit): commit `C1 = 6105df11` is the landed bytes; commit `C2 = 4aded8f9` removes the 2-line call at fixture `:110-111` (`skip-unrecorded-suppresses`), reparsed with `ast.parse` first.
```
python3 -B "$LANE/census/round-40/c3-counter.py" --root "$F" --rev "$C2" --base-rev "$C1" --scratch "$S/c3b"; echo rc=$?
SUMMARY mutants=0 killed=0 survived=0 pristine=FAIL base_killed=0 cases=7
rc=1
```
The gate is `cases >= 8` at `c3-counter.py:179`. Any fixture case removal therefore fails the counter before mutants are scored. (An earlier attempt I made to build `C2` mis-edited the file and gave `cases=0`; that was my fixture-editing error, not a counter result, and it was replaced by the commit above.)

### 4. The `crash` term cannot fire
Probe P7 (tool raises on every run) through the counter's own `score()`:
```
score(candidate, P7)= (True, 'rc=1 fails=8 crash=False failing=-', 8)
score(base r39, P7)= (True, 'rc=1 fails=7 crash=False failing=-', 7)
```
The fixture `main()` (`tests/fixtures/r40-drift-record-branches.py:126-146`) prints `SUMMARY` only after every case, with no exception path after it, so a Python traceback in the fixture's stderr with a `SUMMARY` line cannot occur. The tool's traceback is captured into each case's `out` (fixture `:87`) and is echoed through the case `detail` on stdout, which the counter correctly never reads for `crash` (`c3-counter.py:99-101`).

### 5. Cross-file duplication check (r39 base fixture, landed bytes)
`tests/fixtures/r39-drift-record-rules.py:88` (`good`, same input and expectation as r40 `good`), `:89-111` (trailing-space, total-before-rows, crlf, outside-root, indented-comment, comments-total-only). The r39 fixture has no duplicate-TOTAL case, no `--skip-unrecorded` case, and no invalid-UTF-8 case, so the r40 additions are new coverage. Its `good` is the same baseline input as r40 `good`; that is expected because each fixture is standalone and needs its own pristine control.

## Candidate deletions and what would break

| # | Item (file:line) | Evidence | What would break | Verdict |
|---|---|---|---|---|
| D1 | fixture `skip-unrecorded-suppresses` (`r40-drift-record-branches.py:110-111`) | Same body, flag, and rc as `good` (`:100-101`); its tokens (`SUMMARY`) are a subset of `good`'s (`SUMMARY`, `record_repos=2`). Drop-one: no kill change. | Alone, the counter's floor fails: `pristine=FAIL cases=7` (section 3). Must land with a `cases >= 8` change (`c3-counter.py:179`) or a replacement distinct case. No declared or probed mutant loses a kill. | Deletion candidate. Lowest-risk removal in the battery. |
| D2 | fixture `invalid-utf8-in-comment` (`:117-120`) | Drop-one: no kill change across M15–M18 and P1/P2/P3/P6/P7. Its M16 kill is duplicated by `good`; its P2 kill is duplicated by `invalid-utf8-in-repo-name`. | Also blocked by the floor. Loses the only pinned check that comment-line invalid bytes are tolerated (fixture docstring `:14-15`). A decode mutant that rejects only comment bytes would survive (not probed). | Low-confidence candidate; a judgement call against a documented behaviour. |
| C1 | counter `crash` term (`c3-counter.py:115`, `:118` `and not crash`) | `crash=False` in every run, including P7 (section 4). Unreachable with the landed fixture. | Nothing today. Only a future fixture that prints `SUMMARY` and also writes a traceback to its stderr would be scored as killed without this term. | Dead arm on landed bytes; deletion candidate. Keep only as a guard for a hypothetical fixture. |
| C2 | counter `pristine_proc.returncode == 0` (`:176`) and `int(match.group(2)) == cases` (`:178`) | Fixture derives `pass` and `fail` from one count (`:143-146`), so given `fail == 0` these cannot fail independently. | Nothing for the landed fixture; they only catch a fixture whose `SUMMARY` and rc disagree with its own count. | Redundant; low value. |
| C3 | counter `failing` attribution (`:116-117`), `tool_sha` / `fixture_sha` (`:151-152`, `:202-204`) | Informational. Not a verdict input. | Attribution and receipts in the output would go away; kill verdicts unchanged. | Keep (named in the r40 repair contract, `:22-27`). |

Not candidates (each is the unique killer of something, so deleting it loses a kill; I checked with drop-one above):
- `total-conflicting-second` — unique killer of M15 (first-wins).
- `total-repos-disagrees` — unique killer of M18 (guard removed). Note `total-conflicting-second` is *not* a substitute: under M18 its regs guard still refuses it.
- `invalid-utf8-in-repo-name` — unique killer of M17 (`ignore` vs `replace`).
- `unrecorded-without-flag` — unique killer of P6 (never-scan). Its docstring pairing claim (`:17-19`) is confirmed for this direction, not for M16 (M16 is killed by `good`).
- `total-duplicate-identical` — unique killer of P3 (refuse any second TOTAL). Only case that checks the identical-duplicate direction the docstring states (`:8-9`).
- `good` — the fixture's own pristine control (no kill is unique to it, but dropping it leaves the suite without its baseline; it also trips the floor).

Counter arms that are load-bearing (confirmed by section 3 and the matrix): the anchor-count check (`:186-190`), the base survival check (`:196`, `:205`), `REV.match` plus `resolves` (`:45`, `:89-93`, `:133-136`), and `returncode == 1` in `killed` (`:118`) as a cross-check of fixture `rc` against its own `fails`.

## Anomalies and disclosures
- HEAD of the lane has moved to `549d9ec`. I did not use HEAD; every check used `128e412b`.
- One earlier control run printed `failing=-` for an identical invocation; three later runs (lane, fixture repo, driver) printed the names. I did not isolate the cause. It affects only the attribution text, not the verdicts. Not reproduced.
- My first attempt to build the dropped-case fixture commit mis-edited the file (a broken commit `016a575`). That was my error, detected by the counter returning `cases=0`. It was discarded; the valid dropped-case commit is `4aded8f9`, and both live only in the scratch fixture repo, which was removed.
- The lane working tree has uncommitted changes from other seats (e.g. `SCORECARD.md`, `census/round-40/c1-counter.py`, `census/round-40/records/`, `census/round-40/waves/`). I did not touch them. Every lane access was read-only (`git show`, `git archive`, `git rev-parse`, `git cat-file`, `git status`).
- Installs: none. No pacman, no `uv`, no `npm`, nothing added to `~/.local/bin`.

## Scratch
Scratch directory `/fast/scratch/hyaku/souji-r40/w2/R40w2simplifier03/` was **removed** (`rm -rf` followed by `test -e`: absent). To re-run section 2, recreate it with the setup commands above and run the copied driver with `S` set to the recreated path.
