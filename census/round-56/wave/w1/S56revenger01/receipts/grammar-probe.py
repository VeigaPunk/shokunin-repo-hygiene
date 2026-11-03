#!/usr/bin/env python3
"""S56revenger01 grammar probes over the frozen v5 bytes (read-only copies in
scratch). Prints the observed behaviour for r55 routed shapes that have no
round-56 fixture. No writes outside stdout."""
import importlib.util
import re
import sys

S = '/fast/scratch/hyaku/souji-r56/S56revenger01'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


c1 = load('c1v5', S + '/c56/c1-counter.py')
c2 = load('c2v5', S + '/c56/c2-counter.py')

print('== hidden_lines: HTML comment opener / fence shapes ==')
cases = {
    'prose-midline-mention (F29 class)': "intro: the four-space-indented `<!--` line hides the tail\nR52-CORRECTION SCORECARD.md:10 stale=1 recomputed=2\nvisible after\n",
    'three-space comment opener': "   <!-- note\nR52-CORRECTION SCORECARD.md:10 stale=1 recomputed=2\n-->\n",
    'four-space comment opener (F26 class)': "    <!-- note\nR52-CORRECTION SCORECARD.md:10 stale=1 recomputed=2\n",
    'closer followed by VT (A09 class)': "~~~\nR52-CORRECTION SCORECARD.md:10 stale=1 recomputed=2\n~~~\x0b\nR52-CORRECTION SCORECARD.md:11 stale=1 recomputed=2\n",
    'list-item fence (E09 class)': "- ```text\nR52-CORRECTION SCORECARD.md:10 stale=1 recomputed=2\n```\n",
}
for k, v in cases.items():
    print('%-42s hidden=%s' % (k, sorted(c1.hidden_lines(v))))

print('== pair annotation grammar (N2/N3/D07/D08/D12) ==')
for line in ['999 -> 1000 rows', '999 => 1000 rows', '999 \u2014> 1000 rows',
             '999 to 1000 rows', 'SOURCES.md 999 -> 1000 rows',
             'corpus/SOURCES.md 999 -> 1000 rows',
             '1 -> 2 rows then 999 -> 1000 rows', '\uff17\uff18 -> 79 rows']:
    m = c1.PAIR_ANNOT_RE.search(line)
    print('%-42r match=%-14s corpus-literal=%s' % (line, m.groups() if m else None,
                                                   'corpus/SOURCES.md' in line))

print('== PTR exemption (ERRATUM-R55-2 wording) ==')
for s in ['2.5:1', 'v2.1:3', 'x.md:1', 'docs/a.py:12']:
    print('%-12s exempt=%s' % (s, bool(c1.PTR_RE.search(s))))

print('== correction lexing tolerance (B07 / S55-S3) ==')
for t in ['R52-CORRECTION SCORECARD.md:10 stale=1 recomputed=2',
          'R52-CORRECTION SCORECARD.md:10 stale=1 recomputed=2 --> note',
          '    R52-CORRECTION SCORECARD.md:10 stale=1 recomputed=2',
          '\tR52-CORRECTION SCORECARD.md:10 stale=1 recomputed=2',
          '  <!-- R52-CORRECTION SCORECARD.md:10 stale=1 recomputed=2 -->']:
    print('%-66r CORR_RE=%s' % (t, bool(c1.CORR_RE.fullmatch(t))))

print('== C2 receipt key grammar (RD-A repair scope; RD-B/P1 residuals) ==')
for ln in ['# _KEY=x', '# 1KEY=x', '# KEY=', '# BUILDHOST=', '# KEY-1=x',
           '# KEY.1=x', '# KEY=x y', '# ENTRIES: 999', '# BUILD-HOST=fixture',
           '# BUILD HOST=fixture', '#  KEY=x', '# key=x']:
    m = c2.RECEIPT_KV.fullmatch(ln)
    print('%-26r -> %s' % (ln, m.groups() if m else 'NO-MATCH (silently ignored)'))

print('== C2 capture header known-key grammar (RD-C) ==')
HDR = re.compile(r'# (TOOL_SHA256|FLEET_HEAD|ENTRIES)=(\S+)')
for ln in ['# ENTRIES=3', '#  ENTRIES=3', '# ENTRIES: 3', '# entries=3', '# ENTRIES = 3']:
    m = HDR.fullmatch(ln)
    print('%-22r -> %s' % (ln, m.groups() if m else 'NO-MATCH (ignored)'))

print('== selftest finding wildcard (RD-E) ==')
src = open(S + '/c56/c1-counter.py').read()
print('C1 format: want_find in (", "-") present=%s' % ("want_find in ('', '-')" in src))
src2 = open(S + '/c56/c2-counter.py').read()
print('C2 format: want_find in (", "-") present=%s' % ("want_find in ('', '-')" in src2))

sys.exit(0)
