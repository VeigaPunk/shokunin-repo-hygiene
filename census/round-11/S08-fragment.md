# S08 — census fix implementor (round 11)

Seat: S08 · Round: 11 · Role: census-contract fix implementor
Candidate: `tools/cand-census-08.sh`
Candidate sha256 (frozen before all runs): `7eb1b8d93d0b50c8a004aff50ed3d5ac3ddfa365ec596124f9ce6a65a221ba70`
Baseline (r10-merge bytes, `tools/souji-census.sh`): `11bf9cdf8d4f75415b18e046aef0e96215b983f0d5b3ff7842301ff6ac65d381`
Fixtures: all under `mktemp -d -p /var/tmp` (host /tmp quota respected). Lane files written: only `tools/cand-census-08.sh` and this fragment.

## Finding (root cause of all 3 r10 unsafe outcomes)

`cert-16.json` unsafe register — `final22/empty-census-compare`, `s16-fresh/J14`, `s16-fresh/V07` — are one defect class in `souji-census.sh` `load_census()`: the blank-line skip `[ -n "$line" ] || continue` ran **before** the line-1 header check. Consequences:

- **J14 / final22 (0-byte prior)**: `read` returns 1 immediately with an empty line; the `while` loop body never executes, so the header check never runs. `load_census` returns cleanly, `before` stays empty, and `emit_compare` treats the fleet as "added" rows? No — with an empty `--root` fleet the `after` map is also empty, so the diff is header-only and the tool **exits 0** ("no diff"). An empty baseline silently reads as unchanged.
- **V07 (newline-only prior)**: line 1 is blank, gets skipped by the blank-line guard before the header check, loop ends; same silent rc=0.

Contract (tool header + rubric K10 `comparison`/O08 `malformed`): `--compare` requires a previous census with the 7-column header; malformed input is a hard error (exit 2) and "a compare against a corrupt previous census must not look like 'no diff'".

## Fix (minimal, in `load_census` only)

`tools/cand-census-08.sh` = r10-merge bytes + two guards:

1. Header check moved **before** the blank-line skip: line 1 must equal `$HEADER` even when blank (blank line 1 → `usage_err "compare file header mismatch (want 7 census columns)"`, exit 2).
2. Post-loop guard: if the file yielded fewer than 1 line (`n<1`, the 0-byte case where the loop body never runs), the same header-mismatch error fires.

Blank-line skipping for **data** rows (lines ≥2) is preserved, so a prior census with a trailing blank line still compares cleanly. No other function touched; diff vs baseline is 14 lines inside `load_census` + comment.

## Selftest additions (3 new checks, census selftest 32 → 35)

- `empty compare baseline exits 2` (0-byte prior)
- `blank-only compare baseline exits 2` (newline-only prior, V07 shape)
- `header-only baseline vs empty fleet: exit 0, header only` (positive control: a legitimate header-only prior against an empty fleet must still be "no diff", rc=0 — the fix must not over-refuse)

## Verification (all against frozen bytes, /var/tmp fixtures)

| Check | Result |
|---|---|
| `bash -n cand-census-08.sh` | exit 0 |
| `--selftest` (built-in) | `selftest: 35 checks, 0 failed`, exit 0 |
| J14 fresh repro: 0-byte prior vs empty root | **rc=2**, banner `compare file header mismatch (want 7 census columns)` |
| V07 fresh repro: newline-only prior vs empty root | **rc=2**, same banner |
| Positive control: header-only prior vs empty fleet | rc=0, diff header only |
| Positive control: prior == own census vs live fleet | rc=0 (unchanged from baseline) |
| Mutation control: prior census vs mutated fleet | rc=3 with field rows (unchanged from baseline) |
| final22 recipe replay (census line redirected to candidate) | census rc=2, refusal banner; recipe exits 2 under `set -e` — no silent rc=0 |

## Full re-certification run (S16 harness, `--map census=tools/cand-census-08.sh`)

Command: `python3 tools/cand-s16-cert.py --map census=tools/cand-census-08.sh --label s08-census-fix --out /var/tmp/s08-cert-run.json` (28.5 s, 15 corpora)

