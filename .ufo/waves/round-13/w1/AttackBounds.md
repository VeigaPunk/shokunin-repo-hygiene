# AttackBounds — round 13 / w1 critic (C2 timeout-fix falsification)

Seat: `SoujiR13.AttackBounds` (critic, leaf). Baseline: HEAD `31984f4`. At read time
`tools/souji-quarantine.sh` was unmodified (`git diff --stat HEAD -- tools/souji-quarantine.sh` printed
nothing) and `tests/fixtures/r13-quarantine-bounds.sh` did not exist yet. So this report attacks the C2
design as dispatched to `BoundQuarantine` (w1-spec item 0) against the baseline code. It is not a
review of a landed diff.
This seat is not independent of the round (same wave), and certification stays OFF. I did not run
the quarantine tool, the engine, a selftest or a fixture. Read-only probes that I did run:
`--help`/`--version` of `/usr/bin/mv` and `/usr/bin/timeout`, `pacman -Qo`, `type -a`, `findmnt`,
`stat -f`, and one `sha256sum` on two tool files.
Tags: **[FACT]** means observed in a cited line or probe. **[INFERENCE]** means reasoning I did not
execute. **to-verify** means L1 must check it.
Installs/updates: none.

Axes: calibration (claims match evidence), operability (bounded, diagnosable, contract exit
codes), coverage (fixture cases red on baseline, not vacuous).

---

## A1 — The Q8 motivation is probably misattributed: LOG:373 was serial holds, not a hang

- **[FACT]** LOG.md:373-377: "souji-quarantine.sh staged 3 files then hung (hit its 20-min driver
  timeout) … 2 (launch-chousa/kagi.json) missing post-timeout, restored from origin".
- **[FACT]** The tool processes targets one at a time, and each target runs every stage before the
  next starts. Stage 2 moves the target (`souji-quarantine.sh:528-543`), stage 3 runs
  `sleep "$HOLD"` (`:555-557`), stages 4-5 follow (`:560-598`), and the loop is at `:640-662`.
  The default is `HOLD=450` (`:141`).
- **[FACT]** `census/round-3/operator-approval-list.tsv` lists `launch-chousa.json` as data row 1
  (line 2) and `launch-kagi.json` as data row 2 (line 3).
- **[INFERENCE, strong]** 3 × 450 s = 1350 s, which is more than the 1200 s driver bound. That means
  target 1 was staged, held and deleted; target 2 was staged, held and deleted; target 3 was staged
  and still in its hold when the driver killed the tool. The totals fit: 93 staged by hand plus 1
  staged by the tool gives the "94 copies" in quarantine. The "2 missing" files are exactly rows 1-2,
  which the tool had legitimately DELETED. No mv or digest hang is needed to explain LOG:373.
  This is unverified because the run's stdout was not preserved.
- **[FACT]** LOG.md:403 (the FIFO hang) concerns `souji-vault-verify.impl-17.sh` judge fixtures, not
  this tool.
- **Impacted axes:** calibration (citing either LOG line as "closed by Q8 timeouts" would be false
  provenance) and operability (a 96-row list still needs at least 96 × 450 s, about 12 h, with or
  without timeouts).
- **Smallest safe correction:** in C2 prose and the lesson, cite LOG:373 as "motivation for a bounded
  total runtime; per-target timeouts do NOT bound N×HOLD" and LOG:403 as "FIFO hazard observed in a
  sibling tool". Also record a follow-up mistake: RESULT rows go only to stdout, so a driver kill
  destroys the per-target record, and the operator "restored" two receipt-verified deletions. Do not
  claim Q8 closes LOG:373.

## A2 — Duplicate function definitions: a fix or a grep can land in dead code

- **[FACT]** `file_sha` is defined at `:184` (no guard) and again at `:722-725` (with
  `s18_path_ok && [ -f ]`). `dir_digest` is defined at `:186-194` and again at `:727-734`.
  `run_verify`, `ledger_row_for`, `flow_one` and `second_check` are also redefined at `:1061-1148`.
  Bash keeps the last definition executed, and all of them run before main (`:1519`). So only
  `:722` and `:727` are live, and `:184-194` is dead.
