# R40w2critic09 — falsify S251–S254 (source quotes, locations, URLs, access dates)

Seat: R40w2critic09 (critic). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. Landed instrument commit: 128e412b0ced3c243dc27c3dd3332054a611bc2e (SOURCES rows added at `corpus/SOURCES.md:203-206`). Read-only: no counter, fixture, preregistration, SCORECARD, LOG, corpus or commit was touched. Scratch: /fast/scratch/hyaku/souji-r40/w2/R40w2critic09 (removed; see end).

## Verdict

**FALSIFIED** for S252 and S253 (the quoted text is not verbatim at the cited location; S252 also carries a claim its quote does not support).
**SAFE** for S251 (quote verbatim, location exact) and S254 (quote verbatim at lines 158/173/180/182/193, tag and URL resolve, bytes identical to the live tag).
One minor unsourced annotation under S251 is recorded below; it does not change the S251 verdict.

## Axes attacked

1. Verbatim quote of each registry row (`corpus/SOURCES.md:203-206`) against the snapshot and the live page.
2. Location the row names (section, line numbers, anchor) against the snapshot.
3. URL reachability and that the live bytes equal the snapshot (sha256).
4. Access date (`2026-10-28`) against the host date.
5. Mirrored copies of each quote: `corpus/lessons/round-40.md:15-18`, `corpus/knowledge/*-r40.md`.

## Commands and real output

### A. Snapshot integrity (all five snapshots)

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/sources && sha256sum -c SHA256SUMS
codecs.html: OK
git-merge-base.1.txt: OK
gvfs-trashitem-1.62.0.c: OK
inspect-cleandoc.txt: OK
inspect.html: OK
```

### B. Live re-fetch of each cited URL (all into scratch) and sha comparison

```
$ curl -sSfL -o gvfs-1.62.0-trashitem.c https://raw.githubusercontent.com/GNOME/gvfs/1.62.0/daemon/trashlib/trashitem.c
$ sha256sum gvfs-1.62.0-trashitem.c
3a8f8cbb057ac3bb8d4ba4901d43f8fd1abcd89b9ff095ef927999154af3d25b  gvfs-1.62.0-trashitem.c      # == snapshot, MATCH
$ curl -sSfL -o inspect.html https://docs.python.org/3/library/inspect.html && sha256sum inspect.html
9e740c60462d2648ecd5b9ae1cf5ee96f2fed5e312fb56cae639385c5415a0d6  inspect.html                 # == snapshot, MATCH
$ curl -sSfL -o codecs.html https://docs.python.org/3/library/codecs.html && sha256sum codecs.html
023ec448648e7089efe4b4c25a167e491fa7f93d1cbf116662c6596e71158a4c  codecs.html                  # == snapshot, MATCH
$ curl -sSfL -o git-merge-base.html https://git-scm.com/docs/git-merge-base && sha256sum git-merge-base.html
2432d0108d1e76f0d17540bb8b706310502702bbf05c6a32adf5a283fc0776d1  git-merge-base.html          # HTML page; not byte-comparable to the man snapshot, quote checked by text below
$ for u in https://git-scm.com/docs/git-merge-base https://docs.python.org/3/library/inspect.html https://docs.python.org/3/library/codecs.html; do curl -sSfL -o /dev/null -w "%{http_code} $u\n" "$u"; done
200 https://git-scm.com/docs/git-merge-base
200 https://docs.python.org/3/library/inspect.html
200 https://docs.python.org/3/library/codecs.html
$ git ls-remote --tags https://github.com/GNOME/gvfs.git 'refs/tags/1.62.0*'
3bed1a6d5ab1683f1e3ae2a5b695845fcb3ef9f6	refs/tags/1.62.0
046d5423ef100255f554eff84388f8ba765a2182	refs/tags/1.62.0^{}
$ curl -sSfL -o gvfs-at-tagcommit.c https://raw.githubusercontent.com/GNOME/gvfs/046d5423ef100255f554eff84388f8ba765a2182/daemon/trashlib/trashitem.c && sha256sum gvfs-at-tagcommit.c
3a8f8cbb057ac3bb8d4ba4901d43f8fd1abcd89b9ff095ef927999154af3d25b  gvfs-at-tagcommit.c          # tag commit bytes == snapshot, MATCH
$ date -u +%F
2026-10-28
```

Note: `curl https://api.github.com/repos/GNOME/gvfs/git/refs/tags/1.62.0` returned HTTP 403 (unauthenticated API limit); the tag was confirmed with `git ls-remote` instead.

