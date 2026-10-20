STATUS: DONE — S063 primary quote passes independently (verbatim after HTML whitespace collapse, exactly 25 words, at § NOTES first paragraph); tier agrees, scope needs one wording fix, teaches carries two overclaims and one missing condition, status is premature until used-by resolves.

Seat: SoujiR17-3.ReopenS063-2 (scout, round 17 wave 2, FALSIFY). Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin` (jj-colocated, git HEAD `d7e648d5a1931e6dbacfd5be0587547afee15de3`, target landing `ddb73474433977ff54b015ac3e77669ff2537353`). I ran no `jj` command, no git write, no lane tool, no fixture, and no recursive read. No tools installed or upgraded. Scratch `/var/tmp/souji-r17-ReopenS063/` was created for the page copy and removed after the checks.

## 0. Access record (re-opened independently, 2026-10-20)

| item | value |
|---|---|
| URL | https://git-scm.com/docs/git-gc |
| fetch | `curl -fsS`, **67659 bytes**, sha256 `2ca6d813939c066da22d2ac493ffbcf723dad201b64e71476bb2c52869d63a24` |
| identity with wave-1 | byte-identical to the wave-1 fetch (`SrcGitGcReachability.md:9` records the same size and sha256), so this re-check is against the same served bytes, not a re-rendered variant |
| version line served | `git-gc last updated in 2.52.0` (1 occurrence); `2.53.0 → 2.56.0 no changes` (1 occurrence); the 2.52.0 edition link is stamped `2025-11-17` (1 occurrence) |
| host man | `/usr/share/man/man1/git-gc.1.gz`, git 2.56.0-1 |
| wave-1 report | `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-17/w1/SrcGitGcReachability.md` — **not in `ddb7347` or `HEAD`** (`git cat-file -e` rc 128, “exists on disk, but not in …”); its line numbers below are worktree-line numbers |

## 1. Primary quote A — PASS (with a precise whitespace caveat)

Drafted at `SrcGitGcReachability.md:23`, declared “Answer quote (survival leg): A” at `:31`:

> it will keep not only objects referenced by your current set of branches and tags, but also objects referenced by the index, remote-tracking branches, reflogs

| check | result |
|---|---|
| **verbatim on the served page** | **PASS** on the rendered text. The exact raw HTML span (starting at byte offset 64065) is `it will keep not only\nobjects referenced by your current set of branches and tags, but also\nobjects referenced by the index, remote-tracking branches, reflogs` — **2 newlines, 0 tags, 0 entities inside the quote**. Collapsing HTML whitespace (what a browser renders) yields a string **character-equal** to the draft quote (`rendered_equals_quote: True`). So it is verbatim modulo HTML source line-wrapping, not modulo any inline element. |
| **≤25 words** | **PASS, exactly 25** whitespace-delimited tokens. Zero margin: a hyphen-splitting counter (`[A-Za-z0-9]+`) sees **26** because of `remote-tracking`. If the registry counts whitespace tokens (as wave-1 and this seat do), 25; do not carry a “well under the cap” impression. |
| **anchor named** | **PASS.** The quote sits in the first `<p>` under `<h2 id="_notes">NOTES</h2>`, i.e. § NOTES first paragraph, exactly as the draft says. |
| **man cross-check claimed** | Consistent: roff 412 carries the same sentence on one line with `remote\-tracking` (escaped hyphen), so it is man-verbatim after roff rendering. |

**Verdict: agree.** Quote A is a valid primary quote for the survival leg. No correction to the quote itself. The only thing to record is the source-line-break caveat (a checker that refuses to collapse whitespace would report `False`; a checker that also inserts a space at inline-element boundaries would report a false divergence — see §5).

## 2. Version / last-updated line — PASS

The draft’s `SrcGitGcReachability.md:11` records exactly what the page serves: “git-gc last updated in 2.52.0”; “2.53.0 → 2.56.0 no changes”; the 2.52.0 edition stamped 2025-11-17. I re-derived all three from the fetched bytes. **Agree.** One precision: the served text is the 2.52.0 edition declared unchanged through 2.56.0; it is not a 2.56.0-stamped edition, and the row’s scope says so correctly.

## 3. Cell verdicts (tier / status / scope / teaches)

### tier — **AGREE, unchanged**

`A`. The URL is the official git project manual on git-scm.com; the registry already carries the same URL as tier A (S002). The edition self-declares equivalence through the host’s 2.56.0. No correction.

### status — **DISAGREE as landed; corrected text below**

The cell is registry process state, not a page statement, so it is judged against the registry’s own usage: every `mined` row carries a real citing `used-by`; `queued` rows carry `—` (S005–S008). As drafted, `mined` is coupled to `used-by: corpus/knowledge/jj-colocation-receipts.md`, and that path fails three ways:

1. not present at `ddb7347` — `git cat-file -e ddb7347:corpus/knowledge/jj-colocation-receipts.md` → `fatal: … exists on disk, but not in 'ddb7347…'`, rc 128;
2. not present at `HEAD` (`d7e648d`) — same fatal, rc 128;
3. not tracked — `git ls-files --error-unmatch` rc 1; and the worktree copy contains **no `S051` citation** (`grep -n 'S05[0-9]'` matches only line 1’s prose “see `## Source rows to number`”).

