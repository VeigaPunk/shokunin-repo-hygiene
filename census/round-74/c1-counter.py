#!/usr/bin/env python3
"""c1-counter.py — souji round-74 C2 counter (L1-built, committed after the r74 freeze bcdf2d16).

Round 74 (successor of census/round-73/c1-counter.py; the frozen r73 counter is NOT amended — Q131):

  * C2 calibration — row-specific forgery witness (r73 routed a / S73ExecC2; r73 lesson M2). The r73
    witness credited a row with ANY worktree divergence, and FWw/FC1/FC2 set-up always writes
    `.gitattributes`, so a row whose forgery was removed still read witnessed. The divergence lists are
    now scoped to the row's forged paths (forge_paths: the row's `target`, else the path its in-run kind,
    `chmod_notes` or `index_stat` writes — preregistration.txt C2) before the witness is decided; a row
    with no forged path is unwitnessed (fail closed). base_forgeries now counts witnessed base forgeries
    only (r73 routed e); an unwitnessed one counts in base_unwitnessed alone.
  * claim_upheld also requires new_unwitnessed=0 (S73MutCounter F2 / M17).
  * Selftest section (11) kills the r73 survivors: a failed witness read is unwitnessed in evaluate()
    (M08), a retargeted tracked symlink is a `target` divergence (M14), a gitlink with its directory
    present is no divergence (M15), and the (9a) witness run asserts base/new_unwitnessed=0 (M17); plus
    row_scope/forge_paths checks.

Round 73 text (carried; describes the r73 duties this file still performs):

Round 73 (successor of census/round-72/c1-counter.py; the frozen r72 counter is NOT amended — Q131):

  * C2 calibration — forgery witness (r72 routed D4 / S72MutCounter MF: a refuse row was credited as a
    forgery without any check that its fixture forged). For every row and both slots the counter now
    computes the divergence of the fixture worktree from the row's revision (tree_divergence: `git
    ls-tree -r` entries vs the worktree — missing path, wrong type, wrong exec bit, different raw bytes,
    different symlink target — plus worktree files outside the tree, `.git` excluded; no git status, no
    stat cache, no filter), once before the slot runs and once after. A refuse row a slot accepts with no
    divergence at either point is unwitnessed: CASE lines print base_witness= / new_witness=, SUMMARY
    prints base_unwitnessed= and new_unwitnessed=, claim_upheld requires base_unwitnessed=0, and the
    battery classifier counts an accepted refuse row as a forgery only when witnessed (an unwitnessed
    one is `error`). Selftest section (10) exercises the witness.
  * C1 operability rows (r72 routed D3 / S72Sentinel HIGH, index stat-cache forgery; racy-git.adoc S315,
    git-hash-object(1) S316): FX1 in-run forge of tools/counter.py with its index stat entry rewritten,
    FX2 the same before the run, FX3 the same on the instrument in-run — each `refuse
    RECEIPT-WORKTREE-STAT-CONCEALED`, base_expect `accept`; FXh an honest stale-stat file (mtime +10 s,
    bytes unchanged) and FXc an honest core.autocrlf=true CRLF file re-staged by the fixture — `accept`.
  * r72 spot-check D2: the round-72 text below said FWw's "status reads the worktree file, S314"; S314
    states only the fallback order outside checkout. Corrected in this file's copy of that text.

Round 72 text (carried; describes the r72 duties this file still performs):

Round 72 (successor of census/round-71/c1-counter.py; the frozen r71 counter is NOT amended — Q131):

  * Base-slot binding (C1, r71 routed D2 / S71MutCounter F1). The matrix gains a fourth column,
    `base_expect`: the frozen verdict of the declared reference-weak base writer (the writer at
    --base-rev; for r72 8b9345b1, the pre-r71 writer). Carried rows take the base verdicts printed
    in census/round-71/records/c1-after.txt; the five FW rows take `accept` (pre-freeze probe
    census/round-72/probes/fw-shapes-probe.txt). Every row whose base verdict differs from its
    base_expect counts in `base_mismatches`; SUMMARY prints it and claim_upheld requires 0, so a
    fixture that stops forging the weak base (S71MutCounter Y4/Y6/Y10: base_forgeries 7 -> 2 or 5
    with EXIT=0 under r71) now fails the verdict. Battery MUTANT lines print it; the battery rc
    does not read it (C2 stays separable).
  * Selftest section (9) (C1): (9a) a base witness — the seven r71 forging rows (AS1 AS2 FC1 FC2 FC3
    FM1 FM2) are rebuilt and run against the base writer, and each base verdict must equal its
    base_expect (kills Y4 Y6 Y10); (9b) claim_upheld is false on one base mismatch; (9c) a member
    name with a path separator alone (`sub/M1`) is refused by the name rule (Y1); (9d) a SHA256SUMS
    line naming a dot-file without a separator is refused as non-plain (Y9); (9e) clean_env scrubs
    every name of its scrub tuple, not only the pathspec variables (Z1, S71CriticClaims).
  * C2 coverage: five rows appended (FWr FWi FWp FWw FWs), each `refuse RECEIPT-FILTER-DRIVER-SET`
    with base_expect `accept`: FWr a pre-run forgery under a configured driver whose wrapped command
    restores the bytes and unsets the driver (only the pre-run witness sees it); FWi an honest tree
    whose wrapped command forges same-size bytes and creates the attribute and driver (only the
    post-run witness sees it); FWp a `filter.<d>.process` long-running driver (gitattributes(5)
    "Long Running Filter Process", S313); FWw a committed empty .gitattributes whose worktree copy
    filters itself back to empty and assigns the forging driver (the index copy carries no filter:
    git-check-attr(1) --cached, S312; outside checkout the worktree .gitattributes is read and the index
    copy is only a fall-back, S314 — corrected in r73 from "status reads the worktree file"); FWs a driver literally
    named `set`.

Round 71 text (carried; describes the r71 duties this file still performs):

Round 71 (successor of census/round-70/c1-counter.py; the frozen r70 counter is NOT amended — Q131):

  * C1 operability (writer surface): the 59 r70 rows are carried unchanged and 11 attribute /
    core.fileMode rows are appended (S70Sentinel F1/F2, routed r71). A clean filter driver
    (`filter.<driver>.clean`, gitattributes(5) "filter") that maps size-preserving forged bytes
    back to the committed bytes makes `git status` report a clean tree; the attribute can come from
    a caller-injected GIT_ATTR_SOURCE tree (AS1/AS2), a committed .gitattributes (FC1/FC2) or
    $GIT_DIR/info/attributes (FC3). A repository-local core.fileMode=false hides a mode flip made
    before (FM1) or during (FM2) the run. ASh/FCh/FCh2/FMh are the honest rows: an attribute source
    with no filter, a filter attribute with no configured driver, a configured driver no tracked
    path carries, and core.fileMode=false over an unchanged tree. Forged bytes are size-preserving
    (`counter v2` for the committed `counter v1`): a size change is caught by the stat check before
    any clean filter runs (pre-freeze probe census/round-71/probes/attr-filemode-probe-base.txt).
  * C2 calibration (instrument self-check): the selftest gains section (8), which asserts the
    behaviours the five r70-surviving counter mutants X6-X10 (S70MutCounter, frozen in
    census/round-71/c2-mutants.json) remove: the battery error gate, the ambient pathspec scrub of
    clean_env, the row pathspec_env merge of case_env, and the SHA256SUMS duplicate- and
    malformed-line checks. Battery member names are validated (no path separator, no leading dot;
    S70Sentinel F3/F4) and the SHA256SUMS listing must name the member file exactly.

Round 70 text (carried; describes the r70 duties this file still performs):

Round 70 (successor of census/round-69/c1-counter.py; the frozen r69 counter is NOT amended — Q131):

  * C1 operability (writer surface): the 47 r69 rows are carried unchanged and 12 pathspec-env rows
    are appended. Each new row carries a caller env (`pathspec_env` in CASE_SPECS) setting one of
    GIT_LITERAL_PATHSPECS / GIT_GLOB_PATHSPECS / GIT_NOGLOB_PATHSPECS / GIT_ICASE_PATHSPECS to 1.
    git(1) OPTIONS: `--literal-pathspecs` = "no globbing, no pathspec magic", equivalent to
    GIT_LITERAL_PATHSPECS=1 (S304). Under it the writer's `:(top)` reads become a literal path that
    matches nothing, `ls-files -v` prints nothing with rc 0, and every flag check passes vacuously
    (probed 2026-11-06, census/round-70/probes/lp-ls-files-probe.txt). Rows LD LN4 LU1 LG1 LA9
    re-run D N4 U1 G1 A9 under GIT_LITERAL_PATHSPECS=1 (expected class unchanged); LA is the honest
    clean row under it (accept: a refuse-on-presence writer is over-refusal, not a fix); GA/GD,
    NGA/NGD and ICA/ICD are the honest and skip-worktree rows under the other three variables.
  * C2 calibration (instrument self-check): the selftest gains section (7) — full Q131 precedence
    (forgery outranks over-refusal and echo; error outranks forgery), the D30 echo judge on
    synthetic inputs, and the pure battery verdict (an expectation mismatch and a survived mutant
    each make rc 1). The battery arm verifies every selected member against `SHA256SUMS` in the
    battery dir before any run (missing, unlisted or mismatched member: rc 2) and binds each
    member's sha256 into its MUTANT line (r69 routed F-3).
  * clean_env additionally drops the four pathspec variables, GIT_TEMPLATE_DIR, GIT_ATTR_SOURCE,
    GIT_EXEC_PATH and GIT_DEFAULT_HASH from the ambient environment (r69 routed: S69Sentinel F-1/F-2,
    S69ExecAmbient); a row's own caller env is applied after the scrub, so the C1 rows still reach
    the writer slots.

Round 69 text (carried; describes the r69 duties this file still performs):

Successor of census/round-68/c1-counter.py (its 42 rows are carried as regression rows; the frozen
r68 counter is NOT amended — QUALITY Q131). Three frozen duties ride in this file:

  * C1 calibration battery arm (Q131 outcome split): `--battery-manifest FILE` runs the whole frozen
    matrix once per listed mutant and classifies each mutant's refutation OUTCOME from the CASE rows:
    forgery (a receipt written over a refused state), echo-violation (a refusal message printed a
    caller value that the row's noecho field forbids), over-refusal (a refusal over an accepted
    honest state), label-only (refused with a different class), survived, error. Only forgery-based
    refutations count as declared-protection kills; label-only, over-refusal and echo-violation
    refutations are reported on their own lines and never folded into the kill count. BATTERY
    EXIT=0 iff every mutant's observed outcome equals its manifest expectation, and no mutant
    survives and no row errors.

  * C2 clean environment (sentinel MEDIUM-1 r68): clean_env scrubs HOME, XDG_CONFIG_HOME and every
    GIT_TRACE* variable from the ambient environment, and pins GIT_CONFIG_GLOBAL to the null device
    and GIT_CONFIG_NOSYSTEM=1 on the counter's own git calls, so no host git config can steer
    fixture builds, the regress fixture, or a writer slot. The r68 tuple (GIT_DIR, GIT_WORK_TREE,
    GIT_INDEX_FILE, object redirects, GIT_CONFIG_*, GIT_NO_REPLACE_OBJECTS, GIT_COMMON_DIR,
    GIT_NAMESPACE, GIT_CEILING_DIRECTORIES) is unchanged. The frozen ambient comparison arm adds
    HOME/XDG_CONFIG_HOME/GIT_TRACE* hostility to the r68 tuple (round-68 routed item 3).

  * C2 selftest emit path (round-68 M2): the selftest calls main() on a two-row restricted matrix
    (synthetic TSV over CASE_ORDER[:2]) and asserts the header, slot, matrix, SUMMARY and EXIT lines
    are all emitted, so an emit-path crash after evaluation cannot pass as green.

Matrix (c1-matrix.tsv, 47 rows; CASE_SPECS must cover exactly these rows, in this order):
  A..PK7h — the 42 r68 rows, carried with ONE frozen fixture repair (Q132): W4's poisoned copy is
    now built at `<fixture>/main/main/.git` — the directory its relative caller value `main/.git`
    actually names from the writer's parent cwd — instead of the r68 copy at `<fixture>/main/main`
    that resolved to no directory. The honest writer keeps refusing W4 with `lane worktree is
    dirty` (the value check passes: the cwd-resolved value IS the real common dir; the scrub keeps
    every writer git call on the real repository). The rebuild changes what the row MEASURES: the
    r68 fixture's base slot refused W4 for an unrelated reason (the rev check failed inside the
    broken shape: "rev is not a commit object ... not a git repository", r68 M3), so the base's
    redirect-honoring was unmeasured there; the rebuilt fixture makes the base ACCEPT — a third
    base forgery (W1, W2, W4) — while the mutant W4 label flips (M-CD-SCRUB, M-CD-ROOTREL,
    M-CD-NCRAW, via the failing `rev-parse --git-common-dir` resolution call) and the honest
    candidate's verdict are unchanged from r68. All three arms are pinned in the committed r68
    records (census/round-68/records/c1-after/CAND.txt, M-CD-SCRUB.txt) and this round's battery
    receipt.
  Then the five r69 rows (from the 14 unbattered declared protections of `S68ScoutDeclared`,
    census/round-68/records/wave-w1/seats/S68ScoutDeclared/declared-protections.tsv):
  * U1  unmerged-index-forged      refuse  RECEIPT-INDEX-UNMERGED (two conflicting stages on
                                           tools/notes.txt via update-index --index-info; the flag
                                           check classes the U tag before the dirty check)
  * G1  gitlink-concealed          refuse  RECEIPT-GITLINK-CONCEALED (a 160000 gitlink entry on
                                           tools/sub, committed, then skip-worktree; status hides it)
  * A9  concealed-absent           refuse  RECEIPT-INDEX-CONCEALED-ABSENT (skip-worktree on
                                           tools/notes.txt whose worktree file is removed)
  * F1  fsmonitor-silenced-dirty   refuse  lane worktree is dirty (repo config core.fsmonitor=<
                                           timestamp-printing silent hook> plus --fsmonitor-valid;
                                           the writer's -c core.fsmonitor=false pin sees the dirty
                                           append; D19)
  * W7  git-dir-redirect-hides-mode refuse lane worktree is dirty (GIT_DIR points at a copy of .git
                                           whose config sets core.fileMode=false and names the
                                           fixture repo as core.worktree; the GIT_DIR scrub keeps
                                           the dirty check on the real repository; D21)
  D18 (GIT_OPTIONAL_LOCKS=0) has no row: designed (an index.lock holder), probed, and removed
  before the freeze — git status attempts no optional index-write lock under a held index.lock,
  so the pin has no honest single-edit row; it is a named limit in
  census/round-69/records/declared-coverage.tsv.

No-echo judge (D30): the W/N rows that carry a caller value also freeze `noecho_env` in CASE_SPECS;
a new-slot refusal whose stderr contains that exact caller value is an echo violation, counted in
`echo_violations` and required zero by the claim, and classified echo-violation in the battery arm.
N3/P13 freeze GIT_INDEX_FILE; W1/W2/W3/W4/W5/W6 freeze GIT_COMMON_DIR; W7 freezes GIT_DIR.

D30 mutant (census/round-69/mutate-writer.py): the INDEX-ENV refusal message echoes the caller's
GIT_INDEX_FILE; the N3/P13 noecho rows classify it echo-violation.

The base writer at the round base (3639087917eaeb28719d7603110a6ec22782100e, the round-66 LANDED
candidate) is unchanged from r68 except through the fixture repairs: the rebuilt W4 gives the base
one more forgery (it honours GIT_COMMON_DIR redirects unconditionally; GIT_DIR it already scrubs,
so W7 refuses on the base too), and the pre-freeze candidate probe measured base_forgeries=3
(W1, W2, W4), base_honest=11.

Regress arm, judge, receipts, stub selftest and work-dir rules are the r68 machinery, unchanged.
The battery arm never writes outside --work and --receipt; the battery manifest is frozen in the
preregistration commit and the battery members are COMMITTED under census/round-69/battery/
(closes round-68 routed defect D2 — the members exist as files, not only as digests).

Stdlib only. Writes only under --work and --receipt. --work must exist and must not be under
/tmp, /var/tmp, $TMPDIR, or inside --root. The lane is never written: read-only `git show` and
regress reads. TMPDIR is never used for scratch.

Usage:
  python3 -B c1-counter.py --root LANE --matrix c1-matrix.tsv --base-rev FULL40 \
      (--rev FULL40 --tool RELPATH | --new-tool FILE) --work DIR [--receipt FILE]
  python3 -B c1-counter.py --root LANE --matrix c1-matrix.tsv --base-rev FULL40 --work DIR \
      --battery-manifest FILE --battery-dir DIR [--only NAME[,NAME...]] [--receipt FILE]
  python3 -B c1-counter.py --selftest --root LANE --matrix c1-matrix.tsv --base-rev FULL40 --work DIR

Exit: 0 = claim upheld per SUMMARY (battery: every outcome matches its manifest expectation;
selftest: all checks passed); 1 = claim fails; 2 = could not evaluate.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import posixpath
import re
import shutil
import shlex
import stat
import subprocess
import sys
from typing import Optional

BASE_REL = "tools/souji-receipt-write.py"
FIXTURE_REL = "tests/fixtures/r60-receipt-write.py"
FIXTURE_LAST_WANT = "pass=8 fail=0"
COUNTER_REL = "census/round-74/c1-counter.py"

SEED_INSTR = b"#!/bin/sh\necho instrument-ok\n"
SEED_COUNTER = b"counter v1\n"
SEED_NOTES = b"notes v1\n"
SEED_README = b"readme v1\n"
DIRTY_APPEND = b"dirty\n"
FORGED_COUNTER = b"counter FORGED\n"
FORGED_INSTR = b"#!/bin/sh\necho FORGED\n"
FORGED_NOTES = b"notes FORGED\n"
FORGED_README = b"readme FORGED\n"
APPENDED = b"appended-in-run\n"
TRANSIENT = b"transient-in-run\n"
UNTRACKED = b"u\n"
UNTRACKED_KEEP = b"k\n"

GIT_ID_NAME = "C1 Counter"
GIT_ID_EMAIL = "c1-counter@invalid"
GIT_DATE = "2026-11-05T12:00:00Z"

REV_RE = re.compile(r"^[0-9a-f]{40}$")
ECHO_ARGV = ["/bin/echo", "hi"]
CLASS_STATE = "RECEIPT-STATE-CHANGED-DURING-RUN"
CLASS_FLAG = "RECEIPT-INDEX-FLAG-CONCEALED"
CLASS_ENV = "RECEIPT-INDEX-ENV-SET"
CLASS_DIRTY = "lane worktree is dirty"
CLASS_ENVCFG = "RECEIPT-ENV-CONFIG-SET"
CLASS_ENVRED = "RECEIPT-ENV-REDIRECT-SET"
CLASS_CD = "RECEIPT-ENV-COMMONDIR-MISMATCH"

CASE_ORDER = ["A", "B", "C", "D", "T1", "T2", "T3", "T4", "T5", "N1", "N2", "N3", "N4",
              "V1", "V2", "MOD", "SY1", "SY2", "P13",
              "E1", "E2", "E3", "E4", "E5", "E6", "MOD2", "MOD3", "SY3",
              "W1", "W2", "W3",
              "W4", "W5", "W6", "PK3", "PK3h", "PK4", "PK4h", "PK6", "PK6h", "PK7", "PK7h",
              "U1", "G1", "A9", "F1", "W7",
              "LA", "LD", "LN4", "LU1", "LG1", "LA9", "GA", "GD", "NGA", "NGD", "ICA", "ICD",
              "AS1", "AS2", "ASh", "FC1", "FC2", "FC3", "FCh", "FCh2", "FM1", "FM2", "FMh",
              "FWr", "FWi", "FWp", "FWw", "FWs",
              "FX1", "FX2", "FX3", "FXh", "FXc"]

# r70 C1: the four pathspec variables of git(1) OPTIONS/ENVIRONMENT (S304); each new row sets one.
PATHSPEC_VARS = ("GIT_LITERAL_PATHSPECS", "GIT_GLOB_PATHSPECS", "GIT_NOGLOB_PATHSPECS",
                 "GIT_ICASE_PATHSPECS")
LP_ENV = {"GIT_LITERAL_PATHSPECS": "1"}

# r71 C1: size-preserving forged counter bytes and the clean filter that maps them back.
FORGED_SAMESIZE = b"counter v2\n"
FILTER_CLEAN = "sed s/v2/v1/"
CLASS_FILTER = "RECEIPT-FILTER-DRIVER-SET"
# r72 C2: wrapped-command helpers and the long-running process driver for the FW rows.
RESTORE_UNSET_CODE = ("import subprocess, sys\n"
                      "open(sys.argv[1], 'wb').write(sys.argv[2].encode('latin-1'))\n"
                      "subprocess.run(['git', '-C', sys.argv[3], 'config', '--unset', 'filter.t.clean'], check=True)\n")
CREATE_FORGE_CODE = ("import os, subprocess, sys\n"
                     "repo = sys.argv[1]\n"
                     "open(os.path.join(repo, 'tools', 'counter.py'), 'wb').write(sys.argv[2].encode('latin-1'))\n"
                     "os.makedirs(os.path.join(repo, '.git', 'info'), exist_ok=True)\n"
                     "open(os.path.join(repo, '.git', 'info', 'attributes'), 'wb').write(b'tools/counter.py filter=t\\n')\n"
                     "subprocess.run(['git', '-C', repo, 'config', 'filter.t.clean', sys.argv[3]], check=True)\n")
# pkt-line v2 long-running filter (gitattributes(5) "Long Running Filter Process"); clean maps v2 -> v1.
PROC_FILTER_CODE = r'''import sys
i, o = sys.stdin.buffer, sys.stdout.buffer
def rd():
    h = i.read(4)
    if not h:
        sys.exit(0)
    n = int(h, 16)
    return None if n == 0 else i.read(n - 4)
def wr(b):
    o.write(b"%04x" % (len(b) + 4) + b)
def fl():
    o.write(b"0000"); o.flush()
def lst():
    out = []
    while True:
        p = rd()
        if p is None:
            return out
        out.append(p)
lst(); wr(b"git-filter-server\n"); wr(b"version=2\n"); fl()
lst(); wr(b"capability=clean\n"); fl()
while True:
    hdr = lst()
    data = b"".join(lst())
    cmd = [h for h in hdr if h.startswith(b"command=")]
    if cmd and cmd[0] == b"command=clean\n":
        data = data.replace(b"v2", b"v1")
    wr(b"status=success\n"); fl()
    if data:
        wr(data)
    fl(); fl()
'''
WITNESS_ROWS = ("AS1", "AS2", "FC1", "FC2", "FC3", "FM1", "FM2")
# r73 C1: index stat-cache forgery (S72Sentinel; racy-git.adoc S315). Writes the forged bytes, then
# rewrites that path's index entry stat fields from the forged file's lstat (blob OID and flags kept),
# recomputes the index checksum and moves the index mtime 5 s past the entry so git does not treat the
# entry as racily clean. argv: repo, repo-relative path, forged bytes (latin-1).
CLASS_TRUTH = "RECEIPT-WORKTREE-STAT-CONCEALED"
INDEX_STAT_CODE = r'''import hashlib, os, struct, sys
repo, rel, forged = sys.argv[1], sys.argv[2], sys.argv[3].encode("latin-1")
full = os.path.join(repo, rel)
with open(full, "wb") as f:
    f.write(forged)
st = os.lstat(full)
p = os.path.join(repo, ".git", "index")
data = open(p, "rb").read()
if data[:4] != b"DIRC":
    sys.exit("bad index signature")
ver, n = struct.unpack(">II", data[4:12])
if ver not in (2, 3):
    sys.exit(f"index version {ver} unsupported")
off, out, target, hit = 12, bytearray(data[:12]), rel.encode(), False
for _ in range(n):
    start = off
    fixed = data[off:off + 62]
    sha, flags = fixed[40:60], fixed[60:62]
    ns = off + 62
    z = data.index(b"\0", ns)
    name = data[ns:z]
    tail_end = z + 1 + ((8 - ((z + 1 - start) % 8)) % 8)
    if name == target:
        hit = True
        fixed = struct.pack(">10I", int(st.st_ctime), st.st_ctime_ns % 1_000_000_000,
                            int(st.st_mtime), st.st_mtime_ns % 1_000_000_000,
                            st.st_dev & 0xFFFFFFFF, st.st_ino & 0xFFFFFFFF, st.st_mode,
                            st.st_uid, st.st_gid, st.st_size & 0xFFFFFFFF) + sha + flags
        out += fixed + data[ns:tail_end]
    else:
        out += data[start:tail_end]
    off = tail_end
if not hit:
    sys.exit(f"{rel} not in index")
out += data[off:-20]
out += hashlib.sha1(bytes(out)).digest()
with open(p, "wb") as f:
    f.write(bytes(out))
t = st.st_mtime + 5
os.utime(p, (t, t))
'''

# Inline helpers executed as the wrapped command (argv form; no shell quoting involved).
CHMOD_CODE = "import os, sys\nos.chmod(sys.argv[1], 0o755)\n"
RETARGET_CODE = ("import os, sys\n"
                 "os.unlink(sys.argv[1])\n"
                 "os.symlink(sys.argv[2], sys.argv[1])\n")

# Frozen per-case setup (pre-run mutation) and wrapped-command mutation (`inrun`).
CASE_SPECS = {
    "A":  {"name": "honest-clean"},
    "B":  {"name": "honest-allow-dirty", "dirty": True, "allow_dirty": True},
    "C":  {"name": "dirty-visible", "dirty": True},
    "D":  {"name": "skip-worktree-forged", "flag": "skip-worktree",
           "target": "tools/counter.py", "forged": FORGED_COUNTER},
    "T1": {"name": "inrun-flag", "inrun": "flag"},
    "T2": {"name": "inrun-edit-instrument", "inrun": "edit-instrument"},
    "T3": {"name": "inrun-edit-noninstrument", "inrun": "edit-noninstrument"},
    "T4": {"name": "inrun-transient-restore", "inrun": "transient-restore"},
    "T5": {"name": "inrun-untracked", "inrun": "untracked"},
    "N1": {"name": "allow-dirty-inrun-append-to-dirty", "dirty": True, "allow_dirty": True,
           "inrun": "append-dirty"},
    "N2": {"name": "allow-dirty-inrun-file-in-untracked-dir", "allow_dirty": True,
           "untracked_dir": "tools/extra", "inrun": "untracked-dir-new"},
    "N3": {"name": "git-index-file-env", "flag": "skip-worktree", "target": "tools/notes.txt",
           "forged": FORGED_NOTES, "altidx": True, "allow_dirty": True, "use_env_index": True,
           "noecho_env": ["GIT_INDEX_FILE"]},
    "N4": {"name": "subdirectory-root-scope", "flag": "skip-worktree", "target": "README.md",
           "forged": FORGED_README, "rootsub": "tools"},
    "V1": {"name": "untracked-visibility-concealed", "config_untracked_no": True,
           "untracked_file": "tools/hidden.txt"},
    "V2": {"name": "untracked-visibility-honest", "config_untracked_no": True},
    "MOD": {"name": "allow-dirty-inrun-mode-flip", "dirty": True, "allow_dirty": True,
            "inrun": "chmod-dirty"},
    "SY1": {"name": "allow-dirty-symlink-stable", "allow_dirty": True,
            "untracked_dir": "tools/extra", "symlink": True},
    "SY2": {"name": "allow-dirty-inrun-symlink-retarget", "allow_dirty": True,
            "untracked_dir": "tools/extra", "symlink": True, "inrun": "symlink-retarget"},
    "P13": {"name": "git-index-file-nonexistent", "flag": "skip-worktree",
            "target": "tools/notes.txt", "forged": FORGED_NOTES, "allow_dirty": True,
            "env_index_missing": True, "noecho_env": ["GIT_INDEX_FILE"]},
    # r66 rows: caller-injected config routes and object redirects, full mode bits, same-content retarget.
    "E1":  {"name": "env-config-count-excludes", "untracked_file": "tools/hidden.txt",
            "env_kind": "count-excludes"},
    "E2":  {"name": "env-config-parameters-excludes", "untracked_file": "tools/hidden.txt",
            "env_kind": "params-excludes"},
    "E3":  {"name": "env-config-global-excludes", "untracked_file": "tools/hidden.txt",
            "env_kind": "global-excludes"},
    "E4":  {"name": "env-object-dir-redirect", "env_kind": "object-dir"},
    "E5":  {"name": "env-alternates-redirect", "env_kind": "alternates"},
    "E6":  {"name": "env-replace-ref-base", "env_kind": "replace-base"},
    "MOD2": {"name": "allow-dirty-inrun-setuid-flip", "dirty": True, "allow_dirty": True,
             "inrun": "chmod-setuid"},
    "MOD3": {"name": "allow-dirty-inrun-sticky-flip", "dirty": True, "allow_dirty": True,
             "inrun": "chmod-sticky"},
    "SY3": {"name": "allow-dirty-inrun-symlink-same-content-retarget", "allow_dirty": True,
            "untracked_dir": "tools/extra", "symlink": True, "inrun": "symlink-retarget-same"},
    # r67 rows: caller-injected GIT_COMMON_DIR, value-checked against the repository's own common dir.
    "W1": {"name": "env-common-dir-mismatch-hides-mode", "env_kind": "common-dir-copy",
           "mode_change": True, "noecho_env": ["GIT_COMMON_DIR"]},
    "W2": {"name": "env-common-dir-mismatch-clean", "env_kind": "common-dir-copy",
           "noecho_env": ["GIT_COMMON_DIR"]},
    "W3": {"name": "env-common-dir-match-honest", "env_kind": "common-dir-real",
           "noecho_env": ["GIT_COMMON_DIR"]},
    # r68 rows: the r67 routed items. W4/W5 measure the two M9 claim clauses; PK* freeze the four
    # r67-proposed kill-power fixtures (each flips exactly its pin-drop mutant; see mutate-writer.py).
    # noecho_env freezes the caller values a refusal message must never print (D30, r65-frozen
    # redaction); the judge counts violations, the battery arm classifies them.
    "W4":  {"name": "env-common-dir-relative-poison", "env_kind": "common-dir-rel-poison",
            "repo_name": "main", "cwd_parent": True, "mode_change": True,
            "noecho_env": ["GIT_COMMON_DIR"]},
    "W5":  {"name": "env-common-dir-empty", "env_kind": "common-dir-empty", "cwd_gitdir": True,
            "noecho_env": ["GIT_COMMON_DIR"]},
    "W6":  {"name": "env-common-dir-symlink-alias-honest", "env_kind": "common-dir-alias", "honest": True,
            "noecho_env": ["GIT_COMMON_DIR"]},
    "PK3":  {"name": "exclude-repo-local", "env_kind": "exclude-repo-local"},
    "PK3h": {"name": "exclude-repo-local-honest", "env_kind": "exclude-repo-local", "honest": True},
    "PK4":  {"name": "global-filemode", "env_kind": "global-filemode"},
    "PK4h": {"name": "global-filemode-honest", "env_kind": "global-filemode", "honest": True},
    "PK6":  {"name": "replace-ref-head", "env_kind": "replace-ref-head"},
    "PK6h": {"name": "replace-ref-head-honest", "env_kind": "replace-ref-head", "honest": True},
    "PK7":  {"name": "system-filemode", "env_kind": "system-filemode"},
    "PK7h": {"name": "system-filemode-honest", "env_kind": "system-filemode", "honest": True},
    # r69 rows: the 14 unbattered declared protections (S68ScoutDeclared inventory). Each new row
    # observes at least one protection a battery mutant removes; see the module docstring.
    "U1": {"name": "unmerged-index-forged", "env_kind": "unmerged-index"},
    "G1": {"name": "gitlink-concealed", "env_kind": "gitlink-flag"},
    "A9": {"name": "concealed-absent", "env_kind": "absent-flag"},
    "F1": {"name": "fsmonitor-silenced-dirty", "env_kind": "fsmonitor-silent", "dirty": True},
    "W7": {"name": "git-dir-redirect-hides-mode", "env_kind": "git-dir-copy", "mode_change": True,
           "noecho_env": ["GIT_DIR"]},
    # r70 C1 rows: the carried D/N4/U1/G1/A9 fixtures and the honest clean row re-run with a caller
    # pathspec variable (`pathspec_env`, merged by case_env after any row env). Expected classes are
    # the carried rows' classes: the variable must change no verdict.
    "LA":  {"name": "honest-clean-literal-pathspecs", "pathspec_env": LP_ENV},
    "LD":  {"name": "skip-worktree-forged-literal-pathspecs", "flag": "skip-worktree",
            "target": "tools/counter.py", "forged": FORGED_COUNTER, "pathspec_env": LP_ENV},
    "LN4": {"name": "subdirectory-root-scope-literal-pathspecs", "flag": "skip-worktree",
            "target": "README.md", "forged": FORGED_README, "rootsub": "tools",
            "pathspec_env": LP_ENV},
    "LU1": {"name": "unmerged-index-literal-pathspecs", "env_kind": "unmerged-index",
            "pathspec_env": LP_ENV},
    "LG1": {"name": "gitlink-concealed-literal-pathspecs", "env_kind": "gitlink-flag",
            "pathspec_env": LP_ENV},
    "LA9": {"name": "concealed-absent-literal-pathspecs", "env_kind": "absent-flag",
            "pathspec_env": LP_ENV},
    "GA":  {"name": "honest-clean-glob-pathspecs", "pathspec_env": {"GIT_GLOB_PATHSPECS": "1"}},
    "GD":  {"name": "skip-worktree-forged-glob-pathspecs", "flag": "skip-worktree",
            "target": "tools/counter.py", "forged": FORGED_COUNTER,
            "pathspec_env": {"GIT_GLOB_PATHSPECS": "1"}},
    "NGA": {"name": "honest-clean-noglob-pathspecs", "pathspec_env": {"GIT_NOGLOB_PATHSPECS": "1"}},
    "NGD": {"name": "skip-worktree-forged-noglob-pathspecs", "flag": "skip-worktree",
            "target": "tools/counter.py", "forged": FORGED_COUNTER,
            "pathspec_env": {"GIT_NOGLOB_PATHSPECS": "1"}},
    "ICA": {"name": "honest-clean-icase-pathspecs", "pathspec_env": {"GIT_ICASE_PATHSPECS": "1"}},
    "ICD": {"name": "skip-worktree-forged-icase-pathspecs", "flag": "skip-worktree",
            "target": "tools/counter.py", "forged": FORGED_COUNTER,
            "pathspec_env": {"GIT_ICASE_PATHSPECS": "1"}},
    # r71 C1 rows (S70Sentinel F1/F2). AS*: the filter attribute arrives through a caller
    # GIT_ATTR_SOURCE tree (a commit object beside HEAD, read from case-dir/attr-source.txt).
    "AS1":  {"name": "attr-source-filter-forged", "env_kind": "attr-source-filter",
             "target": "tools/counter.py", "forged": FORGED_SAMESIZE},
    "AS2":  {"name": "attr-source-filter-inrun-edit", "env_kind": "attr-source-filter",
             "inrun": "edit-counter-samesize"},
    "ASh":  {"name": "attr-source-text-honest", "env_kind": "attr-source-text"},
    # FC*: the filter attribute is repository state (committed .gitattributes or info/attributes).
    "FC1":  {"name": "committed-filter-forged", "env_kind": "committed-filter",
             "target": "tools/counter.py", "forged": FORGED_SAMESIZE},
    "FC2":  {"name": "committed-filter-inrun-edit", "env_kind": "committed-filter",
             "inrun": "edit-counter-samesize"},
    "FC3":  {"name": "info-attributes-filter-forged", "env_kind": "info-attributes-filter",
             "target": "tools/counter.py", "forged": FORGED_SAMESIZE},
    "FCh":  {"name": "committed-filter-no-driver-honest", "env_kind": "committed-filter-nodriver"},
    "FCh2": {"name": "driver-configured-no-tracked-path-honest", "env_kind": "driver-unused"},
    # FM*: repository-local core.fileMode=false.
    "FM1":  {"name": "local-filemode-false-prerun-chmod", "env_kind": "local-filemode",
             "chmod_notes": True},
    "FM2":  {"name": "local-filemode-false-inrun-chmod", "env_kind": "local-filemode",
             "inrun": "chmod-clean"},
    "FMh":  {"name": "local-filemode-false-honest", "env_kind": "local-filemode"},
    # r72 C2 rows (S71MutWriter W3/W4/W5/W6/W8 routes; pre-freeze probe fw-shapes-probe.txt).
    "FWr":  {"name": "prerun-forged-driver-restored-and-unset-inrun", "env_kind": "info-attributes-filter",
             "target": "tools/counter.py", "forged": FORGED_SAMESIZE, "inrun": "restore-unset-driver"},
    "FWi":  {"name": "inrun-forge-and-driver-creation", "inrun": "create-driver-forge"},
    "FWp":  {"name": "process-driver-forged", "env_kind": "info-process-filter",
             "target": "tools/counter.py", "forged": FORGED_SAMESIZE},
    "FWw":  {"name": "worktree-only-attributes-forged", "env_kind": "worktree-only-attributes",
             "target": "tools/counter.py", "forged": FORGED_SAMESIZE},
    "FWs":  {"name": "driver-named-set-forged", "env_kind": "info-filter-named-set",
             "target": "tools/counter.py", "forged": FORGED_SAMESIZE},
    # r73 C1 rows (S72Sentinel index stat-cache routes; pre-freeze probes fx-index-stat.txt, fx-honest.txt).
    "FX1":  {"name": "inrun-forge-index-stat-rewritten", "inrun": "index-stat-counter"},
    "FX2":  {"name": "prerun-forge-index-stat-rewritten", "index_stat": ("tools/counter.py", FORGED_SAMESIZE)},
    "FX3":  {"name": "inrun-instrument-forge-index-stat-rewritten", "inrun": "index-stat-instrument"},
    "FXh":  {"name": "honest-stale-stat-bytes-unchanged", "stale_stat": "tools/notes.txt"},
    "FXc":  {"name": "honest-autocrlf-crlf-restaged", "autocrlf_crlf": "tools/notes.txt"},
}

# Inline helpers executed as the wrapped command (argv form; no shell quoting involved).
EDIT_CODE = ("import sys\n"
             "open(sys.argv[1], sys.argv[2]).write(sys.argv[3].encode('latin-1'))\n")
RESTORE_CODE = ("import sys\n"
                "p = sys.argv[1]\n"
                "open(p, 'ab').write(sys.argv[2].encode('latin-1'))\n"
                "open(p, 'wb').write(sys.argv[3].encode('latin-1'))\n")
# r69: the L1 index-lock-holder row was designed and then REMOVED before the freeze — probed
# 2026-11-05, git status (2.5x) attempts no optional index-write lock under a held index.lock
# (rc 0, empty stderr, with and without GIT_OPTIONAL_LOCKS=0), so the D18 pin has no honest
# single-edit row; D18 is a named limit (census/round-69/records/declared-coverage.tsv).


class CaseError(Exception):
    """A fixture build/mutation failure; the case is judged as error."""


def _b(data: bytes) -> str:
    return data.decode("latin-1")


def inrun_argv(kind: str, repo: str) -> list[str]:
    """Wrapped command for an in-run mutation; references the fixture repo by absolute path."""
    tools = os.path.join(repo, "tools")
    if kind == "flag":
        return ["git", "-C", repo, "update-index", "--skip-worktree", "tools/counter.py"]
    if kind == "edit-instrument":
        return [sys.executable, "-c", EDIT_CODE, os.path.join(tools, "instr.sh"), "wb", _b(FORGED_INSTR)]
    if kind == "edit-noninstrument":
        return [sys.executable, "-c", EDIT_CODE, os.path.join(tools, "notes.txt"), "ab", _b(APPENDED)]
    if kind == "transient-restore":
        return [sys.executable, "-c", RESTORE_CODE, os.path.join(tools, "notes.txt"),
                _b(TRANSIENT), _b(SEED_NOTES)]
    if kind == "untracked":
        return [sys.executable, "-c", EDIT_CODE, os.path.join(tools, "extra.txt"), "wb", _b(UNTRACKED)]
    if kind == "append-dirty":
        # N1: appends to the SAME file the pre-run dirty append touched; only meaningful together
        # with dirty=True + allow_dirty=True in the spec.
        return [sys.executable, "-c", EDIT_CODE, os.path.join(tools, "notes.txt"), "ab", _b(APPENDED)]
    if kind == "untracked-dir-new":
        # N2: new file inside the pre-existing untracked directory (parent exists by construction).
        return [sys.executable, "-c", EDIT_CODE,
                os.path.join(repo, "tools", "extra", "new.txt"), "wb", _b(UNTRACKED)]
    if kind == "chmod-dirty":
        # MOD: mode-only flip of the already-dirty tracked file; content and porcelain bytes stay
        # identical, so only the snapshot's mode byte can see it.
        return [sys.executable, "-c", CHMOD_CODE, os.path.join(repo, "tools", "notes.txt")]
    if kind == "symlink-retarget":
        # SY2: retarget the recorded symlink inside the untracked directory; the link name and the
        # directory's other entries keep every porcelain byte identical.
        return [sys.executable, "-c", RETARGET_CODE,
                os.path.join(repo, "tools", "extra", "link"), "../instr.sh"]
    if kind == "chmod-setuid":
        # MOD2: 644 -> 4644 (setuid). Content digest identical; the base snapshot masks the high
        # bits with & 0o777, so only a full-permission-bits mode byte can see it.
        return [sys.executable, "-c", CHMOD_CODE.replace("0o755", "0o4644"),
                os.path.join(repo, "tools", "notes.txt")]
    if kind == "chmod-sticky":
        # MOD3: 644 -> 1644 (sticky). Same class of invisibility under the base mask.
        return [sys.executable, "-c", CHMOD_CODE.replace("0o755", "0o1644"),
                os.path.join(repo, "tools", "notes.txt")]
    if kind == "symlink-retarget-same":
        # SY3: retarget to a byte-identical copy of the original target (notes-copy.txt carries the
        # notes.txt bytes); a read-through symlink hasher sees identical content, the recorded
        # target STRING changes, so the writer still refuses (r65 M11 kill-power row).
        return [sys.executable, "-c", RETARGET_CODE,
                os.path.join(repo, "tools", "extra", "link"), "../notes-copy.txt"]
    if kind == "edit-counter-samesize":
        # AS2/FC2: size-preserving in-run edit of a tracked file a clean filter maps back.
        return [sys.executable, "-c", EDIT_CODE, os.path.join(tools, "counter.py"), "wb",
                _b(FORGED_SAMESIZE)]
    if kind == "chmod-clean":
        # FM2: in-run 644 -> 755 flip of a clean tracked file (no --allow-dirty).
        return [sys.executable, "-c", CHMOD_CODE, os.path.join(tools, "notes.txt")]
    if kind == "restore-unset-driver":
        # FWr: restore the committed bytes and unset the driver; only the pre-run witness saw both.
        return [sys.executable, "-c", RESTORE_UNSET_CODE, os.path.join(tools, "counter.py"),
                _b(SEED_COUNTER), repo]
    if kind == "create-driver-forge":
        # FWi: forge same-size bytes and create info/attributes + the clean driver in-run.
        return [sys.executable, "-c", CREATE_FORGE_CODE, repo, _b(FORGED_SAMESIZE), FILTER_CLEAN]
    if kind == "index-stat-counter":
        # FX1: forge same-size counter bytes and rewrite the entry's stat cache in-run.
        return [sys.executable, "-c", INDEX_STAT_CODE, repo, "tools/counter.py", _b(FORGED_SAMESIZE)]
    if kind == "index-stat-instrument":
        # FX3: forge the instrument and rewrite its stat cache in-run (the writer compared it pre-run only).
        return [sys.executable, "-c", INDEX_STAT_CODE, repo, "tools/instr.sh", _b(FORGED_INSTR)]
    raise CaseError(f"unknown in-run kind {kind!r}")


def wrapped_argv(spec: dict, repo: str) -> list[str]:
    if "inrun" in spec:
        return inrun_argv(spec["inrun"], repo)
    return list(ECHO_ARGV)


def clean_env(extra: Optional[dict] = None) -> dict:
    """r69 C2 (sentinel MEDIUM-1 r68): the ambient environment is scrubbed of HOME and
    XDG_CONFIG_HOME (no host git config file is reachable) and of every GIT_TRACE* variable, and
    the counter's own git calls pin GIT_CONFIG_GLOBAL to the null device with GIT_CONFIG_NOSYSTEM=1,
    so no host, global or system config can steer fixture builds, the regress fixture or a writer
    slot. The r68 scrub tuple is unchanged."""
    e = {k: v for k, v in os.environ.items()
         if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE",
                      "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
                      "GIT_REPLACE_REF_BASE", "GIT_CONFIG_COUNT", "GIT_CONFIG_PARAMETERS",
                      "GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_SYSTEM",
                      "GIT_NO_REPLACE_OBJECTS", "GIT_COMMON_DIR", "GIT_NAMESPACE",
                      "GIT_CEILING_DIRECTORIES", "HOME", "XDG_CONFIG_HOME")
         and not k.startswith("GIT_CONFIG_KEY_") and not k.startswith("GIT_CONFIG_VALUE_")
         and not k.startswith("GIT_TRACE")
         # r70: ambient pathspec variables and the r69-routed template/attr/exec-path/hash routes
         and k not in PATHSPEC_VARS
         and k not in ("GIT_TEMPLATE_DIR", "GIT_ATTR_SOURCE", "GIT_EXEC_PATH", "GIT_DEFAULT_HASH")}
    e["GIT_OPTIONAL_LOCKS"] = "0"
    e["GIT_CONFIG_GLOBAL"] = os.devnull
    e["GIT_CONFIG_NOSYSTEM"] = "1"
    if extra:
        e.update(extra)
    return e


def git_run(repo: str, args: list[str], env: Optional[dict] = None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", repo, *args], stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, env=clean_env(env), timeout=120)


def build_repo(case_dir: str) -> tuple[str, str]:
    """Fresh fixture repo at case_dir/repo; returns (repo, seed rev)."""
    return build_repo_at(os.path.join(case_dir, "repo"))


def build_repo_at(repo: str) -> tuple[str, str]:
    """Fresh fixture repo at the given absolute path; returns (repo, seed rev)."""
    case_dir = os.path.dirname(repo)
    if os.path.isdir(case_dir):
        shutil.rmtree(case_dir)
    os.makedirs(repo)
    r = git_run(repo, ["init", "-q"])
    if r.returncode != 0:
        raise CaseError(f"git init failed: {r.stderr.decode('utf-8', 'replace').strip()}")
    top = git_run(repo, ["rev-parse", "--show-toplevel"])
    if top.returncode != 0 or os.path.realpath(top.stdout.decode().strip()) != os.path.realpath(repo):
        raise CaseError(f"toplevel mismatch before first commit: {top.stdout.decode().strip()!r}")
    for key, val in (("user.name", GIT_ID_NAME), ("user.email", GIT_ID_EMAIL)):
        r = git_run(repo, ["config", key, val])
        if r.returncode != 0:
            raise CaseError(f"git config {key} failed")
    os.makedirs(os.path.join(repo, "tools"), exist_ok=True)
    seeds = {"tools/instr.sh": SEED_INSTR, "tools/counter.py": SEED_COUNTER,
             "tools/notes.txt": SEED_NOTES, "README.md": SEED_README,
             # root-level dual copy of the instrument: lets a writer rooted at <repo>/tools resolve
             # its instrument blob (root-relative `rev:<path>` plumbing) to identical bytes.
             "instr.sh": SEED_INSTR,
             # r66 SY3: a byte-identical copy of notes.txt at the repo root, so a same-content
             # symlink retarget (../notes-copy.txt) exists as a target.
             "notes-copy.txt": SEED_NOTES,
             # r69 D10: the same-content copy BESIDE notes.txt under tools/, because tools/extra/link
             # -> ../notes-copy.txt resolves here; without it the read-through mutant's open() fails
             # into the symlink-unreadable branch and SY3 refuses on the payload change instead of
             # forging (probed 2026-11-05, /fast/scratch/hyaku/souji-r69/probe/d10repro).
             "tools/notes-copy.txt": SEED_NOTES}
    for rel, data in seeds.items():
        with open(os.path.join(repo, rel), "wb") as f:
            f.write(data)
    os.chmod(os.path.join(repo, "tools/instr.sh"), 0o755)
    dates = {"GIT_AUTHOR_DATE": GIT_DATE, "GIT_COMMITTER_DATE": GIT_DATE}
    r = git_run(repo, ["add", "-A"], env=dates)
    if r.returncode != 0:
        raise CaseError("git add failed")
    r = git_run(repo, ["commit", "-q", "-m", "c1 seed"], env=dates)
    if r.returncode != 0:
        raise CaseError(f"git commit failed: {r.stderr.decode('utf-8', 'replace').strip()}")
    h = git_run(repo, ["rev-parse", "HEAD"])
    rev = h.stdout.decode().strip()
    if h.returncode != 0 or not REV_RE.match(rev):
        raise CaseError(f"bad seed HEAD: {rev!r}")
    return repo, rev


def mutate(repo: str, spec: dict) -> None:
    """Pre-run setup. Order: index flag, forged bytes, visible dirty append, untracked dir, alt index."""
    if spec.get("flag"):
        r = git_run(repo, ["update-index", f"--{spec['flag']}", spec["target"]])
        if r.returncode != 0:
            raise CaseError(f"update-index --{spec['flag']} failed")
    if spec.get("forged") is not None:
        with open(os.path.join(repo, spec["target"]), "wb") as f:
            f.write(spec["forged"])
    if spec.get("dirty"):
        with open(os.path.join(repo, "tools/notes.txt"), "ab") as f:
            f.write(DIRTY_APPEND)
    if spec.get("untracked_dir"):
        os.makedirs(os.path.join(repo, spec["untracked_dir"]), exist_ok=True)
        with open(os.path.join(repo, spec["untracked_dir"], "keep.txt"), "wb") as f:
            f.write(UNTRACKED_KEEP)
    if spec.get("untracked_file"):
        with open(os.path.join(repo, spec["untracked_file"]), "wb") as f:
            f.write(UNTRACKED)
    if spec.get("symlink"):
        # r65 M5 rule fixture: a symlink inside the untracked directory; recorded by name and
        # target, never followed. Target is the tracked, forged-free notes.txt beside the dir.
        os.symlink("../notes.txt", os.path.join(repo, spec["untracked_dir"], "link"))
    if spec.get("config_untracked_no"):
        # V1/V2: the operator-injected visibility config lives in the fixture repo's own config;
        # the new writer's per-call `-c status.showUntrackedFiles=all` must override it.
        r = git_run(repo, ["config", "status.showUntrackedFiles", "no"])
        if r.returncode != 0:
            raise CaseError("fixture config status.showUntrackedFiles failed")
    if spec.get("altidx"):
        # A bare `GIT_INDEX_FILE=<copy> git update-index --no-skip-worktree <target>` fails (git
        # reads the nonexistent override as an empty index: fatal: Unable to mark file), so build
        # the flag-free copy by copying the real index first, then clearing the flag in the copy.
        src = os.path.join(repo, ".git", "index")
        dst = os.path.join(repo, ".git", "alt-idx")
        shutil.copyfile(src, dst)
        r = git_run(repo, ["update-index", "--no-skip-worktree", spec["target"]],
                    env={"GIT_INDEX_FILE": dst})
        if r.returncode != 0:
            raise CaseError(f"alt-idx update-index failed: {r.stderr.decode('utf-8', 'replace').strip()}")
        v = git_run(repo, ["ls-files", "-v"], env={"GIT_INDEX_FILE": dst})
        tags = {rec.partition(b" ")[0] for rec in v.stdout.split(b"\0") if rec}
        if v.returncode != 0 or tags - {b"H"}:
            raise CaseError(f"alt-idx is not flag-free: tags={sorted(t.decode() for t in tags)}")


    if spec.get("mode_change"):
        # W1: a tracked 755->644 change on the seeded instrument; visible to `git status` unless a
        # redirected config sets core.fileMode=false.
        os.chmod(os.path.join(repo, "tools", "instr.sh"), 0o644)
    if spec.get("env_kind"):
        # r66 E-rows: caller-injected config/redirect fixtures live BESIDE the repo (case-dir level),
        # never inside it, so no row's fixture content changes another row's porcelain.
        kind = spec["env_kind"]
        case_dir = os.path.dirname(repo)
        if kind in ("count-excludes", "params-excludes", "global-excludes"):
            exc = os.path.join(case_dir, "excludes.txt")
            with open(exc, "wb") as f:
                f.write(b"hidden.txt\n")
            if kind == "global-excludes":
                with open(os.path.join(case_dir, "global.gitconfig"), "w", encoding="utf-8") as f:
                    f.write("[core]\n\texcludesFile = %s\n" % exc)
        elif kind == "object-dir":
            dst = os.path.join(repo, ".git", "objects-copy")
            shutil.copytree(os.path.join(repo, ".git", "objects"), dst,
                            dirs_exist_ok=True, symlinks=True)
            if not os.path.isdir(dst):
                raise CaseError("objects-copy missing")
        elif kind == "alternates":
            os.makedirs(os.path.join(repo, ".git", "alternates-empty"), exist_ok=True)
        elif kind == "common-dir-copy":
            # W1/W2: a byte copy of the fixture repo's .git beside the repo, whose config carries
            # core.fileMode=false; a caller-injected GIT_COMMON_DIR pointed here repoints config
            # (and objects) reads at the copy.
            dst = os.path.join(case_dir, "commondir-copy")
            shutil.copytree(os.path.join(repo, ".git"), dst, symlinks=True)
            with open(os.path.join(dst, "config"), "a", encoding="utf-8") as f:
                f.write("[core]\n\tfileMode = false\n")
            if not os.path.isfile(os.path.join(dst, "config")):
                raise CaseError("commondir-copy config missing")
        elif kind == "common-dir-real":
            # W3: no fixture bytes; case_env resolves the repository's own common dir at run time.
            pass
        elif kind == "common-dir-empty":
            # W5: no fixture bytes; case_env carries the empty caller value.
            pass
        elif kind == "common-dir-alias":
            # W6: a symlink to the repository's own .git (honest: equal after canonicalization).
            os.symlink(os.path.realpath(os.path.join(repo, ".git")), os.path.join(case_dir, "alias-git"))
        elif kind == "exclude-repo-local":
            # PK3: a repository-local core.excludesFile; the defect variant adds the untracked file
            # the excludes file names (hidden from plain git status without the writer's -c pin).
            excl = os.path.join(case_dir, "excl-local.txt")
            with open(excl, "wb") as f:
                f.write(b"hidden.txt\n")
            r = git_run(repo, ["config", "core.excludesFile", excl])
            if r.returncode != 0:
                raise CaseError("fixture config core.excludesFile failed")
            if not spec.get("honest"):
                with open(os.path.join(repo, "tools", "hidden.txt"), "wb") as f:
                    f.write(UNTRACKED)
        elif kind in ("global-filemode", "system-filemode"):
            # PK4/PK7: a caller-named global/system config whose core.fileMode=false hides a tracked
            # 755->644 change; core.filemode is unset in the fixture config so the caller file wins.
            cfg = os.path.join(case_dir, ("global-mode.gitconfig" if kind == "global-filemode"
                                          else "system-mode.gitconfig"))
            with open(cfg, "wb") as f:
                f.write(b"[core]\n\tfileMode = false\n")
            r = git_run(repo, ["config", "--unset", "core.filemode"])
            if r.returncode not in (0, 5):
                raise CaseError(f"fixture unset core.filemode failed rc={r.returncode}")
            if not spec.get("honest"):
                os.chmod(os.path.join(repo, "tools", "instr.sh"), 0o644)
        elif kind == "replace-ref-head":
            # PK6: a repository replace ref for HEAD whose replacement tree carries FORGED instrument
            # bytes; index and worktree carry the same forged bytes, so only a replacement-honouring
            # read sees a clean, matching tree (k67-proposed setup_k6_replace).
            if not spec.get("honest"):
                head = git_run(repo, ["rev-parse", "HEAD"]).stdout.decode().strip()
                fpath = os.path.join(case_dir, "forged-instr.sh")
                with open(fpath, "wb") as f:
                    f.write(FORGED_INSTR)
                os.chmod(fpath, 0o755)
                r = git_run(repo, ["hash-object", "-w", fpath])
                if r.returncode != 0:
                    raise CaseError("hash-object failed")
                blob = r.stdout.decode().strip()
                ienv = {"GIT_INDEX_FILE": os.path.join(case_dir, "forge-idx")}
                r = git_run(repo, ["read-tree", head], env=ienv)
                if r.returncode != 0:
                    raise CaseError("read-tree failed")
                r = git_run(repo, ["update-index", "--add", "--cacheinfo",
                                   f"100755,{blob},tools/instr.sh"], env=ienv)
                if r.returncode != 0:
                    raise CaseError("update-index (forge idx) failed")
                r = git_run(repo, ["write-tree"], env=ienv)
                if r.returncode != 0:
                    raise CaseError("write-tree failed")
                tree = r.stdout.decode().strip()
                dates = {"GIT_AUTHOR_DATE": GIT_DATE, "GIT_COMMITTER_DATE": GIT_DATE}
                r = git_run(repo, ["commit-tree", tree, "-p", head, "-m", "r68 forged replacement"],
                            env={**dates, "GIT_AUTHOR_NAME": "R68 Fixture",
                                 "GIT_AUTHOR_EMAIL": "r68-fixture@invalid",
                                 "GIT_COMMITTER_NAME": "R68 Fixture",
                                 "GIT_COMMITTER_EMAIL": "r68-fixture@invalid"})
                if r.returncode != 0:
                    raise CaseError("commit-tree failed")
                rep = r.stdout.decode().strip()
                r = git_run(repo, ["update-ref", f"refs/replace/{head}", rep])
                if r.returncode != 0:
                    raise CaseError("update-ref replace failed")
                with open(os.path.join(repo, "tools", "instr.sh"), "wb") as f:
                    f.write(FORGED_INSTR)
                os.chmod(os.path.join(repo, "tools", "instr.sh"), 0o755)
                r = git_run(repo, ["update-index", "--cacheinfo", f"100755,{blob},tools/instr.sh"])
                if r.returncode != 0:
                    raise CaseError("update-index (worktree forge) failed")
        elif kind == "common-dir-rel-poison":
            # W4, REBUILT per QUALITY Q132 (the r68 copy at <repo>/main resolved to no directory):
            # the fixture repo is <case>/main; the poisoned .git copy now lives at
            # <case>/main/main/.git — exactly the directory the relative caller value `main/.git`
            # names when git resolves it against the -C root. `main/` is hidden via info/exclude so
            # only the mode_change branch's tracked 755->644 change dirties the real worktree. The
            # honest writer's value check passes (cwd-resolved value == the real common dir) and the
            # scrub keeps every writer git call on the real repository, so the dirty check refuses;
            # an M-CD-SCRUB mutant forwards the value, its git children resolve onto the poison and
            # accept — the row's behavioural kill.
            excl = os.path.join(repo, ".git", "info", "exclude")
            with open(excl, "a", encoding="utf-8") as f:
                f.write("main/\n")
            os.makedirs(os.path.join(repo, "main"), exist_ok=True)
            dst = os.path.join(repo, "main", ".git")
            shutil.copytree(os.path.join(repo, ".git"), dst, symlinks=True)
            with open(os.path.join(dst, "config"), "a", encoding="utf-8") as f:
                f.write("[core]\n\tfileMode = false\n")
            if not os.path.isdir(dst):
                raise CaseError("poison .git copy missing")
        elif kind == "unmerged-index":
            # U1 (D02): two conflicting stages on tools/notes.txt via --index-info (the writer
            # selftest case_17 shape); ls-files -v tags the path U and _flag_refusal classes it
            # RECEIPT-INDEX-UNMERGED before the dirty check.
            r = subprocess.run(["git", "-C", repo, "hash-object", "-w", "--stdin"],
                               input=SEED_NOTES + b"one\n", stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=clean_env(), timeout=120)
            if r.returncode != 0:
                raise CaseError("unmerged hash-object (1) failed")
            s1 = r.stdout.decode().strip()
            r = subprocess.run(["git", "-C", repo, "hash-object", "-w", "--stdin"],
                               input=SEED_NOTES + b"two\n", stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=clean_env(), timeout=120)
            if r.returncode != 0:
                raise CaseError("unmerged hash-object (2) failed")
            s2 = r.stdout.decode().strip()
            records = (f"100644 {s1} 1\ttools/notes.txt\n"
                       f"100644 {s2} 2\ttools/notes.txt\n")
            r = subprocess.run(["git", "-C", repo, "update-index", "--index-info"],
                               input=records.encode("ascii"), stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=clean_env(), timeout=120)
            if r.returncode != 0:
                raise CaseError(f"unmerged --index-info failed: {r.stderr.decode('utf-8', 'replace').strip()}")
        elif kind == "gitlink-flag":
            # G1 (D03): a 160000 gitlink entry on tools/sub, committed, then skip-worktree (the
            # writer selftest case_18 shape); status hides the gitlink, the flag check classes it.
            head = git_run(repo, ["rev-parse", "HEAD"]).stdout.decode().strip()
            r = git_run(repo, ["update-index", "--add", "--cacheinfo", f"160000,{head},tools/sub"])
            if r.returncode != 0:
                raise CaseError("gitlink update-index failed")
            dates = {"GIT_AUTHOR_DATE": GIT_DATE, "GIT_COMMITTER_DATE": GIT_DATE}
            r = git_run(repo, ["commit", "-q", "-m", "gitlink seed"], env=dates)
            if r.returncode != 0:
                raise CaseError(f"gitlink commit failed: {r.stderr.decode('utf-8', 'replace').strip()}")
            r = git_run(repo, ["update-index", "--skip-worktree", "tools/sub"])
            if r.returncode != 0:
                raise CaseError("gitlink skip-worktree failed")
        elif kind == "absent-flag":
            # A9 (D04): skip-worktree on tools/notes.txt whose worktree file is removed; status
            # hides the deletion, the flag check classes RECEIPT-INDEX-CONCEALED-ABSENT.
            r = git_run(repo, ["update-index", "--skip-worktree", "tools/notes.txt"])
            if r.returncode != 0:
                raise CaseError("absent skip-worktree failed")
            os.remove(os.path.join(repo, "tools", "notes.txt"))
        elif kind == "fsmonitor-silent":
            # F1 (D19): repo config core.fsmonitor names a silent hook that prints one timestamp
            # line and no changed paths (the v1 fsmonitor hook contract), and the dirty entry is
            # marked fsmonitor-valid, so an fsmonitor-trusting status read sees a clean tree while
            # the writer's -c core.fsmonitor=false pin sees the dirty append (probed 2026-11-05:
            # `git status --porcelain` prints nothing with the hook and ` M tracked.txt` with the
            # pin, /fast/scratch/hyaku/souji-r69/probe/fsm).
            hook = os.path.join(os.path.dirname(repo), "silent-fsmonitor.sh")
            with open(hook, "wb") as f:
                f.write(b"#!/bin/sh\necho 1762348800\nexit 0\n")
            os.chmod(hook, 0o755)
            r = git_run(repo, ["config", "core.fsmonitor", hook])
            if r.returncode != 0:
                raise CaseError("fsmonitor config failed")
            if not spec.get("dirty"):
                raise CaseError("fsmonitor-silent requires the dirty branch for its target edit")
            r = git_run(repo, ["update-index", "--fsmonitor-valid", "tools/notes.txt"])
            if r.returncode != 0:
                raise CaseError("fsmonitor-valid mark failed")
        elif kind == "git-dir-copy":
            # W7 (D21): a byte copy of .git beside the repo whose config sets core.fileMode=false
            # and names the fixture repo as core.worktree; a caller-injected GIT_DIR pointed here
            # makes an unscrubbed status read see the clean poisoned view. The honest writer
            # scrubs GIT_DIR, so the dirty check refuses on the real repository.
            dst = os.path.join(case_dir, "gitdir-copy")
            shutil.copytree(os.path.join(repo, ".git"), dst, symlinks=True)
            with open(os.path.join(dst, "config"), "a", encoding="utf-8") as f:
                f.write("[core]\n\tfileMode = false\n\tworktree = %s\n" % repo)
            if not os.path.isfile(os.path.join(dst, "config")):
                raise CaseError("gitdir-copy config missing")
        elif kind in ("attr-source-filter", "attr-source-text"):
            # AS1/AS2/ASh: a commit object (not on any ref) whose tree holds only .gitattributes;
            # its id is the caller's GIT_ATTR_SOURCE (read back by _row_env).
            line = (b"tools/counter.py filter=t\n" if kind == "attr-source-filter" else b"*.md text\n")
            if kind == "attr-source-filter":
                _cfg(repo, "filter.t.clean", FILTER_CLEAN)
            blob = _git_in(repo, ["hash-object", "-w", "--stdin"], line)
            tree = _git_in(repo, ["mktree"], b"100644 blob %s\t.gitattributes\n" % blob.encode())
            commit = _git_in(repo, ["commit-tree", "-m", "r71 attr source", tree], b"",
                             env={"GIT_AUTHOR_DATE": GIT_DATE, "GIT_COMMITTER_DATE": GIT_DATE})
            with open(os.path.join(case_dir, "attr-source.txt"), "w", encoding="ascii") as f:
                f.write(commit)
        elif kind in ("committed-filter", "committed-filter-nodriver", "driver-unused"):
            # FC1/FC2/FCh/FCh2: a committed .gitattributes; FCh2 names only a path that is not
            # tracked, so its configured driver applies to no tracked path.
            line = b"nosuch.bin filter=t\n" if kind == "driver-unused" else b"tools/counter.py filter=t\n"
            with open(os.path.join(repo, ".gitattributes"), "wb") as f:
                f.write(line)
            dates = {"GIT_AUTHOR_DATE": GIT_DATE, "GIT_COMMITTER_DATE": GIT_DATE}
            for args in (["add", ".gitattributes"], ["commit", "-q", "-m", "r71 attributes"]):
                r = git_run(repo, args, env=dates)
                if r.returncode != 0:
                    raise CaseError(f"attributes {args[0]} failed: {r.stderr.decode('utf-8', 'replace').strip()}")
            if kind != "committed-filter-nodriver":
                _cfg(repo, "filter.t.clean", FILTER_CLEAN)
        elif kind == "info-attributes-filter":
            # FC3: the attribute lives in $GIT_DIR/info/attributes (never committed, never in status).
            os.makedirs(os.path.join(repo, ".git", "info"), exist_ok=True)
            with open(os.path.join(repo, ".git", "info", "attributes"), "wb") as f:
                f.write(b"tools/counter.py filter=t\n")
            _cfg(repo, "filter.t.clean", FILTER_CLEAN)
        elif kind == "local-filemode":
            # FM1/FM2/FMh: repository-local core.fileMode=false (the r68 PK4/PK7 rows inject it
            # only through caller global/system config files, which the writer already pins).
            _cfg(repo, "core.fileMode", "false")
            if spec.get("chmod_notes"):
                os.chmod(os.path.join(repo, "tools", "notes.txt"), 0o755)
        elif kind == "info-process-filter":
            # FWp: a long-running process driver (no clean key) named by info/attributes.
            pf = os.path.join(case_dir, "proc-filter.py")
            with open(pf, "w", encoding="utf-8") as f:
                f.write(PROC_FILTER_CODE)
            os.makedirs(os.path.join(repo, ".git", "info"), exist_ok=True)
            with open(os.path.join(repo, ".git", "info", "attributes"), "wb") as f:
                f.write(b"tools/counter.py filter=p\n")
            _cfg(repo, "filter.p.process", f"{sys.executable} -B {pf}")
        elif kind == "worktree-only-attributes":
            # FWw: commit an EMPTY .gitattributes (index size 0, so git re-hashes it through its
            # filter), then give the worktree copy a self-erasing filter and the forging driver.
            with open(os.path.join(repo, ".gitattributes"), "wb") as f:
                f.write(b"")
            dates = {"GIT_AUTHOR_DATE": GIT_DATE, "GIT_COMMITTER_DATE": GIT_DATE}
            for args in (["add", ".gitattributes"], ["commit", "-q", "-m", "r72 empty attributes"]):
                r = git_run(repo, args, env=dates)
                if r.returncode != 0:
                    raise CaseError(f"attributes {args[0]} failed: {r.stderr.decode('utf-8', 'replace').strip()}")
            with open(os.path.join(repo, ".gitattributes"), "wb") as f:
                f.write(b".gitattributes filter=e\ntools/counter.py filter=t\n")
            _cfg(repo, "filter.e.clean", "cat >/dev/null")
            _cfg(repo, "filter.t.clean", FILTER_CLEAN)
        elif kind == "info-filter-named-set":
            # FWs: a driver literally named `set` (check-attr prints the same text as the boolean state).
            os.makedirs(os.path.join(repo, ".git", "info"), exist_ok=True)
            with open(os.path.join(repo, ".git", "info", "attributes"), "wb") as f:
                f.write(b"tools/counter.py filter=set\n")
            _cfg(repo, "filter.set.clean", FILTER_CLEAN)
        elif kind != "replace-base":
            raise CaseError(f"unknown env_kind {kind!r}")


def _cfg(repo: str, key: str, val: str) -> None:
    r = git_run(repo, ["config", key, val])
    if r.returncode != 0:
        raise CaseError(f"fixture config {key} failed")


def _git_in(repo: str, args: list[str], data: bytes, env: Optional[dict] = None) -> str:
    r = subprocess.run(["git", "-C", repo, *args], input=data, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=clean_env(env), timeout=120)
    out = r.stdout.decode().strip()
    if r.returncode != 0 or not out:
        raise CaseError(f"git {args[0]} failed: {r.stderr.decode('utf-8', 'replace').strip()}")
    return out


def build_case(work: str, letter: str, which: str, spec: dict) -> tuple[str, str]:
    """Per (row, slot) fixture: work/<letter>/<which>/{repo,out}. Returns (repo, rev)."""
    case_dir = os.path.join(work, letter, which)
    repo_name = spec.get("repo_name", "repo")
    repo, rev = build_repo_at(os.path.join(case_dir, repo_name))
    mutate(repo, spec)
    _r73_prerun(repo, spec)
    os.makedirs(os.path.join(case_dir, "out"), exist_ok=True)
    return repo, rev


def _r73_prerun(repo: str, spec: dict) -> None:
    """r73 pre-run set-up for the FX rows (after mutate())."""
    if spec.get("index_stat"):
        rel, forged = spec["index_stat"]
        r = subprocess.run([sys.executable, "-c", INDEX_STAT_CODE, repo, rel, _b(forged)],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=clean_env(), timeout=120)
        if r.returncode != 0:
            raise CaseError(f"index-stat forge failed: {r.stderr.decode('utf-8', 'replace').strip()}")
    if spec.get("stale_stat"):
        p = os.path.join(repo, spec["stale_stat"])
        s = os.stat(p)
        os.utime(p, ns=(s.st_atime_ns, s.st_mtime_ns + 10_000_000_000))
    if spec.get("autocrlf_crlf"):
        rel = spec["autocrlf_crlf"]
        _cfg(repo, "core.autocrlf", "true")
        with open(os.path.join(repo, rel), "rb") as f:
            data = f.read()
        with open(os.path.join(repo, rel), "wb") as f:
            f.write(data.replace(b"\n", b"\r\n"))
        r = git_run(repo, ["add", "--", rel])
        if r.returncode != 0:
            raise CaseError("autocrlf re-stage failed")


def tree_divergence(repo: str, rev: str) -> list[tuple[str, str]]:
    """r73 C2 forgery witness: (path, kind) for every way the worktree differs from rev's tree, read
    without git status, the index stat cache or any filter. Kinds: missing, type, mode (exec bit),
    bytes, target (symlink), untracked (a worktree file or symlink outside the tree; `.git` excluded).
    Gitlinks are skipped. Raises CaseError when the tree cannot be read."""
    r = git_run(repo, ["ls-tree", "-r", "-z", "--full-tree", rev])
    if r.returncode != 0:
        raise CaseError(f"witness ls-tree failed: {r.stderr.decode('utf-8', 'replace').strip()}")
    ents: dict[bytes, tuple[bytes, bytes]] = {}
    for rec in r.stdout.split(b"\0"):
        if not rec:
            continue
        meta, _, path = rec.partition(b"\t")
        mode, _typ, oid = meta.split()
        ents[path] = (mode, oid)
    top = os.fsencode(repo)
    diffs: list[tuple[str, str]] = []

    def blob(oid: bytes) -> bytes:
        b = git_run(repo, ["cat-file", "blob", oid.decode()])
        if b.returncode != 0:
            raise CaseError("witness cat-file failed")
        return b.stdout

    for path, (mode, oid) in sorted(ents.items()):
        name = path.decode("utf-8", "replace")
        full = os.path.join(top, path)
        try:
            s = os.lstat(full)
        except FileNotFoundError:
            diffs.append((name, "missing"))
            continue
        if mode == b"160000":
            continue
        if mode == b"120000":
            if not stat.S_ISLNK(s.st_mode):
                diffs.append((name, "type"))
            elif os.readlink(full) != blob(oid):
                diffs.append((name, "target"))
            continue
        if not stat.S_ISREG(s.st_mode):
            diffs.append((name, "type"))
            continue
        if bool(s.st_mode & 0o111) != (mode == b"100755"):
            diffs.append((name, "mode"))
        with open(full, "rb") as f:
            if f.read() != blob(oid):
                diffs.append((name, "bytes"))
    for dirpath, dirnames, filenames in os.walk(top):
        rel_dir = os.path.relpath(dirpath, top)
        rel_dir = b"" if rel_dir == b"." else rel_dir
        if rel_dir == b"":
            dirnames[:] = [d for d in dirnames if d != b".git"]
        links = [d for d in dirnames if os.path.islink(os.path.join(dirpath, d))]
        for leaf in filenames + links:
            rel = rel_dir + b"/" + leaf if rel_dir else leaf
            if rel not in ents:
                diffs.append((rel.decode("utf-8", "replace"), "untracked"))
    return diffs


# r74 C2: the path(s) each in-run kind's forging step writes (preregistration.txt C2, frozen).
INRUN_FORGED = {
    "edit-counter-samesize": "tools/counter.py", "restore-unset-driver": "tools/counter.py",
    "create-driver-forge": "tools/counter.py", "index-stat-counter": "tools/counter.py",
    "flag": "tools/counter.py",
    "chmod-clean": "tools/notes.txt", "chmod-dirty": "tools/notes.txt", "chmod-setuid": "tools/notes.txt",
    "chmod-sticky": "tools/notes.txt", "edit-noninstrument": "tools/notes.txt",
    "transient-restore": "tools/notes.txt", "append-dirty": "tools/notes.txt",
    "edit-instrument": "tools/instr.sh", "index-stat-instrument": "tools/instr.sh",
    "untracked": "tools/extra.txt", "untracked-dir-new": "tools/extra/new.txt",
    "symlink-retarget": "tools/extra/link", "symlink-retarget-same": "tools/extra/link",
}


def forge_paths(spec: dict) -> set:
    """r74 C2: the repo-relative paths the row's forging step writes. Empty = no declared forgery."""
    paths = set()
    if spec.get("target"):
        paths.add(spec["target"])
    elif spec.get("inrun") in INRUN_FORGED:
        paths.add(INRUN_FORGED[spec["inrun"]])
    if spec.get("chmod_notes"):
        paths.add("tools/notes.txt")
    if spec.get("index_stat"):
        paths.add(spec["index_stat"][0])
    return paths


