#!/usr/bin/env python3
"""Build the souji r84 wave-1 spec. Run: python3 .ufo/waves/round-84/build-spec.py > .ufo/waves/round-84/w1-spec.json
P and F hashes are read from the lane's git branch (P = instruments + controls, F = preregistration alone)."""
import json
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"

GOD = """/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim \u2014 let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.

"""


def git(*a):
    return subprocess.run(["git", "-C", LANE, *a], stdout=subprocess.PIPE, text=True,
                          check=True).stdout.strip()


base = git("rev-parse", "master")
log = git("log", "--format=%H %s", "-4", "master").splitlines()


def find(prefix):
    for l in log:
        h, _, s = l.partition(" ")
        if s.startswith(prefix):
            return h
    return "<" + prefix + ": not found yet>"


p_hash = find("round-84: instruments")
f_hash = find("round-84: preregistration")

CTX = f"""# Goal
souji round 84 (lane repo {LANE}, lane id souji). The L1 (SoujiR84) holds the planner seat and is the ONLY
integration owner: it freezes the claims, integrates your findings, commits through the lane helper, measures and
writes the report. You are one seat of ONE v1 wave of 12 seats. Seats deliver files and findings only: never commit,
never push, never mutate git/jj state, never edit fleet or sibling-lane files, never edit MANIFEST.json,
.ufo/state/*, .scratch/* or .ufo/watchdog.log. A finding with a reproducer beats an opinion.

# Evidence durability
FIRST action: create your report file (the `Report:` trailer path) with a one-line skeleton and append to it as you
go. Your final yield must repeat the same content. A seat that ends without that file counts as no verdict.
Every `Report:` trailer path is relative to {LANE} \u2014 write it at {LANE}/<that path>.

# Frozen round (read {LANE}/census/round-84/preregistration.txt FIRST \u2014 it is the contract)
Lane base: {base} (r83 closed admitted). P {p_hash}: instruments + controls + the before receipts. F {f_hash}:
preregistration alone.
C1 (calibration 7): the lane's false-row population is the instrument that certifies the pointer counter's rule. The
r84 population census/round-84/c1-false-rows.tsv is 44 rows: the r83 36 rows byte-for-byte plus TF8, TF9, TF10 (TRUE)
and NF-P, NF-L, NF-L2, NF-M, NF-Q (false) at fixture revision R7. census/round-84/c1-clause-battery.py scores the
counter on either pinned population and applies the five frozen single-edit mutants in census/round-84/c1-mutants.json
(m6 digest-blind, m7 round-blind, m8 w-only shapes, m9 basename-only, m10 records-as-wave). Target: pristine green on
both populations (36/0 and 44/0) and 5/5 mutants killed on the 44-row population, while the 36-row population kills
0/5 (census/round-84/controls/c1-before-r83-population.txt).
C2 (operability 8): in tools/souji-vault-verify.sh, cli_kill_tree must freeze the CLI's descendant tree (SIGSTOP each
discovered pid before any trappable signal, a second map pass for a child forked in the read->stop window, then a
SIGKILL sweep) so a CLI that traps the caller's signal and forks a setsid'd child leaves nothing behind; the frozen 22-row population
census/round-84/c2-population.tsv (the r83 20 rows unchanged + l1-late-setsid-pid and l2-late-setsid-group, whose
`latefork` stub traps the signal and starts a setsid'd `sleep 600`) reports SUMMARY rows=22 mismatches=0 errors=0
orphans=0, EXIT=0. Control K-a = census/round-84/controls/c2-K-a-r83-tool.sh (the r83 tool bytes, sha256 72a405f2...)
-> census/round-84/controls/c2-before-r83-tool.txt: mismatches=2 on l1/l2, 1 survivor each, EXIT=1.

# Frozen commands
C1 before: python3 -B census/round-84/c1-clause-battery.py --counter census/round-84/c1-pointer-counter.py --work <empty dir outside /tmp> --only r83
C1 after:  python3 -B census/round-84/c1-clause-battery.py --counter <candidate> --work <empty dir outside /tmp> --only r84 --expect-killed 5
C2:        python3 -B census/round-84/c2-late-fork-counter.py --tool <candidate tool> --work <empty dir outside /tmp>
The population sha256 values are pinned by the harness and the counter; editing a population row kills the claim.

# Scratch and safety (binding)
- Scratch root: /fast/scratch/hyaku/souji-r84/<YourSeatName>/ ; create it with mkdir -p, pass it explicitly, never
  rely on TMPDIR, never write under /tmp (files <50 MB only if unavoidable). Remove your scratch before you yield:
  copy receipts into {LANE}/.ufo/waves/round-84/w1/ first (`trap 'rm -rf -- \"$S\"' EXIT`).
- Any git fixture: D=$(mktemp -d /fast/scratch/hyaku/souji-r84/<Name>/fx.XXXXXX) && git -C "$D" init -q; verify
  `git -C "$D" rev-parse --show-toplevel` equals $D before any mutating git call. Never run git/jj in the lane
  except read-only (log/show/diff/status/rev-parse/merge-base/cat-file), never with an empty or unchecked variable.
- Tooling authorization (operator, 2026-10-19): you may install or upgrade tools that help the task \u2014 read
  /home/vgpnk/.omp/agent/RULES.md first (official channels; record tool/version/channel/reason in your report).
  pacman transactions are PAUSED host-wide: install via `uv tool`/`npx`/an official binary in ~/.local/bin only, and
  never run pacman -S/-Sy/-Syu/-U/-R. Never mutate host sysctls.
- Never message agent://all or another lane's seats; coordinate only through your report and, if needed, the L1.
- Read-only on lane tracked files unless your item says otherwise; candidate bytes go under your seat directory
  {LANE}/.ufo/waves/round-84/w1/<YourSeatName>/ and the L1 integrates them.
- No subagent dispatch (you are a leaf; an executor may spawn one read-only labrat probe only).
"""

