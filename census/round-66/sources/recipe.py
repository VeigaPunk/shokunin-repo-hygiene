#!/usr/bin/env python3
"""recipe.py -- deterministic HTML -> tag-stripped text for souji round-66 S66ScoutSources.

Recipe (recorded here so the L1 can re-derive the exact .txt bytes):

  1. Parse the raw capture with `html.parser.HTMLParser` (stdlib, Python 3).
  2. Skip the entire contents of <script> and <style> elements (their text is
     never emitted).
  3. Emit a newline for every start tag of a block-level element
     (p, div, h1..h6, li, dl, dt, dd, tr, td, th, pre, br, hr, table, ul, ol,
     section, article, header, footer, nav, aside, blockquote, dt, dd).
     <br> also emits a newline.
  4. Emit a single space for every other start tag / end tag (so that
     `foo<b>bar</b>` becomes `foo bar`), then collapse runs of whitespace.
  5. Unescape HTML entities (`&lt;` `&gt;` `&amp;` `&quot;` `&#39;` ...).
  6. Emit the text with LF line endings, one '\n' between logical lines, and
     exactly one trailing '\n' at end of file.
  7. Write the result as UTF-8 (no BOM).  The sha256 of the resulting .txt is
     the anchor recorded in quotes.tsv.

Usage:
  python3 recipe.py IN.html OUT.txt
"""

import hashlib
import html
import sys
from html.parser import HTMLParser

BLOCK = {
    "p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "dl", "dt", "dd",
    "tr", "td", "th", "pre", "br", "hr", "table", "thead", "tbody", "tfoot",
    "ul", "ol", "section", "article", "header", "footer", "nav", "aside",
    "blockquote", "figure", "figcaption", "main", "address", "caption",
}
SKIP = {"script", "style"}


class Strip(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag in BLOCK:
            self.parts.append("\n")
        else:
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag in SKIP:
            if self.skip_depth:
                self.skip_depth -= 1
            return
        if self.skip_depth:
            return
        self.parts.append("\n" if tag in BLOCK else " ")

    def handle_data(self, data):
        if self.skip_depth:
            return
        self.parts.append(data)

    def text(self):
        raw = "".join(self.parts)
        # convert_charrefs=True already decoded entities once; a second
        # html.unescape pass would double-decode (e.g. "&amp;lt;" -> "<").
        lines = []
        for line in raw.split("\n"):
            line = " ".join(line.split())
            if line:
                lines.append(line)
        return "\n".join(lines) + "\n"


def main(argv):
    if len(argv) != 3:
        sys.stderr.write("usage: recipe.py IN.html OUT.txt\n")
        return 2
    with open(argv[1], "rb") as fh:
        raw = fh.read().decode("utf-8", "replace")
    p = Strip()
    p.feed(raw)
    p.close()
    out = p.text().encode("utf-8")
    with open(argv[2], "wb") as fh:
        fh.write(out)
    sys.stderr.write(
        "recipe.py: %s -> %s bytes=%d sha256=%s\n"
        % (argv[1], argv[2], len(out), hashlib.sha256(out).hexdigest())
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
