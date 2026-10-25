# MutDigest — mutation probe on the C1 counter's digest class (class C)

Round 22, attempt 2 (hyaku). Lane: repo/workspace hygiene. Base revision
`4edb25dfe262515d0da63224bbba71e02e36cba5`. Read-only on the lane repo: only
this evidence directory and `w1/MutDigest.md` were written. All fixtures lived
under `/var/tmp` and were removed by the runs' own `finally` cleanup.

Verdict: **KILLED** (by a revision-difference fixture; the frozen `wrong digest`
fixture and the tool's whole 8/8 selftest do **not** kill it).

## Source of the mutated bytes

The task named `.ufo/waves/round-22/attempt2/w1/evidence/impl-a/souji-declared-evidence.py`,
fallback impl-b. At probe start (03:45) **both were absent**:

    ls: cannot access '.ufo/waves/round-22/attempt2/w1/evidence/impl-a': No such file or directory
    ls: cannot access '.ufo/waves/round-22/attempt2/w1/evidence/impl-b': No such file or directory

so the copies were taken from the frozen counter path itself, which is the same
program the preregistration names (`tools/souji-declared-evidence.py`, 14845 B,
mtime 2026-10-25 03:35:01, sha256 `58ddbfef46e08f40c72bc1c4fd7819dacee692f2809cb310de48aced013ae2b2`):

    MutDigest-pristine.py  sha256 58ddbfef46e08f40c72bc1c4fd7819dacee692f2809cb310de48aced013ae2b2
    MutDigest-mutant.py    sha256 4ebf0716ef1294f1f7bc0d676f465ac07e2de8d77bef363fee94d8a39dbab9d6  (mutated)
    MutDigest-mutant.py    sha256 58ddbfef46e08f40c72bc1c4fd7819dacee692f2809cb310de48aced013ae2b2  (after revert)

## The one mutation

Class C (frozen definition: "a 64-hex token in the same cell as exactly one
backticked path -> it must equal sha256 of that path's bytes at `--rev`").
The mutation makes class C hash the **worktree** bytes instead of the bytes at
`--rev`, falling back to the revision blob only when the path is missing from
the worktree — one behavior-bearing point, no other change:

```diff
--- a/tools/souji-declared-evidence.py
+++ b/tools/souji-declared-evidence.py
@@ evaluate(), class C
     if cls == "C":
-        data = repo.blob(a["rev"], a["path"])
+        wt = os.path.join(repo.root, a["path"])
+        data = open(wt, "rb").read() if os.path.isfile(wt) else repo.blob(a["rev"], a["path"])
         if data is None:
             return "mismatch:path-absent", "digest target absent at %s" % a["rev"]
```

The other option offered by the task (compare only length/prefix) was not used:
one mutation only.

## Fixtures (all `/var/tmp`, all removed)

Revision-difference repo, two commits + dirty worktree:

    repo=/var/tmp/mutdigest-8p2yxhp0/repo
    early=12a56d1efa7ac44cefe6be48eb240a578d996a29  late=02ef3690d83ef2114cf06df72393e8f34683f80f
    git status --short: 'M tools/present.sh'
    sha256(committed A) = 306c6ca7407560340797866e077e053627ad409277d1b9da58106fce4cf717cb
    sha256(worktree  B) = f004b40c754174ea11980965e2755c84a77693e27d7bcc874f95f94ecb764cbd
    sha256(git show 02ef369:tools/present.sh) = 306c6ca7...  (== A; worktree differs)

Each declaration is one table cell per the frozen class-C shape:
`| sha256 \`<64hex>\` on \`tools/present.sh\` | measured commit <rev7> |`
(3 assertions each: one class A span, one class C digest, one class B rev token;
the class-C transition is the only thing the mutant can move).

## Observed outputs (same detector on pristine vs mutated bytes)

    [$ F1-revdiff-declared-committed pristine] rc=0  assertions=3 resolved=3 skipped=0 mismatches=0
    [$ F1-revdiff-declared-committed mutant  ] rc=1  assertions=3 resolved=2 skipped=0 mismatches=1
    [$ F2-declared-worktree-bytes    pristine] rc=1  assertions=3 resolved=2 skipped=0 mismatches=1
    [$ F2-declared-worktree-bytes    mutant  ] rc=0  assertions=3 resolved=3 skipped=0 mismatches=0
    [$ F3-frozen-wrong-digest        pristine] rc=1  assertions=3 resolved=2 skipped=0 mismatches=1
    [$ F3-frozen-wrong-digest        mutant  ] rc=1  assertions=3 resolved=2 skipped=0 mismatches=1
    [$ F4-all-good-clean             pristine] rc=0  assertions=3 resolved=3 skipped=0 mismatches=0
    [$ F4-all-good-clean             mutant  ] rc=0  assertions=3 resolved=3 skipped=0 mismatches=0

- **F1** (declared digest = committed bytes, worktree dirty) — pristine is
  correct and green; the mutant goes red. Divergence = kill.
- **F2** (declared digest = the *dirty worktree* bytes) — pristine correctly
  flags `mismatches=1`; the mutant flips to green with `rc=0`. False green = kill.
- **F3** (the frozen `wrong digest` fixture shape, clean worktree) — **identical
  output**; the frozen fixture cannot see this mutant.
- **F4** (all-good, clean worktree) — identical, so the F1/F2 divergence is
  attributable to the worktree/revision difference and not to noise.

## Smallest killing fixture

Substantiated by a second run: one commit, one tracked file, worktree dirtied,
declaration carrying the dirty bytes' digest.

    minimal: 1 commit 4b10621, 1 tracked file, worktree dirty;
             declared digest = sha256(dirty worktree bytes) = 94862798bf9da87e10a2abb45cd2647fd9c59dfcd15e106c5aee5e00de234976
    minimal pristine: rc=1 assertions=3 resolved=2 skipped=0 mismatches=1
    minimal mutant:   rc=0 assertions=3 resolved=3 skipped=0 mismatches=0

Two commits are **not** required to kill it; the requirement is only that the
worktree bytes of the digest target differ from the bytes at `--rev`. The
two-commit shape is what shows the mutant is wrong even when `--rev` is `HEAD`
(F1/F2 both ran at `late` = `HEAD`).

## Survivor evidence (what did not catch it)

The tool's own frozen selftest, both binaries, identical verdicts:

    [$ selftest pristine] rc=0 selftest=8/8
    [$ selftest mutant  ] rc=0 selftest=8/8

All eight lines match, including `fixture4 wrong digest -> mismatch` and
`fixture6 correct digest -> resolved`. Reason: `_fixture_repo()` commits its
last state, so the selftest worktree is clean and worktree bytes == bytes at
`--rev`; class C is exercised only where the two are equal. The frozen C1
selftest therefore has **no fixture whose worktree differs from `--rev`**, and
that gap is exactly the mutant's blind spot.

## Lane-level blindness (bounded finding, source-inferred from measured tsv rows)

The real audited declaration has no class-C instance at either revision:

    lane 4edb25d pristine: assertions=56 resolved=53 skipped=33 mismatches=3
    lane 4edb25d mutant  : assertions=56 resolved=53 skipped=33 mismatches=3
    lane HEAD    pristine: assertions=56 resolved=56 skipped=36 mismatches=0
    lane HEAD    mutant  : assertions=56 resolved=56 skipped=36 mismatches=0

    base-rev rows by class: {'A': 50, 'B': 6}      class-C rows at base: 0
    class-C rows at HEAD: 0
    base-rev mismatch rows: all class A
      line=3  `AXES.md`                        mismatch:path-absent
      line=63 `reason-after.txt`               mismatch:path-absent
      line=77 `.ufo/scopes/souji-mi...`        mismatch:path-absent

Consequence: on the lane's own SCORECARD.md this mutation is undetectable —
there is no digest assertion to mis-evaluate — so a synthetic revision-difference
fixture is the only kill path. Merging that fixture into the tool's selftest is
the fix that would make the frozen kill rule cover class C; the frozen
preregistration is not redefined here.

## Restoration

    before-revert mutant: 4ebf0716ef1294f1f7bc0d676f465ac07e2de8d77bef363fee94d8a39dbab9d6
    after-revert  mutant: 58ddbfef46e08f40c72bc1c4fd7819dacee692f2809cb310de48aced013ae2b2
    MutDigest-pristine.py: 58ddbfef...   tools/souji-declared-evidence.py: 58ddbfef...
    cmp MutDigest-pristine.py MutDigest-mutant.py -> identical

Detector re-run on the restored bytes reproduces pristine behavior:

    dirty-declared (F2-shape):     pristine rc=1 mismatches=1 | mutant-restored rc=1 mismatches=1
    committed-declared (F1-shape): pristine rc=0 mismatches=0 | mutant-restored rc=0 mismatches=0

The lane's tool was never mutated; the lane repo was only read (`--format tsv`,
`--format counts`). Fixtures: `/var/tmp/mutdigest-8p2yxhp0`,
`/var/tmp/mutdigest-min-bltu9dqg`, `/var/tmp/mutdigest-restored-d47n18o1` —
all three reported `exists=False` after removal.

Raw transcript of every run: `MutDigest.raw` (same directory).
