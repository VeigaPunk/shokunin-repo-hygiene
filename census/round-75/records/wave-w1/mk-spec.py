#!/usr/bin/env python3
"""souji r75 wave w1 spec builder (L1 SoujiR75). Writes .ufo/waves/round-75/w1-spec.json."""
import json
import os

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SCR = "/fast/scratch/hyaku/souji-r75"
GS = open(os.path.expanduser("~/.agents/skills/godspeed/directive.md")).read()
HEAD = "/skill:godspeed\n" + GS + "\n\n"
WEAK = "8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0"
BASE = "52d3f07d08422689464598f8be7e2c957fcf0805"
P = "7ba5217d6fc754201615e04e8dfc88cf07c33fd3"
F = "be599cbb02854b9d669a1a2699f15657fd70b336"
I = "f6ec0d7140e0976b8128af803520b895a14a64e0"
W = "1ad737b4a9ac71bd44b6ac849f73387fdc3ab9c5"
A = "5d10e09ed7749f5706eade39ac9a0ae2355aa1f3"
R = f"{LANE}/census/round-75"

context = f"""# Goal
souji round 75 (lane repo {LANE}, lane id souji). The L1 (SoujiR75) holds the planner seat and is the ONLY integration owner: it commits through the lane helper and writes the report. You are one seat of ONE wave of 12 seats. Seats deliver files and findings only. Your mandate is to FALSIFY the frozen round-75 claims and the round's landed changes: re-derive every number yourself from committed bytes; a number you cannot reproduce is a finding. Do not trust the L1's counts.

# Evidence durability
FIRST action: create your report file (the `Report:` trailer path) with a one-line skeleton, and append to it as you go. Your final yield must repeat the same content. A seat that ends without that file counts as no verdict.

# Chronology (binding; read {R}/preregistration.txt first — it is the frozen contract, Q99 grammar)
- Lane base (r74 admitted): {BASE}.
- P {P}: census/round-75/c1-evade-counter.py (C1 counter; imports the 20 r74 routes from census/round-74/records/wave-repair/probes/evade-probe.py and adds f3 f5 f6 f7 f8), c1-population.tsv (25 route ids + expected check-clean), c2-kill-counter.py (C2 counter), c2-mutants.json (X09, X15; composite P1 = X15 then M17 from census/round-74/c2-survivors.json), rec.sh (receipt helper), controls/ (c1-K-a-do-nothing.txt = lane-base gate mismatches=2 EXIT=1; c1-K-b-blanket-ignored.txt = any-ignored-refusal variant mismatches=3 EXIT=1; c2-before-r74-X09/X15/P1/pristine-selftest.txt = r74 counter 62/62; c2-K-do-nothing-r74.txt killed=4/6 EXIT=1; c2-K-blanket-pristine-red.txt), controls/variants/, srcs/gitignore.adoc + git-ls-files.adoc (git v2.56.0), records/census-before.txt.
- F {F}: census/round-75/preregistration.txt (freeze-check: records/freeze-check.txt, `SUMMARY claims=2 findings=0`).
- I {I}: census/round-75/c1-counter.py = census/round-74/c1-counter.py + two selftest checks (search `r75 C2`).
- W {W}: tools/souji-pre-report-gate.sh check 4 — inside the heredoc, after the truth check: untracked paths listed by `git ls-files -o -i --exclude-standard` minus those listed by `--exclude-per-directory=.gitignore` fail clean (RECEIPT-UNTRACKED-LOCAL-EXCLUDE).
- A {A}: records/c1-after.txt (W gate: rows=25 mismatches=0 EXIT=0), records/c2-after-*-selftest.txt, records/c2-after.txt (killed=6/6 pristine PASS EXIT=0), records/variants/r75-*-counter.py.

# Claims (frozen predicates are in the preregistration; never change them)
C1 operability (sourced on S318 gitignore(5) and S319 git-ls-files(1), both opened this round): the pre-report gate refuses untracked content hidden only by a repository-local ignore source (info/exclude, core.excludesFile) while accepting content hidden by committed .gitignore rules. Counter 25 rows: mismatches 2 -> 0; blanket control stays red; domain trial on the lane at the report tip check-clean=PASS. Stated limit: a self-ignoring untracked .gitignore (f7, the .jj/ and .ruff_cache/ shape) is accepted.
C2 calibration: the r75 counter's own selftest kills X09 (new slot unscoped) and P1 (X15 then M17), keeps M08 M14 M15 M17 killed, pristine 64/64: killed 4/6 -> 6/6.

# Frozen invocations (run from {LANE}; never alter counters, populations, edit sets, probes or controls)
- C1: copy the gate and tools/souji-receipt-write.py at a revision into ONE dir (`git show <rev>:tools/souji-pre-report-gate.sh > D/souji-pre-report-gate.sh`, same for the writer); python3 -B census/round-75/c1-evade-counter.py --gate-dir D --work <SCRATCH>/c1 (work must be absent or empty; ~10 s).
- C2 selftest: python3 -B <counter> --selftest --root {LANE} --matrix census/round-73/c1-matrix.tsv --base-rev {WEAK} --work <existing empty dir> (~55 s). Edits: python3 -B census/round-73/apply-edit.py --set census/round-75/c2-mutants.json (or census/round-74/c2-survivors.json) --id <ID> --src census/round-75/c1-counter.py --out <SCRATCH>/<ID>.py.
- C2 tally: python3 -B census/round-75/c2-kill-counter.py --pristine <receipt> --mutant ID=<receipt> ...
- Every receipt starts with `command=<literal command>` (rec.sh); replaying that line with your scratch prefix is a valid check.
<SCRATCH> must be a fresh directory under {SCR}/<your seat name>/ (mkdir -p it). Counters refuse --work under /tmp, /var/tmp or /dev/shm. Many arms in parallel are fine (32 cores) but check load.

# Write scope and bounds
You write ONLY under {LANE}/.ufo/waves/round-75/w1/ (your own seat directory <SeatName>/ and your own <SeatName>.md) and under your scratch dir. Never edit lane tracked files (census/, tools/, corpus/, SCORECARD.md, LOG.md, PROVINCE.md, SKILL.md, SHONEN.md). Never edit MANIFEST.json, .ufo/state/, .ufo/watchdog.log, /home/vgpnk/Projects/shokunin/templates/, /home/vgpnk/Projects/shokunin/scripts/, /home/vgpnk/Projects/shokunin/.scratch/, or any sibling repo. Never commit, push, stash, reset, checkout, switch, pull, or run any mutating git or jj command in the lane or the fleet repo. Read-only git (show, log, diff, status, rev-parse, cat-file, ls-files, ls-remote) is fine; read-only jj only with --ignore-working-copy.
Fixture repos (round-70 fleet incident: a mktemp template without XXXXXX made `git -C ""` fall back to the fleet root and commit there): create D=$(mktemp -d -p "{SCR}/<seat>" fx.XXXXXX) and immediately check `[ -n "$D" ] && [ -d "$D" ] || exit 1`; git -C "$D" init -q; verify `[ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ]` before the first commit; name -C "$D" on every later git call (never a bare `git commit`, never an unchecked variable after -C); in Python assert the -C/cwd path is absolute and non-empty. Commit only with an explicit fixture identity inside $D. To mutate a file, copy it into your scratch dir first; never edit it in the lane. Bind every shell variable in the same shell that uses it (an `A=... && cmd &` chain backgrounds the whole chain; round-75 L1 slip).
Host paths outside your scratch (/boot, /etc, /usr, /var, /efi, other homes) are read-only inputs: never run a binary-editing tool on them. Never run sudo, never change host sysctls or kernel parameters; if a probe needs one, report the need instead. Never message agent://all; never call the task tool.
Scratch discipline: mkdir -p "{SCR}/<seat>" and pass it explicitly (TMPDIR, --work); trap 'rm -rf -- "$S"' EXIT in shell (copy receipts to your seat directory first, small text only). Check bash /home/vgpnk/Projects/shokunin/scripts/hyaku/disk-guard.sh status before any heavy pass; on ENOSPC report the free space you saw and stop. Remove your scratch dir before you yield.
Every `Report:` trailer path is relative to {LANE}; write it at {LANE}/<that path>. All paths you name must be absolute under {LANE} or your scratch dir.

# Tooling authorization (operator, 2026-10-19)
You and every seat may install or upgrade tools that help the task. Read /home/vgpnk/.omp/agent/RULES.md first (official channels, update-safety gate; record tool, version, channel and reason in your report). pacman transactions are PAUSED host-wide (orchestrator ruling 2026-10-20): install via uv tool, npx, or an official binary in ~/.local/bin, or file an L0 question. Never run pacman -Sy, -Syu, -U, -R or a downgrade; before any future pacman -S run pacman -Sp --print-format '%n %v' and proceed only for packages not yet installed.

# Report format
Keep it under 40 lines: verdict per item, the exact commands you ran, the observed output lines that decide the verdict, file:line evidence, and any finding tagged HIGH, MEDIUM or LOW. Name every file you wrote under your seat directory. The report file and your final yield carry the same content.
"""

