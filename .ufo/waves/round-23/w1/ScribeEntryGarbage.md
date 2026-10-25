# ScribeEntryGarbage — C3 entry 2 draft (target-language / community half of `garbage`)

## Status

STATUS: PASS — both community pages opened live this run, the draft claims no fleet figure,
rejects the staged own-work census row and the staged "same reading" sentence, cites only
S118/S119, and passes the lane's own gate predicate on the extracted draft. Two items need the
L1's hand: the snapshot bytes (I may not write the lane tree) and a path conflict between this
item's filename and the frozen C3 counter (Finding 1).

## Deliverable — apply at `corpus/knowledge/count-objects-garbage-readings-r25.md`

```markdown
source: S118 — https://qiita.com/koseki/items/f1af58f1ec1693f0536a — tier B (community), JA
source: S119 — https://bbs.csdn.net/weixin_33940469/article/details/100327798 — tier B (community), ZH
verified-at: 2026-10-25 — both pages fetched live this round (curl rc=0; 129655 and 182147 bytes); no git-version claim is drawn from either
recheck: 180d — re-fetch census/round-23/sources/qiita-gc-auto.raw and census/round-23/sources/csdn-count-objects-vh.raw, then grep each Gate span
ground: F2 — repository size census (what the two target-language communities say `garbage` counts, and what they do not say)

# The two target-language communities do not read `garbage` the same way: one glosses the field, the other means the collection

## Claim (F2, community tier — corroboration only, no fleet figure)
The round's other F2 entry holds the field's authority (git-count-objects(1)) and any
measurement. This entry records only what the two community pages say, at tier B, and
claims no count of its own.

1. **The ZH page glosses the field — and names it as a size.** Its `count-objects -vH`
   field table gives `garbage` as "无法被 Git 识别的垃圾文件大小": the size of garbage
   files Git cannot recognise. The unrecognised-files reading is the one this lane
   adopts; the unit is not. The same table labels its count rows 数量/个数/数 and its
   size rows 空间/大小, yet the `garbage` row — the table's last row, with no
   `size-garbage` row beside it — carries the size noun. git's own field list separates
   the two (`garbage` is a number of files, `size-garbage` their disk space), so a reader
   who takes the ZH row as the field's definition gets the unit wrong. The row
   corroborates the reading, not the unit.
2. **The JA page never glosses the field: its ガベージ is the collection, not the field.**
   The page is titled "Git のガベージコレクションについて" and its eight sections are all
   `gc.*` config. `count-objects` and `size-garbage` appear nowhere in its bytes (grep -c
   → 0 for both), and its only ASCII `garbage` sits inside the quoted git-config sentence
   about "a light-weight garbage collection". Its 6700 is the `gc.auto` loose-object
   default ("The default value is 6700. Setting this to 0 disables it.") — git's default,
   not a fleet setting.
3. **The staged sentence that both languages read the field the same way is unsupported by
   these pages.** One page reads the field as unrecognised files (unit aside); the other
   reads ガベージ as the collection process. They share no field reading, so that agreement
   claim is dropped here rather than inherited.

## What this does NOT establish
- **No fleet figure.** This lane holds no measured fleet `garbage` census. The staged
  entry's own-work row (S134 in the staged package,
  `lanes/souji/round3/evidence/r24-fleet-garbage-census.out`, sha256 c2df19ee…) is **not
  adoptable here**: that evidence lives outside this repository, so no lane path resolves
  it and it cannot be re-derived from lane bytes. This entry states no count, and nothing
  in it may be read as "the fleet has no debris".
- **Tier B is not authority.** Neither page authorises the field's meaning or the `gc.auto`
  value; the manual row does. The ZH article is partly paywalled after its § 2.1 table, so
  its later text is unread and unclaimed.
- Both pages are point-in-time copies. A re-fetch that no longer carries a Gate span flips
  that row, per the flips recorded in the Gate.

## Lane link and consequence
F2's community half is now bounded: one page supplies the field gloss (with a unit error
worth flagging), the other supplies the collection sense and the 6700 default. A future
census quote must take the unit from the manual and may cite S119 only for the
"unrecognised files" reading; S118 supports nothing about the field at all.

## Gate

url: https://qiita.com/koseki/items/f1af58f1ec1693f0536a
url: https://bbs.csdn.net/weixin_33940469/article/details/100327798
opened: 2026-10-25
fetched: curl rc=0 — qiita 129655 bytes sha256 2020b283cdb0b466f4e594180cb358a02f07319ad12c6e33eb078176fa21daa8; csdn 182147 bytes sha256 5a8b27ed3982a915b3b9a82b7d2ff1677f0d377a080be4c7367500bd06f65ab7

- ADMIT: "无法被 Git 识别的垃圾文件大小" — § 2.1 field table, `garbage` row — reason: the community gloss names the unrecognised-file reading this entry adopts, and its size noun is the unit error the body flags — snapshot: census/round-23/sources/csdn-count-objects-vh.raw
- ADMIT: "gc.auto (6700)" — § 設定, `gc.auto` heading — reason: the JA page's subject is gc config, which is what makes its ガベージ the collection rather than the field — snapshot: census/round-23/sources/qiita-gc-auto.raw
- ADMIT: "The default value is 6700. Setting this to 0 disables it." — § 設定 `gc.auto`, quoted git-config text — reason: 6700 is git's default loose-object trigger, not evidence of any fleet setting — snapshot: census/round-23/sources/qiita-gc-auto.raw
- ADMIT: "a light-weight garbage collection" — § 設定 `gc.auto`, quoted git-config text — reason: the only ASCII garbage on the JA page is the collection sense — snapshot: census/round-23/sources/qiita-gc-auto.raw
- REJECT: staged row S134 (own-work fleet garbage census, `lanes/souji/round3/evidence/r24-fleet-garbage-census.out`) — reason: the evidence lives outside this repository, so the row cannot be bound to a lane path or re-derived from lane bytes — flip: that `.out` is committed under `census/round-23/` with a receipt and a read-only re-run bound at a named revision.
- REJECT: staged claim that both target languages read `garbage` the same way — reason: the JA page holds no `count-objects` or `size-garbage` bytes and uses ガベージ for the collection, so the pages share no field reading — flip: a JA source that glosses the `garbage` field itself and states its unit.
```