ITEMS = []


def item(name, role, body):
    ITEMS.append({"name": name, "role": role, "prompt": GOD + body})


item("S84ExecC1", "executor", f"""# Target
Re-derive the C1 claim end to end on the committed bytes. OWN ONLY your seat dir
{LANE}/.ufo/waves/round-84/w1/S84ExecC1/ (create it) plus your report.

# Change
1. Read {LANE}/census/round-84/preregistration.txt, census/round-84/c1-false-rows.tsv, c1-mutants.json and
   c1-clause-battery.py. For EACH of the eight new rows (TF8, TF9, TF10, NF-P, NF-L, NF-L2, NF-M, NF-Q) state, from
   the counter's own judge() order (`census/round-84/c1-pointer-counter.py`), why the expected verdict is the one the
   row carries: which branch decides it, the token's frozen digest, the round comparison, the own-tree shape test and
   the suffix comparison. A row whose expectation you cannot derive branch-by-branch is a finding: name it.
2. Rebuild the R7 fixture independently: write your own fixture under your scratch (a `git clone --shared` of the lane
   at the base, copies at the eight R7 paths, same commit identity/dates as the harness uses is NOT required) and run
   the harness against it by pointing `--population` at a COPY of the population whose R7 rows you re-point; if that is
   too costly, instead verify each R7 path exists at the harness's R7 commit and that its blob digest equals the token's
   frozen digest (or deliberately differs for NF-L). Record the exact commands.
3. Run the after arm: `python3 -B census/round-84/c1-clause-battery.py --counter census/round-84/c1-pointer-counter.py
   --work /fast/scratch/hyaku/souji-r84/S84ExecC1/after --only r84 --expect-killed 5`. Record the SUMMARY, every
   MUTANT line, and the exit code.
4. Run the regression: the r83 harness over the r83 population with the same counter
   (`census/round-83/c1-false-row-harness.py`, 36 rows). Any red row is a finding.
5. Deliver `c1-after-receipt.txt` + your report with the branch-by-branch table and the raw outputs.

# Acceptance
The battery prints `SUMMARY ... killed_r84=5` and exits 0; the r83 36 rows stay green; each of the eight new rows has a
derived verdict. Do not edit the population, the mutants, the harness, the battery or the counter.""")

