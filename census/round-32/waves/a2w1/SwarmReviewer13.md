# SwarmReviewer13 — C2 receipt-run patch review (T16/T19/T24)

## Status

STATUS: PARTIAL — the patch is behaviour-preserving outside the scratch root (checks 1, 3, 4 pass on reproduced runs), but check 2 fails on two reproduced guard deltas: the out-guard now accepts any path under a caller-controlled TMPDIR (fleet-root paths that base refused), and it accepts the scratch root itself as a receipt path (end-to-end crash instead of a clean refusal).

Scope: `git diff 85b61a151923986e7e6b48f7084b9122561b5f3d 98e5203d45b4e419a9e72801733d93303acc7ebd -- tools/souji-receipt-run.py tests/fixtures/r23-receipt-run.py tests/fixtures/r24-receipt-verify.py tests/fixtures/r25-receipt-stderr.py` (4 files, +31/−14). All runs in scratch clones at both revs, origin removed. No tools installed this run (stock git/python3 only).

## Evidence

Item commands (census/round-32/c2-items.tsv): T16 `python3 -B tests/fixtures/r23-receipt-run.py`; T19 `python3 -B tests/fixtures/r24-receipt-verify.py --tool tools/souji-receipt-run.py --lane-root .`; T24 `python3 -B tests/fixtures/r25-receipt-stderr.py --rev 85b61a151923986e7e6b48f7084b9122561b5f3d`. "set" = `TMPDIR=/fast/scratch/hyaku/souji-r32/ReviewC2Receipt/tmp`; "unset" = `env -u TMPDIR`.

12 runs, (rc, last digit-bearing line):

| item | rev | TMPDIR | rc | last line |
|---|---|---|---|---|
| T16 | base | set | 0 | `selftest=8/8` |
| T16 | C2 | set | 0 | `selftest=8/8` |
| T16 | base | unset | 0 | `selftest=8/8` |
| T16 | C2 | unset | 0 | `selftest=8/8` |
| T19 | base | set | 0 | `cases=8 pass=8 refusals=2/2 regress=5/5` |
| T19 | C2 | set | 0 | `cases=8 pass=8 refusals=2/2 regress=5/5` |
| T19 | base | unset | 0 | `cases=8 pass=8 refusals=2/2 regress=5/5` |
| T19 | C2 | unset | 0 | `cases=8 pass=8 refusals=2/2 regress=5/5` |
| T24 | base | set | 0 | `cases=1 pass=1` |
| T24 | C2 | set | 0 | `cases=1 pass=1` |
| T24 | base | unset | 0 | `cases=1 pass=1` |
| T24 | C2 | unset | 0 | `cases=1 pass=1` |

Full-output A/B (T16, T19, TMPDIR set, base vs C2, normalized for mkdtemp suffixes/rev hashes/utc): every case line identical; the only diff is line 1's clone path (`runner=.../base/...` vs `.../rev/...`). Per-case behaviour, refusals and output are unchanged.

Diff audit (check 1): the only code changes are the three fixtures' scratch constants (`SCRATCH_PARENT`/`SCRATCH`, r23:50, r24:47, r25:20) and, in the tool, `scratch_root()` (:70-72), the out-guard (:192-195) and `mkdtemp(dir=scratch_root())` (:221), plus matching docstrings. No case, refusal code, guard or output string otherwise touched. No fixture pins the old refusal code: r23's `CODE` regex binds "an explicit refusal code" and only case 3 names a code literally (`RECEIPT-TOOL-DIGEST-MISMATCH`, a verify-side code, unchanged); r24's two refusal cases pin `RECEIPT-REV-NOT-DURABLE` and `RECEIPT-TOOL-NOT-IN-ARGV` (unchanged); r25 drives only the `verify` subcommand. Repo-wide grep at the C2 rev: no live reference to `OUT-OUTSIDE-VAR-TMP` outside history (corpus/lessons/round-24.md:333 and census/round-26 wave copies are historical records).

TMPDIR unset (check 3): `scratch_root()` returns `/var/tmp` whenever `os.environ.get("TMPDIR")` is falsy (also for an empty TMPDIR), so unset behaviour equals base except finding 2 below. All six TMPDIR-unset runs match base rc/last-line exactly.

Cleanup (check 4): tool `finally: shutil.rmtree(scratch, ignore_errors=True)` (tools/souji-receipt-run.py:269-270) unchanged; the receipt write happens after the finally, so even the finding-2 crash cleans the clone. r23 cleans `_SCRATCH`/`_STRAY` via atexit + SIGINT/SIGTERM/SIGHUP traps (r23:83-91, 518-520); r24 likewise (r24:72-74, 278-280); r25 `finally: shutil.rmtree(scratch)` (r25:87). Observed: after all runs my TMPDIR was empty, `/var/tmp` held no `souji-r23-*`/`souji-r24-*`/`souji-r25-*`/`souji-receipt-*` dirs, and both clones had empty `git status --porcelain`.

## Findings

