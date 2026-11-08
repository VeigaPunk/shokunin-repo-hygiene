# Round 91 — five rows bind the six surviving clauses; the excerpt cut learns sequence boundaries (and its invalid-lead residue is named)

Lane base `681f6c72b242d410d0e8654efadb2a1553fb111d` (r90 closed; spot-check
`corpus/lessons/round-90-verifier-spotcheck.md`). Instruments P1 `7fb865d8`, P2 `d287d3de`; freeze F `a703bcb7`;
after receipts `2836880`. Wave: one v1 wave, 13 seats, `w1`.

## Claims

- **C1 (calibration 7, the lane's lowest owned non-retired axis).** Six mutant edits survived every population the
  lane had pinned: `ld1c-class-keyed`, `ld1d-conflict-keyed`, `nf6i2-last-occurrence`, `nf6j-pathch-narrow`,
  `s1-exact-width`, `s3-equal-two`. Five new rows bind them: LD1c (identical duplicate — kills both duplicate-keyed
  spellings), LD3 (one-column ledger row — kills `len(r) == 2`), LD4 (`where=ledger-resolve` — item P04 must resolve
  MOVED through its unchanged 4-column entry, killing `len(r) != 3`), NF6i2 (R13: the token whole first, a suffix
  later — kills `line.rfind`) and NF6j (R13: the token after each of `. _ @ + ~ -` — kills the narrowed PATHCH).
  Measured: the r91 population reads `SUMMARY mutants=22 sets=r90,r91 pristine_r90=ok pristine_r91=ok killed_r90=16
  killed_r91=22 killed_total=38`, EXIT 0; the do-nothing control on r90 reads `killed_r90=16` with all six new
  members `killed=no` (`census/round-91/records/c1-after.txt`, `controls/c1-control-r90.txt`). **VERIFIED**, with
  STATED LIMITS (iii) narrowed before filing (A1).
- **C2 (operability 8).** The r90 tool cut its 200-octet excerpt at head-100/tail-99 without regard to UTF-8
  sequence boundaries, so a 201-byte stderr whose U+0085 (`C2 85`) straddles the tail cut printed the orphan `0x85`
  as the raw byte's spelling (S90Reviewer2 F1 / r90 A4). The filed tool moves both cuts to sequence boundaries
  before decoding; the r91 fixture adds the four clauses the r90 wording claimed but did not measure (doubled
  backslash spellings, the boundary case, one physical line, the `_one_line` scan). Measured:
  `SUMMARY cases=15 tool_pass=15 before_pass=14`, EXIT 0; the variant probe `SUMMARY variants=3 fixture=r91
  detected=3`, EXIT 0; the r90-fixture control `detected=0`; the r87 K4 counter `rows=12 mismatches=0 errors=0`,
  EXIT 0 (`census/round-91/records/`). **VERIFIED as narrowed** (A2): the tail cut is exact on valid UTF-8 but
  over-advances on a truncated/invalid lead before the cut, and KFF13 is a literal scan. Both residuals are routed
  to r92; no predicate number moved.

## Gate

Sources opened this round (each read here; ids continue the registry after S353):

- **S354 — RFC 3629, UTF-8, a transformation format of ISO 10646, §3 UTF-8 definition**
  (https://www.rfc-editor.org/rfc/rfc3629.txt, HTTP 200, 33856 bytes, sha256
  `a2a3a39457d30420c812f87a38cc2b9194832f6982ef17e619de7d816879d6a6`, capture `census/round-91/srcs/rfc3629.txt`,
  opened 2026-11-08; two independent GETs byte-identical, `R91ScoutSources`). Quote, §3, capture lines 183-185,
  occurrence count 1: "In a sequence of n octets, n>1, the initial octet has the n higher-order bits set to 1,
  followed by a bit set to 0." (25 words.) **ADMIT**, `docs`, tier A, `mined` — grounds the sequence-unit rule C2
  rests on. Used by `corpus/knowledge/utf8-window-sequence-boundary.md`. Locator line-model correction (old→new):
  the row's "capture lines 183-185" is LF-numbered; under `str.splitlines()` the same sentence is at 186-188 because
  the capture carries 14 form feeds (R91Connector F2; `R91ScoutSources` §1 calls the lines "unambiguous"). The row
  now reads "LF capture lines 183-185 (splitlines 186-188)".
- **RFC 3629 §10 Security Considerations — REJECT sample, not filed** (same URL, capture lines 523-570; header at
  523, quote at 525: "Implementers of UTF-8 need to consider the security aspects of how they handle illegal UTF-8
  sequences." 16 words, occurrence 1). **REJECT**: the section states hazard semantics of illegal-sequence handling
  (overlong `C0 80`, `2F C0 AE 2E 2F`, buffer sizing, normalization), not an octet-role/sequence-unit rule; §3
  already grounds C2 and the row's scope cell excludes security considerations. Flip only if a C2 sentence or case
  asserts a validity obligation on the excerpt, or an attack item is characterized as a security mis-parse
  (`R91ScoutSources` §3).

Census (before → after): `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → before
EXIT 0, 275 rows; after EXIT 0, 276 rows (S354 appended), W04 warnings only. The row landed with its `used-by`
entry in the same round, so E11 does not fire.

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | a cited path that does not exist: the r90 report ties the frozen claims to `census/round-90/claims.json`, but the frozen file is `.ufo/waves/round-90/claims.json` and no `census/round-90/claims.json` was ever committed | `corpus/lessons/round-90-verifier-spotcheck.md` §1 (report accuracy) and §7 item 1; `git ls-tree -r 93c7e6dc -- census/round-90/claims.json` prints nothing while `.ufo/waves/round-90/claims.json` resolves | the non-author spot-check's path resolution; the pre-file gate cannot catch it (it resolves only `artifact` cells) | this round's claims live at `.ufo/waves/round-91/claims.json`; the report cites that path only after `test -f`, and the round records the old→new correction in the report errata (plans/round-91.md A0.1) |
| M2 | an unowned count: the r90 report's "attack share 7/12 = 58 %" counts the pre-file gate's broader `ATTACK_ROLES` set while the lane's preregistration says 6/12 and the addendum's four-role definition gives 5/12; the sentence names no definition | `corpus/lessons/round-90-verifier-spotcheck.md` §1 (round shape) and §7 item 2; `.ufo/waves/round-90/w1-spec.json` `items[].role` | the spot-check's recomputation from the committed wave spec | the r91 prereg and report name ONE definition (addendum four roles: 2 reviewer + critic + mutation-tester = 4/13 = 30.8 %) and print the gate's broader count separately (7/13) |
| M3 | an instrument that enforces less than its sentence: `_cut_tail` advanced by the declared length of the first lead octet it found without checking that the continuation run was complete, so a truncated/invalid lead immediately before the tail cut could land the cut inside a LATER valid sequence and re-create the byte/character cell collision the round claims to remove | `.ufo/waves/round-91/w1/R91ExecC2Tool/repro-cut-tail-split.txt` (payloads `A`/`B`, `CELLS_EQUAL=True`); `.ufo/waves/round-91/w1/R91Scribe/cut-edge-probe.txt` (independent reproduction) | the round's own attack seats under Amendment 59; the frozen predicate (KFF11) used only a valid payload, so the counter was green on a narrower property | narrowed in plans/round-91.md A2 and routed to r92 with the exact predicate: require `end <= len(raw) and all(continuation for raw[i:end])` before moving the cut, add the C0/C1/F5-F7 range checks, and add head-cut and invalid-lead fixture rows; a fix counts only once the new rows fail on the r91 tool and pass on the repaired one |
| M4 | a spawned-seat count reported as the attack share: the prereg's 4/13 (2 reviewer + critic + mutation-tester) counts seats the spec spawned; two of the four (R91Critic, R91MutCounter) and two more ledger-role seats (R91Sentinel, R91Revenger) died on provider limits with no artifact, so the settled attack share is 2/13 and the C1 alternative-edit search never ran | `.ufo/waves/round-91/w1-results.json` (empty `output` for the four); `.ufo/waves/round-91/w1/dead-seats/*.json` (last error texts from the session files) | none for the share itself (the gate counts roles from results.json regardless of output); the prefile gate's `attack-seat-unread` forces each dead seat into the ledger — shown able to fail: a ledger copy without the four dead-seat rows exits 1 with four `attack-seat-unread` findings (`.ufo/waves/round-91/prefile-negative-control.txt`) | the report prints planned (4/13) and settled (2/13) attack shares separately and the ledger carries each dead seat as `neutral` with its record, never as a pass |

## Wave findings

Thirteen seats (4 executor, 2 reviewer, critic, mutation-tester, sentinel, connector, scout, scribe, revenger; the L1
holds the planner seat). The wave falsified the C1 limit-(iii) premise and two C2 sentences, all narrowed in
`plans/round-91.md` A1/A2 before filing:

- **R91ReviewerC1 (falsifies-wording, C1):** the LD4 base run is all-resolved (35/35, rc 0), so the stated reason for
  omitting an rc assertion is false; the status assertion alone kills the width-exact spelling. Every hash, the r90
  prefix, the counter bytes and both predicate SUMMARYs re-derive.
- **R91ReviewerC2 (falsifies-wording, C2):** KFF13 is a literal substring count; a real `def _one_line (` and
  `_one_line (` call scores 15/15. The filed tool is clean under AST.
- **R91ExecC2Tool (falsifies-wording, C2):** `_cut_tail` over-advances on a truncated/invalid lead; payloads `A` and
  `B` share a cell. It also found `_cut_head`'s `-> str` annotation on an int return and the structural
  (non-RFC-valid) range test; 1137 valid-UTF-8 payloads show 0 splits.
- **R91Scribe (falsifies-wording, C2):** independently reproduces the `_cut_tail` over-advance with a different
  payload (`A*101 + E0 + 85 C2 85 + B*96`).
- **R91Connector (F1, F2, F3):** the word "valid" is unbound (an RFC-conformant variant also scores 15/15); the S354
  locator's line model is LF, not `splitlines()`; the r91 population's comment lines are inherited from r90.
- **R91ExecC2Fixture (defect, KFF13):** a docstring that merely mentions `_one_line(` false-fails the scan; a spaced
  def/call false-greens. Both directions recorded; the false-green is A2's falsification.
- **R91ExecC1Battery (neutral):** deleting any one new row makes its mutant survive (pristine green on the 62-row
  copy), so each row has exclusive kill power; the control matches the prereg.
- **R91ExecC1Harness (falsifies-wording, C1 limit iii):** the same all-resolved premise, independently reproduced.
- **R91ScoutSources (neutral):** the S354 capture is byte-identical to two live re-fetches; quote 25 words,
  occurrence 1; the §10 reject has a specific flip condition; no duplicate URL.
- **R91MutCounter / R91Critic / R91Sentinel / R91Revenger (dead, no artifact):** each died on a provider limit before
  writing anything adversarial — Critic and Revenger `opencode-go/crouton-alpha-free` 429 rate limit, Sentinel
  `minimax-code` 429 token-plan limit, MutCounter `amr` 400 `tier_limit_exceeded` then devin `permission_denied`
  (last error texts in `.ufo/waves/round-91/w1/dead-seats/<seat>.json`, read from their session files). Never
  replaced. Consequence: the C1 alternative-edit survivor search and every critic/sentinel attack on both claims
  did not happen; the live attack seats are the two reviewers (2/13), plus falsifying executor/scribe/connector
  artifacts. The ledger lists each dead seat as `neutral` with its record, not as a pass.

## Routed to round 92

1. `_cut_tail` full-sequence validation, the C0/C1/F5-F7 range checks, head-cut and invalid-lead fixture rows, and
   the `_cut_head` annotation (A2; R91ExecC2Tool).
2. KFF13 via `ast` (defs and calls), with both the spaced-name and docstring-mention directions as fixture cases
   (A2; R91ReviewerC2, R91ExecC2Fixture).
3. LD4 asserts `rc=0` as well (A1; R91ReviewerC1).
4. The battery's `--expect-killed` split grip (assert `killed_r90` and `killed_r91` separately, not only the sum);
   the `new` strings' absence check (R91ReviewerC1 §8.1–§8.3).
5. The r91 population header names the r90/r91 rows rather than the r86/r81 ancestors (R91Connector F3).
6. The carried list in SCORECARD `### Planned (r91)` not taken this round (p2/p3/p7/p8, the `fleet:` symlink leg,
   the battery stale defaults, the r85/r86 C2 list, `_regular` pathspec framing, the quarantine intro-blob digest
   row, the r79 gate re-measurement, check-4 300 s backstop, r76 K03/K04, the r17 240 s runners).