`corpus/SOURCES.md` at `ddb7347` has **0** occurrences of `S051` (`git show ddb7347:corpus/SOURCES.md | grep -c 'S051'` → `0`), so the id is free; the problem is only the claimed consumer.

Corrected cell text: **`queued`** (with `used-by` `—`) **until the same commit lands `corpus/knowledge/jj-colocation-receipts.md` tracked and citing S051**; at that point flip to `mined` with that path in the same in-place status/used-by change the draft already sanctions.

### scope — **AGREE with one wording fix**

What holds: “retention roots” is the page’s § NOTES enumeration; the version parenthetical is exact; “not jj’s own ref lifecycle”, “not HEAD” and “not refs/jj-specific behaviour” are honest — the page text contains **0** occurrences of `refs/jj` and **0** of `HEAD` (word-boundary, case-sensitive), so it grounds no jj rule and neither keeps nor prunes HEAD.

What overclaims: **“post-deletion prune window”**. The page never measures a window from the deletion; the grace is object-mtime-based (NOTES point 1: “Any object with modification time newer than the `--prune` date is kept”), with the default date two weeks ago. The draft itself says this at `:32` and `:39`, so the cell label contradicts its own evidence.

Corrected cell text:

> git gc retention roots and the mtime-based prune window governing an object after its ref is deleted (web manual git-gc last updated in 2.52.0, 2.53.0 → 2.56.0 no changes); not jj's own ref lifecycle and not HEAD or refs/jj-specific behaviour

### teaches — **PARTIAL: the last clause holds, three earlier clauses need correction**

Clause-by-clause against the page:

