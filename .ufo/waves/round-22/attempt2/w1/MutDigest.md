# MutDigest — C1 digest-class mutation probe

STATUS: PASS

Lane: round 22, attempt 2, repo/workspace hygiene. Base revision
`4edb25dfe262515d0da63224bbba71e02e36cba5`. Read-only on the lane repo; every
fixture under `/var/tmp`, removed by the run's own cleanup; no git/jj writes, no
state/watchdog/MANIFEST/index touched. No tool installed or updated.

## Verdict

**Mutant KILLED** — by a revision-difference fixture. Additional measured
finding: the frozen `wrong digest` fixture and the tool's full 8/8 selftest
both **survive** this mutant unchanged, so the frozen selftest set cannot kill
it.

## Mutation (one, at the smallest behavior-bearing point)

Frozen class C is "a 64-hex token in the same cell as exactly one backticked
path -> it must equal sha256 of that path's bytes at `--rev`". The mutant hashes
the **worktree** bytes instead:

```diff
     if cls == "C":
-        data = repo.blob(a["rev"], a["path"])
+        wt = os.path.join(repo.root, a["path"])
+        data = open(wt, "rb").read() if os.path.isfile(wt) else repo.blob(a["rev"], a["path"])
```

Source of the copied bytes: `impl-a/` and `impl-b/` were both absent at probe
start, so the copies were taken from the frozen counter path itself
(`tools/souji-declared-evidence.py`, 14845 B, sha256
`58ddbfef46e08f40c72bc1c4fd7819dacee692f2809cb310de48aced013ae2b2`):

```
$ ls -d .ufo/waves/round-22/attempt2/w1/evidence/impl-a .../impl-b
ls: cannot access '.../impl-a': No such file or directory
ls: cannot access '.../impl-b': No such file or directory
$ sha256sum tools/souji-declared-evidence.py
58ddbfef46e08f40c72bc1c4fd7819dacee692f2809cb310de48aced013ae2b2  tools/souji-declared-evidence.py
$ sha256sum evidence/MutDigest-mutant.py      # with mutation
4ebf0716ef1294f1f7bc0d676f465ac07e2de8d77bef363fee94d8a39dbab9d6
$ sha256sum evidence/MutDigest-mutant.py evidence/MutDigest-pristine.py   # after revert
58ddbfef...  MutDigest-mutant.py
58ddbfef...  MutDigest-pristine.py
$ cmp MutDigest-pristine.py MutDigest-mutant.py && echo identical
identical
```

## Detector (executed)

Two-commit `/var/tmp` repo with a dirty worktree — `early=12a56d1`,
`late=02ef369`, `git status --short` = `M tools/present.sh`,
`sha256(committed)=306c6ca7…`, `sha256(worktree)=f004b40c…`. Declarations use
the frozen class-C cell shape; each run is
`python3 -B <tool> --root <repo> --file <decl> --rev <late> --format counts`:

```
F1 declared=committed, worktree dirty   pristine rc=0 assertions=3 resolved=3 skipped=0 mismatches=0
                                        mutant   rc=1 assertions=3 resolved=2 skipped=0 mismatches=1
F2 declared=DIRTY worktree bytes        pristine rc=1 assertions=3 resolved=2 skipped=0 mismatches=1
                                        mutant   rc=0 assertions=3 resolved=3 skipped=0 mismatches=0
F3 frozen wrong-digest shape, clean wt  pristine rc=1 assertions=3 resolved=2 skipped=0 mismatches=1
                                        mutant   rc=1 assertions=3 resolved=2 skipped=0 mismatches=1
F4 all-good, clean worktree             pristine rc=0 ... mismatches=0 | mutant rc=0 ... mismatches=0
```

Baseline is green/correct on every fixture, so the F1/F2 divergence is a kill,
not an inconclusive baseline failure. F1 = mutant loses a resolved digest;
F2 = mutant **flips to `rc=0`** on a declaration that does not match the bytes
at `--rev` (false green).

## Smallest killing fixture (executed)

One commit, one tracked file, worktree dirtied, declaration carrying the dirty
bytes' digest (`rev=4b10621`, declared
`94862798bf9da87e10a2abb45cd2647fd9c59dfcd15e106c5aee5e00de234976`):

```
pristine rc=1 assertions=3 resolved=2 skipped=0 mismatches=1
mutant   rc=0 assertions=3 resolved=3 skipped=0 mismatches=0
```

Two commits are not needed to kill it; the only requirement is that the digest
target's worktree bytes differ from its bytes at `--rev`.

## Survivor evidence (what did not catch it)

```
$ python3 -B <pristine> --selftest  -> rc=0 selftest=8/8
$ python3 -B <mutant>   --selftest  -> rc=0 selftest=8/8
```

All eight lines are byte-identical, including `fixture4 wrong digest ->
mismatch` and `fixture6 correct digest -> resolved`. Source-inferred cause
(located in `_fixture_repo`, read): the selftest commits its last state, so the
worktree equals `HEAD` and worktree bytes equal the bytes at `--rev`; class C is
only ever exercised where those two agree. **Coverage finding:** the frozen C1
selftest has no worktree-vs-`--rev` fixture, which is precisely this mutant's
blind spot.

## Lane-level blindness (measured tsv rows)

```
lane 4edb25d pristine assertions=56 resolved=53 skipped=33 mismatches=3
lane 4edb25d mutant   assertions=56 resolved=53 skipped=33 mismatches=3
lane HEAD    pristine assertions=56 resolved=56 skipped=36 mismatches=0
lane HEAD    mutant   assertions=56 resolved=56 skipped=36 mismatches=0
base-rev rows by class: {'A': 50, 'B': 6}; class-C rows at base: 0; class-C rows at HEAD: 0
base-rev mismatch rows: line=3 AXES.md, line=63 reason-after.txt, line=77 .ufo/scopes/... (all class A)
```

SCORECARD.md carries no class-C assertion at either revision, so this mutation
is undetectable on the lane's own declaration — a synthetic revision-difference
fixture is the only kill path. Merging one into the tool's selftest is the
coverage fix (not applied here; the frozen preregistration was not redefined).

## Restoration

`MutDigest-mutant.py` restored to the pristine bytes and re-measured:
`dirty-declared` → rc=1/mismatches=1 and `committed-declared` → rc=0/mismatches=0,
identical to pristine. Accurate hashes before/after are in `evidence/MutDigest.md`;
the lane's `tools/` was never mutated.

## Artifacts

- `.ufo/waves/round-22/attempt2/w1/evidence/MutDigest.md` — full probe record
- `.ufo/waves/round-22/attempt2/w1/evidence/MutDigest.raw` — raw run transcript
- `.ufo/waves/round-22/attempt2/w1/evidence/MutDigest-pristine.py` — copy, sha `58ddbfef…`
- `.ufo/waves/round-22/attempt2/w1/evidence/MutDigest-mutant.py` — reverted, sha `58ddbfef…`

Nothing outside `evidence/` was created in this lane; all three `/var/tmp`
fixture trees reported `exists=False` after removal.
