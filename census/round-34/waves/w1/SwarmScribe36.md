# SwarmScribe36 — r34 w1, SCORECARD draft (measurements table, restatement section, r35 planned bullet)

## Status

STATUS: PASS — `.ufo/waves/round-34/w1/deliver-scorecard.md` written with (a) the `### Round 34
measurements` table pre-filled from the committed controls and the frozen targets, (b) the empty
`### Round 34 registry restatements` section, (c) the r35 planned bullet carrying the closure-sweep
carries and wave-1 residuals. This seat ran no counter, fixture or clone; every number below is
quoted from a committed record or a wave-1 report and is labelled as such.

## Evidence

Inputs read at the frozen revision (contract first): `census/round-34/preregistration.txt` (attempt 2,
A1-A6) at `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`, `c1-counter.py` docstring + lines 94-109, 330-401,
`c2-counter.py` docstring + lines 240-329, `c1-items.tsv` (60 ids G01-G26/E01-E34), `c2-legs.tsv`
(W1-W4, N3, N4, J1, G1-G6), `records/controls.txt`, `records/controls-c1-do-nothing.txt`,
`records/controls-c2-do-nothing.txt`, `records/feasibility-final.txt`, `records/junk-c1.txt`,
`records/junk-c2-final.txt`, `records/closure-sweep.txt`, `SCORECARD.md` (worktree + `2b0171e2` blob),
wave-1 `SwarmExecutor01.md`, `SwarmExecutor09.md`, `SwarmCritic20.md`, `deliver-c2-leg-attacks.txt`,
`deliver-c1-E18.md`.

1. Byte identity of the three C1 counter inputs across the freeze revisions (the transfer proof for the
   do-nothing reading):

```
$ git -C <lane> rev-parse 2b59192:census/round-34/c1-items.tsv 2b0171e2:census/round-34/c1-items.tsv \
    9c76c72:SCORECARD.md 2b59192:SCORECARD.md 2b0171e2:SCORECARD.md 2b59192:SKILL.md 2b0171e2:SKILL.md
ef76faef005df7dffb6478bd88833d82c863c198   c1-items.tsv    (2b59192, 2b0171e2)
a5381e99b70cf14b015107061ded0f5af8d6bf3b   SCORECARD.md    (9c76c72, 2b59192, 2b0171e2)
77f36874b1714da1c02b8ab60d0b51ad71b54265   SKILL.md        (2b59192, 2b0171e2)
```

2. Do-nothing readings (committed; quoted, not re-run):

```
census/round-34/records/controls-c1-do-nothing.txt
# C1 do-nothing control at base 9c76c72, list-rev 2b591924 (freeze)
SUMMARY items=60 agree=35 mismatches=25 restated=0 rev=9c76c7222a8abff027af42e37f0d160d52526bba
rc=1

census/round-34/records/controls-c2-do-nothing.txt
COULD-NOT-EVALUATE legs absent at --list-rev
rc=2
```

3. Exit-code binding of the targets: `c1-counter.py` ends `return 0 if mism == 0 else 1`;
   `c2-counter.py` ends `return 0 if failed == 0 else 1`. The frozen target lines therefore imply rc 0.

4. Section parser (`c1-counter.py:94-109`): `inside` is set only by a line starting with
   `### Round 34 registry restatements`, and any later `#`-heading closes it; only lines whose first cell
   matches `E\d{2}[a-z]?|G\d{2}[a-z]?` are parsed, so the table column header in the delivered section is
   inert.

5. Wave-1 residuals (quoted from the records/reports):

```
census/round-34/records/feasibility-final.txt
LEG  W2  FAIL  CASE=20 summary=SUMMARY total=20 failed=1
LEG  W3  FAIL  base/rev mismatch rc=1/1 line='souji-census: census failed for .../tmp/souji-census-selftest.WMYNZy/...'
LEG  N3  FAIL  cases=12 pinned=True summary=False
LEG  J1  FAIL  Command '[... r34-sandbox-junk.py ...]' timed out after 900 seconds
SUMMARY legs=13 pass=9 fail=4 harm=0 rev=60def78d16017be528ba6b439e350918587cb80b

census/round-34/records/junk-c2-final.txt  -> TimeoutExpired (900 s, inner c2-counter run)
census/round-34/records/junk-c2.txt, junk-c2-repaired.txt -> 0 bytes
```

