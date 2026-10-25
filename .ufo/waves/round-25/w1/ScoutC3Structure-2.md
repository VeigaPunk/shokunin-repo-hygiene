# ScoutC3Structure-2 — C3 recon (structure probe, common-dir envelope)

Seat `L1Souji25.ScoutC3Structure-2` (read-only scout). Written as `-2` to avoid clobbering the live
sibling seat `L1Souji25.ScoutC3Structure`, which has the same rendered path.

## Status
STATUS: PASS. All four questions (a–d) are answered from bytes and scratch runs observed this run. Scratch `/var/tmp/souji-r25-ScoutC3Structure-2/` has been removed.

## Evidence
- Lane HEAD `6e4737eab43d8fde1b85eb9f57023d29046705b4`. `git diff --stat HEAD` on both files is empty. The blobs are identical at HEAD and at base `a6d2d15`:
  `tools/souji-repo-structure.sh` blob `0f42ebf5…` (sha256 `80025137…aec2`, 312 lines);
  `tests/fixtures/r13-repo-structure.sh` blob `39b488a6…` (sha256 `b6bf5205…179f`, 659 lines).
  The receipt `census/round-25/records/c3-control-base.tsv` has a `tool_sha256` that matches. It reads `rc=0`, `selftest=PASS ids=5/5`.
- Host: `git version 2.56.0`. No tool was installed or updated.
- Linked worktree probe. Setup: A = `git init` + 1 commit, then `git worktree add $S/B` run under the fixture's `env -i` allowlist (no identity). That returned `wt_add_envi_rc=0`. Then `env -i <ENV_ALLOW> bash tools/souji-repo-structure.sh --repo $S/B`:
  ```
  probe_B_rc=0   (stderr empty)
  probe.repo_root=/var/tmp/souji-r25-ScoutC3Structure-2/B
  probe.git_dir=/var/tmp/souji-r25-ScoutC3Structure-2/A/.git/worktrees/B
  probe.git_common_dir=/var/tmp/souji-r25-ScoutC3Structure-2/A/.git
  references.branches.count=2 … references.others.count=0 … objects.commits.count=1
  manifest[common A/.git] equal   manifest[private A/.git/worktrees/B] equal   manifest[worktree B] equal
  ```
  `diff` of the probe output for A against the probe output for B: only `probe.command`, `probe.repo_root` and `probe.git_dir` differ. The metrics are identical.
  `git -C B config --local --get extensions.partialClone` returned rc=1, so the read goes to the common config and the refusal does not fire spuriously.
  The private gitdir has 9 manifest entries and sits inside the common dir (`grep -c worktrees/B before.meta` = 9 of 53 entries). Its `commondir` file is `../..`.
- Per-worktree refs: `update-ref refs/worktree/wx` and `refs/bisect/bad` in B. A probe from B gives `references.others.count=2`; a probe from A gives `references.others.count=0`.
  Detached unique commit in B: `objects.commits.count` stays `1`.
- `--format=lines` key count is 28, and `references.others.count` is present.
- Colocated simulation: `git clone SRC PLAIN` and `git clone SRC COLO`, then `update-ref refs/jj/keep/<HEAD> <HEAD>` in COLO. Both probes rc=0 with empty stderr.
  - Full `diff plain.out colo.out`: lines 4–7 (`probe.command/repo_root/git_dir/git_common_dir`) and line 16 (`others.count 0→1`) differ.
  - Metrics-only diff (`grep -v '^probe\.'`): only `references.others.count=0` vs `=1`.
  - Plain clone: `references.remotes.count=2`.
  - A keep ref to an otherwise-unreachable commit (`commit-tree … -p HEAD`) gives `others.count=2`, `objects.commits.count=1→2`, `max_parents 0→1`.
