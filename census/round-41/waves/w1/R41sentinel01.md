# R41sentinel01 — safety review: C3/R1 probe recipes and scoring harness

Role: sentinel (leaf, read-only; no candidate files written).
Freeze: lane HEAD `e2a74312af4233963e44e4dbb38838ece07b8bd2` (re-checked after my runs: still `e2a7431`; `git status --porcelain -- census tools tests corpus` = 0 lines).
Frozen bytes were exported with `git show <freeze>:<path>` into my scratch and hashed:
`tools/souji-worktree-drift.py` sha256 `b2a603cf…34dc6` (matches the pinned PRISTINE value);
`census/round-41/c3-counter.py` sha256 `9ef99e8f20805501c3944e4b598e3fd7b7ac3ea3914674fa46e6affdc1e537ca`.
Not present at freeze: `tests/fixtures/r41-refusal-sites.py`, `tests/fixtures/r41-drift-record-order.py`. Every candidate-scored run therefore needs a candidate first.

## Verdict

**FAIL for unconfined candidate scoring.** Probes and counters write only where the code says, but the harness gives a candidate fixture the full privileges of the user. Four further harness defects let a candidate or the caller's environment reach outside the scratch clone, or the lane. All of these are reproduced below in scratch, and the lane was not written by any run. The frozen drift tool itself follows a symlinked `--json` path (F1). The C3 selftest still passes (3/3), so the instrument's own scoring logic is not in question here.

## Findings

Severity: H = writes outside scratch or touches lane from a candidate or caller; M = integrity or containment gap that needs a precondition; L = hygiene.

### F1 (H, frozen tool — finding for L1, not an edit): `--json` symlinks are followed
- Code: `tools/souji-worktree-drift.py@e2a74312` L326 `json_target = os.path.realpath(os.path.abspath(args.json))`. `realpath` resolves the leaf and every ancestor before the guards at L331–348 and before `open_nofollow` (L238–281, L421). So the O_NOFOLLOW walk never sees the symlink. The docstring at L60–61 says a symlinked path component is "refused by the O_NOFOLLOW walk"; the code does not do that.
- Write set: `realpath(--json)` iff it is not the record (path or inode), not under `--root` or a measured repo/gitdir, is a regular file, and has nlink 1. Then `ftruncate(0)` (L428) and JSON write. Everything else is refused before any write (P10a/P10b/P11/P15/P17 are refused before L428).
- Reproduced (scratch `t/`): `--json work/out.json` where `out.json -> outside/victim.json`:
  ```
  == A: --json is a symlink to an outside file
  DRIFT	ABSENT	ghost	recorded regs=0
  ...rc=1
  -- ls:  lrwxrwxrwx ... out.json -> .../t/outside/victim.json
  -- victim now:  { "drift": [ { "class": "ABSENT", ... } ], "summary": { ... } }   (was VICTIM-ORIGINAL)
  ```
  Ancestor-directory form (`work/dirlink/victim.json`, `dirlink -> outside/`) overwrote the victim the same way (case G).
- Refused as designed (no write, victim intact): B hardlink nlink=2 → `REFUSAL JSON-HARDLINKED … has 2 links`, rc=2, victim `VICTIM-ORIGINAL`; C FIFO → `REFUSAL JSON-NOT-REGULAR … is not a regular file`, rc=2, returned at once; D `/dev/null` → `JSON-NOT-REGULAR`, rc=2; E record as `--json` → `JSON-IS-RECORD`, record unchanged; F directory → `JSON-NOT-REGULAR`. P11 (`/dev/null`) is harmless: it is opened O_WRONLY (no data written) and refused at fstat before any truncate.
- Fix (L1, candidate-side, now): the fixture must create or name every `--json` target itself under its own work dir and assert before invoking the tool:
  ```python
  WORK = os.path.realpath(args.work)
  def own(name):
      p = os.path.join(WORK, name)
      assert not os.path.islink(p), p                     # no symlink at the leaf
      assert os.path.realpath(p) == p, p                  # no symlinked ancestor
      return p
  ```
  Never pass a path that the fixture did not create, and never a path outside WORK.
