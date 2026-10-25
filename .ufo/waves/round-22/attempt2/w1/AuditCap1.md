STATUS: PASS

PASS on the frozen C1 enumeration only: **assertions=14 resolved=14 skipped=15 mismatches=0** over the first 5 `## Capabilities` data rows measured at `4edb25dfe262515d0da63224bbba71e02e36cba5`. No frozen-class assertion in this slice fails. Two *out-of-enum* truth defects were found (F1, F2); neither is counted by the prereg's `M`, and both are disclosed below rather than folded into the verdict.

Evidence census (one row per token): `.ufo/waves/round-22/attempt2/w1/evidence/AuditCap1.tsv` (29 token rows = 14 assertions + 15 skipped).

## Measured revision and slice

- Measured revision: `4edb25dfe262515d0da63224bbba71e02e36cba5` (`git cat-file -e 4edb25d…^{commit}` → rc 0).
- Slice: `SCORECARD.md` `## Capabilities` data rows 1–5 = **base-rev lines 45–49**. Header at base is line 43, separator 44; `## Capabilities` at 41.
- The five rows are **byte-identical** at base rev lines 45–49 and at HEAD `2a130b47db43eb4b3d80b2e7a5112d6b4b021899` / worktree lines 50–54 (`diff` → `five-rows-byte-identical`). Line numbers moved +5 because `SCORECARD.md` grew after the freeze (`git diff --stat 4edb25d HEAD -- SCORECARD.md` → `15 insertions(+), 6 deletions(-)`); slice sha256 = base `b3cecc97…`, HEAD `71507c60…`. The TSV uses **base-rev line numbers** so it addresses the measured revision.
- No glob (`*`) tokens and no `:<line>`-suffixed tokens occur in this slice. No 64-hex token occurs in any of the five rows (`grep -oE '\b[0-9a-f]{64}\b'` → empty), so the slice contains **zero in-cell class-C assertions**.

## Exact command per class (read-only git, no writes to the lane)

| class | command | result |
|---|---|---|
| rev exists | `git -C … cat-file -e 4edb25d…^{commit}` | rc 0 |
| A (path present at rev) | `git ls-tree -r 4edb25d… --name-only` (3545 entries) then exact `grep -Fxq -- <path>` per backticked span | 13/13 `PRESENT` |
| B (revision token) | `git -C … cat-file -e 31984f4^{commit}` | rc 0 → resolved |
| C (digest) | `git show 4edb25d…:<path> \| sha256sum` | no in-cell 64-hex token to score; applied nevertheless to the two tools named by the "current installed digest" phrase (F1) |
| durability cross-check (not a class) | `git rev-parse --disambiguate=31984f4 \| wc -l` → 1; `git rev-parse 31984f4` → `31984f473ce4bdab61a99b16cca194b28108cb81`; `git merge-base --is-ancestor 31984f4 4edb25d` → yes | unique, ancestral |

Class-A paths, all present at the measured rev: `census/round-1/census-summary.json`, `census/round-1/census.tsv`, `tools/souji-verify.sh`, `census/round-13/verification.json` (×3 cells), `tests/results/INSTALL.json`, `tests/results/parent-harness-live.json`, `census/round-3/seat-61.json`, `census/round-3/seat-62.json`, `tools/souji-vault-verify.sh`, `tests/results/parent-vault-battery.json`, `corpus/SOURCES.md`.

## Executed non-class corroboration (reported as observations, never as class verdicts)

- `(246 rows)` (line 45) — `git show 4edb25d:census/round-1/census.tsv | wc -l` → 247 = header + 246 data rows; `census-summary.json` records `"rows_total": 246`. Claim holds.
- `baseline 33 rows, mined=16 queued=15 rejected=2 at 31984f4` (line 49) — at `31984f4`, `corpus/SOURCES.md` has 33 `S###` rows and status column counts exactly `16 mined / 15 queued / 2 rejected`. Claim holds (16+15+2=33).
- All seven referenced JSON files parse as JSON at the base rev (`json.load` → valid for `census-summary.json`, `verification.json`, `seat-61.json`, `seat-62.json`, `INSTALL.json`, `parent-harness-live.json`, `parent-vault-battery.json`).

## Skipped tokens (15, with reasons — none silently dropped)

Counts: `246`, `64`, `33`, `16`, `15`, `2` → `skipped:count-not-in-class` (verified above where a source existed). Round labels `r1, r2, r3, r4, r12` → `skipped:round-label-not-in-class`. `LOG r3`, `LOG r4` → `skipped:not-backticked-non-class-reference`; `LOG.md` is tracked at the rev, so neither is dangling. `current installed digest` (×2) → class C candidate **skipped** because the cell carries no 64-hex token; the defect behind that skip is F1.

## Findings

### F1 — MEDIUM, calibration; out-of-enum (not counted by `M`): "current installed digest" is stale at the measured rev

Lines 46 and 48 state `current installed digest in census/round-13/verification.json`. Executed:

