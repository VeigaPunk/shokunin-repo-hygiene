# W1ExecDeadSeats — R2 re-derived from disk (round 39, wave 1)

Seat: `W1ExecDeadSeats`, role executor, axis **calibration 7**.
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Fleet root (read-only): `/home/vgpnk/Projects/shokunin`.
Contract read first: `census/round-39/preregistration.txt` (freeze `b769bfb84a264d8b284c09bc211d99f39a3e9126`,
lane base `ed30b7f5b77939c9073348d810730bc4f355708d`). It names R2 as
"an unevidenced dead-seat count" and explicitly does **not** claim the r38 report bytes
("Not claimed — Not the r38 report's own fleet bytes"). This seat therefore measures the disk and
returns numbers the round-39 report can carry as errata; it asserts no claim leg of C1/C2/C3.

Scratch: `/fast/scratch/hyaku/souji-r39/W1ExecDeadSeats` (removed at end, see §Cleanup).
No tool installed or upgraded (python3 + git were sufficient).

---

## 1. Contract read

```
$ sed -n '1,6p;18,19p' /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/preregistration.txt
# souji round 39 — preregistration (frozen before any after-data)

lane: souji-shokunin
round: 39 (hyaku run 11, attempt 1)
agent: SoujiR39
base revision: ed30b7f5b77939c9073348d810730bc4f355708d (lane tip == origin/master at round start)
receipts) states a value or a completion the observed repo state contradicts (R1 census numbers,
R2 an unevidenced dead-seat count, R4 untracked wave evidence, R5 a write-scope breach the ledger
```
Verdict: **contract read** — R2 is carried by C1's item list; the *report's own bytes* are explicitly
outside this round's write scope, so this seat's job is measurement, not a byte edit.

---

## 2. Reports on disk, per wave

```
$ find .ufo/waves/round-38/w1 -maxdepth 1 -name '*.md' -type f | wc -l
43
$ find .ufo/waves/round-38/w2 -maxdepth 1 -name '*.md' -type f | wc -l
32
```

```
$ python3 -c "<spec-vs-disk diff: spec names vs basenames of *.md>"
== w1 items 42 reportDir .ufo/waves/round-38/w1
missing: 0 []
reports not in spec: ['W1ScribeReport-fleetroot-draft.md']
== w2 items 32 reportDir .ufo/waves/round-38/w2
missing: 0 []
reports not in spec: []
```

```
$ find .ufo/waves/round-38/w1 .ufo/waves/round-38/w2 -maxdepth 1 -name '*.md' -size 0 | wc -l
0
$ find .ufo/waves/round-38/w1 .ufo/waves/round-38/w2 -maxdepth 1 -name '*.md' -printf '%s %p\n' | sort -n | head -1
3161 .ufo/waves/round-38/w1/W1ScoutGitWorktree.md
```

```
$ python3 -c "<is W1ScribeReport / W1ScribeReport-fleetroot-draft / W2MutBattery in spec>"
True False True
$ head -6 .ufo/waves/round-38/w1/W1ScribeReport-fleetroot-draft.md
# souji round 38 — commit-arm citations, the drift write envelope, and record-validation coverage
... measured landing `<fill>`; ...
```

Verdict: **w1 = 42/42 seat reports, w2 = 32/32 seat reports**. The w1 `*.md` total of 43 is
42 seat reports plus **one non-seat artifact** (`W1ScribeReport-fleetroot-draft.md`, an unfilled
scribe working copy whose landing reads `<fill>`; not a spec name). No zero-byte report exists, so
no "empty file counted as a report" inflation. Counting raw files (43/32) instead of spec-matched
reports (42/32) is the one way to misread this disk.

---

## 3. Seats per spec

```
$ python3 -c "<json .ufo/waves/round-38/{w1,w2}-spec.json: len(items), unique names, item keys>"
== w1 items 42 reportDir .ufo/waves/round-38/w1
keys of item0: ['name', 'role', 'axes', 'prompt']
== w2 items 32 reportDir .ufo/waves/round-38/w2
keys of item0: ['name', 'role', 'axes', 'prompt']
```

