import os, pathlib, shutil, subprocess, sys, runpy
L = '/home/vgpnk/Projects/shokunin/souji-shokunin'
F = 'f8c805dbfa7f45814cf9a7270fa8bbffb41a8373'
O = pathlib.Path(L) / '.ufo/waves/round-43/w1/R43reviewer05'
S = pathlib.Path('/fast/scratch/hyaku/souji-r43/R43reviewer05')
S.mkdir(parents=True, exist_ok=True)
os.environ['TMPDIR'] = str(S)
log = []
def show(path, rev=F):
    cmd = ['git', '-C', L, 'show', rev + ':' + path]
    data = subprocess.check_output(cmd)
    log.append('$ ' + ' '.join(cmd))
    return data
try:
    paths = ['tests/fixtures/r43-correction-prose.py', 'census/round-43/c1-counter.py', 'census/round-42/c1-counter.py', 'corpus/lessons/round-42.md', 'census/round-42/waves/w1/R42critic01.md', 'census/round-42/waves/w1/R42reviewer01.md', 'census/round-43/c1-required.tsv']
    for path in paths:
        dest = O / path.replace('/', '__')
        dest.write_bytes(show(path))
        log.append('saved=' + str(dest.relative_to(pathlib.Path(L))))
    fixture = O / 'tests__fixtures__r43-correction-prose.py'
    cmd = [sys.executable, '-B', str(fixture), '--work', str(S/'full'), '--lane-root', L, '--rev43', F, '--counter42', str(O/'census__round-42__c1-counter.py'), '--counter43', str(O/'census__round-43__c1-counter.py')]
    log.append('$ TMPDIR=' + str(S) + ' ' + ' '.join(cmd))
    p = subprocess.run(cmd, cwd=S, capture_output=True, text=True, timeout=2400)
    log.extend(['exit=' + str(p.returncode), p.stdout, p.stderr])
    # Record a structural discriminator, not an edited instrument or candidate.
    ns = runpy.run_path(str(fixture))
    row = next(r for r in ns['CASES'] if r[0] == 'crlf-register')
    log.append('crlf-register reg43=' + repr(row[3]) + ' reg42=' + repr(row[4]))
finally:
    shutil.rmtree(S)
    log.append('scratch_removed=' + str(not S.exists()))
    (O/'review-receipt.txt').write_text('\n'.join(log))
print('\n'.join(log))
