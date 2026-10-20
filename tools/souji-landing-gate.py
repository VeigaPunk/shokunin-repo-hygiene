#!/usr/bin/env python3
"""souji-landing-gate.py — round-16 C2 landing-claim consistency gate.

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

Scope: landing-claim consistency and failure-channel carry only.
It is NOT a disclosure-enforcement or behavioral-regression suite; it never
executes repository code (only `bash -n FILE` and Python compile()).

Byte provenance: committed bytes are read with `git -C LANE ls-tree -r -z
--full-tree REV` and `git cat-file blob <oid>` (never `git archive`, whose
export-ignore/export-subst/attributes can alter bytes). Files that need a
real path for `bash -n` are written under a private
tempfile.mkdtemp(dir='/var/tmp') snapshot removed in `finally`.

CLI:
  python3 tools/souji-landing-gate.py --root LANE --rev REV --round N
      [--base REV] [--json OUT]
  python3 tools/souji-landing-gate.py --selftest

Exit: 0 no findings, 1 findings, 2 could-not-evaluate (usage, unknown rev,
no SKILL.md, missing .ufo/waves/round-N/ at REV, git failure).

Output: one TSV line per finding `ID\\tpath\\tdetail` (sorted), then
`SUMMARY\\tfindings=K\\tchecked_reg=A\\tchecked_pins=B\\tchecked_markers=C\\tchecked_reports=D`.

Finding ids (pinned): LG-PARSE-REG, LG-MISSING-REG, LG-PARSE-CHANGED,
LG-FROZEN-PIN, LG-FROZEN-MEASURED, LG-SEAT-UNCARRIED, LG-OPEN-ADMITTED.
"""

import argparse
import hashlib
import json
import os
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
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

# Frozen-pin path rule (pinned): an expected.json `files`/`record` key that
# starts with one of these top-level prefixes resolves at the snapshot root;
# any other key resolves inside the frozen dir. No fallback either way.
ROOT_PREFIXES = ("tools/", "tests/", "census/", "corpus/")

