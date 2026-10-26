# SwarmScribe47 — r33 w1 skill/QUALITY drafts

## Status
STATUS: PASS — three drafts written to `.ufo/waves/round-33/w1/deliver-skill-rows.md`: two `## Gate registry` rows whose exit maps are quoted from the two counters' docstrings at `2d9bca5`, one `## Error patterns` bullet for the trailing-slash `TMPDIR` class (mechanism confirmed by two paired base re-runs, executed this seat), and one `QUALITY.md` `Q75` row; every value that no bytes carried is marked `<L1>`. Neither claim target was measured by this seat: C1/C2 counters were not run here.

## Evidence

Contract and shape, read at `2d9bca55a9f042a2c9ed60a797a8069e74c41f46` unless stated:
- `census/round-33/preregistration.txt` — frozen labels C1-CURRENCY / C2-SCRATCH, base `6017a482e7068d5afb7617640198fbb0fe743357`, targets `mismatches=0` and `legs=11 pass=5 fail=0 harm=0`.
- `git show 2d9bca5:SKILL.md`: `## Gate registry` at line 187, the gate table's header row at line 197 (eight columns: name, kind, entry command, verdict map, self-test command, pinned-value path, write scope, owner), last row `r32-c3-counter` at line 258, `Sources for this skill:` at 260. `## Error patterns (false-SAFE signatures)` at 79, whose last bullet is the r32 jj-mtime bullet ending at line 158; the section's closing paragraph starts at line 160.
- `census/round-33/c1-counter.py` docstring: "Exit 0 iff mismatches=0; 1 otherwise; 2 could-not-evaluate. Read-only on --root." Exit 2 covers, in code: non-40-hex/unresolvable `--rev`/`--list-rev`, `c1-items.tsv` absent or a malformed item line, `SCORECARD.md` absent or not prefixed by its `--list-rev` bytes, `--scratch` under `/tmp`, `/var/tmp` or `/dev/shm`, unknown `--only` id, git failure; `--only` prints ` partial=1`.
- `census/round-33/c2-counter.py` docstring: "Exit 0 iff fail=0 and harm=0; 1 otherwise; 2 could-not-evaluate. Read-only on --root." Exit 2 also covers `bwrap`/`strace` absent, `c2-legs.tsv` absent or malformed, clone failure or clone toplevel mismatch.
- `census/round-33/c1-items.tsv:1-15` — 24 items K01-K08, K11-K26, K09/K10 unused.
- `census/round-33/c2-legs.tsv:24-34` — O1 `sandbox`, O2/O3 `sandbox-nt`, O4/O5 `slash`, G1-G6 `guard`, with exact argv.
- `census/round-33/records/controls.txt` — do-nothing at the frozen counters: `SUMMARY items=24 agree=19 mismatches=5 restated=0 rev=2d9bca5…`, rc 1; `SUMMARY legs=11 pass=0 fail=5 harm=0 rev=2d9bca5…`, rc 1.
- `census/round-33/records/feasibility.txt:142-160` — feasibility leg K05/K18 `AGREE … restated` at `190b4b1`, junk arms `BAD-CAUSE` at `65812db`; `:168` O4 base slash line `rev-slash=rc1:selftest: 69 checks, 10 failed`; `:258` the repair diff's added comment line `+# fd prints the single-slash path, so the scratch-prefix case patterns below`.
- `corpus/QUALITY.md` — 179 lines, ends at `Q74` inside `## Round 32 criteria` (line 171); r32 section column header `| id | criterion | applies to | check | motivating evidence |`. Q71 reads "A committed tool, counter, probe or fixture takes its scratch root from the caller's `TMPDIR`".
- Base-bytes mechanism receipts, this seat, scratch clone at `6017a48` (`git -C <clone> rev-parse --show-toplevel` → `/fast/scratch/hyaku/souji-r33/SwarmScribe47/c`, printed before any commit):
  - `env TMPDIR=<scratch>/tmp/ bash tools/souji-census.sh --selftest` → rc 1, `selftest: 69 checks, 13 failed`; failing checks include `FAIL watchdog timeout row missing or malformed`, `FAIL timed-out Git process remains (pid=)`, `FAIL parent SIGTERM cleanup … tmp=`, i.e. the worker-scratch discovery path.
  - `env TMPDIR=<scratch>/tmp bash tools/souji-census.sh --selftest` → rc 0, `selftest: 69 checks, 0 failed` (67.87 s).
  - `env TMPDIR=<scratch>/tmp/ bash tools/souji-verify.sh --selftest` → rc 1, `selftest: 49 checks, 2 failed`; both failures are the two ledger-revocation checks (`FAIL R9 … ledger revocation was reached`), each output line carrying `obsidian=no-matching-ledger-row`, with the scratch path printed as `…/tmp//souji-round9-selftest.5VeKQG/…`.
  - `env TMPDIR=<scratch>/tmp bash tools/souji-verify.sh --selftest` → rc 0, `selftest: 49 checks, 0 failed` (12.96 s).
