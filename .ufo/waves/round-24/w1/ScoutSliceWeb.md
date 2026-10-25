# ScoutSliceWeb — quarantine-slice web rows (round 24, wave 1)

## Status
STATUS: PASS — all 4 web rows hand-checked live; 3 `payload-absent` rows are checker false positives (quote present), 1 `unreachable` row is present via IEEE-hosted record + full-text mirror.

## Evidence
- Revisions: lane HEAD f9db2181647d91470a724a12d626bd6106805076; shokuknow HEAD 8b94c5c12c0521e4cd9ed8e5b6939afd8518c715 (read-only, nothing written).
- Fetch: curl 8.23.0, 2026-10-25 09:20 UTC, scratch /var/tmp/souji-r24-ScoutSliceWeb/ (removed). Text = HTML with script/style dropped, tags stripped, entities unescaped, whitespace collapsed.
- Web-id check: `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md` lines 12/16/24/36 are S114 (docs, git-scm.com), S118 (paper, doi.org), S126 (docs, docs.gtk.org), S138 (community, qiita.com). S123/S124/S131/S133 (lines 21/22/29/31) are `own-work` local artifacts — not web. Expected set S114 S118 S126 S138 confirmed.
- HTTP results:
  - `https://git-scm.com/docs/git-prune` → 200, 27870 B (sha256 5d3dcd3b6588ce51…)
  - `https://docs.gtk.org/gio/method.File.trash.html` → 200, 19401 B (sha256 a5af1920b16444e0…)
  - `https://qiita.com/koseki/items/f1af58f1ec1693f0536a` → 200, 129547 B; `.md` source endpoint → 200, 4047 B
  - `https://doi.org/10.1109/SEQUEN.1997.666900` → redirects to `https://ieeexplore.ieee.org/document/666900/` → **202, 0 B** (retried: 202, 0 B)
  - `http://xplorestaging.ieee.org/ielx4/5423/14659/00666900.pdf?arnumber=666900` (Crossref `link` for this DOI) → 200, HTML record page with abstract metadata
  - `https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf` → 200, 254930 B PDF (pdftotext 26.08.0)
  - `https://api.crossref.org/works/10.1109/SEQUEN.1997.666900` → 200
- Exact-substring check of the register's quote strings against fetched text (python3 -B):
  - `171 S114 'Note that unreachable, packed objects will remain. If this is not desired, see git-repack(1).' {'S114': False}`
  - `S114 prefix-to-git-repack True`
  - `174 S126 'Sends file to the “Trashcan”, if possible. This is similar ... emptying t' {'S126': True}`
  - `177 S138 '## gc.auto (6700)' {'S138': False, 'S138md': True}`
  - `S118 '“roughly the same” and “roughly contained.”' True`; `'Definitions as set intersection problems' True`

## Findings

| id | URL | reachable? | quote found verbatim? | verdict |
|---|---|---|---|---|
| S114 | https://git-scm.com/docs/git-prune | yes (200) | near-verbatim: the web page renders the cross-reference as `[1]`, the register quote has `(1)` | `present` |
| S118 | https://doi.org/10.1109/SEQUEN.1997.666900 | cited URL no (IEEE 202, 0 B); IEEE staging record + PDF mirror yes | yes, in the IEEE abstract and the full-text PDF | `present` (the cited URL itself is unreachable) |
| S126 | https://docs.gtk.org/gio/method.File.trash.html | yes (200) | yes, verbatim in rendered text | `present` |
| S138 | https://qiita.com/koseki/items/f1af58f1ec1693f0536a | yes (200) | yes, verbatim in the page's markdown source; HTML renders it as a heading | `present` |

1. **S114** — register `/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md:171`. Located text (git-scm page, § DESCRIPTION): "Note that unreachable, packed objects will remain. If this is not desired, see git-repack[1] ." The register quote "...see git-repack(1)." matches the **installed man page** that the anchor cites (`man git-prune`, git 2.56.0, line 18: "Note that unreachable, packed objects will remain. If this is not desired, see git-repack(1)."). The miss comes from rendering: the man page writes `(1)` and git-scm writes `[1]`. This is not a fabrication. Side notes: the register lists the same quote twice; the git-scm page's newest listed version is 2.43.0, while the anchor says 2.56.0.
2. **S118** — register line 361 (class: "the cited source could not be fetched, so no quote was checked"). That `unreachable` class is still accurate for the canonical DOI target from this host. The SOURCES row's quoted spans are present elsewhere:
   - The IEEE staging record (`xplorestaging.ieee.org/document/666900`) has an `"abstract"` field beginning "Given two documents A and B we define two mathematical notions: their resemblance r(A, B) and their containment c(A, B) that seem to capture well the informal notions of".
   - The PDF mirror, line 11, reads: "the informal notions of “roughly the same” and “roughly contained.”"
   - The PDF mirror, line 71, reads: "2    Definitions as set intersection problems".
   - **Separate defect in SOURCES line 16:** the venue is given as "IEEE Symposium on Foundations of Computer Science / SEQUENCES 1997". Crossref `container-title` says "Proceedings. Compression and Complexity of SEQUENCES 1997 (Cat. No.97TB100171)", pages 21-29, author A.Z. Broder. The "Foundations of Computer Science" attribution is wrong.
3. **S126** — register line 174. Located text (§ Description): "Sends file to the “Trashcan”, if possible. This is similar to deleting it, but the user can recover it before emptying the trashcan." The raw HTML is `Sends <code>file</code> to the &#8220;Trashcan&#8221;`, so the quote matches only after tag-strip and entity-unescape. The register quote is cut off at 120 characters ("emptying t"). The row's other teaching, `G_IO_ERROR_NOT_SUPPORTED` on system mounts, is also on the page. [INFERENCE] The checker's miss is a normalisation gap (markup or entities). I did not check which of its eleven folds failed.
4. **S138** — register line 177. `## gc.auto (6700)` is line 17 of the Qiita markdown source (`.../f1af58f1ec1693f0536a.md`). The HTML renders it as a heading (`id="gcauto-6700"`), with the text "gc.auto (6700) When there are approximately more than this many loose objects in the repository, git gc --auto will pack them." The `## ` is markdown syntax, so it never appears in the rendered page. Scope note, not a verdict input: the post is dated 2015-06-13 and quotes `git help config (v1.9.2)`, not a current git-config.
5. Every non-web slice row (S123, S124, S131, S133) cites a `lanes/souji/...` own-work artifact. Those are outside this item.

## Attack log
- A1 (register calibration): the register defines `payload-absent` as "**the fabrication class**", meaning every source fetched cleanly and the quote is in none of them. All 3 web `payload-absent` rows in the slice (S114, S126, S138) are false positives: the quote is present once the text is normalised for man-page cross-reference style, HTML markup/entities, or markdown heading markers. These rows must not be refused as fabrications. Whoever appends them should take the quote from the rendered target or the cited man page, so a future checker run matches.
- A2: S118's quote is supported by the IEEE-hosted abstract and the full-text mirror, but its venue field is wrong (Finding 2). If S118 is appended, correct the venue first.
- No tools installed or upgraded. No shokuknow file or register was edited.
