# Souji r13 W1 — BoundQuarantine (Q8 tool fix + Q6 candidate-selection removal)

Seat: `SoujiR13.BoundQuarantine` (leaf). Lane root:
`/home/vgpnk/Projects/shokunin/souji-shokunin`. Baseline HEAD:
`31984f473ce4bdab61a99b16cca194b28108cb81` (verified with
`git -C <lane> rev-parse HEAD`). Certification stays OFF; this is a tool
change plus a fixture, not a verdict.

## Write set (only these paths touched)

| path | state |
|---|---|
| `tools/souji-quarantine.sh` | modified (`M`) |
| `tests/fixtures/r13-quarantine-bounds.sh` | new (`??`, mode 755) |

No commits, no installs/upgrades (nothing to record under the tooling
directive), no operator-sweep or secret reads, no shared bookkeeping files.

## 1. Q8 — bounded per-target staging / digest / delete

All bounds are fixed literals at the call site, GNU form
`timeout --kill-after=10 <secs> <cmd>`:

| step | bound | line |
|---|---|---|
| file digest (`file_sha`) | 120 s | `tools/souji-quarantine.sh:715` |
| directory manifest digest (`dir_digest`) | 300 s | `:725` |
| intro-blob digest (second check) | 120 s | `:310` |
| receipt engine per target (stage 1 and stage 4 prong 1) | 120 s | `:1143` |
| staging `git mv` | 60 s | `:520` |
| staging `mv` | 60 s | `:522` |
| final `rm -rf` from quarantine | 120 s | `:562` |
| `git rm --cached` index cleanup | 60 s | `:571` |
| special-file scan (`find`) | 60 s | `:764` |

Facts on the effective binaries (probed with absolute paths, because this
session's interactive shell has shimmed `mv`/`timeout`/`sha256sum`
builtins that are **not** what a child `bash` resolves):
`/usr/bin/timeout (GNU coreutils) 9.11`, `/usr/bin/mv (GNU coreutils) 9.11`,
`/usr/bin/sha256sum (GNU coreutils) 9.11`.

GNU `timeout` rejects options **after** DURATION:
`/usr/bin/timeout 1 --kill-after=2 sleep 5` →
`timeout: failed to run command ‘--kill-after=2’: No such file or directory`, rc 127.
So the option order used throughout is `--kill-after` **before** the
duration. Group-kill and escalation were probed:
`/usr/bin/timeout --kill-after=2 1 bash -c 'sleep 5 | cat >/dev/null'` → rc 124
in 1 s with **no** surviving `sleep 5` (no M44 orphan class);
`/usr/bin/timeout --kill-after=1 1 bash -c 'trap "" TERM; sleep 4'` → rc 137.

### 1.1 Regular-files-only refusal (before any read)

New pre-flight in the live `flow_one` wrapper (`:1192–1227`), running for
dry-run and real runs alike, before `s18_flow_one` (which calls the engine):

- `q_special_type` (`:748`) uses `stat -c %F`; only `regular file`,
  `regular empty file`, `directory` pass. FIFO, socket, char/block device,
  symlink, unstatable → `RESULT <path> NOT-AUTHORIZED|DRY-RUN-BLOCKED special-file-refused`.
- `q_first_special` (`:762`) scans a directory subtree for
  `-type l|p|s|b|c` under the 60 s bound; first offender →
  `special-descendant offender=<path>`; scan timeout → `special-scan-timeout`;
  unreadable subtree → `special-scan-failed`.
