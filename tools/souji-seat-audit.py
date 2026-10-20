#!/usr/bin/env python3
"""souji-seat-audit — enforce the wave probe rule from seat transcripts (round 16, R5).

Seat self-reports (`## Commands`) are disclosure, not enforcement. This tool
reads the harness-rendered transcripts of every seat in one wave (one text
file per seat, `<SeatName>.txt`, exported from `history://<lane>.<SeatName>`)
and classifies every recorded tool call (`→ tool(args…) ⇒ status`) against the
wave contract, using the wave spec for each seat's role and OWNED files.

Violation classes (pinned):
  major  V-SURFACE      args name a forbidden surface: census/operator-sweep-*,
                        a ~/.omp path (except ~/.omp/agent/RULES.md, which the
                        tooling directive requires), .ufo/state, .ufo/watchdog.log
  major  V-LIVE-CENSUS  a souji-census.sh invocation with --root outside /var/tmp
  major  V-WRITE-SCOPE  write/edit to a path that is neither the seat's report,
                        one of its OWNED files, nor under the seat's
                        /var/tmp/souji-r<N>-<Seat>/ scratch (normalized)
  major  V-WRITE-RELATIVE  a bare (non-header) relative write/edit target: the
                        contract runs tools at the fleet root, so it cannot
                        reach an allowed lane path; attempt semantics, major
                        on ok and error alike
  major  V-EXEC         a non-executor/non-mutation-tester seat runs a lane tool,
                        fixture or --selftest (bash -n / py_compile / ast exempt)
  minor  V-RECURSIVE    find/grep -r/rg/ls -R or a grep/glob tool call rooted at
                        the lane root or the fleet root
  minor  V-PROBE        a bash invocation of find, strace, realpath or readlink
                        touching the lane or fleet root (R16-M5)
  minor/major V-WRITE-UNPARSED  a write/edit call whose rendered target cannot be
                        resolved (prose fragment, truncation, empty): major on
                        a successful call (unresolved writes fail closed),
                        minor on a failed call

Limits: the rendered transcript truncates long arguments (`…`), so a pattern
past the cut is not seen; the audit is a lower bound on violations, never a
proof of absence. It reads no transcript store directly.

Usage: souji-seat-audit.py --spec W.json --transcripts DIR --lane LANE [--json OUT]
       souji-seat-audit.py --selftest
Exit: 0 no major violation; 1 at least one major violation; 2 usage/unreadable.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

CALL_RE = re.compile(r"^→ ([A-Za-z_][\w.-]*)\((.*)\)\s*⇒\s*(\S+)")
# A forbidden surface counts only when it appears as a path (the dated sweep
# directory, a path inside .ufo/state, an absolute watchdog log, the store),
# not as a word inside a search pattern.
SURFACE_RE = re.compile(
    r"census/operator-sweep-\d|\.ufo/state/|/\.ufo/watchdog\.log"
    r"|(?:~|/home/[^/\s]+)/\.omp/(?!agent/RULES\.md)"
)
LINE_NO_RE = re.compile(r"^\d+:")
LIVE_CENSUS_RE = re.compile(r"souji-census\.sh\b[^|;&]*--root\s+(?!/var/tmp)\S")
EXEC_RE = re.compile(
    r"(?:python3?\s+(?:-\w+\s+)*\S*(?:tests/fixtures|tools|census/round-\d+)/\S+\.py(?!\S))"
    r"|(?:(?:^|[;&|(]\s*|&&\s*)bash\s+(?!-n\b)\S*\.sh\b)|--selftest\b"
)
# A rendered hashline header `[path[#TAG]]`. Every header in an edit argument
# is audited; a `[` left unclosed by the renderer's `…` marker is an
# unresolved (truncated) target.
EDIT_HEADER_RE = re.compile(r"\[([A-Za-z0-9_./~+@%:-]+)(?:#([0-9A-Fa-f]+))?\]")
# A write/edit target is a single bare path token: no whitespace, no prose
# punctuation. Anything else in the rendered argument is not a target.
PATH_TOKEN_RE = re.compile(r"[A-Za-z0-9_./~+@%:-]+\Z")
RECURSIVE_BASH_RE = re.compile(r"(?:^|[;&|]\s*)(?:find\s|rg\s|grep\s+-\w*r|ls\s+-\w*R)")
PROBE_BASH_RE = re.compile(r"(?:^|[;&|(]\s*|&&\s*)(?:find|strace|realpath|readlink)\s")
OWN_RE = re.compile(r"OWN ONLY ([^\n]+?)(?:\s\(|\.\s|$)")
ABS_RE = re.compile(r"/home/[^\s,`'\"]+")
WRITE_TOOLS = {"write", "edit", "ast_edit"}
EXEC_ROLES = {"executor", "mutation-tester"}


def owned_paths(prompt: str) -> list[str]:
    out: list[str] = []
    for m in OWN_RE.finditer(prompt):
        out.extend(p.rstrip(".,;:)") for p in ABS_RE.findall(m.group(1)))
    return out


def _norm(p: str) -> str:
    return os.path.normpath(p)


def _under(path: str, prefix: str) -> bool:
    """Normalized `path` equals `prefix` or sits inside it."""
    return path == prefix or path.startswith(prefix + os.sep)


def write_targets(tool: str, args: str) -> list[tuple[str | None, bool, bool]]:
    """Extract the rendered target list of a write/edit call.

    Each item is (target, truncated, is_header):
    - target: the visible path text, or None when the argument is not a
      parseable target (prose fragment, empty, unclosed bracket).
    - truncated: the target text was cut by the renderer's `…` marker.
    - is_header: the target came from a `[path#TAG]` hashline header; header
      targets may resolve under the lane root, bare targets against the
      contract's fleet root."""
    a = args.strip()
    if tool != "write":
        # A `[x]` token is a header only when x looks like a path (has / or .)
        # or carries a #TAG; otherwise it is regex/prose content.
        headers = []
        for m in EDIT_HEADER_RE.finditer(a):
            tok = m.group(1)
            if m.group(2) or "/" in tok or "." in tok:
                headers.append((tok.strip(), False, True))
        if headers or "[" in a:
            # An unclosed `[path` after the last complete header is a
            # truncated header.
            open_tail = a.find("[", a.rfind("]") + 1)
            if open_tail >= 0:
                frag = a[open_tail + 1 :].split("#", 1)[0].strip()
                if frag.endswith("…"):
                    frag = frag[:-1]
                if frag and all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_./~+@%:-" for c in frag):
                    headers.append((frag, True, True))
                else:
                    headers.append((None, True, True))
            if not headers:
                return [(None, True, True)]
            return headers
    first = a.split(",", 1)[0].strip()
    if first.endswith("…"):
        return [(first[:-1], True, False)]
    if PATH_TOKEN_RE.fullmatch(first):
        return [(first, False, False)]
    return [(None, False, False)]