Tooling: no tool installed. `git 2.56.0`, `curl`, `man`, `python3 3.14.8` were already on the host. No pacman, no ~/.local/bin write.

### C. S251 — git-merge-base(1) `--is-ancestor`  → SAFE (quote and location), one unsourced annotation

```
$ MANWIDTH=100 man git-merge-base | sha256sum
45f91e37e113df8651fb125c93e293bb48d8cc46140e4ac95c553547c9ddb043  -   # == snapshot git-merge-base.1.txt
$ MANWIDTH=100 man git-merge-base | cat -n | sed -n 41,43p
    41	     --is-ancestor
    42	         Check if the first <commit> is an ancestor of the second <commit>, and exit with status  0
    43	         if true, or with status 1 if not. Errors are signaled by a non-zero status that is not 1.
$ grep -n '^[A-Z][A-Z ]*$' census/round-40/sources/git-merge-base.1.txt
20:OPERATION MODES
52:OPTIONS
```

Quote check (whitespace-normalised, since the man page has a double space before `0`): `"Check if the first <commit> is an ancestor of the second <commit>, and exit with status 0 if true, or with status 1 if not"` → FOUND in snapshot lines 42-43 and in the live HTML (`FOUND count=1`). Location `§ OPERATION MODES --is-ancestor` = snapshot line 41 under header line 20: correct.

Annotation drift (`corpus/SOURCES.md:203`, S251 cell6): the trailing clause "— a commit is an ancestor of itself, so the equal case passes" is NOT in S251's text (`grep -n -i 'itself|reflexive|equal'` on both the snapshot and the live HTML returns nothing). The behaviour itself is true, checked in a scratch fixture:

```
$ D=$(mktemp -d -p /fast/scratch/hyaku/souji-r40/w2/R40w2critic09) && git -C "$D" init -q && test "$(git -C "$D" rev-parse --show-toplevel)" = "$D" && echo toplevel-ok
toplevel-ok
$ (commit A, commit B on top) ; B=$(rev-parse HEAD); A=$(rev-parse HEAD~1)
$ git -C "$D" merge-base --is-ancestor $B $B; echo "equal rc=$?"
equal rc=0
$ git -C "$D" merge-base --is-ancestor $B $A; echo "backwards rc=$?"
backwards rc=1
$ git -C "$D" merge-base --is-ancestor $A $B; echo "forward rc=$?"
forward rc=0
```

So the reflexive behaviour is real and the C1 strictness argument holds, but the sentence is attributed to S251 without being in S251. Minor source-scope overreach; the knowledge file `corpus/knowledge/git-strict-descendant-relation-r40.md:17-18` states it correctly as an observed property of `--is-ancestor`, which the strictness rule then depends on.

### D. S252 — Python `inspect.cleandoc`  → FALSIFIED (quote not verbatim at cited page; claim beyond quote)

Registry quote (`corpus/SOURCES.md:204`, cell6; mirrored at `corpus/lessons/round-40.md:16` and `corpus/knowledge/docstring-class-continuation-lines-r40.md:12`):
`"Any whitespace that can be uniformly removed from the second line onwards is removed"`

