# SwarmReviewer11 — C2 patch review: souji-cert-evidence.py, souji-evidence-cache.py, souji-preservation-evidence.py, souji-seat-audit.py

Scope: the C2 diff `git diff 85b61a151923986e7e6b48f7084b9122561b5f3d 98e5203d45b4e419a9e72801733d93303acc7ebd -- <the 4 tools>` plus behaviour runs of their c2-items.tsv commands (T07-T10) in scratch clones. Preregistration read first. No tool installs or upgrades were performed (none needed).

## Status

STATUS: PASS — the patch changes only scratch-root selection (parent fixture tree + child TMPDIR); every other observable behaviour is identical base↔rev in both TMPDIR modes (byte-identical stdout and rc); no refusal, guard or write-scope code is touched; cleanup verified empirically (zero leftovers).

## Evidence

Revisions: base 85b61a151923986e7e6b48f7084b9122561b5f3d, rev 98e5203d45b4e419a9e72801733d93303acc7ebd (the C2 landing). Clones `/fast/scratch/hyaku/souji-r32/ReviewC2Cert/{base,rev}`, `--no-local`, origin removed immediately; `git rev-parse --show-toplevel` printed each clone path before first use; scratch removed after the review.

Diff census (raw diff read in full — 11 hunks, 4 files, no mode changes):
- `tools/souji-cert-evidence.py` — docstring 129-141; `_selftest_env()` 990-997: hard-coded child `"TMPDIR": "/var/tmp"` removed, replaced by `if os.environ.get("TMPDIR"): env["TMPDIR"] = os.environ["TMPDIR"]`, wired to every case via `env=_selftest_env()` at :1013; `mkdtemp(dir="/var/tmp")` → `mkdtemp()` at :1158; `--selftest` help text :1494.
- `tools/souji-evidence-cache.py` — docstring 30-36; `mkdtemp(dir="/var/tmp")` → `mkdtemp()` at :1295; child env :1308-1315 same caller-TMPDIR pattern, passed via `_run_tool(..., env=env)` → `subprocess.run(env=env)` at :1270.
- `tools/souji-preservation-evidence.py` — docstring 29-35; `mkdtemp()` at :1956; child env :1970-1979 `"TMPDIR": os.environ.get("TMPDIR") or str(base)`, `subprocess.run(env=env)` at :1929.
- `tools/souji-seat-audit.py` — three `TemporaryDirectory(dir="/var/tmp")` → `TemporaryDirectory()` at :667, :680, :702.

Run matrix (T07-T10, `python3 -B <tool> --selftest`, cwd = clone; "set" = TMPDIR at a fresh scratch dir, "unset" = `env -u TMPDIR`):

| item | tool | base rc, last line | rev rc, last line |
|---|---|---|---|
| T07 | souji-cert-evidence | 0, `selftest: 36/36 passed` (set and unset) | 0, `selftest: 36/36 passed` (set and unset) |
| T08 | souji-evidence-cache | 0, `selftest: 48/48 passed` (set and unset) | 0, `selftest: 48/48 passed` (set and unset) |
| T09 | souji-preservation-evidence | 0, `selftest: 47/47 passed` (set and unset) | 0, `selftest: 47/47 passed` (set and unset) |
| T10 | souji-seat-audit | 0, `SELFTEST pass=118 fail=0` (set and unset) | 0, `SELFTEST pass=118 fail=0` (set and unset) |

Byte-compare of captured stdout (diff of base-run vs rev-run output, 2>&1, per mode): all four tools IDENTICAL with equal rc, in TMPDIR-set and TMPDIR-unset modes (8/8 comparisons).

