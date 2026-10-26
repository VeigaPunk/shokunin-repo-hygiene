# SwarmReviewer14 — C2 fixture patch review (a2w1)

## Status
STATUS: PASS — the C2 patch to the nine scoped fixtures changes only the scratch root (TMPDIR-honouring); all 36 matrix runs (base×c2 × TMPDIR set/unset) exited 0 with identical case sets, guards and refusal verdicts; cleanup intact; no guard widened. One low-severity environment-dependent finding on the new `_private_var_tmp` wrapper; nothing blocking.

## Evidence
Revisions: base `85b61a151923986e7e6b48f7084b9122561b5f3d`, landed C2 `98e5203d45b4e419a9e72801733d93303acc7ebd`, verified in scratch worktrees (`git -C <wt> rev-parse --show-toplevel` printed each worktree; HEADs matched). Diff scope: 9 files, +71/−22.

Matrix: each c2-items.tsv command for my items (T17, T18, T20, T21, T22, T23, T25, T26, T27) run in the scratch clone at both revs, with `TMPDIR=/fast/scratch/hyaku/souji-r32/ReviewC2Fixtures/tmp` and with TMPDIR unset — 36 runs, **all rc=0**. Last lines (identical across all four conditions per item):

| item | last line |
|---|---|
| T17 | `SUMMARY	total=66	pass=66	fail=0	base_discriminating=0` |
| T18 | `SUMMARY	total=52	pass=52	fail=0	blocked=0	inventory=exact	baseline_mismatches=26→31` |
| T20 | `control=FALSE-GREEN-REJECTED` (`selftest=15/15`) |
| T21 | `cases=9 pass=9 control=FALSE-GREEN-REJECTED` |
| T22 | `cases=16 pass=16 control=FALSE-GREEN-REJECTED` |
| T23 | `cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` |
| T25 | `cases=12 pass=12 control=FALSE-GREEN-REJECTED` |
| T26 | `cases=4 pass=4 control=FALSE-GREEN-REJECTED` |
| T27 | `cases=15 pass=15 control=TAMPER-REJECTED` |

Output identity (full stdout, base vs c2, paths normalized to `<WT>`/`<SCRATCH>`):
- T17, T20, T21, T22, T23, T25, T26: byte-identical after normalization (67/20/19/35/13/13/6 lines).
- T18: differs only in `BASELINE_MISMATCH`/`BASELINE_SUMMARY` lines (worktree-content hashes vs pinned baseline `12516f7d`; +5 mismatches = `tools/souji-census.sh`, `souji-cert-evidence.py`, `souji-evidence-cache.py`, `souji-repo-structure.sh`, `souji-round9-selftest.sh`, all confirmed present in `git diff --name-only 85b61a1 98e5203d` (48 files)) and in 40-hex revision tokens inside `first_refusal=` refusal text; CASE sets (52/52) identical modulo those tokens, and base differs from itself across modes (tokens `7619e340…` vs `b1fb1a18…`), i.e. per-run nondeterminism, not the patch.
- T27: differs only in per-run scratch-repo commit ids (`verify-rev rev=<40hex>`); control: two base runs differ in the same 19 lines; `records/failed/uncovered` multisets equal base↔base and base↔c2 (incl. the one `failed=1` tamper case).

Check (2) no guard widened — the patch touches only scratch constants, docstrings/help text, and the appended r20 wrapper. Guard sites unchanged: `tests/fixtures/r26-axis-check.py:342` `if not SCRATCH_BASE.startswith(SCRATCH_PREFIX) or os.path.islink(SCRATCH_BASE):` (same expression, new root value; startswith still holds by construction); `tests/fixtures/r24-size-census.py:378` `isdir(SCRATCH_PARENT)` guard unchanged. Refusal/write-scope suites still enforce at c2 (T17 66/66, T18 52/52, T23 `WRITE-DETECTED`). r28 env override still wins: probe with `SOUJI_R29_C2FIXTURE_BASE` set → scratch landed in the override dir, rc=0, run dir fully cleaned. Quotes: `tests/fixtures/r27-pre-report-gate.sh:7` `D=$(mktemp -d "${TMPDIR:-/tmp}/souji-r27-pre-report.XXXXXX")`; `tests/fixtures/r28-wave-evidence-capture.sh:51` `scratch_root=${SOUJI_R29_C2FIXTURE_BASE:-${TMPDIR:-/tmp}/souji-r29-wave-capture-fixture}`; `tests/fixtures/r23-record-agreement.py:68` `SCRATCH_ROOT = os.path.join(tempfile.gettempdir(), "souji-r23-ExecFixtureAgreement")`.

Check (3) TMPDIR unset — all nine items rc=0 at both revs; c2 falls back to `/tmp` via `tempfile.gettempdir()` / `${TMPDIR:-/tmp}`. `TMPDIR=""` (empty) also tested: T20/T26 rc=0, scratch in /tmp, cleaned.

