#!/usr/bin/env python3
"""souji r76 wave w1 spec builder (L1 SoujiR76). Writes .ufo/waves/round-76/w1-spec.json."""
import json
import os

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SCR = "/fast/scratch/hyaku/souji-r76"
GS = open(os.path.expanduser("~/.agents/skills/godspeed/directive.md")).read()
HEAD = "/skill:godspeed\n" + GS + "\n\n"
WEAK = "8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0"
BASE = "ee59aa4da358d38850ccace194f7cd558ee45ce9"
P = "6c9c2a8eaad2ee570e4f43517d1f437567bb9873"
F = "2ed6b179ef4aeb106488806b9f3dcacca29e2e60"
I = "2c7c1ce6f91062f497ffbbc7fcc9e9c19e2511ce"
W = "e827d2bf53f71470bfc1fce6aa4633549b018270"
A = "113b007202d79275ca2debaaaa719551eaa35198"
R = f"{LANE}/census/round-76"

context = f"""# Goal
souji round 76 (lane repo {LANE}, lane id souji). The L1 (SoujiR76) holds the planner seat and is the ONLY integration owner: it commits through the lane helper and writes the report. You are one seat of ONE wave of 12 seats. Seats deliver files and findings only. Your mandate is to FALSIFY the frozen round-76 claims and the round's landed changes: re-derive every number yourself from committed bytes; a number you cannot reproduce is a finding. Do not trust the L1's counts.

# Evidence durability
FIRST action: create your report file (the `Report:` trailer path) with a one-line skeleton, and append to it as you go. Your final yield must repeat the same content. A seat that ends without that file counts as no verdict.

# Chronology (binding; read {R}/preregistration.txt first — it is the frozen contract, Q99 grammar)
- Lane base (r75 admitted): {BASE}.
- P {P}: census/round-76/c1-evade-counter.py (C1 counter; imports census/round-75/c1-evade-counter.py — its 20 r74 + 5 r75 routes — and adds f9 f10 f14 f11 f12; f7 relabelled FAIL), c1-population.tsv (30 ids + expected check-clean), c2-binding-counter.py (C2 counter: runs a tally per case and compares its exit with the frozen expectation), c2-population.tsv (10 receipt-set cases: h-* honest, u-* unread classes, b-* binding forgeries), c2-cases/ (3 forged receipts built from census/round-75/records by changing EXIT lines only), rec.sh, controls/ (c1-K-a-do-nothing.txt lane-base gate mismatches=4 EXIT=1; c1-K-b-blanket-ignored.txt any-ignored-refusal mismatches=4; c1-K-c-naive-untracked-gitignore.txt any-untracked-.gitignore refusal mismatches=1; c2-K-do-nothing-r75.txt = r75 tally mismatches=5 EXIT=1; c2-K-b-blanket-reject-all.txt mismatches=2), controls/variants/, srcs/git-check-ignore.adoc (git v2.56.0), records/census-before.txt.
- F {F}: census/round-76/preregistration.txt (freeze-check --substance --chronology at F: `SUMMARY claims=2 findings=0`).
- I {I}: census/round-76/c2-kill-tally.py = r75 tally + receipt-to-mutant binding (derives each mutant's counter sha256 from the frozen edit sets applied to census/round-75/c1-counter.py; requires instrument_sha256= to match, command= to carry --selftest, no duplicate receipt digest) and every EXIT= line must agree.
- W {W}: tools/souji-pre-report-gate.sh check 4 — inside the heredoc after the r75 block: every ignored untracked path (`ls-files -o -i --exclude-standard`) is attributed with `git -c core.excludesFile=/dev/null check-ignore -v -n -z --stdin`; its deciding pattern must come from a TRACKED .gitignore in an ancestor directory (RECEIPT-UNTRACKED-UNDECLARED-IGNORE otherwise). Same commit adds `.jj/` and `.ruff_cache/` to the lane's .gitignore.
- A {A}: records/c1-after.txt (W gate: rows=30 mismatches=0 EXIT=0), records/c2-after.txt (r76 tally: cases=10 mismatches=0 EXIT=0), records/c1-regress-r36.txt (21/21), records/c1-regress-r27.txt (4/4).

# Claims (frozen predicates are in the preregistration; never change them)
C1 operability (sourced on S320 git-check-ignore(1), opened this round): the pre-report gate refuses untracked content hidden by an UNTRACKED .gitignore (self-ignoring directory, the r75 stated limit f7) while accepting content hidden by tracked .gitignore rules. 30 rows: mismatches 4 -> 0; K-b and K-c stay red; r27 4/4 and r36 21/21; domain trial on the lane check-clean=PASS.
C2 calibration: the lane's mutant-kill tally binds every receipt to the mutant it is filed under: 10 cases, mismatches 5 -> 0; blanket reject-all stays red; the honest r75 set still reads killed=6.

# Frozen invocations (run from {LANE}; never alter counters, populations, cases or controls)
- C1: copy the gate and tools/souji-receipt-write.py at a revision into ONE dir (`git show <rev>:tools/souji-pre-report-gate.sh > D/souji-pre-report-gate.sh`, same for the writer); python3 -B census/round-76/c1-evade-counter.py --gate-dir D --work <SCRATCH>/c1 (work absent or empty; ~10 s).
- C2: python3 -B census/round-76/c2-binding-counter.py --tally <tally path> (~3 s). A tally is run as `python3 -B <tally> --pristine <receipt> --mutant ID=<receipt> ...` from the lane root.
- Mutants of the r75 counter: python3 -B census/round-73/apply-edit.py --set census/round-75/c2-mutants.json (or census/round-74/c2-survivors.json) --id <ID> --src census/round-75/c1-counter.py --out <SCRATCH>/<ID>.py; selftest: python3 -B <counter> --selftest --root {LANE} --matrix census/round-73/c1-matrix.tsv --base-rev {WEAK} --work <existing empty dir> (~55 s).
- Every receipt starts with `command=<literal command>` (rec.sh); replaying that line with your scratch prefix is a valid check.
<SCRATCH> must be a fresh directory under {SCR}/<your seat name>/ (mkdir -p it). Counters refuse --work under /tmp, /var/tmp or /dev/shm. Parallel arms are fine (32 cores) but check load.

# Write scope and bounds
You write ONLY under {LANE}/.ufo/waves/round-76/w1/ (your own seat directory <SeatName>/ and your own <SeatName>.md) and under your scratch dir. Never edit lane tracked files (census/, tools/, corpus/, .gitignore, SCORECARD.md, LOG.md, PROVINCE.md, SKILL.md, SHONEN.md). Never edit MANIFEST.json, .ufo/state/, .ufo/watchdog.log, /home/vgpnk/Projects/shokunin/templates/, /home/vgpnk/Projects/shokunin/scripts/, /home/vgpnk/Projects/shokunin/.scratch/, or any sibling repo. Never commit, push, stash, reset, checkout, switch, pull, or run any mutating git or jj command in the lane or the fleet repo. Read-only git (show, log, diff, status, rev-parse, cat-file, ls-files, ls-remote, check-ignore) is fine; read-only jj only with --ignore-working-copy.
Fixture repos (round-70 fleet incident: a mktemp template without XXXXXX made `git -C ""` fall back to the fleet root and commit there): create D=$(mktemp -d -p "{SCR}/<seat>" fx.XXXXXX) and immediately check `[ -n "$D" ] && [ -d "$D" ] || exit 1`; git -C "$D" init -q; verify `[ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ]` before the first commit; name -C "$D" on every later git call (never a bare `git commit`, never an unchecked variable after -C); in Python assert the -C/cwd path is absolute and non-empty. Commit only with an explicit fixture identity inside $D. To mutate a file, copy it into your scratch dir first; never edit it in the lane. Bind every shell variable in the same shell that uses it.
Host paths outside your scratch (/boot, /etc, /usr, /var, /efi, other homes) are read-only inputs: never run a binary-editing tool on them (2026-11-06 incident: `objcopy --dump-section` without an output operand rewrote a UKI in place). Never run sudo, never change host sysctls or kernel parameters; if a probe needs one, report the need instead. Never message agent://all; never call the task tool.
Scratch discipline: mkdir -p "{SCR}/<seat>" and pass it explicitly (TMPDIR, --work); trap 'rm -rf -- "$S"' EXIT in shell (copy receipts to your seat directory first, small text only). Check bash /home/vgpnk/Projects/shokunin/scripts/hyaku/disk-guard.sh status before any heavy pass; on ENOSPC report the free space you saw and stop. Remove your scratch dir before you yield.
Every `Report:` trailer path is relative to {LANE}; write it at {LANE}/<that path>. All paths you name must be absolute under {LANE} or your scratch dir.

# Tooling authorization (operator, 2026-10-19)
You and every seat may install or upgrade tools that help the task. Read /home/vgpnk/.omp/agent/RULES.md first (official channels, update-safety gate; record tool, version, channel and reason in your report). pacman transactions are PAUSED host-wide (orchestrator ruling 2026-10-20): install via uv tool, npx, or an official binary in ~/.local/bin, or file an L0 question. Never run pacman -Sy, -Syu, -U, -R or a downgrade; before any future pacman -S run pacman -Sp --print-format '%n %v' and proceed only for packages not yet installed.

# Report format
Keep it under 40 lines: verdict per item, the exact commands you ran, the observed output lines that decide the verdict, file:line evidence, and any finding tagged HIGH, MEDIUM or LOW. Name every file you wrote under your seat directory. The report file and your final yield carry the same content.
"""

