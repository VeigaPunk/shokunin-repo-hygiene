#!/usr/bin/env python3
"""make-spec.py — souji round-66 wave spec: ONE v1 wave, 10 seats (band 8-16), post-freeze.

Run: python3 make-spec.py   (writes w1-spec.json beside this file)
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SCR = "/fast/scratch/hyaku/souji-r66"
WD = f"{LANE}/.ufo/waves/round-66/w1"
CAND = f"{WD}/S66ExecWriter/candidate/souji-receipt-write.py"
CAND_READY = f"{WD}/S66ExecWriter/CANDIDATE-READY"
FREEZE = "02cc660965e027c6c6390604e50702bb06377b2e"
BASE = "045e103478fa4a7eff77db2cab5b9e2f26959a0a"
INSTR = "4576f101a9200206de00ef00923dd38a7b2dbc7d"
CTRL = "4864c01f112c9f423def430d9b6e01bdc0e21f36"

GODSPEED = """/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.
"""

CONTEXT = f"""# Goal
souji round 66 (lane repo {LANE}). L1 = SoujiR66; it holds the planner seat (the validator refuses a planner role) and is the
ONLY integration owner: it copies candidate bytes into tools/, lands commits through the helper and writes the report. You are one
seat of ONE post-freeze v1 wave of 10 seats. Seats deliver files and findings only.

# Frozen chronology (binding; read census/round-66/preregistration-attempt2.txt first)
Base {BASE} (lane master at round start; carries the round-65 landed writer tools/souji-receipt-write.py and round-65 SKILL.md).
Instruments commit {INSTR} (census/round-66/c1-counter.py, c1-matrix.tsv 28 rows, c2-counter.py, c2-statements.tsv,
c2-mutate.py). Do-nothing control receipts commit {CTRL}. FREEZE (attempt 2, operative prereg) commit {FREEZE}.
The attempt-1 file census/round-66/preregistration.txt is SUPERSEDED. Do not amend any frozen file; a predicate change after
data is not this round's rule.
Claims (frozen): C1 operability — the writer refuses caller-injected config and object-redirect env routes (E1-E6), records full
permission bits (MOD2/MOD3), refuses same-content symlink retarget (SY3), on the frozen 28-row matrix; target
`SUMMARY matrix=28 base_forgeries=8 base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS` EXIT=0.
C2 calibration (lowest owned axis, 7) — SKILL.md statements agree with writer bytes (population s1-s5); the round-66 counter
kills the M-ENV mutant that the round-65 counter scores as live (round-65 M10).
Named limits (frozen; do not count as passes): ignore routes (.git/info/exclude, tracked .gitignore, repo-local core.excludesFile)
stay outside C1; lexical C2 read; one M-ENV mutant only.

# Candidate writer (the one writer of this round)
S66ExecWriter (executor) builds the candidate writer in a scratch clone and delivers the bytes. Its completion marker is
{CAND_READY}. Seats S66MutKill, S66ReviewerDesign and S66SentinelScope wait for that marker (bounded loop: `sleep 60`, at most 45
iterations) before their candidate-dependent checks, and run their non-candidate checks first.

# Hard rules for every seat
- Write scope: ONLY your own wave dir and your scratch dir. Never edit tools/, census/, corpus/, SCORECARD.md, LOG.md, SKILL.md,
  MANIFEST.json, shokunin.conf, templates/, scripts/, .ufo/state/, .ufo/watchdog.log, .scratch/ or any sibling repo.
- Never run git/jj mutating commands (commit, add, stash, checkout, reset, pull, push, fetch, rebase, bookmark, new, describe) in the
  lane or anywhere except a scratch clone you created yourself, and in a scratch clone only with explicit `-C "$D"` and an explicit
  identity via `-c user.name=S66Seat -c user.email=s66seat@example.invalid`. Never push. Read-only git is fine.