def row_scope(spec: dict, diffs):
    """r74 C2: the divergences on the row's forged paths only; None (a failed read) stays None."""
    if diffs is None:
        return None
    fp = forge_paths(spec)
    return [d for d in diffs if d[0] in fp]


def case_env(spec: dict, repo: str) -> Optional[dict]:
    """r70: the carried row env (r69 rules, unchanged) with the row's `pathspec_env` merged last."""
    base = _row_env(spec, repo)
    ps = spec.get("pathspec_env")
    if not ps:
        return base
    merged = dict(base or {})
    merged.update(ps)
    return merged


def _row_env(spec: dict, repo: str) -> Optional[dict]:
    if spec.get("use_env_index"):
        return {"GIT_INDEX_FILE": os.path.join(repo, ".git", "alt-idx")}
    if spec.get("env_index_missing"):
        # P13: the env var names a path that does not exist; the base writer's `git ls-files -v -z`
        # prints nothing and exits 0, so its flag loop passes vacuously. The new writer refuses the
        # env var's presence before any git call.
        return {"GIT_INDEX_FILE": os.path.join(repo, ".git", "idx-missing-r65")}
    kind = spec.get("env_kind")
    if kind == "count-excludes":
        # E1: the GIT_CONFIG_COUNT pair injects core.excludesFile into every git call the base
        # writer makes; the injected exclude file hides tools/hidden.txt from the status reads.
        return {"GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "core.excludesFile",
                "GIT_CONFIG_VALUE_0": os.path.join(os.path.dirname(repo), "excludes.txt")}
    if kind == "params-excludes":
        # E2: the legacy single-quoted GIT_CONFIG_PARAMETERS form carries the same excludesFile.
        return {"GIT_CONFIG_PARAMETERS":
                "'core.excludesFile=%s'" % os.path.join(os.path.dirname(repo), "excludes.txt")}
    if kind == "global-excludes":
        # E3: a crafted global config file; the writer repoints GIT_CONFIG_GLOBAL to the null
        # device, so the excluded file shows up untracked and the dirty check refuses.
        return {"GIT_CONFIG_GLOBAL": os.path.join(os.path.dirname(repo), "global.gitconfig")}
    if kind == "object-dir":
        # E4: a byte-identical copy of the object store as the primary object directory.
        return {"GIT_OBJECT_DIRECTORY": os.path.join(repo, ".git", "objects-copy")}
    if kind == "alternates":
        # E5: an empty alternates directory injected into every object lookup.
        return {"GIT_ALTERNATE_OBJECT_DIRECTORIES": os.path.join(repo, ".git", "alternates-empty")}
    if kind == "replace-base":
        # E6: a forged replace-ref namespace base.
        return {"GIT_REPLACE_REF_BASE": "refs/replace-forged-r66/"}
    if kind == "common-dir-copy":
        # W1/W2: the caller repoints the common dir at the beside-repo copy whose config sets
        # core.fileMode=false (W1 also carries a tracked 755->644 change the redirect hides).
        return {"GIT_COMMON_DIR": os.path.join(os.path.dirname(repo), "commondir-copy")}
    if kind == "common-dir-real":
        # W3: the caller's value equals the repository's own resolved common dir (canonicalized);
        # a harmless, already-neutralized value the candidate keeps accepting.
        return {"GIT_COMMON_DIR": os.path.realpath(os.path.join(repo, ".git"))}
    if kind == "common-dir-rel-poison":
        # W4: relative caller value; git -C <root> resolves it against the ROOT (main/main/.git,
        # the poison) while the scrubbed writer resolves nothing from it at all (P-rel2 shape).
        return {"GIT_COMMON_DIR": "main/.git"}
    if kind == "common-dir-empty":
        # W5: the empty-string caller value; the writer refuses it before any git call.
        return {"GIT_COMMON_DIR": ""}
    if kind == "common-dir-alias":
        # W6: the caller value is a symlink to the repository's own common dir (honest).
        return {"GIT_COMMON_DIR": os.path.join(os.path.dirname(repo), "alias-git")}
    if kind == "exclude-repo-local":
        # PK3: no caller env; the route is repository-local config, closed by the -c pin.
        return {}
    if kind == "global-filemode":
        # PK4: the caller names the global config file whose core.fileMode=false hides the mode change.
        return {"GIT_CONFIG_GLOBAL": os.path.join(os.path.dirname(repo), "global-mode.gitconfig")}
    if kind == "system-filemode":
        # PK7: the caller names the system config file whose core.fileMode=false hides the mode
        # change. The r69 counter's clean_env pins GIT_CONFIG_NOSYSTEM=1 (hermeticity), which
        # would otherwise neuter this row for every slot, so the caller env explicitly clears the
        # pin (GIT_CONFIG_NOSYSTEM=0) and each writer's OWN `git()` pin is what defends: the
        # candidate sets it, the K7 mutant does not, so the mutant reads the caller's system file
        # and forges (probed 2026-11-05: without the override K7 survived).
        return {"GIT_CONFIG_SYSTEM": os.path.join(os.path.dirname(repo), "system-mode.gitconfig"),
                "GIT_CONFIG_NOSYSTEM": "0"}
    if kind == "git-dir-copy":
        # W7: the caller repoints GIT_DIR at the beside-repo copy whose config sets
        # core.fileMode=false and names the fixture repo as core.worktree (mode_change in spec).
        return {"GIT_DIR": os.path.join(os.path.dirname(repo), "gitdir-copy")}
    if kind == "replace-ref-head":
        # PK6: repository-state route (refs/replace); no caller env.
        return {}
    if kind in ("attr-source-filter", "attr-source-text"):
        # AS1/AS2/ASh: the caller's GIT_ATTR_SOURCE names the beside-HEAD attributes commit.
        try:
            with open(os.path.join(os.path.dirname(repo), "attr-source.txt"), encoding="ascii") as f:
                return {"GIT_ATTR_SOURCE": f.read().strip()}
        except OSError as exc:
            raise CaseError(f"attr-source.txt unreadable: {exc}")
    if kind in ("committed-filter", "committed-filter-nodriver", "driver-unused",
                "info-attributes-filter", "local-filemode", "info-process-filter",
                "worktree-only-attributes", "info-filter-named-set"):
        # FC*/FM*: repository-state routes; no caller env.
        return {}
    return None


