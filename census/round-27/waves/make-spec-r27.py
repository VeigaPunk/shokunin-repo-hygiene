#!/usr/bin/env python3
from __future__ import annotations
import json, sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
WDIR = ".ufo/waves/round-27/w1"
REPORT_DIR = f"{LANE}/{WDIR}"
R27 = f"{LANE}/.ufo/waves/round-27"
BASE = "e78ac7c4837b81b634db4a927605a751a7f006ba"

CTX = f"""# Goal
Souji round 27 (attempt 2), one v2 wave (build + attack together). Lane: fleet repository & workspace hygiene (掃除). Axes: calibration (7, lowest non-retired), operability (8), coverage (8); no axis may be harmed. Claims FROZEN in {R27}/preregistration.txt (read it FIRST) at lane base {BASE} (branch master, ahead=0, remote verified e78ac7c). C1 calibration: resolve the two internal landing-gate LG-DANGLING-PTR findings via committed corpus/pointer-exemptions.tsv rows (findings 2→0). C2 coverage: assimilate the F4 origin-record theme from /home/vgpnk/Projects/shokuknow/merge/souji/ (admit origin-record-writer-r27.md + origin-record-mechanism-set-r33.md, re-grounded this round; registry rows 132→135, grounded F4 2→4, gate ok=2, sources-census rc 0). C3 operability: tools/souji-pre-report-gate.sh + tests/fixtures/r27-pre-report-gate.sh (selftest 4/4, FALSE-GREEN-REJECTED). The L1 holds the planner seat and is the only integrator.

# HARD BOUND (violating this voids your seat)
souji is a hygiene lane, but its write scope is its own repo only. **Never delete, move, quarantine or classify-for-cleanup anything in {FLEET} outside {LANE}/.** Incident 2026-10-25: the fleet's tracked .scratch/ tree was deleted mid-run by an unidentified seat. Never touch {FLEET}/.scratch/, {FLEET}/.ufo/state/, {FLEET}/.ufo/watchdog.log, MANIFEST.json, the fleet scripts/ or templates/, any sibling lane repo, the lane's jj state or git index, or /home/vgpnk/Projects/shokuknow (read-only source: never write, commit, fetch, push or run a campaign tool there).

# Contract
- Read {R27}/preregistration.txt FIRST. It is the frozen counter contract (C1/C2/C3, counters, kill rules). Never propose changing a predicate, target, counter or case set after data: if you believe a counter is wrong or gameable, report it as an ATTACK. Amendments are stricter-only and logged by the L1.
- You are a READ-ONLY seat for the lane: write ONLY your own report and, if your item names one, the delivery file(s) inside your own report directory ({REPORT_DIR}/). No `git add/commit/push/stash/checkout/reset`, no `jj` mutation, no `rm`/`mv` of anything you did not create, no signals. Read-only `git log/show/diff/status/ls-tree/cat-file/rev-parse` against the lane are fine.
- Scratch goes ONLY under `/var/tmp/souji-r27-<YourName>/` (never /tmp); any git repo you need is created there with `git init` and every later git call names `-C` on it; verify `git -C "$D" rev-parse --show-toplevel` prints `$D` before the first commit. Remove your scratch before you finish.
- Absolute paths only. Your tools start at the FLEET root, not the lane: every lane path must be written as {LANE}/<path>. Every `Report:` trailer path is relative to {LANE} — write it at {LANE}/<that path>. A relative path lands in the wrong repo.
- A source claim needs a location: URL or repo path plus line/section, and a <=25-word verbatim quote copied from bytes you opened this run, containing no literal or escaped `|`.
- Unrun checks have not passed. Never report an execution you did not perform; label inference as `[INFERENCE]`. Run lane Python with `python3 -B` (no __pycache__).
- Tooling is authorized (operator 2026-10-19): you may install or upgrade tools that help the task; read /home/vgpnk/.omp/agent/RULES.md first (official channels only, record tool/version/channel/reason in your report). **pacman guard: all pacman transactions are PAUSED host-wide** — install via `uv tool`/`npx`/an official binary in `~/.local/bin`, or route around it. Never `pacman -S/-Sy/-Syu/-U/-R`, never downgrade, never restart a host service.
- Certification OFF, K5 HELD, F5 reap + NAMESPACE holds unchanged. No credentials, no live /proc census, no `census/operator-sweep-*` contents, no `.scratch/` contents. Never `agent://all` (it reaches every lane's seats) — message your seats by id.

# Output shape
Markdown report at your rendered `Report:` path: `## Status` (one line `STATUS: PASS|PARTIAL|FAIL` + why), `## Evidence` (command, output excerpt, revision), `## Findings` (numbered, each with its location), `## Attack log` where your item is an attack. Terse; no filler."""


items = []
def add(name, role, task): items.append(item(name, role, task))

LANE_L = LANE
REPO = f"{LANE_L}/.ufo/waves/round-27/w1"
def item(name: str, role: str, task: str) -> dict:
    return {"name": name, "role": role, "prompt": task}
def RD(name): return f"{REPO}/{name}.md"

# ---------------- connectors ----------------
add("ConnSiblings","connector",
f"""Cross-axis pattern finder — SIBLING-OVERLAP scan for souji round 27. Read-only reconnaissance over the fleet root {FLEET} and at least the sibling lane repos present there (e.g. tabi-, kasegi-, kengaku-, kaidoku-, tsukuroi-, mado-, kama-, tameshi-, mori-, chousa-, kake-, kumitate-, revenger-, kotoba-, kotodama-shokunin) for any work touching THIS round's surfaces: (a) citations of `corpus/pointer-exemptions.tsv` or landing-gate exemptions; (b) use of `merge/souji/` staged rows (ids in the S109-S242 range) or GLib 2.84.0 origin-record sources; (c) anything writing to {LANE_L} or depending on {LANE_L}/corpus/SOURCES.md. Never write outside your report; `git` read-only against the lane. Concise overlap table: sibling | surface | round/evidence | conflict risk. Deliver at {RD('ConnSiblings')}.""")

add("ConnSources","connector",
f"""Cross-source pattern finder: compare the staged package rows in /home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md with the lane registry {LANE_L}/corpus/SOURCES.md. The lane holds S001-S132 — the package stages S109-S242. Identify which staged rows add an aspect the lane does NOT already hold, focused on the F4 origin-record theme (S152, S210, S211, S022-adjacent rows) and the F3 near-duplicate taxonomy rows (S213-S217 and neighbours). List: staged id | aspect not held | recommended action (adopt / reject / already-held) for at least the F4 cluster and 5 more rows. Read-only; never write into /home/vgpnk/Projects/shokuknow. Report at {RD('ConnSources')}.""")

add("ConnClaims","connector",
f"""Cross-claim dependency check for round 27. Read {R27}/preregistration.txt. Verify the three claims are causally separable: C1 (exemption rows in corpus/pointer-exemptions.tsv + landing-gate counter), C2 (knowledge entries + SOURCES rows + gate + census), C3 (new pre-report-gate tool + fixture). For each pair (C1/C2, C1/C3, C2/C3) state whether any single counter's before/after could change because the OTHER claim lands, and whether the counters share any byte (e.g. census after runs over a tree that also contains C2's rows — is that a dependency or just a same-tree measurement?). Verdict per pair: independent / dependent (name the dependency). Report at {RD('ConnClaims')}.""")

