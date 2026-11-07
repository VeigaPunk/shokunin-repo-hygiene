# ScoutScorecardState — round 27 (w1) scorecard precondition verification

## Status
STATUS: PARTIAL — four of five preconditions hold at base e78ac7c; (d) does NOT:
`## Planned` names no round after r25 (no r26/r27/r28 bullet exists anywhere in the
committed file), so the r28 planned bullet must be created by this round's landing
(marked below). Two adjacent findings also reported: (i) the frozen r27 preregistration
MACHINE BLOCK is not parseable by tools/souji-axis-check.py (rc=2); (ii) the wave's
own c1-before.tsv receipt mislabels a git blob SHA-1 as `gate_sha256`.

## Evidence
Base revision: e78ac7c4837b81b634db4a927605a751a7f006ba; `git rev-parse HEAD` ==
`git rev-parse master` == `git rev-parse origin/master`; `git ls-remote origin refs/heads/master`
→ e78ac7c… (rc 0); `git rev-list --left-right --count origin/master...master` → `0 0`
(ahead=0). Head check: `git symbolic-ref -q HEAD` fails (detached), master==origin/master.

(a) registry rows = 132
```
grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md   # → 132
git show e78ac7c:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'  # → 132 (committed blob)
```
Census malformed / duplicate / enum pre-checks at base are clean: NF!=13 → 0;
`sort | uniq -d` → empty; tiers A=…/B=…/C=…, status mined=108 queued=15 rejected=9.
Also `census/round-26/records/c2-after.tsv` stdout: `registry_rows=132` at rev e0f8dcd.

(b) grounded F4 = 2
```
grep -rlE '^ground: F4' corpus/knowledge/ | wc -l   # → 2
```
Files: `corpus/knowledge/quarantine-staging-no-copy-r23.md`,
`corpus/knowledge/quarantine-origin-record-fields-r24.md` (same two in committed tree at
e78ac7c). Ground line quote (quarantine-origin-record-fields-r24.md:8):
"ground: F4 — restorable quarantine (the read side of a per-item origin record)".

(c) latest measurements block is Round 26; counted commits exist and are ancestors of master
Latest measurements block in file: `### Round 26 measurements` at SCORECARD.md:264 (EOF
region, after `### Round 26 append-only corrections` at :239 and `## Retired` at :233).
Measured-commit column cells: `07f83e6`, `9a6e0f1`, `0c92c2e` (SCORECARD.md:268-270).
```
git merge-base --is-ancestor 07f83e6 master && echo yes     # yes
git merge-base --is-ancestor 9a6e0f1 master && echo yes     # yes
git merge-base --is-ancestor 0c92c2e master && echo yes     # yes
git rev-parse 07f83e6 9a6e0f1 0c92c2e     # all resolve
```
Round 26 block header quote (SCORECARD.md:264): "### Round 26 measurements (2026-10-25;
lane base 89e0fceeefcf28db313c94120be6d25e03c60094)". Counted lane base 89e0fcee also
exists and is an ancestor. Note: the Round 26 block sits at EOF, below `## Retired`,
not in the newest-first top position (Round 25 at :17, Round 24 at :44, Round 23 at :78);
appending a Round 27 measurements block "above `### Round 26 measurements`" keeps the
r26 C1 heading triple `17 44 78` intact (verified by scratch insertion: top-insert shifts to
21 48 82, EOF-insert keeps 17 44 78).

(d) `## Planned` names the next round (r28) — NOT satisfied at base
`## Planned` spans SCORECARD.md:158–203. Largest round named in any planned bullet: r25.
Last bullet (line 202) quote: "- **r25 (planned r24):** (a) calibration: make C2's per-entry kill rule".
```
awk '/^## Planned/,/^## Saturation/' SCORECARD.md | grep -c 'r28'   # → 0
awk '/^## Planned/,/^## Saturation/' SCORECARD.md | grep -c 'r27'   # → 0
awk '/^## Planned/,/^## Saturation/' SCORECARD.md | grep -c 'r26'   # → 0
python3 -B -c "…(planned section)…r26/r27/r28 mentions"            # all 0
```
Round-26's wave drafted an `### Round 26 planned-roll` EOF block containing an "r27 — planned"
bullet (.ufo/waves/round-26/w1/scorecard-r26.md:57,70) — it never landed: commit 166baa1's
SCORECARD diff adds only the Round 26 measurements block (11 added lines), and
`grep -c "Round 26 planned-roll"` = 0 at every revision 728b2ce..e78ac7c.
The L1's ExecScorecardDraft already drafts `- **r28 (planned r27):**` at
.ufo/waves/round-27/w1/scorecard-draft.md:24 to satisfy (d) at the tip.

