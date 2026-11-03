import sys, subprocess, os, shutil
from pathlib import Path
sys.path.insert(0, '/fast/scratch/hyaku/souji-r55/S55critic01/probe')
import probe as P
from probe import b, L, S, ANCHOR, sc, log, REG, RSHA, REC

out = []

# P6 (valid base): second anchor lies beyond the zone in BOTH base and tip, so no DELETED-LINES artifact.
line6 = '| C1 | command `%s` (79) recomputed; dup `%s`%s(999) |' % (ANCHOR, ANCHOR, ' ' * 40)
d = b.init_repo(S, 'p6-second-anchor-beyond')
b.write(d / 'census/round-51/records/ws-drift-vs-r46.tsv', REC)
b.write(d / 'SCORECARD.md', sc(line6))
b.write(d / 'census/round-51/preregistration.txt', P.PRE)
base = b.commit_all(d, 'base', b.T0)
b.write(d / 'corpus/SOURCES.md', REG)
tip = b.commit_all(d, 'tip', b.T1)
rc, lines = P.run_c1(d, base, tip)
out.append('p6-second-anchor-beyond-zone (base=tip line) rc=%d | %s' % (rc, ' ; '.join(x for x in lines if x.startswith('FINDING')) or '-'))
out.append('   ' + [x for x in lines if x.startswith('SITE') or x.startswith('SUMMARY')][-1][:120])

# P7: pair annotation in a file outside LOG.md / corpus/README.md (AF4c, disclosed) -> expect 0
d, base, tip = P.mk('p7-notes-md', {'NOTES.md': log('- the r52 note said corpus/SOURCES.md 274 -> 275 rows.')})
rc, lines = P.run_c1(d, base, tip)
out.append('p7-notes-md-overstatement rc=%d | %s' % (rc, ' ; '.join(x for x in lines if x.startswith('FINDING')) or '-'))

# Mutant kill-power checks (mutants are scratch copies; frozen bytes untouched)
src = (L / 'census/round-55/c1-counter.py').read_text()
muts = {
    'M7-no-ptr-exemption': ("if 'corpus/SOURCES.md' not in ln or PTR_RE.search(ln):", "if 'corpus/SOURCES.md' not in ln:"),
    'M2-any-length-close': ("if body and set(body) == {ch} and len(body) >= n:", "if body and set(body) == {ch} and len(body) >= 1:"),
    'N5-no-sources-recompute': ("if (f[2], f[3]) != (want[0], want[1]):", "if False:"),
}
man = {}
for ln in Path('/fast/scratch/hyaku/souji-r55/S55critic01/selftest/fixture-manifest.tsv').read_text().splitlines()[1:]:
    f = ln.split('\t')
    man[f[0]] = f
for label, (old, new) in muts.items():
    assert src.count(old) == 1, label
    mdir = S / 'mut'
    mdir.mkdir(exist_ok=True)
    mpath = mdir / ('%s.py' % label)
    mpath.write_text(src.replace(old, new))
    fix = {'M7-no-ptr-exemption': 'F12c-LOG-POINTER-EXEMPT', 'M2-any-length-close': 'F8b-BT4-SHORT-RUN',
           'N5-no-sources-recompute': 'F23-SOURCES-RECOMP'}[label]
    f = man[fix]
    d, tip, base = f[2], f[4], f[3]
    srev = ['--sources-rev-before', tip, '--sources-rev-after', tip] if label.startswith('N5') else []
    env = dict(os.environ, TMPDIR=str(S))
    cmd = ['python3', '-B', str(mpath), '--root', d, '--rev', tip, '--base', base,
           '--record-sha256', f[5], '--scratch', str(S / 'run')] + srev
    p = subprocess.run(cmd, cwd=str(L), env=env, capture_output=True, text=True, timeout=300)
    orig = subprocess.run(['python3', '-B', str(L / 'census/round-55/c1-counter.py'), '--root', d, '--rev', tip,
                           '--base', base, '--record-sha256', f[5], '--scratch', str(S / 'run')] + srev,
                          cwd=str(L), env=env, capture_output=True, text=True, timeout=300)
    out.append('%-26s fixture=%-26s frozen rc=%d  mutant rc=%d  mutant-finding=%s' % (
        label, fix, orig.returncode, p.returncode,
        ' ; '.join(x.split(' ')[1] for x in (p.stdout).splitlines() if x.startswith('FINDING')) or '-'))

text = '\n'.join(out)
(S / 'probe2-results.txt').write_text(text + '\n')
print(text)
