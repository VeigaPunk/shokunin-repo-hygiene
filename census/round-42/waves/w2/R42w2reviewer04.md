# R42w2reviewer04 — C2 operability review (falsify lane)

Seat: `R42w2reviewer04` (reviewer). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Base `bf618f6c5c09d302994871c94903abbea2deb60d`; freeze `afe17f416eec04dcf3f480b580a8f928de61d19d`;
landed tip under attack `3105a63b23481fccf7df58e74d14a6681e0ea0c8`.
Axis judged: **operability (C2)**. Milestone: r42 falsify the landed artifacts.

No tracked file was edited. Every frozen artifact (preregistration, `census/round-42/c2-counter.py`,
`census/round-42/c2-cases.tsv`, `census/round-42/controls/c2-control.txt`, the pinned
`tools/souji-worktree-drift.py`) was read only. The only writes are this report and
`.ufo/waves/round-42/w2/R42w2reviewer04/receipts/` under this seat's own directory.

**Receipts kept in this seat directory** (all scratch under `/fast/scratch/hyaku/souji-r42/R42w2reviewer04/`
was deleted after copying):

| receipt | content |
|---|---|
| `receipts/c2-counter-run1.log` … `-run3.log` | the three independent C2 counter runs at the tip (§1.1) |
| `receipts/prereg-sweep-all-rounds.txt` | the tool over every `census/round-*/preregistration.txt` at the tip (§1.3) |
| `receipts/probe7-heading-boundary.txt` | the HEADING-MALFORMED block-boundary probes A–D (F-1) |
| `receipts/probe6-post-freeze-edits.txt` | the post-freeze Control and preregistration edits (F-2), with the blob digests at each revision |

---

## 1. Commands actually run (verbatim) and their output

### 1.1 C2 counter re-measured three times at the tip

```
$ mkdir -p /fast/scratch/hyaku/souji-r42/R42w2reviewer04/m1 m2 m3
$ for i in 1 2 3; do
    TMPDIR=/fast/scratch/hyaku/souji-r42/R42w2reviewer04/m$i \
    python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/c2-counter.py \
      --root /home/vgpnk/Projects/shokunin/souji-shokunin \
      --rev 3105a63b23481fccf7df58e74d14a6681e0ea0c8 \
      --scratch /fast/scratch/hyaku/souji-r42/R42w2reviewer04/m$i > run$i.log 2>&1
  done
```

Three runs, all `exit=0`, all byte-identical SUMMARY lines (receipts
`receipts/c2-counter-run1.log`, `-run2.log`, `-run3.log`):

```
run1 exit=0
run2 exit=0
run3 exit=0
```

Each run's SUMMARY line, verbatim and identical across the three runs:

```
SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=9ddd596b98fb
```

Per-leg lines from each run (identical in all three):

```
real ok rc=0 findings=0 summary=(3, 0)
retro red rc=1 findings=19 summary=(3, 19)
retro_clean ok rc=0 findings=0 summary=(3, 0)
selftest ok rc=0 summary=(31, 31, 0)
```

`tool_sha=9ddd596b98fb` matches the tip blob: `git show 3105a63…:tools/souji-freeze-check.py | sha256sum`
→ `9ddd596b98fbf41b67f98a389c488b1e84d2ef4a7b5fdb0c8711451a007acec6`, and the worktree file hashes
identically (`sha256sum tools/souji-freeze-check.py` → same digest). **The tool measured at the tip is
the tool in the worktree.** No rerouting between runtime identities was observed.

**Verdict on re-measurement: the C2 target is met at the tip, deterministically (3/3 identical runs).**

### 1.2 The tool's own `--selftest`

```
$ TMPDIR=/fast/scratch/hyaku/souji-r42/R42w2reviewer04 \
  python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-freeze-check.py --selftest
SELFTEST cases=31 pass=31 fail=0
selftest exit=0
```

stderr was empty (0 bytes) on the unpatched run. Its case list (parsed from `CASES` at
`tools/souji-freeze-check.py:241-274`, 31 entries):

