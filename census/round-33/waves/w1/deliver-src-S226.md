# deliver-src-S226 — Python 3.14 tempfile docs (SOURCES S226, opened 2026-10-26)

Seat SwarmScribe40 (SourceTempfile), round 33 wave w1. Read-only seat: nothing below was
committed, staged or written into the lane tree; the only lane writes are this file, the
`src-S226.html` snapshot named by the item, and `SwarmScribe40.md`.

Frozen base for the registry shape: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 2d9bca55a9f042a2c9ed60a797a8069e74c41f46:corpus/SOURCES.md`
(rows end at S223; the three w1 source seats hold S224/S225/S226 — this item is S226).

## 1. Access record (the opened source)

| field | value |
|---|---|
| URL | `https://docs.python.org/3.14/library/tempfile.html` |
| HTTP status | `HTTP/2 200` |
| bytes | 75194 |
| sha256 | `6e65c9c14ec44b222591fc1662067cd1087a118f9d465945262ad195dc6bc5e5` |
| `content-type` | `text/html` |
| `last-modified` | `Mon, 26 Oct 2026 10:41:46 GMT` |
| page version line | `Python 3.14.10 documentation` |
| snapshot | `.ufo/waves/round-33/w1/src-S226.html` (same sha256 recomputed after the copy) |
| fetched | 2026-10-26, `curl -sS -D headers-S226.txt -o src-S226.html https://docs.python.org/3.14/library/tempfile.html` |

Command that produced the record (`TMPDIR=/fast/scratch/hyaku/souji-r33/SourceTempfile/tmp`):

```
$ curl -sS -D headers-S226.txt -o src-S226.html -w 'HTTP %{http_code} bytes %{size_download} url %{url_effective}\n' \
    https://docs.python.org/3.14/library/tempfile.html
HTTP 200 bytes 75194 url https://docs.python.org/3.14/library/tempfile.html
$ sha256sum src-S226.html
6e65c9c14ec44b222591fc1662067cd1087a118f9d465945262ad195dc6bc5e5  src-S226.html
```

Anchor: `§ tempfile.gettempdir` (search list + caching sentence), `§ tempfile.gettempdirb`,
`§ tempfile.mkdtemp`, `§ tempfile.tempdir`. Section ids present in the fetched bytes:
`module-tempfile`, `tempfile.mkdtemp`, `tempfile.gettempdir`, `tempfile.gettempdirb`,
`tempfile.tempdir`, plus the mkstemp/mktemp family.

### Quotes (verbatim from the fetched bytes, markup stripped at span boundaries, no pipe character)

1. § tempfile.gettempdir, first item of the search list — 8 words, 1 occurrence in the page text:
   > The directory named by the TMPDIR environment variable.
2. § tempfile.gettempdir, the sentence after the list — 13 words, 1 occurrence:
   > The result of this search is cached, see the description of tempdir below.

Served markup around quote 1 (raw bytes, for the byte-exact reading):
`<li><p>The directory named by the <span class="target" id="index-1"></span><code class="xref std std-envvar docutils literal notranslate"><span class="pre">TMPDIR</span></code> environment variable.</p></li>`

### Negative (the page is silent on trailing-slash normalisation)

```
$ python3 -B -c "… re.sub(r'<[^>]+>','',html); counts on page text …"
slash count in page text= 0 trailing= 0 normali[sz]= 0
```

Raw-byte sweep on the same file: `grep -oic 'slash' / 'trailing' / 'normali[sz]'` → `0 / 0 / 0`.
So the page decides neither half of the trailing-slash question; per QUALITY Q2 that half needs
source at a tag or a fixture run, not this row (see §5).

## 2. Registry rows (append inside `## Registry`, after S223)

