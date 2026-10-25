# SwarmMutationTester51 — registry census mutation test (round 28 w1)

## Status
STATUS: PASS — all four mutants behave as specified against `sources-census.sh validate --file` on the isolated mirror; baseline clean (rc=0, rows=135); exact bytes restored and hash-verified.

## Evidence
Detector (bounded, same command on pristine/mutated/restored bytes):
`bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --today 2026-10-25 --file <mirror>/corpus/SOURCES.md` (plus `census --file` for row counts). Mirror at `/var/tmp/souji-r28-SwarmMutationTester51/mirror/` = copy of lane `corpus/` + `tools/` (E11 resolves used-by paths against the mirror root).

- Pristine baseline: rc=0; `file ok`; 35 W04 warnings (cross-scope URL repeats, warnings only); census `rows 135` (tier A 128 / B 5 / C 2; status mined 111 / queued 15 / rejected 9).
- Mutant 1 — malformed row (10 cells, NF=12≠13, id S900): rc=1; `file E01 S900 fields=10`. KILLED.
- Mutant 2 — tier enum violation (tier=D, id S901): rc=1; `file E06 S901 tier=D`. KILLED.
- Mutant 3 — within-scope duplicate URL (S902 copies S211 URL+scope verbatim): rc=1; `file E04 S902 duplicate url raw.githubusercontent.com/GNOME/glib/2.84.0/glib/gfileutils.c within scope GLib file-content helper temporary-file write and rename publication, distinct from trash info-record reservation`. KILLED.
- Mutant 4 — 4-space-indented valid row (S903): validate rc=0, `file ok`; census `rows 135` (unchanged). SURVIVED as expected (row ignored; no defect).
- Restoration: `cmp` mirror-repo == pristine; sha256 equal across mirror, pristine, and lane file: `7d05be308de08fb67b40b27b5757fdbce23e9fd0cc418d88e86292d786c39f8d` (lane file untouched throughout).

Source claims (bytes opened this run):
- `scripts/sources-census.sh:44-46` — "Maintained parser accepts 0–3 leading ASCII spaces before Markdown rows/headings; 4 or more spaces are indented code and ignored."
- `scripts/sources-census.sh:635-638` — "if (NF!=13) { printf "%s\tE01\t%s fields=%d\n",lane,id,NF-2"
- `scripts/sources-census.sh:657` — "if (tier !~ /^[ABC]$/) printf "%s\tE06\t%s tier=%s\n",lane,id,tier"
- `scripts/sources-census.sh:646-649` — "if (u!="" && (scope_key in url_scopes) && status!="rejected" && url_scope_nonrejected[scope_key] && teaches !~ /supersedes S[0-9]{3}/)" → E04.

## Findings
1. E01 malformed-row check (NF≠13) fires and forces exit 1 — mutant M1 killed.
2. E06 tier-enum check fires for tier=D and forces exit 1 — mutant M2 killed.
3. E04 duplicate-URL-within-scope check fires (non-rejected pair, no supersedes teach) and forces exit 1 — mutant M3 killed; the cross-scope twin (S210 vs S152, same URL different scope) correctly stays W04-only.
4. Indentation boundary: 4+ leading spaces are treated as code block (not a table row) — M4 produces zero findings and row count 135 unchanged; 0–3 leading spaces are accepted (selftest + registry rows).
5. No behavior-bearing defect found: all injected anomalies detected or correctly ignored; no surviving unexpected mutant.

## Attack log
None — item is mutation testing; no counter/predicate/target challenged.
