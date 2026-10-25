# ScoutC2Probe (seat L1Souji25.ScoutC2Probe-2) — C2 size-census refusal surfaces recon

## Status
STATUS: PASS — reproduced all four edge behaviors at tip a6d2d15. The current fixture prints cases=8 pass=8 and has no bare, subdir or partialClone-only case. Two ATTACKS: (1) the named red-arm blob 1efe406 is discriminated ONLY by case 11, not by the bare cases. (2) The committed C2 before-receipt's stdout is not a verbatim run of the fixture it hashes.

## Evidence
Environment: git version 2.56.0; scratch /var/tmp/souji-r25-ScoutC2Probe-2/ (seat-unique name, removed). Lane HEAD 6e4737eab43d8fde1b85eb9f57023d29046705b4; the working-tree tool equals a6d2d15 (`git diff --quiet a6d2d15 -- tools/souji-size-census.py` succeeded).

Blob hashes (sha256), extracted with `git show <rev>:tools/souji-size-census.py`:
- tip a6d2d15 = c5690681b4e86afd4a2a019847c8d18315cea51c2d58d67b3cbc1260143a6eb3 (same as committed tools/).
- old 1efe406 = 7ad5cc763b346c8d13b20d53e56a8e2986a395425ac94201d79bd896912f4578.
- mid 778747e (778747eb671f8e85ef5387bc3d7023337b30467c, the after-state that carried the R24-M24 bare regression) = 09bb8e0d9906b0dfef44775a9e5cd7c8f8a27d9bcdf559e2d371a3ef7ff1ed6d.

Probe script (scratch `probe.sh`). Isolated HOME, GIT_CONFIG_NOSYSTEM=1, GIT_CONFIG_GLOBAL=/dev/null. The manifest is `find -printf '%P %y %m %s %T@'` over the git dir. The four setups:
- bare-nonempty: `git init --bare` + hash-object + mktree + commit-tree + update-ref refs/heads/main.
- bare-empty: `git init --bare`.
- subdir: worktree `wt/` with tracked `wt/sub/f`; the probe runs with `--repo wt/sub`.
- partialClone-only: init + one commit + `git config extensions.partialClone origin` (core.repositoryformatversion=0, 0 .promisor packs).

| case | tip a6d2d15 | old 1efe406 | mid 778747e |
|---|---|---|---|
| bare-nonempty | rc=0, `census.invoked_from=bare`, `garbage=0 size_garbage=0 unreachable=0 alternates=0`, manifest same | rc=0, invoked_from=bare, same counts — **no discrimination** | rc=2 "refused: not a repository: … --show-toplevel exit…" — discriminates |
| bare-empty | rc=1 "git failure: … fsck --unreachable --no-reflogs --no-progress exited 0: notice: No default references", no stdout | rc=1, same diagnostic — **no discrimination** | rc=2 "not a repository" — discriminates |
| subdir | rc=2 "refused: --repo must name the repository itself (…/wt), not a directory inside or below it" | **rc=0, invoked_from=main, counts line** (censuses the enclosing repo) — discriminates | rc=2, same refusal — no discrimination |
| partialClone-only | rc=2 "refused: partial-clone repository (extensions.partialClone=origin)" | rc=2, same — **no discrimination** | rc=2, same — no discrimination |

Every run left the manifest unchanged. Raw git: `git --git-dir=<empty bare> fsck --unreachable --no-reflogs --no-progress` prints `notice: No default references` and returns git_rc=0. The tool maps that stderr to exit 1.

The current fixture at the tip, run with `python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py` (fixture sha256 373ef1f0a02f8ca11fccd4ff32d8511c1eaaf3ede672c37ed11ef2b10968084f, identical at a6d2d15, 6e4737e and the working tree):
```
CASE 2 dangling PASS exit=0 counts=0,0,1,0 manifest_changed=0 lost_found_dir=False
CASE 3 garbage PASS main[exit=0 counts=1,2,0,0 …] linked[exit=0 counts=1,2,0,0 …]
CASE 6 refusal PASS lost_found_argv[exit=2 counts=none …] partial_clone[exit=2 counts=none …] promisor_unset[exit=2 counts=none …]
cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED   rc=0
```
The same 8-case fixture also scores **8/8 rc=0** against old 1efe406, mid 778747e, and all four mutants below. The fixture source has exactly eight CASES (`tests/fixtures/r24-size-census.py:262-264`). Its only refusal case is `case_refusal`, which covers the `--lost-found` argv, a blobless `--filter=blob:none` clone, and promisor unset (:212-238). It has no bare, subdir or partialClone-only case.

Mutants of the tip blob (scratch only). Each is scored with the 8-case fixture, then with the ExecC2 draft `.ufo/waves/round-25/w1/r24-size-census.py` (sha256 9c8a512f94d5682efee725dc7ed7519c127fde6a775a038ec3292374970bd528):

| mutant | 8-case fixture | draft (12 cases) | killed by |
|---|---|---|---|
| tip (unmutated) | 8/8 | 12/12, rc 0 | — |
| old 1efe406 | 8/8 | 11/12 rc 1 (CASE 11 FAIL exit=0 counts=0,0,0,0) | 11 |
| mid 778747e | 8/8 | 10/12 rc 1 (CASE 9 FAIL exit=2; CASE 10 FAIL exit=2) | 9, 10 |
| no-partialclone (delete the `extensions.partialClone` block) | 8/8 | 11/12 (CASE 12 FAIL exit=0) | 12 |
| no-toplevel (`if os.path.realpath(path) != …` → `if False`) | 8/8 | 11/12 (CASE 11 FAIL exit=0) | 11 |
| notice-ok (tolerate the fsck `notice: No default references`) | 8/8 | 11/12 (CASE 10 FAIL exit=0 stdout_counts_line=True) | 10 |
| bare-label (`return common, "bare"` → `"main"`) | 8/8 | 11/12 (CASE 9 FAIL invoked_from_bare=False) | 9 |

