# R92ExecC1Search — C1 re-derivation (souji round 92, wave w1)

Seat scope: re-derive C1's after arm and control end-to-end on committed bytes in
`/home/vgpnk/Projects/shokunin/souji-shokunin`, read-only lane, instruments unmodified.
Contract: `census/round-92/preregistration.txt` (commit F, sole file). Assignment:
after search + control search + pristine harness + every pin + `cmp -n` r91 prefix +
r92-vs-r91 harness diff classified hunk-by-hunk + target-membership check in the
pre-freeze r91 census. Scratch `/fast/scratch/hyaku/souji-r92/R92ExecC1Search/` created
with `mkdir -p`, deleted with `rm -rf` after receipts were copied to the seat dir
(verified absent afterward; other seats' dirs untouched). Peak scratch ~3.2 GB total,
≤2 harness work trees held at once (searched with `--jobs 4` as assigned). No tool
installs (RULES.md read; seat spec also says none needed). No git/jj mutation anywhere;
read-only lane access. Receipts in this seat dir (`search-after-r92.txt`,
`search-control-r91.txt`, `pristine-harness-r92.txt`, `pins-sha256.txt`,
`harness-diff.txt`, `receipt-hashes.txt`, all below).

## 1. After search (47 targets, r92 population) — MATCHES prereg predicate exactly

Command (cwd = lane root, `--work` an empty dir under scratch, `--jobs 4`):
`python3 -B census/round-92/c1-survivor-search.py --counter census/round-87/c1-pointer-counter.py
--harness census/round-92/c1-false-row-harness.py --population census/round-92/c1-false-rows.tsv
--lane . --fleet-root /home/vgpnk/Projects/shokunin --work <empty> --jobs 4 --ids census/round-92/c1-targets.json`

Self-reported header (receipt `search-after-r92.txt`):
counter `fd0a8e24...`, harness `818f84d9...`, population `f66341fc...`,
search `c393d941...`, ids `5a8f6087...` n=47.

```
SEARCH-SUMMARY generated=47 ambiguous=0 uncompiled=0 hung=0 scored=47 killed=47 survived=0
AFTER-EXIT=0
```

All 47 `SEARCH` lines are `killed=yes rc=1`; the id set in the receipt equals the
`c1-targets.json` id set (programmatic check). Receipt sha256 `29d90ea5...`.

## 2. Control search (same 47 targets, r91 population) — MATCHES prereg control exactly

Same command with `--population census/round-91/c1-false-rows.tsv`:

```
SEARCH-SUMMARY generated=47 ambiguous=0 uncompiled=0 hung=0 scored=47 killed=0 survived=47
CONTROL-EXIT=0
```

All 47 lines `killed=no rc=0`. Stronger: the 47 `SEARCH` lines are byte-identical to
the committed P2 control receipt `census/round-92/controls/c1-control-r91-population.txt`
(`diff` clean). Receipt sha256 `b8448350...`.

## 3. Pristine harness on the r92 population — MATCHES prereg exactly

`python3 -B census/round-92/c1-false-row-harness.py --counter census/round-87/c1-pointer-counter.py
--lane . --fleet-root /home/vgpnk/Projects/shokunin --work <empty> --population census/round-92/c1-false-rows.tsv`

Exit 0 (17.6 s). Quoted lines from `pristine-harness-r92.txt`:
- `ROW LD4 where=ledger-resolve rev=BASE item=P04 class=- expect=MOVED/- got=MOVED rc=0 match=yes`
- `ROW LD4r where=ledger-resolve rev=BASE item=P04 class=- expect=MOVED/0 got=MOVED rc=0 match=yes`
- `SUMMARY rows=64 mismatches=0 accepted=0 refused_true=0 errors=0`

64 data rows (67 physical lines: 2 header comments + 1 r92 comment line + 64 rows;
r91 file: 65 lines with 63 rows). Receipt sha256 `4acaaa1e...`.

## 4. Pin table (sha256sum, committed bytes)

| artifact | measured | prereg | status |
|---|---|---|---|
| `census/round-87/c1-pointer-counter.py` | `fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b` | fd0a8e24… | MATCH |
| `census/round-92/c1-false-rows.tsv` (64 rows) | `f66341fc2867f6b5dbd8515a717747370c700fd31bf7aaa497a292ca65027c51` | f66341fc… | MATCH |
| `census/round-91/c1-false-rows.tsv` (63 rows) | `fdc3d23839527fc1b67ef78945d0e537811ba28a8a2156fb9c598946a02bc460` | (harness pin map, line: `"fdc3d238…": 63`) | MATCH |
| `census/round-92/c1-targets.json` (47, unique ids) | `5a8f608787aa47700dd3b76e99a9f9618a335a8cc4af448cab119993dee13e05` | 5a8f6087… | MATCH |
| `census/round-92/c1-false-row-harness.py` | `818f84d96a88288dde7712b71a9bd3e1276e17abe3fbf07ce6cc97c77c4ff967` | (reproduced in header of pristine receipt and in P2 control receipt) | MATCH |
| `census/round-92/c1-survivor-search.py` | `c393d941eb2eb13de8acba81665b0378347ae4f77b620cc2da890854ec4c9cc4` | (reproduced in header of both P2 control and r91-full census receipts) | MATCH |

`cmp -n 16134 census/round-91/c1-false-rows.tsv census/round-92/c1-false-rows.tsv`:
prefix byte-identical, no difference — r92 at line 66 appends exactly one comment
line + LD4r (`ledger-resolve BASE r77 P04 - - MOVED 0`). Note `cmp` ran against the
full r91 file length (16134 bytes); the prereg words this as "r91 63 byte-for-byte
plus one comment line and LD4r", which is exactly what holds (r91 file ends without a
trailing banner after LD4).

