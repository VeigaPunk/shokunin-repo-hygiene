# case-V7 — ledger row with extra columns beyond the 6 canonical → `VERIFIED`

Fixture for `souji-shokunin` round 4 (Obsidian-CLI vault verification), seat S15.

> V7: a ledger row carries extra columns beyond the 6 canonical
> (source_path, source_sha256, vault_path, vault_sha256, exported_at, note).
> Expected: **VERIFIED** — the canonical positions decide, extra columns are
> ignored, the note (column 6) is still read, and hash checking is not
> weakened.

## Files

| path | role |
|---|---|
| `payload/source/src/*.md` | source-side payloads (4 files) |
| `payload/vault/*.md` | fake-vault payloads (4 files; 3 byte-identical, 1 edited) |
| `make-fixture.sh` | builder: payload tree + test ledger + substituted `expected.json` |
| `expected.json` | declaration: 4 ledger rows, 4 targets, armed verdicts, failure modes |
| `selftest.sh` | 25 checks: build invariants, ledger shape, expected.json, r2 baseline, disarmed control, live-surface guard |
| `README.md` | this contract |

`make-fixture.sh` writes only under `--out` (default: fresh `mktemp -d`), plus
`--ledger FILE` when given. The live ledger
(`corpus/knowledge/obsidian-ledger.tsv`) and the real vault
(`/home/vgpnk/Documents/shokoknowledge`) are never touched. The built root gets
an offline `git init` (no commits) so repo-discovery paths behave as on a real
lane; no fetch/push/commit/branch/checkout/reset/rebase is ever run.

## The four rows (ledger.tsv)

| # | file | cols | extra columns | row note (col 6) | expected |
|---|---|---|---|---|---|
| 1 | `extra-cols-notes.md` | **7** | `exported_by=souji-fixture` | `case-V7 extra-cols` | `VERIFIED` (primary) |
| 2 | `extra-cols-8-notes.md` | **8** | `exported_by=…` + empty trailing | `case-V7 extra-cols-8` | `VERIFIED` |
| 3 | `six-cols-notes.md` | 6 | — (control) | `case-V7 six-cols control` | `VERIFIED` |
| 4 | `extra-cols-mismatch.md` | **7** | `exported_by=souji-fixture` | `case-V7 extra-cols mismatch` | `NOT-VERIFIED(vault-hash-mismatch)` |

Rows 1–3: both sides exist and both digests equal the row's recorded values —
only the column count varies, so a parser that rejects >6 columns fails rows 1
and 2 while the control (row 3) passes. Row 4's vault copy was edited after
export (actual digest `6e28bf53…`, recorded `2ceca233…`): ignoring extra columns
must not weaken the vault-side hash check.

Content digests (fixed, asserted at build time):

| file | sha256 |
|---|---|
| `six-cols-notes.md` | `ada33bd81eeab6375081b16fe83dc8db9418131bc62e97a68b6439ac6a68a781` |
| `extra-cols-notes.md` | `1543cfa1785f270374b6f16407440152cbfd27dd08b1ad1f24f71267ab456206` |
| `extra-cols-8-notes.md` | `f2b8420064e81b6efc0eab1917cbb4ff6a088cef150251c66d4b3545a36eef53` |
| `extra-cols-mismatch.md` (source) | `2ceca233cfc70cfd9a07e6e889ea21951c9ee433250cc6b6cc0cd6e9bf3f4239` |
| `extra-cols-mismatch.md` (vault) | `6e28bf53541405576602483a415a368a088845fe63f683085a379d7d2b1b632f` |

Vault copies are mode `0444` (read-only signal).

## Consumption

