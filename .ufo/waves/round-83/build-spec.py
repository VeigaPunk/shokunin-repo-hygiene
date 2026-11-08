#!/usr/bin/env python3
"""Build the souji r83 wave-1 spec. Run: python3 .ufo/waves/round-83/build-spec.py > w1-spec.json
P and F hashes are read from the lane's git branch (P = the commit before F)."""
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


p_hash = find("round-83: instruments")
f_hash = find("round-83: preregistration")

CTX = f"""# Goal
souji round 83 (lane repo {LANE}, lane id souji). The L1 (SoujiR83) holds the planner seat and is the ONLY
integration owner: it freezes the claims, integrates your findings, commits through the lane helper, measures and
writes the report. You are one seat of ONE v1 wave of 12 seats. Seats deliver files and findings only: never commit,
never push, never mutate git/jj state, never edit fleet or sibling-lane files, never edit MANIFEST.json,
.ufo/state/*, .scratch/* or .ufo/watchdog.log. A finding with a reproducer beats an opinion.

# Evidence durability
FIRST action: create your report file (the `Report:` trailer path) with a one-line skeleton and append to it as you
go. Your final yield must repeat the same content. A seat that ends without that file counts as no verdict.
Every `Report:` trailer path is relative to {LANE} \u2014 write it at {LANE}/<that path>.

# Frozen round (read {LANE}/census/round-83/preregistration.txt FIRST \u2014 it is the contract)
Lane base: {base} (r82 closed admitted). P {p_hash}: instruments + controls. F {f_hash}: preregistration alone.
C1 (calibration 7): on the frozen 36-row population census/round-83/c1-false-rows.tsv, the candidate
census/round-83/c1-pointer-counter.py binds a MOVED token's own-round-tree target only when the target's path below
its round-<N> is a real wave directory (w1/, w2/, w3/, w5... = w[0-9]+/, a2w1/, assimilation/, plus the r82 shapes
waves/, wave/, records/wave-<w>/) followed by the token's remaining path below its own wave directory (full suffix).
It must keep TF6 (w2/) and TF7 (w1/), keep TF1-TF5 and PF-1, refuse NF-J (duplicated middle dir under w1/), NF-K
(flattened round-tree root), NF-F/NF-G/NF-H/NF-I; SUMMARY rows=36 mismatches=0 accepted=0 refused_true=0 errors=0,
EXIT=0. K-a = census/round-82/c1-pointer-counter.py unchanged -> census/round-83/controls/c1-K-a-r82-counter.txt
(mismatches=2, TF6/TF7 refused), EXIT=1.
C2 (operability 8): in tools/souji-vault-verify.sh, cli_kill_tree builds the CLI descendant map from ONE fork-free
pass over /proc/<pid>/stat (field 4 ppid, read after the last `)` of comm) and signals each descendant as it is
discovered (TERM, then the KILL sweep), re-reading starttime (field 22) before each signal; the frozen 20-row
population census/round-83/c2-population.tsv (r82 16 rows + d12-term-pid, d12-term-group, d24-term-pid,
d24-monitor-group) reports SUMMARY rows=20 mismatches=0 errors=0 orphans=0, EXIT=0. K-a =
census/round-83/controls/c2-K-a-r82-tool.sh (byte-identical to the r82 tool, sha256 dd6d440e...) ->
census/round-83/controls/c2-K-a-r82-tool.txt (mismatches=4 on the four deep rows), EXIT=1. Zero pgrep invocations per
walk, counted by a PATH shim (the r82 tool makes one per tree node).

# Frozen commands
C1: python3 -B census/round-83/c1-false-row-harness.py --counter <candidate> --lane {LANE} --fleet-root {FLEET} --work <empty dir outside /tmp>
C2: python3 -B census/round-83/c2-tree-walk-counter.py --tool <candidate> --work <empty dir outside /tmp>
The population sha256 is pinned by the counter/harness; editing a population row kills the claim.

# Scratch and safety (binding)
- Scratch root: /fast/scratch/hyaku/souji-r83/<YourSeatName>/ ; create it with mkdir -p, pass it explicitly, never
  rely on TMPDIR, never write under /tmp (files <50 MB only if unavoidable). Remove your scratch before you yield:
  copy receipts into {LANE}/.ufo/waves/round-83/w1/ first (`trap 'rm -rf -- \"$S\"' EXIT`).
- Any git fixture: D=$(mktemp -d /fast/scratch/hyaku/souji-r83/<Name>/fx.XXXXXX) && git -C "$D" init -q; verify
  `git -C "$D" rev-parse --show-toplevel` equals $D before any mutating git call. Never run git/jj in the lane
  except read-only (log/show/diff/status/rev-parse/merge-base/cat-file).
- Tooling authorization (operator, 2026-10-19): you may install or upgrade tools that help the task \u2014 read
  /home/vgpnk/.omp/agent/RULES.md first (official channels; record tool/version/channel/reason in your report).
  pacman transactions are PAUSED host-wide: install via `uv tool`/`npx`/an official binary in ~/.local/bin only, and
  never run pacman -S/-Sy/-Syu/-U/-R. Never mutate host sysctls (r82 incident: a seat set user.max_user_namespaces=0).
- Never message agent://all or another lane's seats; coordinate only through your report and, if needed, the L1.
- Read-only on lane tracked files unless your item says otherwise; candidate bytes go under your seat directory
  `{LANE}/.ufo/waves/round-83/w1/<YourSeatName>/` and the L1 integrates them.
- No subagent dispatch (you are a leaf; an executor may spawn one read-only labrat probe only).
"""

