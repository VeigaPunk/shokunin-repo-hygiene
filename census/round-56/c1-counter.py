#!/usr/bin/env python3
"""C1 counter v5 (souji round 56): declared-count annotation agreement, amended.

Frozen predicate: census/round-56/preregistration.txt, claim C1. A NEW frozen
version of census/round-55/c1-counter.py (whose bytes are never edited). Every
v4 check carries over; v5 instruments the r55 routed surfaces (corpus/
lessons/round-55.md ## Routed to r56 and ## Addendum — the N1/D14/D15 pair
filing hole, the sentinel S55-S2 v3→v4 regression, the sentinel S55-S1 binary
numstat shape, the ERRATUM-R55-1 form-feed fixture, and the reviewer02 RD-A
differential rule):

  PAIR-FILING-HIDDEN (N1/D14/D15) a pair-form R53-CORRECTION filing counts as
                          a filing ONLY when its own line is visible: filings
                          inside fences or HTML comments in the correction
                          file no longer file an overstated LOG/README pair
                          (v4 counted them, so a documentation example could
                          "file" an overstatement). A matching filing that
                          exists but is hidden is refused by name
                          (PAIR-FILING-HIDDEN) beside UNFILED-SOURCES-
                          ANNOTATION, and the SUMMARY carries pairhidden=.
  CommonMark 0.31.2 HTML-COMMENT START (S55-S2 repair) the `<!--` opener
                          needs at most three leading spaces: a four-space-
                          indented `<!--` is indented code, opens no comment
                          region, and no longer hides a following real
                          overstatement from the pair scan (v4 regression:
                          v3 exit 1, v4 exit 0 — receipt
                          census/round-55/records/probe-s2-pair-indent-
                          comment.txt). Fence and closing rules unchanged.
  DELETIONS-UNREADABLE-BINARY (S55-S1) a binary numstat entry (`-` add/del
                          columns) is refused by name instead of being read
                          as deletions=-1 (v4 printed DELETED-LINES with a
                          nonsense count on the NUL-byte shape; receipt
                          census/round-55/wave/w1/S55sentinel01/receipts/
                          attacks-nul.txt).
  NUMSTAT LF-ONLY PARSE   the deletion check splits numstat on LF only; a
                          repository-local core.quotePath=false (which the
                          counter's scrubbed environment does not neutralize)
                          can no longer split a raw NEL-named record (r55
                          named limit, probe receipt records/probe-numstat-
                          quotepath.txt: splitlines records 3, counted 2).
  F7-FF2 (ERRATUM-R55-1)  the exact r54 sentinel S1 shape — two FORM FEED
                          (\x0c) lines above the opening ~~~ fence — enters
                          the frozen fixture set; the r55 F7-FF fixture stays
                          frozen as vertical tab (\x0b).

v3/v4 findings carried over: MULTIPLE-ANNOTATIONS, RECORD-SHA-MISMATCH,
INERT-CORRECTION, CORRECTION-IN-FENCE, DELETED-LINES,
ZONE-TOKEN-STRADDLES-EDGE, BOGUS-RECOMPUTED, UNFILED-SOURCES-ANNOTATION,
SOURCES-RECOMPUTE-MISMATCH, ANCHOR-ALIAS-MISMATCH, PAIR-FILING-INERT.
v5 findings added: PAIR-FILING-HIDDEN, DELETIONS-UNREADABLE-BINARY, CORRECTION-FILE-BINARY.
v5 over-hide repair (F29): an HTML comment region opens only on a line that begins with `<!--`.

  ONE LINE MODEL (S1 fix)         lines are counted by LF only everywhere —
                          the hidden-line set, the correction's own line
                          number, the site lines, the pair scan and the
                          record count. v3 numbered hidden_lines() with
                          str.splitlines() (which also breaks on \x0b \x0c
                          \x1c \x1d \x1e \x85 \u2028 \u2029) while the
                          correction's line number counted only \n, so two
                          form-feed lines above a ~~~ fence moved the fence
                          off the corrections (exit 1 -> exit 0)
  PREFIX-TOLERANT LEXING (R1)     a correction lexes with 0-3 leading spaces
                          and/or a one-line `<!-- ... -->` wrapper; a hidden
                          line that lexes as a correction is audited like any
                          filing (v3 audited only `^R5x`-anchored lines, so a
                          buried bogus correction on an agreeing site exited 0)
  ANCHOR-ALIAS-MISMATCH (R2)      the annotation zone is evaluated after EVERY
                          occurrence of the anchor on a site line; a second
                          annotated anchor whose count disagrees with the
                          first is refused (v3 judged only the first
                          occurrence)
  PAIR-FILING-INERT (R3)          a pair-form R53-CORRECTION filing whose
                          stale pair differs from the annotated pair is
                          refused (v3 silently dropped it)
  UNFILED-SOURCES-ANNOTATION (R4/S2, widened) the pair annotation matches
                          with or without the unit word `rows` and with the
                          `->` or `→` separator (v3 required the word and the
                          ASCII arrow)
  CommonMark 0.31.2 FENCE START CONDITIONS (R5) a fence opener/closer may
                          carry at most three leading spaces (four is an
                          indented code block, not a fence) and a backtick
                          fence's info string may not contain a backtick
                          (v3 over-hid both shapes, refusing visible filings)
  PAIR-SITES HIDE-FENCE (R6)      the LOG/README pair scan skips lines hidden
                          by the same grammar (v3 fired UNFILED on fenced
                          code examples)
  PTR (narrowed exemption)        the pointer exemption now requires a
                          path-like token (optional directories, a file name
                          with a dot extension, colon, line) so a timestamp
                          such as `14:05` no longer exempts an overstating
                          pair line
  SOURCES-RECOMPUTE-MISMATCH (N5) unchanged check; committed fixture F23 now
                          reaches the branch (kill-power pinned)
  BT4 SHORT RUN (M2)              unchanged check; committed fixture F8b now
                          covers the closing-fence length rule (a bare
                          shorter run inside a longer fence is content)

v3 findings carried over: MULTIPLE-ANNOTATIONS, RECORD-SHA-MISMATCH,
INERT-CORRECTION, CORRECTION-IN-FENCE, DELETED-LINES,
ZONE-TOKEN-STRADDLES-EDGE, BOGUS-RECOMPUTED, UNFILED-SOURCES-ANNOTATION,
SOURCES-RECOMPUTE-MISMATCH.

Named limits (disclosed, not fixed): the zone stays frozen at 32 chars and a
token wholly beyond it is still not an annotation (and still forces exit 2
when no other annotation exists on the line); the SOURCES scan is line-based
and exempts lines carrying a path:line pointer (a dot before the colon and a
digit after it — a ratio such as 2.5:1 still exempts, ERRATUM-R55-2);
annotations whose pair does not exceed the current count are
historical notes the instrument does not re-derive; pair annotations in files
other than LOG.md and corpus/README.md are invisible to the instrument; the
registry's append-only monotonicity is assumed; CR-only line endings (no LF)
are one line to this counter; the HTML comment class stays the line-level
`<!--`/`-->` grammar, not full CommonMark HTML blocks (the v5 opener must begin the
line with at most three leading spaces; closer lines and one-line comments keep the loose
line-level rule; a line whose prose merely mentions `<!--` still opens a
region — the real lane's own SCORECARD.md hides its tail this way, disclosed);
a fence-closer line is rstripped, so exotic separators after the closing run
(VT, FF, NEL) still close it in this grammar (CommonMark allows only spaces
and tabs — routed A09-A13, not instrumented in v5); the finding-id
precedence inside one correction is INERT, then BOGUS, then IN-FENCE; the
deletion check parses numstat on LF only, and a monitored path is a fixed
ASCII constant here, so the quotePath record-split shape is parser-hardening
with a differential receipt, not a reachable lane verdict.

Exit 0: every check holds. Exit 1: any finding.
Exit 2: could-not-evaluate (bad CLI, missing file, zero or duplicate anchor
line, no annotation in the zone, a flagged filing without pinned source revs).
Reads committed bytes only (git show / git diff --numstat) with a scrubbed
environment and fsmonitor/hooks neutralized; writes nothing outside --work
(selftest only). No network.

Selftest: --selftest --work DIR [--expected TSV] [--builder-sha256 HEX]
[--expected-sha256 HEX] builds the synthetic fixture repos
(fixtures/build-fixtures.py, same directory), runs every C1 fixture, and
asserts exit code + finding-id against the committed expected file
(records/c1-selftest-expected.tsv by default). When the pin arguments are
given the builder and expected bytes are verified BEFORE exec (the r53
sentinel S4 routed fix); a mismatch is CANNOT-EVALUATE. --scratch is an
alias of --work (the r54 sentinel S6 routed fix: the argument steers writes).
"""
import argparse
import hashlib
import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ANCHOR = 'grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv'
RECORD = 'census/round-51/records/ws-drift-vs-r46.tsv'
SITES = ['SCORECARD.md', 'census/round-51/preregistration.txt']
CORR_FILE = 'SCORECARD.md'
ZONE = 32
CORR_RE = re.compile(r'^ {0,3}(?:<!--\s*)?R52-CORRECTION (\S+):(\d+) stale=(\d+) recomputed=(\d+)(?:\s*-->)?\s*$', re.M)
CORR2_RE = re.compile(r'^ {0,3}(?:<!--\s*)?R53-CORRECTION (\S+):(\d+) stale=(\d+)->(\d+) recomputed=(\d+)->(\d+)(?:\s*-->)?\s*$', re.M)
ANNOT_RE = re.compile(r'(?:→|\()\s*(\d+)')
PAIR_ANNOT_RE = re.compile(r'(\d+)\s*(?:->|→)\s*(\d+)(?:\s+rows?\b)?')
PTR_RE = re.compile(r'(?:[A-Za-z0-9_.\-]+/)*[A-Za-z0-9_.\-]+\.[A-Za-z0-9]{1,5}:\d')
REG_ROW_RE = re.compile(r'^\|[ \t]*S[0-9]{3,}[ \t]*\|', re.M)
PAIR_SITES = ['LOG.md', 'corpus/README.md']
DEFAULT_EXPECTED = HERE / 'records' / 'c1-selftest-expected.tsv'
BUILDER = HERE / 'fixtures' / 'build-fixtures.py'


