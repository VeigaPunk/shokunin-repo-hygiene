# Vadv54StubFix — scope `p6repo/.git` stub to the P6 case

STATUS: DONE — stub now exists only while P6 runs; every case's verdict byte-identical (before/after under /var/tmp byte copy).

Claim served: C3(e) — JjTrialSouji hazard 1 (`/home/vgpnk/Projects/shokunin/.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md` :76). The harness created an EMPTY `p6repo/.git` stub during fixture setup (old :176) and never removed it, so the committed run tree `tests/vault/vadv54-run/` retained a `p6repo/.git` dir after every harness run. jj then treats `p6repo/` as a nested repo and reports tracked `p6repo/one.txt` / `p6repo/inner/keep.txt` as deleted (`D` rows), committable as phantom deletions under a directory pathspec.

OWN ONLY file changed: `tests/vault/vadv54-harness.sh` (no other file touched).

## Diff (vs lane file before edit)

```diff
@@ -173,7 +173,7 @@
 mkdir -p "$P/p1dir"
 printf 'alpha\n' > "$P/p1dir/a.txt"
 printf 'beta\n' > "$P/p1dir/b.txt"
-mkdir -p "$P/p6repo/.git" "$P/p6repo/inner"
+mkdir -p "$P/p6repo/inner"
 printf 'p6 payload one\n' > "$P/p6repo/one.txt"
 printf 'p6 payload inner\n' > "$P/p6repo/inner/keep.txt"
 ln -s "$P/p2.md" "$P/alias-link.md"
@@ -270,8 +270,16 @@
   record P5 p PASS "SAFE tolerated for a distinct copy — but 'vault' semantics unchecked" "$RC" "$OUT" "refused"
 fi
 
-# P6 vault copy nested inside the source directory.
+# P6 vault copy nested inside the source directory. The p6repo/.git stub makes
+# the fixture classify as a repo-root; it must exist only while this case runs
+# because a leftover stub under tests/vault/vadv54-run makes jj treat p6repo as
+# a nested repo and report its tracked files as deleted (JjTrialSouji hazard 1).
+mkdir -- "$P/p6repo/.git"
+# Fail-closed cleanup for interrupted runs: rmdir refuses a non-empty stub.
+trap 'rmdir -- "$P/p6repo/.git" 2>/dev/null || true' EXIT
 run_tool "$LED_P" "$P/p6repo"
+rmdir -- "$P/p6repo/.git" || printf 'vadv54-harness: refusing to remove non-empty stub %s\n' "$P/p6repo/.git" >&2
+trap - EXIT
 v=$(norm_v)
 if [ "$v" = SAFE ]; then
   record P6 p FAIL "NOT-SAFE — the receipt's vault copy lives inside the source directory being evaluated" "$RC" "$OUT" "false-SAFE: removing the repo destroys its own vault copy" '"severity":"critical"'
```

Design notes:

- Why the stub is needed at all: `tools/souji-verify.sh` classifies a dir with `.git` as `repo-root` (:423-424 `if [ -d "$target" ] && [ -d "$target/.git" ]; then evaluate_repo_root`) — that IS the P6 fixture (verdict evidence `unpushed=0 dirty=0` comes from `evaluate_repo_root`). So it cannot simply be deleted; it must exist during the P6 `run_tool` call.
- Why moving creation is verdict-neutral: the only earlier consumers of `p6repo` are `dir_digest` calls (:193-194), which prune `./.git` (`find . -path './.git' -prune -o -type f`, harness :64-65) — digest identical with or without the stub. `LED_P` is written before any case runs; ledgers/digests unchanged.
- `rmdir` (not `rm -rf`) refuses a non-empty stub — if the tool under test ever writes inside `.git`, the harness fails loudly to stderr instead of deleting evidence.
- An EXIT trap covers interrupted runs (SIGINT/TERM, `set -u` failures): it `rmdir`s the stub if still empty, best-effort (`|| true`, stderr suppressed so no noise on the empty/absent double-run path). The trap is installed just before `run_tool` and disarmed right after `rmdir`, so it exists only during P6 and cannot interfere with earlier/later cases.

## Verification (ALLOWED-EXEC only — lane never executed)