def target_verdict(target: str | None, truncated: bool, is_header: bool,
                   allowed: list[str], lane: str, fleet: str,
                   scratch: str) -> str | None:
    """Classify one rendered write/edit target. Returns a violation class."""
    if target is None:
        return "V-WRITE-UNPARSED"
    if target.startswith("agent://"):
        return None  # peer message, not a file write
    if truncated:
        if not target.startswith("/"):
            return "V-WRITE-RELATIVE"
        vis = _norm(target)
        # A visible prefix compatible with the seat's scratch dir resolves
        # inside the one region seats may write freely; allowed like any
        # other scratch write.
        if _under(vis, _norm(scratch)) or _under(_norm(scratch), vis) \
                or _norm(scratch).startswith(vis):
            return None
        for p in allowed:
            np = _norm(p)
            if np == vis or np.startswith(vis):
                return "V-WRITE-UNPARSED"
        return "V-WRITE-SCOPE"
    if target.startswith("/"):
        n = _norm(target)
        if _under(n, _norm(scratch)) or any(n == _norm(p) for p in allowed):
            return None
        return "V-WRITE-SCOPE"
    # Relative target: never silently allowed (CX1). Bare targets resolve at
    # the contract's fleet root, which cannot reach a lane path; header
    # targets are tried against both roots before the attempt is refused.
    if is_header:
        rel = target.removeprefix("./")
        for root in (lane, fleet):
            n = _norm(root + "/" + rel)
            if _under(n, _norm(scratch)) or any(n == _norm(p) for p in allowed):
                return None
    return "V-WRITE-RELATIVE"


