# S58Scribe6 — dispatched source review and draft delivery

## Behavior and axes

Axes: quote fidelity; primary-source authority; bounded C2 scope; historical-byte preservation; auditable capture provenance. Read round-58 preregistration before source work. Frozen predicate commit supplied by assignment: `e7f64f30324e8ddb3f2266302daa9066054cdbb3`; not independently inspected as a commit by this seat.

Reopened gitrevisions, CommonMark 0.31.2, git-cat-file, and secondary candidate MDN live. **Agrees** with existing S284/S285 and the round-58 lesson Gate quotations. This is lane-dispatched source review, **not independent non-author judgment**, acceptance execution, or canonical judgment.

## Gate draft — access 2026-11-04

Capture paths below are relative to `.ufo/waves/round-58/w1/S58Scribe6/`.

| Source | URL / locator | Located quotation (whitespace-separated words) | Decision |
|---|---|---|---|
| S284 | https://git-scm.com/docs/git-cat-file, OPTIONS `-t`; `git-cat-file.html:2234-2235` | “Instead of the content, show the object type identified by <object>.” (11) | Agree: official primary source supports type observation for the supplied object argument. For raw identity, do not supply an already-peeled expression. |
| S285 | https://git-scm.com/docs/gitrevisions, SPECIFYING REVISIONS `<rev>^{<type>}`; `gitrevisions.html:2388-2389` | “dereference the object at <rev> recursively until an object of type <type> is found” (14) | Agree: reject the inference that successful commit peeling proves the original named object is a commit. Flip: observe the raw object's type. |
| Existing S283 reopened | https://spec.commonmark.org/0.31.2/#html-comment, §6.6; `commonmark-0.31.2.html:12365-12366` | “An HTML comment consists of `<!-->`, `<!--->`, or `<!--`, a string of characters not including the string `-->`, and `-->`” (23) | Scope warning only: §6.6 expressly includes short forms; neither receipt repair nor a correction note establishes Markdown-renderer equivalence. |
| Secondary candidate, excluded | https://developer.mozilla.org/en-US/docs/Web/HTML/Comments → https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Comments; `mdn-comments.html:1587` | “comments cannot be nested.” (4) | REJECTED as authority for C2 receipt confinement/type/header semantics, or as a substitute for CommonMark parsing. Flip only if the proposed claim is narrowed to HTML comment guidance; use the primary CommonMark definition for Markdown. |

Git quote context matters: `gitrevisions.html:2389-2390` continues with inability to dereference and the documented failure. The 14-word excerpt describes success search, not the entire refusal contract. The adjacent `^{object}` paragraph at :2398-2401 explicitly describes existence without dereferencing; it does not certify that the original object is a commit.

CommonMark §4.6 was also located at capture :3326-3327 (comment block start/end conditions), but §6.6, not that block-only rule, is the requested S283 scope warning. Literal comment syntax above is code-delimited, not bare table-cell HTML.

## Registry draft disposition

Targeted registry search found latest live rows S284 and S285; a separate max-ID extraction also returned S280–S285. Therefore S286 was the next unused observed ID, not reserved. Initial coordination proposed S286–S288, but no rows were written.

L1 integration direction, verbatim:

> Do not expand registry: L1 already opened both official pages; S284/S285 are sole proposed rows this round. Please review these two+lesson located quotes (11/14 words), report agree/disagree and retain opened capture receipts. New source rows unnecessary; your other candidates can be honest draft-only exclusions, never represented as admitted.

Accordingly, no duplicate Git row or additional admitted row is proposed. For the originally requested fresh-row deliverable, the following is an **unsubmitted, draft-only exclusion**, not an admission or expansion recommendation. S286 is provisional and must be reallocated if used elsewhere:

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S286 (unsubmitted draft) | MDN — Using HTML comments — https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Comments | docs | B | candidate authority for C2 receipt-interface semantics | Notes; opened capture :1587 | REJECTED: HTML comment guidance supplies no receipt path, Git raw-type, or revision-header contract; flip: narrow the claim to HTML guidance, not C2 acceptance or Markdown equivalence | rejected draft only | 2026-11-04 | on-change | — |

