# W1ConnSources — registry adjacency for the three r39 candidate sources

Seat: connector (leaf, no dispatch). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Measured at lane HEAD `2201778e7736af82e7d8a42dec2494f115bf3923` (base `ed30b7f5b77939c9073348d810730bc4f355708d`
verified an ancestor: `git merge-base --is-ancestor ed30b7f5… HEAD` → exit 0).
Registry: `corpus/SOURCES.md`. Census tool: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh`
(read-only use; the fleet-root `scripts/` tree was not modified).
Scratch: `/fast/scratch/hyaku/souji-r39/W1ConnSources` (removed at the end; see §9).
Tooling: nothing installed. Host `git 2.56.0-1`, `python3 3.14.8`.

The three candidates are already registry rows: **S247** (gitrevisions `^<type>`), **S248**
(`ast.get_docstring`), **S249** (argparse usage-error exit 2) — `corpus/SOURCES.md:196-198`. This
report therefore measures their *adjacency*: what the census prints when they land, which existing
rows share their host/path family, and whether each new fact falls inside or outside those rows'
scope cells.

## 1. Census row-count delta (base bytes vs landed bytes)

Base bytes were materialised faithfully rather than through `--file` on a bare file, so that the
census' E11 `used-by` resolution still saw a real lane root:

```
S=/fast/scratch/hyaku/souji-r39/W1ConnSources
mkdir -p "$S/base/corpus"
# symlink every lane top-level entry except corpus, and every corpus entry except SOURCES.md
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show ed30b7f5…:corpus/SOURCES.md > "$S/base/corpus/SOURCES.md"
sha256sum "$S/base/corpus/SOURCES.md" …/corpus/SOURCES.md
```

```
92a1dae0bc9b4e1fe6f66134225051610c6084fc1144313b168d98c813f14b72  …/base/corpus/SOURCES.md
5773b62cb97f939f718c23144b51330808fc946830333168c9551ab726c13e96  …/corpus/SOURCES.md
279  …/base/corpus/SOURCES.md
```

```
bash scripts/sources-census.sh census --file "$S/base/corpus/SOURCES.md"
file	rows	170
file	tier.A	161
file	tier.B	6
file	tier.C	3
file	status.mined	140
file	status.queued	14
file	status.rejected	16
FLEET	rows	170
FLEET	missing	0
rc=0

