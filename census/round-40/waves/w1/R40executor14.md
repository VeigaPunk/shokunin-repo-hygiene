# R40executor14 — C2 operability attack: privileged-runner inversion of the observed-pair probe

- Seat: R40executor14 (executor, leaf; no dispatch). Axis: operability (C2).
- Frozen claim attacked: `census/round-40/preregistration.txt:7-8` — the r40 L4 analyzer "verifies all **observed** class/trigger pairs in the frozen list", observed pairs being derived exactly the r39 way (runtime probe → `classify`), with kill if "any observed class mapping disagrees with runtime behavior".
- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. No production file written, no frozen claim edited, no git/jj mutation, no installs (pacman untouched; nothing installed or updated).

## Named distinct edge (item 14)

**Privileged-runner inversion of the EACCES observation leg.** The C2 predicate's input — the set of "observed class/trigger pairs" — is produced by the counter's own probe procedure (`os.chmod(probe, 0)` → run → `classify`). Under a privileged runner (uid 0 / CAP_DAC_OVERRIDE) the chmod-0 probe **opens successfully**, the tool falls through to `RECORD-EMPTY`, and the observed pair for the EACCES trigger inverts from `(RECORD-MISSING, EACCES)` to `(RECORD-EMPTY, EACCES)`. The preregistration pins no runner environment, so the frozen C2 measurement is environment-relative and cannot reach its predicate as root. The ENOENT leg does **not** invert (measured), so only one of the two frozen observed pairs flips.

Distinctness from prior r40 w1 seats (grep over `.ufo/waves/round-40/w1/` for `sudo|CAP_DAC|as root|chmod 0|RECORD-EMPTY` returned no privileged-runner hits; all four sibling C2 seats are continuation-grammar attacks):
- R40scout17: joiner-depth matrix (`until_next_class`/`one_extra_line`/`until_blank`), TOTAL-on-second-continuation, `duplicate` word boundary.
- R40executor50: first-line-`EACCES` synthetics; real-tool-only comparison cannot establish the control.
- R40executor38: over-join attribution boundary + `EISDIR` negative control.
- R40executor62: continuation prose beginning with a class-like token.

## Evidence pointers (committed r39 artifacts)

- Probe + observation mechanism: `census/round-39/c2-counter.py:219-237` — probe written `:220-222`, `missing = classify(run_drift(... absent ...))` `:223`, `os.chmod(probe, 0)` `:224`, `locked = classify(run_drift(... probe))` `:225`, L4 booleans `:230-237`, detail line `:229`.
- Helpers: `run_drift` `c2-counter.py:117-123`; `classify` `:125-131` (first-match over `RECORD-MISSING, RECORD-MALFORMED, RECORD-EMPTY, RECORD-OUTSIDE-ROOT`); `docstring_classes` `:133-145` (first stripped line per class, `clean=False`).
- Runtime raise sites: `tools/souji-worktree-drift.py:131-136` — `os.open(path, O_RDONLY|O_NONBLOCK)`; `ENOENT` → `RECORD-MALFORMED` `:134-135`; **every other open error (incl. EACCES)** → `RECORD-MISSING` `:136`. `:167-168` — `RECORD-EMPTY: no REPO rows` (raised in `parse_record`, before any git child; refusal path `main` → stderr, exit 2).
- Docstring entries (same bytes): `:44` `RECORD-MISSING EACCES or ELOOP …` (EACCES on the first line), `:46` `RECORD-MALFORMED a missing (ENOENT) …`, `:49` `RECORD-EMPTY no REPO rows` — `RECORD-EMPTY`'s entry contains no `EACCES`.
- Byte identity: worktree `tools/souji-worktree-drift.py` sha256 `e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76` == `git -C <lane> show 0242085909fb…:tools/souji-worktree-drift.py` (verified); `git status --porcelain tools/ census/round-39/` → empty; lane HEAD `be4cb61`, base `0242085`.

## Commands actually run and outputs

