#!/usr/bin/env python3
"""Builds .ufo/waves/round-43/w1-spec.json (souji r43 single v2 wave: build + attack, 64-128 seats). Run: python3 make-spec-w1.py"""
import json
import os

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
RD = LANE + "/census/round-43"
W = LANE + "/.ufo/waves/round-43/w1"
SCR = "/fast/scratch/hyaku/souji-r43"
INST = "f8c805dbfa7f45814cf9a7270fa8bbffb41a8373"   # instruments rev (c2-before receipt committed)
TIP = "13de0e84b45efd1113f077d58fc1e89bc586a013"     # master now
BASE = "619a75034dd6324e1a725f73034c59f7bf9558ef"   # round base (r42 spotcheck tip)
GODSPEED = ("/skill:godspeed\n\n" + open(os.path.expanduser("~/.agents/skills/godspeed/directive.md"),
                                          encoding="utf-8").read().rstrip("\n") + "\n\n")

CONTEXT = f"""# Goal
souji round 43, wave 1 (single v2 wave: build and attack together; candidates are built by executor items and falsified by attack items that read the FROZEN instruments and the pinned base bytes). Lane: {LANE}. Round claims are frozen-instrument-backed; the
instruments are COMMITTED at {INST} and are FROZEN for candidate scoring (defects you find are
findings for the L1, never fixes by you). Master tip: {TIP}. Read-only lane access; your writes go
only to your own directories named in your item.
# The three claims (already frozen; you build CANDIDATES or attack instruments)
- C1 calibration: `census/round-43/c1-counter.py` reads correction prose in
  `corpus/lessons/round-43.md` against the frozen register `census/round-43/c1-required.tsv`
  (rejects fenced/duplicate/retracted/malformed corrections, re-derives R39-D1/D2/D3 from committed
  bytes, counts new declared-evidence mismatches beyond the base line count). Its discrimination
  fixture `tests/fixtures/r43-correction-prose.py` reads 20/20 (r43 column 10/10, r42 defect
  signatures 10/10, receipt `/fast/scratch/hyaku/souji-r43/l1/fixture-cal4.txt` — a scratch path,
  for context only). The round's own corrections land AFTER the wave; you do not write them.
- C2 operability: candidates for `tools/souji-freeze-check.py` speaking the r43 grammar (see the
  docstring of `census/round-43/c2-counter.py` — it is normative). Scored by
  `census/round-43/c2-counter.py`; the before receipt is `census/round-43/controls/c2-before.txt`
  (current bytes: newtable=2/9, r42table=ok, hidden=RED, real=RED).
- C3 coverage: candidates for `tests/fixtures/r43-drift-survivors.py` (kills the 16 frozen
  population mutants of `census/round-43/c3-survivors.tsv` + fails exactly case-json-symlink-leaf
  on the pinned bytes) and candidates for `tools/souji-worktree-drift.py` (N10: refuse a leaf
  symlink named by --json with `REFUSAL JSON-TARGET-SYMLINK:` exit 2, WITHOUT changing any frozen
  anchor string — the population and EQUIV anchors in `census/round-43/c3-counter.py` must each
  still occur exactly once, and the nine committed drift fixtures must stay green).
# Scoring candidates (read-only for the lane; the clone is yours)
`bash {RD}/score-candidate.sh <c1|c2|c3> <your-scratch-root> <dest>=<file>...` clones master,
swaps your candidate in (allowlist: tools/souji-freeze-check.py, tools/souji-worktree-drift.py,
tests/fixtures/r43-drift-survivors.py, tests/fixtures/r43-correction-prose.py,
census/round-43/c1-required.tsv, corpus/lessons/round-43.md, SCORECARD.md), commits in the CLONE
only and runs the counter. c2/c3 scoring takes up to ~20 minutes (the c3 old_killed leg runs 144
fixture executions) — start it early and work on your report while it runs. Candidate files must
be standalone (a fixture is one Python file; the tool is one Python file).
# Scope and rules
Read-only over the lane; a candidate, probe or draft goes ONLY under its own directory
{W}/<seat-name>/ and never into tests/, tools/, census/, corpus/, SKILL.md or any tracked path.
Seats never commit, push or run any mutating git or jj command in the lane or fleet; the L1 alone
lands through jj-lane.sh. Never write the fleet repo, sibling lanes, .ufo/state, the watchdog log,
operator config, templates or fleet scripts. Use absolute lane paths. Never run as root; never
signal processes you did not spawn. Leaf members: no subagent dispatch.
Scratch: every clone, work dir and fixture lives under {SCR}/<seat-name>/ (mkdir -p it; pass
TMPDIR and --work/--scratch explicitly; never rely on an inherited TMPDIR); /tmp only for files
under 50 MB; delete your scratch dir before you yield (trap 'rm -rf -- "$S"' EXIT in shell,
finally: shutil.rmtree in Python) after copying any receipt you need into your seat directory.
A report may cite only paths that are committed or inside your seat directory; a /tmp or scratch
path is never evidence. Git fixtures: D=$(mktemp -d -p {SCR}/<seat-name>) and every later git
call names -C "$D"; verify `git -C "$D" rev-parse --show-toplevel` = $D before the first commit;
author identity ONLY through GIT_AUTHOR_*/GIT_COMMITTER_* env vars, and NEVER export them into
your shell session (a leaked fixture identity breaks the lane helper's push — keep them per-
command). Read-only jj in the lane only with --ignore-working-copy.
Tooling authorization (operator, 2026-10-19): you may install or upgrade tools that help the task;
read /home/vgpnk/.omp/agent/RULES.md first (official channels, update-safety gate; record tool,
version, channel, reason in your report). pacman guard: ALL pacman transactions are paused
host-wide; install via uv tool/npx/an official binary in ~/.local/bin or file the need in your
report; never -Sy, -Syu, -U, -R, downgrade or restart a host service.
Every `Report:` trailer path is relative to {LANE}: write it at {LANE}/<that path>. Report exact
commands run, their observed output and a verdict; unrun is not pass; never fabricate. Every
finding names what it attacks. Return a summary of at most 10 lines."""

items = []


def add(name, role, axes, task, accept):
    name = name.replace("-", "")[:32]
    prompt = GODSPEED + (f"# Target\nsouji round 43 wave 1 item {name} (role {role}).\n# Task\n{task}\n"
                         f"# Acceptance\nWrite your evidence report at {W}/{name}.md with exact commands, "
                         f"observed output and a verdict. {accept}")
    items.append({"name": name, "role": role, "axes": axes, "prompt": prompt})


