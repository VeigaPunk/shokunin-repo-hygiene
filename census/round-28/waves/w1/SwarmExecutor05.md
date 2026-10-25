# SwarmExecutor05 — r28 POSIX.1-2024 snapshot + quote capture

## Status
STATUS: PASS — the three POSIX.1-2024 (Issue 8) pages were opened 2026-10-25 and stored byte-exact under `census/round-28/sources/` with `sha256sum -c` rc 0; four located quotes (open() O_EXCL atomicity; rename() failure clause + atomicity; fsync() durability + null-implementation) are byte-exact substrings of those snapshots and recorded with word counts in `census/round-28/records/posix-quotes.tsv`.

## Evidence

Fetch (curl 8.23.0, pre-installed; no tool installed or upgraded this run):

```
for p in open rename fsync; do
  curl --fail --silent --show-error --location --max-time 120 --proto '=https' --tlsv1.2 \
       -D "$p.headers" -o "$p.html" \
       "https://pubs.opengroup.org/onlinepubs/9799919799/functions/$p.html"
done
```
No `--compressed`, so no `Accept-Encoding` was sent; all three responses are `HTTP/1.1 200 OK`, `Content-Type: text/html; charset=UTF-8`, and each `Content-Length` equals the saved byte count (40401 / 26407 / 10474) — the stored bytes are the transferred representation, not a re-encoded form. `Date:` headers: `Sun, 25 Oct 2026 18:46:39 GMT` (open, rename), `18:46:41 GMT` (fsync). All three pages self-identify as `The Open Group Base Specifications Issue 8` / `IEEE Std 1003.1-2024`.

Digests (`sha256sum -c SHA256SUMS`, run in `census/round-28/sources/`, rc 0):

```
57b770918aa3e0c25186972675df8c96da119cf4b973335ed4487405e260dc3a  open.html     40401 B
06671610134b0a52cdf4dcdaf382f72fef85ef51088b8a52b8679c7f03829318  rename.html   26407 B
5c2975abbb2d65fcad92a4da5241f4f4001f0e5d8cf57f752d9486073ca49747  fsync.html    10474 B
```

Quote verification (read the TSV, re-found each quote in the stored bytes):

```
open.html    occ=1 words=18/18 pipe=False raw_substring=True
rename.html  occ=1 words=19/19 pipe=False raw_substring=True
rename.html  occ=1 words=11/11 pipe=False raw_substring=True
fsync.html   occ=1 words=21/21 pipe=False raw_substring=True
fsync.html   occ=1 words=10/10 pipe=False raw_substring=True
ALL_OK True
```

Lane revision at read time: `0c96332932e66bbaf9cf1c246091d3275a0ab612` (my files are untracked additions; no `git add`/commit, no lane mutation). Scratch `/var/tmp/souji-r28-SwarmExecutor05/` removed after the copy was `cmp`-verified against it.

## Findings

1. **Snapshots delivered.** `census/round-28/sources/{open,rename,fsync}.html` + `SHA256SUMS` (sha256sum format, fetch order open→rename→fsync). The directory also holds `git-fetch-zh-HANS-CN.html` written by another seat (S119 disposal, not mine); `SHA256SUMS` covers only the three POSIX pages, so a `sha256sum -c` is clean but the directory is not a complete inventory.

2. **Quote form is constrained by the frozen gate checker, not by taste.** `tools/souji-gate-check.py:119-122` (`squash()` = `re.sub(r"\s+"," ",…)`) collapses whitespace on both snapshot and quote but does **not** strip HTML tags, and `check_entry` step 4 requires `squash(quote) in squash(snapshot)`. Every snapshot quote must therefore either avoid markup entirely or carry the literal markup (e.g. `<i>fsync</i>`) exactly as served. The TSV rows were chosen to be raw-byte-contiguous single-line spans, so they satisfy both a strict byte search and the checker's squashed search.

3. **BLOCKER for C2's gate — two staged ADMIT quotes are absent from the snapshots.** Verified with the checker's own `squash()` semantics:
   - `.ufo/waves/round-28/w1/origin-record-exclusivity-r28.md:53` quotes `"If the rename() function fails for any reason other than [EIO], any file named by new shall be unaffected."` — `squash_present=False` (snapshot line 82 italicises both names). Byte-exact replacement: `If the <i>rename</i>() function fails for any reason other than [EIO], any file named by <i>new</i> shall be unaffected.` (19 words).
   - `.ufo/waves/round-28/w1/origin-record-durability-r28.md:50` quotes `"after a system crash or other failure that all data up to the time of the fsync() call is recorded on the disk"` — `squash_present=False` (snapshot line 90 italicises `fsync`). Byte-exact replacement: `system crash or other failure that all data up to the time of the <i>fsync</i>() call is recorded on the disk.` (21 words).
   Both rows are in `census/round-28/records/posix-quotes.tsv`; with them as written, `souji-gate-check.py` would report `fail=1` (or more) for each affected entry.

4. **The third staged quote passes but is not byte-contiguous.** `.ufo/waves/round-28/w1/origin-record-exclusivity-r28.md:52` quotes `"The check for the existence of the file and the creation of the file if it does not exist shall be atomic"` — `squash_present=True`, `raw_present=False` (the served bytes wrap after `the` at snapshot line 101, so `creation` starts line 102). It is admissible to the checker; the TSV records instead the byte-contiguous core `creation of the file if it does not exist shall be atomic with respect to other threads executing` (18 words, line 102). Either form grounds S212; the TSV's form additionally survives a strict byte audit.

5. **Independent fetch agreement.** `.ufo/waves/round-28/w1/snapshots/{open,rename,fsync}.html` (written by another seat) are byte-identical to my copies — same three digests. Two separate fetches of the same URLs on the same date agree, so the `verified-at` digests in both staged entries are correct.

6. **Quote selection, per the item.** `open()` — DESCRIPTION, `O_EXCL` option definition (line 102): the atomicity predicate. `rename()` — DESCRIPTION failure clause (line 82, used by the exclusivity entry) and RATIONALE atomicity statement (line 247). `fsync()` — RATIONALE durability clause (line 90, the "recorded on the disk" wording) and RATIONALE null-implementation allowance (line 94, a complete sentence, no markup). All ≤25 words by the checker's `squash().split()` metric; none contains `|` or a tab.

## Attack log
None. No counter, predicate or case set is disputed. The only gameability-adjacent observation is Finding 2/3: `souji-gate-check.py` accepts whitespace-collapsed quotes but not tag-stripped ones, so an HTML-sourced entry can fail on markup alone — that is a citation-fidelity hazard for authors, not a weakened counter, and no exemption or predicate change is proposed.
