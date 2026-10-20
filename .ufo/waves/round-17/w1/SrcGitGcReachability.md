STATUS: DONE — git-gc(1) keeps objects reachable from any refs/* ref (refs/jj/keep/* included) only while that ref exists; after deletion they are unreachable and pruned once their mtime passes the 2-week prune date (configurable to immediate). Drafted S051; nothing on the page contradicts C3(a) as written.

Seat: SoujiR17-3.SrcGitGcReachability (scout, W1 build, round 17). Lane base claimed 5fa6017ddcae9f6bd4412df44765f6360cb16294. I ran no `jj` subcommand, no git write, and none of the lane tools against a real directory. Files read: `corpus/SOURCES.md`, `CORPUS.md` § SOURCES.md, the named knowledge-entry path for an existence/citation check. No tools installed or upgraded.

## 0. Access record

| item | value |
|---|---|
| URL | https://git-scm.com/docs/git-gc, opened 2026-10-20 |
| fetch | `curl -fsS`, 67659 bytes, sha256 `2ca6d813939c066da22d2ac493ffbcf723dad201b64e71476bb2c52869d63a24` |
| version line served | "git-gc last updated in 2.52.0"; "2.53.0 → 2.56.0 no changes"; the 2.52.0 edition is stamped **2025-11-17** |
| host copy | `git version 2.56.0`, package `git 2.56.0-1`; `/usr/share/man/man1/git-gc.1.gz` sha256 `f3ffc655ae3a53ed96f38c25a8c6522f174b4193796d9c00f4d805b4ed2c69a5` |
| agreement | NOTES wording is byte-identical between the served page and the installed roff (line 412) |

Rendering caveat found while checking quotes (matters for "a quote names its location"): the web HTML inserts a space after a `<code>` span that ends a sentence — `gc.pruneExpire ).`, `git pack-refs .` — while the man render does not (`gc.pruneExpire).`). Each quote below names the rendering it was substring-checked in; quotes B and G are man-verbatim only.

## 1. Answer

### 1.1 Quotes (each ≤25 words, verbatim, mechanically substring-checked)

| # | verbatim quote | words | anchor | checked in |
|---|---|---|---|---|
| **A** | "it will keep not only objects referenced by your current set of branches and tags, but also objects referenced by the index, remote-tracking branches, reflogs" | 25 | § NOTES, first paragraph — web; installed git-gc(1) 2.56.0-1 roff 412 | web **and** man |
| **B** | "Prune loose objects older than date (default is 2 weeks ago, overridable by the config variable gc.pruneExpire)." | 17 | § OPTIONS `--prune=<date>` — man roff 112-113 | man only |
| C | "The value \"now\" may be used to disable this grace period and always prune unreachable objects immediately, or \"never\" may be used to suppress pruning." | 25 | § CONFIGURATION `gc.pruneExpire` — web; man roff 327 | web **and** man |
| D | "and anything else in the refs/* namespace" | 7 | § NOTES, first paragraph — web; man roff 412 | web only (man hyphenates "name‐/space" across lines 180-181) |
| E | "Any object with modification time newer than the --prune date is kept, along with everything reachable from it." | 18 | § NOTES, numbered point 1 — web; man roff 424-426 | web **and** man |
| F | "attached to an object does not contribute in keeping the object alive" | 12 | § NOTES, first paragraph — web; man roff 412 | web **and** man |
| G | "This variable determines whether git gc runs git pack-refs" | 9 | § CONFIGURATION `gc.packRefs` — man roff 285-297 (sentence at 290) | man only |

**Answer quote (survival leg): A.** The page's keep set is branches and tags, the index, remote-tracking branches, reflogs, "and anything else in the refs/* namespace". `refs/jj/keep/*` is a ref inside `refs/`, so objects reachable from it are kept while the ref exists.
**Answer quote (deletion leg): B.** Default prune date is two weeks ago; the config section adds that gc calls `prune --expire 2.weeks.ago` and `repack --cruft --cruft-expiration 2.weeks.ago` (roff 318-330). C shows a legal config collapses the grace to zero; E shows the clock is the object's mtime, not the moment the ref disappeared.

### 1.2 One paragraph

Observed: `git gc` "tries very hard not to delete objects that are referenced anywhere in your repository" and enumerates roots as branches/tags, index, remote-tracking branches, reflogs, and anything else under `refs/` (A, D). Because `refs/jj/keep/*` lives in `refs/`, a keep ref protects its closure exactly as a branch does. The page describes no ref-deletion path of its own, but DESCRIPTION's task list includes "removing unreachable objects"; once the keep ref is deleted nothing references the object, and the default prune date is two weeks (B). The grace is measured on object mtime (E), and `gc.pruneExpire=now` prunes immediately while `never` suppresses pruning (C). Default cruft packing (`gc.cruftPacks` true, `--cruft` on by default) changes the storage, not the window: the same two-week cruft expiration applies, and `--expire-to` only writes a copy of pruned objects elsewhere. So a receipt rooted in `refs/jj/keep/*` inherits the ref's lifetime — which git gc neither observes nor guarantees — plus a grace window; delete the ref and the grace is all that remains. That is not durability, which is exactly C3(a)'s NOT-SAFE, and never SAFE(metadata-prune).

### 1.3 Inference and unresolved gaps

- [INFERENCE] Presence is not durability: an existence probe (`git cat-file -e`) succeeds identically for an object held by `refs/heads/x`, by `refs/jj/keep/y`, and for one whose ref was just deleted but whose mtime is still inside the prune date (E). The page states no object-identity or provenance observable that distinguishes the roots.
- [INFERENCE] Post-deletion retention ends at whichever comes first: mtime crossing the prune date (default 2 weeks), `gc.pruneExpire=now`, or a `--prune=now` run. The page's own § OPTIONS warns `--prune=now` "increases the risk of corruption" under concurrent writers, so "now" cannot be treated as a safe default either.
- [UNKNOWN] Whether jj keep refs carry reflogs. The page keeps objects referenced by reflogs (default 90 days; `gc.reflogExpireUnreachable` 30 days for entries not reachable from the tip). A `logs/refs/jj/keep/...` file would extend retention past the mtime window; whether jj writes one is not on this page and I opened no jj source for it.
- [GAP/scope] HEAD: **0 occurrences** on the page. Its enumeration is branches, tags, index, remote-tracking, reflogs, `refs/*`; a detached HEAD is not a branch, so this page grounds neither "HEAD is kept" nor "HEAD is pruned". C3(a)'s "never HEAD" is consistent with the page but is not sourced from it; the nearest root is HEAD's reflog, which expires (90 days default).
- [SCOPE] The page says nothing about jj: **0 occurrences** of `refs/jj`. jj's deletion of keep refs and its rewrite model are the jj-document half of C3; S051 grounds only the git-gc half.

## 2. Drafted SOURCES row

Column order and constraints: 11 columns (NF=13), no `|` in any cell. `S051` is the next unused id — `grep -E 'S051|S052' corpus/SOURCES.md` printed no matches (2026-10-20) and the registry's last row is S050; L1 numbers it.

```
| S051 | git-gc(1) — https://git-scm.com/docs/git-gc | docs | A | git gc retention roots and the post-deletion prune window (web manual git-gc last updated in 2.52.0, 2.53.0 → 2.56.0 no changes); not jj's own ref lifecycle and not HEAD or refs/jj-specific behaviour | § NOTES first paragraph; § OPTIONS --prune=<date>; § CONFIGURATION gc.pruneExpire, gc.cruftPacks, gc.recentObjectsHook; web manual opened 2026-10-20; installed git-gc(1) 2.56.0-1 roff 112-113, 302-304, 318-330, 410-412 | gc keeps objects reachable from any refs/* ref, refs/jj/keep/* included, only while that ref exists; after the ref is deleted they are unreachable and pruned once the 2-week gc.pruneExpire grace passes (now = immediate), so object presence is not durability, and a git note does not keep its target alive | mined | 2026-10-20 | on-release | corpus/knowledge/jj-colocation-receipts.md |
```

Census on the drafted row, contract § Census commands, run from the lane root:

```
rows: 1
malformed: 0
tier: A=1
status: mined=1
enum: (no output)
used-by missing: (no output)
```

Landing caveat: `corpus/knowledge/jj-colocation-receipts.md` exists (`[ -e ]` → EXISTS), so the mechanical used-by check passes, but it does not yet cite the row (`grep -n 'S051'` → "no S051 citation yet"). The contract defines used-by as paths of entries *citing* the row. Smallest fix: add `S051` to that entry's `source:` line when C3(c) lands; if C3(c) will not cite it, flip `status` to `queued` and `used-by` to `—` — a sanctioned in-place status/used-by change, logged old→new in the round lesson.

## 3. Statements that contradict the context's claim text

**None contradicts C3(a) as written.** Three statements constrain its wording, and one contradicts a stronger, tempting reading that must not enter the lesson.

1. **Quote A contradicts "gc does not preserve refs/jj/keep objects".** A says `refs/*` content is kept; while the keep ref exists, gc treats `refs/jj/keep/*` like `refs/heads`. C3(a) does not say otherwise — it calls those refs non-*durable* roots, not non-roots — so the claim survives, but the lesson must attribute the loss to **ref deletion plus the mtime grace**, never to gc ignoring the ref. A sentence such as "git gc does not keep objects held only by jj keep refs" would be false against this page.
2. **Quote F contradicts a note-based receipt.** "a note … attached to an object does not contribute in keeping the object alive." Any later design that records a receipt as `git notes` on the object it must preserve is refuted here. C3 proposes no such design; flagged so it is not introduced as a repair.
3. **Quote G constrains "refs another tool owns".** gc runs `git pack-refs` by default (`gc.packRefs` default true), so a gc in the repository rewrites the jj keep refs' storage into packed-refs. The page states the packing and says nothing about jj's ability to read packed refs. [INFERENCE] this is a second reason a foreign ref is a poor receipt root: housekeeping it does not control mutates the receipt's substrate. Supporting constraint, not a contradiction.
4. **Silence is not contradiction.** HEAD: 0 occurrences. `refs/jj`: 0 occurrences. `refs/stash`: 2 occurrences, both only as a `gc.reflogExpire` / `gc.reflogExpireUnreachable` pattern example (web lines 462-475) — no retention statement specific to stash beyond the `refs/*` rule. Do not cite this page for "HEAD is pruned" or for jj's own ref retention rules.

## 4. Supporting observations useful to the lane

- C3(b)'s addition of `--glob=refs/jj/keep/*` is consistent with gc's root set (A), which counts keep refs as reachable. Boundary: this page defines **gc's** keep set, not rev-list's `--all`; it cannot ground `--all` semantics — that is git-rev-list(1)'s (not opened here).
- Cruft packs do not extend durability: `gc.cruftPacks` default true and `--cruft` on by default, but the packaging is `repack --cruft --cruft-expiration 2.weeks.ago` (roff 318-330); `--expire-to` writes pruned objects to another directory as a backup and "only has an effect when used together with `--cruft`" (roff 283-285).
- `gc.recentObjectsHook` is the only ref-free hold the page documents: hook output is read as object IDs treated as "recent" "regardless of their age", and "all must exit successfully, else the operation … will be halted" (roff 365-375, web § CONFIGURATION). It is per-invocation config output, not a repository fact; [INFERENCE] a receipt cannot be pinned this way without control of the host config.
- Retention clock is object mtime (E), and NOTES point 2 says writes refresh an existing object's mtime — so retention can also be a function of unrelated activity, never of a root.
- Nothing on the page promises a ref survives, is not repacked, or is not deleted; the `refs/*` protection is conditioned on the reference existing.

## 5. Commands run and outputs

```console
$ git --version; pacman -Q git
git version 2.56.0
git 2.56.0-1

$ zcat /usr/share/man/man1/git-gc.1.gz | grep -n -e 'tries very hard' -e 'refs/\*' -e 'Prune loose objects older' -e 'gc.pruneExpire' -e 'prune --expire 2.weeks.ago'
112:Prune loose objects older than date (default is 2 weeks ago, overridable by the config variable
412:\fIgit gc\fR tries very hard not to delete objects that are referenced anywhere in your repository\&. In particular, it will keep not only objects referenced by your current set of branches and tags, but also objects

$ zcat /usr/share/man/man1/git-gc.1.gz | awk 'NR>=110 && NR<=118 || NR>=410 && NR<=430 {printf "%d: %s\n", NR, $0}'
112: Prune loose objects older than date (default is 2 weeks ago, overridable by the config variable
113: \fBgc\&.pruneExpire\fR)\&. --prune=now prunes loose objects regardless of their age ... --prune is on by default\&.
412: \fIgit gc\fR tries very hard not to delete objects ... the index, remote\-tracking branches, reflogs (which may reference commits in branches that were later amended or rewound), and anything else in the refs/* namespace\&. Note that a note (of the kind created by \fIgit notes\fR) attached to an object does not contribute in keeping the object alive\&. ...
424: Any object with modification time newer than the
426: date is kept, along with everything reachable from it\&.

$ zcat /usr/share/man/man1/git-gc.1.gz | grep -n -e 'may be used to disable this grace period' -e 'repack --cruft' -e 'Store unreachable objects in a cruft pack' -e 'recentObjectsHook'
302:Store unreachable objects in a cruft pack (see
327:\fB\-\-cruft\fR)\&. Override the grace period with this config variable\&. The value "now" may be used to disable this grace period and always prune unreachable objects immediately, or "never" may be used to suppress pruning\&. ...
365:gc\&.recentObjectsHook

$ zcat /usr/share/man/man1/git-gc.1.gz | grep -n -e 'gc\&.packRefs' -e 'This variable determines whether'
285:gc\&.packRefs
290:in a repository renders it unclonable by Git versions prior to 1\&.5\&.1\&.2 ... This variable determines whether

$ mkdir -p /var/tmp/souji-r17-SrcGitGcReachability && curl -fsS -o .../git-gc.html https://git-scm.com/docs/git-gc
67659 /var/tmp/souji-r17-SrcGitGcReachability/git-gc.html
1        # grep -c 'git-gc last updated in 2.52.0'
1        # grep -c '2.53.0 → 2.56.0 no changes'

$ MANWIDTH=200 man --nj git-gc | grep -n -e 'Prune loose objects' -e 'prune --expire 2.weeks.ago' -e 'always prune unreachable'
47:  Prune loose objects older than date (default is 2 weeks ago, overridable by the config variable gc.pruneExpire). --prune=now prunes loose objects regardless of their age and increases the
135: When git gc is run, it will call prune --expire 2.weeks.ago (and repack --cruft --cruft-expiration 2.weeks.ago if using cruft packs via gc.cruftPacks or --cruft). Override the grace period
136: with this config variable. The value "now" may be used to disable this grace period and always prune unreachable objects immediately, or "never" may be used to suppress pruning. This feature

$ sha256sum /var/tmp/souji-r17-SrcGitGcReachability/git-gc.html /usr/share/man/man1/git-gc.1.gz
2ca6d813939c066da22d2ac493ffbcf723dad201b64e71476bb2c52869d63a24  .../git-gc.html
f3ffc655ae3a53ed96f38c25a8c6522f174b4193796d9c00f4d805b4ed2c69a5  /usr/share/man/man1/git-gc.1.gz
```

Verbatim/word-count assertions (Python, on the tag-stripped served page and the `man --nj` render):

```
Q1_survival:    words=25 web_verbatim=True  man_verbatim=True
Q2_prune:       words=17 web_verbatim=False man_verbatim=True   # web renders "gc.pruneExpire )."
Q3_refs_star:   words=7  web_verbatim=True  man_verbatim=False  # man hyphenates "name‐/space"
Q4_prune_now:   words=25 web_verbatim=True  man_verbatim=True
Q5_note:        words=12 web_verbatim=True  man_verbatim=True
Q6_mtime:       words=18 web_verbatim=True  man_verbatim=True
web HEAD count: 0 | web refs/jj count: 0 | web refs/stash count: 2 (both gc.reflogExpire examples)
man HEAD count: 0 | man refs/jj count: 0
2.52.0 date: 2025-11-17
```

Census on the drafted row (contract § Census, exact awk blocks): output in § 2.

## 6. Draft search-log entry for `## Search log`

**Round-17 git-gc retention roots (2026-10-20).** Question: does an object held only by `refs/jj/keep/*` have durable retention from git gc, and what governs it once that ref is deleted? Where: the live page https://git-scm.com/docs/git-gc (67659 bytes, sha256 `2ca6d8…`, opened 2026-10-20; served as "last updated in 2.52.0", "2.53.0 → 2.56.0 no changes") and the installed git-gc(1) 2.56.0-1 roff. Identified 1 document, screened 1, included 1 row (S051, tier A, scope: gc retention roots and the post-deletion window), excluded 0. Stop rationale: the page states the `refs/*` keep set, the 2-week prune default, its `now` override, the mtime rule, cruft packaging, `recentObjectsHook` and the notes caveat; jj's ref lifecycle, HEAD's treatment and any `--all` semantics are absent from the page and lie outside this row. Negative findings carry their sweep: 0 occurrences of `HEAD` and 0 of `refs/jj` in both the served page text and the man render.

## 7. Verdict and smallest fix

**Verdict: holds.** The page supports C3(a)'s operative conclusion through two facts — any `refs/*` ref keeps its closure while it exists (A), and deletion leaves the object unreachable with only an mtime-based 2-week grace (B, E) that config can shorten to zero (C) — and contains no statement contradicting the claim text. What it does **not** support: that gc ignores `refs/jj/*` (A refutes that), anything about HEAD, anything about jj.

**Smallest fix for L1:** (i) register S051 as drafted; (ii) word the C3 lesson as "a ref another tool owns, plus a prune grace, is not a durable root: drop the ref and only the grace is left", never "gc does not keep jj refs"; (iii) cite quotes A and B in `corpus/knowledge/jj-colocation-receipts.md`'s `source:` line so S051's used-by is true (today that file exists but contains no `S051`).
