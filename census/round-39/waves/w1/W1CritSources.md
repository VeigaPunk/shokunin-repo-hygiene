# W1CritSources — critic: sources plan for section 2b (r39 wave 1)

Seat: critic (leaf, advisory; L1 integrates). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Measured against lane HEAD `2201778e7736af82e7d8a42dec2494f115bf3923` and base
`ed30b7f5b77939c9073348d810730bc4f355708d`; the three rows under review landed at `c0b007b`
(`round-39: C1 — 14 routed-defect corrections, r39 lesson with Gate/Mistakes, three source rows,
gate-registry rows`). Scratch: `/fast/scratch/hyaku/souji-r39/W1CritSources` (removed at exit; §8).
No tool installs or upgrades; nothing installed.

Read first, as instructed: `corpus/README.md` (frontier map), `corpus/QUALITY.md` (Q1–Q62),
`corpus/lessons/round-38.md` `## Gate` + `### Gate corrections (appended 2026-10-28, after wave 2)`
(the S239/S242 supersession precedent and the S243→S246 quote-cut correction), the frozen
`census/round-39/preregistration.txt`, and `corpus/lessons/round-39.md` `## Gate` / `## Named limits`.

The three candidates are already rows S247–S249 (`corpus/SOURCES.md:196-198`), admitted `mined` in
the r39 Gate (`corpus/lessons/round-39.md:39-41`). This review re-derives each page rather than
trusting the row text.

---

## 1. Candidate 1 — gitrevisions(7) `<rev>^{<type>}` ("`^<commit>` peeling")

**Claim it would ground.** C2 leg L2: a `--rev` naming a non-commit object (a blob) is the
could-not-evaluate class, not a finding. The tool resolves both revisions with
`cat-file -e <rev>^{commit}`:

```
$ grep -n '\^{commit}' tools/souji-citation-reconcile.py
217:    if git_proc(root, ["cat-file", "-e", commit + "^{commit}"]).returncode != 0:
247:    if git_proc(root, ["cat-file", "-e", args.rev + "^{commit}"]).returncode != 0:
253:        or git_proc(root, ["cat-file", "-e", args.register_rev + "^{commit}"]).returncode != 0:
303:        if git_proc(root, ["cat-file", "-e", row["receipt_rev"] + "^{commit}"]).returncode != 0:
```

and the counter's L2 leg builds a blob id and requires rc 2 + `REV-UNRESOLVED` on the new bytes
(`census/round-39/c2-counter.py:196-202`). This is the round's claim-bearing row.

**Does the page state the fact?** Yes, on both the installed page and the canonical URL.

```
$ MANWIDTH=100 man 7 gitrevisions | grep -n "SPECIFYING REVISIONS\|^ *<rev>\^{<type>}\|barf"
19:SPECIFYING REVISIONS
165:     <rev>^{<type>}, e.g. v0.99.8^{commit}
168:         be dereferenced anymore (in which case, barf). For example,  if  <rev>  is  a  commit-ish,
```

Installed page (git 2.56.0-1, `man -w gitrevisions` → `/usr/share/man/man7/gitrevisions.7.gz`):

```
$ MANWIDTH=100 man 7 gitrevisions | sed -n '165,168p'
     <rev>^{<type>}, e.g. v0.99.8^{commit}
         A suffix ^ followed by an object type name enclosed in brace pair  means  dereference  the
         object  at  <rev> recursively until an object of type <type> is found or the object cannot
         be dereferenced anymore (in which case, barf). For example,  if  <rev>  is  a  commit-ish,
```

Canonical URL `https://git-scm.com/docs/gitrevisions` (HTTP 200, 74,526 bytes, plain-text
extraction):

```
<rev>^{<type>} , e.g. v0.99.8^{commit} A suffix ^ followed by an object type name enclosed in brace
pair means dereference the object at <rev> recursively until an object of type <type> is found or
the object cannot be dereferenced anymore (in which case, barf).
```

Live page section id: `id="_specifying_revisions"`; the row's anchor line numbers (entry 165,
quote 166-168) are exact.

**Fact check (executed, isolated fixture).** `D=$(mktemp -d -p "$S" fixture.XXXXXX)`,
`git -C "$D" init -q`, `git -C "$D" rev-parse --show-toplevel` asserted equal to `$D` before the
first commit (`TOPLEVEL-OK ...`):

