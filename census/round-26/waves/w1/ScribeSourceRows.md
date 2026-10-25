# ScribeSourceRows — normalized append block S128–S132

## Status

STATUS: PASS — five-row block drafted at `.ufo/waves/round-26/w1/sources-append-block.md`, 11 cells per row, no literal or escaped `|`, recheck/opened/status/used-by normalized as instructed, each staged row reproduced verbatim in the same file. The same five rows are already committed at HEAD `0833de9`; the draft is byte-identical to them (Finding 1).

## Evidence

Lane revision observed, read-only: `git rev-parse HEAD` → `0833de9591a7db81cdfa4efda2cdad2e75606f58`; `git log --oneline -4` → `0833de9` (round-26 C3), `4453128` (C1 green receipt), `a529c76` (C1 integrate), `965b869` (prereg amendment 2). `git merge-base --is-ancestor 89e0fceeefcf28db313c94120be6d25e03c60094 HEAD` → exit 0, so the prereg freeze commit is an ancestor of the observed tip. Prereg base literal `0eca7c8` per the frozen contract.

Staged bytes (read-only, never written): `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md` lines 7–9 (S109–S111), 21 (S123), 29 (S131). Each staged row splits into 11 cells and carries no `\|`; `MERGE-REPORT.md` confirms `first staged id is S109` and 134 proposed rows.

Source re-open, from already-present round-26 snapshots under `census/round-26/sources/` (`SHA256SUMS` lists 7 digests):

- `grep -n 'run_auto_maintenance' git-builtin-{fetch,merge,rebase,am,commit}.c` → `fetch.c:2926`, `merge.c:509`, `rebase.c:572`, `am.c:1942`, `commit.c:1965` — all five anchor lines re-found.
- `sed -n '390,394p' git-builtin-pull.c` → `392: strvec_pushl(&cmd.args, "fetch", "--update-head-ok", NULL);`.
- `grep -n 'This is enabled by default' git-fetch.1.txt` → `3197:This is enabled by default.` (5-word quote, no `|`).
- `grep -n "ignore errors" git-builtin-{merge,rebase,fetch}.c` → `merge.c:506`, `rebase.c:569`; no such comment at the fetch, am or commit call sites.

Block self-check (`python3 -B`, reading the drafted file and `corpus/SOURCES.md`): 5 lines between the markers; every line splits into 11 cells; `pipe_in_cell=False` and `escaped=False` for all five; `matches_SOURCES=True` for all five; all five staged rows present byte-for-byte in the file.

Deliverable: `.ufo/waves/round-26/w1/sources-append-block.md` (13 259 bytes, 101 lines), the only file this seat wrote.

## Findings

1. **The append block is already landed.** `git log --oneline -S'| S128 ' -- corpus/SOURCES.md` and the same query for `| S132 ` both return `0833de9`; `git diff HEAD -- corpus/SOURCES.md` is empty and `git rev-parse HEAD:corpus/SOURCES.md` matches the worktree. Location: `corpus/SOURCES.md` registry tail, rows S128–S132. L1 must not append a second copy; the drafted block is the normalization record and diff target.
2. **used-by is exactly the admitted set.** S128/S129/S130 → `corpus/knowledge/git-auto-maintenance-trigger-set.md, corpus/knowledge/git-auto-maintenance-trigger-set-r23.md`; S131/S132 → entry B only. Cross-checked against entry front matter: entry A `source:` lines 1–3 name S128/S129/S130; entry B lines 1–5 name S131/S129/S130/S128/S132. Location: `corpus/knowledge/git-auto-maintenance-trigger-set.md:1-3`, `...-r23.md:1-5`, `corpus/SOURCES.md` rows S128–S132.
3. **Recheck prose has no home yet.** S128/S129/S130 are now bare `on-release`, S131/S132 bare `90d`; the stripped instructions (`host git --version is 2.56.0`, `re-grep call sites at the next host git tag`, `re-run bash fixtures/r23-trigger-prune.sh`, `re-run the read-only census`) exist nowhere else — `ls corpus/lessons/ | grep -c round-26` → `0`, and entry A line 52 points the reader at `corpus/lessons/round-26.md` `## Gate`. The Gate seat must carry those four notes or the cadence loses its trigger. Location: `corpus/lessons/` (no `round-26.md`), `corpus/knowledge/git-auto-maintenance-trigger-set.md:52`.
4. **Two teaches cells are tightened, not verbatim staged.** S128 appends `; the switch is default-on` (grounded at `census/round-26/sources/git-fetch.1.txt:3197`); S129 narrows `and ignore errors from git maintenance run --auto` to `merge/rebase ignore errors ...` (grounded at `git-builtin-merge.c:506-507`, `git-builtin-rebase.c:569-570`). Both hold on the opened bytes; if L1 wants zero teaches drift, revert only those two cells and keep anchor/opened/recheck/used-by. S131's edits are prose-equivalent (`2 -> 1` → `2 to 1`, `un-aged` → `unaged`, trailing clause rephrased); S132 drops only `**` markers.
5. **Staged S131's used-by was re-pointed.** Staged row S131 named `corpus/knowledge/count-objects-garbage-semantics-r23.md`, a file this round does not admit; normalized to entry B. The package's own used-by correction table (`MERGE-REPORT.md`) does not list S131, so the only evidence for this re-point is the prereg C2 paragraph plus this block. Location: `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md:29` vs `preregistration.txt` § CLAIM C2. Also note staged S123 collides with the lane's existing S123 (git-worktree(1)); renumber is by document, as the prereg prescribes.
6. **Not verified here.** K3 (`scripts/sources-census.sh validate`, row count 127 → 132) and K4 were not run from this seat; L1 owns them. Snapshot digests quoted in the block are the lane's `SHA256SUMS` entries as read, not re-hashed.

## Limits

- No tool install or upgrade was needed; no pacman transaction was attempted.
- No lane file other than the two named artifacts was written; lane git state untouched (read-only `log`, `show`, `diff`, `status`, `rev-parse`, `merge-base` only).
- Scratch `/var/tmp/souji-r26-ScribeSourceRows/` removed before yield.
