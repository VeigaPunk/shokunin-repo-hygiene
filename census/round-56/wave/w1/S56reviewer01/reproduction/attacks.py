#!/usr/bin/env python3
"""S56reviewer01 attack harness for C1 (v5 correction-filing counter, cce21b55).

Imports the committed fixture builder (copied byte-exact into scratch/bin) for
the frozen 33-fixture control, builds attack fixtures with the same helpers,
runs the committed v4 and v5 counters on each fixture commit, and records a
CommonMark (markdown-it-py 4.2.0, commonmark preset) visibility reading of the
correction tokens. Writes one receipt per case into the seat receipts dir.
Scratch only; reads committed bytes via the counters; writes no lane file.
"""
import hashlib
import importlib.util
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from markdown_it import MarkdownIt

S = Path('/fast/scratch/hyaku/souji-r56/S56reviewer01')
SEAT = Path('/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-56/w1/S56reviewer01')
BIN = S / 'bin'
W = S / 'work'
RC = SEAT / 'receipts'
V4 = BIN / 'c1-v4.py'
V5 = BIN / 'c1-v5.py'
MD = MarkdownIt('commonmark')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


fx = load('fx', BIN / 'build-fixtures.py')
_commit_all = fx.commit_all
def guarded_commit(d, msg, date):
    assert d.resolve().is_relative_to(S.resolve())
    assert Path(fx.git(d, 'rev-parse', '--show-toplevel')).resolve() == d.resolve()
    return _commit_all(d, msg, date)
fx.commit_all = guarded_commit

R52_SC = 'R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79'
R52_PRE = 'R52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79'
R53_LOG = 'R53-CORRECTION LOG.md:2 stale=3->4 recomputed=3->3'
DEFAULT_TAIL = ['', R52_SC, R52_PRE, '']
LOG_OVER = '# fixture log\n- the r52 note said corpus/SOURCES.md 3 -> 4 rows.\n'
RECORD_TEXT = '\n'.join(fx.RECORD_BODY) + '\n'
RECORD_SHA = hashlib.sha256(RECORD_TEXT.encode()).hexdigest()


def mk(name, sc_base=None, sc_tail=None, log=None, log_in_base=False, readme=None):
    """Attack fixture on the frozen F1 layout: base commit, then a tip commit."""
    d = fx.init_repo(W, name)
    sc_base = fx.sc_base_lines(name) if sc_base is None else sc_base
    sc_tail = DEFAULT_TAIL if sc_tail is None else sc_tail
    fx.write(d / 'census/round-51/records/ws-drift-vs-r46.tsv', RECORD_TEXT)
    fx.write(d / 'SCORECARD.md', '\n'.join(sc_base) + '\n')
    fx.write(d / 'census/round-51/preregistration.txt', '\n'.join(fx.pre_base_lines(name)) + '\n')
    fx.write(d / 'corpus/SOURCES.md', fx.REGISTRY_3ROWS)
    if log_in_base and log is not None:
        fx.write(d / 'LOG.md', log)
    if readme is not None:
        fx.write(d / 'corpus/README.md', readme)
    base = fx.commit_all(d, 'attack base', fx.T0)
    fx.write(d / 'SCORECARD.md', '\n'.join(sc_base + sc_tail) + '\n')
    if log is not None and not log_in_base:
        fx.write(d / 'LOG.md', log)
    tip = fx.commit_all(d, 'attack tip', fx.T1)
    sc_text = (d / 'SCORECARD.md').read_bytes().decode('utf-8', 'replace')
    log_text = (d / 'LOG.md').read_bytes().decode('utf-8', 'replace') if (d / 'LOG.md').exists() else ''
    return {'name': name, 'dir': str(d), 'base': base, 'tip': tip,
            'record_sha256': RECORD_SHA, 'srev': (tip, tip), 'sc_text': sc_text, 'log_text': log_text}


