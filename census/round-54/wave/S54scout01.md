# Souji Round 54 Seat S54scout01 Report

- **Seat**: S54scout01
- **Role**: Scout (repo recon and pre-integration hand-checks at lane tip)
- **Wave**: round-54 / w1 (12 seats)
- **Lane**: `souji-shokunin` (`/home/vgpnk/Projects/shokunin/souji-shokunin`)
- **Fleet Head**: `3b0d5329147d3b05d3aec5e908c75405ae3bc05a`
- **Lane Tip**: `bfdbb336329e6afba3ab1ca83cbd6d9759271062`
- **Freeze Commit**: `3c394cab0cd406bbab72b8d365e0f3deed4ef98a`
- **Base Revision**: `fe12daad2549f534650d406ebdbac9113d59313f`
- **Overall Verdict**: PASS (all 8 tasks verified with exact evidence; no defects found)

---

## 1. Tip State

### Commands
```bash
GIT_OPTIONAL_LOCKS=0 /home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh state /home/vgpnk/Projects/shokunin/souji-shokunin
GIT_OPTIONAL_LOCKS=0 git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -3
```

### Verbatim Output
```
state branch=master local=bfdbb336329e6afba3ab1ca83cbd6d9759271062 remote=bfdbb336329e6afba3ab1ca83cbd6d9759271062 ahead=0 behind=0 head=detached tracked=0 untracked=8
bfdbb336 round-54: C2 capture — fleet-root census re-taken at fleet HEAD 3b0d5329 (49 entries, tracked 22 / ignored 22 / untracked-stray 5 / symlink 0), RECEIPT_VERSION=1 run receipt binding CAPTURE_SHA256; tool bytes unchanged (pinned e7e79952, staged outside the fleet root, copied cmp-exact)
3c394cab round-54: freeze — preregistration (2 claims: C1 calibration v3 annotation-agreement, C2 coverage v3 capture), v3 counters, extended builder (pinned GIT dates, hardened git env), expected TSVs, absent-instrument + v2-arm controls, pre-flight receipts (census-before conf rc 0, selftests pinned, base note) — before any claim receipt
fe12daad round-53 verifier spot-check (integrator, hyaku): non-author admit/reject
```

### Assessment
- Tip hash: `bfdbb336329e6afba3ab1ca83cbd6d9759271062` (`bfdbb336`)
- Freeze commit: `3c394cab0cd406bbab72b8d365e0f3deed4ef98a` (`3c394cab`)
- Confirmed: The freeze commit (`3c394cab`) precedes the capture commit (`bfdbb336`) as its immediate parent.
- Receipt: `.ufo/waves/round-54/w1/S54scout01/receipts/task1-tip-state.txt`
- **Verdict**: PASS

---

## 2. Zone Check at the Tip

### Python One-Liner
```bash
python3 -B -c 'import re; A="grep -c \"^ADDED\" census/round-51/records/ws-drift-vs-r46.tsv"; R=re.compile(r"(?:→|\()\s*(\d+)"); [print(f"{p}:{n}\n  zone_32: {repr(after[:32])}\n  zone_tokens: {[int(m.group(1)) for m in R.finditer(after) if m.start()<32]}\n  first_at_or_beyond_32: {next((int(m.group(1)) for m in R.finditer(after) if m.start()>=32), None)}") for p, n in [("SCORECARD.md",1196),("census/round-51/preregistration.txt",125)] for ln in [open(f"/home/vgpnk/Projects/shokunin/souji-shokunin/{p}").readlines()[n-1]] for after in [ln[ln.find(A)+len(A):]]]'
```

### Verbatim Output
```
SCORECARD.md:1196
  zone_32: '` (78); `grep -c "^| S274 |" cor'
  zone_tokens: [78]
  first_at_or_beyond_32: 1
census/round-51/preregistration.txt:125
  zone_32: '` (78);\n'
  zone_tokens: [78]
  first_at_or_beyond_32: None
