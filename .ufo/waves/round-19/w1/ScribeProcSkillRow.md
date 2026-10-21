STATUS: DONE — drafted the C3 SKILL.md rule and the corpus/README.md F5 row and Frontier bullet as verbatim old→new text against the worktree bytes; no lane file edited; five defects in the integrated C3 material reported for L1.

# Findings

1. **The integrated r19 text is close but has three gaps against the item.** The SKILL bullet at `SKILL.md:129-134` names the tool's behaviour and the entry, but gives no exact command, no list/nominate/reap vocabulary, no zero-signal verification route, and no fixture command. The README F5 row at `corpus/README.md:274` points to the fixture file but not to the SKILL rule, and its Frontier bullet at `:281` cites `L0 souji | round-16`, which no lane file locates (`grep` of `*.md` outside `.ufo/waves` finds it only in README itself; `corpus/LOG.md` has no ruling). The drafts below close these.
2. **Base-line r18 rows stay untouched.** `corpus/README.md:242` (F5 row, "frontier") and `:246-248` (Frontier (r18) bullet, "next: a knowledge entry") are the round-18 record. The round-19 section (`:270-288`) already supersedes them. Rewriting them would make the r18 section claim something untrue about r18. L1 applies the old→new below to the r19 section only.
3. **Counting command in the preregistration is defective.** `preregistration.txt` (C3 counting command) names `grep -c 'status: admitted' corpus/knowledge/*.md`. No file in `corpus/knowledge/` contains that string (`grep -l` returned nothing, exit 1), so the command yields 0 for every entry, before and after. Admission in this lane is the three-line header rule in `census/round-13/count-claims.py:38` (`source:`, `verified-at:`, `recheck:` first, no `## Admission status — HELD`). The entry `corpus/knowledge/process-residue-observations.md` meets that rule (lines 1-3; no HELD section). L1 should count with `count-claims.py`, not the grep; the correction paragraph at `corpus/README.md:284-288` already uses it.
4. **Entry overstates "reads only".** `corpus/knowledge/process-residue-observations.md:55-56` says the tool reads `stat`, `status`, `cmdline`, `cwd`, `fd`, `wchan` "only". The tool also reads `/proc/uptime` (`tools/souji-proc-census.sh:280`), `/proc/sys/kernel/random/boot_id` (`:288`) and lists `/proc/[0-9]*` (`:314`, `:324`). `environ` is not read (no match in the tool). The SKILL draft below states the full read set. L1 may append a correction to the entry; this seat did not edit it.
5. **Q32 and the preregistration use inconsistent read lists.** `corpus/QUALITY.md:81` (Q32) lists "stat, cmdline, cwd, fd and wchan" and omits `status`, which the tool reads at `:156`. Q33 (`:82`) supersedes the suffix and signal wording but not the read list. Not a blocker; the SKILL draft lists the full set.
6. **Reap-time constraints come from a round-18 critic, not a source.** "Never signal by pgid, sid or ppid chain" and "re-verify `(pid, starttime, boot_id)` at act time" are the lane's own design constraints from `.ufo/waves/round-18/w1/CriticC3Authority.md` (Answer 3, items 2 and 5). They are not in the S082–S085 entry and not a Q-criterion. They are included as "future reap must" language, marked as lane-derived. L1 decides whether to keep them.

# Drafts for L1 (verbatim apply; line numbers are the worktree bytes read this round)

## A. `SKILL.md` — replace lines 129-134 (the integrated r19 process-residue bullet)

Old (`SKILL.md:129-134`):
```
- **Process residue is a nomination, not a receipt** (r19, Q32–Q33): the
  census lists own-uid deleted cwd links and vanished scratch argv/fd paths;
  it never signals, never reads `environ`, redacts secret-shaped argv, and
  compares inodes when a literal live name ends in ` (deleted)`. The docs
  state the suffix only for `exe` (S076); the cwd/fd rule is fixture-carried.
  Knowledge: `corpus/knowledge/process-residue-observations.md`.
```

