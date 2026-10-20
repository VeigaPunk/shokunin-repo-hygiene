STATUS: BLOCKED — Nine single mutants restored; requested r15 --census detector rejects its CLI, and unchanged behavioral fixtures need a scratch-scope exception.
# MutateCensusD2 — C1-D2 mutation probe
## Scope, axes, and source
Axes: operability (per-repo degradation and intact neighbours); safety (later whole-run refusals remain reachable); diagnostic completeness; detector sensitivity; exact byte restoration. No production changes, git writes, jj execution, installations, or real-repository census were performed.
Committed source: `ddb73474433977ff54b015ac3e77669ff2537353:tools/souji-census.sh`; `79699` bytes; SHA-256 `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59`. Source retrieved by `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show ddb7347:tools/souji-census.sh`.
## Blocking prerequisites and smallest fixes
1. `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py:1440-1443` at ddb7347 accepts `--tool`, not `--census`. Every requested pristine/mutated/restored invocation exits 2 before any CASE. Smallest task correction: authorize the existing `--tool` operand; no source fix is needed.
2. `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-census-hygiene.py:1133` and `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py:1481` at ddb7347 pass explicit `dir="/var/tmp"` to `tempfile.mkdtemp`, ignoring a seat TMPDIR. Running either unchanged behavioral fixture would create detector-owned private temporary trees outside `/var/tmp/souji-r17-MutateCensusD2/`. Parent was asked to authorize these named self-cleaning fixture trees; no such behavioral run has been executed yet. No detector has been rewritten or confined with an unapproved wrapper.
## Single-mutant definitions
| ID | ddb7347 source line | Single behavioral defect | Expected r17 detectors (not run yet) | Mutated SHA-256 |
|---|---:|---|---|---|
| M01 | tools/souji-census.sh:562 | hardlink-loop-early-return | R17-13 | `214b314b6e14c769074007c1dec4197aed96415b20263afaa69784da3ee7344f` |
| M02 | tools/souji-census.sh:560 | hardlink-attributes-whole-run-refusal | R17-07, R17-14, R17-15, R17-20 | `8b881da10ccc9801747937b0d228b06e6f2fd9aadccd6794ad52085938015e9e` |
| M03 | tools/souji-census.sh:967 | skip-gitfile-commondir-file-guard | R17-15, R17-18, R17-26 | `e1aeafbd0960f790bcb4274b65910b44f18d50aa99faeedfdf544a2ffd399606` |
| M04 | tools/souji-census.sh:549 | stat-without-dereference | R17-22 | `cc833f65f853430dab9eece1c8a6c68430c89f7f8b6f06a61d2c5bbe3edadfea` |
| M05 | tools/souji-census.sh:653 | mask-config-diagnostic-with-metadata | R17-20 | `2068383250160eaa3c6064676d5c0b1f26e5a58f0c322a1b72b7c46357cbdbd6` |
| M06 | tools/souji-census.sh:558 | hardlink-threshold-greater-than-two | R17-07, R17-10, R17-13, R17-14, R17-15, R17-18 | `b4f87df66cdf6d7c768ccf56bcaf66768da4d393232ac123968bd384daee2432` |
| M07 | tools/souji-census.sh:553 | directory-attributes-soft-degrade | R17-21 | `aaf4e95c2cf01d8721966e7f6d740dbe1cd62d35ba9bcbe982167013e63c6079` |
| M08 | tools/souji-census.sh:644 | metadata-path-not-recorded | R17-07, R17-08, R17-09, R17-14, R17-15, R17-20, R17-24, R17-26 | `152064e02ab5423186a63d03edf6ada7c96d33515e8ada68785963f3a4caebf7` |
| M09 | tools/souji-census.sh:907 | surface-early-return-after-files-soft | R17-12, R17-20 | `c9a62c4d402176cd8f218e9b24850ecc08eb4bcba5c62818c9238e575c197f3c` |

