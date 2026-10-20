# R15 w1 — OutputLeak (sentinel): secret-value exposure in config refusal output

Seat: `SoujiR15.OutputLeak`. Axes: operability and calibration.

Method: I read the source only. I ran no tests, probes, or edits outside this report.
- Target: `tools/souji-census.sh`, sha256 `fcff8b05…aee9`. This is byte-identical to HEAD `cc21683`, so ConfigRepair had not landed when I read it. `tests/fixtures/r15-census-config.py` does not exist yet.
- Everything about the **repair** is therefore **design-only**. Findings about the baseline cite exact lines.
- Primary docs: `man git-config` (git 2.55.0). Static `strings` extraction of the installed git binary to get exact error format strings. I did not execute git config or status.
- I did not open any credential file, `agent.db*`, or the operator sweep.
- Tool installs: none.

## Baseline status (r14 refusals, verified by reading)

The r14 refusal path is value-blind in what it outputs:
- Keys are read with `--name-only` (`:500`).
- The refusal prints only `reason`, `label=$dir` and `path=$cfg` (`:160-163`, `:506`).
- Every git config read and status call discards stderr: `:500`, `:511`, `:688`, `:694`, `:698`, `:702`, `:716`.
- Repo-local `trace2.*` is ignored. man git-config says: "Trace2 config settings are only read from the system and global config files; repository local and worktree config files and -c command line arguments are not respected."
- Global and system config are `/dev/null` (`:122`), and all `GIT_*` variables (including `GIT_TRACE*`) are scrubbed (`:119`). So git has no trace sink for argv or values.

The repair must keep every one of these properties. The findings below are what the move to value-aware checks puts at risk, plus two defects already present in the baseline.

## Findings

### OL-1 — HIGH (C1 operability; baseline): value-blind glob matches across key lines → false refusals of benign repos

- **Evidence:**
  - `:500` collects every key as one newline-joined string.
  - `:503` lowercases the whole string.
  - `:505` matches patterns such as `*remote.*.promisor*`, `*include.*` and `*filter.*.clean*` against that single string.
  - In a bash `case` pattern, `*` also matches newlines, and subsection names (branch and remote names) are included in the string.
- **Exploit or harm path (benign configs refused with exit 2, which kills the whole census at `:986`):**
  - A repo that has `remote.origin.url` and a branch named `promisor-fix` contains `…remote.origin.url\n…branch.promisor-fix.merge`. That matches `*remote.*.promisor*`, so the repo is refused.
  - Branch `fix/include.docs` produces `branch.fix/include.docs.remote`, which matches `*include.*`.
  - `filter.lfs.required` plus branch `cleanup` produces `…filter.lfs…\n…branch.cleanup.merge`, which matches `*filter.*.clean*`.
- **Impact:** one benign repo in a mixed fleet blocks every row. This is the same class of harm as the rejection r14 received.
- **Smallest remediation:**
  - Classify per line.
  - Split each key into `section`, an optional `subsection` (everything between the first and last dot), and `variable`.
  - Match only on `section.variable`, for example `remote/promisor`, `filter/clean`, `include/path`, `includeif/path`.
  - Never match on the subsection text.
- **Acceptance (fixture):** green control repos with branches `promisor-fix`, `fix/include.docs` and `cleanup`, plus a benign `remote.origin.url`. On the r14 baseline the same command must go red on these rows.

### OL-2 — HIGH (design-gating, leak): subsection names can carry credentials; refusal text must never echo parsed keys

- **Evidence:** git config keys put user data in the subsection. man git-config documents `includeIf "hasconfig:remote.*.url:<pattern>"`, and its example is `https://example.com/**`. Keys such as `url."<base>".insteadOf` and `http."<url>".extraHeader` also embed URLs. `git config --name-only` (`:500`) returns those subsections verbatim.
- **Exploit (synthetic):**
  - `[includeIf "hasconfig:remote.*.url:https://u:SOUJI-R15-CANARY@example.invalid/**"] path = x.inc`
  - `[url "https://u:SOUJI-R15-CANARY@example.invalid/"] insteadOf = gh:`
  - If the repair reports *which* key triggered the refusal by printing the parsed key, as in `git-config-unsupported (includeif.hasconfig:remote.*.url:https://u:…@…/**.path)`, the token reaches stderr. Stderr is captured into CASE lines, logs and evidence.
  - The same leak happens if a value is printed: a `filter.*.clean` / `core.alternateRefsCommand` command string, a remote URL with userinfo, or an `includeIf` condition.
