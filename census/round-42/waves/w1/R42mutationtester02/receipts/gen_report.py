import os, re
S = "/fast/scratch/hyaku/souji-r42/R42mutationtester02"
OUT = S + "/out"
W = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42mutationtester02"
ids = [l.split("\t")[0] for l in open(W + "/mutants/manifest.tsv", encoding="utf-8").read().splitlines()[1:] if l.strip()]
man = {l.split("\t")[0]: l.split("\t") for l in open(W + "/mutants/manifest.tsv", encoding="utf-8").read().splitlines()[1:] if l.strip()}
def rd(p):
    return open(p, encoding="utf-8", errors="replace").read()
def parse(text):
    cases, summ, other, rc = {}, None, {}, None
    for line in text.splitlines():
        if line.startswith("case-"):
            k, v = line.split("=", 1); cases[k] = v
        elif line.startswith("SUMMARY"):
            summ = dict(re.findall(r"(\w+)=(\S+)", line))
        elif re.match(r"^(real|retro|retro_clean|selftest) ", line):
            other[line.split(" ")[0]] = line.split(" ")[1]
        elif line.startswith("PRISTINE"):
            other["PRISTINE"] = "present"
    return cases, summ, other
def fields(tag, base_tag):
    b = rd(f"{OUT}/{base_tag}.out"); m = rd(f"{OUT}/{tag}.out")
    brc = rd(f"{OUT}/{base_tag}.rc").strip(); mrc = rd(f"{OUT}/{tag}.rc").strip()
    bc, bs, bo = parse(b); mc, ms, mo = parse(m)
    f, kind = [], set()
    if brc != mrc: f.append("exit %s->%s" % (brc, mrc)); kind.add("verdict")
    if ms is None:
        f.append("no SUMMARY (output replaced: traceback/abort)"); kind.add("verdict")
    else:
        for k in sorted(set(bs or {}) | set(ms)):
            if (bs or {}).get(k) != ms.get(k):
                f.append("SUMMARY." + k); kind.add("verdict" if k not in ("tool_sha",) else "text")
    if not mc and bc:
        f.append("case lines suppressed"); kind.add("text")
    flips = [k for k in bc if k in mc and bc[k].split(" ")[0] != mc[k].split(" ")[0]]
    dets = [k for k in bc if k in mc and bc[k].split(" ")[0] == mc[k].split(" ")[0] and bc[k] != mc[k]]
    if flips: f.append("case verdict flips x%d (%s)" % (len(flips), flips[0])); kind.add("verdict")
    if dets: f.append("case detail x%d (%s)" % (len(dets), dets[0])); kind.add("text")
    for k in ("real", "retro", "retro_clean", "selftest"):
        if k in bo and k in mo and bo[k] != mo[k]: f.append(k); kind.add("verdict")
    return f, kind
