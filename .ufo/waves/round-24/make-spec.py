#!/usr/bin/env python3
"""Generate the souji round-24 wave specs.

Run: python3 -B .ufo/waves/round-24/make-spec.py w1
Writes .ufo/waves/round-24/w1-spec.json next to this file.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
SK = "/home/vgpnk/Projects/shokuknow"
PKG = f"{SK}/merge/souji"
KPKG = f"{PKG}/knowledge/corpus/knowledge"
BASE = "a65fac98964b445758e94c805728c9a19d302ff8"
PREREG = f"{LANE}/.ufo/waves/round-24/preregistration.txt"
GODSPEED = """You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls."""


def context(goal: str) -> str:
    return f"""# Goal
{goal}

# HARD BOUND (violating this voids your seat)
souji is a hygiene lane, but its write scope is its own repo only. **Never delete, move,
quarantine or classify-for-cleanup anything in {FLEET} outside {LANE}/.** Incident 2026-10-25:
the fleet's tracked .scratch/ tree was deleted mid-run by an unidentified seat. Never touch
{FLEET}/.scratch/, {FLEET}/.ufo/state/, {FLEET}/.ufo/watchdog.log, MANIFEST.json, the fleet
scripts/ or templates/, any sibling lane repo, the lane's jj state or git index, or {SK} (read-only
source: never write, commit, fetch, push or run a campaign tool there).

# Contract
- Read {PREREG} FIRST. It is the frozen counter contract (claims C1/C2/C3, case sets, kill
  rules). Never propose changing a predicate, target or case set as if it were allowed after data:
  if you believe a counter is wrong or gameable, report it as an ATTACK.
- You are a READ-ONLY seat for the lane: write ONLY your own report and, if your item names one,
  the delivery file(s) inside your own report directory. No `git add/commit/push/stash/checkout/
  reset`, no `jj` mutation, no `rm`/`mv` of anything you did not create, no signals. Read-only
  `git log/show/diff/status/ls-tree/cat-file/rev-parse` against the lane are fine.
- Scratch goes ONLY under `/var/tmp/souji-r24-<YourName>/` (never /tmp); any git repo you need is
  created there with `git init`; remove your scratch before you finish.
- Absolute paths only. Your tools start at the FLEET root, not the lane: every lane path must be
  written as {LANE}/<path>. Every `Report:` trailer path is relative to {LANE} — write it at
  {LANE}/<that path>. A relative path lands in the wrong repo.
- A source claim needs a location: URL or repo path plus line/section, and a <=25-word verbatim
  quote copied from bytes you opened this run, containing no literal or escaped `|`.
- Unrun checks have not passed. Never report an execution you did not perform; label inference as
  `[INFERENCE]`. Run lane Python with `python3 -B` (no __pycache__ in the lane).
- Tooling is authorized (operator 2026-10-19): you may install or upgrade tools that help the
  task; read /home/vgpnk/.omp/agent/RULES.md first (official channels only, record tool/version/
  channel/reason in your report). **pacman guard: all pacman transactions are PAUSED host-wide** —
  install via `uv tool`/`npx`/an official binary in `~/.local/bin`, or route around it. Never run
  `pacman -S/-Sy/-Syu/-U/-R`, never downgrade, never restart a host service.
- Certification OFF, K5 HELD, F5 reap + NAMESPACE holds unchanged. No credentials, no live /proc
  census, no `census/operator-sweep-*` contents, no `.scratch/` contents. Never `agent://all`.

# Output shape
Markdown report at your rendered `Report:` path: `## Status` (one line `STATUS: PASS|PARTIAL|FAIL`
+ why), `## Evidence` (command, output excerpt, revision), `## Findings` (numbered, each with its
location), `## Attack log` where your item is an attack. Terse; no filler.
"""


def item(name: str, role: str, task: str) -> dict:
    return {"name": name, "role": role, "prompt": "/skill:godspeed\n" + GODSPEED + "\n\n## Task\n" + task}


ITEMS: list[dict] = []


def add(name: str, role: str, task: str, wave: str = "w1") -> None:
    ITEMS.append(item(name, role, task + f"\nReport path to ask for: `.ufo/waves/round-24/{wave}/{name}.md`."))


SIZE_CLI = """  python3 -B tools/souji-size-census.py --repo PATH
  stdout LC_ALL=C key=value lines (census.tool=souji-size-census, census.status=ok,
  census.git_version=, census.common_dir=, census.invoked_from=main|linked|bare,
  count.<field>= for every `count-objects -v` field with `-` mapped to `_`,
  census.warning=<verbatim> per `warning: garbage found:` stderr line); LAST line is
    garbage=G size_garbage=K unreachable=U alternates=A
  exit 0 ok; 2 refused (unknown argv incl. any --lost-found, promisor/partialClone repo, not a
  repository); 1 git failure (any stderr other than `warning: garbage found:` lines)."""


def wave1() -> dict:
    goal = (f"Souji round 24, wave 1 (build + first falsifiers). Lane: fleet repository & workspace hygiene "
            f"(掃除). Axes: calibration (7, lowest), operability (8), coverage (8); no axis may be harmed. "
            f"Claims frozen in {PREREG} at lane commit f9db2181647d91470a724a12d626bd6106805076: C1 F2 "
            f"write-safety size census (coverage), C2 coverage-map agreement (calibration), C3 receipt "
            f"verify/run symmetry (operability); assimilation theme = F2 linked-worktree `garbage` false "
            f"positive from {PKG}. Lane base {BASE}. The L1 holds the planner seat and is the only integrator.")

    # ---------------- C1 build ----------------
    add("ExecSizeCensusTool", "executor", f"""Write the C1 tool draft at
`{LANE}/.ufo/waves/round-24/w1/souji-size-census.py` (the L1 copies it to `tools/souji-size-census.py`).
Frozen CLI (preregistration C1):
{SIZE_CLI}
Read-only envelope (model it on `{LANE}/tools/souji-repo-structure.sh` header): env GIT_OPTIONAL_LOCKS=0,
GIT_NO_LAZY_FETCH=1, GIT_TERMINAL_PROMPT=0, GIT_NO_REPLACE_OBJECTS=1, LC_ALL=C; config overrides
`-c maintenance.auto=false -c gc.auto=0 -c core.fsmonitor=false`; never `cd`, never a shell string
(subprocess argv lists). Resolve `git -C PATH rev-parse --path-format=absolute --git-common-dir`;
run `git --git-dir=<common> count-objects -v` and `git --git-dir=<common> fsck --unreachable
--no-reflogs --no-progress` (count `unreachable ` lines; never `--lost-found`, never `--dangling`
writes — there are none, but do not add options). alternates = non-empty, non-`#` lines of
`<common>/objects/info/alternates` if present. Refuse (exit 2, before any walk) when
`extensions.partialClone` is set or any `remote.*.promisor=true`. Python 3 stdlib only, <=200 lines,
`--help`, `--selftest` not required. Test it yourself ONLY on throwaway repos under
`/var/tmp/souji-r24-ExecSizeCensusTool/` (include a linked worktree and a dangling blob) and paste
the outputs. Never run it against the lane or fleet repo.""")

    add("ExecSizeCensusFixture", "executor", f"""Write the C1 fixture draft at