def git_env():
    return {
        'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LC_ALL': 'C',
        'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
        'GIT_CONFIG_SYSTEM': os.devnull, 'GIT_NO_REPLACE_OBJECTS': '1',
        'GIT_OPTIONAL_LOCKS': '0', 'GIT_NO_LAZY_FETCH': '1',
        'GIT_TERMINAL_PROMPT': '0',
    }


def git(root, *args):
    e = git_env()
    p = subprocess.run(['git', '-C', str(root),
                        '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=/dev/null']
                       + list(args), capture_output=True, env=e, timeout=120)
    return p


def git_show(root, rev, path):
    p = git(root, 'show', '%s:%s' % (rev, path))
    if p.returncode:
        return None
    return p.stdout


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hidden_lines(text: str):
    """1-based line numbers hidden from correction filing (one line model:
    lines are counted by LF only — the same numbering the correction's own
    line number uses, closing the r54 sentinel S1 splitlines divergence).
    Hidden: fenced code blocks per the CommonMark 0.31.2 start conditions
    (backtick or tilde; at most three leading spaces of indentation — four
    spaces is an indented code block, not a fence; a backtick fence's info
    string may not contain a backtick; the closing fence must be the same
    character, at most three spaces indented, and at least as long as the
    opening one — parity) and HTML comment regions (`<!--` ... `-->`; the
    opener must BEGIN the line (CommonMark HTML block start condition 2: the
    line begins with `<!--`, at most three leading spaces) — a four-space
    indent is code (the r55 sentinel S55-S2 repair), and a prose sentence that
    mentions `<!--` mid-line opens no region (v5 F29 repair: v4 hid every line
    after such a sentence); a one-line comment hides only its own line)."""
    hidden = set()
    in_html = False
    fence = None  # (char, min_length)
    for i, raw in enumerate(text.split('\n'), 1):
        indent = len(raw) - len(raw.lstrip(' '))
        ln = raw.lstrip(' ')
        stripped = ln.rstrip()
        if in_html:
            hidden.add(i)
            if '-->' in ln:
                in_html = False
            continue
        if fence is not None:
            ch, n = fence
            if indent <= 3:
                body = stripped.rstrip(' ')
                if body and set(body) == {ch} and len(body) >= n:
                    fence = None  # closing fence line itself is not hidden content
                    continue
            hidden.add(i)
            continue
        if indent <= 3:
            m = re.match(r'(`{3,}|~{3,})(.*)$', stripped)
            if m and not (m.group(1)[0] == '`' and '`' in m.group(2)):
                fence = (m.group(1)[0], len(m.group(1)))
                continue
        if indent <= 3 and stripped.startswith('<!--'):
            hidden.add(i)
            if '-->' not in ln.split('<!--', 1)[1]:
                in_html = True
            continue
    return hidden


