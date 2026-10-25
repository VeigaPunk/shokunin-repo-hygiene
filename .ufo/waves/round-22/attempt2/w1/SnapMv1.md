# SnapMv1 — re-grounding snapshot: mv(1), `--no-copy` (C2 restorable-quarantine-staging)

STATUS: PASS

## 1. Snapshot identity

| Field | Value |
|---|---|
| Fetch date | 2026-10-25 (UTC clock at capture: 2026-10-25T06:45:42Z) |
| Requested URL | `https://man7.org/linux/man-pages/man1/mv.1.html` |
| Final URL after redirects | `https://man7.org/linux/man-pages/man1/mv.1.html` (0 redirects) |
| HTTP code | `200` |
| `%{size_download}` | `11693` |
| Raw snapshot | `.ufo/waves/round-22/attempt2/w1/evidence/snap-mv1.raw` |
| Raw bytes (`stat -c %s`) | `11693` |
| Raw sha256 | `d20b49ad254a0c791f788920218f60da657a2f8ef765ba681a0f63fd2053ed0c` |
| Text snapshot | `.ufo/waves/round-22/attempt2/w1/evidence/snap-mv1.txt` |
| Text bytes (`stat -c %s`) | `4610` |
| Text sha256 | `18dc9c2185fbf2b8839e780b2a9a88fdf392ffeff311785086c807a5aa4e6687` |
| Text format | UTF-8 plain text, 174 lines, tags/style/script stripped, words in document order |
| Declared source identity on page | GNU coreutils 9.11, April 2026, `MV(1)` (footline, txt L155; COLOPHON L140-152) |
| Bytes are live HTML? | No — a static `text/html` document with the full page text in `<pre>` blocks; no JS-only content |

## 2. Exact commands executed (verbatim)

Fetch (the assigned command; also supplied `%{url_effective}` so the post-redirect URL is measured, not inferred):

```sh
curl -fsSL -m 45 -A 'souji-r22-restructure/1.0' -o /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/attempt2/w1/evidence/snap-mv1.raw -w '%{http_code} %{size_download} %{url_effective}\n' 'https://man7.org/linux/man-pages/man1/mv.1.html'
```

Observed output:

```
200 11693 https://man7.org/linux/man-pages/man1/mv.1.html
```

Redirect/effective-URL confirmation (second, read-only HEAD-style GET writing to `/dev/null`):

```sh
curl -fsSL -m 45 -A 'souji-r22-restructure/1.0' -o /dev/null -w 'final_http=%{http_code} redirects=%{num_redirects} effective=%{url_effective}\n' 'https://man7.org/linux/man-pages/man1/mv.1.html'
```

Observed output:

```
final_http=200 redirects=0 effective=https://man7.org/linux/man-pages/man1/mv.1.html
```

Text strip (run with CWD `.../attempt2/w1/evidence`, `html.parser`, entities decoded, script/style/noscript and comments dropped, block tags turned into line breaks, intra-line whitespace collapsed to single spaces, blank-line runs collapsed, UTF-8 out):

```sh
python3 -c '
import sys, re, html.parser
class P(html.parser.HTMLParser):
    BLOCK = ("br","p","div","h1","h2","h3","tr","pre","hr","table")
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.buf = []
    def handle_starttag(self, t, a):
        if t in ("script","style","noscript"):
            self.skip += 1
        elif t in self.BLOCK:
            self.buf.append("\n")
    def handle_endtag(self, t):
        if t in ("script","style","noscript") and self.skip:
            self.skip -= 1
        elif t in self.BLOCK:
            self.buf.append("\n")
    def handle_data(self, d):
        if not self.skip:
            self.buf.append(d)
p = P()
p.feed(open(sys.argv[1], encoding="utf-8").read())
p.close()
lines = [re.sub(r"[ \t\r\f\v]+", " ", l).strip() for l in "".join(p.buf).splitlines()]
out = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"
open(sys.argv[2], "w", encoding="utf-8").write(out)
' snap-mv1.raw snap-mv1.txt
```

Exit `0`; output file `4610` bytes. Digests (same values reproduced by two independent runs):

```sh
sha256sum snap-mv1.raw snap-mv1.txt
# d20b49ad254a0c791f788920218f60da657a2f8ef765ba681a0f63fd2053ed0c  snap-mv1.raw
# 18dc9c2185fbf2b8839e780b2a9a88fdf392ffeff311785086c807a5aa4e6687  snap-mv1.txt
```

Quote-containment check (the predicate-4 shape: whitespace-collapsed verbatim match):

```sh
python3 -c '
import re
q="do not copy if renaming fails"
print("quote_words=", len(q.split()))
for f in ("snap-mv1.txt","snap-mv1.raw"):
    s=open(f,encoding="utf-8").read()
    c=re.sub(r"\s+"," ",s)
    print(f, "verbatim_collapsed=", q in c)
q2="--no-copy do not copy if renaming fails"
s=re.sub(r"\s+"," ",open("snap-mv1.txt",encoding="utf-8").read())
print("option_plus_gloss_words=", len(q2.split()), "collapsed=", q2 in s)
'
```

