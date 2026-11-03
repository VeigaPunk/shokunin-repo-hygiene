import importlib.util, sys, subprocess, shutil, hashlib, os
from pathlib import Path
sys.dont_write_bytecode = True
L = Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
S = Path('/fast/scratch/hyaku/souji-r55/S55critic01/probe')
S.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location('b55', L / 'census/round-55/fixtures/build-fixtures.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
ANCHOR = b.ANCHOR
REC = ('\n'.join(b.RECORD_BODY) + '\n').encode()
RSHA = hashlib.sha256(REC).hexdigest()
REG = b.REGISTRY_3ROWS


def sc(line5):
    return '\n'.join(['# probe SCORECARD', '', '| row | note |', '|---|---|', line5]) + '\n'


SC79 = sc('| C1 | command `%s` (79) recomputed below |' % ANCHOR)
PRE = '\n'.join(['# probe preregistration', 'sites:', '`%s` (79);' % ANCHOR]) + '\n'


def log(*lines):
    return '\n'.join(['# probe log'] + list(lines) + ['']) + ''


def mk(name, tip_over):
    d = b.init_repo(S, name)
    top = b.git(d, 'rev-parse', '--show-toplevel')
    assert Path(top) == d, (top, d)
    b.write(d / 'census/round-51/records/ws-drift-vs-r46.tsv', REC)
    b.write(d / 'SCORECARD.md', SC79)
    b.write(d / 'census/round-51/preregistration.txt', PRE)
    base = b.commit_all(d, 'base', b.T0)
    b.write(d / 'corpus/SOURCES.md', REG)
    for p, t in tip_over.items():
        b.write(d / p, t)
    tip = b.commit_all(d, 'tip', b.T1)
    return d, base, tip


def run_c1(d, base, tip):
    env = dict(os.environ, TMPDIR=str(S))
    cmd = ['python3', '-B', str(L / 'census/round-55/c1-counter.py'), '--root', str(d), '--rev', tip,
           '--base', base, '--record-sha256', RSHA, '--sources-rev-before', tip,
           '--sources-rev-after', tip, '--scratch', str(S / 'run')]
    p = subprocess.run(cmd, cwd=str(L), env=env, capture_output=True, text=True, timeout=300)
    return p.returncode, [x for x in (p.stdout + p.stderr).splitlines() if x.strip()]


C1 = [
    # (name, tip overrides, predicted exit per the code reading, note)
    ('c1-P0-control-unfiled', {'LOG.md': log('- the r52 note said corpus/SOURCES.md 274 -> 275 rows.')}, 1, 'control'),
    ('c1-P1-pointer-fake', {'LOG.md': log('- the r52 note said corpus/SOURCES.md 274 -> 275 rows (see x.md:1).')}, 0, 'x.md:1 fake'),
    ('c1-P1b-ratio-pointer', {'LOG.md': log('- the r52 note said corpus/SOURCES.md 274 -> 275 rows (ratio 2.5:1).')}, 0, 'numeric ratio'),
    ('c1-P1c-version-pointer', {'LOG.md': log('- the r52 note said corpus/SOURCES.md 274 -> 275 rows (v2.1:3).')}, 0, 'version token'),
    ('c1-P2-multi-pair-first-within', {'LOG.md': log('- corpus/SOURCES.md 1 -> 2 rows and corpus/SOURCES.md 274 -> 275 rows.')}, 0, 'second pair unscanned'),
    ('c1-P2b-multi-pair-first-over', {'LOG.md': log('- corpus/SOURCES.md 274 -> 275 rows and corpus/SOURCES.md 1 -> 2 rows.')}, 1, 'order control'),
    ('c1-P3-unfenced-pair-filing', {'LOG.md': log('- the r52 note said corpus/SOURCES.md 3 -> 4 rows.'),
                                    'SCORECARD.md': SC79 + '\nR53-CORRECTION LOG.md:2 stale=3->4 recomputed=3->3\n'}, 0, 'honest filing'),
    ('c1-P3-fenced-pair-filing', {'LOG.md': log('- the r52 note said corpus/SOURCES.md 3 -> 4 rows.'),
                                  'SCORECARD.md': SC79 + '\n```text\nR53-CORRECTION LOG.md:2 stale=3->4 recomputed=3->3\n```\n'}, 1, 'filing inside a fence (should not file)'),
    ('c1-P3b-comment-pair-filing', {'LOG.md': log('- the r52 note said corpus/SOURCES.md 3 -> 4 rows.'),
                                    'SCORECARD.md': SC79 + '\n<!-- R53-CORRECTION LOG.md:2 stale=3->4 recomputed=3->3 -->\n'}, 1, 'filing inside html comment'),
    ('c1-P4-prose-no-arrow', {'LOG.md': log('- corpus/SOURCES.md now holds 274 rows.')}, 1, 'prose claim, no arrow'),
    ('c1-P4b-fat-arrow', {'LOG.md': log('- corpus/SOURCES.md 274 => 275 rows.')}, 1, 'fat arrow'),
    ('c1-P4c-to-word', {'LOG.md': log('- corpus/SOURCES.md 274 to 275 rows.')}, 1, 'to-word'),
    ('c1-P5-beyond-zone-only', {'SCORECARD.md': sc('| C1 | command `%s`%s(79) |' % (ANCHOR, ' ' * 40))}, 2, 'beyond-zone sole annotation'),
    ('c1-P6-second-anchor-beyond-zone', {'SCORECARD.md': sc('| C1 | command `%s` (79) recomputed; dup `%s`%s(999) |' % (ANCHOR, ANCHOR, ' ' * 40))}, 0, 'second anchor lie beyond zone'),
    ('c1-P6b-second-anchor-in-zone', {'SCORECARD.md': sc('| C1 | command `%s` (79) dup `%s` (999) |' % (ANCHOR, ANCHOR))}, 1, 'control: in-zone alias'),
]

C2_BASE_RECEIPT_INSERT = {
    'c2-P0-control-honest': [],
    'c2-P0b-FB3-control-nospace': ['#BUILDHOST=fixture'],
    'c2-P1-two-unknown-first-named': ['# GENERATOR=x', '# HOST=y'],
    'c2-P2-hyphen-key': ['# BUILD-HOST=fixture'],
    'c2-P3-colon-key': ['# BUILDHOST: fixture'],
    'c2-P4-space-in-value': ['# BUILDHOST=fixture build'],
    'c2-P5-space-in-key': ['# BUILD HOST=fixture'],
    'c2-P6-empty-value': ['# GENERATOR='],
    'c2-P7-known-key-colon-conflict': ['# ENTRIES: 999'],
    'c2-P7b-known-key-spaced-conflict-control': ['#  ENTRIES = 999'],
}
C2_EXPECT = {
    'c2-P0-control-honest': 0, 'c2-P0b-FB3-control-nospace': 1, 'c2-P1-two-unknown-first-named': 1,
    'c2-P2-hyphen-key': 0, 'c2-P3-colon-key': 0, 'c2-P4-space-in-value': 0, 'c2-P5-space-in-key': 0,
    'c2-P6-empty-value': 0, 'c2-P7-known-key-colon-conflict': 0, 'c2-P7b-known-key-spaced-conflict-control': 1,
}


def c2_case(name, inserts, src, tool_sha):
    dst = S / name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    top = b.git(dst, 'rev-parse', '--show-toplevel')
    assert Path(top) == dst, (top, dst)
    rp = dst / 'census/round-53/records/fleet-root-census-run.txt'
    lines = rp.read_text().split('\n')
    lines[2:2] = inserts
    rp.write_text('\n'.join(lines))
    base = b.git(dst, 'rev-list', '--max-parents=0', 'HEAD')
    tip = b.commit_all(dst, 'probe', b.T1) if inserts else b.git(dst, 'rev-parse', 'HEAD')
    env = dict(os.environ, TMPDIR=str(S))
    cmd = ['python3', '-B', str(L / 'census/round-55/c2-counter.py'), '--root', str(dst), '--rev', tip,
           '--capture', 'census/round-52/records/fleet-root-census.tsv',
           '--receipt', 'census/round-53/records/fleet-root-census-run.txt', '--scratch', str(S / 'run')]
    p = subprocess.run(cmd, cwd=str(L), env=env, capture_output=True, text=True, timeout=300)
    return p.returncode, [x for x in (p.stdout + p.stderr).splitlines() if x.strip()]


def main():
    out = []
    out.append('### C1 probes (repo fixtures built by the frozen builder helpers; counter v4 frozen bytes)')
    for name, over, pred, note in C1:
        d, base, tip = mk(name, over)
        rc, lines = run_c1(d, base, tip)
        fnd = [x for x in lines if x.startswith('FINDING')]
        summ = [x for x in lines if x.startswith('SUMMARY') or x.startswith('CANNOT')]
        out.append('%-36s rc=%d predicted=%d [%s] %s | %s' % (name, rc, pred, note, ' ; '.join(fnd) or '-', (summ[-1] if summ else '-')[:140]))
    out.append('### C2 probes (single-commit FH-HONEST fixture + receipt edits in scratch clones)')
    info = b.build_one('FH-HONEST', S / 'c2src')
    for name, ins in C2_BASE_RECEIPT_INSERT.items():
        rc, lines = c2_case(name, ins, info['dir'], None)
        fnd = [x for x in lines if x.startswith('FINDING')]
        summ = [x for x in lines if x.startswith('SUMMARY') or x.startswith('CANNOT') or x.startswith('PRISTINE')]
        out.append('%-42s rc=%d predicted=%d | %s | %s' % (name, rc, C2_EXPECT[name], ' ; '.join(fnd) or '-', (summ[-1] if summ else '-')[:110]))
    text = '\n'.join(out)
    (S / 'probe-results.txt').write_text(text + '\n')
    print(text)


if __name__ == '__main__':
    main()
