# r13 w1 — EvidenceGate (C1 executable evidence gate)

Seat: `SoujiR13.EvidenceGate` (executor, leaf). Scope: C1 only. No delegation,
no commits, no gate/selftest execution in-wave. Certification remains OFF; this
artifact validates declared-fragment consistency and integrity, never tool safety.

## Files delivered

| path (relative to lane root) | role |
|---|---|
| `tools/souji-cert-evidence.py` | stdlib CLI gate; 1526 lines; header carries CLI/schema/finding/exit docs |
| `tests/fixtures/r13-cert-evidence.py` | external black-box replay harness; 196 lines |
| `tests/fixtures/r13-cert-frozen/expected.json` | frozen snapshot pins + expected verdict `clean` |
| `tests/fixtures/r13-cert-frozen/manifest.json` | explicit two-fragment manifest |
| `tests/fixtures/r13-cert-frozen/fragments/alpha.json` | fragment (author/class/artifact/sha256/command/exit_code/verdict/evidence/evidence_sha256) |
| `tests/fixtures/r13-cert-frozen/fragments/beta.json` | second fragment, distinct author/artifact/evidence |
| `tests/fixtures/r13-cert-frozen/installed/fixture-alpha.sh` | synthetic artifact (not an installed lane tool) |
| `tests/fixtures/r13-cert-frozen/installed/fixture-beta.sh` | synthetic artifact |
| `tests/fixtures/r13-cert-frozen/evidence/alpha.txt` | evidence for alpha |
| `tests/fixtures/r13-cert-frozen/evidence/beta.txt` | evidence for beta |

Authored-byte digests (read-only `sha256sum`, observed 2026-10-20):
`tools/souji-cert-evidence.py` = `a029aaa0a604fb53dfcba650f95b3626d543890bd1d96110d2340cd30144ece1`;
`tests/fixtures/r13-cert-evidence.py` = `3a3535da8b46ccc177b459609b6dfcca4e46362d1fe0c56dd727ecbe70891b7c`.

## Contract as implemented

CLI (header lines 11–31; parser at `main` 1485):
`--root PATH --manifest PATH` | `--frozen DIR` | `--selftest`.
Exit constants at lines 171–173 and are stable:

- `0 clean` — all fragments schema-valid, artifacts digest-match, evidence
  present and digest-match, all verdicts `pass` with `exit_code == 0`.
- `1 failed` — well-formed evidence with at least one honest reported failure
  (`verdict=fail`, nonzero `exit_code`); finding `fragment-reported-fail`
  (line 734). This is a certification failure, not a malformed input.
- `2 could-not-evaluate` — malformed/duplicate/shared/unsafe/absent/mismatched/
  inconsistent evidence, tampered frozen snapshot, or argparse usage error.
  Nothing is certified.

Manifest schema (docs lines 33–42): `{"fragments": [rel, ...]}`, non-empty,
each entry a unique safe relative path under `--root`; unknown top-level keys
tolerated; duplicate JSON object keys rejected.

Fragment schema (docs lines 44–68; validation 414–442): all nine keys required —
`author`, `class`, `artifact`, `sha256`, `command`, `exit_code`, `verdict`,
`evidence`, `evidence_sha256`. `author`/`class` are non-empty trimmed labels;
`sha256`/`evidence_sha256` are exactly 64 lowercase hex; `exit_code` is an
integer (bool and strings rejected); `verdict` is `pass|fail`. `author` labels
must be unique; `class` labels are not unique and are not coverage proof.
`artifact` and `evidence` must differ. No identity or execution provenance is
claimed or inferable from labels.

Finding ids are documented at lines 73–88 and emitted as
`finding <id>: <detail>`; level-2 ids force exit 2, the sole level-1 id is
`fragment-reported-fail`. Key implementation anchors:

- path normalization/containment, control chars rejected: `_classify_rel` 248
  (ord <0x20 / 0x7f at 254), `_resolve_under` 273 (per-component lstat, no
  symlink components);
- protected names/operator trees: `_protected_reason` 214 (`.env`, `.env.*`,
  `*.env`, `.envrc`, `*credential*`, `*secret*`, `id_*`, `*.pem`, `*.key`,
  `watchdog.log`, `census/operator-sweep-*`, `.ufo/state`);
- claim resolution/hardlink: `_check_claim` 450, `path-protected` 462–464,
  `path-hardlink` 490 (`st_nlink == 1` required);
- manifest empty: 534–536; duplicate author: 633; duplicate artifact/evidence
  path: 655–658;
- candidate rejection: `artifact-candidate` 671 (basename starts `cand-`);
- artifact digest: 676–688 (`declared=`/`measured=`); evidence digest: 697–705;
- verdict consistency: `verdict-false-pass` 716–720, `verdict-false-fail`
  723–727;
