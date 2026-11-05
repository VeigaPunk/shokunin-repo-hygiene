#!/usr/bin/env python3
"""c1-counter.py — souji round-68 C1 counter (L1-built, pre-freeze; probes in census/round-68/probes/).

Extends census/round-67/c1-counter.py (same slot/judge/regress/selftest machinery, its 31 rows carried
unchanged as regression rows) with the round-67 routed rows: the four PROPOSED kill-power fixtures for
the r66 survivor pins (S67MutKill/k67-decision.md, routed to "the successor counter"), the two M9
claim clauses the r67 frozen matrix did not measure (r67 lesson M9 / r67 verifier routed defect 2),
and the counter hermeticity fix (sentinel M1, r67 routed defect 5):

  * W4  env-common-dir-relative-poison  refuse  lane worktree is dirty (the critic W4 shape: relative
                                             GIT_COMMON_DIR=main/.git with the writer cwd at the parent,
                                             a poisoned main/main/.git copy whose config sets
                                             core.fileMode=false; the value check passes — the scrubbed
                                             resolution is the real common dir — and the SCRUB is the
                                             load-bearing protection: it keeps every writer git call on
                                             the real repository so the dirty check sees the tracked
                                             755->644 change. Measured r67 P-rel2 / critic §4; kills the
                                             M-CD-SCRUB mutant, the no-scrub clause of M9)
  * W5  env-common-dir-empty           refuse  RECEIPT-ENV-COMMONDIR-MISMATCH (empty caller value
                                             refused before any git call; the second M9 clause)
  * PK3  exclude-repo-local            refuse  lane worktree is dirty (a REPOSITORY-LOCAL
                                             core.excludesFile naming tools/hidden.txt; the writer's
                                             `-c core.excludesFile=<devnull>` pin closes the route the
                                             round-66 L1 named limit wrongly called open — r67 probe PK3;
                                             kills the K3 pin-drop mutant)
  * PK3h exclude-repo-local-honest     accept  '-' (same repo-local excludesFile, no concealed file)
  * PK4  global-filemode               refuse  lane worktree is dirty (a caller-named GIT_CONFIG_GLOBAL
                                             file whose core.fileMode=false hides a tracked 755->644
                                             change; not an excludes key, so no -c pin covers it — k67
                                             PK4; kills the K4 pin-drop mutant)
  * PK4h global-filemode-honest        accept  '-' (same global file, no mode change)
  * PK6  replace-ref-head              refuse  lane worktree is dirty (a repository refs/replace/<HEAD>
                                             ref whose replacement tree carries FORGED instrument bytes,
                                             index and worktree matching; the GIT_NO_REPLACE_OBJECTS=1
                                             pin makes the forgery visible as dirty — k67 PK6; kills the
                                             K6 pin-drop mutant)
  * PK6h replace-ref-head-honest       accept  '-' (no replace ref, real bytes)
  * PK7  system-filemode               refuse  lane worktree is dirty (a caller-named GIT_CONFIG_SYSTEM
                                             file whose core.fileMode=false hides a tracked 755->644
                                             change; GIT_CONFIG_NOSYSTEM=1 is the only defence — k67 PK7;
                                             kills the K7 pin-drop mutant)
  * PK7h system-filemode-honest        accept  '-' (same system file, no mode change)

Counter hermeticity (sentinel M1/M2, r67 routed defect 5): this counter's clean_env scrubs
GIT_COMMON_DIR, GIT_NAMESPACE and GIT_CEILING_DIRECTORIES from the ambient environment in addition to
the r67 list, so an operator shell that carries them cannot steer fixture builds or writer child
calls; the per-case caller values (W1-W5) are applied AFTER the scrub as case extras. The regress
fixture is read from the --base-rev blob (round-67 lesson M10: the r67 counter read it from a lane
clone at HEAD), so the regress arm cannot drift from the pinned bytes.

  * W1  env-common-dir-mismatch-hides-mode  refuse  RECEIPT-ENV-COMMONDIR-MISMATCH (GIT_COMMON_DIR points
                                            at a copy of .git whose config sets core.fileMode=false; the
                                            redirected config hides a tracked 755->644 change from the
                                            dirty check, so the base writer accepts a receipt over a
                                            hidden divergence — measured at the r67 base, see probes)
  * W2  env-common-dir-mismatch-clean      refuse  RECEIPT-ENV-COMMONDIR-MISMATCH (same redirect, clean
                                            tree: the caller-injected common-dir redirect is refused on
                                            value mismatch, hiding or no hiding)
  * W3  env-common-dir-match-honest        accept  '-' (GIT_COMMON_DIR set to the repository's own
                                            resolved common dir: a harmless, already-neutralized value is
                                            accepted — Q22 value/effect-aware treatment; the refusal
                                            introduces no honest-run trade)

  * E1  env-config-count-excludes        refuse  RECEIPT-ENV-CONFIG-SET (GIT_CONFIG_COUNT pair injects
                                                 core.excludesFile that hides an untracked file)
  * E2  env-config-parameters-excludes   refuse  RECEIPT-ENV-CONFIG-SET (GIT_CONFIG_PARAMETERS, same forge)
  * E3  env-config-global-excludes       refuse  lane worktree is dirty (GIT_CONFIG_GLOBAL names a crafted
                                                 global config; the writer repoints it to the null device
                                                 with GIT_CONFIG_NOSYSTEM=1, so the file shows up untracked)
  * E4  env-object-dir-redirect          refuse  RECEIPT-ENV-REDIRECT-SET (GIT_OBJECT_DIRECTORY repointed to
                                                 a full copy of the object store: the base writer honors the
                                                 redirect and accepts)
  * E5  env-alternates-redirect          refuse  RECEIPT-ENV-REDIRECT-SET (GIT_ALTERNATE_OBJECT_DIRECTORIES
                                                 set to an empty directory; base accepts)
  * E6  env-replace-ref-base             refuse  RECEIPT-ENV-REDIRECT-SET (GIT_REPLACE_REF_BASE names a forged
                                                 replace namespace; base accepts)
  * MOD2 allow-dirty-inrun-setuid-flip   refuse  RECEIPT-STATE-CHANGED-DURING-RUN (644 -> 4644, setuid; the
                                                 base snapshot masks the high bits with & 0o777 and accepts)
  * MOD3 allow-dirty-inrun-sticky-flip   refuse  RECEIPT-STATE-CHANGED-DURING-RUN (644 -> 1644, sticky; same)
  * SY3  allow-dirty-inrun-symlink-same-content-retarget  refuse  RECEIPT-STATE-CHANGED-DURING-RUN
                                                 (retarget to a byte-identical copy of the original target:
                                                 kills the read-through-symlink-hasher mutant class, r65 M11;
                                                 base and candidate both refuse on the target STRING)

The writer-side hardening these rows demand (round 66 C1): refuse GIT_CONFIG_COUNT / GIT_CONFIG_PARAMETERS /
GIT_CONFIG_KEY_* / GIT_CONFIG_VALUE_* presence (RECEIPT-ENV-CONFIG-SET), refuse GIT_OBJECT_DIRECTORY /
GIT_ALTERNATE_OBJECT_DIRECTORIES / GIT_REPLACE_REF_BASE presence (RECEIPT-ENV-REDIRECT-SET), repoint
GIT_CONFIG_GLOBAL to the null device and set GIT_CONFIG_NOSYSTEM=1 and GIT_NO_REPLACE_OBJECTS=1 on every
git call, pin `-c core.excludesFile=<null device>` on every git call, snapshot `st_mode & 0o7777` instead of
`& 0o777`, and name — never print — environment variable VALUES in the env refusals (the r65 sentinel F4
redaction). The env gate runs before any git call.

Named limits frozen with the r66 rows: `.git/info/exclude` and a tracked `.gitignore` still hide untracked
content from the writer's status reads on BOTH slots (the dirty check is a status check; ignored content is
outside it by design) — the config routes closed here are the caller-injected CONFIG and OBJECT-REDIRECT
environment routes only.

Judges the frozen round-67 C1 claim (operability): the receipt writer must, in addition to the
r60-r66 behaviour (env-route refusals E1-E6, full mode bits MOD2/MOD3, SY3, in-run snapshot, caller-env
refusal, :(top) index scope, untracked-visibility override, mode column, M5 symlink rule, P13),
value-check a caller-injected GIT_COMMON_DIR (W1-W3): refuse a mismatching or empty value with
RECEIPT-ENV-COMMONDIR-MISMATCH and accept the repository's own common-dir value.

The r66 rows (A..SY3, 28) are carried unchanged with their r66 fixture semantics.

The base writer at the round base (3639087917eaeb28719d7603110a6ec22782100e) is the ROUND-66 LANDED
CANDIDATE, measured by this round's own do-nothing control (`census/round-67/controls/c1-do-nothing.txt`):
  * the r66 hardened rows REFUSE on base with exactly their expected_class (the r66 candidate already
    refuses E1-E6 env routes with RECEIPT-ENV-CONFIG-SET / RECEIPT-ENV-REDIRECT-SET, records full mode
    bits so MOD2/MOD3 refuse, and carries the r60-r65 concealment machinery: C, D, T1-T3, T5, N1-N4,
    V1, MOD, SY2, P13, SY3);
  * the 2 base forgeries are exactly W1 and W2 (a caller-injected GIT_COMMON_DIR redirect is honored
    unconditionally: the redirected config hides a tracked mode change in W1 and the redirect is
    accepted in W2);
  * the 6 base honest rows are A, B, T4, V2, SY1, W3 (the equal-value common-dir run is honest on the
    base too — the candidate must keep accepting it).
  * Historical note (supersession, not a claim): the round-66 control
    (`census/round-66/controls/c1-do-nothing.txt`, base 045e1034 = the round-65 writer) measured 8
    forgeries there (E1-E6, MOD2, MOD3) and 5 honest; the round-66 landing moved those closures into
    the base this round measures. The round-66 docstring's stale sentence claiming T1/T2/T3/T5 are
    "accepted" on base was wrong for BOTH bases (M6; the r66 control shows them refusing there too).

Frozen matrix (c1-matrix.tsv, 31 rows; CASE_SPECS must cover exactly these rows, in this order):
  A..SY3 — the 28 r66 rows, unchanged definitions (see census/round-66/c1-counter.py docstring);
  then the three r67 rows W1-W3 as described at the top of this docstring.

Named limits frozen with the r67 matrix (not probed as rows): ignore routes (`.git/info/exclude`, a
tracked `.gitignore`, a repository-local `core.excludesFile` in the repository's own config) still hide
untracked content from the status reads on BOTH slots (L0 `souji | round-66` line 361 — repository-local
config-key scope — is unanswered; nothing here presumes an answer); a committed blob swapped for the
instrument between the pre-run read and the wrapped command is outside any in-run snapshot; the W-value
check reads the caller's environment once at writer start, so a value changed DURING the wrapped command
is outside it (start-of-run scope, consistent with the r62 index-flag check); a relative GIT_COMMON_DIR
value is canonicalized against the writer process's cwd, the same rule git applies; the comparison binds
the common-dir path, not the content behind it; N2's fixture seeds a NON-EMPTY untracked directory
(keep.txt), and the empty-dir variant was probed separately (census/round-65/probes/); N4's dual-seed
fixture shape is the frozen realizability probe resolution — a fixture WITHOUT the root-level dual copies
makes even the base writer fail at `cat-file` ("absent at"), which is the round-64 reviewer's H1 shape,
not this row; E4's objects-copy redirect is byte-identical to the repository's own store, so the base
accept demonstrates the honored redirect, not a content forgery — the writer refuses the redirect's
PRESENCE, which no env-set caller can argue around.

Per row, EACH slot runs against its own fresh fixture repo (a wrapped command mutates the repo, so
the base and new slots must not share state). Fixture rule: `git -C D init -q`, toplevel asserted
equal to D before the first commit, throwaway identity repo-local, fixed dates, one seed commit.

Fixture details fixed this round (probed 2026-11-05 against git 2.5x semantics):
  * seeds include a root-level `instr.sh` byte-identical to `tools/instr.sh` and a root-level
    `README.md`. N4 runs the writer with --root <repo>/tools; the writer then resolves the
    ls-tree pathspec cwd-relative but `cat-file rev:<path>` root-relative, so only byte-identical
    dual copies let a subdirectory-rooted run reach the wrapped command honestly. The N4 forge
    (skip-worktree on `README.md`, outside the subtree) is missed by the base writer because plain
    `git ls-files` is cwd-limited; `git status --porcelain` stays repo-wide, so the hidden forge is
    also porcelain-invisible. Neither extra seed carries a flag or divergence in any other row.
  * N3's flag-free index copy: `GIT_INDEX_FILE=<repo>/.git/alt-idx git update-index
    --no-skip-worktree <target>` alone FAILS (fatal: Unable to mark file — the override file is
    treated as an empty index), so the counter first copies `.git/index` to `.git/alt-idx` and then
    clears the flag in the copy; `git ls-files -v` through the copy must show only H tags. The
    writer runs with GIT_INDEX_FILE pointing at the copy and --allow-dirty; the base writer honors
    the env var (it scrubs only GIT_DIR/GIT_WORK_TREE) and accepts the forge.

Base slot  = tools/souji-receipt-write.py bytes at --base-rev (`git -C ROOT show`, read-only; the
             base slot bytes ALWAYS come from the revision, never from a file).
New slot   = `--tool RELPATH --rev FULL40` (bytes via `git -C ROOT show REV:RELPATH`), or
             `--new-tool FILE` (bytes of FILE). The do-nothing control passes the base bytes as FILE.
Accept = exit 0 and OUT present. Refuse = exit 2 and OUT absent. Any other outcome is `error`.
Refusal class = the row's expected_class substring present in the slot's stderr ('-' for accept rows).
Base and new slots write OUT under separate directories so a base accept cannot mask a new refuse.

Regress arm: tests/fixtures/r60-receipt-write.py located from a lane clone (`git clone --shared`
of --root into WORK/laneref, worktree checkout), cross-checked byte-for-byte against the blob at
--base-rev (a divergence is reported, not fatal), and run against BOTH slots; REGRESS=PASS iff both
exit 0 and the last output line contains `pass=8 fail=0`.

Selftest (--selftest, same CLI minus --tool/--new-tool/--rev): (1) CASE_SPECS vs matrix disagreement
is refused (in-process, with a synthetic CASE_SPECS, and via the CLI with a synthetic TSV); (2) three
stub writers — always-accept, always-refuse, refuse-without-token — are each REJECTED by evaluate().

Receipt emission (--receipt FILE, non-selftest): before the counter output, four column-0 header
lines binding the run: `rev=<measured rev>`, `instrument=census/round-67/c1-counter.py`,
`instrument_sha256=<sha256 of this counter file>`, `command=<the exact command line>`; then the
counter's own output verbatim, ending EXIT=<rc>. Mirrors the census/round-62 control-receipt
grammar consumed by tools/souji-freeze-check.py --substance. The r67 grammar fix (r66 spotcheck
routed defect 5): `<measured rev>` is `--rev` in a candidate run (`--tool ... --rev FULL40`) and
`--base-rev` in a do-nothing run (`--new-tool FILE`), so an After receipt binds a strict descendant
of the freeze where the round-66 c1-after receipt bound the base and tripped
RECEIPT-MEASURED-BEFORE-FREEZE.

Stdlib only. Writes only under --work and --receipt. --work must exist and must not be under
/tmp, /var/tmp, $TMPDIR, or inside --root. The lane is never written: read-only `git show` and the
--shared clone under WORK. TMPDIR is never used for scratch.

Usage:
  python3 -B c1-counter.py --root LANE --matrix c1-matrix.tsv --base-rev FULL40 \
      (--rev FULL40 --tool RELPATH | --new-tool FILE) --work DIR [--receipt FILE]
  python3 -B c1-counter.py --selftest --root LANE --matrix c1-matrix.tsv --base-rev FULL40 --work DIR

Exit: 0 = claim upheld per SUMMARY (selftest: all checks passed); 1 = claim fails (selftest: a check
failed); 2 = could not evaluate (bad args, unreadable matrix/bytes, spec disagreement, bad work dir).
"""
from __future__ import annotations

