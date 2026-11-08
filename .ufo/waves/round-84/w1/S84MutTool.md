# S84MutTool — C2 repair, clause-level mutation probe (round 84, wave 1)

Seat: S84MutTool. Scope: mutation-test the C2 repair of `cli_kill_tree`/`cli_on_signal` in
`tools/souji-vault-verify.sh`. Read-only on the lane; every artifact this seat produced is under
`.ufo/waves/round-84/w1/S84MutTool/` (`candidate.sh`, `mutants/*.sh`, `receipts/`). No lane file, no git/jj
state, no fleet file was touched. No tool was installed or upgraded.

## Headline

Against the frozen 22-row population and counter, of the **nine** clauses the seat brief names:

* **bound (killed)**: exactly one — the SIGSTOP-before-signal freeze (killed by l1, l2). The whole SIGKILL sweep
  is also load-bearing as an anchor (m10 → l1, l2), but its *second-pass coverage* clause (m3) is not;
* **unbound (survived)**: the second map pass, the KILL sweep of a second-pass pid, the seen-pid de-duplication,
  the whole-file stat read, the starttime re-check at STOP, the starttime re-check at KILL, the root guard, and
  the group-kill fallback — eight survivors.
* Two of those survivors are **cheap to bind** and I proved the rows on the same instrument:
  a `nlcomm` row kills the whole-file-read mutant (candidate green, mutant 1 survivor), and a `setsidstorm` row
  binds the second map pass and the second-pass KILL sweep **once a one-line pass-2 defect is fixed** — as filed,
  the second pass catches nothing (`candidate` itself leaves 41 survivors on that row; a one-line
  `seen`-re-descend change takes it to 0).
* I also found a **fatal defect in the reference repair bytes** circulating in the wave dir: a `|| continue`
  appended to the whole-file `read -d ''` makes every per-node stat read look like EOF/failure, so the walk
  discovers nothing; those bytes score `mismatches=5`. My candidate carries the repair without that bug.

## Objects (pinned by sha256)

| object | sha256 | note |
|---|---|---|
| `census/round-84/c2-population.tsv` | `314224777425159c1fae0b7de44dec9f3fb2def83044dab32735758e87fdec58` | 22 rows, unchanged |
| `census/round-84/c2-late-fork-counter.py` | `43078272c03321dd500dea18337ca9686029b31b6b4cb931fd82d67197f6aa36` | unchanged |
| `census/round-84/controls/c2-K-a-r83-tool.sh` | `72a405f2c634712fb0211afb79f0462bf052b0b7c5fb8b663988017d2f1a8a18` | = lane r83 bytes |
| **candidate under test** `.ufo/waves/round-84/w1/S84MutTool/candidate.sh` | `f56a30f9b927712897a6b0404030d46066424ae89be3352f30dc410e5ed29b26` | 80166 B; r83 bytes + two-pass freeze walk |
| reference bytes copied at 03:19 `ref-candidate-a810aca.sh` | `a810acaf438cd6deee83a98f0db5b9697a5b5029f3126c207929c391f1130b25` | 80504 B; **red**, see F2 |

`candidate.sh` differs from `tools/souji-vault-verify.sh` in **one** hunk (`diff` → `@@ -231,49 +231,58 @@`,
`cli_kill_tree`, 47 changed lines) and nothing else; `bash -n` clean. Mutation generator invariants: same line
count, **exactly one** differing line (`x12` is the declared two-edit interaction probe), `bash -n` clean;
line, sha256 and clause per mutant in `mutants/MANIFEST.tsv`.

### Provenance (why not S84ExecC2's file)
`.ufo/waves/round-84/w1/S84ExecC2/souji-vault-verify.sh` existed but was **byte-identical to the r83 do-nothing
control** (`72a405f2…`); a candidate that is the control is INVALID by construction. Per the seat's fallback I
built the candidate from the r83 bytes. The repair text source was the wave's reference copy
`.ufo/waves/round-84/w1/RefC2/souji-vault-verify.sh`; its owner rewrote it while I worked (80257 B→80504 B at
03:19), so I froze the bytes I copied (`a810aca…`) as `ref-candidate-a810aca.sh` and the score above is **against
my frozen `candidate.sh`**, not against whatever RefC2 holds now. **Dependency to disclose: the verdicts below
certify `f56a30f9…` with the F2 line removed; if the lane integrates RefC2's `a810aca…` text as-is, C2 is red.**

## Method (frozen commands only)

