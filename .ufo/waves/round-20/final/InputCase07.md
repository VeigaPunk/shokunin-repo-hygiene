# InputCase07 — C2 caller-case falsifier: `r13-counted-knowledge-added`

Scope: read-only falsifier for one fixture case. Pin `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`; preregistered baseline `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`. Only the applicable caller was inspected: `census/round-13/run-verification.py`. No fixture, caller, helper, gate or count script was executed; no imports; no installs or updates; no writes except this file. Every claim is source-derived unless marked as an observed read-only git query.

## Verdict

- **Source agreement for the case at the pin.** The caller refuses the added counted-knowledge record in its input snapshot: exit 2, the changed path on stderr, empty stdout, no evidence file. The trace in §1 matches each conjunct of the fixture predicate.
- **The predicate is not specific.** `changed_path in stdout+stderr` also passes for an I/O refusal that names the same absolute path (§5a, bounded counterexample). This is latent for the case's own mutation, which writes a readable file.
- **The baseline witness is valid only with `--baseline 12516f7d…`.** With `--baseline 31984f47…`, the caller's own `BASE` constant, the pair blocks because that caller does not exist at 31984f47 (§6).
- No `STATUS: PARTIAL`. Nothing here blocks the case in a default run; the items below are hardening and operator-REV hazards.

## Observed (read-only git; nothing executed)

| Query | Exit | Result |
|---|---|---|
| `git show 1988860…:tests/fixtures/r20-input-binding.py` | 0 | Read in full. |
| `git show 1988860…:tools/souji-rev-pin.py` | 0 | blob `8da7da9c…` (100755). |
| `git show 1988860…:census/round-13/run-verification.py` | 0 | blob `b5107ef5…` (100755). |
| `git show 31984f47…:census/round-13/run-verification.py` | 128 | "exists on disk, but not in 31984f47…". |
| `ls-tree -r --name-only 31984f47… -- <23 closure paths>` | 0 | 13 of 23 absent (listed in §6). |
| `ls-tree -r --name-only 1988860… -- <23>` | 0 | 23 of 23 present; `corpus/knowledge/r20-input-binding-added.md` absent. |
| `ls-tree -r --name-only 12516f7d… -- <23>` | 0 | 23 of 23 present. |
| `ls-tree -r 1988860… and 12516f7d… -- <23>` | 0 | Every blob is 100644 or 100755; no symlink (120000) or submodule (160000). |
| `cat-file -t 12516f7d…` | 0 | `commit`. |
| `git show 12516f7d…:census/round-13/run-verification.py` | 0 | blob `e9b79525…`. |
| `git show 12516f7d…:tools/souji-rev-pin.py` | 0 | blob `332d4f09…`. |
| `git show 1988860…:corpus/knowledge/{dupe-finders-detect-then-act,git-auto-maintenance-prunes-worktrees,git-grace-periods-and-expire-to}.md` | 0 | Each has `source:`, `verified-at:`, `recheck:` on lines 1–3 and no HELD heading. |

"23 closure paths" means the caller's 22 `MEASURED_PATHS` (including the directory `corpus/knowledge`) plus `census/round-13/verification.json`, which the fixture passes via `--previous`.

## 1. Entrypoint trace (pinned caller)

`__main__` → `main()`. argparse accepts the fixture's `--round 20 --output … --retry-failed --previous …`. `validate_output` accepts the new `census/round-20/*.json` (the closed-round floor is 20 because the fixture creates `census/round-20/`). `validate_previous` accepts the regular prior file. Then `execute()`:

1. `PREVIOUS_SOURCE = census/round-13/verification.json`.
2. `resolve_revision()`:
   - `head = git rev-parse HEAD`. The caller's module-level `ENV` drops every `GIT_*` variable at import, so the fixture's decoy `GIT_DIR` is ignored.
   - `tools/souji-rev-pin.py` bytes equal `git show HEAD:tools/souji-rev-pin.py`. The sandbox is committed before the mutation, so they match.
   - `INPUT_PATHS = MEASURED_PATHS + [prior]`, 23 entries.
   - `resolve_durable(ROOT, head, INPUT_PATHS)`: 40-hex ✓, `refs/heads/main` reachable ✓, then `input_snapshot`.
   - `input_snapshot` compares committed blobs (`ls-tree`) with a working-tree `os.walk`. `corpus/knowledge/r20-input-binding-added.md` is in *actual* and not in *expected*, so it raises `Refusal("measured inputs differ from <head> (missing=[] added=['corpus/knowledge/r20-input-binding-added.md'] changed=[])")`.
   - `resolve_revision` catches `ValueError`, prints `run-verification: refused: … (no record written)` to stderr, and calls `raise SystemExit(2)`.

