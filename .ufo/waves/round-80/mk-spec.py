#!/usr/bin/env python3
"""souji r80 wave w1 spec builder (L1 SoujiR80). Writes .ufo/waves/round-80/w1-spec.json.
The context tail is the r79 builder's text with round-79 -> round-80 plus the r79 M5 seat-scope line."""
import json
import os

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SCR = "/fast/scratch/hyaku/souji-r80"
GS = open(os.path.expanduser("~/.agents/skills/godspeed/directive.md")).read()
HEAD = "/skill:godspeed\n" + GS + "\n\n"
BASE = "f80f9368a8a20679438b1dffd72d0faab0ccf194"
P = "515d57c8c559d64d0c071cc25b07df0b815bd77a"
F = "aaad410f4de2c1b0e98f1a7f305736dfcee5c5ab"
W1 = "bd263c3f7d376e617c2fde5b99793622b0908b53"
W2 = "836dac3e336863c57d9d7125837ed22b22d8d044"
A = "a4aa888037922b7b5ccfac7150f156f92af5916e"
R = f"{LANE}/census/round-80"
TAIL = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ctx-tail.txt")).read().replace(
    "{LANE}", LANE).replace("{SCR}", SCR)

context = f"""# Goal
souji round 80 (lane repo {LANE}, lane id souji). The L1 (SoujiR80) holds the planner seat and is the ONLY integration owner: it commits through the lane helper and writes the report. You are one seat of ONE wave of 12 seats. Seats deliver files and findings only. Your mandate is to FALSIFY the frozen round-80 claims and the round's landed changes: re-derive every number yourself from committed bytes, run the frozen commands, and report what does not hold. A finding with a reproducer beats an opinion.

# Evidence durability
FIRST action: create your report file (the `Report:` trailer path) with a one-line skeleton, and append to it as you go. Your final yield must repeat the same content. A seat that ends without that file counts as no verdict.

# Chronology (binding; read {R}/preregistration.txt first — it is the frozen contract)
- Lane base (r79 closed rejected-honest-stop): {BASE}.
- P {P}: census/round-80/c1-false-row-harness.py + c1-false-rows.tsv (C1: 18 rows = the r79 population's 9 + S79MutCounter's NF6b/NF8/NF10 false rows + its 6 detector rows; fixture revs F0 (= r79 fixture 6436db6a), R1, R2, R3 built by the harness), census/round-80/c2-signal-counter.py + c2-population.tsv (C2: 15 rows; TERM/INT/HUP at 4 hang points of tools/souji-quarantine.sh --dry-run — engine stub, sha256sum file digest, find special scan, sort -z in the dir digest — plus 3 no-signal positives; resets INT/QUIT/TERM/HUP in each tool child, asserts the mark's program and parent chain, counts survivors by a per-row SOUJI_R80_NONCE env var), control variants under census/round-80/controls/variants/ and every control receipt, census/round-80/rec.sh (adds a `launch=` line), S327/S328 captures (census/round-80/srcs/) and rows in corpus/SOURCES.md, records/census-before.txt, records/prefreeze-feasibility.txt.
- F {F}: census/round-80/preregistration.txt (freeze-check receipt records/freeze-check-at-F.txt: claims=2 findings=0).
- W1 {W1}: C1 candidate census/round-80/c1-pointer-counter.py (successor of the frozen census/round-79/c2-pointer-counter.py): range members must be blobs of mode 100644/100755 (NF8; S327 git-ls-tree(1)); a MOVED target's round-<N> directory is the token's own or census/round-<N> (NF10); a QUARANTINED declaration names token and quarantine path each as a WHOLE path on one line (NF6b; one sentence-ending . , ; : allowed after a path).
- W2 {W2}: C2 candidate tools/souji-quarantine.sh: a front shell starts the worker (the same file) as `SOUJI_Q_WORKER=1 TMPDIR=<private mktemp dir> setsid "$BASH" "$SELF" "$@" <&0 &` and `wait`s; its TERM/INT/HUP trap SIGSTOPs then SIGKILLs every process whose /proc/<pid>/stat session field equals the worker pid (fork-free scan, up to 8 passes), removes the private dir, prints `SIGNAL<TAB>SIG<name><TAB>RECEIPT-QUARANTINE-SIGNALED`, exits 128+n. Nested calls inside the worker session (selftest children) run inline (SOUJI_Q_SESSION). Sources S325, S326, S328 setsid(1), S068 proc_pid_stat(5).
- A {A}: records/c1-after.txt (18 rows, mismatches 0, accepted 0; K-a r79 counter: 3 accepted NF6b/NF8/NF10), c1-regress-r78 (22/22, 12/12), c1-regress-r77 (35/35, 7/7), c1-regress-r79-harness (9/9); records/c2-after.txt (15 rows, mismatches 0, orphans 0; K-a base 12/12 orphans; K-b trap-only and K-c no-session-kill red 12 each), c2-regress-r13 (5/5), c2-regress-r17 (35, 0 failed, 2 skipped), c2-regress-selftest.txt (81 checks, 51 failed — run on a mode-0644 copy; the L1 reads it as an instrument defect, diagnosis/selftest-base-mode0644-copy.txt shows the BASE copy fails identically; c2-regress-selftest-committed-mode.txt: 108 checks 0 failed on the committed 100755 file), c2-domain-trial.txt (v3 identical=yes, 3 RESULT lines each; v1 was vacuous and v2 location-skewed — diagnosis/).

# Claims (frozen predicates are in the preregistration; never change them)
C1 calibration (lowest owned axis, 7; sourced on S327, opened this round): the successor pointer-resolution counter refuses the three false ledger rows the r79 wave found; harness accepted 3 -> 0 over 18 rows; K-b refuse-all 18/18 but 3/22 on the r78 regression; K-c ablations 1 each; r78 22/22+12/12, r77 35/35+7/7, r79 harness 9/9.
C2 operability (sourced on S328, opened this round): souji-quarantine.sh --dry-run answers a caller's TERM/INT/HUP by killing every process it started and exiting 128+n within 5 s; 15 rows mismatches 12 -> 0, orphans 12 -> 0; K-b/K-c red; r13 5/5, selftest 108/0, r17 35/0, domain trial identical.

# Frozen invocations (run from {LANE}; never alter counters, populations or controls)
- C1: python3 -B census/round-80/c1-false-row-harness.py --counter <counter path> --lane {LANE} --fleet-root /home/vgpnk/Projects/shokunin --work <SCRATCH>/c1 (~45 s). Regressions: python3 -B census/round-80/c1-pointer-counter.py --root {LANE} --rev e65538e73c7f1a8f7570bc24a2215da8a90043f3 --fleet-root /home/vgpnk/Projects/shokunin --population census/round-78/c2-population.tsv --ledger census/round-78/c2-pointer-ledger.tsv --forge census/round-78/c2-forge-r78.tsv (and round-77 population/ledger with census/round-78/c2-forge-r77.tsv).
- C2: put souji-quarantine.sh and souji-verify.sh from a revision into ONE dir (`git show <rev>:tools/<f> > D/<f>`); python3 -B census/round-80/c2-signal-counter.py --tool-dir D --work <SCRATCH>/c2 (~70 s; run it with no other heavy job of yours at the same time: rows have a 5 s settle).
- Every receipt starts with `command=<literal command>` (rec.sh); replaying that line with your scratch prefix is a valid check.
<SCRATCH> must be a fresh directory under {SCR}/<your seat name>/ (mkdir -p it). Counters refuse --work under /tmp, /var/tmp or /dev/shm. Anything that may block runs under `timeout -k 5 <s>` in its own session (setsid) so the whole process group dies; never leave a blocked process behind (check `ps -eo pid,args | grep <your scratch>` before you yield). Never send a signal to a process you did not start.

{TAIL}"""

