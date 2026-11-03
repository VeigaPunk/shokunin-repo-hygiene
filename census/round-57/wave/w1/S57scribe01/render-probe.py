#!/usr/bin/env python3
"""S57scribe01 (souji r57): independent render probe for the four comment shapes.

The four correction blocks are transcribed from the frozen builder
census/round-57/fixtures/build-fixtures.py (B4 at its `elif` branch, C4, C6,
F29, plus base_corrections at line 306); only the placeholder line numbers are
substituted. Rendering uses markdown-it-py's `commonmark` preset, installed on
this host (not a lane tool). "Visible" = the text a browser would paint:
text/code tokens are collected, html_inline and html_block tokens are dropped
(a comment node renders nothing).
"""
import json
import sys

from markdown_it import MarkdownIt

S1, S2 = 7, 9


def corr(line, path):
    return 'R52-CORRECTION %s:%d stale=78 recomputed=79' % (path, line)


BASE = ['', corr(S1, 'SCORECARD.md'), corr(S2, 'census/round-51/preregistration.txt'), '']

BLOCKS = {
    'F29-PROSE-COMMENT-MENTION': [
        '', '- prose: a mention of the token <!-- inside a sentence opens no comment region.',
    ] + BASE,
    'B4-INLINE-NBSP-OPENER': [
        '', '\u00a0<!-- inline comment opened after an NBSP',
        corr(S1, 'SCORECARD.md'), corr(S2, 'census/round-51/preregistration.txt'),
        '-->', '',
    ],
    'C4-INLINE-CLOSED-COMMENT': [
        '', '- prose: an inline note <!-- opens here',
        corr(S1, 'SCORECARD.md'), corr(S2, 'census/round-51/preregistration.txt'),
        'and closes here -->', '',
    ],
    'C6-INLINE-SAME-LINE': [
        '', '- prose: a closed inline note <!-- same line --> stays inline.',
    ] + BASE,
    'CONTROL-NO-COMMENT': list(BASE),
}

VISIBLE = ('text', 'code_inline', 'fence', 'code_block')
HIDDEN = ('html_inline', 'html_block')


def walk(tokens, out, seen):
    for t in tokens:
        if t.type in HIDDEN:
            seen.append(t.type)
            continue
        if t.children:
            walk(t.children, out, seen)
        elif t.type in VISIBLE:
            out.append(t.content)


def main() -> int:
    md = MarkdownIt('commonmark')
    rows = []
    for name, lines in BLOCKS.items():
        src = '\n'.join(lines)
        out, seen = [], []
        walk(md.parse(src), out, seen)
        text = ' '.join(out)
        rows.append({
            'fixture': name,
            'visible_R52_CORRECTION': text.count('R52-CORRECTION'),
            'hidden_token_types': seen,
            'rendered_html': md.render(src),
        })
    for r in rows:
        print(json.dumps({k: v for k, v in r.items() if k != 'rendered_html'}, ensure_ascii=False))
    print()
    for r in rows:
        print('=== %s ===' % r['fixture'])
        print(r['rendered_html'].replace('\u00a0', '<NBSP>'))
    with open('/fast/scratch/hyaku/souji-r57/S57scribe01/render-probe.json', 'w', encoding='utf-8') as fh:
        json.dump(rows, fh, indent=1, ensure_ascii=False)
    return 0


if __name__ == '__main__':
    sys.exit(main())
