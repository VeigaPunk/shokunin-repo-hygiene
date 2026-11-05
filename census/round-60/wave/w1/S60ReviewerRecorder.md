# S60ReviewerRecorder: falsification of C2 (receipt writer operability)

Seat: S60ReviewerRecorder (reviewer, leaf, no subagents). Lane HEAD read: `1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4`.
Claim under attack: `tools/souji-receipt-write.py` passes an 8-case fixture (clean, overwrite refusal, in-flight
atomicity, kill residue, output bound, short rev, absent instrument, dirty tree) while the base recorder
`census/round-57/record-receipt.sh` passes 3.

Builders and logs: `.ufo/waves/round-60/w1/S60ReviewerRecorder/` (see "Reproduction"). Every number below is from
`run-all.sh` (rc 0, logs in `S60ReviewerRecorder/logs/`) unless marked otherwise.

## Snapshots under test (sha256; the artifacts changed while this review ran)

| artifact | sha256 | note |
|---|---|---|
| `census/round-57/record-receipt.sh` (base) | `84148011abc9574048fc77e02427bee9010850418beeeaaa1babe59185109aa9` | unchanged |
| `census/round-58/c2-gate.py` | `56f2a31163035726f1190db3e6b827fc121602377e187d16a54a6ae8f15af543` | r58 gate, used for interop |
| candidate `S60ExecRecorder/souji-receipt-write.py` (659 lines) | `b916a4fd28206ac80208bc22027abc31778d8b893e8f3744270d612684b53e9f` | **all candidate verdicts below are on this snapshot** |
| sibling fixture `S60ExecRecorderFix/r60-receipt-write.py` | `d5291501e8ce828e26aabaea69853fe3223297f2d5ac249aee62f73bb294c114` | snapshot used; runs on the current candidate |
| spec-literal reference (mine, `ref-writer.py`) | `0009d1aded13ea937df897a5357d49cfcb1166ecb1ccbfa84f6aa28a7c670e30` | scratch control, not a deliverable |

Superseded (do not cite): an earlier candidate snapshot `af93273837be216215fa182be1007e4fc8b77e03b75a3290a84ed95858cf04b0`
(658 lines) never appended captured output to `chunks`, so receipts had no command output and its own selftest
read 10/12. The sibling fixture also changed under me: an earlier version crashed (`run_matrix([tool])` passes a list
where `Matrix` expects a str; `AttributeError` at `r60-receipt-write.py:128`). Results from both are discarded; only
the snapshot table above is authoritative.

## Verdict on the claim

| sub-claim | verdict |
|---|---|
| candidate passes the 8-case fixture | **HOLDS** on snapshot `b916…`: my harness 8/8, sibling fixture `SUMMARY cases=8 pass=8 fail=0`, controls rejected, rc 0 |
| base recorder passes 3 | **FALSIFIED**: base passes **4/8** (cases 3, 4, 6, 7) on my harness and on the sibling fixture (`pass=4`) |
| the 8 cases measure "in-flight atomicity" and "kill residue" | **FALSIFIED**: base passes cases 3 and 4; a deliberately non-atomic writer passes cases 3 and 4 (sibling fixture: `pass=3`, passing 1, 3, 4) |
| candidate is "hardened" (atomic, refuse overwrite, refuse dirty tree, bound, rev/instrument checks) | **FALSIFIED** on five named attacks (F4, F6, F7, F9, F11 below); the bound and the instrument checks survive (F8) |

Net: the 8/8 pass is reproducible, but the 8 cases do not test the properties they are named for, and the candidate
still fails several operability attacks the fixture never exercises.

## Numbered findings

