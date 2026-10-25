#!/usr/bin/env python3
"""Generate the souji round-23 wave-1 spec (one v1 wave).

Run: python3 .ufo/waves/round-23/make-spec.py
Writes .ufo/waves/round-23/w1-spec.json next to this file.
"""
from __future__ import annotations

import json
import os

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
GODSPEED = """You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls."""

CONTEXT = f"""# Goal
Souji round 23 (hyaku, in-session L1 lane subagent). Lane: fleet repository & workspace hygiene
(掃除). Axes: calibration (7, the lane's lowest), operability (8), coverage (8); no axis may be
harmed. Three claims frozen before data in {LANE}/.ufo/waves/round-23/preregistration.txt:
C1 record agreement (calibration), C2 blob-bound receipts (operability), C3 one assimilation
theme on F2 size census (coverage). Lane base 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd.
Inbound work: {LANE}/corpus/lessons/round-22-verifier-spotcheck.md sections 5-7
(routed defects D1-D8).

# HARD BOUND (violating this voids your seat)
souji is a hygiene lane, but its write scope is its own repo only. **Never delete, move,
quarantine or classify-for-cleanup anything in {FLEET} outside {LANE}/.** Incident 2026-10-25:
the fleet's tracked .scratch/ tree was deleted mid-run by an unidentified seat. Never touch
{FLEET}/.scratch/, {FLEET}/.ufo/state/, {FLEET}/.ufo/watchdog.log, MANIFEST.json, the fleet
scripts/ or templates/, any sibling lane repo, or the lane's jj state / git index.

# Contract
- Read {LANE}/.ufo/waves/round-23/preregistration.txt FIRST. It is the frozen counter contract;
  never propose changing a predicate, target or key set after data. If you believe a counter is
  ungameable-wrong, say so in your report as an ATTACK, do not edit it.
- You are a READ-ONLY seat unless your item names a delivery file. Read what you need; run
  read-only commands; write ONLY your own report. No `git add`, `git commit`, `git push`, `git
  stash`, `git checkout`, `jj` mutation, no `rm`/`mv` anywhere, no signals. Shell scratch, if you
  need it, goes under `/var/tmp/souji-r23-<YourName>/` and you remove it before you finish.
- Absolute paths only. Your tools start at the FLEET root, not the lane: every lane path must be
  written as {LANE}/<path>. A relative path lands in the wrong repo.
- Every `Report:` trailer path the harness renders is relative to {LANE} — write it at
  {LANE}/<that path>.
- Do not run `git` inside the lane to create state: read-only `git log/show/diff/status/ls-tree/
  cat-file/rev-parse` are fine. Landing happens only through the L1's jj helper.
- A source claim needs a location: URL or repo path plus the line/section, and a <=25-word quote
  verbatim where your item asks for one. Quotes must be copied from bytes you opened this run and
  must not contain a literal or escaped `|` (they become SOURCES.md cells).
- Unrun checks have not passed. Never report an execution you did not perform; label inference
  as `[INFERENCE]`.
- Tooling is authorized (operator 2026-10-19): you may install or upgrade tools that help the
  task; read /home/vgpnk/.omp/agent/RULES.md first (official channels only, record tool/version/
  channel/reason in your report). **pacman transactions are PAUSED host-wide**: install via
  `uv tool`/`npx`/an official binary into `~/.local/bin`, or file nothing and route around it.
  Never run `pacman -S/-Sy/-Syu/-U/-R` or restart a host service.
- Certification OFF, K5 HELD, F5 reap + NAMESPACE holds unchanged. No credentials, no live /proc
  census, no operator-sweep contents, no `.scratch/` contents.

# Output shape
Markdown report at your rendered `Report:` path: `## Status` (one line, `STATUS: PASS|PARTIAL|
FAIL` + why), `## Evidence` (command, output excerpt, revision), `## Findings` (numbered,
each with its location), `## Attack log` where your item is an attack. Be terse; no filler.
"""


def item(name: str, role: str, task: str) -> dict:
    return {"name": name, "role": role, "prompt": "/skill:godspeed\n" + GODSPEED + "\n\n## Task\n" + task}


ITEMS: list[dict] = []


def add(name, role, task):
    ITEMS.append(item(name, role, task))


# ---------------- C3 source opening (scouts) ----------------
add("ScoutCountObjects", "scout", f"""Open **https://git-scm.com/docs/git-count-objects** live (git 2.56.0 is the host version) and
record, for our C3 entry, exactly what `-v/--verbose` reports.
Deliver: (1) the full field list in the page's own order; (2) a located quote (<=25 words, verbatim,
NO literal or escaped pipe character) for the `garbage`/`size-garbage` fields and for `alternate`;
(3) the section/anchor name you took each quote from and the access date 2026-10-25; (4) run
`man git-count-objects 2>/dev/null | head -80` and say whether the installed page is present and
agrees, quoting the same fields if it does. Also state plainly whether the page documents any
WRITE side effect of `count-objects`.
Report path to ask for: `.ufo/waves/round-23/w1/ScoutCountObjects.md`.""")

