# SOURCES rows for C3 — object lifetime behind a dropped jj keep ref (r31 w1)

Registry read at lane base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc, working tree
`/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md`, sha256
`2488d6314ba6f411f221a445da615a7cec8cf367d78389fad4717ed129165588`, 145 rows, max id S221,
`## Registry` header at line 20, last row S221 at line 166. Append-only: the row below goes
directly after line 166, before the blank line that precedes `## Paths`.

## 1. Admitted row — S222

| S222 | git Documentation/git-reflog.adoc at tag v2.56.0 — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-reflog.adoc (served as https://git-scm.com/docs/git-reflog) | docs | A | what `git reflog expire` removes at git 2.56.0: entries past the expire time, and entries past the expire-unreachable time that are not reachable from the current tip, with the `all` and `never` sentinels; not which refs keep objects alive during gc (S063) and not the deletion scope of git-prune (S117) | Documentation/git-reflog.adoc at tag v2.56.0, 161 lines: :19 SYNOPSIS expire; :66-70 § DESCRIPTION; :111-117 --expire, :119-127 --expire-unreachable under § OPTIONS; HTTP 200, 5657 bytes, sha256 59e7f0f15204a8c9f9b058ee62cb26aa2fa726b35dc85c702b75243424d6bf54; opened 2026-10-26 | `expire` removes reflog entries older than the expire time, or older than the expire-unreachable time and unreachable from the current tip; the defaults are gc.reflogExpire 90 days and gc.reflogExpireUnreachable 30 days; `--expire=all` prunes regardless of age and `--expire=never` turns off pruning of reachable entries | mined | 2026-10-26 | on-release | corpus/knowledge/jj-dropped-keep-object-lifetime.md |

Field check: 11 cells, NF=13 in the pipe split; no cell contains a pipe character.
kind `docs` is in the validator enum (`spec|docs|paper|code|tool|dataset|talk|book|community|own-work`).
tier `A` is justified by the task frame: git's own `Documentation/` at the release tag, not a
third-party rendering. status `mined`; opened 2026-10-26; recheck `on-release`; used-by names the
C3 entry alone.

The source cell carries both the fetched URL and its served form, `(served as
https://git-scm.com/docs/git-reflog)`, in the style S220 already uses for its raw/served pair.
Reason: the wave-1 entry draft
(`.ufo/waves/round-31/w1/deliver-entry-jj-dropped-keep-object-lifetime.md`, Gate lines for S222)
cites `https://git-scm.com/docs/git-reflog` inside the Gate, and L6 of
`census/round-31/c3-counter.py:150-152` requires every `https://` URL in the Gate to occur in the
source cell of a cited row. The served URL is second in the cell, so `url_of()` still takes the
raw.githubusercontent URL for duplicate checks and the row stays unique. Local simulation of that
L6 expression over the draft and the mirror (not the counter run — the entry is not at a rev yet):

```
cited ['S002', 'S054', 'S063', 'S117', 'S220', 'S222']
gate_urls ['https://git-scm.com/docs/git-gc', 'https://git-scm.com/docs/git-reflog']
url_unbound []
```

Novelty sweep over the registry (`grep -c` on the file above): `git-reflog` 0, `reflog expire` 0,
`git reflog` 0, `--expire-unreachable` 0. No held row states the `git reflog expire` subcommand
contract, so S222 does not duplicate a row's teaching. Its URL is unique in the registry (the
validator printed no W04 and no E04 for S222).

## 2. S223 — refused (held coverage exists)

No S223 row is drafted. The two config keys are already carried by held row S002
(`git-gc(1) — https://git-scm.com/docs/git-gc`), whose cells read verbatim:

- scope: `git 2.55.0 grace periods on git's own deletions`
- anchor: `§ OPTIONS --prune, --expire-to; § AGGRESSIVE; § CONFIGURATION gc.reflogExpire, gc.reflogExpireUnreachable, gc.rerereResolved, gc.rerereUnresolved, gc.worktreePruneExpire; installed man page git 2.55.0-1`
- teaches: `defaults wait out grace periods: loose objects 2 weeks, reflog 90 days (30 if unreachable), worktree admin files 3.months.ago, rerere 60 and 15 days; --prune=now risks corruption under concurrent writers`

S002 names both keys in its anchor and states both default ages in its teaches cell, so a
`Documentation/config/gc.adoc` row at v2.56.0 would re-teach the same keys. The page was opened
anyway to confirm the values did not drift (HTTP 200, 7753 bytes, sha256
`0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a`): gc.reflogExpire at
`Documentation/config/gc.adoc:115-122` and gc.reflogExpireUnreachable at `:124-132` restate the
90-day and 30-day defaults S002 already carries.

Secondary note, [INFERENCE] (not opened this run): the rendered form of `Documentation/config/gc.adoc`
is included in the `git-config(1)` manual served at https://git-scm.com/docs/git-config, a URL
held by S042 (and, at another scope, S057); a served-URL row for the same page would therefore
also collide on URL. This is presented only as a secondary reason — the decisive one is S002's
held coverage of the two keys.

## 3. Located quotes (bytes opened this run; ≤25 words, no pipe)

Source bytes: `curl` of
https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-reflog.adoc (HTTP 200, 5657
bytes, sha256 `59e7f0f15204a8c9f9b058ee62cb26aa2fa726b35dc85c702b75243424d6bf54`, 161 lines) and
https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config/gc.adoc (HTTP 200, 7753
bytes, sha256 `0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a`, 181 lines).

