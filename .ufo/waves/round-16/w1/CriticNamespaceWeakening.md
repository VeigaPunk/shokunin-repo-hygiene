# C1 namespace-retention critique

Axis: **operability**, including retention of r14's pre-access protected-namespace boundary and whole-run exit-2 refusal. Advisory source review only; no census, fixture, runtime, or acceptance command executed. All `tools/souji-census.sh` line references below are at `cbf688ab2ab28e38103e5a9417ca525b5f2ed423` unless explicitly marked otherwise. Synthetic paths below describe counterexamples; none were created or accessed.

STATUS: Source review identifies a definite soft-refusal precedence defect and multiple newly exposed access paths; runtime outcomes are [INFERENCE], not measured failures. C1's namespace-retention claim is not established by the supplied matrix.

## 1. A soft config error hides a subsequent protected reach

**Counterexample:** valid `.git/config` containing these records in this order (HOME is a synthetic `/var/tmp/H`):

```ini
[include]
    path = ~root/unsupported.cfg
    path = /var/tmp/H/.omp/agent/secret.gitconfig
```

The first pathname returns soft failure at lines 611–612. `scan_config_file` stops immediately, so the second pathname never reaches `guard_config_path` at line 614. `guard_git_config` propagates the soft return (lines 679–683), `guard_git_surface` stops at line 773, and `census_one` emits an `error` row and returns zero (lines 1087–1093). `emit_census` subsequently succeeds. [INFERENCE] Thus a config carrying a protected include changes from cc21683's whole-run exit 2 to exit 0 merely by prepending an unsupported spelling. A FIFO or hardlinked first include gives the same masking at line 616.

This also masks **independent metadata protections**: soft failure at line 773 precedes `commondir` checks (775–790), alternates (793), and registered worktrees (794). A protected alternates/commondir/worktree target need not be checked at all once a config soft-fails.

**Baseline evidence:** cc21683 `tools/souji-census.sh:493–506` parses keys without includes and exits 2 on any include key. Its surface guard propagates that refusal at lines 613/628/650/665. No target content is needed for this comparison.

**Smallest safe correction:** make soft failure sticky rather than terminal. Continue checking independently evaluable records and metadata surfaces; skip only the unevaluable subtree, then emit the per-repo error after all reachable protected-target checks. This preserves the intended benign degradation without letting it outrank a protected reach. An unparseable entire file still cannot reveal its hidden records; distinguish that limitation from skipping already available records.

## 2. Resolving an included filename destroys Git's relative-include origin

**Counterexample layout:** main config includes `/var/tmp/A/link.cfg`; `A/link.cfg` is a symlink to `/var/tmp/B/body.cfg`. `B/body.cfg` contains `[include] path = leaf.cfg`. `B/leaf.cfg` is absent or benign. `A/leaf.cfg` contains an absolute include of `/var/tmp/H/.omp/agent/secret.gitconfig`. All non-store files are regular single-link files; the symlink is outside `.git`.

**Evidence:** lines 611–617 expand the named path, replace it with its fully resolved target, and pass only that resolved filename recursively. Line 611 subsequently bases nested relative includes on `${cfg%/*}`, now `/var/tmp/B`. The guard validates B/leaf.cfg instead of A/leaf.cfg. The actual config readers later run without `--no-includes`, e.g. line 876 and lines 910–911.

**Git-semantics inference:** Git resolves a relative include against the pathname of the including config as opened, not the final symlink target's directory. Consequently Git follows A/leaf.cfg and attempts to open the protected target which the guard never scanned. This holds whether the secret file parses: even a denied/failed open violates the pre-access boundary. The Git implementation was not independently fetched in this seat; the exact syscall outcome remains [INFERENCE]. cc21683 refuses the top-level include key before following this chain.

**Smallest safe correction:** carry two identities: the guarded/resolved file used for safe reads and cycle detection, and the original expanded include pathname used as Git's relative-include origin. Guard every derived target before opening it. Simply applying realpath everywhere changes semantics rather than fixing the mismatch.

## 3. Filter binding probes omit the fsmonitor neutralizer

**Counterexample:** a repo has a nonempty, unbound `filter.x.clean` plus `core.fsmonitor = /var/tmp/H/.omp/agent/monitor`. The index contains a tracked file. cc21683 refuses the filter key. cbf688 admits it and reaches the new index readers.