```

### Assessment
- Inside the frozen 32-character zone, exactly one annotation token (`78`) exists per site (`SCORECARD.md:1196` and `census/round-51/preregistration.txt:125`).
- The first token starting at or beyond offset 32:
  - `SCORECARD.md:1196`: `1` at character offset 48 (from `grep -c "^| S274 |" corpus/SOURCES.md` (1)).
  - `census/round-51/preregistration.txt:125`: `None` (line terminates with newline within offset 10).
- Receipt: `.ufo/waves/round-54/w1/S54scout01/receipts/task2-zone-check.txt`
- **Verdict**: PASS

---

## 3. Append-Only Check

### Command
```bash
GIT_OPTIONAL_LOCKS=0 git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --numstat --no-renames fe12daad2549f534650d406ebdbac9113d59313f..HEAD -- SCORECARD.md LOG.md SKILL.md corpus/README.md corpus/SOURCES.md census/round-51/preregistration.txt census/round-51/records/ws-drift-vs-r46.tsv
```

### Verbatim Output
```
(no output)
```

### Whole-Tree Validation (`fe12daad..HEAD`)
```bash
GIT_OPTIONAL_LOCKS=0 git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --numstat fe12daad2549f534650d406ebdbac9113d59313f..HEAD
```
```
467	0	census/round-54/c1-counter.py
379	0	census/round-54/c2-counter.py
24	0	census/round-54/controls/c1-control-donothing.txt
20	0	census/round-54/controls/c2-control-donothing.txt
472	0	census/round-54/fixtures/build-fixtures.py
54	0	census/round-54/fixtures/run-matrix.sh
200	0	census/round-54/preregistration.txt
2	0	census/round-54/records/base-note.txt
14	0	census/round-54/records/c1-selftest-expected.tsv
18	0	census/round-54/records/c1-selftest.txt
11	0	census/round-54/records/c2-selftest-expected.tsv
15	0	census/round-54/records/c2-selftest.txt
143	0	census/round-54/records/census-before-receipt.txt
130	0	census/round-54/records/census-before.txt
14	0	census/round-54/records/fleet-root-census-run.txt
59	0	census/round-54/records/fleet-root-census.tsv
1	0	census/round-54/records/porcelain-at-base.txt
4	0	census/round-54/records/sources-count-pinned-revs.txt
```

### Assessment
- Named core files had 0 modifications between `fe12daad` and `HEAD`.
- Across the entire diff range `fe12daad..HEAD`, 18 new files were created in `census/round-54/` with 2,027 total insertions and 0 deletions.
- Deletions are 0 everywhere.
- Receipt: `.ufo/waves/round-54/w1/S54scout01/receipts/task3-append-only.txt`
- **Verdict**: PASS

---

## 4. Freeze Audit

### Commands
```bash
GIT_OPTIONAL_LOCKS=0 git -C /home/vgpnk/Projects/shokunin/souji-shokunin show --stat 3c394cab0cd406bbab72b8d365e0f3deed4ef98a
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum census/round-54/c1-counter.py census/round-54/c2-counter.py census/round-54/fixtures/build-fixtures.py census/round-54/records/c1-selftest-expected.tsv census/round-54/records/c2-selftest-expected.tsv
```

### Verbatim Output
```
commit 3c394cab0cd406bbab72b8d365e0f3deed4ef98a
Author: souji-shokunin <souji@shokunin.local>
Date:   Tue Nov 3 17:15:18 2026 -0300

    round-54: freeze — preregistration (2 claims: C1 calibration v3 annotation-agreement, C2 coverage v3 capture), v3 counters, extended builder (pinned GIT dates, hardened git env), expected TSVs, absent-instrument + v2-arm controls, pre-flight receipts (census-before conf rc 0, selftests pinned, base note) — before any claim receipt

 census/round-54/c1-counter.py                      | 467 ++++++++++++++++++++
 census/round-54/c2-counter.py                      | 379 +++++++++++++++++
 census/round-54/controls/c1-control-donothing.txt  |  24 ++
 census/round-54/controls/c2-control-donothing.txt  |  20 +
 census/round-54/fixtures/build-fixtures.py         | 472 +++++++++++++++++++++
 census/round-54/fixtures/run-matrix.sh             |  54 +++
 census/round-54/preregistration.txt                | 200 +++++++++
 census/round-54/records/base-note.txt              |   2 +
 census/round-54/records/c1-selftest-expected.tsv   |  14 +
 census/round-54/records/c1-selftest.txt            |  18 +
 census/round-54/records/c2-selftest-expected.tsv   |  11 +
 census/round-54/records/c2-selftest.txt            |  15 +
 census/round-54/records/census-before-receipt.txt  | 143 +++++++
 census/round-54/records/census-before.txt          | 130 ++++++
 census/round-54/records/porcelain-at-base.txt      |   1 +
 .../round-54/records/sources-count-pinned-revs.txt |   4 +
 16 files changed, 1954 insertions(+)