def run_counter(script, info, scratch, base=None, srev=None):
    base = info['base'] if base is None else base
    srev = info['srev'] if srev is None else srev
    cmd = ['python3', '-B', str(script), '--root', info['dir'], '--rev', info['tip'], '--base', base,
           '--record-sha256', info['record_sha256'],
           '--sources-rev-before', srev[0], '--sources-rev-after', srev[1], '--scratch', str(scratch)]
    env = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'TMPDIR': str(scratch), 'LC_ALL': 'C'}
    p = subprocess.run(cmd, capture_output=True, env=env, timeout=300)
    text = (p.stdout + p.stderr).decode('utf-8', 'replace')
    findings = [ln.split(' ', 2)[1] for ln in text.splitlines() if ln.startswith('FINDING ')]
    summary = [ln for ln in text.splitlines() if ln.startswith('SUMMARY ')]
    return {'rc': p.returncode, 'text': text, 'first': findings[0] if findings else '-',
            'all': findings, 'summary': summary[0] if summary else '', 'cmd': cmd}


def cm_reading(text, tokens):
    """CommonMark (markdown-it-py commonmark preset) visibility of each token."""
    html = MD.render(text)
    stripped = re.sub(r'<!--.*?-->', '', html, flags=re.S)
    code_blocks = re.findall(r'<pre><code[^>]*>(.*?)</code></pre>', html, flags=re.S)
    res = {}
    for t in tokens:
        total = html.count(t)
        vis = stripped.count(t)
        in_code = sum(b.count(t) for b in code_blocks)
        res[t] = {'total_html': total, 'visible_para': vis - in_code, 'visible_code': in_code,
                  'hidden_in_comment': total - vis}
    return res


def cm_summary(reading):
    parts = []
    for t, r in reading.items():
        parts.append('%s para=%d code=%d hidden_comment=%d' % (t, r['visible_para'], r['visible_code'], r['hidden_in_comment']))
    return '; '.join(parts)


def tail(*lines):
    return list(lines)


# ---------------------------------------------------------------- cases
# kind: ctrl | named | harm | limit ; expected v4/v5 (rc, first finding) pinned
# for auto-check; a mismatch is printed, never silently accepted.
CASES = []


def case(cid, kind, note, expect4, expect5, cm_text=None, cm_tokens=None, **kw):
    CASES.append(dict(cid=cid, kind=kind, note=note, e4=expect4, e5=expect5,
                      cm_text=cm_text, cm_tokens=cm_tokens or [], kw=kw))


SCTOK = ['R52-CORRECTION', 'R53-CORRECTION']
LOGTOK = ['corpus/SOURCES.md']

case('CTRL-DEFAULT-HONEST', 'ctrl', 'frozen F1 layout, honest visible filings',
     (0, '-'), (0, '-'), 'sc', SCTOK)

# (a) one-line comment correction, then honest filing
case('A1-ONELINE2-HIDDEN-THEN-HONEST', 'named',
     'two-space `<!--` one-line comment carries a correction; honest filing on next line',
     (1, 'CORRECTION-IN-FENCE'), (1, 'CORRECTION-IN-FENCE'), 'sc', SCTOK,
     sc_tail=['', '  <!-- ' + R52_SC + ' -->', R52_SC, R52_PRE, ''])
case('A1b-ONELINE1-ONLY', 'named',
     'one-space `<!--` one-line comment is the only SCORECARD filing',
     (1, 'CORRECTION-IN-FENCE'), (1, 'CORRECTION-IN-FENCE'), 'sc', SCTOK,
     sc_tail=['', ' <!-- ' + R52_SC + ' -->', R52_PRE, ''])
case('A1c-ONELINE3-TRAILING-TEXT', 'named',
     'three-space one-line comment, text after the closer, sole SCORECARD filing',
     (1, 'CORRECTION-IN-FENCE'), (1, 'CORRECTION-IN-FENCE'), 'sc', SCTOK,
     sc_tail=['', '   <!-- ' + R52_SC + ' --> trailing', R52_PRE, ''])