Scratch: `/fast/scratch/hyaku/souji-r40/R40executor14` with `TMPDIR` set there. Scripts `exp14.py` (copies both artifacts into scratch by reading lane bytes; imports the counter via `importlib` with `PYTHONDONTWRITEBYTECODE=1`; runs E1/E3a/E3c) and `rootrun.py` (runs the drift tool with the counter's exact argv and whitelisted env, prints `classify` verdict). All reads of the lane; the only lane writes anywhere in this seat are this report file.

`TMPDIR=$SCRATCH PYTHONDONTWRITEBYTECODE=1 python3 -B exp14.py`:

```
COPIED counter39.py drift39.py (drift blob from 0242085909fb)
E1 real_map = {'RECORD-MISSING': 'RECORD-MISSING         EACCES or ELOOP opening the record path: the path', 'RECORD-MALFORMED': 'RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, a line'}
E3a non-root missing=RECORD-MALFORMED locked=RECORD-MISSING uid=1000
E3c L4 boolean non-root pair (MALFORMED,MISSING): True
E3c L4 boolean root pair    (MALFORMED,EMPTY):   False
E3c entry r40 would demand EACCES from under root: "<RECORD-EMPTY absent from analyzer's class map>"
```

`sudo -n python3 -B rootrun.py <scratch>/drift39.py <scratch>/rootfix <scratch>/probe0.tsv` (probe chmod-0 during the run, restored after):

```
=== root x chmod-0 probe ===
ROOT-RUN uid=0 record-mode=0 rc=2 class=RECORD-EMPTY
REFUSAL RECORD-EMPTY: no REPO rows in /fast/scratch/hyaku/souji-r40/R40executor14/probe0.tsv
=== root x absent path ===
ROOT-RUN uid=0 record-mode=absent rc=2 class=RECORD-MALFORMED
REFUSAL RECORD-MALFORMED: /fast/scratch/hyaku/souji-r40/R40executor14/absent.tsv is not a regular file
```

Post-run sweep: `find <scratch> -user root -o -name __pycache__ | wc -l` → `0` (no root-owned files, no bytecode written into the lane or scratch).

Execution record: the first root absent-path run was discarded — the wrapper `stat`ted the intentionally nonexistent record for reporting and crashed after the subprocess; guard added, both root arms rerun clean. The discarded run produced no class verdict and is not used as evidence (same discipline as the r39 defective-run discard in `census/round-39/waves/w1/W1ExecC2Docstring.md:172-175`).

## Falsifier (concrete)

The frozen C2 measurement's "observed pairs" are not a property of the candidate bytes; they are a property of candidate bytes **plus runner privilege**:

| runner | absent-path probe | chmod-0 probe | observed EACCES pair | r39 L4 boolean (`:230-237`) |
|---|---|---|---|---|
| uid 1000 | `RECORD-MALFORMED` | `RECORD-MISSING` | `(RECORD-MISSING, EACCES)` — matches docstring `:44` | `True` |
| uid 0 | `RECORD-MALFORMED` | `RECORD-EMPTY` | `(RECORD-EMPTY, EACCES)` — contradicts `:44`; `:49` has no `EACCES` | `False` |

Consequences under the frozen kill conditions, run as root:

1. A faithful r40 analyzer verifying the *observed* pairs must find `(RECORD-EMPTY ↔ EACCES)`; no honest docstring can satisfy it (EACCES belongs to RECORD-MISSING at `:44`) → the kill clause "observed class mapping disagrees with runtime behavior" fires on pristine, correct bytes — a false kill.
2. Conversely, an analyzer that hard-codes the non-root pair to dodge (1) makes the receipt's claimed observed pairs disagree with its own runtime probes in the same run — the predicate is unreachable either way.
3. Even the r39 control leg degrades: with the root-observed pair the L4 boolean is `False` (measured, E3c), so `new_ok and not old_ok` cannot hold and the receipt reports a FAIL that is an artifact of the environment, not of the candidate.

The preregistration (`census/round-40/preregistration.txt:7-8,13`) pins revisions, scratch-path hygiene, and no-hardcoded-`/tmp` — but no runner-privilege precondition. This is an unrecorded environmental dependency of the C2 measurement, demonstrated on committed r39 bytes.

## Bounded measurement plan (smallest fix, for the r40 counter author)

1. Privilege gate: before the L4-equivalent, if `os.geteuid() == 0`, refuse `rc 2` with `REFUSAL COULD-NOT-EVALUATE: privileged runner, the chmod-0 EACCES probe does not invert` (matches the existing refusal style at `c2-counter.py:171-175`). A capability probe (`chmod 0` a scratch file, attempt `open`) is stricter than the euid check and covers `CAP_DAC_OVERRIDE` without uid 0.
2. Print the derived pair in the receipt next to the docstring maps (extend the `:229` detail line and the new wrapped-probe arm) so a reviewer can see which environment the "observed" set came from.
3. Assert the EACCES leg's class explicitly (`locked == "RECORD-MISSING"`); any other value is a refusal, never a silent FAIL leg — keeps environmental falsity out of the verdict channel.

This plan does not touch the continuation-grammar question (owned by scout17/38/50/62); it makes their measurement runnable under any runner.

## Verdict

**Concrete falsifier of the C2 measurement's operability: confirmed and executed.** The frozen C2 claim's "observed class/trigger pairs" input inverts for the EACCES leg under a privileged runner (chmod-0 probe → `RECORD-EMPTY` instead of `RECORD-MISSING`, both observed directly on the committed r39-tip drift tool), and the preregistration records no runner-privilege precondition. Not a falsification of any r40 candidate analyzer (none exists in the lane); on a non-root runner the r39 artifacts behave as previously reported (E1 map matches `R40executor50.md:12-13` independently). The falsifier transfers to the r40 counter unless the receipt adds the privilege gate above.

Scope kept: no counter/fixture/production files touched, no frozen claim edited, no commits, no judgments rendered on other axes.
