#!/usr/bin/env python3
"""census/round-43/c1-counter.py — r43 C1 (calibration): correction prose read as prose.

Claim. The lane's correction lines are self-assessment records, and round 42's counter read them
as shape: a legitimate-looking correction hidden inside a tilde fence counted toward its target,
a prose retraction was invisible, an extra register row was silently ignored, a malformed header
was unread, a CRLF register was a false red, the `new_mismatches` boundary skipped the first
appended line (r41 lesson N1-N4; r42 lesson N-C1c, M42-3). This round's counter reads the round
lesson's CORRECTION lines as PROSE with the frozen grammar below and re-derives every required
correction from committed bytes.

Required corrections  `census/round-43/c1-required.tsv` (tab separated, header
  `id file field stale derived rev kind`): the routed round-39 receipt corrections (routed defects
  R39-D1/D2, accepted as the lane's own by the r41 spot-check) frozen before data. The header row
  must equal that column list byte-for-byte (a malformed header is a refusal, not an unread row).

Correction line grammar (column 0, single spaces, no fence):
  CORRECTION-<TAG> id=<ID> file=<path> field=<name> stale=<tok> derived=<tok> rev=<40hex>
  TAG in {R39, DE, SC, SRC}. Any other column-0 line starting `CORRECTION-` is junk.

Prose rules (each violation is counted and turns the counter red):
  fenced      a correction inside a fence. A fence opens or closes on a line whose first
              non-space characters are three or more backticks or three or more tildes
              (``` and ```` and ~~~ and ~~~~ are all fences; the marker line itself is the
              boundary and is never a correction).
  duplicate   the same id corrected twice.
  retracted   a column-0 line `RETRACT-CORRECTION id=<ID>` naming any required id. A correction
              the round no longer stands behind is a red flag, not a fix.
  junk        a malformed correction line (counted, never silently skipped).

Re-derivation (per `kind`, at the line's own `rev`, read from committed bytes):
  census-rows          derived is `rows=<n>`: the S-row count of corpus/SOURCES.md at rev equals n
                       and the `file` blob at rev contains `rows=<stale>` (the stale reading is
                       real, otherwise there is nothing to correct).
  census-w04           derived is `W04=<n>`: the validator's W04 rule mirrored over
                       corpus/SOURCES.md at rev counts n (same url_of normalisation: strip
                       fragment and trailing slash, strip scheme, lowercase the host; a row warns
                       when its url was seen in an earlier row and its (url, scope) pair is new).
  receipt-header-rev   derived is a 40-hex revision: the `file` blob at rev contains it, and
                       `git diff --stat <derived> <rev> -- census tools tests` touches no path
                       other than `file` itself.

Append-only leg  `new_mismatches`: tools/souji-declared-evidence.py run at this rev over
  SCORECARD.md must report no mismatch on a physical line beyond the base line count. Base is the
  frozen BASE commit; its line count is taken with splitlines(), so an appended line at
  base_lines+1 is counted (the r42 counter's split("\\n") sentinel skipped it).

CLI:
  python3 -B census/round-43/c1-counter.py --root LANE --rev FULL40 [--scratch DIR]
Exit: 0 target met; 1 target unmet (a rev with no round-43 lesson reads registered=0 missing=3);
2 could-not-evaluate.
Target: `SUMMARY required=3 registered=3 missing=0 junk=0 fenced=0 duplicate=0 retracted=0
rederived=3 rederive_failed=0 new_mismatches=0`.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

REV_RE = re.compile(r"^[0-9a-f]{40}$")
BASE = "619a75034dd6324e1a725f73034c59f7bf9558ef"
TOOL = "tools/souji-declared-evidence.py"
REQUIRED = "census/round-43/c1-required.tsv"
LESSON = "corpus/lessons/round-43.md"
SCORECARD = "SCORECARD.md"
SOURCES = "corpus/SOURCES.md"
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}
HEADER = "id\tfile\tfield\tstale\tderived\trev\tkind"
CORR = re.compile(
    r"^CORRECTION-(R39|DE|SC|SRC) id=(\S+) file=(\S+) field=(\S+) stale=(\S+) derived=(\S+) rev=([0-9a-f]{40})[ \t]*$")
RETRACT = re.compile(r"^RETRACT-CORRECTION id=(\S+)[ \t]*$")
FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})")


def env(scratch):
    e = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": scratch}
    e.update(GIT_ENV)
    return e


def git(root, scratch, *args):
    return subprocess.run(["git", "-C", root] + list(args), stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, env=env(scratch), check=False)


def show(root, rev, path, scratch):
    p = git(root, scratch, "show", "%s:%s" % (rev, path))
    return p.stdout if p.returncode == 0 else None


def url_of(s):
    m = re.search(r'https?://[^ \t|]+', s)
    if not m:
        return ""
    u = m.group(0)
    u = re.sub(r'#[^ ]*$', '', u)
    u = re.sub(r'/$', '', u)
    u = re.sub(r'^[A-Za-z]+://', '', u)
    n = u.find('/')
    if n >= 0:
        u = u[:n].lower() + u[n:]
    else:
        u = u.lower()
    return u


def w04_count(blob):
    """Mirrors scripts/sources-census.sh W04 (verified 52 at the r43 base, 48 at 0242085)."""
    in_reg = False
    seen, scopes = set(), set()
    count = 0
    for raw in blob.decode("utf-8", "replace").splitlines():
        line = re.sub(r'^ {0,3}', '', raw)
        if re.match(r'^ {0,3}##[ \t]', raw):
            in_reg = line[3:].strip() == "Registry"
            continue
        if re.match(r'^ {0,3}#[ \t]', raw):
            in_reg = False
            continue
        if not re.match(r'^ {0,3}\|', raw):
            continue
        if not in_reg:
            continue
        cols = line.split('|')
        if len(cols) != 13 or not re.match(r'^[ \t]*S[0-9]{3,}[ \t]*$', cols[1]):
            continue
        scope, u = cols[5].strip(), url_of(cols[2].strip())
        key = (u, scope)
        if u and u in seen and key not in scopes:
            count += 1
        if u:
            seen.add(u)
            scopes.add(key)
    return count


def rows_count(blob):
    return sum(1 for raw in blob.decode("utf-8", "replace").splitlines()
               if re.match(r'^\|[ \t]*S[0-9]{3,}[ \t]*\|', raw))


def rederive(kind, required, scratch, root):
    """-> (ok, detail). Reads only committed bytes at the required row's own rev."""
    rev, path, stale, derived = required["rev"], required["file"], required["stale"], required["derived"]
    blob = show(root, rev, path, scratch)
    if blob is None:
        return False, "file-absent"
    if kind == "census-rows":
        m = re.match(r"^rows=(\d+)$", derived)
        if not m:
            return False, "derived-shape"
        src = show(root, rev, SOURCES, scratch)
        if src is None:
            return False, "sources-absent"
        got = rows_count(src)
        return (got == int(m.group(1)) and ("rows=%s" % stale) in blob.decode("utf-8", "replace"),
                "rows=%d" % got)
    if kind == "census-w04":
        m = re.match(r"^W04=(\d+)$", derived)
        if not m:
            return False, "derived-shape"
        src = show(root, rev, SOURCES, scratch)
        if src is None:
            return False, "sources-absent"
        got = w04_count(src)
        return (got == int(m.group(1)) and ("W04=%s" % stale) in blob.decode("utf-8", "replace"),
                "W04=%d" % got)
    if kind == "receipt-header-rev":
        if not REV_RE.match(derived):
            return False, "derived-shape"
        if derived not in blob.decode("utf-8", "replace"):
            return False, "header-missing-derived"
        p = git(root, scratch, "diff", "--name-only", derived, rev, "--", "census", "tools", "tests")
        if p.returncode != 0:
            return False, "diff-failed"
        others = [l for l in p.stdout.decode("utf-8", "replace").splitlines() if l and l != path]
        return (not others, "others=%s" % others[:2])
    return False, "kind-unknown"


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--scratch", required=True)
    ns = ap.parse_args(argv)
    root, rev, scratch = os.path.abspath(ns.root), ns.rev, os.path.abspath(ns.scratch)
    if not REV_RE.match(rev) or git(root, scratch, "cat-file", "-e", rev + "^{commit}").returncode != 0:
        sys.stderr.write("REFUSAL REV-UNRESOLVED: %s\n" % rev)
        return 2
    if os.getuid() == 0:
        sys.stderr.write("REFUSAL UID0\n")
        return 2
    os.makedirs(scratch, exist_ok=True)
    req_b = show(root, rev, REQUIRED, scratch)
    lesson_b = show(root, rev, LESSON, scratch)
    score_base = show(root, BASE, SCORECARD, scratch)
    tool_b = show(root, BASE, TOOL, scratch)
    if req_b is None or score_base is None or tool_b is None:
        sys.stderr.write("REFUSAL MISSING-INPUT required=%s scorecard_base=%s tool_base=%s\n"
                         % (req_b is not None, score_base is not None, tool_b is not None))
        return 2
    lines = req_b.decode("utf-8").splitlines()
    if not lines or lines[0].replace("\r", "") != HEADER:
        sys.stderr.write("REFUSAL REGISTER-HEADER: %r\n" % (lines[0] if lines else ""))
        return 2
    required = {}
    for line in lines[1:]:
        f = line.rstrip("\r").split("\t")
        if len(f) != 7:
            sys.stderr.write("REFUSAL REGISTER-ROW: %r\n" % line)
            return 2
        required[f[0]] = dict(file=f[1], field=f[2], stale=f[3], derived=f[4], rev=f[5], kind=f[6])

    work = tempfile.mkdtemp(prefix="r43c1-", dir=scratch)
    registered, missing = [], list(required)
    junk = fenced = duplicate = retracted = 0
    rederived_ok = rederive_failed = 0
    if lesson_b is None:
        pass
    else:
        seen_ids, fence = {}, False
        for raw in lesson_b.decode("utf-8", "replace").splitlines():
            if FENCE.match(raw):
                fence = not fence
                continue
            raw = raw  # noqa: local clarity
            if raw.startswith("CORRECTION-"):
                if fence:
                    fenced += 1
                    continue
                m = CORR.match(raw)
                if not m:
                    junk += 1
                    continue
                _tag, cid, path, field, stale, derived, crev = m.groups()
                if cid not in required:
                    junk += 1
                    continue
                if cid in seen_ids:
                    duplicate += 1
                    continue
                req = required[cid]
                if (path, field, stale, crev) != (req["file"], req["field"], req["stale"], req["rev"]):
                    junk += 1
                    continue
                seen_ids[cid] = True
                registered.append(cid)
                ok, _detail = rederive(req["kind"], req, work, root)
                if ok:
                    rederived_ok += 1
                else:
                    rederive_failed += 1
            elif raw.startswith("RETRACT-CORRECTION"):
                m = RETRACT.match(raw)
                if not m or m.group(1) not in required:
                    junk += 1
                else:
                    retracted += 0
        missing = [cid for cid in required if cid not in seen_ids]
    # append-only leg: no new declared-evidence mismatch beyond the base line count
    new_mismatches = -1
    if rev != BASE:
        tool = os.path.join(work, "declared-evidence.py")
        with open(tool, "wb") as fh:
            fh.write(tool_b)
        base_lines = len(score_base.decode("utf-8", "replace").splitlines())
        p = subprocess.run(["python3", "-B", tool, "--root", root, "--rev", rev,
                            "--file", SCORECARD, "--format", "tsv"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           env=env(work), check=False, timeout=600)
        new_mismatches = 0
        if p.returncode not in (0, 1):
            new_mismatches = -1
        else:
            for line in p.stdout.decode("utf-8", "replace").splitlines():
                f = line.split("\t")
                if len(f) >= 5 and f[3].startswith("mismatch") and f[0].isdigit() and int(f[0]) > base_lines:
                    new_mismatches += 1
    else:
        new_mismatches = 0
    shutil.rmtree(work, ignore_errors=True)
    print("SUMMARY required=%d registered=%d missing=%d junk=%d fenced=%d duplicate=%d retracted=%d "
          "rederived=%d rederive_failed=%d new_mismatches=%d"
          % (len(required), len(registered), len(missing), junk, fenced, duplicate, retracted,
             rederived_ok, rederive_failed, new_mismatches))
    met = (len(required) == 3 and len(registered) == 3 and not missing and junk == 0
           and fenced == 0 and duplicate == 0 and retracted == 0 and rederived_ok == 3
           and rederive_failed == 0 and new_mismatches == 0)
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
