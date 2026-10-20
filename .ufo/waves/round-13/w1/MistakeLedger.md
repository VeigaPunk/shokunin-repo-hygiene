# Round 13 — W1 MistakeLedger report

seat: SoujiR13.MistakeLedger (scribe, leaf) · lane root `/home/vgpnk/Projects/shokunin/souji-shokunin` · baseline HEAD `31984f4`
axes: calibration (primary), operability, coverage

## Behavior

Drafted round-13 `## Mistakes` rows M54–M62 (draft numbering; L1 renumbers) covering the r11 certifier
relay, the r12 nonexistent K5 fixture, the M43/M44 quarantine timeout and FIFO defects, and the Q15
circular criterion. Each row names class, evidence path:line, captured-by (with `no-check` where no
executable check exists), a proposed fix, and a demonstrated/planned status. Every routed r12 verifier
item is dispositioned in Table 3 of the draft; the r12 lessons were not rewritten.

Two findings were not in the assignment and are the strongest new evidence:

1. **The r11 "restored" cert-16 bytes are not what HEAD holds.** `git show e879ba0:census/round-10/cert-16.json | sha256sum`
   → `6293283e…`. `git show HEAD:census/round-10/cert-16.json | sha256sum` → `662294df…`. Commit `1ccf11b`
   ("pre-reboot sweep: remaining r11 fragments + results") changed the file (260 insertions, 307 deletions).
   r11 records (`census/round-11/dissent-32.md:62-68`, `census/round-11/cert-12.json:2660`) that the file was
   restored to `6293283e`. The fact is demonstrated; the cause of the change is `[INFERENCE]`.
2. **The CERTIFIED record names a census that is not installed.** HEAD `census/round-10/cert-16.json:2618`
   says `certification_ready: true` for census `60aef4c0…` (`:10`, `:20`). The installed
   `tools/souji-census.sh` is `6a000c59…` (observed this session; r11 cert-13 names it as cand-census-02,
   `census/round-11/cert-13.json:206`). A CERTIFIED verdict on non-installed bytes is the false-success class
   the W1 spec asks the validator to reject.

## Gates

- Mistake rows: 9 drafted (M54–M62), each with a pointer and a status. Nothing is counted toward
  captured-by without its `no-check` note.
- Routed r12 verifier items: 10 dispositions recorded (draft Table 3). The verifier lesson was read and not edited.
- Pointer corrections for prior rows: r12 M44 `souji-vault-verify.sh:608` → guard at `:606`; the
  `wait_for_partner` FIFO source is not in the lane (only `LOG.md:404`) (draft Table 4).

## Touched surfaces

- Created: `census/round-13/mistake-draft.md` (did not exist at start; it is the assigned draft).
- Created: this report, `.ufo/waves/round-13/w1/MistakeLedger.md`.
- Read only: `corpus/lessons/round-11.md`, `round-12.md`, `round-12-verifier-spotcheck.md`, `corpus/QUALITY.md`,
  `corpus/README.md`, `corpus/knowledge/quarantine-same-filesystem-rename.md`, `census/round-11/*`, `census/round-12/*`,
  `census/round-10/cert-16.json`, `LOG.md:364-424`, `tools/souji-quarantine.sh`, `tools/souji-vault-verify.sh`,
  `tools/souji-census.sh` (hash only), `tools/souji-verify.sh` (hash only).
- Not touched: `census/operator-sweep-20261019/` (not opened or searched), any tool, any test, any commit.

## Out of scope

