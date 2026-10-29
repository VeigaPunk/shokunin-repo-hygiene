#!/usr/bin/env python3
"""R42w3mutationtester02: single-point mutants of the landed C3 fixture
tests/fixtures/r42-drift-conditions.py at tip 6a3f75941d3604e3459011d599c2c16f3a97b44c.

Provenance:
  * Catalogue ids H*, D*, C*, W*, T*, X* are the wave-2 catalogue written by seat
    R42w2mutationtester03 (.ufo/waves/round-42/w2/R42w2mutationtester03/mutants.py).  They are
    REUSED here verbatim; the wave-2 grid (w2 grid.jsonl) is reused as a cross-check only.
  * Catalogue ids N* are NEW in wave 3: they attack the fixture from angles the wave-2 catalogue
    did not cover (per-case exit code, per-case argument value, per-case JSON key, the ROW
    constant, the drift_line text argument, the case-name list, the counter's own case count).

Every mutant is one (old, new) string replacement in the landed fixture blob, or one insertion
into the CASES filter (dropping a case from the run).  `build()` asserts that each replacement
hits exactly one place, so every mutant is provably single-point.

Categories: HELPER, ASSERT, TOKEN, COUNT, TIMING, DROP, ARG, KEY
"""

# (id, category, description, old, new)
MUTANTS = [
    # ---------------- HELPER: weaken the two shared predicates ----------------
    ("H01", "HELPER", "refused(): accept any exit code instead of exactly 2",
     'return p is not None and p.returncode == 2 and ("REFUSAL %s:" % cls) in p.stderr.decode("utf-8", "replace")',
     'return p is not None and p.returncode in (0, 1, 2) and ("REFUSAL %s:" % cls) in p.stderr.decode("utf-8", "replace")'),
    ("H02", "HELPER", "refused(): drop the REFUSAL-class token check, keep only rc==2",
     'return p is not None and p.returncode == 2 and ("REFUSAL %s:" % cls) in p.stderr.decode("utf-8", "replace")',
     'return p is not None and p.returncode == 2'),
    ("H03", "HELPER", "refused(): token check loses the trailing colon",
     '("REFUSAL %s:" % cls) in p.stderr.decode("utf-8", "replace")',
     '("REFUSAL %s" % cls) in p.stderr.decode("utf-8", "replace")'),
    ("H04", "HELPER", "drift_line(): accept any exit code instead of exactly 1",
     'return p is not None and p.returncode == 1 and text in p.stdout.decode("utf-8", "replace")',
     'return p is not None and p.returncode in (0, 1, 2) and text in p.stdout.decode("utf-8", "replace")'),
    ("H05", "HELPER", "drift_line(): drop the stdout token check, keep only rc==1",
     'return p is not None and p.returncode == 1 and text in p.stdout.decode("utf-8", "replace")',
     'return p is not None and p.returncode == 1'),
    ("H06", "HELPER", "drift_line(): stdout decoded with ignore instead of replace",
     'text in p.stdout.decode("utf-8", "replace")',
     'text in p.stdout.decode("utf-8", "ignore")'),

    # ---------------- ASSERT: a case's assertion replaced by True ----------------
    ("D01", "ASSERT", "fifo-record: remove the assertion (return True)",
     '    return refused(p, "RECORD-MALFORMED")', '    return True'),
    ("D02", "ASSERT", "root-sibling: remove the assertion (return True)",
     '    rec = put(out + "/rec", "REPO\\t../root2\\tregs=1\\tprunable=0\\n")\n'
     '    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded"])\n'
     '    return refused(p, "RECORD-OUTSIDE-ROOT")',
     '    rec = put(out + "/rec", "REPO\\t../root2\\tregs=1\\tprunable=0\\n")\n'
     '    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded"])\n'
     '    return True'),
    ("D03", "ASSERT", "gitdir-sibling: remove the assertion (return True)",
     '    rec = put(out + "/rec", "REPO\\ts\\tregs=1\\tprunable=0\\n")\n'
     '    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded"])\n'
     '    return refused(p, "RECORD-OUTSIDE-ROOT")',
     '    rec = put(out + "/rec", "REPO\\ts\\tregs=1\\tprunable=0\\n")\n'
     '    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded"])\n'
     '    return True'),
    ("D04", "ASSERT", "timeout-one: remove the assertion (return True)",
     '    return drift_line(p, "DRIFT\\tABSENT\\ta")', '    return True'),
    ("D05", "ASSERT", "default-timeout: remove the assertion (return True)",
     '    return drift_line(p, "DRIFT\\tUNREACHABLE\\tt\\tUNREACHABLE:list-timeout") and elapsed >= 5.0',
     '    return True'),
    ("D06", "ASSERT", "list-timeout: remove the assertion (return True)",
     '    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded", "--timeout", "1"], timeout=60)\n'
     '    return drift_line(p, "DRIFT\\tUNREACHABLE\\tt\\tUNREACHABLE:list-timeout")',
     '    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded", "--timeout", "1"], timeout=60)\n'
     '    return True'),
    ("D07", "ASSERT", "list-rc: remove the assertion (return True)",
     '    return drift_line(p, "DRIFT\\tUNREACHABLE\\tu\\tUNREACHABLE:list-rc=")', '    return True'),
    ("D08", "ASSERT", "root-option-required: remove the assertion (return True)",
     '    p, _ = c.tool_run(["--record", rec], cwd=out)\n'
     '    return p is not None and p.returncode == 2 and "required" in p.stderr.decode("utf-8", "replace")',
     '    p, _ = c.tool_run(["--record", rec], cwd=out)\n    return True'),
    ("D09", "ASSERT", "record-option-required: remove the assertion (return True)",
     '    p, _ = c.tool_run(["--root", root])\n'
     '    return p is not None and p.returncode == 2 and "required" in p.stderr.decode("utf-8", "replace")',
     '    p, _ = c.tool_run(["--root", root])\n    return True'),
    ("D10", "ASSERT", "symlinked-child: remove the assertion (return True)",
     '    return drift_line(p, "DRIFT\\tUNRECORDED\\tu2") and "UNRECORDED\\tlnk" not in text',
     '    return True'),
    ("D11", "ASSERT", "two-digit-regs: remove the assertion (return True)",
     '    return drift_line(p, "record=10 live=1")', '    return True'),
    ("D12", "ASSERT", "json-truncate: remove the assertion (return True)",
     '    return data.get("drift") == [] and "summary" in data', '    return True'),
    ("D13", "ASSERT", "invalid-utf8: remove the assertion (return True)",
     '    return [row.get("repo") for row in data.get("drift", [])] == ["a\\ufffdb"]',
     '    return True'),

    # ---------------- COUNT: weaken a count / drop a conjunct ----------------
    ("C01", "COUNT", "symlinked-child: drop the negative conjunct (UNRECORDED\\tlnk absent)",
     '    return drift_line(p, "DRIFT\\tUNRECORDED\\tu2") and "UNRECORDED\\tlnk" not in text',
     '    return drift_line(p, "DRIFT\\tUNRECORDED\\tu2")'),
    ("C02", "COUNT", "invalid-utf8: JSON repo list equality weakened to a length check",
     '    return [row.get("repo") for row in data.get("drift", [])] == ["a\\ufffdb"]',
     '    return len(data.get("drift", [])) == 1'),
    ("C03", "COUNT", "json-truncate: drift==[] weakened to drift is not None",
     '    return data.get("drift") == [] and "summary" in data',
     '    return data.get("drift") is not None and "summary" in data'),
    ("C04", "COUNT", "invalid-utf8: stdout token check weakened to a bare \\ufffd presence",
     '    if b"DRIFT\\tABSENT\\ta\\xef\\xbf\\xbdb\\t" not in p.stdout or b"\\\\xff" in p.stdout:',
     '    if b"\\xef\\xbf\\xbd" not in p.stdout or b"\\\\xff" in p.stdout:'),

    # ---------------- TIMING: widen a timing bound ----------------
    ("W01", "TIMING", "default-timeout: elapsed bound widened 5.0 s -> 0.5 s",
     '    return drift_line(p, "DRIFT\\tUNREACHABLE\\tt\\tUNREACHABLE:list-timeout") and elapsed >= 5.0',
     '    return drift_line(p, "DRIFT\\tUNREACHABLE\\tt\\tUNREACHABLE:list-timeout") and elapsed >= 0.5'),
    ("W02", "TIMING", "default-timeout: elapsed bound widened 5.0 s -> 0.0 s",
     '    return drift_line(p, "DRIFT\\tUNREACHABLE\\tt\\tUNREACHABLE:list-timeout") and elapsed >= 5.0',
     '    return drift_line(p, "DRIFT\\tUNREACHABLE\\tt\\tUNREACHABLE:list-timeout") and elapsed >= 0.0'),
    ("W03", "TIMING", "list-timeout: subprocess timeout widened 60 s -> 300 s",
     '    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded", "--timeout", "1"], timeout=60)',
     '    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded", "--timeout", "1"], timeout=300)'),
    ("W04", "TIMING", "fifo-record: subprocess timeout widened 25 s -> 300 s",
     '    p, _ = c.tool_run(["--root", root, "--record", out + "/rfifo", "--skip-unrecorded"], timeout=25)',
     '    p, _ = c.tool_run(["--root", root, "--record", out + "/rfifo", "--skip-unrecorded"], timeout=300)'),

    # ---------------- TOKEN: change an asserted token (strict; expected to break pristine) ----------
    ("T01", "TOKEN", "fifo-record: REFUSAL class token changed",
     '    return refused(p, "RECORD-MALFORMED")', '    return refused(p, "RECORD-MALFORMEDX")'),
    ("T02", "TOKEN", "root-sibling: REFUSAL class token changed",
     '    rec = put(out + "/rec", "REPO\\t../root2\\tregs=1\\tprunable=0\\n")\n'
     '    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded"])\n'
     '    return refused(p, "RECORD-OUTSIDE-ROOT")',
     '    rec = put(out + "/rec", "REPO\\t../root2\\tregs=1\\tprunable=0\\n")\n'
     '    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded"])\n'
     '    return refused(p, "RECORD-OUTSIDE-ROOTX")'),
    ("T03", "TOKEN", "timeout-one: DRIFT repo token changed",
     '    return drift_line(p, "DRIFT\\tABSENT\\ta")', '    return drift_line(p, "DRIFT\\tABSENT\\tb")'),
    ("T04", "TOKEN", "two-digit-regs: live count token changed",
     '    return drift_line(p, "record=10 live=1")', '    return drift_line(p, "record=10 live=2")'),
    ("T05", "TOKEN", "json-truncate: summary key token changed",
     '    return data.get("drift") == [] and "summary" in data',
     '    return data.get("drift") == [] and "summaryX" in data'),
    ("T06", "TOKEN", "symlinked-child: UNRECORDED repo token changed",
     '    return drift_line(p, "DRIFT\\tUNRECORDED\\tu2") and "UNRECORDED\\tlnk" not in text',
     '    return drift_line(p, "DRIFT\\tUNRECORDED\\tu3") and "UNRECORDED\\tlnk" not in text'),
    ("T07", "TOKEN", "root-option-required: stderr token changed",
     '    p, _ = c.tool_run(["--record", rec], cwd=out)\n'
     '    return p is not None and p.returncode == 2 and "required" in p.stderr.decode("utf-8", "replace")',
     '    p, _ = c.tool_run(["--record", rec], cwd=out)\n'
     '    return p is not None and p.returncode == 2 and "require" in p.stderr.decode("utf-8", "replace")'),

    # ---------------- N-series (NEW in wave 3): angles the wave-2 catalogue did not attack --------
    # N01: a case's own exit code, not the shared helper.
    ("N01", "ARG", "root-option-required: asserted exit code 2 -> 1",
     '    p, _ = c.tool_run(["--record", rec], cwd=out)\n'
     '    return p is not None and p.returncode == 2 and "required" in p.stderr.decode("utf-8", "replace")',
     '    p, _ = c.tool_run(["--record", rec], cwd=out)\n'
     '    return p is not None and p.returncode == 1 and "required" in p.stderr.decode("utf-8", "replace")'),
    # N02: the same for the record-option case.
    ("N02", "ARG", "record-option-required: asserted exit code 2 -> 0",
     '    p, _ = c.tool_run(["--root", root])\n'
     '    return p is not None and p.returncode == 2 and "required" in p.stderr.decode("utf-8", "replace")',
     '    p, _ = c.tool_run(["--root", root])\n'
     '    return p is not None and p.returncode == 0 and "required" in p.stderr.decode("utf-8", "replace")'),
    # N03: the timeout value the timeout-one case asks for (the G2/G3 boundary lives here).
    ("N03", "ARG", "timeout-one: the --timeout value the case asks for 1 -> 2",
     '    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded", "--timeout", "1"])',
     '    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded", "--timeout", "2"])'),
    # N04: the timeout value the list-timeout case asks for.
    ("N04", "ARG", "list-timeout: the --timeout value the case asks for 1 -> 0",
     '    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded", "--timeout", "1"], timeout=60)',
     '    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded", "--timeout", "0"], timeout=60)'),
    # N05: the ROW constant every record-shaped case writes.
    ("N05", "KEY", "ROW constant: prunable=0 -> prunable=1",
     'ROW = "REPO\\tr\\tregs=1\\tprunable=0\\n"', 'ROW = "REPO\\tr\\tregs=1\\tprunable=1\\n"'),
    # N06: the ROW constant's regs value.
    ("N06", "KEY", "ROW constant: regs=1 -> regs=2",
     'ROW = "REPO\\tr\\tregs=1\\tprunable=0\\n"', 'ROW = "REPO\\tr\\tregs=2\\tprunable=0\\n"'),
    # N07: the JSON key the truncate case reads.
    ("N07", "KEY", "json-truncate: the JSON key read changed drift -> driftlist",
     '    return data.get("drift") == [] and "summary" in data',
     '    return data.get("driftlist") == [] and "summary" in data'),
    # N08: the drift_line text argument of the json-truncate path is not used; instead weaken the
    # stdout-side summary check of the truncate case's sibling (the stdout token of the invalid-utf8 case).
    ("N08", "TOKEN", "invalid-utf8: the stdout token loses its trailing tab",
     '    if b"DRIFT\\tABSENT\\ta\\xef\\xbf\\xbdb\\t" not in p.stdout or b"\\\\xff" in p.stdout:',
     '    if b"DRIFT\\tABSENT\\ta\\xef\\xbf\\xbdb" not in p.stdout or b"\\\\xff" in p.stdout:'),
    # N09: the two-digit-regs case's record line (regs=10 -> regs=1).
    ("N09", "KEY", "two-digit-regs: the record written by the case regs=10 -> regs=1",
     '    rec = put(out + "/rec", "REPO\\tr\\tregs=10\\tprunable=0\\n")',
     '    rec = put(out + "/rec", "REPO\\tr\\tregs=1\\tprunable=0\\n")'),
    # N10: the invalid-utf8 record's byte payload.
    ("N10", "KEY", "invalid-utf8: the invalid byte \\xff replaced by \\xfe",
     '    rec = put(out + "/rec", b"REPO\\ta\\xffb\\tregs=1\\tprunable=0\\n")',
     '    rec = put(out + "/rec", b"REPO\\ta\\xfeb\\tregs=1\\tprunable=0\\n")'),
    # N11: the old-json filler length that makes truncation observable.
    ("N11", "COUNT", "json-truncate: old json filler shortened 5000 -> 5 bytes",
     '    target = put(out + "/old.json", "x" * 5000)', '    target = put(out + "/old.json", "x" * 5)'),
    # N12: the case whose whole scenario is dropped from the run list (a second DROP shape).
    ("N12", "TOKEN", "default-timeout: the UNREACHABLE reason token changed",
     '    return drift_line(p, "DRIFT\\tUNREACHABLE\\tt\\tUNREACHABLE:list-timeout") and elapsed >= 5.0',
     '    return drift_line(p, "DRIFT\\tUNREACHABLE\\tt\\tUNREACHABLE:list-timeoutX") and elapsed >= 5.0'),
    # N13: the list-rc reason token.
    ("N13", "TOKEN", "list-rc: the reason token changed",
     '    return drift_line(p, "DRIFT\\tUNREACHABLE\\tu\\tUNREACHABLE:list-rc=")',
     '    return drift_line(p, "DRIFT\\tUNREACHABLE\\tu\\tUNREACHABLE:list-rcX=")'),
    # N14: the fifo case's --skip-unrecorded flag dropped (the scenario changes, not the assertion).
    ("N14", "ARG", "fifo-record: --skip-unrecorded dropped from the tool invocation",
     '    p, _ = c.tool_run(["--root", root, "--record", out + "/rfifo", "--skip-unrecorded"], timeout=25)',
     '    p, _ = c.tool_run(["--root", root, "--record", out + "/rfifo"], timeout=25)'),
    # N15: the root-sibling case's --skip-unrecorded flag dropped.
    ("N15", "ARG", "root-sibling: --skip-unrecorded dropped from the tool invocation",
     '    rec = put(out + "/rec", "REPO\\t../root2\\tregs=1\\tprunable=0\\n")\n'
     '    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded"])\n'
     '    return refused(p, "RECORD-OUTSIDE-ROOT")',
     '    rec = put(out + "/rec", "REPO\\t../root2\\tregs=1\\tprunable=0\\n")\n'
     '    p, _ = c.tool_run(["--root", root, "--record", rec])\n'
     '    return refused(p, "RECORD-OUTSIDE-ROOT")'),
    # N16: the symlinked-child case's tool invocation loses --skip-unrecorded.
    ("N16", "ARG", "symlinked-child: --skip-unrecorded dropped from the tool invocation",
     '    p, _ = c.tool_run(["--root", root, "--record", rec])',
     '    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded"])'),
    # N17: the elapsed bound narrowed instead of widened (5.0 -> 30.0): the default allowance must
    # be long enough that the case still passes on the pinned tool.
    ("N17", "TIMING", "default-timeout: elapsed bound narrowed 5.0 s -> 30.0 s",
     '    return drift_line(p, "DRIFT\\tUNREACHABLE\\tt\\tUNREACHABLE:list-timeout") and elapsed >= 5.0',
     '    return drift_line(p, "DRIFT\\tUNREACHABLE\\tt\\tUNREACHABLE:list-timeout") and elapsed >= 30.0'),
    # N18: the drift_line text argument of the timeout-one case, prefix form.
    ("N18", "TOKEN", "timeout-one: the DRIFT line matched with the tab prefix dropped",
     '    return drift_line(p, "DRIFT\\tABSENT\\ta")', '    return drift_line(p, "DRIFT\\tABSENT")'),
    # N19: the gitdir-sibling case's gitlink target name.
    ("N19", "KEY", "gitdir-sibling: the gitlink target name gd2 -> gd3",
     '    put(root + "/s/.git", "gitdir: " + w + "/rootX/gd2\\n")',
     '    put(root + "/s/.git", "gitdir: " + w + "/rootX/gd3\\n")'),
    # N20: the two-digit-regs assertion loosened to the record half only.
    ("N20", "COUNT", "two-digit-regs: the live count conjunct dropped",
     '    return drift_line(p, "record=10 live=1")', '    return drift_line(p, "record=10")'),
    # N21: the exit code the json-truncate case expects of the tool.
    ("N21", "ARG", "json-truncate: the expected tool exit code 0 -> 1",
     '    if p is None or p.returncode != 0:\n        return False',
     '    if p is None or p.returncode != 1:\n        return False'),
    # N22: the exit code the invalid-utf8 case expects of the tool.
    ("N22", "ARG", "invalid-utf8: the expected tool exit code 1 -> 2",
     '    if p is None or p.returncode != 1:\n        return False',
     '    if p is None or p.returncode != 2:\n        return False'),
    # N23: the SUMMARY line's fail count (the counter's killed() reads fail>0).
    ("N23", "COUNT", "SUMMARY: the reported fail count pinned to 0",
     '        print("SUMMARY cases=%d pass=%d fail=%d" % (len(CASES), len(CASES) - bad, bad))',
     '        print("SUMMARY cases=%d pass=%d fail=%d" % (len(CASES), len(CASES) - bad, 0))'),
    # N24: the SUMMARY line's pass count (the counter's clean() reads pass==cases).
    ("N24", "COUNT", "SUMMARY: the reported pass count pinned to the case count",
     '        print("SUMMARY cases=%d pass=%d fail=%d" % (len(CASES), len(CASES) - bad, bad))',
     '        print("SUMMARY cases=%d pass=%d fail=%d" % (len(CASES), len(CASES), bad))'),
]

