# W1ScribeGate — round-39 `## Gate` rows, drafted and re-derived

Seat: scribe (leaf). Item: draft the round-39 lesson `## Gate` table rows from the three source
scouts (gitrevisions, ast, argparse), check them against `corpus/SOURCES.md` (duplicate URL/scope)
and `corpus/QUALITY.md` (admission bar), and deliver the rows plus the census consequence
(170 -> 170+k). Advisory: the L1 appends and integrates.

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. HEAD while measuring
`d4c17557b92fd98044e4c8f0ddc79c6d75701b15`; lane base `ed30b7f5b77939c9073348d810730bc4f355708d`;
freeze `b769bfb84a264d8b284c09bc211d99f39a3e9126`.
Scratch: `/fast/scratch/hyaku/souji-r39/W1ScribeGate` (removed at exit; §8).
Installs: **none** — no tool was installed or upgraded. `/tmp` used for nothing.
Git: read-only only (`show`, `diff --numstat`, `rev-parse`, `cat-file -e`, `status`). One scratch
repo for a behaviour probe (`mktemp -d` under scratch, `rev-parse --show-toplevel` asserted, removed).
No lane byte written except this report; `corpus/SOURCES.md` untouched by this seat.

**State of the bytes I am drafting against.** The three rows and the Gate table already exist in
committed bytes (`c0b007b` "…r39 lesson with Gate/Mistakes, three source rows…"): `corpus/SOURCES.md`
lines 196-198 (S247-S249) and `corpus/lessons/round-39.md` lines 37-45. This report therefore does two
things: it delivers the row set as a draft the L1 can append/correct, and it re-derives every locator
and quote independently (Q5: the re-deriving seat) instead of copying the landed text.

---

## 1. Re-derivation of the three candidates

Scout reports (`W1ScoutGitRev.md`, `W1ScoutAst.md`, `W1ScoutArgparse.md`) were read **after** my own
derivation; they landed during this seat. Agreement/disagreement is recorded in §1.4. No scout file
was used as the source of a quote.

### 1.1 gitrevisions — `<rev>^{<type>}`

```
$ git --version
git version 2.56.0
$ man -w 7 gitrevisions
/usr/share/man/man7/gitrevisions.7.gz
$ MANWIDTH=100 man 7 gitrevisions | tail -2
Git 2.56.0                                   2026-09-27                             GITREVISIONS(7)
$ MANWIDTH=100 man 7 gitrevisions | grep -n 'SPECIFYING REVISIONS\|^ *<rev>\^{<type>}\|barf'
19:SPECIFYING REVISIONS
165:     <rev>^{<type>}, e.g. v0.99.8^{commit}
168:         be dereferenced anymore (in which case, barf). For example,  if  <rev>  is  a  commit-ish,
```

Body, lines 165-171 (`MANWIDTH=100 man 7 gitrevisions | sed -n '164,172p'`):

```
165	     <rev>^{<type>}, e.g. v0.99.8^{commit}
166	         A suffix ^ followed by an object type name enclosed in brace pair  means  dereference  the
167	         object  at  <rev> recursively until an object of type <type> is found or the object cannot
168	         be dereferenced anymore (in which case, barf). For example,  if  <rev>  is  a  commit-ish,
169	         <rev>^{commit}  describes  the  corresponding  commit  object.  Similarly,  if  <rev> is a
170	         tree-ish, <rev>^{tree} describes the corresponding tree object.  <rev>^0 is  a  short-hand
171	         for <rev>^{commit}.
```

Web page (anchor the man page cannot show):

```
$ curl -fsSL --max-time 40 -o grevs.html -w 'HTTP=%{http_code} bytes=%{size_download}\n' https://git-scm.com/docs/gitrevisions
HTTP=200 bytes=74526
$ grep -o 'id="Documentation/gitrevisions.txt-revtypeegv0998commit"' grevs.html | head -3
id="Documentation/gitrevisions.txt-revtypeegv0998commit"
$ grep -o 'last updated in [0-9.]*' grevs.html | head -2
last updated in 2.56.0
```

