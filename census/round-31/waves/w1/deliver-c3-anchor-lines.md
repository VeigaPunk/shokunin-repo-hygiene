# C3 source anchors — round 31, item C3Snapshots

Delivered with `deliver-fetch-receipts.tsv` and `sources/{git-reflog.adoc,gc.adoc,git-compatibility.md,SHA256SUMS}`
in `.ufo/waves/round-31/w1/`. L1 integrates the three snapshots to `census/round-31/sources/` keeping these exact
basenames; the receipt rows already name `census/round-31/sources/<basename>` and SHA256SUMS is keyed by basename.

| snapshot | bytes | sha256 | url |
|---|---|---|---|
| `census/round-31/sources/git-reflog.adoc` | 5657 | `59e7f0f15204a8c9f9b058ee62cb26aa2fa726b35dc85c702b75243424d6bf54` | https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-reflog.adoc |
| `census/round-31/sources/gc.adoc` | 7753 | `0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a` | https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config/gc.adoc |
| `census/round-31/sources/git-compatibility.md` | 12284 | `0fb71f992b0ed05d547e597d3f5f1cd33ed9e5d56a4e4e4cb851ba30c766c641` | https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/docs/git-compatibility.md |

All three fetches returned HTTP 200 at 2026-10-26T06:21:38Z (`curl -fsSL -m 60`). Every quote below is bracketed
between `<<<` and `>>>` and was checked this run as a verbatim, whitespace-collapsed substring of the named snapshot
(`python3 -B`: `re.sub(r"\s+"," ",quote) in re.sub(r"\s+"," ",file)`); word counts are `len(quote.split())`, all
inside the frozen 4..25 window. Copy the text between the markers byte-for-byte into the Gate span — backticks,
asterisks and apostrophes are part of the bytes. No quote contains a pipe or a double quote.

## F-A — `git reflog expire`

- `git-reflog.adoc:19` (locator `SYNOPSIS`), 5 words:
<<<
git reflog expire [--expire=<time>] [--expire-unreachable=<time>]
>>>
- `git-reflog.adoc:66-68` (locator `DESCRIPTION`), 23 words:
<<<
Entries older than `expire` time, or entries older than `expire-unreachable` time and not reachable from the current tip, are removed from the reflog.
>>>

## F-B — `--expire-unreachable`

- `git-reflog.adoc:119-121` (locator `OPTIONS`), 16 words:
<<<
Prune entries older than `<time>` that are not reachable from the current tip of the branch.
>>>
- `git-reflog.adoc:124-127` (locator `OPTIONS`), 8 words:
<<<
`--expire-unreachable=all` prunes unreachable entries regardless of their age
>>>
- `git-reflog.adoc:116-117` (locator `OPTIONS`), 10 words:
<<<
`--expire=never` turns off pruning of reachable entries (but see `--expire-unreachable`)
>>>

## F-C / F-D — `gc.reflogExpire` and `gc.reflogExpireUnreachable` defaults

- `gc.adoc:115-122` (locator `line 117`), 14 words, gc.reflogExpire default 90 days:
<<<
'git reflog expire' removes reflog entries older than this time; defaults to 90 days.
>>>
- `gc.adoc:124-132` (locator `line 126`), 22 words, gc.reflogExpireUnreachable default 30 days:
<<<
'git reflog expire' removes reflog entries older than this time and are not reachable from the current tip; defaults to 30 days.
>>>
- `gc.adoc:133-138` (locator `line 138`), 6 words, why the unreachable clock is shorter:
<<<
default is more aggressive than `gc.reflogExpire`
>>>

## F-E — what keeps an object reachable for gc/prune