## 5. Harness diff hunk inventory (r91 `5c6a1cf9…` → r92 `818f84d9…`)

Full diff: `harness-diff.txt` (2 hunks). Classified:
1. Hunk 1 (module docstring, lines 1–13): new r92 banner — **docstring** class
   (states the added pin, LD4r's purpose, and the NF1r/forge limitation). No code.
2. Hunk 2 (population-pin dict, ~line 141): adds `"f66341fc…": 64` next to the
   existing `"fdc3d238…": 63` — **pin** class. No code.

Zero UNEXPECTED hunks: no new row type, no code-path change; `expect_rc` handling
(e.g. the MISMATCH-write at harness line ~492) is byte-unchanged from r91, consistent
with stated limit (ii).

## 6. Target membership in the pre-freeze census — all 47 were r91 survivors

`census/round-92/records/c1-search-r91-full.txt`: `SEARCH-SUMMARY generated=270
ambiguous=9 uncompiled=0 hung=1 scored=260 killed=136 survived=124` (matches prereg).
Every one of the 47 target ids appears as `killed=no` in that file (47/47 survivors,
0 killed, 0 missing; census `killed=no` total = 124, `killed=yes` = 136).
Cross-check: set of 47 targets equals the committed feasibility killed-set
(`c1-feasibility-r92-prefreeze.txt`: `generated=124 killed=47 survived=77`) exactly
(the L1's "chosen as" criterion, stated limit vi), and the 47 are a subset of the
124 survivor ids in `c1-survivors-r91.json`; the residual file holds 77 entries
(124 − 47), matching stated limit (i). So the claim's "survivor" wording is TRUE:
no target was already killed by the r91 63-row population.

## 7. FALSIFIES-WORDING / FALSIFIES-NUMBER

NO-FALSIFICATION. Tried, on committed bytes: the full after search (47/47 killed, exit 0),
the full control search (47/47 survived, exit 0, lines identical to P2 receipt), the
pristine harness (SUMMARY + LD4r `rc=0 match=yes`, exit 0), all six pin hashes, the r91-prefix
`cmp`, the complete 2-hunk harness diff classification (docstring + pin only), and the
registration-file membership / feasibility-set / residual-count cross-checks. Nothing
falsifies any sentence or number of either C1 claim; zero mismatches to the prereg
(no HIGH).
