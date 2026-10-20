STATUS: DONE — one false round-17 live-fleet repository count: SCORECARD.md:15 says 22; measured 21.

# R3 — round-17 live-fleet repository counts at b576341

Base: `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3` (== HEAD at measurement; worktree `census/round-17/live-fleet.json` is byte-identical to the base blob, sha256 `33d429d2db358dc6f7d71af0a042b90353d87a69dbf24217deb834ef96e2bf7f`).

## Measured ground truth

`census/round-17/live-fleet.json` `arms.<arm>.rows` includes a **header row** at index 0
(`["repo","worktrees","unpushed","dirty","scratch_bytes","mtime_iso","verdict_flags"]`).

```
$ python3 -c 'import json;d=json.load(open("census/round-17/live-fleet.json"));print("repos:",len(d["arms"]["changed"]["rows"])-1,"raw:",len(d["arms"]["changed"]["rows"]))'
repos: 21 raw: 22
$ jq '.arms.changed.rows[1:] | length' census/round-17/live-fleet.json
21
$ jq '.arms.r16.rows[1:] | length' census/round-17/live-fleet.json
21
```

Both arms: 21 body rows, 21 unique repos, all basenames end `-shokunin`; `r16` and `changed`
bodies are byte-equal; no row equals `root`. Fleet-wide repository count therefore **21**
(includes `souji-shokunin` itself).

Independent corroboration without the header question: the round-16 record
`census/round-16/live-fleet-final.json` is **headerless** (21 raw rows, 21 unique repos) and
covers the *same repo set* (`set(r16)==set(r17 body)` → `True`; symmetric difference empty).
The step 21 → 22 is a schema change (header added in round 17), not a fleet change.

## Claim inventory (round-17 live-fleet repository count)

| file:line | stated | measured | verdict |
|---|---|---|---|
| `SCORECARD.md:15` | "live fleet paired rows identical (**22 repos**)" | 21 repos (22 raw rows incl. header) | **FAILS — false by one** |
| `corpus/lessons/round-17.md:6` | "Live fleet paired run (`census/round-17/live-fleet.json`): **22 rows**, r16 and changed identical excluding mtime, rc 0, no stderr." | 22 raw rows / **21 repos** | **PARTIAL** — "22 rows" is literally true of the array, but it is the off-by-one source; it does not state a repo count |
| `/home/vgpnk/Projects/shokunin/.ufo/reports/round-17/souji.md:81` | "Live fleet pair (`census/round-17/live-fleet.json`): **22 rows** identical excluding mtime, rc 0." | 22 raw rows / **21 repos** | **PARTIAL** — same wording hazard; same file, `sha256 dc8136a01be64e6d645f70068fa0a647f9adedc08f19e7661c2b25a97a650851` |
| `LOG.md` round-17 section (`:944`–`:946`, end of file) | **no count** (only the claims header line; `grep -E '[0-9]+ (repo|repos|repositories)'` on `NR>=944` → rc 1) | 21 | **N/A — no claim** |
| `SKILL.md` | **no live-fleet count**; only `:157` "no real store or live fleet probe" (capability text); `grep -iE 'live.?fleet'` → single hit | 21 | **N/A — no claim** |

### Adjacent correct claim (not a round-17 claim, recorded to bound the blast radius)

`LOG.md:861-862` (round-16 section, `:836`–`:885`): "Live fleet paired runs
(`live-fleet-final.json`): r14-harm and changed rows identical on **21 repositories**." →
measured `census/round-16/live-fleet-final.json` = 21 headerless rows. **Correct.** Its arms
(`r14-harm`, `changed`) and filename are the round-16 pair, so it is not a round-17 statement
and must not be "corrected".

## Root cause

Round 16 wrote a headerless row array (21 rows = 21 repos). Round 17 added a header row and the
prose carried `len(rows)` forward as "22 rows", which `SCORECARD.md:15` then relabeled
"(22 repos)". No claim was re-derived from the body.

## Smallest fix

1. `SCORECARD.md:15`: `(22 repos)` → `(21 repos)`. One token; the surrounding claims
   ("paired rows identical", fixture numbers) are unaffected and verified.
2. Optional hardening (prevents recurrence, no count change): in `corpus/lessons/round-17.md:6`
   and the fleet report line 81, write `21 repositories (22 rows incl. header)` instead of
   `22 rows`. Lessons/prose are preserved as calibration evidence; the SCORECARD number is the
   only factual defect.

## Remaining unknowns

- Whether any *unlisted* authority file states the count: slices outside my assignment
  (`PROVINCE.md`, `corpus/QUALITY.md`, `corpus/README.md`) were grepped for
  `[0-9]+ (repo|repos|repositories)` and contain only the unrelated "F2 repository size census"
  capability rows — no live-fleet count.
- The authoritative in-census repo count (what `souji-census.sh` itself would emit) was not
  re-run: executing the census against the live fleet is forbidden for this seat. 21 is
  established from the committed record plus the headerless round-16 corroboration.

## Commands run (all read-only)

```
git show b5763415cc67ecff1e8fe56c58c39a6fb106d7a3:census/round-17/live-fleet.json > /tmp/lf.json
python3 -c 'import json;d=json.load(open("/tmp/lf.json"));print(len(d["arms"]["changed"]["rows"])-1)'      # 21
jq '.arms.changed.rows[1:] | length' census/round-17/live-fleet.json                                       # 21
jq '.arms.r16.rows[1:] | length' census/round-17/live-fleet.json                                           # 21
sha256sum census/round-17/live-fleet.json
git show b5763415cc67ecff1e8fe56c58c39a6fb106d7a3:census/round-17/live-fleet.json | sha256sum               # equal
git ls-tree -r --name-only b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 census/ | grep -i 'live-fleet'
  -> census/round-16/live-fleet-final.json
     census/round-16/live-fleet.json
     census/round-17/live-fleet.json
git show <base>:LOG.md | awk 'NR>=944' | grep -nE '[0-9]+ (repo|repos|repositories)'                        # rc 1, no match
grep -n -iE 'live.?fleet|22 rows|21 repos|22 repos' /home/vgpnk/Projects/shokunin/.ufo/reports/round-17/souji.md
  -> 62, 81
```

Verdict: **fails** at `SCORECARD.md:15` ("22 repos" vs measured 21); lessons and fleet-report
"22 rows" are literally accurate but are the carrier of the off-by-one; LOG round-17 section and
SKILL.md carry no count and need no change.
