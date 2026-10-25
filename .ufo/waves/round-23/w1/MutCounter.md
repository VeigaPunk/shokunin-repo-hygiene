# MutCounter — C1 instrument mutant design (round 23, w1)

## Status

STATUS: PARTIAL — 54 clause mutants designed for `tools/souji-record-agreement.py` (sha256
`617f4c9618c06254…`, 350 lines; anchors verified against `66ee7ecf…` and spot-checked at the current
bytes); 12 have a killing case the fixture contract mandates, 13 are killed only if the fixture
carries content the contract does not mandate, 1 is behaviourally equivalent, and **28 have no
killing case** (`uncovered=28`). The two strongest anti-gaming guards the instrument now carries —
`receipt-unbound` (a receipt must bind a tool digest) and `exemption-not-allowed` (an exemption must
name a frozen operator path) — both sit in the uncovered set, so the fixture as specified cannot tell
whether either exists (A12).

## Evidence

Contract read: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-23/preregistration.txt`
(K1-K4, lines 12-52) and
`/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-22-verifier-spotcheck.md` §6
(D1-D8). Lane base `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`.

Fixture contract read from `.ufo/waves/round-23/w1-spec.json` item `ExecFixtureAgreement`. The 9
cases: (1) repaired repo → exit 0 / mismatches=0; (2) receipt file absent → ≥1 K1 mismatch;
(3) SCORECARD counts disagree with the receipt → K1 value-disagree; (4) line revision token differs
from the receipt's `rev=` → K1 rev-disagree; (5) uncorrected superseded 4-tuple in LOG → K2;
(6) filed LOG occurrence deleted → K2 filed-bytes-missing; (7) wrong `<n> present` tally in README →
K3; (8) unexempted dirty path → K4; (9) exempted operator path → NOT a mismatch.

**The instrument moved six times while this seat was reading it**, and every move but the first
changed a clause. All states are recorded because the fixture must be pinned to one, and because two
of the moves are undeclared contract changes (A5, A10):

```
05:08  303 lines  (first read) K1 compared rev == self.rev
05:11  327 lines  7515bb29…   K1 header check -> presence-only; K2 receipt -> -before-final
05:16  333 lines  f9ec0091…   K1 rev arm rewritten (inverted); TALLY_RE gained \s+ and \*{0,2}
05:18  333 lines  e41db304…   K4 source replaced; uncommitted: prefix gate deleted
05:22  350 lines  66ee7ecf…   K1 receipt-unbound + rev arm repaired; K2_FILED retention;
                              K4_ALLOWED allowlist replaces the prefix gate
now    350 lines  617f4c9618c06254…  K1 binds a tuple to the nearest preceding 40-hex token
```

This seat's design targets the current bytes. If the L1 lands another edit before the fixture runs,
re-pin the digest and re-verify the anchor map at the end of this file — the clause text in each row
is the durable key.

```
$ python3 - (tally_of variants over census/round-22/attempt2/slice-verdicts.tsv)
cell[1]-only: {'accepted': 5, 'present': 2, 'unverifiable': 1, 'refused': 0}
any-cell   : {'accepted': 0, 'present': 0, 'unverifiable': 0, 'refused': 0}

$ python3 - (LOG.md section scan)
section lines 1469 -> 1522 len 53
4-tuples in section: 0          # COUNTS_RE finds none per physical line
tally hits in section: 4        # 5 accepted, 1 present, 1 refused, 1 unverifiable
superseded-by lines in section: []      AFTER section: 0
4-tuples AFTER section: 0               tally hits AFTER section: 0

$ sed -n '1485,1489p' LOG.md
`--rev 4edb25d --file SCORECARD.md` -> assertions=56 resolved=53
skipped=33 mismatches=3 (receipt census/round-22/attempt2/
declared-evidence-before.tsv).

$ grep -nE 'assertions=[0-9]+ resolved=' census/round-22/attempt2/declared-evidence-before*.tsv
declared-evidence-before.tsv:57:assertions=56 resolved=53 skipped=33 mismatches=3
declared-evidence-before-final.tsv:56:assertions=55 resolved=52 skipped=33 mismatches=3
$ grep -nE '^rev=' census/round-22/attempt2/declared-evidence-before*.tsv   # neither has one

