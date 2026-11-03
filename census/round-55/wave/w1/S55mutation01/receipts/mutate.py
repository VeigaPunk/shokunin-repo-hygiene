#!/usr/bin/env python3
"""Scratch-only mutation harness for souji r55 seat S55mutation01.

Detector: the counter's own committed selftest (--selftest) asserting exit code
and finding id against the committed expected TSV. Mutants are scratch copies of
the committed counter bytes; the committed files are never written.
"""
import hashlib
import os
import pathlib
import shutil
import subprocess
import sys

LANE = pathlib.Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
S = pathlib.Path('/fast/scratch/hyaku/souji-r55/S55mutation01')
BUILDER = LANE / 'census/round-55/fixtures/build-fixtures.py'
C1 = LANE / 'census/round-55/c1-counter.py'
C2 = LANE / 'census/round-55/c2-counter.py'
EXP1 = LANE / 'census/round-55/records/c1-selftest-expected.tsv'
EXP2 = LANE / 'census/round-55/records/c2-selftest-expected.tsv'
PIN_BUILDER = 'e629a2e993b043bfc32904bc46612f5bdbc13909351cfe68f151b3f604fa8d62'
PIN_EXP1 = 'ca096117204a7262aaba908f1e913aee876e70b8167e6d596028f8f475e7b76e'
PIN_EXP2 = '63391afab07930193df686b9b9a4b9f3d6b9074e7bd3ed3479ede8f05a8bd2bc'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def parse_cases(text):
    cases = {}
    for ln in text.splitlines():
        if ln.startswith('SELFTEST-CASE '):
            f = ln.split(' ')
            # SELFTEST-CASE <name> <pass|fail> rc=N want_rc=M finding=F want_finding=G
            name = f[1]
            cases[name] = {
                'status': f[2],
                'rc': f[3].split('=', 1)[1],
                'want_rc': f[4].split('=', 1)[1],
                'finding': f[5].split('=', 1)[1],
                'want_finding': f[6].split('=', 1)[1],
            }
    return cases


