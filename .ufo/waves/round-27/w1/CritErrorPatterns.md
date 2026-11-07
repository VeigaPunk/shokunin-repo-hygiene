## Status
STATUS: PARTIAL — review based on preregistration, SKILL.md, and staged C3 draft; installed fixture and landed counters are not present in the opened evidence.

## Evidence
- Read `.ufo/waves/round-27/preregistration.txt` lines 1–14 (frozen counters) and `SKILL.md` lines 90–117 (error signatures).
- Read `.ufo/waves/round-27/w1/souji-pre-report-gate.sh` lines 1–29, 79–104, 131–143 and `round-27.md` lines 1–24.
- No fixture at `tests/fixtures/r27-pre-report-gate.sh` was found in the fixture listing; no execution or landing-tip claim made.

## Findings
1. **Unpushed-lane / keep-only counter blind spot — attack.** SKILL.md lines 112–115 explicitly says branch queries miss jj keep-only commits and detached HEAD is not a citable pin. The frozen C1/C2 counters are revision based, while C3 draft compares `refs/heads/$branch` to `ls-remote`; those establish only branch equality, not that measured files/counters or working bytes are at that commit. A keep-only or dirty working-copy change could therefore be omitted/misrepresented if receipts invoke branch-only state. Smallest safe correction: require each receipt to pin full landed revision and prove its measured inputs are committed raw blobs at that pin (use the existing rev-pin semantics), and separately reject changed measured paths; do not treat branch equality as a durable receipt.

2. **Checkpoint-blob bloat — not established.** Opened draft proposal identifies only small source/fixture deliverables; there is no census/round-27 receipt inventory or byte-size evidence to prove generated blobs absent. This remains unverified, not a clean finding. Smallest safe correction: before admission inspect exact new paths and blob sizes/types, explicitly exclude generated census/checkpoint payloads unless required by frozen contract.

3. **Phantom fixture / wrong-byte — unresolved, concrete gap.** Frozen contract requires four isolated `/var/tmp` cases, but the staged gate script alone is not the fixture, and the inspected fixture directory listing did not show `r27-pre-report-gate.sh`. Thus no evidence that fixture worlds check `git rev-parse --show-toplevel` or that invoked bytes are the installed gate. Smallest safe correction: fixture must assert each constructed world’s top-level path equals its private case root and invoke the exact selected/installed tool path, with a negative control proving false-green rejection.

4. **Git deletes without receipt — no signal in inspected draft.** Reviewed gate draft contains `rev-parse`, `ls-remote`, `status`, report grep; no maintenance or delete command appears in those inspected ranges. This is not proof about uninspected fixture/helper code. Keep the test worlds isolated and ensure no raw commit/maintenance path is used.

5. **Post-guard FIFO swap / unbounded read — attack.** C3 draft checks report with `-s`, then separately runs `grep -c` on the report (lines 89–102), creating a post-check reopen and no bound; a substituted FIFO can block, and a concurrent replacement can change bytes after the existence check. Prereg/read and Git operations likewise lack explicit bounds in the draft. Smallest safe correction: consume a single safely opened regular-file snapshot under a hard timeout (reject non-regular/symlink as policy requires), and bound repository commands; avoid check-then-reopen.

## Attack log
- Counter authority must be pinned to committed content, not inferred from branch refs under jj colocation.
- Fixture execution, root identity, and installed-byte binding remain unproven until the named fixture exists and its four isolated cases are inspected/run by the integrator.
