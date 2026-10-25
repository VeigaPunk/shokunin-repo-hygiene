# RevC2Envelope — W2 review of the r24/r25 size-census no-write envelope

Seat: `L1Souji25.RevC2Envelope` (leaf reviewer; no subagents, no edits, no lane writes beyond this report).
Assignment: independently inspect `tests/fixtures/r24-size-census.py` `manifest()` and cases 11/12;
validate the exact no-write envelope (atime/ctime exclusion, content hashing, directory mtimes,
transient files, xattrs, ownership); correct README/lesson statements that overclaim (report only).

## Status

STATUS: PARTIAL. Every disclosed limit in `corpus/README.md` and the knowledge entries holds under
inspection and under empirical probe; no live README/lesson statement overclaims. Two wording/
behavior mismatches were found in the fixture/amendment contract, one of them an empirically
falsified claim in the fixture docstring (`resolve_alternates` relative-path rule), plus one
undisclosed manifest corner (same-length symlink retarget). The frozen C2 predicates for cases
11/12 are implemented exactly; the manifest-equality observation is reported but not gated, as the
docstring and README say — the prereg amendment-2 §3 wording says more than the code does.

## Environment and method

- Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Fixture read in full (397 lines,
  sha256 `9c8a512f94d5682efee725dc7ed7519c127fde6a775a038ec3292374970bd528`, identical to the w1
  receipt fixture cited by `RevC2RedArm`). Host git 2.56.0. Python `python3 -B`.
- Scratch: `/var/tmp/souji-r25-RevC2Envelope/` (probe1/manifest-matrix, probe1b/symlink,
  probe2/alternates, dbg/diagnostic). Removed at the end. No tool installs; no lane/git/jj
  mutations.
- The fixture itself was not re-run (it hardcodes `SCRATCH_PARENT='/var/tmp'`, outside this seat's
  named scratch); its full 12-case execution was already re-run this wave by
  `RevC2RedArm` (red arms, byte-identical receipts) and by the w1 receipts.

## 1. `manifest()` — claim vs tested behavior

Fixture docstring lines 5–10 claim: "Manifest = sorted (relpath, type, mode, size, mtime_ns,
sha256 of regular files) over the resolved common git dir, directories included; atime/ctime
excluded." Code (`:114-129`): `os.lstat` per node; kind d/f/l/o; `stat.S_IMODE(mode)`,
`st_size`, `st_mtime_ns`; sha256 of regular files only via `read_bytes()`; recursion into
directories only (`kind == 'd'`); sorted rows. Atime and ctime are not read. Verified by probes on
a synthetic gitdir-shaped tree (btrfs `/var/tmp`, ns mtimes):

| # | mutation | detected | envelope claim |
|---|---|---|---|
| 1 | atime bump only (`os.utime` ns) | no | atime excluded — TRUE |
| 2 | `os.chown(f, uid, gid)` same values (ctime bumped; uid/gid not recorded) | no | ctime/ownership excluded — TRUE |
| 3 | `os.setxattr(..., 'user.souji.test')` (xattr added; ctime bumped) | no | xattr invisible (covered only via ctime exclusion) |
| 4 | content rewrite, same size | yes (sha256) | content hashing — TRUE |
| 5 | content rewrite, size change | yes | size+hash — TRUE |
| 6 | `chmod 600→640` | yes (mode) | mode captured — TRUE |
| 7 | transient file create+delete (parent dir mtime left bumped) | yes (dir row) | directory mtimes detect transient writes — TRUE |
| 8 | transient file create+delete, parent dir mtime restored | no | disclosed blind spot — TRUE |
| 9 | new persistent file | yes | TRUE |
| 10 | delete file | yes | TRUE |
| 11 | symlink retarget same length + restored symlink and parent mtimes | no | undisclosed corner (no target hashing) |
| 12 | symlink retarget different length | yes (size) | TRUE |

