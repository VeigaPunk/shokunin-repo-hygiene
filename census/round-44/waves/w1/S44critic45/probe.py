#!/usr/bin/env python3
import hashlib, json, os, pathlib, shlex, subprocess, sys
OUT = pathlib.Path(__file__).resolve().parent
LANE = pathlib.Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
SCRATCH = pathlib.Path('/fast/scratch/hyaku/souji-r44/S44critic45')
FROZEN = 'd314fd6e85d62565344fa6c4b102f52f62297884'
BASE = '55d7af6f5a22340f7a3de1c386e514ababfaa75f'
FIXTURE = OUT / 'fixture'
transcript = []
def run(args, cwd=SCRATCH, data=None, allow=False):
    p = subprocess.run([str(x) for x in args], cwd=cwd, input=data, capture_output=True)
    transcript.append('$ ' + shlex.join([str(x) for x in args]) + '\n' + p.stdout.decode(errors='replace') + p.stderr.decode(errors='replace') + 'exit=' + str(p.returncode) + '\n')
    (OUT / 'commands.txt').write_text('\n'.join(transcript))
    if p.returncode and not allow:
        raise RuntimeError(transcript[-1])
    return p

def source(path, rev=FROZEN):
    return run(['git', '-C', LANE, 'show', rev + ':' + path]).stdout

def guarded_git(*args, data=None):
    actual = run(['git', '-C', FIXTURE, 'rev-parse', '--show-toplevel']).stdout.decode().strip()
    assert actual == str(FIXTURE), actual
    return run(['git', '-C', FIXTURE, *args], data=data)

run(['git', 'clone', '--shared', '--no-checkout', LANE, FIXTURE])
# All candidate mutations take place in the isolated fixture, never source git state.
counter = source('census/round-44/c1-counter.py')
(OUT / 'frozen-c1-counter.py').write_bytes(counter)
population = source('census/round-44/c1-population.tsv')
(OUT / 'frozen-c1-population.tsv').write_bytes(population)
assert hashlib.sha256(counter).hexdigest() == 'dde1ae29105ac84c7ce83705547517c501033b0fce38ddbd6a92b4bd0a4b7c51'
assert hashlib.sha256(population).hexdigest() == '422875449468ae146ef029a4622d8f521f05f570a9b79f90286be03b7b0c1e2c'
instrument = FIXTURE / 'tools/souji-declared-evidence.py'
instrument.parent.mkdir(parents=True, exist_ok=True)
instrument.write_bytes(source('tools/souji-declared-evidence.py'))
cmd = [sys.executable, '-B', OUT / 'frozen-c1-counter.py', '--root', FIXTURE, '--rev', FROZEN, '--scratch', SCRATCH]
emit = run(cmd + ['--emit']).stdout.decode()
(OUT / 'derivations.tsv').write_text(emit)
rows = []
for line in emit.splitlines():
    cid, *fields = line.split('\t')
    d = dict(field.split('=', 1) for field in fields)
    rows.append('CORRECTION-R44 id=' + cid + ' file=SCORECARD.md line=' + d['line'] + ' class=' + d['class'] + ' stale=' + d['stale'] + ' derived=' + d['derived'] + ' rev=' + BASE + ' scope=base-SCORECARD-token-referents')
assert len(rows) == 66
baseline = '# Isolated registration control\n\n' + '\n'.join(rows) + '\n'
extra = 'CORRECTION-R44 id=R44-67 file=SCORECARD.md line=999999 class=mismatch:path-absent stale=synthetic-extra-register-row derived=UNHELD rev=' + BASE + ' scope=base-SCORECARD-token-referents\n'
results = {}
for label, text in [('baseline', baseline), ('extra-register-row', baseline + extra)]:
    (OUT / (label + '-lesson.md')).write_text(text)
    guarded_git('read-tree', FROZEN)
    lesson = FIXTURE / 'corpus/lessons/round-44.md'
    lesson.parent.mkdir(parents=True, exist_ok=True)
    lesson.write_text(text)
    guarded_git('add', '--', 'corpus/lessons/round-44.md')
    tree = guarded_git('write-tree').stdout.decode().strip()
    rev = guarded_git('-c', 'user.name=Seat S44critic45', '-c', 'user.email=S44critic45@invalid', 'commit-tree', tree, '-p', FROZEN, '-m', 'Isolated ' + label + ' fixture').stdout.decode().strip()
    probe = run([sys.executable, '-B', OUT / 'frozen-c1-counter.py', '--root', FIXTURE, '--rev', rev, '--scratch', SCRATCH], allow=True)
    results[label] = {'rev': rev, 'exit': probe.returncode, 'output': probe.stdout.decode(), 'stderr': probe.stderr.decode(), 'syntactic_corrections': text.count('CORRECTION-R44 id=')}
    (OUT / (label + '.txt')).write_text(probe.stdout.decode() + probe.stderr.decode() + 'exit=' + str(probe.returncode) + '\n')
(OUT / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
# Q76: whole-file search at the population base, not just the original cell.
sc = source('SCORECARD.md', BASE).decode()
(OUT / 'base-SCORECARD.md').write_text(sc)
terms = ['SCORECARD.md:174', 'c1-control-stub.tsv', 'SCORECARD.md:175', 'R30-CORRECTION', 'L35']
audit = ['Q76 selected existing row: line=174 stale=c1-control-stub.tsv; synthetic extra row: line=999999 stale=synthetic-extra-register-row.']
for term in terms + ['SCORECARD.md:999999', 'synthetic-extra-register-row']:
    matches = [f'{i}:{line}' for i, line in enumerate(sc.splitlines(), 1) if term in line]
    audit.append('\nSEARCH ' + repr(term) + '\n' + ('\n'.join(matches) if matches else 'NO MATCH'))
(OUT / 'q76-base-audit.txt').write_text('\n'.join(audit) + '\n')
print(json.dumps(results, indent=2))