ITEMS = []


def item(name, role, body):
    ITEMS.append({"name": name, "role": role, "prompt": GOD + body})


item("S83ExecC1", "executor", f"""# Target
Build the C1 candidate counter and score it against the frozen population. OWN ONLY your seat directory
{LANE}/.ufo/waves/round-83/w1/S83ExecC1/ (create it) plus your report.

# Change
1. Start from {LANE}/census/round-82/c1-pointer-counter.py (the r82 rule; frozen and never edited). Write the
   candidate to .ufo/waves/round-83/w1/S83ExecC1/c1-pointer-counter.py: keep every r82 branch and add the own-tree
   binding the prereg freezes \u2014 the target's path below its round-<N> must be one of the real wave shapes
   (w[0-9]+/, a2w1/, assimilation/, waves/, wave/, records/wave-<w>/) followed by the token's remaining path below ITS
   own wave directory (the token's first component below its round-<N>), compared component-wise (full suffix, in
   order); tt == tk stays as it is. Do not touch `CAPTURE` (the census-tree rule); the own-tree shapes go in their
   own regex/helper. Keep the digest, round, basename and census-tree branches identical.
2. Score it: `python3 -B census/round-83/c1-false-row-harness.py --counter .ufo/waves/round-83/w1/S83ExecC1/c1-pointer-counter.py
   --lane {LANE} --fleet-root {FLEET} --work /fast/scratch/hyaku/souji-r83/S83ExecC1/c1` (empty dir). Record the
   `SUMMARY` line and every ROW match=no. Target rows=36 mismatches=0 accepted=0 refused_true=0 errors=0, EXIT 0.
3. Run the five regressions with the candidate: r81 harness (census/round-81/c1-false-row-harness.py), r80
   (census/round-80/... harness), r79 harness, r78 and r77 harnesses \u2014 the exact commands are in the r82 lesson
   `## Measured`. Any regression that is red is a finding.
4. Deliver: the candidate file, a `c1-candidate-receipt.txt` with the raw command outputs, and your report with the
   diff against the r82 counter (`diff -u`), the exact rule sentence the code enforces, and the SUMMARY/mismatch lines.

# Acceptance
The candidate file exists, `bash`-level syntax is irrelevant (Python: `python3 -c 'import ast;ast.parse(open(f).read())'`
licenses it), the frozen command prints the target SUMMARY and exits 0 from {LANE}, and the report names each ROW that
diverges, if any. Do not edit census/round-83/c1-false-rows.tsv, the harness, the preregistration or the controls.""")

