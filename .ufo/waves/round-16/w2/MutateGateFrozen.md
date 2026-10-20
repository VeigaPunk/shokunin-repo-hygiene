# W2 mutation probe — LG-FROZEN-PIN / LG-FROZEN-MEASURED
STATUS: PARTIAL — seven of twelve single mutants survived both authorized detectors; this is a calibration/coverage finding, not a demonstrated defect in the pristine gate.
## Scope and axes
Axes: frozen-pin detection sensitivity; negative-control calibration; exact-byte restoration and scratch isolation. The assigned probe covers root-prefix routing, record_sha256, and measured_commit blob checks only. No delegation, commits, lane-source edits, census execution, tool installs, or alternate runtime invocation occurred.
Target: `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py`. External detector: `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py`. Mutants were isolated as `/var/tmp/souji-r16-MutateGateFrozen/m1.py` through `m12.py`. Each copy was tested pristine, after exactly one mutation, and after exact-byte restoration, using both authorized commands in each phase: 72 invocations total. Six detector jobs ran concurrently per phase. Pristine/restored outputs passed for every copy; no baseline failure was counted as a kill.
## Verdict
**Coverage verdict: partial.** Combined detector result: **5 killed, 7 survived, 0 inconclusive**. The selftest killed 4/12 (m1, m6, m7, m8); the external fixture killed 4/12 (m1, m7, m8, m10). m6 survives the external fixture, whereas m10 survives the selftest, showing useful but incomplete complementarity. Negative controls correctly kill m1/m7 via false positives; kills are not all false-negative detections. No production correctness verdict beyond the exercised detector behavior is claimed.
Every pristine and restored selftest exited 0 with `SELFTEST\tpass=18\tfail=0`; every pristine and restored fixture exited 0 with `SUMMARY\ttotal=15\tfailed=0`. All 72 stderr streams were empty. Pristine stdout was byte-identical across the twelve copies for each detector, and every restored stdout exactly matched its corresponding pristine stdout. Full common pristine output and every mutant output are retained below; restored output is identical, not merely a matching summary.
## Single-mutant results
| Copy | Gate line | Single defect | Selftest (exit; pass/fail) | Fixture (exit; failed/15) | Verdict / killing case |
|---|---:|---|---|---|---|
| m1 | 90 | Omit tools/ from root prefixes | 1; SELFTEST; pass=13; fail=5 | 1; SUMMARY; total=15; failed=3 | killed — selftest clean-pass; fixture pin-only-inside-frozen-dir / clean-all-green |
| m2 | 90 | Omit tests/ from root prefixes | 0; SELFTEST; pass=18; fail=0 | 0; SUMMARY; total=15; failed=0 | survived — proposed case S1 |
| m3 | 90 | Omit census/ from root prefixes | 0; SELFTEST; pass=18; fail=0 | 0; SUMMARY; total=15; failed=0 | survived — proposed case S1 |
| m4 | 90 | Omit corpus/ from root prefixes | 0; SELFTEST; pass=18; fail=0 | 0; SUMMARY; total=15; failed=0 | survived — proposed case S1 |
| m5 | 366 | Drop slash boundary from every root prefix comparison | 0; SELFTEST; pass=18; fail=0 | 0; SUMMARY; total=15; failed=0 | survived — proposed case S2 |
| m6 | 425 | Misspell record_sha256 guard as record_sha, omitting record hash validation | 1; SELFTEST; pass=17; fail=1 | 0; SUMMARY; total=15; failed=0 | killed — selftest record-sha256-mismatch; external detector survives |
| m7 | 448 | Invert record hash inequality | 1; SELFTEST; pass=12; fail=6 | 1; SUMMARY; total=15; failed=1 | killed — selftest clean-pass / record-sha256-mismatch; fixture clean-all-green |
| m8 | 481 | Read measured blobs from landing rev instead of measured_commit | 1; SELFTEST; pass=17; fail=1 | 1; SUMMARY; total=15; failed=1 | killed — selftest frozen-measured; fixture pin-vs-measured-commit |
| m9 | 482 | Skip absent measured_commit blobs rather than reporting them | 0; SELFTEST; pass=18; fail=0 | 0; SUMMARY; total=15; failed=0 | survived — proposed case S3 |
| m10 | 491 | Delete measured digest mismatch detection by replacing its condition with False | 0; SELFTEST; pass=18; fail=0 | 1; SUMMARY; total=15; failed=1 | killed — fixture pin-vs-measured-commit; selftest survives |
| m11 | 425 | Enter record hash validation only if record path exists, silently dropping absence | 0; SELFTEST; pass=18; fail=0 | 0; SUMMARY; total=15; failed=0 | survived — proposed case S4 |
| m12 | 394 | Always resolve record key under frozen directory, bypassing root-prefix rule for record | 0; SELFTEST; pass=18; fail=0 | 0; SUMMARY; total=15; failed=0 | survived — proposed case S5 |

