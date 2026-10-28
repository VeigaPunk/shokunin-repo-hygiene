# W1CritReport — criticism of the r39 report plan

seat: W1CritReport (critic) · lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
round 39 / hyaku run 11, wave 1 · base `ed30b7f5b77939c9073348d810730bc4f355708d`, freeze
`b769bfb84a264d8b284c09bc211d99f39a3e9126` · read-only: no lane or fleet file written except this one.

Assignment: read the r38 filed report and the r38 spot-check's 16 routed defects, name which the r39
report must state explicitly, produce a per-section checklist the L1 can execute, and name the two
sections the marker rule does not require but the contract does. Advisory: the L1 integrates.

---

## 1. The two authorities, and the two sections the marker rule does not require

**The two sections: `Sources & frontier` and `Trend verdicts`.** Named twice by two authorities, not
inferred:

- prompt `/home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-39.md:121-125`, verbatim:
  "**Marker rule:** a contentless report (placeholder text, missing required sections other than
  **Sources & frontier** and **Trend verdicts**, or no evidence pointers) counts as the round
  **failed** — the driver relaunches the same round. A report that names real committed work but skips
  those sections is `ok` plus a minimum-content conformance defect, logged as one; neither section is a
  marker predicate."
- `PROTOCOL.md:156-161` (fleet root), verbatim on the frontier section: "It grades conformance only —
  its absence is a defect in the round notes, never a `report_of()` or marker predicate: a report
  missing it is not `failed` for that alone."

So the marker predicate requires four of the six contract sections (Work performed, Landed changes,
Before → after measurements, SHONEN); the contract requires all six. Every r39 report plan that
budgets "enough to pass the marker" therefore under-delivers by exactly those two sections — and both
are the sections that carried r38's *falsified numbers* (R1) and its *overstated verdicts*
(discernment).

**The implementing predicate is weaker still, and this is the duplicate-authority risk.** `PROTOCOL.md:196-204`
describes the marker as "the `SHONEN` heading … **and** the minimum substance above — work performed, at
least one evidence pointer, changes landed in the child repo each tied to a `LOG.md` entry, and a
checkable commit-hash citation". The code that actually runs is `scripts/shokunin-watchdog.sh:187-207`
`report_of()`: a SHONEN heading regex plus `MIN_REPORT_BYTES` (`:54`, default 400). Measured:

```
$ bash -c 'source /home/vgpnk/Projects/shokunin/scripts/shokunin-watchdog.sh >/dev/null 2>&1;
           UFO=/fast/scratch/hyaku/souji-r39/W1CritReport/fakeroot/.ufo;
           wc -c < "$UFO/reports/round-39/souji.md"; report_of souji 39 && echo ACCEPT || echo REJECT'
538
report_of=ACCEPT (driver completion fires on the stub)
```

The stub is `# souji - round 39` + `## SHONEN` + one `[~]` line + twelve filler lines: no claim, no
evidence pointer, no commit, no Sources & frontier, no Trend verdicts. The lane's own contract checker
rejects the same bytes:

```
$ python3 -B tools/souji-report-contract.py --report <stub> --shonen SHONEN.md
detail-claims: claim ids=0 expected 1-3
check-evidence=FAIL
detail-evidence: no evidence pointer
SUMMARY checks=7 pass=0 fail=7
```

And the converse, which is the decisive fact for this checklist: **r38's real report passes the
checker 7/7 and still carried 16 routed defects.**

```
$ python3 -B tools/souji-report-contract.py --report /home/vgpnk/Projects/shokunin/.ufo/reports/round-38/souji.md --shonen SHONEN.md
check-sections=PASS
check-shonen-boxes=PASS
check-trends=PASS
check-stale-lane=PASS
check-measurements=PASS
check-claims=PASS
check-evidence=PASS
SUMMARY checks=7 pass=7 fail=0
rc=0
```

Verdict: **a green pre-report gate is not evidence of report conformance.** The checklist below is
built to fail on the defects the gate structurally cannot see (numbers, dead seats, filing order,
capture, prompt scope, landed-changes coverage).

---

## 2. The 16 routed defects → what the r39 report must state explicitly