New:
```
- **Process residue: list, nominate, never reap** (r19, Q32–Q33; S082–S085):
  run `bash tools/souji-proc-census.sh [--prefix DIR]... [--min-age S]`. It
  lists own-uid processes whose cwd link ends in ` (deleted)` (any location)
  or whose argv/fd names a vanished path under a scratch prefix (defaults
  `/var/tmp`, `/tmp`, `/dev/shm`; `--prefix` never narrows cwd). Three tiers,
  never merged: **list** = a row, keyed by `(pid, starttime, boot_id)`;
  **nominate** = handing that row to the operator, which is neither a removal
  receipt nor a signal authorization; **reap** = any signal to a listed
  process, which no census mode performs and which needs operator approval, a
  fresh `(pid, starttime, boot_id)` check at act time, and a LOG record
  (Q32). Zero-signal rule: census mode sends no signal and reads only
  per-process `stat`, `status`, `cmdline`, `cwd`, `fd`, `wchan` plus
  `/proc/uptime` and `boot_id`, never `environ`; `--selftest` signals only
  workers it spawned, after an identity check. Verify no-signal by syscall
  trace (fixture P7), not by liveness (Q33). Lane-derived for any future reap:
  never pipe rows to `kill`/`xargs`, never signal by pgid, sid or ppid chain
  (`.ufo/waves/round-18/w1/CriticC3Authority.md`, Answer 3). Pointers: entry
  `corpus/knowledge/process-residue-observations.md`; fixture
  `bash tests/fixtures/r18-proc-census.sh --tool tools/souji-proc-census.sh`
  (P1–P19); selftest `bash tools/souji-proc-census.sh --selftest`. A literal
  live name ending in ` (deleted)` is not residue when its inode matches the
  held link (Q33).
```

Notes for L1: the r18 bullet at `SKILL.md:113` ("List residue with `bash tools/souji-proc-census.sh`; killing a listed process is the operator's call (QUALITY Q32)") is a historical lesson; leave it. The table row at `SKILL.md:200` already has the exact command and needs no change.

## B. `corpus/README.md` — F5 row, round-19 section (worktree line 274)

Old:
```
| F5 process residue | **Core for the observation surface** (outside admission pending): first admitted `knowledge/` entry, list-only, no reap authority | `knowledge/process-residue-observations.md` (S082–S085; S075/S076 rechecked); `../tools/souji-proc-census.sh`; `../tests/fixtures/r18-proc-census.sh` |
```

New:
```
| F5 process residue | **Core for the observation surface** (outside admission pending): first admitted `knowledge/` entry (6 → 7), list-only; a listed row is a nomination, never a removal receipt; no reap authority | `knowledge/process-residue-observations.md` (S082–S085; S075/S076 rechecked); SKILL rule "Process residue: list, nominate, never reap" (r19, Q32–Q33); `../tools/souji-proc-census.sh`; `../tests/fixtures/r18-proc-census.sh` |
```

## C. `corpus/README.md` — Frontier (r19) bullet (worktree line 281)

Old:
```
- F5 — reap protocol still awaits the operator ruling (L0 `souji | round-16`); the entry grants no reap authority and the listed fixture orphans remain unreaped.
```

New:
```
- F5 — the reap protocol still awaits an operator ruling; none is recorded in `corpus/LOG.md` or `corpus/` as of 2026-10-21 (the r18 wording cited "L0 `souji | round-16`", which no lane file locates). The entry grants no reap authority, and no change this round adds a reap path: the census tool has no reap mode and its only signal is its own selftest. The 58 fixture orphans listed at round-18 start were not re-observed this round (no live census run). Any future reap must re-verify `(pid, starttime, boot_id)` at act time and never signal by pgid, sid or ppid chain (`.ufo/waves/round-18/w1/CriticC3Authority.md`, Answer 3).
```

Unchanged on purpose: `corpus/README.md:242` and `:246-248` (round-18 record).

## D. Optional, for L1's judgment (not drafted as applied text)

- `corpus/knowledge/process-residue-observations.md:55-56`: an append-only correction could replace "reads … only" with the full read set in draft A (per-process list plus `/proc/uptime`, `boot_id` and the `/proc` directory listing). Not required for C3 admission; L1 decides.
- `census/round-13/count-claims.py` is the counter for "admitted"; the preregistration's grep command should be treated as superseded by the correction already appended to `preregistration.txt`.

