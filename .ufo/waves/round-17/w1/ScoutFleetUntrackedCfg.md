STATUS: DONE — D1 config exposure is nil on this host: 21 lanes + fleet root, zero `status.showUntrackedFiles`, zero `extensions.worktreeConfig`, zero `.git/config.worktree`, zero `include.*`; the false-clean row is latent-only, not live.

# ScoutFleetUntrackedCfg — D1 live exposure sweep

Round 17 / WAVE 1 / lane souji-shokunin (base 5fa6017ddcae9f6bd4412df44765f6360cb16294). Read-only exposure probe for C1/D1.

## Question

Across every lane repo (`/home/vgpnk/Projects/shokunin/*-shokunin`) and the fleet root, is a false-clean census row *live* through any of the three declared D1 sources — repo-local `.git/config`, `.git/config.worktree`, or an `include.path` target reachable from them?

## Method (exact commands run)

```
ls -d /home/vgpnk/Projects/shokunin/*-shokunin            # 21 lanes
ls -d /home/vgpnk/Projects/shokunin/.git                  # fleet root repo exists
stat -c '%F %h %a %U:%G %n' <repo>/.git/config <repo>/.git/config.worktree   # x22
git config --file <repo>/.git/config --list               # x22, full dump
git config --file <repo>/.git/config --get-all extensions.worktreeConfig
git config --file <repo>/.git/config --get-all status.showUntrackedFiles
git config --file <repo>/.git/config --get-all include.path
git config --file <repo>/.git/config --get-regexp '^include'
sha256sum <repo>/.git/config; wc -l <repo>/.git/config   # x22
grep -niE '^[[:space:]]*\[[[:space:]]*(include|includeif)|untracked|worktreeconfig' \
  .git/config *-shokunin/.git/config                     # exit 1 = no match anywhere
awk repositoryformatversion                              # x22
```

No file outside the three named classes was opened. No writes except this report. No `jj`, no git write, no running census/verify/vault/quarantine.

## Result — all 22 repos are identical on the three D1 axes

| repo | .git/config sha256 | lines | status.showUntrackedFiles | extensions.worktreeConfig | .git/config.worktree | include.* |
|---|---|---|---|---|---|---|
| shokunin (fleet root) | f9c71df95e20a480ad5db0f593b7342b54ab2ac3c10c5970983f3089584ff058 | 11 | absent | absent | absent | none |
| audio-shokunin | 4f6c2ae183bd92d82ea4b11f7df62e5258f9abf556b726030e046ede857d955a | 13 | absent | absent | absent | none |
| chousa-shokunin | 0c36e394000f4a9eca88e4fe9e8bf3fabc2688774098c6be61c06d1851d1725c | 14 | absent | absent | absent | none |
| game-dev-2d-shokunin | c3dfa209a0828a52860a600451d7399d31a14b6acdd59c7ae268081865179125 | 14 | absent | absent | absent | none |
| game-dev-3d-shokunin | 79d0728dd674269023b87380ff95b8f062d331feeca26513cc01b373361c0e43 | 14 | absent | absent | absent | none |
| kagi-shokunin | 0dd3dd9bd05dcc1087bc79861cca78203998a4a01b0aff1e1c4e3a6afc152cca | 14 | absent | absent | absent | none |
| kaidoku-shokunin | 615581a0d5ee1c2e4063db916fa45abf013ff632080db72b22ff5df01957d4f6 | 14 | absent | absent | absent | none |
| kake-shokunin | 999514faf3db59e8da47fd8b0d72670c4d1687c49675de2766831a35c30abcd9 | 14 | absent | absent | absent | none |
| kama-shokunin | e0293921db30a09aec906e70b7a0344a1ee8be09b4aae355a46c72190436b019 | 14 | absent | absent | absent | none |
| kasegi-shokunin | f720b4497a78ef6dae64247a095b8a86c0f9f37ef9d17e086c98311df6910777 | 14 | absent | absent | absent | none |
| kengaku-shokunin | c07fd1a331aae2fa621a89f9824dbd2f961a47ba78c1e4671768d33a06f29d17 | 14 | absent | absent | absent | none |
| kotoba-shokunin | 05a01fadcb14da3a7369be15cd4aab84e809a5f2ba34d1004b3880650e52474a | 14 | absent | absent | absent | none |
| kotodama-shokunin | b544e28e46d92e3bfa1b927d3b8af621cd7171a7edd77fe15f8f7fd2362e153a | 16 | absent | absent | absent | none |
| kumitate-shokunin | 8205e2b8c70c946bae223622ac888b19a9a3efcafe427689bdb8b593b2683e0a | 14 | absent | absent | absent | none |
| lore-shokunin | 3e2118c5c23d1db7cb9b5fe75aa3d1afa60a3059310f6e9c3882dd8b973314b1 | 14 | absent | absent | absent | none |
| mado-shokunin | 3a1ed43a0f3c8f2798bde27b917a79347ad101af0efe33d54acdb90d594e65cb | 14 | absent | absent | absent | none |
| mori-shokunin | fd4a3e3a951a829e338f8ef8139a4522c890ea418c4b1432d66b3a012039e1c6 | 14 | absent | absent | absent | none |
| revenger-shokunin | 6ee0ba825d284258a376505eb25e84e75e1b8d8b0a7da151c1e4690f50c7fd1a | 14 | absent | absent | absent | none |
| souji-shokunin | 5f47f8b4ee34ee889d8ffa9aaf75b0bdcd6fbca0d29fea950081426f481f08a6 | 14 | absent | absent | absent | none |
| tabi-shokunin | b2ed930002653a64d05c85c42a6b6c46f0d99251c7dfb921e69010d89617218b | 16 | absent | absent | absent | none |
| tameshi-shokunin | 825c0d3a8e1213deee06b43f6ea2b19ea5adb7e0ff92c33192e02c1d35149a61 | 14 | absent | absent | absent | none |
| tsukuroi-shokunin | c2fa7ae0aa45ca30a20132242cb25b84c6b4fec20678b78279b8c0c90bd3afbc | 14 | absent | absent | absent | none |

