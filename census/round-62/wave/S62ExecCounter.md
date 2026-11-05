# S62ExecCounter — scoped findings (souji round 62, C1, wave w1)

Seat: S62ExecCounter, leaf executor. Scope: build the frozen C1 counter and 7-case
matrix; self-check with the do-nothing control and two stubs. The candidate tool was
NOT run (L1 runs the frozen run after the freeze).

## Files delivered (all under `.ufo/waves/round-62/w1/S62ExecCounter/`)

- `c1-counter.py` — stdlib-only counter; per frozen spec. sha256
  `c6a3159d32b099ba1730a2cc23ffe6eafce40a2c264f6f019fa3e8f468a2150a`.
- `c1-matrix.tsv` — frozen A–G expectations. sha256
  `89abc018ad0715e306de66982fbdbb5d973824f3170ff7c37d647b2ab8ba0b23`.
- `do-nothing.txt` — base bytes in the new slot (`--arm plain`).
- `stubs.txt` — always-accept and always-refuse stub arms.
- `SHA256SUMS`, `report.md` (full commands, outputs, limits).

## Result: counter operational; frozen predicate machine-checked

- Do-nothing control (base bytes as candidate): `SUMMARY matrix=7 base_forgeries=3
  base_honest=2 new_forgeries=3 new_honest=2 class_mismatches=4 regress=PASS`,
  `EXIT=1`, shell exit 1 — the required `new_forgeries=3` + exit 1 shape holds.
  Case-level evidence on the lane base `16fa821fdce00e709d6895ccfc7aaffa465af195`:
  D/E/F (skip-worktree-forged, assume-unchanged-forged, skip-worktree-unmodified) all
  ACCEPTED by the base writer (rc=0, receipt written); C refused with
  `lane worktree is dirty`; G refused with `worktree tools/instr.sh differs from
  committed bytes`. This empirically confirms the round claim's forgery surface and the
  L1's base-revision probe.
- Stub arms both fail the counter (exit 1): always-accept → `new_forgeries=5`,
  regress FAIL; always-refuse → `new_honest=0`, regress FAIL.
- Regression arm green for the base bytes both slots: r60 fixture last line
  `SUMMARY cases=8 pass=8 fail=0 control=ALWAYS-WRITE-REJECTED,ALWAYS-REFUSE-REJECTED`
  (REGRESS base=PASS new=PASS in the do-nothing run).
- Exit-2 paths exercised: missing work dir, /tmp work dir, non-40-hex `--rev` — all
  `C1-COUNTER-FATAL: …` + `EXIT=2`, shell exit 2.

## L1 runbook (after freeze)

```
python3 -B .ufo/waves/round-62/w1/S62ExecCounter/c1-counter.py \
  --root . --matrix .ufo/waves/round-62/w1/S62ExecCounter/c1-matrix.tsv \
  --base-rev 16fa821fdce00e709d6895ccfc7aaffa465af195 --rev <full40-or-none> \
  --tool <candidate.py> --work <scratch>/c1-w1 --arm tool
```
Pass gate: `new_forgeries=0 new_honest=2 class_mismatches=0 regress=PASS`, `EXIT=0`,
G's new_findings = `RECEIPT-INDEX-FLAG-CONCEALED`. Use `--work` under scratch (not
/tmp). `--rev` is metadata/validated-only in this counter; the receipts bind each
fixture repo's own seed HEAD.

## Limits (details in report.md)

No flock/concurrency coverage; no sparse-checkout or submodule paths in the matrix;
expected classes are stderr substrings only (per-path/tag naming not machine-checked);
gate applies to the NEW slot only; accepted/errored refuse rows count as class
mismatches; verdict mapping is exit-code exact (refuse = exit 2). No tools installed.
Scratch `/fast/scratch/hyaku/souji-r62/S62ExecCounter/` removed before yield. No lane
production paths touched; lane git usage read-only throughout.
