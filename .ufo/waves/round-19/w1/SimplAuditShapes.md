STATUS: DONE — the integrated r19 auditor delta is already the minimal C1 shape: extend the existing `allowed` exact-match set for sibling delivery, add one bash-side signal check reusing `_unquoted`, pin `V-SIGNAL`; no spec subsystem or directory prefix whitelist.

# Findings

## Minimal change (one predicate + one token set, no new subsystem)

### Authorized delivery shapes

**Predicate (single, exact):** after `report = f"{lane}/{reportDir}/{name}.md"` is fixed in `run()`, each write/edit call builds

```text
allowed = [report, *owned] + [stem(s) + suffix for suffix in DELIVERY_SUFFIXES]
```

where `stem(s)` is `report` with a trailing `.md` removed (else the full `report` string), and `DELIVERY_SUFFIXES` is the fixed tuple `(".patch", ".py", ".json", ".tsv", ".txt")`. A target is authorized iff `target_verdict` normalizes it and finds **exact equality** against some entry in `allowed`, or it already falls under the existing scratch rule `_under(n, scratch)`.

That is one predicate: **membership in a per-seat closed set of absolute path strings** derived only from `reportDir`, seat `name`, and `owned_paths(prompt)`. It is not a prefix on `.ufo/waves/round-N/wK/`, not a new spec field (`writeAllow`, `scratchDir`), and not prompt surgery moving patch paths into `OWN ONLY` (which would duplicate the report path and still miss `{py,json,tsv,txt}` siblings).

**Reuse (no new write subsystem):**

| Piece | Reuse |
| --- | --- |
| Allow/deny for writes | Existing `target_verdict()` and `any(n == _norm(p) for p in allowed)` at absolute branch |
| Report path | Existing `run()` → `audit_seat(..., report, ...)` |
| Scratch workdir | Existing `_under(n, _norm(scratch))` with `scratch_base + name + "/"` from spec context |
| OWNED lane files | Existing `owned_paths()` / `OWN_RE` + `ABS_RE` |
| Violation when not allowed | Existing **`V-WRITE-SCOPE`** (major) — no new write class |

**Do not adopt (heavier / weakens calibration):**

- Directory or stem-prefix allow under `.ufo/waves/` (would admit neighbour stems and arbitrary files in the wave dir).
- Per-item `writeAllow` / declared scratch in spec schema (new subsystem; ScoutSeatAuditR18 §5).
- Relying only on absolute paths in `OWN ONLY` for patch delivery (13 r18 executors had lane-relative `OWN ONLY`; `owned=[]` caused FM-1).

Private `/var/tmp/souji-r<N>-<Seat>/` writes need **no r19 delivery change**; they already pass via scratch. FM-3 (roster slot suffix vs item name in scratch path) is a separate scratch-declaration problem and must not be “fixed” by widening delivery allow.

### V-SIGNAL

**Token set (one closed vocabulary, two surfaces):**

- Shell command position (after `_unquoted`): `kill`, `pkill`, `killall` followed by an option/operand (`SIGNAL_SHELL_RE`).
- Python invocation only: `os.kill`, `proc.kill`, `.send_signal`, `send_signal` before `(` (`SIGNAL_LIB_RE` gated by `PYTHON_TOKEN_RE` on the same bash line).

**Reuse:**

| Piece | Reuse |
| --- | --- |
| Quote-aware command position | Existing `_unquoted()` (same as `EXEC_RE`, `PROBE_BASH_RE`) |
| Bash-only instrumentation | Same `tool == "bash"` pattern as `LIVE_CENSUS_RE` / `V-EXEC` |
| Severity | New pinned major class **`V-SIGNAL`** in docstring + `flag()` |

**Why not reuse an existing class:**

- **`V-EXEC`**: non-exec roles are already blocked from lane tools; MatrixR18 and fixture owners still emit signal-shaped bash that must stay major (R18-M6). Exec exemption would launder kills.
- **`V-SURFACE`**: signals are not forbidden-path reads/writes; conflating would blur disclosure.
- **`V-PROBE`**: readlink/strace semantics unrelated.

