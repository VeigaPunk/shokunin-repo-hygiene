#!/usr/bin/env python3
"""Attack probes a..g + interop, run against a tool path. Every fixture is a fresh
`git init` repo under --work; every git call names -C <repo>; toplevel asserted."""
import argparse, hashlib, os, signal, subprocess, sys, time, zlib, glob
from pathlib import Path

ENV = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LC_ALL': 'C', 'GIT_CONFIG_NOSYSTEM': '1',
       'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_AUTHOR_NAME': 'fixture', 'GIT_AUTHOR_EMAIL': 'f@example.invalid',
       'GIT_COMMITTER_NAME': 'fixture', 'GIT_COMMITTER_EMAIL': 'f@example.invalid',
       'GIT_AUTHOR_DATE': '2026-11-01T00:00:00+0000', 'GIT_COMMITTER_DATE': '2026-11-01T00:00:00+0000'}
TOOL = None
RESULTS = []


def say(tag, msg):
    line = '%s %s' % (tag, msg)
    RESULTS.append(line)
    print(line, flush=True)


def git(repo, *a, check=True):
    p = subprocess.run(['git', '-C', str(repo)] + list(a), capture_output=True, env=ENV, timeout=60)
    if check and p.returncode:
        raise SystemExit('fixture git failed %r: %s' % (a, p.stderr.decode()))
    return p


def fresh(work: Path, name: str):
    d = work / name
    d.mkdir(parents=True)
    git(d, 'init', '-q', '-b', 'main')
    top = git(d, 'rev-parse', '--show-toplevel').stdout.decode().strip()
    assert os.path.realpath(top) == os.path.realpath(d), 'toplevel %r != %r' % (top, d)
    (d / 'tools').mkdir()
    (d / 'tools' / 'instrument.py').write_text('# fixture instrument v1\n')
    git(d, 'add', 'tools/instrument.py')
    git(d, 'commit', '-q', '-m', 'base')
    rev = git(d, 'rev-parse', 'HEAD').stdout.decode().strip()
    os.chdir(str(d))  # wrapped commands run inside the fixture repo
    return d, rev, hashlib.sha256((d / 'tools' / 'instrument.py').read_bytes()).hexdigest()


def tool_cmd(repo, rev, out, cmd, extra=()):
    if str(TOOL).endswith('.sh'):  # base recorder: positional <lane> <rev> <instr> <out> -- cmd
        return ['bash', str(TOOL), str(repo), rev, 'tools/instrument.py', str(out), '--'] + list(cmd)
    return (['python3', str(TOOL), '--root', str(repo), '--rev', rev, '--instrument', 'tools/instrument.py',
             '--out', str(out)] + list(extra) + ['--'] + list(cmd))


def sibs(out: Path):
    return sorted(x.name for x in out.parent.iterdir() if x.name != out.name)


def compile_so(work, name, code):
    c = work / (name + '.c')
    c.write_text(code)
    so = work / (name + '.so')
    subprocess.run(['gcc', '-shared', '-fPIC', '-O1', '-o', str(so), str(c), '-ldl'],
                   check=True, capture_output=True)
    return so


# ---- a: TOCTOU -------------------------------------------------------------
def atk_a(work):
    repo, rev, _ = fresh(work, 'a1')
    out = work / 'a1-out' / 'r.txt'
    out.parent.mkdir()
    # a1: command itself creates OUT AFTER the up-front existence check
    cmd = ['bash', '-c', 'printf RACER-FILE > "$S60_OUT"; echo ran']
    p = subprocess.run(tool_cmd(repo, rev, out, cmd), capture_output=True,
                       env=dict(os.environ, S60_OUT=str(out)), timeout=60)
    body = out.read_bytes() if out.exists() else b''
    say('ATK a1-cmd-created-out', 'rc=%d receipt_replaced_racer=%s head=%r' %
        (p.returncode, body.startswith(b'instrument='), body[:20]))
    # a2: external racer creates OUT in the gap between check and os.replace
    repo, rev, _ = fresh(work, 'a2')
    out = work / 'a2-out' / 'r.txt'
    out.parent.mkdir()
    racer = subprocess.Popen(
        ['bash', '-c', 'for i in $(seq 1 400); do f=$(ls -d "%s"/*r.txt*.tmp 2>/dev/null | head -1); '
         'if [ -n "$f" ]; then printf RACER > "%s"; exit 0; fi; sleep 0.005; done' % (out.parent, out)],
        start_new_session=True)
    p = subprocess.run(tool_cmd(repo, rev, out, ['bash', '-c', 'sleep 0.5; echo ok']),
                       capture_output=True, timeout=60)
    racer.wait(timeout=10)
    body = out.read_bytes() if out.exists() else b''
    say('ATK a2-external-racer', 'rc=%d final_is_receipt=%s raced_bytes_lost=%s' %
        (p.returncode, body.startswith(b'instrument='), not body.startswith(b'RACER')))


