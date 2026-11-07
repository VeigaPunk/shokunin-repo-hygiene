#!/usr/bin/env python3
"""souji r79 wave w1 spec builder (L1 SoujiR79). Writes .ufo/waves/round-79/w1-spec.json.
The `# Write scope and bounds` .. `# Report format` context tail is the r78 builder's text with round-78 -> round-79."""
import json
import os

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SCR = "/fast/scratch/hyaku/souji-r79"
GS = open(os.path.expanduser("~/.agents/skills/godspeed/directive.md")).read()
HEAD = "/skill:godspeed\n" + GS + "\n\n"
BASE = "e65538e73c7f1a8f7570bc24a2215da8a90043f3"
P = "d7f40f764e6b25e32662384761d82d3032714eb1"
F = "e98cd0c55b1d8aaec8af8ff3402a5856263923ed"
W1 = "c8c3fbca5ac44184feac3a01ee964139f86c02a4"
W2 = "17009fa1f9d335a1bdde1e22ff3894c5d571c250"
A = "b8d094299e06bc66352f5232cd7a75d1f503c0fa"
R1 = "4a9bbb303db7f1508e24f60d4b9feff80bcbc079"
R2 = "feebf2ba6f120903e45d31cf322751c052f2feb9"
R = f"{LANE}/census/round-79"
TAIL = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ctx-tail.txt")).read().replace("{LANE}", LANE).replace("{SCR}", SCR)