C2_GRAMMAR = ("r43 grammar (normative — copy these semantics into your tool's docstring verbatim): "
              "KEY-DUPLICATE first-wins (the first occurrence's value is evaluated; every further "
              "occurrence one KEY-DUPLICATE finding); UNATTACHED-KEY (new class C0: a key line after a "
              "malformed `##` heading and before the next valid `## C<digits>` heading is reported "
              "`FINDING C0 UNATTACHED-KEY line=<n>`, never dropped, never attached to a claim); "
              "ROUND-MALFORMED (new class C0: any column-0 line starting `Round:` that is not "
              "`Round: <strict ASCII digits>` — including zero-padded, fullwidth or suffixed digits — "
              "yields `FINDING C0 ROUND-MALFORMED detail=<text>` and no dispatch scan; a missing Round "
              "line stays C0 FIELD-MISSING Round); CONTROL-SYMLINK (new class C1: the Control path is a "
              "symlink at FREEZE — one finding and the red-control read is refused, so a link text "
              "`EXIT=1` or `EXIT=0` never passes); FROZEN-EDITED extended to the Control blob and the "
              "preregistration text itself between FREEZE and REV (C1 for the Control, C0 for the "
              "preregistration); CRLF preregistration lines parse (a trailing CR is stripped before "
              "matching); `--selftest` still prints `SELFTEST cases=<n> pass=<n> fail=<n>` with n>=31, "
              "all passing, and works when TMPDIR is unset or names a missing directory. All r41/r42 "
              "classes and behaviors stay (the r42 counter must still read cases=37 pass=37 on your "
              "bytes — the counter's r42table leg re-runs the whole r42 table at the r42 measured tip "
              "34343a39ffab8029b06e8e6c9ac699ebcbd65f8a with your tool swapped in).")

for i, approach in enumerate([
        "smallest-diff: patch the committed tool minimally, preserving its structure",
        "clean-room: rewrite the checker from the grammar, keeping the r41/r42 CLI and output shapes",
        "table-driven: reorganize evaluation around a class/trigger table with the new classes as rows",
        "parser-first: a strict block parser producing claims/unattached/malformed events, then a checker",
]):
    add(f"R43executor{i+1:02d}", "executor", ["operability"],
        (f"Build ONE candidate tools/souji-freeze-check.py ({approach}). {C2_GRAMMAR} "
         f"Base your work on the committed bytes (`git -C {LANE} show {INST}:tools/souji-freeze-check.py`). "
         f"Score it before you report: `bash {RD}/score-candidate.sh c2 {SCR}/<you> "
         f"tools/souji-freeze-check.py=<your file>` — the printed SUMMARY must reach "
         f"`newtable=9/9 r42table=ok hidden=ok hidden_ctrl=REJECTED real=RED selftest=ok tmpdir=ok "
         f"control_clean=REJECTED control_findings=REJECTED` (real=RED is EXPECTED at this scoring "
         f"revision: census/round-43/preregistration.txt does not exist yet; a candidate whose real "
         f"leg is red for that reason alone has met the target). Copy the candidate into "
         f"{W}/<seat-name>/candidate.py with its sha256."),
        "The scoring SUMMARY line verbatim, the candidate path+sha256, and any grammar clause you "
        "could not satisfy (a candidate that fails a case must say so — do not hide it).")

add("R43executor05", "executor", ["coverage"],
    (f"Build the candidate TOOL half of C3: tools/souji-worktree-drift.py with the N10 fix. Base: "
     f"`git -C {LANE} show {BASE}:tools/souji-worktree-drift.py` (sha256 "
     f"b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6). Defect (R41sentinel01 F1): "
     f"`json_target = os.path.realpath(os.path.abspath(args.json))` resolves a leaf symlink BEFORE the "
     f"guards, so the write follows the link and the documented O_NOFOLLOW walk never sees it. Fix: "
     f"refuse a --json path whose FINAL component is a symlink with "
     f"`REFUSAL JSON-TARGET-SYMLINK: <path> names a symlink` on stderr and exit 2, checked with "
     f"os.lstat before any guard or write (a leaf symlink is refused whether or not its target "
     f"exists; ancestors may stay realpath-resolved per the documented r37/r38 contract; a missing "
     f"leaf is still created). HARD CONSTRAINTS: every old/new anchor string in "
     f"`census/round-43/c3-counter.py` (MUTANTS and EQUIV tuples) must still occur EXACTLY ONCE in "
     f"your bytes; the nine committed drift fixtures must stay green on your tool (run at least "
     f"tests/fixtures/r42-drift-conditions.py and r38-drift-write-envelope.py yourself: "
     f"`python3 -B tests/fixtures/<f>.py --tool <your tool> --work <scratch dir>` must exit 0); do "
     f"not change any output byte for non-symlink inputs. Score the pair you cannot finish alone — "
     f"the fixture is another seat's item; instead verify your refusal directly (a scratch symlink "
     f"target run must print the refusal and exit 2). Copy the candidate into "
     f"{W}/<seat-name>/candidate.py with its sha256 and the anchor-uniqueness check output "
     f"(python: for each old/new in the counter's tuples, text.count(old)==1)."),
    "The anchor-uniqueness output (all unique), two fixture green runs, the direct refusal probe, "
    "candidate path+sha256.")

