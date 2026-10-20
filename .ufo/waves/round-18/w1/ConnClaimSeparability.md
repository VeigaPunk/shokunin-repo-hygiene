STATUS: DONE — C1, C2, and C3 are separable on disjoint oracles; the drafted C1 recheck and an unconditional Q25(b) are not.

Axes: calibration 7 (lowest; this seat), operability 8 (C1), coverage 8 (C3). One move below keeps a calibration count causal. It leaves the census watchdog and the process-residue census on their own files.

Verdict: **partial**. Each claim can be verified with the other two reverted if, and only if, its counting command never calls the other claims' tools and C2's new findings survive two existing pins. A joint tip `findings=0` does not verify C2. `ScribeSkillRules.md:50` and `:60` wire C1's green to C3.

## Proposed move

Count each claim on an oracle that still runs when the other two diffs are absent. Inside C2, keep the two new findings off the round-17 replay pin and off `check_carry`'s exit 2:

1. Run the `LG-DANGLING-PTR` scan before `check_carry`. At `b576341` there is no `.ufo/waves/round-18/*.md`, so `check_carry` raises and `evaluate` drops every finding already collected (`tools/souji-landing-gate.py:374-375`, `:697-699`). If the pointer scan found one or more dangling tokens, return those rows and exit 1, with `checked_reports=0` and a `checked_tokens` counter greater than 0. If the scan found none and the wave directory is empty, keep exit 2. That leaves `tests/fixtures/r16-landing-gate.py:454-455` (`missing-wave-dir`, round 77, cited `tools/ok.sh` present) on exit 2.
2. Grandfather exact `(record path, measured_commit)` pairs that already exist at `b576341`. A non-resolving `measured_commit` is `LG-FROZEN-MEASURED` for every other pair. The live pair is `tests/fixtures/r14-cache-frozen/record.json` = `0123456789abcdef0123456789abcdef01234567`, and `expected.json` points at that record (`"record": "record.json"`). The same hash is in that file at `cc21683`, `b410186`, `6ff91f5`, and `79bbe7a`. The selftest sentinel `"0" * 40` (`tools/souji-landing-gate.py:844`) is the same class: `clean-pass` expects exit 0 and `checked_measured=0` (`:909-912`). An r18 fixture case uses a hash that is not on the list.
3. C1's survivor count is `ps` / `/proc` inside `tests/fixtures/r18-census-bounded.py`. C3's count is that fixture's own planted sleepers against its own `/proc` walk. The C2 delta is the `LG-DANGLING-PTR` line count plus `checked_tokens` of the new gate on `b576341` versus a C2-only revision. Tip `LG-DANGLING-PTR=0` is a landing barrier, recorded separately from C2's delta.

## Contradiction (do not collapse)

- The goal's before-command is `changed gate --rev b576341 --round 18`. On today's `evaluate`, that command exits 2 and prints no finding rows, because round-18 reports are not in the commit. `git ls-tree -d --name-only b576341 .ufo/waves` lists round-13 through round-17 only.
- Q25(b) says a dangling `measured_commit` is `LG-FROZEN-MEASURED` (`corpus/QUALITY.md:64`; open at `tools/souji-landing-gate.py:548-569`). `LG-DANGLING-PTR` is round-gated so `census/round-17/gate-replays-expected.json` stays byte-identical. Those two requirements disagree on `r14-cache-frozen`: r14-landing and r16-landing are exit 0 with `findings: []` in that JSON (`:18-22`, `:53-58`). Flagging the placeholder adds a finding at rounds 14 and 16. Round-gating Q25(b) leaves the known placeholder invisible at the rounds the replay pin covers.
- Grandfathering the base pairs keeps the JSON identical and flags every new dangling hash. It does not by itself flag the r14 placeholder. The lesson has to name that pair as a bounded exemption. Calling Q25(b) closed on the historical corpus would overclaim.

## Can each claim be verified with the others reverted?

| Claim | Revert the other two | Holds when |
|---|---|---|
| C1 operability | C2 gate diff and C3 `tools/souji-proc-census.sh` absent | The bounded fixture asserts the timeout row, stderr, exit 0, and zero processes in its own session. `r17-census-hygiene.py`, `r15-census-config.py`, and `r14-census-boundary.py` stay at their recorded summaries. |
| C2 calibration | C1 census diff and C3 proc-census absent | The new gate is run against `b576341` and against a commit that contains only the gate, the exemption list, the measured-commit allowlist, and the R2 pointer retargets. `checked_tokens>0`. Replay JSON unchanged. |
| C3 coverage | C1 watchdog and C2 gate absent | The proc-census fixture plants sleepers, compares pid sets to its own `/proc` walk, and the surface count is a diff of `PROVINCE.md` residue bullets. |

