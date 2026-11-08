# Round 90 — the last unrowed clause gets its row, and the byte/character pair gets distinct spellings

Lane base `bd760432df2cc3ba6c5f1ccc540b050fe2ac09e2` (r89 closed). Instruments P1 `1952c1c7`, P2 `e2a11c73`;
freeze F `fd25bfc5430cf27c1af5e4c8b8f6d5899e91a20f`; C2 repair `4cb3a06f`. Wave: one v1 wave, 12 seats, `w1`.

## Claims

- **C1 (calibration 7, the lane's lowest owned non-retired axis).** The r89 sixteen-member mutant set had exactly one
  survivor, `m17c-no-malformed` (the `_ledger` `len(r) < 3` guard). The r90 population adds LD2b: it appends the
  2-column ledger row `ZZ9<TAB>ABSENT` under an id ABSENT from the frozen r77 ledger, so the length guard — not the
  duplicate leg — is the only refusal left. Measured on committed bytes: the unchanged counter, harnessed by the r90
  battery, reads `ARM pristine pop=r89 rows=57 … exit=0`, `ARM pristine pop=r90 rows=58 … exit=0`,
  `SUMMARY mutants=16 sets=r89,r90 … killed_r89=15 killed_r90=16 killed_total=31`, EXIT 0
  (`census/round-90/records/c1-after.txt`). The do-nothing control on the r89 population alone reads
  `killed_r89=15 killed_total=15`, `m17c-no-malformed killed=no`, EXIT 0
  (`census/round-90/controls/c1-before-r89-population.txt`). **VERIFIED.**
- **C2 (operability 8).** The r89 repair made the K4 FLAGFAIL detail injective on the 0xFF/literal pair but left raw
  byte `0x85` and the character U+0085 rendering the same `\x85`. The r90 tool spells the character `\u0085` (joining
  U+2028/U+2029) and deletes the dead escape-first `_one_line`. Measured: `cases=12 tool_pass=12 before_pass=10`,
  EXIT 0 (`census/round-90/records/c2-after.txt`); the control with the r89 bytes as BOTH arms reads
  `tool_pass=10 before_pass=10`, KFF9/KFF10 fail, EXIT 1 (`census/round-90/records/prefreeze-c2-control.txt`); the
  r87 12-row K4 counter stays `rows=12 mismatches=0 errors=0`, EXIT 0. **VERIFIED.**

## Gate

Sources opened this round (each read here; ids continue the registry after S351; S352 is the r89 lesson's label for
an UNFILED reject candidate, so it is never reused — see M3):

- **S353 — Unicode Standard Annex #14, Line Breaking Properties, Unicode 18.0.0 rev 57, § NL: Next Line**
  (https://www.unicode.org/reports/tr14/, HTTP 200, 226166 bytes, sha256
  `296df5332aefe695b4951b511288b118bc6a7b43db7fadfd60f6062096acc7c0`, capture `census/round-90/srcs/tr14.html`,
  opened 2026-11-08; the page names Version "Unicode 18.0.0", Revision "tr14-57.html", Date 2026-09-01). Quote,
  § NL: Next Line, occurrence count 1: "The NL class acts like BK in all respects (there is a mandatory break
  after any NEL character)." (18 words). The class-table row `0085 / NEXT LINE (NEL)` sits at capture lines
  2873-2876, the quoted paragraph at 2878-2879, and
  the LineBreak.txt line in `census/round-90/srcs/LineBreak.txt` reads
  `0085           ; NL # Cc         <control-0085>`. **ADMIT**, `docs`, tier A, `mined` — it grounds the
  byte/character distinction C2's spelling rule rests on. Used by `corpus/knowledge/nel-byte-character-pair.md`.
  No numeric offset is quoted: the first draft's 82360 was a 3-byte slip (S90ScoutSources §4), and the corrected
  82357 is itself convention-dependent — the lane's r63 stripper and the drop-tags normalizer place the same
  sentence at different offsets (S90Scribe § "the stripper rule"), so the section plus the capture lines is the
  locator.
- **UAX #13, Unicode Newline Guidelines — REJECT sample, not filed** (https://www.unicode.org/reports/tr13/, HTTP
  200, 6348 bytes, sha256 `bfa7f97b94c13c0764d99140388f88b20cbce62957d5e7174fab63d29a667c78`, capture
  `census/round-90/srcs/tr13.html`, opened 2026-11-08). The URL now serves a supersession notice: "The material
  formerly covered by UAX #13: Unicode Newline Guidelines has been incorporated into the Core Specification of the
  Unicode Standard, starting with Version 4.0" (25 words). **REJECT**: no actionable content for this cell beyond
  S353's NL class and S348's boundary list; flip only if the lane must decide which newline CONVENTION a producer
  followed, and then open the Core Specification §5.8 at its versioned URL, not this stub. The archived guideline
  the notice points at (https://www.unicode.org/reports/tr13/tr13-9.html, HTTP 200, 21897 bytes, sha256
  `6f38841a84aee71b3da64a6d1147642dc2efe5eb41bc0426189a14937d70333a`, opened by S90ScoutSources) confirms it: it
  says to treat CR, LF, CRLF and NEL the same on input — the opposite of the distinction this cell needs.

