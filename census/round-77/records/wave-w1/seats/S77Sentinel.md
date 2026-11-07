# S77Sentinel — fail-closed / security / resource review of W 9b496b08 + K 6690cb5a
VERDICT: the W refusal mechanism reproduces; no route found to a false `check-clean=PASS` of a source git would open. 3 MEDIUM (guard scope, unbounded pre-check hang, signal leak), 5 LOW. K capture: no credential, no host leak, no finding.
Blobs: /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-pre-report-gate.sh sha256 28a5135573091a253c69809c4134a3a031da014f7e1bccea5860975d127616be
at W=A=HEAD (base 90bdd8c7…47f3 = prereg), writer 70bbf1c2…bfa; K = 14 files, not 15 (raw: 14 “A”, 100644/100755, no symlink).
Route table (real W blob; fixtures/probes in /fast/scratch/hyaku/souji-r77/S77Sentinel and …/w1/S77Sentinel/):
- :70 `git rev-parse --absolute-git-dir` — ok, no exec (probe2 marker empty); HANG on repo-local `include.path`→FIFO (rc=124, probe1).
- :76 `git config --path --get core.excludesFile|core.attributesFile` — ok, no exec; includeIf/hooksPath/alias inert; same HANG. Both new calls run outside `gate_timeout` (:86 assigns it; only :95/:97 use it).
- :82 `find … -path "$lane/.git" -prune` — ok: 0.04 s / 4052 KiB on this lane, 0.08 s / 4228 KiB on a 200k-entry ignored
  tree, no `-L`; a newline dir name inflates the count 1→2 and never 0; defects LOW-1/2/3.
- :95 `git status` under `timeout -k 5 300` — EXEC: repo-local `core.fsmonitor` runs (probe2 marker; :95 lacks the
  `-c core.fsmonitor=false` of :134/:161), timeout-bounded, byte-truth rehash still catches a lying status; a guard-missed
  source blocks it → 300 s → `check-clean=FAIL`, never a pass.
- :97 python block under `timeout -k 5 300` — expiry kills it clean (probe10a: no leak, FAIL “byte truth: no output”).
- Refusals — 18/18 exit 1, class RECEIPT-NONREGULAR-SOURCE, zero path echo (D30; -1 branch prints “source scan failed”).
  Real lane guard count 0 (find=0; .git/info/exclude regular; info/attributes and XDG defaults absent; excludesFile unset).
Numbers re-derived: `python3 -B census/round-77/c1-nonreg-counter.py --gate-dir <s>/gateW --work <s>/c1work` →
`SUMMARY rows=16 mismatches=0 errors=0 hangs=0` EXIT=0; base gate on a FIFO .gitignore rc=124 at 5 s, n8 shape PASS 79 ms.
`python3 -B census/round-77/c2-pointer-counter.py --root . --rev ef04ca6c… --fleet-root /home/vgpnk/Projects/shokunin
--ledger census/round-77/c2-pointer-ledger.tsv` → `SUMMARY items=35 resolved=35 unresolved=0 refused=0 mismatched=0 errors=0`
EXIT=0; `tools/souji-pointer-check.py --root . --rev <rev> <six files>` → missing=35 at base, 31 at A.
MEDIUM-1 guard scope ≠ git read set (probe6/11/12). Worktree lane: gate checks `<absolute-git-dir>/info/exclude`, git reads
 `<common>/.git/info/exclude` (`git rev-parse --git-path`) → guard blind, FIFO at the real path, gate 3012 ms (3 s probe copy;
 300 s real) → `detail-clean: git status failed or timed out:`. Same for a --lane that is a repo subdirectory (find scans only
 $lane, git reads the whole work tree). Fix: `--git-path info/exclude|info/attributes`, scan `--show-toplevel`.
MEDIUM-2 repo-local `include.path`→FIFO in a regular .git/config hangs the gate before every check, no output, no timeout
 (probe1 rc=124 on all four git calls; no trap, so only an external kill ends it). The prereg limit names only “a FIFO
 $GIT_DIR/config”. Fix: wrap :70/:76 in the same `timeout`, map expiry to the -1 refusal.
MEDIUM-3 no signal handling: SIGTERM leaves the check-4 subtree alive (subshell, `timeout`, git, fsmonitor hook, hook child —
 probe7b LEAK COUNT=5 incl. `sleep 600`) and the python block (probe10b leaks=3). Bounded ≤305 s only where the `timeout`s
 apply; unbounded for check 1 and the new pre-check. Fix: EXIT/TERM trap killing the group, or `setsid` + group kill.
LOW-1 “a symlink counts by its target” holds only for -e/-f; the work-tree `! -type f` refuses symlink→regular (probe5 FAIL 13 ms).
LOW-2 `f=$(find … | wc -l) || { echo -1; }` is dead (pipeline rc = wc's): mode-000 dir with the only FIFO → count=0, rc=0, find rc=1.
LOW-3 prune is a string match: trailing slash, /./ or glob chars make find descend into .git and refuse a FIFO named .gitignore there (PASS 50 ms vs false FAIL 12 ms).
LOW-4 :95 runs repo-local core.fsmonitor (EXEC, pre-existing, bounded); one `-c core.fsmonitor=false` fixes it. LOW-5 the timeout branch prints an empty status value (cosmetic).
K capture 6690cb5a: 14 UTF-8 blobs, no NUL/ESC, no symlink, 5 × 0755 (275 tracked 0755 `.ufo/waves` at A); no
key/token/auth-header/private-key shape (`token` hits are identifiers: writer:180, freeze-check:229/232); host data only
`/fast/scratch/hyaku/souji-r64/...` (selftest.txt:1, sha256.txt:1-2), no /home, /root, vgpnk, .ssh, .omp — precedent at A:
4246 files with /fast/scratch, 6694 with /home/vgpnk. Files written: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-77/w1/S77Sentinel.md
and S77Sentinel/probe{1,2,3,4,5,6,7,7b,8,9,10,11,12}-*.sh; no tool installed. Seat mishap, self-corrected, lane untouched:
one probe script briefly landed at fleet-root .ufo/waves/round-77/w1/S77Sentinel/, removed the same minute.