Grounding the S222 teaches cell:

1. "Entries older than `expire` time, or entries older than `expire-unreachable` time and not reachable from the current tip, are removed from the reflog." — `Documentation/git-reflog.adoc:66-68` at tag v2.56.0 (23 words). Primary grounding: what `expire` removes.
2. "the expiration time is taken from the configuration setting `gc.reflogExpire`, which in turn defaults to 90 days" — `Documentation/git-reflog.adoc:113-115` (17 words). Grounds the 90-day default.
3. "`--expire=all` prunes entries regardless of their age; `--expire=never` turns off pruning of reachable entries" — `Documentation/git-reflog.adoc:115-117` (14 words). Grounds the two sentinels.
4. "setting `gc.reflogExpireUnreachable`, which in turn defaults to 30 days" — `Documentation/git-reflog.adoc:123-124` (9 words). Grounds the 30-day default for unreachable entries.

Supporting the S223 refusal (not a teaches cell, no row):

5. "'git reflog expire' removes reflog entries older than this time; defaults to 90 days" — `Documentation/config/gc.adoc:117-118` at tag v2.56.0 (14 words); the key is declared at `:115`.

## 4. Validation — scratch copy, exit 0

Scratch mirror (created under `/fast/scratch/hyaku/souji-r31/SwarmScribe16/`, `TMPDIR` set inside
it): `cp -a corpus` into `<B>/lane/corpus`, the S222 line appended after S221, plus the one
non-corpus used-by target (`tools/souji-size-census.py`) copied so the held rows' E11 checks see
their files. `diff -u` of the mirror against the lane registry shows exactly one added line (the
S222 row).

Command:

```
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file /fast/scratch/hyaku/souji-r31/SwarmScribe16/lane/corpus/SOURCES.md --today 2026-10-26
```

Output tail (full transcript has 37 lines: 36 W04 warnings + the ok line; no `\tE[0-9]{2}\t` line):

```
file	W04	S210 duplicate url raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c across scopes
file	W04	S216 duplicate url man7.org/linux/man-pages/man2/statx.2.html across scopes
file	ok	/fast/scratch/hyaku/souji-r31/SwarmScribe16/lane/corpus/SOURCES.md
exit=0
```

The 36 `W04` cross-scope warnings are pre-existing: validating an unmodified copy of the same
registry (same mirror, registry restored byte-identically) prints the same 36 lines and exit 0,
and `diff` of the two warning sets is empty. None of them names S222, and S222 raises no E01–E12.

Disclosure: the used-by target `corpus/knowledge/jj-dropped-keep-object-lifetime.md` is not in the
lane when the mirror was built or when the last validation ran (03:24 and 03:32): `ls` of
`corpus/knowledge/` shows only `jj-colocation-receipts.md` and `jj-keep-ref-expiry.md`; the wave-1
draft exists only as `.ufo/waves/round-31/w1/deliver-entry-jj-dropped-keep-object-lifetime.md`.
The mirror therefore carries a one-line validation placeholder at that path; the same command must
be re-run on the registry after the L1 lands the entry, where L11 of
`census/round-31/c3-counter.py` runs it.

The validation was re-run after the served URL was added to the source cell: same 37 output lines,
exit 0, no line naming S222.

## 5. used-by changes on held rows the entry cites (old -> new)

Rule for the L1: each held row cited by the C3 entry's `source:` lines gains
`, corpus/knowledge/jj-dropped-keep-object-lifetime.md` at the end of its used-by cell (append,
existing order preserved — the pattern already used by S218). No other cell changes.

Observed citations (not inferred): the wave-1 entry draft
`.ufo/waves/round-31/w1/deliver-entry-jj-dropped-keep-object-lifetime.md:1-6` carries six `source:`
lines naming S222, S063, S002, S117, S220 and S054; the local L6 simulation above reads exactly
`cited ['S002', 'S054', 'S063', 'S117', 'S220', 'S222']`. The entry itself is not yet committed
(`corpus/knowledge/jj-dropped-keep-object-lifetime.md` is absent in the lane), so if the L1
integrates a different `source:` set, trim this list to it. The concrete deltas for the five held
rows:

- S002: `corpus/knowledge/git-grace-periods-and-expire-to.md` -> `corpus/knowledge/git-grace-periods-and-expire-to.md, corpus/knowledge/jj-dropped-keep-object-lifetime.md`
- S054: `corpus/knowledge/jj-colocation-receipts.md, corpus/knowledge/jj-keep-ref-expiry.md` -> `corpus/knowledge/jj-colocation-receipts.md, corpus/knowledge/jj-keep-ref-expiry.md, corpus/knowledge/jj-dropped-keep-object-lifetime.md`
- S063: `corpus/knowledge/jj-colocation-receipts.md, corpus/knowledge/jj-keep-ref-expiry.md` -> `corpus/knowledge/jj-colocation-receipts.md, corpus/knowledge/jj-keep-ref-expiry.md, corpus/knowledge/jj-dropped-keep-object-lifetime.md`
- S117: `corpus/knowledge/repo-size-census-readonly.md` -> `corpus/knowledge/repo-size-census-readonly.md, corpus/knowledge/jj-dropped-keep-object-lifetime.md`
- S220: `corpus/knowledge/jj-keep-ref-expiry.md` -> `corpus/knowledge/jj-keep-ref-expiry.md, corpus/knowledge/jj-dropped-keep-object-lifetime.md`

S222 needs no update: it is new and already names the entry.
