# R93ExecC1 — C1 re-derivation (after + control + pristine + pins + ledger-edit proof + per-kill rows)

Independent re-derivation of C1's after arm, control and pristine run on committed bytes. All runs cwd=/home/vgpnk/Projects/shokunin/souji-shokunin (lane), work under /fast/scratch/hyaku/souji-r93/R93ExecC1 (deleted before yield). Receipts (text only, 52 KB total) in .ufo/waves/round-93/w1/R93ExecC1/. No tool installs; no git/jj mutation.

## Verdict
Every number in C1's predicate re-derives exactly. No falsification: the kill rule, both claims' wording, and the control all hold. NO-FALSIFICATION.

## 1. After arm (r93 population) — search receipt `after-search.out`
Command: `python3 -B census/round-93/c1-survivor-search.py --counter census/round-87/c1-pointer-counter.py --harness census/round-93/c1-false-row-harness.py --population census/round-93/c1-false-rows.tsv --lane . --fleet-root /home/vgpnk/Projects/shokunin --work <empty> --jobs 2 --ids census/round-93/c1-targets.json`

- `SEARCH a491c22-<-to-<= line=491 killed=yes rc=1`
- `SEARCH h-ok-admits-one line=552 killed=yes rc=1`
- `SEARCH-SUMMARY generated=2 ambiguous=0 uncompiled=0 hung=0 scored=2 errored=0 killed=2 survived=0`
- EXIT 0. **Matches prereg predicate exactly.** Receipt header pins (search-run verified): counter fd0a8e24…, harness 1868a570…, population d6439f65…, search 6089260b…, ids fedb2653… (n=2).

## 2. Control (r92 population) — search receipt `control-search.out`
Same invocation with `--population census/round-92/c1-false-rows.tsv`:

- `SEARCH a491c22-<-to-<= line=491 killed=no rc=0`
- `SEARCH h-ok-admits-one line=552 killed=no rc=0`
- `SEARCH-SUMMARY generated=2 ambiguous=0 uncompiled=0 hung=0 scored=2 errored=0 killed=0 survived=2`
- EXIT 0. **Matches prereg control exactly.**

## 3. Pristine harness — receipt `pristine-harness.out`, EXIT 0
Command: `python3 -B census/round-93/c1-false-row-harness.py --counter census/round-87/c1-pointer-counter.py --lane . --fleet-root /home/vgpnk/Projects/shokunin --work <empty> --population census/round-93/c1-false-rows.tsv`

- `ROW LD4 where=ledger-resolve rev=BASE item=P04 class=- expect=MOVED/- got=MOVED rc=0 match=yes`
- `ROW LD4r where=ledger-resolve rev=BASE item=P04 class=- expect=MOVED/0 got=MOVED rc=0 match=yes`
- `ROW LD5 where=ledger-drop rev=BASE item=P04 class=- expect=UNRESOLVED/1 got=UNRESOLVED rc=1 match=yes`
- `ROW LD6 where=ledger-trim rev=BASE item=P04 class=- expect=MOVED/0 got=MOVED rc=0 match=yes`
- `SUMMARY rows=66 mismatches=0 accepted=0 refused_true=0 errors=0` (71 lines total: 66 ROW + 4 header + SUMMARY)
- EXIT 0. **Matches prereg pristine predicate exactly.**

## 4. Pin table (sha256sum on committed bytes vs prereg)
| artifact | measured | prereg | verdict |
|---|---|---|---|
| counter census/round-87/c1-pointer-counter.py | fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b | fd0a8e244a5e0afe… | match |
| harness census/round-93/c1-false-row-harness.py | 1868a570b9100559637ab454e6f7737bfdc881339cf8045d75cc22b3060a84a4 | 1868a570b9100559… | match |
| population census/round-93/c1-false-rows.tsv | d6439f65a632cf83fb9d47c78bd0d32d1f9104d2f6443bdfd770e1c1c5e1a88e | d6439f65a632cf83fb9d47c78bd0d32d1f9104d2f6443bdfd770e1c1c5e1a88e (full) | match |
| population census/round-92/c1-false-rows.tsv | f66341fc2867f6b5dbd8515a717747370c700fd31bf7aaa497a292ca65027c51 | (as POP_PINS 64) | match |
| targets census/round-93/c1-targets.json | fedb26533f3d7c3eba26deba4245ea61dea7e3624fcb2a2318e072e5281974ef | fedb26533f3d7c3e… | match |
| search census/round-93/c1-survivor-search.py | 6089260be7d18c5f48c5bf1289e159efba534f2ef1c5d730f9b4f356d37ed71d | 6089260be7d18c5f… | match |
| r92 harness / r92 search / r92 targets | 818f84d96a88… / c393d941eb2e… / 5a8f608787aa… | (r92 pins in harness POP_PINS) | consistent |

