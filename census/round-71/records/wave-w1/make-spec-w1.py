#!/usr/bin/env python3
"""Build .ufo/waves/round-71/w1-spec.json (souji r71, one v1 falsification/build wave of 12 seats)."""
import json
import os

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SCR = "/fast/scratch/hyaku/souji-r71"
GS = ("/skill:godspeed\nYou are a Godspeed-enabled subagent.\n\n1. **Name the axes.**\n2. **Iterate cheap, in "
      "parallel.**\n3. **Keep moves that improve any axis and harm none.**\n4. **Don't aim — let the frontier "
      "walk itself.**\n\n## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large "
      "batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. "
      "Act directly via tool calls.\n\n\n")

BASE = "8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0"
FREEZE = "aa91d1cad89200ec733edd3475461010a372923d"
CAND = "a1db6c8514771c0a0321c29741831606d09cc2a5"
AFTER = "52e8c3faf678b0f3d2f18cc6d41a365dc91123f7"

CONTEXT = f"""# Goal
souji round 71 (lane repo {LANE}, lane id souji). The L1 (SoujiR71) holds the planner seat and is the ONLY integration owner: it commits through the lane helper and writes the report. You are one seat of ONE wave of 12 seats. Seats deliver files and findings only. Your mandate is to FALSIFY the frozen round-71 claims and the round's other landed changes: re-derive every number yourself from committed bytes; a number you cannot reproduce is a finding. Do not trust the L1's counts.

# Chronology (binding; read {LANE}/census/round-71/preregistration.txt first)
- Base (round start, r70 admitted): {BASE}
- Freeze {FREEZE}: preregistration, census/round-71/c1-counter.py (70-row successor of the r70 counter), c1-matrix.tsv, c2-harness.py, c2-mutants.json (X6-X10), make-controls.py, mk-counter.py, controls (c1-do-nothing, c1-F1/F2/F3 all EXIT=1; c2-before-r70 score=5 EXIT=1; c2-CF1 EXIT=2), probes/attr-filemode-probe.sh + -base.txt, srcs/ (gitattributes, git, git-config captures), records/census-before.txt.
- Candidate {CAND}: tools/souji-receipt-write.py scrubs GIT_ATTR_SOURCE, pins -c core.fileMode=true on every writer git call, refuses RECEIPT-FILTER-DRIVER-SET (pre-run and post-run) when a tracked path's filter attribute names a driver with a configured clean or process command; selftest cases 39-40.
- After {AFTER}: census/round-71/records/c1-after.txt, c2-after.txt, writer-selftest.txt, counter-selftest.txt; corpus/SOURCES.md S306-S308 (admit, mined), S309 (reject), S310 (queued); corpus/knowledge/filter-filemode-witness.md; correction appended to corpus/knowledge/common-dir-route-receipt-writer.md; corpus/README.md frontier r71; SKILL.md registry rows r71.

# Claims (frozen predicates are in the preregistration; never change them)
C1 operability: the r71 counter at the candidate prints SUMMARY matrix=70 base_forgeries=7 base_honest=19 new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS, EXIT=0 (before: do-nothing new_forgeries=7 class_mismatches=7 EXIT=1).
C2 calibration: the c2-harness over census/round-71/c1-counter.py prints SUMMARY label=c2-after-r71 positive_selftest=PASS x_mutants=5 x_killed=5 x_survived=0 cm_mutants=4 cm_killed=4 cm_survived=0 score=0, EXIT=0 (before: the r70 counter x_survived=5 score=5 EXIT=1).

# Frozen invocations (run from {LANE}; never alter the counter, matrix, harness, mutant set or any control)
- C1 candidate: python3 -B census/round-71/c1-counter.py --root {LANE} --matrix census/round-71/c1-matrix.tsv --base-rev {BASE} --rev {CAND} --tool tools/souji-receipt-write.py --work <SCRATCH>/c1
- C1 with a file: the same with --new-tool <FILE> instead of --rev/--tool
- Counter selftest: python3 -B census/round-71/c1-counter.py --selftest --root {LANE} --matrix census/round-71/c1-matrix.tsv --base-rev {BASE} --work <SCRATCH>/st
- C2 after: python3 -B census/round-71/c2-harness.py --label c2-after-r71 --counter census/round-71/c1-counter.py --matrix census/round-71/c1-matrix.tsv --root {LANE} --base-rev {BASE} --mutants census/round-71/c2-mutants.json --work <SCRATCH>/c2
- C2 before: the same with --label c2-before-r70 --counter census/round-70/c1-counter.py --matrix census/round-70/c1-matrix.tsv --base-rev e063a2fcb3f5f3fb8fb19d2ae1592b1f22e6a333
- Writer selftest: python3 -B tools/souji-receipt-write.py --selftest --work <SCRATCH>/wst (set TMPDIR=<SCRATCH>/wst too)
<SCRATCH> must be a fresh directory under {SCR}/<your seat name>/ (mkdir -p it; --work dirs must exist). Counters refuse --work under /tmp, /var/tmp, TMPDIR or inside the lane root. A C1 run takes 1-5 minutes; a harness run about 4 minutes. Never write to /tmp except files under 50 MB. Do NOT run the receipt writer with an --out inside the lane.

# Write scope and bounds
You write ONLY under {LANE}/.ufo/waves/round-71/w1/ (your own seat directory <SeatName>/ and your own <SeatName>.md) and under your scratch dir. Never edit lane tracked files (census/, tools/, corpus/, SCORECARD.md, LOG.md, PROVINCE.md, SKILL.md, SHONEN.md). Never edit MANIFEST.json, .ufo/state/, .ufo/watchdog.log, /home/vgpnk/Projects/shokunin/templates/, /home/vgpnk/Projects/shokunin/scripts/, /home/vgpnk/Projects/shokunin/.scratch/, or any sibling repo. Never commit, push, stash, reset, checkout, switch, pull, or run any mutating git or jj command in the lane or the fleet repo. Read-only git (show, log, diff, status, rev-parse, cat-file, ls-files, ls-remote) is fine; read-only jj only with --ignore-working-copy.
Fixture repos (round-70 incident: a seat's `git -C ""` with an empty variable fell back to the fleet root and committed there): create D=$(mktemp -d -p "{SCR}/<seat>") and immediately check `[ -n "$D" ] && [ -d "$D" ] || exit 1`; git -C "$D" init -q; verify `[ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ]` before the first commit; name -C "$D" on every later git call (never a bare `git commit`); in Python use subprocess with an explicit absolute cwd/-C and assert it is non-empty. Commit only with an explicit fixture identity inside $D. To mutate a file, copy it into your scratch dir first; never edit it in the lane.
Never message agent://all; never call the task tool. Never change host sysctls, sudo settings or kernel parameters; if a probe needs one, report the need instead.
Scratch discipline: mkdir -p "{SCR}/<seat>" and pass it explicitly (TMPDIR, --work); trap 'rm -rf -- "$S"' EXIT in shell (copy receipts to your seat directory first). Check bash /home/vgpnk/Projects/shokunin/scripts/hyaku/disk-guard.sh status before any heavy pass; on ENOSPC report the free space you saw and stop. Remove your scratch dir before you yield.
Every `Report:` trailer path is relative to {LANE}; write it at {LANE}/<that path>. All paths you name must be absolute under {LANE} or your scratch dir.

# Tooling authorization (operator, 2026-10-19)
You and every seat may install or upgrade tools that help the task. Read /home/vgpnk/.omp/agent/RULES.md first (official channels, update-safety gate; record tool, version, channel and reason in your report). pacman transactions are PAUSED host-wide (orchestrator ruling 2026-10-20): install via uv tool, npx, or an official binary in ~/.local/bin, or file an L0 question. Never run pacman -Sy, -Syu, -U, -R or a downgrade.

# Report format
Your final answer is your yield. Keep it under 40 lines: verdict per item, the exact commands you ran, the observed output lines that decide the verdict, file:line evidence, and any finding tagged HIGH, MEDIUM or LOW. Name every file you wrote under your seat directory. Also write the same content to your report file at the Report path.
"""