def run_slot(slot: str, repo: str, rev: str, out: str, allow_dirty: bool,
             wrapped: list[str], root: Optional[str] = None,
             instrument: str = "tools/instr.sh",
             env_extra: Optional[dict] = None,
             cwd: Optional[str] = None) -> tuple[int, str, str]:
    argv = [sys.executable, "-B", slot, "--root", root or repo, "--rev", rev,
            "--instrument", instrument, "--out", out, "--allow-outside"]
    if allow_dirty:
        argv.append("--allow-dirty")
    argv += ["--", *wrapped]
    try:
        p = subprocess.run(argv, cwd=cwd or repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           env=clean_env(env_extra), timeout=180)
    except subprocess.TimeoutExpired:
        return 124, "", "timeout after 180s"
    except OSError as exc:
        return 125, "", f"launch failed: {exc}"
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def judge(rc: int, out: str) -> str:
    if rc == 0 and os.path.isfile(out):
        return "accept"
    if rc == 2 and not os.path.lexists(out):
        return "refuse"
    return "error"


def findings_for(verdict: str, stderr: str, klass: str) -> str:
    if verdict == "refuse" and klass and klass in stderr:
        return klass
    return "-"


def echo_violation(spec: dict, env_extra: Optional[dict], stderr: str) -> bool:
    """D30 no-echo judge: true when a refusal message printed an exact caller value the row's
    frozen noecho_env forbids. The value must appear verbatim (substring) in the new slot's stderr.
    Accept rows never violate (their expected stderr is empty)."""
    for key in spec.get("noecho_env", []) or []:
        val = (env_extra or {}).get(key)
        if val and val in stderr:
            return True
    return False


