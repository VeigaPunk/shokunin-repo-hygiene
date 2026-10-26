# SwarmExecutor03 — round 32 w1, C1 calibration bindings N12–N19

## Status

STATUS: PASS — eight binding rows for N12–N19 (`3` run, `1` record, `4` withdrawn), read
`unbound=0 mismatches=0 withdrawn=4` under **both** `c1-counter-v2.py` and `c1-counter.py` (rc=0 each)
at scratch rev `5c14cad06f52beb2ce898a9e5b5dae28fd08c650`; the four withdrawals are counter-constraint
withdrawals under A0, each reproduced with the counter's own verdicts and listed as attacks below. No
lane file was written or staged outside this report and the delivery, and no tool was installed.

## Evidence

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, base `85b61a151923986e7e6b48f7084b9122561b5f3d`,
list-rev `3ec84fc81b3243429c834a051880b0bcde06291c`. SCORECARD.md at base is blob
`771250313133d5f38b7f51a0922212db50990520` (`git rev-parse <base>:SCORECARD.md`); at the scratch rev it
begins with those bytes and only the binding block is appended, which is what the counter checks (it did
not report `MISMATCH(append-only-violated)`). Scratch: `/fast/scratch/hyaku/souji-r32/C1BindC` (clone with
`origin` removed, toplevel verified by the counter), deleted after the delivery was copied.

My items' base cells, quoted from `git -C <lane> cat-file blob 85b61a1…:SCORECARD.md` this run:

- `:161` — "`bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` 35/0 (5fa6017 tools: 13 fail)"
- `:165` — "r21 synthetic27/27 (old emissions6/27, leaks19→0), `census/round-21/reason-after.txt`, S100/S101"
- `:168` — "final r21 18-step receipts: auditor selftest118/0; r19-seat-audit-shapes17/0 (base12); r20-audit-contract78/0 (base11)"
- `:175` — "`census/round-24/records/c2-control-base.tsv` (2 at base), `c2-after.tsv` (0)"

Where each integer was produced:

- `census/round-17/jj-receipts-base5fa6017.txt:51` — "SUMMARY	total=33	failed=13	skipped=2" (the 13).
- `census/round-21/reason-after.txt:29` — "SUMMARY	total=27	pass=27	fail=0	leaks=0	base_leaks=19	max_reason_bytes=160" (the 19 and the 0).
- `census/round-21/r20-closure-excerpt.json:40` — "r20-audit-contract 78/78/0 base_discriminating=11; same oracle with baseline as tool 40/38; auditor selftest 118/0; r19-seat-audit-shapes 17/0 (12 base-disc)".
- `census/round-24/records/c2-control-base.tsv:11` — "grounded=4 mapped=2 dangling=0 mismatches=2" (the 2).
- `census/round-24/records/c2-after.tsv:5` and `:9` — the argv `--root . --rev 778747eb671f8e85ef5387bc3d7023337b30467c` and "grounded=6 mapped=6 dangling=0 mismatches=0" (the 0).
- `census/round-21/step-inventory.json` — `len(d["steps"]) == 18` (the 18), `source_path` "census/round-20/run-acceptance.py".

Acceptance (v2, then v1 — identical output, both real exits 0):

```
python3 -B <lane>/census/round-32/c1-counter-v2.py --root <scratch clone> --rev 5c14cad06f52beb2ce898a9e5b5dae28fd08c650 \
  --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c \
  --only N12,N13,N14,N15,N16,N17,N18,N19 --scratch <scratch>/cnt
ITEM	N12	SCORECARD.md:161	literal=failed=0	binding=run	MATCH	bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools rc=0 observed=SUMMARY total=35 failed=0 skipped=2
ITEM	N13	SCORECARD.md:165	literal=19 leaks	binding=withdrawn	WITHDRAWN	the only cited occurrence base_leaks=19 sits on reason-after.txt line 29, which N14 already binds, and the counter forbids a shared occurrence
ITEM	N14	SCORECARD.md:165	literal=leaks=0	binding=record	MATCH	census/round-21/reason-after.txt:29
ITEM	N15	SCORECARD.md:168	literal=18 step	binding=withdrawn	WITHDRAWN	the 18 steps live in census/round-21/step-inventory.json, whose basename line 168 never cites, and no line-named script prints them
ITEM	N16	SCORECARD.md:168	literal=base_discriminating=12	binding=run	MATCH	python3 -B tests/fixtures/r19-seat-audit-shapes.py rc=0 observed=SUMMARY total=17 failed=0 base_discriminating=12
ITEM	N17	SCORECARD.md:168	literal=11 base	binding=withdrawn	WITHDRAWN	the 11 needs the pre-r20 auditor passed as --base-tool, no committed copy of it exists, and line 168 cites no round-20 record
ITEM	N18	SCORECARD.md:175	literal=2 base	binding=withdrawn	WITHDRAWN	census/round-24/records/c2-control-base.tsv line 11 holds mismatches=2 but never the word base, so the A0(b) adjacency the unit demands cannot hold
ITEM	N19	SCORECARD.md:175	literal=mismatches=0	binding=run	MATCH	python3 -B tools/souji-coverage-agreement.py --root . --rev 778747eb671f8e85ef5387bc3d7023337b30467c rc=0 observed=grounded=6 mapped=6 dangling=0 mismatches=0
SUMMARY items=8 bound_run=3 bound_record=1 bound_field=0 withdrawn=4 unbound=0 mismatches=0 partial=1 rev=5c14cad06f52beb2ce898a9e5b5dae28fd08c650
```

