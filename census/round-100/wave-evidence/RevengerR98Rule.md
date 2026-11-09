# RevengerR98Rule — r98 rule reverse-engineering (souji round 100, wave w1)

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin — base a662bb0d7e033cc5ceccd70b52eb234404300845
Seat scratch: /fast/scratch/hyaku/souji-r100/RevengerR98Rule/ (deleted before yield; copies retained under wave dir)
Wave dir: .ufo/waves/round-100/w1/RevengerR98Rule/
Method: reconstructed from committed bytes (git show at base) + committed receipts. No live kill run by this seat.

## Commands run (with exit codes)

- `git rev-parse --show-toplevel` → `/home/vgpnk/Projects/shokunin/souji-shokunin` (exit 0)
- `git rev-parse --verify a662bb0d…^{commit}` → `a662bb0d…` (exit 0); `git log --oneline -3` top = `a662bb0d round-99 verifier spot-check…`
- `git show a662bb0d…:census/round-98/c2-setup-arms.py | sha256sum` → `0886271b…` == worktree `sha256sum census/round-98/c2-setup-arms.py` (exit 0) — committed bytes = worktree
- `git show a662bb0d…:census/round-99/c2-setup-arms.py | sha256sum` → `03e8a99e…` == worktree `census/round-99/c2-setup-arms.py` (exit 0)
- `git show a662bb0d…:census/round-97/c2-setup-arms.py | sha256sum` → `da30593c…` == worktree `census/round-97/c2-setup-arms.py` (exit 0)
- `diff -u` r98→r99 (exit 1 = differences present), 64 lines; full diff: `.ufo/waves/round-100/w1/RevengerR98Rule/diff-r98-r99.txt` (reproducer). Committed copies: `r98-committed.py`, `r99-committed.py`, `r97-committed.py` in same dir.
- Receipt reads via `cat` of committed records (exit 0 each): see §b–§d paths.

## Reconstructed contracts (committed bytes)

- r97 `_reap_by_identity` (census/round-97/c2-setup-arms.py:117-145): argv-ONLY kill — any own-uid pid whose argv contains the token byte-exactly is SIGKILLed if `starttime` re-read is non-None (no ownership, no spawn record at all).
- r98 `_reap_owned` (census/round-98/c2-setup-arms.py:164-203): three ownership branches under `spawn is not None`: (a) `pid == spawn_pid` with `st[1] == spawn_st` (starttime-verified, lines 184-186); (b) `_is_descendant(pid, spawn_pid)` ppid-chain walk (lines 187-188); (c) `_is_descendant(pid, os.getpid())` counter-child/subreaper branch (lines 189-191) — "orphaned into the counter (subreaper net): a counter child not under another arm is owned". `spawn is None` → never kill on argv alone (lines 194-197).
- r99 `_reap_owned` (census/round-99/c2-setup-arms.py:164-200): branch (c) REMOVED. Only (a) spawn-pid/starttime + (b) spawn-chain descendant (lines 184-190); else `continue`, never killed.

## Answers

### (a) Byte diff r98 → r99 for `_reap_owned` (file:line both ends)

Only one functional deletion + docstring/comment rewrites; no other `_reap_owned` logic changed.

- Docstring: census/round-98/c2-setup-arms.py:165-168 → census/round-99/c2-setup-arms.py:165-168. r98 "(a) spawn pid … or (b) a descendant of it" → r99 "the recorded spawn pid itself … or a ppid-chain descendant of that spawn pid … a counter-descendant carrier that is not a spawn-chain member is NEVER killed (r98 branch (c) removed)".
- DELETION (the byte diff): r98 lines 189-191
  ```
  elif _is_descendant(pid, os.getpid()):
      # orphaned into the counter (subreaper net): a counter child not under another arm is owned
      pass
  ```
  → absent in r99; r99 line 188 is `pass  # fresh starttime…`, line 189 is `else:`, line 190 `continue`. Neighbouring branches (a) r98:184-186 == r99:184-186 and (b) r98:187-188 == r99:187-188 are byte-identical.
- Companion T1 call-site comments (not `_reap_owned` itself, same diff hunk): r98:354-362 + 371-374 → r99:351-359 + 368-370 — survivors counting narrowed to spawn-chain only, subreaper/counter branch dropped.

Reproducer: `.ufo/waves/round-100/w1/RevengerR98Rule/diff-r98-r99.txt` (plus `r98-committed.py` / `r99-committed.py` for line inspection).

### (b) Foreign-decoy behaviour r98 → r99: NO CHANGE (spared → spared)

