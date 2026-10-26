# SwarmScribe40 — SourceTempfile (SOURCES S226), round 33 w1

## Status

STATUS: PASS — Python 3.14 tempfile docs opened live (HTTP 200, 75194 bytes) and drafted as registry row S226 (docs/A/mined, 11 columns, NF=13) plus a rejected candidate row S227; both appended in a scratch clone and validated (`file ok`, exit 0); the only remaining gate is L1 landing `corpus/lessons/round-33.md` (E11 until then) and confirming S227's provisional id.

## Evidence

All lane reads were `git -C … show 2d9bca55a9f042a2c9ed60a797a8069e74c41f46:…`; all writes went to `.ufo/waves/round-33/w1/`; scratch was `/fast/scratch/hyaku/souji-r33/SourceTempfile/` (`TMPDIR=$D/tmp`), removed at the end.

Fetch (the opened source; `TMPDIR=/fast/scratch/hyaku/souji-r33/SourceTempfile/tmp`):

```
$ curl -sS -D headers-S226.txt -o src-S226.html -w 'HTTP %{http_code} bytes %{size_download} url %{url_effective}\n' \
    https://docs.python.org/3.14/library/tempfile.html
HTTP 200 bytes 75194 url https://docs.python.org/3.14/library/tempfile.html
$ sha256sum src-S226.html
6e65c9c14ec44b222591fc1662067cd1087a118f9d465945262ad195dc6bc5e5  src-S226.html
headers: HTTP/2 200 · content-type text/html · last-modified Mon, 26 Oct 2026 10:41:46 GMT · content-length 75194
page version line: Python 3.14.10 documentation
```

Quotes verified present in the fetched bytes after markup stripping, one occurrence each, no pipe:

```
"The directory named by the TMPDIR environment variable."            (8 words, § tempfile.gettempdir)
"The result of this search is cached, see the description of tempdir below." (13 words, same section)
```

Silence sweep on the same bytes (this is the negative claim): page-text counts `slash=0 trailing=0 normali[sz]=0`; raw `grep -oic` on the file gives the same three zeros.

Validation in scratch (`git clone -q --no-local …` → origin removed → `git -C "$D/c" rev-parse --show-toplevel` = `/fast/scratch/hyaku/souji-r33/SourceTempfile/c`; prereg `corpus/SOURCES.md` copied in; two rows appended after S223; no commit):

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file "$D/c/corpus/SOURCES.md"
… 36 pre-existing W04 lines, none for S226/S227 …
file	ok	/fast/scratch/hyaku/souji-r33/SourceTempfile/c/corpus/SOURCES.md
rcA=0

$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file "$D/c/corpus/SOURCES.md" --today 2026-10-26 | grep -v 'W04'
file	E11	S226 missing used-by corpus/lessons/round-33.md
rcB=1                      # lesson stub removed: the prereg-commit state
```

Census on the same copies: base `rows 147 / tier.A 139 / status.mined 124 / status.rejected 9`; with both rows `rows 149 / tier.A 141 / status.mined 125 / status.rejected 10` (`invalid` and `missing` 0, both exit 0).

Implementation corroboration, opened because the page is silent (not a row of this seat): `https://raw.githubusercontent.com/python/cpython/v3.14.0/Lib/tempfile.py`, HTTP 200, 32875 bytes, 977 lines, sha256 `e3e951ac276abd01709060e4d65a483b9e33beda8b5bba79c756a16ac1fdedb7`; `:163` `for envname in 'TMPDIR', 'TEMP', 'TMP':`, `:198-199` `dir = _os.path.abspath(dir)`, `:302-312` the `_once_lock` cache, `:396` `return _os.path.abspath(file)`. Executed on host `python3 3.14.8` under a scratch TMPDIR: `TMPDIR="$D/tmp/"` → gettempdir `<D>/tmp` (slash gone, identical to no-slash); `mkdtemp()` → `<D>/tmp/tmpadjq4x8d`; `env -u TMPDIR -u TEMP -u TMP` → `/tmp`; gettempdir before `os.environ["TMPDIR"]="/var/tmp"` returned the old value twice (cached).

