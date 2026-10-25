# ExecVerifyLoop — round-26 post-integration verify loop

## Status

STATUS: PARTIAL — the loop is delivered at `.ufo/waves/round-26/w1/verify-loop.sh`
(syntax-clean, 17 checks, exercised on the lane at `166baa18` and on three
falsification arms), but the tip commit `166baa1` landed an earlier broken copy
of that same script (`bash -n` rc 2); my fix exists only as an uncommitted
worktree edit and this seat cannot commit. Two checks also FAIL at the tip for
real reasons (landing gate, receipts) — that is the loop reporting, not a loop
defect.

## Evidence

Deliverable: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/verify-loop.sh`
(read-only: no file is created, moved or deleted; only `>/dev/null`;
`GIT_OPTIONAL_LOCKS=0`; no fetch; exit 0 all PASS, 1 any FAIL, 2 setup refusal).
Frozen commands transcribed from `.ufo/waves/round-26/preregistration.txt`
(+ amendment 1: K4 after-literal; amendment 2: C1 byte-content spans).
`SOUJI_LANE` exists only so the falsification arms can point at a scratch repo.

`bash -n` → `SYNTAX-OK`.

Lane run, `bash .ufo/waves/round-26/w1/verify-loop.sh`, tip
`166baa18f808071bc385187691713044a26bd663` (exit 1):

```
CHECK tip PASS 166baa18f808071bc385187691713044a26bd663
CHECK clean-claim-surfaces PASS dirty=0
CHECK c1-counter PASS rc=0 markers=0 headings=17 44 78  order=25 24 23
CHECK c2-counter PASS rc=0 grounded_f1=2 registry_rows=132
CHECK c3-counter PASS rc=0 tool=present claims=3 flags=0 axis_check_exit=0 cases=12 pass=12 control=FALSE-GREEN-REJECTED fixture_exit=0
CHECK c2-gate PASS rc=0 entries=2 ok=2 fail=0
CHECK c2-k3 PASS rc=0 ok=1 errors=0 warnings=34
CHECK c2-k4 PASS rc=0 grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0
CHECK landing-gate FAIL rc=1 findings=21 checked_reg=50 first=LG-DANGLING-PTR corpus/knowledge/registry
CHECK census-rows PASS rows=132
CHECK census-malformed PASS malformed=0
CHECK census-tier-hist PASS tier=A=125 B=5 C=2  sum=132
CHECK census-status-hist PASS status=mined=108 queued=15 rejected=9  sum=132
CHECK census-duplicate-ids PASS duplicates=0
CHECK census-enum PASS violations=0
CHECK census-usedby PASS missing=0
CHECK receipts FAIL verify_ok=4 fail=5 unverified=c1-before.tsv c1-after.tsv c2-before.tsv c2-after.tsv c3-before.tsv
SUMMARY checks=17 pass=15 fail=2 tip=166baa18f808071bc385187691713044a26bd663
```

Re-run at `e78ac7c4837b81b634db4a927605a751a7f006ba` (tip when this report was
written) printed the same 17 lines with `tip=e78ac7c4...` and the same two
FAILs; the landing gate there still reports 21 findings, `LG-PARSE-CHANGED` for
this script included.

C2 gate was independently observed failing at `0c92c2e` (`entries=2 ok=0
slice_verdicts=0 slice_total=0 fail=2`, rc 1, two `check4-quote-absent-*` rows);
the check's FAIL rendering is exercised by the negative control below.

Falsification arms, scratch `/var/tmp/souji-r26-ExecVerifyLoop/negctl`
(`git init`, then `SOUJI_LANE=<scratch> bash verify-loop.sh`):

- broken repo (base-order SCORECARD, malformed + duplicate + dangling-used-by
  SOURCES rows) → `SUMMARY checks=17 pass=4 fail=13`; e.g.
  `CHECK c1-counter FAIL rc=0 markers=2 headings=3 9 11  order=23 24 25`,
  `CHECK census-malformed FAIL malformed=1`,
  `CHECK census-duplicate-ids FAIL duplicates=S001`,
  `CHECK census-usedby FAIL missing=missing: missing/path.md`,
  `CHECK census-status-hist FAIL status==1 mined=1 queued=1  sum=3 bad_keys=EMPTY`.
- arm 2, four headings `25 24 24 23`, markers 0 →
  `CHECK c1-counter FAIL rc=0 markers=0 headings=3 5 7 9  order=25 24 24 23`.
- arm 3, three headings in correct order with one scaffold marker present →
  `CHECK c1-counter FAIL rc=0 markers=1 headings=3 5 7  order=25 24 23`.

Stamp: `python3 -B` for every lane Python call; no `__pycache__` written by this
seat. No tool installed, upgraded or removed (no `pacman`, no `uv`, no download).
Scratch removed.

## Findings

1. **The tip carries a broken copy of this deliverable.** `166baa1` committed
   `verify-loop.sh` with an unterminated `${r_missing:+ ...}` at
   `.ufo/waves/round-26/w1/verify-loop.sh:314`; `git show HEAD:... | bash -n`
   → `unexpected EOF while looking for matching '"'`. The landing gate reports
   it as `LG-PARSE-CHANGED .ufo/waves/round-26/w1/verify-loop.sh`. The worktree
   file is fixed (`bash -n` rc 0, `git status` shows ` M`); **the L1 must commit
   it** or the gate keeps the finding.

2. **Five of nine prereg receipts refuse `verify` at the tip.**
   `python3 -B tools/souji-receipt-run.py verify --root . census/round-26/records/c1-after.tsv`
   → `RECEIPT-COUNTS-ABSENT	no stdout line starts with a counts line` (rc 2);
   same for `c1-before.tsv`, `c2-before.tsv`, `c2-after.tsv`, `c3-before.tsv`.
   Cause: `COUNTS_RE` (`tools/souji-receipt-run.py:67-76`) has no alternative
   for `markers=`/`headings=`, `grounded_f1=`/`registry_rows=` or
   `axis_check_tool=`; `c3-after.tsv` verifies only because its stdout also
   carries `cases=12 pass=12`. This contradicts the frozen
   "each `verify=ok`" receipt sentences in C1, C2 and C3 of
   `.ufo/waves/round-26/preregistration.txt`. `.ufo/waves/round-26/w1/LabReceiptVerify.md:5`
   reported the same class for 3 of 4 red-before receipts; the tip shows 5 of 9.

3. **Landing gate at `166baa18` reports 21 findings** (`rc 1`, `checked_reg=50`,
   `checked_reports=84`, `status_lines=63`, `carry_heading=0`):
   - 18× `LG-SEAT-UNCARRIED` + `carry_heading=0`:
     `corpus/lessons/round-26.md` has headings at lines 9, 30, 66, 81, 93 and no
     `## Seat-reported failures` heading, while the wave's reports carry STATUS
     lines (e.g. `.ufo/waves/round-26/w1/CritCoverageCredit.md:5`,
     `.ufo/waves/round-26/w1/RevC3Design.md:4`).
   - `LG-DANGLING-PTR corpus/knowledge/registry` — `corpus/QUALITY.md:143`
     (Q59 prose token), new this round.
   - `LG-DANGLING-PTR corpus/lessons/round-24.md:232:S118` —
     `corpus/QUALITY.md:141`, pre-existing: a base run
     (`--rev 0eca7c8 --round 25`) reports this one alone.
   - `LG-PARSE-CHANGED` for my script — finding 1.