- Scratch: every clone, work tree, fixture and counter --work dir lives under {SCR}/<your seat name>/ (mkdir -p). Pass --work
  explicitly. Use trap 'rm -rf -- "$S"' EXIT. Never use /tmp for anything over 50 MB; never rely on an inherited TMPDIR.
- Never change a host sysctl (no `sysctl -w`, no `echo ... > /proc/sys/...`, no `sudo` for system state). A prior wave seat
  set user.max_user_namespaces to 0; that broke every bwrap sandbox. Name the need in your report instead.
- Seat paths are absolute. Every `Report:` trailer path is relative to {LANE} — write it at {LANE}/<that path>.
- Tooling authorization (operator, 2026-10-19): you may install or upgrade tools that help the task; first read
  /home/vgpnk/.omp/agent/RULES.md (official channels, update-safety gate); record tool/version/channel/reason in your report.
  pacman transactions are PAUSED host-wide: install only via `uv tool`, `npx`, or an official binary in ~/.local/bin, otherwise file
  an L0 question. Never `pacman -Sy`, `-Syu`, `-U`, `-R`.
- Every task must skip build/lint/test/formatter runs that the L1 owns UNLESS your item below says to run them.
- Return a terminal result: a short findings summary with file paths and every numeric result you measured. No filler.
"""

ITEMS = []


def item(name: str, role: str, body: str) -> None:
    ITEMS.append((name, role, body))


item("S66ExecWriter", "executor", f"""# Target
Build the round-66 candidate receipt writer. Deliver ONLY under {WD}/S66ExecWriter/:
  candidate/souji-receipt-write.py   (the candidate bytes)
  candidate/SHA256SUMS               (sha256 of that file)
  candidate/c1-run.txt               (stdout of the frozen C1 counter run at your scratch commit, below)
  candidate/selftest.txt             (stdout of `python3 -B souji-receipt-write.py --selftest --work DIR` on the candidate)
  candidate/notes.md                 (what changed, by line, and why; every refusal class and where it is raised)
Then write {CAND_READY} as the LAST file, containing the sha256 of the candidate.

# Work
Scratch: {SCR}/S66ExecWriter/. Create a clone: `git clone --shared -q {LANE} {SCR}/S66ExecWriter/clone` then
`git -C {SCR}/S66ExecWriter/clone checkout -q {BASE}` (detached is fine). Start from the BASE bytes of tools/souji-receipt-write.py.
Apply the changes below to the clone's tools/souji-receipt-write.py, commit IN THE CLONE with
`git -C "$C" -c user.name=S66Seat -c user.email=s66seat@example.invalid commit -q -am "candidate"`, and measure:
  python3 -B {LANE}/census/round-66/c1-counter.py --root "$C" --matrix {LANE}/census/round-66/c1-matrix.tsv \\
     --base-rev {BASE} --rev <that commit> --tool tools/souji-receipt-write.py --work {SCR}/S66ExecWriter/work
Its last lines must read `SUMMARY matrix=28 base_forgeries=8 base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0
regress=PASS` and `EXIT=0`. Iterate in the clone until they do, WITHOUT touching the frozen counter or matrix (census/round-66/ is
read-only to you). Copy the final bytes to candidate/souji-receipt-write.py.

# Required changes to tools/souji-receipt-write.py (exact)
1. Env gate, placed in write_receipt() directly BEFORE the existing GIT_INDEX_FILE gate and before any git call:
   - if any of GIT_CONFIG_COUNT, GIT_CONFIG_PARAMETERS, or any name starting with GIT_CONFIG_KEY_ / GIT_CONFIG_VALUE_ is in
     os.environ: refuse(f"RECEIPT-ENV-CONFIG-SET: {{names}} set in the writer's environment; unset them and retry") where names is
     the sorted list of the NAMES only (never values).
   - if any of GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_REPLACE_REF_BASE is in os.environ: refuse with class
     RECEIPT-ENV-REDIRECT-SET, names only.
   Both are PRESENCE checks (an empty value still refuses).
