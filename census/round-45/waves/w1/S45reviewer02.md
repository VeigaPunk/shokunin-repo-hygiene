# S45reviewer02 — R44 register identity #2 (index 1) audit

Seat: S45reviewer02 · Lane: /home/vgpnk/Projects/shokunin/souji-shokunin · Freeze: 019bccc9ac97f3cec1a1dea574cc2f81f57fc967

## Result

**MATCH at the string level.** The filed `R44-02` derived token equals the value independently derived from git blobs at `55d7af6f5a22340f7a3de1c386e514ababfaa75f`. Expected and filed are identical, 5 candidates, same order.

**Zero new factual credit.** `historical_credit=0`. This audit confirms a register line against a frozen instrument. It corrects no SCORECARD fact.

**Caveat, stated up front:** the agreement is with the frozen instrument's referent rule, which ignores the row's own context. The row's own evidence column cites one referent (`census/round-28/records/c1-after.tsv`), and the r42 accounting resolved the same item to that same path. The frozen expected value is therefore a `multi:` set, which is one instrument choice. It is not proof of which historical run the row used.

## Identity

- Population key: `(line=21, token=c1-after.tsv, class=mismatch:path-absent)`.
- Index: unique keys in first-occurrence order of `census/round-44/c1-population.tsv`. Index 0 is `(14, 65817d0d, mismatch:rev-unresolved)`, index 1 is this key. 70 rows, 66 unique, 4 duplicate keys (`667 c2-after2.txt`, `668 c3-after2.txt`, `792 c2-after-d.txt`, `793 c3-after-d.txt`).
- Corresponding register line: `corpus/lessons/round-44.md:26`, `CORRECTION-R44 id=R44-02 file=SCORECARD.md line=21 class=mismatch:path-absent stale=c1-after.tsv derived=multi:…census/round-28/records/c1-after.tsv rev=55d7af6f… scope=base-SCORECARD-token-referents`.

## Independent derivation (blob level, not the counter's output)

`git ls-tree -r -z --name-only 55d7af6f…` filtered to basename `c1-after.tsv` gives exactly five tracked paths:

| path | blob |
|---|---|
| census/round-24/records/c1-after.tsv | cd644211d4670782e0bd3fdd91c066ac9038dd89 |
| census/round-25/records/c1-after.tsv | b5b16184fc243a2c30cbc91b99b41f330a785baa |
| census/round-26/records/c1-after.tsv | 778ee0b0f246979102b4d592a86bd941a3193e0c |
| census/round-27/records/c1-after.tsv | 23b480bc2b3d103b8ce0459f4017d41177273a5f |
| census/round-28/records/c1-after.tsv | b9a17f83c45861cceb89fa2f8b1988a03ab409db |

- Derived string: `multi:census/round-24/…;census/round-25/…;census/round-26/…;census/round-27/…;census/round-28/…`
- Filed string (`corpus/lessons/round-44.md:26`): identical. `MATCH`.
- Base `SCORECARD.md:21` has no `c1-after.tsv` in its text, so the token is path-absent at base. The historical instrument (`tools/souji-declared-evidence.py` at base, sha256 `a332491607…`) also marks line 21 `mismatch:path-absent` for `c1-after.tsv`. Its `resolved` rows at line 21 point to the `c1-before.tsv` and the commit `de478b48…`.

## Comparison with the prior r42 accounting (Q76)

- `census/round-42/c1-register.tsv` row `21 c1-after.tsv resolved census/round-28/records/c1-after.tsv`. Under r42's rule R3-with-context (`round-28` context selects one of the five), the single referent is round-28.
- R44/R45 derive `multi` (5 candidates) because they ignore the context rule. The same tree yields `resolved→round-28` under r42 and `multi` under r44/r45.
- Q76 before-state check: `git show 55d7af6f…:SCORECARD.md`, `grep -nE 'SCORECARD\.md:21([^0-9]|$)'` hits only line 529, `| E04 | SCORECARD.md:21 | restated | 1 | …gate… findings=19 …`. That row restates the gate's outcome, not the `c1-after.tsv` path token. It does not bind this token item. I read it as not excluding the item under Q76. This is my judgement, not a settled rule, and I flag it as such.
- Net: the r42 and r44/r45 instruments give different expected values for the same identity. The 66/66 measurement is consistent with the frozen r44/r45 rule, and r42's single-referent answer would be scored `derived_mismatches=1` under the frozen counter.

## Attacks