Census (before → after): `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → before
EXIT 0, 274 rows, W04 warnings only (`census/round-90/records/sources-census-before.txt`); after EXIT 0, 275 rows
(S353 appended), W04 warnings only. The registry row landed with its `used-by` entry in the same round, so E11 does
not fire.

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | wave evidence left gitignored: the r89 commit message said "12 seat reports" but `.ufo/waves/` is gitignored, so a clone of the pushed tip could not resolve the pre-file ledger's artifacts (13 `artifact-missing` rows) | `corpus/lessons/round-89-verifier-spotcheck.md` §1 and §2; `git ls-tree -r 4864129b -- .ufo/waves/round-89` lists only six files | the pre-file gate's artifact-existence check — it passed on the local tree and failed on the pushed bytes, which is the only place it counts | every r90 wave file is named explicitly to `jj-lane.sh` (`jj file track --include-ignored`), and the round checks `git ls-tree -r <tip> -- .ufo/waves/round-90` lists the seat reports before filing (plans/round-90.md A0.6) |
| M2 | pre-freeze after-data: the C2 after arm was run once before F as feasibility (Q70) and again after F | `census/round-90/records/prefreeze-c2-after.txt` (mtime 2026-11-08 11:39:44 -03) vs `records/c2-after.txt` (11:46:49) and the F commit (11:46:24); the pre-freeze run predates F by 6m40s | the freeze-before-scoring rule (r63 M2, r89 M2) | the pre-freeze run is disclosed as instrument validation (plans/round-90.md A0.3) and is not the filed evidence; the filed after receipts are the post-F runs on committed bytes |
| M3 | a registry-shaped id used as a prose label: r89's lesson labels an unfiled reject candidate `S352`, which collides with "the next unused id" when the next round files a row | `corpus/lessons/round-89.md` § Sources; `corpus/lessons/round-89-verifier-spotcheck.md` §5 (the candidate was never filed) | the CORPUS id rule (`S` + digits, the next unused, never reused) plus the census's duplicate-id check | unfiled candidates are labelled "reject sample (unfiled)" with no S-number; r90 files the next row as S353 and records the gap's reason in plans/round-90.md A0.2 |

## Wave findings

Twelve seats (3 executor, 2 reviewer, critic, mutation-tester, sentinel, connector, scout, scribe, and the labrat
duty on a revenger-role seat — the validator refuses `labrat`). Both claims re-derived by non-author seats; no frozen
NUMBER moved. The wave falsified four C2 sentences and one C1 evidence sentence, all narrowed in
`plans/round-90.md` A1, A4, A5 before filing:

- **S90Sentinel H1 (HIGH, instrument):** the KFF9/KFF10 substring counts do not bind the word "injective" — a
  one-token mutant doubling the U+0085 branch's backslash survives the r90 fixture 12/12, the r89 fixture 10/10 and
  the r87 12-row counter. The filed tool IS injective on the pair (probe6 brute force over 14 single characters and
  all 2-char strings: zero collisions); the kill rule under-certifies. A1 narrows; the doubled-spelling conjuncts are
  routed to r91.
- **S90Reviewer2 c2-edge-probe (falsifies-wording):** a 201-byte stderr whose U+0085 straddles the 200-byte raw
  window's tail cut renders the surviving byte `\x85` with no `\u0085`. A4 narrows with the boundary clause.
- **S90Reviewer2 c2-variant-newline-fitxture (falsifies-wording):** the kill rule's "each one physical line" is not
  enforced on the cell (a raw newline inside the detail passes 12/12). A4 records it as an instrument gap.
- **S90Critic (falsifies-wording, C2):** the fixture does not test the dead-code half; a tool keeping `_one_line`
  still scores 12/12. A5(c) narrows: the deletion is measured by grep+load, the prereg's second evidence.
- **S90Critic (falsifies-wording, C1):** the battery does not print its own hash; a stub printing the target SUMMARY
  scores with zero runs. A5(b): the evidence rests on the pinned bytes and the committed receipt.
- **S90ExecC1 / S90ExecC3 / S90MutCounter / S90Reviewer / S90Reviewer2 (neutral):** LD2b is the sole killer of
  `m17c` (IndexError, no marker); the counter is byte-identical `fd0a8e24`; the population is the r89 file plus one
  appended line; the r87 12-row K4 counter stays green; the ten r89 fixture cases are unchanged.
- **S90MutCounter Q162 (r91 plan):** `ld1c-class-keyed`, `ld1d-conflict-keyed`, `nf6i2-last-occurrence` and
  `nf6j-pathch-narrow` all survive all eight pinned populations (killed_total=0), so each needs a row; one
  identical-duplicate row binds both duplicate spellings; the 1-column ledger row and the `!= 3` grammar are also
  unrowed.
- **S90ScoutSources / S90Scribe (neutral):** S353 capture byte-identical; quote 18 words, occurrence 1; the first
  offset was a 3-byte slip and is now convention-dependent (dropped); the reject quote is 25 words; UAX #13 is a
  tombstone whose archived tr13-9 confirms the reject.
- **S90Connector (neutral):** the defect is first recorded at r89; the clause in code at r77; no sibling lane owns
  the ground; C1 and C2 are causally separable.

The driver never wrote `w1-results.json`: all twelve reports completed and no WAVE-DONE handoff arrived ~35 min
after spawn, so the L1 constructed the results record with `_source: l1-constructed` from the dispatch task list and
the reports (disclosed; `plans/round-90.md` A0.7; an L0 line asks the orchestrator to settle the wave). This is a
lane writing a driver artifact and is reported as a defect of the settlement path, not hidden.