- Fix (tool, next round, frozen so not applied here): take `os.path.realpath` of the directory only, keep the leaf name, and refuse `os.path.islink(os.path.abspath(args.json))` with `JSON-UNWRITABLE`.

### F2 (H, harness — `census/round-41/score-candidate.sh`): `--dest` traversal writes outside the scratch clone
- Code: L26–31 `dest="${pair%%=*}"; … mkdir -p "$C/$(dirname "$dest")"; cp "$src" "$C/$dest"`. No validation of `dest`.
- Reproduced (fake lane in scratch, copy of frozen script + counter; `scratch root = $S/root`):
  ```
  bash $FL/census/round-41/score-candidate.sh c3 $S/root "../../../escape-canary.txt=$S/cand.txt"
  REFUSAL COULD-NOT-EVALUATE: tool or sites table absent at fe4767b2…
  rc=2
  -rw-r--r-- … /fast/scratch/hyaku/souji-r41/R41sentinel01/escape-canary.txt
  CANDIDATE-BYTES
  ```
  The file landed one directory above the scratch root (`$S`), outside the clone and outside the score dir.
- Fix (L1, now): run only with the allowlisted dests (the header names four). Harness fix (next round):
  ```bash
  case "$dest" in ""|/*|*..*|.git|.git/*) echo "score-candidate: refused dest $dest" >&2; exit 2;; esac
  p="$(realpath -m -- "$C/$dest")"; case "$p" in "$C"/*) ;; *) echo "score-candidate: dest escapes clone" >&2; exit 2;; esac
  ```

### F3 (H, lane-touch path — harness L30): `cp` writes through tracked symlinks into their target
- The lane tip has 47 tracked symlinks at freeze (`git ls-tree -r e2a7431 | cut -c1-6` → 47× `120000`). 14 point at absolute lane paths (`/home/vgpnk/Projects/shokunin/souji-shokunin/...`), 2 at `/dev/null`, 31 relative. Examples: `tests/vault/vadv-51/fixture/vault/x2-note.txt -> /home/vgpnk/Projects/shokunin/souji-shokunin/tests/vault/vadv-51/fixture/src/x2-note.txt`; `tests/vault/vadv54-run/q/led-devnull.tsv -> /dev/null`; `tools/impl-39.sh -> souji-census.impl-39.sh`.
- Reproduced (fake lane with a tracked symlink `tests/fixtures/linked.py -> $S/victim-via-symlink.txt`): `score-candidate.sh c3 $S/root tests/fixtures/linked.py=$S/cand.txt` → `victim-via-symlink.txt` now reads `CANDIDATE-BYTES` (was `ORIGINAL`). The clone itself was removed afterwards (`rm -rf` does not follow the link; `$S/root` ended empty).
- A dest that names one of the 14 absolute-lane links rewrites a lane worktree file, unstaged, dirtying the lane.
- Fix (L1, now): before the copy, refuse a dest that is a symlink or has a symlinked ancestor; `rm -f -- "$C/$dest"` first, so the copy creates a regular file. Harness fix (next round): the `realpath -m` containment check in F2 also catches this, because the resolved path leaves `$C`.

### F4 (H, lane-touch path — harness L34): inherited `GIT_DIR` redirects the candidate commit to another repository
- Code: score-candidate.sh inherits the caller's environment; it only exports identity (L32–33) and runs `git -C "$C" add -A && git -C "$C" commit` (L34). The guard `rev-parse --show-toplevel` (L25) checks the clone's cwd, so it passes even when `GIT_DIR` points elsewhere.
- Reproduced (`FG` = fresh scratch repo; `FL` = fake lane):
  ```
  GIT_DIR="$FG/.git" bash $FL/census/round-41/score-candidate.sh c3 $S/root "cand-env.txt=$S/cand.txt"
  REFUSAL COULD-NOT-EVALUATE: --root/--rev must name a resolvable full40 commit   (counter, after the commit)
  -- commits in FG (the env repo):
  ee48b83 candidate
  -- commits in fakelane (the intended repo):
  1cdad3e fakelane            (unchanged)
  ```
