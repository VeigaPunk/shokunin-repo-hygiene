import re, sys, collections
S = "/fast/scratch/hyaku/souji-r41/R41w2sentinel02"
for f in sys.argv[1:]:
    print("######", f.rsplit('/',1)[1])
    ok_exec = collections.Counter(); fork_pids=set(); sigs=[]
    devnull_writes = collections.Counter()
    rel_or_out = collections.Counter()
    last_by_pid = {}
    ftr=[]; rmdir_line=None
    lines = open(f, errors='replace').read().split('\n')
    for i,line in enumerate(lines):
        m = re.match(r'^\*?\s*\d+\s+(\d+)\s+(.*)$', line) or re.match(r'^\*?(\d+)\s+(.*)$', line)
        if not m: continue
        pid, body = m.group(1), m.group(2)
        last_by_pid[pid] = i
        if body.startswith('execve(') and body.rstrip().endswith('= 0'):
            p = re.match(r'execve\("([^"]*)"', body).group(1)
            ok_exec[p]+=1
        if re.match(r'(clone|vfork)\(', body) and '= ' in body: fork_pids.add(body.rsplit('=',1)[1].strip()[:12])
        if re.search(r'\b(kill|tgkill|tkill)\(', body): sigs.append(body[:160])
        if re.match(r'write(v)?\(\d+</dev/null>', body):
            fd = re.match(r'write(?:v)?\((\d+)', body).group(1)
            devnull_writes[(pid, fd)] += 1
        if re.match(r'rmdir\(".*souji-r41-order|rmdir\(".*tmp[a-z0-9_]{8}"\)', body) or re.match(r'rmdir\("/fast/scratch/hyaku/souji-r41/R41w2sentinel02/work/[^"]*/[^"/]*"\)', body):
            rmdir_line = i
        if '---' in body and 'SIG' in body: sigs.append('SIGNAL-LINE pid=%s %s' % (pid, body[:160]))
        if 'killed by' in body or 'exited with' in body or 'exit_group' in body:
            pass
    print("successful execve (distinct binaries, count):")
    for p,n in ok_exec.most_common(): print("   %3d %s" % (n,p))
    print("clone/vfork children created (count): %d" % len(fork_pids))
    print("write(fd</dev/null>) by (pid,fd):", dict(devnull_writes))
    print("signal-related lines:", len(sigs))
    for s in sigs[:8]: print("   ", s)
    print("first rmdir of scratch-tree line index:", rmdir_line, "of", len(lines))
    if rmdir_line is not None:
        after = lines[rmdir_line+1:]
        acts = [l for l in after if re.search(r'\b(openat|mkdir|creat|rename|link|symlink|unlink|unlinkat|chmod|mknod|write)\(', l) and 'work/' in l and ('O_WRONLY' in l or 'O_CREAT' in l or re.search(r'\b(mkdir|rename|link|symlink|unlink|unlinkat|chmod|mknod|write)\(', l))]
        print("  write-class syscalls after scratch rmdir referencing work/: %d" % len(acts))
        for a in acts[:15]: print("    ", a[:220])