2. GIT_INDEX_FILE gate: keep the block SHAPE exactly: line 1 `    if "GIT_INDEX_FILE" in os.environ:`, then a 2-line refuse(...) call
   whose first line starts with `        refuse(f"RECEIPT-INDEX-ENV-SET:`. Change ONLY the message body so it names the variable and never
   echoes its value (r65 sentinel F4). The needle RECEIPT-INDEX-ENV-SET must stay on the refuse call line.
3. git() helper: keep the scrub of GIT_DIR and GIT_WORK_TREE; add `-c core.excludesFile=<os.devnull>` to the argv; add env entries
   GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM=1, GIT_NO_REPLACE_OBJECTS=1 and keep GIT_OPTIONAL_LOCKS=0. Every git call in the
   writer must go through git(); grep the candidate to confirm no subprocess call to git bypasses it.
4. _snapshot_entry(): the mode mask becomes `st_mode & 0o7777` (setuid, setgid and sticky included); the mode column format stays
   `oct(...)` so _delta_label keeps working.
5. Docstring: replace the round-65 "round 66 routes" wording with the round-66 statement: caller-injected config and redirect env routes
   are refused (RECEIPT-ENV-CONFIG-SET, RECEIPT-ENV-REDIRECT-SET); ignore routes remain named limits. Keep every other docstring line.
6. Writer selftest: keep it passing (it currently has 30 cases). Add cases for the new env refusals and the full-mode-bit refusal if you
   can do so without changing existing case results; report the count.
Do NOT change any other behaviour. Do NOT add any refusal the matrix does not name. No new files under tools/.
Report the exact line numbers of each refusal class in candidate/notes.md.
""")

item("S66MutKill", "mutation-tester", f"""# Target
Kill-power for the round-66 C1 matrix against the candidate, plus the frozen M-ENV recipe check. Deliver under
{WD}/S66MutKill/ (mutants/, kill-matrix.tsv, report.md).
Step 0 (no candidate needed): read census/round-66/c1-counter.py and census/round-66/c1-matrix.tsv; list which C1 rows the base
writer already refuses or accepts (see census/round-66/controls/c1-do-nothing.txt).
Step 1 (wait): loop `test -f {CAND_READY}` with `sleep 60` up to 45 times; if it never appears, deliver report.md saying so and stop.
Step 2: candidate bytes are {CAND}. Verify its sha256 equals the CANDIDATE-READY content. Build mutants of THE CANDIDATE, one change
each, with a fresh scratch clone per mutant at base {BASE} plus the mutant file committed (identity via -c user.name=S66Seat...). Mutants:
  K1 remove the RECEIPT-ENV-CONFIG-SET gate (the whole block)
  K2 remove the RECEIPT-ENV-REDIRECT-SET gate
  K3 remove the git() `-c core.excludesFile=` pin
  K4 remove GIT_CONFIG_GLOBAL=os.devnull from the git() env
  K5 mode mask back to `& 0o777`
  K6 remove the GIT_NO_REPLACE_OBJECTS=1 entry
  K7 remove the GIT_CONFIG_NOSYSTEM=1 entry
  K8 M-ENV: `python3 -B {LANE}/census/round-66/c2-mutate.py --writer <candidate> --out <mutant>` (frozen recipe; it refuses if the anchor
     is absent; record its exit code and stderr verbatim if it refuses)