$ grep -nE '\*\*[0-9]+ (accepted|present|unverifiable|refused)' corpus/README.md corpus/lessons/round-22.md
corpus/lessons/round-22.md:355:empty body; unreachable is not fabrication), **0 refused**.
$ grep -nE '[0-9]+ (accepted|present|unverifiable|refused)' corpus/README.md corpus/lessons/round-22.md
corpus/README.md:440:5 accepted with corrected quotes, 2 present, 0 refused, 1 unverifiable
corpus/README.md:443:sentence said "1 present, 1 refused (wrong-source citation)" until r23; the
```

Five facts the predictions depend on:

1. The live LOG's only 4-tuple is **wrapped across two physical lines** (`assertions=56 resolved=53`
   then `skipped=33 mismatches=3`), so `paragraphs()` (L64-82) is load-bearing on live bytes.
2. That section's 4 tally hits are `5 accepted`, `1 present`, `1 refused`, `1 unverifiable` against a
   true tally of 5/2/0/1 — so **K2's live teeth today are entirely in the tally arm (L226): two stale
   occurrences. The fixture's case 5 tests the 4-tuple arm instead.**
3. The wrapped `56/53` agrees with `declared-evidence-before.tsv` and disagrees with
   `declared-evidence-before-final.tsv`; the tool reads `-final` (L49) while the prereg's K2 names the
   plain file (Attack A5).
4. Neither before-receipt carries a `rev=` header, and `corpus/lessons/round-22.md:355` carries the
   tally in **bold** — the only reason `TALLY_RE`'s `\*{0,2}` (L61) exists (Attack A9).
5. `corpus/README.md:443` quotes a superseded `1 present, 1 refused` inside prose — a stale-looking
   tally that K3 (L257) will flag unless the correction wording keeps it out of TALLY_RE's reach.

The K1 and K4 inputs materialised at 05:18-05:19 while I was reading:

```
$ cat census/round-23/records/declared-evidence-after.tsv
rev=9301d98c1c689c79741f0f1ba1f171138d20af07
tool_sha256=65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4
--- stdout ---
assertions=63 resolved=63 skipped=40 mismatches=0
$ cat -A census/round-23/records/uncommitted-exemptions.tsv
census/operator-sweep-20261019/^Ioperator-owned untracked output (L0 souji | round-17); …
```

So K1's real input now carries a header (`rev=9301d98…`) and a counts line that matches
`SCORECARD.md:14` — the tip state is K1-green by inspection — and K4's real input is a **new** file
with no `uncommitted:` prefix, which is not the file the preregistration freezes (A10).

No tool installs were needed (pacman paused host-wide; nothing required).

## Findings

### 1. Clause inventory — 32 clauses → 54 mutants

L-refs inside the rows are indicative; the verified anchor map at the end is authoritative.

K1 (L139-181): receipt exists at rev (141) · receipt well-formedness (145) · receipt tool_sha256
binding (148-150) · `rev=` header presence (152-155) · record exists (158) · r22/round-22 scope
filter (160) · nearest-preceding-token binding (59, 165-166) · counts-line equality (170) ·
rev-disagree arm (173-176) · per-record occurrence presence (178).
K2 (L184-254): counts-receipt selection (50) · counts-receipt existence (187) · tally-receipt
existence (189) · receipt well-formedness (192) · record existence (199) · section detection (208) ·
header-underline handling (212-214) · section end bound (215-217) · paragraph grouping (67-85, 221) ·
4-tuple staleness (227) · tally staleness (233) · correction-marker presence (237-243) · correction
must name the occurrence (239) · correction window width (238) · correction position is later (240) ·
K2_FILED retention (245-249) · filed-occurrence join (245) · found==0 backstop (250).
K3 (L256-275): record existence (261) · tally regex markdown tolerance (63) · tally regex whitespace
width (63) · tally column restriction (120) · comment skip (117) · per-class tally equality (269) ·
per-class occurrence presence (272).
K4 (L277-302): worktree gate (278) · status-failed (295) · porcelain field offset (298) · exemption
source selection (57, `census/round-23/records/uncommitted-exemptions.tsv`) · exemption allowlist
(58, `K4_ALLOWED`) · allowlist enforcement (288-291) · blank/comment skip (283) · exemption tab split
(285) · exemption path match (301) · empty-path guard (286).
Emit/CLI (L305-327): counts-line reflects rows (307-308) · exit-code mapping (316) · `--rev` 40-hex
guard (321) · `--json` parity (312-315).

### 2. Mutant rows

```
mutant=M01|clause=K1 receipt exists at rev (L138)|killed-by-case=2|predicted=if text is None -> if False; counts_of(None) raises TypeError, no counts line is printed, case 2 loses its K1 row entirely|verdict=KILLED
mutant=M02|clause=K1 absent-receipt class identity (L138-140)|killed-by-case=none|predicted=read_at(...) or "" downgrades receipt-absent to receipt-malformed; case 2 asserts only >=1 K1 mismatch so it still passes and the class string is never pinned|verdict=UNCOVERED
mutant=M03|clause=K1 counts-line equality (L164)|killed-by-case=3|predicted=if m.group(0) != value -> if False; a disagreeing SCORECARD tuple emits no value-disagree row, case 3 sees mismatches=0|verdict=KILLED
mutant=M04|clause=K1 rev-disagree arm (L172-175)|killed-by-case=4|predicted=delete the elif arm so a line quoting the after-value against a different revision emits nothing; seen stays 0 so the only row is occurrence-absent and case 4's class assertion fails; the arm was inverted in the 333-line bytes and repaired here (A8)|verdict=KILLED
mutant=M05|clause=K1 rev= header presence (L147-150)|killed-by-case=none|predicted=if not rev -> if False; a headerless receipt then makes rev="" so L168's not-rev arm flags every in-scope tuple instead of emitting receipt-rev-absent; no case feeds a headerless receipt (both live r22 receipts are headerless, so this is the natural fixture mistake)|verdict=UNCOVERED
mutant=M06|clause=K1 receipt well-formedness (L142)|killed-by-case=none|predicted=delete receipt-malformed; no case keeps the receipt file while stripping its counts line|verdict=UNCOVERED
mutant=M07|clause=K1 record existence (L152)|killed-by-case=none|predicted=delete record-absent; no case deletes SCORECARD.md from the fixture repo|verdict=UNCOVERED
mutant=M08|clause=K1 r22/round-22 scope filter (L157)|killed-by-case=1|predicted=if not K1_SCOPE.search(line) -> if False makes every counts tuple in SCORECARD in-scope, so a non-r22 tuple becomes value-disagree or rev-disagree and case 1 breaks — only if the fixture's case-1 SCORECARD carries an out-of-scope tuple, which the contract does not require|verdict=CONDITIONAL
mutant=M09|clause=K1 per-record occurrence presence (L170)|killed-by-case=none|predicted=delete the seen==0 branch; no case leaves the record with zero rev-bound tuples (case 4 does, and case 4 asserts rev-disagree rather than this class)|verdict=UNCOVERED
mutant=M10|clause=K2 found==0 backstop (L253)|killed-by-case=none|predicted=if found == 0 -> if False is now redundant: the K2_FILED retention loop pins the three filed strings independently, so deleting the backstop still catches a deleted 4-tuple and case 6 stays green on the mutant|verdict=UNCOVERED
mutant=M11|clause=K2 correction-marker presence (L235)|killed-by-case=5|predicted=if not later -> if False treats every stale occurrence as corrected, case 5's uncorrected tuple emits no row|verdict=KILLED
mutant=M12|clause=K2 correction position is later (L233)|killed-by-case=none|predicted=range(start_line, len(lines)) -> range(0, len(lines)) lets a marker that precedes the occurrence satisfy the clause; case 5 has no marker for its tuple either way, so it survives|verdict=UNCOVERED
mutant=M13|clause=K2 correction must name the occurrence (L232)|killed-by-case=none|predicted=drop the occ-in-window conjunct so any later marker masks every stale scalar; case 5 still has no marker at all, so it survives|verdict=UNCOVERED
mutant=M14|clause=K2 correction window width (L231)|killed-by-case=1|predicted=lines[k:k+6] -> lines[k] misses a correction whose named tuple sits on a wrapped continuation line, emitting a false uncorrected row and breaking case 1 — only if the fixture's correction line wraps as the live LOG's tuple does|verdict=CONDITIONAL
mutant=M15|clause=K2 paragraph grouping (L64-82, L214)|killed-by-case=5|predicted=paragraphs(...) -> per-physical-line tuples splits a wrapped 4-tuple so it is never checked and case 5's stale tuple goes unseen; the live LOG wraps its only 4-tuple across two lines, so this is the realistic shape — but the fixture LOG's wrapping is not mandated|verdict=CONDITIONAL
mutant=M16|clause=K2 counts-receipt existence (L179)|killed-by-case=none|predicted=delete receipt-absent for the before-receipt; case 2 removes the K1 after-receipt only (its class is K1)|verdict=UNCOVERED
mutant=M17|clause=K2 tally-receipt existence (L181)|killed-by-case=none|predicted=delete receipt-absent for slice-verdicts.tsv; no case removes that file|verdict=UNCOVERED
mutant=M18|clause=K2 receipt well-formedness (L184)|killed-by-case=none|predicted=delete receipt-malformed; no case strips the counts line from the before-receipt|verdict=UNCOVERED
mutant=M19|clause=K2 want_counts truthiness guard (L220)|killed-by-case=none|predicted=drop the want_counts conjunct so a missing before-receipt marks every 4-tuple stale; no case removes that receipt, so it survives|verdict=UNCOVERED
mutant=M20|clause=K2 record existence (L192)|killed-by-case=none|predicted=delete record-absent for LOG.md; no case deletes LOG.md|verdict=UNCOVERED
mutant=M21|clause=K2 section detection (L201)|killed-by-case=none|predicted=delete section-absent; no case removes the Round22 attempt2 heading|verdict=UNCOVERED
mutant=M22|clause=K2 header-underline handling (L205-207)|killed-by-case=1|predicted=drop the underline skip so the section ends at its own underline, found stays 0 and filed-occurrence-missing fires; case 1 can no longer reach mismatches=0|verdict=KILLED
mutant=M23|clause=K2 section end bound (L208-210)|killed-by-case=6|predicted=end = len(lines) counts scalars outside the section so case 6's filed-occurrence-missing stops firing — only if the fixture LOG carries a scalar after the section (the live LOG carries none)|verdict=CONDITIONAL
mutant=M24|clause=K2 tally staleness (L226)|killed-by-case=none|predicted=if n != want_tally.get(cls,0) -> if False deletes the arm that carries K2's entire live signal (2 stale tallies: 1 present, 1 refused); case 5 tests the 4-tuple arm only, so the mutant survives every case|verdict=UNCOVERED
mutant=M25|clause=K3 per-class tally equality (L257)|killed-by-case=7|predicted=if n != want_tally.get(cls,0) -> if False; a wrong "<n> present" emits no tally-disagree row, case 7 sees mismatches=0|verdict=KILLED
mutant=M26|clause=K3 per-class occurrence presence (L260)|killed-by-case=none|predicted=delete class-absent; no case removes all occurrences of a class, so a record that silently drops a class stays green|verdict=UNCOVERED
mutant=M27|clause=K3 record existence (L249)|killed-by-case=none|predicted=delete record-absent; no case deletes corpus/README.md or corpus/lessons/round-22.md|verdict=UNCOVERED
mutant=M28|clause=K3 tally column restriction (L117)|killed-by-case=none|predicted=count any cell naming a class instead of cells[1]; on the real receipt the tally collapses from 5/2/1/0 to 0/0/0/0, but the fixture receipt shape is unmandated so no case is guaranteed to expose it|verdict=UNCOVERED
mutant=M29|clause=K3 comment-line skip (L114)|killed-by-case=none|predicted=drop the "#" skip; the live header carries no number+class pair and the fixture receipt is unmandated, so the tally is unchanged|verdict=UNCOVERED
mutant=M30|clause=K4 worktree gate (L265)|killed-by-case=8|predicted=if not self.worktree -> if True skips K4 unconditionally, so the unexempted dirty path emits no row and case 8 sees mismatches=0|verdict=KILLED
mutant=M31|clause=K4 status-failed (L278)|killed-by-case=none|predicted=delete status-failed; git status succeeds in every fixture case|verdict=UNCOVERED
mutant=M32|clause=K4 uncommitted path accounting (L285)|killed-by-case=8|predicted=delete the per-path bad() emission; case 8's dirty path produces no mismatch row|verdict=KILLED
mutant=M33|clause=K4 porcelain field offset (L281)|killed-by-case=9|predicted=line[3:].strip() -> line.strip() prefixes the path with its status code, so the exemption comparison fails and case 9's operator path is flagged|verdict=KILLED
mutant=M34|clause=K4 exemption prefix gate (L58)|killed-by-case=none|predicted=the frozen predicate requires uncommitted:-prefixed rows; the shipped bytes replace that gate with the K4_ALLOWED path set, so the mutant that deletes the prefix is identical to the baseline and cannot be scored; the allowlist is stronger than the prefix, so this is a declared deviation rather than a hole (A10)|verdict=UNCOVERED
mutant=M35|clause=K4 exemption tab split (L273)|killed-by-case=9|predicted=drop .split("\t")[0] so the reason column joins the path and the match fails; every live exemption row carries a tab+reason, but the fixture row's shape is unmandated|verdict=CONDITIONAL
mutant=M36|clause=K4 exemption path match (L284)|killed-by-case=9|predicted=path == e or path.startswith(...) -> path == e drops directory exemptions; the live file exempts census/operator-sweep-20261019/ as a directory, but case 9 may name a plain file|verdict=CONDITIONAL
mutant=M37|clause=K4 empty-path guard (L274)|killed-by-case=none|predicted=if path -> if True appends an empty exemption, which only ever matches absolute status paths (porcelain paths are relative), so behaviour is unchanged in every case|verdict=UNCOVERED
mutant=M38|clause=exit-code mapping (L299) always-zero direction|killed-by-case=2|predicted=return 0 if not self.rows else 1 -> return 0; cases 2-8 must observe rc!=0 — only if the fixture records the tool's rc per case, which the contract implies only through the counts line|verdict=CONDITIONAL
mutant=M39|clause=exit-code mapping (L299) always-one direction|killed-by-case=1|predicted=return 0 if not self.rows else 1 -> return 1; case 1 must observe rc==0 — same per-case rc dependency|verdict=CONDITIONAL
mutant=M40|clause=counts-line reflects rows (L291-292)|killed-by-case=2|predicted=hardcode mismatches=0 in the printed line while returning rc from rows; case 2 reads mismatches=0 and fails, and the always-zero control stops being rejected|verdict=KILLED
mutant=M41|clause=--rev 40-hex guard (L304)|killed-by-case=none|predicted=delete the fullmatch guard; every fixture case passes a valid 40-hex rev, so a short or symbolic rev is never refused|verdict=UNCOVERED
mutant=M42|clause=--json parity (L296-298)|killed-by-case=none|predicted=emit an empty mismatches list in the JSON payload; no case reads --json, so a receipt consumer would silently see zero rows|verdict=UNCOVERED
mutant=M43|clause=K2 counts-receipt selection (L49)|killed-by-case=5|predicted=point K2 at declared-evidence-before.tsv (the file the prereg names) instead of declared-evidence-before-final.tsv; the D5 tuple assertions=56 resolved=53 then agrees with the receipt and stops being stale, so case 5 emits no row — only if the fixture's case-5 tuple is the D5 56/53 value|verdict=CONDITIONAL
mutant=M44|clause=K3 tally regex markdown tolerance (L61)|killed-by-case=1|predicted=drop the two \*{0,2} groups so a bold tally is invisible; the live lesson carries its refused count only as **0 refused**, so a bold-only class loses its occurrence — only if the fixture writes any tally in bold (the live shape) and no case pins the occurrences= total|verdict=CONDITIONAL
mutant=M45|clause=K3 tally regex whitespace width (L61)|killed-by-case=none|predicted=\s+ -> a single space so a tab-separated or double-spaced tally is missed; live records use single spaces and the fixture shape is unmandated, so it survives|verdict=UNCOVERED
mutant=M46|clause=K4 exemption source selection (L58)|killed-by-case=9|predicted=restore the frozen source corpus/pointer-exemptions.tsv with the uncommitted: prefix; the fixture then exempts through a file the tool no longer reads (or vice versa) and case 9's operator path is flagged — the direction depends on which shape the fixture author wrote, which is the coordination risk named in A11|verdict=CONDITIONAL
mutant=M47|clause=K4 blank/comment skip (L283)|killed-by-case=none|predicted=delete the skip so a blank or #-comment row appends its first tab-field as an exemption; no case puts a comment or blank line in the exemption file, and a comment's first field can never equal a status path|verdict=UNCOVERED
mutant=M48|clause=K2 K2_FILED retention (L247-251)|killed-by-case=6|predicted=delete the loop that requires assertions=56 resolved=53 skipped=33 mismatches=3, 1 present and 1 refused to survive in the section; deleting the filed occurrence then leaves found>0 from the remaining tallies, no mismatch is emitted and case 6 sees mismatches=0|verdict=KILLED
mutant=M49|clause=K4 exemption allowlist (L288-291)|killed-by-case=none|predicted=delete the path-not-in-K4_ALLOWED check so any row of the exemption file exempts whatever it names; case 9 exempts the operator path, which is allowed, so it passes either way and the tool's strongest anti-gaming guard is never exercised (widening K4_ALLOWED itself is the same mutant with the constant edited)|verdict=UNCOVERED
mutant=M51|clause=K1 receipt tool_sha256 binding (L149-151)|killed-by-case=none|predicted=delete the receipt-unbound check so a hand-written counts line with no tool_sha256= header is accepted as a receipt; no case writes a headerless synthetic receipt, so the direct counter to the write-it-by-hand attack is never exercised|verdict=UNCOVERED
mutant=M52|clause=K2 filed-occurrence join (L245)|killed-by-case=1|predicted=" ".join -> "\n".join stops matching the wrapped filed 4-tuple, so the tip emits a false filed-occurrence-missing and case 1 cannot reach mismatches=0 — only if the fixture LOG wraps its filed tuple as the live LOG does|verdict=CONDITIONAL
mutant=M53|clause=K1 nearest-preceding-token binding (L165-166)|killed-by-case=1|predicted=before[-1] -> "" (or delete the binding) leaves every tuple bound to nothing, so the correct tip tuple falls into the rev-disagree arm and case 1 sees a mismatch on a repaired repo|verdict=KILLED
mutant=M54|clause=K1 nearest vs first preceding token (L166)|killed-by-case=1|predicted=before[-1] -> before[0] binds a two-token line's second tuple to the first revision, so the tip tuple is judged against the base rev and case 1 breaks — only if the fixture SCORECARD line quotes both ends on one physical line as the live line does|verdict=CONDITIONAL
mutant=M55|clause=K1 rev-disagree guard conjunct (L173)|killed-by-case=none|predicted=drop "and bound != rev" so the arm fires for any tuple equal to the receipt value; the if-branch already consumed bound == rev, so the conjunct is unreachable-false and the mutant is behaviourally identical — a redundant condition, not a coverage gap|verdict=EQUIVALENT
```

uncovered=28
conditional=13
killed=12
equivalent=1
total=54

### 3. The gap, stated plainly

`uncovered=28` of 54. The ten clauses the round's own contract names score as follows: receipt
exists at rev — killed (M01) but its class is not pinned (M02); counts-line equality — killed (M03);
rev token equality — killed (M04) only after the A8 repair, so the fixture must run against bytes that
carry it; filed-occurrence
retention — killed (M48), with the found==0 backstop now redundant (M10); correction-line coverage —
killed only in the marker-presence form (M11),
with position (M12), occurrence-naming (M13) and window width (M14) uncovered or conditional;
per-class tally equality — killed (M25); per-class occurrence presence — **uncovered** (M26);
uncommitted path accounting — killed (M30, M32); exemption parsing — the allowlist clause that
replaces the frozen prefix gate is **uncovered** (M49), source selection is conditional (M46), and
only tab split (M35) and directory match (M36) remain as conditional kills; exit-code mapping —
conditional only (M38, M39).

Highest-value closures, each a one-line fixture change:

1. **M24 — the fixture tests the arm that is vacuous on live bytes.** Measured: the live LOG section
   holds 0 per-line 4-tuples and 4 tallies, 2 of them stale. Case 5 pins the 4-tuple arm only. Add
   case 5b: a stale `<n> <class>` tally inside the section with no `superseded by` line.
2. **M15/M14 — make case 5's stale tuple wrapped across two physical lines** and its correction wrap
   too, exactly as the live LOG wraps `assertions=56 resolved=53` / `skipped=33 mismatches=3`.
3. **M02 — case 2 must assert the class string**, not just `>=1 K1 mismatch`.
4. **M38/M39 — record the tool's rc per case**; the counts line alone cannot kill the exit-code
   mutant, which is the clause that makes `M==0` mean anything.
5. **M44 — write one tally in bold** in the fixture record, and assert `occurrences=` so regex width
   and markdown tolerance are both pinned.
6. **M26 — add a case that removes every `refused` occurrence** from both K3 records.
7. **M05 — add a case whose receipt has no `rev=` header**; it is the natural fixture mistake and the
   only input that distinguishes `receipt-rev-absent` from a blanket rev-disagree.
8. **M08 — give case 1's SCORECARD a non-r22 counts tuple** (a stale r21 row), so the scope filter is
   load-bearing.
9. **M46 — agree the K4 exemption shape with the fixture before either lands.** The tool reads
   `census/round-23/records/uncommitted-exemptions.tsv` with no prefix; the prereg freezes
   `corpus/pointer-exemptions.tsv` with `uncommitted:` rows. Case 9 is green on the baseline only if
   the fixture writes the tool's shape, and the mutant is unscorable if it does not. This is a
   two-line fixture/tool agreement, not a coverage preference.
10. **M53/M54 — quote both ends on one SCORECARD line** (as the live line does: `base 4edb25d…
    assertions=55…; tip 9301d98… assertions=63…`). M53 is killed by case 1 already; M54 needs the
    two-token line to prove the *nearest* token, not the first, is the binding.
11. Cheap negatives that close one clause each: absent `--rev` short form (M41), `--json` cross-check
   (M42), a receipt with no counts line (M06/M18), a deleted record (M07/M20/M27), an
   occurrence-free record (M09), a deleted K2 receipt (M16/M17), a missing section (M21), a scalar
   after the section (M23), a comment line carrying `3 accepted` (M29), a blank and a `#` row in the
   exemption file (M47).

