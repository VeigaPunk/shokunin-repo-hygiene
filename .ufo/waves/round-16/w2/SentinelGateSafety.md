# SentinelGateSafety — round 16 wave 2 (source-only security review of tools/souji-landing-gate.py)

Target: `tools/souji-landing-gate.py` at lane HEAD `163158a706352f1c0ee3521c4da2e5289970db57`. The gate was last touched at `a6ec781`. The HEAD blob and the worktree file have the same sha256, `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2`, so the line numbers below refer to both.
Method: I only read the source and git/Python documentation. I did not run the gate, its selftest or its fixture. Every claim below about runtime behaviour is derived from the source plus the cited docs; anything that rests on interpreter or bash internals I have not seen run is marked [INFERENCE].
Threat model: an attacker controls committed content at REV or BASE: blobs, tree entries, path names and modes. The attacker does not control the operator's environment, the repository-local `.git/config`, or the gate script that the operator runs.

## Verdicts on the four questions

| Question | Verdict |
|---|---|
| Can a hostile committed file make the gate execute code? | **holds** (caveats in N1, N2) |
| Can it make the gate write outside /var/tmp? | **holds** |
| Can it make the gate follow a symlink out of its snapshot? | **holds** for escape. Symlinks do cause a parse **evasion** (F4) |
| Can it exhaust resources (huge blob, deep recursion)? | **fails** (F1, F2, F3). Deep recursion in `compile()`/`bash -n` is **holds / fail-closed** |

There is one more defect on the judged axis (calibration). A hostile `expected.json` or `record.json` crashes the gate with a Python traceback, which exits **1**. Exit 1 is documented as "findings", so the run is not reported as could-not-evaluate (exit 2) (F5). Two parse-evasion paths exist in `LG-PARSE-CHANGED` (F6).

### Why "execute code" holds
- Committed bytes reach only three sinks:
  - `bash -n <file under snapdir>` (L201-203).
  - `compile(content, path, "exec")` with no `exec`/`eval` of the result (L216).
  - `json.loads`, `hashlib` and `re` (L383, L460, L337).
- `git cat-file blob` is called without `--textconv` or `--filters`, so committed `.gitattributes` cannot attach filter or textconv drivers (L146-158). The git-cat-file docs restrict textconv and filters to those flags.
- `git diff --name-only` (L557) produces no patch, so `diff.external` and textconv are not consulted.
- `measured_commit` from a committed `record.json` must match `^[0-9a-fA-F]{4,64}$` before it reaches `rev-parse` (L464-472). No option or refspec injection is possible.
- `compile()` honours a PEP 263 coding cookie. [INFERENCE] CPython's `encodings.search_function` only imports undotted `encodings.<name>` submodules from the stdlib package that is already loaded, so a cookie cannot load attacker code.
- [INFERENCE] `bash -n` parses without executing, including command substitutions and here-docs; the gate passes no `-i` flag and no environment changes.

### Why "write outside /var/tmp" holds
- The only filesystem writes on the evaluation path are `os.makedirs` and `open(dest, "wb")` under `snapdir = tempfile.mkdtemp(dir="/var/tmp")` (L197-200, L527).
- `dest` is `snapdir + path`, and `path` must pass `_safe_relpath` (L182-189), which rejects absolute paths and paths whose `normpath` starts with `..`.
- Cited paths are additionally restricted to a single `[A-Za-z0-9_.-]+` segment (L58-60).
- Every pin and record path (L366-368, L394-398) is used only as a key into the in-memory `tree` dict or as a `REV:path` object name. Neither touches the filesystem.
- `--json` is an operator-supplied path, opened with `"x"` (O_CREAT|O_EXCL, L630). This refuses a pre-planted symlink.
- Nit: `_safe_relpath` also rejects legitimate names such as `..foo.sh` because of `norm.startswith("..")`. That is a false finding only (it fails closed).

