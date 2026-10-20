# RevR14Revert — r14 fixture revert + r15 frozen record verification (WAVE 2, round 18)

STATUS: DONE — all four verification targets hold; no defects found.

Attacked claims: r14-census-boundary.py reverted to b576341 bytes at 5efb519 because
tools/souji-preservation-evidence.py pins its digest (C1/C2 supporting invariant);
tests/fixtures/r15-preservation-frozen/{record,expected}.json at 5efb519 pin
measured_commit 2fc5f33… with digests equal to blobs at that commit; frozen check and
selftest execute clean at 5efb519.

## 1. r14 revert — HOLDS

All three digests identical, `e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2`:

- `git show 5efb519f00075d958c3d1109ef6fcb24c487eb87:tests/fixtures/r14-census-boundary.py | sha256sum` → e6a984b1…14b2
- `git show b5763415cc67ecff1e8fe56c58c39a6fb106d7a3:tests/fixtures/r14-census-boundary.py | sha256sum` → e6a984b1…14b2
- tools/souji-preservation-evidence.py @5efb519 line 307 `NAMESPACE_SHA256 = "e6a984b1…14b2"` (also docstring line 107); literal byte-identical at b576341 line 307 — the pin itself was never moved.
- `git diff --stat b576341 5efb519 -- tests/fixtures/r14-census-boundary.py` → empty (R14DIFF-EMPTY).

Revert provenance (git log b576341..5efb519 -- <path>):
- 3f822e8 wave-1 build modified the fixture (diff 3f822e8→2fc5f33: 11 insertions, 63 deletions reversed).
- 2fc5f33 "round-18: … r14 fixture back to pinned bytes …" — the revert commit.
- 5efb519 regenerated the frozen record (see §2).

## 2. Frozen record/expected at 5efb519 — HOLDS

record.json (blob 269fafaa, worktree sha256 bd85b0248bfff4e82909d0085ef9d26a7ee34c2cdcd52ed946b130058ef1d57b):
- `measured_commit` = 2fc5f33d0b000c0e10450a5139137bf4300fe54b; resolvable commit, `git merge-base --is-ancestor` → ancestor of 5efb519.
- `namespace_fixture` = tests/fixtures/r14-census-boundary.py sha e6a984b1…14b2 (equals pinned r14 digest; also equals the blob at 2fc5f33 — checked).
- `fixture` r15-census-config.py sha 61208dbd53367fa85b6f2e6d10d521900a34e1f41a27962cfbb1559ea0189f08 = blob at 2fc5f33 (and identical at 5efb519).
- `runs.changed.tool` and `namespace_controls.tool` sha 7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd = tools/souji-census.sh blob at 2fc5f33 (and identical at 5efb519 — census.sh is byte-identical between 2fc5f33 and 5efb519; both contain 17 `repo-timeout` occurrences, so C1's bounded-census machinery was already in census.sh by 2fc5f33 and 5efb519 touched fixtures/records only).
- namespace_controls cases R14C2-01..12 all pass, exit 0, summary total=12 failed=0; runs arms baseline_preharm (8/20 fail), baseline (16/20 fail), changed (0/20 fail) — internally consistent with the checker's pinned class matrix.

expected.json (blob 98fb90af):
- `record_sha256` bd85b024… = sha256 of record.json blob at 5efb519. ✓
- `files` pins: r14 e6a984b1…, r15-config 61208dbd…, census.sh 7e6a92d4… — all equal blobs at measured_commit 2fc5f33. ✓
- `verdict` "clean". ✓

## 3. ALLOWED-EXEC (clone /var/tmp/souji-r18w2-RevR14Revert/lane @5efb519, deleted after)

- `python3 tools/souji-preservation-evidence.py --root . --frozen tests/fixtures/r15-preservation-frozen`
  → `souji-preservation-evidence: clean`, scope declared-record consistency only,
  measured_commit 2fc5f33…, arms baseline_preharm,baseline,changed,namespace_controls,
  frozen_files: 3, exit 0.
- `python3 tools/souji-preservation-evidence.py --selftest` → `selftest: 47/47 passed`, exit 0.

## Verdict

HOLDS. The r14 fixture at the landed tip is byte-identical to the b576341 baseline and to
the NAMESPACE_SHA256 pin; the frozen record/expected pair at 5efb519 pins measured_commit
2fc5f33 with digests that equal that commit's blobs; the checker admits the frozen input
clean at the tip and the selftest is green.

Residual risk (no action for this round): expected.json pins census.sh at 7e6a92d4…, which
is still the tip blob; any post-5efb519 change to census.sh or either fixture flips the
frozen input to snapshot_tampered (exit 2) until regeneration — behavior documented in
tests/fixtures/r15-preservation-frozen/README.md, by design.

Tooling installs: none (no pacman/uv/npm installs performed; pacman guard respected).
