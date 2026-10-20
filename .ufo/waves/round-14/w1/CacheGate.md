# CacheGate — C1 digest-bound evidence-cache eligibility (r14 w1)

Seat: `SoujiR14.CacheGate` (executor, leaf). Axes: calibration, operability.
Scope: declared-dependency eligibility only. No inference of a complete
dependency set, no command execution, no historical-execution proof.

## Files written

- `tools/souji-evidence-cache.py` (new, stdlib only)
- `tests/fixtures/r14-evidence-cache.py` (new, black-box replay)
- `tests/fixtures/r14-cache-frozen/dependency.txt` (new)
- `tests/fixtures/r14-cache-frozen/record.json` (new)
- `tests/fixtures/r14-cache-frozen/expected.json` (new; pins both inputs)
- this report

No historical runner, shared bookkeeping, census/operator sweep, or sibling
path was modified. No tools installed or upgraded.

## Interface

```
souji-evidence-cache.py --root DIR --record JSON [--require REL ...]
souji-evidence-cache.py --frozen DIR
souji-evidence-cache.py --selftest
```

`--record` accepts literal JSON text, `@PATH`, or a bare regular-file path
(the retention-runner form). Exit codes: 0 reusable, 1 stale/failed,
2 malformed/could-not-evaluate. Findings are `finding <id>: <detail>` lines
with stable ids listed in the module docstring. Level-2 findings dominate.

Record: `name` non-empty control-free string; `matched` exact JSON boolean
(integer/string rejected as `matched-false-type`); `measured_commit` required
40 lowercase hex, never defaulted from HEAD or a run-level field, echoed
verbatim as `measured_commit: <value>`; `dependencies` required, non-empty,
canonical relative keys, values exactly `[0-9a-f]{64}`. Duplicate JSON keys
are rejected at parse (`record-malformed`). Optional `exit_code` /
`expected_exit` must agree with `matched` (`verdict-false-pass` /
`verdict-false-fail`).

Path handling: dependency reads use an fd walk from an `O_NOFOLLOW` root fd,
one `O_DIRECTORY|O_NOFOLLOW` open per component and one
`O_NOFOLLOW|O_NONBLOCK` leaf open; then fstat requires a regular file,
`st_nlink == 1`, and `st_dev == root_dev`, with a 1 GiB digest cap. Keys must
be canonical (no `./`, `//`, trailing slash, backslash, `.`/`..`, lone
surrogate); refused before any open. Protected names are refused before any
lstat/open, so no digest is ever printed for a refused path.

Root/record boundary: lexical (`abspath` string and directory/pair names)
refusal happens first, before any lstat; only then a componentwise `readlink`
walk with a 40-link cap, refusing the moment a link target is protected.
`realpath` is never called. The walk distinguishes protected, unreadable,
non-directory, and loop failures, so a permission error is not mislabeled
protected. The walked result is opened by a second per-component `O_NOFOLLOW`
walk from `/`; root and record bytes are read only from that fd, with one
`lstat` of the original path to detect a final symlink.
Secret-shaped name patterns apply only to dependency keys and the basename of
an absolute root/record path, avoiding refusal of an ordinary checkout under
e.g. `/var/tmp/token-audit`. Protected trees union `$HOME`, the passwd home,
`/root`, `PI_CODING_AGENT_DIR`, each home's `PI_CONFIG_DIR` directory (default
name `.omp`) and its `agent` child (an absolute `PI_CONFIG_DIR` is used
as-is), `home`-relative credential paths (`.omp/agent`, `.ssh`,
`.gnupg`, `.password-store`, `.config`, `.local/share/keyrings`, `.aws`,
`.docker`, `.kube`, `.netrc`, `.git-credentials`, `.npmrc`, `.pypirc`,
`.pgpass`), and `/etc`, `/proc`, `/sys`, `/dev`. A root that equals, is inside,
or is an ancestor of any is refused; a symlink root (including a trailing
slash spelling) is `root-symlink`.

Frozen mode: `expected.json` = `{record, verdict, files{rel: sha256}}`. Pins
are verified by the same fd walk before the record is read; pin
missing/nonregular/symlink/hardlink/device/oversize/mismatch is
`snapshot_tampered`. Every declared dependency and the record must be pinned
or `frozen-incomplete`. Evaluation then runs normally and its status must
match `verdict` (`snapshot-verdict-mismatch`).

## Exit-mapping decisions (explicit)

- digest mismatch of a present regular dependency: **1 stale**
- missing declared dependency file: **1 stale** (the record is well formed;
  the declared target moved or was deleted). `CacheReviewPaths` round-2
  accepted this mapping and withdrew its earlier M5 "missing=2" note; the
  fixture and selftest assert it.
- `matched: false`: **1 failed**
- legacy/absent dependencies, empty dependencies, malformed digest,
  non-boolean matched, malformed/absent measured_commit, non-canonical key,
  duplicate key, absolute/escape/symlink/nonregular/hardlink/cross-device/
  oversized/protected path, protected root/record, undeclared `--require`,
  false-pass/false-fail: **2 could-not-evaluate**

## Discriminating cases

Tool `--selftest` has 48 cases and asserts exact finding-id sets, exit
codes, and status/commit lines as literals: positive, unrelated-file change,
changed dependency,
missing, symlink (leaf and ancestor), malformed hash, escape, absolute,
failed, legacy, empty, non-boolean matched, duplicate keys, malformed commit,
nonregular, hardlink, protected dependency, protected record path, protected
root, symlink root (plain and trailing slash), synthetic-home ancestor/alias
root and alias record, non-canonical key, lone surrogate, false-pass,
false-fail, expected-exit disagreement, oversize, `--require`
declared/undeclared/invalid, dependencies-invalid, path-invalid,
path-not-directory, root-not-directory, record-unreadable, per-result commit
echo, record-path form, frozen clean/tampered/incomplete/verdict-mismatch,
and frozen unreadable/malformed/schema.

