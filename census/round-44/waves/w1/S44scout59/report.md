# S44scout59 — C2 source opening

Result: source opened and preserved; multiplicity interpretation supported. Axes: calibration / operability / coverage; this seat addresses operability only. No numerical score change or admission claim.

## Official source and located quote

- URL: https://docs.python.org/3/library/collections.html#collections.Counter
- Retrieved UTC: 2026-10-30T11:36:03.515664+00:00; HTTP 200. Header Last-Modified: Fri, 30 Oct 2026 11:10:16 GMT (not a claimed publication date).
- Snapshot: `collections.html`, 210465 bytes, SHA-256 `f65e762f0aac68e8c6d5825f643509582f0f6e93c72435cce614435f2760b55e`.
- Located quote (17 whitespace-separated words), Counter objects, snapshot lines 600–601: “Counters support rich comparison operators for equality, subset, and superset relationships: ==, !=, <, <=, >, >=.”
- Lines 478–481 describe counts as dictionary values and bags/multisets; lines 608–609 date missing-as-zero equality behavior to Python 3.10. Fetch metadata is preserved in `source-receipts.json`.

## Frozen source facts

Read preregistration C2 lines 14–20. Frozen blobs were obtained read-only with exact commands:

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show d314fd6e85d62565344fa6c4b102f52f62297884:census/round-44/c2-counter.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show d314fd6e85d62565344fa6c4b102f52f62297884:census/round-44/c2-hidden-audit.py
```

Both exited 0. Captures: `frozen-c2-counter.py` (SHA-256 `0cb6ce80a23b460d1a03e0530ca2ef0866af773bdb7f5b88f6dc84bd0f525252`, matching preregistration); `frozen-c2-hidden-audit.py` (SHA-256 `50872b0da7a36d377ced9cf0e51579ef00f0f0ae402eebad8c579fce6e5e843e`).

Observed textual definition/caller chain:
- `c2-counter.py:125–150` extracts the committed audit blob and invokes it to populate hidden_v2.
- `c2-hidden-audit.py:101–107`, `classes(p)`, retains every FINDING claim/class pair and sorts the resulting list; it does not deduplicate.
- `SCENARIOS:116–118` explicitly repeats `C2:FIELD-MISSING` four times for h4; h3 repeats UNATTACHED-KEY twice and h6 repeats KEY-DUPLICATE twice.
- `main:159–162` checks return code and `classes(p) == sorted(want)`.

Inference, high confidence: for these positive occurrence lists of strings, sorted-list equality expresses exactly the same multiset equality as `Counter(actual) == Counter(expected)`: order is irrelevant but each occurrence count must agree. A single literal `C2:FIELD-MISSING*4` is a different key, not four findings. Counter is explanatory here; the frozen audit actually uses sorted lists, not Counter. Zero/negative counts are irrelevant when constructing counts directly from occurrence lists. Plain set equality would lose the required multiplicity.

## Assigned bounded probe

Exact command, run from the seat scratch directory:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44scout59/probe.py
```

Exit 0. Python 3.14.8. Exact structured output is preserved in `bounded-probe.json`. The probe AST-extracted only frozen `classes` and the literal h4 expected list; it did not execute audit `main`, fixture construction, git mutations, or a counter suite.

| Input | sorted equality | Counter equality |
|---|---|---|
| reversed expected order | true | true |
| one repeated finding missing | false | false |
| one repeated finding extra | false | false |
| literal `FIELD-MISSING*4` replacing four entries | false | false |

Expected counts observed: HEADING-MALFORMED=1, UNATTACHED-KEY=1, FIELD-MISSING=4.

Source-opening tools: `read` opened the official URL; Python `urllib.request.urlopen(url, timeout=60)` independently saved the response bytes, status and headers. No installs or upgrades.

## Proposed registry row (candidate only)

| Source | Opened | Narrow support | Location / receipt | Limits |
|---|---|---|---|---|
| Python standard library: collections.Counter | 2026-10-30 | Equality compares per-key multiplicities; expanded C2 finding repetitions must retain each occurrence, not collapse to sets or star-suffixed strings | https://docs.python.org/3/library/collections.html#collections.Counter ; S44scout59/collections.html:478–481,600–609 ; source-receipts.json | Explanatory support only; actual audit uses sorted lists. Does not establish audit pass, historical-red repair, tool correctness, external capability, admission, certification, or score changes. |

## Limits and hygiene

`read xd://lsp` returned “No such tool”; no semantic server was available. Definition/caller locations above are source-text observations, not LSP semantic proof. No full C2 counter was run and no pass rate is claimed. Official documentation is a moving URL; saved hash binds this opening. Registry integration/admission remains with L1 and outside non-author closure. Production, frozen counters, sibling outputs, git index/jj state and shared bookkeeping were not modified. Scratch was created explicitly and removed before yielding; only seat artifacts and the explicitly named report trailer were written.
