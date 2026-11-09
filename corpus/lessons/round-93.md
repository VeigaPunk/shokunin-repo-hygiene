# Round 93 — two ledger-edit rows reach clauses no r92 run reached; a reference cut pins where the excerpt cut lands

Lane base `91c9bcb1041b18be154ca466ac3c047ac7862fe1` (r92 closed; spot-check
`corpus/lessons/round-92-verifier-spotcheck.md`). Instruments P1 `2c82d362`, controls P2 `0d6442cc`; freeze F
`9a4ab88f`; after receipts A `7bdb96b7`. Wave: one v1 wave, 13 seats, `w1`. Attempt 1 (SoujiR93).

## Claims

- **C1 (calibration 7, the lane's lowest owned non-retired axis).** Two counter edits survived every r92 row:
  `h-ok-admits-one` (R92MutC1 E1, line 552 `resolved >= len(pop) - 1`) and `a491c22-<-to-<=` (R92MutC1 §3c, `_ledger`
  width guard `len(r) <= 3`). Two rows of two new harness row types bind both edits: LD5 (`ledger-drop`, P04's own
  ledger row removed: UNRESOLVED, exit 1) and LD6 (`ledger-trim`, P04's row cut to three columns: MOVED, exit 0).
  Predicted in `census/round-93/c1-prediction.txt` (P1) before any r93-population mutant was scored. After
  `census/round-93/records/c1-after.txt` `killed=2 survived=0 errored=0`; control
  `census/round-93/controls/c1-control-r92-population.txt` `killed=0 survived=2`; pristine 66 rows, 0 mismatches,
  LD5 `rc=1`, LD6 `rc=0`. **VERIFIED as narrowed (A1, A2, A3).** A1: "because no r92 run reaches their clause" was
  false — both clauses run in every r92 run and h-ok flips three r92 exits on rows that assert no rc; it now reads "no
  r92 row asserts an outcome either edit changes". A2: the edits, not their clauses (m5/m6/g2 survive). A3: the kill
  rule still scores an uncaught counter exception (exit 1) as killed; both r93 kills are semantic (`got=UNRESOLVED`
  on the target row). A4: the harness needs two gitignored lane-disk paths (a clean clone reads `errored`).
- **C2 (coverage 8).** KFF18, the r92 fixture's cut-position case, checked only that the excerpt's head/tail are SOME
  prefix/suffix of the full rendering, so three forgeries that move the cut to the wrong place passed 20/20. KFF19
  compares the excerpt with the cell from a reference cut independent of the tool's implementation and of Python's
  codec (written from the WHATWG UTF-8 decoder, S356; it shares the excerpt-format constants) on 14,586
  boundary-class payloads; KFF20 mirrors KFF16 on the head cut. After `records/c2-forgery-after.txt` `rejected=8
  positive=pass`, `records/c2-after.txt` `cases=22 tool_pass=22 before_pass=16`, K4 12/0/0; control
  `controls/c2-control-r92-fixture-probe.txt` `rejected=5`, EXIT 1. **VERIFIED as narrowed (A5)**; 8/8 is a count over
  a chosen forgery set, so the coverage score does not move (A6).

## Gate

Sources opened this round (ids continue the registry after S355):

- **S356 — WHATWG Encoding Standard, §8.1.1 UTF-8 decoder** (https://encoding.spec.whatwg.org/#utf-8-decoder,
  Living Standard Last Updated 19 October 2026; HTTP 200, 591022 bytes, sha256
  `e1421f1791b202717883c452a6267129ce5fb3ca13652e5022a2b6d2a11fc262`, capture `census/round-93/srcs/encoding.html`,
  text `census/round-93/srcs/encoding.txt`; opened 2026-11-09 by the L1). Quote, §8.1.1, one occurrence in the
  whitespace-normalized tag-stripped text: "If byte is 0xE0, then set UTF-8 lower boundary to 0xA0. If byte is 0xED,
  then set UTF-8 upper boundary to 0x9F." (22 words.) **ADMIT**, `spec`, tier A, `mined` — grounds the C2 reference
  cut. Used by `corpus/knowledge/utf8-cut-position-reference.md`.
- **Python `codecs` `surrogatepass` handler — not a new row.** The forgery F5 is defined by it, but S351 already
  registers https://docs.python.org/3/library/codecs.html (the census warns W04 on the shared URL); a second row for
  the same page would add a duplicate, not knowledge. Reject for this round; flip if a claim rests on that handler's
  own wording.
- **WHATWG Encoding Standard §8.1.1, BOM precedence — REJECT sample, not filed** (same capture; R93ScoutSources §4).
  Quote, first sentence of §8.1.1 (it occurs twice in the document, again under §14.2.1; locator is the §8.1.1
  occurrence): "A byte order mark has priority over a label as it has been found to be more accurate in deployed
  content." (21 words.) **REJECT**: it governs label/BOM precedence at the decode entry point, which the section says
  is not part of the decoder algorithm; no r93 claim reads a BOM or a label, and S356's scope excludes them. Flip if a
  claim or fixture is widened to the decode / UTF-8 decode entry point, or the standard moves the BOM rule into the
  decoder steps.
- **S356 re-opened by a non-author seat**: R93ScoutSources fetched the page live on 2026-11-09 — HTTP 200, 591022
  bytes, sha256 identical to the capture (`cmp` exit 0); quote 22 words, one occurrence, under `id="utf-8-decoder"`;
  every decoder fact in the knowledge entry matched §8.1.1 (`.ufo/waves/round-93/w1/R93ScoutSources.md` §2-§3).
- Rows touched old→new: none (S356 appended only; R93Connector §4: one `+` line, zero `-` lines in
  `git diff 91c9bcb1 -- corpus/SOURCES.md`).

Census (before → after): `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → before
EXIT 0, 277 rows (`census/round-93/records/sources-census-before.txt`); after EXIT 0, 278 rows (S356 appended; `census/round-93/records/sources-census-after.txt`).

considerthese/: the lane has no `considerthese/` directory. Assimilation: none — no theme taken from
`/home/vgpnk/Projects/shokuknow/merge/souji/` (both claims came from the r92 spot-check's routed items).

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | concurrent background jobs in one tool call lost receipts: the L1 started three controls with `&`/`wait` in one shell call; the shell tool panicked and two receipts were never written | `plans/round-93.md` A0.2; `census/round-93/controls/` holds only completed runs | none — noticed because two files were missing | run receipt-producing commands one per call (sequentially), and check every expected receipt file exists before committing a control commit |
| M2 | the prereg named a seat role the validator refuses (`labrat`), because the round shape was written before the spec was validated; the first validator stderr was then overwritten by the re-run's redirect | `census/round-93/controls/labrat-role-refusal-repro.txt` (refusal reproduced, EXIT 1); `plans/round-93.md` A0.1 | the wave validator, after the freeze | validate the wave spec before freezing the prereg's ROUND SHAPE sentence, and write each validator run's stderr to its own file |
| M3 | a faithfulness property cited as a position check: r92's KFF18 (head a prefix, tail a suffix of the full rendering) holds for every boundary-respecting cut, so three forgeries that move the cut wrongly passed 20/20 | `.ufo/waves/round-92/w1/R92MutC2.md` (C/D/E); `census/round-93/controls/c2-control-r92-fixture-probe.txt` (`rejected=5`) | R92MutC2 (the r92 wave), not a rule | KFF19 exact equality against a reference cut written from S356; QUALITY Q169. Able to fail: the Q169 command prints `rejected=5` on the r92 fixture and `rejected=8` on the r93 fixture |
| M4 | the r93 kill-rule fix was worded wider than its test (the r92 M4 class, now inside the fix): the docstring says a crashed counter is `errored`, but an uncaught Python exception exits 1 and the harness reads `got=- match=no`, so `verdict()` returns `yes` | `.ufo/waves/round-93/w1/R93Sentinel/repro/h-crash3.out`; `R93Scribe/fk1-verdict.txt`; `R93MutC1.md` §2 k2; `plans/round-93.md` A3 | R93Sentinel, R93Scribe, R93MutC1 (this wave) | narrowed before filing (A3); QUALITY Q170 (cite a kill as semantic only with its killing row's printed `got`; test the rule with a crash-probe mutant). Able to fail: the crash probe reads `yes` today; routed fix: score `got=-` rows as `errored` |
| M5 | a causal clause written from reading, not measured: "survive every r92 row because no r92 run reaches their clause" — the instrument measures survival; both clauses execute in every r92 run, and h-ok flips three r92 exits on rows that assert no rc | `.ufo/waves/round-93/w1/R93ReviewerC1.md` §2 S2/S2a; `R93ReviewerC1/receipts/log-r92-hok.txt`; `R93Critic.md` item 1 | R93ReviewerC1, R93Critic | narrowed (A1) to "no r92 row asserts an outcome either edit changes", which `log-r92-*.txt` vs the r92 harness ROW lines measures; a claim's "because" clause needs its own receipt or is cut |

## Wave findings

Thirteen seats (3 executor, 2 reviewer, critic, 3 mutation-tester — R93Labrat ran as one, A0.1 —, sentinel,
connector, scout, scribe; the L1 holds the planner seat). All thirteen settled with a report in the lane wave dir
(`.ufo/waves/round-93/w1-results.json`); no dead seat; no fleet-root misroot (sweep in the report).

- **R93ExecC1 / R93ExecC2 / R93ExecResidual (neutral):** every predicate, control and pin re-derives; each kill is
  by its own target row (LD5 for h-ok, LD6 for a491c22); the edited ledgers differ from the r77 ledger by exactly
  P04's row; the 78-id residual set reads `killed=0 survived=78` on r92 and `killed=2 survived=76` on r93 (no
  errored, no hung); 300,000 random payloads, 0 filed-tool disagreements with the reference; no codec call in it.
- **R93ReviewerC1 (falsifies-wording, C1):** "because no r92 run reaches their clause" — narrowed A1.
- **R93Critic (falsifies-wording, C1/C2):** the "because" clause, "bind both", "independent", the coverage number;
  C1 is a construction with a verified residue; separability holds both ways; a clean clone reads `errored` (A4);
  KFF19 also rejects G1b (lookback 2) and G2-max3; reference vs codec 77,305,472 comparisons, 0 mismatches.
- **R93Sentinel (falsifies-wording, C1 kill rule; MEDIUM M2):** crash = killed (A3); the fixture's in-process cases
  let a tool's exception escape (under-count only). Ledger-edit writer confined to --work; duplicate/3-column items
  are setup errors as designed.
- **R93MutC1 (falsifies-wording via A2/A3):** m5/m6/g2 spellings survive (limit i); k1 exit-2 path `errored`, k2
  import crash `yes`; one-row attribution holds.
- **R93MutC2 (neutral):** 9 forgeries, 7 rejected; c_reprokey (limit iii), h_filler_a (limit i); a_window3 equivalent.
- **R93ReviewerC2 (falsifies-wording, precision):** the prefix/suffix sentence is KFF18's — narrowed A5; spec-vs-code
  16/16 boundary rows; KFF20 offsets derived.
- **R93Labrat (neutral):** SIGTERM/SIGINT exit 130 in ~0.5 s with zero trees and no live process; the r92 search
  strands trees on SIGTERM; SIGKILL strands on both.
- **R93Connector (neutral):** no sibling owns the surfaces; LD5's "exactly one unresolved" half is described, not
  asserted (measured holds); routed items table; SOURCES rule 2 compliant.
- **R93ScoutSources (neutral):** S356 live byte-identical; reject sample (BOM precedence).
- **R93Scribe (falsifies-wording, kill rule):** FK1; Q169 draft (landed); Mistakes drafts (M3-M5 here).

## Routed to round 94

1. Kill rule: score a ROW with `got=-` (or a counter traceback) as `errored`, not killed; re-run the r93 targets
   under it (A3, Q170).
2. Bind the clauses, not two spellings: m5/m6 (`len(pop) - len(unknown)` forms) and g2 (`len(r) not in (3, 4)`) —
   R93MutC1 names R1/R2 row shapes (a ledger-edit run with an unknown id plus an unresolved item; a 5-column row).
3. Assert LD5's descriptive half (`SUMMARY unresolved=1`), not only `ITEM P04` (R93Connector §2).
4. Harness reproducibility from committed bytes: the two gitignored lane-disk inputs (A4).
5. KFF19: a second payload length and filler (h_filler_a survives); the fixture's in-process exception handling
   (R93Sentinel M2); KFF20 mirrors for `ED A0 80` / `F4 90` leads.
6. Carried: the forge-return channel (limit ii), the 76 residual survivors' classification, the r91 variant tools, and
   the SCORECARD `### Planned (r93)` carried list.
