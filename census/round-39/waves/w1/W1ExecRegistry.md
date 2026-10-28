# W1ExecRegistry — R6 gate-registry evidence (souji r39 wave 1)

Seat: W1ExecRegistry (executor, leaf). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Judged axis: operability. Scope: enumerate the `SKILL.md` gate-registry table and report presence/absence
of the ten names in the R6 set. Advisory only: no commit, no push, no gate verdict on C1/C2/C3.

Revisions read (read-only git only):

```
$ git rev-parse HEAD
2201778e7736af82e7d8a42dec2494f115bf3923
$ git merge-base --is-ancestor ed30b7f5b77939c9073348d810730bc4f355708d HEAD && echo BASE_IS_ANCESTOR
BASE_IS_ANCESTOR
$ git log --oneline ed30b7f5b77939c9073348d810730bc4f355708d..HEAD -- SKILL.md
c0b007b round-39: C1 — 14 routed-defect corrections, r39 lesson with Gate/Mistakes, three source rows, gate-registry rows
```

Lane base `ed30b7f`, freeze `b769bfb`, HEAD `2201778`. `SKILL.md` is touched by exactly one commit since
base (`c0b007b`). Working tree is clean for the file:

```
$ git status --porcelain -- SKILL.md
(no output)
$ git diff --stat -- SKILL.md
(no output)
```

So every byte quoted below is committed HEAD bytes, not a sibling's uncommitted edit.

## Check R6-1 — the table and its header shape

Command (run in the lane):

```
$ grep -n '^| name | kind | entry command |' SKILL.md
199:| name | kind | entry command | verdict map (code → class) | self-test command | pinned-value path | write scope | owner |
```

**Verdict: PASS.** The table header is at `SKILL.md:199` and declares **8 columns**:
`name | kind | entry command | verdict map (code → class) | self-test command | pinned-value path | write scope | owner`.
A new row must therefore be a single line with exactly 8 cells between the outer pipes.

Row-count commands (header and `|---|` separator excluded):

```
$ for r in HEAD ed30b7f5b77939c9073348d810730bc4f355708d b769bfb84a264d8b284c09bc211d99f39a3e9126; do printf '%s rows=' "$r"; \
    git show "$r:SKILL.md" | awk '/^\| name \| kind \| entry command \|/{f=1;next} f&&!/^\|/{f=0} f&&/^\|/{c++} END{print c-1}'; done
HEAD rows=81
ed30b7f5b77939c9073348d810730bc4f355708d rows=72
b769bfb84a264d8b284c09bc211d99f39a3e9126 rows=72
```

Duplicate-name scan over the data rows (`NR 201..281`):

```
$ awk 'NR>=201 && NR<=281' SKILL.md | awk -F'|' '{gsub(/^ +| +$/,"",$2); print $2}' | sort | uniq -c | awk '$1>1{print "DUP "$0}'
(no DUP lines)
```

**Verdict: PASS.** 81 data rows at HEAD, 72 at base and at freeze → **+9 rows**, all landed in `c0b007b`.
No first-cell name is duplicated, so the nine additions did not shadow an existing row.

## Check R6-2 — presence of the ten R6 names

Commands, verbatim (loop over the ten names; `exact` anchors the trailing pipe, `prefix` does not):

```
$ for n in r38-citation-commit r38-drift-write-envelope r38-drift-record r38-drift-mutants r38-counter-arms \
    c1-counter c2-counter c3-counter r39-citation-rev r39-drift-record-rules; do \
    printf '%-28s exact=%-2s prefix=%-2s line=%s\n' "$n" \
    "$(grep -cE "^\| *${n} *\|" SKILL.md)" "$(grep -cE "^\| *${n}" SKILL.md)" \
    "$(grep -nE "^\| *${n}" SKILL.md | cut -d: -f1 | tr '\n' ',')"; done
r38-citation-commit          exact=1  prefix=1  line=278,
r38-drift-write-envelope     exact=1  prefix=1  line=279,
r38-drift-record             exact=1  prefix=1  line=280,
r38-drift-mutants            exact=1  prefix=1  line=281,
r38-counter-arms             exact=1  prefix=1  line=251,
c1-counter                   exact=0  prefix=1  line=273,
c2-counter                   exact=0  prefix=1  line=274,
c3-counter                   exact=0  prefix=1  line=275,
r39-citation-rev             exact=1  prefix=1  line=276,
r39-drift-record-rules       exact=1  prefix=1  line=277,
```

