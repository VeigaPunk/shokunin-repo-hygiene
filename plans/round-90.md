# Round 90 — plan, pre-freeze notes, and claim amendments (pre-file falsification)

Written before the round report is filed. The frozen wording lives in `census/round-90/preregistration.txt`
(commit F) and is not edited here: each amendment records what the round's own artifacts falsified in that
wording, and the narrower sentence the round now puts its name to. Numbers are re-derived on committed bytes by
non-author seats and by the L1; records under `census/round-90/records/` and the wave's reports under
`.ufo/waves/round-90/w1/`.

Wave evidence root: `.ufo/waves/round-90/w1/`.

## A0 — pre-freeze instrument notes (disclosed before any after-data)

- **A0.1 — the r90 fixture's pair checks run on BOTH arms.** The r89 fixture applied the KFF6/KFF7 pair check only
  to the tool-under-test arm, so its control scored the before bytes by case checks alone. The r90 fixture applies
  the KFF6/KFF7 and KFF9/KFF10 pair checks to both arms with the same rule; this is a scoring symmetry fix, landed
  before the control receipt. Measured effect on the control: `tool_pass=10 before_pass=10` (with the one-arm rule
  the same run read `tool_pass=10 before_pass=11`, which would have understated the control).
- **A0.2 — the new source row is S353, not S352.** The r89 lesson labels an *unfiled* reject candidate `S352`
  (`corpus/lessons/round-89.md` § Sources; the verifier spot-check agrees it was never a registry row). The
  registry's next never-used id for a filed row is therefore S353; reusing S352 would contradict a committed
  record. The census checks duplicate ids, not gaps.
- **A0.3 — pre-freeze feasibility runs are disclosed, not filed as after-data.** `records/prefreeze-c1-control.txt`
  and `records/prefreeze-c1-both.txt` were run before F as Q70 feasibility (every conjunct of each predicate);
  the filed after receipts are re-run after F on the committed instruments and are named `records/c1-after.txt`,
  `controls/c1-before-r89-population.txt` and `records/c2-after.txt`.
- **A0.4 — the C1 population is the r89 file plus one appended line.** `census/round-90/c1-false-rows.tsv` is
  byte-identical to `census/round-89/c1-false-rows.tsv` except the appended LD2b row; the harness, the battery, the
  mutant set (16 members, byte-identical to r89) and the counter (`fd0a8e24…`) are otherwise the r89 bytes plus the
  r90 pin and LD2b's append branch. The C1 change is a population+harness change by construction.
- **A0.5 — the C2 repair is committed before its after receipt.** The filed tool is `tools/souji-record-agreement.py`
  sha256 `d095b52f…` (the U+0085 spelling plus the dead `_one_line` deletion); the after receipt is measured on the
  committed bytes and names that sha. The r89 defect (an after receipt that predated the freeze and was later
  re-run) is not repeated: the control precedes F, F precedes the committed repair, the after receipts follow.
- **A0.6 — the r89 wave-evidence durability defect is fixed this round.** Every seat report and receipt under
  `.ufo/waves/round-90/w1/` is committed by naming the files explicitly (`jj file track --include-ignored`), so the
  pre-file ledger's artifacts resolve from the pushed lane, not only from the working tree. `git check-ignore` on
  the wave dir still matches `.ufo/waves/`, and `git ls-tree -r <tip> -- .ufo/waves/round-90` must list the files.

## A1 — C2: the fixture's kill rule does not bind the word "injective"; the claim is narrowed, the tool's wording stands