f45d3d8f4eced147b7e2c4127bf5fefe6d080f2f0fd0c637cfd44f8d41fccf7e  census/round-54/c1-counter.py
84b05295d5b84af23079c8fade6f7e640454ac25c56c842fb0233ea779735e09  census/round-54/c2-counter.py
ae5881f850ba5f5895fc27e6e3185658af372535ae7ccf971476175be118b1ba  census/round-54/fixtures/build-fixtures.py
4e73c495b6a7d1db1ef8dc5506ac874a167720a48e7618d2a41ccec55af2a1c7  census/round-54/records/c1-selftest-expected.tsv
e32f793468cf370781a860f8b642b6a42e1d589f70c0b7f575ded130263fc00d  census/round-54/records/c2-selftest-expected.tsv
```

### Side-by-Side Pin Comparison
| Artifact | Observed SHA-256 | `census/round-54/preregistration.txt` Pin | Status |
| :--- | :--- | :--- | :--- |
| `census/round-54/c1-counter.py` | `f45d3d8f4eced147b7e2c4127bf5fefe6d080f2f0fd0c637cfd44f8d41fccf7e` | line 29: `f45d3d8f4eced147b7e2c4127bf5fefe6d080f2f0fd0c637cfd44f8d41fccf7e` | MATCH |
| `census/round-54/c2-counter.py` | `84b05295d5b84af23079c8fade6f7e640454ac25c56c842fb0233ea779735e09` | line 93: `84b05295d5b84af23079c8fade6f7e640454ac25c56c842fb0233ea779735e09` | MATCH |
| `census/round-54/fixtures/build-fixtures.py` | `ae5881f850ba5f5895fc27e6e3185658af372535ae7ccf971476175be118b1ba` | line 146: `ae5881f850ba5f5895fc27e6e3185658af372535ae7ccf971476175be118b1ba` | MATCH |
| `census/round-54/records/c1-selftest-expected.tsv` | `4e73c495b6a7d1db1ef8dc5506ac874a167720a48e7618d2a41ccec55af2a1c7` | line 30, 148: `4e73c495b6a7d1db1ef8dc5506ac874a167720a48e7618d2a41ccec55af2a1c7` | MATCH |
| `census/round-54/records/c2-selftest-expected.tsv` | `e32f793468cf370781a860f8b642b6a42e1d589f70c0b7f575ded130263fc00d` | line 94, 149: `e32f793468cf370781a860f8b642b6a42e1d589f70c0b7f575ded130263fc00d` | MATCH |

- Receipt: `.ufo/waves/round-54/w1/S54scout01/receipts/task4-freeze-audit.txt`
- **Verdict**: PASS

---

## 5. Correction Liveness

### Commands
```bash
python3 -B -c '
base = "/home/vgpnk/Projects/shokunin/souji-shokunin"
with open(f"{base}/SCORECARD.md") as f: sc = f.readlines()
print("1268:", sc[1268-1].rstrip())
print("1270:", sc[1270-1].rstrip())
with open(f"{base}/LOG.md") as f: log = f.readlines()
print("2527:", log[2527-1].rstrip())
with open(f"{base}/corpus/README.md") as f: cr = f.readlines()
print("870:", cr[870-1].rstrip())
'
GIT_OPTIONAL_LOCKS=0 git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f778b9d131574d3ff09c0cc8a077643c0fc84bb4:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
GIT_OPTIONAL_LOCKS=0 git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 9bf9234ae4d11c7b31706354302a9e95ad0d1f81:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
cat /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-54/records/sources-count-pinned-revs.txt
```

### Verbatim Output
```
1268: R53-CORRECTION LOG.md:2527 stale=274->275 recomputed=198->199
1270: R53-CORRECTION corpus/README.md:870 stale=274->275 recomputed=198->199

2527: - S275 admitted (git(1) GIT_OPTIONAL_LOCKS, located quote 25 words, capture census/round-52/sources/); knowledge entry corpus/knowledge/fleet-root-stray-census.md. corpus/SOURCES.md 274 -> 275 rows.