def audit_seat(text: str, role: str, report: str, owned: list[str], lane: str,
               fleet: str, scratch: str = "/var/tmp/") -> tuple[int, list[dict]]:
    calls = 0
    found: list[dict] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        # Exports through the read tool prefix each line with `N:`.
        m = CALL_RE.match(LINE_NO_RE.sub("", line, count=1))
        if not m:
            continue
        calls += 1
        tool, args, status = m.group(1), m.group(2), m.group(3)

        def flag(cls: str, sev: str, target: str | None = None) -> None:
            row = {"class": cls, "severity": sev, "line": lineno, "tool": tool, "args": args[:200]}
            if target is not None:
                row["target"] = target
            found.append(row)

        if SURFACE_RE.search(args):
            flag("V-SURFACE", "major")
        if tool == "bash" and LIVE_CENSUS_RE.search(args):
            flag("V-LIVE-CENSUS", "major")
        if tool in WRITE_TOOLS:
            allowed = [report, *owned]
            for target, truncated, is_header in write_targets(tool, args):
                cls = target_verdict(target, truncated, is_header, allowed,
                                     lane, fleet, scratch)
                if cls is None:
                    continue
                if cls == "V-WRITE-UNPARSED" and status != "ok":
                    sev = "minor"
                else:
                    sev = "major"
                flag(cls, sev, target)
        if tool == "bash" and role not in EXEC_ROLES and EXEC_RE.search(args):
            flag("V-EXEC", "major")
        if tool == "bash" and RECURSIVE_BASH_RE.search(args) and (lane in args or fleet in args or " . " in args):
            flag("V-RECURSIVE", "minor")
        if tool == "bash" and PROBE_BASH_RE.search(args) and (lane in args or fleet in args or " . " in args):
            flag("V-PROBE", "minor")
        if tool in {"grep", "glob"}:
            a = args.rstrip("…").rstrip()
            if a.endswith(lane) or a.endswith(fleet) or a.endswith(lane + "/") or a.endswith(fleet + "/"):
                flag("V-RECURSIVE", "minor")
    return calls, found


def run(spec_path: Path, tdir: Path, lane: str) -> dict:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    report_dir = spec["reportDir"].rstrip("/")
    fleet = str(Path(lane).parent)
    ctx = str(spec.get("context", "")) + " " + str(spec.get("wave", ""))
    sm = re.search(r"souji-r\d+-", ctx)
    scratch_base = "/var/tmp/" + sm.group(0) if sm else "/var/tmp/"
    result = {"wave": spec.get("wave"), "lane": lane, "seats": {}, "missing_transcripts": []}
    for item in spec["items"]:
        name, role = item["name"], item["role"]
        f = tdir / f"{name}.txt"
        if not f.is_file():
            result["missing_transcripts"].append(name)
            continue
        report = f"{lane}/{report_dir}/{name}.md"
        # An item may grant its seat the named test command explicitly
        # (`ALLOWED-EXEC:` in the item prompt); it is then audited as an
        # executing seat, still bound by every other class.
        eff_role = "executor" if "ALLOWED-EXEC:" in item.get("prompt", "") else role
        calls, found = audit_seat(f.read_text(encoding="utf-8", errors="replace"), eff_role,
                                  report, owned_paths(item.get("prompt", "")), lane, fleet,
                                  scratch=scratch_base + name + "/")
        result["seats"][name] = {"role": role, "calls": calls, "violations": found}
    viol = [v for s in result["seats"].values() for v in s["violations"]]
    result["summary"] = {
        "seats_audited": len(result["seats"]),
        "calls": sum(s["calls"] for s in result["seats"].values()),
        "major": sum(v["severity"] == "major" for v in viol),
        "minor": sum(v["severity"] == "minor" for v in viol),
        "seats_with_major": sorted(n for n, s in result["seats"].items()
                                   if any(v["severity"] == "major" for v in s["violations"])),
    }
    return result