## Findings
1. Expected values for the new cases at tip a6d2d15 (the draft prints exactly these):
   - **9 bare-nonempty**: exit=0; counts=0,0,0,0 (`garbage=0 size_garbage=0 unreachable=0 alternates=0`); `census.invoked_from=bare`; manifest over the bare dir unchanged.
   - **10 bare-empty**: exit=1; no counts line; stderr contains `git failure` and `No default references`; manifest unchanged.
   - **11 subdir**: exit=2; stderr contains `--repo must name the repository itself`; manifest over wt/.git unchanged.
   - **12 partialClone-only**: exit=2; stderr contains `partial-clone repository (extensions.partialClone=origin)`; manifest unchanged.

   Case 12 gives the same result with core.repositoryformatversion=1 (tip rc=2, 1efe406 rc=2, no-partialclone mutant rc=0).
2. Discrimination against the prereg's named red-arm blob 1efe406: **only case 11 discriminates**. Cases 9, 10 and 12 pass on 1efe406. The bare cases discriminate only against 778747e. Location: tool docstring of 1efe406 vs `tools/souji-size-census.py:138-152` (the 315422b split of `--show-toplevel` and the top-level check).
3. Each new case kills exactly one mutant that survives the 8-case fixture. This answers the D3 "tool-clause mutant survivors before/after": 4 survivors before, 0 of these 4 after. Case 12 matters because case 6 cannot kill no-partialclone: its blobless clone is still refused by `remote.origin.promisor` and then by the `.promisor` pack (`tools/souji-size-census.py:167-178`).
4. Tip edge paths that are not frozen cases:
   - `--repo <bare>.git/objects`: rc=2 "must name the repository itself".
   - `--repo <worktree>/.git`: rc=2 "not a work-tree top level".
   - A relative bare path and a symlink to a bare repo: both rc=0, invoked_from=bare.
5. The routed regression is located in the lane's own lesson. `corpus/lessons/round-24.md:59`: "The after-state tool refuses every bare repository with exit 2 "not a repository". This is a regression against `1efe406`". So the regressed bytes are 778747e, not 1efe406.

## Attack log
- **ATTACK A1 (calibration; red arm names the wrong bytes).** The prereg says: "Red-arm: OLD tool blob (1efe406…) run against the EXTENDED fixture must fail >=1 of cases 9–12 (the bare cases discriminate)". Measured on 1efe406: cases 9 and 10 PASS and only case 11 FAILs. The predicate (≥1 of 9–12) is still met, but the parenthetical rationale is false. The frozen red arm therefore never witnesses the routed D2/R24-M24 bare regression the claim exists to cover; that witness is 778747e (fails 9 and 10). Not re-specifying anything: report as-is. The L1 MAY add a disclosed 778747e receipt as non-claim evidence.
- **ATTACK A2 (calibration/integrity; the before-receipt is not verbatim).** `census/round-25/records/c2-control-base.tsv` (commit 6e4737e) cites `tool_sha256=373ef1f0…`, which matches the fixture bytes. But its stdout says: "CASE 2 dangling PASS exit=0 counts=0,0,0,0", "CASE 3 garbage PASS main[exit=0 counts=0,0,0,0" and "promisor_unset[exit=0 counts=0,0,0,0 manifest_changed=0]". These contradict the fixture's own predicates:
  - CASE 2 needs `counts[2] == 1` (:153).
  - CASE 3 needs `counts[0] == 1 and counts[1] == 2` (:164).
  - CASE 6 needs `code_c == 2` (:234).
  - It also prints `counts=None`, where `describe()` emits `'none'` (:134).

  A real run of these bytes at a6d2d15 prints 0,0,1,0, 1,2,0,0, promisor_unset exit=2 and `none`. The final line `cases=8 pass=8` agrees, but the per-case body is not output of this fixture. The L1 was notified by peer message.
- **ATTACK A3 (case 10 pins a defect-shaped behavior).** An empty bare repo is a legitimate census target. git itself exits 0 with only a `notice:`. Case 10 freezes exit 1 on that notice, so a future fix that reports zeros, like the notice-ok mutant, would trip the C2 kill rule. Case 10 also depends on git's notice wording, which is version-specific (only 2.56.0 was observed).
- **ATTACK A4 (wording).** Case 9 says ".git manifest unchanged", but a bare repo has no `.git`; the manifest must be over the bare dir (its common dir). The draft does this. The prereg text is ambiguous.
- **ATTACK A5 (weak predicates).** The prereg's cases 11 and 12 require only rc plus a stderr substring, with no manifest-unchanged clause. That is inconsistent with case 6 (`not delta_*`), so a tool that writes before refusing would pass as frozen. The draft adds `manifest_changed=0`, which is stricter than the frozen text; that is fine if disclosed.
- **ATTACK A6 (coverage gap, minor).** The subdir case covers only a worktree subdir. A mutant that refuses non-bare subdirs but censuses `<bare>.git/objects` as the enclosing repo would survive cases 1–12. [INFERENCE: not built as a mutant; the tip refuses that path (Finding 4).]
- No tool installs or updates were performed.

Scratch /var/tmp/souji-r25-ScoutC2Probe-2/ removed at the end of the run. I used the seat-unique name instead of the assigned /var/tmp/souji-r25-ScoutC2Probe/ to avoid colliding with the live sibling seat L1Souji25.ScoutC2Probe.
