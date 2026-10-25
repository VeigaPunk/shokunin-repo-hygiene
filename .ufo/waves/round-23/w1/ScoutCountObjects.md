# ScoutCountObjects — git-count-objects `-v` field list, quotes, write side effect

STATUS: PASS — live page opened 2026-10-25 (page text is 2.51.1, banner says "2.51.2 → 2.56.0 no changes"), installed man page present at git 2.56.0-1 and agrees field-for-field; neither documents any write side effect.

Lane base: `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` (`git rev-parse HEAD` in `/home/vgpnk/Projects/shokunin/souji-shokunin`, unchanged this run).
Serves: C3 (F2 repository size census, read side) → adopted id **S115**; SOURCES registry holds 114 rows, max `S114`, so `S115` is free.

## Evidence

1. Live page: `https://git-scm.com/docs/git-count-objects`, fetched twice this run (reader text + `:raw` HTML), access date **2026-10-25**. Version banner on the page: `git-count-objects last updated in 2.51.1` and `2.51.2 → 2.56.0 no changes` — so the live text is the text in force for host git 2.56.0.
2. Raw HTML downloaded to `/var/tmp/souji-r23-ScoutCountObjects/co.html` (26017 bytes) and the OPTIONS section paragraphs re-extracted with tag stripping + HTML-unescape, so every quote below is byte-checked against the page, not against a reader's reflow.
3. `man git-count-objects 2>/dev/null | head -80` → present, 50 lines total (the whole page fits inside the 80-line head; nothing was cut), `man -w` → `/usr/share/man/man1/git-count-objects.1.gz` (1102 bytes, `Sep 28 14:57`), footer `Git 2.56.0   2026-09-27`, `pacman -Q git` → `git 2.56.0-1`.
4. Anchors observed in the raw HTML: section `#_options`; option anchors `#Documentation/git-count-objects.txt--v` and `#Documentation/git-count-objects.txt---verbose`. The nine field paragraphs carry **no id of their own** — they are anonymous `<div class="paragraph"><p>` blocks inside the `-v` `<dd>`. The finest available locator for a field is therefore "§ OPTIONS, `-v, --verbose` field list, paragraph N", which is exactly the granularity the staged row already uses.
5. No tool installed or upgraded this run.

## Findings

**F1 — full `-v/--verbose` field list, in the page's own order** (page: § OPTIONS, anchor `#_options`, `-v`/`--verbose` `dd`; identical order in `man git-count-objects`):

| # | field | page's wording (units as printed) |
|---|---|---|
| 1 | `count` | the number of loose objects |
| 2 | `size` | disk space consumed by loose objects, in KiB (unless -H is specified) |
| 3 | `in-pack` | the number of in-pack objects |
| 4 | `packs` | the number of pack files |
| 5 | `size-pack` | disk space consumed by the packs, in KiB (unless -H is specified) |
| 6 | `prune-packable` | the number of loose objects that are also present in the packs. These objects could be pruned using `git prune-packed`. |
| 7 | `garbage` | the number of files in the object database that are neither valid loose objects nor valid packs |
| 8 | `size-garbage` | disk space consumed by garbage files, in KiB (unless -H is specified) |
| 9 | `alternate` | absolute path of alternate object databases; may appear multiple times, one line per path. Note that if the path contains non-printable characters, it may be surrounded by double-quotes and contain C-style backslashed escape sequences. |

Nine fields. `-H`/`--human-readable` is a separate option ("Print sizes in human readable format"), not a tenth field; it changes units of `size`, `size-pack`, `size-garbage` only. There is no field for reachable-object count, no field for object count by type, and no field for reclaimable bytes — the census must not read any of those out of `-v`.

**F2 — quote for `garbage`/`size-garbage`** (18 words, verbatim, no pipe character):
> `garbage: the number of files in the object database that are neither valid loose objects nor valid packs`

Location: `https://git-scm.com/docs/git-count-objects` § OPTIONS (`#_options`), `-v, --verbose` field list, paragraph 7 of 9; access date 2026-10-25. The pairing field, same list, paragraph 8 of 9 (13 words, verbatim, no pipe):
> `size-garbage: disk space consumed by garbage files, in KiB (unless -H is specified)`

Both re-read verbatim from `man git-count-objects` (lines 30-35 of the installed page): `garbage:  the  number of files in the object database that are neither` / `valid loose objects nor valid packs`, and `size-garbage: disk space consumed by garbage files, in KiB (unless  -H` / `is specified)`. Only the man page's justification spacing differs; the words are identical.

