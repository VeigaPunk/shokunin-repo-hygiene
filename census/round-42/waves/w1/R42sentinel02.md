# R42sentinel02 — security and safety review of the C2 patches leg

Seat: R42sentinel02 (sentinel, leaf, no subagents). Lane tip read: `afe17f416eec04dcf3f480b580a8f928de61d19d` (freeze). Frozen bytes re-checked after all runs:

```
fa44392d11338daa73b3b4b9b2fc8f89879c099e9bf278d7b45fa55dea5d0ac1  census/round-42/c2-counter.py      (matches preregistration)
148b7b87411eb282e0207cf5471d55be81e03d4a26ffafd96df37b4db4fd4511  census/round-42/c2-cases.tsv        (matches)
8131847bcfc5ecef513eb608a67ec18feab44f7a8b6c094824b082ffe52a76e2  tools/souji-freeze-check.py         (r41 tool at HEAD)
ccf456cbda2839eb186765670e1f111a1ad4272006f4dcc8d12d899c0b86e3ca  census/round-42/score-candidate.sh  (not edited by this seat)
```

Nothing in the lane, the fleet, `.ufo/state`, or any tracked file was written. All hostile tools were scored through `score-candidate.sh c2` from scratch (`/fast/scratch/hyaku/souji-r42/R42sentinel02`, deleted before yield). Copies of every tool, probe and receipt are under this seat directory (`attacks/`, `probes/`, `receipts/`), so every path below is citable.

Tooling: none installed or upgraded. Host interpreter `/usr/bin/python3` = CPython 3.14.8; git 2.56.0.

## Verdict

**FAIL for the patches leg as a measure of its predicate.** The predicate (`census/round-42/c2-counter.py` docstring, leg `patches`) says a self-test that does not exercise the digest, freeze-detection or ancestry logic must be rejected. A hostile candidate reaches `patches=3/3` with no such logic: it reads `PYTHONPATH` / `SOUJI_R42_PATCH` and exits 1 when either is present (`attacks/v2-stub-tripwire.py`, receipt `receipts/score-c2-v2-stub-tripwire.txt`: `selftest ok rc=0 summary=(13, 13, 0)`, `patches=3/3`). The leg accepts any non-zero exit under the patch, so the detection can be a tripwire rather than the logic. The overall target also needs 37/37 cases, which I did not build; so the defeat is shown at leg level, not as a full `SUMMARY ... target` line.

The other attacks (below) are measurement defects the L1 must record as limits, not contained behaviour. Under `score-candidate.sh` the candidate's `--root` is a scratch clone, so the counter's own legs do not hand it the lane. Nothing contains absolute-path writes, though: the lane is writable by the same user (row 9, `access-W_OK lane=True`), and I did not attempt a write there.

Premise S259 (sitecustomize on PYTHONPATH): **holds** as the patches leg uses it, on 3.14.8 (empirical) and on the live docs (3.15.2 text). Details in the section below.

## Attack table

Columns: attack | observed | reaches target? | limit text for the lesson.

