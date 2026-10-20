# AttributesSafe — round 15 w1 (design + source review, advisory)

Scope: `core.attributesFile` override, in-tree `.gitattributes` effects, path reading vs clean-filter execution, preservation cases.
Axes: operability (C1), calibration (C2). Source inspected: `tools/souji-census.sh` (HEAD cc21683), `tests/fixtures/r14-census-boundary.py` (HEAD 552cae4), `.ufo/waves/round-14/w1/*`. Primary docs: git-scm gitattributes, git-config (`core.attributesFile`, `config.worktree`, `GIT_CONFIG_GLOBAL`), git(1) `-c`. Doc pages are 2.56.0; installed git is 2.55.0 (version skew noted, not checked).
No tests, probes, builds or edits were run. No tools were installed or updated.

## Findings (by severity)

### F1 — MEDIUM (operability): the `core.attributesfile` refusal buys no safety
- `tools/souji-census.sh:505` refuses any repo whose local config has `*core.attributesfile*`. Value-blind.
- `count_dirty` already runs `status` with `-c core.attributesFile=/dev/null` (L710-712). Git documents `-c` as overriding configuration files (git(1)), so the override also wins over a repo-local `core.attributesFile`, and it replaces the XDG default `$XDG_CONFIG_HOME/git/attributes` (fallback `$HOME/.config/git/attributes`) per git-config `core.attributesFile`.
- Only `status` reads worktree path attributes. `rev-list` (L698, L702), `for-each-ref` (L694), `worktree list` (L688, L836) and `rev-parse` (L859) do not do path attribute lookups [INFERENCE from command semantics; BoundaryReviewGit N5 and SafetyCredential N3 state the same, not re-verified here].
- Recommendation R1: delete `*core.attributesfile*` from L505. Keep the `-c core.attributesFile=/dev/null` on L712. Any repo with a local `core.attributesFile` (in-repo path, `/dev/null`, store path) then completes with the same rows as a repo without the key. This preserves benign configs and mixed fleets and changes no store-access result.

### F2 — HIGH (calibration, design fact): clean-filter execution is NOT controlled by `core.attributesFile`
- Path reading and execution are different channels:
  - Attributes only select a driver name. A `filter=<d>` attribute executes nothing by itself. git-gitattributes: "A missing filter driver definition in the config ... is not an error but makes the filter a no-op passthru" (gitattributes, filter section).
  - Execution needs `filter.<d>.clean|smudge|process` in the effective config. The census sets `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_SYSTEM=/dev/null`, `GIT_CONFIG_NOSYSTEM=1` (L122-123) and clears every `GIT_*` (L114-119). Git documents `GIT_CONFIG_GLOBAL` as replacing global configuration (git-config env). So the only possible driver source is the repo's own `.git/config`, which is gated by L505 (`*filter.*.clean*`, `*filter.*.smudge*`, `*filter.*.process*`).
  - The attribute source does not matter to execution. In-tree `.gitattributes`, `$GIT_DIR/info/attributes`, the XDG file or a local `core.attributesFile` can all set `filter=x`; none of them can be neutralized by `-c core.attributesFile`. The round-14 leak is exactly this: `.gitattributes * filter=x` plus `filter.x.clean` printed `LEAK via clean filter` after an mtime change, and `-c core.fsmonitor=false` did not stop it (`.ufo/waves/round-14/w1/BoundaryAttack.md`, E11 / line 131).
- Therefore: the `filter.*` refusal at L505 must stay as the execution gate, whatever is done to the attribute refusal. R2: do not relax L505 for attribute repairs. Any value-based relaxation of filter drivers belongs to the filter seat and must demonstrate that no command runs. I did not verify whether an empty `-c filter.<d>.clean=` neutralizes a driver; treat it as unverified.

### F3 — MEDIUM (operability, safe to fix): `$GIT_DIR/info/attributes` is a path-read gap
- git-gitattributes: `$GIT_DIR/info/attributes` has the highest precedence. `core.attributesFile` does not govern it, and the `-c` override does not affect it. `status` reads it.
- `guard_git_files` (L477) lists `config HEAD index packed-refs commondir info/exclude objects/info/alternates`. `info/attributes` is absent, so an `nlink > 1` hardlink to a store file is not refused. `guard_git_links` (L464-470) does refuse a symlink under gitdir that resolves outside it, so the symlink form is covered.
- BoundaryReviewGit (line 46) records this as an acknowledged residual, "no change requested this round".
- R3: add `info/attributes` to the `guard_git_files` list at L477. An absent file has no effect, so mixed fleets are preserved. Linked worktrees may store it under `worktrees/<id>/info/` [INFERENCE; not verified].

