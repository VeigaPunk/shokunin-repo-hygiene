# SwarmCritic44 — adversarial test of the SOURCES append (godspeed)

## Status
STATUS: PASS — every malformed-injection class the append must defend against is caught by the fleet census (`scripts/sources-census.sh validate`) with exit 1; the 0–3-space parser pattern is confirmed by the contract selftest fixture and by a boundary injection. One documented invisible surface (4+ space indent) is reported; it is Markdown code semantics, not a counter/predicate change.

## Evidence
Harness: scratch mirror `/var/tmp/souji-r28-SwarmCritic44/scratch` (`git init`; `git rev-parse --show-toplevel` → `/var/tmp/souji-r28-SwarmCritic44/scratch`), tar-copied from `souji-shokunin/` this run excluding `.git`, `.ufo`, `census/operator-sweep-*`, `__pycache__`. Validator: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` (E-class table at `:24-31`; parser contract `:40-42` "Maintained parser accepts 0–3 leading ASCII spaces … 4 or more spaces are indented code and ignored"; row gate `:615` `if (line !~ /^ {0,3}\|/) next`; used-by scan `:540-541` same 0–3 pattern). Run: `bash <validator> validate --today 2026-10-25 --file <case>/corpus/SOURCES.md`.

- Contract fixture: `TMPDIR=/var/tmp/souji-r28-SwarmCritic44/selftest-tmp bash <validator> selftest` → `selftest ok`, SELFTEST_RC=0; includes `indented-valid-{0,1,2,3}-counted/clean`, `indented-invalid-{0,1,2,3}-E06/E11`, `indented-outside-{0,1,2,3}-E12` all killed.
- Baseline (pristine mirror): rc=0; `file ok`; census `rows 135`, `status.mined 111`. Only pre-existing W04 warnings (35), which do not affect rc. Live lane file checked read-only: identical (rc=0, rows=135, mined=111), `git status --porcelain -- corpus/SOURCES.md` empty → append S212–S214 not yet landed; registry tail at S211 (line 156).

Injection → verdict (all rows use opened=2026-10-25; recheck=90d):

| id | injection (verbatim, appended inside `## Registry`) | verdict |
|---|---|---|
| (b) duplicate id | `| S999 | Dup one — https://inj-dup1.example/source | docs | B | b9 | §1 | dup one | queued | 2026-10-25 | 90d | — |` + same-row `S999` with `https://inj-dup2.example/source` | E03 `S999 duplicate id`, rc=1 |
| (c) bad kind/tier/status | `| S997 | Bad enum — https://inj-bad.example/x | bogus | Z | c9 | §1 | bad enum row | watch | 2026-10-25 | 90d | — |` | E05 kind=bogus, E06 tier=Z, E07 status=watch; rc=1 |
| (d) used-by → missing entry | `| S996 | Missing used-by — https://inj-usedby.example/x | docs | B | d9 | §1 | dangling used-by | mined | 2026-10-25 | 90d | corpus/knowledge/missing-entry-r28.md |` | E11 `S996 missing used-by corpus/knowledge/missing-entry-r28.md`, rc=1 |
| (e) literal `|` in a cell | `| S995 | Pipe cell — https://inj-pipe.example/x | docs | B | e9 | §1 | a | b teaches | queued | 2026-10-25 | 90d | — |` | E01 `S995 fields=12`, rc=1 |
| (f) E04 dup URL+scope (no supersedes) | `| S994 | Four one — https://inj-four.example/source | docs | B | f9 | §1 | four one | queued | 2026-10-25 | 90d | — |` + `| S993 | Four two — https://inj-four.example/source/ | docs | B | f9 | §1 | four two | queued | 2026-10-25 | 90d | — |` | E04 `S993 duplicate url inj-four.example/source within scope f9`, rc=1 |
| (a) indented row, 4+ spaces, new id | `    | S998 | Indented code row — https://inj-new.example/source | docs | B | a1 | §1 | indented new row | queued | 2026-10-25 | 90d | — |` (4 leading spaces) | NOT flagged; rc=0; census rows unchanged (135) — row ignored as code |
| (a2) indented row, 4+ spaces, duplicate of real S130 | `    ` + verbatim copy of the S130 row | NOT flagged; rc=0; rows unchanged (135) — collision invisible |
| (boundary) 1-space indented duplicate pair | ` | S993 | One-space one — …` + ` | S993 | One-space two — …` (1 leading space each) | E03 `S993 duplicate id`, rc=1 (both rows counted: rows=137) |

## Findings
1. **(b)(c)(d)(e)(f) all fail closed**: duplicate id → E03; bad kind/tier/status → E05/E06/E07; used-by missing → E11 (independent bash path, `usedby_findings`, same 0–3 table pattern); literal `|` cell → E01; duplicate URL+scope → E04. Each exits 1. The append S212–S214 must keep the 11-column shape, unique ids, enum values, existing used-by targets, and no unescaped `|` — the census enforces all of these.
2. **0–3-space parser pattern confirmed**: contract selftest (indented-valid/invalid/outside × 0..3 all pass) plus boundary injection: a 1-space indented duplicate pair is counted and caught (E03, rc=1).
3. **4+ space indentation is a silent bypass surface (documented)**: a row indented ≥4 spaces is neither counted nor validated — rc=0, no warning, even when it duplicates an existing id (case a2). This matches `scripts/sources-census.sh:40-42` and the selftest fixture, which embeds a 4-space indented junk row (`| S999 | … | watch | …`, tier Z) and expects it ignored. Consequence: the append must keep the three new rows at ≤3 leading spaces (column-zero, like the rest of the registry); a 4+ space-indented row will not be seen by the census at all and cannot be "caught" as an E03/E04 collision. This is not a counter/predicate defect — it is Markdown code semantics the validator contract pins; no amendment proposed.
4. W-code semantics confirmed: W04 warnings alone do not flip exit (baseline rc=0 with 35 W04); only E-class findings drive rc=1, matching the claim's "fail or warn" without a bogus failure.

## Attack log
No attack item assigned; adversarial results above are the delivered review. No counter, predicate, target or case set is challenged.

## Tooling
No install/upgrade performed (validator and gawk already present). Scratch removed after run.
