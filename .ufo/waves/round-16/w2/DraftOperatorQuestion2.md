# Round 16 · Wave 2 · DraftOperatorQuestion2 — L0 scope question draft

Seat: SoujiR16.DraftOperatorQuestion2-4 (leaf, no delegation). Lane HEAD a6ec781 (read-only inspection of `tools/souji-census.sh` at 0a70bef sha 64a60fd0…; pre-harm a31642d sha 6a000c59…).
Judged on: calibration.

## Draft L0 question

souji | round-16 | Operator scope call: the round-14 safety-motivated contractions that round 16 keeps — (a) git-metadata guards that refuse the whole run (gitfile/commondir/alternates/symlink), (b) GIT_CONFIG_GLOBAL/GIT_CONFIG_SYSTEM forced to /dev/null, so the operator's global git config is ignored, (c) a bound filter driver skipping status for that one repo (dirty=0, status-unverifiable), (d) `~user` and unresolvable config paths degraded to an `error` row, and (e) `status --ignore-submodules=all`, which can hide a dirty submodule and let the verdict read `clean` — are they accepted as intended costs against the pre-harm (a31642d) behaviour, or must any of them be narrowed back to pre-harm behaviour under a different safety mechanism?

## Findings (evidence)

1. **Contractions are r14, not r16 — holds.** `git log -S` on `tools/souji-census.sh` puts both `ignore-submodules` and `GIT_CONFIG_GLOBAL` in commit `48f8945` ("round-14: bind retained evidence and fence census credential paths"). Pre-harm `a31642d:tools/souji-census.sh` has neither (grep: no `ignore-submodules`, no `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_NOSYSTEM`; status is `git -C "$1" --no-optional-locks status --porcelain -- .`, line 131). Pre-harm also has no `guard_git_surface`/gitfile/commondir handling (grep hits only the test fixture at lines 562/568 and a comment at 331). Round 16 leaves the git-metadata guards unchanged (header line 86–87).
2. **Global config dropped — holds as documented, with a behaviour change vs pre-harm.** `tools/souji-census.sh:153` sets `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null`. Pre-harm honoured global config (e.g. a global `core.excludesFile`). Header line 147–149 documents the clearing. Not a regression in the r16 change; it is an r14 contraction carried forward.
3. **Submodule status hidden — documented, but a calibration hazard.** `tools/souji-census.sh:1037` runs `status --porcelain --ignore-submodules=all`. Header line 38–39 documents "Submodule content is not inspected". The header line 53–54 says `clean` requires `dirty=0`, so a repo whose only change is a modified submodule can get `clean`. [INFERENCE: from git's default `--ignore-submodules=none` semantics and the verdict rule; not executed here — no probe was run against a real or synthetic submodule, per the probe rule.]
4. **Bound filter skip — holds.** `tools/souji-census.sh:1027–1031`: `status-skipped: filter-driver-bound` prints `unverifiable` (dirty unknown). Fixture `tests/fixtures/r15-census-config.py` case 14 (line ~1288–1301) pins it. Pre-harm ran status unconditionally, so this row differs from pre-harm by design.
5. **`~user` / unresolvable config degrade — holds.** `tools/souji-census.sh:640–661` (`cfg_soft "git-config-unsupported"`) and `:1177–1181` emit `printf '%s\t0\t0\t0\t0\t\terror\n'` with stderr `config-unsupported`. Fixture case 03 pins the one-`error`-row shape. Pre-harm has no config guard, so these repos were measured there.
6. **Calibration of the landing record (observation, not a finding against the tool).** `census/round-16/c1-matrix-final.json` records `changed` rev 0a70bef with `fixtures_sha256.r15-config = 85de2a43…`; `census/round-16/c1-matrix-landing.json` records rev 7a79dc2 with `r15-config = 27474396…`. The tool sha (64a60fd0…) and `r14-namespace` fixture sha (e6a984b1…) match across both. The fixture digest differs between the final and landing matrices, so the landing rerun does not measure the same fixture bytes as the final one. L1 should reconcile which fixture revision the claim "changed 20/20" was measured against.

## Verdicts

- Item 1 (contractions originate in r14, absent from pre-harm): **holds**.
- Item 2 (global config ignored): **holds** as a documented contraction.
- Item 3 (`--ignore-submodules=all` can yield `clean` for a dirty-submodule repo): **partial** — documented, but the clean verdict is not guarded; the fix is either to drop `--ignore-submodules=all` (restore pre-harm default) or add a `submodule-hidden` flag. [INFERENCE on the behaviour until probed.]
- Item 4 (bound-filter skip): **holds**.
- Item 5 (`~user` degrade): **holds**.
- Item 6 (fixture digest drift between final and landing matrices): **partial** — the two records disagree on the fixture digest; the claim should name one fixture revision.

## Out-of-scope items

- No execution of `tools/souji-census.sh` (forbidden on real directories; not run here).
- No probe of submodule behaviour (no ALLOWED-EXEC item named).
- No tooling installed or updated.

## Commands

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show a31642d:tools/souji-census.sh | grep -n -E 'ignore-submodules|GIT_CONFIG_GLOBAL|GIT_CONFIG_NOSYSTEM|status --porcelain|config-unsupported|~'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -S'ignore-submodules' -- tools/souji-census.sh; echo '--- GIT_CONFIG_GLOBAL ---'; git log --oneline -S'GIT_CONFIG_GLOBAL' -- tools/souji-census.sh; echo '--- pre-harm include/config refs ---'; git show a31642d:tools/souji-census.sh | grep -n -E 'include|GIT_CONFIG|gitfile|commondir' | head -20
```

Reads (exact named files, no execution): `tools/souji-census.sh` (lines 1–300, 1–300 header), `census/round-16/c1-matrix-final.json`, `census/round-16/c1-matrix-landing.json`, `tests/fixtures/r15-census-config.py` (lines 1–106). Greps on exact `tools/souji-census.sh` for `ignore-submodules|GIT_CONFIG_GLOBAL|config-unsupported|status-skipped|path-protected` and `guard_git_surface()|gitfile|commondir|alternates`.

STATUS: ok
