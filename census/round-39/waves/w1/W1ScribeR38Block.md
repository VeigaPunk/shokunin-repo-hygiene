# W1ScribeR38Block — appended correction block for `corpus/lessons/round-38.md` (R1, R2, R14)

Seat: scribe, souji round 39 wave 1 (hyaku run 11). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Audited revision: lane HEAD `2201778e7736af82e7d8a42dec2494f115bf3923`; frozen base
`ed30b7f5b77939c9073348d810730bc4f355708d`; freeze `b769bfb84a264d8b284c09bc211d99f39a3e9126`.
Contract read first: `census/round-39/preregistration.txt` (C1 calibration 7; items
`census/round-39/c1-items.tsv` rows `R39-C1-01`, `R39-C1-02`, `R39-C1-14`).

No file outside this report was written. No git/jj mutation was run (read-only `log`, `show`,
`status`, `rev-parse`, `cat-file` only). Scratch:
`/fast/scratch/hyaku/souji-r39/W1ScribeR38Block/` — **removed at the end of the seat** (see §8).

## 1. Commands run (exact) and quoted output

Every command below was run with the shell cwd `/home/vgpnk/Projects/shokunin/souji-shokunin`
(absolute paths on every argument that names a file).

### 1.1 Revision state

```
$ git rev-parse HEAD
2201778e7736af82e7d8a42dec2494f115bf3923
$ git log --oneline -8
2201778 round-39: PROVINCE boundary note — two tool contracts repaired, no receipt class, certification OFF
790d16b round-39: C2 — drop unreachable EISDIR from the RECORD-MISSING line (wave-1 W1ExecC2Docstring)
094e531 round-39: C1 — R7 line names the reaped path as $HYAKU_SCRATCH, not a literal scratch root
50972f0 round-39: C1 — single-line anchor bullets for R5/R7/R15 closures
c0b007b round-39: C1 — 14 routed-defect corrections, r39 lesson with Gate/Mistakes, three source rows, gate-registry rows
601195a round-39: C2 — drift docstring puts each trigger on its class line (single-line rule)
bbd9b97 round-39: C2 — resolve --rev/--register-rev (exit 2), drift RECORD-MISSING/MALFORMED contract, r39-citation-rev fixture
b769bfb round-39: freeze — prereg C1/C2/C3, counters, fixtures, base controls
$ git status --porcelain corpus/lessons/round-38.md census/
?? census/round-39/make-cells.py
?? census/round-39/records/c2-after.txt
?? census/round-39/records/c3-after.txt
?? census/round-39/records/census-after.txt
?? census/round-39/records/census-before.txt
$ git show HEAD:corpus/lessons/round-38.md | grep -c 'R39-C1-'
3
$ grep -n 'R39-C1-' corpus/lessons/round-38.md
285:R39-C1-01 — ...
287:R39-C1-02 — ...
289:R39-C1-14 — ...
```

Verdict: the lesson file is **unmodified in the worktree** (absent from `git status`), so its bytes
are HEAD bytes; an equivalent three-line block is already committed at `c0b007b` inside
`### R39 append-only corrections (round 39, 2026-10-28)` (lines 283–289, file length 289 lines).
This seat therefore delivers a *draft* (report-only, per its spec) and §4 states the integration
choice, because appending a second copy would make the three anchors non-unique and weaken the
counter's line-unique re-derivation.

### 1.2 R1 facts — SOURCES census

```
$ git show ca4369a:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
162
$ git show fcdecaa:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
170
$ grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md
173
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji | tail -1
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji | grep -c 'W04'
47
$ cat census/round-39/records/census-before.txt
# SOURCES census before — source: git show ed30b7f5b77939c9073348d810730bc4f355708d:corpus/SOURCES.md > $S/SOURCES-before.md
census_rc=1
# NOTE: file-mode validation resolves used-by paths beside the copied file, so its E11 lines are an artifact of the scratch location; the row and W04 counts below are its measurements
rows=170
W04=47
E11=169
$ cat census/round-39/records/census-after.txt
# SOURCES census after — command: sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
census_rc=0
rows=173
W04=47
E11=0
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
```

Row statuses (`awk` over the `status` column of `corpus/SOURCES.md`, rows `S239`–`S246`):