Observed output:

```
quote_words= 6
snap-mv1.txt verbatim_collapsed= True
snap-mv1.raw verbatim_collapsed= True
option_plus_gloss_words= 7 collapsed= True
```

## 3. Located passage

Locator: **DESCRIPTION** section, `--no-copy` option entry — raw `snap-mv1.raw` lines 105-106; text `snap-mv1.txt` lines 53-54.

Verbatim quote (6 words, <= 25):

> "do not copy if renaming fails"

Option token plus gloss as one contiguous span under whitespace collapse (7 words, also verbatim):

> "--no-copy do not copy if renaming fails"

Raw context as fetched:

```
105:       <b>--no-copy</b>
106:              do not copy if renaming fails
```

The entry sits between `-n, --no-clobber` / "If you specify more than one of -i, -f, -n, only the final one takes effect." and `--strip-trailing-slashes`, which is exactly the no-clobber-adjacent semantics the quarantine-staging theme relies on (`mv --no-clobber` refusing to overwrite a staged item; `--no-copy` refusing the cross-device copy fallback when a rename fails).

## 4. Bounded findings

1. **Locator correction (executed, material).** The item's requested locator `§ OPTIONS` does not exist on this page. The section index is `NAME | SYNOPSIS | DESCRIPTION | AUTHOR | REPORTING BUGS | COPYRIGHT | SEE ALSO | COLOPHON` (txt L9), `grep -nE '^OPTIONS' snap-mv1.txt` printed `NO_OPTIONS_HEADING`, and all mv options are rendered inside **DESCRIPTION** (txt L23). `DESCRIPTION` is one of the frozen locator-token classes in the preregistration ("§, section, line, paragraph, or DESCRIPTION"), so a Gate that cites `DESCRIPTION` plus the option name and the fetched line/byte coordinates satisfies predicate 3 truthfully. A Gate that writes `§ OPTIONS` would pass the mechanical token check while naming a section the document does not have — flagging it so no draft copies the dispatcher's label verbatim.
2. **Quote is verbatim in the committed snapshot (executed).** Confirmed under whitespace collapse in both `snap-mv1.txt` and `snap-mv1.raw` (`True`/`True` above); word count 6 <= 25.
3. **Snapshot is a real static document (executed).** `file` reports `HTML document, Unicode text, UTF-8 text`; page text lives in `<pre>` blocks; no JS-rendered body. `curl -fsSL` returned 200 with a stable 11693-byte body, and `snap-mv1.raw` re-hashes to the same digest across runs. Not a soft-404, not a redirect stub.
4. **Source provenance (source-inferred from page text, not independently verified against upstream tarballs).** COLOPHON states the page is part of coreutils 9.11, obtained from `coreutils-9.11.tar.xz` on 2026-08-03; footline `GNU coreutils 9.11 April 2026 MV(1)`. I did **not** fetch the tarball to cross-check; the quoted bytes are authoritative as the bytes of this URL on this date.
5. **My writes are exactly three paths (executed, with a post-write recheck).** I created/overwrote only `evidence/snap-mv1.raw`, `evidence/snap-mv1.txt`, and this report; no helper scripts, temp files, or copies. Note on the shared directory: `evidence/` is the wave's common evidence dir, and a recheck after sibling seats landed shows 44 files including `snap-gio1.*`, `snap-rename2.*`, `snap-statx2.*`, `snap-trashspec.*`, `slice114-*`, `MutDigest-*`, `.scratchpath` — none of them mine. Both of my digests re-hash unchanged after those landings (`d20b49ad…` raw, `18dc9c21…` text). If a later claim needs "the directory holds only these two files", it would be false as of that recheck; the true claim is the per-file one above.

## 5. Non-actions / bounds observed

- No git/jj writes, no commits, no lane-index, `.ufo/state`, `watchdog.log`, `MANIFEST.json`, templates, scripts, or sibling-repo writes. No write anywhere under `/home/vgpnk/Projects/shokuknow`.
- No `/proc`, credentials, private TSV, `.tower`, or operator-sweep census reads; no process signalling; no deletion or quarantine authority created.
- No subagent dispatch; no background jobs, campaigns, or campaign tools.
- Tooling: no installs or updates (curl, python3, coreutils already present); nothing to record beyond the versions exercised.

## 6. Handoff to C2 authoring

Use in the Gate as: URL `https://man7.org/linux/man-pages/man1/mv.1.html`, `opened: 2026-10-25`, locator `DESCRIPTION, --no-copy entry (snap-mv1.txt L53-54)`, quote `"do not copy if renaming fails"`, snapshot `census/...`-style pointer to the committed `snap-mv1.txt` with sha256 `18dc9c2185fbf2b8839e780b2a9a88fdf392ffeff311785086c807a5aa4e6687`.