add("ScoutFsck", "scout", f"""Open **https://git-scm.com/docs/git-fsck** live and record what the reachability census may and may
not run. Deliver: located quotes (<=25 words verbatim, no pipe characters) for `--unreachable`,
`--dangling/--no-dangling`, `--no-reflogs` and `--lost-found`; the DESCRIPTION's statement of the
default head set; and one explicit line answering: **which of these options writes into the
repository, and where?** Give the exact path pattern the page names. Access date 2026-10-25.
Then check the installed `man git-fsck` and say whether it agrees.
Report path to ask for: `.ufo/waves/round-23/w1/ScoutFsck.md`.""")

add("ScoutPrune", "scout", f"""Open **https://git-scm.com/docs/git-prune** live. Deliver: located quotes (<=25 words verbatim,
no pipe characters) for the DESCRIPTION's prune scope ("unreachable unpacked" vs packed objects),
for `-n/--dry-run`, and for `--expire <time>`; plus the page's own recommendation about `git gc`.
Then answer one question with a quote: **is the set `git prune -n` reports the same set
`git fsck --unreachable` reports?** Access date 2026-10-25. Compare the installed `man git-prune`.
Report path to ask for: `.ufo/waves/round-23/w1/ScoutPrune.md`.""")

add("ScoutCommunity", "scout", f"""Read the two staged community sources of the second C3 entry, read-only:
`/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/count-objects-garbage-semantics-r24.md`
cites https://qiita.com/koseki/items/f1af58f1ec1693f0536a (JA) and
https://bbs.csdn.net/weixin_33940469/article/details/100327798 (ZH).
Fetch both live (2026-10-25). Deliver, per page: does it exist / (un)reachable, does it state the
`gc.auto` 6700 threshold or a `garbage` gloss, the verbatim located quote (<=25 words, no pipe
characters) if present, and your tier call (`community` B by the lane's tiers) — plus whether a
copy of EACH page can be committed as a `census/round-23/sources/` snapshot by the L1. If a page
is unreachable, say so exactly (the lane may adopt the entry with only the git-scm rows and record
the community rows as rejected/unreachable). Do not write into shokuknow.
Report path to ask for: `.ufo/waves/round-23/w1/ScoutCommunity.md`.""")

add("ScoutLocalHost", "scout", f"""Establish the host facts the C3 entries need, read-only: `git --version`; whether `man
git-count-objects`, `man git-fsck`, `man git-prune` are installed (and their package/version);
`git count-objects -v` run ONCE against the LANE repo ({LANE}) only — never against the fleet repo,
never anything that writes. Report the field values you observe and whether `garbage` is 0.
State explicitly that `count-objects -v` is read-only and that you ran no `fsck --lost-found`.
Report path to ask for: `.ufo/waves/round-23/w1/ScoutLocalHost.md`.""")

# ---------------- registry / id / inherited state (scouts) ----------------
add("ScoutRegistryCensus", "scout", f"""Measure the C3 registry baseline at the lane base revision. Run exactly:
  cd {LANE} && /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
and capture exit code + full output; then the row count `grep -cE '^ {{0,3}}\\|[[:space:]]*S[0-9]{{3,}}[[:space:]]*\\|' {LANE}/corpus/SOURCES.md`,
the max id, the tier histogram (3rd `|`-cell bucket A/B/C), the status histogram (mined/queued/
rejected), and the malformed-row count (rows whose cell count != 11). Give each as a copy-pasteable
command with its output. This is the C3 "before" receipt; the L1 will re-run it at round end.
Report path to ask for: `.ufo/waves/round-23/w1/ScoutRegistryCensus.md`.""")

add("ScoutIdCollision", "scout", f"""Run the frozen id-collision step (preregistration, C3) in scratch and prove the guard:
  S=/home/vgpnk/Projects/shokuknow
  A=/var/tmp/souji-r23-ScoutIdCollision; mkdir -p "$A"
  grep -oE '^ {{0,3}}\\|[[:space:]]*S[0-9]{{3,}}' {LANE}/corpus/SOURCES.md | grep -oE 'S[0-9]+' | sort > "$A/reg-ids"
  grep -oE '^ {{0,3}}\\|[[:space:]]*S[0-9]{{3,}}' "$S/merge/souji/SOURCES.append.md" | grep -oE 'S[0-9]+' | sort > "$A/staged-ids"
  comm -12 "$A/reg-ids" "$A/staged-ids" > "$A/collisions"
Report: both id counts, the full `collisions` list, and for EACH colliding id the lane row's title/URL
vs the staged row's title/URL (so the re-pointing can be done BY DOCUMENT, never by arithmetic).
Then prove the 0-3-space extractor catches an indented collision: build a scratch registry fixture
with `  | S115 |` indented and show a column-zero-only pattern misses it while the frozen pattern
catches it. Confirm the staged rows for git-count-objects / git-fsck / git-prune are S112/S113/S114
and name the URL of each. Paste every command and output.
Report path to ask for: `.ufo/waves/round-23/w1/ScoutIdCollision.md`.""")

add("ScoutInherited", "scout", f"""Classify the lane's inherited uncommitted round-22 leftovers (the spot-check's D1) file by file:
  cd {LANE} && git status --porcelain
lists 5 modified `.ufo/waves/round-22/attempt2/w1/*.md` files, 2 untracked
`.ufo/waves/round-22/attempt2/w1/evidence/impl-a/head-c9f1fe3.*` files, and the untracked
`census/operator-sweep-20261019/` (operator-owned: never staged, never read).
For each of the 7: is the working-tree content a genuine in-round seat update of that report (diff
hunks are content, not whitespace-only), and does the untracked evidence file's digest match the
digest the modified report claims for it (`sha256sum`)? Recommend commit-or-revert per file with a
one-line reason. Do NOT stage, commit or revert anything yourself.
Report path to ask for: `.ufo/waves/round-23/w1/ScoutInherited.md`.""")