- **Counterexample:** a timeout added to `:184`/`:192` (the first definitions a reader finds) changes
  nothing at runtime. Q8's acceptance grep `grep -nE 'timeout [0-9]+[smh]? .*(mv|sha256sum)'`
  (QUALITY.md:32) would still pass. That is false success.
- **[FACT]** The candidate engine is a second authority too. `:134-135` prefers
  `tools/cand-merge-verify.sh` over `tools/souji-verify.sh` when the candidate exists. It is tracked,
  and today its bytes equal souji-verify.sh (`9adb1764…`; I hashed it with the harness-builtin
  `sha256sum`, so L1 should re-hash with `/usr/bin/sha256sum`). An edit to `souji-verify.sh` alone
  would be silently ignored by the installed quarantine tool. This matters for C1's installed-hash
  claims.
- **Correction:** edit only the live definitions (`:722-734`), and delete or comment-mark
  `:184-194` as shadowed (in scope as cutover cleanup). Treat the behavioural fixture as the
  authority and the grep as advisory.

## A3 — The Q8 grep cannot match a correct `--kill-after` call

- **[FACT]** `/usr/bin/timeout --help`: `Usage: … timeout [OPTION]... DURATION COMMAND`, and
  `-k, --kill-after=DURATION`.
- **Counterexample:** `timeout -k 5s 30s sha256sum …` and `timeout --kill-after=5s 30s mv …` do not
  match `timeout [0-9]+[smh]? .*` because the literal `timeout ` is followed by `-`. The only spelling
  that matches is `timeout 30 -k 5 mv`. **[INFERENCE, to-verify]** GNU timeout stops parsing options at
  the first operand (getopt `+fk:ps:v`), so that spelling runs `-k` as COMMAND, exits 127, and every
  target fails.
- **Impacted axes:** calibration and coverage. The mandated `--kill-after` design and the Q8 check
  contradict each other, which invites gaming (a comment line that contains the pattern).
- **Correction:** the Q8 test should be behavioural (the fixture). If a grep is kept, use
  `grep -nE 'timeout (-k ?|--kill-after=)[0-9]+[smh]? [0-9]+[smh]? .*(mv|sha256sum)'` against the
  live-definition line numbers.

## A4 — Digest failures already exit via errexit; timeout codes would leak as the tool's exit status

- **[FACT]** `set -euo pipefail` (`:121`). There is no `shopt`, `inherit_errexit` or TERM/INT trap
  (grep: no matches). Each call below is a plain command substitution assigned to a variable, outside
  any condition context. The call chain is `run_mode` → `flow_one` (`:654`/`:661`) → `s18_flow_one`
  (`:1119`) → `second_check` (`:564`) → `s18_second_check` (`:1123`), with no condition context
  anywhere:
  - `:498` `pin_sha=$(content_digest "$ct")`, before the move;
  - `:284` `now_sha=$(content_digest "$QPATH"); local dig_rc=$?`, after the move;
  - `:348` `vault_sha=$(file_sha "$vp")` and `:352` `vault_sha=$(dir_digest "$vp"); vault_rc=$?`.
- **[INFERENCE]** A non-zero digest status ends the script right there. The `dig_rc`/`vault_rc`
  branches (`:290-291` "symlink-present-in-quarantine" and `:353`) are dead: no selftest case
  reaches them (grep: only A1 at `:1451-1465`, a content-tamper case that returns rc 0). Concrete
  baseline outcomes:
  - A special descendant planted after stage 1: `s18_scope_ok` (`:714`) returns 1, so `dir_digest`
    returns 2 (`:729`). At `:284` the tool exits **2** (documented as "usage") after the move,
    with no RESULT and no SUMMARY. The staged copy is retained.
  - A `chmod 000` regular file inside a stale-class dir target: `s18_scope_ok` checks readability
    only for directories (`:707`). `xargs … sha256sum` returns 123, and with pipefail (`:730`) the
    tool exits **123** at `:498`.
  - Vault file removed during the hold: `file_sha` hits `[ -f ]` and returns 1 (`:723`). The tool
    exits **1** at `:348`, after the move.
  - The same pattern with a new `timeout` inside `file_sha`/`dir_digest` exits **124** or **137**.
