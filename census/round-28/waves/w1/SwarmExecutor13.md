## Status
STATUS: PARTIAL — C3 tool, fixture, and rounds 26/27 receipts are implemented and verified; frozen shared lane changes (including 11 tracked round-26 modifications and global `.gitignore`) are intentionally untouched.

## Evidence
- `bash -n tools/souji-wave-evidence-capture.sh && bash -n tests/fixtures/r28-wave-evidence-capture.sh` → both syntax checks passed.
- `bash tests/fixtures/r28-wave-evidence-capture.sh` → `cases=6 pass=6 control=TAMPER-REJECTED`, rc 0. Fixture uses isolated `/var/tmp` lanes only; supplementary check confirms symlink preservation without dereference.
- `bash tools/souji-wave-evidence-capture.sh /home/vgpnk/Projects/shokunin/souji-shokunin 26` → `captured+verified`, rc 0; same command for round 27 → `captured+verified`, rc 0.
- `bash tools/souji-wave-evidence-capture.sh /home/vgpnk/Projects/shokunin/souji-shokunin 26 --verify` and `... 27 --verify` → both rc 0. Receipts: `census/round-26/waves/manifest.sha256` 1,382 entries and `summary.tsv` 88 lines; round 27 manifest 124 entries and summary 80 lines.
- `git status --porcelain=v1 --untracked-files=all` scoped count: 11 dirty `.ufo/waves/` paths remain, all tracked round-26 files; no untracked wave path observed. Existing staged/working changes outside my scope were not modified.
- Base revision named by frozen contract: `3a2a80d0d18940a5e352ebc526da22a57dad83c4` (no revision update asserted; this read-only seat did not commit).

## Findings
1. Implemented capture utility and six-case isolated fixture. Tool copies the snapshot, emits sorted SHA-256 manifest and parsed result summary, verifies receipt and source file hashes, and returns declared failure codes. Location: `tools/souji-wave-evidence-capture.sh`. Source convention opened this run: `census/round-26/c3-counter.sh:1-5` — “souji round 26 C3 frozen counter (receipt-bound). Prints the axis-check instrument's presence and, when present, its verdict”.
2. Fixture includes the frozen six controls plus a supplementary internal/external-symlink preservation check. Location: `tests/fixtures/r28-wave-evidence-capture.sh`. Output as above.
3. Captured and re-verified rounds 26 and 27. Receipts are under `census/round-26/waves/` and `census/round-27/waves/`. Source locations: `.ufo/waves/round-26/w1-results.json`, `.ufo/waves/round-27/w1-results.json` (both opened and parsed this run).
4. No changes made to `.gitignore`, tracked round-26 wave bytes, any non-lane path, or git/jj state. Round-26 tracked modifications are still present; the L1/integrator owns their safe disposition. To ignore all wave dirt the frozen contract needs `.gitignore` containing `.ufo/waves/`, but that global shared file was intentionally left alone by this read-only leaf.

## Attack log
- ATTACK: Frozen `C3` requires dirty `.ufo/waves` count `0` after reverting tracked round-26 modifications. This seat observed 11 modified tracked paths and did not revert them: doing so would mutate shared tracked bytes outside my assigned delivery paths and conflict with the read-only-seat restriction. Parent must resolve at integration; report must not claim C3 fully met.
- ATTACK: `.gitignore` was untracked at observation and contained `.ufo/waves/`, `census/operator-sweep-*/`, `__pycache__/`; no edits made to it. No attempt to inspect operator-sweep contents.