```
blob=63499e4ea8e096b831515ceb1d5a7593e4d87ae5
error: 63499e4ea8e096b831515ceb1d5a7593e4d87ae5^{commit}: expected commit type, but the object dereferences to blob type
fatal: Not a valid object name 63499e4ea8e096b831515ceb1d5a7593e4d87ae5^{commit}
blob_peel_rc=128
commit_peel_rc=0
```

So the row's `teaches` sentence ("refuses a blob or tree id") is true; the page says it ("barf").

**Defect 1 — the ≤25-word quote is cut at exactly the clause that decides the claim.** The filed
quote is 20 words and stops at "…cannot be dereferenced"; the deciding tail "anymore (in which case,
barf)" is omitted with no ellipsis. This is the r38 S243→S246 correction class verbatim
(`corpus/lessons/round-38.md`: "S243 cut its quote mid-sentence without an ellipsis at exactly the
clause that decides the reject"). A reader holding only the quote sees the search, not the refusal.
The complete sentence fits the cap: the extended quote is **25 words** (counted programmatically) and
is a verbatim substring of both the installed page and the live page:

```
S247 as filed words= 20
S247 extended words= 25
S247 filed-quote verbatim on gitrevisions: True
S247 extended verbatim on gitrevisions: True
```

**Defect 2 — duplicate scope, undeclared.** The *same paragraph* is on git-rev-parse(1), the page
row S099 already mines for "typed object-existence peeling":

```
$ MANWIDTH=100 man 1 git-rev-parse | grep -n "SPECIFYING REVISIONS\|^ *<rev>\^{<type>}\|barf"
273:SPECIFYING REVISIONS
419:     <rev>^{<type>}, e.g. v0.99.8^{commit}
422:         be dereferenced anymore (in which case, barf). For example,  if  <rev>  is  a  commit-ish,
```

```
same extended sentence on git-rev-parse page: True
```

S099 (`corpus/SOURCES.md:124`) scope: "plain verify wording versus typed object-existence peeling";
teaches: "object or commit peeling adds the documented existence or type check". S247 as filed
declares only "not `^<n>` parent selectors, not `^{object}`'s existence-only check" — it does not
name S099, so the registry now carries two authorities for one fact with no scope line separating
them. S240's exclusion ("not `^{commit}` type coercion", `corpus/SOURCES.md:189`) covers only the
cat-file row, not S099.

**Defect 3 — the notation in the scope cell and in the plan label is not git syntax.** gitrevisions(7)
defines `^{<type>}`; the scope cell writes "the `^<type>` type-coercion suffix", and the item prompt
calls the candidate "`^<commit>` peeling". `HEAD^commit` is not a revision:

```
$ git -C "$D" rev-parse 'HEAD^commit'
fatal: ambiguous argument 'HEAD^commit': unknown revision or path not in the working tree.
caret_no_brace_rc=128
```

"Peeling" is also the `<rev>^{}` (tag-peel) entry (`MANWIDTH=100 man 7 gitrevisions`, line 179), not
`^{commit}`.

**Verdict for candidate 1: ADMIT the fact, REJECT AS FILED.** It is the row the L2 claim rests on and
the page states it; as filed it carries a truncated deciding clause, an invalid notation, and an
undeclared duplicate of S099. Smallest safe correction: one appended supersession row (the r38
S244/S245 pattern; S247 stays as filed) carrying the 25-word quote above, scope spelling
`^{<type>}` and naming S099, and URL fragment `#_specifying_revisions`. If that row lands, the
lesson's row-count sentence and the Gate's row list must move together (`170 -> 173` becomes
`170 -> 174`), or C1's own calibration claim goes stale — the exact class C1 polices.

---

## 2. Candidate 2 — Python `ast.get_docstring`

**Claim it would ground.** C2 leg L4's instrument: the drift docstring is read through the AST, so a
missing docstring is `None` (not an exception) and the class-to-trigger lines are read as parsed
docstring text, never by slicing source. The counter does exactly that:

```
$ grep -n "get_docstring" census/round-39/c2-counter.py
137:    doc = ast.get_docstring(tree, clean=False) or ""
```

**Does the page state the fact?** Yes. Both `https://docs.python.org/3/library/ast.html` (page title
`ast — Abstract syntax trees — Python 3.15.2 documentation`, HTTP 200) and the host-version page
`https://docs.python.org/3.14/library/ast.html` carry the row's quote verbatim; the anchor exists:

```
$ grep -o 'id="ast.get_docstring"' docs.python.org_3_library_ast.html
id="ast.get_docstring"
S248 quote on /3: True  on /3.14: True
```

Page text:

```
ast. get_docstring ( node , clean = True ) ¶ Return the docstring of the given node (which must be
a FunctionDef, AsyncFunctionDef, ClassDef, or Module node), or None if it has no docstring.
```

Host behaviour (installed Python 3.14.8):

```
$ python3 -c "import ast; print(repr(ast.get_docstring(ast.parse('X = \"doc\"')))); print(repr(ast.get_docstring(ast.parse('\"\"\"real\"\"\"'))))"
None
'real'
```

**Duplicate scope?** No. The registry has no other `ast` row; S050 is `compile()` (parse/compile
without execution), S040 is pathlib resolution — both disjoint. `grep -niE '^\| S[0-9]+ \|.*(docstring|argparse)' corpus/SOURCES.md` returns only S248/S249.

**Limit to disclose (not a defect).** The row's `teaches` adds "a module constant named like a
docstring cannot satisfy the check", which the quoted sentence does not state; it is supplied by the
host run above. Q2 ("installed behaviour outranks prose") is satisfied by the run, but the row or
the lesson should carry the command so the inference is located.

**Verdict for candidate 2: ADMIT as filed.** Smallest safe correction (optional, one line): append
the host recheck command/result (`ast.get_docstring(ast.parse('X = "doc"'))` → `None`) to the row's
`recheck` cell or the lesson's Gate note.

---

## 3. Candidate 3 — Python `argparse` exit status

**Claim it would ground.** A disclosure only: `corpus/lessons/round-39.md:116` — "The `argparse`
exit-2 fact (S249) is a disclosure, not a claim: C2's distinction rides on the class names, not on
the status alone." It explains why `REV-UNRESOLVED` must carry the could-not-evaluate class instead
of exit 2 alone; no counter leg reads it.

**Does the page state the fact?** Yes, with one qualifier: the sentence is about an *invalid argument
list* passed to `parse_args`, i.e. a usage error, not every argparse exit. Both `/3` (title
`argparse — Parser for command-line options, arguments and subcommands — Python 3.15.2
documentation`) and `/3.14` carry the quote verbatim; the anchor exists:

```
$ grep -o 'id="exit-on-error"' docs.python.org_3_library_argparse.html
id="exit-on-error"
S249 quote on /3: True  on /3.14: True
```

Page text:

```
exit_on_error ¶ Normally, when you pass an invalid argument list to the parse_args() method of an
ArgumentParser , it will print a message to sys.stderr and exit with a status code of 2.
```

Host behaviour (installed Python 3.14.8):

```
$ python3 -c "...parser.parse_args(['--nope'])..."
usage: t [-h] [--rev REV]
t: error: unrecognized arguments: --nope
status 2
```

**Duplicate scope?** No. No argparse row exists; exit-status rows are S244 (merge-base: 0/1), S240
(cat-file: 0) and S034/S038 (timeout: 124) — different tools, different codes. The row's scope
correctly excludes `ArgumentParser.exit()`'s default status 0.

**Note.** The 15-word quote starts mid-sentence ("it will print…"); the antecedent that makes it a
*usage-error* fact sits outside the quote, and the full sentence is 30 words (over the cap). This
matches accepted r38 practice (S239's quote also starts mid-sentence), and the row's scope/anchor
supply the antecedent, so no correction is required.

**Verdict for candidate 3: ADMIT as disclosure.** No correction needed.

---

## 4. Does the round satisfy "at least one claim resting on a SOURCES row opened THIS round"?

Yes, before and after any correction:

- S247 (opened 2026-10-28) grounds C2 L2 — the claim's tool uses `^{commit}` at
  `tools/souji-citation-reconcile.py:247` and the counter's L2 leg requires the refusal class.
- S248 (opened 2026-10-28) grounds C2 L4's instrument (`census/round-39/c2-counter.py:137`).
- S249 is disclosure only (lesson line 116), so it does not carry the requirement by itself.

If the L1 rejects S247 rather than correcting it, the requirement still holds through S248's L4
instrument; correcting S247 is the safer reading.

## 5. Registry bookkeeping checks

```
$ git show ed30b7f5b77939c9073348d810730bc4f355708d:corpus/SOURCES.md | grep -cE '^\| S[0-9]{3,} '
170
$ git show HEAD:corpus/SOURCES.md | grep -cE '^\| S[0-9]{3,} '
173
$ git log --oneline -S '| S247 |' -- corpus/SOURCES.md | head -1
c0b007b round-39: C1 — 14 routed-defect corrections, r39 lesson with Gate/Mistakes, three source rows, gate-registry rows
$ git cat-file -e HEAD:corpus/lessons/round-39.md && echo lesson-exists
lesson-exists
```

- Gate's "registry grew 170 -> 173 rows" (lesson:44) is true at HEAD; base is 170.
- The three rows and the Gate landed in one commit (`c0b007b`), matching the index rule.
- `used-by` targets exist at HEAD (`corpus/lessons/round-39.md`), and that file names S247-S249, so
  the k1 direction of Q62 holds for these rows.
- Installed versions named by the rows are exact: `pacman -Q git` → `git 2.56.0-1`;
  `pacman -Q python` → `python 3.14.8-1`; `git --version` → `git version 2.56.0`;
  `python3 --version` → `Python 3.14.8`.

## 6. Per-check verdict table

| check | verdict |
|---|---|
| C1: gitrevisions page states the `^{<type>}` dereference/refusal fact (installed + live) | **PASS** |
| C2: host fixture reproduces blob refusal (rc 128) and commit success (rc 0) | **PASS** |
| C3: S247 ≤25-word quote contains the deciding clause | **FAIL** — 20-word cut before "anymore (in which case, barf)" |
| C4: S247 notation (`^{<type>}`, not `^<type>`/`^<commit>`) | **FAIL** (minor) — `HEAD^commit` rc 128 |
| C5: S247 declares its relation to S099's identical paragraph | **FAIL** — undeclared duplicate scope |
| C6: `ast.get_docstring` page states the quote on /3 and /3.14; anchor exists | **PASS** |
| C7: host `ast.get_docstring` returns `None` for a non-docstring constant | **PASS** |
| C8: `ast.get_docstring` duplicates an existing row's scope | **PASS** (none) |
| C9: argparse page states the quote on /3 and /3.14; anchor exists | **PASS** |
| C10: host argparse usage error exits 2 | **PASS** |
| C11: argparse duplicates an existing row's scope | **PASS** (none) |
| C12: at least one claim rests on a row opened this round | **PASS** (S247 → C2 L2; S248 → C2 L4) |
| C13: Gate row-count `170 -> 173` matches the revision | **PASS** |

## 7. Recommendations (admit/reject per candidate, with the located quote)

1. **gitrevisions(7) `<rev>^{<type>}` — ADMIT the fact; reject as filed; correct by one appended
   supersession row.** Located quote (25 words, verbatim on the installed page lines 166-168 and on
   the live page):
   > "dereference the object at <rev> recursively until an object of type <type> is found or the
   > object cannot be dereferenced anymore (in which case, barf)"

   The correction row must also scope against S099 and use `^{<type>}`; update the lesson's row
   count if it lands.
2. **Python `ast.get_docstring` — ADMIT.** Located quote (17 words, verbatim on /3 and /3.14):
   > "(which must be a FunctionDef, AsyncFunctionDef, ClassDef, or Module node), or None if it has
   > no docstring."
3. **Python `argparse` exit status — ADMIT as disclosure.** Located quote (15 words, verbatim on /3
   and /3.14):
   > "it will print a message to sys.stderr and exit with a status code of 2"

## 8. Scratch

Scratch root `/fast/scratch/hyaku/souji-r39/W1CritSources` held the five fetched pages and one
`mktemp -d` git fixture; the fixture was removed by the same command (`cleaned=0`), and the whole
scratch root was removed at seat exit. Nothing was written outside the report path and that scratch
root; no git/jj mutation ran outside the fixture; no lane file was edited.