item("S83ExecC2", "executor", f"""# Target
Build the C2 candidate tool and score it against the frozen population. OWN ONLY your seat directory
{LANE}/.ufo/waves/round-83/w1/S83ExecC2/ (create it) plus your report.

# Change
1. Copy {LANE}/tools/souji-vault-verify.sh (sha256 dd6d440eaf205570d5e23d5ef3ad614e34c281667075f9bf5f519ddb75855e1a)
   to your seat dir as `souji-vault-verify.sh` and rewrite ONLY `cli_kill_tree` (+ its comment block):
   - one fork-free pass over `/proc/[0-9]*/stat`: read each stat line with the `read` builtin, take the substring
     after the LAST `)` of the comm field (comm may contain spaces and parens), field 2 of that remainder is ppid
     and field 20 is starttime; build `ppid[pid]` and `start[pid]` in assoc arrays. No `pgrep`, no fork, no
     external command inside the pass (bash builtins only; the pass must not need `cat`/`awk`/`sed` per pid).
   - DFS from the root pid over the ppid map, killing each descendant AS IT IS DISCOVERED (`kill -TERM`), and
     re-read that pid's current starttime before the signal; skip (do not signal) a pid whose starttime changed.
   - after the DFS, the same short sleep and `kill -KILL` sweep over the pids whose starttime still matches; never
     signal the root pid itself; keep the caller's group kill fallback in `cli_on_signal` unchanged.
   - keep `bash -n` clean; the tool's own `selftest` must stay green.
2. Score: `python3 -B census/round-83/c2-tree-walk-counter.py --tool .ufo/waves/round-83/w1/S83ExecC2/souji-vault-verify.sh
   --work /fast/scratch/hyaku/souji-r83/S83ExecC2/c2` (empty). Target rows=20 mismatches=0 errors=0 orphans=0, EXIT 0.
   If a deep row still exceeds SETTLE, report WHICH and the seconds; do not weaken the counter.
3. Regressions on your candidate bytes: `bash <candidate> --selftest`, `bash tests/fixtures/r17-jj-receipts.sh --tool-dir <dir>`
   (tools/ copy path; see the r82 lesson for the exact invocation), and
   `python3 -B census/round-81/probes/tmpdir-in-vault.py --tool <candidate> --work <empty>`.
4. Deliver: candidate file, `c2-candidate-receipt.txt`, the `diff -u` of cli_kill_tree against the r82 tool, the pgrep
   count per walk (PATH shim that logs invocations; the counter already does this if present, otherwise your own
   shim), and your report.

# Acceptance
The frozen C2 command prints the target SUMMARY and exits 0; the selftest/r17/probe D are green on the candidate
bytes; the diff touches only cli_kill_tree and its comment; no new external command is called per tree node.
Do not edit tools/souji-vault-verify.sh in the lane (the L1 integrates), the population, the counter or the controls.""")

item("S83ExecEvade", "executor", f"""# Target
Try to make the C2 candidate leave a process behind, lose or change a verdict, exit wrongly, or leak its private
file. Read-only on the lane; all work in your scratch. OWN ONLY your seat dir {LANE}/.ufo/waves/round-83/w1/S83ExecEvade/.

# Change
1. Use the candidate `{LANE}/.ufo/waves/round-83/w1/S83ExecC2/souji-vault-verify.sh` if it exists when you start;
   otherwise the frozen r82 tool `{LANE}/tools/souji-vault-verify.sh`. Copy it into your scratch (never run the lane
   file in place if your probe writes).
2. Build your own fixtures from the counter's shape (`census/round-83/c2-tree-walk-counter.py` build/run_row) or your
   own: a CLI stub with (a) a 24-child fan-out, (b) a 3-deep chain, (c) children that setpgid themselves, (d) a comm
   containing `) (` so the stat parse can be fooled, (e) a child that exits and a pid reused between read and signal
   (document how you detect reuse without racing the host), (f) a fast `sleep`-and-exit CLI, (g) a CLI that ignores
   TERM. Signal the tool by pid and by group, with and without `SHELLOPTS=monitor`.
3. Report per shape: exited within 5 s? rc? `SIG` line on stderr? survivors (nonce method)? private TMPDIR empty?
   Any wrong verdict on a no-signal row? Any signal sent to a pid that is not a descendant (make it observable: a
   canary process whose pid you churn near the CLI's pids; do not signal unrelated host processes).
4. Deliver `evade-receipt.txt` + your report with the exact stub bytes and commands.

# Acceptance
Each shape has an observed result and a reproducer path; a survival or wrong verdict is a finding with the bytes
that produced it. Never signal a process outside your own fixtures; never touch the lane's tracked files.""")