def line_zones(ln: str, anchor: str):
    """Per-occurrence (ok_tokens, straddle) for the frozen zone after EVERY
    occurrence of the anchor on the line (the r54 reviewer R2 routed fix:
    a second annotated anchor must be judged, never aliased). A token wholly
    beyond the zone is still not an annotation (named limit); a token that
    starts inside the zone and ends beyond it straddles the edge."""
    zones = []
    start = 0
    while True:
        idx = ln.find(anchor, start)
        if idx < 0:
            break
        after = ln[idx + len(anchor):]
        ok, straddle = [], False
        for m in ANNOT_RE.finditer(after):
            if m.start() >= ZONE:
                continue  # wholly outside the frozen zone (named limit)
            if m.end(1) > ZONE:
                straddle = True
            else:
                ok.append(int(m.group(1)))
        zones.append((ok, straddle))
        start = idx + 1
    return zones


def registry_count(blob: bytes) -> int:
    return len(REG_ROW_RE.findall(blob.decode('utf-8', 'replace')))


def numstat_deletions(root, base, rev, paths):
    """[(path, deletions)] for the named paths between base and rev.
    deletions is an int, or None for a binary numstat entry (`-` columns —
    refused by name by the caller, the r55 sentinel S55-S1 routed fix; v4
    read it as -1). The output splits on LF only: a repository-local
    core.quotePath=false can put a raw NEL in a path record and splitlines()
    tore the record apart (r55 named limit, probe receipt
    probe-numstat-quotepath.txt)."""
    p = git(root, 'diff', '--numstat', '--no-renames', '%s..%s' % (base, rev), '--', *paths)
    if p.returncode:
        return None
    out = []
    for ln in p.stdout.decode('utf-8', 'replace').split('\n'):
        if not ln:
            continue
        f = ln.split('\t')
        if len(f) != 3:
            continue
        adds, dels, path = f
        out.append((path, None if dels == '-' else int(dels)))
    return out


