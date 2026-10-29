# R42sentinel01 — security and scratch review of `census/round-42/score-candidate.sh` and the four r42 counters

Seat: R42sentinel01 (sentinel). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Freeze commit `afe17f416eec04dcf3f480b580a8f928de61d19d`. Lane HEAD unchanged during the review; the lane was read-only for this seat.

Scope: scorer dest handling, symlink write-through, counter replacement, unconfined candidate execution, scratch discipline, kill leftovers, clone hygiene. Every attack ran against a fixture clone under `/fast/scratch/hyaku/souji-r42/R42sentinel01/fx/` (a `--shared` clone of the lane tip, plus a fixture-only commit `abf883c4…` adding a tracked symlink). The fixture's own `census/round-42/score-candidate.sh` was used, so `LANE` resolved to the fixture. No frozen file was edited. No real-lane file was written. Copies of the logs cited below are in `.ufo/waves/round-42/w1/R42sentinel01/evidence/`. The scratch dir is removed before yield.

## Verdict

**RED for `score-candidate.sh`.** Its N9 defect is still open: a dest escapes the clone, writes through tracked symlinks, and replaces the counter that is then executed. Each was demonstrated. A candidate can also run unconfined code (a pre-commit hook pushed a ref into its origin) before the counter runs. Seat scores from this scorer are forgeable and must not be trusted without an L1 blob check at the landed tip.

**AMBER for the counters' scratch discipline.** The four counters keep their own work dirs under `--scratch`, set `TMPDIR` for children, and hardcode no `/tmp`. But SIGKILL and SIGTERM leave `souji-r42-*` entries under `--scratch` (c2, c3, and the score wrapper). `--scratch` accepts any existing directory, including the lane worktree.

Tooling: no tool was installed or upgraded. No pacman or `~/.local/bin` change. Record for the L1: none.

## Findings

