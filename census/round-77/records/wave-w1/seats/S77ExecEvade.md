# S77ExecEvade r77 C1 falsification (W gate 9b496b0883b255573175726f1463ce5634960a04)

Baseline re-derived: `timeout -k 5 120 python3 -B census/round-77/c1-nonreg-counter.py --gate-dir gatedir --work c1work` (gate/writer via `git show` from W into scratch) → `SUMMARY rows=16 mismatches=0 errors=0 hangs=0`; all 16 rows match=yes (n1-n8,n10 REFUSED, o1-o3 right class, p1-p4 PASS), secs≤0.1.

## Route table (gate bound 12-20s, own session/group kill; label per seat spec)
| route | rc/clean/secs | label |
|---|---|---|
| a1 rel core.excludesFile FIFO in tree | FAIL NONREG 0.0s | REFUSED |
| a2 ~/ core.excludesFile FIFO (scratch HOME) | FAIL NONREG 0.0s | REFUSED |
| a3 core.excludesFile via config.worktree (ext.worktreeConfig) FIFO | FAIL NONREG 0.0s | REFUSED |
| a4 relative `../outside-fifo` excludesFile | FAIL NONREG 0.0s | REFUSED |
| b1/b2 FIFO at $XDG_CONFIG_HOME/git/{ignore,attributes}, excludesFile unset | FAIL NONREG 0.0s | REFUSED |
| c1 .gitignore symlink→unix socket | FAIL NONREG 0.0s | REFUSED |
| c2/c3 .gitignore symlink→/dev/zero, /dev/tty | FAIL NONREG 0.0s | REFUSED |
| c4 directory named sub/.gitignore | FAIL NONREG 0.0s | REFUSED |
| c5 .gitignore symlink→regular file | FAIL NONREG 0.0s | REFUSED (conservative) |
| d1/d2 FIFO .gitignore in nested repo / submodule work tree | FAIL NONREG 0.0s | REFUSED |
| g1 symlink→FIFO .gitattributes chain | FAIL NONREG 0.0s | REFUSED |
| grace regular→FIFO mid-run swap | FAIL NONREG 0.03s | REFUSED-at-check |
| e1 FIFO info/sparse-checkout (disabled) | PASS 0.07s | REFUSED-not-needed (git never opens it) |
| e2 FIFO core.hooksPath hook | PASS 0.06s | REFUSED-not-needed |
| e4b includeIf FIFO (pattern never matches lane) | PASS 0.11s | REFUSED-not-needed |
| broken-symlink .gitignore | FAIL NONREG 0.01s | REFUSED (find ! -type f) |
| sym1 tracked symlink .gitignore hiding path | FAIL NONREG 0.02s | REFUSED (policy false-positive) |

## HANGs (all outside the frozen C1 surface; all OUT-OF-SURFACE where noted)
- HIGH e3 include.path FIFO: HANG>15s; piece probe: `rev-parse` HANG>5s → blocks check 1, before check 4. Prereg stated limit covers "FIFO $GIT_DIR/config / ~/.gitconfig blocks git before check 4". No timeout backstop on checks 1-3 (gate:68-86, `nonreg_sources` git calls un-timed).
- HIGH f1 packed-refs FIFO: gate HANG; `rev-parse` HANG>5s (check 1) AND `status` HANG>6s (check 4's own `timeout 300` would bound it, but row/check-1 already wedged).
- HIGH f2 HEAD FIFO: `rev-parse` & `--absolute-git-dir` HANG>5s (check 1 + gate's own gd resolution) → OUT-OF-SURFACE, before check 4.
- HIGH f4 config FIFO: `rev-parse` HANG>5s (check 1) → OUT-OF-SURFACE.
- HIGH f3 index FIFO: `rev-parse` ok, gate HANG>12s (inside check 4; `timeout -k 5 300` (gate:95,97) bounds it at 300s, i.e. no hang within row bound only if 300s accepted; frozen counter row bound is 30s so it reads HANG there).
- HIGH sp1 sparse-checkout FIFO + core.sparseCheckout=true: gate HANG>20s; `status` alone rc=0, so hang is in check-4 python block (`ls-files`/`ls-tree`/truth path) or nonreg? nonreg does not read sparse-checkout; OUT-OF-SURFACE-but-inside-check-4. Bounds at 300s.
- MEDIUM cd1 commondir: lane=linked worktree, FIFO at COMMON info/exclude — gate HANG>20s, `status` HANG>6s. Gate checks only `rev-parse --absolute-git-dir`/info/exclude (gate:70-71) = per-worktree dir, never `--git-common-dir`. Inside check 4, bounded 300s; but n3-class FIFO escapes the frozen counter's n3 shape.
- MEDIUM cwt config.worktree FIFO (linked worktree): `rev-parse` HANG>5s (check 1) → OUT-OF-SURFACE.

No FORGERY: no fixture hid content and passed; every in-surface vector is REFUSED before `git status`.

## Evidence
Gate pre-check: tools/souji-pre-report-gate.sh:68-94 (nonreg_sources: info/exclude|attributes via -f, config --path, XDG fallback, find ! -type f over work tree minus .git). Checks 1-3 git calls un-timed: :33-36. Check-4 timeout only :95,97.
Repro scripts (full): .ufo/waves/round-77/w1/S77ExecEvade/probe.py (a-e,g routes), probe2.py (f*,race), probe3.py (commondir,sparse), probe4.py (hang localisation), probe5.py (per-call pieces). Scratch removed.
Files written: .ufo/waves/round-77/w1/S77ExecEvade.md + S77ExecEvade/probe{,.2,.3,.4,.5}.py