MUTATIONS = [
    # ---- C1 ----
    dict(mid='C1-01-splitlines', counter='c1', fixture='F7-FF',
         what='hidden_lines() numbered with str.splitlines() again (restores the v3 S1 divergence)',
         old="    for i, raw in enumerate(text.split('\\n'), 1):",
         new="    for i, raw in enumerate(text.splitlines(), 1):"),
    dict(mid='C1-02a-indent-prefix', counter='c1', fixture='F20-R1-INDENT-SWALLOW',
         what='correction lexer loses the 0-3 leading-space tolerance (both regexes)',
         old="^ {0,3}(?:<!--\\s*)?", new="^(?:<!--\\s*)?", expect=2),
    dict(mid='C1-02b-comment-prefix', counter='c1', fixture='F21-R1-ONELINE-SWALLOW',
         what='correction lexer loses the one-line <!-- --> wrapper tolerance (both regexes)',
         old="(?:<!--\\s*)?", new="", expect=2),
    dict(mid='C1-03-alias-first-only', counter='c1', fixture='F13-DUAL-ANCHOR',
         what='anchor-alias loop reduced to the first anchor occurrence',
         old='        for k, (ok_tokens, straddle) in enumerate(zones):',
         new='        for k, (ok_tokens, straddle) in enumerate(zones[:1]):'),
    dict(mid='C1-04-pairinert-removed', counter='c1', fixture='F14-PAIR-STALE-FILING',
         what='PAIR-FILING-INERT loop removed',
         old="""            for f in (fil or []):
                if (f[0], f[1]) != (a, b):
                    pairinert += 1
                    finding('PAIR-FILING-INERT',
                            '%s:%d filing stale=%d->%d does not match the annotated pair %d->%d'
                            % (path, i, f[0], f[1], a, b))
""",
         new="""            pass
"""),
    dict(mid='C1-05-rows-required', counter='c1', fixture='F15-PAIR-NOROWS',
         what='pair annotation re-requires the unit word `rows`',
         old="(?:\\s+rows?\\b)?", new="\\s+rows?\\b"),
    dict(mid='C1-06-ascii-only-arrow', counter='c1', fixture='F16-PAIR-ARROW',
         what='pair annotation loses the typographic arrow separator',
         old="(?:->|\u2192)", new="(?:->)"),
    dict(mid='C1-07-fence-indent', counter='c1', fixture='F17-INDENT4-FENCE',
         what='fence-opener four-space indentation rule removed',
         old="""        if indent <= 3:
            m = re.match(r'(`{3,}|~{3,})(.*)$', stripped)""",
         new="""        if True:
            m = re.match(r'(`{3,}|~{3,})(.*)$', stripped)"""),
    dict(mid='C1-08-backtick-info', counter='c1', fixture='F18-BTINFO-FENCE',
         what='backtick-info-string rule removed (a backtick in the info string still opens a fence)',
         old="            if m and not (m.group(1)[0] == '`' and '`' in m.group(2)):",
         new="            if m:"),
    dict(mid='C1-09-pair-hidefence', counter='c1', fixture='F19-PAIR-IN-FENCE',
         what='PAIR_SITES hide-fence skip removed',
         old="""            if i in phidden:
                continue  # r54 reviewer R6 routed fix: fenced examples are not annotations
""",
         new=""),
    dict(mid='C1-10-ptr-widened', counter='c1', fixture='F22-PTR-TIMESTAMP',
         what='pointer exemption widened back to the v3 shape-only token (no dot extension required)',
         old="PTR_RE = re.compile(r'(?:[A-Za-z0-9_.\\-]+/)*[A-Za-z0-9_.\\-]+\\.[A-Za-z0-9]{1,5}:\\d')",
         new="PTR_RE = re.compile(r'[A-Za-z0-9_.\\-]+:\\d')"),
    dict(mid='C1-11-closing-length', counter='c1', fixture='F8b-BT4-SHORT-RUN',
         what='closing-fence minimum-length rule dropped',
         old="if body and set(body) == {ch} and len(body) >= n:",
         new="if body and set(body) == {ch}:"),
    dict(mid='C1-12-recompute-branch', counter='c1', fixture='F23-SOURCES-RECOMP',
         what='SOURCES-RECOMPUTE-MISMATCH branch dropped',
         old="""            for f in match:
                if (f[2], f[3]) != (want[0], want[1]):
                    log_recomp += 1
                    finding('SOURCES-RECOMPUTE-MISMATCH',
                            '%s:%d filing recomputed=%d->%d but the census grep recomputes %d->%d'
                            % (path, i, f[2], f[3], want[0], want[1]))
""",
         new="""            pass
"""),
    dict(mid='C1-13-exemption-removed', counter='c1', fixture='F12c-LOG-POINTER-EXEMPT',
         what='path.ext:line pointer exemption removed from the SOURCES pair scan',
         old="            if 'corpus/SOURCES.md' not in ln or PTR_RE.search(ln):",
         new="            if 'corpus/SOURCES.md' not in ln:"),
    # ---- C2 ----
    dict(mid='C2-14-tab-rule-narrow', counter='c2', fixture='FB1-TAB4-ROW',
         what='tab rule narrowed back to >= 5 tabs',
         old="            if '\\t' in ln:", new="            if ln.count('\\t') >= 5:"),
    dict(mid='C2-15a-key-case', counter='c2', fixture='FB2-LOWER-KEY',
         what='receipt key character class narrowed back to uppercase-only',
         old="([A-Za-z][A-Za-z0-9_]*)", new="([A-Z0-9_]+)"),
    dict(mid='C2-15b-key-upper', counter='c2', fixture='FB2-LOWER-KEY',
         what='key case normalisation removed (kv.group(1).upper() -> kv.group(1)) [probe]',
         old="            key = kv.group(1).upper()", new="            key = kv.group(1)"),
    dict(mid='C2-16-space-tolerance', counter='c2', fixture='FB3-NOSPACE-KEY',
         what='receipt key whitespace tolerance narrowed back to "# KEY="',
         old="RECEIPT_KV = re.compile(r'\\s*#\\s*([A-Za-z][A-Za-z0-9_]*)\\s*=\\s*(\\S+?)\\s*')",
         new="RECEIPT_KV = re.compile(r'# ([A-Za-z][A-Za-z0-9_]*)\\s*=\\s*(\\S+?)\\s*')"),
    dict(mid='C2-17-fa9-arm-removed', counter='c2', fixture='FA9-WRONG-TOOL-PIN',
         what='FA9-WRONG-TOOL-PIN selftest arm removed from the arm list',
         old="    names = list(mod.C2_FIXTURES) + ['FA9-WRONG-TOOL-PIN', 'FB4-PIN-SHAPE']",
         new="    names = list(mod.C2_FIXTURES) + ['FB4-PIN-SHAPE']"),
    dict(mid='C2-18-fb4-arm-removed', counter='c2', fixture='FB4-PIN-SHAPE',
         what='FB4-PIN-SHAPE selftest arm removed from the arm list',
         old="    names = list(mod.C2_FIXTURES) + ['FA9-WRONG-TOOL-PIN', 'FB4-PIN-SHAPE']",
         new="    names = list(mod.C2_FIXTURES) + ['FA9-WRONG-TOOL-PIN']"),
    dict(mid='C2-19-classmismatch-id', counter='c2', fixture='FA8-SYMLINK-CLASS',
         what='CLASS-MISMATCH problem text reverted to the unnamed r54 shape',
         old="problems_pre.append('CLASS-MISMATCH class %r want %r for %r'",
         new="problems_pre.append('class %r want %r for %r'"),
]


