STATUS: DONE — tests/fixtures/r17-jj-receipts.sh delivers the revised git-only C3 fixture (J1–J9); worktree arm 20/20 pass, 5fa6017 base arm fails exactly the jj-blind cases (7 FAIL, all SAFE false positives).

# FixtureJjReceipts — r17 wave 1

## Deliverable

`tests/fixtures/r17-jj-receipts.sh` (new, executable, 769 lines, bash; `bash -n` and
`shellcheck -S warning` clean). It implements the L1-revised contract, not the earlier
heads/tags/remotes variant:

- roots contract (a'): durable roots are all refs except `refs/jj/*`; HEAD is never a root.
- pushed-receipt novelty (b'): a keep-only commit refuses only when the blob it introduces at
  the target path is absent from remote history; deletions and already-published
  (metaedit/rebase-predecessor) blobs do not refuse.
- git-only by default: every `refs/jj/keep/<sha>` is synthesized with `git update-ref`; real
  jj is used only by the optional J9 arm.
- every case is measured through the tools' CLIs, so the effective (last-defined) functions
  are the ones exercised.

### Cases and fixed oracles

| id | shape | expected |
|---|---|---|
| J1 | absent worktree registration, head held only by `refs/jj/keep/*` | NOT-SAFE, never SAFE(metadata-prune); evidence carries `unique=N` |
| J1-vault | same via `souji-vault-verify.sh --fallback` | NOT-SAFE, never `VERIFIED(metadata-prune)` |
| J2 | same head also on `refs/heads/side` | SAFE/metadata-prune (vault: `VERIFIED(metadata-prune)`) |
| J3 | pushed file + keep-only commit with novel blob | NOT-SAFE; quarantine `--dry-run` DRY-RUN-BLOCKED or NOT-AUTHORIZED |
| J4 | keep-only commit whose blob equals a blob already in remote history (v2 published, reverted) | SAFE/pushed; quarantine DRY-RUN-PASS |
| J5 | keep-only deletion of the target | SAFE/pushed; quarantine DRY-RUN-PASS |
| J6 | plain repo, no `refs/jj/*`: verify + vault stdout compared `--tool-dir` vs `--baseline-dir` on 4 targets | byte-identical |
| J7 | plain repo, absent-worktree head held only by `refs/stash` | SAFE/metadata-prune (both arms) |
| J8 | `refs/jj/root` + `refs/jj/remote-tags/x`, no keep refs | output byte-identical to the pre-insertion capture; SAFE/metadata-prune and SAFE/pushed |
| J9-file / J9-worktree | optional real `jj 0.45.1` colocated clone: keep-only f.txt v2 | NOT-SAFE / NOT-SAFE (CASE SKIP when jj is absent) |

Scenario preconditions are asserted before any measurement (seed tip/blob pins, keep ref
present, `rev-list --count <c> --not --all` = 0 while `--not --branches --tags --remotes` = 1,
deleted path absent from the deletion commit, v2 f_meta blob present in remote history,
novel f_novel blob absent from it, clean worktree). A broken precondition exits 2 — never a
silent pass. SKIP is counted separately and never as a pass.

## Isolation / safety

One private `mktemp -d /var/tmp/r17-jj-receipts.XXXXXX` (hard-coded base, not caller
`TMPDIR`), guard `case $T in /var/tmp/?*)`, `trap 'rm -rf -- "$T"' EXIT INT TERM HUP`, then
`cd -- "$T"`. HOME, XDG_CONFIG_HOME/STATE/CACHE/DATA, GIT_CONFIG_GLOBAL,
GIT_CONFIG_NOSYSTEM=1, GIT_TERMINAL_PROMPT=0, GIT_CEILING_DIRECTORIES=$T, JJ_CONFIG (own
toml), HYAKU_STATE, TMPDIR=$T/tmp are set before any git/jj call;
GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE/GIT_OBJECT_DIRECTORY/GIT_ALTERNATE_OBJECT_DIRECTORIES/
GIT_COMMON_DIR and JJ_USER/JJ_EMAIL are unset. Every git call is `-C <tmp repo>`, every jj
call is `-R <tmp repo>`; the only remote is a bare repo under $T; the lane's `.jj` is never
copied. `gc.auto=0` and `maintenance.auto=false` are pinned in the scratch global config and
as `-c` on every fixture git invocation.

Sentinel-driven fix applied after the first runs: the `jj --version` probe used to run before
HOME/XDG redirection and before the scratch `cd`, i.e. with cwd = lane. jj 0.45.1 loads the
cwd workspace's repo config on every invocation, so those early runs rewrote the lane's
`.jj/repo/config-id` inodes (observed by SentinelJjFixture at 13:53:46/13:54:55). The
fixture now resolves the jj path without executing it, creates the scratch, `cd`s into it,
isolates HOME/XDG, and only then probes `--version`; all later runs left the lane untouched.
Read-only check after the fix: `.jj/repo/config-id` is a regular 20-byte file, not a symlink;
`.jj/repo/config.toml` does not exist, so no symlink target could have been deleted.

## Commands and outputs

Base tools extracted from the recorded base revision (read-only `git show`):

```
$ B=/var/tmp/souji-r17-FixtureJjReceipts/base/tools
$ for f in souji-verify.sh souji-vault-verify.sh souji-quarantine.sh; do
    git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 5fa6017:tools/$f > "$B/$f"; chmod +x "$B/$f"; done
$ sha256sum "$B"/*.sh
df4075112c36bae804b98766c4eb66b0e5b2b80b76d7333475ede27b06b168c4  .../souji-quarantine.sh
f9e778ca478c7aa8b33234ee793030df631c1b9fcebc942b1ff41d0008ed9c5b  .../souji-vault-verify.sh
9adb17645a5f452ae2cc28673642ad256f9aee92109939531f3c34a0972812cd  .../souji-verify.sh
```

Arm runs (both from `cd /var/tmp`, `env -u TMPDIR`; full captures retained at
`/var/tmp/souji-r17-FixtureJjReceipts/base-arm.txt` and `worktree-arm.txt`):

```
bash tests/fixtures/r17-jj-receipts.sh --tool-dir /var/tmp/souji-r17-FixtureJjReceipts/base/tools \
     --baseline-dir /home/vgpnk/Projects/shokunin/souji-shokunin/tools      # rc=1
bash tests/fixtures/r17-jj-receipts.sh --tool-dir /home/vgpnk/Projects/shokunin/souji-shokunin/tools \
     --baseline-dir /var/tmp/souji-r17-FixtureJjReceipts/base/tools         # rc=0
```

Tool bytes actually executed (worktree bytes changed during the wave as seats landed edits):

```
verify    92743004912a497b5c629515913690bc3096be6f789fc42df46c56d6611bc30f
vault     bbca35a142cb8ee23cd90fd918f0aaa538dc705c90e171825de8b62a1687fb64
quarantine b6e3a19256eceffbead0b12ba1105175414eea098375e6829725b130fe68b78f
```

### Base arm (5fa6017) — CASE table verbatim

```
TOOL-DIR	/var/tmp/souji-r17-FixtureJjReceipts/base/tools
TOOL-BASELINE	/home/vgpnk/Projects/shokunin/souji-shokunin/tools
GIT	git version 2.56.0
JJ	/home/vgpnk/.local/bin/jj	jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5
TOOL	/var/tmp/souji-r17-FixtureJjReceipts/base/tools/souji-verify.sh	sha256=9adb17645a5f452ae2cc28673642ad256f9aee92109939531f3c34a0972812cd
TOOL	/var/tmp/souji-r17-FixtureJjReceipts/base/tools/souji-vault-verify.sh	sha256=f9e778ca478c7aa8b33234ee793030df631c1b9fcebc942b1ff41d0008ed9c5b
TOOL	/var/tmp/souji-r17-FixtureJjReceipts/base/tools/souji-quarantine.sh	sha256=df4075112c36bae804b98766c4eb66b0e5b2b80b76d7333475ede27b06b168c4
TOOL	/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-verify.sh	sha256=92743004912a497b5c629515913690bc3096be6f789fc42df46c56d6611bc30f
TOOL	/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-vault-verify.sh	sha256=bbca35a142cb8ee23cd90fd918f0aaa538dc705c90e171825de8b62a1687fb64
SCENARIO	seed	tip=79db34a1673c	meta_v1=626799f0	meta_v2=8c1384d8
SCENARIO	plain	unref=2cd10b664132	wts=absent
CASE	J6-verify	PASS	targets=/var/tmp/r17-jj-receipts.vHrBva/fleet/plainrepo/f.txt,/var/tmp/r17-jj-receipts.vHrBva/wt-plain,/var/tmp/r17-jj-receipts.vHrBva/wt-plain-unref,/var/tmp/r17-jj-receipts.vHrBva/no-such-target,; identical=yes
CASE	J6-vault	PASS	targets=/var/tmp/r17-jj-receipts.vHrBva/fleet/plainrepo/f.txt,/var/tmp/r17-jj-receipts.vHrBva/wt-plain,/var/tmp/r17-jj-receipts.vHrBva/wt-plain-unref,/var/tmp/r17-jj-receipts.vHrBva/no-such-target,; identical=yes
CASE	J8-verify	PASS	targets=f.txt,wt-plain identical=yes
CASE	J8-vault	PASS	targets=f.txt,wt-plain identical=yes
CASE	J7	PASS	exit=0 verdict=SAFE receipt=metadata-prune evidence=dir=absent unique=0 head=c16edd6da75a owner=plainrepo durable-refs-only=yes
SCENARIO	keeprepo	keep_head=e1e06914	keep_novel=1a059ede	keep_meta=fbc82efe	keep_del=dccd1f32	wts=absent
CASE	J1	FAIL	exit=0 verdict=SAFE receipt=metadata-prune evidence=dir=absent unique=0 head=e1e0691453e3 owner=keeprepo durable-refs-only=yes expected=NOT-SAFE,never-SAFE(metadata-prune)
CASE	J1-vault	FAIL	exit=0 verdict=SAFE receipt=metadata-prune r4=VERIFIED(metadata-prune) expected=NOT-SAFE,never-VERIFIED(metadata-prune)
CASE	J2	PASS	exit=0 verdict=SAFE receipt=metadata-prune evidence=dir=absent unique=0 head=e1e0691453e3 owner=keeprepo durable-refs-only=yes
CASE	J2-vault	PASS	exit=0 verdict=SAFE receipt=metadata-prune r4=VERIFIED(metadata-prune)
CASE	J3	FAIL	exit=0 verdict=SAFE receipt=pushed evidence=intro=cf8393b7b05b ref=refs/remotes/origin/main ancestor=yes snapshot=equal clean=yes expected=NOT-SAFE (keep-only commit carries novel content)
CASE	J3-vault	FAIL	exit=0 verdict=SAFE receipt=pushed r4=VERIFIED(pushed) expected=NOT-SAFE
CASE	J3-quarantine	FAIL	exit=0 result=DRY-RUN-PASS receipt=pushed evidence=stage1=intro=cf8393b7b05b ref=refs/remotes/origin/main ancestor=yes snapshot=equal clean=yes expected=DRY-RUN-BLOCKED|NOT-AUTHORIZED
CASE	J4	PASS	exit=0 verdict=SAFE receipt=pushed evidence=intro=cf8393b7b05b ref=refs/remotes/origin/main ancestor=yes snapshot=equal clean=yes
CASE	J4-vault	PASS	exit=0 verdict=SAFE receipt=pushed r4=VERIFIED(pushed)
CASE	J4-quarantine	PASS	exit=0 result=DRY-RUN-PASS receipt=pushed evidence=stage1=intro=cf8393b7b05b ref=refs/remotes/origin/main ancestor=yes snapshot=equal clean=yes
CASE	J5	PASS	exit=0 verdict=SAFE receipt=pushed evidence=intro=cf8393b7b05b ref=refs/remotes/origin/main ancestor=yes snapshot=equal clean=yes
CASE	J5-vault	PASS	exit=0 verdict=SAFE receipt=pushed r4=VERIFIED(pushed)
CASE	J5-quarantine	PASS	exit=0 result=DRY-RUN-PASS receipt=pushed evidence=stage1=intro=cf8393b7b05b ref=refs/remotes/origin/main ancestor=yes snapshot=equal clean=yes
CASE	J9-file	FAIL	jj=jj keep=5b8b9ed1 verdict=SAFE receipt=pushed expected=NOT-SAFE
CASE	J9-worktree	FAIL	jj=jj keep=5b8b9ed1 verdict=SAFE receipt=metadata-prune evidence=dir=absent unique=0 head=5b8b9ed13123 owner=jjrepo durable-refs-only=yes expected=NOT-SAFE,never-SAFE(metadata-prune)
SUMMARY	total=20	failed=7	skipped=0
```

Base verdict: 7/20 FAIL, all of them SAFE false positives (J1, J1-vault, J3, J3-vault,
J3-quarantine via delegated stage 1, J9-file, J9-worktree). That is the required paired
negative control; the plain-repo controls (J2, J4, J5, J6, J7, J8) pass at base by design.

### Worktree arm — CASE table verbatim

```
TOOL-DIR	/home/vgpnk/Projects/shokunin/souji-shokunin/tools
TOOL-BASELINE	/var/tmp/souji-r17-FixtureJjReceipts/base/tools
GIT	git version 2.56.0
JJ	/home/vgpnk/.local/bin/jj	jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5
TOOL	/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-verify.sh	sha256=92743004912a497b5c629515913690bc3096be6f789fc42df46c56d6611bc30f
TOOL	/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-vault-verify.sh	sha256=bbca35a142cb8ee23cd90fd918f0aaa538dc705c90e171825de8b62a1687fb64
TOOL	/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-quarantine.sh	sha256=b6e3a19256eceffbead0b12ba1105175414eea098375e6829725b130fe68b78f
TOOL	/var/tmp/souji-r17-FixtureJjReceipts/base/tools/souji-verify.sh	sha256=9adb17645a5f452ae2cc28673642ad256f9aee92109939531f3c34a0972812cd
TOOL	/var/tmp/souji-r17-FixtureJjReceipts/base/tools/souji-vault-verify.sh	sha256=f9e778ca478c7aa8b33234ee793030df631c1b9fcebc942b1ff41d0008ed9c5b
SCENARIO	seed	tip=661fa465534f	meta_v1=626799f0	meta_v2=8c1384d8
SCENARIO	plain	unref=48b139cbf6d7	wts=absent
CASE	J6-verify	PASS	targets=/var/tmp/r17-jj-receipts.qHdpTL/fleet/plainrepo/f.txt,/var/tmp/r17-jj-receipts.qHdpTL/wt-plain,/var/tmp/r17-jj-receipts.qHdpTL/wt-plain-unref,/var/tmp/r17-jj-receipts.qHdpTL/no-such-target,; identical=yes
CASE	J6-vault	PASS	targets=/var/tmp/r17-jj-receipts.qHdpTL/fleet/plainrepo/f.txt,/var/tmp/r17-jj-receipts.qHdpTL/wt-plain,/var/tmp/r17-jj-receipts.qHdpTL/wt-plain-unref,/var/tmp/r17-jj-receipts.qHdpTL/no-such-target,; identical=yes
CASE	J8-verify	PASS	targets=f.txt,wt-plain identical=yes
CASE	J8-vault	PASS	targets=f.txt,wt-plain identical=yes
CASE	J7	PASS	exit=0 verdict=SAFE receipt=metadata-prune evidence=dir=absent unique=0 head=0deca3dc3d0f owner=plainrepo durable-refs-only=yes
SCENARIO	keeprepo	keep_head=82935977	keep_novel=c5c4df27	keep_meta=59e5ba62	keep_del=fa0471a5	wts=absent
CASE	J1	PASS	exit=0 verdict=NOT-SAFE receipt=none evidence=dir=absent unique=1 head=829359778c6c owner=keeprepo durable-refs-only=yes
CASE	J1-vault	PASS	exit=0 verdict=NOT-SAFE receipt=none r4=NOT-VERIFIED(none)
CASE	J2	PASS	exit=0 verdict=SAFE receipt=metadata-prune evidence=dir=absent unique=0 head=829359778c6c owner=keeprepo durable-refs-only=yes
CASE	J2-vault	PASS	exit=0 verdict=SAFE receipt=metadata-prune r4=VERIFIED(metadata-prune)
CASE	J3	PASS	exit=0 verdict=NOT-SAFE receipt=none evidence=pushed=unpushed-commits-touching intro=10a4638e14f2 jj-keep-novel; obsidian=no-matching-ledger-row; stale=not-scratch-type
CASE	J3-vault	PASS	exit=0 verdict=NOT-SAFE receipt=none r4=NOT-VERIFIED(none)
CASE	J3-quarantine	PASS	exit=3 result=DRY-RUN-BLOCKED receipt=none evidence=stage1=NOT-SAFE(none)
CASE	J4	PASS	exit=0 verdict=SAFE receipt=pushed evidence=intro=10a4638e14f2 ref=refs/remotes/origin/main ancestor=yes snapshot=equal clean=yes
CASE	J4-vault	PASS	exit=0 verdict=SAFE receipt=pushed r4=VERIFIED(pushed)
CASE	J4-quarantine	PASS	exit=0 result=DRY-RUN-PASS receipt=pushed evidence=stage1=intro=10a4638e14f2 ref=refs/remotes/origin/main ancestor=yes snapshot=equal clean=yes
CASE	J5	PASS	exit=0 verdict=SAFE receipt=pushed evidence=intro=10a4638e14f2 ref=refs/remotes/origin/main ancestor=yes snapshot=equal clean=yes
CASE	J5-vault	PASS	exit=0 verdict=SAFE receipt=pushed r4=VERIFIED(pushed)
CASE	J5-quarantine	PASS	exit=0 result=DRY-RUN-PASS receipt=pushed evidence=stage1=intro=10a4638e14f2 ref=refs/remotes/origin/main ancestor=yes snapshot=equal clean=yes
CASE	J9-file	PASS	jj=jj keep=c2d706a1 verdict=NOT-SAFE receipt=none
CASE	J9-worktree	PASS	jj=jj keep=c2d706a1 verdict=NOT-SAFE receipt=none evidence=dir=absent unique=1 head=c2d706a18416 owner=jjrepo durable-refs-only=yes
SUMMARY	total=20	failed=0	skipped=0
```

## Verdict

holds. Worktree arm: 20/20 pass, 0 skip, rc=0. Base arm: rc=1 with exactly the seven
jj-blind SAFE outcomes, so the fixture discriminates the base from the fix on both the
worktree-roots axis (J1) and the pushed-novelty axis (J3), including through vault-verify,
quarantine's delegated stage 1 and a genuine `jj 0.45.1` colocated clone (J9). Scratch was
removed by the trap (`ls -d /var/tmp/r17-jj-receipts.*` → none).

## Risks / notes for L1

1. Tool bytes changed while this seat worked: verify `ecae83d1…`→`92743004…`,
   quarantine `43a43bd4…`→`b6e3a192…`. An intermediate worktree run against `ecae83d1…`
   failed J3/J9-file (SAFE/pushed) because that verify build had the roots fix but not the
   novelty wiring; the final bytes above pass. Record the sha256 set with any replay.
2. J6 requires `--baseline-dir`; without it J6 prints SKIP and is not a pass (never treated
   as one). The command in the wave matrix should pass both dirs (either direction works).
3. J7 asserts the revised root contract (all refs except `refs/jj/*`, so `refs/stash`
   counts). If a future edit narrows roots back to heads/tags/remotes, J7 fails by design.
4. J9 needs `jj 0.45.1`; when jj is absent J9 prints SKIP with a reason. Version is printed
   in the JJ record (probe happens only after cwd/HOME isolation).
5. The lane `.jj/repo/config-id` inode rewrites reported by SentinelJjFixture came from the
   fixture's first two runs (jj `--version` was probed with cwd = lane before isolation).
   Fixed as described; post-fix runs left the lane untouched. I did not remediate lane state
   (no writes permitted). Current shape: regular 20-byte file, no `config.toml`, no symlink.
6. No packages installed or upgraded; no network writes; no commit/push/jj write in the lane.

Retained evidence: `/var/tmp/souji-r17-FixtureJjReceipts/{base-arm.txt,worktree-arm.txt,base/tools/}`.

---

## Wave-2 addendum (same seat, second round)

Parent fix added six case groups covering the mutation/sentinel/critic survivors.
Fixture grew 20 → 35 case ids; every new case drives the tools' own CLIs.

New cases (implemented at fixture ~:441-703):

- **J10** (`verify`/`vault`/`quarantine`): `KREPO/d` directory target with two keep-only
  predecessors — one byte-identical `d` tree, one tree that re-arranges already-published
  leaf blobs into a never-pushed tree id (built via private `GIT_INDEX_FILE` +
  `update-index --cacheinfo` blob swap). Setup asserts the swapped tree id is absent
  from `rev-list --objects --remotes -- d` but its leaf blobs are present. Expectation:
  **SAFE(pushed)** — discriminates leaf-blob comparison from the tree-id comparison
  (MutateJjNovel M02/M06/M12/M18 and Critic directory cases J10/J11).
- **J11**: same `d` target after a keep-only commit adds `d/z.txt` (novel leaf).
  Expectation: NOT-SAFE / `NOT-VERIFIED(none)` / `DRY-RUN-BLOCKED`.
- **J12**: `BREPO/f_broken.txt`, `refs/jj/keep/<40×f>` names a missing commit; asserts
  `pushed=history-unverifiable` and NOT-SAFE (the rc 2 → history-unverifiable route;
  Sentinel F3 / MutateJjNovel M05/M11/M17 failure-path class).
- **J13**: `BREPO2/f_noncommit.txt` with `refs/jj/keep/<tree-sha>` and `<blob-sha>`
  loose ref files (non-commit objects). `for-each-ref` lists them, `rev-list` ignores
  them; SAFE(pushed) must stand.
- **J14**: `BIGREPO/f_big.txt`, 1200 commits synthesized by `git fast-import` into a
  bare origin then cloned — `rev-list --objects --remotes -- f_big.txt` = 3600 objects
  (>64 KiB), and the keep-only predecessor rewrites the file back to the v1199 blob
  (published, listed late). Expectation SAFE(pushed): the wave-1 per-candidate
  `printf | grep -q` would SIGPIPE under `pipefail` and fabricate a false novel here
  (Sentinel F1/F2 scale threshold).
- **J15**: `KREPO/f_side.txt`, the blob is published only through
  `refs/remotes/upstream/fork` — setup asserts it is absent from
  `rev-list --objects --branches` and present under `--remotes`. The keep-only
  predecessor carries that blob. SAFE(pushed): discriminates the `--remotes` known set
  from a `--branches` mutation.

Fresh runs (tool bytes hashed in the CASE-table headers):

- **Worktree arm** (`verify` sha256=7256666953…, `vault` sha256=5cb0fb13fc…,
  `quarantine` sha256=2fa0fff16a…): `SUMMARY total=35 failed=0 skipped=0`, rc 0.
- **Base arm** (5fa6017: `verify` 9adb1764…, `vault` f9e778ca…, `quarantine` df407511…):
  `SUMMARY total=35 failed=13 skipped=0`, rc 1 — the wave-1 seven plus J11-verify/vault/
  quarantine and J12-verify/vault/quarantine, all returning SAFE on shapes that must
  refuse. J10/J13/J14/J15 pass on base (novelty checking is new code; the negative
  control for them is the mutation probe, not the 5fa6017 arm).
- J6-verify/J6-vault again PASS: plain-repo output byte-identical between the arms, so
  the keep-path additions did not perturb plain repos.

Precondition notes: `git rev-list --glob=refs/jj/keep/*` ignores keep refs that point
at non-commit objects (J13) but exits non-zero on a missing object (J12) — measured,
not assumed. J14's bigrepo keeps `git status` clean (no index/worktree writes outside
the private `GIT_INDEX_FILE`). Quarantine rows exercise the delegated stage-1 verify
engine only; `--dry-run` never reaches quarantine's own `jj_keep_novel`, so they are
not independent coverage of the quarantine copy (same caveat as J3-quarantine).

Retained evidence updated: `/var/tmp/souji-r17-FixtureJjReceipts/{base-arm.txt,worktree-arm.txt}`
(35-row tables verbatim).
