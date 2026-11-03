import sys, subprocess, os, shutil, hashlib
from pathlib import Path
sys.path.insert(0, '/fast/scratch/hyaku/souji-r55/S55critic01/probe')
import probe as P
from probe import b, L, S

# Kill-row naming probe: a capture whose column header is wrong, receipt rebound to the
# altered bytes so the FIRST printed FINDING is the header problem alone. The frozen
# run-matrix taker names a row by the second token of the first FINDING line.
info = b.build_one('FH-HONEST', S / 'c2src')
dst = S / 'c2-header-typo'
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(info['dir'], dst)
assert Path(b.git(dst, 'rev-parse', '--show-toplevel')) == dst
cap_p = dst / 'census/round-52/records/fleet-root-census.tsv'
cap = cap_p.read_bytes().decode()
cap2 = cap.replace('name\tkind\ttracked\tignored\tclass\tdisposition', 'name\tkind\ttracked\tignored\tclass\tdisposition2', 1)
assert cap2 != cap
cap_p.write_bytes(cap2.encode())
rp = dst / 'census/round-53/records/fleet-root-census-run.txt'
new_sha = hashlib.sha256(cap2.encode()).hexdigest()
rtxt = rp.read_text().split('\n')
rtxt = [('# CAPTURE_SHA256=%s' % new_sha) if l.startswith('# CAPTURE_SHA256=') else l for l in rtxt]
rp.write_text('\n'.join(rtxt))
tip = b.commit_all(dst, 'header typo', b.T1)
env = dict(os.environ, TMPDIR=str(S))
cmd = ['python3', '-B', str(L / 'census/round-55/c2-counter.py'), '--root', str(dst), '--rev', tip,
       '--capture', 'census/round-52/records/fleet-root-census.tsv',
       '--receipt', 'census/round-53/records/fleet-root-census-run.txt', '--scratch', str(S / 'run')]
p = subprocess.run(cmd, cwd=str(L), env=env, capture_output=True, text=True, timeout=300)
print('header-typo rc=%d' % p.returncode)
print('\n'.join(x for x in (p.stdout + p.stderr).splitlines() if x.strip()))
first = next((x for x in p.stdout.splitlines() if x.startswith('FINDING ')), '')
print('matrix-taker-token=%s' % (first.split(' ')[1] if first else '-'))
