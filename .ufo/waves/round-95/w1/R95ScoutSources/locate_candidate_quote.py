#!/usr/bin/env python3
"""R95ScoutSources — candidate source screen: locate the faulthandler quote.

Reads the live fetch in the scratch dir (already fetched 2026-11-09), strips
tags the same way the r95 captures were built (join handle_data parts with a
single space, collapse whitespace runs, no strip), and locates the candidate
sentence with its section heading and its word count.
"""
import hashlib
import re
import sys
from html.parser import HTMLParser

S = "/fast/scratch/hyaku/souji-r95/R95ScoutSources"
QUOTE = ("Call faulthandler.enable() to install fault handlers for the SIGSEGV , SIGFPE , "
         "SIGABRT , SIGBUS , and SIGILL signals.")


class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

    def flat(self):
        return re.sub(r"\s+", " ", " ".join(self.parts))


def main():
    raw = open(f"{S}/live-faulthandler.html", "rb").read()
    t = Text()
    t.feed(raw.decode("utf-8", "replace"))
    flat = t.flat()
    n = flat.count(QUOTE)
    print(f"bytes={len(raw)}")
    print(f"sha256={hashlib.sha256(raw).hexdigest()}")
    print(f"quote_words={len(QUOTE.split())}")
    print(f"quote_occurrences={n}")
    print(f"quote_present={n > 0}")
    i = flat.find(QUOTE)
    print(f"quote_offset={i}")
    if i >= 0:
        print("context_before=" + repr(flat[max(0, i - 260):i]))
        print("context_after=" + repr(flat[i + len(QUOTE):i + len(QUOTE) + 260]))
    # nearest preceding ¶-bearing heading
    heads = [m.start() for m in re.finditer(r"¶", flat)]
    prev = [h for h in heads if h < i]
    if prev:
        j = prev[-1]
        print("nearest_heading=" + repr(flat[max(0, j - 90):j + 2]))
    # does the page name the atexit/unraisable/monitoring channels?
    for kw in ("unraisable", "excepthook", "atexit", "monitoring", "audit"):
        print(f"page_mentions_{kw}={flat.lower().count(kw.lower())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
