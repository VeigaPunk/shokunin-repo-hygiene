# W1ExecCommitList — r38 Landed-changes table vs. committed history (R15 evidence)

Seat: executor, round 39 wave 1. Item: produce the R15 evidence ("an unlanded commit table") from
committed history only. **No lane file was edited by this seat**; the only file written is this
report. Role: advisory, the L1 integrates.

Provenance at measurement time:

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
790d16b6492f67a8c8a7d13a596d92d3f01af4fe
$ git -C /home/vgpnk/Projects/shokunin rev-parse HEAD
c51b0c8b...            (fleet repo tip; report bytes introduced by 6afdd3c6)
```

The r38 filed report is one file in the **fleet** repo, one commit:

```
$ git -C /home/vgpnk/Projects/shokunin log --format='%h %s' -- .ufo/reports/round-38/souji.md
6afdd3c6 round-38: souji report
```

The report bytes are identical at the introducing commit, at fleet HEAD, and in the working tree, so
the identity of "the filed report" is unambiguous:

```
$ git -C /home/vgpnk/Projects/shokunin show 6afdd3c6:.ufo/reports/round-38/souji.md | sha256sum
ec33659f41200b6fd83db4bef6557b2f209437acb594814193e721a713598570  -
$ git -C /home/vgpnk/Projects/shokunin show HEAD:.ufo/reports/round-38/souji.md | sha256sum
ec33659f41200b6fd83db4bef6557b2f209437acb594814193e721a713598570  -
$ sha256sum /home/vgpnk/Projects/shokunin/.ufo/reports/round-38/souji.md
ec33659f41200b6fd83db4bef6557b2f209437acb594814193e721a713598570  /home/vgpnk/Projects/shokunin/.ufo/reports/round-38/souji.md
```

All measurements below read the r38 report out of git at `6afdd3c6` into
`/fast/scratch/hyaku/souji-r39/W1ExecCommitList/r38-souji-filed.md` (279 lines) and the commit list
out of the **lane** repo.

---

## Check 1 — the r38 round range

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format='%h %s' ca4369a..fcdecaa
fcdecaa round-38: intermediate measurement records as historical evidence
8093c70 round-38: filed-state receipts at 99efe06 and final measured-revision block
99efe06 round-38: S246 (S243 quote supersession) and the sibling-adjacency note
c5050ea round-38: durable counter-arms fixture, SKILL registry rows, receipt
be66886 round-38: final receipts at cb5737a and measured-revision block
cb5737a round-38: A9 random record names, claims corrections, A7 revision note
9b9e2f8 round-38: final receipts at 4bda5f6 and corrected composition label
4bda5f6 round-38: A8 (docstring token by AST span, whole-token behavioural cases), S244/S245 supersession rows, gate corrections
a512efb round-38: M7 misroot mistake and its repair receipt
da92035 round-38: lesson corrections after wave 1 (C1 row composition, A4-A7, envelope residuals)
20eea73 round-38: wave-1 adjudications in LOG
f10a3a8 round-38: final receipts at 78ea25a, wave-1 adjudications in LOG, receipt-pointer update in SCORECARD
78ea25a round-38: A7 revision — comment-stripped whole-token SUMMARY matching (r37 fixture stays 16/16, comment-tail exploit still refused)
6949319 round-38: wave-1 falsifications A4-A7 (record open, battery kill gate, opaque record names, receipt exact fields + receipt_rev arm + register envelope)
9b44320 round-38: lesson with wave adjudications and named limits; QUALITY Q86-Q88
020cfd5 round-38: A3 base-failure composition line, C2 composition receipt
7b542e2 round-38: final after receipts at the amended landing, SCORECARD rows and capability rows
2843805 round-38: tighten-only amendments A0-A2 (docstring-enum via ast+tokenize, isolated receipt-at-commit anchors, corrected six-case count)
828f86b round-38: after receipts at the corrections commit (C1 cells=10 mismatches=0, C2 12/12 base_fail=6, C3 4/4 pristine=ok)
cb80d0d round-38: reconcile the routed self-assessment cells (commit arm), open S239-S243, lesson draft
4090ee5 round-38: freeze claims, commit-arm reconciler, drift write-envelope and record fixtures, do-nothing controls
```

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-list --count ca4369a..fcdecaa
21
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-list --merges ca4369a..fcdecaa
(empty)
```

**Verdict 1 — PASS.** The range is 21 commits, linear, zero merges, all subjects `round-38:`. The
range excludes the base `ca4369a` and includes the landing `fcdecaa`, matching the r38 report's own
header (`census`-free prose: "Lane base `ca4369a…`; … landing `fcdecaa…`").

---

## Check 2 — the Landed-changes table and its rows

The table is at `r38-souji-filed.md:83-92` (section `## Landed changes`, header line 78). It has a
header row, 8 body rows, and 7 body rows carry a full 40-hex commit:

