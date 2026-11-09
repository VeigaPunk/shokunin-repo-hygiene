# Round 92 — a survivor census finds what no row asserted (exit 0 on success); the excerpt cut learns well-formedness

Lane base `5339b2ac79f81aa446f6a2cd4700321cf4982fd3` (r91 closed; spot-check
`corpus/lessons/round-91-verifier-spotcheck.md`). Instruments P1 `44d45b44`, P2 `1d015a2d`; freeze F `e8d31f06`;
after receipts `e5059168`. Wave: one v1 wave, 13 seats, `w1`. Attempt 2 (SoujiR92a2); attempt 1 died before any
wave and its uncommitted work was re-run and adopted (`plans/round-92.md` A0.1).

## Claims

- **C1 (calibration 7, the lane's lowest owned non-retired axis).** The single-token mutation census the r91
  mutation-tester never ran: 270 mutants of the frozen r87 counter, 9 ambiguous, 1 hangs, 260 scored, 124 survive the
  r91 population (`census/round-92/records/c1-search-r91-full.txt`). No r91 row asserted the counter's exit 0 on a
  successful run. One appended row LD4r (LD4 + expect_rc 0) makes the harness exit 1 on 47 of the 124
  (`records/c1-after.txt` `killed=47 survived=0`; control `controls/c1-control-r91-population.txt` `killed=0
  survived=47`; pristine 64 rows, 0 mismatches, LD4r `rc=0`). **VERIFIED as narrowed (A3)**: the row binds the 47
  listed edits, not their clauses (an alternative line-552 edit survives), and none of the 47 kills is a crash.
- **C2 (operability 8).** The r91 tool moved the tail cut by the lead byte's structural length, so an ill-formed lead
  absorbed the next well-formed sequence (payloads A/B shared a cell). The filed tool moves a cut only across one
  strictly decodable sequence (Unicode Table 3-7, S355). Measured: `cases=20 tool_pass=20 before_pass=16`, forgery
  probe 5/5, K4 12/0/0; control the r91 tool 16/20, EXIT 1. **VERIFIED as narrowed (A1)**: the frozen fixture does not
  reject a cut that moves too far (surrogatepass, multi-character span, forward head move pass 20/20); the
  one-sequence property rests on source reading and a 200,000-payload wave sweep (0 counterexamples).

## Gate

Sources opened this round (ids continue the registry after S354):

- **S355 — The Unicode Standard 18.0.0, Chapter 3 Conformance, §3.9 (D84a–D86, Table 3-7)**
  (https://www.unicode.org/versions/latest/core-spec/chapter-3/ → https://www.unicode.org/versions/Unicode18.0.0/core-spec/chapter-3/,
  HTTP 200, 428731 bytes, sha256 `f9e158a640c88cb0aebf60e5f724ea4f957eca539c620fb1e161cb6c8f8fb22e`, capture
  `census/round-92/srcs/unicode-ch3.html`; opened 2026-11-08 by the L1 (attempt 1's capture re-fetched
  byte-identical) and 2026-11-09 by R92ScoutSources (live `cmp` identical)). Quote, §3.9 D86, one occurrence in the
  whitespace-normalized tag-stripped text: "Ill-formed code unit subsequences do not overlap with minimal well-formed
  code unit subsequences." (13 words.) **ADMIT**, `docs`, tier A, `mined` — grounds the C2 cut rule. Used by
  `corpus/knowledge/utf8-window-well-formed-cut.md`. Anchor cell old→new (A4): `id="G7404"` (the §3.9 heading) →
  `id="G27506"` (the Table 3-7 caption), R92ScoutSources `check_s355.out`. The entry's five Table 3-7 facts were
  checked row by row against the capture, and strict decode equals Table 3-7 on 17,535,232 candidates (0 mismatches).
- **§3.9 D93b, maximal subpart of an ill-formed subsequence — REJECT sample, not filed** (same capture; normalized
  offset 145946, one occurrence: "This definition of the maximal subpart is used in describing how far to advance
  processing when making substitutions" (18 words)). **REJECT**: D93b governs how far a U+FFFD substitution advances;
  the tool escapes ill-formed bytes and never substitutes, and no r92 sentence uses U+FFFD. Flip if the tool starts
  substituting U+FFFD or a claim asserts a cut on a maximal-subpart boundary (R92ScoutSources §4).
- **RFC 3629 §4 (S354's document, not a new row).** R92Connector §4 compared the §4 ABNF with Table 3-7: the same
  well-formed set (0 disagreements), but §4 is a whole-string grammar that disclaims authority and has no term for
  the sequence a cut lands in; the r91 spot-check's routed item 4 is answered by grounding the rule on S355, with
  S354 keeping its §3 sequence-unit scope.

Census (before → after): `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → before
EXIT 0, 276 rows (`census/round-92/records/sources-census-before.txt`); after EXIT 0, 277 rows (S355 appended;
`records/sources-census-after.txt`), W04 warnings only.

considerthese/: the lane has no `considerthese/` directory. Assimilation: none — the `/home/vgpnk/Projects/shokuknow/merge/souji/` package exists, but this round took no theme from it (both claims were fixed by the r91 spot-check's routed items).

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | a fan-out runner kept every per-candidate lane clone: the survivor search passed each mutant its own harness `--work` and never removed it, so attempt 1's run plus attempt 2's held ~260 clones and the round's scratch reached 185 GB, pushing `/fast` to the fleet's 91 % hard limit | orchestrator disk message (attempt 2 transcript); `plans/round-92.md` A0.2; `census/round-92/c1-survivor-search.py` `score()` | none in the lane — the orchestrator's disk guard; addendum §7 rule 3 names the class but no lane check enforced it | delete each tree once scored; Q168. Shown able to fail: `census/round-92/records/m1-cleanup-fail-check.txt` — 44 KB with the cleanup, 369,072 KB for one mutant with the line removed (R92Scribe E1 reproduces 0 vs 47 trees) |
| M2 | an expectation cell whose meaning differs by row type: the NF1r draft (NF1 + expect_rc 0) went red on the PRISTINE counter, because the harness writes a non-dash rc on a forge row as a MISMATCH expectation | `census/round-92/controls/nf1r-draft-probe.txt`; reproduced `.ufo/waves/round-92/w1/R92Scribe/receipts/run-nf1r.txt` | the pre-freeze pristine run (red), not a rule | row dropped before freeze, stated limit (ii); Q167 count (0 on r91/r92, 1 on the draft — able to fail) |
| M3 | a census with no per-candidate deadline: mutant `a272c34-1-to-0` loops forever in `line.find`, so the full census stalled twice and one orphan counter ran 2 h 36 min | `plans/round-92.md` A0.3; `census/round-92/records/c1-search-r91-full.txt` (`hung=1`) | none — found by noticing no output after 90 min | `--timeout` with a process-group kill and a `hung` count, plus line-by-line output (Q168). Shown able to fail: without it the census printed nothing for 90 min; with it the same mutant is `SKIP … state=hung` |
| M5 | a seat report misrooted to the fleet root: R92ScoutSources resolved its `Report:` trailer from the fleet root despite the context's absolute-path instruction | fleet-root `git status --porcelain` showed `?? .ufo/waves/round-92/` holding only `w1/R92ScoutSources.md` (sha256 `5d76cd56…`), the lane copy a 82-byte skeleton | the §3 misroot sweep before the report | copied byte-exact into the lane (`cmp` equal), fleet copy deleted; the next spec puts the absolute report path in each item's Target line, not only in the context |
| M4 | a sentence wider than its instrument (the r91 class again, on both claims): C2's "moves a cut only across ONE well-formed sequence" is not rejected by the frozen fixture for over-moving forgeries, and C1's "kills" reads as clause binding while the rule counts any non-zero exit | `.ufo/waves/round-92/w1/R92MutC2.md` (C/D/E 20/20); `R92MutC1.md` §1, §2 E1 | the round's own mutation-testers, before filing (Amendment 59 ledger) | narrowed in `plans/round-92.md` A1/A3; maximality case and an E1-binding row routed to r93 |

## Wave findings

Thirteen seats (4 executor, 2 reviewer, critic, 2 mutation-tester, sentinel, connector, scout, scribe; the L1 holds
the planner seat). All thirteen settled with an artifact (driver `w1-results.json`). R92ScoutSources wrote its final report to the FLEET root
(`/home/vgpnk/Projects/shokunin/.ufo/waves/round-92/w1/R92ScoutSources.md`) and left only a skeleton in the lane; the
misroot sweep copied it byte-exact into the lane path (`cmp` equal, sha256 `5d76cd56…`) and deleted the fleet copy (M5).

- **R92ExecC1Search / R92ReviewerC1 / R92Critic (neutral):** every C1 number, pin, prefix and set equality
  re-derives; the r92 harness differs from r91 by a docstring and one pin.
- **R92ExecC1Cause (neutral):** 14/14 sampled targets fail LD4r and only LD4r; 7 exit-polarity, 7 resolution (a
  different r77 item turns unresolved) — stated limit (iii) confirmed.
- **R92MutC1 (falsifies-wording, C1):** the kill rule scores crashes as kills (none of the 47 is one); an alternative
  line-552 edit survives. Narrowed A3. Residual triage of the 77 into five classes, routed.
- **R92ExecC2Fixture / R92ReviewerC2 / R92ExecC2Sweep (neutral):** every C2 number re-derives; Table 3-7 equals the
  strict decoder; 0 counterexamples in 200,000 payloads; KFF17 does not discriminate (never claimed); KFF13 is
  evadable by `exec` (wording holds).
- **R92MutC2 (falsifies-wording, C2):** surrogatepass, a multi-character span and a forward head move pass 20/20.
  Narrowed A1.
- **R92Sentinel (neutral; instrument defects):** SIGKILL strands in-flight clones, SIGINT drains, the bare-`/tmp`
  guard gap, `--shared` clones touch lane object mtimes. Routed.
- **R92Connector (neutral):** no sibling owns the surface; the cross-claim pattern (rows that assert a marker but no
  exit code; the K4 counters print `rc=` without testing it); RFC 3629 §4 vs Table 3-7; the r93 draft.
- **R92ScoutSources (falsifies-wording, S355 anchor cell):** `G7404` → `G27506`, fixed (A4).
- **R92Scribe (neutral):** M1–M3 drafts with able-to-fail checks; Q167 draft (landed).

## Routed to round 93

1. Bind the forge return through a separate exit-expectation channel; make exit polarity required on resolving rows
   (R92Connector §6); a ledger-resolve row with exactly one unresolved item asserting rc 1 (kills R92MutC1 E1).
2. Classify the 77 residual survivors; name the equivalent mutants (R92MutC1 §3).
3. A C2 maximality case so surrogatepass / multi-character / forward-head forgeries go red (A1); an ill-formed lead
   before the head cut.
4. Search robustness: try/finally cleanup and process-group kill on SIGTERM/SIGINT, `cancel_futures`, the bare-`/tmp`
   guard, `git clone --no-local` in the harness (R92Sentinel M1, L1–L3).
5. The carried list in SCORECARD `### Planned (r93)`.
