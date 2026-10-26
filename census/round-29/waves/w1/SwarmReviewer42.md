# SwarmReviewer42 — Broder source choice (F3 duplicate verdicts)

## Status

STATUS: PARTIAL — the Broder source is sound and the row is admissible at tier B under corrected wording; the staged S118 as written is not admissible (wrong venue, source cell names only a non-dereferenceable DOI, `used-by` names a path absent at HEAD), and the landed S217 carries two residual wording defects.

## Evidence

Lane revision `b8cb4b31ce80e2e3314b88e85d40ea9873180804` (`git -C …/souji-shokunin rev-parse HEAD`), base `691dd29…`; no lane write, no install, no pacman call. Scratch `/var/tmp/souji-r29-SwarmReviewer42/`, removed at close.

1. Fetch (2026-10-26):
```
$ curl -sSL -o broder97.pdf -w 'http=%{http_code} bytes=%{size_download} type=%{content_type}\n' \
    https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf
http=200 bytes=254930 type=application/pdf
$ sha256sum broder97.pdf
da1227992d4a308f9f6f9f99893fd7b00c26e6cf757b1372f426074c101ef56b
$ pdfinfo broder97.pdf | head -4
Producer: Acrobat Distiller 3.0 for Windows
CreationDate: Thu Apr  2 13:05:56 1998 -03
Pages: 9
```
The delivered snapshot under `.ufo/waves/round-29/w1/sources/broder97resemblance.pdf` hashes to the same `da122799…`, so the pin is reproducible from the URL.

2. Decode (`pdftotext` 26.08.0, poppler). Plain decode reproduces the quoted snapshot exactly:
```
$ pdftotext broder97.pdf plain.txt && sha256sum plain.txt && wc -c plain.txt
3ba1e117c6267c72e6c20e37d5b0b98e76bdb4fcf6429f49204cb3196d28325d  plain.txt
21669 plain.txt
```
matches `.ufo/waves/round-29/w1/sources/SHA256SUMS:2` and the entries' `verified-at`. (`pdftotext -layout` gives `ddf97f6b…`, 24939 B — a flag difference, not a bad pin; SwarmScribe25's mismatch note is explained by it.)

3. Text matches the DOI record (Crossref `https://api.crossref.org/works/10.1109/SEQUEN.1997.666900`, HTTP 200):
```
title = "On the resemblance and containment of documents"
author = A.Z. Broder (single)
container-title = "Proceedings. Compression and Complexity of SEQUENCES 1997 (Cat. No.97TB100171)"
event = Compression and Complexity of SEQUENCES 1997, Salerno, Italy, acronym SEQUEN-97; page 21-29; issued = [[null]]
```
PDF: `plain.txt:1` title, `:2` "Andrei Z. Broder", `:3` "digital Systems Research Center", `:6` "Abstract", 9 pages numbered 1–9. No venue imprint, no IEEE/ISBN/DOI string, no running header — only page-number footers; the copy therefore cannot be identified as the proceedings PDF from its own bytes, and its pagination is 1–9, not 21–29.

4. Located lines (snapshot line numbers): abstract `:7-9`; § 2 heading `:67`; resemblance/containment definitions `:100-114`; "Hence the resemblance is some number between 0 and 1" `:115`; "roughly the same" also `:22`, `:134-135`, `:142`; "preliminary version" `:139`.

5. Candidate quotes, checked in bytes and word count (`|` absent):
- `:8-9` "resemblance r(A, B) and their containment c(A, B) that seem to capture well the informal notions of “roughly the same” and “roughly contained.”" — 23 words, verbatim across the line break.
- `:115-117` "the containment is some number between 0 and 1 and if A is a contiguous subsequence of B then c(A, B) = 1" — 23 words.

6. DOI probe, the entry's own command:
```
$ curl -sS -o /dev/null -w '%{http_code} %{size_download} %{url_effective}\n' -L https://doi.org/10.1109/SEQUEN.1997.666900
202 0 https://ieeexplore.ieee.org/document/666900/
```
Header chain: 302 (doi.org) → 301 (http→https ieeexplore) → 202, `content-length: 0`, `x-amzn-waf-action: challenge`. The "202/0 bytes" claim is verified.

## Verdict

**Admissible: yes**, as a tier-B `paper` row whose scope is the vocabulary of document-similarity verdicts, on these conditions: (a) the copy is named as what it is — a Princeton course-archive copy of the author's preliminary version (the host is `www.cs.princeton.edu/courses/archive/…`, not the author; the bytes carry Broder's DEC address, and `:139` says "preliminary version"); (b) the DOI is named as the canonical identifier; (c) the opened PDF and its pins are in the row, because the DOI yields no bytes. Congruence with the registered paper rests on title, single author, abstract and 9-page length, not on any venue mark in the copy — an honest limitation, satisfied here.

**DOI in the anchor:** acceptable but misplaced alone. Contract v1 puts the canonical URL or DOI in `source` and section/page plus revision in `anchor`. Crossref carries no issued date (`issued: [[null]]`), so the DOI is the only revision identifier available and belongs in at least one cell; recommended is both cells:

- `source`: `A. Z. Broder, On the resemblance and containment of documents — https://doi.org/10.1109/SEQUEN.1997.666900 (canonical DOI; bytes opened: https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf, sha256 da1227992d4a308f9f6f9f99893fd7b00c26e6cf757b1372f426074c101ef56b)`
- `anchor`: `§ Abstract (copy p. 1); § 2 "Definitions as set intersection problems" (copy p. 2); In: Compression and Complexity of SEQUENCES 1997 (Cat. No.97TB100171), Salerno, Italy, pp. 21-29; copy is the author's 9-page preliminary version numbered 1-9, decoded text sha256 3ba1e117…; doi.org answers 202 with a zero-byte body`
- `used-by`: `corpus/knowledge/duplicate-verdict-identity.md, corpus/knowledge/duplicate-verdict-byte-equality.md` (drop `duplicate-verdict-taxonomy-r24.md`, finding 3)