1. **Referent vs runtime truth.** The derivation proves that the token resolves to five tracked blobs at base. It does not prove which run SCORECARD line 21 used, or what that run printed.
   - The round-28 blob is the only candidate whose content is that row's receipt: `revision=de478b483db66a8d8ff2d627cde1ccce6e21a014`, `command=… tools/souji-landing-gate.py --round 28 …`, `SUMMARY findings=0 checked_reg=52 …`. The row's measured commit is `de478b48`, matching. Round-24..27 are other tools or other revisions (e.g. round-26 is `census/round-26/c1-counter.sh`, round-27 is `findings=2 … rc=2`).
   - The row's own evidence column cites `census/round-28/records/c1-before.tsv`, `c1-after.tsv`, so the referent in the row's own text is round-28. The four other candidates are not the row's evidence.
   - Limit: the round-28 blob is a self-written receipt. I did not re-run the gate: it needs `--fleet-root /home/vgpnk/Projects/shokunin`, which is outside the lane. The row's `findings=0` is consistent with the receipt; it is not independently reproduced.
2. **Instrument artifact.** Expected `multi` for this identity is an artifact of the frozen rule, not a finding about history. A corrected single-referent answer would score as a derived mismatch. The preregistration freezes the counter, so I report this and do not amend it.
3. **Population count.** The counter's `unique=66` is correct for the file (verified above). Duplicates are four keys, each filed twice in the population. This audit did not check whether those duplicates carry the same fact.

## Discrimination probes (assigned, run in external scratch)

| probe | command | observed |
|---|---|---|
| frozen counter, freeze rev | `python3 -B census/round-45/c1-counter.py --root <lane> --rev 019bccc9… --scratch <ext>` | `SUMMARY population=70 unique=66 registered=66 missing=0 derived_mismatches=0 junk=0 fenced=0 duplicate=0 retracted=0 historical_credit=0`, EXIT=0 |
| wrong-derived for id 2 (only the `derived=` first token changed `census/round-24` → `census/round-24/WRONG-`) | same with `--register-file <ext>/register-wrong-id2.txt` | `registered=65 missing=0 derived_mismatches=1`, EXIT=1 — required pattern |
| id 2 dropped | same with `--register-file <ext>/register-missing-id2.txt` | `registered=65 missing=1 derived_mismatches=0`, EXIT=1 |
| assigned 12-case fixture | `python3 -B tests/fixtures/r45-register-feasibility.py --root <lane> --rev 019bccc9… --scratch <ext>` | `SUMMARY cases=12 pass=12 fail=0`, EXIT=0 |

Fixture outputs are retained at `receipt-fixture-12case.txt`. The two discrimination probe inputs are retained as `probe-wrong-id2.fixture.md` and `probe-missing-id2.fixture.md`. Both are fixture copies of `corpus/lessons/round-44.md` at the freeze rev, edited for one identity line only.

## Inputs checked

- `census/round-44/c1-population.tsv` sha256 `422875449468ae146ef029a4622d8f521f05f570a9b79f90286be03b7b0c1e2c`. Matches the preregistration.
- `census/round-45/c1-counter.py` sha256 `46d5fc68497d7d289b43f55f9c808d6da1d309900d357ebc608542436ee34125`. Matches the preregistration.
- Freeze commit `019bccc9…` exists; `census/round-45/preregistration.txt` is the frozen claim.

## Limitations

- Did not re-run the round-28 gate (outside lane fleet root).
- Q76 reading for `SCORECARD.md:529` is my judgement.
- Did not audit whether the other 65 identities are historical truth. Scope is identity #2 only.
- No new calibration gap, score change, or operability/coverage claim. Historical credit is zero.

## Tooling

No installs or updates. No commits, pushes, or git/jj mutation. Repo tracked status was unchanged by my runs (untracked count 4 before and after). Scratch `/fast/scratch/hyaku/souji-r45/S45reviewer02/` removed before yield; retained receipts are in the seat directory.

## Commands (exact)

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 55d7af6f5a22340f7a3de1c386e514ababfaa75f:tools/souji-declared-evidence.py > instrument.py
python3 -B instrument.py --root <lane> --rev 55d7af6f5a22340f7a3de1c386e514ababfaa75f --file SCORECARD.md --format tsv
git -C <lane> ls-tree -r -z --name-only 55d7af6f5a22340f7a3de1c386e514ababfaa75f   # basename c1-after.tsv filter, Python
git -C <lane> show 55d7af6f5a22340f7a3de1c386e514ababfaa75f:SCORECARD.md | grep -nE 'SCORECARD\.md:21([^0-9]|$)'
python3 -B census/round-45/c1-counter.py --root <lane> --rev 019bccc9ac97f3cec1a1dea574cc2f81f57fc967 --scratch <ext>
python3 -B census/round-45/c1-counter.py … --register-file <ext>/register-wrong-id2.txt
python3 -B census/round-45/c1-counter.py … --register-file <ext>/register-missing-id2.txt
python3 -B tests/fixtures/r45-register-feasibility.py --root <lane> --rev 019bccc9… --scratch <ext>
```

## Verdict

Identity #2: expected = filed = blob-derived (`MATCH`), 0 new historical credit. The r42 single-referent accounting disagrees with the frozen multi-referent rule; that is an instrument choice the lane should record, not a historical fact.