## Attack log

- **A8 — the `rev-disagree` branch was inverted for one edit window; it is repaired in the current
  bytes and M04 is scorable again.** The 333-line bytes read `elif rev in m.group(0) or not rev:`:
  for case 4's input (an in-scope SCORECARD line carrying a counts tuple and naming a different
  revision token) the first arm is False and `not rev` is False, so no row was emitted and the only
  observable was `occurrence-absent` — case 4 would have failed on the baseline. The current bytes
  read `elif m.group(0) == value:` (L173), which fires exactly for the after-value quoted against
  another revision, i.e. D2's own shape, and case 4's class assertion now holds. Recorded because the
  fixture must be run against bytes that carry the repair, and because the intermediate state proves
  the case-4 assertion is load-bearing. Read, not executed.
- **A12 — the two guards that close the gaming attacks have no killing case.** `receipt-unbound`
  (L148-150) refuses a receipt with no `tool_sha256=` header — the direct counter to
  CritC1Gameable's "point K1 at a receipt the author writes by hand" — and `exemption-not-allowed`
  (L288-291) refuses an exemption row outside `K4_ALLOWED` — the direct counter to "declare a giant
  exemption list". Mutants M51 and M49 delete each in one line, and neither is killed by any of the
  nine cases: case 9 exempts the operator path (allowed either way), and no case writes a receipt
  without a digest header. The fixture must add (a) a case whose K1 receipt is a bare counts line and
  (b) a case whose exemption file names a non-operator path that is then dirtied, or the round's two
  strongest anti-gaming clauses ship untested.