def build_mutant(counter_bytes, old, new, mid, expect=1):
    src = counter_bytes.decode('utf-8')
    n = src.count(old)
    if n != expect:
        raise SystemExit('%s: replacement anchor count %d (want %d)' % (mid, n, expect))
    out = src.replace(old, new)
    mdir = S / 'mut' / mid
    if mdir.exists():
        shutil.rmtree(mdir)
    (mdir / 'fixtures').mkdir(parents=True)
    mp = mdir / ('c1-counter.py' if 'C1' in mid else 'c2-counter.py')
    mp.write_text(out)
    shutil.copyfile(BUILDER, mdir / 'fixtures' / 'build-fixtures.py')
    return mp, src, out


def run_selftest(counter_path, work, expected, pin_expected):
    env = dict(os.environ)
    env['TMPDIR'] = str(S)
    cmd = [sys.executable, '-B', str(counter_path), '--selftest', '--work', str(work),
           '--expected', str(expected), '--builder-sha256', PIN_BUILDER,
           '--expected-sha256', pin_expected]
    p = subprocess.run(cmd, capture_output=True, env=env, cwd=str(LANE), timeout=900)
    return p.returncode, p.stdout.decode('utf-8', 'replace') + p.stderr.decode('utf-8', 'replace')


def main():
    c1b = C1.read_bytes()
    c2b = C2.read_bytes()
    print('PRISTINE c1 sha256=%s' % sha(c1b))
    print('PRISTINE c2 sha256=%s' % sha(c2b))
    (S / 'base').mkdir(parents=True, exist_ok=True)
    rc1, out1 = run_selftest(C1, S / 'base' / 'c1-work', EXP1, PIN_EXP1)
    (S / 'base' / 'c1-selftest.txt').write_text(out1)
    rc2, out2 = run_selftest(C2, S / 'base' / 'c2-work', EXP2, PIN_EXP2)
    (S / 'base' / 'c2-selftest.txt').write_text(out2)
    base1, base2 = parse_cases(out1), parse_cases(out2)
    print('BASELINE c1 rc=%d cases=%d pass=%d' % (rc1, len(base1), sum(1 for v in base1.values() if v['status'] == 'pass')))
    print('BASELINE c2 rc=%d cases=%d pass=%d' % (rc2, len(base2), sum(1 for v in base2.values() if v['status'] == 'pass')))
    results = []
    for m in MUTATIONS:
        src_bytes = c1b if m['counter'] == 'c1' else c2b
        mp, before, after = build_mutant(src_bytes, m['old'], m['new'], m['mid'], m.get('expect', 1))
        exp = EXP1 if m['counter'] == 'c1' else EXP2
        pin_exp = PIN_EXP1 if m['counter'] == 'c1' else PIN_EXP2
        work = S / 'mut-work' / m['mid']
        rc, out = run_selftest(mp, work, exp, pin_exp)
        (S / 'mut' / m['mid'] / 'selftest.txt').write_text(out)
        base = base1 if m['counter'] == 'c1' else base2
        cases = parse_cases(out)
        changed = []
        for name in base:
            b, a = base[name], cases.get(name)
            if a is None:
                changed.append((name, 'MISSING', b, None))
            elif (a['status'], a['rc'], a['finding']) != (b['status'], b['rc'], b['finding']):
                changed.append((name, a['status'], b, a))
        named = m['fixture']
        named_case = cases.get(named)
        named_changed = named in [c[0] for c in changed]
        killed = rc != 0 and named_changed
        results.append(dict(mid=m['mid'], counter=m['counter'], what=m['what'], named=named,
                            sha_before=sha(before.encode()), sha_after=sha(after.encode()),
                            selftest_rc=rc, named_status=(named_case or {}).get('status'),
                            named_rc=(named_case or {}).get('rc'),
                            named_finding=(named_case or {}).get('finding'),
                            named_changed=named_changed, killed=killed,
                            changed=[(c[0], c[2], c[3]) for c in changed]))
        print('%-26s selftest_rc=%d named=%s changed=%s killed=%s'
              % (m['mid'], rc, named, named_changed, killed))
        for c in changed:
            print('    DIFF %s: pristine rc=%s finding=%s -> mutant rc=%s finding=%s'
                  % (c[0], c[2]['rc'], c[2]['finding'], (c[3] or {}).get('rc'), (c[3] or {}).get('finding')))
    import json
    (S / 'results.json').write_text(json.dumps(results, indent=1))
    print('\nKILLED %d / %d' % (sum(1 for r in results if r['killed']), len(results)))
    print('SURVIVORS: %s' % [r['mid'] for r in results if not r['killed']])
    print('FINAL PRISTINE c1 sha256=%s (frozen 944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2)' % sha(C1.read_bytes()))
    print('FINAL PRISTINE c2 sha256=%s (frozen e4eb34e6375d16a8c7a8842ac43ef26f262167d85eb4615c1ab07e1c994a568c)' % sha(C2.read_bytes()))


if __name__ == '__main__':
    main()
