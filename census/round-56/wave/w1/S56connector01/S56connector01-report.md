# S56connector01 — sibling-overlap scan (souji round 56, wave w1)

Role: connector. Mode: read-only against the lane and the sibling lanes; no sibling tool was executed.
Measured revision: `cce21b555a617cadda782613ec1e9d3a0c12ac83` (base `fafe371694fea41c5d23f63083865d5ccf3f1d36`).
Sibling bytes read (worktree == HEAD, verified): kaidoku `a35e514105234515e266440aa33a578536b0007b`,
chousa `f748abbb6bf58388e732facd4ecec5612419c457`, kama `6035e952c2521999e192d6f236331f265ac98392`.

All eight frozen pins verified by sha256 before probing (c1/c2 counters, builder, runner, both expected
TSVs, both v4 counters) — exact match, no stop-and-report. The two r56 counter blobs at the measured
revision hash identically to the pins (`git show cce21b55:census/round-56/c1-counter.py` =
`975d3520…bbf179`, `c2-counter.py` = `5608201…259cb8`).

## Instruction defects (reported, not repaired)

1. **Path typo.** The seat assignment names chousa's tool as
   `tools/corpus/evidence/round50/stale-count-check.py`; the committed path is
   `corpus/evidence/round50/stale-count-check.py` (no `tools/` prefix). Probed the real path.
2. **Verdict enum conflict.** The generic seat wrapper prescribes
   `VERDICT: AGREE|DISAGREE|ATTACK-SURVIVED|ATTACK-FOUND|NONE`; this seat's task prescribes
   `VERDICT: NONE|OVERLAP-FOUND`. Used the seat-specific enum (the connector has no agree/attack
   verdict): `VERDICT: OVERLAP-FOUND`.
3. **Write-path conflict (procedural).** The seat bounds allow writes only under
   `.ufo/waves/round-56/w1/S56connector01/`, while the assignment trailer names
   `.ufo/waves/round-56/w1/S56connector01.md`. Wrote the canonical report in the seat directory and the
   scoped findings at the trailer path (the same convention the sibling seats used this wave); no other
   path was written.

## 1. S1 class (splitlines versus LF) in the two named sibling tools

Both tools have the S1 class in code. Neither is live on the committed inputs measured here.

### kaidoku `tools/round-59/annotation-audit.py` (sha256 `ba9ccbb9…74a0bf`)

- **Present.** `extract()` at `annotation-audit.py:107` reads the receipt text from
  `git show REV:RECEIPT` decoded with `errors="replace"` (`:220`) and enumerates
  `lines = text.splitlines()` (`:116`), `enumerate(..., start=1)` (`:118`). Finding line numbers
  (`ann["line"]`, e.g. `:242`, `:259`) and command→output→annotation binding are positions in that
  splitlines list. `raw.strip()` (`:114`) additionally treats VT/FF/NEL as whitespace.
- **Mechanism.** The same one-sentence mechanism as the souji r55 S1 shape: `str.splitlines()` also
  breaks on `\x0b \x0c \x1c \x1d \x1e \x85 \u2028 \u2029`, while the committed file's line numbers
  (git, editor, grep -n) count LF only. A FF/VT/NEL inside a `$` command line splits it into two
  "lines"; a fragment starting `$ ` becomes a second command, and an unterminated quote makes the
  bound probe `COMMAND_UNREEXECUTABLE` — a false finding on bytes that are one LF line. NUL is *not*
  a splitlines boundary (measured), so no NUL-refusal analogue exists here.
- **Unit.** Receipt-local annotation lines: pasted `$` command, the next integer output, and
  `(base: N -> record: M)` annotations bound to the most recent command.
- **Scope.** One receipt at one revision (`--receipt`, `--rev`, optional `--base-rev`), re-derived by
  `git show|lstree` + `grep -c`. No corpus filing grammar, no fence/HTML-comment grammar, no numstat.
- **Overlap with souji's counter.** **Mechanism only.** Same splitlines-vs-LF defect class as
  ERRATUM-R55-1 / F7-FF2 and the same `errors="replace"` decode shape, but a different unit
  (receipt annotations vs SCORECARD `R52-CORRECTION`/`R53-CORRECTION` filings + LOG/README pair
  annotations) and a different scope (one receipt vs a full corpus revision). The shared name
  "annotation-agreement counter" is a naming collision, not a predicate overlap: souji's annotation
  is a SOURCES registry row pair; kaidoku's is a `base→record` receipt probe count.

