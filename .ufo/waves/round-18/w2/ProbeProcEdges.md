STATUS: DONE — C3 edge matrix at 5efb519: 11/13 cases hold, 2 fail on one root cause (live paths whose real name ends in ` (deleted)` are asserted deleted from kernel text alone); live tool↔counter stable-set agreement is 0/0, but the shared predicate cannot see that class.

# Attacked claim — C3 (proc-census), WAVE 2 falsification

C3 as declared: `tools/souji-proc-census.sh` is a list-only residue census over current-uid processes (reasons `cwd-deleted` > `argv-path-gone` > `fd-path-gone`, `# boot_id` line, columns `pid ppid pgid sid age_s starttime state wchan reason cmd`, never signals, never reads environ), fixture `tests/fixtures/r18-proc-census.sh` P1–P11, blind counter `census/round-18/leak-count.py`, live 65 = 65.

Read at tip `5efb519f00075d958c3d1109ef6fcb24c487eb87` (clone `git -C …/lane rev-parse HEAD` → `5efb519f00075d958c3d1109ef6fcb24c487eb87`). Blobs: `tools/souji-proc-census.sh` `c2ea79602865c701821489c507afa1f5709cb372d689624176ae8bb0264c70dc`, `census/round-18/leak-count.py` `210a3caf84dabbfa26d32587ed3746df4ed7207b403df6fa3ef7528bd9d0f56a`, `tests/fixtures/r18-proc-census.sh` `f79124cf67cd77a6409568031f5377ee8d20c1f539f10ad0775047e04133390c`.

# Method (own processes only; all state under /var/tmp/souji-r18w2-ProbeProcEdges)

Clone at the tip, 13 seeded cases, every worker started with `start_new_session=True`, killed only by the recorded pid, fixture state under the seat root and removed. Four tool invocations per run: R1 defaults; R2 `--prefix <seat>/fx` (makes the top level below the prefix the plant dir, so gone-top plants fire); R3 `--prefix <seat>/fx/live` (narrowed prefix); R4 `--prefix <seat>/fx/fdlit/top` (fd ambiguity). Driver `/var/tmp/souji-r18w2-ProbeProcEdges/edge-cases.py`; full output `/var/tmp/souji-r18w2-ProbeProcEdges/edge-run2.txt`. Two full runs, identical results.

Case line format below is literal from run 2. Rows quoted are literal TSV (`ROW <run> <case> …`).

# Findings

## F1 FAIL — live directory literally named `x (deleted)` is reported as `cwd-deleted` (false positive)

Seed: `/var/tmp/souji-r18w2-ProbeProcEdges/fx/literal/x (deleted)` created, `/bin/sleep 300` started with that directory as cwd. Liveness proven at census time: `readlink /proc/<pid>/cwd` = `/var/tmp/souji-r18w2-ProbeProcEdges/fx/literal/x (deleted)` (no kernel annotation), `os.stat(/proc/<pid>/cwd).st_ino == os.stat(literal).st_ino` → `literal_dir_exists=True literal_inode_match=True`.

Tool row (run 1 and 2, both):
```
ROW	R1	literal-cwd	3715846	3715795	3715846	3715846	1	3040013	S	hrtimer_nanosleep	cwd-deleted	/bin/sleep 300
```
(`2602661` in run 1.) R2/R3/R4 also emit it; `--prefix` is irrelevant to the cwd rule.

Cause: `tools/souji-proc-census.sh:326-327`
```
cwd=$(readlink -- "$proc_path/cwd" 2>/dev/null) || cwd=''
[[ $cwd == *' (deleted)' ]] && reason='cwd-deleted'
```
The classification is the suffix alone; no existence/inode confirmation. The kernel's own text is explicitly ambiguous (`fs/d_path.c`, quoted in `.ufo/waves/round-18/w1/SrcProcCwd.md:51`: "Note that this is ambiguous"), and `SrcProcCwd.md:59` states the requirement this delivery misses: "C3 must count that as its own class (confirmed by `stat` on the stripped path, plus a stated residual ambiguity) instead of asserting 'deleted' from text alone." The w1 precision control (`.ufo/waves/round-18/w1/CriticC3Authority.md:72`: live same-uid process in an *existing* `/var/tmp` dir → unlistable, "0 false positives") is violated by its adversarial variant. Fixture P1–P11 has no literal-name case (`tests/fixtures/r18-proc-census.sh:4-16`), so the gate stays green.