| # | case | # | case | # | case | # | case |
|---|---|---|---|---|---|---|---|
| 1 | clean | 9 | base-not-ancestor | 17 | frozen-edited | 25 | heading-spaced |
| 2 | dispatch-after | 10 | counter-missing | 18 | dispatch-before | 26 | heading-suffix |
| 3 | notes-before | 11 | counter-digest | 19 | dispatch-attempts | 27 | heading-valid-tail |
| 4 | sub-heading | 12 | population-missing | 20 | dispatch-ready | 28 | counter-symlink |
| 5 | no-claims | 13 | population-digest | 21 | dispatch-results | 29 | population-symlink |
| 6 | field-missing | 14 | population-empty | 22 | key-duplicate | 30 | rev-unresolved |
| 7 | field-empty | 15 | control-missing | 23 | heading-nospace | 31 | prereg-absent |
| 8 | base-unresolved | 16 | control-not-red | 24 | heading-lowercase | | |

The three runtime patches were re-run directly (not via the counter) to confirm each leg is a real
detection and not a crash: `PYTHONPATH=<patchdir> SOUJI_R42_PATCH=P1|P2|P3 python3 -B tools/souji-freeze-check.py --selftest`:

```
P1: SELFTEST cases=31 pass=3  fail=28   exit=1
P2: SELFTEST cases=31 pass=2  fail=29   exit=1
P3: SELFTEST cases=31 pass=5  fail=26   exit=1
```
All three fail **named cases** (e.g. `selftest FAIL dispatch-attempts`, `selftest FAIL counter-symlink`)
— the selftest detects the patched digest / freeze-detection / ancestry logic rather than crashing.

### 1.3 The tool over every `census/round-*/preregistration.txt` at the tip

```
$ for r in 33 34 35 36 37 38 39 40 41 42; do
    python3 -B tools/souji-freeze-check.py --root <lane> \
      --prereg census/round-$r/preregistration.txt --rev 3105a63b23481fccf7df58e74d14a6681e0ea0c8
  done
```

Full output preserved at `receipts/prereg-sweep-all-rounds.txt`. Tabulated:

| round | exit | claims | findings | verdict | why (structural cause, measured) |
|---|---|---|---|---|---|
| 33 | 1 | 0 | 2 | **red** | no `Round:` line (0 matches of `^\ufeff?Round:[ \t]*\d+`); no `## C<digits>` heading (uses `== C1 …`) → `FIELD-MISSING C0 Round` + `NO-CLAIMS` |
| 34 | 1 | 0 | 2 | **red** | same two findings (0 `Round:` lines, 0 `## C<digits>` headings) |
| 35 | 1 | 0 | 2 | **red** | same two findings (0 `Round:` lines; headings are `## Claims`, not `## C<digits>`) |
| 36 | 1 | 0 | 2 | **red** | same two findings |
| 37 | 1 | 0 | 2 | **red** | same two findings |
| 38 | 1 | 0 | 2 | **red** | same two findings (`## Claims` + `### C1 —` sub-headings) |
| 39 | 1 | 0 | 2 | **red** | same two findings (`## Claims` + `### C1 —`) |
| 40 | 1 | 3 | 19 | **red** | `FIELD-MISSING C0 Round` + 3 claims × 6 missing keys = 19. Its headings *are* `## C1/C2/C3 —` (3 claims parsed), but its key lines are prose (`Predicate:`, `Target: …` inside a sentence) not `Key: value` at column 0 → all six keys missing per claim |
| 41 | 0 | 3 | 0 | clean | r41 grammar: `Round: 41`, 3 `## C<digits>` headings, 23 key lines at column 0 |
| 42 | 0 | 3 | 0 | clean | r42 grammar, same shape |

