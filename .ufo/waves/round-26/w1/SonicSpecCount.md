# SonicSpecCount — w1-spec seat census and role mix (r26)

## Status
STATUS: PASS — 87 seats parsed from the frozen spec with zero missing roles; m_flash-routable share 44/87 = 50.57% (bar ≥50% met by 1 seat), attack share 30/87 = 34.48% (bar ≥25% met by 9 seats).

## Evidence
Spec read this run: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1-spec.json` (lane HEAD `ea0bbe66c974`, file last touched at `bd6588c74ebfe86057b80035fdbc33aded8d7666`; sha256 `5be1679da0e3ae002c45405ed28805f5afc07e075a7ee83e6cb67252b0a2039c`; clean in `git status` for that path).

Command: `python3 -B` — `json.load(spec)` → `Counter(it["role"] for it in d["items"])`.

```
TOTAL_SEATS 87
executor        31   35.63%
reviewer        15   17.24%
scribe          11   12.64%
scout           10   11.49%
critic           9   10.34%
mutation-tester  6    6.90%
connector        2    2.30%
simplifier       2    2.30%
sentinel         1    1.15%
distinct_roles 9
missing_role_indices []
duplicate_names []
```

Thresholds (groups per assignment definitions):
```
ROUTABLE (executor/labrat/scribe/sonic/simplifier) 44  50.57%  >=50%: True
  executor=31 labrat=0 scribe=11 sonic=0 simplifier=2
ATTACK (reviewer/critic/mutation-tester/labrat)    30  34.48%  >=25%: True
  reviewer=15 critic=9 mutation-tester=6 labrat=0
ROLES_OUTSIDE_BOTH_SETS {scout: 10, sentinel: 1, connector: 2} = 13 (14.94%)
```

Spec metadata: `wave=souji-r26-w1`, `reportDir=.ufo/waves/round-26/w1`, `maxLanes=100`, top-level keys `{context, items, maxLanes, reportDir, wave}` (no `lanes`/`spawns` key; seat role is the only routing field carried per item).

## Findings
1. **Routable bar is met by exactly one seat.** 44/87 = 50.5747%; a single seat reclassified out of `executor`/`scribe`/`simplifier` (or any one seat dropped) drops the share to 43/87 = 49.43% and fails the ≥50% bar. Location: `.ufo/waves/round-26/w1-spec.json` items array, role field.
2. **Two routable members contribute zero seats.** `labrat=0` and `sonic=0`; the entire routable mass is `executor` (31) + `scribe` (11) + `simplifier` (2). The attack set therefore reduces in practice to `reviewer` (15) + `critic` (9) + `mutation-tester` (6) — `labrat` is a member of both sets but appears in neither. Location: same role field.
3. **Attack bar has real headroom.** 30/87 = 34.4828%; the bar (21.75 seats) is cleared by 8.25 seats, so it survives up to 8 seats being reclassified away from attack roles before failing.
4. **13 seats are in neither tracking set** (`scout=10`, `sentinel=1`, `connector=2`, 14.94%). `scout` alone is 11.49% of the wave — larger than any single attack-role except reviewer/critic — and is uncounted by both bars as defined in the assignment. Location: same role field.
5. **Coverage arithmetic is exact and total** — role counts sum to 87 = len(items); no item lacks `role`, no duplicate `name`; 9 distinct roles. Location: `.ufo/waves/round-26/w1-spec.json`.
6. **Spec revision drift, informational.** The wave context names lane commit `89e0fceeefcf28db313c94120be6d25e03c60094` as the freeze point, but lane HEAD at read time is `ea0bbe66c974` and the spec file's last commit is `bd6588c74ebfe8`. Counts above bind to the file bytes hashed in Evidence, not to `89e0fce`. Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1-spec.json`.

## Attack log
Not an attack item (calibration/census seat). No counter predicate, target or case set was modified; the two thresholds were evaluated exactly as stated (routable 44/87, attack 30/87).

Scratch: none created — all work was read-only `json.load` from the lane file, no `/var/tmp` world needed.
