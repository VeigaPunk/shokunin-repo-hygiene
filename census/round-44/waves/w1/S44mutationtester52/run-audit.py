import importlib.util
import os
from pathlib import Path
import subprocess
import sys

scratch = Path('/fast/scratch/hyaku/souji-r44/S44mutationtester52').resolve()
os.chdir(scratch)
original_run = subprocess.run

def guarded_run(args, *pos, **kw):
    if isinstance(args, list) and args[:1] == ['git'] and '-C' in args:
        root = Path(args[args.index('-C') + 1]).resolve()
        if not root.is_relative_to(scratch):
            raise RuntimeError('git outside owned scratch: ' + str(root))
        command = args[args.index('-C') + 2]
        if command in ('add', 'commit'):
            result = original_run(['git', '-C', str(root), 'rev-parse', '--show-toplevel'],
                                  capture_output=True, text=True, check=True)
            if result.stdout.strip() != str(root):
                raise RuntimeError('fixture toplevel mismatch')
    return original_run(args, *pos, **kw)

subprocess.run = guarded_run
spec = importlib.util.spec_from_file_location('frozen_audit', scratch / 'audit.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
sys.exit(audit.main(['--tool', str(scratch / 'tool.py'), '--work', str(scratch / sys.argv[1])]))
