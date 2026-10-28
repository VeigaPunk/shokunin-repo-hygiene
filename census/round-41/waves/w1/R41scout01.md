# R41scout01 — feasibility recon of the 19 refusal sites (souji round 41, wave 1)

Seat: R41scout01 (scout, leaf — no subagents). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin.
Scratch: /fast/scratch/hyaku/souji-r41/R41scout01 (deleted before yield; receipts copied here first).
Question assigned: for each trigger in census/round-41/c3-sites.tsv, is it feasible on THIS host as the unprivileged uid, and does the observed errno/class match the table?

## Verdict

ALL 19 sites / 21 probe ids (P01..P19 incl. P02a/P02b, P10a/P10b) are FEASIBLE on this host as uid 1000, and every observed class and errno matches c3-sites.tsv. No trigger differs from the table. Fixture recipes that matter for the C3 author are listed under "Fixture notes".

## Environment (observed)

- uid 1000 (vgpnk) — unprivileged; python 3.14.8; git 2.56.0.
- Pinned tool sha256: b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6 — matches the preregistration byte-for-byte.
- Filesystems: /fast/scratch (all fixtures and every experiment) = xfs; /tmp = xfs; lane = btrfs; /dev/null = tmpfs (devtmpfs-style char device, S_ISCHR=True observed).
- No tool installed or upgraded (python3 and git already present) — nothing to record under the 2026-10-19 tooling authorization.

## Commands run

```
mkdir -p /fast/scratch/hyaku/souji-r41/R41scout01
TMPDIR=/fast/scratch/hyaku/souji-r41/R41scout01/tmp python3 \
  /fast/scratch/hyaku/souji-r41/R41scout01/recon41.py
```

Harness: .ufo/waves/round-41/w1/R41scout01/recon41.py (copy of the exact script). Full transcript: .ufo/waves/round-41/w1/R41scout01/recon-log.txt (every line quoted below is from it). Exp A probes the raw syscalls; Exp B runs the pinned tool once per probe id plus one pristine baseline (exit 0, `SUMMARY ... drift_rows=0 unreachable=0`, json written) to prove the harness itself is sound.

## Exp A — raw errno probes (xfs, observed)

```
A0 open(missing, O_RDONLY|O_NONBLOCK)      -> errno=2(ENOENT)
A1 open(chmod000, O_RDONLY|O_NONBLOCK)     -> errno=13(EACCES)
A2 open(self-symlink, O_RDONLY|O_NONBLOCK) -> errno=40(ELOOP)
A3 open(fifo, O_WRONLY|O_CREAT|O_NOFOLLOW|O_NONBLOCK) -> errno=6(ENXIO)
A4 open(dir, O_RDONLY|O_NONBLOCK)          -> OPENS; S_ISREG=False
A5 open(dir, O_WRONLY|O_CREAT|O_NOFOLLOW|O_NONBLOCK)  -> errno=21(EISDIR)
A6 open(/dev/null, O_WRONLY|...)           -> OPENS; S_ISREG=False S_ISCHR=True
A7 st_nlink of hardlinked pair             -> 2
A8 open(locked/out.json, O_WRONLY|O_CREAT|O_NOFOLLOW|O_NONBLOCK) -> errno=13(EACCES)
A9 realpath(root/../sibling) inside=False
```

## Exp B — pinned tool end-to-end, observed REFUSAL lines (exit 2 each)

