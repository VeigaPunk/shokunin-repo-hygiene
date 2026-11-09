# R95ReviewerC2 — C2 setup-discipline review (r95 probe + sixteen-arm counter)

Seat: correctness review of the r95 probe's setup discipline and the sixteen-arm counter against the C2 wording.
Owned files: this report + `.ufo/waves/round-95/w1/R95ReviewerC2/` (52 receipts; scratch `/fast/scratch/hyaku/souji-r95/R95ReviewerC2/` created, used, and deleted before yield; only text receipts retained).
Instruments reviewed (sha256 verified): probe `bd83e120a71fe01073f63f5bdbafedd468bd772b9fc46fc12b893abc479fdc73`, arms counter `dd2da59b7c9f5ecbc043ff826a13fe848c5f99ef31b775aa4fee274353b2569d`, forgery runner `337fae896bcacfe66fb670c0f63296273c1ae02eedf46300d326acb6e0d7a7a8` — all match prereg pins. FORGERIES tuple byte-identical between r94 and r95 probes (diffed). No tools installed. No frozen file modified; all probes run with `--work` under my scratch (never /tmp; my two /tmp paths `Q1m`/`Q1z` were refused before creation and verified absent afterwards).

## Q1 — Can the r95 probe still exit 1 on a setup failure?

Verdict: NO exit-1 escape found on any setup failure tried, EXCEPT the hang-class case Q1-pipe-holder (see Q3). The catch-all (`cli` → exit 2 on `Fatal`/`OSError`/`Exception`) held everywhere; `argparse` errors also exit 2. Each result: receipt in the seat dir.

Probe-level runs (all `python3 -B census/round-95/c2-forgery-probe.py` with the real r93 fixture unless noted; exit + stderr):

| Case | Exit | Evidence |
|---|---|---|
| fixture is a directory (`Q1a`) | 2 | `C2-FORGERY-FATAL: --fixture … is not a readable regular file` |
| tool / before is a directory (`Q1e`, `Q1f`) | 2 | same, per-arg message |
| fixture / tool / before unreadable (`Q1x`, `Q1y`, mode 000) | 2 | same; running uid 1000, not root |
| fixture is a FIFO (`Q1aa`) | 2 | `isfile` false → Fatal |
| dangling-symlink tool (`Q1o`), tool under a regular file (`Q1ag`) | 2 | Fatal, `isfile` false |
| symlink loop as fixture (`Q1j`) | 2 | `isfile` false (ELOOP) → Fatal |
| `--timeout 0` (`Q1b`), `--timeout -5` (`Q1d`) | 2 | `C2-FORGERY-FATAL: --timeout must be a positive number` |
| `--timeout abc` (`Q1c`), missing `--work` (`Q1k`) | 2 | argparse error, exit 2 (not via `cli`, since parsing precedes it) |
| `--timeout +5` / `007` (`Q1ai`, `Q1aj`) | 2 | accepted as ints; then mute-fixture Fatal (correct) |
| `--work` symlink loop (`Q1g`) | 2 | `exists and is not a directory` (`lexists` true, `isdir` false) |
| `--work` symlink to /tmp (`Q1h`) | 2 | `is not empty` — `/tmp` is non-empty; gate outcome 2 via the emptiness check, not the /tmp check (cosmetic) |
| `--work /tmp` exactly (`Q1l`) | 2 | `is not empty` (note: `realpath("/tmp")` = `/tmp` does NOT match the `startswith("/tmp/")` prefix, so the bare `/tmp` path is refused by the emptiness check rather than the /tmp check — outcome still 2) |
| `--work /tmp/../tmp/absent` (`Q1z`), `/tmp/absent` (`Q1m`) | 2 | `under /tmp, /var/tmp or /dev/shm` (realpath prefix) |
| `--work` dangling symlink (`Q1n`) | 2 | `exists and is not a directory`; symlink NOT followed/created through (target still absent after) |
| `--work` symlink to regular file (`Q1s`) | 2 | `exists and is not a directory` |
| `--work` symlink to empty dir (`Q1p`, mute fixture) | 2 | proceeds past checks (writes go through symlink), mute-fixture Fatal — symlink itself is not refused; no finding, empty-target use is consistent with "existing empty directory" |
| `--work` under a read-only parent (`Q1r`, mode 500) | 2 | `cannot be created: Permission denied` (caught OSError in makedirs) |
| `--work` made read-only after checks (`Q1q`, real fixture) | 2 | fixture cannot create `<work>/positive` → no SUMMARY → Fatal `…(exit 1)` |
| probe's own write failing mid-run (`Q1q2`, fixture chmodded `<work>` to 500 after a passing positive) | 2 | `C2-FORGERY-FATAL: cannot write …/F1-souji-record-agreement.py: Permission denied` — the exact probe-docstring clause "a write under --work that fails after the checks" is exercised and exits 2 |
| fixture syntax error (`Q1af`), fixture exits 2 muted (`Q1ak`) | 2 | no-SUMMARY Fatal with exit code reported |
| fixture prints SUMMARY then hangs (`Q1t`, timeout 5) | 2 | `--timeout 5s; its process group was killed` |
| fixture's same-group child holds pipes (`Q1v`, timeout 5) | 2 | timeout Fatal; no leftover (see Q3) |
| fixture with detached child (pipe not held) that the fixture exits before and outlives via setsid (`Q1u`, timeout 30) | 2 | both probe and outer time controls kill the group; detached child holding pipes still blocks `communicate()` until timeout → Fatal 2 (this run hit the full 30 s) |
| detached grandchild closing pipes, surviving on success (`Q1u2`, timeout 30) | 1 (VERDICT) | probe exits 1 with `FORGERY-SUMMARY … rejected=0 positive=pass`; the grandchild wrote its marker file 5 s later and survived — a fixture escaping its process group is not reaped on the success path, but this is verdict/exit-1, not setup-escape (see Q3/Q5). No probe-level escape; recorded for the frontier |
| broken stdout pipe (`Q1w`, `\| head -c 50`) | 2 | `C2-FORGERY-FATAL: I/O error: [Errno 32] Broken pipe` — `OSError` caught; exit 2, not Python's shutdown 120 |
| empty tool file (`Q1ac`) | 2 | positive fails, F1/F2 forgeries run, then `F3 edit does not apply exactly once` → Fatal 2 |
| overlong `--work` (>NAME_MAX, `Q1an`) | 2 | caught OSError → 2 |
| `--work ""` with empty cwd (`Q1ad`) | 2 | `abspath("")` = cwd; mute fixture → no-SUMMARY Fatal; cwd left empty (no leak) |
| NUL byte in a path arg | UNTESTABLE via CLI | execve rejects NUL before Python starts; not a probe-level case (my first harness bug substituted 'Z'; the correct run hits `ValueError: embedded null byte` in the *parent* before exec — no probe involved) |

