# InputCase03 — `r13-wrapper-dirty` exact C2 falsifier (read-only, source-only)

STATUS: PARTIAL — blocking for `r13-wrapper-dirty` as an exact falsifier. Its predicate can PASS on an r13 runner that refuses every clean run, because a refusal that spells the wrapper path oddly still names that path (F1, source-derived counterexample, not executed). The pinned runner refuses the dirty wrapper correctly by source; I found no pinned-caller defect. The fix is fixture-side (F1, fixes 1 and 2).

## Scope

- Pin: `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`. Baseline read for witness analysis: `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`.
- Read via `git show`, `git ls-tree`, `git cat-file`, and three working-tree queries (two `git diff --name-only`, one `git status --porcelain`; all with `GIT_OPTIONAL_LOCKS=0`; the status call is disclosed in §7). Files: `tests/fixtures/r20-input-binding.py`, `tools/souji-rev-pin.py`, `census/round-13/run-verification.py`, and the baseline counterparts of the last two.
- Nothing executed. No fixture, runner, or helper imported or run. Every behaviour below is source-derived; nothing was observed.
- Applicable caller only: `census/round-13/run-verification.py`. r14, targeted and demo callers not examined.

## 1. Trace of the case

- **Entrypoint.** `caller_command` (kind `r13`): `python3 -B census/round-13/run-verification.py --round 20 --output census/round-20/r20-r13-wrapper-dirty.json --retry-failed --previous census/round-13/verification.json`. Run with cwd = sandbox `<tmp>/r13`, env = `CLEAN_ENV` plus decoy `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, timeout 90 s.
- **Inert byte.** `mutation_plan` entry `("wrapper-dirty", ROUND13, False)` → `mutate_and_call` → `inert_suffix(".py")` appends `\n# inert r20 input-binding mutation\n` after runner line 522 (`sys.exit(main())`). Original bytes are restored in `finally`. The mutation is a comment and syntax-neutral.
- **Closure.** `parse_path_list` reads the runner's `MEASURED_PATHS` (runner lines 92–115; wrapper at line 104), plus `r13_extras = [census/round-13/verification.json]`. The runner adds the same file as `PREVIOUS_SOURCE` (lines 137–138). Sandbox = those bytes in one synthetic commit; `census/round-20/` is created after the commit and is empty.
- **Runner order.** `main` (405) → `validate_output` (342–381) → `validate_previous` (384–402) → `execute` (445) → `resolve_revision` call (448) → `resolve_revision` (121–146). Nothing is written or printed to stdout before `resolve_revision`.
- **Snapshot.** Runner 136–141 calls helper `resolve_durable` (helper 182–227; `input_snapshot` call at 226) and then `input_snapshot` (helper 94–179). The wrapper is hashed by `capture` and compared to its `ls-tree` blob; mismatch raises at helper 177–178.
- **Refusal.** Runner 143–146 catches `ValueError` (helper `Refusal` subclasses it), prints `run-verification: refused: measured inputs differ from <rev> (missing=[] added=[] changed=['census/round-13/run-verification.py']) (no record written)` to stderr, and raises `SystemExit(2)`. `main`'s `except Exception` (439) does not catch `SystemExit`.
- **Predicate.** `caller_refusal`: `returncode == 2 and changed_path in (stdout + stderr) and output absent and stdout == ""`.
- **Output timing.** The evidence file is opened only at runner line 516, after the whole suite. On this path it cannot exist.

## 2. Answers to the four questions

- **Behavioral or wiring?** Behavioral. The case runs the real entrypoint in an isolated repo and checks exit code, stdout, output absence and stderr. The only wiring is `covered_by_measured` inside `mutation_plan`, which decides whether the case runs at all.
- **Can a prerequisite refusal masquerade as the required reason?** Yes. The predicate is a substring test, so any refusal that names the wrapper path with exit 2, empty stdout and no output passes, whether or not the wrapper bytes were ever read. At the pinned source no such refusal is reachable, because `mutate_and_call` asserts `is_file()` immediately before mutation and nothing else alters the file. A one-token regression makes it reachable (F1).
- **Is the input consumed by this caller?** Yes, at source: runner 104 → 136 → 140 → helper 226 → hash and compare at 172–178. The case does not prove consumption, because F1 refuses before any hashing and the case still PASSes.
- **Baseline producer witness?** None, and none can exist under the current design. None of the seven `run_baseline_pairs` pairs changes the r13 wrapper (r13 pairs: helper, sources, new-knowledge; r14: helper, frozen; plus targeted wrapper and demo helper). Structurally, at 12516f7 the same dirty wrapper also gets exit 2, empty stdout and no output:
  - The baseline runner already lists its own wrapper (baseline line 104).
  - The baseline helper refuses dirty tracked measured paths with `git diff --quiet <rev> -- paths` (baseline helper 136–141).
  - The `producer` tripwire therefore never fires (`baseline_reached` is false).
  - The only difference is the message. Baseline text is `tracked measured paths differ from <rev> (a record must not claim bytes the revision does not contain)` (baseline helper 138–140) and omits the path. By source, the baseline would FAIL this case on the named-path clause alone (F3).