**Reading the red rounds.** The reds are *grammar* reds, not freeze reds: the tool applies the r41/r42
grammar (`## C<digits>` heading, `Round:` line, `Key: value` at column 0) to files written before that
grammar existed. Rounds 33–39 predate the `## C<digits>`/`Round:` convention entirely (0 `## C<digits>`
headings and 0 `Round:` lines each, measured); rounds 38–39 use `## Claims` + `### C1 —`; round 40 has
the heading shape but keeps its keys inside prose sentences. No round 33–40 file is red for a
*substantive* freeze reason (no `COUNTER-DIGEST`, no `FROZEN-EDITED`, no `DISPATCH-BEFORE-FREEZE`).

This matters for the counter's `retro` leg, which targets round 40 and expects "red, ≥3 findings": the
round-40 red is 19 × `FIELD-MISSING` + `FIELD-MISSING C0 Round`, i.e. a grammar-shape red. It is the
*right* answer for a pre-grammar file but it does not evidence that the tool detects a genuine
freeze-ordering violation. Round 41 (`retro_clean`) is the first file in the corpus written in the
grammar, and it reads clean — so the r42 preregistration's `retro=red / retro_clean=ok` pair is
satisfied by one grammar-mismatch file and one grammar-conformant file.

---

## 2. The tool against the grammar in the `c2-counter.py` docstring

The authority is the docstring of `census/round-42/c2-counter.py` (lines 1–56), not the tool's own
docstring. Its r42 additions, verbatim:

> `KEY-DUPLICATE` a key line appears more than once in one claim block (identical value or not);
> one finding per duplicated key (detail: the key). First-wins reading is gone.
> `HEADING-MALFORMED` a line at column 0 that starts `##` (and not `###`), then optional spaces, then
> `C` or `c`, optional spaces, a digit, and does not match `## C<digits>` followed by a space or end of
> line (`##C1`, `## c1`, `## C 1`, `## C1x`). Claim label C0, one finding per such line (detail:
> line=<n>); the line opens no claim.
> `COUNTER-SYMLINK` the Counter path is a symlink (git mode 120000) at FREEZE-REV: this finding alone,
> no digest comparison is made (the link text is not the counter)
> `POPULATION-SYMLINK` the same for the Population path
> `DISPATCH-BEFORE-FREEZE` now covers every file under `.ufo/waves/round-<N>/` (any depth) whose basename
> contains `-dispatch` or `.ready`, or ends `-spec.json` or `-results.json`, and was first added by
> FREEZE-REV or an ancestor of it

Tool file: `tools/souji-freeze-check.py` (375 lines, sha256 `9ddd596b98fbf41b67f98a389c488b1e84d2ef4a7b5fdb0c8711451a007acec6`).

### 2.1 Class-by-class table