- `git-reflog.adoc:145-148` (locator `line 148`), 15 words — reflogs are the hold older collectors failed to honour:
<<<
garbage collecting using older versions of Git, which didn't protect objects referred to by reflogs
>>>
- `gc.adoc:96-105` (locator `line 97`), 11 words — the prune clock `git gc` uses:
<<<
When 'git gc' is run, it will call 'prune --expire 2.weeks.ago'
>>>
- `gc.adoc:85-88` (locator `line 86`), 7 words — unreachable objects survive gc in cruft packs (default true):
<<<
Store unreachable objects in a cruft pack
>>>
- `gc.adoc:140-147` (locator `line 144`), 17 words — descendants of a listed id are kept with it:
<<<
any objects (and their descendants) mentioned in the output will be kept regardless of their true age
>>>
- `gc.adoc:99-102` states the `now`/`never` grace-period extremes but its bytes contain double quotes
  (`The value "now" ...`), so it cannot be copied into a double-quoted Gate span; paraphrase or skip it.
- Not stated in either fetched git page: the canonical keep-set sentence is in `git-gc(1)` NOTES
  (`objects referenced by the index, remote-tracking branches, reflogs ... and anything else in the refs/* namespace`).
  It is already pinned in-lane at `census/round-30/sources/git-gc.adoc:141-145`
  (sha `e3dbc4081095faf8d2d760eb4a47a1350f89d0c772f55eaada9cfbcdbeafba8c`), but that path is outside
  `--snapshot-dir census/round-31/sources`, so cite it as background only; a Gate quote of it needs its own
  round-31 pin plus receipt row. Negative sweep backing this: `grep -n -i reachab git-reflog.adoc` matches only
  lines 19, 67, 68, 116, 117, 119, 120, 123-126, 141, 145 — every match is about reflog entries, none about gc's keep set.

## F-F — jj v0.45.1 on HEAD and reflogs in colocated repos

- `git-compatibility.md:44-45` (locator `line 44`), 14 words — bold markers are part of the bytes:
<<<
* **Detached HEAD: Yes.** Jujutsu supports anonymous branches, so this is a natural state.
>>>
- `git-compatibility.md:52-54` (locator `line 52`), 16 words — git gc safety in a colocated workspace is untested:
<<<
It should be safe to run `git gc` in the Git repo, but it's not tested
>>>
- `git-compatibility.md:111-113` (locator `line 111`), 16 words — mixing commands is allowed:
<<<
It is allowed to mix `jj` and `git` commands in such a workspace in any order.
>>>
- `git-compatibility.md:114-117` cannot be used as a Gate span: those bytes contain literal double quotes
  (`repo in a "detached HEAD" state ... "currently tracked branch"`). Use lines 111-113 or paraphrase.
- `git-compatibility.md:229` (locator `line 229`), 13 words — the refs jj uses to hold commits against GC:
<<<
Commits created by `jj` have a ref starting with `refs/jj/` to prevent GC.
>>>
- Reflogs: **not mentioned at all** in this page at v0.45.1. Sweep: `grep -c -i reflog git-compatibility.md` -> `0`
  (258-line file). Do not attribute any reflog statement to the jj page; reflog behaviour for the colocated Git repo
  comes from the two git pages above.

## Gate wiring rules these anchors satisfy

`tools/souji-gate-check.py:80-113` requires, on each quoted Gate line: a locator token (`line `, `§`, `OPTIONS`,
`SYNOPSIS`, `DESCRIPTION`, ...) outside the quote, `snapshot: census/round-31/sources/<basename>` on that same line,
quote <=25 words, and the quote verbatim (whitespace-collapsed) in that snapshot under `--snapshot-dir`.
`census/round-31/c3-counter.py` L4 additionally keys `SHA256SUMS` by basename and `fetch-receipts.tsv` by the full
snapshot path with `http == 200`; L5 requires every Gate span to be 4..25 words. L4 shape was simulated over the
delivered files: 3/3 snapshots match SHA256SUMS and receipt sha256, sizes 5657/7753/12284, receipt keys
`census/round-31/sources/{git-reflog.adoc,gc.adoc,git-compatibility.md}`.

## Tooling

No installs; `curl` (system), `sha256sum`, `python3 -B` only. Scratch `/fast/scratch/hyaku/souji-r31/C3Snapshots/`
(created with `mkdir -p`, TMPDIR inside it) was removed after the copies landed in `.ufo/waves/round-31/w1/`.
