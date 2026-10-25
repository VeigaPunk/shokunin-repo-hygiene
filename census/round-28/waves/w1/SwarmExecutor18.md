# SwarmExecutor18 — round 28, wave 1 (godspeed mistake-mining; C1 evidence seat)

## Status

STATUS: PASS — mistake mined (class=stale-premise), red/green fix demonstration executed in
scratch `/var/tmp/souji-r28-SwarmExecutor18/`; both verifier outputs captured with exit codes;
scratch removed.

## Mistakes (draft row for the L1 lesson)

- R28-M1 (class=stale-premise; evidence: at base `3a2a80d` the Q57 checker reports
  `q57=PASS` (all 4 sites SUPERSEDED) while the landing-gate reports `findings=2` dangling
  cites — the checker's superseded-mask hides the Q57/Q59 cells' pseudo-path tokens from the
  gate; captured-by: none (no criterion or rule caught the two verifiers disagreeing); fix:
  Q57 site-list refactor (committed sites file `census/round-28/q57-sites.txt`, committed
  mapping pointer `census/round-24/records/slice-verdicts.tsv`) + Q59 reword to
  `knowledge-registry` + a cross-check that both verifiers agree at tip). The fix is shown to
  fail on the unfixed pair (red) and pass on the fixed pair (green) below.

Class judgement: stale-premise, not number-drift — no counter literal drifts between rounds;
the defect is the checker's pass premise (superseded-note mask + inline pseudo-path
enumeration) going stale against the corpus surface the gate scans.

## Evidence

Scratch world: `git init` repo at `/var/tmp/souji-r28-SwarmExecutor18/lane`, fetch from the
lane, `rev-parse --show-toplevel` = `/var/tmp/souji-r28-SwarmExecutor18/lane`; base worktree
`3a2a80d0d18940a5e352ebc526da22a57dad83c4`, fix worktree `eb6d41ff9b995ee45bb0a70fa36f89fa86b678da`
(one commit: `census/round-28/q57-sites.txt` + `corpus/QUALITY.md` Q57/Q59 cells + report
placeholder). No tools installed (none needed); tooling-directive record: none.

### RED — unfixed pair at base 3a2a80d (both run against the base worktree)

Command A (landing-gate):
`python3 -B tools/souji-landing-gate.py --root . --rev 3a2a80d0d18940a5e352ebc526da22a57dad83c4 --round 28 --fleet-root /home/vgpnk/Projects/shokunin`

Output (verbatim, rc captured):
```
LG-DANGLING-PTR	corpus/knowledge/registry	corpus/QUALITY.md:143 cites path absent at 3a2a80d0d189
LG-DANGLING-PTR	corpus/lessons/round-24.md:232:S118	corpus/QUALITY.md:141 cites path absent at 3a2a80d0d189
SUMMARY	findings=2	checked_reg=52	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=0
COULD-NOT-EVALUATE	no .md reports under .ufo/waves/round-28/ at 3a2a80d0d18940a5e352ebc526da22a57dad83c4
rc=2
```
This reproduces the frozen before receipt `census/round-28/records/c1-before.tsv` byte-for-byte
(rows 1-4 identical; `c1_rc=2`).

Command B (Q57 checker pair, cell `corpus/QUALITY.md:141` at base):
`python3 -B tests/fixtures/r25-slice-mapping.py` and
`bash tests/fixtures/r25-q57-check.sh . census/round-24/records/slice-verdicts.tsv .ufo/waves/round-24/assimilation/slice-verdicts.tsv corpus/lessons/round-25.md corpus/lessons/round-24.md:240 corpus/lessons/round-24.md:232:S118 LOG.md:1692 SCORECARD.md:181`