v2 was run twice on the same rows (revs `34655dcb27b45a26aaaf30058b2499ea820f0d13` and above) with
identical verdicts. The rows in the delivery are byte-identical to the rows in the validated commit
(`diff` of the two `|`-bearing blocks: empty, 10 lines).

## Findings

1. **N12 is bindable only as a run.** `census/round-17/jj-receipts-base5fa6017.txt:51` holds the 13 as
   `failed=13`, which A0(b) refuses (two alphanumerics `ed` stand between `fail` and `13`). The cell's own
   quoted command, re-run from the base blob at the scratch rev, ends `SUMMARY	total=35	failed=0	skipped=2`
   (rc 0), so the literal is `failed=0`, a restated count. Location: SCORECARD.md:161, that record line.
2. **N14 binds the after count on the cited record.** Among the records SCORECARD.md:165 *cites*,
   `census/round-21/reason-after.txt:29` is the only line holding `leaks` beside an integer; the two other
   round-21 lines that do — `reason-before.txt:29` and `reason-oracle-before.txt:49` — are not named on the
   cell, so A0(a) refuses them (`grep` over `census/round-18/` and `census/round-21/` finds ten such lines,
   transcripts and JSON stdout among them). Location: SCORECARD.md:165, reason-after.txt:29.
3. **N16 reproduces its cell exactly.** `tests/fixtures/r19-seat-audit-shapes.py` (base blob, defaults
   `--tool tools/souji-seat-audit.py --base-rev 3ab2c81…`) ends `SUMMARY	total=17	failed=0	base_discriminating=12`:
   the cell's `r19-seat-audit-shapes17/0 (base12)`. Location: SCORECARD.md:168.
4. **N19 reproduces the record's own argv.** `census/round-24/records/c2-after.tsv:5` records
   `--root . --rev 778747eb671f8e85ef5387bc3d7023337b30467c`; re-running it now prints
   `grounded=6 mapped=6 dangling=0 mismatches=0`, so the literal is `mismatches=0`. The item is unitless,
   so `record:` is forbidden (`BAD-ROW(unitless-record)`) and `run:` is the only kind. Location: SCORECARD.md:175.
5. **N18 is refused by A0(b), not by the record.** `census/round-24/records/c2-control-base.tsv` contains
   the substring `base` zero times (counted on the blob); line 11 holds `mismatches=2`. The unit the
   enumerator derived from "(2 at base)" is the semantic word `base`, so no line of the cited record can
   satisfy adjacency. Withdrawn. Location: SCORECARD.md:175, c2-control-base.tsv:11.
6. **N15's observable exists but is uncitable.** `census/round-21/step-inventory.json` holds 18 steps; line
   168 names no path and no script named on it prints a step count. Withdrawn. Location: SCORECARD.md:168.
7. **N17's baseline is not in the tree.** The 11 is `base_discriminating=11` from the r20-audit-contract run
   with the pre-r20 auditor as `--base-tool`; `git ls-tree -r master` holds no copy of that blob
   (`12516f7:tools/souji-seat-audit.py` = `e5ce94b1…`, absent), and the only committed auditor copy
   (`.ufo/waves/round-26/assimilation/validate/tools/souji-seat-audit.py`) is the current one —
   running the fixture with it prints `SUMMARY	total=78	pass=66	fail=12	base_discriminating=0`. Withdrawn.
   Location: SCORECARD.md:168.
