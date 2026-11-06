#!/usr/bin/env python3
"""Build .ufo/waves/round-70/w1-spec.json (souji r70, one v1 falsification wave of 12 seats)."""
import json
import os

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
GS = ("/skill:godspeed\nYou are a Godspeed-enabled subagent.\n\n1. **Name the axes.**\n2. **Iterate cheap, in "
      "parallel.**\n3. **Keep moves that improve any axis and harm none.**\n4. **Don't aim — let the frontier "
      "walk itself.**\n\n## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large "
      "batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. "
      "Act directly via tool calls.\n\n\n")

BASE = "e063a2fcb3f5f3fb8fb19d2ae1592b1f22e6a333"
FREEZE = "0243af04bbcd422302b4efc3473612073c9aa962"
CAND = "93a051b2c936ff6eafca8e8b31d918e3d20fd3da"
AFTER = "e84f691b9b022425449e2aecc2e7ae308aee4ffe"
TIP = "feb283eea6d03656864d9dcba43e178b127681ee"

CONTEXT = f"""# Goal
souji round 70 (lane repo {LANE}, lane id souji). The L1 (SoujiR70) holds the planner seat and is the ONLY integration owner: it commits through the lane helper and writes the report. You are one seat of ONE post-landing FALSIFICATION wave of 12 seats. Seats deliver files and findings only. Your mandate is to FALSIFY the frozen round-70 claims and the round's other landed changes: re-derive every number yourself from committed bytes; a number you cannot reproduce is a finding. Do not trust the L1's counts.

# Chronology (binding; read {LANE}/census/round-70/preregistration.txt first)
- Base (round start, r69 admitted): {BASE}
- Freeze {FREEZE}: preregistration, census/round-70/c1-counter.py (59-row successor of the r69 counter), census/round-70/c1-matrix.tsv, census/round-70/c2-harness.py, census/round-70/make-controls.py, controls (c1-do-nothing EXIT=1, c1-F1-refuse-on-presence EXIT=1, c1-F2-literal-only-scrub EXIT=1, c2-before-r69 score=5 EXIT=1, c2-CF1/CF2 EXIT=2), probes/lp-ls-files-probe.txt, records/census-before.txt, srcs/ (git-manual.html, gitglossary.html).
- Candidate {CAND}: tools/souji-receipt-write.py scrubs GIT_LITERAL_PATHSPECS, GIT_GLOB_PATHSPECS, GIT_NOGLOB_PATHSPECS, GIT_ICASE_PATHSPECS from every writer git call (PATHSPEC_ENV); selftest case 38.
- After-arms {AFTER}: census/round-70/records/c1-after.txt, c2-after.txt, writer-selftest.txt, counter-selftest.txt.
- 0d8ce29a5e53c5202464f5b2bc755f3686ae1f60: r69 routed D1, byte mirror of .ufo/waves/round-69/w1 into census/round-69/records/wave-w1/.
- Tip {TIP}: corpus/SOURCES.md S304 (admit) and S305 (reject), corpus/knowledge/pathspec-env-scrub.md, corpus/README.md frontier, SKILL.md registry rows (r69 D3, r70).

# Claims (frozen predicates are in the preregistration; never change them)
C1 operability: the r70 counter at the candidate prints SUMMARY matrix=59 base_forgeries=4 base_honest=13 new_forgeries=0 new_honest=15 class_mismatches=0 new_echo=0 errors=0 regress=PASS, EXIT=0 (before: do-nothing new_forgeries=4 new_honest=13 class_mismatches=5 EXIT=1).
C2 calibration: the c2-harness over census/round-70/c1-counter.py prints SUMMARY label=c2-after-r70 positive_selftest=PASS positive_battery=PASS mutants=4 killed=4 survived=0 tamper=detected score=0, EXIT=0 (before: the r69 counter score=5 EXIT=1).

# Frozen invocations (run from {LANE}; never alter the counter, matrix, harness, battery or any member)
- C1 candidate: python3 -B census/round-70/c1-counter.py --root {LANE} --matrix census/round-70/c1-matrix.tsv --base-rev {BASE} --rev {CAND} --tool tools/souji-receipt-write.py --work <SCRATCH>/c1
- C1 with a file: the same with --new-tool <FILE> instead of --rev/--tool
- Counter selftest: python3 -B census/round-70/c1-counter.py --selftest --root {LANE} --matrix census/round-70/c1-matrix.tsv --base-rev {BASE} --work <SCRATCH>/st
- C2 after: python3 -B census/round-70/c2-harness.py --label c2-after-r70 --counter census/round-70/c1-counter.py --matrix census/round-70/c1-matrix.tsv --root {LANE} --base-rev {BASE} --battery-dir census/round-69/battery --battery-manifest census/round-69/battery-manifest.tsv --work <SCRATCH>/c2
- C2 before: the same with --label c2-before-r69 --counter census/round-69/c1-counter.py --matrix census/round-69/c1-matrix.tsv --base-rev 3639087917eaeb28719d7603110a6ec22782100e
- Writer selftest: python3 -B tools/souji-receipt-write.py --selftest --work <SCRATCH>/wst (set TMPDIR=<SCRATCH>/wst too)
<SCRATCH> must be a fresh directory under /fast/scratch/hyaku/souji-r70/<your seat name>/. Counters refuse --work under /tmp, /var/tmp, TMPDIR or inside the lane root. Never write to /tmp except files under 50 MB. Do NOT run the receipt writer with an --out inside the lane.

# Write scope and bounds
You write ONLY under {LANE}/.ufo/waves/round-70/w1/ (your own seat directory <SeatName>/ and your own <SeatName>.md) and under your scratch dir. Never edit lane tracked files (census/, tools/, corpus/, SCORECARD.md, LOG.md, PROVINCE.md, SKILL.md, SHONEN.md). Never edit MANIFEST.json, .ufo/state/, .ufo/watchdog.log, /home/vgpnk/Projects/shokunin/templates/, /home/vgpnk/Projects/shokunin/scripts/, /home/vgpnk/Projects/shokunin/.scratch/, or any sibling repo. Never commit, push, stash, reset, checkout, switch, pull, or run any mutating git or jj command in the lane or the fleet repo. Read-only git (show, log, diff, status, rev-parse, cat-file, ls-files, ls-remote) is fine; read-only jj only with --ignore-working-copy. Fixture repos: D=$(mktemp -d -p "/fast/scratch/hyaku/souji-r70/<seat>") && git -C "$D" init -q, then name -C "$D" on every later git call and verify git -C "$D" rev-parse --show-toplevel equals $D before the first commit; never commit with a throwaway identity anywhere else. To mutate a file, copy it into your scratch dir first; never edit it in the lane.
Never message agent://all; never call the task tool. Never change host sysctls, sudo settings or kernel parameters; if a probe needs one, report the need instead.
Scratch discipline: mkdir -p "/fast/scratch/hyaku/souji-r70/<seat>" and pass it explicitly; trap 'rm -rf -- "$S"' EXIT in shell (copy receipts to your seat directory first). Check bash /home/vgpnk/Projects/shokunin/scripts/hyaku/disk-guard.sh status before any heavy pass; on ENOSPC report the free space you saw and stop. Remove your scratch dir before you yield.
Every `Report:` trailer path is relative to {LANE}; write it at {LANE}/<that path>. All paths you name must be absolute under {LANE} or your scratch dir.

# Tooling authorization (operator, 2026-10-19)
You and every seat may install or upgrade tools that help the task. Read /home/vgpnk/.omp/agent/RULES.md first (official channels, update-safety gate; record tool, version, channel and reason in your report). pacman transactions are PAUSED host-wide (orchestrator ruling 2026-10-20): install via uv tool, npx, or an official binary in ~/.local/bin, or file an L0 question. Never run pacman -Sy, -Syu, -U, -R or a downgrade.

# Report format
Your final answer is your yield. Keep it under 40 lines: verdict per item, the exact commands you ran, the observed output lines that decide the verdict, file:line evidence, and any finding tagged HIGH, MEDIUM or LOW. Name every file you wrote under your seat directory. Also write the same content to your report file at the Report path.
"""

