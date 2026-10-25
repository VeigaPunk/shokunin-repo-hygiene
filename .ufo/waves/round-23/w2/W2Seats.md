# W2Seats — seat-failure carry check (round 23, wave 2)

Seat: `L1Souji23.W2Seats`. Read-only. Lane tip read: `1026900` (`round-23: wave-2 spec, runner decode
hardening, prereg mechanism note`); the round's landed work per the wave-2 brief is `4765250` +
`c0eeaa7`. Scratch `/var/tmp/souji-r23-w2-Seats/` created and removed.

## Verdict

**`survives` on the frozen carry requirement — 9 required, 9 listed, missing 0, extra 0.**
**`falsified` on the section's own method claim** ("Every failure paragraph is carried verbatim
below", `corpus/lessons/round-23.md:124-125`): 2 of the 9 carried entries quote bytes that are not in
the seat report at the lane tip, and 1 quotes a number that exists in no committed revision of that
seat. Findings F1–F4 below; F1–F3 are `fix` or `disclose`, F4 is `disclose`.

## Counting command and output

Required set (first `STATUS:` line says `FAIL` or `PARTIAL`):

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-23/w1
for f in *.md; do v=$(grep -m1 -oE 'STATUS:[[:space:]]*[A-Za-z-]+' "$f" | sed -E 's/STATUS:[[:space:]]*//');
  case "$v" in FAIL|PARTIAL) echo "$f";; esac; done | sort
```

Distribution over all 41 `.md` seat reports in `w1/` (44 files total; the other three are
`swarm-registry.json` and two fixture `.py`):

```
NONE 2   PASS 30   PARTIAL 6   FAIL 3
```

`41 = 30 + 6 + 3 + 2`, and `w1/swarm-registry.json` `members` = **41**, so the lesson's "Wave 1
carried 41 seats; nine reported `PARTIAL` or `FAIL`" (`corpus/lessons/round-23.md:124`) is exact.

Listed set (paths inside `## Seat-reported failures`):

```
awk '/^## Seat-reported failures/{f=1;next} /^## /{f=0} f' corpus/lessons/round-23.md \
  | grep -oE 'w1/[A-Za-z0-9]+\.md' | sed 's|w1/||' | sort
```

```
required=9 have=9
=== MISSING (required, absent from lesson) ===
=== EXTRA (in lesson, not required) ===
SETS-IDENTICAL
```

(`comm -23` / `comm -13` of the two sorted files; `cmp -s` reports identical.)

## The two lists

**A. Required — first `STATUS:` is FAIL/PARTIAL (9)**

| seat | verdict | lesson line |
|---|---|---|
| `CritC2Value.md` | FAIL | 128 |
| `CritC3Ground.md` | PARTIAL | 129 |
| `CritPrereg.md` | FAIL | 130 |
| `MutCounter.md` | PARTIAL | 131 |
| `MutReceipt.md` | PARTIAL | 132 |
| `RevD6.md` | PARTIAL | 133 |
| `RevD7.md` | FAIL | 134 |
| `ScribeLesson.md` | PARTIAL | 135 |
| `SentinelScope.md` | PARTIAL | 136 |

**B. Listed under `## Seat-reported failures` (9)** — same nine, one bullet each, in the order
`CritC2Value, CritC3Ground, CritPrereg, MutCounter, MutReceipt, RevD6, RevD7, ScribeLesson,
SentinelScope`. No duplicates (`uniq -c` gives 1 for every path), no bullet lacks a disposition word
(`grep -vcE 'accepted|rejected|disclosed|open'` = 0 over 9 bullets).

**Diff: missing = ∅, extra = ∅.** Every listed entry carries an explicit `open — accepted[: …]` plus
the repair it was closed by, which satisfies "with a disposition".

## Findings

### F1 — MEDIUM — `corpus/lessons/round-23.md:131` quotes a mutant count that exists in no commit. `fix`

Lesson text:

```
- `.ufo/waves/round-23/w1/MutCounter.md` "STATUS: PARTIAL — 51 clause mutants designed for `tools/souji-record-agreement.py` (sha256" — open — accepted: …
```

The seat, at tip and at the lesson's own landing commit, says **54**:

```
$ grep -m1 'STATUS:' .ufo/waves/round-23/w1/MutCounter.md
STATUS: PARTIAL — 54 clause mutants designed for `tools/souji-record-agreement.py` (sha256
$ git show 4765250:.ufo/waves/round-23/w1/MutCounter.md | grep -m1 'STATUS:'
STATUS: PARTIAL — 54 clause mutants designed for `tools/souji-record-agreement.py` (sha256
$ git diff --stat 4765250 1026900 -- .ufo/waves/round-23/w1/MutCounter.md
(no output — unchanged between the two landing commits)
```

