# Round 91 — plan, pre-freeze notes, and claim amendments (pre-file falsification)

Written before the round report is filed. The frozen wording lives in `census/round-91/preregistration.txt`
(commit F) and is not edited here: each amendment records what the round's own artifacts falsified in that
wording, and the narrower sentence the round now puts its name to. Numbers are re-derived on committed bytes by
non-author seats and by the L1; records under `census/round-91/records/` and the wave's reports under
`.ufo/waves/round-91/w1/`.

Lane base: `681f6c72b242d410d0e8654efadb2a1553fb111d` (r90 closed; its non-author spot-check
`corpus/lessons/round-90-verifier-spotcheck.md` is the outside discernment check this round answers).

Wave evidence root: `.ufo/waves/round-91/w1/`.

## A0 — pre-freeze instrument notes and disclosures

- **A0.1 — the r90 spot-check's five routed defects are answered this round.** (1) The r90 report cited
  `census/round-90/claims.json`, a path that does not exist; this round's frozen claims are
  `.ufo/waves/round-91/claims.json`, and the report cites that path only after `test -f` on it. (2) The r90
  attack-share figure mixed two role sets; this round cites ONE definition in the prereg (addendum four roles:
  reviewer ×2 + critic + mutation-tester = 4/13 = 30.8 %) and prints the prefile gate's broader
  `ATTACK_ROLES` count separately. (3) The r90 settlement record retained no seat outputs; this round reports
  the wave's settlement provenance exactly as the driver or the L1 constructed it. (4) The r89 capability row
  ("a malformed-row binding whose id is absent from the ledger (measured, not landed)") is annotated in
  `SCORECARD.md` as superseded by the landed r90 row instead of being left as a design-only capability. (5) The
  narrowed instrument work (doubled-spelling conjuncts, raw-window boundary, one-physical-line, `_one_line`
  deletion row, battery self-pin) is carried as this round's C2 and the battery self-pin in C1's instrument.
- **A0.2 — C1's counter bytes are unchanged.** `census/round-87/c1-pointer-counter.py` sha256
  `fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b` is the same file the r87–r90 batteries used.
  The round changes the population, the harness (fixture rev R13, the `where=ledger-resolve` row type, the
  LD1c/LD3 append shapes) and the mutant set; the kill rule ("a kill is a non-zero harness exit on that
  population") is unchanged.
- **A0.3 — the r91 population is the r90 file plus five appended lines.** `census/round-91/c1-false-rows.tsv` is
  byte-identical to `census/round-90/c1-false-rows.tsv` for its full length (checked with `cmp -n`), then LD1c,
  LD3, LD4, NF6i2 and NF6j. The harness and battery pins name its sha256; the r90 file is a pinned control.
- **A0.4 — Q162 minimality is recorded, not ignored.** S90MutCounter §4 measured that the identical-duplicate row
  (LD1c here) kills BOTH duplicate-keyed spellings while a same-class-different-target row would kill only one, so
  one row is added, not two; `len(r) <= 2` (`s2`) is logically equivalent to the frozen guard and gets no row;
  the 4+-column and CRLF shapes stay unrowed as S90MutCounter §5.3 measured them indistinguishable from rows the
  population already carries.
- **A0.5 — C2's before-arm is the r90 tool bytes, not the r89 tool.** The claim's pre-state is the current lane
  tool (`census/round-91/controls/c2-before-tool.py`, sha256 `d095b52f…`, `git show master:` bytes). The r89 tool
  is kept as `controls/c2-before-tool-r89.py` (`f6fce6d1…`) so the r90 fixture's own control can be reproduced.
- **A0.6 — pre-freeze feasibility runs are disclosed, not filed as after-data.** The r91 fixture, the variant
  probe and the boundary probe were exercised before F to prove every conjunct can be met and can fail (QUALITY
  Q70); their pre-F outputs live under `census/round-91/controls/` and are named instrument validation. The filed
  after receipts (`records/c1-after.txt`, `records/c2-after.txt`, `records/c2-variants-r91.txt`,
  `records/c2-k4-regression.txt`) are re-run after F on the committed instruments and name the shas.
- **A0.7 — the C2 repair is committed before F and measured after it.** The filed tool bytes (sha256 `21e5c740…`)
  are in P; F freezes the predicate; the after receipts are post-F runs on those bytes. The r90 defect (an after
  run that predated F and was later re-run) is not repeated: the control precedes F, F precedes the after receipts.
- **A0.8 — wave-evidence durability.** Every seat report and receipt under `.ufo/waves/round-91/w1/` is named
  explicitly to `jj-lane.sh` (`jj file track --include-ignored`), so the pre-file ledger's artifact paths resolve
  from the pushed lane tip, not only from the working tree.

## A1 — C1: STATED LIMITS (iii)'s premise is refuted; the claim and every number stand

- **Artifact:** `.ufo/waves/round-91/w1/R91ReviewerC1.md` §5.3 (`pristine-base.out`, `pristine-empty-ledger.out`,
  `s1-base.out`) and §7 (FALSIFIES-WORDING 1); also `.ufo/waves/round-91/w1/R91ExecC1Harness.md` § FALSIFIES-WORDING.
- **Frozen sentence falsified:** prereg C1 STATED LIMITS (iii): "LD4 asserts an ITEM status and no exit code: the
  base run is not all-resolved (the r77 population is mostly false rows), so exit 1 is expected and not asserted."
  The premise is false: the LD4 row's population is the r77 **item** file (`census/round-77/c2-population.tsv`),
  whose 35 items all resolve at BASE — `SUMMARY items=35 resolved=35 unresolved=0 refused=0 mismatched=0 errors=0`,
  rc 0. A whole-ledger refusal prints 31 unresolved and rc 1, so the missing rc assertion would have been
  assertable and was a choice, not an impossibility.
- **What survives:** LD4's ITEM-status assertion already kills `s1-exact-width` (`ITEM P04 … status=UNRESOLVED`),
  and no CLAIM, POPULATIONS, INSTRUMENTS, KILL RULE or PREDICATE sentence is refuted — every hash, the r90 prefix,
  the counter's immutability, both predicate SUMMARYs and the six r90 survivors re-derive (R91ReviewerC1 §1–§4;
  R91ExecC1Battery; R91ExecC1Harness).
