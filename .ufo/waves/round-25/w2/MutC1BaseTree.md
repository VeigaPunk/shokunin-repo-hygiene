# MutC1BaseTree — C1 base/tree mutation probe

STATUS: PASS

Axes: calibration, operability, coverage. This bounded probe targets calibration/coverage of C1's kill-rule cases.

## Evidence

- Frozen definition: `preregistration-amendment-3.txt:5-16` adds k5 partial-removal, k6 extra-ground-allowed, k7 control, and pins `kill_tested` to base-grounded entries and `kill_violations` to entries with ≥1 violation.
- Fixture source: `tests/fixtures/r25-coverage-agreement.py:329-410` implements k1-k7. Current kill-rule in `tools/souji-coverage-agreement.py:115-132` gathers base grounds and flags any missing base ground while comparing name/type in the current revision tree.
- Pristine command (lane cwd): `python3 -B tests/fixtures/r25-coverage-agreement.py --tool tools/souji-coverage-agreement.py`.
- Actual pristine result: all 16 cases passed; `cases=16 pass=16 control=FALSE-GREEN-REJECTED`; exit 0. k1 deleted, k2 regrounded, k3 clean, k4 multi-ground retained, k5 partial-removal, k6 extra-ground allowed, and k7 control all passed.
- Requested synthetic semantics are pinned by this fixture: multi-ground F2+F3 retained (k4), losing one ground fails (k5), same-name ground reappears at HEAD but is absent/re-grounded at `--rev` so base/tree revision is what is checked (k1/k2/k5), and extra ground is accepted (k6). The type-change case is not separately represented: k1 exercises absence, but no case replaces the same-named knowledge path with a non-blob tree entry. Re-grounding is pinned by k2. Thus same-name changed-type remains uncovered by an explicit synthetic case.
- k5 mutant: in isolated tool copy, changed `elif not base_ks <= got:` to `elif base_ks.isdisjoint(got):` (only reports violation when none of the prior grounds survive). Re-ran the same bounded fixture; k5 failed with `kill_tested=1 kill_violations=0 rows=[none] exit=0`; overall `cases=16 pass=15 control=FALSE-GREEN-REJECTED`, exit 1. Verdict: mutant killed. k6 still passed, showing that extra grounds remain allowed under the mutant.
- Before restoration, pristine tool SHA-256: `bb506469be860f994f74f4c7d6eb1c949a4931b676cdb60f9f79de041d12f27f`. Restored scratch tool SHA-256 was identical; scratch directory `/var/tmp/souji-r25-MutC1BaseTree/` was removed.

## Findings

1. k5 is an effective detector for the specific per-entry/all-prior-grounds-lost mutant: it rejects the mutant where a partial loss is ignored. This falsifies the hypothesis that the per-F violation defect survives.
2. The explicit same-name/non-blob replacement behavior is not isolated as a fixture case. Current code checks `kind != "blob"` (`tools/souji-coverage-agreement.py:125`), but no separate case pins that branch. Attack coverage gap only; no contract change proposed.

## Attack log

1. Read frozen preregistration and amendments 1–3, fixture case definitions, and current kill-rule implementation.
2. Ran pristine fixture: 16/16 cases, control rejected.
3. Mutated only the comparison in an isolated scratch copy; ran the same fixture; k5 killed mutant, 15/16 overall.
4. Restored exact tool bytes (matching SHA-256), removed scratch.
