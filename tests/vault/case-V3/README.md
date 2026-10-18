# case-V3 — source file differs from the ledger row's `source_sha256` → `NOT-VERIFIED(source-hash)`

Fixture for vault-verification case **V3** (souji-shokunin round 4, seat S11):

> V3: the source file's content no longer matches the ledger row's
> `source_sha256` (edited after export). The vault copy still matches the row
> exactly. Expected: `NOT-VERIFIED(source-hash)`.

The case pins the **source-side hash** as a required conjunct of a
`moved-to-obsidian` receipt. The vault side is fully present and
hash-matching, so a tool that verifies only the vault copy reports
`VERIFIED` and is caught.

## Files

| path | role |
|---|---|
| `make-fixture.sh` | builder; creates the fake vault, the source tree, the test ledger, and the substituted `expected.json` |
| `expected.json` | declaration (template with `@FIXTURE_ROOT@`); the builder writes the substituted copy to `<ROOT>/expected.json` |
| `README.md` | this contract |
| `selftest.sh` | proves the fixture encodes the V3 expectation and that the expectation is discriminating |

`selftest.sh` consumes the builder; `expected.json` is the declaration of
record. Both run with no writes outside mktemp dirs.

## What the builder creates

```
<FIXTURE_ROOT>/
  .case-V3-fixture            marker; re-running with the same --out rebuilds the tree
  source/src/edited-notes.md      TARGET  edited after export (primary)
  source/src/subtle-notes.md      TARGET  one-byte edit (dropped trailing newline)
  source/src/matched-notes.md     TARGET  control: byte-identical both sides
  vault/edited-notes.md           export-time bytes, mode 0444
  vault/subtle-notes.md           export-time bytes, mode 0444
  vault/matched-notes.md          byte-identical to the source, mode 0444
  ledger.tsv                  header + exactly 3 rows (export-time digests)
  expected.json               this file with @FIXTURE_ROOT@ substituted
```

Git: `git init -q -b master` on the fixture root (offline, no commits), so
the root behaves like a real lane repo. No fetch, no network.

## Consumption contract

```bash
ROOT=$(bash tests/vault/case-V3/make-fixture.sh --quiet | sed -n 's/^FIXTURE_READY case-V3 //p')
```

- stdout, default: line 1 = single-line JSON
  `{case,root,ledger,targets,expect}`; line 2 = `FIXTURE_READY case-V3 <ROOT>`;
  then `LEDGER=`, `TARGET=`, `TARGET_SUBTLE=`, `TARGET_MATCHED=`,
  `VAULT_EDITED=`, `VAULT_SUBTLE=`, `VAULT_MATCHED=`, `SOURCE_SHA256=`
  (row value), `SOURCE_SHA256_ACTUAL=` (current source), `EXPECT=`.
- `--quiet`: the `FIXTURE_READY` line plus the `KEY=VALUE` lines only.
- `--print-ledger`: the three concrete rows (no header).
- `--print-hashes`: the content digest table.
- Exit codes: 0 built (also for `--print-*`), 1 build/assertion failure, 2 usage.

`<ROOT>/ledger.tsv` is the canonical test ledger. `--ledger FILE` additionally
copies it to FILE. The live ledger `corpus/knowledge/obsidian-ledger.tsv` is
never written and stays header-only.

## Verdict matrix (binding)

| target | row source_sha256 | source file now | vault file now | expected |
|---|---|---|---|---|
| `edited-notes.md` | export-time digest | **differs** (edited) | matches row | `NOT-VERIFIED(source-hash)` |
| `subtle-notes.md` | export-time digest | **differs by 1 byte** | matches row | `NOT-VERIFIED(source-hash)` |
| `matched-notes.md` | digest | matches row | matches row | `VERIFIED` |

- For the two negative targets the exact pair `NOT-VERIFIED` + reason
  `source-hash` is binding; the class `SAFE`/`VERIFIED` and the collapsed
  class `NOT-SAFE(...)` are failures.
- For the control only `VERIFIED` is binding.
- Each expect entry carries its own `accept` block. The doc-level `accept`
  keeps the canonical `exact` (`NOT-VERIFIED(source-hash)`) plus
  `reason_aliases_accepted`; the two negative targets each carry a
  per-target `accept.exact` list holding the bare class token and the
  sha/hash spelling aliases the r4 impls emit (`source-hash-mismatch`,
  `source-sha-mismatch`, `source-sha256-mismatch`,
  `source-digest-mismatch`), with `contains: ["source"]` so a wrong-side
  (`vault-*`) answer cannot pass. The `VERIFIED` control is judged only by
  its own per-target block.
- `must_not_be` is scoped by `must_not_be_applies_to` to the primary target
  (V2 house pattern): the class vetoes and the wrong-side reason vetoes
  apply to the primary only, so the `VERIFIED` control's correct answer is
  never vetoed. The bare token `VERIFIED` is deliberately absent from every
  veto list: some harnesses apply `must_not_be` as a substring check and
  `VERIFIED` is a substring of the correct `NOT-VERIFIED(...)`. A false
  `VERIFIED` answer is still caught by the verdict-class comparison.

## Discriminators

- **vault-side-only verification**: the vault digest equals the row's
  `vault_sha256`, so a harness that skips the source hash reports
  `VERIFIED`/`SAFE` — caught by the expected verdict.
- **class collapse**: `NOT-SAFE(none)` / `NOT-SAFE(unreachable)` instead of
  the distinct `NOT-VERIFIED(source-hash)` — caught by the expected reason.
- **blanket answer**: a tool that always answers `source-hash` fails the
  `VERIFIED` control.
- **byte-exactness**: the subtle target differs by exactly one byte (a
  dropped trailing newline), catching size- or mtime-based shortcuts.

## Cross-check against the r2 tool

`tools/souji-verify.sh` predates the r4 `VERIFIED` vocabulary. With
`SOUJI_LEDGER=<ROOT>/ledger.tsv`:

- primary target → `NOT-SAFE` with `obsidian=source-sha-mismatch` in the
  evidence field;
- control target → `SAFE` + `moved-to-obsidian`.

`selftest.sh` runs exactly this pair and pins it.

## Determinism

Content bytes are fixed and asserted at build time against five sha256
constants (and byte counts) cross-checked in `expected.json`; a drift is a
hard failure. Paths vary per run. Two builds at different roots produce
byte-identical files with equal digests.
