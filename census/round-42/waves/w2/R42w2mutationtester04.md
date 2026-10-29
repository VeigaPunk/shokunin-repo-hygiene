# R42w2mutationtester04 — mutation test of the landed r42 C1 lesson and register against the frozen C1 counter

Seat: `R42w2mutationtester04` (role: mutation-tester). Wave 2, round 42, souji lane.
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Tip under attack: `3105a63b23481fccf7df58e74d14a6681e0ea0c8`.
Counter attacked: `census/round-42/c1-counter.py` (frozen, sha256 `0ab07cd3c99e6bbe26220d9e36672b6a7acd45150b96fff1868d0e082dcd46aa`).
Scorer used: `census/round-42/score-candidate.sh c1` (frozen).

**What this attacks.** The landed C1 claim is "the 70 declared-evidence tokens are accounted for and the 5 genuinely wrong ones are
corrected". Its only two content surfaces are `corpus/lessons/round-42.md` (five `CORRECTION-DE` lines plus prose) and
`census/round-42/c1-register.tsv` (70 rows). This seat asks: **which single-point edits to those two surfaces leave the C1 target
met?** Wave 1's `N-C1a` states the counter "cannot tell substance from shape" (R42critic01 built 11 substantively wrong triples that
score at target). This seat measures that claim at field granularity, with 93 single-point edits, and refines it.

