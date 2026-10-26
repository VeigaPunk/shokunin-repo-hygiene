# r32 a2w1 — adjudication of attempt-1 wave-1 reports (critic/reviewer/mutation/connector/revenger/sentinel/simplifier/scribe)

Seat `SwarmCritic38`, wave `souji-r32-a2w1`, leaf member. Read-only over the lane. Frozen inputs read first:
`census/round-32/records/preregistration.txt` (3ec84fc81b3243429c834a051880b0bcde06291c), `records/amendments.txt`
(A0 pre-data, A1 post-wave-1), `records/controls.tsv`, `c3-contract.txt`, the three counters and the M1 tool.
Landed revisions adjudicated: base 85b61a151923986e7e6b48f7084b9122561b5f3d; A0 7a6667cd27652baf8d704b5cdb8e3200bd6e27a1;
C2 98e5203d45b4e419a9e72801733d93303acc7ebd; C3+A1 92e1aae… a92e1aae91dbf46c2d7eff713932cfc820186970;
C1 9e8982b7a6ac57dffa415f9db43cf7cd6e829c93; salvage/tip 4e56c48b8fc828f9aba2746e324dc46aa538bdbf.

Disposition vocabulary (fixed by the assignment): `resolved@<full40>` = landed bytes address it; `amended:A0|A1` = the
frozen amendment addresses it; `disclosed:<path>:<line>` = the landed round states it without changing a predicate;
`open` = the landed bytes do not address it and no amendment covers it.

## Re-derived readings at the tip (this seat, not the salvage records)

Every command below ran with `TMPDIR=/fast/scratch/hyaku/souji-r32/SwarmCritic38/tmp`, `python3 -B`, `--root` the lane,
`--base 85b61a1…`, `--list-rev 3ec84fc…`.

| instrument | rev | reading | matches attempt-1 record |
|---|---|---|---|
| c1-counter.py (v1) | 4e56c48… | `SUMMARY items=44 bound_run=3 bound_record=9 bound_field=9 withdrawn=17 unbound=6 mismatches=6`, rc 0 | yes, `records/c1-after-v1.txt` (taken at 9e8982b) |
| c1-counter-v2.py | 4e56c48… | identical SUMMARY (`withdrawn=17 unbound=6 mismatches=6`) | yes, `records/c1-after-v2.txt` |
| c2-counter.py `--only T18` | 4e56c48… | `ITEM T18 FAIL base=rc0:W4236:…baseline_mismatches=26 sbox=rc0:W4229:…baseline_mismatches=32 regress` | consistent with `records/c2-after-v1.txt` (31 at 98e5203) |
| c3-counter.py (v1) | 4e56c48… | `SUMMARY legs=14 fail=0 f1_entries=5`, rc 0 | yes |
| c3-counter-v2.py (A1) | 4e56c48… | `SUMMARY legs=17 fail=0 f1_entries=5`, rc 0 | yes |

So: C1 MISSED at the tip under both v1 and v2 (`unbound=6 mismatches=6 withdrawn=17`); C2 MISSED (T18 only failure in
the attempt-1 record, re-confirmed at the tip); C3 met under v1 and v2 at the tip.

## The table