```bash
# build (default root: fresh mktemp -d)
ROOT=$(bash tests/vault/case-V7/make-fixture.sh --quiet | sed -n 's/^FIXTURE_READY case-V7 //p')

# evaluate by exact absolute path, with the case's own ledger
SOUJI_LEDGER="$ROOT/ledger.tsv" SHOKUNIN_ROOT="$ROOT" \
  bash tools/souji-verify.sh \
    "$ROOT/source/src/extra-cols-notes.md" \
    "$ROOT/source/src/extra-cols-8-notes.md" \
    "$ROOT/source/src/six-cols-notes.md" \
    "$ROOT/source/src/extra-cols-mismatch.md"
```

Builder CLI: `make-fixture.sh [--out DIR] [--ledger FILE] [--quiet]
[--print-ledger] [--print-hashes]`. stdout: line 1 JSON
`{case,schema,root,ledger,targets,expect}`, line 2 `FIXTURE_READY case-V7
<ROOT>`, then `KEY=VALUE` lines; `--quiet` keeps only the latter two groups.
Exit codes: 0 built, 1 build/assertion failure, 2 usage. The runner interface
(`runner-28.sh`) — `--quiet` first, `FIXTURE_READY` line, `<ROOT>/ledger.tsv`,
`expected.json` targets/expect — is satisfied.

## Measured baselines (2026-10-18)

**r2 tool** (`tools/souji-verify.sh`, sha256 `7efda63b…`; it reads rows as
`IFS=TAB read -r sp ss vp vs _rest`, so extras land in `_rest` and are
ignored). Command: `SOUJI_LEDGER="$ROOT/ledger.tsv" SHOKUNIN_ROOT="$ROOT"
bash tools/souji-verify.sh <4 targets>`; observed:

```
VERDICT  …/extra-cols-notes.md    SAFE  moved-to-obsidian  ledger-row vault=… source-sha256=1543cfa1785f
VERDICT  …/extra-cols-8-notes.md  SAFE  moved-to-obsidian  ledger-row vault=… source-sha256=f2b8420064e8
VERDICT  …/six-cols-notes.md      SAFE  moved-to-obsidian  ledger-row vault=… source-sha256=ada33bd81eea
VERDICT  …/extra-cols-mismatch.md NOT-SAFE none  pushed=no-introducing-commit; obsidian=vault-sha-mismatch; …
```

**Disarmed** (header-only ledger): all four targets report `NOT-SAFE(none)` —
the row is the receipt.

**r4 delta this case pins**: the `VERIFIED`/`NOT-VERIFIED` vocabulary, the
`NOT-VERIFIED(vault-hash-mismatch)` reason class for row 4, and **note
recording** — the r2 tool never surfaces the row's note text; the r4 harness
should carry `case-V7 extra-cols` (etc.) in its verdict output. The notes are
recoverable from column 6 for every row (`awk -F'\t' 'NR>1 {print $6}'`),
asserted by the selftest.

## Discrimination (what fails if the tool is wrong)

| wrong behavior | caught by |
|---|---|
| rejects rows with >6 columns (`malformed-row`/`column-count` reasons) | expect[0], expect[1] (`must_not_be`) |
| ignores extras by skipping hash checks | expect[3] (edited vault must stay NOT-VERIFIED) |
| splits on whitespace, mishandles the empty trailing field | expect[1] |
| never returns VERIFIED (blanket failure) | expect[2] control |
| drops the note column | note_recording check |

## Selftest

```
bash tests/vault/case-V7/selftest.sh [--keep] [--out JSON] [--tool PATH]
```

25 checks: T1 build invariants (pair digests, 0444 modes, mismatch pair
differs), T2 ledger shape (6/7/8/6/7 columns; the four notes recover from
column 6), T3 substituted `expected.json` validity (4 targets, 3×VERIFIED +
1×NOT-VERIFIED), T4 r2 baseline (three SAFE+moved-to-obsidian, one NOT-SAFE
with `vault-sha-mismatch`), T5 disarmed control (0 SAFE, 4×NOT-SAFE(none)),
T6 live-surface guard (live ledger header-only and unchanged). Latest run:
`pass=25 fail=0` (`tests/results/v7-selftest.json`).
