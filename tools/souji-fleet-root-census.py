#!/usr/bin/env python3
"""souji-fleet-root-census.py — read-only top-level hygiene census of a fleet root (souji r52, C2).

Writes ONE capture file (O_EXCL, outside the root) listing the top-level entries of
the fleet root with a frozen class and disposition. Frozen format and class rule:
census/round-52/preregistration.txt (C2). Verified by census/round-52/c2-counter.py.

Never removes, moves, renames, chmods or writes inside the fleet root. Never reads file
contents, never follows symlinks (lstat only), never reads any process environ, never
sends signals, never enumerates below the top level.

Hardening (sentinel review, round 52, findings S1-S8):
  - every git call carries `-c core.fsmonitor=false -c core.hooksPath=/dev/null
    -c core.excludesFile=/dev/null` (command-line config overrides repo config) and the
    frozen GIT_* environment; git runs in its own session and the whole group is killed
    on timeout;
  - the repo config is read with --no-includes and the run is REFUSED if it carries an
    include/includeIf directive or core.worktree (either can make git read files outside
    the root or walk another tree);
  - the fleet root must be its own repository top-level (a subdirectory is refused);
  - the root must not lie inside a credential namespace (~/.omp, ~/.ssh, ~/.gnupg, ~/.aws,
    ~/.kube, ~/.docker, ~/.config/gh), and no top-level name may be credential-shaped:
    either refusal exits 2 with no capture (operator ruling required, L0);
  - --out must not resolve inside the fleet root;
  - ignored status is computed per TOP-LEVEL name with `git check-ignore --no-index`, so
    no ignored subtree is ever enumerated.

Exit: 0 written/selftest pass; 2 refused (nothing emitted); 1 selftest failure.
Usage:  souji-fleet-root-census.py --fleet-root DIR --out PATH
        souji-fleet-root-census.py --selftest
"""
import argparse, contextlib, hashlib, io, os, pwd, re, shutil, signal, stat, subprocess, sys, tempfile

PROG = 'souji-fleet-root-census'
LINE_TITLE = '# souji round-52 fleet-root census (read-only; dry-run)'
LINE_SCOPE = '# SCOPE=top-level entries of the fleet root, dotfiles included, .git excluded'
COLUMNS = 'name\tkind\ttracked\tignored\tclass\tdisposition'
HEX40 = re.compile(r'\A[0-9a-f]{40}\Z')

# Constructed, never inherited. PATH locates git; os.environ is never read.
GIT_ENV = {
    'PATH': '/usr/local/bin:/usr/bin:/bin',
    'LC_ALL': 'C',
    'GIT_OPTIONAL_LOCKS': '0',
    'GIT_CONFIG_NOSYSTEM': '1',
    'GIT_CONFIG_GLOBAL': os.devnull,
    'GIT_CONFIG_SYSTEM': os.devnull,
    'GIT_NO_REPLACE_OBJECTS': '1',
    'GIT_NO_LAZY_FETCH': '1',
}
# Command-line config overrides repository config: no fsmonitor/hook/global-excludes code runs.
HARDEN = ['-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=/dev/null',
          '-c', 'core.excludesFile=/dev/null']
GIT_TIMEOUT = 600
CRED_DIRS = ('.omp', '.ssh', '.gnupg', '.aws', '.kube', '.docker', '.config/gh')
CRED_NAME = re.compile(
    r'(?i)(\A\.env(\Z|\.)|\bcreds?\b|credential|secret|password|token|\.pem\Z|\.key\Z|\.p12\Z|\.pfx\Z'
    r'|\.kdbx\Z|\Aid_(rsa|dsa|ecdsa|ed25519)|\A\.(ssh|gnupg|aws|netrc|kube|docker)\Z)')


class Refused(Exception):
    """A refusal: exit 2, nothing emitted."""


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #

def _b(name):
    """Name -> bytes, round-tripping surrogate-escaped (non-UTF-8) names."""
    return name.encode('utf-8', 'surrogateescape')


def _split0(blob):
    return [part for part in blob.split(b'\0') if part]