import argparse
import hashlib
import os
import posixpath
import re
import shutil
import shlex
import subprocess
import sys
from typing import Optional

BASE_REL = "tools/souji-receipt-write.py"
FIXTURE_REL = "tests/fixtures/r60-receipt-write.py"
FIXTURE_LAST_WANT = "pass=8 fail=0"
COUNTER_REL = "census/round-68/c1-counter.py"

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
              "W4", "W5", "W6", "PK3", "PK3h", "PK4", "PK4h", "PK6", "PK6h", "PK7", "PK7h"]

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
           "forged": FORGED_NOTES, "altidx": True, "allow_dirty": True, "use_env_index": True},
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
            "env_index_missing": True},
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
           "mode_change": True},
    "W2": {"name": "env-common-dir-mismatch-clean", "env_kind": "common-dir-copy"},
    "W3": {"name": "env-common-dir-match-honest", "env_kind": "common-dir-real"},
    # r68 rows: the r67 routed items. W4/W5 measure the two M9 claim clauses; PK* freeze the four
    # r67-proposed kill-power fixtures (each flips exactly its pin-drop mutant; see mutate-writer.py).
    "W4":  {"name": "env-common-dir-relative-poison", "env_kind": "common-dir-rel-poison",
            "repo_name": "main", "cwd_parent": True, "mode_change": True},
    "W5":  {"name": "env-common-dir-empty", "env_kind": "common-dir-empty", "cwd_gitdir": True},
    "W6":  {"name": "env-common-dir-symlink-alias-honest", "env_kind": "common-dir-alias", "honest": True},
    "PK3":  {"name": "exclude-repo-local", "env_kind": "exclude-repo-local"},
    "PK3h": {"name": "exclude-repo-local-honest", "env_kind": "exclude-repo-local", "honest": True},
    "PK4":  {"name": "global-filemode", "env_kind": "global-filemode"},
    "PK4h": {"name": "global-filemode-honest", "env_kind": "global-filemode", "honest": True},
    "PK6":  {"name": "replace-ref-head", "env_kind": "replace-ref-head"},
    "PK6h": {"name": "replace-ref-head-honest", "env_kind": "replace-ref-head", "honest": True},
    "PK7":  {"name": "system-filemode", "env_kind": "system-filemode"},
    "PK7h": {"name": "system-filemode-honest", "env_kind": "system-filemode", "honest": True},
}