- Tooling: no install, no upgrade, no pacman transaction, no subagent, no git/jj mutation in the lane; the only writes are this report and the delivery file. Scratch removed after the receipts were copied (see Deliveries).

## Findings

1. **The two SOURCES ids this bullet must cite are not free rows.** `corpus/SOURCES.md` at `2d9bca5` ends at `S223` (147 `| S…` rows; no `S224`, no `S225`), so no POSIX-pathname or proc_pid_fd row can be quoted. Worse, `corpus/lessons/round-32.md:25` already prints the id `S224` for the git-gc.adoc candidate — "NOT APPENDED as a row; ADMIT as source through `S063`" — so appending `S224` with different content would collide with a committed lesson table. `proc_pid_fd(5)` already carries `S083`, `S086`, `S095`, `S096` (`corpus/SOURCES.md:104,107,116,117`). The draft cites both ids as `<L1>`; the L1 must renumber or record the round-32 collision before the bullet lands.
2. **`corpus/lessons/round-33.md` does not exist** at base, at `2d9bca5`, or in the worktree (`git cat-file -e` fails). `Q75`'s motivating-evidence cell therefore carries `<L1>` for the lesson pointer; the row cannot land before the lesson it cites.
3. **The O4 slash failure count is not a stable observation, though its verdict is.** At identical base bytes the same leg reads `10 failed` (`census/round-33/records/feasibility.txt:168`), `12 failed` (`census/round-33/records/controls.txt`), and `13 failed` (this seat's re-run), each at rc 1 with `69 checks`. The slash PASS rule compares rc and last line between the two *repaired* runs (both `0 failed`), so the frozen target is unaffected; but any receipt quoting the red count as reproducible is wrong, and the bullet says so.
4. **The registry's legacy-selftest instruction is `TMPDIR=/var/tmp`** (`SKILL.md:193`, "Always use `TMPDIR=/var/tmp` for the legacy selftests"), which is a read-only empty dir in the C2 sandbox legs. The two drafted rows therefore name `--scratch` and the counters' own `TMPDIR` handling rather than restating that instruction, so the new rows do not contradict Q71 or the sandbox legs.
5. **Draft placement depends on line numbers that will move.** Gate rows are anchored after line 258 and the error bullet after line 158 at `2d9bca5`; both drafts restate the *row/bullet* content, so the L1 should paste by anchor text, not offset.

## Out of scope
Neither counter was executed by this seat, so no target reading is claimed: C1 `mismatches=0` and C2 `legs=11 pass=5 fail=0 harm=0` are `<L1>`. No amendments, no edits to `SKILL.md`, `QUALITY.md`, `SCORECARD.md` or any tool, no attack on a frozen predicate. No fleet path touched; `/home/vgpnk/Projects/shokuknow` read-only and unopened this run.

## Deliveries
- `.ufo/waves/round-33/w1/deliver-skill-rows.md` — (a) two `## Gate registry` rows, (b) one `## Error patterns` bullet, (c) one `QUALITY.md` `Q75` row with its `## Round 33 criteria` section, each with placement anchors and a `<L1>` field list.
- Scratch `/fast/scratch/hyaku/souji-r33/SwarmScribe47` removed after the receipts above were copied; no tree left behind.
