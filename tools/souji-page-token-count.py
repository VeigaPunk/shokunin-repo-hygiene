#!/usr/bin/env python
"""souji-page-token-count.py — count a token's occurrences in a fetched web page
at two named scopes, raw bytes versus content area (souji r50).

Why: the r49 S267 re-open receipt stated "the page makes zero occurrences of
'factual' and zero of 'histor*'". That reading is exact for the page CONTENT
but not for the page's RAW BYTES, which carry one footer occurrence
("History and License", inside the site-chrome footer div). The r49
non-author verifier routed the fix: name the counting method, or paste the
command. This tool is that command: it counts a case-insensitive token PREFIX
at two scopes and records both numbers plus the exact method in one record,
so a content-scope zero and a raw-scope nonzero can never be conflated again.

Scopes (both computed from the same fetched bytes):
  raw      case-insensitive count of the token's bytes over the exact
           response bytes (lowercased); no decoding, no parsing.
  content  HTML text content: html.parser.HTMLParser with character
           references decoded (convert_charrefs, S273), collecting data()
           while script/style/header/nav/footer ELEMENTS are excluded and
           elements whose class list contains "footer" are excluded (site
           chrome); case-insensitive prefix count over the joined text.

Record grammar (header comment, then one line each):
  SOURCE-MODE=url|capture
  URL=... FINAL-URL=... HTTP-STATUS=...        (url mode)
  CAPTURE-PATH=...                             (capture mode)
  BYTES=<n> SHA256=<64hex> TOKEN=<str>
  SCOPE-RAW-MATCHES=<n> SCOPE-CONTENT-MATCHES=<n>
  METHOD=raw: case-insensitive byte-prefix count over the exact page bytes;
  content: HTML text content via html.parser (character references decoded;
  script/style/header/nav/footer elements and elements whose class list
  contains footer are excluded), case-insensitive prefix count
  PAGE-TOKEN-COUNT-EXIT=0

Usage:
  python -B tools/souji-page-token-count.py --url URL --token STR [--out PATH]
          [--timeout N]
  python -B tools/souji-page-token-count.py --capture FILE --token STR [--out PATH]
  python -B tools/souji-page-token-count.py --selftest
Exit: 0 record emitted; 2 could-not-evaluate (bad arguments, network or HTTP
failure, unreadable capture, selftest environment refusal). The selftest
exits 1 when a case fails. No scratch is needed for page counting: url mode
holds the page in memory; the selftest writes synthetic fixtures only under a
caller-provided TMPDIR and refuses when TMPDIR is unset, empty, or resolves
at or inside the lane root (Q66 scratch discipline). Stdlib only; the record
goes to stdout and, if given, --out.
"""
import argparse
import datetime
import hashlib
import os
import re
import sys
import urllib.request
from html.parser import HTMLParser

HEX64 = re.compile(r"^[0-9a-f]{64}$")

METHOD = ("raw: case-insensitive byte-prefix count over the exact page bytes; "
          "content: HTML text content via html.parser (character references "
          "decoded; script/style/header/nav/footer elements and elements whose "
          "class list contains footer are excluded), case-insensitive prefix count")

SKIP_TAGS = ("script", "style", "header", "nav", "footer")


class _TextExtractor(HTMLParser):
    """Collect text content while skipping site chrome and code elements.

    Exclusions are tracked as a stack of open regions: a region opens on a
    script/style/header/nav/footer start tag or on any element whose class
    list contains "footer", and closes when that same tag name closes, so
    content after the excluded region counts again.
    """

    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self._stack = []
        self._parts = []

    def _enters(self, tag, attrs):
        """True when this start tag opens an excluded region."""
        if tag in SKIP_TAGS:
            return True
        for name, value in attrs:
            if name == "class" and value and "footer" in value.split():
                return True
        return False

    def handle_starttag(self, tag, attrs):
        if self._enters(tag, attrs):
            self._stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        # a self-closing element opens and closes at once: never net-changes depth
        pass

    def handle_endtag(self, tag):
        if self._stack and self._stack[-1] == tag:
            self._stack.pop()

    def handle_data(self, data):
        if not self._stack:
            self._parts.append(data)

    def text(self):
        return "".join(self._parts)


def count_raw(page_bytes, token):
    return page_bytes.lower().count(token.lower().encode("utf-8"))


def count_content(page_bytes, token):
    extractor = _TextExtractor()
    extractor.feed(page_bytes.decode("utf-8", "replace"))
    return extractor.text().lower().count(token.lower())


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def record_lines(mode_fields, data, token):
    """The complete field lines of a record (everything after the header)."""
    lines = list(mode_fields)
    lines.append("BYTES=%d" % len(data))
    lines.append("SHA256=%s" % hashlib.sha256(data).hexdigest())
    lines.append("TOKEN=%s" % token)
    lines.append("SCOPE-RAW-MATCHES=%d" % count_raw(data, token))
    lines.append("SCOPE-CONTENT-MATCHES=%d" % count_content(data, token))
    lines.append("METHOD=%s" % METHOD)
    lines.append("PAGE-TOKEN-COUNT-EXIT=0")
    return lines