```
# committed bytes at the measured rev
git show 4edb25d:tools/souji-verify.sh       | sha256sum -> f88fed23e2c80fdfea13775659f2dfc157f33a5540772059c7e3ab5dd6c7ff1c
git show 4edb25d:tools/souji-vault-verify.sh | sha256sum -> 5cb0fb13fc9b0fc306e3841e5857f028610f1698bee8e8cf69d51575ae2810bb
# what the cited receipt actually records
census/round-13/verification.json "installed_sha256":
  tools/souji-verify.sh       -> 9adb17645a5f452ae2cc28673642ad256f9aee92109939531f3c34a0972812cd
  tools/souji-vault-verify.sh -> f9e778ca478c7aa8b33234ee793030df631c1b9fcebc942b1ff41d0008ed9c5b
# provenance: those values ARE the committed tool bytes at r13, not at the base
6f8ee0f (r13 measured_commit) -> 9adb176…/f9e778c…
31984f4 (r13 baseline_commit) -> 9adb176…/f9e778c…
```

So the recorded digests are genuine but **historical**: they match committed bytes at `6f8ee0f3…` and `31984f4`, and were superseded before `4edb25d`. Presenting them as "current" is false at the measured rev. `git cat-file -t 9adb176…` → `Not a valid object name`, so they are not blobs resolvable as objects either; only sha256-over-bytes (the prereg's class-C definition) can judge them.

Minimal truth-preserving repair (wording only; the capability claim stays):

- line 46: `… | `tools/souji-verify.sh`; r13-era installed digest (superseded; committed at this rev: sha256 f88fed23e2c80fdfea13775659f2dfc157f33a5540772059c7e3ab5dd6c7ff1c) in `census/round-13/verification.json`; historical evidence `tests/results/INSTALL.json`, `tests/results/parent-harness-live.json` |`
- line 48: same substitution with `5cb0fb13fc9b0fc306e3841e5857f028610f1698bee8e8cf69d51575ae2810bb` and `tests/results/parent-vault-battery.json`.

If the round prefers the smallest diff, replacing "current installed digest" with "r13-era digest (historical)" already removes the false currency claim and keeps every path pointer truthfully. Not proposed: deleting the digests or the capability claim. (Note `tests/results/INSTALL.json` records a third value, `7efda63b…`, also not a git object — it describes r2's installed copy; do not present it as current either.)

### F2 — LOW, calibration durability: the line-49 revision token is an abbreviated id the lane's own r19 capability refuses

`31984f4` is class-B resolved and unique today, but `tools/souji-rev-pin.py` raises `"revision %r is not a full 40-hex commit id (HEAD, branch names, abbreviated ids and symrefs are refused)"` and carries fixture case `short-id-refuse`. The SCORECARD's evidence token therefore sits below the lane's own durable-revision standard.

Repair (no claim changed): write `31984f473ce4bdab61a99b16cca194b28108cb81` instead of `31984f4`. The full id is already committed in the same row's cited receipt (`census/round-13/verification.json` → `"baseline_commit": "31984f473ce4bdab61a99b16cca194b28108cb81"`), so this is a one-token edit with committed provenance.

### F3 — MEDIUM, instrument coverage (for the C1 author; no redefinition performed)

Frozen class C requires a 64-hex token **in the same cell as exactly one backticked path**. Every digest-bearing cell in this slice names 3–4 paths and no digest token, so a false "current installed digest" sentence is invisible to the counter: `M=0` is achievable while F1 survives. I did not re-define the enum; the consequence is operational — the in-round repair must be the F1 wording change, not reliance on the counter, and any new checkable digest claim would need a sentence naming exactly one path (new content under the existing class-C rule, not a new rule).

### F4 — INFO: non-class pointers are not dangling

`LOG r3` / `LOG r4` are unbackticked, so class A cannot see them; `LOG.md` is present at the measured rev. They are skipped, not mismatched.

## Residual risk and verification gaps

- Not run: `python3 tools/souji-declared-evidence.py`. At the measured rev it does not exist (`git ls-tree 4edb25d -- tools/souji-declared-evidence.py` → 0 entries; tracked only at HEAD `2a130b4`), so it cannot produce an independent count for `4edb25d`, and running the in-flight HEAD copy would not be a check of my census. All numbers above come from git plumbing and `sha256sum` only.
- Not established: whether an installed copy of the verify tools existed on this host at r13 or exists now (no `souji-*.sh` found on the checked install dirs / PATH). F1 is therefore a statement about committed bytes versus the receipt's recorded digests, not about any host installation.
- Scope held: read-only git only; no writes outside this report and `…/w1/evidence/AuditCap1.tsv`; `SCORECARD.md` untouched (`sha256sum` unchanged, `71507c60…`), no git/jj write, no index/state/MANIFEST touch, no deletion authority created.
- Tooling: no tool installed or updated in this task.

Report: .ufo/waves/round-22/attempt2/w1/AuditCap1.md