Line numbers above reference the pristine gate, not line-shifted mutant copies. m10 is a standard condition-deletion mutant (`elif False:`), not an assertion that a developer would intentionally write that literal. m9 replaces only the missing-blob reporting branch with `continue`; all other mutants replace one line.
## Expected detectors, recorded before running the mutants
- **m1**: Kill: selftest clean-pass and fixture clean-all-green; root tools pins become frozen-local.
- **m2**: Possible survivor: synthetic pins do not include a tests/-rooted key; require an explicit root/local collision case.
- **m3**: Possible survivor: synthetic pins do not include a census/-rooted key; require an explicit root/local collision case.
- **m4**: Possible survivor: synthetic pins do not include a corpus/-rooted key; require an explicit root/local collision case.
- **m5**: Possible survivor: require toolshed.txt (and analogous non-prefix names) local/root collision.
- **m6**: Kill: selftest record-sha256-mismatch; fixture has no isolated record hash mismatch.
- **m7**: Kill: selftest clean-pass plus record-sha256-mismatch; fixture clean-all-green catches false positives.
- **m8**: Kill: selftest frozen-measured and fixture pin-vs-measured-commit.
- **m9**: Possible survivor: selftest frozen-measured has a second mismatched file masking absence; fixture pin-only-inside-frozen-dir asserts PIN only.
- **m10**: Kill: fixture pin-vs-measured-commit; selftest frozen-measured may survive because its missing file still raises the same ID.
- **m11**: Possible survivor: require a record_sha256 with an absent or unset record key and otherwise matching pins.
- **m12**: Possible survivor: all fixture record keys are record.json; require a root-prefixed record key.