Draft length: 66 lines (fence excluded), within the 70-line cap. The draft was extracted from
this report verbatim and run through the lane's own `tools/souji-gate-check.py` in a scratch
mirror with the two fetched snapshots and simulated S118/S119 registry rows:
`entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=0` (rc=0).

## Snapshot materialization (L1, before gate-check)

I am a read-only seat and may not write `census/round-23/`; the two files the Gate names must be
created by the L1, and the Gate's `check4` will refuse the entry until they exist. Exact recipe
(commands I ran this run, byte counts from my run):

```
mkdir -p census/round-23/sources
curl -sSL --max-time 40 -A 'Mozilla/5.0 (X11; Linux x86_64) souji-r23-scribe' \
  'https://qiita.com/koseki/items/f1af58f1ec1693f0536a' -o census/round-23/sources/qiita-gc-auto.raw
curl -sSL --max-time 40 -A 'Mozilla/5.0 (X11; Linux x86_64) souji-r23-scribe' \
  'https://bbs.csdn.net/weixin_33940469/article/details/100327798' -o census/round-23/sources/csdn-count-objects-vh.raw
grep -cF 'a light-weight garbage collection' census/round-23/sources/qiita-gc-auto.raw   # >=1
grep -cF '无法被 Git 识别的垃圾文件大小'      census/round-23/sources/csdn-count-objects-vh.raw # >=1
```

The digests above are informational (CDN/ads vary per fetch); the load-bearing invariant is that
each Gate span is present verbatim in the file the same Gate line names. If a span is absent, the
row is refused (flip already recorded) rather than the span being edited. **Land the two snapshot
files in the same commit as the entry, never after it:** the entry's `recheck:` line resolves the
same two paths, so a landed entry with missing snapshots fails both `check4` and QUALITY Q17.

My scratch (`/var/tmp/souji-r23-ScribeEntryGarbage/`) held the fetched bytes and the gate mirror
and is removed at the end of this seat, per the round's read-only bound — the curl recipe above is
the reproducible path, and its two `grep -cF` assertions are the acceptance check.

