# R40w2revenger01 — reverse-engineering `commit_distinct` (r39) and the r40 `commit_rows=` / `commit_hashes=` rename

Role: revenger (leaf, read-only). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Landed instrument commit audited: `128e412b0ced3c243dc27c3dd3332054a611bc2e`.
Later revisions observed during the audit: `549d9ec` (C1 cells, register), `994de3b` (current HEAD: evidence-path binding added to `census/round-40/c1-counter.py`).
Scratch: `/fast/scratch/hyaku/souji-r40/w2/R40w2revenger01/` (fixture repos, probes). Removed before yield (see §7).
Tools installed: none. Python used: `python3` 3.14.8 (system).

## 1. Question and axes

Axes attacked (calibration, the C1 instrument):
- A1. What does r39's `commit_distinct` actually compute (name vs computation)?
- A2. Is the r40 rename to `commit_rows=` / `commit_hashes=` honest, and does the r40 gate count what its name says?
- A3. Does the r40 item `R40-CLAIM-D3` (the rename claim) test value or only token presence?
- A4. Do the landed bytes, the receipts and the later HEAD agree on what the rename means?

## 2. A1 — r39 `commit_distinct`: computed as a row count, not a distinct-commit count

Source (landed, `census/round-39/c1-counter.py`, unchanged since `b769bfb`/`a6fe389`; verified `R39_IDENTICAL` against 128e412):

- `:136-152` `parse_register`: for each register row, `commit = parts[7] if len(parts) > 7 else ""`; then
  `if commit and commit != parts[6]: distinct += 1`. `parts[6]` is `receipt_rev`. The variable is named `distinct` but it is a count of rows. No `set`, no hash comparison, no ancestry test.
- `:163` `cells, distinct = parse_register(reg_src)`; `:184` returns `"ok:%d" % distinct`.
- `:247` `distinct = int(note.split(":")[1]) ...`; `:248` prints `REGISTER cells=%d mismatches=%d commit_distinct=%d`; `:251` SUMMARY prints `commit_distinct=%d`.
- `:257` gate: `distinct >= args.min_commit_distinct`; argparse default `:270` `default=2`.

Reproduction — pure function, landed bytes (`cmp` against `census/round-39/c1-counter.py` returned identical):

```
$ git -C .../souji-shokunin show 128e412b0ced3c243dc27c3dd3332054a611bc2e:census/round-39/c1-counter.py > $S/probe/c39.py
$ git -C .../souji-shokunin show 128e412b0ced3c243dc27c3dd3332054a611bc2e:census/round-40/c1-counter.py > $S/probe/c40.py
$ cmp $S/probe/c39.py .../census/round-39/c1-counter.py && echo "c39 bytes == landed"   -> c39 bytes == landed
$ cmp $S/probe/c40.py .../census/round-40/c1-counter.py && echo "c40 bytes == landed"   -> c40 bytes == landed
$ python3 -B $S/probe/probe.py $S/probe/c39.py $S/probe/c40.py
six rows, one commit X != R        r39.parse_register=(6, 6)  r40.parse_register=(6, 6, 1)
six rows, six distinct commits     r39.parse_register=(6, 6)  r40.parse_register=(6, 6, 6)
six rows, commit == receipt_rev    r39.parse_register=(6, 0)  r40.parse_register=(6, 0, 1)
six rows, no commit cell (7-col)   r39.parse_register=(6, 0)  r40.parse_register=(6, 0, 0)
probe rc=0
```

Read: r39's second field is `(cells, rows-with-commit≠receipt_rev)`. Six rows naming one commit read `6`. So `commit_distinct` is not a distinct-commit count. The name is false. (Probe script: `$S/probe/probe.py`, the `load()` imports the scratch copies, which are byte-identical to landed.)

End-to-end r39 gate on a git fixture (see §4 for construction). Same register, six rows, one descendant commit:

```
$ python3 -B .../census/round-39/c1-counter.py --root $D --rev $C2 --items $S/fx39.items.tsv --register reg.tsv --scratch $S/scr39A --min-cells 1
ITEM R-1 CLOSED
REGISTER cells=6 mismatches=0 commit_distinct=6
SUMMARY items=1 open=0 register_cells=6 register_mismatches=0 commit_distinct=6 items_sha=9305b99bbee3
rc=0
```

