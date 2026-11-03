import difflib
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

LANE = Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
SRC = LANE / 'census/round-57'
OUT = LANE / '.ufo/waves/round-57/w1/S57executor03'
S = Path('/fast/scratch/hyaku/souji-r57/S57executor03')
os.environ['TMPDIR'] = str(S)
source = (SRC / 'c1-counter.py').read_text()

def replace_once(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new, 1)

mutants = {}
mutants['M1'] = replace_once(source, '                    break  # unclosed: literal text, hides nothing (F29)', '                    end_line = n  # MUTANT: unclosed inline span hides EOF')
mutants['M2'] = replace_once(source, '                    if j > n:', '                    if j > i:  # MUTANT: same-line closer only')
start = source.index('        if indent <= 3:\n            pos = 0')
end = source.index('        i += 1\n    return res', start)
# v5 used ln.rstrip() as stripped. Its block predicate is already equivalent
# to v6's; the actual regression to v5-only opening removes inline recognition.
mutants['M3'] = source[:start] + source[end:]
mutants['M4'] = replace_once(source, '                for t in range(i, end_line + 1):', '                for t in range(i, end_line):  # MUTANT: exclude closer line')
mutants['M5'] = replace_once(source, "                if after.startswith('>') or after.startswith('->'):\n                    pos = k + 4  # <!--> or <!---> closes on its own line\n                    continue\n", '')
old = "                    finding('PAIR-FILING-HIDDEN',\n                            '%s:%d matching filing sits in a hidden line (fence or comment); it does not file'\n                            % (path, i))\n"
pair = replace_once(source, old, '')
mutants['PAIR-all'] = pair
mutants['PAIR-first'] = replace_once(pair, '(got_find == want_find)', '(got_find[:1] == want_find[:1])')
results = {}
try:
    for name, text in mutants.items():
        root = S / name
        root.mkdir(parents=True)
        shutil.copytree(SRC / 'fixtures', root / 'fixtures')
        shutil.copytree(SRC / 'records', root / 'records')
        (root / 'c1-counter.py').write_text(text)
        (OUT / (name + '.diff')).write_text(''.join(difflib.unified_diff(source.splitlines(True), text.splitlines(True), fromfile='frozen/c1-counter.py', tofile=name + '/c1-counter.py')))
        command = ['python3', '-B', str(root / 'c1-counter.py'), '--selftest', '--work', str(S / ('work-' + name)), '--expected', str(SRC / 'records/c1-selftest-expected.tsv'), '--builder-sha256', '2b8b657b8d86541d4a6f38345cd8d67f1a520603a7cda08f0a5bc3038924633b', '--expected-sha256', '538d902e2f65ddc26bc0c532f4f7de67f89c08020f69151563a982d923d8e105']
        p = subprocess.run(command, cwd=S, env=os.environ.copy(), capture_output=True, text=True, timeout=180)
        receipt = 'TMPDIR=' + str(S) + '\nCOMMAND=' + ' '.join(command) + '\n' + p.stdout + p.stderr + '\nEXIT=' + str(p.returncode) + '\n'
        (OUT / (name + '.txt')).write_text(receipt)
        results[name] = {'rc': p.returncode, 'failed_rows': [line for line in p.stdout.splitlines() if line.startswith('SELFTEST-CASE ') and ' fail ' in line], 'summary': [line for line in p.stdout.splitlines() if line.startswith('SELFTEST ')], 'F24': [line for line in p.stdout.splitlines() if line.startswith('SELFTEST-CASE F24-')], 'source_sha256': hashlib.sha256(text.encode()).hexdigest()}
        print(name, json.dumps(results[name]), flush=True)
    (OUT / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
finally:
    shutil.rmtree(S)
    print('SCRATCH_REMOVED=' + str(not S.exists()), flush=True)
