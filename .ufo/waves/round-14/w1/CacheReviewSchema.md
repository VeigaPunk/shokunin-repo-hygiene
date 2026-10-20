# CacheReviewSchema — round 14, wave w1 (re-review #2 after F5/F6)

Seat: `SoujiR14.CacheReviewSchema` (reviewer, leaf, read-only). Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Axes: calibration, operability.
Scope: C1 schema/type checks, stable exits, measured-revision preservation; prior findings F1–F8.
Files reviewed as source: `tools/souji-evidence-cache.py` (1859 lines), `tests/fixtures/r14-evidence-cache.py` (361 lines, unchanged this round), `tests/fixtures/r14-cache-frozen/{dependency.txt,record.json,expected.json}`.

## Evidence separation

- **Code inspection (static, this seat):** all findings come from reading source and tracing each selftest setup to its branch. No selftest, fixture, CLI, or `py_compile` was run by this seat, now or previously.
- **Exercised (this seat), earlier round only:** read-only `sha256sum` of the frozen pins; both match `expected.json`.
- **Not exercised:** whether `--selftest` (48 cases) or the fixture passes. Trace predicts pass; L1 must confirm.

Tooling: none installed or upgraded by this seat.

## Status of prior findings

| ID | Status | Static evidence |
|---|---|---|
| F1 blocker (`_read_path_text` 2-tuple) | RESOLVED | success returns 3-tuple; `_record_payload` unpack matches. |
| F2 (`frozen-incomplete` per-dep emission) | RESOLVED | aggregated into one finding (~1166–1170); selftest expects one id. |
| F3 (lstat before boundary) | RESOLVED | `_resolve_root` order: lexical → `_resolve_boundary` → `lstat` → no-follow open. |
| F4 (walk errors reported as protection ids) | RESOLVED | walk kinds map to `root-not-directory` / `record-unreadable`; only `protected` maps to `*-protected`. |
| F5 (name whitespace undocumented) | RESOLVED | docstring (~66–67) now states "no surrounding whitespace and no non-printable characters". Code is `name == name.strip() and name.isprintable()` (~861). Consistent. Minor nit: the error text at ~864 still says "control-free string", which is less precise than the rule. Operability only, non-blocking. |
| F6 (uncovered stable ids) | LARGELY RESOLVED | Selftest now has 48 `cases.append` sites. New cases verified on trace: `dependencies-invalid` (`dependencies=[]`), `require-invalid` (`--require ../escape.txt`), `root-not-directory` (plain file as `--root`), `record-unreadable` (absent record path), `path-invalid` (control char in key → generic `path-invalid` branch), `path-not-directory` (`src/a.txt/child` → `ENOTDIR` on a regular file, not a symlink → `not-directory`), `frozen-unreadable` (no `expected.json` → `missing`), `frozen-malformed` (`{bad`), `frozen-schema` (`{}` → `record path is invalid`). All reach the intended branch. |
| F7 (leaf open before type check) | MITIGATED | `_open_leaf_checked` stats with `follow_symlinks=False` and rejects non-regular before `os.open`. |
| F8 (`NaN` tolerance) | unchanged, harmless. |

## Uncovered ids after F6 (accepted by CacheGate; reviewer assessment)

- `dependency-device-escape`: needs a second mount. Accepting the gap is reasonable, but the branch is unexercised, so a regression there is silent. Residual risk, not a blocker.
- `internal-error`: needs an injected fault. Its path is `__main__`'s `except Exception`, which is small and readable. Residual risk, not a blocker.
- `key-alias`: documented in the module docstring as unreachable once non-canonical keys are rejected. On trace, `_classify_rel` is identity on accepted keys, so two distinct accepted keys cannot compare equal. Agreed as a defensive branch.

## Other notes (non-blocking)

- Selftest `frozen-unreadable` writes only `record.json`, so the gate's first failure is the `expected.json` open. Correct, but it tests the missing-file path only, not an unreadable (EACCES) one. Acceptable.
- `_emit` prints a `scope:` line before `finding` lines. The selftest `_ids` regex is anchored on `^finding `, so this does not affect id parsing.

## Verdict

**Admissible pending the exercised L1 run.** No blocking defect in the static review. Residual non-blocking items: F5 message wording, three ids without exercised coverage (device-escape, internal-error, key-alias by design).

## Final L1 commands (not run by this seat; main agent runs once after all C1/C2 executors land)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
python3 -m py_compile tools/souji-evidence-cache.py tests/fixtures/r14-evidence-cache.py
python3 tools/souji-evidence-cache.py --selftest; echo "selftest_exit=$?"
python3 tests/fixtures/r14-evidence-cache.py; echo "fixture_exit=$?"
sha256sum tests/fixtures/r14-cache-frozen/dependency.txt tests/fixtures/r14-cache-frozen/record.json
```

Expected: selftest `48/48 passed`; fixture all ok. Static greps (read-only): `grep -n 'object_pairs_hook' tools/souji-evidence-cache.py` (present); `grep -nE 'os\.system|eval\(|exec\(|shell=True' tools/souji-evidence-cache.py` (none); `grep -n 'subprocess' tools/souji-evidence-cache.py` (only in `_run_tool`).

## Residual risk and verification gaps

- No exercised confirmation of selftest or fixture on the current source.
- Three ids (`dependency-device-escape`, `internal-error`, `key-alias`) have no exercised coverage; a regression there passes silently.
- The docstring's caller precondition (digests captured at measurement time) is a design constraint the gate cannot verify.

## Peer communication

- `SoujiR14.CacheGate`: F5/F6 status and residuals sent in a separate message this turn.
