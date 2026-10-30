# Round 44 verifier spot-check — hyaku closure (non-author)

author: hyaku closure (non-author integrator, @m_zfl)
Date: 2026-10-30. Lane round: souji round 44. Lane base `55d7af6f5a22340f7a3de1c386e514ababfaa75f`;
lane HEAD `8376f442389f304340db2eab683b241694298188` (pushed, `ahead=0`). Report:
`.ufo/reports/round-44/souji.md`. I did not author this round; this file verifies it.

## Conformance results

| check | command | result |
|---|---|---|
| report committed by lane identity | `git -C /home/vgpnk/Projects/shokunin log --format='%an <%ae> %H' -- .ufo/reports/round-44/souji.md` | `souji-shokunin <souji@shokunin.local> 424b781ed2f1e97f08baadea5c98037217b950e4` |
| SHONEN heading, one line per box | `sed -n '/^## SHONEN/,$p'` on the report | `## SHONEN` present with four `[~]` lines + self-evaluation |
| report sections in contract order | grep of `^## ` | Work performed / Landed changes / Before → after measurements / Sources & frontier / Trend verdicts / SHONEN |
| cited lane commits exist and are ancestors | `git -C <lane> merge-base --is-ancestor <hash> master` (branch ref, not `@{u}`) | all seven cited hashes (`4641e146`, `6538a153`, `d314fd6e`, `39555219`, `c14d20a6`, `8376f442`, base `55d7af6f`) pass |
| no uncommitted round work | `git status --porcelain` | empty |
| pushed | `scripts/hyaku/jj-lane.sh state <lane>` | `branch=master local=8376f442… remote=8376f442… ahead=0 behind=0` |
| prompt carries template contract | read `.ufo/prompts/souji-round-44.md` | §1 mission/axes binding, §2 claims, §3 L2 floor (≥8, one batched call), §4 report contract (path, ordering, SHONEN heading, hash citation), §5 commit-then-push, push scope, L0 channel, §6 addendum — all present |
| report-after-commit ordering | author dates | lane `8376f442` authored 09:29:25 -0300 → report authored 09:30:21 -0300 → report committed 09:32:54 → driver complete 09:33:23. Committer date 09:31:17 on the lane commit is jj snapshot churn, not a violation |
| dispatch prompt durable | fleet log | committed as `c658069c` (`protocol-shokunin round-44: hyaku closure dispatch for souji`) |

Not a marker report: real committed work, resolvable hashes, full sections. Status-neutral defects found: none new; the round's own disclosures (attempt-1 lane-dead-no-report respawn; three temporary SCORECARD pointer mismatches at `39555219` repaired by `8376f442`; prompt-context "64 seats" misdescription while spec/dispatch/results enumerate 66) are recorded, not charged.

## Per-claim re-check (evidence-verified per Gate standard; source census re-measured live)

Claims resting on lane-owned gates/counters are verified against committed evidence only; I did not execute a sibling's gate.

### C1 calibration — claim DOES NOT VERIFY (lane-declared, confirmed)

- Before receipt: `git show 8376f442:census/round-44/records/c1-before.txt` → `SUMMARY population=70 corrections=0 registered=0 missing=70 … rederive_failed=70`, `EXIT=1` at freeze `d314fd6e`.
- After receipt: `…/c1-final.txt` → `SUMMARY population=70 corrections=66 registered=0 missing=70 junk=0 fenced=0 duplicate=0 retracted=0 rederive=0 rederive_failed=0 new_mismatches=0 instrument_mismatches=66`, `EXIT=1` at `c14d20a6`. `corrections=66` is the unique-key count, not accepted corrections.
- Freeze evidence: `census/round-44/records/freeze.txt` and `freeze-after.txt` both `SUMMARY claims=3 findings=0`, `EXIT=0`; `preregistration.txt` present (authored 08:20, before w1 handoff).
- Verdict: frozen predicate unmet, honestly frozen before scoring; no counter repair or target relaxation after scoring; `new_mismatches=0` confirmed — no calibration harm. Axis verdict: **unchanged** (score stays 7; C1 miss bars whole-round admission).

### C2 operability — finite target met, evidence-verified

- After receipt: `…/records/c2-after.txt` at `39555219` → `SUMMARY tool=present population=ok retention=ok hidden_v2=10/10 clean_stub=REJECTED findings_stub=REJECTED controls_ran=ok selftest=ok tmpdir=ok`, `EXIT=0`.
- Do-nothing control: `…/controls/c2-donothing.txt` retains the r43 oracle (`python3 -B census/round-43/c2-hidden-audit.py --tool tools/souji-freeze-check.py`) → `SUMMARY scenarios=10 pass=8 fail=2`, `EXIT=1`; retention red confirmed. First reading receipt `c2-first.txt` exists.
- Verdict: oracle-replacement target met as declared; lane's limits retained (fixed-case success is not authenticated execution; `S44mutationtester51`'s size-branching fake audit survives). Axis verdict: **unchanged** (score stays 8; no capability row claimed).

### C3 coverage — finite technical target met, evidence-verified