# ---------------- scouts ----------------
add("ScoutC1Baseline","scout",
f"""Reproduce the C1 baseline at {BASE}: run `python3 -B {LANE_L}/tools/souji-landing-gate.py --root {LANE_L} --rev {BASE} --round 27 --fleet-root {FLEET}` and capture the exact SUMMARY line + the two LG-DANGLING-PTR rows. Also run WITHOUT `--fleet-root` and record the 5-finding output. Identify the exact tokens flagged and the file:line of each. Optionally inspect the gate's parser (read-only) to explain why `corpus/knowledge/registry` and `corpus/lessons/round-24.md:232:S118` are matched as paths. Produce a tsv receipt draft (findings=2) for the L1's c1-before.tsv. Report at {RD('ScoutC1Baseline')}.""")

add("ScoutC1FleetDebt","scout",
f"""Check the three fleet-hosted citations that the landing gate resolves when `--fleet-root` is given: {LANE_L}/corpus/README.md:217 (`../../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md`, `JjAuditSouji.md`) and {LANE_L}/corpus/knowledge/jj-colocation-receipts.md:148 (`.ufo/waves/hyaku/jj-w1/reports/`). Verify those files exist in {FLEET}/.ufo/waves/hyaku/jj-w1/reports/ (ls -la), confirm their content genuinely supports the citation (read the two Souji reports' relevant sections), and confirm the directory citation is a real directory. Verdict: fleet-documented (not a lane defect) or stale. Read-only. Report at {RD('ScoutC1FleetDebt')}.""")

add("ScoutRows152210211","scout",
f"""Extract the raw staged rows S152, S210 and S211 verbatim from /home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md (grep the `| S152 |`, `| S210 |`, `| S211 |` lines). For each, list campaign-schema defects vs the lane contract: recheck cell prose vs ISO date/cadence, any literal or escaped `|` inside a cell, used-by cell mismatch with this round's admitted entries (corpus/knowledge/origin-record-writer-r27.md, corpus/knowledge/origin-record-mechanism-set-r33.md), status cell. Read-only (never write into /home/vgpnk/Projects/shokuknow). Deliver a normalization table: raw cell -> normalized cell. Report at {RD('ScoutRows152210211')}.""")

add("ScoutGlibFetch","scout",
f"""Prepare the GLib re-grounding snapshots for C2 (in scratch; the L1 commits them under census/round-27/sources/). Fetch, with bounded `curl -fsSL --max-time 60`: https://raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c and https://raw.githubusercontent.com/GNOME/glib/2.84.0/glib/gfileutils.c into /var/tmp/souji-r27-ScoutGlibFetch/. Compute sha256 of each; verify the cited lines exist: glocalfile.c lines 2261, 2282, 2284, 2359, 2387 and gfileutils.c lines 1697, 1369, 1367, 1041, 1108 (sed -n). Extract a <=25-word verbatim quote from each file (no `|` inside) suitable for the Gate blocks, and record the exact location of each quote. If a fetch fails, record the failure text and mark unavailable (do not fake). Report at {RD('ScoutGlibFetch')}.""")

add("ScoutKnowledgeDrafts","scout",
f"""Read the two proposed knowledge entries in full from /home/vgpnk/Projects/shokuknow/lanes/souji: `round6/KNOWLEDGE-PROPOSED.md` (entry `corpus/knowledge/origin-record-writer-r27.md`, source S152, opened 2026-10-23) and `round13/KNOWLEDGE-PROPOSED.md` (entry `corpus/knowledge/origin-record-mechanism-set-r33.md`, sources S210/S211). Copy their full text into your report. Check PROVINCE fit ({LANE_L}/PROVINCE.md F4 row) and QUALITY bar ({LANE_L}/corpus/QUALITY.md Q1-Q59, especially Q4/Q17/Q54/Q56): list every clause that must be re-grounded or re-verified this round (campaign `opened` dates prove nothing; quotes must be re-located by us). Report at {RD('ScoutKnowledgeDrafts')}.""")

add("ScoutSliceReopen","scout",
f"""Re-derive the souji slice of the absent-defect-register at /home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md (awk on `souji` + round + S-id). Compare the current slice to the r24 verdicts ({LANE_L}/census/round-24/records/slice-verdicts.tsv and {LANE_L}/.ufo/waves/round-24/assimilation/slice-verdicts.tsv). For any row whose status/class changed or that is newly present, give it a fresh verdict (fetch the cited source in bounded scratch; locate the quote; payload-absent -> refuse, unreachable -> unverifiable). Also attempt a fresh bounded fetch of the S118 DOI/Crossref path to see whether the r24 `accepted` re-grade still holds. Summarize: slice rows | r24 verdict | r27 verdict | change. Report at {RD('ScoutSliceReopen')}.""")

add("ScoutScorecardState","scout",
f"""Verify the SCORECARD preconditions for round 27 at {BASE}: (a) registry rows = 132 (`grep -cE '^\|[[:space:]]*S[0-9]{{3,}}[[:space:]]*\|' {LANE_L}/corpus/SOURCES.md`); (b) grounded F4 = 2 (`grep -rlE '^ground: F4' {LANE_L}/corpus/knowledge/ | wc -l`); (c) the latest measurements block is Round 26 and its counted commits exist and are ancestors of master; (d) `## Planned` names the next round (r28); (e) axis scores row shows calibration 7 / operability 8 / coverage 8. Report the exact observed numbers with commands. Report at {RD('ScoutScorecardState')}.""")

add("ScoutReportShape","scout",
f"""Read {FLEET}/.ufo/reports/round-26/souji.md and the round-25 verifier spot-checks ({LANE_L}/corpus/lessons/round-26-verifier-spotcheck.md, round-25-verifier-spotcheck.md) to extract the exact report contract and the routed defects owed this round (commit the r26 w1 trailing seat outputs; S-language edition rows; __pycache__ dirs). Produce the report skeleton checklist for the L1: required sections in order, marker rule, SHONEN heading requirements (one line per box), Stale-lane line, installs section, and the pre-report gates (ls-remote == branch tip; grep -c '^## SHONEN' == 1). Deliver the checklist with pointers to each requirement's source line. Report at {RD('ScoutReportShape')}.""")

add("ScoutTooling","scout",
f"""Verify the host toolchain this round: `node --version`; presence and checksum of /home/vgpnk/Projects/ufo-fsd-alpha/scripts/ufo-swarm-wave.mjs; /home/vgpnk/Projects/shokunin/scripts/sources-census.sh; /home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh (state verb) and fleet-commit.sh; `git --version`; policy files /home/vgpnk/Projects/shokunin/scripts/hyaku/ufo-wave-policy-v2.json (band 64-128). Report versions and any tool that is missing or would need an install (if one is needed, propose channel/version/reason per /home/vgpnk/.omp/agent/RULES.md; do NOT install). Also confirm the lane helper identity rule: `jj-lane.sh commit <lane> --as souji`. Report at {RD('ScoutTooling')}.""")