## Surviving counterexamples and smallest fixes
These are counterexamples to detector mutation resistance: the observed mutated programs pass both suites despite removing the named behavior. Proposed new fixture inputs below are **[INFERENCE]** from the inspected branch and test code; they were not separately executed because this assignment permits only the existing selftest and external fixture. No contract changes or lane-source fixes are proposed.
### S1 — missing root-prefix dimensions (m2, m3, m4): coverage fails
`tools/souji-landing-gate.py:90` can lose `tests/`, `census/`, or `corpus/` independently and still get 18/18 plus 15/15. The selftest pin map at `tools/souji-landing-gate.py:718-721` has only one root-prefixed key, `tools/good.sh`; the held-out prefix case at `tests/fixtures/r16-landing-gate.py:306-336` likewise targets only `tools/`.
**Smallest fix:** parameterize a passing root-pin case over all four ROOT_PREFIXES. For each of the three missing dimensions, create `<prefix>probe.txt` only at repository root, pin its digest, and require exit 0/no LG-FROZEN-PIN. A dropped-prefix mutant will instead look below the frozen directory and report a missing path. Pair it with a shadow-only negative control, requiring LG-FROZEN-PIN when only `<frozen>/<prefix>probe.txt` exists, to enforce the no-fallback rule for each prefix.
### S2 — slash-boundary widening (m5): coverage fails
At `tools/souji-landing-gate.py:366`, replacing `key.startswith(p)` with `key.startswith(p.rstrip("/"))` passes both suites. It changes valid frozen-local names such as `toolshed.txt` into root-addressed names.
**Smallest fix:** add a clean local key `toolshed.txt`, present only under the frozen directory, with a matching pin; require exit 0. The pristine rule treats it as local; m5 treats it as root and fails. Parameterize near-prefix names for tests/census/corpus as well, with conflicting root shadows if desired.
### S3 — missing measured blob skipped (m9): coverage fails
Removing the missing-blob finding at `tools/souji-landing-gate.py:482-490` passes both suites. The selftest at `tools/souji-landing-gate.py:857-881` combines a file absent at measured_commit with a second file whose bytes differ there, then asserts only presence of LG-FROZEN-MEASURED. The second finding masks removal of the first. Conversely, m10 removes the digest-mismatch branch at line 491 and the same selftest still passes because the absent file remains; the held-out `pin-vs-measured-commit` case kills m10, not m9. The external shadow case at `tests/fixtures/r16-landing-gate.py:333-336` requires only LG-FROZEN-PIN, not the independently applicable missing measured-blob row.
**Smallest fix:** split missing-at-measured and changed-at-measured into two independent cases, each pinning exactly one file and requiring the exact path plus LG-FROZEN-MEASURED. For the missing case, commit a clean base without the file, add the file in the landing commit, pin the new bytes, and point record.measured_commit at the base. All current-revision pins must match. Require exactly the missing-file measured finding (and no LG-FROZEN-PIN). Alternatively, assert both exact key-specific findings in the existing selftest, not merely the shared ID.
### S4 — absent/unset record silently skipped (m11): coverage fails
At `tools/souji-landing-gate.py:425`, adding `and record_repo in tree` to the record_sha256 guard suppresses the missing-record branch at lines 428-436 while both suites stay green. Existing record-hash negative coverage at `tools/souji-landing-gate.py:849-855` covers only an existing record with a wrong digest.
**Smallest fix:** a fixture with all files pins matching, record_sha256 present, `record: "record.json"`, and no such record blob; require LG-FROZEN-PIN with the missing-record detail. Include a separate unset-record-key case. These cases must not rely on unrelated file-pin errors.
### S5 — record routing bypasses root-prefix rule (m12): coverage fails
At `tools/souji-landing-gate.py:394`, always resolving record as `frozen_dir/record_key` passes both suites. The fixture uses only `record.json` at `tests/fixtures/r16-landing-gate.py:324,351,475`, so it does not exercise the documented root-prefix rule for `record` keys.
**Smallest fix:** use a root-prefixed record key such as `tools/record.json`, put the JSON record only at root, and set record_sha256 to its actual digest; all files pins must match and the pristine case must exit 0. Add a shadow-only negative control and a real measured_commit variant so path routing cannot bypass measured checks. Parameterizing the four prefixes tests the shared files/record contract rather than only the current implementation structure.
### Complementary detector gaps, not combined survivors
- **m6:** the external fixture reports 15/15 even when the record_sha256 guard is misspelled and all record-hash validation disappears. The selftest kills it with `record-sha256-mismatch`. The smallest held-out addition is one otherwise-clean fixture with a wrong record_sha256 (plus absent-record cases S4).
- **m10:** the selftest reports 18/18 with measured digest mismatches disabled. The external fixture kills it using the isolated `pin-vs-measured-commit` case. Split/strengthen the selftest per S3; do not infer its mismatch branch is tested merely because the shared finding ID appears.

## Byte provenance and restoration
- Pristine gate P0 SHA-256: `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2`.
- Gate source after all phases: `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2` (unchanged).
- External fixture before/after SHA-256: `aae67c9c7bafd86f1b745193ac4aead74b3a3403b5c5ade33991d246e6413f2f` / `aae67c9c7bafd86f1b745193ac4aead74b3a3403b5c5ade33991d246e6413f2f` (unchanged).
- Every before hash was P0. Restoration ran in a `finally` block immediately after mutant detectors. Every restored copy hashed exactly P0; both detectors were then rerun on every restored copy. The table records each distinct mutant hash.
| Copy | Before SHA-256 | Mutated SHA-256 | Restored SHA-256 | Restored selftest / fixture exit |
|---|---|---|---|---|
| m1 | P0 | `e800a58149e6f954a7a1f7989c28a85aaffdd2dc29e990378bbcf3096d066e18` | P0 | 0 / 0 |
| m2 | P0 | `d4abbff9fadba206ebaf784c1ef59c5fb3d51790d39aa520d817c5f951f47169` | P0 | 0 / 0 |
| m3 | P0 | `e6e2d8149d3d155d059b11cbbc90f31cefde2964f91bf6b41dbca36f1f7db453` | P0 | 0 / 0 |
| m4 | P0 | `ed85f3152991281f8047ac6dea3864e352aa0686b194dc7047973fb96e811255` | P0 | 0 / 0 |
| m5 | P0 | `b83ba2c26c76523bfde1580e51721f8dbd6d7dcebf5334bed9dd12d5a4617cfc` | P0 | 0 / 0 |
| m6 | P0 | `869d0f33ce9316472fb3892d42431caa7fecb1bfac34c487340554b7fe1ccbb8` | P0 | 0 / 0 |
| m7 | P0 | `f6197fd7a78836b0f9e8348c6c83a79045bbeca19743a06901e6dbe3f18bb034` | P0 | 0 / 0 |
| m8 | P0 | `b5f47569cf431ce385b9e6fbe692fa09c1ae1ee9c4db615135f53e4cbd97d134` | P0 | 0 / 0 |
| m9 | P0 | `0ed3655b3334603d264b895c60de7340b05f431fc906a9cce9a8d156f43216cc` | P0 | 0 / 0 |
| m10 | P0 | `b89827fe491e3abde71df248d682543dc1d0f9b8b2497d9179c7c3a1fc83ecf6` | P0 | 0 / 0 |
| m11 | P0 | `7bf2658487b1d4ab1657a28057088c472c291cfeb9c0e3c2afc51e00cfe4f160` | P0 | 0 / 0 |
| m12 | P0 | `b40c80e711bd3ef57c62b7f61673fca3d30480c76276c6af61901b871c74784c` | P0 | 0 / 0 |

