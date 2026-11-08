# S90Reviewer2 — Amendment-59 wording falsification, souji r90

Seat: reviewer (attack), lane `souji-shokunin`, wave `.ufo/waves/round-90/w1`.
Measured at lane HEAD `fd25bfc5430cf27c1af5e4c8b8f6d5899e91a20f` (F), lane base
`bd760432df2cc3ba6c5f1ccc540b050fe2ac09e2`. No git/jj mutation was run; every git call was
read-only. Scratch `/fast/scratch/hyaku/souji-r90/S90Reviewer2` was deleted after the receipts
were copied to this seat. Receipts: `.ufo/waves/round-90/w1/S90Reviewer2/receipts/`.

## Verdict

**C1 verifies as stated on my own run.** The r89 sole survivor is `m17c-no-malformed` and nothing
else (`killed_r89=15`, 16 mutants); LD2b is the only r90 row that goes red for m17c and the only
mutant LD2b kills; the population is the r89 57 rows byte-for-byte plus LD2b; the r87 counter is
byte-unchanged; the target reads `killed_r89=15 killed_r90=16 killed_total=31` with both pristine
arms green and EXIT 0; the do-nothing control reads `killed_r89=15`, m17c alive, EXIT 0; the
mechanism is reproduced directly (`LEDGER-REFUSED id=ZZ9` + rc 1 for pristine; IndexError with no
marker for m17c; LD2b green for m17 and m17b). Two C1 wording-precision notes are neutral
(members-vs-file identity; "population and its harness" when the battery also changed).

**C2's numbers verify, and one sentence is falsified at its cell-level reading.** The fixture reads
`SUMMARY cases=12 tool_pass=12 before_pass=10` (EXIT 0); the control reads `tool_pass=10
before_pass=10` (EXIT 1); the r87 12-row K4 counter reads `rows=12 mismatches=0 errors=0`
(EXIT 0); `_one_line` is gone (0 definitions/calls; the r89 before tool had exactly one
occurrence, the definition). But "the CHARACTER U+0085 (NEL) ... now takes the `\u0085`
spelling" is false for a >200-byte stderr whose U+0085 UTF-8 encoding straddles the raw-window
tail cut: the leading `0xC2` is elided and the trailing `0x85` renders `\x85`, and a raw-byte twin
that differs only inside the elided middle renders the **identical** cell (F1). Limit (ii)
discloses the identical-cell consequence of the elided middle but does not narrow the spelling
sentence; r89 A2 (`plans/round-89.md`) is the precedent for narrowing this class. Two
instrument-strength gaps are neutral: the pair check's "each one physical line" is not enforced
(F2), and KFF9's spelling check is substring-based so a `\\u0085` spelling also passes (F3). The
filed tool is correct on both; the after numbers are unaffected.

Recommendation to the L1: file C1 as verified. File C2 as verified-as-narrowed: the L1's plan now
records A1 (the KFF9 substring count does not certify "injective"; the sentinel's `5ec2e925…`
mutant survives it), A4 (the raw-window boundary spelling; A4 cites this seat's
`receipts/c2-edge-probe.txt` and folds in the one-line pair-check gap), and A5 (the members-vs-file
and battery-precision clauses); C2's narrowed sentence is A1 + A4, and the after numbers stand.
This seat's candidate rows below cite those amendments. Remaining report-only notes: the header
omits the tool-repair commit `4cb3a06f`, and S353's HTTP status rests on the scout's re-fetch, not
on the capture alone.

## The after commands (my independent runs, committed bytes)

C1 target (exact lines observed; full output was background-job stdout `bg_23930`):

```
ARM pristine pop=r89 rows=57 mismatches=0 errors=0 exit=0
ARM pristine pop=r90 rows=58 mismatches=0 errors=0 exit=0
MUTANT m17c-no-malformed pop=r89 killed=no mismatches=0 errors=0 exit=0
MUTANT m17c-no-malformed pop=r90 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m17c-no-malformed pop=r89 killed=no mismatches=0 errors=0 exit=0 | pop=r90 killed=yes mismatches=1 errors=0 exit=1
SUMMARY mutants=16 sets=r89,r90 pristine_r89=ok pristine_r90=ok killed_r89=15 killed_r90=16 killed_total=31
BATTERY-EXIT=0
```

C1 do-nothing control (exact lines observed; background-job stdout `bg_23931`):

