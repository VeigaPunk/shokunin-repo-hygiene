# case-V4 — ledger row with an absent vault path → `NOT-VERIFIED(vault-absent)`

Fixture for fixture case **V4** of the round-4 Obsidian-CLI vault
verification family (the vault-side mirror of case-V5's source-absent case):

> V4: a ledger row points at a vault path that does not exist.
> Expected: `NOT-VERIFIED(vault-absent)`.

The case proves the **vault side is a required conjunct** of the ledger
receipt: a row whose source side matches perfectly still cannot verify when
the recorded vault copy is absent — and that failure has its own class
(`vault-absent`), distinct from "no receipt at all".

## Files

| path | role |
|---|---|
| `make-fixture.sh` | builder; creates the source file, the (empty) vault dir, and the test ledger |
| `expected.json` | declaration: the ledger row the harness should find, the single target, and the `NOT-VERIFIED(vault-absent)` expectation |
| `selftest.sh` | proves the build invariants and the discriminating controls (T1–T5) |
| `README.md` | this contract |

`expected.json` uses the placeholder `@FIXTURE_ROOT@`; `make-fixture.sh`
writes the substituted copy to `<ROOT>/expected.json`.

## What the builder creates

```
<FIXTURE_ROOT>/
  .case-V4-fixture          marker; re-running with the same --out rebuilds the tree
  source/round-trip-notes.md    TARGET: present, mode 0444, sha256 matches both row hashes
  vault/                        exists, but the row's vault file is NOT created
  ledger.tsv                    header + exactly one row (vault-absent-row)
  expected.json                 substituted copy of this case's expected.json
```

The row records `source_sha256` and `vault_sha256` as the true digest of the
exported bytes (`d9cae6dfd163…`, 308 bytes). The source file on disk carries
exactly those bytes, so the **only** failing conjunct is the vault path's
presence — absence is exactly the file (its parent `vault/` exists), not a
missing tree.

## Consumption contract

```bash
# 1. build (default root: fresh mktemp -d; nothing else is written)
ROOT=$(bash tests/vault/case-V4/make-fixture.sh --quiet | sed -n 's/^FIXTURE_READY case-V4 //p')

# 2. evaluate by the exact absolute path, with the fixture's own ledger
SOUJI_LEDGER="$ROOT/ledger.tsv" tools/souji-verify.sh "$ROOT/source/round-trip-notes.md"
```

- r2 tool (`tools/souji-verify.sh`) observed output today:
  `NOT-SAFE` / `none` / evidence contains `obsidian=vault-unreachable` —
  that is the class-collapse the r4 vault harness must refine into
  `NOT-VERIFIED(vault-absent)`.
- r4 expectation (binding): `NOT-VERIFIED(vault-absent)` — never
  `SAFE`/`VERIFIED`, and not a bare `NOT-SAFE(none)`/`NOT-SAFE(unreachable)`.
- The live ledger `corpus/knowledge/obsidian-ledger.tsv` and the real vault
  are never touched; the fixture is self-contained under its root.

## Verdict matrix (binding)

| step | vault path state | expected |
|---|---|---|
| as built | absent | `NOT-VERIFIED(vault-absent)` |
| T4 control (selftest materializes the vault file) | present, byte-identical | `SAFE(moved-to-obsidian)` (r2 names) / `VERIFIED` (r4 names) |

The control exists so the case cannot pass by always answering
`vault-absent`: materializing the vault copy flips the verdict.

## Failure modes caught

- **source-side-only verification** — the source hash matches the row, so a
  harness that never checks the vault side reports `VERIFIED`/`SAFE`; caught
  by `expect.verdict`.
- **class collapse** — answering `NOT-SAFE(none)` (or `unreachable`) instead
  of the distinct `NOT-VERIFIED(vault-absent)`; caught by `expect.reason`.
- **false vault-absent** — answered `vault-absent` for a vault-present pair;
  caught by the T4 control.

## Harness-token caveat (must_not_be)

`must_not_be` deliberately does **not** list the bare token `VERIFIED`:
runner-26 and runner-28 apply `must_not_be` entries as substring vetoes, and
`VERIFIED` is a substring of the correct answer `NOT-VERIFIED(vault-absent)`
(a self-collision that vetoes every correct response — observed 2026-10-18
with runner-28's judge). A false `VERIFIED` answer is still caught by the
verdict-class comparison (`want = NOT-VERIFIED`), which a `VERIFIED` answer
cannot satisfy. The selftest (T2) asserts this invariant.

## Determinism

Fixed content bytes; paths vary per run. The builder asserts the content
digest against the `SHA_ROUND_TRIP` constant and the substituted
`expected.json` parses. Exit codes: 0 built, 1 build/assertion failure,
2 usage.

## Selftest

```bash
bash tests/vault/case-V4/selftest.sh            # exit 0 all pass
bash tests/vault/case-V4/selftest.sh --out /tmp/v4-selftest.json
```

T1 build invariants (vault absent, source present 0444, digest, ledger
shape), T2 substituted expected.json, T3 r2-tool delta
(`NOT-SAFE(none)` + `vault-unreachable` note, never `SAFE`), T4
materialize-control (`SAFE(moved-to-obsidian)`), T5 live ledger unchanged
and header-only.
