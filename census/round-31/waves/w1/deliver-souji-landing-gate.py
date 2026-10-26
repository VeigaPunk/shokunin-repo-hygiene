#!/usr/bin/env python3
"""souji-landing-gate.py — round-18 landing-claim consistency gate.

Mechanically re-derives the three round-15 landing defects the non-author
closure found by hand (corpus/lessons/round-15-verifier-spotcheck.md):

  1. A registry-cited script that does not parse landed as "unverified
     candidate" (tools/souji-census.sh at b410186: bash -n rc 2).
  2. Frozen pins matching no committed bytes
     (tests/fixtures/r15-preservation-frozen/expected.json pinned
     tools/souji-census.sh = b5187351…, which no revision has).
  3. A seat-reported known failure not carried into the round lesson
     (.ufo/waves/round-15/w1/ConfigRepair.md STATUS/failure lines vs
     corpus/lessons/round-15.md).

Scope: landing-claim consistency, failure-channel carry, and cited-path
integrity. It is NOT a disclosure-enforcement or behavioral-regression
suite; it never executes repository code (only `bash -n FILE` and Python
compile()).

Byte provenance: committed bytes are read with `git -C LANE ls-tree -r -z
--full-tree REV` and `git cat-file blob <oid>` (never `git archive`, whose
export-ignore/export-subst/attributes can alter bytes). Files that need a
real path for `bash -n` are written under a private
tempfile.mkdtemp(dir='/var/tmp') snapshot removed in `finally`.

CLI:
  python3 tools/souji-landing-gate.py --root LANE --rev REV --round N
      [--base REV] [--fleet-root PATH] [--json OUT]
  python3 tools/souji-landing-gate.py --selftest

Exit: 0 no findings, 1 findings, 2 could-not-evaluate (usage, unknown rev,
no SKILL.md, no .md reports in .ufo/waves/round-N/ or at its committed
capture census/round-N/waves/, git failure, malformed expected.json or
pointer-exemptions.tsv shape).

Output: one TSV line per finding `ID\tpath\tdetail` (sorted), then
`SUMMARY\tfindings=K\tchecked_reg=A\tchecked_changed=G\tchecked_pins=B\tchecked_measured=M\tchecked_markers=C\tstatus_lines=S\tcarry_heading=H\tchecked_reports=D`.
For round 18 and later, `--json` also carries a `fleet` list for citation
paths found only under optional `--fleet-root`; those are not findings.
The JSON summary adds `checked_ptrs` (expanded citation candidates),
`ptr_exempt` (unique used rows for citations or exact-placeholder records),
and `ptr_fleet` (fleet-only citation occurrences).

Per-branch execution counts (r17): `checked_reg` counts registry-cited
script parses at REV, `checked_changed` counts scripts added/modified in
BASE..REV (0 unless --base is given), `checked_pins` counts frozen-pin
comparisons at REV, `checked_measured` counts the comparisons against
`record.measured_commit` (0 means the measured branch never ran, so the
measured class is unevaluated in that replay), `status_lines` counts report
lines opening a STATUS channel (fenced/table lines included, so 0 means the
failure channel had nothing to look at), `carry_heading` is 1 iff the lesson
carries the `## Seat-reported failures` heading, and `checked_reports` is the
number of distinct relative `.md` report paths in the union of
`.ufo/waves/round-N/` and its committed capture `census/round-N/waves/`
(r31: the base gate read one tree alone, hiding capture-only reports). A zero
on any of these means the axis was not exercised — never that it passed.

Environment: every git call runs under GIT_ENV — repository-selecting
ambient variables (GIT_DIR, GIT_WORK_TREE, GIT_INDEX_FILE,
GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_COMMON_DIR)
are removed and GIT_NO_LAZY_FETCH/GIT_NO_REPLACE_OBJECTS are set, so
`--root` alone selects the repository and committed bytes are exact.

Finding ids (pinned): LG-PARSE-REG, LG-MISSING-REG, LG-PARSE-CHANGED,
LG-FROZEN-PIN, LG-FROZEN-MEASURED, LG-SEAT-UNCARRIED, LG-OPEN-ADMITTED,
LG-DANGLING-PTR and LG-DANGLING-PTR-EXEMPT-STALE (round 18+).
"""

import argparse
import hashlib
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata

# ---------------------------------------------------------------------------
# Pinned constants
# ---------------------------------------------------------------------------

# SKILL.md registry citation shape: one path segment deep under tools/,
# tests/fixtures/ or census/round-<n>/.
CITED_PATH_RE = re.compile(
    r"(?:tools|tests/fixtures|census/round-\d+)/[A-Za-z0-9_.-]+\.(?:sh|py)"
)

# A seat report's failure channel (L1 revisions, round 16): a line whose
# stripped text starts with a STATUS prefix (optional heading/bold
# decoration), outside fenced blocks and table rows, whose first value word
# is in the pinned failure vocabulary the wave contract requires seats to use
# for a known failure. Two earlier drafts were measured and dropped: "any
# non-benign first word" plus generic markers (`snapshot_tampered`, `syntax
# error`) flagged 10 benign lines on each admitted round-13/14 replay, and
# free-text phrase markers (`does not parse`, `do not ship`) matched 42 lines
# at the round-16 landing, all quotations of the round-15 failure.
STATUS_PREFIX_RE = re.compile(r"^[#*\s]*STATUS[*]*\s*[:—]\s*(.*)$", re.IGNORECASE)
FAILURE_STATUS_WORDS = frozenset(
    {
        "incomplete", "fail", "failed", "fails", "failing", "failure",
        "blocked", "broken", "partial", "harmed", "red", "unrun", "error",
        "regression", "known",
    }
)

# Carry target in corpus/lessons/round-N.md.
FAILURES_HEADING_RE = re.compile(r"^##\s+Seat-reported failures\b", re.IGNORECASE)
HEADING_RE = re.compile(r"^#{1,6}\s")
CARRY_TOKEN_RE = re.compile(r"(?i)\bopen\b|resolved@[0-9a-f]{7,}")
ADMITTED_TRUE_RE = re.compile(r"(?i)admitted\s*:\s*true\b")

# Carry-wrap rule (r19 C1; rule drafted at
# .ufo/waves/round-18/w1/ScoutCarryWrap.md). A STATUS paragraph is the
# marker line plus its wrapped continuation lines. A carry entry either
# quotes the normalized whole paragraph or a normalized prefix that stops at
# one of the SOURCE's physical-line ends and is followed by an ellipsis; a
# mid-line ellipsis is never a verifiable cut point. The strict branch is
# gated at round 18 so the five pinned historical replays keep their
# expected verdicts; before that gate the old first-physical-line match
# stays in force (and stays blind to wrapped cuts, disclosed).
WRAP_STRICT_FROM_ROUND = 18
ELLIPSIS_RE = re.compile(r"\s*[\"\u201d]?\s*(?:\u2026|\.\.\.)")
LIST_ITEM_RE = re.compile(r"^([-*+]|\d+\.)\s+")
THEMATIC_RE = re.compile(r"^([-*_])(?:\s*\1){2,}$")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

# Frozen-pin path rule (pinned): an expected.json `files`/`record` key that
# starts with one of these top-level prefixes resolves at the snapshot root;
# any other key resolves inside the frozen dir. No fallback either way.
ROOT_PREFIXES = ("tools/", "tests/", "census/", "corpus/")

EXPECTED_JSON_RE = re.compile(r"tests/fixtures/[^/]+-frozen/expected\.json$")
SCRIPT_EXT_RE = re.compile(r"\.(?:sh|py)$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
POINTER_ROOTS = (
    "census/", "tests/", "tools/", "corpus/", ".ufo/waves/",
    ".ufo/quarantine/",
)
POINTER_EXEMPTIONS_PATH = "corpus/pointer-exemptions.tsv"
POINTER_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_./<>*])"
    r"(?:(?:\.\./)+|\./)?"
    r"(?:census|tests|tools|corpus|\.ufo/waves|\.ufo/quarantine)/"
    r"""[^\s`"'()\[\]]+"""
)
ROUND_RANGE_RE = re.compile(r"round-\{?(\d+)\.\.(\d+)\}?", re.IGNORECASE)
ROUND_PLACEHOLDER_RE = re.compile(r"round-N", re.IGNORECASE)
# r30 C2. tools/souji-wave-evidence-capture.sh copies the gitignored
# .ufo/waves/round-N/ tree to census/round-N/waves/, so a wave pointer is
# resolved through that committed capture as well. A token that carries a
# template placeholder, or that ends in `round-` because the tokenizer cut at
# one (`"census/round-"+rd+...`), names no path and is not a pointer.
CAPTURE_POINTER_RE = re.compile(r"^\.ufo/waves/(round-\d+)(/.*)?$")
# r31 C2: printf conversions (%d, %0Nd, %02d, %.3f ...) are template tokens
# too, not paths.
TEMPLATE_POINTER_RE = re.compile(
    r"%[-+ #0]*\d*(?:\.\d+)?[diouxXeEfFgGaAcsp%]|<[Nn]>|\{N\}"
)
# r31 C2: the capture stores a component named `.git` as `.git.captured` and a
# file named `.gitignore`/`.gitattributes` as `<name>.captured`
# (tools/souji-wave-evidence-capture.sh store_name), so a pointer at such a
# name resolves through its stored name.
CAPTURE_STORED_GIT = ".git"
CAPTURE_RENAME_NAMES = (".gitignore", ".gitattributes")
# r31 C2: a token whose components are all letters names prose, not a path
# (`corpus/authority`, `tools/kill/killpg`); a trailing `/` or any `.`, `-`,
# `_` or digit makes it a path again.
LETTERS_ONLY_RE = re.compile(r"[A-Za-z]+")
# The only measured-commit exemption is bound to the known synthetic r14 value.
MEASURED_COMMIT_PLACEHOLDER = "0123456789abcdef0123456789abcdef01234567"

FINDING_IDS = (
    "LG-PARSE-REG",
    "LG-MISSING-REG",
    "LG-PARSE-CHANGED",
    "LG-FROZEN-PIN",
    "LG-FROZEN-MEASURED",
    "LG-SEAT-UNCARRIED",
    "LG-OPEN-ADMITTED",
    "LG-DANGLING-PTR",
    "LG-DANGLING-PTR-EXEMPT-STALE",
)




# Repository-selecting ambient variables are stripped so --root alone
# selects the repository (r17 S3); NO_LAZY_FETCH keeps a partial clone
# from touching the network and NO_REPLACE_OBJECTS keeps `cat-file`
# bytes equal to committed bytes.
GIT_ENV = {
    k: v
    for k, v in os.environ.items()
    if k
    not in (
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_COMMON_DIR",
    )
}
GIT_ENV["GIT_NO_LAZY_FETCH"] = "1"
GIT_ENV["GIT_NO_REPLACE_OBJECTS"] = "1"


class EvalError(Exception):
    """Could-not-evaluate (exit 2)."""

# ---------------------------------------------------------------------------
# Git plumbing (read-only blob access; never `git archive`)
# ---------------------------------------------------------------------------


def _git(root, args, binary=True):
    """Run one git command in `root`; return stdout. Raise EvalError on failure."""
    proc = subprocess.run(
        ["git", "-C", root] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=GIT_ENV,
    )
    if proc.returncode != 0:
        raise EvalError(
            "git %s failed (rc=%d): %s"
            % (" ".join(args[:2]), proc.returncode, proc.stderr.decode("utf-8", "replace").strip()[:300])
        )
    return proc.stdout if binary else proc.stdout.decode("utf-8", "replace")


def list_tree(root, rev):
    """Return dict path -> blob oid for every blob at REV."""
    raw = _git(root, ["ls-tree", "-r", "-z", "--full-tree", rev])
    out = {}
    for rec in raw.split(b"\0"):
        if not rec:
            continue
        meta, _, name = rec.partition(b"\t")
        parts = meta.split(b" ")
        if len(parts) < 3 or parts[1] != b"blob":
            continue
        out[name.decode("utf-8", "surrogateescape")] = parts[2].decode("ascii")
    return out


def blob_by_oid(root, oid):
    return _git(root, ["cat-file", "blob", oid])