ITEMS = [
    ("S71Connector", "connector", """# Target
Sibling-overlap and cross-claim scan for round 71. Read-only.

# Change
1. Grep the other lanes' repos (read-only; each *-shokunin/ directory under /home/vgpnk/Projects/shokunin except souji-shokunin) for tools that decide 'clean tree' from `git status`/`diff --quiet`/`ls-files -m` and inherit the caller's environment: name each (file:line) and say whether it scrubs GIT_ATTR_SOURCE, pins core.fileMode, or checks filter drivers.
2. Cross-claim coupling: decide whether C1 (writer matrix verdict) and C2 (counter self-check harness) are causally separable as the preregistration states — could C1's after-arm change if the counter's selftest section (8) and the verify_members name checks were reverted, and vice versa? Give the code lines that decide it.
3. Check the README r71 frontier 'Ground:' sentence against `git show 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0:corpus/knowledge/<each>.md`: is it true that no earlier entry treats a clean filter as a status-witness route?

# Acceptance
A table of sibling hits with scrub/pin/check yes/no, a separability verdict with line evidence, and a true/false verdict on the Ground sentence with the grep you ran."""),
    ("S71ScoutSources", "scout", """# Target
Re-open the round-71 sources live and check registry rows S306-S310 in corpus/SOURCES.md.

# Change
1. Fetch https://git-scm.com/docs/gitattributes, https://git-scm.com/docs/git and https://git-scm.com/docs/git-config fresh into your scratch dir; record HTTP status, byte count and sha256; compare with census/round-71/srcs/*.html (sha256sum).
2. For each of S306, S307, S308, S309, S310 locate the quoted text in the tag-stripped, whitespace-normalized page (Python: html.unescape(re.sub(r'<[^>]+>',' ',t)) then collapse whitespace); report its offset, its section, and its word count (<=25 required). Compare with the offsets cited in the rows (they cite census/round-71/srcs/*.txt).
3. Decide whether S309's reject reason is true (does the ENVIRONMENT entry for GIT_ATTR_SOURCE say the tree replaces the worktree attributes?) and whether S310 (attr.tree, queued) should instead be mined or rejected.
4. Check each row's 'teaches' cell says only what the page says; check row shape (11 columns), status, and that each used-by path exists at {AFTER}.

# Acceptance
Fetch receipts, located quotes with offsets and word counts, a verdict per row (agree/disagree with reasons), any wrong cell named.""".replace("{AFTER}", AFTER)),
    ("S71ExecC1", "executor", """# Target
Reproduce C1 from committed bytes, without reading the L1's after-receipt first.

# Change
1. Run the C1 candidate invocation (timeout 1800). Record CASE lines for AS1 AS2 ASh FC1 FC2 FC3 FCh FCh2 FM1 FM2 FMh, REGRESS, SUMMARY and EXIT.
2. Run C1 with --new-tool on the base writer (census/round-71/controls/base-writer-8b9345b1.py; check its sha256 equals `git show 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0:tools/souji-receipt-write.py | sha256sum`) and on each of census/round-71/controls/variants/F1-refuse-on-presence.py, F2-attr-source-scrub-only.py, F3-filemode-pin-only.py. Record SUMMARY and EXIT of each.
3. Only AFTER steps 1-2, diff your ^(CASE|SUMMARY|EXIT=) lines against census/round-71/records/c1-after.txt and census/round-71/controls/c1-*.txt. Report identical or the differing lines.
4. Chronology: git merge-base --is-ancestor freeze -> candidate -> after; git log --format='%H %ci' for each; confirm tools/souji-receipt-write.py is unchanged between base and freeze (git diff --quiet base freeze -- tools/souji-receipt-write.py) and that the frozen instruments are unchanged between freeze and after (git diff --stat freeze after -- census/round-71/c1-counter.py census/round-71/c1-matrix.tsv census/round-71/c2-harness.py census/round-71/c2-mutants.json census/round-71/controls census/round-71/preregistration.txt).

# Acceptance
Your SUMMARY/EXIT lines for the five runs, the diff results, the chronology checks with exit codes."""),
    ("S71ExecC2", "executor", """# Target
Reproduce C2 from committed bytes, without reading the L1's receipts first.

# Change
1. Run the C2 after and C2 before invocations (timeout 1800 each). Record POSITIVE, MUTANT, SUMMARY and EXIT lines.
2. Run the harness over census/round-71/controls/variants/CF1-selftest-always-fails.py (label c2-CF1, matrix census/round-71/c1-matrix.tsv, base-rev 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0): must be EXIT=2.
3. Check the mutant set: for each of X6..X10 in census/round-71/c2-mutants.json, apply old->new to census/round-70/c1-counter.py and compare with census/round-70/records/wave-w1/seats/S70MutCounter/mutants/<id>.py (cmp); report equal/different.
4. Only AFTER steps 1-3, diff your lines against census/round-71/records/c2-after.txt and census/round-71/controls/c2-*.txt (ignore scratch paths). Run the writer and counter selftest invocations; compare SELFTEST lines with census/round-71/records/writer-selftest.txt and counter-selftest.txt.
5. Harness hardening: run the harness with --label ../escape and with --label a/b: both must refuse EXIT=2 without touching anything outside --work; after a normal run without --keep, confirm the label directory is gone.

# Acceptance
Your SUMMARY/EXIT lines, 5 cmp verdicts, the diff results, the two SELFTEST lines, label-refusal results."""),
    ("S71ExecPointer", "executor", """# Target
Round-70 routed D3: tools/souji-pointer-check.py exits 1 on missing pointers (a gate by behaviour) but has no self-test. Build one; do NOT edit the lane file — write a complete proposed replacement at {LANE}/.ufo/waves/round-71/w1/S71ExecPointer/souji-pointer-check.py.

# Change
1. Read tools/souji-pointer-check.py (92 lines) and its receipts census/round-70/records/pointer-check-r69.txt and pointer-check-r70.txt.
2. Add a `--selftest --work DIR` mode (stdlib only) that builds a throwaway git repo under DIR (follow the fixture-repo rule in the context exactly), commits a file citing one existing and one missing lane path plus one path in a code span that must NOT be counted if the current tool excludes such spans (read the code to learn its grammar; do not change its grammar), and asserts: missing=1 and exit 1 on that file; missing=0 and exit 0 on a file citing only existing paths; exit 2 on a non-40-hex --rev. Print `SELFTEST cases=N pass=P fail=F` and exit 0 iff fail=0.
3. Show it can fail: run your selftest against a mutant copy whose missing-path test is inverted or whose exit code is always 0; record that the selftest fails (exit 1).
4. Re-run your proposed file in normal mode on the two r70 receipts' inputs (same --rev and files as recorded in their headers) and confirm the SUMMARY lines equal the committed receipts.

# Acceptance
The proposed file, selftest output (pass), the mutant selftest outputs (fail), and the two normal-mode SUMMARY comparisons.""".replace("{LANE}", LANE)),
    ("S71MutWriter", "mutation-tester", """# Target
Mutation-test the round-71 writer change against the frozen r71 counter and the writer selftest.

# Change
1. Copy tools/souji-receipt-write.py (at the candidate) into your scratch dir. Build single-edit mutants, each a separate file: W1 drop "GIT_ATTR_SOURCE" from the git() scrub tuple; W2 drop the `"-c", "core.fileMode=true"` pin; W3 delete the pre-run `_filter_drivers` refusal (keep the post-run one); W4 delete the post-run refusal (keep the pre-run one); W5 check only `clean`, not `process`; W6 treat the attribute value `set` as a driver; W7 return [] from _filter_drivers when ls-files output is non-empty but check-attr fails; W8 any other single edit you judge most likely to survive.
2. Run C1 with --new-tool on each mutant (timeout 1800; you may run them in parallel with separate --work dirs). Record SUMMARY/EXIT and which rows refute it.
3. Run the writer selftest on each mutant copy; record whether cases 39/40 fail.
4. Shown able to fail: copy the BASE writer (git show 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0:tools/souji-receipt-write.py), append cases 39/40 and their CASES entries plus the FILTER_CLASS constant from the candidate, run --selftest: both must FAIL.
5. Each survivor (EXIT=0 in C1 and selftest passing) is a finding with severity; W4 and W5 are expected to survive the matrix (no in-run driver-creation row, no process row) — say whether that is a gap in the claim or a declared limit (prereg 'Named limits').

# Acceptance
A mutant table: id, edit, C1 SUMMARY/EXIT, case 39/40 result, verdict; plus the base-writer case 39/40 result."""),
    ("S71MutCounter", "mutation-tester", """# Target
Mutation-test the round-71 counter's own self-check beyond the frozen X6-X10 and CM1-CM4.

# Change
1. Copy census/round-71/c1-counter.py into your scratch dir. Build at least eight further single-edit mutants aimed at the r71 additions, for example: Y1 MEMBER_RE accepts '/'; Y2 drop the SHA256SUMS non-plain-name check; Y3 drop the symlinked-member check; Y4 _row_env returns {} for attr-source-filter (GIT_ATTR_SOURCE never set); Y5 mutate() skips the filter.t.clean config for committed-filter; Y6 FORGED_SAMESIZE changed to a size-changing value; Y7 local-filemode skips chmod_notes; Y8 the 'edit-counter-samesize' in-run kind writes the committed bytes (no edit); plus any of your choice.
2. Run the counter selftest on each mutant (timeout 900). killed iff EXIT != 0.
3. For each selftest survivor, run the C1 candidate arm with that mutant counter (timeout 1800) and record whether SUMMARY/EXIT still equals the frozen predicate — a mutant that keeps EXIT=0 while removing a row's attack is a blind spot of the instrument (report its SUMMARY).
4. Confirm each X6..X10 edit in census/round-71/c2-mutants.json matches exactly once in census/round-71/c1-counter.py.

# Acceptance
A mutant table: id, edit, selftest result, C1-arm result, verdict. Survivors are findings, not claim failures."""),
    ("S71Reviewer", "reviewer", """# Target
Correctness review of the round-71 diff: git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0 {AFTER} -- tools/ census/round-71/*.py census/round-71/*.json census/round-71/*.tsv SKILL.md corpus/.

# Change
1. Writer: _filter_drivers — is the check-attr -z output parsed correctly (path NUL attr NUL value NUL triples; paths with spaces/newlines; empty index)? Is `git config --get filter.<name>.clean` correct for driver names with dots or uppercase (config subsection case-sensitivity)? Does the pinned env (GIT_CONFIG_GLOBAL=/dev/null, NOSYSTEM) mean a driver configured only globally is ignored — and is that safe given the status read ignores it too? Is the post-run check placed before any receipt byte? Does `-c core.fileMode=true` change any carried verdict (W1/W7/PK4/PK7 rows)?
2. Counter: does any carried r70 row's env or fixture change (compare CASE_SPECS and _row_env against census/round-70/c1-counter.py)? Are the new rows' fixtures built as described in the preregistration (read mutate/_row_env)? Does the selftest (8) test what it claims?
3. Harness: is `killed` correctly defined; can a crashing mutant be counted killed; are label/work checks sound?
4. Preregistration vs receipts: every number in census/round-71/preregistration.txt matches the committed receipts byte for byte (list any mismatch).
5. SKILL.md r71 rows: commands copy-paste runnable; verdict maps match the code.

# Acceptance
A verdict per item (SOUND / DEFECT with severity) with file:line evidence.""".replace("{AFTER}", AFTER)),
    ("S71CriticClaims", "critic", """# Target
Attack the two round-71 claims as claims.

# Change
1. C1: could a do-nothing or a cheaper fix reach the frozen target? Consider the controls (F1 blanket refusal, F2 attr-source scrub only, F3 fileMode pin only), refusing on any configured filter.* key (does FCh2 really kill it?), refusing on any filter attribute (does FCh kill it?), running status with --no-renames or `-c core.attributesFile`. Is new_honest=19 reachable only by the landed design?
2. C1 axis: operability vs coverage/calibration, using /home/vgpnk/Projects/shokunin/AXES.md and the lane SCORECARD axis definitions.
3. C2: the mutants X6-X10 were authored by a previous-round seat (S70MutCounter) and frozen unchanged, but the killing tests were written by the L1 this round knowing the mutants. Is score=0 'teaching to the test'? Is C2 a calibration claim under the prompt rule 'a calibration claim must count mismatches between the lane's self-assessment and observed repo state' — compare with the r70 closure's ruling in corpus/lessons/round-70-verifier-spotcheck.md (C2 section).
4. Separability and chronology: is each claim verifiable without the other? Compare commit times (git log --format='%H %ci') of freeze, candidate and after.
5. Does any committed text overstate (README Ground sentence, knowledge entry, SKILL rows, prereg named limits)?

# Acceptance
A verdict per claim: STANDS / QUALIFIED (exact qualification) / FALLS, with evidence."""),
    ("S71CriticDiscern", "critic", """# Target
Discernment check of the round's source gate: S306, S307, S308 admitted (mined); S309 rejected; S310 queued.

# Change
1. Re-open https://git-scm.com/docs/gitattributes, https://git-scm.com/docs/git and https://git-scm.com/docs/git-config yourself. Decide independently whether S306 is the right ground for 'a clean driver makes status report a size-preserving edit as clean' (does the page say status/diff use the clean command? quote it), whether S307 grounds 'GIT_ATTR_SOURCE replaces the worktree attributes', and whether S308 grounds 'repository-local core.fileMode=false hides a mode flip'.
2. Is S309 (ENVIRONMENT entry) rightly rejected for that scope, or is it adequate ground? Should S310 (attr.tree) be queued, mined or rejected?
3. Check corpus/knowledge/filter-filemode-witness.md: every factual sentence is supported by S306-S310 or by a committed receipt/probe it names; list unsupported or overstated sentences.
4. Check the correction appended to corpus/knowledge/common-dir-route-receipt-writer.md: is the original sentence really false, and does the correction cite evidence that shows it?

# Acceptance
agree/disagree per decision with reasons and located quotes; list of unsupported sentences (or none)."""),
    ("S71Sentinel", "sentinel", """# Target
Security and fail-closed review of the round-71 writer changes: what still forges a clean-tree receipt?

# Change
1. Probe attribute routes the matrix does not cover, each against the CANDIDATE writer (git show a1db6c8514771c0a0321c29741831606d09cc2a5:tools/souji-receipt-write.py) in fixture repos, size-preserving forged bytes, --out under your scratch dir with --allow-outside: (a) repository-local `attr.tree` naming a commit with `filter=t`; (b) repository-local `core.attributesFile` naming a file with `filter=t`; (c) `filter.t.process` driver (a real long-running filter you write, or explain why git refuses it); (d) the wrapped command adds a filter driver + attribute and edits a file in-run; (e) `ident`, `working-tree-encoding`, `eol`/`text` with core.autocrlf in repository config — any size-preserving rewrite git status hides? (f) a driver name with uppercase or dots; (g) `core.ignoreStat`, `core.trustctime`, `core.checkStat=minimal` or `core.untrackedCache` in repository config — can any hide an in-run or pre-run change from the candidate?
2. For each route record writer rc, receipt written or not, and the refusal text.
3. Counter/harness: try the S70Sentinel F3/F4/F5 traversal cases against the r71 counter's verify_members and the r71 harness --label; are they closed?
4. Rate each finding HIGH/MEDIUM/LOW with a reproducible command.

# Acceptance
Finding list with commands and observed output; 'none found' only with the probes you ran."""),
    ("S71Scribe", "scribe", """# Target
Draft material for the round-71 lesson (corpus/lessons/round-71.md is written by the L1; you write a draft file only).

# Change
1. Read census/round-71/preregistration.txt, census/round-71/records/*.txt, census/round-71/controls/*.txt, corpus/lessons/round-70.md and corpus/lessons/round-70-verifier-spotcheck.md.
2. For each r70 routed defect D1-D5 (spot-check) and each r70 'Routed to round 71' item (a)-(d) and later (lesson round-70.md line 78), state whether round 71 closed it, with the commit or file that shows it, or 'open' — as a table.
3. Draft two candidate '## Mistakes' rows in the lane format (class | evidence pointer | captured-by | fix) from what you see in committed bytes of rounds 67-71 that is not already listed in corpus/lessons/round-70.md.
4. Run `python3 -B tools/souji-pointer-check.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 52e8c3faf678b0f3d2f18cc6d41a365dc91123f7 census/round-71/preregistration.txt corpus/knowledge/filter-filemode-witness.md` and report its SUMMARY and EXIT; list any missing pointer.

# Acceptance
The routed-item table, two draft Mistakes rows and the pointer-check result, written to your seat directory as draft.md."""),
]


def main() -> None:
    items = [{"name": n, "role": r, "prompt": GS + b} for n, r, b in ITEMS]
    spec = {
        "wave": "souji-r71-w1",
        "milestone": "souji r71: falsification of C1 filter-driver/core.fileMode witness hardening and C2 counter self-check of the r70 survivors; D3 pointer-check selftest build",
        "reportDir": ".ufo/waves/round-71/w1",
        "context": CONTEXT,
        "items": items,
    }
    out = os.path.join(LANE, ".ufo/waves/round-71/w1-spec.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=1, ensure_ascii=False)
    print(out, len(items))


if __name__ == "__main__":
    main()
