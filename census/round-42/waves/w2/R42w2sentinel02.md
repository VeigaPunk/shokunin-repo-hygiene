# R42w2sentinel02 — falsification of the landed r42 fixture and the scorer's scratch/allowlist discipline

Seat: R42w2sentinel02 (role sentinel, wave 2, round 42). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin.
Lane tip under attack: 3105a63b23481fccf7df58e74d14a6681e0ea0c8 (lane status clean before, during and after; HEAD unchanged; no lane write by this seat).
Pinned tool: tools/souji-worktree-drift.py sha256 b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6 (unchanged throughout).
Axes attacked: **operability** (scratch discipline, signal behaviour, environment isolation, refusal paths) and **coverage** (which hostile conditions the harness actually refuses). No candidate, counter, population, control or tracked file was edited. Scratch: /fast/scratch/hyaku/souji-r42/R42w2sentinel02 (deleted before yield).
Tools installed: none. `unshare -r` (util-linux, already present) was used for a user-namespace root test only.

## Commands run and observed output (abridged where marked; every SUMMARY / EXIT line is verbatim)

Fixture: `F=tests/fixtures/r42-drift-conditions.py`, `T=tools/souji-worktree-drift.py` (absolute lane paths), driver invoked as `python3 -B $F --tool $T --work $S/w-*`.

1. Normal run, --work in scratch (`A1`):
   `SUMMARY cases=13 pass=13 fail=0`, `EXIT=0`, leftover under --work: **0 entries**.