add("ScoutMisroot", "scout", f"""Run the misroot sweep before any report is written:
  git -C {FLEET} status --porcelain
(no pathspec). For every untracked entry, decide whether it names souji round 23 (grep its content
for `souji`/`round-23`), whether it belongs to another lane, and whether it is orchestrator-owned
run state. `{FLEET}/.scratch/` is orchestrator-owned by design and is NEVER a misroot and never
touched. Deliver a table: path, owner (self/other-lane/orchestrator/operator), action (copy into
lane byte-exact + delete fleet copy / leave alone), and the exact `cmp` command the L1 would use.
Do not delete, move or copy anything yourself; do not read `.scratch/` contents.
Report path to ask for: `.ufo/waves/round-23/w1/ScoutMisroot.md`.""")

# ---------------- record reconstruction (revenger) ----------------
add("RevRecords", "revenger", f"""Reconstruct, from committed bytes only, exactly what the four lane records claim today about
round 22's C1 and C2 numbers. For each of `{LANE}/SCORECARD.md`, `{LANE}/LOG.md` (the
"Round22 attempt2" section), `{LANE}/corpus/README.md` (the r22 sections) and
`{LANE}/corpus/lessons/round-22.md`: quote each occurrence of an `assertions=/resolved=/skipped=/
mismatches=` 4-tuple and each `<n> accepted|present|unverifiable|refused` tally with its line
number, and each revision/digest token attached to it. Then state, per occurrence, which receipt
file (if any) commits to that value at that revision: `census/round-22/attempt2/*.tsv`,
`instrument-digests.txt`, `residual/evidence/*.txt`, or none. This is the C1 before-state; the L1's
instrument must reproduce your table. Read-only `git show`/`grep` only.
Report path to ask for: `.ufo/waves/round-23/w1/RevRecords.md`.""")

add("RevGateHistory", "revenger", f"""Reconstruct the r22 gate-check (C2) history so D3 can be closed honestly. From committed bytes:
(a) every digest recorded for `tools/souji-gate-check.py` anywhere in the lane (`grep -rn` over
census/, LOG.md, corpus/, .ufo/waves/round-22/) with the revision it claims; (b) the actual
`sha256sum` of the tool at the lane base and at the current branch tip, and `git log --oneline --
tools/souji-gate-check.py`; (c) whether `tool@<rev> x decl@<rev> -> assertions=63 resolved=61
skipped=39 mismatches=2 rc=1` (the residual seat's C1 line) and the report's `5b8025a8` digest can
both be true at the same revision. Conclusion format: per digest, `bound|unbound|stale` + the
revision it is actually true at. Read-only.
Report path to ask for: `.ufo/waves/round-23/w1/RevGateHistory.md`.""")

# ---------------- C3 entry + row drafts (scribes) ----------------
add("ScribeEntryRepoSize", "scribe", f"""Draft the C3 entry at `corpus/knowledge/repo-size-census-readonly.md` (deliver the draft at
`.ufo/waves/round-23/w1/ScribeEntryRepoSize.md`, the L1 applies it).
Input: the staged entry `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/
repo-size-census-readonly.md` (READ-ONLY: never write into shokuknow) and the three scout reports
next to yours (ScoutCountObjects/ScoutFsck/ScoutPrune) once they exist — if they do not exist yet,
open the three git-scm pages yourself and use YOUR quotes.
Requirements: provenance trio first (`source:`, `verified-at: 2026-10-25`, `recheck:`), `ground: F2`,
a `## Gate` block with `opened: 2026-10-25`, >=1 `ADMIT:` line with a reason and >=1 `REJECT:` line
with a flip condition, located quotes of <=25 words that contain no `|` character, lane-relative
source ids ONLY as `S115`/`S116`/`S117` (git-count-objects / git-fsck / git-prune — the lane's
registry renumber; the staged S112-S114 are already taken by other rows), and a `## What this does
NOT establish` section that keeps the staged entry's honesty. Cite the lane's own
`tools/souji-repo-structure.sh` and `census/round-13/verification.json` where the staged entry links
the lane's F2 capability. Keep it under 90 lines.
Report path to ask for: `.ufo/waves/round-23/w1/ScribeEntryRepoSize.md`.""")

add("ScribeEntryGarbage", "scribe", f"""Draft a second C3 entry: `corpus/knowledge/count-objects-garbage-readings-r25.md`, the
target-language/community half of the `garbage` question (deliver at
`.ufo/waves/round-23/w1/ScribeEntryGarbage.md`).
Input: staged `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/
count-objects-garbage-semantics-r24.md` (READ-ONLY) plus ScoutCommunity's live verdicts on the two
community pages. Rules: this lane holds no measured fleet garbage census of its own, so the entry
must NOT claim one — say the fleet figure is unmeasured here and that the staged S134 own-work row
is not adoptable (the evidence lives outside this repo). Keep only claims the opened sources
support; tier the community rows `B`; ids only `S118`/`S119` for the two community pages if
ScoutCommunity confirms reachability, otherwise refuse the row and record the refusal reason + flip
in the Gate. Provenance trio, `ground: F2`, `## Gate` with `opened: 2026-10-25`, >=1 ADMIT and >=1
REJECT with a flip. <=70 lines. Never write into shokuknow.
Report path to ask for: `.ufo/waves/round-23/w1/ScribeEntryGarbage.md`.""")

