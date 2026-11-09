# R92ReviewerC1 — C1 wording falsification (round 92, seat R92ReviewerC1)

Assignment: falsify C1's stated wording on committed bytes. Own-only: seat dir
`.ufo/waves/round-92/w1/R92ReviewerC1/` and this report. Scratch
`/fast/scratch/hyaku/souji-r92/R92ReviewerC1/` (deleted before yield; text
receipts copied into the seat dir first). Lane read-only; no commits, no
mutations of frozen instruments. Prereg read first:
`census/round-92/preregistration.txt` (commit F e8d31f06, P1 44d45b44,
P2 1d015a2d, lane base 5339b2ac).

No tool installs (none needed).

## Independent runs (mine, --jobs 4)

All commands run with cwd `/home/vgpnk/Projects/shokunin/souji-shokunin`;
work dirs under the seat scratch; `python3 -B` throughout.

### After arm (r92 population, 47 targets)

```
python3 -B census/round-92/c1-survivor-search.py \
  --counter census/round-87/c1-pointer-counter.py \
  --harness census/round-92/c1-false-row-harness.py \
  --population census/round-92/c1-false-rows.tsv --lane . \
  --fleet-root /home/vgpnk/Projects/shokunin \
  --work <scratch>/work-after --jobs 4 \
  --ids census/round-92/c1-targets.json
```

Printed (full log: seat dir `after-r92-search.log`):

- `SEARCH-SUMMARY generated=47 ambiguous=0 uncompiled=0 hung=0 scored=47 killed=47 survived=0`
- exit 0. 47/47 `killed=yes`, 0 `killed=no`.

Matches the predicated line exactly. The prereg predicates `--jobs 8`; the
assignment orders `--jobs 4`. The SUMMARY is jobs-invariant (futures are
collected in submission order; jobs only changes concurrency). Wall time
328.72 s at jobs 4.

### Control arm (r91 population, same 47 targets)

Same command with `--population census/round-91/c1-false-rows.tsv`
(log: seat dir `control-r91-search.log`):

- `SEARCH-SUMMARY generated=47 ambiguous=0 uncompiled=0 hung=0 scored=47 killed=0 survived=47`
- exit 0. 0 `killed=yes`. Wall time 252.53 s.

Matches the predicated control exactly.

### Pristine harness on the r92 population

```
python3 -B census/round-92/c1-false-row-harness.py \
  --counter census/round-87/c1-pointer-counter.py --lane . \
  --fleet-root /home/vgpnk/Projects/shokunin \
  --work <scratch>/work-pristine \
  --population census/round-92/c1-false-rows.tsv
```

Printed (log: seat dir `pristine-r92-harness.log`):

- `ROW LD4r where=ledger-resolve rev=BASE item=P04 class=- expect=MOVED/0 got=MOVED rc=0 match=yes`
- `SUMMARY rows=64 mismatches=0 accepted=0 refused_true=0 errors=0`
- exit 0. Wall time 20.47 s.

Matches the predicated pristine line exactly.

## Sentence table

Verdicts: **holds** / **neutral** / **falsifies-wording**. "Neutral" means
the wording is imprecise but the prereg's own stated limits or the filed
instruments confine it so no defensible falsification follows; such rows
carry what would be needed to falsify them.

