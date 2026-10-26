# SwarmScribe14 — round-30 lesson `## Gate` draft (C3 F1 keep-ref expiry)

## Status

STATUS: PASS — `## Gate` drafted at `.ufo/waves/round-30/w1/deliver-lesson-gate.md` with the round-29 table shape: 4 source decisions (2 ADMIT new row, 2 `no new row` backed by the registry rows that already hold those scopes), 1 entry ADMIT row, 5 per-entry REJECT rows for the staged F1 package, the Q60 line, and the `### SOURCES touched-row log (old → new)` skeleton. All 17 located quotes were re-found verbatim in bytes opened this run (4-25 words, no pipe); all four sources were re-fetched independently and are `cmp`-identical to the wave snapshots. No lane byte was edited; no counter, gate, fixture or jj run was executed (the C3 measurement is another seat's artifact, cited as such).

## Evidence

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, read-only except the two files named under Deliveries. Lane tip read: `df6afe817d096e4ad71ba2b9cc21a83f126eb658` (base `9420341d…`, prereg `d4928ec…`, controls `bae103c…`); `git status --porcelain` → one untracked entry, `?? corpus/lessons/round-30.md`.

| # | command | output excerpt | revision |
|---|---|---|---|
| 1 | read of the frozen contract | `census/round-30/records/preregistration.txt` lines 1-14 (C1/C2/C3, kill rules, fixture contract D1-D7) read whole with `:raw` before any drafting | `d4928ec86b667e3d1ed0adb07fb088e500cf1631` |
| 2 | independent re-fetch, scratch `$TMPDIR` | `curl -fsSL -m 60` → `200 154561 cli`, `200 102068 backend`, `200 3334 oplog`, `200 6744 gitgc`; sha256 `b3306943…333554`, `95147270…d86c69`, `2a48dab8…09ce18`, `e3dbc408…afba8c` | upstream tags `v0.45.1`, `v2.56.0` |
| 3 | `cmp` scratch vs `.ufo/waves/round-30/w1/sources/` | `identical` ×4 (cli-reference@.md.snap, git_backend.rs, operation-log.md, git-gc.adoc) | wave-1 snapshots |
| 4 | `sha256sum -c SHA256SUMS` (cwd `sources/`) | `cli-reference@.md.snap: OK`, `git_backend.rs: OK`, `operation-log.md: OK`, `git-gc.adoc: OK`, `cli-reference.md: OK` | wave-1 snapshots |
| 5 | quote check over the delivery (`python3 -B`, whitespace-normalised substring match) | `SUMMARY spans=17 bad=0`; every span 4-25 words, no pipe | `deliver-lesson-gate.md` |
| 6 | registry sweep for the two new candidates | `grep -c 'cli-reference' corpus/SOURCES.md` → `0`; `grep -c 'operation-log' corpus/SOURCES.md` → `0`; `grep -c 'operation log' corpus/SOURCES.md` → `0` | `df6afe8` |
| 7 | overlap sweep for the other two candidates | `corpus/SOURCES.md:75` S054 scope `creation and removal of refs/jj/keep/* in jj 0.45.1 …`; `:84` S063 scope `which refs keep objects alive during gc`; `:23` S002 git-gc grace periods | `df6afe8` |
| 8 | operation-log page vs `op abandon` | `grep -c 'abandon' sources/operation-log.md` → `0` | `v0.45.1` bytes |
| 9 | L5 regex behaviour on nested quotes | `re.findall(r'"([^"]{2,400})"', '"Only the string "now" can be passed to this parameter."')` → `['Only the string ', ' can be passed to this parameter.']`; first span 3 words → `4 <= len(q.split()) <= 25` False | `census/round-30/c3-counter.py:110-111` |
| 10 | fixture coverage of the C3 counter | `grep -n 'fixture\|r30-jj-keep-expiry' census/round-30/c3-counter.py` → no match (rc 1); leg list L1-L9 read at `:9-20`; `ls tests/fixtures/r30*` → `No such file or directory` | `df6afe8` |
| 11 | landing prerequisites | `ls census/round-30/sources` → `No such file or directory`; `census/round-30/records/` holds no `jj-keep-expiry-run.txt` | `df6afe8` |
| 12 | table shape of the delivery | every `|` line splits to 7 fields (6 columns + edges): 19/19 `OK` | `deliver-lesson-gate.md` |

Receipt: `.ufo/waves/round-30/w1/receipt-SwarmScribe14-quote-check.txt` (4 sections: re-fetch digests, `cmp`, `sha256sum -c`, quote check). Scratch `/fast/scratch/hyaku/souji-r30/SwarmScribe14/` removed after the receipt was written; no git repo was created, no `jj` was run, no tool installed.

## Findings

1. **Two of the four planned C3 source candidates are already grounded; the delivery records `no new row` for them.** `corpus/SOURCES.md:75` (S054: this file at this tag, scope “creation and removal of `refs/jj/keep/*` in jj 0.45.1 … not later releases”, locator `:900-953 recreate_no_gc_refs, :1558-1564 gc`) covers the candidate the wave spec calls S221; `corpus/SOURCES.md:84` (S063) plus `:23` (S002, same manual) cover the candidate called S223. Consequence for the L1: the entry's `source:` line must cite S054 and S063, the two genuinely new rows are S220 (CLI reference) and S221 (operation-log), and any landing that keeps all four rows must give the extra two a scope their existing row does not claim. Recorded in the delivery's renumber note, not applied to the registry.

2. **`docs/operation-log.md` does not document `jj op abandon`.** `grep -c 'abandon' sources/operation-log.md` → `0`; the lever text is in the CLI reference snapshot (`:2415`, `:3793`). The row is therefore cited only for what an operation's view records (Git ref positions, `:8-9`), and the step from “abandon removes the view” to “the keep ref goes” is `[INFERENCE]` across the two rows — marked as such in the delivery's S222 reason cell. Snapshot seat reached the same selection independently (`deliver-c3-anchor-lines.md`, item 3).

3. **C3 leg L5 cannot accept the CLI doc's `"now"` sentence.** The quote regex `"([^"]{2,400})"` splits on the inner quotes and yields a 3-word span (`Only the string `), which fails `4 <= len(q.split()) <= 25`. The entry's `## Gate` must quote the 2-week sentence (`:3801`, 13 words) or another span without nested double quotes. Location: `census/round-30/c3-counter.py:110-111`. The lesson Gate is unaffected (it uses curly delimiters).

4. **C3's counter has no leg for the fixture the preregistration names.** Prereg line 9 requires `tests/fixtures/r30-jj-keep-expiry.sh`; `census/round-30/c3-counter.py` legs L1-L9 never read that path (`grep` → no match), and no such file exists at the tip (only the wave delivery `deliver-r30-jj-keep-expiry.sh`). The target `SUMMARY legs=9 fail=0 f1_entries=3` is therefore reachable without the fixture. Counter-coverage gap for the L1's attack log; this seat does not amend frozen text.

5. **C3 L6 binds an S-id to *a* registry row, not to the right one.** `missing` only checks row existence and `fresh` only checks one cited row opened today; a placeholder-vs-final renumber shift passes. The URL clause catches a crossed citation only when the entry's Gate carries the URL (`bad6` compares Gate URLs against cited rows' source cells, `c3-counter.py:112-117`) — and L4's `snapshot:` lines do carry paths, not necessarily the raw URLs. Combined with finding 1 this is a live risk this round, because the wave-1 entry prompt told the entry seat to use placeholders S220-S223.