add("ScoutPreReport","scout",
f"""Research the failure modes the C3 pre-report gate must catch. Read: {FLEET}/.ufo/watchdog.log lines around 2026-10-25T14:42-14:47 (round 27 attempt 1 death: `lane-dead-no-report`), the round-26 verifier defect 1 (trailing w1 outputs past driver complete), and the r25 lesson's duplicate-dispatch incident. From these, enumerate the exact checks the pre-report gate must run, with the shell/pipeline that would detect each (branch tip == `git ls-remote origin refs/heads/<branch>`; report exists; `grep -c '^## SHONEN'` == 1; lane worktree has no uncommitted lane-authored leftovers; preregistration file present). For each check name the failure mode it prevents. Report at {RD('ScoutPreReport')}.""")

add("ScoutExemptionFormat","scout",
f"""In bounded scratch (/var/tmp/souji-r27-ScoutExemptionFormat), copy {LANE_L}/corpus/pointer-exemptions.tsv and the two files to be exempted (corpus/QUALITY.md, corpus/lessons/round-24.md) and simulate the two proposed exemption rows exactly as they will be appended: `corpus/knowledge/registry` and `corpus/lessons/round-24.md:232:S118`. Then run the landing gate (git show copy at {BASE}) against the copy with `--fleet-root` and confirm: (a) findings drop to 0; (b) no OTHER finding is masked (run the gate before vs after in the copy); (c) an over-broad counterexample (e.g. exempting `corpus/knowledge/` prefix) would clear a REAL dangling finding — show it still fails, proving the two specific rows are precise. Report the before/after finding counts. Report at {RD('ScoutExemptionFormat')}.""")

# ---------------- executors ----------------
add("ExecC1Counter","executor",
f"""Create the C1 counter script DRAFT at {REPO}/c1-counter.sh (the L1 installs it as census/round-27/c1-counter.sh). It must: accept `--rev <full40>` (required, refuse short/HEAD), run `python3 -B {LANE_L}/tools/souji-landing-gate.py --root {LANE_L} --rev $REV --round 27 --fleet-root {FLEET}` in a scrubbed env, parse the `SUMMARY findings=N` line, and emit a tsv receipt with columns rev|gate_cmd_sha256|findings|checked_reg|rc. Refuse to run without --rev. Include a `--base` mode that pins {BASE} and emits the before receipt shape. Do not execute against the live tree beyond harmless grammar checks; deliver the script text in your report. Report at {RD('ExecC1Counter')}.""")

add("ExecExemptions","executor",
f"""Author the exact two new rows for {LANE_L}/corpus/pointer-exemptions.tsv as a draft file {REPO}/exemptions-add.tsv (tab-separated: path TAB reason). Row 1: `corpus/knowledge/registry` — reason must state it is a prose fragment in QUALITY.md Q59's surface-class sentence, not a citation. Row 2: `corpus/lessons/round-24.md:232:S118` — reason: composite enumerated-site token (file:line:row) consumed by tests/fixtures/r25-q57-check.sh as an argument; the gate's path grammar over-matches it; the site itself resolves (round-24.md line 232 carries the S118 verdict row). Keep reasons <=200 chars, truthful, no tabs/newlines. Verify the current file's schema (4 existing rows) and that your rows sort/format identically. Report at {RD('ExecExemptions')}.""")

add("ExecC2GateCheck","executor",
f"""Prepare the C2 gate runner DRAFT at {REPO}/c2-gate.sh (L1 installs as census/round-27/c2-gate.sh). It invokes `python3 -B {LANE_L}/tools/souji-gate-check.py --root {LANE_L} --round-date <ISO-today> --entries corpus/knowledge/origin-record-writer-r27.md corpus/knowledge/origin-record-mechanism-set-r33.md --snapshot-dir census/round-27/sources --slice census/round-27/records/slice-verdicts.tsv --slice-verdicts census/round-27/records/slice-verdicts.tsv` and emits a tsv with entries/ok/fail/rc. Read tools/souji-gate-check.py (read-only) to confirm the CLI flags and expected outputs; note what `--slice`/`--slice-verdicts` expect so the L1 can generate the real slice file (empty allowed). Deliver script text. Report at {RD('ExecC2GateCheck')}.""")

add("ExecAssimMirror","executor",
f"""Build the scratch assimilation mirror in /var/tmp/souji-r27-ExecAssimMirror: copy {LANE_L}/corpus/ (incl. SOURCES.md, knowledge/, lessons/) plus the proposed append block (the normalized S152/S210/S211 rows inserted in the Registry table) and the two admitted knowledge files at their repo-relative paths. Then run `{FLEET}/scripts/sources-census.sh validate --file <mirror>/corpus/SOURCES.md` and iterate until exit 0 with 0 errors (W04 warnings allowed). Also run the manual census greps (row count, malformed NF=13, duplicate ids, enum violations, mined used-by existence) on the mirror and include outputs. If any E03/E04 finding appears (duplicate id / within-scope duplicate URL), stop and report which row; do not append past it. Report at {RD('ExecAssimMirror')}.""")

add("ExecRowsNormalize","executor",
f"""Produce the normalized 11-column SOURCES rows for S152, S210, S211 as a draft append block at {REPO}/rows-append.md, transformed from the staged raw rows (see ScoutRows152210211's table). Contract: 11 columns exactly (id|source|kind|tier|scope|anchor|teaches|status|opened|recheck|used-by); no literal or escaped `|` inside any cell; `recheck` = `365d` (ISO or cadence, no prose); `status` = `mined`; `used-by` lists exactly `corpus/knowledge/origin-record-writer-r27.md` and/or `corpus/knowledge/origin-record-mechanism-set-r33.md` per row; `opened` = today's ISO date; `teaches` <=25 words. Keep the staged URL/anchor evidence; re-point any anchor that must be re-located by our own fetch. Verify each row passes the census `awk NF==13` shape. Report at {RD('ExecRowsNormalize')}.""")

add("ExecKnowledgeWriter","executor",
f"""Draft the knowledge entry `corpus/knowledge/origin-record-writer-r27.md` at {REPO}/origin-record-writer-r27.md for the L1 to install. Front matter: `source: S152 — <GLib glocalfile.c URL at tag 2.84.0>`, `verified-at: <today ISO> — GLib tag 2.84.0; snapshot fetched this round (sha256 in census/round-27/sources/)`, `recheck: 365d`, `ground: F4 — restorable quarantine (who WRITES a per-item origin record, and with what guarantees)`. Body: grounded only in the fetched bytes and located <=25-word quotes; a `## Gate` section listing candidates (admit this entry; reject at least one staged candidate with reason+flip, e.g. a zh/ja edition row whose version alignment is unprovable at decision time per the routed S119 lesson); ADMIT/REJECT rows with the locate quote and access date. No universal clauses; no credential material. Report at {RD('ExecKnowledgeWriter')}.""")

add("ExecKnowledgeMechanism","executor",
f"""Draft the knowledge entry `corpus/knowledge/origin-record-mechanism-set-r33.md` at {REPO}/origin-record-mechanism-set-r33.md. Front matter: `source: S210 — <glocalfile.c URL>`, `source: S211 — <gfileutils.c URL>`, `verified-at: <today ISO> — GLib tag 2.84.0; snapshots fetched this round (sha256 in census/round-27/sources/)`, `recheck: 365d`, `ground: F4 — restorable quarantine (whether a per-item origin record needs O_EXCL uniqueness, rollback, or a different scheme)`. Body: the three complementary mechanisms (exclusive create reservation, temporary-file content write, atomic rename) grounded in the fetched bytes with line-anchored <=25-word quotes; state the limits (this is GLib's implementation, not a specification; no receipt-format decision follows). Include a `## Gate` section with >=1 admit and >=1 reject (with reason+flip) from the staged set. Report at {RD('ExecKnowledgeMechanism')}.""")

