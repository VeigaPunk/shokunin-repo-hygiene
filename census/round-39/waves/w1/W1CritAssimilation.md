# W1CritAssimilation — assimilation decision critique (round 39, wave 1)

STATUS: PARTIAL — the decision `Assimilation: none` is **correct on all three frozen claim
surfaces** (evidence below), but the package's own premise (`108` lane rows) is stale by 65 rows
(`173`), the r38 assimilation sentence names only two of the three frozen surfaces, and the
lesson's `## Gate` admits/rejects (S247–S249 + one reject) are §2b curation, not assimilation-set
verdicts. Three corrections to the none-line and one Gate sentence; nothing to adopt.

Read-only throughout: no byte was written under `/home/vgpnk/Projects/shokuknow`, no campaign tool
was run there, no lane file was edited, no git/jj mutation was issued. Scratch:
`/fast/scratch/hyaku/souji-r39/W1CritAssimilation` (removed at the end of this item; see §7).

---

## 1. What the package is, measured

```
$ cd /home/vgpnk/Projects/shokuknow/merge/souji && echo "knowledge_files=$(ls knowledge/corpus/knowledge | wc -l)" && echo "append_rows=$(grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' SOURCES.append.md)" && echo "lane_rows=$(grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md)"
knowledge_files=68
append_rows=134
lane_rows=173
```

Verdict **PASS**: the package's two headline counts hold (`MERGE-REPORT.md`: "proposed rows
accepted: **134**", "proposed knowledge entries: **68**").

The package's *lane* premise does not hold:

```
MERGE-REPORT.md: "- lane registry currently holds **108** rows; first staged id is **S109**"
measured:                173 lane rows, lane max id S249, staged ids S109–S242
```

Verdict **DEFECT (package doc, not lane bytes)**: the premise was true when built and is now stale
by 65 rows. Any adoption must renumber by document, and any report sentence that quotes `108` would
be a stale literal of exactly the R1/R13 class this round exists to close.

---

## 2. §10 id-collision guard, run read-only in scratch (current registry)

```
S=/fast/scratch/hyaku/souji-r39/W1CritAssimilation; mkdir -p "$S"
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md | grep -oE 'S[0-9]+' | sort > "$S/reg-ids"
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' /home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md | grep -oE 'S[0-9]+' | sort > "$S/staged-ids"
comm -12 "$S/reg-ids" "$S/staged-ids" > "$S/collisions"
```

Output:

```
reg=173 staged=134 collisions=58
lane_max=S249 staged_min=S109 staged_max=S242
S109 S110 S111 S112 S113 S114 S115 S116 S117 S118 S119 S120 S121 S122 S123
S124 S125 S126 S127 S128 S129 S130 S131 S132 S152 S210 S211 S212 S213 S214
S215 S216 S217 S218 S219 S220 S221 S222 S223 S224 S225 S226 S227 S228 S229
S230 S231 S232 S233 S234 S235 S236 S237 S238 S239 S240 S241 S242
```

Verdict **PASS for the guard / DEFECT for the package's implied premise**: 58 of the 134 staged ids
already name lane rows. The guard is not broken (it returns nonempty), so a future adoption is not
auto-refused — but it is not id-free either, and the r32/r33 precedent numbers (`38` at 146 ids,
`39` at 147 ids) are already superseded. The none-line must carry **173 / 134 / 58**, not `108`.

---

## 3. Surface 1 — citation auditing (C1 register arm; C2 `--rev`/`--register-rev` resolution)

```
$ cd /home/vgpnk/Projects/shokuknow/merge/souji && grep -rilE "rev-parse|gitrevisions|merge-base|cat-file|is-ancestor|receipt_rev" knowledge/corpus/knowledge SOURCES.append.md | wc -l
0
```

No staged entry and no staged row cites a revision-resolution page, and none uses the register's
`receipt_rev` vocabulary. The nearest word matches are the prune-durability entries' prose about a
*registration's* tip being "an ancestor of the remote's current default branch"
(`fleet-prune-upstream-confirmed-r31.md:17`, `prune-trigger-levers-r28.md:64`) — a fleet-census
subject, not a citation tool's resolution class.