# Inline helpers executed as the wrapped command (argv form; no shell quoting involved).
EDIT_CODE = ("import sys\n"
             "open(sys.argv[1], sys.argv[2]).write(sys.argv[3].encode('latin-1'))\n")
RESTORE_CODE = ("import sys\n"
                "p = sys.argv[1]\n"
                "open(p, 'ab').write(sys.argv[2].encode('latin-1'))\n"
                "open(p, 'wb').write(sys.argv[3].encode('latin-1'))\n")


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
    raise CaseError(f"unknown in-run kind {kind!r}")


def wrapped_argv(spec: dict, repo: str) -> list[str]:
    if "inrun" in spec:
        return inrun_argv(spec["inrun"], repo)
    return list(ECHO_ARGV)


def clean_env(extra: Optional[dict] = None) -> dict:
    e = {k: v for k, v in os.environ.items()
         if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE",
                      "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
                      "GIT_REPLACE_REF_BASE", "GIT_CONFIG_COUNT", "GIT_CONFIG_PARAMETERS",
                      "GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_SYSTEM",
                      "GIT_NO_REPLACE_OBJECTS", "GIT_COMMON_DIR", "GIT_NAMESPACE",
                      "GIT_CEILING_DIRECTORIES")
         and not k.startswith("GIT_CONFIG_KEY_") and not k.startswith("GIT_CONFIG_VALUE_")}
    e["GIT_OPTIONAL_LOCKS"] = "0"
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
             "notes-copy.txt": SEED_NOTES}
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
            # W4 (critic shape, P-rel2): the fixture repo is <case>/main; a poisoned copy of .git at
            # <case>/main/main/.git (core.fileMode=false) hidden from status via info/exclude; the
            # tracked 755->644 mode change was applied by the early mode_change branch (tools/instr.sh).
            # case_env carries the relative caller value; the writer runs with cwd = <case> (cwd_parent).
            excl = os.path.join(repo, ".git", "info", "exclude")
            with open(excl, "a", encoding="utf-8") as f:
                f.write("main/\n")
            dst = os.path.join(repo, "main")
            shutil.copytree(os.path.join(repo, ".git"), dst, symlinks=True)
            with open(os.path.join(dst, "config"), "a", encoding="utf-8") as f:
                f.write("[core]\n\tfileMode = false\n")
        elif kind != "replace-base":
            raise CaseError(f"unknown env_kind {kind!r}")


