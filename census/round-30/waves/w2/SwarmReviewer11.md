# SwarmReviewer11 — S054 re-open attack on `corpus/knowledge/jj-keep-ref-expiry.md`

## Status

STATUS: PASS — the attack ran end-to-end (live tag re-fetch hashed against `census/round-30/sources/SHA256SUMS`, byte-identity with the committed snapshots, line-exact verification of all six S054 ranges, `gc.rs` `--expire` check, Gate binding judged); the entry held on every S054-attributed claim, with two non-fatal citation imprecisions and one cosmetic locator label.

## Evidence

- Live fetch 2026-10-26 of `https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/lib/src/git_backend.rs` hashes `95147270e5bc2a689e1191256c0f214d8e52ac6d4523756eb6b8ec8113d86c69` — equal to the `census/round-30/sources/SHA256SUMS` line for `git_backend.rs`, and `cmp` against `census/round-30/sources/git_backend.rs` is byte-identical (receipt: `.ufo/waves/round-30/w2/SwarmReviewer11-receipts.txt`). Every quote below is from those bytes.
- Same for `cli-reference@.md.snap`: live hash `b330694348c2a6fb21b637425c711d48ac9fa41d0b3596b4ca2955f7a9333554` equals the manifest line and is `cmp`-identical with the committed snapshot.
- `cli/src/commands/util/gc.rs` at tag v0.45.1 fetched (no manifest row; supplementary seat check), sha256 `9c4d6a3704abb6f3afbb63cfd44153437b83d7e68d0f2426f84f8cdbbb0b4b9b`, staged as `.ufo/waves/round-30/w2/SwarmReviewer11-gc.rs`.
- `census/round-30/records/jj-keep-expiry-run.txt` opened this run; its step lines match the entry's Observed section number-for-number (1→7 yes, 2→8 yes, 3→8 yes, 4→6 no, 5→2 no, 6→8 yes rc=1, 7→8 yes, 8→6 no).
- No tool installs or updates this run.

## Findings

1. **DEFECT-NOT-FATAL** — `corpus/knowledge/jj-keep-ref-expiry.md` claim 1 cites "applying both in one ref transaction (git_backend.rs:900-903, :917-961)". The single-transaction application is `.edit_references(ref_edits)` at `census/round-30/sources/git_backend.rs:963-964` — outside the cited range, which ends at the edit-list chain construction (`new_heads.iter().map(to_no_gc_ref_update),` :961). The claim is true (one `edit_references` call takes both the deletion edits and the keep-ref updates; corroborated by the comment at :958 "It's slow to delete packed refs one by one, so update refs all at once."), but the citation stops 2-4 lines short of the call it names.
2. **DEFECT-NOT-FATAL (cosmetic)** — the S054 row in `census/round-30/sources/SHA256SUMS` labels ":929-937 (mtime check)"; the mtime check proper is :938-946 (`if mtime > keep_newer {` at :941), while :929-937 is the racy-re-import comment plus its TODO block. The entry itself cites both ranges correctly (:929-937 comment, :938-944 gate), so only the row's parenthetical label is loose. The Gate bullet "lines 929-937, mtime check on the loose ref" carries the same loose label, though both of its quotes sit verbatim at :929 and :931.
3. **Observation, no defect** — entry claim 1 omits two code details, neither meaning-bearing for the claim made: the head set is filtered to exclude the root commit (:1563 `filter(|id| *id != self.root_commit_id)`), and a keep ref is kept only when its name suffix equals the target hex (:924-925 `if new_heads.contains(&id) && name_good {`; legacy random-name keep refs are deleted, comment :947 "Also deletes no-gc ref of random name created by old jj."). The entry's "keeps the keep refs for them … every other keep ref" phrasing absorbs both.

## Attack log

Attacked: every S054-attributed claim of the entry, at the six named ranges, plus the `--expire` statement and the Gate binding. Verdicts:

- **:100 namespace constant — HOLDS.** `census/round-30/sources/git_backend.rs:100` is exactly `const NO_GC_REF_NAMESPACE: &str = "refs/jj/keep/";` under the doc comment :99 "Ref namespace used only for preventing GC." — the SOURCES row's "line 100 (namespace constant)" is exact.
- **:900-903 doc comment + signature — HOLDS.** :900-901 is the doc comment, :902-903 the `fn recreate_no_gc_refs(` signature start. Gate quote verbatim at :900: "Recreates `refs/jj/keep` refs for the `new_heads`, and removes the other".
- **:917-961 loop + one ref transaction — DEFECT-NOT-FATAL (finding 1); mechanism HOLDS.** The loop (:917-950) keeps a ref iff its target is a given head with a good name (:925-927), else keeps it iff the loose-ref mtime is newer (:938-944), else pushes it to `no_gc_refs_to_delete` (:949); both edit lists are then applied by the single `edit_references` call at :963-965.
- **:929-944 racy comment + age gate — HOLDS.** :929 "Check timestamp of loose ref, but this is still racy on re-import"; :931 "existing packed ref won't be demoted to loose ref"; the gate :938-944 keeps when `if mtime > keep_newer {` (:941). The entry's packed-ref sentence is correctly labeled `[INFERENCE]` and is mechanically sound: for a packed ref the loose file does not exist, `loose_ref_path.metadata()` errs, the `if let Ok` falls through to deletion — corroborated by comment :931, and disclosed as read-not-measured.
- **:975-977 git gc argument — HOLDS.** :977 is `.arg(format!("--prune=@{} +0000", keep_newer.as_secs()));`; the entry's `--prune=@<keep_newer>` is a faithful abstraction (the arg appends a fixed ` +0000`). The same `keep_newer` instant flows into `recreate_no_gc_refs` (:1564) and `run_git_gc` (:977), confirming the entry's "the keep-ref age test and git's loose-object prune share one instant".
- **:1558-1564 backend gc — HOLDS.** :1558 `fn gc(&self, index: &dyn Index, keep_newer: SystemTime) -> BackendResult<()> {`; :1560-1561 `.all_heads_for_gc()`; :1564 `recreate_no_gc_refs(&git_repo, new_heads, keep_newer)?;` — exactly the entry's "The heads are `index.all_heads_for_gc()` inside the backend `gc(index, keep_newer)`", root-commit filter aside (finding 3).
- **`--expire` accepts only `now` — HOLDS.** `gc.rs` at the tag: :56 `Some("now") => SystemTime::now() - Duration::ZERO,` and :57 `_ => return Err(user_error("--expire only accepts 'now'")),` — any other value is rejected; :55 shows the no-arg default `SystemTime::now() - Duration::from_secs(14 * 86400)` (two weeks). The doc comment :37 "Only the string \"now\" can be passed to this parameter." matches snap :3803 "Only the string \"now\" can be passed to this parameter. Support for arbitrary absolute and relative timestamps will come in a subsequent release." and snap :3801 "By default, only obsolete objects and operations older than 2 weeks are pruned." (all inside the entry's cited :3799-3805). The committed record corroborates: step 6 `expire=tomorrow rc=1 rejected`.
- **Gate blob-vs-raw binding — HONEST.** The Gate's S054 bullets cite `https://github.com/jj-vcs/jj/blob/v0.45.1/lib/src/git_backend.rs` while the snapshot is the raw file. The binding is disclosed in the S054 row itself: "snapshot: the raw bytes of the same file at the same tag". Blob and raw URLs serve identical content for the same tag and path — verified this run by hashing the live raw fetch to the manifest value and `cmp`-ing it byte-identical with the committed snapshot. The Gate bullet also names the snapshot path on the same line, so the bytes each quote was copied from are identified. Residual (cosmetic, not dishonest): the blob URL is an HTML viewer page, not the hashed bytes, and an upstream force-retag of v0.45.1 would re-point the URL while the hash receipt `95147270…` remains the content anchor.

## Deliveries

- `.ufo/waves/round-30/w2/SwarmReviewer11.md` — this report.
- `.ufo/waves/round-30/w2/SwarmReviewer11-gc.rs` — tag bytes of `cli/src/commands/util/gc.rs` (sha256 `9c4d6a3704abb6f3afbb63cfd44153437b83d7e68d0f2426f84f8cdbbb0b4b9b`).
- `.ufo/waves/round-30/w2/SwarmReviewer11-receipts.txt` — fetch/hash/cmp receipt log.

Scratch `/fast/scratch/hyaku/souji-r30/SwarmReviewer11/` removed after staging. No lane file outside `.ufo/waves/round-30/w2/` was written; no git or jj mutation performed.