For each mutant that compiles: run the frozen C1 counter (`--root <clone> --rev <commit> --tool tools/souji-receipt-write.py`) and
record the SUMMARY line and EXIT. Kill = new_forgeries>0 or class_mismatches>0 or EXIT != 0. Compile-fail mutants count as not
measured, never as kills.
Step 3: for K8 also run the frozen C2 counter from the lane: `python3 -B {LANE}/census/round-66/c2-counter.py --root <clone> --tsv
{LANE}/census/round-66/c2-statements.tsv --tsv-rev {INSTR} --rev <mutant commit>` and the round-65 counter
`python3 -B {LANE}/census/round-65/c2-counter.py --root <clone> --tsv census/round-65/c2-statements.tsv --tsv-rev 2761f0aa4d2431b4b9abb4aa997dd3116b0b25b8 --rev <mutant commit>`.
Record both SUMMARY lines. Note that the SKILL.md at the mutant commit is the BASE SKILL.md unless you also commit the lane's SKILL.md
bytes; report that caveat plainly.
Deliver kill-matrix.tsv (K-id, mutant, measured?, new_forgeries, class_mismatches, EXIT, killed?) and the one-line kill rate.
Give the honest survivor list: any mutant that survives is a finding.
Clean up scratch with the EXIT trap. Never leave a clone behind.
""")

item("S66ReviewerDesign", "reviewer", f"""# Target
Attack the FROZEN C1 design (census/round-66/preregistration-attempt2.txt, census/round-66/c1-counter.py, census/round-66/c1-matrix.tsv)
first, then the CANDIDATE once it exists. Read-only. Deliver under {WD}/S66ReviewerDesign/design.md (findings table: id, severity
HIGH/MEDIUM/LOW, evidence path:line, one-line falsifier).
Part A (now): is each frozen row's expected class reachable by the candidate's intended refusal? Is any row a do-nothing pass in
disguise? Are the E-row fixtures realizable on this host (git version via `git --version`; read the fixture code in
c1-counter.py mutate()/case_env())? Check L2 (honest-route behaviour change of the -c core.excludesFile pin) for an honest row that
would change. Check the named limits L1-L5 are stated truthfully.
Part B (wait for {CAND_READY}, bounded `sleep 60` x 45): read the candidate ({CAND}) against the frozen predicate: does any new refusal
fire on an honest row? Does the mode mask change honest output? Is any refusal class emitted by a path other than the one notes.md
names? Verify the candidate's sha256 equals the CANDIDATE-READY content. Read-only; do not run the counter yourself.
Attack, do not praise. Name the single most likely way C1 could be a false green.
""")

item("S66ReviewerC2", "reviewer", f"""# Target
Attack the C2 counter and its population (census/round-66/c2-counter.py at {INSTR}, census/round-66/c2-statements.tsv, the
round-66 token repair RETURN_LITERAL) and the frozen M-ENV recipe (census/round-66/c2-mutate.py). Read-only. Deliver under
{WD}/S66ReviewerC2/review.md.
Checks to run (read-only, against committed bytes at {INSTR} / {BASE}; use `git -C {LANE} show <rev>:<path>`):
  a) Does RETURN_LITERAL (`\\breturn\\s*\\(?\\s*f?["']`) match any live writer line at {BASE} that is NOT a refusal emission? List
     every line the new live_markers() counts that the round-65 live_markers() did not, and vice versa, for the base writer.
  b) Is the M10 regression case in c2-counter.py selftest() a real test of the repair, or does it pass for any token?
  c) Does the stable s5 wording have a second occurrence risk? Is `DUPLICATE-LIVE-WORDING` reachable for a stable row?
  d) Prove or refute: an always-zero counter cannot pass the selftest (selftest control STUB-ALWAYS-ZERO).
  e) Does c2-mutate.py's anchor detection ever match more than one line in the candidate shape the executor is told to keep?
  f) Is the claim's kill-power predicate (r66 counter findings>=1 AND r65 counter findings=0 on M-ENV) falsifiable as written?