- Impact: a seat that calls the harness from a lane git hook, or from a `jj-lane.sh`-style wrapper that exports `GIT_DIR`/`GIT_INDEX_FILE`, would stage the clone tree into the lane index and commit there. This is the nearest path to "lane touched by scoring".
- Fix (L1, now): `env -i PATH="$PATH" HOME="$HOME" TMPDIR="$SCRATCH" bash score-candidate.sh …`. Harness fix (next round): at the top of the script
  ```bash
  unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_OBJECT_DIRECTORY \
        GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE GIT_CONFIG_PARAMETERS
  [ "$(git -C "$C" rev-parse --absolute-git-dir)" = "$C/.git" ] || { echo "clone gitdir mismatch" >&2; exit 2; }
  ```
  The counters are not affected: their git calls run under a whitelisted `child_env` (c3-counter.py L63–66), and the fixture env I captured contained only `GIT_CONFIG_GLOBAL GIT_CONFIG_NOSYSTEM GIT_CONFIG_SYSTEM GIT_TERMINAL_PROMPT LC_ALL PATH TMPDIR` (no `GIT_DIR`, no `DISPLAY`).

### F5 (H, instrument integrity — harness L36): a candidate can replace the counter that scores it
- The counter is run from the clone at `HEAD`, which includes the candidate's own files. Nothing refuses a dest under `census/round-41/` or `tools/`.
- Reproduced: dest `census/round-41/c3-counter.py=$S/fake-counter.py` (prints `CANARY-REPLACED-COUNTER: this line came from candidate bytes`, exit 0) → output `CANARY-REPLACED-COUNTER: this line came from candidate bytes`, `rc=0`. So a `SUMMARY` line from `score-candidate.sh` can be produced by candidate code. The sites table and the tool are sha-pinned inside the counter, so only the counter file itself is exposed.
- Fix (L1, now): never pass a dest under `census/`, `tools/`, or any `*-counter.py`; check that `git -C "$LANE" diff --stat e2a7431 -- census tools` is empty before scoring, and quote the counter's own sha in the report. Harness fix (next round): refuse those dests; run the counter from `git -C "$LANE" show "$FREEZE:census/round-41/$claim-counter.py"` into `$D`, not from the clone.

### F6 (H, fixture confinement — `c3-counter.py` L91–94, `r1-counter.py` L105–109, and `run_fixture` in both): no containment of the candidate fixture
- Both counters run `python3 -B <fixture> --tool … --work …` with the caller's cwd and the caller's filesystem and network. `child_env` whitelists the environment (verified above), so environment secrets are not passed; the filesystem and network are not confined.
- Reproduced in the counter's own code path, `score()` via a driver with cwd = `$S/caller-cwd`: the fixture's relative write landed in the caller's cwd (`caller-cwd/relative-canary.txt`), and its absolute write landed at `$S/abs-canary.txt`. End-to-end through `score-candidate.sh` (fake lane2 with the frozen tool and sites table, cwd = `$S/caller-cwd4`): `caller-cwd4/relative-canary4.txt` and `$S/abs-canary3.txt` both written; the scratch root was left empty. This is the host-guard hazard: if the L1 runs the harness from the fleet root, a relative write from a candidate lands in the fleet root.
- Containment check (reproduced): the same fixture under `bwrap 0.13.1` (`/usr/bin/bwrap`, pre-existing, not installed here) with `--ro-bind / / --dev /dev --proc /proc --unshare-all --die-with-parent --bind WORK WORK --chdir WORK`: the relative write succeeded inside `WORK`, the absolute write was refused (`Read-only file system`), and network is unshared.
- Patched COPY (in scratch only, the frozen counter untouched): `run_fixture` prefixes the command with the bwrap line above and uses `chdir` into the scratch. The copy's selftest still returned `SELFTEST cases=3 fail=0` and the hostile canary was confined as above.
- Fix (L1, now): run the candidate fixture under the same bwrap line by hand as a pre-check, and never run the harness from the fleet root. Harness fix (next round): in `run_fixture`, `cmd = ["bwrap", "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc", "--unshare-all", "--die-with-parent", "--bind", scratch, scratch, "--chdir", scratch] + ["python3", "-B", fixture, "--tool", tool, "--work", scratch]`.

