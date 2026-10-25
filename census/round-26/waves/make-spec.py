#!/usr/bin/env python3
"""Generate the souji round-26 v2 wave spec.

Run: python3 -B .ufo/waves/round-26/make-spec.py
Writes .ufo/waves/round-26/w1-spec.json next to this file.
One v2 wave (64-128 band): build + attack seats together.
"""
from __future__ import annotations

import json
import os
from collections import Counter

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
SK = "/home/vgpnk/Projects/shokuknow"
PKG = f"{SK}/merge/souji"
KPKG = f"{PKG}/knowledge/corpus/knowledge"
BASE = "0eca7c8a5d10bcbfdae50d0c390d277deec63bfd"
FREEZE = "89e0fceeefcf28db313c94120be6d25e03c60094"
PREREG = f"{LANE}/.ufo/waves/round-26/preregistration.txt"
WAVE = "w1"
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
- Read {PREREG} FIRST plus its amendment 1. It is the frozen counter contract (claims
  C1/C2/C3, case sets, kill rules). Never propose changing a predicate, target or case
  set as if it were allowed after data: if you believe a counter is wrong or gameable,
  report it as an ATTACK. Amendments are stricter-only and logged.
- You are a READ-ONLY seat for the lane: write ONLY your own report and, if your item
  names one, the delivery file(s) inside your own report directory
  ({LANE}/.ufo/waves/round-26/{WAVE}/). No `git add/commit/push/stash/checkout/reset`,
  no `jj` mutation, no `rm`/`mv` of anything you did not create, no signals. Read-only
  `git log/show/diff/status/ls-tree/cat-file/rev-parse` against the lane are fine.
- Scratch goes ONLY under `/var/tmp/souji-r26-<YourName>/` (never /tmp); any git repo
  you need is created there with `git init` and every later git call names `-C` on it;
  verify `git -C "$D" rev-parse --show-toplevel` prints `$D` before the first commit.
  Remove your scratch before you finish.
- Absolute paths only. Your tools start at the FLEET root, not the lane: every lane
  path must be written as {LANE}/<path>. Every `Report:` trailer path is relative to
  {LANE} — write it at {LANE}/<that path>. A relative path lands in the wrong repo.
- A source claim needs a location: URL or repo path plus line/section, and a <=25-word
  verbatim quote copied from bytes you opened this run, containing no literal or
  escaped `|`.
- Unrun checks have not passed. Never report an execution you did not perform; label
  inference as `[INFERENCE]`. Run lane Python with `python3 -B` (no __pycache__).
- Tooling is authorized (operator 2026-10-19): you may install or upgrade tools that
  help the task; read /home/vgpnk/.omp/agent/RULES.md first (official channels only,
  record tool/version/channel/reason in your report). **pacman guard: all pacman
  transactions are PAUSED host-wide** — install via `uv tool`/`npx`/an official binary
  in `~/.local/bin`, or route around it. Never `pacman -S/-Sy/-Syu/-U/-R`, never
  downgrade, never restart a host service.
- Certification OFF, K5 HELD, F5 reap + NAMESPACE holds unchanged. No credentials, no
  live /proc census, no `census/operator-sweep-*` contents, no `.scratch/` contents.
  Never `agent://all` (it reaches every lane's seats) — message your seats by id.

# Output shape
Markdown report at your rendered `Report:` path: `## Status` (one line `STATUS: PASS|
PARTIAL|FAIL` + why), `## Evidence` (command, output excerpt, revision), `## Findings`
(numbered, each with its location), `## Attack log` where your item is an attack.
Terse; no filler.
"""


def item(name: str, role: str, task: str) -> dict:
    return {"name": name, "role": role, "prompt": "/skill:godspeed\n" + GODSPEED + "\n\n## Task\n" + task}


ITEMS: list[dict] = []


def add(name: str, role: str, task: str) -> None:
    ITEMS.append(item(name, role, task + f"\nReport path to ask for: `.ufo/waves/round-26/{WAVE}/{name}.md`."))


AXIS_TOOL = """tools/souji-axis-check.py CLI (frozen in prereg C3):
  python3 tools/souji-axis-check.py --prereg PATH --scorecard PATH
  parses the `## MACHINE BLOCK` section only (between that marker line and `END`):
  CLAIM <id> blocks carry `axis:`, `surface-class:` and `enumerate:` lines.
  stdout `claims=C flags=F` + one `FLAG <claim> <rule> <detail>` per finding;
  exit 0 iff F=0, 1 on flags, 2 on usage/malformed input.
  R1: axis in {calibration, operability, coverage}.
  R2: fixture-expansion allowed only on coverage; bookkeeping-file only on
      calibration; knowledge-entry/registry-append only on coverage;
      instrument-acquisition only on operability; other surface-classes
      (receipt-binding, measurement) are neutral.
  R3: >=1 claim declares the lowest-scoring non-retired axis from the
      SCORECARD axes table (scores read from its | axis | score | ... rows).
  R4: a claim block containing whole-word all/every/complete/none/no without
      an `enumerate:` line is flagged."""


def spec() -> dict:
    goal = (f"Souji round 26, one v2 wave (build + attack together). Lane: fleet repository & "
            f"workspace hygiene (掃除). Axes: calibration (7, lowest), operability (8), coverage (8); "
            f"no axis may be harmed. Claims frozen in {PREREG} at lane commit {FREEZE} (branch master, "
            f"ahead=0; amendment 1 already logged): C1 SCORECARD scaffold census+integration "
            f"(calibration), C2 F1 auto-maintenance trigger-set assimilation from {PKG} (coverage, the "
            f"round's sourced+assimilation claim), C3 axis-of-surface prereg checker (operability). "
            f"Lane base {BASE}. The L1 holds the planner seat and is the only integrator.")

    # ============ C3 build (operability) ============
    add("ExecAxisTool", "executor", f"""Write the C3 tool draft at `{LANE}/.ufo/waves/round-26/{WAVE}/souji-axis-check.py`
(the L1 copies it to `tools/souji-axis-check.py`). Frozen CLI and rules:
{AXIS_TOOL}
Implementation notes: Python 3 stdlib only, <=300 lines, argparse; read the SCORECARD axes table rows
`| <axis> | <score> | ...` (skip `retired` rows if a section exists) for R3. Whole-word match via
word boundaries; `enumerate:` presence in the same CLAIM block exempts R4. Malformed inputs (no
MACHINE BLOCK, a CLAIM with no axis line, unparseable scorecard table) exit 2 with a stderr reason
and NO flag lines. Test it yourself ONLY on throwaway prereg/scorecard files under
`/var/tmp/souji-r26-ExecAxisTool/` and paste the outputs; never run it against the lane's real
preregistration or SCORECARD (the L1 does that at integration).""")

    add("ExecAxisFixture", "executor", f"""Write the C3 fixture draft at `{LANE}/.ufo/waves/round-26/{WAVE}/r26-axis-check.py`
(the L1 copies it to `tests/fixtures/r26-axis-check.py`). CLI:
`python3 -B tests/fixtures/r26-axis-check.py --tool PATH`; last stdout line
`cases=12 pass=12 control=FALSE-GREEN-REJECTED|FALSE-GREEN-ACCEPTED`; exit 0 iff 12/12 and the
first spelling. Implement EXACTLY the frozen 12-case set in the preregistration C3 (read it):
(1) r25-C2 replica flagged on frozen operability axis [discriminator: the base/stub arm must NOT
flag]; (2) well-formed 3-claim prereg -> 0 flags; (3) R1 wrong-axis flagged; (4) R2
fixture-expansion-on-operability flagged; (5) R2 bookkeeping-on-coverage flagged; (6) R2
instrument-on-calibration flagged; (7) R3 no-lowest-axis flagged; (8) R4 universal clause without
enumerate flagged; (9) R4 universal clause WITH enumerate passes; (10) well-formed claim with
surface-class + enumerate passes; (11) malformed prereg (missing axis line) -> exit 2, no flag
lines; (12) control: a stub tool always printing `claims=1 flags=0` must be rejected
(FALSE-GREEN-ACCEPTED arm). Each case its own files under `/var/tmp/souji-r26-ExecAxisFixture/`,
removed in a finally block. The r25-C2 replica text: reconstruct it from the committed r25
preregistration at `git -C {LANE} show 6e4737eab43d8fde1b85eb9f57023d29046705b4:.ufo/waves/round-25/preregistration.txt`
C2 (a fixture-expansion claim declared on operability while the axis was frozen) — write it into
the fixture as a synthetic prereg, and pair it with the actual scorecard (axes cal/7 op/8 cov/8)
so the discriminator fires. Print one `CASE <n> <name> PASS|FAIL <detail>` per case. Tool CLI it
targets (the L1 writes the tool in parallel):
{AXIS_TOOL}
Exercise your fixture against a tiny reference tool you write in scratch (and the stub) and paste
both runs; never run anything against the real lane preregistration or SCORECARD.""")

    add("ExecAxisSelftest", "executor", f"""Draft a `--selftest` mode for the C3 tool (deliver at
`{LANE}/.ufo/waves/round-26/{WAVE}/souji-axis-check-selftest.md`): the tool run with no fixture
verifies its own rule table against embedded synthetic cases and prints `selftest=N/N pass`.
Specify the embedded cases (one per R1-R4 positive + negative), the output line, and the exit
contract, matching the lane's embedded-selftest convention (read `tools/souji-rev-pin.py`
`--selftest` for the shape). ALSO read the prereg C3 kill rules and list any frozen check your
selftest design would leave unexercised. Prose spec + pseudocode, not a second tool.""")

    add("ScribeAxisDocs", "scribe", f"""Draft (deliver at `{LANE}/.ufo/waves/round-26/{WAVE}/axis-check-docs.md`):