# ---- b: OUT location --------------------------------------------------------
def atk_b(work):
    repo, rev, _ = fresh(work, 'b1')
    esc = work / 'b1-outside'
    esc.mkdir()
    link = work / 'b1-link'
    os.symlink(str(esc), link)
    out = link / 'r.txt'
    p = subprocess.run(tool_cmd(repo, rev, out, ['echo', 'x']), capture_output=True, timeout=60)
    say('ATK b1-symlink-dir', 'rc=%d wrote_outside_lane=%s' % (p.returncode, (esc / 'r.txt').exists()))
    # b2: OUT whose directory does not exist -> command runs before the failure
    repo, rev, _ = fresh(work, 'b2')
    marker = work / 'b2-ran.marker'
    out = work / 'b2-nodir' / 'r.txt'
    p = subprocess.run(tool_cmd(repo, rev, out, ['bash', '-c', 'touch "%s"; echo x' % marker]),
                       capture_output=True, timeout=60)
    say('ATK b2-missing-outdir', 'rc=%d command_side_effect_ran=%s stderr_tail=%r' %
        (p.returncode, marker.exists(), p.stderr.decode()[-80:]))
    # b3: OUT is a dangling symlink to a victim-free path (must be refused, not followed)
    repo, rev, _ = fresh(work, 'b3')
    out = work / 'b3' / 'r.txt'
    out.parent.mkdir(exist_ok=True)
    os.symlink(str(work / 'b3' / 'victim-absent.txt'), out)
    p = subprocess.run(tool_cmd(repo, rev, out, ['echo', 'x']), capture_output=True, timeout=60)
    say('ATK b3-dangling-symlink-out', 'rc=%d created_target=%s' %
        (p.returncode, (work / 'b3' / 'victim-absent.txt').exists()))


# ---- c: SIGKILL / SIGTERM between fsync and rename ------------------------
FSYNC_SHIM = r'''
#define _GNU_SOURCE
#include <stdlib.h>
#include <unistd.h>
#include <dlfcn.h>
static int (*rf)(int);
int fsync(int fd){ if(!rf) rf=dlsym(RTLD_NEXT,"fsync"); int r=rf(fd);
  const char*s=getenv("S60_SLEEP_AFTER_FSYNC"); if(s) sleep(atoi(s)); return r; }
int fdatasync(int fd){ return fsync(fd); }
'''


def atk_c(work):
    repo, rev, _ = fresh(work, 'c')
    so = compile_so(work, 'fsyncsleep', FSYNC_SHIM)
    for sig, name in ((signal.SIGKILL, 'c1-sigkill'), (signal.SIGTERM, 'c2-sigterm')):
        out = work / name / 'r.txt'
        out.parent.mkdir()
        env = dict(os.environ, LD_PRELOAD=str(so), S60_SLEEP_AFTER_FSYNC='6')
        p = subprocess.Popen(tool_cmd(repo, rev, out, ['echo', 'x']), stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, env=env, start_new_session=True)
        # wait until a temp sibling exists (fsync has run, rename has not)
        t0 = time.time()
        while time.time() - t0 < 15 and not sibs(out) and p.poll() is None:
            time.sleep(0.02)
        time.sleep(0.2)
        try:
            os.killpg(os.getpgid(p.pid), sig)
        except ProcessLookupError:
            pass
        p.wait(timeout=20)
        s = sibs(out)
        say('ATK c-%s' % name, 'signal=%s out_exists=%s residue=%s' % (sig.name, out.exists(), s))


# ---- d: command writes receipt path -----------------------------------------
def atk_d(work):
    repo, rev, _ = fresh(work, 'd1')
    out = work / 'd1-out' / 'r.txt'
    out.parent.mkdir()
    cmd = ['bash', '-c',
           '( exec >/dev/null 2>&1 </dev/null; until [ -f "$S60_OUT" ]; do sleep 0.02; done; '
           'printf FORGED-LATE > "$S60_OUT" ) & echo ran']
    p = subprocess.run(tool_cmd(repo, rev, out, cmd), capture_output=True,
                       env=dict(os.environ, S60_OUT=str(out)), timeout=60)
    time.sleep(0.8)
    body = out.read_bytes() if out.exists() else b''
    say('ATK d1-post-exit-forge', 'rc=%d receipt_tampered_after_exit=%s head=%r' %
        (p.returncode, body.startswith(b'FORGED'), body[:20]))


