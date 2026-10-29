import hashlib, os, sys, py_compile
SRC = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42mutationtester02/c2-counter.py"
OUT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42mutationtester02/mutants"
# (id, class-group, description, old, new)  old must occur exactly once in the frozen counter text
M = [
 ("M01","helper","sha256 -> sha1 in digest helper", 'hashlib.sha256(text.encode("utf-8"))', 'hashlib.sha1(text.encode("utf-8"))'),
 ("M02","helper","digest encoding utf-8 -> ascii", 'hashlib.sha256(text.encode("utf-8"))', 'hashlib.sha256(text.encode("ascii"))'),
 ("M03","prereg","default Round 42 -> 41", 'def prereg_text(claims, round_no="42"):', 'def prereg_text(claims, round_no="41"):'),
 ("M04","prereg","Round line emitted with empty value", 'out = ["# prereg", "Round: %s" % round_no, ""]', 'out = ["# prereg", "Round:", ""]'),
 ("M05","prereg","claim heading numbered n+1", 'out.append("## C%d — claim %d" % (n, n))', 'out.append("## C%d — claim %d" % (n + 1, n))'),
 ("M06","prereg","heading em dash -> hyphen", 'out.append("## C%d — claim %d" % (n, n))', 'out.append("## C%d - claim %d" % (n, n))'),
 ("M07","prereg","key tuple drops Kill", 'for key in ("Base", "Counter", "Population", "Control", "Target", "Kill"):', 'for key in ("Base", "Counter", "Population", "Control", "Target"):'),
 ("M08","prereg","None-filter removed (identity no-op)", 'if key in c and c[key] is not None:', 'if key in c:'),
 ("M09","prereg","key line separator without space", 'out.append("%s: %s" % (key, c[key]))', 'out.append("%s:%s" % (key, c[key]))'),
 ("M10","prereg","claim lines joined by blank line", 'return "\\n".join(out) + "\\n"', 'return "\\n\\n".join(out) + "\\n"'),
 ("M11","prereg","__extra read with None default (crash when absent)", 'for key, value in c.get("__extra", []):', 'for key, value in c.get("__extra", None):'),
 ("M12","build","Counter digest taken from population", '"Counter": "census/c1.py sha256=%s" % sha(counter),', '"Counter": "census/c1.py sha256=%s" % sha(population),'),
 ("M13","build","Counter path with double space before sha256", '"Counter": "census/c1.py sha256=%s" % sha(counter),', '"Counter": "census/c1.py  sha256=%s" % sha(counter),'),
 ("M14","build","Target value changed (fixture only)", '"Target": "items=2 corrected=2", "Kill"', '"Target": "items=2 corrected=3", "Kill"'),
 ("M15","build","Control path points at a missing file", '"Control": "census/control.txt", "Target"', '"Control": "census/control2.txt", "Target"'),
 ("M16","build","counter_digest sentinel 63 zeros + 1", '% ("0" * 64)', '% ("0" * 63 + "1")'),
 ("M17","build","population_digest sentinel changed", '% ("1" * 64)', '% ("2" * 64)'),
 ("M18","build","population override inverted", 'if "population" in mut:', 'if "population" not in mut:'),
 ("M19","build","two_claims: bad claim drops Target instead of Kill", 'bad.pop("Kill")', 'bad.pop("Target")'),
 ("M20","build","two_claims: claim order reversed", 'claims = [claim, bad]', 'claims = [bad, claim]'),
 ("M21","build","counter_missing guard inverted", 'elif not mut.get("counter_missing"):', 'elif mut.get("counter_missing"):'),
 ("M22","build","frozen edit becomes a no-op (commit fails)", 'write("census/c1.py", counter + "# edited after freeze\\n")', 'write("census/c1.py", counter)'),
 ("M23","build","early dispatch written under round-41", 'write(".ufo/waves/round-42/w1-dispatch.json", "{}\\n")\n        commit("early dispatch")', 'write(".ufo/waves/round-41/w1-dispatch.json", "{}\\n")\n        commit("early dispatch")'),
 ("M24","build","early wave files written under round-43", 'write(".ufo/waves/round-42/" + rel, "x\\n")\n        commit("early wave files")', 'write(".ufo/waves/round-43/" + rel, "x\\n")\n        commit("early wave files")'),
 ("M25","build","side branch named main (checkout fails)", 'git(d, scratch, "checkout", "-q", "-b", "side")', 'git(d, scratch, "checkout", "-q", "-b", "main")'),
 ("M26","build","base-not-ancestor claim uses the ancestor base", 'claim["Base"] = side', 'claim["Base"] = base'),
 ("M27","build","base-unresolved sentinel f*40", 'claim["Base"] = "0" * 40', 'claim["Base"] = "f" * 40'),
 ("M28","build","fixture tip returned as freeze commit", 'return d, git(d, scratch, "rev-parse", "HEAD"), "prereg.txt", freeze', 'return d, freeze, "prereg.txt", freeze'),
 ("M29","build","dup sentinel string changed (identical-vs-differs unobservable)", 'value == "CLAIMCOUNTER" else value', 'value == "CLAIMCOUNTERX" else value'),
 ("M30","build","default control becomes the green receipt", 'mut.get("control", CONTROL_RED)', 'mut.get("control", CONTROL_GREEN)'),
 ("M31","build","CONTROL_RED last line EXIT=0", 'CONTROL_RED = "SUMMARY items=2 corrected=0\\nEXIT=1\\n"', 'CONTROL_RED = "SUMMARY items=2 corrected=0\\nEXIT=0\\n"'),
 ("M32","build","CONTROL_GREEN corrected=0 (EXIT=0 kept)", 'CONTROL_GREEN = "SUMMARY items=2 corrected=2\\nEXIT=0\\n"', 'CONTROL_GREEN = "SUMMARY items=2 corrected=0\\nEXIT=0\\n"'),
 ("M33","build","COUNTER constant text changed (digest follows)", "COUNTER = \"# counter\\nprint('counter')\\n\"", "COUNTER = \"# counter\\nprint('counter!')\\n\""),
 ("M34","build","counter symlink target dangling", 'os.symlink("real-c1.py", os.path.join(d, "census/c1.py"))', 'os.symlink("missing.py", os.path.join(d, "census/c1.py"))'),
 ("M35","build","counter symlink not created", 'os.symlink("real-c1.py", os.path.join(d, "census/c1.py"))', 'pass'),
 ("M36","build","population symlink not created", 'os.symlink("real-pop.tsv", os.path.join(d, "census/pop.tsv"))', 'pass'),
 ("M37","build","tail default newline (blank line)", 'mut.get("tail", "")', 'mut.get("tail", "\\n")'),
 ("M38","build","drop() removes the wrong key (Base always)", 'claim.pop(mut["drop"])', 'claim.pop("Base")'),
 ("M39","build","blank() writes a space instead of empty", 'claim[mut["blank"]] = ""', 'claim[mut["blank"]] = " "'),
 ("M40","cases","clean expects rc 1", '("clean", {}, 0, []),', '("clean", {}, 1, []),'),
 ("M41","cases","no-claims expects C1 class", '[("C0", "NO-CLAIMS")]', '[("C1", "NO-CLAIMS")]'),
 ("M42","cases","field-missing-base expects C2 class", '("field-missing-base", {"drop": "Base"}, 1, [("C1", "FIELD-MISSING")]),', '("field-missing-base", {"drop": "Base"}, 1, [("C2", "FIELD-MISSING")]),'),
 ("M43","cases","dup-target want class FIELD-EMPTY (verdict same, detail differs)", '("dup-target", {"dup": ("Target", "something else")}, 1, [("C1", "KEY-DUPLICATE")]),', '("dup-target", {"dup": ("Target", "something else")}, 1, [("C1", "FIELD-EMPTY")]),'),
 ("M44","cases","heading-valid-tail expects 5 copies", '[("C2", "FIELD-MISSING")] * 6),', '[("C2", "FIELD-MISSING")] * 5),'),
 ("M45","cases","counter-symlink expects COUNTER-DIGEST", '[("C1", "COUNTER-SYMLINK")]),', '[("C1", "COUNTER-DIGEST")]),'),
 ("M46","cases","dispatch-names-after expects rc 1", '"w1.ready.dispatched", "w1-results.json"]}, 0, []),', '"w1.ready.dispatched", "w1-results.json"]}, 1, []),'),
 ("M47","cases","dispatch-spec-before fixture file renamed .txt", '{"before_files": ["w1-spec.json"]}', '{"before_files": ["w1-spec.txt"]}'),
 ("M48","cases","dispatch-notes-before negative fixture renamed to a dispatch name", '{"before_files": ["notes.md", "w1/Seat01.md"]}', '{"before_files": ["w1-dispatch-notes.md", "w1/Seat01.md"]}'),
 ("M49","cases","dispatch-attempts-before want class changed", '"w1-dispatch-attempts.txt"]}, 1,\n     [("C0", "DISPATCH-BEFORE-FREEZE")]),', '"w1-dispatch-attempts.txt"]}, 1,\n     [("C0", "DISPATCH-AFTER-FREEZE")]),'),
 ("M50","cases","population-symlink fixture uses missing mutation", '("population-symlink", {"population_symlink": True}, 1,', '("population-symlink", {"population_missing": True}, 1,'),
 ("M51","cases","population-empty fixture no longer empty", '{"population": "id\\tname\\n"}', '{"population": "id\\tname\\n1\\talpha\\n"}'),
 ("M52","cases","two-claims-one-bad want C1 class", '("two-claims-one-bad", {"two_claims": True}, 1, [("C2", "FIELD-MISSING")]),', '("two-claims-one-bad", {"two_claims": True}, 1, [("C1", "FIELD-MISSING")]),'),
 ("M53","cases","base-not-ancestor expects rc 0", '("base-not-ancestor", {"base_side": True}, 1,', '("base-not-ancestor", {"base_side": True}, 0,'),
 ("M54","cases","frozen-edited-population expects POPULATION-DIGEST", '("frozen-edited-population", {"edit_population": True}, 1, [("C1", "FROZEN-EDITED")]),', '("frozen-edited-population", {"edit_population": True}, 1, [("C1", "POPULATION-DIGEST")]),'),
 ("M55","legs","case_ok rc comparison inverted", 'ok = (rc == want_rc and got == sorted(want)', 'ok = (rc != want_rc and got == sorted(want)'),
 ("M56","legs","case_ok multiset compared as set", 'got == sorted(want)', 'set(got) == set(want)'),
 ("M57","legs","case_ok SUMMARY count check weakened", 'and summ[1] == len(want))', 'and summ[1] >= 0)'),
 ("M58","legs","case_ok crash check removed", 'and not crash and summ is not None', 'and summ is not None'),
 ("M59","legs","case_ok detail truncated to 24 chars", 'detail[:240]', 'detail[:24]'),
 ("M60","legs","unresolved-prereg probe uses an existing prereg", 'run_tool(tool, d, tip, "absent.txt", scratch)', 'run_tool(tool, d, tip, "prereg.txt", scratch)'),
 ("M61","legs","unresolved-rev check weakened to != 0", 'r1[0] == 2 and "COULD-NOT-EVALUATE"', 'r1[0] != 0 and "COULD-NOT-EVALUATE"'),
 ("M62","legs","score_tool total drops one", 'return sum(1 for _n, ok, _d in results if ok), len(results)', 'return sum(1 for _n, ok, _d in results if ok), len(results) - 1'),
 ("M63","legs","score_tool drops absent-prereg result", 'zip(("unresolved-rev", "absent-prereg"), two_unresolved(tool, scratch, label))', 'zip(("unresolved-rev",), two_unresolved(tool, scratch, label))'),
 ("M64","legs","FINDING regex without re.M", 're.finditer(r"^FINDING (\\S+) (\\S+)", p.stdout, re.M)', 're.finditer(r"^FINDING (\\S+) (\\S+)", p.stdout)'),
 ("M65","legs","FINDING class group relaxed to uppercase only", 'r"^FINDING (\\S+) (\\S+)"', 'r"^FINDING (\\S+) ([A-Z-]+)"'),
 ("M66","legs","SUMMARY regex trailing-space tolerance removed", 'findings=(\\d+)\\s*$", p.stdout, re.M)', 'findings=(\\d+)$", p.stdout, re.M)'),
 ("M67","legs","run_tool timeout 300 -> 30 (no hang observed)", 'env=env(scratch), timeout=300)', 'env=env(scratch), timeout=30)'),
 ("M68","legs","SELFTEST regex pass group single digit", 'SELFTEST_RE = re.compile(r"^SELFTEST cases=(\\d+) pass=(\\d+) fail=(\\d+)\\s*$", re.M)', 'SELFTEST_RE = re.compile(r"^SELFTEST cases=(\\d+) pass=(\\d) fail=(\\d+)\\s*$", re.M)'),
 ("M69","legs","selftest case threshold 12 -> 13", 'st_sum[0] >= 12', 'st_sum[0] >= 13'),
 ("M70","legs","selftest fail==0 condition weakened", 'and st_sum[2] == 0 and not st_crash', 'and st_sum[2] >= 0 and not st_crash'),
 ("M71","legs","selftest exit code 0 or 1 accepted", 'selftest = "ok" if (st_rc == 0 and st_sum', 'selftest = "ok" if (st_rc in (0, 1) and st_sum'),
 ("M72","legs","patches counted without selftest gate", 'patches += 1 if (selftest == "ok" and p_rc not in (0, 124)) else 0', 'patches += 1 if (p_rc not in (0, 124)) else 0'),
 ("M73","legs","patched exit code only 124 counted", 'p_rc not in (0, 124)', 'p_rc not in (124,)'),
 ("M74","patch","P2 targets --diff-filter=D instead of A", "'--diff-filter=A' in argv", "'--diff-filter=D' in argv"),
 ("M75","patch","P3 misspelled merge-base target", "'merge-base' in argv", "'merge-bas' in argv"),
 ("M76","patch","P1 digest reversal made identity", 'return self._h.hexdigest()[::-1]', 'return self._h.hexdigest()[::1]'),
 ("M77","legs","PYTHONPATH not pointed at patch dir", 'e["PYTHONPATH"] = pdir', 'e["PYTHONPATH"] = os.devnull'),
 ("M78","legs","patch selector env value wrong", 'e["SOUJI_R42_PATCH"] = patch', 'e["SOUJI_R42_PATCH"] = "P0"'),
 ("M79","legs","real leg checks SUMMARY claims only", 'r_summ == (3, 0) and not r_crash', 'r_summ[0] == 3 and not r_crash'),
 ("M80","legs","retro threshold 3 -> 20 findings", 'len(t_find) >= 3', 'len(t_find) >= 20'),
 ("M81","legs","retro_clean expects (1,0)", 'c_summ == (3, 0)', 'c_summ == (1, 0)'),
 ("M82","legs","RETRO_PATH points at round-41", 'RETRO_PATH = "census/round-40/preregistration.txt"', 'RETRO_PATH = "census/round-41/preregistration.txt"'),
 ("M83","legs","PREREG_PATH points at round-41", 'PREREG_PATH = "census/round-42/preregistration.txt"', 'PREREG_PATH = "census/round-41/preregistration.txt"'),
 ("M84","main","stub clean text claims findings=1", "print('SUMMARY claims=1 findings=0')", "print('SUMMARY claims=1 findings=1')"),
 ("M85","main","stub findings receipt exit 0", r'"sys.exit(1)\n")', r'"sys.exit(0)\n")'),
 ("M86","main","stub clean exit 1", r'sys.exit(0)\n")', r'sys.exit(1)\n")'),
 ("M87","main","stub verdict threshold <= (ACCEPTED branch unreachable)", 'stubs[label] = "REJECTED" if sp < sn else "ACCEPTED"', 'stubs[label] = "REJECTED" if sp <= sn else "ACCEPTED"'),
 ("M88","main","stub verdict threshold sn-40 (kills stubs)", 'stubs[label] = "REJECTED" if sp < sn else "ACCEPTED"', 'stubs[label] = "REJECTED" if sp < sn - 40 else "ACCEPTED"'),
 ("M89","main","met conjunct patches==3 dropped", 'and patches == 3)', ')'),
 ("M90","main","met conjunct passed==n dropped", 'met = (n == 37 and passed == n and', 'met = (n == 37 and'),
 ("M91","main","met forced True", 'met = (n == 37 and', 'met = True or (n == 37 and'),
 ("M92","main","exit code inverted", 'return 0 if met else 1', 'return 1 if met else 0'),
 ("M93","main","SUMMARY pass and fail arguments swapped", 'n, passed, n - passed, stubs["control_clean"]', 'n, n - passed, passed, stubs["control_clean"]'),
 ("M94","main","SUMMARY tool_sha prefix 11 chars", 'hashlib.sha256(blob.stdout).hexdigest()[:12]', 'hashlib.sha256(blob.stdout).hexdigest()[:11]'),
 ("M95","main","SUMMARY stub labels swapped (both REJECTED)", 'control_clean=%s control_findings=%s', 'control_findings=%s control_clean=%s'),
 ("M96","main","SUMMARY stub args swapped (both REJECTED)", 'stubs["control_clean"], stubs["control_findings"]', 'stubs["control_findings"], stubs["control_clean"]'),
 ("M97","main","candidate case lines suppressed (verbose off)", 'passed, n = score_tool(tool, scratch, "cand")', 'passed, n = score_tool(tool, scratch, "cand", verbose=False)'),
 ("M98","main","pristine check inverted", 'if blob.returncode != 0:', 'if blob.returncode == 0:'),
 ("M99","main","scratch dir refusal guard weakened", 'if not scratch_root or not os.path.isdir(scratch_root):', 'if not scratch_root:'),
 ("M100","main","rev refusal: or -> and removed (dead for valid rev)", 'if not REV.match(args.rev) or subprocess.run(', 'if subprocess.run('),
 ("M101","main","scratch cleanup removed (not observed)", 'shutil.rmtree(scratch, ignore_errors=True)', 'pass'),
 ("M102","main","default tool path misnamed (default invocation only)", 'TOOL_PATH = "tools/souji-freeze-check.py"', 'TOOL_PATH = "tools/souji-freeze.py"'),
 ("M103","main","REV regex without end anchor (equivalent for 40-hex)", 'REV = re.compile(r"^[0-9a-f]{40}$")', 'REV = re.compile(r"^[0-9a-f]{40}")'),
]
def main():
    src = open(SRC, encoding="utf-8").read()
    os.makedirs(OUT, exist_ok=True)
    rows = []
    seen = set()
    for mid, grp, desc, old, new in M:
        assert mid not in seen, mid; seen.add(mid)
        n = src.count(old)
        if n != 1:
            print("NONUNIQUE", mid, n, old[:70]); sys.exit(2)
        mut = src.replace(old, new, 1)
        assert mut != src, mid
        p = os.path.join(OUT, mid + ".py")
        open(p, "w", encoding="utf-8").write(mut)
        py_compile.compile(p, cfile="/fast/scratch/hyaku/souji-r42/R42mutationtester02/pyc-" + mid, doraise=True)
        rows.append("%s\t%s\t%s\t%s\t%s" % (mid, grp, desc, hashlib.sha256(mut.encode("utf-8")).hexdigest()[:16], "%r -> %r" % (old[:90], new[:90])))
    open(os.path.join(OUT, "manifest.tsv"), "w", encoding="utf-8").write("id\tgroup\tdescription\tmutant_sha256_16\told_to_new\n" + "\n".join(rows) + "\n")
    print("mutants", len(M))
main()
