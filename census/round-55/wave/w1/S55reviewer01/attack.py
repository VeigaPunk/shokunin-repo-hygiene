#!/usr/bin/env python3
"""S55reviewer01 attack driver over the frozen C1 v4 counter (sha256 944feafa...).

Fixture repos are built with the committed builder's helpers (init_repo,
write, commit_all, RECORD_BODY, REGISTRY_3ROWS, sc_base_lines, T0/T1) in
scratch. Each state: base commit = record + SCORECARD + preregistration +
a marker; tip commit adds LOG.md / corpus/SOURCES.md (when given) and a marker,
so DELETED-LINES cannot fire by construction (additions only). The frozen
counter is run from the lane root with TMPDIR in scratch.
"""
import sys, os, subprocess, hashlib, importlib.util
from pathlib import Path

sys.dont_write_bytecode = True
LANE = Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
SCR = Path('/fast/scratch/hyaku/souji-r55/S55reviewer01')
SEAT = LANE / '.ufo/waves/round-55/w1/S55reviewer01'
RCPT = SEAT / 'receipts'
WORK = SCR / 'attack-fixtures'
COUNTER_REL = 'census/round-55/c1-counter.py'
COUNTER = LANE / COUNTER_REL
BUILDER = LANE / 'census/round-55/fixtures/build-fixtures.py'
COUNTER_PIN = '944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2'
BUILDER_PIN = 'e629a2e993b043bfc32904bc46612f5bdbc13909351cfe68f151b3f604fa8d62'

def sha(b):
    return hashlib.sha256(b).hexdigest()

assert sha(COUNTER.read_bytes()) == COUNTER_PIN, 'counter pin mismatch'
assert sha(BUILDER.read_bytes()) == BUILDER_PIN, 'builder pin mismatch'

spec = importlib.util.spec_from_file_location('b55attack', BUILDER)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

A = mod.ANCHOR
REC = ('\n'.join(mod.RECORD_BODY) + '\n').encode()
RECSHA = mod.sha256(REC)
REG = mod.REGISTRY_3ROWS
LOGP = '# fixture log (attack)\n- the r52 note said corpus/SOURCES.md 3 -> 4 rows.\n'

ROW78 = '| C1 | command `%s` (78) recomputed below |' % A
ROW79 = '| C1 | command `%s` (79) recomputed below |' % A
PRE78 = '`%s` (78);' % A
PRE79 = '`%s` (79);' % A
CS1 = 'R52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79'
CS2 = 'R52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79'
HON = ['', CS1, CS2, '']


def sc_text(row=ROW78, extra=(), eol='\n'):
    lines = mod.sc_base_lines('attack')
    lines[4] = row
    return eol.join(lines + list(extra)) + eol


def pre_text(line3=PRE78, eol='\n'):
    return eol.join(['# fixture preregistration (attack)', 'sites:', line3]) + eol


STATES = []


def st(sid, grp, pred, note='', row=ROW78, extra=HON, pre=PRE78, log=None, reg=None, eol='\n'):
    STATES.append(dict(sid=sid, grp=grp, pred=pred, note=note, sc=sc_text(row, extra, eol),
                       pre=pre_text(pre, eol), log=log, reg=reg))


# ---- A: exotic separators / one-line model / fence closers -------------------
st('A01-SEP-VT-x2', 'A', 'IN-FENCE (F7-FF replica, \\x0b)', 'replica of acceptance F7-FF with vertical tab',
   extra=['', '\x0b', '\x0b', '~~~', CS1, CS2, '~~~', ''])
st('A02-SEP-FF-x2', 'A', 'IN-FENCE', 'form feed lines above fence',
   extra=['', '\x0c', '\x0c', '~~~', CS1, CS2, '~~~', ''])
st('A03-SEP-FS-GS-RS', 'A', 'IN-FENCE', 'U+001C/1D/1E above fence',
   extra=['', '\x1c', '\x1d', '\x1e', '~~~', CS1, CS2, '~~~', ''])
st('A04-SEP-NEL-x2', 'A', 'IN-FENCE', 'U+0085 above fence',
   extra=['', '\x85', '\x85', '~~~', CS1, CS2, '~~~', ''])