`51` is therefore not a stale copy of a later revision: the seat has said `54` at every revision that
exists, and the lesson (landed in the same commit, `4765250`) quotes a pre-commit draft. The seat's
own split is `12` contract-mandated kills, `13` contingent kills, `1` equivalent, **`28` with no
killing case** (`MutCounter.md:7-9`) — a reader of the lesson is told a different inventory size.
Round must re-quote the tip bytes (54), or state that the figure is superseded.

### F2 — MEDIUM — `corpus/lessons/round-23.md:132` quotes a clause count the seat no longer holds. `fix`

Lesson quotes `"… 26 mutants over 20 clauses; 9 killed, **uncovered=17**. The fixture is now a"`.
The seat at tip reads `26 mutants over 21 clauses (the 12 enumerated plus 9 the implementation adds
or …` (`MutReceipt.md:3`). The quote was verbatim at `4765250` and went stale at `c0eeaa7`:

```
$ git diff 4765250 1026900 -- .ufo/waves/round-23/w1/MutReceipt.md
-STATUS: PARTIAL — 26 mutants over 20 clauses; 9 killed, **uncovered=17**. The fixture is now a
+STATUS: PARTIAL — 26 mutants over 21 clauses (the 12 enumerated plus 9 the implementation adds or
```

The seat was revised by a later commit than the lesson; the lesson was not re-read against it. This is
the same ordering class as the round's own disclosed "counters repaired after wave-1 scoring", but
here it leaves a *quoted* figure wrong. Fix the quote, or replace "carried verbatim" with "carried as
quoted at `4765250`, since revised" and name the two seats.

### F3 — MEDIUM — `corpus/lessons/round-23.md:132` disposition asserts fixture coverage its own seat denies. `disclose` or `fix`

Disposition: "the receipt fixture now covers the digest-from-clone clause and the newline-preserving
capture". The seat at tip, on the same clause:

```
.ufo/waves/round-23/w1/MutReceipt.md:5-7
… on it the "tool digest from the tree at rev"
clause is **not** killed by case 3 and cannot be: case 3 discriminates only the `verify` side. The
stdout/stderr-verbatim clause is uncovered *by the fixture's own concession*, …
```

`tests/fixtures/r23-receipt-run.py` has no case naming the clone/tree-digest path (grep for
`clone|newline|trailing` over the file returns nothing; cases 1–8 are the enumerated contract cases),
which is consistent with the seat and not with the disposition. A disposition may not claim coverage
the seat reports as `uncovered`; the round must either fix the fixture or restate the disposition as
"case 3 covers the verify side only; the execution-side digest clause is uncovered (seat finding 3)".

### F4 — LOW — the frozen rule is syntactically blind to two seats that carry no `STATUS:` line. `disclose`

`w1/ScribeEntryRepoSize.md` and `w1/ScribeReport.md` have no `STATUS:` line at all (case-insensitive
`status|verdict` scan finds only an unrelated `git status --porcelain` mention at
`ScribeReport.md:194`). Under the frozen rule neither is required, and I have not counted them as
missing. But `ScribeReport.md:3` declares itself "**This is a draft.**" and carries **252**
`<PLACEHOLDER>` tokens, while the other draft seat, `ScribeLesson.md:3`, self-labelled
`STATUS: PARTIAL — draft only` and was carried. Two drafts, one labelled and carried, one unlabelled
and invisible to the rule. `ScribeEntryRepoSize.md` is a completed entry whose acceptance is recorded
by the ADMIT decision instead, so it is covered by another mechanism.

The lesson should state that the carry census is over *labelled* seats and name the two unlabelled
ones, so that "nine reported `PARTIAL` or `FAIL`" is not read as "the other 32 reported `PASS`"
(it is 30 `PASS` + 2 unlabelled).

## What I verified, and what I did not

- Verified by running: the two sets and the set diff; the verdict distribution over all 41 reports;
  the registry member count (41); quote fidelity by prefix comparison of each lesson quote against
  the seat's `STATUS:` line; `git show`/`git diff` of the two seats between `4765250` and `1026900`
  (read-only); absence of any status marker in the two unlabelled seats; absence of a clone/newline
  case name in `tests/fixtures/r23-receipt-run.py`.
- `[INFERENCE]` Not run: I did not execute the fixtures or re-derive any mutant verdict, so I do not
  certify the *truth* of any disposition — only that a disposition exists and, for F3, that it
  contradicts the seat's own text. The other seven dispositions are presence-checked only.
- Residual risk: the carry check is satisfiable by a lesson that lists nine paths and writes nine
  sentences; it has no content constraint, and F1–F3 show the two artefacts (lesson text, seat text)
  can drift apart while the set stays identical. A stronger rule would quote the seat's `sha256`, not
  its prose.
- No credentials, no live `/proc`, no operator-sweep contents, no `.scratch/`, no `.ufo/state/`, no
  git/jj mutation, no installs. Nothing outside the lane written.