Verdict A1: **FALSIFIED** — the name `commit_distinct` is false at `census/round-39/c1-counter.py:150-151, 248, 251`.

Also r39 has no direction test: a register whose commits are ancestors of `receipt_rev` passes:

```
$ python3 -B .../census/round-39/c1-counter.py --root $D --rev $C3 --items $S/fx39.items.tsv --register regB.tsv --scratch $S/scr39B --min-cells 1
REGISTER cells=6 mismatches=0 commit_distinct=6
SUMMARY ... commit_distinct=6
rc=0
```

(`regB.tsv`: `receipt_rev=C2`, `commit=C1`, C1 is an ancestor of C2.) That is the r39 limit the r40 prereg names (control: "has no strict-descendant test"), and it is confirmed.

## 3. A2 — the r40 rename: labels, gate and floor

Source (landed `census/round-40/c1-counter.py`; `git log` shows 128e412 is the only commit that introduced its bytes; `8a5fbdb` carries identical bytes — `git diff --quiet 128e412 8a5fbdb -- census/round-40/c1-counter.py` exit 0):

- `:158-176` `parse_register`:
  - `:174` `distinct_rows = sum(1 for _, receipt_rev, commit in rows if commit and commit != receipt_rev)` — the same expression as r39's counter, now honestly named as a row count.
  - `:175` `distinct_hashes = len({commit for _, _, commit in rows if commit})` — a true distinct count of non-empty commit cells (no validation; unresolvable or backwards values are counted too).
- `:187` / `:232` `register_leg` returns `(cells, mismatches, distinct_rows, distinct_hashes, backwards+notancestor, "ok")`. **`:232` hard-codes the note `"ok"`** regardless of `violations`.
- `:321-327` run prints `REGISTER cells=… commit_rows=… commit_hashes=… violations=… <note>`; `:330-334` SUMMARY prints both.
- `:335-343` gate: `open_count == 0 and forged_closed == 0 and cells >= args.min_cells and mismatches == 0 and violations == 0 and commit_rows >= args.min_commit_rows`. **`commit_hashes` is not in the gate.**
- `:354-355` argparse: `--min-cells` default 1, `--min-commit-rows` default **1** (r39: `--min-commit-distinct` default 2, `c1-counter.py:270`). The floor dropped from 2 to 1 by default; `commit_rows` also still counts rows that fail the strict-descendant rule (`violations` gates them, but the printed `commit_rows` does not).
- Docstring `:29-34` says each row's `commit` must be a strict descendant of `receipt_rev`; `commit_rows` is not that count.

