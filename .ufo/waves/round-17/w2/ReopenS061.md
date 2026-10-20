STATUS: DONE — S061 re-opened independently: the primary quote is verbatim and 15 words at `#str.lstrip`, but 4 of the 11 drafted cells fail as drafted (id, anchor footer clock, teaches tail, status/used-by); tier/scope/kind/recheck/source/opened agree.

# ReopenS061 — independent re-open of S061 (Python `str.lstrip` / `str.removeprefix`)

Scope: the one assignment question — verify the w1 quote against the served page today, record the
served version/last-updated line, and audit the drafted tier/status/scope/teaches cells for claims
the page does not support. Wave-1 artifact read:
`.ufo/waves/round-17/w1/SrcPyLstrip.md` (row at `:47`, access record `:7-17`, quote `:21`,
`S051` note `:52-53`, FP claim `:62-63`, fix `:105-106`).

## 1. What was served (observed 2026-10-20, ~17:32 UTC)

- Requested `https://docs.python.org/3/library/stdtypes.html` →
  `HTTP/2 301`, `location: https://docs.python.org/3/builtins/stdtypes.html` (date `Tue, 20 Oct 2026 17:32:19 GMT`).
  The 301's own body is 162 bytes; the target answers `HTTP/2 200`.
- Canonical response headers: `last-modified: Tue, 20 Oct 2026 17:18:59 GMT`,
  `etag: "6ad7a283-c6d92"`, `content-length: 814482`.
- Title: `Built-in Types — Python 3.15.0 documentation` (the em dash is `&#8212;`; `og:url` is the
  canonical URL, `og:image` is under `/3.15/`).
- Footer: `Last updated on Oct 20, 2026 (17:16 UTC).` , `Created using Sphinx 8.2.3.`
- Structure: `<section id="text-sequence-type-str">` → `<h2>Text Sequence Type — str</h2>`;
  `<section id="string-methods">` → `<h3>String Methods</h3>`; `id="str.lstrip"` occurs exactly
  **once**, inside `string-methods`; `id="str.removeprefix"` likewise. The page also carries
  `bytes.lstrip` under `bytes-and-bytearray-operations`.

**Discrepancy vs w1, observed not inferred:** w1 recorded the footer as
`Last updated on Oct 20, 2026 (13:43 UTC).` (`SrcPyLstrip.md:13`) from a 16:33 UTC fetch; an hour
later the same URL serves `17:16 UTC` with `Last-Modified 17:18:59 GMT`. The page is rebuilt
intraday, so an exact footer clock is not a stable receipt. The date `Oct 20, 2026` is stable.

## 2. Primary quote check — VERBATIM, 15 words, at the named anchor

Page paragraph at `#str.lstrip` (HTML collapsed to text, `<em>` shown as `*…*`):

> Return a copy of the string with leading characters removed. The *chars* argument is a string
> specifying the set of characters to be removed. If omitted or `None`, the *chars* argument
> defaults to removing whitespace. The *chars* argument is not a prefix; rather, all combinations
> of its values are stripped:

- Quote as drafted: `“The *chars* argument is not a prefix; rather, all combinations of its values are stripped:”`
  — **character-exact** against the served paragraph after whitespace normalisation (the HTML wraps
  between `chars</em>` and `argument`; nothing else differs, and `chars` is `<em>` as the draft's
  italics imply). Programmatic containment check: `True`.
- Word count **15** (`The chars argument is not a prefix; rather, all combinations of its values are stripped:`), ≤25 ✓.
- Position: first `<p>` of the `str.lstrip` definition, **fourth and final sentence** ✓; the colon
  introduces the two-line example block ✓.