```
$ python3 -c "<spec names vs results names>"
== w1 spec 42 unique 42 results 42 unique 42
  in spec not results: []
  in results not spec: []
  dup names: []
== w2 spec 32 unique 32 results 32 unique 32
  in spec not results: []
  in results not spec: []
  dup names: []
```

Verdict: **42 + 32 = 74 seats**, and the report's "42 + 32 = 74 seats" arithmetic is correct.
Every spec name has exactly one report and exactly one results row; no duplicates, no strays.

---

## 4. Seats settled per results file

```
$ python3 -c "<json .ufo/waves/round-38/{w1,w2}-results.json: keys, seats field, results len, union keys>"
== w1 keys ['lane', 'round', 'wave', 'seats', 'results']
 seats 42 results len 42
 union keys: ['agent', 'name', 'note', 'output']
== w2 keys ['lane', 'round', 'wave', 'seats', 'results']
 seats 32 results len 32
 union keys: ['agent', 'name', 'note', 'output']
```

```
$ python3 -c "<per-entry output parse + empty-output + blocker/error scan>"
== w1 results 42 empty outputs 0 with note 0 unparseable outputs 0
   error-ish keys: {'verdict': 16, 'status': 3}
== w2 results 32 empty outputs 0 with note 0 unparseable outputs 0
   error-ish keys: {'verdict': 11, 'status': 1}
```

```
$ python3 -c "<per-seat: report on disk + structured output>"
w1: ... results=42 spec_missing_report=[] spec_missing_results=[]
w2: ... results=32 spec_missing_report=[] spec_missing_results=[]
lane=souji round=38 wave=w2 seats_field=32 results_len=32
name	agent	report_on_disk	output_json
W2RevC1	reviewer	yes	yes
... (32 rows, every row report_on_disk=yes output_json=yes) ...
W2MutBattery	mutation-tester	yes	yes
W2ScoutOverlap	scout	yes	yes
lane=souji round=38 wave=w1 seats_field=42 results_len=42
unparseable 0 all reports present
```

```
$ python3 -c "<non-empty blockers / error key per results file>"
w1 results 42 with non-empty blockers 0 [] with error key []
w2 results 32 with non-empty blockers 0 [] with error key []
```

Caveat, stated because it bounds what "settled" means here: the results entries carry **no
`status` field** — `union keys: ['agent','name','note','output']`, and `note` is `None` for all 74.
Settlement is therefore derived, not declared: 74/74 entries exist, each with a non-empty,
JSON-parseable `output`, zero non-empty `blockers`, zero `error` keys, and an on-disk report for
the same seat name. 16 w1 and 11 w2 entries carry a `verdict` key (3 w1 and 1 w2 more carry
`status`); the rest are free-form reports of what was run. Verdict: **settled 42/42 (w1) and
32/32 (w2)**.

---

## 5. Dead seats — the true number

| wave | seats in spec | seat reports on disk | results rows | **dead** |
|---|---|---|---|---|
| w1 | 42 | 42 (+1 non-seat draft file) | 42 | **0** |
| w2 | 32 | 32 | 32 | **0** |
| total | 74 | 74 | 74 | **0** |

```
$ python3 -c "<one-line consolidation>"
w1: md_files=43 spec_seats=42 seat_reports=42 extra_md=['W1ScribeReport-fleetroot-draft'] results=42 spec_missing_report=[] spec_missing_results=[]
w2: md_files=32 spec_seats=32 seat_reports=32 extra_md=[] results=32 spec_missing_report=[] spec_missing_results=[]
```

Verdict: **dead seats = 0 + 0 = 0.** Nothing on disk supports a nonzero dead-seat count in either
wave. The r38 report's opening line

