# VerdictAttack — souji r14 w1 (critic)

Seat: `SoujiR14.VerdictAttack`. This is a leaf seat with no delegation. Axes judged: **calibration** and **operability**.
Target: the gap between declared claims and evidence. The three questions are: does cache-eligible mean historical execution proof; do boundary tests amount to deletion certification; are the legacy scores mapped. The report drafts honest verdict limits and names what makes each limit unprovable.
Rules read: `/home/vgpnk/.omp/agent/RULES.md`, lane `AGENTS.md`, `corpus/QUALITY.md` (Q1, Q6, Q17, Q18), `SCORECARD.md`, `LOG.md` r13, `corpus/lessons/round-13.md`, `census/round-14/{claims,before}.json`.
Installs/upgrades: **none**. Every tool needed was already present: git 2.55.0, Python 3.14.7, shellcheck 0.11.0, `/usr/bin/strace`.

## Evidence classes

**Exercised by this seat.** All of these were read-only commands on lane-owned bytes or host metadata. No test, build, fixture, selftest, census or gate run was performed.
- `git -C <lane> diff --stat 6ed10a7 6f8ee0f` reports 9 files changed, including `tools/souji-cert-evidence.py | 2 +-`.
- `git diff 6ed10a7 6f8ee0f -- tools/souji-cert-evidence.py` shows one changed line, in the `_finding_ids` regex (`[a-z0-9-]` → `[a-z0-9_-]`).
- `git show <rev>:tools/souji-cert-evidence.py | sha256sum` gives `6ed10a7 → a029aaa0a604fb53…`, `6f8ee0f → 943d664c5df4e795…`, and HEAD `a31642d → 943d664c…`.
- I parsed `census/round-13/verification-attempt-1.json` and `verification.json` in Python, read-only, to list each result's keys (results below).
- `git --version`, `python3 --version`, `shellcheck --version`, and `/var/log/pacman.log` show no git, python or shellcheck change since 2026-10-18.
- `stat -c '%d %m'` shows `/var/tmp` on device 31 and `/home` on device 57. `sysctl fs.protected_hardlinks=1`.
- `sha256sum tools/souji-census.sh` gives `6a000c59…`, which is unchanged from r13. C2 had not landed when this report was written.
- `tools/souji-evidence-cache.py` was observed at `085f8edb…`. It was still being edited live during review.

**Code inspection only (not executed):** `tools/souji-evidence-cache.py` (in flux), `census/round-14/cache-demonstration.py`, `census/round-13/run-verification.py:31-76`, `tools/souji-census.sh:95,317-346,355-386`, `tools/souji-cert-evidence.py:1018-1043`.

## Counterexamples

### CE1 — r13 already reused stale green, with an inherited revision (observed, real data)
`verification-attempt-1.json` results carry **no** per-result `measured_commit` and **no** dependency digests. The keys are only `command, exit_code, expected_exit, matched, name, seconds`.

`run-verification.py:51` then fills in the revision with `retained.get("measured_commit", PREVIOUS["measured_commit"])`. So the four retained greens in `verification.json` got `6ed10a7` from the file-level field, not from a per-result record:

| retained result | command depends on | dependency bytes at measured 6ed10a7 | bytes named by `verification.json.installed_sha256` |
|---|---|---|---|
| evidence-frozen | `tools/souji-cert-evidence.py` + `tests/fixtures/r13-cert-frozen/**` | `a029aaa0…` | `943d664c…` |
| historical-replay-wrong-bytes | `tools/souji-cert-evidence.py` + replay manifest/fragments | `a029aaa0…` | `943d664c…` |
| historical-replay-candidate | same | `a029aaa0…` | `943d664c…` |
| structure-selftest | `tests/fixtures/r13-repo-structure.sh`, `tools/souji-repo-structure.sh` | unchanged 6ed10a7→6f8ee0f (empty diff) | same |