```
python3 -B census/round-84/c2-late-fork-counter.py --tool <tool> --work <fresh empty dir>
```
`--work` was always `/fast/scratch/hyaku/souji-r84/S84MutTool/work-*` (never `/tmp`). Each mutant was scored on
all 22 rows; receipts in `receipts/<mutant>.txt`. Batch parallelism ≤7; every verdict that survives/kills rests
on a row-level `match=` line, not on wall-clock magnitude.

Supplementary probes (clearly **not** the frozen population) used a scratch copy of the same counter
(`receipts/probe-counter.py`, `receipts/probe-population.tsv`) with two added stubs and rows, because the frozen
population has no row for those clauses. These are labelled "probe" everywhere below; they are evidence for the
*recommendation*, never for the C2 claim.

## Results — frozen 22-row population

Pristine candidate: `SUMMARY rows=22 mismatches=0 errors=0 orphans=0`, `EXIT=0` (receipts `pristine2.txt`,
`pristine3.txt`).

| # | mutant (single edit of `candidate.sh`) | line | clause removed / weakened | SUMMARY | verdict | killer row(s) |
|---|---|---|---|---|---|---|
| m1 | `m1-term-first.sh` | 276 | `kill -STOP "$k"` → `kill -TERM "$k"` (r83 TERM-first order) | `rows=22 mismatches=2 errors=0 orphans=2` EXIT 1 | **KILLED** | l1-late-setsid-pid, l2-late-setsid-group (survivors=1 each) |
| m2 | `m2-single-pass.sh` | 244 | `for pass in 1 2` → `for pass in 1` (second map pass) | `0/0/0` EXIT 0 | SURVIVED | — |
| m3 | `m3-pass2-not-in-kill-sweep.sh` | 277 | `stopped+=("$k")` → only when `pass = 1` | `0/0/0` EXIT 0 | SURVIVED | — |
| m4 | `m4-no-seen-dedup.sh` | 268 | `[ -n "${seen[$k]:-}" ] && continue` → `:` | `0/0/0` EXIT 0 | SURVIVED | — |
| m5 | `m5-firstline-map-read.sh` | 250 | whole-file stat read → `read -r line` (first line) | `0/0/0` EXIT 0 | SURVIVED | — |
| m6 | `m6-no-starttime-at-stop.sh` | 274 | starttime re-check before SIGSTOP → `:` | `0/0/0` EXIT 0 | SURVIVED | — |
| m7 | `m7-no-starttime-at-kill.sh` | 290 | starttime re-check before SIGKILL → `:` | `0/0/0` EXIT 0 | SURVIVED | — |
| m8 | `m8-no-root-guard.sh` | 267 | `[ "$k" = "$pid" ] && continue` → `:` | `0/0/0` EXIT 0 | SURVIVED | — |
| m9 | `m9-no-term-group-fallback.sh` | 301 | `kill -TERM -"$pid" \|\| kill -TERM "$pid"` → group only | `0/0/0` EXIT 0 | SURVIVED | — |
| m10 | `m10-no-kill-sweep.sh` | 291 | `kill -KILL "$k"` → `:` (whole sweep; sensitivity anchor) | `mismatches=2 orphans=2` EXIT 1 | **KILLED** | l1, l2 (survivors=1 each) |
| m11 | `m11-no-kill-group-fallback.sh` | 306 | `kill -KILL -"$pid" \|\| kill -KILL "$pid"` → group only | `0/0/0` EXIT 0 | SURVIVED | — |
| m12 | `m12-refc2-eof-skip.sh` | 270 | **defect anchor** — append `\|\| continue` to the per-node whole-file read (the reference-copy bug) | `mismatches=5 orphans=5` EXIT 1 | **KILLED** | m1-monitor-term-fork, m2-monitor-hup-fork, d24-monitor-group, l1, l2 |
| x12 | `x12-term-first-single-pass.sh` | 244+276 | interaction probe: TERM-first **and** single pass | `mismatches=2 orphans=2` EXIT 1 | KILLED | l1, l2 |
| m13 | `m13-pass2-redescend.sh` | 268 | **repair candidate** — `seen` pid is re-pushed instead of pruning the DFS | `0/0/0` EXIT 0 | green | — |

`x12` and `m13` are not clause removals: `x12` shows freeze and pass-2 are not jointly replaceable by either
alone; `m13` is the one-line fix F7 recommends (it also stays green, so it costs nothing on the frozen rows).

