STATUS: DONE — The primary quote verifies verbatim (13 words) at the named anchor, but the drafted row is not the planned S054: source, kind, scope, every line anchor and the `mined` status belong to a v0.46.0 docs row (effectively S051), not to the v0.45.1 code row; corrected cells and a full corrected row below.

# ReopenS054 — `refs/jj/keep/*` re-opened independently (2026-10-20)

Scope: one unknown — does `w1/SrcJjKeepRefs.md`'s drafted SOURCES row hold against the sources it names, at the revision the round pins (S054 = `lib/src/git_backend.rs` at tag v0.45.1 + `cli/src/commands/util/gc.rs`)? Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`, landed tip ddb7347. No `jj`, no lane tool, no git write; the only file written is this report. No tool was installed.

## 0. Verdict

**PARTIAL / disagree on the row as S054.**

- The quote check itself **passes**: Q1 is character-exact on the served page, 13 words, at `#format-mapping-details`.
- The row **fails as S054**: it is a docs row (`kind: docs`) with `source` = docs.jj-vcs.dev, `scope` = "on jj v0.46.0", and every code anchor taken at v0.46.0. The round plan assigns S051 to the git-compatibility page and S054 to the v0.45.1 source files. The draft also proposes numbering it "next unused S051", which collides with that plan.
- The mechanics the draft reports are **true at v0.45.1 as well**, with different line numbers and one structural difference (`Backend::gc` + `Store::gc` wrapper at v0.45.1; inherent `pub fn gc` and `git_backend.gc(...)` at v0.46.0). Corrected anchors below.
- The `mined` status **fails on the citation rule**: the named `used-by` file exists on disk (uncommitted, 16 253 B) but cites no `S###` row at all, and its own "Source rows to number" list contains no code row for this mechanism.

## 1. Sources opened (2026-10-20)

