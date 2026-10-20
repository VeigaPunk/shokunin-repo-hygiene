STATUS: DONE — claim wording falsified in four places; smallest honest rewording proposed.

# Attacked claim (C1 operability wording)

"no single repository can hang the fleet census, and no lane fixture leaves a
blocked process behind." Under the hood this rests on C1's shipped mechanism:
`run_repo_with_watchdog` in `tools/souji-census.sh` (5efb519).

All line numbers are `souji-shokunin/tools/souji-census.sh` at 5efb519 (tip),
verified `git diff b576341..HEAD` identical for the r14 fixture
(`sha256sum e6a984b1…14b2` matches `git show b576341:…` byte-for-byte — see
commands below).

## Finding 1 — list-phase and startup phases are NOT bounded; a hung mount on a repo hangs the whole census

The claim says "every repository (list-phase guards and census_one) runs in its
own process group." True for `guard_repo_candidate` / `census_one` — both go
through `run_repo_with_watchdog` (lines 1670-1671, 1699). FALSE for the list
phase itself:

- `list_repos` (lines 1386-1438) runs in the MAIN process, no watchdog:
  `[ -L "$d" ] || [ ! -d "$d" ]` (1418), `[ -L/-f/-d "$g" ]` (1421/1425/1429)
  where `g="$d/.git"`, plus the glob `"$root"/*` readdir (1408). If a child's
  `.git` directory sits on a dead NFS/FUSE mount, `stat` blocks in D state
  forever — the census never reaches the watchdog loop. One repository hangs
  the fleet census before the machinery under test even starts.
- `resolve_guarded` (446-520): `[ -L "$candidate" ]` and
  `readlink -- "$candidate"` (494-495) for every component of `--root`,
  `--compare`, each repo (via `guard_path` at 1306 — inside the watchdog, good)
  — BUT the root walk itself runs at `emit_census` line 1656 and inside
  `load_census` line 1735, both unguarded. The compare file's `[ -f ]`,
  `[ -r ]`, `stat`, and `read` (1740-1753) are likewise unbounded.
- `passwd_home` (308-315): `id -u` and `getent passwd` run unbounded at
  startup; an NSS module (LDAP/sss) that stalls hangs the census before any
  repo work.
- `mktemp`/`rm -rf` on `$CENSUS_TMP` (240, 1530/1644) — a hung /var/tmp
  blocks the whole run.

Smallest fix (wording): bound applies *per-repository after enumeration*, not
to enumeration/startup/compare. Or reword the claim (below).

## Finding 2 — D-state members are reported but LEFT BEHIND; "no blocked process behind" is only best-effort

`run_repo_with_watchdog` treats a D-state (or merely slow-to-die) group member
honestly: after TERM+KILL it polls `kill -0 -- "-$worker"` for ~3 s
(1571-1575, 1599-1603, 1633-1637) and emits
`souji-census: repo-timeout-unreaped <repo>` (1640-1642). The census row is
still `…\terror` and the run continues — the census itself is not hung. But
the unkillable child is reparented and left running. The tool correctly
does not promise more; the CLAIM wording does. "no single repository can hang
the fleet census" survives (main loop never calls a blocking `wait` on a
non-Z child — every `wait "$worker"` is gated on `dead=1`, e.g. 1520, 1563);
"no lane fixture leaves a blocked process behind" does not survive for the
tool path either — `repo-timeout-unreaped` is precisely the residue case, and
the B-fixture never exercises it (see Finding 4).

Also: `kill -0 -- "-$pgid"` returns EPERM for a group member owned by another
uid (line 1488/1492): treated identically to "group exists", so a foreign-uid
member is never killed and never reported — invisible residue, no
`unreaped` diagnostic.

## Finding 3 — setsid/setpgid escapees defeat group semantics entirely

The bound is group-scoped: `kill -TERM/-KILL -- "-$pgid"` (1495/1497) and
liveness `kill -0 -- "-$pgid"` only reach members still in the worker's
process group. Any descendant that calls `setsid` (or `setpgid` into another
group) is invisible to both the kill and the liveness check: the census row
for that repo will look clean once the in-group members die, while the
escapee runs on unboundedly — and no diagnostic names it. Today the tool
neutralizes repo-controlled exec vectors (hooksPath=/dev/null,
fsmonitor=false, no filters run — config `GIT_CONFIG_*` at 199-200), so no
in-fleet repo can currently spawn one; but the wording "runs in its own
process group" is about *containment of all descendants*, which the
mechanism cannot guarantee. Honest wording must scope the bound to
"descendants that remain in the worker's process group."

Adjacent race worth one line: a dead worker's PGID can be recycled by an
unrelated process inside the watchdog's ~1 s `kill -0` window; the watchdog
would then TERM/KILL a group that is not the repo's. Low probability,
unbounded consequence — the diagnostic `repo-timeout-unreaped` would fire on
an innocent group.

## Finding 4 — r14 fixture is byte-frozen at baseline with child-only timeout kill; the B-fixture doesn't cover D/escapee residue

