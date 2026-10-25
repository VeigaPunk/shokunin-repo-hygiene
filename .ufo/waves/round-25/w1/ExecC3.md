# ExecC3 — C3 structure probe under the common-dir envelope + colocated/plain precondition (souji r25 w1)

Seat: L1Souji25.ExecC3-2 (executor, leaf). Lane HEAD 6e4737eab43d8fde1b85eb9f57023d29046705b4. Host git 2.56.0 (`pacman -Q git` = `git 2.56.0-1`). No installs or updates. Scratch was `/var/tmp/souji-r25-ExecC3-2/` (my seat name; kept apart from the sibling ExecC3 seat). It has been removed, and no `/var/tmp/souji-r13-repo-structure.*` dirs remain.

## Status
STATUS: PASS. The draft fixture prints `selftest=PASS ids=7/7` with rc 0 against the **committed, unchanged** probe (blob 0f42ebf5afac31e8dbddfc67de6b30ef96e4806c). It was stable across 4 runs. The 5 existing case bodies are byte-identical; only header comments changed. Five mutant probes are each killed by the draft. Four of them pass the committed fixture as a false green (`ids=5/5`). No probe draft is needed.

## Drafts written
- `.ufo/waves/round-25/w1/r13-repo-structure.sh`. sha256 `eabc5f0ac56ea3db9f6f68d2dfeadbc91f592eb68c3691d2eabbd5b8347e2c13`, git blob `c369546ef7d0eaa6418b15b42d5147bc46355a6c`. Base: the committed `tests/fixtures/r13-repo-structure.sh`, blob 39b488a69e4e, sha256 b6bf5205…179f (`cp -p`, then edited).
- `.ufo/waves/round-25/w1/git-repo-structure-common-dir.md` (knowledge entry draft, 65 lines). sha256 `90d6be2789a8cce7e47ee25daa135567242b679e13170f10db0c9e17bcd3f533`.
- No `souji-repo-structure.sh` draft was written; see Findings 1.

## Evidence
Green arm (frozen counter, run against the draft):
```
$ bash .ufo/waves/round-25/w1/r13-repo-structure.sh --selftest --probe /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-repo-structure.sh
id=SOUJI-R13-STRUCT-manifest-control … verdict=PASS
id=SOUJI-R13-STRUCT-write-free case=write-free rc=0 manifest_entries=41 verdict=PASS
id=SOUJI-R13-STRUCT-object-metrics case=object-metrics checks=29 verdict=PASS
id=SOUJI-R13-STRUCT-bogus-repo case=bogus-repo plain_dir_rc=2 missing_rc=2 verdict=PASS
id=SOUJI-R13-STRUCT-promisor-refusal case=promisor-refusal promisor_rc=2 partial_rc=2 verdict=PASS
id=SOUJI-R13-STRUCT-linked-common-dir case=linked-common-dir rc=0 common_entries=53 private_entries=9 checks=8 control=PASS verdict=PASS
id=SOUJI-R13-STRUCT-colocated-vs-plain case=colocated-vs-plain plain_rc=0 colocated_rc=0 others_plain=0 others_colocated=2 commits_plain=1 commits_colocated=2 differing_keys=8 precondition=colocated-not-interchangeable-with-plain-baseline verdict=PASS
selftest=PASS ids=7/7        (rc=0; 3 more runs: PASS ids=7/7 rc=0 each)
```
Baseline arm (no `--probe`): `selftest=PASS ids=6/6`, rc 0. The new cases run in both modes, and the probe.* checks run only with `--probe`. The linked case runs 2 checks in baseline mode and 8 with `--probe`.

Before control (committed fixture, same host): `bash tests/fixtures/r13-repo-structure.sh --selftest --probe …/tools/souji-repo-structure.sh` → `selftest=PASS ids=5/5`, rc 0.

Diff to the committed fixture: `git diff --no-index --stat` shows 242 insertions and 7 deletions. All 7 deleted lines are header comments: the tally line 70-71 (`ids=4/4`/`ids=5/5` → `ids=6/6`/`ids=7/7`) and the LIMITS paragraph 111-116 (rewritten to name the linked worktree, the clones and the keep-ref simulation). The insertions are the header case docs (+26) and two blocks before `# selftest ids` (+204). The other +2 are the two ids added to `SELFTEST_EXPECTED_IDS`. `bash -n` passed and `shellcheck` printed nothing.