add("ScribeSourcesRows", "scribe", f"""Draft the SOURCES.md append block for C3 (deliver at `.ufo/waves/round-23/w1/ScribeSourcesRows.md`).
The lane registry has exactly 11 columns per row; read the header and 3 existing rows of
`{LANE}/corpus/SOURCES.md` and copy the EXACT column order and cell style. Rows to draft:
`S115` git-count-objects(1), `S116` git-fsck(1), `S117` git-prune(1), and (only if ScoutCommunity
confirms reachability) `S118` the JA page and `S119` the ZH page, tier B.
Hard rules: every cell must contain NO literal and NO escaped `|`; `recheck` is a valid ISO date,
`NNd` cadence, or symbolic (`on-release`); `status` is `mined` for an admitted entry's source;
`used-by` names exactly the admitted entries citing the row (repo-relative knowledge paths);
`opened` is this lane's date 2026-10-25; the `teaches` cell is <=25 words. Also paste the
`source:` ids the two drafted entries cite so the L1 can prove every row is cited by an admitted
entry (an uncited row is not appended). Do not edit corpus/SOURCES.md yourself.
Report path to ask for: `.ufo/waves/round-23/w1/ScribeSourcesRows.md`.""")

# ---------------- C1 record repairs (scribes) ----------------
add("ScribeScorecard", "scribe", f"""Draft the SCORECARD.md repair for round 23 (deliver at
`.ufo/waves/round-23/w1/ScribeScorecard.md`; the L1 applies it).
Read `{LANE}/SCORECARD.md` fully and `{LANE}/corpus/lessons/round-22-verifier-spotcheck.md` §2-§7.
Produce, verbatim-ready: (1) the three axis rows' new text as one-line cells (calibration row must
carry the C1 mechanism, its counts line, the receipt path the lane will commit, and the counting
command; operability row carries C2's counter and refusal; coverage row carries C3's row deltas);
(2) a new capability row for C2 (`blob-bound receipts`); (3) a `## Planned` line for r24;
(4) the r22 paragraph corrected to name exactly one measured revision once a receipt binds it —
write it with a PLACEHOLDER `<R23-C1-REV>` and `<R23-C1-COUNTS>` that the L1 fills from the real
receipt, and say why a placeholder is the honest form at draft time.
Keep every number tied to a command; no number without its command. Do not edit SCORECARD.md.
Report path to ask for: `.ufo/waves/round-23/w1/ScribeScorecard.md`.""")

add("ScribeLog", "scribe", f"""Draft two append-only LOG.md blocks (deliver at `.ufo/waves/round-23/w1/ScribeLog.md`).
(1) A **correction entry** for the round-22 attempt-2 block per Q41: it must NOT rewrite the filed
entry; it names the superseded tuple (`assertions=56 resolved=53`), the correct tuple the committed
receipt `census/round-22/attempt2/declared-evidence-before.tsv` holds, the reason, and the words
`superseded by`. It must also carry the slice-tally correction (README said 1 present / 1 refused;
`census/round-22/attempt2/slice-verdicts.tsv` holds 2 present / 0 refused) and the D3 digest
correction (report cited 5b8025a8…; the tool blob at the measured revision differs — use
`<R23-GATE-DIGEST>` placeholder). (2) The `Round23` entry for this round: claims, counters with
before→after placeholders `<C1-BEFORE>/<C1-AFTER>`, `<C2-BEFORE>/<C2-AFTER>`, the wave shape, the
routed-defect dispositions D1-D8, and the bounds. Mark every placeholder so the L1 replaces it
before commit, and list them at the end of your report.
Report path to ask for: `.ufo/waves/round-23/w1/ScribeLog.md`.""")

add("ScribeReadme", "scribe", f"""Draft the `corpus/README.md` corrections for round 23 (deliver at
`.ufo/waves/round-23/w1/ScribeReadme.md`). Read `{LANE}/corpus/README.md` (446 lines) and
`census/round-22/attempt2/slice-verdicts.tsv`.
Required content: (a) a `### Round 23 corrections` block that sweeps EVERY mention of the r22
slice tally and fixes it to the receipt's tally (the spot-check's D4 says README says "1 present …
1 refused" while the receipt holds 2 present / 0 refused — find every mention, not only the quoted
one, and list them with line numbers); (b) the F2 row update for C3 (status, entries, evidence
pointers) plus the F2 frontier "next" line rewritten to what remains owed after the new entry;
(c) a `## Round 23 — ...` section in the same shape as the existing round sections, with
placeholders `<R23-C1-COUNTS>`, `<R23-C2-RECEIPTS>`, `<R23-REGISTRY>`; (d) a closing list of every
placeholder. Do not edit corpus/README.md.
Report path to ask for: `.ufo/waves/round-23/w1/ScribeReadme.md`.""")

