# W2 MutateGateParse — LG parse-channel mutation probe

STATUS: PARTIAL — the two allowed detectors killed 7 of 12 single mutants; 5 survived with both suites green. All pristine/restored runs passed and every scratch copy was restored before deletion.

## Scope, axes, and verdict

- **Axis: calibration.** Measure fault sensitivity and clean-input specificity, without treating a surviving mutant as permission to weaken the contract.
- **Evidence-integrity constraint:** isolated copies, one behavior-bearing line per mutant, identical detectors on pristine/mutated/restored bytes, full SHA-256 provenance, and scratch cleanup.
- **Scoped verdict: partial.** The detector pair distinguishes seven of these twelve deliberate defects, but does not distinguish the five survivors below. This is a test-coverage finding, not a claim that the unmodified gate contains those injected defects; no round-admission decision is made here.
- Leaf-only work: no delegation, lane source/test edits, staging, commits, integrations, alternate runtime, census execution, or installs/upgrades. The only lane write is this report.

The assigned two-command detector was run for **every copy at every phase**: 12 copies × 3 phases × 2 commands = **72 detector invocations**. Commands were invoked directly by the Python Eval orchestrator with `asyncio.create_subprocess_exec`, at most six concurrently, with a 180-second per-command bound. All 72 completed without timeout; all stderr streams were empty. The suite-internal synthetic repositories and their git commits are fixture behavior, not lane changes.

## Inputs and unchanged lane bytes

- Gate: `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py`. Start/end SHA-256: `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2`.
- External fixture: `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py`. Start/end SHA-256: `aae67c9c7bafd86f1b745193ac4aead74b3a3403b5c5ade33991d246e6413f2f`.
- The lane HEAD supplied by L1 was `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`; the executed copy is identified by its observed byte hash above, not an inferred commit lookup. No git revision command was run by this seat.
- Each mutant was copied from `/var/tmp/souji-r16-MutateGateParse/pristine.py`, which had the same gate hash. Hashline edits changed exactly one source line in each copy. No test expectation was mutated.

## Mutants, expected detectors, and outcomes

The intended behavioral detector for each defect is the pair `python3 <copy> --selftest` plus `python3 <fixture> --tool <copy>`. A kill requires a passing pristine run and a failing mutated run; those preconditions hold for all reported kills. `S` denotes selftest; `F` denotes external fixture.