# ---- e: bound ----------------------------------------------------------------
def atk_e(work):
    repo, rev, _ = fresh(work, 'e1')
    out = work / 'e1-out' / 'r.txt'
    out.parent.mkdir()
    # single 1 MiB line, stdout only, default bound 262144 -> must refuse
    p = subprocess.run(tool_cmd(repo, rev, out, ['bash', '-c', 'head -c 1048576 /dev/zero | tr "\\0" a']),
                       capture_output=True, timeout=120)
    say('ATK e1-single-line-1MiB', 'rc=%d out_exists=%s' % (p.returncode, out.exists()))
    # non-UTF8 stream at exactly the bound boundary
    out = work / 'e2-out' / 'r.txt'
    out.parent.mkdir()
    p = subprocess.run(tool_cmd(repo, rev, out, ['bash', '-c', 'head -c 262144 /dev/urandom']),
                       capture_output=True, timeout=120)
    say('ATK e2-nonutf8-at-bound-262144', 'rc=%d out_exists=%s bytes=%d' %
        (p.returncode, out.exists(), out.stat().st_size if out.exists() else -1))
    # memory: 200 MiB stdout with bound 262144 -> refused, but how much was buffered?
    out = work / 'e3-out' / 'r.txt'
    out.parent.mkdir()
    import resource
    before = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    p = subprocess.run(tool_cmd(repo, rev, out, ['bash', '-c', 'head -c 209715200 /dev/zero']),
                       capture_output=True, timeout=300)
    after = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    say('ATK e3-200MiB-capture', 'rc=%d out_exists=%s child_maxrss_KiB_delta_peak=%d' %
        (p.returncode, out.exists(), after - before))


# ---- f: dirty-tree guard ------------------------------------------------------
def atk_f(work):
    repo, rev, _ = fresh(work, 'f1')
    # f1: ignored file that the command EXECUTES (not in receipt bytes)
    (repo / '.gitignore').write_text('tools/ign*.py\n')
    git(repo, 'add', '.gitignore')
    git(repo, 'commit', '-q', '-m', 'ignore')
    rev1 = git(repo, 'rev-parse', 'HEAD').stdout.decode().strip()
    (repo / 'tools' / 'ign_override.py').write_text('print("EXECUTED-UNTRACKED")\n')
    st = git(repo, 'status', '--porcelain').stdout.decode()
    out = work / 'f1-out' / 'r.txt'
    out.parent.mkdir()
    p = subprocess.run(tool_cmd(repo, rev1, out, ['python3', 'tools/ign_override.py']),
                       capture_output=True, timeout=60)
    body = out.read_bytes() if out.exists() else b''
    say('ATK f1-ignored-executed', 'rc=%d receipt=%s porcelain=%r receipt_says_executed=%s' %
        (p.returncode, out.exists(), st, b'EXECUTED-UNTRACKED' in body))
    # f2: tracked file modified DURING the command (guard checked only up front)
    repo, rev, _ = fresh(work, 'f2')
    out = work / 'f2-out' / 'r.txt'
    out.parent.mkdir()
    p = subprocess.run(tool_cmd(repo, rev, out, ['bash', '-c', 'printf "# tampered\\n" >> tools/instrument.py; echo x']),
                       capture_output=True, timeout=60)
    st = git(repo, 'status', '--porcelain').stdout.decode()
    say('ATK f2-modified-during-run', 'rc=%d receipt=%s porcelain_after=%r' %
        (p.returncode, out.exists(), st))
    # f3: env hijack with a dirty repo (GIT_DIR -> clean clone must NOT be trusted)
    repo, rev, _ = fresh(work, 'f3')
    (repo / 'dirty.txt').write_text('d\n')
    clone = work / 'f3-clone'
    subprocess.run(['git', 'clone', '-q', str(repo), str(clone)], env=ENV, check=True, capture_output=True)
    out = work / 'f3-out' / 'r.txt'
    out.parent.mkdir()
    p = subprocess.run(tool_cmd(repo, rev, out, ['echo', 'x']), capture_output=True,
                       env=dict(os.environ, GIT_DIR=str(clone / '.git'), GIT_WORK_TREE=str(clone)), timeout=60)
    say('ATK f3-env-hijack-dirty-repo', 'rc=%d receipt=%s (rc=2 expected: repo is dirty)' % (p.returncode, out.exists()))
    # f4: staged-only change
    repo, rev, _ = fresh(work, 'f4')
    (repo / 'staged.txt').write_text('s\n')
    git(repo, 'add', 'staged.txt')
    out = work / 'f4-out' / 'r.txt'
    out.parent.mkdir()
    p = subprocess.run(tool_cmd(repo, rev, out, ['echo', 'x']), capture_output=True, timeout=60)
    say('ATK f4-staged-only', 'rc=%d receipt=%s' % (p.returncode, out.exists()))