```
| S226 | Python 3.14 tempfile documentation — https://docs.python.org/3.14/library/tempfile.html | docs | A | how Python 3.14 chooses the scratch root: the gettempdir search list with TMPDIR first, its cached result, and mkdtemp taking gettempdir as the dir default when dir is None; not the trailing-slash question (the page never mentions a slash) and not shell-side TMPDIR joining in a lane script | § tempfile.gettempdir search list first item, and its caching sentence; § tempfile.gettempdir definition sentence for the dir default; § tempfile.mkdtemp `dir` and absolute-return sentence; page self-identifies "Python 3.14.10 documentation"; HTTP 200, 75194 bytes, sha256 6e65c9c14ec44b222591fc1662067cd1087a118f9d465945262ad195dc6bc5e5 | TMPDIR is the first directory gettempdir tries, the search result is cached so an override must precede first use, and dir=None falls back to gettempdir; the page states no trailing-slash normalisation, so that claim needs source at a tag or a fixture | mined | 2026-10-26 | 90d | corpus/lessons/round-33.md |
| S227 | Python 3.15.2 tempfile documentation — https://docs.python.org/3/library/tempfile.html | docs | A | the same gettempdir and mkdtemp teaching at the 3.15.2 documentation line, which is not the interpreter this lane runs | § tempfile.gettempdir, § tempfile.mkdtemp; page self-identifies "Python 3.15.2 documentation"; HTTP 200, 75190 bytes, sha256 edd52c8b5fff8445f14d30f8f98a4977ce481b00ab352a51aa29e3beb37b7766 | rejected: the version line differs from the lane interpreter (python3 3.14.8) and the teaching is identical, so it adds no fact that S226 does not already hold | rejected | 2026-10-26 | 365d | — |
```

Row shape: 11 columns / `NF=13` for both rows, no literal or escaped pipe in any cell
(`ln.split('|')` → 13 fields each; cell scan for `\|` → none). `kind=docs`, `tier=A`,
`status` in the frozen enum, `opened` ISO past date, `recheck=90d` (an `NNd` cadence: the page is
patch-version stamped and re-stamped at 3.14.10 while the host runs 3.14.8, so 90 days forces a
version re-read), `used-by corpus/lessons/round-33.md` for the mined row and `—` for the rejected one.

Two L1 decisions are explicitly left to L1:

- **S227's id.** The id is provisional: no other seat in `w1/swarm-registry.json` claims S227
  (`swarm-registry.json` has zero `S22x` strings; the three source seats are SourcePOSIX,
  SourceProcFd, SourceTempfile). If L1 lands S224/S225/S227 for a different candidate, renumber
  the rejection row and keep the teaches cell — the row is curation-only, as S044/S048 were.
- **The used-by dependency.** `corpus/lessons/round-33.md` does not exist at the prereg commit, so
  the row cannot validate clean until L1 lands the lesson. QUALITY Q62 also requires that lesson to
  name S226 in the direction the row claims. §4 RUN B records that as the only pre-landing finding.

## 3. Gate block entry for `corpus/lessons/round-33.md` `## Gate`

Header row used by round-28's Gate (the shape this lane already reads):
`| Candidate | Decision | Source reopened | Located quote / evidence | Reason / flip |`

```
| S226 Python 3.14 `tempfile` docs | ADMIT | https://docs.python.org/3.14/library/tempfile.html, opened 2026-10-26, HTTP 200, 75194 bytes, sha256 `6e65c9c14ec44b222591fc1662067cd1087a118f9d465945262ad195dc6bc5e5`; snapshot `.ufo/waves/round-33/w1/src-S226.html` | § tempfile.gettempdir, first search-list item: “The directory named by the TMPDIR environment variable.” (8 words); § tempfile.gettempdir, next sentence: “The result of this search is cached, see the description of tempdir below.” (13 words) | Grounds the C2 scratch-root mechanism: TMPDIR is tried first, and the cached result means a scratch override must be set before the module's first use. The page is silent on trailing-slash normalisation (page-text counts `slash=0 trailing=0 normali[sz]=0`), so that half is NOT claimed here and needs source at a tag or a fixture (Q2). Recheck `90d`. |
| Python 3.15.2 `tempfile` docs | REJECT | https://docs.python.org/3/library/tempfile.html, opened 2026-10-26, HTTP 200, 75190 bytes, sha256 `edd52c8b5fff8445f14d30f8f98a4977ce481b00ab352a51aa29e3beb37b7766`; page title reads `tempfile — Generate temporary files and directories — Python 3.15.2 documentation` | Same two sections; the teaching is byte-identical in substance to S226 | Version line is 3.15.2 against a lane interpreter of `python3 3.14.8`; it adds no fact S226 does not hold, so it is a curation rejection (S227, status `rejected`). Flip: re-open when the lane's interpreter line moves to 3.15. |
```