add("ExecFixtureC3Gate","executor",
f"""Implement the C3 pre-report gate DRAFT at {REPO}/souji-pre-report-gate.sh (the L1 installs it as {LANE_L}/tools/souji-pre-report-gate.sh). Frozen CLI: `bash tools/souji-pre-report-gate.sh --lane <abs-lane> --branch <branch> --report <abs-report> [--prereg <abs-file>]`. Checks (each prints `check-<name>=PASS|FAIL|SKIP`): (1) `tip` — `git -C <lane> rev-parse refs/heads/<branch>` equals `git -C <lane> ls-remote origin refs/heads/<branch>` (first line); (2) `report` — report file exists and is nonempty; (3) `shonen` — `grep -c '^## SHONEN' <report>` == 1; (4) `clean` — `git -C <lane> status --porcelain` shows no untracked/modified paths outside an optional `--allow` list (default empty; the L1 passes allowed wave/records dirs); (5) `prereg` — prereg file exists. Exit 0 iff all PASS; exit 1 with FAIL lines otherwise; exit 2 on usage. Shell: set -u; no external non-POSIX tools; run in a scrubbed env. Deliver the script text in your report. Report at {RD('ExecFixtureC3Gate')}.""")

add("ExecFixtureC3Tests","executor",
f"""Implement the C3 selftest harness DRAFT at {REPO}/r27-pre-report-gate.sh (L1 installs as {LANE_L}/tests/fixtures/r27-pre-report-gate.sh). It builds 4 isolated worlds under /var/tmp/souji-r27-ExecFixtureC3Tests (each a `git init` repo with a local bare remote + empty worktree): case 1 clean-pass (tip==remote, report with `## SHONEN`, clean tree, prereg present) -> exit 0 all PASS; case 2 remote-mismatch (remote tip differs) -> FAIL tip, exit 1; case 3 missing-SHONEN (report exists but no heading) -> FAIL shonen, exit 1; case 4 dirty-tree (untracked file) -> FAIL clean, exit 1; plus control FALSE-GREEN: an always-pass stub tool must be rejected (harness detects it and fails). The harness must be deterministic, remove its scratch, and print a final line `cases=4 pass=4 control=FALSE-GREEN-REJECTED`. Deliver harness text. Report at {RD('ExecFixtureC3Tests')}.""")

add("ExecC3Counter","executor",
f"""Create the C3 counter script DRAFT at {REPO}/c3-counter.sh (L1 installs as census/round-27/c3-counter.sh): it verifies the tool exists, runs `bash {LANE_L}/tests/fixtures/r27-pre-report-gate.sh`, parses the `cases=4 pass=4 control=FALSE-GREEN-REJECTED` line, and emits a tsv receipt (tool_sha256 of the installed tool bytes, cases, pass, control, rc). Also emit the presence check `tool=absent|present`. Deliver script text. Report at {RD('ExecC3Counter')}.""")

add("ExecLessonScaffold","executor",
f"""Create the round-27 lesson skeleton DRAFT at {REPO}/round-27.md (L1 installs as {LANE_L}/corpus/lessons/round-27.md): sections `## Gate` (candidates, admitted, rejected with reasons, spot-check placeholder), `## Findings`, `## Residuals`, `## Receipts`, `## Mistakes` (rows ready to fill: R27-M1 class=landing — attempt 1 misread the inline-spawn handoff and refused resume; evidence {FLEET}/.ufo/watchdog.log:1377; captured-by none; fix: this round's C3 pre-report gate incl. a `prereg`/handoff readiness check, plus the prompt now states the L1 writes the ready file), and `## Seat-reported failures` (empty template). Keep all values as placeholders for L1 integration; no fabricated evidence. Report at {RD('ExecLessonScaffold')}.""")

add("ExecSearchLogRow","executor",
f"""Draft the SOURCES `## Search log` note for this round's openings at {REPO}/search-log.md: one PRISMA-inspired block for the F4 origin-record re-grounding (question: which GLib bytes define who writes a per-item origin record and with which mechanisms; where searched: raw.githubusercontent.com GNOME/glib tag 2.84.0 files; date: today; identified 2, screened 2, included 2 (S210/S211), excluded 0; stop rationale: the normative format remains the FreeDesktop trash spec, already held as S022) and a block for the quarantine-slice re-open. No universal claims. Report at {RD('ExecSearchLogRow')}.""")

add("ExecPathsStudy","executor",
f"""Draft a SOURCES `## Paths` addition at {REPO}/paths-study.md: an ordered study sequence for the F4 origin-record ground, e.g. `F4 origin-record — S022 → S152 → S210 → S211: why this order` (spec first, then the reference writer, then the mechanism set), plus a one-line justification per hop. Keep to the contract's `## Paths` shape. Report at {RD('ExecPathsStudy')}.""")

add("ExecReadmeMap","executor",
f"""Draft the coverage-map update for {LANE_L}/corpus/README.md at {REPO}/readme-map.md: the F4 row's `entries` cell gains `knowledge/origin-record-writer-r27.md`, `knowledge/origin-record-mechanism-set-r33.md`; the Frontier F4 line's `next` text becomes per the round outcome (record format/staging tool changes still operator decisions). Also draft the F4 status cell wording that matches the round's landing (candidate, admission pending closure — consistent with prior frontier rows). Quote the current row text first; then the exact replacement lines. Report at {RD('ExecReadmeMap')}.""")

add("ExecCensusAfterScript","executor",
f"""Create the after-state measurement script DRAFT at {REPO}/census-after.sh (L1 runs it at integration): (a) `{FLEET}/scripts/sources-census.sh validate --root {FLEET} souji` -> rc; (b) registry row count; (c) `grep -rlE '^ground: F4' {LANE_L}/corpus/knowledge/ | wc -l`; (d) c1 gate findings; (e) c3 fixture; (f) `git -C {LANE_L} status --porcelain` leftovers summary. Emit a single tsv receipt with every value and rc. Note it must run AFTER the L1's integration, so it just reads expected state; no writes beyond its own output file path given as `--out`. Report at {RD('ExecCensusAfterScript')}.""")

add("ExecWavesEvidence","executor",
f"""Prepare the wave evidence files for the L1: (a) copy the `plan` validation output (from `node /home/vgpnk/Projects/ufo-fsd-alpha/scripts/ufo-swarm-wave.mjs plan --spec <spec>`) into {REPO}/w1-validate.out; (b) record the spec sha256; (c) draft the `w1-dispatch.json` summary note (policy band, spawn count, role histogram) as {REPO}/wave-note.md. Read-only on everything else; do not run the validator yourself (the L1 does). Report at {RD('ExecWavesEvidence')}.""")

add("ExecScorecardDraft","executor",
f"""Draft the SCORECARD additions for round 27 at {REPO}/scorecard-draft.md: (a) a `### Round 27 measurements` block with the C1/C2/C3 rows (claim | axis | before | after | counting command | measured commit) with EVIDENCE-PENDING placeholders for the after values; (b) an appended `## Round 27 append-only corrections` note for the two pointer-exemptions rows (if any in-place line references move, map them); (c) a `- **r28 (planned r27)**` planned bullet naming next round's intended claims (calibration/coverage/operability continuations); (d) capability-table rows for the pre-report gate (name, what it does, evidence pointer, first-working round 27). Follow the file's existing table shapes exactly. Report at {RD('ExecScorecardDraft')}.""")