### F4 — HIGH (coupling hazard, forward-looking): `config.worktree` bypasses the filter gate
- git-config: `$GIT_DIR/config.worktree` is read whenever `extensions.worktreeConfig` is set, and it overrides `.git/config`.
- The guard reads only `$dir/config` (L495-500, `--no-includes --list`). It never reads `config.worktree`. The extension is refused at L505 (`*extensions.worktreeconfig*`), which currently blocks this path.
- If any repaired tool stops refusing `extensions.worktreeConfig`, a `filter.<d>.clean` placed in `config.worktree` would pass the L505 gate and execute during `status`. R4: un-refusing `extensions.worktreeConfig` must come with a scan of `$GIT_DIR/config.worktree` (and `worktrees/<id>/config.worktree` for linked worktrees) using the same key refusals and `--no-includes`. Otherwise keep the extension refusal. Coordinate with the ConfigRepair / PromisorSafe seats that own the extension change.

### F5 — MEDIUM (calibration): the trace oracle cannot see hardlink reads
- r14 `trace_access` (fixture L420-470) runs `strace -y` (L381) and `trace=%file,getdents64,execve`. It flags `openat` lines that name the store, and it runs `os.path.realpath` on quoted paths (L460-465) so a symlink from the repo into the store is caught.
- A hardlink has no path to the store. `openat("<repo>/.git/info/attributes")` resolves to the repo path, so the oracle reports nothing. The same is true for an in-tree `.gitattributes` hardlink.
- Consequence: a hardlink case can be judged only on the guard decision (exit 2 with the `git-metadata-hardlink`-style finding). It must not be presented as store-access evidence. The `baseline red has no observed store access` gate (fixture L713-715) would fail such a baseline, so the checker needs an explicit contract-level label for it, not a silent exception.

### F6 — LOW (calibration): no existing fixture exercises any attribute source
- `tests/fixtures/r14-census-boundary.py` (cases R14C2-01..12, L46-57) has no `attributes`, `filter=` or `.clean` case. The XDG attributes default, `core.attributesFile`, `info/attributes` and in-tree `.gitattributes` are therefore all untested. `git/attributes` appears only as "[INFERENCE]" in SafetyCredential N3.
- The selftest `st_commit` (`tools/souji-census.sh:1157`, `git add -A` with no `-c` override) runs only inside `mktemp -d /var/tmp/souji-census-selftest.*` (L1192), so it is not a live path. Add the same `-c core.attributesFile=/dev/null` override for uniformity [LOW, optional].

### F7 — INFO (residual, not in scope to fix here): system attributes
- git-gitattributes: `$(prefix)/etc/gitattributes` is read for all users. `core.attributesFile` does not govern it, and no `GIT_ATTR_NOSYSTEM` variable appears in the git(1) page (checked; this is not proof that none exists in source). The file is outside the store, so it is not a store boundary issue. Presence on the host was not checked (no probes).

## Path reading vs execution (what each source can do)

| Source | Read by `status` | Neutralized by `count_dirty` `-c` | Can execute code | Current control |
|---|---|---|---|---|
| XDG/HOME attributes (default `core.attributesFile`) | yes, when key unset | yes (L712) | only with a driver definition | override |
| Local `core.attributesFile` (repo config) | yes | yes (`-c` wins) | only with a driver definition | L505 refusal (unnecessary, F1) |
| In-tree `.gitattributes` per dir | yes; symlinks not followed (gitattributes, working-tree section) | no | only with a driver definition | none; hardlinks unguarded (F5) |
| `$GIT_DIR/info/attributes` | yes | no | only with a driver definition | gitdir symlink check (L464-470); hardlink unchecked (F3) |
| `$(prefix)/etc/gitattributes` | yes | no | only with a driver definition | out of store scope (F7) |
| `filter.<d>.clean|smudge|process` in `.git/config` | n/a | not overridable by name | YES, on `status` when hashing is needed | L505 refusal (keep, F2) |
| `$GIT_DIR/config.worktree` | only if `extensions.worktreeConfig` | n/a | yes if read | extension refused L505; not scanned (F4) |

## Preservation cases (acceptance the C2 admission checker must require)

Every red must be the same command under the baseline (r14 tool) and the repaired tool. A green-only case is not evidence.