6. No round-34 bytes exist in SCORECARD.md yet: `grep -c 'Round 34' SCORECARD.md` -> `0`, no
   `registry restatements` heading in SCORECARD.md or SKILL.md, and the `2b0171e2` blob ends at
   `### Planned (appended at round 33)`. Lane HEAD at read time `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`.

7. Deliverable shape check: `awk 'BEGIN{FS="|"} /^\|/{print NR": cols="NF-2}'` on the delivery ->
   measurements rows `cols=6`, restatement table header `cols=8` (id + the 7 frozen cells).

## Findings

1. **The C1 do-nothing record was taken at list-rev `2b591924`, not the frozen `2b0171e2`.** Transfer is
   byte-level: `c1-items.tsv`, `SCORECARD.md` and `SKILL.md` are identical at both revisions (evidence 1),
   and the counter's remaining inputs are `--rev` (unchanged base) and the restatement section (absent in
   both). The delivered `before` cell states the provenance and the transfer argument instead of implying a
   run at the frozen list-rev. Location: `census/round-34/records/controls-c1-do-nothing.txt:1-2` vs
   `census/round-34/preregistration.txt` C1 do-nothing clause.
2. **All three SCORECARD additions are appends onto a file with no round-34 bytes** (evidence 6). The
   restatement heading and every row must land in one commit and stay the last section, or
   `load_restatements` sees no section (evidence 4). Location: `SCORECARD.md` tip; `c1-counter.py:94-109`.
3. **C1 needs 25 corrections, not one.** The base reading is `mismatches=25` of 60; the only row drafted in
   the wave so far is E18 (`deliver-c1-E18.md`, verified AGREE restated in a scratch clone). The delivered
   table therefore names the target, not a partial count. Location:
   `census/round-34/records/controls-c1-do-nothing.txt`; `.ufo/waves/round-34/w1/deliver-c1-E18.md`.
4. **C2 has no passing junk record.** `records/controls.txt` states the C2 junk control "ended with a
   TimeoutExpired ... no pass is claimed"; `junk-c2.txt` and `junk-c2-repaired.txt` are empty and
   `junk-c2-final.txt` is a 900 s `TimeoutExpired` over an inner full-counter run. J1 cannot pass without a
   re-run, so the frozen `pass=13` is unreachable on the current records. Location:
   `census/round-34/records/junk-c2-final.txt:1-12`, `census/round-34/records/junk-c2.txt` (0 bytes).
5. **C2's pre-landing feasibility is `pass=9 fail=4` at `60def78`** with W2, W3, N3 and J1 open
   (evidence 5). It is not a landing or tip reading, so the delivered `after` cell leaves it out and names it
   only in the r35 bullet. Location: `census/round-34/records/feasibility-final.txt`.
6. **Targets require rc 0, and the C1 summary may carry `restated=<n>`** (evidence 3); the delivered cells
   say so so the L1 does not read a nonzero `restated=` as a miss.
7. **The r35 bullet carries only recorded items**: closure-sweep CARRIED lines (C2 oracle envelope,
   letters-only prose blind spot, gate mutants M4/M10, uncarried r15/r19/r23/r24/r25 seat failures, landing
   gate `/var/tmp` snapshots, N-item adjudication incl. N25/N28-N34, S223 placeholder-id, r19-rev-pin literal
   `/var/tmp`, r32 items 1/3/4/5 and T18), plus wave-1 residuals (the `where`-cell off-by-one, the missing
   pre-landing restatement control, the four C2 feasibility failures, the five semantic attacks) and the 37
   r33 wave-2 items if round-34 w2 does not run them. No new claim and no frozen-artifact change is proposed.
   Locations: `census/round-34/records/closure-sweep.txt` disposition lines;
   `.ufo/waves/round-34/w1/SwarmExecutor01.md` finding 6; `SwarmExecutor09.md` state note;
   `deliver-c2-leg-attacks.txt` items 1-5.
8. **Write scope respected.** Only the two delivery files below were written. No clone, fixture or download
   was made (no scratch dir created), no `git`/`jj` mutation in the lane, no `rm`/`mv`, no signals, no tool
   install or upgrade.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w1/deliver-scorecard.md`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w1/SwarmScribe36.md` (this report)