- `tests/fixtures/r14-census-boundary.py:392-402` —
  `subprocess.run(…, timeout=90)`; on `TimeoutExpired` CPython kills only the
  direct child (strace). Killed strace DETACHES its tracees, which keep
  running: the census worker/watchdog subtree is orphaned, not killed. Any
  blocked child (D-state from Finding 2, or a stall under `--repo-timeout`)
  is left behind with no session reaper. r15 (lines 288-292: kill per-pid by
  session id, then `killpg`) and r17 (162-168) and r18
  (r18-census-bounded.py:442-583: `killpg` on `proc.pid` +
  session-member sweep) were patched to kill the whole session; r14 cannot
  be patched because `tools/souji-preservation-evidence.py` pins its digest
  — confirmed byte-identical to b576341. So "no lane fixture leaves a
  blocked process behind" is false for r14 as shipped: on the 90 s timeout
  it abandons the census subtree. Narrow but real: r14 runs the tool under
  strace at default `--repo-timeout 600`, so a genuine stall gets killed at
  90 s leaving the strace-attached subtree alive until the tool's own
  watchdog fires — bounded residue window, but residue nonetheless, and
  D-state residue is unbounded.
- `tests/fixtures/r18-census-bounded.py` B1-B8 exercise FIFO-blocking git
  shims (lines 244-315: shim opens a FIFO read end, `os.mkfifo`, `time.sleep`
  delay) — all simulated stalls are SIGKILL-able children in the worker's
  group. There is no B-case for a group member that ignores SIGKILL
  (D-state), a `setsid` escapee, or the unguarded list-phase stat; residue
  verification (`clean_fifo_problems` 699-729 + `case_resources`) can only
  see in-group leftovers. The fixture proves the mechanism works on the
  killable case it was designed for; it does not prove "no blocked process
  behind."

## Finding 5 — scaling: bound is per-repo, sequential, doubled

Repos are serialized: guard pass then census pass (1665-1688, 1691-1718), each
independently bounded by `--repo-timeout` (default 600) plus ~8-11 s of
TERM-grace/reap/wait margins. Worst case ≈ 2·N·(T + ~10 s): a fleet of 30
repos can consume ~10 h of wall clock while "hanging" nothing. There is no
fleet-wide budget. "No single repository can hang the census" is accurate;
"the census completes in bounded time" would not be.

## Commands run (outputs verbatim)

```
$ git -C souji-shokunin diff --stat b576341..HEAD -- tests/fixtures/r14-census-boundary.py
(empty)
$ git show b576341:tests/fixtures/r14-census-boundary.py | sha256sum
e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2  -
$ sha256sum tests/fixtures/r14-census-boundary.py
e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2  tests/fixtures/r14-census-boundary.py
```

Fixture kill semantics (grep):

```
r14-census-boundary.py:392  subprocess.run(command, …, timeout=90)     # child-only kill
r15-census-config.py:288    os.kill(pid, signal.SIGKILL)               # per-pid session sweep
r15-census-config.py:292    os.killpg(session_id, signal.SIGKILL)
r15-census-config.py:304    Popen(command, start_new_session=True)
r17-census-hygiene.py:162   os.kill(int(entry.name), signal.SIGKILL)   # /proc sid sweep
r17-census-hygiene.py:168   os.killpg(session, signal.SIGKILL)
r17-census-hygiene.py:190   start_new_session=True
r18-census-bounded.py:458/468/546/583  os.killpg(…, SIGKILL); start_new_session=True (516)
census/round-18/run-matrix.py:87-140  kill_session(): /proc sid sweep + killpg
```

## Verdict

Partial / fails as worded. The shipped mechanism is a genuinely good per-repo
watchdog — the strongest counterexamples are outside its declared perimeter:
(1) unbounded pre-watchdog phases (list_repos stats, root/compare resolution,
NSS lookups), (2) group-scope assumptions (setsid escapees, foreign-uid
members, PGID reuse), (3) residue reporting ≠ residue absence (unreaped
D-state children are left behind by design), (4) the frozen r14 fixture's
child-only timeout kill, (5) no fleet-wide time bound.

## Exact honest wording (proposed replacement)

"Every per-repository operation after enumeration — the list-phase metadata
guards and the census measurement — runs in a private process group bounded
by `--repo-timeout` (default 600 s). A repository that exceeds the bound gets
an `error` row, its in-group descendants receive TERM then KILL, and the
census continues and still exits 0. Enumeration, option/compare resolution,
and NSS startup lookups run unguarded in the main process; a filesystem that
hangs stat/readlink there can still stall the whole run, as can a descendant
that escapes the worker's process group (setsid/setpgid) or a group member
owned by another uid. A group member that survives SIGKILL (e.g. D-state) is
reported as `repo-timeout-unreaped` and left reparented — reported residue,
not reclaimed residue. Total time is bounded by roughly 2·N·(timeout +
~10 s); there is no fleet-wide budget. Fixtures r15/r17/r18 reap their whole
session on timeout; r14-census-boundary.py is byte-frozen by the
preservation-evidence digest and kills only its direct child, so a blocked
census subtree can outlive a fixture timeout until the tool's own watchdog
or the kernel clears it."

Tool installs this session: none.