add("R43executor06", "executor", ["coverage"],
    (f"Build the candidate FIXTURE half of C3: tests/fixtures/r43-drift-survivors.py. Protocol: "
     f"`python3 -B <fixture> --tool PATH --work DIR` prints `case-<name>=PASS|FAIL` lines and "
     f"`SUMMARY cases=<n> pass=<p> fail=<f>`; exit 0 iff fail=0; every case runs the tool as a "
     f"subprocess with a whitelisted env (PATH, TMPDIR=work, LC_ALL=C, GIT_CONFIG_NOSYSTEM=1, "
     f"GIT_CONFIG_GLOBAL/SYSTEM=/dev/null, GIT_TERMINAL_PROMPT=0) and asserts only behaviour (exit "
     f"code, stdout/stderr tokens, --json file bytes/mode); the fixture must set umask 0o022 in its "
     f"own process for the mode case; restore anything it chmods in a finally. Frozen case names "
     f"(the counter knows case-json-symlink-leaf by name; the others map to the population probes "
     f"of census/round-43/c3-survivors.tsv column 4): case-big-record-fully-parsed (S03: a record "
     f"with ~3000 REPO rows, >64 KiB, must parse fully), case-total-trailing-junk-refused (S11), "
     f"case-repo-name-with-space (S12), case-empty-regs-refused (S13), "
     f"case-total-prunable-below-rows-refused (S17), case-root-named-not-a-repo (S22), "
     f"case-unreadable-root-listed-absent (S25: chmod 000 the root, assert DRIFT ABSENT lines and "
     f"no traceback, restore in finally), case-symlinked-root-measured (S33), "
     f"case-relative-root-basename (S34: run the tool with cwd=work and --root . where the cwd "
     f"basename names a repo), case-gitdir-probe-honors-timeout (S35: a repo whose .git/HEAD is a "
     f"FIFO, --timeout 1, assert the run returns well under 12s and reports UNREACHABLE), "
     f"case-regs-rise-reported (S43: record regs=1, live worktrees 2 -> REGS-CHANGED), "
     f"case-prunable-fall-reported (S44: record prunable=1, live 0 -> PRUNABLE-CHANGED), "
     f"case-json-sibling-prefix-written (S53: --json under rootX beside root must be written), "
     f"case-json-created-mode (S58: created --json mode is 0644 under umask 022), "
     f"case-json-empty-string-ignored (S63: --json '' writes nothing, rc 0), "
     f"case-timeout-float-refused (S73: --timeout 1.5 exits 2), case-json-symlink-leaf-refused "
     f"(N10: --json via a leaf symlink must be refused — this case FAILS on the pinned bytes "
     f"sha256 b2a603cf... and PASSES on the fixed tool; the fixture itself must not read the "
     f"tool's bytes, only run it). Requirements: >= 17 cases; each case independent (own scene "
     f"dir); no case reads the tool source; deterministic under host load (generous internal "
     f"margins; a tool-level timeout is the expected refusal, never a survivor). Validate your "
     f"fixture against the pinned bytes: exactly case-json-symlink-leaf must fail, and your "
     f"fixture must kill at least 8 of the 16 population mutants (apply the mutants per the "
     f"counter's MUTANTS tuples to a scratch copy of the pinned tool and run your fixture over "
     f"each; the full 16-kill validation is the counter's job, partial evidence is enough to "
     f"report). Copy the fixture into {W}/<seat-name>/candidate.py with its sha256."),
    "The pinned-bytes run (exactly one FAIL, named), your per-mutant kill table (at least 8 rows), "
    "fixture path+sha256.")

add("R43executor07", "executor", ["coverage"],
    (f"Second independent candidate tests/fixtures/r43-drift-survivors.py — same frozen protocol and "
     f"case names as the wave context states for the C3 fixture (read your sibling constraint from "
     f"the counter docstring {RD}/c3-counter.py). Independent implementation: do not read the other "
     f"seat's directory. Validate against the pinned bytes (exactly case-json-symlink-leaf fails) "
     f"and against at least 6 applied population mutants. Copy into {W}/<seat-name>/candidate.py "
     f"with sha256."),
    "Pinned-bytes run, >=6-mutant kill table, path+sha256.")

add("R43executor08", "executor", ["coverage"],
    (f"Third independent candidate tests/fixtures/r43-drift-survivors.py — same constraints "
     f"(protocol and case names frozen; independent implementation; no reading sibling seats). "
     f"Validate against the pinned bytes and >=6 mutants. Copy into {W}/<seat-name>/candidate.py "
     f"with sha256."),
    "Pinned-bytes run, >=6-mutant kill table, path+sha256.")

add("R43executor09", "executor", ["coverage"],
    (f"Second candidate tools/souji-worktree-drift.py with the N10 fix — same constraints as the "
     f"wave context states for the C3 tool (anchors exactly once, prior fixtures green, refusal "
     f"class JSON-TARGET-SYMLINK exit 2). Independent implementation; do not read the other seat's "
     f"directory. Copy into {W}/<seat-name>/candidate.py with sha256 + anchor check."),
    "Anchor check output, two fixture green runs, refusal probe, path+sha256.")

add("R43executor10", "executor", ["calibration"],
    (f"C1 counter edge verification (findings only — the counter is frozen; you never edit it). "
     f"Probe `python3 -B {RD}/c1-counter.py` behaviour at the margins using scratch clones "
     f"(score-candidate.sh c1 with corpus/lessons/round-43.md=<variant> and "
     f"census/round-43/c1-required.tsv=<variant> from your seat dir): (a) a correction line "
     f"containing U+2019 apostrophes in surrounding prose still matches (the regex is on the "
     f"structural tokens); (b) a CRLF lesson file still parses; (c) an indented (4-space) fence "
     f"does not toggle fence state for column-0 grammar lines (indented fences are code blocks; "
     f"state your observation either way); (d) a correction line with trailing spaces still "
     f"matches ([ \\t]*$ in the grammar); (e) a lesson where a required correction appears once "
     f"inside a ``` fence AND once outside reads fenced=1 AND duplicate=0 — say whether the "
     f"outside one registers (it must: fenced and registered are independent counts); (f) "
     f"new_mismatches against a SCORECARD whose append is blank-prefixed stays 0 for a resolvable "
     f"path and 1 for an unresolvable one (the r42 counter skip defect must not recur). Each probe "
     f"is one score-candidate.sh c1 run; paste the SUMMARY of each."),
    "Six probe SUMMARYs with one-line verdicts; any finding names the exact input that breaks the "
    "frozen grammar.")

add("R43critic01", "critic", ["calibration", "operability", "coverage"],
    (f"Attack the frozen instruments BEFORE the freeze (your findings are amendments, not edits). "
     f"(1) `census/round-43/c1-counter.py` + `census/round-43/c1-required.tsv`: find an adversarial "
     f"lesson or register shape that reaches the target SUMMARY (`registered=3 ... new_mismatches=0` "
     f"rc 0) while a required correction is wrong — fenced shapes the grammar misses, a duplicate "
     f"spelled differently, a retraction the counter ignores, a derived value that re-derives but "
     f"is still false, a new_mismatches bypass. Build each adversarial variant under your seat dir "
     f"and score it with `bash {RD}/score-candidate.sh c1 <scratch> "
     f"corpus/lessons/round-43.md=<variant>` (and/or the register dest). (2) "
     f"`census/round-43/c2-cases.tsv` + the counter's builders: a builder whose synthetic repo does "
     f"not actually construct the case its name claims (e.g. control-symlink-text building a "
     f"regular file), or a want-multiset the r43 grammar does not imply. Read the builder code "
     f"against the grammar in the counter docstring. (3) `census/round-43/c3-survivors.tsv` + "
     f"`census/round-43/c3-counter.py`: an anchor pair that does not implement the probe its row "
     f"names (apply a mutant yourself and check the probe's pristine->mutant flip actually "
     f"happens), or a counter leg that can pass without the fixture running the tool. Name every "
     f"finding with the exact input and the observed vs claimed reading."),
    "Table: finding | instrument | exact input | observed | why it is wrong. An instrument you "
    "cannot break is a row too (say what you tried).")