### Row-level detail for the two kills
* m1: `ROW l1-late-setsid-pid … survivors=1 secs=0.8`, `ROW l2-late-setsid-group … survivors=1 secs=0.7`.
* m10: `ROW l1 … survivors=1 secs=2.9`, `ROW l2 … survivors=1 secs=2.8`.
* m1 repeated in a second run: same two rows, `survivors=1` each, EXIT 1 (`receipts/m1b-term-first-repeat.txt`).
Mechanism (verified): the `latefork` trap runs `setsid sleep 600 &`; in a non-monitor launch `setsid` is not a
group leader, so it `setsid()`s in place and the child is a tree child of the CLI — but once the CLI's trap has
run under TERM (m1) or the frozen CLI is never killed (m10), the orphan (reparented to init, in its own session)
is beyond both the map and the group kill, which is exactly the l-row target. **The l rows bind the freeze and
the sweep, not the second pass** (see F6/F7).

## Findings (each with its receipt)

**F1 — the C2 candidate circulating at probe start was the do-nothing control.** `S84ExecC2/…` =
`72a405f2…` = r83. Scoring it would be INVALID. Built from r83 bytes instead (`candidate.sh`).

**F2 — the reference repair bytes `a810aca…` are RED, and the cause is one token.** Scored as-is:
`SUMMARY rows=22 mismatches=5 errors=0 orphans=5`, EXIT 1; red rows `m1-monitor-term-fork (1 survivor)`,
`m2-monitor-hup-fork (1)`, `d24-monitor-group (24)`, `l1 (1)`, `l2 (1)` (`receipts/pristine.txt`). Cause:
bash `read -d ''` returns **1 at EOF while still assigning**, and the reference file writes
`{ IFS= read -r -d '' now < "/proc/$k/stat"; } 2>/dev/null || continue` — so **every** per-node read is treated
as a failure and no descendant is ever discovered; the tree walk is dead and only the group kill works. Proof:
`bash -c '{ IFS= read -r -d "" s < /proc/self/stat; } 2>/dev/null; echo rc=$?'` → `rc=1` (52 fields present).
Reproduced on my candidate as the single edit m12 → the identical five red rows (`receipts/m12-refc2-eof-skip.txt`).
**Fix: drop `|| continue`; test `[ -n "$now" ] || continue` instead** (what `candidate.sh` does, and the
`[ -n "$line" ]` form the map pass already uses). This is the `m`-row regression in the reference copy — the
monitor rows are red only because the tree walk is dead.

**F3 — pristine green.** `candidate.sh` (`f56a30f9…`): `rows=22 mismatches=0 errors=0 orphans=0` EXIT 0, twice
(`pristine2.txt`, `pristine3.txt`). Candidate is VALID for scoring.

**F4 — only one of the nine named clauses is bound** (the freeze; m1 → l1+l2), plus the whole-sweep anchor m10 and
the map-read defect anchor m12. Eight single-edit clause mutants survive. A survivor is a coverage finding, not a
licence to change the contract: on this population the counter certifies that the CLI's tree is frozen before any
signal and then killed, and that the per-node map read actually reads — nothing else in the walk.