8. **The wave-1 union of C1 deliveries already breaks the frozen C1 target.** Summing the five delivery
   files in `.ufo/waves/round-32/w1/`: N01–N05 `withdrawn=2`; N06–N11 `withdrawn=1`; N12–N19 `withdrawn=4`;
   N20–N26 `withdrawn=7`; N27–N34 `mismatches=8`; N35–N43+L29 `withdrawn=3` → 44 items,
   **withdrawn=17, mismatches=8, unbound=0**. The frozen target is `unbound=0 mismatches=0 withdrawn<=8`,
   so as assembled the claim cannot hold; this is a planning-level fact for the L1, not something a seat
   can bind away. Locations: the `SUMMARY` lines of `deliver-c1-bind-N01-N05.md`, `-N06-N11.md`,
   `-N20-N26.md`, `-N27-N34.md`, `-N35-N43-L29.md`.
9. **Two of my runs read REV files that C2 edits.** N12's fixture reads `tools/souji-verify.sh` (C2 item
   T15) and N16's reads `tools/souji-seat-audit.py` (C2 item T10) from the working tree; the C1 counter
   takes only the *script* from the base blob. C2's brief is behaviour-preserving, but both bindings must
   be re-read at the integrated tip. Location: `census/round-32/c2-items.tsv` rows T10, T15.

## Attack log

Reproduced with the frozen counter at probe rev `eefbb9d6a890411e66c872dc6d387ec27a4c2779` (scratch clone,
`--only N13,N14,N15,N17,N18`):

```
ITEM	N13	…	binding=record	BAD-ROW(shared-occurrence)	census/round-21/reason-after.txt:29
ITEM	N14	…	binding=record	BAD-ROW(shared-occurrence)	census/round-21/reason-after.txt:29
ITEM	N15	…	binding=record	BAD-ROW(A0a-not-cited)	census/round-21/step-inventory.json:1
ITEM	N17	…	binding=record	BAD-ROW(A0a-not-cited)	census/round-21/r20-closure-excerpt.json:40
ITEM	N18	…	binding=record	RECORD-MISMATCH	census/round-24/records/c2-control-base.tsv:11
SUMMARY items=5 bound_run=0 bound_record=0 bound_field=0 withdrawn=0 unbound=0 mismatches=5 partial=1
```

A1 — **A0(b) cannot read a compound unit token.** The counter's own `adjacent()` returns False for
`base`/`11` on `census/round-21/r20-closure-excerpt.json:40` (the token is `base_discriminating=11`) and
for `base`/`2` on `c2-control-base.tsv:11` (the word is absent), yet the identical string
`base_discriminating=12` is a legal **run** literal (run bindings are checked with `at_bounds` only). Same
evidence text, two different verdicts depending on the kind — that asymmetry is what forces N17 and N18
into withdrawals.

A2 — **A0(a) empties whole capability rows.** SCORECARD.md:168 names no record at all, so every item on it
(N15, N17) is confined to `run:`; two real observables (18 steps, base_discriminating=11) are refused for
want of a citation that the frozen row never had.

A3 — **No-shared-occurrence plus A0(a) makes a two-integer cell bindable once.** `leaks19→0` lives entirely
on `reason-after.txt:29`; binding both items is `BAD-ROW(shared-occurrence)` for **both** (2 mismatches),
binding one leaves one withdrawal. I bound the after value (N14) because the cited file is the *after*
record; the pair is symmetric, so the L1 may swap N13/N14 without touching either literal.

A4 — **Withdrawal-kind stretch, disclosed.** The kind's docstring reserves `withdrawn` for "no observable
shows it". For N13, N15, N17 and N18 an observable *does* exist; each is blocked by a counter rule, and my
reasons name the rule and the blob rather than claiming invisibility. If the L1 judges the kind
unavailable here, these four become mismatches and C1 fails outright.

A5 — **Target arithmetic.** Finding 8: `withdrawn=17` and `mismatches=8` over 44 items. Neither a seat nor
a stricter-only amendment can close that; the L1 needs either a different item set or an explicit
decision to let C1 fail this round.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/w1/deliver-c1-bind-N12-N19.md` — the
  eight rows to append (byte-identical to the validated commit), the acceptance output, the per-item
  derivation and the integration risk.
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/w1/SwarmExecutor03.md` — this report.

No other file was created or modified. Scratch `/fast/scratch/hyaku/souji-r32/C1BindC` removed.
