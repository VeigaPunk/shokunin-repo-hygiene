# ScoutReportShape — round-27 report skeleton checklist for the L1

## Status

STATUS: PASS — the report contract, marker rule, SHONEN-heading form, Stale-lane line, installs line and both pre-report gates were re-derived from the round-27 prompt, the canonical PROTOCOL and the live watchdog script; four routed defects owed this round were extracted and their current state measured (2 of them still open in the lane worktree at base `e78ac7c`).

Read-only seat: no lane file was edited, no commit, no scratch left behind.

## Evidence

- Lane base / remote (both `e78ac7c`, ahead=0): `git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-remote origin refs/heads/master` → `e78ac7c4837b81b634db4a927605a751a7f006ba	refs/heads/master`; `git -C ... rev-parse refs/heads/master` → same. Revision: `e78ac7c4837b81b634db4a927605a751a7f006ba` (branch `master`).
- Contract source read this run: `/home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-27.md` (fleet, round-27 dispatch) and `/home/vgpnk/Projects/kimi-shokunin/skills/shokunin/protocol/PROTOCOL.md`; watchdog `/home/vgpnk/Projects/shokunin/scripts/shokunin-watchdog.sh`.
- Round-26 house shape, re-measured: `grep -n '^## \|^Stale-lane' /home/vgpnk/Projects/shokunin/.ufo/reports/round-26/souji.md` → `3:## Work performed`, `14:## Landed changes`, `36:## Before → after measurements`, `46:## Sources & frontier`, `50:## Trend verdicts`, `58:## SHONEN`, `65:Stale-lane: …`.
- Marker regex verified against the r26 report byte file: `LC_ALL=C grep -qE "^#+[[:space:]]*[Ss][Hh]([Oo]|Ō|ō)[Nn][Ee][Nn]([^[:alnum:]_]|$)|^[[:space:]]*-[[:space:]]+\*\*[Ss][Hh][Oo][Nn][Ee][Nn]\*\*([[:space:]]|$)"` → exit 0 (SHONEN marker OK); `LC_ALL=C grep -qiE '^#{1,6}[[:space:]]+Sources[[:space:]]*&[[:space:]]*frontier([[:space:]]|$)'` → exit 0 (S&F heading OK); `wc -c` → `8656` (floor 400).
- `grep -c '^## SHONEN' /home/vgpnk/Projects/shokunin/.ufo/reports/round-26/souji.md` → `1`; box lines inside the section: `awk '/^## SHONEN/{f=1;next} /^## /{f=0} f' … | grep -cE '^\[~\]'` → `4`; `grep -cE '^- \[.\]' /home/vgpnk/Projects/shokunin/souji-shokunin/SHONEN.md` → `4` (source checklist has 4 boxes).
- Routed-defect state at base `e78ac7c`: `git -C … status --porcelain .ufo/waves/round-26/w1/` → 36 paths (11 ` M`, 25 `??`); `git status --porcelain` also shows `?? census/operator-sweep-20261019/`, `?? tests/fixtures/__pycache__/`, `?? tools/__pycache__/`; `ls .gitignore` → not found; `git ls-files | grep -c __pycache__` → `1` (`census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc`).
- Registry baseline for the Sources & frontier table: `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md` → `132` (C2 target 135).
- Census baseline: `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → rc `0`, 35 lines, last line `souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md`.
- F4 grounded baseline: `grep -rlE '^ground: F4' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/knowledge/ | wc -l` → `2` (`quarantine-staging-no-copy-r23.md`, `quarantine-origin-record-fields-r24.md`).
- Id-collision guard re-run verbatim from the prompt §10 command, scratch under `/var/tmp/souji-r27-ScoutReportShape/assim`: `comm -12 reg-ids staged-ids` → 24 ids `S109 … S132`; the three rows C2 admits (`S152`, `S210`, `S211`) are **not** in that set (`grep -cE '^(S152|S210|S211)$' collisions` → `0`).

## Findings

### 1. Required report sections, in order (hard contract)

Source: `/home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-27.md:99-120` (report path at `:101`, section bullets at `:104`, `:107`, `:109`, `:111`, `:116`, `:118`); mirrored by `PROTOCOL.md:150-171` (minimum content list). Report path is `/home/vgpnk/Projects/shokunin/.ufo/reports/round-27/souji.md` (fleet repo, not the lane).

| # | heading (verbatim) | must contain | source |
|---|---|---|---|
| 1 | `## Work performed` | opens by naming the round's declared claims (1–3) and their target axes/capability; then one bullet per work item, each with an evidence pointer (path:line, command output, or commit hash) | prompt `:104-106`; PROTOCOL `:155` |
| 2 | `## Landed changes` | every change tied to a `LOG.md` entry and to the commit hash that carries it | prompt `:107-108`; PROTOCOL `:156` |
| 3 | `## Before → after measurements` | one row per claim, with the counting command and the commit it was measured against | prompt `:109-110` |
| 4 | `## Sources & frontier` | `SOURCES.md` rows before→after + counting command, rows added by tier, rows touched old→new, frontier rows advanced; a no-corpus lane writes a line beginning `SOURCES: unchanged —` (main-repo form: `SOURCES: unchanged — main-repo lanes hold no corpus/`). souji HAS a corpus → this section must be real, not the unchanged marker | prompt `:111-115`; PROTOCOL `:158-161`; watchdog `report_sources_conformance` `shokunin-watchdog.sh:302-317` |
| 5 | `## Trend verdicts` | one verdict each for `expansion`, `quality`, `discernment` (`improved` \| `harmed` \| `unchanged` \| `unprovable-but-better`), with evidence, no scalar | prompt `:116-117`; PROTOCOL `:162-164` |
| 6 | `## SHONEN` | one line per box of the lane's `SHONEN.md` checklist | prompt `:118-120`; PROTOCOL `:165-171` |

