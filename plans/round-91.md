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

## A1 — (filled after the wave)

## A2 — (filled after the wave)
