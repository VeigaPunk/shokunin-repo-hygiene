# ScribeProvinceProc — C3 PROVINCE.md and README text draft (round 18, wave 1)

STATUS: DONE — C3 PROVINCE.md bullet, boundary line and corpus/README.md row drafted as text only; no tree file edited.

Scope: draft text for `PROVINCE.md` (work-surface bullet, boundary line) and the frontier/core row for `corpus/README.md`. Text lives in this report only. No product file, fixture, knowledge entry or SKILL rule was written.

Note on "README": the repository root has no `README.md` (`ls README*` → no match). The coverage map that carries frontier and core rows is `corpus/README.md`; the row below targets that file.

## 1. Commands run (all read-only)

| # | Command / read | Result |
|---|---|---|
| 1 | read `PROVINCE.md` (whole, 121 lines) | shape: `## Owns`, `## Work surfaces`, `## Refuses`, `## Adjacency`, `## Core / Frontier / Adjacent`, round-refinement sections r13/r14/r17 |
| 2 | read `corpus/README.md` (whole) | coverage map at :36-42, `## Frontier` :44-49, r13/r14/r15/r16/r17 sections; r17 row shape at :214-216 |
| 3 | `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b5763415cc67ecff1e8fe56c58c39a6fb106d7a3:PROVINCE.md \| diff - PROVINCE.md` | `SAME_AS_BASE` (working copy equals base) |
| 4 | `ls tools/` in the lane | `souji-census.sh`, `souji-verify.sh`, `souji-landing-gate.py`, `souji-quarantine.sh`, `souji-repo-structure.sh`, `souji-seat-audit.py`, … |
| 5 | `ls tools/souji-proc-census.sh` | **No such file** (`cannot access`). It is not landed in the tree at b576341. |
| 6 | `wc -l census/round-18/leaked-procs-before-1631.txt` | 58 lines (matches the "58 processes" host evidence in C1/C3) |
| 7 | `head -5` of the same file, `cut -c1-200` | rows are `pid ppid pgid age… argv`; argv paths name `/var/tmp/r15-census-config.*/unsafe-repos/r-inc-fifo` and `/var/tmp/souji-r1[67]-matrix.*/pre-harm/...` (scratch paths of fixtures, since removed). Only path shapes were read; no credential-shaped argv appears in the 5 rows shown |
| 8 | `grep -n -i "process\|kagi\|signal" SKILL.md` | :2 anti-trigger, :58 colocated quarantine rule, :67 credentials → kagi. No process-signal rule exists in SKILL.md today |
| 9 | `grep -n "^## \|^### " PROVINCE.md` | section list above |

Tools installed or updated: none. No pacman transaction, no `uv tool` install, nothing added to `~/.local/bin`.

## 2. Draft text

### 2a. Work-surface bullet — insert in `## Work surfaces (resolve and re-verify each round)` after the jj-colocated bullet (after current line 30, before `## Refuses`)

```
- Process residue (r18, candidate — admission pending the non-author closure;
  tool `tools/souji-proc-census.sh`, gate: the r18 process-census fixture
  `tests/fixtures/<r18-proc-census>.sh`, path fixed when it lands): own-uid
  processes (`/proc/<pid>` owned by the current uid) whose cwd is deleted, or
  whose argv names a `/var/tmp`, `/tmp` or `/dev/shm` path that no longer
  exists. The tool is read-only and dry-run only; it reports pid, ppid, pgid,
  age, state/wchan, reason and a redacted, truncated command. Residue rows are
  evidence for the operator. They are never a removal receipt and never a
  basis for deleting an artifact.
```

Placeholder note for L1: replace `<r18-proc-census>` with the real fixture path before the bullet lands. The bullet is a scanned pointer under C2 (`LG-DANGLING-PTR` covers `PROVINCE.md`), so it MUST land in the same commit as `tools/souji-proc-census.sh` and the fixture. Landing the bullet first leaves a dangling pointer at REV.

### 2b. Boundary line — insert in `## Refuses` as one new bullet (after the "Operator config" bullet, before "Any artifact whose owning lane…")

```
- Signalling any process (kill, pkill, killpg, or a kill(2) equivalent). The
  process census is list-only; signalling a residue process is
  operator-approved and never a souji action. Command text is redacted:
  credential-shaped argv (tokens, `--password`-style flags, URL userinfo,
  `op://` refs) is kagi-shokunin's province, and the census cites pid and
  path only. It never reads `/proc/<pid>/environ`.
```

### 2c. Adjacency amendment (required, see finding F1)

Replace the first sentence of the mori bullet at `## Adjacency` (current :46-47):

Current:
```
- mori-shokunin observes fleet health and reports; souji acts on artifacts
  and never on processes. Complementary.
```

Proposed:
```
- mori-shokunin observes fleet health and reports; souji acts on artifacts
  and never signals processes. Its process-residue census is list-only
  evidence (see `## Work surfaces`) and may be cited by mori; neither
  lane acts on the other's surface. Complementary.
```

### 2d. Core / frontier shape — `PROVINCE.md` round-18 refinement (append after `## Round 17 boundary refinement`)

