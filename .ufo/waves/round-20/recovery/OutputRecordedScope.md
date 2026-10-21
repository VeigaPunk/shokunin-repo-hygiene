# OutputRecordedScope — operability critic

**STATUS: OPEN.** The proposed file-input binding can support the narrow claim that enumerated repository-owned bytes match a durable revision, but the emitted `input_sha256` / `inputs_unchanged_during_run` labels do not state that boundary. They do not attest the executable binaries, inherited environment/configuration, or external commands that produced the measurements. This is a fixable provenance/wording defect, not a reason to weaken the full-ID guard or recursively bind the host. A claim of complete execution provenance would remain unverified and should not pass the operability axis without a matching environment/tool identity contract.

## Observed source identity

Bounded source reads returned snapshots `souji-seat-audit.py#1A5C`, `souji-rev-pin.py#18FF`, `round-13/run-verification.py#8EBD`, `round-14/run-verification.py#658E`, `round-14/run-targeted.py#7C4E`, and `round-14/cache-demonstration.py#0E04`. The observed `HEAD` was `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`. A one-time SHA-256 capture of the six working files was:

- `tools/souji-seat-audit.py`: `8f7b16473755215f4f90a85e3c1a9da2e31d47614919fd631866ddf01c31e2c9`
- `tools/souji-rev-pin.py`: `0b9018e52553d6517b8f805f07163b6a4093d6e842fa79314876084d7b64f756`
- `census/round-13/run-verification.py`: `a10d66ca6728f641fb4144c7fcfb2996ff1940fd7c6e2f69e30230073a9116e8`
- `census/round-14/run-verification.py`: `45e6896c9b24e45c58a49efed38c0f09e642f0779c60dacf3bd1ab487e9b3502`
- `census/round-14/run-targeted.py`: `2d8c61809a0cb99a4f975f9e0e290bf30ef8cd4f4d7267a6569f759da5df6895`
- `census/round-14/cache-demonstration.py`: `3ad63d5b927fedc3aee70c2b2a13c91ad9c83d7bba9c71c5d85844507ef4213`

These are source observations and hashes only; no runner, fixture, or target code was executed and no fresh receipt is claimed.

## Counterexample and evidence

- `tools/souji-rev-pin.py:93-99` defines `input_snapshot` as a bounded owned file/directory snapshot and explicitly says it is **not** a filesystem sandbox or external-runtime attestation.
- `census/round-14/run-verification.py:18-23` copies the inherited environment except `GIT_*`, then overrides selected variables; it leaves `PATH` and other inherited variables intact. Its commands include `python3`, `bash`, and `shellcheck` at `:134-145`. Yet the top-level record stores only `inputs_after` as `input_sha256` and sets `inputs_unchanged_during_run=True` at `:152-159`; the map is derived from `MEASURED_PATHS` at `:32-46`, not those executable identities or the environment.
- `census/round-13/run-verification.py:53-65` likewise retains ambient environment except selected overrides. Its `:451-464` commands resolve `python3`, `bash`, and `shellcheck` through that environment; `:490-496` rechecks only `INPUT_PATHS` and writes the unqualified input fields. `:52` marks `sources-contract` reuse-exempt, and `:144-180` excludes external absolute paths from per-result dependency hashing; that prevents reuse but does not bind the external command to the output receipt.
- `census/round-14/run-targeted.py:21-25,43-51` delegates to the same r14 resolver/run path and writes the same unqualified fields. The demonstration itself is appropriately narrower: `cache-demonstration.py:1048-1054` says its synthetic producer proves only its fixture observation and that the migrated full command suite is not run.

**[INFERENCE] Falsifiable counterexample:** leave every listed repository input byte and revision unchanged, but put a different `shellcheck` executable first on `PATH`. The r14 runner will resolve and invoke that executable (`:18-22,145`), while `input_snapshot` has no path for it and the recorded map is still solely the `MEASURED_PATHS` snapshot (`:32-46,157`). A controlled substitute could therefore change the `shellcheck-warning` result without changing `input_sha256`. This was not executed; it follows from the source’s environment and command resolution. Equivalent unbound identity exists for `python3`/`bash` and inherited environment/configuration.

## Impact and smallest safe correction

**Impacted axis: operability.** This does not falsify the narrower tracked-file equality guarantee; it prevents treating that map as complete measurement provenance. The round-20 preregistration (`.ufo/waves/round-20/preregistration.txt:2-3`) asks for actual helper/wrapper/fixture/corpus file bindings, not host-wide reproducibility, so keep those bindings bounded.

Smallest correction: add an explicit output/schema scope adjacent to `input_sha256` and define `inputs_unchanged_during_run` as applying only to that exact repository-owned path set (for example, `input_sha256_scope: repository-owned measured files only; PATH-resolved executables, inherited environment/configuration, and external commands are not attested`). Add one oracle case holding all measured files fixed while varying a controlled `PATH`-resolved tool; it must confirm the receipt preserves that limitation rather than implying the environment was fingerprinted. If the intended C2 claim expands to complete execution provenance, then the tool/config/environment identities must instead be explicitly captured; do not silently treat the existing file map as doing so.