case('A2-MULTILINE-COMMENT-HONEST', 'named',
     'multi-line comment opened at 2 spaces wraps honest SCORECARD filings',
     (1, 'CORRECTION-IN-FENCE'), (1, 'CORRECTION-IN-FENCE'), 'sc', SCTOK,
     sc_tail=['', '  <!-- open', R52_SC, R52_PRE, '  -->', ''])

# (b) tab-indented `<!--`
case('B1-TAB-OPENER-HIDES-PAIR-LOG', 'named',
     'tab-indented `<!--` in LOG.md hides an overstated pair line (v4 skips it)',
     (0, '-'), (1, 'UNFILED-SOURCES-ANNOTATION'), 'log', LOGTOK,
     log='# fixture log\n\t<!-- side note\n- the r52 note said corpus/SOURCES.md 999 -> 1000 rows.\n\t-->\n')
case('B2-TAB-OPENER-HIDES-CORRECTION', 'harm',
     'tab-indented `<!--` opens a region in v4 that hides honest SCORECARD filings',
     (1, 'CORRECTION-IN-FENCE'), (0, '-'), 'sc', SCTOK,
     sc_tail=['', '\t<!--', R52_SC, R52_PRE, '\t-->', ''])
case('B3-FOUR-SPACE-OPENER-HIDES-CORRECTION', 'harm',
     'four-space `<!--` (S2 class, deliberate repair) hides honest filings in v4',
     (1, 'CORRECTION-IN-FENCE'), (0, '-'), 'sc', SCTOK,
     sc_tail=['', '    <!--', R52_SC, R52_PRE, '    -->', ''])
case('B4-NBSP-PREFIX-OPENER-HIDES-CORRECTION', 'harm',
     'NBSP before `<!--` is not indentation: v5 sees no opener; CommonMark reads an inline comment',
     (1, 'CORRECTION-IN-FENCE'), (0, '-'), 'sc', SCTOK,
     sc_tail=['', '\u00a0<!--', R52_SC, R52_PRE, '-->', ''])
case('B5-BOM-LINE1-COMMENT-OPENER', 'harm',
     'UTF-8 BOM at byte 0 precedes a `<!--` opener on line 1 (comment spans the tail)',
     (1, 'CORRECTION-IN-FENCE'), (0, '-'), 'sc', SCTOK,
     sc_base=['\ufeff<!-- BOM opener at byte 0'] + fx.sc_base_lines('B5')[1:],
     sc_tail=['', R52_SC, R52_PRE, '-->', ''])

# (c) fences and comments nested
case('C1-FENCE-IN-COMMENT-PAIR-FILING', 'named',
     'pair filing inside a fence inside an HTML comment; overstated LOG.md pair',
     (0, '-'), (1, 'UNFILED-SOURCES-ANNOTATION'), 'sc', SCTOK,
     sc_tail=DEFAULT_TAIL + ['<!--', '```text', R53_LOG, '```', '-->', ''], log=LOG_OVER)
case('C2-COMMENT-IN-FENCE-PAIR-FILING', 'named',
     'HTML comment inside a fence; pair filing inside that comment; overstated LOG.md pair',
     (0, '-'), (1, 'UNFILED-SOURCES-ANNOTATION'), 'sc', SCTOK,
     sc_tail=DEFAULT_TAIL + ['```text', '<!--', R53_LOG, '-->', '```', ''], log=LOG_OVER)
case('C3-FENCE-OPENED-AFTER-COMMENT-UNCLOSED', 'named',
     'comment closes, then a fence opens and never closes; pair filing inside it',
     (0, '-'), (1, 'UNFILED-SOURCES-ANNOTATION'), 'sc', SCTOK,
     sc_tail=DEFAULT_TAIL + ['<!--', '```', '-->', '```text', R53_LOG, ''], log=LOG_OVER)