(a) the QUALITY.md Q59 criterion row text — criterion + applies-to + test + lesson columns — for
the axis-of-surface rule (cites corpus/lessons/round-25.md R25 axis misattribution + this round's
mistake row R26-M1; mirror the exact table shape of the Round 25 criteria block in
`{LANE}/corpus/QUALITY.md`); (b) the SKILL.md Gate-registry row text for `souji-axis-check` and
`r26-axis-check` matching the existing table's column shape (name/kind/entry command/verdict map/
self-test/pinned-value/write scope/owner); (c) a one-paragraph knowledge-adjacent summary of the
surface-class taxonomy the rule encodes (r25 C2 = fixture-expansion on a frozen axis). Every
prose item names where in the file it lands. No invented history.""")

    # ============ C2 build (coverage / assimilation) ============
    add("ScoutStagedEntries", "scout", f"""Read the two staged entries completely:
`{KPKG}/git-auto-maintenance-trigger-set.md` and `{KPKG}/git-auto-maintenance-trigger-set-r23.md`.
For each: list every `source:` line's staged S-id + URL/anchor; note which staged rows the CLAIM
paragraphs actually rest on (vs. only cited in front matter); identify exactly which sentences of
entry B cite staged S131 (fleet worktree census) and the unadmitted knowledge file
`count-objects-garbage-semantics-r23.md` — the L1 must re-point those. Also check both entries for
any claim that contradicts the lane's existing corpus (`{LANE}/corpus/knowledge/git-auto-maintenance-prunes-worktrees.md`,
`git-grace-periods-and-expire-to.md`, `jj-colocation-receipts.md`); report any contradiction as a
finding, verbatim. Read-only; never write into {SK}.""")

    add("ScoutRegroundDocs", "scout", f"""Re-open THIS RUN (the lane must re-ground, the campaign's open dates prove
nothing): fetch and capture snapshots + <=25-word located quotes for the three doc/code rows the
admitted entries cite:
- staged S109 git-fetch(1): https://git-scm.com/docs/git-fetch — § OPTIONS `--auto-maintenance, --no-auto-maintenance, --auto-gc, --no-auto-gc`; quote the switch text verbatim.
- staged S110 git.git v2.56.0 call sites: https://raw.githubusercontent.com/git/git/v2.56.0/builtin/fetch.c (and merge.c, rebase.c, am.c, commit.c, pull.c) — locate `run_auto_maintenance` call sites (fetch.c:2926, merge.c:509, rebase.c:572, am.c:1942, commit.c:1965) and pull.c:392's `strvec_pushl` fetch spawn; capture the exact lines.
- staged S111 is folded into S110's capture (pull.c line).
Write each snapshot's bytes to `/var/tmp/souji-r26-ScoutRegroundDocs/` (they get copied to
`{LANE}/census/round-26/sources/` by the L1): files `git-fetch.1.txt`, `git-builtin-v2560.txt`,
`git-pull-c.txt`. Quote <=25 words each, name the exact § or file:line. Access date 2026-10-25.
Note fetch failures honestly — an unopened source is not a row.""")

    add("ScoutRegroundOwnwork", "scout", f"""Re-ground the two own-work staged rows THIS RUN (read-only):
- staged S123 fixture: read `{SK}/lanes/souji/round2/fixtures/r23-trigger-prune.sh` (full) and
  `{SK}/lanes/souji/round2/evidence/r23-trigger-prune.out` — verify the 7 case ids
  SOUJI-R23-TRIGGER-{{fetch,fetch-auto-off,pull,merge,rebase,locked,fresh}} and the 2->1/2 outcome
  lines; record sha256 of both files.
- staged S131 census: read `{SK}/lanes/souji/round2/evidence/r23-worktree-census.out` — verify the
  5-registrations/0-prunable/0-locked figures; record sha256.
Also re-verify the lane's own `git --version` and, in `/var/tmp/souji-r26-ScoutRegroundOwnwork/`,
re-run ONE case of the fixture logic if a git 2.56.0 is available: create a repo, `git worktree
add` a linked worktree, remove its directory, age nothing, and run `git -c gc.worktreePruneExpire=now worktree prune --dry-run` — report whether the registration is named. That partial re-run is
extra evidence, never the admission basis.""")

    add("ExecScratchMirror", "executor", f"""Write the C2 scratch-mirror builder at
`{LANE}/.ufo/waves/round-26/{WAVE}/mirror-build.py` (a runnable script the L1 executes): copies
`{LANE}/corpus/` to `/var/tmp/souji-r26-mirror/corpus/`, applies the append block (5 rows
S128-S132, normalized to the 11-column census schema — read `{LANE}/corpus/SOURCES.md` for the
exact header and an existing A/mined row), and drops the two admitted knowledge files at their
repo-relative paths (drafts provided by scribes under `.ufo/waves/round-26/{WAVE}/`). Then runs
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file /var/tmp/souji-r26-mirror/corpus/SOURCES.md`
and prints the exit code. Read `{PREREG}` C2 for the exact renumber map and row set. The script
must take `--entries-dir DIR` (where the two entry drafts live) and `--rows-file FILE` (the
normalized append block) so the L1 can feed it the final bytes. Do NOT run it against the real
corpus; produce the script + a self-test on a tiny synthetic corpus in /var/tmp and paste output.""")

    add("ExecRenumberMap", "executor", f"""Build the staged->lane renumber map as data. Read
`{PKG}/SOURCES.append.md` (full) and extract rows S109, S110, S111, S123, S131 verbatim (the
columns: id/source/kind/tier/scope/anchor/teaches/status/opened/recheck/used-by). For each row,
find whether the SAME document (URL or own-work path) already has a row in
`{LANE}/corpus/SOURCES.md` (E04 within-scope duplicate check): run the collision extractor from
the prereg (grep -oE '^ {{0,3}}\\|[[:space:]]*S[0-9]{{3,}}' both files, comm -12) AND a URL grep for
each of the five staged sources against the lane registry. Deliver at
`{LANE}/.ufo/waves/round-26/{WAVE}/renumber-map.md`: the 5 staged rows verbatim, any lane-registry
duplicates found (id + scope), and the final renumber map staged->S128..S132 IN THE PREREG's
ORDER (S109->S128, S110->S129, S111->S130, S123->S131, S131->S132). Also check whether the two
staged own-work rows' evidence paths exist (ls the named files). Do not write into {SK}.""")

    add("ScribeEntryA", "scribe", f"""Draft the admitted entry A at `{LANE}/.ufo/waves/round-26/{WAVE}/entry-git-auto-maintenance-trigger-set.md`
(the L1 copies it to `corpus/knowledge/git-auto-maintenance-trigger-set.md`). Front matter:
`source:` lines citing the LANE ids (S128 git-fetch docs, S129 builtin call sites, S130 pull.c),
`verified-at:` 2026-10-25, `recheck:` the staged entry's own 90d call-site re-grep command, and
`ground: F1 — git-native housekeeping vs receipts (the trigger set and the per-command opt-out)`.
Body: re-ground the staged entry's claims 1-3 (trigger set of five builtins + pull spawning fetch
+ per-invocation opt-out + merge/rebase error-ignoring comment). OMIT the staged S119/S120/S121
language-edition claims (this round refuses that subset — say so in a `## Limits` line citing the
round lesson). Keep every "what this does NOT establish" item from the staged entry. Locate every
quote <=25 words with its § or file:line; snapshots will exist at census/round-26/sources/. Match
the existing entry style of `{LANE}/corpus/knowledge/git-auto-maintenance-prunes-worktrees.md`.
Never invent a measurement — the trigger-set is call-site evidence only (entry B is the fixture).""")

    add("ScribeEntryB", "scribe", f"""Draft the admitted entry B at `{LANE}/.ufo/waves/round-26/{WAVE}/entry-git-auto-maintenance-trigger-set-r23.md`
(the L1 copies it to `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md`). Front matter:
`source:` lines citing LANE ids (S131 own-work fixture, S129 builtin call sites, S130 pull.c,
S128 git-fetch docs), `verified-at:` 2026-10-25, `recheck:` the staged 90d fixture re-run command,
`ground: F1 — git-native housekeeping vs receipts (the trigger set is now MEASURED, not inferred)`.
Body: re-ground all four measured claims (4 commands prune 2->1, no receipt involved, both
off-switches, the fresh-registration control). RE-POINT the body's staged-S131 citation: it must
cite lane row S132 (fleet worktree census) directly and MUST NOT name the unadmitted file
`count-objects-garbage-semantics-r23.md`. Keep every NOT-establish item verbatim-ish. Locate quotes
<=25 words each. Match lane entry style.""")

    add("ScribeSourceRows", "scribe", f"""Draft the normalized append block at
`{LANE}/.ufo/waves/round-26/{WAVE}/sources-append-block.md`: five rows S128-S132 in the exact
11-column census schema of `{LANE}/corpus/SOURCES.md`. Row fields (from staged rows, normalized):
S128 <- staged S109 git-fetch(1) docs A; S129 <- staged S110 git.git v2.56.0 builtins code A;
S130 <- staged S111 builtin/pull.c code A; S131 <- staged S123 own-work fixture r23-trigger-prune.sh
kind own-work tier A; S132 <- staged S131 own-work census r23-worktree-census.out kind own-work
tier A. Recheck cells: staged S109/S110/S111 keep `on-release` cadence phrasing WITHOUT prose after
the cadence (stripped prose goes to the lesson Gate, not the cell); staged S123/S131 keep `90d`.
`opened` = 2026-10-25 (the lane's re-open date, not the campaign's). `status` = mined. `used-by` =
exactly the admitted entries citing the row (entry A cites S128/S129/S130; entry B cites
S128/S129/S130/S131/S132 — set used-by accordingly: S128/S129/S130 list both paths, S131/S132 list
entry B only). No cell may contain a literal or escaped `|` — if a staged teaches cell has one,
rewrite it in your own words. Include the verbatim staged row for each so the L1 can diff.""")

    add("ScribeGateDraft", "scribe", f"""Draft the round lesson's Gate text at