Tested facts 1–10 confirm every disclosed limit verbatim. Fact 11 is a corner the manifest does
not claim to cover and no README/lesson statement claims either; it is recorded for completeness
(symlink targets are never content-hashed; only lstat metadata is captured).

## 2. Case 11/12 vs the frozen predicates

Prereg C2 (`:70-73`) and the extended fixture (`:316-338`) agree exactly:

- Case 11 `subdir` — calls `s.invoke(tool, s.common_dir(repo), '--repo', sub)` with `sub` inside
  the worktree; expects rc=2 and stderr containing `--repo must name the repository itself`.
  Implementation: `return code == 2 and named` with `named = '--repo must name the repository itself' in err`.
  Tool text (`tools/souji-size-census.py:150-152`): `f"--repo must name the repository itself ({top}), "
  "not a directory inside or below it"` — substring matches. ✓
- Case 12 `partialClone-only` — sets `extensions.partialClone=origin`, asserts no `.promisor` pack
  and no `remote.*` config (setup guards raise `RuntimeError` on violation), expects rc=2 and stderr
  containing `partial-clone repository`. Tool text (`:162-164`): `"partial-clone repository (extensions.partialClone="` — ✓.
- Both cases report `manifest_changed` (via `describe_full`) but do not gate on it; matches docstring
  `:10` "cases 10-12 report manifest_changed but do not gate on it (not in the frozen r25 C2
  predicates)" and README `:544` "the r25 fixture checks exit/stderr but not manifest equality on
  cases 11–12". ✓
- Case 10 `bare-empty` expects rc=1, stderr containing `git failure` and `No default references`,
  no counts line. Tool path: `checked()` fails on `fsck` stderr (`notice: No default references`)
  → `GitFailure` → `main()` writes `git failure: …` to stderr and returns 1 before any counts
  output (`:116-120,224-234`). ✓

## Findings (ordered by severity)

1. **Falsified docstring claim — `resolve_alternates` relative-path rule.** Fixture docstring
   `:7-9` says the alternate manifest is "(resolved per git's alternates rule)". The code
   (`:132-145`) resolves relative lines against `objects/info/` (`info / path`). Empirical probe
   (git 2.56.0, this host): with `objects/info/alternates` containing `alts/objectsdir`, `git
   count-objects -v` reports the alternate at `objects/alts/objectsdir` — i.e. **git resolves
   relative alternates lines against the object database `$GIT_DIR/objects`**, not `objects/info/`.
   The fixture's relative branch is therefore wrong whenever a relative line appears. **Not
   exercised by the frozen set**: case 5 (`alternates`) writes an absolute line
   (`str(s.common_dir(alt) / 'objects')`), so the current 12/12 result is unaffected. Latent
   correctness bug + inaccurate docstring phrase. (Tested fact; source of the rule: observed git
   behavior on this host, `count-objects -v` `alternate:` line + `cat-file -t` resolution.)

2. **Amendment-2 §3 overstates the implementation.** Verbatim: "Cases 11 and 12 freeze rc +
   stderr only in the prereg; the implementing fixture adds an unchanged-manifest condition to
   both, disclosed in the report." The landed fixture adds no manifest *condition* (no gate); it
   adds a manifest *observation* (`manifest_changed=`), consistent with the docstring and README
   `:544`. If "condition" meant the report line, the sentence is satisfied; if it meant a gate,
   the implementation does not match the amendment. The frozen predicates (rc+stderr) are met
   either way — report-only, no edit.

3. **Ownership/xattr invisibility is disclosed only implicitly.** README `:544` discloses
   "atime/ctime are excluded"; chown and `setxattr` both bump ctime, so those writes are invisible
   by that same exclusion (probes 2–3). uid/gid and xattrs themselves are not recorded. No live
   statement overclaims coverage, but an explicit "(ownership and xattr changes are also invisible,
   as they only touch ctime/uid/gid)" would make the limit exact. Recommendation only.

