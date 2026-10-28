# R41reviewer05 — audit of the r41 preregistration and the C2 grammar

Seat: R41reviewer05 (reviewer, leaf). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin.
Freeze commit: e2a74312af4233963e44e4dbb38838ece07b8bd2 (HEAD at audit time; `git status --short` empty before and after).
Instruments commit: 6682b98175b995ee4646ffd1ea6bd8a12cd353dd. Base for all claims: 7eebc183f2685d1ea9b004b4de22c09a8a4035a7.
Tools installed: none. Lane writes: none. Scratch: /fast/scratch/hyaku/souji-r41/R41reviewer05 (deleted before yield).

## Verdict

- Preregistration audit: PASS on every check the task names, with one named limit (F1): the four Target literals are not byte-equal to the strings the counters print. They match as printed prefixes; the trailing `(exit 0)` is never printed.
- C2 grammar audit: operable on the 21 cases, but the cases force only part of the grammar. 23 choices are unforced (section 3B). Eleven of them (U1, U2, U3, U7, U8, U9, U11, U12, U13, U14, U15) were run as knob variants through the frozen counter and each scores 21/21, so the counter cannot tell them apart. One of them (U1, reading the prereg from the working tree rather than the blob at --rev) is contrary to the grammar text and still scores 21/21. Under the all-target-then-smaller-bytes tie-break in preregistration rule 3, that gap can decide which candidate lands. Reported as named limit F2 for the L1.

## 1. Commands run and their output

### 1.1 Freeze and instrument identity

    git -C LANE rev-parse HEAD                      -> e2a74312af4233963e44e4dbb38838ece07b8bd2
    git -C LANE rev-parse --show-toplevel           -> /home/vgpnk/Projects/shokunin/souji-shokunin
    git log --diff-filter=A -- census/round-41/preregistration.txt
                                                    -> e2a74312… "round-41: freeze preregistration and do-nothing controls"
    merge-base --is-ancestor 7eebc18… e2a7431…      -> ancestor (Base is a strict ancestor; base != freeze)
    merge-base --is-ancestor 6682b98… e2a7431…      -> ancestor
    git show --stat e2a7431                         -> 9 files, 196 insertions: preregistration.txt and 8 controls/ files
    git ls-tree -r e2a7431 -- .ufo/waves/round-41   -> empty (no wave file tracked at freeze)
    git cat-file -e 6682b98…:census/round-41/records/census-before.txt -> present

### 1.2 Every sha256 recomputed (git show <rev>:<path> | sha256sum), at 6682b98, at e2a7431 and at HEAD

| path | sha256 (recomputed, identical at all three revs) | stated in prereg | match |
|---|---|---|---|
| census/round-41/c1-counter.py | 8860dc7af55848db3d67d11aec69cd8ee1f5a413964dd32ac7baddcebe49ab63 | C1 Counter | yes |
| census/round-41/c1-items.tsv | 2d2a548e253b7863cd9679ebe9f1f851a10223e47d3456e33345279b79a036cf | C1 Population | yes |
| census/round-41/c2-counter.py | 85ffe2638a5ed0c83438ce96224f6dad07b2c99567d3d1a71e76e9316a1d1e11 | C2 Counter | yes |
| census/round-41/c2-cases.tsv | 4854335abdd479423d01d435a4fbe2e8f82d432a58414df945da8b48930e75c6 | C2 Population | yes |
| census/round-41/c3-counter.py | 9ef99e8f20805501c3944e4b598e3fd7b7ac3ea3914674fa46e6affdc1e537ca | C3 Counter | yes |
| census/round-41/c3-sites.tsv | be363c0de5d332dc4223bdf6ccf5f2035e6e38af9cc30735463b07b5d2e764ea | C3 Population | yes |
| census/round-41/r1-counter.py | 8352eed44705066de36f8775ca421f5325820d5856b25d08d3daab7a63c60556 | R1 Counter | yes |
| tools/souji-worktree-drift.py | b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6 | pinned sha (frozen rule 1) | yes |
| census/round-41/preregistration.txt | dd4efc80972b958774c1bc145e00868eee01dea6cddb6e2fe1a7a0e03fa5fb7c | not self-stated | n/a |

The frozen rule that each Counter/Population blob is byte-identical at 6682b98, e2a7431 and HEAD holds for all 8 paths (same sha256 at all three; `git rev-parse` blob ids for c2-counter.py identical at all three: 17ee2fd264e50ffe15bbb27b5399d4e4930c31e5).

