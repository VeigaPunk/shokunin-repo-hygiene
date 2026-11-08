# DRAFT — `corpus/knowledge/gate-signal-handling.md`, new section (r84)

Seat: S84Scribe (drafts only; the L1 integrates). Draft file; the L1 pastes the block below into
`corpus/knowledge/gate-signal-handling.md` and lands the file. Every path, digest and number below is a committed
path or a receipt cited in the round's own artifacts; nothing here asserts a verdict the round has not measured.

> **STATUS: superseded as an integration input.** The L1 landed its own version of this section at `4557fc71`
> under the title "Freezing the tree before signalling it (r84, `tools/souji-vault-verify.sh`)". This draft is
> kept for the L1 to re-check or extend; where the two differ the **landed text is the lane's**. Two things this
> draft carries that the landed text does not: the **read-guard hazard** (the whole-file read's exit status is
> not a guard — the lesson's M2/M4), and the **per-row timing** of the late rows from an independent re-run.

## Section title

`## A re-walk after the TERM pass (r84, `tools/souji-vault-verify.sh`)`

## Draft block (paste-ready)

---

## A re-walk after the TERM pass (r84, `tools/souji-vault-verify.sh`)

source: S331 (own-work wave-directory census), S332 (kernel fs/proc/array.c at v6.17), S075, S326;
census/round-84/c2-late-fork-counter.py; census/round-84/c2-population.tsv
verified-at: <the commit the L1 lands the tool at> (2026-11-08)
recheck: python3 -B census/round-84/c2-late-fork-counter.py --tool tools/souji-vault-verify.sh --work <empty dir outside /tmp>

- **The escape: a CLI that reacts to the signal and leaves the group.** The r83 walk read `/proc` once and then
  sent TERM to each descendant it had found. A CLI that installs a TERM/INT/HUP trap runs that trap *when the signal
  arrives*, which is after the map pass and before the tool's signal is delivered to the descendants: the trap's
  child is forked after the read, so it was never in the map, and a `setsid` in the trap also takes it out of
  `timeout`'s process group, so the group TERM and the group KILL fallback cannot reach it either. The frozen
  `latefork` stub (census/round-84/c2-late-fork-counter.py, `STUBS["latefork"]`) is exactly this shape: it traps
  TERM/INT/HUP, starts a `setsid`'d `sleep 600` on the first signal, and then busy-loops on the `:` builtin — a
  foreground `sleep` would defer the trap past the tool's 0.1 s KILL sweep and the row would measure the stub
  instead of the tool (`plans/round-84.md` A0.1). The two frozen rows `l1-late-setsid-pid` (default launch) and
  `l2-late-setsid-group` (job-control launch) carry it. On the r83 tool bytes the two rows are red with **one
  survivor each** and the run reports `SUMMARY rows=22 mismatches=2 errors=0 orphans=2`, EXIT 1
  (census/round-84/controls/c2-before-r83-tool.txt, tool sha256
  `72a405f2c634712fb0211afb79f0462bf052b0b7c5fb8b663988017d2f1a8a18`).
- **Why one pass cannot see it.** The map pass is a snapshot of a moment; a descendant that appears after the pass
  is not in it. `timeout` puts the command in its own process group (S326), and a `setsid` in the trap puts the
  new child outside that group, so neither the per-descendant map nor the group kill covers it. No amount of
  re-reading the *same* map helps: the child was never in it.
- **The repair: freeze the tree, then re-walk, then KILL.** `cli_kill_tree` now runs **two** fork-free map passes
  over `/proc/<pid>/stat` and, on each pass, SIGSTOPs every descendant it discovers *before any trappable signal
  reaches it* — a stopped process can neither run a signal trap nor fork, so the trap never fires and the late child
  is never created. The second pass covers the read→STOP window: a descendant forked in that window has a
  still-running (and now stopped) parent, so it is still a child of the frozen tree when the second map is read.
  The frozen set is then SIGKILLed, with the starttime re-read immediately before each KILL so a recycled pid is
  not signalled. The r83 shape is kept otherwise: one fork-free pass per iteration (bash builtins only — no
  `pgrep`/`ps`/`cat` per node), the whole-file stat read with the last-`)` strip (S332: comm is emitted unescaped
  and may hold spaces, parentheses or a newline), the field-count guard, the root pid never signalled, and the
  caller's group-kill fallback.
- **Measured (the frozen 22-row population).** `census/round-84/c2-population.tsv` is the r83 20-row population
  unchanged, same order, plus the two late-fork rows; the counter is
  `census/round-84/c2-late-fork-counter.py`. On the reference implementation the run reads
  `SUMMARY rows=22 mismatches=0 errors=0 orphans=0` with **both late rows at `survivors=0 tmpleft=0`** — `l1` at
  1.0 s, `l2` at 0.9 s, inside the frozen 5 s settle — against 1 survivor each for the r83 bytes
  (census/round-84/records/c2-reference-prefreeze.txt). The executor's candidate reproduces it: the executor's own
  receipt reads `rows=22 mismatches=0 errors=0 orphans=0` with both late rows `survivors=0 tmpleft=0` (`l1` 1.4 s,
  `l2` 3.1 s — `.ufo/waves/round-84/w1/S84ExecC2/c2-after-receipt.txt`), and my independent re-run of the same
  bytes reads the same summary with `l1` 0.9 s and `l2` 0.8 s
  (`.ufo/waves/round-84/w1/S84Scribe/receipts/c2-exec-candidate-receipt.txt`).
- **A re-walk must not be a re-read of a dead map.** The second pass is a *new* map, not a re-read of the first
  one, and the identity re-read before each signal is guarded on the *content* of the stat file, not on the exit
  status of the read that fetched it. `IFS= read -r -d ''` returns a non-zero status at EOF (no NUL delimiter
  terminates a stat file) even though it read the whole file — the bash manual's `read` node: "The exit status is
  zero, unless end-of-file is encountered" (`/usr/share/info/bash.info.gz` sha256
  `cde1a3366897684b0a86fe553687e31d070b7839b19ca98186ffc6e0e105588f`, the capture S325 and S329 already cite) —
  so a guard of the form `{ IFS= read -r -d '' now < "/proc/$k/stat"; } 2>/dev/null || continue` skips **every**
  descendant: the read never fails, but it always reports failure. The correct guard keeps the content test
  separate (`|| true` plus `[ -n "$now" ] || continue`). This is not hypothetical — the reference bytes at
  `.ufo/waves/round-84/w1/RefC2/souji-vault-verify.sh` (sha256
  `a810acaf438cd6deee83a98f0db5b9697a5b5029f3126c207929c391f1130b25`) carry exactly that guard, and measured
  through the frozen counter they read `SUMMARY rows=22 mismatches=5 errors=0 orphans=5`, EXIT 1: the two late rows
  **and** the two job-control fork rows and the 24-descendant job-control row go red, because the freeze never
  reaches a descendant at all
  (`.ufo/waves/round-84/w1/S84Scribe/receipts/c2-refc2-current-bytes-FAILING.txt`; the minimal reproducer is
  `.ufo/waves/round-84/w1/S84Scribe/receipts/repro-read-d-status.sh`). The same bytes with the guard corrected
  read `rows=22 mismatches=0 errors=0 orphans=0`
  (`.ufo/waves/round-84/w1/S84Scribe/receipts/c2-fix-candidate.txt`).