### chousa `corpus/evidence/round50/stale-count-check.py` (sha256 `4273436a…3fcbecd9`)

- **Present.** Two splitlines sites: `receipt_rows()` (`:25–27`) counts data rows after
  `read_text(encoding="utf-8").splitlines()`; `main()` (`:69`) scans
  `path.read_text(encoding="utf-8").splitlines()`. The named-line grammar `NAMES` (`:22`,
  `(?::|line\s+)(\d+)\b`) resolves `LOG.md:1803`/`line 1803` as a *splitlines index*
  (`nums[k - 1]`, `:40`). `ln.strip()` (`:26`) has the same exotic-whitespace sensitivity.
- **Mechanism.** A FF/VT/NEL anywhere before a named line shifts the index; the correction names a
  line number that, under LF/git numbering, is a different physical line. This is the exact
  arithmetic of the souji v3 S1 bug (splitlines hidden-line set vs LF correction line number).
  Demonstration in Receipt R5: after one FF, `line 3` resolves to `still-l2` under splitlines while
  LF line 3 is `l3`. A second, weaker surface: a FF inside a TSV field adds a row to `receipt_rows()`.
- **Unit.** Count phrases (`QUOTES=<n>`, `<n>-row manifest`, `<n> located quotes`,
  `CAPTURE_BOUND=<n>/<n>`) in lane prose, compared with the data-row count of
  `corpus/evidence/round49/spans.tsv`; resolution grammar is `correction: … superseded by …` naming
  a line (`:21–22`).
- **Scope.** chousa's `PROSE` set `corpus/QUALITY.md`, `corpus/README.md`, `LOG.md`,
  `corpus/lessons/round-49.md` (`:18`) plus that lane's `spans.tsv`. Two of those file names —
  `LOG.md`, `corpus/README.md` — are exactly souji's `PAIR_SITES` names, so the *scope names*
  overlap, but the unit differs (count statements, not SOURCES pair annotations) and the grammar
  differs (`correction: … superseded by` vs `R52/R53-CORRECTION` filing + arrow pair).
- **Overlap with souji's counter.** **Mechanism only, with a file-scope name overlap.** Same
  splitlines-vs-LF class as F7-FF2; not the same unit, not the same grammar, not the same filing
  model. No fence/HTML-comment hiding and no correction-token grammar.

### Liveness measurement

No VT/FF (`[\x0b\x0c]`) or NEL (`\xc2\x85`) bytes exist in the kaidoku round-58/59 demo receipts or
in chousa's four prose files + `spans.tsv`; `splitlines()` count equals the LF count on every measured
input (Receipt R4). The S1 class is therefore latent in both sibling tools, not live on their
committed inputs — but both accept caller-supplied receipts/files and would diverge on one.

A second-order instance outside item 1: kaidoku `tools/round-61/numstat-edge-audit.py:153` parses
`git diff --numstat` output with `stdout.splitlines()`; that is the *same unit* as souji's named
"numstat LF-only parse" hardening (the r55 named limit where a raw NEL path record splits). It is
latent for the same fixed-ASCII-path reason souji recorded, but the class is present in the sibling
that duplicates the numstat predicate. `round-62/base-binding-sweep.py:161` and
`round-63/edge-numstat-sweep.py:145` repeat splitlines over `git ls-tree` path output (different
unit, same record-splitting class).

## 2. Overlap scan of the r56 claim surfaces against sibling tools/tests

**Population.** The seven-token grep (`<!--`, `CORRECTION`, `R52-CORRECTION`, `receipt`,
`RECEIPT_VERSION`, `hidden_lines`, `numstat`) over `*-shokunin/tools` and `*-shokunin/tests` matches
505 files (310 outside souji); `receipt` dominates. Every candidate was narrowed by reading the
predicate, not by the token. Exact finding-name strings were also checked for collisions.

**Rule used.** An overlap is a file that measures the same unit with the same grammar as a r56 C1/C2
instrumented surface. Disposition (whether binary is refused by name, skipped, or recorded) is noted
separately and does not by itself erase the unit+grammar overlap.