- Missing paths are deliberately **not** pre-refused: they still reach the
  engine so `metadata-prune`/`unreachable` receipts are preserved
  (the internal selftest's `SKIP1` target `wt-inside` is an absent path).
- Symlinks keep their existing `symlink-refused` refusal path.
- Defense in depth: `file_sha` itself now requires `[ -f ] && [ ! -L ]`
  (`:714`), `content_digest` maps non-regular to rc 2 (`:743`), and
  `dir_digest` still routes through `s18_scope_ok` (`:724`).

### 1.2 Fail-closed diagnostics instead of silent `set -e` death

Baseline facts (cited from `git show 31984f4:tools/souji-quarantine.sh`):
`pin_sha=$(content_digest "$ct")` at baseline **:498** and
`now_sha=$(content_digest "$QPATH"); local dig_rc=$?` at baseline **:284**
both run under `set -euo pipefail` (baseline `:121`), so any digest failure
exits the whole script with no `RESULT`/`SUMMARY` and later targets skipped;
a rc-2 exit collides with the usage code. SafetyPaths independently reached
the same conclusion.

Now:

- stage 1: `pin_sha=$(content_digest "$ct") || pin_rc=$?` (`:480`), then
  rc 2 → `special-file-refused`, rc 124/137 → `digest-timeout`,
  other → `digest-failed` (`:481–488`); counters/`RC=3` via `block_one`.
- stage 4 pin: rc captured without excitation (`:266`) and classified into
  `pin=FAIL symlink-present-in-quarantine` (rc 2, token preserved),
  `pin=FAIL digest-timeout rc=…`, or `digest-mismatch` (token preserved for
  the A1 tamper selftest) (`:268–277`).
- receipt engine timeout → `V_VERDICT=ERROR`, evidence
  `receipt-engine-timeout rc=… bound=120s` (`:1141–1146`) → NOT-AUTHORIZED.
- obsidian vault digests no longer abort the run on failure
  (`file_sha … || vault_sha=""` `:330`; `dir_digest … || vault_rc=$?` `:334`).

### 1.3 Staging failure, partial residue, never delete-after-timeout

Stage 2 (`:512–528`) captures the move rc and, on any non-zero rc, calls
`q_stage2_fail` (`:789`) which reports `rc`, `source=present|absent`,
`residue=<qpath>|none` (a partially created destination is **left in place**
and reported, never undone) and, for `git mv`, `index-lock=present-never-removed`
when `<repo>/.git/index.lock` exists. It emits
`QSTAGE stage2-failed …` plus `RESULT <path> STAGE2-FAILED <mv|git-mv>-timeout|-failed …`,
sets `RC=3`, and returns before stage 3/4/5 — so a timed-out move can never
reach the delete step.

Cross-device protection (SafetyOperator): staging is refused with
`cross-device-staging` unless `stat -c %d` of the target's parent equals the
repo root's device (`:1219–1226`). Rationale: GNU mv falls back to
copy-then-unlink across devices, and a bound hit during the unlink could
leave the LIVE source half-removed. `mv --no-copy -T` (`:522`) is a second
belt: a same-device-less rename fails instead of copying, and `-T` prevents
nesting under a raced destination. `--no-copy`/`-T` exist in the probed
`mv --help` (GNU 9.11).

Stage 5 (`:560–573`) bounds the `rm`; a timeout or error yields
`QSTAGE stage5 ABORTED rm-timeout|rm-failed rc=… staged-copy-kept` and
`RESULT ABORTED`, keeping whatever `rm` did not remove (the copy is already
in quarantine, never the live tree). `rm` only runs after `SC_PASS=1`.

### 1.4 Preserved contracts

- Receipts/tokens unchanged: `QVERDICT` fields, `RESULT` outcomes, `SUMMARY`
  counters, `DRY-RUN-PASS`/`DRY-RUN-BLOCKED`, receipt pins (`--list`), and
  the stale pass/fail semantics. Only new reason tokens were added
  (`special-file-refused`, `special-descendant`, `special-scan-timeout`,
  `special-scan-failed`, `cross-device-staging`, `digest-timeout`,
  `digest-failed`, `mv-timeout`, `git-mv-timeout`, `rm-timeout`).
- Dry run still computes the stage-1 verdict for real and prints commands;
  the printed commands now show the bounded forms (`:497–506`).
- Dead duplicates removed rather than left as apparent-only bounds: the
  unbounded early `file_sha`/`dir_digest` and the single early
  `content_digest` (baseline `:184/:186/:196`) are gone, and the superseded
  base `run_verify` (baseline `:212–230`) is gone. The only definitions left
  are the bounded ones (`file_sha`/`dir_digest` at `:712–731`, the relocated
  `content_digest` at `:733`, the live `run_verify` at `:1136`). The late
  duplicates that previously shadowed the early ones no longer shadow
  anything.
- `usage()` header range moved with the header text: `:178` now prints
  lines 2–139 (Q8 block included); the code starts at `:140`.

## 2. Q6 — no automatic candidate engine selection

Baseline `:134–138` silently preferred `tools/cand-merge-verify.sh` whenever
it existed next to the tool (it does exist in the working tree, 50 864 B),
over the installed `tools/souji-verify.sh`. That binds a no-relay verdict to
relay candidate bytes rather than measured installed bytes (QUALITY Q6;
round-11 `cert-16.json` relay lesson).

Removed; selection is now exactly (`:158`):

```
VERIFY_BIN="${SOUJI_VERIFY_BIN:-$REPO_ROOT/tools/souji-verify.sh}"
```

Rationale (also in-file at `:151–157`): an explicit operator pin
(`SOUJI_VERIFY_BIN`, used by fixtures and the r9 runner) is preserved, but
there is no implicit filesystem-dependent fallback. Scope limit: this fixes
*this tool's* selection only; other candidate files in `tools/` are
untouched and are not claimed to be fixed. No certification claim.

## 3. Fixture — `tests/fixtures/r13-quarantine-bounds.sh`

Isolated, self-contained, `/var/tmp` only (Q4 greps on the file:
`grep -c 'TMPDIR:-/tmp'` → 0; `grep -c '/var/tmp'` → 3), trap removes the
whole scratch dir.

### Invocation contract

```
# patched (defaults to <lane>/tools/souji-quarantine.sh and
# <lane>/tools/souji-verify.sh)
bash tests/fixtures/r13-quarantine-bounds.sh
# arbitrary tool (e.g. baseline copy), same fixture
bash tests/fixtures/r13-quarantine-bounds.sh --tool /var/tmp/<dir>/souji-quarantine.sh
# optional: --verify PATH, --case ID (repeatable), --help
```

- `--tool` / `SOUJI_QUARANTINE_BIN` select the tool (`:45`).
- `--verify` defaults to the lane engine (`:46`); it is exported as
  `SOUJI_VERIFY_BIN` for every run, so a baseline copy under `/var/tmp`
  (whose own `$REPO_ROOT/tools/souji-verify.sh` is absent) still gets the
  installed engine.
- Every run sets `SOUJI_QUARANTINE_ALLOW_LIVE=1` for the isolated mktemp
  repo, `SOUJI_Q_SHOKUNIN_ROOT=<scratch>`, `SOUJI_Q_LEDGER=<scratch>/ledger.tsv`,
  and passes `--hold 0` (`:133–138`). A red therefore never depends on the
  live-fleet guard's exit 4 (the guard derives from the *tool's* location).