Red arms. Each mutant is a wrapper around the committed probe. The table shows the final line for the draft fixture and for the committed fixture, both run with `--probe <mutant>`:

| mutant | behaviour | draft | committed |
|---|---|---|---|
| m1-noop | `exit 0`, no output | FAIL rc 1 (linked + colocated also FAIL) | FAIL rc 1 |
| m2-common-write | when linked: append to `$common/description` | FAIL rc 1: `linked-common-dir … detail= common-dir-manifest-delta` | **PASS ids=5/5 rc 0** (false green) |
| m3-private-write | when linked: append to `$private/gitdir` | FAIL rc 1: `common-dir-manifest-delta; private-gitdir-manifest-delta` | **PASS ids=5/5 rc 0** |
| m4-common-misreport | when linked: print `probe.git_common_dir=<private gitdir>` | FAIL rc 1: `probe.git_common_dir=…/linked-main/.git/worktrees/linked-tree want=…/linked-main/.git` | **PASS ids=5/5 rc 0** |
| m5-others-zero | rewrite `references.others.count=0` | FAIL rc 1: `others.count colocated=0 not> plain=0` | **PASS ids=5/5 rc 0** |

Mutant generator. The scratch copies are deleted. Re-create them under a /var/tmp scratch dir, set `P` to the committed probe, then run the two loops:
```bash
MD=/var/tmp/souji-r25-<seat>/mutants; mkdir -p "$MD"; P=/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-repo-structure.sh
printf '#!/usr/bin/env bash\nexit 0\n' >"$MD/m1-noop.sh"
for m in m2-common-write m3-private-write m4-common-misreport m5-others-zero; do
  printf '#!/usr/bin/env bash\nset -u\nMUT=%s\nREAL=%s\n' "$m" "$P" >"$MD/$m.sh"
  cat >>"$MD/$m.sh" <<'EOF'
repo=${2:-}
out="$(bash "$REAL" "$@")"; rc=$?
gd="$(git -C "$repo" rev-parse --path-format=absolute --absolute-git-dir 2>/dev/null)" || gd=""
cd_="$(git -C "$repo" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" || cd_=""
linked=0; [[ -n $gd && $gd != "$cd_" ]] && linked=1
case $MUT in
  m2-common-write) ((linked)) && printf 'x\n' >>"$cd_/description" ;;
  m3-private-write) ((linked)) && printf 'x\n' >>"$gd/gitdir" ;;
esac
while IFS= read -r line; do
  case $MUT:$line in
    m4-common-misreport:probe.git_common_dir=*) ((linked)) && line="probe.git_common_dir=$gd" ;;
    m5-others-zero:references.others.count=*) line="references.others.count=0" ;;
  esac
  printf '%s\n' "$line"
done <<<"$out"
exit $rc
EOF
done
for m in m1-noop m2-common-write m3-private-write m4-common-misreport m5-others-zero; do
  bash .ufo/waves/round-25/w1/r13-repo-structure.sh --selftest --probe "$MD/$m.sh" | tail -1
  bash tests/fixtures/r13-repo-structure.sh --selftest --probe "$MD/$m.sh" | tail -1
done
```