def blob_at_path(root, rev, path):
    """Blob bytes at REV:path, or None if absent. Any git failure that is
    not "path absent" is EvalError (exit 2), never a finding (r17 S1):
    `rev-parse --verify --quiet` exits 1 for an unresolvable pathspec and
    a larger code for a real repository error."""
    spec = "%s:%s" % (rev, path)
    proc = subprocess.run(
        ["git", "-C", root, "rev-parse", "--verify", "--quiet", spec],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=GIT_ENV,
    )
    if proc.returncode == 1:
        return None
    if proc.returncode != 0:
        raise EvalError(
            "git rev-parse %s failed (rc=%d): %s"
            % (spec, proc.returncode, proc.stderr.decode("utf-8", "replace").strip()[:300])
        )
    return blob_by_oid(root, proc.stdout.decode("ascii").strip())


def resolve_commit(root, rev):
    try:
        out = _git(root, ["rev-parse", "--verify", "--quiet", rev + "^{commit}"], binary=False)
    except EvalError as exc:
        raise EvalError("cannot resolve revision %r: %s" % (rev, exc))
    resolved = out.strip()
    if not resolved:
        raise EvalError("unknown revision %r" % rev)
    return resolved


def sha256(data):
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Parse checks (never execute target code)
# ---------------------------------------------------------------------------


def _safe_relpath(path):
    """True iff path is a safe repository-relative path (no absolute/dotdot)."""
    if path.startswith("/") or not path:
        return False
    norm = os.path.normpath(path)
    if norm.startswith("..") or os.path.isabs(norm):
        return False
    return True


