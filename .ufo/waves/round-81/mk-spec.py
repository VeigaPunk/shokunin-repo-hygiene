#!/usr/bin/env python3
"""souji r81 wave w1 spec builder (L1 SoujiR81). Writes .ufo/waves/round-81/w1-spec.json.
The context tail is the r80 builder's text with round-80 -> round-81."""
import json
import os

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SCR = "/fast/scratch/hyaku/souji-r81"
GS = open(os.path.expanduser("~/.agents/skills/godspeed/directive.md")).read()
HEAD = "/skill:godspeed\n" + GS + "\n\n"
BASE = "b15279bbc3f11ec10fc375a05a08b19cac460d0c"
P = "804f132ef717d96157c107e219a254286644b706"
F = "0b1aeaf1c1bb11605bb9e139116323f5680b1a1c"
W1 = "308bc77bddc725aa8f302e4f62746bde3f843f56"
W2 = "7076ed2d12faf82e9c762f49d627b84ae549fbd1"
A = "cb14eae71c02d51d2e071628ac4c882f01daf844"
R = f"{LANE}/census/round-81"
TAIL = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ctx-tail.txt")).read().replace(
    "{LANE}", LANE).replace("{SCR}", SCR)

context = f"""# Goal
souji round 81 (lane repo {LANE}, lane id souji). The L1 (SoujiR81) holds the planner seat and is the ONLY integration owner: it commits through the lane helper and writes the report. You are one seat of ONE wave of 13 seats. Seats deliver files and findings only. Your mandate is to FALSIFY the frozen round-81 claims and the round's landed changes: re-derive every number yourself from committed bytes, run the frozen commands, and report what does not hold. A finding with a reproducer beats an opinion.

# Evidence durability
FIRST action: create your report file (the `Report:` trailer path) with a one-line skeleton, and append to it as you go. Your final yield must repeat the same content. A seat that ends without that file counts as no verdict.

# Chronology (binding; read {R}/preregistration.txt first — it is the frozen contract)
- Lane base (r80 closed admitted): {BASE}.
- P {P}: census/round-81/c1-false-row-harness.py + c1-false-rows.tsv (C1: 25 rows = the r80 population's 18 unchanged + NF12/NF12b/NF12c/NF12d decoys of SwarmExecutor08.md and TRUE rows TF1/TF2/TF3; fixture rev R4 = R3 + the copies), census/round-81/c2-vault-signal-counter.py + c2-population.tsv (C2: 12 rows; TERM/INT/HUP to tools/souji-vault-verify.sh's pid or process group while its advisory CLI call (cli_claim, `timeout` + SOUJI_CLI_BIN stub) blocks, plus 4 no-signal positives p1 honest/agree, p2 hang bounded/timeout, p3 stdin-reading CLI/agree, p4 --fallback), control variants under census/round-81/controls/variants/ and every control receipt, census/round-81/rec.sh (binds absolute paths with mode), S329 capture census/round-81/srcs/bash.info-5.3-Lists.txt and row in corpus/SOURCES.md, corpus/lessons/round-81.md (Inherited, Gate), records/census-before.txt, records/registry-agreement-base.txt, records/prefreeze/ (draft feasibility), records/v1-quarantine/ (V1 verification of the r80 quarantine front at base).
- F {F}: census/round-81/preregistration.txt (records/freeze-check-at-F.txt: claims=2 findings=0, committed at W1).
- W1 {W1}: C1 candidate census/round-81/c1-pointer-counter.py (successor of the frozen census/round-80/c1-pointer-counter.py): a MOVED target under census/round-<N> (token not under census) must lie in census/round-<N>/waves/, /wave/ or /records/wave-<w>/ AND the path below that subtree must be a non-empty whole-component suffix of the token's path below its round-<N> (function _capture_ok).
- W2 {W2}: C2 candidate tools/souji-vault-verify.sh: cli_claim runs `timeout "$CLI_TIMEOUT" "$bin" vault:hash "$vp" <&0 >"$CLI_OUT" 2>/dev/null &` then `wait`, with TERM/INT/HUP trapped to cli_on_signal (kill -TERM the timeout group `-$pid`, falling back to the pid; poll up to 2 s; kill -KILL; remove the private output file; stderr `souji-vault-verify: SIG<name> received during the advisory CLI call; stopped it, no verdict`; exit 128+n); traps reset after the call; the result returns through the global CLI_CLAIM instead of `$(cli_claim)`; if mktemp fails the old foreground call runs. Sources S325 (bash Signals), S326 (timeout.c setpgid/cleanup), S329 (bash Lists: async stdin is /dev/null without explicit redirection; opened this round).
- A {A}: records/c1-after.txt (25 rows, mismatches 0, accepted 0, refused_true 0), c1-regress-r77/r78/r79-harness/r80-harness green; records/c2-after.txt (12 rows, mismatches 0, orphans 0; K-a base 8 mismatches 8 orphans; K-b trap-only 8/8; K-c without <&0: p3 cli=empty), c2-regress-selftest.txt (57 checks 0 failed, committed file in the lane), c2-regress-r17.txt (37/0/0 with --baseline-dir), c2-domain-trial.txt (identical, 3/3; the real ledger is empty so the CLI is never reached on real targets — stated), diagnosis-domain-trial-refuses-empty.txt (EXIT=1).

# Claims (frozen predicates are in the preregistration; never change them)
C1 calibration (lowest owned axis, 7): the successor pointer counter refuses three census decoys the r80 counter accepts (NF12, NF12c, NF12d) and keeps three true captures; harness accepted 3 -> 0, refused_true 0; K-b refuse-all refused_true 3; K-c without the suffix binding accepts NF12c; regressions r78 22/22+12/12, r77 35/35+7/7, r79 harness 9/9, r80 harness 18/18.
C2 operability (sourced on S329, opened this round): souji-vault-verify.sh answers a caller's TERM/INT/HUP during its advisory CLI call by killing timeout's group and exiting 128+n within 5 s with nothing left running; 12 rows mismatches 8 -> 0, orphans 8 -> 0; K-b/K-c red; selftest 57/0, r17 37/0/0, domain trial identical.
V1 (verification, not a claim): the r80 quarantine front (tools/souji-quarantine.sh at base, the r80 R3 bytes) re-measured: frozen r80 counter 15/15 (also SHELLOPTS=monitor) and the three r80 probes green (records/v1-quarantine/).

# Frozen invocations (run from {LANE}; never alter counters, populations or controls)
- C1: python3 -B census/round-81/c1-false-row-harness.py --counter <counter path> --lane {LANE} --fleet-root /home/vgpnk/Projects/shokunin --work <SCRATCH>/c1 (~60 s). Regressions: python3 -B census/round-81/c1-pointer-counter.py --root {LANE} --rev e65538e73c7f1a8f7570bc24a2215da8a90043f3 --fleet-root /home/vgpnk/Projects/shokunin --population census/round-78/c2-population.tsv --ledger census/round-78/c2-pointer-ledger.tsv --forge census/round-78/c2-forge-r78.tsv (and round-77 population/ledger with census/round-78/c2-forge-r77.tsv).
- C2: `git show <rev>:tools/souji-vault-verify.sh > D/souji-vault-verify.sh`; python3 -B census/round-81/c2-vault-signal-counter.py --tool D/souji-vault-verify.sh --work <SCRATCH>/c2 (~50 s; no other heavy job of yours at the same time: rows have a 5 s settle). The selftest conjunct runs the committed lane file: TMPDIR=<SCRATCH>/st bash {LANE}/tools/souji-vault-verify.sh --selftest (a copy outside the lane fails check R9 for base and candidate alike: records/prefreeze/).
- Every receipt starts with `command=<literal command>` (rec.sh); replaying that line with your scratch prefix is a valid check.
<SCRATCH> must be a fresh directory under {SCR}/<your seat name>/ (mkdir -p it). Counters refuse --work under /tmp, /var/tmp or /dev/shm. Anything that may block runs under `timeout -k 5 <s>` in its own session (setsid) so the whole process group dies; never leave a blocked process behind (check `ps -eo pid,args | grep <your scratch>` before you yield). Never send a signal to a process you did not start.

{TAIL}"""

