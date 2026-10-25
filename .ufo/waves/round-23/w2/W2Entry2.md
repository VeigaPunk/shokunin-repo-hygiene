# W2Entry2 — attack on `corpus/knowledge/count-objects-garbage-readings-r25.md` (C3, F2 read side)

Seat: L1Souji23.W2Entry2 (leaf, no dispatch). Mode: falsify, read-only.
Artifact under attack: `corpus/knowledge/count-objects-garbage-readings-r25.md`
Bytes attacked: **pristine export of lane tip `1026900`** (`git archive 1026900 | tar -x -C /var/tmp/souji-r23-w2-W2Entry2/tip`),
because the working tree went dirty under me mid-review (see § Concurrent drift). At the moment the
artifact was first opened its `git hash-object` was `9ea1d0bc…` = the tip blob, so the two agree on content
except the Gate location labels noted in § Concurrent drift.

Scratch: `/var/tmp/souji-r23-w2-W2Entry2/` (removed at end of seat).

---

## VERDICT

**survives** — all three numbered claims and all four Gate spans hold against the live pages and the
committed snapshots, including the two negative claims (`count-objects` = 0, `size-garbage` = 0 on the JA
page) and the ZH unit error. One **medium** defect (F1) sits in the Gate's `fetched:` provenance line, not in
any claim: the two page digests cannot be re-derived and the two byte counts do not match the snapshots the
entry's own `recheck:` names. One **low** procedural gap (F2): the stated recheck cannot re-test claim 2's
central negative.

---

## 1. The claim's own counting command (frozen in preregistration C3), re-run on the tip

```
$ cd /var/tmp/souji-r23-w2-W2Entry2/tip && python3 tools/souji-gate-check.py \
    --root /var/tmp/souji-r23-w2-W2Entry2/tip --round-date 2026-10-25 \
    --entries corpus/knowledge/repo-size-census-readonly.md \
              corpus/knowledge/count-objects-garbage-readings-r25.md \
    --snapshot-dir census/round-23/sources \
    --slice census/round-23/records/empty-slice \
    --slice-verdicts census/round-23/records/empty-verdicts
entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0
rc=0
```

`check_entry` verifies each Gate quote verbatim (whitespace-collapsed) in the snapshot its own line names
(`tools/souji-gate-check.py:9-13,84-114`), so `ok=2` is the instrument's own statement that all four spans are
present in `census/round-23/sources/{csdn-count-objects-vh.raw,qiita-gc-auto.raw}`. Instrument control, run
for this seat:

```
$ python3 tools/souji-gate-check.py --selftest
PASS fixture quote-absent -> fail …  PASS fixture long-quote -> fail …
PASS control always-green -> FALSE-GREEN-REJECTED [FALSE-GREEN-REJECTED]
selftest=9/9
```

