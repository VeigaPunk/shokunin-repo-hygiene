## Status

STATUS: PASS — `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/deliver-results-summary.py` (300 lines, executable, sha256 `7d6568ea335338155e094f1634ef61e246d8955ffa296e470ffb350d79ccb807`) prints seats/roles/status/not-completed/reports as tab-separated sections, exits 0 on readable input and 2 on unreadable input; verified on the r28 wave results (64 seats, role mix as predeclared) with independent one-liner cross-checks and edge-case tests.

## Evidence

Revision: lane base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`, preregistration commit and HEAD `b8cb4b31ce80e2e3314b88e85d40ea9873180804`; `git status --porcelain ... -- census/round-28/waves/ census/round-27/waves/ census/round-29/` → no lines, so the tested r28/r27 bytes are the committed ones. The deliverable lives under `.ufo/waves/`, which `.gitignore:1` ignores, so it is intentionally untracked.

Primary run (r28, unchanged between two runs — `cmp` identical):

```
$ python3 -B .ufo/waves/round-29/w1/deliver-results-summary.py \
    --results census/round-28/waves/w1-results.json \
    --spec census/round-28/waves/w1-spec.json --report-dir census/round-28/waves/w1 ; echo RC=$?
```

```
SECTION	seats
count	64
declared	64
SECTION	roles
executor	20
reviewer	12
scribe	8
critic	6
mutation-tester	6
scout	6
connector	2
sentinel	2
simplifier	2
SECTION	status
completed	41
partial	16
failed	3
waiting	1
unknown	3
SECTION	not-completed
name	role	status	detail
SwarmCritic42	critic	FAIL	{ "status": "FAIL", "report": "souji-shokunin/.ufo/waves/round-28/w1/SwarmCritic42.md", "verdicts": { "q1_entries_new_ground": "Durability new; exclusivity restates already-held O_EXCL/rename ground (
SwarmCritic43	critic	FAIL — C3 capture tool, fixture, durable receipts, manifest verification, and ex	{ "report": ".ufo/waves/round-28/w1/SwarmCritic43.md", "status": "FAIL — C3 capture tool, fixture, durable receipts, manifest verification, and exit/control evidence were absent; ignored tracked r26 m
SwarmExecutor12	executor	PARTIAL	{ "status": "PARTIAL", "files_changed": [ "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-28/records/searchlog-draft.md", "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-28/w
SwarmExecutor13	executor	PARTIAL	{ "status": "PARTIAL", "changed": [ "tools/souji-wave-evidence-capture.sh", "tests/fixtures/r28-wave-evidence-capture.sh", " .ufo/waves/round-28/w1/SwarmExecutor13.md" ], "behavior": "Capture copies w
SwarmMutationTester47	mutation-tester	PARTIAL	{ "report": "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-28/w1/SwarmMutationTester47.md", "status": "PARTIAL", "summary": "Pristine gate baseline had 10 unrelated LG-SEAT-UNCARRIED f
SwarmMutationTester48	mutation-tester	-	 thinking The README F4 row already includes the two new entries! Wait, the current lane working tree is modified `corpus/QUALITY.md`, but `corpus/README.md` is not listed as dirty (status earlier liste
SwarmMutationTester49	mutation-tester	PARTIAL	{ "status": "PARTIAL", "report": "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-28/w1/SwarmMutationTester49.md", "probes": { "manifest_byte_flip": "killed (sha256sum rc 1)", "captured_
SwarmReviewer29	reviewer	-	 thinking Aha! My earlier assumption wrong: the gate finding is `corpus/knowledge/registry` from Q59 and `corpus/lessons/round-24.md:232:S118` from Q57's check cell. There is no separate `.ufo/waves/...
SwarmReviewer31	reviewer	PARTIAL	{ "status": "PARTIAL", "report_path": "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-28/w1/SwarmReviewer31.md", "item": "Rev-C2Rows", "row_verdicts": { "S212": "PASS", "S213": "PASS", 
SwarmReviewer32	reviewer	PARTIAL	{ "report": ".ufo/waves/round-28/w1/SwarmReviewer32.md", "status": "PARTIAL", "findings": [ "Both requested lane entries were absent; only staged candidates reviewed.", "Both staged candidates lack re
SwarmReviewer33	reviewer	PARTIAL	{ "status": "PARTIAL", "report": "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-28/w1/SwarmReviewer33.md", "verdict": "AGREE with ADMIT", "findings": [ "The S119 snapshot SHA-256 is co
SwarmReviewer35	reviewer	PARTIAL	{ "status": "PARTIAL", "report": ".ufo/waves/round-28/w1/SwarmReviewer35.md", "evidence": { "collision_count": 27, "collisions": "S109–S132, S152, S210, S211", "base_and_current_registry_match": true,
SwarmReviewer37	reviewer	PARTIAL	{ "report": "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-28/w1/SwarmReviewer37.md", "status": "PARTIAL", "findings": [ "At review time the dirty-wave counter was 11; all 11 specified
SwarmReviewer38	reviewer	PARTIAL	{ "status": "PARTIAL", "report": "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-28/w1/SwarmReviewer38.md", "summary": "Both round-26 and round-27 receipt directories were absent at ver
SwarmReviewer39	reviewer	PARTIAL	s ≤25 space-delimited words with locations and verified verbatim (open.html direct; rename/fsync across inline tags; S119 at snapshot line 3117, sha256 a7f4742d… matches s119-disposition.tsv:2; S216/S
SwarmReviewer40	reviewer	-	{ "report": "## Status\nSTATUS: PASS — machine check `claims=3 flags=0` rc 0; R3 holds (calibration 7 lowest non-retired, claimed by C1); every CLAIM block carries `enumerate:`; no attack.\n\n## Evide
SwarmScout59	scout	PARTIAL	{ "status": "PARTIAL", "findings": [ { "id": "S236-S242", "source": "Opened staged append tail; file has 140 lines total. S236-S242 exist and are rows about fleet prune scheduling, prune implementatio
SwarmScribe21	scribe	-	{ "aborted": true, "error": "Assignment has conflicting evidence constraints: rows must be drafted from only posix-quotes.tsv and s119-disposition.tsv, but fields including scope, teaches, used-by, so
SwarmScribe22	scribe	PARTIAL	{ "status": "PARTIAL", "behavior": "Drafted round-28 candidate Gate table, including F4 admissions, S119 admission and two rejects.", "gates": "No campaign gates or fixtures run. S119 local snapshot p
SwarmScribe25	scribe	PARTIAL	{ "status": "PARTIAL", "behavior": "No quote-cards file written; requested source registry census/round-28/records/posix-quotes.tsv was absent at the inspected lane path. Verified S119 disposition and
SwarmScribe27	scribe	PARTIAL	{ "status": "PARTIAL", "behavior": "Wrote the exact six-step after-census command recipe, retaining all frozen predicates and expected values; labeled targets as expected rather than observed.", "gate
SwarmScribe28	scribe	[WAIT] Wave results file does not exist yet at `/home/vgpnk/Projects/shokunin/so	{ "status": "[WAIT] Wave results file does not exist yet at `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-28/w1-results.json`. Per instruction, stopped without compiling or inventing 
SwarmSentinel61	sentinel	PARTIAL	{ "seat": "SwarmSentinel61", "item": "seat-write-boundary audit", "status": "PARTIAL", "wait": true, "reason": "w1-results.json absent; only 2/64 seat reports landed", "report": "/home/vgpnk/Projects/
SECTION	reports
name	role	issue
SwarmMutationTester48	mutation-tester	missing-report
SwarmReviewer29	reviewer	missing-report
SwarmScout59	scout	missing-report
SwarmScribe21	scribe	missing-report
SwarmScribe25	scribe	missing-report
SwarmScribe28	scribe	wait+missing-report
RC=0
```

Independent totals (separate one-liners, no code reuse from the deliverable):

```
$ python3 -c "import json,collections;d=json.load(open('census/round-28/waves/w1-results.json'));print('seats',len(d['results']));print(sorted(collections.Counter(r['agent'] for r in d['results']).items(), key=lambda kv:(-kv[1],kv[0])))"
seats 64
[('executor', 20), ('reviewer', 12), ('scribe', 8), ('critic', 6), ('mutation-tester', 6), ('scout', 6), ('connector', 2), ('sentinel', 2), ('simplifier', 2)]
```

Matches the predeclared expectation exactly (64 seats; executor 20, reviewer 12, scribe 8, critic 6, mutation-tester 6, scout 6, connector 2, sentinel 2, simplifier 2) and the tool's `SECTION roles` block.

Independent report-file check (`comm` on basenames, not the tool's `isfile`):

```
$ ls census/round-28/waves/w1/ | grep '\.md$' | sed 's/\.md$//' | LC_ALL=C sort > md.txt   # 61 files
$ python3 -c "import json;print('\n'.join(sorted(r['name'] for r in json.load(open('census/round-28/waves/w1-results.json'))['results'])))" > seats.txt  # 64
$ comm -23 seats.txt md.txt   # seats without a report
SwarmMutationTester48
SwarmReviewer29
SwarmScout59
SwarmScribe21
SwarmScribe25
SwarmScribe28
$ comm -13 seats.txt md.txt   # non-seat md files
origin-record-durability-r28
origin-record-exclusivity-r28
round-28
```

Same six names as the tool's `SECTION reports`; bucket sum 41+16+3+1+3 = 64 and not-completed rows = 23 = 64−41.

Edge cases (scratch `/var/tmp/souji-r29-SwarmExecutor20/`, removed after the run):

| case | command shape | result |
| --- | --- | --- |
| zero seats | `{"seats":0,"results":[]}` | rc 0, `count 0`, empty sections, `report-dir-unset` |
| missing results file | `--results .../nope.json` | rc 2, `error: cannot read results ...` |
| malformed JSON | `--results .../bad.json` | rc 2, `error: cannot parse results ...` |
| no seat array | `{"lane":"souji"}` | rc 2, `error: no results / members array ...` |
| missing spec file | `--spec .../nope.json` | rc 2, `error: cannot read spec ...` |
| spec role mapping, no `agent` | row `id=C1Fixture` + spec `{item:C1Fixture, role:executor}` | `SeatX executor`, unknown id → `?` |
| row `status` field + tab in error | statuses completed/failed/dead/[WAIT] | `completed 1 failed 2 waiting 1`; error tab flattened |
| absent `--report-dir` | r28 run without the flag | `SECTION reports` = single `-  -  report-dir-unset` |

Robustness on a second committed wave (r27, 79 seats, item-named seats): rc 0, `count 79 declared 79`, roles executor 25/reviewer 12/scout 11/critic 10/scribe 8/mutation-tester 6/connector 3/simplifier 3/revenger 1; one missing report (`MutC2Rows`) against 94 md files.

Syntax check without bytecode: `python3 -B -c "import ast;ast.parse(open('.../deliver-results-summary.py').read())"` → `syntax ok`; no `__pycache__` created anywhere.

## Findings

1. **Results rows carry no status or error field.** All 64 rows in `census/round-28/waves/w1-results.json` have exactly `name`, `id`, `agent`, `output` (same in `census/round-26/waves/w1-results.json` 87 rows and `census/round-27/waves/w1-results.json` 79 rows), so the deliverable derives status from the row field when a dispatcher adds one, else from the output payload. Precedence is documented in the script docstring (`deliver-results-summary.py:20-30`).

2. **The canonical receipt derivation is blind to 19 of 64 r28 statuses.** `tools/souji-wave-evidence-capture.sh:105-148` takes `output` → `text` → one `json.loads`; the committed result is `census/round-28/waves/summary.tsv` column 4 with 27 PASS, 15 PARTIAL, 2 FAIL, 1 `[WAIT]`, 19 empty. The new instrument resolves 16 of those 19: nine PASS through the escaped-quote/prose fallback (`SwarmExecutor04`, `SwarmExecutor05`, `SwarmExecutor08`, `SwarmCritic44`, `SwarmScout55`, `SwarmScout57`, `SwarmScout60`, `SwarmSimplifier63`, `SwarmSimplifier64`), one PARTIAL (`SwarmReviewer39`, whose payload is a fragment carrying `"status": "PARTIAL"`), five seats that returned a parseable result object with no status field (`SwarmExecutor01`, `SwarmExecutor10`, `SwarmExecutor19`, `SwarmCritic45`, `SwarmMutationTester52`), and `SwarmScribe21` as failed on its own `{"aborted": true, ...}` payload; the remaining three stay unknown (finding 3). Observation only: the receipt generator is outside this seat's paths.

3. **Three r28 seats have no readable final result and are listed as unknown/not completed.** `SwarmMutationTester48`, `SwarmReviewer29` (thinking-only fragments) and `SwarmReviewer40` (paged markdown, truncated mid-sentence) in `census/round-28/waves/w1-results.json`; `SwarmMutationTester48` and `SwarmReviewer29` also lack `census/round-28/waves/w1/<name>.md`, while `SwarmReviewer40` did land a report.

4. **Six r28 seats lack a seat report at the committed path.** `SwarmMutationTester48`, `SwarmReviewer29`, `SwarmScout59`, `SwarmScribe21`, `SwarmScribe25`, `SwarmScribe28` have no `<name>.md` in `census/round-28/waves/w1/`; the directory also holds three non-seat files (`origin-record-durability-r28.md`, `origin-record-exclusivity-r28.md`, `round-28.md`), so the 61 md files are 58 seat reports.

5. **Status buckets reconcile exactly with the canonical receipt.** Canonical PASS 27 + empty 14 = completed 41; PARTIAL 15 + `SwarmReviewer39` = partial 16; FAIL 2 + `SwarmScribe21` = failed 3; `[WAIT]` 1 = waiting 1; the three unparseable seats = unknown 3. `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-28/waves/summary.tsv` ↔ tool `SECTION status`.

6. **`declared` equals the actual row count on every tested wave** (r28 64/64, r27 79/79), so no results-file truncation was masked by the summary.

7. **Lane-state observation, not written by this seat:** `git status --porcelain` shows ` M .ufo/waves/round-26/w1/ScribeGateDraft.md` (mtime 2026-10-25 20:45, before this seat's 21:38+ run; diff 2 insertions/1 deletion). Left untouched; the only tracked-change line in the lane at the time of this report.

## Deliveries

- `.ufo/waves/round-29/w1/deliver-results-summary.py` — the summarizer (executable, stdlib only, sha256 `7d6568ea335338155e094f1634ef61e246d8955ffa296e470ffb350d79ccb807`).
- `.ufo/waves/round-29/w1/SwarmExecutor20.md` — this report.
