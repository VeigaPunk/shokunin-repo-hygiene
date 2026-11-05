import sys, os, subprocess, pathlib, resource
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import attacks2 as A
A.TOOL = pathlib.Path(sys.argv[1]); work = pathlib.Path(sys.argv[2])
repo, rev, _ = A.fresh(work, 'e3iso')
out = work / 'e3iso-out' / 'r.txt'; out.parent.mkdir()
p = subprocess.run(A.tool_cmd(repo, rev, out, ['bash', '-c', 'head -c 209715200 /dev/zero']), capture_output=True, timeout=300, cwd=str(repo))
peak_kib = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss  # only child of this fresh process
print('E3-ISOLATED tool=%s rc=%d out_exists=%s peak_child_maxrss_MiB=%.1f' % (sys.argv[1].split('/')[-1], p.returncode, out.exists(), peak_kib/1024))