def build_case(work: str, letter: str, which: str, spec: dict) -> tuple[str, str]:
    """Per (row, slot) fixture: work/<letter>/<which>/{repo,out}. Returns (repo, rev)."""
    case_dir = os.path.join(work, letter, which)
    repo_name = spec.get("repo_name", "repo")
    repo, rev = build_repo_at(os.path.join(case_dir, repo_name))
    mutate(repo, spec)
    os.makedirs(os.path.join(case_dir, "out"), exist_ok=True)
    return repo, rev


def case_env(spec: dict, repo: str) -> Optional[dict]:
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
        # PK7: the caller names the system config file whose core.fileMode=false hides the mode change.
        return {"GIT_CONFIG_SYSTEM": os.path.join(os.path.dirname(repo), "system-mode.gitconfig")}
    if kind == "replace-ref-head":
        # PK6: repository-state route (refs/replace); no caller env.
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


def one_line(text: str, limit: int = 160) -> str:
    s = " ".join((text or "").split())
    return (s[: limit - 3] + "...") if len(s) > limit else s


def load_matrix(path: str) -> tuple[Optional[list[tuple[str, str, str]]], str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except OSError as exc:
        return None, f"cannot read matrix: {exc}"
    lines = [l for l in raw.splitlines() if l.strip()]
    if not lines:
        return None, "matrix is empty"
    if lines[0].split("\t") != ["case", "expect", "expected_class"]:
        return None, f"bad header: {lines[0]!r}"
    rows: list[tuple[str, str, str]] = []
    for i, line in enumerate(lines[1:], 2):
        parts = line.split("\t")
        if len(parts) != 3:
            return None, f"line {i}: expected 3 tab-separated fields, got {len(parts)}"
        case, expect, klass = parts
        if expect not in ("accept", "refuse"):
            return None, f"line {i}: expect must be accept|refuse, got {expect!r}"
        if expect == "refuse" and not klass:
            return None, f"line {i}: refuse row needs a non-empty expected_class"
        if expect == "accept" and klass != "-":
            return None, f"line {i}: accept row must use '-' as expected_class"
        rows.append((case, expect, klass))
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
    """Run every frozen row against both slots. Returns counts, detail lines and the regress verdict."""
    lines: list[str] = []
    c = {"base_forgeries": 0, "base_honest": 0, "new_forgeries": 0, "new_honest": 0, "class_mismatches": 0}
    all_new_match = True
    for letter, expect, klass in rows:
        spec = CASE_SPECS[letter]
        try:
            b_repo, b_rev = build_case(work, letter, "base", spec)
            n_repo, n_rev = build_case(work, letter, "new", spec)
        except CaseError as exc:
            lines.append(f"CASE {letter} expect={expect} base=error base_findings=- new=error new_findings=-")
            lines.append(f"# detail {letter} name={spec['name']} build_failed: {exc}")
            all_new_match = False
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
        b_rc, _, b_se = run_slot(base_slot, b_repo, b_rev, b_out, allow_dirty,
                                 wrapped_argv(spec, b_repo), root=root_b, instrument=instrument,
                                 env_extra=case_env(spec, b_repo), cwd=cwd)
        n_rc, _, n_se = run_slot(new_slot, n_repo, n_rev, n_out, allow_dirty,
                                 wrapped_argv(spec, n_repo), root=root_n, instrument=instrument,
                                 env_extra=case_env(spec, n_repo), cwd=cwd_n)
        b_v, n_v = judge(b_rc, b_out), judge(n_rc, n_out)
        b_f, n_f = findings_for(b_v, b_se, klass), findings_for(n_v, n_se, klass)
        lines.append(f"CASE {letter} expect={expect} base={b_v} base_findings={b_f} "
                     f"new={n_v} new_findings={n_f}")
        lines.append(f"# detail {letter} name={spec['name']} rev={n_rev[:12]} "
                     f"base_rc={b_rc} new_rc={n_rc} base_stderr={one_line(b_se)} "
                     f"new_stderr={one_line(n_se)}")
        if expect == "refuse":
            if b_v == "accept":
                c["base_forgeries"] += 1
            if n_v == "accept":
                c["new_forgeries"] += 1
            if not (n_v == "refuse" and klass and klass in n_se):
                c["class_mismatches"] += 1
        else:
            if b_v == "accept":
                c["base_honest"] += 1
            if n_v == "accept":
                c["new_honest"] += 1
        if n_v != expect:
            all_new_match = False

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
            "regress_base": regress_base, "regress_new": regress_new,
            "n_accept": sum(1 for r in rows if r[1] == "accept"),
            "n_refuse": sum(1 for r in rows if r[1] == "refuse")}