No production registry, lesson, knowledge entry, counter, or historical assessment byte was changed by this seat.

## Knowledge / lesson draft

**Raw object identity is not recursive type resolution.** S284 grounds observation of the type identified by an object argument. S285 explains that a type suffix recursively dereferences toward a requested type. Thus a peeled commit result alone is insufficient evidence that an unpeeled annotated-tag OID names a commit. This is primary-source support for the bounded C2 annotated-tag refusal rationale, not a demonstration that the gate implementation refuses it.

**Keep the milestone separate from renderer repair.** C1 corrects two recorded self-assessment discrepancies. C2 enumerates absolute path, traversal, intermediate symlink escape, annotated tag-object revision, and conflicting revision-header refusals, with three honest receipts to preserve. CommonMark §6.6 remains a scope warning: comment grammar and inline parsing cannot be certified by those receipt cases. Historical counters and their open harms remain untouched.

## Capture manifest

| File | Bytes | SHA-256 |
|---|---:|---|
| gitrevisions.html | 74654 | 1ab7124a99e6919e6882be82f77c629ac8fe623bb36af56a749fd4db1919070b |
| commonmark-0.31.2.html | 514698 | c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d |
| git-cat-file.html | 79488 | 91805d9aec858f88581552fc1fe105a40a649544f872e72e6daff210a113e910 |
| mdn-comments.html | 175822 | 0c793938a9bf918b97afb273a2bf8af5a7d58a3359f0cc7ea218949e30aade97 |

Every capture is below 1 MiB. Hash/size observations precede copying; copy completed with explicit EXIT=0. No post-copy recheck was run.

## Command receipts and limitations

Exact source-acquisition commands, retained from the tool transcript (including unnecessary initial shell `ls`, not reproduced as new execution):

```sh
cd /fast/scratch/hyaku/souji-r58/S58Scribe6 && curl -sSL --max-filesize 950000 -w 'gitrevisions http=%{http_code} bytes=%{size_download}\n' -o gitrevisions.html 'https://git-scm.com/docs/gitrevisions' && curl -sSL --max-filesize 950000 -w 'commonmark http=%{http_code} bytes=%{size_download}\n' -o commonmark-0.31.2.html 'https://spec.commonmark.org/0.31.2/' ; ls -l
```

Observed output:

```text
gitrevisions http=200 bytes=74654
commonmark http=200 bytes=514698
total 580
-rw-r--r-- 1 vgpnk vgpnk 514698 Nov  4 11:46 commonmark-0.31.2.html
-rw-r--r-- 1 vgpnk vgpnk  74654 Nov  4 11:46 gitrevisions.html
EXIT: not explicitly emitted by this command; tool returned normally. Separate curl statuses were not retained. HTTP success is observed, not a fabricated shell-status receipt.
```

```sh
cd /fast/scratch/hyaku/souji-r58/S58Scribe6 && curl -sSL --max-filesize 950000 -w 'git-cat-file http=%{http_code} bytes=%{size_download}\n' -o git-cat-file.html 'https://git-scm.com/docs/git-cat-file'
```

```text
git-cat-file http=200 bytes=79488
EXIT: not explicitly emitted; tool returned normally. Not rerun merely to decorate this report.
```

```sh
curl -sSL --max-filesize 950000 -w 'MDN http=%{http_code} bytes=%{size_download} url=%{url_effective}\n' -o /fast/scratch/hyaku/souji-r58/S58Scribe6/mdn-comments.html https://developer.mozilla.org/en-US/docs/Web/HTML/Comments; rc=$?; printf 'EXIT=%s\n' "$rc"
```

