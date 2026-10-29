# R42w2reviewer05 — falsification of C3 at the landed tip (round 42, wave 2)

Seat: R42w2reviewer05 (reviewer, leaf, no subagents). Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, tip `3105a63b23481fccf7df58e74d14a6681e0ea0c8` (`git rev-parse HEAD` confirmed; `git status --porcelain` empty). Lane writes: none. Git: read-only `show`, `rev-parse`, `cat-file` only. Tools installed: none. Scratch `/fast/scratch/hyaku/souji-r42/R42w2reviewer05` removed before yield; receipts copied to `.ufo/waves/round-42/w2/R42w2reviewer05/receipts/`.

Seat directory (all probes and receipts): `.ufo/waves/round-42/w2/R42w2reviewer05/`.

## Verdict

1. **The frozen counter's target is not stable under load.** Four frozen-counter runs at the tip: three read the full target (`killed=13 … old_killed=0 equiv_killed=0`); run 2, started while 16 busy Python processes ran, read `killed=5 survived=8`. I could not reproduce run 2 in four later loaded executions of the same code path, and the counter does not record fixture output, so its cause is **not identified**. A second loaded grid execution (my instrumented copy of the same grid) read `old_killed=1` (r36 killed `J9`). The C3 target is therefore met on the landing run only if that run happens to be quiet; the L1 should re-run it and treat a red as a load artefact until the counter records fixture output.
2. **Per-case attribution (quiet run, verified under load):** all 13 MUTANT rows are killed by at least one named case; **none of the 6 EQUIV rows is killed by any case** (13 cases, `pass=13` for each EQUIV mutant). Every case's failure set is listed in section 3.
3. **Assertion weaknesses (section 3):** two cases (`root-option-is-required`, `record-option-is-required`) kill their mutants by exit code plus a generic argparse word; one case kills G3 by a wall-clock bound only (`elapsed >= 5.0`), and that is the kill most exposed to load; one kill (B1) is a 25-second timeout.
4. **Prior-battery flake (not C3's population, but it is the counter's `old_killed` leg):** the r36 fixture killed `J9` in one loaded grid run (`grid-loaded2`), and in one loaded r36 pass its `read-only` case reported `changed=1` for mutants `G5` and `D4` (`r36probe-loaded` rep 2). Neither reproduced in later loaded runs (six instrumented r36 runs under load, `receipts/r36-readonly-instrumented-under-load.txt`, all clean). The r36 fixture reads mtime and digest of the whole fleet tree, so a concurrent writer in the scenario directory is the plausible cause [INFERENCE: not isolated].

## 1. Three-run requirement: counter runs and differences

Command (identical for all runs):
`python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 3105a63b23481fccf7df58e74d14a6681e0ea0c8 --scratch /fast/scratch/hyaku/souji-r42/R42w2reviewer05`

Load conditions were **not idle** at any point: the host is shared with sibling seats, whose load average was 24 (1 min) at run 1 and 60–200 during the later runs. "Idle" was not achievable; the load column below is what I measured.

| run | when / load (1-min at start) | receipt | SUMMARY (verbatim) | exit | wall |
|---|---|---|---|---|---|
| 1 ("idle" as specified: no stress from me) | 22:07, load 24.4 | `receipts/run1.txt`, `run1.err` | `SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247` | 0 | 171.2 s |
| 2 (16 busy Python processes from `stress.py`, started with the run) | 22:10, load 21 → 60 | `receipts/run2.txt`, `run2.err`, `stress.log` | `SUMMARY mutants=13 killed=5 survived=8 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247` | 1 | 150.6 s |
| 3 (alone after stress was killed) | 22:17, load 77.6 | `receipts/run3.txt`, `run3.err` | `SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247` | 0 | 173.2 s |