Nothing reaches stdout: no print precedes `resolve_revision`. `output.open("x")` is at the end of `execute()` and is never reached. `main`'s `except Exception` does not catch `SystemExit`. Process exit is 2.

Expected fixture CASE line, by source: `CASE pass r13-counted-knowledge-added changed=corpus/knowledge/r20-input-binding-added.md; exit=2 changed_path_named=1 output_absent=1 suite_stdout_absent=1`.

## 2. Changed input

This is not a byte edit. The fixture adds `corpus/knowledge/r20-input-binding-added.md`:

```
source: fixture-local
verified-at: 2026-10-21
recheck: r20-input-binding

# inert counted-input fixture; no external source claim
```

It satisfies the caller's admission predicate (prefixes on lines 1–3, no HELD heading), so it would be counted in `admitted_entries` if it were not refused. "Inert" means only that it makes no external source claim. The fixture's `inert_suffix` byte mutations are not used for this case.

## 3. Closure and consumption

- Caller closure equals fixture closure: `r13_paths + [R13_PRIOR]`, the same 23 paths. Because the fixture passes `--retry-failed --previous R13_PRIOR`, the caller's `INPUT_PATHS` equals the fixture's measured set.
- `corpus/knowledge` is consumed twice. (a) The snapshot, which causes the refusal. Its walk is recursive. (b) `execute()` globs `corpus/knowledge/*.md` into `admitted_entries`, reached only if (a) passes. The glob is non-recursive, so a nested addition is refused but not counted: stricter, with no gap. `obsidian-ledger.tsv` is snapshot-measured but not counted.
- The fixture checks coverage by AST-parsing the caller's literal (`covered_by_measured`). That is a wiring precondition. If `corpus/knowledge` were removed from the caller, the fixture would raise `FixturePrerequisite` and block the whole run with exit 2, rather than FAIL this case.

## 4. Predicate (`caller_refusal`, kind r13)

`returncode == 2 and changed_path in (stdout+stderr) and output_absent and stdout == ""`, where `output_absent` checks that `census/round-20/r20-r13-counted-knowledge-added.json` does not exist in the sandbox. Each conjunct holds on the §1 trace.

The check is behavioral: a subprocess of the real entrypoint, in a real isolated repository, with a real added file. It proves refusal by snapshot. It does not prove counting. The refusal fires before `admitted_entries` is computed, so the case name overstates what is checked.

## 5. Masquerade analysis

**(a) Bounded counterexample: an I/O refusal passes as a counted-knowledge refusal [source-derived; not executed].** `capture()` opens each file with `os.open`. An `OSError` there is re-raised as `Refusal("unreadable measured input: %s" % exc)`, and `str(exc)` embeds the absolute path, which ends in `…/corpus/knowledge/r20-input-binding-added.md`. Run as a non-root user, `os.chmod(<sandbox>/corpus/knowledge/r20-input-binding-added.md, 0)` after the write produces exit 2, the path on stderr, empty stdout, and no output file. The predicate is therefore true and the CASE reports pass, although the reason is `EACCES`. A file removed between the `os.walk` listing and `capture` yields `FileNotFoundError`, with the same tuple. Root ignores mode 0, so this variant needs a non-root run.
- Hardening: match the snapshot text rather than a substring. For this case the caller prints exactly `added=['corpus/knowledge/r20-input-binding-added.md']`. Require `measured inputs differ` and that `repr(changed_path)` appear inside the `added=[…]` segment. An `unreadable measured input` message then fails.

**(b) Decoy redirect: not a masquerade today.** If a caller regression stopped stripping `GIT_*`, the first failing step would be the helper-bytes check. `git show <decoy HEAD>:tools/souji-rev-pin.py` exits 128, because the decoy contains only `decoy-only.txt`. That raises `CalledProcessError` with no path, so the predicate fails and the regression is detected. If the decoy were seeded with the helper, a redirected run would list the whole closure in `added=`, including the changed path, and would masquerade. [INFERENCE for the seeded variant]

**(c) Fixture-level blocking shares exit code 2.** Distinguish it by `SUMMARY … blocked=1` and a `prerequisite` line. A blocked run emits no r13 case and aborts the later callers, the baseline pairs and the historical counters.