**Declared overlap count: N = 7 (same unit + same grammar).** Of those, exactly 1 has souji's
binary-refusal disposition; 6 share the numstat unit+grammar with a different comparison/claim.

| # | File (lane, sha256 prefix) | Line(s) | Unit + grammar | Disposition / difference |
|---|---|---|---|---|
| 1 | `kaidoku-shokunin/tools/round-61/numstat-edge-audit.py` (`6b967e20`) | `parse_numstat` `:151–163`; finding `NUMSTAT_BINARY` `:120`, used `:235–246` | per-path numstat add/del between two revs; `git diff --numstat` three tab columns, `-` = binary | **Exact r56 F27 disposition:** binary refused by name (`NUMSTAT_BINARY`), not read as a count. Receipts apex claims, not corpus filings. Uses `splitlines()` (S1 class). |
| 2 | `kama-shokunin/tools/append-only-audit.py` (`2b9285bf`) | `def numstat` `:465–473` | deletions per path per commit; `--numstat -z`, `-` → `None` (binary recorded as `binary_changes`) | Same unit+grammar; binary skipped/recorded, not refused. Append-only claim. |
| 3 | `kama-shokunin/tools/round47-append-audit-v2-check.py` (`a180ab84`) | `def numstat` `:189–197` | deletions per path; `--numstat` (no `-z`), `parts[1].isdigit()` gate | Binary dropped silently (non-digit), same grammar. |
| 4 | `kama-shokunin/tools/round48-append-audit-v3-check.py` (`92b0f9f1`) | `:324–334` | deletions per path; `--numstat -z`, `parts[1].isdigit()` gate | Binary dropped silently; compares hunk positions to numstat. |
| 5 | `kama-shokunin/tools/round50-append-audit-v5-check.py` (`925f07a4`) | `:472–476` | one numstat record; `.split("\t")`, `ns[1].isdigit()` vs event `deleted` | Binary fails the digit gate (refused by the comparison, unnamed). |
| 6 | `kama-shokunin/tools/round51-append-audit-v6-check.py` (`254e63ba`) | `:306–311` | deletions per path; `--numstat -z`, `parts[1] in ("-","0")` skip | Binary skipped silently. |
| 7 | `kama-shokunin/tools/round52-append-restore-check.py` (`29dfd886`) | `:263–268` | deletions per path; `--numstat -z`, `parts[1] in ("-","0")` skip | Binary skipped silently. |

**Grammar-level, not counted (different unit path or non-instrument config):**
`kaidoku-shokunin/tools/round-43/c2-score-r43.py:170–194` asserts the exact numstat string for
`corpus/SOURCES.md` (`3\t0\tcorpus/SOURCES.md`); C1's monitored deletion set is the record TSV,
`SCORECARD.md`, `census/round-51/preregistration.txt`, `LOG.md`, `corpus/README.md` — `corpus/SOURCES.md`
is not in it, so the unit path differs. `kaidoku-shokunin/tools/round-44/c2-rubric.json` only mentions
numstat. The `.pyc` files under kama `tools/__pycache__/` are build artifacts, not predicates.

**C2 overlaps: N = 0.** No sibling tool/test parses the text receipt grammar
`\s*#\s*([A-Za-z0-9_][A-Za-z0-9_]*)\s*=\s*(\S*)\s*` or the literal `RECEIPT_VERSION`
(non-souji hits: 0). The nearest analogues are JSON validators with a different unit/grammar and are
not overlaps: `tameshi-shokunin/tools/context-capture.py:196`, `:506` (`require_object` against a
frozenset of JSON keys), `kama-shokunin/tests/llamacpp-live/check-receipt.py` (JSON schema versions),
`kaidoku-shokunin/tools/round-40/score-receipt.sh:418–452` (JSON `receipt_version` + counter-key
collision bookkeeping), `kaidoku-shokunin/tools/round-48/record2.py:133` (JSON receipt lookup).
They refuse unknown *JSON object* keys by exact key-set schema, not `# KEY=VALUE` receipt lines; the
digit/underscore-initial-key and empty-value shapes are text-grammar artefacts and do not transpose.

**Finding-name collisions in siblings: 0** for `DELETIONS-UNREADABLE-BINARY`, `CORRECTION-FILE-BINARY`,
`PAIR-FILING-HIDDEN`, `UNFILED-SOURCES-ANNOTATION`, `RECEIPT-UNKNOWN-KEY` (Receipt R7). The behaviour
overlap is in the numstat predicate; the r56 finding *names* are souji-local.