```
$ git -C /home/vgpnk/Projects/shokunin show 6afdd3c602f436456166d2822ae8e76f17918d6f:.ufo/reports/round-38/souji.md | sed -n '1,12p'
# souji — round 38 (hyaku run 11, attempt 1)
...
`master`. Lane base ... Round shape: two v1 waves, 42 +
32 = 74 seats, 4 + 0 dead, inside the 64–128 band.
```

contradicts the same report's own body

```
$ ... | sed -n '60,76p'
- **Wave 1 (42 seats, 0 dead)**: 10 executor, 8 reviewer, 5 critic, 6 scout, 6 scribe, 2 sentinel,
...
- **Wave 2 (32 seats, 0 dead)**: 10 reviewer, 10 critic, 6 mutation-tester, 4 scribe, 2 scout

$ ... | grep -n -i dead
7:32 = 74 seats, 4 + 0 dead, inside the 64–128 band.
64:- **Wave 1 (42 seats, 0 dead)**
70:- **Wave 2 (32 seats, 0 dead)**
199:## Waves, seats and dead seats
201:| wave | seats | role mix | dead | reports |
204:| w2 | 32 launched (11 reports at filing) | ... | 0 reported | `.ufo/waves/round-38/w2/` |
```

**R2 confirmed, and its replacement number is 0, not a smaller unknown.** The line-7 "4" has no
artifact behind it: no spec seat misses a report, none misses a results row, no report is empty, and
the only surplus file is a non-seat draft. So the r38 waves table and its wave bullets ("0 dead")
were right and the summary line was wrong — the defect is a *report-internal inconsistency plus an
unevidenced figure*, exactly as routed.

---

## 6. Filing-time arithmetic (R2's second half)

The r38 report commit, from the fleet repo (the lane has no `.ufo/reports` at all):

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-files .ufo/reports | head -10
(no output)
$ ls -la /home/vgpnk/Projects/shokunin/.ufo/reports/round-38/
-rw-r--r-- 1 vgpnk vgpnk 20890 Oct 28 14:20 souji.md
$ git -C /home/vgpnk/Projects/shokunin log --format='%H|%aI|%s' -n 3 -- .ufo/reports/round-38
6afdd3c602f436456166d2822ae8e76f17918d6f|2026-10-28T14:15:01-03:00|round-38: souji report
$ git -C /home/vgpnk/Projects/shokunin show -s --format='%H%nauthor=%aI%ncommitter=%cI%n%s' 6afdd3c
6afdd3c602f436456166d2822ae8e76f17918d6f
author=2026-10-28T14:15:01-03:00
committer=2026-10-28T14:20:17-03:00
round-38: souji report
```

The report's filing note and "11 reports at filing" claim, tested against file mtimes:

```
$ ... | grep -n -A6 "Filing note"
257:## Filing note
259:The report is filed after wave 1 settled (42/42, `w1-results.json`) and while wave 2 was still
260:settling: 11 of 32 reports were on disk and no `w2-results.json` existed at filing time.