context = f"""# Goal
souji round 79 (lane repo {LANE}, lane id souji). The L1 (SoujiR79) holds the planner seat and is the ONLY integration owner: it commits through the lane helper and writes the report. You are one seat of ONE wave of 12 seats. Seats deliver files and findings only. Your mandate is to FALSIFY the frozen round-79 claims and the round's landed changes: re-derive every number yourself from committed bytes; a number you cannot reproduce is a finding. Do not trust the L1's counts.

# Evidence durability
FIRST action: create your report file (the `Report:` trailer path) with a one-line skeleton, and append to it as you go. Your final yield must repeat the same content. A seat that ends without that file counts as no verdict.

# Chronology (binding; read {R}/preregistration.txt first — it is the frozen contract, Q99 grammar)
- Lane base (r78 admitted): {BASE}.
- P {P}: census/round-79/c1-signal-counter.py (C1 counter: 11 routes; PATH shims for git/python3/find exec `sleep 600` when the row's argv pattern occurs and write their pid to a mark file; the counter then sends TERM/INT/HUP to the gate pid only, waits 5 s, and counts survivors by a per-row SOUJI_R79_NONCE env var in /proc/*/environ), c1-population.tsv, c2-false-row-harness.py (C2 counter: runs a pointer-resolution counter once per row with a one-row forgery file; 9 rows = the r78 wave's S78MutCounter false rows NF1-NF5 and detector rows FP2 FP8 LP2 LP3; 'fixture' rows run in a deterministic `git clone --shared` fixture with planted files, fixture rev 6436db6a8ea2d9d0deea6f57cbc160fafa4c6c23), c2-false-rows.tsv, controls/variants/* and every control receipt at the base (controls/*.txt), srcs/ (S325 bash 5.3 info "Signals", S326 coreutils timeout.c v9.12), records/census-before.txt, records/prefreeze-feasibility.txt.
- F {F}: census/round-79/preregistration.txt.
- W1 {W1}: C1 candidate — tools/souji-pre-report-gate.sh: gate_run/gate_run_file run every child (git, find, head, python) as an async job under `timeout` with output in a private mktemp dir; traps TERM/INT/HUP -> kill the child's process group, remove the dir, print check-signal=FAIL and RECEIPT-GATE-SIGNALED, exit 128+n.
- W2 {W2}: C2 candidate — census/round-79/c2-pointer-counter.py (successor of the frozen census/round-78/c2-pointer-counter.py): `..` range targets must equal the expansion; a wrapped TOKEN must equal the whole path run opening the next line; MOVED needs round-<N> in the token; QUARANTINED needs a committed line (SKILL.md, LOG.md, SCORECARD.md, corpus/) naming token and path.
- A {A}: records/freeze-check-at-F.txt (0 findings), records/c1-after.txt (W1: mismatches=1 — row s4 INT: gate still alive at +5 s, no trap ran; EXIT=1), c1-regress-r78/r77/r76/r36/r27 (17/17, 16/16, 30/30, 21/21, 4/4), c2-after.txt (9/9, accepted 0), c2-regress-r78 (22/22, 12/12), c2-regress-r77 (35/35, 7/7).
- R1 {R1}: a repair after measurement (wait -n + 1 s ticker) aimed at a suspected pending-signal race. Its receipts census/round-79/records/repair/ (three C1 runs launched with `&` from a script, plus regressions) fail s4 identically 3/3.
- R2 {R2}: R1 reverted (gate bytes = W1). L1 diagnosis: the s4 failures are an instrument/launch artefact — a process started with `&` by a non-interactive shell begins with SIGINT ignored (S325), the counter's python and the gate inherit SIG_IGN, and bash cannot trap a signal ignored on entry. Probe census/round-79/probes/sigint-inherit.sh; foreground re-runs of the frozen counter at W1 land under census/round-79/records/foreground/. The claim's frozen kill rule is reported as met at A; confirm or refute the diagnosis.
- Known instrument defect (L1, disclosed): rows s3/s4 name argv pattern `ls-remote`, but the shim matches the pattern anywhere in argv and the row directory name contains `ls-remote`, so s3/s4 actually block at the FIRST `git config --file <rowdir>/clone/.git/config` call of check 0, not at ls-remote. Confirm or refute.

# Claims (frozen predicates are in the preregistration; never change them)
C1 operability (sourced on S325/S326, opened this round): the pre-report gate answers a caller's TERM/INT/HUP by killing its running child group and exiting 128+n with check-signal=FAIL; 11 rows mismatches 10 -> 0 and orphans 10 -> 0 (MEASURED at W1: 10 -> 1; the L1 reports the kill rule as met at W1 and the repair separately); K-b trap-only and K-c no-kill stay red (10 each); r78 17/17, r77 16/16, r76 30/30, r36 21/21, r27 4/4; domain trial on the lane at the report tip (L1, later).
C2 calibration (lowest owned axis, 7): the pointer-resolution counter refuses the five false ledger rows the r78 wave found; harness mismatches 5 -> 0, accepted 5 -> 0; K-b refuse-all scores 9/9 but resolves 3/22 on the r78 regression; K-c ablations (one rule removed each) 2/1/1/1; r78 22/22 + 12/12 and r77 35/35 + 7/7 with the new counter.

# Frozen invocations (run from {LANE}; never alter counters, populations or controls)
- C1: copy the gate and tools/souji-receipt-write.py at a revision into ONE dir (`git show <rev>:tools/souji-pre-report-gate.sh > D/souji-pre-report-gate.sh`, same for the writer); python3 -B census/round-79/c1-signal-counter.py --gate-dir D --work <SCRATCH>/c1 (work absent or empty; ~65 s).
- C2: python3 -B census/round-79/c2-false-row-harness.py --counter <counter path> --lane {LANE} --fleet-root /home/vgpnk/Projects/shokunin --work <SCRATCH>/c2 (~40 s). Regressions: python3 -B census/round-79/c2-pointer-counter.py --root {LANE} --rev <rev> --fleet-root /home/vgpnk/Projects/shokunin --population census/round-78/c2-population.tsv --ledger census/round-78/c2-pointer-ledger.tsv --forge census/round-78/c2-forge-r78.tsv (and the r77 set: --population census/round-77/c2-population.tsv --ledger census/round-77/c2-pointer-ledger.tsv --forge census/round-78/c2-forge-r77.tsv).
- Every receipt starts with `command=<literal command>` (rec.sh); replaying that line with your scratch prefix is a valid check.
<SCRATCH> must be a fresh directory under {SCR}/<your seat name>/ (mkdir -p it). Counters refuse --work under /tmp, /var/tmp or /dev/shm. Anything that may block runs under `timeout -k 5 <s>` in its own session (setsid) so the whole process group dies; never leave a blocked process behind (check `ps -eo pid,args | grep <your scratch>` before you yield).

{TAIL}"""