items = [
 ("S76Connector", "connector", f"""# Target
Cross-claim separation and sibling-overlap scan for round 76. Read-only.

# Change
1. Causal separation: confirm from receipt `# bind`/`instrument=` lines that no C1 receipt (records/c1-*.txt, controls/c1-K-*.txt) reads a C2 tally/counter byte and no C2 receipt (records/c2-after.txt, controls/c2-*.txt) reads a gate byte; and that the W commit {W} touches only the gate and .gitignore while I {I} touches only c2-kill-tally.py. Verdict SEPARABLE/COUPLED.
2. Other lane tools that treat a self-ignoring untracked .gitignore as policy (any tool that reads ignored files, or decides "clean" from status/ls-files): file:line under {LANE}/tools and {LANE}/census/round-7*/; would an f7-shape directory change their verdict?
3. Sibling overlap (read-only; other *-shokunin repos under /home/vgpnk/Projects/shokunin): which sibling gates/tallies (a) decide cleanliness while missing ignored content, (b) tally mutant receipts without binding the receipt to the mutant? Table: lane, file:line, vulnerable yes/no.

# Acceptance
Tables with verdicts and file:line; findings by severity."""),
 ("S76ScoutSources", "scout", f"""# Target
Re-open the round's new source and test the sentences C1 rests on. Read-only on the lane.

# Change
1. Fetch https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-check-ignore.adoc yourself (curl -sSL); compare sha256 with {R}/srcs/git-check-ignore.adoc (940177c7385e…8208, 4159 bytes). Also fetch https://git-scm.com/docs/git-check-ignore and report its version banner.
2. Locate and word-count (must be <=25) the candidate anchor "<source> is the pattern's source file, and <linenum> is the line number of the pattern within that source." Give its byte offset in the raw file and in the whitespace-normalized text. Does it ground the gate's rule (attribute each ignored path to the file whose pattern decides it)? Also test the doc sentence on `-n`/`--non-matching` (fields empty for non-matching paths) — the gate relies on it for core.excludesFile=/dev/null.
3. Test the reading against git source at v2.56.0 (builtin/check-ignore.c output_pattern / check_ignore; dir.c last_matching_pattern; how a path inside an excluded parent directory is attributed): file:line. Is the attribution for `dir/file` under a `dir/` pattern the parent's pattern (as the gate assumes)?
4. Check corpus/SOURCES.md for an existing row with the same URL+scope (grep check-ignore): is a new row S320 a within-scope duplicate?

# Acceptance
sha256 match/mismatch; anchor with offsets/word count or DISAGREE; source answer with file:line; admit/reject."""),
 ("S76ExecC1", "executor", f"""# Target
Reproduce C1 from committed bytes; run the domain trial and timing.

# Change
1. Run the C1 counter over the W gate ({W}) and over the lane-base gate ({BASE}) (each with its own revision's writer beside it); compare SUMMARY/EXIT/ROW lines with records/c1-after.txt and controls/c1-K-a-do-nothing.txt.
2. Replay controls/c1-K-b-blanket-ignored.txt and controls/c1-K-c-naive-untracked-gitignore.txt from their command= lines (gate dir: the variant copied as souji-pre-report-gate.sh beside the base writer); confirm the variants' sha256 equal the `# gate` lines.
3. Replay records/c1-regress-r36.txt and records/c1-regress-r27.txt with the W gate.
4. Domain trial (read-only): bash {LANE}/tools/souji-pre-report-gate.sh --lane {LANE} --branch master --report {R}/preregistration.txt --prereg {R}/preregistration.txt ; record every check line, rc and wall time (`/usr/bin/time -v` if present). If check-clean FAILs name the cause (uncommitted files from `git status --porcelain` — the wave's own seat files under .ufo/waves are ignored by a tracked rule — or the RECEIPT-UNTRACKED-UNDECLARED-IGNORE line). Count ignored untracked paths and attribute them by source (`git -c core.excludesFile=/dev/null check-ignore -v -n -z --stdin`) grouped by source file.
5. Fail-closed: copy the W gate with NO writer beside it and run the counter: expected-PASS rows must read FAIL.

# Acceptance
Each item REPRODUCED / MISMATCH with observed lines; domain-trial result and timing; fail-closed verdict."""),
 ("S76ExecC2", "executor", f"""# Target
Reproduce C2 from committed bytes; attack the tally's binding.

# Change
1. Run census/round-76/c2-binding-counter.py with --tally census/round-76/c2-kill-tally.py, census/round-75/c2-kill-counter.py and census/round-76/controls/variants/tally-K-b-reject-all.py; compare with records/c2-after.txt, controls/c2-K-do-nothing-r75.txt, controls/c2-K-b-blanket-reject-all.txt.
2. Independently recompute each mutant's expected sha256: apply-edit.py for X09, X15, M08, M14, M15, M17 and X15-then-M17 (P1) onto census/round-75/c1-counter.py; compare with the instrument_sha256= lines in census/round-75/records/c2-after-*-selftest.txt and with census/round-75/records/variants/r75-*-counter.py sha256.
3. Forge receipt sets the tally still ACCEPTS (exit 0) although some slot is not a genuine kill of its mutant: e.g. a receipt whose header binds X09 but whose body is the pristine selftest with fail edited to 1; a receipt with instrument_sha256= repeated twice (first right, second wrong); `command=` containing ' --selftest' only inside a path; a receipt with CRLF line ends; a mutant id given twice with two different receipts; an --edits / --counter override that changes derivation. Write each case under your seat dir and run the tally directly.
4. Positive controls: an honest set reordered, and an honest set where one receipt has trailing blank lines — must still accept.

# Acceptance
REPRODUCED/MISMATCH per receipt; forgery table (case, tally exit, verdict: FALSE-GREEN / REFUSED); findings by severity."""),
 ("S76ExecEvade", "executor", f"""# Target
Try to get `check-clean=PASS` from the W gate ({W}, with its writer beside it) on a fixture carrying uncommitted content that no TRACKED .gitignore declares. Model fixtures on census/round-74/records/wave-repair/probes/evade-probe.py build() in your own scripts.

# Change
Attempt at least: (a) core.excludesFile set to a path of a TRACKED subdir .gitignore (relative and absolute) so its patterns apply at root; (b) an untracked .gitignore placed in a directory that a tracked rule ignores, with a negation `!payload` that would re-include — what does attribution say; (c) a tracked .gitignore with skip-worktree / assume-unchanged and a new rule in the work tree; (d) a .gitignore that is a symlink to a tracked file; (e) a tracked file named `.gitignore` in a dir whose name contains a newline or is `-`; (f) GIT_DIR/info/exclude plus a tracked rule matching the same path (which wins in attribution); (g) a path that ls-files lists but check-ignore reports unmatched (any mismatch makes the gate FAIL — find an HONEST tree that hits it: over-refusal); (h) a sparse-checkout or `core.ignoreCase=true` tree; (i) check-ignore failing (rc 128) — fail closed?
For each: gate rc, check-clean, the detail line, and your label (FORGERY = PASS on content no tracked rule declares; OVER-REFUSAL = FAIL on an honest tree; HANG).

# Acceptance
Route table with verdicts; every FORGERY/OVER-REFUSAL/HANG with a minimal reproduction script in your seat directory."""),
 ("S76MutGate", "mutation-tester", f"""# Target
Mutation-test the W gate change (the `r76 C1` block in tools/souji-pre-report-gate.sh at {W}) against the frozen C1 counter.

# Change
1. Copy the gate and tools/souji-receipt-write.py into one scratch dir. Build at least twelve single-edit mutants of the new block, e.g.: drop `src in tracked`; drop the basename == .gitignore test; drop the ancestor-directory test; drop the `!` negation test; drop `-c core.excludesFile=/dev/null`; drop `-n` (record count mismatch); accept any check-ignore rc; skip the echoed-path check; `if undeclared:` -> `if undeclared > 1:`; tracked from `--others` instead of `--cached`; `ign` from `--exclude-per-directory=.gitignore`; sys.exit(0) on undeclared.
2. For each mutant run the C1 counter. A mutant with SUMMARY mismatches=0 EXIT=0 is a survivor (finding): name the protection the counter does not measure, and if you can, a fixture route that would kill it.
3. Run tests/fixtures/r36-report-gate.py and tests/fixtures/r27-pre-report-gate.sh against two of your survivors (r27 uses the lane gate path: copy the fixture and point GATE at your copy).

# Acceptance
Mutant table: id, edit, SUMMARY, verdict; survivors as findings with severity and a proposed killing route."""),
 ("S76MutTally", "mutation-tester", f"""# Target
Mutation-test the C2 instruments: census/round-76/c2-kill-tally.py and census/round-76/c2-binding-counter.py.

# Change
1. c2-kill-tally.py: at least ten single-edit mutants (drop the instrument-sha compare; drop the --selftest command check; drop the duplicate-digest check; take the LAST instrument_sha256= line; `e = exits[-1]` instead of requiring all EXIT lines to agree; treat UNBOUND as KILLED; skip pristine binding; derive P1 as M17 then X15; ignore composites; `ids.count(mid) != 1` removed). Score each with c2-binding-counter.py. A mutant with `SUMMARY cases=10 mismatches=0` is a survivor (finding): name the case that would kill it.
2. c2-binding-counter.py: at least five mutants (accept rc 2 as reject; ignore the SUMMARY requirement; compare expectations as ints wrongly; skip rows; read the population from a different file). For each, does the r75 do-nothing control still read mismatches=5 and the r76 tally 0? A mutant that lets the r75 tally read 0 is HIGH.

# Acceptance
Mutant tables with verdicts; survivors as findings with severity and killing cases."""),
 ("S76Reviewer", "reviewer", f"""# Target
Review the round-76 diff {BASE}..{A} for correctness.

# Change
1. `git diff {F} {W} -- tools/souji-pre-report-gate.sh .gitignore`: the new Python block inside the quoted heredoc (bytes vs str, `sorted(set)` then join with NUL, check-ignore stdin protocol and deadlock with 25k+ paths, rc 0/1 semantics with -n, record-count arithmetic, ancestor test for root-level `.gitignore` and for sources like `.git/info/exclude`, `os.path.dirname` on bytes, the tracked set from `ls-files --cached` incl. sparse/skip-worktree entries, stderr discarded). Is `.jj/` + `.ruff_cache/` in .gitignore a sound declaration, or does it widen what the gate accepts (what can now hide under .jj/)?
2. census/round-76/c1-evade-counter.py: route set 20+5+5, EXPECT vs c1-population.tsv cross-check, f9/f10/f14/f11/f12 builders produce the intended trees (run them and inspect).
3. census/round-76/c2-kill-tally.py and c2-binding-counter.py: parsing and binding rules vs the receipts (two EXIT= lines per receipt; the forged cases' extra first comment line).
4. Check preregistration.txt against every receipt in census/round-76 (controls/, records/): list mismatches (zero is valid). Run python3 -B tools/souji-freeze-check.py --root {LANE} --prereg census/round-76/preregistration.txt --rev {F} --substance --chronology and at --rev {A}.

# Acceptance
Per item SOUND / DEFECT with file:line; findings by severity."""),
 ("S76CriticClaims", "critic", f"""# Target
Attack the two claims as claims (axis, predicate, controls, separability, do-nothing reachability, label rulings).

# Change
1. C1: the labels are the L1's rulings (f7 relabelled FAIL; f11 PASS; f12 PASS; f2 PASS stays). Is the relabel of f7 chosen to manufacture a delta? Would a gate that refuses any untracked .gitignore meet the target (K-c says f11 kills it — is f11 a fair row or built to separate exactly that control)? Does the .gitignore change (`.jj/`, `.ruff_cache/`) make the domain trial pass for a reason other than the rule? Is the population a fair sample of untracked-rule hiding (missing shapes the W gate still passes)? Run base and W gates on any shape you think is missing.
2. C2: is "calibration" the right axis (the tally is the lane's kill-power self-assessment; count = mismatches between tally verdict and receipt binding)? Can the do-nothing (r75 tally) or a trivial tally reach 0 mismatches (e.g. one that rejects any set containing a receipt with a leading `#` line, or any unknown id)? Build the cheapest such tally and score it.
3. Sourced-claim check: does C1's code actually rest on S320 or only cite it?
4. Universal clauses in the preregistration not enumerated by a counter.

# Acceptance
Per question: HOLDS / QUALIFIED / FALLS with evidence; findings by severity."""),
 ("S76CriticDiscern", "critic", f"""# Target
Discernment attack on the round's rulings and on the routed r75 defects.

# Change
1. Read {LANE}/corpus/lessons/round-75-verifier-spotcheck.md (Routed defects 1-5) and {LANE}/corpus/lessons/round-75.md `## Routed to round 76` (a)-(d). For each, say whether round 76's committed bytes address it, partly address it, or leave it. Evidence from files.
2. Read corpus/QUALITY.md rows Q99, Q120, Q135, Q136. Does the r76 freeze chronology (P {P} strictly before F {F}; controls rev={BASE}) meet Q99/Q120 literally? Does Q136's stated limit now need a superseding row? Propose wording (<=60 words) or argue none.
3. Mission fit: souji = stale/duplicate/preserved artifact census, quarantine before delete, never history or credentials. Is refusing self-ignoring tool directories consistent with that (the lane's own .jj/ is VCS state, not an artifact)? Could the rule push operators to commit broad .gitignore rules that hide more?

# Acceptance
Per item: ADDRESSED / PARTIAL / OPEN with evidence; a proposed QUALITY row or reasoned refusal."""),
 ("S76Sentinel", "sentinel", f"""# Target
Fail-closed / security / resource review of the W gate's new block ({W}).

# Change
1. Command resolution: the new subprocess calls `git` via PATH inside `python3 -I`. Can a repo-local config (core.hooksPath, alias, core.fsmonitor, safe.directory, core.excludesFile already forced) make check-ignore run other code or return forged attribution? Probe in scratch.
2. Resource: a fixture with 200k ignored files under a tracked rule, a deep tree (depth 2000), and 50k paths under a self-ignoring dir — gate wall time, memory, hang? Any stdin/stdout pipe deadlock in check-ignore --stdin with subprocess.run(input=...)?
3. Output: is the undeclared count the only thing printed (no path echo, D30)? Try a path with ANSI escapes and a NUL-adjacent name.
4. Over-refusal risk on the operator's real lanes: run the W gate's attribution logic read-only (not the gate's other checks) over {LANE} and two sibling lane repos (read-only); count undeclared paths per source file. A sibling with undeclared tool caches is not a defect of souji but report it.

# Acceptance
Route table with verdicts (EXEC / SKIP / HANG / clean-refuse / ok); findings by severity with reproduction scripts in your seat dir."""),
 ("S76Scribe", "scribe", f"""# Target
Draft the round's corpus text for the L1 to integrate (drafts only in your seat dir).

# Change
1. Draft SOURCES row S320 (git-check-ignore(1) at git v2.56.0, https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-check-ignore.adoc, capture census/round-76/srcs/git-check-ignore.adoc, sha256 940177c7385eb3cf0ffb1f22ffba35661d16800f8ce787ac676e9a8c89d68208, 4159 bytes, HTTP 200, fetched 2026-11-06) in the exact 11-column shape of corpus/SOURCES.md rows S318-S319 (read them): tier A, status mined, opened 2026-11-06, recheck 180d, used-by corpus/knowledge/filter-filemode-witness.md. Quote <=25 words, located by offset in the whitespace-normalized capture; no `|` in any cell.
2. Draft an r76 section for corpus/knowledge/filter-filemode-witness.md (read its r75 section first): the attribution rule, label rulings (f7 FAIL, f11/f12 PASS), the .gitignore declaration of .jj/ and .ruff_cache/, the tally binding rule and its stated limit, with receipt paths (census/round-76/records/*, controls/*).
3. Validate: copy corpus/ into scratch, append your row after S319 in the Registry table, run /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file <scratch>/corpus/SOURCES.md; report exit code and findings.

# Acceptance
Files: S76Scribe/sources-rows.md, S76Scribe/knowledge-r76.md, S76Scribe/census-validate.txt; the census exit code."""),
]

spec = {
    "wave": "souji-r76-w1",
    "milestone": "souji r76: falsification of C1 gate ignore-source attribution and C2 tally receipt binding",
    "reportDir": ".ufo/waves/round-76/w1",
    "context": context,
    "items": [{"name": n, "role": r, "prompt": HEAD + p} for n, r, p in items],
}
with open(f"{LANE}/.ufo/waves/round-76/w1-spec.json", "w") as f:
    json.dump(spec, f, indent=1)
print(len(items), "items")
