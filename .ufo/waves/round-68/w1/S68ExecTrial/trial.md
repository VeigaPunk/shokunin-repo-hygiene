# S68ExecTrial — writer trial on real lane revisions

Frozen writer: `tools/souji-receipt-write.py` blob `f70da577eb1e1624cc63ab8fd0468565927d9b6a`, sha256 `b811ee2a7a67d8d3ea6d00fb3a44780ccb807113b9eeaf28f09e01448715a725`. No writer byte changed. Preregistration: `census/round-68/preregistration.txt`.

## Flags read from `--help` (all three revisions identical)

`python3 -B tools/souji-receipt-write.py --help` → `--root ROOT`, `--allow-outside`, `--rev REV`, `--instrument INSTRUMENT`, `--out OUT`, `--command COMMAND`, `--max-bytes MAX_BYTES`, `--allow-dirty`, `--selftest`, `--work WORK`, `--report REPORT`, `args...` (after `--`). Task flags confirmed; no adaptation needed. `souji-receipt-write.py` has **no verify subcommand** (`main()` at tools/souji-receipt-write.py:1556 only parses the flat flags above plus `--selftest`). `tools/souji-receipt-run.py verify` verifies the *different* receipt-v1 format (`receipt=v1`, `tool=`, `tool_sha256=`, fences `--- stdout ---`/`--- stderr ---`, tools/souji-receipt-run.py:312-369) and therefore refuses writer receipts with `RECEIPT-MALFORMED header order or fences do not match receipt v1` (rc 2). Manual verification used instead: `instrument_sha256=` header == `git show <rev>:tools/souji-receipt-write.py | sha256sum`.

## Exact commands run

All under scratch `$HYAKU_SCRATCH/souji-r68/S68ExecTrial` (=`/fast/scratch/hyaku/souji-r68/S68ExecTrial`), `TMPDIR=$SCRATCH`, lane `LANE=/home/vgpnk/Projects/shokunin/souji-shokunin`:

```bash
git clone --shared -q $LANE $SCRATCH/clone-<label>
git -C $SCRATCH/clone-<label> checkout --detach <rev> -q
git -C $SCRATCH/clone-<label> rev-parse --show-toplevel   # asserted == clone path

# clean
python3 -B $clone/tools/souji-receipt-write.py --root $clone --rev <rev> --instrument tools/souji-receipt-write.py --out $SCRATCH/receipt-<label>-clean.txt --allow-outside -- /bin/echo hi

# verify attempt (documented path for runner receipts)
python3 -B $LANE/tools/souji-receipt-run.py verify --root $LANE $SCRATCH/receipt-<label>-clean.txt

# manual verify
grep '^instrument_sha256=' $SCRATCH/receipt-<label>-clean.txt ; git show <rev>:tools/souji-receipt-write.py | sha256sum

# dirty (printf 'x' >> $clone/SCORECARD.md)
python3 -B $clone/tools/souji-receipt-write.py --root $clone --rev <rev> --instrument tools/souji-receipt-write.py --out $SCRATCH/receipt-<label>-dirty.txt --allow-outside -- /bin/echo hi
python3 -B $clone/tools/souji-receipt-write.py --root $clone --rev <rev> --instrument tools/souji-receipt-write.py --out $SCRATCH/receipt-<label>-dirty-allow.txt --allow-outside --allow-dirty -- /bin/echo hi
```

Revisions: `head = git -C $LANE rev-parse master = 8b393b1911558932eab29e74635361256afdd6e3`, `r67 = f70da577eb1e1624cc63ab8fd0468565927d9b6a`, `r66 = c13fbb4e1b563a78278ddc14316c20252e9a6d8d`.

## Results (9 rows)