Single-pattern confirmation for the nine names added by this round (the nine the freeze did not carry):

```
$ grep -cE '^\| *(r38-citation-commit|r38-drift-write-envelope|r38-drift-record|r38-drift-mutants|c1-counter|c2-counter|c3-counter|r39-citation-rev|r39-drift-record-rules)' SKILL.md
9
```

The same nine names at the **freeze** revision:

```
$ git show b769bfb84a264d8b284c09bc211d99f39a3e9126:SKILL.md | grep -cE '^\| *(r38-citation-commit|r38-drift-write-envelope|r38-drift-record|r38-drift-mutants|c1-counter|c2-counter|c3-counter|r39-citation-rev|r39-drift-record-rules)'
0
$ echo $?
1          (grep: no match, so the freeze carried 0 of the nine)
```

The same names at the **base** revision (`git show ed30b7f...:SKILL.md`, written only to my scratch copy
`/fast/scratch/hyaku/souji-r39/W1ExecRegistry/base-SKILL.md`), prefix grep per name:

```
$ git show ed30b7f5b77939c9073348d810730bc4f355708d:SKILL.md > /fast/scratch/hyaku/souji-r39/W1ExecRegistry/base-SKILL.md
$ for n in r38-citation-commit r38-drift-write-envelope r38-drift-record r38-drift-mutants r38-counter-arms \
    c1-counter c2-counter c3-counter r39-citation-rev r39-drift-record-rules; do \
    printf '%-28s base_prefix=%s\n' "$n" "$(grep -cE "^\| *${n}" /fast/scratch/hyaku/souji-r39/W1ExecRegistry/base-SKILL.md)"; done
r38-citation-commit          base_prefix=0
r38-drift-write-envelope     base_prefix=0
r38-drift-record             base_prefix=0
r38-drift-mutants            base_prefix=0
r38-counter-arms             base_prefix=1     (line 251 at base too)
c1-counter                   base_prefix=0
c2-counter                   base_prefix=0
c3-counter                   base_prefix=0
r39-citation-rev             base_prefix=0
r39-drift-record-rules       base_prefix=0
```

**Verdict: PASS (present, 10/10) — with one named caveat.** All ten names are present at HEAD. Nine are new
in `c0b007b`; `r38-counter-arms` already existed at base (and at freeze). The caveat: `c1-counter`,
`c2-counter` and `c3-counter` are **not exact-token matchable** — their first cell is `c1-counter (r39)`
etc., so `grep -E '^\| *c1-counter *\|'` returns 0 while the prefix form returns 1. A tool or seat that
looks a counter up by exact name will report those three absent. See R6-5 for why this is not a defect.

Cross-check against the lane's own routing note, `SKILL.md:283` (verbatim):

```
R39-C1-06 — four r38 counters had no registry row (r38 routed defect R6): `r38-citation-commit`, `r38-drift-write-envelope`, `r38-drift-record` and `r38-drift-mutants` now carry rows above, beside the five r39 rows this round adds.
```

That note names 4 + 5 = 9 rows, which matches the observed +9 row delta and the nine-name grep count of 9.
The note's arithmetic agrees with the bytes.

## Check R6-3 — column shape of the ten rows

Command:

```
$ awk 'NR>=201 && NR<=281' SKILL.md | grep -E '^\| *(r38-citation-commit|...|r39-drift-record-rules)' \
    | awk -F'|' '{print NF-2" fields: "$2}'
8 fields:  r38-counter-arms
8 fields:  c1-counter (r39)
8 fields:  c2-counter (r39)
8 fields:  c3-counter (r39)
8 fields:  r39-citation-rev
8 fields:  r39-drift-record-rules
8 fields:  r38-citation-commit
8 fields:  r38-drift-write-envelope
8 fields:  r38-drift-record
8 fields:  r38-drift-mutants
```

**Verdict: PASS.** Every one of the ten rows carries exactly 8 cells, matching the 8-column header — no cell
spilled, no cell merged, no unescaped `|` inside a cell. All ten carry `kind=gate`.

Shape audit of the whole table (`|`-split field histogram over every pipe line after the header):

```
{8: 80, 9: 1, 2: 10}
```