add("R43critic02", "critic", ["operability", "coverage"],
    (f"Attack the C2/C3 instrument logic (read-only). (a) The c2-counter r42table leg: it clones at "
     f"R42_TIP 34343a39ffab8029b06e8e6c9ac699ebcbd65f8a, swaps the candidate tool, commits "
     f"--allow-empty and re-runs census/round-42/c2-counter.py — is a candidate that hardcodes "
     f"something about the r42 freeze state able to pass 37/37 while breaking the r42 claims? "
     f"Propose the cheapest such cheat and say whether the leg catches it. (b) The hidden audit "
     f"census/round-43/c2-hidden-audit.py: find a candidate that passes all ten hidden scenarios "
     f"while violating the r43 grammar clause they derive from (per-scenario: is the expectation "
     f"actually forced by the grammar, or is there a weaker behaviour that also satisfies it? At "
     f"least one scenario must have a named weaker-satisfier or the scenario set is not minimal). "
     f"(c) The c3-counter sniff control: the embedded SNIFF fixture kills EQUIV via bytes — is "
     f"there a fixture that kills all 16 population mutants and ZERO equivalents without running "
     f"the tool (a smarter byte read)? Try to write one under your seat dir; if you can, the equiv "
     f"guard is too weak and that is a finding. (d) c3-counter prior leg: the nine prior fixtures "
     f"run only on the rev tool — a candidate that breaks a prior fixture only for MUTATED bytes "
     f"is invisible; name the risk and whether the old_killed leg (prior fixtures over candidate-"
     f"derived mutants) already covers it."),
    "Per item: the cheat you built or the weaker-satisfier named, whether the instrument catches "
    "it, and the one-line verdict. Findings only; you never edit instruments.")

add("R43critic03", "critic", ["calibration"],
    (f"Claim-sizing audit before the freeze. Read {RD}/c1-required.tsv, "
     f"{RD}/c2-cases.tsv, {RD}/c3-survivors.tsv, the three counter docstrings, "
     f"`corpus/lessons/round-42.md` (Named limits + wave 3) and "
     f"`corpus/lessons/round-42-verifier-spotcheck.md` section 6. For each claim: (1) can a "
     f"do-nothing control reach the target without the claimed work (C1's do-nothing receipt is "
     f"`census/round-43/controls/c1-donothing.txt`; C2's is c2-before.txt; C3's is c3-donothing.txt "
     f"— check each is actually red for the RIGHT reason)? (2) is any predicate reachable by a "
     f"partial-work control (state the cheapest one you can build)? (3) is the axis name the "
     f"surface the round changes (C1 calibration self-assessment, C2 operability runnable gate, "
     f"C3 coverage new edge classes)? (4) name any routed item from the spotcheck section 6 list "
     f"the round's claims do NOT dispose of and that therefore needs a report line. Findings only."),
    "Per claim: control-reachability verdict with the receipt you checked; partial-work control "
    "description; axis verdict; unpicked routed items list.")

add("R43mutationtester01", "mutation-tester", ["calibration"],
    (f"Mutation-test the c1 counter (instrument sensitivity, pre-freeze). Generate >= 15 single-"
     f"defect mutants of `census/round-43/c1-counter.py` (grammar regexes, fence toggling, the W04 "
     f"mirror, the rederive kinds, the new_mismatches boundary, the RETRACT handling), score each "
     f"with the discrimination fixture: `python3 -B tests/fixtures/r43-correction-prose.py --work "
     f"<scratch> --counter43 <mutant>` — a mutant that keeps SUMMARY43 10/10 is a SURVIVOR the "
     f"fixture cannot see (name which cases would need to exist to catch it). Mutants live only "
     f"under your seat dir. Report the kill table."),
    "Table: mutant | change | SUMMARY43 | verdict; survivor list with the missing-case name each "
    "would need.")

add("R43mutationtester02", "mutation-tester", ["coverage"],
    (f"Mutation-test the c3 counter's OWN scoring logic (not the drift tool). >= 10 single-defect "
     f"mutants of `census/round-43/c3-counter.py` (kill_reading's traceback rule, the equiv guard, "
     f"the old_killed loop, n10 probe matching, the shim threshold, the target conjunction). For "
     f"each mutant, determine by reading whether the frozen target line could still print rc 0 on "
     f"a fixture that kills nothing (a scored run of the full counter takes ~20 minutes — run the "
     f"FULL counter against the committed absent-fixture state for at most TWO of your most "
     f"suspicious mutants, with --rev {INST} and your scratch; the rest are argued from the code, "
     f"clearly labelled as such). Report which mutants are caught by which leg."),
    "Table: mutant | change | caught-by (leg / argument) | would the target still read rc 0; the "
    "two scored runs' SUMMARYs verbatim.")

add("R43scout01", "scout", ["operability"],
    (f"Harvest the r42 held-out details the r43 case table must not miss. Read "
     f"`{LANE}/census/round-42/waves/w2/R42reviewer02.md`, `R42critic02.md`, `R42critic03.md` and "
     f"`R42w2critic02.md`/`R42w2critic03.md`/`R42w2reviewer04.md`: extract (a) the D1-D5 findings "
     f"of R42critic03 about dispatch/heading grammar readings, (b) R42reviewer02 A1/A2/N1 (hidden-"
     f"case holes), (c) the E-6 list (zero-padded/fullwidth Round, Control symlink text, "
     f"FROZEN-EDITED reach, HEADING-MALFORMED block boundary, run_tool timeout). For each: quote "
     f"the exact finding text (<= 25 words) with its file:line, then say whether "
     f"`{RD}/c2-cases.tsv` + `c2-hidden-audit.py` + the c2-counter grammar docstring already force "
     f"the r43 candidate to close it (yes/no + which case id). Output a coverage matrix."),
    "The matrix: finding | source pointer | covered by (case id) or GAP. Every GAP is a candidate "
    "pre-freeze amendment — be precise.")