**Differences between the three runs.** Only run 2 differs, and only in the kill fields:
- `killed`: 13 (runs 1, 3) vs **5** (run 2); `survived`: 0 vs **8**; `pristine`, `prior`, `old_killed`, `equiv`, `equiv_killed`, `anchors`, `cases`, `tool_sha` are identical in all three.
- Run 2 survivors (each `prior=-`, so no prior fixture killed them): `B1 E2 E4 G2 G4 G5 H1 H2`. Run 2 killed `G3 I1 J9 M1 D4`. The `MUTANT` lines of run 1 and run 3 show all 13 killed.
- The EQUIV rows agree in all three runs (`survived prior=-` each).
- `equiv_killed=1` (executor09's wave-1 reading) did not occur in any of my runs.

Counter-equivalent runs under load that I made afterwards (same code path, output kept by my instrumented copy `grid.py`; the frozen counter does not keep fixture output):
| run | load | SUMMARY |
|---|---|---|
| `receipts/run4.txt` (frozen counter, run concurrently with 16 stress processes and a second loaded job) | 135–204 | `killed=13 … old_killed=0 equiv_killed=0` (exit 0, wall 4m01s) |
| `grid-loaded.txt` (`grid.py`, 16 stress processes) | ≈90 (at end) | `killed=13 … prior=8/8 old_killed=0 … equiv_killed=0` |
| `grid-loaded2.txt` (`grid.py`, 16 stress processes, concurrent with run4) | 150–206 | `killed=13 … prior=8/8 old_killed=1 … equiv_killed=0` (J9 killed by r36) |

So over six full-grid evaluations of this tip, four met the target and two did not (run 2: `killed=5`; grid-loaded2: `old_killed=1`). I could not identify the mechanism of either miss from the receipts.

## 2. Per-case attribution (fixture against each mutant, quiet and loaded)

The frozen counter prints per-mutant verdicts only, so the per-case map is from my own harness that applies the counter's `MUTANTS`/`EQUIV` tables unchanged (`source.replace(old, new)` on the pinned tool blob, which yields the same anchors) and runs `tests/fixtures/r42-drift-conditions.py` at the tip. Commands:
- `python3 -B .ufo/waves/round-42/w2/R42w2reviewer05/diag.py quiet 4` → `diag-quiet.json/.txt` (quiet; its per-case text parse was buggy, superseded by the next line)
- `python3 -B .ufo/waves/round-42/w2/R42w2reviewer05/reparse.py quiet loaded` → `attrib-quiet.txt`, `attrib-loaded.txt` (the corrected parse; use these)
- `python3 -B .ufo/waves/round-42/w2/R42w2reviewer05/diag.py loaded 4` under 16 stress processes → `diag-loaded.*`

Both passes produce **identical failing-case sets for all 19 mutants**, and identical `pass/fail` counts: `attrib-quiet.txt` = `attrib-loaded.txt`. Excerpt of `attrib-quiet.txt` (pristine: `rc=0 cases=13 pass=13 fail=0`):

```
B1    rc=1 cases=13 pass=12 fail=1   failing=fifo-record-is-refused-not-blocked
B3    rc=0 cases=13 pass=13 fail=0   failing=-
B4    rc=0 cases=13 pass=13 fail=0   failing=-
D4    rc=1 cases=13 pass=12 fail=1   failing=invalid-utf8-in-record-becomes-replacement-char
E2    rc=1 cases=13 pass=12 fail=1   failing=root-sibling-prefix-is-outside
E4    rc=1 cases=13 pass=12 fail=1   failing=gitdir-sibling-prefix-is-outside
E5    rc=0 cases=13 pass=13 fail=0   failing=-
E7    rc=0 cases=13 pass=13 fail=0   failing=-
E9    rc=0 cases=13 pass=13 fail=0   failing=-
G2    rc=1 cases=13 pass=11 fail=2   failing=list-timeout-is-reported-unreachable,timeout-of-one-is-accepted
G3    rc=1 cases=13 pass=12 fail=1   failing=default-timeout-outlasts-a-blocked-git
G4    rc=1 cases=13 pass=11 fail=2   failing=default-timeout-outlasts-a-blocked-git,list-timeout-is-reported-unreachable
G5    rc=1 cases=13 pass=12 fail=1   failing=list-nonzero-rc-is-reported-unreachable
H1    rc=1 cases=13 pass=12 fail=1   failing=root-option-is-required
H2    rc=1 cases=13 pass=12 fail=1   failing=record-option-is-required
H4    rc=0 cases=13 pass=13 fail=0   failing=-
I1    rc=1 cases=13 pass=12 fail=1   failing=symlinked-child-is-not-discovered
J9    rc=1 cases=13 pass=12 fail=1   failing=two-digit-regs-are-read-whole
M1    rc=1 cases=13 pass=12 fail=1   failing=longer-old-json-is-truncated-on-write
```

Run 2's survivors are not reproduced by any loaded per-case run here; I did not reproduce run 2's `killed=5`.

## 3. Case table: the 13 cases of `tests/fixtures/r42-drift-conditions.py`

Source: the fixture at the tip, blob sha256 `03392c7d75daaec14f7ac03f8074dd489d8ac7c7efe1d17eb340d13c7f353f45` (equals the wave-1 candidate R42executor10 byte-for-byte). Kill = mutant's failing case(s) from section 2. "Asserts" = what the case checks (exit code, stdout/stderr token, file bytes, timing). Flake risk is my assessment from the code and the loaded runs.

| case | mutants killed | asserts | flake risk |
|---|---|---|---|
| `fifo-record-is-refused-not-blocked` | **B1** (the mutant blocks; the case's `tool_run` times out at 25 s → `None` → FAIL) | rc 2 **and** stderr `REFUSAL RECORD-MALFORMED:`, tool bounded at 25 s. **Kill for B1 is a 25 s wall-clock bound**, not output. | low: pristine refuses in ~0.03 s; the mutant always blocks. |
| `root-sibling-prefix-is-outside` | **E2** (mutant: `../root2` passes the prefix test, ends as `DRIFT ABSENT`, rc 1) | rc 2 **and** stderr `REFUSAL RECORD-OUTSIDE-ROOT:` | none (deterministic). |
| `gitdir-sibling-prefix-is-outside` | **E4** (`.git` file → bare repo in `rootX`; mutant proceeds, rc 0 or 1) | rc 2 **and** stderr `REFUSAL RECORD-OUTSIDE-ROOT:` | low: depends on `git rev-parse --absolute-git-dir` on a `.git` file. |
| `timeout-of-one-is-accepted` | **G2** (mutant refuses `--timeout 1` with rc 2) | rc 1 **and** stdout token `DRIFT\tABSENT\ta` | none. |
| `default-timeout-outlasts-a-blocked-git` | **G3** (default 1 s: same `UNREACHABLE:list-timeout` line; only the **elapsed ≥ 5.0 s** clause differs). **G4** (`raise`: traceback, no DRIFT line) | rc 1 **and** token `DRIFT\tUNREACHABLE\tt\tUNREACHABLE:list-timeout` **and** `elapsed >= 5.0` s. **G3 is killed by the timing clause alone.** | **medium-low for G3**: its kill needs the mutant's case to finish in under 5 s. The receipts give job totals (4.84 s quiet; 5.27–9.11 s under load, the whole fixture) but not the case's own elapsed, so the loaded margin is not measured. The pristine side is always ≥20 s, so no false red here. |
| `list-timeout-is-reported-unreachable` | **G4** (traceback: no `DRIFT` token), **G2** (mutant rc 2 at `--timeout 1`; token absent) | rc 1 **and** token `DRIFT\tUNREACHABLE\tt\tUNREACHABLE:list-timeout` (`--timeout 1` on a FIFO HEAD) | low: a FIFO with no writer blocks git until the subprocess timeout. |
| `list-nonzero-rc-is-reported-unreachable` | **G5** (`if False:` → regs 0, `REGS-CHANGED`, token absent) | rc 1 **and** token `DRIFT\tUNREACHABLE\tu\tUNREACHABLE:list-rc=` | none. |
| `root-option-is-required` | **H1** (mutant runs with `--root .` and exits 1) | rc 2 **and** the word `required` in stderr. Does not name `--root`; the kill is the exit code 2→1 with the generic word. | none. Weak assertion: passes for any argparse-required error. |
| `record-option-is-required` | **H2** (mutant: `TypeError` traceback, rc 1; traceback is in the child's stderr, not the fixture's) | rc 2 **and** `required` in stderr. Same weakness as the root case: the kill is the exit code. | none. Weak assertion. |
| `symlinked-child-is-not-discovered` | **I1** (mutant reports `UNRECORDED lnk`) | stdout contains `DRIFT\tUNRECORDED\tu2` **and** does not contain `UNRECORDED\tlnk` | none. |
| `two-digit-regs-are-read-whole` | **J9** (mutant: `RECORD-MALFORMED` rc 2) | rc 1 **and** token `record=10 live=1` in a DRIFT line | none. |
| `longer-old-json-is-truncated-on-write` | **M1** (old 5000-byte file keeps its tail; `json.loads` fails) | rc 0 **and** the `--json` file parses as JSON with `drift == []` and a `summary` key (file bytes) | none. |
| `invalid-utf8-in-record-becomes-replacement-char` | **D4** (mutant prints the literal `\xff`) | rc 1 **and** stdout bytes contain `DRIFT\tABSENT\ta\xef\xbf\xbdb\t` and not `\xff`; the JSON `repo` equals `a\ufffdb` | none (deterministic; filesystem byte names). |
| *(no case)* | **B3, B4, E5, E7, E9, H4** killed: **0 of 6** | — | — |

Notes on the table:
- **Exit-code-only kills.** H1 and H2 are killed by exit code change (2 → 1); their `required` clause does not name the flag, so the cases are weak tests of the flag, not of argparse wording. This is the "exit code, something a mutant-equivalent could also produce" category: any tool that exits 2 with an argparse "required" error passes.
- **Timing-only kill.** G3 is killed by the 5-second elapsed clause alone; its DRIFT line is identical to the pristine tool's. This is the only case whose kill is decided by a wall-clock measurement. Under heavy load the mutant's 1-second timeout plus process start-up could approach 5 s, and that would turn G3 into a survivor (a red landing, not a false green). I did not observe that in any run.
- **Wall-clock kill.** B1 is killed because the mutant blocks past the 25 s case timeout; its output is never produced. Deterministic, not timing-sensitive in the pristine direction.
- **Byte-level kills.** M1 and D4 assert on file bytes and stdout bytes, respectively. These are behaviour (what the tool writes), not sniffing of the tool's source, so they are not in the counter's byte-presence concern.
- **Equivalents.** No case touches `--json` inside a measured tree, the `set_blocking` lines, or the `measured` list, so all six EQUIV mutants survive. This matches the population and was confirmed by 0/6 kills in every run.
- **Not covered (not in the population, so not a C3 failure):** `JSON-INSIDE-MEASURED-TREE`, `JSON-IS-RECORD`, `JSON-HARDLINKED`, `RECORD-MISSING`, `RECORD-EMPTY`, `USAGE` for `--root`, and the `--json ""` default. These are open refusal classes the counter cannot see.

## 4. Prior-battery observations (the `old_killed` leg)

- `receipts/r36-readonly-instrumented-under-load.txt`: six loaded runs of my instrumented copy of r36 (read-only check prints the snapshot diff) against `G5` and `D4` and pristine: all `rc=0`, no `=FAIL`.
- `r36probe-loaded.txt` rep 2: `G5 … fails=read-only(changed=1)` and `D4 … fails=read-only(changed=1)` (rc 1, `summary=('12','11','1')`); the same two mutants at rep 1 and in `r36probe-quiet.txt` (both reps) are clean. Pristine never failed.
- `grid-loaded2.txt`: r36 killed `J9` once (`prior=r36-worktree-drift.py`).
- So the r36 fixture produced two prior-kill events in ~20 loaded runs (`read-only` changed=1; J9 kill). Neither reproduced in six further loaded runs. The `old_killed` leg is therefore load-sensitive at a low rate; the counter's `old_killed=0` cannot be relied on under load.

## 5. Commands run and their output (verbatim SUMMARY lines)

```
python3 -B census/round-42/c3-counter.py --root <lane> --rev 3105a63b…     (run1)  SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247   exit 0
python3 -B census/round-42/c3-counter.py … (run2, under stress.py 16 procs)  SUMMARY mutants=13 killed=5 survived=8 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247   exit 1
python3 -B census/round-42/c3-counter.py … (run3, alone after stress)     SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247   exit 0
python3 -B census/round-42/c3-counter.py … (run4, concurrent with 16 stress procs)  SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247   exit 0
python3 -B .ufo/.../grid.py grid-loaded   SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247
python3 -B .ufo/.../grid.py grid-loaded2  SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=1 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247
git -C <lane> show 3105a63b…:tests/fixtures/r42-drift-conditions.py | sha256sum   03392c7d75daaec14f7ac03f8074dd489d8ac7c7efe1d17eb340d13c7f353f45
git -C <lane> show 3105a63b…:tools/souji-worktree-drift.py | sha256sum            b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6 (pinned; matches)
```

Load and kernel observations at the time of run 2 and afterwards: `/proc/vmstat` `oom_kill` read 16 at every check I made (22:33 to 22:55), so no new OOM kill occurred during my runs (the counter value predates them). `free` showed 0.6–4 GB free and 8–12 GB available, with 12 GB of 31 GB swap in use. No OOM line appeared in the kernel journal. These readings do not explain run 2.

## 6. Limits of this report

- The counter does not record the fixture's per-case output, so the cause of run 2 and of `grid-loaded2`'s prior kill could not be identified from the receipts; a fix needs the counter (frozen) to keep the failing case names, which is a named limit (N-C3b in the lesson) and not something I edited.
- The per-case attribution is my harness's, not the counter's; it uses the counter's tables verbatim and the counter's kill predicate (`rc == 1 and fail > 0 and no traceback`).
- Loaded runs measured host load from sibling seats, not my stress alone; the "load" column is the 1-minute average at start/end.
- I did not reach an idle host at any point; the specified "idle" first run was at load 24 and the third run at load 77.
- `diag-quiet.txt` carries a buggy case parse (the `\s*` regex, fixed before `diag-loaded` ran); `diag-loaded.txt` is correct. The case-level tables are in `attrib-quiet.txt` and `attrib-loaded.txt`.
- No EQUIV mutant was re-proven equivalent here (wave-1 R42reviewer04 covers that).
