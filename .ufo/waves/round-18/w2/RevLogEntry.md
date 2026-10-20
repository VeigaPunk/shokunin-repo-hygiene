STATUS: DONE — round-18 LOG claims reviewed against the committed records

# Attacked claim

Calibration of `LOG.md:951` at `5efb519f00075d958c3d1109ef6fcb24c487eb87`: verify the round-18 numbers and routed fixes against their committed evidence. No files other than this report were written. No fixtures, selftests, or lane code were run.

# Findings

## MEDIUM — R14's claimed session-wide timeout cleanup was not landed

`LOG.md:951` says the r14/r15/r17 fixtures all kill their session on timeout. That is false for the r14 fixture committed at the reviewed revision. The source at `tests/fixtures/r14-census-boundary.py:392-402` uses `subprocess.run(..., timeout=90)` and returns a timeout result; this path has no new-session setup or descendant/session cleanup. In contrast, the committed r15 fixture's `run_in_session` starts a new session and calls `kill_session` on timeout (`tests/fixtures/r15-census-config.py:297-311`), and r17's `run_process_group` does the same (`tests/fixtures/r17-census-hygiene.py:175-200`). `corpus/QUALITY.md:79` accurately says r14 has no FIFO case and remains at its b576341 bytes because its digest is pinned.

The matrix does not establish the contrary for the landed r14 fixture: `census/round-18/c1-matrix-worktree.json` has `allow_dirty_fixtures: true`, lists `M tests/fixtures/r14-census-boundary.py` in `fixtures_dirty`, and records the test fixture hash as `6c1c0cfde846be2f9c56402eddf24de0337350f007998d0c48da3ce9eb6fb5e3`. At 5efb519, the r14 fixture's SHA-256 is `e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2`; its Git blob is identical at b576341 and 5efb519 (`c6a3b31d54b705148aa5a84687a312014b68de67`). Therefore the recorded r14-namespace 12/0 ran on transient, non-landed bytes; it is not a result for the pinned final fixture.

**Verdict:** the session-wide-kill statement needs an append-only correction; the r14 12/0 result is reported accurately as a run result but is not landing-byte evidence. Smallest fix: append that r14 remained pinned and unmodified, narrow the fixture cleanup claim to r15/r17 (and r18 where applicable), and mark the r14 result as using dirty fixture bytes unless separately remeasured.

## LOW — the R2 correction misidentifies the LOG section it points to

`LOG.md:951` calls `LOG.md:916` the “round-17 D3 entry.” In fact, `LOG.md:910-919` is the round-16 correction for the 28-versus-29 uncarried-marker count; line 916 is the citation inside that correction. The target line does contain the never-committed `census/round-17/gate-replays-ddb7347.json` path, so the correction's underlying path issue is real, but its section attribution is wrong.

**Verdict:** append-only clarification should identify line 916 as part of the round-16 correction, not a round-17 D3 entry. The corrected committed target `census/round-17/gate-replays-4f48343.json` exists at 5efb519; the `gate-replays-ddb7347.json` path does not.

## MEDIUM — linked live-pair equality is not established by the saved pair files

This is not asserted in the text of `LOG.md:951` (which only corrects the repository count), but the cited R3 evidence is also used by `SCORECARD.md:15` for “live fleet pair identical on 21 repositories.” Exact diffs of the committed pair TSVs are not identical: pair 1 differs in the tameshi mtime; pair 2 additionally differs in mado's dirty count (10 in base, 13 in changed), as well as mtime values. Concurrent live changes may explain this, but the records do not bind the two runs to one unchanged snapshot, so they cannot support an unqualified identical-row claim.

**Verdict:** the 21-repository count holds; the stronger adjacent equality claim is unproven by these files. Smallest fix is to qualify the observed live deltas or rerun against a stable snapshot before using the pair as no-harm evidence.

# Checks and evidence