$ python3 -c "<md count with mtime <= each reference instant>"
w1: md_files=43 ... md_le_author=43 md_le_committer=43 md_gt_author=0
w2: md_files=32 ... md_le_author=4 md_le_committer=12 md_gt_author=28
```

| reference instant (UTC-3) | w2 reports on disk | w1 reports on disk |
|---|---|---|
| report **author** time 14:15:01 | **4** | 43 (all, incl. draft) |
| report **committer** time 14:20:17 | **12** | 43 |

Verdict: the claimed "11 of 32" matches **neither** timestamp (4 at author time, 12 at commit time).
The w1 half of the filing note *is* sound: `w1-results.json` mtime is 14:03:39, before the 14:15:01
author time, and all 43 w1 files predate it, so "wave 1 settled 42/42" was true at filing.
"No `w2-results.json` existed at filing" is also true: that file's mtime is 14:39:39.

Also worth recording, because wave-2 reviewers disputed these very numbers: the fleet report file was
written at **14:20:16**, so the wave-2 seat `W2RevReport` (report mtime 14:19:23) legitimately wrote

```
$ head -20 .ufo/waves/round-38/w2/W2RevReport.md
... **Final measured revision: `be668863...`** ...
W2RevReport | "BLOCKER — the filed round-38 report does not exist"
```

— a measurement-instant artifact, not a surviving defect. Committed blob size equals the on-disk size
(`git cat-file -s 6afdd3c:.ufo/reports/round-38/souji.md` → `20890`; `stat -c '%s'` → `20890`), and
`git status --porcelain -- .ufo/reports/round-38/souji.md` is empty, so the committed bytes are the
filed bytes. The lane's `round-38/report-draft.md` is a same-size but **different** file
(`d6013dea799b4c8084691471ac70418a` draft vs `559e72b05180c8709f10850167c6873a` filed; the committed
blob hashes to `559e72b0…`), i.e. the draft is a near-copy, not the filed report.

---

## 7. `W2MutBattery.md` vs the r38 filing — the requested ordering

```
$ stat -c '%y %n' .ufo/waves/round-38/w2/W2MutBattery.md .ufo/waves/round-38/report-draft.md
2026-10-28 14:38:15.662640460 -0300 .ufo/waves/round-38/w2/W2MutBattery.md
2026-10-28 14:20:08.153854309 -0300 .ufo/waves/round-38/report-draft.md

$ python3 -c "<deltas>"
W2MutBattery mtime 2026-10-28 14:38:15
W2MutBattery - author 0:23:14.662641 | - committer 0:17:58.662641 | - lane_tip_ed30b7f 0:18:10.662641
w2-results vs battery 0:01:24.129502
```

`W2MutBattery.md` was written **23 min 14 s after the r38 report commit's author time**
(14:15:01 → 14:38:15), 17 min 58 s after that commit's committer time (14:20:17), 18 min 10 s after
the lane tip the r38 spot-check landed on (`ed30b7f`, author 14:20:05), and **1 min 24 s before
`w2-results.json` was written** (14:39:39). It is the last w2 report on disk (next newest is
14:27:13). Verdict: **post-filing on both clocks** — the r38 report and the r38 spot-check predate
it, and the battery seat settles inside the wave-2 settlement that the report's own filing note
declares unread.

Consequence for the spot-check's numbers (its lesson, read-only):

```
$ grep -n -A3 "R2 — an unevidenced dead-seat number" corpus/lessons/round-38-verifier-spotcheck.md
146:2. **R2 — an unevidenced dead-seat number.** The report's opening line says "4 + 0 dead"; its own waves
147-   table says w1 dead 0 / w2 dead 0, and the disk shows 42/42 w1 reports and 31/32 w2 reports
148-   (`W2MutBattery` absent). Nothing supports 4; state the measured numbers and mark the missing seat.
149:3. **R3 — the report was filed before WAVE-DONE.** ...
150-   filing and no `w2-results.json`; at closure 31 reports were on disk (27 written after the report's
151-   author timestamp) ...
```

- "42/42 w1" — reproduced here (§2).
- "31/32 w2 (`W2MutBattery` absent)" — true only inside the window **[14:27:13, 14:38:15)**, i.e. at
  the w2 directory's own mtime 14:33:57; it cannot be true at the spot-check's 14:20:05 commit. On
  today's disk the count is **32/32**, so the spot-check's "missing seat" no longer exists.
- "27 written after the report's author timestamp" — consistent with a 31-report disk (31 − 4 = 27).
  Today, with the battery present, the same measurement gives **28** (`md_gt_author=28`).

---

## 8. Verdicts per check

| # | check | verdict |
|---|---|---|
| 1 | contract read (C1 axis 7, R2 wording, report bytes outside lane scope) | **PASS** |
| 2 | w1 reports on disk vs spec | **PASS** — 42/42 seat reports; 43rd `*.md` is a non-seat draft |
| 3 | w2 reports on disk vs spec | **PASS** — 32/32 |
| 4 | seats per spec | **PASS** — 42 + 32 = 74, unique, no dupes |
| 5 | seats settled per results file | **PASS (derived)** — 42/42 and 32/32, 0 empty/unparseable/blocked outputs; no `status` field exists |
| 6 | dead-seat count | **R2 CONFIRMED** — true value **0 + 0 = 0**; report line 7's "4 + 0 dead" is unsupported and contradicts lines 64/70/203-204 |
| 7 | filing-time "11 of 32" | **REFUTED** — 4 at author time, 12 at committer time; neither is 11. w1 half of the filing note holds |
| 8 | `W2MutBattery.md` ordering | **MEASURED** — mtime 14:38:15, **+23 m 14 s** after the report's author time, **+17 m 58 s** after its committer time; 1 m 24 s before `w2-results.json` |
| 9 | spot-check's "31/32 (`W2MutBattery` absent)" | **CURRENTLY FALSE** — 32/32 now; the figure is time-stamped to [14:27:13, 14:38:15) |
| 10 | `W2RevReport` "filed report does not exist" | **TIME-STAMPED, not surviving** — fleet file mtime 14:20:16 vs seat measurement at 14:19:23 |

Net for the round-39 report / errata: R2's substance stands (an unevidenced dead-seat number) and
the correct figures are **w1 42 seats / 42 reports / 0 dead; w2 32 seats / 32 reports / 0 dead;
74 total, 0 dead**; the "4 dead" and the "11 of 32 at filing" both come off, and the spot-check's
31/32 should be stated as of its measurement instant, not as closure state.

## Appendix A — residual commands run (with observed output)

Every other command this seat issued, quoted so no read is unreported:

```
$ ls -la .ufo/waves/round-38/
-rw-r--r-- 1 vgpnk vgpnk  20890 Oct 28 14:20 report-draft.md
drwxr-xr-x 1 vgpnk vgpnk   1588 Oct 28 14:10 w1
-rw-r--r-- 1 vgpnk vgpnk 249528 Oct 28 14:03 w1-results.json
-rw-r--r-- 1 vgpnk vgpnk  49060 Oct 28 13:34 w1-spec.json
drwxr-xr-x 1 vgpnk vgpnk    944 Oct 28 14:33 w2
-rw-r--r-- 1 vgpnk vgpnk 219210 Oct 28 14:39 w2-results.json
-rw-r--r-- 1 vgpnk vgpnk  35749 Oct 28 13:48 w2-spec.json