```
## Round 18 boundary refinement (process residue, list-only)

Core now includes (candidate; admission pending the non-author closure) the
bounded process-residue census (`tools/souji-proc-census.sh`, entry
`corpus/knowledge/process-residue-list-only.md`, matching SKILL rule, fixture
named in `## Work surfaces`). It is read-only, dry-run only, own-uid only, and
never signals. Its residue rows are not removal receipts for artifacts. Signalling
stays operator-approved and sits in `## Refuses`. Processes that belong to another
uid, or that are alive and not residue-classified, remain frontier; so does the
signal-authority question.
```

### 2e. `corpus/README.md` row and frontier line

Coverage-map row (insert after the r17 F1-jj row at :216, in the `## Round 18` section that mirrors the r17 section shape):

```
## Round 18 — process residue, list-only (candidate Core; frontier stays)

Landing condition (index rule at :3-4): this section and its Core marking land
only in the same commit as `knowledge/process-residue-list-only.md`, the SKILL
process rule and `tools/souji-proc-census.sh`. Otherwise ship the frontier row
below only.

| ground | status | entries / runnable evidence |
|---|---|---|
| C3 process residue (own-uid, cwd deleted or scratch argv path gone) | Core (candidate, admission pending closure): read-only dry-run census; list-only, signalling operator-approved, credential-shaped argv redacted; residue is never a removal receipt | `knowledge/process-residue-list-only.md`; `../tools/souji-proc-census.sh`; `../tests/fixtures/<r18-proc-census>.sh`; `../census/round-18/` (proc-census verification, red arm 0 blocked processes left) |
```

Frontier line (append under `### Frontier (r18)` if the Core row is not admitted):

```
- process residue beyond own-uid and beyond the scratch-path list (live orphans
  with a living parent, other uids, process-group cleanup authority) — frontier;
  signalling authority is operator-owned and not claimed by any round.
```

Index-row rule for the r18 measurement: count `S064+` rows opened this round in `corpus/SOURCES.md`; do not count them as knowledge. Admitted knowledge stays at its pre-round count until the knowledge entry is admitted.

## 3. Findings

**F1 — the adjacency line contradicts the new surface (must fix; verdict: fails as written).**
`PROVINCE.md:46-47` says "souji acts on artifacts and never on processes." C3 adds a process reader. Without amendment (2c), the new bullet and the old adjacency sentence disagree in the same file. Smallest fix: 2c above.

**F2 — the C3 work-surface bullet dangles until the tool lands (verdict: holds only if landed together).**
`tools/souji-proc-census.sh` does not exist in the tree (command 5). `PROVINCE.md` is scanned by the r18 landing gate (C2 `LG-DANGLING-PTR`; `PROVINCE.md` is in the scanned list). Any token `tools/souji-proc-census.sh` or `tests/fixtures/…` that resolves to nothing at REV is a finding. Smallest fix: land 2a in the same commit as the tool and fixture; keep the placeholder fixture path out of the commit until its real name exists.

**F3 — the refusal line needs a stated home (verdict: holds with 2b).**
`## Refuses` currently has no process row, so signalling is nowhere refused in the authority text. 2b places it there. The "never on processes" sentence at Adjacency and the Refuses line must match: F1 fixes the first, 2b the second.

**F4 — the redaction clause names kagi's province without a credential reader (verdict: holds).**
The boundary cites pid and path only and never reads `/proc/<pid>/environ` (matches PROBE RULE and `## Refuses` credential bullet, `PROVINCE.md:36-37`). This does not add a credential-scanning claim. No credential content was read in this draft (command 7 read path shapes only).

**F5 — `corpus/README.md` is the only coverage-map file; the request's "README" is that file (verdict: holds).**
No root README exists. The row in 2e goes to `corpus/README.md` at the r17 section shape (:205-216). The row names `../census/round-18/` evidence paths that do not exist yet, so the same landing-condition rule as r17 (`corpus/README.md` :3-4) applies: no Core marking until the evidence and knowledge entry land.

**F6 — coverage axis counts (for the scribe's evidence section; advisory).**
Residue classes governed before r18: 0 (SKILL and PROVINCE have no process rule; command 8). Proposed after: 2 classes at the Core candidate level (own-uid cwd-deleted; own-uid argv scratch path gone) plus 1 frontier class (beyond own-uid / live orphans). Host evidence for the first class: 58 rows in `census/round-18/leaked-procs-before-1631.txt` (command 6). The orphan counter comparison (census vs an independent counter) is not run in this seat and stays unmeasured.

## 4. Out of scope (not drafted)

- Knowledge entry `knowledge/process-residue-list-only.md` and SKILL rule text: not drafted here (C3 scribes own them).
- QUALITY.md and SOURCES.md rows: not drafted.
- No test or fixture run; the verification commands belong to the main agent after integration.

## 5. Files touched

- Written: this report only.
- Not written: `PROVINCE.md`, `corpus/README.md`, tools, tests, census, `.ufo/state`, `.ufo/watchdog.log`, `census/operator-sweep-20261019/` (never opened), fleet repo.