Naming: the companion entry's snapshots are landing as `census/round-23/sources/<page>.txt`
(`git-count-objects.1.txt`, `git-fsck.1.txt`, `git-prune.1.txt` were present when I finished). The
Gate here names `.raw` deliberately: my spans are verified against **fetched bytes**, and an
extractor may reflow or unescape text (the ZH table lives inside a JSON-escaped `\n` payload). If
the L1 prefers `.txt` for consistency, re-run the two `grep -cF` assertions on the extracted file
first and only then rewrite the Gate's `snapshot:` paths — an unverified rename would fail
`check4` on landing.

## Evidence

| command | output excerpt | revision |
|---|---|---|
| `read https://qiita.com/koseki/items/f1af58f1ec1693f0536a` (md-suffix) | title `Git のガベージコレクションについて`; `## gc.auto (6700)`; blockquote `When there are approximately more than this many loose objects…`; `The default value is 6700. Setting this to 0 disables it.` | live, 2026-10-25 |
| `read https://bbs.csdn.net/weixin_33940469/article/details/100327798` | § 2.1 table rows `count … 松散对象数量` … `garbage … 无法被 Git 识别的垃圾文件大小`; paywall `最低 0.47元/天 开通会员,解锁全文` after the table | live, 2026-10-25 |
| `curl -sSL … -o qiita-gc-auto.html` / `-o csdn-count-objects-vh.html` | `qiita rc=0 bytes=129655`; `csdn rc=0 bytes=182147` | live, 2026-10-25 |
| `sha256sum *.html` | `5a8b27ed3982a915…  csdn-count-objects-vh.html`; `2020b283cdb0b466…  qiita-gc-auto.html` | live, 2026-10-25 |
| `grep -c -F <span> <raw>` per span | all four Gate spans: `>=1` (qiita 2/2/4, csdn 2) | live, 2026-10-25 |
| `grep -o -F 'count-objects' qiita raw` / `'size-garbage'` (both pages) | `0` / `0` on the JA page; `0` `size-garbage` on the ZH page | live, 2026-10-25 |
| `grep -o -E 'gc\.[A-Za-z]+' qiita raw \| sort -u` | `gc.auto gc.autopacklimit gc.pruneExpire gc.reflogexpire gc.reflogExpireUnreachable gc.rerereresolved gc.rerereunresolved gc.aggressiveWindow` (8 sections) | live, 2026-10-25 |
| `read https://git-scm.com/docs/git-count-objects` | § OPTIONS `-v`: `garbage: the number of files in the object database that are neither valid loose objects nor valid packs`; `size-garbage: disk space consumed by garbage files` | live, 2026-10-25 |
| `read /home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/count-objects-garbage-semantics-r24.md` | staged entry: 1–5 (`source: S134 … r24-fleet-garbage-census.out`), claim 3 ("Both target languages read the field the same way") | staged package, read-only |
| `grep -n 'S11[0-9]\|S13[0-9]' corpus/SOURCES.md` + `grep -n 'F2' corpus/README.md` | registry tail S114 (max id 114); F2 row `frontier, no entry` at README:40, superseded by r13 row at :68 | lane base 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd |
| `sed -n '1,80p' tools/souji-gate-check.py` (checks 1–6) | `check4-snapshot-missing`, `check4-quote-absent-from-snapshot`, `check5-dangling-source`, `check6-no-admit` | lane base |
| `python3 tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries corpus/knowledge/count-objects-garbage-readings-r25.md --snapshot-dir census/round-23/sources --slice … --slice-verdicts …` in `/var/tmp/souji-r23-ScribeEntryGarbage/mirror` | `entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=0`, rc=0 | scratch mirror; lane `corpus/SOURCES.md` + simulated S118/S119 rows, entry extracted from this report, snapshots = the two fetched files |
| same command, 3 controls | snapshot removed → `check4-snapshot-missing-line-8`; S119 row dropped from the mirror registry → `check5-dangling-source: S119`; one Gate span mutated → `check4-quote-absent-from-snapshot-line-8` (each rc=1, each restored to green) | scratch mirror |

