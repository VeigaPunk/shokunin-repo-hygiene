#!/usr/bin/env bash
# Synthetic-only r21 oracle. Never enumerate processes or inspect credentials.
set -euo pipefail
exec python3 -B - "$@" <<'PY'
import argparse
import hashlib
import os
from pathlib import Path
import re
import subprocess
import tempfile

p = argparse.ArgumentParser(description='Synthetic reason-field canaries, no live /proc')
p.add_argument('--tool', required=True)
p.add_argument('--base', required=True)
p.add_argument('--baseline-only', action='store_true')
p.add_argument('--baseline-as-tool', action='store_true',
               help='apply the same oracle to exact original reason emissions')
a = p.parse_args()
source = Path(a.base).read_text()
# Exact base function bodies, not rewritten lookalikes. Only the input root of
# read_process_argv is synthetic: <temporary>/cmdline replaces /proc/PID/cmdline.
names = ('path_under_prefix', 'top_level_scratch_gone', 'sanitize_field', 'read_process_argv')
functions = []
for name in names:
    m = re.search(r'^' + name + r'\(\) \{\n.*?^\}', source, re.M | re.S)
    if not m:
        raise SystemExit('missing original base function: ' + name)
    functions.append(m.group())
base_code = '\n'.join(functions) + '''
PREFIXES=("$3")
if [[ $1 == argv ]]; then
  read_process_argv "$2"
  [[ -n $PROC_GONE_PATH ]] || exit 3
  sanitize_field "$PROC_GONE_PATH"
  printf 'argv-path-gone:%s\\n' "$SAFE_FIELD"
else
  target=''
  IFS= read -r -d '' target || true
  target=${target%$'\\n'}
  top_level_scratch_gone "$target" "$3" || exit 3
  sanitize_field "$target"
  printf 'fd-path-gone:%s\\n' "$SAFE_FIELD"
fi
'''
# No directory at this prefix is created: all paths are harmless nonexistent
# fixture candidates. The temporary input file below is elsewhere.
prefix = '/var/tmp/souji-r21-canary-' + hashlib.sha256(os.urandom(24)).hexdigest()[:12]
assert not Path(prefix).exists()
cases = []
def case(name, mode, value, secret='', expected=None):
    data = b'\0'.join(x.encode() for x in value) + b'\0' if mode == 'argv' else value.encode() + b'\n'
    cases.append((name, mode, data, secret, expected))
for mode in ('argv', 'fd'):
    for label, value, secret in [
        ('github', 'ghp_SOUJIR21FAKE12345', 'SOUJIR21FAKE12345'),
        ('openai', 'sk-SOUJIR21FAKE23456', 'SOUJIR21FAKE23456'),
        ('aws', 'AKIA1234567890ABCDEF', 'AKIA1234567890ABCDEF'),
        ('slack', 'xoxb-SOUJIR21FAKE34567', 'SOUJIR21FAKE34567'),
        ('password', 'PaSsWoRd=SOUJIR21FAKE45678', 'SOUJIR21FAKE45678'),
        ('userinfo', 'https://u:SOUJIR21FAKE56789@host/x', 'SOUJIR21FAKE56789'),
        ('token-marker', '--ToKeN=SOUJIR21FAKE67890', 'SOUJIR21FAKE67890'),
        ('bearer', 'Authorization: Bearer SOUJIR21FAKE78901', 'SOUJIR21FAKE78901'),
    ]:
        path = prefix + '/missing/' + value
        case(mode + '-' + label, mode, ['worker', path] if mode == 'argv' else path, secret)
# Provenance cases: after extracting only the path, no regex marker remains.
for label, argv in [
    ('token-equals', ['worker', '--token=' + prefix + '/SOUJIR21FAKE80123']),
    ('token-next', ['worker', '--token', prefix + '/SOUJIR21FAKE80123']),
    ('password-equals', ['worker', '--password=' + prefix + '/SOUJIR21FAKE80123']),
]:
    case(label, 'argv', argv, 'SOUJIR21FAKE80123', b'argv-path-gone:[REDACTED]\n')
for mode in ('argv', 'fd'):
    path = prefix + '/ordinary/file'
    case(mode + '-plain', mode, ['worker', path] if mode == 'argv' else path,
         expected=(mode + '-path-gone:' + path + '\n').encode())
    path = prefix + '/tab\tline\nfile'
    case(mode + '-controls', mode, ['worker', path] if mode == 'argv' else path,
         expected=(mode + '-path-gone:' + path.replace('\t', ' ').replace('\n', ' ') + '\n').encode())
    path = prefix + '/' + 'z' * 400
    case(mode + '-bound', mode, ['worker', path] if mode == 'argv' else path,
         expected=(mode + '-path-gone:' + path).encode()[:160] + b'\n')
case('no-gone-argv', 'argv', ['worker', '--flag', 'ordinary'], expected=b'')
case('no-gone-fd', 'fd', '/outside-the-declared-prefix/file', expected=b'')
failed = base_leaks = leaks = max_len = 0
with tempfile.TemporaryDirectory(prefix='souji-r21-canary-input-', dir='/var/tmp') as temp:
    root = Path(temp)
    for name, mode, data, secret, expected in cases:
        (root / 'cmdline').write_bytes(data)
        old = subprocess.run(['bash', '-c', base_code, 'baseline', mode, temp, prefix], input=data,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={'PATH':'/usr/bin:/bin','LC_ALL':'C'})
        old_leaks = bool(secret and secret.encode() in old.stdout)
        base_leaks += old_leaks
        if a.baseline_only:
            ok = old.returncode == (3 if expected == b'' else 0)
            print(f'BASE\t{name}\texit={old.returncode}\tleak={int(old_leaks)}\tbytes={len(old.stdout.rstrip(bytes([10])))}')
        else:
            now = old if a.baseline_as_tool else subprocess.run(
                ['bash', str(Path(a.tool).resolve()), '--reason-only', mode, '--prefix', prefix],
                input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env={'PATH':'/usr/bin:/bin','LC_ALL':'C'})
            leak = bool(secret and secret.encode() in now.stdout)
            leaks += leak
            size = len(now.stdout[:-1]) if now.stdout.endswith(b'\n') else len(now.stdout)
            max_len = max(max_len, size)
            ok = (now.returncode == (3 if expected == b'' else 0) and not leak and size <= 160
                  and (expected is None or now.stdout == expected)
                  and (expected == b'' or now.stdout.startswith((mode + '-path-gone:').encode()))
                  and (expected == b'' or now.stdout.count(b'\n') == 1)
                  and b'\t' not in now.stdout and not now.stderr)
            print(f'CASE\t{"pass" if ok else "FAIL"}\t{name}\texit={now.returncode}\tleak={int(leak)}\tbase_leak={int(old_leaks)}\tbytes={size}')
            if not ok:
                print('DETAIL', repr(now.stdout), repr(now.stderr))
        failed += not ok
print(f'SUMMARY\ttotal={len(cases)}\tpass={len(cases)-failed}\tfail={failed}\tleaks={leaks}\tbase_leaks={base_leaks}\tmax_reason_bytes={max_len}')
raise SystemExit(int(bool(failed or (not a.baseline_only and not base_leaks))))
PY
