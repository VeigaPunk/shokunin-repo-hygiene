STATUS: DONE — historical timeout behavior and the recorded process-group rationale reconstructed

# Axis

**Operability.** Scope is fixture subprocess timeout handling in r14/r15/r17 and the contemporaneous lesson record, at `b576341`.

# Finding

The r14 and r15 fixture timeouts were introduced as ordinary `subprocess.run(..., timeout=...)` bounds. Their recorded history gives no descendant/process-group cleanup rationale and no `start_new_session`/`killpg` handling. The group-leak hazard is explicitly recognized in the r17 fixture from its first commit: a timed-out census can leave a Git child from `$(...)` blocked opening a writer-less FIFO, so `run_tool` starts a new session and kills the process group.

Thus, **the hazard was known by the r17 fixture author at `ddb7347`**. The r15 lesson does not record that hazard; the r17 lesson discusses a different FIFO hang in the census itself (a TOCTOU swap after the type stat), not fixture-child leakage. Round-18 context separately reports actual blocked processes from both r15 and r17 fixture runs. That makes the r17 mitigation an intent, not proof that no fixture child can remain: its reported `d2-fifo` residue still needs an explanation.

## Evidence chain

### r14/r15: direct-child timeout pattern

At current source, r14 `run_setup` has `timeout=60` at `tests/fixtures/r14-census-boundary.py:124-136` (timeout at :132); `probe_strace` has `timeout=20` at :322-358 (:350); and `run_tool` has `timeout=90` at :361-412 (:399). The timeout handler returns `Result(124, ...)`; none starts a new session or calls `killpg`.

The matching r15 functions have the same pattern: `run_setup` at `tests/fixtures/r15-census-config.py:268-288` (:281), `probe_strace` at :730-755 (:746), and `run_tool` at :757-807 (:788). In the r15 runner the timeout result is appended to `ACTIVE_RUNS`, but that bookkeeping does not terminate descendants.

History anchors (the `-L` result is the original addition; no later `-L` change introduces process-group handling):

- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log -L 124,136:tests/fixtures/r14-census-boundary.py b576341 --oneline` → `48f8945 round-14: bind retained evidence and fence census credential paths`; added `subprocess.run(..., timeout=60)`.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log -L 322,359:tests/fixtures/r14-census-boundary.py b576341 --oneline` → `48f8945`; added `subprocess.run(..., timeout=20)` for the `strace` probe.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log -L 361,412:tests/fixtures/r14-census-boundary.py b576341 --oneline` → `48f8945`; added `subprocess.run(..., timeout=90)` for `run_tool`.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log -L 274,288:tests/fixtures/r15-census-config.py b576341 --oneline` → `b410186 round-15: land operator-stopped config repair candidates; acceptance unrun`; added `subprocess.run(..., timeout=60)`.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log -L 730,755:tests/fixtures/r15-census-config.py b576341 --oneline` → `b410186`; added the `strace` probe's `timeout=20`.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log -L 757,807:tests/fixtures/r15-census-config.py b576341 --oneline` → `b410186`; added `run_tool` with `timeout=90` and a timeout-to-124 result.

### r17: explicit process-group mitigation, with a FIFO reproducer

`tests/fixtures/r17-census-hygiene.py:271-325` uses `Popen(..., start_new_session=True)`, waits via `communicate(timeout=timeout)`, and on timeout calls `os.killpg(proc.pid, signal.SIGKILL)`, then `communicate()` and `unblock_fifos()`. The decisive source comment at :301-303 says: “Process-group kill: `$(...)` would orphan a git blocked in `open()` on a writer-less FIFO otherwise.” Case R17-08 at :749-758 creates FIFO `.git/info/attributes`, provokes attribute consultation, and explicitly expects a 60-second process-group timeout (`rc 124`) if the census blocks.

History establishes that this was not a later retrospective edit:

- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log -L 271,326:tests/fixtures/r17-census-hygiene.py b576341 --oneline` → `4f48343` and `ddb7347`. The full initial addition at `ddb7347` already contains `start_new_session=True`, `killpg`, and the orphan comment; `4f48343` later adds `extra_env` to the runner while retaining the process-group strategy.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log -L 749,759:tests/fixtures/r17-census-hygiene.py b576341 --oneline` → `ddb7347`; R17-08's FIFO case and process-group-kill rationale were authored together.

Full hashes and subjects from `git show -s --format='%H %s' 48f8945 b410186 ddb7347 4f48343`:

- `48f8945780adeb259cff0ef7dd9b7efbf1544ec7` — r14 fixture addition.
- `b410186cea626a67c92396ac58fbd57fb86876ac` — r15 fixture addition.
- `ddb73474433977ff54b015ac3e77669ff2537353` — r17 fixture addition with group kill.
- `4f4834390ad4845b76804e94cc04d8f867ef9b54` — later r17 wave-2 fixture update.

