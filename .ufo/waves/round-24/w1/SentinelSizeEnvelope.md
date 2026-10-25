# SentinelSizeEnvelope — C1 read-only envelope, adversarial pre-landing review

## Status
STATUS: PASS — every candidate vector was probed (harmless `touch` marker plus a whole-repo manifest before and after) against git 2.56.0. On these two commands, three vectors execute a program and one also writes. The **model envelope** (`tools/souji-repo-structure.sh`) neutralizes **none** of them. The override set below neutralizes all of them in probes. Two hang (DoS) classes have no config override and need a timeout.

## Evidence
- Revision: lane HEAD `f9db2181647d91470a724a12d626bd6106805076` (`git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD`). git: `git version 2.56.0`, `pacman -Q git` -> `git 2.56.0-1`. Docs: the installed man pages rendered with `man -P cat` (all owned by `git 2.56.0-1`).
- Harness: scratch `/var/tmp/souji-r24-SentinelSizeEnvelope/` (removed at the end). Every git call ran under `env -i PATH=/usr/bin:/bin HOME=<empty scratch dir> LC_ALL=C GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null`, plus the vector's config or env. Commands: `count-objects -v` (co) and `fsck --unreachable --no-reflogs` (fs). Columns:
  - raw: no guards.
  - model: `GIT_OPTIONAL_LOCKS=0 GIT_NO_LAZY_FETCH=1 GIT_TERMINAL_PROMPT=0 git -c maintenance.auto=false -c maintenance.autoDetach=false -C R`, exactly as in souji-repo-structure.sh:150-177.
  - propkeep: the proposed `-c` set with the attacker env still present.
  - prop: the full proposal (allowlisted env plus `--git-dir=<common>`).
  Each row reports the marker files created and whether the repo manifest (path, type, mode, size, mtime, sha256) changed.