```
$ awk 'NR>=85 && NR<=92 {n=split($0,a,"|"); print NR": "a[n-1]}' r38-souji-filed.md
85:  `4090ee5b04ca3205d61c044b89fd9f318cf9850c`
86:  `cb80d0d09b04ff63c18d78ee5c1ec7bf6ea5c83d`
87:  `828f86b1581dd22a2ac656b7e185e587e4390389`
88:  `2843805d4631b040219ed1ba60053035b5a86f07`
89:  `7b542e22dca0098c5c743b586ce0e0fda67a856b`
90:  `020cfd5ecd404c9068fb60940fa0c4eb1b49c248`
91:  `9b4432000f51ea28caa21e8f92df23e9a5d9a01e`
92:  `<integration>`
```

The last row, verbatim:

```
| wave-2 findings integrated (this report's integration commit) | §Round 38 | `<integration>` |
```

**Verdict 2 — the last-row placeholder is confirmed.** Row 8 (line 92) is the only row whose commit
cell is not a hash: the literal `<integration>`, a placeholder for a commit that by construction did
not exist when the table was written. It is the report's own admission that the table is
incomplete. **7 of 21 range commits are named in the table; 14 are not.**

---

## Check 3 — per-commit table membership and report-wide mention

Measured by exact 40-hex cell extraction over lines 85–92 (table) and by 7-hex-token scan over all
279 lines (report-wide), each range commit matched by prefix:

| # | commit | subject (truncated) | in Landed table | named anywhere (first line) |
|---|---|---|---|---|
| 1 | `fcdecaa` | intermediate measurement records as historical evidence | **NO** | yes (line 5, also 264) |
| 2 | `8093c70` | filed-state receipts at 99efe06 and final measured-revision block | **NO** | yes (line 6) |
| 3 | `99efe06` | S246 (S243 quote supersession) and the sibling-adjacency note | **NO** | yes (line 105) |
| 4 | `c5050ea` | durable counter-arms fixture, SKILL registry rows, receipt | **NO** | **NO** |
| 5 | `be66886` | final receipts at cb5737a and measured-revision block | **NO** | **NO** |
| 6 | `cb5737a` | A9 random record names, claims corrections, A7 revision note | **NO** | **NO** |
| 7 | `9b9e2f8` | final receipts at 4bda5f6 and corrected composition label | **NO** | **NO** |
| 8 | `4bda5f6` | A8 (docstring token by AST span, whole-token behavioural cases), S244/S245 | **NO** | yes (line 245) |
| 9 | `a512efb` | M7 misroot mistake and its repair receipt | **NO** | **NO** |
| 10 | `da92035` | lesson corrections after wave 1 (C1 row composition, A4-A7) | **NO** | yes (line 244) |
| 11 | `20eea73` | wave-1 adjudications in LOG | **NO** | **NO** |
| 12 | `f10a3a8` | final receipts at 78ea25a, wave-1 adjudications in LOG, receipt-pointer | **NO** | **NO** |
| 13 | `78ea25a` | A7 revision — comment-stripped whole-token SUMMARY matching | **NO** | **NO** |
| 14 | `6949319` | wave-1 falsifications A4-A7 (record open, battery kill gate, …) | **NO** | **NO** |
| 15 | `9b44320` | lesson with wave adjudications and named limits; QUALITY Q86-Q88 | yes (line 91) | yes (line 91) |
| 16 | `020cfd5` | A3 base-failure composition line, C2 composition receipt | yes (line 90) | yes (line 90) |
| 17 | `7b542e2` | final after receipts at the amended landing, SCORECARD rows | yes (line 89) | yes (line 89) |
| 18 | `2843805` | tighten-only amendments A0-A2 (docstring-enum, anchors, six-case) | yes (line 88) | yes (line 88) |
| 19 | `828f86b` | after receipts at the corrections commit (C1 10/0, C2 12/12, C3 4/4) | yes (line 87) | yes (line 87) |
| 20 | `cb80d0d` | reconcile the routed self-assessment cells (commit arm), open S239-S243 | yes (line 86) | yes (line 86) |
| 21 | `4090ee5` | freeze claims, commit-arm reconciler, drift write-envelope, controls | yes (line 85) | yes (line 5, 6, 85) |

The partition of the 21 commits is therefore **7 tabled + 5 prose-only + 9 never named**:

- tabled (7): `4090ee5 cb80d0d 828f86b 2843805 7b542e2 020cfd5 9b44320`
- prose-only (5): `fcdecaa`, `8093c70`, `99efe06`, `da92035`, `4bda5f6` — and four of those five are
  incidental, not change claims:
  - `fcdecaa` is the "landing … (the lane tip at filing)" of line 5 and the checker subject of line 264.
  - `8093c70` appears only in line 6's bracket "claim commits through `8093c70`".
  - `99efe06` appears only inside the C1 measurement row as "`c1-after8.txt`, measured at `99efe06`".
  - `da92035` / `4bda5f6` appear only inside the named-limits bullet at lines 244-245:
    "the sources census was red on the intermediate landing commits (`cb80d0d`-`da92035`) because
    the S242 pipe fix was committed only at `4bda5f6`".
