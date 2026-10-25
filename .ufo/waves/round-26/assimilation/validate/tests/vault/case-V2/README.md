# case-V2 — vault-side tamper fixture

Round 4 (Obsidian-CLI vault verification), seat S10. Spec case **V2**: a
vault file whose content differs from what the ledger's `vault_sha256`
says (tamper case). Expected verdict: **NOT-VERIFIED** with a reason
naming a **vault-side hash mismatch** — `NOT-VERIFIED(vault-hash-mismatch)`.

## Layout

| path | role |
| --- | --- |
| `payload/source/src/*.md` | export-time source bytes (copied into the fixture root) |
| `payload/vault/*.md` | vault copies; `tamper-notes.md` and `subtle-notes.md` are edited after export |
| `make-fixture.sh` | builder: root + `ledger.tsv` + substituted `expected.json`; `--selftest` asserts fixture coherence (A1–A8) |
| `expected.template.json` | declaration with `@FIXTURE_ROOT@` placeholders |
| `expected.json` | placeholder-form copy (same as the template); the builder writes the substituted copy to `<ROOT>/expected.json` (`--case-copy` also refreshes this one) |
| `selftest.sh` | 26 checks (T1–T5) including tool probes; `--out JSON` |

Build:

```
bash make-fixture.sh [--out DIR] [--ledger FILE] [--quiet]
bash make-fixture.sh --selftest          # A1–A8, exit 0 = coherent
bash selftest.sh [--out tests/results/v2-selftest.json]
```

## The three targets

| target | source | vault | expected |
| --- | --- | --- | --- |
| `tamper-notes.md` | `59bea10a…`, matches row | `91d9f779…`, **same 215 bytes**, differs from row | `NOT-VERIFIED(vault-hash-mismatch)` |
| `subtle-notes.md` | `a0d7a278…`, matches row | `f1ebc6ec…`, **1 byte shorter**, differs from row | `NOT-VERIFIED(vault-hash-mismatch)` |
| `matched-notes.md` | `2aa2322d…` | `2aa2322d…` (identical) | `VERIFIED` |

The ledger row for each pair records the **export-time** digest on both
sides, so for the tamper pairs the source side still matches and only the
vault-side conjunct fails.

## Why the tamper pair is shaped this way

- **Same byte count** (primary): a size- or mtime-based shortcut cannot
  distinguish the tampered vault copy from the export-time bytes — only a
  real content hash can.
- **One byte shorter** (subtle): catches coarse equality (prefix, length,
  truncated read) that would pass a same-length tamper.
- **Matched control**: a tool that answers mismatch unconditionally fails
  the control, so the case cannot pass by always returning NOT-VERIFIED.
- **Vault files are `0444`**: the tamper is content, not permissions; a
  tool must hash the file regardless of mode.

## Vocabulary

- r4 harness: verdict `NOT-VERIFIED`, reason `vault-hash-mismatch`.
- r2 baseline (`tools/souji-verify.sh`, sha `7efda63b…`): `NOT-SAFE` /
  `none` with `obsidian=vault-sha-mismatch` in the evidence field. The
  selftest pins this exact class for the r2 sha and holds any other
  candidate to the r4 contract.
- `accept.reason_aliases_accepted` in `expected.json` lists the reason
  spellings accepted: any string containing `vault` + (`hash`/`sha`/
  `digest`) + `mismatch` (or `drift`) satisfies the case.

## Safety

- The live ledger `corpus/knowledge/obsidian-ledger.tsv` is never written;
  the fixture ledger lives at `<ROOT>/ledger.tsv`. T5 asserts the live
  ledger stays header-only and unchanged.
- The real vault is never read from or written to.
- The builder only runs `git init` (offline, no commits); no fetch/push/
  commit/branch/checkout/reset/rebase anywhere.
- The built root carries a `.case-V2-fixture` marker; rebuilds delete only
  a marked root, any other non-empty `--out` is refused.
