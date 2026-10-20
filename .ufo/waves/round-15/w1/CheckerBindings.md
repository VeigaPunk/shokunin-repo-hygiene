# Round 15 w1 — CheckerBindings (C2 digest/commit bindings, path containment)

Status: **design-only.** `tools/souji-preservation-evidence.py` and `tests/fixtures/r15-preservation-evidence.py` do not exist in the lane at review time (`git status`: only `?? .ufo/waves/round-15/`, `?? census/round-15/`, `?? census/operator-sweep-20261019/`). Findings below are grounded in (a) the round-13/14 cert-gate pattern the new checker is expected to inherit and (b) read-only committed-byte measurements. No tests, probes, edits, or installs were run. Tool installs/updates: none.

## Measured state (source inspection only)

| Item | Observed | Basis |
|---|---|---|
| HEAD | `cc2168325768d5356a82c039dcdf787377c55784` | `git rev-parse HEAD` |
| `tools/`, `tests/`, `census/` worktree vs HEAD | no diff | `git diff --stat HEAD -- tools tests census` empty |
| `cc21683:tools/souji-census.sh` sha256 | `fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9` | `git show <rev>:path \| sha256sum` |
| `a31642d:tools/souji-census.sh` (r14 baseline) | `6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026` | same; matches `tests/fixtures/r14-census-boundary.py:61` |
| `48f8945:tools/souji-census.sh` | `fd234148f0c44bcd1edc6857388e08354eba0bc98a59b78e480adf5ab2c3028c` | same (intermediate) |
| `tools/souji-cert-evidence.py` worktree = HEAD blob | `943d664c5df4e795c23821892a1691847772e95ef36752d532f5cbeff0e544d4` (tracked, mode 100755) | `sha256sum` vs `git show HEAD:…` |
| `tools/souji-census.sh` nlink / regular | 1 / regular | `stat -c '%h %s %n'` |
| Tracked symlinks under `tools/`, `tests/`, `census/` | only `tests/vault/**` fixture symlinks (mode 120000) | `git ls-files -s` |

Consequence for C2: round-15's paired "baseline" is the round-14 changed tool, digest `fcff8b05…` at `cc21683` (claims.json `baseline`). That baseline binding is verifiable today from committed bytes. The **changed** binding does not exist yet: `tools/souji-census.sh` will be edited by `ConfigRepair`, so its digest is unknown until that lands.

## Findings (severity order)

**F1 — high, calibration: installed-digest check is self-referential in the pattern being inherited.**
- `tools/souji-cert-evidence.py:450-495` (`_check_claim`) resolves the artifact path *from the record* and hashes whatever file is there; `:676-688` compares it with the record's own `sha256`. The only identity guard is a basename denylist, `cand-` prefix at `:668`. Any non-`cand-` file with its own digest passes. This is the round-13 CX2 replay (`AttackCalibration.md:49-52`) and is the shape the round-15 checker must not reproduce.
- Required: the checker holds a literal table `{path: sha256}` (BASELINE `tools/souji-census.sh` = `fcff8b05…` at `cc21683`; CHANGED = pinned after `ConfigRepair` lands) and compares measured bytes to the **constant**, never to a record field. Any path/digest not in the table → exit 2.
- Negative control (single mutation): one-byte edit to a copy of the tool with the record's declared sha updated to match → exit 2 (pin mismatch), not 1 and not 0.

**F2 — high, calibration: fixture and frozen pins are not anchored.**
- `_frozen_findings` (`cert:789-893`) reads `expected.json` through `_read_text_abs` with no digest pin of its own; the file digests it checks come from that same unpinned file. A tamperer who edits a fixture and rewrites `expected.json` passes.
- Existing good pattern to copy: `tests/fixtures/r14-census-boundary.py:61` (`BASELINE_SHA` literal) and `:702-703` (measure `TOOL.read_bytes()` then compare to the literal).
- Required: fixture identity is a checker-side literal (`tests/fixtures/r15-census-config.py` digest), not read from the record or from a manifest in the same directory.
- Negative control: edit the fixture and update the fixture's own recorded digest → exit 2.

