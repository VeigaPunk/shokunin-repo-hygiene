#!/usr/bin/env python3
"""S57scribe01 (souji r57): independent quote-substring verifier.

Written from scratch for this seat; it does not import any lane tool. The
normalizer is deliberate and simple:

  1. drop <script>…</script> and <style>…</style> bodies;
  2. drop HTML comment spans (<!-- … -->) present in the markup;
  3. replace every tag with ONE space (so block boundaries do not glue words);
  4. decode HTML entities (html.unescape);
  5. collapse every whitespace run to one space and strip the ends.

Quotes are taken from census/round-57/records/source-quotes.txt (the committed
located quotes). Each is tested as a verbatim substring of the normalized page;
the word count is len(quote.split()) and is reported next to the count the
committed record claims.
"""
import hashlib
import html
import json
import re
import sys

SCRIPT_STYLE = re.compile(r'<(script|style)\b[^>]*>.*?</\1\s*>', re.I | re.S)
COMMENT_SPAN = re.compile(r'<!--.*?-->', re.S)
TAG = re.compile(r'<[^>]*>')
WS = re.compile(r'\s+')


def normalize(raw: str) -> str:
    s = SCRIPT_STYLE.sub(' ', raw)
    s = COMMENT_SPAN.sub(' ', s)
    s = TAG.sub(' ', s)
    s = html.unescape(s)
    s = WS.sub(' ', s)
    return s.strip()


def nearest_heading(norm: str, idx: int, probes):
    best = None
    for p in probes:
        j = norm.rfind(p, 0, idx)
        if j >= 0 and (best is None or j > best[0]):
            best = (j, p)
    return best


CASES = [
    {
        'id': 'S279',
        'file': 's279.html',
        'headings': ['13.1.6 Comments'],
        'quotes': [
            ('quote-1', 'Comments must have the following format: The string " <!-- ".', 11),
            ('quote-2', 'the text must not start with the string " > ", nor start with the string " -> "', 17),
        ],
    },
    {
        'id': 'S280',
        'file': 's280.html',
        'headings': ['6.6 Raw HTML'],
        'quotes': [
            ('quote-1', 'An HTML comment consists of <!--> , <!---> , or <!-- , a string of characters not including the string --> , and -->', 24),
        ],
    },
    {
        'id': 'S281',
        'file': 's281.html',
        'headings': ['Using HTML comments'],
        'quotes': [
            ('quote-1', 'This text cannot start with the string > or -> , cannot contain the strings --> or --!> , nor end with the string <!-', 25),
        ],
    },
]


def main(scratch: str) -> int:
    rows = []
    failures = 0
    for case in CASES:
        path = f'{scratch}/{case["file"]}'
        with open(path, 'rb') as fh:
            blob = fh.read()
        raw = blob.decode('utf-8', errors='replace')
        norm = normalize(raw)
        row = {
            'source': case['id'],
            'file': path,
            'bytes': len(blob),
            'sha256': hashlib.sha256(blob).hexdigest(),
            'normalized_chars': len(norm),
        }
        for label, quote, claimed_words in case['quotes']:
            idx = norm.find(quote)
            words = len(quote.split())
            entry = {
                'source': case['id'],
                'label': label,
                'verbatim_substring': idx >= 0,
                'offset': idx,
                'words': words,
                'committed_claimed_words': claimed_words,
                'words_match': words == claimed_words,
                'heading': None,
            }
            if idx >= 0:
                h = nearest_heading(norm, idx, case['headings'])
                entry['heading'] = {'offset': h[0], 'text': h[1]} if h else None
                entry['quote'] = quote
            else:
                # Diagnose: the longest prefix that does verify, and the text that
                # actually follows it in the page (shows the exact deviation).
                lo, hi = 0, len(quote)
                while lo < hi:
                    mid = (lo + hi + 1) // 2
                    if norm.find(quote[:mid]) >= 0:
                        lo = mid
                    else:
                        hi = mid - 1
                prefix = quote[:lo]
                at = norm.find(prefix)
                entry['longest_verified_prefix_chars'] = lo
                entry['longest_verified_prefix'] = prefix
                entry['page_continuation'] = norm[at + lo: at + lo + 80]
                failures += 1
            # Diagnostic only: does the quote verify if a space before terminal
            # punctuation is dropped? (Shows a one-space transcription drift.)
            punct = re.sub(r'\s+([.,;:!?])', r'\1', norm)
            entry['verifies_if_space_before_punct_dropped'] = punct.find(
                re.sub(r'\s+([.,;:!?])', r'\1', quote)) >= 0
            rows.append(entry)
            print(json.dumps(entry, ensure_ascii=False))
        print(json.dumps(row))
    print('FAILURES %d' % failures)
    with open(f'{scratch}/quote-verify.json', 'w', encoding='utf-8') as fh:
        json.dump(rows, fh, indent=1, ensure_ascii=False)
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