**Verdict.** The wave-1 claim `N-C1a` is **confirmed and sharpened**. Of 93 single-point edits, **33 leave the target met**
(counter exit 0) and 60 turn it red. The counter reads **every field it parses** and **no prose whatsoever**: 16 of the 33 survivors
are pure-prose edits that falsify the lesson's substance while the counter stays green; the other 17 are shape edits (fence style,
register row order, header content, decoy rows, CRLF in the lesson, an unbalanced trailing fence, leading zeros in `line=`). The
refinement over wave 1: **the split is not "substance vs shape" but "fields the counter parses vs everything else".** Every survivor
falls outside the counter's parse grammar; every edit *inside* that grammar is killed — with two exceptions where a field the counter
does parse is edited in a way the counter normalises away (`line=014` → `int("014") == 14`; a trailing space/tab after a
`CORRECTION-DE` line, which `CORR`'s `\s*$` tolerates).

---

## 1. Method

### 1.1 What was mutated

Two files, byte-copied from the tip and edited one point at a time:

| dest | tip sha256 | role |
|---|---|---|
| `corpus/lessons/round-42.md` | `4561dfc110a4f95f0663c8cc6596a1aab436daf6a9bf93ad961d2b5df0ae9586` | the 5 `CORRECTION-DE` lines + 200 lines of prose |
| `census/round-42/c1-register.tsv` | `c18274e5a6736afbd3eaac818bae304c76d3c03b87ef653a4581ee43811c2f17` | 1 header + 70 data rows |

### 1.2 Commands actually run

Every mutant was scored through the frozen harness, one clone per mutant, never the lane:

```
bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/score-candidate.sh c1 \
    /fast/scratch/hyaku/souji-r42/R42w2mutationtester04 \
    corpus/lessons/round-42.md=<mutant file> \
    census/round-42/c1-register.tsv=<mutant file>
```

For a lesson mutant the register argument is the pristine tip copy, and vice versa; each mutant therefore changes exactly one file.
The driver scripts are `gen.py`/`gen2.py`/`gen3.py`/`gen4.py` (mutation generators) and `score_all.sh` (the scorer loop), kept
outside the lane in the seat scratch and quoted below; the mutant bytes, the per-mutant `SUMMARY` receipts and the manifest are
copied into this seat's own directory:

- `.ufo/waves/round-42/w2/R42w2mutationtester04/mutants/` — 93 mutant files (`L*.md`, `R*.tsv`)
- `.ufo/waves/round-42/w2/R42w2mutationtester04/results/` — 93 `SUMMARY` receipts + `BASE.txt`
- `.ufo/waves/round-42/w2/R42w2mutationtester04/MANIFEST.tsv` — id → dest → description
- `.ufo/waves/round-42/w2/R42w2mutationtester04/TABLE.md` — the full table below, machine-written
- `.ufo/waves/round-42/w2/R42w2mutationtester04/pristine-lesson.md`, `pristine-register.tsv` — the tip bytes used as the untouched half of each pair

No file in the lane was written. Verification after the run:

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
3105a63b23481fccf7df58e74d14a6681e0ea0c8
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain | wc -l
0
$ sha256sum corpus/lessons/round-42.md census/round-42/c1-register.tsv
4561dfc110a4f95f0663c8cc6596a1aab436daf6a9bf93ad961d2b5df0ae9586  corpus/lessons/round-42.md
c18274e5a6736afbd3eaac818bae304c76d3c03b87ef653a4581ee43811c2f17  census/round-42/c1-register.tsv
$ git show 3105a63b…:corpus/lessons/round-42.md | sha256sum
4561dfc110a4f95f0663c8cc6596a1aab436daf6a9bf93ad961d2b5df0ae9586  -
$ git show 3105a63b…:census/round-42/c1-register.tsv | sha256sum
c18274e5a6736afbd3eaac818bae304c76d3c03b87ef653a4581ee43811c2f17  -
```

### 1.3 Baseline (the honest landed triple)

```
$ bash census/round-42/score-candidate.sh c1 /fast/scratch/hyaku/souji-r42/R42w2mutationtester04
SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0
baseline exit=0
```

(receipt: `results/BASE.txt`). The landed triple is green at the tip, so every red below is caused by the mutant, not by a broken
baseline.

---

## 2. Result table

`SUMMARY` is pasted verbatim from `results/<id>.txt`. "target met?" = the counter's exit code (`exit=0` green, `exit=1` red).
`BASE` = the unmutated tip.

| id | edit | SUMMARY | target met? |
|---|---|---|---|
| BASE | (none — the honest landed triple) | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | yes (exit 0) |
| L1 | delete the `line=14` CORRECTION-DE line | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| L2 | delete the first `line=68` CORRECTION-DE line | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| L3 | delete the second `line=68` CORRECTION-DE line | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| L4 | delete the `line=92` CORRECTION-DE line | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| L5 | delete the `line=175` CORRECTION-DE line | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| L6 | alter one char of the `token=` of the `line=14` correction (`65817d0d`→`65817d0e`) | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L7 | alter the `derived=` of the `line=14` correction (`rev-unresolved`→`path-absent`) | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L8 | alter one hex char of the `derived=sha256=` of the first `line=68` correction | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L9 | alter the `rev=` of the `line=14` correction to `0000…0` | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L10 | alter the `line=` of the `line=14` correction to `15` | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L11 | duplicate the `line=14` CORRECTION-DE line | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L12 | move the `line=14` correction inside a ```` ``` ```` fence | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L13 | move the `line=14` correction inside a `~~~` tilde fence | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L14 | move the `line=14` correction inside a four-backtick fence | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L15 | prose: "and 5 do not" → "and 6 do not" | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L16 | prose: falsify the file the `42259756…` digest is attributed to | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L17 | prose: change the `SCORECARD.md:14` heading to `:15` | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L18 | prose: rename the C1 corrections section heading | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L19 | prose: append a false "all 70 resolved, no correction needed" section | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L20 | convert the whole lesson to CRLF | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L21 | lower-case the marker (`Correction-DE`) | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| L22 | indent the `line=14` correction by one space | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L23 | append a trailing space to the `line=14` correction line | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L24 | prose: mention the literal `CORRECTION-DE` in a sentence | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L25 | move the `line=14` correction into the `## Mistakes` section | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L26 | append a trailing tab to the `line=14` correction line | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L27 | alter the `derived=` of the first `line=68` correction to `sha256=?` | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L28 | upper-case the `rev=` hex of the `line=14` correction | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L29 | double the space between two fields of the `line=14` correction | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L30 | delete the whole prose scope paragraph of the `line=14` section (correction kept) | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L31 | prose: falsify an attribution inside the `line=14` scope paragraph | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L32 | prose: falsify the scope sentence of the `line=175` correction | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L33 | delete the prose paragraph of the `line=175` section (correction kept) | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L34 | prose: "65 resolve" → "64 resolve" | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L35 | prose: remove a backtick pair in a prose sentence | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L36 | prose: falsify the reader agreement count (65 agree → 61 agree) | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L37 | prose: alter the base revision quoted in the lesson header | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L38 | prose: delete the sentence declaring what the correction lines are | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L39 | turn the first `line=68` correction into a markdown list item (`- `) | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L40 | prose: attribute the `71b89eb3…` digest to a different tool | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L41 | move the `line=175` correction to the top of the corrections section | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L42 | alter the `line=` of the `line=92` correction to `175` | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L43 | alter the `derived=` of the `line=175` correction (`path-absent`→`rev-unresolved`) | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L44 | alter the `token=` of the `line=92` correction | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L45 | delete the `## Corrections to filed statements (C1)` heading | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L46 | append a CORRECTION-DE line for the *resolved* item `line=21` | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L47 | append a comma to the `token=` of the `line=14` correction | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L48 | alter the `derived=sha256=` of the second `line=68` correction | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L49 | indent the `line=14` correction by four spaces | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L50 | join two CORRECTION-DE lines onto one physical line | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L51 | write the `line=` of the `line=14` correction with leading zeros (`014`) | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L53 | prefix the `line=14` correction with a `>` blockquote marker | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L54 | wrap the `line=14` correction in an HTML comment | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L55 | insert one unbalanced ` ``` ` fence **before** the corrections section | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=0 junk=5 rewritten=0 new_mismatches=0` | no (exit 1) |
| L56 | append one unbalanced ` ``` ` fence at the **end** of the lesson | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| L57 | spell the `derived=` of the `line=175` correction `path_absent` | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L58 | change the `rev=` of the `line=175` correction to the tip revision | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| L59 | change the `token=` of the `line=175` correction to a resolved item's token | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=4 junk=1 rewritten=0 new_mismatches=0` | no (exit 1) |
| R1 | register: class of the `line=14` row `unresolved`→`resolved` | `SUMMARY items=70 population=ok registered=70 class_ok=69 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R2 | register: `resolved_to` of the `line=14` row `-`→`census/round-42/c1-items.tsv` | `SUMMARY items=70 population=ok registered=70 class_ok=69 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R3 | register: one char of a `resolved_to` path (`round-28`→`round-29`) | `SUMMARY items=70 population=ok registered=70 class_ok=69 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R4 | register: delete the `line=14` row | `SUMMARY items=70 population=ok registered=69 class_ok=69 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R5 | register: delete one of the two identical rows of the duplicated key `667/c2-after2.txt` | `SUMMARY items=70 population=ok registered=68 class_ok=68 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R6 | register: duplicate the `line=21` row | `SUMMARY items=70 population=ok registered=69 class_ok=69 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R7 | register: rewrite the header row (`ln tok kind path`) | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| R8 | register: append a row for a key absent from the population | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| R9 | register: swap two rows (order change only) | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| R10 | register: convert the whole register to CRLF | `SUMMARY items=70 population=ok registered=70 class_ok=0 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R11 | register: append a trailing tab to a row (a 5th field) | `SUMMARY items=70 population=ok registered=69 class_ok=69 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R12 | register: change the `line=` of the `line=21` row to `22` | `SUMMARY items=70 population=ok registered=69 class_ok=69 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R13 | register: change the `token=` of the `line=21` row | `SUMMARY items=70 population=ok registered=69 class_ok=69 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R14 | register: class of the `line=21` row `resolved`→`unresolved` | `SUMMARY items=70 population=ok registered=70 class_ok=69 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R15 | register: remove the trailing newline | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| R16 | register: prefix a `resolved_to` path with `./` | `SUMMARY items=70 population=ok registered=70 class_ok=69 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R17 | register: insert a `#` comment line | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| R18 | register: insert a blank line | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| R19 | register: trailing space in the `class=` field | `SUMMARY items=70 population=ok registered=70 class_ok=69 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R20 | register: swap the `resolved_to` of the `line=21` and `line=22` rows | `SUMMARY items=70 population=ok registered=70 class_ok=68 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R21 | register: add a second row for the `line=14` key with a different class | `SUMMARY items=70 population=ok registered=69 class_ok=69 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R22 | register: relabel every `unresolved` row `resolved` | `SUMMARY items=70 population=ok registered=70 class_ok=65 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R23 | register: delete all five `unresolved` rows | `SUMMARY items=70 population=ok registered=65 class_ok=65 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R24 | register: upper-case the `class=` field (`UNRESOLVED`) | `SUMMARY items=70 population=ok registered=70 class_ok=69 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R25 | register: empty the `resolved_to` field of the `line=14` row | `SUMMARY items=70 population=ok registered=70 class_ok=69 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R26 | register: trailing space after a `resolved_to` path | `SUMMARY items=70 population=ok registered=70 class_ok=69 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R27 | register: point the `line=21` row at a different existing committed path | `SUMMARY items=70 population=ok registered=70 class_ok=69 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R28 | register: relabel the header to `a b c d` | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| R29 | register: append a duplicate of the last row (a key already duplicated) | `SUMMARY items=70 population=ok registered=69 class_ok=69 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R30 | register: `line=` of the `line=14` row with leading zeros (`014`) | `SUMMARY items=70 population=ok registered=69 class_ok=69 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R31 | register: upper-case the `token=` of the `line=14` row | `SUMMARY items=70 population=ok registered=69 class_ok=69 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R32 | register: trailing space in the `class=` of the `line=14` row (`unresolved `) | `SUMMARY items=70 population=ok registered=70 class_ok=69 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R33 | register: point one of the two duplicated `667/c2-after2.txt` rows at a different existing path | `SUMMARY items=70 population=ok registered=70 class_ok=68 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | no (exit 1) |
| R34 | register: append a decoy row with only two fields | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |
| R35 | register: append a four-field decoy row for a non-population key | `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0` | **yes (SURVIVOR)** |

**Survivor count: 33 of 93** (35.5%). Killed: 60.

---

## 3. The counter's blind spots, named

### 3.1 The refinement of wave 1's `N-C1a`

Wave 1 (`R42critic01`, N-C1a) wrote: *"the counter cannot tell substance from shape — 11 substantively wrong triples score at target"*.
The mutation survey shows the split is sharper and **not** substance-vs-shape. It is:

> **The counter reads exactly the grammar it parses, and nothing else. Every edit inside that grammar is killed; every edit outside it
> is free.**

Grammars the counter actually parses (`census/round-42/c1-counter.py`):

- **Lesson**: only lines containing the literal `CORRECTION-DE` (`:218`), of which the ones matching
  `CORR = ^CORRECTION-DE line=(\d+) token=(\S+) derived=(\S+) rev=([0-9a-f]{40})\s*$` (`:63`) are read; the four captured groups
  (`line=`, `token=`, `derived=`, `rev=`) are compared against the counter's own derivation; the line must be outside a fence,
  where a fence is a line whose `lstrip()` starts with ```` ``` ```` (`:219`).
- **Register**: only lines with exactly four tab-separated fields (`:192`), keyed by `(line, token)` (`:194`), and the `class` /
  `resolved_to` pair must equal the counter's own derivation, with the resolved path required to exist at the commit (`:212`).

Everything else in the two files — all prose, all headings, all row ordering, the header line, the row count beyond the 70 population
keys — is **never read**.

### 3.2 The 33 survivors, grouped

**(a) Prose is never read — 16 survivors.** L15, L16, L17, L18, L19, L30, L31, L32, L33, L34, L35, L36, L37, L38, L40, L45.
Every one of these leaves the target met while the lesson's *substance* is falsified:

- L34 changes the population accounting from "65 resolve … 5 do not" to "64 resolve … 5 do not" — the lesson now contradicts the
  register it documents.
- L36 changes the reader-verification figure from "65 agree, 0 disagree" to "61 agree, 4 disagree" — the round's compensation for
  N-C1a is restated as failing.
- L19 appends an outright false section: "All 70 items are resolved to committed paths and no correction is required."
- L16 / L40 attribute the `42259756…` and `71b89eb3…` digests to the wrong files and tools — the *scope* sentences the C1 claim
  depends on, falsified, with no red.
- L30 / L33 delete the "scope of the derived value" paragraphs entirely; the CORRECTION-DE lines remain, so `corrected=5` still
  holds while the lesson no longer states what the corrections mean (QUALITY Q101's scope requirement).
- L37 alters the base revision quoted in the lesson header.
- L45 deletes the `## Corrections to filed statements (C1)` heading, so the corrections sit under no section at all.

This is wave 1's `N1` (prose unread) and `N-C1a` confirmed at field granularity, and it is the direct answer to the round's own
C1 predicate: the predicate says the register accounts for the 70 and the lesson "carries one CORRECTION-DE line per unresolved item
**bound to the value the counter derives**" — but the counter never checks that the *lesson's prose* says what those lines mean.

**(b) The fence rule is ```` ``` ````-only, and its state is order-sensitive — 4 survivors.** L13 (a `~~~` fence — the counter does
not recognise it, so the correction inside still counts as corrected and the target stays met), L20 (the whole lesson in CRLF —
the counter splits on `\n` only), L23 (a trailing space after a CORRECTION-DE line — `CORR`'s `\s*$` swallows it), L26 (a trailing
tab — same), and L56 (one unbalanced ```` ``` ```` appended at the **end** of the lesson, after every correction: the fence flag is
toggled but never consulted again). The contrast with L55 is the sharpest single result here: the **same** unbalanced
```` ``` ```` inserted **before** the corrections section gives `corrected=0 junk=5` and exit 1. One stray fence line, placed one
section earlier, is a red; placed at the end, it is free.

**(c) The register's shape is never read — 8 survivors.** R7 and R28 rewrite the header row to arbitrary text (the header is skipped
by `n == 0`, `:192`); R9 swaps two rows (rows are keyed, so order is irrelevant); R15 removes the trailing newline; R17 inserts a
`#` comment line and R18 a blank line (both have ≠ 4 tab fields, so they are skipped); R8, R34, R35 append decoy rows whose keys
are not population keys (`999 bogus-token`, `997 decoy2`, `998 decoy`) — the counter iterates over the 70 population items, so a row
for a key it never looks up is invisible. This is wave 1's `N10`/`N15` confirmed.