items = [
 ("S81Connector", "connector", f"""# Target
Cross-claim separation and sibling-overlap scan for round 81. Read-only.

# Change
1. Causal separation: from receipt `# bind`/`instrument=` lines and commit contents (`git show --name-only` for W1 {W1}, W2 {W2}, A {A}) confirm no C1 receipt reads a vault-tool byte and no C2 receipt reads a C1 counter byte. Would C1 verify with W2 absent, and C2 with W1 absent? Verdict SEPARABLE/COUPLED.
2. Lane tools under {LANE}/tools and {LANE}/tests that STILL run a `timeout`-wrapped child inside `$(...)` with no trap after W2 (tools/souji-verify.sh, tools/souji-census.sh, tools/souji-quarantine.sh's inner paths, ...): file:line list; which lane pattern (r79 async gate_run, r80 session front, r81 async job + group kill) fits each.
3. Sibling overlap (read-only; other *-shokunin repos under /home/vgpnk/Projects/shokunin): sibling tools that call an external CLI under `timeout` inside `$(...)` with no trap (cap 15 rows: lane, file:line, exposed yes/no). Document only.

# Acceptance
Tables with verdicts and file:line; findings by severity."""),
 ("S81ScoutSources", "scout", f"""# Target
Re-open the round's sources and test the sentences the claims rest on. Read-only on the lane.

# Change
1. S329: `pacman -Qo /usr/share/info/bash.info.gz`; sha256 of the installed file vs census/round-79/srcs/bash.info.gz-5.3 (cde1a336…588f) and vs the row; `zcat | sed -n 738,770p` equals {R}/srcs/bash.info-5.3-Lists.txt byte-for-byte?; locate the quoted sentence on decompressed lines 758-760 and count its words (row/lesson say 19). Does bash's own behaviour match it on this host (a 3-line script: `cmd &` vs `cmd <&0 &` reading stdin from a file, job control off)?
2. S326: in census/round-79/srcs/coreutils-timeout.c-v9.12, cleanup(): does timeout forward a received TERM to its child AND to its process group (send_sig(0, sig)) when not --foreground? Quote file:line. Does that make the W2 group kill redundant (the prereg already discloses a pid-only draft scoring 12/0)? What does timeout do with SIGINT/SIGHUP received?
3. S325/S329 duplicate check: is S329 within S325's scope (S325 row in corpus/SOURCES.md)? Admit/reject with reasons.
4. The W1 docstring now says the NF8 mode whitelist rests on S294; check the S294 row and its capture (census/round-63/sources/s294-git-fast-import.html) list 100644/100755/120000/160000/040000.

# Acceptance
sha256 match/mismatch; quotes with line numbers and word counts; per-question HOLDS/DISAGREE with file:line; admit/reject per row."""),
 ("S81ExecC1", "executor", f"""# Target
Reproduce C1 from committed bytes.

# Change
1. Run the harness with --counter census/round-80/c1-pointer-counter.py and with census/round-81/c1-pointer-counter.py (W1 {W1}); compare with controls/c1-K-a-r80-counter.txt and records/c1-after.txt; confirm fixture revs F0 (=6436db6a…), R1-R4 are identical across two runs.
2. Replay controls c1-K-b-refuse-all.txt and c1-K-c-without-suffix.txt; confirm each variant's sha256 against its bind line and that K-c accepts exactly NF12c.
3. Replay records/c1-regress-r78.txt, c1-regress-r77.txt, c1-regress-r79-harness.txt, c1-regress-r80-harness.txt at W1.
4. Diff ITEM lines of the r77 and r78 populations under the r80 and r81 counters (same --rev): does any verdict move? Run the r81 counter over every MOVED row of both ledgers and list token -> target with the subtree and suffix _capture_ok sees.

# Acceptance
Per receipt reproduced yes/no; ITEM-line diff; findings by severity."""),
 ("S81ExecC2", "executor", f"""# Target
Reproduce C2 from committed bytes, under several launches.

# Change
1. Run the C2 counter over the W2 tool ({W2}) in the foreground, launched with `&` from a bash script, and with `env SHELLOPTS=monitor`; and over the base tool ({BASE}); compare with records/c2-after.txt and controls/c2-K-a-do-nothing.txt (record each run's `# launch` line and per-row ign=).
2. Replay controls/c2-K-b-trap-only.txt and c2-K-c-no-stdin.txt from controls/variants/; confirm sha256 against bind lines.
3. Replay records/c2-regress-selftest.txt (committed lane file), c2-regress-r17.txt (tool dir with W2 souji-vault-verify.sh, souji-verify.sh, souji-quarantine.sh; --baseline-dir with the base copies) and c2-domain-trial.txt (census/round-81/probes/domain-trial.sh); is the trial vacuous for the changed code path (it is stated so) — can you build a domain trial on real lane bytes that DOES reach cli_claim (a real file + a scratch ledger row + a scratch vault copy, SOUJI_LEDGER pointing at scratch) and compare base vs W2 byte-for-byte?

# Acceptance
Per run: SUMMARY lines; per receipt: reproduced yes/no; your extra trial's verdict."""),
 ("S81ExecEvade", "executor", f"""# Target
Try to make the W2 vault tool ({W2}) leave a process behind, lose or change a verdict, or exit wrongly. Scratch copies only.

# Change
Using the counter's fixture shape (read census/round-81/c2-vault-signal-counter.py build/run_row) or your own:
1. Timing: signal immediately after the CLI starts (before its mark), during the `cat` of the output file, between two targets (two ledger pairs on one command line), double/triple signals, a signal during the 2 s poll inside cli_on_signal.
2. A CLI that ignores TERM (trap '' TERM; sleep 600): does the KILL fallback end it within 5 s? A CLI that calls setsid (stated limit). A CLI that writes a huge output.
3. TMPDIR missing, unwritable or containing spaces/newlines: does the foreground fallback run and is the verdict unchanged vs base? Does anything get left in TMPDIR?
4. --json mode and a directory ledger pair that reaches cli_claim: same signal behaviour?
5. No-signal byte identity: base vs W2 stdout/stderr/rc over every CLI state (honest, liar, empty, unparseable, error rc, hang->timeout, unavailable) — any difference?

# Acceptance
Table: probe / base / W2 / verdict; reproducers under your seat dir; findings HIGH/MEDIUM/LOW."""),
 ("S81ExecV1", "executor", f"""# Target
V1 verification (r80 spot-check routed defect 1): attack the r80 quarantine front as it stands at base ({BASE}, tools/souji-quarantine.sh, the r80 R3 bytes). Scratch copies only.

# Change
1. Replay records/v1-quarantine/*.txt (frozen r80 counter census/round-80/c2-signal-counter.py, its SHELLOPTS=monitor run, probes census/round-80/probes/front-launch-modes.py, front-worker-death.py, front-comm-newline.py) with --tool-dir = base souji-quarantine.sh + souji-verify.sh; confirm each SUMMARY.
2. New launch shapes the r80 rows never varied: `nohup`, stdin closed (`<&-`), stdout to a closed pipe (SIGPIPE), `setsid -w` launch, `bash -m -c`, run from a pty (`script -qc`), TMPDIR on a different filesystem (/dev/shm is fine for one probe), a caller that ignores HUP. Any case where the front exits with no RESULT line where the base-before-r80 tool (r80 base e2f2d083… blob: `git show f80f9368a8a20679438b1dffd72d0faab0ccf194:tools/souji-quarantine.sh`) gave one, or leaves a process?
3. Report found defects with reproducers; do not repair.

# Acceptance
Per shape: base-r80 vs current verdict/rc/survivors; findings by severity."""),
 ("S81MutTool", "mutation-tester", f"""# Target
Mutation-test the W2 change to tools/souji-vault-verify.sh against the frozen C2 counter (12 rows) and the selftest.

# Change
Copy W2 tools/souji-vault-verify.sh into your scratch. Mutants (one at a time): drop `<&0`; drop the group kill (pid only); drop the KILL fallback; drop `rm -f "$CLI_OUT"` in the trap; drop `trap - TERM INT HUP` after the call; exit 0 instead of 128+n; trap only TERM; replace `wait "$CLI_PID"` with `wait`; remove the CLI_PID reset; keep `$(cli_claim)` at the call site (return through stdout); mktemp always failing. For each: counter SUMMARY and the rows that kill it; which survive, and is each survivor equivalent or a missing row?

# Acceptance
Mutant table (mutant / killed-by / survives) and a list of missing rows with proposed predicates."""),
 ("S81MutCounter", "mutation-tester", f"""# Target
Mutation-test the W1 rule (census/round-81/c1-pointer-counter.py _capture_ok and its call) against the frozen 25-row harness and the regressions; and hunt new false rows.

# Change
1. Mutants: drop the subtree alternation members one at a time (waves/, wave/, records/wave-*); suffix -> last component only; suffix -> prefix; allow empty suffix; drop the `token not under census` guard; `records/wave-[^/]+/` -> `records/[^/]+/`. For each: harness + r77/r78 regressions; killed-by / survives.
2. New candidate false rows (build fixture revs in your scratch like the harness's build_fixture): a decoy at census/round-32/waves/x/a2w1/SwarmExecutor08.md (stated limit), census/round-32/wave/a2w1/… vs waves/, a records/wave-/ with an empty wave name, a target with `..` or `//` components, case variants (Waves/), a symlink at the target path. Which does the r81 counter accept, and which are genuinely false?

# Acceptance
Mutant table; new-row table with accepted/refused and a falseness argument per row."""),
 ("S81Reviewer", "reviewer", f"""# Target
Review the round's two candidate diffs against the frozen predicates and the chronology.

# Change
1. Chronology: P {P} < F {F} < W1 {W1} < W2 {W2} < A {A}; `git diff {F} {W1} --stat`, `git diff {W1} {W2} --stat`: does any frozen file (counters, populations, variants, control receipts) change after F? Are the control receipts' instrument_sha256 equal to the prereg digests? Run tools/souji-freeze-check.py --root {LANE} --prereg census/round-81/preregistration.txt --rev {F} --substance --chronology.
2. Code review `git diff {BASE} {W2} -- tools/souji-vault-verify.sh` and `git diff --no-index census/round-80/c1-pointer-counter.py census/round-81/c1-pointer-counter.py`: correctness under set -euo pipefail, `$!` fallback in the trap, CLI_CLAIM with a trailing newline (the old `$(cli_claim)` stripped trailing newlines; does the new path keep `state`/`claim` identical?), the foreground fallback, trap reset semantics for signals ignored on entry.
3. Is each frozen predicate honoured as written by records/c1-after.txt and records/c2-after.txt (word by word)?

# Acceptance
HONOURED / NOT per predicate conjunct; findings by severity with file:line."""),
 ("S81CriticClaims", "critic", f"""# Target
Attack the two claims as claims.

# Change
1. C1: is it calibration (does the counter decide whether the lane's self-assessment pointers resolve) or quality on a rule the lane already holds? Is the do-nothing control (K-a, the r80 counter) red for the right reason? Could a cheaper rule (e.g. reject anything under census/round-<N>/ but waves/) meet the target — is NF12d's falseness a label the L1 chose, and is TF1/TF2 enough positive pressure? Is the rule over-fitted to the 14 real rows?
2. C2: does any no-signal behaviour change (stdin of the CLI, a new file in TMPDIR, the mktemp failure path, exit codes, stderr)? Does the claim's "within 5 s" hold when the CLI ignores TERM (the KILL fallback runs after 2 s)? Would the do-nothing tool pass any signal row? Is 8 -> 0 reached by a mechanism the frozen rows can see?
3. Harm hunt: any axis the round harms (operability of other entry points of souji-vault-verify.sh, calibration of SCORECARD rows)?

# Acceptance
Per claim: HOLDS / QUALIFIED / FAILS with reasons and reproducers; harm list."""),
 ("S81Sentinel", "sentinel", f"""# Target
Security and safety review of the W2 change to tools/souji-vault-verify.sh.

# Change
1. The private output file: mktemp under ${{TMPDIR:-/tmp}} (mode, symlink/race, a hostile TMPDIR), removal on every exit path (normal, signal, set -e failure between mktemp and rm); does the CLI's output ever reach a shared path?
2. The trap kills `-$pid` where pid = CLI_PID or, when empty, `$!`: can it signal a process group that is not timeout's (pid reuse after the job ended; `$!` stale from an earlier job; the window before timeout's setpgid)? Show a reproducer or argue impossibility.
3. The CLI now inherits the caller's stdin explicitly: any new exposure (interactive prompts, reading secrets piped to the tool)?
4. The tool's safety rails (header lines 28-41: read-only vault, no GUI launcher, secrets refusal) still hold at W2 (selftest H1/H2/H3).

# Acceptance
P/F per check with evidence; findings by severity."""),
 ("S81CriticDiscern", "critic", f"""# Target
Discernment check of the round's admit/reject decisions, routed-defect dispositions and self-reported mistakes.

# Change
1. Sources: S329 admitted (installed bash info node Lists; same capture file as S325). Re-open it; agree/disagree; is it a within-scope duplicate of S325? Is reusing the id S329 (a withdrawn r80 draft id) sound under CORPUS.md rule 2?
2. Routed defects: corpus/lessons/round-80-verifier-spotcheck.md section 5 items 1-7 vs corpus/lessons/round-81.md `## Inherited`: which are actually discharged by commits {BASE}..{A}, which carried, which mis-described?
3. Decisions left out of the claims: NF14 not a row (prereg Stated limits), V1 as verification not a claim, the K-d pid-only draft disclosed: agree/disagree.
4. Mistake mining: in records/prefreeze/ and the round so far, find a mistake the L1 made (or the r80 round made and r81 repeats) and propose a captured-by rule that can fail.

# Acceptance
Table: item / agree-disagree / reason / evidence; proposed captured-by rules."""),
 ("S81Scribe", "scribe", f"""# Target
Drafts for the L1 to integrate (drafts only, under your seat directory).

# Change
1. A new section (<=25 lines) for {LANE}/corpus/knowledge/gate-signal-handling.md titled "An asynchronous job for one bounded external call (r81, souji-vault-verify.sh)": when one `$(timeout …)` call is the only bounded child, an async job + `wait` + group kill is enough (vs the r80 session front); the stdin rule (S329 quote, lines 758-760), timeout's own forwarding (S326 cleanup()), the private output file, the foreground fallback; what C2 measured (records/c2-after.txt; K-a/K-b/K-c); limits (SIGKILL, CLI leaving timeout's group, INT ignored on entry, other children deferred). Read the existing entry first and match its style.
2. QUALITY rows Q146 (a counter's location rule must be grounded on the full set of real rows it must keep, listed in the prereg, plus at least one built true row it must keep) and Q147 (moving a foreground call to an async job must state and test what the job inherits: stdin, signal dispositions, cwd) in the shape of Q144/Q145 in {LANE}/corpus/QUALITY.md.
3. A SCORECARD capability row "signal-safe vault CLI call" marked closure-gated, in the shape of the r80 capability rows (grep 'closure-gated' {LANE}/SCORECARD.md).

# Acceptance
Files: S81Scribe/knowledge-section.md, S81Scribe/quality-rows.md, S81Scribe/capability-row.md."""),
]

spec = {
    "wave": "souji-r81-w1",
    "milestone": "souji r81: falsification of C1 census-capture binding and C2 vault CLI signal handling; V1 quarantine front",
    "reportDir": ".ufo/waves/round-81/w1",
    "context": context,
    "items": [{"name": n, "role": r, "prompt": HEAD + p} for n, r, p in items],
}
with open(f"{LANE}/.ufo/waves/round-81/w1-spec.json", "w") as f:
    json.dump(spec, f, indent=1)
print(len(items), "items")
