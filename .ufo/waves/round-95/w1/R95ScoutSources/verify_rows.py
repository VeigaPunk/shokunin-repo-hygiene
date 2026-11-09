#!/usr/bin/env python3
"""R95ScoutSources — S360-S364 row verification (exact method reproduction).

Method (reproduced from the committed .txt captures, byte-exact):
  - html.parser.HTMLParser(convert_charrefs=True)
  - skip <script> and <script>/<style> content
  - collect handle_data parts, join with a single space, collapse every
    whitespace run to one space, NO strip (the committed files keep the
    leading/trailing space that the join produces)
  - word count = len(quote.split())
  - occurrence count = number of verbatim substring hits in that text
  - locator = nearest preceding heading (h1..h4 / dt signature) in a
    block-separated variant of the same text
"""
import hashlib
import json
import re
import sys
import urllib.request
from html.parser import HTMLParser

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SEAT = LANE + "/.ufo/waves/round-95/w1/R95ScoutSources"

ROWS = [
    ("S360", "https://docs.python.org/3/library/sys.monitoring.html", "monitoring",
     74653, "cd85fa73159a682f403607b7e539fd005546a9ac90edc99e2ad51743dfc52b98",
     "An exception is raised, except those that cause a STOP_ITERATION event.", 11, 1),
    ("S361", "https://docs.python.org/3/library/threading.html#threading.excepthook", "threading",
     181498, "d6f8ca655ef4dff896685b8cf761c8d4b662233673bbd2d5defcb37709fb0361",
     "Handle uncaught exception raised by Thread.run() .", 7, 1),
    ("S362", "https://docs.python.org/3/library/os.html#os._exit", "os",
     791364, "078e69b12c66fd922353577d209e5a7c2f82a70b1b65eafe64a7910e635427fe",
     "Exit the process with status n , without calling cleanup handlers, flushing stdio buffers, etc.", 15, 1),
    ("S363", "https://docs.python.org/3/library/subprocess.html#subprocess.Popen.returncode", "subprocess",
     208648, "7f5772d756be5dd6b8b440ea12999afaf12119e7cfd9bb3db16287e49fcc3cad",
     "A negative value -N indicates that the child was terminated by signal N (POSIX only).", 15, 2),
    ("S364", "https://docs.python.org/3/library/atexit.html", "atexit",
     29643, "765f26c2d69949d6bf3b0e4198cabef3b23f83ad8188e5c1db3a502785c44bf8",
     "If an exception is raised during execution of an exit handler, a traceback is printed "
     "(unless SystemExit is raised) and the exception information is saved.", 25, 1),
]


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


class Blocks(HTMLParser):
    """Same text, but block-level tags become line breaks so headings are lines."""

    BLOCK = {"p", "div", "li", "dt", "dd", "h1", "h2", "h3", "h4", "h5", "tr", "br",
             "section", "pre", "blockquote", "ul", "ol", "dl", "table", "hr", "figcaption"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines = []
        self.cur = []
        self.skip = 0
        self.heading = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag in self.BLOCK:
            self._flush()
        if tag in ("h1", "h2", "h3", "h4", "h5"):
            self.heading.append(tag)

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1
        if tag in self.BLOCK:
            self._flush()
        if tag in ("h1", "h2", "h3", "h4", "h5") and self.heading:
            self.heading.pop()

    def handle_data(self, data):
        if self.skip:
            return
        self.cur.append(data)

    def _flush(self):
        s = re.sub(r"\s+", " ", " ".join(self.cur)).strip()
        if s:
            self.lines.append(s)
        self.cur = []

    def result(self):
        self._flush()
        return self.lines


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    out = []
    for rid, url, stem, nbytes, rsha, quote, rwords, rcount in ROWS:
        cap_path = f"{LANE}/census/round-95/srcs/{stem}.html"
        with open(cap_path, "rb") as fh:
            cap = fh.read()
        req = urllib.request.Request(url, headers={"User-Agent": "souji-r95-scout/1"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                live = r.read()
                live_status = r.status
        except Exception as exc:
            live = b""
            live_status = f"ERROR {exc!r}"
        with open(f"{LANE}/census/round-95/srcs/{stem}.txt", encoding="utf-8") as fh:
            committed_txt = fh.read()
        t = Text()
        t.feed(cap.decode("utf-8", "replace"))
        flat = t.flat()
        b = Blocks()
        b.feed(cap.decode("utf-8", "replace"))
        lines = b.result()
        # locate: find the line(s) holding the quote, and the nearest preceding heading
        locs = []
        for i, line in enumerate(lines):
            if quote in line:
                head = None
                for j in range(i - 1, -1, -1):
                    if re.match(r"^(Events|Functions|Process Management|CompletedProcess\.returncode|"
                                r"Popen\.returncode|atexit|Modules|Coroutines|Miscellaneous|Other)", lines[j]) \
                            or lines[j].endswith("¶") or re.match(r"^\w[\w.]*\.$", lines[j]):
                        head = lines[j]
                        break
                locs.append({"line_index": i, "line": line[:200], "nearest_preceding_heading": head})
        rec = {
            "id": rid,
            "url": url,
            "row_bytes": nbytes,
            "row_sha256": rsha,
            "live_status": live_status,
            "live_bytes": len(live),
            "live_sha256": sha(live) if live else None,
            "live_equals_committed_capture": live == cap,
            "capture_bytes": len(cap),
            "capture_sha256": sha(cap),
            "capture_matches_row_bytes": len(cap) == nbytes,
            "capture_matches_row_sha256": sha(cap) == rsha,
            "txt_method_reproduces_committed_exactly": flat == committed_txt,
            "quote": quote,
            "quote_words_counted": len(quote.split()),
            "row_words": rwords,
            "quote_words_match": len(quote.split()) == rwords,
            "quote_occurrences_counted": flat.count(quote),
            "row_occurrences": rcount,
            "quote_occurrences_match": flat.count(quote) == rcount,
            "quote_present": flat.count(quote) > 0,
            "quote_locations": locs,
        }
        out.append(rec)
    with open(f"{SEAT}/verify-rows.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    for r in out:
        print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