Deliver findings with HIGH/MEDIUM/LOW and a reproduction command for each. Do not run any mutating command.
""")

item("S66CriticClaims", "critic", f"""# Target
Falsify the two claims of round 66 against the lane's admission rules before any after-data exists. Read: MISSION.md and AXES.md at
/home/vgpnk/Projects/shokunin, {LANE}/corpus/QUALITY.md (Q59 axis-of-surface, Q120/Q122 chronology/content binding, Q126/Q127),
{LANE}/census/round-66/preregistration-attempt2.txt, {LANE}/census/round-66/controls/c1-do-nothing.txt,
{LANE}/census/round-66/controls/c2-do-nothing.txt, {LANE}/corpus/lessons/round-65.md (its Routed-to-round-66 list and Mistakes M1-M12),
{LANE}/corpus/lessons/round-65-verifier-spotcheck.md.
Deliver {WD}/S66CriticClaims/critic.md with: (1) for each routed r65 item, whether round 66 covers it, partly covers it, or
routes it again and why; (2) separability: is C1 independent of C2? Is C2's population row s5 dependent on C1's candidate bytes
(the needles RECEIPT-ENV-CONFIG-SET and RECEIPT-ENV-REDIRECT-SET exist only in the candidate)? If yes, state it as a named limit with
evidence; (3) every universal clause in the prereg and in the claim text ("all", "every", "complete", "none", "no") and whether an
enumerate or a measurement covers it; (4) the do-nothing controls: do they fail for the reason the prereg states? (5) whether the
M10 repair is a frozen-counter amendment or a new counter at a new frozen revision; (6) the honest-row set: is 5 accepts the full
honest population for the routes claimed?
Attack, do not praise. Give a verdict per claim: would-admit / would-reject-if / unprovable, with the single falsifier.
""")

item("S66SentinelScope", "sentinel", f"""# Target
Scope and safety audit of the round's instruments and (when it exists) the candidate. Deliver under {WD}/S66SentinelScope/scope.md.
Part A (now): the instruments census/round-66/c1-counter.py and c2-mutate.py — confirm (by reading code) that they write only under
--work/--receipt/--out and never write into the lane or under /tmp; confirm the counter's clean_env() strips caller GIT_CONFIG_*,
GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_REPLACE_REF_BASE and GIT_NO_REPLACE_OBJECTS, and that the fixture writes
its E-row config files beside the repo (case dir), not inside tools/.
Check what the E-row fixtures could do to the HOST: any fixture that sets a global config? any write outside {SCR}? The E3 fixture writes
global.gitconfig under the case dir only.
Part B (wait for {CAND_READY}, bounded `sleep 60` x 45): audit the candidate ({CAND}) for (a) any echo of an environment VALUE in a
refusal message (r65 F4), (b) any refusal path that writes a file, (c) any subprocess call that bypasses git(), (d) whether the
GIT_CONFIG_GLOBAL repoint could read or write a real global config, (e) whether the env names it refuses cover all of
GIT_CONFIG_* and the three redirects, and (f) whether the mode mask change could widen what the writer records beyond permission
bits. Report HIGH/MEDIUM/LOW with path:line.
Do not run any host-changing command (no sysctl, no sudo, no pacman). Read-only.
""")

item("S66ScoutSources", "scout", f"""# Target
Open the git documentation sources this round's C1 rows rest on, mechanically, and deliver captures plus located quotes. Deliver
under {WD}/S66ScoutSources/:
  git-environment.html   raw capture of https://git-scm.com/docs/git (the "ENVIRONMENT VARIABLES" section)
  git-environment.txt    tag-stripped text (python: html.parser or a regex that drops tags; record the recipe in recipe.py)
  git-config.html        raw capture of https://git-scm.com/docs/git-config
  git-config.txt         tag-stripped text
  quotes.tsv             one row per located quote: source, quote (<=25 words, verbatim), UTF-8 byte offset of the quote in the txt,
                         the sha256 of the txt, the access date (UTC) and the HTTP status
