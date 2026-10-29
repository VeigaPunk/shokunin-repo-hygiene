| counter mutant | change (old -> new) | stub-allpass | stub-sniff | landed-fixture | verdict |
|---|---|---|---|---|---|
| K1 kill-definition | `rc == 1 and failed > 0 and not crash` -> `rc != 0 and failed > 0 and not crash` | identical | identical | identical | BLIND |
| K2 kill-definition | `and failed > 0 and not crash` -> `and failed >= 0 and not crash` | identical | identical | identical | BLIND |
| K3 kill-definition | `and rc == 1 and failed > 0 and not crash` -> `and rc == 1 and failed > 0` | identical | identical | identical | BLIND |
| K4 kill-definition | `rc == 1 and failed > 0` -> `rc == 0 and failed > 0` | identical | killed:13->0; survived:0->13; equiv_killed:6->0 | killed:13->0; survived:0->13; exit 1 | DET-VISIBLE |
| K5 kill-definition | `and failed > 0 and not crash` -> `and failed > 1 and not crash` | identical | identical | killed:13->2; survived:0->11; exit 1 | DET-VISIBLE |
| K6 kill-definition | `cases is not None and rc == 1` -> `rc == 1` | (flake) old_killed:0->2 | identical | (flake) old_killed:0->1; exit 1 | NOISE-CONSISTENT |
| C1 equivalence-guard | `rc == 0 and failed == 0 and passed == cases and not crash` -> `rc != 1 and failed == 0 and passed == cases and not crash` | identical | (flake) old_killed:0->1 | identical | NOISE-CONSISTENT |
| C2 equivalence-guard | `passed == cases and not crash` -> `passed >= cases and not crash` | identical | (flake) old_killed:0->1 | identical | NOISE-CONSISTENT |
| C3 equivalence-guard | `failed == 0 and passed == cases` -> `failed <= 1 and passed == cases` | identical | (flake) old_killed:0->1 | (flake) old_killed:0->1; exit 1 | NOISE-CONSISTENT |
| C4 equivalence-guard | `failed == 0 and passed == cases and not crash` -> `failed == 0 and passed == cases` | (flake) old_killed:0->1 | (flake) old_killed:0->1 | (flake) old_killed:0->1; exit 1 | NOISE-CONSISTENT |
| C5 equivalence-guard | `cases is not None and rc == 0` -> `rc == 0` | identical | identical | (flake) old_killed:0->1; exit 1 | NOISE-CONSISTENT |
| T1 threshold | `and prior_ok == 8` -> `and prior_ok >= 6` | identical | identical | identical | BLIND |
| T2 threshold | `and killed_n == 13` -> `and killed_n >= 12` | (flake) old_killed:0->2 | (flake) old_killed:0->1 | (flake) old_killed:0->3; exit 1 | NOISE-CONSISTENT |
| T3 threshold | `and old_killed == 0` -> `and old_killed <= 1` | identical | identical | identical | BLIND |
| T4 threshold | `and len(EQUIV) == 6` -> `and len(EQUIV) >= 5` | identical | identical | identical | BLIND |
| T5 threshold | `len(MUTANTS) == 13` -> `len(MUTANTS) >= 12` | (flake) old_killed:0->1 | identical | identical | NOISE-CONSISTENT |
| A1 anchors-check | `anchors = "ok" if got == want else "FAIL"` -> `anchors = "ok" if got == want else "ok"` | identical | identical | (flake) old_killed:0->1; exit 1 | NOISE-CONSISTENT |
| A2 anchors-check | `if source.count(old) != 1:` -> `if source.count(old) != 1 and False:` | (flake) old_killed:0->1 | identical | identical | NOISE-CONSISTENT |
| A3 anchors-check | `got[f[0]] = f[2]` -> `got[f[0]] = f[1]` | anchors:ok->FAIL | anchors:ok->FAIL | anchors:ok->FAIL; (flake) old_killed:0->1; exit 1 | DET-VISIBLE |
| A4 anchors-check | `if n and len(f) >= 3:` -> `if n and len(f) >= 3 and f[0] != "B1":` | anchors:ok->FAIL | anchors:ok->FAIL | anchors:ok->FAIL; (flake) old_killed:0->1; exit 1 | DET-VISIBLE |
| P1 prior-leg | `, "tests/fixtures/r41-refusal-sites.py")` -> `)` | (flake) prior:8/8->7/8 | (flake) prior:8/8->7/8 | (flake) prior:8/8->7/8; exit 1 | NOISE-CONSISTENT |
| P2 prior-leg | `prior_ok = sum(1 for p in PRIOR if p in fixtures and clean(pre[p].result()))` -> `prior_ok = sum(1 for p in PRIOR if p in fixtures)` | (flake) old_killed:0->1 | identical | identical | NOISE-CONSISTENT |
| P3 prior-leg | `if args.survey or True:` -> `if args.survey:` | (flake) prior:8/8->7/8 | identical | identical | NOISE-CONSISTENT |
| P4 prior-leg | `old_killed += 1 if by else 0` -> `old_killed += 1` | old_killed:0->13 | old_killed:0->13 | old_killed:0->13; exit 1 | DET-VISIBLE |
| G1 pristine-minimum | `cand_pre[1] >= 13` -> `cand_pre[1] >= 1` | (flake) old_killed:0->1; (flake) prior:8/8->7/8 | (flake) old_killed:0->1 | identical | NOISE-CONSISTENT |
| G2 pristine-minimum | `cand_pre[1] >= 13` -> `cand_pre[1] >= 14` | pristine:ok->FAIL | pristine:ok->FAIL | pristine:ok->FAIL; exit 1 | DET-VISIBLE |
| S1 scratch-handling | `        shutil.rmtree(work, ignore_errors=True)` -> `        pass` | identical | (flake) old_killed:0->1 | identical | NOISE-CONSISTENT |
| S2 scratch-handling | `        e["TMPDIR"] = work` -> `        e["TMPDIR"] = scratch` | identical | (flake) old_killed:0->2 | identical | NOISE-CONSISTENT |
| S3 scratch-handling | `        shutil.rmtree(scratch, ignore_errors=True)` -> `        pass` | (flake) prior:8/8->7/8 | identical | identical | NOISE-CONSISTENT |
| S4 scratch-handling | `scratch = tempfile.mkdtemp(prefix="souji-r42-c3.", dir=scratch_root)` -> `scratch = tempfile.mkdtemp(prefix="souji-r42-c3.", dir=None)` | identical | identical | (flake) old_killed:0->1; exit 1 | NOISE-CONSISTENT |
| M1 reporting | `len(MUTANTS), killed_n, len(MUTANTS) - killed_n,` -> `len(MUTANTS) - 1, killed_n, len(MUTANTS) - killed_n,` | mutants:13->12 | mutants:13->12 | mutants:13->12; (flake) old_killed:0->1; exit 1 | DET-VISIBLE |
| M2 reporting | `equiv_killed += 1 if cand else 0` -> `equiv_killed += 1` | equiv_killed:0->6 | (flake) old_killed:0->1 | equiv_killed:0->6; (flake) old_killed:0->1; exit 1 | DET-VISIBLE |
| M3 reporting | `for mid, _d, _o, _n in EQUIV:` -> `for mid, _d, _o, _n in MUTANTS:` | (flake) prior:8/8->7/8 | equiv_killed:6->13 | equiv_killed:0->13; exit 1 | DET-VISIBLE |