- **[FACT]** The header contract says "Exit codes: 0 … 1 … 2 … 3 … 4 … No other codes" (`:88-92`).
- **Impacted axes:** operability (no diagnostic, and `--list` targets after the failure are never
  processed while earlier ones are already DELETED) and calibration (rc 2 reads as a usage error).
- **Correction:** capture every bounded call explicitly, for example
  `if ! pin_sha=$(content_digest "$ct"); then block_one "$raw" digest-failed "rc=$?"; return 0; fi`.
  At stage 4, on failure set `ok=0` and add evidence `pin=FAIL digest-rc=N`. Map timeout codes (124
  and 137) to evidence strings. The process exit stays within 0 to 4.
  Do **not** write `local x=$(…)`, because `local` masks the status (SC2155).
  Do **not** wrap the bounded step in a helper whose last command is `emit`: errexit is suspended
  inside `if ! helper`, so the helper returns emit's 0.

## A5 — Pipelines that swallow failure and return a valid-looking digest

- **[FACT]** `:328` reads
  `blob_sha=$(git -C "$CREPO" cat-file blob "$intro:$REL" 2>/dev/null | sha256sum | cut -d' ' -f1 || true)`.
  If `git` fails (or is timed out once wrapped), `sha256sum` still hashes empty stdin and prints
  `e3b0c442…`. `|| true` then discards the pipefail status.
- **Counterexample [INFERENCE]:** for an empty tracked file (`.gitkeep`, `__init__.py`),
  `PIN_SHA=e3b0c442…`, so `intro-blob=ok` passes even though git failed. In the baseline this is
  masked, not prevented, by the wrapper's object-id check (`:1132-1137` `default-snapshot`). Wrapping
  `git cat-file` in `timeout` inside this pipeline keeps the hole open.
- **[FACT]** The s18 `dir_digest` of an empty dir is also `sha256(empty)` = `e3b0c442…` (`:732`,
  `xargs -r` emits nothing), the same value as an empty regular file. The digest carries no type tag.
  This is lower severity because the mtime pin (`:296-301`) usually differs.
- **Correction:** capture the producer's output and status separately before hashing:
  `blob=$(timeout … git cat-file blob …) || fail`, then pipe it through `sha256sum`. Never apply
  `|| true` to a pipeline whose consumer outputs a hash on empty input. Optionally prefix the digest
  input with a type tag (`f:`/`d:`). That last part is out of C2 scope, so note it only.

## A6 — Special files: baseline refuses most of them already, so "FIFO red-before" is mostly false

- **[FACT]** The engine refuses a dir with special descendants at stage 1:
  `souji-verify.sh:836-838` (`protected-or-unsupported-descendant-refused`) via `s18_scope_ok`
  (`souji-verify.sh:519`). The quarantine tool reports that as `NOT-AUTHORIZED`, rc 3
  (`:415-416`, `:391-400`).
- **[FACT]** A FIFO as the top-level target can still earn `SAFE(stale)`. `try_stale`
  (`souji-verify.sh:767-786`) has no non-regular check for non-directories. The quarantine pin then
  runs the live `file_sha`, whose `[ -f ]` guard returns 1 (`:723`) **before** `sha256sum`. So
  **[INFERENCE]** the baseline exits 1 at `:498`: no hang, no move, no RESULT.
- **Coverage counterexample:** a fixture case "FIFO descendant → refused, rc 3, unmoved" passes on
  the baseline, so it is not red-before. Labelling it red-before would be false provenance. "FIFO
  target → bounded nonzero, unmoved" also passes on the baseline (rc 1).
- **The only true FIFO hang path in the quarantine digest [INFERENCE]:** a time-of-check/time-of-use
  swap between the `s18_scope_ok` walk (`:729`) and `find -type f … | xargs sha256sum` (`:731-732`).
  `sha256sum` then blocks in `open()` on the FIFO.