```
ARM pristine pop=r89 rows=57 mismatches=0 errors=0 exit=0
MUTANT m17c-no-malformed pop=r89 killed=no mismatches=0 errors=0 exit=0
MUTANT-PAIR m17c-no-malformed pop=r89 killed=no mismatches=0 errors=0 exit=0
SUMMARY mutants=16 sets=r89 pristine_r89=ok killed_r89=15 killed_total=15
BATTERY-EXIT=0
```

C2 after and control (re-run into receipts, executed from committed bytes):

```
SUMMARY cases=12 tool_pass=12 before_pass=10        (c2-after.txt; exit 0)
SUMMARY cases=12 tool_pass=10 before_pass=10        (c2-control.txt; exit 1, KFF9/KFF10 fail both arms)
SUMMARY rows=12 mismatches=0 errors=0; EXIT=0       (c2-k4-regression.txt; counter sha 4e2b7c06)
```

## Integration status at final read (HEAD fd25bfc5, plan untracked)

`plans/round-90.md` now records A1 (the KFF9 substring certification; the sentinel mutant
`5ec2e925…` is the same one-line doubled-backslash edit this seat's
`receipts/variant-doublebackslash-tool.py` reproduces byte-identically), A4 (the raw-window
boundary spelling, citing this seat's `receipts/c2-edge-probe.txt`; it also folds in the one-line
pair-check gap), A5 (the members-vs-file clause and the battery self-pin/dead-code predicate notes,
citing this seat's `receipts/measurements.txt`), plus A0.4 (battery pin/path change) and A2/A3.
Mapping from this seat's findings: F1 -> A4; F2 -> A4's second gap; F3 -> A1; F4 -> A5(a);
F5 -> A0.4 (battery change) and A5(b) (battery self-pin); F6 -> no amendment needed (the scout's
`receipts/verify.out` corroborates the status). The plan was read while untracked; the L1 remains
the integration owner.

## Sentence-by-sentence table

Line refs are `census/round-90/preregistration.txt`. "Holds" means the instrument enforces the
promise and my run reproduces it; "neutral" means a wording/instrument precision that changes no
target number and needs no claim withdrawal; "falsified" means a wave artifact contradicts the
stated wording.

| # | Lines | Promise-bearing sentence | Instrument / my check | Verdict |
|---|---|---|---|---|
| 1 | 1-9 | Frozen before after-data; P1/P2 are the instrument commits; F is this file alone; no widening; falsifiers go to `plans/round-90.md` | `git show --stat` P1 (13 files), P2 (2 files), F (1 file); `git rev-parse` F = fd25bfc5; plan has A0.1-A0.6 | holds (the tool-repair commit 4cb3a06f is not named in the header; see F5/note) |
| 2 | 11-14 | 12 seats; attack 6/12 (2 reviewer, critic, mutation-tester, labrat, sentinel); 1 connector, 3 executors, 1 scribe, 1 scout; L1 planner; residual calls none | `w1/swarm-registry.json` 12 members; roles reviewer x2, critic, mutation-tester, revenger (S90Labrat), sentinel, 3 executor, scribe, scout, connector; dispatch counts spawn=12 resume=0 | holds |
| 3 | 19-21 | r89 16-member set's sole surviving clause is the `len(r) < 3` guard dropped by m17c; bound by one new row LD2b appending `ZZ9<TAB>ABSENT` under an id absent from the frozen r77 ledger | my control run 15/16, only m17c alive; per-row m17c r90: only LD2b red; r89: 0 red; `grep '^ZZ9'` r77 ledger = 0; direct pristine prints `LEDGER-REFUSED id=ZZ9` rc 1; m17c IndexError | holds; uniqueness holds both ways (see tests a/b) |
| 4 | 21-23 | r90 population 58 rows = r89 57 byte-for-byte in order + LD2b; sha256 d64d7695 | 58 vs 57 data rows; first-57 sha `2de0717e…` equals r89 all-rows sha; `diff` of r90 first 59 lines vs r89 file exit 0; last line LD2b | holds |
| 5 | 23-25 | unchanged r87 counter, sha256 fd0a8e24 | sha matches; `git diff base..HEAD -- counter` empty; only the r87 commit in its log | holds |
| 6 | 25-31 | battery e7265335, harness c3664747, mutants 39252248; "the r89 sixteen byte-identical" | all shas match; 16 members JSON-dump-equal to r89; the **file** differs only in the `note` line (bc7e6bb1 vs 39252248) | holds for the members; narrow the file-level reading (F4, neutral) |
| 7 | 32-38 | battery reports the ARM/MUTANT-PAIR/SUMMARY lines EXACTLY; EXIT 0 | my target run above, line for line | holds |
| 8 | 40-44 | counter command target: killed_total=31, 15/16, both pristine green, EXIT 0 | my target run; BATTERY-EXIT=0 | holds |
| 9 | 46-49 | kill = non-zero harness exit (mismatch/error/crash); mutant text exactly once else INVALID exit 2; killed counts and sum | battery code: `src.count(old) != 1 -> return 2`; `k = rc != 0 or mism > 0 or errs > 0`; `tot = sum(killed)` | holds |
| 10 | 51-59 | control reads killed_r89=15, m17c alive, EXIT 0; no work reaches 16/16 or 31; delta is LD2b and nothing else | my control run; population delta is one row; counter/mutant members/kill rule unchanged | holds |
| 11 | 61-66 | mechanism: pristine `ZZ9` in bad -> `LEDGER-REFUSED id=ZZ9` exit 1; m17c executes `ledger[r[0]]=(r[1],r[2])` -> IndexError no marker; m17/m17b keep the length guard and stay green on LD2b | direct counter runs: pristine rc 1 + marker; m17c IndexError at `_ledger` line 494; per-row m17/m17b LD2b match=yes | holds |
| 12 | 68-69 | limit (i): counter, mutant texts and kill rule unchanged; "this round changes the population and its harness only" | counter/members/kill rule unchanged; **battery also changed** (r90 PINS entry + r89 path retarget); harness changed (pin + LD2b append branch); A0.4 discloses | holds as intended; narrow "harness" to "the scoring instruments" if read strictly (F5, neutral) |
| 13 | 69-71 | limit (ii): one malformed shape (2 columns, absent id); the other shapes are unrowed | population has only the 2-column shape; LD2b's row is the only new one | holds |
| 14 | 71-73 | limit (iii): the marker proves the id was refused, not the branch; branch attributed by the four mutants | pristine/m17c/m17/m17b behaviour as above | holds |
| 15 | 73-75 | limit (iv)(v): fixture population not a census; r77 ledger frozen; r89 arm is the control | `git diff base..HEAD` r77 ledger empty; population identity; same data used as control | holds |
| 16 | 80-84 | C2: the K4 FLAGFAIL escaping rule is injective on the byte/character pair; raw 0x85 keeps `\x85`; character U+0085 takes `\u0085`; dead `_one_line` deleted | `_escape_text(_decode_record(x))`: `\udc85`->`\x85`, U+0085->`\u0085`; edge probe short/head/tail/repeat; greps; import | rule-level pair holds; raw byte holds; **character spelling falsified at the window cut (F1)**; `_one_line` holds |
| 17 | 84-92 | fixture sha d4417213; tool sha d095b52f; before sha f6fce6d1 (= r89 filed bytes); SUMMARY 12/12/10; EXIT 0 | shas match; before tool equals `git show bd760432:tools/souji-record-agreement.py`; my run | holds |
| 18 | 94-98 | counter command target | my run; exit 0 | holds |
| 19 | 100-107 | kill rule: the ten r89 cases unchanged; KFF9/KFF10 spellings; pair check requires DIFFERENT cells and each one physical line; both arms; AND semantics | diff of r89/r90 fixture (10 case functions unchanged); KFF9/KFF10 code; pair loop on both kits; **newline variant passes 12/12** (F2); **`\\u0085` variant passes 12/12** (F3) | spellings enforced as substrings; "each one physical line" NOT enforced (F2); distinctness/AND holds |
| 20 | 109-112 | control: 10/10, KFF9/KFF10 fail both arms (identical details), EXIT 1; cannot reach 12 | my control run | holds |
| 21 | 114-117 | regression: r87 12-row K4 counter 12/0/0 EXIT 0; ten r89 cases pass on the filed tool | my runs; receipt counter sha 4e2b7c06 = `census/round-87/c2-k4-counter.py`; writer sha 70bbf1c2 unchanged | holds (the prereg does not name the counter path; receipt names the sha) |
| 22 | 119-122 | dead code: `grep -c 'def _one_line('` = 0; no `_one_line(` call; imports; dynamic caller outside the grep, none claimed | grep 0/0; before tool 1 occurrence = the def; module imports; fixture loads it 24 times | holds (static scope; F-note) |
| 23 | 124-130 | S353: capture HTTP 200, 226166 bytes, sha 296df533, opened 2026-11-08; quote 18 words, tag-stripped offset 82360; U+0085 class NL, mandatory break | sha/size/Version "Unicode 18.0.0"/Date 2026-09-01/This Version tr14-57.html; class row lines 2873-2879; quote present; strip+unescape prefix offset 82360; occurrence 1; 18 words; LineBreak.txt `0085 ; NL` | holds for bytes/sha/size/version/quote/offset; HTTP 200 is corroborated by S90ScoutSources/receipts/verify.out, not by the capture alone (F6, provenance note) |
| 24 | 132-134 | limit (i): repair covers `_escape_text` only; `_escape_record` unchanged; path U+0085 bytes print `\xc2\x85` | tool diff: `_escape_record` unchanged; direct `_escape_record(b'\xc2\x85')` = `\xc2\x85` | holds |
| 25 | 134-136 | limit (ii): injectivity measured is the enumerated KFF9/KFF10 pair; no universal injectivity; a stderr differing only inside the elided middle renders identically | fixture pair; edge probe cut/twin | holds for injectivity; it does not cover the spelling sentence (F1) |
| 26 | 136-137 | limit (iii): KFF10 binding is this round's rule; r89 bound only KFF6/KFF7 to a pair | r89 fixture applies KFF6/KFF7 only, after arm; r90 applies both pairs on both arms | holds |
| 27 | 137-139 | limit (iv): deletion by static grep + import; runtime dispatch not exhaustively excluded | greps; no getattr/string caller found | holds |
| 28 | 138-139 | limit (v): before tool is the r89 filed bytes; r88 and older are not arms | sha equality; no older bytes used | holds |
| 29 | 144-146 | P committed before F; F one file; after F only plan amendments to instruments | commit stats; `git status` shows no modified instrument (receipts/plan/corpus are untracked/modified after-data) | holds |
| 30 | 147-148 | after receipts on committed tool/instrument bytes; report cites the landed hash | receipts name the shas; my runs reproduce on committed bytes; receipts are untracked at measurement (L1 integration) | holds for bytes/shas; landed hash is the L1's |
| 31 | 149-150 | pre-freeze feasibility disclosed, not after-data; after arms re-run after F | A0.3; my after runs executed at HEAD F | holds |

## The four specific tests

**(a) Sole survivor on the r89 population, my own run.** `killed_r89=15` of 16; the only
`killed=no` line is `m17c-no-malformed` (`mismatches=0 errors=0 exit=0`). No other r89 mutant
survives. The r89 round's own receipt (`census/round-89/records/c1-after.txt`) agrees
(`killed_r89=15`, m17c alive).

**(b) "Bound by one new population row".** Two directions, both measured:
- m17c on r90 matches every row except LD2b (`ROW LD2b ... match=no`, one mismatch); on r89 it
  matches all 57 rows (0 mismatches). The population delta is LD2b and nothing else, so no other
  row can bind m17c, and LD2b is the sole binder.
- LD2b against the other 15 mutants: every one has `ROW LD2b ... got=LEDGER-REFUSED rc=1
  match=yes` (the length guard is intact in m17/m17b; the other 13 do not touch `_ledger`).
  LD2b kills m17c and only m17c.
- Direct counter: pristine prints `LEDGER-REFUSED id=ZZ9 why=unknown or duplicate id` with
  `SUMMARY items=35 ... refused=1` and rc 1; m17c raises `IndexError: list index out of range`
  at `_ledger` `ledger[r[0]] = (r[1], r[2])` with no marker and rc 1.
- `ZZ9` is absent from the frozen r77 ledger (`grep '^ZZ9'` = 0); the r77 ledger is unchanged
  since base (`git diff base..HEAD` empty; last commit 8bf42fc6).

**(c) Does the pair check enforce injectivity, or only the two enumerated spellings?** Only the
two enumerated payloads' spellings, and even those as substrings. The pair check
(`_r9 != _r10 and len(_r9) == 1 and len(_r10) == 1`) adds row-level distinctness that the spelling
checks already imply. It does not test injectivity as a property, and it does not enforce "each
one physical line": a variant that appends a raw newline inside the K4 FLAGFAIL detail passes
12/12 (the cell is truncated at the newline; `len(_r9)==1` counts MISMATCH rows, not physical
lines). A variant that spells U+0085 as `\\u0085` (the literal text's spelling) also passes 12/12
because `count(bs+'u0085')==1` counts the second backslash's `\u0085` substring. The filed tool
emits the single-backslash `\u0085` and one physical line, so the filed behavior is correct; the
instrument is weaker than the KILL RULE's sentence.

**(d) Is the grep argument sufficient for "dead `_one_line` (zero callers) is deleted"?** For the
stated static claim, yes: the current tool has 0 `def _one_line(` and 0 `_one_line(` occurrences;
the r89 before tool has exactly 1 `_one_line(` occurrence (the definition, zero calls); the
module imports (the fixture runs it 24 times). It cannot exclude a dynamically generated caller;
the prereg itself says so ("runtime dispatch is not exhaustively excluded") and no `getattr`
string caller was found. The argument is sufficient for the static wording, insufficient for a
runtime wording — which is not claimed. Separately, S90Critic's
`receipts/c2-cheat-spellonly_keep_one_line.txt` shows the C2 *predicate* does not test this half (a
tool that applies only the U+0085 spelling and keeps `_one_line` still scores 12/12); that is a
predicate-scope gap in the critic's artifact, not a defect in this seat's grep check, and it is
cited here as corroboration rather than duplicated as a row.

## Findings by severity

### F1 — C2 wording falsified at the raw-window cut (medium; `falsifies-wording`)

Sentence (lines 82-83): "the CHARACTER U+0085 (NEL), whose UTF-8 encoding the r89 tool also
rendered `\x85`, now takes the `\u0085` spelling".

Reproducer (`receipts/c2-edge-probe.txt`, public K4 path, filed tool):
- payload A = `b"p"*101 + b"\xc2\x85" + b"s"*98` (201 bytes): the cell is
  `the index-flag read failed (` + 100 `p` + `…` + `\x85` + 98 `s` + `); tracked bytes are
  unverified`; `count(\u0085)=0`, `count(\x85)=1`. The window keeps raw[:100] and raw[-99:]; the
  character's bytes sit at 101-102, so `0xC2` is elided and `0x85` is the first tail byte and is
  decoded as the invalid byte, spelled `\x85`.
- payload B = `b"p"*101 + b"\x86\x85" + b"s"*98` (201 bytes): the same head and tail; the cell is
  **identical**. The two stderrs differ only at byte 101 (0xC2 vs 0x86), inside the elided middle.

Limit (ii) discloses "a stderr that differs from another only inside the elided middle still
renders identically", so the identical-cell/injectivity consequence is disclosed; the sentence
about the character's own spelling is not. The r89 A2 precedent (`plans/round-89.md`) narrowed the
same class (pipeline not injective on the pair; window). S90Critic's
`receipts/c2-collision-sweep.txt` records the same cut (`cut-at-window: ...`) and its report §5(b)
classifies it as covered by limit (ii); the readings differ only on whether limit (ii), which
speaks of injectivity and identical rendering, also narrows the positive spelling sentence. The
one-clause narrowing is now recorded as `plans/round-90.md A4` (A4 cites this seat's
`receipts/c2-edge-probe.txt`; its narrowed sentence is: the spelling holds when both bytes of
U+0085 survive the raw window; a cut inside the encoding renders the remaining byte as `\x85`):
"the character takes `\u0085` when its UTF-8 encoding survives the raw window; a cut encoding is
decoded as split bytes, so the trailing 0x85 keeps `\x85` and the cell can equal a raw-byte stderr
that differs only inside the elided middle." The L1 chose the narrowing over the critic's
rule-scoped reading; either way the behavior is disclosed, not silently repaired.

### F2 — The pair check does not enforce "each one physical line" (medium instrument gap; `neutral`)

Sentence (lines 104-106): "...the KFF9 detail and the KFF10 detail must be DIFFERENT cells and
each one physical line...". The fixture's pair code is `len(_r9) == 1 and len(_r10) == 1`, i.e.
one MISMATCH **row** each; a raw newline inside the detail splits the record and leaves one row
with a truncated cell. Reproducer: variant tool sha `e96ef90c…` (adds a raw `\n` before the
FLAGFAIL suffix) reads `SUMMARY cases=12 tool_pass=12 before_pass=10`, EXIT 0
(`receipts/c2-variant-newline-fixture.txt`), and the edge probe with that variant shows the cell
truncated before `); tracked bytes are unverified`. The filed tool's own detail is one physical
line (edge probe: `physical_lines=1` for all payloads). Recorded by the L1 as the second instrument
gap in `plans/round-90.md A4` (and in A1's instrument-gap list). Recommendation: fixture check `out`
for a raw newline (or compare the record bytes), or narrow the KILL RULE sentence; this is a
fixture-strength gap, not a tool defect and not a number change.

### F3 — KFF9's spelling check is substring-based; the certification clause is falsified (medium; `falsifies-wording`, recorded as A1)

Sentence (lines 82-83, 101-102): "KFF9 ... requires the detail to carry exactly one `\u0085`
spelling". The check is `rows[0].count(bs + "u0085") == 1 and rows[0].count(bs + "x85") == 0`; a
doubled-backslash `\\u0085` (the literal text's spelling) contains the `\u0085` substring and
passes. Reproducer: variant sha `5ec2e925…` passes 12/12
(`receipts/c2-variant-doublebackslash-fixture.txt`); the edge probe with that variant shows the
character's cell as `\\u0085`. The filed tool emits the single-backslash `\u0085`. This is the
direct answer to (c): the pair check enforces "contains `\u0085`, no `\x85`" for the two payloads,
not the exact spelling and not injectivity as a property. The L1 recorded this as
`plans/round-90.md A1`; A1's artifact is the sentinel's `S90Sentinel/mut/mutant.py` sha
`5ec2e925…`, the same one-line doubled-backslash edit this seat's variant reproduces
byte-identically (same sha), so the finding is independently corroborated. The missing
doubled-spelling conjunct (`count(bs*2+"u0085")==0`) is routed to r91.

### F4 — C1 "the r89 sixteen byte-identical" is member-scoped (low; `neutral`)

`census/round-90/c1-mutants.json` sha `39252248…` differs from `census/round-89/c1-mutants.json`
sha `bc7e6bb1…` in line 2 only (the top-level `note`); the 16 `members` arrays are JSON-equal
(`json.dumps(a)==json.dumps(b)` true). The claim's parenthetical is true if read as "the sixteen
[mutants] byte-identical"; A0.4 says "16 members, byte-identical". No number change; a report
sentence could add "members". Recorded by the L1 as `plans/round-90.md A5(a)` (citing this seat's
`receipts/measurements.txt`).

### F5 — C1 "this round changes the population and its harness only" (low; `neutral`)

The counter, mutant members and kill rule are unchanged (verified). The **battery** also changed:
the `PINS` map gains an r90 entry and the r89 path retargets from `HERE` to `FLEET`; the row
harness gains the r90 pin and the `LD2b` append branch (`elif rid in ("LD2", "LD2b")`). A0.4
discloses "the harness, the battery ... plus the r90 pin and LD2b's append branch". If "harness"
means only `c1-false-row-harness.py`, the sentence is imprecise; if it means the scoring
instruments, it holds. No number change; a report/plan precision only. Recorded aspects:
`plans/round-90.md A0.4` discloses the battery pin/path change; `A5(b)` records the battery
self-pin gap. The header's instrument-commit list (P1/P2) does not name `4cb3a06f`, the C2
tool-repair commit whose bytes the C2 after/control arms use; the bytes are in the P/F tree
(4cb3a06f is an ancestor of P1), so the freeze holds, but an auditor following the header would
miss the commit. The 4cb3a06f omission remains a report note.

### F6 — S353 "HTTP 200"/"opened 2026-11-08" not carried by the capture (info; `neutral`)

The capture proves 226166 bytes, sha `296df533…`, Version "Unicode 18.0.0", Date 2026-09-01,
This Version `tr14-57.html`, the class row at capture lines 2873-2879, the quote's presence
(tag-stripped + entity-decoded prefix offset 82360, occurrence 1 in whitespace-collapsed text, 18
words), and `LineBreak.txt` `0085 ; NL`. The capture alone does not carry the HTTP status or the
open time; however, the wave's scout seat re-fetched the URL this round and recorded
`https://www.unicode.org/reports/tr14/ http=200 bytes=226166 effective=https://www.unicode.org/reports/tr14/`
with sha `296df533…` and a byte-equal `cmp` against the capture in
`.ufo/waves/round-90/w1/S90ScoutSources/receipts/verify.out` (line 2). So the status/size promise
is corroborated by a wave artifact, not by the capture alone; the "opened 2026-11-08" time is the
L1's fetch date, and the scout's re-fetch proves only that the URL serves the same bytes now.
Provenance note only; no claim failure.

## Candidate pre-file ledger rows (5 columns, TAB-separated)

```
# claim	artifact	verdict	narrowing	note
C1	.ufo/waves/round-90/w1/S90Reviewer2/receipts/c1-per-row.txt	neutral	-	Sole survivor and one-row binding hold in my own run: killed_r89=15, only m17c alive; m17c's only r90 mismatch is LD2b; LD2b matches for all other 15; pristine prints LEDGER-REFUSED id=ZZ9 rc=1 and m17c raises IndexError. No falsification.
C1	.ufo/waves/round-90/w1/S90Reviewer2/receipts/c1-target.txt	neutral	-	Target re-measured exactly on committed bytes: mutants=16, sets=r89,r90, both pristine green, killed_r89=15, killed_r90=16, killed_total=31, BATTERY-EXIT=0. No falsification.
C1	.ufo/waves/round-90/w1/S90Reviewer2/receipts/c1-control.txt	neutral	-	Do-nothing control re-measured: killed_r89=15, m17c alive, BATTERY-EXIT=0. No falsification.
C1	.ufo/waves/round-90/w1/S90Reviewer2/receipts/measurements.txt	neutral	plans/round-90.md A5	Two wording precision notes, no number change: the 16 members are JSON-identical to r89 but the file note differs (sha 39252248 vs bc7e6bb1); the battery also changed (r90 pin + r89 path), so read 'harness' as the scoring instruments or narrow. 4cb3a06f (tool repair) is an unnamed instrument commit in the P/F tree. A5(a) covers the members; A0.4 covers the battery change; A5(b) the battery self-pin.
C2	.ufo/waves/round-90/w1/S90Reviewer2/receipts/c2-edge-probe.txt	falsifies-wording	plans/round-90.md A4	The character-spelling sentence fails at the 200-byte raw-window tail cut: 101p + C2 85 + 98s (201 B) renders ...\x85sss... with no \u0085; a 0x86+0x85 twin differing only inside the elided middle renders the identical cell. Limit (ii) covers the identical rendering, not the spelling sentence. S90Critic's c2-collision-sweep.txt records the same cut and reads it as limit-(ii)-covered; see the report's F1. Recorded by the L1 as plans/round-90.md A4.
C2	.ufo/waves/round-90/w1/S90Reviewer2/receipts/c2-variant-newline-fixture.txt	neutral	plans/round-90.md A4	The KILL RULE's 'each one physical line' is not enforced: a variant appending a raw newline inside the K4 detail passes 12/12 (tool_pass=12 before_pass=10, EXIT 0); len(_r9)==1 counts MISMATCH rows and the cell is truncated. Filed tool's own detail is one physical line. Fixture-strength gap, not a tool defect. Recorded in A4's second instrument gap.
C2	.ufo/waves/round-90/w1/S90Reviewer2/receipts/c2-variant-doublebackslash-fixture.txt	falsifies-wording	plans/round-90.md A1	KFF9's check is substring-based: a variant spelling U+0085 as \\u0085 (the literal text's spelling) passes 12/12; the check enforces 'contains \u0085, no \x85' for the two payloads, not the exact spelling and not injectivity as a property. Recorded by the L1 as A1; the sentinel's mutant sha 5ec2e925 is the same one-line edit as this seat's variant. Filed tool emits the single-backslash \u0085; the fixture cannot certify it.
C2	.ufo/waves/round-90/w1/S90Reviewer2/receipts/c2-after.txt	neutral	-	After target reproduces exactly: SUMMARY cases=12 tool_pass=12 before_pass=10, exit 0; control c2-control.txt 10/10, exit 1; KFF9/KFF10 pass only on the filed tool. No falsification.
C2	.ufo/waves/round-90/w1/S90Reviewer2/receipts/c2-k4-regression.txt	neutral	-	The r87 12-row K4 counter reproduces rows=12 mismatches=0 errors=0, EXIT 0; the counter is census/round-87/c2-k4-counter.py (sha 4e2b7c06), which the prereg and receipt name only by sha. No falsification.
C2	.ufo/waves/round-90/w1/S90Reviewer2/receipts/measurements.txt	neutral	-	S353 capture verified (226166 B, sha 296df533, Unicode 18.0.0, Date 2026-09-01, tr14-57.html, class row 2873-2879, quote 18 words at strip+unescape prefix offset 82360, occurrence 1). The capture alone does not carry the HTTP status or open time; S90ScoutSources/receipts/verify.out records a live re-fetch http=200 bytes=226166 with sha equal to the capture. Provenance note only.
```

The `falsifies-wording` rows now cite the L1's recorded amendments: F1/F2 -> `plans/round-90.md A4`;
F3 -> `plans/round-90.md A1`. The precision rows cite `plans/round-90.md A5`/`A0.4` where an
amendment exists. C2 files as verified-as-narrowed (A1 + A4); the headline tool behavior, the
enumerated KFF9/KFF10 spellings and all after numbers stand.

## Residual risk and verification gaps

- I could not check the live URL: S353's "HTTP 200" and "opened 2026-11-08" are provenance
  claims; the capture's bytes/sha/size/version/quote/offset do verify (F6).
- The L1's `census/round-90/records/c1-after.txt` and `c2-after.txt` were untracked and
  `c1-after.txt` was still being written at my measurement; my after numbers are independent
  runs at HEAD F, not the L1's landed receipts. The final "landed lane hash" is the L1's
  integration.
- `claims.json` was absent at my first measurement and exists at the final read (the L1's
  integration); I did not run the fleet pre-file gate (integration duty; read-only script, but the
  surfaces are the L1's).
- My per-row matrix covers m17c on both populations in full and LD2b against all 16 mutants; the
  battery covers the full 16 x {r89, r90} matrix, and I read its per-mutant lines. I did not
  independently re-run every cell of the full matrix beyond that.
- The "zero callers" claim is static (grep + import); a dynamically generated caller cannot be
  excluded by that argument, and the prereg says so (limit iv).
- I did not re-run the r90 fixture under a different Python/git build; the lane's stated versions
  are Python 3.14.8 / git 2.56.0-1 (fixture docstring); my runs used the host's `python3`/`git`.
- The r89 A2 window-size number (202 raw bytes) is not restated in the r90 prereg, so it is not a
  target; the cut behavior above is measured directly (100 head + 3-byte ellipsis + 99 tail).

## Canonical runtime and routing

One canonical runtime: every C1 arm invokes the same counter (`census/round-87/c1-pointer-counter.py`,
sha `fd0a8e24...`) through `sys.executable -B` from the battery/harness, and every C2 arm invokes the
same tool bytes (`tools/souji-record-agreement.py`, sha `d095b52f...`) through the fixture's
subprocess copy; no arm substitutes a different counter or tool. The harness's row routing is
unchanged: `where in (lane, ledger)` is judged at BASE and fixture rows at their pinned rev
(`R1`..`R12`), enforced by `C1-HARNESS-FATAL` if a lane/ledger row is not BASE or a fixture row is;
the ledger rows append to the row's own population ledger. Saturation is honest: `killed_total=31`
is the sum of 15 r89 kills and 16 r90 kills, and the target is an exact `--expect-killed 31`, not a
floor. This round's dispatch has no resume entry (`spawn=12, resume=0`), so no resume path exists
and `resume_continuity_v1` was not exercised.

## Commands run (read-only; outputs in receipts)

- `sha256sum` on the nine named artifacts (all match the prereg).
- `grep -vc '^#'`/`head`/`sha256sum`/`diff` on the r89 and r90 populations; `tail -1` on LD2b.
- `git log --oneline -- census/round-87/c1-pointer-counter.py`; `git diff --quiet base..HEAD --` counter and r77 ledger.
- `git show --stat` P1/P2/F/4cb3a06f; `git rev-parse` the three commit ids; `git status --porcelain`.
- `python3 -B census/round-90/c1-clause-battery.py ... --only r89,r90 --expect-killed 31` -> the target lines above, EXIT 0.
- `python3 -B census/round-90/c1-clause-battery.py ... --only r89 --expect-killed 15` -> the control lines above, EXIT 0.
- `python3 -B census/round-90/c1-false-row-harness.py --counter <mutant copies> ... --population r89/r90 ...` for all 16 mutants (per-row receipt).
- Direct counter probes: pristine and m17c against the r77 items + a ledger with `ZZ9\tABSENT`.
- `python3 -B tests/fixtures/r90-k4-flagfail.py` with the filed tool, the before tool both arms, and the two variant tools; `python3 -B census/round-87/c2-k4-counter.py --tool tools/souji-record-agreement.py`.
- `python3 -B edge_driver.py` (public K4 path, 14 payloads) with the filed tool and both variants.
- `grep -c 'def _one_line('`, `grep -o '_one_line('`, importlib load of the tool.
- Tag-strip/entity-decode/whitespace-collapse of `census/round-90/srcs/tr14.html`; class-row sed; `wc -c`.

## Tooling and scratch disclosure

No tool was installed or upgraded. No pacman/host mutation. No mutating git/jj command was issued
against the lane or any shared repository; the lane's own read-only harnesses created their
throwaway fixture repositories under my scratch (clone/commit inside the fixture), and those were
deleted with the scratch. Scratch `/fast/scratch/hyaku/souji-r90/S90Reviewer2/` was deleted after copying
`edge_driver.py`, both variant tools, the per-row logs and the receipts into this seat; nothing
was left behind. Writes were confined to `.ufo/waves/round-90/w1/S90Reviewer2.md` and
`.ufo/waves/round-90/w1/S90Reviewer2/`.