**Structural near-overlaps deliberately not counted** (same mechanism family, different unit):
- HTML-comment region hiding over markdown prose: `chousa-shokunin/tools/research-gate.sh:820–860`
  tracks comment state with the *v4 loose* opener (`[[ $line == *'<!--'* ]]` anywhere on the line) —
  the exact over-hide shape souji F29 repaired, but its unit is section/heading assignment, not
  correction filing visibility. `tsukuroi-shokunin/tools/check-adjacency-overlap.py:178`,
  `check-boundary-contract.py:54`, `check-edit-contract.py:68`, `check-owed-statements-r29.py:152–153`
  strip/parse `<!-- ... -->` in their own decision/statement documents (different units).
  `chousa-shokunin/tools/capture-fetch.py:80` strips comments from captured HTML text.
- Correction-resolution model: chousa `stale-count-check.py` closes an earlier overstatement with a
  later `correction: … superseded by … line N` — same append-only intent as souji's R52/R53 filing,
  different token grammar and unit (counts). Not counted.

## 3. PTR and PAIR scope

The v5 pair scan is root-relative and reads only `PAIR_SITES = ['LOG.md', 'corpus/README.md']`
(`c1-counter.py:162`), via `git show <rev>:<path>` (`:442–447`). Its PTR exemption skips a line whose
pair is quoted alongside a path-like `file.ext:NN` token (`PTR_RE`, `:160`, `:450`). Example live in
souji: `LOG.md:2578` quotes `"corpus/SOURCES.md 274 -> 275 rows"` but names `LOG.md:2527`, so PTR
exempts it (the correction line is not re-read as an annotation).

**Sibling LOG-style pair filings invisible to the scan: 27 predicate-matching lines in 14 lanes.**
Measured with the exact v5 predicate (line contains the literal `corpus/SOURCES.md`, PTR does not
match, `PAIR_ANNOT_RE = (\d+)\s*(?:->|→)\s*(\d+)(?:\s+rows?\b)?` matches). All are outside souji's
two pair-site files, so **none is a live souji surface**; souji's own sites hold 13 matching lines and
0 of them mention a sibling lane (so no cross-lane pair is currently quoted into the live surface).

| lane | file | lines (pair) |
|---|---|---|
| chousa | LOG.md | 827 (3->3) |
| game-dev-2d | LOG.md | 1353 (0->31) |
| kagi | LOG.md | 1001 (9->9) |
| kaidoku | LOG.md | 3190 (134->137), 3205 (137->139), 3268 (139->141), 3357 (141->142) |
| kake | LOG.md | 2459 (175->176) |
| kama | LOG.md | 2289 (8->8), 2427 (7->7) |
| kasegi | LOG.md | 1667 (18->19), 1745 (62->63), 1790 (24->25), 1905 (66->68), 2570 (27->35) |
| kotoba | LOG.md | 2322 (1->0), 2325 (11->15), 2352 (15->21), 2371 (0->20), 2928 (176->177) |
| kumitate | corpus/README.md | 94 (6->7), 96 (2->2) |
| mori | LOG.md | 3262 (344->346) |
| revenger | LOG.md | 1007 (51->53) |
| tabi | LOG.md | 487 (8->9) |
| tameshi | LOG.md | 1880 (98->99) |
| tsukuroi | LOG.md | 389 (8->9) |

Fleet root: `LOG.md` has 0 predicate-matching lines; `SCORECARD.md` has 1 (line 27, a table cell
`20 -> 24` next to `corpus/SOURCES.md`), but `SCORECARD.md` is not a `PAIR_SITE` and the scan runs at
the souji lane root. Even a `--root` at the fleet root would read the fleet `LOG.md`, never a sibling
lane's `LOG.md`, so sibling filings are unreachable by construction, not merely by revision.

**Scope risk (named, not a r56 claim defect).** The predicate is shape-only: 7 of the 27 pairs are
same-value, non-registry pairs (`3->3`, `9->9`, `8->8`, `7->7`, `2->2`, `1->0`, `0->31`), so a
cross-lane invocation would treat most of them as candidate annotations. Conversely, if a sibling
pair were ever quoted into souji's `LOG.md`/`corpus/README.md` without a `file.ext:NN` pointer, v5
would audit it as a souji annotation and likely emit `UNFILED-SOURCES-ANNOTATION`; with a pointer it
is PTR-exempt. Neither state exists at the measured revision.

