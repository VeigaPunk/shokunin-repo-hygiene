# S84Sentinel — souji r84 adversarial security review (C1 certification / C2 kill scope)

Seat: S84Sentinel. Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` (read-only except this report and my seat
dir `.ufo/waves/round-84/w1/S84Sentinel/`). Scratch: `/fast/scratch/hyaku/souji-r84/S84Sentinel/` (removed on
exit). No lane tracked file was modified; no git/jj state was mutated; no process outside my own fixtures was
signalled; no pacman transaction was run (no tool install was needed — strace, python3, setsid and git were already
present).

## 0. What I measured (reproducers in my seat dir)

| script | what it does |
|---|---|
| `c1_clause_coverage.py` | drops each MOVED refusal clause of the counter (one edit each) and scores the mutant on BOTH pinned populations |
| `c1_row_flips.py` | applies the five frozen mutants + 3 extra clauses and reports WHICH row flips |
| `c1_wrong_file_demo.py` | calls the filed counter's own `judge()` on a synthetic repo; shows filed REFUSED vs mutant MOVED |
| `c1_wrong_target_search.py` | enumerates candidate target paths under 3 token shapes and counts wrong-file resolutions |
| `c1_unbound_clauses.py` | scores 4 candidate wrong rules on the 44-row population |
| `probe_c2_scope.py` | 7 kill-scope cases (newline comm, canary, reparent, setsid-after-pass, pid churn, TMPDIR-in-vault, private-file mode) + survivor identities |
| `probe_c2_killscope.py` | strace ground truth: every `kill(2)` the abort path issues, classified against the CLI's descendant set |
| `probe_c2_group_join.sh` | a canary that joins the CLI's process group: can the group kill reach a non-descendant? |
| `probe_c2_privfile.py` | private-file mode/removal + `SOUJI_*`/`TMPDIR` spoofing + a TMPDIR symlink into the vault |
| `repro_c2_newline_comm.sh` | one-command C2 reproducer for the newline-comm leak |

### Integration status at the time of writing (important)

The lane advanced while this review ran. HEAD is now `4557fc71` (`round-84: knowledge sections, QUALITY criteria,
S334-S336, lesson, plans and scorecard`), on top of `1f49b3a7` (`round-84: C2 freeze-before-signal repair in
cli_kill_tree, ...`). **The integrated `tools/souji-vault-verify.sh` is sha256
`030fa10d5b7d312c4bc2ef759495c124616b9130f6cd0a52da7be2bdbb6ef41d`**, and it already carries the F6 fix that the
seat candidate did not: every per-node re-read is a whole-file read with `[ -n "$now" ] || continue` (not the read's
exit status). I re-measured the integrated bytes directly:

```
tools/souji-vault-verify.sh  030fa10d  newline-comm reproducer -> survivors=0  RESULT: no leak
                                        selftest                 -> 57 checks, 0 failed
                                        frozen C2 counter        -> see RECEIPTS.txt