Reproduction — scratch fixture (`D=$S/fx.kEGtDR`, `git -C "$D" rev-parse --show-toplevel` == `$D` before the first commit). Reconciler bytes copied from `128e412:tools/souji-citation-reconcile.py`. Notes lines name `` `rcpt.txt` `` in backticks (the reconciler's RECEIPT-UNNAMED rule, `tools/souji-citation-reconcile.py:287-290`). Revs: C0=`2d2d5bb6…`, C1=`3898b9ef…` (`--allow-empty`), C2=`6dd1b141…` (notes + `reg.tsv`), C3=`2a29e8e6…` (+`regB.tsv`), C4=`495c6de9…` (+`regC.tsv`). Full hashes are in the transcript; the counter was run against landed bytes (`$S/probe/c40.py`, cmp-verified):

```
A: python3 -B $S/probe/c40.py --root $D --rev $C2 --items $S/fx.items.tsv --register reg.tsv --scratch $S/scrA2
   (six rows, all commit=C1, a strict descendant of receipt_rev=C0)
   SUMMARY items=1 open=0 forged=0 forged_open=0 forged_closed=0 register_cells=6 register_mismatches=0 register_violations=0 commit_rows=6 commit_hashes=1 ...
   rc=0

B: python3 -B $S/probe/c40.py --root $D --rev $C3 --items $S/fx.items.tsv --register regB.tsv --scratch $S/scrB2
   (receipt_rev=C2, commit=C1: an ancestor, not a descendant)
   REGISTER R-1 BACKWARDS commit-not-descendant 3898b9ef…   (x6)
   REGISTER cells=6 mismatches=0 commit_rows=6 commit_hashes=1 violations=6 ok
   SUMMARY … register_violations=6 commit_rows=6 commit_hashes=1 …
   rc=1

C: python3 -B $S/probe/c40.py --root $D --rev $C4 --items $S/fx.items.tsv --register regC.tsv --scratch $S/scrC2
   (commit == receipt_rev == C1)
   REGISTER R-1 BACKWARDS commit-equals-receipt_rev 3898b9ef…   (x6)
   REGISTER cells=6 mismatches=0 commit_rows=0 commit_hashes=1 violations=6 ok
   SUMMARY … commit_rows=0 commit_hashes=1 …
   rc=1
```

Same fixture, r39 counter, for comparison: A39 `rc=0 commit_distinct=6`; B39 `rc=0 commit_distinct=6` (backwards accepted); C39 `rc=1 commit_distinct=0`.

Lane's own register at HEAD (`git show 549d9ec:census/round-40/cells.tsv`): three rows, all with `commit=556c24a5cacf208c5144c459838712594a43e1f2`. Real run at `994de3b` with landed counter bytes (items, forged, register from the worktree, which equals HEAD):

```
$ cd $L && python3 -B $S/probe/c40.py --root . --rev 994de3b447e9a7bea2abfbd80c4736f6215d3e47 --items census/round-40/c1-items.tsv --forged census/round-40/c1-forged.tsv --register census/round-40/cells.tsv --register-rev 994de3b447e9a7bea2abfbd80c4736f6215d3e47 --min-cells 3 --min-commit-rows 3 --scratch $S/scrReal2
REGISTER cells=3 mismatches=0 commit_rows=3 commit_hashes=1 violations=0 ok
SUMMARY items=3 open=0 forged=3 forged_open=3 forged_closed=0 register_cells=3 register_mismatches=0 register_violations=0 commit_rows=3 commit_hashes=1 items_sha=8f97b0097e09 forged_sha=915b1184e9c6
rc=0
```

Reading: the gate accepts three rows on one commit at `--min-commit-rows 3` (rc 0) while `commit_hashes=1`. The `--min-commit-rows 3` flag is a row floor, not a commit floor.

Verdict A2 (split):
- The field labels are accurate descriptions of what is computed: `commit_rows` = rows with a non-empty commit cell ≠ `receipt_rev` (a row count); `commit_hashes` = distinct non-empty commit cell values. **SAFE** as labels.
- The gate does not count distinct commits; the floor is `commit_rows >= 1` (`c1-counter.py:341, 355`), down from r39's default 2. A one-commit register passes with rc 0 (fixture A; lane's own register at 994de3b). **FALSIFIED** as an enforcement of the distinctness the r39 name advertised (the spot-check's fix, `corpus/lessons/round-39-verifier-spotcheck.md:150`, said "rename … or print both"; r40 printed both and gated on neither distinctness nor the descendant count).
- The `"ok"` note is hard-coded (`c1-counter.py:232`); the line `REGISTER … violations=6 ok` (fixture B and C) is a false label. **FALSIFIED** (cosmetic, but it is in the same line the rename touched).
- `commit_rows` counts backwards and equal rows as well (fixture B: `commit_rows=6` with `violations=6`; C: `commit_rows=0`, `commit_hashes=1`, `violations=6`). The docstring's "strict descendant" language is not what `commit_rows` measures. Rejection itself works: B and C both exit 1. **SAFE** for rejection; the printed number is not the descendant count.

## 4. A3 — the D3 item tests token presence, not value

`census/round-40/c1-items.tsv` line 4 (at 549d9ec and 994de3b):

```
R40-CLAIM-D3	SCORECARD.md	R40-CLAIM-D3	commit_rows=,commit_hashes=	commit_distinct=	census/round-40/c1-counter.py@8a5fbdbddaab24c5ba43fc6a133499efb405f214
```

The must-tokens are the strings `commit_rows=` and `commit_hashes=`; the mustnot is `commit_distinct=`. A line that prints `commit_rows=0 commit_hashes=0` satisfies the same predicate. The item therefore closes on the label, never on the value. **FALSIFIED** as a measure of rename honesty (vacuity: a value-blind predicate for a claim about values). The line it anchors (SCORECARD.md:785 at 549d9ec) says the counter prints both fields and cites `8a5fbdb` as "the counter bytes"; `git log` shows the bytes were introduced at `128e412`, and `8a5fbdb` only carries them unchanged (provenance wording, minor).

## 5. A4 — revisions: landed bytes vs later HEAD (the instrument moved)

- `128e412` (landed): the evidence bound check (`census/round-40/c1-counter.py` ~258-261) requires the 40-hex evidence rev on a good line. No path clause.
- `549d9ec`: `census/round-40/c1-items.tsv`, `cells.tsv` added (`git cat-file -e 128e412:census/round-40/cells.tsv` → not in tree; same for `c1-items.tsv`). **The C1 inputs are absent at the landed revision** — the landed bytes cannot re-run the r40 C1 receipt by themselves.
- During the audit, `census/round-40/c1-counter.py` showed `M` in the worktree (mtime 17:13:30). Its diff added a path-substitution clause (`("`%s`" % row["evidence_path"]) in line`, worktree lines 258-262). Under that worktree bytes, `R40-CLAIM-D3` read `OPEN EVIDENCE-NOT-BOUND`, because SCORECARD.md:785 names `census/round-40/records/c3-after.txt`, not the counter path.
- By the next check the worktree was clean and HEAD had moved to `994de3b` ("bind evidence path as well as revision; add path-substitution control"; 5 files, 55 insertions, 5 deletions, counter +8/-2 lines). Under `994de3b` the HEAD counter and the landed counter both read D3 **CLOSED** and rc 0 (real run above; SCORECARD line was amended by that commit).
- The untracked receipt `census/round-40/records/c1-after-d.txt` (not committed) records `items=3 open=0 … commit_rows=3 commit_hashes=1` at 549d9ec; this matches the landed counter's arithmetic. It is not a committed receipt.

Verdict A4: **FALSIFIED** as a reproducibility claim for the landed instrument alone: the landed bytes do not contain the C1 items or register, and the instrument changed twice (`549d9ec`, `994de3b`) after landing. The rename's honesty (A2 labels) is unaffected by the path clause; the D3 item's outcome is.

## 6. Verdict

- A1 `commit_distinct` (r39): **FALSIFIED** — name says distinct commits; computation is a row count of `commit ≠ receipt_rev`. Evidence: `census/round-39/c1-counter.py:136-152, 248, 251`; probe and fixture A39 above.
- A2 r40 rename: **SAFE as labels, FALSIFIED as gate** — `commit_rows`/`commit_hashes` describe what they compute; the gate reads only the row count with floor 1 (`census/round-40/c1-counter.py:341, 355`), so one-commit registers pass (fixture A; lane register at `994de3b`: `commit_rows=3 commit_hashes=1` rc 0). Hard-coded `"ok"` note at `:232` is **FALSIFIED** as a label.
- A3 D3 item: **FALSIFIED** — token-presence predicate (`census/round-40/c1-items.tsv` line 4) cannot distinguish `commit_rows=0` from `commit_rows=3`.
- A4 revisions/reproducibility: **FALSIFIED** — landed bytes lack C1 inputs; the instrument changed after landing (`994de3b`), and the D3 result depends on which revision is read.

Overall: **FALSIFIED (narrow)**. The rename does not hide a wrong count, but it does not make the gate count what the rename suggests, and the r39 name was false.

## 7. Reproduction block and cleanup

All commands above are re-runnable from the lane with `S=/fast/scratch/hyaku/souji-r40/w2/R40w2revenger01`. The fixture builder is the sequence in §3 (mktemp under `$S`, `git -C "$D" init -q`, check `git -C "$D" rev-parse --show-toplevel` equals `$D`, commit with `-c user.name=R40w2revenger01 -c user.email=scratch@fixture.invalid`). No lane file was edited; no git mutation ran in the lane; the lane's `git status` for the counters was read-only.

Scratch: `$S` (fixture repos `fx.*`, probes, `scr*` dirs) — removed by `rm -rf` before yield; the removal is confirmed in the final message.

Confidence: high for A1 and A2 (reproduced on committed bytes at 128e412 with a git fixture). Medium for A4 — the 17:13 worktree state was transient and I did not capture its full diff; the `994de3b` diff stat is from `git show --stat 994de3b`.
