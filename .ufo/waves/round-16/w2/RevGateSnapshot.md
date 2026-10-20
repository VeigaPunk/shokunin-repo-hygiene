# RevGateSnapshot — landing-gate source review: blob extraction, revision handling, snapshot cleanup, exit-2

Seat: SoujiR16.RevGateSnapshot-4. Mode: source only (the gate was not executed; every claim below is a code-path derivation unless marked as a reproduced command).

Target: `tools/souji-landing-gate.py` (blob `7d32ba7c988f56531bf76e46530ad76c92f5a24c`) and `tests/fixtures/r16-landing-gate.py` (blob `e1737f6dc39c409005c07f0ab26e14d938d94997`) at the assigned lane HEAD `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`.

Provenance note: HEAD advanced during the review to `163158a706352f1c0ee3521c4da2e5289970db57` (parent `a6ec7810`, confirmed with `rev-parse`). The two target blobs are byte-identical at both revs (`cat-file` + `sha256sum`: `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` and `aae67c9c7bafd86f1b745193ac4aead74b3a3403b5c5ade33991d246e6413f2`, equal to the worktree files), so every line citation is valid for the assigned HEAD.

## Verdict by area

- **Blob extraction (`ls-tree`/`cat-file`)** — holds. No defect beyond the already-filed symlink case (Sentinel F4). See "Holds" 1.
- **Revision handling** — holds on the SHA-pinned path; the quote/space/rename evasions and the raw-`base` reuse are already filed (Sentinel F6 and its "Related" line; RevGateCLI F4). One new rooting hazard (S3). No additional `rev` lifecycle defect.
- **Temp snapshot cleanup** — holds on every normal and `EvalError` path; the only failure mode is the creation-before-`try` `OSError` class already filed as RevGateCLI F3. No new defect.
- **Exit-2 paths** — partial. Two exit-1 misclassifications in this area are not covered by the sibling reports (S1, S2); the crash-shape and emit-ordering cases are already filed (Sentinel F5, RevGateCLI F1/F2/F3) and are confirmed, not re-filed.

## New findings

### S1 — a failed git read inside `blob_at_path` becomes a landing finding (exit 1), never could-not-evaluate (exit 2) — severity LOW

- **Where:** `tools/souji-landing-gate.py:150-159` (`blob_at_path` returns `None` for *every* nonzero rc), consumed at `:226-228` (`parse_script` → `"blob unreadable at %s"`) and `:481-489` (measured-pin loop → `LG-FROZEN-MEASURED ... absent at measured_commit`).
- **Trigger:** a git read failure that is not "path absent": missing/promisor object with lazy fetch disabled, corrupt pack, permission/ownership error, or a path that resolves to a tree. Only this read path swallows the error; every `_git`-mediated read (`ls-tree`, `cat-file blob <oid>`, `rev-parse`) correctly raises `EvalError` (`:124-128`).
- **Impact:** the tool's own exit table (`:33-34`: "2 could-not-evaluate (... git failure)") is violated. A repository-level read failure is reported as `LG-PARSE-REG`/`LG-PARSE-CHANGED` (registry paths are known present in `tree` at `:549`, so `None` there is always an I/O failure, not absence) or as a false `LG-FROZEN-MEASURED`, and the run exits 1 — indistinguishable from real findings.
- **Smallest fix:** distinguish "not found" from failure, and prefer the oid already in hand:

```python
def blob_at_path(root, rev, path):
    spec = "%s:%s" % (rev, path)
    p = subprocess.run(["git", "-C", root, "rev-parse", "--verify", "--quiet", spec],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode == 1:          # --verify: path does not resolve at rev
        return None
    if p.returncode != 0:
        raise EvalError("git rev-parse %s failed (rc=%d)" % (spec, p.returncode))
    return blob_by_oid(root, p.stdout.decode("ascii").strip())
```

`parse_script` already receives `tree`, so its REV-script reads can simply be `blob_by_oid(root, tree[path])`; `blob_at_path` is then needed only for the measured-commit pins.