item("S83Scribe", "scribe", f"""# Target
Drafts for the L1 to integrate (drafts only, under your seat dir {LANE}/.ufo/waves/round-83/w1/S83Scribe/).

# Change
1. A new section (<=25 lines) for {LANE}/corpus/knowledge/gate-signal-handling.md titled
   "A one-pass descendant walk for the vault CLI's signal path (r83)" describing: the per-node `pgrep -P` cost
   (F-2: one full /proc scan per node, 0.53-2.15 s per call, >=12 descendants exceeds the 5 s settle), the
   snapshot->KILL gap (F-3, up to 6.11 s), the one-pass ppid map with the comm-paren parse and the starttime
   re-check, the measured N=12/N=24 results, and the stated limits (non-atomic /proc, no pidfd, setsid escape).
   Cite S332 (kernel fs/proc/array.c) and S075/S326 where they apply.
2. A new section for {LANE}/corpus/knowledge/pointer-resolution-binding.md (or the r82 entry it supersedes \u2014 find
   the entry that carries the own-tree rule) titled "Own-tree wave shapes and the full suffix (r83)": the real
   directory census (census/round-83/records/wave-dirs.txt: w1/ 65, w2/ 19, assimilation/ 4, w3/ 1, a2w1/ 1,
   records/ 3), why `decoy/`, the round-tree root and duplicated middle dirs are not captures, the full-suffix
   comparison, and the stated limit (records/ is refused). Cite S331.
3. Two QUALITY.md rows (Q-next): one for "a binding rule names the real directory shapes before it names a shape
   (list the lane's actual directories, not a plausible fixture)" citing lesson round-82 M5/Q151 and this round's
   evidence; one for "a signal-path claim states the descendant count and the settle it was measured under" citing
   round-82 A8/F-2/F-3 and this round's receipts. Include the superseded-row line where they extend an existing row.
4. SOURCES.md: draft the three rows (S330 rejected pgrep(1); S331 own-work wave-directory census; S332 kernel
   fs/proc/array.c at a tag) in the 11-column shape with no `|` inside cells, status/opened/recheck/used-by, in a
   scratch file; do not append to the registry yourself.
5. Deliver all drafts as files under your seat dir + your report listing which accepted r82 routed defect each
   draft answers.

# Acceptance
Drafts are inside 25 lines per section, every count carries its command, every source row is 11 columns, and the
QUALITY rows name the row they extend/supersede. Scribe drafts only: the L1 applies accepted ones.""")

item("S83ScoutDirs", "scout", f"""# Target
Own-tree shape and binding reconnaissance, read-only on the lane.

# Change
1. Re-derive census/round-83/records/wave-dirs.txt yourself from {LANE} (command in the file header) and state any
   difference. Which of those directory names are capture locations for a moved artifact, and which are not (read
   the tree: what is inside .ufo/waves/round-*/records/, residual/, transcripts/, recovery/, l1/, final/, build/,
   attempt2/)?
2. The P04 token `.ufo/waves/round-32/a2w1/SwarmExecutor08.md`: find its history (`git log --all --format='%H %s' -- <path>`,
   `git log --all --diff-filter=R --summary`), its frozen bytes (sha256 d0693448...), and the row in
   census/round-77/c2-population.tsv/ledger that binds it. Is a real own-tree move `.ufo/waves/round-XX/a2w1/X ->
   .ufo/waves/round-XX/wN/X` something the lane actually did? Give the observed instances (paths + commit) or the
   sweep that found none.
3. Enumerate the shapes the candidate rule accepts that the lane never uses (any `w[0-9]+/`, `assimilation/`) and
   whether that can bind a false ledger row in practice (a target must exist at the rev with the frozen bytes).
4. Report: the census, the P04 history, real move instances or the sweep, and the accepted-but-unused shapes.

# Acceptance
Every claim carries a command and its output; a negative carries its sweep. Read-only: no writes outside your seat
dir and report.""")

