STATUS: PASS

# Slice138 — hand-check of register row `souji` / round3 / S138

Seat: leaf member, no subagent dispatch. Access date for every fetch below: **2026-10-25**.
All writes: this report plus the two named evidence snapshots only. No git/jj write, no index,
no `.ufo/state`, no registry edit, no cleanup action, no process signal.

## 1. Frozen row extraction (executed)

Command (field 4 is the id cell; the lane cell is field 2, anchoring the match to `souji` so no
other lane's rows can be parsed):

```
awk -F'|' '$2 ~ /`souji`/ && $4 ~ /S138/ {print NR": "$2"|"$3"|"$4"|"$5"|"$6"|"$7}' \
  /home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md
```

Observed output (register line 177, one match — the `tabi` S138 row at line 195 is excluded by
the lane cell):

```
177:  `souji` | round3 | S138 | `payload-absent` | https://qiita.com/koseki/items/f1af58f1ec1693f0536a | `## gc.auto (6700)`
```

Uniqueness check `awk ... | wc -l` → `1`. Lane slice ids as extracted: `S114 S123 S124 S126
S131 S133 S138 S118` (8 rows).

## 2. Fetch receipts (executed)

```
curl -sS -L --max-time 45 -A 'Mozilla/5.0 … Chrome/130 …' \
  'https://qiita.com/koseki/items/f1af58f1ec1693f0536a'
→ http=200 size=129655 type=text/html; charset=utf-8
  url=https://qiita.com/koseki/items/f1af58f1ec1693f0536a
  sha256=10773183118b0698f6d6951f0248c148e5f2e46a6962fa88162a43419cf516e2

curl -sS -L --max-time 45 'https://qiita.com/api/v2/items/f1af58f1ec1693f0536a'
→ http=200 size=16825 type=application/json; charset=utf-8
  sha256=bf7ddd62859a309b6da3e5304a8f6d029689cc4b52ceb452d48bbbc6824ca68a
  title="Git のガベージコレクションについて"  updated_at=2015-06-13T19:24:40+09:00
  url=https://qiita.com/koseki/items/f1af58f1ec1693f0536a
```

The second URL is the same item (`f1af58f1ec1693f0536a`) served by the same host's public v2
API; it is a representation of the cited source, not a different source.

### JS-rendered test (executed)

The article body is **server-side rendered**; this is not a JS-only page.
`<article` begins at byte offset 79294, the heading string `gc.auto (6700)</h2>` occurs at
82726, and the first `<script` after `<article` is at 101489 — i.e. the heading is in the
returned bytes before any script. Rendered-form element:

```
<h2 data-sourcepos="11:1-11:17">
<span id="gcauto-6700" class="fragment"></span><a href="#gcauto-6700">…</a>gc.auto (6700)</h2>
```

Section heading above it: `<h1 data-sourcepos="3:1-3:8"> … 設定</h1>`. The API item's
`rendered_body` contains `<h2`, confirming the same server-side rendering.

## 3. Located span and locator (executed)

- Exact span (4 words, ≤25): `## gc.auto (6700)`
- Primary locator: API item `body` (the article's own markdown source), **line 11**, inside
  section `# 設定` (body line 3). The article's own `data-sourcepos` for the rendered heading
  is `11:1-11:17`, so markdown line and rendered line agree.
- HTML locator: § 設定 (`<h1 data-sourcepos="3:1-3:8">`) › H2 `gc.auto (6700)`
  (`#gcauto-6700`, `data-sourcepos="11:1-11:17"`).
- Verbatim checks:
  - in saved markdown body: `grep -n -F '## gc.auto (6700)'` → `11:## gc.auto (6700)`;
    whitespace-collapsed match `True`; one occurrence.
  - in saved HTML bytes: `'## gc.auto' in html` → `False`; `'gc.auto (6700)' in html` → `True`
    (the renderer turns the `##` marker into `<h2>`; the marker itself is not HTML payload).

## 4. Saved snapshots (executed; sha256 of the saved file)

| file | bytes | sha256 |
|---|---|---|
| `evidence/slice138-qiita.txt` (byte-exact API `body`, no added header) | 3943 | `65ca1eddf555c57c0f17f40dda791e5c9c0d9cc945cf697d8cb7fb6eba652c28` |
| `evidence/slice138-qiita.html` (byte-exact fetched HTML) | 129655 | `10773183118b0698f6d6951f0248c148e5f2e46a6962fa88162a43419cf516e2` |

Paths are under `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/attempt2/w1/evidence/`.

## 5. Verdict for the row (frozen class)

**`S138	present	evidence/slice138-qiita.txt:11`**

Reason: the claimed quote is the article's own markdown heading line and appears **verbatim**
at line 11 of the item's `body` (`# 設定` at line 3), and its rendered counterpart `gc.auto
(6700)` is present in the cited page's server-rendered bytes under `#gcauto-6700`. The source
returned HTTP 200 with server-side text, so the row is neither `unverifiable` nor a
citation-class defect: the citation points at the web page where the text actually lives.

The register's `payload-absent` class for this row is a **false positive** of the quote census:
its eleven folds did not equate a markdown heading line (`## …`) with the `<h2>` element the
same bytes render, and the literal `## ` marker is absent from the HTML text nodes. No quote
correction is needed for the markdown form, so the class is `present`, not `accepted`. The
register is read-only for this seat; I am not rewriting its row or its class.

## 6. Bounded findings

1. Executed: row extraction is unique; the id cell in field 4 disambiguates it from the `tabi`
   S138 row (line 195), which was not parsed.
2. Executed: both the cited page and the same item's public API answered 200; the page body is
   server-rendered (heading before the first `<script>`).
3. Executed: saved markdown body contains `## gc.auto (6700)` at line 11; saved HTML contains
   the rendered `gc.auto (6700)` under `<h2 data-sourcepos="11:1-11:17">` but not `## gc.auto`.
4. Source-inferred (not executed as a probe): the census tool's matching model strips tags but
   not markdown heading markers, which explains the ABSENT signal. Stated as inference; the
   register's generator was not run.
5. Lane-local cross-reference, read-only: `/home/vgpnk/Projects/shokuknow/lanes/souji/round3/
   SOURCES-PROPOSED.md:23` anchors S138 as `§ 設定 "## gc.auto (6700)"` and its Gate (line 90)
   records `Quoted (§ 設定): "## gc.auto (6700)"` — the same form verified here, so the lane
   artifact and the register quote are the same string and the defect is in classification, not
   in the lane's citation.
6. No tool installed or updated during this seat; no channel used.
7. Lane bounds honoured: report plus the two evidence files only; no mutation, no deletion
   authority, no signal, no writes to the register, `.ufo/state`, index, or sibling repos.