st('A05-SEP-LS-x2', 'A', 'IN-FENCE', 'U+2028 above fence',
   extra=['', '\u2028', '\u2028', '~~~', CS1, CS2, '~~~', ''])
st('A06-SEP-PS-x2', 'A', 'IN-FENCE', 'U+2029 above fence',
   extra=['', '\u2029', '\u2029', '~~~', CS1, CS2, '~~~', ''])
st('A07-CR-TRAILING-FENCE', 'A', 'IN-FENCE', 'opener and closer carry trailing CR',
   extra=['', '~~~\r', CS1, CS2, '~~~\r', ''])
st('A08-CRLF-HONEST', 'A', 'exit0 filed (control)', 'whole SCORECARD CRLF, honest filings',
   extra=HON, eol='\r\n')
st('A09-CLOSER-VT', 'A', 'exit0 (CM: fence still open, corrections are code)',
   'closer ~~~ followed by vertical tab; CommonMark: not a closer',
   extra=['', '~~~text', '~~~\x0b', CS1, CS2, ''])
st('A10-CLOSER-FF', 'A', 'exit0 (CM: still open)', 'closer ~~~ followed by form feed',
   extra=['', '~~~text', '~~~\x0c', CS1, CS2, ''])
st('A11-CLOSER-NEL', 'A', 'exit0 (CM: still open)', 'closer ~~~ followed by U+0085',
   extra=['', '~~~text', '~~~\x85', CS1, CS2, ''])
st('A12-CLOSER-LS', 'A', 'exit0 (CM: still open)', 'closer ~~~ followed by U+2028',
   extra=['', '~~~text', '~~~\u2028', CS1, CS2, ''])
st('A13-CLOSER-FS', 'A', 'exit0 (CM: still open)', 'closer ~~~ followed by U+001C',
   extra=['', '~~~text', '~~~\x1c', CS1, CS2, ''])
st('A14-CLOSER-TAB-CONTROL', 'A', 'exit0 consistent (control)', 'closer ~~~ followed by tab (CM-legal closer)',
   extra=['', '~~~text', '~~~\t', CS1, CS2, ''])

# ---- B: prefix lexing ---------------------------------------------------------
st('B01-3SP-WRAPPER-HONEST', 'B', 'IN-FENCE', '3 spaces + one-line comment wrapper, honest',
   extra=['', '   <!-- ' + CS1 + ' -->', '   <!-- ' + CS2 + ' -->', ''])
st('B02-3SP-BARE-CONTROL', 'B', 'exit0 (control)', '3 spaces bare, honest',
   extra=['', '   ' + CS1, '   ' + CS2, ''])
st('B03-3SP-WRAPPER-BOGUS', 'B', 'BOGUS-RECOMPUTED', '3 spaces + wrapper, bogus recomputed=83 on agreeing site',
   row=ROW79, pre=PRE79,
   extra=['', '   <!-- R52-CORRECTION SCORECARD.md:5 stale=79 recomputed=83 -->', ''])
st('B04-4SP-BARE', 'B', 'no FINDING, unfiled (must NOT lex)', '4 spaces bare honest',
   extra=['', '    ' + CS1, '    ' + CS2, ''])
st('B05-4SP-WRAPPER', 'B', 'no FINDING, unfiled (must NOT lex)', '4 spaces + wrapper',
   extra=['', '    <!-- ' + CS1 + ' -->', '    <!-- ' + CS2 + ' -->', ''])
st('B06-WRAPPER-TRAILING-TEXT', 'B', 'no FINDING, unfiled', 'one-line comment wrapper with text after -->',
   extra=['', '<!-- ' + CS1 + ' --> note', '<!-- ' + CS2 + ' --> note', ''])
st('B07-BARE-TRAILING-TEXT', 'B', 'no FINDING, unfiled', 'bare correction with --> note after it',
   extra=[CS1 + ' --> note', CS2 + ' --> note', ''])
st('B08-VT-AFTER-OPENER', 'B', 'IN-FENCE', '<!--\\x0b before correction (\\s matches VT)',
   extra=['', '<!--\x0b' + CS1 + ' -->', '<!--\x0b' + CS2 + ' -->', ''])
