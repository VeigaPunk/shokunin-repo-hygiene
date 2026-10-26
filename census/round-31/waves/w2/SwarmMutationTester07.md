# SwarmMutationTester07 — w2 mutation probe: C1 counter A2/A4 rules + supersession-row parser regex

## Status
STATUS: PASS — all eight assigned mutants run to a verdict (five rule deletions, three parser-regex mutations); 4 killed by committed controls, 4 survivors, each survivor demonstrated on a scratch state (or, for the regex run-row mutant, on the landed bytes themselves); lane untouched; scratch removed.

## Evidence
Scratch: `/fast/scratch/hyaku/souji-r31/w2-MutateC1A4/` (clone of the lane, origin removed; `rev-parse --show-toplevel` verified; removed at the end). Counter under test = the landed blob, byte-identical four ways:

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file blob 24f343c8ffc820c0f89b4252cbdc94ab9a673aab:tools/souji-capability-cells.py | sha256sum
  -> edf0933d02b8da7c3f04afbef19c32e921e46e89df2b3ff5d29dc25e1d607da3   (== tip blob == working tree == amendments.txt A4 digest)
v1 blob at prereg 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525 -> eced32ea9f36b529e5442709570d28841b9b4bd032f1fd10961a624ce2d9b520
```

Baseline (full 41 items, current counter, `--root <scratch clone> --rev 1d45496... --base 9f17a1ef... --list-rev 1d45496...`):

```
SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34 rev=1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525
```
— byte-identical to the committed `census/round-31/records/controls.tsv` row `C1-do-nothing(base) c1`. Full ITEM dump delivered (`MutateC1A4/do-nothing-items.txt`); base-cell MATCH items: L01 L02 L30 L31 L36 L38 L40.

The committed control scratch revs (fc9a28cf, bfb5eb92, 124d0fd8, 99fa4a80, f86cd002) are absent from the lane repo, so each cheat state was rebuilt in scratch from the committed builders (`census/round-31/controls-amended.sh`, `census/round-31/controls-a4.sh`) and validated by reproducing BOTH committed columns:

| state (rev in scratch clone) | item | v1 column (committed = reproduced) | A2+A4 column (committed = reproduced) |
|---|---|---|---|
| JunkA2 61e9a4d54470af00ae67b607b46a76add5cd5de7 | L07 | bound_record=1 mismatches=0 = MATCH | mismatches=1 = BAD-ROW(shape) |
| A4a ca3745025ab585b797d892a28e0328cc71d00905 | L04 | bound_record=1 mismatches=0 = MATCH | mismatches=1 = BAD-ROW(cmd-item-record) |
| A4b 1379e183f97a6468e5feac813e07f0bc14f9e836 | L30 | bound_record=0 mismatches=1 = RECORD-MISMATCH | mismatches=1 = BAD-ROW(cmd-item-record) |
| A4c 0c622357b9ec23d3b7b93b5715211e7def2b2bdf | L06 | bound_run=1 mismatches=0 = MATCH | mismatches=1 = RUN-MISMATCH (rc=2 unrecognized --ci-satisfy) |
| A4d 3eae9883073fd795a02ca84b7de5453badff3504 | L28,L29 | bound_record=2 mismatches=0 = 2x MATCH | mismatches=2 = 2x BAD-ROW(shared-occurrence) |

All ten validation runs matched the committed TSVs exactly. Two facts fall out of the validation itself: on the A4b state the current counter's refusal verdict is `BAD-ROW(cmd-item-record)` (rule (a) — L30's cell names `python3 tools/souji-declared-evidence.py --selftest`), and v1's refusal there was `RECORD-MISMATCH` (`census/round-22/attempt2/sources/freedesktop-trash.raw` contains no `8/8` at digit boundaries — grep over the base blob returns nothing).

## Findings
1. **A2 (count shape) has no independent control coverage** — harms calibration (C1). Deleting the branch at tools/souji-capability-cells.py:245-246 (`verdict = "BAD-ROW(shape)"  # A2`) flips no committed control: on the only A2-labeled state (C1-junk-A2) the cheat stays refused by rule (a) (L07's cell names a command) and would be by rule (b) (.py record), so the committed c1-a2 column (mismatches=1) is reproduced unchanged. Scratch demo state stM1demo (7c1122556170e739a1e28315ee298e2abdf5294f): record rows `| L10 | SCORECARD.md:159 | 4-4 | record: census/round-21/read-root-oracle-w1-partial.tsv |` and `| L27 | SCORECARD.md:170 | 3-3 | ... |` — the exact shapes amendment A4 lists ("A2's count-shape rule already refuses", amendments.txt) — through a legit-kind unchanged base record; current counter 2x BAD-ROW(shape) mismatches=2, mutant 2x MATCH mismatches=0. Docstring rule at tools/souji-capability-cells.py:41: "anything else is BAD-ROW(shape)".
2. **A4(b) (record kind) has zero independent control coverage; the committed "A4b" control actually pins A4(a)** — harms calibration (C1). Deleting the branch at tools/souji-capability-cells.py:274-275 (`verdict = "BAD-ROW(record-kind)"  # A4(b)`) leaves every committed control expectation intact: on the A4b state the refusal is rule (a)'s, byte-identical verdict. Demo state stM3demo (b38c18df4fdd7aa51229e989e7924bb8fbb684e5): record rows binding L24 (`pass=118\tfail=0`) and L25 (`total=17 failed=0`) — both COUNT_FORM-shaped — to `census/round-20/run-acceptance.py` (a .py record; both items have no base command); current counter 2x BAD-ROW(record-kind) mismatches=2, mutant 2x MATCH mismatches=0. Docstring rule at :48-49: "code, controls and web captures are not measurement records". The committed row `A4b(web capture as record)` in census/round-31/records/controls-a4.tsv never exercised rule (b).
3. **The parser regex is unpinned in both directions** — harms calibration (C1). r1 (dot unescaped, `SCORECARD\.md:` -> `SCORECARD.md:` at tools/souji-capability-cells.py:71): verdict-identical on all five control states; demo stR1demo (8d9eb0e929b120ce98508279e8be9d273c4c8b91): a row with line spec `SCORECARDXmd:170` binds L29 — current counter UNBOUND mismatches=1, mutant MATCH mismatches=0 (bound_record=1). r3 (`(run|record)` -> `(record)`): every control state's SUMMARY unchanged (the A4c state's fallback keeps mismatches=1 via RUN-MISMATCH); on the landed C1 state 24f343c8 `--only L06` the mutant turns the landed run-row binding invisible: MATCH -> RUN-MISMATCH, mismatches 0 -> 1. Parsing is anchored by `m = ROW.match(ln)` (tools/souji-capability-cells.py:181).
4. **The counter would accept an L29 binding the landed claim calls unhonest** — harms calibration (C1); the A4-disclosed file-granularity limitation made concrete on the exact item the landed claim misses. Scratch state stL29row (0652091c3d73e0df47534c2c733e9ec537cbc486): a standard-spelling row `| L29 | SCORECARD.md:170 | 18/18 | record: census/round-21/final-code-verification.json |` makes the CURRENT counter report MATCH, mismatches=0 — the record's `18/18` occurrence is L28's `matched=18/18`, which the file-granular record rule cannot attribute. The landed tail states L29 "has no row: its record states the count only as separate scalar fields" (SCORECARD.md tail at 24f343c8); the unbound=1 in the landed SUMMARY is therefore honesty-enforced, not counter-enforced — the frozen mismatches=0 target is reachable with a file-granular row.
5. Harness note (no axis; not a defect claim): the counter's private clone (`git clone -q --no-local --no-checkout`, tools/souji-capability-cells.py:196) transfers only advertised refs, so a run-row item at an unreachable detached scratch rev fails COULD-NOT-EVALUATE ("unable to read tree"); the committed controls each ran while HEAD sat on the cheat commit. Wave-2 seats rebuilding states must branch them (as done here) before any run-row evaluation.