- Anchor: `#str.lstrip` resolves on the served page (one id), inside `String Methods` ✓.
- No `Changed in version` marker anywhere between `id="str.lstrip"` and `id="str.maketrans"` ✓
  (w1's "no other version stamp" holds).
- Example block asserted by the page:
  `'   spacious   '.lstrip()` → `'spacious   '` ; `'www.example.com'.lstrip('cmowz.')` → `'example.com'` ;
  and later `'Arthur: three!'.lstrip('Arthur: ')` → `'ee!'` against `removeprefix` → `'three!'`.

## 3. Per-cell verdicts (registry order, `corpus/SOURCES.md:13` header)

| cell | w1 text (abridged) | verdict | evidence |
|---|---|---|---|
| id | `S0??`, note "substitute S051" | **DISAGREE** | `corpus/SOURCES.md` holds exactly 50 rows, S001–S050 (`grep -c` → 50; last ids S048/S049/S050). Arithmetic S051 is next *free* id, but the round-17 numbering plan in this wave's context reserves S051–S060 for the jj/git rows and **S061** for this row; the assignment names S061. Landing at S051 collides. |
| source | "Python Built-in Types documentation: str.lstrip, str.removeprefix — URL `#str.lstrip`" | agree | Title is `Built-in Types — Python 3.15.0 documentation`; URL is the canonical 301 target. Style matches S040 (`corpus/SOURCES.md:54`) and S050 (`:64`). |
| kind | `docs` | agree | it is documentation, not code or own-work; matches every Python row. |
| tier | `A` | agree (precedent, not contract-read) | official `docs.python.org/3` language documentation; both prior Python rows are tier A (S040 `:54`, S050 `:64`). **Caveat:** `SOURCES-CONTRACT-v1` (the tier definition, `corpus/SOURCES.md:3`) is not a file in `corpus/` — that directory holds only `README.md`, `SOURCES.md`, `QUALITY.md` — and `QUALITY.md:5-7` defers tiers to `SOURCES.md`. So tier A is judged by registry precedent, not by re-reading the contract. |
| scope | "str.lstrip(chars) character-set semantics and its removeprefix contrast on the served Python 3.15.0 page; not bytes.lstrip and not audit-tool behaviour" | agree | page says "the *set* of characters to be removed" and "not a prefix; rather, all combinations"; `removeprefix` contrast is on the page; the `bytes.lstrip` exclusion is *necessary*, not pedantic — the same page documents `bytes.lstrip` (`id="bytes.lstrip"`, section `bytes-and-bytearray-operations`), so the row must pin `str`. "served Python 3.15.0 page" matches the title. |
| anchor | "§ String Methods › str.lstrip (#str.lstrip) and str.removeprefix (#str.removeprefix); page title …, footer 'Last updated on Oct 20, 2026 (13:43 UTC)'; 301s …" | **DISAGREE (footer clock only)** | section path and ids verified; title verified; 301 verified. The footer clock cannot be reproduced: now `17:16 UTC`, `Last-Modified 17:18:59 GMT`. An exact-time receipt that moves intraday is not a receipt. |
| teaches | "lstrip(chars) strips any combination … from the leading run, not a prefix, while removeprefix removes one prefix string; so target.lstrip('./') drops .ufo's leading dot — the r16 seat-audit V-WRITE-SCOPE false positive" | **DISAGREE (final clause)** | The mechanism half agrees: "leading run" is supported by "Return a copy of the string with leading characters removed." plus the page's own stopping example (`'www.example.com'.lstrip('cmowz.')` → `'example.com'`, stops at `e`). The definite "the … false positive" does not: D4's `.ufo` attribution (`corpus/lessons/round-16-verifier-spotcheck.md:137-138`) is the row L1 adjudicated in round 17 as a **true attempted fleet-root write**, and the landed auditor still classifies that shape as **major** — `V-WRITE-RELATIVE` "attempt semantics, major on ok and error alike" (`tools/souji-seat-audit.py:18-21` at ddb7347), selftest `report-edit-relative-dotufo` → `("V-WRITE-RELATIVE","major")` (`:292`). The page grounds the mis-normalisation (`target.lstrip("./")`, base 5fa6017 `tools/souji-seat-audit.py:80`), not any exoneration. |
| status | `mined` | **DISAGREE as drafted** | `corpus/lessons/round-17.md` → ABSENT (verified). Every mined row in the registry points at an existing used-by path; `queued` rows use `used-by —` (S005/S006, `corpus/SOURCES.md:19-20`). w1 disclosed this (`SrcPyLstrip.md:55-59`); it is a landing precondition, not a cell level. |
| opened | `2026-10-20` | agree | opened today; matches the access record. |
| recheck | `on-release` | agree | matches S040/S050; the page is the 3.15 development branch, and `str.lstrip` carries no version marker, so recheck-on-release is the right cadence. Pinning the footer clock would *not* be a recheck trigger. |
| used-by | `corpus/lessons/round-17.md` | agree with the status condition | path name matches the planned lesson; valid only once that file exists (see status). |

## 4. Corroborating-quote precision (not a cell, but a calibration defect)

`SrcPyLstrip.md:40` block-quotes the `removeprefix` sentence as verbatim ending
`… return a copy of the original string.` — the served page ends it with a **colon**:
`If the string starts with the *prefix* string, return string[len(prefix):]. Otherwise, return a
copy of the original string:` (followed by its example). One-character deviation in a
corroborating quote; the **primary** quote is unaffected.

## 5. What the page does not state (boundaries the cell text must respect)

- Nothing about seat-audit behaviour, `V-WRITE-SCOPE`, or any false positive. That clause is lane
  provenance and must be cited to the lesson/auditor, not implied from the page.
- "all combinations of its values are stripped" is bounded to the **leading run**; the page proves
  it by example, it does not say "anywhere in the string". The teaches paraphrase is sound only in
  that bounded form.
- The teaches cell omits "If omitted or `None`, the *chars* argument defaults to removing
  whitespace" — an omission, not an overclaim.
- `removeprefix` is marked "Added in version 3.9"; `lstrip` itself carries no version marker.
- The host-Python version in w1's fix note (`3.14`) was **not re-probed by me** (no version command
  run); the landed tool already uses `removeprefix` (`tools/souji-seat-audit.py:170` at ddb7347),
  so the ≥3.9 requirement is satisfied wherever its selftest ran. This is a note, not a cell.