| class | docstring clause | implemented where | matches docstring? |
|---|---|---|---|
| NO-CLAIMS | r41 class, prereg-wide label C0 | `tools/souji-freeze-check.py:181` | **yes** |
| FIELD-MISSING | r41 class; `C0 Round` for a missing `Round:` line | `:186` (per-key), `:128` (C0 Round) | **yes** — the `Round` special case is at `:128` inside `dispatch_findings`, matching the r41 tool |
| FIELD-EMPTY | r41 class | `:191` | **yes** |
| BASE-UNRESOLVED | r41 class | `:196` | **yes** |
| BASE-NOT-ANCESTOR | r41 class (strict ancestor of freeze) | `:198` | **yes** — `resolved == freeze` is also rejected (strict) |
| COUNTER-MISSING | r41 class | `:159` (via `check_path_sha`) | **yes** |
| COUNTER-DIGEST | r41 class | `:165-167` | **yes** |
| POPULATION-MISSING | r41 class | `:159` | **yes** |
| POPULATION-DIGEST | r41 class | `:165-167` | **yes** |
| POPULATION-EMPTY | r41 class (<2 non-blank lines) | `:209` | **yes** |
| CONTROL-MISSING | r41 class | `:215` | **yes** |
| CONTROL-NOT-RED | r41 class (last line `EXIT=<nonzero>`) | `:220` | **yes** |
| FROZEN-EDITED | r41 class (blob differs freeze→rev) | `:170-171`, **only for the Counter/Population paths** | **partly** — see F-2: the Control path is never compared |
| DISPATCH-BEFORE-FREEZE (r41 shape) | r41 class | `:123-148` | **yes** |
| DISPATCH-BEFORE-FREEZE (r42 names) | basename contains `-dispatch`/`.ready`, or ends `-spec.json`/`-results.json` | `:141` | **yes** for the name set — but see F-3 for "any depth" |
| KEY-DUPLICATE | one finding **per duplicated key**; detail = the key; first-wins reading gone | `:183` (per key, `sorted(dups)`) + `:109-110` (`:109` tests presence, `:110` adds the key to the `dups` set) + `:188` (`del f[key]`) | **yes** — verified below |
| HEADING-MALFORMED | label C0, one per line, detail `line=<n>`, opens no claim | `:102-105` (collect) + `:179` (emit) + `:103` (`cur = None`) | **yes** for the label/detail/no-claim clauses; see F-1 for the block-boundary clause the docstring does not define |
| COUNTER-SYMLINK | symlink at FREEZE-REV ⇒ this finding alone, no digest comparison | `:86-88` (`ls-tree` mode 120000) + `:161-162` (emit + `return None`) | **yes** — "this finding alone" holds: the `return None` at `:162` precedes the digest compare at `:165` and the FROZEN-EDITED compare at `:170` |
| POPULATION-SYMLINK | same for Population | same code path, `:161-162` | **yes** |
| *(exit codes)* | 0 = no findings, 1 = findings, 2 = could-not-evaluate (`REFUSAL COULD-NOT-EVALUATE: …`) | `:371` (`return 1 if lines else 0`), `:364-366` (refusal → 2) | **yes**, plus an undocumented third path: argparse usage errors also exit 2 (`:347`, see F-4) |

### 2.2 Clauses the docstring defines but the 37 counter cases do not pin

I mutated the landed tool and re-scored it against the **frozen** counter (score only — the counter
and the tool were not edited in the lane; the mutants were written to
`/fast/scratch/hyaku/souji-r42/R42w2reviewer04/variants*/` and scored with the counter's own
`score_tool`).