Reverted-verification fails if C1's green arm is `tools/souji-proc-census.sh` (`ScribeSkillRules.md:50`), or if one matrix requires both r18 suites to be valid (`ScribeSkillRules.md:60`, `census/round-18/c1-matrix.json` covering `r18-proc-census`), or if C2's only accepted number is tip exit 0.

## Shared files

Disjoint implementation files, any landing order: `tools/souji-census.sh` (C1; `emit_census` `:1394-1416` calls `census_one` in `$(...)` at `:1403`; no `repo-timeout` / `set -m`), `tools/souji-landing-gate.py` (C2), `tools/souji-proc-census.sh` (C3; absent at `b576341`, `ls-tree` empty), `corpus/pointer-exemptions.tsv` (C2, new).

`guard_git_files` (`:546-585`) classifies `info/attributes` with `stat -L` and returns. The C1 hang is a swap after that return. `r15-census-config.py` `case_03` already expects `r-inc-fifo` to finish exit 0 with stderr `config-unsupported` and an `error` row (`:1054-1073`, `:1124-1130`). The product watchdog has to leave that diagnostic in place. The host leak file's `r-inc-fifo` `rev-parse` lines are older census binaries (`census/round-18/leaked-procs-before-1631.txt:1-2`), which is why `r15` `run_tool` still needs a process-group kill on the timeout path (`:781-791`; `r14-census-boundary.py:392-402` is the same `subprocess.run` shape; `r17-census-hygiene.py:293-318` already uses `start_new_session` and `killpg`).