The single 9-field line is `SKILL.md:244` (`r22-result-oracle`), which contains a **properly escaped** literal
pipe (`\| python3 -B census/round-22/mutation-adequacy.py --grade-stdin`) — a naive split artifact, not a
broken row. The 2-field lines are five rows of a *different, later* two-column table plus its header/separator
(`SKILL.md:316-320`), outside the gate registry. **No residual shape defect found.**

## Check R6-4 — entry commands resolve to real files

```
$ for f in census/round-39/c1-counter.py census/round-39/c2-counter.py census/round-39/c3-counter.py \
    tests/fixtures/r39-citation-rev.py tests/fixtures/r39-drift-record-rules.py \
    tests/fixtures/r38-citation-commit.py tests/fixtures/r38-drift-write-envelope.py \
    tests/fixtures/r38-drift-record.py tests/fixtures/r38-drift-mutants.py \
    tests/fixtures/r38-counter-arms.py; do \
    if [ -f "$f" ]; then printf 'PRESENT %s\n' "$f"; else printf 'MISSING %s\n' "$f"; fi; done
PRESENT census/round-39/c1-counter.py
PRESENT census/round-39/c2-counter.py
PRESENT census/round-39/c3-counter.py
PRESENT tests/fixtures/r39-citation-rev.py
PRESENT tests/fixtures/r39-drift-record-rules.py
PRESENT tests/fixtures/r38-citation-commit.py
PRESENT tests/fixtures/r38-drift-write-envelope.py
PRESENT tests/fixtures/r38-drift-record.py
PRESENT tests/fixtures/r38-drift-mutants.py
PRESENT tests/fixtures/r38-counter-arms.py
```

**Verdict: PASS.** Each row's entry-command target exists in the lane at HEAD. `census/round-39/` holds
exactly three counters (`c1-counter.py`, `c2-counter.py`, `c3-counter.py` — `ls -1 census/round-39/` plus
`make-cells.py`), so no fourth counter is unregistered.

## Check R6-5 — does any consumer parse row names? (operability of the `(r39)` suffix)

```
$ grep -rn "entry command" --include=*.py --include=*.sh tools/ tests/ census/ 2>/dev/null | head -20; echo "rc=$?"
census/round-26/waves/make-spec.py:170: ... matching the existing table's column shape (name/kind/entry command/verdict map/
census/round-27/waves/make-spec-r27.py:283: ... a gate-registry row for `souji-pre-report-gate` (entry command, verdict map, ...
```

Both hits are round-26/27 wave *prompt text*, not parsers. The only tool that reads this table's cells is
`tools/souji-landing-gate.py`, and it is **path-based, name-agnostic**:

```
tools/souji-landing-gate.py:89
CITED_PATH_RE = re.compile(
    r"(?:tools|tests/fixtures|census/round-\d+)/[A-Za-z0-9_.-]+\.(?:sh|py)"
```

`tools/souji-registry-agreement.py` parses a different table — `corpus/SOURCES.md`, 13 columns,
`raise RuntimeError('malformed registry row: ...')` — and never touches the `SKILL.md` gate registry.

**Verdict: PASS with an advisory.** No consumer keys on the registry first cell, so `c1-counter (r39)` cannot
silently break a gate, and the suffix has in-table precedent — `SKILL.md:237`,
`r21-acceptance (r22 result-contract repair)`. The advisory for the L1: a human or ad-hoc `grep` for the bare
token returns 0 for the three r39 counters (R6-2 caveat). If the round wants exact-token lookup, the names
would have to be `c1-counter`, `c2-counter`, `c3-counter` without the parenthetical — but that would break the
existing r21 convention and is **not** an evidence-backed defect today.

## Two nearest existing rows, verbatim, as column-shape templates

These are the last two pre-existing rows immediately above the appended block (`SKILL.md:271` and `:272`).
They are reproduced byte-for-byte; each has 8 cells.