Population structure: r92 = 16,979 bytes / 67 lines (POP_PINS counts 64 non-comment data rows). r93 = 18,077 bytes / 70 lines (66 data rows). Prefix check: `r93[:16979] == r92` is **True** (r92 population is a byte-for-byte prefix of r93). r93 tail = one comment line + LD5 row + LD6 row. Prereg limit (iv) "reviewer must confirm the r92 64 rows are byte-identical" — confirmed.

## 5. Hunk inventory — harness diff (r92 → r93)
`diff -u census/round-92/c1-false-row-harness.py census/round-93/c1-false-row-harness.py` yields exactly 4 hunks, all expected, **zero UNEXPECTED**:
1. **Docstring** (lines 1–12 of diff): module docstring now describes the r93 population and the two new row types, plus the no-r92-row-reaches-either-clause rationale. Classification: docstring.
2. **Pin** (line ~152–156): one added entry to `POP_PINS`: `"d6439f65a632cf83fb9d47c78bd0d32d1f9104d2f6443bdfd770e1c1c5e1a88e": 66`. Classification: pin.
3. **New row types** (line ~426–462): `where` allowlist extended to `ledger-drop`/`ledger-trim`; `lanelike` tuple refactored from an inline tuple to a named variable; the BASE/lane/root dispatch uses `lanelike`. Classification: new row types (mechanical refactor enabling them).
4. **New row types** (line ~436–474 of the `if where in ("ledger-drop","ledger-trim")` block): the ledger-edit engine itself — reads the frozen ledger in the lane, requires the item to occur exactly once in a 4+-column row (else `C1-HARNESS-FATAL` exit 2), drops the row or cuts it to 3 columns, writes `ledger-<rid>.tsv` under `--work`, runs the counter with `--ledger <edited>`, and judges the item's `ITEM <id> … status=` against `exp_got`/`exp_rc` exactly like the other row types (rc=2 → `match=error`; otherwise mismatch counting). No other code paths touched. Classification: new row types.

## 6. Hunk inventory — search diff (r92 → r93)
`diff -u census/round-92/c1-survivor-search.py census/round-93/c1-survivor-search.py` yields hunks all in the three prereg-declared change classes, **zero UNEXPECTED**:
1. **Docstring**: three numbered changes (kill rule tightening, `h-ok-admits-one`, SIGINT/SIGTERM + /tmp-guard) rewritten; output format now documents `killed=yes|no|errored` and `errored=<E>`. Classification: docstring + summary-format.
2. **HAND**: one added tuple `("h-ok-admits-one", '    ok = counts["resolved"] == len(pop) and not unknown\n', '    ok = counts["resolved"] >= len(pop) - 1 and not unknown  # h-ok-admits-one\n')`; existing hand-edit clause string generalized from `"hand edit: exit code"` to `f"hand edit: {hid}"`. Classification: hand edit (predicted by c1-prediction.txt).
3. **Kill rule**: new `verdict(rc,out)` — killed only on harness exit 1 with ≥1 `ROW … match=no` line (match=error-only or exit 2 → `errored`); `score()` returns a 4-tuple `(verdict, rc)`; the SEARCH line prints `killed=<v>`; summary gains `errored=<E>` with S = E + K + V. Classification: kill rule.
4. **Robustness**: new `_stop`/`_reap`/`LIVE` set; SIGTERM handler; interrupt path kills live harness groups, deletes per-mutant `w` trees, exits 130; `--work`/`--emit` both covered by the /tmp guard; `finally:` around harness-out write + work-tree deletion. Classification: robustness (no scoring change).

