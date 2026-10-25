STATUS: PASS

# Slice118 — hand-check of one absent-defect register row (lane `souji`, row S118)

Scope: one row. Register read-only at
`/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md`.
Lane read-only except this report and the named evidence file. No git/jj write, no
mutating cleanup, no deletion authority, no `pacman`.

## Required verdict

**`unverifiable`** — frozen class, from the four: `present` | `accepted` | `unverifiable` | `refused`.

Reason: one bounded fetch of the cited DOI resolved through to IEEE Xplore and the origin
served **0 bytes** (HTTP 202). No source text was returned, so no span exists to locate and no
quote can be checked. An unreachable/empty payload is never fabrication.

- Fetched-or-read source: `https://doi.org/10.1109/SEQUEN.1997.666900`
  → effective `https://ieeexplore.ieee.org/document/666900/`
- Access date: **2026-10-25**
- Exact located span: **none** (<=25 words trivially satisfied by zero). Not merely "not found
  in a large text" — the response body was 0 bytes, and independently the register row carries
  **no quote at all** (quote column empty; see finding H1). There is nothing to match.
- Locator: **none available** (no document, no section/heading/line).
- Snapshot: `.../w1/evidence/slice118-doi.txt`
  sha256 `b6b361cca397b4cb6c3fbfd94318be444307acbde70456deb64bd214d62dadee`
  (736 bytes = fetch body **0 bytes** + an appended `RECEIPT` block; the sha256 of the
  pre-append zero-byte body is the empty-string digest
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.)

Citation-class defect check: **not applicable / not asserted.** The row cites a remote DOI, not
a local artifact. I therefore do **not** claim the "text actually lives in a man page or web
page" defect for S118, and I do not upgrade it to `refused` or `accepted`.

## Evidence (executed)

1. Frozen extract, field 4 = id cell (`awk -F'|'`, line 361):