| mutant | what it violates | frozen counter verdict |
|---|---|---|
| `last-wins-evaluated` (overwrite the value with the last occurrence) | docstring: "First-wins reading is gone" — a last-wins reading must not survive | **36/37 → REJECTED** (`dup-base-differs` fails) — pinned |
| `first-wins-evaluated` (keep the first occurrence's value and evaluate it) | — | **37/37, and the FULL counter target met** (`exit=0`, `cases=37 pass=37 … selftest=ok patches=3/3`) — **NOT pinned** |
| `malformed-opens-claim` (a malformed heading also opens a claim) | docstring: "the line opens no claim" | **33/37 → REJECTED** — pinned |
| `malformed-does-not-close-block` (a malformed heading does not end the open claim block) | docstring is **silent** on the block boundary | **37/37 and full target met** — see F-1 |
| `symlink+digest` (a symlinked Counter also gets a digest finding) | docstring: "this finding alone" | **35/37 → REJECTED** — pinned |
| `symlink+also-population-empty` (a symlinked Population also gets POPULATION-EMPTY) | docstring: "this finding alone" | **36/37 → REJECTED** — pinned |
| `symlink+also-frozen-edited` (a symlink also gets FROZEN-EDITED) | docstring: "this finding alone" | **37/37 and full target met** — **NOT pinned** |
| `dispatch-r41-names-only` (r41 name set only) | docstring: r42 name set | **33/37 → REJECTED** — pinned |
| `dispatch-depth1-only` (dispatch names matched only at depth 1) | docstring: "any depth" | **37/37 on the cases but the FULL counter target FAILS** (`selftest=FAIL patches=0/3`) — pinned by the *tool's own selftest*, not by the counter's cases |
| `keydup-per-occurrence` (one finding per occurrence, not per key) | docstring: "one finding per duplicated key" | **34/37 → REJECTED** — pinned |
| `heading-detail-text` (detail `line=<n> text` instead of `line=<n>`) | docstring: "detail: line=<n>" | **37/37 and full target met** — **NOT pinned** (the counter matches only `FINDING (\S+) (\S+)` — `census/round-42/c2-counter.py:262` — i.e. claim+class, never the detail) |
| `frozen-edited-covers-control` (FROZEN-EDITED extended to the Control) | docstring silent | **37/37 and full target met** — **NOT pinned** (see F-2) |

**Reading:** the counter pins the *class multiset* of every finding, and it pins the two most
load-bearing r42 semantics (last-wins is rejected; a malformed heading opens no claim; the symlink
"finding alone" is rejected when a digest/emptiness finding is added). It does **not** pin finding
*detail* text, it does not pin the block-boundary reading of a malformed heading, and it does not pin
whether FROZEN-EDITED covers the Control. The `dispatch-depth1-only` mutant shows the depth clause is
enforced only by the tool's own `--selftest`, which the tool itself writes — the frozen counter's 37
cases would pass it.

---

## 3. Findings

### F-1 (medium) — HEADING-MALFORMED's effect on the open claim block is undefined in the docstring and unpinned by the counter

The docstring defines HEADING-MALFORMED only as "one finding per such line (detail: line=<n>); the
line opens no claim." It says nothing about whether the malformed line **ends** the claim block that
was open before it. The landed tool ends it (`tools/souji-freeze-check.py:102-103`, `cur = None`).

Measured behaviour, on a synthetic repo (`/fast/scratch/hyaku/souji-r42/R42w2reviewer04/probe7`).
The preregistration is always `Round: 42` + a complete `## C1 - one` block (Base/Counter/Population/
Control), then the heading under test, then `Target: after-heading` and `Kill: k` — so any
`FIELD-MISSING Target` means the two trailing keys were orphaned from C1:

```
--- A ##C2 (malformed)        FINDING C0 HEADING-MALFORMED line=7
                              FINDING C1 FIELD-MISSING Kill
                              FINDING C1 FIELD-MISSING Target
--- B ## C (space, no digit)  FINDING C1 FIELD-MISSING Kill
                              FINDING C1 FIELD-MISSING Target
--- C ##C (no space,no digit) SUMMARY claims=1 findings=0
--- D ## C2 (valid)           FINDING C1 FIELD-MISSING Kill
                              FINDING C1 FIELD-MISSING Target
                              FINDING C2 FIELD-MISSING Base / Control / Counter / Population
```

Reading A: the malformed heading both closes C1 **and** discards the two keys that follow it — they are
attributed to no claim at all. So the finding set for A is identical to B's plus the HEADING-MALFORMED
line. A tool that instead *keeps* the block open scores 37/37 and the full target (see the mutant
table in §2.2), so the counter cannot tell the two readings apart.

Reading B vs C is a second, subtler asymmetry that the docstring also does not define. The malformed
pattern is `BADHEAD = re.compile(r"^##(?!#) *[Cc] *\d")` (`:45`) — it requires a **digit**. So `## C`
(space, no digit) and `##C` (no space, no digit) are *not* HEADING-MALFORMED. But B still loses both
trailing keys while C loses none: `## C` matches the `:102` `line.startswith("## ")` arm and so closes
the block, whereas `##C` matches no arm at all and is treated as ordinary body text, leaving C1 open.
Neither raises HEADING-MALFORMED. The docstring defines the class as requiring a digit, so both are
legitimately "not malformed" — but the *block-boundary* consequence is then unspecified and
inconsistent between the two spellings of the same intended heading.

(D, the valid `## C2`, is the contrast: it opens a second claim C2 with all six keys missing, and C1
keeps neither trailing key.)

This is the same defect `R42reviewer02` N1 named in wave 1 ("the docstring says only 'the line opens
no claim' … the cases do not exercise this, because the malformed line is always last"). It remains
open at the tip and is carried into the landed tool's own docstring as a silent choice
(`tools/souji-freeze-check.py:22-23` says "opens no claim" and says nothing about closing).

**What it attacks:** the C2 operability claim's grammar fidelity — the docstring is the frozen
specification of the tool's behaviour, and this clause is neither defined nor checked.
**For the L1:** the docstring is frozen; a name is needed in the round-42 lesson's N-C2c block, or the
docstring gap must be recorded as a named limit. The tool's behaviour is not wrong; it is unspecified.

### F-2 (medium-high) — FROZEN-EDITED covers only Counter and Population; a post-freeze edit of the Control is invisible

`check_path_sha` (`:151-173`) compares the FREEZE blob with the REV blob and raises FROZEN-EDITED at
`:170-171`. That function is called only for `Counter` (`:201-202`) and `Population` (`:204-205`). The
Control is read at `:213-214` — `blob = repo.blob(freeze, path)` — and **only at FREEZE**. The Control is
never fetched at REV, so a Control changed after the freeze commit cannot be detected.

Measured (`/fast/scratch/hyaku/souji-r42/R42w2reviewer04/probe6`, a synthetic repo whose freeze
commit is the commit that added the preregistration):

```
=== A) clean at freeze:                       SUMMARY claims=1 findings=0   exit=0
=== B) EDIT THE CONTROL after the freeze commit:
                                               SUMMARY claims=1 findings=0   exit=0   <-- no FROZEN-EDITED
=== C) EDIT THE PREREGISTRATION itself after the freeze commit:
                                               SUMMARY claims=1 findings=0   exit=0   <-- the edited prereg is parsed as if frozen
```

The tool's own docstring is silent on the scope (`tools/souji-freeze-check.py:14-17` lists
FROZEN-EDITED with no path scope), so this is not a docstring mismatch — but it is a real operability
gap against the round's own rule 1, which freezes the **Control** as well as the Counter and
Population ("No Counter, Population, Control, pinned tool, or this file changes after the freeze
commit", `census/round-42/preregistration.txt` line 20). The tool cannot witness the Control half of
that rule.

The same probe shows a second, sharper consequence: **editing the preregistration itself after the
freeze commit is invisible.** `freeze_rev` (`:116-121`) finds the oldest commit that *adds* the
preregistration path, and `evaluate` then parses the blob at **REV** (`:357`, `:363`), not at the freeze
commit. A preregistration rewritten after its own freeze is parsed as if it were the frozen one — the
tool's freeze check is defeated by editing the very file it is checking.

The counter cannot see either gap: the mutant that extends FROZEN-EDITED to the Control scores 37/37
and the full target (§2.2).

**What it attacks:** C2 operability — the tool's ability to witness the freeze rule it exists to
enforce. This is the r41 N13 defect family ("a symlink Counter reads the link text") in a new place.
**For the L1:** the counter is frozen and its 37 cases cannot be extended; this is a named limit for
the round lesson, and it is the same class as R42-N-C2c (counter expectations do not pin a docstring
clause).

### F-3 (low) — the "any depth" clause of the widened DISPATCH-BEFORE-FREEZE is enforced only by the tool's own selftest

The docstring: "covers every file under `.ufo/waves/round-<N>/` (**any depth**)". The tool matches
basenames at whatever depth `git log --name-only` returns (`:140-141`), so the tool implements the
clause correctly. But the counter's 37 cases exercise dispatch names only at depth 1
(`.ufo/waves/round-42/w1-spec.json` etc.), so a depth-1-only tool passes all 37 cases. It fails only
the counter's `selftest` leg, because the tool's *own* `CASES` table contains a depth-2 case
(`tools/souji-freeze-check.py:262-263`, `.ufo/waves/round-7/a/w1.ready.dispatched`).

So the depth clause is pinned, but by a table the candidate writes itself rather than by the frozen
instrument. A candidate that shipped a selftest without the depth-2 case, and a depth-1-only dispatch
check, would pass the counter's 37 cases and the selftest leg (n ≥ 12 is the only requirement).

**What it attacks:** the frozen counter's coverage of the docstring's r42 dispatch clause — the same
"the expectation pins a reading the docstring does not state" gap `R42critic02` K8 flagged for the
symlink-emptiness case.

### F-4 (low) — exit code 2 is overloaded: argparse usage errors and could-not-evaluate share it

The docstring assigns exit 2 to could-not-evaluate, signalled by `REFUSAL COULD-NOT-EVALUATE: …` on
stderr. The tool's `main` does that correctly (`:364-366`), but argparse's own usage error also exits
2 (`:347`):

```
$ python3 -B tools/souji-freeze-check.py --prereg x --rev <40-hex>
souji-freeze-check.py: error: --root, --prereg and --rev are required (or --selftest)
usage exit=2
```
versus
```
REFUSAL COULD-NOT-EVALUATE: --rev 0000000000000000000000000000000000000000 does not resolve to a commit in .
refusal exit=2
```
A caller that keys on the exit code alone cannot tell "could not evaluate" from "you invoked me
wrong". The counter's `two_unresolved` leg (`census/round-42/c2-counter.py:277-282`) checks for the
`COULD-NOT-EVALUATE` string, so
the counter is not fooled — but the docstring's exit-code table is incomplete.

### F-5 (informational, positive) — the tool's `--selftest` is hermetic: own env, own identity, `commit-tree` for the non-ancestor case

The selftest constructs its own env (`:283-285`) with `HOME=tmp`, `GIT_CONFIG_GLOBAL=/dev/null`,
`GIT_CONFIG_NOSYSTEM=1` and explicit author/committer identity, and every git call is `-C <d>`. It
uses `commit-tree` for the non-ancestor case (`:306`) rather than a branch, so no branch or ref is
left behind. Verified: the selftest leaves no file in the working tree and no stderr output when
unpatched (0 bytes).

One note for the L1's Q105 row: the selftest is executed in-process (`main` is called via
`contextlib.redirect_stdout`, `:312`), so the `sitecustomize` patch reaches it — this is why
`patches=3/3` is a real leg and not a vacuous one. Confirmed independently in §1.2.

### F-6 (informational) — the C2 counter does not read its own declared Population file

`census/round-42/c2-cases.tsv` (sha256 `148b7b87…`, pinned in the preregistration as the C2
Population) is never opened by `census/round-42/c2-counter.py`: the case set lives in the Python
`CASES` tuple (`census/round-42/c2-counter.py:212-259`) and the two refusal legs are added by `two_unresolved` (`:277-282`). The
TSV's 37 rows correspond exactly to the 35 tuple entries plus `unresolved-rev` and `absent-prereg`
(verified by diffing the names), so the two agree today — but the TSV is documentation, not a
measurement input, and a divergence between them would go unnoticed. The C1 and C3 counters *do* read
their population files (`c1-counter.py:56` `ITEMS = "census/round-42/c1-items.tsv"`;
`c3-counter.py:49` `POPULATION = "census/round-42/c3-mutants.tsv"`, checked at `c3-counter.py:190-193`
against the declared digests). The C2 counter has no equivalent population-integrity leg.

**What it attacks:** the C2 population's binding to its counter. Not a landed-tool defect; a
counter-instrument asymmetry the L1 should know about (the C3 counter has a `population=` check, C2
does not).

---

## 4. Residual risk and verification gaps

1. **The counter's 37 cases are a closed public set.** This was named in wave 1 (`N-C2a`) and holds at
   the tip: every r42 clause I could mutate was either pinned (5 of 12 mutants rejected) or not
   (7 of 12 accepted, listed in §2.2). The counter's own docstring says the 37 cases are "the 21 r41
   cases plus 16 new"; the tuple holds 35 entries plus the 2 refusal legs, and the TSV holds 37 rows —
   the counts reconcile.
2. **The `patches=3/3` leg is a leg-level proof** (`N-C2b`): the environment-aware stub of
   `R42sentinel02` reaches the target, and a crash counts as a rejection. I confirmed the landed
   tool's selftest *names* the failing cases under each patch rather than crashing, but I did not
   test whether a crash would also be accepted — the counter's rule (`p_rc not in (0, 124)`,
   `census/round-42/c2-counter.py:410`) accepts
   any non-zero, non-124 exit, including a traceback exit 1.