| report | STATUS | finding (location) | disposition |
|---|---|---|---|
| w1/SwarmCritic33.md | PASS | F1 v1 binds citations not truth; N38 `3` is the digit of `python3` (c1-counter.py:15-44) | open |
| w1/SwarmCritic33.md | PASS | F2 A0(a) voided by a bare `*` token; SCORECARD.md:161 carries `refs/jj/*` (c1-counter-v2.py:152) | open — landed N12 is a `run` row, so the hole is unexercised, not closed |
| w1/SwarmCritic33.md | PASS | F3 A0(b) rejects the cell's own record and accepts an unrelated arm (c1-counter-v2.py:161) | open |
| w1/SwarmCritic33.md | PASS | F4 `field` checks key substring and integer value only, no adjacency or quantity identity (c1-counter-v2.py:337-350) | open |
| w1/SwarmCritic33.md | PASS | F5 digit-bearing unit words `k1`, `r26` cannot be represented (c1-counter.py:15) | disclosed:census/round-32/records/amendments.txt:25 and landed withdrawals SCORECARD.md:459,460,470 |
| w1/SwarmCritic33.md | PASS | F6 single-digit literal rejected by any rev-bearing argv, N19 unwinnable by `run` (c1-counter-v2.py:311) | open — landed N19 chose the literal `mismatches=0`, dodging the rule without changing it |
| w1/SwarmCritic33.md | PASS | F7 r13 cell says `33 rows`/`mined=16` while the cited verification.json says 37/20 (SCORECARD.md:151) | disclosed:SCORECARD.md:436-437 (both withdrawn with the contradiction stated) |
| w1/SwarmCritic33.md | PASS | F8 counts of things (list length, RESULT-line count, waves-children) unrepresentable (SCORECARD.md:159,314,424) | disclosed:SCORECARD.md:445,456,471 |
| w1/SwarmCritic33.md | PASS | F9 withdrawal reason is unfalsifiable prose of at least 8 words (c1-counter-v2.py:296) | open |
| w1/SwarmCritic33.md | PASS | F10 shared-occurrence makes line 422 bind at most 2 of 8 items (c1-counter-v2.py:300) | disclosed:amendments.txt:25 and reproduced: only N27 (SCORECARD.md:461) and N32 (:462) bind, N28-N31,N33,N34 unbound |
| w1/SwarmCritic33.md | PASS | F11 enumeration reads only the evidence cell, so count integers in the description cell stay outside (c1-enumerate.py:57) | open |
| w1/SwarmCritic33.md | PASS | F12 honest floor (6 impossible + 11 unrunnable = 17) exceeds the withdrawal cap 8 | disclosed:amendments.txt:24-27 (the miss is recorded) |
| w1/SwarmCritic33.md | PASS | AL1 cheapest mechanical binder meets the v1 target (target met, withdrawn=4) | amended:A0 (v2 instrument + controls-a0.tsv exist pre-data) |
| w1/SwarmCritic33.md | PASS | AL2 unit words too common (mean 86.25 candidate lines per item) | open |
| w1/SwarmCritic33.md | PASS | AL3 withdrawal cap is a quota on honesty | open |
| w1/SwarmCritic33.md | PASS | AL4 masks hide nothing in the evidence cell (negative result) | disclosed:.ufo/waves/round-32/w1/SwarmCritic33.md (no action needed) |
| w1/SwarmCritic34.md | FAIL | F1 pass predicate has no TMPDIR assertion and no case-level output equality (c2-counter.py:174-176) | disclosed:amendments.txt:29-31 (not amended) |
| w1/SwarmCritic34.md | FAIL | F2 cheat A: scratch inside the clone, caller TMPDIR unused, PASS with W111 | disclosed:amendments.txt:29-31 |
| w1/SwarmCritic34.md | FAIL | F3 cheat B: EROFS detected, no cases run, 60 dummy files, PASS | disclosed:amendments.txt:29-31 |
| w1/SwarmCritic34.md | FAIL | F4 work gate vacuous when BASE W is 0; T03 is `rc1:W0` in both runs (c2-counter.py:175) | open — T03 still `base=rc1:W0:assertions=252 …` in records/c2-after-v1.txt |
| w1/SwarmCritic34.md | FAIL | F5 sandbox binds only /tmp, /var/tmp, /dev/shm; clone and $HOME writable (c2-counter.py:154-155) | disclosed:amendments.txt:29-31 |
| w1/SwarmCritic34.md | FAIL | F6 the 27 are not the closure of their own rule: tools/souji-vault-verify.sh:742 is `${TMPDIR:-/var/tmp}`, base-passing, absent | open — 98e5203 patched tools/souji-round9-selftest.sh:7,14 only; souji-vault-verify.sh is unchanged and still out of the set |
| w1/SwarmCritic34.md | FAIL | F7 T13's exclusion reason is accurate (negative check) | disclosed:.ufo/waves/round-32/w1/SwarmCritic34.md (no action needed) |
| w1/SwarmCritic34.md | FAIL | F8 the parenthetical "work not dropped" is intent, not predicate | open |
| w1/SwarmCritic35.md | PASS | F1 L12/L13 satisfiable with zero measurement: six calls issued, statuses discarded, table from constants (c3-counter.py:262,270) | amended:A1 (L16 requires abandon and gc exits 0 plus a cat-file mix, which the documented cheat's `abandon rc=1` fails) |
| w1/SwarmCritic35.md | PASS | F2 M3 proves only that touch's effect is noticed; neither leg reads the object (c3-counter.py:270) | amended:A1 (L15, L16) with residual open: L15 probes the counter's own fresh repo pair, so a record encoding correct default-gc physics from constants still agrees |
| w1/SwarmCritic35.md | PASS | F3 provenance self-declared: hand-written snapshot and a fetch receipt claiming 200 for a 404 URL (c3-counter.py:223,232) | amended:A1 (L17; my run `L17 PASS refetched=4 bad=[]` at the tip) |
| w1/SwarmCritic35.md | PASS | F4 novelty asserted, not tested; L1 is a file count and L2 a map agreement (c3-counter.py:138) | open — no leg requires a `where=cruft` instance of the new edge |
| w1/SwarmCritic35.md | PASS | F5 the measured clock is new F1 ground (defensible claim) | disclosed:.ufo/waves/round-32/w1/SwarmCritic35.md (no action needed) |
| w1/SwarmCritic35.md | PASS | F6 L8 version anchors and L10 spans are free text; cheat D prints literal `jj 0.45.1` (c3-counter.py:244,248) | open — no leg ties a version line to a `--version` call |
| w1/SwarmCritic36.md | PARTIAL | F1 a `RESULT` line followed by a tab, or a bare `RESULT`, is inside the frozen contract and outside both parsers (tools/souji-record-contract.py:44, c3-counter-v2.py:93) | open — both still `startswith("RESULT ")`; contract says "starts with `prefix`" (c3-contract.txt:3) |
| w1/SwarmCritic36.md | PARTIAL | F2 two parsers, one wired; the tool's wildcard leniency is untested against C3 | open |
| w1/SwarmCritic36.md | PARTIAL | F3 the r31 reconstruction drops the frozen clause "no hashes or timestamps on RESULT lines" (m1-r31-contract.txt:4-10) | open |
| w1/SwarmCritic36.md | PARTIAL | F4 non-RUN records are unread; a second record with out-of-contract values passes every leg | open (frozen singular scope) |
| w1/SwarmCritic36.md | PARTIAL | F5 no cross-field constraint between arms and prose | open (frozen; a contract edit would fail L14) |
| w1/SwarmCritic36.md | PARTIAL | F6 wildcard over-acceptance: superscript digits under `#`, `=` inside `*`, empty value under a trailing pipe (tools/souji-record-contract.py:56) | open |
| w1/SwarmCritic37.md | PASS | A1/F1 C3's mandated entry kills C2's T18 (prereg C3 clause vs c2-items.tsv:29) | disclosed:amendments.txt:26-29; reproduced at the tip: 26 to 32, and 5 of the 6 added paths come from C2's own patch (see N2 below) |
| w1/SwarmCritic37.md | PASS | A2/F2 C1 run bindings execute base-blob script with REV callees (c1-counter.py run()) | resolved@9e8982b7a6ac57dffa415f9db43cf7cd6e829c93 for N35, N36, N37 (record rows, SCORECARD.md:463-465); residual open for the three surviving `run` rows (N12 :446, N16, N19) |
| w1/SwarmCritic37.md | PASS | A3/F3 C3 legs L2 and L3 execute REV tools that C2 edits (c3-counter.py L2, L3) | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 — my tip run prints `L2 PASS` and `L3 PASS` after C2 landed |
| w1/SwarmCritic37.md | PASS | A4/F4 Q59 R2 cannot see `instrument-repair`, so an axis-swapped mutant prints flags=0 (tools/souji-axis-check.py R2) | open — tool byte-identical since base |
| w1/SwarmCritic37.md | PASS | A5/F5 a `run` literal may restate a different quantity; N12 cell 13 bound by `failed=0` (c1-counter.py literal check) | open — landed exactly as delivered (SCORECARD.md:446), disclosed in that row's own reason cell |
| w1/SwarmCritic37.md | PASS | F6 claim verdicts (axis right for C1 and C3; C2 killed through T18; attribution unverified) | disclosed:amendments.txt:24-31 |
| w1/SwarmMutationTester38.md | PASS | F1 mutant m1 (drop append-only) killed on both counters | resolved@4e56c48b8fc828f9aba2746e324dc46aa538bdbf — counters byte-identical, kill stands |
| w1/SwarmMutationTester38.md | PASS | F2 m2 (two rows per id) killed | resolved@4e56c48b8fc828f9aba2746e324dc46aa538bdbf |
| w1/SwarmMutationTester38.md | PASS | F3 m3 (drop unit rule) killed | resolved@4e56c48b8fc828f9aba2746e324dc46aa538bdbf |
| w1/SwarmMutationTester38.md | PASS | F4 m4 (drop record line granularity) killed | resolved@4e56c48b8fc828f9aba2746e324dc46aa538bdbf |
| w1/SwarmMutationTester38.md | PASS | F5 m5 (drop round-set check) killed | resolved@4e56c48b8fc828f9aba2746e324dc46aa538bdbf |
| w1/SwarmMutationTester38.md | PASS | F6 m6 (drop unchanged-blob check) killed | resolved@4e56c48b8fc828f9aba2746e324dc46aa538bdbf |
| w1/SwarmMutationTester38.md | PASS | F7 m7 (accept a bool JSON field) survived; no admissible kill state | open (dead code w.r.t. the frozen corpus) |
| w1/SwarmMutationTester38.md | PASS | F8 m8 (drop withdrawal cap) killed, matching the withdraw-all control | resolved@4e56c48b8fc828f9aba2746e324dc46aa538bdbf |
| w1/SwarmMutationTester38.md | PASS | F9 m9 (drop stem-on-line rule) killed | resolved@4e56c48b8fc828f9aba2746e324dc46aa538bdbf |
| w1/SwarmMutationTester38.md | PASS | F10 m10 (accept rc not 0) killed | resolved@4e56c48b8fc828f9aba2746e324dc46aa538bdbf |
| w1/SwarmMutationTester38.md | PASS | F11 detached-HEAD scratch states cannot be transported by the counter's clone | disclosed:.ufo/waves/round-32/w1/SwarmMutationTester38.md (harness note) |
| w1/SwarmMutationTester38.md | PASS | F12 the committed control revs b0a0c718…, d4930a15… are not objects in the lane | open — verified MISSING; see N3 |
| w1/SwarmMutationTester39.md | PASS | F1 no counter hole; every pass-rule component load-bearing (negative sweep) | disclosed:.ufo/waves/round-32/w1/SwarmMutationTester39.md (no action needed) |
| w1/SwarmMutationTester39.md | PASS | F2 the two committed C2 controls are necessary but not sufficient | disclosed:.ufo/waves/round-32/w1/SwarmMutationTester39.md (no action needed) |
| w1/SwarmMutationTester39.md | PASS | F3 the C2-junk control rev bf984f0c… is not an object in the lane (controls.tsv:6 unreplayable) | open — verified MISSING; see N3 |
| w1/SwarmMutationTester39.md | PASS | F4 M7 (SBOX at --base) is invisible to both controls by construction | open |
| w1/SwarmMutationTester39.md | PASS | F5 M2 (/tmp bind) invisible to the do-nothing control; no enumerated item wrote a literal /tmp root | open — note the landed C2 patch now introduces a `${TMPDIR:-/tmp}` fallback in tests/fixtures/r27-pre-report-gate.sh:7 |
| w1/SwarmMutationTester39.md | PASS | F6 T03's base run creates nothing, so its pass is rc and last-line only | open |
| w1/SwarmConnector41.md | PASS | F1 C3 ground uncontested in 20 sibling lanes | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (entry landed; no sibling claim) |
| w1/SwarmConnector41.md | PASS | F2 fleet scripts/hyaku/disk-guard.sh:291-293 uses the same `${TMPDIR:-/var/tmp}` pattern, outside souji scope | disclosed:.ufo/waves/round-32/w1/SwarmConnector41.md (reported, not absorbed) |
| w1/SwarmConnector41.md | PASS | F3 sibling scratch norms split (kaidoku/kotodama /var/tmp vs revenger /tmp) | disclosed:.ufo/waves/round-32/w1/SwarmConnector41.md |
| w1/SwarmConnector41.md | PASS | F4 mori's r44 write-scope supersessions are prior art for the same overclaim class | disclosed:.ufo/waves/round-32/w1/SwarmConnector41.md |
| w1/SwarmConnector41.md | PASS | F5 C1's binding class has sibling instruments, no contested repository | disclosed:.ufo/waves/round-32/w1/SwarmConnector41.md |
| w1/SwarmConnector41.md | PASS | F6 tsukuroi strips ambient TMPDIR from probe children (different subject) | disclosed:.ufo/waves/round-32/w1/SwarmConnector41.md |
| w1/SwarmConnector41.md | PASS | F7 no lane claims souji's counters, SCORECARD or tools | resolved@4e56c48b8fc828f9aba2746e324dc46aa538bdbf (no conflict at the tip) |
| w1/SwarmConnector42.md | PASS | F1 C2 to C1 coupling through REV callees | resolved@9e8982b7a6ac57dffa415f9db43cf7cd6e829c93 for N35-N37; residual open for N12, N16, N19 |
| w1/SwarmConnector42.md | PASS | F2 binding rows are unnamespaced; a later same-shaped row turns the item into BAD-ROW(duplicate), and no post-landing repair path exists | open — no duplicates at the tip, the hazard stands |
| w1/SwarmConnector42.md | PASS | F3 C2 anchors are immune to C1's appended rows | resolved@9e8982b7a6ac57dffa415f9db43cf7cd6e829c93 (T03 identical at base and after the append) |
| w1/SwarmConnector42.md | PASS | F4 the r32 C3 fixture's scratch discipline is enforced by nothing mechanical (outside C2's set) | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 — the landed fixture refuses unset, empty, non-directory, in-lane and in-fleet TMPDIR (tests/fixtures/r32-jj-mtime-clock.sh:62-68) |
| w1/SwarmConnector42.md | PASS | F5 M1 tool and L14 are equivalent for the frozen contract; both miss the tab/bare prefix | open (same hole as Critic36 F1) |
| w1/SwarmConnector42.md | PASS | F6 recurring classes: vacuous targets, record-outside-contract, landing carry | open |
| w1/SwarmConnector42.md | PASS | F7 the binding-channel budget saturates the cap exactly (N15-N17, N20-N24 cannot bind) | disclosed:amendments.txt:24-27 and landed: 17 withdrawals |
| w1/SwarmReviewer32.md | PASS | F1 the base defect independently reproduced for T01, T04, T11, T19, T26 (c2-items.tsv:14,17,24,30,37) | resolved@4e56c48b8fc828f9aba2746e324dc46aa538bdbf (no counter defect; the prereg 26 of 27 FAIL reproduces) |
| w1/SwarmReviewer32.md | PASS | F2 counter base readings verified against an independent implementation: exact on rc and last line for 5 of 5, W within observed noise | resolved@4e56c48b8fc828f9aba2746e324dc46aa538bdbf (negative result, no action) |
| w1/SwarmReviewer32.md | PASS | F3 the half-of-base work rule is stable for the sampled set (smallest margin 529 creations) | resolved@4e56c48b8fc828f9aba2746e324dc46aa538bdbf (negative result, no action) |
| w1/SwarmReviewer32.md | PASS | F4 observation: one untracked lane file, census/round-32/measure.sh, at 7a6667c | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (committed in the C3 commit) |
| w1/SwarmReviewer32.md | PASS | AL no attack filed; optional stricter proposal to take W_base as the median of two runs | disclosed:.ufo/waves/round-32/w1/SwarmReviewer32.md (L1's call; not adopted, targets unchanged) |
| w1/SwarmRevenger29.md | PASS | F1 writer map complete; N18/N19 written by r26 for r24 content | disclosed:.ufo/waves/round-32/w1/SwarmRevenger29.md (informational) |
| w1/SwarmRevenger29.md | PASS | F2 the r12 row was rewritten by r13; the cell states the HEAD reading (33/16), not r12's output | disclosed:SCORECARD.md:436-437 (both counts withdrawn with the r13 pointer named) |
| w1/SwarmRevenger29.md | PASS | F3 eight integers on line 422 confined to two cited occurrences | disclosed:amendments.txt:25; reproduced: N27 and N32 only |
| w1/SwarmRevenger29.md | PASS | F4 `refs/jj/*` voids A0(a) for N12 | open (predicate unchanged; the landed N12 row is a `run` row) |
| w1/SwarmRevenger29.md | PASS | F5 A0(b) forbids derived unit words (`fail` vs `failed=13`) | open — N43 withdrawn at SCORECARD.md:471 for exactly this |
| w1/SwarmRevenger29.md | PASS | F6 three cells name no record at all (SCORECARD.md:168,313,314) | disclosed:SCORECARD.md:452-458 (N15, N17, N20-N24 withdrawn naming the missing record) |
| w1/SwarmRevenger29.md | PASS | F7 the `waves` exclusion refuses the cell's own pointer (census/round-26/waves) | disclosed:SCORECARD.md:456-458 |
| w1/SwarmRevenger29.md | PASS | F8 L29 is bindable under r32's `field` kind | resolved@9e8982b7a6ac57dffa415f9db43cf7cd6e829c93 (SCORECARD.md:434, field expected/matched_command_count=18) |
| w1/SwarmRevenger29.md | PASS | F9 remaining clusters have enough distinct occurrences | resolved@9e8982b7a6ac57dffa415f9db43cf7cd6e829c93 (N06-N10, N35-N42, N04-N05 bound) |
| w1/SwarmRevenger29.md | PASS | F10 max honest binding is 24; 20 need withdrawal, above the cap of 8 | disclosed:amendments.txt:24-27; my run reads 6 unbound and 17 withdrawn |
| w1/SwarmRevenger29.md | PASS | A1 A0(a) glob hole (gameable predicate, reproduced) | open |
| w1/SwarmSentinel43.md | PASS | F1 the 17 credential-shaped matches are the round-21 synthetic canary fixture | disclosed:.ufo/waves/round-32/w1/SwarmSentinel43.md (no action needed) |
| w1/SwarmSentinel43.md | PASS | F2 two canaries are shape-identical to live token formats and will be flagged by scanners | open — no allowlist or reshape landed |
| w1/SwarmSentinel43.md | PASS | F3 reason-oracle-before.txt is a red-before record; the fix is in the same tree | disclosed:.ufo/waves/round-32/w1/SwarmSentinel43.md (no action needed) |
| w1/SwarmSentinel43.md | PASS | F4 the two secret-path files are deny-lists; their `.ssh` writes stay inside a tempdir | disclosed:.ufo/waves/round-32/w1/SwarmSentinel43.md (no action needed) |
| w1/SwarmSentinel43.md | PASS | F5 the host shell rejects `grep -e`; a zero-hit sweep via `-e` is not evidence | disclosed:.ufo/waves/round-32/w1/SwarmSentinel43.md (host tool, no lane change) |
| w1/SwarmSentinel43.md | PASS | F6 one delivered tool hardcodes `/home/vgpnk` (w1/deliver-r31-landing-gate-precision.py:77-78) | open (wave delivery only; not a landed lane file) |
| w1/SwarmSentinel43.md | PASS | F7 no private URLs anywhere in scope | resolved@4e56c48b8fc828f9aba2746e324dc46aa538bdbf (no action needed) |
| w1/SwarmSentinel43.md | PASS | lane-hygiene note: census/round-32/__pycache__/c1-counter-v2.cpython-314.pyc exists (a counter ran without -B) | open — the file is still present, 31585 B, 05:31 |
| w1/SwarmSimplifier44.md | PARTIAL | D1 23 of 44 prompts name lane files relatively; `C3Fixture` creates a path outside the lane | open (attempt-1 plan, gitignored and not revision-pinned; a2w1's own context restates "Absolute paths only") |
| w1/SwarmSimplifier44.md | PARTIAL | D2 two scribes draft the same SKILL.md Gate-registry rows | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (one row each at SKILL.md:253,254,255) |
| w1/SwarmSimplifier44.md | PARTIAL | D3 the per-item C2 idiom allows a `/tmp` fallback, contradicting the frozen `${TMPDIR:?}` idiom | open, realized: tests/fixtures/r27-pre-report-gate.sh:7 is `mktemp -d "${TMPDIR:-/tmp}/…"` (see N1) |
| w1/SwarmSimplifier44.md | PARTIAL | D4 C3Rows and LessonGate disagree on whether the git-gc row exists | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (only S223 was opened; git-gc was already held as S063) |
| w1/SwarmSimplifier44.md | PARTIAL | D5 `<ids>` and `<your scratch>` placeholders in the acceptance lines | open in the w1 plan; absent from a2w1 (count 0) |
| w1/SwarmSimplifier44.md | PARTIAL | D6 ReviewControls re-runs the three critics' cheat vectors | open (attempt-1 plan artifact) |
| w1/SwarmSimplifier44.md | PARTIAL | D7 C3Rows' "exit 0 required" could not pass in wave 1 (E11 missing used-by) | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 — same-commit landing; my `sources-census.sh validate` at the tip prints `file ok`, rc 0, 36 W04, no E line |
| w1/SwarmSimplifier44.md | PARTIAL | D8 the C2 file lists are not closed under runtime dependency (tools/souji-seat-audit.py edited by C2Fix20; round9-selftest.sh needed by T15) | resolved@98e5203d45b4e419a9e72801733d93303acc7ebd (both files in the same landed commit; the plan-level ownership breach did occur) |
| w1/SwarmScribe22.md | PASS | F1 Gate-URL binding needs the raw URL in the cited row's source cell | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (S223's source cell holds the raw URL; `L6 PASS url_unbound=[]`) |
| w1/SwarmScribe22.md | PASS | F2 config-fragment quotes sit behind a page-scoped cell (S002 scope names reflog/rerere/worktree keys only) | open — S002's scope cell (corpus/SOURCES.md:23) is unchanged while the entry labels `gc.cruftPacks`/`gc.pruneExpire` quotes S002; disclosed in the entry's own source line 3 |
| w1/SwarmScribe22.md | PASS | F3 the record refuted two draft predictions and settled a third | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (landing used the record's 22 lines) |
| w1/SwarmScribe22.md | PASS | F4 `where=cruft` is decided by the `.mtimes` file's existence, not its contents | open — tests/fixtures/r32-jj-mtime-clock.sh keeps that method |
| w1/SwarmScribe22.md | PASS | F5 the old arms deliberately drop the descendant keeper | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (landed fixture unchanged in method; entry states the limit) |
| w1/SwarmScribe22.md | PASS | F6 the snapshot needs a SHA256SUMS line and a fetch receipt | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (census/round-32/sources/SHA256SUMS, records/fetch-receipts.tsv) |
| w1/SwarmScribe22.md | PASS | F7 two quotes are truncated to avoid the adoc's own double quotes (L5 counts spans) | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (`L5 PASS quotes=23 bad=[]`) |
| w1/SwarmScribe22.md | PASS | F8 eight Observed spans, all whole record lines | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (`L10 PASS result_spans=8 not_in_record=[]`) |
| w1/SwarmScribe22.md | PASS | F9 remaining L1 work: install entry, snapshots, fixture, record, row, docs | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970; nit open: the entry still says "placeholder id: the L1 renumbers by document" |
| w1/SwarmScribe23.md | PASS | F1 S224 cannot ground `gc.cruftPacks`; a conditional S225 was offered for the config key | open — no S224/S225 landed; the key's quotes stay under S002 |
| w1/SwarmScribe23.md | PASS | F2 the entry attributes config-fragment quotes to rows whose scope does not reach them | open — as landed (entry source line 3, corpus/SOURCES.md:23) |
| w1/SwarmScribe23.md | PASS | F3 relabelling the git-gc Gate lines to S224 without a `source:` line would fail L6 | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (not relabelled; L6 passes) |
| w1/SwarmScribe23.md | PASS | F4 no held row covers cruft behaviour and no duplicate URL is created | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (S223 validates rc 0) |
| w1/SwarmScribe23.md | PASS | F5 `used-by` derives from the entry's source lines | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (S002 and S063 used-by cells name the entry) |
| w1/SwarmScribe24.md | PASS | F1 four documentation edits drafted with anchors | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (corpus/README.md +64, PROVINCE.md +24, SKILL.md +19) |
| w1/SwarmScribe24.md | PASS | F2 the docs are load-bearing: without the F1 row edit L2 fails | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (`L2 PASS grounded=18 mapped=18`) |
| w1/SwarmScribe24.md | PASS | F3 the new paths must satisfy the gate-registry citation shape | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (three rows at SKILL.md:253-255) |
| w1/SwarmScribe24.md | PASS | F4 peer conflict: a sibling read the round-31 counter's ENTRY literal | resolved (landed entry uses the r32 arms mixed/never/nocruft/recent/old) |
| w1/SwarmScribe24.md | PASS | F5 M1 numbers come from the committed receipt, not from this seat's run | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (SKILL row cites m1-red-before.txt) |
| w1/SwarmScribe24.md | PASS | F6 the three registry rows use replayable red arms | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (rows cite the do-nothing control and the M1 receipt) |
| w1/SwarmScribe24.md | PASS | F7 the c2-counter verdict map (exit 0/1/2, partial=1) | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (row 255 states it) |
| w1/SwarmScribe24.md | PASS | F8 placeholder-bounded sentences were disclosed, not asserted | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (measurements filled from the record) |
| w1/SwarmScribe24.md | PASS | F9 peer-reported fixture shape recorded, not adopted | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (landed fixture reports 22 RESULT lines) |
| w1/SwarmScribe24.md | PASS | F10 untracked census/round-32/measure.sh observed and left alone | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (measure.sh committed in the C3 commit) |
| w1/SwarmScribe24.md | PASS | F11 second peer correction: drafted prose constrains no entry heading | resolved (no heading coupling in the landed entry) |
| w1/SwarmScribe24.md | PASS | F12 registry-versus-message conflict; artifacts used, not messages | resolved (landed artifacts are the authority) |
| w1/SwarmScribe24.md | PASS | F13 three draft sentences aligned to sibling drafts | resolved (wording only; landed entry states the same outcomes) |
| w1/SwarmScribe25.md | PASS | F1 defect-2(a) must land as a pair: entry `source: S051` plus S051's used-by cell | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (corpus/SOURCES.md:72 used-by and the appended source line) |
| w1/SwarmScribe25.md | PASS | F2 dropping the S051 quote would delete step 7's caveat | resolved (quote kept; appended bullet states it stays) |
| w1/SwarmScribe25.md | PASS | F3 S063 needs an anchor append, not a dedicated row | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (corpus/SOURCES.md:84 anchor extended) |
| w1/SwarmScribe25.md | PASS | F4 tools/souji-registry-agreement.py evaluates rc 2 at list-rev (facts triviality guard) | open — tool unchanged; K1 remains unrunnable through its entry point |
| w1/SwarmScribe25.md | PASS | F5 companion gap: S051's anchor cell never names `:52-53` | open — S051 anchor still lists only § Colocated workspaces, :115, :158, :229 |
| w1/SwarmScribe25.md | PASS | F6 the entry's last r31 bullet (S063 "scopes the page to § NOTES first paragraph") is stale after the anchor edit | resolved (an appended bullet supersedes it explicitly) |
| w1/SwarmScribe26.md | PARTIAL | F1 two rows leave the raw config/gc.adoc and git-repack.adoc URLs without a carrier under L6 | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (S223 carries the raw URL; `L6 PASS url_unbound=[]`) |
| w1/SwarmScribe26.md | PARTIAL | F2 the base registry is not cruft-free in prose: S004's teaches cell names `--cruft -d --expire-to` | resolved (S223's scope cell names S004 and excludes it) |
| w1/SwarmScribe26.md | PARTIAL | F3 no staged entry can ground the object clock or the cruft arm | resolved (entry sources are live tag bytes, L4 passes) |
| w1/SwarmScribe26.md | PARTIAL | F4 the staged package cannot be appended as-is (38 id collisions, 10 path collisions) | resolved (assimilation recorded as none; nothing staged was admitted) |
| w1/SwarmScribe26.md | PARTIAL | F5 S223 and S224 were provisional ids | open nit — the entry still says "placeholder id: the L1 renumbers by document"; the registry uses S223 |
| w1/SwarmScribe26.md | PARTIAL | F6 the M1 row's "shown able to fail" is a committed receipt, not this seat's run | resolved (receipt verified byte-identical by SwarmCritic36 and cited by the SKILL row) |
| w1/SwarmScribe27.md | PASS | F1 C3's L14 and the M1 tool disagree on wildcard tokens | open |
| w1/SwarmScribe27.md | PASS | F2 none of the three r32 counters refuses a `--scratch` inside the lane or the fleet root | open — c3-counter-v2.py:163-184 still accepts any `--scratch` |
| w1/SwarmScribe27.md | PASS | F3 the reason cell is enforced only for its word count | open |
| w1/SwarmScribe27.md | PASS | F4 the withdrawal cap is load-bearing | resolved — the cap bit: withdraw-all is refused in controls.tsv and the landed rows sit at withdrawn=17 |
| w1/SwarmScribe27.md | PASS | F5 no round-32 lesson exists yet, so motivating evidence cites r31 | open (the L1 lands the lesson after this wave) |
| w1/SwarmScribe27.md | PASS | F6 the probe row was drafted ahead of its fixture | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (SKILL.md:253 matches the landed fixture's 22 lines and refusals) |
| w1/SwarmScribe27.md | PASS | F7 both drafted blocks avoid literal pipes in cells | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (rows parse) |
| w1/SwarmScribe28.md | PASS | F1 C3's disclosed base is a class; the committed control is a number | resolved (the control row is used: `legs=14 fail=13 f1_entries=4`) |
| w1/SwarmScribe28.md | PASS | F2 the C1 target is a conjunction; keep all five SUMMARY fields and both instruments | resolved — both v1 and v2 read unbound=6 mismatches=6 at the tip, so neither can be pasted as a pass |
| w1/SwarmScribe28.md | PASS | F3 the counters default `--scratch` outside TMPDIR but inside the permitted root | open (unchanged; outside C2's frozen set) |
| w1/SwarmScribe28.md | PASS | F4 the M1 receipt mixes two line-number bases (BAD line = file line, lines= = prefixed lines) | open (tool unchanged) |
| w1/SwarmScribe28.md | PASS | F5 one untracked lane file, census/round-32/measure.sh | resolved@a92e1aae91dbf46c2d7eff713932cfc820186970 (committed) |

Row count: 157 over the 20 assigned reports (Critic33 16, Critic34 8, Critic35 6, Critic36 6, Critic37 6, Reviewer32 5,
Mut38 12, Mut39 6, Connector41 7, Connector42 7, Revenger29 11, Sentinel43 8, Simplifier44 8, Scribe22 9, Scribe23 5,
Scribe24 13, Scribe25 6, Scribe26 6, Scribe27 7, Scribe28 5).

## Findings raised by this seat while adjudicating

N1. **The landed C2 fix honours TMPDIR only when it is set.** Six of the 26 patched files keep a literal-root fallback:
`tests/fixtures/r27-pre-report-gate.sh:7` (`mktemp -d "${TMPDIR:-/tmp}/souji-r27-pre-report.XXXXXX"` — the change moved
the fallback from /var/tmp to /tmp), `tools/souji-round9-selftest.sh:7,14`, `tests/fixtures/r13-repo-structure.sh:189,232`,
`tools/souji-repo-structure.sh:266`, `tests/fixtures/r28-wave-evidence-capture.sh:51`, `tools/souji-census.sh:309`.
The r32 fixture itself is stricter (`tests/fixtures/r32-jj-mtime-clock.sh:62-63` refuses an unset or empty TMPDIR), so
the round contains both idioms. The C2 predicate always sets TMPDIR, so `fail` never sees the fallback. Landed-bytes
consequence: the claim "the lane's own tools honour TMPDIR" is true; "never a literal /var/tmp or /tmp" is not.
No target change proposed; the L1 should state which sentence its receipt claims.

N2. **T18 is defeated by C2's own repairs, not only by C3's entry.** Reproduced in a scratch clone at the tip:
`tests/fixtures/r20-input-binding.py --baseline 12516f7d…` reports `BASELINE_SUMMARY … files=66 mismatches=32` at
4e56c48 and `mismatches=26` at 85b61a1; the six added paths are `corpus/knowledge/jj-abandoned-object-mtime-clock.md`
(the C3 entry) plus `tools/souji-census.sh`, `tools/souji-cert-evidence.py`, `tools/souji-evidence-cache.py`,
`tools/souji-repo-structure.sh`, `tools/souji-round9-selftest.sh` (five files 98e5203 patched). Therefore no landing
that performs any of those five repairs can pass T18, and no C3-only remedy (excluding the entry, or exempting one
path) restores the item. `amendments.txt:26-29` already names "C2's own repairs", so this is disclosure-complete;
the operational consequence for r33 is that a pinned-baseline-diff anchor cannot sit inside the set of files the
same claim edits. Stricter-only correction: drop T18 or re-anchor it to a count that excludes the item's own files —
the L1's call, not mine.

N3. **Four of the seven committed control rows cannot be replayed from the lane repo.** `git cat-file -t` prints
MISSING for b0a0c71863ac2f86e0ba725c382abb21322eaf63 (controls.tsv:4), d4930a15551ae168be41bccc65b8b5ec8ac3bce0
(:5), bf984f0cef06b18884450a97ad0a8a7b6728f65d (:6) and 791c07258b2d71bae2295c088af2316a326e6511 (:7). Only the three
do-nothing rows resolve (their `rev` is the prereg commit). Two wave-1 seats reported the C1/C2 cases; the C3-junk rev
is the same class and was not reported. The frozen controls are evidence of gameability, not of the claim, so no
target is affected — but a hygiene lane should not commit readings whose state is unreachable. Smallest correction:
the L1's lesson or receipt states the four revs are scratch-only, or commits the states.

N4. **The M1 guard's scope is still narrower than its own contract.** `census/round-32/c3-contract.txt:3` says "Every
line of the record that starts with `prefix` must carry exactly these keys", while both parsers require a following
space (`tools/souji-record-contract.py:44`, `census/round-32/c3-counter-v2.py:93`). A `RESULT\tarm=reflog-only …` line
is in scope and invisible. This is SwarmCritic36 F1, still open at the tip; the smallest correction is
`line.split(None, 1)[0] == prefix` in both places, which flags a bare prefix line as BAD.

N5. **The entry's S002 attribution is landed unfixed.** `corpus/knowledge/jj-abandoned-object-mtime-clock.md:3` and Gate
bullets `:218-222` label `gc.cruftPacks` and `gc.pruneExpire` quotes S002, whose scope cell (`corpus/SOURCES.md:23`)
names `gc.reflogExpire`, `gc.reflogExpireUnreachable`, the two `gc.rerere*` keys and `gc.worktreePruneExpire` only; S063
now carries the CONFIGURATION anchor but the quotes are not relabelled to it. L4, L5, L6 and L11 all pass because none
compares a Gate bullet's section to its row's scope cell. This is the r31 routed defect 2 class (entry traceability)
in a new place: the round closed the S051 instance and reproduced it for the config fragment. Smallest correction,
stricter-only and counter-neutral: append the two config keys to S002's scope cell.

N6. **Two hygiene defects in the lane tree.** `census/round-32/__pycache__/c1-counter-v2.cpython-314.pyc` (31585 B,
05:31) is still present, i.e. some seat ran a counter without `-B`; gitignored, so the tree is clean, but the contract
asks for `python3 -B`. And the new entry asserts its own record's provenance by hash
(`census/round-32/records/jj-mtime-clock-run.txt`, sha256 01cf6dc0…) — the hash matches the delivered file, but the
record's own header line is the counter command, so a reader cannot tell which fixture run produced it without L9's
replay; that is disclosed by design.

## Negative results (sweeps that produced them)

- C1 v1 and v2 each read the same six unbound items (N28, N29, N30, N31, N33, N34) at the tip; the withdrawal count
  is 17 in all four readings (attempt-1 records and my two runs), so the miss is not a flake.
- C3's two counters pass at the tip with `f1_entries=5`; `L2`, `L3`, `L11` pass after C2 landed, so Critic37's A3
  coupling produced no movement.
- `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file corpus/SOURCES.md --today 2026-10-26`
  at the tip: rc 0, `file ok`, 36 W04, no E line — Simplifier44 D7 is closed by the same-commit landing.
- `git log 85b61a1..master -- tools/souji-axis-check.py tools/souji-registry-agreement.py census/round-32/c2-counter.py
  census/round-32/c2-items.tsv tools/souji-record-contract.py tools/souji-vault-verify.sh` prints nothing: those six
  instruments are byte-identical to base, so every finding that depends on them is still open by construction.