def claim_upheld(res: dict) -> bool:
    c = res["counts"]
    return (c["new_forgeries"] == 0 and c["new_honest"] == res["n_accept"]
            and c["class_mismatches"] == 0 and res["regress"] == "PASS" and res["all_new_match"])


def summary_line(rows, res: dict) -> str:
    c = res["counts"]
    return (f"SUMMARY matrix={len(rows)} base_forgeries={c['base_forgeries']} "
            f"base_honest={c['base_honest']} new_forgeries={c['new_forgeries']} "
            f"new_honest={c['new_honest']} class_mismatches={c['class_mismatches']} "
            f"regress={res['regress']}")


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
        f.write("case\texpect\texpected_class\n")
        for letter, expect, klass in rows:
            if letter != "T5":
                f.write(f"{letter}\t{expect}\t{klass}\n")
    bad_extra = os.path.join(st, "bad-extra-T6.tsv")
    with open(bad_extra, "w", encoding="utf-8") as f:
        f.write("case\texpect\texpected_class\n")
        for letter, expect, klass in rows:
            f.write(f"{letter}\t{expect}\t{klass}\n")
        f.write("T6\trefuse\tRECEIPT-STATE-CHANGED-DURING-RUN\n")
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

    base_bytes, err = git_show(root, f"{ns.base_rev}:{BASE_REL}")
    if base_bytes is None:
        return fatal(f"base bytes unreadable: {err}")

    slots = os.path.join(work, "slots")
    shutil.rmtree(slots, ignore_errors=True)
    os.makedirs(slots)
    base_slot = os.path.join(slots, "base.py")
    new_slot = os.path.join(slots, "new.py")
    base_sha = write_exec(base_slot, base_bytes)
    new_sha = write_exec(new_slot, new_bytes)

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
    emit(f"# c1-counter root={root} base-rev={ns.base_rev} new={new_src}")
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
