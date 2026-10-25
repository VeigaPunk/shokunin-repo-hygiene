# ScoutSOURCESCensus — end-of-round SOURCES census (W2, round 25)

**STATUS: PASS**

Role: scout (leaf, read-only). No lane/fleet edits; only this report written.
Date: 2026-10-25. Scratch: `/var/tmp/souji-r25-ScoutSOURCESCensus/` (removed at finish).

## What was run

1. Frozen validate (round prompt §2b.2):
   `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
   - Exit: **0** (script header: exit 0 = clean or warnings; warnings never change status).
   - stderr: empty (0 lines).
   - stdout: 35 lines = 34× W04 warnings + 1× `souji<TAB>ok<TAB>/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md`.
2. Census mode (counts): `sources-census.sh census --root /home/vgpnk/Projects/shokunin souji` → exit 0.
3. Frozen manual census commands (CORPUS.md §SOURCES/ lines 135–147), run from the lane root
   `/home/vgpnk/Projects/shokunin/souji-shokunin` (used-by paths are lane-root-relative; the E11
   oracle in the script resolves `$dir/$path` against the lane dir, see sources-census.sh:566).
4. Tool consistency probe: python3 -B scan of `corpus/SOURCES.md` for the ID set, order, and
   mined used-by path existence.

## Findings

1. Rows: **127** (grep count = census mode `rows 127` = FLEET rows 127). IDs exactly S001–S127:
   all 127 present, no extras, no gaps; **S124–S127 consecutive** in registry order
   (index 123–126 = S124,S125,S126,S127). First/last: S001, S127.
2. Malformed rows (NF!=13): **0**.
3. Tiers: **A=120, B=5, C=2** (no invalid). Census mode agrees (tier.A 120, tier.B 5,
   tier.C 2, tier.invalid 0).
4. Statuses: **mined=103, queued=15, rejected=9** (no invalid). Census mode agrees
   (status.mined 103, status.queued 15, status.rejected 9, status.invalid 0).
5. Duplicate IDs: **none** (uniq -d empty).
6. Enum violations (kind/tier/status enums + tier-inflation A/community): **none**.
7. Used-by missing paths (mined rows): **0**. Frozen verbatim check prints nothing; script E11
   silent (no E11 line in validate output); python probe over all 112 mined used-by references:
   every path exists from the lane root (25 distinct artifacts: 24 corpus .md + tools/souji-size-census.py).
8. Warnings: **34× W04** (duplicate URL across scopes) — warning-only, exit code unaffected.
   Distinct rows: S035, S036, S038, S049, S057, S058, S059, S063, S065, S072, S073, S075,
   S076, S077, S086, S087, S088, S089, S090, S091, S092, S093, S094, S095, S096, S097, S098,
   S099, S106, S108, S123, S124, S125, S126 (34/34; one warning per row). No E01–E12 findings.

## Evidence

- validate stdout (35 lines) at `/var/tmp/souji-r25-ScoutSOURCESCensus/census.out`
  (sha256 f41ea1fec14133a04a21173caa1cfa18154a1345120816987aa9f34a3f7e70c4); stderr 0 lines.
- Frozen command outputs (run 2026-10-25, lane root):
  - rows: `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → 127
  - malformed: awk NF!=13 → 0
  - tiers: awk $5 histogram → `A=120 B=5 C=2`
  - statuses: awk $9 histogram → `mined=103 queued=15 rejected=9`
  - dup ids: awk $2 | sort | uniq -d → (empty)
  - enum: awk $4/$5/$9 → (empty)
  - used-by: awk $12 for mined | `[ -e ]` → (empty, 0 missing)
- ID/order probe: `have_all_S001_S127 True`, `extras []`, `missing []`, `S124_S127_consecutive True`.
- Census mode: exit 0; lane + FLEET lines identical (rows 127, tier A120/B5/C2, mined 103/
  queued 15/rejected 9, missing 0).

## Method note

Two earlier in-session manual probes mis-reported used-by paths as missing due to probe bugs
(wrong CWD; an undefined awk variable), not registry defects. Corrected probes (verbatim frozen
command from lane root; python ground-truth; script E11) all agree: **0 missing**. No
production writes were made; no tools installed.