| # | Prereg sentence | Verdict | Evidence |
|---|---|---|---|
| 1 | "The search ... generates 270 mutants" | holds | `census/round-92/records/c1-search-r91-full.txt` recounts to 270 units: 260 `SEARCH` lines + 10 `SKIP` lines; summary `generated=270 ambiguous=9 uncompiled=0 hung=1 scored=260 killed=136 survived=124`. Independent recount: killed 136, survived 124, ambiguous 9, hung 1 (a272c34 `SKIP ... state=hung`). |
| 2 | "on the r91 63-row population 9 are skipped as ambiguous ..., 1 hangs, 260 are scored and 124 survive" | holds | Same recount. 63 non-comment rows in `census/round-91/c1-false-rows.tsv` (65 lines: 2 `#` comments + 63 rows). |
| 3 | "(no r91 row asserts the counter's exit code 0 on a successful run)" | holds | Grepped every r91 row's `expect_rc` (field 9): only `-` (56) and `1` (7). Zero `0`. Verified by awk over all 63 rows. |
| 4 | "ONE appended row, LD4r (LD4 with expect_rc 0 ...)" | holds | Field-by-field: LD4r = LD4 in all 8 functional fields (where/rev/population/item/cls/target/exp_got identical: `ledger-resolve BASE r77 P04 - - MOVED`); id `LD4`→`LD4r`, `expect_rc` `-`→`0`, rationale rewritten. No other difference. |
| 5 | "the r92 population ... (64 rows = the r91 63 byte-for-byte plus one comment line and LD4r)" | holds | Byte-level: `r92.startswith(r91)` is True for the file bytes; `l92[:65]==l91` (all 65 r91 lines verbatim, incl. both comments); remainder is exactly one new `#` comment + `LD4r`. 64 non-comment rows. |
| 6 | "kills the 47 survivors listed in census/round-92/c1-targets.json" | holds | Targets (47 ids) ⊂ r91 survivors (124) with none outside; residual file has exactly the other 77 (`residual == survivors − targets`); feasibility killed-47 set == targets set exactly; my after run killed all 47, control killed none. |
| 7 | Predicated after SUMMARY `...killed=47 survived=0` EXIT 0 | holds | Independent run, see receipts. |
| 8 | Predicated pristine `SUMMARY rows=64 ...` with LD4r `rc=0 match=yes`, exit 0 | holds | Independent run, see receipts. |
| 9 | Predicated control `...killed=0 survived=47` EXIT 0 | holds | Independent run, see receipts. |
| 10 | "(sha256 fd0a8e24...)"; "counter unchanged" | holds | Counter sha256 = `fd0a8e244a5e0afe...` as stated; `git diff 77ccef7c HEAD -- census/round-87/c1-pointer-counter.py` is empty (unchanged since its r87 commit). |
| 11 | r92 population sha256 `f66341fc...`, targets sha256 `5a8f6087...` | holds | Both `sha256sum` match the stated prefixes exactly. |
| 12 | "Harness ... (the r91 harness with one added population pin; no new row type or code path)" | holds | `diff` (receipt `harness-r91-vs-r92.diff`): only the module docstring (9 lines) and one `POP_PINS` entry (`...774...: 64}` — the r92 pin). No code-path change. |
| 13 | CLAIM "every comparison flip, and/or swap, `not` deletion, True/False swap and 0/1 swap ... plus two hand edits of the final return" | neutral | See nuance notes below. The code's `SWAP` map is: `==↔!=`, `<↔<=`, `>↔>=`, `and↔or`, `True↔False`, `not`→deleted, NUMBER `0↔1` (exactly the strings "0"/"1"); HAND = 2 edits of the line `    return 0 if ok else 1` (line 574, the final return; unique in the file). "Comparison flip" is loose for `<→<=`/`>→>=` (weaken, not full flip to `>`/`<`), and `is`/`in`/`not in` comparisons are not mutated. But STATED LIMITS (iv) confines the census to "single-token operator edits and two hand edits only; it is not a full mutation space", so the operative claim is the finite, enumerated 270 — which reproduces. To falsify, a reviewer would need the limits to not govern; they do, on the prereg's own terms. |
| 14 | "9 are skipped as ambiguous (their source line occurs more than once)" | holds | `score()` returns `ambiguous` when `src.count(m["old"]) != 1`, `old` being the whole source line — the parenthetical is exact. |
| 15 | "the search ... to stop a harness run after --timeout seconds (default 300) by killing its process group and count it `hung` (neither killed nor survived)" | holds | Code kills the process group (`os.killpg(p.pid, SIGKILL)` with `start_new_session=True`), state `hung`, excluded from killed/survived; SUMMARY prints the `hung=` field; default `--timeout 300`. |
| 16 | Limit (v): "its survivor set equals the set salvaged from two earlier interrupted runs (census/round-92/records/c1-survivors-r91.json)" | holds | Set equality verified: census `killed=no` ids (124) == salvaged file ids (124), exactly. |
| 17 | Limit (vi): "the 47 targets were chosen as exactly the survivors a pre-freeze run on the r92 population killed (census/round-92/controls/c1-feasibility-r92-prefreeze.txt)" | holds | Feasibility `killed=yes` ids (47) == targets ids (47), exactly; its `killed=no` ids (77) == residual file ids exactly. Note: the feasibility receipt's search sha (`8755b53f...`) and SUMMARY shape (no `hung=` field) differ from the frozen search (`c393d941...`) — a pre-freeze instrument was used for *discovery*, disclosed as such; the frozen claim's predicates were re-derived with the frozen search (my runs above). |

### Nuance notes (noted, not counted as falsifications)

- `gen()` deduplicates `(old, new)` pairs and skips multi-line tokens and
  comment lines. For tokens in comments or spanning lines, "every" in the
  CLAIM sentence would overstate — but comment tokens are not operator edits
  and the limits confine the space. Neutral, see row 13.
- `a574c11-0-to-1` (`return 0 if ok else 1` → `return 1 if ok else 1`) is
  semantically the same "always 1" as the hand edit `h-exit-always-1`. The
  count 270 = 268 single-token + 2 hand is still exact, and both appear in
  the census and in the 47 targets. No double-count in any SUMMARY.
- `ambiguous` is checked *before* the compile check, so a mutant that is both
  ambiguous and uncompilable reports as `ambiguous`. The docstring's order
  matches the code. No uncompiled mutants arise (all 9 ambiguous SKIPs are
  `state=ambiguous`, 0 `uncompiled`).

## Search-tool reading

File: `census/round-92/c1-survivor-search.py` (sha256 `c393d941...`; docstring
lines 2-19, `gen` lines 47-73, `score` lines 76-105, `main` lines 108-169).

