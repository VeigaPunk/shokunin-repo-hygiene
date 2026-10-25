# ExecKnowledgeWriter — round-27 w1 report

## Status
STATUS: PASS — draft knowledge entry `origin-record-writer-r27.md` delivered at `.ufo/waves/round-27/w1/origin-record-writer-r27.md`, re-grounded at GLib tag 2.84.0 fetched this run; Gate has 7 ADMIT quoted rows + 1 REJECT (staged S119 zh-Hans row, per the routed round-26 lesson).

## Evidence
- Lane base: `git rev-parse HEAD` → `e78ac7c4837b81b634db4a927605a751a7f006ba` (matches preregistration base; no writes to repo outside w1/).
- Frozen counters at base, observed: `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → `132`; `grep -rlE '^ground: F4' corpus/knowledge/ | wc -l` → `2` (quarantine-origin-record-fields-r24.md, quarantine-staging-no-copy-r23.md). Consistent with preregistration before=132/2.
- Snapshot fetched this run: `curl -fsSL -o glocalfile.c 'https://raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c'` → 83,391 bytes; `sha256sum` → `66b588c495e1d7e036b02c5dc919ab466eace6f578ed38763a49b168d2d47e4f`. Also fetched `glib/gfileutils.c` (86,909 bytes, sha256 `5161ae435ee57448c280323de064e1d6d62dc1ba3ba2771c5982b913888dfad5`) for the sibling mechanism entry's install record.
- Quote verification: `read` of `glocalfile.c:2250-2395` shows lines 2256 (`get_unique_filename`), 2261 (`g_open` O_CREAT|O_EXCL|O_CLOEXEC), 2281 (`g_close`), 2288/2363/2387 (`g_unlink (infofile);`), 2331-2333 (ordering comment), 2340 (URI-escape), 2354-2355 (`[Trash Info]\nPath=%s\nDeletionDate=%s\n`), 2359-2361 (`g_file_set_contents_full` CONSISTENT|ONLY_EXISTING), 2383 (`g_rename`) — all verbatim in fetched bytes; every Gate quote ≤25 words.
- Staged row S152 (`merge/souji/SOURCES.append.md:50`) verified against fetched bytes; its line refs match.
- Tooling: no installs performed (RULES.md read; curl/coreutils already present).

## Findings
1. Delivery: `.ufo/waves/round-27/w1/origin-record-writer-r27.md` (6587 bytes) — front matter `source: S152` with GLib glocalfile.c URL at tag 2.84.0; `verified-at: 2026-10-25`; `recheck: 365d`; `ground: F4`. Body grounded only in fetched bytes/located quotes; no universal clauses; no credential material.
2. Gate: 7 ADMIT rows (create-exclusive, unique-name loop, escape, fixed content, before-move ordering, payload rename, three rollback sites) + 1 REJECT: staged S119 (git-fetch(1) zh-Hans edition, `SOURCES.append.md:17`) — re-staged mined with no sha256-pinned snapshot/decision-time quote; round-26 routed lesson (`corpus/lessons/round-26-verifier-spotcheck.md:47`, `round-26.md` item 2) requires the pin on re-adoption; corroboration-only, no claim-surface loss beyond S109.
3. `census/round-27/sources/` does not exist at base; entry cites sha256 values; L1 to deposit snapshots there at install.
4. Pre-existing uncommitted lane worktree changes at base under `.ufo/waves/round-26/w1/` (`M` CritAmendNeed.md, ExecLandingCheck.md, LabGitVersion.md, ScribeQ58Note.md, SimpCounterCheck.md) — matches round-26 routed defect #1; untouched by me; C3's leftover check should treat as pre-existing.

## Attack log
None. No counter/predicate/target/case anomalies observed; frozen before-state reproduced exactly.