### 1.3 Control paths at e2a7431

    census/round-41/controls/c1-control.txt  PRESENT
    census/round-41/controls/c2-control.txt  PRESENT
    census/round-41/controls/c3-control.txt  PRESENT
    census/round-41/controls/r1-control.txt  PRESENT

Last non-blank line of each control receipt: `EXIT=1` for all four (c1, c2, c3, r1). The C2 grammar's CONTROL-NOT-RED rule therefore passes on the real controls.

### 1.4 Six keys per claim (strict reading)

Parsed the frozen prereg (`git show e2a7431:census/round-41/preregistration.txt`, sha dd4efc80…) with a `## C<digits>` block splitter and column-0 `Key: ` matching:

    C1: Base, Counter, Population, Control, Target, Kill — all six present, no duplicates; Base 40 hex
    C2: same, no duplicates; Base 40 hex
    C3: same, no duplicates; Base 40 hex
    claim blocks = 3 (## C1, ## C2, ## C3); ## R1 and ## Frontier step are not claim blocks
    Counter/Population digests at FREEZE blob: OK for all six paths (sizes 9102, 281, 16336, 752, 13497, 1534 bytes)

Extra column-0 lines `Predicate:` and `Do-nothing control:` do not collide with `Control:` under the anchored grammar. The R1 block carries Base, Counter, Control, Target, Kill and Predicate, and no Population key. R1 is not a claim, so the six-key rule does not apply to it.

### 1.5 Target literals against the counters' print statements

Frozen prereg Target text versus the counter's own `print`/return (source read at the freeze blobs):

| claim | prereg Target (verbatim minus "over the landed lane tip") | counter prints (source) | relation |
|---|---|---|---|
| C1 | `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1 (exit 0)` | c1-counter.py:164-165 `SUMMARY items=%d mismatched=%d corrected=%d uncorrected=%d junk=%d rewritten=%d sourced=%d` | printed prefix equal; `(exit 0)` never printed |
| C2 | `SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red (exit 0)` | c2-counter.py:306-308 `… retro=%s tool_sha=%s` | printed prefix equal; `tool_sha=` printed, not in Target; `(exit 0)` not printed |
| C3 | `SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 (exit 0)` | c3-counter.py:162-164 `… docclasses=%d site_regex=%s docclasses_match=%s tool_sha=%s fixture_sha=%s` | printed prefix equal; four extra fields; `(exit 0)` not printed |
| R1 | `SUMMARY mutants=11 killed=11 survived=0 pristine=ok regress=8/8 new_killed=3/3 old_fixtures_killed_new=0 prior=6/6 (exit 0)` | r1-counter.py:225-228 `… prior=%d/6 cases=%d tool_sha=%s fixture_sha=%s` | printed prefix equal; `(exit 0)` not printed |

Each counter's docstring Target omits the `(exit 0)` suffix. The receipts record exit as a separate `EXIT=<n>` line (controls/c1..r1-control.txt). The do-nothing control receipts show the counters' own lines in the same key order (e.g. controls/c1-control.txt `SUMMARY items=3 mismatched=3 corrected=0 uncorrected=3 junk=3 rewritten=0 sourced=0`), so the prefix match is real. See F1.

### 1.6 C2 probe runs (frozen counter, knob variants of a reference reading)

Method: wrote one reference reading of the c2-counter.py grammar with a few knobs (generator run from scratch; variants saved at `.ufo/waves/round-41/w1/R41reviewer05/probe/variants/`). Each variant was scored through the frozen counter's own `score_tool` plus the real and retro legs, exactly as the counter's `main()` runs them. Output: `probe/variant-results.json`.

    baseline                      cases=21 pass=21 fail=0 real=ok((3, 0)) retro=red(findings=18) failing=-
    read-worktree-not-blob        cases=21 pass=21 fail=0 real=ok((3, 0)) retro=red(findings=18) failing=-
    base-equal-freeze-accepted    cases=21 pass=21 fail=0 real=ok((3, 0)) retro=red(findings=18) failing=-
    population-min-3-lines        cases=21 pass=21 fail=0 real=ok((3, 0)) retro=red(findings=18) failing=-
    digest-checked-at-rev         cases=21 pass=19 fail=2 real=ok((3, 0)) retro=red(findings=18) failing=['frozen-edited-counter', 'frozen-edited-population']
    dispatch-off                  cases=21 pass=20 fail=1 real=ok((3, 0)) retro=red(findings=18) failing=['dispatch-before-freeze']
    dispatch-same-commit-hit      cases=21 pass=21 fail=0 real=ok((3, 0)) retro=red(findings=18) failing=-
    keys-case-insensitive         cases=21 pass=21 fail=0 real=ok((3, 0)) retro=red(findings=18) failing=-
    malformed-sha-as-digest       cases=21 pass=21 fail=0 real=ok((3, 0)) retro=red(findings=18) failing=-
    blank-any-key-field-empty     cases=21 pass=21 fail=0 real=ok((3, 0)) retro=red(findings=18) failing=-
    claims-count-clean-only       cases=21 pass=21 fail=0 real=ok((3, 0)) retro=red(findings=18) failing=-
    rev-abbrev-accepted           cases=21 pass=21 fail=0 real=ok((3, 0)) retro=red(findings=18) failing=-
    label-by-ordinal              cases=21 pass=21 fail=0 real=ok((3, 0)) retro=red(findings=18) failing=-
    control-physical-last-line    cases=21 pass=21 fail=0 real=ok((3, 0)) retro=red(findings=18) failing=-

The reference reading itself scores 21/21 with real=ok and retro=red, so the 21 cases are satisfiable by the grammar as written.

Supported harness, run on the reference and on three variants (advice only, in scratch clones):

    bash census/round-41/score-candidate.sh c2 <scratch> tools/souji-freeze-check.py=probe/reference-baseline-probe.py
        -> 21 case lines PASS; "real ok rc=0 findings=0 summary=(3, 0)"; "retro red rc=1 findings=18 summary=(3, 18)"
           "SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=b99110ee46fb"  exit=0
    … digest-checked-at-rev.py -> "SUMMARY cases=21 pass=19 fail=2 … real=ok retro=red"; failing frozen-edited-counter, frozen-edited-population (findings ['COUNTER-DIGEST','FROZEN-EDITED'] want ['FROZEN-EDITED']); exit=1
    … dispatch-off.py          -> "SUMMARY cases=21 pass=20 fail=1 …"; failing dispatch-before-freeze; exit=1
    … read-worktree-not-blob.py -> "SUMMARY cases=21 pass=21 fail=0 … real=ok retro=red"; exit=0

Scratch clones were removed by score-candidate.sh's own trap. Scratch root deleted at the end.

### 1.7 Other reads

- Working tree: `.ufo/waves/round-41/w1/` holds untracked files written after the freeze (19:38–19:57, other seats' candidates and reports; none is a `*-dispatch.json` or `*.ready`). `git ls-files .ufo/waves/round-41` is empty. See F3.
- `census/round-41/__pycache__/` exists (`c2-counter.cpython-314.pyc`), ignored by `.gitignore:3`, not tracked. Hygiene only.
- Read-only peek at other seats' in-flight `souji-freeze-check.py` (R41executor07/08/09): they resolve the same unforced points differently (e.g. executor09 treats a non-matching key line as FIELD-MISSING; executor07 and executor09 use a merge-base ancestor test for Base). Not scored; not evidence about the frozen counter.

## 2. Findings on the frozen instruments (named limits, not edits)

F1 (prereg Target literals, all four). The Target strings are printed prefixes of the counters' SUMMARY lines with an appended `(exit 0)` that no counter prints; C2, C3 and R1 print extra fields. Strict equality fails for all four Targets. Evidence: §1.5. Named limit for the L1: the receipts' `EXIT=` line is the exit evidence. Not an edit.

F2 (C2 grammar, unforced cases). The counter cannot distinguish readings that violate the grammar text. Most important: the grammar says Preregistration "read from the blob at --rev" (c2-counter.py:12-13). A candidate that reads the working tree passes 21/21 (§1.6). Also: a non-strict Base test (`merge-base --is-ancestor` accepting Base == FREEZE-REV) passes 21/21 although the text says "strict". Under preregistration rule 3 (all-target first, then smaller bytes) a smaller grammar-violating candidate can outscore a conforming one. Named limit for the L1 and the r41 lesson.

F3 (dispatch scope). The DISPATCH-BEFORE-FREEZE check is git-only (`git log --diff-filter=A`). Wave files written to the working tree (untracked) are invisible to it. Currently only untracked files exist, none matching the pattern, so the check result is unaffected today. Named limit.

F4 (cosmetic, no action). Untracked `census/round-41/__pycache__` created without `-B`.

## 3. C2 grammar: ambiguities a candidate could resolve two ways

Source: census/round-41/c2-counter.py docstring lines 12-52 and CASES lines 193-213. "Forced" means the 21 cases (19 mutation cases + 2 refusal cases) fail if the other reading is chosen. "Unforced" means at least one alternative reading also gives 21/21 (probe result cited where run).

### 3A. Forced by the 21 cases (which way they force)

1. COUNTER-DIGEST/POPULATION-DIGEST are computed on the blob at FREEZE-REV, not at --rev. Forced by frozen-edited-counter and frozen-edited-population (probe digest-checked-at-rev: 2 fails, output in §1.6).
2. FROZEN-EDITED is a blob comparison (rev blob vs freeze blob), not a digest mismatch. Forced by counter-digest and population-digest: a rule "FROZEN-EDITED when digest at --rev differs" would emit an extra FROZEN-EDITED in those cases (argued from the case text; not run).
3. A `dispatch` file first added in a strict-ancestor commit of the freeze gives DISPATCH-BEFORE-FREEZE; one added after the freeze gives nothing. Forced by dispatch-before-freeze and clean-dispatch-after (probe dispatch-off: 1 fail).
4. NO-CLAIMS and DISPATCH-BEFORE-FREEZE are labelled C0. Forced by no-claims and dispatch-before-freeze.
5. A claim key that is absent produces exactly one FIELD-MISSING and no cascade: drop Base gives only FIELD-MISSING; drop Counter gives only FIELD-MISSING, not COUNTER-MISSING. Forced by field-missing-base and field-missing-counter.
6. A key line with an empty value after `Key: ` is present-but-blank, so FIELD-EMPTY and not FIELD-MISSING. Forced by field-empty-target, whose line is `Target: ` with a trailing space. Blank Target and Kill are FIELD-EMPTY.
7. Each claim is checked independently: a second, bad claim yields its own finding, and the good first claim yields none. Forced by two-claims-one-bad.
8. Refusals (exit 2, message on stderr containing COULD-NOT-EVALUATE, no traceback) for an unresolvable full40 --rev (`f`×40) and for an absent prereg at a resolvable rev. Forced by unresolved-rev and absent-prereg; findings are not expected on stdout in that case.
9. Exit codes: 0 with no findings, 1 with findings, 2 for refusal. SUMMARY `findings=` equals the count of FINDING lines. The SUMMARY line must match `^SUMMARY claims=(\d+) findings=(\d+)\s*$` and be the last one. FINDING lines are read at column 0. Forced by case_ok's rc and summary check.
10. The claim set is exactly the `## C<digits>` blocks: `## R1` and `## Frontier step` are not claims. Forced by the real leg requiring claims=3 on the lane's prereg.
11. Base == a non-ancestor (side branch) gives BASE-NOT-ANCESTOR; all-zero full40 gives BASE-UNRESOLVED. Forced by base-not-ancestor and base-unresolved.
12. Population with only the header line (1 non-blank line) gives POPULATION-EMPTY. Forced by population-empty.
13. Control whose last non-blank line is `EXIT=0` gives CONTROL-NOT-RED; `EXIT=1` is accepted; a missing control gives CONTROL-MISSING. Forced by control-not-red and control-missing.
14. Retro: the r40 prereg (which has no `Round:` line) must not be a refusal (rc must be 1). Forced by retro=red requiring rc==1.
15. Stub rejection: the two built-in stubs must each fail at least one case (trivial, but it forces the 21 cases to be non-vacuous).

### 3B. Unforced: alternative readings that also score 21/21 (probe result where run)

U1. Prereg read from the working tree vs the blob at --rev. Probe: 21/21. Grammar text says blob at --rev. (F2)
U2. Base == FREEZE-REV: strict (grammar text) vs non-strict. Probe base-equal-freeze-accepted: 21/21. Text resolves it: strict.
U3. Dispatch file first added in the freeze commit itself: "FREEZE-REV or an ancestor of it" (finding) vs "strict-ancestor test" (no finding). The grammar text contradicts itself. Probe dispatch-same-commit-hit: 21/21. Not in the real prereg (checked: no wave file at e2a7431).
U4. Dispatch glob breadth: `*.ready` (no case), nested paths under `.ufo/waves/round-41/` (no case), `*-dispatch.json` vs basename-only match (no case). Not run; by reading only.
U5. Dispatch scope path: literal `.ufo/waves/round-<N>/` (text) vs "the prereg's own directory tree" (the prose). Only the literal is consistent with the text; the cases use the literal path. Not run.
U6. Round number absent (r40 prereg has no `Round:` line): skip the dispatch check vs derive N from the path vs refuse. Retro forces "not refuse"; skip vs path-derivation is unforced. Probe skip: 21/21 and retro red.
U7. Population threshold: "fewer than 2 non-blank lines" (text) vs "fewer than 3". Probe population-min-3-lines: 21/21. Clean population has three non-blank lines, so the boundary is untested.
U8. Blank Base, Counter, Population or Control: grammar assigns FIELD-EMPTY only to Target and Kill. Blank Base could be FIELD-EMPTY, FIELD-MISSING or BASE-UNRESOLVED; blank Control could be FIELD-EMPTY or CONTROL-MISSING. Probe blank-any-key-field-empty: 21/21.
U9. A Counter or Population line without `sha256=<64 hex>`: no class is listed. Could be FIELD-MISSING, COUNTER-DIGEST, or other. Probe malformed-sha-as-digest: 21/21.
U10. Existence and content lookups for COUNTER-MISSING, POPULATION-MISSING, CONTROL-MISSING, POPULATION-EMPTY, CONTROL-NOT-RED: at FREEZE-REV (text) or at --rev. No case adds the path after the freeze, so the choice is invisible. Not run (argued).
U11. Short or abbreviated --rev or Base (not full40). Text: Base not full40 gives BASE-UNRESOLVED; --rev must be "a resolvable full40 commit". Probe rev-abbrev-accepted: 21/21. No case uses an abbreviated rev.
U12. Claim label: the `##` header number (text: "`## C<digits>`") vs the ordinal position of the block. Equal in every case. Probe label-by-ordinal: 21/21.
U13. SUMMARY claims= count: all blocks vs only blocks with no findings. The real leg uses an all-clean prereg, and the other cases check findings only. Probe claims-count-clean-only: 21/21.
U14. Control's exit line: last non-blank line (text) vs last physical line. Probe control-physical-last-line: 21/21. Also `EXIT=-1`, `EXIT=01`, `EXIT= 1` not decided.
U15. Key matching: column-0 exact (text) vs case-insensitive. Probe keys-case-insensitive: 21/21. A non-anchored search also collides with `Do-nothing control:` in the real prereg. The real leg does not detect this (first match is still correct), so this is untested.
U16. Key lines that are indented or lack the space after the colon (`Base:7eeb…`, ` Base: …`). Not decided by text or cases. Not run.
U17. Hashing raw bytes (text) vs decoded text (CRLF, UTF-8 normalisation). The cases are ASCII LF only. Not run.
U18. Freeze lookup `git log --diff-filter=A` on non-linear history (date vs topological order; renames). All cases are linear. Not run.
U19. Counter/Population path deleted at --rev but present at FREEZE-REV: FROZEN-EDITED or COUNTER-MISSING. No case. Not run.
U20. Finding detail text (anything after the class token). Cases check claim and class only. Free.
U21. Output order of FINDING lines. Cases sort. Free.
U22. Working-tree (untracked) dispatch files. Same as F3. Not run.
U23. Stdout/stderr split for FINDING lines in the refusal path. Forced only that refusal is on stderr (see 3A.8); whether FINDING lines may also appear there is free.

Summary: 15 forced choices, 23 unforced (U1–U23). Eleven unforced choices were run through the probe and scored 21/21: U1, U2, U3, U7, U8, U9, U11, U12, U13, U14, U15. U6 (Round line absent) is observed only as the reference reading's skip behaviour, not run as a variant. Every unforced choice marked "not run" stays a reading, not a measurement.

## 4. Verdict on operability

- The prereg is internally consistent and reproducible: every digest, control path and key matches the freeze tree. Only F1 (Target literal wording) is a real mismatch, and it is a prefix-match limit, not an instrument defect.
- The C2 counter is operable as an acceptance test: the reference reading passes 21/21 and the harness runs end to end. As a discriminator of grammar conformance it is weak: F2 (working-tree read, non-strict Base) and the unforced rows in §3B are not caught. The L1 should treat a candidate's C2 score as the harness result plus a manual read against the grammar text in c2-counter.py:12-52, not as a grammar proof.
- Nothing in this seat's scope was edited. No lane, fleet, state or watchdog file was written. HEAD is unchanged (e2a7431), `git status --short` is empty.
