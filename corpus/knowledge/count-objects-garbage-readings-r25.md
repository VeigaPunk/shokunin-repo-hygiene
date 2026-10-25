source: S118 — https://qiita.com/koseki/items/f1af58f1ec1693f0536a — tier B (community), JA
source: S119 — https://bbs.csdn.net/weixin_33940469/article/details/100327798 — tier B (community), ZH
verified-at: 2026-10-25 — both pages fetched live this round (curl rc=0; 129655 and 182147 bytes); no git-version claim is drawn from either
recheck: 180d — re-fetch both community pages live and re-grep each Gate span against the LIVE page bytes (the committed extracts cannot re-test claim 2's negative), and re-hash the committed extracts against census/round-23/sources/SHA256SUMS
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
fetched: 2026-10-25; the committed bounded extracts are `census/round-23/sources/qiita-gc-auto.raw` (sha256 7d2298c139c128dd…) and `census/round-23/sources/csdn-count-objects-vh.raw` (sha256 96aecd9198e70670…); the raw page fetches are volatile one-shots (per-response tokens) and are not reproducible, so the extract digests are the binding ones (Q1)

- ADMIT: "无法被 Git 识别的垃圾文件大小" — § 2.1 field table, `garbage` row — reason: the community gloss names the unrecognised-file reading this entry adopts, and its size noun is the unit error the body flags — snapshot: census/round-23/sources/csdn-count-objects-vh.raw
- ADMIT: "gc.auto (6700)" — § ガベージコレクション, `gc.auto` section — reason: the JA page's subject is gc config, which is what makes its ガベージ the collection rather than the field — snapshot: census/round-23/sources/qiita-gc-auto.raw
- ADMIT: "The default value is 6700. Setting this to 0 disables it." — § ガベージコレクション `gc.auto` section, quoted git-config text — reason: 6700 is git's default loose-object trigger, not evidence of any fleet setting — snapshot: census/round-23/sources/qiita-gc-auto.raw
- ADMIT: "a light-weight garbage collection" — § ガベージコレクション `gc.auto` section, quoted git-config text — reason: the only ASCII garbage on the JA page is the collection sense — snapshot: census/round-23/sources/qiita-gc-auto.raw
- REJECT: staged row S134 (own-work fleet garbage census, `lanes/souji/round3/evidence/r24-fleet-garbage-census.out`) — reason: the evidence lives outside this repository, so the row cannot be bound to a lane path or re-derived from lane bytes — flip: that `.out` is committed under `census/round-23/` with a receipt and a read-only re-run bound at a named revision.
- REJECT: staged claim that both target languages read `garbage` the same way — reason: the JA page holds no `count-objects` or `size-garbage` bytes and uses ガベージ for the collection, so the pages share no field reading — flip: a JA source that glosses the `garbage` field itself and states its unit.
