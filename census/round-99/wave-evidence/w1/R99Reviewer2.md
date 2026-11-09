# R99Reviewer2 — C2 spawn-chain reap review

Seat: R99Reviewer2 (godspeed). Lane: souji @ c94d678c8a76f3f87f73b49a11a9d4e2aff73e3b.
Scratch: /fast/scratch/hyaku/souji-r99/R99Reviewer2/ (deleted before yield).
Axes: (1) wrong-target signalling — TOCTOU / pid-reuse / stale chain snapshots between certification and `os.kill`; (2) coverage vs exclusion — does the narrowed rule still reach the T1 setsid escapee it was built to reap?
Frontier: keep moves that improve any axis and harm none. No edits outside owned wave paths. No `model` override. No installs. No sysctl mutation.
Tooling: python3 system only. `read`/`edit`/`write` none needed beyond report; `bash` for hashing/grep/`py_compile`/reproducers. No packages installed or updated.

## Diff under review

Commands run (cwd `/home/vgpnk/Projects/shokunin/souji-shokunin`):
- `sha256sum census/round-99/c2-setup-arms.py census/round-98/c2-setup-arms.py` → r99 `03e8a99e2e447e4c5e7067dea191450c7d5ec10102cb33e2a246b5b3d1c02b57`, r98 `0886271b4836915bdf849eeac3c1d6b341603900043fdcf061bcbd038b8af67f`. EXIT 0.
- `diff -u census/round-98/c2-setup-arms.py census/round-99/c2-setup-arms.py` → EXIT 1 with exactly two hunks:
  1. `_reap_owned` docstring rewritten from r98 "(a) spawn pid (re-verified by starttime), or (b) descendant …, or (c) orphan reparented to the counter" to r99 "ONLY the recorded spawn pid itself (re-verified by starttime) or a ppid-chain descendant of that spawn pid. … a counter-descendant carrier that is not a spawn-chain member is NEVER killed (r98 branch (c) removed)." Body: branch (c) `elif _is_descendant(pid, os.getpid()): pass` deleted. No other body change in `_reap_owned`.
  2. T1 comment/survivors block rewritten: survivors now counts only spawn-chain members (`pid != spawn[0] and not _is_descendant(pid, spawn[0])` → continue); the subreaper comment on the escapee replaced by an open-limit note.
- `wc -l census/round-99/c2-setup-arms.py census/round-98/c2-setup-arms.py` → 399 vs 403. (Note: r99 file still carries the stale module docstring header — see Finding F4.)
- `grep -n "_is_descendant" census/round-99/c2-setup-arms.py` → def at 127, reap branch 187, survivors 374. No counter-branch remains. EXIT 0.
- `grep -n "os\.kill\|killpg\|_survivors" census/round-99/c2-setup-arms.py` → exactly two signal sites: `os.kill(pid, SIGKILL)` at line 196 inside `_reap_owned`, and `os.killpg(p.pid, SIGKILL)` at line 341 in `one()` on `TimeoutExpired`. `_survivors` at 139 is dead code (no callers). EXIT 0.
- `python3 -B -m py_compile census/round-99/c2-setup-arms.py` → `PY_COMPILE_OK rc=0`. `c2-setup-arms.py --help` → usage printed, rc 0.
- Field-mapping sanity: import module, `_proc_stat(os.getpid())` returns `(ppid, starttime)` with `ppid == os.getppid()` and `starttime == int(stat.split()[19])` → `ppid-match: True starttime-match: True`, EXIT 0. `/proc/sys/kernel/pid_max` → `4194304`. The S075 parse (`fields[1]`, `fields[19]`) is correct.

## Claim C2 wording (`.ufo/waves/round-99/claims.json`, frozen)

> "operability 8. The arms counter's T1 reap kills only the recorded spawn pid and its ppid-chain descendants (starttime verified); a counter-descendant carrier outside the spawn chain is not signalled (branch (c) removed). The committed decoy test shows the foreign decoy spared under the r99 counter and killed under the r97 counter; the cross-arm probe shows a counter-descendant carrier spared under r99 and killed under r98."

## Findings

### F1 (MEDIUM) — Descendant branch kills on a stale chain snapshot with no act-time identity re-read; pid-reuse can signal a non-member

**Location.** `census/round-99/c2-setup-arms.py`, `_reap_owned` lines 179-199:

