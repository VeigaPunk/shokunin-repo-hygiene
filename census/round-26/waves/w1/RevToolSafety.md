# RevToolSafety — C3 tool input-hygiene safety review

Reviewed artifact: committed tip `tools/souji-axis-check.py` and `tests/fixtures/r26-axis-check.py` (HEAD `0c92c2e`; receipt `census/round-26/records/c3-after.tsv` rev `c594901`, rc=0, claims=3 flags=0, cases=12 pass=12). Note: the committed tool differs materially from the w1 draft `souji-axis-check.py` — the draft's `errors="replace"` open and `Refusal` exception class are gone in the landed version; this review is against the landed bytes.

## Status
STATUS: PASS — the frozen C3 counter (K1 self-hosting + K2 12-case fixture) is not gameable; no attack vector found. However, the tool has four real input-hygiene defects the implementation must close before reuse: no identical-path/alias guard, blocking reads on special files, an uncaught `UnicodeDecodeError` that violates the exit-2 refusal contract, and unbounded whole-file reads.

## Evidence
All runs performed this session with `python3 -B` from the lane root; synthetic inputs under `/var/tmp/souji-r26-RevToolSafety/` (removed at close).

- Self-hosting control (real frozen prereg + real SCORECARD.md): `claims=3 flags=0`, rc=0.
- A2 — `--prereg $D/dual.txt --scorecard $D/dual.txt` (same path): `claims=1 flags=0`, rc=0 (silent same-file pass). `dual.txt` contains both a MACHINE BLOCK and an `## Axes` table plus a trailing `## Capabilities` heading.
- B2 — scorecard arg = symlink to the same target: `claims=1 flags=0`, rc=0.
- C — binary non-UTF8 scorecard: uncaught `UnicodeDecodeError`, traceback, rc=1.
- D — directory as scorecard: refusal `cannot read scorecard: [Errno 21] Is a directory`, rc=2.
- F — FIFO as prereg: hung; killed only by external `timeout 5` (rc=124).
- Code locations (committed tool): `tools/souji-axis-check.py:53,93` `text = open(path, encoding="utf-8").read()`; `:56` MACHINE BLOCK regex; `:97` Axes-section regex; `:101-103` row parse restricted to `OWNED_AXES`; `:138-159` `main()` (no path identity or regular-file checks before both opens); `:126-129` R4; `:131-134` R3.
- Fixture: `tests/fixtures/r26-axis-check.py:47-48` scratch constants; `:340-353` scratch-base guards + per-pid run dir; `:373-377` stub written under run dir; `:379-393` stub execution + control; `:398-403` `finally: shutil.rmtree(run_dir, ignore_errors=True)` + best-effort `os.rmdir(SCRATCH_BASE)`.

## Findings
1. **[High, integrity] No identical-path/alias refusal.** `main()` passes the two args straight to two independent `open()` calls with no identity check (lines 144-151). A file engineered to contain both a MACHINE BLOCK and an Axes table validates its own claims against its own axes rows and exits 0 (demonstrated A2; B2 via symlink alias). The two inputs are distinct domains; identical targets make the run meaningless and self-referential. Must refuse: `os.path.samestat(os.stat(a), os.stat(b))` (covers hardlinks) and equal `os.path.realpath` (covers symlinks) → `fail2` exit 2.
2. **[High, availability] Special files block or balloon memory.** `open(path).read()` on a FIFO blocks indefinitely (demonstrated F; no internal timeout — the frozen counter invocation has none either). On endless character devices (e.g. `/dev/zero`) `read()` never EOFs and grows memory unbounded (unrun; [INFERENCE] from `read()` semantics). Non-regular inputs must be rejected before opening via `os.stat` `S_ISREG` (following symlinks), with a size cap on the read.
3. **[Medium, contract] Non-UTF8 input crashes instead of refusing.** `open(path, encoding="utf-8").read()` (lines 53/93) raises `UnicodeDecodeError`, which is not `OSError` and escapes the `try/except`; the tool prints a traceback and exits 1 (demonstrated C), violating the frozen contract "exit 2 on usage/input refusal" (`preregistration.txt` C3: "exit 2 on usage/input refusal"). The draft's `errors="replace"` was dropped in the landed rewrite. Fix: catch `UnicodeError` alongside `OSError` → `fail2`.
4. **[Low-Medium] Whole-file unbounded reads.** Both parsers slurp the full file with no size bound (lines 53/93); a multi-GB or endless input is fully materialized. Fold into finding 2 (size cap).
5. **[Low] Symlink semantics implicit.** Following is undocumented and defeats identity detection (finding 1). Symlink loops do fail as `OSError` → clean refusal. No confidentiality boundary exists (the tool reads only what the caller names; no writes, no subprocess, no env/network — read scope is exactly the two named inputs, confirmed by full 163-line source read).
6. **[PASS] Fixture stub-arm hygiene.** Stub `souji-axis-check-stub.py` is created only under `/var/tmp/souji-r26-ExecAxisFixture/run-<pid>/case-12/` (lines 373-377) and is removed by `shutil.rmtree(run_dir, ignore_errors=True)` in `finally` plus best-effort `os.rmdir` of the base (lines 398-403). It is written mode 0644 (not chmod +x) and executed via the interpreter (`sys.executable -B`), so the executable bit is not required. Leftover dirs on SIGKILL are possible and harmless (unique per-pid names; base rmdir fails silently). Trivial TOCTOU on the base symlink precheck (lines 340-345) is negligible at this trust level. Nothing executes against the lane's real prereg/SCORECARD.
7. **[Note] Stricter-than-spec R2.** Committed `check()` additionally flags a claim with no `surface-class:` line (line 121) — the printed spec (C3 R2) lists mappings but not the missing-line case. Not gameable (stricter, can only add flags; the real prereg has surface-class lines, so K1 is unaffected). Fidelity note only.
8. **[Note] R3 tie handling.** `min(scores, key=...)` (line 132) picks one lowest axis; with the real table (coverage 8, calibration 7, operability 8) calibration wins. If two owned axes tied at the minimum, only one must be declared — acceptable to the singular spec wording.

## Residual risk and verification gaps
- `/dev/zero` OOM behavior was inferred from `read()` semantics, not executed (deliberately not run — it would risk the host). No exception path was exercised for symlink loops (code-inspection only).
- The exit-code contract breach (finding 3) is unreachable from the 12 frozen fixture cases (all inputs are UTF-8), so K2 cannot observe it; it only matters for real-world robustness.
- No gameable path to a false green was found: the fixture executes the actual tool bytes; the frozen K1 invocation uses the lane's real prereg/SCORECARD; none of the findings can flip either counter to green. No attack is reported.
