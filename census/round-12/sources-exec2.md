# r12 SOURCES executor (re-dispatch) — census output

Author: W2RoundSouji-8.R12SourcesExec2 (L2, read-only); transcribed verbatim by the L1 from its final output (session-scoped `agent://W2RoundSouji-8.R12SourcesExec2`; this committed copy is the durable form). 2026-10-19.

## SOURCES gate (souji r12): `corpus/SOURCES.md` and `census/round-12/sources-gate.md` written

I opened all 30 ART rows this session and wrote every one, so **no rows are omitted**. For each source I either fetched it to `/var/tmp/souji-r12-MvtJYK/` or reused a sibling copy only after a byte check against the canonical source (`cmp` against the raw URL at a named tag or commit, or `zcat` of the installed man page). I also added S031 (own-work), S032 (rejected git-filter-branch(1) § WARNING) and S033 (gitrepository-layout(5)). Nothing was committed and I wrote nothing outside the two target files and my mktemp dir.

**Rows: 33.**

| | Count | Rows |
|---|---|---|
| Tier A | 29 | |
| Tier B | 3 | S014 (GitLab blog, community), S017 (rmlint Cautions), S029 (SRE book) |
| Tier C | 1 | S030 |
| mined | 18 | S001–S004, S009, S010, S016–S025, S029, S031 |
| queued | 13 | S005–S008, S011–S015, S026–S028, S033 |
| rejected | 2 | S030, S032 |

All five K-entry files already exist, and their `source:` headers cite the same S-ids as the plan. ART's `watch` statuses became `queued`, or `mined` for S010.

**Where ART differs (each recorded in the gate file):**
- **S017:** I moved it from tier A to B. It is the rmlint project describing other tools' failures, which makes it secondary for those tools.
- **S021:** the group abort happens only when `config.modified_before` is set (dedupe.rs:843-847). Non-regular files and files whose length changed are skipped one at a time.
- **S029:** "lazy deletion" is another name for soft deletion in developer APIs, not a second layer behind it.
- **S009:** the task table entries are `SCHEDULED | MANUAL`; the task is at gc.c:379-389 and the condition at :391-427. These are the reviewer's corrections.
- **S004:** `--drop-filtered` exists only at v2.56.0; the host runs 2.55.0.
- **S008:** I couldn't re-check ART's "(2.52+)", so I left it out of the row.

The search log has three notes: the re-open sweep of the 30 ART rows, the revision pinning, and a negative sweep showing gitrepository-layout(5) has no `worktrees/<id>/index` entry. Eleven ART leads stay under Leads (unopened).

**Census output**, run with `bash -c` from the lane root (`/home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/souji-shokunin`):
```
# rows
33
# malformed
0
# tier
A=29 B=3 C=1 
# status
mined=18 queued=13 rejected=2 
# duplicates
# enum
# used-by missing
missing: corpus/lessons/round-12.md
```
- Duplicates and enum/tier-inflation printed nothing.
- The only missing used-by path is S031's `corpus/lessons/round-12.md`. The L1 writes that file; it doesn't exist yet.
- An extra check found 0 escaped `\|` in `SOURCES.md`.