- Each run is wrapped in `/usr/bin/timeout --kill-after=5 20 bash "$TOOL" …`;
  rc 124/137 is reported as `HANG`, never PASS (`:107–126`).
- Output: `CASE<TAB><id><TAB>PASS|FAIL|HANG<TAB><detail>` and
  `SUMMARY<TAB>total=… failed=… hung=…`; exit 0 iff every selected case
  passes, 1 otherwise, 2 usage/environment.
- Each run prints `TOOL<TAB><path><TAB>sha256=<digest>` and `VERIFY<TAB><path>`
  (measured with the real absolute `sha256sum`).

### Clock compression

Cases 04/05 prepend a PATH shim dir:

- `timeout` shim (`:134`): accepts exactly `--kill-after=N DURATION COMMAND…`
  and re-execs the real GNU timeout as `--kill-after=1 2 COMMAND…`. It only
  compresses the clock; a tool that never calls `timeout` (the baseline) is
  unaffected and hangs.
- `mv` / `sha256sum` shims (`:147`): `sleep 30` then `exec <real binary> "$@"`.

### Case set and stable ids

| id | scenario | expected on patched tool |
|---|---|---|
| R13Q8-01 | regular stale file, full flow | rc 0, `RESULT … DELETED stale`, source gone |
| R13Q8-02 | FIFO target, `--dry-run` | rc 3, `DRY-RUN-BLOCKED special-file-refused`, FIFO intact, no `.ufo-quarantine` |
| R13Q8-03 | directory with FIFO child, `--dry-run` | rc 3, `DRY-RUN-BLOCKED special-descendant`, FIFO intact |
| R13Q8-04 | delayed `mv` | rc 3, `STAGE2-FAILED mv-timeout`, source intact, no quarantine copy, no `DELETED`, `SUMMARY` present |
| R13Q8-05 | delayed `sha256sum` | rc 3, `NOT-AUTHORIZED digest-timeout`, source intact, no quarantine copy |

Predicted baseline (HEAD 31984f4) red — **design prediction, not yet
executed by this seat**:

- 01 PASS (control).
- 02 FAIL: baseline invokes the engine (SAFE stale), then dies in the
  unbounded pin at baseline `:498`; live baseline `file_sha` (`:722–725`)
  has `[ -f ]`, so a FIFO exits silently rc 1 with no `RESULT`/`SUMMARY`
  (no hang — this differs from an earlier assumption that the FIFO case
  hangs on `sha256sum`).
- 03 FAIL: directory pin routes to `dir_digest` → `s18_scope_ok` rejects the
  FIFO child → rc 2 → silent exit rc 2 (collides with usage code).
- 04 HANG at the fixture's 20 s outer bound: baseline `mv` (`:536`) is
  unbounded and the shim sleeps 30 s.
- 05 HANG at 20 s: baseline `sha256sum` inside `file_sha` (`:724`) is
  unbounded.
- Fixture exits 1 with 4 reds, 1 pass.

Both FIFO reds are observed *behavioural* reds (missing refusal token and
missing `SUMMARY`), but they fail on the baseline's silent crash, not on an
observed hang. I make no claim that the patched tool "newly closes" a FIFO
hang; the claim is: special targets are now refused by a pre-flight with a
diagnostic, and the digest/staging/delete calls are bounded.

