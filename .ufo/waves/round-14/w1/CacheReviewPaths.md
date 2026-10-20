# CacheReviewPaths — C1 path, key, and protected-path design review (round 14, w1)

Seat: `SoujiR14.CacheReviewPaths` (reviewer, leaf). Axes: calibration, operability.
Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin`.

## Scope and evidence status

- **Artifact status:** `tools/souji-evidence-cache.py` and `tests/fixtures/r14-evidence-cache.py` did NOT exist at review time (glob and read both returned not found). This is a design review, not a code review of C1.
- **Code inspection (done):** the round-13 precedent `tools/souji-cert-evidence.py` (C1 of r13, same contract shape) was read as the reference pattern. Line numbers below refer to that file unless marked otherwise.
- **Exercised evidence:** none. No tests, selftests, builds, or runs were executed. Every claim below is a source-read fact or marked `[INFERENCE]`.
- **Protected trees:** not accessed. No census/operator-sweep, credential, or `~/.omp` content was opened.
- **Installs or upgrades:** none. Tools used were `read`, `glob`, `grep`, and `write` only.

## Findings (ordered by severity)

### H1 — Duplicate JSON keys in `dependencies` launder stale-green (calibration, high)
- Precedent: `souji-cert-evidence.py:384-394` rejects duplicates via `object_pairs_hook`. Plain `json.loads` keeps the last value silently.
- Risk: `{"tools/x.py": "<sha-old>", "tools/x.py": "<sha-new>"}` passes as one dependency with whichever value is last. A reviewer could see the stale hash while the gate hashes the other.
- Required: parse the record and the nested `dependencies` object with a duplicate-rejecting hook. Finding id `duplicate-key`, exit 2.
- Falsifier: fixture with duplicate dependency key where the first hash is the real one and the second is wrong. Expect exit 2 `duplicate-key`, never 0.

### H2 — `--root` symlink into a protected tree is followed and never checked (operability/security, high)
- Precedent: `souji-cert-evidence.py:1517` does `root = Path(os.path.realpath(root))`. `_protected_reason` (`:214-228`) is applied only to the relative key parts (`:462`), never to the root.
- Risk: `--root /var/tmp/x` where `/var/tmp/x` is a symlink to a credential-bearing tree. Every dependency is then hashed from that tree. Name checks on keys pass because the keys look ordinary.
- Required: compare BOTH `abspath(root)` and `realpath(root)` components against the protected rule and the credential-store boundary (the same boundary C2 uses). Refuse a symlinked root outright (finding `root-symlink`, exit 2). Refuse a root that is itself protected, or that is an ancestor of a protected tree when realpath crosses into it (finding `root-protected`, exit 2).
- Falsifier: synthetic `/var/tmp` root symlinked to a synthetic `.ssh/` or `*secret*` dir with a dependency present. Expect exit 2, and assert via command spy that no open/hash of the target occurred.

### H3 — Parent-directory TOCTOU between lstat walk and hash (security/calibration, high)
- Precedent: `_resolve_under` (`:273-300`) lstat-walks every component, then `_digest_regular` (`:350-375`) opens only the leaf with `O_NOFOLLOW`. The precedent documents this gap itself (`:145-147`: "per-file O_NOFOLLOW plus fstat closes the final-component race, not a parent-directory swap").
- Risk: after the lstat walk, a parent directory can be swapped for a symlink, and the leaf open then reads outside root. Stale-green eligibility is exactly where a silent substitution matters.
- Required: walk with `dir_fd`. Open each component with `os.open(part, O_RDONLY | O_DIRECTORY | O_NOFOLLOW, dir_fd=prev)`, then open the leaf with `O_RDONLY | O_NOFOLLOW | O_NONBLOCK, dir_fd=prev`. `fstat` that fd and require `S_ISREG`, `st_nlink == 1`. Hash only from that fd. Use no path re-open after the walk. This is stdlib-only and Linux-available.
- Falsifier (code assertion, not a race run): grep the tool for `dir_fd=` and for the absence of a second path-based `open(` after `_resolve_under`.

### H4 — Key canonicalization silently aliases distinct keys (calibration, high)
- Precedent: `_classify_rel` (`:248-263`) strips empty and `.` components and returns the joined key, so `./a/b`, `a//b`, and `a/./b` all become `a/b`. A C1 record with both `a/b` and `./a/b` present would carry two entries that map to one file, with possibly different hashes.
- Required: do NOT normalize silently in C1. A dependency key must already be canonical: not absolute, no empty component, no `.` or `..` component, no trailing `/`, no backslash, no leading or trailing whitespace, no control characters (<0x20 or 0x7F), and encodable as strict UTF-8 (see M3). Any non-canonical key fails with `key-noncanonical`, exit 2. Reject two keys that normalize equal with `key-alias`, exit 2 (defensive; should be unreachable once non-canonical keys are rejected).
- Falsifier: record with `./tools/x.py` and `tools/x.py`. Expect exit 2 with the non-canonical id, not a silent dedupe.

### M1 — Dependency value and container types (calibration, medium)
- `dependencies` must be a JSON object (`dict`), not a list. Non-empty; `{}` or absent is legacy and must exit 2 (`legacy-no-dependencies`), never reuse.
- Each value must be `str` and match `re.fullmatch(r"[0-9a-f]{64}", value)`. Use `fullmatch`, not `$` (which accepts a trailing newline). Uppercase hex is an alias and must be rejected (`dependency-sha-malformed`, exit 2). `bool`, `null`, numbers, and lists are malformed.
- Precedent for the regex pattern: `SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")` (`:197`). Acceptable, but prefer `fullmatch` in the C1 tool so the intent is explicit.
- Falsifier: one case per invalid value type (`true`, `null`, `123`, `["..."]`, uppercase hex, 63 chars, 65 chars, trailing `\n`).

### M2 — Protected-name list is incomplete for dependency keys (security/calibration, medium)
- Precedent list (`:200-211`) covers `.env*`, `*credential*`, `*secret*`, `id_*`, `*.pem`, `*.key`, `watchdog.log`, `.git`, and the census and `.ufo/state` adjacency rules (`:214-228`). Matching is case-folded (`:216`), which is correct.
- Gaps for a dependency reader: `.ssh`, `.gnupg`, `.netrc`, `.npmrc`, `.pypirc`, `.git-credentials`, `*token*`, `auth.json`, `*.p12`, `*.pfx`, `*.kdbx`, `*.jks`, and any component named `.omp` (credential-bearing agent config). Also `*.gpg` only if it is not used for legitimate evidence.
- Required: the C1 list must be a superset of the precedent list. Keep one shared list definition in the tool and cite the C2 credential-store boundary. Do not copy two divergent lists.
- Check ordering: protected check runs on the canonical key BEFORE any lstat or open (precedent `:462` already does this; keep it).
- Falsifier: dependency keys `.ssh/id_x`, `auth.json`, `Token.txt` (case variant), `.netrc`. Expect exit 2 `path-protected`, and a spy shows no lstat or open.

### M3 — Non-UTF-8 and surrogate keys can escape classification (calibration, medium)
- A JSON string `"\ud800"` passes `_classify_rel` (`:248-263`) because nothing checks encodability. `os.lstat` raises `UnicodeEncodeError`, which is a `ValueError` and not an `OSError`. Precedent `_resolve_under` catches `ValueError` (`:291`), but `_check_claim` line `:480` catches only `OSError`. Any new call site that lstats a classified key without the `_resolve_under` gate would crash.
- Uncaught Python exceptions exit 1, which the contract reads as "stale/failed", not "could-not-evaluate". That misclassifies a malformed input.
- Required: strict UTF-8 check (`key.encode("utf-8")`, catch `UnicodeEncodeError`) in the classifier, `key-invalid-encoding`, exit 2. Wrap `main` so any uncaught exception exits 2, not 1.
- Falsifier: key `"\ud800"` and `"\u0000"`. Expect exit 2 with a named id, and no traceback on stdout.

### M4 — Hardlink alias defeats name-based protection (security, medium)
- Precedent requires `st_nlink == 1` (`:487`, `:598`). Name checks cannot see a second link to a protected inode from an ordinary-looking name.
- Required: check `st_nlink == 1` on the fstat of the open fd (H3), not on a separate lstat. Finding `path-hardlink`, exit 2.
- Falsifier: `os.link` from a synthetic protected file into the root under an ordinary name. Expect exit 2 `path-hardlink`. (Synthetic protected names only, under `/var/tmp`.)

### M5 — Exit-code mapping is ambiguous for path failures (calibration, medium — design decision for L1)
- Contract: exit 1 = stale/failed, exit 2 = malformed/could-not-evaluate. Precedent treats every path refusal as level 2 (`:234`, `_status_for` `:238-243`).
- Recommended mapping so calibration stays honest: digest mismatch on a present, regular dependency → 1 (stale). Missing, symlink, escape, protected, nonregular, hardlink, root-symlink, root-protected, duplicate-key, non-canonical key, malformed hash, legacy/empty deps, bad encoding → 2 (could-not-evaluate). A dependency that cannot be evaluated must never read as "stale, rerun", and a refused path must never read as a clean measurement.
- L1 must pick one mapping, write it in the tool docstring, and have the fixture assert the exit code per case.

### L1 — Stable finding ids (operability, low)
- Require every refusal to emit a named id from the set above (`duplicate-key`, `root-symlink`, `root-protected`, `key-noncanonical`, `key-alias`, `key-invalid-encoding`, `dependency-sha-malformed`, `legacy-no-dependencies`, `path-protected`, `path-symlink`, `path-escape`, `path-hardlink`, `path-absolute`, `path-invalid`, `dependency-missing`, `dependency-not-regular`, `dependency-digest-mismatch`). The fixture asserts ids, not only exit codes.

## Verified-by-reading strengths (keep)

- Classification before resolution, and protected check before any lstat (`souji-cert-evidence.py:450-465`).
- Duplicate-key rejection hook exists (`:384-394`) and can be copied.
- Case-folded protected matching (`:216`).
- Per-component lstat with symlink refusal and commonpath containment (`:273-300`).

## Final L1 commands (not run here)

Run only after all seats land, with explicit `/var/tmp` temp dirs:

1. `TMPDIR=/var/tmp python3 -m py_compile /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-evidence-cache.py`
2. `TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-evidence-cache.py --selftest; echo rc=$?`
3. `TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-evidence-cache.py; echo rc=$?`
4. Assertion greps (static, no run): `grep -nE 'object_pairs_hook|dir_fd=|O_NOFOLLOW|O_NONBLOCK|st_nlink' <tool>` and `grep -nE 'os\.open\(|os\.lstat\(' <tool>` to confirm no path-based open after the walk.
5. Confirm no `timeout`-free or real-home path: `grep -nE '~|expanduser|/home/' <tool>` should match nothing except docstrings.

## Limitations

- Design-level only. Nothing above is observed runtime behavior of C1.
- Precedent behavior at `souji-cert-evidence.py` is a source reading; its own selftest was not run.
- The credential-store boundary definition was not found in PROVINCE.md, SKILL.md, or LOG.md (greps returned no matches). H2 and M2 depend on C2's definition; this is [INFERENCE] about where it will live.
- Race findings (H3) are code-structure findings. No race was exercised.

## Round 2 — static re-review of tools/souji-evidence-cache.py (read only; nothing run)

Read: tools/souji-evidence-cache.py (docstring, boundary, path, open, record, dependency, frozen, emit) and tests/fixtures/r14-evidence-cache.py (grep only). Status vs round 1:

- H1 duplicate keys: closed (`_reject_duplicate_keys`, :650-656).
- H2 root containment: partly closed. Symlink root refused by lstat (:687), but trailing slash bypasses it (see R2-1).
- H3 TOCTOU: closed for dependencies (fd walk, :495-564). Open for record and root (see R2-2).
- H4 canonical keys: closed (`_classify_rel`, :445-475).
- M1 dependency types: closed (`SHA256_RE.fullmatch`, :817).
- M2 protected list: closed (`.netrc`, `.npmrc`, `.pypirc`, `.pgpass`, `.git-credentials` in PROTECTED_NAME_PATTERNS, :265-271; `.omp` in PROTECTED_DIRS, :262-264).
- M3 encoding: closed (`key-invalid-encoding`, :454-457).
- M4 hardlink: closed (`st_nlink > 1` on fstat, :552).
- M5 exit mapping: WITHDRAWN for missing dependency. Missing dependency is exit 1 (stale, `dependency-missing` is level 1). Accepted: a well-formed record whose declared bytes are absent is stale and fail-closed. Other path refusals stay exit 2.

Open findings:

- R2-1 [medium, contract] Trailing-slash bypass of root-symlink. `_resolve_root` calls `os.lstat(value)` on the raw string (:687). POSIX resolves a symlink with a trailing slash, so the symlink check never fires. Fix: `os.lstat(os.path.abspath(value))`. Fixture: add plain and trailing-slash root-symlink cases (none found by grep).
- R2-2 [medium, TOCTOU] Record and root opened by name after the walk: `_read_path_text` `os.open(absolute)` (:622) and `_resolve_root` `os.open(resolved)` (:699). The walk checks link targets at check time, then the open re-resolves ancestors. Fix: fd walk from `/` with `dir_fd` and `O_NOFOLLOW` per component; re-apply the tree and name checks on each readlink target.
- R2-3 [medium, calibration/operability] `_walk_boundary` returns one reason for EACCES, ENOTDIR, unreadable link, and >40 link depth; callers map every reason to protected (:601-603, :684-685). A permission error is reported as a credential refusal. Fix: differentiate kinds; map to record-unreadable / root-not-directory (still exit 2). Fixture: unreadable synthetic ancestor under /var/tmp.
- R2-4 [low-medium, operability] fnmatch name patterns apply to every ancestor of --root (:692-693) and every record path component (:604-607), so a checkout under a `token-*` or `secrets-*` directory is refused on every run. Operator decision: keep the tree boundary and PROTECTED_DIRS/PAIRS for ancestors; apply patterns only to dependency keys and the record basename.
- R2-5 [low, operability] `_digest_fd` has no time bound; O_NONBLOCK does not bound a stalled FUSE/NFS regular file. 1 GiB cap per dependency. Bound it or document it as a non-guarantee (r13 Q8 precedent).
- R2-6 [low] `key-alias` (:839-842) is unreachable given canonical keys and unique JSON keys. Keep as an unreachable assertion or drop it with the docstring claim (:96-97).

Fixture coverage (grep only, not executed): no `root-symlink` case, no `key-invalid-encoding` literal (`ud800` no match), no unreadable-ancestor case. Confirm or add.

No high-severity exploitable read was found. The highest open items are medium (R2-1, R2-2, R2-3). Exercised evidence: none. Installs or upgrades: none.

Final L1 commands: unchanged from the round-1 section, plus the root-symlink trailing-slash case and a surrogate-key case in the selftest expectations.

## Round 3 — static re-read after CacheGate path fixes (read only; nothing run)

Verified in source (not executed):

- R2-1 root trailing-slash: closed. Root lstat is on `os.path.abspath(value)` (:773, :787). Fixture trailing-slash case at :1511.
- R2-2 record/root reopen: closed. `_open_no_symlink` walks from `/` with per-component `O_NOFOLLOW` (:602-621). Root open (:803) and record open (:720) use the walked path. A swapped symlink component fails with ELOOP or ENOTDIR and is refused, never followed.
- R2-3 walk failure kinds: closed. `_walk_boundary` returns protected / unreadable / not-directory / loop (:428-473). Root maps protected to root-protected and the rest to root-not-directory (:780-785). Record maps protected to record-protected and the rest to record-unreadable (:702-705, :830).
- R2-4 name patterns: closed for ancestors. Name patterns apply only through `_protected_reason` on dependency keys (:346-355) and `_protected_absolute_reason` on the basename (:358-370). Directory and pair rules still cover all ancestors through `_protected_components` (:323).
- R2-5 time bound: documented as a non-guarantee (:227-229).
- R2-6 key-alias: kept as a documented unreachable defensive check (:96-98, :943). `dependency-duplicate` is absent from the source.
- Surrogate fixture: JSON `\ud800` escape at fixture :1548-1549 decodes to a lone surrogate, rejected by `_classify_rel` as `key-invalid-encoding`.

Residuals (low):

- A. Root basename still matches `*token*`, `*secret*` and similar (:774, :798). A root such as `/var/tmp/token-audit` is refused `root-protected`. Accept and document, or exempt the basename.
- B. `_read_path_text` line 711 calls `os.lstat(absolute)` by name. It is a pre-check, not an open, and the read is fd-only. Remove it to make the no-reopen claim literal.
- C. "39 cases" is unverified. L1 must confirm the fixture summary regex (fixture :172) matches the tool's `selftest: N/N passed` line.

No high-severity finding remains. Exercised evidence: none. Installs or upgrades: none.

Final L1 commands: unchanged. Add a check that the tool's selftest summary line matches the fixture regex before trusting the case count.

## Round 4 — static verification of round-3 residuals (read only; nothing run)

- A (basename rule): closed and documented. Tool docstring :142-145 states that name patterns apply to dependency components and to the basename of an absolute root/record path, so `/var/tmp/token-audit` is refused. `_protected_absolute_reason` (:375-380) carries the same rationale.
- B (no-reopen wording): closed. Docstring :117-119 states that root and record bytes are read only from the walked fd, with a single `lstat` of the original path to detect a final symlink. Code matches: `_read_path_text` lstat at :711 precedes the walked open at :720.
- C (selftest count and summary): closed. The tool prints `selftest: %d/%d passed` (:1798). The fixture regex `^selftest: (\d+)/(\d+) passed$` (fixture :172) matches it exactly. Fixture `check()` uses exact-line `^...$` matches (:87-88). Case count: 48 `cases.append` sites in the tool (`:1318` through `:1465` shown; the full set was not counted line by line here).

Exercised evidence: none. Installs or upgrades: none.

No open findings remain from the round-1 through round-3 path review. Final L1 commands are unchanged. Run the tool's `--selftest` once after all seats land and confirm the summary line reads `N/N passed` with N=48 before trusting the count.
