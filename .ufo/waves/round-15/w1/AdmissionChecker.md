# AdmissionChecker — C2 independent preservation-evidence admission gate (r15)

## Files written

- `tools/souji-preservation-evidence.py` (~2625 lines) — the checker. New file.
- `tests/fixtures/r15-preservation-evidence.py` — external black-box driver
  (r13-cert-evidence.py pattern: CLI-only invocations, scratch under
  `/var/tmp`, exit 0/1/2).
- `tests/fixtures/r15-preservation-frozen/{record.json, expected.json,
  README.md}` — shipped pinned frozen input (pre-integration pins; verdict
  `clean`; README documents the two-step re-pin post-integration).

## Behavior

`--record JSON|@PATH|PATH --root DIR`, `--frozen DIR --root DIR`, `--selftest`.
Exit 0 clean / 1 failed honest evidence / 2 could-not-evaluate
(malformed, tampered, inconsistent, protected, unreadable). Level-2 finding
dominates level-1. Recorded commands are never executed — the gate consumes
JSON + file hashes only.

Record schema `souji-preservation-record-v1`: `declared_consistency_only:
true`, `measured_commit` (40hex), `fixture` + `namespace_fixture`
{path, sha256} measured under `--root`, `runs` = exactly
{`baseline_preharm`, `baseline`, `changed`}, plus `namespace_controls`.

Pinned oracles (literals, never derived from fixture output):
- baseline tool = commit cc21683…/sha256 fcff8b05… (observed installed r14
  harm tool); preharm = a31642d…/6a000c59…; namespace fixture sha256
  e6a984b1… (verified against `tests/fixtures/r14-census-boundary.py`).
- r15 matrix agrees with the landed `r15-census-config.py`: harm FAIL =
  HARM_CASES {01,04,06,08,09,10,12,13,15,16}; preharm FAIL = refusals
  {02,03,07,11,14,17,19} + safety 08 + preserve {18,20} (a31642d does not
  clear inherited GIT_* env and lacks the strict malformed-compare guard;
  confirmed by fixture author); preserve 05 passes everywhere; changed
  all-pass; namespace_controls 12/12 over R14C2-01..12.
- Rejects: missing arms (run-missing), green-only, weakened red
  (case-status-unexpected + baseline-not-red), weak baseline reasons
  (baseline-reason-weak), refusal PASS without a non-"none"
  observed_finding and benign PASS with any finding
  (case-finding-mismatch), subset argv (--case/--list → run-inconsistent),
  changed bound to a pinned baseline digest (pinned-mismatch = no repair
  measured), digest/commit inconsistencies, dup/unknown/missing case ids,
  transcript-vs-declared disagreement, protected/absolute/escaping/symlink
  paths. Protected-tree + O_NOFOLLOW fd walk same as evidence-cache tool.

`--frozen`: expected.json {record, record_sha256, verdict, files} — record
bytes pinned under DIR, payload digests pinned under `--root`; incomplete
pin set → frozen-incomplete; drift → snapshot_tampered; post-evaluation
verdict ≠ expected → snapshot-verdict-mismatch.

Selftest: 47 discriminating cases, self-invoked via `sys.executable` on the
same file with scrubbed HOME/PATH env — negative controls prove the gate
rejects weakened/missing/green-only/tampered evidence, no runtime tests.

Driver fixture: `--selftest` sweep plus external synthetic roots covering
clean, green-only, weakened-red, no-ns, changed-is-baseline, and a frozen
tamper check on a copied `r15-preservation-frozen`.

## Coordination

Matrix + transcript contract sent to SoujiR15.RoundRunner and
SoujiR15.ConfigFixture (verbatim id sets, observed_finding token rules,
frozen schema with `record_sha256` + files-under-`--root` semantics,
`--frozen` requiring `--root`).

## Risks / blockers

- Preharm pins for preserve ids (05/18/20 = pass) and safety 08 = fail are
  my reasoned values: a31642d predates the r14 harm but already carries env
  isolation and compare guards; NO_LAZY_FETCH is new. If ConfigRepair's
  real preharm run disagrees, adjust `CONFIG_PRESERVE_PREHARM` /
  `CONFIG_SAFETY_IDS` — single-line, flagged in comments.
- Frozen fixture ships pre-integration pins: evaluation against the live
  lane returns snapshot_tampered/pinned-mismatch (exit 2) until L1 re-pins
  per `README.md`. This is fail-closed by design, not a defect.
- Checker's `--selftest` requires `tests/fixtures/r14-census-boundary.py`
  to equal NAMESPACE_SHA256 (verified true today) and `strace`-free —
  it never runs the fixture.

## Unrun checks (L1 to execute)

- `python3 tools/souji-preservation-evidence.py --selftest` (expect 0/47).
- `python3 tests/fixtures/r15-preservation-evidence.py` (external driver).
- Post-integration: refresh `r15-preservation-frozen` pins per README, then
  `--frozen tests/fixtures/r15-preservation-frozen --root .` (expect clean).

No installs performed; no runtime tests executed (source inspection only).
