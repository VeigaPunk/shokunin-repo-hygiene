# R41w2executor05 — SKILL.md Gate-registry rows for the r41 gates (draft)

Tip measured: `1d41c13574db80fdd9a4bde490b712da7ce2a85f` (lane HEAD, clean, uid 1000). Scratch `/fast/scratch/hyaku/souji-r41/R41w2executor05/` (deleted; outputs pasted below). SKILL.md not edited.

## Deliverable
`.ufo/waves/round-41/w2/R41w2executor05/skill-rows.md` — five exact 8-column rows (9 pipes each, verified by script): `souji-freeze-check`, `r41-freeze-check-cases`, `r41-refusal-sites`, `r41-drift-record-order`, `r41-c1-corrections`. Verdict maps are copied from each artifact's own docstring `Exit:` lines (tool: lines 8, freeze-check; c2-counter L56; c3-counter L31-32; r1-counter L31-32; c1-counter L34-35; fixtures: r41-drift-record-order L22 and r41-refusal-sites main()). Placement: append after the last gate row (`r38-drift-mutants`, SKILL.md L281).

## Commands run (all with TMPDIR and --scratch/--work under my scratch) and observed output
All green arms at `--rev 1d41c13574db…`:
- `python3 -B census/round-41/c1-counter.py --root LANE --rev TIP --scratch S` → `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1`, rc=0
- `python3 -B census/round-41/c2-counter.py …` → `SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=3c3e80baedd8`, rc=0 (`real ok rc=0 findings=0 summary=(3, 0)`, `retro red rc=1 findings=18 summary=(3, 18)`)
- `python3 -B census/round-41/c3-counter.py …` → `SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=f32022e28fe2`, rc=0
- `python3 -B census/round-41/c3-counter.py --selftest --scratch S` → `SELFTEST cases=3 fail=0`, rc=0 (perfect killed=3, stub survived=3, rc-only survived=3)
- `python3 -B census/round-41/r1-counter.py …` → `SUMMARY mutants=11 killed=11 survived=0 pristine=ok regress=8/8 new_killed=3/3 old_fixtures_killed_new=0 prior=6/6 cases=12 tool_sha=b2a603cf4247 fixture_sha=a2880a914106`, rc=0
- Fixtures directly: `python3 -B tests/fixtures/r41-refusal-sites.py --tool tools/souji-worktree-drift.py --work S/f1` → `SUMMARY probes=21 pass=21 fail=0` rc=0; `python3 -B tests/fixtures/r41-drift-record-order.py --tool … --work S/f2` → `SUMMARY cases=12 pass=12 fail=0` rc=0.
- Tool entry: on `census/round-41/preregistration.txt` → `SUMMARY claims=3 findings=0` rc=0; on `census/round-40/preregistration.txt` → last lines `FINDING C3 FIELD-MISSING Population`, `FINDING C3 FIELD-MISSING Target`, `SUMMARY claims=3 findings=18` rc=1.

Red arms (the self-test cell's failing arm), via `score-candidate.sh` with the committed controls:
- c1 + `controls/c1-junk-round-41.md` → `SUMMARY items=3 mismatched=3 corrected=0 uncorrected=3 junk=3 rewritten=0 sourced=0` rc=1
- c2 + `controls/c2-stub-clean.py` → `SUMMARY cases=21 pass=2 fail=19 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=FAIL tool_sha=5ccb4fb2705b` rc=1
- c3 + `controls/c3-stub-fixture.py` → `SUMMARY sites=19 probes=21 pristine=ok killed=0 survived=19 misattributed=0 docclasses=10 …` rc=1
- r1 + `controls/r1-stub-fixture.py` → `SUMMARY mutants=11 killed=8 survived=3 pristine=ok regress=8/8 new_killed=0/3 old_fixtures_killed_new=0 prior=6/6 cases=8 …` rc=1

Exit-2 (could-not-evaluate) arms exercised, each printing `REFUSAL COULD-NOT-EVALUATE: …` and rc=2: freeze-check `--rev HEAD` (not full40); c1 `--rev abc`; c2 `--scratch /nonexistent`; c3 `--rev abc`; r1 `--rev abc`. Fixtures: refusal-sites with no args → argparse usage rc=2; drift-record-order `--work /nonexistent` → `usage: --work must name an existing directory` rc=2.

## Checks on the row contents
- Every `.py`/`.sh` path cited in the rows (10 paths) exists at the tip (`git cat-file -e`), so the landing gate's LG-MISSING-REG / LG-PARSE-REG will not fire on them.
- Counter digests quoted in the rows equal the prereg's frozen `Counter:` lines (`sha256sum`): c1 `8860dc7a…`, c2 `85ffe263…`, c3 `9ef99e8f…`, r1 `8352eed4…`; population digests `c1-items.tsv`, `c2-cases.tsv`, `c3-sites.tsv` and tool `b2a603cf…` re-hashed and equal.
- c2 population consistency: `c2-cases.tsv` lists 21 names; the counter's embedded `CASES` (19) plus `unresolved-rev`/`absent-prereg` equal the same 21 (set difference = exactly those two).

## Findings / limits (not fixed; read-only item)
1. The named models `r40-c1-evidence`, `r40-docstring-joined` do not exist in SKILL.md at the tip (grep `r40|r41` = no match); I modelled rows on `r38-*`/`r39-*` rows (`r39-citation-rev`, `r38-drift-mutants`, `c2-counter (r39)`).
2. `souji-freeze-check` has no embedded selftest; its self-test cell therefore points at the C2 counter (a legitimate failing arm: the stub control exits 1). It is a distinct gate row pair, as assigned.
3. `r41-refusal-sites` and `r41-drift-record-order` are single fixtures whose failing arm is the paired counter's stub control, not a base-blob arm; the fixtures alone are 0-able by an always-PASS stub, which is why each row names the counter as the self-test.
4. c3-counter and r41-refusal-sites refuse uid 0 (rc 2); not exercised here (ran as uid 1000) — the row states it from source ([INFERENCE] for behaviour, source lines read).
5. Docstring targets of the c3/c2/r1 counters are prefixes of the actual SUMMARY line (extra `site_regex=… docclasses_match=… tool_sha=… fixture_sha=…` fields); rows quote the real line.
6. Not run: the landing gate over the drafted SKILL.md (SKILL.md untouched); the L1's pre-landing gate run covers it.

## Verdict
Draft rows complete and each verdict map and self-test was exercised live (green and red arms, plus every exit-2 class reachable without uid 0); no tracked file touched, scratch removed.