- P-A (benign local attribute path). Repo `.git/config` sets `core.attributesFile=<repo-relative file>`. Expect exit 0, row identical to a no-key control, and no `openat` of the in-repo attribute path. Baseline: exit 2 `git-config-unsupported`. Red = baseline exit 2; green = repaired row equality.
- P-B (store-pointing attribute path, paired with override removal). Repo sets `core.attributesFile=<store>/attr` and, separately, `HOME=<store-like>` with `$XDG_CONFIG_HOME/git/attributes` containing `* filter=x` and no driver. Expect exit 0, zero store access by `trace_access(follow_open_symlinks=True)`. Paired control: the same tool with the `-c core.attributesFile=/dev/null` removed must show a store `openat`. That red proves the override is load-bearing. Without the paired control the green is weak.
- P-C (accuracy control, in-tree attributes still apply). Repo commits CRLF content with `.gitattributes` `* text=auto`. Expect dirty count identical to the same repo with no `.gitattributes` after the change is staged. This shows the `-c` override does not disable in-tree attributes. A dirty count change here is a regression, not an improvement.
- P-D (filter attribute without driver). Repo `.gitattributes` `* filter=x`, no `filter.x.*` anywhere. Expect exit 0 and an unchanged dirty count, and no marker written. Shows the gate is config-keyed, not attribute-keyed, so mixed fleets are preserved.
- P-E (execution pair, required). `.gitattributes` `* filter=x` plus a local `filter.x.clean` that writes a synthetic marker file. Repaired tool: exit 2 with `git-config-unsupported`, marker absent. Paired baseline without the gate: marker present after an mtime change. The checker must require both halves; a green-only refusal is weak evidence because the marker may never have been reachable.
- P-F (hardlink, contract-level only). `$GIT_DIR/info/attributes` hardlinked to a store file (`nlink=2`). Expect the repaired guard to refuse with a stable finding after R3. Label it contract-level: the trace cannot see it (F5). The checker must not count it as access proof.
- P-G (symlink into store, in gitdir). `$GIT_DIR/info/attributes -> <store>/file`. Covered by L464-470, so expect refusal. This case is provable by the trace because `follow_open_symlinks` resolves it. Red = guard disabled.
- P-H (in-tree symlink, not followed). Working-tree `.gitattributes -> <store>/file`. Git does not follow working-tree `.gitattributes` symlinks (gitattributes, working-tree section). Expect exit 0 and no store access. This is preservation only, and the mechanism is documented, not demonstrated. The checker must label it green-by-doc and must not accept it as guard evidence.
- P-I (namespace control). A sibling path sharing the store prefix (for example `<store>-backup/x`) must not trip the store check. The existing matcher is boundary-aware: `descendant = agent + "/"` (fixture L432) and exact equality at L444 and L463. Keep it that way; add one positive control.

## Interactions and risks
- Behavior change from R1: fleets with a local `core.attributesFile` go from exit 2 to rows. Dirty counts can rise for files whose clean state depended on the operator's own XDG attributes, because the census ignores those by design. That direction is conservative (more dirty, fewer deletions). Document it; it is not a false-clean.
- Closes the N3/`git/attributes` [INFERENCE] items in SafetyCredential and BoundaryReviewGit N5 for the status path.
- Interaction with F4: R1 is safe only while `extensions.worktreeConfig` stays refused, or while config.worktree is scanned (R4).

## Unrun checks for L1 (not run by this seat)
1. `strace -y` run for P-B, P-E, P-F, P-G with the paired controls above.
2. Confirm by trace that `rev-list`, `for-each-ref`, `worktree list`, `rev-parse` open no attribute path (F1 is inference).
3. Confirm the selftest fixture repos define no `filter.*` before relying on F6.
4. Check `shellcheck` on the L477 and L505 edits.
5. Check whether `/etc/gitattributes` exists on the host (F7). Not probed.

## Messages
Material findings (F1, F2, F4) sent to SoujiR15.

## Boundary disclosure (no-query reminder from SoujiR15)
Calls that touched paths beyond the explicit source set, disclosed per the reminder:
1. `_grep` with `path: /home/vgpnk/Projects/shokunin/souji-shokunin` (whole lane root) for `attributesFile|gitattributes|clean filter|filter\.|core\.attributes`. This is a recursive search that includes `census/`, so it may have touched `census/operator-sweep-20261019/`. The returned matches showed `census/round-12`, `census/round-4`, `census/round-8` entries, and no `operator-sweep` path. I did not open or record any operator-sweep content. Limitation: result set is unverified against that directory.
2. `_bash` `git status --short` run at the lane root. Git walked the tree, and the untracked `census/operator-sweep-20261019/` appeared as `??` in output. Only the status line was seen; no contents were read. Limitation: git traversed the directory.
3. `_bash` `ls -la` at the lane root and `ls` on `tools`, `tests`, `results`. These are directory listings, not recursive; `census/` was listed by name only.
No runtime probes or tests were run. Findings are source-based; no conclusion depends on the disclosed calls.
