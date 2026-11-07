## Status
STATUS: PARTIAL — S126, S138 and S118 corroborating record re-verified; S114 page reachable but tested r24 quote absent; DOI target still returns no body.

## Evidence
- Probe outputs (2026-10-25; lane base `e78ac7c4837b81b634db4a927605a751a7f006ba`): bounded `curl -L --max-time 30`; downloaded to `/var/tmp/souji-r27-LabSliceFetch/` only.
- S114 `https://git-scm.com/docs/git-prune`: HTTP 200, 27,870 bytes; fetched-byte fixed-string test `prune removes` absent. Verdict: still absent (page exists, tested r24 quoted wording does not).
- S126 `https://docs.gtk.org/gio/method.File.trash.html`: HTTP 200, 19,401 bytes; `G_IO_ERROR_NOT_SUPPORTED` present. Verdict: re-verified.
- S138 `https://qiita.com/koseki/items/f1af58f1ec1693f0536a`: HTTP 200, 129,655 bytes; `6700` present. Verdict: re-verified.
- S118 DOI `https://doi.org/10.1109/SEQUEN.1997.666900`: HTTP 202, 0 bytes; verdict still unreachable. Crossref `https://api.crossref.org/works/10.1109/SEQUEN.1997.666900`: HTTP 200, 3,063 bytes; `Compression and Complexity of SEQUENCES` present, corroborating metadata only.
- S123/S124/S131/S133 skipped as lane-internal own-work, as directed.

## Findings
1. S114 remains quote-absent in fetched page bytes. Prior location: `corpus/lessons/round-24.md:231`, quote ≤25 words: “git-prune sentence present; `[1]` vs `(1)`” (opened this run).
2. S126 fetched exact method page, and its required error token occurs in bytes. Source: `https://docs.gtk.org/gio/method.File.trash.html`, quote: “G_IO_ERROR_NOT_SUPPORTED” (opened this run).
3. S138 fetched Qiita page and found `6700`. Source: `https://qiita.com/koseki/items/f1af58f1ec1693f0536a`, quote: “6700” (opened this run).
4. S118 DOI remained bodyless; Crossref resolves the named venue metadata, not the IEEE article span. Prior location: `corpus/lessons/round-24.md:232`, quote: “DOI → IEEE 202, 0 bytes, twice” (opened this run).