$ git log --format='%H %aI %an %s' -- .ufo/reports/          # lane
(no output — the lane tracks no .ufo/reports path)

$ cat .gitignore
.ufo/waves/
census/operator-sweep-*/
__pycache__/

$ git ls-tree -r --name-only ed30b7f5b77939c9073348d810730bc4f355708d | grep -i 'round-38' | head -3
census/round-38/cells.tsv
census/round-38/preregistration.txt
census/round-38/records/a1-docstring-variants.txt

$ git log --format='%H|%aI|%cI|%s' --grep='round-38' -n 30   # head of the list
ed30b7f5b77939c9073348d810730bc4f355708d|2026-10-28T14:20:05-03:00|...|round-38 verifier spot-check (integrator, hyaku): non-author admit/reject
fcdecaaf293f0fee3c39cc148ae91389e04ef63c|2026-10-28T14:19:51-03:00|...|round-38: intermediate measurement records as historical evidence
8093c70a8e7f4105945b0cfaf53bab409b12e6f5|2026-10-28T14:19:18-03:00|...|round-38: filed-state receipts at 99efe06 and final measured-revision block

$ git show --stat --format='%H%n%aI%n%s' ed30b7f5b77939c9073348d810730bc4f355708d
ed30b7f5b77939c9073348d810730bc4f355708d
2026-10-28T14:20:05-03:00
round-38 verifier spot-check (integrator, hyaku): non-author admit/reject

 corpus/lessons/round-38-verifier-spotcheck.md | 225 ++++++++++++++++++++++++++
 1 file changed, 225 insertions(+)
