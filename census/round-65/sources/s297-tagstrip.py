#!/usr/bin/env python3
"""s297-tagstrip.py — the exact, reproducible tag-strip recipe used to produce
s297-git-config.txt from the raw bytes of s297-git-config.html.

Recipe (deterministic; the order matters):
  1. read the raw file as bytes and decode UTF-8 (strict; the page decodes cleanly)
  2. parse the HTML with html.parser.HTMLParser(convert_charrefs=True):
       - <script> and <style> content is skipped entirely
       - a <pre> block is captured VERBATIM (its internal newlines are code)
       - a BLOCK-level open or close tag (p, div, li, ul, ol, dl, dt, dd, h1..h6,
         table, tr, td, th, br, hr, blockquote, section, article, header, footer,
         nav, aside, figure, figcaption, address, form) emits a block separator
       - every other tag emits nothing at all: the text inside the element is
         kept exactly as the source wrote it, so an inline element never injects
         a spurious space (no "normal ." artifacts)
  3. every block is then whitespace-normalised: all runs of whitespace -- including
     the page's own source line wraps -- collapse to a single space, then strip
  4. empty blocks are dropped and the survivors are joined with "\n"

Step 3 is what makes a source-wrapped sentence byte-contiguous in the text
capture: the page's own line wrapping is collapsed to single spaces inside each
block, so a sentence that the HTML wraps across lines becomes one line here.

Run:  python3 s297-tagstrip.py s297-git-config.html s297-git-config.txt
"""
import html
import re
import sys
from html.parser import HTMLParser

BLOCK = {'p', 'div', 'li', 'ul', 'ol', 'dl', 'dt', 'dd', 'h1', 'h2', 'h3', 'h4',
         'h5', 'h6', 'table', 'tr', 'td', 'th', 'br', 'hr', 'blockquote',
         'section', 'article', 'header', 'footer', 'nav', 'aside', 'figure',
         'figcaption', 'address', 'form'}
SKIP = {'script', 'style'}
SEP = '\x00'


class Stripper(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.skip_depth = 0
        self.in_pre = 0
        self.pre_buf: list[str] = []
        self.pre_text: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag == 'pre':
            self.in_pre += 1
            if self.in_pre == 1:
                self.pre_buf = []
            return
        if self.in_pre:
            return
        if tag in BLOCK:
            self.out.append(SEP)

    def handle_startendtag(self, tag, attrs):
        if self.skip_depth or self.in_pre:
            return
        if tag in BLOCK:
            self.out.append(SEP)

    def handle_endtag(self, tag):
        if tag in SKIP:
            if self.skip_depth:
                self.skip_depth -= 1
            return
        if self.skip_depth:
            return
        if tag == 'pre':
            if self.in_pre:
                self.in_pre -= 1
                if self.in_pre == 0:
                    self.pre_text.append(''.join(self.pre_buf))
                    self.out.append('\x00PRE%d\x00' % (len(self.pre_text) - 1))
            return
        if self.in_pre:
            return
        if tag in BLOCK:
            self.out.append(SEP)

    def handle_data(self, data):
        if self.skip_depth:
            return
        if self.in_pre:
            self.pre_buf.append(data)
            return
        self.out.append(data)


def tagstrip(raw: str) -> str:
    p = Stripper()
    p.feed(raw)
    p.close()
    s = ''.join(p.out)
    blocks = []
    for seg in s.split(SEP):
        m = re.fullmatch(r'PRE(\d+)', seg.strip())
        if m:
            blocks.append(p.pre_text[int(m.group(1))])
            continue
        seg = re.sub(r'\s+', ' ', seg).strip()
        if seg:
            blocks.append(seg)
    return '\n'.join(blocks) + '\n'


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: s297-tagstrip.py <in.html> <out.txt>", file=sys.stderr)
        return 2
    raw = open(sys.argv[1], 'rb').read().decode('utf-8')
    open(sys.argv[2], 'wb').write(tagstrip(raw).encode('utf-8'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
