# SKILL.md round-27 additions (L1 integration draft)

Insert in `## Gate registry` table, before `souji-landing-gate`:

| souji-pre-report-gate | gate | `bash tools/souji-pre-report-gate.sh --lane ABS --branch NAME --report ABS [--prereg ABS] [--allow REL]...` | 0 no FAIL (SKIP allowed only for omitted optional prereg); 1 one or more failed checks; 2 usage error | `bash tests/fixtures/r27-pre-report-gate.sh` (4 isolated cases; FALSE-GREEN always-pass control MUST be rejected) | frozen `.ufo/waves/round-27/preregistration.txt` C3; fixture case assertions | reads named lane/report/prereg; fixture uses isolated `/var/tmp` worlds, removes them on exit; `--allow` applies only to clean-check paths | souji |

Add to `## Checklists` after the existing pre-quarantine checklist:

Pre-report (round 27):
- [ ] Run `bash tools/souji-pre-report-gate.sh` against the intended lane branch, report, and frozen preregistration; require `check-tip`, `check-report`, `check-shonen`, `check-clean`, and `check-prereg` PASS (the prereg check is SKIP only when not supplied; round-27 use supplies it).
- [ ] Treat exit 1 as failed and exit 2 as could-not-evaluate/usage; do not convert SKIP or missing remote information into PASS. This is a readiness gate only, not deletion certification or commit/push authority.
- [ ] Run `bash tests/fixtures/r27-pre-report-gate.sh`; require `cases=4 pass=4 control=FALSE-GREEN-REJECTED` and rc 0 before relying on the gate.

Append to `## Known surfaces`:

- Round 27: `tools/souji-pre-report-gate.sh` checks branch tip against origin, report presence and exactly one `^## SHONEN` heading, lane worktree cleanliness outside explicit `--allow` paths, and preregistration presence when supplied. It is an operability/readiness gate, not a safety certification or authority to modify fleet state. Its isolated four-case fixture includes a false-green always-pass control; see `.ufo/waves/round-27/preregistration.txt` C3.