item("S83ScoutSources", "scout", f"""# Target
Open the round's sources and test the sentences the claims rest on. Read-only on the lane.

# Change
1. S332 candidate: the kernel's own procfs writer, `fs/proc/array.c` at a tag (a copy was fetched this round to
   /fast/scratch/hyaku/souji-r83/l1/array.c from
   https://raw.githubusercontent.com/torvalds/linux/v6.17/fs/proc/array.c; if absent, fetch it again). Locate
   do_task_stat()'s field order: ppid and the starttime/start_boottime fields, and the `comm` emission
   (seq_put_decimal_ull with the parentheses). Quote <=25 words with line numbers; does it ground "field 4 is ppid
   after the last `)` and field 22 is starttime in ticks"? Is `array.c` a different source from S075's man page
   (proc_pid_stat(5)) or the same ground? Give the duplicate-URL/scope verdict.
2. S330 candidate: procps-ng pgrep(1), the `-P`/`--parent` paragraph (local man page /usr/share/man/man1/pgrep.1.gz,
   owner procps-ng). Quote <=25 words with location. r82 rejected it (S075 governs process identity); decide whether
   the row should exist as `rejected` with that reason and flip.
3. S331 candidate: the lane's own wave-directory census (census/round-83/records/wave-dirs.txt at the P commit).
   Is an `own-work` row admissible (CORPUS rule 1: opened this round, quote = the command and its output at a named
   revision)? What exactly would it ground that S075/S327 do not?
4. Report: per candidate — admit/reject, tier, scope, anchor, quote, and the row cell text you would write (11
   columns, no `|`).

# Acceptance
Every verdict names the opened file/page and a located quote; a rejection names the reason and flip condition. Never
write the registry or any lane file.""")

item("S83Reviewer", "reviewer", f"""# Target
Review the round's chronology, frozen predicates and digest binding. Read-only.

# Change
1. Chronology: lane base {base}; P {p_hash} (instruments + controls) must be a strict ancestor of F {f_hash}
   (preregistration alone); F a strict ancestor of any candidate commit. Check `git log --format='%H %at %s' -6`,
   `git merge-base --is-ancestor`, and that F touched ONLY census/round-83/preregistration.txt
   (`git show --name-only --format=`) while P did not contain it. Run the lane's freeze-check if it accepts a
   `--round 83` mode (see tools/souji-freeze-check.py --help) and report what it says; do not edit the prereg.
2. Controls: census/round-83/controls/c1-K-a-r82-counter.txt and c2-K-a-r82-tool.txt — are they red for the right
   reason (C1: TF6/TF7 refused; C2: 4 deep rows and their survivor counts)? Is c2-K-a-r82-tool.sh byte-identical to
   the r82 tool (`sha256sum`)? Are both controls committed in P (`git cat-file -e P:<path>`)?
3. Predicates: re-read census/round-83/preregistration.txt against the harness/counter code. Is each frozen sentence
   the same sentence the counter enforces (rows=36/20, accepted/refused_true/orphans, the SETTLE, the pgrep count)?
   Name every place the wording is WIDER than the instrument (Amendment 59).
4. Candidate bytes (when they exist): digest them, check the diff against the r82 counter/tool touches only the
   claimed rule, and re-run the two frozen commands yourself from {LANE}.
5. Report: chronology verdict, control verdict, predicate/wording table (sentence -> enforced property -> verdict),
   and each narrower-than-wording finding with the artifact.

# Acceptance
Every check is an executed command with its output; a wording overreach is a finding with the exact sentence and the
code line that does not enforce it.""")