`{LANE}/.ufo/waves/round-24/w1/r24-size-census.py` (the L1 copies it to `tests/fixtures/r24-size-census.py`).
CLI: `python3 -B tests/fixtures/r24-size-census.py --tool <path-to-tool>`; last stdout line
`cases=C pass=P control=FALSE-GREEN-REJECTED|FALSE-GREEN-ACCEPTED lost_found=WRITE-DETECTED|NOT-DETECTED`;
exit 0 iff P==C and both flags are the first spelling. Implement EXACTLY the frozen 8-case set in
the preregistration (read it), each case in its own repo under a `/var/tmp` mkdtemp (hard-code
/var/tmp), removed in a finally block. Manifest = sorted (relpath, type, mode, size, mtime_ns,
sha256-for-regular-files) over the resolved .git dir; atime/ctime excluded. Case 8 writes its own
stub emitter script to scratch and runs it through cases 2-5. Print one `CASE <n> <name>
PASS|FAIL <detail>` line per case. Tool CLI it targets (the L1 writes the tool in parallel):
{SIZE_CLI}
Exercise your fixture against a tiny reference tool you write in your scratch (and against the
stub) and paste both runs; never run anything against the lane or fleet repo.""")

    add("ProbeLinkedModes", "executor", f"""Hypothesis (from staged entry `{KPKG}/garbage-false-positive-modes-r25.md`): on git 2.56.0
`git -C <linked> count-objects -v` reads `garbage: 1` for ALL five creation modes (`--detach`, `-b
<b>`, `--orphan <b>` (check the exact flag spelling in `git worktree -h`), `--detach`+commit,
`-b`+commit), with `size-garbage: 0`, and the main worktree reads 0. Run the matrix in
`/var/tmp/souji-r24-ProbeLinkedModes/` and paste per-cell output (garbage, size-garbage, stderr
warning path, `ls` of the private gitdir). Also read the same repo with `--git-dir=<common dir>` per
cell. Verdict: hypothesis holds / falsified per cell. This decides whether the r25 entry can be
admitted on lane-produced evidence.""")

    add("ProbeGarbageKinds", "executor", f"""Hypothesis (staged `{KPKG}/garbage-false-positive-modes-r26.md`): a stray file or directory directly
in `objects/` is NOT counted as garbage, while a junk file in `objects/pack/` and an invalid name in
`objects/<2hex>/` ARE counted; `size-garbage` is in KiB and rounds small files to 0. Probe in
`/var/tmp/souji-r24-ProbeGarbageKinds/`: each planting alone, then a 10 KiB junk file in
objects/pack (does size-garbage become 10?), a `tmp_obj_*` file in objects/<2hex>/, a `.keep`/
`.promisor`/`.bitmap` orphan in pack/. Paste outputs and stderr per cell. Verdict per cell.""")

    add("ProbeFsckWrites", "executor", f"""Hypothesis: on git 2.56.0, `git --git-dir=<common> fsck --unreachable --no-reflogs --no-progress`
