# W2Assim — attack on `corpus/lessons/round-23.md` `### Assimilation decisions`

Seat: L1Souji23.W2Assim (wave 2, falsify). Target artifact: `corpus/lessons/round-23.md:88-112`
(`### Assimilation decisions`), tested against `PROVINCE.md` scope, `corpus/QUALITY.md` + the
fleet `CORPUS.md` bar, and the bytes at the lane tip (`4765250`, `c0eeaa7`).
Read-only. No install, no scratch dir, no lane mutation. Nothing outside
`/home/vgpnk/Projects/shokunin/souji-shokunin` was written, moved or deleted.

## Verdict

**survives — as an admission decision.** No entry that was admitted should have been refused, and
the section clears all four demanded checks (§Checks). **Entry 2 does not survive as landed
evidence** until F1–F3 are repaired: its own frontmatter contradicts its committed snapshot, its
central negative claim is not re-derivable from committed bytes, and one of its Gate locators
names a heading that exists only inside an HTML meta description in the declared snapshot. F4 is a
false bookkeeping claim repeated in the Gate and SCORECARD; F5–F6 are overstated ADMIT reasons.
None of these is an admission error; all are repair-or-disclose defects in the same landed block.

## Checks the item demanded

1. **Generic / sibling-domain?** No entry is sibling-domain. Both declare `ground: F2`, and F2 is
   souji's own frontier row (`PROVINCE.md:66-68`, which names `count-objects` explicitly). No
   mori/kagi/chousa/kumitate surface is touched. Entry 1's `git prune` paragraph
   (`corpus/knowledge/repo-size-census-readonly.md:35-40`) is F1-adjacent (git's own deleter), but
   it refuses the deletion reading in the same entry (`:50-52` "Nothing here recommends running
   either") and in the r13 entry's decision table (`corpus/knowledge/git-repo-structure-readonly.md:21`).
   Entry 2 is not generic filler — it is quoted, located, and corrects a staged falsehood — but its
   admitted delta is a curation caveat (see F5).
2. **≥1 ADMIT and ≥1 REJECT with a flip?** Yes, at both levels:
   ```
   $ for f in corpus/knowledge/repo-size-census-readonly.md corpus/knowledge/count-objects-garbage-readings-r25.md; do
       printf "%s ADMIT=%s REJECT=%s flip=%s\n" "$f" "$(grep -c '^- ADMIT' $f)" "$(grep -c '^- REJECT' $f)" "$(grep -c 'flip:' $f)"; done
   corpus/knowledge/repo-size-census-readonly.md ADMIT=7 REJECT=2 flip=2
   corpus/knowledge/count-objects-garbage-readings-r25.md ADMIT=4 REJECT=2 flip=2
   $ awk 'NR>=88 && NR<=113' corpus/lessons/round-23.md | grep -c '^ADMIT'; … '^REJECT'; … '^Flip:'
   2
   3
   3
   ```
   No flip is already met: no `*fleet-garbage-census*` file exists in the lane
   (`find . -name "*fleet-garbage-census*" -not -path "./.git/*"` → empty; the staged evidence is
   at `/home/vgpnk/Projects/shokuknow/lanes/souji/round3/evidence/r24-fleet-garbage-census.out`,
   outside the lane), the JA page holds `count-objects`/`size-garbage` zero times
   (`grep -c count-objects census/round-23/sources/qiita-gc-auto.raw` → `0`, same for
   `size-garbage`), and no `/var/tmp` `--lost-found` fixture exists.
3. **Every admitted entry's cited `S` row present?** Yes.
   ```
   $ awk -F'|' '/^\|[[:space:]]*S[0-9]+ /{n++} END{print n}' corpus/SOURCES.md          → 119
   $ awk -F'|' '… NF!=13 {n++} END{print n+0}' corpus/SOURCES.md                          → 0
   $ (duplicate-id check over column 2)                                                   → no output
   $ bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
   … 30 W04 duplicate-URL warnings … souji ok /…/corpus/SOURCES.md                       RC=0
   ```
   `S115–S119` are all rows, all `status=mined`, `used-by` pointing at the two admitted entries;
   `S115`=git-count-objects, `S116`=git-fsck, `S117`=git-prune, `S118`=Qiita, `S119`=CSDN. Every
   `S` id in entry 1 resolves (S035–S037, S115–S117); entry 2 resolves S118/S119. Its `S134`
   mention (`:37`) is explicitly labelled "in the staged package" and is absent from the lane
   registry — correctly not claimed as a lane row.
   The C3 counter agrees: `python3 tools/souji-gate-check.py … --entries <both> --snapshot-dir
   census/round-23/sources …` → `entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0` (RC 0).
4. **Any entry that should have been refused?** No. Both admissions are in-province, tier-B or
   tier-A, quoted, and bounded; the section's three REJECTs are all true of the bytes they describe
   (staged S112–S114 are the same documents as lane S115–S117 while lane S112–S114 are
   gio/GLib/statx — `SOURCES.append.md:10-12` vs `corpus/SOURCES.md:132-134`; the staged title
   "both target languages read `garbage` the same way" is verbatim
   `count-objects-garbage-semantics-r24.md:8`).

## Findings

### F1 — MEDIUM — entry 2's fetch counts and digests contradict its own committed snapshot (fix)

`corpus/knowledge/count-objects-garbage-readings-r25.md:3` — "curl rc=0; 129655 and 182147 bytes";
`:59` — "qiita 129655 bytes sha256 2020b283…; csdn 182147 bytes sha256 5a8b27ed…".

The declared snapshots say otherwise:
```
census/round-23/sources/qiita-gc-auto.raw:2   fetched: 2026-10-25, curl rc=0, 129547 bytes
census/round-23/sources/csdn-count-objects-vh.raw:2   fetched: 2026-10-25, curl rc=0, 180456 bytes
sha256: qiita 7d2298c139c128dd…  csdn 96aecd9198e70670…
$ grep -rn "2020b283\|5a8b27ed" . --exclude-dir=.git
./corpus/knowledge/count-objects-garbage-readings-r25.md:59
./.ufo/waves/round-23/w1/ScribeEntryGarbage.md:72,128
```
The digests bind full `.html` bytes that are committed nowhere in the lane (only bounded extracts
are). Two committed records give different byte counts for the same fetch (129655/182147 in the
seat report and the entry, 129547/180456 in the snapshot headers). Under `CORPUS.md` "a count
carries its command" and `QUALITY.md` Q17/Q55, this is an unbound count, and the two counts
disagree by 108 and 1691 bytes. **Round must fix**: reconcile the counts, and either commit the
full pages or state that `fetched:` binds uncommitted bytes.

### F2 — MEDIUM — entry 2's central negative and its section count are not re-derivable from committed bytes (fix)

`corpus/knowledge/count-objects-garbage-readings-r25.md:25-26` — "`count-objects` and
`size-garbage` appear nowhere in its bytes (grep -c → 0 for both)"; `:24` — "its eight sections are
all `gc.*` config".

The declared snapshot is `qiita-gc-auto.raw:3` "bounded extract, three spans +-400 bytes each" of a
~129.5 KB page. `grep -c` on the extract is 0 for both strings (I ran it), but absence in three
spans does not support "nowhere in its bytes" — the full bytes are not in the tree. Likewise the
extract holds two `<h2>` headings (`gc.autopacklimit (50)` at `:18`, one truncated at `:35`), so
"eight sections" is not derivable from committed bytes; it comes from a distinct-token grep in an
uncommitted wave-1 report (`.ufo/waves/round-23/w1/ScribeEntryGarbage.md:128`,
`grep -o -E 'gc\.[A-Za-z]+' … | sort -u` → 8 names) — a token count, not a heading count.
**Round must fix**: narrow the negative to the Gate spans or commit the greppable text; replace or
drop "eight sections".

### F3 — MEDIUM — entry 2's `§ 設定` locator is not a heading in its declared snapshot; Q54 passes it (fix + disclose)

`corpus/knowledge/count-objects-garbage-readings-r25.md:62` — "ADMIT: \"gc.auto (6700)\" — § 設定,
`gc.auto` heading — snapshot: census/round-23/sources/qiita-gc-auto.raw". In that snapshot the
string `設定` occurs once, at `:4`, inside
`<meta content="… 設定 git help config (v1.9.2) … gc.auto (6700) …">`; `gc.auto (6700)` also
occurs only there. There is no `設定` heading and no `gc.auto (6700)` heading in the extract.

Both gates pass anyway:
```
$ python3 -B tests/fixtures/r23-locator-heading.py --entries corpus/knowledge/repo-size-census-readonly.md \
    corpus/knowledge/count-objects-garbage-readings-r25.md --snapshot-dir census/round-23/sources
entries=2 locators=11 locators_bad=0   RC=0
```
Q54's text (`corpus/QUALITY.md:128`) requires the locator to "name a heading that exists in one of
the snapshot files"; the implementation tests token presence, which a meta description satisfies.
**Round must fix** the locator (re-anchor to the meta description, or commit the span carrying the
real heading) and **disclose** that Q54's check is token presence, not heading shape. This is the
one place where the round's own new criterion (R23-M7) is satisfied by a token it did not intend.

### F4 — MEDIUM — "snapshots … with their sha256" is false: no digest for any round-23 source is committed (fix)

`corpus/lessons/round-23.md:76` — "the man-page snapshots are committed under
`census/round-23/sources/` with their sha256"; repeated at `SCORECARD.md:23` ("snapshots
`census/round-23/sources/*` with sha256").

Computed digests `4c540915…`, `8ef1170b…`, `5282b2e1…`, `7d2298c1…`, `96aecd91…`; a grep of the
whole lane (excluding `.git`) for those prefixes returns **no hit**. `gate-check-c3.tsv` binds only
the tool digest. **Round must fix**: commit a snapshot-digest record (or drop the claim in both
places).

### F5 — LOW — ADMIT #2's "the difference is actionable" is unsupported (disclose)

`corpus/lessons/round-23.md:96-99` claims the difference is "actionable". The entry's only
consequence is a citation rule (`count-objects-garbage-readings-r25.md:48-52`), and the round's own
trend verdict (`:144`) names three actable consequences — `--lost-found` writes, `prune -n` ≠
`fsck --unreachable`, `alternate` must be read — **all from entry 1**. Not a refusal ground (the
entry is in-province and corrects a staged falsehood), but the ADMIT reason should name the
citation caveat instead of asserting actionability.

### F6 — LOW — ADMIT #1's "supplies the two halves … (the unreachable census and the size census)" overstates (fix wording)

`corpus/lessons/round-23.md:90-94`. The entry runs no census and says so
(`repo-size-census-readonly.md:56-58`, "No fleet repository was censused for this entry"), and
`PROVINCE.md:66-68` still states "whole-workspace size attribution and unreachable-object census
remain frontier". The round's own disposition of `CritC3Ground` (`:129`) restates C3 as the read
side "not as uncovered ground". Reword to "the documented read side for both".

## What I verified as true (so the record is not one-sided)

- Entry 1's quotes are all in its snapshots: `count-objects` field list incl. `garbage`/`size-garbage`/
  `alternate` (`git-count-objects.1.txt:25-35`); fsck blob-contents write sentence
  (`git-fsck.1.txt:70-72`); prune "unpacked … packed remain" (`git-prune.1.txt:15-21`).
- Entry 2's factual claims hold against the committed extracts: ZH table's last row is `garbage`
  with the size noun and no `size-garbage` row (`csdn-count-objects-vh.raw:65-66`, table 42-68);
  count rows use 数量/个数/数 and size rows 空间/大小; JA `count-objects`/`size-garbage` = 0; its
  four `ガベージ` occurrences are the title/meta and `軽量なガベージコレクション`; the 6700 sentence
  is at `:14`.
- Registry delta `114 → 119` reproduces (`git show 1208bfb…:corpus/SOURCES.md | grep -cE …` → 114;
  tip → 119; malformed → 0; census RC 0; gate `ok=2 fail=0`).
- The "by document" re-pointing is real: staged `S112/S113/S114` name git-count-objects/fsck/prune,
  the same documents as lane `S115/S116/S117`; lane `S112–S114` are gio(1)/GLib/statx.

## Residual risk and verification gaps

- I did not fetch the two live pages (certification OFF; the committed bytes are the evidence
  object). The entry's full-page digests and byte counts are therefore **unverified, not refuted**;
  F1 stands on the internal contradiction alone.
- F2's "nowhere in its bytes" could be true of the live page — I can neither confirm nor refute it
  from lane bytes, which is exactly the defect.
- Q54's implementation was read only through its behaviour (fixture output), not audited clause by
  clause; the token-vs-heading gap in F3 is demonstrated on this snapshot, not proven general.
- No re-run of the round's counters beyond the C3 gate/census arms; C1/C2 are out of this item's
  scope.
