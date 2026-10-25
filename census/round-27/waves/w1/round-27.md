# Round 27 (2026-10-25) — pre-report gate, F4 origin records, landing-gate pointer exemptions

DRAFT — wave w1 scaffold; L1 installs this file as
`corpus/lessons/round-27.md` after integration. Every value below is a
placeholder for L1 integration unless it quotes a committed byte (R27-M1
cites `watchdog.log:1377`). No counter result is asserted here.

## Gate

Candidates (frozen preregistration, round-27):

- C1 (calibration): committed `corpus/pointer-exemptions.tsv` rows resolving
  the two internal LG-DANGLING-PTR findings (`corpus/knowledge/registry`
  QUALITY.md Q59 prose token; `corpus/lessons/round-24.md:232:S118`
  QUALITY.md Q57 composite enumerated-site token).
- C2 (coverage): `corpus/knowledge/origin-record-writer-r27.md` and
  `corpus/knowledge/origin-record-mechanism-set-r33.md` from the staged set
  in `/home/vgpnk/Projects/shokuknow/merge/souji/`, re-grounded this round by
  opening GLib tag 2.84.0 snapshots (`gio/glocalfile.c`,
  `glib/gfileutils.c`), each with its own `## Gate` section (>=1 ADMIT,
  >=1 REJECT from the staged set) citing SOURCES rows S152, S210, S211.
- C3 (operability): `tools/souji-pre-report-gate.sh` +
  `tests/fixtures/r27-pre-report-gate.sh` (selftest 4/4 incl. FALSE-GREEN
  control).

Admitted: <L1 fills after counter run — entry/row/tool names>.

Rejected: <L1 fills with reasons — staged candidates not admitted>.

Spot-check: <placeholder — verifier spot-check file name, cf.
round-26-verifier-spotcheck.md>.

## Findings

- <placeholder — L1 fills after verification; e.g. landing-gate findings
  before/after, registry row counts, fixture case results>.
- R27-M1 (see Mistakes): attempt 1 died with no lane writes; the inline-spawn
  handoff misread is now covered by C3's `prereg`/handoff readiness check.

## Residuals

- <placeholder — L1 fills; e.g. unmeasured edges left for later rounds>.

## Receipts

- <placeholder — L1 lists c1-after/c2-after/c3-after receipt paths, e.g.
  `census/round-27/records/*`>.

## Mistakes

- R27-M1 (class=landing; captured-by none → fixed by this round's C3
  pre-report gate incl. a `prereg`/handoff readiness check, plus the prompt
  now states the L1 writes the ready file): attempt 1 misread the inline-spawn
  handoff and refused resume, with no lane writes. Evidence:
  `/home/vgpnk/Projects/shokunin/.ufo/watchdog.log:1377` (2026-10-25T14:46:45,
  `lane-dead-no-report souji round=27`): "L1 misread inline-spawn handoff
  (expected orchestrator to supply claims/ready), declared blocked, refused
  resume".

## Seat-reported failures

(empty template — seats fill rows here for L1 integration; none in w1.)