- Three of the four retained greens were measured on bytes different from the installed digest the same document reports. This is a Q6 shape: the verdict's digest is not the digest of the bytes measured.
- The SCORECARD row discloses "historical replays 6ed10a7", so the revision is disclosed but the byte identity is not.
- [INFERENCE] The changed line is only reached through `_record()` in `--selftest`, so the `--frozen`/`--manifest` outcomes probably did not move.
- A digest-bound gate must not credit that line-level argument. Under C1, all four records are `dependencies-legacy` (exit 2) and must not be reused.

**Impacted axes.** Calibration: the declared revision is inferred, not recorded. Operability: none.

### CE2 — "eligible" can be produced by a pure declaration
- The gate compares the declared digests with the current bytes. A hand-written record `{matched:true, measured_commit:<any 40-hex>, dependencies:<current digests>}` exits 0.
- The gate docstring says this outright ("checks binding and consistency, not truth, and never proves the retained command ran").
- `measured_commit` is format-checked and echoed back. It is **never cross-checked** against the declared dependency digests (for example, `git show <commit>:<path>`).

So "per-result measured revisions remain explicit" means explicitly declared, not verified.

### CE3 — dependency completeness and environment are unbound
- **Incomplete dependency sets pass.** A record that declares only `tools/souji-cert-evidence.py` for `evidence-frozen` binds no `r13-cert-frozen/**` files. Dependencies must be regular files, so directory fixtures must be listed file by file, and a file *added* to such a directory is invisible to the gate.
- **The environment is not bound.** Python, git, shellcheck, the environment variables and HOME are not part of a record.
- QUALITY Q1 exists precisely because git 2.55 changed behaviour (round-9 and round-6 lessons). A host git upgrade would leave a digest-matching stale green.
- This was not observed between r13 and r14: the pacman log shows no git/python/shellcheck change since 2026-10-18. It is a bounded guarantee to state, not a bug.

### CE4 — the C1 demonstration overstates what "fresh execution" means (inspection)
- **Nothing is executed.** In `cache-demonstration.py`, `producer()` hashes two synthetic files and hard-sets `matched=True`. The results are still labelled `result_origin="fresh-execution"` and `producer_executed=true`.
- **The revision does not contain the measured bytes.** Each synthetic result's `measured_commit` is the lane HEAD. HEAD does not contain the `/var/tmp` dependencies, and at HEAD `a31642d` it does not contain the gate either, because the gate is untracked.
- **Finding ids are not asserted.** The checks look only at exit codes. A missing id only produces an advisory, so a wrong finding id still passes.
- **The control is hypothetical.** The "unsafe policy control" has `old_policy_executions = 1` hard-coded, and is honestly labelled `hypothetical: true`.

Conclusion: the demonstration shows routing (gate exit → reuse or re-run). It does not show that retained results were true, or that anything was measured.

### CE5 — C2 spy ordering cannot see builtins; hardlink and HOME aliases (inspection of the r13 census, C2 not landed)
- **Builtins are invisible to PATH spies.** In `souji-census.sh`, directory enumeration is a bash glob (`for d in "$root"/*/`, l.324, i.e. `getdents`). `[ -d ]` and the `read` loop over `--compare` (l.365-385) are also builtins. Spies prove "no git/find/du before refusal"; they cannot prove "no readdir/read".
- **A hardlinked `--compare` file passes.** A hardlink to a store file on the same filesystem (`/home` is a single device 57; `protected_hardlinks` does not stop the owner) passes both lexical and `readlink -m` checks. Its first line is then read before the header-mismatch error.
- **This case can be built safely.** On the same device, a synthetic store and a hardlink both under `/var/tmp` (device 31) reproduce it.
- **A boundary taken only from `$HOME` moves with `HOME`.** If the C2 boundary is derived from `$HOME` alone, the guard follows HOME, and a synthetic-HOME fixture proves exactly that. The evidence-cache gate already adds a defence that C2 should copy: a component-name check (`.omp`, `.ssh`, …) on the resolved parts.
- **Canonicalization touches metadata.** `readlink -m` lstat()s path components that may sit inside the store before the refusal. No content is opened, but this is metadata access, not zero access.
- **Not testable without privilege, so they remain limits:** bind mounts, FUSE and mount-namespace aliases, and TOCTOU (a symlink swapped after the check).

