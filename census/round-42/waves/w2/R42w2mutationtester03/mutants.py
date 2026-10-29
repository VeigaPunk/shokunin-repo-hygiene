#!/usr/bin/env python3
"""R42w2mutationtester03: single-point mutants of the landed C3 fixture.

Every mutant is one (old, new) string replacement in the landed fixture blob, or one
insertion into the CASES filter (dropping a case from the run).  `build()` asserts that
each replacement hits exactly one place, so every mutant is provably single-point.
"""

# (id, category, description, old, new)
# Categories: HELPER, ASSERT, TOKEN, COUNT, TIMING, DROP
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
    return out


if __name__ == "__main__":
    import subprocess
    lane = "/home/vgpnk/Projects/shokunin/souji-shokunin"
    tip = "3105a63b23481fccf7df58e74d14a6681e0ea0c8"
    s = subprocess.run(["git", "-C", lane, "show", "%s:tests/fixtures/r42-drift-conditions.py" % tip],
                       stdout=subprocess.PIPE, check=True).stdout.decode("utf-8")
    m = build(s)
    print("mutants: %d" % len(m))
    for k, v in sorted(m.items()):
        compile(v["source"], k, "exec")
    print("all mutants compile")
