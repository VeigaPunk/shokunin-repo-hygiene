import re, sys, os, shutil
T = sys.argv[1]  # target repo root
W = '/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-31/w1'
docs = open(W + '/deliver-docs-f1.md').read()
blocks = re.findall(r"```[a-z]*\n(.*?)\n```", docs, re.S)
cur_readme, new_readme = blocks[1], blocks[2]
readme_app, prov_app = blocks[4], blocks[5]
cur_skill, new_skill, skill_new = blocks[6], blocks[7], blocks[8]
assert cur_readme.startswith('| F1 git-native') and new_readme.startswith('| F1 git-native')
assert readme_app.startswith('## Round 31 — F1') and prov_app.startswith('## Round 31 boundary note')
assert cur_skill.startswith('- **jj: a keep ref is removed') and new_skill.startswith('- **jj: a keep ref is removed by jj')
assert skill_new.startswith('- **jj: an object outlives')


def rw(path, fn):
    p = os.path.join(T, path)
    s = open(p).read()
    s2 = fn(s)
    assert s2 != s, path
    open(p, 'w').write(s2)


def once(s, a, b):
    assert s.count(a) == 1, (a[:60], s.count(a))
    return s.replace(a, b)


rw('corpus/README.md', lambda s: once(s, cur_readme, new_readme).rstrip('\n') + '\n\n' + readme_app + '\n')
rw('PROVINCE.md', lambda s: s.rstrip('\n') + '\n\n' + prov_app + '\n')
rw('SKILL.md', lambda s: once(s, cur_skill, new_skill + '\n' + skill_new))
# entry, fixture, record, snapshots, receipts
os.makedirs(T + '/census/round-31/sources', exist_ok=True)
os.makedirs(T + '/census/round-31/records', exist_ok=True)
shutil.copyfile(W + '/deliver-entry-jj-dropped-keep-object-lifetime.md', T + '/corpus/knowledge/jj-dropped-keep-object-lifetime.md')
shutil.copyfile(W + '/deliver-r31-jj-object-clock.sh', T + '/tests/fixtures/r31-jj-object-clock.sh')
os.chmod(T + '/tests/fixtures/r31-jj-object-clock.sh', 0o755)
shutil.copyfile(W + '/deliver-jj-object-clock-run.txt', T + '/census/round-31/records/jj-object-clock-run.txt')
for f in ('git-reflog.adoc', 'gc.adoc', 'git-compatibility.md', 'SHA256SUMS'):
    shutil.copyfile(W + '/sources/' + f, T + '/census/round-31/sources/' + f)
shutil.copyfile(W + '/deliver-fetch-receipts.tsv', T + '/census/round-31/records/fetch-receipts.tsv')
# SOURCES: S222 row after S221, used-by appends on held rows
rows = open(W + '/deliver-sources-rows.md').read()
s222 = [l for l in rows.splitlines() if l.startswith('| S222 |')][0]
ENT = 'corpus/knowledge/jj-dropped-keep-object-lifetime.md'


def sources(s):
    out = []
    for l in s.splitlines():
        m = re.match(r'^\| (S\d+) \|', l)
        if m and m.group(1) in ('S002', 'S054', 'S063', 'S117', 'S220'):
            c = l.split('|')
            # used-by is the last data cell (index -2)
            assert ENT not in c[-2]
            c[-2] = ' ' + c[-2].strip() + ', ' + ENT + ' '
            l = '|'.join(c)
        out.append(l)
        if m and m.group(1) == 'S221':
            out.append(s222)
    return '\n'.join(out) + '\n'


rw('corpus/SOURCES.md', sources)
print('applied')
