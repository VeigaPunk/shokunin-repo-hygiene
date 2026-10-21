# R20 C2 — actual-caller input-binding oracle

## Scope and implementation

Added only `tests/fixtures/r20-input-binding.py` in my assigned private worktree. The fixture parses literal `MEASURED_PATHS` / `DEMO_MEASURED_PATHS` and copies only those bounded closures from `--root` into synthetic Git repositories under `/var/tmp`; Git identity is fixture-only and hooks/automatic maintenance are disabled (`tests/fixtures/r20-input-binding.py:42-65,150-250,291-412`). Default `--root` is the repository containing the fixture; `--root PATH` selects another source root.

Each actual caller gets a committed sandbox and isolated inert mutations. The helper tests cover clean snapshot/durable resolution, HEAD/branch/short/keep-only controls, a monkeypatched walk error, `GIT_DIR` redirection, and `input_snapshot(root, ..., ["census"])` with Git/walk sentinels that must remain untouched. Dirty caller arms require exit 2, the changed path in the refusal, no evidence file, and no suite stdout. The demo must return 2 on stderr with empty stdout (`tests/fixtures/r20-input-binding.py:595-816`).

With `--baseline REV`, the fixture records each bounded source-byte mismatch by path and SHA-256, then runs seven old-vs-current actual-entrypoint pairs. Both arms use the same baseline-source input corpus; only the caller/helper implementation bytes under test differ. Each pair imports the entrypoint's real `main`, replaces its measurement producer (`module.run`, nested `targeted.module.run`, or `demo.run_demonstration`) with a named `ProducerReached` tripwire, and asserts current refusal/no producer versus baseline tripwire reach. `BASE` is pinned to each synthetic sandbox commit. No suites run in those pairs (`tests/fixtures/r20-input-binding.py:525-594,818-913`).

## Exact expected CASE inventory

- Helper controls (9): clean `input_snapshot`, clean durable resolve, `HEAD`, branch, short ID, keep-only ref, monkeypatched walk-error refusal, protected `census` ancestor refusal with zero Git/walk calls, and clean resolution under foreign `GIT_DIR`/`GIT_WORK_TREE`/index selectors (`tests/fixtures/r20-input-binding.py:446-524,595-631`).
- r13 actual caller (8): dirty helper, syntax-invalid helper, own wrapper, frozen input, `SOURCES.md`, an existing admitted knowledge file, a newly added counted knowledge file, and the optional prior file.
- r14 actual caller (5): dirty helper, syntax-invalid helper, own wrapper, frozen input, and `SOURCES.md`.
- r14 targeted actual caller (6): the r14 set plus its prior-attempt input.
- Cache demo actual caller (4): dirty helper, syntax-invalid helper, own wrapper, and its measured historical r13 input.
- Historical counter arms (4), all using full 40-hex IDs: r13 `31984f473ce4bdab61a99b16cca194b28108cb81`, r13 `6f8ee0f38a14a3cb599ee606c486a55ec64e8ae6`, r14 `a31642d14006830ec62edf40b0354c3699728c4a`, and r14 `552cae4204b3ab818419ad8adbfef3a4da29a3e0` (`tests/fixtures/r20-input-binding.py:915-966`).

The exact case-ID set is asserted at summary time (`tests/fixtures/r20-input-binding.py:92-143`). Without `--baseline`, the success inventory is 36 CASEs; `\t` denotes one literal tab in these expected output lines:

```text
INVENTORY\texact\texpected=36\tobserved=36\tmissing=-\tunexpected=-\tduplicates=0
SUMMARY\ttotal=36\tpass=36\tfail=0\tblocked=0\tinventory=exact\tbaseline_mismatches=not-requested
```

With `--baseline 12516f7dcdd5b165e5ee208d44a38d63b5bd5812`, the seven producer-tripwire pairs (`baseline-r13-helper`, `baseline-r13-sources`, `baseline-r13-new-knowledge`, `baseline-r14-helper`, `baseline-r14-frozen`, `baseline-targeted-wrapper`, `baseline-demo-helper`) raise the exact inventory to 43. Expected fields are `INVENTORY\texact\texpected=43\tobserved=43\tmissing=-\tunexpected=-\tduplicates=0` and `SUMMARY\ttotal=43\tpass=43\tfail=0\tblocked=0\tinventory=exact\tbaseline_mismatches=<observed count>`. The mismatch count is runtime-derived; each source difference remains a `BASELINE_MISMATCH` record, not a pass.

## Source evidence and falsifiable findings

- Preregistration `.ufo/waves/round-20/preregistration.txt:3` requires per-caller refusal for dirty helper/wrapper/frozen/source-admission inputs, a newly counted knowledge path, clean snapshot positive, strict revision controls, and full-ID historical counters.
- The R19 rejection `corpus/lessons/round-19-verifier-spotcheck.md:78-88` identifies omitted helper/wrapper/frozen/corpus bytes, absent caller-level refusal evidence, short-ID command contraction, and ambient Git repository-selection as an unexercised inference. It explicitly distinguishes those unproved claims from the narrower receipts.
- The current r13 closure and source/admission reads are visible in `census/round-13/run-verification.py:92-141,477-499`; r14's closure and snapshot receipt are in `census/round-14/run-verification.py:32-73,120-163`. The targeted wrapper adds `verification-attempt-1.json` before resolving (`census/round-14/run-targeted.py:20-25,46-52`). The demo's measured closure and durable snapshot calls are in `census/round-14/cache-demonstration.py:80-90,179-207`; its changed-input refusal returns exit 2 before opening the isolated demo (`:1144-1148`).
- The helper API validates bounded tree/blob bytes and working regular leaves in `tools/souji-rev-pin.py:94-179`, then combines that snapshot with full-ID/durable-ref rules in `:182-228`. Its environment setup drops inherited `GIT_*` repository selectors (`:47-61`). The fixture's walk and protected-ancestor controls use only synthetic paths and injected callbacks (`tests/fixtures/r20-input-binding.py:446-484,595-631`).
- Historical receipt examples remain the source of expected inventory values: `census/round-13/counts.json:1-21` and `census/round-14/counts.json:1-23`. Those saved r13 commands display abbreviated selectors; this fixture deliberately invokes both counter CLIs with the full IDs. The current r14 counter uses bounded `tools`, `tests/fixtures`, `corpus/knowledge`, and `corpus/SOURCES.md` pathspecs (`census/round-14/count-claims.py:35-48`); r13's counter is bounded to `tools` and corpus paths (`census/round-13/count-claims.py:34-48`).

## Execution status, risks, and blockers

**Not executed by this seat.** This was an authoring-only wave; I did not run the fixture, tests, suites, linters, formatters, or target code. The CASE list and summaries above are expected assertions, not observed results. L1 should run `python3 -B tests/fixtures/r20-input-binding.py --baseline 12516f7dcdd5b165e5ee208d44a38d63b5bd5812` after integrating this file. Expected inventory is 43 cases; baseline mismatch count remains runtime-derived. Historical-revision availability in a caller-supplied `--root` remains a prerequisite; no missing history is represented as a pass.

No blocker to the scoped implementation. No tool was installed or updated. LSP was not available in the mounted tool inventory, so findings use source reads and static AST inventory only.
