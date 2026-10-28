# R40scribe04 — C1 independent calibration attack

- Seat: scribe (leaf; no dispatch)
- Scope: distinct item 4, **independent source/control: prior committed token-only forgery precedent**.
- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
- Frozen contract read first: `census/round-40/preregistration.txt`, C1 predicate at line 5.
- Claim under attack: each anchored C1 item line must carry a resolvable revision-bound evidence pointer, token-only forgery remains open, and register commit must be strict descendant of `receipt_rev`.
- Tool installs/upgrades: none; pacman untouched.

## Evidence and commands

This is a read-only comparison of committed artifacts; no counter replay or new fixture was run. The exact executed repository reads were:

```text
read /home/vgpnk/.omp/agent/RULES.md
read skill://godspeed
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt
read /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-39/w1/W1RevC1Forge.md
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/records/c1-after.txt
read /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-39/w1/W1ExecC1Items.md
```

Observed pointers:

1. Frozen r40 C1 explicitly requires evidence-bound item lines and a strict-descendant check (`census/round-40/preregistration.txt:5`).
2. Prior committed audit `/.ufo/waves/round-39/w1/W1RevC1Forge.md:128-153` reports an exact token-only forgery: two lines, `R39-C1-06 ...` and `R39-C1-10 ...`, with no receipt/revision/path/commit; the frozen counter returned `ITEM F6 CLOSED`, `ITEM F10 CLOSED`, `SUMMARY items=2 open=0 ...`, rc=0. At lines 171-175 the audit states the forgery succeeded end-to-end and that the counter did not resolve the commit-looking `fcdecaa` token. This precedent directly targets the r40 token-only-open requirement.
3. The prior r39 successful receipt is `census/round-39/records/c1-after.txt:19-21`: `REGISTER cells=6 mismatches=0 commit_distinct=6`; `SUMMARY items=16 open=0 ...`; rc=0. That output demonstrates the older reported register summary values, but not strict descendant semantics by itself.
4. The distinct item-predicate report `/.ufo/waves/round-39/w1/W1ExecC1Items.md:12-16` describes the old check as one-line anchor plus `must`/`mustnot` token co-occurrence; it does not constitute a measurement of the r40 counter.

## Verdict

**Concrete falsifier of the prior-generation control; r40 status NOT MEASURED.** The committed r39 forgery is an observed counterexample to the property that token-only anchored lines remain open under the old instrument. It is relevant adversarial precedent, not proof that the new r40 counter fails: this seat did not execute an r40 candidate counter, did not create a forged r40 item fixture, and did not test equal/backward commit cases. Consequently, C1's r40 acceptance predicate is **unverified here**, not passed or falsified on r40 bytes. A bounded measurement plan is: at the named candidate revision, run its C1 counter once with a token-only anchored item whose line contains no pointer and assert OPEN; run with a resolvable evidence pointer and assert closure; then exercise a register row with commit equal to receipt_rev and one with commit older than receipt_rev, requiring rejection, while a strict descendant passes. Record command, revision, full stdout/stderr, and exit status; compare against the named base control.

## Gates, surfaces, limits

- Gates observed: preregistration contract and committed r39 audit/receipt only; no execution gates run.
- Touched surfaces: this report only, at `.ufo/waves/round-40/w1/R40scribe04.md`.
- Out of scope: production files, frozen claims, git/jj/index mutation, candidate counter execution, and other C1/C2/C3 predicates.
- Known limit: prior report is provenance for a prior instrument and reports its own fixture outputs; this report does not claim to reproduce them. No scratch or installs used.