leaves the .git tree byte-identical (path, type, mode, size, mtime, sha256 of regular files) on (a)
a clean repo, (b) a repo with one dangling blob, (c) a repo with a linked worktree; and `git fsck
--lost-found` on (b) creates `.git/lost-found/other/<oid>` holding the blob CONTENT. Also check
whether `count-objects -v` alone changes anything, and whether either command touches
`.git/index` or `.git/objects/info/commit-graph` mtimes. Probe in `/var/tmp/souji-r24-ProbeFsckWrites/`
with your own manifest script; paste manifests' diffs. Verdict per command.""")

    add("ProbeAlternates", "executor", f"""Hypothesis: `git count-objects -v` on a repo whose `objects/info/alternates` names one other object
dir prints an `alternate: <path>` line (check exact spelling and whether the path is absolutized),
and `fsck --unreachable --no-reflogs` does not report objects that only live in the alternate as
unreachable. Also: does a comment line (`#`) or blank line in alternates appear? Probe in
`/var/tmp/souji-r24-ProbeAlternates/`; paste outputs. Verdict per clause; recommend how the tool
should count alternates (file lines vs `alternate:` output lines).""")

    add("SentinelSizeEnvelope", "sentinel", f"""Adversarial review of the C1 read-only envelope BEFORE the tool lands (contract in the
preregistration; model `{LANE}/tools/souji-repo-structure.sh`). Which repository-controlled config can
make `git count-objects -v` or `git fsck --unreachable --no-reflogs` execute a program or write
(e.g. `core.fsmonitor`, `core.hooksPath`, `fsck.*`/`fsck.skipList`, `core.sshCommand`, `protocol.*`,
`include.path`, `safe.directory`, `GIT_CONFIG_*`, `uploadpack.*`, partial-clone promisor fetch,
`core.alternateRefsCommand`)? For each: does it apply to these two commands on git 2.56.0 (cite the
git doc section you opened, <=25-word quote), and which env/`-c` override neutralizes it. Probe any
doubtful one in `/var/tmp/souji-r24-SentinelSizeEnvelope/` with a harmless marker command. Deliver a
ranked list with the exact overrides the tool must carry.""")

    add("SimplSizeVsStructure", "simplifier", f"""YAGNI check for C1: does the planned `tools/souji-size-census.py` (preregistration CLI) duplicate
`{LANE}/tools/souji-repo-structure.sh` or `tests/fixtures/r13-repo-structure.sh`? Which helper
(manifest function, promisor refusal, envelope) should be shared or copied, and what should NOT be
added (e.g. size attribution, per-pack listing)? Deliver keep/merge/omit per piece with line
estimates, and the minimal manifest function (paste it) both fixtures could use.""")

    # ---------------- C1 sources / assimilation ----------------
    add("ScoutPathC", "scout", f"""Open git.git `path.c` at tag v2.56.0 live (e.g.
https://github.com/git/git/blob/v2.56.0/path.c or https://raw.githubusercontent.com/git/git/v2.56.0/path.c;
also check https://git.kernel.org/pub/scm/git/git.git/tree/path.c?h=v2.56.0) and at v2.30.0. Deliver: the
`struct common_dir` definition with its field comments, the `common_list[]` entries for `refs`,
`logs`, `logs/HEAD`, `gc.pid` with line numbers at each tag, a <=25-word located quote of the
`ignore_garbage` comment, and `report_linked_checkout_garbage()`'s body summary with line numbers.
Access date 2026-10-25. State the exact URL you would put in a SOURCES row and whether the two tags
agree. No pipe characters in quotes.""")

    add("ScoutCountObjectsC", "scout", f"""Open git.git `builtin/count-objects.c` at tag v2.56.0 live (github or git.kernel.org). Deliver
with line numbers: where `report_linked_checkout_garbage` is called and under what condition; how
`garbage` and `size_garbage` are accumulated (loose `objects/<2hex>/` non-object names, pack-dir
garbage via `report_garbage`/`report_pack_garbage` in `packfile.c` — open that too); whether a stray
file directly in `objects/` is ever scanned; the unit of `size-garbage` (KiB rounding). <=25-word
located quotes, access date 2026-10-25, exact URLs for SOURCES rows. No pipe characters in quotes.""")

    add("ScoutWorktreeDoc", "scout", f"""Open https://git-scm.com/docs/git-worktree live; find § DETAILS (per-worktree files under
`$GIT_DIR/worktrees/<id>`, which refs are per-worktree: `refs/bisect`, `refs/worktree`,
`refs/rewritten`) and § "REFS" or equivalent. Deliver <=25-word located quotes that explain WHY a
linked worktree's private gitdir carries a `refs` directory, with the section name, page "last
updated" version and access date 2026-10-25; compare `man git-worktree` installed (git 2.56.0).
Also open https://git-scm.com/docs/gitrepository-layout § `worktrees/<id>` and quote what it lists.
No pipe characters in quotes.""")

    add("ScoutPkgEntries", "scout", f"""Read-only over the staged package. For each of `{KPKG}/garbage-false-positive-modes-r25.md`,
`-r26.md`, `-r27.md` and `{KPKG}/count-objects-garbage-semantics-r23.md`: list every `source:` id, the
matching row in `{PKG}/SOURCES.append.md` (title, URL/path, tier), whether that source is an external
URL a lane can re-open or an own-work path living in shokuknow (`lanes/souji/round*/...`), and every
factual claim in the entry body with whether it is (a) lane-reproducible by a /var/tmp probe, (b)
upstream-source-checkable, (c) a fleet claim (refused: the lane never claims fleet figures). Also read
`{PKG}/MERGE-REPORT.md` for what it says about these entries. Recommend ADMIT/REJECT per entry with
the reason and a flip condition for each reject.""")

    add("ScoutCollisionMap", "scout", f"""The id-collision check ran at round start: `{LANE}/.ufo/waves/round-24/assimilation/{{reg-ids,staged-ids,collisions}}`
(11 collisions). For EACH colliding id show the lane row's title/URL (`{LANE}/corpus/SOURCES.md`) vs
the staged row's title/URL (`{PKG}/SOURCES.append.md`), and mark same-document / different-document.
Then prove the 0-3-space guard: build a scratch registry under `/var/tmp/souji-r24-ScoutCollisionMap/`
with an indented `  | S120 |` row, show a column-zero-only pattern misses it and the frozen
`'^ {{0,3}}\\|[[:space:]]*S[0-9]{{3,}}'` pattern catches it. Paste commands and outputs. Next free lane id
is the max lane id + 1: state it.""")

    add("ScoutSliceWeb", "scout", f"""Hand-check quarantine-slice rows (register `{SK}/.ufo/waves/corpus-expansion-1/absent-defect-register.md`,
read-only; slice at `{LANE}/.ufo/waves/round-24/assimilation/quarantine-slice`) for the staged ids whose
cited source is a WEB page: look each id up in `{PKG}/SOURCES.append.md` (expected web: S114, S118,
S126, S138 — verify), fetch the URL live, and locate the row's quoted text. Per row: id, URL,
reachable?, quote found verbatim? (paste the located <=25-word quote or the nearest text),
verdict `present` / `absent (fabrication class)` / `unverifiable (unreachable)`. Never edit the
register or any shokuknow file.""")

    add("ScoutSliceOwnWork", "scout", f"""Hand-check quarantine-slice rows whose cited source is an OWN-WORK path (expected S123, S124, S131,
S133 — verify in `{PKG}/SOURCES.append.md`; register `{SK}/.ufo/waves/corpus-expansion-1/absent-defect-register.md`).
For each: does the cited path exist anywhere under `{SK}` (find it read-only), does its content
carry the row's claimed figure/quote, and does a digest the row names match `sha256sum`? Verdict per
row: `present` / `absent (fabrication class)` / `unverifiable`, plus whether the evidence lives in
lane bytes (it does not, so note `not lane-re-derivable`). Never edit anything.""")

    add("ScoutRegistry", "scout", f"""Measure the registry baseline at the lane tip: run
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
(exit code + last 5 lines), the row count `grep -cE '^ {{0,3}}\\|[[:space:]]*S[0-9]{{3,}}[[:space:]]*\\|' {LANE}/corpus/SOURCES.md`,
max id, tier histogram and status histogram, and every row whose URL contains `git-scm.com/docs/git-worktree`,
`gitrepository-layout`, `path.c` or `count-objects` (to avoid within-scope duplicate URLs, W04/E04).
Read `/home/vgpnk/Projects/shokunin/CORPUS.md` § SOURCES.md and quote the exact 11-column header and
the allowed `recheck` forms. Paste commands and outputs.""")

    # ---------------- C2 build ----------------
    add("ExecCoverageTool", "executor", f"""Write the C2 tool draft at `{LANE}/.ufo/waves/round-24/w1/souji-coverage-agreement.py`
(the L1 copies it to `tools/souji-coverage-agreement.py`). Frozen contract: preregistration C2 — read it
verbatim. CLI `python3 -B tools/souji-coverage-agreement.py --root <repo> --rev <full40>`; reads ONLY
committed bytes via `git -C <root> show <rev>:<path>` and `git ls-tree` (never the working tree);
refuses a non-40-hex rev (exit 2). Table detection: markdown tables in `corpus/README.md` whose
header row's first cell is `ground` and third header cell begins `entries` (case-insensitive,
trimmed); a table row's ground cell starts with token F<k> when it matches `^F[0-9]+(?=[ \\-]|$)`.
Paths: backticked spans in the entries cell; a span counts as a knowledge path when it ends with
`knowledge/<name>` (`../`-prefixed or not). Entries with ground: `corpus/knowledge/*.md` whose
front-matter (lines before the first `# ` heading) has `^ground:\\s*F([0-9]+)`. Output rows
`MISMATCH\\t<class>\\t<path>\\t<detail>` then counts `grounded=G mapped=M dangling=D mismatches=X`
(mapped = grounded entries found in a matching row); exit 0 iff X==0, 1 otherwise. Stdlib only,
<=160 lines. Run it against the lane READ-ONLY at `--rev {BASE}` and paste the output (that is the
control preview; the L1 re-runs it).""")

    add("ExecCoverageFixture", "executor", f"""Write the C2 fixture draft at `{LANE}/.ufo/waves/round-24/w1/r24-coverage-agreement.py` (the L1
copies it to `tests/fixtures/r24-coverage-agreement.py`). CLI `python3 -B tests/fixtures/r24-coverage-agreement.py
--tool <path>`; builds synthetic git repos under a `/var/tmp` mkdtemp (git init/add/commit INSIDE
scratch only, removed in finally) and runs the tool with `--root <scratch> --rev <full40>`. Cases
(each with the expected counts line): (1) clean map → mismatches=0; (2) grounded entry absent from
map → MISSING-FROM-MAP 1; (3) entry named only in the STATUS column (not entries) → 1; (4) entry
named in a row of a different ground (F3 row for an F2 entry) → 1; (5) map path to a missing file →
DANGLING-MAP-PATH 1; (6) `F2 caveat` row counts as ground F2 / `F21` row does NOT count as F2; (7)
working-tree fix not committed → still 1 (rev-scoped); (8) entry without a ground line → not
grounded, not a mismatch; (9) non-40-hex rev → exit 2. Last line `cases=C pass=P control=FALSE-GREEN-REJECTED|ACCEPTED`
where the control is an always-zero emitter (`grounded=0 mapped=0 dangling=0 mismatches=0`, exit 0)
run through the same cases. Contract details: preregistration C2. Exercise it on a reference tool
you write in scratch and paste the run.""")

    add("ScribeReadmeMap", "scribe", f"""Draft the corpus/README.md append for round 24 (deliver at `{LANE}/.ufo/waves/round-24/w1/ScribeReadmeMap.md`).
It must be an APPEND (`## Round 24 — …` section; never rewrite older sections) carrying a coverage-map
table with header `| ground | status | entries / runnable evidence |` whose F2 row's ENTRIES cell names
every F2 entry as a backticked `knowledge/<file>.md`: `git-repo-structure-readonly.md`,
`repo-size-census-readonly.md`, `count-objects-garbage-readings-r25.md`, plus the round-24
assimilated entry `count-objects-linked-worktree-garbage.md` (placeholder name; the L1 confirms) and
runnable evidence `../tools/souji-size-census.py`, `../tests/fixtures/r24-size-census.py`; and an F4
row only if F4's existing row would otherwise miss an entry (check `{LANE}/corpus/README.md` lines
34-43). Also a `### Frontier (r24)` list (F2 next step after the write-safety fixture) and a one-line
answer to the r23 spot-check's routed defect. Verify every path you name exists at the lane tip
or is one of the named round-24 deliveries.""")

    # ---------------- C3 build ----------------
    add("ExecReceiptVerify", "executor", f"""Implement C3 in a COPY: copy `{LANE}/tools/souji-receipt-run.py` to
`{LANE}/.ufo/waves/round-24/w1/souji-receipt-run.py` and edit only `cmd_verify` (and the docstring's
refusal list): (a) refuse with exit 2 `RECEIPT-REV-NOT-DURABLE` when `durable_rev(root, rev)` is false
(the same predicate `run` uses); (b) refuse `RECEIPT-TOOL-NOT-IN-ARGV` when the receipt's `tool=` value
is not an element of `shlex.split(cmd)` (exact element match; state whether `./tools/x` counts). Keep
every other behaviour byte-identical. Deliver also `w1/souji-receipt-run.diff` (unified diff vs the
lane file). Then, READ-ONLY against the lane, run the patched copy's `verify --root {LANE}` on the
five committed r23 receipts (`{LANE}/census/round-23/records/{{declared-evidence-after,gate-check-at-first-landing,gate-check-at-lane-base,gate-check-c3,agreement-after}}.tsv`)
and paste each result (must stay verify=ok). Any refusal is a finding, not something to patch around.""")

    add("ExecReceiptFixture", "executor", f"""Write the C3 fixture draft at `{LANE}/.ufo/waves/round-24/w1/r24-receipt-verify.py` (the L1 copies it to
`tests/fixtures/r24-receipt-verify.py`). CLI `python3 -B tests/fixtures/r24-receipt-verify.py --tool <runner>
[--lane-root <path>]`. Frozen cases (preregistration C3): (a) non-durable rev → exit 2
`RECEIPT-REV-NOT-DURABLE`: in a /var/tmp scratch repo, make a commit, run the runner's `run` to get a
valid receipt, then point a copy's rev at a commit object reachable from no ref (e.g. `git commit-tree`
output never stored in a ref) whose tree holds the same tool bytes; (b) `tool=` not in `cmd=` argv →
exit 2 `RECEIPT-TOOL-NOT-IN-ARGV`; (c) clean receipt from `run` → exit 0; (d) the five committed r23
receipts under `<lane-root>/census/round-23/records/` verify exit 0 (skip-with-FAIL if lane-root absent).
Last line `cases=C pass=P refusals=R/2 regress=N/5`, exit 0 iff P==C. Read the runner's real CLI and
receipt format in `{LANE}/tools/souji-receipt-run.py` and `{LANE}/tests/fixtures/r23-receipt-run.py`.
Run the fixture against the CURRENT lane runner (expect refusals=0/2: that is the control) and paste.""")

    add("RevR23Residuals", "revenger", f"""Reconstruct from committed bytes every residual limit round 23 named for its C1/C2 instruments
(`{LANE}/corpus/lessons/round-23.md`, `{LANE}/LOG.md` Round23, `{LANE}/SCORECARD.md`, `.ufo/waves/round-23/w2/W2C2Verify.md`,
`W2K1.md`, `MutReceipt.md`). For each: quote it, say whether it is actable without an operator ruling,
and whether C3 (preregistration) closes it, partially closes it, or leaves it open. Specifically
confirm by reading `cmd_verify` and `durable_rev` that (i) verify does not call durable_rev today and
(ii) the `tool=` label is not checked against argv. Read-only.""")

    add("MutRunnerPlan", "mutation-tester", f"""Plan the mutation set for C3 before it lands: for the two new verify clauses (preregistration C3) and
the existing ones in `{LANE}/tools/souji-receipt-run.py` `cmd_verify`, write one mutant per clause
(as a unified diff snippet) and name the fixture case (a/b/c/d of C3, or r23 fixture case) that must
kill it. Then actually run your mutants against the CURRENT r23 fixture `{LANE}/tests/fixtures/r23-receipt-run.py`
using copies in `/var/tmp/souji-r24-MutRunnerPlan/` (never edit the lane) and report killed/survived,
so the L1 knows which clauses only the new fixture covers. `uncovered=<n>` line at the end.""")

    # ---------------- frontier step / records ----------------
    add("ScribeEntry", "scribe", f"""Draft the assimilated F2 entry at `{LANE}/.ufo/waves/round-24/w1/ScribeEntry.md` (proposed lane path
`corpus/knowledge/count-objects-linked-worktree-garbage.md`). Input: staged `{KPKG}/garbage-false-positive-modes-r25.md`
and `-r27.md` (READ-ONLY), and the reports of ScoutPathC, ScoutCountObjectsC, ScoutWorktreeDoc,
ProbeLinkedModes, ProbeGarbageKinds in `{LANE}/.ufo/waves/round-24/w1/` once they exist (wait for
them by re-reading; if absent when you finish, mark the gaps `[PENDING <seat>]`). Shape: copy the
front-matter style of `{LANE}/corpus/knowledge/repo-size-census-readonly.md` (`source:` lines with
`S<id> — URL — § locator`, `verified-at: 2026-10-25`, `recheck:` ISO date / `NNd` / symbolic,
`ground: F2 — …`), body claims each backed by a re-opened upstream source or a lane fixture case, a
`## What this does NOT establish` section (no fleet figure), and a `## Gate` block with ≥1 ADMIT and
≥1 REJECT (reason + flip) per `{LANE}/corpus/QUALITY.md` (read it: Q1/Q2/Q54 locator rules). Use
placeholder ids S120.. and name the URL per id so the L1 re-points by document.""")

    add("ScribeSourcesRows", "scribe", f"""Draft the SOURCES.md append block for the round's opened sources (deliver at
`{LANE}/.ufo/waves/round-24/w1/ScribeSourcesRows.md`). Exactly the 11-column schema of
`{LANE}/corpus/SOURCES.md` (copy its header; read `/home/vgpnk/Projects/shokunin/CORPUS.md` § SOURCES.md
for the cell rules: valid ISO/`NNd`/symbolic recheck, no `|` in any cell, `used-by` = the citing
entry/tool paths, status `mined`). Rows: git.git path.c@v2.56.0, builtin/count-objects.c@v2.56.0
(+ packfile.c if the scout used it), git-worktree DETAILS, gitrepository-layout worktrees/<id> — URLs
and quotes taken from the scout reports in `{LANE}/.ufo/waves/round-24/w1/` (if absent, mark
`[PENDING]`). Number from the next free lane id (max id in the lane registry + 1). Also draft the
lesson's Gate lines (URL, access date 2026-10-25, ≤25-word quote) for each row.""")

    add("ScribeLessonMistakes", "scribe", f"""Mine mistakes for `corpus/lessons/round-24.md` `## Mistakes` (deliver at `{LANE}/.ufo/waves/round-24/w1/ScribeLessonMistakes.md`).
Columns: class · evidence pointer · captured-by (the QUALITY criterion or rule that should have
caught it, or `none`) · fix · failure witness (the fix counts only once shown able to fail). Sources:
`{LANE}/corpus/lessons/round-23-verifier-spotcheck.md` (routed: F2 coverage-map table not updated while
its prose was — the C2 tool is the proposed fix; witness = the tool at base rev reports ≥1), the r23
lesson's own Mistakes and wave-2 falsifications, and the round-23 `W2*` reports. Also read
`{LANE}/corpus/QUALITY.md` and propose ONE new criterion (Q-next) if a mistake has captured-by `none`,
with its lesson pointer. No invented evidence: every pointer is a path:line you opened.""")

    add("ScoutInherited", "scout", f"""Classify inherited lane state: `git -C {LANE} status --porcelain` shows ` M .ufo/waves/round-23/w2/W2K1.md`
and `?? census/operator-sweep-20261019/` (operator-owned: never read its contents, never staged).
For W2K1.md: `git -C {LANE} diff -- .ufo/waves/round-23/w2/W2K1.md` — is it a genuine late seat update
(content hunks) by the round-23 seat W2K1 (which may still be running), and does anything committed in
round 23 cite the old vs new text? Recommend commit-under-round-24-as-inherited or leave-for-author,
with reason. Also check `{FLEET}/.ufo/watchdog.log` for any `lane-dead-no-report souji round=24`
line (read-only grep). Do not stage, commit or revert anything.""")

    add("ConnSiblings", "connector", f"""Sibling-overlap scan, read-only. Search the other lane repos under `{FLEET}/*-shokunin/` (NOT souji) for
(1) size/debris census tools or knowledge on `count-objects`, `fsck --lost-found`, linked-worktree
garbage; (2) receipt verifiers with durable-rev or argv binding; (3) coverage-map / README map
agreement checkers. Use `grep -rl` limited to `tools/ corpus/knowledge/ tests/` of each lane. For each hit:
lane, path, what it does, and whether souji round 24 should reuse, cite, or deliberately differ.
Also name cross-axis patterns (e.g. the same manifest function, the same refusal codes). Never write
outside your report.""")

    # ---------------- first falsifiers ----------------
    add("CritPrereg", "critic", f"""Falsify `{PREREG}` against the round contract (`{FLEET}/.ufo/prompts/souji-round-24.md` §2, §9,
§10) and `{FLEET}/AXES.md`. Check: causal separability of C1/C2/C3 (note the C1-entry-in-map coupling
the preregistration discloses — is it a separability defect?); one concrete after-value per claim,
re-derivable by one command; universal clauses without enumeration; lowest-axis obligation;
axis named by surface; a do-nothing control per claim that cannot meet the target; assimilation as
claim-slot abuse; whether C3 is operability or merely calibration of records. Label each amendment
`pre-data-legal` or `would-invalidate`.""")

    add("CritC1Control", "critic", f"""Attack C1's frozen case set (preregistration). Can a tool that skips the claimed work pass 8/8?
Build the cheapest cheaters in `/var/tmp/souji-r24-CritC1Control/` against the CASE DEFINITIONS (not
the fixture, which may not exist yet): an always-zero stub; a tool that runs `git -C PATH
count-objects -v` without the common-dir discount; a tool that uses `fsck --lost-found` then deletes
lost-found (does the manifest catch the mtime/dir change?); a tool that parses `count-objects`
human output loosely. For each: which case kills it, or which case is missing. Also: is case 4's
witness (raw linked garbage: 1) host-stable? Is the manifest sensitive enough (directory mtimes)?""")

    add("CritC2Gameable", "critic", f"""Attack C2 (preregistration). Ways to reach mismatches=0 without real agreement: delete or rename
`ground:` lines (kill rule only guards the count); name an entry in a junk row starting `F2`; add
a row whose ground cell is `F2 caveat`; put the name in a non-entries column; DANGLING paths written
without backticks; tables outside the coverage-map header shape. For each: does the frozen predicate
catch it, and does it matter? Also run the control: compute by hand (read-only grep at
`git -C {LANE} show {BASE}:corpus/README.md` and `ls-tree {BASE} corpus/knowledge/`) the expected base
mismatches and list them, so the L1 can check the tool's control output.""")

    add("CritC3Value", "critic", f"""Attack C3 (preregistration). Is refusing a non-durable rev in `verify` a real operability gain or a
new false-refusal risk (e.g. receipts whose rev later becomes unreachable after a rebase/jj rewrite
of an unpushed commit; shallow clones; a verifier run in a clone that lacks the ref)? Is
`tool=`-in-argv exact-match too strict (`./tools/x`, `python3 -B tools/x`, absolute paths) or too
weak (a tool named in argv but not executed, e.g. as a `--file` value)? Check
`{LANE}/tools/souji-receipt-run.py` and every receipt under `{LANE}/census/` (`grep -rl '^receipt=v1'`)
for ones the new rules would refuse. Deliver: kept / harmed list.""")

    add("ReviewQualityBar", "reviewer", f"""Review the round's admission bar: read `{LANE}/corpus/QUALITY.md` fully and list the criteria a new
F2 knowledge entry and a new SOURCES row must pass (Q-ids + one-line test each), especially Q1/Q2
(located quotes), Q54 (`§ <NAME>` locator must appear in the Gate's own snapshot), and any snapshot
rule (r23 committed snapshots under `census/round-23/sources/` with SHA256SUMS). Then state what the
L1 must commit this round for the planned entry (snapshots of path.c / count-objects.c / git-worktree
pages?) and run `python3 -B {LANE}/tools/souji-gate-check.py --help` to give the exact gate command for
the new entry (read-only).""")

    add("ReviewAxesTrend", "reviewer", f"""Read `{FLEET}/AXES.md`, `{FLEET}/LEARNING.md` (trend verdicts: expansion/quality/discernment) and
`{LANE}/SHONEN.md`. Deliver: (1) the exact rule for `improved` per trend and what round 24 would need
to show for each given the planned claims (the r23 closure graded expansion and quality
`unprovable-but-better` — why, and what would change that); (2) the SHONEN boxes the round touches
with current state; (3) whether F2 entries 3→4 counts as expansion on ground the map did not hold
(r23 closure said no) and what WOULD count (e.g. a new edge class). Quote lines.""")

    add("ScoutLaneMeasure", "scout", f"""Prepare the lane-bound C1 measurement, read-only: on the LANE repo only (`{LANE}`), run
`GIT_OPTIONAL_LOCKS=0 git -c maintenance.auto=false -C {LANE} count-objects -v` and
`git -C {LANE} rev-parse --path-format=absolute --git-common-dir`, `git -C {LANE} worktree list
--porcelain`, and whether `objects/info/alternates` exists. Do NOT run fsck on the lane (the L1
runs the tool). Report the fields and whether the lane is jj-colocated (does `.jj/` exist; are there
`refs/jj/keep/*` refs: `git -C {LANE} for-each-ref --count=5 refs/jj/`), since the r17 section notes
colocation inflates structure counts. State what a reader must NOT infer from a lane figure.""")

    add("ScoutMisrootEarly", "scout", f"""Early misroot sweep: `git -C {FLEET} status --porcelain` (no pathspec). For each untracked entry,
decide whether it names souji round 24 (grep its content for `souji` and `round-24`), another lane,
or orchestrator run state. `{FLEET}/.scratch/` is orchestrator-owned and is NEVER a misroot: do not
read it. Deliver a table path/owner/action. Do not delete, move or copy anything.""")

    add("ScoutTrendEvidence", "scout", f"""Find quality-trend evidence the round could legitimately produce: LEARNING's quality observable is
corpus-entry re-verification / deepening / supersession. For each of the three current F2 entries
(`{LANE}/corpus/knowledge/{{git-repo-structure-readonly,repo-size-census-readonly,count-objects-garbage-readings-r25}}.md`)
list each `recheck:` value and whether it is due, and which entry claim the C1 fixture would
re-verify empirically (e.g. repo-size-census-readonly's `--lost-found` WRITES claim = case 7). Deliver
a table entry/claim/case/currently-verified-by. Read-only.""")

    add("ReviewRepoStructureFixture", "reviewer", f"""Review `{LANE}/tests/fixtures/r13-repo-structure.sh` (the existing F2 write-safety fixture for `git repo
structure`) as the precedent C1 extends: its manifest definition, detector controls, and the r13
lesson notes on it (`{LANE}/corpus/lessons/round-13*.md`). Is it actually executed anywhere with a
committed PASS? (search `{LANE}/census/` and `{LANE}/tests/results/` for its output.) List the r13
fixture's weaknesses C1's fixture must not repeat. Do not run it against the lane; you may run it if
it only touches /var/tmp (read it first) and paste the result.""")

    return {
        "wave": "souji-r24-w1",
        "reportDir": ".ufo/waves/round-24/w1",
        "maxLanes": 64,
        "context": context(goal),
        "items": ITEMS,
    }