1. **Enumeration.** `gen()` tokenizes the counter with `tokenize`:
   `OP`/`NAME` tokens found in `SWAP` (`==`,`!=`,`<`,`<=`,`>`,`>=`,`and`,`or`,
   `True`,`False`) are replaced by the swap image; `NAME` `not` maps to `""`
   (deletion via `lstrip(" ")` so the splice stays valid); `NUMBER` tokens
   exactly `"0"`/`"1"` swap. Multi-line tokens, comment lines and duplicate
   `(old,new)` pairs are skipped. An id `a<line>c<col>-<tok>-to-<rep>` is
   minted per token. Then the two HAND entries append `h-exit-always-1` /
   `h-exit-always-0` on `    return 0 if ok else 1` (line 574, the counter's
   final return, occurring once). This matches the CLAIM's own enumeration
   modulo the "comparison flip" looseness noted in row 13.
2. **`--ids` refusal.** Robust, and independently exercised: an unknown id
   and an empty list each print
   `C1-SEARCH-FATAL: --ids names an empty, duplicate or ungenerated id` and
   exit **2**, before any scoring. Refusal also covers duplicates
   (`len(set(want)) != len(want)`). Note (neutral): a *missing* ids file
   raises an uncaught `FileNotFoundError` traceback with exit 1 rather than
   the clean `C1-SEARCH-FATAL` message (`main` line 139 opens it without a
   guard) — a usability nit, not a wording falsification: the prereg only
   claims refusal of unknown/empty/duplicate ids, which holds.
3. **`ambiguous` vs `uncompiled` reporting matches the docstring.** Order in
   `score()`: ambiguous (line occurs ≠ once) → compile check → `uncompiled`
   → harness run → `scored` / `hung` (timeout, process group killed).
   Docstring says the same, in the same order. `hung` uses
   `start_new_session=True` + `os.killpg(p.pid, SIGKILL)` — the harness and
   the counter it spawns share the group, so the whole tree dies.
4. **Kill rule faithfully applied.** `killed = rc != 0` per mutant
   ("a kill is a non-zero harness exit"); SUMMARY = `generated` (after
   `--ids` filtering), `ambiguous`, `uncompiled`, `hung`, `scored`,
   `killed = scored − survived`, `survived = rc == 0` count. The `generated=`
   field in the predicated lines is the post-filter count (47) — the full
   270 is separately established by the census record + my recount.
5. **Disk hygiene.** Each per-mutant harness work tree (`d/w`) is deleted
   after scoring (`shutil.rmtree`); only the mutant counter copy and
   `harness.out` remain (measured: 2.1 MB for the 47-mutant after run).
   `--work` under `/tmp`/`/var/tmp`/`/dev/shm` is refused with exit 2.
   Exit 0 when the search ran, 2 on setup error — as documented.
6. **`--emit` writes exactly `{id, clause, old, new}` for survivors** —
   consistent with the residual/salvaged JSON shape.

## Falsification list

**NO-FALSIFICATION.**

Tried:

1. Independent re-derivation of all three predicated lines with `--jobs 4`
   (after, control, pristine) — all reproduce exactly, including exit codes.
2. Recount of every `SEARCH`/`SKIP` line in the filed full census
   (`c1-search-r91-full.txt`): 270 / 9 / 0 / 1 / 260 / 136 / 124 — exact.
3. Grepped every r91 row's `expect_rc`: only `-` and `1`; no `0`. LD4r is
   the sole `0` in r92.
4. Byte-prefix check of r92 vs r91 populations: `r92` begins with the full
   `r91` bytes; remainder is one comment + LD4r. LD4 vs LD4r field diff:
   only id, `expect_rc`, rationale.
5. Hashes of counter, both populations, targets, both harnesses, search —
   all match the prereg's stated pins; counter unchanged since its r87
   commit (empty diff); harness r91→r92 diff is docstring + one pin.
6. Set equalities: targets ⊂ r91 survivors; residual = survivors −
   targets; feasibility killed-set = targets; salvaged set = census
   survivors.
7. `--ids` refusal exercised with unknown and empty ids (exit 2).
8. Read `gen`/`score`/`main` against the docstring and the CLAIM sentence
   by sentence — enumeration, ambiguity, uncompilation, hung, kill rule,
   exit codes all agree; two neutral loosenesses noted above (rows 13, and
   the missing-file traceback nit) that cannot falsify under the prereg's
   stated limits.

Residual risk: the independent runs cover only the 47-target arm of the
census; the 270-mutant full census was verified by recount of the filed
record, not by a fresh 270-mutant run (each harness run clones a ~0.7 GB
fixture tree; a full re-run would take hours and re-measure the same
receipt). A fresh full run could in principle expose a receipt
transcription error, but the record's internal arithmetic (counts, sums,
set equalities with two independently filed survivor sets) leaves nowhere
for such an error to hide without breaking one of the equalities checked.