```
$ python3 extract.py census/round-40/sources/inspect.html "Any whitespace that can be uniformly removed from the second line onwards is removed"
'Any whitespace that can be uniformly removed from the second line onwards is removed' MISSING count= 0
$ python3 extract.py census/round-40/sources/inspect.html "uniformly removed from the second line onwards is removed"
'uniformly removed from the second line onwards is removed' FOUND count= 1
$ sed -n 1210,1211p census/round-40/sources/inspect.html
<p>All leading whitespace is removed from the first line.  Any leading whitespace
that can be uniformly removed from the second line onwards is removed.  Empty
$ grep -rn --exclude-dir=.git -F "Any leading whitespace" census/round-40/sources/inspect.html
census/round-40/sources/inspect.html:1210:<p>All leading whitespace is removed from the first line.  Any leading whitespace
```

Verdict on the quote: the cited docs page (anchor `id="inspect.cleandoc"` at `census/round-40/sources/inspect.html:1206`, text at 1210-1211, live sha equal) reads **"Any leading whitespace that can be uniformly removed..."**. The registry's wording (`Any whitespace …`, missing `leading`) is not in that page. It IS the wording of the installed interpreter docstring:

```
$ sed -n 4p census/round-40/sources/inspect-cleandoc.txt
Any whitespace that can be uniformly removed from the second line
$ python3 -c "import inspect;print(inspect.cleandoc.__doc__)" > $S/cleandoc-runtime.txt
$ diff <(sed 1d census/round-40/sources/inspect-cleandoc.txt) $S/cleandoc-runtime.txt && echo identical
identical
```

So the quote is verbatim from the installed `inspect.cleandoc.__doc__` (snapshot line 4), but the row attributes it to the docs-page URL and the docs snapshot, where it does not appear. Quote drift at the cited location.

Scope drift: the row's claim `"that a docstring's lines after the first are continuations of one logical block"` (cell4) and the annotation `"the lines after the first form one block whose uniform indentation marks them"` (cell6) are not in either text. `grep -n -i 'continuation\|logical block\|one block' census/round-40/sources/inspect.html census/round-40/sources/inspect-cleandoc.txt` finds no such statement; the sources only define whitespace normalisation for lines from the second onward. The C2 "one entry" reading is therefore the lane's inference, not what S252 says, and it is presented as S252's content.

### E. S253 — Python `codecs` § Error Handlers, `replace`  → FALSIFIED (quote not verbatim)

Registry quote (`corpus/SOURCES.md:205`, cell6; mirrored at `corpus/lessons/round-40.md:17` and `corpus/knowledge/drift-record-invalid-utf8-r40.md:11`):
`"Replace with a replacement marker. On decoding, use U+FFFD, the official REPLACEMENT CHARACTER"`

```
$ sed -n 592,596p census/round-40/sources/codecs.html
<tr class="row-even"><td><p><code class="docutils literal notranslate"><span class="pre">'replace'</span></code></p></td>
<td><p>Replace with a replacement marker. On
encoding, use <code class="docutils literal notranslate"><span class="pre">?</span></code> (ASCII character). On
decoding, use <code class="docutils literal notranslate"><span class="pre">�</span></code> (U+FFFD, the official
REPLACEMENT CHARACTER). Implemented in
$ python3 extract.py census/round-40/sources/codecs.html "Replace with a replacement marker. On decoding, use U+FFFD, the official REPLACEMENT CHARACTER"
... MISSING count= 0
$ python3 extract.py census/round-40/sources/codecs.html "On decoding, use U+FFFD, the official REPLACEMENT CHARACTER"
... MISSING count= 0
```

Extracted text of the entry (html stripped): `Replace with a replacement marker. On encoding, use ? (ASCII character). On decoding, use � (U+FFFD, the official REPLACEMENT CHARACTER). Implemented in replace_errors().` The second occurrence in the § Error Handlers body (`snapshot line 734`, text: `Substitutes ? (ASCII character) for encoding errors or � (U+FFFD, the official REPLACEMENT CHARACTER) for decoding errors.`) is also not the quote.