6. **Landing prerequisites for C3 are unmet at the tip, as expected mid-wave.** `census/round-30/sources/` does not exist (snapshots still live only under `.ufo/waves/round-30/w1/sources/`, which is gitignored via `.gitignore:1`) and `census/round-30/records/jj-keep-expiry-run.txt` is not committed; L4 and L8 both read blobs at `--rev`, so both fail until the L1 lands them. The wave originals and their digests are complete and `sha256sum -c` clean.

7. **Package source ids are not portable, per entry.** The staged F1 entries cite package-local ids that collide with this lane's registry — `git-grace-period-semantics-r34.md:1-4` uses S218-S220 where the lane holds S218 link(2) (`SOURCES.md:163`), S219 cmp(1) (`:164`) and, after this round, S220 the jj CLI reference. Each reject row carries its own such detail rather than a grouped one (round-29 closure routed defect D4, `corpus/lessons/round-29.md:17`, corrected for r29 by `SwarmScribe16`); every staged entry is cited by filename plus line, never by package id alone.

8. **The staged F1 set is worktree-prune ground, not keep-ref ground — with one trap.** `git-grace-period-at-release-r35.md:30-31` states “`gc.pruneExpire` defaults to **2 weeks** and governs unreachable loose **objects**”, the same number as jj's keep-ref threshold; its own next clause separates `gc.worktreePruneExpire` at `3.months.ago` for registrations. The delivery's r35 cell names that confusion explicitly so a reader cannot take the file as the source of the jj threshold.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w1/deliver-lesson-gate.md` — the `## Gate` block (preamble, 11-row table, anchor cross-check line, D4 line, renumber note, Q60 line, `### SOURCES touched-row log (old → new)` skeleton).
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w1/receipt-SwarmScribe14-quote-check.txt` — re-fetch digests, `cmp` results, `sha256sum -c` output, quote check.
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w1/SwarmScribe14.md` — this report.