| clause | page basis | verdict |
|---|---|---|
| “gc keeps objects reachable from any refs/* ref” | NOTES: “anything else in the refs/* namespace” kept | holds |
| “refs/jj/keep/* included” | not on the page (`refs/jj`: 0 occurrences); valid **instance** of the refs/* rule, but a specific the page never names | holds as inference; must not be presented as a page statement (the scope’s own “not refs/jj-specific behaviour” is the correct boundary) |
| “only while that ref exists” | keep set is “objects that are referenced” at gc time | holds for the keeping-by-that-ref, but the sentence reads as object lifetime; the page keeps the index, remote-tracking branches and reflogs too, and an mtime inside the prune date holds an object independently |
| “after the ref is deleted they are unreachable” | DESCRIPTION: “removing unreachable objects” | **overclaims**: only if no other root references them. The cell drops the index/reflog/other-ref condition the same page states |
| “pruned once the 2-week gc.pruneExpire grace passes” | `--prune=<date>` default 2 weeks ago; `gc.pruneExpire` calls `prune --expire 2.weeks.ago`; prune on by default | **needs the clock stated**: the date is compared to object mtime (NOTES point 1), not to the deletion; “grace passes” invites a deletion-relative reading |
| “(now = immediate)” | `gc.pruneExpire`: value “now” disables the grace and prunes unreachable objects immediately | holds |
| “so object presence is not durability” | synthesis of the conditional keep set + mtime grace; explicitly `[INFERENCE]` in the draft (`:38`) but unmarked in the cell | holds as inference; should be phrased as conditioned presence, not a page claim |
| “a git note does not keep its target alive” | NOTES: “a note … attached to an object does not contribute in keeping the object alive” | holds verbatim in substance |

Corrected cell text:

> gc keeps objects reachable from any refs/* ref (so refs/jj/keep/*) while that ref exists; after it is deleted only another root (index, reflog, another ref) or an mtime newer than the prune date still holds them, and unreachable objects older than the gc.pruneExpire date (default 2 weeks ago, now = immediate) are pruned; so presence is conditioned on a live root at gc time, not durability, and a git note does not keep its target alive

## 4. Additional cell defect (not in the four asked, but affects the lesson)

**anchor**: it names `gc.recentObjectsHook` but its roff ranges `112-113, 302-304, 318-330, 410-412` do not cover it. Verified installed roff: `gc.recentObjectsHook` is at **365-370**; `gc.packRefs` is at **285-290**. `gc.packRefs` is used by the draft’s own §3 item 3 (a foreign ref’s storage is rewritten by gc’s default `pack-refs`) but appears in neither the anchor nor the scope, so that lesson sentence is currently unsourced by S051.

Corrected anchor text:

> § NOTES first paragraph; § OPTIONS --prune=<date>; § CONFIGURATION gc.pruneExpire, gc.cruftPacks, gc.recentObjectsHook, gc.packRefs; web manual opened 2026-10-20; installed git-gc(1) 2.56.0-1 roff 112-113, 285-290, 302-304, 318-330, 365-370, 410-412

(If §3 item 3 is dropped from the lesson, `gc.packRefs` and `285-290` may be omitted; `365-370` must be added either way because the anchor already names the hook.)

## 5. Secondary errata in the draft’s own cross-check table (does not change the verdict)

Read this as a warning not to propagate the “checked in” column, not as a defect in quote A:

- `:23` row B and `:150` claim “web renders `gc.pruneExpire ).`” and `web_verbatim=False`. At the **same sha256** the raw HTML is `…variable <span class='synopsis'><code>gc.pruneExpire</code></span>).` with **no space** before `)`. Whitespace-normalized, quote B **is** web-verbatim. The draft’s footnote is not reproducible.
- `:23` row D and `:150` claim the man hyphenates “name‐/space” across roff lines 180-181. Roff 180-181 is `gc.aggressiveWindow` prose (`See the documentation for the … --window option…`); the phrase “and anything else in the refs/* namespace” appears intact on **roff 412**, D’s own anchor. D is man-verbatim too.

Both look like checker artifacts (whitespace inserted at inline-element boundaries; a wrong roff line index). They make the draft claim *less* than the page supports, so they are harmless to C3 but must not enter the lesson or the registry as “web only / man only” facts.

## 6. Commands run and outputs

```console
$ mkdir -p /var/tmp/souji-r17-ReopenS063 && curl -fsS -o …/git-gc.html https://git-scm.com/docs/git-gc
$ wc -c …/git-gc.html; sha256sum …/git-gc.html
67659 …/git-gc.html
2ca6d813939c066da22d2ac493ffbcf723dad201b64e71476bb2c52869d63a24  …/git-gc.html

$ grep -o 'git-gc last updated in [0-9.]*' git-gc.html
git-gc last updated in 2.52.0
$ grep -o '2\.53\.0 → 2\.56\.0 no changes' git-gc.html
2.53.0 → 2.56.0 no changes
$ grep -o '2025-11-17' git-gc.html | wc -l
1
$ grep -o 'refs/jj' git-gc.html | wc -l
0
$ grep -c -E '\bHEAD\b' git-gc.html
0
$ grep -o 'refs/stash' git-gc.html | wc -l
2

$ python3  # exact-span check against the fetched bytes
exact_raw_repr: 'it will keep not only\nobjects referenced by your current set of branches and tags, but also\nobjects referenced by the index, remote-tracking branches, reflogs'
tags_inside_quote: []   entities_inside_quote: []   newline_count_inside: 2
rendered_equals_quote: True
whitespace_tokens: 25   hyphen_split_tokens: 26
heading: NOTES   h2_id: _notes

$ python3  # B cross-check at the same bytes
B_norm: True
raw: …variable <span class='synopsis'><code>gc.pruneExpire</code></span>).
```

```console
$ zcat /usr/share/man/man1/git-gc.1.gz | awk 'NR>=110&&NR<=116{…} NR>=300&&NR<=310{…} NR>=316&&NR<=332{…} NR>=362&&NR<=378{…} NR>=408&&NR<=414{…}'
110: \-\-prune=<date>
112: Prune loose objects older than date (default is 2 weeks ago, overridable by the config variable
113: \fBgc\&.pruneExpire\fR)\&. … --prune is on by default\&.
285: gc\&.packRefs
302: Store unreachable objects in a cruft pack (see
318-330: gc.pruneExpire … prune --expire 2.weeks.ago … repack --cruft --cruft-expiration 2.weeks.ago … "now" … immediately … "never" …
365-370: gc\&.recentObjectsHook … plain
410: .SH "NOTES"
412: … anything else in the refs/* namespace\&. Note that a note … does not contribute in keeping the object alive\&.
```

```console
$ git -C <lane> rev-parse HEAD
d7e648d5a1931e6dbacfd5be0587547afee15de3
$ git -C <lane> log --oneline -3
d7e648d round-17: r15 frozen preservation record regenerated at ddb7347 (computed verdict clean)
ddb7347 round-17: C1 census D1/D2, C2 seat-audit precision + r16 transcripts bundle, C3 jj-aware receipt roots/novelty, D6 gate exact ids + replays, vadv54 stub, regenerate verdict
5fa6017 round-16 verifier spot-check (integrator, hyaku): non-author admit/reject

$ git -C <lane> cat-file -e ddb7347:corpus/knowledge/jj-colocation-receipts.md
fatal: path 'corpus/knowledge/jj-colocation-receipts.md' exists on disk, but not in 'ddb7347…'   (rc 128)
$ git -C <lane> cat-file -e HEAD:corpus/knowledge/jj-colocation-receipts.md
fatal: … exists on disk, but not in 'HEAD'   (rc 128)
$ git -C <lane> ls-files --error-unmatch corpus/knowledge/jj-colocation-receipts.md
rc 1  (untracked)
$ git -C <lane> show ddb7347:corpus/SOURCES.md | grep -c 'S051'
0

$ grep -n 'S05[0-9]' corpus/knowledge/jj-colocation-receipts.md
1:source: see `## Source rows to number` …   (no S051 citation)
$ git -C <lane> cat-file -e HEAD:.ufo/waves/round-17/w1/SrcGitGcReachability.md
fatal: … exists on disk, but not in 'HEAD'   (rc 128; wave report is worktree-only)
```

No census, verify, vault, quarantine, gate, or fixture command was run; no write outside `/var/tmp/souji-r17-ReopenS063/` (removed) and this report.

## 7. Smallest fix for L1

1. **Keep quote A as the survival-leg quote**; add one clause to the access record: “verbatim after collapsing the HTML source’s two line breaks; no inline markup inside the span; 25 whitespace tokens (26 if hyphen-split)”.
2. **Scope**: replace “post-deletion prune window” with “mtime-based prune window governing an object after its ref is deleted”.
3. **Teaches**: use the corrected text in §3 — add the “another root” condition, state that the date compares to object mtime, and keep the note clause.
4. **Status/used-by**: as landed, `status` is `mined` with a `used-by` path that is absent at `ddb7347` **and** `HEAD` and cites no S051. Either (a) land the knowledge entry tracked with an `S051` citation in the same commit, or (b) land `status: queued`, `used-by: —`, and flip both in the commit that adds the citation. Do not land (a) as `mined` with an untracked, non-citing entry.
5. **Anchor**: add `365-370` for `gc.recentObjectsHook`; add `gc.packRefs` + `285-290` if §3 item 3 remains. Do not propagate the draft’s “web only / man only” footnotes for B and D (§5).

## 8. Remaining unknowns

- Whether jj writes `logs/refs/jj/keep/*` reflogs remains unknown and is **not** on this page; the page’s reflog retention (90 days / 30 unreachable) would extend the mtime window if such a reflog exists. The corrected teaches text deliberately keeps the “another root” escape hatch for this.
- The page does not define reachability itself (DESCRIPTION uses “unreachable”); that term’s formal definition is git-rev-list(1)/gitglossary territory and is not sourced by S051.
- Whether L1 will keep the draft’s §3 item 3 (packRefs mutates a foreign ref’s substrate) in the lesson; if not, the anchor correction can drop `gc.packRefs`, but the draft’s §3 item 3 would then have no S051 anchor.