def measure(root, rev, base, record_sha, sources_before, sources_after, out):
    """Run the amended measurement; return exit code. Findings print as FINDING lines."""
    findings = []

    def finding(fid, detail):
        findings.append((fid, detail))
        out.append('FINDING %s %s' % (fid, detail))

    record = git_show(root, rev, RECORD)
    if record is None:
        out.append('CANNOT-EVALUATE record absent at %s: %s' % (rev[:12], RECORD))
        return 2
    record_sha_obs = sha256(record)
    record_sha_ok = record_sha_obs == record_sha
    if not record_sha_ok:
        finding('RECORD-SHA-MISMATCH', 'pinned=%s observed=%s' % (record_sha[:12], record_sha_obs[:12]))
    recomputed = sum(1 for ln in record.decode('utf-8', 'replace').split('\n') if ln.startswith('ADDED'))

    registry = git_show(root, rev, 'corpus/SOURCES.md')
    registry_rows = registry_count(registry) if registry is not None else None

    corr_b = git_show(root, rev, CORR_FILE)
    if corr_b is None:
        out.append('CANNOT-EVALUATE %s absent at rev' % CORR_FILE)
        return 2
    if b'\x00' in corr_b:
        # v5 (r55 sentinel S55-S1, silent shape): a NUL byte makes the correction
        # file's lines unreadable to the line lexer; a bogus correction behind a
        # NUL was silently unjudged on an unchanged file (v4 exit 0). Refuse by name.
        finding('CORRECTION-FILE-BINARY', '%s carries NUL bytes; correction lines cannot be lexed' % CORR_FILE)
    corr = corr_b.decode('utf-8', 'replace')
    corr_tuples = []
    for m in CORR_RE.finditer(corr):
        corr_line_no = corr.count('\n', 0, m.start()) + 1
        corr_tuples.append((m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4)), corr_line_no))
    pair_filings = {}
    for m in CORR2_RE.finditer(corr):
        fline = corr.count('\n', 0, m.start()) + 1
        pair_filings.setdefault((m.group(1), int(m.group(2))), []).append(
            (int(m.group(3)), int(m.group(4)), int(m.group(5)), int(m.group(6)), fline))
    hidden = hidden_lines(corr)

    site_text, site_zone_stated, zone_multi, zone_straddle = {}, {}, [], []
    zone_alias = 0
    for path in SITES:
        tb = git_show(root, rev, path)
        if tb is None:
            out.append('CANNOT-EVALUATE site absent: %s' % path)
            return 2
        text = tb.decode('utf-8', 'replace')
        site_text[path] = text
        lines = text.split('\n')
        hits = [i for i, ln in enumerate(lines) if ANCHOR in ln]
        if len(hits) != 1:
            out.append('CANNOT-EVALUATE anchor count %d in %s (want 1)' % (len(hits), path))
            return 2
        ln = lines[hits[0]]
        zones = line_zones(ln, ANCHOR)
        stated = None
        alias_fired = False
        for k, (ok_tokens, straddle) in enumerate(zones):
            if straddle:
                finding('ZONE-TOKEN-STRADDLES-EDGE',
                        '%s line %d a count token starts inside the %d-char zone and ends beyond it'
                        % (path, hits[0] + 1, ZONE))
                zone_straddle.append(path)
                continue
            if not ok_tokens:
                if k == 0 and len(zones) == 1:
                    out.append('CANNOT-EVALUATE no annotation in zone at %s' % path)
                    return 2
                continue  # a later occurrence with no annotation is not an annotation
            if len(ok_tokens) > 1:
                finding('MULTIPLE-ANNOTATIONS', '%s line %d zone tokens %s'
                        % (path, hits[0] + 1, ','.join(str(t) for t in ok_tokens)))
                zone_multi.append(path)
                continue
            tok = ok_tokens[0]
            if stated is None:
                stated = tok
            elif tok != stated:
                zone_alias += 1
                alias_fired = True
                finding('ANCHOR-ALIAS-MISMATCH',
                        '%s line %d anchor occurrence %d reads %d, occurrence 1 reads %s'
                        % (path, hits[0] + 1, k + 1, tok, stated))
        if stated is None and not zone_straddle and not alias_fired and not zone_multi:
            out.append('CANNOT-EVALUATE no annotation in zone at %s' % path)
            return 2
        site_zone_stated[path] = (hits[0] + 1, stated)

    filed_paths = {t[0] for t in corr_tuples}
    inert = fenced = bogus = 0
    for (cpath, cline, stale, m_val, corr_no) in corr_tuples:
        bad = None
        if cpath not in SITES:
            bad = 'names non-site path %s' % cpath
        else:
            lines = site_text[cpath].split('\n')
            if cline < 1 or cline > len(lines):
                bad = 'line %d absent in %s' % (cline, cpath)
            else:
                ln = lines[cline - 1]
                if ANCHOR not in ln:
                    bad = 'line %d of %s carries no anchor' % (cline, cpath)
                else:
                    zones = line_zones(ln, ANCHOR)
                    ok_tokens, straddle = zones[0] if zones else ([], False)
                    if straddle:
                        bad = 'line %d of %s annotation token straddles the zone edge' % (cline, cpath)
                    elif len(ok_tokens) != 1:
                        bad = 'line %d of %s annotation count %d' % (cline, cpath, len(ok_tokens))
                    else:
                        stated = ok_tokens[0]
                        if stated != stale or stale == m_val:
                            bad = 'line %d of %s reads %d, correction claims stale=%d recomputed=%d' % (
                                cline, cpath, stated, stale, m_val)
        if bad is not None:
            inert += 1
            finding('INERT-CORRECTION', '%s:%d %s' % (cpath, cline, bad))
        elif m_val != recomputed:
            bogus += 1
            finding('BOGUS-RECOMPUTED', '%s:%d recomputed=%d but record count is %d'
                    % (cpath, cline, m_val, recomputed))
        if corr_no in hidden:
            fenced += 1
            finding('CORRECTION-IN-FENCE', 'correction at %s:%d (site %s:%d)' % (CORR_FILE, corr_no, cpath, cline))

    dels = numstat_deletions(root, base, rev, [RECORD] + SITES + [CORR_FILE] + PAIR_SITES)
    if dels is None:
        out.append('CANNOT-EVALUATE numstat failed')
        return 2
    deleted = [(p, d) for (p, d) in dels if d is None or d != 0]
    for (p, d) in deleted:
        if d is None:
            finding('DELETIONS-UNREADABLE-BINARY',
                    '%s deletions unreadable (binary numstat entry) between %s..%s'
                    % (p, base[:12], rev[:12]))
        else:
            finding('DELETED-LINES', '%s deletions=%s between %s..%s' % (p, d, base[:12], rev[:12]))

    # The 274->275 class: SOURCES-pair annotations that overstate the registry.
    log_unfiled = log_recomp = pairinert = pairhidden = 0
    for path in PAIR_SITES:
        tb = git_show(root, rev, path)
        if tb is None:
            continue  # absent file: nothing to scan
        ptext = tb.decode('utf-8', 'replace')
        phidden = hidden_lines(ptext)
        for i, ln in enumerate(ptext.split('\n'), 1):
            if i in phidden:
                continue  # r54 reviewer R6 routed fix: fenced examples are not annotations
            if 'corpus/SOURCES.md' not in ln or PTR_RE.search(ln):
                continue
            m = PAIR_ANNOT_RE.search(ln)
            if not m:
                continue
            a, b = int(m.group(1)), int(m.group(2))
            if registry_rows is None or max(a, b) <= registry_rows:
                continue  # historical note within the registry's reach: out of scope
            fil_all = pair_filings.get((path, i)) or []
            for f in fil_all:
                if (f[0], f[1]) != (a, b):
                    pairinert += 1
                    finding('PAIR-FILING-INERT',
                            '%s:%d filing stale=%d->%d does not match the annotated pair %d->%d'
                            % (path, i, f[0], f[1], a, b))
            # v5 (r55 N1/D14/D15): only a VISIBLE filing files the annotation.
            fil = [f for f in fil_all if f[4] not in hidden]
            match = [f for f in fil if (f[0], f[1]) == (a, b)]
            if not fil or not match:
                log_unfiled += 1
                finding('UNFILED-SOURCES-ANNOTATION',
                        '%s:%d claims %d -> %d rows but the registry holds %d; no pair-form filing names it'
                        % (path, i, a, b, registry_rows))
                if any((f[0], f[1]) == (a, b) for f in fil_all):
                    pairhidden += 1
                    finding('PAIR-FILING-HIDDEN',
                            '%s:%d matching filing sits in a hidden line (fence or comment); it does not file'
                            % (path, i))
                continue
            if sources_before is None or sources_after is None:
                out.append('CANNOT-EVALUATE flagged filing at %s:%d needs --sources-rev-before/after'
                           % (path, i))
                return 2
            want = []
            for r in (sources_before, sources_after):
                rb = git_show(root, r, 'corpus/SOURCES.md')
                if rb is None:
                    out.append('CANNOT-EVALUATE sources revision absent: %s' % r[:12])
                    return 2
                want.append(registry_count(rb))
            for f in match:
                if (f[2], f[3]) != (want[0], want[1]):
                    log_recomp += 1
                    finding('SOURCES-RECOMPUTE-MISMATCH',
                            '%s:%d filing recomputed=%d->%d but the census grep recomputes %d->%d'
                            % (path, i, f[2], f[3], want[0], want[1]))

    mism, filed = 0, 0
    for path in SITES:
        s_line, stated = site_zone_stated[path]
        if stated is None:
            continue  # straddling site: already refused above
        status = 'match' if stated == recomputed else 'mismatch'
        tup = (path, s_line, stated, recomputed)
        # A hidden correction neither files nor passes (CORRECTION-IN-FENCE);
        # filedness looks at the correction's own line number.
        corr_nos = [t[4] for t in corr_tuples if t[:4] == tup]
        is_filed = bool(corr_nos) and all(n not in hidden for n in corr_nos)
        if status == 'mismatch':
            mism += 1
            if is_filed:
                filed += 1
        out.append('SITE path=%s line=%d stated=%d recomputed=%d status=%s filed=%s'
                   % (path, s_line, stated, recomputed, status, 'yes' if is_filed else 'no'))
    unfiled = mism - filed
    out.append('SUMMARY sites=%d mismatches=%d filed=%d unfiled=%d record_sha=%s appended=%s '
               'multi=%d inert=%d fenced=%d straddle=%d bogus=%d logunfiled=%d logrecomp=%d '
               'alias=%d pairinert=%d pairhidden=%d recomputed=%d rev=%s base=%s'
               % (len(SITES), mism, filed, unfiled,
                  'ok' if record_sha_ok else 'MISMATCH',
                  'ok' if not deleted else 'DELETED',
                  len(zone_multi), inert, fenced, len(zone_straddle), bogus,
                  log_unfiled, log_recomp, zone_alias, pairinert, pairhidden,
                  recomputed, rev[:12], base[:12]))
    if findings or unfiled > 0:
        return 1
    return 0