| Copy | Source point and single substitution | Expected killing case | Mutated actual output | Verdict |
|---|---|---|---|---|
| m1 | `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py:59` — `(?:sh&#124;py)` → `(?:sh)` in `CITED_PATH_RE`. Omit registry-cited Python scripts. | selftest `nonparsing-cited-py`; fixture `py-compile-defects` | S rc=1, `SELFTEST pass=17 fail=1`; F rc=1, `SUMMARY total=15 failed=1` | **killed** |
| m2 | `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py:59` — Remove the `tests/fixtures` alternative from `CITED_PATH_RE`. Omit an entire promised citation namespace. | No existing killer; proposed fixture-namespace case below | S rc=0, `SELFTEST pass=18 fail=0`; F rc=0, `SUMMARY total=15 failed=0` | **survived** |
| m3 | `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py:59` — Remove the `census/round-\d+` alternative from `CITED_PATH_RE`. Omit the census citation namespace. | No existing killer; proposed census-namespace case below | S rc=0, `SELFTEST pass=18 fail=0`; F rc=0, `SUMMARY total=15 failed=0` | **survived** |
| m4 | `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py:59` — `[A-Za-z0-9_.-]+` → `[A-Za-z0-9_-]+`. Omit dotted basenames while leaving the extension dot intact. | No existing killer; proposed dotted-basename case below | S rc=0, `SELFTEST pass=18 fail=0`; F rc=0, `SUMMARY total=15 failed=0` | **survived** |
| m5 | `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py:208` — `if err:` → `if err and proc.returncode != 0:`. Ignore rc=0 warnings after the nonzero-rc branch. | fixture `truncated-heredoc` | S rc=0, `SELFTEST pass=18 fail=0`; F rc=1, `SUMMARY total=15 failed=1` | **killed** |
| m6 | `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py:204` — `proc.stderr.decode(...)` → `proc.stdout.decode(...)`. Read the wrong subprocess stream for the warning rule. | fixture `truncated-heredoc` | S rc=0, `SELFTEST pass=18 fail=0`; F rc=1, `SUMMARY total=15 failed=1` | **killed** |
| m7 | `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py:216` — `compile(content, path, "exec")` → `compile(content, path, "single")`. Use interactive-statement mode rather than module mode. | No existing killer; proposed clean multi-statement case below | S rc=0, `SELFTEST pass=18 fail=0`; F rc=0, `SUMMARY total=15 failed=0` | **survived** |
| m8 | `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py:216` — `compile(content, path, "exec")` → `compile(content, path, "exec", flags=0x400)`. Request AST-only compilation, losing the module-level-return rejection. | fixture `py-compile-defects` (`tools/returns.py`) | S rc=0, `SELFTEST pass=18 fail=0`; F rc=1, `SUMMARY total=15 failed=1` | **killed** |
| m9 | `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py:545` — Missing-path finding ID `LG-MISSING-REG` → `LG-PARSE-REG`. Keep exit=1 but misclassify the required missing-path channel. | selftest `missing-cited-path`; fixture `missing-reg-and-changed` and `uncited-nobase-invisible` | S rc=1, `SELFTEST pass=17 fail=1`; F rc=1, `SUMMARY total=15 failed=2` | **killed** |
| m10 | `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py:93` — `SCRIPT_EXT_RE = re.compile(r"\.(?:sh&#124;py)$")` → `SCRIPT_EXT_RE = re.compile(r"\.(?:sh)$")`. Skip changed Python scripts without changing citation parsing. | No existing killer; proposed uncited changed-Python case below | S rc=0, `SELFTEST pass=18 fail=0`; F rc=0, `SUMMARY total=15 failed=0` | **survived** |
| m11 | `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py:564` — Changed-script `parse_script(..., resolved)` → `parse_script(..., base)`. Parse the good base bytes instead of the broken revision bytes. | selftest `changed-nonparsing-with-base`; fixture `missing-reg-and-changed` | S rc=1, `SELFTEST pass=17 fail=1`; F rc=1, `SUMMARY total=15 failed=1` | **killed** |
| m12 | `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py:216` — `compile(content, path, "exec")` → `compile(content.splitlines()[0], path, "exec")`. Compile only the header line. | fixture `py-compile-defects` (`tools/returns.py`) | S rc=0, `SELFTEST pass=18 fail=0`; F rc=1, `SUMMARY total=15 failed=1` | **killed** |

No inconclusive baseline was counted as a kill. The selftest alone killed m1/m9/m11; the external fixture killed m1/m5/m6/m8/m9/m11/m12. In particular, the fixture catches stderr-only heredoc warnings and the AST-only/header-only compile regressions that the selftest leaves green.

## Survivor counterexamples and smallest test fixes

These are **counterexamples to detector sufficiency**: the exact injected defect described in the mutant table passed both unchanged suites. The proposed added cases below are **[INFERENCE — not executed]**; this seat was authorized to execute only the two existing commands, not an expanded custom harness. Expected outcomes are the existing contract, not a new one. The smallest repair is additional assertions/cases in the existing tests; no production-code or contract change is proposed.

### m2 — omitted `tests/fixtures` citations: fails detector coverage

Both suites remained green. Existing selftest green-world citations already include `tests/fixtures/fx.py`, but its content is valid and the clean assertion does not pin `checked_reg` (`G:703,708,766–772,782–784` below). Existing malformed/missing citation cases use `tools/`.

Proposed case: cite `tests/fixtures/registry.py` containing `return 0
`, plus an absent `tests/fixtures/ghost.sh`, in the synthetic `SKILL.md`. Require `LG-PARSE-REG` for the Python path and `LG-MISSING-REG` for the absent shell path, with exit 1. Keep the namespace under test, rather than replacing it with an easier `tools/` path.

### m3 — omitted `census/round-<n>` citations: fails detector coverage

Both suites remained green. The selftest cites only a passing `census/round-1/run.py` in its green world (`G:702,707`).

Proposed case: cite `census/round-77/run.py` containing `return 0
` and an absent `census/round-77/missing.sh`. Require path-specific `LG-PARSE-REG` and `LG-MISSING-REG`, exit 1. A count assertion on the existing four-entry green-world registry would additionally detect silently dropping either namespace, but the proposed malformed/missing case checks the promised finding IDs as well.

### m4 — dotted basename omitted by citation regex: fails detector coverage

Both suites remained green. The injected character-class restriction silently excludes a basename with an interior dot.

Proposed case: cite `tools/release.v2.py` containing `return 0
` and absent `tools/missing.v2.sh`. Require `LG-PARSE-REG` and `LG-MISSING-REG` for those exact paths. This remains within the original one-segment basename character class, not an expansion to deeper paths.