### CE6 — legacy numbers cannot carry saturation or stagnation
- SCORECARD's own header says to score "only where a reproducible mapping from evidence to number exists". The cells nonetheless show 7/8/8, marked legacy-unmapped.
- Operability (8) and coverage (8) sit exactly on the stated saturation line, and r13 plus r14 both have numeric delta 0.
- A reader applying the "saturation 8" or "stagnation window 3" rule to these numbers would conclude saturation or stagnation from unmapped labels. That conclusion would be premature.
- "Lowest score 7" picks which axis to work on. It is not a measurement.

## Draft verdict limits (for the L1 gate)

- **C1 (calibration).** Proposed text: "`tools/souji-evidence-cache.py` <sha256> (committed at <measured_commit>) refuses reuse unless every *declared* repository-relative dependency is a contained, non-symlink, nlink-1 regular file whose current sha256 equals its declaration and `matched` is JSON `true`. Legacy or empty dependency maps exit 2, drift exits 1, with named findings (selftest N/N, fixture M/M, both exercised at <rev>)." It must **not** claim:
  - that any retained result was executed;
  - that it was executed at its `measured_commit` (declared, unverified);
  - that dependency sets are complete;
  - that the environment or tool versions are bound;
  - that r13's historical runner was fixed. It stays unaltered by design, and its four retained greens remain legacy or stale under the new rule.
- **C2 (operability).** Proposed text: "`souji-census.sh` <sha256> refuses `--root`/`--compare` that lexically or symlink-canonically equal, contain, or lie inside the synthetic credential-store boundary, before any *spied external* git/find/du call, exit 2 `<id>`, on the enumerated synthetic cases; normal fleet output is retained (selftest N/N)." It must **not** claim:
  - credential safety in general;
  - protection against hardlink, bind-mount, mount-namespace or TOCTOU aliases;
  - protection when HOME is altered (unless a name or passwd fallback is present and tested);
  - absence of builtin readdir/read before refusal (unless traced with strace);
  - anything about the real store, which was never touched.
- **Both claims.** Certification stays OFF. Neither result grants deletion authority (Q18). The census is read-only, and the quarantine/verify tools are unchanged and uncertified. Comprehensive class-suite recertification is not claimed. Scores stay 7/8/8 legacy-unmapped with numeric delta 0, and no saturation or stagnation verdict is drawn from them. S039 may be cited only after L1's own runs.

## What forces "unprovable"

| claim | why it cannot be proven from repository bytes | what would be needed |
|---|---|---|
| retained result actually ran | Records are self-authored JSON, and anyone who can write them can write `matched:true`. There is no attested execution log. | A same-session re-run, or a trusted runner's signed transcript. |
| ran at `measured_commit` | The working tree may have been dirty, and the commit is never compared with the dependency bytes. | Commit before measuring, plus a `git show <mc>:<p> \| sha256sum` binding check. |
| dependency set complete | Only declared files are hashed; no access trace exists for the original run. | Record a file-access trace (for example strace `openat`) during the producer run. |
| environment equal | Interpreter, tool versions and environment variables are not in the record. | Add the versions to the record, or accept the bound and state it. |
| no store access by any alias | Bind mounts, hardlinks, namespaces and races are not enumerable by finite fixtures; the guard works on paths only. | Mount and inode policy at the OS level; out of scope. |
| deletion safety | No deletion path changed; Q18 separates integrity from safety. | The class suites under Q6/Q18. |

## Smallest safe corrections (none blocks C1/C2 if the limits above are adopted)

1. **L1 sequencing (calibration).** Commit the r14 tool and fixture bytes **before** the measuring run, then check `git show <mc>:<path> | sha256sum` against each recorded digest. HEAD `a31642d` does not contain the gate or the C2 change.
2. **No ungated retention in r14.** Run everything fresh, or route every reused result through the installed gate and record its exit code and findings.
3. **Demonstration labels.** Mark the producer as `synthetic-stub, always green` and scope `measured_commit` as "lane HEAD at run". Optionally add a real-data case: the r13 retained records → `dependencies-legacy` (exit 2).
4. **C2.** Refuse a `--compare` file whose `stat -c %h` > 1. Add a name-component check on the resolved path, as the gate does. Either strace the synthetic fixture for `openat`/`getdents64`, or narrow the claim wording to spied external commands.
5. **Optional, gate (tradeoff).** Verify `measured_commit` against the dependency bytes via git, with a stable finding such as `commit-dependency-mismatch`. The cost is that results measured on a dirty tree become ineligible.