Verified against this lane (read-only): `git rev-parse --verify --quiet HEAD:no-such-file` exits 1, while `git cat-file -e HEAD:no-such-file` exits 128 for the same missing path (and 0 for a present one). The existence probe therefore has to be `rev-parse --verify --quiet` (rc 1 = absent), not `cat-file -e` (128 = indistinguishable from a fatal error).

- **Verdict:** fails (exit-2 completeness); conditional on a repository read failure — not observed in this lane.

### S2 — `{"files": null}` (and every falsy non-object) folds to `{}` before any shape check, so a frozen pin set can silently verify nothing — severity MEDIUM (calibration)

- **Where:** `tools/souji-landing-gate.py:391` `files = expected.get("files") or {}`.
- **Trigger:** a committed `tests/fixtures/*-frozen/expected.json` whose `files` is `null`, `[]`, `""`, `0` or `false`. Every falsy value becomes `{}`, so the pin loop (`:395`), the `record_sha256` block (`:427`) and the measured loop (`:478`) run zero pin checks; no `LG-FROZEN-PIN` is emitted and the gate exits 0 with `checked_pins=0`. (Non-empty wrong types — `[1]`, `"x"` — crash exit 1 instead; that half is filed as Sentinel F5 at `:391`/`:395`.)
- **Impact:** a landing that rewrites a frozen `expected.json` to `{"files": null, "verdict": "clean"}` removes the whole frozen-pin axis from evaluation while reporting a clean verdict — the one silent false-clean direction in this area. Deleting the file outright has the same effect (see gaps). It is reachable with valid JSON, so neither the JSON guard at `:383-390` nor Sentinel F5's crash cases fire.
- **Smallest fix:** validate the raw value before folding; keep an absent key legal, but do not accept an explicit non-object:

```python
raw_files = expected.get("files", {})
if not isinstance(raw_files, dict):
    findings.append(("LG-FROZEN-PIN", exp_path,
                     "files is not an object: %s" % type(raw_files).__name__))
    raw_files = {}
files = raw_files
```