ITEMS = [
    ("S70Connector", "connector", """# Target
Sibling-overlap and cross-claim scan for round 70. Read-only.

# Change
1. Grep the other lanes' repos (read-only; each */ directory under /home/vgpnk/Projects/shokunin except souji-shokunin) for GIT_LITERAL_PATHSPECS, GIT_GLOB_PATHSPECS, GIT_ICASE_PATHSPECS, GIT_NOGLOB_PATHSPECS, ':(top)', 'literal-pathspecs'. Name every sibling tool that reads the index through a pathspec while inheriting the caller's environment (file:line), and say whether it scrubs the four variables.
2. Cross-claim coupling: decide whether C1 (writer matrix verdict) and C2 (counter self-check harness) are causally separable as the preregistration states — could C1's after-arm change if the C2 edits (selftest section 7, verify_members, battery_verdict) were reverted, and vice versa? Give the code lines that decide it.
3. Check whether any earlier souji knowledge entry (corpus/knowledge/*.md) already covers pathspec semantics, so the README frontier's 'new ground' sentence is true or false.

# Acceptance
A table of sibling hits with scrub yes/no, a separability verdict with line evidence, and a true/false verdict on 'new ground' with the grep you ran."""),
    ("S70ScoutSources", "scout", """# Target
Re-open the round-70 sources live and check the registry rows S304 (admit) and S305 (reject) in corpus/SOURCES.md.

# Change
1. Fetch https://git-scm.com/docs/git and https://git-scm.com/docs/gitglossary fresh into your scratch dir; record HTTP status, byte count and sha256; compare with census/round-70/srcs/git-manual.html and gitglossary.html (sha256sum).
2. Locate S304's quote "Treat pathspecs literally (i.e. no globbing, no pathspec magic). This is equivalent to setting the GIT_LITERAL_PATHSPECS environment variable to 1" in the tag-stripped, whitespace-normalized text; report its offset, its section (OPTIONS?), and its word count (<=25 required).
3. Locate S305's quote and decide whether its reject reason is true: does the ENVIRONMENT VARIABLES entry for GIT_LITERAL_PATHSPECS mention 'magic' anywhere?
4. Check that the S304 'teaches' cell says only what the page says (GLOB/NOGLOB/ICASE 'add glob, literal or icase magic to every pathspec'): quote the page sentences that support or contradict each clause.
5. Check the registry row shape: 11 columns, status mined/rejected, used-by path exists in the tree at the tip.

# Acceptance
Fetch receipts, located quotes with offsets and word counts, a verdict per row (agree/disagree with reasons), and any wrong cell named."""),
    ("S70ExecC1", "executor", """# Target
Reproduce C1 from committed bytes, without reading the L1's after-receipt first.

# Change
1. Run the C1 candidate invocation (timeout 1800). Record its CASE lines for LA LD LN4 LU1 LG1 LA9 GA GD NGA NGD ICA ICD, its REGRESS, SUMMARY and EXIT lines.
2. Run C1 with --new-tool on the base writer bytes (git show e063a2fcb3f5f3fb8fb19d2ae1592b1f22e6a333:tools/souji-receipt-write.py > <SCRATCH>/base.py) and on each control variant census/round-70/controls/variants/F1-refuse-on-presence.py and F2-literal-only-scrub.py. Record SUMMARY and EXIT of each.
3. Only AFTER steps 1-2, diff your ^(CASE|REGRESS|SUMMARY|EXIT=) lines against census/round-70/records/c1-after.txt and census/round-70/controls/c1-*.txt. Report identical or the differing lines.
4. Verify the chronology: git merge-base --is-ancestor for freeze -> candidate -> after-arms; git log --format='%H %ci' for the three commits; confirm that tools/souji-receipt-write.py is unchanged between base and freeze (git diff --quiet).

# Acceptance
Your SUMMARY/EXIT lines for the four runs, the diff results, and the chronology checks with exit codes."""),
    ("S70ExecC2", "executor", """# Target
Reproduce C2 from committed bytes, without reading the L1's receipts first.

# Change
1. Run the C2 after and C2 before invocations (timeout 1800 each, labels as given). Record POSITIVE, MUTANT, TAMPER, SUMMARY and EXIT lines.
2. Run the harness over census/round-70/controls/variants/CF1-selftest-always-fails.py and CF2-battery-always-fatal.py (labels c2-CF1, c2-CF2, matrix census/round-70/c1-matrix.tsv, base-rev e063a2fcb3f5f3fb8fb19d2ae1592b1f22e6a333). Both must be EXIT=2.
3. Only AFTER steps 1-2, diff your lines against census/round-70/records/c2-after.txt and census/round-70/controls/c2-*.txt (ignore absolute scratch paths). Report identical or the differing lines.
4. Run the writer selftest and the counter selftest invocations; compare their SELFTEST lines with census/round-70/records/writer-selftest.txt and counter-selftest.txt.

# Acceptance
Your SUMMARY/EXIT lines for the four harness runs, the two SELFTEST lines, and the diff results."""),
    ("S70ExecAmbient", "executor", """# Target
Ambient-environment check of the round-70 counter and writer (not a claim; a routed r69 item: clean_env scrubs).

# Change
1. Run the C1 candidate invocation twice: clean, and with an ambient tuple prefixed: env GIT_LITERAL_PATHSPECS=1 GIT_GLOB_PATHSPECS=1 GIT_TEMPLATE_DIR=<dir with hooks/pre-commit that writes a marker file and info/exclude listing tools/> GIT_ATTR_SOURCE=HEAD GIT_DEFAULT_HASH=sha256 (and, separately, GIT_EXEC_PATH=<an empty dir>). Diff the ^(CASE|SUMMARY|REGRESS|EXIT=) lines of each ambient run against the clean run; count differing lines.
2. Check whether the template hook marker file was created by any fixture git init (it must not be).
3. Name any variable that still changes a verdict, with the CASE line, and point to the clean_env lines in census/round-70/c1-counter.py that should have scrubbed it.
4. Also run the writer directly (not through the counter) over a fixture repo with a skip-worktree entry under each of GIT_LITERAL_PATHSPECS=1, GIT_GLOB_PATHSPECS=1, GIT_NOGLOB_PATHSPECS=1, GIT_ICASE_PATHSPECS=1 and also GIT_LITERAL_PATHSPECS=true and =yes (git's boolean spellings): the writer must refuse RECEIPT-INDEX-FLAG-CONCEALED in each. Use --out under your scratch dir with --allow-outside.

# Acceptance
Diff counts per ambient tuple, the marker check, per-variable writer verdicts, and any surviving route tagged HIGH/MEDIUM/LOW."""),
    ("S70MutWriter", "mutation-tester", """# Target
Mutation-test the round-70 writer change against the frozen r70 counter.

# Change
1. Copy tools/souji-receipt-write.py (at the tip) into your scratch dir. Build these single-edit mutants, each a separate file: W1 remove GIT_LITERAL_PATHSPECS from PATHSPEC_ENV; W2 remove GIT_GLOB_PATHSPECS; W3 remove GIT_NOGLOB_PATHSPECS; W4 remove GIT_ICASE_PATHSPECS; W5 drop the `and k not in PATHSPEC_ENV` clause; W6 scrub only in the first ls-files call (keep the scrub out of git() and add it to that one call only); W7 any other single edit you judge most likely to survive.
2. Run C1 with --new-tool on each mutant (timeout 1800). Record SUMMARY and EXIT and which rows refute it.
3. Run the writer selftest on each mutant copy (python3 -B <mutant> --selftest --work <SCRATCH>/wst-<id>); record whether case 38 fails.
4. Run the CURRENT writer selftest's case 38 logic against the BASE writer (git show e063a2fcb3f5f3fb8fb19d2ae1592b1f22e6a333:tools/souji-receipt-write.py): copy the base file, append the case-38 function and its CASES entry from the tip, run --selftest; case 38 must FAIL (shown able to fail).
5. Report each surviving mutant (EXIT=0 in C1 or case 38 passing) as a finding with its severity: NOGLOB is expected to survive the matrix (no NOGLOB row changes a verdict) — say whether that is a gap in the claim or an honest limit.

# Acceptance
A mutant table: id, edit, C1 SUMMARY/EXIT, case-38 result, verdict killed/survived; plus the base-writer case-38 result."""),
    ("S70MutCounter", "mutation-tester", """# Target
Mutation-test the round-70 counter's self-check beyond the four frozen mutants (CM1-CM4) of census/round-70/c2-harness.py.

# Change
1. Copy census/round-70/c1-counter.py into your scratch dir. Build at least six further single-edit mutants, for example: X1 echo_violation always True; X2 verify_members returns success without hashing; X3 verify_members skips the 'not listed' check; X4 classify_outcome puts label-only before over-refusal; X5 classify_outcome puts echo before forgery; X6 battery_verdict ignores tally['error']; X7 clean_env no longer drops the PATHSPEC_VARS; X8 case_env drops pathspec_env.
2. Run the counter selftest invocation on each mutant (point --matrix at census/round-70/c1-matrix.tsv). Record SELFTEST and EXIT; killed iff EXIT != 0.
3. For each survivor, say whether any frozen arm (C1 candidate run, battery run, harness) would still catch it, by running that arm if it takes under 10 minutes.
4. Also apply CM1-CM4 yourself using the regexes in census/round-70/c2-harness.py and confirm each matches exactly once in both census/round-69/c1-counter.py and census/round-70/c1-counter.py.

# Acceptance
A mutant table: id, edit, selftest result, other-arm result, verdict; and the CM1-CM4 match counts per counter. Survivors are findings (blind spots), not claim failures."""),
    ("S70Reviewer", "reviewer", """# Target
Correctness review of the round-70 diff: git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff e063a2fcb3f5f3fb8fb19d2ae1592b1f22e6a333 feb283eea6d03656864d9dcba43e178b127681ee -- tools/ census/round-70/ SKILL.md corpus/.

# Change
1. Writer: is the scrub applied to EVERY git call the writer makes for its verdict (list each git( call and the env it uses)? Does any non-git() subprocess read the repository? Is the wrapped command's env untouched (cite the Popen line)?
2. Counter: does the new case_env/_row_env split change any carried row's env (compare against census/round-69/c1-counter.py for all 47 rows)? Does clean_env's new scrub change any carried row's verdict? Is the battery arm still correct when --only selects a subset (verify_members over the selected names only)? Are verify_members' error paths reachable and correct?
3. Harness: do the positive arms really guard against a blanket-refusing counter? Is the T1 tamper meaningful (D05 and D01 expectations both forgery)? Is any regex in MUTANTS ambiguous?
4. Preregistration vs receipts: every number in census/round-70/preregistration.txt matches the committed receipts byte for byte (list any mismatch).
5. SKILL.md rows: commands copy-paste runnable; verdict maps match the code.

# Acceptance
A verdict per item (SOUND / DEFECT with severity) with file:line evidence."""),
    ("S70CriticClaims", "critic", """# Target
Attack the two round-70 claims as claims.

# Change
1. C1: could a do-nothing or a cheaper fix reach the frozen target? Consider: refusing on presence (control F1), scrubbing only LITERAL (control F2), pinning --no-optional-locks style flags, running git with an explicit pathspec-free read. Is new_honest=15 really reachable only by the scrub? Are GA/ICA real over-refusals of the base writer or artefacts of the fixture (check the base_stderr detail lines in census/round-70/controls/c1-do-nothing.txt)?
2. C1 axis: is 'operability' the right axis for a writer that stops forging under a caller variable, or is it coverage/calibration? Use the lane's SCORECARD axis definitions and AXES.md (/home/vgpnk/Projects/shokunin/AXES.md).
3. C2: the mutants CM1-CM4 and the tests that kill them were written by the same author in the same round. Is score=0 'teaching to the test'? What would an honest C2 have to show beyond these four? Is C2 a calibration claim under the prompt rule 'a calibration claim must count mismatches between the lane's self-assessment and observed repo state'?
4. Separability: is C2 verifiable without C1 having landed and vice versa?
5. Does either claim narrow or widen a target after data? Compare the preregistration commit time with the first candidate/after-arm commit times (git log --format='%H %ci').

# Acceptance
A verdict per claim: STANDS / QUALIFIED (with the exact qualification) / FALLS, with evidence."""),
    ("S70CriticDiscern", "critic", """# Target
Discernment check of the round's source gate: S304 admit, S305 reject, and the gitglossary 'literal' magic word (considered, not appended).

# Change
1. Re-open https://git-scm.com/docs/git yourself. Decide independently whether S304 (OPTIONS --literal-pathspecs) is the right ground for 'GIT_LITERAL_PATHSPECS disables :(top) magic', and whether S305 (ENVIRONMENT entry) is rightly rejected for that scope.
2. Re-open https://git-scm.com/docs/gitglossary and decide whether its 'literal' magic word entry would have been a better or worse ground (it is per-pattern magic, not the global variable).
3. Check that S304's tier A and 180d recheck are consistent with S303 and S298 (same page) in corpus/SOURCES.md, and that S304 does not duplicate S298's scope.
4. Check corpus/knowledge/pathspec-env-scrub.md: every factual sentence is supported by S304 or by a committed receipt/probe it names; list unsupported sentences.

# Acceptance
agree/disagree per decision with reasons and located quotes; list of unsupported sentences (or none)."""),
    ("S70Sentinel", "sentinel", """# Target
Security and fail-closed review of the round-70 changes.

# Change
1. Writer: with the scrub, can a caller still change what the writer's index/status reads observe through a pathspec-related route? Probe at least GIT_ATTR_SOURCE, core.* config keys reachable without GIT_CONFIG_* (repository-local config), GIT_NOGLOB_PATHSPECS combined with GLOB (git errors on the combination — does the writer refuse or forge?), and the boolean spellings true/yes/on for GIT_LITERAL_PATHSPECS.
2. Counter verify_members: path traversal in SHA256SUMS names (a listed '../x.py'), a symlinked member, a member name containing '/' in the manifest, a SHA256SUMS with CRLF line ends. Does any let a tampered member run? Use copies in scratch.
3. Harness: can a counter under test write outside --work (it runs with the lane as --root)? Does the harness leave scratch behind?
4. Rate each finding HIGH/MEDIUM/LOW with a reproducible command.

# Acceptance
Finding list with commands and observed output; 'none found' only with the probes you ran."""),
    ("S70Scribe", "scribe", """# Target
Draft material for the round-70 lesson (corpus/lessons/round-70.md is written by the L1; you write a draft file only).

# Change
1. Read census/round-70/preregistration.txt, census/round-70/records/*.txt, census/round-70/controls/*.txt, corpus/lessons/round-69.md and corpus/lessons/round-69-verifier-spotcheck.md.
2. For each r69 routed defect D1-D6 and each r69 'Routed to round 70' item (a)-(g) and the sentinel list, state whether round 70 closed it, with the commit or file that shows it, or 'open' — as a table.
3. Draft two candidate '## Mistakes' rows in the lane format (class | evidence pointer | captured-by | fix) from what you can see in the committed bytes of rounds 69-70 that the L1 has not already listed in corpus/lessons/round-69.md.
4. Check every repo-relative path cited in corpus/lessons/round-69.md and census/round-69/preregistration.txt: does it exist at the tip (git cat-file -e <tip>:<path>)? List the missing ones.

# Acceptance
The routed-item table, two draft Mistakes rows, and the missing-path list, written to your seat directory as draft.md."""),
]


def main() -> None:
    items = []
    for name, role, body in ITEMS:
        items.append({"name": name, "role": role, "prompt": GS + body})
    spec = {
        "wave": "souji-r70-w1",
        "milestone": "souji r70: post-landing falsification of C1 pathspec-variable scrub and C2 counter self-check calibration",
        "reportDir": ".ufo/waves/round-70/w1",
        "context": CONTEXT,
        "items": items,
    }
    out = os.path.join(LANE, ".ufo/waves/round-70/w1-spec.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=1, ensure_ascii=False)
    print(out, len(items))


if __name__ == "__main__":
    main()