Delivered by peer message (concise): item 4 → `SoujiR14.CensusBoundary`, items 3/CE4 → `SoujiR14.RetentionRunner`, items 1–2 → `SoujiR14.FinalEvidencePlan`.

## Final L1 commands (not run by this seat)

```sh
L=/home/vgpnk/Projects/shokunin/souji-shokunin
# after committing r14 bytes; MC=$(git -C $L rev-parse HEAD)
for p in tools/souji-evidence-cache.py tools/souji-census.sh tests/fixtures/r14-evidence-cache.py tests/fixtures/r14-census-boundary.py census/round-14/cache-demonstration.py; do
  printf '%s ' "$p"; git -C $L show "$MC:$p" | sha256sum; sha256sum "$L/$p"; done        # pairs must match
python3 -B $L/tools/souji-evidence-cache.py --selftest; echo "exit=$?"
python3 -B $L/tests/fixtures/r14-evidence-cache.py --tool $L/tools/souji-evidence-cache.py; echo "exit=$?"
python3 -B $L/tests/fixtures/r14-evidence-cache.py --tool /var/tmp/souji-r14-absent-gate; echo "exit=$?"   # baseline = absence, not behaviour
python3 -B $L/census/round-14/cache-demonstration.py; echo "exit=$?"
# real-data legacy refusal (read-only): expect exit 2, finding dependencies-legacy for each
for n in evidence-frozen structure-selftest historical-replay-wrong-bytes historical-replay-candidate; do
  r=$(python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));print(json.dumps(next(x for x in d["results"] if x["name"]==sys.argv[2])))' $L/census/round-13/verification.json "$n")
  python3 -B $L/tools/souji-evidence-cache.py --root $L --record "$r"; echo "$n exit=$?"; done
# reconstructed (label: reconstructed-from-git, not original) r13 binding: expect exit 1 dependency-digest-mismatch
python3 -B $L/tools/souji-evidence-cache.py --root $L --record '{"name":"evidence-frozen","matched":true,"measured_commit":"6ed10a7cd6c7b26f8068dd6e02497e860f9c4317","dependencies":{"tools/souji-cert-evidence.py":"a029aaa0a604fb53dfcba650f95b3626d543890bd1d96110d2340cd30144ece1"}}'; echo "exit=$?"
# C2: baseline from a31642d extracted under /var/tmp vs installed
python3 -B $L/tests/fixtures/r14-census-boundary.py --tool <var-tmp-baseline-census.sh>; echo "exit=$?"
python3 -B $L/tests/fixtures/r14-census-boundary.py --tool $L/tools/souji-census.sh; echo "exit=$?"
bash $L/tools/souji-census.sh --selftest; echo "exit=$?"
shellcheck -S warning $L/tools/souji-census.sh; echo "exit=$?"
find /var/tmp -maxdepth 1 -name 'souji-r14*' | wc -l    # expect 0 residue
```

Dependency for the real-data and reconstructed commands: they assume the gate's final `--record` accepts literal JSON and tolerates extra keys, as its docstring says. Re-check that after CacheGate's last edit.

## Residual risk

- C2 bytes were not reviewed. Its CE5 points come from the r13 census plus the shared interface (`to-verify`).
- The gate changed while I was reviewing it, so its final digest is `to-verify` at L1.
- CE1's [INFERENCE] about which code path the changed line reaches is not exercised. It is irrelevant to the digest-bound verdict.

## Addendum — follow-up after RetentionRunner's reply

I re-read the files for this follow-up. What I exercised was read-only: `git status --short`, `git diff --stat`, `git diff -- census/round-13/run-verification.py`, `sha256sum`, and greps. Nothing was run. Digests at this time: `census/round-14/cache-demonstration.py` `7748ffd2…`, `tools/souji-evidence-cache.py` `1ab46ab4…`.

