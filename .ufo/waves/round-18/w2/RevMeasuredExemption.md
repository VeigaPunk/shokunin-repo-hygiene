STATUS: DONE — scoped calibration review found a path-only measured-commit suppression risk

Attacked claim: the round-18 landing gate's exemption for `tests/fixtures/r14-cache-frozen/record.json` cannot suppress a real dangling `measured_commit`, and the exempted record is synthetic.

Axes: exemption soundness; placeholder provenance; round-18 calibration evidence.

## Finding

### MEDIUM — measured-commit exemption is path-bound, not value-bound

At `tools/souji-landing-gate.py:590-606`, an unresolvable `measured_commit` at round 18+ is reported as `LG-FROZEN-MEASURED` unless `record_repo in exemptions`. On a path match, the code marks the exemption used and skips the finding without checking the record's value. `load_pointer_exemptions` (`:763-789`) stores only the row's first TSV field as the exemption key; the reason field is not enforced. The stale-exemption pass (`:990-998`) likewise treats any unresolvable value at that path as use, so it will not flag a changed value as stale. The explicit selftest (`:1480-1498`) confirms an exemption suppresses an unresolvable measured commit based on the record path.

The corpus row is `corpus/pointer-exemptions.tsv:3`: `tests/fixtures/r14-cache-frozen/record.json`. Therefore a different, genuinely dangling historical commit written into that same record path would also bypass `LG-FROZEN-MEASURED`. The fixture currently has an independent pin: `tests/fixtures/r14-cache-frozen/expected.json:2-7` includes the digest of `record.json` under `files`. Changing only the record would still produce `LG-FROZEN-PIN` (`tools/souji-landing-gate.py:497-525`); however, updating that mutable expected digest alongside a changed record leaves no invariant tying the exemption to the original placeholder. The exemption does not prevent a fully self-consistent fixture update from hiding the new dangling measurement.

Smallest fix: bind the exemption to the exact expected placeholder value as well as the path, and only mark it used when both match. A different unresolvable value at the same path must still produce `LG-FROZEN-MEASURED`; add that case to the gate selftest.

## Placeholder finding

The current fixture value is synthetic: `tests/fixtures/r14-cache-frozen/record.json:6` contains the sequential placeholder `0123456789abcdef0123456789abcdef01234567`, and the lane Git lookup below could not resolve it as a commit. `corpus/pointer-exemptions.tsv:3` explicitly calls it a deliberate placeholder, and `tests/fixtures/r14-cache-frozen/expected.json:4` pins this exact record content.

The round-14 material supports the general synthetic-demonstration context, but not the provenance of this exact frozen record: `census/round-14/cache-demonstration.py:4-10` describes synthetic `/var/tmp` inputs, while `:12-14` says its generated record carries an actual measured commit. `corpus/lessons/round-14.md:9,12,47-50` documents the cache eligibility/`attempt_reuse` issue and does not identify `r14-cache-frozen/record.json` or the `012345...` value. Thus the current value is credibly a synthetic placeholder, but the lesson is not independent evidence that this exact fixture was produced by the round-14 run.

## Verdict and verification

**Scoped verdict: PARTIAL.** The current `012345...` value is a synthetic, unresolved placeholder, so this review did not establish that a real measurement is presently being suppressed. The exemption mechanism nevertheless permits one at the same path if the fixture and its expected digest are updated together. The baseline artifact `census/round-18/gate-pointers-before-b576341.json:51-53` records the corresponding `LG-FROZEN-MEASURED` finding for that exact placeholder at the baseline.

Commands and observations:

- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat 5efb519f00075d958c3d1109ef6fcb24c487eb87 -- tools/souji-landing-gate.py tests/fixtures/r14-cache-frozen corpus/pointer-exemptions.tsv census/round-14 census/round-18 corpus/lessons` — no output; these scoped paths matched the supplied landed tip in the working tree.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -t 0123456789abcdef0123456789abcdef01234567` — `fatal: git cat-file: could not get object info`.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin merge-base --is-ancestor 0123456789abcdef0123456789abcdef01234567 5efb519f00075d958c3d1109ef6fcb24c487eb87` — `fatal: Not a valid commit name 0123456789abcdef0123456789abcdef01234567` (exit 128).
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --unified=3 b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 5efb519f00075d958c3d1109ef6fcb24c487eb87 -- corpus/pointer-exemptions.tsv tests/fixtures/r14-cache-frozen/record.json tests/fixtures/r14-cache-frozen/expected.json` — the exemptions file is newly added with the row above; the named fixture files have no diff in that comparison.
- LSP was unavailable: attempting to read `xd://lsp` returned `No such tool: xd://lsp`. Source inspection is based on the cited definitions, caller, fixture, and recorded data, not grep as semantic proof.
- No gate or selftest was executed; this seat had no `ALLOWED-EXEC` authorization. Accordingly, the claimed round-18 zero-finding result at 5efb519 was not independently rerun here.

No tools were installed.