### Why "symlink escape" holds
- `list_tree` keeps every `blob` entry, including mode-120000 symlinks (L131-143).
- The gate never materialises a symlink. It writes the blob bytes as a regular file.
- `git cat-file blob REV:path` does not follow in-tree symlinks; `--follow-symlinks` exists only in `--batch` mode (git-cat-file docs). The bytes it returns are the link target string, not the target's content.
- `snapdir` is 0700 and freshly created, so no pre-existing link can sit in the write path.

## Findings

### F1 — Blob reads have no size cap and no timeout (resource exhaustion) — severity MEDIUM
- **Exploit path:**
  1. Commit a zlib bomb, for example a few MiB packed that inflates to several GiB of `\n` or `#`.
  2. Point the gate at it as any of: a cited `tools/x.sh` or `tools/x.py`; `SKILL.md` itself; a `.ufo/waves/round-N/*.md` report; `corpus/lessons/round-N.md`; or a pin target under `files[]` in a `tests/fixtures/*-frozen/expected.json`.
- **Evidence:**
  - `_git` (L116-128) and `blob_at_path` (L150-158) use `subprocess.run(..., stdout=PIPE)` and buffer the whole blob in Python. No call passes `timeout=`.
  - For `.sh`, the whole blob is also written to /var/tmp (L199-200), so the bomb fills the disk there.
  - `compile()` (L216) builds an AST for the whole blob.
  - `bash -n` (L201) and `compile` both have unbounded wall time.
- **Impact:**
  - The gate can be OOM-killed or left hanging. No verdict is produced (it is neither exit 1 nor exit 2).
  - A SIGKILL (OOM killer) skips `finally: shutil.rmtree(snapdir)` (L589-590), so hostile bytes stay in `/var/tmp/souji-landing-gate-*`.
  - /var/tmp can be filled up.
- **Smallest fix:**
  1. Run `git cat-file -s <oid>` first, or read the size from `ls-tree -l` in `list_tree`.
  2. Above a pinned cap (e.g. 8 MiB), record a could-not-evaluate (`EvalError` → exit 2). Do not read the blob.
  3. Add `timeout=` to every `subprocess.run` and map `TimeoutExpired` to `EvalError`.

### F2 — Quadratic matching in the carry check and the comment regex (CPU exhaustion) — severity MEDIUM-LOW
- **Exploit path, carry check:**
  1. A report holds M lines of `STATUS: FAIL x<i>`.
  2. The lesson's `## Seat-reported failures` section holds N long lines that do not contain the needle.
  3. `check_carry` re-runs `norm_line` (NFC plus regex) on every lesson line for every needle (L336-337). That is M×N normalisations, each also doing an O(len) `needle in nl` substring test.
  - With M = N = 10^5 this is about 10^10 operations, i.e. an effective hang.
- **Exploit path, comment regex:** `HTML_COMMENT_RE = <!--.*?-->` with DOTALL (L85), applied to the whole lesson (L289). A lesson containing k occurrences of `<!--` and no `-->` makes each attempt scan to end of text, which is O(k·n).
- **Fix:**
  - Normalise `carry_lines` once, before the report loop.
  - Strip comments with a linear scan: `str.find("<!--")` / `str.find("-->", i)`, and treat an unterminated comment as running to EOF. The current regex leaves an unterminated comment unstripped. Pin whichever choice is made.

### F3 — Pin fan-out amplification — severity LOW
- **Exploit path:** an `expected.json` whose `files` has K keys that all resolve to the same large blob.
- **What happens per key** (L395-399, L480-502):
  - One git spawn plus a full read and sha256.
  - When `measured_commit` resolves, a second read at the measured commit, which is hashed **twice** (L491 and L502).
  - The record blob is read twice (L427 and L458).
- **Fix:** memoise `oid → sha256` (`ls-tree` already gives the oid; for the measured commit, use `rev-parse REV:path` to get the oid), and cap K.