**CE4 resolved, by inspection only.**
- The demo producer is now a real isolated subprocess. `matched` comes from exit 0 plus exact stdout equality.
- `producer_kind`, `harness_revision` and `measured_commit_scope` labels are present.
- The stale and legacy cases assert the exact ids `dependency-digest-mismatch` and `dependencies-legacy`.
- The four r13 retained greens are refused read-only (expected `dependencies-legacy`).

**A1. Historical runner edited in place: identity and provenance (observed in the working tree).**
- `census/round-13/run-verification.py` has an uncommitted change of 174 lines that adds gate-backed retention. The committed runner that produced r13 evidence is index blob `b22ed5b`. CacheGate's spec says "Do not alter historical runner"; the author of this edit is not identified.
- **Impact (calibration):** SCORECARD's r13 operability counting command is `python3 census/round-13/run-verification.py --retry-failed`. That command now runs bytes other than the ones that produced `verification.json`.
- **Impact (operability):** the runner still writes the fixed `OUTPUT = census/round-13/verification.json` with `round=13`. Running it again would overwrite r13 evidence with results produced by r14 bytes.
- **Smallest correction (routed to L1):** move the migrated policy to a `census/round-14/` runner with round-14 output and restore the r13 runner. If the in-place edit is kept, refuse to overwrite an existing round-13 output and record `b22ed5b` as the r13 runner identity in LOG.
- **What the migration itself does well (inspection):** it never inherits a top-level revision, it requires per-result `dependencies_stable`, and it exempts external commands. Its `dependency_map` binds only command-line paths, fixture-directory children, and one special-cased helper. Transitive or sourced files and the environment remain unbound, as in CE3, so they belong in the verdict limits.

**A2. Demo/migrated-runner root mismatch: expected red, by inspection, not executed.**
- `cache-demonstration.py` calls `migrated_module.attempt_reuse(NAME, dict(initial_result))`. That reaches `gate_reuse`, which invokes the gate with `--root str(ROOT)`, and ROOT is the lane root.
- The `initial_result` dependencies (`observations/alpha.txt`, `observations/beta.txt`) exist only in the `/var/tmp` fixture root. The lane has no `observations/` directory (`ls` observed ENOENT).
- [INFERENCE] As a result, `migrated_caller_reuses_unchanged` fails (gate exit 1, `dependency-missing`). `migrated_caller_refuses_stale` also fails, because its findings would be `dependency-missing` rather than `dependency-digest-mismatch`. The demo would then exit 1.
- **Smallest fix (sent to RetentionRunner):** set `migrated_module.ROOT = root` before calling `attempt_reuse`, since the global is read at call time, and record that the root was rebound.

**Extra L1 commands:** run `git diff --stat -- census/round-13/run-verification.py` before committing and decide A1. After any r14 run, check that `git diff -- census/round-13/verification.json` is empty, so r13 evidence was not overwritten. Re-run `python3 -B census/round-14/cache-demonstration.py` and expect `failed_checks: []`.

**Follow-up 2 (L1 reply, source-only, nothing executed).**
- **Authorization:** L1 states that RetentionRunner was explicitly assigned the migration, so A1 is withdrawn as unauthorized overlap. The provenance and overwrite hazard still stands.
- **A2 resolved (inspection).** `cache-demonstration.py` `09fe38d7…` rebinds `migrated_module.ROOT = root` at line 379. In `run-verification.py` `2dcfe72b…`, `gate_reuse` uses the import-time `GATE_LABEL` and absolute `GATE`, and uses ROOT only for `--root`. So the rebind does not raise from `relative_to`, and the record is evaluated against the fixture root.
- **A1 overwrite still unfixed in `2dcfe72b…`.** The runner still has `OUTPUT = census/round-13/verification.json` (line 28), writes it at line 284 with `round=13` (line 273), has no `--round`/`--output` parsing, and reads `--retry-failed` PREVIOUS from the round-13 file at import (line 51).
- **Acceptance for the planned fix (source review of the final bytes):**
  1. Argument parsing and the refusal both happen before any read, `git`, or subprocess call. A missing `--round` or `--output` exits 2.
  2. The output path is canonical, lies under `census/round-<N>/`, and is not `census/round-13/verification.json` or `verification-attempt-1.json`. An existing output is refused (no overwrite) or written via a fresh name.
  3. The `--retry-failed` source is an explicit, read-only path. Import has no side effects, which keeps the demo's `exec_module` safe; currently PREVIOUS reads only when `--retry-failed` is in `sys.argv`.
  4. `round=` in the record equals `--round`, not a literal 13.
  5. LOG and SCORECARD state that reproducing r13 means running blob `b22ed5b` at `6f8ee0f`.