# DROP: drop one case from the run by excluding it in the CASES comprehension.
DROP_CASES = [
    "case_fifo_record_is_refused_not_blocked",
    "case_root_sibling_prefix_is_outside",
    "case_gitdir_sibling_prefix_is_outside",
    "case_timeout_of_one_is_accepted",
    "case_default_timeout_outlasts_a_blocked_git",
    "case_list_timeout_is_reported_unreachable",
    "case_list_nonzero_rc_is_reported_unreachable",
    "case_root_option_is_required",
    "case_record_option_is_required",
    "case_symlinked_child_is_not_discovered",
    "case_two_digit_regs_are_read_whole",
    "case_longer_old_json_is_truncated_on_write",
    "case_invalid_utf8_in_record_becomes_replacement_char",
]

# DROP2: drop a PAIR of cases at once.  The BASE grid shows G2 is killed by two cases
# (timeout-of-one-accepted and list-timeout-is-reported-unreachable) and G4 by two cases
# (default-timeout-outlasts-a-blocked-git and list-timeout-is-reported-unreachable).  These
# mutants test whether a case that is individually redundant is still needed once its partner
# is also removed -- i.e. whether the redundancy is mutual rather than absolute.
DROP_PAIRS = [
    ("P01", ("case_timeout_of_one_is_accepted", "case_list_timeout_is_reported_unreachable"),
     "drop BOTH cases that kill G2"),
    ("P02", ("case_default_timeout_outlasts_a_blocked_git", "case_list_timeout_is_reported_unreachable"),
     "drop BOTH cases that kill G4"),
    ("P03", ("case_timeout_of_one_is_accepted", "case_default_timeout_outlasts_a_blocked_git"),
     "drop timeout-of-one together with default-timeout"),
]