| # | attack (tool / probe) | observed (receipt) | reaches target? | limit text for the lesson |
|---|---|---|---|---|
| 1 | **Environment tripwire + always-green self-test** (`attacks/v2-stub-tripwire.py`): exit 1 if `PYTHONPATH` set or `sitecustomize` in `sys.modules`, otherwise print `SELFTEST cases=13 pass=13 fail=0` | `selftest ok`, `patches=3/3`; cases 24/37 (the r41 body); `receipts/score-c2-v2-stub-tripwire.txt` | **Yes at leg level** (`patches=3/3`, `selftest=ok`). Whole SUMMARY still needs 37/37 cases, not built. | The patches leg proves only that the self-test exits non-zero when an env-visible patch is present. A three-line environment check satisfies it with no digest, freeze or ancestry logic. The leg needs the failing case names (`sha256-*`, `freeze-*`, `merge-base`) under each patch, and the L1 shim audit (rule 3) must classify tripwires. |
| 2 | Always-green stub, no tripwire (`attacks/v4-stub-plain.py`) | `selftest ok`, `patches=0/3` (`receipts/score-c2-v4-stub-plain.txt`) | No | The naive always-green stub is rejected; the env-aware one (row 1) is not. Frozen control B does not test the env-aware stub, so the control is not sufficient. |
| 3 | Honest self-test, 13 real checks (`attacks/v0-honest.py`: NIST sha256 vectors, real `git log --diff-filter=A`, `merge-base`, `--is-ancestor` on a scratch repo) | `selftest ok`, `patches=3/3` (`receipts/score-c2-v0-honest.txt`) | Leg yes (the intended path); cases 24/37 | Baseline: the leg works for a logic-exercising tool. Used as control for rows 5–7. |
| 4 | **Re-exec under `python -I -S`** when not isolated (`attacks/v5-reexec-isolated.py`) | `selftest ok`, `patches=0/3` (`receipts/score-c2-v5-reexec-isolated.txt`) | No (it lowers `patches`) | Re-exec removes the patch (`-I` ignores PYTHONPATH, `-S` skips sitecustomize). The leg then counts exit 0 as "not detected", so a robust candidate is penalised. The leg cannot distinguish "isolated from the patch" from "does not run the logic". No candidate gains from this route. |
| 5 | **Strip the patch dir from `sys.path` and pop `sys.modules['sitecustomize']`** (`attacks/v6-pathstrip.py`) | `selftest ok`, `patches=3/3` (`receipts/score-c2-v6-pathstrip.txt`) | Leg yes (no gain over row 3) | Removing the path after startup does not undo the patch: the monkey-patches to `hashlib.sha256` / `subprocess.run` are already in place. Path removal is not a defeat. |
| 6 | **Use `hashlib.new('sha256', …)` instead of `hashlib.sha256`** (`attacks/v7-hashlib-new.py`) | `selftest ok`, `patches=2/3` (`receipts/score-c2-v7-hashlib-new.txt`) | No (it lowers `patches`) | P1 is observed only through the name `hashlib.sha256`. An ordinary, honest API choice makes P1 invisible, so the leg rejects a correct tool. The patch is keyed to one constructor name. |
| 7 | **Read the env from inside the candidate** (`attacks/v8-probe-writes.py`, `probes/v8-probe.txt`) | Env keys seen in the last (P3) run: `PYTHONPATH`, `SOUJI_R42_PATCH`, `TMPDIR`, `PATH`, `GIT_*`, `LC_ALL`; `HOME` unset | Gives the candidate the patch's identity. This is the enabler for row 1. | `SOUJI_R42_PATCH` and `PYTHONPATH` are visible to the candidate. Any leg whose patch is an env var is keyed by the candidate. The counter's own sentinel name is in the candidate's environment; rule 3 (L1 audit) is the only control. |
| 8 | **Write the cwd** (v8, same run) | `cwd-write=ok`; `probes/cwd-canary-R42sentinel02.txt` written into the caller's cwd (`probes/v8-probe.txt: cwd=…/cwdprobe`) | Not needed for target | `run_tool` / `run_selftest` do not set `cwd=`; the candidate inherits the caller's working directory. A seat invoking from the fleet root gets candidate writes in the fleet root [INFERENCE from the same mechanism; the probe ran in a scratch cwd]. The counter should pass `cwd=scratch`. |
| 9 | **Write outside TMPDIR by absolute path** (v8) | `abs-write=ok` to `probes/abs-canary.txt` (a seat-scratch path outside TMPDIR); `access-W_OK lane=True`, `fleet-root=True` (capability observed, **no write attempted in the lane or fleet**) | Not needed for target | TMPDIR is a convention, not a boundary. The candidate runs as the same user with no sandbox. Any path the user can write is reachable. The limit text must say so; the counter cannot enforce containment. |
| 10 | **Poison sibling case dir** (`attacks/v11-scratch-poison.py`: on `--root …/cand-clean`, `mkdir` the sibling `cand-clean-dispatch-after`) | Counter crashed: `FileExistsError … cand-clean-dispatch-after`, rc=1, no `SUMMARY`; scratch removed by `score-candidate.sh` trap (`receipts/score-c2-v11-scratch-poison.txt`) | No (DoS of the measurement) | `build()` calls `os.makedirs(d)` without `exist_ok`, and the candidate's `--root` parent is the counter's shared scratch. A candidate can crash the counter, and exit 1 is then indistinguishable from "target unmet" except by the absence of `SUMMARY`. |
| 11 | **Shadow `sitecustomize.py` in the shared scratch** (`attacks/v13-shadow-sitecustomize.py`) | `shadow-imports=0` (`receipts/v13-shadow-count.txt`); the shadow never ran | No | Negative: a script-dir `sitecustomize.py` is **not** imported (startup ordering; `receipts/premise-extra-and-bytecode.txt`, script-dir section: `NOT imported`). The sitecustomize vector via script dir is closed on 3.14.8. |
| 12 | **Shadow `argparse.py` in the shared scratch** (`attacks/v13b-shadow-argparse.py` + `attacks/shadow-argparse.py.txt`) | `shadow-argparse-imports=44` (`receipts/v13b-shadow-count.txt`, `probes/shadow-argparse.log`); the shadow forwards to the real module, so verdict unchanged here | Not needed for target; a hostile shadow could alter any later verdict | `sys.path[0]` is the tool's directory, which is the counter's shared scratch. Every later interpreter run in the same counter invocation imports the candidate's module. The 37 cases and stubs are **not independent**. |
| 13 | **`-B` in children** (E1–E3, `receipts/premise-extra-and-bytecode.txt`; `attacks/v9-child-bytecode.py`) | E1 `python3 -B` import: no `__pycache__`. E2 candidate sets `sys.dont_write_bytecode=False`: pyc written. E3 child `python3` spawned without `-B`: pyc written. | Not needed for target | `-B` is passed only to the counter's own children (`run_tool` line 258, `run_selftest` line 344). It is a flag, not an env var, so it does not propagate, and the candidate can override it at run time. `env()` does not set `PYTHONDONTWRITEBYTECODE`. **Correction:** the v9 probe's `tool-self-import-pycache=True` is contaminated by earlier runs in the shared `bc-target`; E1 is the clean result. |
| 14 | **Hostile caller `PYTHONPATH`** (`attacks/probe-scripts/callerpp-sitecustomize.py`; run `env-caller-pythonpath-v0.txt`) | `probes/callerpp-sitecustomize-log.txt`: exactly one import, by the **counter process** itself (no `-I`/`-S`). Zero imports in children. | No | `env()` whitelists the children's environment, so hostile caller `PYTHONPATH` does not reach children. The counter process itself is not isolated: a caller `sitecustomize` runs before the counter's first line. |
| 15 | **Hostile caller `PATH`** (`attacks/probe-scripts/path-shim-python3.sh`; run `env-path-shim-v0.txt`) | `probes/path-shim-log.txt`: 119 shim invocations; the counter's children resolved `python3` through the caller's PATH | No (no target gain) | `env()` passes `PATH` verbatim. `python3` and `git` are resolved by the caller's PATH, so a hostile PATH replaces the interpreter for every child. The counter should use `sys.executable` and a pinned `git` path. |
| 16 | **Self-test timeout with a detached grandchild** (instrumented copy, `attacks/c2-counter-timeout3.instrumented-copy.py` with `timeout=3`; `attacks/v10-hang-grandchild.py`; `receipts/hang-timeout-instrumented.txt`) | Self-test `rc=124`; counter's scratch removed (`leftover=0`); the grandchild survived the counter and wrote `probes/late-outside.txt` at 21:24:05, about 14 s after the counter exited | No | `subprocess.run(timeout=…)` kills only the direct child. The counter removes `work` in `finally`, but a candidate's grandchild outlives the counter and writes outside scratch. Limit: a timed-out candidate can leave processes running. The counter should `start_new_session` and `os.killpg`. |
| 17 | **Cases timeout** (instrumented copy, `attacks/v12-hang-cases.py`; `receipts/hang-cases-timeout-instrumented.txt`) | `subprocess.TimeoutExpired` uncaught in `run_tool` (no try), traceback, `counter_rc=1`, no `SUMMARY`, `leftover-scratch=0` | No (DoS) | `run_tool` has no `TimeoutExpired` handler; a hung case crashes the counter. Scratch is removed; the verdict is an uncaught exception, not `COULD-NOT-EVALUATE`. |
| 18 | **Hostile `GIT_DIR` in the scorer's environment** (`receipts/env-GIT_DIR-decoy-scorer.txt`, `receipts/env-GIT_DIR-decoy-state.txt`) | Decoy repository gained a `candidate` commit (`decoy-commits=2`); the counter then refused with rc=2 because the rev is absent from the clone | No (but it violates the scorer's contract) | `score-candidate.sh` does not scrub the caller's environment: `git -C "$C" add -A && commit` (line 34) honours `GIT_DIR`. With `GIT_DIR` pointing at the lane the commit would land in the lane. The scorer must `env -i` or unset `GIT_*`. Not tested against the lane. |
| 19 | **Real / retro / retro_clean legs run the candidate with `--root` = the caller's tree** (`c2-counter.py` lines 396, 399, 402) | Under `score-candidate.sh` the root is a scratch clone; a direct L1 run over the lane passes the **live lane** as `--root`. The candidate has write capability there (row 9). Not exercised against the lane. | No | The measurement run executes the candidate against the working tree it is judged on. Any landed candidate can mutate the lane during measurement. The counter should run legs against a per-run copy. |
| 20 | **`dest` path traversal in `score-candidate.sh`** (`cp "$src" "$C/$dest"`, line 30) | Not exercised. [INFERENCE] `dest` containing `../` writes outside the clone. | No | `dest` is operator input, not candidate input, so this is low severity; the scorer should reject `..` and absolute destinations. |