4. **Undisclosed corner: same-length symlink retarget.** Probe 11: retarget a symlink to a
   same-length target and restore the link's and parent directory's mtimes → delta = 0. Git does
   not do this to its own gitdir in any tested path; no statement covers it; recorded for the
   envelope's exactness.

5. **Historical row tension (not a live overclaim).** `README.md:517` (r24 F2 row) still reads
   "the counter does not cover an `extensions.partialClone`-only repo or bare/subdirectory inputs
   (the tool refuses or handles them)". The r25 row `:544` supersedes it and states the counter
   now covers those surfaces; `:540` declares the older status prose "stays as history". The stale
   sentence is visible without an appended superseded pointer (unlike `:40`); if any automated
   coverage reader scans status prose, this pair could look contradictory. Q56/C1 read entries
   cells only, so no gate failure.

## 3. README/lesson statements checked — none overclaim

- `corpus/README.md:544` limits: "the r25 fixture checks exit/stderr but not manifest equality on
  cases 11–12; atime/ctime are excluded; content changes remain detected by hashes, but transient
  byte-identical writes/deletes with restored directory mtime can escape. No size baseline,
  deletion authority, or F2 promotion to Core is claimed." — every clause verified (probes 1–10,
  case code).
- `corpus/knowledge/repo-size-census-readonly.md:84-89` (r24 narrowing): "fences `count-objects
  -v` and `fsck --unreachable --no-reflogs` with a common-dir `.git` manifest and shows `fsck
  --lost-found` writing … Concurrency with another writer is still not established and stays
  owed." — accurate; cases 1–6 gate `not delta`, case 7 gates the detector, case 8 rejects the
  stub; concurrency correctly left unclaimed.
- `corpus/knowledge/git-repo-structure-common-dir.md:49-50`: "Universal write-safety: atime and
  ctime are excluded; a write that restores its own mtime is invisible." — accurate.
- `corpus/lessons/round-24.md:56`: "8/8 is not a proven no-write envelope. An mtime-restoring
  write is invisible because ctime is excluded …" — accurate, already conservative.

## Tested facts vs inference

- Tested (this seat, probes): atime exclusion, ctime/ownership exclusion, xattr invisibility,
  sha256 detection (same-size and size-change), mode capture, dir-mtime transient detection, dir-
  mtime-restored escape, new/delete detection, symlink same-length retarget escape, git's relative
  alternates base (`objects/`).
- Tested (static + `RevC2RedArm` execution this wave): case 11/12 expectations match both the
  frozen predicates and the tip tool's refusal texts; red-arm behavior of the two old blobs.
- Inference: that no git operation ever retargets a gitdir symlink same-length with restored mtimes
  (no case exercises it); that xattr/ownership writes by the tested tool do not occur (the tool
  runs only git subprocesses under the allowlist env; no xattr/chown syscall path exists in its
  source). The manifest's blind spots are therefore theoretical for the tool, but real for the
  fixture's claim precision.

## Residual risk and verification gaps

- The relative-alternates branch of `resolve_alternates` is wrong but unexercised; a future case
  adding a relative line would `error=FileNotFoundError` (manifest over a non-existent dir) rather
  than silently pass — fail-loud, but the wrong path is walked first.
- Any write outside the resolved common gitdir (worktree files, XDG/config, credential helpers) is
  outside the envelope by construction; the tool-side allowlist env is the mitigation, not the
  fixture.
- Cases 11/12 do not enforce manifest equality; a tool that writes to the gitdir while still
  returning rc 2 with the right stderr would pass them (reported, not gated — disclosed in README).
- The `lost-found` detector (case 7) proves git writes are visible; it does not prove non-git
  writes are, beyond the manifest matrix above.

Scratch `/var/tmp/souji-r25-RevC2Envelope/` removed. No tool installs/updates; no lane/git/jj
mutations.
