# SwarmCritic06 — r32 a2w1 audit of landed C1 rows N35-N43 + L29

## Status

STATUS: PASS — all ten rows were opened, re-run and judged against their run: 7 MATCH rows are the cell's own r31/r21 measurement, 0 rows fabricate a value, 3 withdrawals have true reasons under the frozen rules; two of those three withdrawals are grammar-blocked, not evidence-absent (A1), and the counter drops decoy rows at a wrong base line without error (A2, reproduced).

## Evidence

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`; audit revisions: base `85b61a151923986e7e6b48f7084b9122561b5f3d`, C1 landing `9e8982b7a6ac57dffa415f9db43cf7cd6e829c93`, tip `4e56c48b8fc828f9aba2746e324dc46aa538bdbf`. Scratch clone `/fast/scratch/hyaku/souji-r32/AuditC1N35N43/r.vdZ1ov/c` (`git rev-parse --show-toplevel` printed it, origin removed, detached at `9e8982b7`); family experiment clone committed only inside `/fast/scratch/hyaku/souji-r32/AuditC1N35N43/`. Python 3.14.8, git 2.56.0; no installs.

**Counter (frozen v2), `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-32/c1-counter-v2.py`, run at the landing commit:**

```
$ python3 -B .../census/round-32/c1-counter-v2.py --root <lane> --rev 9e8982b7a6ac57dffa415f9db43cf7cd6e829c93 \
    --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c \
    --only N35,N36,N37,N38,N39,N40,N41,N42,N43,L29 --scratch <scratch>/cnt