st('B09-NOSPACE-WRAPPER', 'B', 'IN-FENCE', '<!--CORRECTION-->',
   extra=['', '<!--' + CS1 + '-->', '<!--' + CS2 + '-->', ''])
st('B10-TAB-PREFIX', 'B', 'no FINDING, unfiled', 'tab-indented correction (not lexed)',
   extra=['', '\t' + CS1, '\t' + CS2, ''])
st('B11-NBSP-PREFIX', 'B', 'no FINDING, unfiled', 'NBSP-indented correction (not lexed)',
   extra=['', '\u00a0' + CS1, '\u00a0' + CS2, ''])
st('B12-MULTILINE-COMMENT-TRAILING', 'B', 'IN-FENCE', 'multi-line comment whose closing line carries text',
   extra=['', '<!--', CS1, CS2, '--> note', ''])

# ---- C: dual anchor / zone ----------------------------------------------------
st('C01-THREE-ANCHORS-OCC3-LIES', 'C', 'ANCHOR-ALIAS-MISMATCH', 'occ1 79, occ2 79, occ3 78',
   row='| C1 | `%s` (79) ok; `%s` (79) dup; `%s` (78) lie |' % (A, A, A), pre=PRE79, extra=[])
st('C02-OCC2-MULTI-TOKEN', 'C', 'MULTIPLE-ANNOTATIONS', 'second occurrence carries 79 and 80',
   row='| C1 | `%s` (79) x; `%s` (79) (80) |' % (A, A), pre=PRE79, extra=[])
st('C03-ALIAS-OCC2-AGREES-OCC3-LIES', 'C', 'ANCHOR-ALIAS-MISMATCH', 'occ1 78, occ2 78 agree, occ3 79 lies; honest filings',
   row='| C1 | `%s` (78) a; `%s` (78) b; `%s` (79) c |' % (A, A, A), extra=HON)
st('C04-BEYOND-ZONE-FIRST-TOKEN', 'C', 'INERT-CORRECTION (first occurrence zone empty)',
   'occ1 token beyond the 32-char zone; occ2 reads 78; honest filings',
   row='| C1 | `%s` ' % A + ' ' * 34 + '(999) ; `%s` (78) |' % A, extra=HON)
st('C05-OCC2-STRADDLE', 'C', 'ZONE-TOKEN-STRADDLES-EDGE', 'occ2 arrow token starts at offset 31 and straddles the zone',
   row='| C1 | `%s` (78) x; `%s` ' % (A, A) + ' ' * 29 + '→ 79 |', extra=HON)
st('C06-OCC2-PLAIN-CONTROL', 'C', 'exit0 (control)', 'occ2 carries no annotation; honest filings',
   row='| C1 | `%s` (78) dup `%s` |' % (A, A), extra=HON)
st('C07-OCC1-PLAIN-OCC2-78', 'C', 'INERT-CORRECTION', 'occ1 plain, occ2 reads 78 (INERT check uses zones[0] only)',
   row='| C1 | `%s` plain; `%s` (78) |' % (A, A), extra=HON)

# ---- D: pair grammar / SOURCES scan -------------------------------------------
st('D01-PAIR-INERT-BOTH-DIFFER', 'D', 'PAIR-FILING-INERT', 'filing stale 3->5 recomputed 3->6; annotation 3->4',
   extra=HON + ['', 'R53-CORRECTION LOG.md:2 stale=3->5 recomputed=3->6', ''], log=LOGP, reg=REG)
st('D02-PAIR-RECOMPUTE-DIFFERS', 'D', 'SOURCES-RECOMPUTE-MISMATCH', 'stale matches; recomputed 3->6 vs census 3->3',
   extra=HON + ['', 'R53-CORRECTION LOG.md:2 stale=3->4 recomputed=3->6', ''], log=LOGP, reg=REG)
st('D03-PAIR-HONEST-CONTROL', 'D', 'exit0 (control, F12b shape)', 'stale and recomputed match',
   extra=HON + ['', 'R53-CORRECTION LOG.md:2 stale=3->4 recomputed=3->3', ''], log=LOGP, reg=REG)
