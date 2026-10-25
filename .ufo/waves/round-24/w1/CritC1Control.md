# CritC1Control — can a skip-the-work tool pass C1's frozen 8/8? (souji r24 w1)

## Status
STATUS: PASS — attack completed. Six of eleven cheaters (built from the frozen case text) pass every tool-facing case (1–6). Cases 7–8 are tool-independent, so those six reach 8/8. Two more reach 8/8 only if the fixture picks a weak manifest or witness order. Case 4's witness only holds on git ≥ 2.46.0, and a leaked `GIT_DIR` env var flips it.

## Evidence
- Lane revision read: HEAD `f9db2181647d91470a724a12d626bd6106805076` (the preregistration commit). `tools/souji-size-census.py` and `tests/fixtures/r24-size-census.py` are absent at this revision. So the scorer below is a mock written from the frozen case text in `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-24/preregistration.txt` (lines 45–61), not from the lane fixture.
- Host: `git version 2.56.0`, Python 3.14.8, `/var/tmp` on btrfs (ns mtimes). Nothing was installed or updated.
- Scratch: `/var/tmp/souji-r24-CritC1Control/`. The scorer is `score.py` (sha256 `e68c2385951591716befdaa4fb74dac6e36d85a5c40b5fc0ff4e6e3ed7646023`). The cheater family is one file, `tools/base.py` (sha256 `6f9015b8b53625905ac5db7a46b4714238e3aacf26b81689a5432d7854ea4df3`): each cheater is a symlink, and the mode is taken from argv[0]. The scratch directory was removed at the end.
- Scorer environment: `HOME=<scratch>/home` (user name only), `GIT_CONFIG_NOSYSTEM=1`, `LC_ALL=C`. Command: `python3 -B score.py tools/<mode>.py ...`, about 4 s for all modes.
- Each case where the prereg requires "manifest unchanged" was scored under four manifest variants:
  - `files`: regular files only, mtime_ns + sha256.
  - `dirs_s`: all entries plus the `.git` root, mtime in integer seconds.
  - `dirs_ns`: the same, with mtime_ns.
  - `ctime`: dirs_ns + ctime_ns. This one is diagnostic only, because the prereg excludes ctime.
- Extra probes outside the frozen set:
  - X4: linked worktree on a repo that has real pack junk; expected `garbage=1`.
  - X3: a 4096-byte junk file; expected `size_garbage=4`.
  - X9: a path that is not a repository; expected exit 2.
  - X5: an alternates file pointing at a missing directory (git writes other stderr); expected exit 1.

Scorecard (PASS/FAIL per frozen tool case; output excerpts are from the runs above):

| cheater (mode) | what it skips | 1 | 2 | 3 | 4 | 5 | 6 | frozen result | killed by |
|---|---|---|---|---|---|---|---|---|---|
| `stub` | runs no git, always prints zeros | P | F | F | P | F | F (rc 0/0) | killed | 2, 3, 5, 6 |
| `stubargp` | zero stub + argparse | P | F | F | P | F | F (`--lost-found`=2, partial=0) | killed | 2, 3, 5, partial half of 6 |
| `naive` | `git -C PATH count-objects -v`, no common-dir discount | P | P | P | F (`garbage=1`) | P | P | killed | 4 only |
| `loose` | last `garbage: (\d+)` match, which is the size-garbage value | P | P | F (`garbage=0`) | P | P | P | killed | 3 only |
| `loosefirst` | first match used for both keys | P | P | P (`size_garbage=1`, real value 0) | P | P | P | **8/8** | none (X3) |
| `sgzero` | hardcodes `size_garbage=0` | P | P | P | P | P | P | **8/8** | none (X3) |
| `linkzero` | forces `garbage=0` when `.git` is a file | P | P | P | P | P | P | **8/8** | none (X4 gives `garbage=0`) |
| `nowarn` | drops stderr checks and `census.warning=` lines | P | P | P | P | P | P | **8/8** | none (X5 gives rc 0) |
| `lostfound` | `fsck --lost-found`, counts files, then `rm -rf lost-found` | P | P* | P | P | P | P | **8/8 with `files` or `dirs_s`** | case 2 only with `dirs_ns` |
| `lostfound_utime` | the same, then restores the `.git` mtime with `os.utime` | P | P | P | P | P | P | **8/8 with every frozen-compliant manifest** | only `ctime`, which the prereg excludes |
| `rmdirfix` | deletes `<common>/worktrees/<id>/refs`, then reads `-C` | P | P | P | P† | P | P | **8/8 if the witness is read before the tool** | case 4 if the witness is read after the tool (`before=1 after=0`) |
| `honest` (reference) | nothing | P | P | P | P | P | P | 8/8 | — (X3/X4/X5/X9 all PASS) |