## 4. Checks L1 must run (not executed here — wave rules)

```
shellcheck -S warning \
  /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-quarantine.sh \
  /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r13-quarantine-bounds.sh

TMPDIR=/var/tmp timeout 900 bash \
  /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-quarantine.sh --selftest

timeout 120 bash \
  /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r13-quarantine-bounds.sh
# expect 5 CASE lines PASS and exit 0

B=$(mktemp -d /var/tmp/r13-baseline.XXXXXX)
git -C /home/vgpnk/Projects/shokunin/souji-shokunin \
  show 31984f4:tools/souji-quarantine.sh > "$B/souji-quarantine.sh"
chmod +x "$B/souji-quarantine.sh"
timeout 300 bash \
  /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r13-quarantine-bounds.sh \
  --tool "$B/souji-quarantine.sh"
# expect exit 1: 01 PASS; 02/03 FAIL; 04/05 HANG
rm -rf -- "$B"

# Q8 audit (see caveat below): expect >=1
grep -nE 'timeout --kill-after=[0-9]+ [0-9]+[smh]? .*(mv|sha256sum)' \
  /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-quarantine.sh

git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --check -- \
  tools/souji-quarantine.sh tests/fixtures/r13-quarantine-bounds.sh
```

### QUALITY Q8 test caveat (needs L1/criteria decision)

QUALITY Q8's published test is
`grep -nE 'timeout [0-9]+[smh]? .*(mv|sha256sum)' <tool>` ≥ 1. That regex
cannot match a **GNU-valid** `timeout --kill-after=… <secs> <cmd>` call,
because coreutils `timeout` rejects options after DURATION (probe above:
rc 127). My call sites are `timeout --kill-after=10 120 sha256sum …` and
`timeout --kill-after=10 60 mv …`, so the literal published grep returns 0 —
not because the call is unwrapped, but because the criterion's syntax
predates the `--kill-after` requirement. Proposed replacement (provided to
`SoujiR13.VerifySuiteDraft`):

```
grep -nE 'timeout --kill-after=[0-9]+ [0-9]+[smh]? .*(mv|sha256sum)' tools/souji-quarantine.sh
```

plus the fixture above (behavioural). Do not "fix" this by reordering to
`timeout 120 --kill-after=10 …`; that invocation fails at runtime.

## 5. Risks / limitations

1. **Nothing executed by me.** Per wave rules I did not run `bash -n`,
   shellcheck, `--selftest`, or the new fixture. Syntax and the predicted
   reds above are code-grounded, not observed. L1 owns the gate.
2. `mv --no-copy` exists on the probed GNU coreutils 9.11; on an older host
   every untracked stage move fails closed (`STAGE2-FAILED`), not silently
   copies. Host pinning is the lane's existing convention.
3. Cross-device detection compares the source's *parent* device with the
   repo root device; a directory that is itself a mount point passes the
   check and relies on `mv --no-copy`/rename failing `EBUSY` (fail-closed,
   no copy).
4. Directory targets now pay one bounded `find` (≤60 s) before the engine.
   That is deliberate fail-closed cost; huge trees may hit
   `special-scan-timeout` rather than proceed.
5. The 120 s receipt-engine bound is a new failure mode: a legitimately
   slow engine now yields NOT-AUTHORIZED. Chosen over unbounded staging.
6. Stage 3's serial `sleep "$HOLD"` is unchanged. SafetyPaths' reading that
   LOG.md:373's "hung after 3 files" fits 3 × 450 s > the 20-minute driver
   timeout is plausible but is **their inference**; bounding mv/digest does
   not shorten the hold window, so M43's driver-timeout cause is not
   addressed by this slice and must not be claimed closed.
7. A timed-out `git mv` may leave `.git/index.lock`; it is reported and
   never removed here (per instruction). Recovery is operator-owned.
8. Partial stage-2 residue is reported but not rolled back. On a same-device
   rename the residual case is a missing destination or an EEXIST race; on
   `mv --no-copy` no partial copy can be created.
9. Planned-but-unverified compatibility: the internal selftest's D1
   (`git -C` + `rm -rf` substrings), P1/P2/P3 tokens, N2 `unreachable`,
   SKIP1 absent target, and A1 `digest-mismatch` were traced against the
   edits but not executed. The r9 runner's `sha256sum` counter shim still
   intercepts through `timeout` (PATH resolution at exec time), and its
   `SOUJI_VERIFY_BIN` pin is still honored.
10. The Q6 removal changes engine selection for this tool only. A round
    verdict that names installed `souji-verify.sh` bytes is still L1's
    measurement to make; I claim no certification.

## 6. Blockers

None for authoring. The only blocker is procedural: this seat may not run
the verification commands, so L1 must execute §4 before any admission.