### m7 — interactive `single` compilation mode: fails clean-input specificity coverage

Both suites remained green. The fixture actually observed a changed historical replay row count while still passing:

```text
pristine: CASE	replay-b410186	PASS	exit=1 lg_rows=5
mutated:  CASE	replay-b410186	PASS	exit=1 lg_rows=15
restored: CASE	replay-b410186	PASS	exit=1 lg_rows=5
```

That is an observed 5 → 15 → 5 finding-row change accepted by the replay assertions, not an independently enumerated list of which added rows were false positives. The fixture reports row totals rather than those finding details. **[INFERENCE]** module-vs-interactive compile semantics explain the extra findings.

The existing green Python negative controls are one `print` statement (`G:645`; `F:244,461`). Proposed minimal clean case: a cited Python module `tools/two.py` containing `x = 1
x += 1
`. Require exit 0, no `LG-PARSE-REG`, and a positive checked-registry count. This distinguishes valid module compilation from interactive single-statement compilation without executing the file.

### m10 — changed-script filter drops Python: fails changed-path coverage

Both suites remained green. Existing changed-script defects are shell files (`G:804–817`; `F:281–304`), so dropping only `.py` from `SCRIPT_EXT_RE` has no killing case.

Proposed case: leave `tools/uncited.py` uncited; commit a valid module at base, then modify it to `return 0
`. With `--base`, require `LG-PARSE-CHANGED` for the exact path, exit 1, and no `LG-PARSE-REG` for that uncited path. Without `--base`, require no parse finding for it. Add a broken newly added `.py` in the same case if covering both `A` and `M` diff statuses. Do not make it registry-cited, because that could let `LG-PARSE-REG` mask loss of the changed-script check.

Source aliases in this section: 
- `G` = `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py`.
- `F` = `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py`.

## Actual detector output

For **each** of m1–m12, pristine and restored selftest output ended `SELFTEST	pass=18	fail=0` (rc=0), and pristine and restored fixture output ended `SUMMARY	total=15	failed=0` (rc=0). That is 48 individually executed passing detector invocations, not one baseline extrapolated to all copies.

Below are all mutated failing-case lines, the two actual summary lines per mutant, and the replay observation for m7. Non-failing case rows are omitted here; no stderr or timeout was omitted.

### m1 — killed

```text
selftest rc=1
CASE	FAIL	nonparsing-cited-py	exit=0 ids=[] err=None
SELFTEST	pass=17	fail=1
fixture rc=1
CASE	py-compile-defects	FAIL	exit=0 lg_rows=0 FAIL(exit=0 want 1 (stderr=); missing LG-PARSE-REG ~ tools/indented.py; missing LG-PARSE-REG ~ tools/returns.py)
SUMMARY	total=15	failed=1
```

### m2 — survived

```text
selftest rc=0
SELFTEST	pass=18	fail=0
fixture rc=0
SUMMARY	total=15	failed=0
```

### m3 — survived

```text
selftest rc=0
SELFTEST	pass=18	fail=0
fixture rc=0
SUMMARY	total=15	failed=0
```

### m4 — survived

```text
selftest rc=0
SELFTEST	pass=18	fail=0
fixture rc=0
SUMMARY	total=15	failed=0
```

### m5 — killed

```text
selftest rc=0
SELFTEST	pass=18	fail=0
fixture rc=1
CASE	truncated-heredoc	FAIL	exit=0 lg_rows=0 FAIL(exit=0 want 1 (stderr=); missing LG-PARSE-REG ~ tools/hd.sh)
SUMMARY	total=15	failed=1
```

### m6 — killed

```text
selftest rc=0
SELFTEST	pass=18	fail=0
fixture rc=1
CASE	truncated-heredoc	FAIL	exit=0 lg_rows=0 FAIL(exit=0 want 1 (stderr=); missing LG-PARSE-REG ~ tools/hd.sh)
SUMMARY	total=15	failed=1
```

### m7 — survived

```text
selftest rc=0
SELFTEST	pass=18	fail=0
fixture rc=0
CASE	replay-b410186	PASS	exit=1 lg_rows=15
SUMMARY	total=15	failed=0
```

### m8 — killed

```text
selftest rc=0
SELFTEST	pass=18	fail=0
fixture rc=1
CASE	py-compile-defects	FAIL	exit=1 lg_rows=1 FAIL(missing LG-PARSE-REG ~ tools/returns.py)
SUMMARY	total=15	failed=1
```

### m9 — killed