Quotes wanted (locate each; if a sentence is absent say so — do not paraphrase): the GIT_CONFIG_COUNT/GIT_CONFIG_KEY_/GIT_CONFIG_VALUE_
definition; GIT_CONFIG_GLOBAL and GIT_CONFIG_NOSYSTEM; GIT_OBJECT_DIRECTORY; GIT_ALTERNATE_OBJECT_DIRECTORIES; GIT_REPLACE_REF_BASE;
GIT_NO_REPLACE_OBJECTS; core.excludesFile (git-config); and the git-config statement on the precedence of command-line `-c`.
Verify each quote by re-slicing the txt at the offset and comparing bytes. Give the exact offsets and the sha256. Do not assign
registry S-ids (the L1 does). Use `curl -sSL --max-time 60 -o FILE URL` and record the HTTP status.
""")

item("S66ScribeEntry", "scribe", f"""# Target
Draft the round-66 corpus paperwork for the L1 to finalize. Deliver under {WD}/S66ScribeEntry/. Do NOT edit lane files.
1. knowledge-caller-env-routes.md — a draft of corpus/knowledge/caller-env-routes-receipt-writer.md: the claim (a receipt writer's
   status and object reads can be steered by caller-injected GIT_CONFIG_* and object redirects), the rule (the writer refuses
   their presence, pins the config routes to the null device, and masks no permission bits), the falsifiable form, a `## Gate` block
   with the source URLs, access dates, ≤25-word located quotes that the scout delivers in S66ScoutSources/quotes.tsv (cite them by
   offset only after reading that file; if the scout has not finished, leave the offset fields as TODO-SCOUT and say so), the
   `verified-at:` and `recheck:` lines (the recheck is the C1 counter command with the measured revision as a placeholder REV).
   Named limits: ignore routes, lexical C2, single-mutant kill.
2. skill-writer-rule-s5.md — the exact one-sentence SKILL.md writer-rule statement the population row s5 requires. It must contain
   byte-contiguously this literal (verify with grep -F after drafting, using the file census/round-66/c2-statements.tsv column
   after_pattern for s5, read via `git -C {LANE} show {INSTR}:census/round-66/c2-statements.tsv`):
   the s5 after_pattern string. Put that literal alone on one line of your file so the L1 can paste it.
3. sources-rows-draft.md — SOURCES.md registry rows in the contract's shape, copied from the format of the last three rows in
   {LANE}/corpus/SOURCES.md (read them, then match column order exactly). Leave the S-id as NEW-SID-1..3 placeholders and the
   quote/offset cells as TODO-SCOUT until the scout's quotes.tsv exists; note the row count before and after (`grep -cE` census
   command in CORPUS.md section SOURCES.md).
4. round-66-lesson-draft.md — skeleton of corpus/lessons/round-66.md: `## Gate`, `## Claims`, `## Mistakes`. In Mistakes, record the
   round's real mistakes so far, each with class, evidence pointer, captured-by, fix: (M-a) the headerless C2 do-nothing capture that
   broke the first freeze (evidence: the freeze-check output and commits 10d175a5 and 5d17a5de); (M-b) the attempt-1 prereg was edited
   in place by an append (commit 01bc1e16), restored by commit a81280e1; (M-c) GIT_REPLACE_REF_BASE without a trailing slash made the
   E6 row measure a git crash (commit 8410a97e, repaired before controls). Captured-by for each: none, unless you can name the criterion.