```

So **F6 and F8 are findings against the seat candidate bytes as they stood when I measured them**
(`S84ExecC2/souji-vault-verify.sh` sha `a33038e9`, `RefC2/souji-vault-verify.sh` sha `a810acaf`), not against the
integrated tool. **F7 (group-kill scope) and F9 (foreground fallback) still hold against the integrated bytes** — I
re-measured both on `030fa10d`: the group-join canary receives `sig15`, and the TMPDIR-inside-vault case still
leaves 3 CLI processes running with `rc=-15` and no SIG line. The C1 findings (F1-F4) are about the frozen
populations and the counter, which the integration did not change.

---

## 1. C1 — calibration: the population does NOT certify the counter's whole rule

### F1 — CRITICAL: two of the counter's refusal clauses are UNBOUND by BOTH pinned populations, and dropping one
### resolves a WRONG file

`c1_clause_coverage.py` drops each MOVED-refusal clause of `census/round-84/c1-pointer-counter.py` (one text edit
each) and scores the mutant on BOTH pinned populations with the frozen harness:

```
CLAUSE c1-digest              r83 mismatches=0 rc=0 | r84 mismatches=1 rc=1  -> bound
CLAUSE c2-last-component      r83 mismatches=0 rc=0 | r84 mismatches=0 rc=0  -> UNBOUND
CLAUSE c3-round               r83 mismatches=0 rc=0 | r84 mismatches=1 rc=1  -> bound
CLAUSE c4-own-tree-shape      r83 mismatches=4 rc=1 | r84 mismatches=7 rc=1  -> bound
CLAUSE c5-capture-root        r83 mismatches=2 rc=1 | r84 mismatches=2 rc=1  -> bound
CLAUSE c6-census-capture      r83 mismatches=5 rc=1 | r84 mismatches=5 rc=1  -> bound
CLAUSE c7-census-in-census    r83 mismatches=0 rc=0 | r84 mismatches=0 rc=0  -> UNBOUND
CLAUSE c8-token-has-no-round  r83 mismatches=1 rc=1 | r84 mismatches=1 rc=1  -> bound
```

The `c7` clause is the counter's own rule that a **census/round-<N> target must be a wave capture keeping the
token's full path suffix** (the r82 `PF-1` fix). Dropping it is **green on the 36-row r83 population AND on the
44-row r84 population**:

```
c7-dropped mutant on r83 (36 rows): SUMMARY rows=36 mismatches=0 accepted=0 refused_true=0 errors=0 exit=0
c7-dropped mutant on r84 (44 rows): SUMMARY rows=44 mismatches=0 accepted=0 refused_true=0 errors=0 exit=0
```

And that mutant **resolves a wrong file** (`c1_wrong_file_demo.py`, on a synthetic repo in scratch; the lane's
population files are untouched):

```
# token   (absent at rev): census/round-61/waves/a2w1/S61ExecRealRecord/erratum-evidence.txt
# target  (decoy present) : census/round-61/w2/a2w1/S61ExecRealRecord/erratum-evidence.txt
FILED counter  -> REFUSED  class=MOVED why=census-in-tree target is not a wave capture keeping the token's full path suffix
C7-DROPPED     -> MOVED
VERDICT: WRONG FILE RESOLVED
```

`c1_wrong_target_search.py` enumerates the paths and finds two such targets for one token shape:

```
# token census/round-61/waves/a2w1/S61ExecRealRecord/erratum-evidence.txt
  MUTANT c7-census-in-census: 2 wrong-file resolutions
    target=census/round-61/w2/a2w1/S61ExecRealRecord/erratum-evidence.txt
      filed  -> REFUSED (census-in-tree target is not a wave capture keeping the token's full path suffix)
      mutant -> MOVED
    target=census/round-61/w1/a2w1/S61ExecRealRecord/erratum-evidence.txt
      filed  -> REFUSED (same reason)
      mutant -> MOVED
```

**The battery certifies the wrong rule end to end.** The strongest form of the finding is not the harness exit
code but the round's own counting command. Run `c1-clause-battery.py` with the **c7-dropped counter as the counter
under test**:

```
### --only r84 --expect-killed 5
SUMMARY mutants=5 sets=r84 pristine_r84=ok killed_r84=5 killed_total=5           (EXIT 0)
### --only r83 --expect-killed 0
SUMMARY mutants=5 sets=r83 pristine_r83=ok killed_r83=0 killed_total=0           (EXIT 0)
```

Every number in the frozen claim's counting sentence is reproduced — both pristine arms green, `killed_r84=5`,
`killed_r83=0` — **on a counter that resolves a wrong file**. So the sentence "the lane's false-row population is
the instrument that certifies the pointer counter's rule" is false as measured: the instrument certifies a rule
that resolves a wrong file. (The counter's five named mutant clauses are still bound; the unbound `c7` clause is a
sixth clause the instrument never exercises.)

**Why the population cannot bind it.** The clause is reachable only when the TOKEN itself lives under
`census/round-<N>/`. No pinned population item has such a token: the only census-token items with a frozen digest
are `P28`/`L02`/`L03` (`census/operator-sweep-20261019`), and that token names no `round-<N>`, so the counter's
`not kr` clause refuses it first. Every `MOVED` row in the 44-row population has an **own-tree** token
(`.ufo/waves/round-<N>/...`), so the `c7` branch is never reached.

**Scope note (honest):** the r84 claim as *worded* says the population carries "one FALSE row per clause" for the
five clauses it names (m6..m10). That wording is **true and measured**. What is falsified is the stronger sentence
the round answers for — "the lane's false-row population is the instrument that certifies the pointer counter's
rule" — because a rule that resolves a wrong file (the `c7`-dropping mutant) is certified green by **both**
populations. The population certifies five clauses, not the counter's rule.

**Smallest remediation (L1):** either (a) add one FALSE row whose token is a `census/round-<N>/` path with a
frozen digest and whose target is a non-capture directory under the same tree, or (b) narrow the r84 claim's C1
sentence to "certifies five named clauses" and record the `c7` gap in the round's stated limits. Option (a) is
what makes the sentence true; option (b) is what makes the sentence honest.

### F2 — MEDIUM: the "last component" clause is also UNBOUND, but no wrong file was found

`c2-last-component` (the counter's rule that the MOVED target's last component must equal the token's) is green on
both populations:

```
CLAUSE c2-last-component      r83 mismatches=0 rc=0 | r84 mismatches=0 rc=0  -> UNBOUND
```

`c1_wrong_target_search.py` searched 17 target directory layouts × 3 filenames × 3 token shapes and found **0**
wrong-file resolutions for it, so this is an unbound clause with no demonstrated wrong-resolution consequence
(it is redundant with the suffix rules for every shape I could construct). Reported as a coverage gap, not a
wrong-resolution. **Remediation:** one FALSE row whose target has the token's suffix but a different last
component (e.g. `.../w2/erratum-evidence-RENAMED.txt`) would bind it.

### F3 — MEDIUM: the r84 population's own row-to-clause mapping is not one row per clause

`c1_row_flips.py` reports the exact rows each mutant flips (44-row population):

```
MUTANT m6-digest-blind   -> ['NF-L']                          (1 row)
MUTANT m7-round-blind    -> ['NF-L2']                         (1 row)
MUTANT m8-w-only-shapes  -> ['TF10', 'TF9']                   (2 TRUE rows refused)
MUTANT m9-basename-only  -> ['NF-P', 'TF10', 'TF8', 'TF9']    (1 FALSE accepted + 3 TRUE refused)
MUTANT m10-records-as-wave -> ['NF-M']                        (1 row)
```

So of the eight new rows, **`NF-Q` flips under no frozen mutant**. `NF-Q` is the round's stated "a real wN/ prefix
that drops the token's suffix" row; the rule it is filed to bind is a *shape-only* rule (`got[-1] == want[-1]`), and
that rule is **not** among the five frozen mutants. It IS bound by the population — `c1_unbound_clauses.py` /
the wrong-rule sweep show a shape-only rule is killed by the 44-row population (`mismatches=3`, flipping
`NF-J`, `NF-P`, `NF-Q`) — but the **frozen battery never tests it**, so `killed_r84=5` does not demonstrate that
`NF-Q` binds anything. A reader of the receipt would conclude `NF-Q` is covered; it is not covered *by the
battery*. **Remediation:** add the shape-only rule as a sixth frozen mutant (its `old` text occurs exactly once in
the counter, so the battery's `old`-must-occur-once gate is satisfied), or say in the claim that `NF-Q` is bound by
the population but not exercised by the frozen battery.

### F4 — LOW: the r84 population does not bind one more wrong rule that the counter's own text forbids

A rule that accepts an own-tree target whose FIRST component after the wave dir matches the token's, ignoring the
rest (`got[1:2] == want[1:2]`) is green on both populations:

```
RULE w5-owntree-first-component: r83 SUMMARY rows=36 mismatches=0 ... rc=0 flips=[] | r84 SUMMARY rows=44 mismatches=0 ... rc=0 flips=[] -> GREEN-ON-BOTH
```

No wrong-file resolution was demonstrated for it (it is strictly weaker than the shape-only rule, which the
population does bind). Recorded as a lower-severity instance of F1's class.

### F5 — verified-true (no finding): the frozen C1 measurements reproduce exactly

```
ARM pristine pop=r84 rows=44 mismatches=0 errors=0 exit=0
MUTANT m6-digest-blind   pop=r84 killed=yes mismatches=1 ; MUTANT m7-round-blind killed=yes mismatches=1
MUTANT m8-w-only-shapes  pop=r84 killed=yes mismatches=2 ; MUTANT m9-basename-only killed=yes mismatches=4
MUTANT m10-records-as-wave pop=r84 killed=yes mismatches=1
SUMMARY mutants=5 sets=r84 pristine_r84=ok killed_r84=5 killed_total=5

# the do-nothing control on the r83 population:
ARM pristine pop=r83 rows=36 mismatches=0 errors=0 exit=0
MUTANT m6..m10 pop=r83 killed=no (all five)
SUMMARY mutants=5 sets=r83 pristine_r83=ok killed_r83=0 killed_total=0
```

Also verified: the r84 counter is byte-identical to the r83 counter
(`sha256 052c4f3fdb3f902971b70f80653b4e84dc9a6b1c8deed355f067b3ff7d131d79` for both), and the 44-row population's
first 36 data rows are byte-identical to the r83 population's 36 rows (checked programmatically: prefix
byte-identical True, new rows exactly `TF8 TF9 TF10 NF-P NF-L NF-L2 NF-M NF-Q`).

---

## 2. C2 — operability: the freeze repair's kill scope

The claim: `cli_kill_tree` freezes the CLI's descendant tree before terminating it, so a CLI that traps the caller's
signal and forks a `setsid`'d child leaves nothing behind. The kill rule that matters to me: **a signal delivered
to a pid outside the CLI's descendant set fails the claim.**

### F6 — CRITICAL: the frozen 22-row population does NOT bind the "CLI's comm holds a newline" case, and the
### candidate that passes the frozen counter STILL leaks a setsid'd child through it

The frozen population's 22 stubs are all `#!/bin/bash` scripts; their `/proc/<pid>/stat` `comm` is a plain word
(`bash`, `cli-latefork`, ...). **No stub in the frozen population has a newline or a `)` in its comm.** The r83
spot-check already routed this as defect **D5** ("the TERM/KILL re-reads read the first line only, so a comm
carrying a newline truncated them") — and the r83 bytes fixed the *map* pass but **not** the per-node re-read.

A CLI can set its own comm to any bytes it likes (`prctl(PR_SET_NAME)`); the kernel writes them into
`/proc/<pid>/stat` **unescaped**, so a comm holding a newline makes the stat file two lines. A per-node re-read of
only the FIRST line then yields a truncated record.

Measured with `probe_c2_scope.py` / `repro_c2_newline_comm.sh` (the CLI's comm is `a\nb)c`):

```
# tool sha256=a33038e9099e31052a16201d3e23b84b0b228558ab10188679f60efde6c26b15 (the C2 candidate that PASSES the
#            frozen counter: SUMMARY rows=22 mismatches=0 errors=0 orphans=0)
CASE nlcomm_trap exited=y rc=143 sig_line=y survivors=1
  surv_detail=[(2035049, 'a\nb', 'S', 1487)] tmpleft=[] canary_hits=[]
```

and with the one-command reproducer:

```
# cli comm    : a?b)c?
# SURVIVOR pid=3762651
# survivors   : 1
RESULT: LEAK (a setsid'd child of the CLI survived the abort path)
```

**The leak is a NEW one, not the r83 baseline's**: the r83 control leaks here too (same `survivors=1`), but for a
different reason (r83 never freezes at all, so the CLI's TERM trap always runs). The r84 candidate's *whole point*
is that the freeze removes the trap from the path — and with a newline comm the freeze **never reaches that process**,
so the trap runs exactly as in r83. The candidate therefore scores 22/22 green while the behaviour the round claims
to fix is still present for that CLI.

**Root cause (exact, verified).** The candidate's per-node re-read is a first-line read:

```
279:        { read -r now < "/proc/$k/stat"; } 2>/dev/null || continue
293:    { read -r now < "/proc/$k/stat"; } 2>/dev/null || continue
```

For a comm with a newline the first line is `1234 (a` — 4 fields, not 20 — so the `[ "$#" -ge 20 ]` guard skips
the node: it is never SIGSTOPped and never SIGKILLed. The r83 routed defect D5 is thus **reintroduced** by the r84
candidate, in the very code path the repair depends on.

**Proof that this is the whole cause.** One-line fix to the candidate (my seat dir, `cand-execC2-fixed.sh`): read
the whole stat file, and do not use the read's exit status as the node guard (`read -d ''` returns **1** at EOF
because `/proc/<pid>/stat` has no NUL byte, so `|| continue` would skip *every* node):

```
279:        { IFS= read -r -d '' now < "/proc/$k/stat"; } 2>/dev/null
280:        [ -n "$now" ] || continue
293:    { IFS= read -d '' now < "/proc/$k/stat"; } 2>/dev/null
294:    [ -n "$now" ] || continue
```

Result on the same reproducer:

```
# cli comm    : a?b)c?
# survivors   : 0
RESULT: no leak
```

**Why this is CRITICAL rather than LOW.** The kill rule's target is "a signal delivered to a pid outside the
CLI's descendant set"; here the *inverse* holds and it is worse: the tool's own freeze silently does not apply, the
adversarial CLI's trap runs, and a `setsid`'d child survives the abort path — the exact failure the round claims to
close (`l1`/`l2`). The frozen population cannot see it, so `killed_r84=5 / mismatches=0` is **not** evidence for the
claim's stated wording.

**Smallest remediation (L1):** in the candidate's `cli_kill_tree`, replace both per-node re-reads with a whole-file
read whose *presence* (not its exit status) is the guard — the two lines above are the whole change. This is the
r83 spot-check's D5 fix applied to the code the repair depends on. **Already applied in the integrated tool**
(sha `030fa10d`): re-measured `survivors=0` on this reproducer. Keep it applied; the seat-dir candidate
(`a33038e9`) and the sibling candidate (`a810acaf`) both lack it. (Note the trap in the sibling candidate
`RefC2/souji-vault-verify.sh`: it uses `{ IFS= read -r -d '' now < ...; } 2>/dev/null || continue` — the *exit
status* guard — which skips **every** node, so that candidate's tree walk is a no-op. Measured: that candidate
scores `SUMMARY rows=22 mismatches=4 errors=0 orphans=4` on the frozen counter, with `d24-monitor-group
survivors=24` and `l2-late-setsid-group survivors=1`. So it fails the claim outright; only the guard's *shape* is
wrong there, not the read's width.)

### F7 — HIGH: the abort path's group kill reaches pids outside the CLI's descendant set

The abort path ends with `kill -TERM -- "-$pid"` and `kill -KILL -- "-$pid"` — a **process-group** kill, not a
descendant-set kill. `probe_c2_killscope.py` (strace ground truth) shows those calls on every run, e.g.:

```
# tool sha256=a33038e9... case=plain cli_pid=515883
  KILL target=-515819 sig=SIGTERM class=OUTSIDE   513896 kill(-515819, SIGTERM) = -1 ESRCH
  KILL target=515819   sig=SIGTERM class=OUTSIDE   513896 kill(515819, SIGTERM)   = -1 ESRCH
  KILL target=-515819   sig=0      class=OUTSIDE   513896 kill(-515819, 0)
  KILL target=515819    sig=0      class=OUTSIDE   513896 kill(515819, 0)
  KILL target=-515819   sig=SIGKILL class=OUTSIDE  513896 kill(-515819, SIGKILL) = -1 ESRCH
  KILL target=515819    sig=SIGKILL class=OUTSIDE  513896 kill(515819, SIGKILL)   = -1 ESRCH
```

`515819` is the `timeout` wrapper's pid — the group id, **not** a descendant of the CLI. This is pre-existing r81
behaviour (the group kill is the r81 design), so it is not an r84 regression; but it is the one place where the
tool's abort path can reach a pid outside the CLI's descendant set, and the r84 claim's kill rule names exactly
that. `probe_c2_group_join.sh` (a bash driver, because the canary must share the tool's *session* to be able to join
the CLI's group) tests the exploit directly. A canary that is **not** a descendant and joins the CLI's process group
**receives SIGTERM**:

```
# tool        : .../S84Sentinel/cand-execC2.sh      (and: cand-r83.sh - same result)
# cli pgid    : 1105083
# canary joined the CLI's process group
# canary log  : start joined-pgid-1105083 joined sig15
# canary signals received: 1
RESULT: SIGNAL TO A NON-DESCENDANT (CRITICAL)
```

By my acceptance rule ("a signal to a non-descendant is CRITICAL") this is CRITICAL against the claim's kill rule,
and it is **pre-existing**: the r83 control (`cand-r83.sh`) produces the identical result, so it is the r81 group
kill, not an r84 regression. **Re-measured against the INTEGRATED tool (`030fa10d`): identical result** — the
canary still receives `sig15`. So this finding stands against the bytes now at HEAD. The precondition is stated honestly: the victim must be in the tool's session and must
itself call `setpgid(2)` into the CLI's group (the probe's canary does exactly that). Under the *default* launch the
group kill is a no-op (`ESRCH`, measured by strace, because `timeout ... &` stays in the caller's group so no group
with the CLI pid exists); under `SHELLOPTS=monitor` the group is `timeout`'s own group
(`timeout` + CLI + its non-`setsid` descendants). **Remediation (L1):** state the limit in the r84 claim ("the
abort path also TERMs/KILLs the CLI's process group, so a process in that group is signalled even if it is not a
descendant; only descendants are SIGSTOPped"), and — if the claim is to hold literally — replace the group kill with
the descendant-set kill the freeze already computes (the tree walk targets exactly the descendant pids).

### F8 — HIGH: the C2 candidate fails its own frozen counter on a monitor-launch row and on `l2`

Measured with the frozen command on the sibling candidate `RefC2/souji-vault-verify.sh`
(sha256 `a810acaf438cd6deee83a98f0db5b9697a5b5029f3126c207929c391f1130b25`):

```
ROW d24-monitor-group ... survivors=24 ... match=no
ROW l2-late-setsid-group ... survivors=1 ... match=no
SUMMARY rows=22 mismatches=4 errors=0 orphans=4
```

By contrast the candidate at `.ufo/waves/round-84/w1/S84ExecC2/souji-vault-verify.sh`
(sha256 `a33038e9099e31052a16201d3e23b84b0b228558ab10188679f60efde6c26b15`) measures:

```
SUMMARY rows=22 mismatches=0 errors=0 orphans=0
```

**L1 must integrate the `a33038e9` bytes (plus the F6 fix), not the `a810acaf` bytes.** The r83 control
(`c2-K-a-r83-tool.sh`) measures `SUMMARY rows=22 mismatches=2 errors=0 orphans=2` (l1 and l2 red, one survivor
each), matching the frozen receipt `census/round-84/controls/c2-before-r83-tool.txt`.

### F9 — MEDIUM: `tmpvault` — with TMPDIR inside the vault the tool has NO signal handler, so the CLI tree survives
### the signal entirely

`probe_c2_scope.py` case `tmpvault` (TMPDIR = the vault directory; `cli_tmp_ok` then refuses the private file and the
call runs in the foreground, where the tool installs **no** trap):

```
CASE tmpvault exited=y rc=-15 sig_line=n survivors=3
  surv_detail=[(2152001,'bash','S',1487), (2152006,'timeout','S',2152001), (2152022,'python3','S',2152006)]
```

The tool dies from the default SIGTERM disposition (rc=-15, no `souji-vault-verify: SIGTERM` line) and the whole
CLI subtree is left running. This is pre-existing r81 behaviour (the tool documents "If no private file can be made
the call runs in the foreground as before (no trap)"), and the r83 bytes behave identically (measured: r83
`tmpvault` also `rc=-15 sig_line=n survivors=3`). **Re-measured against the INTEGRATED tool (`030fa10d`):
`rc=-15 sig_line=n survivors=3`** — unchanged. **It is a scope limit of the r84 wording, not a regression**:
the claim says "the vault CLI's signal path freezes the descendant tree before terminating it" — but there is no
signal path at all in this configuration. **Remediation (L1):** state the limit in the r84 claim ("the freeze
applies to the private-file (asynchronous) call path only; when TMPDIR is inside the vault the call runs in the
foreground with no trap and the CLI subtree is not frozen").

### F10 — verified-true (no finding): the private file and the environment surface

`probe_c2_privfile.py` on the candidate:

```
CASE baseline: priv_during=[('tmp/souji-vault-cli.oeYSYd', '0o600')] priv_left_after_signal=[] sig_line=y rc=143
CASE vault-hint-spoof: priv_during=[('tmp/souji-vault-cli.Yvy4Nx', '0o600')] priv_left_after_signal=[] sig_line=y rc=143
CASE cli-timeout-1: priv_during=[('tmp/souji-vault-cli.Pys9qQ', '0o600')] priv_left_after_signal=[] sig_line=y rc=143
CASE tmpdir-symlink-into-vault: private file written UNDER THE VAULT during the call=[] after=[]
```

- The private CLI file is **mode 0600** (`mktemp` default) and is **removed on the signal path**
  (`priv_left_after_signal=[]`).
- Spoofing `SOUJI_VAULT` at a nonexistent path does not change the file's mode or its removal.
- A `TMPDIR` that is a **symlink into the vault** does not defeat `cli_tmp_ok`: `readlink -m` resolves the symlink
  (the tool canonicalises with `readlink -m`), so the tool still refuses the private file and **nothing is written
  under the vault** (`during=[] after=[]`). Good.
- The one env vector that does change behaviour is `TMPDIR` *inside* the vault (F9) — the tool's own documented
  fallback, not a spoof.

### F11 — verified-true (no finding): the canary never receives a signal, under pid churn

`probe_c2_scope.py` case `canary` (a pre-existing, non-descendant process with TERM/INT/HUP/QUIT traps) and case
`churn` (the driver forks/exits in a tight loop while the tool walks, to recycle pids under the tool's feet):

```
CASE canary  ... canary_hits=[]  survivors=0
CASE churn   ... canary_hits=[]  survivors=0
```

on the r83 control, the RefC2 candidate and the ExecC2 candidate. The strace ground truth agrees: on the plain
case the only `SIGSTOP`/`SIGKILL` targets were the CLI's own pid, and every group-signalled target was already
dead (`ESRCH`). **So the tree-walk signals stay inside the CLI's descendant set in every fixture I could
construct.** Two qualifications, both measured above: (a) a canary that *joins the CLI's process group* does
receive the group kill (F7 — that is the pre-existing r81 group kill, not the tree walk); (b) the pid-reuse window
the claim's stated limits already name ("a pid reused between the last read and the KILL, with the same starttime,
would be signalled") is the residual risk for the tree walk; I could not turn it into an observed mis-kill, and I
did not observe one.

### F12 — verified-true (no finding): the candidate passes the other three frozen gates

- `tools/souji-vault-verify.sh --selftest` (candidate copied beside `souji-round9-selftest.sh`, as the tool's own
  R9 check requires): `selftest: 57 checks, 0 failed`.
- `census/round-81/probes/tmpdir-in-vault.py --tool <candidate>`: `SUMMARY arms=4 failed=0`.
- `tests/fixtures/r17-jj-receipts.sh --tool-dir <dir with the candidate as souji-vault-verify.sh>`:
  `SUMMARY total=35 failed=0 skipped=2`.

---

## 3. Findings summary

| # | axis | severity | finding | status against HEAD (`030fa10d`) |
|---|---|---|---|---|
| F1 | C1 | **CRITICAL** | two counter clauses (`c7-census-in-census`, `c2-last-component`) are UNBOUND by BOTH pinned populations; dropping `c7` resolves a WRONG FILE while both populations score GREEN | **open** — the populations and counter are unchanged by the integration |
| F7 | C2 | **CRITICAL (pre-existing)** | the abort path's process-GROUP kill signals a canary that joined the CLI's group — a pid outside the descendant set; identical on the r83 control | **open** (re-measured: canary gets `sig15`) |
| F9 | C2 | MEDIUM | with TMPDIR inside the vault the tool installs no trap at all: `rc=-15`, no SIG line, 3 CLI processes survive | **open** (re-measured: unchanged) |
| F2 | C1 | MEDIUM | the "last component" clause is UNBOUND by both populations (no wrong file found in 153 enumerated shapes) | **open** |
| F3 | C1 | MEDIUM | `NF-Q` flips under NO frozen mutant; the shape-only rule it is filed to bind is not in `c1-mutants.json` | **open** |
| F4 | C1 | LOW | an own-tree first-component-only rule is green on both populations (no wrong file demonstrated) | **open** |
| F6 | C2 | **CRITICAL against the candidate, fixed at HEAD** | a CLI whose comm holds a newline is never frozen (r83 routed defect D5, first-line stat re-read) and its `setsid`'d child survives | **FIXED in the integrated bytes** (`030fa10d`, re-measured `survivors=0`); still present in `a33038e9` and `a810acaf` |
| F8 | C2 | **HIGH against the candidate** | `RefC2/...` (sha `a810acaf`) FAILS the frozen counter (`mismatches=4`); its `read -d ''` + `|| continue` skips every node | **not integrated** (the integrated bytes come from the `a33038e9` line and pass) |
| F5, F10-F12 | both | verified | the frozen C1 measurements, private-file mode/removal, `SOUJI_*`/`TMPDIR` spoofing, the canary and pid-churn scope, and the three frozen gates | reproduce as claimed |

**The claim-level consequences that survive the integration:** F1 (the population does not certify the counter's
rule — a wrong-file-resolving rule is green on both populations) and F7/F9 (two configurations where the "the CLI's
signal path freezes the descendant tree" sentence is not true: the group kill reaches non-descendants, and the
foreground fallback has no trap at all).

### What the L1 must do (as of HEAD `030fa10d`)

1. **C1 (F1) — the live claim defect.** Either add one FALSE row whose token is a `census/round-<N>/` path with a
   frozen digest and whose target is a non-capture directory under the same tree, or narrow the r84 C1 sentence to
   "certifies the five named clauses" and record the `c7`/`c2` gap in the stated limits. As filed, a counter that
   resolves a wrong file scores green on **both** populations.
2. **C2 (F7) — state or fix the group-kill scope.** Add it to the stated limits, or make the abort path
   descendant-only (the freeze already computes exactly that set).
3. **C2 (F9) — state the foreground-fallback limit** in the claim: the freeze exists only on the private-file path.
4. **C2 (F6/F8) — keep the whole-file re-read** that HEAD already has, and do not integrate the `a810acaf` bytes.
5. **C1 (F3/F2) — optional hardening:** add the shape-only rule as a sixth frozen mutant, and one row for the
   last-component clause.

### Reproduce everything

```
L=/home/vgpnk/Projects/shokunin/souji-shokunin
S=$L/.ufo/waves/round-84/w1/S84Sentinel
W=/fast/scratch/hyaku/souji-r84/S84Sentinel    # any empty dir outside /tmp

# C1
python3 -B $L/census/round-84/c1-clause-battery.py --counter $L/census/round-84/c1-pointer-counter.py \
        --work $W/b1 --only r84 --expect-killed 5          # SUMMARY killed_r84=5
python3 -B $L/census/round-84/c1-clause-battery.py --counter $L/census/round-84/c1-pointer-counter.py \
        --work $W/b2 --only r83 --expect-killed 0          # SUMMARY killed_r83=0
python3 -B $S/c1_clause_coverage.py --work $W/cov          # the UNBOUND clauses
python3 -B $S/c1_wrong_file_demo.py --work $W/wfdemo       # filed REFUSED vs c7-dropped MOVED
python3 -B $S/c1_row_flips.py --work $W/flips              # which row each mutant flips

# C2
python3 -B $L/census/round-84/c2-late-fork-counter.py --tool $S/cand-integrated.sh --work $W/c0   # HEAD: 22/0/0/0
python3 -B $L/census/round-84/c2-late-fork-counter.py --tool $S/cand-execC2.sh     --work $W/c1   # 22/0/0/0
python3 -B $L/census/round-84/c2-late-fork-counter.py --tool $S/cand-refc2.sh      --work $W/c2   # mismatches=4
python3 -B $L/census/round-84/c2-late-fork-counter.py --tool $S/cand-execC2-fixed.sh --work $W/c3 # 22/0/0/0
bash $S/repro_c2_newline_comm.sh $S/cand-execC2.sh        # survivors=1  (the leak)
bash $S/repro_c2_newline_comm.sh $S/cand-execC2-fixed.sh  # survivors=0  (the fix)
bash $S/repro_c2_newline_comm.sh $S/cand-integrated.sh     # survivors=0  (HEAD already has it)
bash $S/repro_c2_newline_comm.sh $S/cand-r83.sh           # survivors=1  (pre-existing)
python3 -B $S/probe_c2_scope.py --tool $S/cand-execC2.sh --work $W/sc
bash $S/probe_c2_group_join.sh $S/cand-execC2.sh $W/gj    # canary receives sig15
python3 -B $S/probe_c2_privfile.py --tool $S/cand-execC2.sh --work $W/pf
```

### Tooling record

No tool was installed or upgraded (the seat needed only `bash`, `python3`, `strace`, `setsid`, `git`, all present).
No pacman transaction was attempted.