def one_line(text: str, limit: int = 160) -> str:
    s = " ".join((text or "").split())
    return (s[: limit - 3] + "...") if len(s) > limit else s


def load_matrix(path: str) -> tuple[Optional[list[tuple[str, str, str, str]]], str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except OSError as exc:
        return None, f"cannot read matrix: {exc}"
    lines = [l for l in raw.splitlines() if l.strip()]
    if not lines:
        return None, "matrix is empty"
    if lines[0].split("\t") != ["case", "expect", "expected_class", "base_expect"]:
        return None, f"bad header: {lines[0]!r}"
    rows: list[tuple[str, str, str, str]] = []
    for i, line in enumerate(lines[1:], 2):
        parts = line.split("\t")
        if len(parts) != 4:
            return None, f"line {i}: expected 4 tab-separated fields, got {len(parts)}"
        case, expect, klass, base_expect = parts
        if base_expect not in ("accept", "refuse"):
            return None, f"line {i}: base_expect must be accept|refuse, got {base_expect!r}"
        if expect not in ("accept", "refuse"):
            return None, f"line {i}: expect must be accept|refuse, got {expect!r}"
        if expect == "refuse" and not klass:
            return None, f"line {i}: refuse row needs a non-empty expected_class"
        if expect == "accept" and klass != "-":
            return None, f"line {i}: accept row must use '-' as expected_class"
        rows.append((case, expect, klass, base_expect))
    if [r[0] for r in rows] != CASE_ORDER:
        return None, f"matrix rows must be {CASE_ORDER} in order, got {[r[0] for r in rows]}"
    return rows, ""


def spec_agreement(rows: list[tuple[str, str, str]], specs: dict) -> Optional[str]:
    """CASE_SPECS must cover exactly the matrix rows, in CASE_ORDER. Returns an error or None."""
    letters = [r[0] for r in rows]
    if letters != CASE_ORDER:
        return f"matrix rows {letters} != CASE_ORDER {CASE_ORDER}"
    missing = [k for k in letters if k not in specs]
    extra = [k for k in specs if k not in letters]
    if missing or extra:
        return f"CASE_SPECS disagrees with matrix: missing={missing} extra={extra}"
    return None


def git_show(root: str, spec: str) -> tuple[Optional[bytes], str]:
    r = subprocess.run(["git", "-C", root, "show", spec], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=clean_env(), timeout=120)
    if r.returncode != 0 or not r.stdout:
        detail = r.stderr.decode("utf-8", "replace").strip()
        return None, f"{spec}: {detail or 'empty'}"
    return r.stdout, ""


def write_exec(path: str, data: bytes) -> str:
    with open(path, "wb") as f:
        f.write(data)
    os.chmod(path, 0o755)
    return hashlib.sha256(data).hexdigest()


def fixture_from_blob(root: str, base_rev: str, work: str) -> tuple[Optional[str], str]:
    """r68 M10 fix: the regress fixture is read from the --base-rev BLOB, never from a lane clone
    at HEAD (round-67 lesson M10: the r67 counter's fixture_from_clone cloned the lane at HEAD and
    the base-blob cross-check was printed but not part of the verdict). Returns (fixture_path, error).
    """
    blob, err = git_show(root, f"{base_rev}:{FIXTURE_REL}")
    if blob is None:
        return None, f"fixture blob unreadable at {base_rev}: {err}"
    rdir = os.path.join(work, "regress")
    os.makedirs(rdir, exist_ok=True)
    fixture = os.path.join(rdir, "r60-receipt-write.py")
    with open(fixture, "wb") as f:
        f.write(blob)
    return fixture, ""


def run_fixture(fixture: str, slot: str, wdir: str, cwd: str) -> tuple[bool, str, str]:
    os.makedirs(wdir, exist_ok=True)
    try:
        p = subprocess.run([sys.executable, "-B", fixture, "--tool", slot, "--work", wdir],
                           cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           env=clean_env(), timeout=900)
    except (subprocess.TimeoutExpired, OSError) as exc:
        return False, f"fixture launch failed: {exc}", ""
    text = p.stdout.decode("utf-8", "replace")
    lines = [l for l in text.splitlines() if l.strip()]
    last = lines[-1] if lines else ""
    ok = p.returncode == 0 and FIXTURE_LAST_WANT in last
    return ok, f"rc={p.returncode}", last


def evaluate(rows, base_slot: str, new_slot: str, work: str, fixture: Optional[str]) -> dict:
    """Run every frozen row against both slots. Returns counts, per-row fates, detail lines and the
    regress verdict. `row_fate` drives the battery arm's outcome classification (Q131)."""
    lines: list[str] = []
    c = {"base_forgeries": 0, "base_honest": 0, "new_forgeries": 0, "new_honest": 0,
         "class_mismatches": 0, "new_echo": 0, "errors": 0, "base_mismatches": 0,
         "base_unwitnessed": 0, "new_unwitnessed": 0}
    all_new_match = True
    row_fate: list[dict] = []
    for letter, expect, klass, base_expect in rows:
        spec = CASE_SPECS[letter]
        try:
            b_repo, b_rev = build_case(work, letter, "base", spec)
            n_repo, n_rev = build_case(work, letter, "new", spec)
        except CaseError as exc:
            lines.append(f"CASE {letter} expect={expect} base=error base_findings=- new=error new_findings=-")
            lines.append(f"# detail {letter} name={spec['name']} build_failed: {exc}")
            all_new_match = False
            c["errors"] += 1
            c["base_mismatches"] += 1
            row_fate.append({"letter": letter, "expect": expect, "verdict": "error",
                             "class_ok": False, "echo": False, "base": "error", "witness": False})
            continue
        allow_dirty = bool(spec.get("allow_dirty"))
        rootsub = spec.get("rootsub")
        root_b = os.path.join(b_repo, rootsub) if rootsub else b_repo
        root_n = os.path.join(n_repo, rootsub) if rootsub else n_repo
        instrument = "instr.sh" if rootsub else "tools/instr.sh"
        cwd = (os.path.dirname(b_repo) if spec.get("cwd_parent")
               else os.path.join(b_repo, ".git") if spec.get("cwd_gitdir") else None)
        cwd_n = (os.path.dirname(n_repo) if spec.get("cwd_parent")
                 else os.path.join(n_repo, ".git") if spec.get("cwd_gitdir") else None)
        if spec.get("cwd_parent"):
            # W4: instrument named from the repo root, writer cwd at the parent (P-rel2 shape).
            instrument = "instr.sh"
        b_out = os.path.join(work, letter, "base", "out", "receipt.txt")
        n_out = os.path.join(work, letter, "new", "out", "receipt.txt")
        try:
            b_pre, n_pre = tree_divergence(b_repo, b_rev), tree_divergence(n_repo, n_rev)
        except CaseError:
            b_pre = n_pre = None
        b_rc, _, b_se = run_slot(base_slot, b_repo, b_rev, b_out, allow_dirty,
                                 wrapped_argv(spec, b_repo), root=root_b, instrument=instrument,
                                 env_extra=case_env(spec, b_repo), cwd=cwd)
        n_rc, _, n_se = run_slot(new_slot, n_repo, n_rev, n_out, allow_dirty,
                                 wrapped_argv(spec, n_repo), root=root_n, instrument=instrument,
                                 env_extra=case_env(spec, n_repo), cwd=cwd_n)
        b_v, n_v = judge(b_rc, b_out), judge(n_rc, n_out)
        try:
            b_post, n_post = tree_divergence(b_repo, b_rev), tree_divergence(n_repo, n_rev)
        except CaseError:
            b_post = n_post = None
        # r74 C2: the witness reads only the row's forged paths (a set-up divergence elsewhere is not one).
        b_pre, b_post = row_scope(spec, b_pre), row_scope(spec, b_post)
        n_pre, n_post = row_scope(spec, n_pre), row_scope(spec, n_post)
        # r73 C2: a witness read that fails is never a witness (fail closed: unwitnessed).
        b_wit = bool(b_pre is not None and b_post is not None and (b_pre or b_post))
        n_wit = bool(n_pre is not None and n_post is not None and (n_pre or n_post))
        b_f, n_f = findings_for(b_v, b_se, klass), findings_for(n_v, n_se, klass)
        n_echo = echo_violation(spec, case_env(spec, n_repo), n_se)
        if b_v != base_expect:
            c["base_mismatches"] += 1
        lines.append(f"CASE {letter} expect={expect} base={b_v} base_findings={b_f} "
                     f"new={n_v} new_findings={n_f} new_echo={str(n_echo).lower()} "
                     f"base_expect={base_expect} base_witness={'yes' if b_wit else 'no'} "
                     f"new_witness={'yes' if n_wit else 'no'}")
        lines.append(f"# detail {letter} name={spec['name']} rev={n_rev[:12]} "
                     f"base_rc={b_rc} new_rc={n_rc} base_stderr={one_line(b_se)} "
                     f"new_stderr={one_line(n_se)}")
        if n_v == "error":
            c["errors"] += 1
        if expect == "refuse":
            if b_v == "accept":
                if b_wit:
                    c["base_forgeries"] += 1
                else:
                    c["base_unwitnessed"] += 1
            if n_v == "accept":
                c["new_forgeries"] += 1
                if not n_wit:
                    c["new_unwitnessed"] += 1
            if not (n_v == "refuse" and klass and klass in n_se):
                c["class_mismatches"] += 1
        else:
            if b_v == "accept":
                c["base_honest"] += 1
            if n_v == "accept":
                c["new_honest"] += 1
        if n_echo:
            c["new_echo"] += 1
        if n_v != expect:
            all_new_match = False
        row_fate.append({"letter": letter, "expect": expect, "verdict": n_v,
                         "class_ok": bool(n_v == "refuse" and klass and klass in n_se),
                         "echo": n_echo, "base": b_v, "witness": n_wit})

    if fixture is None:
        regress_base = regress_new = "SKIP"
        lines.append("# regress arm skipped")
    else:
        rdir = os.path.join(work, "regress")
        reg_base_ok, reg_base_detail, reg_base_last = run_fixture(
            fixture, base_slot, os.path.join(rdir, "base-r60"), rdir)
        reg_new_ok, reg_new_detail, reg_new_last = run_fixture(
            fixture, new_slot, os.path.join(rdir, "new-r60"), rdir)
        regress_base = "PASS" if reg_base_ok else "FAIL"
        regress_new = "PASS" if reg_new_ok else "FAIL"
        lines.append(f"# regress-detail base {reg_base_detail} last={one_line(reg_base_last)}")
        lines.append(f"# regress-detail new {reg_new_detail} last={one_line(reg_new_last)}")
    if regress_base == "SKIP":
        regress = "SKIP"
    else:
        regress = "PASS" if (regress_base == "PASS" and regress_new == "PASS") else "FAIL"
    return {"lines": lines, "counts": c, "all_new_match": all_new_match, "regress": regress,
            "regress_base": regress_base, "regress_new": regress_new, "row_fate": row_fate,
            "n_accept": sum(1 for r in rows if r[1] == "accept"),
            "n_refuse": sum(1 for r in rows if r[1] == "refuse")}


def claim_upheld(res: dict) -> bool:
    c = res["counts"]
    return (c["new_forgeries"] == 0 and c["new_honest"] == res["n_accept"]
            and c["class_mismatches"] == 0 and c["new_echo"] == 0
            and res["regress"] == "PASS" and res["all_new_match"]
            and c.get("base_mismatches", 1) == 0
            and c.get("base_unwitnessed", 1) == 0
            and c.get("new_unwitnessed", 1) == 0)


def summary_line(rows, res: dict) -> str:
    c = res["counts"]
    return (f"SUMMARY matrix={len(rows)} base_forgeries={c['base_forgeries']} "
            f"base_honest={c['base_honest']} base_mismatches={c['base_mismatches']} "
            f"base_unwitnessed={c['base_unwitnessed']} new_unwitnessed={c['new_unwitnessed']} "
            f"new_forgeries={c['new_forgeries']} "
            f"new_honest={c['new_honest']} class_mismatches={c['class_mismatches']} "
            f"new_echo={c['new_echo']} errors={c['errors']} "
            f"regress={res['regress']}")


def classify_outcome(res: dict) -> str:
    """Q131 outcome split for one battery mutant, from the per-row fates of its run. Precedence
    (the first class that has a row wins): error, forgery, echo-violation, over-refusal,
    label-only, survived. Only forgery-based refutations are declared-protection kills."""
    fates = res["row_fate"]
    # r73 C2: an accepted refuse row is a forgery kill only when its fixture's divergence was observed;
    # an unwitnessed one is an invalid fixture and classifies as error.
    errors = sum(1 for f in fates if f["verdict"] == "error"
                 or (f["expect"] == "refuse" and f["verdict"] == "accept" and not f["witness"]))
    forgeries = sum(1 for f in fates if f["expect"] == "refuse" and f["verdict"] == "accept"
                    and f["witness"])
    echo = sum(1 for f in fates if f["echo"])
    honest = sum(1 for f in fates if f["expect"] == "accept" and f["verdict"] == "refuse")
    label = sum(1 for f in fates if f["expect"] == "refuse" and f["verdict"] == "refuse"
                and not f["class_ok"])
    if errors:
        return "error"
    if forgeries:
        return "forgery"
    if echo:
        return "echo-violation"
    if honest:
        return "over-refusal"
    if label:
        return "label-only"
    return "survived"


def outcome_counts(res: dict) -> dict:
    fates = res["row_fate"]
    return {
        "forgeries": sum(1 for f in fates if f["expect"] == "refuse" and f["verdict"] == "accept"
                         and f["witness"]),
        "echo": sum(1 for f in fates if f["echo"]),
        "honest": sum(1 for f in fates if f["expect"] == "accept" and f["verdict"] == "refuse"),
        "label": sum(1 for f in fates if f["expect"] == "refuse" and f["verdict"] == "refuse"
                     and not f["class_ok"]),
        "errors": sum(1 for f in fates if f["verdict"] == "error"
                      or (f["expect"] == "refuse" and f["verdict"] == "accept" and not f["witness"])),
    }


def load_battery_manifest(path: str) -> tuple[Optional[list[tuple[str, str]]], str]:
    """TSV: name<TAB>expected_outcome. Outcomes are the frozen vocabulary; names are unique."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except OSError as exc:
        return None, f"cannot read battery manifest: {exc}"
    lines = [l for l in raw.splitlines() if l.strip()]
    if not lines:
        return None, "battery manifest is empty"
    if lines[0].split("\t") != ["mutant", "expected_outcome"]:
        return None, f"bad battery manifest header: {lines[0]!r}"
    out: list[tuple[str, str]] = []
    seen = set()
    vocab = ("forgery", "echo-violation", "over-refusal", "label-only", "survived", "error")
    for i, line in enumerate(lines[1:], 2):
        parts = line.split("\t")
        if len(parts) != 2:
            return None, f"battery manifest line {i}: expected 2 fields, got {len(parts)}"
        name, exp = parts
        if exp not in vocab:
            return None, f"battery manifest line {i}: outcome {exp!r} not in {vocab}"
        if name in seen:
            return None, f"battery manifest line {i}: duplicate mutant {name!r}"
        seen.add(name)
        out.append((name, exp))
    return out, ""


def battery_verdict(results: list[tuple[str, str, str]]) -> tuple[dict, bool, int]:
    """r70 C2: the battery's pure verdict over (name, observed, expected) triples. rc 0 iff every
    observed outcome equals its expectation and no mutant survived or errored."""
    tally = {"forgery": 0, "echo-violation": 0, "over-refusal": 0,
             "label-only": 0, "survived": 0, "error": 0}
    all_match = True
    for name, obs, exp in results:
        tally[obs] += 1
        if obs != exp:
            all_match = False
    rc = 0 if (all_match and tally["survived"] == 0 and tally["error"] == 0) else 1
    return tally, all_match, rc


MEMBER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def verify_members(battery_dir: str, names: list[str]) -> tuple[Optional[dict], str]:
    """r70 C2 (r69 routed F-3): read <battery_dir>/SHA256SUMS (`<64hex>  <file>` lines) and require
    every named member `<name>.py` to be listed once and to hash to its listed digest. Returns
    ({name: sha256, '__sums__': sha256 of the sums file}, '') or (None, reason)."""
    for name in names:
        # r71 (S70Sentinel F3/F4): a member name is one plain path component.
        if not MEMBER_RE.match(name):
            return None, f"member name {name!r} is not a plain file name"
    sums_path = os.path.join(battery_dir, "SHA256SUMS")
    try:
        with open(sums_path, "rb") as f:
            sums_raw = f.read()
    except OSError as exc:
        return None, f"cannot read {sums_path}: {exc}"
    listed: dict[str, str] = {}
    for i, line in enumerate(sums_raw.decode("utf-8", "replace").splitlines(), 1):
        if not line.strip():
            continue
        m = re.match(r"^([0-9a-f]{64}) [ *](.+)$", line)
        if not m:
            return None, f"SHA256SUMS line {i} malformed"
        if "/" in m.group(2) or m.group(2).startswith("."):
            return None, f"SHA256SUMS line {i} names a non-plain file"
        if m.group(2) in listed:
            return None, f"SHA256SUMS line {i} lists {m.group(2)} twice"
        listed[m.group(2)] = m.group(1)
    out: dict[str, str] = {"__sums__": hashlib.sha256(sums_raw).hexdigest()}
    for name in names:
        fname = f"{name}.py"
        path = os.path.join(battery_dir, fname)
        if os.path.islink(path):
            return None, f"member {fname} is a symlink"
        if fname not in listed:
            return None, f"member {fname} is not listed in SHA256SUMS"
        try:
            with open(path, "rb") as f:
                digest = hashlib.sha256(f.read()).hexdigest()
        except OSError as exc:
            return None, f"member {fname} unreadable: {exc}"
        if digest != listed[fname]:
            return None, f"member {fname} sha256 {digest[:12]} != listed {listed[fname][:12]}"
        out[name] = digest
    return out, ""


# Stub writers for selftest: they mimic the CLI shape well enough to reach the judge.
ACCEPT_STUB = (
    "#!/usr/bin/env python3\n"
    "import sys\n"
    "a = sys.argv[1:]\n"
    "out = a[a.index('--out') + 1]\n"
    "with open(out, 'wb') as f:\n"
    "    f.write(b'stub-accept\\n')\n"
    "sys.exit(0)\n"
)
REFUSE_STUB = (
    "#!/usr/bin/env python3\n"
    "import sys\n"
    "sys.stderr.write('refused: stub refuses everything\\n')\n"
    "sys.exit(2)\n"
)
MSGLESS_STUB = (
    "#!/usr/bin/env python3\n"
    "import sys\n"
    "sys.stderr.write('refused: unrelated reason, message carries none of the frozen tokens\\n')\n"
    "sys.exit(2)\n"
)


def fatal(msg: str) -> int:
    print(f"C1-COUNTER-FATAL: {msg}", file=sys.stderr)
    print("EXIT=2")
    return 2


class Emitter:
    """Tee: print and keep, so --receipt can replay the run verbatim."""

    def __init__(self) -> None:
        self.lines: list[str] = []

    def __call__(self, line: str = "") -> None:
        print(line)
        self.lines.append(line)


def write_receipt(path: str, base_rev: str, command: str, lines: list[str]) -> str:
    counter_sha = hashlib.sha256(open(os.path.realpath(__file__), "rb").read()).hexdigest()
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"rev={base_rev}\n")
        f.write(f"instrument={COUNTER_REL}\n")
        f.write(f"instrument_sha256={counter_sha}\n")
        f.write(f"command={command}\n")
        for line in lines:
            f.write(line + "\n")
    return counter_sha


def selftest(rows, root: str, base_rev: str, work: str) -> int:
    global CASE_ORDER, CASE_SPECS
    import contextlib
    import io

    st = os.path.join(work, "selftest")
    shutil.rmtree(st, ignore_errors=True)
    os.makedirs(st)
    results: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        results.append((name, bool(ok), detail))

    # (1) in-process spec/matrix disagreement
    check("spec-agreement: real matrix and CASE_SPECS agree", spec_agreement(rows, CASE_SPECS) is None)
    short = {k: v for k, v in CASE_SPECS.items() if k != "T5"}
    e1 = spec_agreement(rows, short)
    check("spec-disagreement: CASE_SPECS missing a matrix row is refused", e1 is not None, e1 or "no error")
    extra = dict(CASE_SPECS)
    extra["T6"] = {"name": "synthetic"}
    e2 = spec_agreement(rows, extra)
    check("spec-disagreement: CASE_SPECS extra row is refused", e2 is not None, e2 or "no error")

    # (2) CLI-level disagreement: synthetic TSVs must make main() exit 2 before any run
    bad_missing = os.path.join(st, "bad-missing-T5.tsv")
    with open(bad_missing, "w", encoding="utf-8") as f:
        f.write("case\texpect\texpected_class\tbase_expect\n")
        for letter, expect, klass, bexp in rows:
            if letter != "T5":
                f.write(f"{letter}\t{expect}\t{klass}\t{bexp}\n")
    bad_extra = os.path.join(st, "bad-extra-T6.tsv")
    with open(bad_extra, "w", encoding="utf-8") as f:
        f.write("case\texpect\texpected_class\tbase_expect\n")
        for letter, expect, klass, bexp in rows:
            f.write(f"{letter}\t{expect}\t{klass}\t{bexp}\n")
        f.write("T6\trefuse\tRECEIPT-STATE-CHANGED-DURING-RUN\trefuse\n")
    for label, path in (("missing-row", bad_missing), ("extra-row", bad_extra)):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            rc = main(["--root", root, "--matrix", path, "--base-rev", base_rev,
                       "--new-tool", os.path.join(st, "unused.py"), "--work", work])
        check(f"cli-disagreement: synthetic TSV ({label}) refused before any run", rc == 2,
              f"rc={rc}")

    # (3) stub writers must each be rejected by the counter
    base_bytes, err = git_show(root, f"{base_rev}:{BASE_REL}")
    if base_bytes is None:
        check("base bytes readable for stub arms", False, err)
    else:
        slots = os.path.join(st, "slots")
        os.makedirs(slots)
        base_slot = os.path.join(slots, "base.py")
        write_exec(base_slot, base_bytes)
        stubs = {"accept": ACCEPT_STUB, "refuse": REFUSE_STUB, "msgless": MSGLESS_STUB}
        for name, src in stubs.items():
            spath = os.path.join(slots, f"stub-{name}.py")
            write_exec(spath, src.encode("utf-8"))
            res = evaluate(rows, base_slot, spath, os.path.join(st, f"stub-{name}"), None)
            c = res["counts"]
            detail = (f"new_forgeries={c['new_forgeries']} new_honest={c['new_honest']} "
                      f"class_mismatches={c['class_mismatches']} n_accept={res['n_accept']} "
                      f"n_refuse={res['n_refuse']}")
            rejected = not claim_upheld(res)
            if name == "accept":
                shape = c["new_forgeries"] == res["n_refuse"] and c["new_honest"] == res["n_accept"]
            elif name == "refuse":
                shape = c["new_forgeries"] == 0 and c["new_honest"] == 0 and c["class_mismatches"] == res["n_refuse"]
            else:
                shape = c["new_forgeries"] == 0 and c["new_honest"] == 0 and c["class_mismatches"] == res["n_refuse"]
            check(f"stub {name} rejected by counter", rejected and shape, detail)

    # (4) Q131 outcome classifier: synthetic fates must classify by the frozen precedence
    def fate(letter, expect, verdict, class_ok=True, echo=False, witness=True):
        return {"letter": letter, "expect": expect, "verdict": verdict,
                "class_ok": class_ok, "echo": echo, "witness": witness}
    synth = {"row_fate": [fate("D", "refuse", "accept")]}
    check("classifier: a forged receipt is a forgery kill", classify_outcome(synth) == "forgery")
    synth = {"row_fate": [fate("W1", "refuse", "refuse", class_ok=False), fate("A", "accept", "refuse")]}
    check("classifier: honest-run refusal outranks a label flip (over-refusal)",
          classify_outcome(synth) == "over-refusal")
    synth = {"row_fate": [fate("W1", "refuse", "refuse", class_ok=False)]}
    check("classifier: class-flip-only refusal is label-only", classify_outcome(synth) == "label-only")
    synth = {"row_fate": [fate("P13", "refuse", "refuse", echo=True)]}
    check("classifier: echoed caller value is echo-violation", classify_outcome(synth) == "echo-violation")
    synth = {"row_fate": [fate("A", "accept", "accept"), fate("C", "refuse", "refuse")]}
    check("classifier: an all-green run is survived", classify_outcome(synth) == "survived")
    synth = {"row_fate": [fate("A", "accept", "error")]}
    check("classifier: an error row is error, never a refutation", classify_outcome(synth) == "error")

    # (5) noecho consistency: every spec noecho_env key must be carried by that spec's case_env
    noecho_bad = []
    for letter, spec in CASE_SPECS.items():
        for key in spec.get("noecho_env", []) or []:
            env_extra = case_env(spec, "/nonexistent-repo")
            if env_extra is None or key not in env_extra:
                noecho_bad.append(f"{letter}:{key}")
    check("noecho: every noecho_env key is present in its row's caller env", not noecho_bad,
          ",".join(noecho_bad))

    # (6) round-68 M2: main()'s emit path runs on a two-row restricted matrix and emits the
    # header, slot, matrix, SUMMARY and EXIT lines (an emit-path crash cannot pass as green).
    two_tsv = os.path.join(st, "two-row.tsv")
    with open(two_tsv, "w", encoding="utf-8") as f:
        f.write("case\texpect\texpected_class\tbase_expect\n")
        for letter, expect, klass, bexp in rows[:2]:
            f.write(f"{letter}\t{expect}\t{klass}\t{bexp}\n")
    saved_order, saved_specs = CASE_ORDER, CASE_SPECS
    buf = io.StringIO()
    try:
        CASE_ORDER = CASE_ORDER[:2]
        CASE_SPECS = {k: CASE_SPECS[k] for k in CASE_ORDER}
        stub_two = os.path.join(st, "stub-accept-two.py")
        with open(stub_two, "w", encoding="utf-8") as f:
            f.write(ACCEPT_STUB)
        two_work = os.path.join(st, "two-row-work")
        os.makedirs(two_work, exist_ok=True)
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            rc = main(["--root", root, "--matrix", two_tsv, "--base-rev", base_rev,
                       "--new-tool", stub_two, "--work", two_work])
    finally:
        CASE_ORDER, CASE_SPECS = saved_order, saved_specs
    out_text = buf.getvalue()
    emitted = [tag for tag in ("# c1-counter root=", "# slot new=", "# matrix=", "SUMMARY matrix=2 ",
                               "EXIT=") if tag in out_text]
    exit_line = [l for l in out_text.splitlines() if l.startswith("EXIT=")]
    rc_line = int(exit_line[-1].split("=", 1)[1]) if exit_line else None
    check("main emit: two-row run emits header/slot/matrix/SUMMARY/EXIT lines",
          len(emitted) == 5 and rc_line == rc,
          f"tags={emitted} rc={rc} exit_line={exit_line[-1:] or ['none']}")

    # (7) r70 C2: instrument self-checks the r69 selftest lacked (S69MutTester / S69CriticClaims).
    # (7a) full Q131 precedence: forgery outranks over-refusal and echo; error outranks forgery.
    synth = {"row_fate": [fate("A", "accept", "refuse"), fate("D", "refuse", "accept")]}
    check("precedence: forgery outranks over-refusal", classify_outcome(synth) == "forgery")
    synth = {"row_fate": [fate("P13", "refuse", "refuse", echo=True), fate("D", "refuse", "accept")]}
    check("precedence: forgery outranks echo-violation", classify_outcome(synth) == "forgery")
    synth = {"row_fate": [fate("A", "accept", "refuse"), fate("P13", "refuse", "refuse", echo=True)]}
    check("precedence: echo-violation outranks over-refusal", classify_outcome(synth) == "echo-violation")
    synth = {"row_fate": [fate("D", "refuse", "accept"), fate("A", "accept", "error")]}
    check("precedence: error outranks forgery", classify_outcome(synth) == "error")
    # (7b) D30 echo judge on synthetic inputs (never exercised by the r69 selftest).
    secret = "/nonexistent-r70-echo-probe"
    spec_e = {"noecho_env": ["GIT_COMMON_DIR"]}
    check("echo judge: a refusal printing the frozen caller value is a violation",
          echo_violation(spec_e, {"GIT_COMMON_DIR": secret}, f"refused: bad {secret}\n") is True)
    check("echo judge: a refusal naming only the variable is not a violation",
          echo_violation(spec_e, {"GIT_COMMON_DIR": secret}, "refused: GIT_COMMON_DIR set\n") is False)
    check("echo judge: a value outside noecho_env is not judged",
          echo_violation({"noecho_env": []}, {"GIT_COMMON_DIR": secret}, secret) is False)
    # (7c) pure battery verdict: an expectation mismatch and a survived mutant each fail the arm.
    _, m_ok, m_rc = battery_verdict([("X1", "forgery", "forgery"), ("X2", "label-only", "forgery")])
    check("battery verdict: an outcome different from its expectation makes rc 1",
          m_ok is False and m_rc == 1, f"all_match={m_ok} rc={m_rc}")
    _, s_ok, s_rc = battery_verdict([("X1", "survived", "survived")])
    check("battery verdict: a survived mutant makes rc 1 even when expected", s_rc == 1,
          f"all_match={s_ok} rc={s_rc}")
    _, g_ok, g_rc = battery_verdict([("X1", "forgery", "forgery"), ("X2", "echo-violation", "echo-violation")])
    check("battery verdict: an all-matching battery is rc 0", g_ok is True and g_rc == 0,
          f"all_match={g_ok} rc={g_rc}")
    # (7d) member binding: a member whose bytes differ from SHA256SUMS is refused; a listed,
    # matching member is accepted; an unlisted member is refused.
    bdir = os.path.join(st, "battery-bind")
    os.makedirs(bdir)
    with open(os.path.join(bdir, "M1.py"), "wb") as f:
        f.write(b"print('m1')\n")
    with open(os.path.join(bdir, "M2.py"), "wb") as f:
        f.write(b"print('m2')\n")
    good = hashlib.sha256(b"print('m1')\n").hexdigest()
    with open(os.path.join(bdir, "SHA256SUMS"), "w", encoding="utf-8") as f:
        f.write(f"{good}  M1.py\n{hashlib.sha256(b'print(0)').hexdigest()}  M2.py\n")
    ok1, e_ok = verify_members(bdir, ["M1"])
    check("member binding: a listed matching member is accepted", ok1 is not None and ok1.get("M1") == good, e_ok)
    bad, e_bad = verify_members(bdir, ["M2"])
    check("member binding: a tampered member is refused", bad is None and "sha256" in e_bad, e_bad)
    unl, e_unl = verify_members(bdir, ["M3"])
    check("member binding: an unlisted member is refused", unl is None and "not listed" in e_unl, e_unl)

    # (8) r71 C2: the behaviours the five r70-surviving mutants X6-X10 remove (S70MutCounter).
    # (8a) X6: an errored member fails the battery even when error was its expectation.
    _, x6_ok, x6_rc = battery_verdict([("E", "error", "error")])
    check("battery verdict: an errored member makes rc 1 even when expected", x6_rc == 1,
          f"all_match={x6_ok} rc={x6_rc}")
    # (8b) X7: clean_env drops every ambient pathspec variable.
    saved_env = {k: os.environ.get(k) for k in PATHSPEC_VARS}
    try:
        for k in PATHSPEC_VARS:
            os.environ[k] = "1"
        leaked = sorted(k for k in PATHSPEC_VARS if k in clean_env())
        kept = clean_env({"GIT_LITERAL_PATHSPECS": "1"}).get("GIT_LITERAL_PATHSPECS")
    finally:
        for k, v in saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    check("clean_env: ambient pathspec variables are scrubbed", leaked == [], f"leaked={leaked}")
    check("clean_env: a row's own caller env is applied after the scrub", kept == "1", f"kept={kept}")
    # (8c) X8: case_env merges each row's pathspec_env, on its own and over a row env.
    la = case_env(CASE_SPECS["LA"], os.path.join(st, "nonexistent-repo"))
    check("case_env: LA carries GIT_LITERAL_PATHSPECS=1", (la or {}).get("GIT_LITERAL_PATHSPECS") == "1",
          f"env={la}")
    merged = case_env({"env_kind": "global-filemode", "pathspec_env": {"GIT_ICASE_PATHSPECS": "1"}},
                      os.path.join(st, "nonexistent-repo"))
    check("case_env: pathspec_env merges over a row env",
          (merged or {}).get("GIT_ICASE_PATHSPECS") == "1" and "GIT_CONFIG_GLOBAL" in (merged or {}),
          f"env={merged}")
    # (8d) X9/X10: duplicate and malformed SHA256SUMS lines are refused beside a valid line.
    ddir = os.path.join(st, "battery-dup")
    os.makedirs(ddir)
    with open(os.path.join(ddir, "M1.py"), "wb") as f:
        f.write(b"print('m1')\n")
    with open(os.path.join(ddir, "SHA256SUMS"), "w", encoding="utf-8") as f:
        f.write(f"{good}  M1.py\n{good} *M1.py\n")
    dup, e_dup = verify_members(ddir, ["M1"])
    check("member binding: a member listed twice is refused", dup is None and "twice" in e_dup, e_dup)
    mdir = os.path.join(st, "battery-malformed")
    os.makedirs(mdir)
    with open(os.path.join(mdir, "M1.py"), "wb") as f:
        f.write(b"print('m1')\n")
    with open(os.path.join(mdir, "SHA256SUMS"), "w", encoding="utf-8") as f:
        f.write(f"{good}  M1.py\nGARBAGE-LINE-NOT-A-DIGEST\n")
    mal, e_mal = verify_members(mdir, ["M1"])
    check("member binding: a malformed line beside a valid one is refused",
          mal is None and "malformed" in e_mal, e_mal)
    # (8e) S70Sentinel F3/F4: traversal names and symlinked members are refused.
    trav, e_trav = verify_members(bdir, ["../M1"])
    check("member binding: a traversal member name is refused", trav is None and "plain" in e_trav, e_trav)
    sdir = os.path.join(st, "battery-sumsname")
    os.makedirs(sdir)
    with open(os.path.join(sdir, "SHA256SUMS"), "w", encoding="utf-8") as f:
        f.write(f"{good}  ../M1.py\n")
    sn, e_sn = verify_members(sdir, ["M1"])
    check("member binding: a SHA256SUMS line naming a non-plain file is refused",
          sn is None and "non-plain" in e_sn, e_sn)
    ldir = os.path.join(st, "battery-link")
    os.makedirs(ldir)
    with open(os.path.join(st, "outside-m1.py"), "wb") as f:
        f.write(b"print('m1')\n")
    os.symlink(os.path.join(st, "outside-m1.py"), os.path.join(ldir, "M1.py"))
    with open(os.path.join(ldir, "SHA256SUMS"), "w", encoding="utf-8") as f:
        f.write(f"{good}  M1.py\n")
    lk, e_lk = verify_members(ldir, ["M1"])
    check("member binding: a symlinked member is refused", lk is None and "symlink" in e_lk, e_lk)

    # (9) r72 C1: the defects the r71 wave found in this instrument (S71MutCounter Y1 Y4 Y6 Y9 Y10,
    # S71CriticClaims Z1) and the base-slot binding (r71 routed D2).
    # (9a) base witness: each r71 forging row still forges the reference-weak base writer.
    wbytes, werr = git_show(root, f"{base_rev}:{BASE_REL}")
    if wbytes is None:
        check("base witness: base bytes readable", False, werr)
    else:
        wslot = os.path.join(st, "witness-base.py")
        write_exec(wslot, wbytes)
        wrows = [r for r in rows if r[0] in WITNESS_ROWS]
        wres = evaluate(wrows, wslot, wslot, os.path.join(st, "witness"), None)
        got = {f["letter"]: f.get("base") for f in wres["row_fate"]}
        bad = [f"{r[0]}:{got.get(r[0])}!={r[3]}" for r in wrows if got.get(r[0]) != r[3]]
        check("base witness: every r71 forging row forges the base writer as its base_expect says",
              len(wrows) == len(WITNESS_ROWS) and not bad and wres["counts"]["base_mismatches"] == 0,
              f"rows={len(wrows)} mismatches={bad}")
        # r74 (M17): the same run witnesses every accepted forging row in both slots, including the
        # in-run-only rows (AS2, FC2, FM2) whose divergence exists after the slot only.
        wc = wres["counts"]
        check("witness run: base_unwitnessed=0 and new_unwitnessed=0 over the r71 forging rows",
              wc["base_unwitnessed"] == 0 and wc["new_unwitnessed"] == 0 and wc["base_forgeries"] == len(wrows),
              f"base_unwitnessed={wc['base_unwitnessed']} new_unwitnessed={wc['new_unwitnessed']} "
              f"base_forgeries={wc['base_forgeries']}")
        # r74 (M08): a witness read that fails is unwitnessed in evaluate(), in both slots.
        def _raise(*_a, **_k):
            raise CaseError("selftest: witness read fails")
        saved_td = globals()["tree_divergence"]
        globals()["tree_divergence"] = _raise
        try:
            frows = [r for r in rows if r[0] == "FM1"]
            fres = evaluate(frows, wslot, wslot, os.path.join(st, "witness-fail"), None)
        finally:
            globals()["tree_divergence"] = saved_td
        fc = fres["counts"]
        check("witness: a failed witness read is unwitnessed (FM1, both slots)",
              len(frows) == 1 and fc["base_unwitnessed"] == 1 and fc["new_unwitnessed"] == 1
              and fc["base_forgeries"] == 0 and fres["row_fate"][0]["witness"] is False,
              f"counts={fc}")
    # (9b) the verdict reads the base slot.
    zero = {"base_forgeries": 0, "base_honest": 0, "new_forgeries": 0, "new_honest": 0,
            "class_mismatches": 0, "new_echo": 0, "errors": 0, "base_mismatches": 0,
            "base_unwitnessed": 0, "new_unwitnessed": 0}
    good_res = {"counts": dict(zero), "n_accept": 0, "regress": "PASS", "all_new_match": True}
    bad_res = {"counts": dict(zero, base_mismatches=1), "n_accept": 0, "regress": "PASS",
               "all_new_match": True}
    check("claim verdict: one base mismatch fails the claim; none passes it",
          claim_upheld(good_res) is True and claim_upheld(bad_res) is False)
    # (9c) Y1: a separator alone (no traversal) fails the NAME rule, not the listing rule.
    sep, e_sep = verify_members(bdir, ["sub/M1"])
    check("member binding: a member name with a path separator is refused as not plain",
          sep is None and "plain" in e_sep, e_sep)
    # (9d) Y9: a leading-dot SHA256SUMS name without a separator is refused as non-plain.
    hdir = os.path.join(st, "battery-dotname")
    os.makedirs(hdir)
    with open(os.path.join(hdir, "M1.py"), "wb") as f:
        f.write(b"print('m1')\n")
    with open(os.path.join(hdir, "SHA256SUMS"), "w", encoding="utf-8") as f:
        f.write(f"{good}  M1.py\n{good}  .hidden.py\n")
    dot, e_dot = verify_members(hdir, ["M1"])
    check("member binding: a SHA256SUMS line naming a dot-file is refused as non-plain",
          dot is None and "non-plain" in e_dot, e_dot)
    # (9e) Z1: clean_env scrubs every name of its tuple from the ambient environment.
    scrub = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
             "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_REPLACE_REF_BASE", "GIT_CONFIG_COUNT",
             "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_SYSTEM",
             "GIT_NO_REPLACE_OBJECTS", "GIT_COMMON_DIR", "GIT_NAMESPACE", "GIT_CEILING_DIRECTORIES",
             "HOME", "XDG_CONFIG_HOME", "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0", "GIT_TRACE",
             "GIT_TRACE2_EVENT", "GIT_TEMPLATE_DIR", "GIT_ATTR_SOURCE", "GIT_EXEC_PATH",
             "GIT_DEFAULT_HASH")
    sentinel = "/nonexistent-r72-ambient-probe"
    saved_amb = {k: os.environ.get(k) for k in scrub}
    try:
        for k in scrub:
            os.environ[k] = sentinel
        amb = clean_env()
    finally:
        for k, v in saved_amb.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    kept_amb = sorted(k for k in scrub if amb.get(k) == sentinel)
    check("clean_env: every scrub-tuple name is removed from the ambient environment",
          kept_amb == [], f"kept={kept_amb}")

    # (10) r73 C2 forgery witness.
    wdir = os.path.join(st, "witness-r73")
    try:
        wrepo, wrev = build_repo_at(os.path.join(wdir, "repo"))
        clean0 = tree_divergence(wrepo, wrev)
        notes = os.path.join(wrepo, "tools", "notes.txt")
        os.chmod(notes, 0o755)
        d_mode = tree_divergence(wrepo, wrev)
        os.chmod(notes, 0o644)
        with open(os.path.join(wrepo, "tools", "extra.txt"), "wb") as f:
            f.write(UNTRACKED)
        d_untr = tree_divergence(wrepo, wrev)
        os.unlink(os.path.join(wrepo, "tools", "extra.txt"))
        os.unlink(os.path.join(wrepo, "README.md"))
        d_miss = tree_divergence(wrepo, wrev)
        with open(os.path.join(wrepo, "README.md"), "wb") as f:
            f.write(SEED_README)
        r10 = subprocess.run([sys.executable, "-c", INDEX_STAT_CODE, wrepo, "tools/counter.py",
                              _b(FORGED_SAMESIZE)], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=clean_env(), timeout=120)
        st10 = git_run(wrepo, ["status", "--porcelain"]).stdout
        d_stat = tree_divergence(wrepo, wrev)
        check("witness: a clean fixture has no divergence", clean0 == [], f"{clean0}")
        check("witness: an exec-bit flip is a mode divergence", d_mode == [("tools/notes.txt", "mode")], f"{d_mode}")
        check("witness: a new worktree file is an untracked divergence",
              d_untr == [("tools/extra.txt", "untracked")], f"{d_untr}")
        check("witness: a deleted tracked file is a missing divergence",
              d_miss == [("README.md", "missing")], f"{d_miss}")
        check("witness: a stat-concealed forgery (git status clean) is a bytes divergence",
              r10.returncode == 0 and st10 == b"" and d_stat == [("tools/counter.py", "bytes")],
              f"rc={r10.returncode} status={st10!r} {d_stat}")
    except (CaseError, OSError) as exc:
        check("witness: fixture set-up", False, f"{exc}")
    unw = {"counts": dict(zero, base_unwitnessed=1), "n_accept": 0, "regress": "PASS", "all_new_match": True}
    check("claim verdict: one unwitnessed base forgery fails the claim", claim_upheld(unw) is False)
    synth = {"row_fate": [fate("FWi", "refuse", "accept", witness=False)]}
    check("classifier: an accepted refuse row without a witness is error, not a forgery",
          classify_outcome(synth) == "error" and outcome_counts(synth)["forgeries"] == 0)
    synth = {"row_fate": [fate("FWi", "refuse", "accept", witness=True)]}
    check("classifier: an accepted refuse row with a witness is a forgery", classify_outcome(synth) == "forgery")

    # (11) r74 C2: row-specific witness and the r73 survivors (S73MutCounter M14, M15).
    xdir = os.path.join(st, "witness-r74")
    try:
        xrepo, _ = build_repo_at(os.path.join(xdir, "repo"))
        os.symlink("notes.txt", os.path.join(xrepo, "tools", "lnk"))
        r_add = git_run(xrepo, ["add", "--", "tools/lnk"])
        sub_oid = git_run(xrepo, ["rev-parse", "HEAD"]).stdout.decode().strip()
        r_gl = git_run(xrepo, ["update-index", "--add", "--cacheinfo", f"160000,{sub_oid},tools/sub"])
        r_ci = git_run(xrepo, ["commit", "-q", "-m", "r74 selftest: symlink + gitlink"])
        xrev = git_run(xrepo, ["rev-parse", "HEAD"]).stdout.decode().strip()
        if r_add.returncode or r_gl.returncode or r_ci.returncode or not xrev:
            raise CaseError(f"r74 witness fixture: add={r_add.returncode} gitlink={r_gl.returncode} "
                            f"commit={r_ci.returncode}")
        os.makedirs(os.path.join(xrepo, "tools", "sub"))
        x_clean = tree_divergence(xrepo, xrev)
        os.unlink(os.path.join(xrepo, "tools", "lnk"))
        os.symlink("counter.py", os.path.join(xrepo, "tools", "lnk"))
        x_tgt = tree_divergence(xrepo, xrev)
        check("witness: a gitlink whose directory is present is no divergence", x_clean == [], f"{x_clean}")
        check("witness: a retargeted tracked symlink is a target divergence",
              x_tgt == [("tools/lnk", "target")], f"{x_tgt}")
    except (CaseError, OSError) as exc:
        check("witness r74: fixture set-up", False, f"{exc}")
    setup_only = [(".gitattributes", "untracked")]
    check("row scope: a set-up-only divergence is not the row's (FWw, FC1, FC2)",
          all(row_scope(CASE_SPECS[k], setup_only) == [] for k in ("FWw", "FC1", "FC2")))
    check("row scope: a divergence on the row's forged path is kept",
          row_scope(CASE_SPECS["FC2"], [("tools/counter.py", "bytes")] + setup_only)
          == [("tools/counter.py", "bytes")])
    check("row scope: a failed read stays a failed read", row_scope(CASE_SPECS["FWw"], None) is None)
    check("row scope: a row with no declared forged path keeps nothing (fail closed)",
          row_scope({"name": "synthetic"}, [("tools/counter.py", "bytes")]) == [])
    acc = [r[0] for r in rows if r[1] == "refuse" and r[3] == "accept"]
    nofp = [k for k in acc if not forge_paths(CASE_SPECS[k])]
    check("forge paths: every base-accepted refuse row declares a forged path", acc and not nofp, f"{nofp}")
    unw2 = {"counts": dict(zero, new_unwitnessed=1), "n_accept": 0, "regress": "PASS", "all_new_match": True}
    check("claim verdict: one unwitnessed new-slot forgery fails the claim", claim_upheld(unw2) is False)

    npass = sum(1 for _, ok, _ in results if ok)
    for name, ok, detail in results:
        print(f"selftest {'ok' if ok else 'FAIL'}: {name}" + (f" | {detail}" if detail else ""))
    print(f"SELFTEST cases={len(results)} pass={npass} fail={len(results) - npass}")
    rc = 0 if npass == len(results) else 1
    print(f"EXIT={rc}")
    return rc


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        prog="c1-counter.py",
        description="round-67 C1 counter: value-checked caller-injected GIT_COMMON_DIR over the "
                    "carried r66 env-route, mode-bit, in-run and concealment matrix",
    )
    ap.add_argument("--root", required=True, help="lane root (read-only)")
    ap.add_argument("--matrix", required=True, help="c1-matrix.tsv path")
    ap.add_argument("--base-rev", required=True, help="full 40-hex lane base revision")
    ap.add_argument("--rev", help="full 40-hex revision of the candidate (with --tool)")
    ap.add_argument("--tool", help="candidate writer RELPATH inside the revision (with --rev)")
    ap.add_argument("--new-tool", help="candidate writer FILE (alternative to --rev/--tool)")
    ap.add_argument("--work", required=True, help="work directory (must exist; not /tmp, not TMPDIR, not in ROOT)")
    ap.add_argument("--receipt", help="write a control receipt (four header lines + run output) to FILE")
    ap.add_argument("--selftest", action="store_true", help="run the counter's own self-checks")
    ap.add_argument("--battery-manifest", help="battery TSV (mutant<TAB>expected_outcome); runs the "
                                                "matrix once per listed mutant and classifies outcomes")
    ap.add_argument("--battery-dir", help="directory holding <mutant>.py files named by the manifest")
    ap.add_argument("--only", help="comma-separated subset of manifest mutants to run (shard mode)")
    ns = ap.parse_args(argv)

    root = os.path.abspath(ns.root)
    work = os.path.abspath(ns.work)
    if not os.path.isdir(root):
        return fatal(f"root is not a directory: {root}")
    if not os.path.isdir(work):
        return fatal(f"work directory does not exist: {work}")
    rp = os.path.realpath(work)
    forbidden = ["/tmp", "/var/tmp"]
    tmpdir = os.environ.get("TMPDIR")
    if tmpdir:
        forbidden.append(os.path.realpath(tmpdir))
    for base in forbidden:
        if rp == base or rp.startswith(base + os.sep):
            return fatal(f"work directory must not live under {base}: {rp}")
    rr = os.path.realpath(root)
    if rp == rr or rp.startswith(rr + os.sep):
        return fatal(f"work directory must not live inside the lane root: {rp}")
    if not REV_RE.match(ns.base_rev):
        return fatal(f"--base-rev must be full 40-hex, got {ns.base_rev!r}")

    rows, err = load_matrix(os.path.abspath(ns.matrix))
    if rows is None:
        return fatal(f"matrix unusable: {err}")
    err = spec_agreement(rows, CASE_SPECS)
    if err:
        return fatal(f"matrix and CASE_SPECS disagree: {err}")

    if ns.selftest:
        return selftest(rows, root, ns.base_rev, work)

    if bool(ns.battery_manifest) != bool(ns.battery_dir):
        return fatal("--battery-manifest and --battery-dir are given together")
    if ns.rev and not REV_RE.match(ns.rev):
        return fatal("--rev must be full 40-hex when given")
    if (ns.tool is None) == (ns.new_tool is None) and not ns.battery_manifest:
        return fatal("give exactly one of --tool RELPATH (with --rev) or --new-tool FILE, "
                     "or a battery manifest")

    base_bytes, err = git_show(root, f"{ns.base_rev}:{BASE_REL}")
    if base_bytes is None:
        return fatal(f"base bytes unreadable: {err}")

    slots = os.path.join(work, "slots")
    shutil.rmtree(slots, ignore_errors=True)
    os.makedirs(slots)
    base_slot = os.path.join(slots, "base.py")
    base_sha = write_exec(base_slot, base_bytes)

    # regress fixture: read from the --base-rev blob (r68 M10 fix), never from a clone at HEAD.
    fixture, ferr = fixture_from_blob(root, ns.base_rev, work)
    if fixture is None:
        return fatal(f"regress fixture unavailable: {ferr}")
    fixture_cross = f"from {ns.base_rev}:{FIXTURE_REL} (blob)"
    rdir = os.path.join(work, "regress")
    os.makedirs(rdir, exist_ok=True)
    with open(os.path.abspath(ns.matrix), "rb") as f:
        matrix_sha = hashlib.sha256(f.read()).hexdigest()

    emit = Emitter()
    emit(f"# c1-counter root={root} base-rev={ns.base_rev} matrix-sha256={matrix_sha}")

    if ns.battery_manifest:
        manifest, err = load_battery_manifest(os.path.abspath(ns.battery_manifest))
        if manifest is None:
            return fatal(f"battery manifest unusable: {err}")
        selected = manifest
        if ns.only:
            want = [s.strip() for s in ns.only.split(",") if s.strip()]
            known = {n for n, _ in manifest}
            unknown = [w for w in want if w not in known]
            if unknown:
                return fatal(f"--only names unknown mutants: {unknown}")
            selected = [(n, e) for (n, e) in manifest if n in set(want)]
        battery_dir = os.path.abspath(ns.battery_dir)
        if not os.path.isdir(battery_dir):
            return fatal(f"battery dir does not exist: {battery_dir}")
        # Battery members are read-only inputs: run_slot executes each member in place and the
        # writer's receipt bytes land under --work; a committed battery under the lane root is fine.
        # r70 C2 (r69 routed F-3): every selected member must be listed in <battery-dir>/SHA256SUMS
        # and match it byte for byte BEFORE any member runs; each MUTANT line binds the member hash.
        member_sha, err = verify_members(battery_dir, [n for n, _ in selected])
        if member_sha is None:
            return fatal(f"battery members unverified: {err}")
        emit(f"# battery manifest={os.path.abspath(ns.battery_manifest)} "
             f"dir={battery_dir} selected={[n for n, _ in selected]} "
             f"sums_sha256={member_sha['__sums__']}")
        results: list[tuple[str, str, str]] = []
        for name, exp in selected:
            mpath = os.path.join(battery_dir, f"{name}.py")
            mwork = os.path.join(work, "battery", name)
            os.makedirs(mwork, exist_ok=True)
            res = evaluate(rows, base_slot, mpath, mwork, fixture)
            oc = outcome_counts(res)
            obs = classify_outcome(res)
            results.append((name, obs, exp))
            for line in res["lines"]:
                emit(line)
            emit(f"MUTANT {name} outcome={obs} expected={exp} "
                 f"forgeries={oc['forgeries']} echo={oc['echo']} honest={oc['honest']} "
                 f"label={oc['label']} errors={oc['errors']} regress={res['regress']} "
                 f"base_mismatches={res['counts']['base_mismatches']} "
                 f"sha256={member_sha[name]}")
        tally, all_match, rc = battery_verdict(results)
        emit(f"BATTERY mutants={len(selected)} kills={tally['forgery']} "
             f"label_only={tally['label-only']} over_refusal={tally['over-refusal']} "
             f"echo_violation={tally['echo-violation']} survived={tally['survived']} "
             f"error={tally['error']} all_match={str(all_match).lower()}")
        emit(f"EXIT={rc}")
        if ns.receipt:
            command = "python3 -B " + " ".join(
                shlex.quote(a) for a in [COUNTER_REL, *argv])
            measured = ns.rev if ns.rev else ns.base_rev
            sha = write_receipt(ns.receipt, measured, command, emit.lines)
            emit(f"# receipt={os.path.abspath(ns.receipt)} instrument_sha256={sha}")
        return rc

    if (ns.tool is None) == (ns.new_tool is None):
        return fatal("give exactly one of --tool RELPATH (with --rev) or --new-tool FILE")
    if ns.tool is not None:
        if not ns.rev or not REV_RE.match(ns.rev):
            return fatal("--tool needs --rev FULL40")
        rel = posixpath.normpath(ns.tool.replace(os.sep, "/"))
        new_bytes, err = git_show(root, f"{ns.rev}:{rel}")
        if new_bytes is None:
            return fatal(f"candidate bytes unreadable: {err}")
        new_src = f"{ns.rev}:{rel}"
    else:
        if not os.path.isfile(ns.new_tool):
            return fatal(f"--new-tool is not a readable file: {ns.new_tool}")
        with open(ns.new_tool, "rb") as f:
            new_bytes = f.read()
        new_src = f"file:{os.path.abspath(ns.new_tool)}"

    new_slot = os.path.join(slots, "new.py")
    new_sha = write_exec(new_slot, new_bytes)
    emit(f"# candidate new={new_src}")
    emit(f"# slot base={base_slot} sha256={base_sha} src={ns.base_rev}:{BASE_REL}")
    emit(f"# slot new={new_slot} sha256={new_sha} src={new_src}")
    emit(f"# matrix={os.path.abspath(ns.matrix)} sha256={matrix_sha}")
    emit(f"# regress fixture={fixture} {fixture_cross}")

    res = evaluate(rows, base_slot, new_slot, work, fixture)
    for line in res["lines"]:
        emit(line)
    emit(f"REGRESS base={res['regress_base']} new={res['regress_new']}")
    emit(summary_line(rows, res))
    rc = 0 if claim_upheld(res) else 1
    emit(f"EXIT={rc}")

    if ns.receipt:
        command = "python3 -B " + " ".join(
            shlex.quote(a) for a in [COUNTER_REL, *argv])
        # r67 receipt grammar (r66 spotcheck routed defect 5): the first line binds the revision the
        # run MEASURED — --rev in a candidate run, --base-rev in a do-nothing run — so the chronology
        # arm binds an After receipt as a strict descendant of the freeze.
        measured = ns.rev if ns.rev else ns.base_rev
        sha = write_receipt(ns.receipt, measured, command, emit.lines)
        emit(f"# receipt={os.path.abspath(ns.receipt)} instrument_sha256={sha}")
    return rc


def posixpath_abspath(p: str) -> str:
    """Best-effort argv rendering for the receipt command line; never fails."""
    try:
        return os.path.abspath(p)
    except Exception:
        return p


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