bash scripts/sources-census.sh census --file …/souji-shokunin/corpus/SOURCES.md
file	rows	173
file	tier.A	164
file	tier.B	6
file	tier.C	3
file	status.mined	143
file	status.queued	14
file	status.rejected	16
FLEET	rows	173
FLEET	missing	0
rc=0
```

**Delta the census prints: `rows 170 → 173` (+3), `tier.A 161 → 164` (+3), `status.mined 140 → 143`
(+3); `tier.B 6`, `tier.C 3`, `queued 14`, `rejected 16`, `missing 0` unchanged.** Fleet-wide run at
HEAD: `souji rows 173` and `FLEET rows 3728`, `FLEET missing 0`; the fleet total therefore carries
the same +3 [INFERENCE: no sibling lane's SOURCES was measured at both ends].

Lesson claim check — `corpus/lessons/round-39.md:44` says “The registry grew 170 -> 173 rows, all
tier A `mined`”. Census agrees exactly (170→173; 161→164 A; 140→143 mined). PASS.

Byte-level check that no existing cell moved:

```
git -C … diff --numstat ed30b7f5… HEAD -- corpus/SOURCES.md
5	0	corpus/SOURCES.md
git -C … diff ed30b7f5… HEAD -- corpus/SOURCES.md | grep -c '^-[^-]'
0
```

The five added lines are the provenance paragraph (`corpus/SOURCES.md:20`), one blank line, and
S247/S248/S249. Zero deleted lines ⇒ no existing status/recheck/used-by/scope cell was rewritten,
which is what the provenance sentence claims.

## 2. W04 consequence — duplicate URL across scopes is allowed

The census' URL key is host+path with the fragment and any trailing slash removed
(`scripts/sources-census.sh:600-604`):

```awk
function url_of(s,   u,n) {
    if (match(s,/https?:\/\/[^[:space:]|]+/)) { u=substr(s,RSTART,RLENGTH)
      sub(/#[^ ]*$/,"",u); sub(/\/$/,"",u); sub(/^[A-Za-z]+:\/\//,"",u)
```

so the three keys are:

| candidate | registry URL | census URL key |
|---|---|---|
| S247 | `https://git-scm.com/docs/gitrevisions` | `git-scm.com/docs/gitrevisions` |
| S248 | `https://docs.python.org/3/library/ast.html#ast.get_docstring` | `docs.python.org/3/library/ast.html` |
| S249 | `https://docs.python.org/3/library/argparse.html#exit-on-error` | `docs.python.org/3/library/argparse.html` |

Two rules read that key (`scripts/sources-census.sh:643-651`):

```awk
scope_key=u SUBSEP scope
if (u!="" && (u in url_seen) && !(scope_key in url_scopes))
  printf "%s\tW04\t%s duplicate url %s across scopes\n",lane,id,u
if (u!="" && (scope_key in url_scopes) && status!="rejected" &&
    url_scope_nonrejected[scope_key] &&
    teaches !~ /supersedes S[0-9]{3}/)
  printf "%s\tE04\t%s duplicate url %s within scope %s\n",lane,id,u,scope
```

`W04` is a warning: only `E` codes set `findings` (`:740`), and the header states “W04 same URL
across scopes (warnings do not affect clean lanes)” (`:33`). `E04` is the error, and only for the
*same URL **and** the same scope cell* with no `supersedes` token.

Observed counts, base vs landed:

```
bash scripts/sources-census.sh validate --file …/corpus/SOURCES.md | grep -c 'W04'   → 47 (HEAD)
bash scripts/sources-census.sh validate --file "$S/base/corpus/SOURCES.md" | grep -c 'W04' → 47 (base)
```

`validate` printed `file	ok	…` and `rc=0` at both revisions; no `E03`/`E04`/`E11` line appeared.
**No new W04 and no new E04: the three rows share their normalised URL with no earlier row** (see
§3). So the warning consequence is: had a page been re-cited under a different scope, the census
would print `W04 … duplicate url … across scopes` and still exit 0 — the pattern the registry
already uses 47 times (e.g. `S106 duplicate url docs.python.org/3/library/json.html across scopes`).
A future row re-citing `ast.html`/`argparse.html` under a *different* fragment would warn the same
way, and only an identical scope string would raise `E04`.

## 3. Adjacency table (what the Gate block can cite)

Membership rule used, stated so it is falsifiable: for each candidate, ring 1 = rows with the same
normalised URL; ring 2 = every row on the same **host**; inside ring 2, a row is scope-adjacent iff
its `scope` or `teaches` cell names the candidate's mechanism (machine test, regex per candidate).
Rows in ring 2 with no such term are outside by absence of the term — that is the whole remainder,
listed by id so nothing is skipped.

```
python3 -B /fast/scratch/hyaku/souji-r39/W1ConnSources/adj.py   (11-cell split of ^| S### | rows, url_of replicated)
rows parsed: 173
```

### 3a. S247 — gitrevisions `^<type>`

Ring 1: `S247` only. Ring 2 host `git-scm.com`: **55 rows** —
S001,S002,S003,S004,S005,S006,S007,S008,S011,S032,S033,S035,S036,S042,S044,S045,S046,S047,S049,
S057,S058,S059,S060,S063,S071,S078,S079,S080,S081,S089,S090,S091,S092,S093,S097,S099,S102,S115,
S116,S117,S123,S124,S125,S126,S127,S128,S215,S232,S236,S237,S238,S239,S240,S244,S247.
Mechanism-naming rows: **S080, S099, S239, S240**.

| row | scope cell (quoted) | verdict |
|---|---|---|
| S247 | “the `^<type>` type-coercion suffix the r39 C2 revision-resolution step relies on; not `^<n>` parent selectors, not `^{object}`'s existence-only check” | **inside** — the row itself |
| S099 (`git-rev-parse`) | “plain verify wording versus typed object-existence peeling” (teaches: “object or commit peeling adds the documented existence or type check”) | **inside the scope's subject, on a different page.** S099's cell already names typed peeling; S247 grounds the same fact class from `gitrevisions` instead of `git-rev-parse`. Different URLs ⇒ neither W04 nor E04, and neither row supersedes the other. Gate must attribute per page: S099 = `--verify` conversion, S247 = the `^{<type>}` suffix grammar. |
| S240 (`git-cat-file -e`) | “the object-existence probe the commit arm's resolve step uses; **not `^{commit}` type coercion**, not the batch modes” | **outside by explicit exclusion** — S247 fills exactly the slot S240 excludes. No contradiction: S240's teaches (“an unresolvable commit cell is therefore a distinct class from a non-ancestor”) is the consumer of S247's rule. |
| S239 (`git-merge-base`) | “the ancestor predicate's exit-status contract that the r38 commit arm reads; not merge-base's other modes, **not gitrevisions syntax**” | **outside by explicit exclusion** — S247 supplies the excluded syntax. |
| S244 (live successor of S239) | “supersedes S239 — the section name in S239 is wrong … the quote, URL and line numbers are unchanged” | **outside** — same git-merge-base subject. Note: S244's scope cell does **not** repeat S239's “not gitrevisions syntax” exclusion (see risk R-b). |
| S080 (`git-for-each-ref`) | “explicit ref-namespace selection and format placeholders” | **outside** — the match is only the word “peeled” in its teaches (`%(*objectname)` yields a peeled tag target), a for-each-ref placeholder, not revision grammar. |
| other 50 host-mates | — | **outside** by absence of any type-coercion/peeling/revision-syntax term in `scope`+`teaches`. |

### 3b. S248 — `ast.get_docstring`

Ring 1: `S248` only. Ring 2 host `docs.python.org`: **14 rows** —
S040,S050,S061,S067,S074,S104,S105,S106,S107,S108,S226,S229,S248,S249. Mechanism-naming row: **S050**.

| row | scope cell (quoted) | verdict |
|---|---|---|
| S248 | “the ast-only module-docstring read the r39 C2 L4 analyser uses; not source text slicing, not `ast.get_source_segment`” | **inside** — the row itself |
| S050 (`functions.html#compile`) | “parse/compile without execution of a source text, not runtime correctness” | **outside** — S050 scopes `compile()` and its `SyntaxError`; `get_docstring` is a different API and the new fact is a *return value* (`None`), not a raise. Shared family is only “static source analysis without execution”; no claim overlap, no supersedes needed. |
| S040 pathlib, S061 lstrip, S067/S074 subprocess, S104/S105/S106 json types, S107/S108 RecursionError, S226/S229 tempfile | topics quoted in §3a of the registry; none names `ast` | **outside** by absence. |
| S229 (`/3/library/tempfile.html`, 3.15.2 line, **rejected**) | “the same gettempdir and mkdtemp teaching at the 3.15.2 documentation line, which is not the interpreter this lane runs” | not a path-family member, but the precedent matters: S229 was rejected because the 3.15.2 line differed from the lane interpreter **and** the teaching was a duplicate. Neither condition transfers: S248 is the first `ast` row (no duplicate teaching) and its fact was confirmed on the lane interpreter (see §4). |

### 3c. S249 — argparse usage-error exit 2

Ring 1: `S249` only. Ring 2 host `docs.python.org`: same 14 rows. Mechanism-naming rows within the
host: **none** (`argparse|exit status|exit code|usage error|status code` matched no other row).

| row | scope cell (quoted) | verdict |
|---|---|---|
| S249 | “argparse's own usage-error exit status (2), which a tool's declared exit map must not contradict; not the `ArgumentParser.exit()` method's default status 0” | **inside** — the row itself |
| all 13 other docs.python.org rows | — | **outside** by absence; no row on that host documents an exit status at all. |
| S244 / S239 (`git-merge-base`) | “the ancestor predicate's exit-status contract …”; teaches “exit with status 0 if true, or with status 1 if not”, errors “a non-zero status that is not 1” | **outside** (git-specific predicate) — and non-conflicting: those rows assign 0/1, S249 assigns 2 to usage error. |
| S093 / S081 (`git-diff --quiet`) | “--quiet output and --exit-code semantics; no completeness claim about supplied paths” / “silent comparison whose status distinguishes equal from different trees” | **outside** — 0/1 semantics only. |
| relation to C2 | — | S249 is the only SOURCES row that explains why exit 2 cannot be a lone sentinel for “could not evaluate”. It is inside **C2's** contract, not inside any other row's scope. |

## 4. Source-byte verification of the three quotes (coverage of the rows themselves)

```
MANWIDTH=100 man 7 gitrevisions | sed -n '160,172p'
```
line 165 = `<rev>^{<type>}, e.g. v0.99.8^{commit}`; lines 166-168 =
“A suffix ^ followed by an object type name enclosed in brace pair means dereference the object at
<rev> recursively until an object of type <type> is found or the object cannot be dereferenced
anymore (in which case, barf).” → matches S247's anchor “entry line 165, quote 166-168”.
Live page `https://git-scm.com/docs/gitrevisions` HTTP 200, 74526 bytes; `SPECIFYING REVISIONS`
present; same sentence present.

```
curl -sS -o $S/ast.html https://docs.python.org/3/library/ast.html   → http=200 bytes=362029
banner: ['Python 3.15.2 documentation']
quote found: True
```
The S248 quote “(which must be a FunctionDef, AsyncFunctionDef, ClassDef, or Module node), or None
if it has no docstring.” is verbatim at § `ast.get_docstring(node, clean=True)`.

```
curl -sS -o $S/argparse.html https://docs.python.org/3/library/argparse.html → http=200 bytes=334734
banner: Python 3.15.2 documentation
curl -sS -o $S/argparse314.html https://docs.python.org/3.14/library/argparse.html → http=200 bytes=330759
banner: Python 3.14.10 documentation
```
S249's sentence is present on **both** pages, at § `exit_on_error`:
“Normally, when you pass an invalid argument list to the parse_args() method of an ArgumentParser,
it will print a message to sys.stderr and exit with a status code of 2.”
Measurement note for the Gate: a raw `grep -c 'exit with a status code of 2'` returns **0** on both
files because the sentence spans a line break in the extracted text; after tag-strip + whitespace
normalisation it is found on both. Anyone re-checking must normalise whitespace.

Interpreter facts on the lane's own `python3 3.14.8`:

```
version 3.14.8
no-docstring: None
with-docstring: 'd'
exit() default code = 0
```
```
python3 -c "import argparse; argparse.ArgumentParser(prog='t').parse_args(['--nope'])"
usage: t [-h]
t: error: unrecognized arguments: --nope
rc=2
```
⇒ S248's “returns None rather than raising” holds on 3.14.8, and S249's “not the
`ArgumentParser.exit()` method's default status 0” holds (default code 0). Both anchors already
disclose the 3.15.2-page / 3.14.8-interpreter split.

Operational consequence of S247's teaching, measured in a throwaway repo:

```
D=$(mktemp -d "$S/gitprobe.XXXX"); git -C "$D" init -q
toplevel=/fast/scratch/hyaku/souji-r39/W1ConnSources/gitprobe.zuxe
guard=ok                      # [ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ]
blob=587be6b4… tree=a1dffc7a… commit=149647d1…
git -C "$D" cat-file -e <blob>^{commit}   → error: …^{commit}: expected commit type, but the object dereferences to blob type / fatal: Not a valid object name …   rc=128
git -C "$D" cat-file -e <tree>^{commit}   → expected commit type, but the object dereferences to tree type                                                    rc=128
git -C "$D" cat-file -e <commit>^{commit} → (silent)                                                                                                            rc=0
git -C "$D" cat-file -e 000…0^{commit}    → fatal: Not a valid object name …                                                                                    rc=128
git -C "$D" cat-file -e deadbeef^{commit} → fatal: Not a valid object name …                                                                                    rc=128
git -C "$D" cat-file -e nosuchref^{commit}→ fatal: Not a valid object name …                                                                                    rc=128
git -C "$D" cat-file -t <blob> → blob (rc 0);  git -C "$D" cat-file -t 000…0 → rc 128
```
So `^{commit}` refuses a blob **and** a tree, exactly as S247's teaches says, and the exit code is
128 — **not** 1, which is what keeps it disjoint from `--is-ancestor`'s 1 (S244/S239).

## 5. Exit-2 class census in the repaired tool (what S249 is load-bearing for)

```
python3 -B tools/souji-citation-reconcile.py --root "$D" --rev <blob> --register /nonexistent.tsv
REFUSAL REV-UNRESOLVED: --rev 587be6b4… does not resolve to a commit          rc=2
python3 -B tools/souji-citation-reconcile.py --root "$D" --rev 000…0 --register /nonexistent.tsv
REFUSAL REV-UNRESOLVED: --rev 0000000000000000000000000000000000000000 does not resolve to a commit   rc=2
python3 -B tools/souji-citation-reconcile.py --root "$D" --rev <commit> --register /nonexistent.tsv
REFUSAL USAGE: unreadable register /nonexistent.tsv: [Errno 2] No such file or directory …           rc=2
python3 -B tools/souji-citation-reconcile.py --root "$D" --rev <commit> --register x --items y
souji-citation-reconcile.py: error: unrecognized arguments: --items y                                 rc=2
```

Three different classes, one exit status. That is precisely S249's teaching (“a tool whose own usage
errors already exit 2 cannot use 2 alone to mean could-not-evaluate; the class name must carry the
distinction”), and the tool does carry it (`REFUSAL REV-UNRESOLVED` vs `REFUSAL USAGE` vs argparse's
own `error:`). The disclosure is load-bearing, not decorative.

## 6. Contradictions and risks (stated, not smoothed)

- **R-a (S099 overlap).** Two rows now name typed object-existence peeling: S099 on the `git-rev-parse`
  page and S247 on `gitrevisions`. Not a registry error (different URLs ⇒ no W04/E04; no `supersedes`
  needed), but a Gate sentence that says “typed peeling” without naming the page is ambiguous. No
  edit is required by the contract; the Gate block should cite S247 for the suffix and S099 for
  `--verify`.
- **R-b (dropped exclusion).** S239's scope carried “not gitrevisions syntax”; its live successor S244
  does not repeat it. No claim depends on the clause, and S247 now supplies the syntax — but the
  exclusion is no longer asserted anywhere. Advisory only; S244 is a frozen landed row this wave.
- **R-c (class breadth).** S247's teaches names blob/tree refusal and is silent about an **absent**
  object, which lands in the same `rc=128` class (measured above). The tool's message is honest
  (“does not resolve to a commit”), so nothing overclaims; a Gate sentence that said the row
  distinguishes “wrong type” from “absent” would overclaim. S247's scope cell does not say that.
- **R-d (fragment stripping).** Because `url_of` removes the fragment, S248/S249 occupy the whole
  `ast.html` / `argparse.html` pages. A later row on either page under a *different* scope will emit
  `W04` (the S106/`json.html` pattern); an identical scope string without `supersedes` would be
  `E04`. The Gate should not read “no W04 today” as “these pages are exhausted”.
- **R-e (version line).** S248/S249 cite the 3.15.2 documentation line while the lane runs 3.14.8.
  Both anchors disclose it, both facts were confirmed on 3.14.8 (§4), and `recheck=365d` is set — so
  the S229 rejection reason does not transfer. A future recheck against the 3.14 page line is the
  honest cadence.
- **R-f (fleet arithmetic).** `FLEET rows 3728` is measured at HEAD only; the +3 attribution to this
  lane is arithmetic from the measured 170→173, not a second fleet measurement [INFERENCE].

## 7. Verdicts

| check | command | observed | verdict |
|---|---|---|---|
| V1 row-count delta | `sources-census.sh census --file` on base and landed bytes | `rows 170` → `rows 173`; `tier.A 161→164`; `mined 140→143`; queued/rejected/B/C/missing unchanged; rc 0 both | **PASS** — delta is exactly +3 rows, all tier-A mined |
| V2 W04 consequence | `sources-census.sh validate --file` both revisions, `grep -c W04` | `47` and `47`; `file ok`; rc 0; no E03/E04/E11 | **PASS** — duplicate URL across scopes is warning-only; the three rows add no warning and no error |
| V3 adjacency completeness | `adj.py` over 173 rows (11-cell split, `url_of` replicated) | git-scm host-mates 55 (hits S080,S099,S239,S240); docs.python.org host-mates 14 (S248 hits S050; S249 hits none) | **PASS** — every host-mate enumerated; inside/outside stated per row in §3 |
| V4 quote location | `man 7 gitrevisions`; two `curl` fetches + normalised text search | S247 at man lines 166-168; S248 verbatim on the 3.15.2 ast page; S249 on both the 3.15.2 and 3.14.10 argparse pages at § `exit_on_error` | **PASS** (raw `grep` without whitespace normalisation returns 0 — measurement caveat recorded) |
| V5 operational consequence | fixture repo `git cat-file -e <rev>^{commit}` for blob/tree/commit/absent | 128/128/0/128; `cat-file -t` blob→0, absent→128 | **PASS** — S247's refusal rule holds; 128 keeps it disjoint from `--is-ancestor`'s 1 |
| V6 exit-2 classes | `tools/souji-citation-reconcile.py` on blob, absent 40-hex, unreadable register, unknown option | three classes, all rc 2, class strings distinct | **PASS** — S249's disclosure is load-bearing for C2 |
| V7 no existing cell moved | `git diff --numstat ed30b7f5… HEAD -- corpus/SOURCES.md` | `5 0`; `grep -c '^-[^-]'` = 0 | **PASS** — provenance sentence at `corpus/SOURCES.md:20` is accurate |

No check was left unrun. Nothing in this report contradicts C1/C2/C3's predicates; the only
advisories are R-a…R-f, none of which requires a byte change in a frozen row.

## 8. Write scope

Wrote exactly one file: this report. Read-only git only (`rev-parse`, `merge-base --is-ancestor`,
`log`, `show`, `diff`, `cat-file`). No commit, push, stash, checkout, switch, reset, pull, or jj
mutation anywhere. The fleet repo, sibling lanes, `.ufo/state/`, `templates/`, `scripts/`, and the
frozen round-39 inputs were not written. No PATH directory was touched.

## 9. Scratch

`/fast/scratch/hyaku/souji-r39/W1ConnSources` (base registry copy, `adj.py`, three fetched HTML
pages, one throwaway git repo) was removed with `rm -rf` after the measurements; `ls` of the parent
after removal is empty of this seat's tree.