st('D04-PAIR-ROW-SINGULAR-NOFILING', 'D', 'UNFILED-SOURCES-ANNOTATION', 'unit word "row" singular, no filing',
   log='# fixture log (attack)\n- corpus/SOURCES.md 3 -> 4 row.\n', reg=REG)
st('D05-PAIR-ARROW-NOROWS-NOFILING', 'D', 'UNFILED-SOURCES-ANNOTATION', 'arrow separator, no unit word, no filing',
   log='# fixture log (attack)\n- corpus/SOURCES.md 3 → 4.\n', reg=REG)
st('D06-PAIR-ARROW-NOROWS-FILED-CONTROL', 'D', 'exit0 (control)', 'arrow no-rows annotation with honest pair filing',
   extra=HON + ['', 'R53-CORRECTION LOG.md:2 stale=3->4 recomputed=3->3', ''],
   log='# fixture log (attack)\n- corpus/SOURCES.md 3 → 4.\n', reg=REG)
st('D07-PAIR-FATARROW-SEP', 'D', 'exit0 (not matched: separator grammar is -> / → only)', '"=>" separator',
   log='# fixture log (attack)\n- corpus/SOURCES.md 999 => 1000 rows.\n', reg=REG)
st('D08-PAIR-EMDASH-ARROW-SEP', 'D', 'exit0 (not matched)', 'em-dash arrow "—>" separator',
   log='# fixture log (attack)\n- corpus/SOURCES.md 999 —> 1000 rows.\n', reg=REG)
st('D09-PTR-FAKE-A.MD:1', 'D', 'exit0 (named limit: pointer-shaped fake exempt)', 'overstatement + (see a.md:1)',
   log='# fixture log (attack)\n- corpus/SOURCES.md 999 -> 1000 rows (see a.md:1).\n', reg=REG)
st('D10-PTR-DOTSLASH-X.PY:2', 'D', 'exit0 (named limit: ./x.py:2 matches pointer shape)', 'overstatement + ./x.py:2',
   log='# fixture log (attack)\n- corpus/SOURCES.md 999 -> 1000 rows; see ./x.py:2.\n', reg=REG)
st('D11-PTR-X.MD:99999', 'D', 'exit0 (named limit: x.md:9 prefix matches)', 'overstatement + x.md:99999',
   log='# fixture log (attack)\n- corpus/SOURCES.md 999 -> 1000 rows; x.md:99999.\n', reg=REG)
st('D12-PATHLESS-SOURCES', 'D', 'exit0 (path literal; registry not named)', 'overstatement written SOURCES.md without corpus/',
   log='# fixture log (attack)\n- SOURCES.md 999 -> 1000 rows.\n', reg=REG)
st('D13-PAIR-IN-HTML-COMMENT', 'D', 'exit0 (comment invisible, CM-consistent)', 'overstatement inside <!-- -->',
   log='# fixture log (attack)\n<!-- corpus/SOURCES.md 999 -> 1000 rows -->\n', reg=REG)
st('D14-PAIR-FILING-IN-FENCE', 'D', 'exit0 (predicted BYPASS: pair filings are not hide-checked)',
   'pair filing inside ```text fence in SCORECARD; LOG overstates 3->4 with no visible filing',
   extra=HON + ['', '```text', 'R53-CORRECTION LOG.md:2 stale=3->4 recomputed=3->3', '```', ''], log=LOGP, reg=REG)
st('D15-PAIR-FILING-IN-COMMENT', 'D', 'exit0 (predicted BYPASS)', 'pair filing inside <!-- --> in SCORECARD',
   extra=HON + ['', '<!--', 'R53-CORRECTION LOG.md:2 stale=3->4 recomputed=3->3', '-->', ''], log=LOGP, reg=REG)
st('D16-PAIR-4SP-CODE-IN-LOG', 'D', 'UNFILED (over-refusal; CM: indented code)', '4-space indented overstatement in LOG.md',
   log='# fixture log (attack)\n    - corpus/SOURCES.md 3 -> 4 rows.\n', reg=REG)
st('D17-PAIR-FENCED-LOG-CONTROL', 'D', 'exit0 (control, F19 shape)', 'fenced LOG example',
   log='# fixture log (attack)\n```\n- corpus/SOURCES.md 999 -> 1000 rows\n```\n', reg=REG)