## Observed requested-detector triads
All nine requested r15 triads are **INCONCLUSIVE**, not kills or survivors: baseline itself fails with an unsupported option; no CASE or SUMMARY is emitted in any phase. The detector output and commands below are actual captured subprocess results.

### M01

requested-pristine: SHA-256 `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` before and `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M01-hardlink-loop-early-return.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M01-hardlink-loop-early-return.sh
```

requested-mutated: SHA-256 `214b314b6e14c769074007c1dec4197aed96415b20263afaa69784da3ee7344f` before and `214b314b6e14c769074007c1dec4197aed96415b20263afaa69784da3ee7344f` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M01-hardlink-loop-early-return.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M01-hardlink-loop-early-return.sh
```

requested-restored: SHA-256 `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` before and `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M01-hardlink-loop-early-return.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M01-hardlink-loop-early-return.sh
```

### M02

requested-pristine: SHA-256 `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` before and `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M02-hardlink-attributes-whole-run-refusal.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M02-hardlink-attributes-whole-run-refusal.sh
```

requested-mutated: SHA-256 `8b881da10ccc9801747937b0d228b06e6f2fd9aadccd6794ad52085938015e9e` before and `8b881da10ccc9801747937b0d228b06e6f2fd9aadccd6794ad52085938015e9e` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M02-hardlink-attributes-whole-run-refusal.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M02-hardlink-attributes-whole-run-refusal.sh
```

requested-restored: SHA-256 `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` before and `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M02-hardlink-attributes-whole-run-refusal.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M02-hardlink-attributes-whole-run-refusal.sh
```

### M03

requested-pristine: SHA-256 `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` before and `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M03-skip-gitfile-commondir-file-guard.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M03-skip-gitfile-commondir-file-guard.sh
```

requested-mutated: SHA-256 `e1aeafbd0960f790bcb4274b65910b44f18d50aa99faeedfdf544a2ffd399606` before and `e1aeafbd0960f790bcb4274b65910b44f18d50aa99faeedfdf544a2ffd399606` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M03-skip-gitfile-commondir-file-guard.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M03-skip-gitfile-commondir-file-guard.sh
```

requested-restored: SHA-256 `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` before and `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M03-skip-gitfile-commondir-file-guard.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M03-skip-gitfile-commondir-file-guard.sh
```

### M04

requested-pristine: SHA-256 `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` before and `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M04-stat-without-dereference.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M04-stat-without-dereference.sh
```

requested-mutated: SHA-256 `cc833f65f853430dab9eece1c8a6c68430c89f7f8b6f06a61d2c5bbe3edadfea` before and `cc833f65f853430dab9eece1c8a6c68430c89f7f8b6f06a61d2c5bbe3edadfea` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M04-stat-without-dereference.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M04-stat-without-dereference.sh
```

requested-restored: SHA-256 `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` before and `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M04-stat-without-dereference.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M04-stat-without-dereference.sh
```

### M05

requested-pristine: SHA-256 `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` before and `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M05-mask-config-diagnostic-with-metadata.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M05-mask-config-diagnostic-with-metadata.sh
```

requested-mutated: SHA-256 `2068383250160eaa3c6064676d5c0b1f26e5a58f0c322a1b72b7c46357cbdbd6` before and `2068383250160eaa3c6064676d5c0b1f26e5a58f0c322a1b72b7c46357cbdbd6` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M05-mask-config-diagnostic-with-metadata.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M05-mask-config-diagnostic-with-metadata.sh
```

requested-restored: SHA-256 `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` before and `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M05-mask-config-diagnostic-with-metadata.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M05-mask-config-diagnostic-with-metadata.sh
```

### M06

requested-pristine: SHA-256 `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` before and `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M06-hardlink-threshold-greater-than-two.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M06-hardlink-threshold-greater-than-two.sh
```

requested-mutated: SHA-256 `b4f87df66cdf6d7c768ccf56bcaf66768da4d393232ac123968bd384daee2432` before and `b4f87df66cdf6d7c768ccf56bcaf66768da4d393232ac123968bd384daee2432` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M06-hardlink-threshold-greater-than-two.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M06-hardlink-threshold-greater-than-two.sh
```

