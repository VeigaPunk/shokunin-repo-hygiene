STATUS: PARTIAL — requested gate fixes and checks are complete, but the 5efb tip still has one quarantine-pointer finding; its exemption row is outside this seat’s OWN ONLY file scope.

# Implementation

Changed only `tools/souji-landing-gate.py` in a detached clone at `5efb519f00075d958c3d1109ef6fcb24c487eb87`. The change:

- Unions all same-round H2 sections in `LOG.md`; an H2 for a different round ends the current section, while H3 headings do not.
- Splits citation components before stripping each component’s line suffix, including suffixes on brace-expanded members; normalizes interior `.`/`..` and source-relative `./` paths; skips Unicode ellipses and unbalanced brace tokens.
- Restricts fleet fallback to a one-level lane escape or `.ufo/waves/hyaku/`; checks the committed lane tree first. Exemptions are consumed before fleet classification.
- Adds `.ufo/quarantine/` to the pointer roots and scanner.
- Binds the measured-record exemption to both `tests/fixtures/r14-cache-frozen/record.json` and the exact placeholder value `0123456789abcdef0123456789abcdef01234567`. Other dangling values still produce `LG-FROZEN-MEASURED` and a stale-exemption finding.
- Counts `ptr_exempt` as unique used exemption rows (including an exact-placeholder record exemption). No CLI knobs were added.

Selftests now discriminate lane/fleet collisions, exemption-prefix widening, line suffixes on comma-list and brace members, same-round LOG corrections, interior dot segments, absent quarantine paths, and exact versus altered measured placeholders.

# Verification

- `python3 /var/tmp/souji-r18w2-GatePointers/lane/tools/souji-landing-gate.py --selftest` → `SELFTEST\tpass=61\tfail=0`.
- `python3 /var/tmp/souji-r18w2-GatePointers/lane/tests/fixtures/r16-landing-gate.py --tool /var/tmp/souji-r18w2-GatePointers/lane/tools/souji-landing-gate.py` → `SUMMARY\ttotal=15\tfailed=0`.
- `python3 /var/tmp/souji-r18w2-GatePointers/lane/tests/fixtures/r18-landing-pointers.py --tool /var/tmp/souji-r18w2-GatePointers/lane/tools/souji-landing-gate.py` → `SUMMARY\ttotal=11\tfailed=0`.
- Before count: `python3 /var/tmp/souji-r18w2-GatePointers/lane/tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 --round 18 --fleet-root /home/vgpnk/Projects/shokunin --json /var/tmp/souji-r18w2-GatePointers/before.json` → exit 2, `findings=11`, `checked_ptrs=320`, `ptr_exempt=0`, `ptr_fleet=3`, `checked_reports=0`; the existing carry gate reports `no .md reports under .ufo/waves/round-18/ at b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`, while the JSON retains all findings.
- Tip count: `python3 /var/tmp/souji-r18w2-GatePointers/lane/tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 5efb519f00075d958c3d1109ef6fcb24c487eb87 --round 18 --fleet-root /home/vgpnk/Projects/shokunin --json /var/tmp/souji-r18w2-GatePointers/tip.json` → exit 1, `findings=1`, `checked_ptrs=446`, `ptr_exempt=3`, `ptr_fleet=3`, `checked_reports=91`.
An intermediate selftest after restricting fleet fallback failed only the two old `pointer-fleet-only` cases, because they used a lane-relative `corpus/` path. Replaced that fixture with the authorized one-level escape and `.ufo/waves/hyaku/` forms; the final selftest and both final fixtures pass.

The previous committed old-grammar before record, `census/round-18/gate-pointers-before-b576341.json`, records 10 findings and `checked_ptrs=319`. The new before run is **11**, a disclosed +1 from scanning `.ufo/quarantine/`.

## Before findings (all 11)

| Finding | Path | Citation/detail |
|---|---|---|
| `LG-DANGLING-PTR` | `.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/dot-git-empty-stub` | `SKILL.md:110` |
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

The three fleet classifications in both before and tip JSON are `JjTrialSouji.md` and `JjAuditSouji.md` from `corpus/README.md:217`, plus the `.ufo/waves/hyaku/jj-w1/reports/` directory from `corpus/knowledge/jj-colocation-receipts.md:148`.

## Tip finding / blocker

The 5efb tip has one remaining `LG-DANGLING-PTR`: `.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/dot-git-empty-stub`, cited at `SKILL.md:110`. The committed `corpus/pointer-exemptions.tsv` has rows for the old `tests/vault/.../.git` token, the operator-owned census path, and the measured-record placeholder, but no row for this quarantine path. The tree contains no quarantine object at that path. Adding the reasoned quarantine-path row would change an unowned file, so I did not do it; this is the one remaining item for L1 to resolve if the desired tip count is zero.

# Replay and remaining scope

Read `census/round-17/gate-replays.py`: its five replay rounds are 15, 13, 14, 16, and 16, and the runner passes those values to `--round`; the round-18-only logic is therefore inactive for them. The replay runner itself was not executed. The round-16 and round-18 fixtures above both passed.

The explicitly requested grammar corrections are covered. Other W2 exploratory classes not named in this move (for example query/fragment URL tokens, generic non-round brace ranges, and HTML-comment citations) were not broadened here. No tools were installed or updated; no LSP interface was available.

Patch: `.ufo/waves/round-18/w1/GatePointersFix.patch`, generated against 5efb519 from only `tools/souji-landing-gate.py` in the private clone.