## 6. Corrected row (single line, 11 cells, no internal `|`; smallest fix)

| S061 | Python Built-in Types documentation: str.lstrip, str.removeprefix — https://docs.python.org/3/builtins/stdtypes.html#str.lstrip | docs | A | str.lstrip(chars) character-set semantics and its removeprefix contrast on the served Python 3.15.0 page; not bytes.lstrip and not audit-tool behaviour | § String Methods (#string-methods, under Text Sequence Type — str) › str.lstrip (#str.lstrip) and str.removeprefix (#str.removeprefix); page title "Built-in Types — Python 3.15.0 documentation", Sphinx 8.2.3; footer date Oct 20, 2026 with an intraday rebuild clock (13:43 UTC at the w1 read, 17:16 UTC and HTTP Last-Modified 17:18:59 GMT at the w2 read); /3/library/stdtypes.html 301s to this canonical URL (curl -sSI 2026-10-20) | The chars argument "is not a prefix; rather, all combinations of its values are stripped": leading characters drawn from the set are removed and stripping stops at the first character outside it, while removeprefix removes one prefix string; this explains the .ufo-dot mis-normalization recorded at corpus/lessons/round-16-verifier-spotcheck.md:138 (target.lstrip("./") at base tools/souji-seat-audit.py:80) — the changed auditor replaces it with removeprefix("./") (:170) and still calls a bare relative target major V-WRITE-RELATIVE (:175, selftest :292) | mined | 2026-10-20 | on-release | corpus/lessons/round-17.md |

Landing precondition, unchanged from w1: land the row **with or after**
`corpus/lessons/round-17.md`; if it must land first, use status `queued` and used-by `—`
(precedent S005/S006). The row's id must be **S061**, not S051.

Verdict on the source claim itself: **holds** — the page states the character-set rule in the
strongest form ("not a prefix"), the quote is verbatim at the named anchor, and nothing on the page
contradicts the claim. Verdict on the drafted row: **partial** — 4 of 11 cells need the edits above.

