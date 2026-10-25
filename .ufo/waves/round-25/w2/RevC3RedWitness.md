# RevC3RedWitness — W2 falsification of ExecC3 red-arm receipts (souji r25 w2)

Seat: L1Souji25.RevC3RedWitness (reviewer, leaf). Host git 2.56.0 (`git --version` = `git version 2.56.0`). Lane HEAD `6deb53561aace9aa14a399f88cf8150da4d4f4bd`. No installs, no probes of `.scratch/`/`/proc`. Scratch `/var/tmp/souji-r25-RevC3RedWitness/`, removed at completion.

## Status
STATUS: PASS. Every red-arm row in `w1/ExecC3.md` reproduces byte-behaviorally: all five mutants (m1–m5) FAIL the extended fixture with rc 1 and the exact `detail=` strings from the receipt table; m2–m5 pass the committed fixture as false green (`ids=5/5` rc 0). Green arms re-verified: committed fixture + real probe = `selftest=PASS ids=5/5` rc 0 (matches `census/round-25/records/c3-control-base.tsv`); extended fixture + real probe = `selftest=PASS ids=7/7` rc 0; baselines `ids=4/4` / `ids=6/6`. No missing red arm: amendment 3's two mandatory arms ((a) misreport private gitdir as common dir, (b) write common dir only under linked worktree) are both present in the receipt and both reproduce FAIL on the extended fixture.