- **Smallest remediation:**
  - Refusal reasons come only from a **fixed allowlist of family tokens**, for example `git-config-unsupported:includeif.path` or `:filter.clean`.
  - The third field stays `$cfg`, which is what the baseline prints.
  - No parsed key, subsection or value is ever interpolated into `protected_fail` or any other printf.
  - Update the boundary header (`:85-91`) so it says refusal output names the effect family, not the key or value.
- **Acceptance (fixture):**
  - Put a distinct canary in the subsection and in the value of every family that is refused or evaluated: `include.path`, `includeIf` condition and path, `filter.<n>.clean|smudge|process`, `core.hooksPath`, `core.attributesFile`, `core.excludesFile`, `core.alternateRefsCommand`, `remote.<n>.promisor` with a userinfo URL, `extensions.*`, `url.*.insteadOf`.
  - Assert every canary is absent from stdout and stderr in **both** the refused and the accepted outcomes.
  - The r14 fixture checks only store-file canaries (`r14-census-boundary.py:488`, `:531`). It does not check config-value canaries.

### OL-3 — MEDIUM (leak via git stderr, design-gating)

- **Evidence:** the installed git binary contains these format strings:
  - `bad boolean config value '%s' for '%s'`
  - `bad numeric config value '%s' for '%s' in file %s: %s`
  - `cannot fork to run external filter '%s'`
  - `external filter '%s' failed`
  - `read from external filter '%s' failed`

  So git echoes the raw value or filter command on stderr.
- **Exploit:**
  - The repair reads "false promisor" with `git config --type=bool --get remote.o.promisor` while stderr is visible or captured with `2>&1`. A non-boolean value such as `SOUJI-R15-CANARY` is then echoed.
  - Or the repair allows "safe clean filters" and drops `2>/dev/null` from `count_dirty` (`:716`). A failing filter then echoes its full command line, including any embedded token.
- **Smallest remediation:**
  - Every new value read keeps `2>/dev/null`.
  - A nonzero exit maps to a fixed refusal token, never to the captured text.
  - `count_dirty` keeps `2>/dev/null` and returns `unverifiable` (`:716-718`).
  - No `2>&1` into any variable that is later printed.
- **Acceptance (fixture):**
  - `remote.o.promisor = SOUJI-R15-CANARY` (not a boolean) → exit 2 with a fixed token, canary absent. It must not be treated as safe-false.
  - If filters are admitted: a filter command that exits nonzero and contains a canary → row `dirty=unverifiable` or a fixed refusal, canary absent.

### OL-4 — MEDIUM (baseline, extended by repair): `protected_fail` prints raw config-derived paths without escaping control characters

- **Evidence:**
  - `:342` and `:352` call `protected_fail "ambiguous-path" input "$raw"` with the **raw** string, including the `\n`, `\t` or `\r` that triggered the refusal.
  - `:359`, `:378`, `:383` and `:398` print lexical or raw paths.
  - Nothing filters ESC or other C0 control characters.
  - A config-derived value reaches this sink today: `core.worktree` (`:511` → `:520` `guard_target core-worktree "$dir/$wt"`).
  - The repair's "boundary-check reachable include paths BEFORE read" will route `include.path`, `includeIf.*.path`, `core.hooksPath`, `core.excludesFile` and `core.attributesFile` values through the same `guard_target` → `protected_fail`.
- **Exploit (synthetic):** `git config core.worktree "x\nsouji-census: path-protected: ok"`. git config escapes `\n` inside a value. Stderr then carries a forged line that looks like a finding. An ESC sequence in a value can also rewrite what the operator's terminal displays. This is a calibration defect: printed findings are not trustworthy.
- **Smallest remediation:** in `protected_fail` (`:160-163`), render `$2` and `$3` with control characters replaced (`${s//[[:cntrl:]]/?}`) or with `printf %q`. For `ambiguous-path` from a config source, print the label and `$cfg` instead of the raw value.
- **Acceptance:** a `core.worktree` or `include.path` value containing `\n` and ESC → exactly one stderr line, no raw ESC byte, and still exit 2 with `ambiguous-path`.

### OL-5 — MEDIUM (design): argv exposure of command-typed or URL values

