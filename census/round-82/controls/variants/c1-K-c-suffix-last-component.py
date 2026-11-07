#!/usr/bin/env python3
"""souji r82 CONTROL K-c (suffix->last-component): the owntree/census suffix binding becomes last-component only, so NF12c-class and PF-1-type decoys accept; green by matching bare basename, red on those rows
One
r82 changes, each closing false ledger rows the r81 wave's S81MutCounter showed the r81 counter accepts:
  NF-F/NF-G a MOVED target in the token's OWN round tree is no longer free: every move must first satisfy the
        token-prefixed check, and the token-prefixed form now applies the same subtree-plus-suffix binding the r81
        rule applies under census/. Only `target[:tr.start]` hunk changes (r81 closed the census-side decoys; the
        own-tree side is the same defect one directory over, S81MutCounter MEDIUM).
  PF-1    the suffix binding is the token's FULL path below its round-<N>, not merely its last component, with case
        competing on that phrase against the name-S-preserving assumption: a decoy dropping the token's middle `w1`
        dir keeps the basename yet breaks the compound-suffix of the token's suffix under the token's round-N? The
        prereg binds the exact rule text (S81MutCounter's P07 PF-1 + PF-1/NF-F/NF-G decoys).
Rest of the r81 rule text follows (NF12 etc.).
  Citation note (r80 spot-check defect 6): the NF8 rule's mode whitelist 100644/100755 below rests on S294
        (git-fast-import(1) mode list: 100644/100755 regular files, 120000 symlink, 160000 gitlink, 040000 tree);
        S327 grounds only that a tree entry carries a mode and an object type.
r81 text follows (the r81 rule the NF12 decoy rows close):
souji r80 C1 counter (successor of census/round-79/c2-pointer-counter.py, which is frozen and unchanged; r80
changes, each closing one false ledger row the r79 wave's S79MutCounter showed the r79 counter accepts:
  NF8   a `..` range member must be a regular file (a blob, mode 100644 or 100755) at --rev, or a regular file
        under --fleet-root when written `fleet:` — a directory or symlink at a member's name is not that member
        (S327 git-ls-tree(1): each entry carries its mode and object type);
  NF10  a MOVED target's `round-<N>` directory is the token's own (same path before `round-<N>`) or the lane's
        capture root `census/round-<N>` (where wave evidence is captured since r28): a byte-equal copy under
        another tree with the same round number (`corpus/round-32/decoy/X.md`) is not the moved file;
  NF6b  a QUARANTINED declaration line must name the token and the quarantine path each as a whole path — the
        character before the match is not a path character, and the character after it is not a path character
        (a single trailing `.`, `,`, `;` or `:` that ends the sentence is allowed) — never as the prefix of a
        longer path (`.../other-stub.bak`, `.../.gitignore-p6repo`).
r79 text (the r79 changes over the r78 counter):
r79 changes, each closing one false ledger row the r78 wave's S78MutCounter showed the r78 counter accepts: a `..`
range TOKEN must list exactly the range's expansion (NF1, NF2); a TOKEN wrapped onto the next line must equal
the whole path run opening that line (NF5); MOVED needs a `round-<N>` in the token (NF3); QUARANTINED needs a
committed line of SKILL.md/LOG.md/SCORECARD.md/corpus/ at --rev naming both the token and the quarantine path
(NF4)). Base text of the r78 counter follows:
every evidence pointer a pinned population names must resolve at the measured revision to bytes whose
location AND identity the counter verifies itself, and every forged ledger row of a frozen forgery set must be
refused, item by item.

Populations (pinned by sha256; any other population file is FATAL, exit 2 — this is the r77 HIGH-3 fix):
  r77  census/round-77/c2-population.tsv  35 MISSING findings over SCORECARD/SKILL/QUALITY/README/PROVINCE at
       base d4f515637884695b3aa016da169d859d3ece6ac4.
  r78  census/round-78/c2-population.tsv  every MISSING finding of `tools/souji-pointer-check.py` over LOG.md at
       base a8558d410e9855a9d990d6542a24a9a3a365ab6c.
Population rows: id, file, line, token, frozen digest of the lane-disk bytes at the token path when frozen
(disk_digest) or '-'. Ledger rows: `id <TAB> class <TAB> target <TAB> note`.

Resolution rules (per item; first rule that applies decides; nothing else resolves an item):
  R0  integrity: the population's base blob of <file> carries <token> on <line>; else the item is an ERROR.
  R1  CAPTURED   the token path exists at --rev and the digest of its bytes there equals the frozen digest.
                 An item with no frozen digest is never resolved by a path appearing at --rev, and an unequal
                 digest is a MISMATCH (stub capture).
  Ledger classes (an item already CAPTURED ignores its ledger row):
  MOVED <path>   frozen digest present; <path> exists at --rev with the same digest; AND (r78, r77 G6) the
                 location is bound: the target's last component equals the token's, and when the token names
                 `round-<N>` the target names the same `round-<N>` component.
  LOCAL-POLICY   frozen digest present; the token sits under a frozen policy-local prefix
                 (.ufo/quarantine, census/operator-sweep-) and the lane disk still holds equal bytes.
  QUARANTINED <path>  no frozen digest; token absent at --rev, on the lane disk AND under the fleet root
                 (r78, r77 G5); <path> exists on the lane disk as `.ufo/quarantine/<one segment>/<rest>` with
                 dirname(<rest>) == dirname(token) (r78, r77 G4: the quarantine copy sits where the token sat).
  FLEET          no frozen digest; token absent at --rev and on the lane disk; it starts with `.ufo/` and exists
                 under --fleet-root (a fleet-owned path: runtime state, logs, the fleet L0 file, operator scopes).
  TOKEN <t;t>    no frozen digest; the token carries a parse artefact (trailing `>`, `\\` or `-`, or `..` inside its
                 last component); every target exists (at --rev, or under --fleet-root when written
                 `fleet:<path>`) and is bound to the source text (r78, r77 G1/G2):
                   trailing artefact: target = stem + rest, stem = token without trailing `>`/`\\`; rest is empty,
                   or the next line of the source (leading blanks and backticks stripped) starts with rest (a
                   wrapped path), or rest = <N> + S where `"<token>"` is followed on the line by a concatenation
                   whose next string literal is exactly S, and `r<N>` occurs on the line as a whole word;
                   `..` range: same directory, same stem before the digits and same suffix (r77 rule).
  ABSENT         no frozen digest; no parse artefact; token absent at --rev, on the lane disk, under --fleet-root
                 and in every lane ref's history (`git log --all -- <token>` empty).
  A ledger row whose rule fails, an unknown id or class, or a duplicate id is a REFUSED item.

Forgeries (--forge FILE, frozen per population): rows `fid <TAB> item id <TAB> class <TAB> target <TAB> expect`
where expect is REFUSED or MISMATCH. Each forged row replaces the ledger row of its item (all other rows as in
--ledger) and only that item is re-judged; the row matches iff the status equals expect. A forged row the counter
resolves is ACCEPTED.

Output: one `ITEM <id> <file>:<line> status=<...> [why=...]` line per item, `SUMMARY items=<N> resolved=<R>
unresolved=<U> refused=<F> mismatched=<M> errors=<E>`, then with --forge one `FORGE <fid> item=<id>
expect=<E> got=<S> match=<yes|no>` line per forgery and `FORGE-SUMMARY forged=<N> matched=<K> accepted=<A>`.
Exit 0 iff resolved == N, no unknown ledger id, and (with --forge) every forgery matches; 1 otherwise; 2 on usage.
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
POPS = {
    # population sha256: (label, base revision, row count)
    "bbc19ac66e543b0f974b5524b678985a2a755664294804dab4773953d14e889e":
        ("r77", "d4f515637884695b3aa016da169d859d3ece6ac4", 35),
    "7c04cdaf8b5935cca8f715b601bff4de1cbf0cbcd2627086925d5d2ac74ae4b5":
        ("r78", "a8558d410e9855a9d990d6542a24a9a3a365ab6c", 22),
}
POLICY_LOCAL = (".ufo/quarantine", "census/operator-sweep-")
CLASSES = ("MOVED", "LOCAL-POLICY", "QUARANTINED", "FLEET", "TOKEN", "ABSENT")
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
            "GIT_OPTIONAL_LOCKS": "0"})
ROUND = re.compile(r"(?:^|/)round-([0-9]+)(?:/|$)")


def git(root, *args, check=True):
    p = subprocess.run(["git", "-C", root, "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null",
                        *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
    if check and p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} rc={p.returncode}")
    return p


def _listing_digest(entries):
    h = hashlib.sha256()
    for rel, kind, digest in sorted(entries):
        h.update(rel + b"\0" + kind + b"\0" + digest.encode() + b"\n")
    return h.hexdigest()


def disk_digest(path):
    """f:<sha256> for a regular file, d:<listing sha256> for a directory (files and symlinks below it),
    l:<sha256 of target> for a symlink, None when absent."""
    if os.path.islink(path):
        return "l:" + hashlib.sha256(os.fsencode(os.readlink(path))).hexdigest()
    if os.path.isfile(path):
        with open(path, "rb") as f:
            return "f:" + hashlib.sha256(f.read()).hexdigest()
    if os.path.isdir(path):
        ent = []
        for dp, dns, fns in os.walk(path):
            for n in fns + [d for d in dns if os.path.islink(os.path.join(dp, d))]:
                p = os.path.join(dp, n)
                rel = os.fsencode(os.path.relpath(p, path))
                if os.path.islink(p):
                    ent.append((rel, b"l", hashlib.sha256(os.fsencode(os.readlink(p))).hexdigest()))
                elif os.path.isfile(p):
                    with open(p, "rb") as f:
                        ent.append((rel, b"f", hashlib.sha256(f.read()).hexdigest()))
                else:
                    ent.append((rel, b"x", "-"))
        return "d:" + _listing_digest(ent)
    if os.path.lexists(path):
        return "x:-"
    return None


def rev_digest(root, rev, path):
    """Same digest shape for <path> at <rev>, None when absent."""
    t = git(root, "cat-file", "-t", f"{rev}:{path}", check=False)
    if t.returncode != 0:
        return None
    kind = t.stdout.strip()
    if kind == b"blob":
        mode = git(root, "ls-tree", "-z", rev, "--", path).stdout.split(b" ", 1)[0]
        data = git(root, "cat-file", "blob", f"{rev}:{path}").stdout
        return ("l:" if mode == b"120000" else "f:") + hashlib.sha256(data).hexdigest()
    if kind == b"tree":
        out = git(root, "ls-tree", "-r", "-z", f"{rev}:{path}").stdout
        ent = []
        for rec in out.split(b"\0"):
            if not rec:
                continue
            meta, rel = rec.split(b"\t", 1)
            mode, typ, oid = meta.split(b" ")
            if typ != b"blob":
                ent.append((rel, b"x", "-"))
                continue
            data = git(root, "cat-file", "blob", oid.decode()).stdout
            ent.append((rel, b"l" if mode == b"120000" else b"f", hashlib.sha256(data).hexdigest()))
        return "d:" + _listing_digest(ent)
    return "x:-"


def _template_ok(token, rest, line):
    """rest = <N> + S, `"<token>"` followed on the line by a concatenation whose next literal is S, `r<N>` on
    the line as a whole word."""
    m = re.match(r"^([0-9]+)(.*)$", rest)
    if not m:
        return False
    n, s = m.group(1), m.group(2)
    lit = re.search(re.escape('"' + token + '"') + r'\s*\+[^"]*\+\s*"([^"]*)"', line)
    if not lit or lit.group(1) != s:
        return False
    return re.search(r"(?<![A-Za-z0-9])r" + n + r"(?![0-9])", line) is not None


AUTHORITY = ("SKILL.md", "LOG.md", "SCORECARD.md", "corpus")


def _declared(root, rev, token, target):
    """True iff one line of a committed authority file at <rev> names both <target> and <token>."""
    p = git(root, "grep", "-h", "-F", "-I", "-e", target, rev, "--", *AUTHORITY, check=False)
    if p.returncode not in (0, 1):
        raise RuntimeError(f"git grep rc={p.returncode}")
    lines = p.stdout.split(b"\n")
    # r80 (S79MutCounter NF6b): both paths must occur as whole paths on the SAME line
    return any(_whole(target.encode(), l) and _whole(token.encode(), l) for l in lines)


PATHCH = frozenset(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._/@+~-")


def _whole(needle, line):
    """True iff <needle> occurs in <line> as a whole path: the byte before is not a path byte, and the byte after
    is not a path byte, or is one sentence-ending `.`/`,`/`;`/`:` followed by a non-path byte or the line end."""
    i = line.find(needle)
    while i >= 0:
        j = i + len(needle)
        before_ok = i == 0 or line[i - 1] not in PATHCH
        after = line[j:j + 2]
        after_ok = (not after or after[0] not in PATHCH
                    or (after[:1] in (b".", b",", b";", b":") and (len(after) < 2 or after[1] not in PATHCH)))
        if before_ok and after_ok:
            return True
        i = line.find(needle, i + 1)
    return False


def _regular(root, rev, fleet, t):
    """True iff <t> is a regular file: a blob of mode 100644/100755 at <rev>, or (written `fleet:<path>`) a regular
    non-symlink file under <fleet>."""
    if t.startswith("fleet:"):
        p = os.path.join(fleet, t[len("fleet:"):])
        return os.path.isfile(p) and not os.path.islink(p)
    out = git(root, "ls-tree", "-z", rev, "--", t, check=False).stdout
    if not out:
        return False
    meta, _, name = out.rstrip(b"\0").partition(b"\t")
    mode, typ, _oid = meta.split(b" ")
    return name == t.encode() and typ == b"blob" and mode in (b"100644", b"100755")


def token_ok(root, rev, fleet, token, targets, line, nextline):
    last = token.rsplit("/", 1)[-1]
    trailing = token[-1] in ">\\-"
    dots = ".." in last
    if not (trailing or dots) or not targets:
        return "no parse artefact" if not (trailing or dots) else "no target"
    for t in targets:
        orig = t
        if t.startswith("fleet:"):
            t = t[len("fleet:"):]
            if not os.path.lexists(os.path.join(fleet, t)):
                return f"target absent under fleet root: {t}"
        elif rev_digest(root, rev, t) is None:
            return f"target absent at rev: {t}"
        if dots and not _regular(root, rev, fleet, orig):
            # r80 (S79MutCounter NF8): a range member is a regular file, never a directory or symlink
            return f"range member is not a regular file: {orig}"
        if trailing:
            stem = token.rstrip(">\\")
            if not t.startswith(stem):
                return f"target does not continue the token: {t}"
            rest = t[len(stem):]
            wrapped = nextline.lstrip(" \t`")
            # r79 (S78MutCounter NF5): a wrapped continuation is the WHOLE path run that opens the next line,
            # never a prefix of it (a one-character `-l` file resolved `...-located-quote.txt`).
            run = re.match(r"[A-Za-z0-9._/@+~-]*", wrapped).group(0)
            if not (rest == "" or (rest and rest == run) or _template_ok(token, rest, line)):
                return f"target continuation is not in the source text: {t}"
        else:
            d, b = os.path.split(t)
            pre, suf = last.split("..", 1)
            stem = pre.rstrip("0123456789")
            m = re.match(r"^[A-Za-z_-]*[0-9]+(.*)$", suf)
            if not m or not stem or stem == pre:
                return "range endpoints carry no digits"
            sfx = m.group(1)
            mid = b[len(stem):len(b) - len(sfx)] if sfx else b[len(stem):]
            if (d != os.path.dirname(token) or not b.startswith(stem) or not b.endswith(sfx)
                    or not mid.isdigit()):
                return f"target is not an expansion of the range: {t}"
    if dots:
        # r79 (S78MutCounter NF1/NF2): the targets are exactly the range's expansion, every member present —
        # one member never stands for the range, and a member outside the span is not an expansion.
        pre, suf = last.split("..", 1)
        lo = re.search(r"([0-9]+)$", pre).group(1)
        m = re.match(r"^[A-Za-z_-]*([0-9]+)(.*)$", suf)
        hi, sfx = m.group(1), m.group(2)
        stem = pre[:len(pre) - len(lo)]
        w = len(lo) if lo.startswith("0") and len(lo) > 1 else 0
        if int(hi) < int(lo) or int(hi) - int(lo) > 999:
            return "range span is empty or unbounded"
        want = {os.path.join(os.path.dirname(token), f"{stem}{i:0{w}d}{sfx}")
                for i in range(int(lo), int(hi) + 1)}
        got = {t[len("fleet:"):] if t.startswith("fleet:") else t for t in targets}
        if got != want or len(targets) != len(want):
            return f"targets are not exactly the range's expansion ({len(got & want)}/{len(want)} members)"
    return ""


CAPTURE = re.compile(r"^(?:waves/|wave/|records/wave-[^/]+/)(.+)$")


def _capture_ok(token, kr, target, tr):
    """r81: True iff <target>'s path below census/round-<N>/ is a wave capture subtree (waves/, wave/,
    records/wave-<w>/) followed by a non-empty whole-component suffix of <token>'s path below its round-<N>/."""
    m = CAPTURE.match(target[tr.end(0):].rstrip("/"))
    if not m:
        return False
    want = [c for c in m.group(1).split("/") if c]
    have = [c for c in token[kr.end(0):].rstrip("/").split("/") if c]
    return bool(want) and bool(have) and want[-1] == have[-1]