Source read: `corpus/lessons/round-38-verifier-spotcheck.md` § Routed defects (lines 155-215) and the
filed report `/home/vgpnk/Projects/shokunin/.ufo/reports/round-38/souji.md`. "Section" = where the r39
report must carry the statement; "must state" = the sentence the report may not omit; "r39 command" =
the check that keeps the sentence true.

| id | r38 defect | section | must state | r39 command (expected observable) |
|---|---|---|---|---|
| **R1** | Sources & frontier numbers false (162→167, "A ×5", "44 W04"; measured 162→170, 8 rows, 47 W04); S246 in no lesson byte | **Sources & frontier** + Errata | rows before→after **170 → 173**, rows added **3** (S247, S248, S249, all tier A `mined`), **W04=47**, `rc 0` at the landing, and *each new id named in `corpus/lessons/round-39.md`* | `git diff --numstat ed30b7f..<landing> -- corpus/SOURCES.md` → `5 0`; `git diff … \| grep -cE '^\+\|[[:space:]]*S[0-9]{3}'` → `3`; `grep -c '^\| S24[789]' corpus/lessons/round-39.md` → `3`; `sources-census.sh validate` → `rows=173 W04=47 rc=0` |
| **R2** | "4 + 0 dead" with no evidence, contradicted by its own table | **Work performed** opening + Waves/dead seats | the measured seat/dead numbers *with the command*, per seat, and the respawn map; never a bare "N + 0 dead" | `w1-spec.json` items=71, `ls .ufo/waves/round-39/w1/*.md \| wc -l`, `w1.ready.partial` entries=61 (at 15:02: 20 reports, 51 missing) |
| **R3** | report filed before WAVE-DONE (11/32 reports, no `w2-results.json`) | **Filing note** | filing happened *after* WAVE-DONE, quoting the `<wave>-results.json` and the report count at that instant; no "still settling" prose | `ls .ufo/waves/round-39/w1-results.json` (absent now) + the results body quoted |
| **R4** | wave evidence untracked (`.ufo/waves/` in `.gitignore:1`), unreachable to a fresh session | **Landed changes** + wave capture | where the wave evidence is *committed*, and the capture receipt's verify line | `bash tools/souji-wave-evidence-capture.sh <lane> 39 --verify --rev <landing>` → `verify-rev rev=… records=N failed=0 uncovered=0`; precedent `census/round-27..34/waves/` |
| **R5** | prompt committed by the lane (`068f75dc`), r37 defect 8 repeated, while the r38 ledger claimed "not repeated" | **Work performed** (misroot line) + **Errata** | the fleet commits authored `souji-shokunin` and their paths — *including the recurrence* — and the corrected ledger row | `git -C /home/vgpnk/Projects/shokunin log --author=souji --since=<launch> --format='%h %ci %s' --name-only` |
| **R15** | Landed-changes table missed 9 of 21 lane commits and ended with `<integration>` | **Landed changes** | every lane commit in `base..landing` by hash; no placeholder cell | set-difference script (§4.1); r38 control: `lane commits: 21 missing from report: 9`, `placeholder <integration> present: True` |
| R6 | four claim counters had no gate-registry row | Landed changes / Work performed | the SKILL rows for c1/c2/c3 counters **and both fixtures** by row name | `grep -n 'c1-counter (r39)\|c2-counter (r39)\|c3-counter (r39)\|r39-citation-rev\|r39-drift-record-rules' SKILL.md` → lines 273-277 |
| R7 | a receipt named a reaper-deleted `/fast/scratch/...` path | Before → after measurements | every receipt pointer is a revision or a committed path; no scratch root in a receipt | `grep -n '/fast/scratch' census/round-39/records/*.txt` → empty |
| R8 | prereg evidence pointer stale, instrument table incomplete | Before → after / Errata | the receipt actually regenerated is the one cited, and the fixture is named in the instrument list | cite `c2-after.txt`/`c3-after.txt` by committed path, not "the after receipt" |
| R9 | frozen prereg rewritten in place | Errata / prereg statement | r39's own prereg is append-only (A1 appended, 0 deleted) | `git diff --numstat b769bfb..<landing> -- census/round-39/preregistration.txt` → `9 0` |
| R10 | docstring class map ≠ code | Before → after (C2 L4) | the class→input mapping as the fixture measures it, both arms | `census/round-39/records/c2-after.txt` `LEG L4 PASS … new_maps=True old_maps=False` |
| R11 | `--rev` never resolved; no exit 2 | Before → after (C2 L1/L2) | `REFUSAL REV-UNRESOLVED`, exit 2, with base arm rc 1 | `c2-after.txt` `LEG L1 PASS new rc=2 class=True old rc=1 class=False` |
| R12 | SCORECARD finality labels; last block 2 commits behind | Before → after + SCORECARD rows | each row names the *measured* revision; one label per block | SCORECARD row text carries `<40-hex>`; `git cat-file -e <hex>^{commit}` |
| R13 | residual stale literals | every section | no number in the report that a receipt does not print | `grep -oE '[a-z_]+=[0-9]+' <report>` vs the receipts |
| R14 | receipt misdescribed its own operation | Before → after (counting command cell) | the command cell is the command actually run, flags included (`--register`, `--register-rev`, `--base-rev`) | paste the exact argv used; compare with the receipt header |
| R16 | r37 defect 4 still owed (r36 lesson rewrite) | Landed changes + Open items | *closed*, with the appended line, not "carried" | `git diff --numstat ed30b7f..<landing> -- corpus/lessons/round-36.md` → `4 0` |

