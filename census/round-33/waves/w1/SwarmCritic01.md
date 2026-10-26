# SwarmCritic01 — r33 w1, C1 item K01 (fail-closed attack)

## Status
STATUS: PASS — attack executed on all four questions. Item verdict: **LAX-PREDICATE** (predicate component; the
exit conjunct is faithful and load-bearing). K01 reproduces deterministically (4/4 runs, rc=0,
`selftest=PASS 6/6`) at list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 and at tip
fef88f2159f6380a4d1360f73365b3d595973a37, and needs no restatement.

## Evidence

Scratch: `/fast/scratch/hyaku/souji-r33/AuditK01/` (clone `c` = `git clone -q --no-local` of the lane, origin
removed, `rev-parse --show-toplevel` printed the clone, detached at list-rev). Revisions: base
6017a482e7068d5afb7617640198fbb0fe743357; list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46; tip read
fef88f2159f6380a4d1360f73365b3d595973a37.

**E1 — the cell (SCORECARD.md:152 at base, byte-identical at list-rev and tip; `git diff 6017a482 2d9bca55 -- SCORECARD.md`
= 0 lines, `git diff 2d9bca55 HEAD -- SCORECARD.md` = 0 lines):**
```
| maintenance-guard gate | prove on the host git that a plain commit can prune expired unlocked worktree metadata and
that `-c maintenance.auto=false`, `worktree lock` and a fresh index prevent it | `bash
tests/fixtures/r12-maintenance-guard.sh --selftest` → 6/6 PASS, exit 0; `tests/results/r12-maintenance-guard.txt` | r12 |
```
Verbatim (SCORECARD.md:152 at 6017a482, ≤25 words): "`bash tests/fixtures/r12-maintenance-guard.sh --selftest` → 6/6
PASS, exit 0"

**E2 — determinism, 4 runs, clone root, fixture hard-codes /var/tmp so TMPDIR is ignored (fixture
tests/fixtures/r12-maintenance-guard.sh:47):**
```
run1 TMPDIR=$D/t1              rc=0  selftest=PASS ids=6/6   verdict PASS=6 FAIL=0 bytes=587
run2 TMPDIR=$D/t2              rc=0  selftest=PASS ids=6/6   verdict PASS=6 FAIL=0 bytes=587
run3 env -u TMPDIR             rc=0  selftest=PASS ids=6/6   verdict PASS=6 FAIL=0 bytes=587
run4 env -u TMPDIR -u GIT_CONFIG_GLOBAL -u GIT_CONFIG_NOSYSTEM
                               rc=0  selftest=PASS ids=6/6   verdict PASS=6 FAIL=0 bytes=587
diff r1 r2 (minus git_version) = identical; diff r1 r3 = identical; diff r1 r4 = identical
/var/tmp/souji-r12-maintenance.* residue after all runs = 0
```
Per-case lines (identical in all four runs): `plain-commit-sync before=2 after=1 expect=1 verdict=PASS`,
`plain-commit-default before=2 after=1 expect=1 verdict=PASS`, `auto-off 2/2/2 PASS`, `locked 2/2/2 PASS`,
`fresh 2/2/2 PASS`, `maintenance-auto before=2 after=1 expect=1 PASS`; `git_version=git version 2.56.0`.

**E3 — frozen counter, list-rev and tip:**
```
$ python3 -B census/round-33/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --list-rev 2d9bca55… --scratch …/cnt --only K01
ITEM	K01	AGREE	original	rc=0 expect_exit=0 predicate holds last=selftest=PASS ids=6/6
SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46   (rc=0)
$ … --rev fef88f2159f6380a4d1360f73365b3d595973a37 …
ITEM	K01	AGREE	original	rc=0 expect_exit=0 predicate holds last=selftest=PASS ids=6/6   (rc=0)
```

**E4 — the cell's other stated outcomes, re-derived (all current):** prune-on-plain-commit 2→1; `-c
maintenance.auto=false` 2→2; `worktree lock` 2→2; fresh index 2→2 — all as case lines above. Record facts from
`tests/results/r12-maintenance-guard.txt` (last touched d7266c5): plain gate (no flag) `rc=0`, 6 verdicts PASS;
unknown arg `--bogus` → `rc=2` + `usage: tests/fixtures/r12-maintenance-guard.sh [--selftest]`; `shellcheck -S
warning` → `version: 0.11.0`, `sc_rc=0` (record states "exit 0 (ShellCheck 0.11.0)").

**E5 — predicate-fidelity mutants (own copy `…/AuditK01/mut`, lane untouched):**
```
M1  run_case maintenance-auto 1 → 3   (mechanism regressed, exit contract intact)
    rc=1   last: selftest=FAIL ids=6/6 missing=[] extra=[] failed_verdicts=1
    verdict=PASS×5, verdict=FAIL×1
    frozen predicate "\b6/6\b && PASS" holds = True ; strict "selftest=PASS ids=6/6" holds = False
M2  M1 + `exit "$FAILED"` → `exit 0`  (line 241)
    rc=0   last: selftest=FAIL ids=6/6 missing=[] extra=[] failed_verdicts=1
    frozen predicate holds = True ; row's stated outcome "selftest=PASS ids=6/6" present = False
