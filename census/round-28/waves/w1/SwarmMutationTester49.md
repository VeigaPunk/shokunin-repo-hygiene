## Status
STATUS: PARTIAL — all four requested probes killed on an isolated synthetic round-26 receipt; lane round-26 receipt did not yet exist. Fixture baseline has an unrelated symlink-control failure.

## Evidence
- Revision context: frozen preregistration at lane base `3a2a80d0d18940a5e352ebc526da22a57dad83c4`.
- Existence check: `TOOL-EXISTS`, `R26WAVES-ABSENT`, `R27WAVES-ABSENT`, `FIXTURE-EXISTS`.
- Probe used `/var/tmp/souji-r28-SwarmMutationTester49/lane` (isolated; removed after probe) and delivered `tools/souji-wave-evidence-capture.sh` with `--verify`.
- Pristine output: `./a.txt: OK`, `./summary.tsv: OK`; tool `captured+verified` (rc 0).
- Manifest-byte mutation: `./a.txt: FAILED`; `sha256sum_rc=1` (KILLED).
- Captured-file deletion: `error: verification failed`, `verify_rc=4` (KILLED).
- Stray receipt file: `error: verification failed`, `verify_rc=4` (KILLED).
- Corrupt summary: `error: verification failed`, `verify_rc=4` (KILLED).
- Restored: both `sha256sum -c` entries `OK`; tool `captured+verified`, `verify_rc=0`. Restored manifest hash matched saved original (`585fd120a95539cb5dde3e1e1a5b8fde4d8f20d835e7b1a75927e043d10eb8e8`); summary matched saved original (`c11f3dd151ef17d298de17c64feef062a27855c4e61c62698c7d95b6fb79724c`). Scratch removed.
- Fixture command: `bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r28-wave-evidence-capture.sh`; output ended `case-4: FAIL (symlink refused rc=3 rc=0)` and `cases=6 pass=5 control=TAMPER-REJECTED`; command rc 1. Baseline failure makes the fixture run inconclusive as a full-suite result, not as evidence against the four isolated probes.

## Findings
1. Isolated receipt verifier rejects manifest alteration, missing member, unexpected member, and corrupted summary; each mutation was restored and pristine verification passed. Location: `tools/souji-wave-evidence-capture.sh:177-214`, quote: “The receipt is then re-verified: the manifest is recomputed over the copy”.
2. The four probes used a scratch-generated receipt, not the requested committed `census/round-26/waves/manifest.sha256`, because that path was absent at inspection. Actual round-26 receipt mutation remains untested.
3. Fixture symlink case does not reject a symlink during capture (observed rc 0 instead of expected 3). Location: `tests/fixtures/r28-wave-evidence-capture.sh:109-114`, quote: “case 4: symlink inside snapshot”. ATTACK: fixture failed its baseline control; do not treat the fixture as passing.

## Attack log
- ATTACK: C3 fixture baseline fails case 4 (symlink refusal); observed output `captured+verified` and rc 0 where rc 3 was expected. No predicate or target changed.