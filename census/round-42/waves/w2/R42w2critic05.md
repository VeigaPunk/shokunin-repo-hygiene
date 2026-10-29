# R42w2critic05 — falsify the landed C3 fixture (sniffing and brittleness)

Seat: R42w2critic05 (critic). Lane tip attacked: `3105a63b23481fccf7df58e74d14a6681e0ea0c8`
(the working tree is byte-identical to the tip for both files: `cmp` against `git show`).
Attacked artifact: `tests/fixtures/r42-drift-conditions.py` (sha256 `03392c7d75daaec14f7ac03f8074dd489d8ac7c7efe1d17eb340d13c7f353f45`).
Pinned tool: `tools/souji-worktree-drift.py` (sha256 `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6`, verified).
Environment: uid 1000 (not root); Python 3.14.8 (`/usr/bin/python3`); git 2.56.0 (`/usr/bin/git`); strace at `/usr/bin/strace` (already installed, nothing installed or upgraded by this seat).
Scratch: `/fast/scratch/hyaku/souji-r42/R42w2critic05/` (deleted before yield; copies of every receipt are in the seat directory).
Receipts: `.ufo/waves/round-42/w2/R42w2critic05/receipts/` (`index.txt`, `run.sh`, per-scenario `.out`/`.err`, `sha256.txt`, `strace-tool-opens.txt`, `wrap-s2b.py`, `counter-tip.txt`, `nonexist-work.err`).

## Commands actually run

Setup (the fixture and tool are extracted from the tip, not the working tree):
```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 3105a63b…:tests/fixtures/r42-drift-conditions.py > $S/cand.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 3105a63b…:tools/souji-worktree-drift.py > $S/pristine-tool.py
cmp <(git … show 3105a63b…:tests/fixtures/r42-drift-conditions.py) …/tests/fixtures/r42-drift-conditions.py  -> WT_EQ_TIP_FIXTURE
cmp <(git … show 3105a63b…:tools/souji-worktree-drift.py) …/tools/souji-worktree-drift.py                  -> WT_EQ_TIP_TOOL
```
Variants (`s3/tool-ro.py` = copy chmod 0444; `s4/tool-comment.py` = copy + `printf '\n# r42w2critic05 appended trailing comment probe\n' >>`;
`s1 alt dir/nested/xq-moved.dat` = copy under a different name in a directory containing a space; sha256 of all three recorded in `receipts/sha256.txt`).
Scenario driver: `receipts/run.sh` (run as `bash run.sh`, output `receipts/index.txt`; wall time 522 s). Each scenario is
`python3 -B $S/cand.py --tool <tool> --work <dir>` unless noted. Results (verbatim from `index.txt`):

```
s0 rc=0 SUMMARY cases=13 pass=13 fail=0 fails=[] stderr-lines=0
s0 leftovers: 0
s1 rc=0 SUMMARY cases=13 pass=13 fail=0 fails=[] stderr-lines=0
s2a rc=0                      (audit-candidates.py c3, see below)
s2b rc=0 SUMMARY cases=13 pass=13 fail=0 fails=[] stderr-lines=0
s2b invocations=13 tool-arg-prefixes= 1 --record; 12 --root;
s3 rc=0 SUMMARY cases=13 pass=13 fail=0 fails=[] stderr-lines=0
s4 rc=0 SUMMARY cases=13 pass=13 fail=0 fails=[] stderr-lines=0
s5a rc=0 SUMMARY cases=13 pass=13 fail=0 fails=[] stderr-lines=0
s5a sentinels: sentinel dir=kept leftovers=keepdir,keep.txt,
s5b rc=0 SUMMARY cases=13 pass=13 fail=0 fails=[] stderr-lines=0
s6a rc=0 SUMMARY cases=13 pass=13 fail=0 fails=[] stderr-lines=0
s6b rc=0 SUMMARY cases=13 pass=13 fail=0 fails=[] stderr-lines=0
s7 rc=0 SUMMARY cases=13 pass=13 fail=0 fails=[] stderr-lines=0
s8-1 … s8-12: rc=0 SUMMARY cases=13 pass=13 fail=0 fails=[] stderr-lines=0   (all twelve; receipts/s8-all.out)
stray-procs: 0
```

Scenario specifics:
- (1) different name and directory: `python3 -B $S/cand.py --tool "$S/s1 alt dir/nested/xq-moved.dat" --work $S/s1/w` (tool path contains a space).
- (2a) `python3 -B .ufo/waves/round-42/audit-candidates.py c3 $S/cand.py --lane <lane> --scratch $S/s2a` → receipts/s2a.out:
  `wrapper run rc=0 cases=13 fail=0 invocations=13` / `AUDIT c3 findings=0` (static leg: no C3-STATIC or C3-ANCHOR finding).
- (2b) own logging wrapper `receipts/wrap-s2b.py` (appends argv to `calls.log`, then `runpy`s the pristine tool): 13 invocations, all with `--record` or `--root` first, 13/13 pass.
- (5a) `--work "$S/s5a/non empty"` with pre-existing `keep.txt` ("sentinel") and `keepdir/`: 13/13 pass, both sentinels survive, the fixture leaves only its own pre-existing entries.
- (5b) `--work "$S/s5b/work with spaces"`: 13/13 pass.
- (6a) `(cd / && python3 -B $S/cand.py --tool $S/pristine-tool.py --work $S/s6/w)`: 13/13 pass.
- (6b) `(cd "$S/s6 cwd" && python3 -B $S/cand.py --tool ../pristine-tool.py --work $S/s6b/w)` (relative tool path, spaced cwd): 13/13 pass.
- (7) `env -u HOME PATH=/usr/bin:/bin python3 -B $S/cand.py --tool $S/pristine-tool.py --work $S/s7/w`: 13/13 pass.
- (8) twelve concurrent copies, each with its own `--work` (`$S/s8/w<i>`): 12 of 12 `rc=0 pass=13 fail=0`.