- Key output excerpts (verbatim harness lines):
  - `fsmonitor model fs rc=0 marks=fsmonitor repo=same | warning: Empty last update token. unreachable blob 82cef6e…`
  - `fsmonitor propkeep fs rc=0 marks=none repo=same | unreachable blob 82cef6e…`
  - `A2 raw --git-dir=COMMON fsck rc=0 marks=fsmonitor` / `A3 --no-optional-locks -C R fsck rc=0 marks=fsmonitor` / `A6 GIT_INDEX_FILE=/dev/null -C R fsck rc=0 marks=fsmonitor` / `A9 … --connectivity-only … marks=fsmonitor` / `A10 … --no-references … marks=fsmonitor`
  - `A4 -c core.fsmonitor=false -C R fsck rc=0 marks=none` / `A5 -c core.fsmonitor= (empty) … marks=none` / `A7 raw -C R count-objects -v rc=0 marks=none`
  - `A12 wt-config fsmonitor, fsck from wt … marks=fsmonitor` / `A13 same, -c core.fsmonitor=false from wt … marks=none`
  - `G1 raw -C R fsck rc=0 marks=none repo=CHANGED`, then `fsmonitor--daemon.ipc` (socket) and `fsmonitor--daemon/` appeared in `.git`, and `fsmonitor-daemon is watching '…/q/fsd'`. `G4 raw --git-dir=COMMON fsck … repo=CHANGED` and `G5 model envelope (-C R) fsck … repo=CHANGED`, each with the daemon watching. `G2 -c core.fsmonitor=false … repo=same`. `G3 raw count-objects … repo=same`, daemon not watching. Every daemon this harness started was stopped with `git fsmonitor--daemon stop`; the final `pgrep -af fsmonitor--daemon` returned nothing.
  - `GIT_TRACE=1 git -C R fsck --unreachable --no-reflogs` spawned three children: `run_command: git refs verify`, `git multi-pack-index verify --object-dir .git/objects --no-progress`, and `git commit-graph verify --object-dir .git/objects --no-progress`. With `-c core.commitGraph=false -c core.multiPackIndex=false --no-references` it spawned none. `count-objects` spawned none.
  - `C1 GIT_EXEC_PATH=fake fsck (no commit-graph) … marks=execgit` / `C2 same --no-references … marks=execgit` / `C4 same + -c core.commitGraph=false … marks=execgit` / `C5 PATH=fake:/usr/bin (no GIT_EXEC_PATH) fsck … marks=none` / `C6 GIT_EXEC_PATH=fake count-objects … marks=none` / `C7 PATH=fake: bare 'git' resolution (tool) … marks=execgit`
  - `env_cfgcount model fs … marks=cfgcount` and `env_cfgparams model fs … marks=cfgparams`, with propkeep and prop `marks=none`. `env_trace model co … marks=trace,trace2-env`. `env_global_trace2 model co … marks=trace2-global`, propkeep the same, prop `marks=none`. `GIT_CONFIG_SYSTEM=<file with core.fsmonitor> GIT_CONFIG_NOSYSTEM=0 … fsck` -> marker `fsmonitor`.
  - `pager raw co rc=0 marks=pager` (under a tty via `script`). `B2 tty GIT_PAGER=cat fsck marks=` / `B3 tty --no-pager fsck marks=` / `B5 non-tty raw fsck (captured) … marks=none`.
  - Positive controls for lazy fetch (partial clone, missing blob): `E1 cat-file -e raw (remote.origin.uploadpack) rc=128 marks=uploadpack` / `E6 … (ext:: url) marks=ext` / `E9 … (core.sshCommand) marks=ssh`. The same vectors on the two target commands showed no marker in any column: `E4 fsck --unreachable --no-reflogs raw … marks=none`, `E5 count-objects -v raw … marks=none`, `E8c`/`E9b` `marks=none`, `lazy_* raw co/fs … marks=none`. `E7 same, -c protocol.allow=never rc=128 marks=ext`, `E8 same, GIT_ALLOW_PROTOCOL=none … marks=none … transport 'ext' not allowed`, `E8b same, GIT_NO_LAZY_FETCH=1 rc=1 marks=none`.
  - Hangs: `skiplist_fifo raw/model/propkeep/prop fs rc=124`; `D2 skipList=FIFO, -c fsck.skipList=/dev/null rc=124`; `include_fifo raw/model/propkeep co+fs rc=124` (the prop row passed only after I fed the FIFO an EOF); `K1 objects/info/alternates is FIFO: count-objects rc=124`. The tool's own `rev-parse --git-common-dir` also blocked on the include FIFO until it received EOF.
  - No-effect rows: `hookspath`/`hooksdir` (29 hook names) `marks=none` in all 16 runs. `altrefs` `marks=none`. `trace2_repo` `marks=none`. `gcauto` (`gc.auto=1`, `gc.autoPackLimit=1`, `maintenance.auto=true`, 7 loose objects) `repo=same` in all columns. `D1 skipList lists dangling oid … unreachable blob 82cef6e…` (still listed). `D3 unknown fsck.<msg-id> in repo config rc=128 … fatal: Unhandled message id: bogusmsgid`.
  - Ownership: with `GIT_TEST_ASSUME_DIFFERENT_OWNER=1`, repo-config `safe.directory=*` -> `fatal: detected dubious ownership`; command-line `-c safe.directory='*'` -> `count: 2` (gate bypassed).
  - Discovery: `K2 discovery from non-repo subdir: …/q/disc/.git`. `K3 with GIT_CEILING_DIRECTORIES=…/sub: fatal: not a git repository`.
  - Partial clone calibration: refs all `afde02b`, yet `fsck --unreachable --no-reflogs` printed `unreachable tree aaff7498…`, `unreachable commit 0ffd4084…`, `unreachable tree 3683f870…`.
