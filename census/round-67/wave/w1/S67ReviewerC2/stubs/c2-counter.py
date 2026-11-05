#!/usr/bin/env python3
"""c2-counter.py — souji round-67 C2 counter (extends round-66; M4/M5/M7 repairs): SKILL.md statement/writer agreement at a pinned revision.

Extends census/round-66/c2-counter.py (same evaluator shape) with the three round-66 routed defects:

  * M4 — the round-66 selftest case `m10-returncode-line-not-live` bound the wrong row (s3), whose
    finding came from a missing SKILL sentence, not from the marker read, so reverting the round-66
    token repair (RETURN_LITERAL) left --selftest at 14/14: a vacuous guard. The r67 case
    `m10-s5-assertion-line-not-live` binds the M10 shape to the s5 row: the writer stub carries both
    env needles ONLY on `r.returncode` assertion lines (no `refuse(`, no return-literal), so the
    repaired rule reads them dead and the row's env-claim overreach produces findings=1, while the
    reverted round-65 rule (any line carrying the bare `return` substring, which `r.returncode`
    matches) reads them live and produces findings=0 — the case MISMATCHES and --selftest fails.
  * M5 — the r66 s5 sentence claims the object-redirect route CLASS closed while the class, frozen
    here as REDIRECT_ENUM from the committed S298 capture (git(1) § ENVIRONMENT VARIABLES), has a
    fourth member (GIT_COMMON_DIR) the r66 W2 probe measured open. The new claim token
    `redirects_closed` requires the r66 redirect marker (envred) AND the GIT_COMMON_DIR marker
    (cdred), so a writer that refuses only the three named members leaves the class claim an
    overreach the lexical r66 counter could not see.
  * M7 — the r66 population's s4 note ("absent from base SKILL.md") was false (base SKILL.md carries
    s4; grep count 1); the r67 population corrects the note cell. Notes are not machine-checked
    (the note column is bookkeeping), so this fix is a frozen-population cell plus the lesson record,
    not a counter branch.

Reads, at one full 40-hex revision, committed bytes only:
  * the frozen statement population (--tsv, a repo-relative path, read as a git blob at
    --tsv-rev; --tsv-rev defaults to --rev; its digest is pinned by the preregistration),
  * each row's governed file (SKILL.md) as a git blob at --rev,
  * the receipt-writer blob tools/souji-receipt-write.py at --rev, scanned for the LIVE refusal
    needles that define the enforced surface:

  markers (live needles in tools/souji-receipt-write.py):
    flag      RECEIPT-INDEX-FLAG-CONCEALED     (r62 start-of-run index-flag refusal)
    inrun     RECEIPT-STATE-CHANGED-DURING-RUN (r63/r64 in-run content-snapshot refusal)
    env       RECEIPT-INDEX-ENV-SET            (r64 caller-env refusal)
    unmerged  RECEIPT-INDEX-UNMERGED           (r63 unmerged-refusal classing, the s4 clause)
    envcfg    RECEIPT-ENV-CONFIG-SET           (r66 caller-injected config-route refusal)
    envred    RECEIPT-ENV-REDIRECT-SET         (r66 object-redirect refusal, three names)
    cdred     RECEIPT-ENV-COMMONDIR-MISMATCH   (r67 value-checked GIT_COMMON_DIR refusal)

  claim tokens, requirement (markers that must be present) / forbidden (must be absent):
    stable_flag      required: flag                (r62 writer rule, unchanged)
    closed_full      required: flag, inrun, env    (wording claims the concealment class is closed)
    inrun_landed     required: inrun               (wording says the in-run refusal landed)
    inrun_open       forbidden: inrun              (wording says the in-run gap is open)
    unmerged_refused required: unmerged            (wording pins the unmerged-refusal clause)
    env_closed       required: envcfg, envred      (the r66 s5 claim; kept for historical populations)
    redirects_closed required: envred, cdred       (r67 enumeration-bound object-redirect closure, M5)

  Per row the counter resolves which frozen wording is live (base_pattern XOR after_pattern;
  a row whose two patterns are equal is one stable wording and never resolves as duplicate),
  then checks the live wording's claim against the live-marker map, flagging overreach (statement
  claims behavior the writer bytes lack) and stale-open (statement denies behavior the writer
  bytes carry) in BOTH directions. Claim violations are aggregated to one finding per kind
  per row. Findings, one line each, `FINDING <KIND> <id>: <detail>`:
  GOVERNED-STATEMENT-UNRESOLVED  neither frozen wording present (deleting a statement cannot pass)
  DUPLICATE-LIVE-WORDING         both frozen wordings present (a stale copy left beside the new one)
  SCOPE-OVERREACH                wording claims marker(s) the writer bytes lack
  SCOPE-STALE-OPEN               wording denies marker(s) the writer bytes carry
  CLAIM-TOKEN-INVALID            unknown claim token in the population
  FILE-ABSENT                    governed file missing at the revision

Named limits: this is text-and-marker agreement, not semantic truth beyond the markers. The live
read is lexical: a needle placed inside a docstring or plain literal ON a line that also carries
the text `refuse(`/`return` would still count live, and reachability is not proven — a refusal
behind `if False:` keeps its live line textually and is the C1 behavioral matrix's kill, not this
counter's. The scope check binds refusal NEEDLES, not reached code paths: the M5 class closure is
as deep as the marker read, and the C1 behavioral matrix (W1-W3) is the behavioral kill. The
population is SKILL.md statements only (round-63 M3 narrowing). Matching is plain substring over
stable sentence fragments, never line numbers (round-62 lesson M4 class). The frozen TSV lives at
the controls commit, from where the counter reads it via --tsv-rev.

CLI:
  python3 -B census/round-67/c2-counter.py --root LANE --tsv PATH --rev FULL40 [--tsv-rev FULL40] [--receipt FILE]
  python3 -B census/round-67/c2-counter.py --selftest
Exit: 0 findings=0 (PASS); 1 findings>0 (FAIL); 2 usage/environment error.
The selftest keeps no scratch; it is pure in-memory. --receipt writes four header lines (rev= the
measured revision, instrument= this counter, instrument_sha256=, command=) and then the verbatim
run output, ending EXIT=<rc> — the same grammar as the round-66 c2 receipts, now machine-written.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import shlex
import subprocess
import sys

C2_COUNTER_REL = "census/round-67/c2-counter.py"

WRITER_REL = "tools/souji-receipt-write.py"

MARKERS = {
    "flag": b"RECEIPT-INDEX-FLAG-CONCEALED",
    "inrun": b"RECEIPT-STATE-CHANGED-DURING-RUN",
    "env": b"RECEIPT-INDEX-ENV-SET",
    "unmerged": b"RECEIPT-INDEX-UNMERGED",
    "envcfg": b"RECEIPT-ENV-CONFIG-SET",
    "envred": b"RECEIPT-ENV-REDIRECT-SET",
    "cdred": b"RECEIPT-ENV-COMMONDIR-MISMATCH",
}

REQUIRED = {
    "stable_flag": ("flag",),
    "closed_full": ("flag", "inrun", "env"),
    "inrun_landed": ("inrun",),
    "inrun_open": (),
    "unmerged_refused": ("unmerged",),
    "env_closed": ("envcfg", "envred"),
    # r67 M5 fix: a statement that claims the object-redirect route CLASS is closed must be checked
    # against the class enumeration, not only the three r66 needles. REDIRECT_ENUM below freezes the
    # class from the committed S298 capture (git(1) § ENVIRONMENT VARIABLES); its fourth member,
    # GIT_COMMON_DIR, is the route the round-66 W2 probe measured open (census/round-66/probes/
    # w2-w3-env-probe.txt). The claim token therefore requires the r66 redirect marker (envred) AND
    # the GIT_COMMON_DIR refusal marker (cdred); a writer that refuses only the three named members
    # leaves this claim an overreach.
    "redirects_closed": ("envred", "cdred"),
}

# The object-redirect route class, frozen from the committed round-66 source capture
# census/round-66/sources/git-environment.txt (S298, git(1) § ENVIRONMENT VARIABLES): the three
# r66 refusal names plus GIT_COMMON_DIR (whose entry reads "If this variable is set to a path" —
# it redirects where git finds the shared parts of a repository). A statement that claims the class
# closed while any member lacks a live refusal needle is a scope overreach (round-66 M5).
REDIRECT_ENUM = ("GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
                 "GIT_REPLACE_REF_BASE", "GIT_COMMON_DIR")

FORBIDDEN = {
    "inrun_open": ("inrun",),
}

EMISSION_TOKENS = ("refuse(",)
# r66 M10 repair: `return` as a bare substring matched `returncode`, so a selftest assertion line that
# carries a needle and `r.returncode` read as an emission path (round-65 M10: deleted env refusal -> findings=0).
# An emission path is now a `refuse(` call or a `return` statement whose value begins with a string literal.
RETURN_LITERAL = re.compile(r"\breturn\s*\(?\s*f?[\"']")


def live_markers(writer: bytes) -> dict:
    """r65 C2: a marker counts only when its needle occurs on a refusal-emitting code line: a line
    that does not start with `#` and that also carries `refuse(` or `return` (the emission paths of
    every writer refusal: direct refuse(...) calls and the _flag_refusal return strings). A token
    kept only in a comment, a docstring (which carries no refuse(/return text in this writer
    family) or an unused literal is dead and scores as absent — the dead-token polarity class.
    Named limit: reachability is not proven; a refusal behind `if False:` keeps its live line and
    is the C1 behavioral matrix's kill."""
    out = {name: False for name in MARKERS}
    for raw in writer.decode("utf-8", "replace").splitlines():
        if raw.lstrip().startswith("#"):
            continue
        if not (any(tok in raw for tok in EMISSION_TOKENS) or RETURN_LITERAL.search(raw)):
            continue
        for name, needle in MARKERS.items():
            if not out[name] and needle.decode("utf-8", "replace") in raw:
                out[name] = True
    return out

COLUMNS = ["id", "file", "base_pattern", "base_claim", "after_pattern", "after_claim", "note"]
REV_RE = re.compile(r"^[0-9a-f]{40}$")


def git_show(root: str, rev: str, rel: str) -> bytes:
    r = subprocess.run(["git", "-C", root, "show", f"{rev}:{rel}"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"git show {rev}:{rel} failed rc={r.returncode}: "
                           f"{r.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return r.stdout


def check_claim(claim: str, markers: dict) -> list[tuple[str, str]]:
    """Return (kind, detail) pairs for one claim token, aggregated per kind."""
    if claim not in REQUIRED:
        return [("CLAIM-TOKEN-INVALID", claim)]
    out: list[tuple[str, str]] = []
    missing = [name for name in REQUIRED[claim] if not markers.get(name)]
    if missing:
        out.append(("SCOPE-OVERREACH",
                    f"claim {claim} needs writer markers {', '.join(missing)}; writer blob lacks them"))
    denied_present = [name for name in FORBIDDEN.get(claim, ()) if markers.get(name)]
    if denied_present:
        out.append(("SCOPE-STALE-OPEN",
                    f"claim {claim} forbids writer markers {', '.join(denied_present)}; "
                    f"writer blob carries them"))
    return out


def evaluate(rows: list[dict], blobs: dict, markers: dict) -> list[dict]:
    """Pure evaluator. rows: dicts with COLUMNS keys. blobs: relpath -> bytes (None = absent).
    markers: marker name -> bool. Returns a list of finding dicts {id, kind, detail}."""
    findings: list[dict] = []
    for row in rows:
        rid = row["id"]
        blob = blobs.get(row["file"])
        if blob is None:
            findings.append({"id": rid, "kind": "FILE-ABSENT", "detail": row["file"]})
            continue
        stable = row["base_pattern"] == row["after_pattern"]
        base_hit = row["base_pattern"].encode("utf-8") in blob
        after_hit = row["after_pattern"].encode("utf-8") in blob
        if stable:
            if not base_hit:
                findings.append({"id": rid, "kind": "GOVERNED-STATEMENT-UNRESOLVED",
                                 "detail": "stable wording absent at this revision"})
                continue
            wording, claim = "stable", row["after_claim"]
        else:
            if base_hit and after_hit:
                findings.append({"id": rid, "kind": "DUPLICATE-LIVE-WORDING",
                                 "detail": "both frozen wordings present; a stale copy remains"})
                continue
            if not base_hit and not after_hit:
                findings.append({"id": rid, "kind": "GOVERNED-STATEMENT-UNRESOLVED",
                                 "detail": "neither frozen wording present at this revision"})
                continue
            wording, claim = ("base", row["base_claim"]) if base_hit else ("after", row["after_claim"])
        for kind, detail in check_claim(claim, markers):
            findings.append({"id": rid, "kind": kind, "detail": f"{wording} wording: {detail}"})
    return findings


def load_tsv_text(text: str) -> list[dict]:
    rows: list[dict] = []
    seen: set[str] = set()
    lines = text.splitlines()
    if not lines:
        raise RuntimeError("tsv is empty")
    header = lines[0].split("\t")
    if header != COLUMNS:
        raise RuntimeError(f"tsv header {header!r} != {COLUMNS!r}")
    for lineno, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) != len(COLUMNS):
            raise RuntimeError(f"tsv line {lineno}: {len(cells)} cells, want {len(COLUMNS)}")
        row = dict(zip(COLUMNS, cells))
        if row["id"] in seen:
            raise RuntimeError(f"tsv line {lineno}: duplicate statement id {row['id']}")
        seen.add(row["id"])
        rows.append(row)
    if not rows:
        raise RuntimeError("tsv holds no statements")
    return rows


def run(root: str, rev: str, tsv_rel: str, tsv_rev: str) -> int:
    if not REV_RE.match(rev):
        print(f"C2-COUNTER-FATAL: rev is not full 40-hex ({rev})", file=sys.stderr)
        print("EXIT=2")
        return 2
    if not REV_RE.match(tsv_rev):
        print(f"C2-COUNTER-FATAL: tsv-rev is not full 40-hex ({tsv_rev})", file=sys.stderr)
        print("EXIT=2")
        return 2
    try:
        rows = load_tsv_text(git_show(root, tsv_rev, tsv_rel).decode("utf-8"))
        blobs: dict = {WRITER_REL: git_show(root, rev, WRITER_REL)}
        for row in rows:
            rel = row["file"]
            if rel not in blobs:
                try:
                    blobs[rel] = git_show(root, rev, rel)
                except RuntimeError:
                    blobs[rel] = None
    except (RuntimeError, OSError) as exc:
        print(f"C2-COUNTER-FATAL: {exc}", file=sys.stderr)
        print("EXIT=2")
        return 2
    writer = blobs[WRITER_REL]
    markers = live_markers(writer)
    findings = evaluate(rows, blobs, markers)
    for f in findings:
        print(f"FINDING {f['kind']} {f['id']}: {f['detail']}")
    print("MARKERS " + " ".join(f"{n}={int(v)}" for n, v in markers.items()))
    print(f"SUMMARY rows={len(rows)} findings={len(findings)} "
          f"verdict={'PASS' if not findings else 'FAIL'} rev={rev}")
    rc = 0 if not findings else 1
    print(f"EXIT={rc}")
    return rc


S1_PAT = ("any tracked index entry whose `git ls-files -v` tag is not `H`, "
          "with a message beginning `RECEIPT-INDEX-FLAG-CONCEALED:`")
S2_BASE = "closed in round 62 by C1"
S2_AFTER = ("closed by the `tools/souji-receipt-write.py` refusals `RECEIPT-INDEX-FLAG-CONCEALED`, "
            "`RECEIPT-STATE-CHANGED-DURING-RUN` and `RECEIPT-INDEX-ENV-SET`")
S3_BASE = "a flag set, or a file edited, while the wrapped command runs is not checked"
S3_AFTER = ("a flag set, or a file edited, while the wrapped command runs is refused with "
            "`RECEIPT-STATE-CHANGED-DURING-RUN`")
S4_PAT = "an unmerged index entry is refused with `RECEIPT-INDEX-UNMERGED`"
S5_PAT = ("closed for the caller-injected config and object-redirect routes by the "
          "`tools/souji-receipt-write.py` refusals `RECEIPT-ENV-CONFIG-SET` and "
          "`RECEIPT-ENV-REDIRECT-SET`")


def _row(rid: str, file: str, bp: str, bc: str, ap: str, ac: str) -> dict:
    return {"id": rid, "file": file, "base_pattern": bp, "base_claim": bc,
            "after_pattern": ap, "after_claim": ac, "note": ""}


def _rows4() -> list[dict]:
    return [
        _row("s1", "SKILL.md", S1_PAT, "stable_flag", S1_PAT, "stable_flag"),
        _row("s2", "SKILL.md", S2_BASE, "closed_full", S2_AFTER, "closed_full"),
        _row("s3", "SKILL.md", S3_BASE, "inrun_open", S3_AFTER, "inrun_landed"),
        _row("s4", "SKILL.md", S4_PAT, "unmerged_refused", S4_PAT, "unmerged_refused"),
    ]


def _rows5() -> list[dict]:
    """The r67 population shape: the four carried rows plus s5 (the r66 env sentence, whose claim
    is upgraded from env_closed to the enumeration-bound redirects_closed; round-66 M5)."""
    rows = _rows4()
    rows.append(_row("s5", "SKILL.md", S5_PAT, "env_closed", S5_PAT, "redirects_closed"))
    return rows


def selftest() -> int:
    """Pure in-memory cases through evaluate(). Expected finding counts are fixed in advance.
    Writer blobs come in live form (each needle sits on a `refuse(`/`return` line), dead form
    (needles only in comments/plain literals — the dead-token second-polarity mutant, which must
    produce findings wherever the live form passes), and token-free form. The always-zero stub
    (a counter that reports nothing) must be rejected: its output would equal the honest-pass
    result on the first case, so at least one non-pass case must be nonzero."""

    def _live(*names: str) -> bytes:
        out = bytearray()
        for n in names:
            out += (f'def _e_{n.decode()}(p):\n    refuse("{n.decode()}: " + p)\n'
                    f"    return\n").encode("utf-8")
        return bytes(out)

    writer_all = _live(MARKERS["flag"], MARKERS["inrun"], MARKERS["env"], MARKERS["unmerged"])
    writer_flag = _live(MARKERS["flag"])
    writer_dead = (b"# RECEIPT-INDEX-FLAG-CONCEALED\n"  # comment-only tokens: the dead-token mutant
                   b"DEAD = 'RECEIPT-STATE-CHANGED-DURING-RUN'\n"
                   b"DOC = \"\"\"RECEIPT-INDEX-ENV-SET RECEIPT-INDEX-UNMERGED\"\"\"\n"
                   b"refuse('unrelated')\n")
    writer_none = b"x plain writer, no refusal tokens y\n"
    skill_base = (S1_PAT + "\n" + S2_BASE + "\n" + S3_BASE + "\n").encode("utf-8")
    skill_base4 = (S1_PAT + "\n" + S2_BASE + "\n" + S3_BASE + "\n" + S4_PAT + "\n").encode("utf-8")
    skill_tip = (S1_PAT + "\n" + S2_AFTER + "\n" + S3_AFTER + "\n" + S4_PAT + "\n").encode("utf-8")
    skill_tip5 = (skill_tip + S5_PAT.encode("utf-8") + b"\n")

    def _live_cd(*names: bytes) -> bytes:
        out = bytearray()
        for n in names:
            out += (f'def _e_{n.decode()}(p):\n    refuse("{n.decode()}: " + p)\n'
                    f"    return\n").encode("utf-8")
        return bytes(out)

    # r67 scope fixtures: the r66 writer shape refuses the three r66 redirect names (envred live)
    # but has no GIT_COMMON_DIR refusal (cdred dead); the repaired shape carries cdred too. Both
    # carry every other live marker so only the redirects_closed claim differs between the cases.
    _writer_envred_no_cd = _live_cd(MARKERS["flag"], MARKERS["inrun"], MARKERS["env"],
                                    MARKERS["unmerged"], b"RECEIPT-ENV-CONFIG-SET",
                                    b"RECEIPT-ENV-REDIRECT-SET")
    _writer_envred_with_cd = _live_cd(MARKERS["flag"], MARKERS["inrun"], MARKERS["env"],
                                      MARKERS["unmerged"], b"RECEIPT-ENV-CONFIG-SET",
                                      b"RECEIPT-ENV-REDIRECT-SET",
                                      b"RECEIPT-ENV-COMMONDIR-MISMATCH")
    cases = [
        # green on the four-row population when every live marker is present
        ("honest-tip-green", _rows4(), {"SKILL.md": skill_tip}, writer_all, 0),
        # do-nothing at the base: s2 overreach (closed_full vs flag-only) + s4 statement absent
        ("do-nothing-base-s2-overreach-s4-unresolved", _rows4(), {"SKILL.md": skill_base}, writer_flag, 2),
        # kind-only forgery: claims without any live markers -> every claim overreaches
        ("kind-only-forgery-claims-without-markers", _rows4(), {"SKILL.md": skill_tip}, writer_none, 4),
        # DEAD-TOKEN FALSIFIER: needles present but dead (comment/literal only) must score like
        # the token-free writer and produce the same four findings the live form does not
        ("dead-token-mutant-produces-findings", _rows4(), {"SKILL.md": skill_tip}, writer_dead, 4),
        # green writer with dead tokens ONLY in comments/literals is refused by the anchored read
        ("dead-tokens-are-not-live", _rows4(), {"SKILL.md": skill_tip}, writer_dead, 4),
        # stale-open: base wording denies behavior the full writer carries (s4 present so the case
        # isolates the stale-open finding)
        ("stale-open-base-wording-full-writer", _rows4(), {"SKILL.md": skill_base4}, writer_all, 1),
        ("duplicate-live-wordings", _rows4(), {"SKILL.md": skill_tip + S2_BASE.encode("utf-8") + b"\n"},
         writer_all, 1),
        ("deleted-governed-statements", _rows4(), {"SKILL.md": b"unrelated text\n"}, writer_all, 4),
        ("decoy-row-file-absent", [_row("d0", "census/round-65/nonexistent-statements.md",
                                        "decoy base", "stable_flag", "decoy after", "stable_flag")],
         {}, writer_all, 1),
        ("claim-token-invalid", [_row("t8", "f.md", "w1", "bogus_claim", "w1", "bogus_claim")],
         {"f.md": b"w1\n"}, writer_all, 1),
        ("stable-wording-missing-flag", [_rows4()[0]], {"SKILL.md": S1_PAT.encode("utf-8")},
         writer_none, 1),
        ("unmerged-clause-green", [_rows4()[3]], {"SKILL.md": S4_PAT.encode("utf-8")},
         _live(MARKERS["unmerged"]), 0),
        ("unmerged-clause-dead-token", [_rows4()[3]], {"SKILL.md": S4_PAT.encode("utf-8")},
         writer_dead, 1),
        # r66 M10 regression: a needle on a selftest assertion line that carries `r.returncode` is not an
        # emission path; the env refusal's deletion (round-65 M10 mutant m4) must therefore score findings.
        ("m10-returncode-line-not-live", [_rows4()[2]], {"SKILL.md": S2_AFTER.encode("utf-8")},
         b'if r.returncode != 2 or "RECEIPT-INDEX-ENV-SET" not in r.stderr:\n    pass\n'
         b'if r.returncode != 2 or "RECEIPT-STATE-CHANGED-DURING-RUN" not in r.stderr:\n    pass\n'
         b'_live_flag = "RECEIPT-INDEX-FLAG-CONCEALED"\n', 1),
        # r67 M4 fix: the vacuous r66 case above still passes with the token rule reverted (its
        # finding comes from a missing SKILL sentence, not from the marker read). This case binds
        # the M10 shape to a row whose outcome DEPENDS on the token rule: the writer stub carries
        # the env needles ONLY on `r.returncode` assertion lines (no `refuse(`, no return-literal),
        # the SKILL blob resolves the statement, and the row's claim `env_closed` needs both env
        # markers live. The repaired rule reads them dead -> SCOPE-OVERREACH (findings=1); the
        # reverted round-65 rule (any line carrying the bare `return` substring, which
        # `r.returncode` matches) reads them live -> findings=0 and this case's want=1 MISMATCHES.
        # Reverting the repair fails --selftest. The claim is env_closed, NOT redirects_closed: a
        # cdred-requiring claim would fail on the stub's absent cdred marker regardless of the
        # token rule — the exact vacuity shape the round-66 case suffered (bound to an outcome its
        # mutation cannot move; caught by this lane's own pre-freeze mutant run, round-67 lesson).
        ("m10-s5-assertion-line-not-live",
         [_row("s5", "SKILL.md", S5_PAT, "env_closed", S5_PAT, "env_closed")],
         {"SKILL.md": S5_PAT.encode("utf-8")},
         b'if r.returncode != 2 or "RECEIPT-ENV-CONFIG-SET" not in r.stderr:\n    pass\n'
         b'if r.returncode != 2 or "RECEIPT-ENV-REDIRECT-SET" not in r.stderr:\n    pass\n', 1),
        # r67 M5 kill, historical state: the r66 SKILL s5 sentence claims the object-redirect class
        # closed while the pinned r66 writer refuses only three of the four enumerated members
        # (GIT_COMMON_DIR open, measured by census/round-66/probes/w2-w3-env-probe.txt). The live
        # read must flag exactly this overreach.
        ("redirects-closed-scope-overreach-at-r66", _rows5(),
         {"SKILL.md": skill_tip5}, _writer_envred_no_cd, 1),
        # the same population and wording against a writer that carries all four refusal markers is
        # green — the token does not over-flag an honest repaired state.
        ("redirects-closed-green-with-cd", _rows5(),
         {"SKILL.md": skill_tip5}, _writer_envred_with_cd, 0),
    ]
    got_counts = []
    ok = True
    for name, crows, cblobs, cwriter, want in cases:
        markers = live_markers(cwriter)
        got = len(evaluate(crows, cblobs, markers))
        got_counts.append(got)
        good = got == want
        ok = ok and good
        print(f"SELFTEST-CASE {name}: findings={got} want={want} {'pass' if good else 'MISMATCH'}")
    stub_zero = all(c == 0 for c in got_counts[1:])
    print(f"SELFTEST control=STUB-ALWAYS-ZERO {'ACCEPTED-FALSE-GREEN' if stub_zero else 'REJECTED'}")
    ok = ok and not stub_zero
    print(f"SELFTEST pass cases={len(cases)} fail={0 if ok else 1}")
    print(f"EXIT={0 if ok else 1}")
    return 0 if ok else 1


def write_receipt(path: str, rev: str, command: str) -> str:
    """r67: machine-written receipt header for the run (the r66 c2 receipts were L1-assembled by
    hand; this helper replaces that). Four column-0 header lines, then nothing — the caller tees the
    run output into the file after this header, or passes output_lines."""
    counter_sha = hashlib.sha256(open(os.path.realpath(__file__), "rb").read()).hexdigest()
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"rev={rev}\n")
        f.write("instrument=census/round-67/c2-counter.py\n")
        f.write(f"instrument_sha256={counter_sha}\n")
        f.write(f"command={command}\n")
    return counter_sha


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="souji round-67 C2 counter: SKILL.md statement/writer agreement with the "
                    "enumeration-bound redirects_closed scope check (r66 M5) and the M10-bound "
                    "selftest row (r66 M4)")
    ap.add_argument("--root", help="lane root (or a scratch clone holding --tsv-rev)")
    ap.add_argument("--tsv", help="frozen population, a repo-relative path (required)")
    ap.add_argument("--rev", help="full 40-hex revision to read statements and writer from")
    ap.add_argument("--tsv-rev", help="revision holding the frozen population (default: --rev); "
                    "the do-nothing control reads the population from a commit that holds it")
    ap.add_argument("--receipt", help="write a header-complete receipt (rev/instrument/"
                    "instrument_sha256/command + the run output) to FILE")
    ap.add_argument("--selftest", action="store_true")
    ns = ap.parse_args(argv)
    if ns.selftest:
        if ns.root or ns.rev or ns.tsv:
            print("C2-COUNTER-FATAL: --selftest takes no --root/--tsv/--rev", file=sys.stderr)
            return 2
        return selftest()
    if not ns.root or not ns.tsv or not ns.rev:
        print("C2-COUNTER-FATAL: --root, --tsv and --rev are required without --selftest",
              file=sys.stderr)
        return 2
    if ns.receipt:
        # Tee: capture stdout while run() prints, then write headers + captured output.
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = run(ns.root, ns.rev, ns.tsv, ns.tsv_rev or ns.rev)
        command = "python3 -B " + " ".join(shlex.quote(a) for a in [C2_COUNTER_REL, *argv])
        sha = write_receipt(ns.receipt, ns.rev, command)
        with open(ns.receipt, "a", encoding="utf-8") as f:
            f.write(buf.getvalue())
        print(buf.getvalue(), end="")
        print(f"# receipt={os.path.abspath(ns.receipt)} instrument_sha256={sha}")
        return rc
    return run(ns.root, ns.rev, ns.tsv, ns.tsv_rev or ns.rev)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