def check_bash(path, content, snapdir):
    """Write content under snapdir mirroring `path`, run `bash -n`.
    Return a detail string on failure (rc!=0 or ANY stderr), else None."""
    if not _safe_relpath(path):
        return "unsafe path %r" % path
    dest = os.path.join(snapdir, path)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as fh:
        fh.write(content)
    proc = subprocess.run(
        ["bash", "-n", dest], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    err = proc.stderr.decode("utf-8", "replace").strip()
    if proc.returncode != 0:
        first = err.splitlines()[0] if err else "no stderr"
        return "bash -n rc=%d: %s" % (proc.returncode, first)
    if err:
        return "bash -n rc=0 but stderr: %s" % err.splitlines()[0]
    return None


def check_python(path, content):
    """compile() only — never executes. Return detail on failure, else None."""
    try:
        compile(content, path, "exec")
    except (SyntaxError, ValueError) as exc:
        return "%s: %s" % (type(exc).__name__, str(exc).splitlines()[0][:200])
    except Exception as exc:  # e.g. TypeError on undecodable bytes
        return "%s: %s" % (type(exc).__name__, exc)
    return None


def parse_script(root, tree, path, snapdir):
    """Parse one script path from the already-enumerated REV tree. Return
    detail on failure, else None. Reads by oid, so a read failure is
    EvalError, never a finding."""
    content = blob_by_oid(root, tree[path])
    if path.endswith(".sh"):
        return check_bash(path, content, snapdir)
    return check_python(path, content)


# ---------------------------------------------------------------------------
# Seat failure channel (LG-SEAT-UNCARRIED / LG-OPEN-ADMITTED)
# ---------------------------------------------------------------------------


def norm_line(text):
    """Normalization order (pinned): NFC, drop `*` and backticks, collapse
    whitespace to one space, strip."""
    text = unicodedata.normalize("NFC", text)
    text = text.replace("*", "").replace("`", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def status_value(line):
    """If `line` opens a STATUS channel, return its value text, else None."""
    stripped = line.strip()
    m = STATUS_PREFIX_RE.match(stripped)
    if not m:
        return None
    return m.group(1)


def is_failure_line(line, in_fence, in_table):
    """Failure-channel membership (L1 revision 2, round 16): only a STATUS
    line outside fenced blocks and table rows whose first value word is in
    the contract failure vocabulary. Free-text phrase markers are not used:
    at the round-16 landing they matched 42 lines, every one a quotation of
    the round-15 failure, none an undisclosed round-16 failure."""
    if in_fence or in_table:
        return False
    value = status_value(line)
    if value is None:
        return False
    first = re.match(r"[*:—\s]*(\S+)", value)
    word = first.group(1).strip("*:—").lower() if first else ""
    return word in FAILURE_STATUS_WORDS


def seat_failure_lines(report_text):
    """Yield (lineno, raw_line) failure-channel lines of one report."""
    out = []
    in_fence = False
    for lineno, line in enumerate(report_text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if is_failure_line(line, in_fence, stripped.startswith("|")):
            out.append((lineno, line))
    return out


def lesson_lines(lesson_text):
    """Lesson text minus HTML comments, as raw lines."""
    return HTML_COMMENT_RE.sub("", lesson_text).splitlines()


def failures_section_lines(lesson_text):
    """Raw lines under EVERY `## Seat-reported failures` section, each until
    the next heading.

    r31 C2: the base gate stopped at the first heading after the first such
    section, so an append-only carry section (a second one at the end of the
    lesson) was invisible and its failures read as uncarried. A blank
    separator is kept at each section end so the entry joiner cannot merge a
    bullet of one section into the previous section's entry."""
    inside = False
    out = []
    for line in lesson_lines(lesson_text):
        stripped = line.strip()
        if FAILURES_HEADING_RE.match(stripped):
            inside = True
            continue
        if inside and HEADING_RE.match(stripped):
            inside = False
            out.append("")
            continue
        if inside:
            out.append(line)
    return out


def status_line_count(report_text):
    """Number of report lines carrying a STATUS channel prefix — inside or
    outside fences/tables, failure-vocabulary or not. Reported so a round
    whose carry axis was never exercised is visible in SUMMARY."""
    return sum(
        1 for line in report_text.splitlines() if status_value(line) is not None
    )


def _continues_paragraph(line):
    """A wrapped STATUS paragraph continues through prose only: not a fence,
    table row, quote, HTML block, heading, new bullet, thematic break, or a
    new STATUS line."""
    s = line.strip()
    return bool(s) and not (
        s.startswith(("```", "|", ">", "<"))
        or HEADING_RE.match(s)
        or LIST_ITEM_RE.match(s)
        or THEMATIC_RE.match(s)
        or status_value(line) is not None
    )


def status_paragraph(lines, idx):
    """Marker physical line plus its wrapped continuation lines."""
    block = [lines[idx]]
    j = idx + 1
    while j < len(lines) and _continues_paragraph(lines[j]):
        block.append(lines[j])
        j += 1
    return block


def carry_entries(carry_lines):
    """Join a carry bullet's own wrapped continuation lines into one entry.

    Symmetric with status_paragraph and closes the false-fail direction: a
    correct quote whose lesson bullet wraps must still match.
    """
    ents = []
    for line in carry_lines:
        if ents and _continues_paragraph(line):
            ents[-1] += " " + line
        else:
            ents.append(line)
    return [norm_line(e) for e in ents]


def carries(block, entry):
    """True iff `entry` carries the marker paragraph `block`.

    (a) the normalized whole paragraph occurs; or
    (b) the normalized first k physical lines (1 <= k < len(block)) occur and
        the very next non-space characters are an ellipsis (an optional
        closing quote may sit between). A mid-line ellipsis never carries.
    """
    full = norm_line(" ".join(block))
    if full and full in entry:
        return True
    for k in range(1, len(block)):
        prefix = norm_line(" ".join(block[:k]))
        if not prefix:
            continue
        for m in re.finditer(re.escape(prefix), entry):
            if ELLIPSIS_RE.match(entry, m.end()):
                return True
    return False


def _report_paths(tree, round_no):
    """Committed seat reports of one round: the union of `.ufo/waves/round-N/`
    and its committed capture `census/round-N/waves/`, one entry per distinct
    relative suffix.

    r31 C2: the wave dir is gitignored, so a revision may carry a subset of it
    as the capture (tools/souji-wave-evidence-capture.sh) and a subset
    force-added; the base gate read the wave dir alone whenever it held any
    report, hiding the capture-only ones. A suffix committed in both trees is
    read once, from the `.ufo/waves/round-N/` copy (the author's bytes; the
    capture is a copy of it)."""
    wave_prefix = ".ufo/waves/round-%d/" % round_no
    capture_prefix = "census/round-%d/waves/" % round_no
    chosen = {}
    for prefix, wins in ((capture_prefix, False), (wave_prefix, True)):
        for path in tree:
            if not path.startswith(prefix) or not path.endswith(".md"):
                continue
            suffix = path[len(prefix):]
            if wins or suffix not in chosen:
                chosen[suffix] = path
    return sorted(chosen.values())


def check_carry(root, tree, rev, round_no):
    """Return (findings, n_markers, n_reports, n_status, carry_heading)."""
    wave_prefix = ".ufo/waves/round-%d/" % round_no
    capture_prefix = "census/round-%d/waves/" % round_no
    reports = _report_paths(tree, round_no)
    if not reports:
        raise EvalError(
            "no .md reports under %s or %s at %s"
            % (wave_prefix, capture_prefix, rev)
        )

    lesson_path = "corpus/lessons/round-%d.md" % round_no
    lesson = None
    if lesson_path in tree:
        lesson = blob_by_oid(root, tree[lesson_path]).decode("utf-8", "replace")

    carry_lines = []
    lesson_admitted = False
    carry_heading = False
    if lesson is not None:
        carry_lines = failures_section_lines(lesson)
        carry_heading = any(
            FAILURES_HEADING_RE.match(line.strip())
            for line in lesson_lines(lesson)
        )
        lesson_admitted = bool(ADMITTED_TRUE_RE.search(lesson))

    findings = []
    n_markers = 0
    n_status = 0
    carried_open = []
    wrap_strict = round_no >= WRAP_STRICT_FROM_ROUND
    entries = carry_entries(carry_lines) if wrap_strict else []
    for report_path in reports:
        text = blob_by_oid(root, tree[report_path]).decode("utf-8", "replace")
        n_status += status_line_count(text)
        report_lines = text.splitlines()
        for lineno, raw in seat_failure_lines(text):
            n_markers += 1
            needle = norm_line(raw)
            carried = None
            block = None
            if wrap_strict:
                block = status_paragraph(report_lines, lineno - 1)
                for entry in entries:
                    if CARRY_TOKEN_RE.search(entry) and carries(block, entry):
                        carried = entry
                        break
            else:
                for lline in carry_lines:
                    nl = norm_line(lline)
                    if needle and needle in nl and CARRY_TOKEN_RE.search(nl):
                        carried = nl
                        break
            detail = "line %d: %s" % (lineno, needle[:220])
            if carried is None:
                if block is not None and len(block) > 1:
                    detail += (
                        "; paragraph continues at line %d "
                        "(mark the cut with ...)" % (lineno + 1)
                    )
                findings.append(("LG-SEAT-UNCARRIED", report_path, detail))
            elif re.search(r"(?i)\bopen\b", carried):
                carried_open.append((report_path, detail, carried))

    if lesson_admitted:
        for report_path, detail, _cl in carried_open:
            findings.append(
                (
                    "LG-OPEN-ADMITTED",
                    report_path,
                    detail + " carried open while lesson declares admitted: true",
                )
            )
    return findings, n_markers, len(reports), n_status, carry_heading


# ---------------------------------------------------------------------------
# Frozen pins (LG-FROZEN-PIN / LG-FROZEN-MEASURED)
# ---------------------------------------------------------------------------


def _pin_repo_path(frozen_dir, key):
    """Repo path a pin key addresses, per the pinned prefix rule."""
    if any(key.startswith(p) for p in ROOT_PREFIXES):
        return key
    return "%s/%s" % (frozen_dir, key)


def check_frozen_pins(root, tree, rev, round_no, exemptions=()):
    """Return findings, check counts, and exemptions used for measured commits."""
    findings = []
    n_checks = 0
    n_measured = 0
    used_exemptions = set()
    frozen_dirs = sorted(
        os.path.dirname(p)
        for p in tree
        if EXPECTED_JSON_RE.match(p)
    )
    for frozen_dir in frozen_dirs:
        exp_path = "%s/expected.json" % frozen_dir
        try:
            expected = json.loads(
                blob_by_oid(root, tree[exp_path]).decode("utf-8")
            )
        except (ValueError, UnicodeDecodeError) as exc:
            # r17 F5: unreadable/malformed expected.json is the same
            # could-not-evaluate shape-defect class as a falsy `files` —
            # exit 2, not a finding.
            raise EvalError("%s: expected.json unreadable: %s" % (exp_path, exc))
        if not isinstance(expected, dict):
            raise EvalError(
                "%s: expected.json is not an object: %r" % (exp_path, expected)
            )
        files = expected.get("files")
        # r17 S2: a falsy `files` (null, [], "", 0, false, {}) cannot fold to
        # zero checks while reporting clean — a shape defect in the pin
        # contract is could-not-evaluate, not a finding. A truthy non-object
        # is the same could-not-evaluate class (exit 2, not a crash).
        if not isinstance(files, dict) or not files:
            raise EvalError(
                "%s: 'files' is absent, falsy or not an object: %r"
                % (exp_path, files)
            )
        record_key = expected.get("record")
        record_repo = _pin_repo_path(frozen_dir, record_key) if record_key else None
        for key, pinned in sorted(files.items()):
            n_checks += 1
            repo_path = _pin_repo_path(frozen_dir, key)
            oid = tree.get(repo_path)
            actual = sha256(blob_by_oid(root, oid)) if oid else None
            if actual is None:
                findings.append(
                    (
                        "LG-FROZEN-PIN",
                        exp_path,
                        "files[%s] resolves to absent path %s" % (key, repo_path),
                    )
                )
            elif not isinstance(pinned, str) or not SHA256_RE.match(pinned):
                findings.append(
                    (
                        "LG-FROZEN-PIN",
                        exp_path,
                        "files[%s] pinned value is not a sha256: %r" % (key, pinned),
                    )
                )
            elif actual != pinned:
                findings.append(
                    (
                        "LG-FROZEN-PIN",
                        exp_path,
                        "files[%s] pinned %s but %s hashes %s"
                        % (key, pinned[:16], repo_path, actual[:16]),
                    )
                )
        if "record_sha256" in expected:
            n_checks += 1
            record_bytes = blob_by_oid(root, tree[record_repo]) if record_repo and record_repo in tree else None
            if record_bytes is None:
                findings.append(
                    (
                        "LG-FROZEN-PIN",
                        exp_path,
                        "record_sha256 present but record %s absent"
                        % (record_repo or "<unset 'record' key>"),
                    )
                )
            else:
                actual = sha256(record_bytes)
                pinned = expected["record_sha256"]
                if not isinstance(pinned, str) or not SHA256_RE.match(pinned):
                    findings.append(
                        (
                            "LG-FROZEN-PIN",
                            exp_path,
                            "record_sha256 is not a sha256: %r" % pinned,
                        )
                    )
                elif actual != pinned:
                    findings.append(
                        (
                            "LG-FROZEN-PIN",
                            exp_path,
                            "record_sha256 pinned %s but record hashes %s"
                            % (pinned[:16], actual[:16]),
                        )
                    )
        # measured_commit cross-check (LG-FROZEN-MEASURED)
        if record_bytes := (blob_by_oid(root, tree[record_repo]) if record_repo and record_repo in tree else None):
            try:
                record = json.loads(record_bytes.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                record = {}
            measured = record.get("measured_commit") if isinstance(record, dict) else None
            if isinstance(measured, str) and re.match(
                r"^[0-9a-fA-F]{4,64}$", measured
            ):
                # Resolve before comparing pinned digests. A dangling value
                # stays silent for pinned pre-r18 replays and is a finding
                # from round 18 onward; other git failures remain exit 2.
                verify = subprocess.run(
                    ["git", "-C", root, "rev-parse", "--verify", "--quiet",
                     measured + "^{commit}"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    env=GIT_ENV,
                )
                if verify.returncode not in (0, 1):
                    raise EvalError(
                        "git rev-parse %s^{commit} failed (rc=%d): %s"
                        % (
                            measured,
                            verify.returncode,
                            verify.stderr.decode("utf-8", "replace").strip()[:300],
                        )
                    )
                measured_ok = verify.returncode == 0
            else:
                measured_ok = False
            if (
                round_no >= 18
                and isinstance(record, dict)
                and "measured_commit" in record
                and not measured_ok
            ):
                if (
                    record_repo in exemptions
                    and measured == MEASURED_COMMIT_PLACEHOLDER
                ):
                    used_exemptions.add(record_repo)
                else:
                    findings.append(
                        (
                            "LG-FROZEN-MEASURED",
                            exp_path,
                            "measured_commit %r does not resolve to a commit"
                            % measured,
                        )
                    )
            if measured_ok:
                for key, pinned in sorted(files.items()):
                    n_measured += 1
                    repo_path = _pin_repo_path(frozen_dir, key)
                    blob = blob_at_path(root, measured, repo_path)
                    if blob is None:
                        findings.append(
                            (
                                "LG-FROZEN-MEASURED",
                                exp_path,
                                "files[%s] absent at measured_commit %s (path %s)"
                                % (key, measured[:12], repo_path),
                            )
                        )
                    elif sha256(blob) != pinned:
                        findings.append(
                            (
                                "LG-FROZEN-MEASURED",
                                exp_path,
                                "files[%s] pinned %s but %s:%s hashes %s"
                                % (
                                    key,
                                    str(pinned)[:16],
                                    measured[:12],
                                    repo_path,
                                    sha256(blob)[:16],
                                ),
                            )
                        )
    return findings, n_checks, n_measured, used_exemptions


# ---------------------------------------------------------------------------
# Citation pointers (LG-DANGLING-PTR; round 18+)
#
# r30 C2: a `.ufo/waves/round-N/...` pointer also resolves through its
# committed capture census/round-N/waves/... (CAPTURE_POINTER_RE), and a token
# carrying a template placeholder (TEMPLATE_POINTER_RE, or a `round-` cut) is
# not a pointer at all.
# ---------------------------------------------------------------------------


def _round_heading_number(line):
    if not re.match(r"^##\s", line):
        return None
    match = re.search(r"\bround(?:-|\s+)(\d+)\b", line, re.IGNORECASE)
    return int(match.group(1)) if match else None


def _round_log_lines(text, round_no):
    """Collect all H2 sections numbered round_no, through same-round entries."""
    selected = []
    in_round = False
    for line_no, line in enumerate(text.splitlines(), 1):
        number = _round_heading_number(line)
        if number == round_no:
            in_round = True
        elif number is not None:
            in_round = False
        if in_round:
            selected.append((line_no, line))
    return selected


def _expand_braces(path):
    match = re.search(r"\{([^{}]*)\}", path)
    if not match or "," not in match.group(1):
        return [path]
    choices = match.group(1).split(",")
    if len(choices) < 2 or any(not choice for choice in choices):
        return [path]
    out = []
    for choice in choices:
        out.extend(_expand_braces(path[:match.start()] + choice + path[match.end():]))
    return out


def _expand_round_ranges(path):
    match = ROUND_RANGE_RE.search(path)
    if not match:
        return [path]
    first, last = map(int, match.groups())
    if last < first:
        return [path]
    out = []
    for number in range(first, last + 1):
        expanded = (
            path[:match.start()]
            + "round-%d" % number
            + path[match.end():]
        )
        out.extend(_expand_round_ranges(expanded))
    return out


def _trim_pointer_token(token):
    """Drop punctuation, a `:line` spec and a `:<text>` suffix from a token.

    r31 C2: a line spec may be a single number, a hyphen range, an en/em dash
    range or a comma list (`tools/x.py:274–277`), and a `:<non-digit>` suffix
    after a path names something inside the cited path (a capture's
    `:fixture/` slot), not part of it. Both are removed before resolution;
    neither was, so both were reported as loud absent paths."""
    token = token.rstrip(".,;:!?")
    token = re.sub(r":\d+(?:[-\u2013\u2014,]\d+)*$", "", token)
    token = re.sub(r":(?![0-9])[^:\s]*$", "", token)
    return token


def _prose_pointer(path):
    """True iff `path` is prose slash alternation, not a path: no trailing `/`
    and every component is letters only (`corpus/authority`,
    `tools/kill/killpg`). A `.`, `-`, `_`, digit or empty component makes it a
    candidate path again (r31 C2)."""
    if path.endswith("/"):
        return False
    components = path.split("/")
    return all(LETTERS_ONLY_RE.fullmatch(component) for component in components)


def _normalize_pointer_path(path, source):
    if path.startswith(("../", "./")):
        return posixpath.normpath(
            posixpath.join(posixpath.dirname(source), path)
        )
    if any(component in (".", "..") for component in path.split("/")):
        return posixpath.normpath(path)
    return path


def _balanced_braces(token):
    depth = 0
    for char in token:
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def _pointer_paths(text, source):
    for match in POINTER_PATH_RE.finditer(text):
        raw = match.group(0)
        if (
            not raw
            or "…" in raw
            or "..." in raw
            or any(char in raw for char in "<>*")
            or ROUND_PLACEHOLDER_RE.search(raw)
            or not _balanced_braces(raw)
        ):
            continue
        # A comma outside braces separates citations; each member must lose
        # its own :line suffix before path resolution.
        parts = []
        depth = 0
        start = 0
        for index, char in enumerate(raw):
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            elif char == "," and depth == 0:
                parts.append(raw[start:index])
                start = index + 1
        parts.append(raw[start:])
        for part in parts:
            part = _trim_pointer_token(part)
            if not part:
                continue
            if (
                TEMPLATE_POINTER_RE.search(part)
                or part.rstrip("/").endswith("round-")
            ):
                continue
            normalized = _normalize_pointer_path(part, source)
            if (
                _safe_pointer_path(normalized)
                and not normalized.startswith(POINTER_ROOTS)
            ):
                continue
            for braced in _expand_braces(normalized):
                for expanded in _expand_round_ranges(braced):
                    expanded = _trim_pointer_token(expanded)
                    if expanded:
                        yield expanded


def _safe_pointer_path(path):
    if not path or path.startswith("/"):
        return False
    components = path.rstrip("/").split("/")
    return all(component and component not in (".", "..") for component in components)


def _path_exists_in_tree(path, tree_paths):
    return _safe_pointer_path(path) and path.rstrip("/") in tree_paths


def _capture_pointer_path(path):
    """Map `.ufo/waves/round-N/<suffix>` onto census/round-N/waves/<suffix>.

    The wave dir is gitignored; its capture (tools/souji-wave-evidence-capture.sh)
    keeps the same relative names, so the same suffix is where the bytes were
    committed. A bare directory pointer maps onto the capture directory, which
    `tree_paths` holds only when that directory carries a committed blob."""
    match = CAPTURE_POINTER_RE.match(path.rstrip("/"))
    if not match:
        return None
    return "census/%s/waves%s" % (match.group(1), match.group(2) or "")


def _captured_pointer_path(path):
    """Map a pointer at a gitignored/stored name onto the capture's name.

    `tools/souji-wave-evidence-capture.sh store_name` stores every component
    named `.git` as `.git.captured` and a file named `.gitignore` or
    `.gitattributes` as `<name>.captured`, so a committed pointer at the live
    name resolves there (r31 C2). None when no component is such a name."""
    trailing = "/" if path.endswith("/") else ""
    components = path.rstrip("/").split("/")
    out = []
    changed = False
    for index, component in enumerate(components):
        last = index == len(components) - 1
        if component == CAPTURE_STORED_GIT:
            out.append(CAPTURE_STORED_GIT + ".captured")
            changed = True
        elif last and component in CAPTURE_RENAME_NAMES:
            out.append(component + ".captured")
            changed = True
        else:
            out.append(component)
    if not changed:
        return None
    return "/".join(out) + trailing


def _pointer_candidates(path):
    """Resolution candidates for one cited token, in order: the path as cited,
    its capture-mapped form (r30), and the stored `.captured` name of either
    (r31)."""
    candidates = [path]
    for candidate in (path, _capture_pointer_path(path)):
        if candidate is None:
            continue
        if candidate not in candidates:
            candidates.append(candidate)
        stored = _captured_pointer_path(candidate)
        if stored is not None and stored not in candidates:
            candidates.append(stored)
    return candidates


def load_pointer_exemptions(root, tree):
    oid = tree.get(POINTER_EXEMPTIONS_PATH)
    if oid is None:
        return set()
    try:
        text = blob_by_oid(root, oid).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EvalError("%s is not UTF-8: %s" % (POINTER_EXEMPTIONS_PATH, exc))
    exemptions = set()
    for line_no, line in enumerate(text.splitlines(), 1):
        fields = line.split("\t")
        if (
            len(fields) != 2
            or not fields[0]
            or fields[0] != fields[0].strip()
            or not fields[1].strip()
            or not fields[0].startswith(POINTER_ROOTS)
            or not _safe_pointer_path(fields[0])
            or any(char in fields[0] for char in "<>*")
            or fields[0] in exemptions
        ):
            raise EvalError(
                "%s:%d malformed exemption row (expected unique path<TAB>reason)"
                % (POINTER_EXEMPTIONS_PATH, line_no)
            )
        exemptions.add(fields[0])
    return exemptions


def check_pointers(root, tree, rev, round_no, fleet_root=None, exemptions=()):
    """Return findings, fleet classifications, counts, and used exemptions."""
    if fleet_root is not None and not os.path.isdir(fleet_root):
        raise EvalError("--fleet-root %s is not a directory" % fleet_root)
    tree_paths = set(tree)
    for path in tree:
        parent = os.path.dirname(path)
        while parent:
            tree_paths.add(parent)
            parent = os.path.dirname(parent)

    sources = {
        path for path in (
            "SKILL.md",
            "SHONEN.md",
            "SCORECARD.md",
            "PROVINCE.md",
            "corpus/QUALITY.md",
            "corpus/README.md",
            "corpus/lessons/round-%d.md" % round_no,
            "corpus/lessons/round-%d-verifier-spotcheck.md" % round_no,
        ) if path in tree
    }
    sources.update(
        path for path in tree
        if path.startswith("corpus/knowledge/")
        and path.count("/") == 2
        and path.endswith(".md")
    )

    source_lines = []
    for source in sorted(sources):
        text = blob_by_oid(root, tree[source]).decode("utf-8", "replace")
        source_lines.extend(
            (source, line_no, line)
            for line_no, line in enumerate(text.splitlines(), 1)
        )

    if "LOG.md" in tree:
        log_text = blob_by_oid(root, tree["LOG.md"]).decode("utf-8", "replace")
        source_lines.extend(
            ("LOG.md", line_no, line)
            for line_no, line in _round_log_lines(log_text, round_no)
        )

    findings = []
    fleet = []
    used_exemptions = set()
    checked_ptrs = ptr_fleet = 0
    for source, line_no, line in source_lines:
        for path in _pointer_paths(line, source):
            checked_ptrs += 1
            if any(
                _path_exists_in_tree(candidate, tree_paths)
                for candidate in _pointer_candidates(path)
            ):
                continue
            if path in exemptions:
                used_exemptions.add(path)
                continue
            if _prose_pointer(path):
                # Counted and exemptible above, but never reported: a
                # letters-only slash alternation names prose, not a path.
                continue
            # Only an explicit one-level escape or the known hyaku report
            # prefix may resolve under the separately supplied fleet root.
            fleet_path = None
            if path.startswith("../") and not path.startswith("../../"):
                fleet_path = path[3:]
            elif path.startswith(".ufo/waves/hyaku/"):
                fleet_path = path
            if (
                fleet_path is not None
                and fleet_root is not None
                and _safe_pointer_path(fleet_path)
                and os.path.exists(os.path.join(fleet_root, fleet_path))
            ):
                fleet.append(
                    {
                        "classification": "fleet",
                        "path": fleet_path,
                        "source": source,
                        "line": line_no,
                    }
                )
                ptr_fleet += 1
                continue
            findings.append(
                (
                    "LG-DANGLING-PTR",
                    path,
                    "%s:%d cites path absent at %s" % (source, line_no, rev[:12]),
                )
            )
    return findings, fleet, checked_ptrs, ptr_fleet, used_exemptions




# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


def evaluate(root, rev, round_no, base=None, fleet_root=None):
    """Return dict {exit, findings, counts, error}.

    exit: 0 (no findings), 1 (findings), 2 (could-not-evaluate)."""
    result = {
        "exit": 2,
        "findings": [],
        "checked_reg": 0,
        "checked_changed": 0,
        "checked_pins": 0,
        # r18: was missing, so every early could-not-evaluate (unknown rev,
        # missing SKILL.md, malformed exemptions) crashed in emit() with a
        # KeyError traceback and exit 1 instead of exit 2.
        "checked_measured": 0,
        "checked_markers": 0,
        "checked_reports": 0,
        "status_lines": 0,
        "carry_heading": 0,
        "error": None,
    }
    snapdir = tempfile.mkdtemp(prefix="souji-landing-gate-", dir="/var/tmp")
    try:
        resolved = resolve_commit(root, rev)
        result["resolved_rev"] = resolved
        if base is not None:
            result["resolved_base"] = resolve_commit(root, base)
        tree = list_tree(root, resolved)
        pointer_exemptions = (
            load_pointer_exemptions(root, tree) if round_no >= 18 else set()
        )

        if "SKILL.md" not in tree:
            raise EvalError("no SKILL.md at %s" % resolved)
        skill = blob_by_oid(root, tree["SKILL.md"]).decode("utf-8", "replace")

        # LG-PARSE-REG / LG-MISSING-REG: cited registry scripts at REV.
        findings = []
        cited = sorted(set(CITED_PATH_RE.findall(skill)))
        for path in cited:
            if path not in tree:
                findings.append(
                    ("LG-MISSING-REG", path, "cited in SKILL.md but absent at %s" % resolved[:12])
                )
                continue
            result["checked_reg"] += 1
            detail = parse_script(root, tree, path, snapdir)
            if detail:
                findings.append(("LG-PARSE-REG", path, detail))

        # LG-PARSE-CHANGED: scripts added/modified in BASE..REV. NUL-split
        # (`-z`) so paths containing spaces or C-quoted non-ASCII bytes are
        # exact; a reported path absent from the enumerated tree is
        # could-not-evaluate, never a crash or a silent skip (r17 F1).
        if base is not None:
            changed_out = _git(
                root,
                ["diff", "--name-only", "-z", "--diff-filter=AM", base, resolved],
            )
            for path in sorted(
                {
                    p.decode("utf-8", "surrogateescape")
                    for p in changed_out.split(b"\0")
                    if p
                }
            ):
                if not SCRIPT_EXT_RE.search(path):
                    continue
                if path not in tree:
                    raise EvalError(
                        "diff path %r absent from tree at %s" % (path, resolved[:12])
                    )
                result["checked_changed"] += 1
                detail = parse_script(root, tree, path, snapdir)
                if detail:
                    findings.append(("LG-PARSE-CHANGED", path, detail))

        # LG-FROZEN-PIN / LG-FROZEN-MEASURED.
        pin_findings, n_pins, n_measured, measured_exemptions = check_frozen_pins(
            root, tree, resolved, round_no, pointer_exemptions
        )
        findings.extend(pin_findings)
        result["checked_pins"] = n_pins
        result["checked_measured"] = n_measured

        # Evaluate pointers before carry. A pre-wave round-18 baseline may
        # have no reports yet; preserve that could-not-evaluate result while
        # still returning its independent pointer findings.
        if round_no >= 18:
            (
                pointer_findings,
                fleet,
                checked_ptrs,
                ptr_fleet,
                pointer_exemptions_used,
            ) = check_pointers(
                root, tree, resolved, round_no,
                fleet_root=fleet_root, exemptions=pointer_exemptions,
            )
            findings.extend(pointer_findings)
            result["fleet"] = fleet
            result["checked_ptrs"] = checked_ptrs
            result["ptr_fleet"] = ptr_fleet
            used_exemptions = measured_exemptions | pointer_exemptions_used
            result["ptr_exempt"] = len(used_exemptions)
            for path in sorted(pointer_exemptions - used_exemptions):
                findings.append(
                    (
                        "LG-DANGLING-PTR-EXEMPT-STALE",
                        path,
                        "exemption does not suppress an unresolved pointer or "
                        "dangling measured_commit at %s" % resolved[:12],
                    )
                )

        # LG-SEAT-UNCARRIED / LG-OPEN-ADMITTED.
        try:
            carry_findings, n_markers, n_reports, n_status, carry_heading = check_carry(
                root, tree, resolved, round_no
            )
        except EvalError as exc:
            if round_no < 18:
                raise
            result["error"] = str(exc)
            carry_findings = []
            n_markers = n_reports = n_status = 0
            carry_heading = False
        findings.extend(carry_findings)
        result["checked_markers"] = n_markers
        result["checked_reports"] = n_reports
        result["status_lines"] = n_status
        result["carry_heading"] = 1 if carry_heading else 0

        findings.sort(key=lambda f: (f[0], f[1], f[2]))
        result["findings"] = [
            {"id": i, "path": p, "detail": d} for i, p, d in findings
        ]
        result["exit"] = 2 if result["error"] else (1 if findings else 0)
    except EvalError as exc:
        result["error"] = str(exc)
        result["exit"] = 2
    finally:
        shutil.rmtree(snapdir, ignore_errors=True)
    return result


def emit(result, json_out=None):
    """Print TSV findings + SUMMARY; optionally write --json (refuse overwrite)."""
    for f in result["findings"]:
        detail = f["detail"].replace("\t", " ").replace("\n", " ")
        print("%s\t%s\t%s" % (f["id"], f["path"], detail))
    print(
        "SUMMARY\tfindings=%d\tchecked_reg=%d\tchecked_changed=%d\tchecked_pins=%d\tchecked_measured=%d\tchecked_markers=%d\tstatus_lines=%d\tcarry_heading=%d\tchecked_reports=%d"
        % (
            len(result["findings"]),
            result["checked_reg"],
            result["checked_changed"],
            result["checked_pins"],
            result["checked_measured"],
            result["checked_markers"],
            result["status_lines"],
            result["carry_heading"],
            result["checked_reports"],
        )
    )
    if result["error"]:
        print("COULD-NOT-EVALUATE\t%s" % result["error"], file=sys.stderr)
    if json_out:
        if os.path.exists(json_out):
            print("--json output %s exists; refusing to overwrite" % json_out, file=sys.stderr)
            return 2
        payload = {
            "exit": result["exit"],
            "findings": result["findings"],
            "summary": {
                "findings": len(result["findings"]),
                "checked_reg": result["checked_reg"],
                "checked_changed": result["checked_changed"],
                "checked_pins": result["checked_pins"],
                "checked_measured": result["checked_measured"],
                "checked_markers": result["checked_markers"],
                "status_lines": result["status_lines"],
                "carry_heading": result["carry_heading"],
                "checked_reports": result["checked_reports"],
            },
            "resolved_rev": result.get("resolved_rev"),
            "resolved_base": result.get("resolved_base"),
            "error": result["error"],
        }
        if "checked_ptrs" in result:
            for key in ("checked_ptrs", "ptr_exempt", "ptr_fleet"):
                payload["summary"][key] = result[key]
        if "fleet" in result:
            payload["fleet"] = result["fleet"]
        try:
            with open(json_out, "x", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2, sort_keys=True)
                fh.write("\n")
        except OSError as exc:
            print("--json write failed: %s" % exc, file=sys.stderr)
            return 2
    return result["exit"]


# ---------------------------------------------------------------------------
# Selftest — synthetic repos under /var/tmp, removed afterwards
# ---------------------------------------------------------------------------

GOOD_SH = "#!/bin/sh\necho ok\n"
BAD_SH = "#!/bin/sh\nif true; then\n  echo broken\n"  # missing fi
GOOD_PY = "print('ok')\n"
BAD_PY = "def broken(:\n"

BASE_LESSON = "# Round 16\n\nAll good.\n"


def _mkrepo(path):
    os.makedirs(path, exist_ok=True)
    env = dict(GIT_ENV)
    env["GIT_AUTHOR_NAME"] = env["GIT_COMMITTER_NAME"] = "selftest"
    env["GIT_AUTHOR_EMAIL"] = env["GIT_COMMITTER_EMAIL"] = "selftest@test"
    env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = "2026-01-01T00:00:00Z"

    def g(*args, inp=None):
        proc = subprocess.run(
            ["git", "-C", path] + list(args),
            input=inp,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        if proc.returncode != 0:
            raise EvalError(
                "selftest git %s failed: %s" % (args[0], proc.stderr.decode()[:200])
            )
        return proc.stdout.decode()

    g("init", "-q", "-b", "main")
    return g


def _write_file(repo, relpath, content):
    dest = os.path.join(repo, relpath)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    mode = "wb" if isinstance(content, bytes) else "w"
    with open(dest, mode) as fh:
        fh.write(content)


def _commit_all(g, repo, msg):
    g("add", "-A")
    g("commit", "-q", "-m", msg)
    return g("rev-parse", "HEAD").strip()


def _sha(repo, relpath):
    with open(os.path.join(repo, relpath), "rb") as fh:
        return sha256(fh.read())


def _base_files():
    """The minimal green world: cited scripts, frozen pins, wave report."""
    files = {
        "SKILL.md": (
            "# skill\n"
            "| probe | `bash tools/good.sh --x` | row |\n"
            "| gate | `python3 tools/good.py --x` | row |\n"
            "| runner | `python3 census/round-1/run.py --x` | row |\n"
            "| fixture | `python3 tests/fixtures/fx.py --tool T` | row |\n"
        ),
        "tools/good.sh": GOOD_SH,
        "tools/good.py": GOOD_PY,
        "census/round-1/run.py": GOOD_PY,
        "tests/fixtures/fx.py": GOOD_PY,
        "tools/uncited-bad.sh": BAD_SH,  # parses-broken but never cited
        "corpus/lessons/round-16.md": BASE_LESSON,
        ".ufo/waves/round-16/w1/SeatA.md": "# SeatA\n\nSTATUS: ok — all clean.\n",
        "corpus/lessons/round-17.md": "# Round 17\n\nAll good.\n",
        ".ufo/waves/round-17/w1/Seat17.md": "# Seat17\n\nSTATUS: ok — all clean.\n",
        "corpus/lessons/round-18.md": "# Round 18\n\nAll good.\n",
        ".ufo/waves/round-18/w1/Seat18.md": "# Seat18\n\nSTATUS: ok — all clean.\n",
    }
    return files


def _frozen_world(files):
    """Add a r9-frozen pin set whose pins match the committed bytes."""
    pin_paths = {
        "data.txt": "tests/fixtures/r9-frozen/data.txt",
        "tools/good.sh": "tools/good.sh",
    }
    for key, repo_path in pin_paths.items():
        if repo_path not in files:
            files[repo_path] = "payload for %s\n" % repo_path
    record = {"measured_commit": "0" * 40}
    files["tests/fixtures/r9-frozen/record.json"] = json.dumps(record, indent=2)
    files["tests/fixtures/r9-frozen/expected.json"] = json.dumps(
        {
            "files": {
                key: sha256(
                    files[repo_path].encode()
                    if isinstance(files[repo_path], str)
                    else files[repo_path]
                )
                for key, repo_path in pin_paths.items()
            },
            "record": "record.json",
            "record_sha256": sha256(files["tests/fixtures/r9-frozen/record.json"].encode()),
            "verdict": "clean",
        },
        indent=2,
    )
    return files


def _r14_measured_world(files, measured):
    """Add one frozen r14-shaped record with a caller-selected commit value."""
    frozen_dir = "tests/fixtures/r14-cache-frozen"
    data_path = "%s/dependency.txt" % frozen_dir
    record_path = "%s/record.json" % frozen_dir
    expected_path = "%s/expected.json" % frozen_dir
    data = "synthetic dependency\n"
    record = json.dumps({"measured_commit": measured}, indent=2)
    files[data_path] = data
    files[record_path] = record
    files[expected_path] = json.dumps(
        {
            "files": {"dependency.txt": sha256(data.encode())},
            "record": "record.json",
            "record_sha256": sha256(record.encode()),
            "verdict": "clean",
        },
        indent=2,
    )
    return files


def run_selftest():
    top = tempfile.mkdtemp(prefix="souji-landing-gate-selftest-", dir="/var/tmp")
    passed = failed = 0

    def build(case_name, files, extra_commits=()):
        repo = os.path.join(top, case_name)
        g = _mkrepo(repo)
        for rel, content in files.items():
            _write_file(repo, rel, content)
        rev = _commit_all(g, repo, "base")
        commits = [rev]
        for commit_files in extra_commits:
            for rel, content in commit_files.items():
                _write_file(repo, rel, content)
            commits.append(_commit_all(g, repo, "next"))
        return repo, g, commits

    def check(case_name, repo, expect_exit, expect_ids=(), rev="HEAD", base=None,
              expect_err=None, expect_n=None, expect_counts=None, round_no=16,
              fleet_root=None, expect_paths=None, expect_fleet=None):
        """Assert the EXACT finding-id set plus any requested path detail."""
        nonlocal passed, failed
        res = evaluate(
            repo, rev, round_no, base=base, fleet_root=fleet_root
        )
        ids = sorted({f["id"] for f in res["findings"]})
        finding_paths = sorted(f["path"] for f in res["findings"])
        fleet_paths = sorted(item["path"] for item in res.get("fleet", []))
        ok = (
            res["exit"] == expect_exit
            and set(ids) == set(expect_ids)
            and (expect_err is None or expect_err in (res["error"] or ""))
            and (expect_n is None or len(res["findings"]) == expect_n)
            and (expect_paths is None or finding_paths == sorted(expect_paths))
            and (expect_fleet is None or fleet_paths == sorted(expect_fleet))
            and all(res.get(k) == v for k, v in (expect_counts or {}).items())
        )
        detail = "exit=%d ids=%s paths=%s fleet=%s err=%s" % (
            res["exit"], ids, finding_paths, fleet_paths, res["error"]
        )
        if ok:
            passed += 1
            status = "pass"
        else:
            failed += 1
            status = "FAIL"
        print("CASE\t%s\t%s\t%s" % (status, case_name, detail))

    try:
        # Round-18 citations are checked only in the current round section.
        f = _base_files()
        f["SKILL.md"] += "`census/round-18/missing.json`.\n"
        repo, g, (rev,) = build("dangling-skill-pointer", f)
        check(
            "dangling-skill-pointer", repo, 1, ("LG-DANGLING-PTR",),
            rev=rev, round_no=18, expect_n=1,
            expect_paths=["census/round-18/missing.json"],
        )
        # Even without current-round reports, retain independent pointers and
        # keep the existing fail-closed carry result.
        f = _base_files()
        del f[".ufo/waves/round-18/w1/Seat18.md"]
        f["SKILL.md"] += "`census/round-18/missing.json`.\n"
        repo, g, (rev,) = build("pointer-without-wave-reports", f)
        check(
            "pointer-without-wave-reports", repo, 2,
            ("LG-DANGLING-PTR",), rev=rev, round_no=18,
            expect_err="no .md reports under", expect_n=1,
            expect_paths=["census/round-18/missing.json"],
        )

        # Resolve parent-relative citation paths from their source directory.
        f = _base_files()
        f["corpus/README.md"] = "`../census/round-18/missing.json`.\n"
        repo, g, (rev,) = build("relative-pointer-normalization", f)
        check(
            "relative-pointer-normalization", repo, 1, ("LG-DANGLING-PTR",),
            rev=rev, round_no=18, expect_n=1,
            expect_paths=["census/round-18/missing.json"],
        )

        # A relative target that still escapes the repo is rejected.
        f = _base_files()
        f["corpus/README.md"] = "`../../census/round-18/missing.json`.\n"
        repo, g, (rev,) = build("relative-pointer-escape", f)
        check(
            "relative-pointer-escape", repo, 1, ("LG-DANGLING-PTR",),
            rev=rev, round_no=18, expect_n=1,
            expect_paths=["../census/round-18/missing.json"],
        )

        # SHONEN.md and the optional round verifier spotcheck are sources too.
        f = _base_files()
        f["SHONEN.md"] = "`census/round-18/shonen-missing.json`.\n"
        f["corpus/lessons/round-18-verifier-spotcheck.md"] = (
            "`corpus/spotcheck-missing.md`.\n"
        )
        repo, g, (rev,) = build("extended-pointer-sources", f)
        check(
            "extended-pointer-sources", repo, 1, ("LG-DANGLING-PTR",),
            rev=rev, round_no=18, expect_n=2,
            expect_paths=[
                "census/round-18/shonen-missing.json",
                "corpus/spotcheck-missing.md",
            ],
        )

        # Simple brace alternatives expand independently.
        f = _base_files()
        f["SKILL.md"] += "`tools/{good.sh,missing.sh}`.\n"
        repo, g, (rev,) = build("brace-pointer-expansion", f)
        check(
            "brace-pointer-expansion", repo, 1, ("LG-DANGLING-PTR",),
            rev=rev, round_no=18, expect_n=1,
            expect_paths=["tools/missing.sh"],
        )

        # A :line suffix is removed before resolution.
        f = _base_files()
        f["SKILL.md"] += "`corpus/missing.md:42:`.\n"
        repo, g, (rev,) = build("pointer-line-suffix", f)
        check(
            "pointer-line-suffix", repo, 1, ("LG-DANGLING-PTR",),
            rev=rev, round_no=18, expect_n=1,
            expect_paths=["corpus/missing.md"],
        )

        # Comma-separated citations trim each member's own line suffix.
        f = _base_files()
        f["SKILL.md"] += "`tools/good.sh:12,tools/good.py:20`.\n"
        repo, g, (rev,) = build("pointer-comma-line-suffix", f)
        check("pointer-comma-line-suffix", repo, 0, rev=rev, round_no=18)

        # Brace members have their line suffixes trimmed after expansion.
        f = _base_files()
        f["SKILL.md"] += "`tools/{good.sh:12,good.py:20}`.\n"
        repo, g, (rev,) = build("pointer-brace-line-suffix", f)
        check("pointer-brace-line-suffix", repo, 0, rev=rev, round_no=18)

        # Interior dot segments and a source-relative ./ prefix normalize.
        f = _base_files()
        f["SKILL.md"] += "`corpus/../tools/good.sh` `./tools/good.py`.\n"
        repo, g, (rev,) = build("pointer-interior-dot-segments", f)
        check(
            "pointer-interior-dot-segments", repo, 0,
            rev=rev, round_no=18,
        )

        # Placeholder and wildcard citations are intentionally not findings.
        f = _base_files()
        f["SKILL.md"] += (
            "`tools/<script>.py` `census/round-N/results.json` "
            "`tests/fixtures/*.sh` `census/round-18/live-pairs/…` "
            "`census/round-18/{seat-01..64.json, approvals-*.tsv,`.\n"
        )
        repo, g, (rev,) = build("pointer-placeholder-skip", f)
        check("pointer-placeholder-skip", repo, 0, rev=rev, round_no=18)

        # Inclusive round ranges must resolve each concrete lesson path.
        f = _base_files()
        f["SKILL.md"] += "`corpus/lessons/round-{16..18}.md`.\n"
        f["SKILL.md"] += "`corpus/lessons/round-16..18.md`.\n"
        repo, g, (rev,) = build("pointer-round-range", f)
        check("pointer-round-range", repo, 0, rev=rev, round_no=18)

        # All same-round H2 sections are scanned through later corrections;
        # H3 headings do not end the union and the next-round H2 does.
        f = _base_files()
        f["LOG.md"] = (
            "## Round 17\n`corpus/lessons/missing-17.md`\n\n"
            "## Round 18\n`corpus/lessons/round-18.md`\n\n"
            "### correction notes\n`corpus/lessons/round-18.md`\n\n"
            "## Round 18 correction\n"
            "`census/round-18/log-correction-missing.json`\n\n"
            "## Round 19\n`corpus/lessons/missing-19.md`\n"
        )
        repo, g, (rev,) = build("pointer-log-round-section", f)
        check(
            "pointer-log-round-section", repo, 1, ("LG-DANGLING-PTR",),
            rev=rev, round_no=18, expect_n=1,
            expect_paths=["census/round-18/log-correction-missing.json"],
        )

        # A committed path<TAB>reason exemption suppresses that exact path.
        f = _base_files()
        f["SKILL.md"] += (
            "`corpus/intentional-runtime-state` "
            "`corpus/intentional-runtime-state`.\n"
        )
        f["corpus/pointer-exemptions.tsv"] = (
            "corpus/intentional-runtime-state\truntime-created path\n"
        )
        repo, g, (rev,) = build("pointer-exemption", f)
        check(
            "pointer-exemption", repo, 0, rev=rev, round_no=18,
            expect_counts={"checked_ptrs": 6, "ptr_exempt": 1, "ptr_fleet": 0},
        )

        # The new quarantined path root is scanned and can be reason-exempted.
        f = _base_files()
        f["SKILL.md"] += "Stub: `.ufo/quarantine/round-18/empty-stub`.\n"
        f["corpus/pointer-exemptions.tsv"] = (
            ".ufo/quarantine/round-18/empty-stub\tdeliberately empty stub\n"
        )
        repo, g, (rev,) = build("quarantine-path-exemption", f)
        check(
            "quarantine-path-exemption", repo, 0, rev=rev, round_no=18,
            expect_counts={"checked_ptrs": 5, "ptr_exempt": 1, "ptr_fleet": 0},
        )

        # Without an exemption the same absent quarantine path is a finding.
        f = _base_files()
        f["SKILL.md"] += "Stub: `.ufo/quarantine/round-18/absent-stub`.\n"
        repo, g, (rev,) = build("quarantine-path-absent", f)
        check(
            "quarantine-path-absent", repo, 1, ("LG-DANGLING-PTR",),
            rev=rev, round_no=18, expect_n=1,
            expect_paths=[".ufo/quarantine/round-18/absent-stub"],
        )

        # Exemptions that are unused or resolve in the lane are stale.
        f = _base_files()
        f["corpus/pointer-exemptions.tsv"] = (
            "tools/good.sh\talready resolves\n"
            "corpus/not-cited.md\tno occurrence\n"
        )
        repo, g, (rev,) = build("pointer-stale-exemptions", f)
        check(
            "pointer-stale-exemptions", repo, 1,
            ("LG-DANGLING-PTR-EXEMPT-STALE",), rev=rev, round_no=18,
            expect_n=2,
            expect_paths=["corpus/not-cited.md", "tools/good.sh"],
        )

        # Malformed exemption rows are could-not-evaluate, not clean.
        f = _base_files()
        f["corpus/pointer-exemptions.tsv"] = "corpus/missing.md\t\n"
        repo, g, (rev,) = build("pointer-bad-exemption", f)
        check(
            "pointer-bad-exemption-exit2", repo, 2, rev=rev,
            round_no=18, expect_err="malformed exemption row",
        )

        # r18 totality: an early could-not-evaluate through the CLI (unknown
        # rev; malformed exemptions) must print SUMMARY and exit 2, never a
        # traceback with exit 1 (the b576341 gate crashed in emit()).
        for case_name, cli_rev in (
            ("cli-unknown-rev-exit2", "0" * 40),
            ("cli-bad-exemption-exit2", rev),
        ):
            proc = subprocess.run(
                [
                    sys.executable, os.path.abspath(__file__),
                    "--root", repo, "--rev", cli_rev, "--round", "18",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=GIT_ENV,
            )
            ok = (
                proc.returncode == 2
                and b"Traceback" not in proc.stderr
                and b"SUMMARY\tfindings=" in proc.stdout
            )
            if ok:
                passed += 1
                print("CASE\tpass\t%s\trc=%d" % (case_name, proc.returncode))
            else:
                failed += 1
                print("CASE\tFAIL\t%s\trc=%d stderr=%r"
                      % (case_name, proc.returncode, proc.stderr[-300:]))

        # Fleet-only files are reported as fleet data, not as findings.
        f = _base_files()
        f["corpus/README.md"] = (
            "Fleet report `../../.ufo/waves/hyaku/fleet-only.md`.\n"
        )
        f["corpus/knowledge/fleet.md"] = (
            "Fleet report `.ufo/waves/hyaku/fleet-direct.md`.\n"
        )
        repo, g, (rev,) = build("pointer-fleet-only", f)
        fleet_root = os.path.join(top, "pointer-fleet-root")
        _write_file(fleet_root, ".ufo/waves/hyaku/fleet-only.md", "relative\n")
        _write_file(fleet_root, ".ufo/waves/hyaku/fleet-direct.md", "direct\n")
        check(
            "pointer-fleet-only", repo, 0, rev=rev, round_no=18,
            fleet_root=fleet_root,
            expect_fleet=[
                ".ufo/waves/hyaku/fleet-direct.md",
                ".ufo/waves/hyaku/fleet-only.md",
            ],
        )

        fleet_json = os.path.join(top, "pointer-fleet-only.json")
        proc = subprocess.run(
            [
                sys.executable, os.path.abspath(__file__),
                "--root", repo, "--rev", rev, "--round", "18",
                "--fleet-root", fleet_root, "--json", fleet_json,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=GIT_ENV,
        )
        try:
            with open(fleet_json, encoding="utf-8") as fh:
                fleet_payload = json.load(fh)
        except (OSError, ValueError):
            fleet_payload = {}
        expected_fleet = [
            {
                "classification": "fleet",
                "path": ".ufo/waves/hyaku/fleet-only.md",
                "source": "corpus/README.md",
                "line": 1,
            },
            {
                "classification": "fleet",
                "path": ".ufo/waves/hyaku/fleet-direct.md",
                "source": "corpus/knowledge/fleet.md",
                "line": 1,
            },
        ]
        ok = (
            proc.returncode == 0
            and fleet_payload.get("findings") == []
            and fleet_payload.get("fleet") == expected_fleet
            and fleet_payload.get("summary", {}).get("checked_ptrs") == 6
            and fleet_payload.get("summary", {}).get("ptr_exempt") == 0
            and fleet_payload.get("summary", {}).get("ptr_fleet") == 2
        )
        if ok:
            passed += 1
            print("CASE\tpass\tpointer-fleet-json\trc=%d" % proc.returncode)
        else:
            failed += 1
            print(
                "CASE\tFAIL\tpointer-fleet-json\trc=%d payload=%r stderr=%r"
                % (
                    proc.returncode,
                    fleet_payload,
                    proc.stderr.decode("utf-8", "replace")[:200],
                )
            )

        # A committed lane object takes precedence over a same-path fleet
        # object, and does not increment the fleet classification counter.
        f = _base_files()
        f["SKILL.md"] += "`corpus/shared.md`.\n"
        f["corpus/shared.md"] = "lane file\n"
        repo, g, (rev,) = build("pointer-lane-fleet-collision", f)
        collision_fleet = os.path.join(top, "pointer-collision-fleet")
        _write_file(collision_fleet, "corpus/shared.md", "fleet file\n")
        check(
            "pointer-lane-fleet-collision", repo, 0, rev=rev, round_no=18,
            fleet_root=collision_fleet, expect_fleet=[],
            expect_counts={"checked_ptrs": 5, "ptr_fleet": 0},
        )

        # Exact exemption membership must not match a longer shared prefix.
        f = _base_files()
        f["SKILL.md"] += "`corpus/runtime` `corpus/runtime-extra`.\n"
        f["corpus/pointer-exemptions.tsv"] = "corpus/runtime\texact path\n"
        repo, g, (rev,) = build("pointer-exemption-prefix", f)
        check(
            "pointer-exemption-prefix", repo, 1, ("LG-DANGLING-PTR",),
            rev=rev, round_no=18, expect_n=1,
            expect_paths=["corpus/runtime-extra"],
            expect_counts={"checked_ptrs": 6, "ptr_exempt": 1},
        )

        # Round 17 replays do not acquire the round-18 pointer finding.
        f = _base_files()
        f["SKILL.md"] += "`census/round-17/missing.json`.\n"
        repo, g, (rev,) = build("pointer-before-round-18", f)
        check("pointer-round-17-disabled", repo, 0, rev=rev, round_no=17)

        # A dangling measured_commit is an LG-FROZEN-MEASURED finding at r18.
        repo, g, (rev,) = build(
            "dangling-measured-commit", _frozen_world(_base_files())
        )
        check(
            "dangling-measured-commit", repo, 1,
            ("LG-FROZEN-MEASURED",), rev=rev, round_no=18, expect_n=1,
        )

        # Only the exact historical synthetic placeholder is exemptible.
        record_path = "tests/fixtures/r14-cache-frozen/record.json"
        f = _r14_measured_world(
            _base_files(), MEASURED_COMMIT_PLACEHOLDER
        )
        f["corpus/pointer-exemptions.tsv"] = (
            "%s\tr14 synthetic placeholder\n" % record_path
        )
        repo, g, (rev,) = build("measured-record-placeholder-exemption", f)
        check(
            "measured-record-placeholder-exemption", repo, 0,
            rev=rev, round_no=18, expect_n=0,
            expect_counts={"ptr_exempt": 1},
        )

        # A different dangling value at the same record path remains a
        # measured finding and makes the placeholder-only exemption stale.
        f = _r14_measured_world(_base_files(), "0" * 40)
        f["corpus/pointer-exemptions.tsv"] = (
            "%s\tr14 synthetic placeholder\n" % record_path
        )
        repo, g, (rev,) = build("measured-record-wrong-value", f)
        check(
            "measured-record-wrong-value", repo, 1,
            ("LG-DANGLING-PTR-EXEMPT-STALE", "LG-FROZEN-MEASURED"),
            rev=rev, round_no=18, expect_n=2,
            expect_paths=[
                "tests/fixtures/r14-cache-frozen/expected.json",
                record_path,
            ],
        )

        # CASE clean-pass: everything parses, pins match, STATUS benign.
        repo, g, (rev,) = build("clean-pass", _frozen_world(_base_files()))
        check("clean-pass", repo, 0, rev=rev,
              expect_counts={"checked_reg": 4, "checked_changed": 0,
                             "checked_pins": 3, "checked_measured": 0,
                             "checked_markers": 0, "carry_heading": 0,
                             "status_lines": 1, "checked_reports": 1})

        # CASE clean-measured: a resolvable measured_commit whose pinned
        # bytes match at both revisions emits nothing (r17 F2 — without
        # this, an always-firing measured check passes green).
        repo = os.path.join(top, "clean-measured")
        g = _mkrepo(repo)
        f = _frozen_world(_base_files())
        for rel, content in f.items():
            _write_file(repo, rel, content)
        c1 = _commit_all(g, repo, "pinned bytes")
        record = {"measured_commit": c1}
        _write_file(repo, "tests/fixtures/r9-frozen/record.json", json.dumps(record))
        exp = json.loads(f["tests/fixtures/r9-frozen/expected.json"])
        exp["record_sha256"] = _sha(repo, "tests/fixtures/r9-frozen/record.json")
        _write_file(repo, "tests/fixtures/r9-frozen/expected.json", json.dumps(exp))
        rev = _commit_all(g, repo, "bind measured")
        check("clean-measured", repo, 0, rev=rev,
              expect_counts={"checked_measured": 2, "checked_pins": 3})

        # CASE cli-summary-exact: emit() must serialize every counter — an
        # in-memory assertion cannot see a mutated SUMMARY interpolation
        # (r17 M17). Assert exact positive values on a measured run.
        proc = subprocess.run(
            [
                sys.executable,
                os.path.abspath(__file__),
                "--root", repo, "--rev", rev, "--round", "16",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=GIT_ENV,
        )
        out = proc.stdout.decode("utf-8", "replace")
        ok = proc.returncode == 0 and (
            "SUMMARY\tfindings=0\tchecked_reg=4\tchecked_changed=0\t"
            "checked_pins=3\tchecked_measured=2\tchecked_markers=0\t"
            "status_lines=1\tcarry_heading=0\tchecked_reports=1" in out
        )
        if ok:
            passed += 1
            print("CASE\tpass\tcli-summary-exact\trc=%d" % proc.returncode)
        else:
            failed += 1
            print(
                "CASE\tFAIL\tcli-summary-exact\trc=%d stdout=%r stderr=%r"
                % (proc.returncode, out[-400:], proc.stderr.decode("utf-8", "replace")[:200])
            )

        # CASE nonparsing-cited-sh.
        f = _base_files()
        f["tools/good.sh"] = BAD_SH
        repo, g, (rev,) = build("bad-cited-sh", _frozen_world(f))
        check("nonparsing-cited-sh", repo, 1, ("LG-PARSE-REG",), rev=rev,
              expect_n=1, expect_counts={"checked_reg": 4, "checked_pins": 3})

        # CASE nonparsing-cited-py.
        f = _base_files()
        f["tools/good.py"] = BAD_PY
        repo, g, (rev,) = build("bad-cited-py", _frozen_world(f))
        check("nonparsing-cited-py", repo, 1, ("LG-PARSE-REG",), rev=rev,
              expect_n=1)

        # CASE missing-cited-path.
        f = _base_files()
        f["SKILL.md"] = f["SKILL.md"] + "| gone | `bash tools/gone.sh --x` | row |\n"
        repo, g, (rev,) = build("missing-cited", _frozen_world(f))
        check("missing-cited-path", repo, 1, ("LG-MISSING-REG",), rev=rev,
              expect_n=1)

        # CASE changed-nonparsing-with-base: base parses, rev adds a broken
        # uncited script (exact ids: the cited world stays clean).
        repo, g, commits = build(
            "changed-bad",
            _frozen_world(_base_files()),
            extra_commits=({"tools/new.sh": BAD_SH},),
        )
        check(
            "changed-nonparsing-with-base",
            repo,
            1,
            ("LG-PARSE-CHANGED",),
            rev=commits[1],
            base=commits[0],
            expect_n=1,
            expect_counts={"checked_changed": 1},
        )

        # CASE changed-paths-exact: space and non-ASCII changed paths reach
        # the parser whole — the old whitespace split turned 'space file.sh'
        # into a crash (KeyError) and core.quotepath hid 'café.sh'
        # (r17 F1).
        repo, g, commits = build(
            "changed-paths",
            _frozen_world(_base_files()),
            extra_commits=({
                "tools/space file.sh": GOOD_SH,
                "tools/café.sh": GOOD_SH,
            },),
        )
        check(
            "changed-paths-exact",
            repo,
            0,
            rev=commits[1],
            base=commits[0],
            expect_counts={"checked_changed": 2},
        )

        # CASE uncited-nonparsing-passes-without-base.
        repo, g, (rev,) = build("uncited-bad", _frozen_world(_base_files()))
        check("uncited-nonparsing-not-flagged", repo, 0, rev=rev)

        # CASE pin-mismatch.
        f = _frozen_world(_base_files())
        exp = json.loads(f["tests/fixtures/r9-frozen/expected.json"])
        exp["files"]["tools/good.sh"] = "0" * 64
        f["tests/fixtures/r9-frozen/expected.json"] = json.dumps(exp)
        repo, g, (rev,) = build("pin-mismatch", f)
        check("pin-mismatch", repo, 1, ("LG-FROZEN-PIN",), rev=rev, expect_n=1)

        # CASE pin-missing-file: key addresses absent path.
        f = _frozen_world(_base_files())
        exp = json.loads(f["tests/fixtures/r9-frozen/expected.json"])
        exp["files"]["ghost.txt"] = "0" * 64  # resolves inside frozen dir, absent
        f["tests/fixtures/r9-frozen/expected.json"] = json.dumps(exp)
        repo, g, (rev,) = build("pin-missing", f)
        check("pin-missing-file", repo, 1, ("LG-FROZEN-PIN",), rev=rev, expect_n=1)

        # CASE record-sha256-mismatch.
        f = _frozen_world(_base_files())
        exp = json.loads(f["tests/fixtures/r9-frozen/expected.json"])
        exp["record_sha256"] = "0" * 64
        f["tests/fixtures/r9-frozen/expected.json"] = json.dumps(exp)
        repo, g, (rev,) = build("record-mismatch", f)
        check("record-sha256-mismatch", repo, 1, ("LG-FROZEN-PIN",), rev=rev,
              expect_n=1)

        # CASE frozen-measured: the hash-mismatch branch alone — data.txt
        # has identical bytes at both revisions; only tools/good.sh differs.
        repo = os.path.join(top, "frozen-measured")
        g = _mkrepo(repo)
        _write_file(repo, "tools/good.sh", "old-good-bytes\n")
        _write_file(repo, "tests/fixtures/r9-frozen/data.txt", "v2 bytes\n")
        old_rev = _commit_all(g, repo, "old")
        f = _base_files()
        f["tests/fixtures/r9-frozen/data.txt"] = "v2 bytes\n"
        for rel, content in f.items():
            _write_file(repo, rel, content)
        record = {"measured_commit": old_rev}
        _write_file(repo, "tests/fixtures/r9-frozen/record.json", json.dumps(record))
        exp = {
            "files": {
                "data.txt": _sha(repo, "tests/fixtures/r9-frozen/data.txt"),
                "tools/good.sh": _sha(repo, "tools/good.sh"),  # new bytes
            },
            "record": "record.json",
            "record_sha256": _sha(repo, "tests/fixtures/r9-frozen/record.json"),
            "verdict": "clean",
        }
        _write_file(repo, "tests/fixtures/r9-frozen/expected.json", json.dumps(exp))
        rev = _commit_all(g, repo, "frozen")
        check("frozen-measured", repo, 1, ("LG-FROZEN-MEASURED",), rev=rev,
              expect_n=1, expect_counts={"checked_measured": 2})

        # CASE frozen-measured-absent: the absent-at-measured branch alone —
        # data.txt did not exist at measured_commit; good.sh is unchanged.
        repo = os.path.join(top, "measured-absent")
        g = _mkrepo(repo)
        _write_file(repo, "tools/good.sh", GOOD_SH)
        old_rev = _commit_all(g, repo, "old")
        f = _base_files()
        f["tests/fixtures/r9-frozen/data.txt"] = "v2 bytes\n"
        for rel, content in f.items():
            _write_file(repo, rel, content)
        record = {"measured_commit": old_rev}
        _write_file(repo, "tests/fixtures/r9-frozen/record.json", json.dumps(record))
        exp = {
            "files": {
                "data.txt": _sha(repo, "tests/fixtures/r9-frozen/data.txt"),
                "tools/good.sh": _sha(repo, "tools/good.sh"),
            },
            "record": "record.json",
            "record_sha256": _sha(repo, "tests/fixtures/r9-frozen/record.json"),
            "verdict": "clean",
        }
        _write_file(repo, "tests/fixtures/r9-frozen/expected.json", json.dumps(exp))
        rev = _commit_all(g, repo, "frozen")
        check("frozen-measured-absent", repo, 1, ("LG-FROZEN-MEASURED",), rev=rev,
              expect_n=1)

        # CASE measured-tree-path-exit2: a pin key resolving to a tree at the
        # measured commit makes the blob read fail — could-not-evaluate
        # (exit 2), never a finding (r17 S1).
        repo = os.path.join(top, "tree-path")
        g = _mkrepo(repo)
        _write_file(repo, "tests/fixtures/r9-frozen/tools/x.txt", "x\n")
        _write_file(repo, "tools/good.sh", GOOD_SH)
        old_rev = _commit_all(g, repo, "old")
        f = _base_files()
        f["tests/fixtures/r9-frozen/tools/x.txt"] = "x\n"
        for rel, content in f.items():
            _write_file(repo, rel, content)
        record = {"measured_commit": old_rev}
        _write_file(repo, "tests/fixtures/r9-frozen/record.json", json.dumps(record))
        exp = {
            "files": {"tools": sha256(b"x\n")},
            "record": "record.json",
            "record_sha256": _sha(repo, "tests/fixtures/r9-frozen/record.json"),
            "verdict": "clean",
        }
        _write_file(repo, "tests/fixtures/r9-frozen/expected.json", json.dumps(exp))
        rev = _commit_all(g, repo, "frozen")
        check("measured-tree-path-exit2", repo, 2, rev=rev,
              expect_err="cat-file")

        # CASES falsy/misshapen `files` → exit 2 (r17 S2): a pin set that
        # would silently verify nothing cannot report clean.
        for case_name, value in (
            ("files-null-exit2", None),
            ("files-empty-exit2", {}),
            ("files-nonobject-exit2", "not-a-dict"),
        ):
            f = _frozen_world(_base_files())
            exp = json.loads(f["tests/fixtures/r9-frozen/expected.json"])
            exp["files"] = value
            f["tests/fixtures/r9-frozen/expected.json"] = json.dumps(exp)
            repo, g, (rev,) = build(case_name, f)
            check(case_name, repo, 2, rev=rev,
                  expect_err="'files' is absent, falsy or not an object")

        # CASES malformed expected.json shape → exit 2 (r17 F2/F5): the pin
        # contract's top level is guarded like `files` — a valid-JSON
        # non-object and unreadable JSON are both could-not-evaluate, never
        # a crash (exit 1) or a finding.
        for case_name, content, err in (
            ("expected-nonobject-exit2", json.dumps([1, 2, 3]),
             "expected.json is not an object"),
            ("expected-unreadable-exit2", "{ not json",
             "expected.json unreadable"),
        ):
            f = _frozen_world(_base_files())
            f["tests/fixtures/r9-frozen/expected.json"] = content
            repo, g, (rev,) = build(case_name, f)
            check(case_name, repo, 2, rev=rev, expect_err=err)
        # CASE uncarried-marker: STATUS failure + phrase, lesson lacks them.
        f = _frozen_world(_base_files())
        f[".ufo/waves/round-16/w1/SeatA.md"] = (
            "# SeatA\n\n## STATUS: INCOMPLETE — file has an unresolved syntax error\n"
        )
        repo, g, (rev,) = build("uncarried", f)
        check("uncarried-marker", repo, 1, ("LG-SEAT-UNCARRIED",), rev=rev,
              expect_n=1,
              expect_counts={"status_lines": 1, "carry_heading": 0,
                             "checked_markers": 1, "checked_reports": 1,
                             "checked_pins": 3})

        # CASE bold-uncarried: a bold-decorated STATUS failure is positively
        # in the failure channel (r17 F4 — without it, losing bold
        # acceptance in STATUS_PREFIX_RE passes green).
        f = _frozen_world(_base_files())
        f[".ufo/waves/round-16/w1/SeatA.md"] = (
            "# SeatA\n\n**STATUS:** INCOMPLETE — widget red\n"
        )
        repo, g, (rev,) = build("bold-uncarried", f)
        check("bold-uncarried", repo, 1, ("LG-SEAT-UNCARRIED",), rev=rev,
              expect_n=1)

        # CASE status-in-fence: an identical failure STATUS inside a fenced
        # block is ignored while the outside copy is flagged (r17 F1 —
        # exercises both the fence toggle and the failure detector;
        # expect_n=1 fails if fence tracking is deleted).
        f = _frozen_world(_base_files())
        f[".ufo/waves/round-16/w1/SeatA.md"] = (
            "# SeatA\n\n```\nSTATUS: FAIL — inside a fenced block\n```\n\n"
            "STATUS: FAIL — inside a fenced block\n"
        )
        repo, g, (rev,) = build("fence", f)
        check("status-in-fence", repo, 1, ("LG-SEAT-UNCARRIED",), rev=rev,
              expect_n=1, expect_counts={"status_lines": 2})

        # CASE status-in-table: an identical failure STATUS inside a table
        # row is ignored while the outside copy is flagged (r17 F1).
        f = _frozen_world(_base_files())
        f[".ufo/waves/round-16/w1/SeatA.md"] = (
            "# SeatA\n\n| code | cause |\n|---|---|\n"
            "| 1 | STATUS: FAIL — inside a table row |\n\n"
            "STATUS: FAIL — inside a table row\n"
        )
        repo, g, (rev,) = build("table", f)
        check("status-in-table", repo, 1, ("LG-SEAT-UNCARRIED",), rev=rev,
              expect_n=1, expect_counts={"checked_markers": 1})

        # CASE carried-open: failure carried under the heading with `open`.
        f = _frozen_world(_base_files())
        marker = "## STATUS: INCOMPLETE — file has an unresolved syntax error"
        f[".ufo/waves/round-16/w1/SeatA.md"] = "# SeatA\n\n%s\n" % marker
        f["corpus/lessons/round-16.md"] = (
            "# Round 16\n\n## Seat-reported failures\n\n"
            "- SeatA `.ufo/waves/round-16/w1/SeatA.md:3` %s — open\n" % marker
        )
        repo, g, (rev,) = build("carried-open", f)
        check("carried-open", repo, 0, rev=rev,
              expect_counts={"carry_heading": 1, "status_lines": 1})

        # CASE carried-resolved.
        f = _frozen_world(_base_files())
        marker = "**STATUS:** FAILED — guard refuses"
        f[".ufo/waves/round-16/w1/SeatA.md"] = "# SeatA\n\n%s\n" % marker
        f["corpus/lessons/round-16.md"] = (
            "# Round 16\n\n## Seat-reported failures\n\n"
            "- SeatA `.ufo/waves/round-16/w1/SeatA.md:3` `%s` — resolved@cbf688ab2ab2\n"
            % marker
        )
        repo, g, (rev,) = build("carried-resolved", f)
        check("carried-resolved", repo, 0, rev=rev,
              expect_counts={"carry_heading": 1})

        # CASE open-admitted: carried open + admitted: true → LG-OPEN-ADMITTED.
        f = _frozen_world(_base_files())
        marker = "## STATUS: BROKEN — gate still red"
        f[".ufo/waves/round-16/w1/SeatA.md"] = "# SeatA\n\n%s\n" % marker
        f["corpus/lessons/round-16.md"] = (
            "# Round 16\n\nadmitted: true\n\n## Seat-reported failures\n\n"
            "- SeatA `.ufo/waves/round-16/w1/SeatA.md:3` %s — open\n" % marker
        )
        repo, g, (rev,) = build("open-admitted", f)
        check("open-admitted", repo, 1, ("LG-OPEN-ADMITTED",), rev=rev,
              expect_n=1, expect_counts={"checked_markers": 1})

        # CASE wrap-unmarked (r19 C1): a quote that stops at the SOURCE's
        # first physical line with no ellipsis is a silent cut, not a carry.
        f = _base_files()
        del f[".ufo/waves/round-18/w1/Seat18.md"]
        f[".ufo/waves/round-18/w1/SeatWrap.md"] = (
            "# SeatWrap\n\n"
            "STATUS: PARTIAL — guarded repos measured and the\n"
            "remaining arm never runs under a bound.\n"
        )
        f["corpus/lessons/round-18.md"] = (
            "# Round 18\n\n## Seat-reported failures\n\n"
            "- SeatWrap `.ufo/waves/round-18/w1/SeatWrap.md:3` "
            "\"STATUS: PARTIAL — guarded repos measured and the\" — open\n"
        )
        repo, g, (rev,) = build("wrap-unmarked", f)
        check("wrap-unmarked", repo, 1, ("LG-SEAT-UNCARRIED",), rev=rev,
              round_no=18, expect_n=1,
              expect_counts={"checked_markers": 1, "checked_reports": 1,
                             "status_lines": 1, "carry_heading": 1})

        # CASE wrap-marked: the cut is marked with an ellipsis exactly at the
        # source physical-line end, so the carry is honest.
        f = _base_files()
        del f[".ufo/waves/round-18/w1/Seat18.md"]
        f[".ufo/waves/round-18/w1/SeatWrap.md"] = (
            "# SeatWrap\n\n"
            "STATUS: PARTIAL — guarded repos measured and the\n"
            "remaining arm never runs under a bound.\n"
        )
        f["corpus/lessons/round-18.md"] = (
            "# Round 18\n\n## Seat-reported failures\n\n"
            "- SeatWrap `.ufo/waves/round-18/w1/SeatWrap.md:3` "
            "\"STATUS: PARTIAL — guarded repos measured and the …\" — open\n"
        )
        repo, g, (rev,) = build("wrap-marked", f)
        check("wrap-marked", repo, 0, rev=rev, round_no=18, expect_n=0,
              expect_counts={"checked_markers": 1, "checked_reports": 1,
                             "status_lines": 1, "carry_heading": 1})

        # CASE wrap-complete: the whole paragraph quoted on one line carries
        # without an ellipsis.
        f = _base_files()
        del f[".ufo/waves/round-18/w1/Seat18.md"]
        f[".ufo/waves/round-18/w1/SeatWrap.md"] = (
            "# SeatWrap\n\n"
            "STATUS: PARTIAL — guarded repos measured and the\n"
            "remaining arm never runs under a bound.\n"
        )
        f["corpus/lessons/round-18.md"] = (
            "# Round 18\n\n## Seat-reported failures\n\n"
            "- SeatWrap `.ufo/waves/round-18/w1/SeatWrap.md:3` "
            "\"STATUS: PARTIAL — guarded repos measured and the remaining "
            "arm never runs under a bound.\" — open\n"
        )
        repo, g, (rev,) = build("wrap-complete", f)
        check("wrap-complete", repo, 0, rev=rev, round_no=18, expect_n=0,
              expect_counts={"checked_markers": 1, "checked_reports": 1,
                             "status_lines": 1, "carry_heading": 1})

        # CASE wrap-bullet-wrapped: the LESSON bullet itself wraps; joining
        # the entry must still carry the complete paragraph (false-fail
        # direction).
        f = _base_files()
        del f[".ufo/waves/round-18/w1/Seat18.md"]
        f[".ufo/waves/round-18/w1/SeatWrap.md"] = (
            "# SeatWrap\n\n"
            "STATUS: PARTIAL — guarded repos measured and the\n"
            "remaining arm never runs under a bound.\n"
        )
        f["corpus/lessons/round-18.md"] = (
            "# Round 18\n\n## Seat-reported failures\n\n"
            "- SeatWrap `.ufo/waves/round-18/w1/SeatWrap.md:3` "
            "\"STATUS: PARTIAL — guarded repos measured and the remaining\n"
            "arm never runs under a bound.\" — open\n"
        )
        repo, g, (rev,) = build("wrap-bullet-wrapped", f)
        check("wrap-bullet-wrapped", repo, 0, rev=rev, round_no=18,
              expect_n=0,
              expect_counts={"checked_markers": 1, "checked_reports": 1,
                             "status_lines": 1, "carry_heading": 1})

        # CASE missing-wave-dir → exit 2.
        f = _frozen_world(_base_files())
        del f[".ufo/waves/round-16/w1/SeatA.md"]
        repo, g, (rev,) = build("no-wave-dir", f)
        check("no-wave-dir-exit2", repo, 2, rev=rev,
              expect_err="no .md reports under")

        # CASE benign-status-words: non-vocabulary STATUS values and prose
        # failure phrases inside a fence/table pass (channel, not phrases).
        f = _frozen_world(_base_files())
        f[".ufo/waves/round-16/w1/SeatA.md"] = (
            "# SeatA\n\nSTATUS: none\n\n```\nsyntax error inside a fenced block\n```\n"
            "| note | snapshot_tampered quoted in a table |\n"
            "STATUS — done\n"
        )
        repo, g, (rev,) = build("benign-status", f)
        check("benign-status-words", repo, 0, rev=rev,
              expect_counts={"status_lines": 2})

        # CASE bad-rev → exit 2.
        repo, g, (rev,) = build("badrev", _frozen_world(_base_files()))
        check("bad-rev-exit2", repo, 2, rev="0" * 40,
              expect_err="cannot resolve revision")

        # CASE no-skill → exit 2.
        f = _frozen_world(_base_files())
        del f["SKILL.md"]
        repo, g, (rev,) = build("no-skill", f)
        check("no-skill-exit2", repo, 2, rev="HEAD", expect_err="no SKILL.md")

        # CASE ambient-git-dir (r17 S3): a poisoned GIT_DIR/GIT_WORK_TREE
        # must not redirect revision resolution — --root still selects the
        # repository.
        repo, g, (rev,) = build("ambgitdir", _frozen_world(_base_files()))
        old_dir = os.environ.get("GIT_DIR")
        old_wt = os.environ.get("GIT_WORK_TREE")
        os.environ["GIT_DIR"] = "/nonexistent/souji-r17.git"
        os.environ["GIT_WORK_TREE"] = "/nonexistent/souji-r17-wt"
        try:
            res = evaluate(repo, rev, 16)
        finally:
            if old_dir is None:
                os.environ.pop("GIT_DIR", None)
            else:
                os.environ["GIT_DIR"] = old_dir
            if old_wt is None:
                os.environ.pop("GIT_WORK_TREE", None)
            else:
                os.environ["GIT_WORK_TREE"] = old_wt
        ok = (
            res["exit"] == 0
            and not res["findings"]
            and res.get("resolved_rev") == rev
        )
        if ok:
            passed += 1
            print("CASE\tpass\tambient-git-dir\texit=0 resolved=%s" % rev[:12])
        else:
            failed += 1
            print(
                "CASE\tFAIL\tambient-git-dir\texit=%d resolved=%s err=%s"
                % (res["exit"], res.get("resolved_rev"), res["error"])
            )

        # CASE cli-ambient-git-dir (r17 M09): a gate *child process* whose
        # GIT_DIR/GIT_WORK_TREE are poisoned at process start must still
        # resolve --root. The in-process case above cannot see this: its
        # poison lands after the module-level GIT_ENV snapshot is built.
        env = dict(GIT_ENV)
        env["GIT_DIR"] = "/nonexistent/souji-r17.git"
        env["GIT_WORK_TREE"] = "/nonexistent/souji-r17-wt"
        proc = subprocess.run(
            [
                sys.executable,
                os.path.abspath(__file__),
                "--root", repo, "--rev", rev, "--round", "16",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        ok = proc.returncode == 0 and "SUMMARY\tfindings=0" in proc.stdout.decode(
            "utf-8", "replace"
        )
        if ok:
            passed += 1
            print("CASE\tpass\tcli-ambient-git-dir\trc=%d" % proc.returncode)
        else:
            failed += 1
            print(
                "CASE\tFAIL\tcli-ambient-git-dir\trc=%d stderr=%r"
                % (proc.returncode, proc.stderr.decode("utf-8", "replace")[:200])
            )
    finally:
        shutil.rmtree(top, ignore_errors=True)

    print("SELFTEST\tpass=%d\tfail=%d" % (passed, failed))
    return 0 if failed == 0 else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="souji-landing-gate.py",
        description="Round-18 landing-claim consistency gate (souji C2).",
    )
    ap.add_argument("--root", help="lane repository path")
    ap.add_argument("--rev", help="revision whose committed bytes are checked")
    ap.add_argument("--round", type=int, dest="round_no", help="round number N")
    ap.add_argument("--base", help="optional base revision for changed-script checks")
    ap.add_argument("--fleet-root", help="optional fleet repository for fleet-only pointer classification")
    ap.add_argument("--json", dest="json_out", help="write findings+summary JSON (refuses overwrite)")
    ap.add_argument("--selftest", action="store_true", help="run synthetic-repo selftest")
    args = ap.parse_args(argv)

    if args.selftest:
        return run_selftest()
    if not args.root or not args.rev or args.round_no is None:
        ap.print_usage(sys.stderr)
        return 2
    if not os.path.isdir(args.root):
        print("COULD-NOT-EVALUATE\t--root %s is not a directory" % args.root, file=sys.stderr)
        return 2
    try:
        result = evaluate(
            args.root, args.rev, args.round_no, base=args.base,
            fleet_root=args.fleet_root,
        )
    except Exception as exc:  # belt-and-braces: no uncaught class masquerades
        # as findings (exit 1) — a crash is could-not-evaluate (r17 F1).
        result = {
            "exit": 2,
            "findings": [],
            "checked_reg": 0,
            "checked_changed": 0,
            "checked_pins": 0,
            "checked_markers": 0,
            "checked_reports": 0,
            "checked_measured": 0,
            "status_lines": 0,
            "carry_heading": 0,
            "resolved_rev": None,
            "resolved_base": None,
            "error": "internal error: %s: %s" % (type(exc).__name__, exc),
        }
    return emit(result, json_out=args.json_out)


if __name__ == "__main__":
    sys.exit(main())
