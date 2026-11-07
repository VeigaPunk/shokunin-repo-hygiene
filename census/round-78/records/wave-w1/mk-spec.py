#!/usr/bin/env python3
"""souji r78 wave w1 spec builder (L1 SoujiR78). Writes .ufo/waves/round-78/w1-spec.json.
The `# Write scope and bounds` .. `# Report format` context tail is the r77 builder's text with round-77 -> round-78."""
import json
import os

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SCR = "/fast/scratch/hyaku/souji-r78"
GS = open(os.path.expanduser("~/.agents/skills/godspeed/directive.md")).read()
HEAD = "/skill:godspeed\n" + GS + "\n\n"
BASE = "a8558d410e9855a9d990d6542a24a9a3a365ab6c"
P = "a0dcfa8d7da794e821b22a421584ac2a03c611c0"
F = "007404ea363461a76ff23afcf6173b3281532dd3"
W = "ed22dc9cb7a6b61a7d0bd150db4a95191b1333aa"
K = "d90740fec1862556ed504aafcd21e89d5dece0f0"
L = "a0f3b91fe59129802c48f7e4db750960ddeaa408"
L2 = "87d456179668738ca59e607c3176de056e6a9991"
A = "319109b0ddc836c6cf3364fdde3ab99796f21f32"
R = f"{LANE}/census/round-78"
TAIL = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ctx-tail.txt")).read().replace("{LANE}", LANE).replace("{SCR}", SCR)