EXPECTED_JSON_RE = re.compile(r"tests/fixtures/[^/]+-frozen/expected\.json$")
SCRIPT_EXT_RE = re.compile(r"\.(?:sh|py)$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

FINDING_IDS = (
    "LG-PARSE-REG",
    "LG-MISSING-REG",
    "LG-PARSE-CHANGED",
    "LG-FROZEN-PIN",
    "LG-FROZEN-MEASURED",
    "LG-SEAT-UNCARRIED",
    "LG-OPEN-ADMITTED",
)


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
    """Blob bytes at REV:path, or None if absent."""
    proc = subprocess.run(
        ["git", "-C", root, "cat-file", "blob", "%s:%s" % (rev, path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout


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


def parse_script(root, tree, path, snapdir, rev):
    """Parse one script path at REV. Return detail on failure, else None."""
    content = blob_at_path(root, rev, path)
    if content is None:
        return "blob unreadable at %s" % rev
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
    """Raw lines under `## Seat-reported failures` until the next heading."""
    inside = False
    out = []
    for line in lesson_lines(lesson_text):
        if FAILURES_HEADING_RE.match(line.strip()):
            inside = True
            continue
        if inside and HEADING_RE.match(line.strip()):
            break
        if inside:
            out.append(line)
    return out


def check_carry(root, tree, rev, round_no):
    """Return (findings, n_markers, n_reports)."""
    prefix = ".ufo/waves/round-%d/" % round_no
    reports = sorted(
        p for p in tree if p.startswith(prefix) and p.endswith(".md")
    )
    if not reports:
        raise EvalError("no .md reports under %s at %s" % (prefix, rev))

    lesson_path = "corpus/lessons/round-%d.md" % round_no
    lesson = None
    if lesson_path in tree:
        lesson = blob_by_oid(root, tree[lesson_path]).decode("utf-8", "replace")

    carry_lines = []
    lesson_admitted = False
    if lesson is not None:
        carry_lines = failures_section_lines(lesson)
        lesson_admitted = bool(ADMITTED_TRUE_RE.search(lesson))

    findings = []
    n_markers = 0
    carried_open = []
    for report_path in reports:
        text = blob_by_oid(root, tree[report_path]).decode("utf-8", "replace")
        for lineno, raw in seat_failure_lines(text):
            n_markers += 1
            needle = norm_line(raw)
            carried = None
            for lline in carry_lines:
                nl = norm_line(lline)
                if needle and needle in nl and CARRY_TOKEN_RE.search(nl):
                    carried = nl
                    break
            detail = "line %d: %s" % (lineno, needle[:220])
            if carried is None:
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
    return findings, n_markers, len(reports)


# ---------------------------------------------------------------------------
# Frozen pins (LG-FROZEN-PIN / LG-FROZEN-MEASURED)
# ---------------------------------------------------------------------------


def _pin_repo_path(frozen_dir, key):
    """Repo path a pin key addresses, per the pinned prefix rule."""
    if any(key.startswith(p) for p in ROOT_PREFIXES):
        return key
    return "%s/%s" % (frozen_dir, key)


def check_frozen_pins(root, tree, rev):
    """Return (findings, n_pin_checks)."""
    findings = []
    n_checks = 0
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
            findings.append(
                ("LG-FROZEN-PIN", exp_path, "expected.json unreadable: %s" % exc)
            )
            continue
        files = expected.get("files") or {}
        record = {}
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
                # A dangling measured_commit contributes no checks: verify it
                # resolves before comparing pinned digests against it.
                verify = subprocess.run(
                    ["git", "-C", root, "rev-parse", "--verify", "--quiet",
                     measured + "^{commit}"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                )
                measured_ok = verify.returncode == 0
            else:
                measured_ok = False
            if measured_ok:
                for key, pinned in sorted(files.items()):
                    n_checks += 1
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
    return findings, n_checks


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


def evaluate(root, rev, round_no, base=None):
    """Return dict {exit, findings, counts, error}.

    exit: 0 (no findings), 1 (findings), 2 (could-not-evaluate)."""
    result = {
        "exit": 2,
        "findings": [],
        "checked_reg": 0,
        "checked_pins": 0,
        "checked_markers": 0,
        "checked_reports": 0,
        "error": None,
    }
    snapdir = tempfile.mkdtemp(prefix="souji-landing-gate-", dir="/var/tmp")
    try:
        resolved = resolve_commit(root, rev)
        result["resolved_rev"] = resolved
        if base is not None:
            result["resolved_base"] = resolve_commit(root, base)
        tree = list_tree(root, resolved)

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
            detail = parse_script(root, tree, path, snapdir, resolved)
            if detail:
                findings.append(("LG-PARSE-REG", path, detail))

        # LG-PARSE-CHANGED: scripts added/modified in BASE..REV.
        if base is not None:
            changed_out = _git(
                root,
                ["diff", "--name-only", "--diff-filter=AM", base, resolved],
                binary=False,
            )
            for path in sorted(set(changed_out.split())):
                if not SCRIPT_EXT_RE.search(path):
                    continue
                result["checked_reg"] += 1
                detail = parse_script(root, tree, path, snapdir, resolved)
                if detail:
                    findings.append(("LG-PARSE-CHANGED", path, detail))

        # LG-FROZEN-PIN / LG-FROZEN-MEASURED.
        pin_findings, n_pins = check_frozen_pins(root, tree, resolved)
        findings.extend(pin_findings)
        result["checked_pins"] = n_pins

        # LG-SEAT-UNCARRIED / LG-OPEN-ADMITTED.
        carry_findings, n_markers, n_reports = check_carry(
            root, tree, resolved, round_no
        )
        findings.extend(carry_findings)
        result["checked_markers"] = n_markers
        result["checked_reports"] = n_reports

        findings.sort(key=lambda f: (f[0], f[1], f[2]))
        result["findings"] = [
            {"id": i, "path": p, "detail": d} for i, p, d in findings
        ]
        result["exit"] = 1 if findings else 0
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
        "SUMMARY\tfindings=%d\tchecked_reg=%d\tchecked_pins=%d\tchecked_markers=%d\tchecked_reports=%d"
        % (
            len(result["findings"]),
            result["checked_reg"],
            result["checked_pins"],
            result["checked_markers"],
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
                "checked_pins": result["checked_pins"],
                "checked_markers": result["checked_markers"],
                "checked_reports": result["checked_reports"],
            },
            "resolved_rev": result.get("resolved_rev"),
            "resolved_base": result.get("resolved_base"),
            "error": result["error"],
        }
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
    env = dict(os.environ)
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
    }
    return files


def _frozen_world(files, record_extra=None):
    """Add a r9-frozen pin set whose pins match the committed bytes."""
    pin_paths = {
        "data.txt": "tests/fixtures/r9-frozen/data.txt",
        "tools/good.sh": "tools/good.sh",
    }
    for key, repo_path in pin_paths.items():
        if repo_path not in files:
            files[repo_path] = "payload for %s\n" % repo_path
    record = {"measured_commit": "0" * 40}
    if record_extra:
        record.update(record_extra)
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


def run_selftest():
    top = tempfile.mkdtemp(prefix="souji-landing-gate-selftest-", dir="/var/tmp")
    cases = []  # (name, fn)
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

    def check(case_name, repo, expect_exit, expect_ids=(), rev="HEAD", base=None, forbid_ids=()):
        nonlocal passed, failed
        res = evaluate(repo, rev, 16, base=base)
        ids = sorted({f["id"] for f in res["findings"]})
        ok = res["exit"] == expect_exit and all(i in ids for i in expect_ids)
        ok = ok and not any(i in ids for i in forbid_ids)
        detail = "exit=%d ids=%s err=%s" % (res["exit"], ids, res["error"])
        if ok:
            passed += 1
            status = "pass"
        else:
            failed += 1
            status = "FAIL"
        print("CASE\t%s\t%s\t%s" % (status, case_name, detail))

    try:
        # CASE clean-pass: everything parses, pins match, STATUS benign.
        repo, g, (rev,) = build("clean-pass", _frozen_world(_base_files()))
        check("clean-pass", repo, 0, rev=rev)

        # CASE nonparsing-cited-sh.
        f = _frozen_world(_base_files())
        f["tools/good.sh"] = BAD_SH
        repo, g, (rev,) = build("bad-cited-sh", f)
        check("nonparsing-cited-sh", repo, 1, ("LG-PARSE-REG",), rev=rev)

        # CASE nonparsing-cited-py.
        f = _frozen_world(_base_files())
        f["tools/good.py"] = BAD_PY
        repo, g, (rev,) = build("bad-cited-py", f)
        check("nonparsing-cited-py", repo, 1, ("LG-PARSE-REG",), rev=rev)

        # CASE missing-cited-path.
        f = _frozen_world(_base_files())
        f["SKILL.md"] = f["SKILL.md"] + "| gone | `bash tools/gone.sh --x` | row |\n"
        repo, g, (rev,) = build("missing-cited", f)
        check("missing-cited-path", repo, 1, ("LG-MISSING-REG",), rev=rev)

        # CASE changed-nonparsing-with-base: base parses, rev breaks.
        repo, g, commits = build(
            "changed-bad",
            _frozen_world(_base_files()),
            extra_commits=({"tools/good.sh": BAD_SH},),
        )
        check(
            "changed-nonparsing-with-base",
            repo,
            1,
            ("LG-PARSE-CHANGED", "LG-PARSE-REG"),
            rev=commits[1],
            base=commits[0],
        )

        # CASE uncited-nonparsing-passes-without-base.
        repo, g, (rev,) = build("uncited-bad", _frozen_world(_base_files()))
        res = evaluate(repo, rev, 16)
        ok = res["exit"] == 0 and not res["findings"]
        if ok:
            passed += 1
            print("CASE\tpass\tuncited-nonparsing-not-flagged\texit=%d" % res["exit"])
        else:
            failed += 1
            print(
                "CASE\tFAIL\tuncited-nonparsing-not-flagged\texit=%d findings=%s"
                % (res["exit"], res["findings"])
            )

        # CASE pin-mismatch.
        f = _frozen_world(_base_files())
        exp = json.loads(f["tests/fixtures/r9-frozen/expected.json"])
        exp["files"]["tools/good.sh"] = "0" * 64
        f["tests/fixtures/r9-frozen/expected.json"] = json.dumps(exp)
        repo, g, (rev,) = build("pin-mismatch", f)
        check("pin-mismatch", repo, 1, ("LG-FROZEN-PIN",), rev=rev)

        # CASE pin-missing-file: key addresses absent path.
        f = _frozen_world(_base_files())
        exp = json.loads(f["tests/fixtures/r9-frozen/expected.json"])
        exp["files"]["ghost.txt"] = "0" * 64  # resolves inside frozen dir, absent
        f["tests/fixtures/r9-frozen/expected.json"] = json.dumps(exp)
        repo, g, (rev,) = build("pin-missing", f)
        check("pin-missing-file", repo, 1, ("LG-FROZEN-PIN",), rev=rev)

        # CASE record-sha256-mismatch.
        f = _frozen_world(_base_files())
        exp = json.loads(f["tests/fixtures/r9-frozen/expected.json"])
        exp["record_sha256"] = "0" * 64
        f["tests/fixtures/r9-frozen/expected.json"] = json.dumps(exp)
        repo, g, (rev,) = build("record-mismatch", f)
        check("record-sha256-mismatch", repo, 1, ("LG-FROZEN-PIN",), rev=rev)

        # CASE frozen-measured: pin disagrees with measured_commit blob.
        f = _base_files()
        f["tests/fixtures/r9-frozen/data.txt"] = "v2 bytes\n"
        f["tools/good.sh"] = GOOD_SH
        # measured_commit must be a real commit: build two-commit repo.
        repo = os.path.join(top, "frozen-measured")
        g = _mkrepo(repo)
        _write_file(repo, "tools/good.sh", "old-good-bytes\n")
        old_rev = _commit_all(g, repo, "old")
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
        check("frozen-measured", repo, 1, ("LG-FROZEN-MEASURED",), rev=rev)

        # CASE uncarried-marker: STATUS failure + phrase, lesson lacks them.
        f = _frozen_world(_base_files())
        f[".ufo/waves/round-16/w1/SeatA.md"] = (
            "# SeatA\n\n## STATUS: INCOMPLETE — file has an unresolved syntax error\n"
        )
        repo, g, (rev,) = build("uncarried", f)
        check("uncarried-marker", repo, 1, ("LG-SEAT-UNCARRIED",), rev=rev)

        # CASE carried-open: failure carried under the heading with `open`.
        f = _frozen_world(_base_files())
        marker = "## STATUS: INCOMPLETE — file has an unresolved syntax error"
        f[".ufo/waves/round-16/w1/SeatA.md"] = "# SeatA\n\n%s\n" % marker
        f["corpus/lessons/round-16.md"] = (
            "# Round 16\n\n## Seat-reported failures\n\n"
            "- SeatA `.ufo/waves/round-16/w1/SeatA.md:3` %s — open\n" % marker
        )
        repo, g, (rev,) = build("carried-open", f)
        check("carried-open", repo, 0, rev=rev)

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
        check("carried-resolved", repo, 0, rev=rev)

        # CASE open-admitted: carried open + admitted: true → LG-OPEN-ADMITTED.
        f = _frozen_world(_base_files())
        marker = "## STATUS: BROKEN — gate still red"
        f[".ufo/waves/round-16/w1/SeatA.md"] = "# SeatA\n\n%s\n" % marker
        f["corpus/lessons/round-16.md"] = (
            "# Round 16\n\nadmitted: true\n\n## Seat-reported failures\n\n"
            "- SeatA `.ufo/waves/round-16/w1/SeatA.md:3` %s — open\n" % marker
        )
        repo, g, (rev,) = build("open-admitted", f)
        check("open-admitted", repo, 1, ("LG-OPEN-ADMITTED",), rev=rev)

        # CASE missing-wave-dir → exit 2.
        f = _frozen_world(_base_files())
        del f[".ufo/waves/round-16/w1/SeatA.md"]
        repo, g, (rev,) = build("no-wave-dir", f)
        check("no-wave-dir-exit2", repo, 2, rev=rev)

        # CASE fenced-and-table phrases ignored; benign STATUS words pass.
        f = _frozen_world(_base_files())
        f[".ufo/waves/round-16/w1/SeatA.md"] = (
            "# SeatA\n\nSTATUS: none\n\n```\nsyntax error inside a fenced block\n```\n"
            "| note | snapshot_tampered quoted in a table |\n"
            "STATUS — done\n"
        )
        repo, g, (rev,) = build("fenced-table-ignored", f)
        check("fenced-and-table-ignored", repo, 0, rev=rev)

        # CASE bad-rev → exit 2.
        repo, g, (rev,) = build("badrev", _frozen_world(_base_files()))
        res = evaluate(repo, "0" * 40, 16)
        if res["exit"] == 2:
            passed += 1
            print("CASE\tpass\tbad-rev-exit2\texit=2")
        else:
            failed += 1
            print("CASE\tFAIL\tbad-rev-exit2\texit=%d" % res["exit"])

        # CASE no-skill → exit 2.
        f = _frozen_world(_base_files())
        del f["SKILL.md"]
        repo = os.path.join(top, "no-skill")
        g = _mkrepo(repo)
        for rel, content in f.items():
            _write_file(repo, rel, content)
        g("add", "-A")
        g("commit", "-q", "-m", "x")
        res = evaluate(repo, "HEAD", 16)
        if res["exit"] == 2:
            passed += 1
            print("CASE\tpass\tno-skill-exit2\texit=2")
        else:
            failed += 1
            print("CASE\tFAIL\tno-skill-exit2\texit=%d" % res["exit"])
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
        description="Round-16 landing-claim consistency gate (souji C2).",
    )
    ap.add_argument("--root", help="lane repository path")
    ap.add_argument("--rev", help="revision whose committed bytes are checked")
    ap.add_argument("--round", type=int, dest="round_no", help="round number N")
    ap.add_argument("--base", help="optional base revision for changed-script checks")
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
    result = evaluate(args.root, args.rev, args.round_no, base=args.base)
    return emit(result, json_out=args.json_out)


if __name__ == "__main__":
    sys.exit(main())