def build(src):
    out = {}
    for mid, cat, desc, old, new in MUTANTS:
        n = src.count(old)
        if n != 1:
            raise SystemExit("mutant %s: old string occurs %d times (expected 1)" % (mid, n))
        out[mid] = {"category": cat, "description": desc, "source": src.replace(old, new, 1),
                    "old": old, "new": new}
    anchor = 'if name.startswith("case_") and callable(fn)]'
    if src.count(anchor) != 1:
        raise SystemExit("CASES anchor occurs %d times" % src.count(anchor))
    for i, name in enumerate(DROP_CASES, 1):
        mid = "X%02d" % i
        out[mid] = {"category": "DROP", "description": "drop case %s from the run" % name,
                    "source": src.replace(anchor,
                                          'if name.startswith("case_") and callable(fn) and name != "%s"]' % name, 1),
                    "old": anchor, "new": name}
    for mid, names, desc in DROP_PAIRS:
        filt = "".join(' and name != "%s"' % n for n in names)
        out[mid] = {"category": "DROP2", "description": desc,
                    "source": src.replace(anchor,
                                          'if name.startswith("case_") and callable(fn)%s]' % filt, 1),
                    "old": anchor, "new": ",".join(names)}
    return out


if __name__ == "__main__":
    import subprocess
    lane = "/home/vgpnk/Projects/shokunin/souji-shokunin"
    tip = "6a3f75941d3604e3459011d599c2c16f3a97b44c"
    s = subprocess.run(["git", "-C", lane, "show", "%s:tests/fixtures/r42-drift-conditions.py" % tip],
                       stdout=subprocess.PIPE, check=True).stdout.decode("utf-8")
    m = build(s)
    print("mutants: %d" % len(m))
    for k, v in sorted(m.items()):
        compile(v["source"], k, "exec")
    print("all mutants compile")
