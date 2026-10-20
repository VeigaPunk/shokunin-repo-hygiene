STATUS: DONE — the landed (b') novelty rule fires on 2 of 785 tracked candidate paths in kaidoku-shokunin (0 in the other six jj-colocated lanes); both are refusals caused by *abandoned* keep-only drafts while the path's current content is byte-identical to origin/main, so "novel ≈0 / live exposure nil" fails, narrowly, with a concrete mechanism and a one-line smallest fix.

# ScoutJjExposureNovel — C3 (b') live-lane exposure

Round 17, wave 2 (falsify). Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`, evidence commit `ddb7347`. All commands below are read-only `git -C <repo> ...` plus `sha256sum`/`stat`. No `jj` was executed, no receipt/census tool was run, no file outside this report was written, no commits.

## Question and method

Question: for each jj-colocated lane under `/home/vgpnk/Projects/shokunin/*-shokunin` (`test -d <r>/.jj`), how many tracked paths would refuse under the landed (b') novelty rule — for each keep-only commit and each path it changes, is `<c>:<path>` an object absent from the remote-history object set for that path?

Lanes found (7): kaidoku, kama, mado, souji, tabi, tameshi, tsukuroi; every one has `origin` and remote-tracking refs (remote commit counts 54–158), so `--remotes` is a real set in every lane.

I did not model the rule; I ran the landed function's body verbatim against each distinct candidate path (copy of `tools/souji-verify.sh:241-256`, identical text at `tools/souji-vault-verify.sh:433-448` and `tools/souji-quarantine.sh:977-992`):

```bash
jj_keep_novel() { local repo=$1 rel=$2 c obj known
  [ -n "$(git -C "$repo" for-each-ref --format='%(refname)' --count=1 refs/jj/keep/ 2>/dev/null)" ] || return 1
  if ! known=$(git -C "$repo" rev-list --objects --remotes -- "$rel" 2>/dev/null | cut -d' ' -f1); then return 2; fi
  if ! c=$(git -C "$repo" rev-list "--glob=refs/jj/keep/*" --not --branches --tags --remotes -- "$rel" 2>/dev/null); then return 2; fi
  while IFS= read -r c; do [ -n "$c" ] || continue
    obj=$(git -C "$repo" rev-parse -q --verify "$c:$rel" 2>/dev/null) || continue
    printf '%s\n' "$known" | grep -Fxq -- "$obj" || return 0
  done <<< "$c"
  return 1; }
```

Candidate enumeration (per lane): `git rev-list --glob='refs/jj/keep/*' --not --branches --tags --remotes`, then per commit `git show --format= --name-only --no-renames -r -m --first-parent <c> | grep -v '^$'`, unioned. The same enumeration plus `rev-parse <c>:<path>` + `rev-list --objects --remotes -- <path>` was also run as a cross-check of the function (same results).

### Bound

The mandated 300-path bound was applied first: the capped pass evaluated the first 300 distinct paths per lane and stopped (cap hit on kaidoku 785, mado 907, tameshi 914; kama/souji/tabi/tsukuroi were under 300 and complete). It found exactly the same two kaidoku paths (at union indexes 87 and 263) and 0 elsewhere. Because a full-lane sweep cost 33 s wall for all seven lanes together (remote histories are 54–158 commits), I then ran the uncapped authoritative function sweep and report *every* distinct path; no lane was stopped for runtime. Nothing was left unexamined.

## Results (sweep of the landed function, 2026-10-20 ~14:58–15:00 -03)

| lane | keep-only commits | distinct candidate paths | paths that refuse (rc=0) | rc=2 (git failure) |
|---|---|---|---|---|
| kaidoku-shokunin | 30 | 785 | **2** | 0 |
| kama-shokunin | 10 | 188 | 0 | 0 |
| mado-shokunin | 42 | 1062 | 0 | 0 |
| souji-shokunin | 13 | 165 | 0 | 0 |
| tabi-shokunin | 18 | 237 | 0 | 0 |
| tameshi-shokunin | 18 | 914 | 0 | 0 |
| tsukuroi-shokunin | 15 | 195 | 0 | 0 |

Novel paths (the complete list):

- `kaidoku-shokunin/SKILL.md` — refusing blob `9479f5a23590470b7f2e1d250eb2834d73d25c93` (59612 B), carried by keep snapshots `refs/jj/keep/13b6a5c…`, `50a3f90…`, `5397f9f…`, `95e9eb9…`, `f11a961…`, all committed `2026-10-20 13:23:55 -0300` (parents `9011581`, `eb6c266`).
- `kaidoku-shokunin/.ufo/waves/round-18/w2/SiblingOverlap2.md` — refusing blob `89e180e705fe1c0a0abfec6a93176d9ea2afc0ff` (22128 B), carried by keep snapshots `8425a16…`, `95754e3…`, `a6bbefb…`, `c0339f2…` (`2026-10-20 14:21:03 -0300`).

Counts drift while the lanes run (jj is creating keep refs during the sweep): mado's keep-only set grew 34→38→42 and its path union 907→1062, tsukuroi 12→15; the 0 result is for that snapshot. The two kaidoku hits were reproduced in three independent passes (capped enumeration, full enumeration, verbatim-function sweep) and are stable.

## Counterexample detail — both refusals are stale-draft false positives

Rule invocation, verbatim-function emulation:

```
== SKILL.md
  fn_novel_obj=9479f5a23590470b7f2e1d250eb2834d73d25c93 at 13b6a5c6075409c67498f7c017ced327fd9be422
  rc=0 (0=novel/refuse,1=not novel)
== .ufo/waves/round-18/w2/SiblingOverlap2.md
  fn_novel_obj=89e180e705fe1c0a0abfec6a93176d9ea2afc0ff at 8425a16ae28196f35eae9a3ffc4bf5b69d49f35b
  rc=0 (0=novel/refuse,1=not novel)
== README.md
  fn_c_list=[]
  rc=1 (0=novel/refuse,1=not novel)
```

For both paths the *current* file is pushed, so the refusal does not describe the target's state:

```
== worktree vs origin/main content (sha256 of bytes)
SKILL.md            worktree=b67e242d78dc3ee76e9c8572903c3e53f6002a342424445c27287223ec5b5b58
                    origin/main=b67e242d78dc3ee76e9c8572903c3e53f6002a342424445c27287223ec5b5b58
.ufo/.../SiblingOverlap2.md  worktree=ce256255f101bbcc48660ab2e79a5876ce8fa7cc0b14bba7bac710b6d0645af8
                    origin/main=ce256255f101bbcc48660ab2e79a5876ce8fa7cc0b14bba7bac710b6d0645af8
```

The upstream gates of `try_pushed` (`tools/souji-verify.sh:694-730`) also clear, so `jj_keep_novel` is the *sole* refusal cause — without it both targets would reach `R_VERDICT=SAFE; R_RECEIPT=pushed` at `:728-730`. Gate by gate: the status gate (`:697-702`, `status --porcelain --untracked-files=all --ignored=matching -- <target>`) sees no change because the file content equals HEAD (`HEAD` = `origin/main` = `a245bb0`); the intro gate (`:703-705`) resolves; the r6 unpushed-touching gate (`:710-715`) is 0; novelty (`:716-721`) is the first and only gate that returns 1; ancestry (`:722-724`) and the default-snapshot equality check (`:725-727`) would both pass on the content hashes above.

```
== intro commit is ancestor of origin/main (a245bb0, 2026-10-20 14:21:03 -0300)
b3669e6 rc=0     # SKILL.md intro
db4bdb1 rc=0     # .ufo path intro
== r6 branch-unpushed count touching path
SKILL.md count=0
.ufo/waves/round-18/w2/SiblingOverlap2.md count=0
```

The refusing blobs are nowhere in branch/tag/remote history (`git rev-list --objects --branches --tags --remotes | cut -d' ' -f1 | grep -Fxc <blob>` = `0` for both; `git log --all --format='%h %ci %s' --find-object=<blob>` lists only the keep snapshots above). Mechanism, therefore:

1. jj snapshots the working copy repeatedly; each snapshot that is not bookmarked gets `refs/jj/keep/<sha>`.
2. An intermediate draft of `SKILL.md` (13:23:55, 59612 B; 27 insertions/8 deletions away from the later final, `git diff --stat`) and of the w2 report (22128 B) was superseded and never pushed.
3. The final content was pushed (`origin/main` `db4bdb1` 14:16:45 for both files; tip `a245bb0` 14:21:03), but that does not retire the old keep refs, and the intermediate blob never enters remote history at that path.
4. `jj_keep_novel` iterates *every* keep-only commit touching the path (`tools/souji-verify.sh:247-254`), so the abandoned blob keeps returning rc 0 — permanently, for the life of the keep ref.

Retention is not documented: `corpus/knowledge/jj-colocation-receipts.md:28` (uncommitted draft) records only "Commits created by `jj` have a ref starting with `refs/jj/` to prevent GC", and `:98-101` states the keep-ref lifetime is `[INFERENCE]`; `jj util gc` behaviour on them is unvalidated (`:73-77`). So the refusal window is unbounded from the receipt's point of view.

## Verdict

- The rule does exactly what (b') claims: deletions and *published* identical-content predecessors do not refuse (fixture J4/J5; all 6 other lanes; the 8 keep snapshots carrying the pushed `0ed9757` blob at the `.ufo` path), and a keep-only blob absent from remote refuses (fixture J3, the two kaidoku paths). **holds as stated.**
- "Novel paths expected ≈0 / live exposure nil": **fails** — 2/785 (0.25%) in kaidoku, 0/188, 0/1062, 0/165, 0/237, 0/914, 0/195 elsewhere. Both hits are *policy* false positives against the receipt's own question ("is this path's current content pushed?"), because the refusal is produced by retired draft content that no actor intends to push, and pushing the final content cannot clear it.
- Exposure is small and lane-specific, but it is not nil and it is sticky. Practical reachability: `SKILL.md` is a plausible receipt target; the `.ufo/waves/...` report path is less likely to be receipted but is a tracked repository path, so it counts under the rule.

## Smallest fix (advisory)

Judge only the path's current snapshot, not its whole keep lineage. One line after `tools/souji-verify.sh:249` (and the identical inserts at `souji-vault-verify.sh:440`, `souji-quarantine.sh:984`):

```bash
  # newest keep snapshot for this path is the current one; older pins are drafts
  c=$(printf '%s\n' "$c" | head -1)
```

`rev-list` returns newest-first (commit-date order), and the newest keep commit touching each false-positive path already carries the pushed blob (`501acf5` 14:16:44 for `SKILL.md`; `28a30ef` 14:21:03 for the `.ufo` path), so both clear; J1–J5 semantics are unchanged (each fixture path has one keep commit; J4's predecessor blob is published). A more faithful but larger alternative is to compare the worktree file's blob (`git -C "$repo" hash-object --path="$rel" -- "$repo/$rel"`, read-only without `-w`) against `known`, and fall back to the keep lineage only when the target is absent from the worktree — that answers the receipt question directly and keeps the dirty-file catch.

Test gap that let this land: `tests/fixtures/r17-jj-receipts.sh` has J3 (novel keep-only content) and J4 (published predecessor) but no "superseded, never-published draft + published final snapshot" case. Add a J10: keep commit A with a novel blob at `f.txt`, sibling keep commit B (newer) with the pushed blob at `f.txt` → expect SAFE(pushed) under the fix, NOT-SAFE at `ddb7347`.

## Remaining unknowns

- Whether any real ledger in the fleet actually receipts `kaidoku-shokunin/SKILL.md` or the `.ufo` w2 path — I did not search lane trees (probe rule forbids recursive search); exposure is "would refuse if targeted", not "a receipt currently targets it".
- jj GC/retention on `refs/jj/keep/*` (does a `jj util gc` or `git gc` retire these pins, and after what age) — undocumented per the knowledge draft; my measurement covers only the current pin set.
- The other six lanes' 0 is a snapshot; stale drafts may appear there as work continues (mado's keep set grew by 4 commits and 155 paths during this measurement).

## Environment note (no installs)

No tool was installed or upgraded. One harness issue worth recording: shell loops using process substitution (`mapfile -t x < <(git …)`) hung the persistent shell (three jobs, 200–900 s, no git child alive in `ps`); the same loops written with command substitution + here-string completed in ~1–30 s. All numbers above come from the here-string form.