The git-scm page was opened for one purpose only: to fix the count-vs-size distinction the ZH row
gets wrong. It is **not** cited by id in the draft (S115 belongs to the companion entry and does
not exist in the registry yet), so nothing in the draft depends on that row landing first.

## Findings

1. **Path conflict, needs the L1's decision (not a defect I may repair).** The frozen C3 counter
   (preregistration §C3) names entry `corpus/knowledge/count-objects-garbage-semantics-r24.md`;
   this wave item names `corpus/knowledge/count-objects-garbage-readings-r25.md`. Landing only
   the item's filename leaves the frozen `--entries` list pointing at a missing file
   (`entry-missing`), which fails C3 with the contract unamended. Recommendation: land this
   draft at the prereg-named path; if the r25 filename is also required by a later contract, land
   it as a second path only with an explicit note that the frozen counter then counts 3 entries
   for a two-entry claim. I did not choose; the counter is frozen and I did not edit it.
2. **`garbage` unit error in the adopted ZH row (calibration).** The row the draft admits
   labels the field 大小 (size); git-count-objects(1) § OPTIONS `-v` makes `garbage` a count of
   files and gives `size-garbage` for the space. The draft admits the reading and rejects the
   unit in the same sentence, so the registry row's `teaches` cell must not repeat "size".
3. **The JA page cannot support a field reading at all.** `count-objects`: 0 occurrences;
   `size-garbage`: 0; ASCII `garbage`: 2, both inside the quoted "light-weight garbage
   collection" sentence; 8 sections, all `gc.*`. The staged entry's claim 3 ("both target
   languages read the field the same way") is therefore over-claimed on the JA side, and the
   draft drops it (Gate REJECT 2).
4. **Staged ids do not travel.** Staged S134 (own-work census), S138 (Qiita), S139 (CSDN) collide
   with nothing in this lane's registry (tail S114) but S134's evidence is outside the repo and
   S138/S139 are renumbered to the lane's S118/S119 — both rows are re-pointed by document, per
   CORPUS rule 1. No staged `opened` date (2026-10-23) or quote was carried; both pages were
   re-opened on 2026-10-25 and every Gate span comes from bytes I fetched this run.
5. **ScoutCommunity had published no verdict when I finished** (`agent://L1Souji23.ScoutCommunity`
   showed only its first sentence). Reachability is nevertheless confirmed by my own fetch: both
   pages HTTP 200 with `curl rc=0` and all four spans present. If ScoutCommunity later reports
   either page unreachable, the matching row flips to `refused` with that reason — the flip is
   already in the Gate, and the entry's body carries no claim that would survive the loss of
   either page.
6. **No fleet number anywhere in the draft.** No `count-objects` was run by me against any
   repository this run; the staged S134 figure is unmeasured here and is rejected, not quoted.
   The word "fleet" appears in the draft only in disclaimers.
7. **Line cap and gate predicate are measured, not asserted:** 66 lines; provenance trio present;
   `ground: F2`, `## Gate` with `opened: 2026-10-25`, 4 ADMIT + 2 REJECT (each with a reason and
   a flip), no `|` character in any Gate quote, every quote ≤25 words — and the lane's own
   predicate was executed on the extracted draft (Evidence row `scratch gate-check`), not inferred.

## Attack log

Not an attack item. Two observations against the frozen contract are filed as Findings 1 and 2;
neither predicate was edited, and no key set was narrowed.

## Out of scope / not done

- `corpus/SOURCES.md` rows for S118/S119 (ScribeSourcesRows drafts them; the `teaches` cell must
  carry Finding 2).
- `census/round-23/sources/*.raw` (L1 writes them; recipe above).
- `tools/souji-gate-check.py` was executed **only** in `/var/tmp/souji-r23-ScribeEntryGarbage/`
  against a scratch mirror (lane `corpus/SOURCES.md` + two simulated S118/S119 rows + the two
  fetched snapshots), never against the lane tree, and the scratch is removed at the end of this
  seat. `sources-census.sh validate` was read, **not run**. The lane's C3 counter on the real
  registry stays the L1's to execute at round end: unrun checks have not passed.
