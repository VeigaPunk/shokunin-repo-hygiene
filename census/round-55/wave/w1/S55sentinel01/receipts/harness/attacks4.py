#!/usr/bin/env python3
"""S55sentinel01 probe set 4: C2 receipt empty-value escape + C1 LOG pair-scan
indent escape + NUL reproducibility. Frozen builder imported, never edited."""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

LANE = Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
BUILDER = LANE / 'census/round-55/fixtures/build-fixtures.py'
WORK = Path(sys.argv[1])
OUT = Path(sys.argv[2])

spec = importlib.util.spec_from_file_location('bf', BUILDER)
bf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bf)

ANCHOR = bf.ANCHOR
results = []


def run_c1(name, sc_val, pre_val, corrections, log_lines=None, registry=True):
    d = bf.init_repo(WORK, name)
    record = '\n'.join(bf.RECORD_BODY) + '\n'
    bf.write(d / 'census/round-51/records/ws-drift-vs-r46.tsv', record)
    bf.write(d / 'SCORECARD.md', '\n'.join([
        '# fixture SCORECARD', '', '| row | note |', '|---|---|',
        '| C1 | command `%s` (%d) recomputed below |' % (ANCHOR, sc_val)]) + '\n')
    bf.write(d / 'census/round-51/preregistration.txt', '\n'.join([
        '# fixture preregistration', 'sites:', '`%s` (%d);' % (ANCHOR, pre_val)]) + '\n')
    base = bf.commit_all(d, 'fixture base', bf.T0)
    bf.write(d / 'SCORECARD.md', '\n'.join([
        '# fixture SCORECARD', '', '| row | note |', '|---|---|',
        '| C1 | command `%s` (%d) recomputed below |' % (ANCHOR, sc_val), '']
        + corrections + ['']))
    if log_lines is not None:
        bf.write(d / 'LOG.md', '\n'.join(log_lines))
    if registry:
        bf.write(d / 'corpus/SOURCES.md', bf.REGISTRY_3ROWS)
    tip = bf.commit_all(d, 'fixture tip', bf.T1)
    for arm, script in (('v4-r55', 'census/round-55/c1-counter.py'),
                        ('v3-r54', 'census/round-54/c1-counter.py')):
        cmd = ['python3', '-B', script, '--root', str(d), '--rev', tip, '--base', base,
               '--record-sha256', bf.sha256(record.encode()), '--scratch', str(WORK)]
        env = dict(os.environ); env['TMPDIR'] = str(WORK)
        p = subprocess.run(cmd, cwd=str(LANE), capture_output=True, env=env, timeout=300)
        out = p.stdout.decode('utf-8', 'replace')
        f = [ln for ln in out.splitlines() if ln.startswith('FINDING ')]
        results.append({'probe': name, 'arm': arm, 'exit': p.returncode,
                        'first': f[0].split(' ')[1] if f else '-', 'n': len(f),
                        'findings': f, 'stdout': out, 'tip': tip, 'base': base})
        print('RESULT %-26s %-7s exit=%d first=%-26s n=%d' %
              (name, arm, p.returncode, results[-1]['first'], len(f)))
    return tip, base