add("R43scout02", "scout", ["coverage"],
    (f"Pre-flight the C3 consumer surface. For each of the nine committed drift fixtures "
     f"(tests/fixtures/r36-worktree-drift.py, r37-drift-discrimination.py, r38-drift-record.py, "
     f"r38-drift-write-envelope.py, r39-drift-record-rules.py, r40-drift-record-branches.py, "
     f"r41-drift-record-order.py, r41-refusal-sites.py, r42-drift-conditions.py): (1) run it "
     f"against the PINNED tool (`python3 -B <f> --tool <(git -C {LANE} show {BASE}:tools/"
     f"souji-worktree-drift.py) --work <scratch>` — extract the blob to your scratch first) and "
     f"record exit + SUMMARY (this is the baseline the candidate must reproduce); (2) read its "
     f"code for any case that touches the --json path or the root-realpath region the N10 fix "
     f"will edit and say whether the fix could flip that case (the fix adds a leaf-symlink "
     f"refusal before the guards — only a case that PASSES a symlinked --json target today could "
     f"flip). Output the baseline table + the flip-risk column."),
    "Table: fixture | pinned exit | SUMMARY | json-path case? | flip-risk. Flag any fixture whose "
    "pinned run is not exit 0.")

add("R43scout03", "scout", ["operability"],
    (f"Transcribe the C2 named gaps from the r42 wave-3 tool mutation report. Read "
     f"`{LANE}/census/round-42/waves/w3/R42w3mutationtester01.md` (and the inherited "
     f"`w2/R42w2mutationtester01.md`): list the 30 part-A coverage gaps (mutant ids + one-line "
     f"behaviour each) that no r42 leg observes. For each, say whether the r43 grammar cases "
     f"(`{RD}/c2-cases.tsv`) or the hidden audit force a candidate to close it, or whether it "
     f"stays a named limit for the r43 report. Output the 30-row table (or the file's actual "
     f"gap count) with the covered-by column."),
    "The table with covered-by / named-limit verdicts; total gap count stated.")

add("R43reviewer01", "reviewer", ["calibration", "operability", "coverage"],
    (f"Code review the three frozen counters for correctness defects the wave can still hit "
     f"(read-only; findings only): `census/round-43/c1-counter.py`, `c2-counter.py`, "
     f"`c3-counter.py` at {INST}. For each: concurrency hazards in the ThreadPoolExecutor legs "
     f"(shared mutable state, work-dir collisions), error paths that exit 0 or 1 instead of 2, "
     f"scratch leaks on exception paths, and any place the printed SUMMARY could disagree with "
     f"the returned exit code. Also review `tests/fixtures/r43-correction-prose.py` for lane "
     f"writes (it must only write its --work tree and the clone it creates) and for the r42-"
     f"lesson strip regex eating non-correction lines. Every finding: file:line + the concrete "
     f"failure it causes + severity."),
    "Findings table (file:line | defect | consequence | severity); instruments you cleared are "
    "rows too.")

add("R43sentinel01", "sentinel", ["operability", "coverage"],
    (f"Write-envelope audit of the new instruments and harness (read-only; reproduce in scratch "
     f"only). Check: (1) `census/round-43/score-candidate.sh` — the allowlist really blocks "
     f"counter/population/prereg paths and symlinked dests (try a refused dest and paste the "
     f"refusal); (2) the c2-counter's synthetic builds never write outside --scratch (git config "
     f"leaks? HOME? try with HOME=<scratch>/home); (3) the c3-counter's mutated tool files and "
     f"fixture copies all land under --scratch (strace or a PATH-shim probe: run a fixture that "
     f"tries to write its cwd and confirm the counter's env pins cwd=scratch); (4) the hidden "
     f"audit's built repos set no global git state (run it with GIT_CONFIG_GLOBAL pointing at a "
     f"canary file and verify the canary is untouched); (5) the c1-counter rederive kinds never "
     f"execute repository code (read the code paths; they must be read-only git plumbing only). "
     f"Never run anything as root; never write the lane."),
    "Per check: command + observed + verdict; any escape is a finding with the exact path it "
    "wrote.")

add("R43revenger01", "revenger", ["calibration", "coverage"],
    (f"Reverse-engineer the routed items the round did NOT pick up, to keep the report honest. "
     f"(1) S259 scope (r42 spotcheck item 5, E-5): read `{LANE}/corpus/SOURCES.md` S259 and "
     f"`corpus/lessons/round-42.md` E-5 — does the r43 round need a superseding row (the "
     f"`using/cmdline` page) for C2's patches leg to stay sourced, and is anything in the r43 "
     f"claims actually resting on the narrowed reading? (2) The 17 equivalent survivors of "
     f"`census/round-42/waves/w2/R42w2critic04.md` section 5: verify the r43 EQUIV set (six "
     f"anchors in c3-counter.py) is a subset that still applies at the current bytes (each old "
     f"string occurs exactly once — run the count) and name which of the 17 equivalents the r43 "
     f"fixture could accidentally kill without the guard noticing. (3) r1-counter's frozen "
     f"predicate (spotcheck item 1): read `census/round-42/r1-counter.py` and state in two "
     f"sentences whether it should be amended as a new instrument version next round or retired, "
     f"with the reason. Findings only."),
    "Three dispositions with pointers; any error you find in the routed reasoning is a finding.")

add("R43connector01", "connector", ["calibration", "operability", "coverage"],
    (f"Sibling-overlap scan (read-only). (1) Does any sibling lane own a freeze-check, correction-"
     f"prose reader, or drift-tool symlink refusal that r43 would duplicate? grep the sibling "
     f"repos' tools/ and SKILL.md registries for `freeze-check`, `correction`, `RETRACT`, "
     f"`JSON-TARGET-SYMLINK`, `NOFOLLOW` (git -C <sibling> grep at their master). Siblings: "
     f"mori, tabi, tsukuroi, kengaku, kasegi, kaidoku, mado, tameshi, chousa, kama, kake, "
     f"kumitate, kotodama, kotoba (all under /home/vgpnk/Projects/shokunin/). (2) Does any "
     f"sibling's corpus cite souji's r42 artifacts in a way r43's renames would break (grep for "
     f"`souji-round-42`, `r42-drift-conditions`, `souji-freeze-check`)? (3) Name any lane whose "
     f"round contract already claims symlink-refusal or correction-prose ground (contested scope "
     f"= report, never absorb). Output the three lists with pointers."),
    "Three sections with repo:path pointers; a clean scan says so per section with the grep "
    "commands used.")

