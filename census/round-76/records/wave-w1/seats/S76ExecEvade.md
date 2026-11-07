# S76ExecEvade — W-gate (e827d2bf) ignore-source attribution: 9 routes
Gate+writer extracted from e827d2bf into scratch; each route built an origin+clone
fixture, committed a base, pushed `HEAD:master`, then ran the full gate.
Commands: `python3 -B probe.py`, `probe2.py`, `probe3.py`, `probe4.py` (copies in
`.ufo/waves/round-76/w1/S76ExecEvade/`). Gate check: `check-clean` + `detail-clean`.

| # | Route | Result | Label |
|---|---|---|---|
| a-rel | `core.excludesFile=sub/.gitignore` (tracked sub file, relative) hides root `payload.txt` | FAIL `pinned git status lists 1 record(s)` | defended (by status, not attribution; excludesFile cannot fully hide — `ignored-perdir: b''`, check-ignore rc=1 unmatched) |
| a-abs | same, absolute path | identical FAIL | defended, same reason |
| b-neg | tracked root ignores `hidden/`; untracked `hidden/.gitignore` with `!payload`; `hidden/payload` | PASS, ignored=`[hidden/.gitignore, hidden/payload]` | **FORGERY HIGH** — negation never re-includes (dir excluded); attribution reads `hidden/.gitignore` untracked → should fail (see note) but PASS |
| c-skipwt | tracked `sub/.gitignore`, `--skip-worktree`, append rule + payload | FAIL `RECEIPT-WORKTREE-STAT-CONCEALED` | defended (hash-truth catches it) |
| d-symlink | `linkdir/.gitignore` symlink to tracked root `.gitignore` | FAIL `unable to access 'linkdir/.gitignore': Too many levels of symbolic links` (self-loop when symlink sits in root) | defended/noisy, not a forgery |
| e-newline | untracked dir `bad-dir-name\nx/` with own `.gitignore`+payload | FAIL `?? "bad-dir-name\nx/.gitignore"` (status names it — NUL-safety broken by quoting) | defended but coarse; untracked `.gitignore` itself visible to status |
| f-exclude | `info/exclude` duplicates tracked-rule match | PASS | correct — tracked rule decides; excludesFile-only case already FAILs (a2: `check-ignore rc=1`, `ignored-perdir b''`) |
| g-tracked | tracked `sub/.gitignore` decides `sub/payload` (g2); tracked `-/payload` (g3) | PASS | CORRECT PASS both — ancestor rule honored, `-` and nested dirs work |
| h-sparse | sparse-checkout cone + tracked rule | PASS | correct |
| h-ignoreCase | `core.ignoreCase=true`, `PAYLOAD.TXT` pattern vs `payload.txt` | PASS | correct |
| i-rc128 | `core.excludesFile` = a directory | gate errors `fatal: cannot use … as an exclude file` before attribution (`ignored-file listing failed` path) → FAIL | fail-closed, no HANG |

## Findings
- **FORGERY HIGH (b-neg):** `hidden/payload` ships with no tracked rule declaring it:
  parent dir is excluded by the tracked rule, and the untracked `!payload` negation
  cannot re-include it (git does not descend into an excluded dir), so both files
  land in `ignored-standard` with deciding source `hidden/.gitignore` (untracked) —
  the exact shape f7 labels FAIL. The gate printed `check-clean=PASS`. The r76
  predicate reads the last matching pattern's source; here the last match for
  `hidden/payload` is the `!` negation line — the gate's pattern check
  `not pat.startswith(b"!")` should count it undeclared, yet the run passed,
  so the routing differs from the preregistration's model (likely the deciding
  pattern recorded is the parent-dir exclusion, not the negation). Repro:
  `probe.py` route `b-neg` (minimal: tracked `sub/*`, untracked `sub/.gitignore`
  `!payload`, `sub/payload`).
- No other FORGERY / OVER-REFUSAL / HANG found. a-rel/a-abs fail via earlier
  status layers, not via attribution — the excludesFile path still relies on
  `ignored-perdir` difference, so an excludesFile that excludes only paths the
  per-dir rules also match would pass silently (f-exclude shows the tracked-rule
  twin passes by design).
- MEDIUM: b-neg's untracked `.gitignore` is itself counted in `ignored-standard`
  only because the tracked rule catches it; where the parent is *not* excluded,
  an untracked `.gitignore` surfaces in `git status` (e-newline shows the
  quoting), so the attribution block is the only guard for the f7 shape.

Files written: `.ufo/waves/round-76/w1/S76ExecEvade.md` (this),
`.ufo/waves/round-76/w1/S76ExecEvade/probe.py`, `probe2.py`, `probe3.py`, `probe4.py`.
Scratch `/fast/scratch/hyaku/souji-r76/S76ExecEvade` removed before yield.