- **Correction:**
  - Red-before FIFO coverage must plant the FIFO **after stage 1**. Use the existing test hook
    (`SOUJI_Q_TEST_HOOK`, `:546-551`, honoured only with `SOUJI_Q_SELFTEST_ACTIVE=1`) to `mkfifo`
    inside the staged dir. Baseline: rc 2 with no RESULT. Fixed: RESULT `ABORTED`, rc 3,
    `special-file` evidence, staged copy retained.
  - For a pre-move red case, use the unreadable descendant from A4 (baseline rc 123).
  - Assert a specific RESULT token **and** SUMMARY **and** rc 3, not just "nonzero and unmoved".
  - Bound the whole pipeline (`timeout -k K T bash -c 'set -o pipefail; cd -- "$1" && find … | sort -z | xargs -0 -r sha256sum | sha256sum' _ "$d"`).
    `timeout` cannot run a shell function or subshell directly: `timeout 30 file_sha` exits 127.
  - If the fix adds a special-descendant scan, it must check the scan's own exit status, because
    `find` exits 1 with partial output on an unreadable subdir, and it must be bounded too.

## A7 — Timeout after a partial move: residue, `--no-copy`, index.lock

- **[FACT]** The untracked path runs `mv -- "$ct" "$qpath"` (`:536`). It has no `-T` and no
  no-clobber, and nothing re-checks for a collision after `:477`. On failure it emits only the
  ERRTMP text and never reports where the bytes are (`:537-538`).
