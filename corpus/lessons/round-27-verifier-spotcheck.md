# Round 27 verifier spot-check (non-author integrator)

author: hyaku closure (non-author integrator, @m_kfc)
round: souji 27 (attempt 2); lane tip `c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0`; base `e78ac7c4837b81b634db4a927605a751a7f006ba`
date: 2026-10-25

## Conformance (step 1)

- Report committed in fleet repo by lane identity: `git log --format='%an %H' -- .ufo/reports/round-27/souji.md` → `souji-shokunin 6468c465095a171f1d40a3ca943a4d9e764e285b` (`round-27: souji report`); ancestor of fleet HEAD (rc 0).
- `SHONEN` heading: exactly one `## SHONEN`; one `[~]` line per box (4 boxes), each with a resolvable pointer. No `[x]` written by a non-author.
- Cited lane commits exist and are ancestors of branch `master`: `git merge-base --is-ancestor 6cb22dc20c9fdb3c7a49eaa1accabca339054c17 master` rc 0; same for `c973d1a…` rc 0.
- Lane pushed: `jj-lane.sh state` → `branch=master local=c973d1a… remote=c973d1a… ahead=0 behind=0 head=detached`. `git status --porcelain` shows only `.ufo/waves/round-{26,27}/` wave-runtime files (tracked-modified r26 slice + untracked r26/r27), `census/operator-sweep-20261019/`, `__pycache__/` dirs — uncommitted round work/leftovers remain (defect, named below; helper refuses `.ufo/` paths).
- Prompt `souji-round-27.md` carries the template contract (templates/round-prompt.md sections 1–5 rendered; five child-lane items present: report path/filename, commit-before-report, SHONEN heading, landed-hash citation rule, write scope) plus hyaku §6 addendum. Report is real (committed work, evidence pointers, measurements), not a marker → status `ok`.

## Per-claim re-check (step 2)

Commands run by the reviewer over committed bytes at `c973d1a…` (receipts) and at both revisions (counters). Gate claims are evidence-verified (receipts/registry); the lane's gates were not executed (§Gate standard).

| claim | re-derived result | reported | verdict |
|---|---|---|---|
| C1 calibration | receipts `c1-before.tsv` findings=2 rc=2 checked_reg=50; `c1-after.tsv` findings=2 rc=2 checked_reg=52 (gate sha256 `02b58f81…` identical both ends); preregistration frozen target findings=0; kill rule: any finding remaining → fail | before 2 → after 2, target 0 failed | matches; target failed, honest stop |
| C2 coverage | `git show e78ac7c:corpus/SOURCES.md \| grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` = 132; at tip = 135. `git grep -lE '^ground: F4'` = 2 → 4. `c2-after.tsv`: rows=135 grounded_f4=4 gate_entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0 census_rc=0. Fleet `sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` exit 0, 35 warning-only W04 (incl. S210 duplicate-URL across scopes) | 132→135; F4 2→4; gate 2/2, slice 8/8; census rc 0 | matches; claim verifies |
| C3 operability | `git cat-file -e e78ac7c:tools/souji-pre-report-gate.sh` rc 128 (absent at base); at tip exists (rc 0); fixture `tests/fixtures/r27-pre-report-gate.sh` committed. `c3-after.tsv`: base_absent=1 cases=4 pass=4 control=FALSE-GREEN-REJECTED rc=0. Registry rows exist in SKILL.md for `souji-landing-gate` and `souji-pre-report-gate` (selftest cmd, verdict map) | tool absent → present; fixture 4/4, control rejected | matches; claim verifies (evidence-verified, gate not executed) |

- No owned axis harmed: `git diff e78ac7c c973d1a -- SCORECARD.md` adds only the Round 27 measurements table and the r28 planned bullet; scores stay calibration 7, coverage 8, operability 8.
- No exploratory claim declared → no `unprovable-but-better` judgment needed.
- Wave shape corroborated: `w1-dispatch.json` 79 tasks with role mix executor 25 / reviewer 12 / scout 11 / critic 10 / scribe 8 / mutation-tester 6 / connector 3 / simplifier 3 / revenger 1; `w1-results.json` 79 results, all with final outputs, no dead seat named.

## Discernment spot-check (step 3)

Sample from `corpus/lessons/round-27.md` `## Gate`: one admit and one reject; sources re-opened.

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S152 (glocalfile.c) | ADMIT | URL re-fetched `https://raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c` → sha256 `66b588c495e1d7e036b02c5dc919ab466eace6f578ed38763a49b168d2d47e4f` matches committed snapshot `census/round-27/sources/glocalfile.c` and SHA256SUMS; quote `trashname = get_unique_filename (basename, i++);` located at line 2256 (5 words ≤ 25) | agree | quote present in pinned snapshot; access date and URL recorded; claim scoped to GLib 2.84.0 |
| S119 (zh-Hans git-fetch edition) | REJECT | staged row re-opened in read-only package `merge/souji/SOURCES.append.md` (line 17): row carries no decision-time sha256/snapshot pin; anchor is the live zh_HANS-CN edition opened 2026-10-23 | agree | without a pinned snapshot the decision-time version state is unrecoverable; flip condition (decision-time pin + located quote) is precise and currently unmet |

- New SOURCES rows S152/S210/S211: re-opened; row schema valid (11 cols, tier A, status mined, `used-by` exactly the two admitted F4 entries); quotes present in the entries' Gate blocks with opened date and snapshot paths.

## Trend verdicts

| trend | verdict | evidence |
|---|---|---|
| expansion | improved | 2 new admitted knowledge entries on F4 coverage-map ground (`ground: F4` 2→4), each citing a `mined` row S152/S210/S211; SOURCES rows 132→135; census rc 0 |
| quality | improved | entries re-grounded against sha256-verified GLib 2.84.0 snapshots (re-fetched digests match); source gate receipts 2/2, slice 8/8; C3 adds a runnable tested pre-report gate; no admitted entry failed re-check |
| discernment | unchanged | sampled gate decisions agree (1/1 admit, 1/1 reject); C1 calibration counter did not reach target; no disagreement left unlearned, but no new criterion added |

Axis verdicts: calibration `unchanged` (7; claim failed honestly, no harm), coverage `improved`, operability `improved`. Round admitted? No — C1 did not verify, so the all-claims admission rule is unmet; this is an honest stop (`rejected-honest-stop`).

## Routed defects for next round

1. S119 / Q57 stale composite-site citation: correct the Q57 composite site (S118 stale class) and re-adopt S119 only with a decision-time pinned snapshot + sha256 (r28 planned).
2. `.ufo/waves/` wave-runtime artifacts (r26 36 leftovers + r27 dispatch/results) are uncommittable through `jj-lane.sh`; need an operator-approved committable evidence path — currently uncommitted round work in the lane worktree (clean-worktree check of the new pre-report gate also fails on them).
3. Untracked `census/operator-sweep-20261019/` and `__pycache__/` leftovers in the lane worktree should be committed or gitignored.
4. Observation (not verifiable from committed bytes): run-7 m_flash-majority share is 36/79 seats (45.6%) if all mapped roles routed per map; per-seat models are not recorded in the committed wave artifacts — leave to the operator/routing record.
