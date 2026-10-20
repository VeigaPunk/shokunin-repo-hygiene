# Souji r13 W1 — BoundQuarantine (Q8 bounds, Q6 selection, shellcheck)

Seat: `SoujiR13.BoundQuarantine` (leaf). Lane root:
`/home/vgpnk/Projects/shokunin/souji-shokunin`.
Baseline HEAD at authorship: `31984f473ce4bdab61a99b16cca194b28108cb81`.
Integration state: L1's suite ran at `6ed10a7` and reverted the stage-5
rm/git-rm bounds coherently (see §1.3); this revision fixes that suite's one
failing case (05) and the shellcheck warnings L1 reported. Certification
stays OFF; nothing here is a deletion verdict.

## Write set

| path | state |
|---|---|
| `tools/souji-quarantine.sh` | modified |
| `tests/fixtures/r13-quarantine-bounds.sh` | new, mode 755 |
| `.ufo/waves/round-13/w1/BoundQuarantine.md` | this report |

No commits, no installs, no operator-sweep or secret reads.

## 1. Q8 — bounded per-target staging / digest

Bounds are fixed literals at the call site, GNU form
`timeout --kill-after=10 <secs> <cmd>`:

| step | bound | line |
|---|---|---|
| file digest (`file_sha`) | 120 s | `tools/souji-quarantine.sh:710` |
| directory manifest digest (`dir_digest`) | 300 s | `:720` |
| intro-blob digest (second check) | 120 s | `:310` |
| receipt engine per target (stage 1 and stage 4 prong 1) | 120 s | `:1137` |
| staging `git mv` | 60 s | `:518` |
| staging `mv` | 60 s | `:520` |
| special-file scan (`find`) | 60 s | `:759` |

Stage-5 deletion is **not** time-bounded (L1 reverted that; see §1.3) and no
bounded-delete claim is made.

Facts about the effective binaries (probed by absolute path, because this
session's interactive shell has shimmed `mv`/`timeout`/`sha256sum` builtins
that a child `bash` does not resolve):
`/usr/bin/timeout (GNU coreutils) 9.11`, `/usr/bin/mv (GNU coreutils) 9.11`,
`/usr/bin/sha256sum (GNU coreutils) 9.11`.
GNU `timeout` rejects options after DURATION
(`/usr/bin/timeout 1 --kill-after=2 sleep 5` → rc 127,
`failed to run command ‘--kill-after=2’`), so `--kill-after` precedes the
duration everywhere. Group kill and escalation were probed:
`timeout --kill-after=2 1 bash -c 'sleep 5 | cat >/dev/null'` → rc 124 in 1 s
with no surviving `sleep 5`; `timeout --kill-after=1 1 bash -c 'trap "" TERM; sleep 4'` → rc 137.

### 1.1 Regular-files-only refusal (before any read)

Live `flow_one` pre-flight (`:1186–1220`), applied before `s18_flow_one`
(which calls the engine), for dry-run and real runs alike:

- `q_special_type` (`:743`) via `stat -c %F`: only `regular file`,
  `regular empty file`, `directory` pass. FIFO/socket/char/block device/
  symlink/unstatable → `special-file-refused`.
- `q_first_special` (`:757–767`) scans a directory subtree for
  `-type l|p|s|b|c` under the 60 s bound: first offender →
  `special-descendant offender=…`, bound hit → `special-scan-timeout`,
  unreadable subtree → `special-scan-failed`.
- Missing paths are deliberately not pre-refused, so `metadata-prune`
  (absent worktree dir, internal selftest SKIP1) and `unreachable` receipts
  still come from the engine. Symlinks keep their own `symlink-refused`.
- Defense in depth: `file_sha` requires `[ -f ] && [ ! -L ]` (`:709`),
  `content_digest` maps non-regular to rc 2, `dir_digest` keeps
  `s18_scope_ok` (`:719`).
- Cross-device staging is refused (`cross-device-staging`, `:1210–1220`)
  when the target parent's `stat -c %d` differs from the repo root's:
  GNU mv would copy-then-unlink, and a bound hit during the unlink could
  leave the LIVE source half-removed. `mv --no-copy -T` (`:520`) is the
  second belt (probed: both flags in GNU 9.11 `mv --help`).

### 1.2 Fail-closed diagnostics instead of silent `set -e` death