add("ScribeQuality", "scribe", f"""Draft the `corpus/QUALITY.md` additions (deliver at
`.ufo/waves/round-23/w1/ScribeQuality.md`). Read QUALITY.md's rules-of-this-file paragraph and the
last three criteria tables, plus `corpus/lessons/round-22.md` `## Mistakes` rows R22-M4/M8/M9/M12
and `{LANE}/corpus/lessons/round-22-verifier-spotcheck.md` §6.
Draft exactly two criteria in the established 5-column shape:
- **Q54** (closes the spot-check's D7: R22-M17/M22 recorded `captured-by: none` and no QUALITY
  criterion was written): a round that ends with uncommitted lane-authored round work, or whose
  report claims "none uncommitted", must be caught by a named criterion — write the criterion, its
  applies-to, its runnable check (must be one command), and its lesson pointer.
- **Q55**: a receipt that names a measurement must bind the revision AND the digest of the bytes
  that produced it; a record quoting a count without a binding receipt is a record defect, not a
  measurement (this is the criterion the C1/C2 work needs).
Each criterion must cite the lesson that produced it; no criterion may be a restatement of a
counter's implementation. Do not edit QUALITY.md.
Report path to ask for: `.ufo/waves/round-23/w1/ScribeQuality.md`.""")

add("ScribeLesson", "scribe", f"""Draft `corpus/lessons/round-23.md` (deliver at `.ufo/waves/round-23/w1/ScribeLesson.md`).
Shape it on `corpus/lessons/round-22.md`: `## Claim and boundary`, `## Mistakes` (table: id, class,
evidence, captured-by, fix/failure witness), `## Gate` (`### Opened sources` with URL, access date
2026-10-25 and a <=25-word located quote with no `|`; `### Assimilation decisions` with >=1 ADMIT
and >=1 REJECT with a flip; `### Independent expectations and rejected scope`), `## Seat-reported
failures` (append-only list, initially empty with a note), and `## Trend verdicts`.
Mistakes to mine (from the routed spot-check, one row each, with the criterion that should have
caught it and the fix that lands this round): D1 uncommitted round work claimed as none; D2 an
after-state named at a revision no receipt binds; D3 a counter run whose tool blob changed before
the cited digest; D4 a record swept in one place and left wrong in another; D5 superseded numbers
kept without an append-only correction; D6 an overbroad reject reason; D7 a `captured-by: none`
class producing no criterion. Use placeholders `<C1-...>`/`<C2-...>` where a measured number is
not yet known and list them. Do not edit corpus/lessons/.
Report path to ask for: `.ufo/waves/round-23/w1/ScribeLesson.md`.""")

add("ScribeReport", "scribe", f"""Draft the fleet report at `{FLEET}/.ufo/reports/round-23/souji.md` — deliver the draft at
`.ufo/waves/round-23/w1/ScribeReport.md` (the L1 writes the real report; never write the fleet path
yourself). Required sections in this order, per the round contract: **Work performed** (opens by
naming C1/C2/C3 and their axes, then one bullet per work item with an evidence pointer),
**Landed changes** (change → LOG entry → commit hash), **Before → after measurements** (one per
claim, counting command + measured commit), **Sources & frontier** (rows before→after + counting
command, rows added by tier, rows touched old→new, frontier rows advanced), **Trend verdicts**
(expansion / quality / discernment, one verdict each with evidence), **SHONEN** (one line per box),
plus **Stale-lane**, **Tool installs**, and the routed-defect dispositions D1-D8.
Use placeholders for every hash and number and list them. Read
`{FLEET}/.ufo/reports/round-22/souji.md` for the house shape. Do not write outside your report.
Report path to ask for: `.ufo/waves/round-23/w1/ScribeReport.md`.""")

# ---------------- instruments (executors) ----------------
add("ExecFixtureAgreement", "executor", f"""Write the fixture for the C1 instrument, delivering a runnable file at
`.ufo/waves/round-23/w1/r23-record-agreement.py` (the L1 copies it to
`{LANE}/tests/fixtures/r23-record-agreement.py`).
It must exercise a tool CLI of exactly this shape (the L1 is writing the tool in parallel):
  python3 tools/souji-record-agreement.py --root <repo> [--rev <full40>] [--json <path>]
Counts line on stdout: `keys=K records=R occurrences=O mismatches=M`; exit 0 iff M==0; each
mismatch row starts with `MISMATCH\\t<key>\\t<record>\\t<class>\\t<detail>`.
Frozen keys (see the preregistration): K1 after-receipt binding, K2 LOG superseded-number
correction, K3 slice tally, K4 uncommitted round work (working-tree `git status` minus committed
`uncommitted:` exemptions in `corpus/pointer-exemptions.tsv`).
Build a synthetic git repo under `/var/tmp` (Q4: hard-code `/var/tmp`, never `/tmp`, trap-clean it)
by `git init` + writing fixture files + `git add`/`git commit` INSIDE that scratch repo only, then
run the tool against it. Cases: (1) repaired repo → exit 0, mismatches=0; (2) receipt file absent
→ >=1 K1 mismatch; (3) SCORECARD counts disagree with the receipt → K1 value-disagree; (4) the
revision token on that line differs from the receipt's `rev=` → K1 rev-disagree; (5) an uncorrected
superseded 4-tuple in LOG → K2; (6) deleting the filed LOG occurrence → K2 filed-bytes-missing;
(7) a wrong `<n> present` tally in README → K3; (8) an unexempted dirty path → K4; (9) an
exempted operator path → NOT a mismatch. Print `case=<n> expect=<...> got=<...>` per case and a
final `selftest=<pass>/<total>`; exit 0 iff every case observes its expectation. Cases 2-8 are the
always-zero control: a tool that always prints mismatches=0 fails them, so print
`control=FALSE-GREEN-REJECTED` when at least one instrumented case would fail a zero-only emitter.
Deliver only that file plus your report; run your fixture at least once and paste the output.
Report path to ask for: `.ufo/waves/round-23/w1/ExecFixtureAgreement.md`.""")