## S259 premise: what the docs say (read, not inferred)

Sources: live `https://docs.python.org/3/library/site.html` (sha256 `620581fe…` = snapshot `census/round-42/sources/python-3-library-site.html`, identical) and live `https://docs.python.org/3/using/cmdline.html` (sha256 `c19141f2…`, not snapshotted). Both pages are the **Python 3.15.2** documentation; the host runs 3.14.8. Excerpts: `receipts/docs-and-host-state.txt`; full extracted text `probes/live-site-text.txt`, `probes/live-cmdline-text.txt`.

- **sitecustomize discovery (site page):** "After these path manipulations, an attempt is made to import a module named `sitecustomize`" and "If this import fails with an ImportError … it is silently ignored. … Any other exception causes a silent and perhaps mysterious failure of the process." So the import is an ordinary `sys.path` search performed after site's own path work.
- **`-S` (site page + cmdline):** "Python startup option `-S` blocks this" (site automatic import); `-S` disables the import of `site` and the site-dependent path manipulations (cmdline `-S`). With `-S`, `sitecustomize` is not imported. Verified: `python3 -S -B -c pass` → NO-IMPORT.
- **`-I` (cmdline):** "run Python in isolated mode. This also implies `-E`, `-P` and `-s` … sys.path contains neither the script's directory nor the user's site-packages … All `PYTHON*` environment variables are ignored." The page does **not** say `-I` disables `site`. Verified: under `-I`, `site` is loaded and `ENABLE_USER_SITE` is False. So `-I` defeats a PYTHONPATH sitecustomize but not a sitecustomize reachable from a non-PYTHONPATH `sys.path` entry [INFERENCE for site-packages; not tested, since writing to system site-packages was out of scope].
- **`-E` and PYTHONPATH (cmdline):** `-E` ignores `PYTHON*` variables "e.g. PYTHONPATH". `PYTHONPATH` "augments the default search path". The site page itself contains no `PYTHONPATH` text (0 hits); the link is made by the cmdline page plus startup order.
- **`-B` (cmdline):** "If given, Python won't try to write .pyc files"; `PYTHONDONTWRITEBYTECODE` is the env equivalent. Flag-only, so not inherited by children (row 13).
- **`usercustomize` (site page):** imported "if `ENABLE_USER_SITE` is true", part of `sys.path` "unless disabled by `-s`". The counter's children are not `-s`. Host state: `~/.local/lib/python3.14/site-packages` exists; `import usercustomize` → ModuleNotFoundError (none present now). So a user-writable `usercustomize.py` would reach every child: **not blocked by the env whitelist** [INFERENCE from docs; not tested].

