# W1ScoutGitRev

Scout only. No lane source edit. Scratch `/fast/scratch/hyaku/souji-r39/W1ScoutGitRev` held the fetched HTML and was removed (`SCRATCH_GONE`). No tool install.

## Axes

Quote fidelity (verbatim, ≤25 words), locator (section + man line numbers + live anchor), claim fit (C2 `--rev` peel, not the ancestor predicate S239/S244 already cite).

## Check 1 — installed page and the peel entry

Command:

```
MANWIDTH=100 man 7 gitrevisions
```

`man -w 7 gitrevisions` → `/usr/share/man/man7/gitrevisions.7.gz`. `git --version` → `git version 2.56.0`. `pacman -Q git` → `git 2.56.0-1` (query only). Footer of the same man page:

```
Git 2.56.0                                   2026-09-27                             GITREVISIONS(7)
```

`nl -ba` on `MANWIDTH=100 man 7 gitrevisions` (blank lines numbered). Section heading:

```
    19	SPECIFYING REVISIONS
```

The type peel is the brace entry, not a bare `^<type>` form. The unbraced entry immediately above it is parent selection:

```
   152	     <rev>^[<n>], e.g. HEAD^, v1.5.1^0
   153	         A suffix ^ to a revision parameter means the first parent of  that  commit  object.   ^<n>
   154	         means the <n>th parent (i.e.  <rev>^ is equivalent to <rev>^1). As a special rule, <rev>^0
   155	         means  the  commit  itself  and is used when <rev> is the object name of a tag object that
   156	         refers to a commit object.
```

Peel entry (heading line 165, body 166-171; `^{object}` / `^{tag}` continue 173-177 and are a different rule):

```
   165	     <rev>^{<type>}, e.g. v0.99.8^{commit}
   166	         A suffix ^ followed by an object type name enclosed in brace pair  means  dereference  the
   167	         object  at  <rev> recursively until an object of type <type> is found or the object cannot
   168	         be dereferenced anymore (in which case, barf). For example,  if  <rev>  is  a  commit-ish,
   169	         <rev>^{commit}  describes  the  corresponding  commit  object.  Similarly,  if  <rev> is a
   170	         tree-ish, <rev>^{tree} describes the corresponding tree object.  <rev>^0 is  a  short-hand
   171	         for <rev>^{commit}.
   173	         <rev>^{object} can be used to make sure <rev> names an object that exists, without requir‐
   174	         ing  <rev>  to  be a tag, and without dereferencing <rev>; because a tag is already an ob‐
   175	         ject, it does not have to be dereferenced even once to get to an object.
```

**Verdict: pass.** Section `SPECIFYING REVISIONS` (line 19). Peel entry `<rev>^{<type>}` at lines 165-171. The prompt's `<rev>^<type>` spelling is not the peel on this page; `<rev>^[<n>]` (152-156) selects a parent. `<rev>^0` is the shorthand for `<rev>^{commit}` (170-171), which is why line 154 can say `^0` means the commit itself.

## Check 2 — ≤25-word quote

Joined prose (justification spaces collapsed). Two verbatim spans; neither alone says "requires the object to be a commit":

| span | words | lines | text |
|---|---|---|---|
| failure rule | 19 | 167-168 | until an object of type &lt;type&gt; is found or the object cannot be dereferenced anymore (in which case, barf) |
| commit example | 11 | 168-169 | if &lt;rev&gt; is a commit-ish, &lt;rev&gt;^{commit} describes the corresponding commit object |

Word counts are `str.split()` on those strings (19 and 11).

**Verdict: pass, with a limit.** The page does not say `<rev>^{commit}` requires the named object to already be a commit. It says dereference until type `<type>` or barf, and that a commit-ish peels to the commit object. An annotated tag of a commit is a commit-ish and succeeds. `^{object}` (173-175) is the existence check that does **not** dereference and must not be cited as this rule.

## Check 3 — canonical URL, anchor, access date

Command:

```
curl -fsSL --max-time 40 -A souji-r39-scout -D - -o <scratch>/gitrevisions.html https://git-scm.com/docs/gitrevisions
```

Response: `HTTP/2 200`, `date: Wed, 28 Oct 2026 18:04:31 GMT`, `last-modified: Mon, 26 Oct 2026 14:52:06 GMT`, `content-type: text/html; charset=utf-8`, 74526 bytes. Banner text: `gitrevisions last updated in 2.56.0`.