### `-S` and lesson history: when the risk was recorded

The requested `start_new_session` pickaxe was run over both older fixtures, r17, and both lessons:

`git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -S'start_new_session' b576341 -- tests/fixtures/r14-census-boundary.py tests/fixtures/r15-census-config.py tests/fixtures/r17-census-hygiene.py corpus/lessons/round-15.md corpus/lessons/round-17.md`

Output:

```text
4f48343 round-17: wave-2 fixes — census empty/locale/dot-admin + both soft diagnostics, jj_keep_novel leaf-blob/SIGPIPE-safe/fail-closed, gate exit-2 totality + mutant killers, seat-audit survivors, fixtures R17-27..29 and J10..J12
ddb7347 round-17: C1 census D1/D2, C2 seat-audit precision + r16 transcripts bundle, C3 jj-aware receipt roots/novelty, D6 gate exact ids + replays, vadv54 stub, regenerate verdict
```

There are no r14/r15 or lesson hits. The corresponding `-S'killpg'` query over the same paths returns only `ddb7347`. `-S'process-group'` and `-S'orphan'` over those paths also return only `ddb7347`.

Lesson provenance:

- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log -L 5,12:corpus/lessons/round-15.md b576341 --oneline` → `fc3a8d4 round-15: learn rejected-harmed config preservation and declare repairs`. Its mistakes concern preservation, capability wording, and prohibited mid-flight probes; no fixture-process leak is recorded. The exact full hash is `fc3a8d49b52de26bef74418da96611aae34b958d`.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log -L 52,61:corpus/lessons/round-17.md b576341 --oneline` → `d98065d`, full hash `d98065ded46b27cb8f135255dfda72b1936e0743`. It records Sentinel F3, “TOCTOU FIFO swap hangs the run” and the proposed census-side timeout, not a Python fixture child leak. Its residual at :84-88 repeats that target-census hang. `git log -S'timeout'` hits the r17 lesson and the r15 lesson's `timeout-invocation` URL; `git log -S'leak'` on those lessons returns no commit.

### Leak-known verdict and divergence

**Known as a risk:** yes, explicitly, in the original r17 fixture commit `ddb7347`; both its comment and FIFO case say why process-group cleanup is needed. **Documented as a prior realized fixture leak in the r14/r15 lessons:** no evidence in the queried history. **Actually left behind by fixtures:** the round-18 context supplied for this assignment reports 58 blocked processes in removed `/var/tmp` paths, including r15 `r-inc-fifo rev-parse` and r17 `d2-fifo status`. I did not independently enumerate those processes; this is the supplied host observation, not a result of this historical-only probe.

That r17 report is a material divergence from the intended guarantee: the group-kill code is present from `ddb7347`, yet the supplied context attributes residuals to the r17 FIFO case too. This history does not establish whether those instances escaped that runner, came from another subprocess boundary, or survived its cleanup. Do not treat the r17 comment or its timeout return code as proof of zero residue.

**Smallest fix for the legacy surface:** replace direct-child timeout handling at every census-running fixture boundary with a fresh session and timeout cleanup that kills and reaps all census descendants, including workers placed in a separate process group; preserve FIFO cleanup. The historical r17 `killpg(proc.pid, ...)` pattern is only sufficient while descendants remain in that one group. A peer's in-progress r18 note reports census workers entering a separate group and explains why group-only cleanup can miss them; I did not verify that proposed change against a landed revision, so do not treat `killpg` alone as the r18 acceptance contract.

**Confidence:** High that r17 recognized the process-group hazard at fixture creation, based on the explicit comment and R17-08 case. Medium that r14/r15 had not yet recognized it: the queried source and lesson history contains no corresponding mechanism or acknowledgment, but absence of record cannot prove absence of awareness. The process-group limitation is structurally clear: if an r18 census worker is put in a sibling pgroup, `killpg(proc.pid, ...)` cannot reach it; a peer reports that in-progress arrangement, not independently verified here. Confidence is medium that this explains the supplied residues, since I made no process-level observation.


# Tooling / verification record

- No test, fixture, or other runtime was invoked; this is static source and Git-history reconstruction only. No tool was installed or updated.
- The role-required LSP device was unavailable: `read` on `xd://lsp` returned `No such tool: xd://lsp` and listed mounted devices without an LSP. The callsite semantics above are grounded in named source lines and `git log -L` history, not grep-based inference.
- Commands run were read-only `git log -L`, `git log -S`, `git show -s`, the named-file `grep`, and source/lesson reads. No repo code was edited.