| # | finding | demonstration command + output | severity | named limit the L1 should record |
|---|---|---|---|---|
| F1 | **dest path traversal** (N9). `dest` is never validated; `cp "$src" "$C/$dest"` writes wherever `..` leads. | `bash $SC c1 $F/rootA1 ../../../escaped-from-dest.txt=$F/cand/escape.txt` → counter line `SUMMARY items=70 population=ok registered=0 class_ok=0 unresolved=5 ...`; `ls -la $F/escaped-from-dest.txt` → present, 13 bytes (`ESCAPE-PROBE`). `../../x-persist.txt` → `$F/rootA1/x-persist.txt` survives the run while `souji-r42-score.*` is removed. Depth: the clone sits 2 levels below the per-run dir, and the scratch root is 5 components below `/`, so 7 `..` from a seat-root clone reach `/`. Dry `normpath` (no write): `../../../../../../../home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/c1-counter.py` → `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/c1-counter.py`. | HIGH | Scorer writes any path the seat user can write. The L1 runs scoring only with a fresh seat-owned `$HYAKU_SCRATCH` root and treats any seat score as advice. Named limit N9a open; fix = reject `..`, absolute, or non-`git ls-files` dests. |
| F2 | **tracked symlink dest written through** (N9). `cp` follows symlinks in the clone. | Fixture commit `abf883c4…` adds `corpus/probe-link.md -> $F/cand/symtarget.txt` (`SYMTARGET-ORIGINAL`). `bash $SC c1 $F/rootA3 corpus/probe-link.md=$F/cand/symprobe.txt` → counter exit 1, then `cat symtarget.txt` → `SYMLINK-PROBE`; the link itself is intact. Real lane: `git ls-tree -r HEAD` lists 47 tracked symlinks: 14 absolute into the real lane (e.g. `tests/vault/vadv54-run/p/alias-link.md -> /home/vgpnk/Projects/shokunin/souji-shokunin/tests/vault/vadv54-run/p/p2.md`; `readlink -f` on a clone confirms the target exists and was **not** written), 3 to `/dev/null`, 30 relative. | HIGH | Dests that name a tracked symlink write the link's target, including real-lane files. Named limit N9b open. Fix = `rm -f "$C/$dest"` before `cp`, or refuse non-regular tracked entries (mode 120000). |
| F3 | **dest naming a counter** (N9). A candidate replaces the counter that is then run from the clone; the forged counter scores as a pass. | `bash $SC c1 $F/rootA3 census/round-42/c1-counter.py=$F/cand/forged-c1-counter.py` → `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` then `FORGED-COUNTER-RAN argv=[...]`, exit 0. Fixture lane's frozen `c1-counter.py` sha before and after: `0ab07cd3…` (only the clone changed). Same class applies to `c2-counter.py`, `c3-counter.py`, `r1-counter.py`, and to `census/round-42/c1-items.tsv` / `c1-register.tsv` (read from `--rev`). | HIGH (scoring integrity) | Scorer output is advice (prereg rule 2). The L1 must check that the landed tip's Counter and Population blobs equal the preregistered sha256 and run the counter from the landed tree, never from a seat clone. Named limit: `score-candidate.sh` does not refuse dests under `census/` or `tools/`. |
| F4 | **candidate code runs unconfined, before the counter, with full environment.** A dropped `.git/hooks/pre-commit` runs during the scorer's own `git commit`. | `bash $SC c1 $F/rootA5 .git/hooks/pre-commit=$F/cand/hook.sh` → `hook-ran.txt`: `HOOK-RAN pid=2715806 uid=1000 home=/home/vgpnk pwd=…/clone`; `hook-env.txt` has 274 variables incl. `HOME`. The score wrapper scrubs no env (only the counters strip env). | HIGH | Unconfined execution (N9). No sandbox, no network or FS restriction. Named limit: a seat may score only candidates it has read. |
| F5 | **candidate writes into another repo via origin.** `git clone --shared $LANE` sets `remote.origin.url` = the lane; a hook can push into it. | `bash $SC c1 $F/rootP .git/hooks/pre-commit=$F/cand/push-hook.sh` → `push-exit=0`; `git -C $F/lane branch --list r42-sentinel-probe` → `r42-sentinel-probe`, `rev-parse` → `abf883c4…`. Real-lane check: branch count 0 (see closing checks). | HIGH | Scorer clone has push access to the lane through origin. Named limit: fix = clone with `--no-checkout` then `git remote remove origin`, or pin `remote.origin.pushurl` to a no-push value. |
| F6 | **candidate tool writes an absolute path and runs under the seat uid.** c2 runs `tools/souji-freeze-check.py` from the candidate; the counter strips env to `PATH, TMPDIR, GIT_*, PYTHONPATH, SOUJI_R42_PATCH` (no `HOME`). | `bash $SC c2 $F/rootA6 tools/souji-freeze-check.py=$F/cand/tool-probe.py` → `SUMMARY cases=37 pass=0 fail=37 … patches=0/3`; `tool-env.txt` lists the stripped env (no `HOME`); `PROBE-FROM-TOOL.txt` written at `$F/lane/PROBE-FROM-TOOL.txt`, content `tool wrote absolute lane path, uid=1000`. | HIGH | Env stripping is hygiene, not confinement; FS is unrestricted. Named limit: subprocess `timeout` kills only the direct child; grandchildren are not reaped (code read of `run_tool` in c1/c2/c3, not demonstrated — [INFERENCE]). |
| F7 | **clone hygiene** (partial pass). Hooks are not inherited (`init.templatedir` unset); `--shared` alternates point at lane objects; the commit freshens two lane loose objects (mtime only). | Fixture planted `post-checkout` in lane `.git/hooks`; `git clone -q --shared` → clone `hooks` lists only `*.sample`. `cat …/h1clone/.git/objects/info/alternates` → `$F/lane/.git/objects`. `find $F/lane/.git/objects -newer marker2 -type f` after a candidate-only `score-candidate.sh c1` → `9088b4c0…` (blob, the symlink) and `d53bb813…` (tree); `cat-file -t` ok for both. Object content unchanged; only utime. | LOW | Named limit: `git add` in the clone freshens alternate loose objects (mtime writes into the lane store). Harmless for correctness; can extend `gc --prune` age. |
| F8 | **scratch leftovers after SIGKILL/SIGTERM.** | score wrapper: `timeout -s KILL 3 bash $SC c1 $F/rootK1 …` → exit 137, `rootK1/souji-r42-score.8HVWKp/` left. `timeout -s TERM 3 …` → exit 124, `rootK2/souji-r42-score.Rb5LpR/` left (bash EXIT trap does not fire on TERM). c2: `timeout -s KILL 3` → `kc2/souji-r42-c2.8c5d60w8`; `timeout -s KILL 1` → `k1c2/souji-r42-c2.e0bgg7bm`. c3: `timeout -s KILL 3` → `kc3/souji-r42-c3.v_tlbm0g`; `timeout -s TERM 3` → `kc3t/souji-r42-c3.1ihbsrgz`. c1 and r1 completed in under 1 s (`k1c1`, `k1r1` empty; not killed mid-run). Drift fixture: `TMPDIR=$F/kt timeout -s KILL 0.6 python3 -B tests/fixtures/r41-drift-record-order.py` (twice) → `kt/souji-r41-order.wqb2bgql`, `kt/souji-r41-order.ya1x1asj`. | MEDIUM | Carries N17 (C3 fixture leaves entries under `--work` after TERM/KILL). Named limit: the L1 sweeps `<scratch>/souji-r4*` after every run; the counters' `finally: rmtree` does not run on KILL/TERM. c1 and r1 mid-run kill not demonstrated. |
| F9 | **scratch root not confined.** `score-candidate.sh` checks only `[ -d "$root" ]`; counters check `--scratch` only for existence. The operator's `$HYAKU_SCRATCH` rule is not enforced (`HYAKU_SCRATCH` unset in the seat shell). | `timeout -s KILL 3 bash $SC c2 $F/lane lane-dest-probe.txt=…` → exit 137; `git -C $F/lane status --porcelain` → `?? souji-r42-score.wqvwRQ/` (an untracked leftover clone inside the lane worktree). Fixture drivers default to `/var/tmp`: `tests/fixtures/r41-drift-record-order.py:153` `work = args.work or os.environ.get("TMPDIR") or "/var/tmp"`. 47 fixtures contain literal `/tmp` or `/var/tmp`; 86 tools use `${TMPDIR:-/tmp}`. The r42 counters do not (grep of `census/round-42/*.py`, `*.sh` for `/tmp` is empty). | MEDIUM | Named limit: scorer and counters accept a lane path as scratch root; the L1 must pass a `$HYAKU_SCRATCH`-rooted dir it created. Fixture-driver `/var/tmp` fallback and tools' `/tmp` fallback are outside r42's frozen surface (not changed). |
| F10 | **counter-level integrity** (advisory). c1 derives population from the base tool and compares it with the `--rev` items (`population=ok` requires equality with base rows, so a changed population reads `DRIFT`). c3 pins the tool sha (`PRISTINE_SHA256`) and derives anchors from the `--rev` population, but does not pin that population file's sha. c2 derives its Counter/Population digests from the candidate tree. | Read from `c1-counter.py:177`, `c3-counter.py:179–196`, `c2-counter.py:155–169`. Not executed for this finding; F3 already shows the counter file itself is forgeable. | LOW (advisory) | Named limit: the frozen blobs are protected only by the L1's landed-tip blob check, not by the counters. |