```python
        st = _proc_stat(pid)          # ONE read of candidate (ppid, starttime) at L179
        ...
        if spawn is not None:
            spawn_pid, spawn_st = spawn
            if pid == spawn_pid:
                if st[1] != spawn_st:  # spawn branch: identity re-checked
                    continue
            elif _is_descendant(pid, spawn_pid):   # L187: chain walk, OTHER processes' /proc reads
                pass  # fresh starttime re-read above; chain walked at act time
            else:
                continue
        ...
            os.kill(pid, signal.SIGKILL)   # L196: numeric pid, no pidfd, no fresh re-read
```

Three coupled defects:

1. **No identity binding for the descendant case.** The spawn branch re-verifies `st[1]` against the recorded `spawn_st`. The descendant branch records NOTHING about the candidate at spawn time (it cannot — the escapee does not exist yet), and the single `st` read at L179 is discarded: `pass` uses neither `st[0]` nor `st[1]`. The comment "fresh starttime re-read above" describes a read that authorizes nothing — `st[1]` is never compared to anything. Claim wording "(starttime verified)" is therefore false for every non-spawn victim: the ONLY starttime verification in the function is the spawn-pid equality check. The fresh read is decorative.
2. **Chain walk and kill are not atomic.** `_is_descendant` walks `cur = _proc_ppid(cur)` repeatedly (each an independent `open(/proc/<pid>/stat)`). Between the successful walk and `os.kill`, the certified process can exit and the pid be recycled. `os.kill` takes a bare numeric pid with no pidfd/close-on-exec identity handle. The kernel will deliver SIGKILL to whatever process holds that pid at kill time, including a freshly spawned innocent process with matching argv-token. `pid_max` is 4,194,304 here, so spontaneous recycling is RARE in this deployment, but the window is real and the code does nothing to close it. The spawn branch is protected (pid reuse changes starttime, detected at L179-read time — though even there a reuse between L179-read and L196-kill is unprotected); the descendant branch — the branch that does all the real work against the escapee — is not.
3. **Reproducer (live, observed).** `repro_live_toctou.py`: plant a token-carrying sleeper not in any spawn chain, monkeypatch `_is_descendant` to `True` (modelling a chain walk that certified the pid just before the victim died and the number was recycled), call `_reap_owned(token, exclude, (999999, 0))`. Observed: `_reap_owned killed=1 child.returncode=-9`, `final poll=-9`, EXIT 0. I.e., with the certification stale, the function signals an innocent non-member. Structure proof `repro_pidreuse_toctou.py`: AST counts `_reap_owned: os.kill calls=1, _proc_stat reads=1, _is_descendant calls=1`, EXIT 0. On real pid reuse the kernel side would be identical; `pid_max = 4194304` makes the organic trigger unlikely, which is why this is MEDIUM not HIGH — but "starttime verified" and "kills ONLY … descendants" overstate the guarantee.

**Fix that would close it** (for L1/planner, not applied): re-read the victim's starttime immediately before kill and compare to the value observed when the chain certified it (store `st` from the chain-walk read, re-read, `continue` on mismatch — narrows but does not eliminate the window); or better, `pidfd_open(pid)` + `pidfd_getfd`-style identity pin, or `pidfd_send_signal` after `pidfd_open` + starttime check via the fd. The L1 owns the predicate freeze; this is a finding, not a patch.

### F2 (HIGH) — The narrowed rule cannot reach the T1 escapee it exists to reap (under-kill); the claim sentence "kills only … descendants" hides the converse failure

**Location.** `_reap_owned` r99 (branch (c) deleted) + `one()` T1 arm.

The T1 fixture (`PIPHOLDER`): the fixture forks a child, the child `os.setsid()`s and sleeps 3600 s, the fixture exits 0. The probe (spawn pid) raises that fixture as a subprocess. When the fixture exits, the setsid grandchild is orphaned; with `PR_SET_CHILD_SUBREAPER(1)` set by `_set_child_subreaper()`, it reparents to the **counter** (pid `os.getpid()`), not to the probe, not to init. Its ppid chain is therefore `counter → …`, never reaching the spawn pid. `_is_descendant(escapee, spawn_pid)` is false by construction AFTER the fixture parent exits. Under the r99 rule the escapee is deliberately not killed — Executor C2's spec acknowledges this as an "open limit … it is then NOT killed". The survivors loop at lines 362-376 only counts spawn-chain members, so the orphaned escapee is also invisible to `survivors`. The conform gate at line 390 (`survivors == 0`) can now pass vacuously: nothing spawn-chain remains because the escapee was never spawn-chain after reparenting.