```
S239  status=mined
S240  status=mined
S241  status=mined
S242  status=mined
S243  status=rejected
S244  status=mined
S245  status=mined
S246  status=rejected
```

`S244`/`S245`/`S246` each begin `supersedes S239` / `supersedes S242` / `supersedes S243` in their
`teaches` cell (`grep -n '^| S24[0-6]' corpus/SOURCES.md` → lines 193, 194, 195).

Verdict: **PASS** — r38 close = 170 rows (`162 → 170`, `SOURCES-added=8` = six `mined` +
two `rejected`, three of them supersessions), `W04=47`; the r39 tip reads 173 rows / `W04=47`
(three r39 rows added, warning count unchanged).

### 1.3 R1's quoted false literals

```
$ sed -n '158,159p' corpus/lessons/round-38.md
SOURCES census before → after: 162 rows, rc 0 → 167 rows, rc 0. Rows added by tier: A ×5
(S239-S242 admitted, S243 rejected); touched old→new: none. No `ground: F<k>` line moved: the four
$ grep -n 'W04' corpus/lessons/round-38.md
67:warns W04, which is allowed), and the Python `os.open` page was opened and is **not** a valid
285:R39-C1-01 — the `## Frontier` block above reads ...
$ sed -n '126p' /home/vgpnk/Projects/shokunin/.ufo/reports/round-38/souji.md
- Rows before → after: **162 → 167** (rc 0 both ends; 44 W04 duplicate-URL warnings, which the
```

Verdict: **PASS with a correction to the landed wording** — `A ×5` and `touched old→new: none` are
the lesson `## Frontier` block's literals; `44 W04` is the **r38 report's** literal (report line
126), not the lesson's (`grep -n W04 corpus/lessons/round-38.md` has no `44`). The landed
`R39-C1-01` line attributes all four literals to "the `## Frontier` block above"; the draft below
attributes `44 W04` to the report.

### 1.4 R2 facts — r38 report wording, wave counts, settlement time

```
$ sed -n '1,8p' /home/vgpnk/Projects/shokunin/.ufo/reports/round-38/souji.md     # last two lines
32 = 74 seats, 4 + 0 dead, inside the 64–128 band.
$ sed -n '202,206p' /home/vgpnk/Projects/shokunin/.ufo/reports/round-38/souji.md
|---|---|---|---|---|
| w1 | 42 | executor 10, reviewer 8, critic 5, scout 6, scribe 6, sentinel 2, mutation-tester 2, connector 1, revenger 1
| w2 | 32 launched (11 reports at filing) | reviewer 10, critic 10, mutation-tester 6, scribe 4, scout 2 | 0 reported |
$ git -C /home/vgpnk/Projects/shokunin log -1 --format='commit=%H%nauthor=%ai%ncommitter=%ci%nsubject=%s' -- .ufo/reports/round-38/souji.md
commit=6afdd3c602f436456166d2822ae8e76f17918d6f
author=2026-10-28 14:15:01 -0300
committer=2026-10-28 14:20:17 -0300
subject=round-38: souji report
$ ls .ufo/waves/round-38/w1/*.md | wc -l      # includes the r39 M7 fix copy
43
$ ls .ufo/waves/round-38/w1/ | grep -v fleetroot-draft | wc -l
43          # 42 reports + swarm-registry.json
$ ls .ufo/waves/round-38/w2/*.md | wc -l
32
$ python3 -c 'import json;print(json.load(open(".ufo/waves/round-38/w1-dispatch.json"))["counts"])'
{'spawn': 42, 'resume': 0, 'total': 42}
$ python3 -c 'import json;print(json.load(open(".ufo/waves/round-38/w2-dispatch.json"))["counts"])'
{'spawn': 32, 'resume': 0, 'total': 32}
$ python3 -c 'import json;print(json.load(open(".ufo/waves/round-38/w1-results.json"))["seats"])'
42
$ python3 -c 'import json;print(json.load(open(".ufo/waves/round-38/w2-results.json"))["seats"])'
32
$ stat -c '%y %n' .ufo/waves/round-38/w2-results.json .ufo/waves/round-38/w2/W2MutBattery.md
2026-10-28 14:39:39.792142465 -0300 .ufo/waves/round-38/w2-results.json
2026-10-28 14:38:15.662640460 -0300 .ufo/waves/round-38/w2/W2MutBattery.md
$ grep -n '31/32' corpus/lessons/round-38-verifier-spotcheck.md
147:   table says w1 dead 0 / w2 dead 0, and the disk shows 42/42 w1 reports and 31/32 w2 reports
```

