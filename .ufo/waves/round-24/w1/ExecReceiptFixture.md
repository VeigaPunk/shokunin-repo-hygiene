# ExecReceiptFixture — r24 w1, C3 fixture draft

## Status
STATUS: PASS — fixture draft written; the current runner scores the frozen control `refusals=0/2` (exit 1), and a scratch-patched correct runner scores `cases=8 pass=8 refusals=2/2 regress=5/5` (exit 0).

## Evidence
Delivery: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-24/w1/r24-receipt-verify.py`. The first draft's sha256 was `531e924883de9d0df264337a522b96f7f63ae1478191c377954dabc3753f6c4a`; the current version is `f8c4c391…08b2` (see the Amendment section). The L1 copies it to `tests/fixtures/r24-receipt-verify.py`.
Lane HEAD `f9db2181647d91470a724a12d626bd6106805076`; runner `tools/souji-receipt-run.py` sha256 `e13d0c8352c9fbaa95c4dc2560b85d4aa9125c332a4e9240a5c0bc6e96f1121d`; git 2.56.0.

Contract quotes:
- preregistration.txt:100 — "Counter (frozen): python3 -B tests/fixtures/r24-receipt-verify.py --tool tools/souji-receipt-run.py"
- preregistration.txt:111 — "Before (control): the base runner -> refusals=0/2. After target: refusals=2/2 regress=5/5, exit 0."
- tools/souji-receipt-run.py:279 — `if not COUNTS_RE.search(header["_body"]):` (this is why the synthetic counter prints `assertions=4 resolved=3 skipped=1 mismatches=0`).

**Control run** against the current lane runner, from the lane root:
`python3 -B .ufo/waves/round-24/w1/r24-receipt-verify.py --tool tools/souji-receipt-run.py`
```
tool=/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-receipt-run.py lane_root=/home/vgpnk/Projects/shokunin/souji-shokunin
case=c verdict=PASS expect=<run at a durable rev writes a receipt; verify rc=0 verify=ok> got=<run rc=0; verify rc=0 out=verify=ok rev=5172fb56ba6f52af12d2127784c161e3fc140045 tool=tools/tiny-counter.py tool_sha256=2e18f2698c9f78ed0d769a8df4fad54b8437865686e...>
case=a verdict=FAIL expect=<rev -> commit-tree object in no ref, same tool bytes: verify rc=2 RECEIPT-REV-NOT-DURABLE> got=<rev=d6cba5084d7f refs_containing=0 digest_equal=True verify rc=0 out=verify=ok rev=d6cba5084d7ff5821fae564f1d81a70b495098be tool=tools/tiny-counter.py tool_sha256=2e18f2698c9f78ed0d769a8df4fad54b8437865686e...; run_same_rev rc=2>
case=b verdict=FAIL expect=<tool= with its true digest at rev, not an argv element of cmd=: verify rc=2 RECEIPT-TOOL-NOT-IN-ARGV (absent path and substring-only path)> got=<absent(tool=tools/other-counter.py) rc=0 out=verify=ok ...; substring(tool=counter.py) rc=0 out=verify=ok ...>
case=d-declared-evidence-after verdict=PASS ... got=<rc=0 out=verify=ok rev=9301d98c1c689c79741f0f1ba1f171138d20af07 ...>
case=d-gate-check-at-first-landing verdict=PASS ... got=<rc=0 out=verify=ok rev=a211e4d1bf6ea592670d16269f34e9f67f33e8b3 ...>
case=d-gate-check-at-lane-base verdict=PASS ... got=<rc=0 out=verify=ok rev=1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd ...>
case=d-gate-check-c3 verdict=PASS ... got=<rc=0 out=verify=ok rev=476525026cdb179f2d49441e1cb6c6f7316f3124 ...>
case=d-agreement-after verdict=PASS ... got=<rc=0 out=verify=ok rev=eb1aa49783ae4a0d42e062aa5a61e49a91b0f76a ...>
cases=8 pass=6 refusals=0/2 regress=5/5
exit=1
```

**Falsification runs.** These used runner copies under `/var/tmp/souji-r24-ExecReceiptFixture/` (now removed). Lane files were not edited.

| runner variant | last line | exit |
|---|---|---|
| `fixed`: verify adds `durable_rev` → `RECEIPT-REV-NOT-DURABLE` and `tool not in shlex.split(cmd)` → `RECEIPT-TOOL-NOT-IN-ARGV` | `cases=8 pass=8 refusals=2/2 regress=5/5` | 0 |
| `substr` mutant: same, but `tool not in header["cmd"]` (substring) | `cases=8 pass=7 refusals=1/2 regress=5/5` (case b substring instance `rc=0 verify=ok`) | 1 |
| `fixed`, no `--lane-root`, tool outside any git repo | `cases=8 pass=3 refusals=2/2 regress=0/5` (`lane-root absent (unresolved)`) | 1 |
| `fixed`, `--lane-root` pointing at a missing path | `cases=8 pass=3 refusals=2/2 regress=0/5` | 1 |
| `--tool` absent | `cases=8 pass=0 refusals=0/2 regress=0/5` | 1 |
| `fixed`, inside a runner-shaped clone (`--no-local --no-checkout`, sparse `!/census/operator-sweep-*`, detached at f9db218), default lane root | `cases=8 pass=8 refusals=2/2 regress=5/5` | 0 |
| current runner, same clone | `cases=8 pass=6 refusals=0/2 regress=5/5` | 1 |

Residue check after every run: no `/var/tmp/souji-r24-receipt-verify-*` and no `/var/tmp/souji-receipt-*` remained. No `__pycache__` was created in the lane.

## Findings
1. **Fixture design** (`r24-receipt-verify.py`):
   - All synthetic writes go to one scratch git repo, `/var/tmp/souji-r24-receipt-verify-*`. It uses isolated git config (`GIT_CONFIG_GLOBAL=/dev/null`, `NOSYSTEM`, hooksPath set to an empty directory) and is trap-cleaned on atexit, SIGINT, SIGTERM and SIGHUP.
   - The lane root is only read, through the runner's own `verify` (cat-file and for-each-ref).
   - Case order is c → a → b → d. Cases a and b doctor the clean receipt from c, so if c fails, a and b are scored FAIL rather than crashing.
   - Any exception is scored as FAIL.
2. **Case a preconditions** are asserted before scoring, so a refusal for some other reason cannot count as case a:
   - `for-each-ref --contains <dangling>` over all refs is empty.
   - The dangling commit differs from the receipt's original rev.
   - The tool blob's sha256 at the dangling commit equals the one at the durable rev.
   - The pass test is `rc == 2`, the literal code on stderr, and no `verify=ok` on stdout.
3. **Symmetry witness (current runner).** On the same non-durable rev, `verify` accepts (`rc=0 verify=ok`) while `run` refuses (`run_same_rev rc=2`). This is the asymmetry r23 disclosed, reproduced here. It is reported in case a's `got=` field but not scored.
4. **ATTACK on case b instance choice.** A single "path absent from cmd" receipt would let a substring check (`tool in cmd_string`) reach `refusals=2/2`; the `substr` mutant demonstrates this.
   - I therefore score case b on two instances that must both refuse:
     - `tools/other-counter.py`, which does not appear in cmd at all;
     - `counter.py`, which is a committed file at the repo root and a substring and suffix of the argv element `tools/tiny-counter.py`, but not itself an element.
   - Both carry the tool's true digest at the rev, so tool label vs argv is the only defect.
   - This stays inside the frozen predicate ("does not occur as an argv element"); it does not change it. The L1 may drop the substring instance if it judges otherwise.
5. **Default lane root.** `--lane-root` defaults to `git rev-parse --show-toplevel` of the directory containing `--tool`.
   - Under the receipt runner this resolves to the runner's private clone. There, durability of the r23 revs comes from `refs/remotes/origin/*`; the runner-shaped clone emulation passes 5/5.
   - An unresolvable or missing lane root scores FAIL for each of the five d cases, never a skip.
6. **Regression risk for C3's fix.** All five r23 receipt revs pass a durability-checking `verify` against the lane at f9db218 (`fixed` row). [INFERENCE] The kill rule fires only if a fix checks something stricter than refs/heads, tags and remotes.
7. **Stream binding.** Refusal codes must appear on stderr, which matches the runner's `refuse()` convention (tools/souji-receipt-run.py:121-123). A fix that printed codes to stdout would score FAIL.
8. **Lane observation.** An untracked `census/round-24/` directory appeared in the lane during this run. The fixture writes nothing in the lane. [INFERENCE] Another seat created it.
9. **Tooling note.** The Read tool refused `tools/souji-receipt-run.py` and `tests/fixtures/r23-receipt-run.py` with a spurious "exceeds 100000 characters" error (the files are 12950 and 21836 bytes). I read the runner in pages and the r23 fixture with `sed -n`. No tools were installed or upgraded.

## Amendment (L1 pre-data, 2026-10-25 09:28 UTC)
The L1 asked for a second instance in case a. The fixture was edited in place; total cases stay at 8 and the last-line format is unchanged.
- The new instance is a `commit-tree` commit held only by `refs/jj/keep/r24-fixture`, created with `git update-ref` inside the scratch repo.
- The precondition requires `for-each-ref --contains` to list exactly that one ref.
- Case a passes only if both instances refuse with `RECEIPT-REV-NOT-DURABLE`.

Fixture sha256 after the amendment: `f8c4c391097ee9745b72cbf5eef51aec235a89946c22831d10a1db7badc708b2`.

| runner | sha256 | last line | exit |
|---|---|---|---|
| lane `tools/souji-receipt-run.py` (working tree, read-only) | `9df0738cdfd969fc0c75ea858f5c2392d34dbf4bb78911916637e146850d82ff` | `cases=8 pass=8 refusals=2/2 regress=5/5` | 0 |
| base `master:tools/souji-receipt-run.py` (f9db218) | `e13d0c8352c9fbaa95c4dc2560b85d4aa9125c332a4e9240a5c0bc6e96f1121d` | `cases=8 pass=6 refusals=0/2 regress=5/5` | 1 |
| mutant: lane runner, `durable_rev` counting every ref | — | `cases=8 pass=7 refusals=1/2 regress=5/5` (jj-keep-only `verify rc=0`) | 1 |

- On the lane runner, case a shows both instances refused (`verify rc=2 out=RECEIPT-REV-NOT-DURABLE`).
- On the base runner, both instances return `verify rc=0 verify=ok`. The same no-ref rev gets `run_same_rev rc=2`.
- The mutant shows the jj instance is needed: a durability check that counts any ref passes the no-ref instance but not the jj-keep one.
- Scratch `/var/tmp/souji-r24-ExecReceiptFixture/` was removed. There is no residue in `/var/tmp`.

## Attack log
- **A4 (refs/jj durability leak):** a verifier that counts any ref as durable would pass a single no-ref instance. The jj-keep-only instance catches it (`refusals=1/2`, exit 1).
- **A1 (case b gameability):** a substring check scores a false 2/2 against a single-instance case b. The substring instance closes this, and the `substr` mutant is caught (`refusals=1/2`, exit 1).
- **A2 (skip-to-green on case d):** an absent lane root, missing path or missing receipt is scored FAIL. Witnessed `regress=0/5`, exit 1.
- **A3 (vacuous pass with an absent tool):** all 8 cases FAIL. Witnessed `pass=0`, exit 1.