## 4. Validation in scratch

Scratch root `/fast/scratch/hyaku/souji-r33/SourceTempfile/` with `TMPDIR=$D/tmp` created;
clone `git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin "$D/c"`, origin removed
at once, `git -C "$D/c" rev-parse --show-toplevel` printed
`/fast/scratch/hyaku/souji-r33/SourceTempfile/c` before any write. `corpus/SOURCES.md` in the clone
was replaced by the prereg blob (254 lines), the two rows appended after S223, and only that copy
validated. No commit was made in the clone; no lane file was touched.

RUN A — row plus a `corpus/lessons/round-33.md` stub that names S226 (the post-landing state):

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file "$D/c/corpus/SOURCES.md"
file	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
file	W04	S036 duplicate url git-scm.com/docs/git across scopes
… (36 pre-existing W04 rows, none for S226/S227) …
file	W04	S216 duplicate url man7.org/linux/man-pages/man2/statx.2.html across scopes
file	ok	/fast/scratch/hyaku/souji-r33/SourceTempfile/c/corpus/SOURCES.md
rcA=0
```

RUN B — same file, the lesson stub removed (the state at the prereg commit), W04 filtered:

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file "$D/c/corpus/SOURCES.md" --today 2026-10-26 | grep -v 'W04'
file	E11	S226 missing used-by corpus/lessons/round-33.md
rcB=1
```

RUN B is the single expected pre-landing finding: E11 on the missing lesson path, and nothing else —
no E01–E10, no E12, no finding on S227, and no W02/W03. So the rows are structurally clean and the
only gate left is L1 landing `corpus/lessons/round-33.md` with an S226 citation (Q62).

