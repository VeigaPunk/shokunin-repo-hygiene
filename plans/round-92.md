# Round 92 — plan, pre-freeze notes, and claim amendments (pre-file falsification)

Written before the round report is filed. The frozen wording lives in `census/round-92/preregistration.txt`
(commit F `e8d31f06`) and is not edited here: each amendment records what the round's own artifacts falsified in
that wording, and the narrower sentence the round now puts its name to. Numbers are re-derived on committed bytes by
non-author seats and by the L1; records under `census/round-92/records/` and the wave's reports under
`.ufo/waves/round-92/w1/`.

Lane base: `5339b2ac79f81aa446f6a2cd4700321cf4982fd3` (r91 closed; its non-author spot-check
`corpus/lessons/round-91-verifier-spotcheck.md` is the outside discernment check this round answers).
Commits: P1 `44d45b44` (instruments), P2 `1d015a2d` (C1 control, full census, search `--timeout`), F `e8d31f06`
(preregistration alone), after receipts `e5059168`.

## A0 — pre-freeze notes and disclosures

- **A0.1 — attempt 1 left uncommitted work; attempt 2 adopted it after re-running it.** SoujiR92 (attempt 1) died
  when the orchestrator session was SIGTERM-killed before any wave was dispatched. It left: the C2 tool repair
  (`tools/souji-record-agreement.py`, `_straddling_sequence`), `tests/fixtures/r92-k4-flagfail.py`,
  `census/round-92/c1-survivor-search.py`, `census/round-92/c2-forgery-probe.py`,
  `census/round-92/controls/c2-before-tool.py` (= `git show 5339b2ac:tools/souji-record-agreement.py`, `cmp` equal)
  and the S355 capture `census/round-92/srcs/unicode-ch3.{html,txt}`. Attempt 2 re-ran the fixture (20/20 vs 16/20),
  the forgery probe (5/5), re-fetched the capture (byte-identical, sha256 `f9e158a6…`) and adopted all of them in P1.
  Nothing was discarded except attempt 1's scratch trees (see A0.2).
- **A0.2 — the survivor search filled /fast.** Attempt 1's search held every per-mutant harness work tree (a lane
  clone each); with attempt 2's own run the round's scratch reached 185 GB and pushed `/fast` to the fleet's 91 %
  hard limit (orchestrator message). Both runs were stopped and deleted; the search now removes each tree once
  scored (`census/round-92/c1-survivor-search.py` `score()`), and a later 47-mutant run left 5.4 MB.
- **A0.3 — one mutant never terminates.** `a272c34-1-to-0` turns `line.find(needle, i + 1)` into `line.find(needle,
  i)`, an endless loop; it stalled the full census twice (one orphan counter ran 2 h 36 min). P2 adds `--timeout`
  (process-group kill) and a `hung` count; the committed census reads `generated=270 ambiguous=9 uncompiled=0
  hung=1 scored=260 killed=136 survived=124` and its survivor set equals the set salvaged from two earlier
  interrupted runs.
- **A0.4 — the NF1r draft row was discarded before freeze.** A second exit-polarity row (NF1 with expect_rc 0) went
  red on the PRISTINE counter: the harness writes a non-dash expect_rc into the forge file as a MISMATCH
  expectation (`census/round-92/controls/nf1r-draft-probe.txt`). The population was rebuilt with LD4r only (64 rows)
  and the forge return is stated limit (ii).
- **A0.5 — the 47 targets were selected by a pre-freeze run.** `census/round-92/controls/c1-feasibility-r92-prefreeze.txt`
  scored all 124 survivors on the r92 population; the 47 it killed are the target set. Stated limit (vi) says so; the
  do-nothing control (`controls/c1-control-r91-population.txt`, `killed=0 survived=47`) was committed in P2 before F.
- **A0.6 — the C1 control was run twice.** The first run (pre-`--timeout` search) printed the same `killed=0
  survived=47`; its receipt was replaced in P2 by the run of the amended search, whose summary line carries the
  `hung=` field the predicate names.
- **A0.7 — the r91 spot-check's routed items.** (1) invalid-lead collision → C2; (2) KFF13 by `ast`, both directions →
  fixture self-check; (3) the survivor search → C1; LD4's `rc=0` → LD4r; (4) re-gate before any validity claim → S355
  (Unicode Table 3-7 / D86) is the validity source, RFC 3629 §3 (S354) keeps its sequence-unit scope; (5) population
  header hygiene → the r92 population's appended comment line names the r90/r91/r92 rows (the r91 prefix stays
  byte-identical, so the r91 header lines are not rewritten).
- **A0.8 — job counts.** The predicate commands name `--jobs 8` (and the full census `--jobs 10`); the wave was told
  `--jobs 4 at most` to bound scratch. The count is parallelism only: the kill rule reads each mutant's own harness
  exit, and R92ReviewerC1 re-derived the after, control and pristine lines with `--jobs 4` exactly (R92Scribe M4).

## A1 — C2: the frozen fixture does not bind "only across ONE well-formed sequence"; the claim is narrowed to what it certifies

- **Artifact:** `.ufo/waves/round-92/w1/R92MutC2.md` (forgery table) with receipts
  `R92MutC2/fixture_C_surrogatepass.txt`, `fixture_D_len_ge1.txt`, `fixture_E_head_fwd.txt` (each `rc=0`,
  `SUMMARY cases=20 tool_pass=20 before_pass=16`) and `R92MutC2/differ.txt` (D differs from the filed tool on 1,280 of
  1,536 payloads).
