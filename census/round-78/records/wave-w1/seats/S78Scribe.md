S78Scribe — round-78 corpus drafts (verdict)

VERDICT: drafts delivered. The L1 landed its own S323/S324, Q140 and knowledge entry in bbd199da
(round-78: I — integration part 1) while this seat drafted, so my files compare against landed bytes; the
landed registry validates clean and two defects below are in it.

Reproduced from committed bytes (digests recomputed, receipts read, counters not rerun)
- `srcs/git-config.adoc-v2.56.0` sha256 a6e644cb…b2c9, 21095 B; refetch HTTP 200, 21095 B, same sha256;
  `Includes` at line 85, quote at lines 99-100 (22 words, no `|`).
- `srcs/git-setup.c-v2.56.0` sha256 8316b1ad…c589, 83214 B; refetch HTTP 200, 83214 B, same sha256;
  `get_common_dir_noenv()` line 321, the quoted file_exists/strbuf_read_file lines 328-329.
- Gate blob b746bd9d… at ed22dc9c and 319109b0; 5d08f547… at base a8558d41 and P a0dcfa8d (prereg K-a).
- `records/c1-after.txt`: `SUMMARY rows=17 mismatches=0 errors=0 hangs=0` EXIT=0 (rev 87d45617, gate
  b746bd9d). `controls/c1-K-a-do-nothing.txt`: mismatches=12 hangs=12 EXIT=1; K-b 14, K-c 10, K-d 11 all
  EXIT=1. Regressions r77 16/16, r76 30/30, r36 21/21 (cases=21 pass=21), r27 4/4.
Commands deciding the verdict
  bash scripts/sources-census.sh validate --file corpus/SOURCES.md --today 2026-11-07   -> EXIT=0, 0 E-codes
  same validate over 319109b0's registry + my two rows (scratch mirror)                -> EXIT=0, 0 E-codes
  curl -sS -o refetch-<n> -w '%{http_code} %{size_download}' <raw URL>; sha256sum      -> 200, byte-equal
Findings
- HIGH: none.
- MEDIUM: landed S323/S324 `used-by` names only `corpus/knowledge/git-discovery-sources.md`; Q140 in the same
  commit cites S323/S324 (`corpus/SOURCES.md:282-283` vs `corpus/QUALITY.md:356`), so the row under-declares
  a used-by surface. My draft adds `corpus/QUALITY.md`; the census accepts it (E11 clean).
- MEDIUM: `corpus/knowledge/git-discovery-sources.md` is the only one of 52 entries without `verified-at:`
  and `recheck:` header lines (`grep -L '^verified-at:' corpus/knowledge/*.md` -> 1 file), and it records no
  re-run command for its 17-row claim.
- LOW: landed S324 anchor quotes lines 327-329, putting nested `"%s/commondir"` quotes inside a table cell;
  lines 328-329 alone carry the claim (my draft quotes those and names line 327 in the teaches cell).
- LOW: S324 shares the `setup.c` URL with S300 -> `W04 S324 duplicate url … across scopes`; a warning, the
  lane still reads `file ok`, EXIT=0. The seat brief's "lines 99-101" for S323 is off by one: the quote ends
  on line 100 (line 101 begins "variable is a relative path"); landed row and draft both say 99-100.
- LOW: the landed knowledge doc grounds `packed-refs` only on row g3; no SOURCES row quotes a packed-refs
  read. My draft labels it unquoted.

Files written (under .ufo/waves/round-78/w1/S78Scribe/): `sources-rows.md`, `knowledge-git-discovery-sources.md`
(60 lines), `quality-q140.md`, `census-validate.txt`; report `.ufo/waves/round-78/w1/S78Scribe.md`. Not done:
no lane edits, no commits, no counter reruns (receipts read, digests recomputed); Q141 is C2, untouched here;
no tools installed.