### F1. Base recorder passes 4 of 8, not 3 (claim number falsified)
- Input: the 8 cases as built by `harness.py eight` (independent) and `sibling-fixture-as-delivered.py` (positional style for `.sh`).
- Command: `python3 harness.py eight --tool census/round-57/record-receipt.sh --mode base --work <W>`; `python3 -B sibling-fixture-as-delivered.py --tool census/round-57/record-receipt.sh --work <W>/fx`.
- Observed: harness `EIGHT cases=8 pass=4 fail=4` (passes 3-in-flight, 4-killresidue, 6-shortrev, 7-instrabsent; fails 1, 2, 5, 8). Sibling `SUMMARY cases=8 pass=4 fail=4`. Both rc 0 / rc 1 (fixture exits 1 on pass≠8, expected).
- Expected by claim: 3. Verdict: **FALSIFIED** (4).
- Caveat: sibling case 5 reports `tool rc=127`, a positional-argv artifact (the base has no `--max-bytes`); the base fails case 5 regardless.

### F2. Candidate passes the 8-case fixture (claim holds on snapshot b916)
- Command: `python3 harness.py eight --tool cand-souji-receipt-write.py --mode cand --work <W>`: `EIGHT cases=8 pass=8 fail=0`, rc 0.
- Sibling: `python3 -B sibling-fixture-as-delivered.py --tool cand-souji-receipt-write.py --work <W>/fx`: `CASE 1..8 pass`, `# control always-write failed cases [1..8] -> ALWAYS-WRITE-REJECTED`, `# control always-refuse failed cases [1, 3] -> ALWAYS-REFUSE-REJECTED`, `SUMMARY cases=8 pass=8 fail=0 control=...`, rc 0.
- Candidate's own selftest: `python3 cand-souji-receipt-write.py --selftest --work <W>` → `SELFTEST cases=12 pass=12 fail=0`, rc 0.
- Verdict: **HOLDS** (this part of the claim is not falsified).

### F3. The two "atomicity" cases do not measure atomicity or kill residue
- Case 3 polls OUT at 0.3 s while the wrapped command sleeps 1 s. Any writer that writes only after the command exits passes it, including a non-atomic one.
  - Non-atomic stub (`nonatomic-stub.py`: truncate-in-place `open(out,"w")`, header, sleep 0.6 s, tail): attack g1 shows `early_absent=True final_last_line_EXIT0=True`. Sibling fixture against the stub: `CASE 3 atomic-in-flight pass`.
- Case 4 kills the process group at 0.4 s while the command is still in `sleep 3`. The candidate creates its temp only after the command exits, so no temp exists at kill time and residue cannot appear. The base also passes trivially (it writes nothing until the command exits).
- Kill-after-temp-exists, which is the actual residue risk, is not in the fixture. See F6.
- Verdict: **FALSIFIED** as tests of "in-flight atomicity" and "kill residue". They discriminate writers that write early from writers that write late, not atomic from non-atomic writers.

### F4. (a) TOCTOU between the existence check and the rename: FALSIFIED in the rename window
- Candidate code path: the post-command `os.path.lexists(out)` recheck in `write_receipt`, then `os.replace(tmp, out)`. Python's `os.replace` silently overwrites; no no-clobber primitive is used (`noreplace=False linkat=False` in the strace evidence from `harness.py probe toctou`).
- a1, command creates OUT itself (`bash -c 'printf RACER-FILE > "$S60_OUT"; echo ran'`, OUT pre-check passes): candidate **rc 2**, racer bytes preserved. Ref and base: rc 0, receipt replaced racer. Verdict: candidate **not falsified** (its post-command `lexists` recheck catches it).
- a2, external poller creates OUT when `*r.txt*.tmp` appears (run-all, n=1): candidate **rc 2**, racer preserved. Verdict: not falsified at this sample size.
- a3, deterministic: LD_PRELOAD shim on `rename`/`renameat`/`renameat2` that creates OUT immediately before the real rename (`harness.py probe toctou`, shim fired):
  - candidate: `shim_fired=True rc=0 receipt_intact=True raced_bytes_survived=False`.
  - reference: identical.
  - Expected: rc 2, racer bytes preserved. Verdict: **FALSIFIED**. A file created at OUT between the final check and the rename is silently destroyed with rc 0.