## Connector synthesis (one bounded move)

- **Evidence.** Seven sibling instruments parse the same `git diff --numstat` unit with the same
  three-column/`-` grammar as C1's F27 surface; one of them (kaidoku round-61) already refuses binary
  by name, and one (kaidoku round-62/63 family; r61 itself) carries the S1 `splitlines()` line model
  on the same record type. C2's receipt-key surface has no sibling overlap (0).
- **Affected axes.** calibration 7 (claim scoping only), coverage 8 (unchanged — C2 has no overlap).
  No axis is harmed: nothing here falsifies T1–T8/T1–T7 or edits frozen bytes.
- **Proposed move (bounded, no claim change).** In the r56 report/lesson (never in the prereg,
  counters, fixtures, expected TSVs or a post-freeze claim receipt), record F27 as a **lane-local
  naming closure**, not a fleet-first name: `DELETIONS-UNREADABLE-BINARY` names souji's r55
  mislabel, while the binary-numstat refusal already exists as `NUMSTAT_BINARY` in kaidoku round-61
  and six kama append-only instruments parse the same grammar. Route one r57 item: decide whether the
  numstat binary/LF-only predicate becomes a shared helper or stays duplicated per lane.
- **Risks.** (i) Any prose added to a receipt could be read as a post-freeze claim amendment —
  keep it in the round report/lessons, append-only; (ii) "fleet-first" is not claimed by r56, so the
  note is a scope disclosure, not a defect admission; (iii) a shared helper would cross lane bounds —
  the r57 item is advisory only.
- **Verification.** Re-run the claim receipts unchanged (C1 T1–T8, C2 T1–T7); confirm the 7 file
  hashes above still match their lane HEADs; confirm `RECEIPT_VERSION`/`R5x-CORRECTION` remain
  souji-only; confirm the 27 sibling pair lines stay outside the two `PAIR_SITES`.

VERDICT: OVERLAP-FOUND

## Receipts

### R1 — frozen pins (measured revision bytes)
```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin
$ sha256sum census/round-56/{c1-counter.py,c2-counter.py,fixtures/build-fixtures.py,fixtures/run-matrix.sh,records/c1-selftest-expected.tsv,records/c2-selftest-expected.tsv} census/round-55/{c1-counter.py,c2-counter.py}
975d35201075b71affcd106b46341c7300e87e200b04c6c44864d636bcbbf179  census/round-56/c1-counter.py
5608201124fa4df9f378a95dda6472077bca249bf8bdf51a4a24e0d59c259cb8  census/round-56/c2-counter.py
2f26d6aa68ce44cfd9e4afdeaa4ef04837db7622c5ed5213429d8bda1c30b85a  census/round-56/fixtures/build-fixtures.py
a7e1a8924b9e3fd636f9882e368306faad8908638677e83fa395878211962de3  census/round-56/fixtures/run-matrix.sh
48a7cc0e869773b493b0b5f01446f70b9016595f1c307602912317aa3f7c5bfb  census/round-56/records/c1-selftest-expected.tsv
90517c4d4c6b7542229d1df85287bbfdf3fef631e2e18e279ad62c4c926841b3  census/round-56/records/c2-selftest-expected.tsv
944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2  census/round-55/c1-counter.py
e4eb34e6375d16a8c7a8842ac43ef26f262167d85eb4615c1ab07e1c994a568c  census/round-55/c2-counter.py
$ for f in census/round-56/c1-counter.py census/round-56/c2-counter.py; do git show cce21b555a617cadda782613ec1e9d3a0c12ac83:"$f" | sha256sum; done
975d35201075b71affcd106b46341c7300e87e200b04c6c44864d636bcbbf179  -
5608201124fa4df9f378a95dda6472077bca249bf8bdf51a4a24e0d59c259cb8  -
EXIT=0
```

