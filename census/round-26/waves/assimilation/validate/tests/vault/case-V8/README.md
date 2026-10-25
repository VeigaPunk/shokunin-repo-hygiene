# case-V8 — space-bearing names → `VERIFIED` (receipt `moved-to-obsidian`)

Fixture for fixture case **V8** in the round-4 Obsidian-CLI vault
verification contract:

> V8: vault file + source file whose names contain spaces. Expected: VERIFIED.

The case proves the ledger gate survives paths with **literal spaces** on
both sides: the source file and the vault file are deliberately different
names (`meeting notes 2026-10.md` → `Meeting Notes 2026-10.md`, the shape a
real export produces when the note title is applied), both containing
spaces, and the ledger row matches **source path + source sha256 + vault
path + vault sha256** (all four conjuncts).

## Files

| path | role |
|---|---|
| `make-fixture.sh` | builder; creates the source file, the fake vault, the auxiliary control pair, and the per-case ledger |
| `expected.json` | declaration: the ledger row the tool SHOULD find, the target, and the expected verdict (`@FIXTURE_ROOT@` placeholder, substituted copy written into the fixture root) |
| `selftest.sh` | executable proof: builds the fixture, asserts the invariants, and runs the installed `tools/souji-verify.sh` armed/disarmed |
| `README.md` | this contract |

## What the builder creates

```
<ROOT>/
  .case-V8-fixture                 marker; re-running with the same --out rebuilds
  source/meeting notes 2026-10.md  TARGET (sha256 2fc29f1f…, 225 B)
  vault/Meeting Notes 2026-10.md   byte-identical copy, mode 0444
  source/control notes.md          auxiliary control (sha256 3f5d8d2f…, 143 B)
  vault/Control Notes.md           byte-identical control copy, mode 0444
  ledger.tsv                       copy of the ledger written to --ledger
  expected.json                    @FIXTURE_ROOT@-substituted copy
```

and (re)writes the per-case ledger at `tests/vault/ledger-V8.tsv`
(override with `--ledger FILE`) as **header row + exactly one data row**:

```
source_path<TAB>source_sha256<TAB>vault_path<TAB>vault_sha256<TAB>exported_at<TAB>note
<ROOT>/source/meeting notes 2026-10.md<TAB>2fc29f1f…<TAB><ROOT>/vault/Meeting Notes 2026-10.md<TAB>2fc29f1f…<TAB>2026-10-18<TAB>case-V8 space-bearing names
```

Both path fields carry literal spaces; the columns are separated by TABs.
A parser that splits on runs of whitespace breaks the path fields at the
spaces and cannot match the row — that is a caught failure mode.

`make-fixture.sh` never writes the live ledger
`corpus/knowledge/obsidian-ledger.tsv` (it stays header-only) and never
touches the real vault. The fixture root is `git init -q -b master`ed
(offline, no commits, no refs), so the `pushed` receipt cannot fire and the
verdict is observable only through the ledger.

## Verdict matrix (binding)

| target | armed (row present) | disarmed (header-only ledger) |
|---|---|---|
| `source/meeting notes 2026-10.md` (TARGET) | `VERIFIED` (receipt `moved-to-obsidian`) | `NOT-VERIFIED` |
| `source/control notes.md` (auxiliary) | `NOT-VERIFIED` | `NOT-VERIFIED` |

- For the target the exact pair `VERIFIED` + `moved-to-obsidian` is binding
  under the round-4 vocabulary; the r2 tool reports the same pair under r2
  names (`SAFE` + `moved-to-obsidian`) — see `expected.json` "crosscheck".
- The auxiliary control is byte-identical on both sides but has no ledger
  row: the row is the receipt, not the copy. It is declared under
  `auxiliary_checks`, **not** in `targets`, so runners evaluating the
  single-target contract are unaffected; `selftest.sh` exercises it.

## Consumption contract

```bash
# 1. build (default root: fresh mktemp -d)
ROOT=$(bash tests/vault/case-V8/make-fixture.sh --quiet | sed -n 's/^FIXTURE_READY V8 //p')

# 2. evaluate the target by its exact absolute path — quote it (spaces!)
env SOUJI_LEDGER="$ROOT/ledger.tsv" tools/souji-verify.sh "$ROOT/source/meeting notes 2026-10.md"
#   r2 tool -> VERDICT<TAB>…<TAB>SAFE<TAB>moved-to-obsidian<TAB>ledger-row vault=… source-sha256=2fc29f1f5638

# 3. disarmed check — header-only ledger, same target
HDR_ONLY=$(mktemp); printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$HDR_ONLY"
env SOUJI_LEDGER="$HDR_ONLY" tools/souji-verify.sh "$ROOT/source/meeting notes 2026-10.md"
#   -> NOT-SAFE (no matching ledger row)
```

stdout contract of the builder: line 1 = JSON
`{case,root,targets,expect,vault,ledger,sha256}`; line 2 =
`FIXTURE_READY V8 <ROOT>`. **The third token is the ROOT, never the
target** — the target path contains spaces and runners parse that line with
`FIXTURE_READY\s+\S+\s+(\S+)`; the space-bearing target is carried by the
JSON line, the `TARGET=`/`SOURCE_FILE=` KEY=VALUE lines, and
`<ROOT>/expected.json`. `--quiet` prints KEY=VALUE lines plus the same
`FIXTURE_READY` line. Exit codes: 0 ok, 1 build/assertion failure, 2 usage.

## Failure modes caught

1. **Unquoted path handling** — word-splitting anywhere in the pipeline
   fails to find the file (or the row) and reports NOT-VERIFIED.
2. **Basename matching** — vault and source basenames differ, so matching
   on basename instead of the exact full path cannot receipt this pair.
3. **Whitespace column splitting** — the ledger row's path fields contain
   literal spaces; splitting on spaces instead of TABs breaks matching.
4. **Secret-shape false positive** — no path component matches the
   secrets-refusal shapes; refusing this target for secret reasons is wrong.

## Determinism

Content is fixed; two builds at different roots produce byte-identical
files and equal sha256 values (paths vary per run). The builder asserts
both content constants and cross-checks `expected.json`; a drift is a hard
failure. `--out` re-runs are safe only on a directory carrying the
`.case-V8-fixture` marker (or an empty directory); anything else non-empty
is refused rather than deleted.

## Rebuild / verify

```
bash make-fixture.sh [--out DIR] [--ledger FILE] [--quiet] [--skip-ledger] [--print-row] [--print-hashes]
bash selftest.sh            # builds, asserts invariants, runs the r2 tool armed+disarmed
```