1. MEDIUM — out-guard write scope now follows the caller-controlled TMPDIR. tools/souji-receipt-run.py:192-195 (C2) vs :184-187 (base). Base: `if not out.startswith("/var/tmp/"):` — a fixed root, immune to env. C2: `if not (out == base_scratch or out.startswith(base_scratch + os.sep)):` with `base_scratch = os.path.realpath(scratch_root())`, where scratch_root() is TMPDIR when set (:70-72, "The caller's scratch root: TMPDIR when set, else /var/tmp"). With a broad TMPDIR the guard accepts arbitrary paths modulo three residual checks: OUT-IN-REPO (:197-198), OUT-PROTECTED four substrings `/.ufo/state/`, `/.tower/`, `/.scratch/`, `/MANIFEST.json` (:216-218, unchanged from base :205-207), OUT-SIBLING-LANE regex (:219). Reachable with `TMPDIR=/home/vgpnk/Projects/shokunin`: `.ufo/watchdog.log`, `scripts/*`, `templates/*`, `.ufo/waves/*` — the very fleet-truncation class the refusal message cites ("r24 W2Scope: the old guard let a receipt truncate fleet files", :30). Caller-gated (the caller already owns TMPDIR), and under the operator discipline (`TMPDIR=/fast/scratch/hyaku/souji-r32/<seat>/tmp`) the scope is the seat's own scratch — the mandated C2 behaviour — but the guard no longer independently pins a safe root. For the L1: a stricter-only amendment could extend OUT-PROTECTED or require the resolved scratch root to sit under a scratch-discipline root; the frozen C2 counter and item set are not touched by this report.

2. LOW — the scratch root itself is now accepted as a receipt path. tools/souji-receipt-run.py:193 (`out == base_scratch` disjunct) vs base :184 (required a component under `/var/tmp/`). Reproduced end-to-end at the C2 rev, TMPDIR unset: `run --root . --rev 85b61a1… --tool tools/souji-receipt-run.py --out /var/tmp -- python3 -B tools/souji-receipt-run.py --help` → rc=1, unhandled `IsADirectoryError: [Errno 21] Is a directory: '/var/tmp'` — a traceback instead of a clean refusal code. No data written; the clone was removed by the finally.

3. LOW (observation) — TMPDIR set but nonexistent degrades to /tmp with a misleading message. tools/souji-receipt-run.py:70-72: `tempfile.gettempdir()` falls back to /tmp when TMPDIR is unwritable, so `scratch_root()` returns `/tmp`; every `--out` is then refused (fail-closed: under-/tmp outs hit OUT-UNDER-TMP :191 first, others fail the scratch check), but the refusal names the wrong root — reproduced: `TMPDIR=<nonexistent> --out /var/tmp/probe.receipt` → `OUT-OUTSIDE-SCRATCH receipts are written under the caller's scratch root (/tmp) …`. Had any out passed, `mkdtemp` (:221) would land under /tmp, contradicting the "never a bare /tmp" docstring; unreachable in practice because the out-guards refuse first.

## Attack log

All probes stop at a pre-clone refusal (guard order: rev checks → OUT-UNDER-TMP :191 → OUT-OUTSIDE-SCRATCH :192-195 → OUT-IN-REPO :197-198 → command checks → OUT-PROTECTED :216-218 → OUT-SIBLING-LANE :219 → mkdtemp :221), so nothing was written outside scratch; fleet root untouched (watchdog.log mtime is the orchestrator's own; probes A/E refused before any write).

- A (scope widening): rev clone, `TMPDIR=/home/vgpnk/Projects/shokunin`, `run --root . --rev 85b61a1… --tool tools/souji-receipt-run.py --out /home/vgpnk/Projects/shokunin/.ufo/watchdog.log -- echo hello` → rc=2 `TOOL-NOT-IN-ARGV` — the scratch guard PASSED for a fleet-root path. Base clone, same invocation → rc=2 `OUT-OUTSIDE-VAR-TMP`. Widening reproduced.
- B (root acceptance): rev clone, TMPDIR unset, `--out /var/tmp -- echo hello` → rc=2 `TOOL-NOT-IN-ARGV` (guard passed); base → rc=2 `OUT-OUTSIDE-VAR-TMP`. Widening reproduced.
- C (end-to-end degenerate): rev clone, TMPDIR unset, `--out /var/tmp` with a valid command → rc=1 `IsADirectoryError` traceback (finding 2).
- D (unwritable TMPDIR): rev clone, `TMPDIR=<nonexistent>`, `--out /var/tmp/probe.receipt` → rc=2 `OUT-OUTSIDE-SCRATCH … (/tmp)` (finding 3; fail-closed).
- E (protection intact): rev clone, `TMPDIR=/home/vgpnk/Projects/shokunin`, `--out /home/vgpnk/Projects/shokunin/MANIFEST.json` with the tool in argv → rc=2 `OUT-PROTECTED /MANIFEST.json is operator or orchestrator runtime`. MANIFEST.json, `.ufo/state/`, `.tower/`, `.scratch/`, sibling lanes and the measured repo remain refused.

## Deliveries

- .ufo/waves/round-32/a2w1/SwarmReviewer13.md (this report)