**F5 — why the group fallbacks (m9, m11) cannot be bound by any row of this shape.** GNU `timeout` puts its child
in a **new process group whose pgid is timeout's pid** (verified: `timeout 30 sleep 60 &` → `timeout pid=539187
pgid=539187`, child `pgid=539187`). So `kill -TERM/-KILL -- "-$pid"` always succeeds and reaches every
group-resident descendant; the `|| kill … "$pid"` fallbacks never fire. Rows whose children stay in the group
(the `fork`/`deep` rows, and my group-inheriting `forkstorm` probe) are all cleaned by the group kill alone,
which is also why the tree walk is only observable on `setsid`/job-control rows.

**F6 — m6/m7 (starttime re-checks) and m4 (seen dedup) are not row-observable.** The re-checks only matter under
pid reuse between a read and a signal; no bounded row can force that reliably (it is a race, and a row that forces
it would be a fork-bomb). `seen` dedup can only matter if a pid is reachable twice in one walk; a pid has exactly
one ppid, so within a pass it is a pure guard against re-visiting — no row can bind it. Both should stay as
defence, but the claim's wording must not imply the population binds them.

**F7 — the second map pass, as filed, is INERT; and it is a one-line fix.** The DFS prunes at
`[ -n "${seen[$k]:-}" ] && continue` **before** `stack+=("$k")`, so in pass 2 the already-stopped CLI (and any
already-stopped ancestor) is never re-expanded: children forked into its subtree after pass 1 are never seen.
Measured with a scratch `setsidstorm` row (a CLI that forks `setsid sleep 600 &` at ~175/s and is still forking
while the tool maps `/proc`). The window is real and wide: a map pass over the box's 5051 processes costs 231 ms,
and in the first (sequential) diag block of `receipts/storm-setsid-window.log` the paced stub logged 100 forks
over 570 ms, ~43 of them in the last 250 ms before the CLI was SIGSTOPped; later blocks of that log are the three
parallel and three sequential probe runs appended to the same file, so only the first block is a clean timing
sample.

| tool | `setsidstorm` survivors |
|---|---|
| candidate `f56a30f9…` (two passes, as filed) | **41** → row red |
| m2 single pass | 41 |
| m3 pass-2 pid not in the KILL sweep | 44 |
| m13 = candidate + `seen → { stack+=("$k"); continue; }` | **0** → row green |
| x14 = m13 + single pass | 30 → red |
| x15 = m13 + pass-2 pids not in the KILL sweep | 39 → red |

`receipts/probe-ss-cand.txt`, `probe-ss-m2.txt`, `probe-ss-m3.txt`, `probe-ss-m13.txt`,
`probe-ss-x14.txt`, `probe-ss-x15.txt`. So the one-line change makes the second pass do what the stated wording
claims, and the `setsidstorm` row then kills both m2 and m3.

**F8 — a cheap row for the whole-file stat read (m5) exists and works.** Scratch `nlcomm` stub: CLI writes the
mark, starts `setsid sleep 600 &`, then `exec python3 -c 'ctypes…prctl(15, b"a\nb", …)'` so its comm carries a
newline (the kernel writes comm raw). Candidate: 0 survivors, row green. m5 (first-line read): **1 survivor**,
row red (`receipts/probe-m5.txt` vs `receipts/probe-candidate.txt`). Cost: one stub + one row, no new timing.

**F9 — a stated limit, demonstrated (not a mutant finding).** The same `nlcomm` stub under the **monitor** launch
leaves 1 survivor on the candidate too (`receipts/probe-candidate.txt`, row `pn-nlcomm-group`): under job control
the CLI's `setsid` is a process-group leader, so it forks and its child reparents to init before the walk — the
pre-registered limit "a descendant that setsids before the walk is a root of its own and is not found at all".
Not fixable by any clause in this diff; do not add such a row as a scoring row.

**F10 — the root guard (m8) is unreachable by construction.** `[ "$k" = "$pid" ]` can only fire if a pid is its
own parent; `/proc/<pid>/stat` cannot produce `ppid == pid`. No row can ever bind it; keep it only as belt and
braces and do not claim it.

## Recommendations to the L1 (integration owner)

1. Do **not** integrate the reference text as-is: remove the `|| continue` after the per-node whole-file read
   (F2), else 5 rows are red.
2. Fix pass 2 (F7): `[ -n "${seen[$k]:-}" ] && { stack+=("$k"); continue; }`. Green on the frozen 22 rows
   (m13); the second pass then actually catches the read→stop window.
3. If the C2 wording keeps the eight unbound clauses, add at most two cheap rows — `nlcomm` (kills m5, F8) and
   `setsidstorm` (kills m2 and m3 after item 2) — and narrow the sentence for m4/m6/m7/m8/m9/m11 to "defence,
   not population-bound" (F5, F6, F10). The population is frozen this round; that is a next-round amendment, not
   an edit now.
4. `x12` shows freeze and pass 2 are not interchangeable: with the freeze removed the l rows are red even with
   pass 2 present (the setsid child orphans before pass 2 can see it) — the freeze is the load-bearing clause.

## Limits of this probe

* Verdicts are against the frozen population/counter; every mutant is scored on the same 22 rows, once each.
  l1/l2 kills are survivor-based (settled 5 s sweep), not timing-magnitude-based.
* The `setsidstorm`/`forkstorm`/`nlcomm` rows are **scratch probes** in a copied counter; their survivor counts
  are timing-shaped (30–44 across runs) and they are not evidence for the frozen claim.
* Everything above certifies the `f56a30f9…` bytes; the reference copy in the wave dir is live and may differ.
* Scratch `/fast/scratch/hyaku/souji-r84/S84MutTool/` was removed after its receipts were copied into
  `.ufo/waves/round-84/w1/S84MutTool/receipts/`.