```
**E6 — fail-closed probe:** with `mktemp` replaced by a failing shim on PATH (simulates unwritable /var/tmp):
`rc=2`, `git_version=git version 2.56.0`, `id=SOUJI-R12-MAINT-SETUP error=mktemp failed under /var/tmp`. An
environment fault is exit 2 ⇒ MISMATCH, never a false green.

## Findings
1. **K01 needs no restatement.** AGREE `original` at list-rev and tip (E3); every count in the cell reproduces (E2,
   E4). Location: SCORECARD.md:152; census/round-33/c1-items.tsv K01.
2. **Deterministic on this host.** Four runs, three TMPDIR regimes, byte-identical apart from nothing at all
   (E2). No 30 s default-case race observed; the poll loop (fixture:151-158) never had to iterate. Location:
   tests/fixtures/r12-maintenance-guard.sh:145-158.
3. **Exit conjunct is faithful to the tool's documented contract**: "and exits 1 on mismatch (0 when both the
   cases and the id assertion hold)." (tests/fixtures/r12-maintenance-guard.sh:41; implementation
   `exit "$FAILED"` at :241 with `FAILED=1` at :182/:233). So `exit 0` ⇒ no `verdict=FAIL` and id set equal ⇒
   `selftest=PASS ids=6/6`. Location: same file.
4. **The `PASS` conjunct is unanchored and therefore lax** (E5 M1): `PASS` is satisfied by any per-case
   `verdict=PASS` line, and `\b6/6\b` by the FAIL line's `ids=6/6`, so the frozen predicate alone holds on a run
   whose own aggregate line reads `selftest=FAIL … failed_verdicts=1`. Location: c1-items.tsv K01 predicate column
   vs tests/fixtures/r12-maintenance-guard.sh:192-236.
5. **False AGREE reachable only by also breaking the exit contract** (E5 M2): rc=0 + `selftest=FAIL ids=6/6` is
   reported AGREE. Every regression that keeps the documented exit contract is absorbed by the exit conjunct, so
   no false green exists for an in-contract tool. Location: as 3 + 4.
6. **Out-of-set residual R-A (stale environment footer in the cell's cited evidence).** `tests/results/
   r12-maintenance-guard.txt:4` records `# git version 2.55.0`; the live command prints `git_version=git version
   2.56.0` (E2). The cell's live pair (6/6 PASS, exit 0) is still true on 2.56.0, and the record is a dated
   r12 observation (last touched d7266c5), so this is a superseded footer, not a false claim — but the record is
   named in the cell as current evidence and has not been regenerated. Location: SCORECARD.md:152;
   tests/results/r12-maintenance-guard.txt:4,11,22.
7. **Out-of-set residual R-B (retired path inside the same record).** The record's unknown-arg gate line embeds
   `/home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/souji-shokunin/tests/fixtures/r12-maintenance-guard.sh`;
   that directory is gone (`ls: cannot access … No such file or directory`) and today's gate prints
   `usage: tests/fixtures/r12-maintenance-guard.sh [--selftest]` (E4). Historical provenance only.
8. **Out-of-set residual R-C (scope, not a K01 claim).** The fixture pins a hard-coded /var/tmp root and ignores
   TMPDIR — "Hermetic: hard-coded scratch root /var/tmp/souji-r12-maintenance.XXXXXX"
   (tests/fixtures/r12-maintenance-guard.sh:47, implemented :68) — the same defect family as C2 legs O1-O5, yet
   this file is not in census/round-33/c2-legs.tsv. It fails closed (E6), so K01 cannot false-green on a
   read-only /var/tmp; it can only MISMATCH. Reported, no leg change proposed (legs are the L1's).

## Attack log
- **ATTACK-K01-A — predicate laxness (`PASS` conjunct).** Reproduced state: E5 M1 (`selftest=FAIL ids=6/6 …
  failed_verdicts=1`, 5×`verdict=PASS`) satisfies the frozen predicate; E5 M2 turns the same state into a false
  AGREE with rc=0. Not reachable from a tool that keeps its documented exit interface (tests/fixtures/
  r12-maintenance-guard.sh:41), so severity is bounded but non-zero: "guard exits 0 while its own output says
  FAIL" is exactly the false-green class other C1 items pin with `control=FALSE-GREEN-REJECTED`
  (c1-items.tsv K16-K21, K23). **Smallest safe correction, for L1 only (I change nothing):** make the PASS
  conjunct the aggregate line the cell actually quotes — `selftest=PASS ids=6/6` — which every honest run here
  satisfies (E2: all four runs contain it) and which M1/M2 both fail; stricter-only, also reject the tokens
  `selftest=FAIL` / `verdict=FAIL`. This brings K01 in line with the counter's prevailing exact-form style
  (`cases=N pass=N`, `total=N failed=0`).
- **ATTACK-K01-B — cited-evidence decay (R-A/R-B).** Not a rule defect; recorded because the cell names the
  record as evidence and the record's footer and one embedded path are superseded. No action requested beyond the
  L1's discretion.
- **Counterexample search that failed (recorded as a negative sweep):** no environment, TMPDIR, argument or
  concurrency state produced NONDETERMINISTIC output (E2, 4 runs + 1 plain gate run + 1 unknown-arg run); no
  strict-predicate false negative (the honest output contains the cell's exact `6/6 PASS` pair).

## Deliveries
- `.ufo/waves/round-33/w1/SwarmCritic01.md` (this report).

Tooling: no installs or upgrades performed (none needed); no pacman transaction attempted. Scratch
`/fast/scratch/hyaku/souji-r33/AuditK01` removed after copying these receipts.

Seat defect, disclosed: the first write of this report used a relative path and landed at
`/home/vgpnk/Projects/shokunin/.ufo/waves/round-33/w1/SwarmCritic01.md` (fleet root, outside the lane). It was
copied to the lane path above and the stray copy plus its now-empty directory were removed; nothing else outside
the lane was written. All later paths were absolute.
