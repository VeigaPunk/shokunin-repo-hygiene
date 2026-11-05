# S67ConnectorOverlap — cross-claim map (read-only)

Frozen basis: `census/round-67/preregistration-attempt4.txt` (freeze `4c61efcb`). C1 = operability, receipt-binding,
31-row matrix, `GIT_COMMON_DIR` value check. C2 = calibration, bookkeeping-file, pinned state `c13fbb4e`, `FINDING SCOPE-OVERREACH s5`.

## 1. Routed items and where they land

| # | routed item (source) | rides | evidence in the frozen state | note for L1 |
|---|---|---|---|---|
| R1 | `GIT_COMMON_DIR` route, W2 (r66 spotcheck item 2; lesson "C1 GIT_COMMON_DIR open") | **C1** | matrix W1 (refuse, COMMONDIR-MISMATCH), W2 (refuse), W3 (accept, honest); base-writer `grep GIT_COMMON_DIR` = 0; the probe `census/round-67/probes/l1-w2-repro.md` P1 reproduces base accept rc 0 | Covered by the frozen predicate. Seat owners: S67ExecWriter (bytes), S67ReviewerDesign, S67SentinelScope, S67RevengerProbe (attacks). |
| R1b | "route sweep of git's environment surface as a frozen enumeration" (r66 spotcheck item 2; lesson routed item 1) | **outside C1 predicate**, only partly covered | prereg freezes only the GIT_COMMON_DIR route; L3 names `GIT_NAMESPACE`/`GIT_CEILING_DIRECTORIES` as not refused | **Gap to state.** The prereg does not freeze a git(1) environment enumeration. The report must say the sweep is narrowed to GIT_COMMON_DIR and L3 carries the rest. Not a blocker under the frozen predicate, but it is not "done" as the r66 lesson asked. |
| R1c | repository-local `core.fileMode=false` / ignore keys hiding changes | **named limit** (prereg L1) | the W2 note: "the repository's own core.fileMode=false is the same config read" | Stays open. L0 361 routed around by the value-aware rule (equal value is accepted, so no answer is needed for the common-dir path). |
| R2 | vacuous M10 selftest guard, M4 (r66 M4; lesson routed item 2) | **C2** | `c2-counter.py` case `m10-s5-assertion-line-not-live` binds the M10 shape to the s5 row (docstring lines 6-19). Probe P4 (`l1-w2-repro.md`): the first draft was vacuous and was repaired before freeze, measured by the reverted-rule recipe | Claim-bound. Attack seats: S67ReviewerC2, S67MutKill. |
| R2b | docstring defect, M6 (r66 M6; lesson routed item 2) | **label mismatch** | the prereg lists "C2: M4, M7, M6", but the M6 correction lives in `census/round-67/c1-counter.py:76-78`, the **C1** counter. `c2-counter.py` has no M6 text. | No predicate effect (docstring only). Record that M6 is in the C1 instrument, so the prereg label and the file disagree. Report as a mislabel, not a defect. |
| R2c | s4 population note, M7 (r66 M7) | **C2**, but not machine-checked | `c2-statements.tsv` note column is bookkeeping; `c2-counter.py` docstring says notes are not checked (lines 20-24) | C2 cannot falsify this. It is a frozen-cell fix plus the lesson record. |
| R3 | s5 scope overreach / object-redirect closure, M5 (r66 M5; lesson routed item 3) | **C2** (verdict) and **C1** (the route it names) | C2 token `redirects_closed` needs `envred` and `cdred` (`c2-counter.py` docstring lines 13-19). At the pinned `c13fbb4e` writer there is no `cdred`, so s5 fires. | Separability holds: C2's verdict reads the pinned writer, not the candidate. See §3 for the post-landing inference. |
| R3b | s5 wording ruling, L0 362 | **outside**, routed around | the r66 wording stays frozen; C2 is pinned, so the claim neither needs nor permits an edit | L1 must not edit s5 in SKILL.md at landing (the frozen claim wording is not amended). |
| R4 | kill power K3/K4/K6/K7 (r66 named limit; lesson routed item 6) | **outside** (wave seat S67MutKill; "defence in depth" decision) | not in either claim's predicate | The W1/W2 fixtures are the mode-hiding fixture the r66 lesson said K6/K7 lacked. Whether that kills K6/K7 is for S67MutKill to measure, not inferred here [INFERENCE]. |
| R5 | honest-run refusal under `git -c` (W3/L2 trade; L0 360; prereg L6) | **outside**, unchanged | the r66 `RECEIPT-ENV-CONFIG-SET` predicate is unchanged; `git -c` children are still refused | Operator ruling pending. Not claimed as an improvement. |
| R6 | E3 wording, `GIT_CONFIG_GLOBAL` "refuses" vs repoint (M8) | **outside** | the matrix E3 class is `lane worktree is dirty` on both slots | Operator wording ruling; no predicate change. |
| R7 | receipt grammar, `rev=` the measured revision (chronology) | **outside the claim predicate, but it gates C1's After receipt** | `c1-counter.py:1004` sets `measured = ns.rev if ns.rev else ns.base_rev`. So a C1 After receipt produced with `--rev <candidate>` carries the candidate (a descendant of the freeze). The do-nothing control carries the base, which is correct. | Produce `records/c1-after.txt` with `--rev` and `--receipt`, never by hand (the r66 mistake). Then run `souji-freeze-check.py --chronology` on the landing; it should show no RECEIPT-MEASURED-BEFORE-FREEZE. C2 has no After line, so the chronology arm does not apply to it (prereg). |
| R8 | Q129 correction, QUALITY row (r66 spotcheck item 7) | **outside** (landing duty) | the live lane tree has an uncommitted row **Q130** in `corpus/QUALITY.md` (`git diff --stat`: 1 insertion) | See §3: attribute the edit before landing. |
| R9 | L0 line 360/361/362 | 360 outside; 361 routed around (C1 named limit L1); 362 routed around (C2 pinned; no s5 edit) | prereg "Routed items handled outside the claims" | Consistent with the frozen text. |

