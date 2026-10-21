STATUS: DONE — integrated helper is already one function + one CLI; five fixture-wired consumers split into two invocation shapes (runner vs counter); three runner-owned measured-path lists must stay local.

# Findings

## Axes (operability)

1. **Refusal before record** — a bad revision or dirty measured tree must exit 2 with typed text and write no JSON (`tools/souji-rev-pin.py:10–12`; runners print a caller prefix then `SystemExit(2)`).
2. **Historical replay** — an explicit 40-hex revision reachable from durable refs must still run when the working tree has moved (`resolve_durable(..., tree_check=False)`; CLI `--no-tree-check`).
3. **No second policy layer** — durable roots are fixed (`refs/heads|refs/tags|refs/remotes`, never `refs/jj`); callers supply only *which tracked paths* their record claims to have measured.

## Exact minimal API (keep as-is)

**One function** (`tools/souji-rev-pin.py:86–147`):

```python
def resolve_durable(root, rev, measured_paths=None, tree_check=True) -> str:
    """Return verified 40-hex commit or raise Refusal."""
```

**One CLI** (`:296–320`):

```text
python3 tools/souji-rev-pin.py --root DIR --rev REV [--path PATH]... [--no-tree-check]
python3 tools/souji-rev-pin.py --selftest
```

| Exit | Meaning |
|------|---------|
| 0 | stdout: single 40-hex line |
| 2 | stderr: `souji-rev-pin: refused: …` (or missing `--rev`) |
| 1 | `--selftest` failure |

**Exception type:** `Refusal` — callers catch it; do not replace with errno tuples or a result enum (that would be a policy engine).

**Public surface to shrink (optional, non-semantics):** `durable_tips()` (`:69–83`) is implementation-only; rename to `_durable_tips` or document as private. No second exported resolver.

## Five call sites (fixture wiring)

`tests/fixtures/r19-rev-pin.py` `WIRING` (`:47–68`) names exactly five lane consumers. A sixth runner-style caller, `census/round-14/cache-demonstration.py` (`git_head` → `resolve_durable`, `:189–197`), is part of C2 preregistration but is not in that wiring dict.

### Invocation shape A — runner (default `tree_check=True`)

Call pattern after local `git rev-parse HEAD` (40-hex **value**, not the symref string `HEAD`):

```python
resolve_durable(str(ROOT), head, MEASURED_PATHS)  # tree_check defaults True
```

| Call site | Share helper unchanged? | Measured-path list |
|-----------|-------------------------|-------------------|
| `census/round-13/run-verification.py` | Yes — same function/CLI contract | **Own** `MEASURED_PATHS` (`:92–105`, 12 paths: r13 tools, fixtures, runner) |
| `census/round-14/run-verification.py` | Yes | **Own** `MEASURED_PATHS` (`:30–39`, 8 paths: r14 tools, fixtures, runners) |
| `census/round-14/run-targeted.py` | Yes — **no direct helper import**; calls `module.resolve_revision()` from r14 run-verification (`:23`) | Inherits r14 list via delegated `resolve_revision()` |
| `census/round-14/cache-demonstration.py` | Yes — same `resolve_durable` | **Own** `DEMO_MEASURED_PATHS` (`:80–87`, 6 paths): proper subset of r14’s list (drops `check-timeout-anchor.py` and `run-verification.py` because the demo does not execute those as measured subjects) |

None of the three distinct path lists can be centralized in the helper without lying about what a record measured.

### Invocation shape B — counter (`tree_check=False`)

```python
resolve_durable(str(root), value, [], tree_check=False)
```

| Call site | Share helper unchanged? | Measured-path list |
|-----------|-------------------------|-------------------|
| `census/round-13/count-claims.py` | Yes — identical helper args | **None** (empty paths; all bytes read via `git show` / `ls-tree` at `rev`) |
| `census/round-14/count-claims.py` | Yes — same one-liner as r13 | **None** |

The two `resolve_claims_revision()` wrappers (`:15–29` in each file) are thin stderr-prefix glue, not a second policy engine. They may be inlined to a direct `resolve_durable` call without changing semantics; keeping the named function aids the fixture wiring marker.

## Arguments that could be dropped