870: - SOURCES 274 -> 275 rows (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`); census exit 0 (conf form, this host). Assimilation: none (open L0 on mass id drift, r46). considerthese/: no such directory.

198
199

# registry row counts at the two revisions pinned for the SOURCES-annotation recompute
# command: git show <rev>:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
before f778b9d131574d3ff09c0cc8a077643c0fc84bb4: 198
after  9bf9234ae4d11c7b31706354302a9e95ad0d1f81: 199
```

### Assessment
- Stale pair on annotated lines (`LOG.md:2527` and `corpus/README.md:870`) is `274 -> 275 rows`, matching `stale=274->275` on filing lines (`SCORECARD.md:1268` and `1270`).
- Recomputed count at `f778b9d1`: exactly 198.
- Recomputed count at `9bf9234a`: exactly 199.
- Both recomputed counts match `census/round-54/records/sources-count-pinned-revs.txt` and match `recomputed=198->199` in both filings.
- Receipt: `.ufo/waves/round-54/w1/S54scout01/receipts/task5-correction-liveness.txt`
- **Verdict**: PASS

---

## 6. LOG/README Scan Preview

### Command
```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE 'corpus/SOURCES\.md' LOG.md corpus/README.md | grep -E '[0-9]+ -> [0-9]+'
```

### Verbatim Output
```
LOG.md:1801:- C3 coverage (1baf4da02b71b012ee2426ea7c309496c0c3aca0): `corpus/knowledge/jj-dropped-keep-object-lifetime.md` (`ground: F1`), row S222 new (`corpus/SOURCES.md` 145 -> 146), fixture `tests/fixtures/r31-jj-object-clock.sh`, record `census/round-31/records/jj-object-clock-run.txt` (17 `RESULT` lines, jj 0.45.1, git 2.56.0); v1 `legs=11 fail=10 f1_entries=3` -> `legs=11 fail=0 f1_entries=4`, v2 `legs=12 fail=11` -> `legs=12 fail=0`, v3 `legs=13 fail=0` (both remover mutants differ from the record with fewer `object_present=no` lines). Met.
LOG.md:1804:- Frontier: `corpus/SOURCES.md` 145 -> 146 rows, S222 opened this round with its snapshot and fetch receipt (`census/round-31/sources/`); census rc 0 at the start (`census/round-31/records/census-start.txt`), the end census committed with this entry; F1 map row in `corpus/README.md` `## Round 31` and the boundary note in `PROVINCE.md` (`## Round 31 boundary note (F1 object lifetime)`).
LOG.md:1817:- Frontier: `corpus/SOURCES.md` 146 -> 147 rows (S223, tier A, opened 2026-10-26); census rc 0 at start and end (`census/round-32/records/census-end.txt`). Assimilation: none (20 staged entries rejected per entry). considerthese/: absent.
LOG.md:1898:- Frontier: `corpus/SOURCES.md` 170 -> 174 rows (S247-S250; S250 supersedes S247 after a wave seat showed S247's quote hid the refusal clause), W04 47 -> 47, census rc 0 at both ends; no `ground:` line moved. Assimilation: none — the staged package serves none of the three claims and its id range collides with the lane's own.
LOG.md:1932:- **Frontier:** `corpus/SOURCES.md` 182 -> 183 rows (S259 Python `site`, tier A), W04 52 -> 52, census exit 0 at both ends (`census/round-42/records/census-before.txt`). Assimilation: none; no `considerthese/` directory exists in this lane.
LOG.md:2527:- S275 admitted (git(1) GIT_OPTIONAL_LOCKS, located quote 25 words, capture census/round-52/sources/); knowledge entry corpus/knowledge/fleet-root-stray-census.md. corpus/SOURCES.md 274 -> 275 rows.
LOG.md:2563:  + named limits). corpus/SOURCES.md 199 -> 200 rows (census command recomputed at both
LOG.md:2578:  "corpus/SOURCES.md 274 -> 275 rows" — LOG.md:2527 (the r52 entry) and
corpus/README.md:809:- Registry: 181 -> 182 rows (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`, `census/round-41/records/census-final.txt`), census exit 0. Assimilation: none; no `considerthese/` directory exists in this lane.
corpus/README.md:815:- Registry: 182 -> 183 rows (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`), census exit 0. Assimilation: none; no `considerthese/` directory exists in this lane. No knowledge entry added; F1 stays frontier.
corpus/README.md:870:- SOURCES 274 -> 275 rows (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`); census exit 0 (conf form, this host). Assimilation: none (open L0 on mass id drift, r46). considerthese/: no such directory.
corpus/README.md:879:- SOURCES 199 -> 200 rows (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`;
```

### Analysis & Exemption Breakdown
Registry row count at current tip: 200 (recompute grep: `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`).
`c1-counter.py` instruments the SOURCES-pair scan via:
1. `max(A, B) > registry_rows` (lines where the declared pair overstates the registry).
2. Exemption: `PTR_RE = re.compile(r'[A-Za-z0-9_.\-]+:\d')` (meta-references citing a `path:line` pointer are exempt).

| File & Line | Quoted Pair | Exceeds 200/201? | Carries `path:line` Pointer? | Counter Status |
| :--- | :--- | :--- | :--- | :--- |
| `LOG.md:1801` | (145 -> 146) | No (146 <= 200) | No | Out of scope (historical note) |
| `LOG.md:1804` | 145 -> 146 | No (146 <= 200) | No | Out of scope (historical note) |
| `LOG.md:1817` | 146 -> 147 | No (147 <= 200) | No | Out of scope (historical note) |
| `LOG.md:1898` | 170 -> 174 | No (174 <= 200) | No | Out of scope (historical note) |
| `LOG.md:1932` | 182 -> 183 | No (183 <= 200) | No | Out of scope (historical note) |
| `LOG.md:2527` | 274 -> 275 | **YES** (275 > 200) | No | **Flagged / Requires filing** (filed at `SCORECARD.md:1268`) |
| `LOG.md:2563` | 199 -> 200 | No (200 <= 200) | No | Out of scope (historical note) |
| `LOG.md:2578` | 274 -> 275 | **YES** (275 > 200) | **YES** (`LOG.md:2527`) | **EXEMPT** via `PTR_RE` pointer rule |
| `corpus/README.md:809` | 181 -> 182 | No (182 <= 200) | No | Out of scope (historical note) |
| `corpus/README.md:815` | 182 -> 183 | No (183 <= 200) | No | Out of scope (historical note) |
| `corpus/README.md:870` | 274 -> 275 | **YES** (275 > 200) | No | **Flagged / Requires filing** (filed at `SCORECARD.md:1270`) |
| `corpus/README.md:879` | 199 -> 200 | No (200 <= 200) | No | Out of scope (historical note) |

- Receipt: `.ufo/waves/round-54/w1/S54scout01/receipts/task6-sources-scan.txt`
- **Verdict**: PASS

---

## 7. considerthese/ Absence Re-check & Open souji L0 Questions

### Commands
```bash
ls /home/vgpnk/Projects/shokunin/souji-shokunin | grep -ci consider || echo "grep returned rc $?"
grep -n '^souji |' /home/vgpnk/Projects/shokunin/.ufo/l0-questions.md | cut -c 1-80
```

### Verbatim Output
```
0
grep returned rc 1
59:souji | round-16 | Operator scope call on the census contractions round 16 ke
66:souji | round-17 | jj keep refs: colocated lanes accumulate refs/jj/keep/* (s
67:souji | round-17 | Disposition of the untracked operator output souji-shokuni
70:souji | round-18 | Approve reaping the 58 souji fixture orphans (cwd-deleted;
71:souji | round-18 | May souji re-derive NAMESPACE_SHA256 in tools/souji-preser
79:souji | round-20 | F5 reason-field exposure ruling requested: source review s
202:souji | round-40 | The read-only `merge/souji/` package's staged S109-S242 I
205:souji | round-40 | Correction to the round-40 collision note above (W2 `R40w
206:souji | round-41 | inline dispatcher log (.ufo/state/inline-dispatcher.log) 
215:souji | round-44 | Prior r43 verifier routed defect 5 asks for operator-leve
223:souji | round-46 | merge/souji staged package (134 rows, head 8b94c5c) has 5
235:souji | round-46 | L2 floor on this Windows host: no AgentSwarm/seat dispatc
245:souji | round-48 | The round contract census command names the conf form (so
252:souji | round-50 | Consolidated proposal to CLOSE the carried census conf-fo
261:souji | round-52 | Operator ruling wanted on the fleet-root census's credent
262:souji | round-52 | Operator decision on the derivation of the 'ignored' colu
263:souji | round-52 | Fleet-root stray entries reported report-only (no removal
264:souji | round-52 | Host note, no ruling requested: the round-start census co
```

### Assessment
- `considerthese/` is completely absent from the lane repo (`ls | grep -ci consider` = 0, return code 1).
- 18 open souji L0 questions listed. Line 223 is the open r46 question on mass ID drift (`merge/souji staged package (134 rows, head 8b94c5c) has 5...`), which continues to hold assimilation closed.
- Receipt: `.ufo/waves/round-54/w1/S54scout01/receipts/task7-considerthese-l0.txt`
- **Verdict**: PASS

---

## 8. Capture Commit Check

### Commands
```bash
GIT_OPTIONAL_LOCKS=0 git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -e bfdbb336329e6afba3ab1ca83cbd6d9759271062 && echo present
GIT_OPTIONAL_LOCKS=0 git -C /home/vgpnk/Projects/shokunin/souji-shokunin show --stat bfdbb336329e6afba3ab1ca83cbd6d9759271062
```

### Verbatim Output
```
present
commit bfdbb336329e6afba3ab1ca83cbd6d9759271062
Author: souji-shokunin <souji@shokunin.local>
Date:   Tue Nov 3 17:32:39 2026 -0300

    round-54: C2 capture — fleet-root census re-taken at fleet HEAD 3b0d5329 (49 entries, tracked 22 / ignored 22 / untracked-stray 5 / symlink 0), RECEIPT_VERSION=1 run receipt binding CAPTURE_SHA256; tool bytes unchanged (pinned e7e79952, staged outside the fleet root, copied cmp-exact)

 census/round-54/records/fleet-root-census-run.txt | 14 ++++++
 census/round-54/records/fleet-root-census.tsv     | 59 +++++++++++++++++++++++
 2 files changed, 73 insertions(+)
```

### Assessment
- Object `bfdbb336329e6afba3ab1ca83cbd6d9759271062` is present in the lane git database.
- Commit adds `fleet-root-census-run.txt` (14 lines) and `fleet-root-census.tsv` (59 lines).
- Receipt: `.ufo/waves/round-54/w1/S54scout01/receipts/task8-capture-commit.txt`
- **Verdict**: PASS

---

## 9. Tip Counter Verification (C1 & C2)

Both frozen counters were executed against the lane tip `bfdbb336329e6afba3ab1ca83cbd6d9759271062`:

### C1 Counter Run
```bash
python3 -B census/round-54/c1-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev bfdbb336329e6afba3ab1ca83cbd6d9759271062 \
  --base fe12daad2549f534650d406ebdbac9113d59313f \
  --record-sha256 2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30 \
  --sources-rev-before f778b9d131574d3ff09c0cc8a077643c0fc84bb4 \
  --sources-rev-after 9bf9234ae4d11c7b31706354302a9e95ad0d1f81 \
  --scratch /fast/scratch/hyaku/souji-r54/S54scout01/c1-scratch
```
**Output**:
```
SITE path=SCORECARD.md line=1196 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=125 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=bfdbb336329e base=fe12daad2549
```
Exit code: `0`

### C2 Counter Run
```bash
python3 -B census/round-54/c2-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev bfdbb336329e6afba3ab1ca83cbd6d9759271062 \
  --capture census/round-54/records/fleet-root-census.tsv \
  --receipt census/round-54/records/fleet-root-census-run.txt \
  --tool-sha256 e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b \
  --scratch /fast/scratch/hyaku/souji-r54/S54scout01/c2-scratch
```
**Output**:
```
SUMMARY entries=49 rows=49 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok tool_pin=ok rev=bfdbb336329e
```
Exit code: `0`

- Receipt: `.ufo/waves/round-54/w1/S54scout01/receipts/tip-counter-runs.txt`
- **Verdict**: PASS

---

## 10. Defect Classification

- **New Defects**: NONE.
- **Named Limits** (confirmed disclosed per `census/round-54/preregistration.txt` lines 157-169):
  1. The anchor zone remains frozen at 32 characters; count tokens wholly starting beyond offset 32 (such as the `1` on line 1196 at offset 48) are not evaluated as annotations for this anchor.
  2. The `corpus/SOURCES.md` annotation scan is line-based and explicitly exempts lines carrying a `path:line` pointer (e.g. `LOG.md:2578` referencing `LOG.md:2527`).
  3. Historical notes within registry reach (pairs `<= registry_rows`) are out of scope and not recomputed.
  4. Monotonicity of the append-only registry is assumed.

All checks are green. No unclassified or unrouted defects exist.

---

## 11. Receipt Index
All receipt files are preserved in the seat directory:
- `receipts/task1-tip-state.txt`
- `receipts/task2-zone-check.txt`
- `receipts/task3-append-only.txt`
- `receipts/task4-freeze-audit.txt`
- `receipts/task5-correction-liveness.txt`
- `receipts/task6-sources-scan.txt`
- `receipts/task7-considerthese-l0.txt`
- `receipts/task8-capture-commit.txt`
- `receipts/tip-counter-runs.txt`
