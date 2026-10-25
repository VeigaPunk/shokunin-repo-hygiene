# ScoutC3LinkedManifest — W2 falsification of the integrated C3 fixture/probe

Skill: godspeed (host directive). Seat: L1Souji25.ScoutC3LinkedManifest (scout, leaf, read-only).
Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. Host: linux 7.2.11-arch1-1 x64, git 2.56.0.
Scratch: /var/tmp/souji-r25-ScoutC3LinkedManifest/ (removed at finish).

**STATUS: PARTIAL** — production counter passes (selftest=PASS ids=7/7, rc=0) and the linked
case manifests BOTH dirs with the detector control first; but amendment 3.4's *literal* `$A/.git`
oracle is not implemented (A's recomputed rev-parse is used; same value in this topology, not the
literal). Item 3 below.

## What this attack item required

> Read the integrated C3 fixture and probe. Verify the linked test manifests both common dir and
> private gitdir, detector controls pass first, and literal oracle uses A/.git (not same rev-parse
> used by probe). Run it once and report outputs/limits. Note if tool itself changes; no edits.

## Evidence (exact commands, this run)

Production counter (frozen prereg C3 command), run once, cwd = lane root, 2026-10-25:

```
bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh
rc=0
--- stdout ---
git_version=git version 2.56.0
probe_mode=tool:tools/souji-repo-structure.sh
fixture_repo=/var/tmp/souji-r13-repo-structure.3A3hMt/repo
fixture_git_dir=/var/tmp/souji-r13-repo-structure.3A3hMt/repo/.git
id=SOUJI-R13-STRUCT-manifest-control case=manifest-control content_delta=seen stat_delta=seen mtime_delta=seen restore=equal verdict=PASS
id=SOUJI-R13-STRUCT-write-free case=write-free rc=0 manifest_entries=41 verdict=PASS
id=SOUJI-R13-STRUCT-object-metrics case=object-metrics checks=29 verdict=PASS
id=SOUJI-R13-STRUCT-bogus-repo case=bogus-repo plain_dir_rc=2 missing_rc=2 verdict=PASS
id=SOUJI-R13-STRUCT-promisor-refusal case=promisor-refusal promisor_rc=2 partial_rc=2 verdict=PASS
id=SOUJI-R13-STRUCT-linked-common-dir case=linked-common-dir rc=0 common_entries=53 private_entries=9 checks=8 control=PASS verdict=PASS
id=SOUJI-R13-STRUCT-colocated-vs-plain case=colocated-vs-plain plain_rc=0 colocated_rc=0 others_plain=0 others_colocated=2 commits_plain=1 commits_colocated=2 differing_keys=8 precondition=colocated-not-interchangeable-with-plain-baseline verdict=PASS
selftest=PASS ids=7/7
--- stderr --- (empty)
```

Red-arm arms (amendment 3.2's two prescribed mutants, each run against the integrated fixture; both
must FAIL the linked case):

```
bash tests/fixtures/r13-repo-structure.sh --selftest --probe <scratch>/mutant-a-common-as-private.sh
rc=1
id=SOUJI-R13-STRUCT-linked-common-dir case=linked-common-dir rc=0 common_entries=53 private_entries=9 checks=8 verdict=FAIL detail= probe.git_common_dir=/var/tmp/souji-r13-repo-structure.3JunV5/linked-main/.git/worktrees/linked-tree want=/var/tmp/souji-r13-repo-structure.3JunV5/linked-main/.git; probe.git_dir==probe.git_common_dir
selftest=FAIL ids=7/7 missing=[] extra=[] failed_verdicts=1

bash tests/fixtures/r13-repo-structure.sh --selftest --probe <scratch>/mutant-b-writes-common.sh
rc=1
id=SOUJI-R13-STRUCT-linked-common-dir case=linked-common-dir rc=0 common_entries=53 private_entries=9 checks=8 verdict=FAIL detail= common-dir-manifest-delta
selftest=FAIL ids=7/7 missing=[] extra=[] failed_verdicts=1
```

Mutant A = real tool with `--git-common-dir` replaced by `--absolute-git-dir` (reports the private
gitdir as common). Mutant B = real tool that appends one line to `$COMMON/description` only when
`$common != $git_dir` (linked worktree only). Both were trivial patches of the unmodified tool bytes,
in scratch; the lane tool itself was never edited. Both fail exactly the linked case; all other ids
stay PASS.