- **[FACT]** The tracked path runs `git -C "$crepo" mv` (`:529`).
- **[FACT]** `/usr/bin/mv` is GNU coreutils 9.11 (`pacman -Qo`), and `--help` lists `--no-copy` ("do
  not copy if renaming fails"), `-T`, and `--update=none-fail`. `/home` is btrfs `@home` and
  `/var/tmp` is btrfs `@` (findmnt), so they are separate subvolumes.
- **Counterexamples [INFERENCE]:**
  1. **EXDEV fallback.** A target inside a nested subvolume or mount under the repo makes `mv`
     copy and then unlink. A timeout or KILL mid-copy leaves a partial tree in quarantine with the
     source intact, or a full copy plus a partly removed source. SourceTimeout.md §4.1 agrees.
  2. **Delay after the rename.** A shim, slow fs or post-rename stall where the rename succeeds and
     *then* the timeout fires gives rc 124. The baseline-shaped handler reports
     `STAGE2-FAILED mv-failed` with no qpath and no residue. The file sits in quarantine
     unreported, and the next run reports `quarantine-collision`.
  3. **SIGKILL on `git mv`.** `--kill-after` SIGKILL on `git mv` leaves `.git/index.lock` in the
     **owning lane's repo**, which blocks that lane's git operations (cross-lane harm caused by the
     fix). It can also leave the worktree renamed with the index not updated (` D rel` plus
     `?? .ufo-quarantine/…`).
  4. **Collision race.** If `qpath` becomes a directory after `:477`, plain `mv`/`git mv` moves the
     target *into* it.
- **Correction:**
  - Untracked: `timeout -k 10s "$T" mv --no-copy -T --update=none-fail -- "$ct" "$qpath"`. This is
    rename-or-fail, never copies, never clobbers, and never nests.
  - On any non-zero status, lstat both ends and emit
    `STAGE2-FAILED <timeout|mv-failed> rc=N source=present|absent quarantine=present|absent qpath=…`.
  - Never continue to stage 3, 4 or 5. Never delete. Never auto-restore; a restore is another
    unbounded mutation, so leave the copy in quarantine.
  - Tracked: on 124/137 also report `index-lock=present|absent`, and never remove it, because it may
    belong to a concurrent git process.
  - Use a kill-after (≥10 s) long enough that git normally exits on TERM and runs its lock cleanup.
  - **Stop the `--list` loop after the first timeout.** A timeout usually means a hung filesystem,
    and 96 rows × (T+K) brings back the LOG:373 driver kill. Emit SUMMARY and return rc 3.
- **Coverage limitation:** Q16 withdraws `/dev/shm` and leaves Q4 unrelaxed, so a cross-device
  fixture is not admissible this round. The `--no-copy` defence is therefore grounded in the source
  (mv `--help`, S034 candidate) and is **not** tested by a fixture. The report must not claim tested
  partial-move safety.

## A8 — Command shims: keep PATH resolution and prove the shim fired

- **[FACT]** The round-9 selftest depends on PATH shims of `sha256sum` (`souji-round9-selftest.sh:196-219`)
  and `git` (`:132-144`). The quarantine ledger-revocation case triggers on the **2nd** hash of the
  vault (`R9_GATE_HIT=2`, `:215`), and the shim counts `sha256sum` calls from both the engine and the
  tool through PATH.
- **Counterexamples:**
  - Hardening with absolute `/usr/bin/sha256sum` bypasses the shim. The round-9 check "ledger
    revocation was reached" (`:228`) then fails, breaking "existing selftests remain compatible".
  - Adding any extra vault hash before `:348` moves hit 2 earlier (pre-move), so the case returns
    `NOT-AUTHORIZED` instead of `ABORTED`. That changes what the test means, and it can still
    pass by accident.
  - A blanket "delayed sha256sum" fixture shim also delays the **engine's** ledger pin at stage 1
    (`souji-verify.sh:590`). The engine call is unbounded (`:1067-1068`), so the fixed tool either
    hangs or is refused at stage 1 with `NOT-AUTHORIZED`: a green result for the wrong reason.
  - The same vacuity applies if the fix stops calling the shimmed name: the "delayed" case becomes
    an ordinary success.
- **Correction:**
  - Keep `timeout … sha256sum` resolved through PATH; GNU timeout uses execvp, so shims still apply.
  - Gate fixture shims on the exact target argument (like the r9 `${!#}`/`$PWD` gate, `:200`).
  - Have each shim write a marker, and require marker plus a `digest-timeout`/`mv-timeout` evidence
    token before crediting a bounded PASS.
  - For the tracked delay, use a `git` shim that matches the ` mv ` subcommand, because `git mv`
    calls rename(2), not the `mv` binary.
  - Test both delay orders: sleep before the real `mv` (source stays, no qpath) and sleep after it
    (qpath present, source absent, residue reported, no stage 3/4/5 lines).
  - At startup, require GNU timeout (`timeout --version` prints `GNU coreutils`), otherwise exit 1.
    Never fall back silently to unbounded execution.
- **[FACT] Harness hazard for L1:** in this agent's shell, `mv`, `timeout` and `sha256sum` are
  enabled **builtins** (`type -a`, `enable -a` count 3; builtin `mv --version` → `mv 0.8.0`, with no
  `--no-copy`; builtin `timeout --version` errors). `/usr/bin/bash -c 'type -t …'` shows `file` for
  all three, so scripts run under real bash get GNU. Checks typed directly into the harness shell,
  including SourceTimeout.md's suggested `timeout -k 1s 1s …` and `mv --no-copy …`, get non-GNU
  semantics. Use `/usr/bin/timeout`, `/usr/bin/mv`, or wrap them in `/usr/bin/bash -c`.

## A9 — Dry-run must stay non-mutating and must print the commands it would run

- **[FACT]** The dry-run branch starts at `:504`, after `pin_sha=$(content_digest "$ct")` (`:498`).
  So `--dry-run` reads and hashes target content and can hang or errexit there. The printed commands
  (`:505-516`) are hand-built strings, separate from the commands live mode executes.
- **Counterexamples [INFERENCE]:**
  1. A same-device check (needed for `--no-copy` gating) written as `mkdir -p "$qdir"; stat -c %d "$qdir"`
     placed before `:504` makes dry-run mutate. Selftest D1 (`:1341`, `[ ! -e "$R/.ufo-quarantine" ]`)
     would catch only the directory, not other residue.
  2. A "residue cleanup" of stale partial quarantines placed before the `DRYRUN` branch deletes in
     dry-run.
  3. Live mode switches to `timeout -k … mv --no-copy -T …` while dry-run still prints
     `mv -- src dst`, so the printed runbook no longer matches what runs. D1 greps only `git -C` and
     `rm -rf` (`:1339-1340`).
- **Correction:**
  - Compare `stat -c %d` of the source's parent and of `$crepo`, both of which exist, and never
    create anything before `:504`.
  - Build each bounded command once as an array and both print it (`printf '%q '`) and execute it.
  - Map a pin-digest timeout in dry-run to `DRY-RUN-BLOCKED digest-timeout` via `block_one`.
  - The fixture asserts that after dry-run the fixture tree is byte- and mtime-identical (for
    example `find "$R" -path "$R/.git" -prune -o -printf '%y %p %s %T@\n' | sort | sha256sum` before
    and after) and that `.ufo-quarantine` is absent.

## A10 — Bound values and the unbounded engine

- **[FACT]** `/usr/bin/timeout --help`: "A duration of 0 disables the associated timeout." Any env or
  flag override that accepts `0` (for T or for `-k`) silently removes the bound. The existing
  validator for `HOLD` accepts 0 (`:1549`).
- **[INFERENCE]**
  - A fixed short digest T (for example 30 s) fails large legitimate targets: multi-GB files, or
    the 42 G kotodama `.scratch` noted in LOG:409.
  - The pin runs before the move, so a pin timeout refuses safely, but this is an operability cost.
  - After a 450 s hold the page cache may be cold, so the stage-4 digest can exceed T even when the
    pin did not. The result is ABORTED and the copy stays in quarantine (safe and recoverable, but
    noisy).
  - **Uninterruptible sleep (D state: hung NFS/FUSE) is not bounded by `timeout`.** KILL is queued
    and the inner `timeout` waits. Q8 can only claim to bound interruptible hangs.
- **[FACT]** Stage-1 and stage-4 engine calls are unbounded (`:1067-1068`). They walk the fleet, and
  `rg` appears in `count_live_refs`.
  **[INFERENCE]** Bounding them is cheap and fail-closed, because `rc != 0` already gives
  `V_VERDICT=ERROR` (`:1070`), which leads to `block_one` (`:415`) or `engine-error=FAIL`
  (`:1127-1129`).
- **[INFERENCE] Process-group note:** GNU timeout without `--foreground` creates its own process
  group. An outer driver's process-group kill therefore misses inner-timeout children, but they
  self-terminate within T+K. A fixture that asserts "no stray `sha256sum`/`sleep`" must wait at least
  T+K, or it will be flaky. Never use `--foreground`; children of COMMAND are not timed out under it
  (`--help`). Never use `--preserve-status`; it hides 124 (see SourceTimeout.md §3.3).
- **Correction:**
  - Use fixed constants, for example digest T=300 s, `mv` T=60 s, kill-after 10 s.
  - Any override must be a positive integer (reject 0).
  - Bound `run_verify` as well, for example `timeout -k 10s 600s bash "$VERIFY_BIN"`.
  - Document the D-state limitation in the tool header and the lesson.

---

## Smallest safe correction set (what the canonical judge should require)

1. Put every timeout on the live definitions only (`:722-734`, `:529`, `:536`, `:328`, and
   optionally `:1067`). Delete the shadowed `:184-194`.
2. Capture every bounded call explicitly. Never let a digest status reach errexit. Keep the process
   exit within 0 to 4 and give each target a RESULT row (A4).
3. Untracked staging: `mv --no-copy -T --update=none-fail` under
   `timeout -k`. On failure, emit a residue lstat report, never delete, never restore, and stop
   further `--list` rows (A7).
4. Hash producer output separately from the producer's status; no `|| true` on a hash pipeline (A5).
5. Leave PATH resolution unchanged and require GNU timeout at startup (A8).
6. Before `:504`, do no mkdir and no cleanup; build each command once and use it for both the
   printed runbook and execution (A9).
7. Make the C2 prose honest: LOG:373 is not closed by Q8 (A1), cross-device is not
   fixture-tested (A7), D-state is not bounded (A10), and the FIFO-descendant refusal was already
   green on the baseline (A6).

## Exact final checks for L1 (run with real GNU tools, not harness builtins)

```
T=/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-quarantine.sh
/usr/bin/bash -n "$T"
shellcheck -S warning "$T"                                   # Q9
/usr/bin/timeout -k 10s 900s /usr/bin/bash "$T" --selftest; echo "rc=$?"   # existing + R9 suites, expect 0
grep -nE '^(file_sha|dir_digest)\(\)' "$T"                   # expect ONE live definition each (A2)
grep -nE 'timeout (-k ?|--kill-after=)[0-9]+[smh]? [0-9]+[smh]? .*(mv|sha256sum)' "$T"   # A3 form
grep -nE 'mv --no-copy' "$T"                                  # A7
grep -nE '\|\| *true' "$T" | grep -E 'sha256sum'              # expect none (A5)
grep -nE 'timeout [0-9]+[smh]? +-k' "$T"                      # expect none (A3 misorder)
# fixture, red on baseline then green on installed, with the outer bound from /usr/bin/timeout:
B=$(mktemp /var/tmp/souji-q-base.XXXXXX) && trap 'rm -f -- "$B"' EXIT && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 31984f4:tools/souji-quarantine.sh > "$B"
/usr/bin/timeout -k 10s 600s /usr/bin/bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r13-quarantine-bounds.sh --tool "$B"; echo "baseline rc=$?"   # expect red
/usr/bin/timeout -k 10s 600s /usr/bin/bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r13-quarantine-bounds.sh --tool "$T"; echo "installed rc=$?"  # expect 0
```

Note: a baseline copy in `/var/tmp` sits outside `tools/`, so it resolves `REPO_ROOT` as `/var` and
`VERIFY_BIN` as `/var/tools/souji-verify.sh` (`:127-137`), and it would exit 1 "receipt engine
missing". The fixture must pass `SOUJI_VERIFY_BIN=<lane>/tools/souji-verify.sh` (and `SOUJI_Q_LEDGER`,
`SOUJI_Q_SHOKUNIN_ROOT`) explicitly. Otherwise "red on baseline" is a missing-engine error, not a
timeout result. This is a vacuous-red trap.