- **Risk:** values passed as arguments to external processes are visible in `/proc/<pid>/cmdline` and in the r14 PATH-spy argv logs. The r14 fixture records git argv, and its CASE lines print matching spy hits. Two ways the repair could do this:
  - neutralize by echoing copied values back as `-c key=<value>`;
  - pass a filter, alternateRefsCommand or URL value to `stat`, `readlink` or `git` as an argument.
- **Bound:** stat-ing a path-typed value (an include target) is inherent and acceptable. Command-typed and URL-typed values must never become argv.
- **Remediation:** neutralize with **constant** overrides only, as the existing pattern does at `:710-712` (`-c core.hooksPath=/dev/null`, and so on). Command and URL values are classified inside the shell and never exec'd or passed on.
- **Acceptance:** command-typed and URL canaries are absent from the spy argv log.

### OL-6 — LOW (residual; caller-trusted environment): inherited shell tracing

- **Evidence:** `:108-123` clears `GIT_*` variables and shell functions, but not `SHELLOPTS` or `BASH_XTRACEFD`.
- **Risk:** once the repair keeps config values in shell variables, an inherited exported `SHELLOPTS=xtrace` traces every expansion of those values to stderr. `BASH_ENV` runs before the script starts and cannot be fixed inside it.
- **Remediation:** add `set +x` after `set -euo pipefail`. This is cheap and has no effect on behaviour.
- **Cross-ref:** GitEnvironment lane. If promisor=true is ever admitted, `GIT_NO_LAZY_FETCH=1` is not re-exported after the `:119` scrub. A repo-local `credential.helper` (not refused) could then run on a lazy fetch, with its stderr hidden. That belongs to the PromisorSafe and CommandInjection lanes, so I only note it here.

## Acceptance needed from ConfigRepair / ConfigFixture (for L1; none run by me)

1. `grep -nE 'protected_fail[^#]*\$(key|k|name|val|value|v|line)\b' tools/souji-census.sh` → 0. Refusal fields are fixed tokens plus `$dir`/`$cfg` only.
2. `grep -nE 'git config[^#]*--get[^#]*$' tools/souji-census.sh`: every hit must carry `2>/dev/null` on the same logical command. Also, `grep -n '2>&1' tools/souji-census.sh` must show no new hit outside the selftest.
3. `protected_fail` sanitizes control characters (OL-4).
4. A fixture case in `r15-census-config.py` must cover:
   - per-family subsection and value canaries (OL-2);
   - a non-boolean promisor canary (OL-3);
   - a control-character path value (OL-4);
   - command and URL canaries absent from spy argv (OL-5);
   - benign branch-name controls `promisor-fix`, `fix/include.docs` and `cleanup` (OL-1), which must be **red on the r14 baseline and green on the repair**.
5. The r14 boundary fixture must still pass on the repaired tool (namespace gains kept).

## Not checked

- I did not check the repair diff itself, because it was not present.
- No runtime confirmation of git's stderr wording beyond the static format strings.
- No check of whether `git config --name-only` normalizes subsection case. The tool lowercases at `:503` in any case.

## Boundary disclosure (added after SoujiR15's no-query reminder)

Two of my calls searched recursively under the lane root and may have scanned the OPERATOR-authored `census/operator-sweep-20261019/` tree. That directory is untracked, not gitignored, so the search's gitignore filtering would not have excluded it. I will not repeat these calls.

1. A `grep` with pattern `refus|config.*(value|secret)|redact` and path = the whole lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`.
   - The output I saw was truncated at 413 of 432 lines.
   - None of the visible matches came from the operator sweep.
   - The 19 lines I did not see were never read.
2. A `grep` with pattern `git-config-unsupported|path-protected: ` and path `census;corpus;LOG.md`. This searched `census/` recursively.
   - Only matches in `census/round-15/lesson-draft.md` and `corpus/lessons/round-14-verifier-spotcheck.md` were returned.
   - No operator-sweep content was returned.

Other calls that touch the boundary:
- `git status --short` listed the directory *name* `census/operator-sweep-20261019/` (no contents).
- `ls census/round-15/` listed only that directory.
- I ran `strings -n 12 $(command -v git) | grep …` once. It reads the installed git binary statically and executes no git behaviour. It may still fall under the "no empirical probes" rule.

None of these calls opened, copied, edited or moved any operator-sweep file. Every finding in this report rests on `tools/souji-census.sh`, `tests/fixtures/r14-census-boundary.py`, the round-15 spec, and `man git-config`.