TIP = "ca7fc1cb6dd1333096c6f3bdbad304686691d126"
AFTER = "778747eb671f8e85ef5387bc3d7023337b30467c"
INSTR = "1efe406e7f39b8fe736be2a566053703a571ffc0"
AMEND = f"{LANE}/.ufo/waves/round-24/preregistration-amendment-1.txt"
REC = f"{LANE}/census/round-24/records"


def wave2() -> dict:
    goal = (f"Souji round 24, wave 2 (FALSIFY). Every item attacks one landed artifact; a seat that cannot "
            f"falsify says `survives` with the commands it ran. Frozen contract: {PREREG} plus the append-only "
            f"{AMEND} (stricter-only, written before any control/after receipt). Landed: instruments "
            f"{INSTR}; control receipts ce5971c9fe7a04f958f06c7b1933e07ffbc9ddd3; after-state {AFTER}; "
            f"after-receipts {TIP} (lane tip; read it with `git -C {LANE} rev-parse master`). Receipts live in "
            f"{REC}/ and verify with `python3 -B {LANE}/tools/souji-receipt-run.py verify --root {LANE} <receipt>`. "
            f"Wave-1 reports: {LANE}/.ufo/waves/round-24/w1/. Lane base {BASE}.")
    ITEMS.clear()
    w = "w2"
    # ---------------- C1 ----------------
    add("W2C1Rerun", "reviewer", f"""Attack C1's after-state. In a `/var/tmp` clone of the lane at {TIP} (`git clone --no-local {LANE}`; never run
in the lane), run `python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py` and verify
`{REC}/c1-after.tsv` and `{REC}/c1-control-stub.tsv` with the runner. Does the tip reproduce `cases=8 pass=8
control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, and does the stub control at {INSTR} reproduce `pass=4`
without the target line? Compare per-CASE lines with the receipt. Verdict survives/falsified.""", w)
    add("W2C1MutTool", "mutation-tester", f"""Mutation-test C1's TOOL against its fixture. Copy `{LANE}/tools/souji-size-census.py` and
`tests/fixtures/r24-size-census.py` (at {TIP}) to `/var/tmp/souji-r24-W2C1MutTool/`. One mutant per clause: common-dir
read (use -C PATH), alternates from file lines, no .promisor-pack refusal, no top-level check, env passthrough
(caller env), no timeout, no core.fsmonitor override, size_garbage hard-coded 0, unreachable from `--dangling`,
warning lines treated as failures, stderr ignored. Run the fixture per mutant; table clause/mutant/killed-by-case or
SURVIVED, `uncovered=<n>`. Survivors are findings, not edits.""", w)
    add("W2C1MutFixture", "mutation-tester", f"""Mutation-test C1's FIXTURE (`{LANE}/tests/fixtures/r24-size-census.py` at {TIP}): weaken each
assertion (manifest without directories; whole-second mtimes; case 3 without size check; case 4 witness read before
the tool; case 6 without the promisor-unset arm; case 7 detector skipped; case 8 control requiring 0 failures) and
show whether the weakened fixture still FAILS the stub and a known-bad tool (e.g. the plain `git -C PATH
count-objects -v` cheater). A weakening that changes no outcome = the assertion is untested. Scratch only.""", w)
    add("W2C1Envelope", "sentinel", f"""Re-attack the hardened C1 envelope (`{LANE}/tools/souji-size-census.py` at {TIP}; read its docstring and
`{LANE}/.ufo/waves/round-24/w1/SentinelSizeEnvelope.md`). In `/var/tmp/souji-r24-W2C1Envelope/` repos with a harmless
`touch` marker program, try: repo `core.fsmonitor=<marker>`, caller `GIT_EXEC_PATH`/`GIT_CONFIG_COUNT`/
`GIT_CONFIG_PARAMETERS`/`GIT_TRACE2_EVENT`/`GIT_DIR` set, a poisoned PATH `git`, `include.path` to a FIFO (expect
exit 1 after the timeout — you may patch TIMEOUT_S in a scratch COPY to 5 s to test), `core.alternateRefsCommand`,
`uploadpack.packObjectsHook`. Any marker fired or any write = finding. Paste each probe.""", w)
    add("W2C1TopLevel", "critic", f"""Attack the new `--repo must be the top level` refusal in `{LANE}/tools/souji-size-census.py` ({TIP}).
Does it refuse legit inputs (bare repo given as its git dir, bare repo given as its parent, a symlinked path to the
top level, trailing slash, a linked worktree, a repo whose top level contains a symlink) and does it still let an
enclosing repo through (path under a non-repo dir inside a repo; `GIT_CEILING_DIRECTORIES` not set)? Scratch repos
only. Table input/expected/got. Is the C1 fixture blind to any regression here?""", w)
    add("W2C1LaneMeasure", "reviewer", f"""Attack `{LANE}/census/round-24/size-census-lane.txt` (the lane-bound C1 measurement). Is its rev/tool_sha256
header true (`git -C {LANE} show {AFTER}:tools/souji-size-census.py | sha256sum`)? Is `unreachable=1093` correctly
described (jj keep refs, cruft pack, `--no-reflogs`; `.ufo/waves/round-24/w1/ScoutLaneMeasure.md`), and does any
lane record turn it into a fleet figure or a cleanup recommendation? Re-run the tool read-only on the lane ONCE and
explain any drift. No fsck --lost-found, no writes.""", w)
    add("W2C1Axis", "critic", f"""Attack C1's axis naming (§9 of `{FLEET}/.ufo/prompts/souji-round-24.md`): is C1 coverage (F2 frontier →
a new tool + operation class) or quality (re-scoring a rule the lane holds)? Read `{LANE}/corpus/README.md` § Round 24
and `### Frontier (r23)`, and AXES.md. Name the command that would show the surface unmoved and run it at {BASE} and
{TIP}. Verdict: coverage-move holds / mislabelled.""", w)
    add("W2C1Amend", "critic", f"""Attack the amendment discipline. Diff `{PREREG}` against `{AMEND}` and the fixture bytes
(`git -C {LANE} show {INSTR}:tests/fixtures/r24-size-census.py`). Is every amendment stricter-only (no case dropped,
no expected value loosened)? Were any after-receipts created before the amendment commit (`git log` order of
{INSTR}, ce5971c, {AFTER}, {TIP})? Were the L1's disclosed sanity runs claim data in disguise? Verdict + list.""", w)
    # ---------------- C2 ----------------
    add("W2C2Rerun", "reviewer", f"""Attack C2's after-state. Run `python3 -B {LANE}/tools/souji-coverage-agreement.py --root {LANE} --rev {TIP}` and
`--rev {BASE}`, verify `{REC}/c2-after.tsv`, `c2-control-base.tsv`, `c2-fixture-after.tsv`. Then apply the amended
per-entry kill rule yourself: list every entry with a `ground: F<k>` line at {BASE} and at {TIP} (`git show`), and
confirm none disappeared or changed F<k>. Verdict per check.""", w)
    add("W2C2Mut", "mutation-tester", f"""Mutation-test C2: copy `tools/souji-coverage-agreement.py` and `tests/fixtures/r24-coverage-agreement.py`
(at {TIP}) to scratch; mutants: entries column index off by one, status column counted, F-token prefix match (F2
matches F21), front-matter read past the first heading, working-tree read, dangling check off, escaped `\\|` split,
only first table read. Fixture kills? Then also run each mutant at the real lane {BASE} and {TIP}: which mutants
change the claim's numbers? `uncovered=<n>`.""", w)
    add("W2C2Game", "critic", f"""Attack how C2 reached 0. `git -C {LANE} diff {BASE} {TIP} -- corpus/README.md corpus/knowledge/` : the
README gained a Round 24 table whose F2 row lists all F2 entries, and `git-repo-structure-readonly.md` gained a
`ground: F2` line. Is either a game (a row that disclaims the capability, a ground line that is false, a superseded
row left unmarked like README line 40 "frontier, no entry")? Does the new F2 row's status prose match the landed
bytes? Verdict: real agreement / gamed, with lines.""", w)
    add("W2C2Calib", "critic", f"""Attack C2's axis: §9 says a calibration claim counts mismatches between the lane's self-assessment
(SCORECARD/SHONEN) and observed repo state. C2 uses the corpus/README.md coverage map. Read `{FLEET}/AXES.md`
(calibration definition) and `{LANE}/SCORECARD.md`. Is the coverage map a self-assessment surface? Would the operator
accept it as the lowest-axis claim? Give the strongest case both ways and your ruling.""", w)
    # ---------------- C3 ----------------
    add("W2C3Rerun", "reviewer", f"""Attack C3's after-state. In a `/var/tmp` clone at {TIP}, run `python3 -B tests/fixtures/r24-receipt-verify.py
--tool tools/souji-receipt-run.py --lane-root .` and the same with the base runner (`git show {BASE}:tools/souji-receipt-run.py`).
Then verify EVERY receipt in the lane (`grep -rl '^receipt=v1' census/`) with the tip runner and with the base runner;
any receipt the tip refuses that the base accepted (other than intended) is a C3 harm. Paste the table.""", w)
    add("W2C3Mut", "mutation-tester", f"""Mutation-test the C3 runner changes (`git -C {LANE} diff {BASE} {TIP} -- tools/souji-receipt-run.py`): one mutant
per new clause (verify durable check, verify argv check, verify command_refusal mirror, MALFORMED on shlex error,
run TOOL-NOT-IN-ARGV, run TOOL-PATH-REDACTED, per-element redaction, COUNTS_RE alternatives). Run r23 and r24 receipt
fixtures per mutant in scratch copies. Table + `uncovered=<n>`.""", w)
    add("W2C3Symmetry", "critic", f"""Attack the claim title "verify/run symmetry" at {TIP}: enumerate argv/receipt shapes and find any that `run`
accepts but `verify` refuses on the receipt `run` wrote, or that `verify` accepts but `run` would refuse (e.g.
`./tools/x`, absolute tool path, tool as a data argument, `bash -c`, redaction-matching args like `password=a$b`,
tool path with `sk-`). Scratch repo only; paste each pair. Verdict: symmetric / asymmetric with list.""", w)
    add("W2C3Redact", "sentinel", f"""Attack the per-element redaction change in `run` (`cmd=` now redacts each argv element, then the joined
line). Construct argv where a secret spans two elements (`--token` `abc...`, `-H` `Authorization: Bearer x`,
`password` `=` `x`) and compare the cmd= line produced by the base runner and the tip runner in a scratch repo. Any
secret that the base redacted and the tip leaks = HIGH finding. Paste outputs (use fake secrets only).""", w)
    add("W2C3CountsRE", "reviewer", f"""Attack the COUNTS_RE widening in `{LANE}/tools/souji-receipt-run.py` ({TIP}). Can a receipt with no real
measurement pass verify (e.g. stdout `cases=0 pass=0`, a counts line only in stderr, a decoy line)? Note
`{REC}/c2-fixture-after.tsv`: `run` printed the FIRST counts match (`grounded=2…`, a case line), not the final
`cases=9 pass=9` line — is any lane record misled by that? Recommend the narrowest fix; do not edit.""", w)
    # ---------------- sources / entry / assimilation ----------------
    add("W2SrcPath", "scout", f"""Re-open S120 and S121 (`{LANE}/corpus/SOURCES.md` rows) live: github blob URLs for path.c at v2.56.0 and v2.30.0.
Check every quote the entry `{LANE}/corpus/knowledge/count-objects-linked-worktree-garbage.md` and the rows carry
against the live bytes and the snapshots in `{LANE}/census/round-24/sources/` (`sha256sum -c SHA256SUMS`). Check
line numbers (89-124, 111, 104-108, 112-114, 365-385, 371). Any mismatch = finding.""", w)
    add("W2SrcCountWt", "scout", f"""Re-open S122 (builtin/count-objects.c@v2.56.0) and S123 (git-scm.com/docs/git-worktree § REFS/DETAILS) live and
check every quote and line number the entry and rows use (118, 49-52, 151-152; the two git-worktree quotes) against
live bytes and `{LANE}/census/round-24/sources/`. Also: is S123's scope distinct from S003/S058 (read those rows)?""", w)
    add("W2EntryClaims", "reviewer", f"""Attack the body of `{LANE}/corpus/knowledge/count-objects-linked-worktree-garbage.md` item by item (items 1-7
and the NOT-established list). Reproduce in `/var/tmp/souji-r24-W2EntryClaims/` on git 2.56.0: five creation modes
read 1; active bisect (bad+good marked) reads 2; a refs/worktree ref reads 2 and 3 with reflog; 1023/1024 byte
size-garbage; uppercase-hex loose name not garbage; `--git-dir=<common>` reads 0 for all. Any claim not reproduced
or overstated = finding with the line.""", w)
    add("W2EntryGate", "reviewer", f"""Attack the entry's Gate. Re-run at {TIP}: `python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25
--entries corpus/knowledge/count-objects-linked-worktree-garbage.md --snapshot-dir census/round-24/sources --slice
census/round-24/records/quarantine-slice --slice-verdicts census/round-24/records/slice-verdicts.tsv` and
`python3 -B tests/fixtures/r23-locator-heading.py --entries <entry> --snapshot-dir census/round-24/sources` (from
{LANE}, read-only). Then judge each ADMIT/REJECT line: is the reason true of the bytes it describes (R23-M6 class:
an overbroad reject reason)? Is every flip condition not already met?""", w)
    add("W2Rejects", "critic", f"""Attack the two rejects by re-opening the staged bytes: `{KPKG}/garbage-false-positive-modes-r26.md` and
`{KPKG}/count-objects-garbage-semantics-r23.md` (read-only). For each reject reason in the entry's Gate (falsified
central claim, fleet arm, shokuknow-only evidence, id collision, contradicted 'only two fields'), quote the staged
line it refers to and say whether the reason is TRUE of those bytes. Also attack the r25 partial admit: is the
lane really holding committed evidence for the five-mode matrix (C1 case 4 runs only ONE mode)?""", w)
    add("W2Registry", "scout", f"""Attack the registry at {TIP}: run `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root
/home/vgpnk/Projects/shokunin souji` (exit code, E/W lines), count rows (expect 123), check S120-S123 cells: 11
columns, no `|`, tier/kind/status vocab, `used-by` paths exist at {TIP} and actually cite the id (grep the files),
recheck form, opened date. Also: does `tools/souji-size-census.py` cite S120/S122 as `used-by` claims? Findings
with row ids.""", w)
    add("W2Slice", "reviewer", f"""Attack the quarantine-slice verdicts: `{REC}/slice-verdicts.tsv` (gate format) and
`{LANE}/.ufo/waves/round-24/assimilation/slice-verdicts.tsv` (detail). Compare each of the 8 rows with
`.ufo/waves/round-24/w1/ScoutSliceWeb.md` and `ScoutSliceOwnWork.md` and with round 22's
`{LANE}/census/round-22/attempt2/slice-verdicts.tsv`. Re-fetch ONE web row and ONE own-work row yourself. Is S118
`unverifiable` consistent with its scout's `present` reading? Are any verdicts unsupported?""", w)
    add("W2Collisions", "scout", f"""Re-run the §10 id-collision check at {TIP} (registry now 123 rows) exactly as in
`{FLEET}/.ufo/prompts/souji-round-24.md` §10 into `/var/tmp/souji-r24-W2Collisions/`, and compare with the committed
`{LANE}/.ufo/waves/round-24/assimilation/{{reg-ids,staged-ids,collisions}}`. Did the appended S120-S123 create new
collisions with staged ids naming DIFFERENT documents (staged S120-S123)? Is each lane S120-S123 re-pointed by
document (URL) rather than staged id? Paste lists.""", w)
    # ---------------- quality / records ----------------
    add("W2Reverify", "reviewer", f"""Attack the quality-trend evidence: `{LANE}/corpus/knowledge/git-repo-structure-readonly.md` now carries a
`ground: F2` line and an r24 re-verification note citing `{REC}/r13-recheck-receipt.tsv` and
`census/round-24/records/r13-repo-structure-recheck-git2.56.0.out`. Verify the receipt, re-run the recheck command
in a `/var/tmp` clone at {TIP}, and judge: does this entry now 're-verify' under `{FLEET}/LEARNING.md`'s quality rule?
Is anything in the note overstated?""", w)
    add("W2ReadmeRow", "reviewer", f"""Attack `{LANE}/corpus/README.md` § `Round 24` (appended): every backticked path must exist at {TIP}
(`git ls-tree`); every status statement must match landed bytes (e.g. what the C1 fixture fences, what C3 refuses);
the Frontier (r24) and routed-defect lines must be true. List each false or stale statement with its line.""", w)
    add("W2R23F4", "critic", f"""Reproduce the r23 instrument hole that ScoutInherited found (`{LANE}/.ufo/waves/round-24/w1/ScoutInherited.md`):
`tools/souji-record-agreement.py` `counts_of` takes the last counts line anywhere in a receipt, so a line after the
stderr fence can override the real stdout. In a scratch clone at {TIP}, build the doctored receipt and show the
false pass. Then say which r23 records (lesson lines 144-147) are contradicted and what the narrowest fix is. This
is the round's mined mistake candidate: give class / evidence / captured-by / fix / failure witness.""", w)
    add("W2Inherited", "scout", f"""Re-check inherited state at {TIP}: `git -C {LANE} status --porcelain` and the diffs of
`.ufo/waves/round-23/w2/W2K1.md` and `W2D3.md` (round-23 seat late updates). Have they changed since
`.ufo/waves/round-24/w1/ScoutInherited.md`? Is the round-23 seat still writing (file mtimes)? Recommend: commit as
inherited late round-23 updates in a separate labelled commit, or leave; with reasons under the prompt's
"Inherited state" rule (`{FLEET}/.ufo/prompts/souji-round-24.md` §6 item 5).""", w)
    add("W2Misroot", "scout", f"""Final misroot sweep: `git -C {FLEET} status --porcelain` (no pathspec). For each untracked entry decide whether a
souji round-24 seat wrote it (content names souji and round-24). `{FLEET}/.scratch/` is orchestrator-owned: never a
misroot, never read. Also list any `/var/tmp/souji-r24-*` leftovers (`ls -d /var/tmp/souji-r24-*`). Table only; do
not delete, move or copy.""", w)
    add("W2Separable", "critic", f"""Attack causal separability of C1/C2/C3 as landed: they share commit {AFTER}; C2's after-state includes C1's
new entry in the map; C1/C2 receipts verify only because C3's COUNTS_RE widening landed. For each claim, can it be
verified without the others' files (build the counterfactual tree in scratch: e.g. {TIP} with
tools/souji-receipt-run.py reverted to {BASE}, or without the new entry)? Verdict per claim.""", w)
    add("W2Trend", "critic", f"""Attack the round's planned trend verdicts before they are written: expansion (new edge class F2 linked-worktree
garbage + debris-census capability; 0 new map ground?), quality (a stale entry re-verified on git 2.56.0; the new
entry supersedes/narrows staged claims), discernment (≥1 admit and ≥1 reject with reasons; slice verdicts). Read
`{FLEET}/LEARNING.md` rules and `{LANE}/corpus/lessons/round-23-verifier-spotcheck.md` trend gradings. Give the
verdict you would assign each and why.""", w)
    add("W2Scope", "sentinel", f"""Attack the round's scope bound: list every path the lane commits since {BASE} changed (`git -C {LANE} diff
--stat {BASE} {TIP}`); flag any write outside {LANE}, any `census/operator-sweep-*` content, any credential-shaped
string (`grep -nE 'sk-|ghp_|BEGIN .*PRIVATE|password=' ` over the round's new files), any `/tmp` (not /var/tmp) use in
new tools/fixtures, any `__pycache__`. Findings with paths.""", w)
    add("W2LessonDraft", "scribe", f"""Draft `corpus/lessons/round-24.md` (deliver at `{LANE}/.ufo/waves/round-24/w2/W2LessonDraft.md`). Base it on
the committed receipts in `{REC}/`, the preregistration + amendment, wave-1 reports, and (as they land) the other
wave-2 reports in `{LANE}/.ufo/waves/round-24/w2/`. Sections: Claim and boundary (C1/C2/C3 with before/after and
receipts), Process deviations (amendments, L1 sanity runs, controls committed after freeze), ## Mistakes (from
`.ufo/waves/round-24/w1/ScribeLessonMistakes.md` + the r23 F4 last-wins hole + the counts-first-match display; each
with captured-by and a failure witness), ## Gate (S120-S123 opened 2026-10-25 with URL + ≤25-word quote; ADMIT/REJECT
list; slice verdicts; S115 used-by change old→new), Q56 proposal text, Trend verdicts draft. Every number must name
its receipt. No invented evidence.""", w)
    add("W2ScorecardDraft", "scribe", f"""Draft the SCORECARD.md and LOG.md appends for round 24 (deliver at
`{LANE}/.ufo/waves/round-24/w2/W2ScorecardDraft.md`). SCORECARD: a `### Round 24 measurements` table (claim, axis,
before, after, counting command, measured commit) matching the r23 table's shape in `{LANE}/SCORECARD.md`, using
ONLY the receipts in `{REC}/`; capability rows for the debris census and coverage-map agreement; Planned: mark r24
done and draft an r25 planned line from the wave-1/2 residuals. LOG: a `Round24` block in the shape of the r23 LOG
block. Check every number against its receipt and say which you checked.""", w)
    return {
        "wave": "souji-r24-w2",
        "reportDir": ".ufo/waves/round-24/w2",
        "maxLanes": 64,
        "context": context(goal),
        "items": list(ITEMS),
    }


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "w1"
    spec = {"w1": wave1, "w2": wave2}[which]()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{which}-spec.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(spec, fh, indent=1, ensure_ascii=False)
    print(f"wrote {out}: items={len(spec['items'])}")
    print(Counter(i["role"] for i in spec["items"]))