## 7. Commands run (exact, with the load-bearing output)

```
curl -sSI https://docs.python.org/3/library/stdtypes.html | grep -iE '^(HTTP|location|date|last-modified|etag|content-length)'
# HTTP/2 301 ; location: https://docs.python.org/3/builtins/stdtypes.html ; date: Tue, 20 Oct 2026 17:32:19 GMT
curl -sSI -L … # HTTP/2 200 ; last-modified: Tue, 20 Oct 2026 17:18:59 GMT ; etag: "6ad7a283-c6d92" ; content-length: 814482
curl -sS https://docs.python.org/3/builtins/stdtypes.html -o /var/tmp/souji-r17-ReopenS061/stdtypes.html
grep -c 'id="str.lstrip"' <file>            # 1
grep -o 'Last updated on [^<]*' <file>      # Last updated on Oct 20, 2026 (17:16 UTC).
grep -o '<title>[^<]*' <file>               # Built-in Types &#8212; Python 3.15.0 documentation
python3 - <<'EOF' … EOF                     # parse: heading ids/text; quote containment True, 15 words; footer; etag; sphinx
                                            # lstrip section: string-methods ; removeprefix section: string-methods
                                            # Changed markers in lstrip entry: [] ; bytes.lstrip present: True
cd /home/vgpnk/Projects/shokunin/souji-shokunin
grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md   # 50
grep -oE '^\| S[0-9]{3,}' corpus/SOURCES.md | tail -3                  # S048 S049 S050
sed -n '12,18p' corpus/SOURCES.md                                      # 11-column header
grep -n 'docs.python.org' corpus/SOURCES.md                            # :54 S040, :64 S050
test -e corpus/lessons/round-17.md && echo EXISTS || echo ABSENT        # ABSENT
git show ddb7347:tools/souji-seat-audit.py | sed -n '10,32p'            # violation classes, V-WRITE-RELATIVE definition
git show ddb7347:tools/souji-seat-audit.py | cat -n | sed -n '168,176p' # :170 removeprefix("./") ; :175 V-WRITE-RELATIVE
git show ddb7347:tools/souji-seat-audit.py | sed -n '288,295p'          # selftest report-edit-relative-dotufo → major
git show 5fa6017:tools/souji-seat-audit.py | cat -n | sed -n '74,82p'   # :80 rel = target.lstrip("./")
grep -n 'lstrip\|V-WRITE-SCOPE\|own report path' corpus/lessons/round-16-verifier-spotcheck.md  # :137-138
grep -nE 'tier|Tier|contract' corpus/SOURCES.md corpus/QUALITY.md      # :3 SOURCES-CONTRACT-v1 ; QUALITY :5-7
```

Probe compliance: read/grep on the named lane files, `git show` (read-only) on the named revisions,
`curl` page fetches, and a local HTML parse of the fetched bytes; no `jj`, no git write, no lane
census/verify/audit tool run against any real directory, no recursive search over the lane or fleet
root, no writes outside `/var/tmp/souji-r17-ReopenS061/` (scratch HTML) and this report. No tool
installs or pacman transactions.

## 8. Remaining unknowns

- `SOURCES-CONTRACT-v1` (tier definitions, `corpus/SOURCES.md:3`) was not located by exact-path
  probe: `corpus/` holds only `README.md`, `SOURCES.md`, `QUALITY.md`, and `QUALITY.md:5-7` defers to
  `SOURCES.md`. Tier A is therefore supported by registry precedent (S040, S050), not by the frozen
  contract text.
- The frozen "mined rows whose used-by path does not exist" check was not located at an exact named
  path, so the status verdict rests on (a) the verified ABSENT file and (b) registry convention
  (no mined row points at a missing path; queued rows carry `—`).
- Why the page's footer clock advanced inside one hour (13:43 → 17:16 UTC) is not established; only
  the observation and the HTTP `Last-Modified` are. It is sufficient to bar an exact-clock receipt.