add("R43simplifier01", "simplifier", ["operability", "calibration"],
    (f"Complexity review of the three counters + the discrimination fixture (read-only; findings "
     f"only). For each of census/round-43/c1-counter.py, c2-counter.py, c3-counter.py, "
     f"tests/fixtures/r43-correction-prose.py: name up to three deletions or simplifications that "
     f"would keep every frozen case/leg outcome byte-identical (dead code, unused constants, "
     f"branches unreachable under the frozen inputs, duplicated logic between the counters and "
     f"the fixture). Estimate the line delta for each. Do not edit; the L1 applies safe ones as "
     f"pre-freeze amendments with the fixture/controls re-run as proof."),
    "Per file: simplification | why safe | line delta; mark which ones change no frozen outcome.")

add("R43scribe01", "scribe", ["calibration"],
    (f"Draft the SOURCES registry rows for the two sources opened this round, from the committed "
     f"snapshots (you open the FILES, not the network): "
     f"`{RD}/sources/man2-symlink.html` (sha256 c929903b2dec6c985e149ca27d509243e04fc80861d8b98c1f98e2325e857178, "
     f"= https://man7.org/linux/man-pages/man2/symlink.2.html) and "
     f"`{RD}/sources/python-3-library-subprocess.html` (sha256 "
     f"5935a4afd34ad560cc5b66f0ed6e90d4d63ba9047ad8f367d5081474650078b5, = "
     f"https://docs.python.org/3/library/subprocess.html). For each: verify the sha256, locate "
     f"(a) in the symlink page the ELOOP sentence in the ERRORS section and (b) in the subprocess "
     f"page the sentence about run(timeout) killing and waiting for the child and re-raising "
     f"TimeoutExpired; give each a <=25-word located quote with the HTML-section name and the "
     f"snapshot line numbers, and note the page's version marker (man-pages release for the first; "
     f"the footer 'Last updated' for the second). Then draft the two registry rows in the exact "
     f"column shape of `corpus/SOURCES.md` (S260 and S261 are the next free ids — verify by "
     f"counting; tier A docs; scope: the symlink row grounds 'a leaf symlink named by --json is "
     f"refused, ELOOP is what an O_NOFOLLOW walk raises on a link', the subprocess row grounds "
     f"'run(timeout) kills and waits for the direct child, so a fixture-side kill with a recorded "
     f"timeout is the load-robust kill'; status mined; recheck on-release for the first, 365d for "
     f"the second; used-by the r43 lesson path corpus/lessons/round-43.md). No cell may contain a "
     f"literal or escaped | character. Write the draft rows into {W}/R43scribe01/rows.tsv and the "
     f"quote evidence into {W}/R43scribe01/gate.md."),
    "Both sha256 verifications, the two located quotes with line numbers, the two drafted rows, "
    "and the next-free-id verification.")

add("R43scribe02", "scribe", ["calibration"],
    (f"Draft the round-43 lesson skeleton as a STRUCTURED OUTLINE (prose drafts only; you do not "
     f"write the final lesson). Read `corpus/lessons/round-42.md` for the house style, then "
     f"produce an outline covering: header (round, lane, base {BASE}, instruments rev {INST}); "
     f"the routed-defect disposition table (r42 spotcheck section 6 items 1-6, with the planned "
     f"disposition of each: item 3 via C1, item 4 via C2 + the 30-gap named-limit note, item 2 "
     f"via the c3 counter's load-robust kill rule, items 1/5/6 as report lines unless the wave "
     f"finds otherwise); a Gate section skeleton (sources S260/S261 rows with quote placeholders, "
     f"admit/reject sections, spot-check placeholder); a Mistakes section skeleton with the "
     f"already-known candidate: M43-1 'fixture-identity env leaked into the lane helper's push "
     f"env (GIT_CONFIG_GLOBAL=/dev/null + GIT_AUTHOR_*/GIT_COMMITTER_*=fixture), two pushes "
     f"rejected with could-not-read-askpass before the cause was found' — class, evidence pointer "
     f"(the helper err file ~/.local/state/shokunin-hyaku/jj-_home_vgpnk_Projects_shokunin_souji-shokunin.err), "
     f"captured-by (none; the wave context now forbids exporting fixture identity), fix. Write "
     f"the outline to {W}/R43scribe02/lesson-skeleton.md."),
    "The outline file with every section headed, the disposition table filled for items 1-6, and "
    "M43-1 drafted in the four-part class/evidence/captured-by/fix shape.")

add("R43executor11", "executor", ["coverage"],
    (f"One falsifiable hypothesis: the S35 timing case (case-gitdir-probe-honors-timeout) kills "
     f"its mutant reliably under load. Method: apply the S35 mutant per "
     f"`{RD}/c3-counter.py` MUTANTS to a scratch copy of the pinned tool (`git -C {LANE} show "
     f"{BASE}:tools/souji-worktree-drift.py`), build the FIFO-HEAD scenario, and run the scenario "
     f"probe (tool run with --timeout 1 against a repo whose .git/HEAD is a FIFO) 10 times "
     f"serially and 10 times under a synthetic load of 16 busy spinners you spawn and kill, "
     f"recording elapsed time and outcome each run. Hypothesis: pristine < 12s and mutant >= 20s "
     f"in every run (the case kills with margin). If any run crosses the boundary, the case "
     f"needs a larger margin or a different observable — that is the finding."),
    "A 20-row timing table (run | load | elapsed | rc) and the hypothesis verdict; spinners killed "
    "with your own recorded pids only; scratch removed on exit.")