3. **The `real=ok` leg is thin.** It runs the tool over the round's own preregistration at the tip and
   requires `claims=3 findings=0`. Both the r42 and r41 preregistrations are written in the tool's own
   grammar, so this is a self-consistency check, not an independent measurement of the tool.
4. **`retro=red` is a grammar red**, as tabulated in §1.3. It exercises the "unknown grammar" path, not
   the dispatch-timing path.
5. **I did not re-run `score-candidate.sh`** for C2: there is no candidate to score — the tool is
   landed, and the counter measures it directly at `--rev`. The three runs in §1.1 are the measurement.
6. **The dispatch clause cannot be witnessed in this lane**, because `.gitignore` line 1 ignores
   `.ufo/waves/` and the r42 wave files are untracked (`git ls-files .ufo/waves/round-42/` → empty).
   The clause is exercised only by the synthetic fixtures. This is the r41 `R41w2critic07` F4 defect,
   unchanged.
7. **The `HEADING-MALFORMED` block-boundary reading (F-1) and the Control/prereg freeze-edit blindness
   (F-2) are not observable in the C2 target** — neither moves the counter off `pass=37`. They are
   quality defects in the landed tool, not claim misses. The C2 claim's kill conditions
   ("any case fail, either built-in stub accepted, real not ok, retro not red, retro_clean not ok,
   selftest not ok, or fewer than 3 patches rejected") are all satisfied.

---

## 5. Verdict

**C2 (operability) holds at the tip: the claim is met, and the tool implements the counter docstring's
grammar faithfully on every class the docstring names.**

- The frozen counter reads `cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED
  real=ok retro=red retro_clean=ok selftest=ok patches=3/3` on **three consecutive independent runs**,
  exit 0, byte-identical SUMMARY lines, with `tool_sha=9ddd596b98fb` matching the tip blob and the
  worktree file.
- The tool's own `--selftest` runs 31 cases, all passing, exit 0; each of the three runtime patches
  makes it fail **named** cases (28/29/26 failures), so the digest, freeze-detection and ancestry
  legs are genuinely exercised.
- Reading the tool against the docstring class by class: all 18 named classes are implemented, with
  the tool's line numbers cited in §2.1; the two new semantics that carry the most weight
  (last-wins is gone; a malformed heading opens no claim; the symlink finding stands alone) are all
  **pinned by the frozen counter** (the corresponding mutants are rejected 34/37, 33/37, 35/37,
  36/37).
- Four defects are named for the L1, none of which is a claim miss and none of which may be fixed by
  editing a frozen file: **F-1** the HEADING-MALFORMED block-boundary clause is undefined in the
  docstring and unpinned; **F-2** FROZEN-EDITED does not cover the Control and a post-freeze edit of
  the preregistration itself is invisible (a genuine operability gap against preregistration rule 1);
  **F-3** the dispatch "any depth" clause is pinned only by the candidate's own selftest;
  **F-4** exit 2 is overloaded by argparse usage errors.
- The per-round preregistration sweep is tabulated in §1.3 with the structural cause of each red:
  rounds 33–39 are red on `NO-CLAIMS` + `FIELD-MISSING C0 Round` (they predate the grammar), round 40
  is red on 18 × `FIELD-MISSING` + `FIELD-MISSING C0 Round` (headings conform, keys are prose), and
  rounds 41 and 42 read clean.

No lane file was modified; no commit, push, or mutating git/jj command was run in the lane or fleet.