Check (4) cleanup — final residue scan of my TMPDIR, /tmp, /var/tmp after all runs: zero residue from my nine items except by-design persistent roots `souji-r29-wave-capture-fixture` (present and empty in all three roots; the fixture removes only its `run.XXXXXX` — same policy at base, root relocated). Wrapper private dirs `souji-private-vartmp.*` removed in every run, including the failing-bwrap probe. Ambient note: sibling seats ran the same fixtures concurrently during my window (`souji-census-now.*`, `souji-quarantine-selftest.*`, `r13/r14/r15-selftest` dirs in /var/tmp); pre-existing entries recorded, untouched, not mine to remove.

Tooling: none installed or upgraded (nothing needed beyond bwrap 0.13.1, already present).

## Findings
1. **LOW** — `tests/fixtures/r20-audit-contract.py:664-685`, `tests/fixtures/r20-input-binding.py:1292-1313`: if `bwrap` exists but cannot run (userns denied, seccomp), the wrapper exits with bwrap's rc and the fixture never runs: reproduced with a failing stub → rc=99, stdout empty, stderr `bwrap: stub failure`. Opaque failure mode for counter runs; docstring claims "bwrap binds a fresh directory under TMPDIR over /var/tmp for the whole process tree" but nothing reports a sandbox-skipped-vs-failed distinction. Mitigated on this host (see Attack log A2).
2. **INFO** — same wrapper: masks `/var/tmp` only; with TMPDIR unset the private dir is `/tmp`-backed (`tempfile.mkdtemp` default), so the "caller's TMPDIR" is effectively /tmp — consistent with the `${TMPDIR:-/tmp}` fallback used elsewhere, scratch is tiny and cleaned. Also `subprocess.call` returns −N on child signal and `sys.exit(rc)` maps that to 256−N (247 not 137) — cosmetic rc skew only on signal death `[INFERENCE — not exercised]`.
3. **INFO** — T18 `baseline_mismatches` 26→31 is an expected input-content artifact: the fixture hashes 65 tracked files against the pinned baseline, and the C2 commit patched 5 more of them. Same commit also patched `tools/souji-rev-pin.py`, `tools/souji-census.sh`, `tools/souji-cert-evidence.py`, `tools/souji-evidence-cache.py`, `tools/souji-repo-structure.sh`, `tools/souji-round9-selftest.sh`, `tests/fixtures/r13-repo-structure.sh` — outside my nine-file scope; routing note for the L1 (other seats cover those).
4. **INFO** — amendments record C2 `26/27 -> MISSED on T18` at the integration commit. Not reproduced here: counter-style nested bwrap at `98e5203d` passes T18 52/52 (Attack log A2). Either the miss predates the current tree or is environment-specific; the mechanism in Finding 1 is the plausible candidate if the counter's sandbox blocked nested userns.
5. **INFO** — `tests/fixtures/r23-record-agreement.py:68`: fixed shared-name scratch root retained (`gettempdir()/souji-r23-ExecFixtureAgreement`, rmtree-whole-root in `cleanup()`), so two concurrent runs of the same fixture still delete each other's world — pre-existing property at base (`/var/tmp` fixed name), not widened or worsened by this patch; under a per-seat TMPDIR it is private.
6. **INFO** — `tests/fixtures/r28-wave-evidence-capture.sh:51-54`: persistent `scratch_root` with per-run `run.XXXXXX` trap-cleanup is unchanged semantics; override precedence `SOUJI_R29_C2FIXTURE_BASE` > `TMPDIR` > `/tmp` preserved.

## Attack log
- A1 (opaque wrapper failure): stub `bwrap` exiting 99 → T17 at c2: rc=99, stdout 0 lines. Reproduced Finding 1.
- A2 (counter-sim nesting): outer `bwrap --dev-bind / / --ro-bind /tmp /tmp --ro-bind /var/tmp /var/tmp --ro-bind /dev/shm /dev/shm` + `TMPDIR=<scratch>`, inner wrapper active: T17 rc=0 66/66, T18 rc=0 52/52, T20 rc=0 15/15; zero residue in the sim scratch. Nested bwrap works on this host; wrapper survives the counter's sandbox.
- A3 (nondeterminism controls): T27 base-vs-base and T18 base-vs-base (tmpset vs tmpunset) differ in exactly the rev-token lines — proves those deltas are per-run, not patch-caused.
- A4 (guard-widening hunt): full diff read of all nine files — no conditional, path check, refusal policy or case set modified; only constants/docstrings/help text + the appended wrapper. r26 `startswith` guard still self-consistent; no widened path acceptance found.
- A5 (empty TMPDIR): `TMPDIR=""` → both shell (`${TMPDIR:-/tmp}`) and Python (`gettempdir()`) paths fall back to /tmp, rc=0, cleaned.
- A6 (cleanup hunt): per-run and final residue scans; only by-design empty persistent roots remain (see Evidence).

## Deliveries
- `.ufo/waves/round-32/a2w1/SwarmReviewer14.md` (this report)