## 2. Which claim each routed item rides

- C1 carries: R1 (GIT_COMMON_DIR, W1-W3), part of R1c (the ignore/config named limit).
- C2 carries: R2 (M4), R2c (M7 note, not machine-checked), R3 (M5 scope, pinned).
- Outside both: R1b (enumeration, partly), R2b (M6 label), R3b (L0 362), R4 (K3/K4/K6/K7), R5 (L0 360), R6 (M8), R7 (chronology gating, a C1 receipt tool), R8 (Q130), the honest-run trade.

## 3. Separability and post-landing inference

- C1 and C2 are separable as the prereg says: C2 reads only pinned bytes (`c13fbb4e` writer, the instruments commit population);
  C1 reads only the candidate bytes.
- [INFERENCE, unmeasured] After C1 lands, the live SKILL.md s5 sentence ("closed for the caller-injected config and
  object-redirect routes by RECEIPT-ENV-CONFIG-SET and RECEIPT-ENV-REDIRECT-SET") would be a true statement about the
  three names it lists, but it still names only the r66 refusals. Whether the C2 counter, run at a landed head, scores it
  findings=0 depends on the `cdred` rule, and the instrument reads the live SKILL text. C2's frozen verdict is at the pinned
  state, so this does not move the claim. It does mean the lane will carry a SKILL statement that a later counter run could
  score differently. Name it in the report; do not edit s5 (L0 362).

## 4. File-boundary overlaps between seats (coordination notes for L1; not blockers)

Seat list from `w1-spec.json` (10 items): S67ExecWriter, S67MutKill, S67ReviewerDesign, S67ReviewerC2, S67CriticClaims,
S67SentinelScope, S67ScoutSources, S67ScribeEntry, S67ConnectorOverlap (this seat), S67RevengerProbe.

| boundary | seats touching it | overlap | coordination |
|---|---|---|---|
| `tools/souji-receipt-write.py` (lane) | S67ExecWriter writes candidate bytes under its own dir; S67RevengerProbe, S67SentinelScope, S67ReviewerDesign, S67MutKill read it | read-only for all but the writer; L1 copies | L1 copies the candidate only after the sha and selftest checks; attacks read the candidate directory, never the lane path |
| `census/round-67/*` frozen instruments and matrix (`c1-counter.py`, `c1-matrix.tsv`, `c2-counter.py`, `c2-statements.tsv`, `c2-mutate.py`) | S67ExecWriter's spec lists `c1-counter.py` and `c1-matrix.tsv`; S67ReviewerC2, S67MutKill, S67CriticClaims read them | frozen; any seat edit would be a freeze breach | confirm S67ExecWriter's report says read-only for these paths |
| `corpus/QUALITY.md` | S67ScribeEntry's spec lists it, and its rule says "do NOT edit lane files". The live lane tree has an uncommitted Q130 row. | **Unattributed edit in the live tree** | L1 to confirm which actor wrote it. If it was ScribeEntry, that breaks the no-lane-edit rule. If it was L1, it is the planned landing. Land it through the lane helper only. |
| S300 source id | S67ScoutSources (`quotes.tsv`, the environment.c and worktree.c captures) and S67ScribeEntry (the knowledge-entry provenance trio) both name S300 | id assignment | L1 assigns the registry id once; scout supplies the capture; scribe cites it |
| `corpus/knowledge/` | S67ScribeEntry drafts `common-dir-route-receipt-writer.md`; the r66 entry `corpus/knowledge/caller-env-routes-receipt-writer.md` already names GIT_COMMON_DIR as open (line 42) | **topic overlap** | Recommend the L1 amend or fold into the existing entry instead of adding a second entry on the same route (the shokuknow merge checklist's fold rule, applied by analogy) |
| `corpus/lessons/round-67.md` | S67ScribeEntry's spec lists it | lesson ownership | the lesson is an L1 landing; the scribe supplies a draft only |
| `census/round-67/controls/*`, `records/*` | ScribeEntry and CriticClaims read controls; `records/c1-after.txt` is L1-produced | read vs write | records are produced by the L1 with `--rev` and `--receipt` (see R7) |

Roster note: the live roster also lists peers without the S67 prefix (for example ExecC2V2, ExecMutVerify, ReviewC1-25,
MutC1-6). They are not in this wave's 10-item spec and were not assessed.
