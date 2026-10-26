# SwarmExecutor15 — round-29 w1 — C3 source pinning

## Status

STATUS: PASS — four C3 snapshots pinned byte-exact (all HTTP 200, sha256 recorded, `sha256sum -c` clean); all nine requested claims carry a verbatim quote of ≤25 words that passes the gate's own `QUOTE_RE` + `squash()` matching against the delivered snapshot bytes (9/9 rows OK, FAILS=0), and each was cross-checked against the rendered text for the three man pages.

## Evidence

Lane revision during work: `b8cb4b31ce80e2e3314b88e85d40ea9873180804` (prereg commit). Runtime: curl 8.23.0, pdftotext 26.08.0 (poppler), Python 3.14.8 run as `python3 -B`. No tool installs or upgrades were needed, so there is no install record.

### Fetches (exact command per URL: `curl -sSL -m 60 -A 'Mozilla/5.0' -o <file> -w '%{http_code} %{url_effective} %{size_download} %{content_type}' <url>`)

| file | UTC window | HTTP | final URL | bytes | content-type |
|---|---|---|---|---|---|
| statx.2.html | 2026-10-26T00:36:19Z → :20Z | 200 | `https://man7.org/linux/man-pages/man2/statx.2.html` | 33125 | text/html |
| link.2.html | 2026-10-26T00:36:20Z → :21Z | 200 | `https://man7.org/linux/man-pages/man2/link.2.html` | 19883 | text/html |
| cmp.1.html | 2026-10-26T00:36:21Z → :21Z | 200 | `https://man7.org/linux/man-pages/man1/cmp.1.html` | 9791 | text/html |
| broder97resemblance.pdf | 2026-10-26T00:36:21Z → :29Z | 200 | `https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf` | 254930 | application/pdf |

Final URL equals request URL in all four cases (no redirect). Validators from a separate `curl -sSI` at 2026-10-26T00:38:24Z–:26Z, all `HTTP/1.1 200 OK`: the three man7 pages share `Last-Modified: Thu, 08 Oct 2026 17:39:35 GMT` with ETags `"8165-65d57b70ec3c0"` / `"4dab-65d57b70ec3c0"` / `"263f-65d57b70ec3c0"`; the PDF has `Last-Modified: Mon, 04 Feb 2013 15:48:39 GMT`, `ETag: "3e3d2-4d4e806e35702"`.

PDF text derived with `pdftotext -q broder97resemblance.pdf broder97resemblance.txt` (21669 bytes, 457 lines).

### Snapshots (`sha256sum` over relative names, as delivered)

```
da1227992d4a308f9f6f9f99893fd7b00c26e6cf757b1372f426074c101ef56b  broder97resemblance.pdf
3ba1e117c6267c72e6c20e37d5b0b98e76bdb4fcf6429f49204cb3196d28325d  broder97resemblance.txt
5c68e8d874e987391e7679dd2637f953b90087076bffe6de18c40db86cd046a3  cmp.1.html
9cb197a7abe32a459bb3dbe96f67d906ff199e0f9d5f19f41a3a05e46cea1ec9  link.2.html
2a47fe319c5894d7d907b5ac03ced8cf64fb786bab69c12d276e90ba18359e8e  statx.2.html
```

`sha256sum -c SHA256SUMS` → `broder97resemblance.pdf: OK`, `broder97resemblance.txt: OK`, `cmp.1.html: OK`, `link.2.html: OK`, `statx.2.html: OK`. All six text files decode as strict UTF-8, LF-only.

### Page version lines

- `statx.2.html:587` — `<span class="footline">Linux man-pages 6.19            2026-02-08                       <i>statx</i>(2)</span>`.
- `link.2.html:310` — `<span class="footline">Linux man-pages 6.19            2026-02-11                        <i>link</i>(2)</span>`.
- COLOPHON corroboration for both: `statx.2.html:577` and `link.2.html:300` read `This page was obtained from the tarball man-pages-6.19.tar.gz`, fetched 2026-09-09.
- `cmp.1.html:156` — `<span class="footline">diffutils 3.12.26-bbc1         August 2026                         <i>CMP</i>(1)</span>`; COLOPHON `cmp.1.html:146-149` says the page came from the diffutils upstream Git repository on 2026-08-03, most recent commit found 2026-06-20.