Baseline facts (`git show 31984f4:tools/souji-quarantine.sh`): the pin at
baseline `:498` and the second-check capture at baseline `:284` are simple
assignments under `set -euo pipefail` (baseline `:121`), so a digest failure
exited the whole run with no `RESULT`/`SUMMARY`, skipped later targets, and
rc 2 collided with the usage code.

Now:

- stage 1: `pin_sha=$(content_digest "$ct") || pin_rc=$?` (`:478`), then
  rc 2 → `special-file-refused`, rc 124/137 → `digest-timeout`,
  other → `digest-failed` (`:479–486`).
- stage 4 pin: rc captured (`:266`); rc 2 keeps
  `pin=FAIL symlink-present-in-quarantine`, 124/137 →
  `pin=FAIL digest-timeout rc=…`, else `digest-mismatch` (`:274`), which the
  A1 tamper selftest greps.
- receipt engine timeout → `V_VERDICT=ERROR` with evidence
  `receipt-engine-timeout rc=… bound=120s` (`:1137`).
- moved-to-obsidian vault digests no longer abort the run on failure
  (`ledger_pin=$(file_sha …) || ledger_pin=""` `:322`;
  `vault_sha=$(file_sha …) || vault_sha=""` `:330`;
  `vault_sha=$(dir_digest …) || vault_rc=$?` `:334`).

### 1.3 Staging failure, residue, and the stage-5 revert (L1-owned)

Stage 2 (`:516–526`) captures the move rc; on failure `q_stage2_fail`
(`:784`) reports `rc`, `source=present|absent`, `residue=<qpath>|none`,
never undoes a partial move, and for `git mv` adds
`index-lock=present-never-removed` when `<repo>/.git/index.lock` exists.
It emits `QSTAGE stage2-failed` + `RESULT <path> STAGE2-FAILED <mv|git-mv>-timeout|-failed`,
sets `RC=3`, and returns before stages 3–5.

L1 reverted the stage-5 bounds at `6ed10a7`. Current stage 5 (`:558–568`)
is the baseline behavior: unbounded `rm -rf` only after `SC_PASS=1`; on
failure it reports `rm-failed residue-may-be-partial` and ABORTED (an `rm`
killed mid-way can leave a partial staged copy, so the old
`staged-copy-kept` wording was wrong and is gone). `git rm --cached` is
likewise unbounded. No new bounded-delete claim; the header Q8 block states
this explicitly.

The staging/pin guarantee stands: a staging or pin timeout never advances to
deletion.

### 1.4 Preserved contracts

`QVERDICT` fields, `RESULT` outcomes, `SUMMARY` counters,
`DRY-RUN-PASS`/`DRY-RUN-BLOCKED`, receipt pins (`--list`), and stale
pass/fail semantics are unchanged; only additive reason tokens were added
(`special-file-refused`, `special-descendant`, `special-scan-timeout`,
`special-scan-failed`, `cross-device-staging`, `digest-timeout`,
`digest-failed`, `mv-timeout`, `git-mv-timeout`). Dry run still computes
stage-1 verdicts and prints commands; the staging/digest prints are bounded
(`:493–499`), while the `rm`/index prints are baseline (`:502`, `:504`).
Dead unbounded duplicates were removed rather than left as apparent-only
bounds: early `file_sha`/`dir_digest`/`content_digest` (baseline
`:184/:186/:196`) and the superseded base `run_verify` (baseline `:212–230`);
one bounded definition each remains (`:707`, `:717`, `:728`), plus the live
`run_verify` (`:1130`). `usage()` prints lines 2–139 (`:178`).

### 1.5 Shellcheck remediation (L1-reported; no suppressions added)

| code | location (pre-fix) | fix |
|---|---|---|
| SC2221/2222 | `is_secret_shaped` case | removed redundant `.env`; `*.env` already covers it (`:196`) |
| SC2221/2222 | stage-1 rel-path case | removed the no-op `''|.*/*|./*` arm; the `forbidden-prefix` arm and the separate dotdot case were already the whole behavior |
| SC2034 | `METHOD=$method` | removed the global assignment (the local `method` still feeds `QSTAGE` and `q_stage2_fail`) and its doc mention (`:260`) |
| SC2034 | `local nul_prefix` + `read` target | the NUL gate now uses `IFS= read -r -d '' <"$LIST_FILE"` (REPLY), same detection (`:617`) |
| SC2034 | `FAIL_REASON=pushed-unverifiable` | removed; the variable was never expanded (grep: zero `${FAIL_REASON}`) |
| SC2034 | `R_REASON` | removed **all** 11 assignments; grep shows zero expansions anywhere, so every one was dead |
| SC2155 | `local rmp="$(dirname …)"` | split: `local rmp` then `rmp=$(dirname -- "$qpath")` (`:569–571`) |
| SC2100 | `reason=source-equals-vault` | quoted RHS: `reason="source-equals-vault"` (`:887`) |