- frozen: `_frozen_required_inputs` 748, `_frozen_findings` 789,
  `snapshot_tampered` 872/880/887, coverage `frozen-incomplete` 931,
  verdict compare `snapshot-verdict-mismatch` 945, `evaluate_frozen` 896;
- output scope line: `_emit` 955, exact text at 958:
  `scope: evidence_valid/NOT_CERTIFICATION (...)`.

`--frozen DIR` verifies every `expected.json` file pin (absent/symlink/
non-regular/hardlink/unreadable/mismatch → `snapshot_tampered`, exit 2) before
normal evaluation, requires every reachable input (manifest, fragments,
artifacts, evidence) to be pinned (`frozen-incomplete`), then runs the normal
manifest evaluation and compares the result with `"verdict"`. `expected.json`
is the caller-supplied trust anchor and is not self-authenticated.

## Frozen snapshot pins (observed, recomputed read-only)

| path | sha256 |
|---|---|
| `manifest.json` | `58f199c1d59d1325e7305b1e245a82add843e2d717259b8732284dc7a9241301` |
| `fragments/alpha.json` | `c78445a709b23c4f57908978ef14ddd0914efee45a002b9f5dc078f02e160392` |
| `fragments/beta.json` | `606d4f9e27bdbb9010bda32d10d698e5b1d5a762cb3232fdd0ee1e5e32a85c36` |
| `installed/fixture-alpha.sh` | `3b41e8f9da09b74e6ecb941a9023cb5af4e42116b2cbc185ec446391aab32234` |
| `installed/fixture-beta.sh` | `26beb4ca14652a852f50000da24068eb2fc53c397d2d7f689c785be7ebe17a34` |
| `evidence/alpha.txt` | `902fd6238158b8aec7978e0932143ec34b6d857f234d88fbcfcff5579aed0e87` |
| `evidence/beta.txt` | `48dce861f7e8fd426f20f2df5f594b7382e9ecaa99ccf5e9598eaea151f96379` |

A read-only Python recomputation (not the gate) confirmed all seven pins and
that the required-input set equals the pinned set exactly.

## Selftest

`--selftest` (1149) builds fixtures with
`tempfile.mkdtemp(prefix="souji-r13-cert-selftest.", dir="/var/tmp")` (1156),
invokes this CLI as a subprocess per case, asserts the exact finding-id set and
return code (`_record` 1030), copies the committed frozen snapshot for the
mutation case, and removes the tree in `finally` (shutil.rmtree). There is no
shell trap and no `/tmp` fallback; passing `dir="/var/tmp"` means an inherited
`TMPDIR` cannot move the base.

Battery: 36 cases (31 `case`, 4 `frozen_case`, 1 direct `_record` for
root-not-directory). Negative fixtures each apply one defect to a clean shape
and assert an exact id set:

clean; digest-mismatch; duplicate-fragment; duplicate-author; shared-artifact;
shared-evidence; claim-shared; missing-evidence; missing-artifact; false-pass;
honest-fail (rc 1); false-fail; path-escape; path-absolute; path-symlink;
evidence-fifo; malformed-manifest; malformed-fragment; fragment-schema;
missing-class; evidence-digest-mismatch; hardlinked-artifact; control-char-path;
protected-path; protected-env-local; parent-symlink; candidate-artifact;
fragment-missing; manifest-empty; fragment-not-regular; manifest-missing;
root-not-directory; frozen-clean; frozen-tampered; frozen-incomplete;
frozen-verdict-mismatch.

Expected final line: `selftest: 36/36 passed` (format at 1479); exit 0 only
then, 1 on any assertion failure, 2 when the committed frozen fixture is absent.
`tests/fixtures/r13-cert-evidence.py` externally re-runs `--selftest`, a clean
manifest, a digest mismatch, and the frozen clean/tampered paths, printing
`fixture: 5/5 checks passed`.

## Historical replay contract for L1

Observed read-only facts (2026-10-20):

- `census/round-10/cert-16.json` lines 9–12 declare candidate census sha
  `60aef4c07aa75099ff577e8f544e33ceb4914b278c81b8e5f2785e3f582be7fc`; its
  `lane_tool_sha256` at line 20 repeats it, while its `installed_tool_sha256`
  at line 24 records `462dabd281e417c80266ba4d3ffd2cd8ebca0aa84147e1c45c9832ee638b52ca`.
  Lines 2618–2620 record `"certification_ready": true` / `"CERTIFIED"`.
- Current bytes: `tools/souji-census.sh` =
  `6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026`;
  `tools/cand-census-03.sh` =
  `60aef4c07aa75099ff577e8f544e33ceb4914b278c81b8e5f2785e3f582be7fc`;
  `census/round-10/cert-16.json` =
  `662294df4291c16fb0fe8c9a0b6dd58b72ada9476b45113fa7c44d383952c3c1`.

To replay the historical claim against the lane's declared installed path
(root = lane root), one fragment with exactly these keys:

