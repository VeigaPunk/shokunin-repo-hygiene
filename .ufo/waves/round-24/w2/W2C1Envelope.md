# W2C1Envelope — FALSIFY re-attack of the hardened C1 size-census envelope

## Status
STATUS: PASS — **survives**. I re-attacked the landed C1 tool (`tools/souji-size-census.py`
at `ca7fc1cb6dd1333096c6f3bdbad304686691d126`) with a harmless `touch`-marker program across
every vector named in my assignment plus two extra arms. Against the two census commands
(`count-objects -v`, `fsck --unreachable --no-reflogs --no-progress`) on git 2.56.0, **no attack
vector fired a marker and none changed the `.git` manifest**. Two positive controls fired,
proving the marker mechanism is live. The FIFO vector behaved exactly as the docstring predicts
(hang → timeout → exit 1, no write, no exec). I could not falsify the envelope.

## Evidence
- Revisions: attacked tool = `git -C <lane> show ca7fc1cb6dd1333096c6f3bdbad304686691d126:tools/souji-size-census.py` (extracted to scratch and run verbatim). Lane `master` observed at `d3666c3ef291c0c6c7827ffcfb58471c4b8d54f7` (moved during the run; I attacked the assigned landed blob, not the tip). git: `git version 2.56.0`.
- Harness: `/var/tmp/souji-r24-W2C1Envelope/` (removed at end). Each probe used its own repo under `repos/`, each with one unreferenced (dangling) blob so `fsck` always prints `unreachable blob …` — i.e. the walk really ran. A per-probe marker program writes `marks/fired-<tag>`; before/after I snapshot a manifest of the COMMON git dir (`find … -printf '%y %m %s %p'` + `sha256sum` of every regular file). Tool invoked exactly as `python3 -B tool.py --repo <repo>` with the vector set in the **caller** env/config.
- Envelope mechanics confirmed by reading the landed source: child env is built from an **allowlist dict** and passed as `subprocess.run(argv, env=env, …)` (so no caller `GIT_*`/`PATH` is inherited); git is the absolute `/usr/bin/git`; `CONFIG` forces `-c core.fsmonitor=false -c core.hooksPath=/dev/null` (+ maintenance/gc off); `TIMEOUT_S = 900` on every call including discovery `rev-parse`.
- To exercise the FIFO path cheaply I patched **a scratch copy only** (`tool5.py`, `TIMEOUT_S = 5`, verified `grep -n '^TIMEOUT_S'` → `74:TIMEOUT_S = 5`); the landed tool is unmodified.

### Positive controls (marker mechanism is live)
```
==== raw git + repo core.fsmonitor=<marker> + fsck (no envelope) ====
POS CONTROL fsmonitor: FIRED (mechanism works)
==== raw git + GIT_CONFIG_COUNT core.fsmonitor=<marker> + fsck ====
POS CONTROL GIT_CONFIG_COUNT: FIRED
marks/log:
  FIRED tag=posctl-fsmon argv=[2 1792921262726325403] cwd=.../repos/posctl
  FIRED tag=posctl-cfgcount argv=[2 1792921262730679772] cwd=.../repos/posctl
```
Both unguarded arms executed the `touch` marker (fsmonitor is called with argv `2 <token>`),
so a null result below is a real defence, not a dead harness.

### Attack probes (each: exit, marker verdict, manifest verdict)
Every tool run returned `exit=0`, `census.status=ok`, the dangling blob counted as
`unreachable`, and in every case `markers: NONE fired` / `manifest: UNCHANGED`:

```
v1-fsmonitor            repo core.fsmonitor=<marker>                 exit=0 NONE fired UNCHANGED
v1b-wtfsmon             config.worktree core.fsmonitor=<marker>      exit=0 NONE fired UNCHANGED
v2-GIT_EXEC_PATH        GIT_EXEC_PATH=<dir with fake git>            exit=0 NONE fired UNCHANGED
v3-GIT_CONFIG_COUNT     GIT_CONFIG_COUNT/KEY_0/VALUE_0=core.fsmonitor exit=0 NONE fired UNCHANGED
v4-GIT_CONFIG_PARAMETERS GIT_CONFIG_PARAMETERS='core.fsmonitor=<m>'  exit=0 NONE fired UNCHANGED
v5-GIT_TRACE2_EVENT     GIT_TRACE2_EVENT=<path>                      exit=0 NONE fired UNCHANGED
v6-GIT_DIR              GIT_DIR=<other repo>/.git                    exit=0 NONE fired UNCHANGED
v7-poisoned-PATH        PATH=<dir with fake git>:/usr/bin:/bin       exit=0 NONE fired UNCHANGED
v8-alternateRefsCommand core.alternateRefsCommand=<marker> (+alt)   exit=0 NONE fired UNCHANGED
v9-packObjectsHook      uploadpack.packObjectsHook=<marker>          exit=0 NONE fired UNCHANGED
```
`v6` output shows the census stayed on the real repo despite `GIT_DIR`:
`census.common_dir=/var/tmp/souji-r24-W2C1Envelope/repos/v6/.git` (not `v6-other`).
Final `ls marks/fired-*` → only `fired-posctl-cfgcount`, `fired-posctl-fsmon`; the eight
attack marker programs (`mk-v1-fsmonitor.sh`, `mk-v1b-wtfsmon.sh`, `mk-v3-cfgcount.sh`,
`mk-v4-cfgparams.sh`, `mk-v8-altrefs.sh`, `mk-v9-uphook.sh`, plus the `execpath`/`poisonpath`
fake `git`s) all existed on disk (live references) yet never ran.