TMPDIR honoured (watcher differential: 50 ms poll of the caller TMPDIR during the run for the tool's scratch tree):
- rev: cert SEEN, cache SEEN, preservation SEEN, seat-audit SEEN (each rc=0 with the selftest lines above).
- base: cert NEVER, seat-audit NEVER (each rc=0) — base pins `/var/tmp` by construction (`dir="/var/tmp"`, child `TMPDIR: /var/tmp`). The two base controls cover both code patterns (explicit mkdtemp dir; TemporaryDirectory + child env).

(2) No guard widened: the diff contains no hunk in any check/refusal/write-scope path. seat-audit's audit grammar is byte-identical base↔rev per `git grep` at both revs (`LIVE_CENSUS_RE` :90, `ABS_RE` :128, scratch-grant patterns :204/:208/:217) — the only /var/tmp strings left there are audit fixtures and grammar, unchanged. cert's refusal battery printed identical case lines at base and rev, including `path-escape`, `path-absolute`, `path-symlink`, `protected-path`, `protected-env-local`, `snapshot_tampered`, `frozen-verdict-mismatch`; seat-audit's 118 cases (write-scope, slot, grant, V-LIVE-CENSUS) all PASS identically. evidence-cache's documented refusal (doc :144) is untouched.

(3) TMPDIR unset: all four pass at rev (matrix above); cert/cache children then receive no TMPDIR key at all (→ tempfile default `/tmp`); preservation pins the child to the selftest's own tree (`os.environ.get("TMPDIR") or str(base)`, :1976-1978, comment :1975). Post-run `/tmp` prefix count after the rev unset runs: 0.

(4) Cleanup: after every set-mode run, `find <run TMPDIR> -mindepth 1 | wc -l` = 0 (8/8 runs) — nothing the selftests create survives. Code agreement: `shutil.rmtree(base, ignore_errors=True)` in finally at cert :1469-1470, cache :1786-1787, preservation :2577-2578; seat-audit uses context-manager `TemporaryDirectory`. Preservation's unset-mode child scratch lives inside the rmtree'd `base` tree, so it is removed with it.

## Findings

1. info — `tools/souji-preservation-evidence.py:1976-1978`: in the unset case the child TMPDIR policy intentionally differs from cert/cache (pinned to the selftest tree instead of unset). Quote from :1975: `The child gets the caller's scratch root`. Stricter than required, disclosed in-code; observed behaviour identical (47/47 in both modes). No action.
2. info — TMPDIR honouring is best-effort, not guaranteed: with `TMPDIR` pointing at a regular file, all four rev selftests still pass rc=0 because Python's `tempfile` silently falls back to `/tmp` when a candidate fails its probe (probe run, rev, all four tools, rc=0). Under the operator's scratch discipline TMPDIR is always a valid writable dir, so C2's intent holds; recorded so nobody claims a hard-fail property the stdlib does not provide.
3. info — empty-string `TMPDIR` is treated as unset by `os.environ.get("TMPDIR")` (cert :995, cache :1314) — consistent with `tempfile`'s own candidate semantics (empty candidates are skipped), so parent and child never disagree. Edge run: rev cert with `TMPDIR=` passed `selftest: 36/36 passed`.
4. info — remaining `/var/tmp` literals in the four files at rev are all outside the diff and byte-identical to base: preservation `_arm(tool_path="/var/tmp/tool.sh")` default :1840 (parameter, not exercised as a scratch write in T09's passing run), evidence-cache doc :144, seat-audit grammar/fixture strings (:14, :19, :45, :57, :90, :128, :204, :208, :217, :537-743). None was loosened or widened.
5. observation — during base-side calls, single `souji-r13-cert-selftest.*` / `souji-r14-cache-selftest.*` entries were seen in `/tmp`; base writes `/var/tmp` by construction, so these are from concurrent seats' rev-mode runs, not from my runs (my rev unset runs left `/tmp` litter=0). Left untouched (not mine to remove).

Residual risk / gaps: I exercised the frozen T07-T10 entry points (`--selftest`) only; the tools' non-selftest CLI paths (`--root/--frozen/--manifest`) are outside those commands and untouched by the diff except the shared cert env helper, whose only use is inside the selftest battery (def :990, use :1013). Watcher poll at 50 ms could in principle miss a <50 ms tree lifetime; the trees live seconds (subprocess per case) and post-run leftovers=0 confirms create+remove, so the 6/6 SEEN/NEVER asymmetry is sound. I did not run the full c2-counter — counter re-derivation belongs to other seats.

## Attack log

Not an attack item; falsification attempts on the landed patch:
- Guard-widening hunt: no hunk touches any check; byte-identical stdout+rc across 8 base↔rev comparisons makes behavioural widening undetectable by run and absent by diff. Nothing to report.
- Broken-TMPDIR probe (file as TMPDIR) was discarded as non-discriminating (tempfile falls back silently, all runs rc=0) and replaced with the watcher differential, which discriminated 6/6 (rev SEEN ×4, base NEVER ×2).

## Deliveries

- `.ufo/waves/round-32/a2w1/SwarmReviewer11.md` — this report (only file written in the lane).