### F7 (M, uid 0 — `score-candidate.sh` has no check; `r1-counter.py` has no check): root turns F2 and F6 into system-wide writes
- The only uid guard is in `c3-counter.py` L232 (`os.geteuid() == 0` → exit 2). `score-candidate.sh` copies candidate bytes (L30) before the counter ever checks uid. `r1-counter.py` has no uid check at all (grep for `geteuid|euid|getuid` returns only the c3 line).
- Not reproduced: I did not run as root (and would not). This is a code-read finding.
- Fix (L1, now): run as the unprivileged user only. Harness fix: first line `[ "$(id -u)" -ne 0 ] || { echo "refuses uid 0" >&2; exit 2; }` in score-candidate.sh and in r1-counter.py.

### F8 (M, fixture timeout — both counters, `subprocess.run(timeout=900)`): only the direct child is killed
- Reproduced with the same `subprocess.run(…, timeout=3)` pattern: a fixture that spawned `sleep 1234.5678` in a new session. `TimeoutExpired raised; direct child killed`; then `pgrep -af 'sleep 1234.5678'` → `833888 sleep 1234.5678`, still alive. I killed that one process (my own spawned grandchild, pid 833888); `none after cleanup`.
- Also: `TimeoutExpired` is not caught, so the counter exits 1 (traceback), which the counter's contract defines as "target unmet", not 2 "could-not-evaluate".
- Fix (L1, now): never accept a fixture that spawns background work; after every run `pgrep -f "$SCRATCH"` must be empty. Harness fix: `Popen(..., start_new_session=True)`, on timeout `os.killpg(p.pid, signal.SIGKILL)`, and catch `TimeoutExpired` → exit 2.

### F9 (L, direct-CLI override): `c3-counter.py --pristine-sha` and `--fixture`/`--sites` are overridable
- `score-candidate.sh` does not pass them, so the harness path is safe. A direct run with `--pristine-sha <other>` would score a modified tool. Fix: remove the override or require a `--unpinned` flag that prints "NOT A CLAIM".

### F10 (L, direct-CLI usage): `c3-counter.py` usage shows `--root LANE`
- Nothing refuses a lane root; with the fixture's inherited cwd and writable lane, a direct run lets a candidate write into the lane. Covered by F6; the L1 should not use the direct form for candidates.

### F11 (L, residue): `tests/fixtures` candidates that `chmod 000` a dir (P02a, P18) must restore modes before cleanup
- `score()` and `main` use `shutil.rmtree(..., ignore_errors=True)`, so an unrestored `000` dir is silent residue under the scratch root. The fixture must `chmod` back in a `finally`.

## Per-probe write audit (P01–P19, probe recipes C3; R1 counter)

| Probe | Writes outside WORK? | Basis |
|---|---|---|
| P01, P02a, P02b, P03–P09, P12, P13, P14, P19 | no | record/root reads only; drift tool writes nothing without `--json` |
| P10a FIFO | no | O_WRONLY\|O_NONBLOCK → ENXIO → refused (`tools/souji-worktree-drift.py@e2a74312` L267–272) |
| P10b directory | no | EISDIR → refused |
| P11 `/dev/null` | no | open only; refused at fstat (D) |
| P15 record as `--json` | no | JSON-IS-RECORD before any write (E) |
| P16 `--json` inside tree | no | refused by inside-measured guard (L342–348) |
| P17 hardlink | no | refused at nlink before ftruncate (B) |
| P18 unwritable dir | no | EACCES in open; code path refused; but restore mode (F11) |
| any `--json` path outside root, regular, nlink 1 | **yes** | F1 — the fixture's path choice is the write set |
| R1 counter (`r1-counter.py`) | no (own writes) | every `write()`/`mkdtemp` is under `scratch`; the fixture it runs is candidate code (F6) |