Static and kernel-level sniff checks:
- `grep` of the fixture for tool-, hash-, label- and environment-reading tokens (`open(`, `read`, `environ`, `argv`, `sha`, `hashlib`, `mut-`, `pristine`, `b2a6`, `TMPDIR`, `HOME`, `PATH`, `tool`, `anchor`, `REFUSAL`). Every hit is one of: a write of the fixture's own scenario file (`put`, `open(path, "wb")`); a read of the fixture's own `--json` output (`json.loads` on `target`, `js`); `self.tool` used only as the argv element of `subprocess.run`; `os.environ.get("PATH", …)` (the only host environment key read; `TMPDIR`, `HOME` and the `GIT_*` keys are *set* for children, never read). No digest, no `mut-`/`pristine` name, no mutant anchor, no label read, no tool file open.
- `strace -f -e trace=openat,execve -o out/strace-s0.txt python3 -B cand.py --tool pristine-tool.py --work st/w` (rc 0, `SUMMARY cases=13 pass=13 fail=0`): the fixture root process (pid 219312) opens the tool path **0** times; the 26 `openat` lines naming `pristine-tool.py` belong to child pids that exec the tool as a script (Python reading its own source). Receipt: `receipts/strace-tool-opens.txt`.
- The audit-candidates static leg (C3-STATIC regex set and the C3-ANCHOR fragment check) reports zero findings on the fixture.

Tip counter (re-measurement, run once, read-only on the lane):
```
python3 -B census/round-42/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 3105a63b23481fccf7df58e74d14a6681e0ea0c8 --scratch $S/counter
SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247
counter rc=0
```

Non-scenario observation (usage, outside the listed eight):
```
python3 -B cand.py --tool pristine-tool.py --work "$S/does-not-exist"   -> rc=1, FileNotFoundError traceback (receipts/nonexist-work.err)
```

## Table

| scenario | result | verdict |
|---|---|---|
| static grep of fixture for tool bytes, hashes, labels, anchors, `mut-`/`pristine` names, counter env keys | no read of tool file, digest, label or anchor; only own outputs and `os.environ["PATH"]` | sniff: none (clean) |
| strace of fixture process tree | root pid opens tool 0 times; 26 opens are child python processes executing the tool | sniff: none (clean) |
| (1) pristine tool, different file name and spaced directory | 13/13 | ok |
| (2a) audit-candidates.py c3 (frozen lane audit) | `AUDIT c3 findings=0`, wrapper 13 invocations | sniff: none (clean) |
| (2b) own logging wrapper | 13 invocations, 13/13 | ok |
| (3) pristine tool read-only 0444 | 13/13 | ok |
| (4) pristine + appended trailing comment (sha differs) | 13/13 | ok (fixture reads no bytes) |
| (5a) `--work` existing non-empty directory | 13/13; pre-existing sentinel and dir preserved | ok |
| (5b) `--work` path with spaces | 13/13 | ok |
| (6a) cwd `/` | 13/13 | ok |
| (6b) cwd with space, relative `--tool` | 13/13 | ok |
| (7) `HOME` unset, `PATH=/usr/bin:/bin` | 13/13 | ok |
| (8) twelve concurrent copies | 12/12 `pass=13 fail=0` | ok |
| tip counter re-run | `mutants=13 killed=13 … anchors=ok` (target met) | ok |
| `--work` directory does not exist | traceback `FileNotFoundError`, rc=1, no usage message | brittle-minor (usage only; the counter always passes an existing directory, so it cannot trip the counter) |

## Verdict

No sniffing. The fixture reads nothing of the tool except through its own subprocess invocation; the byte-changed copy (4), the renamed and relocated copy (1), the read-only copy (3), the logging wrapper (2a, 2b) and the `strace` attribution all show it depends on the tool's behaviour, not its bytes, names, digest or location.

No brittleness under the requested variants: (1)-(8) all 13/13, and the concurrent batch of 12 passed. One usage-level brittleness exists (a non-existent `--work` directory gives a traceback instead of a message); the frozen counter always supplies an existing directory, so the re-measurement is not affected.

Residual risk, not observed as a failure: three cases depend on wall-clock margins (`case_timeout_of_one_is_accepted` and `case_list_timeout_is_reported_unreachable` run the tool with `--timeout 1`; `case_default_timeout_outlasts_a_blocked_git` asserts `elapsed >= 5.0`). All of them passed in the twelve-way concurrent batch and the 522 s serial suite on this host, but no run loaded the host beyond twelve processes, so a much slower host could flip the `--timeout 1` cases. This is a named limit for the L1 to record, not a defect that changes the verdict.

Limits of this seat: no mutation was re-run (the counter's own kill table was re-measured once and matches); the static grep is a token scan, the strace attribution covers the one scenario traced; nothing was edited, committed or landed; no tool was installed or upgraded.

Verdict: C3 fixture at 3105a63b — sniff: none found; brittle: none under (1)-(8); one usage-level brittleness (missing `--work` directory) recorded as minor.