st('D18-PAIR-IN-SCORECARD-OUTSIDE-SITES', 'D', 'exit0 (named limit: pair scan covers LOG/README only)',
   'overstatement line placed in SCORECARD.md', extra=HON + ['', '- corpus/SOURCES.md 999 -> 1000 rows', ''], reg=REG)
st('D19-F22-TIMESTAMP-CONTROL', 'D', 'UNFILED-SOURCES-ANNOTATION (acceptance F22 shape)', 'clock time only',
   log='# fixture log (attack)\n- at 14:05 the r52 note said corpus/SOURCES.md 999 -> 1000 rows.\n', reg=REG)

# ---- E: fence starts / closers / containers -----------------------------------
st('E01-5SP-FENCE-VISIBLE-CONTROL', 'E', 'exit0 consistent (indented code; corrections at col 0)', '5-space fence after blank line',
   extra=['', '     ```text', '     x', '', CS1, CS2, ''])
st('E02-5SP-FENCE-CORR-INDENT5', 'E', 'no FINDING, unfiled (CM: code)', '5-space fence with corrections at 5 spaces',
   extra=['', '     ```text', '     ' + CS1, '     ' + CS2, '     ```', ''])
st('E03-TILDE-BACKTICK-INFO', 'E', 'IN-FENCE', '~~~ opener whose info carries backticks (legal for tilde)',
   extra=['', '~~~text `x`', CS1, CS2, '~~~', ''])
st('E04-CLOSER-LONGER', 'E', 'exit0 consistent', '```` closes ``` fence; corrections after',
   extra=['', '```text', 'x', '````', CS1, CS2, ''])
st('E05-CLOSER-3SP', 'E', 'exit0 consistent', 'closer indented 3 spaces',
   extra=['', '```text', 'x', '   ```', CS1, CS2, ''])
st('E06-CLOSER-4SP', 'E', 'IN-FENCE', 'closer indented 4 spaces does not close',
   extra=['', '```text', 'x', '    ```', CS1, CS2, '```', ''])
st('E07-CLOSER-WITH-INFO', 'E', 'IN-FENCE', 'closer with info text does not close',
   extra=['', '```text', 'x', '``` text', CS1, CS2, '```', ''])
st('E08-TILDE-4SP-CONTROL', 'E', 'exit0 consistent (indented code)', '4-space tilde opener after blank',
   extra=['', '    ~~~text', '', CS1, CS2, ''])
st('E09-LIST-BULLET-FENCE', 'E', 'exit0 (predicted BYPASS: CM fence inside list item)', '- ```text with corrections at 2 spaces',
   extra=['', '- ```text', '  ' + CS1, '  ' + CS2, '  ```', ''])
st('E10-LIST-ORDERED-TILDE', 'E', 'exit0 (predicted BYPASS: CM fence inside list item)', '1. ~~~ with corrections at 3 spaces',
   extra=['', '1. ~~~', '   ' + CS1, '   ' + CS2, '   ~~~', ''])
st('E11-BLOCKQUOTE-FENCE-COL0', 'E', 'exit0 consistent', '> ``` fence; corrections at col 0 end the blockquote',
   extra=['', '> ```text', CS1, CS2, '> ```', ''])
st('E12-PARA-INTERRUPT-3SP-FENCE', 'E', 'IN-FENCE', 'fence interrupts paragraph at 3 spaces',
   extra=['', 'some paragraph text', '   ```text', CS1, CS2, '   ```', ''])

# ---- F: digits, CR-only -------------------------------------------------------
st('F01-UNICODE-DIGITS-SITE', 'F', 'exit0 (routed low: \\d accepts fullwidth digits)',
   'site annotation (７８) fullwidth; ASCII honest filings',
   row='| C1 | command `%s` (７８) |' % A, extra=HON)
st('F02-CR-ONLY-FILE', 'F', 'no FINDING, unfiled (named limit: CR-only is one line)',
   'SCORECARD and honest filings joined by CR only', extra=HON, eol='\r')


