import re, sys, collections
S = "/fast/scratch/hyaku/souji-r41/R41w2sentinel02"
WORK = S + "/work/"
files = sys.argv[1:]
LINE = re.compile(r'^(?:\*)?\s*(\d+)\s*\|?\s*(\d+)?\s*(.*)$')
# strace -f -y lines: "[*]PID|? SYSCALL(...)" ; with pid prefix "3284681 ..." after line numbers
PATHRE = re.compile(r'"([^"]*)"')
out = collections.OrderedDict()
def add(k, v):
    out.setdefault(k, []).append(v)
for f in files:
    tag = f.rsplit('/',1)[1]
    for raw in open(f, errors='replace'):
        line = raw.rstrip('\n')
        m = re.match(r'^\*?\s*\d+\s+(\d+)\s+(.*)$', line) or re.match(r'^\*?(\d+)\s+(.*)$', line)
        if not m:
            continue
        pid, body = m.group(1), m.group(2)
        # strip "<... x resumed>" fragments not needed; take syscall name
        sc = re.match(r'^(?:<\.\.\. )?([a-z_0-9]+)', body)
        name = sc.group(1) if sc else '?'
        if name in ('openat','open','creat'):
            if re.search(r'O_(WRONLY|RDWR|CREAT|TRUNC|APPEND)', body) or name=='creat':
                p = PATHRE.findall(body)
                path = p[0] if p else '?'
                flags = re.search(r'(O_[A-Z_|]+)', body)
                add(tag+' WRITE-OPEN', (pid, path, flags.group(1) if flags else '', 'ok' if '= -1' not in body else 'fail'))
        elif name in ('chmod','fchmodat','fchmodat2','fchmod','chown','fchown','fchownat','lchown'):
            add(tag+' CHMOD/CHOWN', (pid, body[:260]))
        elif name in ('mkdir','mkdirat','mknod','mknodat','symlink','symlinkat','link','linkat','unlink','unlinkat','rmdir','rename','renameat','renameat2','truncate','ftruncate','utimensat'):
            add(tag+' FS-MUTATE '+name, (pid, body[:260]))
        elif name in ('execve',):
            add(tag+' EXECVE-OK' if ('= 0' in body[-12:] or body.rstrip().endswith('= 0')) else tag+' EXECVE-FAIL', (pid, body[:200]))
        elif name in ('clone','clone3','vfork','fork'):
            add(tag+' FORK', (pid, body[:120]))
        elif name in ('kill','tgkill','tkill','rt_sigqueueinfo'):
            add(tag+' SIGNAL-SENT', (pid, body[:200]))
        elif name in ('write','writev','pwrite64'):
            if '</dev/null>' in body:
                add(tag+' WRITE-TO-/dev/null', (pid, body[:200]))
        if '</dev/null>' in body and name in ('openat','open') and 'O_WRONLY' in body or ('"/dev/null"' in body and 'O_RDWR' in body):
            pass
for k, v in out.items():
    print("== %s: %d" % (k, len(v)))
    seen = collections.Counter()
    for item in v:
        key = item[1] if len(item)>1 else item
        seen[str(item)] += 1
    # print distinct paths with counts for write opens; full detail for others (capped)
    if 'WRITE-OPEN' in k:
        c = collections.Counter((it[1], it[2], it[3]) for it in v)
        for (path, fl, st), n in sorted(c.items()):
            inside = path.startswith(WORK) or path.startswith(S+"/strace/") 
            print("   [%s] %s  flags=%s  %s  x%d" % ("in-scratch" if inside else "OUTSIDE", path, fl, st, n))
    else:
        for it in v[:12]:
            print("   ", it)
        if len(v) > 12:
            print("    ... (%d more)" % (len(v)-12))