**F3 — quote for `alternate`** (15 words, verbatim, no pipe character):
> `alternate: absolute path of alternate object databases; may appear multiple times, one line per path.`

Location: same page, § OPTIONS (`#_options`), `-v, --verbose` field list, paragraph 9 of 9; access date 2026-10-25. The trailing sentence (double-quote/C-escape wrapping for non-printable paths) is on the same paragraph and matters to a census parser: `alternate` can emit **one line per path**, so a `-v` reader must not assume nine fixed lines. Installed man page agrees verbatim (lines 36-40).

**F4 — installed page present and in agreement.** `man git-count-objects` exists (`/usr/share/man/man1/git-count-objects.1.gz`, git 2.56.0-1) and its OPTIONS block lists the same nine fields in the same order with the same units and the same `prune-packable`/`garbage`/`alternate` wording. The man page adds nothing the web page lacks and omits nothing. Because the web page's own banner records "2.51.2 → 2.56.0 no changes", the two are consistent rather than merely similar. A `-v` parser written against either reads the other correctly.

**F5 — write side effect: the page documents NONE. Stated plainly.** The page's only behavioural sentence is DESCRIPTION: `Counts the number of unpacked object files and disk space consumed by them, to help you decide when it is a good time to repack.` Word scans for `writ*|delet*|remov*|mutat*|updat*|rewrit*|modif*` return **NO MATCHES** across the entire installed man page, and on the live page those words occur only in site chrome (a dark-mode `localStorage.removeItem`, the sidebar link to `git-write-tree`) — never in the command's own text. The two mutation-adjacent words present are advisory only, and neither is an action `count-objects` takes: `repack` ("decide when it is a good time to repack") and `prune-packable` ("These objects could be pruned using git prune-packed" — advice naming a *different* command). There is no `--lost-found`-style write flag, no `--force`, no cleanup option, and no NOTES/BUGS section at all; the page has exactly five sections (NAME, SYNOPSIS, DESCRIPTION, OPTIONS, GIT).
Caveat, labelled: [INFERENCE] this is a *documentation-absence* finding, not an empirical read-only proof — an undocumented lock or cache touch is not excluded by the page, and the lane's read-only receipts must lean on the separate `GIT_OPTIONAL_LOCKS` instrument (S036), not on this entry. What the entry may assert is bounded and useful: `count-objects -v` is documented as a pure reporter, in contrast with `git fsck --lost-found`, whose write side effect *is* documented (the C1 Sourced-ground distinction).

**F6 — ready SOURCES row material for S115** (row format per `corpus/SOURCES.md` line 19 header: `id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`):
- source: `git-count-objects(1), git 2.56.0 — https://git-scm.com/docs/git-count-objects`
- kind `docs`, tier `A`
- scope: the read side of an F2 size census — the nine `-v` fields, their units, and the documented absence of a write side effect; not a reachability census and not a reclaimable-bytes figure
- anchor: `§ OPTIONS (#_options), -v/--verbose field list; installed man page git 2.56.0 (2026-09-27)`
- teaches: `count-objects -v` reports loose count and size, in-pack count, pack count and size, prune-packable count, garbage count and size, and alternate paths — all as reporters, with no documented write
- opened: **2026-10-25** (this lane, this run)
- recheck: on host git upgrade — re-read `man git-count-objects`
- used-by: `corpus/knowledge/repo-size-census-readonly.md`, `corpus/knowledge/count-objects-garbage-semantics-r24.md`

**F7 — collision note for the C3 append (corroboration, not a new claim).** The staged package row at `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md` line 10 is staged **S112** and describes this same URL with a scope ("git 2.56.0 loose-object and pack census fields, including the garbage and alternate-database fields") that my re-open confirms is accurate; its staged `opened` date is 2026-10-23. Per preregistration the staged ids collide with this lane's real S112-S114 (quarantine rows, `corpus/SOURCES.md` lines 132-134) and the row must be re-pointed to S115 with `opened` 2026-10-25. The staged row's `teaches` cell is a paraphrase, not a <=25-word verbatim quote; the quotes in F2/F3 above replace it under CORPUS rule 1.

## Attack log

Not an attack item; no predicate, target or key set was edited or proposed for edit. One calibration remark for the L1, filed here rather than acted on: F1 shows `-v` carries **no reachable-object and no reclaimable-bytes field**, so any C3 row or counter that reads a "size" figure out of `count-objects -v` is reading loose-object KiB (`size`) or pack KiB (`size-pack`) only, and must say which — summing them silently would overstate what the census measures.

Shell scratch used `/var/tmp/souji-r23-ScoutCountObjects/` and was removed before finishing.