**(d) Same predicate weakness in a sibling case.** `helper-syntax-invalid` never reaches `exec_module`, because `helper.read_bytes() != committed` raises first. The SyntaxError path is not exercised, yet the predicate still passes on the substring `tools/souji-rev-pin.py`.

## 6. Baseline producer witness

- **`--baseline 31984f47…`: blocked, not a witness.** The caller and 13 of the 23 closure inputs are absent at that commit. `run_baseline_pairs` → `path_list_at_revision` → `run_git("show", …)` raises `FixturePrerequisite`, and the run exits 2. Even past that point, `make_overlay_sandbox` would raise "baseline lacks shared pair input".
- **`--baseline 12516f7d…`: valid by source.**
  - Old caller: `MEASURED_PATHS` has 12 entries, with no `corpus/knowledge`, no `corpus/SOURCES.md`, no helper and no prior. Its `execute()` still globs `corpus/knowledge/*.md` into `admitted_entries`. That is counted but unmeasured input, which is the C2 defect.
  - Old `resolve_durable` has no `input_snapshot`. Its only tree check is `git diff --quiet <rev> -- <12 paths>`, which covers tracked files only. The baseline sandbox is clean on those paths, so the helper returns the revision. `execute()` then reaches its first `run("evidence-selftest", …)`, which the tripwire replaces with `ProducerReached("baseline-r13-new-knowledge")`: status `producer`, output absent.
  - Current caller in the overlay sandbox: refuses as in §1, with exit 2, the path on stderr, empty stdout and no output.
  - All 23 inputs are present at 12516f7d and none is a symlink or submodule. Both legs are non-vacuous.
- `BASELINE_MISMATCH` lines do not change the exit status; `summary()` ignores them.

## 7. Operability notes for L1

1. **A default run reads the working tree, not the pin.** `expand_closure(root, …)` and `choose_existing_admitted(root)` read the lane's files, and so does `census/round-13/verification.json`. For a pinned verdict, run the fixture from a clean `git clone --no-local` checked out at 1988860.
2. **Whole-run blockers (exit 2):** a missing or symlinked closure path in the working tree; no admitted `.md` in the working-tree `corpus/knowledge` (at the pin, `dupe-finders-detect-then-act.md` qualifies); `corpus/knowledge/r20-input-binding-added.md` already present; `census/round-13/verification.json` absent.
3. **Interpreter.** The helper uses `hashlib.file_digest`, which needs Python 3.11 or later. The fixture does not check this. I did not verify the host interpreter.
4. **Failure-path residue [INFERENCE].** If the refusal regresses, the caller runs its suite. `run()` uses `start_new_session=True`, and the fixture's `subprocess.run(timeout=90)` kills only the direct child, so descendants survive. The `sources-contract` entry runs `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin` against the lane.
5. **`run_historical_counters`** runs `census/round-13/count-claims.py` against the live root (`cwd=root`), outside any sandbox. I did not inspect that script, so its write behavior is unverified.
6. **Residual race, declared out of boundary.** `admitted_entries` is read between the start and end snapshots, and only the endpoints are compared. A transient A→B→A change during the run yields `input_sha256` for A with `admitted_entries` from B. The helper docstring states that "filesystem races stay outside" the boundary. No case covers it.
7. **Baseline REV.** The caller's `BASE` (31984f47) is not a valid `--baseline`. The operator must pass the preregistered `12516f7d…`.
8. **r14** was not inspected. No knowledge requirement is asserted for r14, and the r14 plan has no knowledge-added case.

## 8. Answers

- **Behavioral or wiring?** Behavioral for the refusal, via a real subprocess of the real entrypoint. Wiring only for coverage (`covered_by_measured`, AST). Counting is not exercised.
- **Can a prerequisite refusal masquerade as the required reason?** Yes, through I/O errors whose message embeds the same path (§5a). This case's readable 0644 mutation does not trigger it. The weakness is in the predicate, not in the caller.
- **Is the input consumed by this caller?** Yes, twice: by the snapshot (the refusal) and by the `admitted_entries` glob. Closure parity holds.
- **Proposed hardening (one predicate change):** require `measured inputs differ` and an `added=[…]` segment containing `repr(changed_path)`. Keep exit 2, empty stdout and output-absent.

Installs or updates: none. Checks for L1 to run: the default-mode fixture from a clean 1988860 clone, expecting `CASE pass r13-counted-knowledge-added`; and `--baseline 12516f7dcdd5b165e5ee208d44a38d63b5bd5812`, expecting `baseline-r13-new-knowledge` to pass.
