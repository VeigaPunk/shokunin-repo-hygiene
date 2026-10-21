# InputTargetWrapper — round-20 C2 operability review

**Axis:** operability. **Scope:** targeted r14 wrapper's measured-input binding and output path; source-only review.

## Observed source snapshot

The repository HEAD observed was `12516f7dcdd5b165e5ee208d44a38d63b5bd5812` (the declared baseline). At that observation, all six assigned source files were working-tree-modified relative to HEAD. Their SHA-256 digests were:

| Path | SHA-256 |
|---|---|
| `tools/souji-seat-audit.py` | `78d73d85ba198df6614a47b5d4d9388038da5c74407b475148713bc8958f6269` |
| `tools/souji-rev-pin.py` | `d49efa4e0ee4e9c275e2866dd7b6a20b201a4ac12d2225ca9a0772cfae6578c9` |
| `census/round-13/run-verification.py` | `945cf6ecd5f4472c2556eb6f0b26e0a42193268a158cf3a0a8d776c00ef1d0cc` |
| `census/round-14/run-verification.py` | `bde95f972e09de393d32b1aa840bc2282f1677c147399ae7ed24c6558f525f73` |
| `census/round-14/run-targeted.py` | `a0c08e1252df3b7c20cab6eaecaa8222c7eed5f39ba19188eca2da031c5fd3f2` |
| `census/round-14/cache-demonstration.py` | `706200486d0938322a773116ae01377f3a56ec82443415e0d1956cd126c95bd6` |

These are working-byte observations at review time, not committed-tip digests. No target code, runner, fixture, build, test, formatter, or linter was executed. No LSP device is mounted in this session; checks were from bounded source reads and the named baseline blob only.

## Findings

### MEDIUM — Targeted wrapper rereads a measured prior after its final snapshot check

`census/round-14/run-targeted.py:23-25` adds `census/round-14/verification-attempt-1.json` to `MEASURED_PATHS` and resolves the revision. After its commands, line 46 calls `module.checked_inputs(revision)`. That function compares the current snapshot with the initial `INPUT_SHA256` and raises on mismatch (`census/round-14/run-verification.py:75-79`). But line 49 then rereads the same measured prior via `module.sha(prior)`, and `module.sha` uses `Path.read_bytes()` (`census/round-14/run-verification.py:102-103`), which follows a replacement symlink. The wrapper subsequently hardcodes `inputs_unchanged_during_run=True` at `run-targeted.py:51` and writes the record at lines 58-59 without another snapshot check.

**Counterexample:** after `checked_inputs` returns at line 46, replace the prior evidence file with different bytes (or a symlink) before line 49. The wrapper can emit the already-verified `input_sha256` mapping alongside a `prior_evidence_sha256` computed from the replacement, still claiming inputs were unchanged. The post-check read is outside the check; source inspection shows no later refusal path for this drift.

**Suggested correction:** perform any separate prior digest read before the final `checked_inputs` call, then let that final snapshot reject drift before output; alternatively derive the field from the verified snapshot mapping and make the final snapshot the last measured-input read before creating the record. Add one deterministic oracle interleaving: mutate/symlink the prior immediately after its separate digest read and before the final snapshot, requiring exit 2 and no output. This tests the no-drift-before-output property rather than only a dirty-at-start path.

**STATUS: OPEN.** The targeted wrapper's C2 no-drift-before-output guarantee is not complete while it rereads a measured input after the final snapshot check and emits an unchanged claim without revalidation.

## Confirmed behavior / residual verification gaps

The specific historical own-wrapper omission appears repaired in the observed working bytes: `census/round-14/run-verification.py:32-46` includes the helper (`tools/souji-rev-pin.py`), the r14 runner itself, `run-targeted.py`, the frozen fixture directory, `corpus/SOURCES.md`, and the r13 evidence file. `run-targeted.py:25` resolves before running measurements; `run-targeted.py:46` rechecks before record construction; and `run-verification.py:82-100` validates a contained new JSON output path and rejects an existing target. The baseline HEAD list had only eight entries and omitted the helper and targeted wrapper, consistent with the bounded historical issue at `/home/vgpnk/Projects/shokunin/.ufo/reports/round-19/souji.md:242-245`.

Static path checks found every listed r13/r14 measured file or bounded directory tracked at HEAD and present in the worktree. No runtime refusal, output creation, race, or CLI behavior was exercised under this read-only assignment. The preregistered C2 oracle names dirty helper/wrapper/frozen/source/knowledge paths, but does not name this wrapper's appended prior-evidence input or the post-check interleaving above; add that specific arm before treating this receipt path as verified.