- never named (9): reconstructed by prefix-absence over the whole 279-line file:

```
$ for h in c5050ea be66886 cb5737a 9b9e2f8 a512efb 20eea73 f10a3a8 78ea25a 6949319; do \
    echo -n "== $h count="; grep -c "$h" r38-souji-filed.md; done
== c5050ea count=0
== be66886 count=0
== cb5737a count=0
== 9b9e2f8 count=0
== a512efb count=0
== 20eea73 count=0
== f10a3a8 count=0
== 78ea25a count=0
== 6949319 count=0
```

**Verdict 3 — the spot-check's "nine" is confirmed only under the report-wide definition, and
falsified under the definition the item states.** The item asks which commits the report "names …
in its Landed-changes table". Under that definition the unnamed count is **14**, not 9. The nine is
the count of commits never named **anywhere** in the 279-line report:

```
UNNAMED_TABLE   = ['fcdecaa','8093c70','99efe06','c5050ea','be66886','cb5737a','9b9e2f8',
                   '4bda5f6','a512efb','da92035','20eea73','f10a3a8','78ea25a','6949319']   n=14
UNNAMED_ANY     = ['c5050ea','be66886','cb5737a','9b9e2f8','a512efb','20eea73','f10a3a8',
                   '78ea25a','6949319']                                                     n=9
```

So R15's routed phrasing must be pinned to one of the two numbers before the r39 report quotes it:
**14 table-unnamed**, or **9 absent from the report entirely**. Quoting "nine" as the unlanded
commit count silently mixes the two definitions (5 prose-only commits would read as tabled).

---

## Check 4 — the report contradicts its own coverage claim

Line 6 asserts, about the same table:

```
freeze `4090ee5`, claim commits through `8093c70`, each named in **Landed changes**). Round shape: two v1 waves, 42 +
```

`8093c70` is itself absent from the table (Check 2: the table's newest commit is `9b44320`, line
91), and 13 further commits between `9b44320` and `8093c70` are absent too. Measured by ordering:
**every one of the 14 table-unnamed commits is strictly newer than the table's newest named commit
`9b44320`** — the table froze at the lesson commit and was never extended for the wave-2/measurement
commits it claims to cover.

**Verdict 4 — FALSIFIED on the report's own bytes.** Line 6's "each named in **Landed changes**" is
false for 14 of 21 range commits, including the `8093c70` bound it names in the same sentence. This
is the sharpest form of R15: not merely an incomplete table, but a table whose stated completeness
is contradicted by the table.

---

## Summary of verdicts

| check | measurement | verdict |
|---|---|---|
| 1 range enumeration | 21 commits, linear, 0 merges, all `round-38:` | PASS |
| 2 table rows | 8 body rows; 7 carriage rows carry a 40-hex commit; line 92 commit cell is `<integration>` | placeholder CONFIRMED |
| 3 per-commit membership | 7 tabled, 5 prose-only, 9 absent; table-unnamed = 14 | "nine" CONFIRMED report-wide, FALSIFIED table-only |
| 4 header self-claim | line 6 says every claim commit through `8093c70` is in the table; 14 are not | FALSIFIED |

Numbers the L1 can carry into the r39 report's R15 errata, each with its command above:
`range=21 tabled=7 prose_only=5 absent=9 table_unnamed=14 table_last_named=9b44320
table_placeholder_row=92 placeholder_text='<integration>' header_false_by=14`.

## Notes, limits, scratch

- Nothing was edited: this seat wrote only this report. `git -C …/souji-shokunin status --short`
  before and after shows the same four untracked `census/round-39/records/*.txt` files; the only
  entry that appeared between the two reads is `census/round-39/make-cells.py`, written by another
  seat, not by this one. The report itself is inside gitignored `.ufo/`.
- Definitional limit, stated rather than hidden: "names that hash" is scored by 7-hex-prefix
  presence (`c5050ea` etc. never occur as coincidental substrings in this 279-line file; each of the
  nine returns `grep -c 0`). A 6-hex or looser match would not change any cell: the shortest hash
  token the report uses is 7 hex.
- `census`-side consumers: the r38 reconciler's `COMMIT-UNNAMED` arm is not exercised here; it reads
  a register, not the report prose. Mapping these nine onto `census/round-39/cells.tsv` rows is not
  this seat's item and no value is asserted.
- Scratch used: `/fast/scratch/hyaku/souji-r39/W1ExecCommitList/` (report snapshot + measurement
  script). Removed on completion; nothing left on disk.
- No tool was installed or upgraded for this item.
