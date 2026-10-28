# R40sentinel47 — C2 operability claim attack (round 40, wave 1)

- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
- Frozen claim under attack: `census/round-40/preregistration.txt` §C2 (sha256
  `7218101a24a48ce8648e9625c992af1aa972d0e4274f17044e185ac0b3b4758c`)
- Base revision (r40 prereg's declared base): `0242085909fb6a4ee041c5443d76316ac6d59d4b`
  (round-39 verified tip)
- r39 control base: `ed30b7f5b77939c9073348d810730bc4f355708d`
- Role: sentinel — attack the frozen claim, do not alter it
- Axis: **operability** (C2)
- Tool installs: **none** (no pacman/uv/cargo/npm install was run; every command below is a
  stock `git`, `python3`, `mkdir`, `mktemp`, `ln`, `mkfifo`, `chmod`, `sha256sum`)
- Scratch root: `/fast/scratch/hyaku/souji-r40/R40sentinel47` (removed at end of this report)
- Lane files written: **this report only** (`.ufo/waves/round-40/w1/R40sentinel47.md`). No lane
  file was edited, no `git`/`jj` mutation in the lane, no commit, no push.

---

## 0. Named distinct edge case for item 47

**The C2 leg's *observation* channel is not the same as its *docstring* channel, and the
observation channel is attacker-adjacent in the r40 design.**

Every C2 discussion in r39 and in the r40 preregistration is about the **docstring reader**
(`docstring_classes`, one line per class → r40: joined continuation lines). Nobody has
attacked the other half of the same leg: **how the leg decides which refusal class the tool
actually raised.** In `census/round-39/c2-counter.py:125-130`, `classify()` picks the first
class token that appears **anywhere** in `stdout+stderr` — and the drift tool embeds the
`--record` path verbatim in every refusal message. The r40 preregistration explicitly
**mandates** operator-supplied scratch paths ("All counters must accept explicit scratch paths
and avoid hardcoded `/tmp`", `census/round-40/preregistration.txt:13`), and the counter
constructs its probe paths *inside* that operator-supplied tree
(`census/round-39/c2-counter.py:172` `tempfile.mkdtemp(prefix="souji-r39-c2.", dir=args.scratch)`,
then `:220` `probe = os.path.join(base_scratch, "record-probe.tsv")` and `:223`
`os.path.join(base_scratch, "absent.tsv")`).

**So: the operator-chosen scratch path flows into the string that `classify()` substring-matches
against. A scratch directory whose name contains a class token silently rewrites the "observed
class".** This is the edge case I attack. It is distinct from every C2 finding in r39
(`W1RevC2Doc` mutants A/B/C were docstring-wording and code-mapping defects; `W1CritDisclosure`
D15 noted `classify` is "first-match over a substring set" as a *disclosure* item but did not
measure its input surface).

I name it explicitly: **the observation channel is path-contaminated — `classify()` is a
substring scan over output that embeds an operator-controlled path, so the observed class is a
function of the scratch path, not only of the tool bytes.**

---

## 1. Falsifier A (headline) — an operator-supplied scratch path flips the observed class and
turns a FAILING leg into a PASSING one

### 1.1 The mechanism, measured directly

`classify()` (`census/round-39/c2-counter.py:125-130`) is a first-match substring scan over
`stdout+stderr` in the order `RECORD-MISSING`, `RECORD-MALFORMED`, `RECORD-EMPTY`,
`RECORD-OUTSIDE-ROOT`. The drift tool's refusal message embeds the record path:

```
tools/souji-worktree-drift.py:135
    raise Refusal("RECORD-MALFORMED: %s is not a regular file" % path)
```

Command (scratch probe `classify_probe.py`; verbatim copy of the counter's `classify` semantics):

```
cd /fast/scratch/hyaku/souji-r40/R40sentinel47
TMPDIR=$PWD python3 -B classify_probe.py $PWD/drift-tip.py $PWD
```

Observed:

```
== classify() vs the refusal token the tool actually emitted ==
record path                                emitted class (from message) classify() says        agree?
plain absent name                          RECORD-MALFORMED       RECORD-MALFORMED       yes
path contains RECORD-MISSING               RECORD-MALFORMED       RECORD-MISSING         NO  <-- FLIP
path contains RECORD-EMPTY                 RECORD-MALFORMED       RECORD-MALFORMED       yes
path contains RECORD-MALFORMED             RECORD-MALFORMED       RECORD-MALFORMED       yes
path contains RECORD-OUTSIDE-ROOT          RECORD-MALFORMED       RECORD-MALFORMED       yes
```

The decisive case, verbatim:

```
== decisive probe ==
tool stderr        : REFUSAL RECORD-MALFORMED: /fast/scratch/.../classify.cxkwde9w/RECORD-MISSING.tsv is not a regular file
classify() result  : RECORD-MISSING
r39 L4 would then look up the docstring entry for 'RECORD-MISSING'
and require 'missing' in that entry's text -> the class NAME itself supplies it
=> L4 passes on a tool whose RECORD-MALFORMED entry never mentions a missing path.
```

Note the flip is **order-dependent**: only `RECORD-MISSING` flips it, because it is first in the
scan tuple. `RECORD-EMPTY` / `RECORD-MALFORMED` / `RECORD-OUTSIDE-ROOT` in the path do **not**
flip it (the real `RECORD-MALFORMED` matches first). A lowercase `record-MISSING` does not flip
it (case-sensitive `in`). So the exploit needs the exact uppercase token — but the token set is
small and public, and a scratch path is chosen by the operator or by CI, not by the tool.

### 1.2 End-to-end through the REAL r39 counter

Mutant **E** (fixture at `/fast/scratch/hyaku/souji-r40/R40sentinel47/lane-clone`, toplevel
asserted before commit): the **tip code** unchanged (still raises `RECORD-MALFORMED` for an
absent record path) with the **r39-base `RECORD-MALFORMED` prose** restored — i.e. the exact
documentation defect the r39 round fixed, reintroduced. This is the defect the r40 C2 claim
exists to prevent; a correct r40 leg must keep it open.

```
cd /fast/scratch/hyaku/souji-r40/R40sentinel47
S=$PWD; C=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c2-counter.py
B=ed30b7f5b77939c9073348d810730bc4f355708d

TMPDIR=$S python3 -B "$C" --root "$S/lane-clone" \
  --rev 1fac3fa4968cdc2220e679a39e2d44e4c4d63db3 --base-rev $B --scratch "$S/clean2"
TMPDIR=$S python3 -B "$C" --root "$S/lane-clone" \
  --rev 1fac3fa4968cdc2220e679a39e2d44e4c4d63db3 --base-rev $B --scratch "$S/poison/RECORD-MISSING"
```

Observed (identical tool bytes, identical revisions — **only `--scratch` differs**):

```
=== MUTANT E (RECORD-MALFORMED names no missing path), CLEAN scratch ===
LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=False
SUMMARY legs=6 pass=5 fail=1 harm=0 tool_sha=59f1e57d7af0/fa934f895d5b fixture_sha=e555d8281484

=== MUTANT E, POISONED scratch (operator path contains RECORD-MISSING) ===
LEG L4 PASS missing=RECORD-MISSING locked=RECORD-MISSING new_maps=True old_maps=False
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/fa934f895d5b fixture_sha=e555d8281484
```

**The whole counter reports `SUMMARY legs=6 pass=6 fail=0 harm=0` (rc 0) on a tool whose
docstring does not document the missing-path trigger at all — purely because the scratch
directory was named `RECORD-MISSING`.** Deterministic across two runs each:

```
run1 poison: LEG L4 PASS missing=RECORD-MISSING locked=RECORD-MISSING new_maps=True old_maps=False
run1 clean:  LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=False
run2 poison: LEG L4 PASS missing=RECORD-MISSING locked=RECORD-MISSING new_maps=True old_maps=False
run2 clean:  LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=False
```

And the same poisoning on the **pristine tip bytes** does not change the verdict (the tip is
correct, so it passes either way) — the poison only ever manufactures a **false PASS**, never a
false FAIL, on this leg:

```
scratch=clean                    tool=drift-tip.py   legA(r39-shaped)=PASS  legB(pair,first-match)=PASS  legB'(pair,anchored)=PASS
scratch=poison/RECORD-MISSING    tool=drift-tip.py   legA(r39-shaped)=PASS  legB(pair,first-match)=FAIL  legB'(pair,anchored)=PASS
```

**Verdict: FALSIFIER A is real and confirmed.** The r40 C2 leg's verdict is a function of the
operator-supplied scratch path, not only of the audited bytes. Under the r40 preregistration's
own rule (explicit scratch paths, `preregistration.txt:13`), this is reachable in normal use:
the scratch path is a documented, operator-chosen input.

**Why this bites r40 specifically.** r39's L4 already had a documented weakness — the `"missing"`
conjunct is satisfied by the class name `RECORD-MISSING` itself (`W1RevC2Doc.md` §3, "VACUOUS").
r40's predicate upgrades L4 to "verifies **all observed class/trigger pairs** in the frozen
list". Under a *pair-based* formulation the tautology disappears **only if the observed class is
right**. Falsifier A shows the observed class can be wrong without any byte change, so the
tautology is not merely a latent r39 defect — it is **load-bearing** for r40: the pair-based
check's power depends entirely on `classify()` returning the true class, and `classify()` does
not.

**Impact.** An r40 C2 counter that inherits r39's `classify()` verbatim and whose "frozen
list" is compared against the *observed* class can be made to report a **false PASS** on a
mutant that re-opens the exact r39 documentation defect (mutant E above: the `RECORD-MALFORMED`
entry names no missing path). The r40 kill condition ("Kill if wrapped trigger is missed, or if
**any observed class mapping disagrees with runtime behavior**") is therefore not enforceable as
written: the leg cannot tell a correct mapping from a contaminated observation.

**Smallest remediation (for the L1; not applied by me — read-only seat).** Anchor the
observation to the refusal token instead of substring-scanning the whole output. The tool emits
`REFUSAL <CLASS>: <detail>` on stderr (`tools/souji-worktree-drift.py:446`,
`sys.stderr.write("REFUSAL %s\n" % exc)`), so the token
immediately after `REFUSAL ` is the class. Measured, this fixes both directions:

```
scratch=poison/RECORD-MISSING    tool=drift-tip.py               legA(r39-shaped)=PASS  legB(pair,first-match)=FAIL  legB'(pair,anchored)=PASS
scratch=poison/RECORD-MISSING    tool=drift-base.py              legA(r39-shaped)=FAIL  legB(pair,first-match)=FAIL  legB'(pair,anchored)=FAIL
scratch=poison/RECORD-MISSING    tool=souji-worktree-drift.py    legA(r39-shaped)=PASS  legB(pair,first-match)=FAIL  legB'(pair,anchored)=FAIL
```

`legB'` (anchored observation) is the only variant that (a) keeps mutant E failing under both
scratch names and (b) keeps the pristine tip passing under both. A one-line change
(`s.split(":",1)[0]` on the token after `REFUSAL `) is enough; `classify_anchored` in
`honest_r40.py` is the exact implementation I measured. Independently, the probe path should be
placed in a scratch subdirectory whose name the counter controls (not derived from the
operator's `--scratch` leaf), so no operator-chosen string can reach the message.

---

## 2. Falsifier B — the "frozen list" the r40 C2 predicate references is **not a committed
artifact**

The r40 predicate reads:

> "r40 L4 docstring analyzer joins wrapped continuation lines into one class entry and verifies
> all observed class/trigger pairs in **the frozen list**"

`census/round-40/` contains exactly one file:

```
$ ls -la census/round-40/
total 4
drwxr-xr-x 1 vgpnk vgpnk  4096 Oct 28 16:26 .
drwxr-xr-x 1 vgpnk vgpnk  4096 Oct 28 16:26 ..
-rw-r--r-- 1 vgpnk vgpnk  2299 Oct 28 16:26 preregistration.txt
$ git ls-files census/round-40/
            (empty — the whole directory is untracked: "?? census/round-40/")
```

Compare r39, which shipped the frozen list as a **committed, hashable** artifact alongside the
preregistration:

```
census/round-39/c1-items.tsv
census/round-39/cells.tsv
census/round-39/preregistration.txt
```

The r39 wave's own enumeration of the pairs (the only committed statement of them) is prose in
a wave report — `census/round-39/waves/w1/W1RevC2Doc.md` §6: *"the `RECORD-MALFORMED` line
enumerates five (missing, non-regular, schema, duplicate, TOTAL) and the `RECORD-MISSING` line
two (EACCES, ELOOP)"*, with `EISDIR` dropped as unreachable at `790d16b`. `SCORECARD.md:779`
(the r40 plan) says only *"carry the remaining class-to-trigger pairs the wave listed"* — a
pointer to prose, not a list.

I reconstructed that 7-pair list and measured it against the committed tip bytes:

```
$ TMPDIR=$PWD python3 -B frozen7.py $PWD/drift-tip.py $PWD
== frozen 7-pair list at /fast/.../drift-tip.py ==
trigger token    doc class      runtime class          1-line   joined   agrees?   note
EACCES           RECORD-MISSING RECORD-MISSING         yes      yes      yes
ELOOP            RECORD-MISSING RECORD-MISSING         yes      yes      yes
missing          RECORD-MALFORMED RECORD-MALFORMED     yes      yes      yes
non-regular      RECORD-MALFORMED RECORD-MALFORMED     yes      yes      yes
schema           RECORD-MALFORMED RECORD-MALFORMED     NO       yes      yes
duplicate        RECORD-MALFORMED RECORD-MALFORMED     NO       yes      yes
TOTAL            RECORD-MALFORMED RECORD-MALFORMED     NO       yes      yes

  pairs visible to the r39 ONE-LINE analyzer: 4/7
  pairs visible to a JOINED analyzer:          7/7
```

This **confirms the r40 predicate's core mechanism is real and useful**: joining the wrapped
continuation lines takes the visible-pair count from 4/7 to 7/7, and the three pairs that only
become visible (`schema`, `duplicate`, `TOTAL`) are exactly the three the r39 wave flagged as
having no probe (`W1RevC2Doc.md` §6). So the r40 C2 *direction* is sound.

**But the list itself is not frozen.** There is no committed r40 artifact naming the pairs, so
"the frozen list" is a back-reference to prose that a later wave can reinterpret. The
preregistration's own last line — *"No post-data change to these predicates"* — cannot bind a
list that does not exist as bytes.

**Impact.** A reviewer cannot mechanically re-derive the r40 C2 verdict without re-deriving the
list by reading r39 wave prose. This is the same defect class the r39 C1 axis was raised for
("bind the C1 items to *evidence* rather than token presence"), one axis over.

**Smallest remediation.** Commit the pair list as bytes next to the preregistration — e.g.
`census/round-40/c2-pairs.tsv` with one row per `(class, trigger_token)` — and have the counter
read *that file* (not a hardcoded tuple) so the frozen set is hashable and diffable. The
measurement above shows such a file would immediately carry 7 rows and discriminate the r39
one-line reader (4/7) from the joined reader (7/7).

---

## 3. Falsifier C — the joined-reader is not pinned: two defensible join rules disagree on the
same committed bytes

The predicate says the analyzer "joins wrapped continuation lines into one class entry" but
does not say **which lines count as continuations**. The docstring has four distinct indent
levels, and two natural rules give different class entries for the same bytes.

The refusal table's own continuation column is indent 25 (e.g. line 43
`'                         exists but cannot be opened or read'`). But the docstring also contains
indented *non-continuation* blocks: the CLI block (indent 2/6, lines 36-37), the record-format
block (indent 4, lines 22-23), and the measurement block (indent 2/12, lines 27-29). A rule of
"any line indented deeper than 2 is a continuation" therefore **swallows the CLI block into the
`UNRECORDED` entry** (which starts at indent 0 on line 33).

Measured (probe `synth.py`/`pairs.py`, rule A = indent ≥ 25, rule B = indent > 2):

```
RULES DISAGREE ON: ['UNRECORDED']

UNRECORDED under indent>=25 rule:
   'UNRECORDED (a git work tree under --root the record does not name).'
UNRECORDED under indent>2 rule:
   'UNRECORDED (a git work tree under --root the record does not name). [--timeout SECS] [--json OUT] [--skip-unrecorded]'

  token --skip-unrecorded in indent>=25 entry: False  | in indent>2 entry: True
  token --json           in indent>=25 entry: False  | in indent>2 entry: True
  token --timeout        in indent>=25 entry: False  | in indent>2 entry: True
```

`UNRECORDED` is not hypothetical — it is an **observable runtime class** on stdout, reachable by
an ordinary unregistered work tree under `--root`:

```
$ TMPDIR=$PWD python3 -B drift-tip.py --root "$W/fleet" --record "$W/rec.tsv"
DRIFT	UNRECORDED	unregistered	live regs=1 prunable=0
SUMMARY ... drift_rows=1 unreachable=0
```

**Impact.** Under rule B the `UNRECORDED` class entry falsely carries `--skip-unrecorded`,
`--json` and `--timeout`. A pair check that looks for a trigger token in the joined entry would
then "verify" `UNRECORDED` against `--skip-unrecorded` — a **token that is not a trigger of that
class at all**. This is precisely the r39-style token-presence over-claim that `W1RevC2Doc.md`
F2 flagged, re-entering through the join rule. It also crosses into the C3 axis
(`--skip-unrecorded` is one of the C3 branches), so a mis-pinned join rule can manufacture
apparent C3 evidence.

**Smallest remediation.** Pin the continuation predicate to the table's own column (indent ≥ 25
at the refusal table), or better: treat a line as a continuation only if it is indented *strictly
more* than the class token's own start column **and** carries no class token. Assert the
rule in the counter's output (e.g. print the join rule and the per-class entry length), so a
reviewer can see which rule produced the verdict.

---

## 4. Falsifier D — the r40 "synthetic wrapped-trigger probe" is a *fixed* fixture and cannot
detect the class of defect it is aimed at

The predicate's discriminator is:

> "a synthetic wrapped-trigger probe is detected while the r39 one-line analyzer misses it"

I built exactly that probe (a copy of the tip tool whose `RECORD-MALFORMED` entry carries
`missing` **only** on a wrapped continuation line) and measured the control and the after:

```
scratch=clean
  Q1 r39 one-line sees 'missing' in RECORD-MALFORMED : False  (predicate control: expect False)
     one-line entry: 'RECORD-MALFORMED       a record path, a non-regular record path, a line'
  Q2 joined sees 'missing' in RECORD-MALFORMED      : True  (predicate after: expect True)
     joined entry  : 'RECORD-MALFORMED       a record path, a non-regular record path, a line that does not match the schema, a duplicated name, a missing (ENOENT) path, or a TOTAL row that disagrees'
  observed class (first-match) = RECORD-MALFORMED ; (anchored) = RECORD-MALFORMED
  Q3 wrapped-trigger DETECTED, first-match observation: True
  Q3 wrapped-trigger DETECTED, anchored observation  : True
```

So the control and the after both behave exactly as the predicate wants. **The probe is
sound in isolation.** But it is a *single fixed synthetic tool* — it proves the joined reader
sees a token the one-line reader cannot. It does **not** prove the joined reader attributes the
token to the *right* class, and it cannot detect Falsifier A (which is upstream of the reader).

This matters because the probe is the r40 leg's **only** new evidence surface: the r39 leg
probes two triggers (absent path, `chmod 000`), and r40 adds a synthetic docstring probe. Neither
is a *runtime* probe of a class the docstring does not name — see Falsifier E.

---

## 5. Falsifier E — the r40 "all observed class/trigger pairs" wording is unsatisfiable at the
tip bytes, because the docstring's `RECORD-MISSING` prose is **false for two reachable errnos**

The r40 predicate requires that the leg "verifies **all observed** class/trigger pairs" and
kills if "any observed class mapping disagrees with runtime behavior". If the observed set is
derived from the tool's own raise sites rather than from the docstring's prose, the **pristine
r39 tip bytes already fail** — because the tip's `RECORD-MISSING` entry names only `EACCES` and
`ELOOP`, while the code raises `RECORD-MISSING` for **every** non-`ENOENT` `OSError` from the
record open (`tools/souji-worktree-drift.py:133-136`):

```
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            raise Refusal("RECORD-MALFORMED: %s is not a regular file" % path)
        raise Refusal("RECORD-MISSING: %s" % exc)
```

The r39 wave already found and fixed one *unreachable* name in this line (`EISDIR`, dropped at
`790d16b`). The mirror-image defect — a **reachable but unnamed** errno — survives, and I
measured it:

```
$ TMPDIR=$PWD python3 -B errno.py $PWD/drift-tip.py $PWD
== errno sweep at the record open ==
errno            rc     class raised           does the path exist?
ENOTDIR          2      RECORD-MISSING         NO      record path does NOT exist (a parent component is a regular file)
      REFUSAL RECORD-MISSING: [Errno 20] Not a directory: '.../plainfile/rec.tsv'
ENAMETOOLONG     2      RECORD-MISSING         NO      record path cannot exist (name exceeds NAME_MAX)
      REFUSAL RECORD-MISSING: [Errno 36] File name too long: '.../zzz...'
ELOOP            2      RECORD-MISSING         yes     record path exists (a symlink cycle)
EACCES           2      RECORD-MISSING         yes     record path exists but cannot be opened
ENOENT           2      RECORD-MALFORMED       NO      record path does not exist
```

and with realistic paths:

```
/etc/passwd/rec.tsv    REFUSAL RECORD-MISSING: [Errno 20] Not a directory: '/etc/passwd/rec.tsv'
```

The tip's `RECORD-MISSING` prose is:

```
'RECORD-MISSING         EACCES or ELOOP opening the record path: the path exists but cannot be opened or read'
```

`ENOTDIR` and `ENAMETOOLONG` are **not named**, and for both the prose's own clause *"the path
exists but cannot be opened or read"* is **factually false** — in both cases the path does not
exist (or cannot exist). A one-word typo in a `--record` path (`/etc/passwd/rec.tsv`) is enough.

Per the pair census at the tip:

```
ENOTDIR          RECORD-MISSING         NO       'EACCES or ELOOP opening the record path: the path exists but cannot be opened or read'
ENAMETOOLONG     RECORD-MISSING         NO       'EACCES or ELOOP opening the record path: the path exists but cannot be opened or read'
```

**Impact.** If r40's leg derives its pair list from the **raise sites** (which "all observed"
implies) rather than from the docstring prose (which is what r39 did), then:

* an honest r40 counter **fails on the pristine tip bytes** — the claim is reported honestly
  failing until the `RECORD-MISSING` entry is amended; or
* r40 pins the list to the docstring's own prose (the 7 pairs), in which case "all observed" is
  not verified at all, and the `ENOTDIR`/`ENAMETOOLONG` falsehood stays invisible forever.

Either way the r40 predicate's wording forces a decision the preregistration does not make.
**This is a real, still-present documentation defect of the same family as `EISDIR`, and it is
the smallest available amendment to the tip**: add `ENOTDIR` and `ENAMETOOLONG` to the
`RECORD-MISSING` line, and correct the prose clause (the path need not exist).

**Smallest remediation.** Amend `tools/souji-worktree-drift.py`'s `RECORD-MISSING` entry to
name every reachable non-`ENOENT` errno of the record open, or to describe the class by
condition rather than by errno list ("the record path could not be opened for a reason other
than its absence"). Then the r40 leg can use a *raise-site-derived* pair list and satisfy "all
observed" honestly.

---

## 6. What the r40 C2 leg must still cover — a bounded measurement plan

These are the checks I could not close as pass/fail against the frozen predicate (the r40
counter does not exist yet), stated as a plan the L1 can execute. Each is cheap.

| # | check | command shape | what it decides |
|---|---|---|---|
| M1 | observation anchored to the refusal token | run the leg with the `REFUSAL `-anchored classifier under clean **and** poisoned scratch | whether Falsifier A is closed (must FAIL mutant E under both) |
| M2 | scratch-path independence | run the leg twice with scratch dirs named `RECORD-MISSING` and `X` | verdict must be byte-identical; any difference is Falsifier A live |
| M3 | join rule pinned | print the join rule and the per-class joined entry in the leg's own output | a reader can see which rule produced the verdict; catches Falsifier C |
| M4 | pair list committed | `sha256sum census/round-40/c2-pairs.tsv` and the leg reads the file | closes Falsifier B (the list is bytes, not prose) |
| M5 | pair list derived from raise sites | grep the tool for `raise Refusal("<CLASS>` and diff that class set against the pair list's class set | closes the "all observed" wording; surfaces `ENOTDIR`/`ENAMETOOLONG` |
| M6 | errno closure | run the tip tool over {`ENOTDIR`, `ENAMETOOLONG`, `ELOOP`, `EACCES`, `ENOENT`} and require every observed class to be named in its joined entry | closes Falsifier E at the tool bytes, not just at the counter |
| M7 | every observed class reachable by the reader | for each class the tool can print, assert the reader produced a non-empty entry | closes the `REGS-CHANGED`/`PRUNABLE-CHANGED`/`ABSENT`/`UNREACHABLE` blind spot (§7) |

---

## 7. Secondary observation — four of the tool's observable drift classes are unreachable by
any line-start reader

The tool prints five drift classes on stdout (`tools/souji-worktree-drift.py:356-383`):
`ABSENT`, `UNREACHABLE`, `REGS-CHANGED`, `PRUNABLE-CHANGED`, `UNRECORDED`. Their docstring
mention is a **prose paragraph**, not a class table — only `UNRECORDED` happens to start a
line:

```
== where each observable class token lives in the docstring ==
  REGS-CHANGED             line_start_lines=-            inline_lines=[31]         +inline
  PRUNABLE-CHANGED         line_start_lines=-            inline_lines=[31]         +inline
  ABSENT                   line_start_lines=-            inline_lines=[31]         +inline
  UNREACHABLE              line_start_lines=-            inline_lines=[32]         +inline
  UNRECORDED               line_start_lines=[33]         inline_lines=-            line-start
```

A reader that requires the class token to *start* a line — which is what the r39 counter does
(`census/round-39/c2-counter.py:141`, `stripped.startswith(cls)`) and what any r40 "joins
wrapped continuation lines into one class entry" reader will inherit unless told otherwise —
**cannot reach four of the five observable drift classes**, even though they are printed at
runtime:

```
== but the drift classes ARE observable at runtime (drift rows on stdout) ==
  rc=1
    DRIFT	REGS-CHANGED	alpha	record=0 live=1
  observable class tokens in that output: ['REGS-CHANGED']
  of those, NOT reachable by a line-start reader over the docstring: ['REGS-CHANGED']
```

**This is not a falsifier of the frozen predicate** — the frozen 7-pair list is a *refusal*-class
list, and the predicate's "observed class/trigger pairs" plausibly means the refusal classes
only. I report it because the r40 leg's *stated* mechanism ("joins wrapped continuation lines
into one class entry") is a mechanism that provably cannot cover the drift classes, so if the
r40 scope is later read as "every class the tool prints", the reader needs a second mode that
the preregistration does not mention. It also overlaps the C3 `--skip-unrecorded` branch.

---

## 8. Summary of verdicts

| # | finding | severity | type | status |
|---|---|---|---|---|
| **A** | `classify()`'s observation channel is path-contaminated: an operator-supplied scratch path containing `RECORD-MISSING` flips the observed class and turns a **FAILING** L4 into a **PASSING** one on mutant E (`SUMMARY legs=6 pass=6 fail=0 harm=0` on a tool whose docstring is wrong). r40's prereg *mandates* operator-supplied scratch paths. | **high** | operability — falsifier | **CONFIRMED**, deterministic, measured end-to-end through the real r39 counter |
| **B** | the "frozen list" the r40 predicate references is not a committed artifact (`census/round-40/` holds only `preregistration.txt`, and the directory is untracked); the list exists only as r39 wave prose | **medium** | operability — falsifier of verifiability | **CONFIRMED** |
| **C** | the join rule is unpinned: two defensible rules (indent ≥ 25 vs indent > 2) disagree on `UNRECORDED` for the same committed bytes; the looser rule injects `--skip-unrecorded` / `--json` / `--timeout` into that class entry, manufacturing false pair matches | **medium** | operability — falsifier | **CONFIRMED** |
| **D** | the r40 synthetic wrapped-trigger probe is a fixed fixture: it proves the joined reader sees a token the one-line reader cannot, but cannot detect A (upstream of the reader) or attribute the token to the right class | **medium** | operability — limit | **CONFIRMED** (the probe's own control/after both behave as specified) |
| **E** | the `RECORD-MISSING` docstring entry is **false for two reachable errnos** (`ENOTDIR`, `ENAMETOOLONG`) and its prose clause "the path exists but cannot be opened or read" is false for both; "all observed class/trigger pairs" is therefore unsatisfiable at the tip bytes unless the entry is amended or the list is pinned to the prose | **high** | operability — still-present doc defect | **CONFIRMED** (same family as the `EISDIR` finding r39 fixed) |
| §7 | four of the tool's five observable drift classes are unreachable by any line-start reader | low | operability — scope note | **CONFIRMED** (not a falsifier of the frozen predicate) |

**The r40 C2 claim is not falsified by this report** — the r40 counter does not exist yet, and
the direction of the claim (join wrapped continuation lines; take the visible-pair count from
4/7 to 7/7) is **measured to work**. What this report delivers is: (i) one confirmed,
end-to-end **falsifier** of the leg's *observation* channel (A), which the r40 predicate's
"any observed class mapping disagrees with runtime behavior" kill condition depends on;
(ii) two confirmed measurement-integrity gaps (B, C) that let a candidate pass without the
frozen list or the join rule being pinned; (iii) one confirmed **still-present documentation
defect** (E) in the tool the claim is about — the same family r39 fixed with `EISDIR`, in the
mirror direction; and (iv) a seven-item bounded measurement plan (§6).

**Recommended disposition for the L1 (not applied — read-only seat):** land the `RECORD-MISSING`
docstring amendment (E) and commit `census/round-40/c2-pairs.tsv` (B) **before** the r40 C2
counter is written, then write the counter with the `REFUSAL `-anchored observation (A), a
pinned join rule (C), and a raise-site-derived pair list (M5/M6). Doing A–E in the other order
produces a counter whose L4 verdict is a function of the scratch path — which is exactly what I
measured above.

---

## 9. Commands actually run (all from `/fast/scratch/hyaku/souji-r40/R40sentinel47`)

Every command below was executed. Output quoted above is verbatim.

**Setup / extraction (read-only against the lane):**

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
git rev-parse --show-toplevel                      # /home/vgpnk/Projects/shokunin/souji-shokunin
git log --oneline -3 0242085909fb6a4ee041c5443d76316ac6d59d4b
git show 0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py > $S/drift-tip.py
git show ed30b7f5b77939c9073348d810730bc4f355708d:tools/souji-worktree-drift.py > $S/drift-base.py
sha256sum $S/drift-tip.py $S/drift-base.py \
  /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c2-counter.py \
  /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt
diff -u $S/drift-base.py $S/drift-tip.py            # docstring-only delta, 2 insertions / 3 deletions
```

**Probes (all written under my scratch root, all read-only against the lane):**

```
python3 -B docgeom.py $S/drift-tip.py              # docstring geometry + join rules
python3 -B oracle.py  $S/drift-tip.py $S           # record-path trigger oracle
python3 -B pairs.py   $S/drift-tip.py $S           # (class, trigger) census + join-rule comparison
python3 -B driftcls.py $S/drift-tip.py $S          # drift-class reachability
python3 -B errno.py   $S/drift-tip.py $S           # errno closure sweep (ENOTDIR/ENAMETOOLONG/…)
python3 -B frozen7.py $S/drift-tip.py $S           # the 7-pair frozen list, 1-line vs joined
python3 -B classify_probe.py $S/drift-tip.py $S    # classify() path-contamination probe
python3 -B matrix.py $S/drift-tip.py $S clean
python3 -B matrix.py $S/drift-tip.py $S poison/RECORD-MISSING
python3 -B honest_r40.py $S/drift-tip.py $S clean
python3 -B honest_r40.py $S/drift-tip.py $S poison/RECORD-MISSING
python3 -B synth.py   $S/drift-tip.py $S clean
python3 -B synth.py   $S/drift-tip.py $S poison/RECORD-MISSING
```

**Real counter runs (frozen r39 instrument, unmodified):**

```
C=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c2-counter.py
L=/home/vgpnk/Projects/shokunin/souji-shokunin
B=ed30b7f5b77939c9073348d810730bc4f355708d

# receipt reproduction (clean scratch)
TMPDIR=$S python3 -B $C --root $L --rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --base-rev $B --scratch $S/repro
#   -> LEG L1..L6 PASS; SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484
#   -> byte-identical to census/round-39/records/c2-after.txt

# control (base vs base, clean scratch)
TMPDIR=$S python3 -B $C --root $L --rev $B --base-rev $B --scratch $S/clean
#   -> LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=False

# Falsifier A, mutant E, clean vs poisoned scratch (2 runs each)
TMPDIR=$S python3 -B $C --root $S/lane-clone --rev 1fac3fa4968cdc2220e679a39e2d44e4c4d63db3 --base-rev $B --scratch $S/clean2
TMPDIR=$S python3 -B $C --root $S/lane-clone --rev 1fac3fa4968cdc2220e679a39e2d44e4c4d63db3 --base-rev $B --scratch $S/poison/RECORD-MISSING
TMPDIR=$S python3 -B $C --root $S/lane-clone --rev 1fac3fa4968cdc2220e679a39e2d44e4c4d63db3 --base-rev $B --scratch $S/poison2/RECORD-MISSING-probe
TMPDIR=$S python3 -B $C --root $S/lane-clone --rev 1fac3fa4968cdc2220e679a39e2d44e4c4d63db3 --base-rev $B --scratch $S/poison3/record-MISSING

# pristine tip, clean vs poisoned (poison is a no-op on correct bytes)
TMPDIR=$S python3 -B $C --root $L --rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --base-rev $B --scratch $S/poison/RECORD-MISSING
```

**Fixture (git), toplevel asserted before every commit — no lane mutation:**

```
F=$(mktemp -d "$S/fixture.XXXXXX")
git -C "$F" init -q
git -C "$F" rev-parse --show-toplevel      # asserted == $F
git -C "$F" -c user.email=t@t -c user.name=t add -A
git -C "$F" -c user.email=t@t -c user.name=t commit -qm "..."
```

The mutant used in §1.2 was committed in a scratch **clone** of the lane
(`/fast/scratch/hyaku/souji-r40/R40sentinel47/lane-clone`, created with
`git clone --quiet --no-hardlinks`), with `git rev-parse --show-toplevel` asserted to equal the
clone root before the commit. Mutant E = tip tool bytes with only the `RECORD-MALFORMED`
docstring paragraph reverted to the r39-base wording; `git diff --stat HEAD~1 HEAD` shows
`tools/souji-worktree-drift.py | 5 ++---` (docstring only; the code is byte-identical to the
tip, sha256 `e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76`).

**Runtime probes needing a git repo (all under scratch, toplevel asserted):**

```
git -C "$W/fleet/repoA" init -q ; git -C "$W/fleet/unregistered" init -q
```

---

## 10. Scratch

`/fast/scratch/hyaku/souji-r40/R40sentinel47` (probe scripts, extracted tool bytes, the scratch
clone, the mutant-E commit, the poisoned/clean scratch trees) was removed with `rm -rf` after
measurement. Nothing of mine remains on disk. **The only file this seat wrote inside the lane is
this report**, `.ufo/waves/round-40/w1/R40sentinel47.md`. No lane file was edited, no commit, no
push, no `git`/`jj` mutation in the lane, no `.ufo/state` / watchdog / operator-config / fleet
script / template touched, no tool installed.