## 3. Findings (severity order)

### F1 — BLOCKING: the predicate accepts a wrapper-spelling refusal (source-derived counterexample)

Mechanism:
- Fixture `safe_relative` normalizes with `PurePosixPath`. Pathlib collapses `./`, trailing `/` and `//`, so `parse_path_list` returns the canonical name. The wiring gate and sandbox construction therefore see a clean `census/round-13/run-verification.py`.
- Helper `input_snapshot` checks the raw spelling before any git call or hash: `parts = path.split("/")` and `if any(part in ("", ".", "..") ...)` raise `measured path %r escapes or is ambiguous` (helper 106–108).
- A one-token spelling edit to runner line 104 therefore makes every runner invocation refuse on clean bytes, and the refusal names the wrapper.

Counterexample (source-derived; not executed):

| Regression in runner line 104 | Runner result on clean bytes | r13-wrapper-dirty verdict |
|---|---|---|
| `"./census/round-13/run-verification.py"` | stderr `run-verification: refused: measured path './census/round-13/run-verification.py' escapes or is ambiguous (no record written)`; exit 2; stdout empty; no output | PASS (false) |
| `"census/round-13/run-verification.py/"` | stderr `... measured path 'census/round-13/run-verification.py/' escapes or is ambiguous ...`; exit 2 | PASS (false) |
| entry removed | `mutation_plan` raises `FixturePrerequisite` (wiring gate); `main` returns blocked, exit 2 | not a PASS; whole matrix aborted (F5) |

- In the first two rows the case reports PASS while the caller refuses every run.
- The sources, frozen, admitted-knowledge, counted-knowledge and optional-prior cases FAIL under the same regression, because their paths never appear in the spelling message. The run looks mostly red, but this case still reads green.
- `r13-helper-dirty` and `r13-helper-syntax-invalid` still PASS correctly: the helper byte check (runner 131–132) runs before the spelling check and names the helper. Only the wrapper case PASSes wrongly, because its own dirty input is reached only inside `input_snapshot`, after the spelling check.
- The same normalization blindness applies to all four callers' path lists, so spelling drift in any of them is invisible to wiring.

Fix (fixture only, bounded):
1. In `parse_path_list`, reject any raw literal where `value != PurePosixPath(value).as_posix()` or where `value.split("/")` contains `""` or `"."`. This makes the wiring gate fail closed on spelling drift. The pinned r13 list is canonical (all 22 entries checked), so this does not block the pinned state.
2. Tighten the dirty clause for the wrapper to the typed snapshot refusal: `measured inputs differ from [0-9a-f]{40} (missing=[] added=[] changed=['census/round-13/run-verification.py'])`, with the path passed through `re.escape`. The substring test is the weak point.

### F2 — MEDIUM (residual after F1): clean over-refusal naming the wrapper still passes

- A caller regression that makes the wrapper's clean digest mismatch, and so emits exactly the snapshot text, would still PASS. The fixture has no caller-level clean run.
- The clean controls it does have (`helper-input-snapshot-clean`, `helper-resolve-clean`) exercise the helper on a parallel sandbox built by the same `make_sandbox(r13_paths, r13_extras)` call. They do not exercise the caller's own composed list or its refusal path.
- A caller-level clean run is not cheap here. `execute` runs the full suite (including the external `sources-census.sh` and shellcheck) and writes evidence, which a falsifier must not do.
- Options: a probe that starts the clean caller, waits for its first `evidence-selftest:` line, then kills its process group; or document this as residual risk.

### F3 — MEDIUM (evidence gap, not a caller defect): no baseline witness; the only delta is the message

