# S66SentinelScope — report, souji round 66 w1 (scope & safety audit)

Full deliverable: .ufo/waves/round-66/w1/S66SentinelScope/scope.md (Parts A+B, line-cited).
Method: source reading only; no instrument or candidate was executed; read-only `git show` against the lane;
no tooling installed; no host state touched. Scratch /fast/scratch/hyaku/souji-r66/S66SentinelScope used and removed.

## Part A — instruments (frozen 4576f10)
- c1-counter.py writes ONLY under --work plus the explicit --receipt path: every write primitive
  (slots :577-581/:906-911, regress fixture :921-925, case fixtures :335-450 incl. in-run helper code :186-189/:242-247
  which is always repo-joined, selftest :763-810, clone :590-594) resolves under the work join. No tempfile, no /tmp
  use besides the guard (:861-871). CONFIRMED.
- clean_env (:313-324) strips GIT_CONFIG_COUNT/PARAMETERS/GLOBAL/NOSYSTEM/SYSTEM, GIT_CONFIG_KEY_*, GIT_CONFIG_VALUE_*,
  GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_REPLACE_REF_BASE, GIT_NO_REPLACE_OBJECTS, GIT_INDEX_FILE,
  GIT_DIR, GIT_WORK_TREE — all five required groups CONFIRMED; injection values reach only the writer subprocess
  (case_env -> run_slot env_extra :473-486/:494-517), never the counter's own git calls.
- E-row fixtures write beside the repo at case-dir level: excludes.txt (:427-429), E3 global.gitconfig (:430-432);
  E4/E5 inside the fixture repo's .git only (:433-440); E6 writes nothing. CONFIRMED — not inside tools/.
- Host exposure: no fixture sets a host/global config; every write is under --work, which main() pins by realpath
  away from /tmp, /var/tmp, $TMPDIR and inside-root (:859-871). LOW-1: --receipt has no such guard (operator-supplied
  path, :747-756). LOW-2: counter's own fixture git calls (:338-370) still read the host's real global/system config
  (no NOSYSTEM/excludes pin, hooks could run on fixture commits) — read-only w.r.t. the host, robustness only.
- c2-mutate.py writes only --out (mkstemp in --out's dir + os.replace, refuses existing out, compile() in memory so no
  pycache, never executes the writer, no /tmp). CONFIRMED.

## Part B — candidate (sha256 a8c47d362a901c222f9582b8b96609fba39cb5e0e662d4057e724db96c1097fc, matches marker; poll 0)
1478 lines vs base-r65 1374 (6be46a05...); diff 173 lines. Verdict: NO HIGH, NO MEDIUM; all six checks conform.
- (a) PASS — no env VALUE echoed anywhere; gate prints names only (:288-306); r65 F4 redacted, GIT_INDEX_FILE message
  now "(value not shown)" (:305-306); selftest cases 31/32 assert planted values stay off stderr.
- (b) PASS — every refusal fires before the receipt temp exists (:507); the one in-window refusal (os.link EEXIST :519)
  is cleaned by the finally (:525-532); SIGTERM/SIGINT handlers unlink too (:257-265, :1472-1473).
- (c) PASS — non-selftest subprocess sites are git() (:98-99) and the wrapped-command Popen (:434) only; all plumbing
  via git(); new selftest cases reuse existing helpers.
- (d) PASS — git() overwrites GIT_CONFIG_GLOBAL=os.devnull (:95) on every child with NOSYSTEM=1, NO_REPLACE_OBJECTS=1,
  excludesFile=/dev/null pins (:96-99); no config-writing command exists in the main flow → real global config is
  neither read nor written; caller value overwritten before first spawn.
- (e) PASS per frozen surface — refuses COUNT, PARAMETERS, KEY_*, VALUE_* (prefix tuple), and the three redirects,
  presence-inclusive; GIT_CONFIG_GLOBAL intentionally repointed not refused (frozen E3 expects "lane worktree is dirty").
  LOW-3: names outside the frozen six (GIT_COMMON_DIR, GIT_NAMESPACE, GIT_CEILING_DIRECTORIES, GIT_CONFIG_SYSTEM — the
  last dead under NOSYSTEM=1) are neither refused nor pinned; out of round-66 scope, record for a future round.
- (f) PASS — `& 0o7777` (:176) records exactly permission bits + setuid/setgid/sticky; type bits and all else masked;
  symlink branch unchanged (M5), no widening possible.

## Numbers
- Matrix rows: 28; base-forgery rows: 8 (E1-E6, MOD2, MOD3); base-honest rows: 5 (A, B, T4, V2, SY1); matrix classes
  cross-checked against CASE_SPECS/CASE_ORDER and the prereg target line.
- Marker wait: 0 of 45 iterations consumed.
- Findings: 0 HIGH, 0 MEDIUM, 4 LOW (LOW-1 receipt guard, LOW-2 counter host-config reads, LOW-3 env names beyond the
  frozen six, LOW-4 r60-frozen stale-temp glob).
- Tooling installed: none.