- **Artifact:** `.ufo/waves/round-90/w1/S90Sentinel.md` §4 (H1, probe8/probe10) and §5 (H2a–H2d); the
  reproducer is durable at `.ufo/waves/round-90/w1/S90Reviewer2/receipts/variant-doublebackslash-tool.py` sha256
  `5ec2e925…74a6` (byte-identical to the Sentinel's scratch copy, which its seat deleted; S90Reviewer2 F7);
  `.ufo/waves/round-90/w1/S90Reviewer.md` §4.3
  (independent mutants: 11/12 failing exactly KFF9 and 11/12 failing exactly KFF10); `.ufo/waves/round-90/w1/
  S90Critic.md` § C2-b/C2-c.
- **Frozen wording falsified (the certification clause):** the prereg's KILL RULE says KFF9 "requires exactly one
  `\u0085` spelling and no `\x85`", implemented as `count(bs+"u0085")==1 and count(bs+"x85")==0`. A substring count
  cannot separate the character U+0085 from the literal text `\u0085` (the escaped literal `\\u0085` CONTAINS the
  substring `\u0085`). Measured: a one-token mutant that doubles the U+0085 branch's backslash passes the r90
  fixture 12/12 EXIT 0, the r89 fixture 10/10 and the r87 12-row counter. The r89 KFF6/KFF7 pair had the missing
  conjunct (`count(bs*2+"xff")==0`); the r90 pair dropped it.
- **Wording that survives (measured independently):** on the filed bytes the property is true. S90Sentinel probe6
  brute-forces 14 single characters and every 2-character string over that alphabet and finds zero collisions;
  `_escape_text("\u0085")` is `\u0085` and `_escape_text("\udc85")` is `\x85`, and they differ. The tool is
  injective on the pair; the fixture's kill rule does not prove it.
- **Narrowed sentence (what the round puts its name to):** *On the filed tool, the K4 FLAGFAIL cell spells the raw
  byte 0x85 `\x85` and the character U+0085 `\u0085`, so the two cells differ; the r90 fixture measures that each
  spelling occurs exactly once in its own case's cell and no bare `\x85` appears in the character case (KFF9) and
  no `\u0085` appears in the byte case (KFF10), `SUMMARY cases=12 tool_pass=12 before_pass=10` EXIT 0, against the
  r89 control `tool_pass=10 before_pass=10` EXIT 1. The fixture's substring counts do NOT certify the word
  "injective" on their own: a mutant that doubles the U+0085 branch survives them (S90Sentinel H1). The
  injectivity evidence is the independent brute-force probe, not the kill rule; the missing doubled-spelling
  conjuncts (`count(bs*2+"u0085")==0`, `count(bs*2+"x85")==0`) are routed to r91.*
- **Why not repair the fixture now:** the claim is judged on the counter, kill rule and predicate declared before
  data; a rule changed after any seat has scored is not the claim's rule (the r42 kumitate lesson). The repair is a
  one-clause-per-case change and is carried to r91.

## A2 — C2's other arms are out of the claim's scope (routed, not falsifying)

- **Artifact:** `.ufo/waves/round-90/w1/S90Sentinel.md` §5 H2a–H2d; `.ufo/waves/round-90/w1/S90Critic.md` § C2-c.
- **Measured:** the FORGED arm (real LF, U+0085, U+2028, U+2029) renders one identical cell `a\nb` because
  `out.splitlines()` runs before `_escape_text`; the REFUSED arm truncates its reason at a NEL; the no-verdict arm
  (`_stderr_tail`) does not escape at all; the pair collides at the FLAGFAIL window boundary (embedded middle).
  All four are byte-identical on the r89 and r90 tools (pre-existing), and every one lies outside the prereg's
  stated limit (i) — `_escape_text` for the delegated-stderr cell only. They are routed to r91 as a K4-record-level
  readability debt, not scored against C2.

## A3 — C1's row binds the dropped-guard spelling, not every malformed-guard spelling

- **Artifact:** `.ufo/waves/round-90/w1/S90MutCounter.md` §3 (six alternative spellings scored on both populations).
- **Measured:** LD2b kills `m17c` (the guard dropped) but an alternative grammar `len(r) != 3` still refuses the
  2-column row and would survive; `len(r) <= 2` and `== 2` also refuse it. So the frozen claim ("the guard is
  bound by one new population row") is true for the frozen mutant set, and the row does NOT bind a hypothetical
  `!=3` spelling. This is a limit of the row, not a falsification; the narrowing sentence is: *LD2b binds the
  `len(r) < 3` guard as the frozen `m17c-no-malformed` edit drops it; a `!= 3` rewrite of the same guard is not
  exercised by any row and is carried to r91 as a Q162 candidate.*

## A4 — C2's spelling sentence fails at the raw-window boundary; the claim is narrowed again

- **Artifact:** `.ufo/waves/round-90/w1/S90Reviewer2/receipts/c2-edge-probe.txt`;
  `.ufo/waves/round-90/w1/S90Sentinel.md` §5 H2d.
- **Measured:** a stderr of 101 `p` + the two-byte UTF-8 encoding of U+0085 + 98 `s` (201 raw bytes) is cut by the
  200-byte raw window as head-100 + `…` + tail-99; the tail starts on the SECOND byte of the character's encoding,
  so the carved window decodes that lone `0x85` as a surrogate and the cell reads `…\x85sss…` with no `\u0085`.
  The prereg's stated limit (ii) covered a stderr that differs from another only inside the elided middle (the SAME
  cell); it did not cover a CHARACTER whose own bytes are cut by the window.
- **Narrowed sentence (adds one clause to A1's):** *The character spelling holds when both bytes of U+0085 survive
  the raw window; a window cut inside the encoding renders the remaining byte as `\x85`, which no window can avoid.
  The fixture's KFF9/KFF10 payloads are short and do not exercise the boundary, so this clause is stated, not
  measured, and the boundary row is routed to r91.*
- **Second instrument gap, same artifact:** the KILL RULE's "each one physical line" is not enforced: a variant
  that appends a raw newline inside the K4 detail passes 12/12 because `len(rows)==1` counts MISMATCH rows and the
  fixture reads the row's fifth cell only. The filed tool's own detail is one physical line; the fixture cannot
  certify it. Folded into A1's instrument-gap list; no claim number moves.

## A5 — three instrument-precision clauses narrowed by the wave (no number moves)

- **Artifact:** `.ufo/waves/round-90/w1/S90Critic.md` § Verdict items 1–2; `.ufo/waves/round-90/w1/S90ExecC1.md`
  §1 precision notes; `.ufo/waves/round-90/w1/S90Reviewer2/receipts/measurements.txt`.
- **(a) Mutants "byte-identical":** the prereg's parenthetical "(the r89 sixteen byte-identical)" describes the
  sixteen MEMBERS, which are identical in id, order and `old`/`new` (`json.dumps(members, sort_keys=True)` hashes
  equal, `1a93a7b6…`); the FILE differs in its top-level `note` field (r89 `bc7e6bb1…` vs r90 `39252248…`).
  Narrowed: *the sixteen members are identical; the file is not byte-identical.*
- **(b) The battery does not print its own hash:** a stub battery that prints the target SUMMARY and exits 0 scores
  the literal predicate with zero runs; only the prereg's external pin `e7265335…` and the committed copy catch it.
  The claim's evidence therefore also rests on the pinned bytes, not on the SUMMARY line alone. Stated, routed to
  r91 as an instrument self-pin.
- **(c) The fixture does not bind the dead-code half:** a tool that applies only the U+0085 spelling and keeps
  `_one_line` still scores `tool_pass=12 before_pass=10` EXIT 0. The deletion is measured by the separate
  `grep -c 'def _one_line('` → 0 plus the module-load check, which the prereg names as the claim's second evidence;
  the fixture certifies the spelling pair only. Narrowed: *the fixture measures the pair; the deletion is measured by
  grep and load, not by the fixture, and a fixture row for it is routed to r91.*

## A0.7 — the wave's results record is L1-constructed (settlement defect, disclosed)

The wave spawned at 11:47:09 -03 (12 seats) and all twelve seat reports were complete under
`.ufo/waves/round-90/w1/` by 12:07, but no `w1-results.json` and no `WAVE-DONE` handoff arrived ~35 minutes after
spawn; an L0 line asks the orchestrator to settle/adopt the wave. To keep the round fileable without inventing any
seat output, the L1 wrote the results record from the dispatch task list and the presence/content of each seat's
report, with top-level `_source: l1-constructed` and a note. The pre-file gate reads it; every attack seat's report
is named in the ledger. This is the TameshiR96 class (a lane writing a driver artifact) and is recorded as a defect
of the settlement path. **Outcome:** three seats finalised their reports at 12:13–12:14 and the driver wrote its own
`w1-results.json`; the WAVE-DONE handoff at 12:16 -03 named it and it superseded the provisional L1 record. The final
wave bytes are committed at `47bd575b`. The provisional record is kept only as the LF disclosure; it is not evidence.
The L0 line asking for settlement was appended and needs no answer.
