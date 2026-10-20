STATUS: DONE — jj has, since 0.36.0, skipped any directory that merely contains a `.git` or `.jj` entry, so tracked files beneath it snapshot as absent and report as deleted; grounded in changelog, tracker, and tagged source.

# SrcJjNestedRepo — how jj snapshots a directory containing `.git`

Question: does jj skip a directory containing a nested repository's `.git` and therefore report tracked files under it as deleted?

Answer (observed): **yes.** The rule is a *name-presence* check, not a repository-validity check: while walking the working copy, if a directory contains an entry named `.git` or `.jj`, `process_dir_entry` returns `Ok(None)` for that directory, so the whole subtree is omitted from the snapshot. Any path already tracked beneath it is then missing from the new tree and appears as `D` in `jj status` / `jj diff`. Nothing is deleted on disk, and (inferred from code order) ignore rules and `--include-ignored` cannot re-include the subtree because the reserved-name check precedes the matcher.

## 1. Verbatim located quote

Primary (≤25 words; 21 words), opening date 2026-10-20:

> "Sub-repos are no longer tracked. Any directory containing `.jj` or `.git` is ignored. Note that Git submodules are unaffected by this."

Location: `CHANGELOG.md` at tag **v0.46.0** (latest release, published 2026-10-07T21:28:17Z), lines **1438–1439**, section **`## [0.36.0] - 2025-12-03` › `### Breaking changes`**. URL: https://github.com/jj-vcs/jj/blob/v0.46.0/CHANGELOG.md

Consequence quote (11 words), same access date, from the tracker (issue is a user report, tier C):

> "`jj status` believes that files are deleted in the working copy"

Location: https://github.com/jj-vcs/jj/issues/8285 § **Actual Behavior** (opened 2025-12-10T14:19:17Z by @mkeeter; state **open**; updated 2026-03-18T21:16:21Z). The same report confirms the cause and intent after the reporter found stray `.git` directories: "This is a weird failure mode, but `jj` seems to be working as intended." (§ comment 2025-12-10T16:55:34Z).

Version/"last updated" line served: `https://docs.jj-vcs.dev/latest/working-copy/` and `/latest/git-compatibility/` served **no version stamp and no "last updated" line** on 2026-10-20 (grep for `[Ll]ast updated|Jujutsu [0-9]|version [0-9]|0\.[0-9][0-9]\.[0-9]` matched only unrelated prose). Version therefore pinned from the GitHub release API (`v0.46.0`, 2026-10-07) and the file pinned at that tag; `main` was `5176b1d8a3b0e569bb79b5e681c37874543ec617` (committed 2026-10-20T13:05:03Z) when the same entry was read at lines 1506–1508.

## Evidence chain (exact reads/greps and what they returned)

1. `read https://github.com/jj-vcs/jj/issues/8285` (GitHub API method) — title "`jj` is convinced that files in nested repositories are deleted"; § Actual Behavior prints `D 2016/01/.gitignore`, `D 2016/01/Cargo.toml`, … while `ls` shows the files present; reporter then finds `./2016/02/.git`, `./2016/01/.git`, `./.git`. Comment by @yuja (2025-12-11T11:11:35Z; listed among 0.36.0 contributors): "We can add config knob or `jj file track` flag to track files in nested repository, but I'm not sure if this is a common request." — i.e. no opt-out shipped.
2. `grep 'Sub-repos are no longer tracked' https://raw.githubusercontent.com/jj-vcs/jj/v0.46.0/CHANGELOG.md` →
   ` 1437|`, `*1438|* Sub-repos are no longer tracked. Any directory containing \`.jj\` or \`.git\``, ` 1439|  is ignored. Note that Git submodules are unaffected by this.`, ` 1440|` — the enclosing version heading is `## [0.36.0] - 2025-12-03`, subsection `### Breaking changes`.
