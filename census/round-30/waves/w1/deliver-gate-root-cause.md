# C2 base failures mapped to code (read-only)

Gate: /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py (blob tag #B8DD at read; `git diff 9420341d9a81 HEAD -- tools/souji-landing-gate.py` printed no change, so line numbers hold at base and lane HEAD df6afe81).
Base rev: 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b.

## 1. Command and output (run in /fast/scratch/hyaku/souji-r30/GateRootCause/, TMPDIR there)

`python3 -B .../tools/souji-landing-gate.py --root .../souji-shokunin --rev 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --round 29 --fleet-root /home/vgpnk/Projects/shokunin` → rc=2

```
LG-DANGLING-PTR	.ufo/waves/round-29/	corpus/lessons/round-29-verifier-spotcheck.md:132 cites path absent at 9420341d9a81
LG-DANGLING-PTR	census/round-	corpus/QUALITY.md:150 cites path absent at 9420341d9a81
LG-DANGLING-PTR	corpus/lessons/round-	corpus/QUALITY.md:150 cites path absent at 9420341d9a81
SUMMARY	findings=3	checked_reg=58	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=0
COULD-NOT-EVALUATE	no .md reports under .ufo/waves/round-29/ at 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b
```
(COULD-NOT-EVALUATE goes to stderr; a `--json` run adds `checked_ptrs=1012 ptr_exempt=4 ptr_fleet=3`.)

## 2. Line-to-code map

| output line | producer | lines |
|---|---|---|
| all 3 `LG-DANGLING-PTR` | `check_pointers()` appends `("LG-DANGLING-PTR", path, "%s:%d cites path absent at %s")` | 985-991 (def 905-992) |
| the existence test that lets them through | `_path_exists_in_tree(path, tree_paths)` = `path.rstrip("/") in tree_paths`; `tree_paths` = every tracked blob path plus all parent dirs | 957-958; helper 872-873; set build 909-914 |
| the fleet/exemption escapes tried first (neither fits) | exemptions 959-961; fleet only for `../x` (one level) or `.ufo/waves/hyaku/` prefix | 959-984 (fleet_path rule 964-968) |
| `.ufo/waves/round-29/` | token from `.../round-29-verifier-spotcheck.md` line 132 ("no reports under the gitignored `.ufo/waves/round-29/`"); passes tokenizer, `.ufo/waves/round-29` is not in the base tree (only round-13..26 are tracked under `.ufo/waves/`: 35/35/70/148/131/206/72/122/109/522/84/102/162/1216 paths; round-29 is captured at `census/round-29/waves/`, 132 paths, 86 `.md`) | tokenizer 823-862; source list 924-925 |
| `COULD-NOT-EVALUATE` | `check_carry()` raises `EvalError("no .md reports under %s at %s" % (prefix, rev))` when no tracked path starts with `.ufo/waves/round-29/` and ends `.md` | prefix 469, reports 470-472, raise 473-474 |
| why it surfaces as exit 2 with findings kept | `evaluate()` catches that EvalError for `round_no >= 18`, stores `result["error"]`, zeroes marker counts (so `checked_reports=0`, `status_lines=0`) and `exit = 2 if error` | 1117-1132, 1138 |
| stderr print | `emit()` | 1166-1167 |

## 3. The tokenizer that cut `census/round-` and `corpus/lessons/round-` out of QUALITY.md:150

QUALITY.md:150 (base; same bytes at HEAD) is row Q60. The two tokens are inside a Python one-liner in its `check` cell (column offsets 967 and 1024 of the 2484-char line):

> `pre=g("census/round-"+rd+"/records/preregistration.txt");les=g("corpus/lessons/round-"+rd+".md")`

Cutter: `POINTER_PATH_RE` (lines 141-146):

```
(?<![A-Za-z0-9_./<>*])(?:(?:\.\./)+|\./)?(?:census|tests|tools|corpus|\.ufo/waves|\.ufo/quarantine)/[^\s`"'()\[\]]+
```
The tail class `[^\s`"'()\[\]]+` stops at the `"` that closes the Python string literal, so the match is the string-literal fragment `census/round-` (resp. `corpus/lessons/round-`). Then `_pointer_paths()` (823-862) filters: skip on `…`, any of `<>*`, `ROUND_PLACEHOLDER_RE` (`round-N`, line 148), unbalanced braces (826-833). `census/round-` has none of these, so it passes; `_trim_pointer_token` (795-798) strips only trailing `.,;:!?` and a `:N` suffix; `_normalize_pointer_path` (801-808) is a no-op; the `normalized.startswith(POINTER_ROOTS)` test (853-857) keeps it (roots at 136-139); `_expand_round_ranges` (777-792, `ROUND_RANGE_RE` line 147) needs `round-N..M`, no match. Yielded verbatim and reported.
Other same-line tokens are real paths that resolve (`corpus/lessons/round-29.md`, `corpus/lessons/round-28-verifier-spotcheck.md` after `:49` trim, `census/round-28/records/preregistration.txt;` after `;` trim, `census/round-29/waves/w1/deliver-q60-q62-red-before.tsv`).

Template forms probed with the committed module (`_pointer_paths(text, "SKILL.md")`):
- `` `census/round-<N>/x` `` → `[]` (skipped by the `<>*` char test, 829) — not flagged today.
- `` `census/round-%s/waves/x.md` `` → `['census/round-%s/waves/x.md']` — flagged (only `round-N` is a placeholder).
- `census/round-{N}/x` and `census/round-$R/x` → yielded as-is — flagged.
- `g("census/round-"+rd+"/...")` → `['census/round-']` — flagged.

## 4. `checked_reg=58` is NOT the pointer file set

`checked_reg` is incremented at line 1046 per SKILL.md-cited script that parses: `CITED_PATH_RE` (85-87) `(?:tools|tests/fixtures|census/round-\d+)/[A-Za-z0-9_.-]+\.(?:sh|py)`, applied via `sorted(set(CITED_PATH_RE.findall(skill)))` to SKILL.md only (1037-1049). Recomputed at base: 58 distinct paths = 29 `tests/fixtures/…`, 15 `tools/…`, 14 `census/round-N/…`. They are parse-checked (`parse_script`), not pointer-scanned.

The pointer scan (`checked_ptrs=1012`) reads, from the committed tree at REV (`blob_by_oid`, 937), lines 916-948:
- `SKILL.md`, `SHONEN.md`, `SCORECARD.md`, `PROVINCE.md`, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/lessons/round-29.md`, `corpus/lessons/round-29-verifier-spotcheck.md` (each only if present in tree; all 8 present at base);
- every direct child `corpus/knowledge/*.md` (`count("/") == 2`, 928-933): 22 files at base;
- `LOG.md` H2 sections numbered 29 and their continuation (943-948, `_round_log_lines` 749-761).
Not scanned: tools/, census/, tests/, other lessons, SOURCES.md, pointer-exemptions.tsv.
Exemptions (`corpus/pointer-exemptions.tsv`, 4 rows at base) suppress exact paths only (959-961); none covers the three findings.

## 5. Other places that assume `.ufo/waves/round-N/`

Code (non-selftest):
1. `check_carry` 469-474 — the report set and the exit-2 trigger (the only functional dependency).
2. `POINTER_ROOTS` 136-139 and `POINTER_PATH_RE` 144 — accept `.ufo/waves/…` as a citation root; existence is decided against the git tree only (957), so a capture-mapped pointer can never resolve.
3. `check_pointers` 964-968 — `.ufo/waves/hyaku/` is the sole waves path with a non-tree fallback (fleet root).
4. Docstring/comments only: 13, 33-34, 114.
`evaluate()` 1117-1132 fixes behaviour for the missing-report case; `main()` 2278-2322 has no round/waves logic. Pins (`ROOT_PREFIXES` 131, `EXPECTED_JSON_RE` 133), `carries()`, `_round_heading_number` and `check_frozen_pins` do not reference waves.
Report paths flow into findings as `report_path` (526, 528, 536); carry matching compares quoted STATUS text, not the path (510, 516), so a capture-path report would not change carry matching.

Selftest (lines 1250-2270; 65 cases, `SELFTEST pass=65 fail=0` on the committed tool at HEAD in this run): every `.ufo/waves/round-N/` use is a synthetic fixture file (e.g. 1277/1279/1281 base files; 2009-2175 seat reports; 1399 deletion). No fixture contains a `census/round-N/waves/` path (grep of lines 1250-2326: none).

Would a capture fallback change a selftest case? [INFERENCE, not run against a patched gate]
- A fallback that applies only when `.ufo/waves/round-N/` has no tracked `.md` AND `census/round-N/waves/` has one leaves every selftest case unchanged, because no fixture holds `census/round-N/waves/`.
- Cases that assert the both-absent path and must keep the exact substring `no .md reports under`: `pointer-without-wave-reports` (1396-1407, exit 2, `expect_err="no .md reports under"`, `expect_n=1`) and `no-wave-dir-exit2` (2174-2178). The error text must stay when both locations are empty.
- Cases that would change if the fallback were unconditional or preferred the capture: none exist in the selftest, but `expect_counts` cases (1759-1762 `checked_reports=1`, 1797-1800) rely on exactly the `.ufo/waves/round-N/` count; a union of both locations would still give 1 there only because the fixture has no capture.
- Pointer resolution: mapping `.ufo/waves/round-N/X` → `census/round-N/waves/X` before 957 touches fixtures only where a cited `.ufo/waves/round-…` path is absent: `.ufo/quarantine/…` is a different root (1538-1556, unaffected); `.ufo/waves/hyaku/` fleet cases (1612-1658) must keep resolving via fleet root (the mapping must not rewrite `hyaku`, which has no `round-N`). `expect_counts={"checked_ptrs": 6, "ptr_exempt": 1}` (1706) would move only if the mapping changed which tokens are yielded; it would not if applied at the existence test instead of in `_pointer_paths`.
- Tokenizer fixes for `round-%s` / `round-"+rd+` change `checked_ptrs`; the only pinned `checked_ptrs` is 1706 (6) and its fixture contains no template token (not run against a patched gate).

Capture layout facts for the mapping (base tree): `census/round-29/waves/` has `make-spec.py`, `manifest.sha256`, `summary.tsv` at depth 1, and 113 paths under `w1/` (4 under `w1/assimilation/`, 6 under `w1/sources/`); reports sit at `census/round-29/waves/w1/*.md` — i.e. `.ufo/waves/round-29/w1/X.md` ↔ `census/round-29/waves/w1/X.md`, direct 1:1 under the `waves/` root. Tracked `.ufo/waves/round-13..26` also exist at base, so rounds ≤26 would never take the fallback.