- **The other half of the same guard: a newline in `comm` still truncates a first-line read.** The r83 spot-check
  routed defect D5 — "read each stat whole" was true of the map pass only, while the signal re-reads read the
  first line (`corpus/lessons/round-83-verifier-spotcheck.md` D5). A first-line read of a stat file whose `comm`
  carries a newline yields a truncated line with no closing `)`, so the last-`)` strip finds nothing and the field
  count collapses. Measured on this host: a process whose `comm` is `x\ny` (set with `prctl(PR_SET_NAME)`) has a
  first line of 10 bytes with no `)`, and after the strip the field count is **2** where the guard wants 20; the
  whole-file read of the same file yields **50** fields. So the repair of D5 has to be the **whole-file read with a
  content guard** — first-line reads silently skip a hostile-CLI descendant (r83 spot-check §2 measured that such a
  descendant is still reached by the group kill, which is why no frozen row fails today), and a whole-file read
  guarded on the *status* skips every descendant. The two error modes are opposite, and only the second one
  disables the freeze. The whole-file read's exit status is **1 on every pid**, normal or not, so the guard cannot
  be the status.
- **Stated limits (frozen wording; they are not claimed away).**
  - A child forked **after the second pass** is not seen: the freeze covers the tree as of the second map, and
    nothing re-walks after the KILL sweep.
  - `/proc` is **not an atomic snapshot**. A descendant forked in the read→STOP window of its own parent survives
    pass 1 and is caught by pass 2 only while it is still a child of the frozen tree — a child whose parent died in
    that window does not qualify.
  - **pidfd is not used** (the tool is bash); identity is the stat starttime re-read, so the STOP→KILL pair widens
    the pid-reuse window the r83 tool already disclosed.
  - A child that **reparents before the second map** is no longer a descendant of the frozen tree and is missed.
  - A descendant that left the tree before the walk (a `setsid` before the signal) is a root of its own and is not
    found at all, before or after.
  - The `latefork` stub forks on the **first** signal only, so a CLI that forks on every signal is not a row.
  - The deep stub remains a flat fan-out, and a stopped process holds its locks and files until the KILL sweep,
    which is microseconds later.