```text
MDN http=200 bytes=175822 url=https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Comments
EXIT=0
```

Capture metadata commands:

```sh
sha256sum /fast/scratch/hyaku/souji-r58/S58Scribe6/*.html && wc -c /fast/scratch/hyaku/souji-r58/S58Scribe6/*.html
sha256sum /fast/scratch/hyaku/souji-r58/S58Scribe6/git-cat-file.html /fast/scratch/hyaku/souji-r58/S58Scribe6/mdn-comments.html && wc -c /fast/scratch/hyaku/souji-r58/S58Scribe6/git-cat-file.html /fast/scratch/hyaku/souji-r58/S58Scribe6/mdn-comments.html; rc=$?; printf 'EXIT=%s\n' "$rc"
```

Output is the four manifest hashes/sizes above; the first command saw only the first two captures (589352 total), without explicit EXIT emission. The second saw the latter two (255310 total), explicit EXIT=0.

Registry inspection used the grep tool (`^\| ?S2[0-9]{2}`) and this exact fact command:

```sh
grep -oE '\bS[0-9]{2,3}\b' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md | sort -Vu | tail -6 | tr '\n' ' '
```

Output: `S280 S281 S282 S283 S284 S285 `; explicit EXIT was not emitted. This shell search/paging choice was unnecessary; the specialized targeted grep already established the latest rows. No claim of a canonical source census follows from it.

Preservation and cleanup command (cwd `/fast/scratch/hyaku/souji-r58`):

```sh
mkdir -p /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-58/w1/S58Scribe6 && cp /fast/scratch/hyaku/souji-r58/S58Scribe6/gitrevisions.html /fast/scratch/hyaku/souji-r58/S58Scribe6/commonmark-0.31.2.html /fast/scratch/hyaku/souji-r58/S58Scribe6/git-cat-file.html /fast/scratch/hyaku/souji-r58/S58Scribe6/mdn-comments.html /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-58/w1/S58Scribe6/; rc=$?; printf 'copy EXIT=%s\n' "$rc"; if test "$rc" -eq 0; then rm -r /fast/scratch/hyaku/souji-r58/S58Scribe6; printf 'scratch removal EXIT=%s\n' "$?"; fi
```

Observed: `copy EXIT=0`; `scratch removal EXIT=0`.

## Gates, touched surfaces, out-of-scope legs

- Exercised: live HTTP source acquisition; located quotation review against saved captures; registry/lesson read; capture hashes/sizes; preservation and own-scratch removal.
- Findings: S284/S285 and 11/14-word Gate quotes agree with opened primary documents. Secondary MDN candidate rejected for the assigned C2 authority. CommonMark warns against Markdown-repair overclaim.
- Unrun: C1 measurement/correction probes, all five C2 refusal probes, all three preservation receipts, before/after control arms, selftest, mutations, canonical Rust judgment, non-author verification, builds, lint, formatters. No passing result inferred from their contracts or lesson prose.
- Touched: this report and its four HTML captures only; own scratch created then removed. No production edits, fleet/sibling edits, Git/jj commands or mutations, commits, pushes, installs, package transactions, services, configuration changes, runtime dispatch, or task dispatch.
- Known limit: early acquisition commands did not print explicit EXIT; preserve that omission rather than invent it. New registry expansion withheld under L1's integration direction.

## Self-assessment (not a gate)

Accuracy 4: quoted primary text is located; early explicit EXIT values unavailable. Completeness 4: requested fresh row retained only as an excluded draft under L1 direction. Clarity 4: decisions and execution limits separated, but command provenance is lengthy. Actionability 4: sources and locators are supplied; integration remains solely L1's. Conciseness 4: full receipts increase length. Overall 4.0. Improvements: emit EXIT at initial acquisition; use only specialized targeted registry search. User-agreement check: this is a source-review delivery, not C1/C2 closure or independent judgment.

Report: .ufo/waves/round-58/w1/S58Scribe6.md
