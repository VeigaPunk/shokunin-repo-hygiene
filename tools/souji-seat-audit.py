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
                        one of its OWNED files, nor under /var/tmp
  major  V-EXEC         a non-executor/non-mutation-tester seat runs a lane tool,
                        fixture or --selftest (bash -n / py_compile / ast exempt)
  minor  V-RECURSIVE    find/grep -r/rg/ls -R or a grep/glob tool call rooted at
                        the lane root or the fleet root

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
EDIT_TARGET_RE = re.compile(r"^(?:\*\*\* Begin Patch\s*)?\[([^\]#]+)(?:#[0-9A-Fa-f]+)?\]")
RECURSIVE_BASH_RE = re.compile(r"(?:^|[;&|]\s*)(?:find\s|rg\s|grep\s+-\w*r|ls\s+-\w*R)")
OWN_RE = re.compile(r"OWN ONLY ([^\n]+?)(?:\s\(|\.\s|$)")
ABS_RE = re.compile(r"/home/[^\s,`'\"]+")
WRITE_TOOLS = {"write", "edit", "ast_edit"}
EXEC_ROLES = {"executor", "mutation-tester"}


def owned_paths(prompt: str) -> list[str]:
    out: list[str] = []
    for m in OWN_RE.finditer(prompt):
        out.extend(p.rstrip(".,;:)") for p in ABS_RE.findall(m.group(1)))
    return out


def write_target(args: str) -> str:
    a = args.strip()
    m = EDIT_TARGET_RE.match(a)
    if m:
        return m.group(1).strip()
    return a.split(",", 1)[0].strip()


def allowed_target(target: str, allowed: list[str]) -> bool:
    """Rendered targets may be absolute or relative to the session root."""
    if target.startswith("/var/tmp/"):
        return True
    rel = target.lstrip("./")
    return any(target == p or p.endswith("/" + rel) for p in allowed)


def audit_seat(text: str, role: str, report: str, owned: list[str], lane: str, fleet: str) -> tuple[int, list[dict]]:
    calls = 0
    found: list[dict] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        # Exports through the read tool prefix each line with `N:`.
        m = CALL_RE.match(LINE_NO_RE.sub("", line, count=1))
        if not m:
            continue
        calls += 1
        tool, args = m.group(1), m.group(2)

        def flag(cls: str, sev: str) -> None:
            found.append({"class": cls, "severity": sev, "line": lineno, "tool": tool, "args": args[:200]})

        if SURFACE_RE.search(args):
            flag("V-SURFACE", "major")
        if tool == "bash" and LIVE_CENSUS_RE.search(args):
            flag("V-LIVE-CENSUS", "major")
        if tool in WRITE_TOOLS:
            target = write_target(args)
            if target.startswith("agent://"):
                pass  # peer message, not a file write
            elif not target:
                flag("V-WRITE-UNKNOWN", "minor")
            elif not allowed_target(target, [report, *owned]):
                flag("V-WRITE-SCOPE", "major")
        if tool == "bash" and role not in EXEC_ROLES and EXEC_RE.search(args):
            flag("V-EXEC", "major")
        if tool == "bash" and RECURSIVE_BASH_RE.search(args) and (lane in args or fleet in args or " . " in args):
            flag("V-RECURSIVE", "minor")
        if tool in {"grep", "glob"}:
            a = args.rstrip("…").rstrip()
            if a.endswith(lane) or a.endswith(fleet) or a.endswith(lane + "/") or a.endswith(fleet + "/"):
                flag("V-RECURSIVE", "minor")
    return calls, found


def run(spec_path: Path, tdir: Path, lane: str) -> dict:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    report_dir = spec["reportDir"].rstrip("/")
    fleet = str(Path(lane).parent)
    result = {"wave": spec.get("wave"), "lane": lane, "seats": {}, "missing_transcripts": []}
    for item in spec["items"]:
        name, role = item["name"], item["role"]
        f = tdir / f"{name}.txt"
        if not f.is_file():
            result["missing_transcripts"].append(name)
            continue
        report = f"{lane}/{report_dir}/{name}.md"
        calls, found = audit_seat(f.read_text(encoding="utf-8", errors="replace"), role,
                                  report, owned_paths(item.get("prompt", "")), lane, fleet)
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
    cases = [
        ("clean-read", "reviewer", f"→ read({lane}/SKILL.md) ⇒ ok · 3 lines", []),
        ("report-write", "scribe", f"→ write({rep}) ⇒ ok · 2 lines", []),
        ("owned-write", "executor", f"→ write({lane}/tools/x.py) ⇒ ok · 2 lines", []),
        ("foreign-write", "scribe", f"→ write({lane}/SKILL.md) ⇒ ok · 2 lines", ["V-WRITE-SCOPE"]),
        ("sweep", "scout", f"→ read({lane}/census/operator-sweep-20261019/a.tsv) ⇒ ok", ["V-SURFACE"]),
        ("store", "scout", "→ bash(cat /home/u/.omp/agent/config.yml) ⇒ ok", ["V-SURFACE"]),
        ("rules-ok", "scout", "→ read(/home/u/.omp/agent/RULES.md) ⇒ ok", []),
        ("live-census", "executor", f"→ bash(bash {lane}/tools/souji-census.sh --root /home/u/P/f) ⇒ ok", ["V-LIVE-CENSUS"]),
        ("scratch-census", "executor", "→ bash(bash /var/tmp/x/souji-census.sh --root /var/tmp/w) ⇒ ok", []),
        ("reviewer-exec", "reviewer", f"→ bash(python3 {lane}/tests/fixtures/r15-census-config.py --tool x) ⇒ ok", ["V-EXEC"]),
        ("reviewer-bash-n", "reviewer", f"→ bash(bash -n {lane}/tools/souji-census.sh) ⇒ ok", []),
        ("executor-exec", "executor", f"→ bash(python3 {lane}/tools/g.py --selftest) ⇒ ok", []),
        ("recursive-find", "scout", f"→ bash(find {lane} -name x) ⇒ ok", ["V-RECURSIVE"]),
        ("recursive-grep-tool", "reviewer", f"→ grep(foo in {lane}) ⇒ ok", ["V-RECURSIVE"]),
        ("peer-message", "scout", "→ write(agent://L.S2) ⇒ ok", []),
        ("edit-relative-owned", "executor", "→ edit([tools/x.py#AB12] PUT 1.=1: + y) ⇒ ok", []),
        ("edit-relative-foreign", "executor", "→ edit([SKILL.md#AB12] PUT 1.=1: + y) ⇒ ok", ["V-WRITE-SCOPE"]),
        ("shellcheck-not-exec", "reviewer", f"→ bash(shellcheck -s bash {lane}/tools/x.sh) ⇒ ok", []),
        ("pattern-word-not-surface", "reviewer", f"→ bash(git -C {lane} status | grep -v '^?? census/operator-sweep') ⇒ ok", []),
    ]
    passed = failed = 0
    for cid, role, line, want in cases:
        _, found = audit_seat(line, role, rep, [f"{lane}/tools/x.py"], lane, "/home/u/P/f")
        got = sorted({v["class"] for v in found})
        if got == sorted(want):
            passed += 1
            print(f"PASS\t{cid}")
        else:
            failed += 1
            print(f"FAIL\t{cid}\tgot={got}\twant={want}")
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
