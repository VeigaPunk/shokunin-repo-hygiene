# SwarmSimplifier35 — spec hygiene (w1, souji round 30)

## Status
STATUS: PARTIAL — the rendered plan is dispatchable and six of eight enumerated checks hold (distinct ids/prompts, allowed roles, flash and attack shares, unique deliver paths, scratch prefix, role mix), but two mandated rules fail at five sites: the absolute-path rule (shared context plus three items, one undefined placeholder) and the write-scope rule (two items name lane-relative write targets). Findings 1-5 are the violations; 6-10 are spec defects the L1 should reconcile; the non-violations list closes the remaining checks.

## Evidence

Lane HEAD `df6afe817d096e4ad71ba2b9cc21a83f126eb658`; one untracked L1-authored file (`corpus/lessons/round-30.md`, 01:29, header `author: souji L1 (SoujiR30)`) left untouched. Generator `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/make-spec-w1.py` (111 lines, 35 `add()` calls); rendered plan `w1-dispatch.json` (01:27, `w1.ready.dispatched` 01:48, `w1-run.err` 0 bytes); spec `w1-spec.json`.

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30 && python3 -B -c '<counts over w1-spec.json + w1-dispatch.json>'
items 35 ids 35 prompts 35
roles {'connector': 2, 'critic': 4, 'executor': 7, 'mutation-tester': 3, 'revenger': 1, 'reviewer': 4, 'scout': 4, 'scribe': 8, 'sentinel': 1, 'simplifier': 1}
flash_wide 22 / 35
flash_narrow_r7 16 / 35
attack 11 / 35
dispatch counts {'spawn': 35, 'resume': 0, 'total': 35} tasks 35 registry 35 band 32 64
labrat_trailers 7 executor_seats 7
deliver_files 23 dups []
scratch_refs 17
ctx_rel_C3 True
rel_write_C2 True
rel_write_C3 True
placeholder True
crossref_B True C True
B_has_root False
```

```
$ python3 -B -c '<per-prompt string checks over the same spec>'
C1RowsA --root True --rev True --scratch True --only True
C1RowsB --root False --rev False --scratch False --only True
C1RowsC --root False --rev False --scratch False --only True
DocsF1 'for PROVINCE.md' True
DocsF1 'SKILL.md' True
SourcesRows 'append them to a scratch copy of the registry' True
OpenJjUtilGc '/home/vgpnk/Projects/shokunin' False
EntryDraft record path: True
```

Generator re-execution (self-disclosure): an eval cell executed `make-spec-w1.py` to compare generator items with the rendered plan; its own `json.dump` re-serialised `w1-spec.json` at 01:49:11. Size before and after is 50760 bytes; the regenerated `context` equals the dispatch-embedded context (True) and all 35 prompts are exact prefixes of the 35 dispatched task texts (35/35), so the stored value is unchanged and the mtime is the only observable difference. No other lane write, no scratch tree created, no tool installed.

## Findings

1. **Absolute-path rule violated in the shared context (all 35 seats).** `make-spec-w1.py:23` names `tools/souji-landing-gate.py` — "`tools/souji-landing-gate.py` evaluates a round's COMMITTED reports" — and `:24` names the C3 write target — "one new entry corpus/knowledge/jj-keep-ref-expiry.md". Both are lane-relative. `/home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-30.md:333` requires "The wave `context` and every item must name absolute paths under /home/vgpnk/Projects/shokunin/souji-shokunin". Mitigation: every affected item repeats the target with an absolute `Deliver` path.
2. **C2Fixture asks for a lane-relative write target** (`make-spec-w1.py:61`): "Write the frozen C2 fixture tests/fixtures/r30-landing-gate-discovery.py". Seat tools start at the fleet root, so that resolves to `/home/vgpnk/Projects/shokunin/tests/fixtures/` — outside the lane and outside `w1/`, violating the seat's write scope. It should say: author it under `/fast/scratch/hyaku/souji-r30/C2Fixture/` and deliver it.
3. **C3JjFixture asks for the same** (`make-spec-w1.py:65`): "Write tests/fixtures/r30-jj-keep-expiry.sh". Same resolution hazard and same fix.
4. **Undefined relative placeholder in C2Fixture** (`make-spec-w1.py:61`): the red-before redirect is `> <scratch>/base-gate.py`; `<scratch>` is not defined anywhere in the prompt or context, so the target is neither absolute nor unique to the item. Name the item's absolute scratch path.
5. **Item-level relative lane names without an absolute twin.** DocsF1 (`make-spec-w1.py:78`) says "for PROVINCE.md" and a "SKILL.md rule bullet" (bare, while the same item uses the absolute `corpus/README.md` path); QualityCriteria also cites bare `SKILL.md`. SourcesRows (`:74`) says "append them to a scratch copy of the registry" without naming where that copy lives — a seat could append to the lane's `corpus/SOURCES.md`. OpenJjUtilGc names no lane path at all (URL-only item; the letter of round-prompt:333 is unmet, no write risk).
6. **C1RowsB and C1RowsC are not self-contained** (`make-spec-w1.py:63`, `:64`): both open "Same as the C1RowsA item, for rows R07-R12", but a seat cannot read another item's prompt. B gives no counter invocation at all — `--root`, `--rev` and `--scratch` are absent, only "with `--only <ids>` = all CORRECTED"; C is the same. A's own acceptance run is also incomplete: "run the counter with `--rev <that commit> --only <your ids>`" omits `--root <clone>`. A's `cmd=` decision rule is not restated in B. Consequence: three executors must guess the acceptance command.
7. **Frozen sizing mismatch.** `census/round-30/records/preregistration.txt:15` states "Sizing: one v2 wave (64-100 seats) under policy v2"; the rendered plan is a v1 wave (dispatch `policy.waveMinLanes=32`, `waveMaxLanes=64`; `scripts/hyaku/ufo-wave-policy.json:89-90`, `counts.spawn=35`). `souji-round-30.md:174-175` permits "one v2 wave of 64–100, or two v1 waves (32–64 each)", so the shape is legal, but the frozen prereg states the other shape. For a legal round total (64-100) wave 2 must be 32-64 (round total 67-99). The L1 must record the shape and reconcile the prereg line.
8. **Flash-share definition conflict.** 22/35 = 62.9 % under the frozen prereg (`flash roles (executor, scribe, labrat, sonic, simplifier, critic, revenger, sentinel)`) and under `souji-round-30.md:152` ("m_flash roles still carry ≥50 % of every wave"), but 16/35 = 45.7 % under the Run-7 parenthetical at `souji-round-30.md:182` ("≥50% of seats as executor/scribe/labrat/sonic/simplifier"). The plan passes the frozen contract; the report's role-mix line must state which definition it uses, or a closure reviewer can read 45.7 % as a miss.
9. **EntryDraft's source path is the post-integration path** (`make-spec-w1.py:73`): "The measured results will come from census/round-30/records/jj-keep-expiry-run.txt (another seat produces it)" — wave 1 produces `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w1/deliver-jj-keep-expiry-run.txt`; the named path exists only after L1 integration. The `<k>` placeholders make the item survivable, but the delivery path should be named.
10. **Generator guard gap** (`make-spec-w1.py:105`, `:108`): the asserts cover id/prompt uniqueness, the 32-64 band and the two role shares only; nothing checks absolute paths, write scope, scratch prefix or deliver-file uniqueness, which is why findings 1-5 passed generation.

Non-violations (checked, no defect):
- **Executor-only labrat bound.** Exactly the 7 executor trailers carry "Lane bounds: leaf member — no subagent dispatch except your single labrat."; the other 28 read "Lane bounds: leaf member — no subagent dispatch." This matches `souji-round-30.md:328` ("an executor seat may spawn one read-only `labrat` probe"). My own delivered seat text carried the leaf line.
- **Unique deliveries.** 23 deliver paths across 19 items, no duplicates; every `Deliver` target is under `w1/` (0 outside). `w1/sources/` is written by C3Snapshots and read by CredScan — a read/write pair, not a collision.
- **Shared integration targets are disjoint.** C1RowsA/B/C append R30-CORRECTION lines for R01-R06 / R07-R12 / R13-R18 to SCORECARD.md; R29Carry and R29GateCorrection append two disjoint blocks to `corpus/lessons/round-29.md`. No delivery-file collision; the L1 applies both append-only.
- **Scratch prefix.** 17 distinct `/fast/scratch/hyaku/souji-r30/<ItemId>/` references, each under its own item id; 18 items cite no scratch and need none (read-only or deliver-only). No `/tmp` reliance; C2Fixture and C3JjFixture set `TMPDIR` explicitly.
- **Role set and mix.** 10 distinct roles, all in the allowed list; 2 connector seats; attack 11/35 = 31.4 % (≥25 %).

## Deliveries

None — report-only item; this file is the artifact.
