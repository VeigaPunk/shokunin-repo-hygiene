# Report — S66ReviewerC2 (souji round 66 w1, C2 attack review)

Full detail with reproduction commands: `.ufo/waves/round-66/w1/S66ReviewerC2/review.md`.
Read-only attack of frozen instruments at `4576f101a9200206de00ef00923dd38a7b2dbc7d` /
`045e103478fa4a7eff77db2cab5b9e2f26959a0a`; counter/TSV sha256 pins verified MATCH; the frozen
do-nothing control receipt `census/round-66/controls/c2-do-nothing.txt` reproduced byte-identically
(`rows=5 findings=1 verdict=FAIL`, `MARKERS flag=1 inrun=1 env=1 unmerged=1 envcfg=0 envred=0`,
`EXIT=1`). No mutating command run anywhere; experiments lived in
`/fast/scratch/hyaku/souji-r66/S66ReviewerC2/`. No tooling installs.

## Findings

**MEDIUM-1 (check b) — the M10 regression selftest case is vacuous.**
`m10-returncode-line-not-live` (c2-counter.py L321–326) passes under BOTH the repaired and the
unrepaired emission rule: reverting `RETURN_LITERAL` to the r65 bare-substring rule leaves all 14
selftest cases green (`python3 -B /fast/scratch/hyaku/souji-r66/S66ReviewerC2/c2-counter-reverted.py
--selftest` → rc=0, zero MISMATCH). The case's blob is `S2_AFTER` but its row is s3, so the row
always resolves `GOVERNED-STATEMENT-UNRESOLVED` — marker-independent, hence it cannot pin the repair.
This round's kill-power is still real (measured below), but `--selftest` would not catch a future
reversion of the repair. Recommend the L1 record a lesson-class note; no frozen file touched.

**LOW-1 (check a) — RETURN_LITERAL matches 5 non-refusal lines at base (dormant overcount).**
`return "content"` ×2, `return "mode"` ×2 (L175/L177/L183/L186) and
`return "python3 -c " + shlex.quote(code)` (L853) match; none carries a needle, marker impact zero
at base. Kin of the r65 overcount, narrowed to string-literal returns.

**Check a (answered, proven).** New live_markers() counts a line r65 did not: empty set for ANY
writer (RETURN_LITERAL implies the `return` substring — verified over all 1374 base lines). Reverse:
r65 counts 140 lines r66 does not (emission set 182 → 42); exactly one carries a needle —
base L1129 `if r.returncode != 2 or os.path.exists(out3) or "RECEIPT-INDEX-ENV-SET" not in r.stderr:`
(the writer selftest's empty-GIT_INDEX_FILE assertion), the entire substance of round-65 M10. Shared
marker maps at base are identical (flag/inrun/env/unmerged all 1). RETURN_LITERAL's 4 remaining
matches are true refusal emissions (base L119, L123, L127, L130).

**Check c (answered, proven).** s5 is a stable row (`base_pattern == after_pattern` byte-equal);
`DUPLICATE-LIVE-WORDING` sits inside the `else:` of `if stable:` (c2-counter.py L157–170) and is
statically unreachable for every stable row (s1, s4, s5). Second occurrence of the s5 wording is
invisible (presence-only substring match) and benign this round; the counter cannot identify which
copy is the governed statement — inside the declared lexical named limit (L4), not a new defect.

**Check d (proven, double-guarded).** An always-zero counter exits 1 under both stubs on my scratch
copies: stub `live_markers` (all-False) fails the honest case itself and the control (`REJECTED`);
stub `evaluate` (always []) mismatches all 11 want≥1 cases and is forced red by
`ok = ok and not stub_zero` (L337–339) even while the control message prints
`ACCEPTED-FALSE-GREEN` (correct behavior, confusing wording). STUB-ALWAYS-ZERO cannot pass.

**Check e (answered, fail-closed).** Anchor test is exact stripped equality
(`line.strip() == 'if "GIT_INDEX_FILE" in os.environ:'`); base writer has exactly one hit (L278) and
the executor's pinned shape (w1-spec.json S66ExecWriter item 2) keeps exactly one. >1 matches are
impossible to score silently: c2-mutate.py refuses exit 2 (`anchor … occurs N times`). Residual LOW
fragility: `block = lines[i:i+3]` amputates unconditionally with only a needle-containment check —
safe only under the pinned 3-line shape; a 1-line refuse reflow would additionally delete the
following line and a deleted comment/blank would still compile (silent unrelated amputation).
Watch item for the L1's landing receipt (pin `removed_lines=3`).

**Check f (answered — falsifiable as written).** Both halves are single, deterministic,
read-printable commands over committed, sha-pinned artifacts; refutation = r66-on-mutant
`findings=0`, or r65-on-mutant `findings>=1`. Mechanism validated in-memory on base bytes with the
committed instruments' own code objects: M-ENV mutant of the base writer (1374→1371 lines,
`removed_lines=3`) gives r66 `env=False` → findings=1 (s2 `closed_full` SCOPE-OVERREACH; s5 stays
green, envcfg/envred untouched by M-ENV) while r65 `env=True` (carried solely by the surviving
returncode assertion line, base L1129 / mutant L1126) → findings=0 on the same green s1–s5 SKILL.md;
honest candidate map → findings=0. Caveats: (1) `findings>=1` does not pin the finding kind —
attribution rests on the honest `findings=0` run reading the same rev/SKILL.md; (2) the r65-blind
half silently requires the candidate to keep a residual env-needle on a `return`-substring line
outside the deleted block (today L1129; executor instruction 6 preserves it); (3) the predicated r65
run needs one scratch-clone commit (mutant bytes at `tools/souji-receipt-write.py`) per the prereg's
recipe — L1's job, not mine.

## Numbers measured
counter/tsc sha pins: MATCH/MATCH · base writer 1374 lines · RETURN_LITERAL matches 9 (5 non-refusal)
· emission lines r65 182 / r66 42 · r66∖r65 = ∅ (proved) · r65∖r66 = 140 (1 needle-carrying: L1129)
· do-nothing control reproduced byte-identical, EXIT=1 · r65 counter at base: findings=0 EXIT=0 ·
selftests: r66 14/14 rc=0; r65 13/13 rc=0; reverted-rule r66 14/14 rc=0 (the MEDIUM-1 evidence) ·
stub runs EXIT=1 both · M-ENV of base: 3 lines removed, anchor hits 0, residual env-needle lines 3 ·
mutant markers: r66 env=0 vs r65 env=1 · in-memory kill: r66 findings=1 / r65 findings=0 ·
s5 stable ⇒ DUPLICATE unreachable · anchor hits 1 (L278).

Report: .ufo/waves/round-66/w1/S66ReviewerC2.md
