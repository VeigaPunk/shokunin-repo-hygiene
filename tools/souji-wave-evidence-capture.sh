#!/usr/bin/env bash
# souji-wave-evidence-capture.sh
#
# Capture a round's .ufo/waves evidence into a committable census receipt, so
# that the receipt verifies over COMMITTED bytes rather than over the lane disk
# (r28 closure routed defect 1).
#
#   bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N>
#   bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> --verify
#   bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> --verify --rev <full40>
#
# <lane-abs>  absolute path to the lane repo root
# <round-N>   integer round number
# --verify    re-verify an existing receipt against the disk copy (no copy)
# --rev H     with --verify: verify the receipt against the blobs of the tree
#             committed at revision H instead of the disk copy (git plumbing
#             only: ls-tree/cat-file; hashing in python3 because this host's
#             /usr/bin/sha256sum is uutils 0.8.0 and cannot parse GNU escaped
#             records)
#
# Copy rules (destination = <lane>/census/round-<N>/waves/, paths relative to
# the source wave dir, which is also the receipt-relative namespace):
#   regular file                 copied byte-exact
#   .gitignore / .gitattributes  (any depth, file or symlink) stored as
#                                "<same name>.captured" and recorded in
#                                renames.tsv, so copied rules can never make the
#                                receipt ignore itself; a stored-name collision
#                                is refused (exit 3)
#   symlink                      copied verbatim (never dereferenced) and
#                                recorded in symlinks.tsv with its exact target;
#                                symlinks carry no manifest record (a manifest
#                                record pointing at a symlink is a failure)
#   dest path git ignores        not copied; recorded in excluded.tsv with the
#                                sha256 of the source bytes and reason
#                                "ignored". The decision is
#                                `git -C <lane> check-ignore --no-index -q --
#                                <dest>` taken AFTER the receipt dir is cleared
#                                and nested rule files are renamed, i.e. with
#                                the source's own nested .gitignore rules
#                                neutralised; never `git add`. A lane that is
#                                not a git work tree gets no ignore rules
#                                (warning on stderr).
#   .git dir/file (any depth)    every path component named `.git` is stored as `.git.captured`
#                                (directories are recursed and their files copied byte-exact;
#                                a `.git` file or symlink is stored the same way) and each
#                                file/symlink row is recorded in renames.tsv, so a nested
#                                repository can never become a gitlink in the receipt and its
#                                bytes are preserved, not merely hashed
#   fifo/socket/device/other     refused (exit 3), never silently skipped
#
# Receipt files:
#   manifest.sha256 - GNU format ("<sha256>  ./<rel>", LC_ALL=C byte-sorted),
#                     covering every regular file in the receipt except
#                     manifest.sha256 itself: copied files, summary.tsv, and
#                     renames.tsv / excluded.tsv / symlinks.tsv when non-empty.
#                     Names containing a newline or backslash are written as
#                     GNU backslash-escaped records ("\<hash>  ./...\\n...").
#   summary.tsv     - header only (no results file present) or one TSV row per
#                     seat row from each <*-results.json> in the source.
#   renames.tsv     - header "# original<TAB>stored"; one row per renamed path.
#   excluded.tsv    - header "# path<TAB>sha256<TAB>reason"; one row per source
#                     path that is not in the receipt.
#   symlinks.tsv    - header "# path<TAB>target"; one row per copied symlink.
# The three accounting TSVs are written only when they have rows.
#
# Capture then re-verifies: the manifest is recomputed over the receipt and
# compared byte-for-byte, and the receipt's regular-file set is compared
# (name + sha256) against the expected set derived from the source, so a
# silently dropped or renamed file cannot pass. --verify does the manifest
# comparison only; --verify --rev does it against the committed tree.
#
# Source access is read-only; no git/jj mutation (check-ignore/ls-tree/cat-file
# only); never network.
#
# Exit codes:
#   0 captured + verified (or verified)
#   1 usage error / unrepresentable revision
#   2 source directory missing
#   3 refusal: special file / path escape / nested src-dst / name collision
#   4 verification failed (manifest mismatch, missing or uncovered record,
#     or receipt/source set mismatch)
#   5 copy / receipt write failure
set -u
set -o pipefail
export LC_ALL=C

usage() {
  printf '%s\n' \
    'Usage: bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> [--verify [--rev <full40>]]' \
    '  <lane-abs> absolute path to the lane repo root' \
    '  <round-N>  integer round number' \
    '  --verify   re-verify an existing receipt (no copy)' \
    '  --rev H    with --verify: verify against the tree committed at H'
}