(This is deliberately stricter than Sentinel F5's `isinstance(files, dict)` sketch: that sketch, applied after `or {}`, cannot see `null` or `[]`.)

- **Verdict:** fails (silent zero-pin pass); conditional on a landing editing the pin file.

### S3 — every git call inherits ambient `GIT_DIR`; `--root` does not select the repository — severity LOW (verified behavior)

- **Where:** `tools/souji-landing-gate.py:118-123` (`_git`), `:152-156` (`blob_at_path`), `:469-475` (measured `rev-parse`), and the selftest at `:653`/`:659`. None passes an `env=`.
- **Trigger:** any caller with `GIT_DIR` (or `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`) exported. Reproduced: `GIT_DIR=/nonexistent/x.git git -C <lane> rev-parse --verify --quiet HEAD` → `fatal: not a git repository: '/nonexistent/x.git'`, rc 128, while the same command without `GIT_DIR` returns the lane SHA. `-C` does not override `GIT_DIR`.
- **Impact:** with a *valid* foreign `GIT_DIR` the gate resolves `--rev` and reads blobs from that repository, then reports findings/exit 0 for the wrong repo while `resolved_rev`/`resolved_base` in `--json` look normal. With a nonexistent one it exits 2 (honest, but for the wrong reason). This is the same class the census hardened (Sentinel N2), but here it is repository *selection*, not just config: `GIT_NO_LAZY_FETCH`/`GIT_NO_REPLACE_OBJECTS` are also unset, so a partial clone can fetch over the network and replace refs can substitute "committed" bytes.
- **Smallest fix:** one sanitized environment used by every git call (and by `_mkrepo`):

```python
GIT_ENV = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE",
                        "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
                        "GIT_COMMON_DIR")}
GIT_ENV["GIT_NO_LAZY_FETCH"] = "1"
GIT_ENV["GIT_NO_REPLACE_OBJECTS"] = "1"
```

- **Verdict:** fails (revision rooting is not hermetic); conditional on the caller environment — a normal shell exports none of these, so not observed in this lane.

## Independently confirmed, already filed (not re-filed)

- **Sentinel F5** (hostile JSON shape → crash exit 1): `:383-395`, `:366` — confirmed. S2 is the falsy variant that their fix must not fold away first.
- **Sentinel F6** (quotePath / space splitting / rename status, plus raw-`base` reuse): `:557-560`, `:558` — confirmed. Integration note for the agreed `-z` fix: `_git(..., binary=False)` decodes with `"replace"` (`:128`), while `list_tree` keys use `surrogateescape` (`:140`); take `-z` output as bytes and split `b"\0"` (or decode `surrogateescape`) or non-UTF-8 names will not match `tree`.
- **Sentinel F4** (a symlinked registry script "parses"): `cat-file blob <rev>:<path>` returns the link text, which `bash -n` accepts — confirmed.
- **Sentinel F3** (measured pin hashed twice): `:491` and again inside the finding at `:502` — confirmed.
- **RevGateCLI F1** (`emit` returns 2 after printing findings): `:595-614`, `:630-635` — confirmed.
- **RevGateCLI F2** (findings dropped, counters kept): counters `:548`, `:563`, `:571`, `:578` are set before `check_carry` is called at `:574`; `result["findings"]` is only assigned at `:581-584` — confirmed. A rev with a broken cited script and no round `.md` reports yields exit 2, `findings=[]`, `checked_reg>=1`.
- **RevGateCLI F3** (`OSError` → traceback + exit 1): `:527` (before the `try` at `:528`), `:198-201`, `:749` — confirmed.
- **RevGateCLI F4** (`changed_out.split()`): `:560` — confirmed; fully subsumed by Sentinel F6(b).
- **Forward-looking integration note** (not a current defect): `emit` sanitizes only `detail` (`:597`), not `path` (`:598`). Once the diff becomes `-z`, a changed filename containing a tab/newline would corrupt the `id\tpath\tdetail` row; sanitize `path` in the same patch.

## Holds — checked, no defect

1. **Blob provenance.** `list_tree` (`:131-143`) parses `ls-tree -r -z --full-tree` with NUL framing, first-TAB partition, a `blob`-type filter and ASCII oids. Every content read is `cat-file blob <oid>` (`:146-147`) from commit objects — never `git archive` (`:20-23`, `:112`), never the worktree — so `export-ignore`/`export-subst`/attributes cannot alter the hashed bytes and uncommitted edits cannot affect a verdict. Pin keys are resolved through `tree` only (`tree.get` at `:397`, guarded `in tree` at `:427`/`:458`), so a hostile pin key never reaches the filesystem. `check_bash` writes only under `snapdir`, and only after `_safe_relpath` (`:176-183`, `:194-197`) rejects absolute and `..` paths.
2. **Revision pinning.** `rev` is resolved once to a full SHA (`:529-533`), and every later read uses `resolved` (`:534`, `:549`, `:558`, `:564`, `:569`, `:574`); ref movement cannot swap the evaluated tree mid-run. `ls-tree` is quote-safe (`-z`). `--base` is also resolved (`:531`); its raw-string reuse in the diff is the filed Sentinel F6 note, not a separate finding.
3. **Snapshot lifecycle.** One private `mkdtemp(dir="/var/tmp")` per `evaluate` (`:527`), all writes inside it, and `shutil.rmtree` in `finally` (`:589-590`) on normal return and on every caught `EvalError` (including `:314` and `_git` failures). `run_selftest`'s own `top` (`:749`) is removed at `:968`. No path writes a snapshot outside `/var/tmp`; the only leak/exit-mode gap is creation before `try` (RevGateCLI F3). No new defect.
4. **Documented exit-2 mapping.** Unknown/unresolvable revision (`:162-169`), missing `SKILL.md` (`:535-536`), no `.md` reports under `.ufo/waves/round-N/` (`:314`), every `_git` rc≠0 (`:124-128`), missing `--root`/non-directory root, and usage errors (`:994-1001`) all return 2. `emit` prints `COULD-NOT-EVALUATE` on stderr and still writes `--json` with `exit: 2` and the error.
5. **Frozen-pin semantics.** Prefix rule (`:364-368`), `record_sha256` (`:427-455`) and `measured_commit` cross-check (`:458-504`) match the pinned docstring; a dangling/non-hex `measured_commit` deliberately contributes no checks (`:464-476`), which is consistent with shallow/partial checkouts. No finding.

## Verification gaps and residual risk

- **Source-only by assignment:** the gate was not executed, so the five/selftest/fixture tallies are not re-measured here. S1/S2/S3 are code-path derivations with their triggers stated; only S3's `GIT_DIR` override was reproduced (with `git rev-parse`).
- **Fixture coverage:** `tests/fixtures/r16-landing-gate.py` has no case for a malformed `expected.json` shape, a whitespace/non-ASCII/renamed changed path, ambient `GIT_*`, missing `git`, unwritable `/var/tmp`, or `--json`. Its `evaluate()` (`:176-196`) asserts rc plus listed rows only, and the gate selftest's `check()` (`:766-771`) requires only `all(i in ids)` + `forbid_ids`; a regression that adds spurious ids to an expected-exit-1 case still passes. The "changed 20/20 / 18/18 / 15/15" design does not catch over-firing.
- **Pin-set deletion:** frozen dirs are discovered solely by the presence of `tests/fixtures/*-frozen/expected.json` (`:375-379`); deleting that file at REV removes the pin axis with `checked_pins=0` and no finding. The gate does not claim pin-set inventory, but if C2 wants round-15 defect 2 covered, the integrator must run `tools/souji-preservation-evidence.py --frozen` alongside it (or the gate must pin the pin-set inventory).
- **Object/env hardening:** `GIT_NO_REPLACE_OBJECTS`/`GIT_NO_LAZY_FETCH` are unset (`:118-123`, `:152-156`, `:469-475`), so the docstring's "committed bytes" is exact only on a repository without `refs/replace`; a partial clone may fetch during the run. Conditional; same fix site as S3.
- **Out of area but noted:** the fixture docstring at `:22-23` and `:38` still describes the dropped "benign allowlist + phrase markers" rule, while the implementation uses only the failure vocabulary (`:63-73`, `:257-270`). Likely carry-seat overlap; not filed here.

STATUS: PARTIAL — blob provenance, SHA-pinned revision handling and snapshot cleanup hold, and all filed sibling findings are independently confirmed; exit-2 totality has two additional holes (S1: a failed git read becomes a finding/exit 1; S2: a falsy `files` value silently drops the whole pin set), and revision selection is not rooted against ambient `GIT_DIR` (S3).

## Commands

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git -C . rev-parse HEAD && git -C . ls-tree -r --name-only HEAD | head -100
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la tools tests/fixtures 2>/dev/null | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "ls-tree\|cat-file\|mktemp\|mkdtemp\|TemporaryDirectory\|tempfile\|exit(2)\|exit 2\|sys.exit" tools/souji-landing-gate.py tools/souji-preservation-evidence.py tools/souji-seat-audit.py tests/fixtures/r15-preservation-frozen/regenerate.py 2>/dev/null
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l tools/souji-landing-gate.py tools/souji-preservation-evidence.py tools/souji-seat-audit.py tools/souji-census.sh tests/fixtures/r15-preservation-frozen/regenerate.py 2>/dev/null; ls -la tests/fixtures/r15-preservation-frozen/
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "def list_tree\|def blob_by_oid\|def blob_at_path\|def resolve_commit\|def evaluate\|snapdir\|mkdtemp\|rmtree\|changed_out\|diff --name-only\|name-only\|record_bytes\|files.items\|expected.get\|record_key\|return 2\|exit\"\] = \|except EvalError\|except OSError\|json_out" tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "git\|tempfile\|mkdtemp\|rmtree\|sys.exit\|return 2" tools/souji-preservation-evidence.py | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "_pin_repo_path\|ROOT_PREFIXES" tools/souji-landing-gate.py | head; grep -n "phrase markers\|benign allowlist\|snapshot_tampered\|syntax error" tests/fixtures/r16-landing-gate.py | head -20
true
cd /home/vgpnk/Projects/shokunin/souji-shokunin && GIT_DIR=/nonexistent/x.git git -C . rev-parse --verify --quiet HEAD; echo "with_env_rc=$?"; git -C . rev-parse --verify --quiet HEAD; echo "clean_rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "dict(os.environ)\|GIT_AUTHOR_NAME\|def _mkrepo" tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD; git rev-parse --verify --quiet HEAD; git ls-tree a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py; git ls-tree HEAD tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py; sha256sum tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git cat-file blob 7d32ba7c988f56531bf76e46530ad76c92f5a24c | sha256sum; git cat-file blob e1737f6dc39c409005c07f0ab26e14d938d94997 | sha256sum; git rev-parse 163158a706352f1c0ee3521c4da2e5289970db57^
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -m py_compile tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py && echo PYCOMPILE_OK
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "all(i in ids\|forbid_ids\|def check(\|def evaluate(proc" tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "blob = blob_at_path\|content = blob_at_path\|if content is None\|files = expected.get\|record_key = expected.get\|for key, pinned in sorted(files.items())\|if record_bytes :=\|except (ValueError, UnicodeDecodeError)\|expected = json.loads" tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '20,40p' tests/fixtures/r16-landing-gate.py | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "^#\|^##\|json\|exit 2\|mkdtemp\|split\|rename\|expected.json\|GIT_DIR" .ufo/waves/round-16/w2/RevGateCLI.md | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "isinstance\|AttributeError\|not an object\|files is not\|GIT_DIR\|blob_at_path\|resolved_base\|quotePath\|--no-renames\|rename" .ufo/waves/round-16/w2/MutateGateFrozen.md .ufo/waves/round-16/w2/RevRegenerate.md .ufo/waves/round-16/w2/CriticC2Calibration.md .ufo/waves/round-16/w2/SimplifyGate.md .ufo/waves/round-16/w2/SentinelGateSafety.md 2>/dev/null | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "^##\|^###\|blob_at_path\|conflat\|unreadable\|measured_commit\|GIT_DIR\|GIT_NO_REPLACE" .ufo/waves/round-16/w2/SentinelGateSafety.md | head -50
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "archive\|\.git/\|os.getcwd\|chdir" tools/souji-landing-gate.py; grep -n "files.*null\|or {}" tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "checked_reg\|checked_pins\|findings.sort\|result\[\"findings\"\]\|check_carry(\|pin_findings\|carry_findings\|result\[\"checked_markers\"\]" tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "^STATUS:" .ufo/waves/round-16/w2/RevGateCLI.md .ufo/waves/round-16/w2/SentinelGateSafety.md .ufo/waves/round-16/w2/SimplifyGate.md .ufo/waves/round-16/w2/RerunGateSelftest.md .ufo/waves/round-16/w2/RevRegenerate.md 2>/dev/null
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "def is_failure_line\|FAILURE_STATUS_WORDS\|STATUS_PREFIX_RE\|def status_value\|def seat_failure_lines" tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "^STATUS" .ufo/waves/round-16/w2/RevGateSnapshot.md; wc -l .ufo/waves/round-16/w2/RevGateSnapshot.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse --verify --quiet HEAD:no-such-file 2>/dev/null; echo "revparse_missing_rc=$?"; git cat-file -e HEAD:no-such-file 2>/dev/null; echo "catfile_missing_rc=$?"; git cat-file -e HEAD:tools/souji-landing-gate.py 2>/dev/null; echo "catfile_present_rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "revparse_missing_rc\|catfile_missing_rc\|catfile_present_rc" .ufo/waves/round-16/w2/RevGateSnapshot.md; tail -5 .ufo/waves/round-16/w2/RevGateSnapshot.md
```

Notes on the command list: `true` was a no-op placeholder in a parallel batch; `sed -n '20,40p' … | cat -n` was a read-only slice of a named file. All reads were exact-file reads; no directory-recursive grep, no execution of `tools/souji-census.sh`, no gate execution, no lane mutation other than this report.