- **Narrowed sentence (what this round puts its name to):** *LD4 asserts the ITEM status `MOVED` for item P04 with
  the unchanged 4-column base ledger and does not assert an exit code; the base run is all-resolved and exits 0, so
  the missing rc was a grip choice, not an impossibility; the status assertion alone is what kills the width-exact
  spelling.* Routed to r92: assert `rc=0` as well (strictly stronger).

## A2 — C2: two wording clauses are narrowed; the numbers stand and the residual is routed

- **Artifact (a):** `.ufo/waves/round-91/w1/R91ExecC2Tool/repro-cut-tail-split.txt` and `R91ExecC2Tool.md`
  § FALSIFIES-WORDING (payloads `A = a*110 + F0 80 + a + C2 85 + b*95`, `B = a*110 + F0 80 + a + b + 85 + b*95`,
  both 210 bytes, `CELLS_EQUAL=True`); independently reproduced by `.ufo/waves/round-91/w1/R91Scribe/cut-edge-probe.txt`
  (payload `A*101 + E0 + 85 C2 85 + B*96`, `_cut_tail` returns 104, a continuation of a valid `C2 85` whose lead the
  advance elided). `.ufo/waves/round-91/w1/R91Connector.md` F1 adds that the sequence-length test is **structural**
  (C0–DF/2, E0–EF/3, F0–F7/4), not RFC-validity-validated, and an RFC-conformant reading also scores 15/15.
