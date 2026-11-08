# S86Scribe — souji round 86 seat report

Seat: `S86Scribe` (scribe). Lane: `souji` (`/home/vgpnk/Projects/shokunin/souji-shokunin`). Wave: r86 w1, 12 seats,
one v1 wave. I deliver files and findings only: no commit, no push, no git/jj mutation in the lane, no edit of fleet
or sibling-lane files, no edit of `MANIFEST.json`, `.ufo/state/*`, `.scratch/*` or `.ufo/watchdog.log`.

Tooling: no tool was installed or upgraded this round, so there is nothing to record under the operator directive of
2026-10-19. Everything below was produced with the host's stock `python3` and `git` 2.56.0-1. I ran no `pacman`
transaction (the pacman guard is paused host-wide).

## What I delivered

Three drafts for the L1 to integrate, all under `.ufo/waves/round-86/w1/S86Scribe/`; the lane's `corpus/` files are
unchanged.

1. `S86Scribe/draft-own-tree-pointer-binding-row-is-the-work.md` — the new section for
   `corpus/knowledge/own-tree-pointer-binding.md`, "Grounding an unbound clause: the row is the work (r86)".
2. `S86Scribe/draft-filter-filemode-witness-audit-tool-concealment-classes.md` — the new section for
   `corpus/knowledge/filter-filemode-witness.md`, "The audit tool's own concealment classes (r86)".
3. `S86Scribe/draft-quality-q158-q159.md` — the two `corpus/QUALITY.md` rows Q158 and Q159, round-85 style, in a new
   `## Round 86 criteria` section.

Plus three reproducer instruments and their receipts, so the L1 can re-derive the per-row attribution, the raw record
text and the TAB-class defect that the round's own receipts do not carry:

- `S86Scribe/probe-row-decides-clause.py` → `S86Scribe/receipts/f1-row-decides-clause.txt`
- `S86Scribe/probe-k4-record-text.py` → `S86Scribe/receipts/f2-k4-record-text.txt`
- `S86Scribe/probe-tab-name-field-split.py` → `S86Scribe/receipts/f4-tab-name-field-split.txt`
- `S86Scribe/receipts/f3-c1-two-arms.txt` — my verbatim re-derivation of the two C1 arms.

Each draft ends with a `## Gate` note naming its destination, what it replaces (nothing, in all three cases), the L1's
dependencies, and the pointers it carries.

## `## Gate` — which draft is which entry

Each of the three drafts carries its own `## Gate` note. The map, in one place:

| draft | destination entry | replaces | L1 dependency |
|---|---|---|---|
| `S86Scribe/draft-own-tree-pointer-binding-row-is-the-work.md` | `corpus/knowledge/own-tree-pointer-binding.md`, a NEW section "Grounding an unbound clause: the row is the work (r86)" | nothing | update the file's `source:`/`verified-at:`/`recheck:` front matter; no new SOURCES row needed |
| `S86Scribe/draft-filter-filemode-witness-audit-tool-concealment-classes.md` | `corpus/knowledge/filter-filemode-witness.md`, a NEW section "The audit tool's own concealment classes (r86)" | nothing | update the file's front matter; no new SOURCES row needed (the L1 already admitted S341-S343) |
| `S86Scribe/draft-quality-q158-q159.md` | `corpus/QUALITY.md`, a NEW `## Round 86 criteria` section carrying Q158 and Q159 | nothing (Q158 extends Q157 and says so; Q159 is new) | author `corpus/lessons/round-86.md` with the C1/C2 findings the rows' lesson cells name — the file now exists in the L1's working tree, so the dependency is met |

## Findings

### F1 — each new row binds exactly one clause, and the clause is not always the branch that prints the refusal

The r86 C1 population adds NF-W (`census/round-86/c1-false-rows.tsv:49`) and NF-Y (`:50`), and the mutant set adds
`c7-census-in-tree` and `m14-short-shape` (`census/round-86/c1-mutants.json`). I re-derived, on the committed bytes
(receipt `receipts/f1-row-decides-clause.txt`, produced by `probe-row-decides-clause.py`):

- the counter's own refusal message for each row (its `--forge` path, with the expectation deliberately wrong so the
  counter prints `why`):
  - NF-W → `why=census-in-tree target is not a wave capture keeping the token's full path suffix`
    (`census/round-86/c1-pointer-counter.py:425`);
  - NF-Y → `why=own-round-tree target is neither the token's own path nor a wave capture keeping the token's suffix`
    (`:409`);
- each mutant turns exactly one row green and leaves the other refused:
  - `c7-census-in-tree` → NF-W goes `REFUSED`→`MOVED`, NF-Y stays `REFUSED`;
  - `m14-short-shape` → NF-Y goes `REFUSED`→`MOVED`, NF-W stays `REFUSED`;