# ---- genuine verification items (one per frozen target), added so the single v2 wave is 64+ ----
for mid, old_desc in [("S03","record read stops after the first 64 KiB chunk"),("S11","TOTAL regex loses its end anchor"),
                      ("S12","REPO name excludes spaces"),("S13","REPO regs accepts an empty field"),
                      ("S17","TOTAL prunable compared one-sidedly"),("S22","root-as-repo match skips the root .git test"),
                      ("S25","unreadable root raises"),("S33","root_real not realpath-resolved"),
                      ("S34","--root not abspath-resolved"),("S35","gitdir probe ignores --timeout"),
                      ("S43","REGS-CHANGED one-sided"),("S44","PRUNABLE-CHANGED one-sided"),
                      ("S53","--json containment uses commonprefix"),("S58","--json created mode 0600"),
                      ("S63","--json '' treated as set"),("S73","--timeout parsed as float")]:
    pair = [x for x in [mid]]
    add(f"R43mutanchor-{mid}", "mutation-tester", ["coverage"],
        (f"Population row {mid} ({old_desc}) — anchor-to-probe fidelity check (pre-freeze). Read the "
         f"row in `{RD}/c3-survivors.tsv` (column 4 names its probe) and its MUTANTS tuple in "
         f"`{RD}/c3-counter.py`. (1) Apply the mutant to a scratch copy of the pinned tool "
         f"(`git -C {LANE} show {BASE}:tools/souji-worktree-drift.py`) with the tuple's old->new "
         f"replacement; confirm old occurs exactly once. (2) Build the probe scenario the row names "
         f"(its probe column) in a scratch dir and run the PINNED tool and the MUTANT tool on it; "
         f"record rc and stdout/stderr tokens. (3) Verdict: does the observable flip (pristine -> "
         f"mutant) hold as the row's description claims? If the flip does not hold, the row is a "
         f"population defect — say exactly what the mutant does instead. Scratch under your seat "
         f"directory only; remove scratch on exit."),
        "Table: mutant | anchor count | pristine rc+token | mutant rc+token | flip holds (yes/no) | "
        "defect text if no.")

for rid, desc, ptr in [("R43-D1","census-rows 173->174 at 0242085","census/round-39/records/census-after.txt:3"),
                       ("R43-D2","W04 47->48 at 0242085","census/round-39/records/census-after.txt:4"),
                       ("R43-D3","receipt header names 5441045 not 0242085","census/round-39/records/final-tip-measure.txt:1")]:
    add(f"R43rederive-{rid}", "reviewer", ["calibration"],
        (f"Independent re-derivation of required correction {rid} ({desc}; receipt pointer {ptr}). "
         f"Do NOT read the counter's code path for this item beyond its row in "
         f"`{RD}/c1-required.tsv`. Re-derive the value from committed bytes with plain git/grep/awk "
         f"at the revision named in that row (`git -C {LANE} show <rev>:<path>`): for R43-D1 count "
         f"S-rows in corpus/SOURCES.md at 0242085 with `grep -cE '^\\|[[:space:]]*S[0-9]{{3,}}[[:space:]]*\\|'`; "
         f"for R43-D2 count W04 warnings by the validator's rule (same URL in >=2 rows under different "
         f"scope, the later row warns) — state your counting method; for R43-D3 read the receipt header "
         f"line and `git diff --stat 5441045 0242085 -- census tools tests`. Compare to the stale value "
         f"the receipt prints. Verdict: does the derived value match the register row, and is the stale "
         f"value what the receipt actually prints?"),
        "Command, observed value, match yes/no, and the stale-value check.")

for gname, cases in [("A", "dup-key-first-bad, dup-key-first-good, heading-unattached-key"),
                     ("B", "round-zero-padded, round-fullwidth, round-missing"),
                     ("C", "control-symlink-text, frozen-edit-control, frozen-edit-prereg")]:
    add(f"R43casebuild-{gname}", "critic", ["operability"],
        (f"Builder audit for c2-cases.tsv cases {cases} (read-only; findings only). For each case id, read "
         f"its builder in `{RD}/c2-counter.py` (CASE_BUILDERS and build()) and the expected row in "
         f"`{RD}/c2-cases.tsv`. (1) Does the builder construct the shape its name claims (write the "
         f"synthetic repo in a scratch dir by calling build() and list the files/keys/symlinks it "
         f"produced)? (2) Does the expected (exit, classes) follow from the r43 grammar in the counter "
         f"docstring — derive it yourself first, then compare. (3) Name the weakest alternative "
         f"implementation (a tool that would pass this case for the wrong reason). Scratch under your "
         f"seat dir only."),
        "Per case: built shape (observed), grammar-derived expectation, match yes/no, weakest "
        "alternative.")

for cls, grammar in [("KEY-DUPLICATE","first-wins: first value evaluated, each further occurrence one finding"),
                     ("UNATTACHED-KEY","a key after a malformed ## heading and before the next valid claim heading is reported, never dropped"),
                     ("ROUND-MALFORMED","any Round: line not strict ASCII digits yields one finding and no dispatch scan"),
                     ("CONTROL-SYMLINK","a symlink Control at FREEZE is one finding and its link text is never read as the control"),
                     ("FROZEN-EDITED-extended","Control blob and prereg text compared FREEZE vs REV"),
                     ("CRLF-prereg","CRLF prereg lines parse with the trailing CR stripped")]:
    add(f"R43classaudit-{cls}", "scout", ["operability"],
        (f"Class audit for the new r43 grammar class {cls} ({grammar}). Read the r42 tool at its measured "
         f"tip (`git -C {LANE} show 34343a39ffab8029b06e8e6c9ac699ebcbd65f8a:tools/souji-freeze-check.py`) "
         f"and the r42 counter's table (`git -C {LANE} show 34343a39ffab8029b06e8e6c9ac699ebcbd65f8a:"
         f"census/round-42/c2-counter.py`). (1) Does ANY r42 counter case assert the OPPOSITE of the r43 "
         f"behaviour for this class (which case id, which expectation)? If yes, the candidate cannot "
         f"pass r42table without a repair — name the case. (2) Does the r43 frozen table "
         f"(`{RD}/c2-cases.tsv`) or the hidden audit exercise this class? (3) Name one input that "
         f"exercises the class but that neither table covers. Findings only."),
        "Three numbered answers with case ids and file:line pointers.")

for gname, sib in [("A","mori tabi tsukuroi kengaku kasegi kaidoku mado"),("B","tameshi chousa kama kake kumitate kotodama kotoba")]:
    add(f"R43connector-{gname}", "connector", ["calibration","operability","coverage"],
        (f"Sibling-overlap scan, group {gname} ({sib}), under /home/vgpnk/Projects/shokunin/. Use "
         f"`git -C <lane> grep -n -E 'freeze-check|RETRACT|CORRECTION-|JSON-TARGET-SYMLINK|O_NOFOLLOW' "
         f"HEAD -- tools SKILL.md corpus census` at each sibling's master (read-only). For each hit "
         f"naming a mechanism that r43 would duplicate or contest, record repo:path:line and the "
         f"overlap kind. Clean scan says so with the commands used. Read-only; never write a sibling."),
        "Per sibling: grep command and hit list (or clean); contested-scope verdict per hit.")

