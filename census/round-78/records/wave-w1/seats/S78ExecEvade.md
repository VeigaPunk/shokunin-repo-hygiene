# S78ExecEvade — routes outside the 17 frozen rows (W gate ed22dc9c vs base a8558d41)

## Route table (measured; B=base a8558d41, W=W ed22dc9c)

| route | B verdict | W verdict | secs | severity |
|---|---|---|---|---|
| a-alternates-fifo ($GIT_DIR/objects/info/alternates) | HANG | HANG | 60.1/60.1 | LOW (stated limit: not a discovery source) |
| b-loose-ref-fifo ($GIT_DIR/refs/heads/master) | HANG | HANG | 60.1/60.1 | LOW (stated limit: not a discovery source) |
| c-shallow-fifo ($GIT_DIR/shallow) | HANG | HANG | 60.0/60.1 | LOW (stated limit: not a discovery source) |
| d-gitfile-fifo-config (.git gitfile -> realgit with FIFO config) | HANG | FAIL/GITSRC | 60.1/0.1 | — |
| d2-gitfile-itself-fifo (.git is a FIFO) | FAIL/NONREGULAR-SOURCE | FAIL/GITSRC | 0.1/0.0 | — |
| e-worktree-common-config-fifo (linked worktree, common dir config FIFO) | HANG | FAIL/GITSRC | 60.1/0.1 | — |
| e2-worktree-config.worktree-fifo (worktree gitdir config.worktree FIFO) | HANG | FAIL/GITSRC | 60.1/0.03 | — |
| f1-include-tilde (~/ expansion to FIFO) | HANG | FAIL/GITSRC | 60.1/0.0 | — |
| f2-include-leading-space (" /abs..." -> <dir>/ /abs... = <dir>/<space>/abs...) | HANG | FAIL/GITSRC | 60.1/0.07 | — |
| f3-include-newline (path value with embedded newline) | FAIL/NONREGULAR-SOURCE | FAIL/GITSRC | 0.1/0.1 | — |
| g1-include-cycle (a includes b includes a) | FAIL/NONREGULAR-SOURCE | FAIL/NONREGULAR-SOURCE | 0.1/0.1 | — |
| g2-include-chain12 (12-deep chain ending in FIFO) | FAIL/NONREGULAR-SOURCE | FAIL/GITSRC | 0.2/0.2 | — |
| g10ok-include-chain10-all-regular | — | PASS | 0.9 | — |
| g11ok-include-chain11-all-regular | — | FAIL/GITSRC | 0.4 | — |
| gcycle2-include-cycle-with-FIFO | FAIL/NONREGULAR-SOURCE | FAIL/GITSRC | 0.1/0.2 | — |
| h1-includeIf-onbranch:master (FIFO, condition true) | HANG | FAIL/GITSRC | 60.1/0.1 | — |
| h2-includeIf-hasconfig:remote.*.url (FIFO, condition true) | PASS | FAIL/GITSRC | 0.2/0.0 | — |
| h3-includeIf.gitdir:<clone>/.git (FIFO, condition true) | — | FAIL/GITSRC | 0.03 | — |
| h5-includeIf.onbranch:nonexistent (FIFO, condition false) | PASS | FAIL/GITSRC | 0.7/0.07 | LOW (fail-closed policy, allowed) |
| i-hooksPath-in-included (FIFO hook) | PASS | PASS | 0.5/0.7 | — |
| i2-fsmonitor-FIFO-in-included | PASS | PASS | 0.6/0.8 | — |
| j-xdg-attributes-fifo-no-home | FAIL/NONREGULAR-SOURCE | FAIL/NONREGULAR-SOURCE | 0.1/0.1 | — |
| j2-xdg-config-fifo-HOME-unset | HANG | FAIL/GITSRC | 60.1/0.1 | — |
| k-remote-head-fifo (origin HEAD FIFO) | HANG | FAIL/GIT-TIMEOUT | 60.1/45.8 | — |
| k2-remote-alternates-fifo | PASS | PASS | 0.4/0.6 | — |
| k3-remote-packed-refs-fifo | HANG | FAIL/GIT-TIMEOUT | 60.1/45.5 | — |
| k4-remote-loose-ref-fifo | HANG | FAIL/GIT-TIMEOUT | 60.1/45.5 | — |
| k5-remote-include-fifo | HANG | FAIL/GIT-TIMEOUT | 60.1/45.4 | — |
| g2b-HEAD-symlink-to-FIFO | FAIL/NONREGULAR-SOURCE | FAIL/GITSRC | 0.2/0.1 | — |
| g3b-packed-refs-symlink-to-FIFO | HANG | FAIL/GITSRC | 60.1/0.1 | — |
| g4b-commondir-symlink-to-FIFO | HANG | FAIL/GITSRC | 60.1/0.09 | — |
| g8b-config.worktree-symlink-to-FIFO | HANG | FAIL/GITSRC | 60.1/0.05 | — |
| g9b-HOME-gitconfig-symlink-to-FIFO | HANG | FAIL/GITSRC | 60.1/0.1 | — |
| g11b-config-symlink-to-include-FIFO | HANG | FAIL/GITSRC | 60.1/0.05 | — |
| d3-gitfile-FIFO-commondir | HANG | FAIL/GITSRC | 60.1/0.1 | — |
| d4-gitfile-FIFO-HEAD | HANG | FAIL/GITSRC | 60.1/0.09 | — |