Order is normative ("Required sections, in order", prompt `:102`). Also required by PROTOCOL `:157`: cross-domain evidence encountered, with the domain it belongs to — r26 carried it inside the Work-performed bullets and in SHONEN box 4, not as its own heading.

### 2. Marker rule (what makes the round `failed`)

Source: prompt `:121-125`; PROTOCOL `:198-215`; watchdog `report_of()` `shokunin-watchdog.sh:144-164`.

- A contentless report — placeholder text, **missing required sections other than Sources & frontier and Trend verdicts**, or no evidence pointers — counts as the round **failed**; the driver relaunches the same round. So sections 1, 2, 3 and 6 above are marker predicates; sections 4 and 5 are conformance items only ("neither section is a marker predicate").
- A report naming real committed work but skipping those sections is `ok` + one minimum-content conformance defect.
- Mechanical acceptance the watchdog actually runs (`report_of`):
  - the file exists at `$UFO/reports/round-27/souji.md`;
  - it carries a SHONEN marker — `^#+[[:space:]]*SHONEN…` **or** `- **SHONEN**` (`shokunin-watchdog.sh:162`; ASCII case variants plus both macron bytes, so `Shonen`/`SHONEN` both match);
  - `wc -c` ≥ `MIN_REPORT_BYTES` (default **400**, `shokunin-watchdog.sh:54`, `:163`) — r26 filed 8656 bytes;
  - the file digest differs from the same-round baseline digest (`.ufo/state/souji.report-baseline` currently holds round `27` + the empty-string digest `e3b0c442…`), i.e. the report must be new bytes, not unchanged.
- A report filed with no lane work, no evidence pointer and no resolvable commit is a **marker, not a report**: the integrator records the lane-round `failed` (PROTOCOL `:207-212`).

### 3. SHONEN heading requirements (one line per box)

Source: prompt `:118-120` and `:391-392`; PROTOCOL `:165-171`; lane checklist `/home/vgpnk/Projects/shokunin/souji-shokunin/SHONEN.md`.

- Exactly one `## SHONEN` heading, spelled that way, at column 0 (`grep -c '^## SHONEN' <report>` must print **1** — prompt `:391-392`).
- The lane checklist has **4 boxes** (`grep -cE '^- \[.\]' SHONEN.md` → `4`; box order at `SHONEN.md:5`, `:7`, `:9`, `:11`). The report must carry **4 lines**, one per box, in `SHONEN.md` byte order.
- Marker per box: `[x]` **only** with a named non-author verifier; `[~]` with a resolvable evidence pointer; `[ ]` if untouched (prompt `:118-120`). `[~]` means asserted-by-author, not skipped (PROTOCOL `:167`).
- All four boxes are currently `[~]` at source and the lane is author-side, so the filed section should be 4 × `[~]` with a pointer each (r26 filed exactly that: `grep -cE '^\[~\]'` inside the section → `4`, and `:63` names the "No non-author verifier checked this round" fact).
- Do not mix the two paste forms. r25/r26 used `[~]` at column 0; a `- [~]` bullet form is accepted by the watchdog's second regex alternative but then `grep -cE '^\[~\]'` under-counts — pick one form and keep the count check consistent (r26 precedent: `.ufo/waves/round-26/w1/shonen-lines.md`, "Shape (the frozen contract)" table rows A1–A6).
- Absence of the heading is worse than a missing section: it is a conformance defect **and** disqualifies the report as evidence in the promotion review; the assessment must be re-filed next round (PROTOCOL `:168-171`).