- both mutants are no-ops on the r85 47-row population (`SUMMARY rows=47 mismatches=0` for each) and each kills exactly
  one row on the r86 49-row population (`ROW NF-W … match=no` / `ROW NF-Y … match=no`, `SUMMARY rows=49 mismatches=1`).

**The point worth carrying into the corpus.** For NF-W the branch that PRINTS the refusal is the deciding one: the
census-in-tree branch at `:417-425`, reached because the own-tree belt at `:405` is vetoed by its
`not _owntree_ok(...)` conjunct (`OWNTREE_WAVE` at `:351` matches `w1/`, and `got[1:] == want[1:]` at `:371` holds).
For NF-Y the branch that PRINTS the refusal is the own-tree belt at `:405-409`, but the branch that DECIDES the row is
the short-shape guard inside `_owntree_ok` at `:366-367`: dropping only that guard lets `_capture_ok` (`:368-369`)
accept the one-component remainder, `_owntree_ok` returns True, the belt stands down, and the row resolves as MOVED.
The mutant is the right witness for a clause, not the printed reason — the belt is a caller of the guard, not the guard.
The draft says this explicitly, because a reader who binds "the own-tree belt" here would bind the wrong clause and
would then believe the belt is unbound.

### F2 — the two C1 arms re-derive green on the committed bytes, and the delta is the population

- after: `python3 -B census/round-86/c1-clause-battery.py --counter census/round-86/c1-pointer-counter.py --work
  <scratch outside /tmp> --only r85,r86 --expect-killed 14` → `ARM pristine pop=r85 rows=47 mismatches=0 errors=0`,
  `ARM pristine pop=r86 rows=49 mismatches=0 errors=0`, six `MUTANT-PAIR` `killed=yes` on both, `c7-census-in-tree`
  `pop=r85 killed=no | pop=r86 killed=yes`, `m14-short-shape` `pop=r85 killed=no | pop=r86 killed=yes`,
  `SUMMARY mutants=8 sets=r85,r86 pristine_r85=ok pristine_r86=ok killed_r85=6 killed_r86=8 killed_total=14`, EXIT 0;
- before: the same battery and the same eight mutants on the r85 population alone → `killed_r85=6`,
  `c7-census-in-tree killed=no`, `m14-short-shape killed=no`, EXIT 0.

Both agree with the filed receipts `census/round-86/records/c1-after.txt` and
`census/round-86/controls/c1-before-r85-population.txt` line for line (the receipt binds counter
`8278ea4d…f3`, harness `2dac2e81…9d9`, mutants `6f055ede…a6`, populations `1468236c…8d42` / `79db70f6…f561` — all four
shas re-derived from the committed files). I also confirmed the population delta directly: the r86 population minus
NF-W and NF-Y is byte-identical to the r85 population, and the r86 counter differs from the r85 counter by ONE `POPS`
entry (`:136-140`) plus its docstring — no resolution rule, guard, branch or message changed.

### F3 — the two C2 arms re-derive green, and the raw records show the class split

- filed tool: `SUMMARY rows=9 mismatches=0 errors=0`, `EXIT=0`; KG1 `k4=1 named=yes` (`k4rows=['.|index-flag-concealed']`),
  KG2 `k4=1 named=yes` (`k4rows=['.|stat-cache-concealed']`);
- lane-base tool bytes (`census/round-86/controls/c2-before-base-tool.py`, byte-identical to the tool at `89d02c90`):
  `SUMMARY rows=9 mismatches=2 errors=0`, `EXIT=1`; KG1 `k4=0 named=no` (no row at all), KG2 `k4=1 named=no`;
- the seven r85 rows are identical in both arms.

Both agree with `census/round-86/records/c2-after.txt` and `census/round-86/controls/c2-before-base-tool.txt`.