items = [
 ("S80Connector", "connector", f"""# Target
Cross-claim separation and sibling-overlap scan for round 80. Read-only.

# Change
1. Causal separation: from receipt `# bind`/`instrument=` lines and commit contents (`git show --name-only` for W1 {W1}, W2 {W2}, A {A}) confirm no C1 receipt reads a quarantine-tool byte and no C2 receipt reads a C1 counter byte. Would C1 verify with W2 absent, and C2 with W1 absent? Verdict SEPARABLE/COUPLED.
2. Other lane tools under {LANE}/tools and {LANE}/tests that still run `timeout`-wrapped children from `$(...)` or pipelines with no signal handling (tools/souji-vault-verify.sh, tools/souji-verify.sh, tools/souji-census.sh, ...): file:line list; which of the two lane patterns (the r79 gate's async gate_run, the r80 front/worker session) would fit each, and why.
3. Sibling overlap (read-only; other *-shokunin repos under /home/vgpnk/Projects/shokunin): which sibling lane tools run `timeout` children in `$(...)` with no trap (grep -n 'timeout' / 'trap')? Table lane, file:line, exposed yes/no (cap 15 rows).

# Acceptance
Tables with verdicts and file:line; findings by severity."""),
 ("S80ScoutSources", "scout", f"""# Target
Re-open the round's sources and test the sentences the claims rest on. Read-only on the lane.

# Change
1. S327: `pacman -Qo /usr/share/man/man1/git-ls-tree.1.gz`; sha256 vs {R}/srcs/git-ls-tree.1.gz-2.56.0 (c0e10ef5…7e86); zcat and locate line 204 ("%(objectmode) %(objecttype) %(objectname)%x09%(path)") and line 252 ("The type of the object (commit, blob or tree)"). Is mode 120000 (symlink) or 160000 (gitlink/commit) a blob in ls-tree output? (git-ls-tree / gitglossary; the counter accepts only blob + 100644/100755.)
2. S328: `pacman -Qo /usr/share/man/man1/setsid.1.gz`; sha256 vs {R}/srcs/setsid.1.gz-util-linux-2.42.4 (614ae07f…7243); locate line 37. Confirm in util-linux source (https://raw.githubusercontent.com/util-linux/util-linux/v2.42.4/sys-utils/setsid.c or the nearest tag; record HTTP codes) that setsid forks only when getpgrp() == getpid(), and that a background job of a non-interactive bash is not a process-group leader (bash manual JOB CONTROL / S325 if needed). file:line.
3. S068 (corpus/SOURCES.md, proc_pid_stat(5) web copy): does field (6) session follow the parenthesised comm, and can comm contain `) ` (so the tool's `${{st##*) }}` parse is right)? Quote the man page (installed /usr/share/man/man5/proc_pid_stat.5.gz is fine).
4. Duplicates: would S327 duplicate S071/S078 within scope; is the withdrawn draft S329 truly a duplicate of S068? Admit/reject per row with reasons.

# Acceptance
sha256 match/mismatch; quotes with line numbers and word counts; per-question HOLDS/DISAGREE with file:line; admit/reject per row."""),
 ("S80ExecC1", "executor", f"""# Target
Reproduce C1 from committed bytes.

# Change
1. Run the harness with --counter census/round-79/c2-pointer-counter.py and with census/round-80/c1-pointer-counter.py (W1 {W1}); compare with controls/c1-K-a-r79-counter.txt and records/c1-after.txt; confirm the fixture revs (F0=6436db6a8ea2d9d0deea6f57cbc160fafa4c6c23, R1, R2, R3) are identical across two runs (determinism).
2. Replay controls c1-K-b-refuse-all(.txt, -regress-r78.txt) and the three c1-K-c-without-*.txt; confirm each variant's sha256 against its bind line and that each ablation accepts exactly the row its rule closes.
3. Replay records/c1-regress-r78.txt, c1-regress-r77.txt, c1-regress-r79-harness.txt at W1 and at the lane tip.
4. Diff the ITEM lines of the r77 and r78 populations under the r79 and r80 counters (same --rev): does any verdict move? If so, which rule moved it and is the new verdict right?

# Acceptance
Per receipt reproduced yes/no; ITEM-line diff; findings by severity."""),
 ("S80ExecC2", "executor", f"""# Target
Reproduce C2 from committed bytes, in the foreground and launched with `&`.

# Change
1. Run the C2 counter over the W2 tool ({W2}) once in the foreground and once launched with `&` from a bash script, and once over the base tool ({BASE}); compare SUMMARY/ROW lines with records/c2-after.txt and controls/c2-K-a-do-nothing.txt; record each run's `# launch` line and the per-row `ign=` values.
2. Replay controls/c2-K-b-trap-only.txt and c2-K-c-no-session-kill.txt (tool dir: the variant from controls/variants/ copied as souji-quarantine.sh beside the base souji-verify.sh); confirm sha256 against bind lines.
3. Replay records/c2-regress-r13.txt, c2-regress-r17.txt (tool dir with souji-quarantine.sh, souji-verify.sh, souji-vault-verify.sh at W2) and the selftest TWICE: on a `git show` copy (mode 0644) and on a copy with chmod 0755. Does the L1's reading (c2-regress-selftest.txt 81/51 is an instrument defect: the selftest runs "$SELF" directly) hold? Is the base tool's 0644 copy also 81/51?
4. Replay records/c2-domain-trial.txt (probe census/round-80/probes/domain-trial.sh) and say whether v3 is still vacuous in any way (e.g. both arms skip the bounded children).

# Acceptance
Per run: SUMMARY lines; per receipt: reproduced yes/no; selftest verdict."""),
 ("S80ExecEvade", "executor", f"""# Target
Break the W2 quarantine front/worker split outside the 15 frozen rows. Scripts under your seat dir; run the tool only on fixture repos in your scratch (copy the r80 C2 counter's fixture shape: git init a repo, an aged untracked file or directory, SOUJI_Q_SHOKUNIN_ROOT/SOUJI_Q_LEDGER pinned, --dry-run).

# Change
1. Signal timing: before the worker starts (during the front's mktemp), right after `setsid` but before the worker's own checks, between two targets, twice in a row, TERM then INT, a signal during the trap handler; does the tool always exit 128+n with the SIGNAL line, no survivor and no leftover private dir within ~2 s?
2. Escapes: a shimmed sha256sum that `setsid`s or double-forks a `sleep` (leaves the session) — does it survive (stated limit) — and one that only changes its process group (setpgid via `perl -e 'setpgrp'` or python os.setpgid) — killed?
3. Pass-through: stdin (--list from stdin is not a mode; check `<&0` with a here-doc target list if any), exit codes 0/1/2/3/4 identical to base for: usage error, no targets, live-fleet guard refusal (non-dry-run inside the fleet root), selftest; stdout/stderr ordering; TMPDIR unset / unwritable / with spaces (the front's mktemp fails -> exit 2?).
4. Environment spoofing: a caller that exports SOUJI_Q_WORKER=1 or SOUJI_Q_SESSION=<its own sid>: does the tool skip the front and lose the signal guarantee? Severity?
5. A non-dry-run stage-2 move in a scratch fixture (SOUJI_QUARANTINE_ALLOW_LIVE=1, --hold 0) signalled while a shimmed mv sleeps: what state is left (source present? residue?) — report, do not judge it as a claim row.

# Acceptance
Findings HIGH/MEDIUM/LOW with reproducer scripts and observed output; list of probes that held."""),
 ("S80MutTool", "mutation-tester", f"""# Target
Mutation test of the W2 front/worker code (tools/souji-quarantine.sh at {W2}, the block after LIVE_FLEET_ROOT) against the frozen C2 counter.

# Change
1. Build >=10 mutants (one change each): no SIGSTOP pass; a single kill pass (no loop); q_kill_session never called (pid kill only); kill only the worker's process group (`kill -- -$worker`); wrong exit code (fixed 1); no SIGNAL line; SIGNAL line with a wrong class; trap only TERM; no `rm -rf` of the private dir; worker not in a new session (drop `setsid`); `wait` replaced by a foreground run (`"$BASH" "$SELF" "$@"` without `&`); q_proc_sid reading field 5 (pgrp) instead of 6.
2. Run the frozen C2 counter on each (tool dir with the mutant as souji-quarantine.sh); where a mutant touches the no-signal path also run r13 and the selftest (mode 0755 copy). Table mutant / killed-by / surviving.
3. For every survivor: propose a row that kills it (do not edit lane files).

# Acceptance
Mutant table, kill ratio, survivors with proposed rows; mutants and outputs under your seat dir. Run one counter at a time (5 s settle)."""),
 ("S80MutCounter", "mutation-tester", f"""# Target
Falsify the r80 C1 counter (census/round-80/c1-pointer-counter.py at W1 {W1}): false ledger rows it still accepts, and mutants of its three new rules the frozen artefacts do not kill.

# Change
1. Mutants (>=8, one change each) of the three r80 rules and helpers: _regular accepting 120000/160000 modes or any blob; _regular skipped for `fleet:` members; the capture-root tuple widened (e.g. + "corpus") or the comparison made a prefix test; _whole's before-check dropped; _whole's after-check dropped; the sentence-punctuation allowance widened to any punctuation; _whole applied to the target only (not the token). Run each against the r80 harness and the r77/r78 regressions; table mutant / killed-by.
2. New false rows (NF11+): a range member that is a symlink (mode 120000) or a submodule entry; a MOVED target under census/round-<N>/ of the right round but unrelated (byte-equal decoy inside census/round-32/...: is that accepted, and is it the stated limit?); a declaration line naming `.../stub.` vs `.../stub.bak`; a declaration where the token occurs whole but inside a URL or a backticked longer path with a space; a quarantine path quoted with a trailing `)`. Build them in a fixture (copy the harness's build_fixture shape; fixed identity), run the pristine W1 counter, record got=.

# Acceptance
Mutant table with kill ratio; NF11+ rows with exact forged rows, observed got=, severity."""),
 ("S80Reviewer", "reviewer", f"""# Target
Review the round's landed changes against the preregistration.

# Change
1. Chronology: P {P} < F {F} < W1 {W1} < W2 {W2} < A {A} (git log --format='%H %ci'); every control receipt's rev= is the base; freeze-check receipt; prereg sha256 at F equals the file at the tip; the counters' and populations' sha256 at the tip equal the prereg lines.
2. Diff review `git diff {BASE} {W2} -- tools/souji-quarantine.sh`: the front/worker block — q_proc_sid parse, q_kill_session loop termination and races (a process forking between scan and kill; zombies; pid reuse), the worker's session-leader self-check, the nested-call branch (SOUJI_Q_SESSION), exit status pass-through, the private TMPDIR's lifetime on every exit path, `set -euo pipefail` interactions (does any new line abort under -e or -u?), usage() still printing lines 2-139.
3. Diff review `git diff --no-index census/round-79/c2-pointer-counter.py census/round-80/c1-pointer-counter.py`: each new rule vs its NF row; any legitimate r77/r78 ledger row it could wrongly refuse (the prefreeze record says a first NF10 draft refused L15/P31); _regular's ls-tree parse (-z, path with spaces).
4. The A-arm defects the L1 disclosed (selftest on a 0644 copy; domain trial v1 vacuous, v2 location-skewed): is the L1's re-measurement on the committed mode / symmetric layout the frozen predicate, or a changed rule? Say which and why.

# Acceptance
Findings HIGH/MEDIUM/LOW with file:line; verdict per claim: predicate honoured / not."""),
 ("S80CriticClaims", "critic", f"""# Target
Attack the two claims as claims.

# Change
1. C1: the 18 rows are the r79 wave's own findings plus the r79 population; the L1 wrote the rules knowing the rows. Is accepted 3 -> 0 a calibration gain or a fit? Is the capture-root rule (census/round-<N>) principled or tuned to pass L15/P31? Do K-b and the K-c ablations show each rule is needed and the harness discriminates?
2. C2: hang points are shims (`exec sleep 600`) and an engine stub; the directory-digest rows use a SAFE stub engine. Is the measured surface the tool's real behaviour? Would a tool that special-cases `sleep` pass? Does K-a skip exactly the claimed work, and do K-b/K-c skip only part of it? Is "operability" the honest axis?
3. The selftest conjunct was first measured red (81/51) on a 0644 copy and re-measured green on the committed file; the domain trial was re-written twice after A. Under the frozen kill rule, what is C2's verdict? Give the strictest defensible reading and the most lenient, with reasons.
4. Harm: does either claim move another owned axis (coverage, calibration, operability) down — e.g. the tool's runtime, a new failure mode (worker refuses when not a session leader), pointer verdicts on r77/r78?

# Acceptance
Per claim: verdict (holds / qualified / fails) with reasons and evidence pointers."""),
 ("S80Sentinel", "sentinel", f"""# Target
Safety review of the W2 front/worker code ({W2}).

# Change
1. Can q_kill_session ever STOP or KILL a process the tool did not start: a stale worker pid after the worker exited (signal arriving after `wait` returns but before `exit`), a pid reused by an unrelated session leader, another user's process (kill fails, but STOP?), the caller's own shell? Reproduce any path you find with harmless sleeps you own.
2. The private dir: `mktemp -d "${{TMPDIR:-/tmp}}/souji-quarantine.XXXXXXXX"` handed to the worker as TMPDIR — symlink/race exposure, removal on every exit path, and whether the worker's own ERRTMP and selftest fixtures now land inside it (so a SIGKILLed worker leaves nothing behind)?
3. The front trusts SOUJI_Q_WORKER / SOUJI_Q_SESSION from the environment: a hostile caller environment or a repo-controlled value (can repo content set them?) — what does it unlock?
4. Does the worker running in its own session change anything the tool does to repos (it loses the controlling tty: any git/jj call that prompts? any `read` from the terminal?)
5. No new line prints a secret-shaped path or child output (the tool's secret-shaped refusal list)?

# Acceptance
Findings HIGH/MEDIUM/LOW with reproducers (scripts under your seat dir); no host changes, no sudo, signals only to processes you started."""),
 ("S80Scribe", "scribe", f"""# Target
Draft the round's corpus text for the L1 to integrate (drafts only, under your seat directory — never the lane files).

# Change
1. Draft a new section (<=25 lines) for {LANE}/corpus/knowledge/gate-signal-handling.md titled "A session front for tools that use `$(...)` everywhere (r80, souji-quarantine.sh)": why the r79 async gate_run pattern does not fit a 1900-line tool that captures children in `$(...)` at many depths; the front/worker split (setsid, S328: line 37 quote), killing by session id from /proc/<pid>/stat field 6 (S068), SIGSTOP then SIGKILL in passes, the private TMPDIR; what C2 measured (records/c2-after.txt; K-a/K-b/K-c); named limits (SIGKILL to the front, setsid escapes, INT ignored on entry, stage-2 not measured). Read the existing entry first and match its style; cite receipts by lane path.
2. Draft QUALITY rows Q144 (a signal-handling claim on a tool must state the tool's process topology — which children run where — and a survivor census must count by an inherited marker, not by process group) and Q145 (a regression conjunct that replays a tool must run the committed object, mode included — a `git show` copy drops the exec bit; and an equivalence trial must refuse a vacuous match: both arms must produce the expected verdict lines) in the shape of Q142/Q143 in {LANE}/corpus/QUALITY.md (read them).
3. Draft a SCORECARD capability row for "signal-safe quarantine dry-run" in the shape of the r79 capability rows (grep 'closure-gated' {LANE}/SCORECARD.md) marked closure-gated.

# Acceptance
Files: S80Scribe/knowledge-section.md, S80Scribe/quality-rows.md, S80Scribe/capability-row.md."""),
 ("S80CriticDiscern", "critic", f"""# Target
Discernment check of the round's admit/reject decisions and its self-reported mistakes.

# Change
1. Sources: the L1 admits S327 (installed git-ls-tree(1)) and S328 (installed setsid(1)) and withdrew a draft S329 (installed proc_pid_stat(5)) as a within-scope duplicate of S068. Re-open all three yourself (sha256 vs captures under {R}/srcs/ where kept). Agree or disagree with each decision; is "installed man page" an acceptable tier-A locator?
2. The r79 spot-check (corpus/lessons/round-79-verifier-spotcheck.md section 5) routed seven defects; check which the round's commits ({BASE}..{A}) address and which the L1 must carry, against corpus/lessons/round-80.md `## Inherited`.
3. Mistakes the L1 already knows of (records/prefreeze-feasibility.txt: an NF10 draft refused legitimate rows; a slow session scan; records/diagnosis/: the selftest on a 0644 copy, the vacuous v1 and location-skewed v2 domain trials): are they the same class as r79 M2-M4 (measurement environment / instrument defects found after measuring)? What captured-by rule should have caught each before A, and can that rule fail (show how)?

# Acceptance
Table: item / agree-disagree / reason / evidence; proposed captured-by rules."""),
]

spec = {
    "wave": "souji-r80-w1",
    "milestone": "souji r80: falsification of C1 counter refusals and C2 quarantine signal handling",
    "reportDir": ".ufo/waves/round-80/w1",
    "context": context,
    "items": [{"name": n, "role": r, "prompt": HEAD + p} for n, r, p in items],
}
with open(f"{LANE}/.ufo/waves/round-80/w1-spec.json", "w") as f:
    json.dump(spec, f, indent=1)
print(len(items), "items")