## Lane/fleet touch audit

- `score-candidate.sh` L23 `git clone -q --shared "$LANE"`: read-only on lane; creates alternates only in the clone (verified: lane status clean after runs).
- `score-candidate.sh` L30 `cp` onto a symlink: writes through (F3). L34 commit: redirected by `GIT_DIR` (F4).
- Counter `git show` / `cat-file -e` calls: read-only; run under a whitelisted env (c3 L63–66, r1 L86–89).
- Drift tool git calls (`worktree list --porcelain`, `worktree prune --dry-run -v`, `rev-parse --absolute-git-dir`): read-only, `--no-optional-locks`, `GIT_OPTIONAL_LOCKS=0`, whitelisted env, `core.hooksPath=/dev/null`, `core.fsmonitor=false`. Pointed at the fleet they measure but do not write.
- `--json` containment is relative to `--root`, not to the lane. Any lane path outside `--root` is a legal `--json` target (F1).
- Fixture cwd: inherited (F6). Lane is writable from a candidate that uses relative paths when cwd is the lane.

## Commands run (cwd = my scratch `/fast/scratch/hyaku/souji-r41/R41sentinel01`; nothing run as root; no installs)

- `git -C <lane> show e2a7431…:<path> > <scratch>/frozen/…` (read-only export); `sha256sum` of the two pinned files.
- `git -C <lane> rev-parse HEAD`; `git --no-optional-locks -C <lane> diff --stat e2a7431 HEAD -- census tools tests` (empty); `git -C <lane> ls-tree -r e2a7431 | cut -c1-6 | sort | uniq -c` → 8013×100644, 1026×100755, 47×120000.
- `python3 -B <frozen>/census_round-41_c3-counter.py --selftest --scratch <scratch>/st` → `SELFTEST cases=3 fail=0`, rc=0.
- Drift tool cases A–I (`python3 -B <frozen>/tools_souji-worktree-drift.py --root … --record … --json …`, with `timeout 30`), results in F1; `bwrap --version` → `bubblewrap 0.13.1`.
- Fake lanes `fakelane.*` and `fakelane2.*` created with `git -C … init` and committed with `GIT_AUTHOR_*`/`GIT_COMMITTER_*` env only; `rev-parse --show-toplevel` checked against each dir before commit.
- `bash <fakelane>/census/round-41/score-candidate.sh …` for S1–S4 and the end-to-end hostile run (F2, F3, F4, F5, F6).
- Driver `score()` with a hostile fixture, cwd = `caller-cwd`; same fixture under bwrap (F6).
- `subprocess.run(timeout=3)` grandchild test (F8).
- `env`-whitelist check: fixture saw 7 keys, no `GIT_DIR` (F6).
- `grep` for `geteuid|euid|getuid` across the two counters and the script (F7).

## Not verified / limits

- Candidate fixtures `tests/fixtures/r41-refusal-sites.py` and `r41-drift-record-order.py` do not exist at freeze, so no full harness score (`killed=19`/`M19–M21`) was produced. I did not fabricate one.
- P10a/P10b/P17 were exercised with the drift tool directly, not through a probe fixture.
- F7 is a code-read finding only.

## Installs / host

- No tool installed or upgraded. `bwrap`, `unshare`, `systemd-run` were already present (`/usr/bin/bwrap`, bubblewrap 0.13.1). No pacman transaction.
- Canaries were all written under my scratch; scratch is removed at the end of this run.