case('C4-INLINE-COMMENT-SPANS-CORRECTIONS', 'harm',
     'prose `<!--` mid-line (F29 family) opens a CommonMark inline comment that spans the honest SCORECARD filings',
     (1, 'CORRECTION-IN-FENCE'), (0, '-'), 'sc', SCTOK,
     sc_tail=['', 'Note: prose opens an inline comment <!-- here', R52_SC, R52_PRE,
              'and it closes here --> now.', ''])
case('C5-INLINE-COMMENT-HIDES-PAIR-LOG', 'named',
     'mid-line inline comment in LOG.md hides an overstated pair line (v4 skips it, v5 scans it)',
     (0, '-'), (1, 'UNFILED-SOURCES-ANNOTATION'), 'log', LOGTOK,
     log='# fixture log\nsee <!-- here\n- the r52 note said corpus/SOURCES.md 999 -> 1000 rows.\n--> closes\n')

# (d) fence closer followed by exotic separators (rstrip-based closer)
case('D1-VT-CLOSER-FENCE', 'limit',
     'closing run followed by vertical tab; CommonMark keeps the fence open, v4 and v5 close it',
     (0, '-'), (0, '-'), 'sc', SCTOK,
     sc_tail=['', '```text', 'sample', '```\x0b', R52_SC, R52_PRE, ''])
case('D2-FF-CLOSER-FENCE', 'limit',
     'closing run followed by form feed',
     (0, '-'), (0, '-'), 'sc', SCTOK,
     sc_tail=['', '```text', 'sample', '```\x0c', R52_SC, R52_PRE, ''])
case('D3-NEL-CLOSER-FENCE', 'limit',
     'closing run followed by NEL (U+0085)',
     (0, '-'), (0, '-'), 'sc', SCTOK,
     sc_tail=['', '```text', 'sample', '```\x85', R52_SC, R52_PRE, ''])
case('D4-LS-CLOSER-FENCE', 'limit',
     'closing run followed by U+2028',
     (0, '-'), (0, '-'), 'sc', SCTOK,
     sc_tail=['', '```text', 'sample', '```\u2028', R52_SC, R52_PRE, ''])
case('D5-TILDE-VT-CLOSER-FENCE', 'limit',
     'tilde fence closed by a run followed by vertical tab',
     (0, '-'), (0, '-'), 'sc', SCTOK,
     sc_tail=['', '~~~', 'sample', '~~~\x0b', R52_SC, R52_PRE, ''])
case('D6-TAB-CLOSER-FENCE-CONTROL', 'ctrl',
     'closing run followed by a tab (CommonMark-legal closer)',
     (0, '-'), (0, '-'), 'sc', SCTOK,
     sc_tail=['', '```text', 'sample', '```\t', R52_SC, R52_PRE, ''])

# (e) NUL in SCORECARD.md
case('E1-NUL-BOGUS-LINE-HONEST-DEFAULT', 'named',
     'NUL on a bogus correction-looking line; honest default filings present',
     (0, '-'), (1, 'CORRECTION-FILE-BINARY'), 'sc', SCTOK,
     sc_tail=DEFAULT_TAIL + ['R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=83\x00'])
case('E2-NUL-ON-HONEST-SC-FILING', 'named',
     'NUL on the honest SCORECARD filing line (the filing is unlexable)',
     (1, '-'), (1, 'CORRECTION-FILE-BINARY'), 'sc', SCTOK,
     sc_tail=['', R52_SC + '\x00', R52_PRE, ''])
case('E3-NUL-INSIDE-FENCE-LINE', 'named',
     'NUL on a line inside a fence (silent under v4)',
     (0, '-'), (1, 'CORRECTION-FILE-BINARY'), 'sc', SCTOK,
     sc_tail=DEFAULT_TAIL + ['```text', 'filler\x00', '```', ''])
case('E4-NUL-BEFORE-TOKEN-SAME-LINE', 'named',
     'NUL before a correction-looking token on a bogus line',
     (0, '-'), (1, 'CORRECTION-FILE-BINARY'), 'sc', SCTOK,
     sc_tail=DEFAULT_TAIL + ['\x00R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=83'])

