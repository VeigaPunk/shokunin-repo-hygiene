# S62ExecCandidate — C1 calibration candidate (round 62, w1)

Lane base: 16fa821fdce00e709d6895ccfc7aaffa465af195. Scratch clone verified at base before edit (`rev-parse HEAD` = base; `--show-toplevel` = clone dir; clean status). No lane, index, or jj writes. No commits.

## Delivered files (this directory)

- `souji-receipt-write.candidate.py` — full candidate bytes
- `souji-receipt-write.base.py` — base bytes (`git show 16fa821…:tools/souji-receipt-write.py`)
- `candidate.patch` — `git diff` in the clone
- `candidate.sha256`
- `rows-candidate.txt`, `rows-base.txt` — one line per row (row, arm, rc, OUT existence, stderr first line)
- `rows-candidate.detail.txt`, `rows-base.detail.txt` — non-`H` index tags and porcelain per row
- `rows.json` — machine-readable rows and both r60 return codes
- `r60-candidate.log`, `r60-base.log` — full r60 fixture output
- `receipts/` — every OUT receipt that was actually written

## Candidate hashes

- candidate.patch sha256: `233bef014be55c841b8cda168c93b06254ae7c59f6a2d364d4309f574843992b`
- souji-receipt-write.candidate.py sha256: `9fb55f356aa256475d08f4b82d7132b1ce200a30f0dc26fec17eae969df0ec9b`
- base sha256: `367a0ca3bdea35714f1c1dba7bca407f05e8ec8d8f6e9c16f071d6e20e503d2c`

Diff scope: `git -C clone diff --stat` → `tools/souji-receipt-write.py | 18 ++++++++++++++++++`, 1 file, 18 insertions, 0 deletions. Python `ast.parse` of the candidate: ok (rc 0).

## What was edited

1. Module docstring: added blank line + paragraph `round 62 (C1): refuses any index entry whose / \`git ls-files -v\` tag is not H, before the dirty check.` (3 lines).
2. Inserted the specified block immediately before `# behaviour 7: clean lane tree unless --allow-dirty` (15 lines): `git(root, "ls-files", "-v", "-z")`, non-zero rc → `refuse("cannot read index flags of …")`, per-record tag != `H` → `refuse("RECEIPT-INDEX-FLAG-CONCEALED: <path> carries index flag <tag>; …")`. The `git()` helper signature and `refuse()` are as in the file; no adaptation was needed. Refusal text is verbatim from the spec.

Nothing else changed. No deviation from the specification.

## r60 fixture (`tests/fixtures/r60-receipt-write.py --tool <bytes> --work <dir>`)

- Candidate arm (`$S/clone/tests/fixtures/…`, tool = candidate bytes): `SUMMARY cases=8 pass=8 fail=0 control=ALWAYS-WRITE-REJECTED,ALWAYS-REFUSE-REJECTED`, exit rc=0.
- Base arm (`clone-base`, tool = base bytes): `SUMMARY cases=8 pass=8 fail=0 control=ALWAYS-WRITE-REJECTED,ALWAYS-REFUSE-REJECTED`, exit rc=0.

Both arms: `# control always-write failed cases [1..8] -> ALWAYS-WRITE-REJECTED`, `# control always-refuse failed cases [1, 3] -> ALWAYS-REFUSE-REJECTED`.

## Seven concealment rows (fresh repos under scratch; command `python3 -B <tool> --root R --rev REV --instrument tools/instr.sh --out OUT --allow-outside [--allow-dirty] -- sh -c 'echo ok'`)

Candidate arm:

| Row | Case | rc | OUT exists | stderr (first line) |
|---|---|---|---|---|
| A | honest-clean | 0 | yes | (empty) |
| B | honest-allow-dirty | 0 | yes | (empty) |
| C | dirty-visible | 2 | no | `refused: lane worktree is dirty (git status --porcelain non-empty); pass --allow-dirty to override` |
| D | skip-worktree-forged | 2 | no | `refused: RECEIPT-INDEX-FLAG-CONCEALED: tools/counter.py carries index flag S; …` |
| E | assume-unchanged-forged | 2 | no | `refused: RECEIPT-INDEX-FLAG-CONCEALED: tools/counter.py carries index flag h; …` |
| F | skip-worktree-unmodified | 2 | no | `refused: RECEIPT-INDEX-FLAG-CONCEALED: tools/counter.py carries index flag S; …` |
| G | instrument-skip-worktree-forged | 2 | no | `refused: RECEIPT-INDEX-FLAG-CONCEALED: tools/instr.sh carries index flag S; …` |

Base arm:

| Row | Case | rc | OUT exists | stderr (first line) |
|---|---|---|---|---|
| A | honest-clean | 0 | yes | (empty) |
| B | honest-allow-dirty | 0 | yes | (empty) |
| C | dirty-visible | 2 | no | `refused: lane worktree is dirty (git status --porcelain non-empty); pass --allow-dirty to override` |
| D | skip-worktree-forged | 0 | yes | (empty) — forgery accepted |
| E | assume-unchanged-forged | 0 | yes | (empty) — forgery accepted |
| F | skip-worktree-unmodified | 0 | yes | (empty) — accepted under flag |
| G | instrument-skip-worktree-forged | 2 | no | `refused: worktree tools/instr.sh differs from committed bytes at 4a7173fa…` |

Index/porcelain evidence (`git ls-files -v` non-`H` entries; `git status --porcelain`): A none / `''`; B and C `M notes.txt`; D `S tools/counter.py` / `''`; E `h tools/counter.py` / `''`; F `S tools/counter.py` / `''`; G `S tools/instr.sh` / `''`. The D/E/F/G porcelain is empty even with forged bytes, confirming the concealment.

Predicate as seen by this seat: candidate new_forgeries = 0 (D, E, F refused), new_honest = 2 (A, B accepted), class_mismatches = 0 (D/E/F/G name `RECEIPT-INDEX-FLAG-CONCEALED`; C names `lane worktree is dirty`), G refused, r60 `pass=8 fail=0` with both controls rejected. Base: D/E/F accepted = 3 forgeries (the do-nothing control's `new_forgeries=3` observation is reproduced as three accepted forgery receipts; the counter's own scoring script was not run by this seat).

## Limits

- The check inspects only index-tracked paths via `git ls-files -v`; untracked files remain the existing porcelain status check's responsibility.
- A flag set after the check but before the receipt is written is a TOCTOU window; the receipt does not bind index state.
- The `git status --porcelain` check still runs after the flag check, unchanged.
- Row fixtures are created by this seat in scratch repos with a throwaway identity; they mirror the spec's mutations, not the counter's own generated fixtures, so the counter's authoritative scoring remains the L1's after-measurement.
- No tools were installed or upgraded by this seat (Python 3.14.8 present; none added). Record: none.
- Scratch `$S` removed after copying receipts into this directory.

## Checks for the L1 to run

- `sha256sum -c candidate.sha256` (in this directory) to confirm the candidate bytes; `git apply --check candidate.patch` against base for integration.
- The counter's 7-row scoring against the candidate bytes and the base bytes (`new_forgeries`, `new_honest`, `class_mismatches`), and the r60 fixture on the integrated lane tree.
