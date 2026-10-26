# SwarmScribe24 — round 32 w1, C3Docs (F1 documentation edits drafted)

## Status

STATUS: PASS — the four assigned documentation edits are drafted at
`.ufo/waves/round-32/w1/deliver-docs-f1.md` with exact anchors, old/new lines and full replacement
text; every measured line is a `<RESULT ...>` placeholder because the C3 entry, fixture and record
belong to sibling seats and do not exist at the revision read, which the assignment requires.

## Evidence

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`; revision read
`7a6667cd27652baf8d704b5cdb8e3200bd6e27a1` (`git rev-parse HEAD` and
`git log -1 --format='%H %s'` → `round-32: controls, amendment A0 (C1 v2: cited evidence, count
adjacency) with its controls`), which is the controls commit named in the assignment; the frozen
preregistration is `3ec84fc81b3243429c834a051880b0bcde06291c`.

Target shapes read this run:

```
$ wc -l corpus/README.md PROVINCE.md SKILL.md
   701 corpus/README.md
   236 PROVINCE.md
   403 SKILL.md
$ grep -n 'F1 git-native housekeeping' corpus/README.md
39: (the F1 coverage-map row: status cell "frontier, entries held", six backticked entries)
$ grep -n '^## Round' corpus/README.md | tail -1
643:## Round 31 — F1 object lifetime behind a dropped keep ref
$ grep -n '^##' PROVINCE.md | tail -1
213:## Round 31 boundary note (F1 object lifetime)
$ grep -n 'Gate registry' SKILL.md
170:## Gate registry   (last table row 236, the r31-jj-object-clock probe)
```

Counter literals that bind the docs I draft (`grep -nE '^(ENTRY|RUN|FIXTURE|CONTRACT|ARMS)' census/round-31/c3-counter.py census/round-32/c3-counter.py`):

```
census/round-32/c3-counter.py:51:ENTRY = "corpus/knowledge/jj-abandoned-object-mtime-clock.md"
census/round-32/c3-counter.py:52:RUN = "census/round-32/records/jj-mtime-clock-run.txt"
census/round-32/c3-counter.py:53:FIXTURE = "tests/fixtures/r32-jj-mtime-clock.sh"
census/round-32/c3-counter.py:54:CONTRACT = "census/round-32/c3-contract.txt"
census/round-32/c3-counter.py:56:ARMS = ("recent", "old", "mixed", "never", "nocruft")
census/round-31/c3-counter.py:38:ENTRY = "corpus/knowledge/jj-dropped-keep-object-lifetime.md"
```

Base readings used as the three new gate-registry rows' red arms, copied verbatim:

```
census/round-32/records/controls.tsv
C2-do-nothing(prereg)	c2	SUMMARY items=27 pass=1 fail=26 rev=3ec84fc81b3243429c834a051880b0bcde06291c
census/round-32/records/m1-red-before.txt
BAD 16 arm=reflog-only outside the contract's two arm values (same for BAD 17, 18 and 19)
lines=17 bad=4
exit=1
```

`tools/souji-record-contract.py` (82 lines) and `census/round-32/c2-counter.py` docstring plus
`main()` were read whole; `census/round-32/c3-contract.txt`,
`census/round-32/records/amendments.txt`, `census/round-32/records/preregistration.txt`,
`census/round-32/c2-items.tsv` header, `tools/souji-coverage-agreement.py:1-60` and
`tools/souji-landing-gate.py:86-88,1197-1210` were read for the constraints in the delivery.

Artifact presence at the read revision (`for` loop over the five paths):
`corpus/knowledge/jj-abandoned-object-mtime-clock.md`, `tests/fixtures/r32-jj-mtime-clock.sh` and
`census/round-32/records/jj-mtime-clock-run.txt` → MISSING;
`tools/souji-record-contract.py` (82 lines) and `census/round-32/records/amendments.txt` (11 lines)
→ EXISTS.

Uncommitted drafts in the wave directory, read for wording alignment only (`wc -l`, then a count of
`RESULT` lines): `deliver-entry-jj-abandoned-object-mtime-clock.md` 200 lines, `deliver-r32-jj-mtime-clock.sh`
313 lines, `deliver-jj-mtime-clock-run.txt` 24 lines of which 22 start `RESULT `; the wave directory
held 101 entries. These are blobs in `.ufo/waves/round-32/w1/`, not the committed entry, fixture or
record, and no counter can read them.

No measurement was executed by this seat and no counter was run: nothing here is an execution
claim. No scratch directory was created (`/fast/scratch/hyaku/souji-r32/C3Docs` does not exist);
no clone, fixture or download was needed. No tool was installed or updated.

## Findings

1. Delivery written: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/w1/deliver-docs-f1.md`
   (19324 bytes) — Edit 1 at draft line 39 (in-place `corpus/README.md:39` F1 row, one name
   appended: `knowledge/jj-abandoned-object-mtime-clock.md`, status cell unchanged), Edit 2 at
   line 53 (`## Round 32 — F1 the abandoned object's own mtime clock` with `### Frontier (r32)`
   and `### Round 32 corrections`), Edit 3 at line 118 (`## Round 32 boundary note (F1 mtime
   clock)`, one paragraph), Edit 4 at line 146 (one error-pattern bullet plus three gate-registry
   rows). Fill notes, eight in all, follow at line 178.
