STATUS: PARTIAL — the requested counts were observed, but the 105-check result is sandbox-dependent and B4’s passing summary omits one measured run.

# Attacked claim

Calibration of the changed `SKILL.md` registry rows at `5efb519f00075d958c3d1109ef6fcb24c487eb87`: census 62 checks; landing-gate 53; seat-audit 66; quarantine 105; landing pointers 11/0; proc-census P1–P11; bounded census B1–B8.

All executions below used the clone at `/var/tmp/souji-r18w2-RevSkillRegistryNumbers/lane`, whose `HEAD` was confirmed as `5efb519f00075d958c3d1109ef6fcb24c487eb87`. Where noted, `TMPDIR` was set to the seat directory to respect the run boundary; this means those invocations do not exactly reproduce registry commands that explicitly set `TMPDIR=/var/tmp`.

# Findings

## Low — B4 summary omits one of its two measured cases

- `SKILL.md:170` describes per-case rows/exit/diagnostics for `r18-census-bounded`.
- Executed once: `TMPDIR=/var/tmp/souji-r18w2-RevSkillRegistryNumbers python3 tests/fixtures/r18-census-bounded.py --census tools/souji-census.sh` — exit 0, `SUMMARY total=8 failed=0`; B1–B8 each printed `PASS`.
- B4’s output printed six `expected_rows` (`ignore/{a,b,c}` and `attributes/{a,b,c}`), but only three `observed_rows` (`a,b,c`) and `problems=[]`.
- Evidence: `tests/fixtures/r18-census-bounded.py:927-998` executes and validates separate `.gitignore` and `.gitattributes` runs, then combines the expected labels. The output path at `:1161-1171` takes `actual_runs[-1]` for `observed_rows` and `observed_exit`, so it reports only the final run. The assertions check both measured runs (`:969-978`); this is an incomplete diagnostic, not evidence that B4’s assertion passed vacuously.
- Smallest fix: emit each B4 measured run separately, with `ignore/` and `attributes/` row prefixes, or aggregate both measured runs in the summary. Keep the existing per-run assertions.

## Medium — bounded fixture uses a shared temp root outside the seat sandbox

- `tests/fixtures/r18-census-bounded.py:35` hardcodes `SEAT_TMP = /var/tmp/souji-r18-FixtureR18Bounded`; `:111-112` creates a child scratch directory there, and `:1202-1210` removes only that child, not the shared root.
- This run’s `TMPDIR` override did not redirect the fixture. A post-run `stat` found `/var/tmp/souji-r18-FixtureR18Bounded` still present; its birth time predates this run, so I did not inspect or remove it. The assigned boundary required execution state under `/var/tmp/souji-r18w2-RevSkillRegistryNumbers/` only.
- Smallest fix: allocate a unique fixture root beneath the caller-provided `TMPDIR` (the seat directory here), and remove the root created by this invocation. Do not remove the existing shared directory as cleanup; it predates this run.

# Results and verdict

| Claim | Exact executed command | Observed output | Verdict |
|---|---|---|---|
| `SKILL.md:149`, census 62 | `TMPDIR=/var/tmp/souji-r18w2-RevSkillRegistryNumbers bash tools/souji-census.sh --selftest` | `selftest: 62 checks, 0 failed`; exit 0 | **Count holds.** The selftest reported fixture path `/var/tmp/souji-census-selftest.c1sQqJ`, despite the `TMPDIR` override; post-run `stat` found that path absent. The exact registry environment (`TMPDIR=/var/tmp`) was not used. |
| `SKILL.md:165`, landing-gate 53 | `python3 tools/souji-landing-gate.py --selftest` | `SELFTEST pass=53 fail=0`; exit 0 | **Holds.** |
| `SKILL.md:165`, landing pointers 11/0 | `TMPDIR=/var/tmp/souji-r18w2-RevSkillRegistryNumbers python3 tests/fixtures/r18-landing-pointers.py --tool tools/souji-landing-gate.py` | `SUMMARY total=11 failed=0`; exit 0 | **Count holds.** `TMPDIR` was added for the sandbox. |
| `SKILL.md:168`, seat-audit 66 | `python3 tools/souji-seat-audit.py --selftest` | `SELFTEST pass=66 fail=0`; exit 0 | **Count holds at 5efb519.** The registry’s historical wording says “at b576341”; that baseline was not run because execution was authorized only at 5efb519. |
| Requested quarantine 105 | `TMPDIR=/var/tmp/souji-r18w2-RevSkillRegistryNumbers bash tools/souji-quarantine.sh --selftest` | `selftest: 105 checks, 36 failed`; exit 1 | **Partial / not a valid pass calibration.** The count is 105, but this is not the registry’s exact `TMPDIR=/var/tmp` invocation. `tools/souji-quarantine.sh:167-168` sets `LIVE_FLEET_ROOT` to the clone’s parent; `:1494` places the test fleet under `TMPDIR`; with the required seat-local `TMPDIR`, fixture repos fall under that guard root, and `:682-688` refuses mutations with exit 4 (matching the observed “got=4” failures). No code defect is inferred from this constrained run. The exact documented command would put fixture data outside the assigned seat root, so it was not rerun there. |
| `SKILL.md:170`, B1–B8 | `TMPDIR=/var/tmp/souji-r18w2-RevSkillRegistryNumbers python3 tests/fixtures/r18-census-bounded.py --census tools/souji-census.sh` | `SUMMARY total=8 failed=0`; B1–B8 each `PASS`; exit 0 | **Case counts hold**, subject to the B4 output limitation and shared-temp-root finding above. |
| `SKILL.md:173`, P1–P11 | `TMPDIR=/var/tmp/souji-r18w2-RevSkillRegistryNumbers bash tests/fixtures/r18-proc-census.sh --tool tools/souji-proc-census.sh` | `SUMMARY total=11 failed=0`; P1–P11 each `PASS`; exit 0 | **Holds.** `tests/fixtures/r18-proc-census.sh:67-75` uses a hardcoded `/var/tmp` scratch path and an EXIT cleanup trap; `TMPDIR` does not redirect it. |

# Residual risk and verification gaps

- Overall verdict: **PARTIAL**. Counts 62, 53, 66, 11/0, B1–B8, and P1–P11 matched the one-run outputs. The requested 105 count appeared, but its constrained run had 36 failures and cannot establish the outcome of the exact registry invocation.
- The B4 internal checks pass, but the emitted per-case summary does not expose all six expected/observed rows. The B8 fixture’s fixed `/var/tmp` root also prevents this run from satisfying the seat-local filesystem boundary; I did not remove the pre-existing root.
- The census selftest reported a global `/var/tmp` fixture path and the proc-census fixture hardcodes `/var/tmp`; these test implementations do not honor the seat-local `TMPDIR` override. The observed census fixture path was absent after completion. I did not inspect or clean other global temp paths.
- No LSP device/server was exposed in the supplied tool inventory. This was a registry-number/fixture-output review rather than a caller/definition review; direct file reads and actual command outputs are the evidence here. No source finding is based on grep alone.
- Tool installs/updates: none.
