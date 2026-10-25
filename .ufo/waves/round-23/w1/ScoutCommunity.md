# ScoutCommunity — C3 second entry: the two staged community sources, re-fetched live

STATUS: PASS — both cited pages exist and are reachable from this host on 2026-10-25 (HTTP/2 200
each, twice); the JA page states the `gc.auto` 6700 threshold, the ZH page states the `garbage`
gloss verbatim; both are `community` tier B. One accuracy caveat (ZH gloss mislabels the unit) and
one snapshot caveat (raw HTML digests are volatile) are recorded below; neither blocks the entry.

Lane base 1208bfb4924d. Preregistration read first (C3: entries=2, registry 114 -> >=117, ids
continue at S115). Read-only seat: this file is my only write; nothing under shokuknow was touched.

## Evidence

Fetch (both, 2026-10-25 08:11 GMT), `curl -sS -L -A '<browser UA>'`:

```
qiita  HTTP=200 SIZE=129655 https://qiita.com/koseki/items/f1af58f1ec1693f0536a
csdn   HTTP=200 SIZE=180364 https://bbs.csdn.net/weixin_33940469/article/details/100327798
HEAD qiita: HTTP/2 200  content-type: text/html; charset=utf-8  server: nginx  date: Sun, 25 Oct 2026 08:11:47 GMT
HEAD csdn : HTTP/2 200  server: openresty  date: Sun, 25 Oct 2026 08:11:48 GMT  content-length: 180094
            <link rel="canonical" href="https://bbs.csdn.net/weixin_33940469/article/details/100327798">
sha256 fetch1: qiita 8f0f425c3c8941b799dc2bf71df5f35edacd5ea55113132cf433c205d04b8d38
               csdn  bc187f430b19b2099a6186288cf63048b0d0b4dffcc20a805e4d476c0e74961a
sha256 fetch2 (same URLs, ~6 s later):
               qiita ccb83f4af39cd904b6ac05e5bf57490d05320bfc4e1db6931055e5b04d702db7 (129547 B)
               csdn  c50b8721e8a95c0c91a68bdef89c7e00c0f547fa12212cf0179b43203bb5d8a0 (182365 B)
```

Content stability across the two fetches (counts identical in both bodies): qiita `6700` x15,
`gc.auto (6700)` x5, the default-value sentence x2; csdn `无法被 Git 识别的垃圾文件大小` x2,
`默认 6700 个` x2, `的输出值得逐行看` x2. The `diff` of the whitespace-squashed bodies is ad/tracking
tokens only (`dist_request_id`, `silkroad_…`, ad `u=` hashes).

Corroboration that the 6700 value is current, not 2015-only: `git --version` = 2.56.0;
`man git-config | col -b | sed -n '3762,3772p'` gives gc.auto "…light-weight garbage collection
from time to time. The default value is 6700." (line 3766 of that extraction).

Registry state: `grep -cE '^\s{0,3}\|\s*S[0-9]{3,}' corpus/SOURCES.md` = 114, max id S114;
`grep -i 'qiita\|csdn\|koseki\|weixin' corpus/SOURCES.md` = no rows (so neither URL can trip E04 or
W04). `census/round-23/` does not exist yet — the snapshot dir is the L1's to create.

## Findings