2. `timeout -s KILL 5` (`A2`): `EXIT=137`; leftover under --work: **60 entries** (`r42dc.<rand>/default-timeout/{root,o,...}`). Orphans of this seat afterwards: none (`pgrep` on scratch path: none).
3. `timeout -s TERM 5` (`B1`): `EXIT=124`; leftover: **60 entries** (`w-term/r42dc.38bbmdx3/default-timeout/...`). Orphans: none.
4. Root refusal (`B2`, `unshare -r` gives euid 0 in a user namespace, no host privilege): `uid=0(root)`, then `r42-drift-conditions: refusing to run as root`, `EXIT=2`, leftover **0**. Real root was not used (policy).
5. Caller environment (`E1`): canary HOME with `.gitconfig` (`[user] name = Canary`), TMPDIR canary, cwd canary. Run: `SUMMARY cases=13 pass=13 fail=0 EXIT=0`. After: canary `.gitconfig` sha256 `221639cc6bf28c141f2068a1d46344e80e10728cafd6c5ed219e180e4d467e69` equals the sha of the content I wrote (unchanged); canary TMPDIR and cwd remain empty; `/home/vgpnk/.config/git/config` mtime `2026-10-28 16:40:41` (predates this run); `find /tmp -newer marker` showed only other seats' files (chousa-*, zcode-*, orangery, ecc-metrics), none named r42dc/souji-r42.
6. Hostile `git` first on PATH (`E2`, shim logs its argv then `exit 127`): all 13 `git init -q` calls logged (`HOSTILE-GIT ... args=init -q .../root/r`); every case `FAIL` via `CalledProcessError ... exit status 127`; `SUMMARY cases=13 pass=0 fail=13`, `EXIT=1`, no traceback, leftover **0**.
7. `GIT_DIR=<decoy>/.git GIT_WORK_TREE=<decoy>` (`E5a`): `SUMMARY cases=13 pass=13 fail=0 EXIT=0`; decoy metadata hash `92f4b0bc…` identical before and after (the fixture's env is a whitelist; GIT_DIR never reaches git).
8. `--work` path that does not exist (operability): `FileNotFoundError: [Errno 2] No such file or directory: '…/does-not-exist/r42dc.j2o1fiju'`, `EXIT=1` (an unhandled traceback, not a usage refusal).
9. score-candidate.sh hostile dests (`C-hostile`, each with a valid candidate source; all refused before the clone is committed):
   `../x` → `score-candidate: dest ../x is not on the allowlist`, `EXIT=2`; `/tmp/abs-evil` → same class, `EXIT=2`; `census/round-42/c1-counter.py` → `EXIT=2`; `SCORECARD.md<LF>x` → `dest SCORECARD.md\nx is not on the allowlist`, `EXIT=2`. Scratch leftover 0.
10. score-candidate.sh candidate sources (`A1..A4`, dest `SCORECARD.md`, claim c1):
    FIFO → `… fifo.txt is not a file`, `EXIT=2`; symlink→FIFO → `… is not a file`, `EXIT=2`; symlink→/dev/null → `… is not a file`, `EXIT=2`; symlink→regular file → accepted, `SUMMARY items=70 … mismatches`, counter ran, `EXIT=1` (the counter's verdict, not a harness refusal).
11. Tracked symlink as the dest leaf (`fx-b`: `tests/fixtures/r42-drift-conditions.py` committed as a symlink to `outside/victim.py`, claim c3): `score-candidate: dest tests/fixtures/r42-drift-conditions.py is a symlink in the clone`, `EXIT=2`; `victim` content unchanged.
12. Tracked symlinked **parent** (`fx-c`: `corpus/knowledge` committed as a symlink to `$S/outside`, dest `corpus/knowledge/jj-colocation-receipts.md`, claim c1): **accepted**; counter ran (`SUMMARY items=70 population=ok registered=70 class_ok=63 … rewritten=0 new_mismatches=0`, `EXIT=1`); `ls $S/outside` shows `jj-colocation-receipts.md` (2 bytes: the candidate) written **outside the clone**. The leaf check `[ ! -L "$C/$dest" ]` tests only the last component.
13. `GIT_DIR` in the scorer environment (`fx-a` = a scratch clone of the lane, `GIT_DIR=$S/fx-a/.git`, claim c1): `SUMMARY items=70 … new_mismatches=0`, `EXIT=1`; then `git -C fx-a log --oneline -1` → `3ef6fc33 candidate`: **the candidate commit was written into the repository named by GIT_DIR**. The real lane was untouched (its HEAD stayed `3105a63`, `status` 0). The same run with the decoy (`GIT_DIR` only) produced `candidate` commit `72c8c71` in the decoy: `DECOY CHANGED by scorer`. With `GIT_WORK_TREE` also set, `git clone` aborted first (`fatal: working tree '…/decoy' already exists`, `EXIT=2`, decoy unchanged).
14. No-`=` pair (`N1`/`N2`/`N2'`): `score-candidate.sh c1 <scratch> SCORECARD.md` run with cwd lacking SCORECARD.md → `score-candidate: SCORECARD.md is not a file`, `EXIT=2`. Same pair with cwd = a scratch lane copy that has SCORECARD.md → `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0`, `EXIT=0`, leftover 0: the source was read from the caller's working directory. (The earlier `D5` run reported `SUMMARY mutants=13 … cases=13` for the same pair, consistent with this.)
15. KILL during the scorer (`K1`, c1, `timeout -s KILL 4`): `EXIT=137`; leftover under --scratch **1044 entries** (`souji-r42-score.<rand>/clone` and counter scratch). Orphans after 15 s: none of this seat's.
16. KILL during counters (`K2` c2 at 5 s: **763 entries**; `K3` c3 at 10 s: **91 entries**; earlier c1 at ~8 s: **2 entries**). Lane status 0 after each.
17. c3 counter under a hostile `git` first on PATH (`C3h`): `REFUSAL COULD-NOT-EVALUATE: --rev must name a resolvable full40 commit`, `EXIT=2`, leftover 0, one shim call logged (`cat-file -e 3105a63…^{commit}`). Refused before any scoring.
18. Lane after all runs: `git status --porcelain | wc -l` = `0`; `git rev-parse HEAD` = `3105a63b23481fccf7df58e74d14a6681e0ea0c8`; `git ls-tree` shows 47 symlinks in the tip tree, none under an allowlisted dest or parent (parent dirs `tools`, `tests`, `tests/fixtures`, `census`, `census/round-42`, `corpus`, `corpus/knowledge` are `040000 tree`; the nine dest leaves are `blob`).

## Attack table

| attack | observed | severity | handling |
|---|---|---|---|
| Fixture normal run, --work in scratch (cmd 1) | 13/13 pass, EXIT 0, 0 leftover | none | pass |
| Fixture under `timeout -s KILL 5` (cmd 2) | EXIT 137; **60 entries** left under --work; no orphans | low (scratch rule: "nothing under scratch after exit") | not landed. Finding for L1: the driver's `finally: rmtree` does not run on signal; a SIGTERM/SIGINT handler or an explicit wrapper cleanup would close it. Counter-driven runs are contained only because the counter removes its own `w-<tag>` dir. Named limit N-H covers counters, not the fixture. |
| Fixture under `timeout -s TERM 5` (cmd 3) | EXIT 124; **60 entries** left; no orphans | low | same as above |
| Fixture as euid 0 (cmd 4, `unshare -r`) | "refusing to run as root", EXIT 2, 0 entries written | none | pass; check runs before any write. Tested in a user namespace only (policy: no real root). |
| Writes outside --work / HOME / global git config (cmd 5) | canary HOME `.gitconfig` sha unchanged; canary TMPDIR/cwd empty; real `~/.config/git/config` untouched; no `/tmp` residue of r42dc/souji-r42 | none | pass |
| Hostile `git` shim first on PATH (cmd 6) | 13 shim calls, all 13 cases FAIL (exit 127), `SUMMARY … fail=13`, EXIT 1, no traceback, 0 leftover | none | pass: fails honestly, does not pass silently |
| `GIT_DIR` set to a decoy (cmd 7) | 13/13 pass; decoy hash identical before/after | none | pass: fixture env is a whitelist |
| `--work` directory missing (cmd 8) | unhandled `FileNotFoundError` traceback, EXIT 1 | low (operability: crash path, not a usage refusal) | not landed; finding for L1 |
| score-candidate hostile dests `../x`, `/tmp/abs-evil`, counter path, newline (cmd 9) | all refused "not on the allowlist", EXIT 2, before any commit; 0 leftover | none | pass |
| score-candidate candidate source FIFO, symlink→FIFO, symlink→/dev/null (cmd 10) | "is not a file", EXIT 2 | none | pass. Residual [INFERENCE, unrun]: `[ -f ]` then `cp` is a TOCTOU; a FIFO swapped in after the check blocks `cp`. Severity low. |
| symlink→regular file as candidate source (cmd 10) | accepted and scored (legitimate read-through) | none | expected behaviour |
| tracked symlink as the dest leaf (cmd 11) | refused "is a symlink in the clone", EXIT 2; victim unchanged | none | pass (the leaf check works) |
| tracked symlinked **parent** dir, allowlisted dest under it (cmd 12) | **accepted**; `cp` wrote `jj-colocation-receipts.md` outside the clone (`$S/outside`) | **medium** (write escapes the scoring clone; latent: no allowlisted parent is a symlink at 3105a63) | not landed. Fix: reject any dest component that is a symlink in the clone, or resolve with realpath and require it under `$C`. Not in the lesson's N-H list. |
| `GIT_DIR` set in the scorer's environment (cmd 13) | candidate commit `3ef6fc33 candidate` landed in the repo named by GIT_DIR (the scratch lane copy); decoy variant `72c8c71` likewise; real lane untouched only because the test used a copy | **high** against the contract "never writes the lane" when GIT_DIR names the lane; needs the caller's environment, so operator-controlled | not landed. Fix: run the scorer under `env -i` with an explicit whitelist (as the fixture and counters already do for git). Lesson N-C2 understates this as "reaches the scoring clone's decoy": the commit is written to the named repository. |
| `GIT_WORK_TREE` set in the scorer's environment (cmd 13) | `git clone` aborts (`working tree already exists`), EXIT 2, decoy unchanged | low | same fix as above |
| No-`=` pair (cmd 14) | source read from the caller's cwd: refused when absent, accepted and scored when present (EXIT 0) | low (caller error; the pair grammar is not validated) | not landed. Fix: require `=` and an absolute source path. |
| score-candidate KILL at 4 s (cmd 15) | 1044 entries left under --scratch | low (known family, N-H) | not landed; the trap does not run on KILL |
| counters KILL at 5 s / 10 s / 8 s (cmd 16) | c2 763, c3 91, c1 2 entries left | low (known, N-H) | not landed |
| c3 counter with hostile `git` on PATH (cmd 17) | REFUSAL COULD-NOT-EVALUATE at rev resolution, EXIT 2, 0 leftover | none | pass |
| orphan processes after KILL/TERM (cmds 2, 3, 15) | none of this seat's processes alive (other seats' processes in the same host were not signalled) | none | pass |
| lane integrity across all runs (cmd 18) | status 0, HEAD 3105a63, tool sha b2a603cf… | none | pass |

## Verdict

- **Fixture (C3 artifact, operability and coverage of the environment surface): AMBER.** It refuses euid 0, keeps the caller's HOME, global git config, GIT_DIR and TMPDIR untouched, fails honestly under a hostile `git`, and runs 13/13 on the lane tip. It does **not** satisfy the scratch rule on signal termination (60 entries left after KILL or TERM), and a missing `--work` produces a traceback rather than a refusal. Neither changes a C3 verdict (the counter wraps each fixture run in its own work dir), but the operator's scratch rule is violated by the fixture as shipped.
- **score-candidate.sh allowlist (destinations and candidate sources): AMBER.** Traversal, absolute, counter-path, newline and FIFO/device sources are refused, and a tracked symlinked leaf is refused. Two holes remain: a tracked symlinked **parent** lets the write escape the clone (medium, latent at the tip), and the script trusts `GIT_DIR` and the cwd so a candidate can be committed into the named repository (high under the "never writes the lane" contract, operator-env dependent). Both were demonstrated only in scratch copies and a decoy; the real lane was never pointed at.
- **Scratch residue on signal exit: RED** for all four tools (fixture 60, scorer 1044, c2 763, c3 91), matching the lesson's N-H for the counters and extending it to the fixture and scorer.
- No frozen file, candidate or tracked file was changed. Nothing was landed. Named findings for the L1: (a) parent-symlink escape in score-candidate.sh, (b) GIT_DIR/GIT_WORK_TREE honoured by score-candidate.sh (lesson N-C2 understates it), (c) no-`=` pair reads the cwd, (d) fixture leaves 60 entries on signal and tracebacks on a missing --work, (e) scorer and counter KILL residue (N-H).