def load_builder():
    if not BUILDER.exists():
        return None
    spec = importlib.util.spec_from_file_location('r54fixtures', BUILDER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_selftest(work: Path, expected_path: Path, out, builder_sha=None, expected_sha=None):
    if builder_sha is not None and sha256(BUILDER.read_bytes()) != builder_sha:
        out.append('CANNOT-EVALUATE PIN-MISMATCH builder sha256 %s != pinned %s'
                   % (sha256(BUILDER.read_bytes()), builder_sha))
        return 2
    if expected_sha is not None and sha256(expected_path.read_bytes()) != expected_sha:
        out.append('CANNOT-EVALUATE PIN-MISMATCH expected sha256 %s != pinned %s'
                   % (sha256(expected_path.read_bytes()), expected_sha))
        return 2
    mod = load_builder()
    if mod is None:
        out.append('CANNOT-EVALUATE builder missing: %s' % BUILDER)
        return 2
    fdir = work / 'c1-fixtures'
    fdir.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name in mod.C1_FIXTURES:
        info = mod.build_one(name, fdir)
        manifest[name] = info
    exp = {}
    for row in expected_path.read_text().splitlines()[1:]:
        if not row.strip():
            continue
        f = row.split('\t')
        exp[f[0]] = (int(f[1]), f[2] if len(f) > 2 else '')
    ok = True
    for name in mod.C1_FIXTURES:
        info = manifest[name]
        buf = []
        base = info['tip'] if name not in ('F5-REWRITE', 'F6-RECORD-DRIFT',
                                           'F27-BINARY-NUMSTAT') else info['base']
        srevs = info.get('sources_revs') or (None, None)
        rc = measure(Path(info['dir']), info['tip'], base, info['record_sha256'],
                     srevs[0], srevs[1], buf)
        want_rc, want_find = exp.get(name, (None, ''))
        got_find = next((ln.split(' ')[1] for ln in buf if ln.startswith('FINDING ')), '')
        passed = (rc == want_rc) and (want_find in ('', '-') or got_find == want_find)
        ok = ok and passed
        out.append('SELFTEST-CASE %s %s rc=%d want_rc=%s finding=%s want_finding=%s'
                   % (name, 'pass' if passed else 'fail', rc, want_rc, got_find or '-', want_find or '-'))
    out.append('SELFTEST %s cases=%d' % ('pass' if ok else 'fail', len(mod.C1_FIXTURES)))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root')
    ap.add_argument('--rev')
    ap.add_argument('--base')
    ap.add_argument('--record-sha256', dest='record_sha')
    ap.add_argument('--sources-rev-before', dest='sources_before', default=None)
    ap.add_argument('--sources-rev-after', dest='sources_after', default=None)
    ap.add_argument('--scratch', default=None,
                    help='alias of --work (r54 sentinel S6 routed fix: the argument steers writes)')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--work', default=None)
    ap.add_argument('--expected', default=None)
    ap.add_argument('--builder-sha256', dest='builder_sha', default=None)
    ap.add_argument('--expected-sha256', dest='expected_sha', default=None)
    ns = ap.parse_args()
    out = []
    if ns.selftest:
        work = ns.work or ns.scratch
        if not work:
            print('CANNOT-EVALUATE --selftest requires --work (or --scratch)', file=sys.stderr)
            return 2
        exp = Path(ns.expected) if ns.expected else DEFAULT_EXPECTED
        rc = run_selftest(Path(work), exp, out, ns.builder_sha, ns.expected_sha)
    else:
        missing = [a for a, v in (('--root', ns.root), ('--rev', ns.rev),
                                  ('--base', ns.base), ('--record-sha256', ns.record_sha)) if not v]
        if missing:
            print('CANNOT-EVALUATE missing required args: %s' % ', '.join(missing), file=sys.stderr)
            return 2
        if not re.fullmatch(r'[0-9a-f]{40}', ns.rev) or not re.fullmatch(r'[0-9a-f]{40}', ns.base):
            print('CANNOT-EVALUATE full 40-hex revisions required', file=sys.stderr)
            return 2
        if not re.fullmatch(r'[0-9a-f]{64}', ns.record_sha):
            print('CANNOT-EVALUATE record pin must be 64-hex', file=sys.stderr)
            return 2
        for name, val in (('sources-rev-before', ns.sources_before), ('sources-rev-after', ns.sources_after)):
            if val is not None and not re.fullmatch(r'[0-9a-f]{40}', val):
                print('CANNOT-EVALUATE %s must be a full 40-hex revision' % name, file=sys.stderr)
                return 2
        rc = measure(Path(ns.root).resolve(), ns.rev, ns.base, ns.record_sha,
                     ns.sources_before, ns.sources_after, out)
    print('\n'.join(out))
    return rc


if __name__ == '__main__':
    sys.exit(main())