items = [
 ("S75Connector", "connector", f"""# Target
Cross-claim separation and sibling-overlap scan for round 75. Read-only.

# Change
1. Causal separation: confirm from receipt `# bind`/`instrument=` lines that no C1 receipt (records/c1-after.txt, controls/c1-K-*.txt) reads a C2 counter byte and no C2 receipt (records/c2-*.txt, controls/c2-*.txt) reads a gate byte. Verdict SEPARABLE/COUPLED.
2. List every other lane tool that decides "nothing uncommitted" from `git status` with ignored files left out (tools/souji-verify.sh, tools/souji-record-agreement.py:351, tools/souji-guard.r9-s18.sh, tools/souji-idx-repair.py, tools/souji-receipt-write.py _status_z, any other): file:line; would an info/exclude-hidden file change its verdict?
3. Sibling overlap (read-only; other *-shokunin repos under /home/vgpnk/Projects/shokunin): which sibling pre-report/landing gates read cleanliness from `git status --porcelain` and so miss info/exclude-hidden files? Table: lane, file:line, vulnerable yes/no.

# Acceptance
Tables with verdicts and file:line; findings by severity."""),
 ("S75ScoutSources", "scout", f"""# Target
Re-open the round's two new sources and test the sentences the C1 claim rests on. Read-only on the lane.

# Change
1. Fetch https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitignore.adoc and .../git-ls-files.adoc yourself (curl -sSL); compare sha256 with {R}/srcs/gitignore.adoc (338221577b4f…5e71) and {R}/srcs/git-ls-files.adoc (56af3aad88df…a74b). Also fetch https://git-scm.com/docs/gitignore and report its version banner.
2. Locate and word-count (must be <=25) these candidate anchors: gitignore.adoc "Patterns which are specific to a particular repository but which do not need to be shared with other related repositories"; git-ls-files.adoc "To emulate what `--exclude-standard` specifies, you can give `--exclude-per-directory=.gitignore`, and then specify:". Give byte offsets in the raw files. Do they ground (a) info/exclude is repository-local/unshared and (b) --exclude-per-directory alone does NOT read info/exclude or core.excludesFile? Propose better anchors if not.
3. Test (b) against git source at v2.56.0 (builtin/ls-files.c: how --exclude-standard vs --exclude-per-directory call setup_standard_excludes / add_patterns): file:line.
4. Check corpus/SOURCES.md for an existing row with the same URL+scope (S047 and S276 cite git-scm gitignore with other scopes; S292 git-ls-files -v/-t): is a new row a within-scope duplicate?

# Acceptance
sha256 match/mismatch; anchors with offsets/word counts or DISAGREE; source answer with file:line; admit/reject per source."""),
 ("S75ExecC1", "executor", f"""# Target
Reproduce C1 from committed bytes; run the domain trial.

# Change
1. Run the C1 counter over the W gate ({W}) and over the lane-base gate ({BASE}) (each with its own revision's writer beside it); compare SUMMARY/EXIT/ROW lines with records/c1-after.txt and controls/c1-K-a-do-nothing.txt.
2. Replay controls/c1-K-b-blanket-ignored.txt from its command= line (gate dir: controls/variants/gate-K-b-blanket-ignored.sh copied as souji-pre-report-gate.sh beside the base writer).
3. Domain trial: run the W gate directly on the lane (read-only): bash {LANE}/tools/souji-pre-report-gate.sh --lane {LANE} --branch master --report {R}/preregistration.txt --prereg {R}/preregistration.txt ; record every check line, rc and wall time. If check-clean FAILs, name the cause (uncommitted files from `git status --porcelain`, or the new RECEIPT-UNTRACKED-LOCAL-EXCLUDE line). Also count `git -C {LANE} ls-files -o -i --exclude-standard | wc -l` vs `--exclude-per-directory=.gitignore`.
4. Fail-closed: copy the W gate with NO writer beside it and run the counter: expected-PASS rows must read FAIL.

# Acceptance
Each item REPRODUCED / MISMATCH with observed lines; domain-trial result and timing; fail-closed verdict."""),
 ("S75ExecC2", "executor", f"""# Target
Reproduce C2 from committed bytes; attack the two new selftest checks.

# Change
1. Apply X09, X15, P1 (X15 then M17), M08, M14, M15, M17 to census/round-75/c1-counter.py; run each --selftest; compare SELFTEST/EXIT and the failing check names with records/c2-after-*-selftest.txt. Run the pristine r75 selftest. Run c2-kill-counter.py over your receipts; compare with records/c2-after.txt.
2. Diff census/round-74/c1-counter.py vs census/round-75/c1-counter.py: confirm only the docstring and the two selftest blocks changed (no evaluate()/verdict change). Any other hunk is a finding.
3. Attack the X09 detector: it monkeypatches tree_divergence. Build two other single-edit mutants of the new-slot scoping (e.g. `row_scope(spec, n_post)` only for n_post; scope n_pre only; scope with forge_paths of a different row) and say whether the r75 selftest kills them.
4. Attack the M17 second detector: build a mutant where the new slot reads only the post-run divergence (`n_wit = bool(n_post)`), and one where row_fate records base witness instead of new; killed or survived?

# Acceptance
REPRODUCED/MISMATCH per receipt; mutant table for items 3-4; findings by severity."""),
 ("S75ExecEvade", "executor", f"""# Target
Try to get `check-clean=PASS` from the W gate ({W}, with its writer beside it) on a fixture carrying an uncommitted lane change, through the ignore surface and the new code. Model fixtures on census/round-74/records/wave-repair/probes/evade-probe.py build() in your own scripts.

# Change
Attempt at least: (a) core.excludesFile via GIT_CONFIG_GLOBAL / HOME/.gitconfig / XDG_CONFIG_HOME/git/ignore in the caller env (does --exclude-standard read it, does the gate scrub it?); (b) a pattern in info/exclude that ALSO appears in a committed .gitignore elsewhere (subdir scoping); (c) a negated pattern `!new.txt` in a committed .gitignore with info/exclude re-ignoring; (d) an untracked .gitignore inside an existing tracked directory that ignores a new file (and itself); (e) a tracked .gitignore modified with skip-worktree to add a rule; (f) a file under an ignored directory where the directory rule comes from info/exclude but a committed rule matches the file name; (g) `git ls-files` failing (e.g. unreadable directory) — does the gate fail closed; (h) GIT_DIR/GIT_WORK_TREE/GIT_COMMON_DIR via env or core.worktree pointing the ls-files call elsewhere; (i) a path with newline or non-UTF-8 bytes. Also run each honest twin (expected PASS) to detect OVER-REFUSAL.
For each: gate rc, check-clean, and your own label (FORGERY = PASS on an uncommitted change not covered by a committed rule; OVER-REFUSAL = FAIL on an honest tree; HANG).

# Acceptance
Route table with verdicts; every FORGERY/OVER-REFUSAL/HANG with a minimal reproduction script in your seat directory."""),
 ("S75MutGate", "mutation-tester", f"""# Target
Mutation-test the W gate change (the `r75 C1` block in tools/souji-pre-report-gate.sh at {W}) against the frozen C1 counter.

# Change
1. Copy the gate and tools/souji-receipt-write.py into one scratch dir. Build at least ten single-edit mutants of the new block, e.g.: swap the two set operands; `if hidden:` -> `if not hidden:`; drop `--ignored`; drop `--others`; replace `--exclude-per-directory=.gitignore` with `--exclude-standard`; replace `--exclude-standard` with `--exclude-per-directory=.gitignore`; ignore the ls-files rc (return empty set); sys.exit(0) on hidden; move the block before the truth loop; drop `-z` (split on newline).
2. For each mutant run the C1 counter. A mutant with SUMMARY mismatches=0 EXIT=0 is a survivor (finding): name the protection the counter does not measure.
3. Re-run census/round-74 fixtures r27/r36 regressions against the W gate if present (see census/round-74/records/regress-*.txt for their commands).

# Acceptance
Mutant table: id, edit, SUMMARY, verdict; survivors as findings with severity; regression results."""),
 ("S75MutCounter", "mutation-tester", f"""# Target
Mutation-test the C2 instruments: census/round-75/c2-kill-counter.py and the two r75 selftest blocks of census/round-75/c1-counter.py.

# Change
1. c2-kill-counter.py: at least eight single-edit mutants (accept EXIT=2 as killed; count `fail>=0` as killed; ignore pristine; first SELFTEST line wins when several; treat UNREAD as KILLED; exit 0 when killed>0; parse EXIT from the first EXIT= line instead of the last; drop the f>=1 test). Score each over records/c2-after-*.txt and controls/c2-*.txt receipts and over two forged receipts you write in scratch (a receipt with `SELFTEST ... fail=1` but last line EXIT=0; one with two SELFTEST lines). A mutant that gives the same verdicts on all receipts is a survivor.
2. The r75 selftest blocks: at least six single-edit mutants (e.g. `is not True` -> `is False`; drop `len(...) == len(wrows)`; FM1 -> FM2 in the set-up-only test; the off-path name changed to a forge path of FM1; restore tree_divergence before evaluate; check only sc["base_unwitnessed"]). Run --selftest on each; a mutant with 64/64 is a survivor — then say whether it would still kill X09/P1.

# Acceptance
Mutant tables with verdicts; survivors as findings with severity."""),
 ("S75Reviewer", "reviewer", f"""# Target
Review the round-75 diff {BASE}..{A} for correctness.

# Change
1. `git diff {F} {W} -- tools/souji-pre-report-gate.sh`: the new Python block inside the quoted heredoc (variable `lane` scope, `-I` isolation, subprocess env inherited from the gate's scrubbed env, PATH lookup of git, stderr discarded, set difference on raw bytes, behaviour with 25k ignored files on the lane, `-c core.fsmonitor=false` relevance to ls-files).
2. census/round-75/c1-evade-counter.py: imports the r74 probe by path (is the bound digest printed and is the route set really 20+5?), EXPECT vs c1-population.tsv cross-check, error handling, the f3..f8 builders really produce the intended trees (read and run them).
3. census/round-75/c2-kill-counter.py: parsing rules vs the receipts it reads (two EXIT= lines in each receipt: the counter's own and rec.sh's).
4. Check preregistration.txt against every receipt in census/round-75 (controls/, records/): list mismatches (zero is a valid result). Run tools/souji-freeze-check.py --root {LANE} --prereg census/round-75/preregistration.txt --rev {A} --substance --chronology.

# Acceptance
Per item SOUND / DEFECT with file:line; findings by severity."""),
 ("S75CriticClaims", "critic", f"""# Target
Attack the two claims as claims (axis, predicate, controls, separability, do-nothing reachability, label rulings).

# Change
1. C1: the expected labels are the L1's rulings (n-filemode-config FAIL, f2-gitignore PASS, f7-selfignore-dir PASS). Is any label chosen to make the candidate pass? Would a gate that refuses only info/exclude (not core.excludesFile) meet the target (f3 is FAIL at base already — why; which code catches it)? Is the 25-row population a fair sample of the ignore surface, or does it omit a hiding source the W gate still passes (global excludes file, subdirectory .gitignore committed later, `git add -f`'d ignored tracked file)? Run the base and W gates on any shape you think is missing.
2. C2: does the X09 detector test scoping or only the monkeypatched path (would any counter whose new-slot witness ignores divergences pass)? Is P1 a fair target or constructed to be killed? Can the do-nothing (r74 counter) or a selftest that always fails reach the target (controls/c2-K-*)?
3. Sourced-claim check: does C1's code/claim actually rest on S318/S319 or only cite them?
4. Universal clauses in the preregistration not enumerated by a counter.

# Acceptance
Per question: HOLDS / QUALIFIED / FALLS with evidence; findings by severity."""),
 ("S75CriticDiscern", "critic", f"""# Target
Discernment attack on the round's rulings and on the routed r74 defects.

# Change
1. Read {LANE}/corpus/lessons/round-74-verifier-spotcheck.md (Routed defects 1-4). For each, say whether round 75's committed bytes (preregistration domain-trial wording; n-filemode-config ruling; the ignored-untracked rows) address it, partly address it, or leave it. Evidence from files.
2. Read corpus/QUALITY.md rows Q99, Q120, Q133-Q135. Does the r75 freeze chronology (P {P} strictly before F {F}; records/freeze-check.txt) meet Q99 and Q120 literally? Any gap is a finding.
3. Is ruling f2-gitignore PASS consistent with the lane's mission (souji = stale/duplicate artifact census; "never history or credentials")? Could a committed `.gitignore` rule hide a credential-shaped untracked file the gate should still refuse? Propose a QUALITY row wording (<=60 words) for the ignore-source rule with its stated limit, or argue none is needed.

# Acceptance
Per item: ADDRESSED / PARTIAL / OPEN with evidence; a proposed QUALITY row or reasoned refusal."""),
 ("S75Sentinel", "sentinel", f"""# Target
Fail-closed / security review of the W gate's new block ({W}).

# Change
1. Command resolution: the new subprocess calls `git` via PATH from inside `python3 -I`. Can a caller PATH or a repo-local config (core.hooksPath, alias, core.fsmonitor, safe.directory) make ls-files run other code or return a forged empty listing? Probe in scratch.
2. Resource: a fixture with 200k ignored files, a deep directory tree (depth 2000) and a FIFO named in an ignored directory — gate wall time, memory, hang?
3. Output: is the hidden count the only thing printed (no path echo, D30)? Try a path with ANSI escapes.
4. Does `--exclude-standard` read a caller-env core.excludesFile (GIT_CONFIG_COUNT/KEY/VALUE, GIT_CONFIG_PARAMETERS — the gate unsets them; check the order) or HOME/XDG? If the operator's global excludes hide an editor swap file in the lane, does the gate FAIL (over-refusal risk)? Measure with a fixture HOME.

# Acceptance
Route table with verdicts (EXEC / SKIP / HANG / clean-refuse / ok); findings by severity with reproduction scripts in your seat dir."""),
 ("S75Scribe", "scribe", f"""# Target
Draft the round's corpus text for the L1 to integrate (drafts only in your seat dir).

# Change
1. Draft SOURCES rows S318 (gitignore(5) at git v2.56.0, https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitignore.adoc, capture census/round-75/srcs/gitignore.adoc) and S319 (git-ls-files(1) at v2.56.0, .../git-ls-files.adoc, capture census/round-75/srcs/git-ls-files.adoc) in the exact 11-column shape of corpus/SOURCES.md rows S315-S317 (read them): tier A, status mined, opened 2026-11-06, recheck 180d, used-by corpus/knowledge/filter-filemode-witness.md. Quote <=25 words each, located by byte offset in the capture; no `|` in any cell.
2. Draft an r75 section for corpus/knowledge/filter-filemode-witness.md (read its r73/r74 sections first): the gate's ignore-source check, the label rulings, the stated limit f7, the C2 selftest detectors, with receipt paths (census/round-75/records/*, controls/*).
3. Validate: copy corpus/ into scratch, append your rows after S317 in the Registry table, run /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file <scratch>/corpus/SOURCES.md; report exit code and findings.

# Acceptance
Files: S75Scribe/sources-rows.md, S75Scribe/knowledge-r75.md, S75Scribe/census-validate.txt; the census exit code."""),
]

spec = {
    "wave": "souji-r75-w1",
    "milestone": "souji r75: falsification of C1 gate ignore-source rule and C2 counter selftest kills (X09, P1)",
    "reportDir": ".ufo/waves/round-75/w1",
    "context": context,
    "items": [{"name": n, "role": r, "prompt": HEAD + p} for n, r, p in items],
}
with open(f"{LANE}/.ufo/waves/round-75/w1-spec.json", "w") as f:
    json.dump(spec, f, indent=1)
print(len(items), "items")
