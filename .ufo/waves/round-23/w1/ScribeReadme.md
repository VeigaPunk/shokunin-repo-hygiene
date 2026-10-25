STATUS: PASS

# ScribeReadme — `corpus/README.md` corrections for round 23 (wave 1)

Seat: L1Souji23.ScribeReadme (scribe). Item: draft the `corpus/README.md` corrections for round 23.
Deliverable: this report. **This seat did not edit `corpus/README.md`.** It was 446 lines and clean at
the base revision (E6); **another seat edited it in the working tree at 05:16:27 while this report was
being written** (449 lines, ` M`), and that intermediate edit still fails the frozen K3 predicate —
two mismatching pairs remain at `:443` (E10, Finding 11). §A therefore gives the replacement for the
**current working-tree bytes**, and records the base-revision bytes for audit.

Measured revision: lane base `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`.

## 0. What L1 applies — two operations, in this order

| op | location | content |
|---|---|---|
| **A** | in place, `corpus/README.md:439-445` in the current working tree (`:439-442` at base `1208bfb`) | replace the r22 slice-tally sentence **and** its r23 correction note with the receipt's tally stated in words (§A below) |
| **B** | append at EOF, after the last line | the `## Round 23 — …` block verbatim (§B below) |

**Why A is in place and not append-only.** The frozen C1/K3 predicate scans *every*
`<n> <class>` pair in the file at `--rev` and requires each to equal the receipt's tally
(`tools/souji-record-agreement.py:52-59`, `TALLY_RE = (\d+) (accepted|present|unverifiable|refused)`).
An appended correction cannot neutralise a filed wrong pair, because the filed pair is still scanned.
`README.md` is an index, not a filed log — `LOG.md` is the append-only record and keeps its bytes
(K2's `superseded by` marker). So: repair README where it is wrong, and record the sweep in §B's
`### Round 23 corrections` block so the repair is auditable. This is a deliberate departure from
README's own "sections above stand, corrections below" convention and is disclosed in that block.

**Constraint L1 must respect when applying §B:** the frozen pattern matches a digit, exactly one
space, then a class word. §B therefore quotes the receipt's tally (all four pairs correct) and
describes the superseded figures **in words**. Do not re-introduce a superseded figure as
`<digit> <class>` anywhere in `corpus/README.md` — that would itself be a K3 mismatch.

## A. In-place replacement (`corpus/README.md:439-445`, current working tree)

**A1 — before (current working-tree bytes, verbatim; 449-line file):**

```
The lane's absent-defect register slice (8 rows) now carries a verdict each —
5 accepted with corrected quotes, 2 present, 0 refused, 1 unverifiable
(unreachable DOI). Verdict table:
`../census/round-22/attempt2/slice-verdicts.tsv`. (Corrected in round 23: this
sentence said "1 present, 1 refused (wrong-source citation)" until r23; the
receipt above is the authority and the correction is recorded in `../LOG.md`
`Round22 attempt2 corrections`.)
```

This state fixes the live sentence (four correct pairs at `:440`) but the correction note at `:443`
re-quotes both superseded figures, so K3 still reports two mismatches (E10). The note is the defect
now, not the sentence.

**A2 — after (replacement bytes):**

```
The lane's absent-defect register slice (8 rows) now carries a verdict each —
5 accepted with corrected quotes (four of them wrong-source citations repaired
by re-citing, not refusals), 2 present, 1 unverifiable (unreachable DOI),
0 refused. Verdict table:
`../census/round-22/attempt2/slice-verdicts.tsv`. (Corrected in round 23: the
filed sentence reported one present and one refused; the receipt above is the
authority and the correction is recorded in `../LOG.md` `Round22 attempt2
corrections`. The superseded figures are not restated here because every
digit-plus-class pair in this file is measured against the receipt.)
```

**A3 — the base-revision bytes this replaces** (committed at `1208bfb`, `:439-442`, for audit only —
do not apply to the working tree, whose line numbers have shifted):

```
The lane's absent-defect register slice (8 rows) now carries a verdict each —
5 accepted with corrected quotes, 1 present, 1 refused (wrong-source
citation), 1 unverifiable (unreachable DOI). Verdict table:
`../census/round-22/attempt2/slice-verdicts.tsv`.
```

The replacement removes every disagreeing pair and leaves exactly four, each equal to the receipt:
`5 accepted`, `2 present`, `1 unverifiable`, `0 refused`. It also corrects the class-boundary
misreading that produced the defect: the four genuine wrong-source citations (S123, S124, S131,
S133) are `accepted` — repairable re-cites — because `refused` means the span is in *no* reachable
document (`lessons/round-22.md:357-359`). The superseded figures survive as *words* ("one present
and one refused") so the repair is still readable in place without becoming a measured pair.

## B. Appended block (verbatim, for `corpus/README.md` EOF)

```markdown
## Round 23 — record agreement, blob-bound receipts, F2 size-census read side

Three claims, none of which moves an axis by bookkeeping alone. C1 (calibration) lands an
instrument that re-derives the four routed r22 bookkeeping defects from committed bytes; C2
(operability) makes a receipt bind the tool blob it was measured with; C3 (coverage) assimilates
one theme on F2, the lane's only frontier row that held no entry. Inbound:
`lessons/round-22-verifier-spotcheck.md` §6 (D1–D8). D1/D2/D3 are repaired by the C1/C2 receipts,
D5 append-only in `LOG.md`, D4 in this file (below), D6–D8 in the lesson and the gate registry.
Nothing here is an admission: certification OFF, K5 HELD, F5 reap and NAMESPACE_SHA256 holds
unchanged. Evidence lands under `../census/round-23/`; the wave specification, dispatch and seat
reports under `../.ufo/waves/round-23/`; measurements are recorded in `lessons/round-23.md`.

| ground | status | entries / runnable evidence |
|---|---|---|
| C1 record agreement (calibration) | instrument landed, outside admission pending: `<R23-C1-COUNTS>` at `<full40>`; the do-nothing control at the base revision reports a nonzero mismatch count | `../tools/souji-record-agreement.py`; `../tests/fixtures/r23-record-agreement.py`; `../census/round-23/records/agreement-control-base.tsv`; `../census/round-23/records/declared-evidence-after.tsv`; `lessons/round-23.md` |
| C2 blob-bound receipts (operability) | runner + verifier landed, outside admission pending: `<R23-C2-RECEIPTS>` receipts carry a `tool_sha256` bound to the committed blob at their named revision and each pass `verify`; a receipt carrying the stale r22 tool digest is refused with `RECEIPT-TOOL-DIGEST-MISMATCH` | `../tools/souji-receipt-run.py`; the bound receipts under `../census/round-23/records/`; `lessons/round-23.md` |
| F2 repository size census | frontier, entries admitted for the read-only size/reachability instruments and the community reading of `garbage` (round-23 admission pending the non-author closure); wider size attribution, including `alternate` object databases, remains frontier | `knowledge/repo-size-census-readonly.md` (S115–S117); `knowledge/count-objects-garbage-readings-r25.md` (S118/S119, tier B); `knowledge/git-repo-structure-readonly.md` (S035–S037, reachable graph only); `../tools/souji-repo-structure.sh`; `../tests/fixtures/r13-repo-structure.sh`; `../census/round-13/verification.json`; `../census/round-23/sources/` |
| SOURCES registry (C3 id re-pointing) | gate change, outside admission pending: registry rows 114 → `<R23-REGISTRY>`, 0 malformed, 0 duplicate ids; staged ids that collide with existing rows are re-pointed by document, never appended as staged | `corpus/SOURCES.md`; `../census/round-23/sources/`; `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` exit 0 |

### Frontier (r23)

- F2 — next: the `/var/tmp` write-safety fixture itself, which no file yet supplies — the r23
  entry names the hazard (`git fsck --lost-found` materialises blob contents under
  `.git/lost-found/`) and states the fixture is still owed; then a colocated/plain byte-comparison
  before any `git repo structure` baseline (r17 `:233`, still unrun), and a fleet `garbage`/size
  measurement this lane can bind to its own receipt. The community reading adopted here is not that
  measurement.
- F1, F3, F4, F5 — unchanged. F5 reap and NAMESPACE_SHA256 stay HELD.

### Round 23 corrections

- **r22 slice tally (D4), this file, repaired in place** (`:439-442` at the base revision; `:439-445`
  in the working tree after an intermediate r23 edit whose own correction note re-stated the
  superseded figures and is replaced by the same repair). The filed sentence reported one present and
  one refused; `../census/round-22/attempt2/slice-verdicts.tsv` is the authority and
  holds 5 accepted, 2 present, 1 unverifiable, 0 refused. The superseded figures are not reproduced
  here on purpose: every digit-plus-class pair in this file is the K3 measurement surface, so
  quoting a superseded pair would itself be a mismatch. The sentence now states the receipt's
  figures and records that the wrong-source rows are repaired re-cites, not refusals.
- **Occurrence sweep — every mention in this file.** `:439` the register-slice row count, agrees
  with the receipt's 8 rows. `:440` the accepted figure, agreed and unchanged. `:440` the present
  and refused figures, the two that disagreed, repaired. `:441` the unverifiable figure, agreed and
  unchanged. `:427` "(2/2 entries, 8/8 register-slice verdicts)", the gate checker's entry and
  verdict counts rather than a class tally; agrees and is unchanged. `lessons/round-22.md:348-355`
  states the same classification in bolded prose and agrees with the receipt; its bare
  `0 refused` is the only pair the frozen pattern can see there. `LOG.md:1508-1510` repeats the
  superseded tally and is corrected append-only by this round's LOG entry — `LOG.md` is a filed log
  and keeps its bytes.
- **F2 rows superseded for the entry cell.** The r12 row (`:40`, "frontier, no entry") has been
  stale since r13 and is superseded here; the r13 row (`:68`) keeps its bounded structure-census
  capability and its pointers, and its entry cell is superseded by the r23 row above. The F2
  next-step at `:47` is superseded by `### Frontier (r23)`. The r17 colocated-repo caveat (`:217`)
  and its colocated/plain precondition (`:233`) stand unchanged and are still owed.
```

## Placeholders — every one, in order of first use

| placeholder | section | what L1 fills in |
|---|---|---|
| `<R23-C1-COUNTS>` | Round 23 table, C1 row | the counter's counts line `keys=… records=… occurrences=… mismatches=…` from `python3 tools/souji-record-agreement.py --rev <full40> --root .`, plus its exit status |
| `<full40>` | Round 23 table, C1 row | the full 40-hex landing revision the counter was run at (preregistration metavariable) |
| `<R23-C2-RECEIPTS>` | Round 23 table, C2 row | the number of receipts carrying a `tool_sha256=` line (`grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ \| wc -l`), prereg target ≥4 |
| `<R23-REGISTRY>` | Round 23 table, SOURCES-registry row | the registry row count after the C3 rows land, `114 → N`, with the adopted id range (prereg: continuation from S115) |

No other placeholder appears in §B. Every path in §B was checked to exist at the base revision or
is a round-23 path the wave itself creates (E7).

## Occurrence sweep — every r22 slice-tally mention (D4)

Frozen pattern `(\d+) (accepted|present|unverifiable|refused)` (`tools/souji-record-agreement.py:59`),
run over both K3 records at the base revision (E2):

| record:line | pair(s) found | receipt value | verdict |
|---|---|---|---|
| `corpus/README.md:440` | `5 accepted` | 5 | agrees — unchanged |
| `corpus/README.md:440` | `1 present` | 2 | **disagrees — repaired by op A** |
| `corpus/README.md:440` | `1 refused` | 0 | **disagrees — repaired by op A** |
| `corpus/README.md:441` | `1 unverifiable` | 1 | agrees — unchanged |
| `corpus/lessons/round-22.md:355` | `0 refused` | 0 | agrees — no edit (out of this item's scope) |
| `corpus/README.md:427` | none — "(2/2 entries, 8/8 register-slice verdicts)" | gate-check 2/2, 8/8 | not a class tally; agrees — unchanged |
| `corpus/README.md:439` | none — "(8 rows)" | 8 receipt rows | not a class tally; agrees — unchanged |
| `corpus/lessons/round-22.md:348-355` | none — `5 **accepted**`, `2 **present**`, `1 **unverifiable**`, `**0 refused**` | 5/2/1/0 | bold markers break the frozen pattern; prose agrees with the receipt |

Adjacent, not this file: `LOG.md:1508-1510` carries the same two wrong pairs and is K2's record
(the LOG correction entry, append-only with `superseded by`). `corpus/lessons/round-22.md` needs no
edit for K3: its one visible pair agrees, and the class-presence check is global across the two
records, which `README.md` alone satisfies after op A.

## Evidence

E1 — receipt tally derived from committed bytes (`census/round-22/attempt2/slice-verdicts.tsv`,
8 rows):

```
$ awk -F'\t' '!/^#/{c[$2]++} END{for(k in c) print k, c[k]}' census/round-22/attempt2/slice-verdicts.tsv
accepted 5
present 2
unverifiable 1
$ grep -vc '^#' census/round-22/attempt2/slice-verdicts.tsv
8
```

`refused` is absent from the receipt, so `tally_of()` defaults it to 0
(`tools/souji-record-agreement.py:116-124`: `tally = {c: 0 for c in K3_CLASSES}`).

E2 — frozen pattern run over both K3 records:

```
corpus/README.md 4 [(440, '5 accepted'), (440, '1 present'), (440, '1 refused'), (441, '1 unverifiable')]
corpus/lessons/round-22.md 1 [(355, '0 refused')]
```

E3 — the predicate, read from the tool (`tools/souji-record-agreement.py:52-59`):

```
K3_RECORDS = ("corpus/README.md", "corpus/lessons/round-22.md")
K3_CLASSES = ("accepted", "present", "unverifiable", "refused")
TALLY_RE = re.compile(r"(\d+) (accepted|present|unverifiable|refused)")
```

`k3()` reports `tally-disagree` per occurrence and one `class-absent` row for the union of classes
(`:238-255`). It does **not** scan `LOG.md`; that is `k2()`, whose section bounds are
`^Round22 attempt2` … `^=====`.

E4 — F2 mentions in `corpus/README.md` (`grep -n 'F2'`): `:40` (r12 row), `:47` (r12 next-step),
`:64` (r13 section heading), `:68` (r13 row), `:77`, `:90`, `:108`, `:171` (prose), `:217` (r17
caveat row), `:233` (r17 F2 next-step), `:240` (r18 "not F2"), `:249`, `:282` (unchanged lists).
§B supersedes `:40`, `:47`, `:68` and leaves `:217`/`:233` standing; `:240`/`:249`/`:282` are not
F2 entry claims and need no change.

E5 — the r23 next-step's grounding: the staged entry states the write-safety fixture is owed —
`/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/repo-size-census-readonly.md`
§ What this does NOT establish: "that is exactly what a `/var/tmp` write-safety fixture would have
to establish and is still owed." `grep -rln 'lost-found' tests/ tools/` → no match: no fixture
exists. `corpus/knowledge/git-repo-structure-readonly.md:11` excludes "alternates" from its
no-change claim, which is why wider size attribution stays frontier.

E6 — lane state. At base `1208bfb`, `corpus/README.md` is 446 lines and absent from
`git status --porcelain` (12 paths then). **While this report was being written another seat modified
it** — `stat -c '%y %s'` → `2026-10-25 05:16:27.809029438 -0300`, 29506 B, 449 lines;
`git status --porcelain corpus/README.md` → ` M`; `git diff --stat` → `1 file changed, 6 insertions(+),
3 deletions(-)`.

E7 — pointer existence check (all `OK`): `census/round-13/verification.json`,
`tests/fixtures/r13-repo-structure.sh`, `tools/souji-repo-structure.sh`,
`census/round-22/attempt2/slice-verdicts.tsv`, `corpus/SOURCES.md`, `corpus/pointer-exemptions.tsv`.
`census/round-23/` and `census/round-23/sources/` do not exist yet (wave-created).
`corpus/knowledge/count-objects-garbage-readings-r25.md` does not exist yet (wave-created).

E8 — registry size and gate tool: `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`
→ 114; `tools/souji-gate-check.py` present (14269 B).

E9 — **simulation, not an execution of the tool.** Applying §A A2 to the current working-tree
`README.md` bytes in memory, appending the §B block, and re-running the frozen `TALLY_RE`/tally
comparison over both K3 records in that in-memory state:

```
occurrences: 10 disagreements: [] missing classes: []
```

Ten agreeing occurrences (four in the repaired sentence, five in §B's corrections block, one in the
lesson), every class present, no disagreement. This is the K3 predicate re-implemented over bytes;
`tools/souji-record-agreement.py` was not run — its K1 receipt
(`census/round-23/records/declared-evidence-after.tsv`) does not exist yet, so the counter cannot
reach `M==0` this wave, and K1/K2/K4 are other items' scope. The §B block's own pairs were checked
separately and are exactly `5 accepted`, `2 present`, `1 unverifiable`, `0 refused`, `0 refused`
(the last is the lesson citation inside the corrections block).

E10 — **the current working tree still fails K3** (frozen pattern, current bytes, no edit applied):

```
440 5 accepted OK
440 2 present OK
440 0 refused OK
440 1 unverifiable OK
443 1 present MISMATCH
443 1 refused MISMATCH
```

Two `tally-disagree` rows remain, both from the intermediate edit's correction note at `:443` that
quotes the superseded figures. §A A2 removes them; nothing else in the file mismatches.

Tool installs this run: none (no `pacman`, `uv`, `npx` or binary install was needed).

## Findings

1. **`corpus/README.md` has exactly one physical tally sentence.** At the base revision it spans
   `:439-442` and two of its four pairs disagree with the receipt (`1 present` vs 2, `1 refused` vs
   0) while two agree (`5 accepted`, `1 unverifiable`). In the current working tree it spans
   `:439-445`: the sentence is fixed, but the appended correction note at `:443` re-quotes both
   superseded figures, so the file still carries two mismatching pairs (E10, Finding 11). No third
   mention exists — the sweep in the table above is complete for the frozen pattern, and the two
   non-tally mentions (`:427`, `:439`) were checked and agree.
2. **The filed wrong pairs cannot be corrected append-only.** K3 scans every occurrence at `--rev`,
   so the repair must be in place (§A) while README's own convention says corrections go below.
   §B's `### Round 23 corrections` block discloses the departure and records the sweep, so the file
   remains auditable. `LOG.md` is different — K2 demands the filed occurrence survive and be named
   by a later `superseded by` line — so the two records are repaired differently on purpose.
3. **The corrections block must not quote superseded digits.** Any `README.md` text containing
   `<digit> <class>` is measured; restating the old figures would re-create the mismatch. §B states
   them in words and says why. L1 must not "improve" that into a quoted before/after table.
4. **`corpus/lessons/round-22.md:348-355` is invisible to the frozen pattern** because every class
   word is bolded (`5 **accepted**` …), except `**0 refused**`, whose `0 refused` still matches.
   It therefore contributes one agreeing occurrence and cannot supply class presence on its own;
   after op A `README.md` carries all four classes, which is what the global check needs.
5. **`LOG.md:1508-1510` repeats the same two wrong pairs** and is K2's record, not this file's.
   The LOG correction entry must name them with a later `superseded by` line and keep the filed
   bytes; that is ScribeLog's item (D5), not a README edit.
6. **F2 has five distinct statements in `corpus/README.md`** (`:40` row, `:47` next-step, `:68`
   row, `:217` caveat, `:233` next-step). The r12 row `:40` ("frontier, no entry") has been stale
   since r13 wrote its "supersedes the r12 F2 row" section at `:64`; §B supersedes it explicitly so
   the stale row is not left as a live claim beside the new one.
7. **The F2 next-step is not empty after the new entry.** The entry supplies the instrument reading,
   not the fixture: no `lost-found`-fencing fixture exists in `tests/` or `tools/`, the
   colocated/plain precondition (`:233`) is still unrun, and the lane holds no fleet `garbage`
   measurement of its own — the wave's second entry is explicitly forbidden from claiming one.
   §B's rewritten next-step names exactly those three remainders plus `alternate` attribution.
8. **Entry-name divergence inside the round (see Attack log A1).** The prereg's C3 counter names
   `corpus/knowledge/count-objects-garbage-semantics-r24.md`; the wave item that produces the entry
   names `corpus/knowledge/count-objects-garbage-readings-r25.md`. §B names the wave-item path and
   carries a fork note for L1 below. I did not edit the prereg.
9. **Integration forks L1 must resolve when applying §B** (all are "file exists" rules, per
   `README.md:1-2` "write the row when the file exists, not before"):
   - if `knowledge/count-objects-garbage-readings-r25.md` is refused at its gate, delete it from the
     F2 entry cell and from the SOURCES-registry row's id range, and append the refusal reason and
     flip to the F2 cell — the next-step's "community reading" clause then becomes owed work, not
     done work;
   - if the community rows land tier B as dispatched, `<R23-REGISTRY>` is the post-landing count
     with the adopted id range, not a projection;
   - if `census/round-23/sources/` is not populated at landing, drop that pointer rather than land a
     dangling one (the landing gate's `LG-DANGLING-PTR` applies at round ≥ 18).
10. **`corpus/pointer-exemptions.tsv` carries no `uncommitted:` rows** (`grep -c` → 0) while the
    working tree has 12 uncommitted paths, including both new round-23 tools
    (`tools/souji-record-agreement.py`, `tools/souji-receipt-run.py`, both `??`) and this report's
    directory. K4 will count every one of them at `--rev`; they must be committed (or exempted)
    before the C1 after-run, and this file must not be left untracked.
11. **The intermediate working-tree edit to `corpus/README.md` does not close D4.** Another seat
    replaced the sentence with the receipt's tally at 05:16:27 (`:439-445`) but appended a correction
    note that re-quotes the superseded figures — "said \"1 present, 1 refused (wrong-source
    citation)\"" at `:443` — which the frozen pattern measures as two `tally-disagree` rows (E10).
    K3 is not satisfied by fixing the sentence while restating the old figures anywhere in the file.
    §A A2 is the minimal repair: keep the four correct pairs, state the superseded figures in words,
    and say why they are not restated. This seat did not edit the file; L1 or the owning seat must
    apply A2 before the C1 after-run.

## Attack log

**A1 — C3's frozen counter names a path the wave will not produce.**
`.ufo/waves/round-23/preregistration.txt` (C3, "Counter (frozen)") runs
`python3 tools/souji-gate-check.py --entries corpus/knowledge/repo-size-census-readonly.md corpus/knowledge/count-objects-garbage-semantics-r24.md …`.
The wave item `ScribeEntryGarbage` (`.ufo/waves/round-23/w1-spec.json`) delivers
`corpus/knowledge/count-objects-garbage-readings-r25.md` and instructs that the entry "must NOT
claim" a fleet census and may take ids `S118`/`S119` only. So the frozen C3 command, as written,
would point gate-check at a file that does not exist once the entry lands under its dispatched name.
This is not a counter I may edit; recorded here as the required honest report. §B names the
dispatched path so the README row is not wrong either way, and Finding 9 makes the fork explicit.

**A2 — the K3 predicate is satisfiable only by an in-place edit, which contradicts README's stated
convention.** Recorded, not attacked: the predicate is coherent and gameable in neither direction
(it measures the file's own claims against a committed receipt and demands class presence), but it
does force `corpus/README.md` to stop being append-only for this class. If the lane wants README to
stay append-only, the predicate would have to scope to a marker-bearing paragraph as K2 does — a
counter change, so out of scope for this round and not proposed.

No other counter, target or key set was found ungameable-wrong. The tally itself is derived from the
receipt by the tool (`tally_of`), never from prose.

## Closing placeholder list

Every placeholder this deliverable carries, and nothing else: `<full40>`, `<R23-C1-COUNTS>`,
`<R23-C2-RECEIPTS>`, `<R23-REGISTRY>`. The table in *Placeholders* gives each one's location in §B
and the value L1 substitutes. No other angle-bracket metavariable appears inside the §B block; the
only bracketed text there besides these four is the literal path `/var/tmp`.