3. `read pr://jj-vcs/jj/8157/diff/4` — the implementing PR ("working-copy: Ensure sub-repos are not tracked", @matts1, opened 2025-11-28) adds to `lib/src/local_working_copy.rs`:
   `let disk_dir = entry.path();` / `for &name in RESERVED_DIR_NAMES {` / `if disk_dir.join(name).symlink_metadata().is_ok() {` / `return Ok(None);` / `}`, with the in-code rationale "To solve this, we ignore all nested repos entirely." (fixes #4349).
4. `grep RESERVED_DIR_NAMES https://raw.githubusercontent.com/jj-vcs/jj/v0.46.0/lib/src/local_working_copy.rs` →
   `:822` `const RESERVED_DIR_NAMES: &[&str] = &[".git", ".jj"];`; `:1731-1732` a file/entry literally named `.git`/`.jj` returns `Ok(None)`; `:1745-1756` the directory branch: "If a submodule was added in commit C … To solve this, we ignore all nested repos entirely." then the `symlink_metadata().is_ok()` presence loop.
5. `read …/v0.46.0/lib/src/local_working_copy.rs:1715-1775` — confirms the presence loop sits in `process_dir_entry`, before both the `git_ignore.matches_dir` branch and the `self.matcher` branch; returning `Ok(None)` yields no tree entries for the subtree.
6. `read https://api.github.com/repos/jj-vcs/jj/releases/latest` → `"tag_name": "v0.46.0"`, `"published_at": "2026-10-07T21:28:17Z"`.
7. `read https://api.github.com/repos/jj-vcs/jj/commits/main` → `"sha": "5176b1d8a3b0e569bb79b5e681c37874543ec617"`.
8. Bounded negative sweeps for a later opt-out: `grep 'subrepo|sub-repo|nested' https://raw.githubusercontent.com/jj-vcs/jj/v0.46.0/docs/config.md` → no matches; `grep 'sub-repo|subrepo|nested repositor|RESERVED' …/v0.46.0/docs/cli-reference.md` → no matches; `grep 'Sub-repos|sub-repo|nested repositor|ignored' https://raw.githubusercontent.com/jj-vcs/jj/main/CHANGELOG.md` → only the 0.36.0 entry (plus unrelated "ignored" hits). So the changelog entry is the only documented statement and no knob is documented at v0.46.0.
9. `grep 'nested|sub-repo|\.git' https://raw.githubusercontent.com/jj-vcs/jj/main/docs/working-copy.md` → only the `.gitignore` paragraph; `grep 'Sub-repos|sub-repo|nested' …/main/docs/git-compatibility.md` → no matches. The guide pages do **not** state the nested-repo rule; the changelog and source are the authorities.

## Facts, inference, gaps

- **Observed:** documented rule (0.36.0 Breaking changes) + implementation (presence check on `.git`/`.jj` names, `symlink_metadata`, whole-directory `Ok(None)`) + tracker reproduction (`D` rows for files that exist on disk).
- **Observed:** the check requires only that the name exists — `symlink_metadata().is_ok()` succeeds for an empty directory and for a dangling symlink; there is no `HEAD`/`config`/validity test. Therefore an **empty untracked** `.git` stub inside a tracked directory is enough, which is exactly context claim (e)'s fixture (`tests/vault/vadv54-run/p/p6repo/.git`).
- **Observed:** the check runs before gitignore and path-matcher evaluation in `process_dir_entry`, and `jj file track --include-ignored` only widens a matcher — therefore ignore rules cannot rescue the subtree.
- **Inference (not stated):** because the snapshotter omits the subtree rather than emitting deletions, a later jj command sees the tracked paths as absent from the new tree; the working-copy commit then diffs them as deletions. The issue output is the observed instance of this.
- **Gap:** I did not and could not run `jj` (probe rule forbids it), so I have no local reproduction; and the host jj version is unknown. The behavior is version-gated at **jj ≥ 0.36.0** (2025-12-03); a lane on ≤ 0.35.0 would not see it.
- **Gap:** the issue remains open and no config knob or `jj file track` flag is documented; whether `jj file track` can override the reserved-name return in current code is `[INFERENCE]` from code order, not a tested claim.

## 2. Drafted SOURCES row

Exact registry column order: `id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`. No pipes inside cells.

```
| S0?? | Jujutsu CHANGELOG, 0.36.0 Breaking changes — https://github.com/jj-vcs/jj/blob/v0.46.0/CHANGELOG.md | docs | A | jj 0.36.0+ worktree snapshotting of a directory containing a `.git` or `.jj` entry (nested repository); not jj ref, bookmark or receipt semantics | CHANGELOG.md at tag v0.46.0 (published 2026-10-07) lines 1438-1439, section `## [0.36.0] - 2025-12-03` then `### Breaking changes`; implementation lib/src/local_working_copy.rs RESERVED_DIR_NAMES at :822 and directory presence check at :1745-1756 | a directory merely containing `.git` or `.jj` is skipped whole, so tracked files beneath it snapshot as deleted and an empty fixture `.git` stub fakes deletions | mined | 2026-10-20 | on-release | corpus/lessons/round-17.md |
```

- `status` justification: it grounds a lane change this round — context claim (e) (the `p6repo/.git` stub) and the jj recipes that must warn fixture authors. `used-by` assumes the round-17 lesson cites it in `## Gate`; L1 may prepend `corpus/knowledge/jj-colocation-receipts.md` if that entry also cites it. If neither file cites the row, downgrade to `queued` before landing (the census fails a `mined` row whose used-by paths do not exist).
- Optional second row (only if L1 wants the failure symptom cited directly; **not counted** as the requested row): `jj issue #8285` — https://github.com/jj-vcs/jj/issues/8285, `kind=community`, `tier=C` (never sole support), `status=queued`, `recheck=90d`, teaches: "stray `.git` directories make `jj status` show tracked files as deleted and `jj restore` cannot unconvince it; no opt-out shipped". The A-tier changelog row above carries the rule, so this is corroboration only.
- Not a row: PR #8157 — it is the implementation vehicle for the same claim; cite it in the lesson's evidence chain, not as a separate registry row (a `code` row would be defensible if the lane wants the exact presence semantics cited as primary implementation, but it duplicates the A row's anchor).

## 3. Contradiction check against the context claim text

**None found.** No statement on the opened pages contradicts claim (e) ("the empty untracked fixture stub …`p6repo/.git` makes jj see phantom deletions of two tracked files"). The changelog's "Any directory containing `.jj` or `.git` is ignored" and the source's presence-only `symlink_metadata` check both *support* it, including for an empty stub.

Two source-internal tensions to record, neither contradicting the claim:

1. The changelog says "Note that Git submodules are unaffected by this", but issue comment @yaahc (2025-12-18T22:34:00Z) reports `library/stdarch` — whose `.git` is a gitlink file `gitdir: ../../.git/modules/library/stdarch` — showing `D` rows in rust-lang/rust, and asks why the other subtrees with `.git` files are not affected. Lane guidance must not lean on the submodule parenthetical; the mechanism this round relies on is the plain `.git` directory stub, which is unambiguous.
2. The tracker's own framing is "working as intended" while the context calls it "phantom deletions". Both describe the same behavior; the lane should call it a *documented skip with a destructive-looking status*, not an upstream bug.

## Verdict and smallest fix

**Verdict: holds.** For jj ≥ 0.36.0, a directory containing a `.git` entry is skipped entirely; previously tracked files under it report as deleted, and the files remain on disk.

Smallest fix in the lane: remove the `.git` stub from the fixture (`tests/vault/vadv54-run/p/p6repo/.git`) or create it only transiently under `/var/tmp`; do not rely on ignore rules or `jj file track --include-ignored`, which cannot re-include a reserved-name directory. Add one line to the jj recipes/knowledge entry: "a `.git` or `.jj` entry in any directory makes jj skip that directory whole (0.36.0+); tracked paths beneath report deleted; no documented opt-out at v0.46.0."

## Probe and tooling record

- Web reads only: github.com/jj-vcs/jj issue/PR/changelog/API and docs.jj-vcs.dev. No lane file read except `corpus/SOURCES.md` (header + two rows + tail sections) and the fleet `CORPUS.md` contract section; no recursive search; no shell tooling run.
- No tools installed or upgraded this seat.
