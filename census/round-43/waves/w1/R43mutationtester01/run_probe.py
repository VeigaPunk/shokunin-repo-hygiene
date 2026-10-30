#!/usr/bin/env python3
"""Axes: discrimination sensitivity, mutation isolation, byte restoration."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

LANE = Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
SEAT = LANE / '.ufo/waves/round-43/w1/R43mutationtester01'
S = Path('/fast/scratch/hyaku/souji-r43/R43mutationtester01')
FROZEN = 'f8c805dbfa7f45814cf9a7270fa8bbffb41a8373'
TIP = '13de0e84b45efd1113f077d58fc1e89bc586a013'
COUNTER = 'census/round-43/c1-counter.py'
FIXTURE = 'tests/fixtures/r43-correction-prose.py'
def sha(b):
    return hashlib.sha256(b).hexdigest()
def committed(path):
    return subprocess.run(['git', '-C', str(LANE), 'show', FROZEN + ':' + path], check=True, capture_output=True).stdout

# Each row changes exactly one behavior-bearing expression.
MUTATIONS = [
 ('M01', '(R39|DE|SC|SRC)', '([A-Z]+)', 'Accept arbitrary uppercase correction tags', 'unknown-tag-correction'),
 ('M02', 'file=(\\S+) field=', 'file=(\\S+) +field=', 'Accept repeated spaces before field', 'double-space-correction'),
 ('M03', '(`{3,}|~{3,})', '(`{3,})', 'Ignore tilde fences', 'tilde-fenced'),
 ('M04', 'fence = not fence', 'fence = True', 'Never close fences', 'correction-after-closed-fence'),
 ('M05', "u = re.sub(r'#[^ ]*$', '', u)", 'u = u', 'Do not strip URL fragments', 'w04-fragment-normalization'),
 ('M06', 'u and u in seen and key not in scopes', 'u and u in seen', 'Count same-scope URL repeats', 'w04-same-scope-repeat'),
 ('M07', '(got == int(m.group(1)) and ("rows=%s" % stale) in blob.decode("utf-8", "replace"),', '(got == int(m.group(1)),', 'Skip rows stale-token proof', 'rows-stale-token-absent'),
 ('M08', '(got == int(m.group(1)) and ("W04=%s" % stale) in blob.decode("utf-8", "replace"),', '(got == int(m.group(1)),', 'Skip W04 stale-token proof', 'w04-stale-token-absent'),
 ('M09', 'if derived not in blob.decode("utf-8", "replace"):', 'if False:', 'Skip header derived-revision membership', 'header-derived-revision-absent'),
 ('M10', 'return (not others, "others=%s" % others[:2])', 'return (True, "others=%s" % others[:2])', 'Ignore unrelated header diff paths', 'header-revision-unrelated-path'),
 ('M11', 'return False, "kind-unknown"', 'return True, "kind-unknown"', 'Accept unknown rederive kind', 'unknown-rederive-kind'),
 ('M12', 'int(f[0]) > base_lines:', 'int(f[0]) > base_lines + 1:', 'Skip first appended mismatch', 'boundary-mismatch'),
 ('M13', 'retracted += 1', 'retracted += 0', 'Ignore valid retractions', 'retracted'),
 ('M14', 'if not m or m.group(1) not in required:', 'if not m:', 'Accept retraction of unknown id', 'unknown-id-retraction'),
 ('M15', 'elif raw.startswith("RETRACT-CORRECTION"):', 'elif RETRACT.match(raw):', 'Silently ignore malformed retractions', 'malformed-retraction'),
 ('M16', 'duplicate += 1', 'duplicate += 0', 'Silently accept duplicate correction', 'duplicated'),
 ('M17', 'if kind == "census-rows":', 'if kind == "census-row":', 'Miss census-rows dispatch', 'honest-corrections'),
 ('M18', 'if kind == "census-w04":', 'if kind == "census-w4":', 'Miss census-w04 dispatch', 'honest-corrections'),
 ('M19', 'if kind == "receipt-header-rev":', 'if kind == "receipt-header":', 'Miss receipt-header-rev dispatch', 'honest-corrections'),
]

def main():
    SEAT.mkdir(parents=True, exist_ok=True)
    S.mkdir(parents=True, exist_ok=True)
    original = committed(COUNTER)
    fixture = committed(FIXTURE)
    lane_before = sha((LANE / COUNTER).read_bytes())
    (SEAT / 'frozen-counter42.py').write_bytes(committed('census/round-42/c1-counter.py'))
    (SEAT / 'pristine-counter.py').write_bytes(original)
    (SEAT / 'frozen-fixture.py').write_bytes(fixture)
    env = dict(os.environ, TMPDIR=str(S))
    results = []
    def detect(label, counter):
        work = S / (label + '-work')
        cmd = ['python3', '-B', str(SEAT / 'frozen-fixture.py'), '--work', str(work), '--lane-root', str(LANE), '--rev43', TIP, '--counter42', str(SEAT / 'frozen-counter42.py'), '--counter43', str(counter)]
        p = subprocess.run(cmd, cwd=S, env=env, capture_output=True, text=True, timeout=1800)
        (SEAT / (label + '.stdout.txt')).write_text(p.stdout)
        (SEAT / (label + '.stderr.txt')).write_text(p.stderr)
        return {'command': cmd, 'exit': p.returncode, 'summary43': [x for x in p.stdout.splitlines() if x.startswith('SUMMARY43')], 'summary42': [x for x in p.stdout.splitlines() if x.startswith('SUMMARY42')], 'failed_cases': [x for x in p.stdout.splitlines() if x.startswith('case-') and x.endswith('FAIL')]}
    try:
        baseline = detect('baseline', SEAT / 'pristine-counter.py')
        (SEAT / 'baseline.json').write_text(json.dumps(baseline, indent=2) + '\n')
        if baseline['exit'] != 0:
            raise RuntimeError('Baseline fails: mutation verdicts inconclusive; see baseline output')
        def probe(row):
            mid, old, new, change, missing = row
            text = original.decode()
            assert text.count(old) == 1, (mid, text.count(old))
            mutant = text.replace(old, new, 1).encode()
            saved = SEAT / (mid + '-counter.py')
            saved.write_bytes(mutant)
            active = S / (mid + '-active.py')
            active.write_bytes(original)
            before = sha(active.read_bytes())
            try:
                active.write_bytes(mutant)
                observed = detect(mid, active)
                survived = observed['summary43'] == ['SUMMARY43 cases=10 pass=10 fail=0']
                result = dict(id=mid, change=change, missing_case=missing, before_sha256=before, mutant_sha256=sha(mutant), verdict='SURVIVOR' if survived else 'KILLED', **observed)
            finally:
                active.write_bytes(original)
            result['restored_sha256'] = sha(active.read_bytes())
            assert result['restored_sha256'] == before
            return result
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            for r in pool.map(probe, MUTATIONS):
                results.append(r)
                (SEAT / (r['id'] + '.json')).write_text(json.dumps(r, indent=2) + '\n')
        restored = detect('restored', SEAT / 'pristine-counter.py')
        receipt = dict(axes=['discrimination sensitivity', 'mutation isolation', 'byte restoration'], frozen=FROZEN, tip=TIP, original_sha256=sha(original), lane_counter_before=lane_before, fixture_sha256=sha(fixture), baseline=baseline, mutants=results, restored=restored, lane_counter_after=sha((LANE / COUNTER).read_bytes()))
        (SEAT / 'results.json').write_text(json.dumps(receipt, indent=2) + '\n')
        print(json.dumps({'baseline': baseline['summary43'], 'restored': restored['summary43'], 'table': [(r['id'], r['summary43'], r['verdict']) for r in results]}, indent=2))
    finally:
        shutil.rmtree(S)

if __name__ == '__main__':
    main()

