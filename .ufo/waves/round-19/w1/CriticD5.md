STATUS: DONE — D5 is an admissible bounded operability improvement, not proof that PID recycling is impossible.

# Findings

- The repair adds a useful per-PID guard: both fixtures snapshot session members with their `starttime`, reread the pair immediately before `os.kill(pid, SIGKILL)`, and skip a mismatch (`tests/fixtures/r15-census-config.py:287-307`; `tests/fixtures/r17-census-hygiene.py:169-189`). Their comments correctly say the window is narrowed, not closed (`r15-census-config.py:288-291`; `r17-census-hygiene.py:170-172`). This directly addresses the routed D5 defect (`corpus/lessons/round-18-verifier-spotcheck.md:149`; `.ufo/waves/round-19/preregistration.txt:66-70`).
- The exact field-22 contract is a boot-relative start time expressed in clock ticks: man7 says “The time the process started after system boot” and “Since Linux 2.6, the value is expressed in clock ticks” (https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html, accessed 2026-10-21, `DESCRIPTION`, field (22) `starttime`). That is a timestamp with tick granularity, not a documented unique generation identifier. [INFERENCE] Distinct process starts that map to the same tick can therefore compare equal after PID reuse; the man page gives no uniqueness guarantee that would disprove this counterexample.
- Even with distinct start times, the read/check and `os.kill(pid, ...)` are separate operations. If the checked process exits and the PID is reused between them, the later PID-based signal can address the replacement. Thus the recheck narrows the window, but cannot make the check-and-signal atomic.
- Both implementations also retain an unconditional `os.killpg(session_id, SIGKILL)` after the per-PID checks (`r15-census-config.py:309-312`; `r17-census-hygiene.py:191-194`). That group signal is not guarded by the per-member `(pid,starttime)` recheck; do not extend the per-PID claim to it. [INFERENCE] A stale/reused group ID is a separate residual risk if the original group has ceased to exist before this call.
- **Decision:** Admit the implementation as a bounded reduction of stale-PID risk for the individually signalled scan members. Do not label PID-recycle safety “closed” or claim that the tuple proves identity. The repair is not unprovable as an improvement: its guard and intended scope are visible in code; only an absolute safety guarantee is unproven.

# Evidence

- `tests/fixtures/r15-census-config.py:269-312` — parser returns session plus field-22 value; scan captures it, per-PID recheck precedes `os.kill`, then a separate process-group signal follows.
- `tests/fixtures/r17-census-hygiene.py:151-194` — same pattern, with its existing scan-failure handling and group signal.
- `census/round-18/run-matrix.py:107-139` — comparison design also rechecks `(session,starttime)` before per-PID signalling; it demonstrates the established pattern, not an atomic kernel identity guarantee.
- man7 `proc_pid_stat(5)`, URL and access date above, `DESCRIPTION`, field (22) `starttime` — authoritative granularity semantics.

# Commands run

None. Static source/documentation reads and search only; no fixture, test, census, or live-process probe was run.

# Contract compliance

Read-only review. No subagents, installs, signals, live `/proc` reads, or git/jj mutations. The only public URL opened was the assigned man7 `proc_pid_stat(5)` page. This report is the only file written.