Hashes: lane tool `sha256sum tools/souji-repo-structure.sh` = `80025137b20d5a6143db0120057552bd239fb60de1a504ede69896baade5aec2`;
base-blob fixture `git show a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe:tests/fixtures/r13-repo-structure.sh | sha256sum` = `b6bf52056d037b2251632b409be3d31852588480c392ddc50ca8f8dbf101179f` (matches receipt tool_sha256, which hashes the FIXTURE, not the probe);
draft fixture (worktree) = `eabc5f0ac56ea3db9f6f68d2dfeadbc91f592eb68c3691d2eabbd5b8347e2c13`.

## Numbered findings

1. **Linked case manifests BOTH the common dir and the private gitdir (PASS).** The integrated
   fixture roots the no-write manifest at the COMMON dir and separately at B's private gitdir:
   `manifest_all "$LW_COMMON" "$WORK/lw-common-before"` / `manifest_all "$LW_PRIV" "$WORK/lw-priv-before"`
   before `run_structure "$LW_TREE" …` and both `-after` snapshots after (fixture lines 718-724),
   guarded by `manifests_equal` on both (lines 732-735; `common-dir-manifest-delta` and
   `private-gitdir-manifest-delta` failure arms). Non-vacuous: the common manifest must contain
   HEAD, config, refs/heads/master, refs/heads/r25-linked, and the private HEAD/commondir/gitdir/
   index; the private manifest additionally must contain its own index (lines 738-751). Observed:
   common_entries=53, private_entries=9, both equal, verdict=PASS, stderr empty.
2. **Detector controls pass first (PASS).** Both `detector_control` calls — on `$LW_COMMON/description`
   and on `$LW_PRIV/gitdir` — execute before any before-snapshot and before the measured probe
   (lines 714-715 then 718-722). The control itself proves the manifest detects content, stat and
   mtime-only deltas and observes byte-exact restore (content_delta=seen stat_delta=seen
   mtime_delta=seen restore=equal). Linked run reports control=PASS.
3. **Literal oracle `$A/.git` (PARTIAL).** Amendment 3.4 requires probe.git_common_dir's oracle to
   be the literal `$A/.git`, "not a recomputed rev-parse". The integrated fixture instead computes
   `LW_COMMON="$(g "$LW_MAIN" rev-parse --path-format=absolute --absolute-git-dir)"`
   (fixture line 704) and compares `check_eq probe.git_common_dir "$(printf %q "$LW_COMMON")"`
   (line 761). The oracle is A's own recomputed rev-parse, not the literal `$LW_MAIN/.git`.
   Mitigations: (a) in this topology they coincide — A is a plain repo whose `.git` is a real
   directory, so `--absolute-git-dir` == `$LW_MAIN/.git`; (b) the oracle is independent of the
   probe's mechanism (probe runs its own `git -C B rev-parse --git-common-dir` in a separate
   process/command — not "the same rev-parse used by probe"); (c) amendment 3.4's second clause IS
   implemented: `[[ $LW_PRIV == "$LW_COMMON"/worktrees/* ]]` (lines 710-711) asserts the private
   gitdir equals `$COMMON/worktrees/<name>` (observed `…/linked-main/.git/worktrees/linked-tree`).
   Discrimination proven: mutant A (private-as-common) is caught by this oracle
   (`probe.git_common_dir=…worktrees/linked-tree want=…linked-main/.git`). Verdict: functionally
   sound and independent; literally non-compliant with the "literal `$A/.git`" wording.
4. **Red arms per amendment 3.2 (PASS functionally; receipts missing).** Both prescribed probe
   mutants FAIL the extended fixture, failing only the linked case (selftest=FAIL ids=7/7,
   missing=[] extra=[] failed_verdicts=1). So the integrated fixture discriminates as the
   amendment demands. HOWEVER, the mandated red-arm **receipts** are not yet committed:
   `census/round-25/records/` holds only c1/c2/c3-control-base.tsv + coverage/record-agreement
   at-base receipts (listing verified 2026-10-25). Amendment 3.2 requires each receipt "before any
   after-data"; the amendment's closed attack (ScoutC3Structure-2 attack 1) therefore remains an
   open obligation for L1 (this scout is a read-only seat and commits nothing).