```
$ awk -F'|' 'NR==361{...}' "$R"
NF=7
$1=[]
$2=[ `souji` ]
$3=[ round1 ]
$4=[ S118` ]
$5=[ the cited source could not be fetched, so no quote was checked ]
$6=[ https://doi.org/10.1109/SEQUEN.1997.666900 ]
$7=[]
```
   Header row is `NF=9` (`$2=lane $3=round $4=id $5=class $6=cited source $7=quote(s) $8=note`).
   My row is **5 cells, not 7**.

2. Bounded fetch (single attempt, as contracted):

```
$ curl -fsSL -m 20 -o slice118-doi.txt \
    -w 'HTTP=%{http_code} SIZE=%{size_download} URL=%{url_effective}\n' \
    'https://doi.org/10.1109/SEQUEN.1997.666900'
HTTP=202 SIZE=0 URL=https://ieeexplore.ieee.org/document/666900/
EXIT=0
```
   Exact status/error record: exit 0, HTTP **202 Accepted**, `size_download` **0**, no curl
   error (202 is 2xx, so `-f` did not fire). The DOI resolver redirect is confirmed by
   `url_effective`; the IEEE origin returned an empty challenge body. Zero payload ⇒
   unverifiable. No second fetch, no HEAD, per the one-attempt bound.

3. No lane-local artifact can supply the text (source-inferred absence made executable):

```
$ grep -rIl -e 'SEQUEN' -e '666900' . --exclude-dir=.git
./.ufo/waves/round-22/attempt2/w1/evidence/slice118-doi.txt   <- my own receipt
./.ufo/waves/round-22/attempt2/w1-spec.json                   <- this wave's task text
./.ufo/waves/round-22/attempt2/w1-dispatch.json               <- this wave's task text
$ grep -ral -e 'SEQUEN' -e '666900' census corpus tools | wc -l
0
$ grep -oE '\| S[0-9]{3}' corpus/SOURCES.md | tr -d ' |S' | sort -n | tail -1
114          # registry ids present 109..114; S118 is NOT in corpus/SOURCES.md
```
   So there is neither a local artifact nor a lane registry row (and hence no quote string)
   for corpus id S118.

4. Corroboration from committed lane bytes, found **after** the fetch was recorded (not used to
   derive the verdict): `LOG.md:1510` "1 unverifiable (S118 DOI 202 empty body)";
   `census/round-22/attempt2/slice-verdicts.tsv` line 2
   `S118<TAB>unverifiable<TAB>DOI resolves 202 with an empty body 2026-10-25; no text to check;
   unreachable is not fabrication`. Independent fetch agrees.

5. Why the 0 bytes are not an outage artefact (peer-captured headers for the same row, read
   only after my own fetch; `evidence/rev-doi-S118.headers`, `date: Sun, 25 Oct 2026 06:46:18
   GMT`): `HTTP/2 302` (doi.org) → `HTTP/1.1 301` (CloudFront) → **`HTTP/2 202`** with
   **`content-length: 0`** and **`x-amzn-waf-action: challenge`**, `cache-control: no-store`.
   The origin is up and answers; it refuses to serve the article body to a non-JS client.
   That is precisely "the source could not be fetched" for quote purposes — unreachable text,
   not absent payload and not a citation-class defect.

## Findings

**H1 (register-level, affects extractors) — malformed id cell is systemic, and it is not the
only malformation.** The id cell is `` S118` ``: **one trailing backtick, no opening backtick**,
so it is not the `` `S118` `` form every well-formed row uses. Worse, the row has **5 cells
against a 7-column header**: the `class` position holds the prose note, the `cited source`
position (coincidentally) holds the URL, and the `quote(s)` and `note` cells are **absent**.
Census over the register:

```
$ awk -F'|' '$4 ~ /S[0-9]/ && $4 ~ /`/ && $4 !~ /` *S[0-9]+ *`/ {n++; if ($7 ~ /[^ ]/) q++} END{...}' "$R"
malformed_rows=109 with_nonempty_quote_col=0
```
   All **109** rows share this shape; **0** of the 109 carry a quote.

**Would the stray backtick defeat a column-zero-only extractor?** Yes, in two distinct ways,
and partly. (a) Row anchoring survives: the line begins with `|` at column 0, so a
`^\|`-anchored, per-line extractor still reaches the row. (b) An exact backtick-wrapped id
matcher `` ^\s*`S[0-9]{3}`\s*$ `` **fails** — the id is unmatched and the row silently drops.
(c) Any extractor assuming the header's field positions mis-reads the row: class → prose, note →
absent; only the source (cell 5) lands correctly by luck. A permissive `S[0-9]{3}` regex does
recover `S118`. **Observed, not hypothesised:** the frozen extractor already propagated the
shift into the committed derived slice —
`census/round-22/attempt2/quarantine-slice:8` = `` S118`   the cited source could not be
fetched, so no quote was checked`` — i.e. the slice row's class slot contains prose, not one of
the four frozen classes. The extractor does not normalise these 109 rows.

**M1 (register-level accounting) — the `Totals` table omits this class entirely.** Totals
declares `rows with at least one ABSENT quote: 194` and `| payload-absent | 194 |`, yet the
`Rows` section carries 109 rows whose class cell is either "the cited source could not be
fetched…" or "the gate block named no locator…" — classes the register's own legend defines as
`unreachable` ("re-fetch, or mark the row unverifiable — do NOT call it a fabrication"). Those
109 rows are in neither totals bucket, so the register under-reports its own row count and maps
an `unreachable` population under a `payload-absent`-only table.

**L1 (scope note) — the register is read-only to me.** H1/M1 are reported, not repaired; no
register byte was modified. If a repair is wanted it belongs to the register's owner
(`shokuknow`), which is read-only for this lane.

## Residual risk and verification gaps

- **One bounded fetch by contract.** No retry, no `HEAD`, no header dump, no authenticated or
  alternate mirror (e.g. IEEE PDF, author copy, Crossref metadata). I therefore make **no claim**
  about whether S118's original quote was real: it is unverifiable, not cleared and not accused.
- `HTTP 202` with `SIZE=0` is a served-but-empty response, not a DNS/TLS failure. I classify it
  as an unreachable payload because **no text was delivered**; the distinction is recorded here
  rather than smoothed over.
- Local-artifact absence was scanned text-and-binary over the whole lane (`grep -rIl` all files
  excluding `.git`, `grep -ral` over `census/ corpus/ tools/`). Untracked build outputs outside
  the lane, and anything under operator-owned or private paths, were **not** read by design
  (no `/proc`, no credentials, no private TSVs, no `.tower`, no operator-sweep census).
- The id-cell shape means a future consumer must not rely on fixed field indices for these 109
  rows; that is a consumer-side constraint I can state but cannot enforce from here.
- Tooling: **no installs and no updates** performed, so no version/channel record is owed.