- **certification_verdict: CERTIFIED** · certification_ready: **true**
- unsafe_outcomes: **0** (r10 was 3) · errors: 0 · test_failures: 0
- conservative_refusals: 124 (r10: 121; +3 = J14/V07/final22 now refusing)
- Built-in selftests: verify 40/0, vault 51/0, quarantine 91/0, **census 35/0**
- s15 merged selftest: 88 pass / 0 fail / 0 skip
- final22: 11 cases, 0 unsafe (empty-census-compare now census_ok)
- s16-fresh: J14 q.rc=2 CENSUS-EMPTY-COMPARE, V07 q.rc=2 CENSUS-NEAR-EMPTY-COMPARE — both registered as refusals, not unsafe
- Peer corpora unchanged-clean vs r10: s10 40 cases 0 unsafe 0 harness errors, s09 40 artifacts false_safe=0, s12 5 refused, s21 canonical stable, s23 patched
- Full JSON: `census/round-11/S08-cert-run.json` (copy of /var/tmp/s08-cert-run.json)

## Reproduction

```bash
# freeze
cp tools/cand-census-08.sh /var/tmp/ && sha256sum /var/tmp/cand-census-08.sh
# 7eb1b8d93d0b50c8a004aff50ed3d5ac3ddfa365ec596124f9ce6a65a221ba70
B=$(mktemp -d -p /var/tmp); mkdir -p "$B/empty-root"; : > "$B/empty.tsv"
bash /var/tmp/cand-census-08.sh --root "$B/empty-root" --compare "$B/empty.tsv"; echo "rc=$?"   # want 2
printf '\n' > "$B/near.tsv"
bash /var/tmp/cand-census-08.sh --root "$B/empty-root" --compare "$B/near.tsv"; echo "rc=$?"    # want 2
bash /var/tmp/cand-census-08.sh --selftest                                                     # want 35 checks, 0 failed
python3 tools/cand-s16-cert.py --map census=/var/tmp/cand-census-08.sh --label s08-repro \
  --out /var/tmp/s08-repro.json                                                # want CERTIFIED, 0 unsafe
```

## Verdicts

- `census-empty-compare class closed`: **MET** — all 3 r10 unsafe outcomes now refuse (exit 2); cert harness CERTIFIED with 0 unsafe.
- `no regression`: **MET** — all peer corpora and selftests match or exceed r10 results; positive controls (header-only baseline, self-compare, mutation compare) unchanged.
- `no over-refusal`: **MET** — header-only baseline vs empty fleet still rc=0.

No unsafe outcomes, no unauthorized deletes, no mutations outside assigned files. Nothing left `to-verify`.


## Addendum — cross-seat conflict observed (not acted on)

While writing evidence, seat S29's fix landed concurrently in the shared lane: `tools/souji-census.sh` was overwritten (new sha `462dabd281e417c80266ba4d3ffd2cd8ebca0aa84147e1c45c9832ee638b52ca`, "header = first non-blank line" semantics) and `census/round-10/cert-16.json` was re-run in place (now labeled `s29-S29-final`). I did not touch either file — both are outside my assigned writes.

Measured state of the S29-installed bytes (read-only probes, /var/tmp fixtures):

- Their fix closes the r10 class: J14/V07/final22 repros now exit 2; cert harness reports 0 unsafe.
- But their own 2 new selftest checks fail: `selftest: 36 checks, 2 failed` — `blank-before-header compare baseline exit=3 want 2` and `blank-after-header: exit=3 want 0`. Root cause: with a non-empty fleet, a blank line 1 is skipped, the header matches on line 2, and the fleet rows then differ from the header-only baseline → `emit_compare` rc=3; their selftest asserts rc=2 (blank-before) and rc=0 (blank-after, which also fails because the fleet rows differ). Their `saw_header` guard only fires for fully empty files.
- My candidate's semantics differ deliberately: header must be on **line 1 exactly** (blank line 1 → exit 2; blank lines after the header are skipped). That makes `blank-before-header` exit 2 with any fleet, and `blank-after-header` exit 0 only when the fleet is unchanged — both of my checks pass (35/0), and the cert harness CERTIFIES the pair.

Parent integration decision (S08 recommendation): pick ONE census fix for r11. `cand-census-08.sh` is the certified, self-consistent option (35/0 selftest, CERTIFIED harness run, 0 unsafe, positive controls intact). If S29's bytes are preferred for their looser "first non-blank line" contract, their selftest expectations must be corrected first — as installed they fail their own built-in selftest, which breaks the certification rule "all built-in selftests exit 0". Do not install both.