NOTES = {
"M01": "digest algorithm change breaks every digest-bearing claim (40-hex digest fails grammar)",
"M02": "EQUIV: all digested fixtures (COUNTER, POPULATION constants) are ASCII; encoding never differs",
"M03": "tool scopes dispatch files by the Round: line; round-41 default flips dispatch-before-freeze",
"M04": "empty Round: value -> FIELD-MISSING C0 Round on every fixture",
"M05": "claim headings numbered n+1; expected C1 labels no longer appear",
"M06": "EQUIV: heading tail after `## C<digits>` is not read by the tool",
"M07": "Kill key never written -> FIELD-MISSING on every clean fixture",
"M08": "EQUIV: no claim value is None (drop/blank use pop/assignment)",
"M09": "NAMED LIMIT NL-SPACING: Key:value without space is accepted by the tool; no case pins it",
"M10": "NAMED LIMIT NL-SPACING: blank lines inside a claim block are accepted; no case pins it",
"M11": "crash: __extra default None raises TypeError in every fixture (no output)",
"M12": "Counter digest taken from population -> COUNTER-DIGEST on clean",
"M13": "NAMED LIMIT NL-SPACING: double space before sha256= accepted by `[ \\t]+`; no case pins it",
"M14": "NAMED LIMIT NL-VALUE: Target value is never read by the tool or the counter",
"M15": "Control path missing -> CONTROL-MISSING on clean",
"M16": "EQUIV: any non-matching digest gives the same COUNTER-DIGEST class",
"M17": "EQUIV: any non-matching digest gives the same POPULATION-DIGEST class",
"M18": "inverted population override -> KeyError crash in clean fixture",
"M19": "NAMED LIMIT NL-FIELDNAME: missing key is compared by class only; run_tool keeps claim+class, not the key",
"M20": "two-claims order swapped -> C1 FIELD-MISSING where C2 is expected",
"M21": "COUNTER-MISSING on clean fixture",
"M22": "no-op 'edit' makes git commit fail -> RuntimeError (output replaced)",
"M23": "dispatch file written outside round-42 path; base no longer sees it",
"M24": "NAMED LIMIT NL-BASERED: wave-file path change in dispatch-*-before fixtures; base and stub are FAIL there with identical detail, so the fixture change is invisible to scored tools",
"M25": "branch name clash -> checkout fails -> crash",
"M26": "base-not-ancestor claim uses an ancestor base -> case flips PASS->FAIL",
"M27": "EQUIV: any unresolvable sha yields BASE-UNRESOLVED",
"M28": "tip returned as freeze commit: frozen-edited fixtures no longer see the edit",
"M29": "EQUIV: KEY-DUPLICATE is defined by key repetition alone (value-independent); the sentinel does not change the class",
"M30": "green receipt as default control -> CONTROL-NOT-RED on clean",
"M31": "EXIT=0 last line in red receipt -> control-not-red fixtures disturbed",
"M32": "NAMED LIMIT NL-RECEIPT: corrected= count of the green receipt is never read (tool reads only the final EXIT line)",
"M33": "EQUIV: the COUNTER constant and its digest are derived from one value; only digest equality is checked",
"M34": "NAMED LIMIT NL-SYMLINK-TARGET: dangling link reads as COUNTER-DIGEST on base; target name not pinned and case is red on base",
"M35": "counter-symlink fixture without the symlink -> COUNTER-MISSING (detail only; verdict FAIL both before and after)",
"M36": "population-symlink fixture without the symlink -> detail only; verdict FAIL both before and after",
"M37": "EQUIV: a trailing blank line is ignored by the tool",
"M38": "NAMED LIMIT NL-FIELDNAME: every drop fixture removes Base; FIELD-MISSING checked by class, so the key is never verified",
"M39": "EQUIV: tool strips values, so one space is FIELD-EMPTY like the empty value",
"M40": "clean expects rc 1 -> FAIL on base and stub",
"M41": "no-claims expects a C1 class -> FAIL",
"M42": "field-missing-base expects C2 -> FAIL",
"M43": "dup-target wants FIELD-EMPTY: FAIL on both, only the printed want changes",
"M44": "heading-valid-tail expects 5 copies; multiset exact -> FAIL",
"M45": "counter-symlink expects COUNTER-DIGEST: base case flips FAIL->PASS (fail 13->12)",
"M46": "dispatch-names-after expects rc 1 -> PASS->FAIL",
"M47": "NAMED LIMIT NL-BASERED: dispatch-spec-before fixture renamed; base/stub red with identical detail (the names are not printed)",
"M48": "NAMED LIMIT NL-BASERED: negative fixture renamed to a dispatch-pattern name; base/stub PASS. Only a tool that implements the widened name rule would fail it",
"M49": "dispatch-attempts-before wants DISPATCH-AFTER: FAIL both, only the printed want changes",
"M50": "population-symlink fixture as population_missing: detail only",
"M51": "population-empty fixture no longer empty -> POPULATION-EMPTY absent -> FAIL",
"M52": "two-claims wants C1 -> FAIL",
"M53": "base-not-ancestor wants rc 0 -> FAIL",
"M54": "frozen-edited-population wants POPULATION-DIGEST -> PASS->FAIL",
"M55": "rc comparison inverted -> 35 of 37 cases flip",
"M56": "NAMED LIMIT NL-MULTISET: set vs multiset; base and stub produce exact multiplicities, so no scored case decides on multiplicity",
"M57": "NAMED LIMIT NL-SUMCOUNT: SUMMARY findings count compared with len(want), never with the FINDING lines; no scored tool prints an inconsistent count",
"M58": "NAMED LIMIT NL-CRASH: crash guard unexercised; no scored tool emits a traceback",
"M59": "detail truncated to 24 chars: FAIL lines shorter, verdict unchanged",
"M60": "absent-prereg probe uses an existing prereg -> FAIL",
"M61": "NAMED LIMIT NL-REFUSAL-RC: unresolved rev accepted with rc 1 as well as 2; no scored tool exits 1 here",
"M62": "cases total off by one -> cases=36",
"M63": "absent-prereg probe dropped from the total -> cases=36",
"M64": "FINDING regex without re.M: only the first finding is read (retro findings 19->1, population-symlink detail)",
"M65": "EQUIV: the class tokens of both tools are uppercase; the relaxed group matches the same tokens",
"M66": "EQUIV: neither tool prints trailing whitespace on the SUMMARY line",
"M67": "EQUIV: no scored run approaches 30 s (about 10 s wall); the timeout is never hit",
"M68": "stub selftest line no longer matches (pass=12 needs two digits) -> selftest FAIL on stub",
"M69": "selftest threshold 13 -> stub selftest FAIL",
"M70": "NAMED LIMIT NL-SELFTEST: fail==0 condition; the stub reports fail=0 only, so the condition is never exercised",
"M71": "NAMED LIMIT NL-SELFTEST: selftest rc 1 accepted; no scored tool exits 1 from --selftest",
"M72": "patch count without the selftest gate: base's argparse rc 2 counted -> base 3/3",
"M73": "only 124 counted as patched failure: always-green stub -> 3/3",
"M74": "NAMED LIMIT NL-PATCHLEG: P2 injection dead; both scored tools give 0/3 by construction, so the patch leg is invisible",
"M75": "NAMED LIMIT NL-PATCHLEG: P3 injection dead; same invisibility",
"M76": "NAMED LIMIT NL-PATCHLEG: P1 reversal made identity; same invisibility",
"M77": "NAMED LIMIT NL-PATCHLEG: patch dir not on PYTHONPATH; same invisibility",
"M78": "NAMED LIMIT NL-PATCHLEG: patch selector value wrong; same invisibility",
"M79": "NAMED LIMIT NL-REAL: real leg checks claims only; both scored tools have findings=0 anyway",
"M80": "retro threshold 20: base has 19 findings -> retro FAIL",
"M81": "retro_clean expects (1,0) -> FAIL on both",
"M82": "RETRO_PATH on round-41: rc 0, so retro FAIL",
"M83": "NAMED LIMIT NL-REAL: the round-41 prereg is also clean on base and stub (real=ok), so the path change is not observed",
"M84": "NAMED LIMIT NL-STUB: stub text never printed; control verdict is a pass count only",
"M85": "NAMED LIMIT NL-STUB: stub findings exit code never observed",
"M86": "NAMED LIMIT NL-STUB: stub clean exit code never observed",
"M87": "NAMED LIMIT NL-ACCEPTED: ACCEPTED branch needs a tool passing all 37 cases; neither scored tool does",
"M88": "stub threshold sn-40: both stubs flip to ACCEPTED",
"M89": "NAMED LIMIT NL-MET: AND conjunct; base and stub fail >=2 conjuncts, so dropping one leaves exit 1",
"M90": "NAMED LIMIT NL-MET: AND conjunct passed==n; same",
"M91": "met forced True -> exit 0",
"M92": "exit code inverted -> exit 0",
"M93": "SUMMARY pass/fail values swapped",
"M94": "tool_sha prefix changed (SUMMARY text)",
"M95": "EQUIV: both stubs are REJECTED; swapping the label order yields the same tokens",
"M96": "EQUIV: both stubs are REJECTED; swapping the arguments yields the same tokens",
"M97": "candidate case lines suppressed; SUMMARY and exit unchanged (text-only kill)",
"M98": "pristine check inverted: present tool reported absent (no case lines)",
"M99": "PROBE KILL: scratch guard weakened; invocation with a missing scratch dir gives a FileNotFoundError traceback (rc 1) where the frozen counter refuses (rc 2). Not reached by any scored run",
"M100": "PROBE KILL: rev guard dropped; a 7-char short rev (afe17f4) runs the whole counter (rc 1) where the frozen counter refuses (rc 2). Not reached by any scored run",
"M101": "EQUIV for printed output: scratch cleanup removed; the leaked directory is not observed by the harness",
"M102": "PROBE KILL: default TOOL_PATH misnamed; the default invocation (used by score-candidate.sh) prints PRISTINE FAIL TOOL-ABSENT. Scored runs pass --tool explicitly, so they cannot see it",
"M103": "EQUIV: cat-file rejects any non-commit string, so a 41-char rev refuses identically",
}
rows = []
counts = {"killed-verdict": 0, "killed-text": 0, "killed-probe": 0, "equiv": 0, "named": 0}
PROBE = {"M99", "M100", "M102"}
for mid in ids:
    desc = {"M100": "rev format guard (`not REV.match`) dropped from the refusal test"}.get(mid, man[mid][2])
    fb, kb = fields(mid + "-base", "base-base")
    fs, ks = fields(mid + "-stub", "base-stub")
    allf = []
    for x in fb + fs:
        if x not in allf: allf.append(x)
    kinds = kb | ks
    note = NOTES[mid]
    if mid in PROBE:
        killed = "no (scored); YES by probe"; counts["killed-probe"] += 1
        pf = "probe-only: " + {"M99": "exit 2->1 + traceback", "M100": "exit 2->1 (full run)", "M102": "PRISTINE TOOL-ABSENT, all cases red"}[mid]
        allf = allf or []
        allf = [pf]
        if not (fb or fs): allf = [pf]
    elif kinds & {"verdict"}:
        killed = "YES (verdict)"; counts["killed-verdict"] += 1
    elif kinds & {"text"}:
        killed = "YES (text only)"; counts["killed-text"] += 1
    else:
        if note.startswith("EQUIV") or note.startswith("EQUIV"):
            killed = "no - equivalent"; counts["equiv"] += 1
        elif note.startswith("EQUIV") is False and "NAMED LIMIT" in note:
            killed = "no - survived (named limit)"; counts["named"] += 1
        else:
            killed = "no - survived"; counts["named"] += 1
    if mid not in PROBE and not (kinds & {"verdict", "text"}) and note.startswith("EQUIV"):
        pass
    rows.append((mid, desc, killed, "; ".join(allf) if allf else "none", note))
# sanity: killed rows
tbl = ["| mutant id | change | killed? | which printed field changed | notes |", "|---|---|---|---|---|"]
for mid, desc, killed, fld, note in rows:
    tbl.append("| %s | %s | %s | %s | %s |" % (mid, desc.replace("|", "/"), killed, fld.replace("|", "/"), note.replace("|", "/")))
open(W + "/table.md", "w", encoding="utf-8").write("\n".join(tbl) + "\n")
print(counts, len(rows))
print("\n".join(tbl[:12]))
