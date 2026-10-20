STATUS: DONE — reviewed at 3020befa… (1 major, 1 medium, 3 low); revision 9c45701a… fixes the major and the medium, the 3 lows remain open

# SentinelJjFixture — safety review of tests/fixtures/r17-jj-receipts.sh

Seat: SentinelJjFixture (sentinel, read-only).
Reviewed file: `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-jj-receipts.sh`. This is the revised git-only contract with J1–J9; real jj is used only in J9. The file was absent for about 15 minutes, and the review is of this landed version:

- sha256 `3020befa3337258077bdb4ffcc1ea1190d6fc8b1515fd2238a34b6003edacc34`
- mtime 2026-10-20 13:54:22, 763 lines

Mandate: the fixture must never run jj or git against a real repo, never push to a non-temp remote, isolate JJ_CONFIG/HOME/GIT_CONFIG_GLOBAL, clean up, and never read the user's jj config.

## Verdict

**partial.** Git isolation, remotes, receipt-tool pinning and normal-exit cleanup **hold**.

"Never run jj against a real repo" **fails** whenever the fixture is started from inside a jj workspace. It was started that way: the author ran it with `cd /home/vgpnk/Projects/shokunin/souji-shokunin && … bash tests/fixtures/r17-jj-receipts.sh` (history://SoujiR17-3.FixtureJjReceipts lines 223/236/245/250). "Never read the user's jj config" **fails** at line 138.

## Findings

### S1 — MAJOR: every jj call loads, and can write, the caller's CWD jj repo; the fixture never leaves the caller's CWD

- **Lines:** 138 (`jj --version`), 708 (`jj git clone --colocate`), 713, 717 and 718 (`jj -R "$JREPO" …`). There is no `cd` anywhere in the file (grep `^cd ` → no match).
- **Mechanism, from jj v0.45.1 source:**
  - `cli/src/cli_util.rs` `run_internal`, about :4602-4612: before looking at `-R`, jj builds `maybe_cwd_workspace_loader` from `find_workspace_dir(&cwd)` and calls `config_env.reset_repo_path(...)` and `reload_repo_config(...)`. So `-R <tmp>` does **not** stop jj from opening the CWD repo.
  - `lib/src/secure_config.rs` `maybe_load_config`: if `<repo>/.jj/repo/config-id` exists but `<XDG_CONFIG_HOME>/jj/repos/<id>/metadata.binpb` does not, it calls `generate_initial_config`. `generate_config` then `atomic_write`s `<repo>/.jj/repo/config-id`, which is a write inside the real repo.
  - The fixture correctly redirects `XDG_CONFIG_HOME` to `$T/home/.config` (line 151). That redirection is exactly what makes the metadata lookup miss, so every post-isolation jj call from CWD = lane rewrites the lane's `config-id`.
- **Observed (consistent with this mechanism; I cannot attribute it beyond timing):**
  ```
  $ stat -c '%n %y %i %s' …/souji-shokunin/.jj/repo/config-id
  …/config-id 2026-10-20 13:53:46.847783074 -0300 43438588 20     (first check)
  …/config-id 2026-10-20 13:54:55.370014798 -0300 43439044 20     (second check; fixture mtime 13:54:22)
  $ cat …/.jj/repo/config-id → acda0786460d4a89c9c1
  $ stat ~/.config/jj/repos/acda0786460d4a89c9c1/metadata.binpb → 2026-10-20 12:29:50 (unchanged)
  ```
  - The file was replaced twice: new inode, bytes unchanged. The lane `.jj` dir dates from 12:29:49, and the lane's real repo config still resolves.
  - The second rewrite came 33 s after the author's last edit. That matches the author's runs from CWD = lane.
  - Net damage today: none to content. But it is a jj-driven write into the real lane's `.jj`, which the contract forbids.
- **Latent destructive path:** a CWD repo whose config is still a legacy `.jj/repo/config.toml` without a `config-id` goes through `maybe_migrate_legacy_config`. On unix, `update_legacy_config_file` deletes that `config.toml` and replaces it with a **symlink into `$T/home/.config/jj/repos/<new-id>/config.toml`**. The EXIT trap then deletes the target. The real repo is left with:
  - a dangling config symlink;
  - a `config-id` that exists nowhere in the user's real config dir.

  The next real jj call silently starts from an empty repo config. For a lane that means `snapshot.auto-track="none()"`, the lane identity and the `trunk()` alias are lost. That is the 152-file index spam in JjTrialSouji step 3.
- **Exploit path:** run the fixture (the author's way, or a future gate runner with `cwd=<lane>`) from any jj workspace. J9 then makes four jj calls that each open that workspace.
- **Smallest fix:** add `cd -- "$T" || die "cannot enter scratch"` immediately after the exports and unsets (after line 172, before the heredocs). Optionally also use `env -C "$T"` on each jj call. Also fix the comment at line 59-60, "every jj call is `-R <tmp repo>` (a jj call from the lane cwd would mutate the lane)": `-R` alone does not prevent this.

### S2 — MEDIUM: `jj --version` runs before isolation and reads the user's jj config

- **Line 138:** `[ -n "$JJ_BIN" ] && JJ_VERSION=$("$JJ_BIN" --version …)` runs before `export HOME` (150), `XDG_CONFIG_HOME` (151) and `JJ_CONFIG` (160).
- `--version` is parsed by clap only after `reload_system_config`, `reload_user_config` and the CWD repo/workspace config loads (cli_util.rs `run_internal`: config load at about :4606-4612, `parse_args` later). So it reads:
  - `/etc/jj/config.toml` and `conf.d`;
  - `~/.config/jj/config.toml` and `conf.d`, or `~/.jjconfig.toml`;
  - the CWD repo's real `~/.config/jj/repos/<id>/config.toml`.
- The comment at lines 126-127 ("JJ_CONFIG is always ours, so the user's config is never read") is false for this line.
- **Fix:** resolve only the absolute `JJ_BIN` path before isolation (that is correct, lines 128-136). Move the `--version` probe after the exports and the S1 `cd`.

### S3 — LOW: the signal trap cleans up but does not exit, so the script keeps running

- **Line 145:** `trap 'rm -rf -- "$T"' EXIT INT TERM HUP`. In bash, a trap handler that does not `exit` returns control to the next command (documented bash trap semantics; [INFERENCE], not executed here).
- After Ctrl-C, or a TERM from an outer `timeout`, the fixture deletes `$T` and then continues building and running tools against a missing tree. Several steps recreate parts of `$T`: `mkdir -p "$SRC"` at 296, `git clone` targets, and jj `create_dir_all` under `$T/home`.
- If the outer runner then escalates to SIGKILL, those recreated dirs stay in `/var/tmp`.
- **Fix:** `trap 'rm -rf -- "$T"' EXIT; trap 'exit 129' HUP; trap 'exit 130' INT; trap 'exit 143' TERM`.

### S4 — LOW: the scratch location honors the caller's TMPDIR and only checks it lexically

- **Lines 140-144:** `mktemp -d "${TMPDIR:-/var/tmp}/…"`, then `case "$T" in /var/tmp/?*)`.
- `TMPDIR=/var/tmp/../home/vgpnk` passes the guard and puts the scratch, including `HOME`, `GIT_CEILING_DIRECTORIES` and the bare origin, under the real home. The dir is still fresh and trap-removed, so impact is low.
- **Fix:** hard-code `/var/tmp`, as the r12 precedent does deliberately: `tests/fixtures/r12-maintenance-guard.sh:47-48` "(TMPDIR deliberately ignored)" and `:68`. Alternatively canonicalize with `readlink -f` before the `case`.

### S5 — LOW: the git env scrub misses config-injection variables

- **Lines 169-172** unset `GIT_DIR`, `GIT_WORK_TREE` and others. They do **not** unset:
  - `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_COUNT`, `GIT_CONFIG_KEY_<n>`, `GIT_CONFIG_VALUE_<n>`;
  - `GIT_NAMESPACE`, `GIT_SSH_COMMAND`, `GIT_EXEC_PATH`.
- A caller env carrying `GIT_CONFIG_PARAMETERS` (for example `url.<real-remote>.insteadOf=/var/tmp/`) is applied to every `g` call. It could redirect the only pushes, at 306 and 313 (`push -q origin main` to `$SRC/origin.git`), to a non-temp remote.
- `GIT_NAMESPACE` would silently relocate the synthetic `refs/jj/keep/*` (a correctness issue, not a safety one).
- **Fix:** add those names to the `unset` list.

### S6 — INFO: unneeded `protocol.file.allow=always`

- **Lines 184-185.** It is only needed for submodule file transport, and nothing here uses submodules. It is harmless with local-only remotes. Drop it to keep the config minimal.

## What holds (evidence lines)

- **No non-temp remote.** The only remote is `$SRC/origin.git` (`SRC="$T/src"`):
  - seed `remote add` at 305;
  - pushes at 306 and 313;
  - `g clone` in `build_plain`/`build_keep_repo`;
  - `jj git clone` at 708.

  J9 no longer pushes. The fixture never invokes `scripts/hyaku/jj-lane.sh`, which always pushes to `origin` (jj-lane.sh:350/695); `HYAKU_STATE` is pinned to `$T/hyaku-state` anyway (159).
- **No git against the lane.** Every repo operation is `g -C <$T path>` or targets an absolute `$T` path. `LANE` (line 70) is used only to default `--tool-dir`. `refs/jj/*` are synthesized with `git update-ref` inside `$T` (`build_keep_repo`, `case_j8`).
- **Git config isolation.** Set before any git call:
  - `GIT_CONFIG_GLOBAL=$T/gitconfig` and `GIT_CONFIG_NOSYSTEM=1` (155-156);
  - `HOME`/`XDG_*` under `$T` (150-154).

  jj's gix and its git subprocess therefore cannot see `~/.gitconfig`, `~/.config/git/config` or `/etc/gitconfig`.
- **jj user config (after line 150).** `JJ_CONFIG=$T/jj.toml` (160) replaces user and system config (docs/config.md v0.45.1: "If the environment variable is set … ignore the default locations"). Isolating `XDG_CONFIG_HOME` keeps secure per-repo config writes for `$T` repos inside `$T` (config.rs:60 `REPO_CONFIG_DIR="repos"`, :286 `root_config_dir`). `JJ_CONFIG` alone would not have done that. The exception is S1/S2.
- **Receipt engines.** They cannot reach the real fleet, ledger or vault:
  - `SHOKUNIN_ROOT=$T/fleet`, `SOUJI_LEDGER`, `SOUJI_Q_SHOKUNIN_ROOT`, `SOUJI_Q_LEDGER`, `SOUJI_VERIFY_BIN` (162-167). Without these, verify.sh:70/72 would default to the real fleet root and ledger, and run `git worktree list` (:447/:969) plus `rg --no-ignore` (:206) over every fleet repo, or over all of `/var/tmp` for the 5fa6017 copy.
  - vault-verify always runs `--fallback` (`vlt_run`, J6, J8), so `$HOME/.local/bin/obsidian` (vault-verify.sh:164) is never executed.
  - quarantine runs `--dry-run --hold 0` only (`q_run`).
- **No detached gc or maintenance.** `gc.auto=0` and `maintenance.auto=false` are set both in the global config (176-181) and on every `g` call (196), so no background `git maintenance` can outlive the trap. This is the r12 hazard: `r12-maintenance-guard.sh:5-24`.
- **Scoped deletes.** Every `rm -rf` targets a `$T/...` constant: 332, 338, 378, 624, 739, plus the trap. `T` is set under `set -u` and guarded at 141-144.
- **Cleanup observed.** `stat /var/tmp/r17-jj-receipts.*` finds nothing after the author's runs. Leftovers outside the fixture: the author's ad-hoc probes `/var/tmp/jjprobe.HBJEw5` (13:38:59), `/var/tmp/jjprobe.fiH044` (13:39:10) and `/var/tmp/probe4.N4u9Hj` (13:53:57). These are outside the seat's sanctioned `/var/tmp/souji-r17-FixtureJjReceipts/` and were not deleted (seat hygiene, not the fixture).

## Commands run (all read-only)

```
read  …/tests/fixtures/r17-jj-receipts.sh            (absent ×4, then landed; full read)
read  …/scripts/hyaku/jj-lane.sh:1-300 ; grep :300-711   (push/config-set sites)
read  …/tests/fixtures/r13-quarantine-bounds.sh:1-83, r12-maintenance-guard.sh:1-73, .gitignore
grep  tools/souji-verify.sh, souji-vault-verify.sh, souji-quarantine.sh  (env defaults, roots, CLI flags)
read  .ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md, JjAuditSouji.md:1-300
curl  raw.githubusercontent.com/jj-vcs/jj/v0.45.1/{docs/config.md,cli/src/config.rs,cli/src/cli_util.rs,lib/src/secure_config.rs}  (web read)
stat  …/souji-shokunin/.jj, .jj/repo/config-id (×3), ~/.config/jj/repos/<id>/{,metadata.binpb,config.toml}  (paths/mtimes only)
cat   …/souji-shokunin/.jj/repo/config-id  → acda0786460d4a89c9c1 (identifier, not a secret)
bash -n …/r17-jj-receipts.sh → BASH-N-OK
shellcheck -S warning -s bash …/r17-jj-receipts.sh → clean
sha256sum …/r17-jj-receipts.sh → 3020befa3337258077bdb4ffcc1ea1190d6fc8b1515fd2238a34b6003edacc34
stat  /var/tmp/r17-jj-receipts.* /var/tmp/jjprobe.* /var/tmp/probe4.*
```

- I never executed the fixture, jj, the souji tools, or any git write.
- I used one background wait loop (`timeout 1500 sh -c 'until [ -s F ]; do sleep 20; done; …'`), which only `stat`s the fixture path.

Coordination: I sent the author three messages: the isolation checklist, then the JJ_CONFIG/secure-config and SHOKUNIN_ROOT/ledger pins (now present at 150-168), then the S1/S2 `cd "$T"` fix. S1/S2 were still unfixed at sha `3020befa…`.

Installs/updates: none.

## Smallest remediation (in priority order)

1. After line 172, add `cd -- "$T" || die "cannot enter scratch"`. Move line 138 (`--version`) below it. Correct comments 59-60 and 126-127. This closes S1 and S2.
2. Change line 145 to `trap 'rm -rf -- "$T"' EXIT; trap 'exit 129' HUP; trap 'exit 130' INT; trap 'exit 143' TERM` (S3).
3. Change line 140 to `mktemp -d /var/tmp/r17-jj-receipts.XXXXXX` (S4).
4. Extend the unset at 169-172 with `GIT_CONFIG_PARAMETERS GIT_CONFIG_COUNT GIT_NAMESPACE GIT_SSH_COMMAND GIT_EXEC_PATH`, and the `GIT_CONFIG_KEY_*`/`GIT_CONFIG_VALUE_*` names via `compgen -e` (S5).
5. Optional: drop `protocol.file.allow` at 184-185 (S6).

L1 check after the fix: `stat -c '%i %y' <lane>/.jj/repo/config-id` before and after one fixture run from CWD = lane. Inode and mtime must be unchanged.

## Addendum — re-check of revision 9c45701a…

The file now has sha256 `9c45701a9091c3ba7bc24c2b3d39a1692ce4392a2afcf1068f201848b1749a63`, mtime 13:56:55, after my S1/S2 message.

- **S1 resolved.** Line 147 now has `cd -- "$T" || die "cannot enter scratch $T"`, directly after the trap and before any jj call. From here on jj's CWD workspace lookup starts inside `$T`, and `$T` has no `.jj`, so no real repo is opened.
- **S2 resolved.** The `--version` probe moved to line 199, after the HOME/XDG/JJ_CONFIG exports, so it no longer reads the user's jj config.
- **Still open:** S3 (trap at 146 still `EXIT INT TERM HUP` with no exit), S4 (141 still honors TMPDIR), S5 (no `GIT_CONFIG_PARAMETERS` scrub) and S6 (186-187).
- **Lane state at re-check:** `.jj/repo/config-id` still has mtime 13:54:55 and inode 43439044, so there was no new rewrite. That is consistent with no run from CWD = lane since the fix, but I did not observe a run.
- **Verdict for the fixed revision:** holds on all five mandate points (no real-repo git/jj, no non-temp remote, JJ_CONFIG/HOME/GIT_CONFIG_GLOBAL isolated, cleanup, no user jj config). S3–S6 remain low-severity hardening items.
- **For L1:** add one check. Record `stat -c '%i %y'` of the lane's `.jj/repo/config-id`, run the fixture once from CWD = lane, and confirm inode and mtime are unchanged.
