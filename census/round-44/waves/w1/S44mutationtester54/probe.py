import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile

SCRATCH = Path('/fast/scratch/hyaku/souji-r44/S44mutationtester54').resolve()
LANE = '/home/vgpnk/Projects/shokunin/souji-shokunin'
REV = 'd314fd6e85d62565344fa6c4b102f52f62297884'
HERE = Path(__file__).resolve().parent
ORIGINAL_RUN = subprocess.run
# Keep Python's fallback temporary storage inside this seat, never /tmp.
tempfile.tempdir = str(SCRATCH)

def guarded_run(argv, *args, **kwargs):
    argv = list(argv)
    if Path(str(argv[0])).name == 'git' and '-C' in argv:
        index = argv.index('-C')
        directory = Path(argv[index + 1]).resolve()
        command = argv[index + 2]
        if command in ('init', 'add', 'commit'):
            if not directory.is_relative_to(SCRATCH):
                raise RuntimeError('fixture escaped scratch: ' + str(directory))
            if command != 'init':
                actual = ORIGINAL_RUN(['git', '-C', str(directory), 'rev-parse', '--show-toplevel'], capture_output=True, text=True, check=True).stdout.strip()
                if actual != str(directory):
                    raise RuntimeError('fixture root mismatch: ' + actual)
    if Path(str(argv[0])).name.startswith('python'):
        pos = 1
        while pos < len(argv) and argv[pos].startswith('-'):
            pos += 1
        if pos < len(argv) and argv[pos].endswith('.py'):
            argv = argv[:pos] + [str(Path(__file__).resolve()), '--child'] + argv[pos:]
    return ORIGINAL_RUN(argv, *args, **kwargs)

subprocess.run = guarded_run
if sys.argv[1] == '--child':
    entry = sys.argv[2]
    sys.argv = sys.argv[2:]
    runpy.run_path(entry, run_name='__main__')
else:
    stage = sys.argv[1]
    candidate = SCRATCH / 'tool.py'
    module = runpy.run_path(str(HERE / 'counter.py'), run_name='probe_counter')
    main = module['main']
    namespace = main.__globals__
    original_blob = namespace['blob']
    def candidate_blob(root, rev, path):
        return candidate.read_bytes() if path == namespace['TOOL'] else original_blob(root, rev, path)
    namespace['blob'] = candidate_blob
    rc = main(['--root', LANE, '--rev', REV, '--scratch', str(SCRATCH / stage)])
    print('PROBE stage=%s exit=%d candidate_sha256=%s' % (stage, rc, hashlib.sha256(candidate.read_bytes()).hexdigest()))
    sys.exit(rc)