2. The docs are load-bearing for the C3 counter, not decoration: `census/round-32/c3-counter.py:14`
   fixes L2 as `coverage agreement (tools/souji-coverage-agreement.py@REV) prints exactly`
   `grounded=18 mapped=18 dangling=0 mismatches=0`, and
   `tools/souji-coverage-agreement.py:7-8` defines `MISSING-FROM-MAP   entry with front-matter`
   and `DANGLING-MAP-PATH  knowledge path` — so Edit 1's entries-cell span is what moves `mapped`
   17→18 while `dangling` stays 0. An entry landed without that row edit fails L2.
3. `tools/souji-landing-gate.py:86-88` fixes the citation shape my rows must satisfy:
   `# SKILL.md registry citation shape: one path segment deep under tools/,` with
   `tests/fixtures`/`census/round-<n>` equivalents, and lines 1197-1210 flag `LG-MISSING-REG` for a
   cited path absent at REV. All three new paths (`tests/fixtures/r32-jj-mtime-clock.sh`,
   `tools/souji-record-contract.py`, `census/round-32/c2-counter.py`) match the shape and must exist
   at the C3 landing commit.
4. Peer conflict, reported verbatim. `SwarmScribe22` (item `C3Entry`) wrote: "Name mismatch first: no
   `corpus/knowledge/jj-abandoned-object-mtime-clock.md` exists or is drafted in this lane/wave."
   and "The r31 C3 entry is bound by a literal in the frozen counter — `census/round-31/c3-counter.py`
   sets ENTRY = `corpus/knowledge/jj-dropped-keep-object-lifetime.md`". The round-32 counter's own
   literal (`census/round-32/c3-counter.py:51`, quoted above) and the frozen contract
   (`census/round-32/c3-contract.txt`, keys `arm step obj mtime where object_present`) show the peer
   is reading the round-31 instrument. I replied with those literals and warned that an entry
   drafted on the r31 arm shape (`solo`, `descendant`, `reflog-only`) fails L14. Risk for the L1: if
   the landed entry cites the r31 path or the r31 arms, C3 cannot reach `f1_entries=5 fail=0`.
5. M1 numbers in the drafts are the receipt's, not the assignment prose:
   `census/round-32/records/m1-red-before.txt` prints four `BAD` lines (record lines 16-19) and
   `lines=17 bad=4`, `exit=1`, reproduced over `census/round-31/records/jj-object-clock-run.txt`
   against `census/round-32/m1-r31-contract.txt` (its line 5 fixes the two arm values `solo` and
   `descendant`, so `arm=reflog-only` is out of set). The r32 correction bullet states the r31
   record stands as landed and the fix is instrumentation only.
6. The three gate-registry rows use replayable red arms, not a pinned green baseline:
   `r32-c2-counter` red arm is the counter at the base revision (`controls.tsv` →
   `SUMMARY items=27 pass=1 fail=26`); `souji-record-contract` red arm is the M1 receipt above;
   `r32-jj-mtime-clock` is a probe with no self-test, judged by the C3 counter's L8, L9, L12 and
   L13, matching the `r31-jj-object-clock` row's shape.
7. `census/round-32/c2-counter.py` `main()` confirms the row's verdict map and diagnostics:
   `SUMMARY items=<n> pass=<p> fail=<f> rev=REV`, exit 1 on any fail, exit 2 `could-not-evaluate`
   for usage, bad revision, items file absent at `--list-rev`, or `bwrap`/`strace` absent, and
   `--only` prints `partial=1` and is never a pass. The row states each of those.
8. Everything bounded by placeholders is disclosed, not asserted: the entry, fixture and record are
   absent at `7a6667cd`, so the drafts carry no measured `RESULT` line and no `where=` or
   `object_present=` value; the only counts are placeholders plus fill note 6's peer-reported shape,
   labelled as a message and not as my observation. The fill notes tell the L1 to copy each
   `RESULT` line from the record and to delete any clause the record contradicts, so the prose
   cannot outrun the measurement.