`{LANE}/.ufo/waves/round-26/{WAVE}/gate-draft.md`: for each of the five new rows S128-S132 write
the ADMIT line — URL/path, access date 2026-10-25, <=25-word located quote — plus the REFUSE line
for the staged S119/S120/S121 subset (reason: peripheral language-edition corroboration, not
load-bearing; flip: a later round wants the multilingual record). For each re-pointed staged id
write the old->new pair (staged S109->S128 etc.). Add the search-log note: the theme was chosen
because it closes the lane's own F1 frontier question ('call sites only — whether each prunes was
not fixture-run'). Keep the exact `## Gate` shape of `{LANE}/corpus/lessons/round-25.md`.""")

    # ============ C1 build (calibration) ============
    add("ExecC1Surgery", "executor", f"""Produce the C1 SCORECARD integration as DRAFT FILES (the L1 applies it):
deliver at `{LANE}/.ufo/waves/round-26/{WAVE}/`: (a) `c1-scaffold-extract.md` — the fenced block's
content split into its three payloads: the Round 24 measurements table (5 claim rows), the two
capability rows, and the two planned bullets — each copied VERBATIM from `git -C {LANE} show
89e0fce...:SCORECARD.md` (use `git -C {LANE} show 89e0fceefcf28db313c94120be6d25e03c60094:SCORECARD.md | sed -n '172,229p'` and cite exact line ranges); (b) `c1-new-scorecard-head.md` — the
file's new top section: base lines 1-16 + `### Round 24 measurements` inserted directly above
`### Round 23 measurements` (per the file's own "newest first" contract — but Round 25's table
already sits at the file's end as the historical layout; insert r24's table immediately above
r23's heading), then base lines 17+ unchanged; (c) `c1-line-map.md` — a mapping of every line
number cited by the trailing `superseded by SCORECARD.md:NNN` lines (:181, :180, :92, :224, :225)
to its new number after your edit, so the L1 can append a mapping note. Verify your draft
computes `markers=0` under the frozen counter and the heading triple orders n25<n24<n23... wait —
the real r25 table is at the file END, not above r23: the file's actual order after your edit
must still satisfy the K2 counter's n25<n24<n23 ordering. Check what the counter actually counts
and tell the L1 the exact required ordering (the r25 table is BELOW the scaffold). Report the
true required layout honestly, even if it conflicts with "newest first" prose — the frozen
counter is the contract.""")

    add("ExecC1Verify", "executor", f"""Independently verify the C1 claim's base state and draft edit feasibility:
(a) at `{FREEZE}`, reproduce `git -C {LANE} grep -cE '^(Insert the table below directly above|Optional same-landing correction)' {FREEZE} -- SCORECARD.md` -> 2; (b) extract the fenced payload lines
172-228 at that rev and byte-diff them against the ExecC1Surgery draft when it appears (or extract
yourself now); (c) compute the post-edit heading positions for a candidate edit: removing base
lines 170-229 (blank..---) and inserting the r24 table above `### Round 23 measurements` — report
the resulting line triple under the frozen awk counter; (d) verify the capabilities table has no
`debris census (r24)`/`coverage-map agreement (r24)` rows OUTSIDE the fence (the two rows exist
only inside it) and that Planned lacks the r24/r25 bullets outside the fence. Deliver
`{LANE}/.ufo/waves/round-26/{WAVE}/c1-verify.md` with each command+output.""")

    add("ScribeC1Note", "scribe", f"""Draft at `{LANE}/.ufo/waves/round-26/{WAVE}/c1-append-note.md`: the
`### Round 26 append-only corrections` text for SCORECARD.md — a mapping note recording that the
r25-era superseded-by lines name the PRE-CLEANUP line numbers (:181, :180, :92, :224, :225), with
the old->new map (from ExecC1Verify's work or your own computation). Also draft the LOG.md Round26
block section covering C1's before/after (markers 2->0, headings moved), in the exact style of the
existing Round25 LOG block at `{LANE}/LOG.md` tail. Do not fabricate receipts — leave
`RECEIPT-PENDING` placeholders the L1 fills.""")

    # ============ Attack seats (>=25% share) ============
    add("RevC1Counter", "reviewer", f"""Attack the C1 frozen counter. Read {PREREG} C1. Is K1's grep
pattern gameable (could a scaffold survive while printing 0)? Does K2's awk correctly require
exactly three measurement headings AND the n25<n24<n23 ordering the claim names? Re-run BOTH
commands at {FREEZE} yourself and paste output. Check whether removing the scaffold could violate
a kill-rule arm (what if the fenced r24 table differs from a 'real' r24 table that should exist —
is there one?). Check the file has no other scaffold residue the counter misses: `grep -nE 'Insert|Optional same-landing|Findings 6|newest first' <(git -C {LANE} show {FREEZE}:SCORECARD.md)`.
Verdict: counter sound / gameable-by-X / misses-Y.""")

    add("RevC2Scope", "reviewer", f"""Attack the C2 assimilation claim. Read {PREREG} C2. Questions:
(1) Do the two chosen entries actually belong to souji's PROVINCE (F1 git-native housekeeping)?
Check `{LANE}/PROVINCE.md` frontier F1 wording. (2) Is the ground genuinely 'uncovered' for
expansion credit — the lane already holds F1 entries: does trigger-set + measured-prune add
anything the map doesn't hold? Compare against
`{LANE}/corpus/knowledge/git-auto-maintenance-prunes-worktrees.md` and
`git-grace-periods-and-expire-to.md` — quote the gap the existing entries name (the r1 entry's
own admission that fetch/merge/rebase were 'call sites only — not fixture-run'). (3) Is the
renumber-by-document rule correctly applied — could a staged row's document collide with an
existing lane row (check git-fetch docs against S001-S127)? Verdict: claim sound / overclaims /
collides.""")

    add("RevC3Design", "reviewer", f"""Attack the C3 tool design. Read {PREREG} C3. Is the
surface-class->axis table the right encoding of the r25 lesson (was C2 really
fixture-expansion->coverage, or is the rule too rigid — a fixture that changes a runnable
command's behaviour is legitimately operability)? Does R3's lowest-axis read parse the SCORECARD
axes table correctly (rows like `| coverage | 8 | ...` — verify against the real file)? Can a
malicious prereg pass R4 by hiding a universal clause (e.g. 'no ' inside a counter command)?
Name the strongest adversarial input that SHOULD flag but wouldn't. Also check R2's neutral
classes list: does 'measurement'/'receipt-binding' carve a hole where any claim can declare
operability? Verdict + the worst input.""")

    add("MutC1Surgery", "mutation-tester", f"""Mutation-test the C1 integration plan. The edit: delete
SCORECARD.md base lines ~170-229 and re-insert payloads. Attack surfaces: (a) does the r25 table
(231-240) or corrections (241-251) accidentally shift/lose bytes (mutate the plan by also moving
the r25 table — is that required by 'newest first' or forbidden?); (b) the trailing superseded-by
lines cite old line numbers — propose the exact mutations to the edit that would break the
line-mapping note (e.g. forgetting that deleting the scaffold changes ALL subsequent line numbers);
(c) check whether `### Round 24 measurements` inside the fence uses the same heading syntax the
awk counter matches (`^### Round 24 measurements`) — does the extraction keep the heading line or
drop it? Write the three strongest mutations of the L1's planned edit and say which pass/fail the
K2 counter. Deliver your verdict at your report path.""")

    add("MutC2Rows", "mutation-tester", f"""Mutation-test the C2 append block. Take the staged rows
S109/S110/S111/S123/S131 from `{PKG}/SOURCES.append.md` and the census commands in
`{LANE}/CORPUS.md` (the Census section): hand-run the malformed-row awk check (NF!=13), the
duplicate-id check, the enum check and the tier-inflation check against the FIVE staged rows as
if appended verbatim to `{LANE}/corpus/SOURCES.md` in a /var/tmp mirror. Which rows fail which
check (report the staged rows' recheck cells — do they contain prose like 'on-release — re-grep
call sites...' that violates the recheck-cell schema, or literal `|`)? Then mutate: indent a
staged row 2 spaces (does the census still count it?), append a row whose used-by names an
unadmitted entry (does the missing-path check fire?). Paste every command+output.""")

    add("MutC3Fixture", "mutation-tester", f"""Mutation-test the C3 fixture design. Read the frozen
12-case set in {PREREG}. Find the weakest case: which case would a subtly-broken tool still pass
(e.g. a tool that only checks R2 and skips R1/R3/R4 — does any case cover each rule alone)? The
discriminator case 1 pairs the r25-C2 replica with the real scorecard — propose a replica variant
that still fools a partial implementation (e.g. fixture-expansion on coverage = legal, but
receipt-binding on operability = is that legal?). Also: is case 12's always-green stub arm able
to fail if the fixture compares only the last line? Design a stronger control (e.g. a stub that
prints flags=0 but exits 2 — should the fixture reject it?). List every survivor-class hole.""")

    add("CritClaims", "critic", f"""Falsify the round's three claims as a set. Read {PREREG}. Are the
three claims causally separable (can each verify without the others)? Is C1 really calibration
(self-assessment vs observed state) or is it bookkeeping-without-axis? Is C3 really operability or
is it calibration-dressed-as-tooling (the instrument catches axis misattribution — arguably a
calibration surface)? Note the round's own checker would flag bookkeeping-file on a non-calibration
axis: does C1's declared axis survive its own R2 table (bookkeeping-file->calibration only — does
C1 change ONLY the bookkeeping file, or also fixtures/tools)? Apply the checker mentally to this
prereg and report whether IT flags anything. Verdict: separable/overlap; each axis call right or
wrong, with reasons.""")

    add("CritC2Admission", "critic", f"""Falsify the C2 entry admissions specifically. Read the two
staged entries fully (`{KPKG}/git-auto-maintenance-trigger-set.md`, `-r23.md`) and the lane's
QUALITY.md bar (Q1-Q4, Q17, Q54, Q56). Does entry B's own-work fixture row (staged S123) meet the
A-tier standard for `own-work` (it is the campaign's evidence, not this lane's rerun — is a
fixture the lane did not itself run an A row here?)? Does entry A's claim 3 (merge/rebase
error-ignoring comment) have a located quote in the staged bytes or is it unattributed? Which
claim sentences in either entry lack a located quote and would fail the Gate's quote rule? Name
every sentence that should be cut or re-grounded.""")

    add("SentBounds", "sentinel", f"""Bound-sweep the wave contract. The wave's HARD BOUND forbids
writes outside {LANE}, jj/git mutation, /proc, operator-sweep contents, and {SK} writes. Check the
round's actual work plan in {PREREG} for any step that violates its own bound: (a) does the C2
assimilation require writing anywhere in {SK}? (b) does the mirror validation run
sources-census.sh --file on a /var/tmp copy — is that the sanctioned path per CORPUS.md? (c) do any
counter commands read `census/operator-sweep-20261019/` contents or `.scratch/`? (d) the own-work
re-grounding reads campaign evidence files — is reading them inside the read-only bound or does
it cross it? Deliver the bound-compliance verdict per step.""")

    add("LabAxisRun", "labrat", f"""Runnable probe for C3: hand-simulate the axis-check rules on the
ROUND'S OWN preregistration. Parse `{PREREG}`'s MACHINE BLOCK (CLAIM C1/C2/C3 blocks). Scorecard
scores: read `{LANE}/SCORECARD.md` axes table at {FREEZE}. Compute: R1 (all three axes owned?),
R2 (C1 bookkeeping-file->calibration OK? C2 knowledge-entry->coverage OK? C3
instrument-acquisition->operability OK?), R3 (is calibration the lowest non-retired? which claim
declares it?), R4 (any whole-word all/every/complete/none/no in a claim block without enumerate:?
— grep each block). Paste your manual parse + the expected `claims=3 flags=N` result; if you get
flags>0, say which rule and why (this is the self-host check — a flag on the real prereg is a
KILL finding).""")

    add("LabReceiptVerify", "labrat", f"""Runnable probe: verify the four committed red-before
receipts at `{LANE}/census/round-26/records/` (c1-before, c2-before, c3-before, c2-k4-base) with
`python3 -B tools/souji-receipt-run.py verify --root . --rev 12fd90bcd9cdfab495e178023eeaa838a977fcbe <receipt>`
(or per receipt's recorded rev). Report verify=ok / the refusal string per receipt. ALSO check
the receipt files are byte-consistent with what the runner would emit at their revs (tool_sha256
vs `git -C {LANE} show <rev>:<tool> | sha256sum`). Paste every command+output.""")

    add("LabSourcesCensus", "labrat", f"""Runnable probe: run the frozen census commands from
`{LANE}/CORPUS.md` §Census against `{LANE}/corpus/SOURCES.md` at {FREEZE}: row count, malformed
count, tier histogram, status histogram, duplicate ids, enum violations, mined-used-by-missing.
Paste each command+output verbatim. Then run
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
and paste its exit + tail. Any nonzero finding is an attack on the round's starting state.""")

    add("ConnSiblings", "connector", f"""Sibling-overlap scan for the round's ground. Check each
rostered lane's PROVINCE.md + SKILL.md (read-only at {FLEET}/<lane>-shokunin/ or siblings) for
overlap with: (a) C2's F1 trigger-set ground — git auto-maintenance, worktree prune, grace
periods (do tsukuroi, kama, kumitate hold entries on maintenance/prune that souji would absorb?
kumitate owns worktree locking per the adjacency note); (b) C3's prereg-gate surface (does any
sibling own preregistration/claim-gating — kaidoku's eval?); (c) the SCORECARD-surgery surface.
Report per-lane overlap verdicts: absorb/report/routed. Read-only.""")

    add("ConnCrossSource", "connector", f"""Cross-source pattern check for C2. Do any of the five
staged rows' documents already exist in the lane registry under OTHER ids or scopes (E04/E03
within-scope duplicate)? Grep `{LANE}/corpus/SOURCES.md` for: git-scm.com/docs/git-fetch,
github.com/git/git/blob/v2.56.0, builtin/pull.c, r23-trigger-prune, r23-worktree-census. Report
every hit (id + scope) — a hit inside the same scope is an append-refusal (E04), a hit outside
scope is a warning to record. Also check whether any of the two staged entries' knowledge file
names collide with existing `{LANE}/corpus/knowledge/` names.""")

    add("RevPreregFreeze", "reviewer", f"""Verify the freeze ordering: was the preregistration
committed before any claim work? Check `git -C {LANE} log --oneline -8 -- .ufo/waves/round-26/`
and `git -C {LANE} diff 0eca7c8 {FREEZE} -- SCORECARD.md corpus tools tests` (must be empty — the
freeze changed only prereg + counters + receipts). Was amendment 1 logged before any seat scored?
Confirm the counters produce the declared base literals (re-run them in a private clone at
{FREEZE} under /var/tmp). Verdict: freeze clean / contaminated.""")

    add("CritKillRules", "critic", f"""Falsify the kill rules. For each claim in {PREREG}, name the
cheapest way to make its counter print the after-value WITHOUT doing the work: (C1) leave the
scaffold but strip the two marker strings only; (C2) append rows without the mirror validation
or without re-grounding; (C3) write a tool that hardcodes `claims=3 flags=0`. For each, say
whether the other counters/kill rules catch it (e.g. C1's kill rule 'any landed number
disagrees with its receipt' — does it catch the marker-strip cheat? the headings would stay
unmoved but markers=0!). If a cheat survives, the counter set needs a strengthening amendment —
propose the amendment text (stricter only).""")

    add("MutReadmeF1", "mutation-tester", f"""Mutation-test the C2 README edit. The F1 row at
`{LANE}/corpus/README.md` :39 gains two backticked entry paths. Mutations: (a) append paths to
the status cell instead of entries cell (Q56 says status-column mentions never map — does
coverage-agreement flag it?); (b) name the paths without backticks; (c) update the r12-era F1
row but leave the later r13+ sections' F1 rows stale (there may be MULTIPLE F1 rows — enumerate
them: `grep -n '| F1' {LANE}/corpus/README.md` and check each row's role). Report which mutations
the K4 kill rule catches and which sail through.""")

    add("LabGateCheck", "labrat", f"""Runnable probe: dry-run the C2 gate command shape BEFORE the
entries exist: `python3 -B tools/souji-gate-check.py --root {LANE} --round-date 2026-10-25
--entries corpus/knowledge/git-auto-maintenance-trigger-set.md corpus/knowledge/git-auto-maintenance-trigger-set-r23.md --snapshot-dir census/round-26/sources --slice census/round-26/records/empty-slice --slice-verdicts census/round-26/records/empty-verdicts`.
It must fail now (entries absent) — paste the failure output (this is the red arm that proves
the gate fires). Also read `tools/souji-gate-check.py` enough to name every check it runs
(provenance trio, snapshot § locators per Q54, slice verdicts, pipe-escapes) and confirm the
command the prereg freezes is the tool's actual CLI.""")

    add("LabSnapshotPlan", "labrat", f"""Runnable probe: check what snapshot files the C2 gate needs.
Read `tools/souji-gate-check.py`'s snapshot resolution (how it maps an entry's `snapshot:` or
source URLs to files under --snapshot-dir) and list the EXACT filenames it will look for in
`{LANE}/census/round-26/sources/` for the two entries' cited sources. Cross-check against the
ScoutRegroundDocs deliverables (git-fetch.1.txt, git-builtin-v2560.txt, git-pull-c.txt) — report
any filename mismatch BEFORE the L1 copies them. Also verify Q54's heading-set rule applies to
each snapshot's § locators.""")

    # ============ More build seats ============
    add("ExecSh256Sums", "executor", f"""After snapshots land, the L1 commits a SHA256SUMS over
census/round-26/sources/. Prepare the generation+verification recipe at
`{LANE}/.ufo/waves/round-26/{WAVE}/sha256sums-recipe.md`: the exact `sha256sum` invocation sorted
LC_ALL=C, matching `census/round-25/sources/SHA256SUMS` format (inspect it); plus a dry-run
against the r25 dir to prove the recipe's verify step exits 0. Paste output.""")

    add("ScribeScorecardR26", "scribe", f"""Draft at `{LANE}/.ufo/waves/round-26/{WAVE}/scorecard-r26.md`: the
`### Round 26 measurements` table (claim/axis/before/after/counting command/measured commit) in
the r25 table's shape, plus capability row for `prereg axis-check (r26)`, plus the Planned edits
(mark r26 done, draft the r27 line from the residuals below). Residuals to carry: the staged
S119/S120/S121 subset refusal, F1 remaining frontier (keep-ref expiry, fleet exposure census
numerator), and whatever wave findings land. Use RECEIPT-PENDING placeholders for numbers the L1
fills. Also draft the two-axis verdict sentences (quality/discernment trends).""")

    add("ScribeLogR26", "scribe", f"""Draft at `{LANE}/.ufo/waves/round-26/{WAVE}/log-r26.md`: the full
LOG.md Round26 block (mirroring the Round25 block's shape): freeze commit, amendment 1, claims
C1/C2/C3 with before/after + receipts, wave shape + seat totals + dead seats (L1 fills),
SOURCES before->after counts, assimilation theme + considerthese absence line, mistakes
R26-M1 (axis misattribution) + the Q58 catch (K4 literal), certification OFF/K5 HELD/F5 line.
RECEIPT-PENDING placeholders for measured values.""")

    add("ScribeLessonR26", "scribe", f"""Draft at `{LANE}/.ufo/waves/round-26/{WAVE}/lesson-r26.md`:
corpus/lessons/round-26.md skeleton in the r25 lesson's exact shape — Author line (SoujiR26,
souji@shokunin.local), lane base {BASE}, Claim-and-boundary table (C1/C2/C3 rows), Process
deviations section (empty pending wave), `## Gate` (from the GateDraft material: S128-S132
admits + the S119-S121 refuse + renumber old->new + search-log note), `## Mistakes` (R26-M1
axis-misattribution row: class attribution/scope, evidence r25 prereg + W2 CritC2Classification,
captured-by none->Q59, fix C3 instrument — failure witness SHOWN once the tool flags the r25-C2
replica; plus the Q58-catch near-miss row for the K4 literal), `## Seat-reported failures`
(placeholder), Trend verdicts (draft), Boundaries section. No invented numbers.""")

    add("ExecLandingCheck", "executor", f"""Write the landing-gate re-run recipe at
`{LANE}/.ufo/waves/round-26/{WAVE}/landing-check.md`: the exact command to re-run
`tools/souji-landing-gate.py` at the round tip (--root {LANE} --rev <tip> --round 26), plus the
expected classes it could emit on this round's changes (LG-DANGLING-PTR for the new entries'
snapshot/census citations if any path is wrong). List every new repo-relative path this round
adds (entries, sources snapshots, records, waves dir, counter scripts, tools, fixtures) so the
gate input is complete. Read the gate's --help to confirm the CLI.""")

    # ============ Reconnaissance & misc scouts ============
    add("ScoutCensusBefore", "scout", f"""Re-derive the round-start census independently: run
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
fresh and diff against `{LANE}/.ufo/waves/round-26/census-before.txt` — byte-identical expected;
report any divergence. Also run the six manual census greps from CORPUS.md on
`{LANE}/corpus/SOURCES.md` at {FREEZE} and paste outputs (rows, malformed, tier+status
histograms, dup ids, enum violations, mined-missing).""")

    add("ScoutF1Gap", "scout", f"""Map the F1 frontier precisely for the report: read
`{LANE}/corpus/knowledge/git-auto-maintenance-prunes-worktrees.md` and
`git-grace-periods-and-expire-to.md` fully. List verbatim every sentence that defers the
fetch/merge/rebase/pull trigger set (the gap entries A/B close). Also enumerate the F1 surface's
remaining open items per PROVINCE + README (`keep-ref` expiry unmeasured; the fleet's own
registrations numerator at r24/25). Deliver the gap list that grounds the C2 expansion claim.""")

    add("ScoutAssimRegister", "scout", f"""Check the assimilation quarantine register for souji: read
`/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md` rows
where col-2 = `souji` and col-3 matches round[0-9]+ and col-4 has an S-id (the awk in the
addendum §10). Report the FULL slice (every S-id + its class cell) — the r24 gate already
accepted 8; check whether the C2 entry set (trigger-set theme) touches any register-quarantined
row. Read-only; never write the register.""")

    add("ScoutWaveEvidence", "scout", f"""Inventory the wave evidence files the L1 must commit:
list every path under `{LANE}/.ufo/waves/round-26/` and `{LANE}/census/round-26/` at {FREEZE}
with sizes; then enumerate the deliverable paths every seat's item names (grep the spec at
`{LANE}/.ufo/waves/round-26/w1-spec.json` for `.ufo/waves/round-26/w1/` paths). Deliver the
expected-vs-present checklist for the L1's landing pass.""")

    add("SonicLineCount", "sonic", f"""Mechanical checks at {FREEZE}: (a) `git -C {LANE} show
{FREEZE}:SCORECARD.md | wc -l` (expect 254); (b) the exact byte offset range of base lines
170-229 (the scaffold span incl. fences + ---); (c) `grep -c 'superseded by SCORECARD' <
(git -C {LANE} show {FREEZE}:SCORECARD.md)`; (d) line numbers of every `### ` heading at
{FREEZE}. Paste raw outputs only.""")

    add("SonicReadmeMap", "sonic", f"""Mechanical checks: enumerate every coverage-map row in
`{LANE}/corpus/README.md` at {FREEZE} (`grep -nE '^\\| F[0-9]|^\\| receipts' corpus/README.md` and
the r13+ later-section F1/F2 rows too), plus the exact line numbers of the F1 row at :39 and the
superseded F2 row at :40. Paste raw outputs only.""")

    add("SimpCounterCheck", "simplifier", f"""Simplify check: are the three counter scripts
(`{LANE}/census/round-26/c1-counter.sh`, c2-counter.sh, c3-counter.sh) minimal and correct for
their frozen predicates? Does c1's awk match heading lines the file actually contains (verify
against the real headings at {FREEZE})? Does c2's `grep -l ... | wc -l` correctly count
FILES (not lines)? Does c3's presence check + tool run print both the marker and the tool's
stdout (does the receipt capture the tool's exit code correctly — is `axis_check_exit` the
tool's real exit)? Report any bug or simplification.""")

    add("DistilFindings", "distiller", f"""Late-wave duty: read all completed
`{LANE}/.ufo/waves/round-26/{WAVE}/*.md` reports, deduplicate findings across seats, and produce
`{LANE}/.ufo/waves/round-26/{WAVE}/distill-findings.md`: one line per distinct finding with its
strongest seat pointer + severity (attack/observation/finding); flag any two seats that
disagree on the same fact. If fewer than 10 reports exist when you run, report that and stop.""")

    add("RevEntryDrafts", "reviewer", f"""Review the two entry drafts once they appear (check
`{LANE}/.ufo/waves/round-26/{WAVE}/entry-*.md`; if absent when you run, review the staged
sources directly): verify every `source:` lane-id maps to the correct document (S128=git-fetch
docs, S129=builtins, S130=pull.c, S131=trigger fixture, S132=worktree census); every quote is
<=25 words and located; front matter trio present; `ground: F1` line present; no claim rests on
an unappended row; entry B's staged-S131 citation is re-pointed to S132 without naming the
unadmitted file. Report per-entry: admit-ready / defect-at-line.""")

    add("CritCoverageCredit", "critic", f"""Falsify C2's coverage credit: is adding two F1 entries
expansion 'on ground the coverage map did not hold' (LEARNING.md) or deepening held frontier
ground? The lane's r25 closure called a same-ground entry 'quality improved, expansion
unchanged'. Read corpus/README.md F1 row + the r24/r25 lessons' expansion verdicts; rule whether
C2's K1 counter (grounded-F1 0->2) honestly measures a coverage move or just an entry count.
Report the honest verdict and the exact sentence the report should use.""")

    add("MutEntryLocators", "mutation-tester", f"""Mutation-test the entries' Gate locators: for each
planned snapshot § locator (git-fetch § OPTIONS switch text; builtin files :2926/:509/:572/
:1942/:1965; pull.c :392), check whether the actual snapshot bytes contain that heading/line —
fetch a copy yourself to /var/tmp or read the staged evidence. Mutate: cite § ENVIRONMENT for a
switch documented under § OPTIONS (Q54 heading-set rule — does the gate catch it?); cite a line
number one off the real call site. Report which locator mutations the K2 gate would catch.""")

    add("LabGitVersion", "labrat", f"""Runnable probe: `git --version` on this host (expect 2.56.0)
and `git -C {LANE} config --list --show-origin | grep -iE 'maintenance|gc\\.|worktree'` — report
the effective maintenance config of the LANE repo itself (does the lane hold its own prune
risk? this grounds the fleet-exposure denominator language in entry B). Also verify the host's
`man git-fetch` documents --auto-maintenance (grep the installed man page). Paste outputs.""")

    add("RevQ59Text", "reviewer", f"""Review the Q59 criterion draft (from ScribeAxisDocs if landed,
else draft it yourself in your report): does the criterion correctly capture 'a preregistered
claim's declared axis must match the class of surface it changes', does it cite the right
lessons (r25 misattribution R25 axis + this round's R26-M1), is the test column executable (the
C3 fixture command), and does it avoid overreach (it checks declared-vs-surface class, not
semantic correctness)? Also check it doesn't contradict Q58 (base-derived targets) — the two are
adjacent but distinct.""")

    add("CritSourcedClaim", "critic", f"""Verify the §2b sourced-claim requirement: the round needs
>=1 claim resting on a SOURCES.md row opened THIS round. C2's entries cite S128-S132 — are those
rows OPENED this round (opened=2026-10-25, the lane's own re-open, not the campaign's 2026-10-23)?
If a row's `opened` cell wrongly reuses the campaign date, the sourced-claim fails its own gate.
Check the staged rows' opened cells and the prereg's instruction (opened=2026-10-25); flag if any
draft row keeps the campaign date.""")

    add("LabK4Tip", "labrat", f"""Runnable probe (final-state projection): in a private
--no-local clone of the lane at {FREEZE} under /var/tmp, simulate C2's landing: copy corpus/,
append the five normalized rows (draft them from staged rows if the scribe block isn't ready),
drop the two entry files at corpus/knowledge/, update the F1 row, then run
`python3 -B tools/souji-coverage-agreement.py --root <clone> --rev <cloned-tip>` — does it print
grounded=9 mapped=9? This is a PROJECTION, not claim evidence; label it as such.""")

    add("ExecReportDirSetup", "executor", f"""Create the wave evidence scaffold the L1 commits:
deliver at `{LANE}/.ufo/waves/round-26/{WAVE}/evidence-checklist.md` — the ordered list of every
path this round adds under census/round-26/ (records/, sources/, counter scripts already
committed) and .ufo/waves/round-26/ (spec, dispatch, ready, results, seat reports), with the
commit grouping the L1 should use (per-claim landing commits + bookkeeping). Cross-check against
the actual directory now and at your finish time.""")

    # ============ More attack seats ============
    add("RevR25Residuals", "reviewer", f"""Review routed residuals from the r25 spotcheck for this
round's coverage: read `{LANE}/corpus/lessons/round-25-verifier-spotcheck.md` 'Routed defects'.
Which of its 4 items does this round address (D1 axis-check + QUALITY criterion + mistakes row =
C3; D2 red-arm receipts before after-data = the round's receipt ordering; D3 operator-sweep
leftover = NOT addressed — is that a defensible lane doctrine? the lane's doctrine says
never-read/never-stage operator sweep content; check SKILL/README wording and say whether
leaving it named-but-untouched is consistent); D4 SHONEN boxes. Report per-defect: addressed /
routed-forward / defended.""")

    add("CritQ54Gate", "critic", f"""Falsify the Q54 applicability: the C2 entries' Gate locators
must resolve to snapshot headings. Check whether `tools/souji-gate-check.py` actually enforces
snapshot § locators for THIS entry shape (front matter source: lines + body quotes vs the
staged entries' format) — read its snapshot resolution and locator extraction; name the exact
locator strings the tool will try to resolve for entry A and B. If the tool cannot see a
locator the entry uses, that's a gate hole — report it.""")

    add("MutFreezeOrder", "mutation-tester", f"""Mutation-test the amendment ordering claim: the
prereg says amendment 1 was logged BEFORE any seat scored. Check `git -C {LANE} log
--format='%H %ct %s' -3` timestamps: was the freeze (12fd90b) BEFORE the red receipts commit
(89e0fce), and were BOTH before this wave's spawn? Mutate the claim: what if a seat had already
produced green data before the amendment — would the prereg's own rules catch it? Report the
actual ordering evidence + the hole if any.""")

    add("RevClaimSeparation", "reviewer", f"""Verify causal separability concretely: produce three
counterfactual checks — (i) if C2's assimilation were reverted, would C1's counter and C3's
fixture still pass? (ii) if C1's SCORECARD surgery were reverted, would C2's K4 counter still
print grounded=9 (careful: does the map-agreement tool read SCORECARD? no — it reads corpus/;
verify by reading the tool) and C3's self-host still run? (iii) if C3's tool were reverted,
would C1/C2 counters still verify? Only C1's SCORECARD edit could conceivably disturb C3's R3
(axes table scores) — confirm the C1 kill rule forbids axes-table changes so the ordering
holds. Report the separability verdict with the tool-read evidence.""")

    add("SonicSpecCount", "sonic", f"""Mechanical: count the spec's seats and role mix — load
`{LANE}/.ufo/waves/round-26/w1-spec.json`, print Counter(role) and the total, flag whether
m_flash-routable roles (executor/labrat/scribe/sonic/simplifier) are >=50% and attack roles
(reviewer/critic/mutation-tester/labrat) are >=25%. Paste numbers only.""")

    add("ScoutPromptFidelity", "scout", f"""Check this round's prompt fidelity: compare
`/home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-26.md` against the fleet's round-prompt
template (`{FLEET}/templates/round-prompt.md` or the r25 prompt's shape): does it carry the full
contract (mission/axes binding, 1-3 claims + falsifiability, frontier step, L2 floor, report
contract, commit/push/L0) and the hyaku run-7 addendum? Report missing/added sections by heading.""")

    add("CritSelfHost", "critic", f"""Falsify C3's self-host claim: the tool must print `claims=3
flags=0` on this prereg + scorecard. Attack: (a) does the MACHINE BLOCK parse survive the
amendment (the amended C2 K4 lines sit OUTSIDE the block — verify); (b) R4 scans claim blocks
for universal words — does 'no' appear in C1's block (e.g. 'no score move' prose)? the block is
only the MACHINE BLOCK lines — check what exactly the tool parses vs the prose claims below;
(c) could the scorecard's axes-table parse break if a row's score cell contains prose like
'unprovable-but-better'? Read the actual axes rows at {FREEZE}. Report flag risk per rule.""")

    add("LabC1AfterSim", "labrat", f"""Runnable probe: simulate the C1 surgery in a private clone
under /var/tmp at {FREEZE}: apply the planned edit (delete scaffold lines, insert r24 table above
r23 heading, add capability rows + planned bullets), then run `bash census/round-26/c1-counter.sh`
inside the clone — print markers and headings. Expected post-edit: markers=0, headings ordered
per K2. Paste the simulated output + the exact sed/awk you used. PROJECTION label required.""")

    add("RevGateTool", "reviewer", f"""Review the C2 gate's actual coverage: read
`tools/souji-gate-check.py` end-to-end. What does it verify for each named entry (provenance
trio presence, snapshot existence per cited row, § locator resolution, quote length, pipe-escape,
slice files)? Which of the prereg K2/K3/K4 predicates does it NOT cover (registry row count,
histogram deltas, coverage-agreement)? List the gate's blind spots so the report doesn't
overclaim 'the gate passed' => 'the claim held'.""")

    add("SonicSourcesGrep", "sonic", f"""Mechanical greps at {FREEZE}: (a) `git -C {LANE} grep -c
'^ground: F' {FREEZE} -- corpus/knowledge/` per-ground histogram (F1/F2/F3/F4/F5 counts);
(b) `git -C {LANE} grep -l 'ground: F1' {FREEZE} -- corpus/knowledge/` (expect empty);
(c) highest S-id in `{LANE}/corpus/SOURCES.md` (`grep -oE 'S[0-9]+' corpus/SOURCES.md | sort -V |
tail -3`); (d) `ls {LANE}/corpus/knowledge/ | wc -l`. Paste raw outputs only.""")

    add("DistillPlanCheck", "distiller", f"""Dedupe this round's claim set against prior rounds:
does C1 duplicate any earlier SCORECARD-consistency claim (search LOG.md + lessons for
'scaffold', 'template', 'generation block', 'bookkeeping matches')? Does C3's axis-check overlap
the r25 kill-rule instrument or Q58? Does C2's F1 theme overlap anything already admitted (the
existing F1 entries' scope lines)? Report overlap verdicts: new / extends-Sxxx / duplicates.""")

    add("SimplPlan", "simplifier", f"""Simplifier sweep: is any planned artifact redundant? Check
whether (a) the c1/c2/c3 counter scripts could be one script; (b) the SCORECARD surgery could
avoid moving the r25 table (does the file's actual 'newest first' contract already hold with r25
at the end — is the contract the awk counter or the prose?); (c) Q59 vs the C3 tool (one is the
criterion, one the instrument — needed both?); (d) any deliverable a seat produces that the L1
doesn't land. Report keep/cut with reasons.""")

    add("LabAxisCase12", "labrat", f"""Runnable probe for C3 case 12: write a throwaway stub tool at
`/var/tmp/souji-r26-LabAxisCase12/stub.py` that prints `claims=1 flags=0` for any input, then
specify exactly how the fixture must distinguish FALSE-GREEN-ACCEPTED (stub passed the cases it
should fail) from FALSE-GREEN-REJECTED (stub correctly rejected). Is checking the last line
enough, or must the fixture run the stub against the r25-C2 replica and require flags>0? Report
the exact control-arm semantics the fixture needs.""")

    add("RevAssimRules", "reviewer", f"""Review the C2 assimilation against every §10 contract rule:
(1) one theme + 1-3 entries — is 'trigger set' ONE theme across two staged packages (round1 +
round2)? (2) per-entry PROVINCE scope (F1 fit); (3) QUALITY bar per entry; (4) expansion credit
ground; (5) id-collision check + scratch renumber BY DOCUMENT (not arithmetic); (6) scratch
mirror + census --file exit 0 BEFORE append; (7) rows normalized (no `|`, valid recheck,
used-by); (8) Gate records >=1 admit + >=1 reject; (9) own-work rows re-grounded; (10) nothing
written into {SK}. For each rule name the artifact step that satisfies it and flag any step the
current plan skips.""")

    add("SonicRowSchema", "sonic", f"""Mechanical: for each of the 5 staged rows (S109/S110/S111/
S123/S131 in `{PKG}/SOURCES.append.md`), print field counts (`awk -F'|' '{{print NF}}'` — expect
13) and flag cells containing `|` escapes or prose recheck values that violate the fleet schema.
Paste the per-row field-count line and the offending cells only.""")

    add("CritAmendNeed", "critic", f"""Decide whether the prereg needs amendment 2: attack the
prereg for (a) the C3 tool's R2 neutral classes ('receipt-binding','measurement') — are these
defined anywhere or left to abuse? (b) C2 K3's row count 127->132 — is 'net new rows' the right
predicate when a staged row could legitimately supersede (append-only forbids edits, so net-new
is forced — verify)? (c) C1's protected-region definition 'base lines 1-171 minus Planned
section 95-137' — does it correctly allow the planned-bullet additions INSIDE Planned while
forbidding Axes-table changes? Propose the amendment text if a hole is real.""")

    add("LabManifestDiff", "labrat", f"""Runnable probe: diff the staged append file's schema
against the lane registry's: for the 5 staged rows compute normalized forms (fix recheck cells
to bare cadence + date, strip `|` content, set used-by) and show the exact byte-diff vs the
staged originals — the diff the mirror will contain. Paste both staged and normalized row bytes
in your report.""")

    add("RevTrendWording", "reviewer", f"""Draft-review the trend verdicts: given this round's
claims, what are the honest trend verdicts? Expansion: C2 adds 2 entries on F1 (held frontier
ground — is that 'improved' or 'unchanged' per the r25 precedent where a same-ground entry was
'expansion unchanged'?); quality: C3 instrument + C1 consistency repair; discernment: the Q58
catch + Q59 + the spot-check history. Write the three verdict sentences the report should use,
each with its evidence pointer. Honest, not padded.""")

    add("MutCounterStub", "mutation-tester", f"""Mutation-test the counter scripts: could a broken
integration still print green? Mutate: (a) c1-counter greps SCORECARD.md but the surgery leaves
a SECOND SCORECARD (e.g. a backup file) — does any counter read only the right file? (b) c2's
ground grep counts files with `ground: F1` anywhere in corpus/knowledge — could an entry's
escaped '\\`ground:' or a comment line false-match (check `grep '^ground: F1'` semantics vs the
tool's own parse)? (c) c3 prints the tool's output but does the receipt's verify re-run the
command or just hash it (read souji-receipt-run.py verify semantics — does verify=ok mean 'bytes
bind correctly' not 'output is true'?). Report the false-green paths.""")

    add("ScoutR24Residuals", "scout", f"""Enumerate the open residual lists for the report's
'carried forward' section: read `{LANE}/corpus/lessons/round-25.md` Boundaries + the
`.ufo/waves/round-24/w1/RevR23Residuals.md` 20-item list (which are still open per the r25
disclosures: 1 closed, 6 narrowed, 12 open, 1 open-by-design) and the r25 Routed-defects 4 items.
Produce the consolidated open-items list the r27 planned line must carry.""")

    add("LabSparseClone", "labrat", f"""Runnable probe: can the receipt runner's private clone
handle this round? Read `tools/souji-receipt-run.py` run path (sparse-checkout note about the
operator-sweep blob tree) — does the clone correctly materialize `census/round-26/` and
`tools/` paths at the named revs? Run the verify on one committed red receipt and paste output;
then run a NEW `run` at {FREEZE} for c1-counter (already done by L1 — just re-verify the
committed receipt bytes: `python3 -B tools/souji-receipt-run.py verify --root . --rev
12fd90bcd9cdfab495e178023eeaa838a977fcbe census/round-26/records/c1-before.tsv`).""")

    add("CritSourceTiers", "critic", f"""Falsify the five new rows' tiers: staged S109/S110/S111 are
tier A (docs/code primary); S123/S131 are own-work tier A (campaign evidence). Is a
campaign-authored fixture/census really 'the lane's own re-runnable gate output' (the A-tier
definition)? The lane did not author or run it — is tier A defensible, or must they be B
('strong secondary')? If B, the append block must carry tier=B. Rule on the tier with the
contract text; flag if the scribe's draft rows mislabel.""")

    add("RevMirrorGate", "reviewer", f"""Review the scratch-mirror gate order: the contract requires
the mirror census --file to exit 0 BEFORE the first registry append. Walk the L1's planned
landing order (prereg -> red receipts [done] -> wave -> entries+rows appended together in ONE
commit after mirror validation -> README F1 row -> after receipts). Is the mirror built BEFORE
the real append commits (verify the sequence has no path where SOURCES.md gains rows before the
mirror validates)? Report the required commit order the L1 must follow.""")

    add("SonicReadmeRows", "sonic", f"""Mechanical: paste the exact bytes of `{LANE}/corpus/README.md`
lines 37-41 (coverage map header + F1 row + F2 row) and of the staged
`{PKG}/SOURCES.append.md` rows S109/S110/S111/S123/S131 (full lines). Also list filenames in
`{LANE}/corpus/knowledge/` matching `*maintenance*` and `*trigger*`. Raw output only.""")

    add("LabSelftestShape", "labrat", f"""Runnable probe: check `--selftest` conventions across
lane tools so the C3 selftest matches: run `python3 -B tools/souji-rev-pin.py --selftest` tail
and `python3 -B tools/souji-cert-evidence.py --selftest | tail -2` (paste final lines + exit
codes). Report the expected selftest output shape and whether a bare `pass`/`fail` line or the
'N/N' convention is standard. Also `python3 -m py_compile` the C3 fixture draft if it exists.""")

    add("CritEntryB", "critic", f"""Falsify entry B's strongest claim: 'all four commands prune
(2->1)'. The fixture evidence is the CAMPAIGN's run (S131 staged row), not the lane's. Does the
entry's verified-at honestly distinguish 're-grounded by reading the campaign evidence file' from
'measured by this lane'? Where must the entry say 'measured in campaign evidence
lanes/souji/round2/evidence/r23-trigger-prune.out, verified by this lane by reading it' vs imply
the lane ran it? Draft the exact honest wording for the entry's verified-at and the Gate's quote.""")

    add("MutK4Base", "mutation-tester", f"""Mutation-test the K4 base receipt: c2-k4-base.tsv was
generated at rev 0eca7c8 (the base itself) — but the receipt tool measures in a private clone;
verify the receipt's rev matches the claim's named base and that grounded=7 there matches a
manual recount at that rev: `git -C {LANE} grep -l '^ground: F' 0eca7c8 -- corpus/knowledge/ |
wc -l` (should be 7) and cross-check the tool's mapping logic handles the F1 row lacking a
ground: line on existing entries. Paste recount + explain any diff.""")

    add("LabReadmeF1", "labrat", f"""Runnable probe: enumerate every coverage-map row whose ground
cell starts with a letter+digit token in `{LANE}/corpus/README.md` (there may be multiple F1/F2
rows across r12/r13/r17/r18/r19/r24 sections — `grep -nE '^\\| *F[0-9]'`); for each row print its
entries cell; identify WHICH row the two new entries must be named in (the earliest active F1
row? the Q56 rule: 'a coverage-map row whose ground cell starts with F<k>' — could naming them
in a LATER F1 section row satisfy it, or must it be the r12 row at :39?). Report row numbers +
which the coverage-agreement tool reads.""")

    # ============ Remaining seats to 70 ============
    add("ExecVerifyLoop", "executor", f"""Write the L1's post-integration verify loop at
`{LANE}/.ufo/waves/round-26/{WAVE}/verify-loop.sh` (runnable, the L1 executes after each claim
lands): runs the three counters, the C2 gate command, the coverage-agreement K4 command at the
current tip, the landing gate (--round 26), and the six manual SOURCES census greps; prints a
`CHECK <name> PASS|FAIL` per command with the raw value. Read-only script; hard-code the frozen
commands from the prereg.""")

    add("ScoutShonen", "scout", f"""Read `{LANE}/SHONEN.md` and the r25 spotcheck's D4 note
('all four are plausibly non-author checkable next round'). For each of the four boxes, state
the exact resolvable pointer it currently names and whether this round's work lets any box move
to `[x]` (the promotion is operator-owned — the lane only records `[~]`/`[ ]`; report what would
qualify). Deliver the report-ready SHONEN lines.""")

    add("CritReportContract", "critic", f"""Pre-attack the report contract: list every required
section of `.ufo/reports/round-26/souji.md` (Work performed / Landed changes / Before-after
measurements / Sources & frontier / Trend verdicts / SHONEN / Stale-lane line / tool installs)
and, for each, the failure mode that makes it contentless per the marker rule. Also check the
SHONEN heading grep (`grep -c '^## SHONEN'` must equal 1) and the per-box `[~]`/`[ ]`/`[x]`
rule. Deliver the checklist the L1 writes against.""")

    add("RevSourcesRows", "reviewer", f"""Review the final append block bytes (from ScribeSourceRows
or the mirror): each row must have NF=13 fields, valid kind/tier/status enums, recheck = ISO
date|NNd|cadence token only, opened=2026-10-25, no `|` chars, used-by naming exactly the admitted
entries. Hand-check all 11 columns per row against CORPUS.md contract v1. Report per-row verdict.""")

    add("LabQ56Mechanics", "labrat", f"""Runnable probe: trace `tools/souji-coverage-agreement.py`'s
mechanics — how it finds `ground:` lines (file glob + regex), how it maps entries to coverage-map
rows (backticked knowledge/<name> in entries cell of a row whose ground cell starts with F<k>),
and how --base-rev differs from --rev. Verify the K4 predicate 'grounded=9 mapped=9 kill_tested=7'
is what the tool would print after the C2 landing (simulate on the /var/tmp clone if time).
Paste the tool's parse code lines that implement each piece.""")

    add("MutProvenance", "mutation-tester", f"""Mutation-test the entries' provenance trio: front
matter needs source:/verified-at:/recheck:. Mutations: (a) source: citing a staged S-id not a
renumbered lane id (does the gate catch it? does Q54?), (b) verified-at using the campaign date
2026-10-23 instead of the lane's re-open 2026-10-25, (c) recheck naming a command that references
staged evidence paths (lanes/souji/...) instead of lane-visible ones, (d) missing `ground: F1`
(would K1 or K4 catch which?). Report per-mutation which counter/gate fires.""")

    add("ScribeReportDraft", "scribe", f"""Draft the round report skeleton at
`{LANE}/.ufo/waves/round-26/{WAVE}/report-draft.md` in the required section order (Work performed
/ Landed changes / Before→after measurements / Sources & frontier / Trend verdicts / SHONEN /
Stale-lane / installs) with EVIDENCE-PENDING placeholders for the L1's measured values, the
round's declared claims named at top, and a per-section checklist of what the L1 must fill.
Mirror `.ufo/reports/round-25/souji.md` structure (read it).""")

    add("ExecCensusAfter", "executor", f"""Prepare the round-end census recipe at
`{LANE}/.ufo/waves/round-26/{WAVE}/census-after-recipe.md`: the exact validate --root command
plus the six manual census greps to paste as 'after' evidence, plus the row-count and histogram
deltas expected (127->132 rows, A-tier +3? compute from the append block tiers, mined +5,
queued 0). Deliver the expected-delta table for the report.""")

    add("RevToolSafety", "reviewer", f"""Safety-review the C3 tool spec: does it read anything
outside named inputs (prereg + scorecard paths)? Does --prereg/--scorecard handle symlinks,
non-files, absolute escapes? Must it refuse when paths are identical (prereg==scorecard)? Does
the fixture's stub-arm create executable files under /var/tmp only and remove them? Flag every
input-hygiene hole the implementation must close.""")

    add("LabJunction", "labrat", f"""Runnable probe: the C3 fixture writes synthetic prereg files —
verify on this host that python3 can `os.chmod`/`tempfile.mkdtemp` under /var/tmp and that a
fixture invoking `sys.executable -B <tool>` on synthetic files works; then hand-run the tool's
R4 semantics on one synthetic block (`CLAIM C9\\naxis: coverage\\nsurface-class: knowledge-entry\\n
... 'no unpushed commits'` — with vs without an enumerate: line) using your own 20-line reference
implementation. Paste the reference code + outputs.""")

    add("SonicToolsList", "sonic", f"""Mechanical: list `{LANE}/tools/` and `{LANE}/tests/fixtures/`
matching `*axis*` (expect none); count tools (`ls tools | wc -l`) and fixtures (`ls tests/fixtures
| wc -l`) at {FREEZE}; `git -C {LANE} log --oneline -3` for context. Raw output.""")

    add("CritNoHarm", "critic", f"""Falsify 'no axis is harmed': for each claim, name the axis that
could be harmed and the evidence that rules it out: C1's surgery could break SCORECARD's own
integrity (calibration); C2's assimilation could add a bad row/entry (coverage/quality);
C3's new instrument could be wrong and bless future bad claims (calibration, indirectly). Also:
does moving the Round 24 table out of the fence LOSE information vs keeping the fence? Check
whether the fence content is byte-identical to what a correct r24 table should be — if the
fenced copy has defects the L1 must not silently propagate them.""")

    add("SimplReport", "simplifier", f"""Simplify check on the report plan: list deliverables the
wave produces that the report does NOT need (duplicate receipts, intermediate drafts) and any
planned artifact that duplicates an existing counter (e.g. is the c2-k4 receipt necessary when
the coverage-agreement receipt exists?). Suggest the minimal evidence set for each claim. Do not
recommend cutting required gates.""")

    add("LabQ54Locators", "labrat", f"""Runnable probe: for each snapshot the C2 entries will cite,
check Q54's heading-set rule: extract candidate § locators from the staged entries' source lines
(e.g. '§ OPTIONS', 'builtin/fetch.c:2926', 'builtin/pull.c:392') and verify a real
`tools/souji-gate-check.py` locator parse would resolve each (read the tool's locator→heading
extraction for man-page vs code-file snapshots). Report the exact locator spellings that pass.""")

    add("RevCensusSchema", "reviewer", f"""Review the append block against census schema: verify
kind values are in the enum (docs/code/own-work allowed), tier A/B/C letters only, status
queued/mined/rejected only, `used-by` paths comma-separated or `—`, `opened` is ISO date,
`recheck` is ISO|NNd|symbolic. Read CORPUS.md contract v1 column definitions and rule on each
of the 5 rows' planned cells. Report per-cell violations found.""")

    add("MutFixtureIsolation", "mutation-tester", f"""Mutation-test fixture isolation: the C3
fixture creates synthetic prereg/scorecard files under /var/tmp. Could a fixture bug make it
read the REAL prereg/scorecard (e.g. absolute path leak, cwd fallback)? Check the fixture draft's
path handling once it exists — or enumerate the leak patterns the implementation must avoid
(env var override, relative resolve). Also: does case 11's 'malformed -> exit 2' distinguish
exit 2 from exit 1 (a crash could print wrong code)? Report the isolation requirements.""")

    add("ScoutWavePrompt", "scout", f"""Read `.ufo/waves/round-26/w1-spec.json` items list: which
items write delivery files vs reports-only? Build the role->deliverable matrix (executor files
the L1 copies, scribe drafts, read-only analyses). Flag any two seats assigned overlapping
deliverable paths. Also flag any item whose prompt asks for a production edit (should be none —
L1 is integrator).""")

    add("CritAdmissionHistory", "critic", f"""Compare this round's claim pattern against the lane's
last three outcomes (r24 admitted?, r25 honest-stop, r23 admitted): does the round design avoid
the r25 failure mode (axis misattribution caught late) and the r24 mode? Specifically: C3 IS the
instrument that catches the r25 failure — does claiming it on operability repeat the same
misattribution risk (an instrument catching calibration defects declared as operability —
fixture-expansion-like)? Apply the checker's own R2 to C3: 'instrument-acquisition->operability
only' — is the claim honestly operability (new runnable gate) or is it calibration wearing a
tool costume? Give the verdict the closure will most likely reach, with precedent pointers.""")

    add("ExecResultsCount", "executor", f"""Write the wave-results counter at
`{LANE}/.ufo/waves/round-26/{WAVE}/results-count.py`: reads
`{LANE}/.ufo/waves/round-26/{WAVE}-results.json` (when it lands), prints `seats=N dead=D
roles=role:count...` and per-seat name/agent/status, matching how the L1 must report 'seats,
dead seats and role mix from results.json'. Include the dead-seat error text extraction.""")

    add("LabGateSliceArms", "labrat", f"""Runnable probe: the K2 gate command passes empty
--slice/--slice-verdicts files. Read the gate tool's slice handling — do empty files make the
slice arm inert (prints slice_verdicts=0) or do they need specific headers? Create the empty
files in /var/tmp, run the tool's slice arm against a dummy entry set to see the output shape,
and report what `entries=2 ok=2` vs `slice_verdicts=` the real run will print.""")

    add("RevC2Kill", "reviewer", f"""Review C2's kill rule completeness: it lists row count,
malformed, duplicate, enum, used-by-missing, locator failures, pipe-escapes, unappended-citations,
writes to {SK}. Missing candidates to rule on: (a) a new entry whose front matter is malformed
(does K2 gate catch?), (b) the README F1 row edit breaking Q56 for OTHER entries, (c) a row
whose source URL fails to resolve TODAY (should the gate re-fetch? no — the Gate quote is the
evidence; is that enough?), (d) an entry citing S128-S132 with a wrong document (does anything
check id->document mapping?). Say whether each gap needs a kill-rule arm amendment.""")
    add("ExecReportAssemble", "executor", f"""Write the L1's report assembler at
`{LANE}/.ufo/waves/round-26/{WAVE}/report-assemble.py`: reads the wave results json +
the committed receipts under census/round-26/records/ + the lesson + LOG and emits a
filled `.ufo/reports/round-26/souji.md` draft at `{LANE}/.ufo/waves/round-26/{WAVE}/report-rendered.md`
with every section populated where data exists and `RECEIPT-PENDING` where not. The L1
reviews and files the real report. Include a `--check` mode that verifies the draft has
all required sections and exactly one `## SHONEN` heading.""")

    add("ScribeQ58Note", "scribe", f"""Draft at `{LANE}/.ufo/waves/round-26/{WAVE}/q58-note.md`:
the LOG.md + lesson text recording the Q58 catch (amendment 1): the K4 literal was
copied from r25's base (6) before the true base count (7) was re-derived — exactly the
R25-M1 class caught pre-data. Also the one-line note for the lesson's Process
deviations that the amendment was logged before any seat scored.""")

    add("ExecShonenFile", "executor", f"""Draft the report's SHONEN section at
`{LANE}/.ufo/waves/round-26/{WAVE}/shonen-lines.md`: four lines, one per SHONEN.md box,
each `[~]` with the resolvable pointer (read `{LANE}/SHONEN.md` and the ScoutShonen
findings if landed). Also a `--check` style assertion list the L1 runs before filing:
`grep -c '^## SHONEN' <report>` must print 1.""")

    add("ExecCensusTables", "executor", f"""Write the before/after census delta table at
`{LANE}/.ufo/waves/round-26/{WAVE}/census-delta.md`: run the six manual census greps
from `{LANE}/CORPUS.md` §Census on `{LANE}/corpus/SOURCES.md` NOW (before state) and
paste outputs; also print the expected after-state deltas given the 5-row append
(rows 127->132, tiers/mined deltas from the append block tiers). Deliver the
paste-ready before/after block for the report's Sources & frontier section.""")

    CUT_NAMES = {
        "LabJunction", "SimplReport", "LabSelftestShape", "CritReportContract",
        "ExecReportDirSetup", "ScoutWaveEvidence", "LabSparseClone", "LabQ54Locators",
        "LabAxisCase12", "LabManifestDiff", "LabGateSliceArms", "MutFixtureIsolation",
        "MutK4Base",
        # attack/recon rebalance toward >=50% m_flash seats
        "RevSourcesRows", "CritC2Admission", "CritSourceTiers", "CritSelfHost",
"MutProvenance", "MutReadmeF1", "ScoutPromptFidelity", "LabK4Tip",
        "ScoutR24Residuals",
    }
    kept = [i for i in ITEMS if i["name"] not in CUT_NAMES]
    # labrat is a frozen-topology seat (per-child of an executor), not a swarm
    # role: runnable probes/mechanical seats ride executor instead.
    kept = [
        {**i, "role": "executor"} if i["role"] in ("labrat", "sonic") else
        ({**i, "role": "scout"} if i["role"] == "distiller" else i)
        for i in kept
    ]
    return {
        "wave": "souji-r26-w1",
        "reportDir": ".ufo/waves/round-26/w1",
        "maxLanes": 100,
        "context": context(goal),
        "items": kept,
    }


if __name__ == "__main__":
    spec = spec()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "w1-spec.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(spec, fh, indent=1, ensure_ascii=False)
    print(f"wrote {out}: items={len(spec['items'])}")
    print(Counter(i["role"] for i in spec["items"]))