context = f"""# Goal
souji round 78 (lane repo {LANE}, lane id souji). The L1 (SoujiR78) holds the planner seat and is the ONLY integration owner: it commits through the lane helper and writes the report. You are one seat of ONE wave of 12 seats. Seats deliver files and findings only. Your mandate is to FALSIFY the frozen round-78 claims and the round's landed changes: re-derive every number yourself from committed bytes; a number you cannot reproduce is a finding. Do not trust the L1's counts.

# Evidence durability
FIRST action: create your report file (the `Report:` trailer path) with a one-line skeleton, and append to it as you go. Your final yield must repeat the same content. A seat that ends without that file counts as no verdict.

# Chronology (binding; read {R}/preregistration.txt first — it is the frozen contract, Q99 grammar)
- Lane base (r77 admitted): {BASE}.
- P {P}: census/round-78/c1-gitsrc-counter.py (C1 counter, 17 routes: g1-g11 FIFO git discovery sources — $GIT_DIR/config, HEAD, packed-refs, commondir, include.path, includeIf.gitdir, nested relative include, config.worktree, $HOME/.gitconfig, $XDG_CONFIG_HOME/git/config, symlinked config; t1 FIFO config in the ORIGIN repository; q1-q5 positive controls; runs the gate in its own session with a 75 s bound and kills the process group -> verdict=HANG), c1-population.tsv, c2-pointer-counter.py (C2 successor counter: pinned populations r77/r78, MOVED bound to round + last component, QUARANTINED bound to the token's directory and refused when the token exists under the fleet root, TOKEN bound to the source text; --forge per-row forged-ledger expectations), c2-population.tsv (22 MISSING findings of tools/souji-pointer-check.py over LOG.md at the base), c2-forge-r77.tsv (7 forgeries over the r77 population), c2-forge-r78.tsv (12 over the LOG population), c2-forge-legacy.py (runs the frozen r77 counter per forgery), c2-mechanical-ledger.py (control generator), controls/ (C1: K-a lane-base gate mismatches=12 hangs=12; K-b refuse-any-include 14; K-c config-only 10; K-d timeout-only 11. C2: K-a no ledger resolved=0; K-b mechanical ledger resolved=19 refused=3; K-c r77 counter accepts 7 of 7 forgeries; K-d shifted population FATAL exit 2; K-e G6 byte-equal copy at round-02: r77 accepts, r78 refuses), records/c2-prefreeze-*.txt, srcs/ (S323 git config.adoc, S324 git setup.c at v2.56.0).
- F {F}: census/round-78/preregistration.txt.
- W {W}: C1 candidate — tools/souji-pre-report-gate.sh: gitsrc_scan()/gitsrc_one() before check 1 (refuses RECEIPT-NONREGULAR-GITSOURCE, skips checks 1 and 4 as FAIL), check 1's rev-parse and ls-remote under `timeout -k 5 45` (RECEIPT-GIT-TIMEOUT).
- K {K}: C2 candidate part 1 — force-added .ufo/waves/round-27/ (all files), .ufo/waves/round-53/w1-results.json, .ufo/waves/round-68/w1/ (240 files) at their own paths.
- L {L}: census/round-78/c2-pointer-ledger.tsv as first committed (DEFECTIVE: L21's row overwritten by a duplicate L19 row; receipt records/attempts/c2-at-L-duplicate-row.txt).
- L2 {L2}: ledger repaired (19 rows).
- A {A}: records/c1-after.txt (17/17, hangs=0), c1-regress-r77.txt (16/16), c1-regress-r76.txt (30/30), c1-regress-r36.txt (21/21), c1-regress-r27.txt (4/4), c2-after.txt (22/22, forgeries 12/12 refused), c2-regress-r77.txt (35/35, 7/7), c2-pointer-check-after.txt (missing=19), freeze-check-at-F.txt.

# Claims (frozen predicates are in the preregistration; never change them)
C1 operability (sourced on S323/S324, opened this round): the pre-report gate refuses non-regular git discovery sources before any git call and bounds check 1; 17 rows mismatches 12 -> 0 and hangs 12 -> 0; K-b/K-c/K-d stay red; r77 16/16, r76 30/30, r36 21/21, r27 4/4; a domain trial on the lane at the report tip (run by the L1 later).
C2 calibration (lowest owned axis, 7): the 22 LOG.md evidence pointers the pointer check reports MISSING at the base resolve to verified classes under the location-bound successor counter; resolved 0 -> 22 (mechanical no-capture ledger ceiling 19); 12 LOG forgeries and 7 r77 forgeries refused; pointer-check missing 22 -> 19.

# Frozen invocations (run from {LANE}; never alter counters, populations, ledgers or controls)
- C1: copy the gate and tools/souji-receipt-write.py at a revision into ONE dir (`git show <rev>:tools/souji-pre-report-gate.sh > D/souji-pre-report-gate.sh`, same for the writer); python3 -B census/round-78/c1-gitsrc-counter.py --gate-dir D --work <SCRATCH>/c1 (work absent or empty; ~50 s on the W gate, ~15 min on the base gate because 12 rows hit the 75 s bound).
- C2: python3 -B census/round-78/c2-pointer-counter.py --root {LANE} --rev <rev> --fleet-root /home/vgpnk/Projects/shokunin --population census/round-78/c2-population.tsv [--ledger census/round-78/c2-pointer-ledger.tsv] [--forge census/round-78/c2-forge-r78.tsv] (~2 s; LOCAL-POLICY/QUARANTINED read the lane disk, so --root must be the lane checkout). The r77 population: --population census/round-77/c2-population.tsv --ledger census/round-77/c2-pointer-ledger.tsv --forge census/round-78/c2-forge-r77.tsv.
- Pointer check: python3 -B tools/souji-pointer-check.py --root . --rev <rev> LOG.md (~3 s).
- Every receipt starts with `command=<literal command>` (rec.sh); replaying that line with your scratch prefix is a valid check.
<SCRATCH> must be a fresh directory under {SCR}/<your seat name>/ (mkdir -p it). Counters refuse --work under /tmp, /var/tmp or /dev/shm. FIFO fixtures: never open a FIFO without a timeout; run anything that may block under `timeout -k 5 <s>` in its own session (setsid) so the whole process group dies; never leave a blocked process behind.

{TAIL}"""