Output (verbatim, rc captured):
```
mapping_pointers=2/2 path=corpus/lessons/round-25.md
S118 gate=accepted detail_mapped=accepted PASS
rows=8/8 status=PASS
slice-mapping rc=0
---
MAPPING-PRESENT corpus/lessons/round-25.md
recount census/round-24/records/slice-verdicts.tsv: 8 accepted
POINTS census/round-24/records/slice-verdicts.tsv -> corpus/lessons/round-25.md
POINTS .ufo/waves/round-24/assimilation/slice-verdicts.tsv -> corpus/lessons/round-25.md
SUPERSEDED corpus/lessons/round-24.md:240
SUPERSEDED corpus/lessons/round-24.md:232:S118
SUPERSEDED LOG.md:1692
SUPERSEDED SCORECARD.md:181
q57=PASS
q57-check rc=0
```
Mismatch: `q57=PASS` (rc 0) while the gate reports `findings=2` (rc 2). The checker's
SUPERSEDED branch is `tests/fixtures/r25-q57-check.sh:45-47`, fed by the superseded notes
`corpus/lessons/round-24.md:387-388` (e.g. line 388: "superseded by
corpus/lessons/round-24.md:232; mapping corpus/lessons/round-25.md § Quarantine-slice
vocabulary; authority census/round-24/records/slice-verdicts.tsv; recount S118 accepted"), so
the four sites pass masked; the gate separately flags the cell tokens
`corpus/lessons/round-24.md:232:S118` (QUALITY.md:141) and `corpus/knowledge/registry`
(QUALITY.md:143) as absent paths.

### GREEN — fixed pair at eb6d41f (Q57 refactor + Q59 reword committed in scratch)

Fix delta (mirrors the lane working-tree C1 edits): Q57 check cell now runs
`bash tests/fixtures/r25-q57-check.sh . census/round-24/records/slice-verdicts.tsv census/round-24/records/slice-verdicts.tsv corpus/lessons/round-25.md $(cat census/round-28/q57-sites.txt)`
(second mapping argument = committed authority; inline pseudo-path tokens dropped); Q59 body
token reworded `corpus/knowledge/registry` -> `knowledge-registry`.

Command A (landing-gate at eb6d41f):
`python3 -B tools/souji-landing-gate.py --root . --rev eb6d41ff9b995ee45bb0a70fa36f89fa86b678da --round 28 --fleet-root /home/vgpnk/Projects/shokunin`

Output (verbatim, rc captured):
```
SUMMARY	findings=0	checked_reg=52	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=1
rc=0
```

Command B (Q57 checker pair at eb6d41f, new cell command):
```
mapping_pointers=2/2 path=corpus/lessons/round-25.md
S118 gate=accepted detail_mapped=accepted PASS
rows=8/8 status=PASS
slice-mapping rc=0
MAPPING-PRESENT corpus/lessons/round-25.md
recount census/round-24/records/slice-verdicts.tsv: 8 accepted
POINTS census/round-24/records/slice-verdicts.tsv -> corpus/lessons/round-25.md
POINTS census/round-24/records/slice-verdicts.tsv -> corpus/lessons/round-25.md
SUPERSEDED corpus/lessons/round-24.md:240
SUPERSEDED corpus/lessons/round-24.md:232:S118
SUPERSEDED LOG.md:1692
SUPERSEDED SCORECARD.md:181
q57=PASS
q57-check rc=0
```
Agreement at tip: gate `findings=0` (rc 0) and checker `q57=PASS` (rc 0). The C1 target
"landing-gate findings 2->0" is met in the demo fix; no exemptions used.

## Findings

1. C1 defect A: `corpus/QUALITY.md:141` (Q57 check cell) at base embeds the enumerated-site
   token `corpus/lessons/round-24.md:232:S118`; the landing-gate reads it as a citation
   candidate and reports `LG-DANGLING-PTR` ("cites path absent") — reproduced at base, gone at
   the fix rev.
2. C1 defect B: `corpus/QUALITY.md:143` (Q59 criterion body) at base contains the token
   `corpus/knowledge/registry`; the landing-gate reports `LG-DANGLING-PTR` for it; the reword
   to `knowledge-registry` removes the finding.
3. Mask mechanics: `tests/fixtures/r25-q57-check.sh:45-47` accepts any site carrying a
   `superseded by` note that names `file:line` plus the mapping, so the four r24 sites report
   `SUPERSEDED` and `q57=PASS` regardless of the cell tokens the gate flags — the two
   verifiers disagree at base with no rule intercepting (captured-by none).
4. rc nuance: at base the gate exits 2 (`COULD-NOT-EVALUATE`, no `round-28` wave reports) yet
   still emits `findings=2`; the before receipt records `c1_rc=2`. The green run has a report
   present and exits 0. The claim counter is the SUMMARY `findings` literal in both states.

## Attack log

No attack claims from this seat; the C1 counters (findings 2->0, no exemptions) were
reproduced as stated in the frozen preregistration.

## Handoff checks for the L1

- Main C1 verification: run the gate at tip (`findings=0`, rc 0) and the Q57 pair
  (`q57=PASS`); confirm `census/round-28/q57-sites.txt` is committed and the Q57 cell's second
  mapping argument is the committed authority.
- Add the R28-M1 draft row to the round-28 lesson's `## Mistakes`.
- Scratch `/var/tmp/souji-r28-SwarmExecutor18/` removed; no lane files changed by this seat
  (read-only; report file only).
