# SwarmSimplifier67 — spec hygiene (w1, souji round 29)

## Status
STATUS: PASS — all seven enumerated checks hold over the rendered plan: 68 distinct items/prompts, 10 allowed roles only, role mix exactly the frozen mix (`executor` 21, `scribe` 10, `scout` 7, `reviewer` 8, `critic` 8, `mutation-tester` 6, `sentinel` 2, `connector` 3, `revenger` 1, `simplifier` 2 = 68), no item asks for a model or routing, every prompt names a surface and a deliverable or finding, 45 unique deliverable paths all under `w1/`, and no item mandates a write outside its scope. Notes in Findings 8-11 are non-violations (duplicate authority, guard gap, tracking status, wording hazard), reported for the L1 only.

## Evidence
Lane HEAD at check time: `b8cb4b31ce80e2e3314b88e85d40ea9873180804` (`git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD`). Generator: `.ufo/waves/round-29/make-spec.py` (121 lines). Rendered plan: `.ufo/waves/round-29/w1-dispatch.json`; generator output `.ufo/waves/round-29/w1-spec.json`.

Counts (spec, the generator's own output):
```
$ python3 -B -c "import json,collections; d=json.load(open('.../round-29/w1-spec.json'))['items']; print(len(d),len({i['item'] for i in d}),len({i['prompt'] for i in d}),dict(sorted(collections.Counter(i['role'] for i in d).items())))"
items=68 ids=68 prompts=68 roles={'connector': 3, 'critic': 8, 'executor': 21, 'mutation-tester': 6, 'revenger': 1, 'reviewer': 8, 'scout': 7, 'scribe': 10, 'sentinel': 2, 'simplifier': 2} total=68
```
Counts (rendered plan, independent of the spec file):
```
$ python3 -B -c "... loads w1-dispatch.json ..."
tasks=68 names=68 texts=68 counts={'spawn': 68, 'resume': 0, 'total': 68}
roles={'connector': 3, 'critic': 8, 'executor': 21, 'mutation-tester': 6, 'revenger': 1, 'reviewer': 8, 'scout': 7, 'scribe': 10, 'sentinel': 2, 'simplifier': 2}
registry_roles={'connector': 3, 'critic': 8, 'executor': 21, 'mutation-tester': 6, 'revenger': 1, 'reviewer': 8, 'scout': 7, 'scribe': 10, 'sentinel': 2, 'simplifier': 2}
name_role_item_triples_match=True
```
Generator internals agree with the rendered files:
```
$ grep -c '^add(' .../make-spec.py
68
$ sed -n '116,121p' .../make-spec.py
assert len(ITEMS)==68, len(ITEMS)
assert len({i['item'] for i in ITEMS})==68
assert len({i['prompt'] for i in ITEMS})==68
```
`add()` order and (role, item) pairs parsed from source equal the spec items in order (`order/role matches spec: True`), and every rendered task is exactly `/skill:godspeed` + the item prompt + a per-seat trailer (`items where task != prefix+prompt+suffix: 0`).
```
$ python3 -B -c "... 45 deliver paths from spec prompts ..."
deliver_paths=45 outside_W=0 paths_cited_by_2plus={'W/deliver-souji-wave-evidence-capture.sh': ['C2FixtureV2', 'C2ToolV2']}
reports=68 distinct=68 all_under_W=True
```
Context identity: `spec.context==dispatch.context: True len= 5538`; `compaction: False`; `resumeSends: 0`.

## Findings
1. **Distinct item ids and prompts — clean.** 68 items in the generator (`.ufo/waves/round-29/make-spec.py:38-113`, `grep -c '^add('` = 68), 68 distinct ids, 68 distinct prompt strings, and 68 distinct rendered task texts in `w1-dispatch.json` (`len(set())` over `item`, `prompt`, `task`). Generator asserts the same three properties at `make-spec.py:116-118` (`assert len({i['prompt'] for i in ITEMS})==68`).
2. **Roles — clean.** Every `role` field in the spec, every `agent` in `taskCall.tasks`, and every `registry.members[*].role` is one of scout, reviewer, critic, connector, sentinel, executor, mutation-tester, revenger, simplifier, scribe; zero offenders in all three views. `name_role_item_triples_match=True` (no seat assigned a role different from its item's role).
3. **Role counts — clean and exactly the frozen mix.** Spec = dispatch = on-disk registry: executor 21, scribe 10, scout 7, reviewer 8, critic 8, mutation-tester 6, sentinel 2, connector 3, revenger 1, simplifier 2; total 68. Matches `census/round-29/records/preregistration.txt:15` verbatim: "one v2 wave, 68 seats, role mix executor 21, scribe 10, simplifier 2, revenger 1, sentinel 2, critic 8". Attack share 8+8+6 = 22/68 = 32.4% (same line: "attack seats reviewer+critic+mutation-tester 22 of 68").
4. **No model or routing ask — clean.** Zero occurrences of any model identifier (`opus|sonnet|haiku|gpt|claude|deepseek|gemini|llama|mistral|qwen`) in any prompt. The five broad keyword hits are all non-routing and adjudicated: `provider` 1 — a mistake-class word (`MistakesRows`: "attribution, landing, provider"); `route` 1 — a verdict class (`CredScanR26`: "route-to-kagi"); `flash` 1 — an audit target (`AttackWavePlan`: "flash-role share vs 50%", asking a critic to check sizing, not to assign a model); `model` 2 — the verb "model the r28 failure" (`MutateCaptureFixtureBase`) and this item's own rule text (`SpecHygiene`: "no item asks for a model or routing"); `routing` 1 — same `SpecHygiene` rule text. No prompt names a model, temperature, provider choice or route.
5. **Surface + deliverable/finding — clean.** All 68 prompts name at least one surface (lane path, own `/var/tmp/souji-r29-<ItemId>/` scratch root, or an https URL); no item names a foreign scratch root (`S()` args = item ids; 23 prompts name `/var/tmp`). 41 prompts name one or more `w1/deliver-*` files; the other 27 name a finding sink instead, e.g. OpenStatx "Deliver in your report: the page's version/date line", AttackC2 "Deliver numbered attacks with evidence", MutateC1Forward "report a kill table", VerifyBroder "Verdict: row admissible yes/no", MutateGuardAndRows "Report which fixtures the guard catches/misses". Every one of the 68 rendered task trailers carries a unique `Report: write your scoped findings to .ufo/waves/round-29/w1/Swarm<Role><NN>.md` under `w1/` (68 distinct paths).
6. **Deliverable paths — clean.** 45 distinct `w1/deliver-*` paths; `outside_W=0`. Each path is written by exactly one item. The single path cited by two items is `w1/deliver-souji-wave-evidence-capture.sh`: C2ToolV2 delivers it; C2FixtureV2 only reads it conditionally ("If /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/deliver-souji-wave-evidence-capture.sh exists when you finish, also run against it and report") — no second write.
7. **No write mandate outside scope — clean.** The only non-`deliver-*` `w1/` write sinks are disjoint: `w1/assimilation/{reg-ids,staged-ids,collisions}` (C3CollisionGuard), `w1/assimilation/quarantine-slice` (C3SliceGate), `w1/sources/` + `w1/sources/SHA256SUMS` (C3SnapshotPin; C3RehearseAdmit only reads `w1/sources/`). Three prompts name a final lane path as a landing note, never as a seat write: C1Fixture "(final path will be tests/fixtures/r29-registry-agreement.py)", C2ToolV2 "(final path tools/souji-wave-evidence-capture.sh)", C2FixtureV2 "(final path tests/fixtures/r28-wave-evidence-capture.sh…)" — all three still deliver into `w1/`. C3CollisionGuard's addendum command (`A=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/assimilation`) is explicitly redirected: "Write these three files at /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/assimilation/ instead". Lane mutations appear only as prohibitions ("do NOT edit the tool", "never write into the lane", "Never edit the lane file", "never touch the register") or as scratch-only commits ("commit in the scratch only", "commit there with a scratch-local identity"). At check time `w1/` held no entry outside the spec'd deliverable/report/`assimilation`/`sources`/registry names (`unexpected top-level entries: []`).
8. **Duplicate authority (note, not a violation of any enumerated check).** Two seats author the same lane target, as two different deliverable files, and the plan does not state precedence: `corpus/knowledge/duplicate-verdict-identity.md` from EntryIdentity (`w1/deliver-entry-identity.md`) and from C3RehearseAdmit (`w1/deliver-duplicate-verdict-identity.md`); `corpus/knowledge/duplicate-verdict-byte-equality.md` from EntryByteEquality and C3RehearseAdmit. Likewise the four registry rows exist in three deliverables — SourcesRows (`w1/deliver-sources-rows.md`), C3MirrorValidate (`w1/deliver-sources-append-block.md`), C3CollisionGuard (renumber map) — and the `corpus/README.md:41` F3 row in two (ReadmeProvinceF3 `w1/deliver-docs-f3.md`, C3RehearseAdmit `w1/deliver-readme-f3-row.md`). Recommendation (L1, no spec edit needed): treat the C3RehearseAdmit variants as canonical because they are the only ones validated by `souji-gate-check.py`/`coverage-agreement`/`sources-census` in the scratch clone, and use the scribe drafts as prose inputs only.
9. **Generator guard gap (note).** `make-spec.py:116-118` asserts only count 68 and distinct ids/prompts; the frozen per-role mix is printed (`make-spec.py:121`, `print(dict(c))`) but never asserted, so role drift would not fail generation. Counts are correct this round (Finding 3); a stricter-only `assert dict(c)=={...}` would make the frozen mix machine-enforced. No amendment proposed (counters/targets untouched).
10. **Plan is not revision-bound (note).** The generator, spec and dispatch are ignored by the lane: `git check-ignore -v` prints `.gitignore:1:.ufo/waves/` for all three, and lane `git status --porcelain` shows only `.ufo/waves/round-26/w1/ScribeGateDraft.md` modified. Only the preregistration is committed (`b8cb4b3`), so this hygiene verdict binds to lane HEAD plus the bytes read this run; the dispatch markers `w1.ready` / `w1.ready.dispatched` (151 B JSON / `2026-10-25T21:58:29`) are the only dispatch record.
11. **Wording hazard (note).** C2FixtureV2's final-path note says "final path tests/fixtures/r28-wave-evidence-capture.sh, replacing the six-case file" — a seat could read "replacing" as licence to edit the lane fixture. The delivery instruction in the same prompt targets `w1/deliver-r29-wave-evidence-capture-fixture.sh`, so the mandate stays in scope; the L1 should treat the replacement as its own landing step.
12. **Registry agreement.** The on-disk `w1/swarm-registry.json` (68 members) matches `w1-dispatch.json` field-for-field on every member (`field diffs: 0`); it adds only top-level `createdAt`/`updatedAt`/`wave`. `reportDir` = `.ufo/waves/round-29/w1` in spec, dispatch and registry. `counts` = spawn 68 / resume 0 / total 68, `compaction.applied` false, so no item was trimmed from the rendered plan.

No tool installs; no lane writes; no credentials encountered.

## Deliveries
- `.ufo/waves/round-29/w1/SwarmSimplifier67.md` (this report). No other files.