**F3 — high, calibration: commit binding is recorded, not verified.**
- Round-14 `census/round-14/verification.json:3` carries `measured_commit` (top-level `measured_commit_scope` key, same file, states "lane HEAD is recorded as harness_revision only"). Nothing checks that the field names the bytes measured. The r14 closure rejected this class of value-blind evidence (`corpus/lessons/round-14-verifier-spotcheck.md:116-117`).
- Required when a record names `measured_commit`:
  - validate `^[0-9a-f]{40}\Z` (fullmatch) before use, so an option-like value cannot reach git;
  - validate the path through `_classify_rel` before concatenation into `<commit>:<path>`;
  - run `git -C <root> cat-file blob <commit>:<path>` as an argv list (no shell), with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_NO_REPLACE_OBJECTS=1`, a timeout, and hash the raw bytes;
  - require committed sha == on-disk sha == literal pin; any absence or mismatch → exit 2.
  - This is fixed plumbing on the checker side, not execution of recorded commands. If the round-15 design forbids any subprocess, the commit check must move to L1 and the checker must refuse records lacking a commit field (exit 2), not treat absence as a pass.
- Chicken-and-egg to state explicitly: the CHANGED blob exists only in the commit that carries `ConfigRepair`'s edit. CHANGED evidence therefore has to be committed in a later commit than the tool blob it measures, or be labelled as an uncommitted working-tree digest (never as commit-bound).

**F4 — medium, containment: parent-directory swap is not closed; final-file identity is not compared.**
- `_resolve_under` (`cert:273-300`) lstat-walks every component (good). `_digest_regular` (`:350-375`) opens the final component with `O_NOFOLLOW|O_NONBLOCK` and fstat's S_ISREG, but never compares `(st_dev, st_ino)` against the earlier lstat. The module docstring concedes the parent-swap race (`cert:145-147`).
- Impact here is bounded: the digest must still equal the literal pin, so a swap only helps if the attacker supplies bytes with the pinned digest. Severity low-medium for this lane.
- Recommended hardening (stdlib, cheap): walk from a root dirfd with `os.open(part, O_DIRECTORY|O_NOFOLLOW, dir_fd=parent)` per component, then `os.open(final, O_RDONLY|O_NOFOLLOW, dir_fd=parent)`, and require fstat `(st_dev, st_ino)` to equal the lstat identity. Operability cost is small; keep it if it does not break the repo's Python 3 baseline.

**F5 — medium, containment: record and manifest paths are caller-trusted, not contained.**
- `evaluate` reads the manifest with `_read_text_abs(manifest_path)` (`cert:514`) and `main` passes `Path(args.manifest)`, which is relative to CWD (`cert:1519`). Only the final component is checked; parents are followed.
- For round-15: the `--record FILE` path is caller input and should be documented as trusted. Everything *inside* the record (artifact, fixture, evidence, commit path) must go through `_classify_rel` + `_resolve_under`. `--root` must be `realpath`'d and checked `is_dir()` as in `cert:1510-1517`.
- Acceptance: absolute, `..`, control-character, and symlinked-component paths inside the record each → exit 2 with a distinct finding id.

**F6 — medium, calibration: JSON type and NaN holes in the pattern.**
- `_load_json` (`cert:393-394`) uses only `object_pairs_hook`; there is no `parse_constant`, so `NaN`/`Infinity` parse (round-13 CX7, `AttackCalibration.md:74-85`).
- Required: `parse_constant` raises; `exit_code` checked with `type(x) is int` (not `isinstance`, which admits `bool`); digests fullmatch `[0-9a-f]{64}`; duplicate keys rejected (already present at `cert:384-390`).
- Negative controls: `NaN` literal → 2; `"exit_code": true` → 2; duplicate `"verdict"` key → 2.

**F7 — medium, calibration: paired red/green must bind to digests, not labels.**
- Requirement from the dispatch: baseline run must be red on the benign-control IDs *and* produced by the pinned baseline digest; changed run green on the same IDs *and* produced by the pinned changed digest; namespace controls 12/12.
- Binding rule: each run record carries the digest it measured; the checker compares it to the literal for that role. A run with the wrong role digest, a missing run, or a case-ID set that is not exactly the pinned set → exit 2.
- Negative controls: swap baseline/changed record labels → 2; drop one benign case from a record → 2; green-only record (no baseline red) → 1 or 2 per the spec's taxonomy, but never 0.

**F8 — low, calibration: the checker's own provenance is not measured.**
- Literal pins live in `tools/souji-preservation-evidence.py`. A commit that edits both the pin and the record would pass. This is a stated limitation, not fixable inside the checker. Emit the measured digests and the scope line `NOT_CERTIFICATION` (as `cert:955-958` does) so L1 can compare them to the committed blob.

**F9 — process, operability: pin staleness.**
- Any `ConfigRepair` edit after the CHANGED pin is set invalidates the pin (round-13 CX6 pattern, `AttackCalibration.md:70-72`). L1 must run the checker last, after every tool write and immediately before the commit point, and record the printed digests.

## Acceptance needed (design-only, for AdmissionChecker to satisfy)

1. Literal pin table in checker: `tools/souji-census.sh` BASELINE `fcff8b05…`; CHANGED literal set after `ConfigRepair`; fixture literal for `tests/fixtures/r15-census-config.py`. Any other path or digest → 2.
2. Record schema: `measured_commit` (40-hex), artifact path, declared sha256, fixture path+sha256, baseline/changed role, exact case-ID list. Missing field → 2.
3. Commit binding via `git cat-file blob` as above, or explicit refusal when absent; CHANGED evidence committed after its tool blob, or labelled uncommitted.
4. Containment: `_classify_rel` + `_resolve_under` + `st_nlink == 1` + regular + `O_NOFOLLOW`; preferably a dirfd walk with `(st_dev, st_ino)` identity compare (F4).
5. JSON: `object_pairs_hook` dup-reject, `parse_constant` reject, `type(x) is int`, fullmatch digests (F6).
6. Negative controls, each a single mutation from a clean fixture, asserting the exact finding-id set and rc: tool edited with its own digest; fixture edited with its own pin; absolute path; `..` path; symlinked `tools/`; hardlinked tool; missing/invalid `measured_commit`; `NaN`; duplicate key; swapped baseline/changed labels; dropped case ID; green-only record.
7. Positive control: committed pinned tool + committed evidence + red baseline + green changed → rc 0 with scope `NOT_CERTIFICATION`.
8. Selftest temp trees under `tempfile.mkdtemp(dir="/var/tmp")` with `finally` cleanup (cert pattern, `cert:132-136`).

## Unrun checks (for L1, after all seats land)

- `python3 tools/souji-preservation-evidence.py --selftest` → exit 0, exact finding ids for each negative control.
- Hash `tools/souji-census.sh` on disk and `git show HEAD:tools/souji-census.sh | sha256sum`; both must equal the CHANGED literal at the commit point.
- Confirm `git cat-file blob cc21683:tools/souji-census.sh` hash equals BASELINE `fcff8b05…`.
- Re-run the checker after the final commit; record printed digests.

## Limits

- The checker does not exist yet; every finding about its behaviour is design-level or inherited from `tools/souji-cert-evidence.py`.
- Committed-byte digests above were read with read-only `git show`/`sha256sum`; nothing was executed from the lane.
- **Query-boundary disclosure (no-query rule, per SoujiR15 IRC).** Two early calls violated the boundary and are not repeated: (1) a `glob` over the whole lane root with `gitignore: false`, which listed entry names under `census/operator-sweep-20261019/` (e.g. `.hold.json`, `stage-hold-delete.sh`, `results/*.tsv`); (2) a `grep` over the whole lane root with `gitignore: false` for `checker|digest|binding|symlink|traversal`. That grep's output was truncated, so I cannot confirm whether it matched inside the operator-sweep directory; I did not open or read any operator-sweep file by name. Every later query was limited to `tools/`, `tests/`, `census/round-14`, `census/round-15`, `.ufo/waves/round-15`, and specific known files, plus read-only `git` plumbing on tracked paths.