- Verified remedy (scratch, not applied to the candidate): `O_TMPFILE` + `os.link("/proc/self/fd/N", OUT)`. With OUT pre-existing: `EEXIST refused, no clobber -> EXISTING`, and the directory held only `r.txt` (no residue). `os.link` on an existing target is the no-clobber primitive `os.replace` is not.

### F5. (b) OUT location
- b1, symlinked OUT directory (`link` in the work dir → an outside dir; OUT=`link/r.txt`): candidate **rc 0**, `wrote_outside_lane=True`. Base: same. Ref: same.
  - Verdict: **FALSIFIED against "hardened"**. The numbered requirements do not require containment of OUT (requirement 10 restricts only lane writes), so this is a gap rather than a stated-requirement violation.
- b2, OUT directory missing: candidate **rc 2, command not run** (`command_side_effect_ran=False`). Ref: command ran, rc 1. Base: command ran, rc 0 (`No such file or directory`). Verdict: candidate **not falsified**.
- b3, OUT a dangling symlink to a missing target: candidate **rc 2**, `created_target=False` (refused by `lexists`). Base: created the target (`rc 0`). Verdict: candidate **not falsified**.
- x1, OUT on `/dev/shm` (tmpfs; lane on btrfs/xfs): candidate **rc 0**, receipt written; temp is beside OUT so no EXDEV. Verdict: not falsified.

### F6. (c) SIGKILL between fsync and rename leaves residue; SIGTERM does not
- Probe: `LD_PRELOAD` shim on `fsync` sleeping 6 s after the real fsync. The harness waits until a temp appears, sleeps 0.2 s, then sends the signal to the process group.
- c1, SIGKILL: candidate **`out_exists=False residue=['r.txt.yx8zajsg.tmp']`**. Base: no temp is ever created, so the probe is **invalid for base** (it waits 15 s and kills after completion; `out_exists=True`). Ref: `.r.txt.*.tmp` residue.
- c2, SIGTERM: candidate **`residue=[]`**, handler works (`_on_signal`). Ref: residue (no handler in my spec-literal control).
- Verdict: **FALSIFIED** for SIGKILL. The fixture's case 4 cannot see this (F3). No user-space writer can clean up after SIGKILL, so the claim must either name the residue and sweep it on the next run, or avoid named temps (the `O_TMPFILE` remedy in F4 leaves no name to leak).