```
| r34-c1-counter | gate | `python3 -B census/round-34/c1-counter.py --root LANE --rev REV --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 --scratch DIR [--only G01,...]` | 0 `SUMMARY items=60 agree=60 mismatches=0`; 1 any item MISMATCH/BAD-ROW/BAD-CAUSE/RUN-FAILED; 2 could-not-evaluate (invalid or missing revision/input, non-persistent scratch root, malformed items, failed clone). The target was not reached: base control `agree=35 mismatches=25`; W1 proved frozen unreachable predicates/cause bindings, including G05/G17b/G24/E23b. A targeted counter row may be diagnostic only; `--only`/`partial=1` is never a gate pass | `python3 -B census/round-34/c1-counter.py --selftest` is a literal tripwire only; the behavioral forged-row control is `python3 -B tests/fixtures/r34-c1-junk.py --counter census/round-34/c1-counter.py --scratch DIR` (`cases=3 pass=3 control=STUB-REJECTED`, frozen-control revision only) | frozen item set `census/round-34/c1-items.tsv` at list revision 2b0171e; base and control receipts in `census/round-34/records/controls.txt`; append-only valid corrections at `SCORECARD.md` `### Round 34 registry restatements`; overall target remains unmet | read-only lane input; one clone per selected item under caller scratch, origin removed, detached; Q77 lock under scratch | souji |
| r34-c2-counter | gate | `python3 -B census/round-34/c2-counter.py --root LANE --rev REV --base 9c76c7222a8abff027af42e37f0d160d52526bba --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 --scratch DIR` | 0 `SUMMARY legs=13 pass=13 fail=0 harm=0`; 1 any LEG not PASS; 2 could-not-evaluate (invalid revisions, absent/malformed legs, unavailable bwrap/strace, ephemeral scratch, clone failure). Repaired feasibility is red: `legs=13 pass=9 fail=4 harm=0` (W2, W3, N3, J1 fail); no C2 pass is claimed | `python3 -B census/round-34/c2-counter.py --selftest` behaviorally refuses witness-dropped/junk-less legs; J1 fixture `python3 -B tests/fixtures/r34-sandbox-junk.py --counter census/round-34/c2-counter.py --scratch DIR` timed out at 900 s, not a pass | frozen legs `census/round-34/c2-legs.tsv`; re-pinned counter 2b0171e; feasibility and junk outcomes in `census/round-34/records/controls.txt` | private per-leg clones, bwrap sandbox with TMPDIR and private `/var/tmp` bind; real `/var/tmp` canary checked for N3; lane working tree read-only | souji |
```

Column shape these two establish, cell by cell: `name` (bare id, optional parenthetical) · `kind`
(`gate`|`probe`|`evidence`) · `entry command` (backticked, absolute-from-lane relative path, `LANE`/`REV`
placeholders) · `verdict map` (`0 …; 1 …; 2 …` in that order, with literal summary strings and refusal
classes named) · `self-test command` · `pinned-value path` · `write scope` · `owner` (`souji`).

## Verdicts

| check | what it asserts | verdict |
|---|---|---|
| R6-1 | header at `SKILL.md:199`, 8 columns; 81 data rows at HEAD vs 72 at base/freeze; no duplicate names | **PASS** |
| R6-2 | all ten R6 names present at HEAD; nine new in `c0b007b`, freeze carried 0 of them; `r38-counter-arms` pre-existing | **PASS** |
| R6-3 | each of the ten rows has exactly 8 cells, `kind=gate`; no shape defect in the table | **PASS** |
| R6-4 | every entry-command target exists; exactly three r39 counters, all registered | **PASS** |
| R6-5 | no consumer parses row names; `(r39)` suffix has precedent (`SKILL.md:237`); bare-token grep misses the three counters | **PASS, advisory** |

Net: **R6 is closed in lane bytes at HEAD `2201778`** — the four r38 rows the routing named are present, the
five r39 rows are present, and all ten rows are well-formed 8-cell `gate` rows whose entry targets exist.
No absence found; the only finding is the exact-token naming caveat, which is convention-consistent and
breaks no consumer.

## Risks / notes

- The nine rows exist only from `c0b007b` onward; at the freeze `b769bfb` the set is empty. Any C1 leg that
  measures the registry at `--rev` with a revision at or before the freeze will read them absent — expected,
  but the counter's `--rev` must be the landing revision.
- Advisory items do not change the frozen contract: I did not run `c1-counter.py`, `c2-counter.py`,
  `c3-counter.py` or any fixture. Presence was measured by grep and `[ -f ]`, not by executing the gates;
  whether each row's verdict map matches its tool's real behaviour is C1/C2/C3's claim, not mine.
- Scratch: `/fast/scratch/hyaku/souji-r39/W1ExecRegistry/` was created only to hold the extracted base
  `SKILL.md`; it was removed before this report was finished (`rm -rf` verified — no tree left on disk).
- No tool installed or upgraded this seat. No mutating git command was run: the only git calls were `rev-parse`,
  `merge-base --is-ancestor`, `log`, `show`, `status`, `diff`.