items = [
 ("S79Connector", "connector", f"""# Target
Cross-claim separation and sibling-overlap scan for round 79. Read-only.

# Change
1. Causal separation: from receipt `# bind`/`instrument=` lines and commit contents (`git show --name-only` for W1 {W1}, R1 {R1}, W2 {W2}) confirm no C1 receipt reads a C2 byte and no C2 receipt reads a gate byte. Would C1 verify with W2 absent, and C2 with W1/R1 absent? Verdict SEPARABLE/COUPLED.
2. Other lane tools under {LANE}/tools and {LANE}/tests that run children under `timeout` in the foreground (`$(timeout ...)`, `timeout ... | ...`) or with no signal handling, so a caller's TERM orphans the child: file:line list, and whether the r79 pattern (gate_run) would apply.
3. Sibling overlap (read-only; other *-shokunin repos under /home/vgpnk/Projects/shokunin): which sibling pre-report gates or lane tools run `timeout`-wrapped children in the foreground with no trap (`grep -n timeout`, `grep -n trap`)? Table: lane, file:line, exposed yes/no.

# Acceptance
Tables with verdicts and file:line; findings by severity."""),
 ("S79ScoutSources", "scout", f"""# Target
Re-open the round's two new sources and test the sentences C1 rests on. Read-only on the lane.

# Change
1. S325: the installed bash info (pacman -Qo /usr/share/info/bash.info.gz; zcat it) node "Signals": compare with {R}/srcs/bash.info-5.3-Signals.txt (sha256 42b40cdf…a462) and {R}/srcs/bash.info.gz-5.3 (cde1a336…588f). Locate "it will not execute the trap until the command completes" and "the `wait` builtin will return immediately with an exit status greater than 128, immediately after which the shell executes the trap." (line numbers, word counts <=25). Try the online manual https://www.gnu.org/software/bash/manual/html_node/Signals.html (curl -m 30; gnu.org was unreachable for the L1) and record the outcome.
2. Does the bash source confirm it, and is there a documented race (a signal that arrives before `wait` starts)? Look at bash 5.3 sources if reachable (e.g. https://raw.githubusercontent.com/bminor/bash/<tag>/jobs.c wait_sigint_handler / CHECK_WAIT_INTR, trap.c trap_handler, builtins/wait.def; try tags like bash-5.3 or master/devel; record HTTP codes). Quote file:line for: SIGINT special handling while waiting (`wait_sigint_handler`), when `wait_signal_received` is set, and whether a trap pending before `wait` interrupts it. This decides whether the R1 repair addresses a real race.
3. S326: https://raw.githubusercontent.com/coreutils/coreutils/v9.12/src/timeout.c; compare sha256 with {R}/srcs/coreutils-timeout.c-v9.12 (bf1f0d99…8cc9); quote the setpgid(0,0) comment lines; does timeout forward a received TERM/INT/HUP to its group (cleanup handler send_sig(0, sig))? file:line. Is installed /usr/bin/timeout 9.12 (pacman -Qo)?
4. corpus/SOURCES.md: would rows for S325/S326 duplicate S034/S038/S094/S098 (timeout manual) or S043/S065/S072 (bash manual) within scope? Admit/reject per row with reasons.

# Acceptance
sha256 match/mismatch; quotes with line numbers and word counts; per-question HOLDS/DISAGREE with file:line; admit/reject per row."""),
 ("S79ExecC1", "executor", f"""# Target
Reproduce C1 from committed bytes, at W1, in the foreground and with `&`.

# Change
1. Run the C1 counter over the W1 gate ({W1}) twice in the foreground and twice launched with `&` from a bash script, and once over the base gate ({BASE}); check the SIGINT disposition the counter process starts with (python3 -c 'import signal; print(signal.getsignal(signal.SIGINT))' in each launch mode); compare SUMMARY/EXIT/ROW lines with records/c1-after.txt and controls/c1-K-a-do-nothing.txt. Run some runs concurrently (load matters: the A run's s4 failure happened with 11 counters in parallel).
2. Replay controls/c1-K-b-trap-only.txt and c1-K-c-no-kill.txt from their command= lines (gate dir: the variant from controls/variants/ copied as souji-pre-report-gate.sh beside the base writer); confirm each variant's sha256 equals the receipt's bind line.
3. Replay records/c1-regress-r78/r77/r76/r36/r27 with the W1 gate.
4. Confirm or refute the s3/s4 mislabel and the L1's SIGINT-ignored-on-entry diagnosis (where do s3/s4 block? print the shim's argv at the mark).
5. After every run, check that no process from your scratch dir is left.

# Acceptance
Per run: SUMMARY lines; per receipt: reproduced yes/no; s3/s4 verdict."""),
 ("S79ExecEvade", "executor", f"""# Target
Break the W1 gate's signal path ({W1}; R2 restores these bytes) outside the 11 frozen rows. Write scripts under your seat dir; run the gate on fixtures in your scratch only.

# Change
1. Signal timing: signal before the first child (during mktemp), between children, during the short `$(...)` forks (realpath, awk), twice in a row, TERM then INT, a signal during the trap handler itself; does the gate always exit 128+n with check-signal=FAIL and no survivor within ~2 s?
2. Escaping children: a shimmed git that `setsid`s or double-forks a `sleep` (leaves timeout's process group) — does it survive a TERM to the gate? Is that within the claim (the claim kills the child's process group) or a stated-limit gap?
3. Environment: TMPDIR unset, unwritable, with spaces, or a symlink; HOME unset; a huge child output (100 MB) and NUL bytes in output; the ticker under `ulimit -u` pressure.
4. No-signal behaviour: run the W1 gate on a clean fixture and on the lane (read-only: --lane {LANE} --branch master --report <a scratch copy of a report with one ## SHONEN> --prereg {R}/preregistration.txt) and compare check lines with the base gate; measure the wall time difference.

# Acceptance
Findings HIGH/MEDIUM/LOW with reproducer scripts and observed output; list of probes that held."""),
 ("S79MutGate", "mutation-tester", f"""# Target
Mutation test of the W1 gate's signal path against the frozen C1 counter.

# Change
1. Build >=10 mutants of tools/souji-pre-report-gate.sh at W1 {W1} (one change each): drop the group kill; drop the pid kill; wrong exit code (128 fixed); no gate_cleanup in the handler; trap only TERM; gate_child never set; print check-signal=PASS; run one call site (e.g. find) in the foreground again; remove `<&0` from gate_run_file (the byte-truth heredoc); remove the trailing-newline strip.
2. Run the frozen C1 counter (and the r78/r36 regressions where the mutant touches no-signal behaviour) on each; table mutant / killed-by / surviving.
3. For every survivor: propose a row that kills it (do not edit lane files).

# Acceptance
Mutant table, kill ratio, survivors with proposed rows; mutants and outputs under your seat dir."""),
 ("S79ExecC2", "executor", f"""# Target
Reproduce C2 from committed bytes.

# Change
1. Run the harness with --counter census/round-78/c2-pointer-counter.py and with census/round-79/c2-pointer-counter.py (at W2 {W2}); compare with controls/c2-K-a-r78-counter.txt and records/c2-after.txt; confirm the fixture rev is 6436db6a8ea2d9d0deea6f57cbc160fafa4c6c23 in both runs (determinism).
2. Replay controls c2-K-b-refuse-all(.txt, -regress-r78.txt) and the four c2-K-c-without-*.txt; confirm each variant's sha256 against its bind line.
3. Replay records/c2-regress-r78.txt and c2-regress-r77.txt at W2 and at the current lane tip.
4. Run the lane pointer check (python3 -B tools/souji-pointer-check.py --root . --rev <tip> LOG.md SCORECARD.md SKILL.md corpus/QUALITY.md corpus/README.md) and report the missing counts; for each MISSING, does the r79 counter's rule change alter any ledger verdict of the r77/r78 populations (diff ITEM lines r78 counter vs r79 counter)?

# Acceptance
Per receipt reproduced yes/no; ITEM-line diff; findings by severity."""),
 ("S79MutCounter", "mutation-tester", f"""# Target
Falsify the r79 C2 counter (census/round-79/c2-pointer-counter.py at W2 {W2}): find false ledger rows it still accepts, and mutants of its four new rules the frozen artefacts do not kill.

# Change
1. Mutants (>=8, one change each) of the four r79 rules (range expansion, whole next-line run, MOVED round requirement, QUARANTINED declaration) and of their helpers (_declared's AUTHORITY tuple, the `token in line` test, the range zero-padding, the 999 bound). Run each against the harness (census/round-79/c2-false-row-harness.py) and both regressions; table mutant / killed-by.
2. New false rows (NF6+): e.g. a QUARANTINED path declared in a committed line that names the token for another reason (a lesson that quotes both while refusing the quarantine); a range row whose members exist but one is a directory; `fleet:` members in a range; a wrapped TOKEN whose next line starts with a backtick-quoted different path; MOVED to a byte-equal copy at the right round in a different subtree. Build them in a scratch fixture (S78MutCounter repro.txt step 6 style; follow the fixture rules in the context) and report got= for both counters.

# Acceptance
Mutant table with kill ratio; NF6+ rows with exact forged rows, observed got=, severity."""),
 ("S79Reviewer", "reviewer", f"""# Target
Review the round's landed changes against the preregistration.

# Change
1. Chronology: P {P} < F {F} < W1 {W1} / W2 {W2} < A {A} < R1 {R1} < R2 {R2} (git log --format='%H %ci'); every control receipt's rev= is the base; freeze-check receipt; prereg sha256 at F equals the file at the tip.
2. Diff review `git diff {BASE} {W1} -- tools/souji-pre-report-gate.sh` (and confirm R2's gate blob equals W1's): correctness of gate_run/gate_run_file (output capture identical to the old `$(...)` incl. trailing newlines and stderr handling per call site; return codes 124/137 for timeout detection; the heredoc stdin; the nonreg_sources global), the trap (kill order, exit codes, cleanup idempotence). File:line per finding.
3. Diff review `git diff --no-index census/round-78/c2-pointer-counter.py census/round-79/c2-pointer-counter.py` (at W2): each new rule vs its stated NF row; any legit r77/r78 ledger row it could wrongly refuse; _declared's git grep (rev form, -h, pathspec, binary files).
4. Does the claim text (prereg Target) match what the counters compute (same predicate sentence in plan, code and receipt)?

# Acceptance
Findings HIGH/MEDIUM/LOW with file:line; verdict per claim: predicate honoured / not."""),
 ("S79CriticClaims", "critic", f"""# Target
Attack the two claims as claims.

# Change
1. C1: the hang points are shims (`exec sleep 600`), not real blocked git. Is the measured surface the real gate behaviour? Would a gate that special-cases the shim (e.g. kills `sleep`) pass? Does the do-nothing control (K-a) really skip the claimed work, and do K-b/K-c skip only part of it? The W1 measurement was 10 -> 1 and the repair R1 came after measurement: what verdict does the frozen kill rule give, and is any repair-time number admissible as the claim?
2. C2: the population is the r78 wave's own findings (non-author) — but the L1 wrote the fixes knowing the rows. Is 5 -> 0 a calibration gain or a fit to five known rows? Does K-b refuse-all (9/9 on the harness) show the harness alone is not discriminating? Are the K-c ablations enough to show each rule is needed? Is "calibration" the honest axis (the claim changes an instrument, not a self-assessment statement)?
3. Separability and harm: does C1 or C2 move any other axis down (gate runtime, pointer verdicts on r77/r78 populations)?

# Acceptance
Per claim: verdict (holds / qualified / fails) with reasons and evidence pointers."""),
 ("S79Sentinel", "sentinel", f"""# Target
Safety review of the W1 gate's new code path ({W1}; R2 restores these bytes).

# Change
1. The private dir: `mktemp -d -t souji-gate.XXXXXXXX` under a caller TMPDIR — symlink/race attacks on $gate_tmp/o by another local user or a hostile repository (can repo content influence TMPDIR?); is it removed on every exit path (normal, usage error after creation, signal, `set -u` abort)?
2. `kill -KILL -- -$gate_child`: can it ever hit a process group the gate does not own (pid reuse, child not yet a group leader, gate_child stale after the loop)? `kill $gate_tick` after the ticker exited?
3. Does running children as async jobs change what they inherit (stdin now explicit `<&0`; SIGINT/SIGQUIT ignored in async children when job control is off — S325) in a way that changes check results or lets a child outlive the gate on a normal exit?
4. D30 no-echo: any new detail line printing a path or child output?
5. Re-check the r78 hostile-repo routes still hold at W1 (FIFO config/HEAD/include) — spot-run 3 of them in scratch.

# Acceptance
Findings HIGH/MEDIUM/LOW with reproducers (scripts under your seat dir); no host changes, no sudo."""),
 ("S79Scribe", "scribe", f"""# Target
Draft the round's corpus text for the L1 to integrate (drafts only, under your seat directory).

# Change
1. Draft two SOURCES rows in the exact 11-column shape of {LANE}/corpus/SOURCES.md rows S322-S324 (read them): S325 GNU Bash 5.3 Reference Manual node "Signals" as installed (bash 5.3.20-1, /usr/share/info/bash.info.gz, capture census/round-79/srcs/bash.info.gz-5.3 sha256 cde1a3366897684b0a86fe553687e31d070b7839b19ca98186ffc6e0e105588f, node text census/round-79/srcs/bash.info-5.3-Signals.txt), quote "it will not execute the trap until the command completes" (verify words and lines yourself); S326 coreutils src/timeout.c at tag v9.12 (https://raw.githubusercontent.com/coreutils/coreutils/v9.12/src/timeout.c, capture census/round-79/srcs/coreutils-timeout.c-v9.12, sha256 bf1f0d998729f12ddd2323d69db34648763d807d9c4d769eb1414a8738652cc9, 21183 bytes, fetched 2026-11-07 HTTP 200), quote line 567 "Ensure we're in our own group so all subprocesses can be killed." No `|` in any cell.
2. Draft corpus/knowledge/gate-signal-handling.md (<=60 lines): why `timeout` children outlive a killed script (S326), why a bash trap does not fire while a foreground child runs (S325), the async-job + wait pattern, and why a signal ignored on entry cannot be trapped (S325; the r79 s4 launch artefact), what the gate now guarantees and its named limits (SIGKILL, setsid escapes, short forks). Cite S-ids only, no `.ufo/waves` paths.
3. Draft QUALITY rows Q142 (a lane tool that starts children must kill them when it is signalled and must be measured by a survivor census, not by exit code) and Q143 (a forged-row counter's population includes the previous wave's false rows) in the shape of Q140/Q141 in {LANE}/corpus/QUALITY.md.
4. Run /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file <a scratch copy of corpus/SOURCES.md with your two rows appended to the Registry table> and record output and exit code.

# Acceptance
Files: S79Scribe/sources-rows.md, S79Scribe/knowledge-gate-signal-handling.md, S79Scribe/quality-rows.md, S79Scribe/census-validate.txt; the census exit code."""),
 ("S79CriticDiscern", "critic", f"""# Target
Discernment check of the round's admit/reject decisions and its self-reported mistakes.

# Change
1. Sources: the L1 admits S325 (installed bash info, not the online manual: gnu.org unreachable at 02:00 -03) and S326 (timeout.c v9.12 rather than the manual rows S034/S038/S094/S098 the lane already holds). Agree or disagree: is an installed info file an acceptable tier-A source; is source code the right citation for the process-group behaviour? Re-open both yourself.
2. Rejections the L1 made: the bminor/bash GitHub mirror paths (HTTP 404 for doc/bashref.texi at master, devel, bash-5.3) and coreutils timeout.c at master (replaced by the v9.12 tag). Agree or disagree.
3. The r78 spot-check (corpus/lessons/round-78-verifier-spotcheck.md section 5) routed six defects; check which the round's commits address (git log {BASE}..HEAD) and which the L1 must carry.
4. The disclosed instrument defects (s3/s4 argv pattern matching the row directory name; the counter not resetting an inherited SIGINT ignore) and the misdiagnosed R1 repair: are they recorded as mistakes with a captured-by and a fix that can fail?

# Acceptance
Table: item / agree-disagree / reason / evidence."""),
]

spec = {
    "wave": "souji-r79-w1",
    "milestone": "souji r79: falsification of C1 gate signal handling and C2 false-ledger-row refusal",
    "reportDir": ".ufo/waves/round-79/w1",
    "context": context,
    "items": [{"name": n, "role": r, "prompt": HEAD + p} for n, r, p in items],
}
with open(f"{LANE}/.ufo/waves/round-79/w1-spec.json", "w") as f:
    json.dump(spec, f, indent=1)
print(len(items), "items")