Every `.git/config` is a regular file, `nlink=1`, mode `0644`, owner `vgpnk:vgpnk` (no symlinked or hardlinked config in the fleet — D2's hardlink hazard does not extend to `config`).

## Findings

F1 (observed, high confidence). `status.showUntrackedFiles` is set in **no** repo-local config and in no worktree/included file. All 22 dumps contain only `core.*`, `remote.origin.*`, `branch.*.remote|merge`, optional `user.name|email`, `commit.gpgsign`, `lfs.repositoryformatversion`. Grep for `untracked` over all 22 raw files: no match (`grep` exit 1). Therefore the D1 false-clean trigger is **latent, not live** on any lane or the fleet root.

F2 (observed). No `.git/config.worktree` exists in any of the 22 repos (`stat` ENOENT for all). Additionally `extensions.worktreeConfig` is absent in all 22, so git does not consult a `config.worktree` for these repositories even if one appeared: activation requires `extensions.worktreeConfig=true`, documented under the version-1 repository format. Belt: every repo reports `core.repositoryformatversion=0` (observed), and `audio-shokunin` / `tabi-shokunin` additionally report the unrelated `lfs.repositoryformatversion=0` (do not mistake that key for the extension in a grep).

F3 (observed). No `include.path`, no `includeIf.*`, no `[include]` section anywhere (git `--get-regexp '^include'` empty for all 22; raw-text grep for `[include`/`[includeif` exit 1). There is no included file to resolve, inside or outside the fleet.

F4 (observed). Repo variant keys exist but are orthogonal: `kotodama-shokunin` has `commit.gpgsign=false`; `audio-shokunin` and `tabi-shokunin` carry the LFS key. None touch status or worktree-config behavior, so the uniform "absent" result above is not an artifact of templating.

F5 (inference, documented precedence). The blanket result above does not prove a global/system config or a `GIT_CONFIG_*`/`GIT_DIR` environment at census invocation time cannot set `status.showUntrackedFiles=no`. Those scopes were outside this assignment's read bound ("read ONLY these files"). The D1 fix remains the correct control because a command-line `--untracked-files=normal` on the `status` invocation overrides config from every scope, whereas relying on repo-local absence does not.

## Verdict

**Holds (exposure nil).** For the three declared D1 sources, no live false-clean exposure exists across 21 lanes + fleet root. Confidence high on the negative: full config dumps, `--get-all` per key, raw-text grep, and `stat` of the worktree config all agree; the only gap is the out-of-bounds global/env scope (F5).

## Smallest fix (advisory)

None is required to close a live exposure; keep D1 exactly as claimed (explicit `--untracked-files=normal` in `count_dirty`) for scope-independence and to make the hygiene fixture meaningful. Consequence for the r17 harness: the `tests/fixtures/r17-census-hygiene.py` arm must **create** `status.showUntrackedFiles=no` in its own throwaway repo config (plus a `config.worktree` arm gated on `extensions.worktreeConfig=true` with `core.repositoryformatversion=1`, since a bare `config.worktree` is inert at version 0) — no host repo will supply the trigger, so a fixture that merely reuses an existing lane would pass vacuously. If the fixture also wants the include arm, it must write an `include.path` into its own config; again nothing in the fleet provides one.

## Residual unknowns / limits

- Global/system config and census-invocation env were not read (out of assigned bounds); see F5 for the mitigation.
- Linked-worktree gitdirs (`<repo>/.git/worktrees/*/config.worktree`) were not walked (out of assigned reads) but, per F2, are inert while `extensions.worktreeConfig` is absent and version is 0.
- This probe verifies configuration state only; it does not re-read `tools/souji-census.sh` and makes no claim about whether the base revision already passes the flag.

## Tooling installed/updated

None. No pacman, uv, npm, or cargo transaction was performed.