- **A5 — the frozen K2 receipt name and the shipped K2 receipt disagree, and the shipped one is what
  gives K2 its teeth.** Prereg K2 compares against `census/round-22/attempt2/declared-evidence-before.tsv`;
  the tool reads `declared-evidence-before-final.tsv` (L49). Measured: the plain file's counts line is
  `assertions=56 resolved=53 skipped=33 mismatches=3` — exactly the tuple D5 calls superseded — so
  under the prereg's literal name K2 finds that occurrence in agreement and demands no correction for
  it; `-final` is `55/52`, which makes it stale and does demand one. As frozen, K2 cannot catch the
  occurrence D5 routes. Either the prereg's K2 receipt name is corrected in the round record as a
  declared pre-data contract change, or K2's 4-tuple arm is vacuous on the D5 number. I edited
  neither file.
- **A6 — K1's header clause was replaced, not merely relaxed, and nothing now binds the receipt header
  to `--rev`.** The 327-line bytes required `rev == self.rev`; the current bytes require only that a
  header exist (L146-149), with the comment that a receipt cannot name the commit containing it. The
  self-reference argument is sound (an after-receipt is committed inside the revision it measures) and
  the new form matches prereg K1's literal wording. But an author can pair a receipt whose header names
  any old commit with a SCORECARD line naming that same commit and K1 goes green while the after-state
  is bound to nothing — the CritC1Gameable "receipt the author writes by hand" attack, unclosed by the
  frozen predicate.
