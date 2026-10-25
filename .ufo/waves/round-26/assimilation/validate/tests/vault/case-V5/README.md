# case-V5 — ledger row with an absent source path → `NOT-VERIFIED(source-absent)`

Fixture for vault-verification case **V5** in souji-shokunin round 4:

> a ledger row points at a source path that does not exist.
> Expected: `NOT-VERIFIED(source-absent)`.

The case is built so that **every conjunct except source presence passes**:
the vault copy exists, its sha256 equals the row's `vault_sha256`, and the
row's `source_sha256` is the true digest of the exported bytes. The single
failing conjunct is that the recorded `source_path` is absent from disk.
That makes V5 a discriminator, not a smoke test.

## Files

| path | role |
|---|---|
| `make-fixture.sh` | builder: fake vault + absent source path + test ledger + substituted `expected.json` |
| `expected.json` | declaration: the ledger row, the target, the expectation, and the failure modes this case catches |
| `selftest.sh` | proves the fixture encodes the V5 expectation and that the expectation is discriminating (22 checks) |
| `README.md` | this contract |

Nothing here reads or writes the live ledger
(`corpus/knowledge/obsidian-ledger.tsv`), the real vault
(`/home/vgpnk/Documents/shokoknowledge`), or any sibling repo. All state
lives under the fixture root, which defaults to a fresh `mktemp -d`.

## Build

```bash
ROOT=$(bash tests/vault/case-V5/make-fixture.sh --quiet | sed -n 's/^FIXTURE_READY case-V5 //p')
```

Default stdout (without `--quiet`) is a one-line JSON contract on line 1,
then `FIXTURE_READY case-V5 <ROOT>`, then `LEDGER=`, `TARGET=`, `VAULT=`,
`SOURCE_SHA256=`, `VAULT_SHA256=`, `EXPECT=` lines. stderr carries the same
facts as `key=value`.

Options: `--out DIR` (default `mktemp -d`; an existing case-V5 root marked
`.case-V5-fixture` is rebuilt, any other non-empty dir is refused),
`--ledger FILE` (extra copy of the test ledger), `--quiet`, `--print-ledger`
(the row without the header), `--print-hashes`. Exit 0 built, 1 build or
assertion failure, 2 usage.

## What the builder creates

```
<ROOT>/
  .case-V5-fixture          marker; re-running with the same --out rebuilds the tree
  source/                   empty directory (the row's source parent, present)
  vault/
    round-trip-notes.md     0444, 272 bytes, sha256 12e00f27…
  ledger.tsv                header + exactly one data row (below)
  expected.json             expected.json with @FIXTURE_ROOT@ substituted
  .git/                     offline repo context (init only, no commits)
```

The row, tab-separated in ledger column order:

| column | value |
|---|---|
| `source_path` | `<ROOT>/source/round-trip-notes.md` — **absent** |
| `source_sha256` | `12e00f2715df6aa34ffba48dd508834bb602561c6335fd7de475b251e23506ac` |
| `vault_path` | `<ROOT>/vault/round-trip-notes.md` — present, 0444 |
| `vault_sha256` | `12e00f2715df6aa34ffba48dd508834bb602561c6335fd7de475b251e23506ac` (matches the vault file) |
| `exported_at` | `2026-10-18` |
| `note` | `case-V5 source-absent` |

The content digest is asserted at build time (`--print-hashes` prints the
table); a mismatch is a build failure, never a warning.

## Expected verdict

| field | value |
|---|---|
| target | `<ROOT>/source/round-trip-notes.md` |
| verdict | `NOT-VERIFIED` |
| reason | `source-absent` |
| verdict string | `NOT-VERIFIED(source-absent)` |
| receipt | none — vault verification is not a removal receipt |