- The lane today: `git config --file <lane>/.git/config --no-includes --list` filtered for risky keys -> `no risky keys in lane local config`. `--show-scope --get-regexp` over fsmonitor, hooksPath, include, fsck, trace2, safe.directory and extensions -> `no such keys in any scope`. `--is-shallow-repository` -> `false`. 1 worktree.
- Tooling installs: none.

## Findings
Ranked by severity for `count-objects -v` and `fsck --unreachable --no-reflogs` on git 2.56.0. "Applies" means executes or writes in a probe.

1. **HIGH — `core.fsmonitor=<path>` (repo config, `config.worktree`, or any injected scope) executes a program during `fsck`; `count-objects` is not affected.**
   - Doc: git-config.txt:1410 "Otherwise, this variable contains the pathname of the "fsmonitor" hook command." git-fsck.txt:19 "If no objects are given, git fsck defaults to using the index file, all SHA-1 references in the refs namespace".
   - Not neutralized by the model envelope, `GIT_OPTIONAL_LOCKS=0`/`--no-optional-locks`, `--git-dir=<common>`, `GIT_INDEX_FILE=/dev/null`, `--connectivity-only`, or `--no-references` (A2, A3, A6, A9, A10).
   - Override: `-c core.fsmonitor=false`. Verified at A4, A13, propkeep and prop; an empty value works too (A5).
   - The stderr line it causes (`warning: Empty last update token.`) would make the tool exit 1, but only after the program has already run. The stderr rule is not a guard.

2. **HIGH — `core.fsmonitor=true` makes `fsck` start a persistent `git fsmonitor--daemon` and write a socket and a directory into `.git`.**
   - Doc: git-config.txt:1403 "If set to true, enable the built-in file system monitor daemon for this working directory (git-fsmonitor--daemon(1))." The page calls it Windows/macOS-only, but git-config.txt:2516 "This Mac OS and Linux-specific option" and probe G1 show Linux support.
   - This breaks the C1 manifest invariant and leaves a process behind. It also fires with `--git-dir=<common>` (G4) and under the model envelope (G5).
   - Override: the same `-c core.fsmonitor=false` (G2).