- **A7 — `rev=""` collapses the rev clause into a blanket flag.** With no header, L173's
  `elif m.group(0) == value` arm can never fire (nothing to compare) and `seen` never increments, so a
  headerless receipt yields one `occurrence-absent` for the whole record rather than one
  `receipt-rev-absent` plus per-line detail. The guard at L152 is the only thing keeping that legible.
- **A10 — K4's exemption source and gate were replaced; the gate got stronger, the source still
  deviates.** Prereg K4 freezes "corpus/pointer-exemptions.tsv rows prefixed `uncommitted:`
  (operator-owned paths only)". The current bytes read
  `census/round-23/records/uncommitted-exemptions.tsv` (L57) and enforce membership in
  `K4_ALLOWED = {"census/operator-sweep-20261019/"}` (L58, L288-291) instead of the prefix. The
  allowlist is strictly stronger than a prefix — it names the paths rather than a marker — so the
  CritC1Gameable "declare a giant exemption list" attack is closed *in code*, and A12 notes the price:
  the closing clause is untested by the fixture. What remains is the source deviation: the frozen
  sentence describes a file the tool no longer reads, so the round record must declare it or the
  fixture will be written against the wrong file (A11).
- **A11 — cases 4 and 9 can go red on the baseline for reasons no mutant explains.** A8's inversion
  did that to case 4 for one edit window (now repaired); A10 still moves the exemption source. If
  `ExecFixtureAgreement` wrote case 9 against the
  *preregistration's* file and prefix, the shipped tool never reads it and case 9 fails on the
  baseline; if it wrote the tool's shape, the prereg-shaped mutant (M46) is what fails. Two seats are
  writing the two halves of one contract in parallel with no shared pin. Fix before either lands: the
  fixture must import the tool's `K4_EXEMPT_FILE` rather than hard-code a path, and the L1 must record
  the deviation from the frozen K4 wording. The same applies to K1: the after-receipt now exists with
  `rev=9301d98…` and `assertions=63 resolved=63 skipped=40 mismatches=0`, so case 1's synthetic
  receipt must reproduce that shape (header plus counts line) or K1's header clause is untested there.