def emit_record(lines, out):
    text = "\n".join(lines) + "\n"
    sys.stdout.write(text)
    if out:
        with open(out, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)


def parse_record(text):
    record = {}
    for line in text.splitlines():
        if line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        record[key] = value
    return record


def fetch(url, timeout):
    request = urllib.request.Request(url, headers={"User-Agent": "souji-page-token-count/1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        status = getattr(response, "status", None)
        final = response.geturl()
        data = response.read()
    return status, final, data


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tmpdir_refusal():
    value = os.environ.get("TMPDIR", "")
    if not value.strip():
        return "TMPDIR is unset or empty; refusing to run (Q66 scratch discipline)"
    resolved = os.path.realpath(value)
    root = os.path.realpath(repo_root())
    if resolved == root or resolved.startswith(root + os.sep) or root.startswith(resolved + os.sep):
        return "TMPDIR resolves at or inside the lane root; refusing to run"
    return ""


def selftest():
    refusal = tmpdir_refusal()
    if refusal:
        sys.stderr.write("ERROR: %s\n" % refusal)
        return 2
    import tempfile
    import shutil

    fixtures = [
        ("body-text", u"<html><body><p>local history notes</p></body></html>", "histor", 1, 1),
        ("footer-class-only", u'<html><body><p>clean prose</p>'
                              u'<div class="footer">History and License</div></body></html>',
         "histor", 1, 0),
        ("script-only", u'<html><head><script>var h="history";</script></head>'
                        u'<body><p>clean prose</p></body></html>', "histor", 1, 0),
        ("absent", u"<html><body><p>nothing relevant here</p></body></html>", "histor", 0, 0),
        ("case-insensitive", u"<html><body><p>History</p></body></html>", "HISTOR", 1, 1),
        ("charref-decoded", u"<html><body><p>histo&#114;y of the lane</p></body></html>",
         "histor", 0, 1),
        ("footer-tag-only", u"<html><body><p>clean prose</p><footer>History</footer>"
                            u"</body></html>", "histor", 1, 0),
        ("content-resumes-after-footer", u'<html><body><div class="footer">History'
                                         u'</div><p>history resumes here</p></body></html>',
         "histor", 2, 1),
    ]
    scratch = tempfile.mkdtemp(prefix="souji-page-token-selftest.")
    passed = failed = 0
    try:
        for name, html, token, want_raw, want_content in fixtures:
            path = os.path.join(scratch, name + ".html")
            with open(path, "wb") as handle:
                handle.write(html.encode("utf-8"))
            with open(path, "rb") as handle:
                data = handle.read()
            lines = record_lines(["SOURCE-MODE=capture",
                                  "CAPTURE-PATH=%s" % path], data, token)
            record = parse_record("\n".join(lines))
            got_raw = int(record.get("SCOPE-RAW-MATCHES", "-1"))
            got_content = int(record.get("SCOPE-CONTENT-MATCHES", "-1"))
            ok = (got_raw == want_raw and got_content == want_content
                  and record.get("PAGE-TOKEN-COUNT-EXIT") == "0"
                  and HEX64.match(record.get("SHA256", "")) is not None)
            if ok:
                passed += 1
                print("SELFTEST-CASE pass %s raw=%d content=%d" % (name, got_raw, got_content))
            else:
                failed += 1
                print("SELFTEST-CASE fail %s raw=%d want=%d content=%d want=%d"
                      % (name, got_raw, want_raw, got_content, want_content))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    total = len(fixtures)
    if failed == 0:
        print("SELFTEST cases=%d pass=%d fail=0" % (total, passed))
        return 0
    print("SELFTEST cases=%d pass=%d fail=%d" % (total, passed, failed))
    return 1


def main(argv):
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--url")
    parser.add_argument("--capture")
    parser.add_argument("--token")
    parser.add_argument("--out")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()

    if bool(args.url) == bool(args.capture):
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: exactly one of --url / --capture is required\n")
        return 2
    if not args.token:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --token is required\n")
        return 2

    if args.capture:
        if not os.path.isfile(args.capture):
            sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: capture file missing: %s\n" % args.capture)
            return 2
        with open(args.capture, "rb") as handle:
            data = handle.read()
        fields = ["SOURCE-MODE=capture", "CAPTURE-PATH=%s" % os.path.abspath(args.capture)]
        emit_record(["# page-token-count v1 - %s" % utcnow()] + record_lines(fields, data, args.token),
                    args.out)
        return 0

    try:
        status, final, data = fetch(args.url, args.timeout)
    except Exception as error:  # network/DNS/timeout — could-not-evaluate
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: fetch failed: %s\n" % error)
        return 2
    if status != 200:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: HTTP status %s for %s\n" % (status, args.url))
        return 2
    fields = ["SOURCE-MODE=url", "URL=%s" % args.url,
              "FINAL-URL=%s" % final, "HTTP-STATUS=%s" % status]
    emit_record(["# page-token-count v1 - %s" % utcnow()] + record_lines(fields, data, args.token),
                args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