\* `lostfound`, case 2: `manifest=files:same,dirs_s:same,dirs_ns:CHANGED,ctime:CHANGED` in 10 of 10 repeats. The `dirs_s` variant missed the write all 10 times, because the repo is built within the same second as the tool run.
† `rmdirfix`, case 4: `manifest=files:same,dirs_s:CHANGED,dirs_ns:CHANGED`. Case 4 has no manifest predicate, so this change is not scored.

Witness and environment probe (scratch repo `a` + `git worktree add --detach ../wt`; repo `other` holds one dangling blob and a 4 KiB junk file):
```
--- real user env witness:                garbage: 1
--- GIT_CONFIG_GLOBAL=/dev/null NOSYSTEM:   garbage: 1
--- GIT_DIR=a/.git leaked:                  garbage: 0
--- GIT_COMMON_DIR leaked:                  garbage: 1
--- honest tool on a/ with GIT_DIR=other leaked:
garbage=1 size_garbage=4 unreachable=1 alternates=0   rc=0
--- honest tool on a/ clean env:  garbage=0 size_garbage=0 unreachable=0 alternates=0
--- rmdir worktrees/wt/refs then raw: garbage: 0   (git status does not recreate refs/)
```

Git source (`curl -sSfL https://raw.githubusercontent.com/git/git/<tag>/...`, accessed 2026-10-25):
- `builtin/worktree.c` sha256 values:
  - v2.44.0 `14e831a6…`
  - v2.45.0 `8c55ac41…`
  - v2.56.0 `af2bd523e1c89e33d5e370941321fa3c3567c50cf44104e2b502f009e298babc`
- `refs/files-backend.c` v2.56.0 sha256 `430c0cc19e0355b8ebbc459d68fbd9eccc041d82d42b94718e079f0a9943b7ca`.
- `grep -c create_on_disk builtin/worktree.c`: 0 at v2.44.0 and v2.45.0; 1 at v2.46.0, v2.47.0, v2.48.0, v2.49.0, v2.50.0 and v2.56.0.

## Findings
1. **The case-8 stub dies, but cheaper partial cheats survive.** The always-zero stub fails cases 2, 3 and 5, and case 6 when it has no argparse. So `control=FALSE-GREEN-REJECTED` is sound for the stub. But the `--lost-found` half of case 6 comes free with argparse: unknown argv exits 2. Only the partialClone half discriminates. (Prereg line 55: "extra argv `--lost-found` -> exit 2; partialClone repo -> exit 2; manifest unchanged in both.")
2. **`size_garbage` is never discriminated (missing case).** Case 1 expects all zeros, and the case-3 junk does not need to be ≥1 KiB. So `sgzero` and `loosefirst` (which reports `size_garbage=1` for 5 bytes of junk) score 8/8. The only per-key predicates are garbage, unreachable and alternates (prereg lines 50–54).
3. **Case 4 cannot tell "common-dir figure" from "zero on linked" (missing case).** The contract says "count-objects runs against the resolved COMMON git dir, so a linked worktree path reports the common-dir figure" (prereg lines 39–40). Case 4's common dir holds no real garbage, so `linkzero` passes. X4 (linked worktree plus real pack junk, expected `garbage=1`) kills it, but X4 is not in the frozen set.
4. **Case 4 admits a destructive "fix".** `rmdirfix` removes the private `refs/` (the exact causal mechanism) and then reads raw `-C`. It passes because case 4 has no manifest predicate and does not fix the witness order. This is a write inside `.git` by a hygiene-lane census tool, which is the failure class the HARD BOUND exists for. Reading the witness after the tool kills it (`after=0`).
5. **The manifest is only as sensitive as the fixture makes it.** The frozen text is "manifest (sorted path+type+mode+size+mtime+sha256 of regular files; atime/ctime excluded)" (prereg lines 47–48). Results by implementation:
   - Regular files only: misses `fsck --lost-found` followed by cleanup.
   - Directories with integer-second mtime: missed 10/10.
   - Directories with mtime_ns, root included: caught 10/10.
   - Case 7's detector does not force directory entries: it leaves `lost-found/other/<oid>` in place, which even a files-only manifest sees. So case 7 passing does not show that transient writes are visible.