Verification greps after the cleanup: `grep -n 'R_REASON\|FAIL_REASON\|METHOD\|nul_prefix' tools/souji-quarantine.sh` → no matches.

## 2. Q6 — no automatic candidate engine selection

Baseline `:134–138` silently preferred `tools/cand-merge-verify.sh` (present
in the working tree) over the installed engine, binding a no-relay verdict
to relay candidate bytes (QUALITY Q6; round-11 relay defect). Removed.
Selection is exactly (`:158`):

```
VERIFY_BIN="${SOUJI_VERIFY_BIN:-$REPO_ROOT/tools/souji-verify.sh}"
```

Rationale is in-file (`:151–157`). Explicit `SOUJI_VERIFY_BIN` pins for
fixtures/r9 are preserved; no implicit filesystem-dependent fallback remains.
Scope: this tool only; other candidates in `tools/` are untouched and not
claimed fixed. No certification claim.

## 3. Fixture — `tests/fixtures/r13-quarantine-bounds.sh`

Isolated, `/var/tmp` only (`grep -c 'TMPDIR:-/tmp'` → 0; `grep -c '/var/tmp'` → 3),
trap removes the scratch tree.

### Invocation

```
bash tests/fixtures/r13-quarantine-bounds.sh [--tool PATH] [--verify PATH] [--case ID …]
```

- `--tool` / `SOUJI_QUARANTINE_BIN` (`:49`), default installed tool.
- `--verify` (`:50`) default lane engine, exported as `SOUJI_VERIFY_BIN` for
  every run so a `/var/tmp` baseline copy does not look for a missing
  sibling engine.
- Every run: `SOUJI_QUARANTINE_ALLOW_LIVE=1` (isolated mktemp repo; prevents
  a false exit-4 red from the location-derived guard),
  `SOUJI_Q_SHOKUNIN_ROOT=<scratch>`, `SOUJI_Q_LEDGER=<scratch>/ledger.tsv`,
  `--hold 0`, outer `/usr/bin/timeout --kill-after=5 20` (`:132–140`).
- Output `CASE<TAB><id><TAB>PASS|FAIL|HANG<TAB><detail>` + `SUMMARY`
  (`:110`, `:302`); rc 124/137 is HANG, never PASS; exit 0 iff all pass.

### Clock compression and gating

- `timeout` shim (`:142`) rewrites the tool's literal
  `timeout --kill-after=N <secs> cmd` to `--kill-after=1 2`, nothing else;
  a tool that never calls `timeout` (baseline) hangs.
- `mv`/`sha256sum` shims sleep 30 s **only when the last argument equals the
  gate path** (`:159`): staging destination (`$qp`) for case 04, stage-1
  target (`$t`) for case 05. This is the fix for the `6ed10a7` failure.

### Observed suite result at `6ed10a7` (L1-reported, not run by this seat)

Cases 01–04 PASS; case 05 returned rc 3 but without
`NOT-AUTHORIZED digest-timeout`. Cause (read from installed engine): the
receipt engine's `try_obsidian` hashes the ledger **unconditionally**
(`tools/souji-verify.sh:251`, `ledger_pin=$(file_sha "$LEDGER")`), so the
blanket sleeping `sha256sum` shim delayed the engine; the tool's 120 s engine
bound was compressed to 2 s by the `timeout` shim → `engine-timeout` →
`NOT-AUTHORIZED engine-error`. The gated shim now passes the ledger hash
straight through and delays only the tool's stage-1 digest, which is the
class under test.

### Cases and ids

| id | scenario | expected on patched tool |
|---|---|---|
| R13Q8-01 | regular stale file, full flow | rc 0, `RESULT … DELETED stale`, source gone |
| R13Q8-02 | FIFO target, `--dry-run` | rc 3, `DRY-RUN-BLOCKED special-file-refused`, FIFO intact, no `.ufo-quarantine` |
| R13Q8-03 | directory with FIFO child, `--dry-run` | rc 3, `DRY-RUN-BLOCKED special-descendant`, FIFO intact |
| R13Q8-04 | delayed `mv` (gated on qpath) | rc 3, `STAGE2-FAILED mv-timeout`, source intact, no copy, no `DELETED`, `SUMMARY` |
| R13Q8-05 | delayed `sha256sum` (gated on target) | rc 3, `NOT-AUTHORIZED digest-timeout`, source intact, no copy |

