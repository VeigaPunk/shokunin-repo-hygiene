# SwarmConnector28 — sibling-overlap scan of round-32 landed items (a2w1)

## Status

STATUS: PASS — the three landed subjects (C3 mtime-clock entry + row S223; C2 TMPDIR/bwrap private-/var/tmp repairs) have zero contested scope in the 960 sibling-lane scoped files; all 171 keyword hits are non-overlapping classes, enumerated in the delivery file.

## Evidence

- Frozen contract read first: `census/round-32/records/preregistration.txt` (committed 3ec84fc; landings 98e5203 C2, a92e1aa C3+A1, 9e8982b C1; tip at scan 4e56c48, `git -C souji-shokunin log --oneline -8 master`).
- Landed subjects opened this run: `corpus/knowledge/jj-abandoned-object-mtime-clock.md` (full), `corpus/SOURCES.md:168` (S223 row), `git show 98e5203 -- tests/fixtures/r20-audit-contract.py` (the bwrap `--bind <tmpdir> /var/tmp` re-exec pattern).
- Sweep (run 2026-10-26, cwd `/home/vgpnk/Projects/shokunin`, souji-shokunin excluded): `grep -i -n -E 'cruft|mtimes|pruneExpire|cruftPacks|gitformat-pack|bwrap|private /var/tmp' */PROVINCE.md */SKILL.md */corpus/README.md */corpus/SOURCES.md */corpus/knowledge/*.md` over 20 sibling lanes, 960 files (PROVINCE 20, SKILL 18, corpus/README 20, corpus/SOURCES 20, corpus/knowledge/*.md 882; `ok` and `research` hold none). Case-sensitive pass identical.
- Per-keyword sibling counts (sum of `grep -i -c` over the same set): cruft 0, gitformat-pack 0, pruneExpire 0, cruftPacks 0, `private /var/tmp` 0, mtimes 90 lines/52 files, bwrap 81 lines/22 files.
- Supplementary probes: literal `/var/tmp` (kaidoku/kotodama/tsukuroi use it only as a historical scratch location, e.g. `kaidoku-shokunin/corpus/knowledge/2026-10-19-arc3-r1-evm-real-solc.md:7` "mkdir -p /var/tmp/cr2-recheck && TMPDIR=/var/tmp/cr2-recheck npx"); `git gc` + `unreachable` domain check — only `kumitate-shokunin/corpus/knowledge/agent-isolation-substrates.md:241` ("history after a source history rewrite plus `git gc --prune=now`"), which manufactures unreachable state for an isolation demo.
- Verbatim quotes copied from bytes opened this run (≤25 words, no pipe): tameshi `corpus/knowledge/guard-kill-closure.md:129` — "The probes run in the bwrap envelope in `defect-probes.py:4-14`, with `env -i`, a private /tmp, and isolated PID and network namespaces."; kengaku `SKILL.md:608` — "needs `/usr/bin/bwrap` and is the only registry row with a runtime cost outside its own temp dir"; mori `corpus/knowledge/lane-silence-r2.md:128` — "Siblings commit into these trees and a checkout's mtimes move"; kumitate `corpus/knowledge/agent-isolation-substrates.md:164` — "run untrusted or generated code (counters, controls)" under `bwrap --unshare-all --die-with-parent --new-session`.
- Tool defect worked around and reported: mounted `grep` device returns false "No matches found" for mid-path star globs (reproduced 3x against known-hit bytes); filed at `xd://report_issue`, then used `grep(1)` over the identical file set.

## Findings

1. C3 entry vocabulary is fleet-unique in scope: `cruft`, `cruftPacks`, `pruneExpire`, `gitformat-pack` — zero sibling hits across 960 files. Location: sweep counts above; landed entry `corpus/knowledge/jj-abandoned-object-mtime-clock.md`.
2. The 90 sibling `mtimes` hits (52 files, enumeration in delivery) are all filesystem-timestamp evidence class — config/cache/socket/checkout mtimes — none about git object mtimes or pack sidecars. Nearest git neighbours (mori `lane-silence-r2.md:128,147`, `silence-cutover-r3.md:138`) concern checkout-attribution hygiene, the opposite concern. Not overlap.
3. Row S223 has no sibling SOURCES counterpart; sibling bubblewrap rows (kumitate S069/S070/S095, tameshi S093/S267) are a different document. Not overlap.
4. The 81 sibling `bwrap` hits (22 files, enumeration in delivery) are sandbox-confinement of untrusted execution (unshare/ro-bind/tmpfs-`/tmp`/`--clearenv`); the C2 landed pattern is bind-target redirection of `/var/tmp` into TMPDIR inside souji's own r20 fixtures — shared tool, disjoint purpose and target. `private /var/tmp` and any `/var/tmp` bind target: zero sibling hits. Not overlap.
5. Bookkeeping observation only: kengaku's cross-lane bwrap map (`kengaku-shokunin/PROVINCE.md:318-332`) predates r32 and names no souji row; recording souji's r20 pattern there is kengaku's own choice. Contested scope: none.

## Attack log

Not an attack item — connector scan; no counter/gameability claim. (Tooling note: the `grep` device glob defect above was reported, not attacked.)

## Deliveries

- `.ufo/waves/round-32/a2w1/deliver-sibling-overlap-w2.md` — full scan: method, keyword table, per-cluster findings with quotes, per-hit lane/file:line enumeration, contested-scope verdict.
- `.ufo/waves/round-32/a2w1/SwarmConnector28.md` — this report.