## Grounding map for the L1

| draft sentence | grounded in |
|---|---|
| latefork stub bytes, trap, `setsid sleep 600`, busy-loop on `:` | `census/round-84/c2-late-fork-counter.py` `STUBS["latefork"]`; `plans/round-84.md` A0.1 |
| l1/l2 ids, launches, columns | `census/round-84/c2-population.tsv` |
| r83 bytes red on l1/l2, 1 survivor each, `rows=22 mismatches=2 errors=0 orphans=2`, EXIT 1 | `census/round-84/controls/c2-before-r83-tool.txt` |
| r83 tool sha256 `72a405f2…` | `census/round-84/controls/c2-before-r83-tool.txt` header line |
| freeze-then-KILL repair, two passes, starttime re-read | `census/round-84/preregistration.txt` C2 stated wording; `.ufo/waves/round-84/w1/S84ExecC2/cli_kill_tree.diff` |
| reference run `rows=22 0/0/0`, l1 1.0 s / l2 0.9 s, survivors 0 | `census/round-84/records/c2-reference-prefreeze.txt` |
| executor run `rows=22 0/0/0`, l1 0.9 s / l2 0.8 s | `.ufo/waves/round-84/w1/S84ExecC2/c2-after-receipt.txt` |
| `read -d ''` returns non-zero at EOF; the guard skips every descendant | `.ufo/waves/round-84/w1/S84Scribe/receipts/repro-read-d-status.sh` + `.out`; `c2-refc2-current-bytes-FAILING.txt` |
| corrected guard restores `rows=22 0/0/0` | `.ufo/waves/round-84/w1/S84Scribe/receipts/c2-fix-candidate.txt` |
| frozen limits (child after the second pass, non-atomic `/proc`, no pidfd, reparent before the second map) | `census/round-84/preregistration.txt` C2 "Stated limits (frozen)" |

### Open point for the L1 (not a draft sentence)

The `verified-at:` line is a placeholder: it must name the commit at which the L1 lands the tool, and the `recheck:`
line must be re-run on those bytes. The executor's candidate (`sha256 a33038e9099e31052a16201d3e23b84b0b228558ab10188679f60efde6c26b15`)
and the reference bytes (`a810acaf…`) are **different** files; the L1 should land one and cite that one's digest.