def _owntree_ok(token, kr, target, tr):
    """r82: True iff a MOVED target in the token's own round tree is a capture shape: the path from the token's
    round-<N> (or from the target's round-<N> when equal) equals the token's path below its round-<N> (the true
    shape) OR is a wave capture subtree. This binds the own-tree decoys NF-F/NF-G (a byte-equal copy under
    .../decoy/) while keeping the true capture TF4 (the token itself moved)."""
    tt = target[tr.end(0):].rstrip("/")
    tk = token[kr.end(0):].rstrip("/")
    if tt == tk:
        return True
    return _capture_ok(token, kr, target, tr)


def judge(root, rev, fleet, item, entry, blob):
    """(status, why) for one population item under one ledger entry (None = no ledger row)."""
    iid, file, line, token, frozen = item
    frozen = None if frozen == "-" else frozen
    if not (line.isdigit() and 0 < int(line) <= len(blob) and token in blob[int(line) - 1]):
        return "ERROR", "token not on the base line"
    text = blob[int(line) - 1]
    nextline = blob[int(line)] if int(line) < len(blob) else ""
    at_rev = rev_digest(root, rev, token)
    if at_rev is not None:
        if frozen is not None and at_rev == frozen:
            return "CAPTURED", ""
        return "MISMATCH", ("no frozen bytes (stated absent or non-lane)" if frozen is None
                            else "digest differs")
    if entry is None:
        return "UNRESOLVED", ""
    cls, target = entry
    on_disk = disk_digest(os.path.join(root, token))
    why = ""
    if cls not in CLASSES:
        why = f"unknown class {cls}"
    elif cls == "MOVED":
        tr, kr = ROUND.search(target), ROUND.search(token)
        if frozen is None:
            why = "no frozen bytes to move"
        elif rev_digest(root, rev, target) != frozen:
            why = "target absent at rev or digest differs"
        elif os.path.basename(target.rstrip("/")) != os.path.basename(token.rstrip("/")):
            why = "target's last component differs from the token's"
        elif kr and (not tr or tr.group(1) != kr.group(1)):
            why = "target names a different round than the token"
        elif kr and target[:tr.start(0)] == token[:kr.start(0)] and not _owntree_ok(token, kr, target, tr):
            # r82 (S81MutCounter NF-F/NF-G): the token-prefixed branch also requires a true capture shape; only
            # the identical token path (the true move) or a wave subtree passes, so byte-equal own-tree decoys
            # (`.ufo/waves/round-<N>/decoy/...`) fail here.
            why = "own-round-tree target is neither the token's own path nor a wave capture keeping the token's suffix"
        elif kr and target[:tr.start(0)] not in (token[:kr.start(0)], "census"):
            # r80 (S79MutCounter NF10): a moved file lands where the token sat or in the lane's capture root
            why = "target's round-<N> directory is neither the token's nor census/round-<N>"
        elif kr and target[:tr.start(0)] == "census" and token[:kr.start(0)] != "census" \
                and not _capture_ok(token, kr, target, tr):
            # r81 (S80MutCounter NF12): under the capture root only a wave capture subtree holds the moved file
            why = "census/round-<N> target is not a wave capture keeping the token's own path suffix"
        elif kr and target[:tr.start(0)] == "census" and token[:kr.start(0)] == "census" \
                and not _capture_ok(token, kr, target, tr):
            # r82 (S81MutCounter PF-1): the suffix is the token's FULL path below its round-<N>, not its last
            # component, so a partial suffix dropping the token's middle dir (census/round-61/wave/S61ExecRealRecord/...)
            # is not the moved file. _capture_ok already checks the whole suffix; the defect is the moved-last-component rule
            # asked only for the basename. The order carries: owntree/PF-1 before the last-component basename test.
            why = "census-in-tree target is not a wave capture keeping the token's full path suffix"
        elif not kr:
            # r79 (S78MutCounter NF3): with no round-<N> in the token the location binding is the last
            # component alone, so a byte-equal copy in any directory would resolve the item.
            why = "token names no round-<N>: a moved location cannot be bound"
    elif cls == "LOCAL-POLICY":
        if frozen is None:
            why = "no frozen bytes"
        elif not token.startswith(POLICY_LOCAL):
            why = "not under a policy-local prefix"
        elif on_disk != frozen:
            why = "lane disk bytes absent or changed"
    elif frozen is not None:
        why = f"{cls} refused: the lane disk held bytes at the token path at freeze"
    elif on_disk is not None:
        why = f"{cls} refused: the lane disk holds the token path"
    elif cls == "QUARANTINED":
        parts = target.split("/")
        rest = "/".join(parts[3:])
        if not target.startswith(".ufo/quarantine/") or len(parts) < 4 \
                or not os.path.lexists(os.path.join(root, target)):
            why = "quarantine target absent on the lane disk"
        elif os.path.dirname(rest) != os.path.dirname(token.rstrip("/")):
            why = "quarantine target does not sit where the token sat"
        elif os.path.lexists(os.path.join(fleet, token)):
            why = "token exists under the fleet root"
        elif not _declared(root, rev, token, target):
            # r79 (S78MutCounter NF4): the quarantine leaf is bound to a committed declaration — one line of
            # the lane's authority files at --rev names both the token and this quarantine path.
            why = "no committed line declares this quarantine path for the token"
    elif cls == "FLEET":
        if not token.startswith(".ufo/") or not os.path.lexists(os.path.join(fleet, token)):
            why = "not under the fleet root"
    elif cls == "TOKEN":
        why = token_ok(root, rev, fleet, token, [t for t in target.split(";") if t], text, nextline)
    elif cls == "ABSENT":
        if token[-1] in ">\\-" or ".." in token.rsplit("/", 1)[-1]:
            why = "token carries a parse artefact (TOKEN, not ABSENT)"
        elif os.path.lexists(os.path.join(fleet, token)):
            why = "exists under the fleet root"
        elif git(root, "log", "--all", "--format=%H", "-1", "--", token).stdout.strip():
            why = "present in lane history"
    if why:
        return "REFUSED", f"class={cls} why={why}"
    return cls, ""