1. **Qiita page — exists, reachable, states the 6700 threshold. Does NOT gloss `garbage`.**
   https://qiita.com/koseki/items/f1af58f1ec1693f0536a — title "Git のガベージコレクションについて",
   author `koseki`, `datePublished` 2015-06-13T18:52:41+09:00, `dateModified`
   2015-06-13T19:24:40+09:00. § 設定 contains `<h2>` "gc.auto (6700)" (sourcepos 11:1-11:17) and
   the blockquote at 21:1-21:59. Verbatim, located:
   § 設定, subsection "gc.auto (6700)", blockquote — "The default value is 6700. Setting this to 0 disables it."
   (The page's own Japanese restatement on the next line is "デフォルト 6700。0 で無効。")
   The page's two `garbage` occurrences are both inside the English quote at 17:1-17:106
   ("light-weight garbage collection"); it never mentions `count-objects` or the `garbage` field.
   So this page grounds **only** the threshold, and its own anchor is `git help config` v1.9.2 —
   it corroborates, it does not authorise. Tier call: **community, B** (`kind=community`, `tier=B`;
   E10 forbids community at tier A).
2. **CSDN page — exists, reachable, states the `garbage` gloss verbatim, and the 6700 number
   without naming `gc.auto`.** https://bbs.csdn.net/weixin_33940469/article/details/100327798 —
   title "Git仓库瘦身全攻略：诊断、清理与预防，告别.git目录膨胀", canonical points at itself,
   `"publishTime":"2026-09-19 05:45:09"`, byline account `weixin_33940469` (a WeChat-import mirror
   account; the page header shows "2,968原创"). § 2.1 "先看总量：count-objects 与 du", paragraph
   "git count-objects -vH 的输出值得逐行看", field table row `garbage` — verbatim, located:
   § 2.1 field table, row "garbage" — "无法被 Git 识别的垃圾文件大小"
   The same page states the threshold under § 1.2 "场景二：长期不执行 gc": "Git 的自动 gc 默认在
   「松散对象数量超过阈值」时触发（默认 6700 个）". `gc.auto` appears **0** times in the page — the
   number is stated, the config key is not. Tier call: **community, B**.
3. **Accuracy caveat on the ZH gloss (does not block, but the lesson must not repeat the unit).**
   The gloss says 大小 (size) for the `garbage` field; git's `garbage` is a **count of files** and
   `size-garbage` is the size (round 2's finding S130, and the field pair this lane's own census
   prints). The page's table has no `size-garbage` row (`size-garbage` x0). So the gloss
   corroborates the *referent* (files git cannot recognise) but mislabels the *unit*. The staged
   entry's sentence "Both readings match the measurement" should be tightened to "both readings
   agree on what the field points at; the ZH gloss mislabels its unit, the measurement settles it".
   `[INFERENCE]` for the "entry sentence should be tightened" part; the field/unit facts are observed.
4. **Both pages CAN be snapshotted for `census/round-23/sources/` — but not as raw HTML.**
   Three reasons, all observed: (a) raw digests are volatile — two fetches 6 s apart differ in
   sha256 while every quoted span is unchanged, so a receipt must bind the normalised extract, not
   the raw response; (b) `tools/souji-gate-check.py` check4 requires the squashed quote to appear in
   the squashed snapshot named on the same Gate line, and in raw HTML the CSDN row is
   `<td>garbage</td> <td>无法被 Git 识别的垃圾文件大小</td>` — a combined "garbage …gloss" quote
   would fail there, so quote the gloss cell alone or render the snapshot as a text extract
   (`garbage<TAB>gloss`); (c) 310 KB of boilerplate plus third-party text is the wrong thing for a
   hygiene lane to add — the CSDN HTML carries an unrelated 相关推荐 sidebar with other authors'
   article bodies, and the Qiita post is author-copyrighted with no redistribution licence. A
   ~1-2 KB bounded extract per page satisfies the gate and keeps the repo honest. Suggested names
   (L1 creates the dir): `census/round-23/sources/qiita-koseki-gc-auto-6700.txt`,
   `census/round-23/sources/csdn-weixin-count-objects-field-table.txt`, each headed by URL, HTTP
   status, fetch timestamp (2026-10-25T08:11Z), byte length and the fetch sha256 above, then the
   located section text. I did not write these files.
5. **Gate-line shapes that will pass** (for the L1's `## Gate`, so the two community rows land):
   one line per quote, each carrying a locator token, `opened: 2026-10-25`, `snapshot: <path>`, and
   ≤25 words with no `|` (they become SOURCES.md cells); plus at least one `- ADMIT:` and one
   `- REJECT:` line, and `source: S115`/`S116` ids that exist in `corpus/SOURCES.md` at the same
   revision (check5). Both quotes above are 10 words and 1 token respectively, contain no pipe, and
   each appears verbatim in its fetched body.
6. **No fallback needed.** The preregistered fallback (adopt with only the git-scm rows, record the
   community rows as rejected/unreachable) is not triggered: neither page was unreachable, neither
   returned a challenge page, neither redirected off its own canonical URL.

## Attack log

Not an attack item. One calibration-relevant observation offered as an ATTACK-shaped note, without
proposing any predicate change: C3's entry count is 2 and the ZH gloss is the only sentence in the
staged package that a reader could mistake for authority on the field's *unit*, and it is wrong on
the unit. If the round lands the entry unchanged, the lane ships a sentence ("Both readings match
the measurement") that its own census contradicts in one word. Repair belongs in the lesson text,
not in the frozen counter.