**Follow-up 3: source review of the final runner `7993ef18…` (demo `fc6f69a0…`; read only, nothing executed).**
- Criterion 1 passes. `main()` refuses with exit 2 when `--round` or `--output` is missing, and `validate_output` and `validate_previous` refuse with exit 2. All of this happens before `git rev-parse`, before the previous-file read, and before any subprocess (lines 331–346 precede 349). The import now sets `PREVIOUS=None` with no read (line 65), so the demo's `exec_module` has no side effects.
- Criterion 2 passes. The output must be lexically inside `census/round-<N>/`, be a `.json` file, and have no protected or operator-sweep component, no symlink, and no symlink ancestor. An existing file is refused (`output-exists`). The write uses exclusive create (`open("x")`, O_EXCL), so a race or a dangling final symlink also fails closed with exit 2. The historical round-13 files exist, so they are refused.
- Criterion 3 passes. `--previous` is explicit (default `census/round-13/verification.json`), contained, regular, non-symlink, and read-only. Its results have no `dependencies` or per-result `dependencies_stable`, so `attempt_reuse` re-executes every one (`prior-dependencies-unstable`/`legacy`). No historical green can be retained.
- Criterion 4 passes: `round=args.round`.
- Criterion 5 is open and lies outside RetentionRunner's files. The SCORECARD r13 counting command `python3 census/round-13/run-verification.py --retry-failed` now exits 2 (fail-closed, no overwrite). LOG and SCORECARD must say that reproducing r13 means running blob `b22ed5b` at `6f8ee0f`.
- Low residuals, not blocking:
  - (a) `--round 13 --output census/round-13/<new>.json` is accepted, so r14-byte evidence can land inside the closed r13 evidence directory labelled round 13. Smallest fix: refuse a round lower than the current round, or document the case.
  - (b) Unhandled exceptions after validation exit 1. Examples are a `git` failure, a malformed `--previous` JSON or a `KeyError`. Exit 1 also means "checks failed", so wrap these and return 2.
  - (c) A parent-directory swap between validation and `open("x")` is not closed. The same bound is already documented for the gate.

**Follow-up 4: runner `624ebaef…`, demo unchanged `fc6f69a0…` (read only, nothing executed).**
- Residual (a) is closed. `closed_round_floor()` takes the highest non-symlink directory under `census/` named `round-<N>`, and `validate_output` refuses any lower `--round` as `round-closed` before any check runs (lines 260–287). Now that `census/round-14/` exists, round 13 is refused.
- One side effect of computing the floor from directories: a stray higher `census/round-<M>/` raises the floor. That only refuses more runs (fail-closed); it is not a safety gap.
- Residual (b) is closed. `main()` wraps `execute()`. `FileExistsError` and every other `Exception` after validation exit 2 (lines 367–375). Red checks alone exit 1 (line 444).
- Residual (c) stays a documented bound, and criterion 5 (the LOG/SCORECARD reproduction note) is still owned by L1 or Bookkeeping.
- For L1: use `--round 14 --output census/round-14/<new>.json`. Any round-13 output is now refused.
- Final digest check (`sha256sum`, exercised): demo `fc6f69a0…` and runner `624ebaef…` match RetentionRunner's final report. The gate `tools/souji-evidence-cache.py` is now `f8f541f7…`, not the `b4b50d00…` that report ends at, so it moved again. L1 must commit the gate before measuring and check that the demo's recorded `gate.sha256` equals `git show HEAD:tools/souji-evidence-cache.py | sha256sum`.