The fixture must contain these cases. Each needs an rc assertion, a RESULT token, a SUMMARY line,
a shim marker where relevant, and a byte check of source and qpath:
- **regular success:** DELETED, rc 0.
- **pre-move mv delay:** `STAGE2-FAILED` with a timeout token, source present, no qpath, rc 3, run
  ends within T+K plus slack.
- **post-move mv delay:** qpath present, source absent, residue reported, no `QSTAGE stage3`, rc 3.
- **tracked git-mv delay:** git shim on ` mv `; index.lock state reported.
- **target-gated sha256sum delay at pin:** `NOT-AUTHORIZED`/`DRY-RUN-BLOCKED` with digest timeout,
  unmoved.
- **post-stage-2 FIFO via hook:** `ABORTED`, staged copy retained, rc 3. Baseline: rc 2 with no
  RESULT (red).
- **unreadable descendant:** refused with diagnostic, rc 3. Baseline: rc 123 (red).
- **dry-run on every case:** tree byte- and mtime-identical, no `.ufo-quarantine`, printed CMD
  identical to the live argv.
- **`--list` with a timeout on row 1 and a valid row 2:** row 2 not processed after the stop rule,
  SUMMARY present.
- **override `0`:** rejected with a usage error (rc 2).

Every fixture path must come from `mktemp -d /var/tmp/...` with a trap cleanup. Fixture git must use
`-c maintenance.auto=false`. Any `touch -d` on a FIFO must be wrapped in `/usr/bin/timeout`
(**to-verify**: GNU touch opens with O_NONBLOCK and falls back to utimensat).

## Limitations

- I did not run the tool, the engine, the selftests or a fixture. Every errexit and exit-code outcome
  above is **[INFERENCE]** from bash semantics and the cited lines.
- A1's timing reconstruction is inference. The 2026-10-19 run's stdout, driver log and `--hold`
  value were not available, and I did not read `census/operator-sweep-20261018/` or `-20261019/`
  content.
- Three items are unverified: GNU timeout's `+` getopt stop (A3), `rg` skipping FIFOs during
  traversal, and GNU touch on FIFOs.
- I did not check whether any live fleet target lives on a nested subvolume or mount (EXDEV
  exposure).
- I read nothing outside the lane except `/usr/bin` tool help text and mount metadata.