- **A1 — the frozen "LATER" ordering is already weaker in shipped bytes than in the preregistration.**
  Prereg K2 requires the correction be named by a "LATER LOG.md line"; L233 scans
  `range(start_line, len(lines))` from the occurrence's own paragraph first line, and L230-232 accept a
  marker anywhere in a 6-line window. A `superseded by` line placed *above* the stale tuple in the same
  paragraph satisfies the predicate. One-line fix that does not touch the target:
  `range(start_line + 1, len(lines))` with the marker anchored below the occurrence's own line.
- **A2 — mirror defect, over-strict:** the 6-line window (L231) reads a correction whose named span
  wraps past 5 lines as uncorrected, producing a false mismatch. False-red, not a gameable green, but
  the round must reach M=0 honestly.
- **A9 — `corpus/README.md:443` quotes a superseded tally in prose** (`"1 present, 1 refused
  (wrong-source citation)"`). TALLY_RE (L61) matches it, so unless the round-23 correction keeps that
  quoted form out of reach (or the receipt genuinely agrees), K3 will report it as a stale occurrence
  and case 1's repair must account for it. Flagged because the round's own D4 sweep edits that
  paragraph.
- **A3 — the `--json` payload is an unverified second emitter:** `mismatches` is serialised from
  `self.rows` (L296-298) and no case reads it, so a receipt consumer sees a surface no case pins.