item("S84ExecC2", "executor", f"""# Target
Build and score the C2 candidate tool. OWN ONLY your seat dir {LANE}/.ufo/waves/round-84/w1/S84ExecC2/ (create it)
plus your report.

# Change
1. Copy {LANE}/tools/souji-vault-verify.sh (sha256 72a405f2...) to your seat dir as `souji-vault-verify.sh` and
   rewrite ONLY `cli_kill_tree` (+ its comment block). The repair the prereg freezes: FREEZE before signalling —
   SIGSTOP every descendant discovered from the /proc map before any trappable signal is delivered (a stopped process
   cannot run a trap or fork), run a second map pass to STOP a child forked in the read->stop window, then SIGKILL the
   frozen set. Keep: one fork-free pass per iteration (bash builtins only, no pgrep/ps/cat per pid), the whole-file
   stat read with the last-`)` strip, the starttime re-check before every STOP and KILL, the root pid never signalled,
   and `cli_on_signal`'s group kill, KILL fallback and `souji-vault-verify: SIG<name>` line unchanged. A TERM to a
   stopped pid is deferred, so the freeze is what removes the trap from the path — say so in the comment.
2. Score: `python3 -B census/round-84/c2-late-fork-counter.py --tool <your tool> --work
   /fast/scratch/hyaku/souji-r84/S84ExecC2/c2`. Target rows=22 mismatches=0 errors=0 orphans=0, EXIT 0, and both
   l1/l2 rows `survivors=0 tmpleft=0`. If a row still fails, report WHICH with its seconds and survivors.
3. Regressions on your bytes: `bash <candidate> --selftest`; `bash tests/fixtures/r17-jj-receipts.sh` with the
   tool-dir your candidate lives in (see the r83 lesson for the exact invocation); and
   `python3 -B census/round-81/probes/tmpdir-in-vault.py --tool <candidate> --work <empty>`.
4. Deliver `c2-after-receipt.txt`, the `diff -u` of cli_kill_tree against the r83 tool, the per-pass cost (seconds
   for l1/l2 and d24), and your report.

# Acceptance
The frozen command prints the target SUMMARY and exits 0; selftest/r17/probe D green; the diff touches only
cli_kill_tree and its comment; no external command is called per tree node. Do not edit tools/souji-vault-verify.sh,
the population or the counter.""")

item("S84ExecEvade", "executor", f"""# Target
Try to make the C2 candidate leave a process behind, lose or change a verdict, exit wrongly, or leak its private
file. Read-only on the lane; all work in your scratch. OWN ONLY your seat dir {LANE}/.ufo/waves/round-84/w1/S84ExecEvade/.

# Change
1. Use the candidate `{LANE}/.ufo/waves/round-84/w1/S84ExecC2/souji-vault-verify.sh` if it exists when you start;
   otherwise the r83 tool `{LANE}/tools/souji-vault-verify.sh`. Copy it into your scratch before probing.
2. Shapes to build from the counter's stub patterns (`census/round-84/c2-late-fork-counter.py`): (a) a CLI that forks
   a setsid child on the FIRST signal and again on the second; (b) a CLI that double-forks a daemon (`setsid` +
   `&` + exit) during the walk; (c) a 24-child fan-out plus a late setsid child; (d) a comm containing `)` and a
   newline; (e) a CLI whose child exits so a pid could be reused (state how you detect reuse without racing the host);
   (f) a CLI that ignores TERM; (g) a fast exit. Signal the tool by pid and by group, with and without
   `SHELLOPTS=monitor`.
3. Per shape record: exit within 5 s? rc? SIG line present? survivors (nonce method)? private TMPDIR empty? Any signal
   delivered to a pid that is not a descendant (use your own canary processes only)?
4. Deliver `evade-receipt.txt` + your report with the exact stub bytes and commands.

# Acceptance
Each shape has an observed result and a reproducer path; a survival or wrong verdict is a finding with the bytes that
produced it. Never signal a process outside your own fixtures; never touch lane tracked files.""")

item("S84Scribe", "scribe", f"""# Target
Drafts for the L1 to integrate (drafts only, under {LANE}/.ufo/waves/round-84/w1/S84Scribe/).

# Change
1. A new section for {LANE}/corpus/knowledge/gate-signal-handling.md titled "A re-walk after the TERM pass (r84,
   `tools/souji-vault-verify.sh`)": the late-fork escape (a CLI that traps the signal and forks after the map pass,
   and leaves timeout's group with setsid), why one pass cannot see it, the second pass + KILL sweep, the measured
   l1/l2 rows (0 survivors, seconds) and the stated limits (a child forked after the second pass; non-atomic /proc;
   no pidfd; a child that reparents before the second map).
2. A new section for {LANE}/corpus/knowledge/own-tree-pointer-binding.md titled "Bounding a population, not just a
   rule (r84)": the mutation-kill view of the population (five clause-blind mutants survived 36/36, are killed 5/5 by
   the 44-row population), why a true row on every real shape (a2w1/, assimilation/, a deep token) and a false row for
   every clause (digest, round, shape set, suffix depth, non-wave dir) is the criterion, and the limit that a
   population proves discrimination on its own rows, not the rule's correctness on the world. Cite S332/S331 and the
   new r84 sources the SOURCES seat lands.
3. Two QUALITY.md rows (append under `## Round 84 criteria`): one for "a population is judged by what its rows kill:
   every clause the rule enforces carries a false row and every real shape a true row" (evidence: the battery receipts
   and the r83 A2 route); one for "a signal-path repair names the descendant it could not see and the pass that now
   sees it" (evidence: the latefork stub bytes and the l1/l2 rows).
4. Deliver the three draft blocks as separate files plus your report.

# Acceptance
Every draft sentence is grounded in a committed path or a receipt you can cite; no sentence claims a verdict the
round has not measured. Do not edit the lane's corpus files (the L1 integrates).""")

