#!/usr/bin/env python3
"""S60ReviewerRecorder C2 falsification harness (scratch, read-only on the lane).

Modes:
  eight   --tool PATH --mode base|cand : independent 8-case fixture run
  probe   --tool PATH --mode base|cand --probe NAME : single attack probe
  all     --tool PATH --mode base|cand : eight + every probe
"""
import argparse, hashlib, os, shutil, signal, subprocess, sys, time, glob, json
from pathlib import Path, PurePosixPath

SCRATCH = Path(__file__).resolve().parent
GITENV = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LC_ALL': 'C',
          'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
          'GIT_AUTHOR_NAME': 'fixture', 'GIT_AUTHOR_EMAIL': 'fixture@example.invalid',
          'GIT_COMMITTER_NAME': 'fixture', 'GIT_COMMITTER_EMAIL': 'fixture@example.invalid',
          'GIT_AUTHOR_DATE': '2026-11-01T00:00:00+0000',
          'GIT_COMMITTER_DATE': '2026-11-01T00:00:00+0000'}


def git(root, *args, check=True):
    p = subprocess.run(['git', '-C', str(root)] + list(args),
                       capture_output=True, env=GITENV, timeout=60)
    if check and p.returncode:
        raise SystemExit('fixture git failed: %r %s %s' % (args, p.stdout, p.stderr))
    return p


def build_repo(work: Path):
    """Isolated fixture repo. Returns dict(rev, instr_rel, instr_sha, repo)."""
    work.mkdir(parents=True, exist_ok=True)
    repo = work / 'repo'
    repo.mkdir()
    git(repo, 'init', '-q', '-b', 'main')
    top = git(repo, 'rev-parse', '--show-toplevel').stdout.decode().strip()
    assert os.path.realpath(top) == os.path.realpath(repo), 'toplevel mismatch %r' % top
    (repo / 'tools').mkdir()
    (repo / 'tools' / 'instrument.py').write_text('# fixture instrument v1\n')
    git(repo, 'add', 'tools/instrument.py')
    git(repo, 'commit', '-q', '-m', 'fixture base')
    rev = git(repo, 'rev-parse', 'HEAD').stdout.decode().strip()
    sha = hashlib.sha256((repo / 'tools' / 'instrument.py').read_bytes()).hexdigest()
    return {'repo': repo, 'rev': rev, 'instr': 'tools/instrument.py', 'sha': sha}


def tool_args(mode, repo, rev, instr, out, cmd, extra=()):
    """Adapter: translate the common call into the tool's interface."""
    if mode == 'base':
        return ['bash', str(TOOL[0]), str(repo), rev, instr, str(out), '--'] + list(cmd)
    # candidate: --root LANE --rev REV --instrument PATH --out FILE -- cmd...
    return ['python3', str(TOOL[0]), '--root', str(repo), '--rev', rev,
            '--instrument', instr, '--out', str(out), '--'] + list(cmd) + list(extra)

TOOL = [None]


def run_tool(mode, repo, rev, instr, out, cmd, extra=(), env_extra=None, timeout=30):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    p = subprocess.run(tool_args(mode, repo, rev, instr, out, cmd, extra),
                       capture_output=True, env=env, timeout=timeout, start_new_session=True)
    return p


def siblings(out: Path):
    return sorted(x.name for x in out.parent.iterdir() if x.name != out.name)