6. **The utime-restore cheat is undetectable under the frozen predicate.** `lostfound_utime` restores `.git`'s mtime with `os.utime`. Every frozen-compliant manifest then reads "same". Only ctime_ns, which the prereg excludes, changes. This is a limit of the frozen predicate, not a fixture defect.
7. **The stderr contract is untested.** "`warning: garbage found:` stderr lines are expected and passed through as census.warning= lines; any other stderr is a failure" (prereg lines 40–41). No case checks for a `census.warning=` line or for exit 1 on other stderr, so `nowarn` scores 8/8 (X5: rc 0). Exit 2 for "not a repository" is also untested (X9). I did not test the promisor-only partial-clone form (`remote.<r>.promisor` without `extensions.partialClone`).
8. **Case 4's witness depends on the host's git version.** In the source, the private `refs/` dir comes from `ref_store_create_on_disk`. `builtin/worktree.c` first calls it at v2.46.0:
   - [v2.46.0 line 512](https://github.com/git/git/blob/v2.46.0/builtin/worktree.c#L512): "ret = ref_store_create_on_disk(wt_refs, REF_STORE_CREATE_ON_DISK_IS_WORKTREE, &sb);"
   - The same call is at [v2.56.0 line 557](https://github.com/git/git/blob/v2.56.0/builtin/worktree.c#L557). It is absent at v2.44.0 and v2.45.0.
   - The files backend creates the dir unconditionally. [refs/files-backend.c v2.56.0 line 3667](https://github.com/git/git/blob/v2.56.0/refs/files-backend.c#L3667): "We need to create a "refs" dir in any case so that older versions of".
   - [INFERENCE, not executed: no older git binary on this host] On git ≤ 2.45.x, `worktree add` does not create the dir. The witness then reads `garbage: 0`, and case 4 fails even when the tool is correct.
   - On 2.56.0 the witness is stable across the real user config and an empty one (`GIT_CONFIG_GLOBAL=/dev/null`). The reftable result comes from sibling `ProbeLinkedModes.md`.
9. **A leaked `GIT_DIR` flips the witness and redirects the tool.** With `GIT_DIR=<common>` set, the raw witness reads `garbage: 0`. With `GIT_DIR=<other repo>` set, even the honest tool counted the other repo and exited 0 (`garbage=1 size_garbage=4 unreachable=1`). This is an operability risk, for example when the fixture or a landing gate runs from a git hook. `GIT_COMMON_DIR` alone did not flip the witness.

## Attack log
Impacted axes:
- coverage (C1): 8/8 would not certify `size_garbage`, the linked common-dir figure, the stderr contract or a no-write envelope.
- calibration: an 8/8 claim would overstate what was verified.
- operability: `GIT_DIR` leak (finding 9) and git-version dependency (finding 8).

| # | counterexample | type | smallest safe correction |
|---|---|---|---|
| A1 | `lostfound` passes with a files-only or seconds manifest | fixable fixture defect, inside the freeze | Manifest every entry under the `.git` common dir (dirs and symlinks too, root included) with `st_mtime_ns`, never seconds or floats. |
| A2 | `rmdirfix` passes when the witness is read first | fixable, inside the freeze (the order is unspecified) | Read the raw `-C <linked>` witness after the tool run (or before and after) and require `garbage: 1` after. |
| A3 | `GIT_DIR` leak flips the witness and redirects the tool | fixable, inside the freeze | Fixture and tool run git with a scrubbed env: drop every `GIT_*` variable except `GIT_CONFIG_NOSYSTEM`, and set `HOME` to scratch and `LC_ALL=C`. |
| A4 | git < 2.46 makes case 4 fail with a correct tool | host dependency | Fixture checks `git --version` ≥ 2.46.0 first and prints a distinct precondition failure, so the result is not scored as a tool defect. Disclose the dependency in the F2 entry. |
| A5 | `sgzero` and `loosefirst` reach 8/8 | missing case; frozen set | Not addable once any seat has scored (prereg kill rule, lines 69–70). If no seat has scored, the fixture may use ≥1 KiB junk in case 3 and assert the full counts line. Otherwise, disclose "`size_garbage` unverified" in the C1 receipt and knowledge entry, and preregister it for r25. |
| A6 | `linkzero` reaches 8/8 | missing case; frozen set | Disclose "common-dir figure on linked worktree unverified beyond zero"; preregister X4 for r25. |
| A7 | `nowarn` reaches 8/8 | missing case; frozen set | Disclose; preregister a `census.warning=` assertion on case 3 plus X5 and X9 for r25. |
| A8 | `lostfound_utime` is invisible to every frozen manifest | tradeoff of the frozen predicate (ctime excluded); the judge must not read 8/8 as a proven no-write envelope | r25: include `st_ctime_ns` for directories, or run the tool against a read-only `.git` (`chmod -R a-w`, taken before the before-manifest). |

Note for the scorer: cases 7 and 8 pass for any `--tool` when the fixture is correct, so `pass=8` means exactly six tool-facing cases passed.