Scratch directory `/var/tmp/souji-r16-MutateGateFrozen` was deleted after restoration and result capture; the observed post-delete existence check was `False`. No scratch copy remains. Original source and fixture were never edited. No tool was installed or upgraded.

## Actual detector output
Outputs below are captured stdout verbatim (tabs retained). Return codes are in the results table; every stderr was empty.
### Common pristine output (identical for m1–m12 and for every restored run)

**selftest, exit 0**

```text
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-CHANGED', 'LG-PARSE-REG'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	fenced-and-table-ignored	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2
CASE	pass	no-skill-exit2	exit=2
SELFTEST	pass=18	fail=0
```

**fixture, exit 0**

```text
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
```

### m1 — killed

**selftest, exit 1**

```text
CASE	FAIL	clean-pass	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-FROZEN-PIN', 'LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-CHANGED', 'LG-PARSE-REG'] err=None
CASE	FAIL	uncited-nonparsing-not-flagged	exit=1 findings=[{'id': 'LG-FROZEN-PIN', 'path': 'tests/fixtures/r9-frozen/expected.json', 'detail': 'files[tools/good.sh] resolves to absent path tests/fixtures/r9-frozen/tools/good.sh'}]
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED', 'LG-FROZEN-PIN'] err=None
CASE	pass	uncarried-marker	exit=1 ids=['LG-FROZEN-PIN', 'LG-SEAT-UNCARRIED'] err=None
CASE	FAIL	carried-open	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	FAIL	carried-resolved	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-FROZEN-PIN', 'LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	FAIL	fenced-and-table-ignored	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	bad-rev-exit2	exit=2
CASE	pass	no-skill-exit2	exit=2
SELFTEST	pass=13	fail=5
```

**fixture, exit 1**

```text
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	FAIL	exit=0 lg_rows=0 FAIL(exit=0 want 1 (stderr=); missing LG-FROZEN-PIN ~ tools/pinned.sh)
CASE	pin-vs-measured-commit	FAIL	exit=1 lg_rows=2 FAIL(unexpected LG-FROZEN-PIN ~ tools/meas.py)
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	FAIL	exit=1 lg_rows=2 FAIL(exit=1 want 0 (stderr=); missing SUMMARY ~ findings=0; unexpected LG-FROZEN-PIN ~ ; unexpected LG-FROZEN-MEASURED ~ )
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=3
```

### m2 — survived

**selftest, exit 0**

```text
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-CHANGED', 'LG-PARSE-REG'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	fenced-and-table-ignored	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2
CASE	pass	no-skill-exit2	exit=2
SELFTEST	pass=18	fail=0
```

**fixture, exit 0**

```text
CASE	replay-b410186	PASS	exit=1 lg_rows=8
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
```

### m3 — survived

**selftest, exit 0**

```text
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-CHANGED', 'LG-PARSE-REG'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	fenced-and-table-ignored	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2
CASE	pass	no-skill-exit2	exit=2
SELFTEST	pass=18	fail=0
```

