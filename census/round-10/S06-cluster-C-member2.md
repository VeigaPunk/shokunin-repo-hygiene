# Round 10 — S06, cluster C member 2 (nested-.git scope, symlink containment, quarantine root)

Fixture policy: every case builds a fresh fixture under `mktemp -d -p /var/tmp`.
No live fleet path is read or written. Tool under test is only ever pointed at
fixture roots.

## Patch base

Installed (S17) tools measured at:

```
4baa8d955c531fcc73edc6b62021cb9531a31e1baed8aa853ba957b204d1cfc1  souji-verify.sh
ea43bb0f9b9fe96cc26451df1a41d2df97d2d044852f122c987c209b6ec7b7a7  souji-vault-verify.sh
f6f8516c15ab654f7e5f2dc2a7840eef0b53b9f9433e2ff70a64490b35fde68f  souji-quarantine.sh
11bf9cdf8d4f75415b18e046aef0e96215b983f0d5b3ff7842301ff6ac65d381  souji-census.sh
```

Candidates produced by this seat:

```
7733279e1d844528479fd007019fc4c59b57c6b22f7dc3a3eecf0cc575adcf1c  tools/cand-c2-verify.sh
71aad587ec3863ab213a445a49fe9cdd007ec9c88696f93f52def4e26e710c50  tools/cand-c2-vault.sh
919433e5ee64b2da752c69f64a94e0abed55cf596329860a3117dbb3c5b509c3  tools/cand-c2-quarantine.sh
23a89f8bfd016fe2588189d9e57fcd7a59d6917290e2d203ae74e463c35c9ac6  tools/cand-c2-clusterc-selftest.sh
```

## Battery result (same cases, three toolsets)

```
bash tools/cand-c2-clusterc-selftest.sh tools                        installed -> CLUSTERC installed 12 12
bash tools/cand-c2-clusterc-selftest.sh <cand>/tools                 cand      -> CLUSTERC cand      24  0
bash tools/cand-c2-clusterc-selftest.sh <merged>/tools               merged    -> CLUSTERC merged    24  0
C2_STRICT_LABELS=1 bash ... <cand>/tools                             cand      -> CLUSTERC cand-strict 24 0
```

Refusal cases assert the VERDICT (any non-SAFE verdict), not the receipt
label; `C2_STRICT_LABELS=1` re-adds exact-label matching. This matters for
integration: the S15 merged bytes answer the same protected-descendant input
with `NOT-SAFE/secrets-refusal protected-or-unsupported-descendant-refused`
where this candidate says `NOT-SAFE/nested-repo-or-unverifiable`, and the
containment case with `NOT-AUTHORIZED/quarantine-containment
symlink-or-noncanonical-quarantine-path` where this candidate says
`quarantine-root-symlink`. A label-coupled corpus scored those as 7 failures
(17/7); they are label drift on a fail-closed verdict, not unsafe outcomes.

Raw evidence: `census/round-10/S06-installed-clusterc.txt`,
`census/round-10/S06-cand-clusterc.txt`,
`census/round-10/S06-merged-clusterc.txt`,
`census/round-10/S06-selftest-counts.txt`.

## Defects confirmed on the installed (S17) tools

**C2-Q1 (HIGH, containment).** `<repo>/.ufo-quarantine` as a symlink to a
directory outside the repo is followed. `mkdir -p`/`mv`/`rm -rf` then operate
through the link. Two observed outcomes on the same fixture shape:
(a) a normal DELETED run stages the payload in the link target, and a
watchdog sampling the target during the run shows
`outside/<date>/.scratch/c7/old.out` present; (b) the ABORTED path (failing
second check) leaves the payload — including hook-appended tampered bytes —
resting outside the repo at `outside/<date>/old.out`, with the original gone.
A hold-window repoint of the symlink moves the staged bytes to an
attacker-chosen directory. Fixed by refusing any symlink component below the
repo on the quarantine path (`quarantine-root-symlink`).

**C2-Q2 (HIGH, scope scan).** The directory scope scan is
`find . -path './.git' -prune -o \( -name .git -o -name .ufo \) -print -quit`.
The `-prune` matches only a literal top-level `./.git`, so a directory whose
only nested live repository is reachable through a symlinked subdirectory
scans clean and earns `SAFE(pushed)`. Reproduced on both `souji-verify.sh`
and `souji-vault-verify.sh`. The `-type l` case (symlink in scope, dangling
symlink) is likewise invisible. Fixed by refusing when the scan finds a
symlink, nested `.git`, or `.ufo`, and by separating the scan-failure branch
from the found-something branch.

**C2-Q3 (MEDIUM, batch abort).** `pin_sha=$(content_digest "$ct")` under
`set -e` aborts the whole process when `content_digest` returns 2 (symlink in
scope). On a `--list` batch this kills the run mid-stream: rc=2, no SUMMARY,
rows after the poisoned one never reported — while rows before it were already
deleted. Reproduced with a 3-row list: `results=1`, `rc=2`. Fixed by
capturing the status and refusing that row (`symlink-in-scope`); the batch now
completes with `SUMMARY total=3 deleted=2 unauthorized=1`.

