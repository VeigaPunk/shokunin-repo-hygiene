### fixture-mutant grid (wave 3)

| fixture mutant | cat | pristine (pinned tool) | population mutants still killed | lost kills | verdict |
|---|---|---|---|---|---|
| C01 | COUNT | clean rc=0 fail=0 pass=13/13 | 12/13 | I1 | LOAD-BEARING (removing it loses a kill) |
| C02 | COUNT | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| C03 | COUNT | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| C04 | COUNT | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| D01 | ASSERT | clean rc=0 fail=0 pass=13/13 | 12/13 | B1 | LOAD-BEARING (removing it loses a kill) |
| D02 | ASSERT | clean rc=0 fail=0 pass=13/13 | 12/13 | E2 | LOAD-BEARING (removing it loses a kill) |
| D03 | ASSERT | clean rc=0 fail=0 pass=13/13 | 12/13 | E4 | LOAD-BEARING (removing it loses a kill) |
| D04 | ASSERT | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| D05 | ASSERT | clean rc=0 fail=0 pass=13/13 | 12/13 | G3 | LOAD-BEARING (removing it loses a kill) |
| D06 | ASSERT | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| D07 | ASSERT | clean rc=0 fail=0 pass=13/13 | 12/13 | G5 | LOAD-BEARING (removing it loses a kill) |
| D08 | ASSERT | clean rc=0 fail=0 pass=13/13 | 12/13 | H1 | LOAD-BEARING (removing it loses a kill) |
| D09 | ASSERT | clean rc=0 fail=0 pass=13/13 | 12/13 | H2 | LOAD-BEARING (removing it loses a kill) |
| D10 | ASSERT | clean rc=0 fail=0 pass=13/13 | 12/13 | I1 | LOAD-BEARING (removing it loses a kill) |
| D11 | ASSERT | clean rc=0 fail=0 pass=13/13 | 12/13 | J9 | LOAD-BEARING (removing it loses a kill) |
| D12 | ASSERT | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| D13 | ASSERT | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| H01 | HELPER | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| H02 | HELPER | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| H03 | HELPER | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| H04 | HELPER | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| H05 | HELPER | clean rc=0 fail=0 pass=13/13 | 11/13 | G4,G5 | LOAD-BEARING (removing it loses a kill) |
| H06 | HELPER | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| N01 | ARG | FAIL rc=1 fail=1 | 13/13 | - | CAUGHT-BY-PRISTINE (self-inconsistent: breaks on the pinned tool) |
| N02 | ARG | FAIL rc=1 fail=1 | 13/13 | - | CAUGHT-BY-PRISTINE (self-inconsistent: breaks on the pinned tool) |
| N03 | ARG | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| N04 | ARG | FAIL rc=1 fail=1 | 13/13 | - | CAUGHT-BY-PRISTINE (self-inconsistent: breaks on the pinned tool) |
| N05 | KEY | FAIL rc=1 fail=1 | 13/13 | - | CAUGHT-BY-PRISTINE (self-inconsistent: breaks on the pinned tool) |
| N06 | KEY | FAIL rc=1 fail=1 | 13/13 | - | CAUGHT-BY-PRISTINE (self-inconsistent: breaks on the pinned tool) |
| N07 | KEY | FAIL rc=1 fail=1 | 13/13 | - | CAUGHT-BY-PRISTINE (self-inconsistent: breaks on the pinned tool) |
| N08 | TOKEN | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| N09 | KEY | FAIL rc=1 fail=1 | 13/13 | - | CAUGHT-BY-PRISTINE (self-inconsistent: breaks on the pinned tool) |
| N10 | KEY | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| N11 | COUNT | clean rc=0 fail=0 pass=13/13 | 12/13 | M1 | LOAD-BEARING (removing it loses a kill) |
| N12 | TOKEN | FAIL rc=1 fail=1 | 13/13 | - | CAUGHT-BY-PRISTINE (self-inconsistent: breaks on the pinned tool) |
| N13 | TOKEN | FAIL rc=1 fail=1 | 13/13 | - | CAUGHT-BY-PRISTINE (self-inconsistent: breaks on the pinned tool) |
| N14 | ARG | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| N15 | ARG | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| N16 | ARG | FAIL rc=1 fail=1 | 13/13 | - | CAUGHT-BY-PRISTINE (self-inconsistent: breaks on the pinned tool) |
| N17 | TIMING | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| N18 | TOKEN | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| N19 | KEY | FAIL rc=1 fail=1 | 13/13 | - | CAUGHT-BY-PRISTINE (self-inconsistent: breaks on the pinned tool) |
| N20 | COUNT | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| N21 | ARG | FAIL rc=1 fail=1 | 13/13 | - | CAUGHT-BY-PRISTINE (self-inconsistent: breaks on the pinned tool) |
| N22 | ARG | FAIL rc=1 fail=1 | 13/13 | - | CAUGHT-BY-PRISTINE (self-inconsistent: breaks on the pinned tool) |
| N23 | COUNT | clean rc=0 fail=0 pass=13/13 | 0/13 | B1,E2,E4,G2,G3,G4,G5,H1,H2,I1,J9,M1,D4 | LOAD-BEARING (removing it loses a kill) |
| N24 | COUNT | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| P01 | DROP2 | clean rc=0 fail=0 pass=11/11 | 12/13 | G2 | DROPPED-CASE (cases<13: not pristine under the counter's cases>=13 rule) |
| P02 | DROP2 | clean rc=0 fail=0 pass=11/11 | 11/13 | G3,G4 | DROPPED-CASE (cases<13: not pristine under the counter's cases>=13 rule) |
| P03 | DROP2 | clean rc=0 fail=0 pass=11/11 | 12/13 | G3 | DROPPED-CASE (cases<13: not pristine under the counter's cases>=13 rule) |
| T01 | TOKEN | FAIL rc=1 fail=1 | 13/13 | - | CAUGHT-BY-PRISTINE (self-inconsistent: breaks on the pinned tool) |
| T02 | TOKEN | FAIL rc=1 fail=1 | 13/13 | - | CAUGHT-BY-PRISTINE (self-inconsistent: breaks on the pinned tool) |
| T03 | TOKEN | FAIL rc=1 fail=1 | 13/13 | - | CAUGHT-BY-PRISTINE (self-inconsistent: breaks on the pinned tool) |
| T04 | TOKEN | FAIL rc=1 fail=1 | 13/13 | - | CAUGHT-BY-PRISTINE (self-inconsistent: breaks on the pinned tool) |
| T05 | TOKEN | FAIL rc=1 fail=1 | 13/13 | - | CAUGHT-BY-PRISTINE (self-inconsistent: breaks on the pinned tool) |
| T06 | TOKEN | FAIL rc=1 fail=1 | 13/13 | - | CAUGHT-BY-PRISTINE (self-inconsistent: breaks on the pinned tool) |
| T07 | TOKEN | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| W01 | TIMING | clean rc=0 fail=0 pass=13/13 | 12/13 | G3 | LOAD-BEARING (removing it loses a kill) |
| W02 | TIMING | clean rc=0 fail=0 pass=13/13 | 12/13 | G3 | LOAD-BEARING (removing it loses a kill) |
| W03 | TIMING | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| W04 | TIMING | clean rc=0 fail=0 pass=13/13 | 13/13 | - | REDUNDANT (still kills all 13: vacuous for the population) |
| X01 | DROP | clean rc=0 fail=0 pass=12/12 | 12/13 | B1 | DROPPED-CASE (cases<13: not pristine under the counter's cases>=13 rule) |
| X02 | DROP | clean rc=0 fail=0 pass=12/12 | 12/13 | E2 | DROPPED-CASE (cases<13: not pristine under the counter's cases>=13 rule) |
| X03 | DROP | clean rc=0 fail=0 pass=12/12 | 12/13 | E4 | DROPPED-CASE (cases<13: not pristine under the counter's cases>=13 rule) |
| X04 | DROP | clean rc=0 fail=0 pass=12/12 | 13/13 | - | DROPPED-CASE (cases<13: not pristine under the counter's cases>=13 rule) |
| X05 | DROP | clean rc=0 fail=0 pass=12/12 | 12/13 | G3 | DROPPED-CASE (cases<13: not pristine under the counter's cases>=13 rule) |
| X06 | DROP | clean rc=0 fail=0 pass=12/12 | 13/13 | - | DROPPED-CASE (cases<13: not pristine under the counter's cases>=13 rule) |
| X07 | DROP | clean rc=0 fail=0 pass=12/12 | 12/13 | G5 | DROPPED-CASE (cases<13: not pristine under the counter's cases>=13 rule) |
| X08 | DROP | clean rc=0 fail=0 pass=12/12 | 12/13 | H1 | DROPPED-CASE (cases<13: not pristine under the counter's cases>=13 rule) |
| X09 | DROP | clean rc=0 fail=0 pass=12/12 | 12/13 | H2 | DROPPED-CASE (cases<13: not pristine under the counter's cases>=13 rule) |
| X10 | DROP | clean rc=0 fail=0 pass=12/12 | 12/13 | I1 | DROPPED-CASE (cases<13: not pristine under the counter's cases>=13 rule) |
| X11 | DROP | clean rc=0 fail=0 pass=12/12 | 12/13 | J9 | DROPPED-CASE (cases<13: not pristine under the counter's cases>=13 rule) |
| X12 | DROP | clean rc=0 fail=0 pass=12/12 | 12/13 | M1 | DROPPED-CASE (cases<13: not pristine under the counter's cases>=13 rule) |
| X13 | DROP | clean rc=0 fail=0 pass=12/12 | 12/13 | D4 | DROPPED-CASE (cases<13: not pristine under the counter's cases>=13 rule) |

### BASE row: which case kills which population mutant (landed fixture, unmutated)

| population mutant | killed by the landed fixture | failing case(s) |
|---|---|---|
| B1 | yes | fifo-record-is-refused-not-blocked |
| E2 | yes | root-sibling-prefix-is-outside |
| E4 | yes | gitdir-sibling-prefix-is-outside |
| G2 | yes | list-timeout-is-reported-unreachable,timeout-of-one-is-accepted |
| G3 | yes | default-timeout-outlasts-a-blocked-git |
| G4 | yes | default-timeout-outlasts-a-blocked-git,list-timeout-is-reported-unreachable |
| G5 | yes | list-nonzero-rc-is-reported-unreachable |
| H1 | yes | root-option-is-required |
| H2 | yes | record-option-is-required |
| I1 | yes | symlinked-child-is-not-discovered |
| J9 | yes | two-digit-regs-are-read-whole |
| M1 | yes | longer-old-json-is-truncated-on-write |
| D4 | yes | invalid-utf8-in-record-becomes-replacement-char |

### cases and the population mutants they catch

- `default-timeout-outlasts-a-blocked-git`: G3,G4
- `fifo-record-is-refused-not-blocked`: B1
- `gitdir-sibling-prefix-is-outside`: E4
- `invalid-utf8-in-record-becomes-replacement-char`: D4
- `list-nonzero-rc-is-reported-unreachable`: G5
- `list-timeout-is-reported-unreachable`: G2,G4
- `longer-old-json-is-truncated-on-write`: M1
- `record-option-is-required`: H2
- `root-option-is-required`: H1
- `root-sibling-prefix-is-outside`: E2
- `symlinked-child-is-not-discovered`: I1
- `timeout-of-one-is-accepted`: G2
- `two-digit-regs-are-read-whole`: J9