Host behaviour (does `^{commit}` refuse a non-commit? — the row's teaches cell asserts it):

```
$ D=$(mktemp -d "$S/gitprobe.XXXXXX") && git -C "$D" init -q && test "$(git -C "$D" rev-parse --show-toplevel)" = "$D" …
toplevel=/fast/scratch/hyaku/souji-r39/W1ScribeGate/gitprobe.fdJvL1
commit=019489ba781a3d9729d399fce49221757a2367d5
blob=587be6b4c3f93f93c489c0111bba5596147a26cb
RC_COMMIT_PEEL=0
error: 587be6b4c3f93f93c489c0111bba5596147a26cb^{commit}: expected commit type, but the object dereferences to blob type
fatal: Not a valid object name 587be6b4c3f93f93c489c0111bba5596147a26cb^{commit}
RC_BLOB_PEEL=128
fatal: Not a valid object name deadbeefdeadbeefdeadbeefdeadbeefdeadbeef^{commit}
RC_MISSING_PEEL=128
```

### 1.2 ast.get_docstring

```
$ python3 -c "import sys;print(sys.version)"
3.14.8 (main, Oct  2 2026, 10:23:31) [GCC 16.2.1 20260810]
$ curl -sS -o ast.html -w 'ast %{http_code} %{size_download}\n' https://docs.python.org/3/library/ast.html
ast 200 362029
$ grep -n 'Python 3\.1[0-9]' ast.html | head -1
20:    <title>ast — Abstract syntax trees &#8212; Python 3.15.2 documentation</title>…
$ grep -n 'which must be a' ast.html | cut -c1-80
2798:<dd><p>Return the docstring of the given <em>node</em> (which must be a
$ grep -n 'id="ast.get_docstring"' ast.html | cut -c1-60
2796:<dt class="sig sig-object py" id="ast.get_docstring">
```

Stripped text, lines 2797-2800 (`sed -n '2796,2803p'` with tags removed):

```
2797 ast.get_docstring(node, clean=True)¶
2798 Return the docstring of the given node (which must be a
2799 FunctionDef, AsyncFunctionDef, ClassDef,
2800 or Module node), or None if it has no docstring.
2801 If clean is true, clean up the docstring’s indentation with
```

Host behaviour (the row's teaches cell: "returns None rather than raising when a module has none"):

```
$ python3 -c "import ast;print(repr(ast.get_docstring.__doc__))"
'\nReturn the docstring for the given node or None if no docstring can\nbe found.  If the node provided does not have docstrings a TypeError\nwill be raised.\n\n…'
$ python3 -c "…print('module-docstring:', ast.get_docstring(ast.parse('x=1\n')))"
module-docstring: None
$ python3 -c "…ast.get_docstring(ast.parse('x=1').body[0])"
wrong-node-type: TypeError: 'Assign' can't have docstrings
$ python3 -c "…ast.get_docstring(ast.parse('__doc__ = \"fake\"\nX = \"not a docstring\"\n'))"
module-const-only: None
$ python3 -c "…ast.get_docstring(ast.parse('\"\"\"hello\"\"\"\n'))"
module-doc: 'hello'
```

Rejected sibling candidate, same page:

```
$ grep -n 'id="ast.get_source_segment"' ast.html | cut -c1-60
2809:<dt class="sig sig-object py" id="ast.get_source_segment">
2811:<dd><p>Get source code segment of the <em>source</em> that generated <em>node</em>.
```

### 1.3 argparse exit status

```
$ curl -sS -o argparse.html -w 'argparse %{http_code} %{size_download}\n' https://docs.python.org/3/library/argparse.html
argparse 200 334734
$ sed -n '20p' argparse.html | cut -c1-120
    <title>argparse — Parser for command-line options, arguments and subcommands &#8212; Python 3.15.2 documentation</title>…
$ grep -n 'id="exit-on-error"' argparse.html | cut -c1-60
790:<section id="exit-on-error">
$ grep -n 'status code of 2' argparse.html | cut -c1-120
2418:<a class="reference internal" href="sys.html#sys.stderr" …>sys.stderr</a> and terminates the program with a status code of 2.</p>
```

Stripped text, lines 791-794:

```
791 exit_on_error¶
792 Normally, when you pass an invalid argument list to the parse_args()
793 method of an ArgumentParser, it will print a message to sys.stderr and exit with a status
794 code of 2.
```

The second hit (line 2418) is `ArgumentParser.error`, a **different section** — the section
attribution in S249 is right and the quote must be pinned to 792-794, not 2418.

```
$ python3 -c 'import argparse;ap=argparse.ArgumentParser(prog="probe");ap.add_argument("--x",required=True);ap.parse_args([])' 2>ap.err 1>ap.out; echo "EXIT=$?"
EXIT=2
STDOUT_BYTES=0
STDERR:
usage: probe [-h] --x X
probe: error: the following arguments are required: --x
```

### 1.4 Scout agreement

| candidate | my derivation | scout | agree? |
|---|---|---|---|
| S247 | heading line 19; entry 165; quote 166-168; page 2.56.0 (last-modified 2026-10-26); blob peel rc 128 | W1ScoutGitRev: same lines 165-171, same 2.56.0 stamp, same anchor id; leaves the blob case **unrun** | agree; my blob/missing probe supplies the case the scout listed as unresolved |
| S248 | dt 2796, quote 2798-2800, 17 words; Module-without-docstring → `None`, wrong node type → `TypeError`; `__doc__` on 3.14.8 claims a TypeError for "does not have docstrings" | W1ScoutAst: same 17-word quote, same `None`/`TypeError` split, same `__doc__` wording; adds that `/3.14/` today is the 3.14.10 build while `/3` is 3.15.2 | agree |
| S249 | h3 791, quote 792-794, 15 words; rc 2, stdout 0 bytes, stderr usage+error; line 2418 is `error()` | W1ScoutArgparse: same 15-word quote, same section id, same stream split (74 B stderr), same `ArgumentParser.error` distinction, same "disclosure only" reading | agree |
| reject (get_source_segment) | dt 2809, quote 2811, 10 words, takes `source` text | W1ScoutAst: same entry, same reading | agree |

---

## 2. The draft `## Gate` rows

House shape of the landed table (`corpus/lessons/round-39.md:37`, five columns). Quotes carry the
**leading/trailing ellipsis** the landed bytes omit (§6 F2), and every locator carries line numbers.
Word counts are `str.split()` on the quoted string.

```
| id | source (URL) | access | located quote (<=25 words) | verdict |
|---|---|---|---|---|
| S247 | gitrevisions(7) § SPECIFYING REVISIONS `<rev>^{<type>}` — https://git-scm.com/docs/gitrevisions#Documentation/gitrevisions.txt-revtypeegv0998commit | 2026-10-28 | "… dereference the object at <rev> recursively until an object of type <type> is found or the object cannot be dereferenced …" (installed man page git 2.56.0-1, `MANWIDTH=100 man 7 gitrevisions`, section heading line 19, entry line 165, quote 166-168; 20 words) | **admit** — grounds C2's `--rev`/`--register-rev` arm: `cat-file -e <rev>^{commit}` is the peel, and the page's "or the object cannot be dereferenced … barf" is why a blob id is could-not-evaluate rather than a finding (host probe: commit peel rc 0, blob peel rc 128 `expected commit type`, missing name rc 128) |
| S248 | Python docs `ast.get_docstring` — https://docs.python.org/3/library/ast.html#ast.get_docstring | 2026-10-28 | "… (which must be a FunctionDef, AsyncFunctionDef, ClassDef, or Module node), or None if it has no docstring." (docs.python.org/3, Python 3.15.2 page fetched 2026-10-28, section `ast.get_docstring`, heading line 2797, quote lines 2798-2800; 17 words) | **admit** — grounds C2 L4: the analyser reads the module docstring through `ast.parse` + `ast.get_docstring`, and a module with no docstring is `None`, not an error (host probe on 3.14.8: `None`; a module constant named like a docstring is `None`; a non-docstring node type is `TypeError`) |
| S249 | Python docs argparse `exit_on_error` — https://docs.python.org/3/library/argparse.html#exit-on-error | 2026-10-28 | "… it will print a message to sys.stderr and exit with a status code of 2" (docs.python.org/3, Python 3.15.2 page fetched 2026-10-28, section `exit_on_error`, h3 line 791, quote lines 792-794; 15 words) | **admit** — disclosure for C2's declared exit map: argparse's own usage errors already exit 2, so 2 alone cannot mean could-not-evaluate and the class token `REV-UNRESOLVED` must carry it (host probe: rc 2, stdout 0 bytes, message on stderr) |
| — | Python docs `ast.get_source_segment` (same page, next entry) — https://docs.python.org/3/library/ast.html#ast.get_source_segment | 2026-10-28 | "Get source code segment of the source that generated node" (section `ast.get_source_segment`, heading line 2809, quote line 2811; 10 words) | **reject** — it takes the `source` text and returns the node's own span, which is the source slicing the docstring check must not do; flip: the docstring read must go through `get_docstring` |
```

Two consequences the L1 must not lose:

- The reject candidate carries **no id and adds no registry row**. Precedent for a lesson-only
  rejection row: `corpus/lessons/round-24.md:206` (`| — | S122 | builtin/count-objects.c@v2.56.0 |`).
  Rejections that *do* get ids (S030, S032, S044, S048, S227-S229; 16 `| rejected |` rows) are
  registry rows. So the census consequence is **+3, not +4** (§5).
- S249 is **disclosure**, not a scored predicate: the frozen C2 legs score `--rev` resolution, the
  `--register-rev` harm leg and the drift docstring; none scores argparse's exit status. The row
  must not be read as a C2 predicate.

---

## 3. Duplicate URL / scope check against `corpus/SOURCES.md`

```
$ grep -n 'docs.python.org/3/library/ast.html\|docs.python.org/3/library/argparse.html\|docs.python.org/3/library/functions.html\|git-scm.com/docs/gitrevisions\|git-scm.com/docs/git-rev-parse' corpus/SOURCES.md | cut -c1-160
75:| S050 | Python built-in compile() — https://docs.python.org/3/library/functions.html#compile | docs | A | parse/compile without execution of a source text
104:| S079 | git-rev-parse --verify — https://git-scm.com/docs/git-rev-parse | docs | A | one explicit parameter resolved to an object id; no durability or wo
116:| S091 | git-rev-parse verification, source-only narrowing — https://git-scm.com/docs/git-rev-parse | docs | A | one parameter resolving to an object; no 
124:| S099 | rev-parse conversion and existence qualification — https://git-scm.com/docs/git-rev-parse | docs | A | plain verify wording versus typed object-e
196:| S247 | gitrevisions(7) § SPECIFYING REVISIONS `<rev>^{<type>}` — https://git-scm.com/docs/gitrevisions | docs | A | the `^<type>` type-coercion suffix 
197:| S248 | Python docs, ast.get_docstring — https://docs.python.org/3/library/ast.html#ast.get_docstring | docs | A | the ast-only module-docstring read the
198:| S249 | Python docs, argparse exit status — https://docs.python.org/3/library/argparse.html#exit-on-error | docs | A | argparse's own usage-error exit st
```

(lines above are `cut -c1-160`, so each ends mid-cell — that is the truncation, not the row)

| candidate | URL unique? | scope overlap found | verdict |
|---|---|---|---|
| S247 | yes — `gitrevisions` appears in no other row's URL (line 196 only) | **yes, one**: the peel paragraph is byte-identical on `git-rev-parse(1)` lines 419-427, the page **S099** already cites ("OPTIONS verify and following type-peeling paragraph"; teaches "object or commit peeling adds the documented existence or type check"). S239/S244 are `git-merge-base --is-ancestor` exit status and do not state how a name is shown to be a commit; S240 (`cat-file -e`) excludes `^{commit}` type coercion | **admit, adjacency disclosed** — see F1 |
| S248 | yes — `ast.html` appears only at line 197 (S050 is `functions.html#compile`, a different page) | none | **admit** |
| S249 | yes — `argparse.html` appears only at line 198 | none (no row mentions argparse) | **admit** |
| reject | `ast.get_source_segment` in no row | none | **reject** |

Registry-level duplicate instrument (fleet script, read-only):

```
$ bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji > validate-head.txt; echo "EXIT=$?"
EXIT=0
$ wc -l < validate-head.txt ; awk -F'\t' '{print $2}' validate-head.txt | sort | uniq -c
48
      1 ok
     47 W04
$ grep -c 'S247\|S248\|S249' validate-head.txt
0
$ tail -1 validate-head.txt
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
```

**Verdict: pass.** No E-code, no new W04; the three new rows appear in no duplicate-URL warning.
`W04` stays 47 and the warning id set is unchanged (47 before, 47 after per
`.ufo/waves/round-39/w1/W1ExecSources.md` §4, which compared the id sets).

---

## 4. Admission bar (`corpus/QUALITY.md`)

| criterion | check run | observed | verdict |
|---|---|---|---|
| Q1 (claim names the version verified on **and** the host version re-run on) | rows read; host probes in §1 | S247 names `git 2.56.0-1` and the host `git version 2.56.0`; S248/S249 name the 3.15.2 page **and** "installed interpreter Python 3.14.8"; my probes re-ran on exactly those host versions | **pass**, with F4 |
| Q2 (where docs are silent/disagree with behaviour, cite code at a tag or a fixture run; installed behaviour outranks prose) | §1.1 blob probe, §1.2 four `ast` probes, §1.3 stream probe | every teaches cell in the three rows is behaviour-confirmed on the host; the one prose/behaviour disagreement found is the installed `ast.__doc__` sentence (F4) | **pass** |
| Q17/Q31 (a named evidence path resolves at the measured revision) | `git cat-file -e HEAD:corpus/lessons/round-39.md` → rc 0; lesson names each id | `used-by` target exists at HEAD and cites all three ids (`S247`×2, `S248`×1, `S249`×3) | **pass** |
| Q54 (every `§ <NAME>` locator resolves to a heading-like line in a declared snapshot) | Gate declares **no** `snapshot:` paths, so the criterion does not scope it; the locators were still resolved: `SPECIFYING REVISIONS` at man line 19, `ast.get_docstring` dt at html 2796 / rendered 2797, `exit_on_error` h3 at html 791, `ast.get_source_segment` dt at html 2809 | all four resolve | **pass (not scoped; checked anyway)** |
| Q56 (grounded knowledge entry ⇄ README coverage map) | `grep -rn 'S24[789]' corpus/knowledge/` → no output | no knowledge entry cites the new rows, so no map row is owed | **n/a** |
| Q62 (bidirectional used-by/source agreement) | `python3 -B tools/souji-registry-agreement.py --root . --rev d4c1755… --list-rev b769bfb…` | `COULD-NOT-EVALUATE derived facts are trivial`, `EXIT=2` — the tool's round-29 fixture requires the r29 `c2-counter.py` to report non-trivial `r26 records=` at `--list-rev`, which the r39 prereg does not produce | **instrument unusable this round** — manual check instead (below) |
| Q62 manual | `grep -n 'used-by' …`; lesson id grep | row → `used-by corpus/lessons/round-39.md`, file exists at HEAD and names S247/S248/S249; no knowledge entry's `source:` cites them, so the reverse direction has no obligation | **pass (manual)** |

Quote-length gate (the row shape's `<=25 words`):

```
$ python3 - <<'PY'  # str.split() on each quoted string
S247 20 words
S248 17 words
S249 15 words
REJ-get_source_segment 10 words
```

**Verdict: pass** — all four ≤25.

---

## 5. Census consequence

```
$ bash …/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin souji
souji	rows	173
souji	tier.A	164
souji	tier.B	6
souji	tier.C	3
souji	status.mined	143
souji	status.queued	14
souji	status.rejected	16
FLEET	rows	173
FLEET	missing	0
EXIT=0
$ git -C … show ed30b7f5b77939c9073348d810730bc4f355708d:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
170
$ git -C … rev-parse HEAD
d4c17557b92fd98044e4c8f0ddc79c6d75701b15
$ git -C … diff --numstat ed30b7f5b77939c9073348d810730bc4f355708d..HEAD -- corpus/SOURCES.md
5	0	corpus/SOURCES.md
```

**Delivered consequence: `170 -> 170+k` with `k = 3`, i.e. `170 -> 173`.** Distribution moved
tier.A 161 → 164, mined 140 → 143, B/C/queued/rejected unchanged; the registry diff is 5 added lines
and 0 removed (one provenance paragraph + three rows), so no existing row's `status`, `recheck` or
`used-by` cell changed. `k` is 3 and not 4 because the rejected `get_source_segment` candidate is
lesson-only (§2, `corpus/lessons/round-24.md:206` precedent).

Advisory on the assignment's own arithmetic: `170` is the **base-of-round** reading. Any r39 sentence
that quotes 170 as a *closing* number, or says the registry was untouched, is contradicted by the
5-line diff above. The landed lesson already states the correct form
(`corpus/lessons/round-39.md:44`: "The registry grew 170 -> 173 rows, all tier A `mined`").

---

## 6. Findings for the L1 (append-only; nothing here was rewritten by me)

**F1 — S247's fact is already grounded by S099; only the locator is new (advisory, no integrity
defect).** The peel paragraph is byte-identical on two man pages:

```
$ MANWIDTH=100 man 7 gitrevisions | sed -n '164,172p'
     <rev>^{<type>}, e.g. v0.99.8^{commit}
         A suffix ^ followed by an object type name enclosed in brace pair  means  dereference  the
         object  at  <rev> recursively until an object of type <type> is found or the object cannot
         be dereferenced anymore (in which case, barf). …
$ MANWIDTH=100 man git-rev-parse | sed -n '419,428p'
     <rev>^{<type>}, e.g. v0.99.8^{commit}
         A suffix ^ followed by an object type name enclosed in brace pair  means  dereference  the
         object  at  <rev> recursively until an object of type <type> is found or the object cannot
         be dereferenced anymore (in which case, barf). …
```

S099 (`corpus/SOURCES.md:124`) cites the rev-parse page's "type-peeling paragraph" and teaches that
"object or commit peeling adds the documented existence or type check". Recommended append-only
clause for S247's scope cell (the L1 appends; the row keeps `mined`): the sentence also appears on
`git-rev-parse(1)` lines 419-427, which S099 cites, so S247 is the `gitrevisions(7)` **locator** for
the suffix the tool spells, not a new fact. Not a rejection: the tool's contract names the peel
suffix, and no row states the "barf on a non-dereferenceable object" consequence as a behaviour
(§1.1 probe) — but the L1 should decide with F1 in view.

**F2 — all three admitted quotes cut mid-sentence with no ellipsis (defect class; the lane rejected a
row for this in r38).** Landed text starts at "dereference the object…" / "(which must be…" / "it will
print…", i.e. after the words "…brace pair means", "Return the docstring of the given node", "…of an
ArgumentParser,". S247 also cuts its tail before "anymore (in which case, barf)". S246 was rejected in
r38 for "cut its quote mid-sentence without an ellipsis at exactly the clause that decides the
reject". Fix: use the §2 rows, which carry `…` at each cut. Word counts stay 20/17/15.

**F3 — S248/S249 have no line numbers (the item requires "section + line numbers").** Supplied:
ast.html 2798-2800 (heading 2797); argparse.html 792-794 (h3 791). Both pages are the 3.15.2 build,
fetched 2026-10-28 (362 029 B / 334 734 B). Also pin S249 away from line 2418, which is
`ArgumentParser.error`, not `exit_on_error`.

**F4 — the installed `ast.get_docstring.__doc__` contradicts the served page and the behaviour (Q2
case).** Installed 3.14.8: "If the node provided does not have docstrings a TypeError will be
raised." Served 3.15.2 page: "or None if it has no docstring." Observed: a `Module` with no docstring
→ `None`; a non-docstring node type (`Assign`) → `TypeError: 'Assign' can't have docstrings`. So
S248's teaches cell is correct and the `__doc__` sentence is only true of the node-type precondition.
Recommended disclosure line in the Gate prose (not a row change): a seat reading `ast.get_docstring.__doc__`
instead of the page would derive a false claim, which is exactly why the row cites the page.

**F5 — the Q62 instrument cannot be run against a round-39 prereg.**
`tools/souji-registry-agreement.py --root . --rev d4c1755… --list-rev b769bfb…` → `EXIT=2`,
`COULD-NOT-EVALUATE derived facts are trivial`; the guard (`tools/souji-registry-agreement.py:108-118`)
runs the pinned round-29 `c2-counter.py` at `--list-rev` and refuses when it reports
`r26 records=0`. The bidirectional check was therefore done manually (§4) and passes. QUALITY Q62's
test names the tool with a generic `<full40>`; for r39 the r29 list is not the prereg, so the
criterion's test is unsatisfiable as written this round — a QUALITY wording item, not a lane defect.

**F6 — S247's URL lacks the fragment the page emits.** `grep -o 'id="Documentation/gitrevisions.txt-revtypeegv0998commit"' grevs.html`
→ present. Sibling rows carry fragments (S239, S240, S244). Advisory: append
`#Documentation/gitrevisions.txt-revtypeegv0998commit`; the man-page line numbers already locate the
entry, so this is cosmetic and does not change the row count.

**F7 — S249 is disclosure only.** It must not be counted as a C2 predicate: C2's scored legs are
`--rev` resolution, the `--register-rev` harm leg, the drift docstring mapping, the fixture and the
six consumers. A round-39 claim that "C2 passes because argparse exits 2" would be a calibration
defect.

---

## 7. Verdict per check

| # | check | observed | verdict |
|---|---|---|---|
| S1 | S247 locator re-derived | heading 19, entry 165, quote 166-168, page 2.56.0, anchor id present | PASS |
| S2 | S247 claim on host | commit peel rc 0; blob peel rc 128 `expected commit type`; missing rc 128 | PASS |
| S3 | S248 locator + behaviour | dt 2796, quote 2798-2800 (17 w); `None` for no-docstring module, `TypeError` for wrong node type, `None` for a look-alike constant | PASS |
| S4 | S249 locator + behaviour | h3 791, quote 792-794 (15 w); rc 2, stdout 0 B, stderr usage+error | PASS |
| S5 | reject candidate | dt 2809, quote 2811 (10 w), takes `source` text | PASS (reject stands) |
| S6 | quote lengths | 20 / 17 / 15 / 10 words, all ≤25 | PASS |
| S7 | duplicate URL | each URL appears in exactly one row; `validate` exit 0, 47 W04, no new id | PASS |
| S8 | duplicate scope | S247 adjacent to S099 (byte-identical paragraph) — disclosed, not a URL duplicate | PASS with F1 |
| S9 | admission bar | Q1 pass (F4), Q2 pass, Q17/Q31 pass, Q54 not scoped/checked, Q56 n/a, Q62 tool unusable → manual pass | PASS with F5 |
| S10 | census consequence | 170 → 173 (k=3), tier.A 161→164, mined 140→143, diff 5 added / 0 removed | PASS |
| S11 | quote fidelity | three mid-sentence cuts without ellipsis in the landed bytes | **FAIL (F2)** — fix by appending the §2 rows |
| S12 | locator completeness in landed bytes | S248/S249 lack line numbers | **FAIL (F3)** — supplied in §2 |

Bottom line: **the three candidates are admissible and the census consequence is `170 -> 173`
(k=3)**. The landed Gate table is substantively right — every teaches cell I re-derived is
behaviour-confirmed on this host — but it carries two hygiene defects the lane's own precedent
polices (F2 quote cuts, F3 missing line numbers) and one scope adjacency worth a disclosure line
(F1). Nothing was written to `corpus/SOURCES.md`; the L1 appends.

---

## 8. Hygiene

- Scratch `/fast/scratch/hyaku/souji-r39/W1ScribeGate` held `ast.html`, `argparse.html`,
  `grevs.html`, `ap.err`, `ap.out`, `validate-head.txt`, `registry-agreement.txt`, `grevs.txt`,
  `revparse.txt` and one `gitprobe.*` repo. **Removed at exit — `SCRATCH_GONE`.** `/tmp` unused.
- The scratch git repo was created with `mktemp -d`, `git init -q`, and
  `git rev-parse --show-toplevel` asserted equal to `$D` before the single commit; commits used
  `-c maintenance.auto=false` and a named pathspec (`-- f.txt`).
- Writes: this report only. No fleet-repo path, no sibling lane, no `.ufo/state/`, no `templates/`,
  no `scripts/`, no frozen receipt, no `census/round-39/*-items.tsv` or `*.json` spec touched.
- No install or upgrade; nothing to record under the tooling authorization.
- Not run by this seat (so not passed): the frozen C1/C2/C3 counters, the drift/citation fixtures,
  the `c2-counter.py` legs, the `/3.14/` docs pages, and a reconstructed-base `validate` run (the base
  registry was read only as a row-count grep on the `ed30b7f` blob).
