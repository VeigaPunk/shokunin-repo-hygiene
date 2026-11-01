#!/usr/bin/env python
"""census/round-50/c1-counter.py — r50 C1 (calibration): the S267 token-count
readings re-derivable by committed command.

Claim (r49 non-author closure routed defect 1). The r49 S267 re-open receipt
stated "the page makes zero occurrences of 'factual' and zero of 'histor*'" —
exact for the page content, but the raw page bytes carry one footer occurrence
("History and License" inside the site-chrome footer div) — and no committed
command could re-derive either reading, so a raw grep contradicted the record
as written. The repair lands two things: (a) the counting instrument
`tools/souji-page-token-count.py` (content area versus raw bytes, method named
in every record), and (b) the append-only erratum naming the method and the
command, grounded on the committed page capture. This counter reads, at the
round tip (exit 0):

  SUMMARY reading=ok footer=ok body=ok erratum=ok sourced=ok selftest=ok
          content_histor=<n> raw_histor=<n> content_factual=<n> raw_factual=<n>
          tool_sha=<12hex>

with content_histor=0, raw_histor>=1, content_factual=0, raw_factual=0 — and
reads TOOL-ABSENT (exit 1) at the round base, where none of these blobs exist
(the do-nothing control `census/round-50/controls/c1-control-donothing.txt`).
The SAME counter measures both ends; the world (the lane's committed bytes)
moves, not the instrument — the r45 different-instrument limit does not apply.

Legs over the lane's committed bytes at --rev (git object store only, never
the work tree):
  reading   the extracted tool over the committed page capture
            census/round-50/sources/s267-stdtypes-capture.html: token "histor"
            must read SCOPE-CONTENT-MATCHES=0 with SCOPE-RAW-MATCHES>=1 (the
            record's zero is a content-scope zero; the raw scope carries the
            footer occurrence) and token "factual" must read 0/0
  footer    the committed fixture census/round-50/c1-footer-fixture.html (the
            token only inside a class~=footer div): content=0, raw>=1 — the
            instrument reproduces the exact distinction the erratum names
  body      the committed fixture census/round-50/c1-body-fixture.html (the
            token in body text): content>=1 and raw>=1 — the instrument is
            not an always-zero emitter
  erratum   corpus/lessons/round-50.md at --rev carries a line beginning
            S267-COUNT-ERRATUM naming the instrument command
  sourced   corpus/SOURCES.md at --rev carries the S273 row (the html.parser
            contract grounding the content scope)
  selftest  the extracted tool's --selftest exits 0 printing
            SELFTEST cases=N pass=N fail=0 with N >= 6

CLI:
  python -B census/round-50/c1-counter.py --root LANE --rev FULL40 --scratch DIR
Exit: 0 target met; 1 target unmet; 2 could-not-evaluate. All scratch (the
extracted tool, capture and fixtures) lives under --scratch; nothing is
written inside the repo. The counter itself writes no digest-bound fixture
bytes and launches the extracted tool with sys.executable (no `python3`
interpreter-name dependency; this host has none). Python stdlib only; the
reading leg runs fully offline over committed bytes.
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

REV = re.compile(r"^[0-9a-f]{40}$")
TOOL_PATH = "tools/souji-page-token-count.py"
CAPTURE_PATH = "census/round-50/sources/s267-stdtypes-capture.html"
FOOTER_FIXTURE = "census/round-50/c1-footer-fixture.html"
BODY_FIXTURE = "census/round-50/c1-body-fixture.html"
LESSON_PATH = "corpus/lessons/round-50.md"
SOURCES_PATH = "corpus/SOURCES.md"
RECORD_RE = re.compile(r"^SCOPE-RAW-MATCHES=(\d+)$", re.M), re.compile(r"^SCOPE-CONTENT-MATCHES=(\d+)$", re.M)
SELFTEST_RE = re.compile(r"^SELFTEST cases=(\d+) pass=(\d+) fail=(\d+)\s*$", re.M)


def env(work):
    return {"PATH": os.environ.get("PATH", ""), "TMPDIR": work, "LC_ALL": "C",
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}


def git(root, args, envp):
    return subprocess.run(["git", "-C", root] + args, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, env=envp, check=False)


def run_tool(tool, argv, tmp_dir):
    try:
        p = subprocess.run([sys.executable, "-B", tool] + argv, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True, check=False, env=env(tmp_dir),
                           timeout=300)
    except subprocess.TimeoutExpired:
        return 124, "", True
    crash = "Traceback (most recent call last)" in p.stderr
    return p.returncode, p.stdout, crash


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--tool", default=TOOL_PATH)
    ap.add_argument("--scratch", required=True)
    args = ap.parse_args(argv)
    if not REV.match(args.rev):
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --rev must be a full 40-hex commit id\n")
        return 2
    if not os.path.isdir(args.root) or not os.path.isdir(args.scratch):
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --root and --scratch must name directories\n")
        return 2
    envp = env(args.scratch)
    chk = git(args.root, ["cat-file", "-e", args.rev + "^{commit}"], envp)
    if chk.returncode != 0:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --rev does not resolve in %s\n" % args.root)
        return 2

    def blob(path):
        p = git(args.root, ["show", "%s:%s" % (args.rev, path)], envp)
        return p.stdout if p.returncode == 0 else None

    def text_at(path):
        data = blob(path)
        return data.decode("utf-8", "replace") if data is not None else None

    work = tempfile.mkdtemp(prefix="souji-r50-c1.", dir=args.scratch)
    # The tool computes its lane-root refusal boundary from its own location
    # (dirname(dirname(__file__)) — for the extracted tool, `work`): extract
    # it under a `tools/` subtree and keep TMPDIR in a SIBLING tree under
    # --scratch, so the Q66 refusal does not fire on the counter's own
    # scratch layout.
    tools_dir = os.path.join(work, "tools")
    os.makedirs(tools_dir)
    tmp_dir = tempfile.mkdtemp(prefix="souji-r50-c1-tmp.", dir=args.scratch)
    try:
        tool_bytes = blob(args.tool)
        if tool_bytes is None:
            print("PRISTINE FAIL TOOL-ABSENT %s at %s" % (args.tool, args.rev))
            print("SUMMARY reading=FAIL footer=FAIL body=FAIL erratum=FAIL sourced=FAIL "
                  "selftest=FAIL tool_sha=absent")
            return 1
        tool = os.path.join(tools_dir, "souji-page-token-count.py")
        with open(tool, "wb") as handle:
            handle.write(tool_bytes)
        tool_sha = hashlib.sha256(tool_bytes).hexdigest()[:12]

        results = {}

        capture_bytes = blob(CAPTURE_PATH)
        capture_path = os.path.join(work, "capture.html")
        if capture_bytes is not None:
            with open(capture_path, "wb") as handle:
                handle.write(capture_bytes)
            rc, out, crash = run_tool(tool, ["--capture", capture_path, "--token", "histor"], tmp_dir)
            m_raw, m_content = RECORD_RE
            raw_m = m_raw.search(out) if rc == 0 else None
            content_m = m_content.search(out) if rc == 0 else None
            raw_h = int(raw_m.group(1)) if raw_m else -1
            content_h = int(content_m.group(1)) if content_m else -1
            rc_f, out_f, crash_f = run_tool(tool, ["--capture", capture_path, "--token", "factual"], tmp_dir)
            raw_f = int(m_raw.search(out_f).group(1)) if rc_f == 0 and m_raw.search(out_f) else -1
            content_f = int(m_content.search(out_f).group(1)) if rc_f == 0 and m_content.search(out_f) else -1
            results["reading"] = (rc == 0 and not crash and rc_f == 0 and not crash_f
                                  and content_h == 0 and raw_h >= 1
                                  and content_f == 0 and raw_f == 0)
            results["counts"] = (content_h, raw_h, content_f, raw_f)
        else:
            results["reading"] = False
            results["counts"] = (-1, -1, -1, -1)

        for name, fixture, want_content_exact in (("footer", FOOTER_FIXTURE, 0),
                                                  ("body", BODY_FIXTURE, None)):
            data = blob(fixture)
            ok = False
            if data is not None:
                fpath = os.path.join(work, os.path.basename(fixture))
                with open(fpath, "wb") as handle:
                    handle.write(data)
                rc, out, crash = run_tool(tool, ["--capture", fpath, "--token", "histor"], tmp_dir)
                m_raw, m_content = RECORD_RE
                rm = m_raw.search(out) if rc == 0 else None
                cm = m_content.search(out) if rc == 0 else None
                if rc == 0 and not crash and rm is not None and cm is not None:
                    raw_val = int(rm.group(1))
                    content_val = int(cm.group(1))
                    content_ok = (content_val == want_content_exact
                                  if want_content_exact is not None
                                  else content_val >= 1)
                    ok = content_ok and raw_val >= 1
            results[name] = ok

        lesson = text_at(LESSON_PATH) or ""
        results["erratum"] = any(
            line.startswith("S267-COUNT-ERRATUM") and "tools/souji-page-token-count.py" in line
            for line in lesson.splitlines())

        sources = text_at(SOURCES_PATH) or ""
        results["sourced"] = ("| S273 |" in sources and "html.parser" in sources)

        rc, out, crash = run_tool(tool, ["--selftest"], tmp_dir)
        m = SELFTEST_RE.findall(out)
        results["selftest"] = (rc == 0 and not crash and bool(m)
                               and int(m[-1][0]) >= 6 and m[-1][0] == m[-1][1] and m[-1][2] == "0")

        content_h, raw_h, content_f, raw_f = results["counts"]
        verdicts = {k: ("ok" if results[k] else "FAIL")
                    for k in ("reading", "footer", "body", "erratum", "sourced", "selftest")}
        print("SUMMARY reading=%s footer=%s body=%s erratum=%s sourced=%s selftest=%s "
              "content_histor=%d raw_histor=%d content_factual=%d raw_factual=%d tool_sha=%s"
              % (verdicts["reading"], verdicts["footer"], verdicts["body"], verdicts["erratum"],
                 verdicts["sourced"], verdicts["selftest"], content_h, raw_h, content_f, raw_f,
                 tool_sha))
        met = all(results[k] for k in ("reading", "footer", "body", "erratum", "sourced", "selftest"))
        return 0 if met else 1
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