A provenance-discipline screen also finds nothing usable:

```
$ grep -rilE 'provenance|located quote|citation discipline' knowledge/corpus/knowledge SOURCES.append.md | wc -l
7
```

All seven hits are about the *provenance of a GitLab/reclamation name* or of a BFG recipe, never
about a register row's commit-vs-receipt distinction.

**Structural fact that settles this surface.** The stranded schema cannot carry the claim's cells:

```
$ grep -m1 -E '^\| id ' SOURCES.append.md
| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
```

C1's register is an 8-column TSV built by `census/round-39/make-cells.py` from lane receipts
(`table = ["id\tfile\tanchor\texpected\tstale\treceipt\treceipt_rev\tcommit"]`), and
`census/round-39/c1-counter.py:137` keys on `["id","file","anchor","expected","stale","receipt","receipt_rev"]`
with `commit = parts[7]`. A staged SOURCES row has no receipt, receipt_rev or commit cell, so **no
staged row can ever become a C1 register row**; an adopted entry could at most ground a *source* a
register row cites, and the register rows cite lane receipts plus S247 (`gitrevisions(7)`).

Verdict **PASS — none**: nothing staged serves the citation-auditing surface.

## 4. Surface 2 — tool output envelope (C2 exit 0/1/2, `REFUSAL REV-UNRESOLVED`)

```
$ grep -rilE "exit status|exit code|argparse|sys\.exit" knowledge/corpus/knowledge SOURCES.append.md
knowledge/corpus/knowledge/duplicate-verdict-taxonomy-r24.md
knowledge/corpus/knowledge/duplicate-receipt-class-decision-r25.md
knowledge/corpus/knowledge/prune-lever-paths-r30.md
SOURCES.append.md
```

Strongest counterexample tested: `duplicate-verdict-taxonomy-r24.md` teaches a genuine three-valued
exit contract —

> "`cmp` is a byte-by-byte comparison with a three-valued exit status … 'Exit status is 0 if inputs
> are the same, 1 if different, 2 if trouble.'"

and `duplicate-receipt-class-decision-r25.md:49` adds "The 'trouble' exit status is currently
unrepresented". If anything staged could serve C2's could-not-evaluate class, it is this pair.
It does not, on the entry's own words:

> "`cmp`'s '2 if trouble' is the exit status of the *tool*, not a receipt class; a souji receipt
> would have to record that third outcome explicitly." (`duplicate-verdict-taxonomy-r24.md`, "What
> this does NOT establish")

and its "Lane link and consequence" says "F3's frontier item is an **operator decision**". Adopting
it to ground C2 would (a) substitute an oracle for a file comparison where C2 needs a citation
tool's refusal class, and (b) import the deferred duplicate-receipt-class ruling into a round whose
preregistration says "Not claimed … No receipt class, no deletion verdict, no certification:
deletion certification stays OFF and K5 HELD" — a new or widened target, which §10's frozen-round
clause forbids. `prune-lever-paths-r30.md`'s hit is a probe method line ("every case records the
task's exit status") and `SOURCES.append.md`'s are S136 (`cmp(1)`) and S194 (a measured probe), same
refusal.

The claim's real envelope sources are already lane-opened this round, from primary bytes:
S247 `gitrevisions(7)` `^{<type>}`, S248 `ast.get_docstring`, S249 argparse `exit_on_error`
(`corpus/SOURCES.md:20`, `corpus/lessons/round-39.md:39-41`). No staged row cites any of them:

```
$ grep -c "docs.python.org\|gitrevisions" SOURCES.append.md
0
$ grep -icE "gitrevisions|merge-base|rev-parse|cat-file" SOURCES.append.md
0
```

The three `python` hits in the append file (S124, S133, S141) are lane probe scripts, not CPython
docs.

Verdict **PASS — none**, with the caveat that the refusal reason must name the F3 import, not just
"no match".

## 5. Surface 3 — record-parser coverage (C3 M11–M14)