requested-restored: SHA-256 `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` before and `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M06-hardlink-threshold-greater-than-two.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M06-hardlink-threshold-greater-than-two.sh
```

### M07

requested-pristine: SHA-256 `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` before and `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M07-directory-attributes-soft-degrade.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M07-directory-attributes-soft-degrade.sh
```

requested-mutated: SHA-256 `aaf4e95c2cf01d8721966e7f6d740dbe1cd62d35ba9bcbe982167013e63c6079` before and `aaf4e95c2cf01d8721966e7f6d740dbe1cd62d35ba9bcbe982167013e63c6079` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M07-directory-attributes-soft-degrade.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M07-directory-attributes-soft-degrade.sh
```

requested-restored: SHA-256 `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` before and `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M07-directory-attributes-soft-degrade.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M07-directory-attributes-soft-degrade.sh
```

### M08

requested-pristine: SHA-256 `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` before and `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M08-metadata-path-not-recorded.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M08-metadata-path-not-recorded.sh
```

requested-mutated: SHA-256 `152064e02ab5423186a63d03edf6ada7c96d33515e8ada68785963f3a4caebf7` before and `152064e02ab5423186a63d03edf6ada7c96d33515e8ada68785963f3a4caebf7` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M08-metadata-path-not-recorded.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M08-metadata-path-not-recorded.sh
```

requested-restored: SHA-256 `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` before and `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M08-metadata-path-not-recorded.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M08-metadata-path-not-recorded.sh
```

### M09

requested-pristine: SHA-256 `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` before and `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M09-surface-early-return-after-files-soft.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M09-surface-early-return-after-files-soft.sh
```

requested-mutated: SHA-256 `c9a62c4d402176cd8f218e9b24850ecc08eb4bcba5c62818c9238e575c197f3c` before and `c9a62c4d402176cd8f218e9b24850ecc08eb4bcba5c62818c9238e575c197f3c` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M09-surface-early-return-after-files-soft.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M09-surface-early-return-after-files-soft.sh
```

requested-restored: SHA-256 `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` before and `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59` after; rc `2`.

```text
$ timeout 300 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --census /var/tmp/souji-r17-MutateCensusD2/M09-surface-early-return-after-files-soft.sh
stdout: (empty)
stderr:
usage: r15-census-config.py [-h] [--tool TOOL] [--case ID] [--list] [--json]
r15-census-config.py: error: unrecognized arguments: --census /var/tmp/souji-r17-MutateCensusD2/M09-surface-early-return-after-files-soft.sh
```

## Restoration evidence
Each of the nine exact scratch filenames was overwritten with the original committed bytes, byte-compared in memory to the git-show buffer, and rehashed before the restored detector invocation. All nine comparisons were true and all restored hashes were `688ff8ad684b970dd7ea87fa641ce5cf943449327b109eb32831d33136394f59`. A separate `sha256sum` invocation over the pristine copy and all nine restored filenames printed that same hash on all ten rows.

## Fixture identities
- hygiene: `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-census-hygiene.py` SHA-256 `136b0e49910bee6fef57c6f91c9e2bf8193112f870c3b395c172a3fb6484d693`, exact match to its ddb7347 blob.
- config: `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py` SHA-256 `27474396808f33ead4c44747d202a8ca0193363651ef6d1adfa458172beffd25`, exact match to its ddb7347 blob.

No operability verdict is claimed from argument-parser failures. No installations or updates were needed.

## Scratch cleanup

After exact-byte restoration and the restored requested-detector runs, the assigned scratch tree was removed:

```text
$ rm -rf -- /var/tmp/souji-r17-MutateCensusD2
exit: 0
stdout: (empty)
stderr: (empty)
```

All captured requested-detector commands and outputs and all before/mutated/restored hashes are preserved above; no scratch artifacts are needed to interpret the inconclusive verdicts.