ITEM	N35	SCORECARD.md:423	literal=cases=10	binding=record	MATCH	census/round-31/records/c2-after-v1.txt:22
ITEM	N36	SCORECARD.md:423	literal=pass=10	binding=record	MATCH	census/round-31/records/c2-after-v2.txt:22
ITEM	N37	SCORECARD.md:423	literal=cases=10	binding=record	MATCH	census/round-31/records/c2-after-v3.txt:22
ITEM	N38	SCORECARD.md:423	literal=pass=3	binding=withdrawn	WITHDRAWN	the base-gate arm's 3 is recorded only in census/round-31/records/c2-fixture-red-before.txt, which this base line does not cite, and that arm exits 1
ITEM	N39	SCORECARD.md:423	literal=fp=0	binding=record	MATCH	census/round-31/records/c2-after-v1.txt:28
ITEM	N40	SCORECARD.md:423	literal=real=2	binding=record	MATCH	census/round-31/records/c2-after-v2.txt:29
ITEM	N41	SCORECARD.md:423	literal=cne=0	binding=record	MATCH	census/round-31/records/c2-after-v3.txt:30
ITEM	N42	SCORECARD.md:423	literal=495	binding=withdrawn	WITHDRAWN	the item's only unit r26 contains a digit, ...
ITEM	N43	SCORECARD.md:424	literal=17 RESULT	binding=withdrawn	WITHDRAWN	the 17 is a count of RESULT lines ...
ITEM	L29	SCORECARD.md:170	literal=18/18 remote-source-after.json	binding=field	MATCH	census/round-21/remote-source-after.json expected_command_count=18 matched_command_count=18
SUMMARY items=10 bound_run=0 bound_record=6 bound_field=1 withdrawn=3 unbound=0 mismatches=0 partial=1 rev=9e8982b7a6ac57dffa415f9db43cf7cd6e829c93
EXIT=0
```

The frozen v1 counter (`census/round-32/c1-counter.py`, same argv) printed the same ten verdicts and the same SUMMARY. The same v2 run at the lane tip `4e56c48b` printed the same ten lines (`SUMMARY ... rev=4e56c48b8fc828f9aba2746e324dc46aa538bdbf`); `SCORECARD.md` blob `ceef747c200d15b4c40d5f07498842301e3c1c7c` is identical at `9e8982b7` and tip.

**Append-only and block shape:**

```
base bytes=81245 ; cmp -n 81245 base.md rev.md -> PREFIX-IDENTICAL
grep -bo "### Round 32 capability-count bindings" rev.md -> 81246
rows=38, duplicate ids=0, shared record occurrences=0, shared field keys=0
withdrawn rows in block=17 ; items=44 ; items with no row: N28 N29 N30 N31 N33 N34
```

The ten landed rows are byte-identical to the block in `.ufo/waves/round-32/w1/deliver-c1-bind-N35-N43-L29.md` (row-by-row `IDENTICAL` x10), i.e. the L1 appended verbatim.

**Blob identity at base / landing / tip (all SAME):** `c2-after-v1.txt` `2cd9461cd37f`, `c2-after-v2.txt` `668b6ba09789`, `c2-after-v3.txt` `f5d13dd47208`, `c2-fixture-red-before.txt` `d123b9baf137`, `census/round-21/remote-source-after.json` `f4123cf12614`, `jj-object-clock-run.txt` `63502d12a74b`. No C1 row in this batch reads a file any r32 seat may edit.

**Arm provenance.** `tools/souji-landing-gate.py` = `7bfcb9b5a42f` and `tests/fixtures/r31-landing-gate-precision.py` = `943f42d38826` at `8024b540` (the records' --rev), at `f9502678` (the commit that wrote `SCORECARD.md:423`), and at the r32 base — so the r31 C2 counter's `FIXTURE`/`REDARM` legs (`census/round-31/c2-counter.py:136` and `:142`: `run([sys.executable, "-B", fx, "--tool", tool_r], ...)`; prints at `:145-146`) measured exactly the bytes the cell names.

## Row verdicts

| item | occurrence it enumerates (`c1-items.tsv` context) | bound row | verdict |
|---|---|---|---|
| N35 | first `cases=10`, current-tool arm (`-gate.py` -> `cases=10 pass=10`) | `c2-after-v1.txt:22` = `FIXTURE rc=0 line='cases=10 pass=10 control=FALSE-GREEN-REJECTED'` | **HONEST** — same commit, same fixture argv, same case total |
| N36 | `pass=10`, current-tool arm | `c2-after-v2.txt:22`, same line | **HONEST** — same output, second field |
| N37 | second `cases=10`, **base-tool** arm (` tool prints 'cases=10 pass=3'`) | `c2-after-v3.txt:22`, current-tool line | **HONEST (occurrence-substituted)** — see Finding 3 |
| N38 | `pass=3`, base-tool arm | withdrawn | **OTHER** — reason true under the rules (Finding 4); no cited line passes A0(b) |
| N39 | `fp=0` in the quoted `fp=0 real=2 cne=0 r26=495` | `c2-after-v1.txt:28` — the very quoted line | **HONEST** |
| N40 | `real=2` in the same quoted string | `c2-after-v2.txt:29` (`rev=8024b540…`, identical fields + `shift=ok`) | **HONEST** — same measurement re-run at the same rev |
| N41 | `cne=0` in the same quoted string | `c2-after-v3.txt:30` (first run, `rev=8024b540…`) | **HONEST** — and correctly not `v3:65`, the divergent run (`fp=13 r26=466 … rev=1d45496a…`) |
| N42 | `r26=495` | withdrawn | **OTHER** — reason true, but the observable is committed and cited (Finding 5, A1) |
| N43 | `17 RESULT` | withdrawn | **OTHER** — reason true, but `results=17` sits on a cited line (Finding 6, A1) |
| L29 | `remote-source-after.json18/18` | field `census/round-21/remote-source-after.json` `expected_command_count=18 matched_command_count=18` | **HONEST** — same commit wrote cell and record (Finding 7) |

No row is WRONG-WITHDRAWAL, and every MATCH row's literal is a true value of the quantity its item names. Every bound record is from the row's own round — r31 for `SCORECARD.md:423`/`:424`, r21 for `:170` — and the items' round sets `{26,31}` and `{20,21}` accept those `census/round-K/` paths.

## Findings

1. **Rows landed verbatim, block append-only.** `SCORECARD.md@9e8982b7` = base bytes (81245) + block (10188 bytes, starting `\n### Round 32 capability-count bindings`), rows identical to the wave-1 delivery. Location: `SCORECARD.md:430` at `9e8982b7`; `.ufo/waves/round-32/w1/deliver-c1-bind-N35-N43-L29.md`.
2. **N35/N36 are the cell's own reading.** `census/round-31/c2-counter.py:136` runs the same fixture against `tool@REV`, and the tool/fixture blobs are identical at `8024b540`, `f9502678` and base (Evidence). Record line `census/round-31/records/c2-after-v1.txt:22` reproduces the cell's `cases=10 pass=10 control=FALSE-GREEN-REJECTED`.
3. **N37 is value-true but stands for the other arm.** The item maps to the base-tool sentence (`c1-items.tsv` N37 context: tool prints cases=10 pass=3), whose own record is `census/round-31/records/c2-fixture-red-before.txt:30` = `    cases=10 pass=3 control=FALSE-GREEN-REJECTED` (uncited on `SCORECARD.md:423`, so A0(a) refuses it). The bound line is the *current*-tool run. The number is arm-independent — the cited `REDARM` line `c2-after-v1.txt:23` lists all ten case labels `('G1' … 'G10')` for the base arm with 3 `PASS` — so the row is honest in value, but it evidences the case total, not the base-arm execution the sentence quotes. The row discloses this (`the case total is arm-independent`).
4. **N38's withdrawal is true; its "only" is one word too strong.** No line of the three cited records passes `adjacent()` for `(pass, 3)` (`census/round-31/records/c2-after-v1.txt` / `-v2` / `-v3`: no admissible line), and the arm does exit 1 (`c2-after-v1.txt:23`: `REDARM rc=1 base_cases=[…] ok`). But the 3-PASS reading *is* corroborated on a cited line as ten per-case verdicts (`c2-after-v1.txt:23`), so "recorded only in `c2-fixture-red-before.txt`" is accurate for the printed count, not for the reading. Location: `SCORECARD.md:423` row N38.
5. **N42 is a grammar-blocked withdrawal, not an absent observable.** `census/round-31/records/c2-after-v1.txt:28` prints `fp=0 real=2 cne=0 r26=495 …` and A0(b) adjacency holds (`r26=495`), but the item's only unit `r26` carries the digit run `26`, so any unit-bearing literal holds two integers. Reproduced: literal `r26=495` → `BAD-ROW(literal)`; literal `495` → `BAD-ROW(literal)` (diagnostic commits `0b67f4af…`, `fe0ef238…`). The frozen rule text calls `withdrawn` "no observable shows it" (`census/round-32/c1-counter-v2.py:47`); here one does.
6. **N43 is the same class.** `census/round-31/records/c3-after-c3-counter-v3.txt:9` = `L8 PASS run_record=present results=17` (cited on `SCORECARD.md:424`, unchanged base→tip). Reproduced: literal `17 RESULT` → `RECORD-MISMATCH`; literal `17 results` → `RECORD-MISMATCH` (the plural `s` defeats `adjacent()`, `c1-counter-v2.py:161-166`); `census/round-31/records/amendments.txt:53` (`4 of 17 RESULT lines`) → `BAD-ROW(A0a-not-cited)`. Diagnostic commits `5e112462…`, `503d4ec8…`, `a42d595b…`.
7. **L29 is the strongest row in the batch.** `git blame` at base puts `SCORECARD.md:170` in `4eb2fda`, the same commit that added `census/round-21/remote-source-after.json` (blob `f4123cf1`, unchanged base/REV/tip). The JSON holds `"expected_command_count": 18,` (line 4566), `"matched_command_count": 18,` (line 4724), `"all_matched": true`, 18 `commands` entries, none with `failure_lines` — exactly the `remote-source-after.json18/18` the cell states.
8. **Block aggregates (context).** 38 rows for 44 items; `withdrawn` rows = 17 (`grep -cE "^\| (N|L)[0-9]{2} \|.*\| withdrawn: " appended block` → 17); unbound items = N28 N29 N30 N31 N33 N34. Frozen targets `unbound=0 mismatches=0 withdrawn<=8` therefore cannot hold at `9e8982b7` or at tip — consistent with `census/round-32/records/amendments.txt` ("MISSED"); my ten items contribute 3 of the 17 withdrawals.