External fixture has 22 cases with hard-coded ids/codes, default run is
flagless (`--tool PATH` optional; a missing path is a distinct
`fixture: tool missing:` diagnostic with exit 2). It asserts the exact
`measured_commit` echo and zero `finding` lines on success, self-asserts
>= 20 cases, uses a synthetic HOME and `mkdtemp(dir="/var/tmp")` with
finally-cleanup (no `/dev/shm`, no bare `tempfile` default).

Committed frozen fixture pins (computed with `sha256sum`, not a run):

```
875598b6f830e010b5fc1c6db42528ef127423623e1af60d276be6527623366a  dependency.txt
67221a338ef4ada7505d26a41cc634fcbabb1e6b64e8ef47138e7b766871df41  record.json
```

`record.json` carries `measured_commit
0123456789abcdef0123456789abcdef01234567`; `expected.json` verdict is
`reusable`.

## Static-review corrections (no runs)

Peer reviewers read the landed files without executing them; these defects were
found and fixed in place before hand-off:

- `_read_path_text` returned a 2-tuple on success while `--record PATH`
  unpacked 3, which would have made every file-path record an
  `internal-error`; fixed to `(text, None, None)`.
- `frozen-incomplete` emitted one finding per unpinned dependency, breaking
  the exact-id assertion; it now emits one aggregated finding.
- `root-symlink` missed a trailing-slash spelling; root lstat now uses the
  normalized absolute path.
- A directory symlink opened with `O_DIRECTORY|O_NOFOLLOW` reports `ENOTDIR`
  on Linux; the walk now nofollow-stats an `ENOTDIR` component and reports
  `path-symlink` (selftest case `symlink-ancestor`).
- Root and record files are now opened by a second per-component
  `O_NOFOLLOW` walk after boundary resolution, not by their original strings.
- Boundary failures distinguish protected from unreadable/not-directory/loop.
- Secret-shaped fnmatch patterns apply only to dependency keys and absolute
  basenames, so an ordinary checkout beneath an ancestor named `token-audit`
  is not refused; a root whose own basename is `token-audit` is conservatively
  refused `root-protected`.
- Output now includes a `scope:` non-claim line and a `root: '<path>'` line.
- Fixture frozen-snapshot copies use `symlinks=True`; scratch HOME setup is
  inside the try/finally so an early error cannot leak the `/var/tmp` base.
- Protected store set adds `.mozilla`, `.thunderbird`, `.pki`,
  `.var/app`, `.local/share/kwalletd`; a symlink-relocated store outside the
  lexical home is an explicit non-guarantee.
- Selftest status/commit/dependency/frozen-count lines are matched as exact
  lines, not substrings; nine previously uncovered ids now have cases
  (`dependencies-invalid`, `require-invalid`, `root-not-directory`,
  `record-unreadable`, `path-invalid`, `path-not-directory`,
  `frozen-unreadable`, `frozen-malformed`, `frozen-schema`).

## Code inspection vs exercised evidence

- **Inspected:** all new source, fixture, and frozen-snapshot files; Python
  `ast.parse` syntax-only validation passed for both `.py` files. No behavior
  was run by this seat, per the wave rule and the "no actual store tests"
  instruction.
- **Exercised:** none. The selftest/fixture/frozen outputs below are the
  expected first-run results, not observed ones. The committed digests were
  computed by `sha256sum` on the written bytes.

## Final L1 commands

```
python3 -B tools/souji-evidence-cache.py --selftest
# expect exit 0, final `selftest: 48/48 passed`

python3 -B tests/fixtures/r14-evidence-cache.py
# expect exit 0, final `fixture: 22/22 checks passed`

python3 -B tools/souji-evidence-cache.py --frozen tests/fixtures/r14-cache-frozen
# expect exit 0; `souji-evidence-cache: reusable`, `frozen_files: 2`,
# `measured_commit: 0123456789abcdef0123456789abcdef01234567`,
# `root: '<abs path>'`, no findings

python3 -B tests/fixtures/r14-evidence-cache.py --tool /var/tmp/absent-cache-gate
# expect exit 2 and `fixture: tool missing: /var/tmp/absent-cache-gate`
```

## Risks / limits

- Verdict is point-in-time. The recorded `matched` is a claim; the gate never
  proves the command ran or ran at the declared revision.
- Digests must be captured at measurement time by the runner. Recomputed-at-
  retain-time digests launder; the gate cannot detect that (caller
  precondition in the docstring).
- Only declared dependencies are measured: no completeness, no transitivity,
  and out-of-root inputs (absolute toolchains/scripts, git/shellcheck, the
  interpreter) can never be declared. Runtime/toolchain versions are unmeasured.
- Root and record paths are resolved by the boundary walk and then opened by a
  second per-component `O_NOFOLLOW` walk; a component swapped to a symlink
  fails closed, but a rename/mount swapping in a different real directory
  between the two walks is not detected (no post-open dev/ino recheck for
  root/record, unlike dependencies).
- Digest reads are size-bounded (1 GiB per dependency) but not time-bounded.
  `O_NONBLOCK` does not bound a regular file on a stalled FUSE/NFS mount; run
  the gate under an outer timeout.
- Protected matching is name-based and conservative for dependency keys and
  absolute basenames; a root such as `/var/tmp/token-audit` is refused
  `root-protected`, and an innocuous `*token*`/`*secret*`-shaped name can be
  refused. A store relocated by a symlink outside the lexical HOME/passwd
  tree is not discovered. This is not a DLP classifier.
- No vendor timeout behavior is involved, so S038 was not applicable, and
  S039 was not used (L1 has not run).