add("ExecFixtureReceiptRun", "executor", f"""Write the fixture for the C2 runner, delivering a runnable file at
`.ufo/waves/round-23/w1/r23-receipt-run.py` (the L1 copies it to
`{LANE}/tests/fixtures/r23-receipt-run.py`). Runner CLI (the L1 is writing it in parallel):
  python3 tools/souji-receipt-run.py run --root <repo> --rev <full40> --tool <repo-rel-path> --out <abs-path> -- <cmd...>
  python3 tools/souji-receipt-run.py verify --root <repo> <receipt>
Receipt v1 header lines, in this order: `receipt=v1`, `rev=<40hex>`, `tool=<path>`,
`tool_sha256=<64hex>`, `cmd=<shell-quoted argv>`, `rc=<int>`, `utc=<ISO8601>`, then
`--- stdout ---` and `--- stderr ---` fences.
Fixture cases (synthetic git repo under `/var/tmp`, trap-cleaned, all git writes inside that repo):
(1) run a tiny counter script at the repo's only commit → receipt written, header order exact,
`rc=0`, stdout present; (2) `verify` on it → exit 0; (3) mutate the tool file in a NEW commit and
verify the OLD receipt → nonzero with `RECEIPT-TOOL-DIGEST-MISMATCH`; (4) a receipt whose `rev=` is
a branch name or a 7-char id → `verify` refuses with an explicit code (no output file); (5) a
receipt whose tool path does not exist at `rev` → refusal code; (6) run with `--out` under `/tmp`
→ refusal (Q4); (7) the runner must not modify the target repo: `git status --porcelain` in the
scratch repo before/after `run` is empty both times; (8) two `run`s of the same rev produce
identical `tool_sha256` and `cmd` but different `utc` (so `utc` is not part of equality).
Print `case=<n> expect=<...> got=<...>` and `selftest=<pass>/<total>`; exit 0 iff all pass.
Run it once and paste the output. Deliver only that file plus your report.
Report path to ask for: `.ufo/waves/round-23/w1/ExecFixtureReceiptRun.md`.""")

add("ExecGateReproduce", "executor", f"""Independently reproduce the r22 gate-check (C2) before/after in scratch, without touching the lane.
Read `{LANE}/tools/souji-gate-check.py --help` and its docstring. Build two read-only mirrors under
`/var/tmp/souji-r23-ExecGateReproduce/`: (a) the lane tree at the base revision via
`git -C {LANE} archive 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd | tar -x -C <mirror-base>`, (b) at
the current branch tip (`git rev-parse master`) via a second `git archive`. Run the tool from each
mirror against ITS OWN corpus and report: counts line, exit code, and the `sha256sum` of
`tools/souji-gate-check.py` in each mirror. Then answer precisely: does the base mirror reproduce
the recorded `fail=10` before-state, and does the tip mirror reproduce `fail=0`? Name any
difference from the spot-check's D3 finding. Never write in the lane; never run the tool against
the live lane tree; clean up your scratch.
Report path to ask for: `.ufo/waves/round-23/w1/ExecGateReproduce.md`.""")

# ---------------- attacks: routed defects (reviewers) ----------------
for _id, _what in [
    ("D1", "uncommitted round-22 work (5 modified seat reports + 2 untracked evidence files) while the r22 report claims none uncommitted"),
    ("D2", "no committed receipt binds the r22 C1 after-state at the revision SCORECARD names (`9301d98`), and the report names a different tip (`77d6595`)"),
    ("D3", "the after-run was measured with tool blob f26aa728 while the report cited `5b8025a8…`, and no `before` (`fail=10`) receipt exists"),
    ("D4", "README says `1 present … 1 refused` where the receipt and lesson say 2 present / 0 refused"),
    ("D5", "the LOG round-22 entry keeps superseded numbers (`assertions=56 resolved=53`, slice `1 present, 1 refused`) with no append-only correction"),
    ("D6", "the lesson Gate's reject reason for `quarantine-staging-no-copy-r24` is overbroad"),
    ("D7", "M17/M22 record `captured-by: none` and no QUALITY.md criterion was written base→tip"),
    ("D8", "the derived slice row for S118 carries a stray backtick"),
]:
    add(f"Rev{_id}", "reviewer", f"""Verify routed defect **{_id}** independently against committed bytes, then judge whether this round's
planned repair actually closes it. The spot-check's claim: {_what}.
Steps: (1) reproduce the defect with one command (paste it and its output); (2) state whether the
defect is real as stated, overstated, or already closed at the lane base; (3) name the exact
minimal repair that closes it (file + cell/line + wording constraint) and the command that would
prove closure; (4) if the repair is not achievable without editing filed evidence or operator
files, say so and give the append-only alternative.
`corpus/lessons/round-22-verifier-spotcheck.md` §6 is the source of the claim; §2-§5 is its evidence.
Report path to ask for: `.ufo/waves/round-23/w1/Rev{_id}.md`.""")