**Reproducer.** `repro_escapee.py`: model the counter's spawn (probe process running the pipe-holder fixture), observe ppid of the setsid fork: initially orphaned to the harness/counter (`ppid = harness pid`, `is_desc_of_spawn=False`), token carrier present, `_reap_owned would kill? … branch spare`. Observed lines: `pid=3807107 ppid=3806972 … is_desc_spawn=False`, `token carrier pid=3807107 ppid=3806972 starttime=7369974 is_desc_spawn=False`, `_reap_owned would kill? argv-match=yes spawn-descendant=False -> branch spare`, EXIT 0. The same structure holds inside the real counter (escapee reparents to counter via subreaper, probe already gone or still blocked on pipe EOF).

**Consequence for the claim.** The claim says the reap "kills only the recorded spawn pid and its ppid-chain descendants". That sentence is, strictly, what the code does — but the round-99 C2 story is that the counter REAPS the T1 escapee by ownership. Under the narrowed rule it does not, and `ARM T1 … survivors=0` no longer evidences "the escapee was reaped" (the spot-check's routed defect 4 already warned: keep decoy predicate, not survivors, as the C2 witness). If the L1 freezes this rule, the T1 escapee leaks as a 3600-s orphan on every run, and any locus checking "the counter reaped the escapee" (conform includes `survivors==0` and `line==yes`) goes green vacuously. The claim as frozen does not name this under-kill; the falsified sentence is the implicit converse ("the T1 escapee is reaped by the spawn-chain rule") together with the `(starttime verified)` parenthetical (F1). L1 must either freeze the narrow rule AND amend the C2 sentence to concede the escapee is not reaped (open limit, timed orphan), or restore a starttime-pinned subreaper path. Do NOT ship both "branch (c) removed" and "T1 escapee reaped" as if they were the same claim.

### F3 (LOW) — `os.killpg(p.pid)` on the hung arm is an unscoped group signal outside the spawn-chain rule

**Location.** `one()` line 341: on `TimeoutExpired`, `os.killpg(p.pid, SIGKILL)`. The spawn was created with `start_new_session=True`, so `p.pid` is a session and process-group leader. `killpg` signals the ENTIRE group: every process that currently has PGID == spawn pid, whether or not its ppid chain reaches the spawn pid (e.g., a peer that called `setpgid` into the probe's group, or a descendant that inherited the group but whose ppid chain no longer reaches the spawn pid after reparenting). The claim sentence "kills only the recorded spawn pid and its ppid-chain descendants" is literally false for this second signal site, which fires on every --arm-timeout hang (S12 and any hung probe). It is also the SAME pre-existing path as r98, not a regression — but the frozen r99 wording claims exclusivity, and this path widens the blast radius beyond the spawn-chain rule. Severity LOW because it only fires on a hung arm (scope-limited, operator-visible as `exit=hung`), and group members are almost always spawn descendants in practice. Name it or scope the claim sentence to "the T1 reap".

Reproducer: semantic inspection + `test_killpg_mechanics.py` (killpg = entire PGID; setsid child in a DIFFERENT pgid is NOT reached, same-pgid non-descendant IS reached). Observed: `killpg semantics: SIGKILL to entire PGID == p.pid; blast radius = sessoin leader group`, EXIT 0. No end-to-end organic hang reproduction attempted (would need a 300 s arm timeout; S12 arms exercise it in the real 20-arm run — L1's measurement covers it).

### F4 (LOW — hygiene) — Stale r98 wording left in the r99 module: header docstring and arm comments describe the deleted rule

**Location.** `census/round-99/c2-setup-arms.py`:
- Lines 2, 4-11: module docstring still opens "souji r98 C2 counter" and describes the three-branch rule including "(c) an orphan reparented to the counter itself". A reader (or a future text-search audit) will conclude branch (c) still exists.
- Line 330 comment still says "r98 ownership" and "with matching starttime" for descendants (F1 shows no such matching).
- Line 335 field: spawn recorded as `(p.pid, _proc_starttime(p.pid))` — if the probe exits instantly, `_proc_starttime` returns `None`; the spawn branch then `st[1] != None` always → spawn pid skipped (safe under-kill, not an over-kill). Worth a comment, not a defect.

Nothing here affects runtime. It does affect claim-to-code traceability. Recommend the L1 regenerate the module docstring at freeze time.

## Cross-arm sparing (the narrowed rule working as specified)

**Reproducer.** `repro_cross_arm.py`: fake spawn probe (`spawn=(3828065, 7370375)`), cross-arm carrier (child of the harness, ppid=3827951 i.e. harness/counter, argv carries token, `is_desc_spawn=False is_desc_counter=True argv_match=True`). Observed: `r99 _reap_owned killed=0 (probe excluded, carrier should be spared) carrier_rc=None probe_rc=None`, EXIT 0. The r99 rule does spare counter-descendant non-spawn carriers, as the claim requires. The corresponding positive control (r98 kills it) was not re-run here (branch (c) is present in `census/round-98/c2-setup-arms.py:189-191` by diff; L1's cross-arm probe owns the r98-kills leg — do not duplicate a 83-decoy-scale run per the r98 spot-check routing).

## Falsified / at-risk sentences in C2 wording

1. **"(starttime verified)"** — falsified for descendants (F1). Only the spawn pid's own starttime is verified; the descendant branch discards the fresh read. Sentence to strike or to qualify "for the spawn pid".
2. **"kills only the recorded spawn pid and its ppid-chain descendants"** — falsified as a global statement by the `killpg` site (F3). True as a statement about the T1 `_reap_owned` path only.
3. Implied **"the T1 escapee is reaped by this rule"** — falsified by construction (F2). The escapee is provably not spawn-chain reachable after fixture-parent exit under the subreaper net. If the frozen claim implies reaping, F2 bars it.

NOT falsified: "a counter-descendant carrier outside the spawn chain is not signalled (branch (c) removed)" — verified by `repro_cross_arm.py` (killed=0) and by the diff (branch deleted).

## Residual risk and verification gaps

- F1's organic pid-reuse trigger probability is low at `pid_max=4194304`, but the race window is exercised on EVERY T1 reap (argv scan → stat → chain walk → kill is four sequential /proc reads with no re-read). A `pidfd_open`+`pidfd_send_signal` scheme would close it structurally; the current code only narrows it for the spawn pid.
- F2's escapee leak is certain, not probabilistic, on every T1 run. The 20-arm measurement (L1's gate) will show `ARM T1 survivors=0` regardless; the decoy/cross-arm probes are the only witnesses that discriminate over- vs under-kill now.
- This seat did NOT run the full 20-arm counter (~minutes), the 83-decoy run, or the cross-arm probe end-to-end — those are R99ExecC2/R99ExecC2b/L1 measurement gates. Findings above are unit-level reproducers against the committed r99 bytes (`03e8a99e…`), static + live, each with observed output.
- The `spawn=(pid, None)` edge (probe exits before `_proc_starttime` reads) was reasoned, not observed live; it under-kills, not over-kills.

## Commands summary (observed outputs)

- `sha256sum … / diff -u …` → hashes above; diff two hunks (`_reap_owned` docstring + branch (c) deletion; T1 survivors comment). EXIT 0/1 as noted.
- `grep -n "_is_descendant|os.kill|killpg" census/round-99/c2-setup-arms.py` → 1× `os.kill` (L196), 1× `killpg` (L341), `_survivors` dead. EXIT 0.
- `python3 -B -m py_compile census/round-99/c2-setup-arms.py` → `PY_COMPILE_OK rc=0`.
- `repro_pidreuse_toctou.py` → `_reap_owned: os.kill calls=1, _proc_stat reads=1, _is_descendant calls=1`, EXIT 0.
- `repro_live_toctou.py` → `killed=1 child.returncode=-9`, EXIT 0 (innocent non-member signalled under stale certification).
- `repro_escapee.py` → `token carrier … is_desc_spawn=False … branch spare`, EXIT 0 (escapee unreachable under spawn-chain rule after parent exits).
- `repro_cross_arm.py` → `r99 _reap_owned killed=0 … carrier_rc=None`, EXIT 0 (cross-arm carrier spared, claim leg holds).
- `test_killpg_mechanics.py` → `killpg semantics … blast radius = … group`, EXIT 0.

Report: .ufo/waves/round-99/w1/R99Reviewer2.md
Lane bounds: leaf member — no subagent dispatch.