## Findings
1. **No probe change is needed** (`tools/souji-repo-structure.sh:181,193`). With `--repo B`, the committed probe printed `probe.git_dir=…/A/.git/worktrees/B` and `probe.git_common_dir=…/A/.git`, equal to `git -C A rev-parse --path-format=absolute --absolute-git-dir`. A `find`/`sha256sum` manifest of `A/.git` was identical before and after the probe. The same manifest detected a default `git -C B status` (index refresh in `worktrees/B/index`), so the detector sees real git writes in that root. A `refs/jj/keep/<oid>` ref moved `references.others.count` from 0 to 1. The probe was used as-is.
2. **linked-common-dir design** (draft fixture, `# linked worktree common dir` block). The case builds main repo `linked-main`, adds `git worktree add -q -b r25-linked linked-tree`, and asserts that the setup's `--git-common-dir` equals A's `--absolute-git-dir`. It then runs a new `detector_control` (the same content/stat/mtime arms as the r13 control, now rooted per call) on the common dir (`description`) and on the private gitdir (`gitdir`), before the measured run. A control failure fails the case. Manifests are taken over the common dir (53 entries, which includes `worktrees/<id>`) and over the private gitdir (9 entries), before and after. Eight non-vacuity markers are checked: common HEAD and config, both branch refs, and private HEAD, commondir, gitdir and index. In probe mode the case also asserts `probe.git_common_dir == %q(A's resolved git dir)`, `probe.git_dir == %q(private)`, the two differ, and `probe.repo_root == %q(toplevel)`.
3. **colocated-vs-plain design** (draft fixture, `# colocated vs plain` block). Two `clone --no-hardlinks` copies of the r13 fixture repo are made. The colocated-like clone gets `refs/jj/keep/<HEAD>` and `refs/jj/keep/<hidden>`, where the hidden commit is made with `commit-tree -p HEAD` and is reachable only from its keep ref. Both runs must have rc 0, empty stderr and an unchanged git-dir manifest. Their `references.*`/`objects.*` lines must differ, and `others` must be greater on the colocated clone. The `probe.*` lines are excluded from the comparison because they differ by path alone; otherwise a do-nothing difference would satisfy "outputs differ". The case emits `precondition=colocated-not-interchangeable-with-plain-baseline`. It also records `commits_plain=1 commits_colocated=2`: the keep refs change object totals, not only ref counts.
4. **Baseline-mode tally changes 4/4 → 6/6.** Grep finds `ids=4/4` only in round-13 history (`census/round-13/final-checks.md:49`, `registry-draft.md:178,261,406`, `frontier-draft.md:127,232`). No live counter pins the baseline arm. The probe-arm target `ids=7/7` matches the prereg.
5. **S125 source conflict for the knowledge entry** (`w1/ScoutSourcesOpen.md` Findings 2–3 vs `w1/sources-rows.md` Registry rows). The scout rejects the briefed glossary "common directory" entry (0 matches) and recommends git(1) `GIT_COMMON_DIR`. The scribe drafted S125 as gitglossary(7) § worktree. My entry draft follows the scribe's rows: S124 = gitrepository-layout § commondir/§ objects, S125 = gitglossary § worktree. The L1 must pick one. If S125 becomes git(1) § `GIT_COMMON_DIR`, swap the S125 `source:` line and ADMIT for the quote I opened in the installed git(1) man page (L1045-1047): "If this variable is set to a path, non-worktree files that are normally in $GIT_DIR will be taken from this path instead." (22 words).
6. **Entry quotes were verified against bytes opened this run.** Each of the 3 ADMIT quotes is a whitespace-normalised substring of the installed `man -P cat` output: gitrepository-layout § commondir (L237-240), § objects (L45-46), and gitglossary § worktree (L676-682). No quote contains `|`. The entry's `source:` line cites only S124/S125, so no existing row's `used-by` changes. It refers to S035–S037 only via the sibling entry path. The README F2 map row must gain `knowledge/git-repo-structure-common-dir.md` in the same commit (Q56); that is the L1's job. The `verified-at:` line names the w1 draft run. Re-point it to the landing receipt when the fixture lands.
7. **Recheck hazard, observed and not a defect.** gitrepository-layout § worktrees/<id>/gitdir says that file's mtime "should be updated every time the linked repository is accessed" (installed man L255-256; registry scope S033). On 2.56.0 the probe left it unchanged. A future git that refreshes it on reads would turn `linked-common-dir` red on `private-gitdir-manifest-delta`. The entry records this as a recheck trigger. I did not cite it under S124, because it is outside the drafted S124 scope (S033 owns `worktrees/<id>/gitdir`).

## Attack log
- A1 (on the frozen "outputs differ" predicate): comparing the full probe outputs is trivially true, because `probe.command`, `probe.repo_root`, `probe.git_dir` and `probe.git_common_dir` embed the clone paths. The draft compares only `references.*`/`objects.*` lines and additionally requires `others` to be strictly greater. A whole-output comparison would be a gameable reading of the counter. I report this as an attack on the wording, not as a predicate change.
- A2 (r24 blind spot, confirmed): the committed fixture passes m2, m3, m4 and m5 as `PASS ids=5/5`. Its `--absolute-git-dir` root cannot see common-dir writes or a misreported common dir.
- A3 (residual): the keep-ref simulation does not exercise jj itself (op log, `.jj/repo/store`, `refs/jj/root`-style refs). The case grounds only "extra `refs/jj/keep/*` refs change the census". The fixture LIMITS and the entry's NOT-establish list say so.