item("S84ScoutDirs", "scout", f"""# Target
Reconnaissance of the lane's real directory shapes and the R7 fixture's relation to them. OWN ONLY your seat dir
{LANE}/.ufo/waves/round-84/w1/S84ScoutDirs/.

# Change
1. Census the lane's own-tree shapes at the lane base: `for d in {LANE}/.ufo/waves/round-*/*/; do ... uniq -c` (name
   the exact command you run) and the `census/round-<N>/` capture shapes. Compare with
   census/round-83/records/wave-dirs.txt (w1/ 65, w2/ 19, assimilation/ 4, records/ 3, w3/ 1, a2w1/ 1).
2. State whether every shape the r84 population uses as TRUE (w2/, w3/, a2w1/, assimilation/, the deep two-component
   suffix) exists in the lane's real tree, and whether every shape it REFUSES (records/ at the own-tree level, a real
   wN/ with the suffix dropped, another round's tree) exists too. Quote the counts.
3. Chase the r83 routed item "ground or delete the census-in-tree branch" (`census/round-84/c1-pointer-counter.py`,
   the `_capture_ok` calls in the census-tree branches): find a population row, a real ledger row or a real layout that
   makes the branch load-bearing; if none exists, say so with the commands that would show it and route it.
4. Deliver `dirs-receipt.txt` + your report.

# Acceptance
Every claim is a command output in your receipt; a shape named TRUE but absent from the real tree is a finding.
Read-only on the lane.""")

item("S84ScoutSources", "scout", f"""# Target
Open the sources the two claims' knowledge sections need, this round, with URL + access date + a located quote of
<=25 words each. OWN ONLY your seat dir {LANE}/.ufo/waves/round-84/w1/S84ScoutSources/.

# Change
1. Read {LANE}/corpus/SOURCES.md (shape + the id sequence) and {FLEET}/CORPUS.md section "SOURCES.md — where a
   shokunin learns" (the row contract). Do not invent an id: report the next free numbers from the registry and the
   collision check (`grep -oE '^ {{0,3}}\\|[[:space:]]*S[0-9]{{3,}}'`, 0-3 leading spaces).
2. Open at least two candidate sources for C2: `setsid(1)`/`setsid(2)` (the new session/process group semantics a
   late-forked child uses to leave timeout's group) and one of: `proc(5)` on `/proc/<pid>/stat` field semantics,
   `timeout(1)` on process-group creation, or the bash manual on traps vs foreground children. For C1 one candidate on
   mutation-style discrimination (e.g. a primary source on mutation testing / fault seeding) OR the lane's own
   `census/round-83/records/wave-dirs.txt` as an `own-work` provenance row.
3. For each: fetch it (curl to a scratch file), record HTTP status, byte count, sha256, the exact locator (man page
   line numbers or section), and a <=WORD_LIMIT-word quote you can defend as the sentence the entry will cite. State
   ADMIT or REJECT with the reason and a flip condition; a rejected row stays a row.
4. Deliver `sources-draft.tsv` (registry schema draft) + `sources-receipt.txt` + your report.

# Acceptance
Every draft row names a URL that answered this round and a located quote you transcribed from the fetched bytes; no
row is guessed. Never write to /home/vgpnk/Projects/shokuknow or any campaign tool.""")