**Evidence:** `guard_bound_filters` detects driver definitions at lines 910–920, then invokes `ls-files --cached` and `check-attr` at lines 922–925 with only a `core.attributesFile` override. Unlike status (lines 947–949), neither command carries `-c core.fsmonitor=false` or the hooksPath neutralizer. The fixture's fsmonitor sentinel repository has no filter driver (`tests/fixtures/r15-census-config.py:397–400`), while the bound-filter repositories do not combine fsmonitor (`:498–513`); those separate controls do not exercise this interaction.

**[INFERENCE]:** Git index loading can initialize/refresh fsmonitor, which can execute a configured fsmonitor hook. The new readers therefore expose an execution route not covered by the status-only override; exact firing depends on Git/index state and was not probed here.

**Smallest safe correction:** apply the same fsmonitor/hooksPath overrides to **both** newly added index-reading commands. This does not require rejecting benign filter declarations or changing dirty semantics.

## 4. `check-attr` receives protected tracked paths with no boundary/pathspec filter

**Counterexample:** the index contains `.ufo/state/deep/file`, and the worktree has `.ufo/state/.gitattributes`; config defines any nonempty unbound filter driver. An equivalent case uses a synthetic `census/operator-sweep-X/file` entry. No actual operator directory was inspected.

**Evidence:** lines 922–925 feed **all** cached paths to worktree-reading `check-attr`, with no exclusions or component walk. The later status command alone has the protected pathspec exclusions (lines 949–954). `check-attr` needs ancestor `.gitattributes` sources for each pathname; [INFERENCE] it can attempt an open inside the protected directory before status's exclusions matter. A tracked directory replaced by a leading symlink toward the store is another exposure candidate; do not assume final-component symlink refusal protects leading components. cc21683 never reaches this new probe because it refuses the filter definition.

**Smallest safe correction:** restrict the binding probe to status's eligible path domain and guard worktree attribute-source ancestry before any probe access. `check-attr --cached` alone is **not** an equivalent fix: it misses modified/untracked worktree attribute bindings and could allow a driver to run during status. Blindly skipping every repo with any driver also sacrifices the explicitly claimed unbound-driver restitution. These tradeoffs require correction, not silent acceptance as a Pareto improvement.

## Hardlinks, tilde, XDG, and config.worktree scope notes

- Include/config.worktree targets have an explicit single-link gate (`guard_config_file_kind`, lines 556–568; callers 616/663). Direct symlink-to-store includes pass through the component guard before that gate. `~/` expands through HOME; `~user`/`%(prefix)` soft-fail. Those direct cases do not supply an additional bypass beyond the precedence defect above.
- Config-named attributes/excludes and XDG defaults lack that single-link check (lines 619–624 and 874–900). A benign-path hardlink to a store inode can therefore be newly read where cc21683 refused the explicit key or forced `/dev/null`. This is **inode aliasing**, not proof of an access naming a protected pathname. The header already documents arbitrary hardlinks as a residual; do not falsely present this as a newly discovered path-based bypass. A conservative single-link check on these newly honored input sources would reduce that residual without statting the store.
- XDG default targets are guarded and replaced by `/dev/null` on failure (lines 894–900); an explicit store path there does not itself prove store access. Suppressed refusal from a failing resolver is local to that optional default.
- `CFG_WT_ENABLED` is mutated while recursively scanning includes (lines 617/633–638) and while scanning config.worktree itself. [INFERENCE] This should be compared with Git's repository-format `extensions.worktreeConfig` activation, not assumed to be ordinary include-expanded last-wins config. A raw common config enabling it followed by an included disabling value is a missing adversarial interaction. This seat did not read Git's repository-format implementation, so this is a bounded follow-on risk, not a confirmed additional failure.
- No new store-path-output leak is established here. The new redaction at lines 185–192 improves the old refusal printer; access/refusal findings above do not depend on printing secret content or paths.

## Disposition

These are fixable implementation defects/candidates in the newly expanded config/status surface, not a reason to abandon value-aware restitution. The strongest entirely local counterexample is **soft error before a protected include or metadata target**. Keep the source-inferred access candidates separate from measured evidence; the existing 20/20 and 12/12 do not establish their absence. L1 alone owns acceptance and integration.

No tools installed/updated. No code edits, commits, census execution, or test execution. Only this owned report was written.

## Commands

Every shell command run, verbatim:

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat cc21683 cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff cc21683 cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cc21683:tools/souji-census.sh
```
