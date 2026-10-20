STATUS: DONE — S1/S2/S3 substantially hold; two uncaught-crash holes break exit-2 totality (one NEW regression), and `checked_reg` folds the changed branch so that axis has no honest zero.

All line refs: `tools/souji-landing-gate.py` at ddb7347. Static review only (seat has no ALLOWED-EXEC); the selftest/gate was not executed and L1's run counts (28/28, gate-replays) were not re-measured.

## Findings

### F1 (MEDIUM — NEW regression, exit-2 totality): LG-PARSE-CHANGED branch can crash with a traceback and exit 1
- `:639` `for path in sorted(set(changed_out.split()))` — `git diff --name-only` output split on whitespace (pre-existing at 5fa6017:560). A path containing a space (`tools/my script.sh`) splits into fragments; a fragment ending `.sh`/`.py` passes `SCRIPT_EXT_RE` (`:640`) and reaches `parse_script` → `:278` `content = blob_by_oid(root, tree[path])` → **KeyError** if absent from the tree. The cited branch guards membership (`:622 if path not in tree`); the changed branch does not.
- Uncaught → CPython traceback, **exit 1** — the code that downstream parsers read as "findings", not the contract's exit 2 (`:31-33`).
- This is a regression vs 5fa6017: base `parse_script` (5fa6017:226-228) used `blob_at_path` and returned the `"blob unreadable"` finding on absent — total, if ugly. D6 switched to `tree[path]` without adding the changed-loop guard.
- Same loop, silent-skip hole (pre-existing): non-ASCII paths are C-quoted by `diff --name-only` (default `core.quotepath`), `"tools/caf\303\251.py"` fails the `$`-anchored `SCRIPT_EXT_RE` (`:640`) → the script is silently never checked, no counter moves. No crash, no finding, no zero — invisible.
- Smallest fix: switch to `["diff","--name-only","-z","--diff-filter=AM",base,resolved]` + NUL split (fixes spaces and quoting at once), and `if path not in tree: raise EvalError(...)` before `parse_script`. Belt-and-braces: wrap the `evaluate()` call in `main` (`:1235`) with `except Exception → exit 2` so no uncaught class can masquerade as exit 1.

### F2 (MEDIUM — pre-existing, in S2's claimed class): top-level non-object `expected.json` crashes instead of exit 2
- `:449-458`: `expected = json.loads(...)` (catches only `ValueError`/`UnicodeDecodeError`, `:453`) then `files = expected.get("files")`. Valid-JSON non-object — `[]`, `null`, `"x"`, `5` — → **AttributeError**, uncaught → traceback, exit 1.
- The landed S2 rationale (`:460-462` "a shape defect in the pin contract is could-not-evaluate, not a finding") is implemented for `files` only; the selftest falsy cases (`:1043-1054`) all mutate `files` inside a well-formed object. The top level of the same contract is unguarded (identical at 5fa6017:391).
- Fix: after `json.loads`, `if not isinstance(expected, dict): raise EvalError("%s: expected.json is not an object" % exp_path)`.

### F3 (MEDIUM-LOW — SUMMARY honesty): `checked_reg` folds two branches; LG-PARSE-CHANGED can never print an honest 0
- `:627` (cited) and `:642` (changed) both increment `checked_reg`. A no-`--base` run and a `--base` run are indistinguishable on this counter, and the docstring's own standard — `:44-46` "A zero on any of these means the axis was not exercised — never that it passed" — is violated for the changed-script axis by construction: it has no counter of its own, so it cannot print 0. `:36` lists `checked_reg=A` without defining it.
- Fix: separate `checked_changed=N` in SUMMARY and `--json`, or explicitly document the fold in the `:36-46` contract.

### F4 (LOW): measured-branch verify conflates real git failure with dangling commit
- `:544-552`: `measured_ok = verify.returncode == 0` — rc 128 (real repository error) silently disables the measured branch; run can exit 0 with `checked_measured=0`. Every other git read failure is EvalError→exit 2 (`:163-167`, `:204-208`). SUMMARY=0 does declare "unevaluated" (`:40-41`), so it is honest-by-counter but contradicts S1's "failed git read → exit 2". Fix: rc not in (0,1) → EvalError.