Predicted baseline red (design, not executed here): 01 PASS;
02 FAIL (silent rc 1 from baseline `:498`; live `file_sha` `[ -f ]` refuses
the FIFO without hashing, so no hang); 03 FAIL (silent rc 2 from
`dir_digest` → `s18_scope_ok` rejecting the FIFO child); 04/05 HANG at the
20 s outer bound (baseline staging/digest calls are unbounded; the gated
shims still sleep for the target/qpath). Fixture exits 1. The FIFO reds are
behavioural reds (missing diagnostic, missing `SUMMARY`), not observed hangs;
no claim that the patched tool newly closes a FIFO hang — the claim is
pre-flight refusal plus bounded staging/digest.

## 4. Checks for L1 (only the failed ones need rerunning)

```
shellcheck -S warning \
  /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-quarantine.sh \
  /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r13-quarantine-bounds.sh
# expect 0

timeout 120 bash \
  /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r13-quarantine-bounds.sh \
  --case R13Q8-05
# expect CASE R13Q8-05 PASS, SUMMARY failed=0, exit 0

# optional full fixture, patched and baseline-copy red:
timeout 120 bash …/r13-quarantine-bounds.sh
# expect 5/5 PASS
B=$(mktemp -d /var/tmp/r13-baseline.XXXXXX)
git -C /home/vgpnk/Projects/shokunin/souji-shokunin \
  show 31984f4:tools/souji-quarantine.sh > "$B/souji-quarantine.sh"
chmod +x "$B/souji-quarantine.sh"
timeout 300 bash …/r13-quarantine-bounds.sh --tool "$B/souji-quarantine.sh"
# expect exit 1: 01 PASS; 02/03 FAIL; 04/05 HANG
rm -rf -- "$B"

# Q8 audit (see caveat)
grep -nE 'timeout --kill-after=[0-9]+ [0-9]+[smh]? .*(mv|sha256sum)' \
  /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-quarantine.sh
```

### QUALITY Q8 test caveat (unchanged from the prior report)

The published regex `timeout [0-9]+[smh]? .*(mv|sha256sum)` cannot match a
GNU-valid `timeout --kill-after=…` call (coreutils rejects options after
DURATION; probe rc 127). Use
`timeout --kill-after=[0-9]+ [0-9]+[smh]? .*(mv|sha256sum)` plus the fixture.
Do not reorder; that invocation fails at runtime.

## 5. Risks / limitations

1. Not executed by this seat. Syntax, shellcheck, selftest and fixture
   outcomes are code-grounded predictions; L1 owns the gate.
2. The `6ed10a7` selftest's 16 failures were attributed by L1 to a missing
   Git identity in its isolated global config (runner will set
   author/committer env). Not a tool claim from this seat.
3. `mv --no-copy` requires GNU coreutils ≥9.5 (host 9.11 probed); an older
   host fails the untracked stage move closed (`STAGE2-FAILED`), never copies.
4. Cross-device detection compares the source parent device with the repo
   root; a directory that is itself a mount point passes and relies on the
   rename failing (`EBUSY`), still fail-closed.
5. Directory targets pay one bounded `find` (≤60 s) before the engine;
   big trees may get `special-scan-timeout` rather than proceed.
6. The 120 s engine bound is a new failure mode for a legitimately slow
   engine (NOT-AUTHORIZED) — chosen over unbounded staging.
7. Stage 3's serial `sleep "$HOLD"` is unchanged. SafetyPaths' inference
   that LOG.md:373's "hung after 3 files" fits 3 × 450 s is plausible but
   not adopted as fact; this slice does not shorten the hold and does not
   claim M43 closed.
8. Stage-5 deletion is unbounded per L1's revert; an interrupted `rm` can
   leave a partial staged copy (reported `residue-may-be-partial`), never a
   live-tree deletion.
9. Fixture gating depends on the tool's documented call shapes
   (`sha256sum -- <target>`, `mv … <qpath>`); a future shape change makes
   the case FAIL/HANG instead of silently passing, which is the intended
   direction.
10. Q6 removal covers this tool only; L1 still owns the installed-bytes
    measurement. No certification claim.

## 6. Blockers

None. Remaining work is L1's rerun of shellcheck and `R13Q8-05`.