A harness may render this as one token or as separate verdict/reason fields
(see `accept` in `expected.json`). What must not happen is `SAFE`/`VERIFIED`
(vault-side-only verification) or a collapsed `NOT-SAFE(none)` /
`NOT-SAFE(unreachable)` (the source-absent class must be distinguishable
from both "no receipt" and "target missing").

## Failure modes this case catches

1. **Vault-side-only verification.** The vault copy hashes correctly, so a
   harness that verifies only the vault side reports `VERIFIED`/`SAFE`.
2. **Class collapse.** Reporting `NOT-SAFE(none)` or `NOT-SAFE(unreachable)`
   instead of the distinct `NOT-VERIFIED(source-absent)` — the operator
   cannot tell "the row is good but the file is gone" from "no receipt".
3. **Always-source-absent.** Copying the vault file back to the source path
   must flip the verdict to `SAFE(moved-to-obsidian)`; a harness that
   answers `source-absent` unconditionally fails this control.

Failure mode 3 is exercised by `selftest.sh` (T4); mode 1 and 2 are pinned
by the assertion T3 records.

## Measured baseline (2026-10-18)

`tools/souji-verify.sh` (round-2 tool, sha256 `7efda63bd760…`) answers
`NOT-SAFE(unreachable)` for this target: its absent-target short-circuit
fires before the ledger is consulted, so the row is never seen and the tool
cannot express the source-absent class at all. This is the delta the round-4
vault harness must close — read the ledger row first, then classify the
source side.

```bash
# observed
SOUJI_LEDGER=<ROOT>/ledger.tsv tools/souji-verify.sh <ROOT>/source/round-trip-notes.md
# -> VERDICT	<ROOT>/source/round-trip-notes.md	NOT-SAFE	unreachable	missing path

# control: source present and byte-identical -> the same row verifies
cp <ROOT>/vault/round-trip-notes.md <ROOT>/source/round-trip-notes.md
SOUJI_LEDGER=<ROOT>/ledger.tsv tools/souji-verify.sh <ROOT>/source/round-trip-notes.md
# -> VERDICT	<ROOT>/source/round-trip-notes.md	SAFE	moved-to-obsidian	ledger-row ...
```

## Selftest

```bash
bash tests/vault/case-V5/selftest.sh [--keep] [--out JSON] [--tool PATH]
```

22 checks: build invariants (source absent with parent present, vault 0444,
digests, one-row ledger), substituted `expected.json` consistency, the
candidate-tool probe, the T4 false-source-absent control, and T5 live
surfaces untouched (live ledger sha and row count unchanged, still
header-only). Exit 0 all pass, 1 any fail. `--out JSON` writes a machine
readable result document.

`--tool PATH` selects the candidate (default `<lane>/tools/souji-verify.sh`).
The selftest recognizes the round-2 sha256 (`7efda63b…`) and pins its exact
observed class, `NOT-SAFE(unreachable)`; any other candidate is held to the
r4 contract `NOT-VERIFIED(source-absent)`. The probe was validated against
synthetic candidates in both directions:

| candidate | T3 | T4 control | overall |
|---|---|---|---|
| round-2 tool (installed) | `NOT-SAFE(unreachable)` — pinned | `SAFE(moved-to-obsidian)` | PASS 22/22 |
| stub answering `NOT-VERIFIED(source-absent)` always | passes T3 | **FAIL** (never verifies) | FAIL 20/22 |
| stub that verifies when the source exists | passes T3 | passes | PASS 22/22 |

The middle row is the point: the case cannot be satisfied by answering
`source-absent` unconditionally.

## Integration note

`source/` is intentionally an empty directory with no placeholder file: the
absence must be exactly the file, not a missing tree. If a future harness
needs to move the vault copy back, do it under the fixture root only — never
against the real vault.

Builder invocation forms verified 2026-10-18 (sandbox copy, TMPDIR pinned):
no-args (mints under `$TMPDIR`), `--out DIR`, and positional `DIR` all exit 0
and produce a valid root with the expected layout.
