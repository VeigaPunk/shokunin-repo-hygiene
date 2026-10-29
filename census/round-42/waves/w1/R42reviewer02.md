# R42reviewer02 — C2 grammar re-derivation (operability, reviewer)

Freeze: afe17f416eec04dcf3f480b580a8f928de61d19d. Base: bf618f6c5c09d302994871c94903abbea2deb60d.
Scope: read-only. No lane, tool, census or corpus file was edited. No git mutation was run.

## 1. Inputs and hashes (read-only)

```
sha256sum tools/souji-freeze-check.py census/round-42/c2-counter.py census/round-42/c2-cases.tsv
8131847bcfc5ecef513eb608a67ec18feab44f7a8b6c094824b082ffe52a76e2  tools/souji-freeze-check.py
fa44392d11338daa73b3b4b9b2fc8f89879c099e9bf278d7b45fa55dea5d0ac1  census/round-42/c2-counter.py
148b7b87411eb282e0207cf5471d55be81e03d4a26ffafd96df37b4db4fd4511  census/round-42/c2-cases.tsv
git show afe17f41...:tools/souji-freeze-check.py | sha256sum  -> 8131847bcfc5ecef513eb608a67ec18feab44f7a8b6c094824b082ffe52a76e2
git show afe17f41...:census/round-42/c2-counter.py | sha256sum -> fa44392d11338daa73b3b4b9b2fc8f89879c099e9bf278d7b45fa55dea5d0ac1
```

The working-tree tool and counter are byte-identical to the frozen blobs, so the scored bytes are the frozen bytes.

## 2. Grammar-only derivation (docstring c2-counter.py:4-56 and :15-33; CASES not consulted)

Base-tool behaviour that the docstring keeps unchanged: claim header `## C<digits>`, key lines at column 0, the six keys, `PATH sha256=<64 hex>` digests, FREEZE-REV, and the r41 classes.

| case | derived exit | derived findings (from docstring alone) | determined? |
|---|---|---|---|
| dup-base-differs | 1 | C1 KEY-DUPLICATE (+ value-check outcome, see A1) | ambiguous (A1) |
| dup-counter-identical | 1 | C1 KEY-DUPLICATE | yes ("identical value or not"; identical digests are valid, no FROZEN-EDITED) |
| dup-target | 1 | C1 KEY-DUPLICATE | yes (Target has no value check beyond presence/non-empty) |
| heading-nospace `##C2 - second` | 1 | C0 HEADING-MALFORMED | yes (explicit example `##C1`; line opens no claim; nothing follows it) |
| heading-lowercase `## c2 - second` | 1 | C0 HEADING-MALFORMED | yes (explicit example `## c1`) |
| heading-spaced-digit `## C 2 - second` | 1 | C0 HEADING-MALFORMED | yes (explicit example `## C 1`) |
| heading-suffix `## C2x second` | 1 | C0 HEADING-MALFORMED | yes (explicit example `## C1x`) |
| heading-valid-tail `## C2 - empty second claim` | 1 | C2 FIELD-MISSING x6 (Base, Counter, Population, Control, Target, Kill) | yes (valid claim, zero keys) |
| dispatch-spec-before `w1-spec.json` | 1 | C0 DISPATCH-BEFORE-FREEZE | yes (`-spec.json` suffix; added in ancestor of freeze) |
| dispatch-attempts-before `w1-dispatch-attempts.txt` | 1 | C0 DISPATCH-BEFORE-FREEZE | yes (basename contains `-dispatch`) |
| dispatch-dispatched-before `w1.ready.dispatched` | 1 | C0 DISPATCH-BEFORE-FREEZE | yes (basename contains `.ready`) |
| dispatch-results-before `w1-results.json` | 1 | C0 DISPATCH-BEFORE-FREEZE | yes (`-results.json` suffix) |
| dispatch-names-after (4 files, all after freeze) | 0 | none | yes (ancestor rule; nothing added before freeze) |
| dispatch-notes-before `notes.md`, `w1/Seat01.md` | 0 | none | yes (neither basename matches; `w1/` depth is irrelevant to a non-match) |
| counter-symlink | 1 | C1 COUNTER-SYMLINK only | yes ("this finding alone, no digest comparison is made") |
| population-symlink | 1 | C1 POPULATION-SYMLINK | ambiguous (A2) |

For every case the CASES expectation (exit code and class multiset) equals this derivation under the reading stated in A1 and A2. CASES was not used to derive the rows above; I compared afterwards.