```text
selftest rc=1
CASE	FAIL	missing-cited-path	exit=1 ids=['LG-PARSE-REG'] err=None
SELFTEST	pass=17	fail=1
fixture rc=1
CASE	missing-reg-and-changed	FAIL	exit=1 lg_rows=2 FAIL(missing LG-MISSING-REG ~ tools/ghost.sh)
CASE	uncited-nobase-invisible	FAIL	exit=1 lg_rows=1 FAIL(missing LG-MISSING-REG ~ tools/ghost.sh)
SUMMARY	total=15	failed=2
```

### m10 — survived

```text
selftest rc=0
SELFTEST	pass=18	fail=0
fixture rc=0
SUMMARY	total=15	failed=0
```

### m11 — killed

```text
selftest rc=1
CASE	FAIL	changed-nonparsing-with-base	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-REG'] err=None
SELFTEST	pass=17	fail=1
fixture rc=1
CASE	missing-reg-and-changed	FAIL	exit=1 lg_rows=1 FAIL(missing LG-PARSE-CHANGED ~ tools/uncited.sh)
SUMMARY	total=15	failed=1
```

### m12 — killed

```text
selftest rc=0
SELFTEST	pass=18	fail=0
fixture rc=1
CASE	py-compile-defects	FAIL	exit=1 lg_rows=1 FAIL(missing LG-PARSE-REG ~ tools/returns.py)
SUMMARY	total=15	failed=1
```

## Before / mutated / restored SHA-256 and cleanup

Restoration used `cp` from the original scratch `pristine.py`, not a reverse edit. Every restored hash equals its own pristine hash, and the same two detectors were rerun afterward.

