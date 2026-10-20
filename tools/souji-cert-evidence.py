#!/usr/bin/env python3
"""souji-cert-evidence.py — executable evidence-consistency gate (r13 / C1).

Purpose
-------
Replace trust in a shared certification relay with a boring, executable
validator over per-author evidence fragments. It checks *internal consistency
and artifact-byte digests*, nothing else. It does not execute the recorded
commands and does not certify that any tool is safe. Certification stays OFF.

CLI
---
    souji-cert-evidence.py --root PATH --manifest PATH
    souji-cert-evidence.py --frozen DIR
    souji-cert-evidence.py --selftest

Exit codes (stable)
-------------------
    0  clean               every fragment is schema-valid, every declared
                           artifact digest matches, evidence paths exist, and
                           every verdict is pass with exit_code 0.
    1  failed              the evidence is well formed and at least one
                           fragment honestly reports a failure (verdict=fail
                           with a nonzero exit_code). This is a valid
                           certification *failure*, not a defective input.
    2  could-not-evaluate  the evidence cannot be trusted: malformed input,
                           duplicate/shared ownership, unsafe paths, absent
                           evidence, digest mismatch, inconsistent verdict, or
                           a tampered frozen snapshot. Nothing is certified.

Argparse usage errors also exit 2 (before any finding is emitted).

Manifest schema (JSON object)
-----------------------------
    {
      "fragments": ["fragments/a.json", "fragments/b.json"]
    }

`fragments` is required, non-empty, and each entry is a unique relative JSON
path under --root. Paths use `/`, must be relative, must not contain `..`, and
must resolve through non-symlink components to a regular file. Unknown
top-level keys are tolerated. Duplicate object keys are rejected.

Fragment schema (JSON object), every key required
-------------------------------------------------
    author      non-empty string, unique across the manifest
    class       non-empty string naming the defect/test class this fragment
                measures (a label only; the gate does not verify identity or
                that the command ran)
    artifact    relative path under --root of the bytes measured (the gate
                cannot prove this path is the installed tool location)
    sha256      64 lowercase hex characters; must equal the artifact digest
    command     non-empty string, recorded verbatim (never executed)
    exit_code   integer (bool rejected); compared only against zero
    verdict     "pass" or "fail"
    evidence    relative path under --root of the evidence file
    evidence_sha256  64 lowercase hex characters; must equal the evidence
                digest, so an overwritten evidence file is rejected
    (extra keys are tolerated; `artifact` and `evidence` must differ)

The `author` and `class` values are self-declared labels. A duplicate author
label is rejected so one person/seat cannot silently stand in for another's
measurement, but the gate cannot and does not establish unique real human or
model identity, nor that the recorded command was actually executed. Class
labels are not a coverage proof: untested classes remain unknown, and a clean
result never means zero unknown classes.

All fragment/artifact/evidence paths are resolved against --root, not against
the fragment file's directory. Paths are opened with O_NOFOLLOW/O_NONBLOCK and
fstat-verified as regular files; FIFOs, sockets, devices, directories and
symlink components are rejected without reading.

Finding ids (stable; emitted as `finding <id>: <detail>`)
---------------------------------------------------------
level 2 (could-not-evaluate):
    root-not-directory, manifest-unreadable, manifest-malformed,
    manifest-schema, manifest-empty, fragment-duplicate, fragment-missing,
    fragment-unreadable, fragment-not-regular, fragment-malformed,
    fragment-schema, author-duplicate, fragment-shared, claim-shared,
    path-absolute, path-escape, path-invalid, path-symlink, path-protected,
    path-hardlink,
    artifact-missing, artifact-not-regular, artifact-unreadable,
    artifact-digest-mismatch, artifact-candidate, evidence-missing,
    evidence-not-regular, evidence-unreadable, evidence-digest-mismatch,
    verdict-false-pass, verdict-false-fail,
    frozen-unreadable, frozen-malformed, frozen-schema, frozen-incomplete,
    snapshot_tampered, snapshot-verdict-mismatch, selftest-unavailable
level 1 (failed):
    fragment-reported-fail

`verdict-false-pass` is a pass with a nonzero exit_code (false success).
`verdict-false-fail` is a fail with exit_code 0 (a failure claim unsupported by
the recorded run). Both make the evidence untrustworthy, hence exit 2.
`fragment-shared` is two fragments claiming the same artifact or evidence path;
`author-duplicate` is two fragments with the same author; `fragment-duplicate` is
the same fragment path listed twice. Each is rejected so no fragment can stand
in for another author's measurement. `path-hardlink` rejects any claimed file
with more than one link: an alias outside --root can change the measured bytes.
`artifact-candidate` rejects an artifact basename that starts with `cand-`: a
candidate selection is not an installed-tool claim. Other non-cand candidate
files (for example `.impl-*`) are not detected; the gate has no installed-tool
allowlist and --root is caller-chosen. The caller-chosen --root and the explicit
manifest define the measured set, and a clean result still grants no
certification.

Frozen snapshot mode
--------------------
    --frozen DIR

DIR is a committed snapshot of inputs plus `expected.json`:

    {
      "manifest": "manifest.json",
      "verdict": "clean",                     # clean | failed | could-not-evaluate
      "files": {
        "manifest.json": "<sha256>",
        "fragments/a.json": "<sha256>",
        "installed/tool.sh": "<sha256>",
        "evidence/a.txt": "<sha256>"
      }
    }

`--frozen` first verifies the sha256 of every listed file, treating absent,
symlinked, non-regular, unreadable, or mismatched bytes as `snapshot_tampered`
(exit 2). It then requires every snapshot input reachable from the manifest
(the manifest, each listed fragment, and each fragment's artifact and evidence)
to be pinned in `files` (`frozen-incomplete`). Only after that does it run the
normal manifest evaluation, rooted at DIR, and compare the resulting status
with `verdict` (`snapshot-verdict-mismatch`). `expected.json` itself is the
caller-supplied trust anchor: it is not self-authenticated.

--selftest builds every fixture with tempfile.mkdtemp(dir="/var/tmp"), invokes
this CLI as a subprocess for each case, asserts the return code and the exact
finding-id set, copies the committed frozen snapshot to detect a mutated input,
and removes its temp tree. Its final line is `selftest: <passed>/<total>
passed`. It exits 0 only if every case passes, 1 on an assertion failure, 2 if
its committed fixture is unavailable.

Limitations (deliberate)
------------------------
- A co-conspiring author can report a false exit_code whose digest and paths
  all match; this gate checks consistency, not truth.
- The recorded command is never run, by design; exit_code/verdict are compared
  only for zero/nonzero agreement.
- Component symlink checks and open() are not one atomic operation; per-file
  O_NOFOLLOW plus fstat closes the final-component race, not a parent-directory
  swap during evaluation.
- Files with more than one hardlink are refused rather than followed, so a
  legitimate hardlinked install cannot be measured by this gate.
- Protected path patterns are name-based: they prevent reading obvious secret
  and operator paths, but they are not a data-loss-prevention classifier.
- A clean result means the evidence package is well formed and digest-pinned.
  It is not a safety certification of any tool or file.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

EXIT_CLEAN = 0
EXIT_FAILED = 1
EXIT_COULD_NOT_EVALUATE = 2

STATUS_BY_CODE = {
    EXIT_CLEAN: "clean",
    EXIT_FAILED: "failed",
    EXIT_COULD_NOT_EVALUATE: "could-not-evaluate",
}
CODE_BY_VERDICT = {
    "clean": EXIT_CLEAN,
    "failed": EXIT_FAILED,
    "could-not-evaluate": EXIT_COULD_NOT_EVALUATE,
}

FRAGMENT_FIELDS = (
    "author",
    "class",
    "artifact",
    "sha256",
    "command",
    "exit_code",
    "verdict",
    "evidence",
    "evidence_sha256",
)
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
LEVEL1_FINDINGS = frozenset({"fragment-reported-fail"})
MAX_JSON_BYTES = 16 * 1024 * 1024
PROTECTED_NAME_PATTERNS = (
    ".env",
    ".env.*",
    "*.env",
    ".envrc",
    "*credential*",
    "*secret*",
    "id_*",
    "*.pem",
    "*.key",
    "watchdog.log",
)


def _protected_reason(parts):
    """Return why a path component chain must not be read, or None."""
    lowered = [part.lower() for part in parts]
    for part in lowered:
        if part == ".git":
            return "git metadata"
        for pattern in PROTECTED_NAME_PATTERNS:
            if fnmatch.fnmatchcase(part, pattern):
                return "secret-shaped name"
    for index in range(len(lowered) - 1):
        if lowered[index] == "census" and lowered[index + 1].startswith("operator-sweep-"):
            return "operator sweep"
        if lowered[index] == ".ufo" and lowered[index + 1] == "state":
            return "operator runtime state"
    return None


# ---------------------------------------------------------------- findings

def _add(findings, finding_id, detail):
    level = 1 if finding_id in LEVEL1_FINDINGS else 2
    findings.append({"id": finding_id, "level": level, "detail": detail})


def _status_for(findings):
    if any(item["level"] >= 2 for item in findings):
        return EXIT_COULD_NOT_EVALUATE
    if findings:
        return EXIT_FAILED
    return EXIT_CLEAN


# ---------------------------------------------------------------- paths

def _classify_rel(value):
    """Return (normalized relative key, None) or (None, reason)."""
    if not isinstance(value, str) or not value:
        return None, "invalid"
    if value != value.strip():
        return None, "invalid"
    if any(ord(char) < 0x20 or ord(char) == 0x7F for char in value):
        return None, "invalid"
    if PurePosixPath(value).is_absolute():
        return None, "absolute"
    parts = [part for part in value.split("/") if part not in ("", ".")]
    if not parts:
        return None, "invalid"
    if any(part == ".." for part in parts):
        return None, "escape"
    return "/".join(parts), None


def _norm_rel(value):
    key, reason = _classify_rel(value)
    if reason is not None:
        return None
    return key


def _resolve_under(root, rel):
    """Resolve a normalized relative path under root without following links.

    Returns (path, None, key) or (None, reason, key). Every component is
    lstat-checked; a symlink anywhere below root is refused.
    """
    key, reason = _classify_rel(rel)
    if reason is not None:
        return None, reason, None
    current = root
    for part in key.split("/"):
        current = current / part
        try:
            info = os.lstat(current)
        except FileNotFoundError:
            return None, "missing", key
        except PermissionError:
            return None, "unreadable", key
        except (OSError, ValueError):
            return None, "invalid", key
        if stat.S_ISLNK(info.st_mode):
            return None, "symlink", key
    try:
        if os.path.commonpath([str(root), str(current)]) != str(root):
            return None, "escape", key
    except ValueError:
        return None, "escape", key
    return current, None, key


def _read_text_abs(path):
    """Read a regular non-symlink UTF-8 file safely. Returns (text, reason)."""
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        return None, "absent"
    except PermissionError:
        return None, "unreadable"
    except OSError:
        return None, "unreadable"
    if stat.S_ISLNK(info.st_mode):
        return None, "symlink"
    if not stat.S_ISREG(info.st_mode):
        return None, "not-regular"
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    try:
        fd = os.open(path, flags)
    except FileNotFoundError:
        return None, "absent"
    except PermissionError:
        return None, "unreadable"
    except OSError:
        return None, "unreadable"
    chunks = []
    total = 0
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            return None, "not-regular"
        while True:
            block = os.read(fd, 1 << 20)
            if not block:
                break
            total += len(block)
            if total > MAX_JSON_BYTES:
                return None, "too-large"
            chunks.append(block)
    except OSError:
        return None, "unreadable"
    finally:
        os.close(fd)
    try:
        return b"".join(chunks).decode("utf-8"), None
    except UnicodeDecodeError:
        return None, "invalid-utf8"


def _digest_regular(path):
    """sha256 of a regular file opened without following the final symlink."""
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    try:
        fd = os.open(path, flags)
    except FileNotFoundError:
        return None, "missing"
    except PermissionError:
        return None, "unreadable"
    except OSError:
        return None, "unreadable"
    digest = hashlib.sha256()
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            return None, "not-regular"
        while True:
            block = os.read(fd, 1 << 20)
            if not block:
                break
            digest.update(block)
    except OSError:
        return None, "unreadable"
    finally:
        os.close(fd)
    return digest.hexdigest(), None


# ---------------------------------------------------------------- JSON

class _DuplicateKey(ValueError):
    pass


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey(key)
        result[key] = value
    return result


def _load_json(text):
    return json.loads(text, object_pairs_hook=_reject_duplicate_keys)


def _json_or_error(text):
    try:
        return _load_json(text), None
    except _DuplicateKey as exc:
        return None, "duplicate object key %r" % (str(exc),)
    except json.JSONDecodeError as exc:
        return None, "invalid JSON: line %d column %d: %s" % (
            exc.lineno,
            exc.colno,
            exc.msg,
        )
    except ValueError as exc:
        return None, "invalid JSON: %s" % (exc,)


# ---------------------------------------------------------------- validate

def _validate_fragment(obj):
    """Return a list of schema errors for one fragment object."""
    if not isinstance(obj, dict):
        return ["fragment is not a JSON object"]
    errors = []
    missing = [key for key in FRAGMENT_FIELDS if key not in obj]
    if missing:
        return ["missing required key(s): %s" % ", ".join(missing)]
    author = obj["author"]
    if not isinstance(author, str) or not author or author != author.strip():
        errors.append("author must be a non-empty trimmed string")
    tested_class = obj["class"]
    if not isinstance(tested_class, str) or not tested_class or tested_class != tested_class.strip():
        errors.append("class must be a non-empty trimmed string")
    for key in ("artifact", "evidence"):
        value = obj[key]
        if not isinstance(value, str) or not value or value != value.strip():
            errors.append("%s must be a non-empty trimmed string" % key)
    sha = obj["sha256"]
    if not isinstance(sha, str) or SHA256_RE.fullmatch(sha) is None:
        errors.append("sha256 must be 64 lowercase hex characters")
    evidence_sha = obj["evidence_sha256"]
    if not isinstance(evidence_sha, str) or SHA256_RE.fullmatch(evidence_sha) is None:
        errors.append("evidence_sha256 must be 64 lowercase hex characters")
    command = obj["command"]
    if not isinstance(command, str) or not command.strip():
        errors.append("command must be a non-empty string")
    exit_code = obj["exit_code"]
    if isinstance(exit_code, bool) or not isinstance(exit_code, int):
        errors.append("exit_code must be an integer")
    verdict = obj["verdict"]
    if verdict not in ("pass", "fail"):
        errors.append('verdict must be "pass" or "fail"')
    return errors


def _check_claim(root, rel, label, findings, frag_label):
    """Resolve one artifact/evidence claim; return (path, key)."""
    key, reason = _classify_rel(rel)
    if reason == "absolute":
        _add(findings, "path-absolute", "%s %s=%r is absolute" % (frag_label, label, rel))
        return None, None
    if reason == "escape":
        _add(findings, "path-escape", "%s %s=%r escapes --root" % (frag_label, label, rel))
        return None, None
    if reason == "invalid":
        _add(findings, "path-invalid", "%s %s=%r is not a usable relative path" % (frag_label, label, rel))
        return None, None
    protected = _protected_reason(key.split("/"))
    if protected is not None:
        _add(findings, "path-protected", "%s %s=%s is protected (%s)" % (frag_label, label, key, protected))
        return None, key
    path, resolve_reason, resolved_key = _resolve_under(root, key)
    if resolve_reason == "missing":
        _add(findings, "%s-missing" % label, "%s %s=%s" % (frag_label, label, key))
        return None, resolved_key
    if resolve_reason == "symlink":
        _add(findings, "path-symlink", "%s %s=%s traverses a symlink" % (frag_label, label, key))
        return None, resolved_key
    if resolve_reason == "unreadable":
        _add(findings, "%s-unreadable" % label, "%s %s=%s" % (frag_label, label, key))
        return None, resolved_key
    if resolve_reason in ("escape", "invalid", "absolute"):
        _add(findings, "path-%s" % resolve_reason, "%s %s=%s" % (frag_label, label, key))
        return None, resolved_key
    try:
        info = os.lstat(path)
    except OSError:
        _add(findings, "%s-unreadable" % label, "%s %s=%s" % (frag_label, label, key))
        return None, resolved_key
    if not stat.S_ISREG(info.st_mode):
        _add(findings, "%s-not-regular" % label, "%s %s=%s" % (frag_label, label, key))
        return None, resolved_key
    if info.st_nlink != 1:
        _add(
            findings,
            "path-hardlink",
            "%s %s=%s has %d links (alias can change measured bytes)"
            % (frag_label, label, key, info.st_nlink),
        )
        return None, resolved_key
    return path, resolved_key


# ---------------------------------------------------------------- normal

def evaluate(root, manifest_path):
    """Evaluate one manifest rooted at root. Returns (findings, counts)."""
    findings = []
    counts = {"fragments": 0, "assessed": 0, "pass": 0, "fail": 0}

    protected_manifest = _protected_reason(Path(str(manifest_path)).parts)
    if protected_manifest is not None:
        _add(
            findings,
            "path-protected",
            "manifest=%r is protected (%s)" % (str(manifest_path), protected_manifest),
        )
        return findings, counts

    text, read_reason = _read_text_abs(manifest_path)
    if read_reason is not None:
        if read_reason in ("invalid-utf8", "too-large"):
            _add(findings, "manifest-malformed", "manifest=%r: %s" % (str(manifest_path), read_reason))
        else:
            _add(findings, "manifest-unreadable", "manifest=%r: %s" % (str(manifest_path), read_reason))
        return findings, counts

    manifest, json_error = _json_or_error(text)
    if json_error is not None:
        _add(findings, "manifest-malformed", "manifest=%r: %s" % (str(manifest_path), json_error))
        return findings, counts
    if not isinstance(manifest, dict):
        _add(findings, "manifest-schema", "manifest is not a JSON object")
        return findings, counts

    fragments = manifest.get("fragments")
    if not isinstance(fragments, list):
        _add(findings, "manifest-schema", '"fragments" must be an array')
        return findings, counts
    counts["fragments"] = len(fragments)
    if not fragments:
        _add(findings, "manifest-empty", "no fragments: nothing to certify")
        return findings, counts

    seen_fragments = {}
    authors = {}
    artifacts = {}
    evidences = {}

    for index, rel in enumerate(fragments):
        frag_label = "fragments[%d]" % index
        if not isinstance(rel, str):
            _add(findings, "manifest-schema", "%s is not a string" % frag_label)
            continue
        key, reason = _classify_rel(rel)
        if reason is not None:
            _add(
                findings,
                "manifest-schema",
                "%s path=%r is %s (not a unique contained relative path)"
                % (frag_label, rel, reason),
            )
            continue
        if key in seen_fragments:
            _add(
                findings,
                "fragment-duplicate",
                "%s path=%s already listed at fragments[%d]"
                % (frag_label, key, seen_fragments[key]),
            )
            continue
        seen_fragments[key] = index

        protected = _protected_reason(key.split("/"))
        if protected is not None:
            _add(
                findings,
                "path-protected",
                "%s path=%s is protected (%s)" % (frag_label, key, protected),
            )
            continue

        path, resolve_reason, _ = _resolve_under(root, key)
        if resolve_reason is not None:
            if resolve_reason == "missing":
                _add(findings, "fragment-missing", "%s path=%s" % (frag_label, key))
            elif resolve_reason == "symlink":
                _add(findings, "path-symlink", "%s path=%s traverses a symlink" % (frag_label, key))
            elif resolve_reason == "escape":
                _add(findings, "path-escape", "%s path=%s escapes --root" % (frag_label, key))
            elif resolve_reason == "not-regular":
                _add(findings, "fragment-not-regular", "%s path=%s" % (frag_label, key))
            else:
                _add(findings, "fragment-unreadable", "%s path=%s: %s" % (frag_label, key, resolve_reason))
            continue
        try:
            info = os.lstat(path)
        except OSError:
            _add(findings, "fragment-unreadable", "%s path=%s" % (frag_label, key))
            continue
        if not stat.S_ISREG(info.st_mode):
            _add(findings, "fragment-not-regular", "%s path=%s" % (frag_label, key))
            continue
        if info.st_nlink != 1:
            _add(
                findings,
                "path-hardlink",
                "%s path=%s has %d links (alias can change fragment bytes)"
                % (frag_label, key, info.st_nlink),
            )
            continue

        frag_text, frag_reason = _read_text_abs(path)
        if frag_reason is not None:
            if frag_reason in ("invalid-utf8", "too-large"):
                _add(findings, "fragment-malformed", "%s path=%s: %s" % (frag_label, key, frag_reason))
            else:
                _add(findings, "fragment-unreadable", "%s path=%s: %s" % (frag_label, key, frag_reason))
            continue
        fragment, frag_json_error = _json_or_error(frag_text)
        if frag_json_error is not None:
            _add(findings, "fragment-malformed", "%s path=%s: %s" % (frag_label, key, frag_json_error))
            continue
        schema_errors = _validate_fragment(fragment)
        if schema_errors:
            _add(
                findings,
                "fragment-schema",
                "%s path=%s: %s" % (frag_label, key, "; ".join(schema_errors)),
            )
            continue

        counts["assessed"] += 1
        findings_before = len(findings)
        author = fragment["author"]
        if author in authors:
            _add(
                findings,
                "author-duplicate",
                "author=%r at %s path=%s already used by %s"
                % (author, frag_label, key, authors[author]),
            )
        else:
            authors[author] = "%s path=%s" % (frag_label, key)

        artifact_key = _norm_rel(fragment["artifact"])
        evidence_key = _norm_rel(fragment["evidence"])
        if artifact_key is not None and artifact_key == evidence_key:
            _add(
                findings,
                "claim-shared",
                "%s path=%s artifact and evidence are the same path %s"
                % (frag_label, key, artifact_key),
            )
        for label, claim_key, table in (
            ("artifact", artifact_key, artifacts),
            ("evidence", evidence_key, evidences),
        ):
            if claim_key is None:
                continue
            if claim_key in table:
                _add(
                    findings,
                    "fragment-shared",
                    "%s %s=%s claimed by %s and %s path=%s"
                    % (label, label, claim_key, table[claim_key], frag_label, key),
                )
            else:
                table[claim_key] = "%s path=%s" % (frag_label, key)

        artifact_path, artifact_actual_key = _check_claim(
            root, fragment["artifact"], "artifact", findings, frag_label
        )
        if artifact_actual_key is not None and PurePosixPath(artifact_actual_key).name.startswith("cand-"):
            _add(
                findings,
                "artifact-candidate",
                "%s artifact=%s is a candidate file, not an installed-tool claim"
                % (frag_label, artifact_actual_key),
            )
        if artifact_path is not None:
            actual, digest_reason = _digest_regular(artifact_path)
            if digest_reason is not None:
                _add(
                    findings,
                    "artifact-%s" % digest_reason,
                    "%s artifact=%s" % (frag_label, fragment["artifact"]),
                )
            elif actual != fragment["sha256"]:
                _add(
                    findings,
                    "artifact-digest-mismatch",
                    "%s artifact=%s declared=%s measured=%s"
                    % (frag_label, fragment["artifact"], fragment["sha256"], actual),
                )

        evidence_path, evidence_actual_key = _check_claim(
            root, fragment["evidence"], "evidence", findings, frag_label
        )
        if evidence_path is not None:
            actual, digest_reason = _digest_regular(evidence_path)
            if digest_reason is not None:
                _add(
                    findings,
                    "evidence-%s" % digest_reason,
                    "%s evidence=%s" % (frag_label, fragment["evidence"]),
                )
            elif actual != fragment["evidence_sha256"]:
                _add(
                    findings,
                    "evidence-digest-mismatch",
                    "%s evidence=%s declared=%s actual=%s"
                    % (
                        frag_label,
                        fragment["evidence"],
                        fragment["evidence_sha256"],
                        actual,
                    ),
                )

        verdict = fragment["verdict"]
        exit_code = fragment["exit_code"]
        if verdict == "pass" and exit_code != 0:
            _add(
                findings,
                "verdict-false-pass",
                "%s author=%r verdict=pass exit_code=%d"
                % (frag_label, author, exit_code),
            )
        elif verdict == "fail" and exit_code == 0:
            _add(
                findings,
                "verdict-false-fail",
                "%s author=%r verdict=fail exit_code=0"
                % (frag_label, author),
            )
        elif verdict == "pass":
            if len(findings) == findings_before:
                counts["pass"] += 1
        else:
            counts["fail"] += 1
            _add(
                findings,
                "fragment-reported-fail",
                "%s author=%r verdict=fail exit_code=%d"
                % (frag_label, author, exit_code),
            )

    return findings, counts


# ---------------------------------------------------------------- frozen

def _frozen_required_inputs(root, manifest_key):
    """Snapshot inputs reachable from the manifest: manifest, fragments, data."""
    required = {manifest_key}
    if _protected_reason(manifest_key.split("/")) is not None:
        return required
    path, reason, _ = _resolve_under(root, manifest_key)
    if reason is not None:
        return required
    text, read_reason = _read_text_abs(path)
    if read_reason is not None:
        return required
    manifest, json_error = _json_or_error(text)
    if json_error is not None or not isinstance(manifest, dict):
        return required
    fragments = manifest.get("fragments")
    if not isinstance(fragments, list):
        return required
    for rel in fragments:
        key = _norm_rel(rel) if isinstance(rel, str) else None
        if key is None:
            continue
        required.add(key)
        if _protected_reason(key.split("/")) is not None:
            continue
        frag_path, frag_reason, _ = _resolve_under(root, key)
        if frag_reason is not None:
            continue
        frag_text, frag_read_reason = _read_text_abs(frag_path)
        if frag_read_reason is not None:
            continue
        fragment, frag_json_error = _json_or_error(frag_text)
        if frag_json_error is not None or not isinstance(fragment, dict):
            continue
        for label in ("artifact", "evidence"):
            claim = fragment.get(label)
            claim_key = _norm_rel(claim) if isinstance(claim, str) else None
            if claim_key is not None:
                required.add(claim_key)
    return required


def _frozen_findings(dir_path):
    """Verify expected.json pins. Returns (findings, pinned hash count, manifest key)."""
    findings = []
    pinned = 0
    expected_path = dir_path / "expected.json"
    text, read_reason = _read_text_abs(expected_path)
    if read_reason is not None:
        if read_reason in ("invalid-utf8", "too-large"):
            _add(findings, "frozen-malformed", "expected.json: %s" % read_reason)
        else:
            _add(findings, "frozen-unreadable", "expected.json: %s" % read_reason)
        return findings, pinned, None

    expected, json_error = _json_or_error(text)
    if json_error is not None:
        _add(findings, "frozen-malformed", "expected.json: %s" % json_error)
        return findings, pinned, None
    if not isinstance(expected, dict):
        _add(findings, "frozen-schema", "expected.json is not a JSON object")
        return findings, pinned, None

    schema_errors = []
    manifest_rel = expected.get("manifest")
    manifest_key = _norm_rel(manifest_rel) if isinstance(manifest_rel, str) else None
    if manifest_key is None:
        schema_errors.append('"manifest" must be a contained relative path')
    recorded_verdict = expected.get("verdict")
    if recorded_verdict not in CODE_BY_VERDICT:
        schema_errors.append('"verdict" must be clean, failed, or could-not-evaluate')
    files = expected.get("files")
    if not isinstance(files, dict) or not files:
        schema_errors.append('"files" must be a non-empty object')
        files = {}
    normalized_files = {}
    for rel, declared in files.items():
        key, reason = _classify_rel(rel)
        if reason is not None:
            schema_errors.append("files key %r is %s" % (rel, reason))
            continue
        if not isinstance(declared, str) or SHA256_RE.fullmatch(declared) is None:
            schema_errors.append("files[%r] must be 64 lowercase hex characters" % rel)
            continue
        if key in normalized_files:
            schema_errors.append("files key %r duplicates %r" % (rel, normalized_files[key]))
            continue
        normalized_files[key] = declared
    if schema_errors:
        _add(findings, "frozen-schema", "; ".join(schema_errors))
        return findings, pinned, manifest_key

    if manifest_key is not None:
        protected = _protected_reason(manifest_key.split("/"))
        if protected is not None:
            _add(
                findings,
                "path-protected",
                "frozen manifest=%s is protected (%s)" % (manifest_key, protected),
            )

    for key in sorted(normalized_files):
        declared = normalized_files[key]
        protected = _protected_reason(key.split("/"))
        if protected is not None:
            _add(
                findings,
                "path-protected",
                "frozen file=%s is protected (%s)" % (key, protected),
            )
            continue
        path, reason, _ = _resolve_under(dir_path, key)
        if reason is None:
            try:
                info = os.lstat(path)
            except OSError:
                reason = "unreadable"
            else:
                if not stat.S_ISREG(info.st_mode):
                    reason = "not-regular"
                elif info.st_nlink != 1:
                    reason = "hardlink"
        if reason is not None:
            _add(
                findings,
                "snapshot_tampered",
                "path=%s expected=%s actual=%s" % (key, declared, reason),
            )
            continue
        actual, digest_reason = _digest_regular(path)
        if digest_reason is not None:
            _add(
                findings,
                "snapshot_tampered",
                "path=%s expected=%s actual=%s" % (key, declared, digest_reason),
            )
            continue
        if actual != declared:
            _add(
                findings,
                "snapshot_tampered",
                "path=%s expected=%s actual=%s" % (key, declared, actual),
            )
            continue
        pinned += 1

    return findings, pinned, manifest_key


def evaluate_frozen(dir_arg):
    """Verify a frozen snapshot, then its manifest. Returns (findings, counts, status)."""
    dir_path = Path(dir_arg)
    if not dir_path.is_dir():
        findings = []
        _add(findings, "frozen-unreadable", "frozen directory absent: %r" % dir_arg)
        return findings, {"fragments": 0, "assessed": 0, "pass": 0, "fail": 0, "frozen_files": 0}, _status_for(findings)
    dir_path = Path(os.path.realpath(dir_path))

    findings, pinned, manifest_key = _frozen_findings(dir_path)
    counts = {"fragments": 0, "assessed": 0, "pass": 0, "fail": 0, "frozen_files": pinned}
    if findings:
        return findings, counts, _status_for(findings)
    if manifest_key is None:
        _add(findings, "frozen-schema", "expected.json has no usable manifest path")
        return findings, counts, _status_for(findings)

    expected_text, expected_reason = _read_text_abs(dir_path / "expected.json")
    if expected_reason is not None:
        _add(findings, "frozen-unreadable", "expected.json: %s" % expected_reason)
        return findings, counts, _status_for(findings)
    expected, _ = _json_or_error(expected_text)
    recorded_verdict = expected["verdict"]

    pinned_keys = set()
    listed = expected["files"]
    for rel in listed:
        key = _norm_rel(rel)
        if key is not None:
            pinned_keys.add(key)
    required = _frozen_required_inputs(dir_path, manifest_key)
    for key in sorted(required):
        if key not in pinned_keys:
            _add(
                findings,
                "frozen-incomplete",
                "path=%s is a snapshot input but not pinned in expected.json files"
                % key,
            )
    if findings:
        return findings, counts, _status_for(findings)

    manifest_path = dir_path / manifest_key
    findings, counts = evaluate(dir_path, manifest_path)
    counts["frozen_files"] = pinned
    actual_status = _status_for(findings)
    if actual_status != CODE_BY_VERDICT[recorded_verdict]:
        _add(
            findings,
            "snapshot-verdict-mismatch",
            "expected=%s actual=%s evaluation_findings=%d"
            % (recorded_verdict, STATUS_BY_CODE[actual_status], len(findings)),
        )
        actual_status = _status_for(findings)
    return findings, counts, actual_status


# ---------------------------------------------------------------- output

def _emit(status, findings, counts):
    lines = [
        "souji-cert-evidence: %s" % STATUS_BY_CODE[status],
        "scope: evidence_valid/NOT_CERTIFICATION (declared-fragment consistency/integrity only; not tool safety certification; class coverage and command execution are not established)",
    ]
    for item in sorted(findings, key=lambda item: (item["id"], item["detail"])):
        lines.append("finding %s: %s" % (item["id"], item["detail"]))
    if "frozen_files" in counts:
        lines.append(
            "summary fragments=%d assessed=%d pass=%d fail=%d findings=%d frozen_files=%d"
            % (
                counts["fragments"],
                counts["assessed"],
                counts["pass"],
                counts["fail"],
                len(findings),
                counts["frozen_files"],
            )
        )
    else:
        lines.append(
            "summary fragments=%d assessed=%d pass=%d fail=%d findings=%d"
            % (
                counts["fragments"],
                counts["assessed"],
                counts["pass"],
                counts["fail"],
                len(findings),
            )
        )
    print("\n".join(lines))


# ---------------------------------------------------------------- selftest

def _selftest_env():
    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "LC_ALL": "C",
        "TMPDIR": "/var/tmp",
        "PYTHONDONTWRITEBYTECODE": "1",
    }


def _invoke(tool, *, root=None, manifest=None, frozen=None):
    command = [sys.executable, str(tool)]
    if frozen is not None:
        command.extend(["--frozen", str(frozen)])
    else:
        command.extend(["--root", str(root), "--manifest", str(manifest)])
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120,
            env=_selftest_env(),
        )
    except subprocess.TimeoutExpired:
        return None, "", "TIMEOUT"
    return result.returncode, result.stdout, result.stderr


def _finding_ids(stdout):
    return [
        match.group(1)
        for match in re.finditer(r"(?m)^finding ([a-z0-9-]+): ", stdout)
    ]


def _reported_status(stdout):
    match = re.search(r"(?m)^souji-cert-evidence: ([a-z-]+)$", stdout)
    return match.group(1) if match else None


def _record(results, name, rc, stdout, stderr, want_rc, want_ids, want_status):
    observed_ids = _finding_ids(stdout)
    observed_status = _reported_status(stdout)
    problems = []
    if rc != want_rc:
        problems.append("rc=%r want %d" % (rc, want_rc))
    if sorted(observed_ids) != sorted(want_ids):
        problems.append(
            "findings=%s want exactly=%s"
            % (",".join(observed_ids) or "-", ",".join(want_ids) or "-")
        )
    if want_status is not None and observed_status != want_status:
        problems.append("status=%r want %r" % (observed_status, want_status))
    if problems:
        results.append(
            {
                "ok": False,
                "name": name,
                "detail": "; ".join(problems),
                "stdout": stdout,
                "stderr": stderr,
            }
        )
    else:
        results.append(
            {
                "ok": True,
                "name": name,
                "detail": "rc=%s status=%s findings=%s"
                % (rc, observed_status, ",".join(observed_ids) or "-"),
                "stdout": stdout,
                "stderr": stderr,
            }
        )


def _write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path, obj):
    _write_text(path, json.dumps(obj, indent=2, sort_keys=True) + "\n")


def _sha_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _artifact_content(author):
    return "#!/bin/sh\n# r13 selftest artifact for %s\nprintf '%%s\\n' '%s ok'\n" % (
        author,
        author,
    )


def _fragment_obj(
    author,
    artifact,
    evidence,
    sha,
    evidence_sha,
    exit_code=0,
    verdict="pass",
    tested_class="selftest-case",
):
    return {
        "author": author,
        "class": tested_class,
        "artifact": artifact,
        "sha256": sha,
        "command": "sh %s" % artifact,
        "exit_code": exit_code,
        "verdict": verdict,
        "evidence": evidence,
        "evidence_sha256": evidence_sha,
    }


def _write_fragment(root, stem, author, artifact, evidence, sha, evidence_sha, **kwargs):
    rel = "fragments/%s.json" % stem
    _write_json(
        root / rel,
        _fragment_obj(author, artifact, evidence, sha, evidence_sha, **kwargs),
    )
    return rel


def _patch_fragment(root, rel, **changes):
    path = root / rel
    obj = json.loads(path.read_text(encoding="utf-8"))
    obj.update(changes)
    _write_json(path, obj)


def _drop_fragment_key(root, rel, key):
    path = root / rel
    obj = json.loads(path.read_text(encoding="utf-8"))
    obj.pop(key, None)
    _write_json(path, obj)


def _pass_fixture(root, stem, author, artifact_rel, evidence_rel, **kwargs):
    content = _artifact_content(author)
    evidence_text = "%s ok\n" % author
    _write_text(root / artifact_rel, content)
    _write_text(root / evidence_rel, evidence_text)
    return _write_fragment(
        root,
        stem,
        author,
        artifact_rel,
        evidence_rel,
        _sha_text(content),
        _sha_text(evidence_text),
        **kwargs
    )


def selftest():
    tool = Path(os.path.realpath(__file__))
    frozen_fixture = tool.parent.parent / "tests" / "fixtures" / "r13-cert-frozen"
    if not (frozen_fixture / "expected.json").is_file():
        print("finding selftest-unavailable: %s" % frozen_fixture)
        return EXIT_COULD_NOT_EVALUATE

    base = Path(tempfile.mkdtemp(prefix="souji-r13-cert-selftest.", dir="/var/tmp"))
    results = []

    def case(name, root, want_rc, want_ids=(), want_status=None, manifest=None):
        manifest_path = manifest if manifest is not None else root / "manifest.json"
        rc, stdout, stderr = _invoke(tool, root=root, manifest=manifest_path)
        _record(results, name, rc, stdout, stderr, want_rc, list(want_ids), want_status)

    def frozen_case(name, directory, want_rc, want_ids=(), want_status=None):
        rc, stdout, stderr = _invoke(tool, frozen=directory)
        _record(results, name, rc, stdout, stderr, want_rc, list(want_ids), want_status)

    try:
        # 1. clean: two independent passing fragments.
        root = base / "clean"
        root.mkdir()
        first = _pass_fixture(root, "alpha", "author-alpha", "installed/alpha.sh", "evidence/alpha.txt")
        second = _pass_fixture(root, "beta", "author-beta", "installed/beta.sh", "evidence/beta.txt")
        _write_json(root / "manifest.json", {"fragments": [first, second]})
        case("clean", root, EXIT_CLEAN, want_status="clean")

        # 2. installed digest does not match the declared sha256.
        root = base / "digest-mismatch"
        root.mkdir()
        only = _pass_fixture(root, "alpha", "author-alpha", "installed/alpha.sh", "evidence/alpha.txt")
        _patch_fragment(root, only, sha256="0" * 64)
        _write_json(root / "manifest.json", {"fragments": [only]})
        case("digest-mismatch", root, EXIT_COULD_NOT_EVALUATE, ["artifact-digest-mismatch"], "could-not-evaluate")

        # 3. same fragment listed twice.
        root = base / "duplicate-fragment"
        root.mkdir()
        only = _pass_fixture(root, "alpha", "author-alpha", "installed/alpha.sh", "evidence/alpha.txt")
        _write_json(root / "manifest.json", {"fragments": [only, only]})
        case("duplicate-fragment", root, EXIT_COULD_NOT_EVALUATE, ["fragment-duplicate"], "could-not-evaluate")

        # 4. two fragments written by the same author.
        root = base / "duplicate-author"
        root.mkdir()
        first = _pass_fixture(root, "alpha", "same-author", "installed/alpha.sh", "evidence/alpha.txt")
        second = _pass_fixture(root, "beta", "same-author", "installed/beta.sh", "evidence/beta.txt")
        _write_json(root / "manifest.json", {"fragments": [first, second]})
        case("duplicate-author", root, EXIT_COULD_NOT_EVALUATE, ["author-duplicate"], "could-not-evaluate")

        # 5. two authors claim the same artifact path.
        root = base / "shared-artifact"
        root.mkdir()
        content = _artifact_content("shared")
        _write_text(root / "installed/shared.sh", content)
        _write_text(root / "evidence/alpha.txt", "alpha ok\n")
        _write_text(root / "evidence/beta.txt", "beta ok\n")
        first = _write_fragment(root, "alpha", "author-alpha", "installed/shared.sh", "evidence/alpha.txt", _sha_text(content), _sha_text("alpha ok\n"))
        second = _write_fragment(root, "beta", "author-beta", "installed/shared.sh", "evidence/beta.txt", _sha_text(content), _sha_text("beta ok\n"))
        _write_json(root / "manifest.json", {"fragments": [first, second]})
        case("shared-artifact", root, EXIT_COULD_NOT_EVALUATE, ["fragment-shared"], "could-not-evaluate")

        # 6. two authors claim the same evidence path.
        root = base / "shared-evidence"
        root.mkdir()
        alpha_content = _artifact_content("alpha")
        beta_content = _artifact_content("beta")
        _write_text(root / "installed/alpha.sh", alpha_content)
        _write_text(root / "installed/beta.sh", beta_content)
        _write_text(root / "evidence/shared.txt", "shared ok\n")
        first = _write_fragment(root, "alpha", "author-alpha", "installed/alpha.sh", "evidence/shared.txt", _sha_text(alpha_content), _sha_text("shared ok\n"))
        second = _write_fragment(root, "beta", "author-beta", "installed/beta.sh", "evidence/shared.txt", _sha_text(beta_content), _sha_text("shared ok\n"))
        _write_json(root / "manifest.json", {"fragments": [first, second]})
        case("shared-evidence", root, EXIT_COULD_NOT_EVALUATE, ["fragment-shared"], "could-not-evaluate")

        # 7. one fragment uses the artifact as its own evidence.
        root = base / "claim-shared"
        root.mkdir()
        content = _artifact_content("self")
        _write_text(root / "installed/self.sh", content)
        only = _write_fragment(root, "alpha", "author-alpha", "installed/self.sh", "installed/self.sh", _sha_text(content), _sha_text(content))
        _write_json(root / "manifest.json", {"fragments": [only]})
        case("claim-shared", root, EXIT_COULD_NOT_EVALUATE, ["claim-shared"], "could-not-evaluate")

        # 8. evidence path absent.
        root = base / "missing-evidence"
        root.mkdir()
        only = _pass_fixture(root, "alpha", "author-alpha", "installed/alpha.sh", "evidence/alpha.txt")
        (root / "evidence/alpha.txt").unlink()
        _write_json(root / "manifest.json", {"fragments": [only]})
        case("missing-evidence", root, EXIT_COULD_NOT_EVALUATE, ["evidence-missing"], "could-not-evaluate")

        # 9. artifact path absent.
        root = base / "missing-artifact"
        root.mkdir()
        only = _pass_fixture(root, "alpha", "author-alpha", "installed/alpha.sh", "evidence/alpha.txt")
        (root / "installed/alpha.sh").unlink()
        _write_json(root / "manifest.json", {"fragments": [only]})
        case("missing-artifact", root, EXIT_COULD_NOT_EVALUATE, ["artifact-missing"], "could-not-evaluate")

        # 10. verdict=pass with a nonzero recorded exit code (false success).
        root = base / "false-pass"
        root.mkdir()
        only = _pass_fixture(root, "alpha", "author-alpha", "installed/alpha.sh", "evidence/alpha.txt")
        _patch_fragment(root, only, exit_code=3)
        _write_json(root / "manifest.json", {"fragments": [only]})
        case("false-pass", root, EXIT_COULD_NOT_EVALUATE, ["verdict-false-pass"], "could-not-evaluate")

        # 11. honest reported failure: valid evidence, failed certification.
        root = base / "honest-fail"
        root.mkdir()
        only = _pass_fixture(root, "alpha", "author-alpha", "installed/alpha.sh", "evidence/alpha.txt", verdict="fail", exit_code=1)
        _write_json(root / "manifest.json", {"fragments": [only]})
        case("honest-fail", root, EXIT_FAILED, ["fragment-reported-fail"], "failed")

        # 12. verdict=fail with exit_code 0 (unsupported failure claim).
        root = base / "false-fail"
        root.mkdir()
        only = _pass_fixture(root, "alpha", "author-alpha", "installed/alpha.sh", "evidence/alpha.txt", verdict="fail", exit_code=0)
        _write_json(root / "manifest.json", {"fragments": [only]})
        case("false-fail", root, EXIT_COULD_NOT_EVALUATE, ["verdict-false-fail"], "could-not-evaluate")

        # 13. artifact path escapes --root.
        root = base / "path-escape"
        root.mkdir()
        content = _artifact_content("escape")
        _write_text(root / "evidence/alpha.txt", "escape ok\n")
        only = _write_fragment(root, "alpha", "author-alpha", "../escape.sh", "evidence/alpha.txt", _sha_text(content), _sha_text("escape ok\n"))
        _write_json(root / "manifest.json", {"fragments": [only]})
        case("path-escape", root, EXIT_COULD_NOT_EVALUATE, ["path-escape"], "could-not-evaluate")

        # 14. artifact path absolute.
        root = base / "path-absolute"
        root.mkdir()
        content = _artifact_content("absolute")
        _write_text(root / "evidence/alpha.txt", "absolute ok\n")
        only = _write_fragment(root, "alpha", "author-alpha", "/etc/passwd", "evidence/alpha.txt", _sha_text(content), _sha_text("absolute ok\n"))
        _write_json(root / "manifest.json", {"fragments": [only]})
        case("path-absolute", root, EXIT_COULD_NOT_EVALUATE, ["path-absolute"], "could-not-evaluate")

        # 15. evidence is a symlink, even though it resolves inside root.
        root = base / "path-symlink"
        root.mkdir()
        only = _pass_fixture(root, "alpha", "author-alpha", "installed/alpha.sh", "evidence/alpha.txt")
        (root / "evidence/alpha.txt").unlink()
        _write_text(root / "evidence/real.txt", "alpha ok\n")
        os.symlink("real.txt", root / "evidence/alpha.txt")
        _write_json(root / "manifest.json", {"fragments": [only]})
        case("path-symlink", root, EXIT_COULD_NOT_EVALUATE, ["path-symlink"], "could-not-evaluate")

        # 16. evidence is a FIFO: rejected without opening or blocking.
        root = base / "evidence-fifo"
        root.mkdir()
        only = _pass_fixture(root, "alpha", "author-alpha", "installed/alpha.sh", "evidence/alpha.txt")
        (root / "evidence/alpha.txt").unlink()
        os.mkfifo(root / "evidence/alpha.txt")
        _write_json(root / "manifest.json", {"fragments": [only]})
        case("evidence-fifo", root, EXIT_COULD_NOT_EVALUATE, ["evidence-not-regular"], "could-not-evaluate")

        # 17. malformed manifest JSON.
        root = base / "malformed-manifest"
        root.mkdir()
        _write_text(root / "manifest.json", "{not json")
        case("malformed-manifest", root, EXIT_COULD_NOT_EVALUATE, ["manifest-malformed"], "could-not-evaluate")

        # 18. malformed fragment JSON.
        root = base / "malformed-fragment"
        root.mkdir()
        _write_text(root / "fragments/alpha.json", "{not json")
        _write_json(root / "manifest.json", {"fragments": ["fragments/alpha.json"]})
        case("malformed-fragment", root, EXIT_COULD_NOT_EVALUATE, ["fragment-malformed"], "could-not-evaluate")

        # 19. fragment missing a required key.
        root = base / "fragment-schema"
        root.mkdir()
        only = _pass_fixture(root, "alpha", "author-alpha", "installed/alpha.sh", "evidence/alpha.txt")
        _drop_fragment_key(root, only, "sha256")
        _write_json(root / "manifest.json", {"fragments": [only]})
        case("fragment-schema", root, EXIT_COULD_NOT_EVALUATE, ["fragment-schema"], "could-not-evaluate")

        # 20. fragment missing the tested-class label.
        root = base / "missing-class"
        root.mkdir()
        only = _pass_fixture(root, "alpha", "author-alpha", "installed/alpha.sh", "evidence/alpha.txt")
        _drop_fragment_key(root, only, "class")
        _write_json(root / "manifest.json", {"fragments": [only]})
        case("missing-class", root, EXIT_COULD_NOT_EVALUATE, ["fragment-schema"], "could-not-evaluate")

        # 21. evidence file overwritten after the fragment pinned its digest.
        root = base / "evidence-digest-mismatch"
        root.mkdir()
        only = _pass_fixture(root, "alpha", "author-alpha", "installed/alpha.sh", "evidence/alpha.txt")
        _write_text(root / "evidence/alpha.txt", "overwritten evidence\n")
        _write_json(root / "manifest.json", {"fragments": [only]})
        case("evidence-digest-mismatch", root, EXIT_COULD_NOT_EVALUATE, ["evidence-digest-mismatch"], "could-not-evaluate")

        # 22. a claimed artifact has a second hardlink (alias can change bytes).
        root = base / "hardlinked-artifact"
        root.mkdir()
        content = _artifact_content("hardlink")
        _write_text(root / "installed/alpha.sh", content)
        _write_text(root / "evidence/alpha.txt", "alpha ok\n")
        os.link(root / "installed/alpha.sh", root / "installed/alias.sh")
        only = _write_fragment(root, "alpha", "author-alpha", "installed/alpha.sh", "evidence/alpha.txt", _sha_text(content), _sha_text("alpha ok\n"))
        _write_json(root / "manifest.json", {"fragments": [only]})
        case("hardlinked-artifact", root, EXIT_COULD_NOT_EVALUATE, ["path-hardlink"], "could-not-evaluate")

        # 23. a control character in a path cannot forge an output line.
        root = base / "control-char-path"
        root.mkdir()
        content = _artifact_content("control")
        _write_text(root / "evidence/alpha.txt", "control ok\n")
        only = _write_fragment(root, "alpha", "author-alpha", "installed/alpha\nsouji-cert-evidence: clean.sh", "evidence/alpha.txt", _sha_text(content), _sha_text("control ok\n"))
        _write_json(root / "manifest.json", {"fragments": [only]})
        case("control-char-path", root, EXIT_COULD_NOT_EVALUATE, ["path-invalid"], "could-not-evaluate")

        # 24. secret-shaped path is refused before hashing.
        root = base / "protected-path"
        root.mkdir()
        content = _artifact_content("protected")
        _write_text(root / ".env", content)
        _write_text(root / "evidence/alpha.txt", "protected ok\n")
        only = _write_fragment(root, "alpha", "author-alpha", ".env", "evidence/alpha.txt", _sha_text(content), _sha_text("protected ok\n"))
        _write_json(root / "manifest.json", {"fragments": [only]})
        case("protected-path", root, EXIT_COULD_NOT_EVALUATE, ["path-protected"], "could-not-evaluate")

        # 25. .env.* variants are refused too.
        root = base / "protected-env-local"
        root.mkdir()
        content = _artifact_content("protected-env-local")
        _write_text(root / ".env.local", content)
        _write_text(root / "evidence/alpha.txt", "protected env local ok\n")
        only = _write_fragment(root, "alpha", "author-alpha", ".env.local", "evidence/alpha.txt", _sha_text(content), _sha_text("protected env local ok\n"))
        _write_json(root / "manifest.json", {"fragments": [only]})
        case("protected-env-local", root, EXIT_COULD_NOT_EVALUATE, ["path-protected"], "could-not-evaluate")

        # 26. a parent directory of the artifact is a symlink inside root.
        root = base / "parent-symlink"
        root.mkdir()
        content = _artifact_content("parent-link")
        _write_text(root / "real/alpha.sh", content)
        _write_text(root / "evidence/alpha.txt", "parent ok\n")
        os.symlink("real", root / "linked")
        only = _write_fragment(root, "alpha", "author-alpha", "linked/alpha.sh", "evidence/alpha.txt", _sha_text(content), _sha_text("parent ok\n"))
        _write_json(root / "manifest.json", {"fragments": [only]})
        case("parent-symlink", root, EXIT_COULD_NOT_EVALUATE, ["path-symlink"], "could-not-evaluate")

        # 27. a cand-* artifact is a candidate selection, not an installed claim.
        root = base / "candidate-artifact"
        root.mkdir()
        content = _artifact_content("candidate")
        _write_text(root / "tools/cand-alpha.sh", content)
        _write_text(root / "evidence/alpha.txt", "candidate ok\n")
        only = _write_fragment(root, "alpha", "author-alpha", "tools/cand-alpha.sh", "evidence/alpha.txt", _sha_text(content), _sha_text("candidate ok\n"))
        _write_json(root / "manifest.json", {"fragments": [only]})
        case("candidate-artifact", root, EXIT_COULD_NOT_EVALUATE, ["artifact-candidate"], "could-not-evaluate")

        # 28. listed fragment file absent.
        root = base / "fragment-missing"
        root.mkdir()
        _write_json(root / "manifest.json", {"fragments": ["fragments/ghost.json"]})
        case("fragment-missing", root, EXIT_COULD_NOT_EVALUATE, ["fragment-missing"], "could-not-evaluate")

        # 29. empty fragment list cannot certify anything.
        root = base / "manifest-empty"
        root.mkdir()
        _write_json(root / "manifest.json", {"fragments": []})
        case("manifest-empty", root, EXIT_COULD_NOT_EVALUATE, ["manifest-empty"], "could-not-evaluate")

        # 30. fragment path is a directory, not a regular file.
        root = base / "fragment-not-regular"
        root.mkdir()
        (root / "fragments").mkdir()
        (root / "fragments/alpha.json").mkdir()
        _write_json(root / "manifest.json", {"fragments": ["fragments/alpha.json"]})
        case("fragment-not-regular", root, EXIT_COULD_NOT_EVALUATE, ["fragment-not-regular"], "could-not-evaluate")

        # 31. manifest itself absent.
        root = base / "manifest-missing"
        root.mkdir()
        case("manifest-missing", root, EXIT_COULD_NOT_EVALUATE, ["manifest-unreadable"], "could-not-evaluate", manifest=root / "absent.json")

        # 32. --root is not a directory.
        root = base / "root-not-directory"
        root.mkdir()
        not_a_dir = root / "file.txt"
        _write_text(not_a_dir, "not a directory\n")
        rc, stdout, stderr = _invoke(tool, root=not_a_dir, manifest=root / "manifest.json")
        _record(results, "root-not-directory", rc, stdout, stderr, EXIT_COULD_NOT_EVALUATE, ["root-not-directory"], "could-not-evaluate")

        # 33-36. frozen snapshot: clean, tampered, incomplete pins, verdict mismatch.
        clean_copy = base / "frozen-clean"
        shutil.copytree(frozen_fixture, clean_copy)
        frozen_case("frozen-clean", clean_copy, EXIT_CLEAN, want_status="clean")

        tampered_copy = base / "frozen-tampered"
        shutil.copytree(frozen_fixture, tampered_copy)
        evidence_path = tampered_copy / "evidence" / "alpha.txt"
        with evidence_path.open("ab") as handle:
            handle.write(b"tampered\n")
        frozen_case("frozen-tampered", tampered_copy, EXIT_COULD_NOT_EVALUATE, ["snapshot_tampered"], "could-not-evaluate")

        incomplete_copy = base / "frozen-incomplete"
        shutil.copytree(frozen_fixture, incomplete_copy)
        expected_path = incomplete_copy / "expected.json"
        expected_obj = json.loads(expected_path.read_text(encoding="utf-8"))
        expected_obj["files"].pop("evidence/beta.txt", None)
        _write_json(expected_path, expected_obj)
        frozen_case("frozen-incomplete", incomplete_copy, EXIT_COULD_NOT_EVALUATE, ["frozen-incomplete"], "could-not-evaluate")

        mismatch_copy = base / "frozen-verdict-mismatch"
        shutil.copytree(frozen_fixture, mismatch_copy)
        expected_path = mismatch_copy / "expected.json"
        expected_obj = json.loads(expected_path.read_text(encoding="utf-8"))
        expected_obj["verdict"] = "failed"
        _write_json(expected_path, expected_obj)
        frozen_case("frozen-verdict-mismatch", mismatch_copy, EXIT_COULD_NOT_EVALUATE, ["snapshot-verdict-mismatch"], "could-not-evaluate")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    failures = [item for item in results if not item["ok"]]
    for item in results:
        if item["ok"]:
            print("case %s: ok %s" % (item["name"], item["detail"]))
        else:
            print("case %s: FAIL %s" % (item["name"], item["detail"]))
            for stream_name, stream in (("stdout", item["stdout"]), ("stderr", item["stderr"])):
                if stream:
                    print("  %s: %s" % (stream_name, stream.strip().replace("\n", "\n  ")))
    print("selftest: %d/%d passed" % (len(results) - len(failures), len(results)))
    return EXIT_CLEAN if not failures else EXIT_FAILED


# ---------------------------------------------------------------- main

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Executable evidence-consistency gate (not a safety certification)."
    )
    parser.add_argument("--root", help="evidence root; all fragment paths resolve here")
    parser.add_argument("--manifest", help="manifest JSON with an explicit fragments array")
    parser.add_argument("--frozen", help="frozen snapshot directory containing expected.json")
    parser.add_argument("--selftest", action="store_true", help="run built-in /var/tmp fixture battery")
    args = parser.parse_args(argv)

    if args.selftest:
        if args.root or args.manifest or args.frozen:
            parser.error("--selftest accepts no other arguments")
        return selftest()

    if args.frozen:
        if args.root or args.manifest:
            parser.error("--frozen accepts neither --root nor --manifest")
        findings, counts, status = evaluate_frozen(args.frozen)
        _emit(status, findings, counts)
        return status

    if not args.root or not args.manifest:
        parser.error("--root and --manifest are required unless --frozen or --selftest")

    root = Path(args.root)
    if not root.is_dir():
        findings = []
        _add(findings, "root-not-directory", "root=%r" % args.root)
        counts = {"fragments": 0, "assessed": 0, "pass": 0, "fail": 0}
        _emit(_status_for(findings), findings, counts)
        return _status_for(findings)
    root = Path(os.path.realpath(root))

    findings, counts = evaluate(root, Path(args.manifest))
    status = _status_for(findings)
    _emit(status, findings, counts)
    return status


if __name__ == "__main__":
    sys.exit(main())