# ---- g: poll-window blindness (case 3) ------------------------------------------
def atk_g(work):
    stub = work / 'g-nonatomic.py'
    stub.write_text(r'''import os, sys, time, hashlib, subprocess
a = sys.argv[1:]
root, rev, instr, out = (a[a.index(k) + 1] for k in ("--root", "--rev", "--instrument", "--out"))
cmd = a[a.index("--") + 1:]
p = subprocess.run(cmd, capture_output=True)
sha = hashlib.sha256(subprocess.run(["git", "-C", root, "show", rev + ":" + instr], capture_output=True).stdout).hexdigest()
f = open(out, "w")                        # truncate-in-place, NOT atomic
f.write("instrument=%s\ninstrument_sha256=%s\nrev=%s\n" % (instr, sha, rev)); f.flush()
time.sleep(0.6)                           # partial OUT visible here
f.write("command=%s\n%sEXIT=%d\n" % (" ".join(cmd), p.stdout.decode(), p.returncode)); f.close()
sys.exit(p.returncode)
''')
    repo, rev, _ = fresh(work, 'g1')
    out = work / 'g1-out' / 'r.txt'
    out.parent.mkdir()
    # case-3 mechanics: command sleeps 1s, poll at 0.3s, check final last line
    p = subprocess.Popen(['python3', str(stub), '--root', str(repo), '--rev', rev, '--instrument',
                          'tools/instrument.py', '--out', str(out), '--', 'bash', '-c', 'sleep 1; echo done'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    time.sleep(0.3)
    early = out.exists()
    p.wait(timeout=20)
    final = out.read_bytes()
    say('ATK g1-case3-on-nonatomic-stub', 'early_absent=%s final_last_line_EXIT0=%s' %
        (not early, final.rstrip().endswith(b'EXIT=0')))
    # kill mid-write at 0.3s after the command: partial receipt readable -> non-atomic
    repo, rev, _ = fresh(work, 'g2')
    out = work / 'g2-out' / 'r.txt'
    out.parent.mkdir()
    p = subprocess.Popen(['python3', str(stub), '--root', str(repo), '--rev', rev, '--instrument',
                          'tools/instrument.py', '--out', str(out), '--', 'echo', 'fast'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    time.sleep(0.4)
    try:
        os.killpg(os.getpgid(p.pid), signal.SIGKILL)
    except ProcessLookupError:
        pass
    p.wait(timeout=20)
    say('ATK g2-kill-mid-write', 'out_exists=%s partial_is_readable=%r' %
        (out.exists(), out.read_bytes()[-40:] if out.exists() else None))


# ---- interop: r58 gate on receipts the writer accepts --------------------------
def atk_interop(work, gate):
    repo, rev, _ = fresh(work, 'i1')
    # annotated tag OID, loose object
    tagbody = ('object %s\ntype commit\ntag vannot\ntagger f <f@example.invalid> 1793491200 +0000\n\nt\n' % rev).encode()
    tagobj = b'tag ' + str(len(tagbody)).encode() + b'\0' + tagbody
    toid = hashlib.sha1(tagobj).hexdigest()
    o = repo / '.git' / 'objects' / toid[:2] / toid[2:]
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_bytes(zlib.compress(tagobj))
    out = work / 'i1-rcpt' / 'tag.txt'
    out.parent.mkdir()
    p = subprocess.run(tool_cmd(repo, toid, out, ['echo', 'x']), capture_output=True, timeout=60)
    say('ATK i1-tagoid-accepted', 'writer_rc=%d receipt=%s' % (p.returncode, out.exists()))
    if out.exists():
        rec = repo / 'receipts' / 'tag.txt'
        rec.parent.mkdir(exist_ok=True)
        rec.write_bytes(out.read_bytes())
        man = work / 'i1-manifest.tsv'
        man.write_text('receipt\tinstrument\nreceipts/tag.txt\ttools/instrument.py\n')
        g = subprocess.run(['python3', gate, '--root', str(repo), '--manifest', str(man)],
                           capture_output=True, timeout=120)
        say('ATK i1-r58-gate-on-tagoid-receipt', 'gate_rc=%d out=%r' % (g.returncode, g.stdout.decode()[:200]))


PROBES = {'a': atk_a, 'b': atk_b, 'c': atk_c, 'd': atk_d, 'e': atk_e, 'f': atk_f, 'g': atk_g}

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--tool', required=True)
    ap.add_argument('--work', required=True)
    ap.add_argument('--only', default=','.join(PROBES) + ',interop')
    ap.add_argument('--gate', default='/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-58/c2-gate.py')
    ns = ap.parse_args()
    TOOL = Path(ns.tool)
    work = Path(ns.work)
    for k in ns.only.split(','):
        if k == 'interop':
            atk_interop(work, ns.gate)
        else:
            PROBES[k](work)