## Commands run (exact, condensed)

```
F=/fast/scratch/hyaku/souji-r42/R42sentinel01/fx ; SC=$F/lane/census/round-42/score-candidate.sh
git clone -q --shared /home/vgpnk/Projects/shokunin/souji-shokunin $F/lane     # git -C $F/lane rev-parse --show-toplevel == $F/lane asserted
git -C $F/lane commit (fixture-only symlink corpus/probe-link.md)               # fixture tip abf883c46abde92a8dd74e4bcd1087f4e57aea36
timeout 300 bash $SC c1 $F/rootA1 ../../../escaped-from-dest.txt=$F/cand/escape.txt   # escape file present, 13 bytes
timeout 300 bash $SC c1 $F/rootA1 ../../x-persist.txt=$F/cand/escape.txt             # $F/rootA1/x-persist.txt present
timeout 300 bash $SC c1 $F/rootA3 census/round-42/c1-counter.py=$F/cand/forged-c1-counter.py
timeout 300 bash $SC c1 $F/rootA3 corpus/probe-link.md=$F/cand/symprobe.txt          # symtarget.txt now SYMLINK-PROBE
timeout 300 bash $SC c1 $F/rootA5 .git/hooks/pre-commit=$F/cand/hook.sh
timeout 600 bash $SC c2 $F/rootA6 tools/souji-freeze-check.py=$F/cand/tool-probe.py
timeout -s KILL 3 bash $SC c1 $F/rootK1 kill1.txt=$F/cand/escape.txt                 # exit 137, leftover
timeout -s TERM 3 bash $SC c1 $F/rootK2 kill2.txt=$F/cand/escape.txt                 # exit 124, leftover
timeout -s KILL 3 python3 -B $F/lane/census/round-42/c2-counter.py --root $F/lane --rev $REV --scratch $F/kc2   # exit 137, leftover
timeout -s KILL 3 python3 -B $F/lane/census/round-42/c3-counter.py --root $F/lane --rev $REV --scratch $F/kc3   # exit 137, leftover
timeout -s TERM 3 python3 -B $F/lane/census/round-42/c3-counter.py --root $F/lane --rev $REV --scratch $F/kc3t  # exit 124, leftover
timeout -s KILL 1 python3 -B $F/lane/census/round-42/c1-counter.py --root $F/lane --rev $REV --scratch $F/k1c1  # exit 1, empty
timeout -s KILL 1 python3 -B $F/lane/census/round-42/r1-counter.py --root $F/lane --rev $REV --scratch $F/k1r1  # exit 1, empty
timeout -s KILL 1 python3 -B $F/lane/census/round-42/c2-counter.py --root $F/lane --rev $REV --scratch $F/k1c2  # exit 137, leftover
timeout -s KILL 3 bash $SC c2 $F/lane lane-dest-probe.txt=$F/cand/escape.txt        # lane root accepted; leftover in lane worktree
TMPDIR=$F/kt timeout -s KILL 0.6 python3 -B tests/fixtures/r41-drift-record-order.py  # exit 137, souji-r41-order.* left
timeout 300 bash $SC c1 $F/rootP .git/hooks/pre-commit=$F/cand/push-hook.sh          # push-exit=0; fixture branch created
```