**fixture, exit 0**

```text
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
```

### m4 — survived

**selftest, exit 0**

```text
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-CHANGED', 'LG-PARSE-REG'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	fenced-and-table-ignored	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2
CASE	pass	no-skill-exit2	exit=2
SELFTEST	pass=18	fail=0
```

**fixture, exit 0**

```text
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
```

### m5 — survived

**selftest, exit 0**

```text
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-CHANGED', 'LG-PARSE-REG'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	fenced-and-table-ignored	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2
CASE	pass	no-skill-exit2	exit=2
SELFTEST	pass=18	fail=0
```

**fixture, exit 0**

```text
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
```

### m6 — killed

**selftest, exit 1**

```text
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-CHANGED', 'LG-PARSE-REG'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	FAIL	record-sha256-mismatch	exit=0 ids=[] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	fenced-and-table-ignored	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2
CASE	pass	no-skill-exit2	exit=2
SELFTEST	pass=17	fail=1
```

**fixture, exit 0**

```text
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
```

### m7 — killed

**selftest, exit 1**

```text
CASE	FAIL	clean-pass	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-FROZEN-PIN', 'LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-CHANGED', 'LG-PARSE-REG'] err=None
CASE	FAIL	uncited-nonparsing-not-flagged	exit=1 findings=[{'id': 'LG-FROZEN-PIN', 'path': 'tests/fixtures/r9-frozen/expected.json', 'detail': 'record_sha256 pinned 15cd24399730fb35 but record hashes 15cd24399730fb35'}]
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	FAIL	record-sha256-mismatch	exit=0 ids=[] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED', 'LG-FROZEN-PIN'] err=None
CASE	pass	uncarried-marker	exit=1 ids=['LG-FROZEN-PIN', 'LG-SEAT-UNCARRIED'] err=None
CASE	FAIL	carried-open	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	FAIL	carried-resolved	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-FROZEN-PIN', 'LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	FAIL	fenced-and-table-ignored	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	bad-rev-exit2	exit=2
CASE	pass	no-skill-exit2	exit=2
SELFTEST	pass=12	fail=6
```

**fixture, exit 1**

```text
CASE	replay-b410186	PASS	exit=1 lg_rows=6
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=3
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=2
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	FAIL	exit=1 lg_rows=1 FAIL(exit=1 want 0 (stderr=); missing SUMMARY ~ findings=0; unexpected LG-FROZEN-PIN ~ )
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=1
```

### m8 — killed

**selftest, exit 1**

```text
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-CHANGED', 'LG-PARSE-REG'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	FAIL	frozen-measured	exit=0 ids=[] err=None
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	fenced-and-table-ignored	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2
CASE	pass	no-skill-exit2	exit=2
SELFTEST	pass=17	fail=1
```

**fixture, exit 1**

```text
CASE	replay-b410186	PASS	exit=1 lg_rows=4
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	FAIL	exit=0 lg_rows=0 FAIL(exit=0 want 1 (stderr=); missing LG-FROZEN-MEASURED ~ tools/meas.py)
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=1
```

### m9 — survived

**selftest, exit 0**

```text
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-CHANGED', 'LG-PARSE-REG'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	fenced-and-table-ignored	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2
CASE	pass	no-skill-exit2	exit=2
SELFTEST	pass=18	fail=0
```

**fixture, exit 0**

```text
CASE	replay-b410186	PASS	exit=1 lg_rows=4
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=1
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
```

### m10 — killed

**selftest, exit 0**

```text
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-CHANGED', 'LG-PARSE-REG'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	fenced-and-table-ignored	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2
CASE	pass	no-skill-exit2	exit=2
SELFTEST	pass=18	fail=0
```

**fixture, exit 1**

```text
CASE	replay-b410186	PASS	exit=1 lg_rows=4
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	FAIL	exit=0 lg_rows=0 FAIL(exit=0 want 1 (stderr=); missing LG-FROZEN-MEASURED ~ tools/meas.py)
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=1
```

### m11 — survived

**selftest, exit 0**

```text
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-CHANGED', 'LG-PARSE-REG'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	fenced-and-table-ignored	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2
CASE	pass	no-skill-exit2	exit=2
SELFTEST	pass=18	fail=0
```