Blind counter shares the defect: `census/round-18/leak-count.py:104-111` also classifies on the suffix with `require_missing=False`; `COUNTERPID literal-cwd counted`. Consequence for the claim's measurement: live 65 = 65 cannot expose this class — both implementations are wrong together on any seeded world containing it.

Note for the fix: the w1 recommendation ("stripped-path stat as confirmation") cannot disambiguate this case, because the stripped path `…/literal/x` is absent for a live `x (deleted)` too. The predicate that works is inode identity between the raw link text and the held inode; validated below.

## F2 FAIL (lower severity, same root cause) — live file literally named `x (deleted)` held as an fd is reported as `fd-path-gone`

Seed: `/var/tmp/souji-r18w2-ProbeProcEdges/fx/fdlit/top/x (deleted)` created and held live as `sleep 300`'s stdout; R4 runs with `--prefix …/fx/fdlit/top` (the file's own directory). Row:
```
ROW	R4	fd-literal	3715865	3715795	3715865	3715865	12	3040013	S	hrtimer_nanosleep	fd-path-gone:/var/tmp/souji-r18w2-ProbeProcEdges/fx/fdlit/top/x	/bin/sleep 300
```
Cause: `tools/souji-proc-census.sh:245-255` strips ` (deleted)` from the link text and never tests the raw text; the top-level rule then passes because the stripped file name is absent. Geometry note: writes were confined under the seat root, so the equivalent of a live `/var/tmp/x (deleted)` held as an fd was produced by selecting the file's parent as `--prefix`; the code path (`find_deleted_fd_path` + `top_level_scratch_gone`) is identical. With default prefixes the same shape needs a literal-name file directly in `/var/tmp`, `/tmp`, or `/dev/shm` — legal, not exotic.

## F3 HOLDS — zombie child excluded, no crash

`state=Z`, `readlink /proc/<pid>/cwd` fails `ENOENT`; stdout/stderr `cmdline` empty. Absent from R1 and R2, tool rc 0:
```
CASE	W1-zombie	PASS	state=Z cwd="ERR:[Errno 2] No such file or directory: '/proc/3715844/cwd'" rows R1/R2 absent/absent
```
Matches the w1 pin (`CriticC3Measure.md:26`, S9).

## F4 HOLDS — `--root=<gone top>/x` is an argv candidate and yields the exact path

Row:
```
ROW	R2	argv-root	3715854	…	argv-path-gone:/var/tmp/souji-r18w2-ProbeProcEdges/fx/argvgone/x	bash -c while :; do sleep 30; done bash --root=/var/tmp/souji-r18w2-ProbeProcEdges/fx/argvgone/x
```
Matches the delivered candidate grammar `absolute elements or values in --opt=/path arguments` (`.ufo/waves/round-18/w1/ProcCensus.md:11`; code `tools/souji-proc-census.sh:218-231`). Note this supersedes the earlier critic sketch that wanted `--root=` *not* listed (`CriticC3Measure.md:45`); the claim I attacked names `--root=` as a case, and the tool's documented rule agrees.

## F5 HOLDS — `/var/tmp/<top>/sub` deleted while `<top>` survives

Three variants, top-level kept alive: argv element → absent (`W4b-nested-argv PASS`), deleted stdout fd → absent (`W4c-nested-fd PASS`), cwd = deleted `sub` → listed `cwd-deleted` (`W4a-nested-cwd PASS`). Matches P10/S5 for argv/fd (`top_level_scratch_gone`, `tools/souji-proc-census.sh:162-180`) and the intentionally unrestricted cwd rule.

## F6 HOLDS — deleted cwd outside the selected prefix is still listed

R3 uses `--prefix …/fx/live`; the deleted cwd lives under `…/fx/other/del`. Row present with `cwd-deleted` (`W3-narrowed-prefix-cwd PASS`). Source: the cwd branch never consults `PREFIXES` (`tools/souji-proc-census.sh:325-327`), matching the pinned unrestricted rule (`CriticC3Measure.md:27`, S7). Side note, not a claim failure: usage says `--prefix DIR … Scratch-path prefix to inspect` (`:20-25`) while cwd rows can never be narrowed by it; the doc should say prefix scopes argv/fd only.

