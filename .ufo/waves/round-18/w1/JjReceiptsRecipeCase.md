STATUS: DONE — Added owner-specific jj quarantine recipe assertions and delivered the scoped patch.

Axis: operability.

## Changed files and behavior

- Own-clone implementation: `tests/fixtures/r17-jj-receipts.sh`.
- Patch handoff: `.ufo/waves/round-18/w1/JjReceiptsRecipeCase.patch`.
- Added `J13` for a jj-colocated `kama-shokunin` repo, requiring exactly one dry-run commit recipe with `--as kama` and no `--as souji`; added `J13-own` for `souji-shokunin`, requiring `--as souji` and no `--as kama`. The fixture uses real jj 0.45.1 when available and otherwise creates a git-emulated `.jj/repo/config.toml` plus a query-only `jj` shim. It skips only if that emulated identity setup cannot be created.
- Existing fixture cases remain in their previous order and retained their prior statuses in both runs (31 PASS, 2 J6 SKIP); only the two new checks differ between base and patched recipe runs.

## Evidence and verdict

- Base source `tools/souji-quarantine.sh:246-251` hardcodes `--as souji`. The lane identity convention at `scripts/hyaku/jj-lane.sh:105-110` reads `user.name` and removes `-shokunin`.
- Fixture additions: `tests/fixtures/r17-jj-receipts.sh:283-340` (real/emulated setup and recipe assertions), `:748-774` (J13/J13-own), and `:1150` (invocation).
- Extracted base quarantine SHA-256: `83cc3ce1331bf75ed23b9148ad82b6f0881e9eda1d9a283a224f0318d6ab1de3`. The temporary patched copy at `/var/tmp/souji-r18-JjReceiptsRecipeCase/patched-tools/souji-quarantine.sh` changed only `q_jj_commit_recipe`, deriving the name with `jj --ignore-working-copy config get user.name`, removing `-shokunin`, and using `protocol` if there is no lane suffix; its SHA-256 was `0a685f797f4bf8196d3fa962883c532be57271bc95c4ea65889e3b56129bd92e`.
- Both fixture runs observed `JJ\t/home/vgpnk/.local/bin/jj\tjj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5`.

Exact executed fixture commands and relevant output:

```text
bash /var/tmp/souji-r18-JjReceiptsRecipeCase/lane/tests/fixtures/r17-jj-receipts.sh --tool-dir /var/tmp/souji-r18-JjReceiptsRecipeCase/base-tools
CASE\tJ13\tFAIL\tmode=jj-0.45.1 exit=0 result=DRY-RUN-PASS recipe=jj-lane.sh commit /var/tmp/r17-jj-receipts.FlcQxH/fleet/kama-shokunin --as souji
CASE\tJ13-own\tPASS\tmode=jj-0.45.1 exit=0 result=DRY-RUN-PASS recipe=jj-lane.sh commit /var/tmp/r17-jj-receipts.FlcQxH/fleet/souji-shokunin --as souji
SUMMARY\ttotal=35\tfailed=1\tskipped=2
exit: 1

bash /var/tmp/souji-r18-JjReceiptsRecipeCase/lane/tests/fixtures/r17-jj-receipts.sh --tool-dir /var/tmp/souji-r18-JjReceiptsRecipeCase/patched-tools
CASE\tJ13\tPASS\tmode=jj-0.45.1 exit=0 result=DRY-RUN-PASS recipe=jj-lane.sh commit /var/tmp/r17-jj-receipts.ORKzbm/fleet/kama-shokunin --as kama
CASE\tJ13-own\tPASS\tmode=jj-0.45.1 exit=0 result=DRY-RUN-PASS recipe=jj-lane.sh commit /var/tmp/r17-jj-receipts.ORKzbm/fleet/souji-shokunin --as souji
SUMMARY\ttotal=35\tfailed=0\tskipped=2
exit: 0

shellcheck /var/tmp/souji-r18-JjReceiptsRecipeCase/lane/tests/fixtures/r17-jj-receipts.sh
(no diagnostics)
```

The failing base `J13` is the intended regression control; the patched recipe passes both owner cases and all existing non-skipped cases. Smallest fix evidenced: derive the `--as` id from the colocated repo's recorded `user.name`, rather than hardcoding `souji`.

## Risks / blockers

- The real jj 0.45.1 branch was exercised. The git-emulated fallback is implemented but was not exercised here because real jj 0.45.1 was available.
- No blocker. No tools were installed or updated.