**(d) Two normalisation escapes inside the parsed grammar — 2 survivors.** L51 writes the `line=` field as `014`: `CORR` captures
`"014"` and `int("014") == 14`, so the key matches the derivation and the target stays met. The register has no such escape (R30
`014` gives `registered=69`, because the register key is the raw string `"014"`). L23/L26 (trailing space/tab) are the third
normalisation escape: `CORR`'s trailing `\s*$` tolerates them.

### 3.3 Fields the counter never reads (the requested list)

| surface | field | never read? | evidence |
|---|---|---|---|
| `corpus/lessons/round-42.md` | any prose sentence, paragraph, heading or scope statement | **yes** | L15–L19, L30–L38, L40, L45 all exit 0 |
| `corpus/lessons/round-42.md` | the section a `CORRECTION-DE` line sits in | **yes** | L25 (moved into `## Mistakes`), L41 (moved to the top of the section) exit 0 |
| `corpus/lessons/round-42.md` | the order of the five `CORRECTION-DE` lines | **yes** | L41 exit 0 |
| `corpus/lessons/round-42.md` | line endings (CRLF vs LF) | **yes** | L20 exit 0 |
| `corpus/lessons/round-42.md` | trailing whitespace after a `CORRECTION-DE` line | **yes** | L23, L26 exit 0 |
| `corpus/lessons/round-42.md` | the leading zeros of `line=` | **yes** (`int()` normalises) | L51 exit 0 (register analogue R30 is red) |
| `corpus/lessons/round-42.md` | a ```` ``` ```` fence **after** the last correction | **yes** | L56 exit 0 (the same fence before them: L55 red) |
| `corpus/lessons/round-42.md` | `~~~` fences, HTML comments, blockquotes, list markers, indentation | **yes** (as *masking*) | L13 exit 0; L54, L53, L39, L22, L49 red — the counter does not mask them, so a correction inside one still counts as corrected (L13) or the line is junk (others) |
| `census/round-42/c1-register.tsv` | the header row's content | **yes** | R7, R28 exit 0 |
| `census/round-42/c1-register.tsv` | row order | **yes** | R9 exit 0 |
| `census/round-42/c1-register.tsv` | rows whose `(line, token)` key is not a population key | **yes** | R8, R34, R35 exit 0 |
| `census/round-42/c1-register.tsv` | comment lines, blank lines, the trailing newline | **yes** | R17, R18, R15 exit 0 |
| `census/round-42/c1-register.tsv` | the number of rows beyond the 70 population keys | **yes** | R8, R34, R35 exit 0 |

And the fields the counter **does** read — every one of them was attacked and every attack was killed:

| surface | field | read how | killed by |
|---|---|---|---|
| lesson | `line=` | `int(m.group(1))` → key | L10 (`14`→`15`), L42 (`92`→`175`) |
| lesson | `token=` | key part 2, exact string | L6, L44, L47, L59 |
| lesson | `derived=` | compared to `wanted_correction(item)` | L7, L27, L43, L48, L57 |
| lesson | `rev=` | compared to `--base` | L9, L28, L58 |
| lesson | line must be outside a fence | fence toggle on ```` ``` ```` | L12, L14 (four backticks count) |
| lesson | exactly one line per unresolved item | `seen` / `wants` | L1–L5 (delete), L11 (duplicate), L46 (extra for a resolved item) |
| register | `line=` | key part 1, exact string | R12, R30 |
| register | `token=` | key part 2, exact string | R13, R31 |
| register | `class=` | compared to derived class | R1, R14, R19, R24, R32, R22 |
| register | `resolved_to=` | compared to derived path; must exist at the commit | R2, R3, R16, R20, R25, R26, R27, R33 |
| register | row count / duplication per key | `multiplicity` vs `len(got)` | R4, R5, R6, R11, R21, R23, R29 |

