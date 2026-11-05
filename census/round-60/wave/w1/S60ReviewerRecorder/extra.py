import sys, os, subprocess, pathlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import attacks2 as A
tool, work, gate = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3]
A.TOOL = pathlib.Path(tool)
# keep-only: commit on a temp branch, park a jj-keep ref on it, delete branch, HEAD stays on main
repo, rev, _ = A.fresh(work, 'k1')
A.git(repo, 'checkout', '-q', '-b', 'keeptmp')
(repo / 'tools' / 'instrument.py').write_text('# keep-only variant\n')
A.git(repo, 'add', 'tools/instrument.py'); A.git(repo, 'commit', '-q', '-m', 'keep')
keep = A.git(repo, 'rev-parse', 'HEAD').stdout.decode().strip()
A.git(repo, 'checkout', '-q', 'main'); A.git(repo, 'branch', '-D', 'keeptmp')
A.git(repo, 'update-ref', 'refs/jj/keep/fixture', keep)
out = work / 'k1-rcpt' / 'keep.txt'; out.parent.mkdir()
p = subprocess.run(A.tool_cmd(repo, keep, out, ['echo', 'x']), capture_output=True, timeout=60, cwd=str(repo))
A.say('ATK k1-keeponly-accepted', 'writer_rc=%d receipt=%s stderr=%r' % (p.returncode, out.exists(), p.stderr.decode()[:100]))
if out.exists():
    rec = repo / 'receipts' / 'keep.txt'; rec.parent.mkdir(exist_ok=True); rec.write_bytes(out.read_bytes())
    man = work / 'k1-manifest.tsv'; man.write_text('receipt\tinstrument\nreceipts/keep.txt\ttools/instrument.py\n')
    g = subprocess.run(['python3', gate, '--root', str(repo), '--manifest', str(man)], capture_output=True, timeout=120)
    A.say('ATK k1-r58-gate', 'gate_rc=%d out=%r' % (g.returncode, g.stdout.decode()[:160]))
# cross-filesystem OUT (/dev/shm tmpfs) with the lane on btrfs/xfs
repo, rev, _ = A.fresh(work, 'x1')
out = pathlib.Path('/dev/shm') / ('s60rr-x1-%d.txt' % os.getpid())
try:
    p = subprocess.run(A.tool_cmd(repo, rev, out, ['echo', 'x']), capture_output=True, timeout=60, cwd=str(repo))
    A.say('ATK x1-outside-lane-tmpfs', 'rc=%d receipt=%s head=%r' % (p.returncode, out.exists(), out.read_bytes()[:20] if out.exists() else b''))
finally:
    if out.exists(): out.unlink()