item("S84Connector", "connector", f"""# Target
Cross-claim and sibling-overlap scan for round 84. OWN ONLY your seat dir
{LANE}/.ufo/waves/round-84/w1/S84Connector/.

# Change
1. **Separability:** prove or falsify that C1 (population/mutants/harness) and C2 (tool cli_kill_tree + population)
   share no file, counter, population, command or receipt; name every file each claim touches.
2. **Sibling overlap inside the lane:** `tools/souji-proc-census.sh` already parses /proc stat ppid/starttime
   (r83 connector §3.1). Does the r84 cli_kill_tree re-walk duplicate code the lane should single-source? Is
   `census/round-83/c2-tree-walk-counter.py`'s map-pass shape now duplicated in a third place? Report the exact lines.
3. **Wording table:** list every sentence in census/round-84/preregistration.txt that asserts something the
   instruments do not exercise (the r83 pattern: unrowed clauses, dead alternatives, shape lists wider than the
   population), with the row or mutant that would exercise it, and whether it exists.
4. Deliver `connector.md` with the three sections and a table of findings.

# Acceptance
Every finding names a path:line or a receipt; a separability claim names the two file sets. Read-only.""")

item("S84Reviewer", "reviewer", f"""# Target
Independent re-derivation of both claims on the committed bytes, plus chronology. OWN ONLY your seat dir
{LANE}/.ufo/waves/round-84/w1/S84Reviewer/.

# Change
1. Re-run the two frozen commands yourself (scratch under /fast/scratch/hyaku/souji-r84/S84Reviewer/):
   C1 after (`--only r84 --expect-killed 5`) with `census/round-84/c1-pointer-counter.py`, C1 before (`--only r83`),
   and C2 with the candidate tool if it exists at
   `.ufo/waves/round-84/w1/S84ExecC2/souji-vault-verify.sh` (otherwise the r83 tool, and say so).
2. Check the chronology and the scope of the round's commits: P must hold instruments/controls/receipts and F the
   preregistration ALONE (`git show --name-only <F>`); no after-arm receipt may predate F; every candidate byte's
   sha256 must equal the sha256 the receipts bind.
3. Attack the claims as statements: does `killed_r84=5` mean what the prereg sentence says (a mutant killed by ANY
   red row, including a harness error)? Is a "kill" fair when the mutant changes a branch the row exercises only
   indirectly? Is `mismatches=2` on l1/l2 reproducible, and is the survivor really the late setsid child?
4. Deliver `reviewer.md` with a numbered finding list, each with a reproducer, and an overall verdict per claim
   (verified / unverified / harmed).

# Acceptance
Every number you report is from a command you ran; every disagreement cites the receipt or the code line. Read-only
on the lane.""")

item("S84Critic", "critic", f"""# Target
Falsify the two claims' WORDING before the round files them. OWN ONLY your seat dir
{LANE}/.ufo/waves/round-84/w1/S84Critic/.

# Change
1. C1: the claim says the population is the instrument and its kill rate is its discriminating power. Attack three
   ways: (a) a cheaper population (fewer rows) that kills the same five mutants — build it in scratch and score it;
   (b) a mutant the 44-row population still does NOT kill (try: `len(want) < 2 or len(got) < 2` guard removal, the
   `_capture_ok` fallback removal, the basename test, the `target[:tr.start(0)] not in (...)` branch, the
   unknown-class refusal) — report survivors with the rows they evade; (c) whether an "accepted" row can ever be a
   digest-identical copy that is not a move (NF rows are byte-equal by design) — say what the population can and
   cannot prove.
2. C2: (a) is the freeze sound — a child forked in the read->STOP window, a CLI that forks from a path other than
   its signal trap (a timer loop), a third-generation fork, a child whose parent is killed before its own STOP; (b) can
   the late child instead be found by pid recorded in the first pass? (c) does the STOP->KILL pair widen the pid-reuse
   window (more reads before the signal)? Name the exact window.
3. Deliver `critic.md` with a verdict per claim and the exact amended sentence you would file.

# Acceptance
Each attack has a file and a command output; "no cheaper population" requires the rows you tried. Read-only.""")