- Mutants (scratch copies of the committed probe):
  - **mut-common**: line 306 prints `"$git_dir"` instead of `"$common"`.
  - **mut-write**: after the output, `if [[ $git_dir != "$common" ]]; then printf 'x\n' >>"$common/description"; fi`.

  On B:
  ```
  souji-repo-structure.sh: rc=0 common_line=…/A/.git want=…/A/.git common_manifest=equal private_manifest=equal
  mut-common.sh: rc=0 common_line=…/A/.git/worktrees/B want=…/A/.git common_manifest=equal private_manifest=equal
  mut-write.sh:  rc=0 common_line=…/A/.git want=…/A/.git common_manifest=DIFF private_manifest=equal
  ```
  Committed fixture copy (only change: mktemp root moved under my scratch; `diff` shows line 159 only), `bash fx.sh --selftest --probe <P>`:
  real probe `selftest=PASS ids=5/5 rc=0`; mut-common `selftest=PASS ids=5/5 rc=0`; mut-write `selftest=PASS ids=5/5 rc=0`.

## Findings
1. **(a) The probe handles a linked worktree correctly today.** Its `--absolute-git-dir` is the private gitdir. `--path-format=absolute --git-common-dir` is A's `.git`, already normalized (not `…/worktrees/B/../..`). `--show-toplevel` prints the worktree root B.
   `git repo structure` from B walks the common object store with the shared refs, because its metrics equal A's when no per-worktree refs exist. B's per-worktree refs ARE counted (`others` 2 vs 0). So "B's figures equal the common-dir figures" holds only when B has no per-worktree refs.
   The probe doc already claims this. `tools/souji-repo-structure.sh:33-34`: "In a linked worktree the probe reports the resolved common dir; the object store is shared."
2. **(b) Insertion point.** Add both cases after the promisor-refusal block closes (`fi`, line 615) and before `# ---- selftest ids` (line 617). Add both ids to `SELFTEST_EXPECTED_IDS` at lines 618-626. The prereg target `ids=7/7` is in --probe mode, so put them in the `if ((PROBE_SET))` append at 624-626 or in the base list. Then baseline becomes 4/4 or 6/6; the prereg does not say which (see Attack 5).
   - **linked-common-dir.** Use a NEW repo `A="$WORK/linked-main"`, not `$REPO`: `worktree add` without `--detach` adds a branch, which would break `references.branches.count=1` in object-metrics if the order changed.
     - Run `g "$A" worktree add -q --detach "$WORK/linked-wt"`, or without `--detach`, which then expects `branches.count=2`.
     - Pass the manifest root as `COMMON_ABS="$(g "$WORK/linked-wt" rev-parse --path-format=absolute --git-common-dir)"`, i.e. `manifest_all "$COMMON_ABS" …` before/after. Also manifest `PRIVATE_ABS` (`--absolute-git-dir` in B) and assert `PRIVATE_ABS == "$COMMON_ABS/worktrees/linked-wt"`. The private tree is a subtree of the common manifest, so the private manifest alone is not enough: it missed mut-write.
     - Use an independent oracle: `check_eq probe.git_common_dir "$(printf %q "$A/.git")"`, built from the known layout rather than recomputed with the same rev-parse the probe uses. Also check `probe.git_dir` == `$A/.git/worktrees/linked-wt` and `probe.repo_root` == `$WORK/linked-wt`.
     - "Detector control passes first": the existing control (lines 321-363) mutates only `$GITDIR_ABS/description` of `$REPO`. Either gate on `CTRL_OK`, or re-run the description append/`touch -d`/`cp -p` control on `$COMMON_ABS/description`. A linked worktree's private gitdir has no `description` file.
   - **colocated-vs-plain.**
     - Setup: `g clone -q "$SRC" "$WORK/plain"`, `g clone -q "$SRC" "$WORK/colo"`, then `g "$WORK/colo" update-ref "refs/jj/keep/$OID" "$OID"`. The keep ref ideally points to a `commit-tree` commit not on any branch, which is the jj hidden-commit shape.
     - Probe each with `run_structure`.
     - Compare only `references.*`/`objects.*` lines (`grep -v '^probe\.'`) and require `others(colo) > others(plain)`. A whole-output byte diff is vacuous; see Attack 3.
     - A no-write manifest is not required by the prereg for this case. Using each clone's `--absolute-git-dir` is cheap if wanted.