The six the assignment names (R1, R2, R3, R4, R5, R15) are exactly the six the contract checker cannot
see and the spot-check found *in the report body* rather than in the lane's tools. R6-R16 are lane-byte
items (C1's 16 rows) whose report obligation is only the citation; they are included so the report does
not re-open a closed one in prose.

---

## 3. Per-section checklist the L1 can execute

Order matters: sections 1-6 are the contract order; A/B are required by the contract or the prompt but
not by the marker rule.

### §1 Work performed
- [ ] Opens by naming the three declared claims with their axes (calibration 7, operability 8,
      coverage 8) — same text as `census/round-39/preregistration.txt` § Claims, no paraphrase of the
      predicates.
- [ ] One bullet per work item with `path:line` or receipt path; the 16 routed defects are *not* listed
      as a group (the prereg's "Not claimed" forbids it) — the C1 bullet cites `c1-items.tsv` + the
      counter, not "all 16 closed".
- [ ] **Misroot line**: `git -C /home/vgpnk/Projects/shokunin status --porcelain` quoted, plus every
      fleet path written under the lane identity (R5).
- [ ] Wave paragraph: seat count from the spec, roles from the spec, dead seats measured (R2).

### §2 Landed changes
- [ ] Every lane commit in `base..landing` named by hash, each tied to a `LOG.md` entry (R15).
- [ ] No placeholder cell (`<integration>`, `TBD`, `pending`). The report's own fleet commit is
      described as the report, never as a lane change.
- [ ] The wave-evidence capture receipt is a *committed* path (R4), and the capture tool's verify line
      is quoted.
- [ ] The two new fixtures, the three counters and the SKILL rows 273-277 are each named (R6).

### §3 Before → after measurements
- [ ] Three rows (C1/C2/C3) + base controls. Each row: counting command (full argv), before value with
      its receipt, after value with its receipt, **measured revision** as 40-hex (R12).
- [ ] Quote the counters' *literal* SUMMARY lines, not the contract's abbreviated strings: C3's real
      line is
      `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5`
      — the contract text omits `cases=`, and a report that prints the contract string quotes a line no
      receipt contains (R1/R13 class). C2's is
      `SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=7ab7c3d85a81`.
- [ ] Every cited receipt resolves *at the landing revision* (R4/R8): `git cat-file -e <landing>:<path>`.
- [ ] C1's register arm: `cells.tsv` exists, ≥6 cells, ≥2 rows with `commit != receipt_rev` (C1's own
      limit from r38). Do not describe register rows that are not in the committed file.

### §4 Sources & frontier  ← **contract-required, marker-exempt**
- [ ] Counting command + both exit codes. **Both**, and honestly: `census-before.txt` records
      `census_rc=1` (`rows=170 W04=47 E11=169`, an E11 artifact of the scratch copy, stated in the
      receipt's own NOTE); `census-after.txt` records `census_rc=0 rows=173 W04=47 E11=0`. "rc 0 both
      ends" would repeat R1 verbatim.
- [ ] Rows before→after `170 → 173`; rows added `3` (S247, S248, S249; tier A `mined`); rows touched
      old→new `none` (`numstat 5 0` — five *lines*, three *rows*; conflating them is R1's exact
      arithmetic error); frontier rows advanced `none` with the reason.
- [ ] Each new id appears in `corpus/lessons/round-39.md` (the S246 lesson of R1): grep each id.

### §5 Trend verdicts  ← **contract-required, marker-exempt**
- [ ] Exactly one line each for `expansion`, `quality`, `discernment`, each opening with a verdict
      token (`improved`/`harmed`/`unchanged`/`unprovable-but-better`) and each with evidence a
      non-author can re-run.
- [ ] No unverifiable aggregate prose: r38's "the panel agreed on the four admits and the reject" was
      contradicted by S244/S246. If the report says a panel agreed, it cites the per-seat files.
- [ ] `discernment` must account for the wave-1 falsifications (this round's own instruments), not
      merely assert that corrections were disclosed.

### §6 SHONEN
- [ ] `grep -c '^## SHONEN'` → `1`; four `[~]`/`[ ]`/`[x]` lines, one per `SHONEN.md` box
      (measured: `SHONEN.md` has 4 boxes). `[x]` only with a named non-author verifier.

### A. Filing note (contract: §4 marker + prompt §6 directive)
- [ ] Written only after `w1-results.json` exists; quotes it. **Currently absent** — filing now repeats
      R3 exactly (`ls .ufo/waves/round-39/w1-results.json` → no such file; 20/71 reports).
- [ ] Names the wave totals at filing (seats, reports, dead, attack share). Spec now: 71 seats, roles
      executor 19 / reviewer 10 / scribe 10 / critic 8 / scout 8 / mutation-tester 5 / connector 4 /
      simplifier 4 / revenger 2 / sentinel 1; attack 30/71 = 42 % (band 64-128 satisfied).

### B. Errata / carried debt
- [ ] The r38 report's report-side halves that this round cannot edit are carried as errata (prereg
      "Not claimed"): R1's numbers, R2's dead-seat line, R15's table — and R5's ledger row 8, which is
      now *false twice over* (§4.2 below).
- [ ] R16 stated as closed with its line; R9 stated as append-only with `numstat 9 0`.

### C. Stale-lane, tool installs, disclosed limits
- [ ] `Stale-lane:` line (checker predicate 4) and a tool-installs line (none for this seat; the L1
      states its own).

---

## 4. Counterexamples found now — falsifications of the current plan

### 4.1 R15 control, reproduced on the r38 report (the check the L1 must run)

```
$ python3 - <<'EOF'   # base..landing lane commits vs report text
revs = git log --format=%H ca4369a..fcdecaa ; text = r38 report
EOF
lane commits: 21 missing from report: 9
missing: c5050ea be66886 cb5737a 9b9e2f8 a512efb 20eea73 f10a3a8 78ea25a 6949319
placeholder <integration> present: True
```

r39 analogue (run at filing): `git log --format=%H ed30b7f..<landing>` — 8 commits at 15:02
(`b769bfb`, `bbd9b97`, `601195a`, `c0b007b`, `50972f0`, `094e531`, `790d16b`, `2201778`), plus any
integration commit; every one must appear in the report by hash and every `commit` cell must satisfy
`git cat-file -e <h>^{commit}`.

### 4.2 R5 has already recurred in r39 — the report must not claim "not repeated"

```
$ git -C /home/vgpnk/Projects/shokunin show --stat --format='%h %an %ci %s' 36d25dbc
36d25dbc souji-shokunin 2026-10-28 14:34:23 -0300 round-39: souji dispatch evidence (hyaku inline attempt 1)
 .ufo/prompts/souji-round-39.md | 689 +++++++++++++++++++++++++++++++++++++++++
 1 file changed, 689 insertions(+)
$ git -C /home/vgpnk/Projects/shokunin show --stat --format='%h %an %ci %s' 068f75dc   # r38, R5
068f75dc souji-shokunin 2026-10-28 13:24:11 -0300 round-38: souji dispatch evidence (hyaku inline attempt 1)
 .ufo/prompts/souji-round-38.md | 689 +++++++++++++++++++++++++++++++++++++++++
$ grep -n "souji round=39" /home/vgpnk/Projects/shokunin/.ufo/watchdog.log
1860:2026-10-28T14:34:25-03:00 launch souji round=39 pgid=686189 driver=hyaku-inline attempt=1
```

Byte-for-byte the r38 defect, two seconds before the launch line. The r38 ledger row 8 said "not
repeated"; r39 must say **repeated** and correct that row by erratum. A report that writes "this round
committed no `.ufo/prompts/` path" is true only of the lane repo (`git log ed30b7f..HEAD -- .ufo/prompts`
is empty) and false of the round's acts — state both halves.

### 4.3 C1 is red right now, and its two open items are the R3/R4 evidence

```
$ python3 -B census/round-39/c1-counter.py --root . --rev $(git rev-parse HEAD) \
    --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv
ITEM R39-C1-03 OPEN FILE-ABSENT census/round-39/records/waves-wait.txt
ITEM R39-C1-04 OPEN FILE-ABSENT census/round-39/records/waves-capture.txt
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=2 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
rc=1
```

Consequence for the plan: **C1 cannot be claimed until the wave has settled and been captured.** Item
03 requires a `waves-wait.txt` whose line carries `waves=1,dead=0`; item 04 requires a
`waves-capture.txt` whose line carries `records=,failed=0,uncovered=0` (the capture tool's `--verify`
prints exactly `verify-rev rev=%s records=%d failed=%d uncovered=%d`,
`tools/souji-wave-evidence-capture.sh:589`). Filing early, or writing those receipts before WAVE-DONE,
fabricates the claim the round is scored on.

Also unlanded: `census/round-39/cells.tsv` does not exist and `make-cells.py` is untracked —

```
$ git ls-files census/round-39 | cat
census/round-39/c1-counter.py
census/round-39/c1-items.tsv
census/round-39/c2-counter.py
census/round-39/c3-counter.py
census/round-39/preregistration.txt
census/round-39/records/c1-before.txt
census/round-39/records/c2-before.txt
census/round-39/records/c3-before.txt
$ git status --porcelain
?? census/round-39/make-cells.py
?? census/round-39/records/c2-after.txt
?? census/round-39/records/c3-after.txt
?? census/round-39/records/census-after.txt
?? census/round-39/records/census-before.txt
```

The register arm (`register_cells>=6`, `commit_distinct>=2`) has **no committed file** yet, and the
four after/census receipts the report must cite are **working-tree only** — a pointer to them does not
resolve at a landing revision (R4/R8 class). Smallest safe correction: land `cells.tsv`, the two wave
receipts and the four receipts in the same integration commit that the report cites, and run the C1
counter with `--rev <that landing>`.

### 4.4 Wave state at 15:02 — filing now repeats R3

```
spec items=71 reports=20 missing=51
respawn map entries=61
$ ls .ufo/waves/round-39/w1-results.json   → No such file or directory
$ cat .ufo/waves/round-39/w1.ready
{"lane":"souji","round":39,"wave":"w1","dispatch":"…/w1-dispatch.json","l1":"SoujiR39"}
```

`w1.ready` means *launched*, not settled. `w1.ready.partial` carries 61 respawn mappings, so the dead-seat
line must distinguish **unsettled** (no report yet) from **dead** (settled with no report / failed
respawn) — r38's "4 + 0 dead" is the number that distinction is meant to prevent.

### 4.5 The contract strings handed to seats are abbreviations of the receipts

C3: assignment/claim text says `mutants=4 killed=4 survived=0 pristine=ok base_killed=0`; the receipt
prints `… base_killed=0 cases=7 tool_sha=… fixture_sha=…`. C1's assignment text and the receipt agree.
C2's agree. Only C3 differs, and `cases>=6` is the kill rule's floor — the report must quote the literal
line so the floor is visible.

### 4.6 Append-only held on r39's own prereg (do not lose this in prose)

```
$ git diff --numstat b769bfb..HEAD -- census/round-39/preregistration.txt
9	0	census/round-39/preregistration.txt
```

9 added, 0 deleted: A1 was appended, not rewritten (the R9 class). The report must state this with the
command; a prose "append-only respected" is the kind of sentence r38's spot-check falsified.

---

## 5. Verdicts

| # | check | observed | verdict |
|---|---|---|---|
| 1 | the two marker-exempt sections are named by the contract | prompt §4:121-125 names **Sources & frontier** and **Trend verdicts**; `PROTOCOL.md:161` repeats the frontier exemption | **PASS** — the answer is those two sections |
| 2 | the marker predicate is weaker than the contract text | stub 538 B → `report_of=ACCEPT`; same stub → `checks=7 pass=0 fail=7` | **FAIL (plan risk)** — a report built to the marker under-delivers by 2 sections and by every number check |
| 3 | gate green ⇒ report conformant | r38 report `checks=7 pass=7 fail=0`, rc 0, and 16 routed defects | **FAIL (falsified)** — the gate cannot see R1-R5/R15 |
| 4 | R1 covered by a command in the checklist | SOURCES `numstat 5 0`, 3 row lines, 170→173, W04 47 both ends, base `census_rc=1` documented | **PASS (checklist)** / **OPEN (report)** — no report exists yet |
| 5 | R2 covered | spec 71 / reports 20 / missing 51 / respawns 61 measured | **PASS (checklist)** / **OPEN** |
| 6 | R3 covered | `w1-results.json` absent; `w1.ready` = launch only | **PASS (checklist)** / **OPEN** — filing now would repeat R3 |
| 7 | R4 covered | `.gitignore:1 .ufo/waves/`; capture tool exists (`:589` verify line); precedent `census/round-27..34/waves/` | **PASS (checklist)** / **OPEN** — wave evidence is untracked today |
| 8 | R5 covered | `36d25dbc` authored `souji-shokunin` commits `.ufo/prompts/souji-round-39.md`, 14:34:23, launch 14:34:25 | **FAIL (already repeated)** — the report must state the recurrence and correct r38's ledger row 8 |
| 9 | R15 covered | r38 control reproduces 21/9/placeholder; r39 has 8 lane commits to name | **PASS (checklist)** / **OPEN** |
| 10 | C1 claim currently reachable | `open=2`, `register_cells=0`, `cells.tsv` absent, 4 receipts untracked | **FAIL (blocked on wave settle + capture)** — not a report defect, a sequencing constraint |
| 11 | C2 claim receipt | `SUMMARY legs=6 pass=6 fail=0 harm=0 …`, `L1/L2 rc=2 class=True` | **PASS (receipt reads green; not my claim to certify)** |
| 12 | C3 claim receipt | `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 …` | **PASS (receipt reads green; `cases=7 ≥ 6`)** |
| 13 | prereg append-only | `9 0` since freeze | **PASS** |
| 14 | SHONEN shape | `SHONEN.md` 4 boxes; r38 report `## SHONEN` count 1 | **PASS (checklist)** |

**Smallest safe corrections, in order:** (1) do not file until `w1-results.json` exists and quote it;
(2) land `cells.tsv`, the two wave receipts and the four after/census receipts in the integration
commit the report cites, then run C1 at that revision; (3) write the R5 recurrence and the R38-ledger
erratum; (4) build the Landed-changes table from `git log --format=%H ed30b7f..<landing>` with a
set-difference check, no placeholder; (5) quote literal SUMMARY lines and both census exit codes;
(6) give Sources & frontier and Trend verdicts full sections even though the marker does not demand
them.

Scratch: `/fast/scratch/hyaku/souji-r39/W1CritReport` (stub + fake `.ufo` root for the `report_of`
test) — removed with `rm -rf` before yielding; nothing of mine remains on disk. Tool installs: none
(no `pacman`, no `uv tool`, no `npx`; `python3`, `git`, `bash` sufficed).