Empirical premise checks (3.14.8; `receipts/premise-experiments.txt`):

| invocation with `PYTHONPATH=<dir with sitecustomize.py>` | sitecustomize imported |
|---|---|
| `python3 -B -c pass` | yes |
| `python3 -I -B` | no |
| `python3 -S -B` | no |
| `python3 -E -B` | no |
| `python3 -s -B` | yes |
| `python3 -P -B` | yes |
| `python3 -I -S -B` | no |
| `PYTHONSAFEPATH=1 python3 -B` | yes |

**Verdict on S259:** the mechanism the patches leg relies on (sitecustomize on PYTHONPATH, imported at startup, silently) holds on the host and matches the docs. The premise does not establish that a candidate cannot see or defeat it; that is what rows 1, 4, 5, 7 and 8 show.

## Commands actually run (condensed; exact outputs in receipts)

```
sha256sum census/round-42/sources/python-3-library-site.html            # = 620581fe…
curl -sSL --max-time 60 -o live-site.html https://docs.python.org/3/library/site.html     # rc=0
curl -sSL --max-time 60 -o live-cmdline.html https://docs.python.org/3/using/cmdline.html  # rc=0
python3 -B … (premise matrix; see receipts/premise-experiments.txt)
bash census/round-42/score-candidate.sh c2 /fast/scratch/hyaku/souji-r42/R42sentinel02 tools/souji-freeze-check.py=<cand>.py
   # run for: v0-honest, v2-stub-tripwire, v4-stub-plain, v5-reexec-isolated, v6-pathstrip,
   #          v7-hashlib-new, v8-probe-writes, v9-child-bytecode, v11-scratch-poison, v13-shadow-sitecustomize, v13b-shadow-argparse
   # env runs: PYTHONPATH=<callerpp> and PATH=<shim>:$PATH around score-candidate.sh c2 (v0-honest)
   # GIT_DIR=<decoy>/.git score-candidate.sh c2 (v4-stub-plain)   [decoy repository, not the lane]
instrumented copy (`timeout=300` replaced by `timeout=3`, 2 occurrences asserted by a one-off rewrite) run directly against a scratch clone:
   python3 -B <scratch>/instr/c2-counter-timeout3.py --root <clone> --rev <rev> --scratch <scratch>/instr   # rows 16, 17
```