add("RevSHONEN", "reviewer", f"""Audit `{LANE}/SHONEN.md` against the repo at the lane base: for each of the four boxes, does its
named evidence pointer resolve at the named revision, and does it support the box's wording? Use
`git cat-file -e <rev>:<path>` / `git show` and the counting commands the pointers name. Deliver a
per-box verdict (`supported`, `pointer-dangles`, `wording-overclaims`) with the command and output,
plus the single cheapest change that would earn an `[x]` from a non-author verifier (do not claim
`[x]` yourself — promotion is operator-owned).
Report path to ask for: `.ufo/waves/round-23/w1/RevSHONEN.md`.""")

# ---------------- attacks: critics ----------------
add("CritC1Gameable", "critic", f"""Falsify the C1 claim before it is measured. Target: `tools/souji-record-agreement.py` with keys
K1-K4 as frozen in `{LANE}/.ufo/waves/round-23/preregistration.txt`.
Attack list (at least six, each with a concrete cheap move an author could make to reach
`mismatches=0` without repairing anything): delete the quoted numbers; move a number to another
file; relax K3 by removing the class-occurrence requirement; declare a giant `uncommitted:`
exemption list in `corpus/pointer-exemptions.tsv`; point K1 at a receipt the author writes by hand;
make the revision-token check vacuous. For each: does the frozen predicate catch it, and if not,
what one-line predicate change closes it WITHOUT changing the target? Then give a verdict: is
`M_after=0` at the tip reachable by a do-nothing control? Justify with the base-state facts.
Do not edit the tool or the preregistration; your output is the attack record.
Report path to ask for: `.ufo/waves/round-23/w1/CritC1Gameable.md`.""")

add("CritC2Value", "critic", f"""Falsify the C2 (blob-bound receipts) claim. Questions to answer with evidence: (1) does the lane
already have a receipt mechanism that binds a revision (`tools/souji-rev-pin.py`, Q37/Q40,
`census/round-22/attempt2/instrument-digests.txt`)? If yes, is a new runner a duplication — or does
it close a real gap (the digest was recorded out-of-band and never re-checked)? (2) Is the counter
`grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ | wc -l` a real capability measure or a grep for a
string the author types? Name what a fake-green author would have to do and whether `verify` stops
it. (3) Does the runner violate any quality rule (Q4 /var/tmp, Q37 durable refs, Q40 input
binding, Q41 do-not-rewrite-filed-evidence)? Give a verdict: `capability`, `ceremony`, or
`capability-with-named-limit`, and the strongest single argument against the claim.
Report path to ask for: `.ufo/waves/round-23/w1/CritC2Value.md`.""")

add("CritC3Ground", "critic", f"""Falsify the C3 coverage claim. The claim: F2 (repository size census) moves from "frontier, no
entry" to "frontier, entries admitted" via two assimilated entries, so the credit is on ground the
lane did not hold.
Check against `{LANE}/corpus/README.md` (coverage map + every F2 mention),
`{LANE}/corpus/knowledge/git-repo-structure-readonly.md`,
`{LANE}/corpus/knowledge/`'s other entries, and `{LANE}/corpus/SOURCES.md`'s F2-related rows (S035,
S036, S037 and any count-objects/fsck/prune rows). Verdicts needed: (1) does the lane already hold
this ground in another entry (name file:line)? (2) does the staged entry add a consequence the lane
can act on, or only restate held material? (3) is `garbage`-semantics ground held by
`knowledge/process-residue-observations.md` or `git-repo-structure-readonly.md`? (4) does the
assimilation draw credit from a `frontier` row without moving it to core (is that allowed by
AXES.md's coverage definition — quote it)? Give `credit-honest` or `credit-overclaimed` + reason.
Report path to ask for: `.ufo/waves/round-23/w1/CritC3Ground.md`.""")

# ---------------- sibling overlap + scope ----------------
add("ConnectorSiblingSources", "connector", f"""Sibling-overlap scan for C3's source rows. For each URL the round is about
(git-scm.com/docs/git-count-objects, git-fsck, git-prune, the qiita JA item, the csdn ZH article):
search the OTHER lane repos under `{FLEET}` (`for d in {FLEET}/*-shokunin; do grep -l <host/path>
"$d/corpus/SOURCES.md"; done` — read-only) and the fleet-level corpora if any, and report which
lane already holds a row for that URL, with its id and its scope cell. Then: does souji's row
duplicate ANOTHER LANE's ground (cross-lane duplication is a discernment issue, not a census
error), and is there a lane whose own frontier clearly owns the ground better? Also check the
in-lane duplicate-URL warnings the census reports (`sources-census.sh validate` output) and name
whether the three git-scm pages already appear in souji's registry under another id — if they do,
the new rows must supersede or be refused (CORPUS rule 2), never silently duplicated.
Report path to ask for: `.ufo/waves/round-23/w1/ConnSiblingSources.md`.""")