add("ExecMisrootPlan","executor",
f"""Prepare the misroot sweep plan for the L1 at {REPO}/misroot-plan.md: the L1 must run `git -C {FLEET} status --porcelain` (no pathspec) and for every untracked file at the fleet root that names this lane/round, copy it byte-exact into {LANE_L}/<same relative path>, `cmp`, then delete the fleet copy and record under Mistakes. Draft the exact commands and the criteria (only files this round's seats wrote; never touch .ufo/state/*, .scratch/, other lanes' files). Report at {RD('ExecMisrootPlan')}.""")

add("ExecInheritedResolve","executor",
f"""Catalog the inherited r26 wave leftovers at {LANE_L}/.ufo/waves/round-26/w1/: run `git -C {LANE_L} status --porcelain -- .ufo/waves/round-26/w1` and split into tracked-modified vs untracked; for each file, state whether it is a seat report/results/script, its mtime, and propose the resolution: commit under this round's entry (wave evidence) with the exact path list, or sweep (with reason). Verify none of them are operator-owned (no `round-*-aggregator-*`/`verifier-spotcheck` files in that dir). Deliver the path list ready for the jj-lane.sh helper: `-- .ufo/waves/round-26/w1/...`. Report at {RD('ExecInheritedResolve')}.""")

add("ExecPycacheFix","executor",
f"""Draft the .gitignore hygiene for {LANE_L} at {REPO}/gitignore-draft.md: verify the three `__pycache__/` dirs (census/round-10/__pycache__, tools/__pycache__, tests/fixtures/__pycache__) are untracked and propose adding `__pycache__/` (and optionally `*.pyc`) to {LANE_L}/.gitignore, confirming no tracked file matches the pattern (`git ls-files | grep __pycache__` empty). Provide the exact two lines to append. Report at {RD('ExecPycacheFix')}.""")

# ---------------- reviewers ----------------
add("RevC1Counter","reviewer",
f"""Attack the C1 counter: read {R27}/preregistration.txt C1 and the landing-gate CLI. Questions: (1) does `findings=N` from SUMMARY count exactly the LG-DANGLING-PTR rows, and can a different invocation (no --fleet-root) or a different --round change N? (2) Is `findings=2` at {BASE} reproducible — run it once in read-only mode and compare; (3) can the exemption mechanism be gamed so a real dangling citation disappears (try adding a broad exemption in a scratch copy and show the gate clears a REAL break -> that must fail C1); (4) does the counter pin the gate's committed bytes (tool sha256 vs installed file)? Verdict: counter sound / gameable (name the mutation). Report at {RD('RevC1Counter')}.""")

add("RevC1ExemptionSemantics","reviewer",
f"""Review the planned pointer-exemptions.tsv additions (see ExecExemptions). Check against the gate's exemption rule (Q31): a committed exemption row must carry a truthful reason; an exemption that suppresses nothing is itself a finding. Verify row 1 (`corpus/knowledge/registry`) is indeed only prose in QUALITY.md Q59 (quote the sentence) and not a real citation; verify row 2 (`corpus/lessons/round-24.md:232:S118`) is a composite site token consumed by tests/fixtures/r25-q57-check.sh (quote the check column) and that round-24.md line 232 actually exists and concerns S118. Also confirm there is no alternative fixing that would be better (e.g. gate grammar change) and record why it is out of scope this round. Verdict: exemptions justified / not. Report at {RD('RevC1ExemptionSemantics')}.""")

add("RevC2Entries","reviewer",
f"""Review the two drafted knowledge entries (origin-record-writer-r27.md, origin-record-mechanism-set-r33.md) against PROVINCE F4, QUALITY Q1-Q59 (esp. Q4 /var/tmp self-containment, Q17 resolved fixture/evidence, Q54 snapshot locators, Q56 grounded mapping) and the SOURCES contract. Check each `source:` cites an appended S-row opened this round, `verified-at:` is today, `recheck:` is a cadence, and every factual claim is grounded in a located <=25-word quote from the fetched bytes (no campaign-quote reuse). Flag any overclaim (e.g. implying a receipt-format decision, or universal statements). Verdict per entry: admit-ready / needs fixes (list). Report at {RD('RevC2Entries')}.""")

add("RevC2Rows","reviewer",
f"""Review the normalized append rows S152/S210/S211 (see ExecRowsNormalize) against the 11-column census schema and the append-only rule. Verify: no `|` inside cells; `id` unique within the registry (S001-S132 present — confirm 152/210/211 do not collide); `status=mined`; `used-by` exactly the two admitted entries; `tier` scoped (code/dataset rows: A is allowed for pinned source code — confirm the scope cell makes the scoping explicit); `recheck` ISO/cadence. Then run the manual census awk checks on a scratch copy with the rows appended and include outputs. Verdict: rows append-ready / defects (list). Report at {RD('RevC2Rows')}.""")

add("RevC2Mirror","reviewer",
f"""Review the assimilation mirror procedure (ExecAssimMirror): confirm the mirror contains a byte-exact copy of the lane corpus + the append block + the knowledge files at repo-relative paths; confirm `sources-census.sh validate --file` exits 0 with 0 errors before any append; confirm the id-collision proof (comm -12) was run with the 0-3-space pattern and produced the full S109-S132 collision set, and that adopted ids continue the registry (S152/S210/S211 are >S132 and need no renumber). Flag anything that could make the E03/E04 gate a false pass. Verdict: mirror gate sound / broken. Report at {RD('RevC2Mirror')}.""")

add("RevC3Gate","reviewer",
f"""Review the C3 pre-report gate script (ExecFixtureC3Gate): shell hygiene (set -u, no nonexit traps, no eval), exit-code contract (0 all PASS, 1 any FAIL, 2 usage), no mutation of the lane (read-only git), correct `git -C` usage, correct ls-remote parsing (first line, ref match), and that the `clean` check does not false-flag the lane's own allowed dirs (the `--allow` list is passed by the L1). Identify at least three ways the script could produce a false PASS (e.g. missing set -e after cmp, empty branch name, report path with spaces) and propose guards. Verdict: gate sound / needs fixes. Report at {RD('RevC3Gate')}.""")

add("RevC3Fixture","reviewer",
f"""Review the C3 selftest harness (ExecFixtureC3Tests): determinism (fixed seeds, no wall-clock dependence), isolation (all worlds under /var/tmp, cleaned by trap), that each world is a real repo with a real bare remote (so ls-remote comparison is meaningful), and that the FALSE-GREEN control actually exercises the stub path (the harness must fail if the stub passes). Also check the harness itself cannot pass vacuously (e.g. by not running cases). Verdict: fixture sound / needs fixes. Report at {RD('RevC3Fixture')}.""")