- r98: `census/round-98/records/decoy-r98-final.txt` → `DECOY-SUMMARY verdict=spared`, `DECOY-PLANTED n=83 dead=0 alive=83`, `EXIT=0`; corroborated `census/round-99/records/c2-decoy-r98.txt` → `verdict=spared`, `n=83 dead=0 alive=83`, `DECOY-EXIT=0`.
- r99: `census/round-99/records/c2-decoy-r99.txt` → `DECOY-SUMMARY verdict=spared`, `n=83 dead=0 alive=83`, `DECOY-EXIT=0`.
- Why branch-(c) removal cannot flip this: r98 branch (c) requires `_is_descendant(pid, os.getpid())` — the foreign decoy is driven by a separate driver process, never a counter child, so neither r98 nor r99 reaches it. The decoy test's `dead=82` for CM8 vs `dead=0` for r98/r99 confirms the foreign-pid exclusion held in both.

### (c) Escapee behaviour r98 → r99: REAPED → LEAKED (alive=0 → alive=1)

- r99 leaked: `census/round-99/records/c2-escapee-r99.txt` line 1+3 → `pid=3122349 stat=S ppid=1525`, `ESCAPEE-ALIVE run=r99 alive=1 token=…/r99-work/arms/fixture-pipe-holder.py`.
- r98 reaped: same file line 4 → `ESCAPEE-ALIVE run=r98 alive=0 token=…/r98-work/arms/fixture-pipe-holder.py`. The T1 setsid escapee orphans when the fixture parent exits; under r98 branch (c) it reparents to the counter (PR_SET_CHILD_SUBREAPER net, r98:206-221) and `_is_descendant(escapee, os.getpid())` holds → killed. Under r99, with branch (c) gone, the escapee's ppid chain no longer reaches the spawn pid (fixture parent is dead) and it is never killed (r99:189-190 `continue`); the survivors scan (r99:368-370) does not count it either — but the post-exit live count in c2-escapee-r99.txt proves it lived. NOTE: the `ESCAPEE-ALIVE … alive=0` lines appended inside `census/round-99/records/c2-counter-r*.txt` are VOID per `census/round-99/records/c2-escapee-NOTE.txt` (doubled `arms/arms/` token bug in the first measure.sh build); c2-escapee-r99.txt is the valid measurement.

### (d) Could any seat produce decoy verdict=spared under the r97 argv-only rule? NO.

r97 `_reap_by_identity` (census/round-97/c2-setup-arms.py:117-145) kills every token carrier with a readable starttime — foreign decoys included; it has no spawn record, no ppid walk, no counter check. Committed r97 decoy receipts show the kill: `census/round-98/records/decoy-r97-final.txt` → `DECOY-PLANTED n=83 dead=60 alive=23`, `DECOY-SUMMARY verdict=killed`, `EXIT=1`; identical in `census/round-99/records/c2-decoy-r97.txt` (`verdict=killed`, `DECOY-EXIT=1`). The CM8 argv-only mutant behaves the same (`census/round-99/records/c2-decoy-cm8.txt` → `dead=82 alive=1`, `verdict=killed`). verdict=spared requires at least one ownership gate (r98 branches, r99 branches) — pure argv identity cannot spare a token carrier. No seat in this wave can change that: the rule is the committed counter bytes, frozen; seats only write receipts under their own wave dir.

## Findings (each with reproducer)

- F1 (CONFIRMED, the routed defect): r99's removal of branch (c) is exactly the T1 escapee leak — alive=0 (r98, c2-escapee-r99.txt:4) → alive=1 (r99, c2-escapee-r99.txt:3). Reproducer: `.ufo/waves/round-100/w1/RevengerR98Rule/diff-r98-r99.txt` + receipts above.
- F2 (CONFIRMED): foreign-decoy outcome unchanged r98→r99 (spared/spared, dead=0 both) — the r99 narrowing did not move the decoy axis. Receipts §b.
- F3 (CONFIRMED): r97/CM8 argv-only kills foreign decoys (killed/killed, dead=60/82) — no spared verdict possible without an ownership gate. Receipts §d.
- F4 (OBSERVED, for L1): the only r99-observed escapee (pid 3122349, ppid 1525 at measure time) proves the escapee outlived the counter's ppid-chain window — consistent with r100 C1 needing field-6 session ownership (S075/S368), since ppid-chain alone cannot reach an orphaned setsid process. [INFERENCE width: counter exited before measure; init reparenting is the standard mechanism, consistent with ppid=1525 ≠ any counter.]

## Tooling

No installs. Read /home/vgpnk/.omp/agent/RULES.md; pacman paused host-wide per spec — no install attempted.

Report: .ufo/waves/round-100/w1/RevengerR98Rule.md