Also run, per C3: `./scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → last line
`souji  ok  /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md`, `census rc=0`; no duplicate-url
row for S118/S119 (only S088-S108 rows are flagged).

---

## 2. Gate quotes, verbatim, in the committed extracts AND on the live pages

Live re-fetch this seat (2026-10-25, absolute URLs):

```
$ curl -sS -o q1.html -w 'qiita rc=%{http_code} bytes=%{size_download}\n' https://qiita.com/koseki/items/f1af58f1ec1693f0536a
qiita rc=200 bytes=129655
$ curl -sS -o c1.html -w 'csdn rc=%{http_code} bytes=%{size_download}\n' -A 'Mozilla/5.0 (X11; Linux x86_64)' https://bbs.csdn.net/weixin_33940469/article/details/100327798
csdn rc=200 bytes=180300
```

Counts at the tip snapshot vs the live page (`str.count`, exact bytes, not regex):

| Gate span | tip snapshot | live page |
|---|---|---|
| `无法被 Git 识别的垃圾文件大小` | `csdn-count-objects-vh.raw`: 1 | 2 |
| `gc.auto (6700)` | `qiita-gc-auto.raw`: 1 | 5 |
| `The default value is 6700. Setting this to 0 disables it.` | `qiita-gc-auto.raw`: 2 | 2 |
| `a light-weight garbage collection` | `qiita-gc-auto.raw`: 2 | 2 |

The 2-vs-1 factors are the pages' own double-embedding (Qiita ships the rendered HTML plus a `\u003c`-escaped
JSON copy; CSDN ships rendered table plus an embedded markdown payload). No span is paraphrased and none is
absent. All four are ≤25 words, so `check3` is satisfied on merit, not by a loose reading.

---

## 3. Claim 2 — "the JA page never glosses the field" (the load-bearing negative)

```
$ grep -c -F 'count-objects' q1.html   → 0
$ grep -c -F 'size-garbage'  q1.html   → 0
$ grep -o -i -F 'garbage' q1.html | wc -l → 2
$ python3 -c "…re.finditer('<h[1-3]…>')"
h1 'Git のガベージコレクションについて'
h1 '設定'
h2 'gc.auto (6700)'  h2 'gc.autopacklimit (50)'  h2 'gc.pruneExpire (2 weeks ago)'
h2 'gc.reflogexpire (90 days)'  h2 'gc.reflogExpireUnreachable (30 days)'
h2 'gc.rerereresolved (60 days)'  h2 'gc.rerereunresolved (15 days)'
h2 'gc.aggressiveWindow (250)'
```

- `count-objects` **0** and `size-garbage` **0** on the whole live page — claim 2's negative holds.
- "eight sections are all `gc.*` config" holds: exactly 8 `h2`, all `gc.*`, under `h1 設定`.
- The two ASCII `garbage` occurrences are the same sentence twice:
  `…perform a light-weight garbage collection from time to time.` at chars 83105 (rendered) and 115266
  (`\u003c`-escaped JSON). "its only ASCII garbage sits inside the quoted git-config sentence" holds.
- 11 × `ガベージ`, **0 standalone** (every one is `ガベージコレクション`) — "its ガベージ is the collection,
  not the field" holds.
- The 6700 default is git's, not a fleet setting, and it is still git's at the installed version:
  `man git-config` (git 2.56.0-1) lines 3762-3766: `gc.auto … The default value is 6700.` So the entry
  understates rather than overstates when it says "git's default".

---

## 4. Claim 1 — the ZH table, the count/size labelling, and the unit error

Table rows parsed from the tip snapshot (and re-parsed from the live page — identical):

```
['字段','含义']
['count','松散对象数量']            ['size','松散对象占用空间（已压缩）']
['in-pack','打包对象数量']          ['packs','pack 文件个数']
['size-pack','pack 文件总大小']     ['prune-packable','可被清理但仍以松散形态存在的对象数']
['garbage','无法被 Git 识别的垃圾文件大小']
```

- count rows → 数量/个数/数; size rows → 空间/大小. Exactly as claim 1 states ("数量/个数/数" and "空间/大小").
- `garbage` is the **last** of the 7 field rows; `size-garbage` count on the live page = **0**. "no
  `size-garbage` row beside it" holds.
- The unit error is real against the manual the lane already holds:
  `census/round-23/sources/git-count-objects.1.txt:30` `garbage: the number of files …`,
  `:33` `size-garbage: disk space consumed by garbage files`. A `大小` gloss on `garbage` misstates the unit.
- Paywall clause at `:43` holds: the rendered article body stops at the § 2.1 table (VIP banner at char
  46030, whose text is `最低 0.47元/天 开通会员,解锁全文`), and the embedded markdown payload's last heading is
  `2.1` (headings in payload: 1, 1.1, 1.2, 2, 2.1 — no 2.2). So the later text is genuinely not in the page
  bytes; "unread and unclaimed" is a fact, not a shortcut.
- Registry row `corpus/SOURCES.md:139` (S119) adds "restates a 6700 … threshold": supported — `6700` occurs
  twice on the live page, once in rendered body § 1.2 (`场景二：长期不执行 gc … （默认 6700 个）`).

---

## 5. Findings

### F1 — MEDIUM — the Gate's `fetched:` digests are unverifiable and its byte counts are not the snapshots' bytes

Files/lines: `corpus/knowledge/count-objects-garbage-readings-r25.md:59` (Gate `fetched:`), `:3` (`verified-at`),
against `census/round-23/sources/qiita-gc-auto.raw:2` and `census/round-23/sources/csdn-count-objects-vh.raw:2`.

`:59` declares `qiita 129655 bytes sha256 2020b283…; csdn 182147 bytes sha256 5a8b27ed…`. The snapshots the
entry's own `recheck:` (`:4`) names record **129547** and **180456** bytes. Measured this seat:

```
qiita (6 fetches): 129547 e76b1cc1…, 129547 4f3521a7…, 132084 8ba8b9d7…,
                   129655 17b14030…, 129655 691140be…, 129655 7ccdc715…