- The wrapper is already in the baseline boundary (baseline line 104), so the case is a regression guard for an input both versions refuse.
- Its only current-versus-baseline discriminator is the named-path clause, which the baseline message lacks (see §2). The producer-tripwire pair mechanism cannot record that.
- The C2 boundary delta for r13 is carried by other cases: `r13-admitted-knowledge-dirty`, `r13-counted-knowledge-added`, `r13-optional-prior-dirty`, `r13-sources-dirty`, `r13-frozen-dirty`, and the helper pair (the helper and the knowledge paths are absent from the baseline list).
- Either relabel this case as a regression guard (not a C2 falsifier), or record the naming delta separately.

### F4 — MEDIUM, conditional on a regression [INFERENCE]: timeout orphans

- `caller_refusal` uses `subprocess.run(..., timeout=90)`, which SIGKILLs only the direct child.
- If the runner ever reaches its suite, its children run with `start_new_session=True` (runner 279–281) and are not killed by the fixture.
- These include the external `sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` (runner 473). Whether that command is read-only was not verified.
- Fix: start the caller in its own process group and `killpg` it on timeout.

### F5 — LOW: the wiring gate is fail-stop for the whole matrix; blocked shares exit 2 with refusal

- `mutation_plan` raises `FixturePrerequisite` before any r13 case runs. `run_caller_matrix` stops, and every later r14, targeted and demo case disappears from the inventory.
- `main` returns `cases.summary(blocked=True)` with exit 2, the same code the callers use for refusal. The summary line `blocked=1` distinguishes it, but it is easy to misread.

## 4. Verified facts (source)

- Working tree equals pinned bytes for all 22 r13 MEASURED entries (including `corpus/knowledge`, `tests/fixtures/r13-cert-frozen` and `census/round-13`), the previous-evidence file, the runner, the helper and the fixture: `git diff --name-only 1988860…` over those paths is empty (exit 0). The fixture reads the working tree, so its verdict is about bytes equal to the pin.
- All r13 MEASURED entries queried exist at the pin. At baseline, the 13 MEASURED entries and the previous-evidence file I queried all exist; the nine MEASURED tool and test entries (`tools/souji-verify.sh` and similar) were not queried at baseline.
- `choose_existing_admitted` succeeds at this pin: `corpus/knowledge/dupe-finders-detect-then-act.md` has `source:`, `verified-at:`, `recheck:` on lines 1–3 and no HELD marker.
- Ambient-GIT_DIR protection is real. The runner strips `GIT_*` (runner 57–61) and the helper does too (helper `_env` 47–61). An ambient-GIT_DIR regression would refuse with a non-wrapper message, so the decoy cannot mask it.
- Host prerequisites: Python 3.14.8 and git 2.56.0 (both meet `hashlib.file_digest` and `git switch`/`init --initial-branch` requirements).

## 5. Residual risk and verification gaps

- Nothing was executed. Every behaviour above is source-derived.
- CPython's exit status for a missing script (`can't open file`, exit 2, path named) is [INFERENCE]. It is unreachable in the serial harness because `mutate_and_call` asserts `is_file()` first. It would pass the predicate if the wiring gate were removed and the runner were absent from the sandbox, which makes the gate load-bearing.
- The git behaviour of `diff --quiet <rev> -- paths` on a dirty tracked file (baseline) is [INFERENCE] from git semantics, not observed.

## 6. Operability (what works)

- The refusal path is cheap: about forty `cat-file` calls plus interpreter startup, well under the 90 s timeout.
- The per-case detail line is informative: `changed=...; exit=2 changed_path_named=1 output_absent=1 suite_stdout_absent=1`.
- The wrapper is restored byte-for-byte in `finally`, and the decoy protects the GIT_DIR surface.
- Blocking is distinguishable from refusal only through `blocked=1` (F5).

## 7. Tooling and scope disclosure

- Installs or updates: none (host version probes only: `python3 --version`, `git --version`). Subagents: none. Background jobs: none.
- Writes: this report and its directory only. No git mutation; all three working-tree queries (two `git diff --name-only`, one `git status --porcelain`) used `GIT_OPTIONAL_LOCKS=0`.
- Scope deviation (disclosed): one `git status --porcelain -- LOG.md census corpus tests tools` call included the pathspec `census`. Git therefore inspected untracked entries under `census/` and printed one name, `?? census/operator-sweep-20261019/`. I did not open, list, read or copy anything inside it, and I will not repeat a query that reaches it.
- Verification for L1 after F1 is fixed: run the fixture once (operator decision). Do not treat `r13-wrapper-dirty` as C2 falsifying evidence until then.