# (f) NUL in pair sites on an unchanged file (LOG.md, corpus/README.md)
case('F1-NUL-IN-LOG-PAIR-UNCHANGED', 'limit',
     'NUL splits an overstated pair annotation in LOG.md (unchanged base->tip)',
     (0, '-'), (0, '-'), 'log', LOGTOK, log_in_base=True,
     log='# fixture log\n- the r52 note said corpus/SOURCES.md 3\x00 -> 4 rows.\n')
case('F2-NUL-IN-README-PAIR-UNCHANGED', 'limit',
     'NUL splits an overstated pair annotation in corpus/README.md (unchanged)',
     (0, '-'), (0, '-'), None, [], readme='# corpus readme\n- the r52 note said corpus/SOURCES.md 3\x00 -> 4 rows.\n')
case('F3-NUL-IN-PATH-TOKEN-UNCHANGED', 'limit',
     'NUL inside the path token of an overstated LOG.md pair (unchanged)',
     (0, '-'), (0, '-'), 'log', LOGTOK, log_in_base=True,
     log='# fixture log\n- the r52 note said corpus/SOURCES\x00.md 3 -> 4 rows.\n')
case('F4-CONTROL-LOG-PAIR-UNCHANGED-NO-NUL', 'named',
     'control: the same overstated pair, no NUL, LOG.md unchanged',
     (1, 'UNFILED-SOURCES-ANNOTATION'), (1, 'UNFILED-SOURCES-ANNOTATION'), 'log', LOGTOK, log_in_base=True,
     log=LOG_OVER)


def build_attack(c):
    kw = dict(c['kw'])
    return mk(c['cid'].replace('-', '_').lower()[:40], **kw)


def build_committed(name):
    return fx.build_one(name, W / 'committed')


def write_receipt(cid, body):
    RC.mkdir(parents=True, exist_ok=True)
    (RC / ('%s.txt' % cid)).write_text(body)


def arm_block(label, script, res, tip):
    return '\n'.join([
        '--- %s (%s) ---' % (label, script.name),
        'CMD: ' + ' '.join(res['cmd']),
        res['text'].rstrip('\n'),
        'EXIT=%d' % res['rc'],
    ])