- `git show 5efb519f00075d958c3d1109ef6fcb24c487eb87:census/round-18/c1-matrix-worktree.json | jq ...` returned changed arm `rev=WORKTREE`, census SHA-256 `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`, r18 bounded `0/8` failed, r14/r15/r17 suites `0/12`, `0/20`, `0/29` failed, and census selftest `62` checks/`0` failed. Baseline `b576341` had r18 bounded `5/8` failed and selftest `49`; the reported C1 numbers hold. The committed census SHA-256 matches the changed-arm SHA. The committed r15, r17, and r18 fixture hashes match their matrix hashes; r14 is the sole fixture hash mismatch.
- `git show 5ef...:census/round-18/gate-pointers-before-b576341.json | jq ...` returned exit 2, `findings=10`, `checked_ptrs=319`, `checked_measured=3`. Its paths group as two gate-replays citations, five jj-receipts citations, one operator-sweep path, one nested `.git` path, and one `LG-FROZEN-MEASURED`; thus the LOG's “10 findings (7 never-committed record citations)” holds.
- `git show 5ef...:census/round-18/gate-replays-r18.json | jq ...` returns five recorded historical replays (r13-admitted, r14-landing, r15-landing, r16-landing, r16-precarry), all `match=true`. This supports the round-17 pinned-replay statement in the round-18 lesson (the r17 replay suite covers those five historical records); `expected_sha_match=false` is explicitly described there as by design. The record's top-level `selftest` is `null`, so it does not itself preserve the claimed gate selftest output or a current-tip gate result.
- `git show 5ef...:census/round-18/jj-receipts-r18-baseb576341.txt` ends `SUMMARY total=35 failed=1 skipped=2`, with J13 FAIL. The changed receipt ends `SUMMARY total=35 failed=0 skipped=2`, with J13 PASS. This supports the J13 b576341 FAIL → PASS claim. `tools/souji-quarantine.sh:252-255` reads `git config --get lane.id`; the Q29 row in `corpus/QUALITY.md:78` matches the routed owner rule.
- Each of the four `census/round-18/live-fleet-pairs/*.tsv` files has 22 lines: one header plus 21 repositories. The R3 repository count is correct. `leak-count-live-1721.json` reports 65 PIDs; `proc-census-live-1721.tsv` has 67 lines (boot-id comment, header, 65 rows). A `comm -3` comparison of its sorted numeric PIDs against the JSON PIDs emitted no differences. The pre-round orphan list has 58 lines, matching the stated starting count.
- Pair-file `diff -u` results: pair1 exit 1 (tameshi mtime differs); pair2 exit 1 (mado dirty count 10→13 and mtime differences). This is why the neighboring SCORECARD equality claim is not supported as written.
- `3f822e8` resolves to `3f822e85c6a5f866c4003be0ad039d5583d14364` and is an ancestor of 5efb519. `LOG.md:951`'s build revision is valid. R2's corrected record path and R3's repository count are correct; Q29's supersession of Q7 is stated in the committed quality row.

# Residual risk and verification gaps

The round-18 lesson records gate selftest 33→53 and pointer/proc-census fixtures 11/0; it records the quarantine selftest count as 101→105, while `LOG.md:951` asserts 105/0. The corresponding fixture sources exist. The committed round-18 JSON records inspected here do not preserve those individual command outputs, and `gate-replays-r18.json` has `selftest: null`; these results are not falsified, but they are not independently recoverable from the cited structured records. The lesson's “after: same command at the round tip — see Gate” pointer does not include a zero-findings output, and the baseline gate JSON is not a current-tip run; the round-tip 0 claim therefore remains unsubstantiated by the cited records.

LSP is unavailable in this environment (`read xd://lsp` returned “No such tool”). Exact-file reads and literal searches were used as the fallback; no grep result is treated as semantic proof. No runtime routing or saturation change is present in the reviewed LOG entry, so canonical-runtime and same-identity-rerouting checks are not applicable here. Overall verdict: **PARTIAL** — the principal C1 and baseline C2 numbers, J13, R2's corrected path, R3 count, and R4 hold; append-only correction is required for the r14 cleanup claim and the R2 section attribution, and the linked live-pair equality wording needs qualification.