if [[ $# -lt 2 ]]; then usage >&2; exit 1; fi
lane=$1
round=$2
shift 2
verify_only=0
rev=
while [[ $# -gt 0 ]]; do
  case $1 in
    --verify)
      [[ $verify_only -eq 0 ]] || { usage >&2; exit 1; }
      verify_only=1
      shift
      ;;
    --rev)
      [[ -n ${2-} && -z $rev ]] || { usage >&2; exit 1; }
      rev=$2
      shift 2
      ;;
    *)
      usage >&2
      exit 1
      ;;
  esac
done

case $round in
  ''|*[!0-9]*) usage >&2; exit 1 ;;
esac
if [[ $lane != /* ]]; then printf '%s\n' 'error: lane must be absolute' >&2; exit 1; fi
case /$lane in
  */../*|*/..) printf '%s\n' 'error: lane must not contain .. segments' >&2; exit 1 ;;
esac
if [[ -n $rev ]]; then
  [[ $verify_only -eq 1 ]] || { printf '%s\n' 'error: --rev requires --verify' >&2; exit 1; }
  case $rev in
    *[!0-9a-f]*) usage >&2; exit 1 ;;
  esac
  [[ ${#rev} -eq 40 ]] || { printf '%s\n' 'error: --rev must be a full 40-hex revision' >&2; exit 1; }
fi

python3 -B - "$lane" "$round" "$verify_only" "$rev" <<'PY'
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

RENAME_NAMES = ('.gitignore', '.gitattributes')
ACCOUNTING = ('summary.tsv', 'renames.tsv', 'excluded.tsv', 'symlinks.tsv')
MANIFEST = 'manifest.sha256'
REC = re.compile(rb'^([0-9a-f]{64})  (.*)$')


class Die(Exception):
    def __init__(self, code, msg):
        Exception.__init__(self, msg)
        self.code = code
        self.msg = msg


def die(code, msg):
    raise Die(code, msg)


def w(msg):
    print(msg, file=sys.stderr)


# ---- hashing ---------------------------------------------------------------

def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        while True:
            chunk = fh.read(1 << 20)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


# ---- git plumbing (read-only) ---------------------------------------------

def git_bytes(root, *args):
    p = subprocess.run(
        ['git', '-C', root, '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=/dev/null', *args],
        capture_output=True)
    if p.returncode != 0:
        die(4, 'could not evaluate git %s: %s' % (' '.join(args), p.stderr.decode('utf-8', 'replace').strip()))
    return p.stdout


def make_ignorer(lane):
    """Dest-path ignore predicate; False when the lane is not a git work tree."""
    p = subprocess.run(['git', '-C', lane, 'rev-parse', '--is-inside-work-tree'], capture_output=True)
    if p.returncode != 0 or p.stdout.strip() != b'true':
        w('warning: lane is not a git work tree; ignore rules not evaluated')
        return lambda destrel: False

    def ignored(destrel):
        q = subprocess.run(
            ['git', '-C', lane, '-c', 'core.fsmonitor=false', 'check-ignore', '--no-index', '-q', '--', destrel],
            capture_output=True)
        if q.returncode == 0:
            return True
        if q.returncode == 1:
            return False
        die(3, 'cannot evaluate ignore rules for %s: %s'
            % (destrel, q.stderr.decode('utf-8', 'replace').strip()))

    return ignored


# ---- tree walks ------------------------------------------------------------

def store_name(rel, is_dir):
    """Receipt-relative stored path: `.git` components -> `.git.captured`; a file named
    .gitignore/.gitattributes -> `<name>.captured` (so no live rule file or nested repo exists)."""
    parts = ['.git.captured' if c == '.git' else c for c in rel.split('/')]
    if not is_dir and parts[-1] in RENAME_NAMES:
        parts[-1] += '.captured'
    return '/'.join(parts)


def scan_source(root):
    """[(rel, kind)] for every entry, kinds: dir/file/link/other."""
    out = []
    stack = ['']
    while stack:
        rel = stack.pop()
        base = os.path.join(root, rel) if rel else root
        with os.scandir(base) as it:
            items = list(it)
        for e in items:
            r = e.name if not rel else rel + '/' + e.name
            if e.is_symlink():
                out.append((r, 'link'))
            elif e.is_dir(follow_symlinks=False):
                out.append((r, 'dir'))
                stack.append(r)
            elif e.is_file(follow_symlinks=False):
                out.append((r, 'file'))
            else:
                out.append((r, 'other'))
    out.sort(key=lambda t: os.fsencode(t[0]))
    return out


def receipt_regular_files(root):
    """['./rel'] for every regular file under root except manifest.sha256."""
    out = []
    stack = ['']
    while stack:
        rel = stack.pop()
        base = os.path.join(root, rel) if rel else root
        with os.scandir(base) as it:
            items = list(it)
        for e in items:
            r = e.name if not rel else rel + '/' + e.name
            if e.is_symlink():
                continue
            if e.is_dir(follow_symlinks=False):
                stack.append(r)
            elif e.is_file(follow_symlinks=False):
                if r != MANIFEST:
                    out.append('./' + r)
    out.sort(key=os.fsencode)
    return out


# ---- manifest --------------------------------------------------------------

def gnu_line(name, digest):
    nb = os.fsencode(name)
    if b'\n' in nb or b'\\' in nb:
        nb = nb.replace(b'\\', b'\\\\').replace(b'\n', b'\\n')
        return b'\\' + digest.encode('ascii') + b'  ' + nb + b'\n'
    return digest.encode('ascii') + b'  ' + nb + b'\n'


def manifest_bytes(root):
    return b''.join(gnu_line(n, sha256_file(os.path.join(root, n[2:])))
                    for n in receipt_regular_files(root))


def unescape(name):
    out = bytearray()
    i = 0
    while i < len(name):
        c = name[i:i + 1]
        if c == b'\\' and i + 1 < len(name):
            n = name[i + 1:i + 2]
            if n == b'n':
                out += b'\n'
                i += 2
                continue
            if n == b'\\':
                out += b'\\'
                i += 2
                continue
        out += c
        i += 1
    return bytes(out)


def parse_manifest(blob):
    recs = {}
    bad = 0
    for line in blob.split(b'\n'):
        if not line:
            continue
        esc = line.startswith(b'\\')
        m = REC.match(line[1:] if esc else line)
        if not m:
            bad += 1
            continue
        name = m.group(2)
        if esc:
            name = unescape(name)
        name = os.fsdecode(name)
        if name.startswith('./'):
            name = name[2:]
        recs[name] = m.group(1).decode('ascii')
    return recs, bad


# ---- receipt writers -------------------------------------------------------

def write_bytes(path, data, what):
    try:
        with open(path, 'wb') as fh:
            fh.write(data)
    except OSError as exc:
        die(5, 'cannot write %s: %s' % (what, exc))


def write_tsv(path, header, rows, what):
    if not rows:
        return False
    body = header + '\n' + ''.join('\t'.join(r) + '\n' for r in rows)
    write_bytes(path, body.encode('utf-8', 'surrogateescape'), what)
    return True


def write_summary():
    rows = ['name\tagent\tid\tstatus\tfinal_output_available']
    try:
        names = sorted(n for n in os.listdir(src) if n.endswith('-results.json'))
    except OSError:
        names = []
    for n in names:
        try:
            with open(os.path.join(src, n), encoding='utf-8') as fh:
                data = json.load(fh)
        except Exception as exc:
            w('warning: cannot parse %s: %s' % (n, exc))
            continue
        results = data.get('results') if isinstance(data, dict) else None
        if not isinstance(results, list):
            continue
        for e in results:
            if not isinstance(e, dict):
                continue
            name = e.get('name', '')
            agent = e.get('agent', '')
            eid = e.get('id', '')
            raw = e.get('output')
            avail = 0 if raw in (None, '', [], {}) else 1
            status = ''
            if avail:
                try:
                    dd = ast.literal_eval(raw) if isinstance(raw, str) else None
                    txt = dd.get('text', '') if isinstance(dd, dict) else ''
                    inner = json.loads(txt) if isinstance(txt, str) and txt.strip() else {}
                    status = str(inner.get('status', '')) if isinstance(inner, dict) else ''
                except Exception:
                    status = ''
            rows.append('\t'.join((str(name), str(agent), str(eid), status, str(avail))))
    write_bytes(os.path.join(dst, 'summary.tsv'),
                ('\n'.join(rows) + '\n').encode('utf-8', 'surrogateescape'), 'summary.tsv')


# ---- capture ---------------------------------------------------------------

def capture():
    if not os.path.isdir(src):
        die(2, 'source directory not found: ' + src)
    if os.path.islink(src):
        die(3, 'source is a symlink')
    entries = scan_source(src)
    for rel, kind in entries:
        if kind == 'other':
            die(3, 'refused special file in source: ' + rel)
        for comp in rel.split('/'):
            if comp == '..':
                die(3, 'escaping path in source: ' + rel)
    if dst == src or dst.startswith(src + '/'):
        die(3, 'destination nested in source')
    if src.startswith(dst + '/'):
        die(3, 'source nested in destination')
    if os.path.islink(dst):
        die(3, 'destination is a symlink')

    # Clear first: this is what neutralises any nested .gitignore carried by an
    # earlier receipt, so the ignore decision below sees only the lane's rules.
    try:
        if os.path.lexists(dst):
            shutil.rmtree(dst)
        os.makedirs(dst)
    except OSError as exc:
        die(5, 'cannot create receipt directory: %s' % exc)

    ignored = make_ignorer(lane)
    expected = {}
    renames = []
    excluded = []
    symlinks = []
    seen = {}

    for rel, kind in entries:
        if kind == 'dir':
            try:
                os.makedirs(os.path.join(dst, store_name(rel, True)), exist_ok=True)
            except OSError as exc:
                die(5, 'cannot create %s: %s' % (rel, exc))
            continue

        stored = store_name(rel, False)
        if stored in seen:
            die(3, 'destination name collision: %s (%s and %s)' % (stored, seen[stored], rel))
        if '/' not in stored and stored in ACCOUNTING + (MANIFEST,):
            die(3, 'destination name shadows a receipt file: %s' % stored)
        seen[stored] = rel

        ab = os.path.join(src, rel)
        if ignored(waves_rel + '/' + stored):
            if kind == 'link':
                digest = sha256_bytes(os.fsencode(os.readlink(ab)))
            else:
                digest = sha256_file(ab)
            if '\t' in rel or '\n' in rel or '\\' in rel:
                die(3, 'refused ignored path not representable in excluded.tsv: ' + repr(rel))
            excluded.append((rel, digest, 'ignored'))
            continue

        target = os.path.join(dst, stored)
        parent = os.path.dirname(target)
        try:
            if parent:
                os.makedirs(parent, exist_ok=True)
        except OSError as exc:
            die(5, 'cannot create %s: %s' % (os.path.dirname(stored), exc))
        if kind == 'link':
            link_target = os.readlink(ab)
            if '\t' in stored or '\n' in stored or '\\' in stored or '\t' in link_target \
                    or '\n' in link_target or '\\' in link_target:
                die(3, 'refused symlink not representable in symlinks.tsv: ' + repr(stored))
            try:
                os.symlink(link_target, target)
            except OSError as exc:
                die(5, 'cannot copy symlink %s: %s' % (rel, exc))
            symlinks.append((stored, link_target))
        else:
            h_src = sha256_file(ab)
            try:
                shutil.copyfile(ab, target)
                try:
                    shutil.copymode(ab, target)
                except OSError:
                    pass
            except OSError as exc:
                die(5, 'copy failed for %s: %s' % (rel, exc))
            h_dst = sha256_file(target)
            if h_src != h_dst:
                die(5, 'copy mismatch for %s' % rel)
            expected[stored] = h_dst
        if stored != rel:
            renames.append((rel, stored))

    write_summary()
    expected['summary.tsv'] = sha256_file(os.path.join(dst, 'summary.tsv'))
    if write_tsv(os.path.join(dst, 'renames.tsv'), '# original\tstored', sorted(renames, key=lambda r: os.fsencode(r[0])), 'renames.tsv'):
        expected['renames.tsv'] = sha256_file(os.path.join(dst, 'renames.tsv'))
    if write_tsv(os.path.join(dst, 'excluded.tsv'), '# path\tsha256\treason', sorted(excluded, key=lambda r: os.fsencode(r[0])), 'excluded.tsv'):
        expected['excluded.tsv'] = sha256_file(os.path.join(dst, 'excluded.tsv'))
    if write_tsv(os.path.join(dst, 'symlinks.tsv'), '# path\ttarget', sorted(symlinks, key=lambda r: os.fsencode(r[0])), 'symlinks.tsv'):
        expected['symlinks.tsv'] = sha256_file(os.path.join(dst, 'symlinks.tsv'))

    write_bytes(os.path.join(dst, MANIFEST), manifest_bytes(dst), MANIFEST)
    check_manifest_and_set(expected, check_only_manifest=False)
    print('captured+verified: %s -> %s' % (src, dst))
    print('records=%d renames=%d excluded=%d symlinks=%d'
          % (len(expected), len(renames), len(excluded), len(symlinks)))
    return 0


# ---- verification ----------------------------------------------------------

def check_ignore_neutralised():
    for name in receipt_regular_files(dst):
        if name.rsplit('/', 1)[-1] in RENAME_NAMES:
            die(4, 'receipt carries a live ignore/attribute rule file: ' + name)
        if '.git' in name.split('/'):
            die(4, 'receipt carries a live .git path component: ' + name)


def check_manifest_and_set(expected, check_only_manifest):
    mp = os.path.join(dst, MANIFEST)
    if not os.path.isfile(mp):
        die(4, 'manifest.sha256 missing in receipt')
    try:
        with open(mp, 'rb') as fh:
            stored = fh.read()
    except OSError as exc:
        die(4, 'cannot read manifest.sha256: %s' % exc)
    if manifest_bytes(dst) != stored:
        die(4, 'verification failed: manifest does not match the receipt bytes')
    check_ignore_neutralised()
    if check_only_manifest:
        return
    actual = {n[2:]: sha256_file(os.path.join(dst, n[2:])) for n in receipt_regular_files(dst)}
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    changed = sorted(k for k in set(actual) & set(expected) if actual[k] != expected[k])
    if missing or extra or changed:
        die(4, 'verification failed: receipt/source set mismatch missing=%s extra=%s changed=%s'
            % (missing[:5], extra[:5], changed[:5]))


def verify_disk():
    if not os.path.isdir(dst):
        die(4, 'receipt directory missing: ' + dst)
    check_manifest_and_set(None, check_only_manifest=True)
    print('verified: %s' % dst)
    print('records=%d' % len(receipt_regular_files(dst)))
    return 0


def verify_rev():
    if not os.path.isdir(os.path.join(lane, '.git')):
        die(4, 'lane is not a git repository: ' + lane)
    p = subprocess.run(['git', '-C', lane, 'rev-parse', '--verify', '--quiet', rev + '^{commit}'], capture_output=True)
    if p.returncode != 0:
        die(1, 'unknown revision: ' + rev)
    ents = {}
    for rec in git_bytes(lane, 'ls-tree', '-r', '-z', rev, '--', waves_rel).split(b'\0'):
        if not rec:
            continue
        meta, path = rec.split(b'\t', 1)
        mode, _typ, sha = meta.decode('ascii').split()
        ents[os.fsdecode(path)] = (mode, sha)
    man = waves_rel + '/' + MANIFEST
    if man not in ents:
        die(4, 'manifest.sha256 missing at %s:%s' % (rev, waves_rel))
    recs, failed = parse_manifest(git_bytes(lane, 'cat-file', 'blob', ents[man][1]))
    for name, h in recs.items():
        if name.startswith('/') or not name or '..' in name.split('/'):
            failed += 1
            continue
        e = ents.get(waves_rel + '/' + name)
        if e is None or e[0] == '120000':
            failed += 1
            continue
        if sha256_bytes(git_bytes(lane, 'cat-file', 'blob', e[1])) != h:
            failed += 1
    links = {}
    lt = waves_rel + '/symlinks.tsv'
    if lt in ents:
        text = git_bytes(lane, 'cat-file', 'blob', ents[lt][1]).decode('utf-8', 'surrogateescape')
        for line in text.split('\n'):
            if not line.strip() or line.startswith('#'):
                continue
            f = line.split('\t')
            if len(f) >= 2:
                links[f[0]] = f[1]
    uncovered = 0
    for path, (mode, sha) in ents.items():
        if path == man:
            continue
        rel = path[len(waves_rel) + 1:]
        if rel in recs:
            continue
        if mode == '120000' and rel in links:
            if git_bytes(lane, 'cat-file', 'blob', sha).decode('utf-8', 'surrogateescape') == links[rel]:
                continue
        uncovered += 1
    print('verify-rev rev=%s records=%d failed=%d uncovered=%d' % (rev, len(recs), failed, uncovered))
    return 0 if (failed == 0 and uncovered == 0) else 4


# ---- entry -----------------------------------------------------------------

lane, round_s, verify_s, rev = sys.argv[1:5]
lane = lane.rstrip('/') or '/'
waves_rel = 'census/round-%s/waves' % round_s
src = lane + '/.ufo/waves/round-' + round_s
dst = lane + '/' + waves_rel

try:
    if rev:
        sys.exit(verify_rev())
    if verify_s == '1':
        sys.exit(verify_disk())
    sys.exit(capture())
except Die as exc:
    print('error: ' + exc.msg, file=sys.stderr)
    sys.exit(exc.code)
except OSError as exc:
    print('error: %s' % exc, file=sys.stderr)
    sys.exit(5)
PY
exit $?