### 3.4 Two false-red observations (the counter is also stricter than its own rule)

These are edits that leave the *substance* intact yet turn the counter red — the complement of N-C1a and worth the L1's attention
because they are the "honest candidate is rejected" direction:

- **R10 (register in CRLF)** → `class_ok=0`, exit 1. The counter splits the register on `\n` only, so every `resolved_to` keeps a
  trailing `\r` and no class matches. The lesson tolerates CRLF (L20 exit 0) but the register does not — the asymmetry wave 1 recorded
  as N13, confirmed here from the other direction.
- **L24 (a prose sentence mentioning `CORRECTION-DE`)** → `junk=1`, exit 1, on an otherwise honest triple. The counter flags any line
  containing the marker that does not parse as a correction. This is wave 1's N14.

---

## 4. What this does and does not say

**It says.** The landed triple is exactly as good as the frozen counter can see, and no better. Of 93 single-point edits to the two
content files of C1, 33 leave the target met — every one of them either outside the counter's parse grammar (prose, headings,
placement, ordering, header, decoy rows, line endings, trailing whitespace) or inside it but normalised away (`line=014`, trailing
whitespace after a correction line). Every edit to a field the counter parses is caught. The counter's coverage of the C1 claim is
therefore **exactly the 5 `CORRECTION-DE` lines and the 70 register rows, and nothing else**.

