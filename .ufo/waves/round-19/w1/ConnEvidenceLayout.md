STATUS: DONE — the r19 plan has receipts for individual C1/C2/C3 runs, but omits several r18 closure records and has two naming mismatches that would leave the outside verifier guessing.

# Findings

## One bounded move

Before closure, make an r18-shaped, commit-bound r19 evidence packet. Preserve the existing per-command outputs; add the missing aggregate records below and point the round report/lesson at the exact committed paths. Use the seven-character prefix of each record's actual measured code revision in the matrix and final-verification filenames; do not reuse the existing `63bb887` suffix for changed bytes.

| Exact path L1 should provide | Why / current status |
|---|---|
| `census/round-19/c1-matrix-<measured-code-revision-short>.json` | Missing from the current census inventory. R18's `c1-matrix-4800fd7.json` is the structured, per-arm/per-suite record with revision, fixture digests, run metadata and results; r19 currently has separate text receipts `c1-carry.txt` and `c1-audit.txt`, not a comparable matrix. Bind base `3ab2c81`, changed revision, tool/fixture hashes, per-case base-vs-changed outcomes and preserved controls. |
| `census/round-19/final-verification-<measured-code-revision-short>.json` | `run-acceptance.py` defines this commit-suffixed output. `final-verification-63bb887.json` exists, but its record binds `63bb887` and the recorded seat-audit fixture digest; read-only `git diff --name-status 63bb887..HEAD` showed that fixture and the acceptance runner changed afterward. Keep the old record as history and create the final receipt for the finalized changed bytes. |
| `census/round-19/counts.json` | The preregistration correction explicitly names this C3 before→after record, but the current inventory has only `counts-start.json` and `counts-end.json`. Record the actual full-revision `count-claims.py` invocations and outputs (6 at `3ab2c81`, 7 at `005f3d3`), or append a correction that explicitly makes the split files authoritative; do not leave the named path absent. |
| `census/round-19/source-counts.json` | Missing from the current inventory. This is the r18 convention for the source-registry before/after rows, tiers, statuses, malformed count, and new-row/change note. The r19 `counts-start/end.json` contain source totals (78→85) alongside the knowledge count, but do not provide the established same-named aggregate. Keep this distinct from the C3 admitted-entry `counts.json`. |
| `census/round-19/seat-audit-r18-recheck.json` | The preregistration names this singular output; the current records are split into `seat-audit-r18-recheck-w1.json` and `...-w2.json` (plus `-confirm` records). Add the named aggregate/index with both wave results and references/digests to the detailed records, or explicitly correct the preregistered pointer in an append-only correction. |
| `.ufo/waves/round-19/dead-seats.json` | Missing from the current wave-directory inventory. Record initial-dead counts, failed follow-ups, retry/replacement disposition for w1, w1b and w2. Explicitly keep the 22 seats dropped during repacking under the job cap classified as unexecuted-for-packing, not dead seats or replacements. |
| `census/round-19/transcripts/MANIFEST.sha256` | Missing with the transcript tree from the current census inventory. Include the raw transcript files for every executed batch (w1, w1b and w2; keep batch identity in the relative paths) and hash each one. A manifest without its referenced transcript bytes is insufficient. |

The existing `census/round-19/proc-agreement-pinned.json` and `verify-agreement-pin.py` are present and cover the planned D2 pin artifact; retain them with the packet. The current C1 text receipts are useful evidence, not substitutes for the missing aggregate matrix.

## Conventions and discrepancies

R18's closure relies on a structured matrix and a commit-bound final-verification record, re-derives counts from the committed matrix, reports `dead-seats.json`, and checks a transcript manifest against the transcript files (`corpus/lessons/round-18-verifier-spotcheck.md:45-56,64-68,82`). The source-count aggregate is specifically `census/round-18/source-counts.json:1-8`; dead-seat dispositions are in `.ufo/waves/round-18/dead-seats.json:1-13`; the transcript checksum file is `census/round-18/transcripts/MANIFEST.sha256` (170 files/170 manifest lines: `corpus/lessons/round-18-verifier-spotcheck.md:49-50`).

R19's preregistration specifies C1 command outputs and the singular audit-recheck path (`.ufo/waves/round-19/preregistration.txt:23-31`), the C3 source/knowledge measurements (`:56-64`), and then explicitly names `counts.json` (`:79-96`). In the worktree, `counts-start.json` records the baseline and points to `counts-end.json` (`census/round-19/counts-start.json:1-20`); the end record has the 6→7 knowledge and 78→85 source values (`census/round-19/counts-end.json:20-56`). This is useful data, but it does not satisfy the preregistered `counts.json` path or the r18 `source-counts.json` convention without a clear pointer/correction.

The existing final-verification record is commit-keyed and captures changed-file hashes (`census/round-19/final-verification-63bb887.json:1-20`); the runner documents the required final-revision output naming (`census/round-19/run-acceptance.py:1-13`). Since the measured revision and a changed fixture differ from the current lane tip, the record is a historical receipt, not evidence for the later changed fixture. No current r19 `c1-matrix-*.json`, `source-counts.json`, `counts.json`, top-level audit aggregate, `dead-seats.json`, or transcript manifest was present in the directory inventories I read.

# Evidence

- R18 closure evidence: `corpus/lessons/round-18-verifier-spotcheck.md:45-56,64-68,82`; source-count format `census/round-18/source-counts.json:1-8`; matrix identity/fixture metadata `census/round-18/c1-matrix-4800fd7.json:2540-2565`; dead-seat schema ` .ufo/waves/round-18/dead-seats.json:1-13`.
- R19 preregistered paths and corrections: `.ufo/waves/round-19/preregistration.txt:23-31,56-64,79-96`.
- Current r19 records read: `census/round-19/c1-carry.txt:4-18`, `c1-audit.txt:22-30`, `counts-start.json:1-20`, `counts-end.json:20-56`, `final-verification-63bb887.json:1-20`, and `run-acceptance.py:1-13`.
- Read-only revision comparison: current `HEAD` was `3a25875cee6053ec7f76ed278986d6367bf7bff7`; `git diff --name-status 63bb8878bace9f814c1d94a8c7932b37da1259c8..HEAD` included modifications to `tests/fixtures/r19-seat-audit-shapes.py` and `census/round-19/run-acceptance.py`.
- R19 wave packing is documented in `.ufo/waves/round-19/w1b-spec.json:5`; distinguish its packing drops from dead-seat accounting.

# Commands run

- Read the r19 preregistration and w1/w1b/w2 specs; read the r18 verifier spot-check and named r18/r19 evidence records.
- Listed `.ufo/waves/round-18`, `.ufo/waves/round-19`, `census/round-18`, and `census/round-19` with the directory reader. R18 contains the named matrix, source counts, dead-seats record and transcript manifest; current r19 inventory lacks the named closure records above.
- Read-only `git rev-parse HEAD`; `git log -6 --oneline --decorate`; `git diff --name-status 63bb8878bace9f814c1d94a8c7932b37da1259c8..HEAD`.
- No tests, census, acceptance runner, or verification command was executed.

# Contract compliance

Only this scoped report was written. No subagents, `ask`, jj commands or git mutations; no signal, `/proc/*/environ` or secret reads; no network access, scratch directory, or tool installation. The suggested closure checks are not claimed as run. The outside closure can verify the packet statically by checking each recorded revision/hash against committed bytes, recomputing the count deltas from the records, and running `sha256sum -c --quiet` over `census/round-19/transcripts/MANIFEST.sha256`; that transcript verification was not run here.