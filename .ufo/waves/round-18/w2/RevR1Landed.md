STATUS: DONE — R1 behavior and requested mutant tested in isolated clones; one config-scope edge remains.

# Attacked claim: R1 — quarantine recipe owner

## Findings (by severity)

### P2 — `lane.id` lookup can consume an unrelated global/system value

Evidence: `tools/souji-quarantine.sh:252-279` reads `owner` with `git -C "$repo" config --get lane.id` at line 254, then treats any syntactically valid value as the owner and skips the basename fallback. Git's `git-config` documentation says reads default to system, global, and repository-local config files (https://git-scm.com/docs/git-config). The fleet helper then rejects an `--as` value unless it matches the repository's lane identity or `protocol` (`scripts/hyaku/jj-lane.sh:515-517`).

[INFERENCE] If a repo lacks its local `lane.id` but the operator's global/system config contains a different valid `lane.id`, the quarantine command can print a recipe with that unrelated identity; running it will be refused by `jj-lane.sh`. Properly initialized lanes are not affected: init writes the repo binding with `git config lane.id "$id"` at `scripts/hyaku/jj-lane.sh:436-440`, and local config wins. This edge affects the intended missing-ID fallback path, not the initialized-lane path.

Smallest fix: scope the read to the repository-local config (`git -C "$repo" config --local --get lane.id`) and add a fixture with conflicting global `lane.id` plus no local value, asserting basename fallback or the placeholder.

## Verification and exact results

All lane-code commands ran only in isolated `/var/tmp` clones at the requested commits. Both clones were removed after testing.

- In the `5efb519` clone, `TMPDIR=/var/tmp bash tools/souji-quarantine.sh --selftest` → `selftest: 105 checks, 0 failed` (exit 0).
- In the `5efb519` clone, `bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` → `CASE J13 PASS` (`--as kama`), `CASE J13-own PASS` (`--as souji`), `SUMMARY total=35 failed=0 skipped=2` (exit 0). The two skips are J6 baseline comparisons without `--baseline-dir` / baseline vault tool.
- Using the same `5efb519` fixture with the `b576341` tools, `bash tests/fixtures/r17-jj-receipts.sh --tool-dir /var/tmp/souji-r18w2-RevR1Landed-baseline/lane/tools` → `CASE J13 FAIL` (baseline recipe uses `--as souji` for the `kama-shokunin` lane), `SUMMARY total=35 failed=1 skipped=2` (exit 1); `J13-own` passes.
- Mutant in the isolated `5efb519` quarantine script: set `owner=souji` whenever `lane.id` is absent, before the basename fallback. `TMPDIR=/var/tmp bash tools/souji-quarantine.sh --selftest` → `FAIL R1 kama recipe owner`, `FAIL R1 unknown recipe owner`, `selftest: 105 checks, 2 failed` (exit 1). Thus the selftest catches the requested default-to-souji mutant.
- With that same mutant, `bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` still reports `SUMMARY total=35 failed=0 skipped=2`. Its `recipe_build_repo` helper explicitly writes a local `lane.id` at `tests/fixtures/r17-jj-receipts.sh:313-315`, so J13 itself does not exercise the missing-ID fallback; the selftest's basename and unknown-owner cases do.
- `scripts/hyaku/jj-lane.sh:420-445` confirms init unconditionally writes `lane.id` for an initialized lane at line 440.

## Verdict

PARTIAL. The landed implementation passes the requested positive and baseline-negative tests, and the selftest detects the default-souji mutation. The R1 recipe lookup is nevertheless not strictly bound to repository-local identity when that key is absent, so the missing-ID fallback can be bypassed by ambient Git config.

## Residual risk / verification gaps

No test with a conflicting global/system `lane.id` was run; the finding is inferred from the documented Git config read scope and the implementation/helper checks above. The `lsp` device is unavailable in this environment (`xd://lsp` returned “No such tool”); therefore references/definition/diagnostics were unavailable. No source grep was used as semantic proof. No tools were installed or updated.