item("S84MutCounter", "mutation-tester", f"""# Target
Extend the mutation evidence for the C1 instrument beyond the five frozen mutants. OWN ONLY your seat dir
{LANE}/.ufo/waves/round-84/w1/S84MutCounter/.

# Change
1. From census/round-84/c1-mutants.json take the five frozen mutants as the baseline (each must be killed on the
   44-row population, none on the 36-row one).
2. Write TEN more single-edit mutants of census/round-84/c1-pointer-counter.py in the same JSON shape (id/clause/
   old/new), each removing or widening one clause the claim's knowledge will state: the `len(want) < 2 or len(got) < 2`
   guard, the `_capture_ok` fallback call, the basename test, the `target[:tr.start(0)] not in (token_prefix,
   "census")` branch, the unknown-class refusal, the QUARANTINED declaration check, the LOCAL-POLICY disk check, the
   `not kr` refusal, the token-on-line check, the ledger-duplicate refusal. Apply each with your own driver (do not
   edit c1-mutants.json) and score it on both populations via
   `census/round-84/c1-false-row-harness.py --population <pin>`.
3. Report a table: mutant · clause · killed by r83 pop (yes/no) · killed by r84 pop (yes/no) · the row that kills it.
   Survivors are findings routed to r85 with the row shape that would catch them.
4. Deliver `mutcounter.md` + the mutant JSON + receipts.

# Acceptance
Each mutant applies exactly once; every cell is an observed run. Read-only on the lane.""")

item("S84MutTool", "mutation-tester", f"""# Target
Mutation-test the C2 repair: which of the candidate tool's new clauses does the frozen population actually kill?
OWN ONLY your seat dir {LANE}/.ufo/waves/round-84/w1/S84MutTool/.

# Change
1. Take the candidate tool (`{LANE}/.ufo/waves/round-84/w1/S84ExecC2/souji-vault-verify.sh` if present, else build the
   two-pass walk yourself from the r83 bytes into your seat dir).
2. Produce at least EIGHT single-edit mutants of `cli_kill_tree`/`cli_on_signal`, each removing or weakening one
   clause: the SIGSTOP before the signal (i.e. TERM first, the r83 order); the second map pass; the KILL sweep of a
   second-pass pid; the seen-pid de-duplication; the whole-file stat read (last-`)` strip); the starttime re-check on
   STOP; the starttime re-check on KILL; the `[ "$k" = "$pid" ] && continue` root guard; the group kill fallback. Score each with
   `census/round-84/c2-late-fork-counter.py --tool <mutant> --work ...`.
3. Report: mutant · clause · SUMMARY · which row killed it (or SURVIVED). A survivor is a finding: name the row that
   would catch it and whether it is cheap (no new stub) or needs one.
4. Deliver `muttool.md` + the mutant files + receipts.

# Acceptance
The pristine candidate is green (else INVALID) and every mutant is scored on the same 22 rows. Read-only on the lane.""")

item("S84Sentinel", "sentinel", f"""# Target
Adversarial security review of the two claims' surfaces: can the C2 repair be made to signal a process it should not,
and can the C1 population be made to certify a rule that resolves a wrong file? OWN ONLY your seat dir
{LANE}/.ufo/waves/round-84/w1/S84Sentinel/.

# Change
1. **C2 kill scope.** Build fixtures where a pid is reused or a foreign process is a near-neighbour: a canary process
   you own whose pid you churn (fork/exit loops) while the tool walks; the CLI spawning a child that is NOT a
   descendant (a pre-existing canary pid passed as an argument); a child that reparents to init mid-walk; a CLI whose
   comm holds a newline and `)`; a child that setsids after the first pass. For each: does the tool signal anything
   outside its own descendant set? Record evidence (a canary that logs signals it receives, e.g.
   `trap 'echo hit >> canary.log' TERM`).
2. **Private file and env.** Confirm the private CLI file is 0600 and removed on the signal path with the new second
   pass; try SOUJI_*/TMPDIR spoofing through the environment the tool inherits.
3. **C1 certification.** Take a false row (NF-L, NF-L2, NF-M, NF-Q) and ask: what would the counter have to believe to
   accept it, and is there a row shape under which the population would certify a WRONG resolution while the battery
   stays green? Name at most three such shapes with a reproducer if cheap.
4. Deliver `sentinel.md` with findings graded CRITICAL/HIGH/MEDIUM/LOW and the exact reproducers.

# Acceptance
Every finding has a command and an observed output; a signal to a non-descendant is CRITICAL. Never signal a process
outside your own fixtures; never touch lane tracked files.""")


def main():
    spec = {
        "wave": "souji-r84-w1",
        "milestone": ("souji r84: C1 the false-row population binds five pointer-counter clauses (calibration), "
                      "C2 the vault CLI signal path freezes the tree before terminating it (operability)"),
        "reportDir": ".ufo/waves/round-84/w1",
        "context": CTX,
        "items": ITEMS,
    }
    json.dump(spec, sys.stdout, indent=1, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