def main():
    W.mkdir(parents=True, exist_ok=True)
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    table = []
    # ---- committed 33-fixture control (both arms, same commits as the frozen matrix)
    exp = {}
    for row in (BIN / 'c1-expected.tsv').read_text().splitlines()[1:]:
        if row.strip():
            f = row.split('\t')
            exp[f[0]] = (int(f[1]), f[2] if len(f) > 2 else '-')
    ctrl_rows = []
    if mode in ('all', 'control'):
        for name in fx.C1_FIXTURES:
            info = build_committed(name)
            base = info['tip'] if name not in ('F5-REWRITE', 'F6-RECORD-DRIFT', 'F27-BINARY-NUMSTAT') else info['base']
            srev = info.get('sources_revs') or (info['tip'], info['tip'])
            info2 = dict(info, record_sha256=info['record_sha256'], srev=srev)
            scratch = S / 'scratch-ctrl' / name
            scratch.mkdir(parents=True, exist_ok=True)
            r4 = run_counter(V4, info2, scratch, base=base, srev=srev)
            r5 = run_counter(V5, info2, scratch, base=base, srev=srev)
            ew = exp[name]
            ok5 = (r5['rc'] == ew[0]) and (ew[1] == '-' or r5['first'] == ew[1])
            ctrl_rows.append((name, r4['rc'], r4['first'], r5['rc'], r5['first'], ew[0], ew[1], 'pass' if ok5 else 'FAIL'))
    if ctrl_rows:
        lines = ['name\tv4_rc\tv4_first\tv5_rc\tv5_first\tfrozen_rc\tfrozen_finding\tv5_vs_frozen']
        lines += ['\t'.join(str(x) for x in r) for r in ctrl_rows]
        (RC / 'committed-control-matrix.tsv').write_text('\n'.join(lines) + '\n\nEXIT=0\n')
        for r in ctrl_rows:
            print('CONTROL', *r)
        # T4 check: v4 nonzero & v5 zero must be exactly F29
        narrowed = [r[0] for r in ctrl_rows if r[1] != 0 and r[3] == 0]
        print('CONTROL narrowed(v4!=0,v5=0)=', narrowed)
        print('CONTROL v4=0,v5!=0=', [r[0] for r in ctrl_rows if r[1] == 0 and r[3] != 0])

    # ---- attack fixtures
    if mode in ('all', 'attacks'):
        built = []
        for c in CASES:
            built.append((c, build_attack(c)))
        for c, info in built:
            scratch = S / 'scratch-att' / c['cid']
            scratch.mkdir(parents=True, exist_ok=True)
            r4 = run_counter(V4, info, scratch)
            r5 = run_counter(V5, info, scratch)
            text = info['sc_text'] if c['cm_text'] == 'sc' else info['log_text']
            cm = cm_reading(text, c['cm_tokens']) if c['cm_tokens'] else {}
            cm_s = cm_summary(cm) if cm else 'n/a'
            ok4 = (r4['rc'] == c['e4'][0]) and (c['e4'][1] == '-' or r4['first'] == c['e4'][1])
            ok5 = (r5['rc'] == c['e5'][0]) and (c['e5'][1] == '-' or r5['first'] == c['e5'][1])
            cls = classify(c['kind'], r4['rc'], r5['rc'])
            table.append((c['cid'], c['kind'], r4['rc'], r4['first'], r5['rc'], r5['first'], cls,
                          'exp-ok' if ok4 and ok5 else 'EXPECT-MISMATCH', c['note'], cm_s))
            body = [
                'CASE %s' % c['cid'],
                'KIND %s  CLASS %s' % (c['kind'], cls),
                'NOTE %s' % c['note'],
                'FIXTURE dir=%s base=%s tip=%s' % (info['dir'], info['base'], info['tip']),
                'SCORECARD.md tip bytes (repr):',
                repr(info['sc_text']),
                'LOG.md tip bytes (repr):',
                repr(info['log_text']),
                'CM (markdown-it-py %s commonmark): %s' % ('4.2.0', cm_s),
                arm_block('v4 committed round-55', V4, r4, info['tip']),
                arm_block('v5 committed round-56', V5, r5, info['tip']),
                'SUMMARY v4 %s' % r4['summary'],
                'SUMMARY v5 %s' % r5['summary'],
                'EXPECTATION-CHECK %s' % ('ok' if ok4 and ok5 else 'MISMATCH'),
                'EXIT=0',
            ]
            write_receipt(c['cid'], '\n'.join(body) + '\n')
            print('ATTACK %-36s %-6s v4=%d:%-24s v5=%d:%-24s %s %s' % (
                c['cid'], c['kind'], r4['rc'], r4['first'], r5['rc'], r5['first'], cls,
                'exp-ok' if ok4 and ok5 else 'EXPECT-MISMATCH'))
            print('   CM', cm_s)
        hdr = ['case', 'kind', 'v4_rc', 'v4_first', 'v5_rc', 'v5_first', 'class', 'expect', 'note', 'cm_reading']
        out = ['\t'.join(hdr)] + ['\t'.join(str(x) for x in row) for row in table]
        (RC / 'attack-table.tsv').write_text('\n'.join(out) + '\n\nEXIT=0\n')
    return 0


def classify(kind, rc4, rc5):
    if rc4 != 0 and rc5 == 0:
        return 'HARM'
    if rc4 == 0 and rc5 != 0:
        return 'NAMED(tightened)'
    if rc4 != 0 and rc5 != 0:
        return 'NAMED(both-refuse)'
    return 'PASS-BOTH' if kind != 'limit' else 'LIMIT'


if __name__ == '__main__':
    sys.exit(main())