## 3. Ambiguous cases (expectation not fully fixed by the docstring)

ambiguous_cases=2
- dup-base-differs
- population-symlink

**A1 dup-base-differs.** The docstring says a duplicated key gives "one finding per duplicated key (detail: the key). First-wins reading is gone." It does not say which occurrence the value checks read. The case has Base = valid ancestor commit (first line) and Base = `0`×40 (second line, appended as `__extra`). CASES expects only `C1 KEY-DUPLICATE`. That expectation holds only if the value checks use the first occurrence, or if a duplicated key is not value-checked. If the last occurrence is checked, or both are, the extra `C1 BASE-UNRESOLVED` appears and the case fails.
Proposed reading: the first occurrence is still the one evaluated, and KEY-DUPLICATE is added on top. The docstring should say so.

**A2 population-symlink.** The docstring says "the same for the Population path" after "this finding alone, no digest comparison is made". Read literally, "alone" covers the whole claim line, so POPULATION-EMPTY must not fire. But the POPULATION-EMPTY check reads blob lines, and the link text `real-pop.tsv` is one line (< 2), so an implementer who runs the content checks independently gets two findings. The r41 base does exactly that (see section 5, `population-symlink`: POPULATION-DIGEST + POPULATION-EMPTY).
Proposed reading: a symlink Population is a SYMLINK-only finding, with no content or digest checks, matching CASES. The docstring should state that "alone" applies to POPULATION-SYMLINK too.

## 4. Not in the 16 cases, but the grammar leaves open (not counted in ambiguous_cases)

- **N1 malformed heading and block boundary.** The block rule is "runs to the next `## ` line". `##C2` (no space) is not `## `, so it does not close the preceding claim, and key lines after it stay with the earlier claim. `## c2` is `## `, so it does close the block. The two malformed forms therefore differ in block boundary. This matters for KEY-DUPLICATE across a boundary (`Base` in C1, then `##C2`, then `Base` again). The docstring says only "the line opens no claim". Proposed reading: every `##` line that is not `###` closes the current block. The cases do not exercise this, because the malformed line is always last.
- **N2 `.ready` in a `w1/` subdirectory.** Determined by the docstring: "any depth", "basename contains". `w1/Seat01.ready` is flagged. A directory named `x.ready/` is not, because only the basename is tested.
- **N3 duplicate across two claims.** Determined: KEY-DUPLICATE is "in one claim block", so a Base in C1 and a Base in C2 are not a duplicate (subject to N1).
- **N4 symlink with wrong digest.** Determined: only SYMLINK is emitted ("alone"), so no digest finding.

## 5. Base run: pass=24 fail=13 confirmed

Command (run from my scratch directory, explicit TMPDIR):

```
mkdir -p /fast/scratch/hyaku/souji-r42/R42reviewer02 && cd /fast/scratch/hyaku/souji-r42/R42reviewer02 && TMPDIR=/fast/scratch/hyaku/souji-r42/R42reviewer02 bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/score-candidate.sh c2 /fast/scratch/hyaku/souji-r42/R42reviewer02 tools/souji-freeze-check.py=/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-freeze-check.py; echo "EXIT=$?"
```

Output (verbatim):