- No quarantine tool change, no Q8 implementation, no deletion certification, no live target access.
- No LOG.md, SCORECARD, or lesson edit (integration is L1's).
- The `tests/vault/vadv-52/ledger-k5.tsv` file matches `k5` by name only; its content was not read.

## Findings (demonstrated vs planned)

| id | class | status | key evidence |
|---|---|---|---|
| M54 | r11 relay; restore claim false at HEAD | demonstrated (bytes); cause inference | sha256 `6293283e` (e879ba0) vs `662294df` (HEAD); `1ccf11b` stat 260+/307- |
| M55 | CERTIFIED on non-installed census (false success) | demonstrated (bytes) | cert-16 `:2618`, `:10`; installed `6a000c59`; cert-14 `:326` BYTE MISMATCH |
| M56 | evidence paths outside lane | demonstrated (paths cited; one present on host, sha `2844fc13…`) | cert-16 `:8-9`, `:24`; cert-13 `:10`; cert-12 `:2660` |
| M57 | K5 committed fixture absent | demonstrated | K5 `:21` "not committed"; round-12 `:136`, `:357-359`; `grep souji-k5 tests` → none |
| M58 | Q15 circular; Q16 withdrawal | demonstrated (text) | QUALITY `:39`, `:40`; postreview `:90` |
| M59 | quarantine per-target staging, no timeout | demonstrated (incident + grep `timeout`=0) | LOG `:373-378`; quarantine `:529`, `:536` |
| M60 | FIFO digest hang | incident demonstrated (LOG); tool mechanism inference; FIFO selftest absent (grep 0) | LOG `:402-404`; `FIFO|mkfifo` = 0 in both tools |
| M61 | duplicate helper defs (shadowing) | demonstrated (count 4 each); effective-def inference | quarantine `:184/:186/:722/:727`; vault `:109/:111/:717/:722`; dispatch `:1568` |
| M62 | captured-by counts criteria with no check | demonstrated (test column read) | round-12 `:57`; QUALITY Q2,Q4,Q6,Q7,Q8,Q13,Q16 |

No fix is implemented. Q8 (M59/M60) is unmet; Q6 (M54/M55) is unmet; the K5 fixture (M57) does not exist.

## Proposed final checks for L1 (not run by this seat)

1. `git show e879ba0:census/round-10/cert-16.json | sha256sum` = `6293283e…`; `git show HEAD:census/round-10/cert-16.json | sha256sum` = `662294df…` (pre-fix; re-check after any change).
2. `sha256sum tools/souji-census.sh tools/souji-quarantine.sh tools/souji-vault-verify.sh` — record installed bytes next to every CERTIFIED claim (now `6a000c59…`, `141c0fdc…`, `f9e778ca…`).
3. `grep -c timeout tools/souji-quarantine.sh` = 0 now; after fix, `grep -nE 'timeout [0-9]+[smh]? .*(mv|sha256sum)' tools/souji-quarantine.sh` ≥ 1.
4. `grep -cE 'FIFO|mkfifo' tools/souji-quarantine.sh` = 0 now; after fix, ≥ 1 with a selftest case under `/var/tmp`.
5. `grep -cE '^(file_sha|dir_digest)\(\)' tools/souji-quarantine.sh` = 4 now; 2 after shadowed copies are removed (same for `tools/souji-vault-verify.sh`).
6. `grep -rl 'souji-k5' tests` empty now; K5 stays HELD until a committed `/var/tmp`-only fixture matches its recheck.
7. `shellcheck -S warning` (QUALITY Q9) on any new or edited shell; `bash -n` on each edited tool.
8. Any new fixture: `grep -c 'TMPDIR:-/tmp' <fixture>` = 0; a `mktemp -d` under `/var/tmp` with a trap; no `/dev/shm` (Q4/Q16).
9. Round-count: the r12 awk command (`round-12.md:55`) applied to `corpus/lessons/round-13.md` after integration; report the count with `no-check` rows flagged.
10. `grep -oE 'QUALITY\.md Q[0-9]+' corpus/lessons/round-13.md | sort -u` — each resolves to a non-withdrawn `^| Qn |` row.

## Tool installs

None. Commands used: `git show`, `git ls-files`, `git rev-parse`, `git log`, `git status`, `grep`, `sha256sum`, `test -e`, `wc`. No package install or upgrade was needed.

## Limits

- Draft IDs; rows are not independent non-author evidence. Do not claim non-author status.
- M54 cause (`1ccf11b`) and M60 mechanism (bash last-definition-wins, M61) are `[INFERENCE]`; neither was executed.
- The M60 fixture provenance (`wait_for_partner`) is `[to-verify]`: only `LOG.md:404` names it in the lane.
- The census-hash claim in finding 2 is from one `sha256sum` this session; the r11 history is read from the r11 records, not re-run.
- The peer `SoujiR13.AttackCalibration` sent a fact on the installed census (`6a000c59`, cert-16 `662294df`, commit `1ccf11b`); this seat re-observed both facts and folded them into M54/M55. Its own report file was not read.

Artifacts:
- `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-13/mistake-draft.md` (draft rows, Table 1–4, final checks, limits)
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-13/w1/MistakeLedger.md` (this report)