4. **C1's K2 literal is gameable as frozen.** `awk` prints line numbers in file
   order, so any three existing headings produce an ascending triple
   (base `17 175 231`, tip `17 44 78`); "n25 < n24 < n23" cannot fail while the
   headings exist. The loop therefore also derives the heading *names*
   (`grep -nE '^### Round (23|24|25) measurements' SCORECARD.md`) and requires
   `25 24 23`; arm 2 above shows names in base order passing the bare triple
   and failing the loop. Reported as an ATTACK note on the counter; no frozen
   predicate, target or case set was changed.

5. **Unexercised arms, disclosed.** `c2-k3` can only PASS in these runs: the
   frozen command targets `/home/vgpnk/Projects/shokunin` absolutely, and
   writing a failing registry there is outside my bound — its FAIL arm is not
   observed. `landing-gate` PASS (`rc 0`, `findings=0`) is not observed at any
   tip this run; only `rc 1` and `rc 2` (scratch repo, missing tool). Its
   predicate is the tool's own documented exit code plus `findings=0`.

6. **Scope note for the L1.** `clean-claim-surfaces` checks only
   `SCORECARD.md`, `corpus/SOURCES.md`, `corpus/README.md` and
   `corpus/knowledge/` — the bytes where the worktree-reading counters and the
   committed-bytes gates (K2/K4/landing gate) must agree. Untracked wave
   reports are out of its scope by design; the landing gate evaluates committed
   reports, so the loop fails until the wave reports are committed.