## F7 HOLDS — deleted cwd recreated at the same path (S10)

`rmdir D; mkdir D` after spawn: `readlink` still `…/D (deleted)`, stripped path exists with a new inode (`recreate_cwd_readlink=… (deleted) stripped_exists=True`); row retains `cwd-deleted` (`W7-recreate PASS`). This is also the counter-example that rules out an `-e stripped_path` fix for F1.

## F8 HOLDS — precedence and single-row output

cwd deleted AND argv path gone (different gone tops): exactly one row, `cwd-deleted` (`W6-precedence PASS`), matching `ProcCensus.md:10` and the check order `tools/souji-proc-census.sh:325-339`.

## F9 HOLDS — very long argv

Argv of 200 × 1024-byte arguments plus the gone path last (~205 kB): exact row, 10 columns, `cmd` exactly 160 bytes (the byte-slice at `:211`), no raw tab/newline leakage, rc 0:
```
ROW	R2	long-argv	3715862	…	argv-path-gone:/var/tmp/souji-r18w2-ProbeProcEdges/fx/longgone/x	bash -c while :; do sleep 30; done bash AAAA…
CASE	W8-long-argv	PASS	… cmd<=160B
```

## F10 HOLDS — output contract and exit status

Every run: rc 0, stderr empty, first line `# boot_id <uuid>`, second line exactly the 10 documented columns (`RUN … header_ok=True boot_ok=True`). No environ access anywhere: grep of the tool shows only `/proc/stat`, `/proc/sys/kernel/random/boot_id`, `$proc_path/stat`, `status`, `cmdline`, `cwd`, `wchan`, `fd/*`; no `kill` outside the selftest EXIT trap (`:363-383`). Workers in all 13 cases stayed alive across four census runs (no `worker-dead` lines).

## F11 Live tool↔blind-counter agreement

First naive pair: tool 86 rows, counter 86 — but 16 pids each way; every tool-only pid was dead before the counter ran (one was listed by the counter in the first window; all are `ENOENT` now), i.e. churn, not classification. Two-window protocol (`CriticC3Measure.md` F5: disagreement only if present in one implementation across both windows):
```
window sizes t1,t2,c1,c2: 80 80 94 87
stable-in-tool never counted: []
stable-in-counter never tool: []
```
So 0/0 stable disagreements. Absolute counts are no longer 65: other seats' fleet fixtures have added residues (by_reason in the counter window: argv 22 / cwd 60 / fd 12). The declared "live 65 = 65" is a dated snapshot, not reproducible today; the agreement property reproduces under the pinned protocol. Caveat: the tool scan costs 3.24–4.83 s versus 0.06 s for the counter, so the "within one second" precondition cannot be met; the two-window protocol is the valid comparison, not a single pair.

Predicate validation for the fix, over the tool's first live window: 60 `cwd-deleted` rows → 58 confirmed deleted by inode comparison, 0 live-literal, 2 unreadable (exited mid-scan). So the fix below would not drop live residue.

## Residual unknown — single-dash `-root=<gone>` diverges from the blind counter (not part of the declared grammar)

`CASE W5b-single-dash PASS` (absent), consistent with the candidate glob `--*=/*` (`tools/souji-proc-census.sh:218-223`) and `ProcCensus.md:11`. But `leak-count.py:21,55-65` regex-matches `/var/tmp/…` anywhere in any argv token, so a seeded process carrying `-root=/var/tmp/<gone>/x` would be counted by the counter and missed by the tool. Marked INFERENCE: not executed, because reproducing it needs a deleted top level directly under `/var/tmp`, outside this seat's write bounds. If pid-set equality on seeded worlds matters, extend the candidate case to `-?*=/*` (and mirror it in the counter), or document the asymmetry.

# Verdict

**C3 fails on precision; operability and the output contract hold.** Reasons/columns/`# boot_id`/exit 0/never-signal/never-environ, precedence, top-level boundary, zombie exclusion, `--root=` extraction, recreated-path classification, and very long argv all behave as declared (11/13 seeded cases). The single root cause F1/F2 is that ` (deleted)` text is treated as proof of deletion; a live directory (or fd target) whose real name ends in the suffix is emitted as residue. Fixture P1–P11 does not cover the class, and the blind counter implements the same suffix-only rule, so the live agreement metric is blind to it. Because the kernel annotation is ambiguous by design and the lane's own S064 item requires the ambiguity to be carried, this is a genuine defect in the delivered C3 surface, latent on today's live host (0 live-literal cwds observed) but reproducible on demand.