Verdict: **PASS with a correction to the landed wording** — `w1-reports=42/42` (dispatch 42,
results 42, 42 report files) and `w2-reports=32/32` (dispatch 32, results 32, 32 report files) hold
at the r38 close; `W2MutBattery` settled-after-closure: report file 14:38:15, wave results record
(`w2-results.json`, which carries its seat entry) 14:39:39, i.e. 19 min after the 14:20:17 report
commit `6afdd3c6` (author stamp 14:15:01). `dead=0` is the measured reading, not the report's `4 + 0`.
The landed `R39-C1-02` line says "its waves table said w2 31/32" — that is **not** what the table
says (table literal: `32 launched (11 reports at filing)`); `31/32` is the **spot-check's disk
reading** (spot-check line 147). The draft below fixes the attribution.

### 1.5 R14 facts — the vacuity receipt and the three `escapes=9` rows

```
$ cat census/round-38/records/c1-vacuity2.txt
# C1 vacuity control at 2843805d4631b040219ed1ba60053035b5a86f07 — register row 1 expected token replaced by mismatches=99
MISMATCH R38-C1-1 EXPECTED-MISSING SCORECARD.md expected='mismatches=99'
MISMATCH R38-C1-1 COMMIT-RECEIPT-DISAGREES census/round-37/records/c2-after.txt expected='mismatches=99' ...
MISMATCH R38-C1-1 RECEIPT-DISAGREES census/round-37/records/c2-after.txt expected='mismatches=99' ...
MISMATCH R38-C1-7 ... (3 lines)
MISMATCH R38-C1-10 ... (3 lines)
SUMMARY cells=10 mismatches=9
rc=1
$ grep -n 'escapes=9' census/round-38/cells.tsv
2:R38-C1-1	SCORECARD.md	| R38-C1-1 |	escapes=9	escapes=4	census/round-37/records/c2-after.txt	02b4339...
8:R38-C1-7	LOG.md	R38-C1-7	escapes=9	escapes=6	census/round-37/records/c2-after.txt	02b4339...
11:R38-C1-10	corpus/QUALITY.md	R38-C1-10	escapes=9	escapes=4	census/round-37/records/c2-before.txt	861c2ba...
```

