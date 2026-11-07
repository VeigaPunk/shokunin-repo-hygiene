# SCORECARD additions — round 27 (draft; L1 integrates)

Apply the following as additions to `SCORECARD.md`; preserve the existing tables and rows. Keep the measurements newest-first (above `### Round 26 measurements`), append corrections at EOF, add the planned bullet under `## Planned`, and append the capability row inside `## Capabilities`.

### Round 27 measurements

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 internal landing-gate dangling-pointer findings | calibration 7 | `findings=2` at base `e78ac7c4837b81b634db4a927605a751a7f006ba`; the two `LG-DANGLING-PTR` findings are `corpus/knowledge/registry` and `corpus/lessons/round-24.md:232:S118` (observed by running the frozen gate at base) | EVIDENCE-PENDING: expected `findings=0`; do not replace until final-tip receipt is measured | `python3 -B tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <full40> --round 27 --fleet-root /home/vgpnk/Projects/shokunin` | EVIDENCE-PENDING |
| C2 grounded F4 origin-record entries and registry assimilation (S152/S210/S211) | coverage 8 | `registry_rows=132`, `grounded_F4=2` at base `e78ac7c4837b81b634db4a927605a751a7f006ba` (frozen preregistration) | EVIDENCE-PENDING: expected `registry_rows=135`, `grounded_F4=4`, gate `entries=2 ok=2 fail=0`, sources-census rc 0 | `grep -cE '^\\|[[:space:]]*S[0-9]{3,}[[:space:]]*\\|' corpus/SOURCES.md`; `grep -rlE '^ground: F4' corpus/knowledge/ | wc -l`; `python3 -B tools/souji-gate-check.py ...`; `sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` | EVIDENCE-PENDING |
| C3 pre-report gate and isolated false-green fixture | operability 8 | gate absent at base `e78ac7c4837b81b634db4a927605a751a7f006ba` | EVIDENCE-PENDING: expected gate present; fixture `cases=4 pass=4 control=FALSE-GREEN-REJECTED` rc 0; c3 receipt verify=ok | `bash tests/fixtures/r27-pre-report-gate.sh`; `tools/souji-receipt-run.py verify ...` | EVIDENCE-PENDING |

### Round 27 append-only corrections

- R27-C1: appended pointer exemption `corpus/knowledge/registry` is for the prose fragment in `corpus/QUALITY.md` Q59's surface-class sentence, not a repository citation. It does not alter Q59 or its source line.
- R27-C1: appended pointer exemption `corpus/lessons/round-24.md:232:S118` is the composite enumerated-site token described by `corpus/QUALITY.md` Q57, not a whole-file/path citation. It does not alter the lesson or Q57. No in-place line-reference change is made by these two append-only exemption rows; therefore there are no old-to-new line mappings for this correction.

Capability table addition (append within `## Capabilities`):

| pre-report gate (r27) | check the lane branch tip against its remote, require a report with exactly one `## SHONEN` heading, reject uncommitted lane-authored leftovers, and require the preregistration file; named check outcomes/exit codes, with a four-case isolated selftest that rejects an always-pass false-green control | `tools/souji-pre-report-gate.sh`; `tests/fixtures/r27-pre-report-gate.sh` (EVIDENCE-PENDING receipt) | r27 |

Planned-section addition:

- **r28 (planned r27):** (a) calibration continuation: re-audit the pointer-exemption counter and its exact-token/non-overmatch boundary against any newly surfaced internal landing-gate citation sites; keep all source citations intact and append corrections rather than rewriting prior records. (b) coverage continuation: continue bounded F4 origin-record assimilation only where fresh primary-source grounding supports a distinct mechanism; re-ground existing F4 entries and retain explicit admit/reject gates. (c) operability continuation: exercise the pre-report gate against additional report/worktree/remote edge cases without weakening the r27 four-case contract or changing its false-green rejection requirement. No axis harm; certification OFF, K5 HELD, F5 reap and NAMESPACE holds unchanged.