```
$ grep -rilE "CRLF|splitlines|trailing whitespace|indented|leading spaces" knowledge/corpus/knowledge SOURCES.append.md | wc -l
0
```

Strongest counterexample tested: the ten-entry `origin-record-*` / `quarantine-*` cluster — a record
*file* subject. It is F4's per-item trash origin record: "In `trash_item_get_trashinfo()`, line 158
builds it: `trashinfo = g_strdup_printf ("%s/info/%s.trashinfo", trashpath, basename);`" and "It has
exactly two keys, in one group" (`origin-record-format-gvfs-r26.md`); the closest generic sentence,
"the record file exists is not the same as the record's content is final"
(`origin-record-mechanism-set-r33.md`), is about GLib's exclusive-create/rename window, not about a
record row's grammar. C3's four mutants are `tools/souji-worktree-drift.py` rules over a TSV whose
comments are `#`-prefixed: `$`-anchored schema vs trailing whitespace (M11), `str.splitlines` vs CRLF
(M12), the `--root` containment guard (M13), leading-indent acceptance (M14). A GKeyFile with
`Path`/`DeletionDate` cannot discriminate any of the four; nothing staged mentions CRLF, indentation
or trailing whitespace at all.

Verdict **PASS — none**. Refusal reason: different artifact (trash origin record vs drift record
grammar) and different failure class (write atomicity vs parse rules); adopting it would be a new
target.

## 6. The decision text itself

Existing lines to measure the draft against:

- r38: "Assimilation: none this round — the `merge/souji/` package's staged entries do not touch
  citation auditing or a tool's output envelope, and adopting one would not serve a frozen claim"
  (`corpus/lessons/round-38.md:161`). **Only two surfaces** — copied verbatim, it leaves C3's
  record-parser surface unscreened.
- r33 (the strongest precedent): "Assimilation: none. Wave-1 `SwarmScout41` swept the read-only
  package … (12 hits, 0 admit candidates; …) and ran the prompt §10 id-collision check in scratch:
  147 registry ids, 134 staged ids, 39 collisions (S109-S132, S152, S210-S223). Nothing was appended
  from the package. considerthese/: absent in this lane." (`corpus/lessons/round-33.md:31`).
- r32 judged refusals per entry ("The 20 REJECT rows are judged per entry …") and carried the guard
  numbers (`corpus/lessons/round-32.md:49`).

```
$ ls -d /home/vgpnk/Projects/shokunin/souji-shokunin/considerthese
ls: cannot access 'considerthese': No such file or directory
$ ls /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/reports/
ls: cannot access '.ufo/reports/': No such file or directory
```

Verdicts: `considerthese/` absent — **PASS** (the report owes the one "absent" line). No report
exists yet, so no assimilation line has been written: the decision is being taken now and this seat
drafts it.