### FIFO in include.path (DoS path, scratch 5 s timeout)
```
config:  [include]
             path = .../repos/v10b/evil.fifo
cmd: python3 -B tool5.py --repo .../repos/v10b
exit=1 elapsed=5s
souji-size-census: git failure: /usr/bin/git … -c core.fsmonitor=false … -C …/v10b
  rev-parse --path-format=absolute --git-common-dir --git-dir --is-bare-repository
  --show-toplevel timed out after 5s
markers: NONE fired
manifest: UNCHANGED
lingering git on repo: (none)
```
Discovery `rev-parse` (the tool's first config-reading call) blocks on the FIFO; the per-call
timeout fires and the tool reports a `GitFailure` → **exit 1**, with no marker and no write.
In the landed tool this is exit 1 after 900 s. Matches the docstring ("a FIFO in include.path …
hangs git; no -c override exists; every git call has a 900 s timeout") and wave-1 finding #5.

## Findings
1. **No falsification.** The allowlist child-env (`env=` dict, not caller-env-minus-GIT_\*)
   defeats every caller-environment vector in my list: `GIT_EXEC_PATH` (v2), `GIT_CONFIG_COUNT`
   (v3), `GIT_CONFIG_PARAMETERS` (v4), `GIT_TRACE2_EVENT` (v5), `GIT_DIR` (v6), and a poisoned
   `PATH` `git` (v7) — none reached the child. Location: `tools/souji-size-census.py` (blob
   `ca7fc1c`) `git_env()` returns a fixed dict and `git()` calls `subprocess.run(argv, env=env,
   stdin=subprocess.DEVNULL, capture_output=True, timeout=TIMEOUT_S)`; verbatim quote (≤25 words):
   "p = subprocess.run(argv, env=env, stdin=subprocess.DEVNULL, capture_output=True, timeout=TIMEOUT_S)".
2. **`core.fsmonitor=<marker>` is neutralized** in repo config (v1) and in `config.worktree`
   (v1b) by the forced `-c core.fsmonitor=false` (command scope beats both). Positive control
   proves the same key fires `touch` under raw git. Location: `souji-size-census.py` `CONFIG`
   tuple; verbatim quote (≤25 words): "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null".
3. **`core.alternateRefsCommand` (v8) and `uploadpack.packObjectsHook` (v9) never fire** on
   `count-objects -v` / `fsck --unreachable` — they are advertising/upload-pack only, confirming
   wave-1 finding #9. No `-c` guard is even needed for these two commands.
4. **FIFO include.path is a bounded DoS, not an exploit** (v10): hang → 900 s timeout → exit 1,
   no marker, no write, no lingering git. This is the already-disclosed operability limit
   (wave-1 finding #5), not a new attack.

## Attack log
- **ATTACK (repo `core.fsmonitor=<marker>`):** planted in repo config (v1) and `config.worktree`
  (v1b). RESULT: survives — `markers: NONE fired`, `manifest: UNCHANGED`; forced `-c core.fsmonitor=false` wins.
- **ATTACK (caller `GIT_EXEC_PATH` → fake `git`):** v2. RESULT: survives — allowlist env drops it; absolute `/usr/bin/git` used.
- **ATTACK (caller `GIT_CONFIG_COUNT`/`KEY_0`/`VALUE_0=core.fsmonitor`):** v3. RESULT: survives — not inherited by child.
- **ATTACK (caller `GIT_CONFIG_PARAMETERS=core.fsmonitor=<marker>`):** v4. RESULT: survives — not inherited.
- **ATTACK (caller `GIT_TRACE2_EVENT=<path>`):** v5. RESULT: survives — no trace file written.
- **ATTACK (caller `GIT_DIR=<other repo>`):** v6. RESULT: survives — census stayed on the real repo (`common_dir=…/v6/.git`).
- **ATTACK (poisoned `PATH` `git`):** v7. RESULT: survives — absolute git + fixed child `PATH=/usr/bin:/bin`.
- **ATTACK (`core.alternateRefsCommand` with an alternate present):** v8. RESULT: survives — not fired by these commands.
- **ATTACK (`uploadpack.packObjectsHook` + `uploadpack.allowFilter`):** v9. RESULT: survives — upload-pack only.
- **ATTACK (`include.path` → FIFO, DoS):** v10 on scratch `TIMEOUT_S=5` copy. RESULT: survives — exit 1 after timeout, no write/exec, no lingering process.

Commands run: harness `/var/tmp/souji-r24-W2C1Envelope/{run.sh,fifo.sh}` (removed); each probe
`python3 -B <scratch tool copy> --repo <scratch repo>`; positive controls under
`env -i PATH=/usr/bin:/bin HOME=/nonexistent LC_ALL=C … /usr/bin/git … fsck`. Tooling installs:
none. Scratch removed before finishing.