items = [
 ("S78Connector", "connector", f"""# Target
Cross-claim separation and sibling-overlap scan for round 78. Read-only.

# Change
1. Causal separation: from receipt `# bind`/`instrument=` lines and commit contents (`git show --name-only` for W {W}, K {K}, L2 {L2}) confirm no C1 receipt reads a C2 byte and no C2 receipt reads a gate byte. Would C1 verify with K/L/L2 absent, and C2 with W absent? Verdict SEPARABLE/COUPLED.
2. Other lane tools under {LANE}/tools that run git in the lane with no discovery-source guard or timeout (a FIFO $GIT_DIR/config or HEAD blocks them the same way): file:line, and whether the r78 pre-check covers them (it covers only the gate).
3. Sibling overlap (read-only; other *-shokunin repos under /home/vgpnk/Projects/shokunin): which sibling pre-report gates call git (rev-parse, ls-remote, status) with no timeout before any source check; which siblings' LOG.md files cite `.ufo/waves/...` paths that are not committed (count per lane via `git ls-tree`). Table: lane, file:line or count, exposed yes/no.

# Acceptance
Tables with verdicts and file:line; findings by severity."""),
 ("S78ScoutSources", "scout", f"""# Target
Re-open the round's two new sources and test the sentences the claims rest on. Read-only on the lane.

# Change
1. Fetch https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config.adoc and https://raw.githubusercontent.com/git/git/v2.56.0/setup.c yourself (curl -sSL); compare sha256 with {R}/srcs/git-config.adoc-v2.56.0 (a6e644cb…b2c9) and {R}/srcs/git-setup.c-v2.56.0 (8316b1ad…c589).
2. config.adoc "Includes" (lines ~85-105): locate "The contents of the included file are inserted immediately, as if they had been found at the location of the include directive." (line, word count <=25). Does git skip a missing include file silently (find the sentence or the code: config.c handle_path_include at v2.56.0, file:line)? Does git open an include target with a blocking open (config.c git_config_from_file / fopen_or_warn)? file:line.
3. setup.c get_common_dir_noenv (~line 320) and validate_headref (~line 350): quote the file_exists/strbuf_read_file lines and the HEAD open; do both block on a FIFO (strbuf_read_file -> open(2) without O_NONBLOCK, wrapper.c/strbuf.c at v2.56.0)? Is the gate's claim "every git command reads HEAD and commondir at discovery" true for `rev-parse` and `ls-remote` (setup.c is_git_directory / discovery path)?
4. corpus/SOURCES.md: would new rows for config.adoc Includes (S323) and setup.c (S324) be within-scope duplicates of existing rows (grep config.adoc, git-config, setup.c, S057, S124)? The S321 row's anchor cell says "the fstat type read follows at line 1169" — r77 closure routed this as wrong (fstat feeds the size only): confirm or refute from https://raw.githubusercontent.com/git/git/v2.56.0/dir.c lines 1160-1200.

# Acceptance
sha256 match/mismatch; quotes with line numbers and word counts; per-question HOLDS/DISAGREE with file:line; admit/reject per row."""),
 ("S78ExecC1", "executor", f"""# Target
Reproduce C1 from committed bytes.

# Change
1. Run the C1 counter over the W gate ({W}) and over the lane-base gate ({BASE}), each with its own revision's writer beside it; compare SUMMARY/EXIT/ROW lines with records/c1-after.txt and controls/c1-K-a-do-nothing.txt (the base run takes ~15 min; run it in the background while you do step 2).
2. Replay controls/c1-K-b-refuse-any-include.txt, c1-K-c-config-only.txt, c1-K-d-timeout-only.txt from their command= lines (gate dir: the variant from controls/variants/ copied as souji-pre-report-gate.sh beside the base writer); confirm each variant's sha256 equals the receipt's `# gate` line.
3. Replay records/c1-regress-r77.txt, c1-regress-r76.txt, c1-regress-r36.txt (create its --work dir first), c1-regress-r27.txt with the W gate.
4. After every run, check that no process from your scratch dir is left (ps -eo pid,args | grep <your scratch>); a leftover blocked git is a HIGH finding against the counter.
5. Run the W gate on the lane itself (read-only): bash {LANE}/tools/souji-pre-report-gate.sh --lane {LANE} --branch master --report {R}/preregistration.txt --prereg {R}/preregistration.txt; record check lines, rc and wall time. check-clean may FAIL while seat files sit under .ufo/waves (now partly tracked!) — name the cause if it fails.

# Acceptance
Every reproduced/differing number with the command and output lines; HIGH/MEDIUM/LOW findings."""),
 ("S78ExecC2", "executor", f"""# Target
Reproduce C2 from committed bytes and test the ledger against the lane.

# Change
1. Run the C2 counter at A {A} with the ledger and --forge census/round-78/c2-forge-r78.tsv; at the base {BASE} with no ledger; with the mechanical control ledger (controls/variants/c2-K-b-mechanical-ledger.tsv) at the base; the r77-population regression; compare with records/c2-after.txt, controls/c2-K-a-no-ledger.txt, controls/c2-K-b-mechanical.txt, records/c2-regress-r77.txt.
2. Replay controls/c2-K-c-forge-r77-counter.txt (c2-forge-legacy.py with a fresh --work), c2-K-d-shifted-population.txt and c2-K-e-g6-collision.txt (probes/g6-collision.sh LANE REV fresh-WORK) from their command= lines.
3. Byte identity of the K captures: for each of .ufo/waves/round-27, .ufo/waves/round-53/w1-results.json, .ufo/waves/round-68/w1 compare the committed tree at K with the frozen digest in c2-population.tsv (L10, L14, L20) using the counter's own rev_digest (import it). Are any files in those dirs on disk but NOT committed, or committed but not on disk?
4. The pointer check over LOG.md at A: missing=19? Which 19?
5. Ledger truth row by row: for each MOVED row, is the target the same seat/wave artefact (not just same bytes)? For each ABSENT row, `git log --all -- <token>` and a search of the fleet root and lane disk.

# Acceptance
Every reproduced/differing number with the command and output lines; HIGH/MEDIUM/LOW findings."""),
 ("S78ExecEvade", "executor", f"""# Target
Forge or hang the W gate ({W}) through routes OUTSIDE the 17 frozen rows. Work only on fixtures in your scratch.

# Change
Build fixtures like census/round-74/records/wave-repair/probes/evade-probe.py build() (import it) and run the W gate (with its writer) in its own session under a 60 s bound; for each route record rc, check lines and secs. Routes to try (add your own): (a) a FIFO $GIT_DIR/objects/info/alternates; (b) a FIFO loose ref $GIT_DIR/refs/heads/master; (c) a FIFO $GIT_DIR/shallow; (d) `.git` as a gitfile (`gitdir: <dir>`) whose target dir holds a FIFO config — and a gitfile that is itself a FIFO; (e) a linked worktree (git worktree add) whose common dir config is a FIFO, gate run on the worktree; (f) include.path with `~/` and with a value containing a newline or a leading space; (g) an include cycle (a includes b includes a) and an include chain 12 deep (git's limit is 10 — does git error, and does the gate pass/fail correctly?); (h) includeIf.onbranch / hasconfig conditions pointing at a FIFO; (i) core.hooksPath / core.fsmonitor configured in an included file; (j) a FIFO at $XDG_CONFIG_HOME/git/attributes or ignore with HOME unset; (k) the remote URL pointing at a path whose HEAD is a FIFO (does t1's timeout cover it?); (l) a FIFO /etc/gitconfig cannot be built without root — reason about it instead, do not try.
For each route: does the base gate hang/forge, does W hang/forge or refuse? Any W hang >45 s or a W PASS on a lane that hides content is a finding.

# Acceptance
Route table: route, base verdict, W verdict, secs, severity; probe script(s) under your seat directory."""),
 ("S78MutGate", "mutation-tester", f"""# Target
Kill power of the frozen C1 counter (census/round-78/c1-gitsrc-counter.py, 17 rows) against mutants of the W gate ({W}).

# Change
Write >=10 mutants of the W gate's r78 block (copy into your scratch; never edit the lane), e.g.: drop HOME/XDG checks; drop include recursion (depth 0 only); drop relative-include resolution; drop the commondir read; drop packed-refs; `-f` -> `-e`; skip-check-4 removed; timeout removed from ls-remote; timeout raised to 300; RECEIPT-GIT-TIMEOUT message removed; refuse when gitsrc_n>1 instead of >0; include scan without GIT_CONFIG_GLOBAL isolation. Run the frozen counter on each (gate dir = mutant + W writer). Table: mutant, killed by which row(s) / SURVIVED. For every survivor say whether it is a real gap (a route the rows miss) and propose one row.

# Acceptance
Mutant table with kill rows; survivors with proposed rows; mutant files under your seat directory."""),
 ("S78MutCounter", "mutation-tester", f"""# Target
Kill power of the r78 C2 counter's new rules against its own frozen forgery sets and controls.

# Change
Copy census/round-78/c2-pointer-counter.py into your scratch and write >=10 mutants of the r78 rule changes: MOVED round binding removed; MOVED basename binding removed; QUARANTINED dirname binding removed; QUARANTINED fleet check removed; TOKEN next-line rule accepting any rest; TOKEN template rule dropping the `r<N>` check; template literal check removed; population pin bypassed (any sha accepted); forge `matched == forged` replaced by `accepted == 0`; forge rows judged with the full ledger instead of the forged row. Run each mutant (a) over the r78 population with the ledger and c2-forge-r78.tsv at A {A}, (b) over the r77 population with the r77 ledger and c2-forge-r77.tsv, (c) probes/g6-collision.sh adapted to call the mutant. Table: mutant, killed by which forgery/control, or SURVIVED. Then forge NEW single ledger rows (not in either frozen set) that the r78 counter accepts but that are false; each is a finding.

# Acceptance
Mutant table; accepted false forgeries with the exact row; files under your seat directory."""),
 ("S78Reviewer", "reviewer", f"""# Target
Surgical correctness review of the W gate diff and the two r78 counters.

# Change
1. `git diff {BASE} {W} -- tools/souji-pre-report-gate.sh`: bash correctness (quoting, word splitting of include values, `${{line#* }}` parsing of `git config --get-regexp` output for keys with spaces/case, `~/` expansion vs git's `~user/`, relative-path base, recursion and the seen-set, `set -u` traps, the `case $?` after command substitution, exit codes 124/137, behaviour when HOME is unset), and whether a refusal can be bypassed (gitsrc_n stays 0 while a FIFO is read) or the scan itself can hang (any open of an unchecked path: `read < $lane/.git`, `read < commondir`).
2. census/round-78/c1-gitsrc-counter.py: does it judge what the prereg says (verdict FAIL needs rc=1 AND a check-*=FAIL line; class anywhere in output)? Can a gate that prints the class token but passes match a FAIL row? Is the 75 s bound vs the 45 s gate timeout sound for t1?
3. census/round-78/c2-pointer-counter.py vs census/round-77/c2-pointer-counter.py (`diff`): any rule weaker than r77? R0 still reads the population's own base? Forge mode isolation (one row replaced, only that item judged)?

# Acceptance
Findings with file:line, severity, and a reproducer where possible."""),
 ("S78CriticClaims", "critic", f"""# Target
Attack the two claims as declared: are they real moves a do-nothing control cannot reach, correctly axis-named, and causally separable?

# Change
1. C1: is the move operability (the gate stops hanging) or coverage? Does any K control come close (K-c config-only 10, K-d timeout-only 11)? Would a gate that runs everything under `timeout 45` and fails on expiry (no pre-check) meet the frozen target? Build that variant in scratch and run the frozen counter. Is t1 meaningful (it fails tip on any slow remote)?
2. C2: thin? 19 of 22 reachable by the committed mechanical generator; the claimed delta beyond it is 3 captures + an instrument upgrade that landed pre-freeze. Is the instrument upgrade a pre-freeze control or an unregistered claimed gain? Is ABSENT for lost evidence (L04 L05) a truthful resolution or a label that hides a calibration defect? Is LOG.md a self-assessment file in the sense of the r77 C2 claim (calibration = mismatches between the lane's self-assessment and repo state)?
3. Check the prereg's targets against the receipts literally (numbers, EXIT codes, class tokens).

# Acceptance
Verdict per claim (holds / thin / wrong axis / falsified) with evidence; findings by severity."""),
 ("S78CriticDiscern", "critic", f"""# Target
Discernment of the round's source rows and ledger classes.

# Change
1. Source rows: S323 (git config.adoc Includes) and S324 (git setup.c get_common_dir_noenv) — do they ground the C1 sentences "every git command reads HEAD/commondir/config/includes at discovery" and "a FIFO there blocks"? Which parts rest on S062 fifo(7) and which on code reading? Is a tier-A code row right for a behaviour claim the fixtures already show?
2. Ledger: for each of the 19 rows in census/round-78/c2-pointer-ledger.tsv decide agree/disagree with its class and note (open the LOG.md line at the base {BASE}: `git show {BASE}:LOG.md | sed -n '<line>p'`). Pay attention to L04/L05 (lost evidence called ABSENT), L07/L08/L19 (prose), L17 (removed), L06 (QUARANTINED via a stub), L16/L18 (fleet L0 file).
3. Pick one admit and one reject the L1 should record in the lesson Gate.

# Acceptance
Row table agree/disagree with reasons; source verdicts."""),
 ("S78Sentinel", "sentinel", f"""# Target
Safety review of the W gate's new code path: can a hostile repository make the gate execute code, read outside its bounds, hang, or leak paths?

# Change
1. The include scan runs `git config --file <path>` from `/` with GIT_CONFIG_GLOBAL=/dev/null and GIT_CONFIG_NOSYSTEM=1: can a repository-controlled include value make that call read a device (/dev/zero, /dev/stdin, /proc/self/fd/0), a huge file, or a path that blocks other than a FIFO (a socket? a character device like /dev/tty)? `-f` excludes non-regular files, but what about /proc files (regular, may block)? Test in scratch with timeouts.
2. Can a value with `$(...)`, backticks, or glob characters be expanded by the gate's bash (word splitting, globbing in `$v` uses)? Test.
3. Deep or cyclic includes: CPU/time bound of the recursion; does the seen-set stop cycles via different spellings (`a`, `./a`, `../dir/a`, symlink aliases)?
4. D30 no-echo: does any new detail line print a path?
5. SIGTERM (S77Sentinel MEDIUM-3): is it still open? Does the new timeout change it?

# Acceptance
Findings HIGH/MEDIUM/LOW with reproducers (scripts under your seat dir); no host changes, no sudo."""),
 ("S78Scribe", "scribe", f"""# Target
Draft the round's corpus text for the L1 to integrate (the L1 decides; you write drafts only under your seat directory).

# Change
1. Draft two SOURCES rows in the exact 11-column shape of {LANE}/corpus/SOURCES.md rows S320-S322 (read them): S323 git config.adoc at v2.56.0 "Includes" (capture census/round-78/srcs/git-config.adoc-v2.56.0, sha256 a6e644cb2495df1f5e25f584e2cb7c06ec673e8b90acc52ae061a0fb6d42b2c9, 21095 bytes, fetched 2026-11-07, HTTP 200), quote lines 99-101 "The contents of the included file are inserted immediately, as if they had been found at the location of the include directive." (verify words <=25 and the line numbers yourself); S324 git setup.c at v2.56.0 get_common_dir_noenv (capture census/round-78/srcs/git-setup.c-v2.56.0, sha256 8316b1ad961ac6b1fa29dfdf1094a344aec8673f6637e6c00ba913a6668fc589, 83214 bytes), quote the file_exists/strbuf_read_file lines (no `|` characters inside any cell — paraphrase code containing `||`). used-by: corpus/knowledge/git-discovery-sources.md and corpus/QUALITY.md Q140.
2. Draft corpus/knowledge/git-discovery-sources.md (<=60 lines): which files every git command reads before doing anything (HEAD, commondir, config scopes, includes, config.worktree, packed-refs on ref lookup), why a FIFO there hangs any tool (S062, S323, S324), the gate's rule (regular-or-absent, include walk, 45 s timeout on check 1), named limits (SIGTERM, /etc/gitconfig, conditions not evaluated). Cite S-ids only, no `.ufo/waves` paths.
3. Draft QUALITY Q140 (one table row in the shape of Q138/Q139 in {LANE}/corpus/QUALITY.md): a lane gate that runs git in a repository it does not own checks git's discovery sources first and time-bounds remote calls.
4. Run {LANE}/../scripts/sources-census.sh validate --file <a scratch copy of corpus/SOURCES.md with your two rows appended to the Registry table> and record the output and exit code.

# Acceptance
Files: S78Scribe/sources-rows.md, S78Scribe/knowledge-git-discovery-sources.md, S78Scribe/quality-q140.md, S78Scribe/census-validate.txt; the census exit code."""),
]

spec = {
    "wave": "souji-r78-w1",
    "milestone": "souji r78: falsification of C1 gate git-discovery-source refusal and C2 LOG.md pointer resolution",
    "reportDir": ".ufo/waves/round-78/w1",
    "context": context,
    "items": [{"name": n, "role": r, "prompt": HEAD + p} for n, r, p in items],
}
with open(f"{LANE}/.ufo/waves/round-78/w1-spec.json", "w") as f:
    json.dump(spec, f, indent=1)
print(len(items), "items")