Verdict: **PASS** — the receipt's header claims a one-row substitution yet the arm replaced every
row whose expected token is `escapes=9`; exactly **three** register rows carry that expected token
(`cells.tsv` lines 2, 8, 11) and each emitted three mismatch classes → `mismatches=9`. A faithful
one-row substitution therefore reads `mismatches=3`. Independent corroboration in lane bytes:
`.ufo/waves/round-38/w1/W1ScribeLessonClaims.md:213` ("the arm changed every row whose expected
token is `escapes=9`").

### 1.6 Counter readings for the three rows (frozen `census/round-39/c1-counter.py`)

```
$ S=/fast/scratch/hyaku/souji-r39/W1ScribeR38Block
$ { sed -n '6p' census/round-39/c1-items.tsv; grep -E '^R39-C1-(01|02|14)\b' census/round-39/c1-items.tsv; } > "$S/items-3.tsv"
$ TMPDIR="$S" python3 -B census/round-39/c1-counter.py \
    --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 2201778e7736af82e7d8a42dec2494f115bf3923 \
    --items "$S/items-3.tsv" --register census/round-39/cells.tsv --scratch "$S/reg"
ITEM R39-C1-01 CLOSED
ITEM R39-C1-02 CLOSED
ITEM R39-C1-14 CLOSED
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=3 open=0 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=f706daafe728
rc=1
$ TMPDIR="$S" python3 -B census/round-39/c1-counter.py \
    --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev ed30b7f5b77939c9073348d810730bc4f355708d \
    --items "$S/items-3.tsv" --register census/round-39/cells.tsv --scratch "$S/reg"
ITEM R39-C1-01 OPEN ANCHOR-ABSENT corpus/lessons/round-38.md anchor='R39-C1-01'
ITEM R39-C1-02 OPEN ANCHOR-ABSENT corpus/lessons/round-38.md anchor='R39-C1-02'
ITEM R39-C1-14 OPEN ANCHOR-ABSENT corpus/lessons/round-38.md anchor='R39-C1-14'
SUMMARY items=3 open=3 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=f706daafe728
rc=1
```

Verdict: **PASS on the item arm** — the three rows read CLOSED at HEAD `2201778` and OPEN
`ANCHOR-ABSENT` at base `ed30b7f`, the same class the frozen control
`census/round-39/records/c1-before.txt` prints for these three ids (`open=16` overall).
`rc=1` is **not** an item failure: it is the register arm, which reads `cells=0` because
`census/round-39/cells.tsv` **does not exist at HEAD** (`ls: cannot access ... No such file or
directory`; `git ls-tree --name-only HEAD census/round-39/` lists only the three counters, the items
TSV, the prereg and `records/`). The C1 register arm is a different item's scope — see §7.

Two earlier attempts at this same command failed and are recorded rather than dropped:

```
# attempt 1 — items file built from `head -5` (the frozen header is line 6, not in the first five)
REFUSAL USAGE: items /fast/scratch/hyaku/souji-r39/W1ScribeR38Block/items-3.tsv has no header before line 6
rc=2
# attempt 2 — --scratch pointed at a directory that did not exist yet
FileNotFoundError: [Errno 2] No such file or directory: '/fast/scratch/hyaku/souji-r39/W1ScribeR38Block/reg/souji-r39-c1.akj6tfvn'
rc=1
```

Both are invocation errors on my side (wrong header offset; missing `mkdir -p "$S/reg"`), not tool
defects: the counter refused with its documented usage class and, second time, with a raw traceback
instead of a refusal — noted in §6 as a cosmetic finding, not part of this item's claim.

### 1.7 Draft-line validation against the frozen matcher

The draft lines were fed through the counter's own `parse_items` + `has_token` (imported, no
mutation):

```
$ python3 - "$S/draft-block.md"   # imports census/round-39/c1-counter.py
draft lines: 3
R39-C1-01 anchor=True must_ok=4/4 missing=[] mustnot_hits=[] verdict=CLOSED
R39-C1-02 anchor=True must_ok=5/5 missing=[] mustnot_hits=[] verdict=CLOSED
R39-C1-14 anchor=True must_ok=2/2 missing=[] mustnot_hits=[] verdict=CLOSED
```

Verdict: **PASS** — each draft line carries its anchor, every frozen `must` token as a whole token,
and no `mustnot` token.

## 2. The block (markdown, as it should read in the lesson)

```markdown
### R39 append-only corrections, block 2 (round 39, 2026-10-28; R1, R2, R14)

R39-C1-01 — the r38 close's sources numbers are false: the `## Frontier` block above reads "162 rows, rc 0 → 167 rows, rc 0", "A ×5" and "touched old→new: none", and the r38 report reads "44 W04"; the corrected close is SOURCES-rows=170 with SOURCES-added=8 rows (six `mined`: S239, S240, S241, S242, S244, S245; two `rejected`: S243, S246; three of the eight are supersessions S244→S239, S245→S242, S246→S243) and W04=47 at `ed30b7f`, as the non-author spot-check re-derived at `fcdecaa`; S244–S246 are named by this block and by the r39 Gate.

R39-C1-02 — the r38 report's opening "4 + 0 dead" is unevidenced: its waves table records "32 launched (11 reports at filing)" and the non-author spot-check read 31/32 w2 reports on disk; at the r38 close the disk reads w1-reports=42/42 and w2-reports=32/32, because W2MutBattery settled-after-closure at 14:39 (report 14:38:15, `w2-results.json` 14:39:39), 19 minutes after the 14:20:17 report commit `6afdd3c6`, so dead=0 with one late seat, not four dead seats.