**fixture, exit 0**

```text
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
```

### m12 — survived

**selftest, exit 0**

```text
CASE	pass	clean-pass	exit=0 ids=[] err=None
CASE	pass	nonparsing-cited-sh	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-REG'] err=None
CASE	pass	nonparsing-cited-py	exit=1 ids=['LG-PARSE-REG'] err=None
CASE	pass	missing-cited-path	exit=1 ids=['LG-MISSING-REG'] err=None
CASE	pass	changed-nonparsing-with-base	exit=1 ids=['LG-FROZEN-PIN', 'LG-PARSE-CHANGED', 'LG-PARSE-REG'] err=None
CASE	pass	uncited-nonparsing-not-flagged	exit=0
CASE	pass	pin-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	pin-missing-file	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	record-sha256-mismatch	exit=1 ids=['LG-FROZEN-PIN'] err=None
CASE	pass	frozen-measured	exit=1 ids=['LG-FROZEN-MEASURED'] err=None
CASE	pass	uncarried-marker	exit=1 ids=['LG-SEAT-UNCARRIED'] err=None
CASE	pass	carried-open	exit=0 ids=[] err=None
CASE	pass	carried-resolved	exit=0 ids=[] err=None
CASE	pass	open-admitted	exit=1 ids=['LG-OPEN-ADMITTED'] err=None
CASE	pass	no-wave-dir-exit2	exit=2 ids=[] err=no .md reports under .ufo/waves/round-16/ at e302f4c1547a1ea33ede290135f4d39303f51e13
CASE	pass	fenced-and-table-ignored	exit=0 ids=[] err=None
CASE	pass	bad-rev-exit2	exit=2
CASE	pass	no-skill-exit2	exit=2
SELFTEST	pass=18	fail=0
```

**fixture, exit 0**

```text
CASE	replay-b410186	PASS	exit=1 lg_rows=5
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=4
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
```

## Commands
No shell was invoked directly. The following exact argv-equivalent commands were launched with Python subprocess.run (shell=False). Each phase lists every invocation verbatim; jobs within a phase ran concurrently. PYTHONDONTWRITEBYTECODE=1 was supplied to avoid incidental bytecode files. Copying, hashing, mutation metadata capture, byte-for-byte restoration, and cleanup used the eval Python standard library; surgical mutations used the edit tool.
L1 explicitly authorized the unmodified detectors' own auto-cleaned `/var/tmp/souji-landing-gate-*` (including selftest/snapshot) and `/var/tmp/souji-r16-lgfixture-*` directories outside the seat root; no containment shim was used. Those directories are created/removed by the authorized detector code itself (`run_selftest`/snapshot cleanup and fixture finally block). Only the assigned seat root was explicitly deleted by this probe. No independent real-lane gate run, census run, git command, shellcheck, compile check, or extra behavioral detector was invoked.

### pristine

```sh
python3 /var/tmp/souji-r16-MutateGateFrozen/m3.py --selftest
python3 /var/tmp/souji-r16-MutateGateFrozen/m1.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m1.py
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m3.py
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m2.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m2.py --selftest
python3 /var/tmp/souji-r16-MutateGateFrozen/m4.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m4.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m5.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m5.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m6.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m6.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m7.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m7.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m8.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m8.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m9.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m9.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m10.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m10.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m11.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m11.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m12.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m12.py
```

### mutated

```sh
python3 /var/tmp/souji-r16-MutateGateFrozen/m1.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m1.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m2.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m2.py
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m3.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m3.py --selftest
python3 /var/tmp/souji-r16-MutateGateFrozen/m4.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m4.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m5.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m5.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m6.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m6.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m7.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m7.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m8.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m8.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m9.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m9.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m10.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m10.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m11.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m11.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m12.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m12.py
```

### restored

```sh
python3 /var/tmp/souji-r16-MutateGateFrozen/m1.py --selftest
python3 /var/tmp/souji-r16-MutateGateFrozen/m2.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m1.py
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m2.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m3.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m3.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m4.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m4.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m5.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m5.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m6.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m6.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m7.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m7.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m8.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m8.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m9.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m9.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m10.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m10.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m11.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m11.py
python3 /var/tmp/souji-r16-MutateGateFrozen/m12.py --selftest
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r16-MutateGateFrozen/m12.py
```
