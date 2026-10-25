# case-V6 — ledger TSV with CRLF line endings + a valid row

Fixture for the round-4 vault-verification harness (`souji-vault-fixture/1`
schema, same family as case-V1/V4/V5). Question: does a ledger whose lines
end in CRLF still parse, and does a valid row still verify?

| field | value |
| --- | --- |
| fixture root | printed by `make-fixture.sh` (`FIXTURE_READY V6 <ROOT>`); default `mktemp -d` |
| artifact | `<ROOT>/src/payload.md` (byte-identical copy at `<ROOT>/vault/payload.md`) |
| primary ledger | `<ROOT>/ledger-crlf.tsv` — header + 1 valid row, CRLF end-to-end |
| expected verdict | `VERIFIED(moved-to-obsidian)` (r2 tool names: `SAFE(moved-to-obsidian)`) |
| judged probes | `probes[]` in `expected.json`: `crlf-valid-row`, `lf-control` |

## Probes

- **crlf-valid-row** — `<ROOT>/ledger-crlf.tsv` -> `VERIFIED(moved-to-obsidian)`. The assignment's case.
- **lf-control** — `<ROOT>/ledger-lf-control.tsv` -> `VERIFIED(moved-to-obsidian)`. Identical row, LF endings; isolates CRLF as the only variable. The two outputs are byte-identical under the r2 tool (measured).
- **boundary (informational, not judged)** — `<ROOT>/ledger-crlf-truncated.tsv`: CRLF row truncated after the 4 hash columns; the CR then rides on `vault_sha256`, so the digest comparison fails (`vault-sha-mismatch`). A schema-tolerant harness that strips CR from every field may legitimately still verify it, so no verdict is required of candidate harnesses; `selftest.sh` pins it against the r2 tool.

## CRLF mechanics (why the row survives)

`ledger_lines()` skips the header by prefix match (`source_path` + TAB), so a
CRLF header is skipped like an LF one. `try_obsidian()` reads each row with
IFS=TAB (`read -r sp ss vp vs _rest`): the trailing CR is not TAB-separated,
so it stays attached to the last field of the line. In the canonical
6-column row that field is `note` (absorbed by `_rest`), leaving
`vault_sha256` (field 4) clean -> the row matches -> verified. Only when the
row is truncated to 4 columns does the CR land on the hash itself ->
mismatch. That is the break boundary this case pins.

## Build / run

```
bash make-fixture.sh [--out DIR] [--ledger FILE] [--quiet]   # default: mktemp -d, ledger copy -> tests/vault/ledger-V6.tsv
bash selftest.sh [--tool PATH] [--out JSON] [--keep]         # 13 checks; result -> tests/results/v6-selftest.json
```

Consumers: runner-26 reads `probes[]` (per-probe ledger/target/verdict);
runner-28 reads `probes[]` too (ledger resolved against the case dir, target
against its `--out` root — the builder refreshes the case-dir ledger copies to
point at the current root); runner-29 has an explicit case-V6 branch that
resolves both against its `--out` root with a case-dir fallback, and
additionally judges `ledger-crlf-truncated.tsv` as `NOT-VERIFIED` when present
(stricter than this case's judged contract — see the boundary note above).

## Files

- `make-fixture.sh` — builder (writes only `<ROOT>/**` and `--ledger`)
- `expected.json` — contract, schema `souji-vault-fixture/1`; `@FIXTURE_ROOT@` substituted by the builder
- `selftest.sh` — 13 checks incl. the CRLF/LF byte comparison; writes `tests/results/v6-selftest.json`
- `.gitignore` — guards against accidental in-tree `--out` materialization

## Safety

The builder never reads or writes the live ledger
(`corpus/knowledge/obsidian-ledger.tsv` stays header-only), the real vault
(`/home/vgpnk/Documents/shokoknowledge`), or any sibling repo. No Obsidian
process, CLI or network is involved; the GUI launcher `/usr/bin/obsidian` is
never executed. Fixture content is fixed, so the payload sha256 is constant
(`127ac886a92b…`); ledger rows embed per-root absolute paths, so ledger file
hashes vary per build root by design.