**It does not say.** That the landed triple is *wrong*. The lane's compensating checks (the five-reader verification of the register,
the independent re-derivation, the L1's instrument re-run at the landed revision) are unaffected by this survey — the survey shows
the *counter* cannot see prose, not that the prose is false. Nothing here argues for editing the frozen counter: the counter is
frozen, and a miss is reported, never narrowed.

**Recommendation for the L1 (a named limit, not an edit).** The wave-1 `N-C1a` wording should be refined to the grammar-level
statement in §3.1, and the round lesson's own `N-C1c` list should gain the three limits this survey adds: (i) the prose, headings and
placement of the lesson are never read (16 survivors, L15–L19, L30–L38, L40, L45); (ii) the fence rule is ```` ``` ````-only and
position-sensitive (L13, L20, L23, L26, L56 vs L55); (iii) the register's header, order, extra rows and non-population decoy rows are
never read (R7, R8, R9, R15, R17, R18, R28, R34, R35). The two normalisation escapes (L51 `line=014`; L23/L26 trailing whitespace)
should also be named, and the register/lesson CRLF asymmetry (R10 vs L20) is worth one line in the lesson's limit list.

---

## 5. Reproducibility and hygiene

- Every mutant file and every `SUMMARY` receipt is in this seat's own directory (`.ufo/waves/round-42/w2/R42w2mutationtester04/`),
  which is git-ignored (`.gitignore:1: .ufo/waves/`), so nothing in the lane is tracked or modified.
- The mutation generators (`gen.py` … `gen4.py`), the scorer loop (`score_all.sh`) and the pristine copies were kept under
  `/fast/scratch/hyaku/souji-r42/R42w2mutationtester04/`, the seat's own scratch, and that directory was removed after the receipts
  were copied here. `score-candidate.sh` clones the lane into a fresh temp dir under the same scratch root and removes it; it never
  writes into the lane.
- The lane was not written at any point. `git status --porcelain` is empty and both attacked files hash identically to the tip commit
  `3105a63b23481fccf7df58e74d14a6681e0ea0c8` (§1.2).
- No tool was installed or upgraded for this seat (nothing needed installing); the host's `pacman` guard was not touched.
- No mutating git or jj command was run in the lane or the fleet; `score-candidate.sh`'s commit happens inside its own throwaway clone
  with identity supplied through the environment, and every git call there names `-C "$C"`.