Keep every draft short. Name every file you wrote in your result.
""")

item("S66ConnectorOverlap", "connector", f"""# Target
Cross-claim/cross-source pattern scan. Deliver under {WD}/S66ConnectorOverlap/:
1. sibling-overlap.md: READ-ONLY grep of sibling lane repos under /home/vgpnk/Projects/shokunin/*-shokunin/ (not souji-shokunin) for
   the terms: GIT_CONFIG_COUNT, GIT_OBJECT_DIRECTORY, GIT_REPLACE_REF_BASE, core.excludesFile, status.showUntrackedFiles,
   RECEIPT-INDEX, receipt writer, st_mode. For each hit: path:line, whose ground it is, and whether it overlaps round 66's C1/C2.
   Use `grep -rn --include='*.md' --include='*.py' --include='*.sh' -e TERM1 -e TERM2 /home/vgpnk/Projects/shokunin/<lane>` with the
   lane list from `ls -d /home/vgpnk/Projects/shokunin/*-shokunin`. Read-only.
2. merge-check.md: READ-ONLY read of /home/vgpnk/Projects/shokuknow/merge/souji/MERGE-REPORT.md (if it exists) and the list of
   staged theme names. Name any theme that touches receipt-writer env routes, untracked visibility or mode bits. Do NOT run any
   campaign tool there. Do not write into shokuknow.
3. considerthese-check.md: `test -d {LANE}/considerthese` and what it says (expected: absent).
4. Overlap verdict: one paragraph, with the sibling lane that is closest to round 66's ground and why it is or is not overlap.
Connector seats never mutate anything. Read-only throughout.
""")

item("S66RevengerProbe", "revenger", f"""# Target
Empirical probe of how this host's git (run `git --version`; record it) honours each caller-injected environment form the C1 rows
use. Read-only against throwaway repos that you create under {SCR}/S66RevengerProbe/ (D=$(mktemp -d -p {SCR}/S66RevengerProbe),
`git -C "$D" init -q`, verify `git -C "$D" rev-parse --show-toplevel` equals $D before the first commit, identity via -c flags only).
Deliver {WD}/S66RevengerProbe/probe.txt — one line per probe: name, the exact env/argv used, rc, and the observed effect.
Probes:
  P1 GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.excludesFile GIT_CONFIG_VALUE_0=<file listing an untracked name>: does `git status
     --porcelain` hide the untracked file? (expect yes; record)
  P2 GIT_CONFIG_PARAMETERS="'core.excludesFile=<file>'" (the legacy single-quoted form): does it hide the file? record rc and effect.
  P3 GIT_CONFIG_GLOBAL=<file with excludesFile>: hides? Then GIT_CONFIG_GLOBAL=/dev/null with GIT_CONFIG_NOSYSTEM=1: does it stop
     hiding? (the E3 repoint)
  P4 GIT_OBJECT_DIRECTORY=<copy of .git/objects>: does `git cat-file -t HEAD` still succeed? record rc.
  P5 GIT_ALTERNATE_OBJECT_DIRECTORIES=<empty dir>: rc and effect.
  P6 GIT_REPLACE_REF_BASE=refs/replace-forged-r66 (no trailing slash) vs refs/replace-forged-r66/ (trailing slash): rc and stderr
     for `git cat-file -t HEAD` (expect the no-slash form to abort with a BUG line — record exactly).
  P7 -c core.excludesFile=/dev/null on the command line PLUS GIT_CONFIG_COUNT pointing at a hiding file: which wins? (expect the
     command-line -c; record)
  P8 GIT_NO_REPLACE_OBJECTS=1 with a replace ref present: does `git cat-file -p` show the original? (record; build the replace ref
     with `git -C "$D" replace` in the throwaway repo only)
  P9 chmod 4644 and 1644 on a regular file: does `oct(os.stat(p).st_mode & 0o777)` hide the bits (python3 -c) and `os.stat & 0o7777`
     show them? record.
Verify each finding by re-running it once. Clean up with a trap. Do not touch host config, sysctls or any repo outside your scratch.
""")

CONFIG = {
    "wave": "souji-r66-w1",
    "milestone": "souji r66 (attempt 1): post-freeze wave — candidate writer for the env-route and mode-bit rows, kill-power on the matrix and "
                 "M-ENV, design/C2/claim attacks, scope audit, git-environment source capture, corpus drafts, sibling overlap, host git probes",
    "reportDir": ".ufo/waves/round-66/w1",
    "context": CONTEXT,
    "items": [
        {"name": name, "role": role, "prompt": GODSPEED + "\n" + body}
        for name, role, body in ITEMS
    ],
}


def main() -> None:
    out = os.path.join(HERE, "w1-spec.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(CONFIG, f, indent=1, ensure_ascii=False)
    print(f"wrote {out} with {len(CONFIG['items'])} seats")


if __name__ == "__main__":
    main()