9. Peer-reported fixture shape recorded, not adopted as evidence: `SwarmExecutor18` (`C3Fixture`)
   reports 22 `RESULT` lines (recent 2, old 3, mixed 8, never 3, nocruft 6), the contract's six
   step tokens, `where` values `loose`, `cruft`, `absent` and no `pack` arm, a `lines=22 bad=0`
   contract check with the C3 counter's own checker, and seven measured exit-2 conditions (unset,
   empty, non-directory or inside-lane/inside-fleet TMPDIR; missing `jj`, `git` or `touch`; an
   `mktemp` base in either root). Delivery fill note 6 states that provenance and tells the L1 to
   re-count `<N>` and the arm split from the landed fixture and record; the `r32-jj-mtime-clock`
   gate-registry row now carries the seven refusals as run-reported, to be re-checked against the
   landed bytes and narrowed if they differ. The fixture, record and entry bytes were still absent
   from the lane when checked (`ls` rc 2 on all three; `git status --porcelain` unchanged at one
   untracked `measure.sh`), so nothing in this report or the delivery is an observation of them.
10. Lane state observed, not touched: `git status --porcelain` printed one untracked path,
    `?? census/round-32/measure.sh`, which was not mine and was left alone.
11. Second peer correction applied: `SwarmScribe22` confirmed the round-32 literals, voided its r31
    arm shape, and reported that the entry has no bytes yet and that its `##` headings are
    unconstrained except `## Gate` (which L4, L5 and L6 read). My drafts named no entry heading
    after this, and the `### Frontier (r32)` bullet now says "the edge classes the entry itself
    states as not established" rather than quoting one — the drafted prose constrains no section
    name of the entry it cites. On that peer's landing condition, delivery fill note 7 makes the
    clause a check against the entry's final bytes at the landing commit (rewrite or drop it if the
    entry does not state those classes) and applies the same condition to every "measured" sentence
    in the README entry bullet, the PROVINCE note and the SKILL bullet.
12. Registry-versus-message conflict, resolved from artifacts: `.ufo/waves/round-32/w1/swarm-registry.json`
    assigns `SwarmScribe22` the item `C3Entry` in wave `souji-r32-w1`, yet that agent's IRC messages
    denied any round-32 entry draft and scoped its output to round 31 ("Delivery
    `.ufo/waves/round-31/w1/deliver-quality-q67-q69.md`", "no draft for it exists under
    `.ufo/waves/round-32/w1/`"). The wave directory contradicts both statements: it holds
    `SwarmScribe22.md` ("C3 entry draft (r32 w1)", STATUS PASS),
    `deliver-entry-jj-abandoned-object-mtime-clock.md` (200 lines, H1 and `ground: F1` at lines 8 and
    6), `deliver-jj-mtime-clock-run.txt` (22 `RESULT` lines) and `deliver-r32-jj-mtime-clock.sh`
    (313 lines), 101 entries in all. I used those artifact bytes, not the messages, and left every
    one of them untouched; the committed paths `corpus/knowledge/jj-abandoned-object-mtime-clock.md`
    and `census/round-32/records/jj-mtime-clock-run.txt` are still absent at `7a6667cd`, so C3
    cannot pass L1, L2 or L8 until the L1 integrates them.
13. Three draft sentences were aligned to the sibling drafts, which is wording work, not evidence:
    the `nocruft` outcome now reads as the recent object staying loose rather than a pack being
    removed (`arm=nocruft step=gc-cruft-disabled obj=C … where=loose object_present=yes`, so no cruft
    pack exists in that arm); the backdating is "the object's loose files" (the entry names commit,
    tree and blob); and `### Frontier (r32)` lists the four classes the entry's own limits section
    leaves open instead of the round-31 ones. Delivery fill note 8 records the provenance and leaves
    the landing-time rule to note 7.
14. Attack log: not applicable — this item drafts documentation and asserts no counter claim. Nothing
    in this report proposes a change to a predicate, target, counter or item set.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/w1/deliver-docs-f1.md`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/w1/SwarmScribe24.md` (this report)

## Touched surfaces

Two files, both inside the assigned wave directory. No lane source, corpus, tool, counter, contract
or SCORECARD byte was edited; no `git add`, `commit`, `push`, `stash`, `checkout` or `reset`; no
`jj` mutation; no `rm` or `mv` of anything; no signals. Everything outside the wave directory was
opened read-only.

## Out of scope / limits

- The knowledge entry, its front matter and its Gate; `corpus/SOURCES.md` rows; the fixture; the run
  record; the SCORECARD rows and axis text; the LOG and SHONEN pointers — all other seats' items.
- The delivery's `<RESULT ...>`/`<N>` placeholders must be filled by the L1 from the landed record
  before the landing commit; this report claims no measured value for the mtime clock.
- The C3 counter, the C2 counter and `tools/souji-record-contract.py` were read, never run here; the
  gate-registry rows I drafted describe verdict maps from their source bytes, and their green arms
  are for the L1's verification run.