3. **(c) Risks.**
   - **Environment allowlist and `git worktree add`:** no blocker. It succeeds even under the stricter `env -i` allowlist without identity (`wt_add_envi_rc=0`). In the fixture it goes through `g()` (identity, maintenance off), and the `ERR` trap maps any failure to rc 2.
   - **Config refusal:** it is not triggered on a linked worktree or on a local clone. The clone carries `remote.origin.url`/`fetch` but no `promisor`. `extensions.worktreeConfig` / `config.worktree` scope was not tested. [INFERENCE] A `remote.*.promisor` in `config.worktree` would still be read, because the regexp lookup has no `--local`. `extensions.partialClone` only in `config.worktree` would be missed by `--local`.
   - **`references.others.count`:** the key is present in the 28-key lines output on 2.56.0, and keep refs and per-worktree refs land there. The key set is EXPERIMENTAL (tool lines 36-39).
   - **`--show-toplevel`:** prints the worktree root.
   - **Manifest flake:** `manifest_entries` varied 40/41 between runs. [INFERENCE] This is loose-object fan-out directory collisions from time-dependent commit oids. It is harmless against the threshold of 10, but new cases must not pin an exact entry count.
4. **Stale documentation that C3 makes contradictory.**
   - Fixture line 9 ("normal (non-bare, non-linked)") and LIMITS lines 111-112 ("does not exercise packs, tags, remotes, linked worktrees") must be updated together with the cases, along with the CASES list at lines 77-105 and the final-line spec at lines 70-71.
   - Line 4 "STATUS: authored, NOT EXECUTED" is already stale, since the receipt shows it executed.
   - Tool lines 50-52 say "the committed fixture and its write-safety claim cover one normal work tree only". This becomes false after C3, but Separability forbids touching the tool under C3. The L1 must decide whether to accept that drift or route a doc-only fix.

## Attack log
1. **No red arm for C3 (calibration hole).** C1 and C2 each preregister an OLD-bytes red arm; C3 has only "Before: 5/5 → After: 7/7".
   - Observed: two linked-worktree mutants (mut-common, mut-write) both score `selftest=PASS ids=5/5` on the current fixture.
   - The proposed linked-common-dir case discriminates both on B: the common-line check catches mut-common, and the common manifest catches mut-write.
   - Recommendation (not a predicate change): receipt these two mutants against the extended fixture before after-data. Both must yield `selftest=FAIL` naming only `SOUJI-R13-STRUCT-linked-common-dir`.
2. **ids=7/7 can be gamed by vacuous cases.** The do-nothing control (current fixture) emits 5 ids and cannot reach 7/7. But the counter checks only the id set and the PASS verdicts, so two unconditional `emit … verdict=PASS` lines would satisfy it. Attack 1's mutant red arm is the guard.
3. **The colocated-vs-plain "byte-comparison" is vacuous.** The probe outputs ALWAYS differ, because `probe.command/repo_root/git_dir/git_common_dir` embed different paths (diff lines 4-7). The prereg's parenthetical "(references.others.count greater)" is the only discriminating predicate.
   Even that predicate tests git's ref classification, not the probe. Any pass-through probe passes, and a mutant that drops the `others` key is already caught by object-metrics `check_eq references.others.count 0` (fixture line 439). This case records a precondition (calibration) rather than adding probe coverage.
4. **Would the new cases pass with no probe change? Yes,** as observed manually: linked rc=0, common dir correct, all manifests equal; colocated `others` 0 vs 1. C3 is therefore pure fixture coverage of existing behaviour, which is consistent with the coverage axis and with Separability (fixture-only). It is not operability, because no behaviour changes. That is honest only if the score is framed as coverage, with Attack 1's red arm as evidence that the cases can fail.
5. **Baseline-mode count is unspecified.** The prereg pins `ids=7/7` for `--probe` only. Whether baseline mode becomes 4/4 or 6/6 is open and must be fixed before scoring. The fixture header (lines 70-71) states both counts.
6. **The predicate "probe.git_common_dir == A's resolved git dir" is near-tautological** if "resolved" is computed with the same `rev-parse --path-format=absolute --git-common-dir` call the probe makes (tool line 193). Use the layout oracle `$A/.git`; `/var/tmp` is not a symlink on this host (`readlink -f /var/tmp` = `/var/tmp`).
7. **Gap outside the case set.** A probe from a linked worktree counts that worktree's per-worktree refs (`refs/worktree/*`, `refs/bisect/*`): `others` 2 vs 0. A detached unique HEAD in B is not counted. Nothing in C3 pins this, so "linked == common figures" must not be asserted or claimed beyond refs-free worktrees.