## Findings

- **No W hang >45 s and no W PASS on a lane that hides content.** Every W HANG row (a,b,c) is a stated-limit non-discovery-source (refs, objects/info/alternates, shallow) — the prereg explicitly excludes them.
- **h2/h5 (includeIf conditions git would not meet):** W refuses with GITSRC while B passes. This is fail-closed policy, explicitly allowed by the prereg ("the gate is allowed to refuse it"). LOW.
- **f2 leading-space include:** git resolves `" /abs-fifo-placeholder"` to `<dir>/ /abs-fifo-placeholder` = `<dir>/<space>/abs-fifo-placeholder` (space is a directory component). W correctly refuses when the FIFO is at that resolved path; B hangs. The earlier f2 PASS was a fixture bug (FIFO at wrong path).
- **f3 newline include:** git config parse error (rc=128) → W refuses GITSRC, B fails NONREGULAR-SOURCE. No hang.
- **Remote-side FIFOs (k,k3,k4,k5):** W's `timeout -k 5 45` on ls-remote bounds them to ~45.5 s and prints RECEIPT-GIT-TIMEOUT; B hangs past 60 s. This is the t1 mechanism generalized — t1's timeout covers remote packed-refs, loose refs, HEAD, and include.path in the remote config.
- **Symlink variants (g2b,g3b,g4b,g8b,g9b,g11b):** W refuses all; B hangs on all except g2b (HEAD symlink → B fails NONREGULAR-SOURCE, not hang, because git's rev-parse fails fast on the symlink-to-FIFO? Actually B FAIL not HANG — git readlink/stat fails before open).

## Commands run

- `git show ed22dc9c:tools/souji-pre-report-gate.sh > gd-W/` and `git show a8558d41:tools/souji-pre-report-gate.sh > gd-base/` (plus writer).
- `python3 -B .ufo/waves/round-78/w1/S78ExecEvade/evade-r78.py --work /fast/scratch/hyaku/souji-r78/S78ExecEvade/evade-work --gate-w ... --gate-base ...` (16 routes, BOUND=60, own session, killpg on expiry).
- Individual `python3 -B` probes for corrected fixtures (f2 space-dir, f3 cfg call, d-gitfile commondir, e2 worktree config.worktree, h3/h5 includeIf, i2/i3 hooks/fsmonitor, j2 XDG-HOME-unset, k2-k5 remote variants, g2b/g3b/g4b/g8b/g9b/g11b symlink variants, g10ok/g11ok depth boundary, gcycle2 cycle+FIFO).

## Files written

- `.ufo/waves/round-78/w1/S78ExecEvade/evade-r78.py` (probe script, 16 routes)
- `.ufo/waves/round-78/w1/S78ExecEvade.md` (this report)
- Scratch: `/fast/scratch/hyaku/souji-r78/S78ExecEvade/` (gd-W, gd-base, evade-work, probe-*)

## Blockers / notes

- L1 landed repair at 3221566c (NUL-delimited include records, --type=path, canonical seen-set + 64-file cap, loose-ref check) after my W extraction. My W results are for ed22dc9c (the frozen W). The repair may change f2/f3/h2/h5 behavior; not tested (out of scope, L1 owns integration).
- /etc/gitconfig FIFO: cannot test without root; reasoned — gitsrc_scan checks `-f /etc/gitconfig`, FIFO → `-f` false → gitsrc_n++ → refuse. B would hang on git's first config read.
- a/b/c (alternates, loose ref, shallow): W HANGs because these are read by git during object/ref resolution, not config discovery. The 45 s timeout on check 1's git calls should bound them, but the gate's own gitsrc_scan doesn't check them and check 4's nonreg_sources doesn't either. The 60 s HANG is the runner bound, not the gate's — the gate's `timeout -k 5 45` on rev-parse/ls-remote should fire at 45 s. Wait: W HANG at 60.1 s means the gate did NOT finish within 60 s. The `timeout -k 5 45` should kill git at 45 s, then check 4 runs `git status` under `timeout -k 5 300` which ALSO hangs on the FIFO (status reads refs/objects). So W hangs in check 4, not check 1. This is a real finding: **check 4's `git status` is not protected against FIFO refs/objects/shallow** — the 300 s timeout bounds it but 300 s > 60 s runner bound. Severity: MEDIUM (W hangs for up to 300 s on a lane with FIFO refs, but eventually fails; not a forge, just slow).
