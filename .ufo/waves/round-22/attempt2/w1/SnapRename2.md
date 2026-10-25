STATUS: PASS

# SnapRename2 — restorable-quarantine re-grounding snapshot (rename(2))

Preregistration read first: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/attempt2/preregistration.txt` (frozen 2026-10-25, base `4edb25d`). This seat contributes the rename(2) capture that C2's per-entry predicate check 2/3/4 consumes; it renders no C2 verdict of its own and did not run `tools/souji-gate-check.py`.

## 1. Fetch (executed)

Exact command run (cwd irrelevant, absolute `-o`):

```
curl -fsSL -m 45 -A 'souji-r22-restructure/1.0' \
  -o /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/attempt2/w1/evidence/snap-rename2.raw \
  -w '%{http_code} %{size_download}' https://man7.org/linux/man-pages/man2/rename.2.html
```

Observed output: `200 23571` (exit 0). Page reachable; not JS-only; no redirect.

Redirect/final-URL receipt, separate read-only request:

```
curl -fsSL -m 45 -A 'souji-r22-restructure/1.0' -o /dev/null \
  -w 'code=%{http_code} redirects=%{num_redirects} effective=%{url_effective}\n' \
  https://man7.org/linux/man-pages/man2/rename.2.html
```

Observed: `code=200 redirects=0 effective=https://man7.org/linux/man-pages/man2/rename.2.html`

- fetch date: **2026-10-25**
- http code: **200**
- bytes downloaded: **23571**
- final URL after redirects: **https://man7.org/linux/man-pages/man2/rename.2.html** (0 redirects)
- page identity (from its own footer, in the snapshot): `Linux man-pages 6.19  2026-02-08  rename(2)`
- curl 8.23.0 (libcurl/8.23.0), CPython 3.14.8.

## 2. Text snapshot (executed)

`snap-rename2.txt` is UTF-8, 15799 bytes, 400 lines, LF, plus a 11-line `#`-prefixed metadata header (source URL, final URL, fetch date, http code, raw bytes, raw sha256, fetch/strip commands). Body words are in document order.

Strip command — stated exactly: I did **not** invoke `python3 -c`; I ran the same interpreter (CPython 3.14.8) with an inline `html.parser.HTMLParser` program through the eval tool. Semantics reproduced verbatim below:

```python
# convert_charrefs=True (entities decoded); handle_data appends text in document order;
# newline emitted on block tags (pre,p,div,h1,h2,li,tr,br); script/style never entered;
# lines right-stripped, lines that are only the page's "top" link text dropped,
# runs of blank lines collapsed to one.
```

No sed, no regex tag soup: tag removal is the parser's tokenisation, so text cannot be reordered or duplicated.

## 3. Digests and sizes (executed)

```
8772946a809a0db54f4854f200908f10bee758ea452e8df5efd955bc3b8e6e57  snap-rename2.raw   (23571 bytes, 509 lines)
88cba52e7f5ee81985c34a33a3d4112ce0fecd377da5d0665ca7adb76c9631c4  snap-rename2.txt   (15799 bytes, 400 lines)
```

Produced by `sha256sum snap-rename2.raw snap-rename2.txt` after the writes; `file snap-rename2.txt` → `Unicode text, UTF-8 text`.

## 4. Passage (verbatim, locator, 13 words)

> "Don't overwrite newpath of the rename.  Return an error if newpath already exists."

Locator: **§ DESCRIPTION → renameat2() flags list → `RENAME_NOREPLACE` paragraph** (Linux man-pages 6.19, page dated 2026-02-08; raw HTML lines 162–164; `snap-rename2.txt` lines 122–124). Straight apostrophe as served (`Don't`, U+0027).

Whitespace-collapsed self-check (executed): the quote occurs verbatim in `snap-rename2.txt` → `True`; word count 13 ≤ 25.

Context immediately following, same flag: "RENAME_NOREPLACE can't be employed together with RENAME_EXCHANGE." and "RENAME_NOREPLACE requires support from the underlying filesystem." — not part of the quotation above.

## 5. Cross-checks (executed, read-only)

- `cmp` against `.ufo/waves/round-22/attempt2/w1/evidence/slice124-rename2.html` (an independent seat's capture of the same URL): **byte-identical**, sha256 `8772946a…e6e57`. Two independent fetches at ~03:45 returned the same bytes, so the source is stable and the capture is not seat-local.
- `cmp` against the committed gate snapshot `census/round-22/attempt2/sources/man7-rename.2.raw`: **byte-identical**, same sha256. The file the C2 entries' Gates name is corroborated by this independent fetch, not merely copied.
- The r23 entry's ADMIT line quotes `RENAME_NOREPLACE Don't overwrite newpath of the rename. Return an error if newpath already exists.` (14 words). Collapsed-match against `census/round-22/attempt2/sources/man7-rename.2.txt` → `True`; against my `snap-rename2.txt` → `True`. Both snapshots carry the span.

## 6. Files written (only these)

- `.ufo/waves/round-22/attempt2/w1/evidence/snap-rename2.raw` (new, 23571 B)
- `.ufo/waves/round-22/attempt2/w1/evidence/snap-rename2.txt` (new, 15799 B)
- `.ufo/waves/round-22/attempt2/w1/SnapRename2.md` (this report)

No other path was written. No git/jj writes, no deletions, no process signals, no credential/proc/.tower/private-TSV reads, no package installs (nothing needed; tool records: none installed in this seat).

## 7. Bounded findings / risk

- **Snapshot-dir mismatch is not a defect for this seat.** The frozen counter reads `--snapshot-dir census/round-22/attempt2/sources`; my capture lives in `w1/evidence/` per my assignment. The Gate-named file `census/round-22/attempt2/sources/man7-rename.2.txt` (sha256 `74c30ae25e76818ab25d9da03a12247f94eceb92be2e1d6c46c70d868b67bbaf`) already contains the quoted span and its raw is byte-identical to mine, so predicate check 4 is satisfiable without moving my file. If the entry owner prefers one canonical text strip, the census txt (12570 B) and mine (15799 B) differ in formatting only — both pass the collapsed-verbatim test; do not "fix" either silently.
- **Quote-length headroom is 11 words** (13 used, 14 as the entry quotes it, cap 25). A future edit that extends this quotation has little room before tripping frozen fixture (2) `quote of 26 words -> fail`.
- **Not verified here:** the gate-check run itself, the slice verdict rows, SOURCES.md id resolution, and the r23/r24 Gate ADMIT/REJECT completeness — other seats own them; I did not run them and report no verdict.
- Source-inferred, not executed: nothing material; every claim above is from a command in this transcript except the page's own publication date/version, which is quoted from its bytes.