## Attack log

**A1 — the withdrawn budget is being spent on counter grammar, not on missing evidence (reproduced).** Items N42 and N43 withdraw integers whose observables are committed and cited; only the literal/adjacency grammar refuses them (Finding 5, 6). With `withdrawn<=8` frozen and 17 used, two of the eight are consumed by a *rule-shape* defect; the residue is `MISSED` either way. Smallest safe correction: do not re-classify landed rows (post-data), but (a) the round's lesson/QUALITY text must not claim "each of the 44 integers carries its own evidence", and (b) carry the two defects as named r33 input with these reproductions — unit token containing digits (`r26`) and plural unit word (`results`) defeating `adjacent()`.

**A2 — decoy rows at a wrong base line are invisible to the counter (reproduced).** `c1-counter-v2.py:224` filters an item's rows to those whose `SCORECARD.md:<line>` equals the item's line *before* the duplicate check, so extra rows for the same id at any other line are dropped silently. Reproduced on top of the landed block: appended `| N35 | SCORECARD.md:9999 | cases=10 | record: census/round-31/records/c2-after-v1.txt:22 | …` and `| N38 | SCORECARD.md:9999 | pass=3 | record: census/round-31/records/c2-fixture-red-before.txt:30 | …` (diagnostic commit `bc5b104b…`); the counter still prints `N35 MATCH`, `N38 WITHDRAWN`, `mismatches=0`. Impact: a contradictory or decoy row can be parked in the appended block without any verdict change. Smallest safe correction (stricter-only): count rows per item id before line filtering and return `BAD-ROW(duplicate)` when any extra row exists, whatever its line. No such decoy row exists in the landed block today (`duplicate ids=0`, 38 rows).

**A3 — one measurement, three items (no action required, but do not over-read).** `c2-after-v1/-v2/-v3.txt:22` are three separate r31 counter runs at `rev=8024b540`, printing one identical `FIXTURE` line; they satisfy N35, N36 and N37. This is not fabrication (three executions, three blobs, no shared occurrence), but "bound" here means one measurement recorded three times, not three independent confirmations — the same file-granularity the r32 planned text names for the record rule.

## Deliveries

- `.ufo/waves/round-32/a2w1/SwarmCritic06.md` (this report).

Scratch `/fast/scratch/hyaku/souji-r32/AuditC1N35N43/` removed after writing this file; no lane file was modified, and no `git add/commit/checkout/reset` touched the lane or its jj state.