The entry's own anchor element:

```
<dt class="hdlist1" id="Documentation/gitrevisions.txt-emltrevgtlttypegtemegemv0998commitem">
<a id="Documentation/gitrevisions.txt-revtypeegv0998commit" class="anchor"
   href="#Documentation/gitrevisions.txt-revtypeegv0998commit"></a>
```

Rendered body matches the man sentence, including "in which case, barf" and "commit-ish".

**Canonical URL (the href the page emits):**

https://git-scm.com/docs/gitrevisions#Documentation/gitrevisions.txt-revtypeegv0998commit

The `dt` id is a second fragment on the same node: `#Documentation/gitrevisions.txt-emltrevgtlttypegtemegemv0998commitem`. Section slug `#_specifying_revisions` is the heading only.

**Access date: 2026-10-28.**

**Verdict: pass.**

## Check 4 — which r39 claim, and why S239/S244 do not cover it

**Claim: C2 operability, the `--rev` / `--register-rev` resolution leg, not C1 and not C3.**

`census/round-39/preregistration.txt` lines 47-50 and 55-62: R11 is that `tools/souji-citation-reconcile.py` never resolves `--rev`, so a mistyped or non-commit revision collapses to "not an ancestor" and exits 1; the new contract is exit 2 `REFUSAL REV-UNRESOLVED` for an unresolvable `--rev` (L1) and for `--rev` naming a blob (L2). L3 keeps an unresolvable `--register-rev` at exit 2.

Committed at HEAD `2201778e7736af82e7d8a42dec2494f115bf3923` (file clean). `git blame -L 247,250 -- tools/souji-citation-reconcile.py` attributes the gate to `bbd9b9746ba9e3c5d640bf095bbad18a00c80e83`:

```
if git_proc(root, ["cat-file", "-e", args.rev + "^{commit}"]).returncode != 0:
    sys.stderr.write(
        "REFUSAL REV-UNRESOLVED: --rev %s does not resolve to a commit\n" % args.rev)
    return 2
```

Same suffix on `--register-rev` (lines 251-256) and on the commit cell (line 217). The `^{commit}` suffix is the gitrevisions peel. The man page is what makes a non-commit-ish name fail that probe instead of being fed to `merge-base --is-ancestor`.

**S239 and S244 do not already cover it.** Both rows in `corpus/SOURCES.md` (lines 188 and 193) cite `git-merge-base(1)` `--is-ancestor`, not `gitrevisions(7)`.

- S239 scope cell: "the ancestor predicate's exit-status contract that the r38 commit arm reads; not merge-base's other modes, not gitrevisions syntax". Teach: exit 0 if true, 1 if not, any other non-zero is an error.
- S244 supersedes S239 only on the section name (`OPERATION MODES` line 20, entry 41-43; `OPTIONS` at line 52 is `-a`/`--all`). It keeps the same quote and the same predicate. `corpus/lessons/round-38-verifier-spotcheck.md` line 114 admits that correction.

That predicate answers a different question: given two commits, is one an ancestor (status 1 = finding, other non-zero = error). It does not say how to decide that a revision is a commit. C2's bug was the collapse of "does not resolve" into that status-1 finding. The peel is the prior gate. Applying S239/S244 to a blob id is the defect R11 names, not a citation of the peel.

Adjacent, not a substitute: S240 (`corpus/SOURCES.md` line 189) is `git cat-file -e` existence only, and its scope cell excludes `^{commit}` type coercion. S247 (line 196) already points at this same gitrevisions entry, but its URL has no fragment and its quote stops at "cannot be dereferenced", dropping "anymore (in which case, barf)".

**Verdict: pass.** The fact grounds C2 `--rev` resolution (`cat-file -e <rev>^{commit}` → `REFUSAL REV-UNRESOLVED`, exit 2). S239/S244 are the ancestor exit-status contract and say they are not gitrevisions syntax.

## Unresolved

- Not run here: a blob or missing name under `git cat-file -e <rev>^{commit}`. The page says "barf" when `<type>` cannot be reached; it does not name blobs. That a blob fails the probe is an application of that sentence, not a second quote.
- HTML fragment was checked in the saved document (ids present, body matches the man sentence). The fragment is not a separate HTTP resource.