# ---------------------------------------------------------------- 8-case run
def case_eight(mode, work):
    r = build_repo(work / 'c8')
    repo, rev, instr, sha = r['repo'], r['rev'], r['instr'], r['sha']
    res = {}

    def rec(name, ok, detail):
        res[name] = (ok, detail)
        print('CASE %s %s %s' % (name, 'pass' if ok else 'FAIL', detail))

    # 1 clean
    out = work / 'c8' / 'out1' / 'r.txt'
    out.parent.mkdir(exist_ok=True)
    p = run_tool(mode, repo, rev, instr, out, ['echo', 'hello'])
    txt = out.read_bytes() if out.exists() else b''
    ok = (p.returncode == 0 and out.exists()
          and b'instrument=' in txt and ('instrument_sha256=' + sha).encode() in txt
          and ('rev=' + rev).encode() in txt and b'command=' in txt
          and txt.rstrip().endswith(b'EXIT=0') and not siblings(out))
    rec('1-clean', ok, 'rc=%d out=%d siblings=%s' % (p.returncode, len(txt), siblings(out)))

    # 2 overwrite refusal
    out = work / 'c8' / 'out2' / 'r.txt'
    out.parent.mkdir(exist_ok=True)
    out.write_bytes(b'KNOWN-BYTES')
    p = run_tool(mode, repo, rev, instr, out, ['echo', 'hello'])
    ok = (p.returncode == 2 and out.read_bytes() == b'KNOWN-BYTES' and not siblings(out))
    rec('2-overwrite', ok, 'rc=%d bytes=%r siblings=%s' % (p.returncode, out.read_bytes()[:20], siblings(out)))

    # 3 atomic-in-flight
    out = work / 'c8' / 'out3' / 'r.txt'
    out.parent.mkdir(exist_ok=True)
    p = subprocess.Popen(tool_args(mode, repo, rev, instr, out, ['bash', '-c', 'sleep 1; echo done']),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    time.sleep(0.3)
    early = out.exists()
    p.wait(timeout=20)
    txt = out.read_bytes() if out.exists() else b''
    ok = (not early and txt.rstrip().endswith(b'EXIT=0'))
    rec('3-inflight', ok, 'early_exists=%s final_last=%r' % (early, txt[-20:]))

    # 4 kill residue
    out = work / 'c8' / 'out4' / 'r.txt'
    out.parent.mkdir(exist_ok=True)
    p = subprocess.Popen(tool_args(mode, repo, rev, instr, out, ['bash', '-c', 'sleep 3; echo done']),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    time.sleep(0.4)
    try:
        os.killpg(os.getpgid(p.pid), signal.SIGKILL)
    except ProcessLookupError:
        pass
    p.wait(timeout=20)
    sib = siblings(out)
    bad = [s for s in sib if '.tmp' in s or 'partial' in s or '.part' in s]
    ok = (not out.exists() and not bad)
    rec('4-killresidue', ok, 'out_exists=%s siblings=%s flagged=%s' % (out.exists(), sib, bad))

    # 5 bound
    out = work / 'c8' / 'out5' / 'r.txt'
    out.parent.mkdir(exist_ok=True)
    big = ['bash', '-c', 'head -c 2097152 /dev/zero | tr "\\0" x']
    if mode == 'cand':
        p = run_tool(mode, repo, rev, instr, out, big, extra=['--max-bytes', '65536'])
    else:
        p = run_tool(mode, repo, rev, instr, out, big)
    ok = (p.returncode == 2 and not out.exists())
    rec('5-bound', ok, 'rc=%d out_exists=%s' % (p.returncode, out.exists()))

    # 6 rev short
    out = work / 'c8' / 'out6' / 'r.txt'
    out.parent.mkdir(exist_ok=True)
    p = run_tool(mode, repo, rev[:12], instr, out, ['echo', 'x'])
    ok = (p.returncode == 2 and not out.exists())
    rec('6-shortrev', ok, 'rc=%d out_exists=%s' % (p.returncode, out.exists()))

    # 7 instrument absent at rev
    out = work / 'c8' / 'out7' / 'r.txt'
    out.parent.mkdir(exist_ok=True)
    p = run_tool(mode, repo, rev, 'tools/nope.py', out, ['echo', 'x'])
    ok = (p.returncode == 2 and not out.exists())
    rec('7-instrabsent', ok, 'rc=%d out_exists=%s' % (p.returncode, out.exists()))

    # 8 dirty tree
    out = work / 'c8' / 'out8' / 'r.txt'
    out.parent.mkdir(exist_ok=True)
    (repo / 'untracked.txt').write_text('dirty\n')
    p = run_tool(mode, repo, rev, instr, out, ['echo', 'x'])
    ok = (p.returncode == 2 and not out.exists())
    rec('8-dirtytree', ok, 'rc=%d out_exists=%s' % (p.returncode, out.exists()))

    npass = sum(1 for ok, _ in res.values() if ok)
    print('EIGHT cases=8 pass=%d fail=%d' % (npass, 8 - npass))
    return res


# ---------------------------------------------------------------- probes
def probe_toctou(mode, work):
    """(a) check-then-replace race: strace the rename family; then demonstrate
    clobbering via an LD_PRELOAD shim that creates OUT right before rename."""
    r = build_repo(work / 'a')
    repo, rev, instr = r['repo'], r['rev'], r['instr']
    out = work / 'a' / 'r.txt'
    # syscall evidence
    args = tool_args(mode, repo, rev, instr, out, ['echo', 'hello'])
    st = subprocess.run(['strace', '-f', '-e', 'trace=rename,renameat,renameat2,linkat,openat,unlink,unlinkat',
                         '-o', str(work / 'a' / 'strace.txt')] + args,
                        capture_output=True, timeout=60)
    lines = (work / 'a' / 'strace.txt').read_text(errors='replace').splitlines()
    renames = [l for l in lines if ('rename' in l or 'linkat' in l) and 'unfinished' not in l]
    uses_noreplace = any('RENAME_NOREPLACE' in l for l in renames)
    uses_link = any('linkat(' in l for l in renames)
    plain = [l for l in renames if ('renameat(' in l or 'rename(' in l or 'renameat2(' in l) and 'RENAME_NOREPLACE' not in l]
    print('TOCTOU-syscalls noreplace=%s linkat=%s plain_rename=%d' % (uses_noreplace, uses_link, len(plain)))
    for l in plain[:4]:
        print('  ', l.split(' ', 1)[-1][:160])
    # dynamic demonstration: shim creates OUT just before the rename lands
    shim = work / 'a' / 'toctou.so'
    ccode = r'''
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <dlfcn.h>
static int (*real_renameat2)(int, const char*, int, const char*, unsigned int);
static int (*real_renameat)(int, const char*, int, const char*);
static int (*real_rename)(const char*, const char*);
static void hit(const char *target, const char *dest) {
    const char *t = getenv("TOCTOU_TARGET");
    if (!t || !target || strcmp(target, t)) return;
    int fd = open(dest, O_CREAT|O_WRONLY|O_TRUNC, 0644);
    if (fd >= 0) { ssize_t w = write(fd, "RACED-IN", 8); (void)w; close(fd); }
    const char *f = getenv("TOCTOU_FIRED");
    if (f) { FILE *m = fopen(f, "w"); if (m) { fputs("1", m); fclose(m); } }
}
int renameat2(int od, const char *o, int nd, const char *n, unsigned int f) {
    if (!real_renameat2) real_renameat2 = dlsym(RTLD_NEXT, "renameat2");
    hit(n, n);
    return real_renameat2(od, o, nd, n, f);
}
int renameat(int od, const char *o, int nd, const char *n) {
    if (!real_renameat) real_renameat = dlsym(RTLD_NEXT, "renameat");
    hit(n, n);
    return real_renameat(od, o, nd, n);
}
int rename(const char *o, const char *n) {
    if (!real_rename) real_rename = dlsym(RTLD_NEXT, "rename");
    hit(n, n);
    return real_rename(o, n);
}
'''
    (work / 'a' / 'toctou.c').write_text(ccode)
    subprocess.run(['gcc', '-shared', '-fPIC', '-O1', '-o', str(shim), str(work / 'a' / 'toctou.c'), '-ldl'],
                   check=True, capture_output=True)
    # the strace run above wrote OUT: clear it so the shim run starts from "no OUT"
    out.unlink(missing_ok=True)
    fired = work / 'a' / 'shim-fired'
    fired.unlink(missing_ok=True)
    env = dict(os.environ, LD_PRELOAD=str(shim), TOCTOU_TARGET=str(out), TOCTOU_FIRED=str(fired))
    p = subprocess.run(args, capture_output=True, env=env, timeout=60)
    body = out.read_bytes() if out.exists() else b''
    raced = fired.exists()
    print('TOCTOU-race shim_fired=%s rc=%d out_head=%r receipt_intact=%s raced_bytes_survived=%s'
          % (raced, p.returncode, body[:24], body.startswith(b'instrument='), b'RACED-IN' in body))
    if not renames:
        verdict = 'NO-RENAME-AT-ALL: writer is not atomic (direct open/write to OUT)'
    elif uses_noreplace or uses_link:
        verdict = 'RACE-FREE primitive observed (RENAME_NOREPLACE/linkat)'
    else:
        verdict = 'VULNERABLE (check-then-replace; concurrent create at OUT is silently clobbered)'
    print('TOCTOU-VERDICT', verdict)
    return {'plain_rename': len(plain), 'noreplace': uses_noreplace, 'raced': raced}


def probe_out_fs(mode, work):
    """(b) OUT on another filesystem; symlinked OUT dir; symlinked OUT file."""
    r = build_repo(work / 'b' / 'repo-holder')
    repo, rev, instr = r['repo'], r['rev'], r['instr']
    out = {}
    # b1: OUT under /dev/shm (tmpfs) while lane (fixture repo) is on scratch fs
    d = work / 'b' / 'shm'
    d.mkdir(parents=True)
    shm_out = Path('/dev/shm') / ('s60rr-%d-r.txt' % os.getpid())
    try:
        p = run_tool(mode, repo, rev, instr, shm_out, ['echo', 'hello'])
        body = shm_out.read_bytes() if shm_out.exists() else b''
        out['b1-crossfs'] = 'rc=%d written=%d head=%r' % (p.returncode, len(body), body[:16])
        sib = [x for x in Path('/dev/shm').glob('s60rr-%d-*' % os.getpid()) if x != shm_out]
        out['b1-crossfs-siblings'] = [x.name for x in sib]
    finally:
        for x in Path('/dev/shm').glob('s60rr-%d-*' % os.getpid()):
            x.unlink()
    # b2: OUT through a symlinked intermediate dir pointing OUTSIDE the lane
    esc = work / 'b' / 'escape-outside-lane'
    esc.mkdir(parents=True)
    (repo / 'receipts').mkdir(exist_ok=True)
    os.symlink(str(esc), repo / 'receipts' / 'linkdir')
    out2 = repo / 'receipts' / 'linkdir' / 'r.txt'
    p = run_tool(mode, repo, rev, instr, out2, ['echo', 'hello'])
    wrote = esc.joinpath('r.txt').exists()
    out['b2-symlinkdir'] = 'rc=%d wrote_outside_lane=%s' % (p.returncode, wrote)
    # b3: OUT itself a dangling symlink to a victim file
    victim = work / 'b' / 'victim.txt'
    victim.write_bytes(b'VICTIM-ORIGINAL')
    (repo / 'receipts' / 'dang.txt').unlink(missing_ok=True) if False else None
    dang = repo / 'receipts' / 'dang.txt'
    if dang.exists() or dang.is_symlink():
        dang.unlink()
    os.symlink(str(victim), dang)
    p = run_tool(mode, repo, rev, instr, dang, ['echo', 'hello'])
    vb = victim.read_bytes()
    out['b3-symlinkout'] = 'rc=%d victim_clobbered=%s victim=%r' % (p.returncode, vb != b'VICTIM-ORIGINAL', vb[:16])
    for k, v in out.items():
        print(k, v)
    return out


def probe_fsync_kill(mode, work):
    """(c) SIGKILL between fsync and rename via an fsync-sleeping LD_PRELOAD."""
    r = build_repo(work / 'c')
    repo, rev, instr = r['repo'], r['rev'], r['instr']
    shim = work / 'c' / 'fsynckill.so'
    ccode = r'''
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <dlfcn.h>
static int (*real_fsync)(int);
int fsync(int fd) {
    if (!real_fsync) real_fsync = dlsym(RTLD_NEXT, "fsync");
    int r = real_fsync(fd);
    const char *m = getenv("FSYNC_MARKER");
    if (m) { FILE *f = fopen(m, "w"); if (f) { fputc('1', f); fclose(f); } }
    const char *s = getenv("FSYNC_SLEEP");
    if (s) sleep(atoi(s));
    return r;
}
'''
    (work / 'c' / 'fsynckill.c').write_text(ccode)
    subprocess.run(['gcc', '-shared', '-fPIC', '-O1', '-o', str(shim), str(work / 'c' / 'fsynckill.c'), '-ldl'],
                   check=True, capture_output=True)
    out = work / 'c' / 'r.txt'
    out.parent.mkdir(exist_ok=True)
    marker = work / 'c' / 'fsync.marker'
    env = dict(os.environ, LD_PRELOAD=str(shim), FSYNC_MARKER=str(marker), FSYNC_SLEEP='20')
    p = subprocess.Popen(tool_args(mode, repo, rev, instr, out, ['echo', 'hello']),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True, env=env)
    deadline = time.time() + 25
    while time.time() < deadline and not marker.exists() and p.poll() is None:
        time.sleep(0.05)
    killed = False
    if marker.exists() and p.poll() is None:
        time.sleep(0.3)          # inside the fsync sleep, before rename
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
            killed = True
        except ProcessLookupError:
            pass
    p.wait(timeout=30)
    sib = siblings(out)
    resid = [(s, (out.parent / s).stat().st_size) for s in sib]
    fixture_glob_hits = [s for s in sib if '.tmp' in s or 'partial' in s or '.part' in s]
    print('FSYNCKILL killed_after_fsync=%s out_exists=%s siblings=%s fixture_glob_would_catch=%s'
          % (killed, out.exists(), resid, fixture_glob_hits))
    return {'killed': killed, 'out': out.exists(), 'siblings': resid, 'glob': fixture_glob_hits}


def probe_cmd_writes_out(mode, work):
    """(d) wrapped command writes to the receipt path itself (foreground + late)."""
    r = build_repo(work / 'd')
    repo, rev, instr = r['repo'], r['rev'], r['instr']
    res = {}
    # d1: foreground write to OUT during the command
    out = work / 'd' / 'fg.txt'
    out.parent.mkdir(exist_ok=True)
    cmd = ['bash', '-c', 'printf FORGED-FG > "$S60_OUT"; echo ran']
    env = dict(os.environ, S60_OUT=str(out))
    args = tool_args(mode, repo, rev, instr, out, cmd)
    p = subprocess.run(args, capture_output=True, env=env, timeout=60)
    body = out.read_bytes() if out.exists() else b''
    res['d1-foreground'] = 'rc=%d final_head=%r forged_survives=%s' % (
        p.returncode, body[:20], body.startswith(b'FORGED-FG'))
    # d2: background child writes OUT after the writer exits (survives pipe EOF)
    out = work / 'd' / 'late.txt'
    cmd = ['bash', '-c',
           '( exec >/dev/null 2>&1; until [ -f "$S60_OUT" ]; do sleep 0.05; done; '
           'printf FORGED-LATE > "$S60_OUT" ) & echo ran']
    env2 = dict(os.environ, S60_OUT=str(out))
    p = subprocess.run(tool_args(mode, repo, rev, instr, out, cmd),
                       capture_output=True, env=env2, timeout=60)
    body_after = out.read_bytes() if out.exists() else b''
    time.sleep(1.6)
    body_late = out.read_bytes() if out.exists() else b''
    res['d2-late'] = 'rc=%d right_after_head=%r after_1.6s_head=%r tampered=%s' % (
        p.returncode, body_after[:20], body_late[:20], body_late.startswith(b'FORGED-LATE'))
    for k, v in res.items():
        print(k, v)
    return res


def probe_bound(mode, work):
    """(e) bound bypass: single huge line, non-UTF8 stream, NUL bytes, stderr-only."""
    r = build_repo(work / 'e')
    repo, rev, instr = r['repo'], r['rev'], r['instr']
    res = {}
    extra = ['--max-bytes', '65536'] if mode == 'cand' else []

    def run_case(name, cmd, use_extra=True):
        out = work / 'e' / (name + '.txt')
        out.parent.mkdir(exist_ok=True)
        p = run_tool(mode, repo, rev, instr, out, cmd, extra=(extra if use_extra else ()))
        body = out.read_bytes() if out.exists() else b''
        res[name] = 'rc=%d out=%d head=%r tail=%r siblings=%s' % (
            p.returncode, len(body), body[:24], body[-24:], siblings(out))

    run_case('e1-huge-line', ['bash', '-c', 'head -c 2097152 /dev/zero | tr "\\0" a'])
    run_case('e2-nonutf8', ['bash', '-c', 'head -c 2000 /dev/urandom | tr -d "\\n"'])
    run_case('e3-nul-bytes', ['bash', '-c', 'printf "a\\x00b\\x00c"'])
    run_case('e4-boundary', ['bash', '-c', 'head -c 65536 /dev/zero | tr "\\0" b'])
    run_case('e5-stderr-only', ['bash', '-c', 'head -c 2097152 /dev/zero | tr "\\0" c >&2'])
    for k, v in res.items():
        print(k, v)
    return res


def probe_dirty(mode, work):
    """(f) dirty-tree guard bypass: ignored file, staged-only, TOCTOU touch,
    non-repo root, GIT_* env hijack, --allow-dirty."""
    r = build_repo(work / 'f')
    repo, rev, instr = r['repo'], r['rev'], r['instr']
    res = {}

    def run_case(name, repo_p, env_extra=None, cmd=('echo', 'x'), extra=()):
        out = work / 'f' / (name + '.txt')
        out.parent.mkdir(exist_ok=True)
        p = run_tool(mode, repo_p, rev, instr, out, list(cmd), extra=extra, env_extra=env_extra)
        res[name] = 'rc=%d out_exists=%s' % (p.returncode, out.exists())

    # f1 ignored file
    (repo / '.gitignore').write_text('ignored*\n')
    git(repo, 'add', '.gitignore')
    git(repo, 'commit', '-q', '-m', 'gitignore')
    rev2 = git(repo, 'rev-parse', 'HEAD').stdout.decode().strip()
    (repo / 'ignored-artifact.bin').write_text('x')
    st = git(repo, 'status', '--porcelain').stdout.decode()
    run_case('f1-ignored', repo)
    res['f1-porcelain'] = repr(st)
    # f2 staged-only change
    (repo / 'staged.txt').write_text('staged\n')
    git(repo, 'add', 'staged.txt')
    st = git(repo, 'status', '--porcelain').stdout.decode()
    run_case('f2-staged', repo)
    res['f2-porcelain'] = repr(st)
    git(repo, 'reset', '-q')
    # f3 dirty-check TOCTOU: tracked file modified mid-command
    for stray in ('staged.txt', 'untracked.txt', 'untracked2.txt'):
        (repo / stray).unlink(missing_ok=True)
    git(repo, 'rm', '-q', '--cached', '--ignore-unmatch', 'staged.txt')
    out = work / 'f' / 'f3.txt'
    out.parent.mkdir(exist_ok=True)
    toucher = subprocess.Popen(['bash', '-c', 'sleep 0.5; printf tampered >> %s/tools/instrument.py' % repo],
                               start_new_session=True)
    p = run_tool(mode, repo, rev2, instr, out, ['bash', '-c', 'sleep 1.2; echo x'])
    toucher.wait()
    st = git(repo, 'status', '--porcelain').stdout.decode()
    res['f3-toctou'] = 'rc=%d out_exists=%s porcelain_after=%r' % (p.returncode, out.exists(), st)
    git(repo, 'checkout', '-q', '--', 'tools/instrument.py') if False else None
    # restore instrument without touching lane (fixture repo only)
    (repo / 'tools' / 'instrument.py').write_text('# fixture instrument v1\n')
    # f4 non-repo root
    nonrepo = work / 'f' / 'nonrepo'
    nonrepo.mkdir()
    run_case('f4-nonrepo', nonrepo)
    # f5 GIT_* env hijack: point every git call at a CLEAN CLONE of the fixture
    clean = work / 'f' / 'cleanclone'
    subprocess.run(['git', 'clone', '-q', str(repo), str(clean)], env=GITENV, check=True,
                   capture_output=True, timeout=60)
    st_clean = git(clean, 'status', '--porcelain').stdout.decode()
    run_case('f5-envhijack', repo,
             env_extra={'GIT_DIR': str(clean / '.git'), 'GIT_WORK_TREE': str(clean)})
    res['f5-clone-status'] = repr(st_clean)
    # f6 --allow-dirty sanity (candidate only)
    if mode == 'cand':
        out = work / 'f' / 'f6.txt'
        out.parent.mkdir(exist_ok=True)
        (repo / 'untracked2.txt').write_text('x')
        p = run_tool(mode, repo, rev2, instr, out, ['echo', 'x'], extra=['--allow-dirty'])
        res['f6-allowdirty'] = 'rc=%d out_exists=%s' % (p.returncode, out.exists())
    for k, v in res.items():
        print(k, v)
    return res


def probe_window(mode, work):
    """(g) case-3 poll-window blindness: a non-atomic-at-end stub passes case 3."""
    stub = work / 'g' / 'nonatomic-stub.py'
    stub.parent.mkdir(parents=True)
    stub.write_text('''#!/usr/bin/env python3
import os, sys, time
# deliberately NON-atomic: opens OUT with O_TRUNC after the command, writes in chunks
args = sys.argv[1:]
def val(f):
    return args[args.index(f) + 1]
root, rev, instr, out = val("--root"), val("--rev"), val("--instrument"), val("--out")
i = args.index("--"); cmd = args[i + 1:]
import subprocess, hashlib
p = subprocess.run(cmd, capture_output=True)
sha = subprocess.run(["git", "-C", root, "show", rev + ":" + instr], capture_output=True).stdout
time.sleep(0.2)
with open(out, "w") as f:                       # plain truncate-in-place write
    f.write("instrument=%s\\n" % instr)
    f.flush()
    time.sleep(0.6)                             # window: OUT exists, partial
    f.write("instrument_sha256=%s\\n" % hashlib.sha256(sha).hexdigest())
    f.write("rev=%s\\ncommand=%s\\n" % (rev, " ".join(cmd)))
    f.write("EXIT=%d\\n" % p.returncode)
sys.exit(p.returncode)
''')
    r = build_repo(work / 'g')
    repo, rev, instr = r['repo'], r['rev'], r['instr']
    out = work / 'g' / 'r.txt'
    out.parent.mkdir(exist_ok=True)
    p = subprocess.Popen(['python3', str(stub), '--root', str(repo), '--rev', rev,
                          '--instrument', instr, '--out', str(out), '--', 'bash', '-c', 'sleep 1; echo done'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    time.sleep(0.3)
    early = out.exists()
    p.wait(timeout=20)
    print('WINDOW stub_passes_case3_early_absent=%s (stub is non-atomic: partial OUT visible later in its write)' % (not early))
    # prove the stub is non-atomic: kill mid-write
    out2 = work / 'g' / 'r2.txt'
    p2 = subprocess.Popen(['python3', str(stub), '--root', str(repo), '--rev', rev,
                           '--instrument', instr, '--out', str(out2), '--', 'echo', 'fast'],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    time.sleep(0.45)            # inside the 0.6s partial-write sleep
    try:
        os.killpg(os.getpgid(p2.pid), signal.SIGKILL)
    except ProcessLookupError:
        pass
    p2.wait(timeout=20)
    body = out2.read_bytes() if out2.exists() else b''
    print('WINDOW kill-mid-write out_exists=%s partial_head=%r -> case-3 window cannot discriminate' % (
        out2.exists(), body[:30]))
    return {'early_absent': not early, 'partial': body[:30]}



def probe_revtype(mode, work):
    """Interop: revs the writer may accept that the r58 c2-gate REFUSES
    (annotated tag object OID -> RECEIPT-REV-ABSENT; jj-keep-only commit ->
    RECEIPT-REV-KEEP-ONLY), plus a committed-symlink instrument."""
    import zlib
    r = build_repo(work / 'r')
    repo, rev, instr, sha = r['repo'], r['rev'], r['instr'], r['sha']
    res = {}

    def attempt(name, use_rev, use_instr=None):
        out = work / 'r' / (name + '.txt')
        out.parent.mkdir(exist_ok=True)
        p = run_tool(mode, repo, use_rev, use_instr or instr, out, ['echo', 'x'])
        body = out.read_bytes() if out.exists() else b''
        res[name] = 'rc=%d out_exists=%s err=%r' % (p.returncode, out.exists(), p.stderr.decode()[:120])
        return p, body

    # annotated tag object as a loose object (no tag/update-ref mutation beyond refs/tags)
    tagbody = ('object %s\ntype commit\ntag vannot\ntagger fixture '
               '<fixture@example.invalid> 1793491200 +0000\n\nfixture tag\n' % rev).encode()
    tagobject = b'tag ' + str(len(tagbody)).encode() + b'\0' + tagbody
    tagoid = hashlib.sha1(tagobject).hexdigest()
    obj = repo / '.git' / 'objects' / tagoid[:2] / tagoid[2:]
    obj.parent.mkdir(parents=True, exist_ok=True)
    obj.write_bytes(zlib.compress(tagobject))
    (repo / '.git' / 'refs' / 'tags' / 'vannot').write_text(tagoid + '\n')
    attempt('rt-tagoid', tagoid)
    # keep-only commit
    (repo / 'tools' / 'instrument.py').write_text('# keep-only variant\n')
    git(repo, 'add', 'tools/instrument.py')
    git(repo, 'commit', '-q', '-m', 'keep-only')
    keep = git(repo, 'rev-parse', 'HEAD').stdout.decode().strip()
    kd = repo / '.git' / 'refs' / 'jj' / 'keep'
    kd.mkdir(parents=True, exist_ok=True)
    (kd / 'fixture').write_text(keep + '\n')
    (repo / '.git' / 'refs' / 'heads' / 'main').write_text(rev + '\n')
    attempt('rt-keeponly', keep)
    # committed symlink as instrument
    os.symlink('instrument.py', repo / 'tools' / 'instrument-link.py')
    git(repo, 'add', 'tools/instrument-link.py')
    git(repo, 'commit', '-q', '-m', 'symlink instrument')
    symrev = git(repo, 'rev-parse', 'HEAD').stdout.decode().strip()
    (repo / '.git' / 'refs' / 'heads' / 'main').write_text(symrev + '\n')
    attempt('rt-instrsymlink', symrev, 'tools/instrument-link.py')
    # absent rev (40 zeros)
    attempt('rt-absent', '0' * 40)
    for k, v in res.items():
        print(k, v)
    return res


PROBES = {'toctou': probe_toctou, 'outfs': probe_out_fs, 'fsynckill': probe_fsync_kill,
          'cmdwrites': probe_cmd_writes_out, 'bound': probe_bound, 'dirty': probe_dirty,
          'window': probe_window, 'revtype': probe_revtype}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode2', nargs='?')
    ap.add_argument('--tool', required=True)
    ap.add_argument('--mode', choices=['base', 'cand'], default='cand')
    ap.add_argument('--work', required=True)
    ap.add_argument('--probe')
    ns = ap.parse_args()
    TOOL[0] = ns.tool
    work = Path(ns.work)
    if ns.mode2 == 'eight' or ns.probe is None and ns.mode2 != 'all':
        case_eight(ns.mode, work)
        return
    if ns.probe:
        PROBES[ns.probe](ns.mode, work)
        return
    case_eight(ns.mode, work)
    for name in PROBES:
        print('--- probe', name)
        try:
            PROBES[name](ns.mode, work)
        except Exception as e:
            print('probe', name, 'ERROR', repr(e))


if __name__ == '__main__':
    main()