item("S83CriticClaims", "critic", f"""# Target
Attack the two frozen claims as claims. Read-only.

# Change
1. C1: is this calibration (the lane's self-assessment vs the real directory layout) or quality on a rule the lane
   already holds? Does the do-nothing control K-a fail for the right reason, or could a cheaper rule meet the target
   (e.g. accept ANY `.ufo/waves/round-<N>/<one-component>/<basename>`)? Test that cheaper rule on the 36 rows and
   show which rows kill it. Is TF7 (w1/) a real shape the lane has (census/round-83/records/wave-dirs.txt) or a
   fixture-only shape? Is NF-J/NF-K's refusal load-bearing or decorative?
2. C2: does the counter measure the tool or the host (pgrep cost scales with host process count)? Is the 5 s SETTLE
   frozen before the candidate? Does the candidate's starttime re-check actually add anything measurable, or would a
   plain kill-as-discovered pass the same rows? Propose the row that would distinguish them and say whether the frozen
   population has it.
3. Both: is the claim's target one a do-nothing control cannot reach? Is the axis named by the surface the round
   changes (calibration: the ledger rule vs the real dirs; operability: the signal path's settle)?
4. Report: per claim, the strongest surviving attack with a reproducer, and the wording that should be narrowed.

# Acceptance
Every attack is run against committed bytes and names the row/code line; "no attack survived" is stated only after
the cheapest alternative rule/mutant was tested.""")

item("S83MutCounter", "mutation-tester", f"""# Target
Mutation-test the C1 candidate rule against the frozen 36-row harness; hunt new false rows. Work in your scratch,
OWN ONLY your seat dir {LANE}/.ufo/waves/round-83/w1/S83MutCounter/.

# Change
1. Copy the candidate `{LANE}/.ufo/waves/round-83/w1/S83ExecC1/c1-pointer-counter.py` (or the r82 counter if the
   candidate is absent) into your scratch. Mutants, one at a time, each scored with the frozen command:
   m1 the own-tree shapes list minus `w[0-9]+/`; m2 shapes only, no remaining-path comparison (accept any
   `<shape>/<basename>`); m3 remaining path compared by basename only; m4 the own-tree branch dropped; m5 the
   identity `tt == tk` clause dropped; m6 starttime/`frozen` digest check dropped; m7 the round-number equality
   dropped; m8 the shapes list widened to `records/`. For each: which ROW lines go red (the killer rows)? A mutant
   that survives all 36 rows and the regressions is a missing row \u2014 name the row that should exist.
2. Hunt new false rows: a target in a real shape whose bytes differ (`digest differs`), a target in a real shape
   with a duplicated leading component, a target that is a directory, a token whose first component is not a wave
   dir. Show whether the candidate accepts any (a false-green).
3. Regressions: run the r81 and r77 harnesses with the candidate and with each survivor mutant; a survivor that also
   survives a regression is a real gap.
4. Deliver `mutants.txt` (mutant -> rows red) + your report.

# Acceptance
Every mutant is run, not reasoned about; survivors name the missing row; the frozen population/controls are not
edited.""")

