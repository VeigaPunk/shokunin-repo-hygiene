# MutC3Vacuity — mutation-test of the C3 7-case structure fixture (souji r25 w2)

Seat: L1Souji25.MutC3Vacuity (mutation-tester, leaf). Lane repo:
/home/vgpnk/Projects/shokunin/souji-shokunin. Host git 2.56.0 (git version 2.56.0).
Scratch `/var/tmp/souji-r25-MutC3Vacuity/` only; removed before finish. No tool
installs. No lane/sibling/fleet writes outside this report.

## Target and bounded detector

Frozen counter (preregistration C3): `bash tests/fixtures/r13-repo-structure.sh
--selftest --probe tools/souji-repo-structure.sh`. Detector oracle used for every
run: fixture exit code + final stdout line `selftest=PASS ids=7/7`. The fixture
bytes mutation-tested are the W1-integrated draft currently in the lane tree
(`tests/fixtures/r13-repo-structure.sh`, sha256 `eabc5f0ac56ea3db9f6f68d2dfeadbc91f592eb68c3691d2eabbd5b8347e2c13`; git blob c369546e) and the committed probe
(`tools/souji-repo-structure.sh`, sha256 `80025137b20d5a6143db0120057552bd239fb60de1a504ede69896baade5aec2`; blob 0f42ebf).

## Pristine re-run (before data)