R39-C1-14 — `census/round-38/records/c1-vacuity2.txt` describes its own operation wrongly: its header says one row's expected token was replaced by `mismatches=99`, yet the arm changed every row whose expected token is `escapes=9`, and `escapes=9` appears on three rows (`three-rows`: R38-C1-1 `SCORECARD.md`, R38-C1-7 `LOG.md`, R38-C1-10 `corpus/QUALITY.md`), each emitting three mismatch classes, so the receipt's `mismatches=9` is a three-row result; a faithful one-row substitution reads vacuity-operation=mismatches=3.
```

Ready-to-append snippet — byte-identical to the three anchored lines above, one physical line each
(no wrapping, no trailing spaces; the heading and one blank line precede them):

```text
### R39 append-only corrections, block 2 (round 39, 2026-10-28; R1, R2, R14)

R39-C1-01 — the r38 close's sources numbers are false: the `## Frontier` block above reads "162 rows, rc 0 → 167 rows, rc 0", "A ×5" and "touched old→new: none", and the r38 report reads "44 W04"; the corrected close is SOURCES-rows=170 with SOURCES-added=8 rows (six `mined`: S239, S240, S241, S242, S244, S245; two `rejected`: S243, S246; three of the eight are supersessions S244→S239, S245→S242, S246→S243) and W04=47 at `ed30b7f`, as the non-author spot-check re-derived at `fcdecaa`; S244–S246 are named by this block and by the r39 Gate.

R39-C1-02 — the r38 report's opening "4 + 0 dead" is unevidenced: its waves table records "32 launched (11 reports at filing)" and the non-author spot-check read 31/32 w2 reports on disk; at the r38 close the disk reads w1-reports=42/42 and w2-reports=32/32, because W2MutBattery settled-after-closure at 14:39 (report 14:38:15, `w2-results.json` 14:39:39), 19 minutes after the 14:20:17 report commit `6afdd3c6`, so dead=0 with one late seat, not four dead seats.

R39-C1-14 — `census/round-38/records/c1-vacuity2.txt` describes its own operation wrongly: its header says one row's expected token was replaced by `mismatches=99`, yet the arm changed every row whose expected token is `escapes=9`, and `escapes=9` appears on three rows (`three-rows`: R38-C1-1 `SCORECARD.md`, R38-C1-7 `LOG.md`, R38-C1-10 `corpus/QUALITY.md`), each emitting three mismatch classes, so the receipt's `mismatches=9` is a three-row result; a faithful one-row substitution reads vacuity-operation=mismatches=3.
```

## 3. Placement

Append-only, at end of file: after the last block, which is
`### R39 append-only corrections (round 39, 2026-10-28)` and ends at **line 289**
(`R39-C1-14 …`); the file is 289 lines at HEAD `2201778` and ends with that line plus a trailing
newline. The new heading goes after one blank line; nothing above is edited, reordered or removed.

## 4. Integration choice (required by the current lane state)

At HEAD `c0b007b` the lane **already carries** three equivalent lines (285/287/289) inside
`### R39 append-only corrections (round 39, 2026-10-28)`. Therefore:

- If the L1 keeps those bytes, **do not append this block**: a second copy duplicates the anchors
  and makes `grep -c` on each anchor 2, which weakens the frozen items' line-unique re-derivation
  (`c1-items.tsv` header: "Line-unique anchors keep the predicate re-derivable") even though the
  counter would still read CLOSED.
- If the L1 prefers the draft, **replace** the three lines in place (or drop the landed block and
  append this one) — never both. The draft's substantive deltas vs the landed text, each a
  calibration fix of the same class the round polices:
  1. `R39-C1-01`: landed attributes `"44 W04"` to the lesson's `## Frontier` block; `44 W04` is the
     r38 **report's** literal (report line 126), and the lesson's literal is `162 rows, rc 0 → 167
     rows, rc 0`. Draft attributes each literal to its file and quotes the lesson verbatim.
  2. `R39-C1-02`: landed says "its waves table said w2 31/32"; the table literal is
     `32 launched (11 reports at filing)` and `31/32` is the **spot-check's disk reading**
     (spot-check line 147). Draft fixes the attribution and adds the measured settlement stamps
     (`14:38:15` report, `14:39:39` results record, report commit `14:20:17`).
  3. `R39-C1-14`: landed says "`mismatches=9` needs every `escapes=9` row"; the draft states the
     frozen wording explicitly ("`escapes=9` appears on three rows") and names each row's file.

