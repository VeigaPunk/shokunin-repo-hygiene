# R42executor02 — C2 candidate (souji-freeze-check.py)

Candidate: .ufo/waves/round-42/w1/R42executor02/souji-freeze-check.py
sha256 3aa2020142914dc29ffd9655ff2e3135f3eabb12d972253758dfee2b9edd5c4b, 20753 bytes.

## Commands run
1. `TMPDIR=<scratch> python3 -B souji-freeze-check.py --selftest` -> `SELFTEST cases=47 pass=47 fail=0`, rc=0.
2. `bash census/round-42/score-candidate.sh c2 /fast/scratch/hyaku/souji-r42/R42executor02 tools/souji-freeze-check.py=<candidate>` (exit 0). Observed:
   - all 37 `case-*=PASS`
   - `real ok rc=0 findings=0 summary=(3, 0)`
   - `retro red rc=1 findings=19 summary=(3, 19)`
   - `retro_clean ok rc=0 findings=0 summary=(3, 0)`
   - `selftest ok rc=0 summary=(47, 47, 0)`
   - `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=3aa202014291`

## Design (angle: small pure functions + table-driven self-test)
- Pure/small functions: `parse_claims` (-> claims with key->list of values, plus malformed-heading line numbers), `is_dispatch_name`, `digest`, `base_finding`, `control_finding`, `claim_findings`, `check_path_sha`, `added_dispatch_files`; `check(root, prereg, rev)` is the whole CLI check, and `main` only prints its result.
- New classes: KEY-DUPLICATE (duplicated key is reported once and not value-checked, so there is no first-wins reading); HEADING-MALFORMED (`##` + optional spaces + C/c + optional spaces + digit that is not `## C<digits>` followed by space or end of line; opens no claim and ends the open block); COUNTER-SYMLINK / POPULATION-SYMLINK (git `ls-tree` mode 120000 at freeze, reported alone); DISPATCH-BEFORE-FREEZE widened (basename contains `-dispatch` or `.ready`, or ends `-spec.json` / `-results.json`, any depth, `git log -z` parsing).
- r41 hardening kept: whitelisted git env, no GIT_DIR, `log.mailmap=false`, `core.quotePath=false`, NUL/space paths, CRLF/BOM (BOM now also stripped before heading parse). Added `GIT_LITERAL_PATHSPECS=1`.
- `--selftest`: builds synthetic repos under `$TMPDIR` with the same `Repo` helper the CLI uses (every git call `-C`, identity via env, `rev-parse --show-toplevel` asserted equal to the fixture dir), runs the in-process `check()` (so the tool's own `hashlib.sha256`, `git log --diff-filter=A` and `git merge-base --is-ancestor` calls run for real) over 37 table cases, plus 10 heading-grammar cases and a digest known-answer. Stated digests in fixtures are hard-coded constants (not computed by the tool's digest function), so a reversed digest makes cases fail; freeze and dispatch cases fail when `--diff-filter` log is empty; ancestry cases fail when merge-base always fails. patches=3/3 confirms.
- No reading of the counter's CASES, SITECUSTOMIZE text or env var names. Caveat: a grep I ran to find the docstring bounds incidentally displayed one line of the sitecustomize header containing an env var name; the candidate does not use it and has no special-casing of patches or fixture names.

## Verdict
C2 target met in scratch score (advice only). Scratch dir deleted. No installs, no tracked files touched.
