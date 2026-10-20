# W2 · RevMatrixRunnerFinal — `census/round-16/run-matrix.py` validation / `invalid_suites`

Item: **source-only** review of the validity gate of the C1 counting command.
Lane HEAD: `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`.
Reviewed bytes: `census/round-16/run-matrix.py` sha256 `2815712bbb0da37c213ed31391497efed2f2443e8a2818131aa1be4968e813c9`
= git blob `b1c1b688b7b48077171cab23a00a0548b74562d6` = `HEAD:census/round-16/run-matrix.py`;
`git diff --stat HEAD` over the runner and both fixtures is empty (clean at HEAD).
No execution of the runner, the census tool, or either fixture (source-only item, no `ALLOWED-EXEC`).

## Verdict

The gate is sound against the failure modes it names (missing/truncated SUMMARY, duplicated
CASE ids, verdict/SUMMARY disagreement, timeout, fixture usage error), and it is *sound for
the two authoritative records already in the tree*. It has one genuine false-green path
(F1), one provenance field that is recorded but never gates (F2), one misclassification
(F3), and one stale sibling record with an incompatible schema (F4). **None of the four
changes any landed result.**

| # | Severity | Target | Verdict |
|---|---|---|---|
| F1 | Medium | `run-matrix.py:57-60` — `valid` accepts `rc=1` with `failed=0` | **fails** (false green) |
| F2 | Low-Medium | `run-matrix.py:83-86,131-133` — `fixtures_dirty` never gates | **partial** |
| F3 | Low | `run-matrix.py:57-60,131-138` vs fixture `id-set` row | **partial** (misclassification) |
| F4 | Low | `census/round-16/c1-matrix.json` — pre-gate schema in the admission dir | **fails** (consumer KeyError) |

---

## F1 — Medium — `valid` cannot distinguish "evaluated and green" from "crashed after SUMMARY"

`census/round-16/run-matrix.py:57-60`:

```python
    valid = (rc in (0, 1) and isinstance(total, int) and total > 0
             and isinstance(failed, int) and 0 <= failed <= total
             and len(cases) == total
             and sum(c["verdict"] == "FAIL" for c in cases.values()) == failed)
```

`rc in (0, 1)` treats exit 1 as *evidence of measurement*, but 1 is simultaneously
(a) the fixtures' "cases failed" signal and (b) CPython's uncaught-exception exit. The
predicate never ties `rc` to `failed`, although both fixtures define exactly that contract:
`return 0 if failed == 0 else 1` (`tests/fixtures/r15-census-config.py:1567`,
`tests/fixtures/r14-census-boundary.py:729`).

**Counterexample (constructed from the two sources, not executed).** `suite()` receives
`rc=1` and stdout containing 20 `CASE\tR15CFG-nn\tPASS\t…` lines plus
`SUMMARY\ttotal=20\tfailed=0`. Then `total=20, failed=0, len(cases)=20`, FAIL tally `0`:
every clause is satisfied → `valid=True`. That stdout is exactly what the r15 fixture emits
on a clean run, because `SUMMARY` is printed at **line 1546 while the process is still inside
the `try`**, and teardown runs in the `finally` at **1568-1569**:

```
1567         return 0 if failed == 0 else 1
1568     finally:
1569         cleanup()
```

and `cleanup()` deliberately makes teardown loud — `tests/fixtures/r15-census-config.py:1430`:

```
1430         shutil.rmtree(SCRATCH, ignore_errors=False)
```