The raw `MISMATCH\tK4\t…` lines (not carried by any receipt; from my own run over the counter's own fixture) are in
`receipts/f2-k4-record-text.txt`:

- KG1, filed: `MISMATCH\tK4\t.\tindex-flag-concealed\tRECEIPT-GITLINK-CONCEALED: nest is a gitlink (mode 160000)
  carrying index flag S; …` — KG1, base: no K4 row at all.
- KG2, filed: `… (bad\nname.txt); …` (one physical line, the name recoverable); KG2, base: `… (bad name.txt); …`
  (one physical line, the name NOT recoverable).

**The point worth carrying into the corpus.** The two rows exercise the two layers SEPARATELY: KG1 is a flag class
(caught by the new index-flag sweep, reported `index-flag-concealed`) and KG2 is a stat-cache class (caught by the
byte-truth re-hash, reported `stat-cache-concealed`). A repair that had added only the flag sweep would have left KG2
failing; a repair that had only escaped the message would have left KG1 failing. And the space-join is the worse
failure of the two escape options: it keeps the record on one line while making the name unrecoverable — `bad\nname.txt`
and `bad name.txt` are different paths, and only one of them exists.

### F4 — the space-join is a SECOND defect, not the LF defect the r85 seat described

The r85 seat's §2e finding (`S85ExecK4.md`) described the newline-path defect as "the emitted `MISMATCH…` line embeds a
literal LF inside the detail", and the r85 repair `ec7c5732` responded by replacing that LF with a SPACE in the
bootstrap (`msg.replace(chr(10), ' ')`, still at `census/round-86/controls/c2-before-base-tool.py:199`). The lane-base
bytes therefore do NOT embed a raw LF — they space-join it. That is a real difference and it changes the lesson: the
space-join is not "the LF problem, still unfixed", it is a second, quieter defect that the space-join introduced, and
it is what makes the r86 escaping necessary. The space-join keeps the record on one physical line but makes the name
UNRECOVERABLE — `bad\nname.txt` and `bad name.txt` are different paths and only one of them exists. The r86 draft says
so, and the QUALITY draft Q159 says "escaped, never space-joined" for exactly this reason.

**Correction to my own first reading of this.** I wrote in an earlier draft of this report that the landed r85 corpus
section "still describes the LF-embedding form" and that a reader comparing it with the base bytes would see two
descriptions of the same defect. That is WRONG, and I checked it rather than leaving it: the landed r85 corpus section
(`corpus/knowledge/filter-filemode-witness.md`, "r85: the lane's own audit instrument was the last one trusting the
stat-cache verdict") does not mention the newline, the LF or the escape AT ALL — `git show HEAD:corpus/knowledge/
filter-filemode-witness.md` over that section returns zero matches for `newline|escape|\n`. The LF-embedding
description lives only in the r85 SEAT REPORT (`.ufo/waves/round-85/w1/S85ExecK4.md` §2e), not in the corpus. So
there is no corpus contradiction to flag; the thing that needs saying is the one my F4 first paragraph says, and the
L1's new corpus section (already in the working tree) does not repeat the LF-embedding form either.

### F5 — the base bytes' space-join leaves a TAB name to split the record's fields (a class the round did not measure)

The base tool's bootstrap replaces ONLY `chr(10)` with a space
(`census/round-86/controls/c2-before-base-tool.py:199`). A TAB in a path name is not replaced at all, so it lands RAW
inside the detail field of a TAB-delimited record and the record's field structure changes. I measured this directly
(`probe-tab-name-field-split.py`, receipt `receipts/f4-tab-name-field-split.txt`): a tracked file named
`bad<TAB>name.txt`, forged under the index stat cache, over the frozen counter's own fixture:

```
--- FILED rc=1
   fields=5  repr='MISMATCH\tK4\t.\tstat-cache-concealed\tRECEIPT-WORKTREE-STAT-CONCEALED: 1 tracked path(s) git status reports clean do not hash to the object id the index records (bad\\tname.txt); the index stat cache conceals a worktree change; no receipt written'
--- BASE rc=1
   fields=6  repr='MISMATCH\tK4\t.\tstat-cache-concealed\tRECEIPT-WORKTREE-STAT-CONCEALED: 1 tracked path(s) git status reports clean do not hash to the object id the index records (bad\tname.txt); the index stat cache conceals a worktree change; no receipt written'
```

The filed tool emits FIVE tab-separated fields and the base tool SIX — the base record's detail field is split in two
by the raw TAB, so a reader parsing on the tab boundary reads the detail as two fields and the path as a fragment. The
filed tool escapes the TAB (`tools/souji-record-agreement.py:226` replaces `"\t"` with `"\\t"`), so it holds the record
shape.

This is a class the round's own KG2 row does NOT measure: KG2 is a NEWLINE name, and the newline is exactly the one
control byte the base bytes happen to handle (by destroying it). The round's population has no tab-named row, so this
defect was invisible to the frozen 9-row counter — which is why its two arms read `mismatches=2` and `mismatches=0`
without this appearing anywhere. My QUALITY draft Q159 names the TAB explicitly and points at the escape line, and my
filter draft's `## Gate` note says the raw record text is mine rather than the round's. This is the r87 candidate the
L1 should route, not something this round's claims cover.

### F6 — pointer audit of the L1's working-tree corpus sections: three r85 line numbers carried into an r86 section

The L1 landed its own `corpus/knowledge/own-tree-pointer-binding.md` section in the working tree while I was measuring.
I audited its line pointers against the committed bytes. The section's `verified-at:` is `47602fa6` (the r86
instruments commit) and its `recheck:` names `census/round-86/c1-pointer-counter.py`, so its pointers must resolve in
the R86 counter. Three do not:

| landed pointer | landed text says | in `census/round-86/c1-pointer-counter.py` it is | the r86 line is |
|---|---|---|---|
| `:351` | "the own-tree short-shape guard in `_owntree_ok`" | `OWNTREE_WAVE = re.compile(r"^(?:w[0-9]+\|a2w1\|assimilation)/")` | `:366-367` (the guard) |
| `:387` | "The basename clause at `:387`" | `else "digest differs")` | `:401-402` (the basename clause) |
| `:417-425` | "census-in-tree at `:417-425`" | CORRECT — the census-in-tree branch and its `why` | `:417-425` |

`:351` and `:387` are the R85 counter's line numbers (`census/round-85/c1-pointer-counter.py:351` is `got = [c for c
in tt.split("/") if c]` and `:387` is the basename clause's `elif`). The r85 corpus section already cites `:387` for
the basename clause, in a section about the r85 counter, where it is right; the r86 section inherits the number into a
section whose instrument is the r86 counter, where it is not.

The audit is mechanical and I ran it over my own drafts too: every `path:line` reference in my three drafts resolves
(45 line references, 0 unresolved) and every path resolves. My drafts cite the r86 counter's lines throughout.

**Status.** These are pointers in the L1's WORKING-TREE files, which are not yet committed; the L1 owns the edit and
may already have moved them. I report it because the corpus file's own `verified-at:`/`recheck:` header says which
counter a reader should read, and a pointer that names a different file's line is the one failure mode a reader
cannot detect by reading.

## Out of scope / not done

- I did not edit `corpus/knowledge/own-tree-pointer-binding.md`, `corpus/knowledge/filter-filemode-witness.md` or
  `corpus/QUALITY.md`; the L1 owns those edits (and landed its own while I was measuring — see the note at the end).
- I did not author `corpus/lessons/round-86.md`; the L1's QUALITY rows name it as their lesson pointer. The file now
  exists in the L1's working tree, so that dependency is met without me writing it.
- I did not verify the round's claim-falsification ledger (`.ufo/waves/round-86/claim-falsification.tsv`) against the
  preregistration's stated wording beyond reading the preregistration itself; the L1 owns the pre-file reconciliation.
- I did not touch the C1 `items` population, the counter, the mutants, the batteries, the C2 counter or the tool.

## Known limits of my own findings

- The per-row attribution (F1) and the raw record text (F3) are MINE, not the round's: the filed receipts carry the
  arm summaries and the `k4=`/`named=` columns, but not which row kills which mutant, and not the `MISMATCH` lines.
  Both are reproducible with the probes in my seat directory, and both are quoted in the drafts with that stated.
- The C1 fixture rows NF-W and NF-Y are synthetic; they prove the rule's verdict on their shapes, not that the lane
  ever made those moves. Both drafts state this.
- The C2 fixture is hermetic and synthetic; KG1's nested repository is bound by an index gitlink with no
  `.gitmodules`, so the row proves the flag sweep SEES a concealed gitlink commit, not that submodule state is read.
  The draft states this.
- I re-derived the arms on the committed bytes at lane base `2acbbfc8`; the receipts under `census/round-86/records/`
  were untracked in the working tree at the time I read them (`git status` shows `?? census/round-86/records/`), so the
  L1 should confirm they are committed at the shape I quoted.
- The L1 landed its own `corpus/` sections, `corpus/lessons/round-86.md` and `plans/round-86.md` in the working tree
  WHILE I was measuring (I observed `corpus/QUALITY.md`, `corpus/README.md`, `corpus/SOURCES.md`,
  `corpus/knowledge/filter-filemode-witness.md`, `corpus/knowledge/own-tree-pointer-binding.md` and the new
  `corpus/lessons/round-86.md` as modified/untracked). My drafts were written against the committed bytes and were not
  revised to match the L1's working-tree text; they are drafts, and the L1 owns the merge. Two checks the L1 may want
  against its own landed text, both of which I verified on the committed bytes: the landed own-tree section cites the
  census-in-tree branch at `:417-425` and the basename clause at `:387` — in the r86 counter `:387` is
  `else "digest differs")` and the basename clause is at `:401-402` (`:387` is the r85 counter's line); and the landed
  section cites the short-shape guard at `:351`, which in the r86 counter is `OWNTREE_WAVE` (the guard is at `:366-367`).
  Those are the r85 counter's line numbers carried into an r86-counter section. My own draft cites the r86 counter's
  lines throughout (`:351` for `OWNTREE_WAVE`, `:366-367` for the guard, `:405-409` for the own-tree belt,
  `:417-425` for the census-in-tree branch).
