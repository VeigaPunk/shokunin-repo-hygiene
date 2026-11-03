# S56sentinel01 — adversarial security review of the r56 v5 counters (souji round 56, wave w1)

Role: sentinel (security review of the counters as tools). Seat: `S56sentinel01`.
Measured revision: `cce21b555a617cadda782613ec1e9d3a0c12ac83` (base `fafe371694fea41c5d23f63083865d5ccf3f1d36`).
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` (read-only). Scope: `census/round-56/c1-counter.py`,
`census/round-56/c2-counter.py`, `census/round-56/fixtures/build-fixtures.py` at the freeze commit.

## 0. Preconditions (all verified before probing)

Frozen pins, verified with `sha256sum` on the bytes installed into my scratch (copies, never edits;
`receipts/pins.txt`): C1 `975d3520…bbf179`, C2 `56082011…259cb8`, builder `2f26d6aa…c30b85a`,
expected TSVs `48a7cc0e…c5bfb` / `90517c4d…841b3` — all match the preregistration. The v4 before-arm bytes
(`944feafa…21a2`, `e4eb34e6…4568c`) were not needed for this surface and were only pin-checked.
Environment: `strace 7.2`, `git 2.56.0`, `Python 3.14.8`, kernel `7.2.11-arch1-1`. No tool was installed or
upgraded (no `pacman`, no `uv`, no binary fetch).

Method: every probe runs the frozen counter **from a sha256-identical copy** in
`/fast/scratch/hyaku/souji-r56/S56sentinel01/inst/`, against fixture repositories built in my own scratch
(`repos/F1-HONEST-TIP`, `repos/F12b-LOG-FILED`, `repos/FH-HONEST` via the committed `build_one`, plus
hand-built attack repos). Every fixture repo asserted `git -C <dir> rev-parse --show-toplevel == <dir>`
before its first commit (`receipts/inputs-args-replace.txt`, `ASSERT-OK` set in the transcript). No lane,
fleet or sibling file was written; no frozen byte was edited; nothing was committed outside my scratch.

Healthy-instrument controls (context, not my claim): C1 real lane at `cce21b55` exits 0 with
`unfiled=0 … recomputed=79`; C2 real lane at `cce21b55` with the pinned tool digest exits 0 with
`entries=49 … tool_pin=ok`; C1 selftest prints `SELFTEST pass cases=33`, exit 0
(`receipts/c1-selftest-33-cases.txt`). So each attack below is measured against a counter that is intact
and passing.

## 1. Threat model used

The counter is an offline audit instrument run by an operator over a repository whose **committed bytes are
not trusted**: `SCORECARD.md`, `census/round-51/preregistration.txt`, `corpus/SOURCES.md`, `LOG.md`,
`corpus/README.md`, the capture/receipt files. Attack surfaces examined, as assigned:
(i) the input path (blob size, argument injection, revision shape, repository-local config and attributes
that could make `git show` / `git diff --numstat` execute something or lie);
(ii) writes (does the default run write anything, and does the selftest stay inside `--work`);
(iii) output (does committed text reach the terminal unfiltered);
(iv) the selftest's fixture builder under `--work` (symlink following / containment).

## 2. Results — every attack, with receipt

Legend: **NONE** = attempted, defence held (receipt shown); **LOW/MEDIUM** = named limit, routed to r57.

| # | Attack | Result | Class |
|---|---|---|---|
| A1 | 50 MB committed `SCORECARD.md` (52,429,066 B, 699,050 lines) as `--rev` | 0.76 s, 319,544 KB RSS, exit 0. No time blow-up; memory ≈ 6.1× input, no size gate | LOW |
| A2 | N `R52-CORRECTION` lines in `SCORECARD.md` (line-number computation is O(N·file)) | 5k 0.66 s → 10k 2.43 s → 20k 9.46 s → 40k 39.24 s (≈×4 per doubling, O(N²)); extrapolated ≈ 6–10 h for a 50 MB all-correction file | **MEDIUM** |
| A3 | `--rev HEAD` / `--rev <tag>` / option-shaped `--rev` / `--root=-x` / `--root` with `\n` | exit 2 every time: 40-hex fullmatch (c1 lines 612, 619) + argparse; `Path(ns.root).resolve()` (line 622) absolutizes `-x`, so no leading dash reaches `git -C` | NONE |
| A4 | committed `.gitattributes` + repo-local `diff.evil.textconv`, `filter.evil.clean/smudge`, `diff.external` | no command executed by the counter (marker log 0 lines); `git show` returns the raw blob; `--numstat` counts the real 2 deleted lines. Only the `-diff` binary attribute changes the finding **name** (`DELETIONS-UNREADABLE-BINARY`), exit stays 1 | NONE (exec) / LOW (name) |
| A5 | repo-local `core.fsmonitor=<script>` and `core.hooksPath=<dir with hook>` | counter's `-c core.fsmonitor=false -c core.hooksPath=/dev/null` override repo-local config (`config --get` → `false`, `/dev/null`); positive control without the overrides runs both (`TEXTCONV_RAN`, `HOOK_RAN`) | NONE |
| A6 | default (non-selftest) run trace: C1 and C2 on the real lane | only write-mode syscalls are 12 (C1) / 3 (C2) `openat("/dev/null", O_RDWR)`; zero `mkdir`/`unlink`/`rename`; targeted lane file hashes unchanged; `find -newer` on the lane immediately after the run = 0 | NONE |
| A7 | selftest under `strace -f` (33 fixtures) | 0 absolute write paths outside `--work` (excluding `/dev/null`); 659 relative write paths, all resolving inside the fixture cwd, none with `..`; zero `/tmp`/`/var/tmp` writes; `.pyc` = 0 under the canonical `-B` | NONE (normal path) |
| A8 | `--work/c1-fixtures` is a symlink to an outside directory | one fixture directory **is created outside `--work`** (`F1-HONEST-TIP/.git`, 18 files, no fixture content), then the builder's toplevel assertion aborts the run (exit 1) | LOW |
| A9 | `--work` itself is a symlink (honest invocation) | same mismatch → the honest selftest **falsely fails** (exit 1) after creating the fixture dir at the resolved target | LOW |
| A10 | dangling symlink at `work/c1-fixtures`; symlink at `work/c1-fixtures/F1-HONEST-TIP`; `--work` a regular file | `FileExistsError` / `rmtree` "Cannot call rmtree on a symbolic link" / `NotADirectoryError`; exit 1, **no write** outside | NONE |
| A11 | committed text carrying terminal control sequences (C1 correction path token; C2 capture header) | raw ESC/CSI bytes printed by both counters; a rendered screen shows a FINDING line erased and replaced with `NO-FINDINGS` (exit stays 1) | **MEDIUM** |
| A12 | `git replace` ref forging the `SCORECARD.md` blob | counter reads the original (`stated=78`), plain `git show` reads the forgery (`(79)` ×1); `GIT_NO_REPLACE_OBJECTS=1` holds | NONE |
| A13 | C2 `--capture` = `../../etc/passwd`, `/etc/passwd`, `-p`, `census/../../../../etc/hostname` | all refused by `git show <rev>:<path>` → `PRISTINE FAIL`, exit 1; no file read outside the tree | NONE |
| A14 | repo-local `trace2.eventTarget` / `trace2.normalTarget` / `trace2.perfTarget` | git ignores trace2 keys from repo config (0 files created); env-driven control writes 1,552 B, proving the keys are otherwise live | NONE |
| A15 | selftest **without** `-B`: builder import (importlib, C1 line 532 / C2 line 349) | writes `fixtures/__pycache__/build-fixtures.cpython-314.pyc` next to the builder, i.e. outside `--work`; with `-B` 0 pyc | LOW |
| A16 | 50 MB committed capture for C2 (1,941,807 rows) | 1.18 s but **1,183,596 KB RSS** (≈22.6× input); no size gate | LOW |
| A17 | `git` call exceeding `timeout=120` (c1 line 181, c2 line 133) or `git` absent | [INFERENCE from frozen lines: `TimeoutExpired`/`FileNotFoundError` have no handler, so the run dies with a traceback and rc 1, not the documented rc 2] — not reproduced | LOW |
| A18 | LOG.md pair annotations that each match a pair filing (2 `git show` per flagged line, c1 lines 519–524) | linear with a large constant: 100 lines 0.16 s / 210 `git` execve; 400 lines 0.55 s (≈2 subprocesses per line); part of the same "no aggregate work budget" limit | LOW (INFO) |

## 3. Findings

### F1 — MEDIUM — unbounded, quadratic CPU on committed correction lines (C1)
**Exploit path.** Anyone who can commit to the audited repo writes a `SCORECARD.md` whose tip is many
`R52-CORRECTION …` lines. For every regex match the counter rescans the whole correction string to derive
the line number (`c1-counter.py:331` and `:335`: `corr.count('\n', 0, m.start())`), so the run is
Θ(N · bytes). The audit then never returns in the round's budget; a CI job or a seat that waits for the
counter times out, and the tempting operator action is to skip the check.
**Evidence.** `receipts/quad-times.txt` — 5k 0.66 s / 10k 2.43 s / 20k 9.46 s / 40k 39.24 s for files of
265 kB / 530 kB / 1.06 MB / 2.12 MB (an earlier pass on the same fixtures measured 0.73 / 2.79 / 13.49 /
64.25 s). Zero findings in all four runs, so the cost does not depend on the attacker's line being invalid.
Extrapolation to a 50 MB correction file (≈874k lines): ≈ 6–10 h [INFERENCE from the measured ≈4× per
doubling]. No aggregate deadline exists; `timeout=120` applies per `git` call only (c1 line 181).
**Impact.** Denial of the audit run (availability), not of a host service; no privilege boundary crossed.
**Smallest remediation.** Compute the line number in one pass: precompute newline offsets once (or advance
a running offset while iterating `finditer`), which makes the loop O(bytes); optionally cap the correction
file at a named `CANNOT-EVALUATE` size.

### F2 — MEDIUM — committed text is printed verbatim: terminal control-sequence injection (C1 **and** C2)
**Exploit path (C1).** A committed line
`R52-CORRECTION \x1b[2K\x1b[1G\x1b[31mSPOOFED\x1b[0m:5 stale=78 recomputed=79` matches `CORR_RE`, whose
`(\S+)` path group accepts ESC (ESC is not whitespace). The detail is formatted with `%s`
(`c1-counter.py:394` and `:417`) and printed raw (`finding()` at `:302–304`, flushed at `:624`).
A second line whose path token starts `\x1b[1A\x1b[2K\x1b[1GNO-FINDINGS\x1b[K` moves the cursor up,
erases the previous FINDING line and rewrites it.
**Exploit path (C2).** A committed capture header `# TOOL_SHA256=\x1b[2K\x1b[1GEVIL<64hex>` is echoed raw by
`c2-counter.py:265–266` and by the `CAPTURE-RECEIPT-MISMATCH` detail at `:313–314`; `# COUNT
\x1b[31mtrk\x1b[0m=2` reaches the terminal through `:278` (`COUNT %s …`).
**Byte sequences that reach the terminal** (from committed bytes): `1b 5b 32 4b` (`CSI 2K`, erase line),
`1b 5b 31 47` (`CSI 1G`, column 1), `1b 5b 31 41` (`CSI 1A`, cursor up), `1b 5b 4b` (`CSI K`, erase to
end), `1b 5b 33 31 6d` / `1b 5b 30 6d` (SGR). OSC forms (`1b 5d …`, e.g. window title, hyperlink,
clipboard) are equally `\S`-compatible and therefore reachable [INFERENCE]; only CSI was measured.
**Evidence.** `receipts/c1-terminal-injection-raw.txt` (605 B, two FINDING lines, `ESC` count 2),
`receipts/c2-terminal-injection-raw.txt` (751 B, two FINDING lines, `ESC` count 2). Rendered through a
minimal CSI interpreter the C1 stream displays `NO-FINDINGS` where the first FINDING line was; 1 of 2
`FINDING` lines is visible afterwards while the process still exits 1.
**Impact.** Spoofing of the instrument's human-readable report — the exact artifact a seat reads to decide
whether to file a correction. The exit code and the unrendered bytes stay honest, which is why this is not
HIGH; but an operator who trusts the terminal sees a clean verdict.
**Smallest remediation.** Render every committed-derived string with `%r`/`ascii()` (or emit JSON) in
`finding()` details: c1 `:394`, `:417`, `:424`; c2 `:266`, `:314`, `:323`, `:327`, `:278`.

### F3 — LOW — selftest can create one `.git` skeleton outside `--work` through a symlinked `<work>/<kind>-fixtures`
**Exploit path.** `fdir = work / 'c1-fixtures'; fdir.mkdir(parents=True, exist_ok=True)` (c1 `:551–552`, c2
`:368–369`) succeeds silently when `c1-fixtures` is a symlink to an existing directory, so `build_one` runs
`git init` in the target. The builder's containment check (`build-fixtures.py:259–260`) compares git's
resolved toplevel with the unresolved path and aborts — but only **after** the directory and `.git` exist
outside `--work`.
**Evidence.** `receipts/symlink-and-bytecode.txt` V-a: `fixture toplevel mismatch …/outside/F1-HONEST-TIP !=
…/work/c1-fixtures/F1-HONEST-TIP`, exit 1; outside holds 18 files, all inside `.git/`, 0 fixture files.
**Impact.** Writes an empty repository skeleton outside the declared write root, then stops. Needs a
pre-existing symlink in the operator's `--work` (e.g. a shared scratch dir) — not attacker-reachable from a
repo under audit.
**Smallest remediation.** Refuse symlinked components: `p = work.resolve(); if (p/'c1-fixtures').is_symlink():
CANNOT-EVALUATE`, or compare `os.path.realpath(fdir)` to `realpath(work)/'c1-fixtures'` before `mkdir`.

### F4 — LOW — a symlinked `--work` makes the honest selftest falsely fail
**Evidence.** `receipts/symlink-and-bytecode.txt` V-b: the same toplevel mismatch fires for a benign
`--work` given through a symlink (`…/worklink` vs `…/real`), exit 1, after creating
`real/c1-fixtures/F1-HONEST-TIP`. Operability limit, same root cause as F3. Smallest remediation: resolve
`--work` once at entry and use the resolved path for both `mkdir` and the builder's toplevel comparison.

### F5 — LOW — the selftest writes a `.pyc` outside `--work` when `-B` is omitted
**Evidence.** `receipts/symlink-and-bytecode.txt` A15: importing the builder through `importlib` (c1 `:532`,
c2 `:349`) writes `fixtures/__pycache__/build-fixtures.cpython-314.pyc`; `python3 -B` writes 0. Every frozen
command line in the preregistration and `run-matrix.sh` uses `-B`, so this contradicts the docstring's
"writes nothing outside `--work`" only for a non-canonical invocation — but then the write lands in the lane
(`census/round-56/fixtures/__pycache__/`), i.e. in frozen territory.
**Smallest remediation.** `sys.dont_write_bytecode = True` before `exec_module` (or import the builder with
`SourceFileLoader.get_code` / `compile`+`exec`), so the guarantee does not depend on the caller's flag.

### F6 — LOW — no input-size gate; memory amplification 6× (C1) / 22.6× (C2)
**Evidence.** C1: 52,429,066 B `SCORECARD.md` → 319,544 KB RSS, 0.76 s (`receipts/quad-times.txt` big50
line). C2: 52,429,266 B capture → 1,183,596 KB RSS, 1.18 s (`receipts/c2-50mb-capture-time.txt`). Both are
linear, but a repository can commit a much larger blob (the counters accept any size), so a 500 MB capture
predicts ≈11 GB RSS → OOM, which is a crash rather than the documented exit 2.
**Smallest remediation.** A named size gate (`CANNOT-EVALUATE input exceeds N bytes`) on the four blobs C1
and the capture/receipt C2 read; stream the record/registry instead of materialising them.

### F7 — LOW — repository attributes can rename a real deletion to `DELETIONS-UNREADABLE-BINARY`
**Evidence.** `receipts/attributes-exec.txt`: with a committed `.gitattributes` containing
`SCORECARD.md -diff`, `git diff --numstat` returns `-\t-\tSCORECARD.md` and the counter reports
`DELETIONS-UNREADABLE-BINARY` instead of `DELETED-LINES SCORECARD.md deletions=2`. Exit stays 1, so the
rewrite is still refused; only the finding name is wrong. Without `-diff`, the count is exact (`0 2`).
**Impact.** A repo can choose *which* refusal it gets, not whether it is refused. Named limit; the
already-frozen `DELETIONS-UNREADABLE-BINARY` id is the observable, so this is a documentation item for r57
rather than a code bug.

### F8 — LOW ([INFERENCE]) — a hung or missing `git` reports as a finding, not as could-not-evaluate
`subprocess.run(..., timeout=120)` (c1 `:181`, c2 `:133`) is not wrapped; `TimeoutExpired` /
`FileNotFoundError` escape `measure()`, so the process dies with a traceback and rc 1 while the contract
says rc 2. Not reproduced (no hang was induced); reported as a code-path observation with line evidence.

### F9 — INFO — per-flagged-line subprocesses (C1 pair scan)
`want` is recomputed with two `git show` calls for every flagged `LOG.md`/`corpus/README.md` line
(c1 `:483–485`). Measured 210 `git` execve for 100 flagged lines (≈2 per line) and 0.68 ms per call on a
warm cache: a 50 MB `LOG.md` of annotations predicts ≈1.4 M git calls (≈16 min) — linear, but the largest
constant in the instrument and part of F1's "no aggregate work budget" limit. Smallest remediation: hoist
the two `registry_count` reads out of the loop.

## 4. Defences that held (positive receipts)

- **Revision shape**: only `[0-9a-f]{40}`; symbolic refs and tags refused with exit 2 (`A3`).
- **Argument injection**: `Path(root).resolve()` before `git -C`; option-shaped `--rev` swallowed by argparse;
  every fixed monitored path is an ASCII constant.
- **Repository-local config**: `-c core.fsmonitor=false -c core.hooksPath=/dev/null` override repo-local keys
  (measured both ways), and git itself ignores repo-local `trace2.*` targets (`A5`, `A14`).
- **Attributes / filters**: `git show` is the raw blob; `filter.*.clean/smudge` run only on index/checkout
  operations the counter never performs; textconv is not applied to `--numstat`; `diff.external` needs
  `--ext-diff` (`A4`).
- **Object integrity**: `GIT_NO_REPLACE_OBJECTS=1` defeats a forged `git replace` of the correction blob
  (measured against a live forging control, `A12`); `GIT_NO_LAZY_FETCH=1`, `GIT_TERMINAL_PROMPT=0`,
  `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1` are all present in `git_env()`.
- **Writes in the default path**: no file created anywhere; only `/dev/null` is opened read-write (the
  `GIT_CONFIG_GLOBAL=os.devnull` path); lane hashes unchanged (`A6`).
- **Selftest writes (normal path)**: 0 absolute paths outside `--work`, all relative writes inside the
  fixture cwds, no `..`, no `/tmp` (`A7`); dangling/regular-file/`fixture-name` symlink shapes are contained
  by `FileExistsError` / `rmtree` refusal / `NotADirectoryError` with no write (`A10`).
- **C2 path arguments**: `git show <rev>:<path>` rejects `..`, absolute paths and dash-leading names; no
  out-of-tree read (`A13`).

## 5. Named limits and routing

F1–F9 are named limits of the frozen v5 instruments; per the freeze rule they are **not** edited here and
route to round 57. No finding changes a C1/C2 verdict at `cce21b55`: the real-lane runs stay at exit 0 with
the pinned SUMMARY fields, and every attack that touched the verdict path either preserved the refusal
(`A4` binary attribute) or was rejected (`A3`, `A12`, `A13`). Only the human-readable output (F2) and the
run's completion time (F1) are attacker-influenced.

## 6. Verdict

Attacks found real, reproducible defects (two MEDIUM, five LOW, one INFO), none HIGH, and no case where a
hostile repository escapes the default read-only path, gets a command executed, or turns a refusal into a
pass. The two MEDIUMs are report-integrity and audit-availability limits, both triggerable by committed
bytes alone.

VERDICT: FINDINGS

WAVE-VERDICT: ATTACK-FOUND

## 7. Receipts (in this seat directory)

- `receipts/pins.txt` — sha256 of the frozen bytes installed into scratch.
- `receipts/inputs-args-replace.txt` — A3, A12, A13, root shapes.
- `receipts/attributes-exec.txt` — A4 numstat/filter/textconv/binary-attribute probes.
- `receipts/hooks-fsmonitor-trace2.txt` — A5, A14 with the positive controls.
- `receipts/c1-default-writes.txt`, `receipts/c2-default-writes.txt` — A6 strace extracts.
- `receipts/c1-selftest-writes.txt`, `receipts/c1-selftest-33-cases.txt` — A7 and the healthy control.
- `receipts/symlink-and-bytecode.txt` — A8–A10, A15.
- `receipts/c1-terminal-injection-raw.txt`, `receipts/c2-terminal-injection-raw.txt` — A11 raw bytes.
- `receipts/quad-times.txt`, `receipts/c2-50mb-capture-time.txt`, `receipts/pair100.time`,
  `receipts/pair400.time` — A1, A2, A16, A18 timings.