def selftest() -> int:
    lane = "/home/u/P/f/lane"
    rep = f"{lane}/.ufo/waves/round-9/w1/S.md"
    fleet = "/home/u/P/f"
    seat_scratch = "/var/tmp/souji-r9-S/"
    cases = [
        # (id, role, rendered line, exact [(class, severity), ...], scratch)
        ("clean-read", "reviewer", f"→ read({lane}/SKILL.md) ⇒ ok · 3 lines", [], None),
        ("report-write", "scribe", f"→ write({rep}) ⇒ ok · 2 lines", [], None),
        ("owned-write", "executor", f"→ write({lane}/tools/x.py) ⇒ ok · 2 lines", [], None),
        ("foreign-write", "scribe", f"→ write({lane}/SKILL.md) ⇒ ok · 2 lines", [("V-WRITE-SCOPE", "major")], None),
        ("sweep", "scout", f"→ read({lane}/census/operator-sweep-20261019/a.tsv) ⇒ ok", [("V-SURFACE", "major")], None),
        ("store", "scout", "→ bash(cat /home/u/.omp/agent/config.yml) ⇒ ok", [("V-SURFACE", "major")], None),
        ("rules-ok", "scout", "→ read(/home/u/.omp/agent/RULES.md) ⇒ ok", [], None),
        ("live-census", "executor", f"→ bash(bash {lane}/tools/souji-census.sh --root /home/u/P/f) ⇒ ok", [("V-LIVE-CENSUS", "major")], None),
        ("scratch-census", "executor", "→ bash(bash /var/tmp/x/souji-census.sh --root /var/tmp/w) ⇒ ok", [], None),
        ("reviewer-exec", "reviewer", f"→ bash(python3 {lane}/tests/fixtures/r15-census-config.py --tool x) ⇒ ok", [("V-EXEC", "major")], None),
        ("reviewer-bash-n", "reviewer", f"→ bash(bash -n {lane}/tools/souji-census.sh) ⇒ ok", [], None),
        ("executor-exec", "executor", f"→ bash(python3 {lane}/tools/g.py --selftest) ⇒ ok", [], None),
        ("recursive-find", "scout", f"→ bash(find {lane} -name x) ⇒ ok", [("V-PROBE", "minor"), ("V-RECURSIVE", "minor")], None),
        ("recursive-grep-tool", "reviewer", f"→ grep(foo in {lane}) ⇒ ok", [("V-RECURSIVE", "minor")], None),
        ("peer-message", "scout", "→ write(agent://L.S2) ⇒ ok", [], None),
        # Hashline headers resolve under lane or fleet; [tools/x.py] hits the
        # owned path under the lane root (LandingGate.txt:101 resolved there).
        ("edit-relative-owned", "executor", "→ edit([tools/x.py#AB12] PUT 1.=1: + y) ⇒ ok", [], None),
        # [SKILL.md] resolves under the lane root to the lane file, which is
        # out of scope: the unresolved-resolution class, not SCOPE.
        ("edit-relative-foreign", "executor", "→ edit([SKILL.md#AB12] PUT 1.=1: + y) ⇒ ok", [("V-WRITE-RELATIVE", "major")], None),
        ("shellcheck-not-exec", "reviewer", f"→ bash(shellcheck -s bash {lane}/tools/x.sh) ⇒ ok", [], None),
        ("pattern-word-not-surface", "reviewer", f"→ bash(git -C {lane} status | grep -v '^?? census/operator-sweep') ⇒ ok", [], None),
        # D4 r16 w2 rows: a bare relative edit is a fleet-root attempt (major,
        # failed or not); prose arguments are unparsed, minor on error.
        ("report-edit-relative-dotufo", "scribe", "→ edit(.ufo/waves/round-9/w1/S.md) ⇒ error · file absent", [("V-WRITE-RELATIVE", "major")], None),
        ("report-edit-table-prose", "scribe", "→ edit(| 2 | stale pin | 9 `files` pins: `tests/fixtures/r14-cache-frozen/expected.json` 2, `tests/fixtures/r13-cert-frozen/ex…) ⇒ error", [("V-WRITE-UNPARSED", "minor")], None),
        ("report-edit-sentence-prose", "scribe", "→ edit(N6 is the exact harm the r14 non-author closure rejected the round on (`corpus/lessons/round-14-verifier-spotcheck.md`,…) ⇒ error", [("V-WRITE-UNPARSED", "minor")], None),
        # D4: the r16 w1 real major (SrcGitNoLazyFetch.txt:144) stays major.
        ("edit-abs-foreign-placeholder", "scout", f"→ edit({lane}/.ufo/waves/round-9/r9-placeholder.md) ⇒ error · file absent", [("V-WRITE-SCOPE", "major")], None),
        # MutateSeatAudit.md survivor coverage (round-16 R16-M5 follow-on).
        ("state-path", "scout", f"→ read({lane}/.ufo/state/lane.round) ⇒ ok", [("V-SURFACE", "major")], None),
        ("reviewer-standalone-selftest", "reviewer", f"→ bash({lane}/tools/check --selftest) ⇒ ok", [("V-EXEC", "major")], None),
        ("reviewer-shell-exec", "reviewer", f"→ bash(bash {lane}/tools/x.sh) ⇒ ok", [("V-EXEC", "major")], None),
        ("foreign-write-report-as-content", "scribe", f"→ write({lane}/SKILL.md, {rep}) ⇒ ok", [("V-WRITE-SCOPE", "major")], None),
        ("edit-header-relative-owned", "executor", "→ edit(*** Begin Patch [tools/x.py#AB12] PUT 1.=1: + y) ⇒ ok", [], None),
        ("recursive-glob-tool", "reviewer", f"→ glob({lane}) ⇒ ok", [("V-RECURSIVE", "minor")], None),
        ("recursive-grep-root-slash", "reviewer", f"→ grep(foo in {lane}/) ⇒ ok", [("V-RECURSIVE", "minor")], None),
        # V-PROBE (R16-M5): find/strace/realpath/readlink over lane or fleet roots.
        ("probe-realpath-lane", "reviewer", f"→ bash(realpath {lane}/tools) ⇒ ok", [("V-PROBE", "minor")], None),
        ("probe-strace-fleet", "executor", "→ bash(strace -f stat /home/u/P/f) ⇒ ok", [("V-PROBE", "minor")], None),
        ("probe-readlink-scratch", "reviewer", "→ bash(readlink /var/tmp/x/link) ⇒ ok", [], None),
        ("probe-find-dot", "reviewer", "→ bash(find . -maxdepth 2 -name '*.md') ⇒ ok", [("V-PROBE", "minor"), ("V-RECURSIVE", "minor")], None),
        # H1–H8 held-out shapes (CriticC2Overclaim).
        ("h1-rel-write-ok", "scribe", "→ write(.ufo/waves/round-9/w1/S.md) ⇒ ok · 1 line", [("V-WRITE-RELATIVE", "major")], None),
        ("h2-bare-write-ok", "scribe", "→ write(S.md) ⇒ ok", [("V-WRITE-RELATIVE", "major")], None),
        ("h3-trunc-foreign-abs", "scribe", "→ write(/home/u/P/f/other/…) ⇒ ok", [("V-WRITE-SCOPE", "major")], None),
        ("h3b-trunc-header-foreign", "executor", "→ edit([/home/u/P/f/other/…) ⇒ ok", [("V-WRITE-SCOPE", "major")], None),
        ("h4-trunc-lane-report", "scribe", f"→ write({lane}/.ufo/waves/round-9/w1/S…) ⇒ ok", [("V-WRITE-UNPARSED", "major")], None),
        ("h5-unparsed-ok", "executor", "→ edit(| a | b |) ⇒ ok · 3 lines", [("V-WRITE-UNPARSED", "major")], None),
        ("h5b-unparsed-error", "executor", "→ edit(| a | b |) ⇒ error · Validation failed", [("V-WRITE-UNPARSED", "minor")], None),
        ("h6-multi-header", "executor", f"→ edit(*** Begin Patch [{rep}#AB12] PUT 1.=1: + x [{lane}/SKILL.md#CD34] PUT 2.=2: + y) ⇒ ok", [("V-WRITE-SCOPE", "major")], None),
        ("h7-dotdot-scratch", "scribe", "→ write(/var/tmp/../home/u/P/f/lane/SKILL.md) ⇒ ok", [("V-WRITE-SCOPE", "major")], None),
        ("h8-trunc-header-rel", "executor", "→ edit([tools/x.py#AB12] PUT 1.=1: + y [tools/…) ⇒ ok", [("V-WRITE-RELATIVE", "major")], None),
        # Seat-scoped scratch (contract: /var/tmp/souji-r<N>-<Seat>/ only).
        ("scratch-seat-write", "executor", "→ write(/var/tmp/souji-r9-S/out.txt) ⇒ ok", [], seat_scratch),
        ("scratch-other-seat", "executor", "→ write(/var/tmp/souji-r9-Other/out.txt) ⇒ ok", [("V-WRITE-SCOPE", "major")], seat_scratch),
        ("scratch-unscoped-executor", "executor", "→ write(/var/tmp/misc/out.txt) ⇒ ok", [], None),
        ("scratch-trunc-header", "executor", "→ edit([/var/tmp/souji-r…) ⇒ ok", [], seat_scratch),
    ]
    passed = failed = 0
    for cid, role, line, want, scratch in cases:
        sc = scratch if scratch is not None else "/var/tmp/"
        _, found = audit_seat(line, role, rep, [f"{lane}/tools/x.py"], lane, fleet, scratch=sc)
        got = sorted((v["class"], v["severity"]) for v in found)
        if got == sorted(want):
            passed += 1
            print(f"PASS\t{cid}")
        else:
            failed += 1
            print(f"FAIL\t{cid}\tgot={got}\twant={sorted(want)}")
    with tempfile.TemporaryDirectory(dir="/var/tmp") as td:
        spec = {"wave": "t", "reportDir": ".ufo/waves/round-9/w1",
                "items": [{"name": "S", "role": "scribe", "prompt": "x"}, {"name": "Gone", "role": "scout", "prompt": "y"}]}
        sp = Path(td) / "spec.json"
        sp.write_text(json.dumps(spec), encoding="utf-8")
        (Path(td) / "S.txt").write_text(f"→ write({lane}/SKILL.md) ⇒ ok\n", encoding="utf-8")
        r = run(sp, Path(td), lane)
        if r["summary"]["seats_with_major"] == ["S"] and r["missing_transcripts"] == ["Gone"]:
            passed += 1
            print("PASS\twave-summary")
        else:
            failed += 1
            print(f"FAIL\twave-summary\t{r['summary']}")
    print(f"SELFTEST\tpass={passed}\tfail={failed}")
    return 0 if failed == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec")
    ap.add_argument("--transcripts")
    ap.add_argument("--lane")
    ap.add_argument("--json")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.spec and a.transcripts and a.lane):
        print("souji-seat-audit: --spec, --transcripts and --lane are required", file=sys.stderr)
        return 2
    try:
        r = run(Path(a.spec), Path(a.transcripts), a.lane.rstrip("/"))
    except (OSError, ValueError, KeyError) as exc:
        print(f"souji-seat-audit: could not evaluate: {exc}", file=sys.stderr)
        return 2
    text = json.dumps(r, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    if a.json:
        out = Path(a.json)
        if out.exists():
            print(f"souji-seat-audit: refusing to overwrite {out}", file=sys.stderr)
            return 2
        out.write_text(text, encoding="utf-8")
    for name, s in sorted(r["seats"].items()):
        for v in s["violations"]:
            print(f"{v['severity']}\t{v['class']}\t{name}\t{v['tool']}\t{v['args'][:120]}")
    sm = r["summary"]
    print(f"SUMMARY\tseats={sm['seats_audited']}\tcalls={sm['calls']}\tmajor={sm['major']}\tminor={sm['minor']}\tmissing={len(r['missing_transcripts'])}")
    return 1 if sm["major"] else 0


if __name__ == "__main__":
    sys.exit(main())
