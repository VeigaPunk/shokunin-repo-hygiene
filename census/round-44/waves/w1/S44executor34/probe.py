#!/usr/bin/env python3
import hashlib, json, os, pathlib, subprocess, sys

LANE = pathlib.Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
SCRATCH = pathlib.Path('/fast/scratch/hyaku/souji-r44/S44executor34')
BASE = '55d7af6f5a22340f7a3de1c386e514ababfaa75f'
FREEZE = 'd314fd6e85d62565344fa6c4b102f52f62297884'
TOOL_PATH = 'tools/souji-worktree-drift.py'

def blob(rev):
    return subprocess.check_output(['git', '-C', str(LANE), 'show', f'{rev}:{TOOL_PATH}'])

def run(rev, label):
    work = SCRATCH / label
    root = work / 'root'
    repo = root / 'repo'
    outside = work / 'outside'
    repo.mkdir(parents=True)
    outside.mkdir()
    subprocess.run(['git', '-C', str(repo), 'init', '-q'], check=True)
    record = work / 'record.tsv'
    record.write_text('REPO\trepo\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n')
    tool = work / 'tool.py'
    data = blob(rev)
    tool.write_bytes(data)
    link = work / 'result.json'
    victim = outside / 'victim.json'
    victim.write_bytes(b'KEEP-EXACTLY\n')
    link.symlink_to(victim)
    before = hashlib.sha256(victim.read_bytes()).hexdigest()
    refused = subprocess.run([sys.executable, '-B', str(tool), '--root', str(root), '--record', str(record), '--json', str(link)], cwd=work, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    after = hashlib.sha256(victim.read_bytes()).hexdigest()
    safe = work / 'success.json'
    success = subprocess.run([sys.executable, '-B', str(tool), '--root', str(root), '--record', str(record), '--json', str(safe)], cwd=work, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return {'rev': rev, 'tool_sha256': hashlib.sha256(data).hexdigest(), 'refusal_rc': refused.returncode, 'refusal_stdout': refused.stdout, 'refusal_stderr': refused.stderr, 'victim_before_sha256': before, 'victim_after_sha256': after, 'victim_unchanged': before == after, 'symlink_still_present': link.is_symlink(), 'success_rc': success.returncode, 'success_stdout': success.stdout, 'success_stderr': success.stderr, 'success_json_exists': safe.is_file(), 'success_json_bytes': safe.read_text() if safe.exists() else None}

results = {label: run(rev, label) for label, rev in [('base', BASE), ('freeze', FREEZE)]}
(LANE / '.ufo/waves/round-44/w1/S44executor34/receipts.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results, indent=2))
