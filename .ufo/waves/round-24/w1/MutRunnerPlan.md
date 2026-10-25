# MutRunnerPlan — C3 mutation set for `souji-receipt-run.py verify` (souji r24 w1)

## Status
STATUS: PASS. I wrote and ran 15 mutants: 11 primary (one per verify clause) and 4 variants. Each ran against the r23 fixture, the landing r24 fixture and an extra probe, on 3 runner variants. Every restore matched the pristine bytes and the lane hashes are unchanged. 6 primary clauses are covered by neither fixture.

## Evidence
- Lane at HEAD `f9db2181647d91470a724a12d626bd6106805076`. The C3 edit landed **uncommitted** while this seat ran: `git status --porcelain` shows ` M tools/souji-receipt-run.py` and `?? tests/fixtures/r24-receipt-verify.py`.
- Runner variants under test (sha256 of the lane bytes):
  - `head`: `git show HEAD:tools/souji-receipt-run.py`, `e13d0c83…` (identical to lane base `a65fac9`).
  - `wt`: the working-tree tip, `17a6d985…`.
  - `cand`: `.ufo/waves/round-24/w1/souji-receipt-run.py`, `cbe96d73…`. It has the same clauses as `wt`, minus the wider `COUNTS_RE`.
- Detectors:
  - `r23`: `tests/fixtures/r23-receipt-run.py`, `18f4da11…`.
  - `r24`: `tests/fixtures/r24-receipt-verify.py` = `.ufo/waves/round-24/w1/r24-receipt-verify.py`, byte-identical at `531e9248…`. It ran with `--lane-root` set to the lane, so case d is the real regression check.
  - `probe`: an extra probe by this seat (not a preregistered counter). It has one subcase per clause that neither fixture exercises.
- Isolation: the scratch copies changed only `SCRATCH_ROOT`/`SCRATCH_PARENT`, pointing them at `/var/tmp/souji-r24-MutRunnerPlan/tmp`. The r23 copy also prints `ok=<0/1>` per case line (output only). The same patched copies were used for the pristine, mutated and restored runs. Detector-copy sha256: r23 `09b17ef6…`, r24 `65ddbe6e…`, probe `e399caa4…`.
- Protocol, per variant×mutant: write pristine bytes, hash, apply the mutant in place, hash, run all 3 detectors, restore the pristine bytes, hash, and re-run r23 on the restored bytes. All 30 applied mutants: `restored_eq_pristine=True` and restored `r23` `selftest=8/8`. The 5 N-mutants on `head` were `SKIP anchor count 0`, because the clauses are absent there.
- Pristine baselines:
  - `head`: r23 `selftest=8/8`; r24 `cases=8 pass=6 refusals=0/2 regress=5/5` (this is the prereg control); probe 8/10 (`x-a2-jj-only` and `x-shlex` have no clause at head).
  - `wt`/`cand`: r23 `selftest=8/8`; r24 `cases=8 pass=8 refusals=2/2 regress=5/5`; probe 9/10 (`h-redact-symmetry` fails; see Attack A1).
- A failing baseline subcase is scored inconclusive, never killed.
- Lane hash check, before vs after the run: `True`. git 2.56.0, Python 3.14.8. No tools installed.

### Mutants: diff, assigned killer, verdict at tip (`wt`; `cand` verdicts identical)

| id | clause (wt line) | must-kill case | r23 | r24 | probe |
|---|---|---|---|---|---|
| E1 | RECEIPT-UNREADABLE (271) | none in r23 or C3 a–d | survived | survived | killed x-unreadable (rc=1 traceback) |
| E2 | RECEIPT-MALFORMED guard (273) | none | survived | survived | killed x-garbage/x-v2/x-order/x-fence |
| E3 | MALFORMED: line 1 is `receipt=v1` (250) | none | survived | survived | killed x-v2 |
| E4 | MALFORMED: header key order (255) | none | survived | survived | killed x-order |
| E5 | MALFORMED: stdout fence (259) | none | survived | survived | killed x-fence |
| E6 | RECEIPT-REV-MALFORMED (276) | r23 case 4 (short7 half) | **killed** case 4 | survived | survived |
| E7 | RECEIPT-TOOL-ABSENT deleted (281) | r23 case 5 | **killed** case 5 (rc=1 crash) | survived | killed x-absent-exact |
| E7b | TOOL-ABSENT fail-open | r23 case 5 (head only) | head: **killed**; tip: survived | survived | killed x-absent-exact |
| E8 | RECEIPT-TOOL-DIGEST-MISMATCH (282) | r23 case 3 | **killed** case 3 | survived | survived |
| E9 | RECEIPT-COUNTS-ABSENT (286) | none | survived | survived | killed x-counts |
| N1 | RECEIPT-REV-NOT-DURABLE deleted (287) | C3 a | survived | **killed** a | killed x-a2-jj-only |
| N1b | NOT-DURABLE using any ref (refs/jj counts) | none (case a has no ref) | survived | survived | killed x-a2-jj-only |
| N2 | RECEIPT-TOOL-NOT-IN-ARGV deleted (294) | C3 b | survived | **killed** b | killed x-shlex |
| N2b | NOT-IN-ARGV as a substring of `cmd=` | C3 b, substring instance | survived | **killed** b | killed x-shlex |
| N2c | NOT-IN-ARGV: shlex `ValueError` uncaught (291) | none | survived | survived | killed x-shlex (rc=1 traceback) |