### F4 — A symlink stands in for a registry script and "parses" (LG-PARSE-REG evasion) — severity MEDIUM (calibration)
- **Exploit path:** commit `tools/souji-census.sh` (or any cited `.sh`) as a symlink to a broken script elsewhere in the tree, or outside it.
  - `blob_at_path` returns the link text, e.g. `../vendor/real.sh` (L150-158).
  - `bash -n` on a one-word file returns rc 0 with no stderr, so no finding is raised.
  - The registry row then claims "parses" while the bytes that actually run are unchecked.
  - For `.py`, the link text would usually fail `compile()`, so `.py` is accidentally fail-closed.
- **Evidence:** `list_tree` discards the mode field, so the gate cannot tell a symlink from a file (L136-142: `parts[0]` is never inspected).
- **Fix:** keep the mode in `list_tree`. For a cited or changed script whose mode is `120000` (or `160000`), emit `LG-PARSE-REG` / `LG-PARSE-CHANGED` with the detail "not a regular file (mode M)".

### F5 — A crash on hostile JSON exits 1, which means "findings", instead of 2 — severity MEDIUM (calibration)
- **Exploit path:** `evaluate` catches only `EvalError` (L586). Each of the following escapes as an uncaught exception, which makes Python exit with status 1:
  - `expected.json` = `[]` or `"x"` → `expected.get` raises AttributeError (L391).
  - `{"files": [1]}` or `{"files": "x"}` → `.items()` raises AttributeError (L395).
  - `{"record": 1}` or `{"record": ["a"]}` → `key.startswith` raises AttributeError (L366, reached from L394).
  - `expected.json` or `record.json` nested about 10^5 deep, e.g. `[[[[…` → [INFERENCE: CPython's C json scanner raises `RecursionError`]. That is not a `ValueError`, so the except clauses at L386 and L461 do not catch it.
- **Impact:** a caller that keys on the exit code reads "findings present" from a run that evaluated nothing. No `SUMMARY` line is printed and `--json` is not written. `finally` still removes snapdir.
  - It fails closed (nonzero), but under the gate's own exit contract (docstring L33-34: 2 = could-not-evaluate) it is mislabelled.
  - It can mask the real outcome: an operator who fixes the "finding" finds no finding id to fix.
- **Smallest fix:**
  - Validate shapes: `isinstance(expected, dict)`, `isinstance(files, dict)`, `isinstance(record_key, str)`. A violation becomes an `LG-FROZEN-PIN` finding with the detail "expected.json shape invalid".
  - Add `RecursionError` to both except tuples at L386 and L461.
  - Optionally, wrap `main()` so that any unexpected exception returns 2.
- **Coverage:** no hostile-shape case exists in the selftest or in `tests/fixtures/r16-landing-gate.py`. A grep for symlink, quotepath, rename, recursion, nested, unicode and similar terms in the fixture returned no match.

### F6 — `LG-PARSE-CHANGED` can be evaded through path quoting, whitespace splitting and rename status — severity MEDIUM (calibration)
- **Exploit paths:** each takes `--base` and L557-560 as given.
  - **(a) Quoted names.** With `core.quotePath` at its default of true, `git diff --name-only` wraps any path containing bytes ≥0x80, a TAB, `"` or `\` in double quotes with C escapes (git-config docs). A changed `tools/brokén.sh` prints as `"tools/bro\303\251n.sh"`. That ends in `.sh"`, so `SCRIPT_EXT_RE` (L93, L561) silently skips it: the file is never checked and there is no finding.
  - **(b) Spaces.** `.split()` (L560) cuts on spaces, and git does not quote spaces. A changed broken `tools/x y.sh` becomes `tools/x`, which is skipped, plus `y.sh`. If the attacker also commits a well-formed root-level `y.sh`, the decoy is parsed instead and passes. Without the decoy, the result is a mislabelled "blob unreadable" finding.
  - **(c) Renames.** `diff.renames` defaults to true for porcelain `git diff` (diff-config docs). A broken script that is renamed and kept ≥50% similar shows status `R`, which `--diff-filter=AM` excludes. Type changes (`T`) are excluded the same way.
- **Impact:** the "changed scripts parse" claim covers only plain-ASCII, space-free, non-renamed paths.
- **Smallest fix:** run `git diff --name-only -z --no-renames --diff-filter=AMT base resolved` and split on `\0`. Decode with `surrogateescape` so the paths match the `list_tree` keys.
- **Related:** the diff uses the raw `base` string (L557), not the oid resolved at L532. A branch name that moves between the two calls diffs a different base from the one reported in `resolved_base`. Pass the resolved oid instead.

## Notes (informational, not exploitable from committed content)
- **N1 — Startup imports come from the worktree.** `python3 tools/souji-landing-gate.py` puts the lane worktree's `tools/` first on `sys.path`. A `tools/random.py`, `tools/selectors.py` or similar in the **worktree** would run when `tempfile`/`subprocess` import it. This is reachable only if the operator has checked out the hostile revision, and in that case the gate itself is attacker-controlled anyway. Run the gate with `python3 -P` (or `-I`) from a trusted checkout.
- **N2 — Git hardening asymmetry with the census.**
  - `souji-census.sh` exports `GIT_NO_LAZY_FETCH=1` and `GIT_CONFIG_COUNT` with `core.fsmonitor=false` and `core.hooksPath=/dev/null` (souji-census.sh L161-163). The gate's `_git`, `blob_at_path` and `rev-parse` calls set none of these.
  - [INFERENCE] `ls-tree`, `cat-file`, `rev-parse` and tree-to-tree `diff` do not read the index, so fsmonitor and hooks are not triggered.
  - In a partial clone, a `cat-file blob` of a missing object would perform a network lazy fetch.
  - This is controlled by local config, not committed content. For parity, pass the same environment to the gate's git calls.
- **N3 — Deep recursion in the two parsers is fail-closed.**
  - `check_python` catches `Exception`, which covers `RecursionError` and `MemoryError` (L219). [INFERENCE] This assumes an interpreter recent enough to raise rather than overflow the C stack.
  - If `bash -n` crashes on deep nesting, it returns a negative returncode, which yields a finding (L205-207). Unbounded time still falls under F1.
- **N4 — Selftest inherits the operator's global git config.** `run_selftest` calls `git commit` in /var/tmp repos with the operator's global configuration, so a global `core.hooksPath` or `commit.gpgSign` would take effect (L651-668). This is not committed-content-reachable.
- **N5 — Trailing newline in the measured-commit regex.** `$` at L465 also matches before a trailing newline, so `"abcd\n"` passes the regex. `rev-parse` then fails on it, so this is harmless.

## Tool installs
None. Nothing was installed or updated, so I did not need to read RULES.md.

STATUS: FAIL — the gate does not execute code, write outside /var/tmp or follow symlinks out of its snapshot. It does have unbounded resource exhaustion from hostile blobs and quadratic text (F1, F2), and it exits 1 instead of 2 when it crashes on a hostile expected.json or record.json shape or nesting (F5). There are also two evasions: a symlinked registry script that "parses" (F4), and changed-script paths lost to quoting, spaces or renames (F6).

## Commands
```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show HEAD:tools/souji-landing-gate.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD && git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file blob HEAD:tools/souji-landing-gate.py | sha256sum && sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py && git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -3 -- tools/souji-landing-gate.py
echo skip
```
Non-shell reads were exact-file only: grep and read on `tools/souji-landing-gate.py`; grep on `tools/souji-census.sh` and `tests/fixtures/r16-landing-gate.py`. Web reads: git-scm.com `git-config` (core.quotePath), `diff-config` (diff.renames) and `git-cat-file`.