add("RevMistake","reviewer",
f"""Review the planned R27-M1 mistakes row (see ExecLessonScaffold): class vocabulary fit (mistakes.md §5 classes), evidence pointer resolvability ({FLEET}/.ufo/watchdog.log line 1377), captured-by (none), and whether the claimed fix (C3 pre-report gate incl. handoff readiness) is really shown able to fail — propose the concrete red-before demonstration the L1 must commit (e.g. running the gate on a workspace lacking a prereg file must FAIL). Also propose a second mined mistake candidate if you find one (e.g. the r26 leftover wave outputs as a `landing`/`bookkeeping` mistake). Verdict: mistakes plan sound / needs fixes. Report at {RD('RevMistake')}.""")

add("RevReportIntegrity","reviewer",
f"""Review the planned report contract against {FLEET}/.ufo/reports/round-26/souji.md and the protocol: required sections in order (Work performed / Landed changes / Before→after measurements / Sources & frontier / Trend verdicts / SHONEN / Stale-lane / installs), marker rule (contentless = failed), SHONEN heading with one line per box, commit-hash citation rule (lane tip cited and ancestor), report lands last after lane push, fleet commit via fleet-commit.sh --as souji. Identify anything that would make the report a marker or non-conformant, and list the exact pre-report commands. Verdict: plan conformant / gaps. Report at {RD('RevReportIntegrity')}.""")

add("RevNoHarm","reviewer",
f"""Check the no-axis-harmed invariant for all three claims: C1 touches only corpus/pointer-exemptions.tsv (append) + census receipts; C2 appends SOURCES rows, two knowledge entries, README map row, lesson/LOG/SCORECARD updates; C3 adds tools/ + tests/fixtures/ + gitignore. For each, confirm no existing admitted entry/row/criterion is rewritten or deleted (append-only), no other lane's files touched, and no score changes (calibration 7, operability 8, coverage 8 stay). Also confirm no claim changes another claim's counter (ConnClaims). Verdict per claim: no-harm holds / violation (name). Report at {RD('RevNoHarm')}.""")

add("RevInheritedSafe","reviewer",
f"""Review the plan to commit the inherited r26 w1 leftovers under this round's entry (ExecInheritedResolve): (1) verify none of the files contain a nested `.git` (git check-ignore / find), (2) verify all paths are under `.ufo/waves/round-26/w1/` and are lane-authored seat outputs (not aggregator/operator files), (3) confirm the jj-lane.sh helper is the only writer — the L1 must pass explicit file paths, never a directory containing nested `.git`, (4) confirm committing them does not violate the `nothing to commit` or identity rules. Also confirm the alternative (sweep) is not chosen for track-record files. Verdict: commit plan safe / hazard. Report at {RD('RevInheritedSafe')}.""")

add("RevTrendForecast","reviewer",
f"""Forecast the three trend verdicts for round 27 with evidence mapping: expansion (C2 adds two admitted entries on F4 ground not previously held, each citing mined rows opened this round — improved if gates pass), quality (entries re-grounded with fresh verified-at; no existing entry falsified — improved if no re-check fails), discernment (gate decisions vs outside spot-check; C1 resolves two citation defects; prereg/axis-check discipline — improved if the counter wins hold). List the exact observations that would flip each verdict to unchanged/harmed. Report at {RD('RevTrendForecast')}.""")

# ---------------- critics ----------------
add("CritC1Attack","critic",
f"""Adversarially attack C1 (calibration). Read {R27}/preregistration.txt C1. Attack vectors: (1) is `findings=2→0` a real improvement or bookkeeping? The two findings are grammar over-matches — do they actually measure self-assessment quality, or just the gate's parser? (2) Could the claim be satisfied by a do-nothing control (e.g. by changing the gate invocation rather than fixing anything)? (3) Does the exemption mechanism weaken the gate for future rounds (false sense of cleanliness)? (4) Is `findings=2` at base exactly reproducible, and is the `--fleet-root` pass legitimate (it changes what counts)? Deliver a numbered attack list with verdicts (kills claim / survives). Report at {RD('CritC1Attack')}.""")

add("CritC2Attack","critic",
f"""Adversarially attack C2 (coverage/assimilation). Vectors: (1) is F4 origin-record writer/mechanism ground genuinely uncovered, or is `quarantine-origin-record-fields-r24.md` already claiming it (compare grounding lines and scope cells)? (2) Are S152/S210/S211 merely the campaign's own rows, and does citing them add knowledge or just rows (CORPUS rule 4: expansion is knowledge, not rows)? (3) Do the two entries duplicate each other (writer vs mechanism-set overlap)? (4) Would a do-nothing control (append rows without entries) trip the same counters — does the gate check actually tie rows to entries? Deliver numbered attacks with verdicts. Report at {RD('CritC2Attack')}.""")

add("CritC3Attack","critic",
f"""Adversarially attack C3 (operability). Vectors: (1) is a pre-report gate script a real operability move or busywork — does it replace a step the L1 actually performs, and is it demonstrably runnable end-to-end? (2) Could the selftest pass vacuously (harness missing a case, or control not actually wired)? (3) Are the checks themselves meaningful (ls-remote equality, SHONEN count, clean tree) — could a broken lane still pass all five? (4) Does the script touch only read-only git? Deliver numbered attacks with verdicts. Report at {RD('CritC3Attack')}.""")

add("CritAssimAttack","critic",
f"""Attack the assimilation compliance of C2 against the addendum §10 contract: (1) id-collision proof must be committed as wave evidence with the exact comm command and the 0-3-space pattern; (2) quarantine slice reporting — every slice row needs a verdict; (3) ≥1 admit AND ≥1 reject with Gate blocks; (4) re-grounding — campaign `opened` dates prove nothing, our quotes must be from our own fetch; (5) no staged row appended as-is (normalization required); (6) scratch transform + mirror gate exit 0 BEFORE any append; (7) assimilation must be named in the report's Sources & frontier section. List every requirement and mark the plan's coverage. Report at {RD('CritAssimAttack')}.""")

add("CritCounterFidelity","critic",
f"""Attack counter fidelity across all three claims: (1) each counter's before state must be measured against the SAME committed counter bytes at the named base rev (check that c1/c2/c3 counters will exist at base or that before receipts are produced from base bytes); (2) receipts must pin measured commits (40-hex, durable, reachable) and tool sha256 (Q55); (3) counters must reject an always-zero emitter (FALSE-GREEN control) — verify each claim's counter has one; (4) no counter may depend on the live worktree (revision-scoped). Deliver verdicts per claim. Report at {RD('CritCounterFidelity')}.""")

add("CritNoHarmAttack","critic",
f"""Hunt hidden harms: (1) C1 exemptions — could they hide future real dangling pointers (check the exemption format's reason-only gate)? (2) C2 — does appending rows risk colliding with ids the campaign package uses elsewhere (S152/S210/S211 are within the staged range — confirm the lane registry never receives them twice) or with future staged rows? (3) C3 — does the new tool/checklist contradict SKILL's existing gate registry (same name conflicts)? (4) Does anything touch operator-owned surfaces (config.yml, mcp.json, scripts/, .ufo/state/)? (5) Does the C2 source opening (GLib) imply any dependency outside the lane? Deliver findings with severity. Report at {RD('CritNoHarmAttack')}.""")

