# SwarmMutationTester55 — mutation probe of the C1 instrument's K1 forward+parse logic

## Status

STATUS: PASS — 11/11 single-point K1/parsing mutants of `tools/souji-registry-agreement.py` were killed by a 12-case scratch battery; pristine baseline matched hand-derived expectations on all 12 cases; zero survivors; lane bytes untouched (sha256 identical before/after).

## Evidence

- Lane state (read-only): `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD` → `b8cb4b31ce80e2e3314b88e85d40ea9873180804` (prereg commit); `git rev-parse HEAD:tools/souji-registry-agreement.py` → blob `68c97278907b7b89d55b8d3fbc3f6bd8d4175d30`; `git status --porcelain=v1 -- tools/souji-registry-agreement.py` → empty.
- Instrument bytes: sha256 `51131fe74faa95a1488ad6957d90b272a22c52171c257d9b97bb27c305b09801` before probe == after probe == scratch pristine copy (restoration evidence: lane file never opened for write; mutants were separate scratch copies).
- Probe command: `python3 -B /var/tmp/souji-r29-MutateC1Forward/run_probe.py` (built battery, asserted pristine baseline, applied mutants, ran kill table). Python 3.14.8 host-present; no tools installed.
- Baseline (pristine tool vs hand-derived expected rc/k1/k2, all OK): C01 0/0/0, C02 1/1/0, C03 1/1/0, C04 0/0/0, C05 2/–/–, C06 0/0/0, C07 0/0/0, C08 1/1/0, C09 0/0/0, C10 0/0/0, C11 1/1/0, C12 0/0/0. A baseline failure would have been inconclusive; there was none.
- Example kill output (M01, case C02): expected `K1 used-by-missing S102 corpus/knowledge/absent.md` + `SUMMARY k1=1 k2=0 mismatches=1` rc=1; mutant printed `SUMMARY k1=0 k2=0 mismatches=0` rc=0.

## Battery (12 tiny git repos under /var/tmp/souji-r29-MutateC1Forward/battery/, each committed; `git rev-parse --show-toplevel` asserted == case dir before first commit)

| Case | Fixture gist | Expected (rc, k1, k2) |
|---|---|---|
| C01_clean | row S101, used-by = its citing entry | 0,0,0 |
| C02_usedby_missing | used-by path absent at rev | 1,1,0 |
| C03_usedby_no_cite | target contains only `S1033` (no boundary match) | 1,1,0 |
| C04_four_space_row | row indented 4 spaces, broken used-by | 0,0,0 (row invisible) |
| C05_malformed_row | 10-cell row (12 split items) | rc=2 could-not-evaluate |
| C06_semicolon_usedby | used-by `a; b`, both exist and cite | 0,0,0 |
| C07_blank_line_split | second table after blank line | 0,0,0 |
| C08_four_digit_id | rows S201+S2001 valid; entry cites S2099 (no row) | 1,1,0 |
| C09_spaced_dotted_usedby | `./a.md, b.md` (space after comma) | 0,0,0 |
| C10_source_past_heading | `source: S299` line after first heading | 0,0,0 |
| C11_dash_source_no_usedby | `- source: S212`, entry not in used-by | 1,1,0 |
| C12_emdash_placeholder | used-by cell is `—` | 0,0,0 |

All cases carry a valid corrected K2 fixture (stale list + `LOG.md` with `R29-CORRECTION LOG.md:2`) so k2=0 isolates K1 differences.

## Kill table

| Mutant | Site (tool line) | Killing case(s) | Expected → got |
|---|---|---|---|
| M01_drop_existence_check | :54 | C02 | rc1 k1=1 → rc0 k1=0 |
| M02_substring_id_match | :57 | C03 | rc1 k1=1 → rc0 k1=0 |
| M03_accept_4space_rows | :17 | C04 | rc0 → rc1 k1=1 |
| M04_drop_13col_check | :44 | C05 | rc2 → rc0 k1=0 |
| M05_comma_only_split | :46 | C06 | rc0 → rc1 k1=3 |
| M06_stop_at_first_blank | :41 | C07 | rc0 → rc1 k1=1 |
| M07_exactly_3digit_ids | :17,:67 | C08 | rc1 k1=1 → rc0 k1=0 |
| M08_norm_identity | :30 | C06, C09 | rc0 → rc1 k1=2 |
| M09_no_heading_break | :64 | C10 | rc0 → rc1 k1=1 |
| M10_source_line_start_only | :66 | C11 | rc1 k1=1 → rc0 k1=0 |
| M11_keep_emdash_as_path | :46 | C12 | rc0 → rc1 k1=1 |

Each mutant is one minimal in-place change to a scratch copy (verbatim old snippet asserted present exactly once before replacement); the lane tool was never edited.

## Findings

1. Baseline holds: the pristine instrument reproduced all 12 hand-derived outputs exactly (commands above). The detector is sound on this battery.
2. Kill coverage 11/11, zero survivors: every sampled parsing decision — row-indent bound (:17), blank-line scan stop (:41), 13-column guard (:44), used-by cell splitting incl. `;` and `—` filter (:46), path normalization (:30), existence check (:54), word-boundary id match (:57), heading-boundary of front matter (:64), `- `-prefixed source lines (:66), 3+-digit id shape (:17,:67) — is behavior-bearing and detected. No equivalent mutants, so no survivor gap analysis is due.
3. The malformed-row guard is load-bearing, not cosmetic: M04 (guard dropped, location `tools/souji-registry-agreement.py:44-45`, quote `raise RuntimeError('malformed registry row: ' + l[:60])`) silently accepted a 10-cell row and exited 0 (`mismatches=0`). This is the same failure shape the prereg kill rule names as "an always-zero emitter"; C05 shows the fixture battery would catch one at the K1 parse layer.
4. Real gap candidate (not a mutant survivor): the existence check emits before the cite check (location `tools/souji-registry-agreement.py:54-57`, quote `out.append(f'K1 used-by-missing {i} {p}')`), so one missing path and one uncited path on the same row are distinguishable — correct behavior, but M02 shows the cite check alone decides used-by agreement when files exist; a battery case mixing both defects per row (kept out to keep cases single-defect) would harden the fixture further.
5. Scope limits: probe covers single-point K1-forward/parse mutants only; K2 statement logic, `--list-rev`/`--stale-list` plumbing, and multi-mutant combinations were not sampled. [INFERENCE] The K2 half is likewise regex/TSV-driven and would likely yield to the same method, but no claim is made without runs.

## Attack log

- Item is an attack seat; probes executed as above (11 mutants × 12 cases + 12 baseline runs = 144 instrument executions).
- No surviving mutant and no gameability finding against the K1 forward/parse logic within this mutant set; no counter-predicate, target or case-set change proposed.

## Deliveries

- `.ufo/waves/round-29/w1/SwarmMutationTester55.md` (this report)
- Scratch `/var/tmp/souji-r29-MutateC1Forward/` removed after the run; nothing under it was lane material.