## Method and exact commands
Old fixture = committed bytes only: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show HEAD:tests/fixtures/r13-repo-structure.sh > /var/tmp/souji-r25-RevC3RedWitness/old-fixture.sh` (sha256 `b6bf52056d037b2251632b409be3d31852588480c392ddc50ca8f8dbf101179f`). Extended fixture = `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-25/w1/r13-repo-structure.sh` (sha256 `eabc5f0ac56ea3db9f6f68d2dfeadbc91f592eb68c3691d2eabbd5b8347e2c13`); `cmp` shows the working-tree `tests/fixtures/r13-repo-structure.sh` is byte-identical to this draft. Mutants rebuilt exactly from the ExecC3 generator (lines 44–67 of the receipt). Probe = `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-repo-structure.sh` (blob `0f42ebf5afac31e8dbddfc67de6b30ef96e4806c` at HEAD, sha256 `80025137b20d5a6143db0120057552bd239fb60de1a504ede69896baade5aec2`).

Runs (each: `bash <fixture> --selftest --probe <mutant|probe>`, stdout+stderr captured separately; stderr 0 bytes on every run, including all failing runs):

```
OLD (committed)      NEW (extended)
m1-noop   rc=1 FAIL ids=5/5 failed_verdicts=1   rc=1 FAIL ids=7/7 failed_verdicts=1
m2-common-write       rc=0 PASS ids=5/5          rc=1 FAIL ids=7/7
m3-private-write      rc=0 PASS ids=5/5          rc=1 FAIL ids=7/7
m4-common-misreport   rc=0 PASS ids=5/5          rc=1 FAIL ids=7/7
m5-others-zero        rc=0 PASS ids=5/5          rc=1 FAIL ids=7/7
real probe            rc=0 PASS ids=5/5          rc=0 PASS ids=7/7
baseline (no probe)   rc=0 PASS ids=4/4          rc=0 PASS ids=6/6
```

## Receipt-vs-rerun table (W1 ExecC3 rows re-run)
| mutant | receipt row (W1) | rerun OLD | rerun NEW | match |
|---|---|---|---|---|
| m1-noop | FAIL rc 1 (both) | FAIL rc 1 | FAIL rc 1 | yes |
| m2-common-write | draft FAIL `common-dir-manifest-delta`; committed PASS 5/5 | PASS 5/5 | FAIL detail=`common-dir-manifest-delta` | yes |
| m3-private-write | draft FAIL `common-dir-manifest-delta; private-gitdir-manifest-delta`; committed PASS 5/5 | PASS 5/5 | FAIL detail=`common-dir-manifest-delta; private-gitdir-manifest-delta` | yes |
| m4-common-misreport | draft FAIL `probe.git_common_dir=…/linked-main/.git/worktrees/linked-tree want=…/linked-main/.git`; committed PASS 5/5 | PASS 5/5 | FAIL detail=`probe.git_common_dir=<…>/linked-main/.git/worktrees/linked-tree want=<…>/linked-main/.git; probe.git_dir==probe.git_common_dir` | yes (path prefix differs by mktemp id, expected) |
| m5-others-zero | draft FAIL `others.count colocated=0 not> plain=0`; committed PASS 5/5 | PASS 5/5 | FAIL detail=`others.count colocated=0 not> plain=0` | yes |

Failures are case-local, never id-set mismatches: every failing run prints `selftest=FAIL ids=7/7 missing=[] extra=[] failed_verdicts=1`. Green-arm case lines (extended): `linked-common-dir … rc=0 common_entries=53 private_entries=9 checks=8 control=PASS verdict=PASS` and `colocated-vs-plain … others_plain=0 others_colocated=2 commits_plain=1 commits_colocated=2 differing_keys=8 precondition=colocated-not-interchangeable-with-plain-baseline verdict=PASS` — byte-identical to the ExecC3 receipt.

## Hash binding verification
- Committed fixture: HEAD blob `39b488a69e4ecd5fe74fcb4c3cebaf553d611688`, sha256 `b6bf52056d037b2251632b409be3d31852588480c392ddc50ca8f8dbf101179f` — EXACT match to `c3-control-base.tsv` `tool_sha256=` (receipt v1, rev a6d2d157…, rc=0, ids=5/5) and to W1's `b6bf5205…179f`.
- Extended fixture: sha256 `eabc5f0ac56ea3db9f6f68d2dfeadbc91f592eb68c3691d2eabbd5b8347e2c13` — EXACT match to W1's draft hash; `git diff --stat` vs HEAD = 242 insertions/7 deletions, matching W1's claim.
- Probe blob at HEAD `0f42ebf5afac31e8dbddfc67de6b30ef96e4806c` — matches W1.
- Mutants rebuilt from the receipt's generator: sha256 m1 `fb99eae951f1adc14d1a4a9a186c21930db2786b3208c94c7d9af382bd1048e5`, m2 `b2e13b45dbfefb3be7882628349043b702cefdeb6ff710511068dc68539b0423`, m3 `2b676341d1edbe3b5a5e32ae54b685d0e294d45b4476bb097cc3a1ed3494fc97`, m4 `c7248cb6d536075dffeec3f5c28a52d3767807ffddf5d089569a986b4609f718`, m5 `433e44f495e34b329fab4cc10cf94ac4049e81f4914978072e6046336c9c5a23`.

## Findings
1. **Red-arm receipts are truthful and complete.** All five mutants reproduce the table rows on both fixtures; the two amendment-3 mandatory arms (m4 misreport, m2 common-dir write) FAIL the extended fixture exactly as required. Eight (5×2) red-arm executions, no drift. No missing red arm found — the only arm absent from W1's table would be a mutant class the extended fixture does not kill, and none exists. m1-noop is the always-zero control; it kills both fixtures (5/5 and 7/7 fail) as expected.
2. **The working-tree fixture path is currently the EXTENDED draft, not the old fixture.** `tests/fixtures/r13-repo-structure.sh` is `M` in `git status --porcelain`; its bytes equal the W1 draft (`cmp` IDENTICAL, sha256 eabc5f0…). The old 5-case fixture exists only as HEAD blob `39b488a69e4e…` (index still pins it). Anyone re-running the "old fixture passes 5/5 false green" receipt against the working-tree path will instead observe the extended fixture REJECTING m2–m5 — a false alarm if read as a receipt failure. The red-arm receipts are therefore verified against the committed bytes (`git show HEAD:`); the pre-data receipt `c3-control-base.tsv` remains valid and reproducible.
3. **Mutant hashes are absent from the W1 receipts.** The receipt binds fixture hashes exactly (verified) and pins mutant *behavior* via the generator + result rows; it does not record mutant byte hashes. My rebuilt mutants match all behaviors byte-for-byte in output, but byte-identity with W1's originals is unverifiable from the receipt alone. This is a documented verification gap, not a mismatch.

## Attack log
- A1 (misroot guard): no lane/fleet writes; only scratch and this report; scratch removed.
- A2 (stale-path hazard): guarded by using `git show HEAD:` for the old fixture (Finding 2).
- A3 (mutation timing): mutants mutate after the probe returns but before output is emitted, i.e. between manifest-before and manifest-after; confirmed by the observed deltas (m2/m3) — the red arms exercise the intended window.

## Residual risk
- Byte-identity of W1's original mutant files cannot be confirmed (no hashes recorded); behavioral equivalence is exact.
- The old-fixture arms depend on committing the extended fixture; until the L1 commits, the working-tree fixture file is the draft (Finding 2).