add("SentinelScope", "sentinel", f"""Security and scope review of the round's surfaces. Check and report:
(1) does any planned artifact read, print or store a credential-shaped string (the round touches
git object databases, man pages, community web pages) — inspect `tools/souji-receipt-run.py`'s and
`tools/souji-record-agreement.py`'s stdout surfaces once they exist in
`{LANE}/.ufo/waves/round-23/w1/` or in `{LANE}/tools/`, and name any unbounded echo of command
output into a committed receipt (a receipt captures stdout verbatim — what could leak?);
(2) does the receipt runner keep the lane read-only (no writes, no fetch, no prune, no
`fsck --lost-found`)? name the exact guard the implementation needs; (3) does anything in the round
plan touch `{FLEET}/.scratch/`, `.ufo/state/`, sibling lanes, or the shokuknow repo (read-only)?;
(4) is the C3 entry's claim about `git fsck --lost-found` accurate that it WRITES — confirm from the
opened page and flag if the round's own commands could ever reach it. Verdict per item: `clean`,
`needs-guard`, `finding`.
Report path to ask for: `.ufo/waves/round-23/w1/SentinelScope.md`.""")

# ---------------- mutation testers ----------------
add("MutCounter", "mutation-tester", f"""Design (do not run against the lane) the mutant list for the C1 instrument. Read
`{LANE}/corpus/lessons/round-22-verifier-spotcheck.md` §6 and the preregistration's K1-K4.
Enumerate EVERY predicate clause the instrument must implement (receipt exists at rev; counts-line
equality; rev token equality; filed-occurrence retention; correction-line coverage; per-class tally
equality; per-class occurrence presence; uncommitted path accounting; exemption parsing; exit-code
mapping) as one mutant each: a one-line change that deletes or weakens that clause. For each mutant
state the fixture case (from the C1 fixture's 9 cases) that must kill it, and the mutant's
predicted observable. Any mutant with no killing case is a coverage gap — say so plainly. Deliver
`mutant=<id>|clause=<...>|killed-by-case=<n>|predicted=<...>` rows plus `uncovered=<count>`.
Report path to ask for: `.ufo/waves/round-23/w1/MutCounter.md`.""")

add("MutReceipt", "mutation-tester", f"""Same method for the C2 runner. Enumerate the clauses: rev must be full 40-hex; rev must be
reachable from a durable ref (not `refs/jj/*`); archive extraction; tool digest computed from the
tree at rev (not the working tree); `--out` must not be under `/tmp`; the runner must not write the
target repo; `verify` recomputes the digest at the receipt's rev; `verify` refuses a missing tool at
rev; `verify` refuses a malformed rev; receipt header order; `rc` is the command's real exit code;
stdout/stderr are captured verbatim. One mutant per clause with the fixture case (from the C2
fixture's 8 cases) that must kill it, plus `uncovered=<count>`. Call out specifically whether the
"tool digest from tree at rev" clause is killed by case 3 — the case where the tool changed in a
later commit — and why that case, not `verify`'s own re-hash, is the discriminating one.
Report path to ask for: `.ufo/waves/round-23/w1/MutReceipt.md`.""")

add("SimplTouched", "simplifier", f"""YAGNI pass over what this round touches. Read the round plan (preregistration) and the lane's
existing instruments (`tools/souji-declared-evidence.py`, `tools/souji-gate-check.py`,
`tools/souji-rev-pin.py`, `tools/souji-landing-gate.py`). Answer:
(1) which of the two NEW instruments duplicates an existing one (if any) and what should be deleted
or merged instead of added? (2) which existing helper could host the new checks with fewer lines?
(3) which dead weight in the touched files (SCORECARD prose, README round sections, LOG entries)
should be DELETED rather than corrected — naming it exactly, with the reason it is dead and the
line that supersedes it? Never propose deleting filed evidence or operator files: say so where the
temptation exists. Deliver `keep/merge/delete` per item with a line count estimate.
Report path to ask for: `.ufo/waves/round-23/w1/SimplTouched.md`.""")

add("CritPrereg", "critic", f"""Falsify the preregistration itself (`{LANE}/.ufo/waves/round-23/preregistration.txt`)
against the round contract and §9 claim-sizing rules. Check: are the three claims causally
separable (does C1 verify if C2 never lands, and vice versa)? Is each after-state ONE concrete value
re-derivable by ONE command over committed bytes? Does any target use a universal clause without an
enumerating command? Is the lowest-axis obligation met (calibration 7 vs operability 8, coverage 8)
per `{FLEET}/AXES.md`? Does each claim name an axis by the surface it changes rather than by the
number it produces? Is there a do-nothing control for each? Is `Assimilation` a claim slot abuse
(§10 says it adds no claim slot)? Flag anything that would make the round non-admissible and give
the minimal amendment — but note that predicates may not be changed after data, so label each
amendment `pre-data-legal` or `would-invalidate`.
Report path to ask for: `.ufo/waves/round-23/w1/CritPrereg.md`.""")

SPEC = {
    "wave": "souji-r23-w1",
    "reportDir": ".ufo/waves/round-23/w1",
    "maxLanes": 64,
    "context": CONTEXT,
    "items": ITEMS,
}

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "w1-spec.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(SPEC, fh, indent=1, ensure_ascii=False)
    print(f"wrote {out}: items={len(ITEMS)}")
    from collections import Counter
    print(Counter(i["role"] for i in ITEMS))