add("CritErrorPatterns","critic",
f"""Attack the round plan using SKILL's error-pattern tables ({LANE_L}/SKILL.md error signatures): (1) unpushed-lane trap — do the c1/c2/c3 counters or receipts risk reading branch-based state while jj keep-only commits exist? (2) checkpoint-blob bloat — will any new census/round-27 files be huge or contain generated blobs? (3) phantom fixture / wrong-byte — do the C3 fixture worlds verify `rev-parse --show-toplevel`? (4) git deletes without receipt — does anything run git maintenance? (5) post-guard FIFO swap — do any new reads open repo files without bounds? Deliver findings. Report at {RD('CritErrorPatterns')}.""")

add("CritReportContract","critic",
f"""Attack the planned report for marker/gap risk: (1) would any section be missing at filing (Sources & frontier and Trend verdicts are conformance items — must appear); (2) is every requirement bullet backed by an evidence pointer planned (committed file/line, command output, commit hash); (3) does the report meet the `SHONEN` heading rule (exactly one line per box); (4) will the timing hold (report last, after lane pushed, citing tip hash); (5) are the wave shape/seat counts/roles/dead seats and planner-seat mapping recorded; (6) is the Stale-lane line present. Deliver a checklist with pass/fail per item based on the current plan. Report at {RD('CritReportContract')}.""")

add("CritRoutings","critic",
f"""Review role/route assignments for the wave and the assumptions: each seat's role must exist in the run-7 route map (executor/labrat/scribe/simplifier/critic/revenger→m_flash; reviewer/mutation-tester→m_zfl; connector→m_antigravity; scout→m_mim); no seat passes a model; seats keep their captured route on resume; report the expected answering-model bucket per role from ~/.omp/agent/config.yml (read-only) and flag any role missing from the table. Also verify the L1 (m_kfc) is the only integrator and that no seat is a coordinator. Deliver the mapping table. Report at {RD('CritRoutings')}.""")

add("CritSlotValidation","critic",
f"""Attack the wave spec itself: read the generated spec JSON (the L1 will write it) only if present; otherwise review the item list design: unique names, pairwise-distinct prompts, roles matching the policy's `lanes` set, band 64-128 (v2), maxLanes ≤100, reportDir lane-relative, no duplicates, no frozen-topology seats. List any role/name/prompt risk that would make the validator refuse, and any two items that overlap in deliverables (same report path). Report at {RD('CritSlotValidation')}.""")

# ---------------- mutation-testers ----------------
add("MutC1Exempt","mutation-tester",
f"""Mutation-test the C1 exemption approach. In scratch, take a copy of {LANE_L}/corpus/pointer-exemptions.tsv at {BASE} and the gate, then apply mutations to the two proposed exemption rows: (a) prefix-broaden row 1 to `corpus/knowledge/` — verify the gate then clears a REAL dangling finding (fabricate one, e.g. cite `corpus/knowledge/nonexistent.md`) and shows it must NOT pass; (b) drop the tab; (c) empty reason; (d) point row 2 at `corpus/lessons/round-24.md` only. For each mutation state pass/fail of the gate run and why the two exact rows are the minimal correct fix. Report at {RD('MutC1Exempt')}.""")

add("MutC1Count","mutation-tester",
f"""Mutation-test the C1 counter invocation: run the landing gate at {BASE} with mutations — (a) `--round 26` (must NOT change findings count semantics? record output), (b) without `--fleet-root` (must show 5 findings), (c) with `--rev` short hash (must refuse or fail), (d) `--rev {BASE}` again (reproducibility: two runs identical). Confirm the counter's `findings=N` line is stable and the receipt format captures rc. Report at {RD('MutC1Count')}.""")

add("MutC2Rows","mutation-tester",
f"""Mutation-test the C2 append-block gate: take the mirror (ExecAssimMirror procedure) and apply five mutations to the normalized rows — (a) status cell `mined`→`queued`; (b) used-by cell lists an entry that does not exist; (c) a literal `|` inside a quote cell; (d) recheck cell `365d`→prose; (e) duplicate id with an existing registry row. For each, run `{FLEET}/scripts/sources-census.sh validate --file ...` and the manual awk checks; confirm every mutation is caught (exit non-0 or malformed>0) and the clean mirror passes. Report at {RD('MutC2Rows')}.""")

add("MutC3Tool","mutation-tester",
f"""Mutation-test the C3 pre-report gate: create variants of the draft script in scratch — (a) always-PASS branch (every check echoes PASS and exits 0) → the harness must fail it; (b) remove `set -u`; (c) compare `git rev-parse` against `git ls-remote` output with trailing whitespace (does the comparison normalize?); (d) omit the report-exists check. For each variant state whether the harness/fixture catches it (red) and why. Report at {RD('MutC3Tool')}.""")

add("MutC3Checks","mutation-tester",
f"""Mutation-test the C3 selftest harness itself: (a) drop case 2 (remote mismatch) from the harness — does it still print `cases=4`? (must not); (b) change the FALSE-GREEN stub to a genuinely passing tool — the harness must fail (control wired); (c) make the harness skip cleanup — trap still removes scratch; (d) run the harness twice — deterministic output. Report observed vs expected per mutation. Report at {RD('MutC3Checks')}.""")

add("MutLessonTick","mutation-tester",
f"""Mutation-test the R27-M1 mistakes-row plan: the fix must be shown able to fail. Build the red-before demonstration in scratch: run the C3 pre-report gate on a workspace where the preregistration file is missing (must FAIL check `prereg`) and where the report lacks the `## SHONEN` heading (must FAIL `shonen`); capture the failure text. Then confirm the fix (the gate's checks) is the only delta. Also verify the lesson row's evidence pointer resolves (watchdog line 1377). Report at {RD('MutLessonTick')}.""")

# ---------------- labrats ----------------
add("LabKinsProbe","executor",
f"""Empirically probe the landing-gate's token grammar (read-only) to confirm the two flagged tokens are the ONLY over-matches of their kind: construct ~6 synthetic variants in scratch (`corpus/knowledge/registry`, `corpus/lessons/round-24.md:232:S118`, `corpus/lessons/round-24.md:240`, `corpus/knowledge/nonexistent.md`, `LOG.md:1692`, `SCORECARD.md:181`) inside a scratch copy of the authority files and run the gate at {BASE}; record which are flagged and which are accepted. This pins that the two exemption rows precisely cover the over-match classes and no sibling token needs one. Report at {RD('LabKinsProbe')}.""")

add("LabF4Probe","executor",
f"""Probe the F4 ground count method: run both `grep -rlE '^ground: F4' {LANE_L}/corpus/knowledge/ | wc -l` (expect 2) and `python3 -B {LANE_L}/tools/souji-coverage-agreement.py --root {LANE_L} --rev {BASE}` (expect grounded=9 mapped=9) and reconcile the two numbers (the tool counts all grounded entries; the claim's counter is the grep). Also verify README's F4 row entries cell currently names exactly the 2 grounded files. Report observed numbers. Report at {RD('LabF4Probe')}.""")

add("LabCensusProbe","executor",
f"""Empirically compare the manual registry-row grep against `sources-census.sh validate` on a scratch copy after appending the three rows: confirm both agree (132→135) and that W04 warnings stay warning-only (exit 0). Also verify the 0-3-space indented-collision guard on a synthetic fixture: a registry with an indented `  | S210 |` row colliding with the staged set must produce a nonempty `collisions` file (paste the proof). Report at {RD('LabCensusProbe')}.""")