Setup: `cp -a` of `tools/souji-verify.sh`, `tools/souji-verify.spec.md`, `tests/vault/vadv54-harness.sh`, `corpus/knowledge/obsidian-ledger.tsv` into `/var/tmp/souji-r17-Vadv54StubFix/{before,after}/` (harness derives REPO_ROOT from its own path; `--out` pointed outside the copies; VAULT snapshot is the harness's own read-only `find|sha256sum` against `/home/vgpnk/Documents/shokoknowledge` — observed only, never written).

- `bash -n` → OK. `shellcheck -S warning` → exit 0, no diagnostics (ShellCheck 0.11.0, already installed).
- BEFORE run (original harness): `bash tests/vault/vadv54-harness.sh --out ../before.json`, exit 0, 2.68 s. Leftover confirmed: `tests/vault/vadv54-run/p/p6repo/.git` present (empty dir) — hazard reproduced.
- AFTER run (edited harness): exit 0, 2.63 s. `ls -ld …/p6repo/.git` → "No such file or directory" — stub removed in-run. `p6repo/one.txt`, `p6repo/inner/keep.txt` intact.
- Verdict comparison (Python, `before.json` vs `after.json`): identical case-id sets; per-case `(verdict, rc, note)` tuples **all equal**; `totals` both `{"pass":16,"fail":2,"warn":3,"info":1}`; per-case `out` fields identical after normalizing the `/before/→/after/` path prefix (no OUT-DIFF). The only stdout diffs were `head -c 150` truncation shifts caused by the one-character path-length difference — no content change. Q6 (swap-race INFO case) showed identical output `SAFE=0 NOT-SAFE=100 other=0` in both runs.
- No `vadv54-harness: refusing to remove non-empty stub` diagnostic emitted (stderr empty beyond the normal run lines) — `rmdir` succeeded.

Both stdout tails:

```
==== vadv-54 summary ====
PASS=16 FAIL=2 WARN=3 INFO=1  readonly_ok=true  tool_sha_stable=yes
```

## Pre-existing observations (unchanged by this edit — disclosed, not fixed)

- **S0 FAIL in both runs** (`souji-verify.sh --selftest` exit 1 after `PASS H1…`; 600-char `out` cap hides the failing line). Identical before/after → unrelated to the stub change; likely environmental to the byte-copy fixture tree. The lane's own committed harness evidence should be checked against a lane run by whoever owns gate execution.
- The lane worktree **currently still contains the stale stub** `tests/vault/vadv54-run/p/p6repo/.git` (left by the last historical run; jj-visible phantom `D` rows on `one.txt`/`inner/keep.txt` until removed). Not in my OWN ONLY scope to delete; the next harness run's `rm -rf -- "$WORK"` (:47) removes it, and with this edit no run will ever leave it again. L1 may want a one-line `rmdir` by whoever owns the run tree, or let the next harness execution clean it.

## Files changed

- `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/vault/vadv54-harness.sh` — scoped stub lifetime to P6 (10 insertions, 2 deletions).

## Commands run (evidence)

| Command | Result |
|---|---|
| `bash -n tests/vault/vadv54-harness.sh` | OK |
| `shellcheck -S warning tests/vault/vadv54-harness.sh` | exit 0, silent |
| `bash tests/vault/vadv54-harness.sh --out /var/tmp/…/before.json` (copy, unedited) | exit 0; stub left behind |
| same, edited copy | exit 0; stub absent; verdicts identical |
| `diff`/`python3` verdict comparison | all 22 case `(verdict,rc,note)` equal; `out` equal modulo path prefix |

## Tooling

No installs needed — `shellcheck` 0.11.0 already at `/usr/bin/shellcheck`; `rg`, `python3` present. No pacman transactions attempted.

## Risks / blockers

- Residual risk: an interrupted run between `mkdir` and `rmdir` relies on the EXIT trap; if the process is SIGKILLed the stub persists until the next run's `rm -rf "$WORK"`. Acceptable — next-run cleanup is unconditional and the stub is empty+untracked.
- No blockers. `/var/tmp/souji-r17-Vadv54StubFix/` deleted after reporting.