| Revision | Run | rc | Receipt | Receipt head | Verify (runner) | Verdict |
|---|---|---|---|---|---|---|
| 8b393b19… (HEAD/freeze) | clean | 0 | `receipt-head-clean.txt` (exists) | `instrument=tools/souji-receipt-write.py / instrument_sha256=b811ee2a…48715a725 / rev=8b393b19… / command=/bin/echo hi / hi / EXIT=0` | rc 2 `RECEIPT-MALFORMED header order or fences do not match receipt v1` | PASS clean; runner verify N/A (different format). Manual sha match YES |
| 8b393b19… | dirty | 2 | `receipt-head-dirty.txt` (absent) | — | — | PASS refused: `refused: lane worktree is dirty (git status --porcelain non-empty); pass --allow-dirty to override` |
| 8b393b19… | dirty + `--allow-dirty` | 0 | `receipt-head-dirty-allow.txt` (exists) | same head, EXIT=0 | — | PASS admitted; instrument sha still `b811ee2a…` |
| f70da577… (r67) | clean | 0 | `receipt-r67-clean.txt` (exists) | `instrument_sha256=b811ee2a… / rev=f70da577… / EXIT=0` | rc 2 `RECEIPT-MALFORMED …` | PASS; manual sha match YES |
| f70da577… | dirty | 2 | `receipt-r67-dirty.txt` (absent) | — | — | PASS refused, same dirty message |
| f70da577… | dirty + `--allow-dirty` | 0 | `receipt-r67-dirty-allow.txt` (exists) | `instrument_sha256=b811ee2a… / EXIT=0` | — | PASS admitted |
| c13fbb4e… (r66) | clean | 0 | `receipt-r66-clean.txt` (exists) | `instrument_sha256=a8c47d36…1097fc / rev=c13fbb4e… / EXIT=0` | rc 2 `RECEIPT-MALFORMED …` | PASS; manual sha match YES (pre-r67 writer) |
| c13fbb4e… | dirty | 2 | `receipt-r66-dirty.txt` (absent) | — | — | PASS refused, same dirty message |
| c13fbb4e… | dirty + `--allow-dirty` | 0 | `receipt-r66-dirty-allow.txt` (exists) | `instrument_sha256=a8c47d36…1097fc / EXIT=0` | — | PASS admitted |

Dirty file in all three: `SCORECARD.md` (`git status --porcelain` = ` M SCORECARD.md`).

### Evidence

- `trial-driver.log`: 9 blocks with exact rc/receipt/verify lines (see scratch, removed after capture).
- All receipts: `instrument=tools/souji-receipt-write.py`, `command=/bin/echo hi`, body `hi`, `EXIT=0`.
- Runner `verify` rc 2 on every clean receipt is *expected format mismatch*, not corruption: writer format is `instrument=/instrument_sha256=/rev=/command=/body/EXIT=` (tools/souji-receipt-write.py:521-525), runner format is `receipt=v1/rev=/tool=/tool_sha256=/cmd=/rc=/utc=/--- stdout ---/--- stderr ---` (tools/souji-receipt-run.py:312-331).

## Findings

- HIGH [none] — no lane files modified; `git -C $LANE status --porcelain -- .ufo/` shows only seat-dir writes.
- MEDIUM: writer receipts have no documented verifier in the lane (writer has no `verify` subcommand; runner `verify` rejects the format). Callers must verify manually (`instrument_sha256` vs `git show`) or via the c1-counter's own checks. This is the correct fallback per task ("if a flag differs, adapt and say so"; "with the writer's verify subcommand if one exists … or with … receipt-run.py verify if that is the documented path" — neither exists for this format).
- LOW: r66 writer `instrument_sha256=a8c47d36…` (pre-r67 base) confirms base slot bytes differ from candidate; both behave identically on clean/dirty/allow-dirty in this trial.

## Verdict

PASS all 9 cells (3 clean accepted, 3 dirty refused rc 2 no receipt, 3 dirty+allow-dirty accepted). Manual sha256 verification 3/3 YES. No counterexample. Lane untouched.