add("LabSliceFetch","executor",
f"""Bounded reachability probes for the quarantine-slice rows (in /var/tmp/souji-r27-LabSliceFetch, curl --max-time 30, no writes to lane): attempt fresh fetches for the payload-absent slice sources (S114 git-prune doc, S123/S124/S131/S133 own-work outputs are lane-internal — skip, S126 gtk docs, S138 qiita) and the unreachable S118 (DOI → Crossref API). For each, record URL, HTTP status, bytes fetched, and whether the r24 quoted span is present in the fetched bytes (grep). Verdict per row: re-verified / still absent / still unreachable. Report at {RD('LabSliceFetch')}.""")

add("LabGitIgnoreProbe","executor",
f"""Probe the proposed .gitignore addition: in scratch, create a mini repo with `__pycache__/` dirs and files, apply the proposed `__pycache__/` rule, and verify `git status --porcelain` hides only untracked pycache entries while `git ls-files` (tracked) is unaffected; confirm no tracked lane file matches the pattern (`git -C {LANE_L} ls-files | grep -c '__pycache__'` → 0). Also confirm the three real dirs become ignored (status clean for them). Report at {RD('LabGitIgnoreProbe')}.""")

# ---------------- simplifiers ----------------
add("SimplWaveSpec","simplifier",
f"""Review the 80-item wave spec for redundancy: flag any two items whose deliverables overlap (same report path or same evidence), any task text that duplicates another's core ask, and any item that is padding (no distinct output). Propose merges or deletions ONLY as recommendations (the L1 decides); never change the spec yourself. Deliver a table: item pair | overlap | merge proposal. Report at {RD('SimplWaveSpec')}.""")

add("SimplExistingTools","simplifier",
f"""Scan {LANE_L}/tools/ and census/ for dead or superseded artifacts that this round's work could remove or consolidate (recommendations only): e.g. the many `impl-*.sh`/`cand-*` variants, `souji-round9-s18-*` files, duplicate counter scripts. State for each candidate: path, why superseded (evidence), and whether removal is safe (nothing references it — grep). No deletions. Report at {RD('SimplExistingTools')}.""")

add("SimplReportText","simplifier",
f"""Review the planned report/lesson prose style against recent reports (r25/r26): flag placeholder noise, duplicated boilerplate, and sentences that would read as unsupported claims. Provide a tightened skeleton for the report's Work performed and Trend verdicts sections (without fabricating numbers). Report at {RD('SimplReportText')}.""")

# ---------------- revenger ----------------
add("RevengC1Gate","revenger",
f"""Reverse-engineer how the landing gate decides `LG-DANGLING-PTR` for the two tokens (read-only on tools/souji-landing-gate.py): find the exact regex/parser path that matches `corpus/knowledge/registry` (a backticked token in QUALITY.md) and `corpus/lessons/round-24.md:232:S118` (a composite token), how `--fleet-root` changes resolution, and how exemptions are read from pointer-exemptions.tsv (matching semantics: exact path? prefix?). Document the line numbers in the tool and confirm the two proposed exemption rows will be matched exactly (not prefix). This pins C1's fix correctness. Report at {RD('RevengC1Gate')}.""")

# ---------------- scribes ----------------
add("ScribePrereg","scribe",
f"""Review the frozen preregistration file {R27}/preregistration.txt against the axis-check tool's machine block expectations: run `python3 -B {LANE_L}/tools/souji-axis-check.py --prereg {R27}/preregistration.txt --scorecard {LANE_L}/SCORECARD.md` and record output (expect claims=3 flags=0; if flags>0, report the exact flag lines). Also verify the text matches the three claims as they appear in this wave's context. Report at {RD('ScribePrereg')}.""")

add("ScribeLessonGate","scribe",
f"""Draft the `## Gate` section content for corpus/lessons/round-27.md at {REPO}/lesson-gate.md: candidates table (the F4 staged entries S152/S210/S211 source rows, plus reject candidates with reason+flip), admitted rows with our access date and <=25-word located quotes (from ScoutGlibFetch), rejected rows with reasons, and the spot-check placeholder (non-author verifier duty). Keep to the lesson format of round-26.md's Gate. Report at {RD('ScribeLessonGate')}.""")

add("ScribeSOURCES","scribe",
f"""Draft the SOURCES additions for the lane registry at {REPO}/sources-add.md: the normalized S152/S210/S211 rows (from ExecRowsNormalize) formatted into the Registry table continuation (11 columns), plus the Search log and Paths notes (from ExecSearchLogRow/ExecPathsStudy), plus any status/recheck/used-by change log old→new for existing rows (this round: none expected — state that). Read the current SOURCES tail to match formatting. Report at {RD('ScribeSOURCES')}.""")

add("ScribeScorecard","scribe",
f"""Draft the SCORECARD Round 27 measurements block and planned bullet (from ExecScorecardDraft) in final prose form: numbers as placeholders `[PENDING]` where the L1 must fill after integration, but exact commands written out. Follow the Round 26 block's table shape byte-for-byte. Report at {RD('ScribeScorecard')}.""")

add("ScribeReport","scribe",
f"""Assemble the full round report draft at {REPO}/report-draft.md with sections in order: Work performed (naming claims C1/C2/C3 and target axes), Landed changes, Before→after measurements, Sources & frontier, Trend verdicts, SHONEN (4 box lines with `[~]`/`[ ]` + pointers), Stale-lane, installs. Fill everything known from other seats' drafts; use `[PENDING:<what>]` only where the L1's integration values are required. Read the r26 report for exact style. Report at {RD('ScribeReport')}.""")

add("ScribeLOG","scribe",
f"""Draft the LOG.md Round27 append entries at {REPO}/log-draft.md: one entry per claim with the motivating evidence pointers (receipt paths, commits), the inherited-leftover resolution, and the assimilation/auxiliary mentions. Match LOG.md's existing round-entry style (date header, bullet Evidence). Report at {RD('ScribeLOG')}.""")

add("ScribeInvariant","scribe",
f"""Draft the SKILL.md gate-registry and capability/authority wording updates needed for the new C3 tool at {REPO}/skill-add.md: a gate-registry row for `souji-pre-report-gate` (entry command, verdict map, self-test command, pinned-value path, write scope, owner) consistent with existing rows, and any SKILL checklist/known-surface updates tied to this round. No restyling of unrelated content. Report at {RD('ScribeInvariant')}.""")

add("ScribeFrontierNotes","scribe",
f"""Draft the frontier notes section for corpus/README.md and the round lesson at {REPO}/frontier-notes.md: F4 status after landing (writer + mechanism-set admitted; record format/staging tool changes remain operator decisions), F1/F2/F3/F5 states unchanged (quote their current lines), and the F4 `next` line. Report at {RD('ScribeFrontierNotes')}.""")

# ---------------- spec assembly ----------------
spec = {
    "wave": "souji-r27-w1",
    "reportDir": WDIR,
    "maxLanes": 100,
    "context": CTX,
    "items": items,
}
assert len(items) == 79, len(items)
from collections import Counter
roles = Counter(i["role"] for i in items)
print("items:", len(items), dict(roles))
names = [i["name"] for i in items]
assert len(set(names)) == len(names), "duplicate names"
assert len(set((i["prompt"]) for i in items)) == len(items), "duplicate prompts"
with open(f"{R27}/w1-spec.json", "w") as f:
    json.dump(spec, f, indent=1)
print("wrote", f"{R27}/w1-spec.json")