csdn  (4 fetches): 180973 97e913f4…, 180300 ed91cb05…, 179871 16b7363c…, 181153 2a7244d8…
```

- **Neither declared digest is reproducible, by construction.** Two qiita fetches at identical length differ
  in 127 blocks: 124 pure token substitutions (CSRF/tracking token at char ~1757, per-response UUIDs) and 3
  tiny `style`/`div` inserts. Content identical, digest different. Same for CSDN.
- **182147 was never observed** in 4 CSDN fetches (range 179871-181153) and is 1,691 bytes above the
  snapshot's own 180456.
- Consequence: the Gate's most precise-looking field is the one field a verifier cannot check, and the
  numbers the Gate declares describe a *different fetch* than the bytes the entry rechecks. This is the
  D3 defect class ("no receipt binds the named revision") that C2 exists to close, left open inside a Gate.

**Action: fix.** Bind the Gate to the durable artifact — add the snapshot digests
(`7d2298c1…` qiita, `96aecd91…` csdn; git blobs `8b703259…`, `ee1f4510…` at tip) — and either drop the two
page digests or label them "one-shot; page is response-volatile" with the byte counts marked approximate.
Do not leave a bare 64-hex claim that no re-fetch can reproduce.

### F2 — LOW — the `recheck:` procedure cannot re-test claim 2's negative

File/line: `corpus/knowledge/count-objects-garbage-readings-r25.md:4`.

The stated recheck is "re-fetch [the two snapshots], then grep each Gate span". The committed JA snapshot is a
bounded extract — three spans ±400 bytes (`qiita-gc-auto.raw:3`) — so `grep -c 'count-objects'` on it returns 0
whether or not the live page carries a count-objects section. Claim 2's load-bearing negative (the JA page
never glosses the field) therefore has no re-test in the entry's own procedure; only a whole-page fetch tests
it. The substantive flip at `:66` names the right condition, so this is procedural, not a wrong claim.

**Action: disclose or fix** — add "and grep the live page for `count-objects|size-garbage`" to `:4`.

### F3 — NIT — `verified-at` reads as if 129655/182147 were the snapshotted sizes

`:3`. They are not (129547/180456). Folded into F1's fix; no separate action.

### Passing cross-checks (recorded so a later seat does not re-do them)

- `REJECT: staged row S134` (`:65`): the named path does not exist —
  `find /home/vgpnk/Projects/shokuknow/merge/souji -name r24-fleet-garbage-census.out` → nothing. The REJECT
  is right; its reason ("lives outside this repository") merely under-states the case (absent, not just
  out-of-repo).
- S118/S119 registry rows (`corpus/SOURCES.md:138-139`) point at this entry, URLs unique, ids continuous from
  S115, no malformed/duplicate row from the census validator.

---

## 6. Concurrent drift (not a finding against the tip; needs the round's attention)

The working tree went dirty under this seat at 05:50:13. `git diff` against `1026900` shows the artifact and
its JA snapshot being edited by another seat:

- `count-objects-garbage-readings-r25.md`: Gate labels changed from `§ 設定` to `§ ガベージコレクション`.
  **This is a regression in location accuracy**: the page's section heading is `h1 設定` (verified above);
  `ガベージコレクション` is the page *title*, not a section. At the tip the labels are correct.
- `census/round-23/sources/qiita-gc-auto.raw`: spans re-cut, `h1` added, `note:` reworded; header still says
  `129547 bytes`.
- Also dirty: `LOG.md`, `SCORECARD.md`, `corpus/README.md`, `corpus/lessons/round-23.md`,
  `census/round-23/records/refusal-stale-digest.txt`, four `tools/`+`tests/fixtures/` files.

Verdict above is on `git archive 1026900`; nothing here was run against the dirty tree except the first
(dirty-free) gate-check. If the relabel lands, F1's fix should be applied in the same edit.

---

## 7. Residual risk and verification gaps

- [INFERENCE] "Paywalled" is inferred from `开通会员,解锁全文` + dual truncation; I did not test the page while
  logged in, so "paywalled" vs "server truncation with a VIP upsell" is unproven as a cause. The observable
  (later text absent from page bytes) is proven and is all the claim needs.
- I tested `gc.auto`'s 6700 default against installed git 2.56.0 only; I did not reproduce git 1.9.2, the
  version the JA page quotes. The entry claims "git's default", which the installed manual supports.
- The two pages are volatile in tokens/UUIDs; every statement above about live content is true of the
  fetches quoted here, not of a canonical page.
- Not attacked by me: C1/C2 instruments, `repo-size-census-readonly.md`, the S115-S117 manual rows beyond the
  two `garbage`/`size-garbage` lines cited.

---

## 8. Convergence with `W2Digests.md`

The W2Digests seat lands the same defect from a different angle (its § 3 "two community digests are
published"): F1 here is not a duplicate but the same defect reached from live re-fetch — this seat measured
the non-reproducibility, W2Digests measured the missing committed-side binding. Both actions reduce to:
publish digests of the committed extracts (or commit the pages the published digests bind). One refinement
their reading adds [INFERENCE of cause, their evidence]: the lane already holds two 129655-byte fetches with
different digests, so equal size + different digest is expected. My own byte-level diff of a 129547-byte
fetch vs a 129655-byte fetch attributes the 108-byte gap to three inserted blocks (a `data-emotion` style
rule, a `div class="style…` opener, a `></div` closer) — a conditional render block, not article content —
so the size split is conditional markup, not a second edition. The CSDN 182147-vs-180456 gap (1,691 bytes)
has no such attribution from this seat.
