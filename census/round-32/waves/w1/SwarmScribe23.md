# SwarmScribe23 — r32 w1 SOURCES rows for C3

Seat `SwarmScribe23-3`, item `ScribeSourcesRows`, wave souji-r32-w1, leaf member. Read-only seat:
wrote this report and `.ufo/waves/round-32/w1/deliver-sources-rows.md` only.

## Status

STATUS: PASS — two C3 registry rows (S223 gitformat-pack, S224 git-gc) drafted in the exact
11-column schema, each source opened by this seat from its raw tag URL at v2.56.0, each `teaches`
grounded by a located 14–19-word verbatim quote, the rows validated in a scratch copy with
`sources-census.sh validate` at exit 0 (E=0), and the `used-by` edits on the cited held rows stated
old → new. One provenance finding (config-fragment quotes attributed to a row whose scope does not
hold them) is reported with a conditional third row; it is the L1's decision, not a silent fix.

## Evidence

Lane base `85b61a151923986e7e6b48f7084b9122561b5f3d` (master); preregistration
`3ec84fc81b3243429c834a051880b0bcde06291c`; sources at tag `v2.56.0`; host `git version 2.56.0`;
opened and fetched 2026-10-26.

1. Sources opened by this seat (scratch fetch, http code from `curl -w '%{http_code}'`):

```
gitformat-pack.adoc http=200 bytes=27494 sha256=ec285ba4f4e15a68ad83a570eaf74e8549b477496e49933126ef935d9291381b lines=704
git-gc.adoc         http=200 bytes=6744  sha256=e3dbc4081095faf8d2d760eb4a47a1350f89d0c772f55eaada9cfbcdbeafba8c lines=187
config/gc.adoc      http=200 bytes=7753  sha256=0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a lines=181
```

All three are `cmp -s` byte-identical to the copies the C3 anchor seat staged at
`.ufo/waves/round-32/w1/sources/`, so its `SHA256SUMS` and `deliver-fetch-receipts.tsv` address the
same bytes these rows cite.

2. Validation of the rows (scratch registry copy, rows inserted after `S222`):

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file /fast/scratch/hyaku/souji-r32/C3Rows/lane/corpus/SOURCES.md --today 2026-10-26
… 36 pre-existing W04 shared-URL warnings, no E line, no S223/S224 line …
file	ok	/fast/scratch/hyaku/souji-r32/C3Rows/lane/corpus/SOURCES.md
EXIT=0        E=0  W=36
```

Pristine copy of the same registry: `EXIT=0 E=0 W=36` — the same 36 warnings, so the rows add no
finding (no `E04`, no `E11`). The rows were then re-extracted from the delivery file's own bytes and
revalidated twice (two rows and three rows): `EXIT=0 E=0 W=36`, `file ok` each time. Full output is
pasted in the delivery, §6.

3. Cruft coverage sweep that justifies S224 (no held row's scope claims it):

```
$ awk -F'|' '$2 ~ /^ S[0-9]/ {s=$6; if (s ~ /[Cc]ruft/) print $2": "$6}' corpus/SOURCES.md
(no output)
$ grep -Fc gc.cruftPacks      git-gc.adoc   -> 0
$ grep -Fc cruft-expiration   git-gc.adoc   -> 0
```

4. Quote locations were computed from byte offsets, not by eye (whitespace-reflowed substring
search over the fetched file), e.g. `gitformat-pack.adoc` quote → lines 655-656,
`git-gc.adoc` quote → 63-64, `config/gc.adoc` quote → 86-87.

Revision for every row claim: the registry at the lane base plus the two rows above; the emitted
blobs are the tag v2.56.0 documents whose sha256s are in the rows' anchor cells. I did not run
`census/round-32/c3-counter.py` (the L1's integration step), so no C3 leg result is claimed here.

## Findings

1. **S224 cannot ground `gc.cruftPacks`; the literal key is not in git-gc.adoc.**
   `Documentation/git-gc.adoc` v2.56.0 contains zero occurrences of `gc.cruftPacks` and of
   `--cruft-expiration` (both `grep -Fc` = 0); it reaches that text only through
   `include::config/gc.adoc[]` at `:136`. The key and the `repack --cruft --cruft-expiration`
   sentence are at `Documentation/config/gc.adoc` v2.56.0 `:85-89` and `:96-99`. S224's scope is
   therefore worded to the command-level bytes it does hold (`--cruft` on by default, `--no-cruft`,
   `--expire-to`, `--prune=<date>`), and the delivery carries a conditional S225 (config fragment,
   validated) for the key itself.

2. **The entry draft attributes config-fragment quotes to rows whose scope does not reach them.**
   At `.ufo/waves/round-32/w1/deliver-entry-jj-abandoned-object-mtime-clock.md:181-185` the Gate
   quotes `config/gc.adoc:86-88` and `:97-102` (`gc.cruftPacks`, `gc.pruneExpire`) under `S002`,
   whose registry anchor is `git 2.55.0` `§ OPTIONS --prune, --expire-to` plus the reflog/rerere/
   worktree keys (`corpus/SOURCES.md:23`) — `gc.pruneExpire` and `gc.cruftPacks` are absent from it.
   S063's anchor does reach `config/gc.adoc:96-147` (`corpus/SOURCES.md:84`), but its scope is
   "which refs keep objects alive during gc", not the cruft switch. This is the r31 routed defect 2
   (C3 entry traceability) in a new place; the quotes themselves are correct bytes (all 23 Gate
   quotes verified verbatim against my fetches), so the defect is row attribution, not quotation.

3. **L6 URL-binding hazard if the git-gc.adoc Gate lines are relabelled to S224.** The C3 counter
   takes `cited` only from `source:` front-matter lines and fails `url_unbound` when a Gate `https://`
   URL is absent from a cited row's source cell (`census/round-32/c3-counter.py:227-231`). Relabelling
   the Gate's `S063 … https://git-scm.com/docs/git-gc` lines to S224 without changing the URL and
   without adding `source: S224 …` would fail that leg. The delivery states the exact edit pair.

4. **No held row covers the cruft behaviour, and no duplicate URL is created.** Scope-cell sweep for
   `cruft` over the whole registry returns nothing; S004's scope is git-repack's `--expire-to` /
   `--drop-filtered` and its teaches only names the repack option. The raw tag URLs of S223/S224 are
   distinct from the served git-scm page held by S002/S063, and the validator raised no E04.

5. **`used-by` set derives from the draft's `source:` lines, not from guesswork.** The draft cites
   S223, S063, S002 (`deliver-entry-jj-abandoned-object-mtime-clock.md:1-3`). The two held rows get
   one appended path each (old → new spelled out in the delivery §4); S004/S054/S117/S220/S222 are
   cited by the earlier F1 entry, not by this draft, so they are left alone.

## Deliveries

- `.ufo/waves/round-32/w1/deliver-sources-rows.md` — the two paste-ready rows (S223, S224), the
  quote table with word counts and line spans, the S224 admissibility argument, the held-row
  `used-by` old → new edits, the validated output, the conditional S225 row, and the L1 integration
  notes.
- `.ufo/waves/round-32/w1/SwarmScribe23.md` — this report.

Out of scope and untouched: product code, counters, contract, registry, git/jj state, every path
outside `souji-shokunin/.ufo/waves/round-32/w1/`, `/home/vgpnk/Projects/shokuknow`. No tool installs
or upgrades. Scratch `/fast/scratch/hyaku/souji-r32/C3Rows` removed after the deliveries were written.