### 4. Stale-lane line

Source: prompt `:400-401`; PROTOCOL `:176-190`.

- One line, written literally `Stale-lane: …`. Content rule (PROTOCOL `:179-183`): list any mission open longer than two driver ticks, age from the launch timestamp, and say whether it is **progressing** or **silent**; progressing means observable activity in the lane's write scope since launch — a lane-authored commit or files modified under its repo — and sibling-authored activity alone is the third grade `progressing-weak`. Prompt `:400-401` narrows it to "respawn-per-round driver; no other mission of this lane is open".
- r26 precedent (`/home/vgpnk/Projects/shokunin/.ufo/reports/round-26/souji.md:65`): `Stale-lane: mission progressing (lane commits and round artifacts landed; wave seats still running behind the job cap). Open L0 questions: none. Tool installs/updates: none.` — the L0-questions and tool-installs sentences ride the same closing line in this lane's house style.
- Round 27 attempt 1 is already a fact to state: the watchdog logged `lane-dead-no-report souji round=27` (attempt 1 died with no lane writes); the round-27 prompt `:213-217` requires inherited outputs to be reused-or-discarded and both to be named in the report.

### 5. Installs section

Source: prompt `:400-401` ("and any tool installs") and `:402-405` (tooling authorization); `/home/vgpnk/.omp/agent/RULES.md:14`.

- A line naming the installs of this round — even when empty ("Tool installs/updates: none.", r26 `:65`; kasegi r27 used a `Tooling:` line: `/home/vgpnk/Projects/shokunin/.ufo/reports/round-27/kasegi.md:110`).
- When something was installed: record **tool, version, channel, reason** (RULES.md `:14`); channel order is pacman → `uv tool` → official release binary into `~/.local/bin` → `cargo install`/`npm -g` (RULES.md `:7-9`).
- Binding guard for this round: **all pacman transactions are PAUSED host-wide** — never `pacman -S/-Sy/-Syu/-U/-R`, never a downgrade, never a host-service restart (prompt `:402-405`). This seat installed nothing, so the report's installs line is "none" unless another seat installs.

### 6. Pre-report gates (run before filing the report)

Source: prompt `:387-392`; C3 in `.ufo/waves/round-27/preregistration.txt:7` makes the same four checks the subject of a runnable gate (`tools/souji-pre-report-gate.sh`, drafted this round at `.ufo/waves/round-27/w1/souji-pre-report-gate.sh`).