## Findings

1. **[blocking if S118 lands verbatim] Wrong venue in the anchor.** Staged row `| S118 |` (`/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md:16`) says "IEEE Symposium on Foundations of Computer Science / SEQUENCES 1997"; FOCS is not this venue. Crossref: `Proceedings. Compression and Complexity of SEQUENCES 1997 (Cat. No.97TB100171)`, Salerno, Italy, SEQUEN-97.
2. **[blocking] The source cell names only the DOI, which serves no bytes.** `source` = "On the resemblance and containment of documents — https://doi.org/10.1109/SEQUEN.1997.666900"; probe returns `202 0` (evidence 6). The URL whose bytes hold the quote (the Princeton PDF) is absent from the row, so a reader cannot re-open it; contract rule 1 wants the URL in the Gate and `source` wants the canonical locator. Also `anchor` calling the DOI "resolves to ieeexplore.ieee.org/document/666900" reads as readable when the target is a WAF challenge.
3. **[high] `used-by` names a path absent at HEAD.** Staged cell includes `corpus/knowledge/duplicate-verdict-taxonomy-r24.md`; `git -C …/souji-shokunin cat-file -e HEAD:corpus/knowledge/duplicate-verdict-taxonomy-r24.md` → `fatal: … does not exist`, rc 128. C1's K1 counts used-by paths that do not exist, so landing this cell verbatim adds a mismatch. The other entry, `duplicate-verdict-identity.md`, lands this round (present as `deliver-*` files, not yet in the tree).
4. **[high] `recheck` is not executable as written.** Staged `365d — re-resolve the DOI and re-read § 2`: § 2 is not on the DOI landing page and the landing page serves nothing (202/0). Rewrite to re-fetch the PDF, compare `da122799…`/`3ba1e117…`, re-read § Abstract and § 2, and probe the DOI expecting `202 0`.
5. **[medium] `teaches` states inferences as the paper's finding.** Staged: "each a number between 0 and 1, so \"duplicate\" is a thresholded family of verdicts, not one predicate". The bytes define resemblance/containment and say they are numbers between 0 and 1 (`:115`); the words "duplicate", "threshold" and any verdict taxonomy never appear as the paper's claim, and "taxonomy" in the scope cell is the row's framing. Keep the inference, label it as the lane's.
6. **[medium] Tier B is unexplained against the contract.** SOURCES-CONTRACT-v1 tiers: A includes "original paper"; B is "strong secondary". The paper is primary for this scope, so B is a deliberate under-grade and needs its reason recorded — borrowed-vocabulary scope plus a preliminary-version copy, not the version of record. The landed S217's field note gives that reason (`deliver-sources-rows.md:56`); the staged row gives none, and the row has no reason column, so the reason belongs in the lesson Gate.
7. **[low] Anchor lacks page and a date.** Staged anchor cites the section but no page and no publication date (Crossref has none), and duplicates the DOI already in `source`. The landed S217 fixes the container and the 202 note but still omits the copy's pagination (abstract p. 1, § 2 p. 2) and the PDF/text pins; "proceedings year 1997" is an inference from the container title, not an issued date — say so.
8. **[low] "author-hosted" is inaccurate where it lands.** `deliver-sources-rows.md:45` (`anchor`, `recheck`), `deliver-lesson-gate.md:187` and `deliver-duplicate-verdict-*` all call the copy "author-hosted". The host is a Princeton course archive (`/courses/archive/spring13/cos598C/`); nothing in the bytes shows author hosting (the PDF names DEC Systems Research Center and dates from 1998-04-02). Use "course-archive copy of the author's preliminary version".
9. **[low] Three line locators off by one in `deliver-entry-identity.md` against the snapshot it names.** `:98` cites "lines 54-55" for "We calculated our clusters based on a 50% resemblance." (snapshot `:53-54`); `:99` cites "line 58" for "a mixture of exact duplicates and similar" (snapshot `:57`); `:100` cites "line 68" for "Definitions as set intersection problems" (snapshot `:67`). The quotes themselves verify; only the locators drift (systematic +1).
10. **[confirm] Provenance and pins hold.** Title, single author A.Z. Broder, abstract text and 9-page length agree with the Crossref record for the DOI; the delivered PDF (`da122799…`) and decoded text (`3ba1e117…`) reproduce from the live URL and match `w1/sources/SHA256SUMS`. The `teaches` figures in S217 are in bytes: "over 30,000,000 documents" `:51`, "a 50% resemblance" `:54`.

## Open verification gap (not a defect)

`census/round-29/sources/` does not exist at HEAD; the entries cite snapshot paths there, and only `.ufo/waves/round-29/w1/sources/` holds the bytes. The L1 must land the four files (or fix the paths) before the entries' `verified-at` lines are true at the tip. The delivered S217's `teaches` reports the paper's own 50% operating point inside a scope that says "not a threshold"; the scope disclaims it, but a reader could still cite it as a threshold — one clause ("the paper's own operating point") removes the ambiguity.

## Deliveries

- `.ufo/waves/round-29/w1/SwarmReviewer42.md` (this report). No delivery file was named for this seat; no other writes.
