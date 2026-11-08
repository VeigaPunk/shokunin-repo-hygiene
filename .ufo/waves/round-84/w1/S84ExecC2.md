# S84ExecC2 — C2 candidate tool (freeze-before-signal)

Seat: S84ExecC2 (executor). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. Report: this file.
Candidate dir: `.ufo/waves/round-84/w1/S84ExecC2/`. Scratch: `/fast/scratch/hyaku/souji-r84/S84ExecC2/`
(removed on exit; receipts copied here first).

## 1. Delivered

| file | what |
|---|---|
| `souji-vault-verify.sh` | the C2 candidate, sha256 `a33038e9099e31052a16201d3e23b84b0b228558ab10188679f60efde6c26b15`, mode 0755 |
| `c2-after-receipt.txt` | full counter stdout for the candidate |
| `cli_kill_tree.diff` | `diff -u tools/souji-vault-verify.sh <candidate>`: **one hunk**, only the `cli_kill_tree` comment block and the function |
| `souji-round9-selftest.sh` | verbatim copy of `tools/souji-round9-selftest.sh` (see F4) |

## 2. Candidate behavior (frozen command)

```
python3 -B census/round-84/c2-late-fork-counter.py \
  --tool .ufo/waves/round-84/w1/S84ExecC2/souji-vault-verify.sh \
  --work /fast/scratch/hyaku/souji-r84/S84ExecC2/c2
SUMMARY rows=22 mismatches=0 errors=0 orphans=0      EXIT=0
```

l1-late-setsid-pid `secs=1.4 survivors=0 tmpleft=0`, l2-late-setsid-group `secs=3.1 survivors=0 tmpleft=0`,
both `sig_line=y exited=y rc=143`. d24-term-pid `2.2`, d24-monitor-group `0.9`, d12 rows `2.0/1.4` —
all against SETTLE=5.0 s. (Host load note: every signal row took 0.9–3.5 s under concurrent fleet load;
the r83 tool's rows sit at the same scale. Absolute margin ~1.5–4 s.)

The rewrite keeps ONLY `cli_kill_tree` changed:

- Two fork-free map iterations (`for pass in 1 2`): the r83 whole-file `/proc/<pid>/stat` read with the
  `*)` last-paren strip and the `[ "$#" -ge 20 ]` field-count guard, builtins only — no pgrep/ps/cat/awk
  per pid (grep of the diff: no external call lines, only comment text).
- Each pass: DFS from the root pid; each descendant's starttime is re-read right before `kill -STOP`.
  A stopped process can neither run a TERM/INT/HUP trap nor fork, and a TERM delivered to a stopped pid
  pends until CONT — so the freeze removes the trap from the path (said in the comment, as required).
- Pass 2 re-reads the map to catch a child forked in pass 1's read->STOP window; the parent is stopped by
  then, so the child stays its child and is seen. `start_of` keeps the first write across both passes, so a
  pid recycled between the passes never passes the re-check.
- `cli_on_signal`, the group kill, the KILL fallback and the `souji-vault-verify: SIG<name>` line are
  byte-identical; the 0.1 s pause is kept; the root pid is never signalled; `seen[]` deduplicates `tree[]`.

## 3. Regressions on the candidate bytes

- `bash <candidate> --selftest` → `selftest: 57 checks, 0 failed` (with `souji-round9-selftest.sh` beside it).
- `python3 -B census/round-81/probes/tmpdir-in-vault.py --tool <candidate> --work <empty>` →
  `SUMMARY arms=4 failed=0`, all `state=cli=agree`, EXIT 0.
- r17: `bash tests/fixtures/r17-jj-receipts.sh --tool-dir /fast/scratch/hyaku/souji-r84/S84ExecC2/r17dir`
  → `SUMMARY total=35 failed=0 skipped=2`, EXIT 0. Without `--baseline-dir` the J6-verify/J6-vault
  byte-identity arms SKIP (2 skipped); all vault cases PASS. Tool dir assembled in scratch (candidate
  vault tool + lane `souji-verify.sh`/`souji-quarantine.sh`/runner, unmodified) because the fixture dies
  on a dir without `souji-verify.sh` (r17 lesson below).
- `bash -n` clean.

## 4. Findings

### F1 (followed by construction): default `--tool-dir tools` is not the r17 run for seat bytes
The seat spec says "with the tool-dir your candidate lives in" — the fixture requires `souji-verify.sh`
beside the vault tool (line 131) and SKIPs the vault tool entirely if it's absent, so the candidate must be
run from a dir holding the lane's verify/quarantine beside it. Done in scratch; the J6 arms SKIP without a
baseline dir (byte-identity needs two arms; the candidate touches no receipt path — the diff is confined to
the signal handler — so J6 cannot distinguish candidate from base. Stated, not measured, as a limit).

### F2 (LOW): `pgrep/ps/cat` grep of the candidate hits only comments
A naive per-node external-call check on the whole file matches comment lines 227/234/242 (historical r82
description, my r84 description). The diff adds no external call: inside `cli_kill_tree` the only
process-spawning lines are `kill -STOP`/`kill -KILL` builtins and `sleep 0.1` (kept from r83, once per
call, not per node). A strict per-node counter (PATH shim) would read 0, as the r83 candidate did.

## 5. Risks / stated limits of the candidate

- Same frozen limits as the prereg: `/proc` is not atomic, so a child forked in the read->STOP window whose
  parent died in that window is not a descendant any pass could see; a descendant that setsid'd before the
  walk is a root of its own; the STOP->KILL pair widens the pid-reuse window (starttime re-read before each
  signal is the only guard; pidfd unavailable in bash).
- The STOP-first ordering means a descendant that had ignored SIGSTOP... (no such case: STOP cannot be
  trapped or ignored) — every discovered pid freezes.
- Cost: two map passes + one KILL sweep per signal, all builtins. Measured deep rows 0.9–2.2 s, inside the
  5 s settle with margin under current fleet load; two passes roughly double the map cost of r83's one.

## 6. What the L1 should run

1. The frozen command on `tools/souji-vault-verify.sh` after integration (candidate sha above).
2. The three regressions in §3; r17 with a baseline dir if J6 byte-identity is required on the integrated
   bytes.
3. The K-a control is untouched; no edit to `tools/souji-vault-verify.sh`, the population or the counter
   was made from this seat (lane `git status` clean apart from this seat dir).