- **A4 — K4's exemption file is read at `--rev`**, so a working-tree exemption is invisible; case 9's
  operator path must therefore be exempted by committed bytes or it tests nothing. Measured: the
  exemption file exists in the working tree at 05:19 and is not yet committed, so a run at `--rev`
  before the commit would report the operator sweep as an uncommitted path.

## Anchor map (verified against sha256 `66ee7ecf…`, 350 lines)

Every row above cites a line from this table; the clause text in the row is authoritative if the
bytes move again. This map is re-verified, so where a row's own L-ref lags the file, the map wins.

```
M43       L50  K2_RECEIPT
M46       L57  K4_EXEMPT_FILE
M34       L58  K4_ALLOWED (supersedes the frozen uncommitted: prefix)
M44 M45   L63  TALLY_RE
M29       L117 if line.startswith("#")
M28       L120 cells[1].strip() in tally
M01 M02   L141 if text is None
M06       L145 if parsed is None
M51       L148-150 RECEIPT_TOOL_RE / receipt-unbound
M05       L152-155 if not rev / receipt-rev-absent
M07       L158 if body is None (K1)
M08       L160 K1_SCOPE.search
M53 M54   L59 L165-166 REV_TOKEN_RE / before[-1]
M03       L170 m.group(0) != value
M04 M55   L173-176 elif m.group(0) == value and bound != rev / rev-disagree
M09       L178 if seen == 0
M16       L187 counts_text is None
M17       L189 tally_text is None
M18       L192 parsed is None (K2)
M20       L199 if body is None (K2)
M21       L208 if start is None
M22       L212-214 body_start += 1
M23       L215-217 end / section-end scan
M15       L221 paras = paragraphs(...)
M19       L227 want_counts and ...
M24       L233 tally staleness arm (K2)
M11-M14   L237-243 later = any(...) / range(start_line, ...)
M48 M52   L245-249 section_text join / K2_FILED retention
M10       L250 if found == 0
M27       L261 if body is None (K3)
M25       L269 n != want_tally.get(cls, 0) (K3)
M26       L272 missing = sorted(...)
M30       L278 if not self.worktree
M47       L283 blank / #-comment skip
M35       L285 line.split("\t")[0]
M37       L286 if path
M49       L288-291 path not in K4_ALLOWED / exemption-not-allowed
M31       L295 status-failed
M33       L298 line[3:]
M36       L301 any(path == e or ...)
M32       L303 self.bad("K4", path, ...)
M40       L307-308 counts line
M42       L312-315 --json payload
M38 M39   L316 return 0 if not self.rows else 1
M41       L321 re.fullmatch(r"[0-9a-f]{40}", rev)
```