```

```
$ stat -c '%y %s %n' .ufo/waves/round-38/w2-results.json .ufo/waves/round-38/w1-results.json \
    .ufo/waves/round-38/w1 .ufo/waves/round-38/w2
2026-10-28 14:39:39.792142465 -0300 219210 .ufo/waves/round-38/w2-results.json
2026-10-28 14:03:39.402309624 -0300 249528 .ufo/waves/round-38/w1-results.json
2026-10-28 14:10:39.769449292 -0300 1588 .ufo/waves/round-38/w1
2026-10-28 14:33:57.676918125 -0300 944 .ufo/waves/round-38/w2

$ ls .ufo/waves/round-38/ | grep -i "done\|ready"
w1.ready
w1.ready.dispatched
w2.ready
w2.ready.dispatched
```

No `WAVE-DONE` marker exists for either wave in this round, which is why §4 derives settlement from
`*-results.json` rather than from a done file. The dispatch maps corroborate the seat counts (line 1
is a timestamp, line 2 the map):

```
$ python3 -c "<parse .ready.dispatched: first line, len(map)>"
w1 first line: 2026-10-28T13:36:05 | map entries: 42
w2 first line: 2026-10-28T14:13:49 | map entries: 32
```

```
$ python3 -c "<list explicit verdict/status per w2 seat>"      # 11 of 32 rows; three quoted
W2RevC2 | "C2 claim REPRODUCED exactly at the tip; r37 escape control REPRODUCED; A1 docstring case correctly rejects ...
W2RevReport | "BLOCKER — the filed round-38 report does not exist"
W2CritAdmission | "ADMIT C1/C2/C3 with 5 routed defects (D1, D4 require append-only fixes before filing)"
W2ScribeCaps | "NO row states a count its command no longer prints; 6/6 rows reproduce; ...
W2ScoutOverlap | "free"
```

```
$ md5sum .../souji-shokunin/.ufo/waves/round-38/report-draft.md /home/vgpnk/Projects/shokunin/.ufo/reports/round-38/souji.md
d6013dea799b4c8084691471ac70418a  .../round-38/report-draft.md
559e72b05180c8709f10850167c6873a  /home/vgpnk/Projects/shokunin/.ufo/reports/round-38/souji.md
$ git -C /home/vgpnk/Projects/shokunin show 6afdd3c602f436456166d2822ae8e76f17918d6f:.ufo/reports/round-38/souji.md | md5sum
559e72b05180c8709f10850167c6873a  -
$ stat -c '%y %s %n' /home/vgpnk/Projects/shokunin/.ufo/reports/round-38/souji.md
2026-10-28 14:20:16.902729680 -0300 20890 /home/vgpnk/Projects/shokunin/.ufo/reports/round-38/souji.md
$ git -C /home/vgpnk/Projects/shokunin status --porcelain -- .ufo/reports/round-38/souji.md
(no output)
$ git -C /home/vgpnk/Projects/shokunin cat-file -s 6afdd3c602f436456166d2822ae8e76f17918d6f:.ufo/reports/round-38/souji.md
20890
```

```
$ ls .ufo/waves/round-39/
gen-w1-spec.py  w1  w1-dispatch.json  w1-gen.err  w1-spec.json  w1-validation.err  w1.ready  w1.ready.partial
$ ls .ufo/waves/round-39/w1 | wc -l
14
$ grep -n -A12 "^## R2\|R2[ .:—-]" corpus/lessons/round-38-verifier-spotcheck.md   # lines 146-151, quoted in §7
```

## Cleanup

Scratch `/fast/scratch/hyaku/souji-r39/W1ExecDeadSeats` was created for the per-seat status dumps and
removed at the end of the seat (`rm -rf`); nothing of mine remains outside this report file. No git
or jj mutation was run anywhere; every repository read was `log`/`show`/`status`/`ls-files`/
`cat-file`/`rev-parse`-class. No tool installed or upgraded.