| gate | command | expected | source |
|---|---|---|---|
| tip on branch | `git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-remote origin refs/heads/master` | must print the **final lane hash** — the same hash `git -C … rev-parse refs/heads/master` prints; an older hash means the commits are off-branch (land them via `jj-lane.sh`, never plain git) | prompt `:388-390` |
| report SHONEN | `grep -c '^## SHONEN' <report>` | `1`, followed by one `[~]`/`[ ]` line per SHONEN.md box | prompt `:391-392` |
| commit path | commit the report only via `fleet-commit.sh --as souji` | the report lands last and cites the pushed lane hash | prompt `:390`, `:333-336` |
| prereg present | `.ufo/waves/round-27/preregistration.txt` exists in the lane | present (the C3 gate checks it) | prereg `:7` |
| clean worktree | `git -C … status --porcelain` | no uncommitted lane-authored leftovers (the C3 gate's `clean` check) | prereg `:7` |

At base the tip gate already passes: `ls-remote origin refs/heads/master` → `e78ac7c…` = local `refs/heads/master`. It must be re-run after the last `jj-lane.sh` landing, because the lane uses jj-colocated VCS and the git HEAD is detached — read the tip as `refs/heads/<branch>`, never `HEAD` (prompt `:365-370`).

### 7. Routed defects owed this round (from the r26 and r25 verifier spot-checks)

| # | defect | source | state at base `e78ac7c` | owed action |
|---|---|---|---|---|
| D1 | trailing wave-seat outputs under `.ufo/waves/round-26/w1/` uncommitted | `corpus/lessons/round-26-verifier-spotcheck.md:60` | **still open**: 36 paths (11 ` M`, 25 `??`) under that directory | commit under a round-27 entry or sweep, and **record the sweep** in the report (PROTOCOL `:194-197`: a respawned mission inherits and must resolve uncommitted lane-authored changes before filing) |
| D2 | S-language edition rows: the r26 reject rationale for S119-style rows is time-fragile | `corpus/lessons/round-26-verifier-spotcheck.md:61` | staged S119/S120/S121 are zh-Hans / Pro Git-ja / Atlassian-ja editions; the r26 verifier re-opened S119 live and found it now carries the 2.56.0 `--auto-maintenance` switch, i.e. the recorded "version alignment unprovable" reason does not reproduce today | if any S-language row is re-adopted this round: pin the snapshot + sha256 and record the fetch date and the located quote at decision time; otherwise keep the reject and restate the time-fragility in the round-27 lesson `## Gate` |
| D3 | `__pycache__/` dirs untracked (`tools/`, `tests/fixtures/`) | `corpus/lessons/round-26-verifier-spotcheck.md:62` | **still open**: `?? tools/__pycache__/`, `?? tests/fixtures/__pycache__/`; no `.gitignore` at the lane root; **one tracked** pyc exists — `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc` (commit `e879ba0`), so a bare pattern does not hide it (seat note `.ufo/waves/round-27/w1/ExecPycacheFix.md`, `.ufo/waves/round-27/w1/gitignore-draft.md`) | add a lane-root `.gitignore` (`__pycache__/`, `*.pyc`) **and** decide the tracked pyc explicitly (`git rm --cached` needs the L1's writer); name the choice in the report |
| D4 | `census/operator-sweep-20261019/` untracked leftover | `corpus/lessons/round-25-verifier-spotcheck.md:73` (and `:26`) | **still open**: `?? census/operator-sweep-20261019/` | commit, quarantine, or remove per lane hygiene — but note it is operator-owned output already named in `corpus/pointer-exemptions.tsv:1` ("operator-owned untracked output, deliberately never committed or opened by the lane"); the L1 must decide and name it, not silently leave it |
| D5 | SHONEN boxes remain `[~]`-only; promotion is operator-owned | `corpus/lessons/round-25-verifier-spotcheck.md:74` | 4 boxes still `[~]` | the L1 must not write `[x]`; keep `[~]` with pointers and leave promotion to the operator |
| D6 | preregistration axis-of-surface check before freeze; red-arm receipts committed before after-data | `corpus/lessons/round-25-verifier-spotcheck.md:71-72` | r26 delivered `tools/souji-axis-check.py` + 12-case fixture and QUALITY Q59 for the first; the before-data receipt discipline is a per-round discipline | keep the r27 prereg amendment-free and commit the control receipts at base revisions before landing after-data |

### 8. Two contract items the r26 house shape did not surface — check them in the r27 report

- **Before → after measurements must carry the frozen base.** The r27 base is `e78ac7c4837b81b634db4a927605a751a7f006ba` (branch `master`, ahead=0, remote verified); the report's measurement rows should name the base revision and the landing tip explicitly, per QUALITY Q58 ("A preregistered numeric target is derived at the named base revision, not copied from a prior round's different base", `corpus/QUALITY.md:142`).
- **The C2 id-collision kill rule needs a committed renumber map.** The C2 kill rule reads "the id-collision proof producing a nonempty `collisions` set without a committed renumber map, fails C2" (prereg `:7`). The verbatim prompt §10 guard produces a **nonempty** 24-id set (`S109 … S132`) because the staged package was built against an older lane registry — even though the three rows C2 admits (`S152`, `S210`, `S211`) are collision-free. The L1 must therefore commit the renumber/disposition map as wave evidence (paste both id lists, the collision count and the map into the report, per prompt §10) or C2 fails on its own kill rule. This is a routing note, not a proposed predicate change.

## Attack log

Not an attack item — no predicate, target, counter or case set is proposed for change. Two items are flagged for the L1 as obligations already written into the frozen contract, not as amendments:

1. **C2 kill rule vs. the collision guard (Finding 8, second bullet).** The frozen kill rule requires a committed renumber map whenever the collision set is nonempty; the guard's set *is* nonempty (24 ids) though the admitted rows are collision-free. Resolution is a committed map, not a rule edit. `[INFERENCE]` — the L1's reading of "nonempty collisions set" as scoped to the whole staged set versus the admitted subset is the only judgment here, and the safer reading (commit the map) satisfies both.
2. **D3's tracked pyc (Finding 7, D3).** A `.gitignore` pattern alone does not satisfy "add to `.gitignore` or never stage" for the already-tracked `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc`; the L1 must take the explicit decision and name it rather than let the pattern imply a state change that did not happen.

Scratch: `/var/tmp/souji-r27-ScoutReportShape/` (census output, collision lists) — removed before this report was filed.
