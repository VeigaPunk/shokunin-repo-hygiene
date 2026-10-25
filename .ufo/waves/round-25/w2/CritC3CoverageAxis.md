# CritC3CoverageAxis — C3 surface review: does the common-dir fixture move a new surface into coverage?

Seat: L1Souji25.CritC3CoverageAxis (critic, read-only leaf). Lane HEAD `6deb53561aace9aa14a399f88cf8150da4d4f4bd`; C3 draft in the working tree (uncommitted): `tests/fixtures/r13-repo-structure.sh` sha256 `eabc5f0a…e2c13` == w1 draft blob `c369546e` (byte-identical to ExecC3's draft), `corpus/knowledge/git-repo-structure-common-dir.md`, `corpus/README.md`, `corpus/SOURCES.md`, `SCORECARD.md` diffs. Probe `tools/souji-repo-structure.sh` unchanged at base and HEAD (blob `0f42ebf5`). Host git 2.56.0. Scratch `/var/tmp/souji-r25-CritC3CoverageAxis/` removed.

## STATUS: PASS — verdict: coverage IMPROVED (bounded); two minor overclaim/quibble defects

## Verdict
- **Coverage improved**, but strictly bounded: the improvement is on the **fixture/test surface and the knowledge map**, not on the probe. The linked-worktree common-dir write-safety envelope was previously **ungoverned**; it is now governed and falsifiable. No new probe code path, no capability, no operability delta (correctly not claimed). The colocated-vs-plain case is a precondition/calibration record, not probe-code coverage (see Finding 3).
- Not unprovable: the before→after (5/5 → 7/7) is measured and I reproduced it; the red arms die.
- Coverage map stays F2 frontier; no SKILL rule lands: confirmed — SKILL.md untouched (git status), README F2 row states "No size baseline, deletion authority, or F2 promotion to Core is claimed."

## Evidence (independent reproduction)
Green arm — extended fixture × committed probe (exact command: `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh`, git 2.56.0):
```
id=SOUJI-R13-STRUCT-linked-common-dir case=linked-common-dir rc=0 common_entries=53 private_entries=9 checks=8 control=PASS verdict=PASS
id=SOUJI-R13-STRUCT-colocated-vs-plain case=colocated-vs-plain plain_rc=0 colocated_rc=0 others_plain=0 others_colocated=2 commits_plain=1 commits_colocated=2 differing_keys=8 precondition=colocated-not-interchangeable-with-plain-baseline verdict=PASS
selftest=PASS ids=7/7   (baseline, no --probe: selftest=PASS ids=6/6)
```
Red arms (mutant wrappers around the committed probe; each run against extended fixture and against the committed OLD fixture `39b488a6`):
| mutant | behaviour | EXTENDED | OLD |
|---|---|---|---|
| m2 | appends to `$common/description` when linked | FAIL `linked-common-dir … detail= common-dir-manifest-delta` | PASS ids=5/5 (false green) |
| m3 | appends to `$private/gitdir` when linked | FAIL `… detail= common-dir-manifest-delta; private-gitdir-manifest-delta` | PASS ids=5/5 |
| m4 | prints private gitdir as `probe.git_common_dir` when linked | FAIL `… detail= probe.git_common_dir=…/linked-main/.git/worktrees/linked-tree want=…/linked-main/.git; probe.git_dir==probe.git_common_dir` | PASS ids=5/5 |
| m5 | rewrites `references.others.count=0` (colocated) | FAIL `colocated-vs-plain … others.count colocated=0 not> plain=0` | PASS ids=5/5 |
| m1 | noop | FAIL (no metrics) | FAIL (no metrics) |

Old fixture × real probe → `selftest=PASS ids=5/5` (matches committed base receipt `census/round-25/records/c3-control-base.tsv`: `tool_sha256=b6bf5205…179f`, rc=0, ids=5/5).

Q56: README F2 row entries column names `knowledge/git-repo-structure-common-dir.md` (SOURCES S124–S126) — satisfied in the draft.

## Findings
1. **A new surface enters coverage: yes, the linked-worktree common-dir write-safety envelope.** The old fixture passed all three linked mutants as false green, its LIMITS explicitly excluded linked worktrees, and the probe's own doc (tools/souji-repo-structure.sh:50-52) admits the committed fixture covers "one normal work tree only". The extended fixture now fails common-dir writes, private-gitdir writes, and a misreported common dir, and the detector controls run on both roots first. The 5/5 → 7/7 delta is real and its falsifiability is proven (red arms die). This is a genuine coverage gain for the skill's test arsenal under AXES.md coverage ("repo paths, tools, edge classes" — linked-worktree env and jj keep-ref refs are new edge classes).
2. **But it is coverage of pre-existing probe behaviour — not new probe surface.** The probe is byte-unchanged; it already handled linked worktrees correctly at base (blob 0f42ebf5). No new code path of the tool is exercised or added. The claim is therefore honestly a *fixture/knowledge* coverage move, and it would be an overclaim to read it as any tool improvement. SCORECARD/README frame it only as fixture counts + precondition — that framing is correct.
3. **colocated-vs-plain is a precondition/calibration record, not probe-surface coverage** (ScoutC3Structure-2 attack 3 upheld). The metric difference comes from git's own ref classification (`git repo structure --format=lines` is passed through verbatim, tool:312); any pass-through probe passes, and only a mutation of the emitted metric dies (m5). Its value is guarding the knowledge entry's precondition and preventing baseline misuse — real, but different in kind from the linked case. The README's "colocated/plain checks" wording should not be read as new probe coverage.
4. **Overclaim quibble A — S126 quote is not byte-verbatim.** The entry's Gate quotes "…main worktree's $GIT_DIR" with an ASCII apostrophe; the installed git-worktree(1) snapshot uses U+2019 ("main worktree’s"). S124/S125 quotes are present verbatim after whitespace normalization (23 and 6 words, both ≤25). Fix the S126 character or record the normalization.
5. **Overclaim quibble B — pending-evidence pointers.** SCORECARD's C3 row cites `census/round-25/records/c3-after.tsv`, and SCORECARD/README cite `corpus/lessons/round-25.md`; neither exists in the tree yet, and no amendment-3 red-arm receipt is committed. These must materialize at landing before admission; as of W2 they are drafts, not receipts.
6. **Envelope disclosure gap.** The linked case manifests the common dir and private gitdir but not the worktree root (B's `.git` file / B tree); a probe write to the worktree root would pass unnoticed. The entry discloses atime/ctime/mtime-restoring limits but not this root blind spot. Recommend one sentence in the entry's NOT-establish list.
7. **"No SKILL rule lands / F2 stays frontier": confirmed.** SKILL.md untouched; README explicitly renounces F2 promotion; the round claims only the measured fixture/knowledge delta.

## Attack log
- A1 (green/red reproduction): ran extended fixture × real probe (7/7), old fixture × real probe (5/5), and mutants m1–m5 against both; all expected outcomes reproduced (above).
- A2 (S124/S125/S126 quote fidelity): whitespace-normalized substring check against `census/round-25/sources/*.txt` snapshots; S126 mismatch noted (Finding 4).
- A3 (Q56 row): README F2 entries column inspected raw; entry named with S124–S126.
- A4 (receipt/tree state): `ls census/round-25/records/` shows only base controls; no c3-after/red-arm receipts yet (Finding 5).
- A5 (syntax/state): `bash -n` on extended fixture OK; working-tree fixture sha256 equals ExecC3's draft hash; probe unchanged.