- Before receipt: `…/waves/w1/S44executor65/missing-fixture.stdout.txt` → `SUMMARY surface=RED tool_class=RED legacy=ok legacy_case=RED legacy_base=RED battery=RED battery_clean=RED battery_refuse=RED prior=5/5`, rc=1.
- After receipt: `…/records/c3-after.txt` at `39555219` → `SUMMARY surface=ok tool_class=ok legacy=ok legacy_case=ok legacy_base=ok battery=ok battery_clean=REJECTED battery_refuse=REJECTED prior=5/5`, `EXIT=0`.
- Parent-error regression: `c3-parent-before.txt` `SUMMARY cases=8 pass=6 fail=2 EXIT=1` → `c3-parent-after.txt` `SUMMARY cases=8 pass=8 fail=0 EXIT=0`; identical extended fixture, frozen tool; JSON-UNWRITABLE preserved.
- Verdict: joint cutover verified at finite scope (r38 legacy 12/12 + five named prior fixtures; not every historical suite, as declared); operator provenance open. Axis verdict: **unchanged** (score stays 8).

### Sources & frontier — re-measured live (not evidence-verified)

- `git show 55d7af6f:corpus/SOURCES.md | grep -cE '^\|\s*S[0-9]{3,}\s*\|'` → **187**; `git show 8376f442:…` → **189**. Matches report.
- Tier/status at final: `A=180 B=6 C=3`, `mined=157 queued=14 rejected=18`; at base `A=178 B=6 C=3`, `mined=156 queued=14 rejected=17`. Matches report (A+2, rejected+1, mined+1).
- `sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → `souji ok`, exit 0 (W04 duplicate-URL-across-scopes warnings only; S264/S265 intentionally share one URL across an admit and a reject scope).
- Wave census re-read from committed bytes: `records/wave-summary.json` → seats 66 (executor31/reviewer13/critic8/mutation-tester8/scout2/scribe2/connector2 = 66), nonempty 60, terminal errors 6 (S44critic41/42/43/44 MiniMax Token Plan 429; S44mutationtester53 Devin permission_denied; S44scribe64 Cursor USAGE_PRICING_REQUIRED), attack 29/66 = 43.9%. `records/seat-terminal-errors.json` lists the same 6 with exact events. `records/capture-committed.txt`: `verify-rev rev=c14d20a6… records=405 failed=0 uncovered=0 EXIT=0`.
- No axis harmed: `git diff 55d7af6f 8376f442 -- SCORECARD.md` is append-only (round-44 attribution limits, measurements table, planned section); axis scores untouched; Certification OFF / K5 HELD / NAMESPACE unchanged.

## Per-axis verdicts

| axis | verdict | basis |
|---|---|---|
| calibration | unchanged | C1 frozen predicate unmet (registered=0, exit1), honestly declared and frozen before scoring; `new_mismatches=0` at final; score row unchanged at 7 |
| operability | unchanged | C2 finite oracle target met with retained red control, score delta 0, no authenticated-execution claim, no capability row |
| coverage | unchanged | C3 finite cutover + parent-repair verified (6/8→8/8), score delta 0, operator provenance open |

## Spot-check table (LEARNING.md discernment)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S264 admit (C2 multiset vocabulary) | admit | `https://docs.python.org/3/library/collections.html#collections.Counter` re-fetched 2026-10-30; quote verified verbatim after tag-strip: "The Counter class is similar to bags or multisets in other languages." in the Counter objects class description (raw HTML wraps `Counter` in inline markup, so the raw-bytes grep misses; located receipt `census/round-44/sources/collections-located-quote.txt` matches) | agree | Quote real, correctly located, ≤25 words (13); admit scope limited to multiplicity vocabulary and explicitly not proof of scenario expectations; tier A (official docs) fits the scope |
| S265 reject (Counter semantics as oracle authority) | reject | same URL, same class description | agree | The source describes data-structure semantics, not this lane's audit grammar; admitting it as hidden-scenario authority would overreach. Flip condition (independent grammar derivation + non-crashing negative controls) is the right test |

Both sampled gate decisions agree with the outside check; no disagreement to learn from this sample. Q107/Q108 in `corpus/QUALITY.md` are lesson-grounded (motivating evidence cites `round-44.md` Mistakes and `S44critic48`), satisfying the "criterion with a lesson behind it" bar.

## Trend verdicts (closure)

- **expansion: unchanged** — no new `knowledge/` entry, no capability row, no Core move (CORPUS rule 4: rows are not knowledge). Source registry +2 rows is curation, not expansion.
- **quality: unchanged** — no admitted entry re-verified or superseded this round; instrument-level oracle repair with retained limitations is operational, not corpus-quality movement.
- **discernment: improved** — the round's admit (S264) and reject (S265) both agree with this outside non-author spot-check, which is the canonical `improved` condition in `LEARNING.md`; Q107/Q108 criteria carry lessons behind them. The lane pre-declared `unchanged` pending this check; with the check complete and agreeing, the verdict resolves to improved.

## Routed defects / carried items for round 45

1. **C1 instrument red (own defect, disclosed):** `census/round-44/c1-counter.py`'s inconsistent tuple order/arity keeps the honest 66-key register red (`instrument_mismatches=66`). Next round must freeze a feasible honest-register counter (consistent tuple identities, Q108-honouring population) — the SCORECARD planned row already binds this; do not reinterpret round 44's miss.
2. **C2 counter does not authenticate substance (own defect, disclosed):** a size-branching fake audit survives the repaired oracle (`S44mutationtester51`). Execution-bound audit attribution or a non-crashing discriminating negative control is needed before any operability score move.
3. **C3 operator provenance (open L0, operator-owned):** `souji | round-44 | Prior r43 verifier routed defect 5 asks for operator-level disposition…` — the defensive leaf-symlink contract awaits operator ruling; technical green is not approval. Route around it; never treat it as answered.
4. SHONEN boxes carry `[~]` with resolvable pointers and name no outside verifier — promotion review remains operator-owned; nothing here writes `[x]`.