Integrated code matches this minimal design (~45 lines of logic + selftest cases vs base `3ab2c81`).

## What the change must not weaken

1. **`tools/` (and tests/census/corpus) writes** — any normalized absolute target not in `allowed` and not under seat scratch stays **`V-WRITE-SCOPE` major** (selftest `delivery-tools-still-major`; fixture `tools-write`).
2. **Neighbour delivery** — `Other.patch` beside the seat report stays major (exact stem match only).
3. **Bare relative lane writes** — unchanged **`V-WRITE-RELATIVE`** (fixture `relative-target`; CX1).
4. **Nine confirmed driver-state baseline reads** — RevMisrootRisk reads of `.ufo/state/*.report-baseline` must remain **`V-SURFACE` majors** on the read tool; delivery/V-SIGNAL do not touch `SURFACE_RE`. Re-audit w2 still lists nine such rows for that seat (`census/round-19/seat-audit-r18-recheck-w2.json`).
5. **Signal false positives** — quoted `kill` in grep patterns must stay clean (`signal-prose-not-flag` selftest).

Widening delivery to prefix allow or shrinking suffix set without Q38 alignment would weaken (1) or (2). Disabling python-gating for lib tokens would weaken (5) for `-c` strings that mention `os.kill` in prose.

## Calibration verdict on integrated bytes

The worktree auditor implements the minimal proposal; no second convention was found that could be deleted without losing C1 discrimination. Optional trim only if L1 narrows Q38 suffix list: `DELIVERY_SUFFIXES` could shrink to `(".patch", ".py")` **only** if the quality pin is narrowed accordingly; current five suffixes match `corpus/QUALITY.md` Q38.

# Evidence

- Integrated delivery + signal wiring: `tools/souji-seat-audit.py` lines 95–107 (`DELIVERY_SUFFIXES`, signal regexes), 267–271 (`V-SIGNAL`), 272–275 (`allowed` extension).
- Base omission (no delivery siblings, no signal): `git show 3ab2c81:tools/souji-seat-audit.py` — `allowed = [report, *owned]` only; no `SIGNAL_*`.
- FM-1 / rejected alternatives: `.ufo/waves/round-18/w1/ScoutSeatAuditR18.md` §3 FM-1, §5 (spec fields).
- Q38 exact-predicate pin: `corpus/QUALITY.md` Q38 row.
- Fixture discriminates base on ≥2 cases: delivery-patch → base `V-WRITE-SCOPE`; signal-kill → base clean; changed arm passes all five.
- r18 w1 re-audit summary after integrated auditor: `major=134` in `census/round-19/seat-audit-r18-recheck-w1.json` (down from raw 139 false-heavy majors per prereg); new `V-SIGNAL` rows present (e.g. BaseArmLeaks line 86).

# Commands run

```bash
python3 tests/fixtures/r19-seat-audit-shapes.py --tool tools/souji-seat-audit.py
# SUMMARY total=5 failed=0 base_discriminating=2

python3 tools/souji-seat-audit.py --selftest
# SELFTEST pass=73 fail=0

git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff 3ab2c81 -- tools/souji-seat-audit.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 3ab2c81:tools/souji-seat-audit.py | head -320
```

Read-only: `census/round-18/seat-audit-adjudication.json` (RevMisrootRisk confirmed-read-violation), `census/round-19/seat-audit-r18-recheck-w{1,2}.json`, `.ufo/waves/round-19/preregistration.txt`, `tests/fixtures/r19-seat-audit-shapes.py`.

No tool installs.

# Contract compliance

- Leaf seat: no subagents, no lane edits outside report path, no git/jj mutations, no census/live lane tool execution, no signals, scratch under `/var/tmp/souji-r19-SimplAuditShapes/` (removed after run).
- Report only: `.ufo/waves/round-19/w1/SimplAuditShapes.md`.
- Evidence from worktree bytes verified via commands above; integrated state not accepted without fixture/selftest exercise.