3. **HIGH — Inherited caller environment injects config or replaces the git binary.**
   - Config injection: `GIT_CONFIG_COUNT`/`KEY_n`/`VALUE_n`, `GIT_CONFIG_PARAMETERS`, and `GIT_CONFIG_SYSTEM`/`GIT_CONFIG_GLOBAL` all carried `core.fsmonitor` into fsck (exec). Doc: git-config.txt:330 "If GIT_CONFIG_COUNT is set to a positive number, all environment pairs GIT_CONFIG_KEY_<n> and GIT_CONFIG_VALUE_<n> up to that number will be added".
   - `GIT_EXEC_PATH`: fsck always spawns `git refs verify`, `multi-pack-index verify`, and `commit-graph verify`, resolved through the exec path. A poisoned value ran the fake `git` even with `--no-references` and `core.commitGraph=false` (C1, C2, C4). Doc: git.txt:66 "This can also be controlled by setting the GIT_EXEC_PATH environment variable."
   - `GIT_TRACE`/`GIT_TRACE2_*`, and `trace2.*` set in global config, write files on both commands.
   - The tool's own bare `git` lookup follows `PATH` (C7).
   - The model script unsets only six `GIT_*` variables (souji-repo-structure.sh:153-154), so all of the above pass through.
   - `-c` beats `GIT_CONFIG_COUNT`/`GIT_CONFIG_PARAMETERS` for the keys it names (propkeep `marks=none`), but not for keys it doesn't name.
   - Override: build the child env from an allowlist (`env -i` or `subprocess` `env=`), not a denylist. Use `PATH=/usr/bin:/bin`, `LC_ALL=C`, `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_SYSTEM=/dev/null`, `GIT_CONFIG_GLOBAL=/dev/null` (git.txt:1022 "Likewise, if GIT_CONFIG_GLOBAL is set, neither $HOME/.gitconfig nor $XDG_CONFIG_HOME/git/config will be read."), and invoke absolute `/usr/bin/git`. An allowlist also drops `GIT_DIR`, `GIT_COMMON_DIR`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES` and `GIT_INDEX_FILE`, which would otherwise redirect the census.

4. **MEDIUM (calibration) — Path discovery walks up to the parent repo.**
   - `--repo <non-repo dir>` resolves the enclosing repository (K2). Under the fleet root that means a census of the fleet repo, which breaks "a figure about this repo only".
   - Fix: refuse with exit 2 unless `realpath(--repo)` equals `rev-parse --show-toplevel` (or, for a bare repo, `--absolute-git-dir`). Alternatively set `GIT_CEILING_DIRECTORIES=<parent of realpath(--repo)>` (K3).

5. **MEDIUM (operability, DoS) — A FIFO in `include.path`, `fsck.skipList`, or `objects/info/alternates` hangs git indefinitely; no `-c` override exists.**
   - Doc: git-config.txt:3198 "to include other configuration files. See the "CONFIGURATION FILE" section in the main git-config(1) documentation".
   - `-c fsck.skipList=/dev/null` still hangs (D2), consistent with skipList being additive. Discovery (`rev-parse`) hangs too.
   - Fix: a hard timeout on every git subprocess, including discovery, mapped to exit 1. No write or exec was observed.

6. **LOW (latent on these two commands) — Lazy promisor fetch.**
   - Vectors: `remote.<n>.uploadpack`, `core.sshCommand`, `ext::` URLs with repo `protocol.ext.allow=always`, and `core.gitProxy`. The first three execute for `cat-file` (E1, E6, E9). None fired for `count-objects -v` or `fsck --unreachable --no-reflogs` in any column. `core.gitProxy` had no positive control (it needs a `git://` host).
   - Doc: git-config.txt:1506 "the specified command instead of ssh when they need to connect to a remote system." git-config.txt:3984 "known-dangerous protocols (ext) have a default policy of never".
   - Overrides: `GIT_NO_LAZY_FETCH=1` (git.txt:1129 "Setting this Boolean environment variable to true tells Git not to lazily fetch missing objects from the promisor remote on demand.", E8b) and `GIT_ALLOW_PROTOCOL=none` (git.txt:1150 "If set to a colon-separated list of protocols, behave as if protocol.allow is set to never,", E8).
   - **`-c protocol.allow=never` does NOT override a repo-level `protocol.ext.allow=always` (E7). The tool must not rely on it.**
   - Keep the contract's partialClone refusal for calibration as well: fsck reports reachable history as `unreachable tree/commit` in a partial clone (E').

7. **LOW — `pager.<cmd>` and `core.pager` execute only when stdout is a tty (raw/model `marks=pager`).**
   - The tool captures stdout, so no exec happens there (B5).
   - Defence in depth at no cost: `--no-pager` plus `GIT_PAGER=cat` (git.txt:982 "If it is set to an empty string or to the value "cat", Git will not launch a pager."; B2, B3).

8. **NONE (a guard against a tool mistake) — `safe.directory` is honoured only in protected config.**
   - Doc: git-config.txt:4506 "This config setting is only respected in protected configuration (see the section called “SCOPES”)." git-config.txt:314 "Protected configuration refers to the system, global, and command scopes."
   - A repo cannot whitelist itself (probe). But **the tool MUST NOT pass `-c safe.directory=*`**: command scope counts as protected, and that flag bypassed the ownership gate (`count: 2`).
   - Reading global and system config as `/dev/null` means a repo owned by someone else fails closed (exit 128, tool exit 1). That is the desired behaviour.