No tool was installed or upgraded (no pacman/uv/npx/cargo use; `curl`, `git`, `python3 -B` and the fleet script were already present).

## Findings

1. **Row S226 admitted, structurally clean.** Draft in `.ufo/waves/round-33/w1/deliver-src-S226.md` §2: `docs | A | mined | 2026-10-26 | 90d | corpus/lessons/round-33.md`, anchor carrying the page's own `Python 3.14.10 documentation` line plus HTTP 200 / 75194 bytes / sha256 `6e65c9c1…8352e5`. `ln.split('|')` → 13 fields; no cell contains a literal or escaped pipe. Recheck is `90d` because the page is patch-stamped (3.14.10) while the host runs 3.14.8.
2. **One pre-landing gate, on S226 only**: `E11 S226 missing used-by corpus/lessons/round-33.md` (exit 1) at the prereg-commit state. QUALITY Q62 also requires that lesson to name S226; L1 owns both.
3. **The page cannot ground the trailing-slash half of the teaching.** Page text has zero `slash`, `trailing` and `normali[sz]` occurrences; the normalisation is `Lib/tempfile.py@v3.14.0:198-199` plus my probe on 3.14.8. Any C2 prose that says tempfile normalises a trailing slash must cite that line or the probe, not S226 (QUALITY Q2). For the O4/O5 legs the mechanism sits on the shell side instead: `tools/souji-census.sh:309` and `:1879` `mktemp -d "${TMPDIR:-/tmp}/souji-census-now.XXXXXX"`, `tools/souji-round9-selftest.sh:7` `mktemp -d "${TMPDIR:-/var/tmp}/souji-round9-selftest.XXXXXX"` — string concatenation, so a trailing slash doubles the separator. Attribution of O4/O5 to concatenation alone is `[INFERENCE]`; I ran neither leg.
4. **Rejected candidate S227** (`.ufo/waves/round-33/w1/deliver-src-S226.md` §2–§3): `https://docs.python.org/3/library/tempfile.html`, opened 2026-10-26, HTTP 200, 75190 bytes, sha256 `edd52c8b…b7766`, title `Python 3.15.2 documentation`. Same teaching, wrong version line for a lane interpreter of 3.14.8 → `status=rejected`, flip on a 3.15 interpreter move. Id is provisional: no other w1 seat claims S227 (`w1/swarm-registry.json` contains no `S22x` string; the three source seats are SourcePOSIX/SourceProcFd/SourceTempfile).
5. **No URL collision**: the only other Python 3.14 row is S074 (`.../3.14/library/subprocess.html`); the validator raised no W04/E04 for either new row. The 33 W04 lines in RUN A are base rows.
6. **Snapshot** saved at `.ufo/waves/round-33/w1/src-S226.html`, 75194 bytes, sha256 re-checked after the copy = `6e65c9c14ec44b222591fc1662067cd1087a118f9d465945262ad195dc6bc5e5` (not committed by this seat).
7. Scratch `/fast/scratch/hyaku/souji-r33/SourceTempfile` removed (`scratch_exists=no`); no tree of mine remains under `/fast/scratch/hyaku/souji-r33/`.

## Deliveries

- `.ufo/waves/round-33/w1/deliver-src-S226.md` — access record, both registry rows, the Gate block entries (ADMIT S226 / REJECT 3.15.2), validation and census output, implementation corroboration, findings, cleanup.
- `.ufo/waves/round-33/w1/src-S226.html` — the fetched bytes (75194, sha256 `6e65c9c14ec44b222591fc1662067cd1087a118f9d465945262ad195dc6bc5e5`).
- `.ufo/waves/round-33/w1/SwarmScribe40.md` — this report.