| artifact | served status / identity | "last updated" line |
|---|---|---|
| `https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/lib/src/git_backend.rs` | 200, tag file, 2616 lines in reader capture | none (raw file; revision is the tag) |
| `https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/cli/src/commands/util/gc.rs` | 200, tag file, 67 lines | none (raw file; revision is the tag) |
| `https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/lib/src/index.rs`, `lib/src/store.rs`, `cli/src/commands/operation/abandon.rs` | 200, tag files | none |
| `https://docs.jj-vcs.dev/latest/git-compatibility/` | 200; title "Git compatibility - Jujutsu docs"; version resolved by site = **v0.46.0** (`versions.json`: `{"version":"v0.46.0","aliases":["latest"]}`) | **none** — `grep -in 'last updated\|last-modified\|article:modified\|git-revision'` = 0 hits |
| `https://docs.jj-vcs.dev/v0.45.1/git-compatibility/` | 200; same paragraph, quote appears 1× | none |
| `https://docs.jj-vcs.dev/v0.45.1/cli-reference/` | 200; `id="jj-util-gc"` 1×, 2-week sentence 1×, predecessor sentence 1× | none |
| `https://docs.jj-vcs.dev/v0.45.1/technical/architecture/` | 200; `refs/jj/keep` 1× | none |
| `https://jj-vcs.github.io/jj/latest/git-compatibility/` | `HTTP/2 301`, `location: http://docs.jj-vcs.dev/latest/git-compatibility/` (draft's claim exact) | n/a |
| `https://api.github.com/repos/jj-vcs/jj/releases/latest` | `"tag_name": "v0.46.0"`, `"published_at": "2026-10-07T21:28:17Z"` | n/a |

The draft's §3 access record is accurate on all of these points: no page-level "last updated" line is served; the latest alias resolves to v0.46.0; the served paragraph matches the tag file.

## 2. Primary quote check (the specific ask)

Draft Q1: "Commits created by `jj` have a ref starting with `refs/jj/` to prevent GC."

- **Character-exact:** yes, on the served latest page (after inline `<code>` markup) and in the tag files `docs/git-compatibility.md` at **v0.46.0:260** and **v0.45.1:229**. One sentence, terminal period included; no ellipsis, no edit.
- **Word count:** 13 (`Commits 1 created 2 by 3 jj 4 have 5 a 6 ref 7 starting 8 with 9 refs/jj/ 10 to 11 prevent 12 GC 13`). ≤25 ✓.
- **Anchor named:** `Git compatibility, § Format mapping details, #format-mapping-details`. The served page has `<h2 id="format-mapping-details">`; the quote is the only paragraph under it that mentions refs. ✓.
- **Version served:** latest = v0.46.0; the v0.45.1 versioned page also serves it (count 1).
- **What it does not say:** the literal `keep` namespace, which commits are held, or what deletes them. The draft says this correctly. Its own "assigned page" label is therefore the problem, not the quote: this sentence grounds S051, not S054.

## 3. Source-side observations at tag v0.45.1 (authoritative raw line numbers)

- `lib/src/git_backend.rs:100` — `const NO_GC_REF_NAMESPACE: &str = "refs/jj/keep/";`
- `lib/src/git_backend.rs:493-497` — import race guard: `// Create no-gc ref even if known to the extras table. Concurrent GC` / `// process might have deleted the no-gc ref.` then `.edit_references(head_ids.iter().copied().map(to_no_gc_ref_update))`.
- `lib/src/git_backend.rs:868-871` — ``/// Returns `RefEdit` that will create a ref in `refs/jj/keep` if not exist.`` / ``/// Used for preventing GC of commits we create.`` then `fn to_no_gc_ref_update(...)`, `let name = format!("{NO_GC_REF_NAMESPACE}{id}");`.
- `lib/src/git_backend.rs:900-967` — ``/// Recreates `refs/jj/keep` refs for the `new_heads`, and removes the other`` / ``/// unreachable and non-head refs.``; body deletes refs not in `new_heads` or with a non-hex name, **except** `if mtime > keep_newer` (`:941`), and comments "Also deletes no-gc ref of random name created by old jj." (`:947`); ref edits at `:961`.
- `lib/src/git_backend.rs:1466` — every commit written by the backend gets a keep ref: `.edit_reference(to_no_gc_ref_update(&id))` after "Everything up to this point had no permanent effect on the repo except GC-able objects".
- `lib/src/git_backend.rs:1558-1583` — `fn gc(&self, index: &dyn Index, keep_newer: SystemTime)` (a `Backend` trait impl method at v0.45.1), `new_heads = index.all_heads_for_gc()` filtered against the root commit (`:1561`), `recreate_no_gc_refs(&git_repo, new_heads, keep_newer)` (`:1564`), extras gc, `run_git_gc(...)` (`:1575`), packed-ref cache refresh (`:1583`).
- `lib/src/git_backend.rs:970-977` — `run_git_gc(...)`; `.arg(format!("--prune=@{} +0000", keep_newer.as_secs()))` (`:977`).
- `lib/src/index.rs:141-148` — `all_heads_for_gc` doc: "Heads among all indexed commits at the associated operation" … "returns the heads that should be preserved on garbage collection."
- `lib/src/store.rs:255-256` — `pub fn gc(&self, index, keep_newer)` → `self.backend.gc(index, keep_newer)` (the v0.45.1 wrapper; **absent at v0.46.0**, where `git_backend.gc(...)` is called directly).
- `cli/src/commands/util/gc.rs:26-29` — "Run backend-dependent garbage collection." + "run `jj op abandon ..<some old operation>` before `jj util gc`."
- `cli/src/commands/util/gc.rs:34-35` — "By default, only obsolete objects and operations older than 2 weeks are pruned."
- `cli/src/commands/util/gc.rs:49-58` — refuses a non-head operation; `None => now - 14*86400`, `Some("now") => now - ZERO`, other values rejected.
- `cli/src/commands/util/gc.rs:61-65` — `repo.op_store().gc(...)` (`:63`) then `repo.store().gc(repo.index(), keep_newer)` (`:65`).
- `cli/src/commands/operation/abandon.rs:40-43` — "Previous versions of a change (or predecessors) are also discarded if they become unreachable from the operation history." then "The abandoned operations, commits, and other unreachable objects can later be garbage collected by using `jj util gc` command."
- `CHANGELOG.md:4197`, `:4253-4254` — `## [0.14.0] - 2024-02-07`; "New `jj op abandon` command is added to clean up the operation history. Git / refs and commit objects can be further compacted by `jj util gc`." (Q4 verbatim across the wrap).
- `docs/git-compatibility.md:224, :229` and `docs/technical/architecture.md:72, :78-80` — Q1 and Q2/Q3 anchors at v0.45.1 (Q1 moved 260 → **229**).

**v0.46.0 vs v0.45.1 line drift** (draft's numbers are v0.46.0): `to_no_gc_ref_update` 869→870; `recreate_no_gc_refs` fn 901→902; `gc` fn 1566→1558; `all_heads_for_gc` call 1569→1561; `run_git_gc` call site 1580s→1575; `gc.rs` store call 67→65; docs Q1 260→229. `NO_GC_REF_NAMESPACE` is line 100 at both tags. The structural change at v0.46.0 (`Store::gc` removed; `pub fn gc` inherent) is not noted in the draft.

## 4. Per-cell verdict on the drafted row

Draft row (worktree `.ufo/waves/round-17/w1/SrcJjKeepRefs.md`, §5; not in ddb7347):

| cell | drafted text (abridged) | verdict | corrected cell text |
|---|---|---|---|
| id | `S0??` — "L1 numbers it — next unused is S051" | **disagree** | `S054`. ddb7347 `corpus/SOURCES.md` has 50 rows ending `S050` (line 64), so S051 *is* next unused, but the round plan already assigns S051 to the git-compatibility page and S054 to this source. A docs row here consumes S051 and leaves S054 undone. |
| source | "Jujutsu docs, Git compatibility and technical architecture — https://docs.jj-vcs.dev/latest/git-compatibility/" | **disagree** | "Jujutsu source at tag v0.45.1 — lib/src/git_backend.rs (`NO_GC_REF_NAMESPACE`, `to_no_gc_ref_update`, `recreate_no_gc_refs`, `Backend::gc`), lib/src/index.rs (`all_heads_for_gc`), lib/src/store.rs (`Store::gc`); CLI cli/src/commands/util/gc.rs and cli/src/commands/operation/abandon.rs — https://github.com/jj-vcs/jj/blob/v0.45.1/lib/src/git_backend.rs" |
| kind | `docs` | **disagree** | `code` (tagged upstream source; multi-file rows have precedent, S009). |
| tier | `A` | **agree** | `A` — tagged source is primary/authoritative for jj's own mechanism and the official docs corroborate; no `community` source involved. |
| scope | "purpose, holders and removal of `refs/jj/keep/` on jj v0.46.0; not git's own ref or GC semantics" | **disagree** (version; "holders" page-stated only for the docs half) | "what writes `refs/jj/keep/<commit-id>`, which commits they pin, and what deletes them, on jj v0.45.1; not git's own GC defaults and not jj operation-store retention after a keep ref is deleted" |
| anchor | all v0.46.0 lines + `CHANGELOG.md:4493-4494 (main @ 7dd5f92)` + docs latest | **disagree** | "tag v0.45.1: lib/src/git_backend.rs:100, :493-497, :868-871, :900-967, :1466, :1558-1583, :970-977; lib/src/index.rs:141-148; lib/src/store.rs:255-256; cli/src/commands/util/gc.rs:26-29, :34-35, :49-58, :61-65; cli/src/commands/operation/abandon.rs:40-43; corroborating docs at tag v0.45.1 docs/git-compatibility.md:229, docs/technical/architecture.md:78-80; CHANGELOG.md:4197, :4253-4254" |
| teaches | "jj refs every operation-log-reachable commit head under `refs/jj/keep/<commit-id>` so Git cannot collect hidden or abandoned history; only the manual `jj util gc` re-derives those refs and deletes the rest, by default after two weeks" | **disagree (overclaim x2)** | "jj writes `refs/jj/keep/<commit-id>` for each commit it writes and each Git head it imports and, at `jj util gc`, keeps one ref per indexed head while deleting the rest unless the loose ref is newer than the default two-week threshold; a commit held only by these refs can disappear after that command once it is no longer in the operation history" — see §4.1. |
| status | `mined` (with note "only once C3(c) lands the entry") | **disagree as written** | `queued`. Contract: `mined` = "cited by ≥1 path in `used-by`"; the named entry exists (16 253 B, uncommitted) but cites **no** `S###` row today and its "Source rows to number" list has no code row for this mechanism. Flip `queued → mined` in the round lesson only after the entry cites S054. |
| opened | `2026-10-20` | **agree** | `2026-10-20` (sources opened today; tag v0.45.1 and the versioned docs both served). |
| recheck | `on-release` | **agree** | `on-release` — upstream tag-pinned mechanism; re-open when a jj release changes the refs/GC path (it already changed shape between 0.45.1 and 0.46.0). |
| used-by | `corpus/knowledge/jj-colocation-receipts.md` | **disagree on timing** | `—` while `queued`; `corpus/knowledge/jj-colocation-receipts.md` once that entry cites S054. |

### 4.1 Why `teaches` overclaims

1. **"refs every operation-log-reachable commit head" understates the writer sites.** At v0.45.1 a keep ref is written for every commit the backend writes (`git_backend.rs:1466`) and for every imported Git head (`:493-497`), not only at `jj util gc` for operation-log heads. The steady-state set after `jj util gc` is one ref per `all_heads_for_gc()` id (`:1561`, `:900-967`).
2. **"only the manual `jj util gc` … deletes the rest" hides the mtime guard.** `recreate_no_gc_refs` skips deletion when the loose ref mtime is newer than `keep_newer` (`:941`) and deletes name-mismatched refs too (`:947`, `:961`). With the default threshold, refs younger than two weeks survive even if not in `new_heads`; `--expire=now` removes that protection (`gc.rs:49-58`).
3. **"only the manual" is version-dependent evidence.** The explicit "only call site" sweep in the draft (`grep -rn '\.gc(' cli lib | grep -v test` → `gc.rs:63, :67`, `git_backend.rs:1580`) was run on the v0.46.0 tarball. At v0.45.1 the chain is `gc.rs:65` → `Store::gc` (`store.rs:255-256`) → `Backend::gc` (`git_backend.rs:1558`), and I did not run a full-tree grep under this seat's probe bound; the claim is *observed for the opened files*, not proven absent. Keep "only" only if the v0.46.0 tarball evidence is cited, or restate as "the CLI path is `jj util gc`".
4. **"so Git cannot collect hidden or abandoned history"** is an inference (the draft marks it as such); the assigned page says only "to prevent GC". It should read as jj's stated purpose, not as an independently proven Git-semantics claim. The corrected text above avoids it.

## 5. Corrected row (registry column order, ready for L1 to number)

```text
| S054 | Jujutsu source at tag v0.45.1 — lib/src/git_backend.rs (`NO_GC_REF_NAMESPACE`, `to_no_gc_ref_update`, `recreate_no_gc_refs`, `Backend::gc`), lib/src/index.rs (`all_heads_for_gc`), lib/src/store.rs (`Store::gc`); CLI cli/src/commands/util/gc.rs and cli/src/commands/operation/abandon.rs — https://github.com/jj-vcs/jj/blob/v0.45.1/lib/src/git_backend.rs | code | A | what writes `refs/jj/keep/<commit-id>`, which commits they pin, and what deletes them, on jj v0.45.1; not git's own GC defaults and not jj operation-store retention after a keep ref is deleted | tag v0.45.1: lib/src/git_backend.rs:100, :493-497, :868-871, :900-967, :1466, :1558-1583, :970-977; lib/src/index.rs:141-148; lib/src/store.rs:255-256; cli/src/commands/util/gc.rs:26-29, :34-35, :49-58, :61-65; cli/src/commands/operation/abandon.rs:40-43; corroborating docs at tag v0.45.1 docs/git-compatibility.md:229 and docs/technical/architecture.md:78-80; CHANGELOG.md:4197, :4253-4254 | jj writes `refs/jj/keep/<commit-id>` for each commit it writes and each Git head it imports and, at `jj util gc`, keeps one ref per indexed head while deleting the rest unless the loose ref is newer than the default two-week threshold; a commit held only by these refs can disappear after that command once it is no longer in the operation history | queued | 2026-10-20 | on-release | — |
```

If L1 instead decides to keep the row at v0.46.0 (latest release), the draft's line anchors are correct as written (verified: const 100, `to_no_gc_ref_update` doc 867-868/fn 869, `recreate_no_gc_refs` fn 901, `pub fn gc` 1566, `.all_heads_for_gc()` 1569, `gc.rs` store call 67, docs 260), but the row still must not consume S051, still should be `kind: code`, and still needs the writer-site/mtime corrections in §4.1. The version choice is L1's; the plan currently says v0.45.1 and the lane's own observed evidence is jj 0.45.1.

## 6. Cross-item findings L1 should see

1. **S051 collision.** The knowledge entry's planned row list (`corpus/knowledge/jj-colocation-receipts.md:109-121`) already has a docs row for `git-compatibility` with "refs/jj/ GC ref" in scope. The drafted row duplicates it. Split: docs quote Q1 → S051; code row → S054.
2. **`mined` is uncited.** `grep -n '^source:\|^recheck:\|S05[0-9]\|refs/jj/keep\|util gc' corpus/knowledge/jj-colocation-receipts.md` returns no `S0xx` citation; the file's `source:` line points at its own "Source rows to number" section. Entry §3 line 28 says retention is "not documented in the pages read" and Limits line 98 calls it `[INFERENCE]` — both are true of the docs pages but false once S054's code evidence lands. The entry must be amended to cite S054 and state removal per `gc.rs:26-29`/`abandon.rs:40-43`, or the row stays `queued`.
3. **Census vs contract.** The frozen census only checks `[ -e "$p" ]` for `mined` rows (CORPUS.md census block), so a `mined` row with the uncommitted entry would pass the script while failing the contract's "cited by" wording. Don't use the census pass as the status justification.
4. **`jj util gc` also refuses a non-head operation** (`gc.rs:49-52`) and `--expire` accepts only `now` (`gc.rs:54-58`) — the draft's "2-week default / --expire=now" is right; the refusal is worth keeping in the knowledge entry because it gates the recheck recipe.
5. **The draft's §6 "Worktrees" and "GC of jj's own data" contradictions** were not re-opened here (outside S054); the versioned v0.45.1 page still says "git-worktree: No" and "no garbage collection … yet", while the v0.45.1 CLI reference already documents `jj util gc`. Relevant only to S051's scope; do not cite the stale clause.

## 7. Exact commands and outputs

Web (2026-10-20, all read-only):

1. `read https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/lib/src/git_backend.rs` (+ `:493-497`, `:868-871`, `:900-967`, `:1466`, `:1558-1583`, `:970-977` regions) and `read .../cli/src/commands/util/gc.rs` (full, 67 lines).
2. `curl -fsSL .../lib/src/git_backend.rs | grep -n 'const NO_GC_REF_NAMESPACE\|Create no-gc ref\|fn to_no_gc_ref_update\|fn recreate_no_gc_refs\|fn gc(&self, index\|all_heads_for_gc\|edit_reference(to_no_gc_ref_update\|fn run_git_gc\|--prune=@\|Also deletes no-gc ref\|if mtime > keep_newer'` →
   `100:const NO_GC_REF_NAMESPACE…`, `493: // Create no-gc ref…`, `870:fn to_no_gc_ref_update…`, `902:fn recreate_no_gc_refs…`, `941: if mtime > keep_newer`, `947: // Also deletes no-gc ref…`, `970:fn run_git_gc…`, `977: .arg(format!("--prune=@{} +0000"…`, `1466: .edit_reference(to_no_gc_ref_update(&id))`, `1558: fn gc(&self, index…`, `1561: .all_heads_for_gc()`.
3. `curl … git_backend.rs | grep -n 'edit_references(head_ids\|format!("{NO_GC_REF_NAMESPACE}\|new_heads.iter().map\|recreate_no_gc_refs(&git_repo\|run_git_gc(\|git_repo.refs.force_refresh'` → `497`, `871`, `961`, `1564`, `1575`, `1583`.
4. `curl … cli/src/commands/util/gc.rs | grep -n 'expire\|keep_newer\|is_at_head_operation\|\.gc(\|fn cmd_util_gc'` → `41 expire`, `44 pub async fn cmd_util_gc`, `49 is_at_head_operation`, `54 let keep_newer`, `57 --expire only accepts 'now'`, `63 .gc(slice::from_ref(repo.op_id())…`, `65 repo.store().gc(repo.index(), keep_newer)?`.
5. `curl … lib/src/store.rs | grep -n 'fn gc\|backend.gc\|\.gc('` → `255: pub fn gc(&self, index…`, `256: self.backend.gc(index, keep_newer)`.
6. `curl … lib/src/index.rs | grep -n 'all_heads_for_gc\|Heads among all indexed\|should be preserved on garbage'` → `54`, `141`, `145`, `148`.
7. `curl … cli/src/commands/operation/abandon.rs | grep -n 'Previous versions\|become unreachable\|garbage collected'` → `40`, `41`, `42` (doc lines 40-43).
8. `curl … v0.45.1/docs/git-compatibility.md | grep -n 'Commits created by\|^## Format mapping'` → `224:## Format mapping details`, `229:Commits created by …`; same for `architecture.md` → `72:### GitBackend`, `78:To prevent GC…`, `80:the refs/jj/keep/ namespace.`
9. `curl … v0.45.1/CHANGELOG.md | grep -n 'further compacted\|^## \[0.14.0\]\|^## \[0.6.0\]\|refs/jj'` → `4197:## [0.14.0] - 2024-02-07`, `4254:  refs and commit objects can be further compacted by \`jj util gc\`.` (bullet starts 4253; `refs/jj` count = 0).
10. `curl … v0.46.0/lib/src/git_backend.rs | grep -n …` → `100`, `869`, `901`, `1566`, `1569`; `curl … v0.46.0/docs/git-compatibility.md | grep -n 'Commits created by'` → `260`; architecture → `78`, `80`.
11. `curl … v0.46.0/lib/src/store.rs | grep -n 'fn gc'` → **no output**; `curl … v0.46.0/cli/…/gc.rs | grep …` → `67: git_backend.gc(repo.index(), keep_newer)?` (confirms the 0.45.1→0.46.0 shape change).
12. `curl -sI https://jj-vcs.github.io/jj/latest/git-compatibility/ | grep -i '^HTTP\|^location'` → `HTTP/2 301`, `location: http://docs.jj-vcs.dev/latest/git-compatibility/`.
13. `curl -s -o /dev/null -w 'v0451:%{http_code}\n' …` → `v0451:200`, `latest:200`; `curl … | grep -c 'Commits created by .*refs/jj/'` → `1` and `1`.
14. `curl -fsSL https://docs.jj-vcs.dev/latest/git-compatibility/ | grep -in 'last updated\|last-modified\|article:modified\|git-revision\|v0.46\|This is the documentation'` → no matches; same for the v0.45.1 page (no matches).
15. `curl -fsSL https://docs.jj-vcs.dev/versions.json` → `prerelease`, `v0.46.0` (aliases `latest`), `v0.45.1`, …
16. `curl -fsSL https://docs.jj-vcs.dev/v0.45.1/cli-reference/ | grep -c …` → `1` (`id="jj-util-gc"`), `1` (2-week sentence), `1` (predecessor sentence); v0.45.1 architecture `grep -c refs/jj/keep` → `1`.
17. `curl -fsSL https://api.github.com/repos/jj-vcs/jj/releases/latest | grep -m2 '"tag_name"\|"published_at"'` → `"tag_name": "v0.46.0"`, `"published_at": "2026-10-07T21:28:17Z"`.

Lane (read-only):

18. `git show ddb7347:corpus/SOURCES.md | grep -n '^| S05'` → line 64 `| S050 | Python built-in compile() …`; `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` → `50`.
19. `git cat-file -e ddb7347:.ufo/waves/round-17/w1/SrcJjKeepRefs.md` → `fatal: path … exists on disk, but not in 'ddb7347'`; `git cat-file -e ddb7347:corpus/knowledge/jj-colocation-receipts.md` → same; `stat -c '%n %s' corpus/knowledge/jj-colocation-receipts.md` → `16253`.
20. `grep -n '^source:\|^recheck:\|S05[0-9]\|refs/jj/keep\|util gc' corpus/knowledge/jj-colocation-receipts.md` → line 1 `source: see \`## Source rows to number\`…`, line 3 recheck, lines 25-29, 92, 98, 101; **no `S0xx` citation**.
21. `grep -n '^## \|^### ' corpus/knowledge/jj-colocation-receipts.md` and `grep -n -A12 'Source rows to number'` → rows at 109-121: git-compatibility, working-copy, bookmarks, config, git-comparison, concurrency, git-rev-list, two own-work reports, helper source — **no code row for `refs/jj/keep`**.

No lane tool was run; no `jj`; no git write; no `/var/tmp` scratch was needed; no installation.

## 8. Remaining unknowns

1. **Which tag S054 will pin.** The plan says v0.45.1; the docs latest is v0.46.0 and the draft used it. Both are fully anchored above; L1 must pick one, and the row must not mix the two (the `gc` call shape and `Store::gc` presence differ).
2. **Full-tree "only `jj util gc`" proof at v0.45.1.** I confirmed the opened chain (`gc.rs:65` → `store.rs:255-256` → `git_backend.rs:1558/1564`) and no other caller in the files opened, but a repo-wide grep at the tag was outside this seat's probe bound. The draft's exhaustive grep is v0.46.0-only.
3. **Whether the knowledge entry will be amended to cite S054.** Today it cites no row and calls retention `[INFERENCE]`; until amended, `mined` is not available under the contract.
4. **Exact retention after a ref is deleted** (op-store segment vs ref mtime) — the draft's §9 gap stands; the code at v0.45.1 does not resolve it either (`recreate_no_gc_refs` keys on `all_heads_for_gc()` and the loose-ref mtime, not on op-store retention).
