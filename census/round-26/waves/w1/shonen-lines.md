# Round 26 — paste-ready SHONEN section

Box order follows `SHONEN.md` byte order at the lane tip (`0c92c2e`, re-verified unchanged at `166baa1`), one line per box, all `[~]`
(promotion is operator-owned; the lane writes no `[x]`). `ScoutShonen` never landed
(`w1/swarm-registry.json`: `"agentId": null`), so every pointer below was resolved by this seat
against the tip bytes named in `ExecShonenFile.md` §Evidence.

## SHONEN

[~] SKILL.md contains real decision tables, error patterns, checklists and cited sources — `SKILL.md:42` Decision tables, `SKILL.md:78` Error patterns (false-SAFE signatures), `SKILL.md:147` Checklists, `SKILL.md:167` Gate registry; `corpus/SOURCES.md:121-124` (S100-S103) plus this round's `corpus/SOURCES.md:149-153` (S128-S132); `corpus/lessons/round-21.md:25` Gate. No non-author verifier checked this round.
[~] At least one end-to-end domain task executed and logged in LOG.md — `LOG.md` heading "## 2026-10-19 — operator sweep (execution): root-wide receipts + home-wide cache/tmp cleanup" at `LOG.md:362` (96 pushed-receipt artifacts quarantined, second-checked, removed), corroborated by the Round 25 execution block at `LOG.md:1723`.
[~] Instructions executable by an agent without oral context — `census/round-21/run-acceptance.py` with `census/round-21/accepted-matrix.json` (scenarios=3, replayed=3, `matched_command_count`=18 per scenario) and `census/round-21/remote-source-after.json` (`all_matched: true`); this round adds `census/round-26/c1-counter.sh`, `census/round-26/c2-counter.sh`, `census/round-26/c3-counter.sh`, `tools/souji-axis-check.py` and `tests/fixtures/r26-axis-check.py`, bound by receipts `census/round-26/records/c1-after.tsv` (`markers=0`), `c2-after.tsv` (`registry_rows=132`), `c3-after.tsv` (`cases=12 pass=12 control=FALSE-GREEN-REJECTED`).
[~] No cross-domain bleed (PROVINCE.md still accurate) — `PROVINCE.md:161` "### Round21 privacy boundary"; `.ufo/waves/round-21/w1/ConnSiblingOverlap.md`; `corpus/lessons/round-21.md:38` "### Boundaries and teaching"; this round's re-scan `.ufo/waves/round-26/w1/ConnSiblings.md` §1-3 (21 rostered lanes, zero collision, all routed).

## L1 `--check` assertion list (run from the lane root, before filing)

`R` is the filed report path, passed as `R=<path>`; the lane copy is
`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/reports/round-26/souji.md` and the fleet copy is
`/home/vgpnk/Projects/shokunin/.ufo/reports/round-26/souji.md` — run against the byte-identical
file the L1 actually files. Expected value on the right of `->`.

### Shape (the frozen contract)

| # | command | expected |
|---|---|---|
| A1 | `grep -c '^## SHONEN' "$R"` | `-> 1` |
| A2 | `awk '/^## SHONEN/{f=1;next} /^## /{f=0} f' "$R" \| grep -cE '^\[~\]'` | `-> 4` |
| A3 | `awk '/^## SHONEN/{f=1;next} /^## /{f=0} f' "$R" \| grep -cE '^\[ \]\|^\[x\]'` | `-> 0` |
| A4 | `grep -c '^- \[~\]' SHONEN.md` — box count in the source checklist equals the report's line count | `-> 4` |
| A5 | `grep -cE '^- \[[ x]\]' SHONEN.md` — source checklist untouched | `-> 0` |
| A6 | `awk '/^## SHONEN/{f=1;print;next} /^## /{f=0} f' "$R" \| head -1` | `-> ## SHONEN` (exactly one, correct spelling/case) |

A2 assumes the paste starts each line at column 0 with `[~]` (round-25 filing form). If the L1
pastes the round-24 bullet form (`- [~]`) instead, use
`grep -cE '^([-*] )?\[~\]'` and keep the same expected `4`; do not mix the two forms.

### Pointer resolution (each pointer in the four lines)

| # | command | expected |
|---|---|---|
| B1 | `sed -n '42p;78p;147p;167p' SKILL.md \| grep -cE '^## (Decision tables\|Error patterns \(false-SAFE signatures\)\|Checklists\|Gate registry)'` | `-> 4` |
| B2 | `sed -n '121,124p' corpus/SOURCES.md \| grep -cE '^\| *S10[0-3] '` | `-> 4` |
| B3 | `sed -n '149,153p' corpus/SOURCES.md \| grep -cE '^\| *S1(28\|29\|30\|31\|32) '` | `-> 5` |
| B4 | `sed -n '25p' corpus/lessons/round-21.md \| grep -c '^## Gate'` | `-> 1` |
| B5 | `sed -n '38p' corpus/lessons/round-21.md \| grep -c '^### Boundaries and teaching'` | `-> 1` |
| B6 | `sed -n '362p' LOG.md \| grep -c '^## 2026-10-19 — operator sweep (execution)'` | `-> 1` |
| B7 | `sed -n '1723p' LOG.md \| grep -c '^## 2026-10-25 — Round 25 honest stop'` | `-> 1` |
| B8 | `sed -n '161p' PROVINCE.md \| grep -c '^### Round21 privacy boundary'` | `-> 1` |
| B9 | `for f in census/round-21/run-acceptance.py census/round-21/accepted-matrix.json census/round-21/remote-source-after.json .ufo/waves/round-21/w1/ConnSiblingOverlap.md .ufo/waves/round-26/w1/ConnSiblings.md census/round-26/c1-counter.sh census/round-26/c2-counter.sh census/round-26/c3-counter.sh tools/souji-axis-check.py tests/fixtures/r26-axis-check.py census/round-26/records/c1-after.tsv census/round-26/records/c2-after.tsv census/round-26/records/c3-after.tsv; do test -f "$f" \|\| echo "MISSING $f"; done` | no output |

B1-B8 encode the anchor text *and* the current line number, so a moved heading shows up as a
failed count rather than a silent stale pointer; re-derive the number if a seat appends above it.

### Value assertions behind the pointers (receipts, not re-runs)

| # | command | expected |
|---|---|---|
| C1 | `python3 -B -c "import json;d=json.load(open('census/round-21/accepted-matrix.json'));assert d['scenarios']==3 and d['replayed']==3 and [r['matched_command_count'] for r in d['records']]==[18,18,18]"` | exit `0` |
| C2 | `python3 -B -c "import json;d=json.load(open('census/round-21/remote-source-after.json'));assert d['all_matched'] is True"` | exit `0` |
| C3 | `grep -c '^markers=0$' census/round-26/records/c1-after.tsv` | `-> 1` |
| C4 | `grep -c '^registry_rows=132$' census/round-26/records/c2-after.tsv` | `-> 1` |
| C5 | `grep -c '^cases=12 pass=12 control=FALSE-GREEN-REJECTED$' census/round-26/records/c3-after.tsv` | `-> 1` |

### Non-assertions (deliberate)

- No `[x]` is claimed or written: promotion is operator-owned, and the round-25 spotcheck's D4
  note only says the four boxes are *plausibly* non-author checkable next round. A closure that
  re-reviews them may say so in its own words; the report must not pre-empt it.
- The `## SHONEN` block is not a measurement section: it carries no unrun-check claim, so none of
  A1-A6 or B1-B9 depends on a command this seat executed.