- **Frozen sentences falsified (a):** C2 CLAIM: "The filed tool moves BOTH cuts to sequence boundaries before
  decoding (`_cut_head` backs off a valid partial sequence; `_cut_tail` advances past continuations whose lead the
  middle elided; …)". `_cut_tail` does not validate the continuation run: with a truncated/invalid lead immediately
  before the tail cut it returns `lead_index + need` even when the run is shorter, landing the cut inside a LATER
  valid sequence; the surviving continuation then prints `\x85` and two materially different payloads share one cell.
  The repair is exact on valid UTF-8 payloads (ExecC2Tool's 1137-row sweep, 0 splits; KFF11 is valid and unaffected),
  but the sentence as written is unqualified.
- **Artifact (b):** `.ufo/waves/round-91/w1/R91ReviewerC2.md` §4 FALSIFIES-WORDING 1 and its reproducer
  `kff13-spaced-name-tool.py` / `kff13-probe.out`: a tool carrying a real `def _one_line (text)` and a real
  `_one_line (value)` call scores `cases=15 tool_pass=15 before_pass=14`, EXIT 0.
- **Frozen sentence falsified (b):** C2 CLAIM's "the tool source carries no `_one_line(` definition or call
  (KFF13)". KFF13 is a literal substring count; Python allows whitespace before `(`, so an in-source definition and
  call can be written without the substring. `.ufo/waves/round-91/w1/R91ExecC2Fixture.md` §5c adds the mirror defect:
  a docstring that merely mentions `_one_line(` false-FAILS the same scan.
- **Narrowed sentence (a) — what this round puts its name to:** *On payloads whose bytes around the cuts are valid
  UTF-8, the filed tool moves both cuts to sequence boundaries before decoding: the head backs off a valid partial
  sequence, the tail advances past continuation bytes whose lead the elided middle began, and a no-lead continuation
  keeps its `\xNN` spelling. The sequence-length test is structural (C0–DF/2, E0–EF/3, F0–F7/4), not RFC-validity;
  on a truncated/invalid lead immediately before the tail cut, `_cut_tail` can over-advance into a later valid
  sequence and re-create the byte/character cell collision (reproducer above). Routed to r92: validate the whole
  declared sequence (`end <= len(raw) and all(continuation)`) before moving the cut, add the C0/C1/F5-F7 range
  checks, and add head-cut and invalid-lead fixture rows.*
- **Narrowed sentence (b) — what this round puts its name to:** *KFF13 enforces the literal absence of the
  substrings `def _one_line(` and `_one_line(`; a definition or call spelled with whitespace before the paren is
  not detected (an in-source gap outside limit (ii)'s dynamic-caller exclusion), and a docstring that mentions the
  token false-fails the scan. The filed tool carries neither an `_one_line` definition nor a call under an AST
  check (`ast.parse`: 0 defs, 0 calls).* Routed to r92: replace the literal scan with an AST check and add both
  directions as fixture cases.
- **Wave-added limits (recorded, not claim sentences):** (1) the battery's `--expect-killed` gates on the SUM
  `killed_r90 + killed_r91`; the split is asserted by the printed SUMMARY line, not by the exit code
  (R91ReviewerC1 §8.1); (2) KFF11 exercises the tail cut only; the head cut is exercised by ExecC2Tool's sweep;
  (3) the fixture cannot distinguish the filed tool from an RFC-validity-conformant variant (R91Connector F1);
  (4) the r91 population's two comment lines are inherited byte-for-byte from r90 and describe the r86/r81
  ancestors, not the r90/r91 rows (R91Connector F3 — record hygiene, routed to r92).

## A3 — four attack seats died; their attacks did not happen (attempt 2, SoujiR91a2)

- **Artifacts:** `.ufo/waves/round-91/w1/dead-seats/R91Critic.json`, `R91Sentinel.json`, `R91Revenger.json`,
  `R91MutCounter.json` (driver settlement row + last error text read from each seat's session file).
- R91Critic and R91Revenger died on `opencode-go/crouton-alpha-free` 429; R91Sentinel on `minimax-code` 429
  (token-plan limit); R91MutCounter on `amr` 400 `tier_limit_exceeded` then devin `permission_denied`, after writing
  only an "in progress" stub. None was replaced. No claim sentence is narrowed by a dead seat, but no claim may cite
  them as attacks survived: the settled attack share is 2/13 (planned 4/13), and the C1 alternative-edit survivor
  search is routed to r92 unperformed.
- Attempt 1's L1 (SoujiR91) died after commit `28368806` with LOG/SCORECARD/SOURCES/plan/lesson edits uncommitted
  and no report (`lane-dead-no-report souji round=91`, watchdog 13:51:17). Attempt 2 re-read every inherited edit
  against the wave reports, kept them, corrected two statements that cited the dead MutCounter as if it had run,
  and landed them with the wave evidence.