C3 case c and the five case-d receipts killed none of these mutants. They are harm detectors (`regress=5/5` under every mutant), not clause detectors.

Unified diffs. Line numbers are in the `wt` scratch copy, which is offset +0 against the lane working tree for the verify body:
```diff
# E1
-    try:
-        with open(args.receipt, encoding="utf-8") as fh:
-            text = fh.read()
-    except OSError as exc:
-        return refuse("RECEIPT-UNREADABLE", str(exc))
+    with open(args.receipt, encoding="utf-8") as fh:
+        text = fh.read()
# E2
-    if header is None:
-        return refuse("RECEIPT-MALFORMED", "header order or fences do not match receipt v1")
# E3
-    if not lines or lines[0] != "receipt=v1":
+    if not lines:
# E4
-        if idx >= len(lines) or not lines[idx].startswith(name + "="):
+        if idx >= len(lines) or "=" not in lines[idx]:
# E5
-    if idx >= len(lines) or lines[idx] != "--- stdout ---":
-        return None
# E6
-    if not REV_RE.match(rev):
-        return refuse("RECEIPT-REV-MALFORMED", f"rev={rev!r}")
# E7
-    if actual is None:
-        return refuse("RECEIPT-TOOL-ABSENT", f"{tool} absent at {rev}")
# E7b
-        return refuse("RECEIPT-TOOL-ABSENT", f"{tool} absent at {rev}")
+        actual = header["tool_sha256"]
# E8
-    if actual != header["tool_sha256"]:
-        return refuse("RECEIPT-TOOL-DIGEST-MISMATCH",
-                      f"receipt {header['tool_sha256'][:12]} != tree {actual[:12]} at {rev}")
# E9
-    if not COUNTS_RE.search(header["_body"]):
-        return refuse("RECEIPT-COUNTS-ABSENT", "no counts line in the recorded output")
# N1  (deletes the 3-line durable_rev block after COUNTS-ABSENT)
-    if not durable_rev(root, rev):
-        return refuse("RECEIPT-REV-NOT-DURABLE",
-                      f"{rev} is not reachable from refs/heads...")   # message elided
# N1b
-    if not durable_rev(root, rev):
+    if not git(root, "for-each-ref", "--contains", rev).stdout.strip():
# N2
-    if tool not in argv:
-        return refuse("RECEIPT-TOOL-NOT-IN-ARGV", f"{tool} is not an argv element of cmd=")
# N2b
-    if tool not in argv:
+    if tool not in header["cmd"]:
# N2c
-    try:
-        argv = shlex.split(header["cmd"])
-    except ValueError:
-        argv = []
+    argv = shlex.split(header["cmd"])
```

Key detector output excerpts (from this run):
- `wt-E6 r23`: `case=4 ok=0 ... got=<short7(rev=1a09e72) rc=0 codes=->`
- `head-E7b r23`: `case=5 ok=0 ... got=<rc=0 codes=->`. `wt-E7b r23`: `case=5 ok=1 ... got=<rc=2 codes=RECEIPT-TOOL-NOT-IN-ARGV>`
- `wt-E8 r23`: `case=3 ok=0 ... got=<stale digest accepted (rc=0)>`
- `wt-N1 r24`: `case=a verdict=FAIL ... refs_containing=0 digest_equal=True verify rc=0 out=verify=ok`
- `wt-N2b r24`: `case=b verdict=FAIL ... substring(tool=counter.py) rc=0`
- `wt-N1b probe`: `probe=x-a2-jj-only ok=0 rc=0 stderr=<> durable_refs=<> any_refs=<refs/jj/keep/probe>`
- `wt probe`: `probe=h-redact-symmetry ok=0 rc=2 stderr=<RECEIPT-TOOL-NOT-IN-ARGV tools/task-count.py is not an argv element of cmd=> run_rc=0 recorded=<cmd=/usr/bin/python3 tools/ta[REDACTED]>`