## 5. Verdicts per check

| check | evidence | verdict |
|---|---|---|
| anchor `R39-C1-01` present, single line, tokens `S246`, `SOURCES-rows=170`, `SOURCES-added=8`, `W04=47`, names S244–S246 | §1.7 matcher `must_ok=4/4`; §1.2 census measurements | PASS |
| anchor `R39-C1-02` present, single line, tokens `w1-reports=42/42`, `w2-reports=32/32`, `W2MutBattery`, `dead=0`, `settled-after-closure` | §1.7 `must_ok=5/5`; §1.4 counts + stamps | PASS |
| anchor `R39-C1-14` present, single line, tokens `vacuity-operation=mismatches=3`, `three-rows`; states `escapes=9` on three rows | §1.7 `must_ok=2/2`; §1.5 receipt + `cells.tsv` lines 2/8/11 | PASS |
| three rows CLOSED at HEAD, OPEN at base | §1.6 counter output both revisions | PASS |
| no `mustnot` token on any line | §1.7 `mustnot_hits=[]` ×3 | PASS |
| append-only placement named | §3 | PASS |
| report names every command with quoted output | §1 | PASS |

## 6. Findings (reported, not absorbed)

1. **`census/round-39/cells.tsv` is absent at HEAD `2201778`.** The frozen C1 predicate names it as
   `--register`, and the counter's register leg therefore reads `cells=0` → `rc=1` for any item
   subset. `census/round-39/make-cells.py` exists only as an untracked worktree file. The C1 register
   arm (`register_cells>=6`, `commit_distinct>=2`) is not reachable from committed bytes yet; it is
   outside this seat's item and is reported for the L1's C1 ledger.
2. **Landed `R39-C1-01`/`-02` misattribute two quoted literals** (§4). Both still satisfy their
   frozen `must` lists, so they are not contract failures — they are the same
   self-assessment-vs-observed-state class the round exists to close, which is why the draft is
   offered as a replacement rather than a duplicate.
3. **`w1-reports=42/42` is only derivable after excluding the r39 fix copy**
   `.ufo/waves/round-38/w1/W1ScribeReport-fleetroot-draft.md` (M7): `ls .ufo/waves/round-38/w1/*.md |
   wc -l` → 43, and `ls .ufo/waves/round-38/w1/ | grep -v fleetroot-draft | wc -l` → 43 including
   `swarm-registry.json`, i.e. 42 reports. Any future re-derivation must state that exclusion.
4. **`census/round-39/c1-counter.py --scratch <missing dir>` crashes instead of refusing.**
   `tempfile.mkdtemp(dir=args.scratch)` raises `FileNotFoundError` and the process exits 1 with a
   traceback, where every other precondition on this counter refuses with exit 2 (the documented
   could-not-evaluate class). Cosmetic and outside C1's predicate; recorded because the counter's own
   `--scratch` is the documented way to keep `/tmp` out of the run.

## 7. Out of scope / not claimed

- The r38 report's own fleet bytes (`.ufo/reports/round-38/souji.md`) — the corrections are carried
  as lane lesson bytes and, per the prereg, as r39 report errata.
- The C1 register arm, the C2/C3 legs, the other 13 C1 items, and any landing/commit.
- No receipt class, no deletion verdict, no certification (K5 HELD).

## 8. Scratch state

Scratch root `/fast/scratch/hyaku/souji-r39/W1ScribeR38Block/` held `items-3.tsv`,
`draft-block.md`, `reg/`. Removed with `rm -rf -- "$S"` at the end of the seat; verified absent:

```
$ rm -rf -- "$S"; test -e "$S" && echo "STILL-PRESENT $S" || echo "absent $S"
absent /fast/scratch/hyaku/souji-r39/W1ScribeR38Block
$ git status --porcelain corpus/lessons/round-38.md | wc -l
0
```

The lesson file carries no worktree modification from this seat (`git status` on it is empty; the
`M LOG.md`, `M SKILL.md`, `M corpus/QUALITY.md` entries in the lane status are sibling seats'
bytes, not mine). Nothing was written under `/tmp`, the fleet repo, a sibling lane, `~/.omp`,
`~/.config`, or `~/.local/bin`. No tool was installed or upgraded.