```json
{
  "author": "<seat-or-integrator-label>",
  "class": "historical-relay-installed-digest",
  "artifact": "tools/souji-census.sh",
  "sha256": "60aef4c07aa75099ff577e8f544e33ceb4914b278c81b8e5f2785e3f582be7fc",
  "command": "census/round-10/cert-16.json (historical relay; not executed by the gate)",
  "exit_code": 0,
  "verdict": "pass",
  "evidence": "census/round-10/cert-16.json",
  "evidence_sha256": "662294df4291c16fb0fe8c9a0b6dd58b72ada9476b45113fa7c44d383952c3c1"
}
```

Manifest: `{"fragments": ["<relative fragment path>"]}`. Expected result:
exit 2, `finding artifact-digest-mismatch`, detail
`declared=60aef4… measured=6a000c…`. Declaring the relay's historical installed
`462dab…` instead yields the same id with `measured=6a000c…`. Use one distinct
evidence path per claim: two fragments sharing `cert-16.json` are rejected as
`fragment-shared`. Evidence is digest-pinned, so any later edit to cert-16.json
also yields `evidence-digest-mismatch`. The gate re-hashes the path it is given;
it cannot prove that path is the install location, so L1 should run with a
clean `tools/` status and name the intended file explicitly.

Candidate-substitution negative: a fragment with
`"artifact": "tools/cand-census-03.sh"` is rejected with `artifact-candidate`
(exit 2) even when its declared sha matches the candidate bytes; declaring the
current measured sha instead adds `artifact-digest-mismatch`. The denylist is
basename-only: a non-`cand-` candidate file (e.g. `tools/souji-census.impl-46.sh`,
the r11 wrong-selection candidate) would pass it if it is given its own digest,
so the path choice remains L1's explicit claim. No old relay was altered.

## Proposed final checks (not executed by this seat)

Run gate invocations under `timeout -k 5 300` (SafetyPaths SP-G7: JSON has a
size cap, artifact/evidence digests do not).

1. `python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-cert-evidence.py --selftest`
   → exit 0, final line `selftest: 36/36 passed`, each `case …: ok`.
2. `python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r13-cert-evidence.py`
   → exit 0, `fixture: 5/5 checks passed`.
3. `python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-cert-evidence.py --frozen /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r13-cert-frozen`
   → exit 0, `souji-cert-evidence: clean`, summary `frozen_files=7`.
4. Build the historical manifest/fragment from the template above under a temp
   lane-relative path, run with `--root /home/vgpnk/Projects/shokunin/souji-shokunin
   --manifest <manifest>` → exit 2 with `artifact-digest-mismatch`.
5. Negative candidate replay with `tools/cand-census-03.sh` → exit 2 with
   `artifact-candidate`.

## Risks, limits, blockers

- No gate or selftest execution occurred in-wave (contract). Statements about
  runtime behavior are derived by reading the authored code; the only executed
  code was read-only evidence work: AST parsing, JSON parsing, digest
  recomputation, and the two pure path helpers (`_protected_reason`,
  `_classify_rel`) extracted via AST. If L1 wants an executed proof, checks
  1–3 above provide it.
- The gate evaluates only declared fragments: a fragment silently omitted from
  the manifest cannot be detected. That is completeness, outside the parent's
  stated scope; `--frozen` makes a tampered manifest/input set evident but does
  not discover never-listed fragments.
- `author`/`class` are labels; unique real identity, sole authorship, and actual
  command execution are not established. No installed-tool allowlist and no
  proof that the declared artifact path is the installed location; the `cand-`
  basename denylist does not catch `.impl-*` or other non-cand candidates
  (AttackCalibration CX12). Root and manifest are caller-chosen. A clean result
  is explicitly `evidence_valid/NOT_CERTIFICATION`.
- The round claim text at `census/round-13/claims.json:5` still calls C1 an
  "Installed-byte evidence gate". That overclaims and is outside this seat's
  write set; L1 should reword it to a declared-artifact digest gate. The gate
  itself is consistent-only: no installed identity, no unlisted-fragment
  detection, and it does not alter the old `census/round-10/cert-16.json`
  relay; replaying that relay is expected to reject with
  `artifact-digest-mismatch`.
- Name-based `path-protected` is not a DLP classifier. Hardlinked files are
  refused (nlink > 1), so a legitimate hardlinked install cannot be measured.
  Frozen pin verification and the later manifest evaluation are separate reads;
  a writer between them is not excluded. The component/open race is closed only
  for the final component (O_NOFOLLOW + fstat); a parent-directory swap during
  hashing remains a documented TOCTOU. Nested mount points below `--root` are
  not detected (SP-G4: no `st_dev` equality check), and `--manifest` may live
  outside `--root` (SP-G6: caller-supplied anchor, protected-name policy only).
  Digest cost is unbounded (SP-G7); L1 should keep the timeout wrapper.
- Historical digests above are observed facts at this HEAD; if the measured tool
  bytes change, the expected `measured=` value changes (the finding id does not).