def build(sid, sc, pre, log=None, reg=None):
    d = mod.init_repo(WORK, sid)
    top = subprocess.run(['git', '-C', str(d), 'rev-parse', '--show-toplevel'],
                         capture_output=True, text=True).stdout.strip()
    assert Path(top) == d, (top, d)
    mod.write(d / 'census/round-51/records/ws-drift-vs-r46.tsv', REC)
    mod.write(d / 'SCORECARD.md', sc)
    mod.write(d / 'census/round-51/preregistration.txt', pre)
    mod.write(d / 'base-marker.txt', 'base\n')
    base = mod.commit_all(d, 'attack base', mod.T0)
    if log is not None:
        mod.write(d / 'LOG.md', log)
    if reg is not None:
        mod.write(d / 'corpus/SOURCES.md', reg)
    mod.write(d / 'tip-marker.txt', 'tip\n')
    tip = mod.commit_all(d, 'attack tip', mod.T1)
    return {'dir': str(d), 'base': base, 'tip': tip}


def run_counter(info):
    argv = ['python3', '-B', COUNTER_REL, '--root', info['dir'], '--rev', info['tip'],
            '--base', info['base'], '--record-sha256', RECSHA,
            '--sources-rev-before', info['tip'], '--sources-rev-after', info['tip'],
            '--scratch', str(SCR)]
    env = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'TMPDIR': str(SCR), 'LC_ALL': 'C'}
    p = subprocess.run(argv, cwd=str(LANE), env=env, capture_output=True, text=True, timeout=300)
    cmd = 'cd %s && TMPDIR=%s %s' % (LANE, SCR, ' '.join(argv))
    return cmd, p.returncode, p.stdout, p.stderr


def tree_dump(info):
    out = []
    files = subprocess.run(['git', '-C', info['dir'], 'ls-tree', '-r', '--name-only', info['tip']],
                           capture_output=True, text=True).stdout.split('\n')
    for f in [x for x in files if x]:
        blob = subprocess.run(['git', '-C', info['dir'], 'show', '%s:%s' % (info['tip'], f)],
                              capture_output=True).stdout
        out.append('--- %s (%d bytes, sha256 %s)' % (f, len(blob), sha(blob)))
        for ln in blob.decode('utf-8', 'replace').split('\n'):
            out.append('    ' + repr(ln))
    return '\n'.join(out)


def main():
    RCPT.mkdir(parents=True, exist_ok=True)
    rows = []
    for s in STATES:
        info = build(s['sid'], s['sc'], s['pre'], s['log'], s['reg'])
        cmd, rc, out, err = run_counter(info)
        findings = [ln for ln in out.splitlines() if ln.startswith('FINDING ')]
        first = findings[0] if findings else '-'
        summ = next((ln for ln in out.splitlines() if ln.startswith('SUMMARY')), '-')
        tree = tree_dump(info)
        body = [
            '# S55reviewer01 C1 attack receipt — %s' % s['sid'],
            'group: %s' % s['grp'],
            'attack: %s' % s['note'],
            'predicted: %s' % s['pred'],
            'counter: %s sha256=%s' % (COUNTER_REL, COUNTER_PIN),
            'base: %s' % info['base'],
            'tip: %s' % info['tip'],
            'command: %s' % cmd,
            'exit: %d' % rc,
            'first_finding: %s' % first,
            '--- stdout (verbatim) ---',
            out.rstrip('\n'),
            '--- stderr ---',
            err.rstrip('\n'),
            '--- complete fixture tree at tip %s ---' % info['tip'],
            tree,
            '',
        ]
        (RCPT / ('%s.txt' % s['sid'])).write_text('\n'.join(body), encoding='utf-8')
        rows.append((s['grp'], s['sid'], s['pred'], str(rc), first, summ, s['note']))
    with open(SEAT / 'attack-table.tsv', 'w', encoding='utf-8') as fh:
        fh.write('group\tstate\tpredicted\texit\tfirst_finding\tsummary\tnote\n')
        for r in rows:
            fh.write('\t'.join(r) + '\n')
    for r in rows:
        print('%s\t%s\texit=%s\t%s' % (r[0], r[1], r[3], r[4]))
    print('states=%d' % len(rows))


if __name__ == '__main__':
    main()
