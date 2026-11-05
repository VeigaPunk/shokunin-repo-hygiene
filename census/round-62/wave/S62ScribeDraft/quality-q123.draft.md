## Round 62 criteria

Append under `corpus/QUALITY.md` after the `## Round 61 criteria` table (same five-column layout as Q121 and Q122).

| id | criterion | applies to | check | motivating evidence |
|---|---|---|---|---|
| Q123 | An index-flagged entry is refused before a clean-tree receipt. A receipt writer's clean-tree decision reads the index tag of every tracked path it depends on (`git ls-files -v -z`) and refuses any tag that is not `H`, with a message beginning `RECEIPT-INDEX-FLAG-CONCEALED:` that names the path and tag, unconditionally (`--allow-dirty` does not override it). A clean `git status --porcelain` is not evidence of a clean tree when a tracked entry carries skip-worktree or assume-unchanged. | receipt writers and any gate that certifies a clean tree from `git status` | counter matrix rows D, E, F and G are refused with `RECEIPT-INDEX-FLAG-CONCEALED`; rows A and B are accepted; row C is refused with `lane worktree is dirty`; the base bytes in the candidate slot give `new_forgeries={{DO_NOTHING_FORGERIES}} EXIT={{DO_NOTHING_EXIT}}` (the fix is shown able to fail; frozen expectation 3 and EXIT 1) | `corpus/lessons/round-62.md` `## Mistakes` M1; S292 (git-ls-files(1) `-v`); S291 (git-update-index(1) NOTES); `corpus/knowledge/skip-worktree-concealment.md`; control `{{CONTROL_RECEIPT_PATH}}` |