### F7. (d) A command writes to the receipt path
- d1, foreground write during the run (`printf FORGED-FG > "$S60_OUT"`): candidate refuses (rc 2, F4 a1 mechanism). Not falsified.
- d2, background child waits until OUT exists, then writes `FORGED-LATE` after the writer has exited (run-all `attacks-cand`):
  - candidate **rc 0**, `receipt_tampered_after_exit=True head=b'FORGED-LATE'`.
  - Verdict: **FALSIFIED**. Nothing kills or waits for the command's process group before the rename, and nothing re-verifies OUT after the writer exits.
  - [INFERENCE, not tested] killing the process group (same pgid, since the child is in the command's group) before the rename would close d2. Not verified here.

### F8. (e) Bound bypass attempts: candidate HOLDS
- e1, single 1 MiB line with default bound 262144: candidate **rc 2, OUT absent**. Ref: rc 2. Base: rc 0, no bound.
- e2, 262144 bytes of `/dev/urandom` (non-UTF-8) at the bound: candidate **rc 0, receipt 262357 bytes** = 262144 body + 213 header. The body is raw bytes, so no expansion. Note: the bound applies to the body; the receipt exceeds N by the header size only. Ref (`decode('utf-8','replace')`): 475911 bytes, i.e. the replacement character expands invalid bytes 3× and breaks the bound. Verdict for the candidate: **not falsified**; the ref's expansion is a real bug in a naive writer.
- e3, 200 MiB output in a fresh process (`e3-isolated.py`, only child, peak `ru_maxrss` of the child):
  - candidate: **rc 2, OUT absent, peak 21.4 MiB** (streams, kills at overflow).
  - ref: rc 2, peak 420.5 MiB (buffers everything).
  - Base peak 17 MiB is not comparable: bash `$(…)` drops NUL bytes [INFERENCE, not verified here].
- Verdict: candidate **not falsified** on bound or memory.
- Note on measurement: an earlier in-process `ru_maxrss` delta reported 0 for the candidate, which only means the child did not exceed earlier children's peak. Superseded by the isolated measure.

### F9. (f) Dirty-tree guard bypasses
- f1, ignored untracked code executed (`.gitignore: tools/ign*.py`; untracked `tools/ign_override.py` prints `EXECUTED-UNTRACKED`; command `python3 tools/ign_override.py`; `--rev` = HEAD): candidate **rc 0, porcelain=''**, receipt says `executed=True`.
  - Verdict: **FALSIFIED**. The receipt binds rev and instrument bytes, but the command ran working-tree code that is not at rev and is invisible to `git status --porcelain`. Remedy: check `--ignored`, or run from an export of the rev (e.g. `git archive`), not the worktree.
- f2, tracked instrument modified during the run (`printf "# tampered\n" >> tools/instrument.py; echo x`): candidate **rc 0, receipt written**, `porcelain_after=' M tools/instrument.py'`.
  - Verdict: **FALSIFIED**. The dirty check runs once, before the command. Remedy: re-run `git status --porcelain` after the command and before the rename.
- f3, `GIT_DIR`/`GIT_WORK_TREE` pointed at a clean clone, repo dirty: candidate **rc 2, receipt absent**. Not falsified (its `git()` scrubs `GIT_DIR`/`GIT_WORK_TREE`).
- f4, staged-only change (`A  staged.txt`): candidate **rc 2**. Not falsified.
- Untracked file refused: candidate **rc 2** (8-case case 8). Not falsified.

### F10. (g) Case 3 poll window: FALSIFIED (see F3)
- Non-atomic stub passes case 3 (g1). Kill mid-write leaves a readable partial receipt (g2: `out_exists=True partial_is_readable=b'9ef05…\n'`), so the stub really is non-atomic. The poll window at 0.3 s is shorter than the command's 1 s, so the stub's partial write never falls in the observed window.

### F11. Interop with the r58 receipt gate: FALSIFIED
- i1, annotated tag object OID as `--rev` (loose object, `refs/tags/vannot`): candidate **rc 0, receipt written**. The r58 gate on that receipt: `FINDING RECEIPT-REV-ABSENT`, gate rc 1. Base: same (gate rc 1).
- kd1, keep-only commit as `--rev` with `--allow-dirty` and the worktree instrument set to the keep commit's bytes: candidate **rc 0, receipt written**. The r58 gate: `FINDING RECEIPT-REV-KEEP-ONLY`, gate rc 1.
- k1, same keep-only commit, clean worktree at main: candidate **rc 2** ("worktree … differs from committed bytes at rev"). The refusal is incidental (worktree binding), not a keep-only check.
- Verdict: **FALSIFIED**. The writer produces receipts the downstream gate refuses, and the 8-case fixture does not test either rev class.

### F12. Candidate passes its own selftest and the sibling fixture on b916; base and ref interop differ
- Reference (spec-literal, scratch control) passes my 8-case harness 8/8 as well, so the 8-case set is passable by a writer that follows the spec; the discrimination is against base, not against the spec.
- Attacks on the reference: a1 rc 0 (no post-command recheck, see F4), a2/F4 clobber, d2 tamper, e2 expansion, f1/f2 as candidate, i1/kd1 accepted. The candidate improves on the reference in a1, e2, e3, SIGTERM and f2 is no better.

## Attack-by-attack table (exact input, observed rc, expected, verdict)

| attack | input (exact) | candidate rc / observation | expected | verdict |
|---|---|---|---|---|
| (a) TOCTOU, command creates OUT | `bash -c 'printf RACER-FILE > "$S60_OUT"; echo ran'` | rc 2, racer kept | refuse, rc 2 | holds |
| (a) TOCTOU, external poller | poll `*r.txt*.tmp`, write OUT | rc 2, racer kept (n=1) | refuse | holds (n=1) |
| (a) TOCTOU, rename window | LD_PRELOAD creates OUT just before rename | rc 0, racer destroyed | refuse, rc 2 | **falsified** |
| (b) symlinked OUT dir | OUT = `<link>/r.txt`, link → outside | rc 0, wrote outside | refuse or contain | **falsified** (gap) |
| (b) OUT dir missing | OUT under non-existent dir | rc 2, command not run | refuse before run | holds |
| (b) dangling symlink OUT | OUT → missing target | rc 2, nothing created | refuse | holds |
| (b) OUT on tmpfs | OUT in `/dev/shm` | rc 0, receipt written | write | holds |
| (c) SIGKILL after temp | fsync shim sleep 6 s; SIGKILL pgroup | residue `r.txt.*.tmp` | no residue | **falsified** |
| (c) SIGTERM after temp | same, SIGTERM | no residue | no residue | holds |
| (d) foreground OUT write | command writes OUT during run | rc 2 (via recheck) | refuse | holds |
| (d) background post-exit write | child writes OUT after writer exits | rc 0, receipt replaced | receipt immutable | **falsified** |
| (e) single 1 MiB line | `head -c 1048576 /dev/zero \| tr` | rc 2, OUT absent | refuse | holds |
| (e) non-UTF-8 at bound | `head -c 262144 /dev/urandom` | rc 0, body 262144 + 213 B header | bound on output | holds (boundary note) |
| (e) 200 MiB output | `head -c 209715200 /dev/zero` | rc 2, peak 21.4 MiB | bounded memory | holds |
| (f) ignored untracked executed | `.gitignore` `tools/ign*.py`; command runs it | rc 0, clean porcelain, executed | refuse or export | **falsified** |
| (f) tracked edit during run | command appends to `tools/instrument.py` | rc 0, dirty after, receipt written | refuse | **falsified** |
| (f) GIT_DIR hijack, dirty | GIT_DIR → clean clone | rc 2 | refuse | holds |
| (f) staged-only | `git add staged.txt` | rc 2 | refuse | holds |
| (g) case-3 window | non-atomic stub, poll 0.3 s, command 1 s | passes case 3 | must fail | **falsified** |
| interop tag OID | loose annotated tag OID as `--rev` | rc 0; r58 gate RECEIPT-REV-ABSENT | refuse (r58 contract) | **falsified** |
| interop keep-only (allow-dirty) | keep commit as `--rev`, worktree = keep bytes | rc 0; r58 gate RECEIPT-REV-KEEP-ONLY | refuse (r58 contract) | **falsified** |

## Named limits

1. Single run per verdict on snapshot `b916a4…`; a2 (external poller) is n=1. The deterministic rename-window shim (F4 a3) is the authoritative race result.
2. Only Linux, glibc, Python 3.14.8, git 2.56.0. The `fsync` shim targets glibc `fsync`; `O_TMPFILE` behaviour verified on the scratch filesystem only.
3. The base SIGKILL probe (F6) is invalid (the base never creates a temp); base residue is therefore "not measured", not "clean".
4. The memory numbers (F8 e3) are from a single fresh process per tool; the base figure is not comparable (NUL-dropping `$(…)` [INFERENCE]).
5. The receipt-size boundary (F8 e2) is documented, not a bypass: the bound applies to the body; the header adds 213 bytes in this test.
6. [INFERENCE, not verified] killing the process group before the rename would close F7 d2; the `O_TMPFILE` + `os.link` remedy is verified only in isolation, not in the candidate.
7. No mutation test of the candidate (mutation-tester seat's job). I did not modify the candidate; I only copied it.
8. The sibling fixture changed during review; the verdicts use the snapshot in the table. The sibling's own `SUMMARY` on its current version is the fixture-of-record result.
9. The spec-literal reference is my control, not a candidate; it is not part of any deliverable.

## Lane and tool hygiene

- No lane writes. Lane git: `git log`, `git rev-parse HEAD`, and one `git status --porcelain` (read-only intent; `git status` may refresh the index stat cache, disclosed). All fixture git calls name `-C <fixture>` and assert `--show-toplevel`.
- Tools installed: none. Used system `gcc`, `strace`, `python3` 3.14.8, `git` 2.56.0. No pacman, no `~/.local/bin` changes.
- Scratch: `/fast/scratch/hyaku/souji-r60/S60ReviewerRecorder/` (harness copies and `tmp.*` fixtures) removed on exit; `run-all.sh` runs its own scratch under `trap … EXIT`.

## Reproduction

From `.ufo/waves/round-60/w1/S60ReviewerRecorder/`:

```
bash ./run-all.sh        # rc 0; per-step rc printed; logs in logs/
```

Builders in the directory:
- `harness.py`: 8-case independent harness (`eight`), TOCTOU shim probe (`probe --probe toctou`), other probes.
- `attacks2.py`: attacks a, b, c, d, e, f, g, plus `interop` (tag OID).
- `extra.py`: keep-only (no allow-dirty) and tmpfs OUT.
- `keeponly-allowdirty.py`: keep-only with `--allow-dirty` and worktree bytes = keep bytes.
- `e3-isolated.py`: isolated peak RSS.
- `nonatomic-stub.py`: the non-atomic writer control for g and for the sibling case 3.
- `ref-writer.py`: spec-literal control.
- `cand-souji-receipt-write.py`, `sibling-fixture-as-delivered.py`: byte snapshots (sha in `SHA256SUMS`).
- `logs/`: all outputs. Step rcs from the last `run-all.sh` run: eight-base 0, eight-ref 0, eight-cand 0, selftest-cand-own 0, attacks-base/ref/cand 0, extra-base/ref/cand 0, toctou-cand 0, toctou-ref 0, sibling-vs-cand 0, sibling-vs-base 1 (fixture exit on pass≠8, expected), sibling-vs-nonatomic 1 (expected), keeponly-allowdirty-cand 0, e3-isolated-cand 0, e3-isolated-ref 0.

Exact summary lines (from `logs/`):
- `eight-base.txt`: `EIGHT cases=8 pass=4 fail=4`
- `eight-ref.txt`: `EIGHT cases=8 pass=8 fail=0`
- `eight-cand.txt`: `EIGHT cases=8 pass=8 fail=0`
- `selftest-cand-own.txt`: `SELFTEST cases=12 pass=12 fail=0`
- `sibling-vs-cand.txt`: `SUMMARY cases=8 pass=8 fail=0 control=ALWAYS-WRITE-REJECTED,ALWAYS-REFUSE-REJECTED`
- `sibling-vs-base.txt`: `SUMMARY cases=8 pass=4 fail=4 control=ALWAYS-WRITE-REJECTED,ALWAYS-REFUSE-REJECTED`
- `sibling-vs-nonatomic.txt`: `SUMMARY cases=8 pass=3 fail=5 control=ALWAYS-WRITE-REJECTED,ALWAYS-REFUSE-REJECTED`
- `toctou-cand.txt`: `TOCTOU-race shim_fired=True rc=0 out_head=b'instrument=tools/instrum' receipt_intact=True raced_bytes_survived=False`
- `e3-isolated-cand.txt`: `rc=2 out_exists=False peak_child_maxrss_MiB=21.4`; ref: `peak_child_maxrss_MiB=420.5`

## Recommendation to the L1 (planner)

Do not carry "passes 8 while base passes 3" into the freeze as evidence of operability. The defensible statement is: the candidate passes 8/8 on the named cases; base passes 4/8; cases 3 and 4 do not test atomicity or kill residue; and F4, F6, F7, F9, F11 are open. If C2 must hold as "operability", the fixture needs (i) a kill-after-temp case, (ii) a racer injected before the rename, (iii) a post-exit forge case, (iv) an ignored-file and mid-run-mutation case, and (v) an r58-gate interop case. Fixes verified or identified: `O_TMPFILE` + `os.link` (F4, verified in isolation), post-command status recheck (F9 f2), process-group kill before rename (F7, unverified).