### Quote verification

Method mirrors `tools/souji-gate-check.py`: `squash(t) = re.sub(r"\s+", " ", t).strip()` applied to both the raw snapshot bytes (utf-8, errors=replace) and the quote; a quote passes only if `squash(quote) in squash(bytes)` and it has ≤25 words. The rendered-text column comes from a stdlib `html.parser` extraction with character references resolved (not a browser), used only as a cross-check.

| # | claim | snapshot:line | words | raw bytes | rendered | markup inside span |
|---|---|---|---|---|---|---|
| 1 | statx `stx_ino` inode number | `statx.2.html:335` | 6 | hit | hit | none (label `<i>stx_ino</i>` precedes) |
| 2 | statx `stx_nlink` number of hard links | `statx.2.html:323` | 8 | hit | hit | none (label `<i>stx_nlink</i>` precedes) |
| 3 | statx `stx_btime` creation | `statx.2.html:356` | 4 | hit | hit | none (label `<i>stx_btime</i>` precedes) |
| 4 | statx `stx_mnt_id` / `STATX_MNT_ID_UNIQUE` | `statx.2.html:379-380` | 15 | hit | hit | none |
| 5 | link(2) creates a hard link | `link.2.html:95-96` | 14 | hit | hit | none (markup `<b>link</b>()` precedes) |
| 6 | link(2) `"original"` | `link.2.html:102-103` | 7 | hit | hit | none (straight quotes follow the span) |
| 7 | cmp(1) three-valued exit | `cmp.1.html:113-114` | 15 | hit | hit | none |
| 8 | Broder resemblance/containment | `broder97resemblance.txt:8` | 8 | hit | n/a (text extraction) | none |
| 9 | Broder `roughly the same` | `broder97resemblance.txt:9` | 9 | hit | n/a (text extraction) | none |

Gate simulation over `deliver-quotes.tsv` — each row rendered as `- ADMIT: "<quote>" — <locator> — reason: … — snapshot: <path>` and parsed with the gate's own `QUOTE_RE`, `SNAPSHOT_RE` and `LOCATOR_RE`:

```
$ python3 -B /var/tmp/souji-r29-SwarmExecutor15/validate_tsv.py
OK   words= 6 present=True single_quote=True locator=True snapshot_field=True forbidden=- | statx.2.html
… (9 rows, all OK)
ROWS=9 FAILS=0
```