## Classes verified CLOSED by S17 (passes, not defects)

Nested `.git` directory; nested `.git` gitfile; relative gitfile; `.git`
symlink to the outer repo; nested repo behind a mode-000 subdir; deep nesting
with a sibling `.ufo`; and the read-only index contract — index digests
unchanged across verify/vault/census with stale stat data, and an absent
`.git/index` is not created by a read-only probe.

## Selftest counts

New regression cases are embedded in each tool's own `--selftest` (the
pattern peer seats use), so the counts below carry them.

```
                      installed            candidate            new
souji-verify.sh       40 checks, 0 failed  44 checks, 0 failed  +4  (C2R01, C2R03, C2R04, C2R08)
souji-vault-verify.sh 51 checks, 0 failed  54 checks, 0 failed  +3  (C2R03, C2R04, C2R08)
souji-quarantine.sh   91 checks, 0 failed  98 checks, 0 failed  +7  (C2R05 x4, C2R07 x3)
souji-census.sh       32 checks, 0 failed  (unchanged, not patched)
r9 battery            verify 16/0 vault 16/0 quarantine 28/0  (identical on candidates)
```

Totals on the candidates: **196 checks, 0 failed** (vs 182 installed), and
all 182 pre-existing checks are still present and passing — no pre-existing
case was traded away for a new one.

## Cross-toolset check on the S15 merged bytes (measured this pass)

S15's own merged-harness figures are cited, not re-derived here (that
harness is S15's artifact and no runner for it is in the tree):

```
installed   verify 18/5   vault 19/4   quarantine 31/5
candidates  verify 18/5   vault 19/4   quarantine 32/4
```

Measured independently on the merged bytes (`tools/cand-merge-*`, staged
lane-shaped) with this seat's corpus:

```
cluster-C safety corpus   merged 24/0      (installed 12/12)
merged selftests          40/51/91, 0 failed  -- i.e. the S17 baseline counts,
                          no cluster-C regression cases embedded
```

So the merge **preserves** cluster-C safety (containment and protected-scope
refusals both fire, `NOT-AUTHORIZED` / `NOT-SAFE`) while minting different
receipt labels, and it carries **no** cluster-C regression cases of its own.
Label drift is the integration hazard; missing embedded cases are the
coverage hazard. Neither is an unsafe outcome, and neither is claimed as a
defect of the merged tool.

The remaining failures in S15's harness (J01 dirty-pushed replacement, J02
hidden live references, J03 ignored directory payload, J05 self-referential
ledger row, J08 unpushed-vetoes-stale) belong to other clusters and are
**not claimed** by this seat.

## Residual limits (honest)

- The `q_symlink_below` walk in the candidate is a TOCTOU-narrowed, not
  TOCTOU-proof, check: it closes the symlinked-root shape and the observed
  hold-window repoint, but a repoint landing exactly between the check and the
  `mkdir`/`mv` is not excluded by construction.
- C2-Q1's outside-write assertion is state-based, not syscall-traced. The
  outside tree is inspected after the run; transient writes that are later
  removed would not be caught. The installed tool's own `rm -rf` is what
  cleans up the link target in the pass case.
- `cand-c2-clusterc-selftest.sh` must be pointed at a toolset staged
  **lane-shaped** (`<stage>/souji-shokunin/tools/`). Staged anywhere else,
  the quarantine live-fleet guard fires: `LIVE_FLEET_ROOT` becomes an
  ancestor of the fixture root, every mutation case returns rc=4
  `live-fleet-mutation-forbidden`, and the corpus reads 19/5 for a candidate
  that is actually 24/0. That refusal is correct fail-closed behavior, not a
  defect; the corpus simply has to be run from a layout whose guard cannot
  fire. The evidence files use `/var/tmp/s06-stage/souji-shokunin/tools`.
- No candidate is promoted here. Promotion, byte re-freeze and certification
  remain the parent's decision; deletion authorization stays OFF.

## Second pass (same seat, independent re-run)

Every number above was re-measured from scratch on fresh `mktemp -p /var/tmp`
fixtures against the frozen installed bytes
(`4baa8d95…` / `ea43bb0f…` / `f6f8516c…` / `11bf9cdf…`), and reproduced:
selftests 44/54/98 (0 failed) with all 182 pre-existing cases retained, the
r9 shared battery at 16/0, 16/0, 28/0, and the cluster-C corpus at
installed 12/12 vs candidate 24/0. The corpus itself was corrected this pass
from label-coupled to verdict-coupled assertions after it mis-scored the
merged bytes; `tools/cand-c2-clusterc-selftest.sh` is now
`23a89f8bfd016fe2588189d9e57fcd7a59d6917290e2d203ae74e463c35c9ac6` and the
candidate tool bytes are unchanged from the first pass.

## Safety

- Fixtures: `/var/tmp` only, all under `mktemp -d -p /var/tmp`.
- Live fleet: not read, not written. `census/round-10/` and `tools/cand-c2-*`
  are the only paths this seat wrote.
- No secret-shaped content read; no GUI launched; no git history mutated.