def build_c2_receipt(name, receipt_extra):
    d = bf.init_repo(WORK, name)
    stub = bf.STUB_TOOL.encode()
    tool_sha = bf.sha256(stub)
    rows = [('a.txt', 'file', 'yes', 'no', 'tracked', 'none'),
            ('b.md', 'file', 'yes', 'no', 'tracked', 'none'),
            ('zz', 'dir', 'no', 'yes', 'ignored', 'none')]
    counts = {'tracked': 2, 'ignored': 1, 'untracked-stray': 0, 'symlink': 0}
    body = ['\t'.join(str(x) for x in r) for r in rows]
    cap = '\n'.join([
        '# fixture fleet-root census', '# SCOPE=top-level entries, dotfiles included, .git excluded',
        '# TOOL_SHA256=%s' % tool_sha, '# FLEET_HEAD=%s' % bf.FLEET_HEAD, '# ENTRIES=3',
        '# COUNT tracked=2', '# COUNT ignored=1', '# COUNT untracked-stray=0', '# COUNT symlink=0',
        'name\tkind\ttracked\tignored\tclass\tdisposition'] + body) + '\n'
    receipt_lines = ['# fixture run receipt', '# RECEIPT_VERSION=1', '# TOOL_SHA256=%s' % tool_sha,
                     '# FLEET_HEAD=%s' % bf.FLEET_HEAD,
                     '# CAPTURE_SHA256=%s' % bf.sha256(cap.encode()), '# ENTRIES=3']
    receipt_lines += receipt_extra
    receipt_lines += ['command: fixture census run (synthetic); no live root was read', '']
    receipt = '\n'.join(receipt_lines)
    bf.write(d / 'census/round-52/records/fleet-root-census.tsv', cap)
    bf.write(d / 'census/round-53/records/fleet-root-census-run.txt', receipt)
    bf.write(d / 'tools/souji-fleet-root-census.py', stub)
    tip = bf.commit_all(d, 'fixture base', bf.T0)
    for arm, script in (('v4-r55', 'census/round-55/c2-counter.py'),
                        ('v3-r54', 'census/round-54/c2-counter.py')):
        cmd = ['python3', '-B', script, '--root', str(d), '--rev', tip,
               '--capture', 'census/round-52/records/fleet-root-census.tsv',
               '--receipt', 'census/round-53/records/fleet-root-census-run.txt',
               '--scratch', str(WORK)]
        env = dict(os.environ); env['TMPDIR'] = str(WORK)
        p = subprocess.run(cmd, cwd=str(LANE), capture_output=True, env=env, timeout=300)
        out = p.stdout.decode('utf-8', 'replace')
        f = [ln for ln in out.splitlines() if ln.startswith('FINDING ')]
        results.append({'probe': name, 'arm': arm, 'exit': p.returncode,
                        'first': f[0].split(' ')[1] if f else '-', 'n': len(f),
                        'findings': f, 'stdout': out, 'tip': tip, 'base': tip})
        print('RESULT %-26s %-7s exit=%d first=%-26s n=%d' %
              (name, arm, p.returncode, results[-1]['first'], len(f)))


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    # --- C1: LOG pair scan, overstating pair hidden behind a 4-space-indented
    #     '<!--' region opener (CommonMark: 4 spaces = indented code block)
    run_c1('LOG-INDENT4-HIDE', 79, 79, [],
           log_lines=['# fixture log', '    <!--',
                      '- the r52 note said corpus/SOURCES.md 999 -> 1000 rows.', ''])
    run_c1('LOG-INDENT4-CONTROL', 79, 79, [],
           log_lines=['# fixture log',
                      '- the r52 note said corpus/SOURCES.md 999 -> 1000 rows.', ''])
    run_c1('LOG-NESTED-HIDE', 79, 79, [],
           log_lines=['# fixture log', '<!-- <!--',
                      '- the r52 note said corpus/SOURCES.md 999 -> 1000 rows.', ''])
    # --- C1: NUL byte reproducibility (same shape, two independent builds)
    for i in (1, 2):
        run_c1('NUL-REPRO-%d' % i, 79, 99,
               ['R52-CORRECTION SCORECARD.md:5 stale=79 recomputed=83\x00',
                'R52-CORRECTION census/round-51/preregistration.txt:3 stale=79 recomputed=83\x00'])
    # --- C2: unknown receipt key with an EMPTY value
    build_c2_receipt('C2-EMPTY-VALUE-KEY', ['# BUILDHOST='])
    build_c2_receipt('C2-EMPTY-VALUE-KEY-SPACE', ['# BUILDHOST = '])
    build_c2_receipt('C2-KNOWN-EMPTY-VALUE', ['# ENTRIES='])
    build_c2_receipt('C2-CONTROL-NONEMPTY', ['# BUILDHOST=fixture'])
    (OUT / 'probe4.json').write_text(json.dumps(results, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
