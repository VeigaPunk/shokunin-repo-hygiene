# S82CriticClaims — falsification of C1/C2 claims

## C1 calibration — verdict QUALIFIED (core delta HOLDS, one branch vacuous/un-grounded)
- Do-nothing control K-a red for right reason: `controls/c1-K-a-r81-counter.txt`
  `ROW NF-F/NF-G expect=REFUSED got=MOVED match=no`, `SUMMARY rows=32 mismatches=2 accepted=2`,
  `ROW NF-H/NF-I/PF-1 match=yes` already refused/MOVED under r81. 2 accepted exactly the own-tree decoys.
- `_owntree_ok` (`c1-pointer-counter.py:310-319`, fired at `:353` before basename) is the real delta:
  `target[:tr.start]==token[:kr.start]` + `_capture_ok` after `round-<N>`; NF-F `decoy/` fails CAPTURE
  (`no-capture-match decoy/Swarm...`), TF4 `waves/a2w1/...` passes (`want=[a2w1,Swarm] have=[a2w1,Swarm]`).
  K-b owntree-dropped `mismatches=2 accepted=2 [NF-F,NF-G]` (receipt `controls/c1-K-b-owntree-dropped.txt`),
  K-c suffix->last-component `mismatches=2 [NF12c,NF-I]` — both stay red as frozen.
- PF-1 label MOVED is right and not part of delta (prereg `:49-55`): token
  `.ufo/waves/round-61/w1/S61ExecRealRecord/...` prefix `.ufo/waves`, target prefix `census` → judged by the
  r81 census branch (`tokenprefix != census`, `_capture_ok` suffix-True), already MOVED in K-a (`match=yes`).
  The r82 `census-in-tree` branch (`:365-371`, requires `tokenprefix==census`) never fires for PF-1 nor any of
  the 32 rows (no token under `census/`). Verified: `cap(PF-1)=True want=[S61Exec..,txt] have=[w1,S61Exec..,txt]`.
  So the "PF-1" branch is vacuous for the frozen target; a cheaper rule (only `_owntree_ok`) already reaches 32/0/0.
- MEDIUM: census-in-tree branch refuses a neighbourhood with no real-row predicate — the exact Q146 failure the
  prereg cites at `:25-26`. It harms no frozen/regression row (r78 22/22+12/12, r77 35/35+7/7, r79 9/9,
  r80 18/18, r81 25/25 all green) but is speculative tightening; delete it or ground it with a real NF row.
- TF4 caution: named r77 P04 real pair is token `.ufo/waves/round-32/a2w1/SwarmExecutor08.md` →
  ledger target `census/round-32/waves/a2w1/...` (`census/round-77/c2-pointer-ledger.tsv:5`). TF4 target
  `.ufo/waves/round-32/waves/a2w1/...` is a synthetic fixture fence, never a real ledger move — it tests that
  own-tree does not over-refuse, it is not evidence. Rule is not otherwise over-fitted: `_capture_ok` =
  `waves/|wave/|records/wave-*` + whole-component suffix (`:296-307`) matches the 14 real r77/r78 MOVED rows.
- Calibration vs quality: NF-F/G fix is calibration (accepted 2→0 on lowest axis 7). Census-in-tree half is
  quality/hardening smuggled into a calibration claim. Receipts `records/c1-after.txt: SUMMARY 32/0/0 EXIT=0`
  hold either way.

## C2 operability — verdict HOLDS (launch-mode delta, honestly labelled after M2 correction)
- No-signal behaviour unchanged: diff `tools/souji-vault-verify.sh` = new `cli_kill_tree` (`:227-242`) called
  only from `cli_on_signal` (`:243-264`) + `local pid=${CLI_PID:-}` (drops `${!:-}`). `cli_claim` post-`wait`
  path byte-identical. `pgrep -P` recursion runs only on signal. Selftest `57/0`, r17 `37/0/0`,
  probe-D `6/6` (write rail, signal-independent) — `records/c2-regress-*.txt`, `records/probe-d-successor.txt`.
- Both-launches 16/0/0 (`records/c2-after.txt`, `records/c2-after-monitor.txt`): fork stub (`c2-vault-signal-counter.py:89`
  `sleep 600 &` then `exec sleep 600`) puts grandchild in its own PGID under `SHELLOPTS=monitor`, outside
  timeout's group → group kill misses (K-a monitor: `v7/v8/m1/m2 survivors=1 mismatches=4`). Tree snapshot via
  PPID still finds it (`exec` preserves pid, PPID intact), TERM→0.1s→KILL per pid, then group kill remains.
  Mechanism frozen rows see. v9/v10 termign pass via 2s KILL fallback.
- Do-nothing under default: `records/prefreeze/c2-base-default.txt SUMMARY 16/0/0` — baseline is 16/16, so
  default-mode delta is zero. Prereg `:80-85` + lesson M2 disclose "the change is launch-mode, not
  default-mode". Honest labelling HOLDS; any "operability improved" reading must carry the monitor qualifier.
- `$!` drop is a safety fix, not a finding: `CLI_PID=$!` (`:291`) is the timeout pid; a signal before
  assignment would previously signal whatever `$!` last held (innocent pid) — now no-ops. Window shrinks to
  one instruction; orphan risk bounded, wrong-kill eliminated.
- Missing-`pgrep` degrades to baseline (group kill only), no new failure mode.

## Harm hunt
- M1 freeze chronology (HIGH for provenance, no effect on counter bytes): `records/freeze-check-at-P.txt`
  `FINDINGS=3` (C0 FROZEN-EDITED + C1/C2 CONTROL-ADDED), still reproduces at HEAD (re-ran freeze-check,
  `--rev 7dc3c7260fa19b2311d413597ad8f948c57be9c1` → `findings=3`). P `1cb7c7d1` already contains
  `preregistration.txt`, contradicting prereg `:3-5` "P strictly precedes F". Prereg sha P→F→F3:
  `02f83d→dc8fe0→d2a9b5` (F3 `d2a9b5…` is HEAD; sha audit `git show <rev>:census/round-82/preregistration.txt`).
  F2 revert-then-F3-edit + one-line parse fix (`diff 1cb7c7d1..HEAD`) disclosed as corrective in lesson M1 but
  the freeze-check never goes green; receipts bind `instrument_sha256` digests so measurements stand.
  Closure must not claim chronology/subs—stance pass.
- No harm to SCORECARD numbers: C1 regressions green, C2 selftest/r17 ratios unchanged, `census-after` ok.
- Future harm LOW: census-in-tree branch could false-refuse a future token-under-`census` true capture; no
  real row today (tokens are `.ufo/...` / lane paths).
- No other entry-point harm: `cli_kill_tree` touches only the signal path; refused-config/foreground path
  (`cli_tmp_ok` false) untouched as stated limit.

## Commands run (read-only; no frozen counter replayed — verdict derives from committed bytes + receipts)
- `diff` r81→r82 `c1-pointer-counter.py` and `tools/souji-vault-verify.sh` vs base `488956c`
- Python truth tables for `_capture_ok`/`_owntree_ok` on P04/P07 token-target pairs; `sha256` of prereg at
  P/F/F2/F3/HEAD; `git show --name-only 1cb7c7d1`; freeze-check re-run at HEAD sha above.

## Files written
- `.ufo/waves/round-82/w1/S82CriticClaims.md` (this report); scratch dir `/fast/scratch/hyaku/souji-r82/S82CriticClaims/` (empty).
