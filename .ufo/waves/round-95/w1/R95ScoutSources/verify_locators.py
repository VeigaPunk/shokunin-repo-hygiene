#!/usr/bin/env python3
"""R95ScoutSources — locator check for S360-S364.

For each row: the HTML heading set of the committed capture (h1..h6), whether
the row's locator section token is a heading-like line in the tag-stripped text
(the lane's r23 locator rule), the page's documentation version, and the
positions of the quoted sentence relative to the section headings.

Read-only over the lane tree; writes nothing outside the seat dir.
"""
import json
import re
from html.parser import HTMLParser

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SEAT = LANE + "/.ufo/waves/round-95/w1/R95ScoutSources"

ROWS = [
    ("S360", "monitoring", "Events", "the `sys.monitoring.events.RAISE` entry",
     "An exception is raised, except those that cause a STOP_ITERATION event."),
    ("S361", "threading", "Functions", "the `threading.excepthook` entry",
     "Handle uncaught exception raised by Thread.run() ."),
    ("S362", "os", "Process Management", "the `os._exit` entry",
     "Exit the process with status n , without calling cleanup handlers, flushing stdio buffers, etc."),
    ("S363", "subprocess", "CompletedProcess.returncode", "and `Popen.returncode`",
     "A negative value -N indicates that the child was terminated by signal N (POSIX only)."),
    ("S364", "atexit", "atexit", "the module introduction before the `atexit.register` entry",
     "If an exception is raised during execution of an exit handler, a traceback is printed "
     "(unless SystemExit is raised) and the exception information is saved."),
]


class Heads(HTMLParser):
    """HTML headings of a capture (h1..h6), tag-stripped."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cur = None
        self.buf = []
        self.out = []

    def handle_starttag(self, tag, attrs):
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.cur = tag
            self.buf = []

    def handle_endtag(self, tag):
        if self.cur == tag:
            s = re.sub(r"\s+", " ", " ".join(self.buf)).strip()
            if s:
                self.out.append((tag, s))
            self.cur = None
            self.buf = []

    def handle_data(self, data):
        if self.cur:
            self.buf.append(data)


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
    out = []
    for rid, stem, locator, sub, quote in ROWS:
        raw = open(f"{LANE}/census/round-95/srcs/{stem}.html", encoding="utf-8", errors="replace").read()
        h = Heads()
        h.feed(raw)
        headings = [s for _, s in h.out]
        t = Text()
        t.feed(raw)
        flat = t.flat()
        # heading-like lines in the tag-stripped text: "X ¶"
        pilcrow = [seg.strip() for seg in flat.split("¶ ")[:-1]]
        locator_is_heading = any(locator == s or s.startswith(locator) for s in headings)
        locator_in_pilcrow_lines = any(locator in s for s in pilcrow)
        m = re.search(r"<title>([^<]*)</title>", raw)
        rec = {
            "id": rid,
            "capture": f"census/round-95/srcs/{stem}.html",
            "page_title": m.group(1) if m else None,
            "locator_section_token": locator,
            "locator_token_is_an_html_heading": locator_is_heading,
            "locator_token_appears_in_a_pilcrow_line": locator_in_pilcrow_lines,
            "html_headings": headings,
            "quote_occurrences": flat.count(quote),
            "quote_offset": flat.find(quote),
        }
        out.append(rec)
    with open(f"{SEAT}/verify-locators.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    for r in out:
        print(json.dumps({k: v for k, v in r.items() if k != "html_headings"},
                         ensure_ascii=False, indent=1))
        print("  headings:", r["html_headings"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
