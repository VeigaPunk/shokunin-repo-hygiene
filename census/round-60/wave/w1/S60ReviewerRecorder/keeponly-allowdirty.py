import sys, os, subprocess, pathlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import attacks2 as A
A.TOOL = pathlib.Path(sys.argv[1]); work = pathlib.Path(sys.argv[2]); gate = sys.argv[3]
repo, rev, _ = A.fresh(work, 'kd1')
A.git(repo, 'checkout', '-q', '-b', 'keeptmp')
(repo / 'tools' / 'instrument.py').write_text('# keep-only variant\n')
A.git(repo, 'add', 'tools/instrument.py'); A.git(repo, 'commit', '-q', '-m', 'keep')
keep = A.git(repo, 'rev-parse', 'HEAD').stdout.decode().strip()
A.git(repo, 'checkout', '-q', 'main'); A.git(repo, 'branch', '-D', 'keeptmp')
A.git(repo, 'update-ref', 'refs/jj/keep/fixture', keep)
# worktree bytes := keep's committed instrument; dirty tree permitted explicitly
(repo / 'tools' / 'instrument.py').write_text('# keep-only variant\n')
out = work / 'kd1-rcpt' / 'keep.txt'; out.parent.mkdir()
p = subprocess.run(A.tool_cmd(repo, keep, out, ['echo', 'x'], extra=['--allow-dirty']), capture_output=True, timeout=60, cwd=str(repo))
A.say('ATK kd1-keeponly-allowdirty', 'writer_rc=%d receipt=%s stderr=%r' % (p.returncode, out.exists(), p.stderr.decode()[:100]))
if out.exists():
    rec = repo / 'receipts' / 'keep.txt'; rec.parent.mkdir(exist_ok=True); rec.write_bytes(out.read_bytes())
    man = work / 'kd1-manifest.tsv'; man.write_text('receipt\tinstrument\nreceipts/keep.txt\ttools/instrument.py\n')
    g = subprocess.run(['python3', gate, '--root', str(repo), '--manifest', str(man)], capture_output=True, timeout=120)
    A.say('ATK kd1-r58-gate', 'gate_rc=%d out=%r' % (g.returncode, g.stdout.decode()[:160]))