`bash fixture.sh --selftest --probe $SCRATCH/probe.sh` (absolute probe; a relative
bare probe name fails exec under the fixture's `env -i` allowlist — `timeout: failed
to run command 'probe.sh': No such file or directory`, rc=127 everywhere; all verdict
runs below therefore use absolute probe paths):
- run 1: `selftest=PASS ids=7/7`, rc 0
- run 2 (direct rc check): `selftest=PASS ids=7/7`, rc 0
All 7 ids PASS; linked case `checks=8 control=PASS`; colocated case
`others_plain=0 others_colocated=2 commits_plain=1 commits_colocated=2 differing_keys=8`.

## Mutant results (13 mutants; 8 killed, 5 survived)

Probe mutants (P): pristine fixture + mutant probe. Fixture mutants (F): mutant
fixture + pristine probe. All runs used absolute probe paths.

| # | mutant | behavior injected | detector output | verdict |
|---|---|---|---|---|
| P1 | wrong common dir | linked worktree: print `probe.git_common_dir=<private gitdir>` (swap with git_dir) | rc 1, `selftest=FAIL ids=7/7`; linked case `probe.git_common_dir=<…/worktrees/linked-tree> want=<…/linked-main/.git>`; `probe.git_dir==probe.git_common_dir` | **KILLED** |
| P2 | common-dir write | linked: append to `$common/description` during probe | rc 1, FAIL; linked case `common-dir-manifest-delta` | **KILLED** |
| P3 | private-dir write | linked: append to `$private/gitdir` during probe | rc 1, FAIL; linked case `common-dir-manifest-delta; private-gitdir-manifest-delta` (the private gitdir file is under `worktrees/<id>/`, so it also appears in the common-dir manifest) | **KILLED** |
| P4 | zero references.others.count | rewrite `references.others.count=0` on stdout | rc 1, FAIL; colocated case `others.count colocated=0 not> plain=0` | **KILLED** |
| P5 | always-PASS/noop emitter | `exit 0`, no output | rc 1, FAIL; object-metrics (all probe/reference keys empty), bogus-repo (plain-dir-accepted, rc=0 want=2), promisor-refusal (markers missing), linked, colocated all FAIL | **KILLED** |
| F1 | private-dir-only manifest | linked case: drop the `manifests_equal` common-dir check (private gitdir check kept) | rc 0, `selftest=PASS ids=7/7`, 0 FAIL lines | **SURVIVED** |
| F2 | always-PASS case emitters | remove all 7 `FAILED=1` flag sites (aggregate never scans for `verdict=FAIL`) | rc 0, `selftest=PASS ids=7/7`, 0 FAIL lines | **SURVIVED** |
| F3a | omitted linked case (id kept) | delete the whole linked-common-dir case body; keep id in `SELFTEST_EXPECTED_IDS` | rc 1, `selftest=FAIL ids=6/7 missing=[SOUJI-R13-STRUCT-linked-common-dir] extra=[] failed_verdicts=0` | **KILLED** |
| F3b | omitted linked case (id dropped) | delete case body and its expected id | rc 0, `selftest=PASS ids=6/6` — **killed only by the frozen final-line oracle** (`ids=7/7` required); survives a lax exit-code-only reading | KILLED (strict oracle) / survives (lax) |
| F4 | wrong target repo | linked case probes main repo A (`$LW_MAIN`) instead of worktree B | rc 1, FAIL; linked case `probe.git_dir=<A/.git> want=<B private>`; `probe.repo_root=<A> want=<B>`; `probe.git_dir==probe.git_common_dir` | **KILLED** |
| F5a | output path-only difference | colocated case compares FULL probe outputs (probe.* lines differ by path alone) instead of `references.*/objects.*` metric lines | rc 0, `selftest=PASS ids=7/7`, 0 FAIL lines (others-monotonicity check still enforced) | **SURVIVED** |
| F5b | output path-only difference, vacuous | full-output comparison AND the `others` greater-than check dropped | rc 0, `selftest=PASS ids=7/7`, 0 FAIL lines | **SURVIVED** |
| F6 | no real keep refs | colocated case never creates `refs/jj/keep/*` refs | rc 1, FAIL; colocated case `metrics-identical; others.count colocated=0 not> plain=0` | **KILLED** |

Killed: 8 (P1–P5, F3a, F4, F6). Survived: 5 (F1, F2, F5a, F5b; F3b survives the
lax detector). Under the frozen final-line oracle F3b is also killed, making 9/13
killed strictly.

## Findings

1. **The two new C3 cases carry the discrimination; the five legacy cases do not
   discriminate the common-dir surface.** P1–P4 are all killed exclusively by the
   `linked-common-dir` / `colocated-vs-plain` verdicts; the legacy 5/5 cases stay
   green. This matches the W1 scal (the committed 5-case fixture false-greened m2–m5).
2. **F1 survives: the fixture's linked-case no-write envelope is only as strong as
   the common-dir manifest comparison.** With that one `manifests_equal` check
   removed, the fixture reports 7/7 PASS while a probe that appends to
   `$common/description` (P2) goes undetected — **F1+P2 combined run:
   `selftest=PASS ids=7/7`, rc 0 (false green)**. The private-gitdir manifest alone
   cannot see common-dir writes.
3. **F2 survives: the selftest aggregate trusts the `FAILED` flag and never scans
   for `verdict=FAIL` lines.** Removing the 7 `FAILED=1` sites yields `selftest=PASS
   ids=7/7` even though cases emit FAIL. **F2+P1 combined run: wrong-common-dir
   probe → `selftest=PASS ids=7/7`, rc 0 (false green)**.
4. **F5b survives: a whole-output comparison is a gameable reading of the counter.**
   The draft's `references.*/objects.*`-only comparison plus the strict `others`
   monotonicity check is what makes the colocated case meaningful; dropping both
   passes trivially. **F5b+P4 combined run: zeroed `references.others.count` probe →
   `selftest=PASS ids=7/7`, rc 0 (false green)**.
5. **F3b is the only mutant whose survival depends on the detector oracle.** The
   fixture self-test exits 0 and prints `selftest=PASS ids=6/6`; the frozen counter's
   target line is `ids=7/7`, so a strict oracle kills it. A counter that only checks
   rc 0 would be fooled. Recommendation for the counter contract: the `ids=N/7`
   literal must be part of the oracle (it already is in the prereg).
6. **P5 (always-PASS/noop emitter) is killed loudly** by multiple cases (metrics,
   bogus, promisor, linked, colocated) — the k0/k7-style control passes.
7. P3's double delta (common + private) is expected: the private gitdir file lives
   at `$COMMON/worktrees/<id>/gitdir`, inside the common-dir subtree. Not a defect.

## Attack log

- A1: first detector batch used relative probe paths; under the fixture's `env -i`
  allowlist a bare name fails exec (`timeout: failed to run command 'probe.sh'`),
  producing rc=127 false FAILs on F1/F3b/F5a/F5b. Recognized as invocation artifact
  (not detector behavior), verified by direct rc checks, and all verdict runs re-run
  with absolute probe paths. The final table above uses only absolute-path runs.
- A2: F1+P2, F2+P1, F5b+P4 false-green combination runs confirm the three survivor
  holes are exploitable by a defect-carrying probe, not just inert deletions.

## Restoration evidence

Lane bytes untouched throughout (read-only seat): lane fixture sha256
`eabc5f0ac56ea3db9f6f68d2dfeadbc91f592eb68c3691d2eabbd5b8347e2c13` == scratch
pristine copy (cmp IDENTICAL); lane probe sha256
`80025137b20d5a6143db0120057552bd239fb60de1a504ede69896baade5aec2` == scratch
pristine copy (cmp IDENTICAL). Baseline (pristine + pristine) re-run green 7/7; rc 0.

STATUS: PASS (13 mutants, 8 killed / 5 survived; 3 false-green combination runs
documented; pristine 7/7 re-verified).