(The validator was scratch under `/var/tmp/souji-r29-SwarmExecutor15/`, removed after use per the seat contract; its method is stated above and is the gate's own regex set.)

## Findings

1. **The gate matches raw snapshot bytes, not rendered words.** `tools/souji-gate-check.py` squashes the snapshot file's bytes, so any inline markup between words breaks a quote. Two decisive negative probes on the delivered bytes: `link() creates a new link` → MISS (raw is `<b>link</b>() creates a new link`), but `<b>link</b>() creates a new link` → hit; `STATX_MNT_ID_UNIQUE Want unique stx_mnt_id` → MISS (raw is `<b>STATX_MNT_ID_UNIQUE </b>Want unique stx_mnt_id (since Linux 6.8)`), not even with the source's trailing padding collapsed. Consequence: quote the prose definitions, never the bolded option table. All nine delivered quotes are markup-free spans — location `link.2.html:95`, `statx.2.html:257`, `tools/souji-gate-check.py:squash`.
2. **`link.2.html:102-103` contains straight ASCII double quotes around `original`, which collide with the gate's quote delimiter** (`QUOTE_RE = "([^"]{2,400})"`). The full sentence `… and it is impossible to tell which name was the "original".` cannot be pasted verbatim inside a Gate quote: the regex splits it into two matches (`impossible to tell which name was the` and `original`). I therefore deliver the 7-word slice `impossible to tell which name was the`, which is a verbatim substring and parses as exactly one quoted span. If the L1 wants the full sentence, it must accept the split — both fragments do occur in the snapshot, but the split is fragile against any rewording. Location `corpus/knowledge` Gate authoring + `tools/souji-gate-check.py:QUOTE_RE`.
3. **The Broder PDF's text uses curly quotes and puts the period inside the closing quote.** `broder97resemblance.txt:9` is byte `… notions of \xe2\x80\x9croughly the same\xe2\x80\x9d and \xe2\x80\x9croughly contained.\xe2\x80\x9d`. A first draft ending at `contained”` (period outside) MISSed; the delivered slice includes the period. Curly quotes are safe inside the gate's straight-quote delimiters, but they must be copied, not retyped as ASCII. The `.txt` is a derived artifact of pdftotext 26.08.0 and its sha256 is version-dependent; the PDF sha256 is the durable pin.
4. **`cmp.1.html:113-114` renders the exit-status sentence across a source line break** (break after `Exit status is`, continuation `0 if inputs are the same, 1 if different, 2 if trouble.`), inside `<pre>`, with no markup on any word and a trailing full stop outside the delivered slice. Squashing makes it a single-span match; a quote copied from a terminal with a hard line break also survives for the same reason.
5. **Alternate quote for claim 4, verified but not in the TSV** (kept claim→row 1:1): `If using STATX_MNT_ID, this is the mount ID of the mount containing the file.` at `statx.2.html:374-375` — 14 words, raw-bytes hit, rendered hit. The delivered row instead uses the `STATX_MNT_ID_UNIQUE` sentence because the duplicate-verdict claim rests on identity that is not reused across mounts.
6. **Version drift risk:** the three man7 pages were all last modified 2026-10-08 and the PDF 2013-02-04. If the L1 re-fetches instead of copying the delivered bytes, the sha256 in `SHA256SUMS` and the Gate quotes can diverge. Location: `sources/SHA256SUMS`; mitigation is byte-exact copy.
7. **Landing requirement:** `deliver-quotes.tsv` names snapshots as `census/round-29/sources/<name>` because `check_entry` rejects a `snapshot:` outside the configured snapshot dir. The bytes currently sit at `.ufo/waves/round-29/w1/sources/<name>`; they must be copied byte-exact (sha256 above) to `census/round-29/sources/` when the L1 composes `corpus/knowledge/duplicate-verdict-identity.md` and `duplicate-verdict-byte-equality.md`, or the Gate lines will fail `check4-snapshot-missing`. Location: `tools/souji-gate-check.py:check_entry` (snapshot-root check).
8. **No index contact.** `.ufo/waves/` is ignored (`.gitignore:1:.ufo/waves/`), confirmed with `git check-ignore -v`; `git status --porcelain` at the end showed only the pre-existing sibling modification `.ufo/waves/round-26/w1/ScribeGateDraft.md`, which is not mine and was left untouched.

## Attack log

N/A — this seat is a source-pinning seat, not an attack seat. Findings 1–3 are instrument observations (gate quote parser + pdftotext character fidelity) offered to the round's attack seats; no predicate, target, counter or case set is proposed for change.

## Deliveries

All under `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/`:

- `sources/statx.2.html` — sha256 `2a47fe319c5894d7d907b5ac03ced8cf64fb786bab69c12d276e90ba18359e8e`
- `sources/link.2.html` — sha256 `9cb197a7abe32a459bb3dbe96f67d906ff199e0f9d5f19f41a3a05e46cea1ec9`
- `sources/cmp.1.html` — sha256 `5c68e8d874e987391e7679dd2637f953b90087076bffe6de18c40db86cd046a3`
- `sources/broder97resemblance.pdf` — sha256 `da1227992d4a308f9f6f9f99893fd7b00c26e6cf757b1372f426074c101ef56b`
- `sources/broder97resemblance.txt` — sha256 `3ba1e117c6267c72e6c20e37d5b0b98e76bdb4fcf6429f49204cb3196d28325d` (pdftotext 26.08.0)
- `sources/SHA256SUMS` — 414 bytes, sha256 `dba28f7b18280355f48943e02d1e29494eb304ee5258fc1d242166b0e58c1647`
- `deliver-quotes.tsv` — 9 claim rows + header, sha256 `0c9aa9e611733c0eacd4b04e424a629d513334c3d7e4e783a163834ac1d5efe1`