| Copy | Pristine SHA-256 | Mutated SHA-256 | Restored SHA-256 |
|---|---|---|---|
| m1 | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` | `d78c31e5646c8af8b791ae9c9350f94ce894eb90a96566891e7dd536a307bf4e` | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` |
| m2 | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` | `403cbb55e0fd6f7279c7450205dab94974d55a339bc7c2873c3050e653653748` | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` |
| m3 | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` | `75251fab48c64246aa3d65ed1a935a07a84b079e6704cc643f6b00d980cbeda8` | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` |
| m4 | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` | `a422bd6720ad3fae441482ac78c4f8a0d89501a9bdc2371b32f569836da07c14` | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` |
| m5 | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` | `7f9d7ced45f42d70c3948b6f014a0dae7b7312226300c865d3dd80c60eec71bf` | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` |
| m6 | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` | `7c3bd570ed4719f3b9530bd127b41980e45dee7b016b9cbd0095e4f3873fd282` | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` |
| m7 | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` | `e4ce036de75739d33f166dd934391535974b43df041e5f1424fb6409c6888fa7` | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` |
| m8 | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` | `df48f92ef8f7427480bcb9fcb7a3f4378c9fc3109ab901731075479b52e327e4` | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` |
| m9 | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` | `520c69379d9fb01e60f03b0c98dafdd1d104857b2a507c4101ad121658f3f551` | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` |
| m10 | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` | `093dafb0da42fb7c56ecdcf22ea4a5fea7d322c5f341787a96d73989a35863dd` | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` |
| m11 | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` | `6a1507949aa2884fc192b088dc88103ed2a41eab73f68490cfc3f5d457dc0865` | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` |
| m12 | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` | `9edb2690616e998a9e67fe0e86128e3b80688681492ec1c7b3f2df514d2a9435` | `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` |

After restoration and the restored detector runs, `rm -rf -- /var/tmp/souji-r16-MutateGateParse` exited successfully. An exact-path `glob` then returned `Path not found: /var/tmp/souji-r16-MutateGateParse`. Thus all twelve mutants and the pristine scratch backup were deleted; no scratch evidence path is offered as a durable dependency. The exact deltas, observed outputs, hashes, and command log are retained in this report.

## Commands

These are every shell command issued by the seat, plus the exact argv-rendered detector commands invoked directly from Eval (no shell was used for those). Commands are grouped by phase, not completion order. Non-shell operations were exact-file reads, twelve single-line hashline edits under the assigned scratch directory, checksum bookkeeping and stdout summarization in Eval, the exact-path post-cleanup glob, and this report write. No other behavioral command was run.

**Authorized detector-owned extra temp directories:** besides the assigned `/var/tmp/souji-r16-MutateGateParse/`, the unchanged gate and fixture use `/var/tmp/souji-landing-gate-selftest-*` (`G:749,967–968`), `/var/tmp/souji-landing-gate-*` (`G:527,589–590`), and `/var/tmp/souji-r16-lgfixture-*` (`F:224–226,521–522`); the fixture also creates its vacuity stub inside its own scratch root (`F:500–503`). L1 explicitly authorized these existing detector scratch roots. Their `finally` cleanup paths are in the cited source; unique directory suffixes were not emitted and were not independently listed. No custom detector directory outside the assigned scratch root was created by this seat.

### Setup shell command

```sh
mkdir -p /var/tmp/souji-r16-MutateGateParse && cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /var/tmp/souji-r16-MutateGateParse/pristine.py && cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m1.py && cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m2.py && cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m3.py && cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m4.py && cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m5.py && cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m6.py && cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m7.py && cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m8.py && cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m9.py && cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m10.py && cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m11.py && cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m12.py
```

### Start hash shell command (concurrent with setup)

```sh
sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py
```

### Pristine detector commands

```sh
python3 /var/tmp/souji-r16-MutateGateParse/m1.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m1.py
python3 /var/tmp/souji-r16-MutateGateParse/m2.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m2.py
python3 /var/tmp/souji-r16-MutateGateParse/m3.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m3.py
python3 /var/tmp/souji-r16-MutateGateParse/m4.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m4.py
python3 /var/tmp/souji-r16-MutateGateParse/m5.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m5.py
python3 /var/tmp/souji-r16-MutateGateParse/m6.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m6.py
python3 /var/tmp/souji-r16-MutateGateParse/m7.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m7.py
python3 /var/tmp/souji-r16-MutateGateParse/m8.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m8.py
python3 /var/tmp/souji-r16-MutateGateParse/m9.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m9.py
python3 /var/tmp/souji-r16-MutateGateParse/m10.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m10.py
python3 /var/tmp/souji-r16-MutateGateParse/m11.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m11.py
python3 /var/tmp/souji-r16-MutateGateParse/m12.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m12.py
```

### Mutated detector commands

```sh
python3 /var/tmp/souji-r16-MutateGateParse/m1.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m1.py
python3 /var/tmp/souji-r16-MutateGateParse/m2.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m2.py
python3 /var/tmp/souji-r16-MutateGateParse/m3.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m3.py
python3 /var/tmp/souji-r16-MutateGateParse/m4.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m4.py
python3 /var/tmp/souji-r16-MutateGateParse/m5.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m5.py
python3 /var/tmp/souji-r16-MutateGateParse/m6.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m6.py
python3 /var/tmp/souji-r16-MutateGateParse/m7.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m7.py
python3 /var/tmp/souji-r16-MutateGateParse/m8.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m8.py
python3 /var/tmp/souji-r16-MutateGateParse/m9.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m9.py
python3 /var/tmp/souji-r16-MutateGateParse/m10.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m10.py
python3 /var/tmp/souji-r16-MutateGateParse/m11.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m11.py
python3 /var/tmp/souji-r16-MutateGateParse/m12.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m12.py
```

### Restoration shell command

```sh
cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m1.py && cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m2.py && cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m3.py && cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m4.py && cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m5.py && cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m6.py && cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m7.py && cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m8.py && cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m9.py && cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m10.py && cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m11.py && cp /var/tmp/souji-r16-MutateGateParse/pristine.py /var/tmp/souji-r16-MutateGateParse/m12.py
```

### Restored detector commands

```sh
python3 /var/tmp/souji-r16-MutateGateParse/m1.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m1.py
python3 /var/tmp/souji-r16-MutateGateParse/m2.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m2.py
python3 /var/tmp/souji-r16-MutateGateParse/m3.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m3.py
python3 /var/tmp/souji-r16-MutateGateParse/m4.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m4.py
python3 /var/tmp/souji-r16-MutateGateParse/m5.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m5.py
python3 /var/tmp/souji-r16-MutateGateParse/m6.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m6.py
python3 /var/tmp/souji-r16-MutateGateParse/m7.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m7.py
python3 /var/tmp/souji-r16-MutateGateParse/m8.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m8.py
python3 /var/tmp/souji-r16-MutateGateParse/m9.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m9.py
python3 /var/tmp/souji-r16-MutateGateParse/m10.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m10.py
python3 /var/tmp/souji-r16-MutateGateParse/m11.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m11.py
python3 /var/tmp/souji-r16-MutateGateParse/m12.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateParse/m12.py
```

### End hash shell command (concurrent with restored detectors)

```sh
sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py
```

### Cleanup shell command

```sh
rm -rf -- /var/tmp/souji-r16-MutateGateParse
```
