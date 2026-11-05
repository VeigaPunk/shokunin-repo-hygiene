#!/usr/bin/env python3
"""c2-counter.py — souji round-65 C2 counter: SKILL.md statement/writer agreement at the landed tip.

Adapted from census/round-64/c2-counter.py (same evaluator shape) with the round-65 changes: a
fourth population row pinning the unmerged-refusal clause, and a LIVE (anchored) marker read —
a refusal needle counts only when it occurs on an uncommented code line that also carries
`refuse(` or `return`, the two emission paths of every writer refusal. This is the round-64
connector's dead-token falsifier (tabi round-62 polarity class): writer bytes can carry every
needle inside a comment or an unused literal while the refusal itself is disabled; such bytes
score as if the needle were absent, so a dead-token second-polarity mutant produces findings.

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

  claim tokens, requirement (markers that must be present) / forbidden (must be absent):
    stable_flag      required: flag                (r62 writer rule, unchanged)
    closed_full      required: flag, inrun, env    (wording claims the concealment class is closed)
    inrun_landed     required: inrun               (wording says the in-run refusal landed)
    inrun_open       forbidden: inrun              (wording says the in-run gap is open)
    unmerged_refused required: unmerged            (wording pins the unmerged-refusal clause)

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
counter's. The population is SKILL.md statements only (round-63 M3 narrowing). Matching is plain
substring over stable sentence fragments, never line numbers (round-62 lesson M4 class). The
frozen TSV lives at the controls commit, from where the counter reads it via --tsv-rev; the
after-wordings are the counter's own S2_AFTER/S3_AFTER literals plus the s4 sentence.

CLI:
  python3 -B census/round-65/c2-counter.py --root LANE --tsv PATH --rev FULL40 [--tsv-rev FULL40]
  python3 -B census/round-65/c2-counter.py --selftest
Exit: 0 findings=0 (PASS); 1 findings>0 (FAIL); 2 usage/environment error.
The selftest keeps no scratch; it is pure in-memory.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys

WRITER_REL = "tools/souji-receipt-write.py"

MARKERS = {
    "flag": b"RECEIPT-INDEX-FLAG-CONCEALED",
    "inrun": b"RECEIPT-STATE-CHANGED-DURING-RUN",
    "env": b"RECEIPT-INDEX-ENV-SET",
    "unmerged": b"RECEIPT-INDEX-UNMERGED",
}

REQUIRED = {
    "stable_flag": ("flag",),
    "closed_full": ("flag", "inrun", "env"),
    "inrun_landed": ("inrun",),
    "inrun_open": (),
    "unmerged_refused": ("unmerged",),
}

FORBIDDEN = {
    "inrun_open": ("inrun",),
}

EMISSION_TOKENS = ("refuse(", "return")


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
        if not any(tok in raw for tok in EMISSION_TOKENS):
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


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="souji round-65 C2 counter: SKILL.md statement/writer agreement (live markers)")
    ap.add_argument("--root", help="lane root (or a scratch clone holding --tsv-rev)")
    ap.add_argument("--tsv", help="frozen population, a repo-relative path (required)")
    ap.add_argument("--rev", help="full 40-hex revision to read statements and writer from")
    ap.add_argument("--tsv-rev", help="revision holding the frozen population (default: --rev); "
                    "the do-nothing control reads the population from a commit that holds it")
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
    return run(ns.root, ns.rev, ns.tsv, ns.tsv_rev or ns.rev)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