```
S01  P01  REFUSAL RECORD-MALFORMED: .../S01/absent.rec is not a regular file
S02a P02a REFUSAL RECORD-MISSING: [Errno 13] Permission denied: '.../S02a/rec.txt'
S02b P02b REFUSAL RECORD-MISSING: [Errno 40] Too many levels of symbolic links: '.../S02b/rec.txt'
S03  P03  REFUSAL RECORD-MALFORMED: .../S03/recdir is not a regular file
S04  P04  REFUSAL RECORD-MALFORMED: line 2 duplicates alpha
S05  P05  REFUSAL RECORD-MALFORMED: line 3 does not match the census schema
S06  P06  REFUSAL RECORD-EMPTY: no REPO rows in .../S06/rec.txt
S07  P07  REFUSAL RECORD-MALFORMED: TOTAL repos=2 but 1 REPO rows
S08  P08  REFUSAL RECORD-MALFORMED: TOTAL regs=99 but REPO rows sum to 1
S09  P09  REFUSAL RECORD-MALFORMED: TOTAL prunable=7 but REPO rows sum to 0
S10a P10a REFUSAL JSON-NOT-REGULAR: .../S10a/outside/pipe.fifo is not a regular file
S10b P10b REFUSAL JSON-NOT-REGULAR: .../S10b/outside/adir is not a regular file
S11  P11  REFUSAL JSON-NOT-REGULAR: /dev/null is not a regular file
S12  P12  REFUSAL USAGE: --root .../notadir.txt is not a directory
S13  P13  REFUSAL RECORD-OUTSIDE-ROOT: ../sibling resolves outside .../S13/root
S14  P14  REFUSAL RECORD-OUTSIDE-ROOT: linked gitdir resolves outside .../S14/root
S15  P15  REFUSAL JSON-IS-RECORD: .../S15/rec.txt is the record file
S16  P16  REFUSAL JSON-INSIDE-MEASURED-TREE: .../root/alpha/inside.json is under .../S16/root
S17  P17  REFUSAL JSON-HARDLINKED: .../outside/shared.txt has 2 links
S18  P18  REFUSAL JSON-UNWRITABLE: [Errno 13] Permission denied: 'out.json'
S19  P19  REFUSAL USAGE: --timeout must be >= 1
```

Assigned triggers, individually: chmod 000 record → EACCES observed, class RECORD-MISSING (table: match). Self-referential symlink record → ELOOP, RECORD-MISSING (match). FIFO no reader, O_WRONLY|O_CREAT|O_NOFOLLOW|O_NONBLOCK → ENXIO, JSON-NOT-REGULAR (match; no hang — returns instantly). Directory as --json → EISDIR, JSON-NOT-REGULAR (match). /dev/null as --json → opens, S_ISCHR, JSON-NOT-REGULAR (match). Two-link file → JSON-HARDLINKED, nlink=2, and the target content survived (`KEEP` preserved — ftruncate is after the nlink check) (match). Unwritable directory (mode 555, target not pre-existing) → EACCES, JSON-UNWRITABLE (match). .git file pointing outside the root → RECORD-OUTSIDE-ROOT via `git rev-parse --absolute-git-dir` (match).

## Fixture notes for the C3 author (facts from the runs)

1. S01: the record path must NOT exist; ENOENT deliberately keeps class RECORD-MALFORMED ("is not a regular file"), not RECORD-MISSING.
2. S02: chmod 000 works only because we run as uid 1000; if a probe ever runs privileged it opens fine — assert euid or expect the probe to weaken.
3. S14: the outside gitdir must be a valid gitdir. `git init outside/x.git` (non-bare) then a `.git` file pointing at `outside/x.git` FAILS: `fatal: gitfile does not point to a valid repository` (rc 128, observed in first run). Use `git init --bare outside/linked.git` (observed rev-parse rc 0 → refusal fires), or point the gitfile at a non-bare repo's `.git` subdir. If rev-parse fails, the tool silently skips the gitdir check (unreachable=1, exit 1, no refusal) — a probe must assert the REFUSAL line, not just exit != 0.
4. S17: the nlink check runs after measurement; with an ABSENT ghost row the refusal still fires (exit 2). Target content is not truncated on refusal.
5. S18: the --json file must not pre-exist inside the 555 dir — O_CREAT on an existing owned file would succeed and no refusal would fire.
6. Timing: S01–S09, S12–S16, S19 refuse BEFORE the measurement loop (no git needed); S10/S11/S17/S18 refuse AFTER it (drift lines may precede the refusal on stdout).

## Filesystem caveat

Every probe ran on xfs (/fast/scratch, /tmp). The lane itself sits on btrfs; I did not run fixtures there (seat bounds allow writes only to my scratch and report paths). Errno behavior exercised here (EACCES/ELOOP/ENXIO/EISDIR, st_nlink) is VFS-level and not expected to differ on btrfs [INFERENCE for btrfs specifically]; a C3 probe suite scored via score-candidate.sh clones into scratch (xfs), so xfs results are the representative surface.

## Evidence pointers

- Report: .ufo/waves/round-41/w1/R41scout01.md (this file)
- Full transcript: .ufo/waves/round-41/w1/R41scout01/recon-log.txt
- Harness script copy: .ufo/waves/round-41/w1/R41scout01/recon41.py
- Pinned tool read: tools/souji-worktree-drift.py (sha256 verified against preregistration)