for n, what in [("scoutH","the W04 duplicate-URL mirror in this round's Python (census/round-43/c1-counter.py w04_count) against scripts/sources-census.sh's awk, on corpus/SOURCES.md at the lane master and at 0242085 — the two values must be 52 and 48. Report any row where the Python and awk disagree."),
                ("scoutHT","the tiers and statuses histogram of corpus/SOURCES.md at master: `grep -E` each S-row, confirm tiers in {A,B,C} and statuses in {queued,mined,rejected}; report anomalies.")]:
    add(f"R43{n}", "scout", ["calibration"],
        (f"Read-only check: {what} Scratch under your seat dir only."),
        "Commands run, observed values, verdict.")

add("R43revenger02", "revenger", ["operability"],
    (f"Reverse-engineer why the r42 counter's `retro` leg (census/round-40/preregistration.txt must read "
     f"red at >=3 findings) and `retro_clean` leg (census/round-41/preregistration.txt must read clean) "
     f"behave as they do on the r43 candidate: run `git -C {LANE} show 34343a39ffab8029b06e8e6c9ac699ebcbd65f8a:"
     f"tools/souji-freeze-check.py` over those two preregs at the r42 tip and record findings. Then state "
     f"which grammar change in the r43 docstring could flip retro_clean red (quote the clause). Findings only."),
    "Two observed SUMMARYs and the flip-risk clause quoted with file:line.")

add("R43reviewer04", "reviewer", ["operability", "coverage"],
    (f"Review the r43 hidden audit census/round-43/c2-hidden-audit.py at {INST} for every scenario's "
     f"builder correctness (does each build the shape its id claims, does its expectation follow from the "
     f"r43 grammar, does the refusal scenario h10 really refuse). Findings only; scratch under your seat."),
    "Per scenario: builder ok/defect; expectation ok/defect; file:line.")

add("R43reviewer05", "reviewer", ["calibration"],
    (f"Review tests/fixtures/r43-correction-prose.py at {INST}: each frozen case's expectation vs the "
     f"counter's documented grammar; each r42 defect signature cited to its lesson/receipt pointer; and "
     f"whether the fixture's clone writes stay under --work. Findings only."),
    "Per case: expectation grounded yes/no with pointer; write-scope verdict.")

add("R43sentinel02", "sentinel", ["operability"],
    (f"Escape check on the hidden audit and c3 counter's build/score paths (read-only; reproduce in "
     f"scratch): run `python3 -B census/round-43/c2-hidden-audit.py --tool <pinned tool copy> --work <scratch>` "
     f"with HOME pointing at a canary dir and GIT_CONFIG_GLOBAL unset; afterwards check the canary dir and "
     f"~/.gitconfig are byte-identical to before (sha256). Report the before/after digests."),
    "Canary digests before/after; verdict.")

add("R43simplifier02", "simplifier", ["operability"],
    (f"Complexity audit of census/round-43/c2-hidden-audit.py and census/round-43/score-candidate.sh (read-only): "
     f"name up to three deletions that keep every scenario outcome identical; estimate line delta. Do not edit."),
    "Per file: simplification | safe-because | line delta.")

add("R43mutationtester03", "mutation-tester", ["operability"],
    (f"Mutate the hidden audit's expectations: >=6 single-defect mutants of census/round-43/c2-hidden-audit.py "
     f"(flip one expected exit code, drop one expected class, swap two scenario expectations); for each run the "
     f"audit against the candidate-free PINNED freeze-check tool at {INST}'s tools/souji-freeze-check.py and "
     f"report whether the audit's SUMMARY still reads all-pass (a surviving expectation mutant is a finding)."),
    "Table: mutant | audit SUMMARY | survived yes/no.")

add("R43critic04", "critic", ["operability", "coverage"],
    (f"Cheat search on the r42table leg: census/round-43/c2-counter.py re-runs census/round-42/c2-counter.py at "
     f"34343a39 with a candidate tool swapped in. Find the cheapest candidate that passes the r42 37-case table "
     f"while violating a named r43 grammar clause (read the r43 docstring for the clauses). Build it under your "
     f"seat dir; run the r42 counter over it the way c2-counter does (clone at 34343a39, swap, commit --allow-empty, "
     f"run); report SUMMARY and which clause it violates. A cheat that passes = the r42table leg is not a "
     f"behaviour-retention guard for that clause."),
    "Cheat description, violated clause (quoted), r42 counter SUMMARY verbatim.")

add("R43critic05", "critic", ["coverage"],
    (f"Discrimination attack on tests/fixtures/r43-correction-prose.py: build one lesson variant that the r43 "
     f"counter scores green (SUMMARY required=3 registered=3 ... rc 0) while a required correction is FALSE "
     f"(e.g., derived value wrong), and check whether the fixture's own cases would notice. If none would, the "
     f"fixture does not discriminate the derivation leg; say so with the variant text."),
    "Variant description, counter SUMMARY, fixture case that notices or 'none'.")

add("R43mutationtester04", "mutation-tester", ["calibration"],
    (f"Mutation battery over the c1 counter's register and derivation leg (>=6 mutants, pre-freeze): flip the "
     f"tuple order of the rederive kinds, weaken `new_mismatches` to count from line 1 instead of base+1, drop "
     f"the header check, drop the RETRACT count, accept a CR-terminated register row; for each run "
     f"score-candidate.sh c1 with the mutant as the r43 counter's dest? NO — c1-counter is not on the allowlist; "
     f"instead copy the counter to your seat dir, apply the mutant there, and run it at {INST} with --scratch. "
     f"Report SUMMARY per mutant and survivors."),
    "Table: mutant | SUMMARY | survived yes/no.")

add("R43scout03b", "scout", ["coverage"],
    (f"Read-only: list every file in census/round-42/controls/ (c1-control.txt, c2-control.txt, c3-control.txt) and "
     f"state whether the r43 C3 do-nothing control (census/round-43/controls/c3-donothing.txt) reads red for the "
     f"same reason as the r42 control (absent fixture, pristine=FAIL). Quote both receipt heads."),
    "Two receipt quotes and the same-reason verdict.")

if __name__ == "__main__":
    spec = {"wave": "souji-r43-w1", "milestone": "r43 single v2 wave: candidates + instrument attacks",
            "reportDir": ".ufo/waves/round-43/w1",
            "context": CONTEXT, "items": items}
    out = os.path.join(LANE, ".ufo/waves/round-43/w1-spec.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(spec, handle, indent=1, ensure_ascii=False)
        handle.write("\n")
    from collections import Counter
    print(len(items), dict(Counter(i["role"] for i in items)))