# Smallest fix

1. `tools/souji-proc-census.sh:326-327` — keep the suffix test, but confirm deletion with inode identity between the raw link text and the held inode (bash `-ef` uses stat(2); no extra process):
```bash
cwd=$(readlink -- "$proc_path/cwd" 2>/dev/null) || cwd=''
if [[ $cwd == *' (deleted)' ]]; then
  # d_path() text is ambiguous (fs/d_path.c): a live name can end in the
  # suffix. Live iff the raw text resolves to the inode the process holds.
  if [[ -e $cwd && $cwd -ef $proc_path/cwd ]]; then
    :  # live directory literally named with the suffix: not residue
  else
    reason='cwd-deleted'
  fi
fi
```
2. `tools/souji-proc-census.sh:248-250` — same guard in `find_deleted_fd_path` before stripping:
```bash
[[ $fd_link == *' (deleted)' ]] || continue
[[ -e $fd_link && $fd_link -ef $fd_path ]] && continue   # live file named with the suffix
target=${fd_link%' (deleted)'}
```
3. Mirror the same confirmation in `census/round-18/leak-count.py:104-111` so the pair stays equal on seeded worlds, and add the regression cases to `tests/fixtures/r18-proc-census.sh`: literal live cwd (F1), literal live fd (F2), zombie (F3), `--root=` gone (F4), nested top-alive argv/fd (F5), recreated cwd (F7), 200 kB argv (F9). F1/F2 are the two that currently fail.

`-ef` predicate verified in isolation with inherited fds: literal live path vs held fd → `SAME`; deleted path text vs held fd → `DIFF`; i.e. exactly the discrimination needed, and it preserves all 58 live deleted-cwd rows sampled.

# Peer cross-check (w2, read-only)

- The cwd-vs-`--prefix` scope asymmetry (my F6) is already reported by siblings: `.ufo/waves/round-18/w2/RevProcCensusCode.md:9` and `RevLeakCounterBlind.md:25-27`. Those reports treat it as a defect; the pinned w1 rule (`.ufo/waves/round-18/w1/CriticC3Measure.md:27`, S7) says the unrestricted cwd rule is intentional. I record it as holds-per-pin plus a usage/doc ambiguity, not as a claim failure.
- My F1/F2 literal-name precision class is not among the mutation survivors in `MutProcCensus.md` (its survivors are prefix component-boundary mutants, `MutProcCensus.md:27`), nor in the source-review reports above. It is distinct from the prefix-scope issue: it reproduces with default prefixes (F1) and with the `--prefix` equal to the literal path's own root (F2), and it is invisible to the tool↔counter agreement because both use the same suffix-only predicate.
- `SoujiR18.ReopenS064` owns the source item; the S064 requirement quoted here (`SrcProcCwd.md:51,59`) is unchanged at the tip.

# Limits

- Live cwd outside all default prefixes (e.g. under `$HOME`) was not created: writes are confined to `/var/tmp/souji-r18w2-ProbeProcEdges`. The narrowed-`--prefix` case exercises the same code path (the cwd branch ignores `PREFIXES` entirely).
- The very-long-argv case used ~205 kB total (200 × 1 KiB + path), beyond any page/buffer boundary in the read loop; a single argument cannot exceed the kernel's 128 KiB MAX_ARG_STRLEN.
- The fixture `tests/fixtures/r18-proc-census.sh` was not executed (not in this seat's ALLOWED-EXEC list); its P1–P11 case list was read for coverage only.
- All live-pair differences were attributed by re-reading `/proc`: tool-only pids were dead before the counter ran; counter-only stable pids became residue between the tool window and the counter window (seen in both tool windows for two of them). No stable-set disagreement was observed.

# Tooling / hygiene

No tools installed or upgraded; no pacman transaction attempted. Lane clone was only read/executed, no lane file modified; this report is the only lane write. Clone removed after the runs; no seat-started process remains (`ps -eo pid,pgid,args | grep /var/tmp/souji-r18w2-ProbeProcEdges` → empty), fixture root removed.