Observed outputs are in the evidence copies (see Closing checks). Harness note: several calls in this session printed `(no output)` with exit 1 because a shell-level `set -e` was active from the fixture-setup call; those were re-run with `set +e` and their outputs are the ones cited.

## Named limits for the L1 to record

1. **N9a (F1), open.** `score-candidate.sh` accepts any dest; `..` and absolute paths write outside the clone. Demonstrated.
2. **N9b (F2), open.** Tracked symlink dests write through, including to 14 absolute symlinks into the real lane. Demonstrated on a fixture; real-lane targets identified by `readlink -f`, not written.
3. **N9c (F3), open.** A dest naming `census/round-42/*-counter.py` (or the `c1-items.tsv` / `c1-register.tsv` population files) forges the score. Demonstrated; the lane's counter sha stayed `0ab07cd3…`.
4. **N9d (F4–F6), open.** Candidate hooks and tools run unconfined with the seat's uid and environment; a hook pushed a ref into origin (the lane). Demonstrated.
5. **N17 (F8), open** for the r42 counters (c2, c3 leave `souji-r42-*` on KILL/TERM) and the r41 drift fixture (`souji-r41-order.*`).
6. **Scratch root (F9), open.** `--scratch` / `<scratch-root>` is not confined to a `$HYAKU_SCRATCH` directory; the lane worktree is accepted.
7. **Advisory (F7, F10).** Alternate-object freshen writes mtime into the lane store; counters do not self-pin population blobs. Scorer output is advice; the L1 measures at the landed tip.

## Closing checks (read-only, real lane, after all attacks)

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD            -> afe17f416eec04dcf3f480b580a8f928de61d19d (freeze, unchanged)
git -C /home/vgpnk/Projects/shokunin/souji-shokunin branch --list r42-sentinel-probe | wc -l   -> 0 (the push probe landed only in the fixture)
sha256sum census/round-42/c1-counter.py   -> 0ab07cd3c99e6bbe26220d9e36672b6a7acd45150b96fff1868d0e082dcd46aa (matches prereg)
sha256sum census/round-42/c2-counter.py   -> fa44392d11338daa73b3b4b9b2fc8f89879c099e9bf278d7b45fa55dea5d0ac1 (matches prereg)
sha256sum census/round-42/c3-counter.py   -> bf0ebf4fef0cf0070daf2dd89184e83575bfabe4e4e82fa50511b3c6c8585d76 (matches prereg)
sha256sum census/round-42/r1-counter.py   -> f2dcbd06eecdb864e5ca215154aa82e564f7dbba586f617ad5543c0a811cc1bb (matches prereg)
sha256sum census/round-42/c1-items.tsv    -> b2601340eb20f70b0298542806acd47ef6e60586eacac92efdf94b1b231a8d39 (matches prereg)
sha256sum census/round-42/c3-mutants.tsv  -> 2f6f8df39ed6dd66cda22806012b68db9e12712e5572931286daed60a4bab205 (matches prereg)
sha256sum census/round-42/c2-cases.tsv    -> 148b7b87411eb282e0207cf5471d55be81e03d4a26ffafd96df37b4db4fd4511 (matches prereg)
sha256sum tools/souji-worktree-drift.py   -> b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6 (pin matches)
```

Evidence copies: `.ufo/waves/round-42/w1/R42sentinel01/evidence/` (`a1.out`, `a1c.out`, `h3.out`, `h3b.out`, `p.out`, `kill1.log`, `serial.log`, `c1-serial.out`, `push-hook.out`, and the hostile probes `forged-c1-counter.py`, `hook.sh`, `push-hook.sh`, `tool-probe.py`, plus `hook-ran.txt`). The K1–K7 and A3/A4/A5/A6 stdout is quoted in the table rows above; their log files were not separately copied.
The scratch dir `/fast/scratch/hyaku/souji-r42/R42sentinel01/` is removed before yield; fixture commits and leftovers were disposable and are not evidence.

## Yield summary

- score-candidate.sh: RED. N9a dest traversal, N9b symlink write-through, N9c counter replacement, N9d unconfined hook/tool with origin push, all demonstrated.
- Counters: AMBER. KILL/TERM leftovers under `--scratch` for c2 and c3 (and the r41 drift fixture); the lane is accepted as scratch root.
- No tool installed or upgraded. No lane, fleet, or frozen file written.