| Argument / surface | Drop? | Reason |
|--------------------|-------|--------|
| `tree_check` | **No** | Only switch between runner binding and counter replay; inferring from `measured_paths` would break the default (empty paths + `tree_check=True` must refuse runners with “no measured paths”) |
| `measured_paths` when `tree_check=False` | Already optional (`[]`) | — |
| CLI `--root` default `.` | Optional | Harmless; ad-hoc smoke uses lane cwd |
| CLI `--path` when `--no-tree-check` | Optional | Counter-style CLI checks need no paths; omitting `--path` is valid with `--no-tree-check` |
| Per-caller `importlib.util` loader block | **Do not centralize** | `tools/` is not a package; a shared importer would be a second convention |
| Caller `git rev-parse HEAD` before helper | **Do not move into helper** | Helper must refuse symref *names* (`HEAD`, branch names); callers need the resolved 40-hex for the current tip while still enforcing durable reachability + tree equality |

## What must NOT be abstracted

1. **Per-record measured-path sets** — each runner names the tracked paths it executes or reads; the helper only diffs those paths, never discovers them.
2. **Record write timing and paths** — JSON emission, `--output` guards, artifact unchanged checks stay in census scripts.
3. **Configurable durable-ref policy** — namespaces are hard-coded (`DURABLE_NAMESPACES`, `:33–34`); no flags for “also allow refs/jj” or stash/original toggles.
4. **Automatic HEAD / branch acceptance** — would recreate the pre-r19 false stamps preregistration lists (`census/round-13/run-verification.py:384`, etc. at base `3ab2c81`).
5. **Dependency maps, reuse, cache gate logic** — r13 runner-only; unrelated to revision durability.
6. **Verdict / “sufficient measurement”** — module docstring (`:11–12`) states the helper is resolution only.
7. **Git hardening inside the helper** — `GIT_CONFIG`, `LC_ALL=C`, hooks disabled (`:34–38`, `:45–53`); callers keep their own execution `ENV`.

## Deletion / simplification candidates (no lane edits)

| Candidate | Action | Tradeoff |
|-----------|--------|----------|
| Public `durable_tips` | Make private | Zero behavioral change; narrows import surface |
| Duplicate `resolve_claims_revision` in two count-claims files | Inline one-liner at two call sites | −~10 lines each; wiring marker string must stay in file |
| Duplicate `resolve_revision` in r13 vs r14 | **Keep separate** | Lists differ; shared wrapper would take `MEASURED_PATHS` parameter → second API |
| Add `resolve_consumer()` wrapper | **Reject** | Violates “one function”; use `tree_check=False` at call site |

Integrated bytes reviewed: worktree `tools/souji-rev-pin.py`, five wired consumers above, `census/round-14/cache-demonstration.py`, `tests/fixtures/r19-rev-pin.py`.

# Evidence

- Helper contract and refusal ordering: `tools/souji-rev-pin.py:86–147`, `:296–320`.
- r13 runner paths + `resolve_revision`: `census/round-13/run-verification.py:92–120`.
- r14 runner paths + `resolve_revision`: `census/round-14/run-verification.py:30–54`.
- Targeted delegation: `census/round-14/run-targeted.py:23`.
- Demo paths + `git_head`: `census/round-14/cache-demonstration.py:80–87`, `:189–197`.
- Counter shape: `census/round-13/count-claims.py:15–29`, `census/round-14/count-claims.py:16–30`.
- Five-site enumeration: `tests/fixtures/r19-rev-pin.py:47–68`.
- SKILL row matches CLI: `SKILL.md:203`.
- C2 before→after scope: `.ufo/waves/round-19/preregistration.txt:39–49`.

# Commands run

```text
read tools/souji-rev-pin.py, census/round-{13,14}/*.py (callers), tests/fixtures/r19-rev-pin.py, SKILL.md, preregistration.txt
grep souji-rev-pin / resolve_durable across lane
mkdir -p .ufo/waves/round-19/w1
```

No installs. No private /var/tmp execution (read-only simplifier seat).

# Contract compliance

- Report only at `.ufo/waves/round-19/w1/SimplRevPin.md`; no edits to `tools/`, `tests/`, `census/`, corpus, SCORECARD, LOG, SKILL, MANIFEST.
- No git/jj mutations; no subagents; no census executors; no network.
- Scratch: none created.