### R2 — sibling bytes pinned at lane HEAD (read-only `git show`)
```
$ cd /home/vgpnk/Projects/shokunin
$ for lane/rev/file ...; do work=$(sha256sum "$lane/$f"); head=$(git -C "$lane" show "$rev:$f" | sha256sum); [ "$work" = "$head" ] && eq=clean_at_HEAD || eq=DIFFERS; done
kaidoku-shokunin/tools/round-59/annotation-audit.py  ba9ccbb9e0d803eb  clean_at_HEAD  a35e514105234515e266440aa33a578536b0007b
kaidoku-shokunin/tools/round-61/numstat-edge-audit.py 6b967e20e8f717ca  clean_at_HEAD  a35e514105234515e266440aa33a578536b0007b
kaidoku-shokunin/tools/round-43/c2-score-r43.py      459cbccbb2bf1723  clean_at_HEAD  a35e514105234515e266440aa33a578536b0007b
kaidoku-shokunin/tools/round-62/base-binding-sweep.py 18273023dbfaedba  clean_at_HEAD  a35e514105234515e266440aa33a578536b0007b
kaidoku-shokunin/tools/round-63/edge-numstat-sweep.py 0e67bd4527282271  clean_at_HEAD  a35e514105234515e266440aa33a578536b0007b
chousa-shokunin/corpus/evidence/round50/stale-count-check.py 4273436ac915ab47 clean_at_HEAD f748abbb6bf58388e732facd4ecec5612419c457
chousa-shokunin/tools/research-gate.sh                d5d48128509f77ed  clean_at_HEAD  f748abbb6bf58388e732facd4ecec5612419c457
chousa-shokunin/tools/capture-fetch.py                adf2c79d1c4f8ee8  clean_at_HEAD  f748abbb6bf58388e732facd4ecec5612419c457
kama-shokunin/tools/append-only-audit.py              2b9285bfdeeeeda4  clean_at_HEAD  6035e952c2521999e192d6f236331f265ac98392
kama-shokunin/tools/round47-append-audit-v2-check.py  a180ab84cc642731  clean_at_HEAD  6035e952c2521999e192d6f236331f265ac98392
kama-shokunin/tools/round48-append-audit-v3-check.py  92b0f9f1027b8214  clean_at_HEAD  6035e952c2521999e192d6f236331f265ac98392
EXIT=0
```

### R3 — sibling pair filings under the exact v5 pair predicate
```
$ cd /home/vgpnk/Projects/shokunin && python3 - <<'PY'
$ PAIR = re.compile(r'(\d+)\s*(?:->|→)\s*(\d+)(?:\s+rows?\b)?')
$ PTR  = re.compile(r'(?:[A-Za-z0-9_.\-]+/)*[A-Za-z0-9_.\-]+\.[A-Za-z0-9]{1,5}:\d')
$ for each sibling lane, rel in ('LOG.md','corpus/README.md'):
$   if 'corpus/SOURCES.md' not in ln or PTR.search(ln): continue
SIBLING_TOTAL 27
lane/file/line/pair rows: chousa/LOG.md:827 3->3; game-dev-2d/LOG.md:1353 0->31; kagi/LOG.md:1001 9->9;
kaidoku/LOG.md:3190 134->137, :3205 137->139, :3268 139->141, :3357 141->142; kake/LOG.md:2459 175->176;
kama/LOG.md:2289 8->8, :2427 7->7; kasegi/LOG.md:1667 18->19, :1745 62->63, :1790 24->25, :1905 66->68,
:2570 27->35; kotoba/LOG.md:2322 1->0, :2325 11->15, :2352 15->21, :2371 0->20, :2928 176->177;
kumitate/corpus/README.md:94 6->7, :96 2->2; mori/LOG.md:3262 344->346; revenger/LOG.md:1007 51->53;
tabi/LOG.md:487 8->9; tameshi/LOG.md:1880 98->99; tsukuroi/LOG.md:389 8->9
SOUJI_PAIR_ROWS 13 (LOG.md 1801/1804/1817/1845/1858/1898/1932/2527/2563, corpus/README.md 809/815/870/879)
LANE_MENTION_COUNT 0
fleet LOG.md PAIR_ROWS 0; fleet SCORECARD.md PAIR_ROWS 1 (line 27) but SCORECARD.md is not a PAIR_SITE
EXIT=0
```