def _ledger(path):
    ledger, bad = {}, []
    with open(path, encoding="utf-8") as f:
        for l in f:
            if not l.strip() or l.startswith("#"):
                continue
            r = l.rstrip("\n").split("\t")
            if len(r) < 3 or r[0] in ledger:
                bad.append(r[0] if r else "?")
                continue
            ledger[r[0]] = (r[1], r[2])
    return ledger, bad


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--fleet-root", required=True)
    ap.add_argument("--population", required=True, help="pinned population TSV")
    ap.add_argument("--ledger", help="ledger TSV (absent = no ledger)")
    ap.add_argument("--forge", help="frozen forgery TSV for this population")
    ns = ap.parse_args(argv)
    root, fleet = os.path.abspath(ns.root), os.path.abspath(ns.fleet_root)
    rv = git(root, "rev-parse", "--verify", ns.rev + "^{commit}", check=False)
    if rv.returncode != 0:
        print("C2-COUNTER-FATAL: --rev does not name a commit", file=sys.stderr)
        return 2
    rev = rv.stdout.decode().strip()
    with open(ns.population, "rb") as f:
        pop_sha = hashlib.sha256(f.read()).hexdigest()
    if pop_sha not in POPS:
        print(f"C2-COUNTER-FATAL: population sha256 {pop_sha} is not pinned", file=sys.stderr)
        return 2
    label, base, n = POPS[pop_sha]
    with open(ns.population, encoding="utf-8") as f:
        pop = [l.rstrip("\n").split("\t") for l in f if l.strip() and not l.startswith("#")]
    if len(pop) != n or len({r[0] for r in pop}) != n or any(len(r) != 5 for r in pop):
        print(f"C2-COUNTER-FATAL: population is not {n} well-formed rows", file=sys.stderr)
        return 2
    ledger, bad_ledger = _ledger(ns.ledger) if ns.ledger else ({}, [])
    with open(os.path.abspath(__file__), "rb") as f:
        print(f"# counter sha256={hashlib.sha256(f.read()).hexdigest()} population={label} base={base} rev={rev}")
    print(f"# population path={ns.population} sha256={pop_sha}")
    for opt, p in (("ledger", ns.ledger), ("forge", ns.forge)):
        if p:
            with open(p, "rb") as f:
                print(f"# {opt} path={p} sha256={hashlib.sha256(f.read()).hexdigest()}")
        else:
            print(f"# {opt} none")
    blobs = {}
    for r in pop:
        if r[1] not in blobs:
            blobs[r[1]] = git(root, "show", f"{base}:{r[1]}", check=False).stdout.decode(
                "utf-8", "replace").split("\n")
    ids = {r[0] for r in pop}
    unknown = sorted(set(ledger) - ids) + bad_ledger
    counts = dict(resolved=0, unresolved=0, refused=0, mismatched=0, errors=0)
    key = {"UNRESOLVED": "unresolved", "REFUSED": "refused", "MISMATCH": "mismatched", "ERROR": "errors"}
    for item in pop:
        st, why = judge(root, rev, fleet, item, ledger.get(item[0]), blobs[item[1]])
        counts[key.get(st, "resolved")] += 1
        print(f"ITEM {item[0]} {item[1]}:{item[2]} status={st}" + (f" {why}" if why else ""))
    for u in unknown:
        counts["refused"] += 1
        print(f"LEDGER-REFUSED id={u} why=unknown or duplicate id")
    print(f"SUMMARY items={len(pop)} resolved={counts['resolved']} unresolved={counts['unresolved']} "
          f"refused={counts['refused']} mismatched={counts['mismatched']} errors={counts['errors']}")
    ok = counts["resolved"] == len(pop) and not unknown
    if ns.forge:
        byid = {r[0]: r for r in pop}
        forged = matched = accepted = 0
        with open(ns.forge, encoding="utf-8") as f:
            for l in f:
                if not l.strip() or l.startswith("#"):
                    continue
                r = l.rstrip("\n").split("\t")
                if len(r) != 5 or r[1] not in byid or r[4] not in ("REFUSED", "MISMATCH"):
                    print(f"C2-COUNTER-FATAL: malformed forgery row {r[0] if r else '?'}", file=sys.stderr)
                    return 2
                fid, iid, cls, target, expect = r
                st, why = judge(root, rev, fleet, byid[iid], (cls, target), blobs[byid[iid][1]])
                forged += 1
                hit = st == expect
                matched += hit
                accepted += st not in ("REFUSED", "MISMATCH", "UNRESOLVED", "ERROR")
                print(f"FORGE {fid} item={iid} class={cls} expect={expect} got={st} match={'yes' if hit else 'no'}"
                      + (f" {why}" if why and not hit else ""))
        print(f"FORGE-SUMMARY forged={forged} matched={matched} accepted={accepted}")
        ok = ok and forged > 0 and matched == forged
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