def _run_git(root, args, data=None, ok=(0,)):
    argv = ['git', '-C', root] + HARDEN + list(args)
    try:
        proc = subprocess.Popen(argv, env=GIT_ENV, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                start_new_session=True)
    except OSError as exc:
        raise Refused('git unusable at %s: %s' % (root, exc))
    try:
        out, err = proc.communicate(data, timeout=GIT_TIMEOUT)
    except subprocess.TimeoutExpired:
        with contextlib.suppress(OSError):
            os.killpg(proc.pid, signal.SIGKILL)
        proc.communicate()
        raise Refused('git %s timed out at %s' % (' '.join(args), root))
    if proc.returncode not in ok:
        detail = ' '.join(err.decode('utf-8', 'replace').split())
        raise Refused('git %s failed at %s (rc=%d): %s'
                      % (' '.join(args), root, proc.returncode, detail[:200]))
    return proc.returncode, out


def git(root, *args):
    return _run_git(root, args)[1]


def self_sha256():
    """sha256 of this script's own bytes, read at runtime."""
    with open(__file__, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def kind_of(mode):
    if stat.S_ISLNK(mode):
        return 'symlink'
    if stat.S_ISDIR(mode):
        return 'dir'
    if stat.S_ISREG(mode):
        return 'file'
    return 'other'


def home_dir():
    """The account's home from the passwd database (environ is never read)."""
    return pwd.getpwuid(os.getuid()).pw_dir


def protected_root_reason(real_root, home):
    """Refusal text if real_root lies inside a credential namespace under home, else None."""
    for rel in CRED_DIRS:
        base = os.path.realpath(os.path.join(home, rel))
        if real_root == base or real_root.startswith(base + os.sep):
            return 'fleet-root lies inside a credential namespace (%s)' % rel
    return None


def scan_top_level(root):
    """[(name, kind)] for top-level entries; dotfiles included, .git excluded."""
    entries = []
    try:
        with os.scandir(root) as it:
            for entry in it:
                if entry.name == '.git':
                    continue
                st = entry.stat(follow_symlinks=False)   # lstat: never follow
                entries.append((entry.name, kind_of(st.st_mode)))
    except OSError as exc:
        raise Refused('cannot enumerate %s: %s' % (root, exc))
    return entries


def check_repo_config(root):
    """Refuse a repository config that can make git read outside the root or walk another tree."""
    _rc, out = _run_git(root, ('config', '--local', '--no-includes', '--list', '-z'), ok=(0, 1))
    for entry in _split0(out):
        key = entry.split(b'\n', 1)[0].lower()
        if key.startswith(b'include.') or key.startswith(b'includeif.'):
            raise Refused('repository config carries %s: git would read files outside the root'
                          % key.decode('utf-8', 'replace'))
        if key == b'core.worktree':
            raise Refused('repository config sets core.worktree: the census would walk another tree')


def tracked_first_components(root):
    """First '/'-component of every path `ls-files --cached` reports (index read only)."""
    return {p.split(b'/')[0] for p in _split0(git(root, 'ls-files', '-z', '--cached'))}


def ignored_among(root, names):
    """Subset of the given top-level names that exclude rules ignore (untracked-or-not;
    the frozen class rule checks tracked first). Never expands a directory."""
    if not names:
        return set()
    _rc, out = _run_git(root, ('check-ignore', '--no-index', '-z', '--stdin'),
                        data=b'\0'.join(names) + b'\0', ok=(0, 1))
    return set(_split0(out))


def frozen_class(kind, tracked, ignored):
    """Frozen rule, first match wins."""
    if kind == 'symlink':
        return 'symlink'
    if tracked == 'yes':
        return 'tracked'
    if ignored == 'yes':
        return 'ignored'
    return 'untracked-stray'


def frozen_disposition(cls):
    return 'report-only' if cls == 'untracked-stray' else 'none'


# --------------------------------------------------------------------------- #
# capture construction
# --------------------------------------------------------------------------- #

def build(root, home=None):
    """Return (capture_bytes, counts, entries).  Raises Refused."""
    root = os.path.abspath(root)
    if os.path.islink(root):
        raise Refused('fleet-root is a symlink: %s' % root)
    if not os.path.isdir(root):
        raise Refused('fleet-root is not a directory: %s' % root)
    real_root = os.path.realpath(root)

    reason = protected_root_reason(real_root, home or home_dir())
    if reason:
        raise Refused(reason)

    toplevel = git(real_root, 'rev-parse', '--show-toplevel').decode('utf-8', 'replace').strip()
    if os.path.realpath(toplevel) != real_root:
        raise Refused('fleet-root is not its own repository top-level (top-level %s)' % toplevel)
    head = git(real_root, 'rev-parse', 'HEAD').decode('ascii', 'replace').strip()
    if not HEX40.match(head):
        raise Refused('git unusable at %s: HEAD is not a 40-hex commit (%r)' % (root, head))
    check_repo_config(real_root)

    entries = scan_top_level(real_root)
    for name, _kind in entries:
        if CRED_NAME.search(name):
            raise Refused('credential-shaped top-level name %r: no capture emitted; '
                          'operator ruling required' % name)

    tracked = tracked_first_components(real_root)
    ignored = ignored_among(real_root, [_b(name) for name, _k in entries])

    rows, counts = [], {'tracked': 0, 'ignored': 0, 'untracked-stray': 0, 'symlink': 0}
    for name, kind in entries:
        nb = _b(name)
        tstate = 'yes' if nb in tracked else 'no'
        istate = 'yes' if nb in ignored else 'no'
        cls = frozen_class(kind, tstate, istate)
        counts[cls] += 1
        rows.append((nb, kind, tstate, istate, cls, frozen_disposition(cls)))

    for nb, *_rest in rows:
        if b'\t' in nb or b'\n' in nb:
            raise Refused('entry name contains a tab or newline: %r' % nb)
    rows.sort(key=lambda row: row[0])

    lines = [
        LINE_TITLE.encode('ascii'),
        LINE_SCOPE.encode('ascii'),
        b'# TOOL_SHA256=' + self_sha256().encode('ascii'),
        b'# FLEET_HEAD=' + head.encode('ascii'),
        b'# ENTRIES=%d' % len(rows),
        b'# COUNT tracked=%d' % counts['tracked'],
        b'# COUNT ignored=%d' % counts['ignored'],
        b'# COUNT untracked-stray=%d' % counts['untracked-stray'],
        b'# COUNT symlink=%d' % counts['symlink'],
        COLUMNS.encode('ascii'),
    ]
    for nb, kind, tstate, istate, cls, disp in rows:
        lines.append(b'\t'.join((nb, kind.encode('ascii'), tstate.encode('ascii'),
                                 istate.encode('ascii'), cls.encode('ascii'),
                                 disp.encode('ascii'))))
    return b'\n'.join(lines) + b'\n', counts, len(rows)


def capture(root, out, home=None):
    """Write the census of `root` to `out` (O_EXCL).  Returns a process exit code."""
    if os.path.lexists(out):
        sys.stderr.write('%s: REFUSED --out already exists: %s\n' % (PROG, out))
        return 2
    try:
        out_real_parent = os.path.realpath(os.path.dirname(os.path.abspath(out)))
        real_root = os.path.realpath(os.path.abspath(root))
        if out_real_parent == real_root or out_real_parent.startswith(real_root + os.sep):
            raise Refused('--out resolves inside the fleet-root: %s' % out)
        data, counts, n = build(root, home)
    except Refused as exc:
        sys.stderr.write('%s: REFUSED %s\n' % (PROG, exc))
        return 2

    try:
        fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        sys.stderr.write('%s: REFUSED --out already exists: %s\n' % (PROG, out))
        return 2
    except OSError as exc:
        sys.stderr.write('%s: REFUSED cannot create --out %s: %s\n' % (PROG, out, exc))
        return 2

    try:
        with os.fdopen(fd, 'wb') as fh:
            fh.write(data)
    except OSError as exc:
        with contextlib.suppress(OSError):
            os.unlink(out)               # our own O_EXCL file, never a pre-existing one
        sys.stderr.write('%s: REFUSED cannot write --out %s: %s\n' % (PROG, out, exc))
        return 2

    sys.stdout.write('CENSUS ENTRIES=%d tracked=%d ignored=%d untracked-stray=%d '
                     'symlink=%d out=%s\n'
                     % (n, counts['tracked'], counts['ignored'],
                        counts['untracked-stray'], counts['symlink'], out))
    return 0


# --------------------------------------------------------------------------- #
# selftest
# --------------------------------------------------------------------------- #

def parse_capture(path):
    """Return (kv, counts, header_row, rows) from a written capture file."""
    with open(path, 'rb') as fh:
        raw = fh.read().decode('utf-8', 'replace')
    lines = raw.split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    kv, counts, rows, header = {}, {}, [], None
    for line in lines:
        if line.startswith('#'):
            m = re.fullmatch(r'# (TOOL_SHA256|FLEET_HEAD|ENTRIES)=(\S+)', line)
            if m:
                kv[m.group(1)] = m.group(2)
                continue
            m = re.fullmatch(r'# COUNT (\S+)=(\d+)', line)
            if m:
                counts[m.group(1)] = int(m.group(2))
            continue
        if header is None:
            header = line
            continue
        rows.append(line.split('\t'))
    return kv, counts, header, rows


def selftest():
    failures = []
    checks = 0
    base = None

    def check(cond, msg):
        nonlocal checks
        checks += 1
        print('SELFTEST %s %s' % ('ok  ' if cond else 'FAIL', msg))
        if not cond:
            failures.append(msg)

    def refused_reason(root, needle, home=None):
        try:
            build(root, home)
        except Refused as exc:
            return needle in str(exc)
        return False

    def quiet_capture(root, out, home=None):
        err, outbuf = io.StringIO(), io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(outbuf):
            rc = capture(root, out, home)
        return rc, err.getvalue()

    try:
        base = tempfile.mkdtemp(prefix='souji-r52-census-selftest-')
        root = os.path.join(base, 'root')
        os.makedirs(root)
        fake_home = os.path.join(base, 'home')
        os.makedirs(os.path.join(fake_home, '.omp', 'agent'))

        # --- fixture: the tracked set is created before the commit -----------
        with open(os.path.join(root, '.gitignore'), 'w', encoding='utf-8') as fh:
            fh.write('ignored-entry/\n')
        with open(os.path.join(root, 'tracked-file.txt'), 'w', encoding='utf-8') as fh:
            fh.write('tracked\n')
        os.makedirs(os.path.join(root, 'tracked-dir'))
        with open(os.path.join(root, 'tracked-dir', 'inner.txt'), 'w', encoding='utf-8') as fh:
            fh.write('tracked in a tracked dir\n')

        git(root, 'init', '-q')
        toplevel = git(root, 'rev-parse', '--show-toplevel').decode('utf-8', 'replace').strip()
        check(os.path.realpath(toplevel) == os.path.realpath(root),
              'fixture rev-parse --show-toplevel is the fixture root')
        ident = ('-c', 'user.name=fixture', '-c', 'user.email=fixture@local',
                 '-c', 'commit.gpgsign=false')
        git(root, *(ident + ('add', '-A')))
        git(root, *(ident + ('commit', '-q', '-m', 'fixture')))

        # --- fixture: the untracked / ignored / symlink set -------------------
        os.makedirs(os.path.join(root, 'ignored-entry'))
        with open(os.path.join(root, 'ignored-entry', 'inside.txt'), 'w', encoding='utf-8') as fh:
            fh.write('ignored by .gitignore\n')
        with open(os.path.join(root, 'stray-file.txt'), 'w', encoding='utf-8') as fh:
            fh.write('stray\n')
        os.makedirs(os.path.join(root, 'stray-dir'))
        with open(os.path.join(root, 'stray-dir', 'with.txt'), 'w', encoding='utf-8') as fh:
            fh.write('stray dir content\n')
        os.symlink('tracked-file.txt', os.path.join(root, 'link-to-file'))
        with open(os.path.join(root, '.stray-dotfile'), 'w', encoding='utf-8') as fh:
            fh.write('stray dotfile\n')
        with open(os.path.join(root, 'name with space.txt'), 'w', encoding='utf-8') as fh:
            fh.write('stray name with a space\n')

        expected = {
            '.gitignore': ('file', 'yes', 'no', 'tracked', 'none'),
            '.stray-dotfile': ('file', 'no', 'no', 'untracked-stray', 'report-only'),
            'ignored-entry': ('dir', 'no', 'yes', 'ignored', 'none'),
            'link-to-file': ('symlink', 'no', 'no', 'symlink', 'none'),
            'name with space.txt': ('file', 'no', 'no', 'untracked-stray', 'report-only'),
            'stray-dir': ('dir', 'no', 'no', 'untracked-stray', 'report-only'),
            'stray-file.txt': ('file', 'no', 'no', 'untracked-stray', 'report-only'),
            'tracked-dir': ('dir', 'yes', 'no', 'tracked', 'none'),
            'tracked-file.txt': ('file', 'yes', 'no', 'tracked', 'none'),
        }

        out = os.path.join(base, 'capture.tsv')
        rc, errtext = quiet_capture(root, out, fake_home)
        check(rc == 0, 'capture on the synthetic root exits 0 (rc=%d %r)' % (rc, errtext.strip()))
        if rc != 0:
            raise SystemExit(1)

        with open(out, 'rb') as fh:
            lines = fh.read().decode('utf-8', 'replace').split('\n')
        check(lines[0] == LINE_TITLE, 'first line is the frozen title')
        check(lines[1] == LINE_SCOPE, 'second line is the frozen SCOPE')

        kv, counts, header, rows = parse_capture(out)
        check(header == COLUMNS, 'column header is name/kind/tracked/ignored/class/disposition')
        check(kv.get('TOOL_SHA256') == self_sha256(),
              'TOOL_SHA256 equals sha256(open(__file__,"rb"))')
        head = git(root, 'rev-parse', 'HEAD').decode('ascii').strip()
        check(kv.get('FLEET_HEAD') == head and bool(HEX40.match(kv.get('FLEET_HEAD', ''))),
              'FLEET_HEAD is 40-hex and equals the fixture HEAD')
        check(kv.get('ENTRIES') == str(len(expected)) == str(len(rows)),
              'ENTRIES=%d equals the row count' % len(expected))

        got = {row[0]: tuple(row[1:]) for row in rows}
        for name in sorted(expected, key=_b):
            check(got.get(name) == expected[name],
                  'row %r is %r (got %r)' % (name, expected[name], got.get(name)))
        check(set(got) == set(expected), 'no extra or missing rows')
        check(len({row[0] for row in rows}) == len(rows), 'names are unique')
        check([row[0] for row in rows] == sorted((row[0] for row in rows), key=_b),
              'rows are sorted by name in byte order')
        check(all(row[5] == 'report-only' for row in rows if row[4] == 'untracked-stray'),
              'untracked-stray rows carry disposition report-only')
        check(all(row[5] == 'none' for row in rows if row[4] != 'untracked-stray'),
              'non-untracked-stray rows carry disposition none')
        check(not any(row[5] in ('remove', 'delete', 'quarantine') for row in rows),
              'no row proposes removal')
        check(counts == {'tracked': 3, 'ignored': 1, 'untracked-stray': 4, 'symlink': 1},
              'COUNT lines are tracked=3 ignored=1 untracked-stray=4 symlink=1 (got %r)' % (counts,))

        # --- S1: repo-local fsmonitor is never executed ------------------------
        marker = os.path.join(base, 'fsm-marker')
        hook = os.path.join(base, 'fsm-hook.sh')
        with open(hook, 'w', encoding='utf-8') as fh:
            fh.write('#!/bin/sh\necho executed > %s\nprintf "\\0"\n' % marker)
        os.chmod(hook, 0o755)
        git(root, 'config', 'core.fsmonitor', hook)
        out_fsm = os.path.join(base, 'capture-fsm.tsv')
        rc_fsm, _ = quiet_capture(root, out_fsm, fake_home)
        check(rc_fsm == 0 and not os.path.exists(marker),
              'S1 repo-local core.fsmonitor is not executed by the census (rc=%d marker=%s)'
              % (rc_fsm, os.path.exists(marker)))
        git(root, 'config', '--unset', 'core.fsmonitor')

        # --- S2: repo-local include is refused --------------------------------
        secret = os.path.join(base, 'outside-secret.cfg')
        with open(secret, 'w', encoding='utf-8') as fh:
            fh.write('[x]\n\tmarker = outside\n')
        git(root, 'config', 'include.path', secret)
        check(refused_reason(root, 'include', fake_home),
              'S2 a repo config carrying include.path is refused')
        git(root, 'config', '--unset', 'include.path')

        # --- S3: credential-shaped names and credential namespaces are refused -
        cred = os.path.join(base, 'cred-root')
        os.makedirs(cred)
        git(cred, 'init', '-q')
        git(cred, *(ident + ('commit', '-q', '--allow-empty', '-m', 'fixture')))
        with open(os.path.join(cred, 'creds.json'), 'w', encoding='utf-8') as fh:
            fh.write('{}\n')
        check(refused_reason(cred, 'credential-shaped', fake_home),
              'S3 a credential-shaped top-level name (creds.json) is refused')
        cred_home_root = os.path.join(fake_home, '.omp', 'agent', 'repo')
        os.makedirs(cred_home_root)
        git(cred_home_root, 'init', '-q')
        git(cred_home_root, *(ident + ('commit', '-q', '--allow-empty', '-m', 'fixture')))
        check(refused_reason(cred_home_root, 'credential namespace', fake_home),
              'S3 a fleet-root inside ~/.omp is refused as a credential namespace')

        # --- S7: --out inside the root is refused -----------------------------
        out_inside = os.path.join(root, 'capture-inside.tsv')
        rc7, _ = quiet_capture(root, out_inside, fake_home)
        check(rc7 == 2 and not os.path.lexists(out_inside),
              'S7 --out inside the fleet-root: exit 2 and nothing created')

        # --- S8: a subdirectory of a repo is refused --------------------------
        sub = os.path.join(root, 'tracked-dir')
        check(refused_reason(sub, 'not its own repository top-level', fake_home),
              'S8 a repo subdirectory is refused as not its own top-level')

        # --- refusals (carried from r52 fixture) ------------------------------
        rc2, _ = quiet_capture(root, out, fake_home)
        check(rc2 == 2, 'a second capture at the same --out is refused with exit 2')
        link_root = os.path.join(base, 'link-root')
        os.symlink(root, link_root)
        check(refused_reason(link_root, 'is a symlink', fake_home),
              'a symlink fleet-root is refused as a symlink')
        out_link = os.path.join(base, 'capture-link.tsv')
        rc3, _ = quiet_capture(link_root, out_link, fake_home)
        check(rc3 == 2 and not os.path.lexists(out_link),
              'symlink fleet-root: exit 2 and no --out created')
        notdir = os.path.join(base, 'not-a-dir')
        with open(notdir, 'w', encoding='utf-8') as fh:
            fh.write('not a directory\n')
        check(refused_reason(notdir, 'not a directory', fake_home),
              'a non-directory fleet-root is refused as not a directory')
        norepo = os.path.join(base, 'not-a-repo')
        os.makedirs(norepo)
        out_nr = os.path.join(base, 'capture-norepo.tsv')
        rc5, _ = quiet_capture(norepo, out_nr, fake_home)
        check(rc5 == 2 and not os.path.lexists(out_nr),
              'a non-repo fleet-root is refused (git unusable): exit 2, no --out')
        for label, bad in (('tab', 'bad\tname'), ('newline', 'bad\nname')):
            badroot = os.path.join(base, 'bad-' + label)
            os.makedirs(badroot)
            git(badroot, 'init', '-q')
            git(badroot, *(ident + ('commit', '-q', '--allow-empty', '-m', 'fixture')))
            with open(os.path.join(badroot, bad), 'w', encoding='utf-8') as fh:
                fh.write('x\n')
            check(refused_reason(badroot, 'tab or newline', fake_home),
                  'an entry name containing a %s is refused for that reason' % label)
            out_bad = os.path.join(base, 'capture-bad-%s.tsv' % label)
            rc6, _ = quiet_capture(badroot, out_bad, fake_home)
            check(rc6 == 2 and not os.path.lexists(out_bad),
                  'entry name with a %s: exit 2 and no --out created' % label)

        print('SUMMARY selftest checks=%d failures=%d verdict=%s'
              % (checks, len(failures), 'PASS' if not failures else 'FAIL'))
        return 0 if not failures else 1
    finally:
        if base is not None:
            shutil.rmtree(base, ignore_errors=True)
            print('SELFTEST cleanup synthetic root removed: %s' % base)


# --------------------------------------------------------------------------- #
# entry point
# --------------------------------------------------------------------------- #

def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    parser = argparse.ArgumentParser(
        prog=PROG,
        description='read-only top-level hygiene census of a fleet root')
    parser.add_argument('--fleet-root', metavar='DIR')
    parser.add_argument('--out', metavar='PATH')
    parser.add_argument('--selftest', action='store_true')
    ns = parser.parse_args(argv)

    if ns.selftest:
        if ns.fleet_root or ns.out:
            parser.error('--selftest takes no other arguments')
        return selftest()
    if not ns.fleet_root or not ns.out:
        parser.error('--fleet-root DIR and --out PATH are required')
    return capture(ns.fleet_root, ns.out)


if __name__ == '__main__':
    sys.exit(main())