## Attack log
All runs `python3 -B <mutant> --root <scratch clone> --rev <state> --base 9f17a1ef... --list-rev 1d45496... --scratch <scratch>/s1 --only <items>`; committed controls re-run with `--only` as required. Serial execution throughout.

| mutant | mutation | JunkA2 L07 | A4a L04 | A4b L30 | A4c L06 | A4d L28,L29 | verdict |
|---|---|---|---|---|---|---|---|
| committed (cur.py) | — | 1 shape | 1 cmd-item-record | 1 cmd-item-record | 1 RUN-MISMATCH | 2 shared-occurrence | — |
| m1_a2_del | A2 branch deleted | 1 (cmd-item-record) | 1 | 1 | 1 | 2 | SURVIVOR; demo stM1demo 2->0 |
| m2_a4a_del | A4(a) branch deleted | 1 (shape) | **0 MATCH** | 1 (record-kind) | 1 | 2 | KILLED by controls-a4.tsv row A4a |
| m3_a4b_del | A4(b) branch deleted | 1 (shape) | 1 | 1 (cmd-item-record, identical) | 1 | 2 | SURVIVOR; demo stM3demo 2->0 |
| m4_a4c_del | base-blob overwrite deleted | — | — | — | **0 MATCH (edited fixture runs, rc=0 observed=18/18)** | — | KILLED by controls-a4.tsv row A4c |
| m5_a4d_del | shared-occurrence deleted | — | — | — | — | **0 (2x MATCH)** | KILLED by controls-a4.tsv row A4d |
| r1_dot | `SCORECARD\.md:` -> `SCORECARD.md:` | 1 | 1 | 1 | 1 | 2 | SURVIVOR; demo stR1demo UNBOUND->MATCH |
| r2_run_only | `(run|record)` -> `(run)` | 1 (fallback RUN-MISMATCH) | 1 (fallback RUN-MISMATCH) | **0 (fallback MATCH, observed=selftest=8/8)** | 1 | 2 (2x UNBOUND) | KILLED by controls-a4.tsv row A4b, via the base-cell fallback |
| r3_record_only | `(run|record)` -> `(record)` | 1 (shape) | 1 | 1 | 1 (fallback RUN-MISMATCH) | 2 | SURVIVOR; landed-state demo L06 MATCH->RUN-MISMATCH |

Survivors: m1_a2_del, m3_a4b_del, r1_dot, r3_record_only. Killed: m2_a4a_del, m4_a4c_del, m5_a4d_del, r2_run_only.

## Deliveries
- Report: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-31/w2/SwarmMutationTester07.md (this file)
- Mutant diffs (unified, vs the landed blob edf0933d): .ufo/waves/round-31/w2/MutateC1A4/{m1_a2_del,m2_a4a_del,m3_a4b_del,m4_a4c_del,m5_a4d_del,r1_dot,r2_run_only,r3_record_only}.diff
- Baseline ITEM dump: .ufo/waves/round-31/w2/MutateC1A4/do-nothing-items.txt
- Scratch dir /fast/scratch/hyaku/souji-r31/w2-MutateC1A4/ removed after the deliveries were copied. No lane writes outside .ufo/waves/round-31/w2/; no git/jj mutation in the lane; no signals.