Census counts on the same two files (the number L1's sources census will need):

```
$ sources-census.sh census --file "$D/base/corpus/SOURCES.md"      # prereg bytes
file	rows	147   tier.A 139  tier.B 6  tier.C 2   status.queued 14  status.mined 124  status.rejected 9
$ sources-census.sh census --file "$D/c/corpus/SOURCES.md"         # + S226 + S227
file	rows	149   tier.A 141  tier.B 6  tier.C 2   status.queued 14  status.mined 125  status.rejected 10
```

(`tier.invalid`/`status.invalid` = 0 and `missing` = 0 in both runs; both exited 0.)

## 5. Implementation corroboration (opened for the silence, NOT a registry row of this seat)

The page's silence on normalisation is answered by source at a tag, which is what Q2 asks for. I
opened it so the round does not read the silence as "no behaviour":

| field | value |
|---|---|
| URL | `https://raw.githubusercontent.com/python/cpython/v3.14.0/Lib/tempfile.py` |
| HTTP status | `HTTP/2 200`, 32875 bytes, 977 lines |
| sha256 | `e3e951ac276abd01709060e4d65a483b9e33beda8b5bba79c756a16ac1fdedb7` |
| anchors | `Lib/tempfile.py:163` (env order), `:198-199` (per-candidate abspath), `:302-312` (`_gettempdir` caching), `:124-126` (`_sanitize_params` dir default), `:396` (mkdtemp return) |

Located quotes (≤25 words, no pipe):

- `:163` — `for envname in 'TMPDIR', 'TEMP', 'TMP':` (implementation confirms the documented order).
- `:198-199` — `if dir != _os.curdir:` / `dir = _os.path.abspath(dir)` (each candidate is made
  absolute, and `abspath` removes a trailing slash), so the value gettempdir returns is normalised.
- `:302-312` — the double-checked `tempdir is None` assignment under `_once_lock` (the caching the
  page describes).

Executed probe on the host interpreter (scratch TMPDIR only, no lane script run):

```
$ python3 -V
Python 3.14.8
$ TMPDIR="$D/tmp/" python3 -B -c 'import tempfile;print(repr(tempfile.gettempdir()))'
'/fast/scratch/hyaku/souji-r33/SourceTempfile/tmp'
$ TMPDIR="$D/tmp"  python3 -B -c 'import tempfile;print(repr(tempfile.gettempdir()))'
'/fast/scratch/hyaku/souji-r33/SourceTempfile/tmp'
$ TMPDIR="$D/tmp/" python3 -B -c 'import tempfile;d=tempfile.mkdtemp();print(d);import os;os.rmdir(d)'
/fast/scratch/hyaku/souji-r33/SourceTempfile/tmp/tmpadjq4x8d
$ env -u TMPDIR -u TEMP -u TMP python3 -B -c 'import tempfile;print(repr(tempfile.gettempdir()))'
'/tmp'
$ python3 -B -c 'import tempfile,os;first=tempfile.gettempdir();os.environ["TMPDIR"]="/var/tmp";print(repr(first), repr(tempfile.gettempdir()))'
'/fast/scratch/hyaku/souji-r33/SourceTempfile/tmp' '/fast/scratch/hyaku/souji-r33/SourceTempfile/tmp'
```

Read-out: a trailing slash in TMPDIR does not survive gettempdir or mkdtemp on 3.14.8, and setting
TMPDIR after the first call changes nothing. That is implementation evidence at v3.14.0 plus a
fixture run — it is NOT what S226 claims, and it is not in the S226 row.

## 6. Findings

1. **S226 admits and is structurally clean** (`## Registry` append, 11 columns, NF=13, kind/doc,
   tier A, status mined, opened 2026-10-26, recheck 90d, used-by `corpus/lessons/round-33.md`).
   RUN A above: `file ok`, exit 0.
2. **One pre-landing gate on S226 only**: E11 for the absent `corpus/lessons/round-33.md`
   (RUN B, exit 1). L1 must land that lesson naming S226 (Q62 bidirectional used-by).
3. **The page cannot ground the trailing-slash claim.** Page text counts `slash=0 trailing=0
   normali[sz]=0`; the normalisation lives in `Lib/tempfile.py@v3.14.0:198-199`. If the round's C2
   prose says "tempfile normalises a trailing slash", its citation must be the code line or the
   probe, not S226. For C2's own legs this matters only as attribute: the two slash legs (O4, O5)
   run `tools/souji-census.sh` and `tools/souji-round9-selftest.sh`, which build their paths by string
   concatenation — `tools/souji-census.sh:309` and `:1879` `CENSUS_TMP=$(mktemp -d "${TMPDIR:-/tmp}/souji-census-now.XXXXXX")`,
   `tools/souji-round9-selftest.sh:7` `R9_TMP=$(mktemp -d "${TMPDIR:-/var/tmp}/souji-round9-selftest.XXXXXX")` —
   so a trailing slash doubles the separator in the shell path, where Python's `tempfile` would have
   removed it. `[INFERENCE]` that attribution to string concatenation is the whole cause; I did not
   run either leg and did not read the O4/O5 failures.
4. **Version skew, recorded not resolved**: the page is `Python 3.14.10 documentation`, the host
   interpreter is 3.14.8. All four claims I quote are present and were exercised on 3.14.8, so the
   skew does not touch this row; it is why recheck is `90d` rather than `on-release`.
5. **`docs.python.org/3.14/library/tempfile.html` is not a duplicate URL** in the frozen registry:
   the only other 3.14 Python row is S074 (`.../3.14/library/subprocess.html`). The census validator
   reports no W04/E04 for S226; the 36 W04 lines in RUN A are pre-existing base rows.
6. **S227 is a curation rejection, not a claim**: the 3.15.2 page differs only in the version line
   for this teaching, and the lane runs 3.14.8. Its id is provisional (see §2).

## 7. Cleanup

Scratch removed with `rm -rf /fast/scratch/hyaku/souji-r33/SourceTempfile`; nothing left under
`/fast/scratch/hyaku/souji-r33/`. No tool was installed or upgraded for this item (no `pacman`,
`uv`, `npx` or cargo channel used); `curl`, `git`, `python3 -B` and the fleet
`sources-census.sh` were already present.

## 8. Explicit non-claims

- I did not run any lane tool, selftest, counter or leg, and did not touch SCORECARD.md, tools/,
  tests/ or any frozen pin.
- I did not commit, stage, or write outside `.ufo/waves/round-33/w1/`.
- Nothing here asserts a C1 or C2 verdict; the row is source curation for C2's mechanism.