Scanned by the new pointer check, so they are one barrier commit: `SKILL.md`, `SCORECARD.md`, `PROVINCE.md`, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/knowledge/*.md`, `corpus/lessons/round-18.md`, and the round-18 section of `LOG.md`. `CITED_PATH_RE` (`souji-landing-gate.py:77-78`) already requires a registry-cited `tools/*.sh`, `tests/fixtures/*.py`, or `census/round-N/*.{sh,py}` to exist and parse. `LG-DANGLING-PTR` is the wider net (json, txt, md, the knowledge entry).

Known dangling tokens at this base, from the files named in the goal: `SKILL.md:163` and `:165` cite `census/round-17/gate-replays-ddb7347.json`; `corpus/knowledge/jj-colocation-receipts.md:2`, `:44`, `:126`, and `:148` cite `census/round-17/jj-receipts-ddb7347.txt`. Those retargets are C2's delta. R3 is the operability cell at `SCORECARD.md:15` ("22 repos"). R4 is `corpus/QUALITY.md` Q7. R1 is `tools/souji-quarantine.sh:246-247` (`--as souji`) and is outside these three claims; it shares no oracle with them.

`census/round-17/gate-replays-expected.json` is not edited by any claim.

`tests/fixtures/r16-landing-gate.py:68` sets `ROUND = 77`, so a round≥18 check runs on every synthetic case. `clean-all-green` (`:486-488`) expects exit 0 and `SUMMARY findings=0`. Its cited `tools/m.sh` and `tools/m.py` are written into the synthetic repo (`:459-461`). Absent `SCORECARD.md` / `PROVINCE.md` / `QUALITY.md` / `README.md` / `corpus/knowledge/*` add zero tokens. Treating a missing authority file as exit 2 turns this case red. The in-tool selftest passes `--round 16` (`souji-landing-gate.py:940`, `:1318`), so it does not exercise `LG-DANGLING-PTR`.

## Ordering constraint

1. Land the disjoint tools, the exemption list, the measured-commit allowlist, and the r14/r15 timeout-path `start_new_session` + `killpg` edits in any order.
2. One barrier commit after every path those edits cite is in the same revision: the eight scanned doc surfaces above. `SCORECARD.md:15` is rewritten in that commit with the r17 "22 repos" cell corrected to 21 repositories in the same sentence as the r18 operability claim. A later C1 rewrite of that cell reintroduces R3 if the 21 is left behind.
3. The revision in step 2 is the only one where tip `LG-DANGLING-PTR=0` is a landing invariant. Record it beside C2's delta, not as the delta.
4. Do not commit `census/round-17/gate-replays-expected.json` changes. Do not point the C1 fixture at `souji-proc-census.sh`. Do not make "all r18 suites valid" the counting command for either C1 or C3.

## Counting commands

These do not call each other. None of them was run in this seat (the probe rule forbids running `souji-census.sh`, the landing gate, and `souji-proc-census.sh` against a real tree).

C1, valid with C2 and C3 reverted:

```shell
python3 tests/fixtures/r18-census-bounded.py --tool tools/souji-census.sh
```

The fixture's own oracle: the swapped repo's row is `<repo>\t0\t0\t0\t0\t\terror`, stderr contains `souji-census: repo-timeout <N>s <repo>`, exit 0, neighbour rows match a run of the same binary without the shim, and after return `ps -eo pid,pgid,sess,stat,wchan,args` shows no process in that case's session. No-harm companions, same binary, C3 not imported:

```shell
python3 tests/fixtures/r17-census-hygiene.py --census tools/souji-census.sh
python3 tests/fixtures/r15-census-config.py --tool tools/souji-census.sh
python3 tests/fixtures/r14-census-boundary.py --tool tools/souji-census.sh
```

Recorded baselines to keep, from `SCORECARD.md:15` (not re-measured here): hygiene 29/0, r15-config 20/0, r14 namespace 12/0.

C2, valid with C1 and C3 reverted. Count `^LG-DANGLING-PTR` lines and `checked_tokens`. The exit code is 2 until round-18 reports exist; the line count is the measurement.

```shell
python3 tools/souji-landing-gate.py --root <checkout> --rev b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 --round 18
python3 tools/souji-landing-gate.py --root <checkout> --rev <c2-only> --round 18
```

L1's hand sweep at this base was 281 tokens, 18 unresolved. The gate's own `checked_tokens` and `LG-DANGLING-PTR` lines replace that hand number once the scan exists. Before must be greater than 0 on this same binary or a later 0 is vacuous. Replay identity, still with C1 and C3 absent:

```shell
python3 census/round-17/gate-replays.py --gate-rev <c2-gate-rev> --output <new.json>
```

Diff against `census/round-17/gate-replays-expected.json` is empty. External no-harm: `python3 tests/fixtures/r16-landing-gate.py --tool tools/souji-landing-gate.py` with `clean-all-green` still `findings=0`. `python3 tools/souji-landing-gate.py --selftest` stays the round-16 parse/pin/carry count; it is not the dangling-pointer count.

C3, valid with C1 and C2 reverted:

```shell
python3 tests/fixtures/r18-proc-census.py --tool tools/souji-proc-census.sh
```

Planted pid set equals the fixture's independent `/proc/<pid>/{stat,cmdline,cwd,wchan}` walk. `strace -f -e trace=kill,tkill,tgkill` on the probe is empty. Surface count: residue classes named in `PROVINCE.md` at `b576341` are 0 (work surfaces end at the jj bullet, `:21-30`; adjacency `:46-47` is "never on processes"). After is the count of residue classes that bullet gains. `wc -l census/round-18/leaked-procs-before-1631.txt` is 58 lines of C1 fixture residue; it is host evidence, not C3's after number.

## Risks

- Grandfathering `r14-cache-frozen` leaves that one dangling hash unflagged. The lesson names the pair. A new hash not on the allowlist is the Q25(b) positive case.
- A pointer scanner that exit-2s on a missing `SCORECARD.md` fails `clean-all-green` at round 77.
- `set -m` left on in the census parent, or `start_new_session` around r14/r15's `strace -f`, can move those fixtures' stderr or trace oracles. The timeout path kills the group; the success path keeps today's stdout. Re-count r14 and r15 after that edit; a moved trace is a C1 no-harm failure, not a C2 or C3 result.
- Exempting a prefix (`census/`) zeros the before count and hides the `ddb7347` tokens. Exemptions are exact paths.

## Commands run

```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -d --name-only b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 .ufo/waves
.ufo/waves/round-13
.ufo/waves/round-14
.ufo/waves/round-15
.ufo/waves/round-16
.ufo/waves/round-17
```

`ls-tree` of `.ufo/waves/round-18` and of `tools/souji-proc-census.sh` at that rev printed nothing (exit 0).

```text
git grep 0123456789abcdef0123456789abcdef01234567 b576341 -- tests/fixtures census
tests/fixtures/r14-cache-frozen/record.json:6
```

The same record line is present at `cc21683`, `b410186`, `6ff91f5`, and `79bbe7a`. It is absent at `a31642d` (r13 replay).

```text
git show cc21683:tests/fixtures/r14-cache-frozen/expected.json
git show 6ff91f5:tests/fixtures/r14-cache-frozen/expected.json
```

Both contain `"record": "record.json"` and pin `record.json` under `files`. `check_frozen_pins` therefore loads `measured_commit` (`souji-landing-gate.py:474-475`, `:538-569`).

Reads: `souji-census.sh:546-585`, `:1261-1416`, `:2038-2049`; `souji-landing-gate.py:1-123`, `:368-425`, `:538-599`, `:607-702`, `:814-950`, `:1040-1127`; `r16-landing-gate.py:67-68`, `:81-84`, `:165-195`, `:450-495`; `r15-census-config.py:757-807`, `:1054-1146`; `r17-census-hygiene.py:271-325`; `r14-census-boundary.py:370-402`; `SKILL.md:147`, `:158`, `:163-165`; `SCORECARD.md:15`; `PROVINCE.md:19-47`; `QUALITY.md:64`; `jj-colocation-receipts.md:2`; `gate-replays-expected.json:9-59`; `leaked-procs-before-1631.txt:1-2` (file length 58); `ScribeSkillRules.md:49-60`; `souji-quarantine.sh:246-247`.

No tool installed. pacman was not used.