Score lines (verbatim `SUMMARY` lines are in the receipts; representative):

```
SUMMARY cases=37 pass=24 fail=13 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3   # v0-honest, v2-stub-tripwire, v6-pathstrip, v8-probe-writes, v9-child-bytecode, v13-shadow-sitecustomize, v13b-shadow-argparse
SUMMARY cases=37 pass=24 fail=13 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=0/3   # v4-stub-plain, v5-reexec-isolated
SUMMARY cases=37 pass=24 fail=13 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=2/3   # v7-hashlib-new
# v11-scratch-poison: no SUMMARY (counter crashed with FileExistsError, rc=1). Timeout copies (rows 16-17): see receipts/hang-*.txt.
```

Note: every hostile tool scored only 24/37 cases because each is the r41 body plus a self-test; the 13 new r42 cases are not implemented here (that is the executors' work). The `patches` and `selftest` legs are the only ones these tools were built to move.

## Limits to write into the round lesson (C2 operability)

1. The patches leg is defeated at leg level by an env tripwire (row 1). The leg must require the failing case names under each patch, not only a non-zero exit.
2. Re-exec isolation and hashlib-name choice are penalised as "undetected" (rows 4, 6). The leg conflates "robust" with "not exercised".
3. Candidate environment exposes `SOUJI_R42_PATCH` and `PYTHONPATH` (row 7). The L1 shim audit (rule 3) is the only control.
4. No containment: absolute writes succeed (row 9); cwd is inherited (row 8); scratch siblings can be pre-created (row 10); shared scratch shadows stdlib modules for later runs (row 12: 44 later imports); children do not inherit `-B` (row 13); children resolve `python3` via caller PATH (row 15).
5. Timeouts: orphan grandchildren survive (row 16); case timeouts crash without `COULD-NOT-EVALUATE` (row 17).
6. `score-candidate.sh` does not scrub the environment: `GIT_DIR` redirects the commit (row 18); `dest` is unvalidated (row 20).
7. Measurement legs run candidates against `--root` = caller tree (row 19).
8. Docs premise: the site page does not mention PYTHONPATH; `-I` does not imply `-S`; live docs are 3.15.2, host is 3.14.8 (verified on 3.14.8 only).

## Suggested remediation (for the L1 to decide; not edits to frozen files)

- Patches leg: require `SELFTEST` output to name at least one failing case from the digest / freeze / ancestry set under each patch, and reject a non-zero exit with no named failure.
- `sitecustomize`: after patching, scrub its traces (`os.environ.pop('PYTHONPATH')`, `os.environ.pop('SOUJI_R42_PATCH')`, `del sys.modules['sitecustomize']`, remove `pdir` from `sys.path`). This alone does not stop a candidate reading the patch's effects, so pair it with the named-failure requirement.
- Patch `hashlib.new` and the `_hashlib` constructors as well as `hashlib.sha256`.
- Child runs: `cwd=scratch`, `env` with `PYTHONDONTWRITEBYTECODE=1`, `sys.executable` (absolute), `start_new_session=True` and `os.killpg` on timeout, `TimeoutExpired` caught and reported as `COULD-NOT-EVALUATE`.
- Run legs against a per-run copy of the tree, not the caller's `--root`; pre-clean scratch siblings or use `exist_ok` with unique names.
- `score-candidate.sh`: `env -i` with an explicit whitelist (or unset `GIT_*`), and reject `dest` containing `..` or starting with `/`.
- Frozen-instrument note: none of these edits is made here; each is a finding for the L1 under rule 1.

## Evidence index (seat-relative)

- `attacks/`: `gen-candidates.py` (generator for v0–v9), `v0-honest.py`, `v2-stub-tripwire.py`, `v4-stub-plain.py`, `v5-reexec-isolated.py`, `v6-pathstrip.py`, `v7-hashlib-new.py`, `v8-probe-writes.py`, `v9-child-bytecode.py`, `v10-hang-grandchild.py`, `v11-scratch-poison.py`, `v12-hang-cases.py`, `v13-shadow-sitecustomize.py`, `v13b-shadow-argparse.py`, `shadow-argparse.py.txt`, `r41-tool-lane-HEAD.py` (lane tool at HEAD, unchanged), `c2-counter-timeout3.instrumented-copy.py` (copy of the frozen counter with `timeout=3`; **not** the frozen file), `probe-scripts/` (runners and the sitecustomize/shim used).
- `probes/`: `v8-probe.txt`, `cwd-canary-R42sentinel02.txt`, `abs-canary.txt`, `late-outside.txt`, `callerpp-sitecustomize-log.txt`, `path-shim-log.txt`, `shadow-argparse.log`, `live-site-text.txt`, `live-cmdline-text.txt`.
- `receipts/`: `score-c2-*.txt` (v0, v2, v4, v5, v6, v7, v8, v9, v11, v13, v13b), `env-caller-pythonpath-v0.txt`, `env-path-shim-v0.txt`, `env-GIT_DIR-decoy-scorer.txt`, `env-GIT_DIR-decoy-state.txt`, `hang-timeout-instrumented.txt`, `hang-cases-timeout-instrumented.txt`, `premise-experiments.txt`, `docs-and-host-state.txt`, `v13-shadow-count.txt`, `v13b-shadow-count.txt`.
- `receipts/premise-extra-and-bytecode.txt`: `PYTHONSAFEPATH` row, E1–E3 bytecode experiments, `-I`/`-S` site state, script-dir `sitecustomize` test. `receipts/docs-and-host-state.txt`: live-page sha256, cmdline excerpts, host `sitecustomize`/`usercustomize` state.

## Not done / residual

- A 37/37 candidate was not built; the overall SUMMARY target was therefore not demonstrated, only the patches and selftest legs.
- Rows 19 and 20 are code-reading plus a capability observation; no write to the lane or fleet was made.
- The usercustomize and site-packages sitecustomize paths are [INFERENCE] from the docs.
- Docs are 3.15.2; host is 3.14.8; tested on 3.14.8 only.
- The v9 `tool-self-import-pycache` probe line is contaminated by shared state; the clean E1–E3 experiments replace it.