## Findings
1. **Covered only by the new fixture: N1 (C3 a) and N2/N2b (C3 b).** r23 survives all three on `wt` and `cand`. The landing `r24-receipt-verify.py` kills them: N1 drops it to `refusals=1/2`, and N2/N2b likewise. Location: `tools/souji-receipt-run.py:287` and `:294`. Quote: "if tool not in argv:".
2. **Covered only by r23: E6, E7, E8.** The r24 fixture kills no existing clause; its cases a–d never present a malformed rev, an absent tool or a stale digest.
   - E6 is killed only by r23 case 4's 7-hex half. The branch-name half is refused anyway, because `main` resolves to rev2 and the digest mismatches. Location: `tests/fixtures/r23-receipt-run.py:385`, "short = st["rev1"][:7]".
3. **Covered by neither fixture: E1, E2, E3, E4, E5, E9.** These are UNREADABLE, the MALFORMED guard and its three parse sub-checks, and COUNTS-ABSENT. The probe kills each one, so they are real gaps, not equivalent mutants.
   - E1 and E2 turn an exit-2 refusal into an exit-1 traceback. E3–E5 and E9 make verify accept malformed or counts-less receipts with exit 0.
   - Location: `tools/souji-receipt-run.py:250`, `:255`, `:259`, `:271`, `:273`, `:286`.
4. **Masking regression in r23 case 5 at tip (E7b).** At `head`, r23 case 5 kills a fail-open TOOL-ABSENT. At `wt`/`cand`, the new N2 clause refuses that same receipt with `RECEIPT-TOOL-NOT-IN-ARGV`, because the doctored `tools/absent-at-rev.py` is not in `cmd=`. r23 matches the code generically, so case 5 still passes. r23 case 5 therefore no longer pins TOOL-ABSENT after C3. Location: `tests/fixtures/r23-receipt-run.py:417`, "ok = proc.returncode != 0 and bool(CODE.findall(combined(proc)))".
5. **N1b survives C3.** Case a uses a ref-less commit. The landing fixture header says "(a `git commit-tree` object never stored in a ref, same tree as the receipt's" (`.ufo/waves/round-24/w1/r24-receipt-verify.py:9`). A verify that counts any ref, including `refs/jj/*`, therefore passes C3 a. That breaks the runner's own rule, "refs/jj/* never counts — Q37" (`tools/souji-receipt-run.py:28`).
6. **N2c survives both fixtures.** No case presents an unparseable `cmd=`, so dropping the `ValueError` guard turns the refusal into a traceback. Location: `tools/souji-receipt-run.py:291`.
7. All five r23 receipts keep `regress=5/5` under every mutant on `wt`/`cand`. Read-only, against the lane: each receipt's `tool=` is an exact argv element of its `cmd=`, and each `rev=` is contained in `refs/heads/master` (`git for-each-ref --contains`).

## Attack log
- **A1. The new argv clause reintroduces a run/verify asymmetry (a redaction false refusal).**
  - What happens: `run` writes `cmd=` through `redact()`, which applies "(re.compile(r"sk-[A-Za-z0-9_.-]+"), "[REDACTED]")," (`tools/souji-receipt-run.py:76`) to "f"cmd={redact(shlex.join(args.command))}"," (`:230`). A tool whose repo path contains `sk-`, such as `tools/task-count.py`, is recorded as `tools/ta[REDACTED]`.
  - Measured: `run` exits 0, then `verify` refuses the receipt with `RECEIPT-TOOL-NOT-IN-ARGV` (probe output above).
  - The frozen case c uses `tools/tiny-counter.py`, so the counter cannot see this.
  - In-lane exposure: no current `tools/` name matches. Tracked paths with the shape do exist (`git ls-files` shows `.ufo/waves/round-22/w1-task-result.json`), so the hazard is latent rather than live.
  - Reported, not a counter-change proposal.
- **A2. `run` has no tool-in-argv check.** [INFERENCE, from reading `cmd_run` at `tools/souji-receipt-run.py:145-239`.] `run --tool tools/x.py -- python3 ./tools/x.py` would write a receipt that the tip's `verify` refuses. The candidate's own docstring says "`./tools/x` does not match `tools/x`". C3 makes `verify` stricter than `run` on this axis. Not executed this run.
- **A3. The C3 case set leaves N1b and N2c alive, and r23 case 5 is masked (Findings 4–6).** A refs/jj-only commit for case a and an unparseable `cmd=` for case b would kill them. Recorded as coverage findings; no predicate or case change is proposed.

Notes: I could not find a `godspeed` skill file under `/home/vgpnk/.omp`, so I did not read one. No tools were installed. Scratch `/var/tmp/souji-r24-MutRunnerPlan/` was removed after this report was written.

uncovered=6