9. **NONE on these commands (probed, no exec, no write):**
   - `core.hooksPath` and `$GIT_DIR/hooks`: no hook fires for either command. The cheap pin is still `-c core.hooksPath=/dev/null` (git-config.txt:1659 "You can also disable all hooks entirely by setting core.hooksPath to /dev/null.").
   - `core.alternateRefsCommand`: used only for advertising (git-config.txt:1527 "When  advertising  tips  of available history from an alternate, use the shell to execute the specified command instead of git-for-each-ref(1)."). Not fired, even with alternates present.
   - `uploadpack.packObjectsHook`: upload-pack only and protected-only (git-config.txt:5072 "If this option is set, when upload-pack would run git pack-objects to create a packfile for a client, it will run this shell command instead.").
   - `trace2.*` in repo config: ignored (git-config.txt:4831 "Trace2 config settings are only read from the system and global config files; repository local and worktree config files and -c command line arguments are not respected.").
   - `gc.auto` and `maintenance.auto`: no auto-maintenance on either command (repo unchanged).
   - `fsck.<msg-id>` and `fsck.skipList` (non-FIFO): no exec, and the unreachable lines are unchanged (D1, D5). An unknown msg-id is fatal (git-config.txt:2491 "Setting an unknown fsck.<msg-id> value will cause fsck to die"), which fails closed as tool exit 1.
   - `GIT_OPTIONAL_LOCKS=0`: blocks nothing here (A3). Harmless; keep it.

**Overrides the tool must carry** (prop column: all exec and write vectors neutralized, and the unreachable/garbage figures equal raw on every non-partial case):
```
env -i PATH=/usr/bin:/bin LC_ALL=C HOME=<empty dir> \
  GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_SYSTEM=/dev/null GIT_CONFIG_GLOBAL=/dev/null \
  GIT_NO_LAZY_FETCH=1 GIT_ALLOW_PROTOCOL=none GIT_PROTOCOL_FROM_USER=0 \
  GIT_OPTIONAL_LOCKS=0 GIT_TERMINAL_PROMPT=0 GIT_PAGER=cat GIT_NO_REPLACE_OBJECTS=1 \
/usr/bin/git --no-pager --no-lazy-fetch --no-optional-locks \
  -c core.fsmonitor=false -c core.hooksPath=/dev/null \
  -c maintenance.auto=false -c maintenance.autoDetach=false -c gc.auto=0 \
  --git-dir=<resolved common dir> {count-objects -v | fsck --unreachable --no-reflogs --no-progress}
```
- Every git call, including discovery, runs under a timeout.
- `--repo` must equal the discovered top level.
- Never pass `-c safe.directory`.
- Load-bearing on 2.56.0 (proven by ablation): `core.fsmonitor=false`, the env allowlist, and an absolute git path. The rest is defence in depth; no live vector was found without them.
- Optionally, `-c core.commitGraph=false -c core.multiPackIndex=false --no-references` removes all three fsck children (trace showed zero). It also drops verify coverage that the counts do not need. [INFERENCE: the counts do not depend on those verifies; not measured.]
- `HOME` was only tested as an empty scratch dir. [INFERENCE: with `GIT_CONFIG_GLOBAL=/dev/null` any value is inert.]

## Attack log
- **ATTACK (counter blindness, C1 frozen case set):** cases 1–8 never plant hostile config or env. A tool that runs plain `git count-objects -v` / `git fsck --unreachable --no-reflogs` with no envelope would score `cases=8 pass=8` while still executing `core.fsmonitor` and starting the daemon (findings 1–2). The manifest check in cases 1 and 2 would catch the daemon's writes only if a case set `core.fsmonitor=true`, and none does. I am not proposing a case change after data; this is reported so the L1 does not read pass=8 as envelope evidence. The envelope's evidence is this probe log.
- **ATTACK (stderr rule as a false guard):** "any other stderr is a failure" fires after the fsmonitor hook has already run (finding 1). It is a detector, not a preventer.
- **ATTACK (model envelope inherited as-is):** copying souji-repo-structure.sh's guards (lines 150-177) into the size census leaves findings 1, 2 and 3 open; probed in the model column.