### F5 (LOW — calibration inconsistency): malformed-vs-unreadable expected.json split across channels
- Invalid JSON / bad UTF-8 → finding LG-FROZEN-PIN + `continue` (`:449-457`); `files` shape defect → exit 2 (`:463-467`). Docstring `:32-33` books "malformed expected.json shape" under exit 2. Neither folds to clean, so no false pass — but the same defect class rides two channels and the docstring matches only one. Fix: unify and align the docstring.

## Axis verdicts (with evidence)

**S1 failed git read → exit 2 — holds except F1/F4.** All cited reads are by oid from the enumerated tree (`:278`, membership guard `:622`); `_git` raises EvalError on any nonzero rc (`:163-167`); `blob_at_path` discriminates via `rev-parse --verify --quiet` (`:196-208`). Discriminator probed read-only on this repo:
```
git rev-parse --verify --quiet "ddb7347:nosuch/path.sh"; echo $?   → 1   (absent)
git rev-parse --verify --quiet "ddb7347:census"; echo $?           → 0   (tree: --verify accepts trees → cat-file blob fails → exit 2, matches selftest :1016-1039)
git rev-parse --verify --quiet "0000…0^{commit}"; echo $?          → 1   (dangling)
env -u GIT_DIR -u GIT_WORK_TREE git -C /nonexistent-souji-probe rev-parse --verify --quiet HEAD; echo $? → 128 (real error)
```
so the `:191-194` docstring claim is true as written. Parse failures remain *findings* by design (`:263-281`) — correct: a non-parsing script is a finding, not could-not-evaluate.

**S2 falsy `files` → exit 2 — holds at the `files` level, hole at the top level (F2).** `:463` `not isinstance(files, dict) or not files` covers absent/None/[]/""/0/False/{} and truthy non-objects; no fold-to-clean path remains at that level. A pin can also not silently pass via absent paths (`:475-482`), bad pinned values (`:483-490`), or record mismatch (`:503-531`) — all findings.

**S3 GIT_DIR/GIT_WORK_TREE ignored — holds.** Every git subprocess passes `env=GIT_ENV` (`:161`, `:200`, `:548`; selftest `:741,752`); the six repo-selecting vars are stripped (`:130-142`); `GIT_NO_REPLACE_OBJECTS=1` pins bytes against replace refs and `GIT_NO_LAZY_FETCH=1` makes partial-clone misses loud exit-2 failures rather than wrong bytes. The selftest case (`:1169-1201`) genuinely discriminates: if `env=` were dropped, children would inherit the poisoned `os.environ` → rc 128 → exit 2 → case fails. Residual (informational): `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_n`/`GIT_CONFIG_VALUE_n`, `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_GLOBAL/SYSTEM` are not stripped; none can alter ls-tree/cat-file/rev-parse bytes or repository selection for these plumbing reads (config `diff.renames` can only change which paths the changed branch enumerates — coverage, not bytes).

**SUMMARY per-branch honesty — holds except F3.** Each counter increments only inside its branch body; never-ran prints 0 exactly as `:38-46` declares: `checked_pins` per files key + record_sha256 (`:471,:501`), 0 with no frozen dirs; `checked_measured` only when the measured commit verifies and the loop runs (`:555`), 0 for dangling (`:539-552`); `status_lines` counts every STATUS-channel line including fence/table (`:357-363`), 0 = nothing to look at; `carry_heading` 1 iff the lesson carries the heading, 0 when the lesson is absent (`:377-388`); `checked_reports` ≥ 1 is enforced by the wave-dir EvalError (`:372-373`); on exit 2 the partial counters print with a stderr `COULD-NOT-EVALUATE` line (`:681-695`) — consistent with "not exercised". Selftest case count: 27 `check()` calls + the manual ambient-git-dir case = 28, matching the claimed 28/28; exact-id set equality (`:861`) makes an over-firing gate fail.

## Residual risk and verification gaps
- Static only: F1's crash path and F2's AttributeError are code-path arguments (uncaught-exception → CPython exit 1), not executed reproductions; the `diff --name-only` does-not-quote-plain-spaces premise is standard git behavior, not probed on this repo.
- L1's run results (28/28, gate-replays ddb7347.json, r16 fixture 15/15) were not re-measured here; the selftest has no case for a changed path absent from the tree (F1) or a non-object expected.json (F2) — both would pass 28/28 while the holes stand.
- `bash -n` snapshot OSError (e.g. /var/tmp full) is likewise uncaught → traceback exit 1 (`:247-253`); folded into F1's catch-all recommendation.