- **Frozen sentence falsified (as an instrument-certified sentence):** prereg C2 CLAIM, "The filed tool ... moves a
  cut only across ONE well-formed UTF-8 sequence (the candidate bytes must decode strictly to exactly one character,
  which applies every Table 3-7 row ...)". The predicate binds it only partly: three one-edit forgeries that move a
  cut too far — decoding with `surrogatepass` (a surrogate encoding ED A0..BF counts as a character), accepting a
  span of two or more characters (`len(...) >= 1`), and moving the head cut forward — all pass the r92 fixture 20/20.
  KFF18 checks that the head is a prefix and the tail a suffix of the whole rendering; an over-eager cut that elides
  whole extra units still satisfies that. The forgery probe's five named edits do not include them.
- **What survives:** every predicate number re-derives (R92ExecC2Fixture, R92ReviewerC2, R92Critic); the sentence is
  TRUE of the filed tool by reading (R92ReviewerC2 §3: the strict decoder matches every Table 3-7 row and rejects each
  ill-formed class) and by measurement outside the frozen predicate (R92ExecC2Sweep property (d): 200,000 seeded
  payloads, 0 filed-tool counterexamples; the r91 tool shows 9,120 head and 11,954 tail property-(d) violations). Forgeries B, F and G are rejected (KFF16, KFF11,
  KFF18); A is an equivalent mutant; H is the hardcode class of stated limit (iii).
- **Narrowed sentence (what this round puts its name to):** *The filed tool moves a cut only across one well-formed
  UTF-8 sequence — shown by source reading and by a 200,000-payload wave sweep, not by the frozen predicate. The
  frozen predicate certifies the 20 fixture cases (the A/B pair spelled distinctly, the overlong case, the head
  U+20AC case, the 29,700-payload prefix/suffix sweep, the `ast` KFF13 with its self-check), the rejection of five
  named forgeries, and the 12-row K4 regression; it does not reject a cut that moves too far (surrogatepass, a
  multi-character span, a forward head move).* Routed to r93: a maximality case (the excerpt equals the filed tool's
  exact window on boundary payloads, or a surrogate/2-character straddle row) so C, D and E go red.

## A2 — residuals recorded, no claim sentence falsified

- **C1 certifying power (R92Critic):** the 47 targets are, by construction, what LD4r kills (stated limit (vi)); the
  claim is reproducible-or-fail, not predictive. The control (`killed=0`) and the per-target attribution
  (R92ExecC1Cause: 14/14 sampled kills fail LD4r and only LD4r; 7 exit-polarity, 7 resolution) are what make it more
  than its own construction. Stated limit (iii) (kills may come from any r77 item) is confirmed, not contradicted.
- **KFF17 is not discriminating** (R92ReviewerC2): the r91 tool also passes it; the prereg's control sentence never
  claimed otherwise (red: KFF14/15/16/18).
- **KFF13 `exec` evasion** (R92ReviewerC2 §6.1): a runtime `_one_line` built from a string passes the `ast` check;
  the prereg wording ("no function definition ... no call") is about the parsed source and holds.
- **Search robustness (R92Sentinel M1, L1, L2):** a SIGKILLed search strands one clone per in-flight mutant
  (~0.65 GB); SIGINT drains the queue; the `/tmp` guard misses the bare `/tmp` path. Instrument defects, routed; no
  claim sentence depends on them.
- **The K4 regression and the fixture do not bind the tool's exit code** (R92Connector §5 note): consistent with C2,
  which asserts no tool exit code.

## A3 — C1: "kills" means "makes the harness exit non-zero on the listed edits", not "binds their clauses"

- **Artifact:** `.ufo/waves/round-92/w1/R92MutC1.md` §1 (FK1/FK2: an import-crash mutant and an argparse mutant are
  both scored `killed` by the frozen kill rule; receipts `R92MutC1/harness-import-crash-r92.txt`,
  `harness-argparse-r92.txt`) and §2 E1 (`ok = counts["resolved"] >= len(pop) - 1 and not unknown`, a different edit of
  the line-552 clause one target hits, survives both populations: `R92MutC1/harness-E1-ok-relaxed-r92.txt`).
- **Frozen sentences read wider than the evidence:** CLAIM "ONE appended row, LD4r ... kills the 47 survivors" with
  KILL RULE "a kill is a non-zero harness exit". The rule cannot tell a crash from a verdict change, and the word
  "kills" can be read as binding the clause.
- **What survives:** every C1 number (R92ExecC1Search, R92ReviewerC1 with `--jobs 4`, R92Critic, R92MutC1 §4); all 47
  filed kills are harness rc 1 with a row mismatch, none a crash (R92MutC1 §1c); in R92ExecC1Cause's 14-target
  sample LD4r is the only mismatching row in every case.
- **Narrowed sentence:** *On the r92 population LD4r makes the harness report a row mismatch and exit 1 for each of
  the 47 single-token edits listed in `census/round-92/c1-targets.json` (none is a crash); on the r91 population none
  of them does. LD4r binds those 47 edits, not the clauses they touch: an alternative edit of line 552 that tolerates
  one unresolved item survives both populations (R92MutC1 E1), and its binding row (a ledger-resolve run with exactly
  one unresolved item asserting rc 1) is routed to r93.*

## A4 — S355's anchor cell named the wrong id (source-locator sentence, not a claim)

- **Artifact:** `.ufo/waves/round-92/w1/R92ScoutSources.md` §2 and `R92ScoutSources/check_s355.out`: `id="G7404"`
  wraps the §3.9 heading; the Table 3-7 caption sits under `id="G27506"`.
- **Fix:** the S355 anchor cell now reads `id="G27506"` with the correction noted in the cell (old→new logged in
  `corpus/lessons/round-92.md` Gate). The quote, the D86 location and every Table 3-7 fact were confirmed (13 words,
  one occurrence; strict decode equals Table 3-7 on 17,535,232 candidates, 0 mismatches).
