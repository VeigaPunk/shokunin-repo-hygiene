import re, sys, collections
S = "/fast/scratch/hyaku/souji-r41/R41w2sentinel02"
WORK = S + "/work/"
files = ["strace/r41-refusal-sites.strace", "strace/r41-drift-record-order.strace", "strace/term-refusal-sites.strace", "strace/term-drift-record-order.strace"]
def pidbody(line):
    m = re.match(r'^\*?\s*\d+\s+(\d+)\s+(.*)$', line) or re.match(r'^\*?(\d+)\s+(.*)$', line)
    return (m.group(1), m.group(2)) if m else (None, None)
targets = collections.Counter()
for f in files:
    L = open(S + "/" + f, errors='replace').read().split('\n')
    # 1. write-class targets (fs mutation or write-open) per syscall, absolute or AT_FDCWD-cwd-relative
    for line in L:
        pid, body = pidbody(line)
        if body is None: continue
        if re.match(r'openat\(', body) and re.search(r'O_(WRONLY|RDWR|CREAT|TRUNC|APPEND)', body):
            if body.rstrip().endswith('= -1 ' ) or ' = -1 ' in body: 
                # failed open still counts as attempted write-open
                pass
            m = re.search(r'openat\((?:AT_FDCWD|\d+)<([^>]*)>, "([^"]*)"', body)
            if m:
                base, p = m.group(1), m.group(2)
                full = p if p.startswith('/') else base.rstrip('/') + '/' + p
                targets[(f.split('/')[-1], 'open-w', full)] += 1
        for sc in ('mkdir','mkdirat','mknod','mknodat','symlink','symlinkat','link','linkat','unlink','unlinkat','rmdir','rename','renameat','renameat2','chmod','fchmodat','truncate','utimensat'):
            if re.match(sc + r'\(', body):
                for p in re.findall(r'"([^"]*)"', body)[:2]:
                    if p.startswith('/'): targets[(f.split('/')[-1], sc, p)] += 1
                    else:
                        cw = re.search(r'<([^>]*)>', body)
                        targets[(f.split('/')[-1], sc, (cw.group(1) if cw else '?') + '/' + p)] += 1
                break
# categorize
cat = collections.Counter()
outside = []
for (f, kind, p), n in targets.items():
    if p.startswith(WORK) or p.startswith(S + "/strace/"):
        cat['in-scratch-work' if p.startswith(WORK) else 'scratch-strace-stdout'] += n
    elif p.startswith('/dev/null') or p.endswith('/null') and '/dev/' in p:
        cat['dev-null'] += n
    elif p.startswith('/tmp') or p.startswith('/var/tmp') or p.startswith('/home/vgpnk/Projects/shokunin/souji-shokunin'):
        outside.append((f, kind, p, n))
    else:
        outside.append((f, kind, p, n))
print("categories:", dict(cat))
print("write-class targets outside scratch+/dev/null (count=%d):" % len(outside))
for o in outside[:80]: print("   ", o)
# relative paths resolved against cwd annotations
rel = [k for k in targets if not k[2].startswith('/')]
print("unresolved relative:", rel[:5])
# 2. distinct executed binaries (successful execve), pairing unfinished->resumed
ex = collections.Counter()
for f in files:
    L = open(S + "/" + f, errors='replace').read().split('\n')
    pending = {}
    for line in L:
        pid, body = pidbody(line)
        if body is None: continue
        if body.startswith('execve("') :
            p = re.match(r'execve\("([^"]*)"', body).group(1)
            if body.rstrip().endswith('= 0'): ex[(f.split('/')[-1], p)] += 1
            elif body.rstrip().endswith('<unfinished ...>'): pending[pid] = p
        elif body.startswith('<... execve resumed>') and body.rstrip().endswith('= 0') and pid in pending:
            ex[(f.split('/')[-1], pending.pop(pid))] += 1
print("successful execve binaries:")
for k,n in sorted(ex.items()): print("   %-28s %3d  %s" % (k[0], n, k[1]))
# 3. the sequence after the tool's /dev/null json open (refusal-sites)
L = open(S + "/strace/r41-refusal-sites.strace", errors='replace').read().split('\n')
idx = [i for i,l in enumerate(L) if '"null", O_WRONLY|O_CREAT|O_NONBLOCK|O_NOFOLLOW' in l]
print("open_nofollow(/dev/null) occurrences:", len(idx))
if idx:
    i = idx[0]
    for l in L[i:i+5]: print("   ", l[:200])
idx2 = [i for i,l in enumerate(L) if '"hl", O_WRONLY|O_CREAT|O_NONBLOCK|O_NOFOLLOW' in l]
if idx2:
    i = idx2[0]
    print("open_nofollow(hardlink):")
    for l in L[i:i+4]: print("   ", l[:200])
print("ftruncate/truncate syscalls in refusal-sites:", sum(1 for l in L if re.search(r'\b(ftruncate|truncate)\(', l)))
L2 = open(S + "/strace/r41-drift-record-order.strace", errors='replace').read().split('\n')
print("ftruncate/truncate syscalls in drift-order:", sum(1 for l in L2 if re.search(r'\b(ftruncate|truncate)\(', l)))
print("tool open_nofollow for /dev/null in drift-order (should be 0):", sum(1 for l in L2 if '"null", O_WRONLY|O_CREAT' in l))
