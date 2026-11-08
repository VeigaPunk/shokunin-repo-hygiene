# S82MutTool — mutation probe of W2 tools/souji-vault-verify.sh (cli_kill_tree) + p5-late-term (S81MutTool M05)

Bytes: lane file sha256 556ad94abc7341107716e30295e41c0981f980ef83263afe46ca60ba9010c032 (= git show 73110f6f:…);
every mutant is a scratch copy. Commands: `python3 -B census/round-82/c2-vault-signal-counter.py --tool <bytes> --work
<fresh>` (and the same under `env SHELLOPTS=monitor`), `TMPDIR=<fresh> bash <copy>/souji-vault-verify.sh --selftest`
with tools/souji-round9-selftest.sh beside it, plus my p5 and missing-row probes. Before: pristine 16/0/0 EXIT=0 both
launches, selftest 57/0. After the matrix (restored bytes): the same, EXIT=0; lane file/counter/population hashes and
`git status --porcelain -- tools/ census/round-82/` unchanged (sha.txt).
| mutant | default | monitor | selftest | verdict |
|---|---|---|---|---|
| M01 drop `cli_kill_tree "$pid"` (L249) | 16/0/0 | 4 mism v7,v8,m1,m2 survivors=1 | 57/0 | killed (monitor only) |
| M02 cli_kill_tree top pid only | 16/0/0 | 4 mism same rows | 57/0 | killed (monitor only) |
| M03 cli_kill_tree TERM only (no KILL) | 16/0/0 | 2 mism (v2 exited=n 5.0 s; v8 survivors=1); rerun 16/0/0 | 57/0 | SURVIVES |
| M04 drop group kill + wait loop (L250-256) | 1 mism v3 rc=0 cli=timeout; rerun 16/0/0 | 16/0/0 | 57/0 | SURVIVES |
| M05 drop trap's `rm -f "$CLI_OUT"` (L258) | 12 mism tmpleft=1 | 12 mism tmpleft=1 | 57/0 | killed |
| M06 drop `trap - TERM INT HUP` (L295) | 16/0/0 | 16/0/0 | 57/0 | SURVIVES; p5 probe kills it |
| M07 `exit 0` for 128+n (L260) | 12 mism rc=0 | 12 mism rc=0 | 57/0 | killed |
| M08 trap only TERM (L288-289) | 6 mism v2,v3,v5,v6,v8,m2 | 6 mism | 57/0 | killed |
| M09 `wait` without pid (L292) | 1 mism p2 state=cli= | 1 mism | 57/0 | killed |
| M10 `$(cli_claim)` at the call site (L447) | 13 mism (6 survivors, 6 rc=-n, p2) | 13 mism | 1 failed V11b | killed |
- MEDIUM counter:217 `rid.startswith("m-")` never matches `m1-monitor-term-fork`/`m2-monitor-hup-fork` (counter:73-74):
  the prereg label "m1/m2 run with SHELLOPTS=monitor in the tool's environment" is not implemented; under the default
  launch m1/m2 duplicate v7/v8. M01/M02 score 16/0/0 default but 4 mismatches under monitor — the default launch
  cannot see the W2 change at all; the claim holds only because the counter itself is re-launched under monitor.
- MEDIUM missing row `termign-fork` (mark; `trap "" TERM INT HUP`; `sleep 600 &`; `exec sleep 600`; SHELLOPTS=monitor,
  delivery pid, frozen SIGNALED predicate): pristine match=yes survivors=0 (twice), M03 match=no survivors=1 (twice);
  it measures the tree KILL, which no population row combines with a forked CLI.
- MEDIUM missing row `p5-late-term` REPRODUCED (stub answers, then truncates the vault to 4 GiB so the post-call
  `lv2=$(file_sha …)` hashes for seconds; TERM to the tool pid at the post-call sha256sum): pristine rc=-15, no SIG
  line, 0.00 s; M06 rc=143, SIG line, 9.18 s (the trap defers the signal behind the hash, S325). Predicate: default
  disposition, no `souji-vault-verify: SIG` line; kills M06, keeps pristine.
- MEDIUM M04 cannot be distinguished by a reachable fixture: the proposed `reparent-fork` row (`( sleep 600 & )`)
  matches both bytes (0.57 s / 0.63 s, survivors=0) — the orphan inherits timeout's group, so the tree TERM to the
  timeout pid kills it. Only an unreadable-pgrep configuration needs the group kill; that needs a mount/sysctl change
  (reported as a need, not run).
- LOW counter nondeterminism: M03's v2 (5 s SETTLE vs a 1.9-4.7 s handler) and M04's v3 (rc=0, cli=timeout, no SIG
  line; replays rc=129/130 with the SIG line) fail once and pass on rerun and replay — a false-kill path exists.
- The C2 claim holds on the pristine bytes; the W2 tree kill is load-bearing (drop: 4 rows under monitor; TERM-only: a survivor on termign-fork); surviving mutants are missing rows, not false claims.
Files: .ufo/waves/round-82/w1/S82MutTool.md; .ufo/waves/round-82/w1/S82MutTool/evidence/{matrix.txt, kill-lines.txt,
mutants.diff, sha.txt, replays.txt, p5-late-term-probe.py, probe-missing-rows.py, diag-rows.py}. Tooling: none.
