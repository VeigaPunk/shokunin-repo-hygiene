# R42scribe06 — S259 row and Gate block (round 42, wave 1, role scribe)

Verdict: S259 row and Gate text drafted; quote located and matched live; one caveat in the requested scope is NOT supported by the S259 page (see Finding F1); the row's `used-by` path does not exist yet and must be created by the L1 in the same landing (see F2). corpus/SOURCES.md was not edited.

## Hash check (live bytes vs L1 snapshot)

Commands (run from scratch dir `/fast/scratch/hyaku/souji-r42/R42scribe06`):

```
curl -sSL -A "Mozilla/5.0" -o live.html -w "http=%{http_code} size=%{size_download} url=%{url_effective}\n" https://docs.python.org/3/library/site.html
sha256sum live.html /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/sources/python-3-library-site.html
cat /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/sources/SHA256SUMS
```

Output:

```
http=200 size=76970 url=https://docs.python.org/3/library/site.html
620581fe5440952a9b62554526f6fe613b030b2c7a1521e1e57495f22e5d546a  live.html
620581fe5440952a9b62554526f6fe613b030b2c7a1521e1e57495f22e5d546a  .../census/round-42/sources/python-3-library-site.html
620581fe5440952a9b62554526f6fe613b030b2c7a1521e1e57495f22e5d546a  python-3-library-site.html
```

- Live page sha256: `620581fe5440952a9b62554526f6fe613b030b2c7a1521e1e57495f22e5d546a` (76970 bytes).
- L1 snapshot sha256: `620581fe5440952a9b62554526f6fe613b030b2c7a1521e1e57495f22e5d546a` (`census/round-42/sources/python-3-library-site.html`, 76970 bytes).
- Verdict: the live bytes EQUAL the L1 snapshot. No finding of drift at 2026-10-28.

The served page is "Python 3.15.2 documentation" (snapshot line 11 meta and page header text). The row records that version in its anchor.

## Quote location (snapshot lines = live bytes, identical)

Commands: HTML grep and plain-text extraction (python regex strip of tags, whitespace collapse) of the live page.

- Quote "an attempt is made to import a module named sitecustomize, which can perform arbitrary site-specific customizations." — snapshot `python-3-library-site.html` lines 418-419, section `module-sitecustomize`, the text after "After these path manipulations,". Word count: 16 (≤25). Present verbatim in the extracted live text (python check: `quote_in_live_text=True`).
- Suppression sentence "The automatic import can be suppressed using the interpreter’s -S option." — lines 227-228, § `site` introduction (`<p><strong>This module is automatically imported during initialization.</strong> The automatic import can be suppressed using the interpreter’s … -S … option.</p>`). Present in extracted live text (`suppress_in_live_text=True`).
- Also at lines 230-231: "However, Python startup option -S blocks this, and this module can be safely imported with no automatic modifications to the module search path or additions to the builtins."

## Census shape of the proposed row

Row file: `.ufo/waves/round-42/w1/R42scribe06/S259-row.md` (one line). Checks run:

```
awk -F'|' '{print "NF="NF" cells="NF-2}' S259-row.md        -> NF=13 cells=11
awk on S255-S258 rows                                        -> NF=13 (same shape)
row_lines=1, double_quotes=4 (two quoted spans: the version string and the 16-word quote)
```

- 11 cells, no pipe inside any cell; id `S259`, kind `docs`, tier `A` (vendor documentation, official Python docs), status `mined`, opened `2026-10-28`, recheck `on-release` (symbolic cadence; the page is version-specific and changes per Python release), used-by `corpus/lessons/round-42.md`.
- Shape follows S255-S258: col5 carries the scope, col6 the anchor, col7 the located quote (the existing rows put the grounding quote in the teaches column).

## Findings

F1 — the requested scope caveat "-S and -I bypass it" is only partly supported by the S259 page.
- The S259 page (`site.html`) documents only `-S`. It contains no mention of `-I`, `isolated`, or `PYTHONPATH` (grep counts: `PYTHONPATH` = 0; no `-I`/`isolated` tokens). The `-I` caveat therefore cannot be admitted under S259.
- Separate, not-admitted source checked for the caveat: `https://docs.python.org/3/using/cmdline.html` (HTTP 200, 171073 bytes, sha256 `c19141f2030687e14e00e73fff1ed482c3608813dfdc66a0b0931b92bb2902ac`, fetched to scratch and not copied). Its `-I` entry: "Run Python in isolated mode. This also implies -E, -P and -s options. In isolated mode sys.path contains neither the script’s directory nor the user’s site-packages directory. All PYTHON* environment variables are ignored, too." Its `-S` entry: "Disable the import of the module site and the site-dependent manipulations of sys.path that it entails."
- Consequence: `-I` does not appear to disable the site import; it drops PYTHON* environment variables (so a PYTHONPATH-delivered module is not searched). The Gate text states this and marks the `-I` line as NOT located on S259. If the L1 wants `-I` admitted as a bypass, it needs its own admitted row (a new S-id) for the command-line page; this scribe did not create one.
- `-S` → sitecustomize: the site page says the automatic import is suppressed by `-S` and that `sitecustomize` is attempted by the site module after its path manipulations. That `-S` also removes the sitecustomize attempt is [INFERENCE] from the module's own text (the import is performed by site), recorded as such in the Gate block.

F2 — `used-by` path does not exist yet.
- `corpus/lessons/round-42.md` is absent at the lane tip (`ls: cannot access`). CORPUS.md census (line 147 of its census script) requires every `mined` row's `used-by` path to exist. The L1 must create the round-42 lesson (with the `## Gate` table from `S259-gate.md`) in the same landing as the row, or the row must stay `queued` with `used-by` `—` until it exists.

F3 — PYTHONPATH delivery is not on the S259 page.
- The page places the typical `sitecustomize` "in the site-packages directory" (line 420). The C2 knowledge that the patches leg uses a `sitecustomize` on PYTHONPATH is NOT admitted by S259; PYTHONPATH is absent from the page (0 occurrences). The Gate text marks this as [INFERENCE] needing its own source. This matters for the C2 knowledge entry's `source:` line: it should cite S259 only for the automatic import and `-S`.

## Files written

- `.ufo/waves/round-42/w1/R42scribe06/S259-row.md` — proposed registry row (one line, 11 cells).
- `.ufo/waves/round-42/w1/R42scribe06/S259-gate.md` — Gate block (URL, access date 2026-10-28, quote, location, admitted-for with scope caveats F1 and F3).
- `.ufo/waves/round-42/w1/R42scribe06.md` — this report.

Not edited: `corpus/SOURCES.md`, any frozen census/tools/tests file, any tracked file. The one lane command run beyond the scratch work was a read-only `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat -- corpus/SOURCES.md` (empty output; used only to confirm the registry was untouched). No mutating git/jj command was run. No tools were installed or upgraded (no tool needed beyond curl, sha256sum, python3, awk, which were already present).

## Scratch

Scratch dir `/fast/scratch/hyaku/souji-r42/R42scribe06/` held `live.html`, `live.txt`, `cmdline.html`; removed before yield (see final shell call). No receipt in scratch is cited as evidence; every evidence pointer above is a committed path (`census/round-42/sources/...`) or a value recorded here.
