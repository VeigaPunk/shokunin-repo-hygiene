| id | category | description | pristine | pop killed | lost | verdict |
|---|---|---|---|---|---|---|
| C01 | COUNT | symlinked-child: drop the negative conjunct (UNRECORDED\tlnk absent) | clean | 12/13 | I1 | LOAD-BEARING |
| C02 | COUNT | invalid-utf8: JSON repo list equality weakened to a length check | clean | 13/13 | - | REDUNDANT |
| C03 | COUNT | json-truncate: drift==[] weakened to drift is not None | clean | 13/13 | - | REDUNDANT |
| C04 | COUNT | invalid-utf8: stdout token check weakened to a bare \ufffd presence | clean | 13/13 | - | REDUNDANT |
| D01 | ASSERT | fifo-record: remove the assertion (return True) | clean | 12/13 | B1 | LOAD-BEARING |
| D02 | ASSERT | root-sibling: remove the assertion (return True) | clean | 12/13 | E2 | LOAD-BEARING |
| D03 | ASSERT | gitdir-sibling: remove the assertion (return True) | clean | 12/13 | E4 | LOAD-BEARING |
| D04 | ASSERT | timeout-one: remove the assertion (return True) | clean | 13/13 | - | REDUNDANT |
| D05 | ASSERT | default-timeout: remove the assertion (return True) | clean | 12/13 | G3 | LOAD-BEARING |
| D06 | ASSERT | list-timeout: remove the assertion (return True) | clean | 13/13 | - | REDUNDANT |
| D07 | ASSERT | list-rc: remove the assertion (return True) | clean | 12/13 | G5 | LOAD-BEARING |
| D08 | ASSERT | root-option-required: remove the assertion (return True) | clean | 12/13 | H1 | LOAD-BEARING |
| D09 | ASSERT | record-option-required: remove the assertion (return True) | clean | 12/13 | H2 | LOAD-BEARING |
| D10 | ASSERT | symlinked-child: remove the assertion (return True) | clean | 12/13 | I1 | LOAD-BEARING |
| D11 | ASSERT | two-digit-regs: remove the assertion (return True) | clean | 12/13 | J9 | LOAD-BEARING |
| D12 | ASSERT | json-truncate: remove the assertion (return True) | clean | 13/13 | - | REDUNDANT |
| D13 | ASSERT | invalid-utf8: remove the assertion (return True) | clean | 13/13 | - | REDUNDANT |
| H01 | HELPER | refused(): accept any exit code instead of exactly 2 | clean | 13/13 | - | REDUNDANT |
| H02 | HELPER | refused(): drop the REFUSAL-class token check, keep only rc==2 | clean | 13/13 | - | REDUNDANT |
| H03 | HELPER | refused(): token check loses the trailing colon | clean | 13/13 | - | REDUNDANT |
| H04 | HELPER | drift_line(): accept any exit code instead of exactly 1 | clean | 13/13 | - | REDUNDANT |
| H05 | HELPER | drift_line(): drop the stdout token check, keep only rc==1 | clean | 11/13 | G4,G5 | LOAD-BEARING |
| H06 | HELPER | drift_line(): stdout decoded with ignore instead of replace | clean | 13/13 | - | REDUNDANT |
| N01 | ARG | root-option-required: asserted exit code 2 -> 1 | FAIL | 13/13 | - | CAUGHT-BY-PRISTINE |
| N02 | ARG | record-option-required: asserted exit code 2 -> 0 | FAIL | 13/13 | - | CAUGHT-BY-PRISTINE |
| N03 | ARG | timeout-one: the --timeout value the case asks for 1 -> 2 | clean | 13/13 | - | REDUNDANT |
| N04 | ARG | list-timeout: the --timeout value the case asks for 1 -> 0 | FAIL | 13/13 | - | CAUGHT-BY-PRISTINE |
| N05 | KEY | ROW constant: prunable=0 -> prunable=1 | FAIL | 13/13 | - | CAUGHT-BY-PRISTINE |
| N06 | KEY | ROW constant: regs=1 -> regs=2 | FAIL | 13/13 | - | CAUGHT-BY-PRISTINE |
| N07 | KEY | json-truncate: the JSON key read changed drift -> driftlist | FAIL | 13/13 | - | CAUGHT-BY-PRISTINE |
| N08 | TOKEN | invalid-utf8: the stdout token loses its trailing tab | clean | 13/13 | - | REDUNDANT |
| N09 | KEY | two-digit-regs: the record written by the case regs=10 -> regs=1 | FAIL | 13/13 | - | CAUGHT-BY-PRISTINE |
| N10 | KEY | invalid-utf8: the invalid byte \xff replaced by \xfe | clean | 13/13 | - | REDUNDANT |
| N11 | COUNT | json-truncate: old json filler shortened 5000 -> 5 bytes | clean | 12/13 | M1 | LOAD-BEARING |
| N12 | TOKEN | default-timeout: the UNREACHABLE reason token changed | FAIL | 13/13 | - | CAUGHT-BY-PRISTINE |
| N13 | TOKEN | list-rc: the reason token changed | FAIL | 13/13 | - | CAUGHT-BY-PRISTINE |
| N14 | ARG | fifo-record: --skip-unrecorded dropped from the tool invocation | clean | 13/13 | - | REDUNDANT |
| N15 | ARG | root-sibling: --skip-unrecorded dropped from the tool invocation | clean | 13/13 | - | REDUNDANT |
| N16 | ARG | symlinked-child: --skip-unrecorded dropped from the tool invocation | FAIL | 13/13 | - | CAUGHT-BY-PRISTINE |
| N17 | TIMING | default-timeout: elapsed bound narrowed 5.0 s -> 30.0 s | clean | 13/13 | - | REDUNDANT |
| N18 | TOKEN | timeout-one: the DRIFT line matched with the tab prefix dropped | clean | 13/13 | - | REDUNDANT |
| N19 | KEY | gitdir-sibling: the gitlink target name gd2 -> gd3 | FAIL | 13/13 | - | CAUGHT-BY-PRISTINE |
| N20 | COUNT | two-digit-regs: the live count conjunct dropped | clean | 13/13 | - | REDUNDANT |
| N21 | ARG | json-truncate: the expected tool exit code 0 -> 1 | FAIL | 13/13 | - | CAUGHT-BY-PRISTINE |
| N22 | ARG | invalid-utf8: the expected tool exit code 1 -> 2 | FAIL | 13/13 | - | CAUGHT-BY-PRISTINE |
| N23 | COUNT | SUMMARY: the reported fail count pinned to 0 | clean | 0/13 | B1,E2,E4,G2,G3,G4,G5,H1,H2,I1,J9,M1,D4 | KILLS-NOTHING |
| N24 | COUNT | SUMMARY: the reported pass count pinned to the case count | clean | 13/13 | - | REDUNDANT |
| P01 | DROP2 | drop BOTH cases that kill G2 | clean | 12/13 | G2 | DROPPED-CASE |
| P02 | DROP2 | drop BOTH cases that kill G4 | clean | 11/13 | G3,G4 | DROPPED-CASE |
| P03 | DROP2 | drop timeout-of-one together with default-timeout | clean | 12/13 | G3 | DROPPED-CASE |
| T01 | TOKEN | fifo-record: REFUSAL class token changed | FAIL | 13/13 | - | CAUGHT-BY-PRISTINE |
| T02 | TOKEN | root-sibling: REFUSAL class token changed | FAIL | 13/13 | - | CAUGHT-BY-PRISTINE |
| T03 | TOKEN | timeout-one: DRIFT repo token changed | FAIL | 13/13 | - | CAUGHT-BY-PRISTINE |
| T04 | TOKEN | two-digit-regs: live count token changed | FAIL | 13/13 | - | CAUGHT-BY-PRISTINE |
| T05 | TOKEN | json-truncate: summary key token changed | FAIL | 13/13 | - | CAUGHT-BY-PRISTINE |
| T06 | TOKEN | symlinked-child: UNRECORDED repo token changed | FAIL | 13/13 | - | CAUGHT-BY-PRISTINE |
| T07 | TOKEN | root-option-required: stderr token changed | clean | 13/13 | - | REDUNDANT |
| W01 | TIMING | default-timeout: elapsed bound widened 5.0 s -> 0.5 s | clean | 12/13 | G3 | LOAD-BEARING |
| W02 | TIMING | default-timeout: elapsed bound widened 5.0 s -> 0.0 s | clean | 12/13 | G3 | LOAD-BEARING |
| W03 | TIMING | list-timeout: subprocess timeout widened 60 s -> 300 s | clean | 13/13 | - | REDUNDANT |
| W04 | TIMING | fifo-record: subprocess timeout widened 25 s -> 300 s | clean | 13/13 | - | REDUNDANT |
| X01 | DROP | drop case case_fifo_record_is_refused_not_blocked from the run | clean | 12/13 | B1 | DROPPED-CASE |
| X02 | DROP | drop case case_root_sibling_prefix_is_outside from the run | clean | 12/13 | E2 | DROPPED-CASE |
| X03 | DROP | drop case case_gitdir_sibling_prefix_is_outside from the run | clean | 12/13 | E4 | DROPPED-CASE |
| X04 | DROP | drop case case_timeout_of_one_is_accepted from the run | clean | 13/13 | - | DROPPED-CASE |
| X05 | DROP | drop case case_default_timeout_outlasts_a_blocked_git from the run | clean | 12/13 | G3 | DROPPED-CASE |
| X06 | DROP | drop case case_list_timeout_is_reported_unreachable from the run | clean | 13/13 | - | DROPPED-CASE |
| X07 | DROP | drop case case_list_nonzero_rc_is_reported_unreachable from the run | clean | 12/13 | G5 | DROPPED-CASE |
| X08 | DROP | drop case case_root_option_is_required from the run | clean | 12/13 | H1 | DROPPED-CASE |
| X09 | DROP | drop case case_record_option_is_required from the run | clean | 12/13 | H2 | DROPPED-CASE |
| X10 | DROP | drop case case_symlinked_child_is_not_discovered from the run | clean | 12/13 | I1 | DROPPED-CASE |
| X11 | DROP | drop case case_two_digit_regs_are_read_whole from the run | clean | 12/13 | J9 | DROPPED-CASE |
| X12 | DROP | drop case case_longer_old_json_is_truncated_on_write from the run | clean | 12/13 | M1 | DROPPED-CASE |
| X13 | DROP | drop case case_invalid_utf8_in_record_becomes_replacement_char from the run | clean | 12/13 | D4 | DROPPED-CASE |