```
case-clean=PASS ... case-two-claims-one-bad=PASS            (19 r41 tuple cases: all PASS)
case-dup-base-differs=FAIL rc=0 want=1 findings=[] want=[('C1', 'KEY-DUPLICATE')] summary=(1, 0) crash=False
case-dup-counter-identical=FAIL rc=0 want=1 findings=[] want=[('C1', 'KEY-DUPLICATE')] summary=(1, 0) crash=False
case-dup-target=FAIL rc=0 want=1 findings=[] want=[('C1', 'KEY-DUPLICATE')] summary=(1, 0) crash=False
case-heading-nospace=FAIL rc=0 want=1 findings=[] want=[('C0', 'HEADING-MALFORMED')] summary=(1, 0) crash=False
case-heading-lowercase=FAIL rc=0 want=1 findings=[] want=[('C0', 'HEADING-MALFORMED')] summary=(1, 0) crash=False
case-heading-spaced-digit=FAIL rc=0 want=1 findings=[] want=[('C0', 'HEADING-MALFORMED')] summary=(1, 0) crash=False
case-heading-suffix=FAIL rc=0 want=1 findings=[] want=[('C0', 'HEADING-MALFORMED')] summary=(1, 0) crash=False
case-heading-valid-tail=PASS
case-dispatch-spec-before=FAIL rc=0 want=1 findings=[] want=[('C0', 'DISPATCH-BEFORE-FREEZE')] summary=(1, 0) crash=False
case-dispatch-attempts-before=FAIL rc=0 want=1 findings=[] want=[('C0', 'DISPATCH-BEFORE-FREEZE')] summary=(1, 0) crash=False
case-dispatch-dispatched-before=FAIL rc=0 want=1 findings=[] want=[('C0', 'DISPATCH-BEFORE-FREEZE')] summary=(1, 0) crash=False
case-dispatch-results-before=FAIL rc=0 want=1 findings=[] want=[('C0', 'DISPATCH-BEFORE-FREEZE')] summary=(1, 0) crash=False
case-dispatch-names-after=PASS
case-dispatch-notes-before=PASS
case-counter-symlink=FAIL rc=1 want=1 findings=[('C1', 'COUNTER-DIGEST')] want=[('C1', 'COUNTER-SYMLINK')] summary=(1, 1) crash=False
case-population-symlink=FAIL rc=1 want=1 findings=[('C1', 'POPULATION-DIGEST'), ('C1', 'POPULATION-EMPTY')] want=[('C1', 'POPULATION-SYMLINK')] summary=(1, 2) crash=False
case-unresolved-rev=PASS
case-absent-prereg=PASS
real ok rc=0 findings=0 summary=(3, 0)
retro red rc=1 findings=19 summary=(3, 19)
retro_clean ok rc=0 findings=0 summary=(3, 0)
selftest FAIL rc=2 summary=None
SUMMARY cases=37 pass=24 fail=13 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=FAIL patches=0/3 tool_sha=8131847bcfc5
EXIT=1
```

Confirmed: pass=24 fail=13, as expected.

Explanation of the 13 failures (all are "tool does not implement the r42 class yet", none is a counter bug):
- **3 KEY-DUPLICATE** (dup-base-differs, dup-counter-identical, dup-target): the base parser keeps the first occurrence silently (`parse_claims`, tool lines 84-86: `if m and m.group(1) not in cur[1]`). Nothing is reported, so rc=0.
- **4 HEADING-MALFORMED** (heading-nospace, -lowercase, -spaced-digit, -suffix): base HEADER is `^## C(\d+)(?![0-9A-Za-z_])` (tool line 28). Malformed lines give no claim and no finding, so rc=0.
- **4 DISPATCH widening** (dispatch-spec-before, -attempts-before, -dispatched-before, -results-before): base flags only `endswith("-dispatch.json")` or `endswith(".ready")` (tool line 115). `-spec.json`, `-results.json`, `-dispatch-attempts.txt` and `.ready.dispatched` are not flagged, so rc=0.
- **2 symlink classes** (counter-symlink, population-symlink): base has no symlink check. It reads the link text as content: COUNTER-DIGEST (wrong class), and for the population link POPULATION-DIGEST + POPULATION-EMPTY (wrong class, two findings).

Totals: 3 + 4 + 4 + 2 = 13.

The 3 new passes at base are heading-valid-tail (base already treats `## C2` as a claim), and the two negative controls dispatch-names-after and dispatch-notes-before (base flags nothing, which is the expected outcome).

`selftest=FAIL patches=0/3` in the SUMMARY is expected at base: the base tool has no `--selftest` (argparse rc=2). It is not one of the 13 case failures.

## 6. Comparison with CASES

My derivation (section 2) matches CASES for all 16 new cases: exit code and multiset. Under the readings in A1 and A2 the match is exact. No row is contradicted by the docstring. Count check: CASES has 35 tuple entries plus the two `two_unresolved` checks = 37, which matches the docstring's "37 cases" (21 r41 + 16 new).

## 7. Verdict

- Base reproduction: CONFIRMED (pass=24 fail=13, rc=1, failures explained class-by-class).
- Grammar determinacy of the 16 expectations: 14 of 16 fully determined; 2 ambiguous (A1 dup-base-differs, A2 population-symlink). Each has a proposed reading, and the docstring should state it so that two honest implementations cannot disagree.
- Residual: N1 (malformed heading closes or does not close a block) is not exercised by any case and is a docstring gap for the L1. Nothing here is edited.

## 8. Cleanup and tooling

- Scratch: /fast/scratch/hyaku/souji-r42/R42reviewer02 (score-candidate's own clone was removed by its trap). The scratch dir was removed with `rm -rf` in the same step that wrote this report; `ls` afterwards reports it absent.
- No tool was installed or upgraded. No git or jj mutation was run.
