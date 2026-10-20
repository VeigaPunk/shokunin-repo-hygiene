STATUS: DONE — Completed L1's follow-up in the assigned gate and refreshed the scoped patch.

# Scope and behavior

Changed only `tools/souji-landing-gate.py` in `/var/tmp/souji-r18-GatePointers/lane`. Round-18+ pointer scanning now includes `SHONEN.md` and `corpus/lessons/round-N-verifier-spotcheck.md` when present. Leading `../` and `../../` tokens are normalized relative to their citing file before repository resolution; paths that still escape the lane are rejected as dangling. The existing scope, brace/range expansion, path-line stripping, placeholder skips, round-18 threshold, and `LOG.md` round-section boundary remain in place.

`corpus/pointer-exemptions.tsv` is parsed from the target `REV`. Exemptions apply to an unresolved in-scope pointer and to an unresolvable frozen record's `measured_commit`. Unused rows, including rows for resolved paths, produce `LG-DANGLING-PTR-EXEMPT-STALE`; malformed rows still return exit 2. JSON summary counters are `checked_ptrs` (expanded citation candidates), `ptr_exempt` (exempted citation occurrences), and `ptr_fleet` (fleet-only citation occurrences). The pointer scan runs before the carry check so a missing round report preserves exit 2 without suppressing pointer results.

# Verification

- `python3 /var/tmp/souji-r18-GatePointers/lane/tools/souji-landing-gate.py --selftest` → `SELFTEST\tpass=51\tfail=0`. New exact-ID cases cover relative normalization, repo escape rejection, SHONEN/optional spotcheck sources, valid/stale exemptions, frozen-record exemption, and JSON counters; all previous cases also passed.
- `python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r18-GatePointers/lane/tools/souji-landing-gate.py` → `SUMMARY\ttotal=15\tfailed=0`.
- `python3 /var/tmp/souji-r18-GatePointers/lane/tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 --round 18 --fleet-root /home/vgpnk/Projects/shokunin --json /var/tmp/souji-r18-GatePointers/before.json` → exit 2; summary `findings=12`, `checked_reg=27`, `checked_changed=0`, `checked_pins=13`, `checked_measured=3`, `checked_markers=0`, `status_lines=0`, `carry_heading=0`, `checked_reports=0`, `checked_ptrs=319`, `ptr_exempt=0`, `ptr_fleet=1`; error: `no .md reports under .ufo/waves/round-18/ at b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`.

Every finding in `before.json`:

| Finding | Path | Citation/detail |
|---|---|---|
| `LG-DANGLING-PTR` | `../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md` | `corpus/README.md:217` — escapes the lane, rejected |
| `LG-DANGLING-PTR` | `../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md` | `corpus/README.md:217` — escapes the lane, rejected |
| `LG-DANGLING-PTR` | `census/operator-sweep-20261019/` | `corpus/README.md:81` |
| `LG-DANGLING-PTR` | `census/round-17/gate-replays-ddb7347.json` | `SKILL.md:163` |
| `LG-DANGLING-PTR` | `census/round-17/gate-replays-ddb7347.json` | `SKILL.md:165` |
| `LG-DANGLING-PTR` | `census/round-17/jj-receipts-ddb7347.txt` | `corpus/README.md:216` |
| `LG-DANGLING-PTR` | `census/round-17/jj-receipts-ddb7347.txt` | `corpus/knowledge/jj-colocation-receipts.md:126` |
| `LG-DANGLING-PTR` | `census/round-17/jj-receipts-ddb7347.txt` | `corpus/knowledge/jj-colocation-receipts.md:148` |
| `LG-DANGLING-PTR` | `census/round-17/jj-receipts-ddb7347.txt` | `corpus/knowledge/jj-colocation-receipts.md:2` |
| `LG-DANGLING-PTR` | `census/round-17/jj-receipts-ddb7347.txt` | `corpus/knowledge/jj-colocation-receipts.md:44` |
| `LG-DANGLING-PTR` | `tests/vault/vadv54-run/p/p6repo/.git` | `SKILL.md:110` |
| `LG-FROZEN-MEASURED` | `tests/fixtures/r14-cache-frozen/expected.json` | `measured_commit '0123456789abcdef0123456789abcdef01234567' does not resolve to a commit` |

JSON separately classified `.ufo/waves/hyaku/jj-w1/reports/` as `fleet`, cited at `corpus/knowledge/jj-colocation-receipts.md:148`.

The two round-17 evidence paths are actual missing pointers; the operator-sweep path and nested `.git` stub are deliberate non-files and require committed exemptions at the landing revision. The two `../../.ufo/waves/` references in `corpus/README.md:217` escape the lane and are intentionally not treated as fleet paths under L1's rejection rule. `corpus/pointer-exemptions.tsv` is absent at the measured base, so `ptr_exempt=0`. The round-18 report directory is also absent at the base, explaining exit 2; all independent findings remain in JSON.

# Replay semantics and limitations

Read `census/round-17/gate-replays.py`: `REPLAYS` contains only rounds 15, 13, 14, 16, and 16 (lines 72–78), and `run_replay` passes those exact values to `--round` (lines 127–139). New pointer/exemption behavior is gated at round 18, so the old replay rounds do not activate it. The replay runner itself was not executed; this confirmation is source-based. The external round-16 fixture passed all 15 cases.

An initial selftest attempt earlier in the work reported `pass=42, fail=3` because the edited CLI argument block had lost the existing `--json` registration; restoring it produced the final 51/51 result. An earlier baseline attempt also short-circuited at the missing wave-report error; the evaluator now runs pointers first while preserving exit 2.

No LSP interface was available in this seat. Exact-file grep confirmed the changed helper callsites; this is not an inference from an empty LSP response. No tools were installed or updated.

Patch: `.ufo/waves/round-18/w1/GatePointers.patch` (generated from `git diff b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 -- tools/souji-landing-gate.py` in the assigned clone).