(r14's counterpart at 645-654 uses `ignore_errors=True`, so this is r15-only by design.)
Any `OSError` from that `rmtree` (EACCES on a case-created path, ENOTEMPTY race, read-only
`/var/tmp`) raises **after** the last CASE and SUMMARY lines → traceback → `rc=1`,
`failed=0`. `suite()` then records `valid: True`, `failed: 0`, and puts the traceback in
`stderr_tail` (line 62) — a field **nothing ever reads** (`grep -n stderr_tail` returns only
line 62 itself). `main()` prints `changed … r15=20/0fail`, writes `invalid_suites: []`, and
returns 0. The matrix reports a fully green arm whose fixture crashed during teardown.

The mirror case (`rc=0` with `failed>0`) is admitted by the same gap; it is unreachable with
the current fixtures but becomes reachable with any fixture whose exit code is not derived
from `failed`.

**Smallest fix** — add the contract clause (reorder for readability; semantics identical
when `failed is None` because the None guard still runs):

```python
    valid = (isinstance(total, int) and total > 0
             and isinstance(failed, int) and 0 <= failed <= total
             and rc == (1 if failed else 0)
             and len(cases) == total
             and sum(c["verdict"] == "FAIL" for c in cases.values()) == failed)
```

Optional second guard, independent of exit-code semantics: `and not err.strip()`. Both
fixtures write to stderr only through `die()` (`r15:264`, `r14:120`), so this holds today;
it makes a crashed teardown invalid even if a future fixture exits 0 on teardown failure.
It is stricter than the current fixture contract, so gate it as a policy choice.

**No landed value changes.** Machine-checked over all three records (24 suite rows): every
row satisfies `rc == (1 if failed else 0)`, and no row contains an `id-set` case.
`c1-matrix-final.json` — changed r15 `0/0`, r14 `0/0`; pre-harm `1/8`, `1/10`; r14-harm
`1/16`, `0/0`; r15-baseline `1/20`, `1/12`; `c1-matrix-landing.json` identical. All
`valid: true` stay `true`.

## F2 — Low-Medium — `fixtures_dirty` is recorded but never gates validity

`run-matrix.py:83-86` computes the fixture digests and the dirty string, and `131-133`
builds `invalid` from the two suite verdicts only:

```python
131     invalid = [f"{a}:{k}" for a, arm in record["arms"].items()
132                for k in ("r15-config", "r14-namespace") if not arm[k]["valid"]]
```

So a run against a **modified** fixture still exits 0 with `invalid_suites: []`; the only
trace is a free-text field (`"fixtures_dirty": " M tests/fixtures/r15-census-config.py"`)
that nothing compares to a pin. The C1 claim is a *cross-arm comparison over one fixture
byte-identity*, so fixture drift silently breaks the comparison while the gate says green.

Honest scope: the overall admission path is not open — `tools/souji-preservation-evidence.py`
pins the fixture paths and digests independently (`NAMESPACE_SHA256` at 307-311;
`expected.json` `files` pins at 186-192) — but `run-matrix.py` is the only producer of
`invalid_suites`, and it does not use the provenance it already computes.

**Smallest fix** (3 lines moved + 2 added):

```python
    fixture_paths = [str(v.relative_to(LANE)) for v in fixtures.values()]
    fixtures_dirty = git("status", "--porcelain", "--", *fixture_paths).strip()
    record = { … "fixtures_dirty": fixtures_dirty, … }
    …
    if fixtures_dirty:
        invalid.append("fixtures:dirty")
```

**No landed value changes:** `fixtures_dirty` is `''` in both `c1-matrix-final.json` and
`c1-matrix-landing.json`.

## F3 — Low — the fixture's `id-set` row increments `failed` without incrementing `total`

Both fixtures emit a synthetic integrity row when the case universe drifts, and count it as
a failure while still reporting `total=len(ran)`:

`tests/fixtures/r15-census-config.py:1540-1546` (same at `r14-census-boundary.py:722-728`):

```
1540         if not args.case and tuple(ran) != EXPECTED_IDS:
1541             failed += 1
1542             print(
1543                 "CASE\tid-set\tFAIL\t"
…
1546         print(f"SUMMARY\ttotal={len(ran)}\tfailed={failed}")
```

Consequence in `run-matrix.py`: emitted rows `= total + 1`, so `len(cases) == total` (line
59) fails → `valid: false` → `invalid_suites: ["<arm>:<suite>"]` → exit 2 with the message
`could not evaluate suites` (line 138). Two problems:

1. **Classification:** the run *was* evaluated and the fixture *refused its own case set*;
   reporting it as "could not evaluate" hides the actionable fact (case-universe drift,
   i.e. exactly the R16-M3 class of defect).
2. **Latent inconsistency:** the record carries `failed` one greater than the number of
   FAIL rows in `cases`, so the two halves of the record disagree; only the `len` clause
   catches it. A future edit that normalizes the row count without normalizing the tally
   would silently admit it.

**Smallest fix** (normalize the synthetic row, 1 line + 1 clause):

```python
    synthetic = 1 if "id-set" in cases else 0
    …
             and len(cases) - synthetic == total
```

Then an id-set drift is a *valid* suite with `failed=1` → a red arm with the honest
`id-set` detail, gate still exits 0 (arms were evaluated). If L1 prefers "id-set drift is
not evaluable", keep the predicate and reword line 138 to `suite refused/failed
structurally: {invalid}` — but the record must not claim "could not evaluate".

**No landed value changes:** no record contains an `id-set` case (checked in all three JSONs).

## F4 — Low — a pre-gate matrix record with an incompatible schema sits in the same directory

`census/round-16/` holds three matrices. `c1-matrix-final.json` (11:43) and
`c1-matrix-landing.json` (11:58) are the cited records (`LOG.md:860-861`) and carry
`runner_sha256 = 2815712b…` — i.e. the reviewed bytes. The third,
`census/round-16/c1-matrix.json` (11:16), is from the pre-gate runner:

- lane_head `cbf688ab2ab2` (neither `0a70bef` nor the landing `7a79dc2`);
- **no** `invalid_suites` key, **no** `runner_sha256` key;
- observed consequence: `json.load(open('census/round-16/c1-matrix.json'))["invalid_suites"]`
  raises `KeyError: 'invalid_suites'` (executed, see Commands).

A consumer that iterates `census/round-16/*matrix*.json` and indexes the gate result
crashes on the stale file; a consumer that uses `.get()` silently accepts a record produced
before the gate existed.

**Smallest fix:** add one line to the record dict (`run-matrix.py:80-93`),
`"record_schema": 2,` so consumers can refuse pre-gate records explicitly; and L1 should
delete or regenerate `c1-matrix.json` (artifact hygiene — it is not cited anywhere:
`grep -n c1-matrix LOG.md corpus/lessons/round-16.md .ufo/waves/round-16/w2-*.json` names
only `-final` and `-landing`).

---

## What holds (no action)

Confirmed by construction from the source, not by execution:

- **Missing or truncated SUMMARY** → `total is None` → `isinstance` guard false → invalid (57-58).
- **Timeout** → `run()` returns `rc=124` (38-42) → invalid (57).
- **Fixture usage/preflight failure** → `die()` → `SystemExit(2)` (`r15:263-265`, `r14:120`) → invalid (57).
- **Duplicate CASE ids** → dict overwrite at 53 → `len(cases) < total` → invalid (59).
- **Verdict/SUMMARY disagreement** → tally check at 60.
- **Empty suite** → `total > 0` (57).
- **id-set drift** → caught via 59 (mislabeled, F3).
- **Coverage of the gate itself**: `invalid` is computed over *both* suite keys for *every*
  arm, including `changed` (131-132); non-empty → exit 2 (137-139); the record is still
  written first (136), so an invalid run is debuggable rather than lost.
- **Provenance is adequate for the landed claim**: `lane_head`, per-arm resolved `rev` and
  `sha256`, `fixtures_sha256`, `runner_sha256`, git/bash/shellcheck/python versions
  (80-93); `runner_sha256` matches `HEAD` bytes in both cited records, and `git diff --stat
  HEAD` over runner + fixtures is empty.
- **No cross-arm masking**: totals are identical per suite across all arms (r15=20, r14=12
  in both cited records), so the "changed 20/20, r14 12/12; harm red 8/16/20 and 10/12/12"
  reading is internally consistent with the fixture's own id-set guard being intact
  (`r15:1540`, `r14:722`).

## Nits (no patch requested)

- `run-matrix.py:38-42` — `run()` does not catch `OSError`; a missing interpreter or fixture
  raises out of `main()`, producing exit 1 (undocumented; the runner otherwise uses 0/2) and
  no record. Conservative in effect (nonzero), but the failure is a traceback, not a verdict.
- `run-matrix.py:131` — loop variable `a` shadows the argparse namespace `a` (66). Harmless
  today because `a` is not read after line 82, but it is a trap for the next edit.
- `run-matrix.py:91` — `runner_sha256` hashes the *working-tree* file, so a dirty runner is
  recorded rather than refused. The sha is self-identifying (as F4 shows), so this is
  adequate; only noting that it is provenance, not a gate.

## Residual risk / verification gaps

- **No execution.** This seat had no `ALLOWED-EXEC`; F1's counterexample is derived from
  `run-matrix.py:57-60` plus the fixture's print/teardown order (`1546` → `1568-1569` →
  `1430`), not observed. Empirically confirming it needs a mutated fixture copy that raises
  after `SUMMARY` — a copy-only mutation test under `/var/tmp`.
- **No LSP.** No `lsp` device is mounted for this seat, so caller/definition checks were done
  by exact-file reads and named-path greps. `stderr_tail`'s zero-consumer status and the
  absence of any reader of `invalid_suites` were established by `grep` on the three named
  files (`run-matrix.py`, `souji-preservation-evidence.py`, `souji-landing-gate.py`,
  `souji-seat-audit.py`), not by semantic references — recorded as such.
- **Severity of F1 is conditional on environmental failure** (teardown `OSError`), not on a
  deterministic fixture path. It is a false-green *in the gate*, not a false green in the
  landed evidence: no current record is affected.

STATUS: PARTIAL — gate holds for every truncation/duplication/tally case and for all landed records, but `rc in (0, 1)` admits a post-SUMMARY crash as `valid` (run-matrix.py:57), `fixtures_dirty` never gates (83-86 vs 131-133), the fixture `id-set` row is misreported as "could not evaluate", and `c1-matrix.json` carries the pre-gate schema.

## Commands

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git status --porcelain=v1 | head -20 && wc -l census/round-16/run-matrix.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la census/round-16/ && python3 -m json.tool census/round-16/c1-matrix-final.json 2>/dev/null | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py && grep -n "print(\|sys.exit\|return 1\|return 0\|SUMMARY\|CASE" tests/fixtures/r15-census-config.py | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "print(\|sys.exit\|SUMMARY\|CASE" tests/fixtures/r14-census-boundary.py | head -40 && echo --- && python3 - <<'EOF'
import json
d=json.load(open('census/round-16/c1-matrix-final.json'))
print("invalid_suites:", d.get("invalid_suites"))
for arm,v in d["arms"].items():
    print(arm, v["rev"][:12], {k:(v[k]["total"],v[k]["failed"],v[k]["valid"],len(v[k]["cases"])) for k in ("r15-config","r14-namespace")}, "selftest", v["selftest"])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
for f in ("census/round-16/c1-matrix-final.json","census/round-16/c1-matrix-landing.json","census/round-16/c1-matrix.json"):
    d=json.load(open(f))
    print("==",f)
    print(" lane_head",d["lane_head"][:12],"changed",d["changed"],"| fixtures_dirty=",repr(d["fixtures_dirty"]),"| invalid_suites=",d["invalid_suites"])
    for arm,v in d["arms"].items():
        print("  ",arm,v["rev"][:12],"bash_n",v["bash_n"]["rc"],"sc",v["shellcheck_warning"]["rc"],
              "| r15 rc=%s tot=%s fail=%s val=%s"%(v["r15-config"]["rc"],v["r15-config"]["total"],v["r15-config"]["failed"],v["r15-config"]["valid"]),
              "| r14 rc=%s tot=%s fail=%s val=%s"%(v["r14-namespace"]["rc"],v["r14-namespace"]["total"],v["r14-namespace"]["failed"],v["r14-namespace"]["valid"]))
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "def cleanup\|def die" -A 14 tests/fixtures/r15-census-config.py | sed -n '1,40p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1495,1525p' tests/fixtures/r15-census-config.py | cat -A | sed -n '1,31p' | cut -c1-160
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "--- run-matrix anchors"; grep -n "rc in (0, 1)\|fixtures_dirty\|invalid = \|invalid_suites\|len(cases) == total\|isinstance(total" census/round-16/run-matrix.py; echo "--- r15 chmod/000 anchors"; grep -n "0o000\|chmod(.*0o700\|ignore_errors" tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum census/round-16/run-matrix.py tools/souji-census.sh && git hash-object census/round-16/run-matrix.py && echo "--- git HEAD blob" && git rev-parse HEAD:census/round-16/run-matrix.py 2>/dev/null || echo "NOT IN HEAD" && echo "--- recorded runner_sha256" && python3 - <<'EOF'
import json
for f in ("census/round-16/c1-matrix-final.json","census/round-16/c1-matrix-landing.json","census/round-16/c1-matrix.json"):
    d=json.load(open(f))
    print(f, "runner", d.get("runner_sha256"), "lane", d["lane_head"][:12], "keys", "invalid_suites" in d, "fixtures_dirty", repr(d.get("fixtures_dirty")))
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '700,735p' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "--- stderr_tail uses"; grep -n "stderr_tail" census/round-16/run-matrix.py; echo "--- consumers of matrix/invalid_suites in named files"; grep -n "invalid_suites\|run-matrix\|c1-matrix" tools/souji-landing-gate.py tools/souji-preservation-evidence.py tools/souji-seat-audit.py 2>/dev/null || echo "none"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -3 -- census/round-16/run-matrix.py && git log -1 --format=%H%n%ad -- census/round-16/run-matrix.py && git diff --stat HEAD -- census/round-16/run-matrix.py tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py && echo "clean-if-empty"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '300,350p' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "c1-matrix\|matrix" tools/souji-preservation-evidence.py | head -20; echo "--- fixture pins"; grep -n "sha256\|PIN\|pin" tools/souji-preservation-evidence.py | head -25
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=45&&NR<=66{printf "%4d %s\n",NR,$0}' census/round-16/run-matrix.py; echo "..."; awk 'NR>=72&&NR<=96{printf "%4d %s\n",NR,$0}' census/round-16/run-matrix.py; echo "..."; awk 'NR>=124&&NR<=139{printf "%4d %s\n",NR,$0}' census/round-16/run-matrix.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls .ufo/waves/round-16/w2/ 2>/dev/null | head -30; echo "---"; awk 'NR>=1418&&NR<=1432{printf "%4d %s\n",NR,$0}' tests/fixtures/r15-census-config.py; echo "---"; awk 'NR>=1538&&NR<=1570{printf "%4d %s\n",NR,$0}' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "c1-matrix" LOG.md corpus/lessons/round-16.md .ufo/waves/round-16/w2-spec.json .ufo/waves/round-16/w2-dispatch.json 2>/dev/null | cut -c1-220
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=725&&NR<=735{printf "%4d %s\n",NR,$0}' tests/fixtures/r14-census-boundary.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "tuple(ran) != EXPECTED_IDS" tests/fixtures/r14-census-boundary.py tests/fixtures/r15-census-config.py && grep -n "def cleanup" -A 8 tests/fixtures/r14-census-boundary.py | head -12
```

File reads used the `read` tool on the exact named paths
`census/round-16/run-matrix.py`, `tests/fixtures/r15-census-config.py`,
`tests/fixtures/r14-census-boundary.py` only. No installer or update was run.