### R4 — S1 liveness: splitlines vs LF on the tools' committed inputs
```
$ python3 - <<'PY'  # decode(errors="replace"); len(text.splitlines()) vs text.count("\n")
kaidoku .ufo/waves/round-58/l1/scores/c1-after.txt        splitlines=43  LF=43  equal=True
kaidoku .ufo/waves/round-58/l1/scores/c1-before.txt       splitlines=25  LF=25  equal=True
kaidoku .ufo/waves/round-59/l1/scores/d581-correction.txt splitlines=27  LF=27  equal=True
chousa/LOG.md                                              splitlines=2139 LF=2139 equal=True
chousa/corpus/README.md                                    splitlines=1353 LF=1353 equal=True
chousa/corpus/QUALITY.md                                   splitlines=1016 LF=1016 equal=True
chousa/corpus/lessons/round-49.md                           splitlines=220  LF=220  equal=True
chousa/corpus/evidence/round49/spans.tsv                    splitlines=32   LF=32   equal=True
$ LC_ALL=C grep -cP '[\x0b\x0c]' / grep -c $'\xc2\x85' over the same set
0 hits in every listed file (no VT/FF/NEL)
EXIT=0
```

### R5 — S1 arithmetic demonstration (generic Python; no sibling tool executed)
```
$ python3 - <<'PY'
samples: 'a\nb\n' splitlines=2 LF=2; 'a\x0cb\n' splitlines=2 LF=1; 'a\x0bb\n' splitlines=2 LF=1;
         'a\x85b\n' splitlines=2 LF=1; 'a\x00b\n' splitlines=1 LF=1   # NUL is not a boundary
chousa shape: text = 'x\n'*98 + '\x0c' + 'z\n'
  splitlines()[99] = 'z'      # a name 'line 100' resolves here
  LF line 100      = ''       # ... but the committed LF/git line 100 is the FF-bearing line/tail
EXIT=0
```

### R6 — overlap population and finding-name collisions
```
$ grep -rlE '<!--|CORRECTION|R52-CORRECTION|receipt|RECEIPT_VERSION|hidden_lines|numstat' --include='*.py' --include='*.sh' *-shokunin/tools *-shokunin/tests | wc -l
505 total (souji 195; non-souji 310)
$ grep -rl -- '--numstat' --include='*.py' --include='*.sh' *-shokunin/tools *-shokunin/tests
kaidoku-shokunin/tools/round-43/c2-score-r43.py
kaidoku-shokunin/tools/round-44/c2-rubric.json
kaidoku-shokunin/tools/round-61/numstat-edge-audit.py
kama-shokunin/tools/append-only-audit.py
kama-shokunin/tools/round47-append-audit-v2-check.py
kama-shokunin/tools/round48-append-audit-v3-check.py
kama-shokunin/tools/round50-append-audit-v5-check.py
kama-shokunin/tools/round51-append-audit-v6-check.py
kama-shokunin/tools/round52-append-restore-check.py
(+ kama tools/__pycache__/*.pyc build artifacts)
$ for n in DELETIONS-UNREADABLE-BINARY CORRECTION-FILE-BINARY PAIR-FILING-HIDDEN UNFILED-SOURCES-ANNOTATION RECEIPT-UNKNOWN-KEY; do grep -rl ... | grep -vc '^souji-shokunin/'; done
0 0 0 0 0
$ grep -rn 'RECEIPT_VERSION' --include='*.py' --include='*.sh' *-shokunin/tools *-shokunin/tests | grep -v '^souji-shokunin/'
(no output)
EXIT=0
```

### R7 — C1 constants and F27 claim row at the measured revision
```
$ grep -nE '^(ANCHOR|RECORD|SITES|CORR_FILE|ZONE|REG_ROW_RE|PAIR_SITES)' census/round-56/c1-counter.py
151:ANCHOR = 'grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv'
152:RECORD = 'census/round-51/records/ws-drift-vs-r46.tsv'
153:SITES = ['SCORECARD.md', 'census/round-51/preregistration.txt']
154:CORR_FILE = 'SCORECARD.md'
155:ZONE = 32
161:REG_ROW_RE = re.compile(r'^\|[ \t]*S[0-9]{3,}[ \t]*\|', re.M)
162:PAIR_SITES = ['LOG.md', 'corpus/README.md']
$ grep -n 'F27' census/round-56/records/c1-selftest-expected.tsv
32:F27-BINARY-NUMSTAT	1	DELETIONS-UNREADABLE-BINARY
EXIT=0
```