5. **Colocated-vs-plain, amendment 3.3 (PASS).** Metric-only comparison is implemented
   (`grep -E '^(references|objects)\.'` extracts only metric lines, dropping probe.*; lines
   813-814); `references.others.count` must be greater in the keep-ref clone (`((10#$CP_COLO_OTHERS > 10#$CP_PLAIN_OTHERS))`, line 827); a do-nothing emitter cannot reach PASS (`metrics-identical` → FAIL; plus rc=0/stderr-empty/unchanged-manifest guards). Observed: others_plain=0, others_colocated=2, differing_keys=8, both rc=0, stderr empty, verdict=PASS. The keep-ref simulation (refs/jj/keep/* at HEAD and at an extra commit reachable only from the keep ref) raises commits 1→2 as well as others 0→2, confirming the precondition is non-empty for the census.
6. **Tool itself unchanged (PASS).** `tools/souji-repo-structure.sh` is byte-identical at base
   a6d2d15 and HEAD (git diff empty) and unmodified in the worktree (git status clean for it):
   sha256 `80025137b20d5a6143db0120057552bd239fb60de1a504ede69896baade5aec2`. The round-25
   integration touches only the fixture (draft sha256 `eabc5f0a…`), the knowledge entry
   `corpus/knowledge/git-repo-structure-common-dir.md` (present, 5717 B, 09:57), and SOURCES rows
   S124/S125/S126 (draft in w1 sources-rows.md). c3-control-base.tsv (v1, rev a6d2d15, rc=0,
   selftest=PASS ids=5/5, 2026-10-25T12:33:07Z) hashes the base fixture blob exactly (b6bf52056…)
   — receipt is internally consistent.
7. **Limits (disclosed, unchanged).** Fixture LIMITS header: fresh SHA-1 loose-object one-/two-commit
   repos; one normal repo, one linked worktree, two local clones; no packs, tags, bare repos,
   alternates, real promisor fetches, submodules, real jj-managed repos or concurrent writers; the
   keep-ref simulation only proves extra refs/jj/keep/* refs change the census. Envelope: env -i
   allowlist (PATH/HOME/LC_ALL=C/GIT_OPTIONAL_LOCKS=0/GIT_NO_LAZY_FETCH=1/GIT_TERMINAL_PROMPT=0/
   GIT_CONFIG_GLOBAL=/dev/null/GIT_CONFIG_NOSYSTEM=1; GIT_DIR/WORK_TREE/COMMON_DIR/INDEX_FILE/
   OBJECT_DIRECTORY/ALTERNATE unset); content = sorted sha256 of regular files, meta =
   type/mode/size/mtime/path[/link-target]; atime and ctime excluded by design (ctime changes from
   controls not compared); `timeout 120` per measured command; result is an observed
   no-persistent-delta for this host/run, not universal write-safety.

## Attack log
- Read prereg + amendments 1-3 (oracle, red-arm and colocated clauses identified).
- Read integrated fixture (worktree bytes; helper defs, linked case 699-767, colocated 779-848,
  id set + verdict/ear 851-892) and tool (probe.git_dir/git_common_dir/repo_root emission).
- Verified base..HEAD tool diff = 0 lines; git status shows only the fixture modified among C3 files.
- Production counter run (exact frozen command), rc=0, selftest=PASS ids=7/7, stderr empty.
- Built mutant A + mutant B in scratch from verbatim tool bytes; both fixture runs FAIL only the linked case.
- Hash verifications (tool, base fixture blob vs receipt, draft fixture).
- Checked census/round-25/records/ for red-arm receipts — absent (finding 4).
- No lane edits; scratch removed.

## Remaining unknowns
- Whether L1 will commit the amendment 3.2 red-arm receipts (c3-red-arm-*.tsv) before after-data —
  my runs prove the integrated fixture already discriminates both mutants, so the receipts are
  reproducible now.
- The literal-oracle deviation (finding 3) is a compliance question for L1: runtime the wording
  ("literal `$A/.git`") or accept the independent-rev-parse oracle as equivalent in this topology.
