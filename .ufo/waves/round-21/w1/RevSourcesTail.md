# Review — `corpus/SOURCES.md` S089–S099

## Finding (minor): `used-by` omits current helper citations

The `SOURCES.md` rows S089, S092, S093 and S099 list only `corpus/lessons/round-20.md` in `used-by`, but the current `tools/souji-rev-pin.py` module docstring explicitly cites those four source IDs at lines 14–21. The round-20 lesson's line 141 instead says the helper cites `S089/S091–S093`; that no longer matches the checked-in docstring, which cites S089, S099, S092 and S093, not S091. This is a registry/lesson accounting mismatch, not a defect in the helper's documented behavior.

Proposed exact changes (append the existing helper path to `used-by`):

- S089: `corpus/lessons/round-20.md` → `corpus/lessons/round-20.md, tools/souji-rev-pin.py`
- S092: `corpus/lessons/round-20.md` → `corpus/lessons/round-20.md, tools/souji-rev-pin.py`
- S093: `corpus/lessons/round-20.md` → `corpus/lessons/round-20.md, tools/souji-rev-pin.py`
- S099: `corpus/lessons/round-20.md` → `corpus/lessons/round-20.md, tools/souji-rev-pin.py`

Related lesson correction: `current helper cites S089/S091–S093` → `current helper cites S089, S092, S093 and S099`. Leave S091's `used-by` unchanged: no S091 citation appears in the checked-in helper docstring.

## Other requested checks

- **Status vs used-by:** All eleven rows have a non-dash `used-by`; the recorded census reports W04 warnings only, not W02/W03. S090 and S097 are properly `rejected` rows with lesson use and substantive rejection/flip teaching; the other rows are `mined`. Do not flip S090 to mined: S097 explicitly supersedes its old, non-reversing flip language while retaining the current reject decision. S091/S099, S094/S098 and S095/S096 similarly retain earlier mined rows as historical/source-scope corrections; the newer rows explicitly qualify or supersede teaching rather than invalidate the older source record.
- **Recheck/staleness:** All S089–S099 rows use the allowed symbolic `on-release` cadence and were opened/reopened on 2026-10-21. The recorded validator contract treats symbolic cadence as reported, not overdue. Their anchors identify current 2.56.0 Git documentation (or explicitly unchanged through 2.56.0), Coreutils 9.12 material, or Linux man-pages 6.19. No stale row or cadence change is supported by the reviewed record.
- **Duplicate URLs:** `source-census-start.txt` records W04 for every row in S089–S099; it states `souji\tok\t/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md` and `exit=0`. These are warning-only cross-scope duplicates, not same-URL/same-scope conflicts: S089 shares Git's URL with S036/S049; S090/S097 share filter-branch; S091/S099 share rev-parse; S092 shares for-each-ref with S080; S093 shares git-diff with S081; S094/S098 share timeout with S038 and each other; S095/S096 share proc_pid_fd with S083/S086. The newer rows narrow or correct teaching and state the supersession; no URL or status flip is warranted.

## Evidence and verification gaps

- Read `corpus/SOURCES.md` lines 99–119, `corpus/lessons/round-20.md` lines 131–147 and 329–351, `tools/souji-rev-pin.py` lines 10–23, `corpus/knowledge/process-residue-observations.md` lines 145–159, the round-21 source-census record, and `scripts/sources-census.sh` lines 1–38.
- Executed `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff 544c8358039a07e8b45e6db72312da5c8d965275 -- /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md`; it produced no output. No build, test, lint, or target-code execution was performed.
- The `xd://lsp` probe returned “No such tool”; no LSP status, references, definition, or diagnostics were available. The cited helper evidence above is the literal checked-in docstring, not a semantic reference search. No LSP-dependent caller/definition claim is made.

## Residual risk

The only actionable issue found is completeness of the four `used-by` lists and the associated lesson wording. No recheck, status, duplicate-URL, or stale-row correction is recommended.