Drift: the quote splices two sentences of the entry (`On encoding, use ? (ASCII character).` is elided with no ellipsis), drops the `(` before `U+FFFD`, and drops the closing `)`. The quoted string is not a substring of the cited text. Location is right (`#error-handlers` anchor at snapshot line 564, `replace` row 592-596, `replace_errors` anchor present); the URL resolves (200) and the live sha equals the snapshot. The substantive claim (undecodable byte becomes U+FFFD) is supported by that text; the quote as written is not.

### F. S254 — GNOME/gvfs 1.62.0 `trashitem.c`  → SAFE

```
$ grep -nF 'trashinfo = g_strdup_printf ("%s/info/%s.trashinfo", trashpath, basename);' census/round-40/sources/gvfs-trashitem-1.62.0.c
158:  trashinfo = g_strdup_printf ("%s/info/%s.trashinfo", trashpath, basename);
$ sed -n 173p ...  →  "Trash Info", "Path",
$ sed -n 180p ...  →  decoded = g_uri_unescape_string (orig, NULL);
$ sed -n 182p ...  →  if (g_path_is_absolute (decoded))
$ sed -n 193p ...  →  "Trash Info", "DeletionDate",
```

Quote, lines, group and keys all verbatim. The tag resolves (`refs/tags/1.62.0` → `046d5423…` peeled), the bytes at the peeled commit equal the snapshot (sha `3a8f8cbb…`), and the raw URL at tag name equals it too. Access date 2026-10-28 matches the host date. The lessons table (`corpus/lessons/round-40.md:18`) writes the quote with literal backslash-escaped quotes (`\"%s/info/…\"`); the raw bytes do not contain backslashes, so the lessons copy is a presentation mismatch, not a content mismatch. The knowledge copy (`corpus/knowledge/origin-record-format-gvfs-r40.md:13`) is verbatim.

## Drift table

| Row | Quote | Location | URL | Access date | Verdict |
|---|---|---|---|---|---|
| S251 | verbatim (whitespace-normalised) | exact (man l.41-43, OPERATION MODES) | resolves, live text has quote | 2026-10-28 ok | SAFE; annotation "ancestor of itself" unsourced in S251 (behaviour true: `equal rc=0`) |
| S252 | NOT verbatim at cited page ("Any leading whitespace" in docs; "Any whitespace" only in installed docstring) | docs page line 1210-1211; quote lives at inspect-cleandoc.txt:4 | resolves, sha equal | 2026-10-28 ok | FALSIFIED: quote drift + "continuations of one logical block" not in source |
| S253 | NOT verbatim (two sentences spliced, `(`/`)` and `�` dropped) | codecs.html 592-596 / 564 anchor | resolves, sha equal | 2026-10-28 ok | FALSIFIED: quote drift |
| S254 | verbatim, lines 158/173/180/182/193 | exact | tag 1.62.0 resolves; bytes equal | 2026-10-28 ok | SAFE |

## Consequence for the round

The C2 knowledge entry (`corpus/knowledge/docstring-class-continuation-lines-r40.md:12`) and the C3 entry (`corpus/knowledge/drift-record-invalid-utf8-r40.md:11`) both present these non-verbatim strings as quotations. The rows are the round's own ledger, so a reader who checks the cited page will fail the check. The smallest correction (not applied here; read-only seat): quote `Any leading whitespace that can be uniformly removed from the second line onwards is removed` (inspect.html:1210-1211) for S252 and drop the "one logical block" clause, or cite the installed docstring for the shorter wording; quote `On decoding, use � (U+FFFD, the official REPLACEMENT CHARACTER)` verbatim (or with an explicit ellipsis) for S253.

## Scratch

Scratch dir: /fast/scratch/hyaku/souji-r40/w2/R40w2critic09 — removed after this report was written (`rm -rf -- "$S"`).
No file was written outside this report and the scratch dir. No git/jj mutation was run in the lane.