## 7. Ledger-edit proof — LD5/LD6 edit ONLY P04's own row
Method: scratch copy of the harness (`/fast/scratch/.../harness-ld.py`) with two injections only (a rows filter to LD5,LD6 after the pin check; a `shutil.copyfile` saving each edited ledger to `$R93EVID/edited-<rid>.tsv`). The copy is in scratch and was never committed; the edited artifacts were copied into this seat dir as `edited-LD5.tsv` / `edited-LD6.tsv`. Frozen ledger: `census/round-77/c2-pointer-ledger.tsv` (sha256 011faa0e96333b28af0418df8f56a5cbb169ed71aa0e9f688ee6d97d7aa39ba5).

- LD5 edited sha256 `6891c7b7243f7b256ad59a245f2a203212a77a884645f45cf482e0d09976208e`. **Diff vs frozen: exactly one line removed — line 5 `P04\tMOVED\tcensus/round-32/waves/a2w1/SwarmExecutor08.md\tr32 wave capture, byte-equal`** and nothing else (`5d4`). No ledger line touched in any other position.
- LD6 edited sha256 `b21e1da2fc6548a347741d7d485bbb24c9c2b8b1de95903b3bea7e18eb4c7fb1`. **Diff vs frozen: exactly line 5 rewritten — the same P04 row cut to its first three columns `P04\tMOVED\tcensus/round-32/waves/a2w1/SwarmExecutor08.md`** and nothing else (`5c5`). Nothing else changed.
- The LD5/LD6-only run printed `ROW LD5 … rc=1 match=yes`, `ROW LD6 … rc=0 match=yes`, `SUMMARY rows=2 mismatches=0 … errors=0`, EXIT 0 (receipt `ld-run.out`). Expected: pristine `len(r) < 3` accepts a 3-column row, so P04 resolves MOVED with exit 0 — as observed.

## 8. Per-kill killing-row table
Each mutant was rerun alone via a one-id `--ids` JSON (seat-receipts `hok-search.out` / `a491-search.out`, both `SEARCH-SUMMARY generated=1 … killed=1 survived=0` EXIT 0). Full 66-row harness outputs saved as `hok-harness.out` / `a491-harness.out`.

| mutant | killing ROW(s) | other red rows | attribution |
|---|---|---|---|
| h-ok-admits-one (line 552) | exactly one `match=no`: `ROW LD5 where=ledger-drop rev=BASE item=P04 class=- expect=UNRESOLVED/1 got=UNRESOLVED rc=0 match=no` (SUMMARY `rows=66 mismatches=1 errors=0`) | none — all 65 other rows `match=yes` | **LD5 is the sole killer** |
| a491c22-<-to-<= (line 491) | exactly one `match=no`: `ROW LD6 where=ledger-trim rev=BASE item=P04 class=- expect=MOVED/0 got=UNRESOLVED rc=1 match=no` (SUMMARY `rows=66 mismatches=1 errors=0`) | none — all 65 other rows `match=yes` | **LD6 is the sole killer** |

Cross-check on the control: on the r92 population both mutants survive (`killed=no rc=0` each), so no r92 row is red for either mutant — i.e., no OTHER row red contradicts the control. The two kills are mutually exclusive: h-ok is killed by LD5's exit-code assertion (the slackened test returns 0 where 1 is required) and a491c22 by LD6's status assertion (the widened guard refuses the 3-column row, leaving P04 UNRESOLVED and the run at rc=1 where rc=0 is required). This is exactly the prereg's stated binding, confirmed line-for-line.

## 9. Falsification check
Tried to falsify C1's number and wording by: re-running the full after/control/pristine predicates independently; prefix-comparing the populations; auditing every hunk of both instrument diffs; diffing both edited ledgers against the frozen ledger; and attributing each kill via one-id reruns. Nothing falsifies any sentence of C1. **NO-FALSIFICATION.**

Caveats for the L1 (risk/notes, not blockers):
- The ledger-edit proof used a scratch harness copy with a row filter and a copyfile injection; the injection is 2 added lines, verified byte-identical otherwise by construction. Pristine LD5/LD6 behavior was additionally verified with the unmodified filed harness.
- All receipts live in `.ufo/waves/round-93/w1/R93ExecC1/` (52 KB). Scratch `/fast/scratch/hyaku/souji-r93/R93ExecC1/` was removed before yield; per-run work dirs were empty-dir verified by the search/harness guards.
- Never more than one harness work tree at a time was held outside the search's own `--jobs 2` (each scored mutant's tree is deleted by the search immediately).

Report: .ufo/waves/round-93/w1/R93ExecC1.md