item("S83MutTool", "mutation-tester", f"""# Target
Mutation-test the C2 candidate tool against the frozen 20-row counter; hunt missing rows. OWN ONLY your seat dir
{LANE}/.ufo/waves/round-83/w1/S83MutTool/.

# Change
1. Copy the candidate `{LANE}/.ufo/waves/round-83/w1/S83ExecC2/souji-vault-verify.sh` (or the r82 tool if absent) into
   your scratch. Mutants of `cli_kill_tree`, one at a time, each scored with the frozen C2 command:
   m1 no starttime re-check (signal whatever pid the map names); m2 no TERM, only the KILL sweep; m3 the tree walk
   dropped (group kill only); m4 one `pgrep -P` per node reinstated (the r82 mechanism) with the new kill order;
   m5 the KILL sweep dropped (TERM only); m6 the DFS visits children but signals nothing (collect only); m7 the
   ppid map built from `ps` instead of /proc; m8 the private file removed before the tree kill. For each: the ROW
   lines that go red and the rows that should exist.
2. Measure the pgrep invocation count per walk for the r82 tool and the candidate (PATH shim), and the signal->exit
   seconds per deep row from the counter's ROW lines.
3. A mutant that survives all 20 rows is a missing row \u2014 name it, with the stub shape that would kill it, and say
   whether the frozen population can be extended next round (this round's population is frozen).
4. Deliver `mutants.txt` + your report.

# Acceptance
Every mutant is run against committed bytes; the counters and the lane tool are never edited in place.""")

item("S83Sentinel", "sentinel", f"""# Target
Security and safety review of the C2 candidate `cli_kill_tree`. Read-only on the lane; work in your scratch.

# Change
1. The pid it starts from: can the new walk signal a process that is NOT a descendant (pid reuse between the stat
   pass and the signal; the CLI_PID window before `CLI_PID=$!`; a zombie's ppid; a pid reparented to init)? Does the
   starttime re-check close it, and what is the residual window in syscalls? Measure the window on the real tool and
   say how you measured it.
2. The /proc parse: comm can contain `)` and spaces; the pass takes the substring after the LAST `)`. Build a
   fixture with a comm containing `) ( ` and a spoofed-looking stat line; does the pass mis-attribute a ppid or a
   starttime? What if /proc/<pid>/stat is unreadable (permission, race)?
3. The kill order: TERM-as-discovered then a KILL sweep over matching starttimes \u2014 can a descendant escape between
   the two (fork after discovery)? Can the tool signal its own pid, the timeout pid, or the caller? Compare with the
   r82 behaviour and with the caller's group kill fallback.
4. The private file: at what point is it removed relative to the walk, and for how long after the signal can it
   exist? Is it still 0600 under a private TMPDIR, and does the `setpgid`/setsid escape still hold?
5. Report every finding with severity, the fixture bytes, the command and the observation; state the smallest fix
   for each MEDIUM+.

# Acceptance
Every finding is reproduced on the candidate bytes (or on the r82 bytes if the candidate is absent); no host
process outside your fixtures is signalled; the lane is not edited.""")

item("S83Connector", "connector", f"""# Target
Cross-claim separation, sibling-overlap scan and wording cross-check. Read-only.

# Change
1. Separation: from the receipts and commits, is C1 verifiable without C2 and C2 without C1 (different files,
   different counters, different commands)? Name any shared byte or command that makes them one claim.
2. Sibling overlap: does another lane's tool or this lane's other tools already implement a /proc ppid walk or an
   own-tree binding rule (search {FLEET}/*-shokunin/tools and souji's tools for `ppid`, `pgrep -P`, `_owntree_ok`,
   `wave-`)? Report the pattern (path:line) without judging the sibling's scope.
3. Wording: compare the preregistration's C1/C2 sentences with what the candidate code and counters enforce; list
   every clause that names a property no row/counter checks (Amendment 59 class), and every place SKILL.md/SCORECARD
   already claims the old r82 behaviour (which the L1 must update).
4. The two claims' stated limits: is each limit actually disclosed in the prereg (records/ refusal, non-atomic
   /proc, setsid, flat deep stub)?
5. Report: separation verdict, sibling rows with paths, the wording table, and the SKILL/SCORECARD pointers to update.

# Acceptance
Every overlap is a path:line with its bytes; the wording table quotes the sentence it attacks; no lane file is
edited.""")

spec = {
    "wave": "souji-r83-w1",
    "milestone": "souji r83: C1 own-tree real wave shapes + full suffix (calibration), C2 one-pass fork-free descendant walk (operability)",
    "reportDir": ".ufo/waves/round-83/w1",
    "context": CTX,
    "items": ITEMS,
}
json.dump(spec, sys.stdout, indent=1, ensure_ascii=False)
print()