Full 16-arm counter re-run by this seat on the frozen bytes (`arms-full-r95.txt`, `--jobs 4`, wall 120.5 s): `ARMS-SUMMARY arms=16 conform=16`, exit 0 — predicate number re-derived by an independent runner. R94-probe S9/S10/S11 traceback-exit-1 reproduced (`Q1r94-S9/S10/S11`: `UnicodeDecodeError` / `NotADirectoryError` tracebacks, exit 1, no FATAL line) — the prereg control's `S9, S10, S11 exit=1` is confirmed on the r94 bytes.

## Q2 — Does each new arm (S9–S14) test what its label says?

Verdict: YES, all six, verified by construction + per-arm outputs (`arms-full-S9/S10/S11/S14-out.txt`, control file).

- S9 `tool-nonutf8`: filed tool bytes + `b"# \xff not utf-8 (S9)\n"` under `--work`; `decode` fails at byte `len(tool)+2`. r95: `read_utf8` → Fatal 2. r94: traceback exit 1 (reproduced). Label accurate (the added line is a comment; only the 0xFF byte matters).
- S10 `before-nonutf8`: same with r91 tool bytes. Accurate.
- S11 `work-fileparent`: `--work` = `<regular file>/sub`; `os.makedirs` raises `NotADirectoryError`. r95 catches OSError → Fatal 2; r94 traceback exit 1 (reproduced). Label accurate.
- S12 `fixture-hang`: `import time\nwhile True: time.sleep(3600)` — sleeps forever, as labelled. r95 probe timeout (default 120) → Fatal 2; r94 waits until the counter's 300 s arm-timeout → `exit=hung`. Accurate. (Minor: the counter docstring says "the counter kills the arm after --arm-timeout"; the probe kills its own fixture group at 120 s — both true, probe first.)
- S13 `work-tmp`: `/tmp/souji-r95-arm-S13-<pid>-absent`, never created by the counter (presence asserted absent; probe refuses). Accurate. Probe-side receipt `arms-full-S13-out.txt` shows refusal. (One residual fetched here: another seat's probe created the empty `/tmp/souji-r95-arm-S13-1159388-absent` dir — not this seat's; S13's stub dir is not cleaned by the counter. Not a label defect.)
- S14 `edit-twice`: filed tool + a triple-quoted string literal holding a second copy of F3's edit target. Verified: tool holds F3's target exactly once (count 1), dup holds twice (count 2); probe `text.count(old) != 1` → Fatal 2. Label accurate — the second copy is inert (inside a string) exactly as labelled; the arm binds the `count != 1` check (R94MutC2 M11).

All six arms were live-run in this seat's full counter run (all `conform=yes` for r95; control file shows the r94 split).

## Q3 — Timeout process-group kill; anything left running after S12?

Verdict: the kill is correct for fixtures that stay in their process group; NOTHING is left running after S12 (the bound HANG fixture). One genuine residual beyond the bound: a fixture whose new-session grandchild holds the output pipes makes the probe hang forever.

- S12 replica with default timeout (`Q3-S12-replica.txt`): exit 2, wall 120.1 s, `…exceeded --timeout 120s; its process group was killed`; `ps` after +1 s: no leftover.
- S12 with a 3-deep same-group child tree (`Q3-hang-tree.txt`, timeout 5): exit 2 in 5.0 s; no leftover. `killpg` + second `communicate()` reaps the tree.
- Same-group child holding pipes (`Q1v`): killed, no leftover.
- Detached child with pipes closed, escaping to a new session (`Q1u2`): SURVIVES the success path (marker file written at +5 s) — probe exits 1 by verdict; this is scope limit (i) verbatim: "a fixture that escapes its process group … are the wave's to try" — tried, survives, no exit-1 escape, but no reaping either.
- **Pipe-holding detached grandchild (`Q1-pipe-holder.txt`) — the frontier finding:** fixture forks, child `setsid()`s, inherits stdout/stderr, `sleep(3600)`; fixture itself prints SUMMARY and exits 0 at once. Probe run `--timeout 5` with a 60 s outer deadline: **the probe HANGS** (`TIMEOUT60`, wall 60.1 s — first `communicate(timeout=5)` blocked on pipe EOF, `killpg` could not reach the escaped grandchild, second `communicate()` blocked on the still-open pipes). A leftover process (PID 2474225, the grandchild) was still running when the outer timeout killed the probe, and this seat `pkill -9 -f 'fix-pipe-holder'`-ed it; `ps` confirmed clean afterwards. So the instrument docstring sentence "a fixture run that outlives --timeout: its process group is killed and the probe names the run" is falsified *for escaping fixtures*: the probe neither kills the escaped group nor names the run. The r94 probe hangs identically (worse: no timeout at all). The claim's own S12 fixture (HANG, in-group) is covered and clean — this residual lives inside stated limit (i) ("a fixture that escapes its process group") and is therefore NOT booked as FALSIFIES-WORDING (see Q5). `run()` fix sketch (not applied — L1 owns integration): close pipes after kill with a bounded second communicate, or drain via threads with `p.communicate(timeout=…)` on the reap leg / redirect to files instead of pipes.

## Q4 — Is "before 12" exactly what the control file shows?

Verdict: YES. `census/round-95/controls/c2-control-r94-probe.txt` arms (parsed): conform=yes for P1, P2, S1–S8, S13, S14 (12 arms); conform=no for S9 (exit=1), S10 (exit=1), S11 (exit=1), S12 (exit=hung). `ARMS-SUMMARY arms=16 conform=12`, EXIT 1 — exactly the prereg control line ("`ARMS-SUMMARY arms=16 conform=12` (S9, S10, S11 exit=1; S12 exit=hung)"). No miscount: 12 conforming arms = P1, P2, S1, S2, S3, S4, S5, S6, S7, S8, S13, S14. This seat also reproduced the r94 side (Q1r94 receipts).

## Q5 — Any sentence wider than the predicate?

Verdict: the CLAIM sentences survive; two narrower wording notes (neither a claim-sentence falsification).

Checked claim sentences:
1. "The r95 probe refuses each of S9–S12 with exit 2 and a `C2-FORGERY-FATAL:` line" — holds on the bound arms (this seat's full run: S9–S12 all exit=2, FATAL line yes) and on every sibling case in Q1 except the out-of-bound pipe-holder hang.
2. "and conforms on the twelve arms the r94 probe conforms on (P1, P2, S1–S8, S13 …, S14 …)" — the parenthesised list IS the 12 (P1, P2, S1, S2, S3, S4, S5, S6, S7, S8, S13, S14); matches the control file exactly per Q4. No wider reading available; "the twelve" is enumerated.
3. "Counted quantity: conforming arms of 16 — before 12, after 16" — re-derived: 12 (control file) and 16 (this seat's independent full run). No widening.
4. Predicate `arms=16 conform=16` EXIT 0 — re-derived under a different runner + different `--jobs` than the L1 receipt.

Notes (flagged, not falsifications):
- The probe docstring over-promises for escaping fixtures (Q3 pipe-holder): "its process group is killed and the probe names the run" is true only for in-group fixtures; the prereg INSTRUMENTS repeat the timeout description but the CLAIM binds only S12 = HANG. Since stated limit (i) explicitly reserves "a fixture that escapes its process group … [for] the wave's to try", Amendment-59 falsification of a *claim* sentence does not attach — but the docstring sentence itself is false as written for the escaping case, and the wave's job is to try exactly that. Recommend the L1 either narrow the docstring or book the pipe-holder as a follow-up instrument fix.
- `Q1h`/`Q1l` cosmetic: `--work` symlinked-to-/tmp or bare `/tmp` is refused by the emptiness check, not the /tmp-prefix check. Outcome identical (exit 2); no wording claims the /tmp message specifically.

## NO-FALSIFICATION

No artifact produced by this seat falsifies any sentence of the C2 claim as stated (incl. the predicate, the before/after counted quantity, and the arm list). The strongest counter-evidence found — the pipe-holding detached grandchild that makes the r95 probe hang past its own --timeout (`Q1-pipe-holder.txt`) — falls inside the claim's stated limit (i) ("a fixture that escapes its process group and other setup failures are the wave's to try") and outside the bound S12 fixture ("a fixture that sleeps forever"); it is reported as a residual risk and a docstring-scope note, not a wording/numeral falsification. What was tried: 40+ probe-level cases (dirs, symlinks, dangling links, loops, FIFOs, unreadable files, read-only mid-run for both fixture- and probe-side writes, timeout spellings 0/negative/float/non-integer, summary-then-hang, four child/escape topologies, broken pipe, empty tool, overlong/empty work), a full independent 16/16 arms re-run (120.5 s), and r94-side S9/S10/S11 traceback reproduction.

## Residual risk and verification gaps

1. Escaping fixtures (new-session grandchild holding pipes) hang the probe indefinitely past --timeout; also the success-path grandchild in `Q1u2` survives reaping. Fix belongs in `run()` (bounded reap leg / file redirection), owned by the L1; the four bound arms and forgery controls do not exercise it.
2. The catch-all is unbound by any arm (prereg limit (i) says so): no arm triggers "any other exception escaping main()". Q1 probes covered argparse, OSError, ValueError-class parent-side failures — all exit 2 — but no frozen arm binds the generic clause; GA/GB/GC cover only the verdict-exit, decode, and timeout lines.
3. Verification gap: this seat rederived conform=16 and the control conform=12, but did not re-run the forgery controls (GA/GB/GC) — the L1 receipt `controls/c2-forgery-controls.txt` stands; GB's `S10 exit=0` (decode-replace makes the non-UTF-8 before parse and run to a verdict) is worth noting: the GB mutant fails safely (exit 0 = verdict "all rejected" on garbage input) rather than exiting 1 — refused by the summary check, but its failure *mode* is a verdict pass on bad bytes, which the conform counter catches only via want=2.
4. S13 leaves the /tmp stub dir to sibling seats (empty, harmless, never created by the counter); the probe itself creates nothing under /tmp.

Receipts (all under `.ufo/waves/round-95/w1/R95ReviewerC2/`): Q1a–Q1an probe runs (per-case argv/exit/stdout/stderr), Q3-S12-replica (120.1 s, no leftover), Q3-hang-tree, Q1-pipe-holder (probe hang + leftover + cleanup), Q1u2 (grandchild survival marker), arms-full-r95 + per-arm copies (S9–S14, P1, P2), Q1r94-S9/S10/S11 (r94 traceback exit-1), arms-full-S12-out (S12 FATAL line). Scratch deleted; /tmp untouched by this seat (both /tmp paths refused pre-creation, verified absent).