(e) axis scores row shows calibration 7 / operability 8 / coverage 8
`## Axes` rows parsed by the lane tool (parse_scores): coverage=8, calibration=7,
operability=8 (SCORECARD.md:13–15). Saturation prose (line 207) agrees:
"rows above: coverage 8, operability 8, calibration 7".

C1 before-counter re-run (read-only) at base:
```
python3 -B tools/souji-landing-gate.py --root … --rev e78ac7c… --round 27 --fleet-root …
```
→ `LG-DANGLING-PTR corpus/knowledge/registry corpus/QUALITY.md:143 …` +
`LG-DANGLING-PTR corpus/lessons/round-24.md:232:S118 corpus/QUALITY.md:141 …`;
`SUMMARY findings=2 checked_reg=50 …` (rc=2 driven by `COULD-NOT-EVALUATE no .md reports
under .ufo/waves/round-27/` at base — expected before round reports land).

## Findings
1. **Precondition (d) fails at base.** `## Planned` names no round after r25; r26, r27
   and r28 tokens have 0 occurrences in the section, and the r26 wave's drafted
   `### Round 26 planned-roll` block (with its "r27 — planned" bullet) never landed
   (166baa1 diff adds only the measurements block). The r28 planned bullet is a round-27
   deliverable (draft exists at .ufo/waves/round-27/w1/scorecard-draft.md:24) — L1 must
   land it inside `## Planned`.
2. **Frozen r27 preregistration MACHINE BLOCK is not machine-parseable** by
   `tools/souji-axis-check.py`: the marker line is `MACHINE BLOCK` (no `## ` prefix,
   preregistration.txt:11) and there is no `END` terminator; CLAIM lines use single-line
   `axis=… surface-class=… enumerate=…` form, not the parser's `axis:`-style line form.
   Verbatim run: `python3 -B tools/souji-axis-check.py --prereg .ufo/waves/round-27/preregistration.txt --scorecard SCORECARD.md` → rc=2, "no `## MACHINE BLOCK ... END` section found". r26's prereg parses fine (claims=3 flags=0). Same claim content re-expressed in the expected form → claims=3 flags=0 (scratch). This blocks the ScribePrereg expectancy `claims=3 flags=0` on the frozen file.
3. **Wave receipt digest mislabel:** `.ufo/waves/round-27/records/c1-before.tsv:2` puts
   `e67810d1…` under column `gate_sha256`; that value is the **git blob SHA-1** of
   `tools/souji-landing-gate.py` (`git hash-object` → e67810d1…), while the file's sha256
   is `02b58f81…`. The committed blob id at e78ac7c is e67810d1… (blob exists). Field
   content/name mismatch — receipt-run convention expects `tool_sha256=<64 hex>`.
4. **C2 registry id-space note:** lane ids are contiguous S001–S132 (max S132). Staged
   `SOURCES.append.md` (shokuknow) carries 134 rows S109–S242; its S109–S132 (24 ids)
   collide with existing lane rows, whereas the prereg's three admission ids S152/S210/S211
   do not exist in the lane (no collision within the admitted set; gaps S133–S151 etc.
   remain). Staged S152/S210/S211 rows as raw bytes are malformed for the lane census
   (NF=15/14/16 due to escaped `\|` inside cells → E01 under both the lane's and the
   fleet's awk -F'|' parsers); `ExecRowsNormalize` (round-27 seat) reports normalizing them
   to NF=13. Appended rows must be NF=13 for the C2 `sources-census` rc 0 counter.
5. **Worktree not clean at base:** 11 tracked files under `.ufo/waves/round-26/w1/`
   carry uncommitted modifications (mtimes 14:38–14:41 today, i.e. after commit 166baa1),
   plus 30 untracked paths (26 in round-26/w1; `.ufo/waves/round-27/`; `census/operator-sweep-20261019/`;
   `tools/__pycache__/`, `tests/fixtures/__pycache__/`). The two `__pycache__` dirs are
   lane-authored leftovers from python runs without `-B` (created 14:25–14:37 today).
   Relevant to C3's "no uncommitted lane-authored leftovers" pre-report-gate check.

## Attack log
Not an attack item (scout/verification seat). Findings 2/3 are record-vs-bytes facts for
the L1 to adjudicate; no counter/predicate change proposed. Preregistration remains frozen.