# Evidence

- `SKILL.md:129-134` (integrated r19 bullet, read at worktree bytes); `SKILL.md:113` (base r18 bullet, unchanged in worktree); `SKILL.md:200` (`souji-proc-census` table row, base bytes and unchanged).
- `corpus/README.md:242`, `:246-248` (base r18 bytes, unchanged in worktree); `:270-288` (integrated r19 section: F5 row `:274`, Frontier (r19) `:279-281`, counting correction `:284-288`).
- `corpus/QUALITY.md:81-82` (Q32, Q33 at base; unchanged in worktree).
- `tools/souji-proc-census.sh:1-28` (header, usage, default prefixes `/var/tmp /tmp /dev/shm`, `--prefix` argv/fd only, exit codes 0/1/2); `:117`, `:156`, `:256`, `:360` (per-process reads `stat`, `status`, `cmdline`, `wchan`); `:280`, `:288`, `:314`, `:322-324` (`/proc/uptime`, `boot_id`, `/proc` listing); `:340-342` (cwd readlink and inode check); `:388-417` (selftest worker identity check and `kill -KILL -- "$pid"` only for workers that pass it).
- `tests/fixtures/r18-proc-census.sh:1-16` (case list P1–P19, P7 = no kill/tkill/tgkill/pidfd_send_signal); `:221-232` (strace trace of the tool's own run with `trace=kill,tkill,tgkill,pidfd_send_signal`).
- `corpus/knowledge/process-residue-observations.md:1-3` (header lines admitted by `count-claims.py:38`); `:55-56` ("reads … only").
- `census/round-13/count-claims.py:33-45` (admission rule, read at worktree bytes).
- `.ufo/waves/round-18/w1/CriticC3Authority.md` Answer 3 items 2 and 5 (reap re-check and no pgid/sid/ppid signalling).
- `preregistration.txt` C3 counting command (grep `status: admitted`) and its correction paragraph.
- Path checks, all present: `census/round-18/proc-agreement-final.json`, `census/round-18/proc-agreement-counterfix.json`, `census/round-18/proc-census-live-1721.tsv`, `tests/fixtures/r18-proc-census.sh`, `tools/souji-proc-census.sh`, `corpus/knowledge/process-residue-observations.md`.

# Commands run

- `read` of SKILL.md, corpus/README.md, corpus/QUALITY.md, corpus/SOURCES.md, corpus/knowledge/*.md, tools/souji-proc-census.sh, tests/fixtures/r18-proc-census.sh, census/round-13/count-claims.py (grep only), preregistration.txt, .ufo/waves/round-19/w1-spec.json (item text), .ufo/waves/round-18/w1/CriticC3Authority.md.
- `git show 3ab2c81:corpus/README.md`, `git show 3ab2c81:SKILL.md`, `git show 3ab2c81:corpus/knowledge/quarantine-same-filesystem-rename.md`, `git show 3ab2c81 --stat`, `git ls-tree -r --name-only 3ab2c81 corpus/`, `git diff 3ab2c81 -- SKILL.md corpus/...` (read-only).
- `grep` over SKILL.md, README, knowledge entries, tools and `.ufo` for F5/reap/ruling/status terms.
- No tool was run. No `--selftest`, census, or fixture was executed. No process was signalled.

# Contract compliance

- Wrote only the report at `.ufo/waves/round-19/w1/ScribeProcSkillRow.md` (lane-relative). No lane file edited; no git or jj mutation; no subagent; no `ask`.
- No network access; no `/proc/*/environ` read; no live census; no lane tool run.
- No scratch directory created; nothing to clean up.
- No tool installed or updated; the operator's tooling directive was considered and not invoked (no install needed for a text draft).
- Base `3ab2c81` bytes read where the item says base; worktree bytes read for the integrated r19 text (named by line). Integrated state was verified against the tool and fixture bytes, not accepted on trust.
- Quotes from lane files are short identifiers, not external quotations; no URL citation was needed.