**Gate-sourcing risk (identity change).** The lesson's `## Gate` rows — S247/S248/S249 **admit** and
one **reject** (`ast.get_source_segment`, "returns the node's own span, which is the source-slicing
the r38 M5 finding forbids") — are §2b curation of sources the round itself opened, not verdicts on
the assimilation set. §10 asks the Gate for "≥1 admit and ≥1 reject *from the assimilation set*" for
the non-author spot-check; with `none` declared that clause is inert, and the report must say so,
or the spot-checker scores a §2b reject as an assimilation reject (false provenance).

---

## 7. Counterexample, evidence, axes, smallest safe correction

**Counterexample (the one I would have to concede).** `duplicate-verdict-taxonomy-r24.md` +
`duplicate-receipt-class-decision-r25.md` carry a documented three-valued exit contract with an
explicit "unrepresented third outcome" gap — structurally the same shape as C2's could-not-evaluate
class. It survives the intersect test only on *subject*: `cmp` is a comparison oracle, the entry
disclaims receipt-class use in its own "What this does NOT establish", and the class it points at
(F3 duplicate receipt) is explicitly outside this round's preregistration. If a future round claims
a receipt class, this pair becomes an admit candidate — flip condition, not a r39 defect.

**Evidence (all reproducible, in place):** 68 staged entries / 134 staged rows
(`MERGE-REPORT.md` and §1); 0 files on the citation surface and 0 on the parser surface; 4 files on
the envelope surface, all refused with quoted self-disclaimers; 58 id collisions at 173 live rows;
C1 register schema is 8-column and unreachable from an 11-column SOURCES row; the claims' own
sources are lane-opened live (S247–S249.

**Impacted axes:** calibration (a stale `108` literal in the report is the exact R1/R13 defect class
— C1's own subject); operability (an `cmp` row would mislabel C2's envelope ground); coverage (the
F4 trash-record cluster would mislabel C3's parser ground). None of the three is *improved* by
adopting anything this round, so `none` is the axis-neutral move; the only axis gain available is
honest evidence in the line.

**Smallest safe correction (for the L1, no new work beyond one paragraph):** paste the line below
into the round report's `Sources & frontier`, and add one Gate sentence: "*The S247–S249 admits and
the `ast.get_source_segment` reject are §2b curation of sources opened this round, not
assimilation-set verdicts; the package stays unadopted, its 108-row premise is stale (live registry
173), and the 58-collision guard goes to the next adoption round together with the package's two
dangling citations (`quarantine-origin-record-fields-r23/-r24` cite `S022`, absent from the package)
and its three sources the lane already holds (S143, S169, S170 `used-by` overlap rows).*"

Drafted line:

> **Assimilation: none.** The staged `merge/souji/` package (68 knowledge entries, 134 rows,
> `MERGE-REPORT.md`) has no intersection with any frozen claim. Citation auditing (C1's register
> arm, C2's `--rev`): `grep -rilE "rev-parse|gitrevisions|merge-base|cat-file|is-ancestor|receipt_rev"`
> over its knowledge files and `SOURCES.append.md` returns **0** files, and no staged 11-column
> SOURCES row can fill C1's 8-column register row (no `receipt`/`receipt_rev`/`commit` cell); the
> claim's source is the lane's own S247 `gitrevisions(7)`, opened 2026-10-28. Tool output envelope
> (C2): the only exit-status *contract* material is `cmp(1)`'s 0/1/2 oracle in
> `duplicate-verdict-taxonomy-r24.md`, which states in its own "What this does NOT establish" that
> "`cmp`'s '2 if trouble' is the exit status of the *tool*, not a receipt class" — adopting it would
> import the deferred F3 duplicate-receipt ruling, which this preregistration does not claim. Record-
> parser coverage (C3): `grep -rilE "CRLF|splitlines|trailing whitespace|indented|leading spaces"`
> returns **0** files; the `origin-record-*` cluster is F4's trash GKeyFile (`Path`/`DeletionDate`),
> not the drift tool's TSV grammar M11–M14 assert. Nothing was appended, so the §10 guard had nothing
> to append; run against the live registry it reads **173** lane ids vs **134** staged ids,
> **58** collisions (S109–S131, S152, S210–S242) — the package's "108 rows / first staged id S109"
> premise is stale by 65 rows. `considerthese/` is absent in this lane.

**Do not:** write into `/home/vgpnk/Projects/shokuknow`; record the S247–S249 verdicts as
assimilation admits; append any staged row this round; quote `108` as the current registry size.

**Scratch:** `/fast/scratch/hyaku/souji-r39/W1CritAssimilation` held only `reg-ids` (865 B),
`staged-ids` (670 B) and `collisions` (290 B), 1 825 B in total, and was removed after the outputs
above were captured; no staged repo or lane clone was created, nothing landed under `/tmp`, and no
tool was installed or upgraded.

**Verdict summary:** `Assimilation: none` — **correct**; evidence as of this seat: three-surface
screen (0 / 4-refused / 0), 58-collision guard, structural schema mismatch, and the claims' own
sources already opened lane-side. Fixes owed to the drafted text, not to the decision: name all
three surfaces, carry 173/134/58, and separate §2b Gate verdicts from assimilation verdicts.
