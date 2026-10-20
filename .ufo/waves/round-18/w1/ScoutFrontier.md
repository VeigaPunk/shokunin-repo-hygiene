STATUS: DONE — C1 and C2 touch Core surfaces (no F1–F4 row); C3 has no surface anywhere (opens F5); PROVINCE bullet/Refuses/adjacency/boundary and the corpus/README frontier row are drafted as text only. No tree file edited.

# ScoutFrontier — r18 claim → frontier/surface map, process-residue pre-naming audit, C3 text drafts

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`, base `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3` (short `b576341`). Round 18, wave 1. Read-only; no `jj`, no git write, no tool run beyond the listed reads/`ls-tree`/`cat-file`/`grep`/`wc`.

## 1. Exact commands run (all read-only)

| # | command | key output |
|---|---|---|
| 1 | `read corpus/README.md` (234 lines), `read PROVINCE.md` (121), `read SKILL.md` (253), `read SCORECARD.md` (114) | shapes below; r17 sections at README:205-234, PROVINCE:101-121 |
| 2 | `grep -nEi 'process\|residue\|leak\|orphan\|timeout\|watchdog\|bounded' PROVINCE.md corpus/README.md SKILL.md SCORECARD.md corpus/QUALITY.md` | PROVINCE:39,47; SKILL:70,95,98,100; no process surface anywhere |
| 3 | `grep -nEi 'F1\|F2\|F3\|F4\|frontier' PROVINCE.md corpus/README.md` | PROVINCE:56-66 (F1–F4), README:39-49 (index), README:226-234 (Frontier r17) |
| 4 | `grep -n '^## ' PROVINCE.md` | Owns:6, Work surfaces:19, Refuses:32, Adjacency:44, Core/Frontier:53, r13:78, r14:88, r17:101 |
| 5 | `git ls-tree --name-only b576341 census/round-17/` | 16 names; records are `gate-replays-4f48343.json`, `jj-receipts-4f48343.txt`, `seat-audit-r16-replay-4f48343.json` (+ `-base5fa6017`), no `ddb7347` variants |
| 6 | `git cat-file -e b576341:<path>` for `gate-replays-ddb7347.json`, `jj-receipts-ddb7347.txt`, `gate-replays-4f48343.json`, `jj-receipts-4f48343.txt`, `seat-audit-r16-replay-4f48343.json`, `census/operator-sweep-20261019`, `census/round-18/leaked-procs-before-1631.txt`, `.ufo/waves/round-17/w1/ScoutFleetJjKeep.md` | `ABSENT` for the two `ddb7347` records, `census/operator-sweep-20261019` and `census/round-18/…`; `EXISTS` for the rest |
| 7 | `for f in SKILL.md SCORECARD.md PROVINCE.md corpus/QUALITY.md corpus/README.md corpus/knowledge/jj-colocation-receipts.md LOG.md; do grep -n 'gate-replays-ddb7347\|jj-receipts-ddb7347\|seat-audit-r16-replay-ddb7347' "$f"; done` | 8 lines across 4 files (see F3) |
| 8 | `wc -l census/round-18/leaked-procs-before-1631.txt`; `grep -c` per pattern | 58 rows; `souji-census.sh` 21, `/usr/bin/git` 26 (`rev-parse` 22, ` status` 2), `stat` 2, `r-inc-fifo` 37, `d2-fifo` 7, `d2-symlink-fifo` 7, `r17-FixtureR17Census` 10, `souji-r16/preharm` 1, `souji-r16-repin` 7, `souji-r16-matrix` 8, `souji-r17-matrix` 4; 24 distinct pgid; 26 rows share ppid 1497 |
| 9 | `grep -n 'round_no' tools/souji-landing-gate.py` | `--round` parsed :1355; `evaluate(..., round_no)` :607/:1370; carry dir + lesson path derived from it :368-377/:684 |
| 10 | `python3 -c "json.load(open('census/round-17/gate-replays-expected.json'))"` (read-only) | `gate.gate_rev_arg` `5fa6017`; replay labels `r13-admitted, r14-landing, r15-landing, r16-landing, r16-precarry` — all rounds < 18 |

Verified against `SCORECARD.md:15` (r17 operability prose) and `LOG.md:862` ("21 repositories") for the R3 base, and against `corpus/lessons/round-17.md:86` for C1's routed residual.

## 2. Claim → axis → frontier row / province surface

| claim | axis | frontier row | surface it actually touches (exact anchors) |
|---|---|---|---|
| C1 census bounded reads | operability (8) | **none of F1–F4** | Core, `PROVINCE.md:17` ("Dry-run censuses and removal-list proposals for operator approval") + `:21-22` (the roots it enumerates) + `:88-100` (r14 census refusal fence / per-repo degrade). Tool card: `SKILL.md:147` (`souji-census` **probe**, verdict map) and `SKILL.md:184-186` (repeatable fleet census). Closes the routed item at `corpus/lessons/round-17.md:86` first clause and sentinel F3 (`:25`, `:60`). Counting base `SCORECARD.md:15`. |
| C2 pointer integrity | calibration (7, lowest) | **none of F1–F4** | Core evidence surface, `SKILL.md:163` (`souji-landing-gate` **gate**: finding-id list, 28-case selftest, pinned replay record) + `SCORECARD.md:47` (landing-claim gate capability, "18/18") + `corpus/QUALITY.md:64` Q25(b) ("a dangling `measured_commit` is not yet flagged by the gate: open, r17") + the index rule the lane already states at `corpus/README.md:3-4`. |
| C3 process residue | coverage (8) | **no row exists; opens F5** (F5 token unused: `grep -n 'F5' PROVINCE.md corpus/README.md` → 0) | Not in `## Owns`, not in `## Work surfaces`, not in `## Refuses`, not in any frontier row, not in SKILL, not in QUALITY. See §3. |

Two boundary notes that keep the mapping honest:

- **C1 is not F2.** F2 (`PROVINCE.md:61-63`, `SKILL.md:188+`) is the `git repo structure`/`count-objects` census; C1 is `tools/souji-census.sh` (per-repo worktrees/unpushed/dirty/scratch). Landing C1 must not mark F2 as advanced, and must not cite the F2 entry.
- **C2 is not a frontier row either.** It is the lane's own gate improving (Q25's family). The round gate's dispatch point is `evaluate()` (:607); the historical-pin condition is satisfied because every replay label is a round ≤ 16 (`r13-admitted … r16-precarry`), so a `round_no >= 18`-gated finding leaves `census/round-17/gate-replays-expected.json` verdicts unchanged.

## 3. Is process residue already named anywhere? — exact lines

Verdict: **absent as a governed surface**; it appears only as (a) a prohibition, (b) one operator action, (c) file residue, and (d) a false-positive heading.

1. `PROVINCE.md:46-47` — the only process sentence in PROVINCE, and it *negates* the surface:
   `- mori-shokunin observes fleet health and reports; souji acts on artifacts` / `and never on processes. Complementary.`
   This is a direct contradiction with a process reader unless amended (draft 4c).
2. `LOG.md:401-407` — one recorded, operator-directed action, not a lane surface:
   `Process kill (evidence-backed): 3` / `orphaned r4 `souji-vault-verify.impl-17.sh` judge-fixture processes (~9h,` / `ppid=systemd, do_wait) each stuck on `sha256sum` of a **FIFO**` / `(`wait_for_partner`); killed parents+children, freeing their /tmp world` / `dirs.`
   This is the precedent the C3 boundary must cite and must *not* turn into souji authority: the kill was operator-directed.
3. `SCORECARD.md:66` — file residue, not processes: `` `/tmp` fixture residue routed to tsukuroi/operator `` (under `## Planned`, r5). No `process` token occurs anywhere else in SCORECARD (`grep -n 'process' SCORECARD.md` → no match).
4. `corpus/lessons/round-5.md:30` — `## Process findings (recorded, no fix claimed)` uses "process" in the **round-procedure** sense (LOG append violation, claim conflict, drift). Do not cite it as a process-residue precedent.
5. `SKILL.md:95` ("orphaning a detached HEAD's commits") and `:98-100` ("quarantine residue after any timeout") are git objects and files; `:70` `.ufo/watchdog.log` is config, not a process.
6. `PROVINCE.md:39` and `SKILL.md:70` list `.ufo/state/`, `.ufo/watchdog.log` under `## Refuses`; neither is a process surface.

Host evidence (this round, exact file): `census/round-18/leaked-procs-before-1631.txt`, 58 rows / 24 distinct process groups. It is slightly broader than the claim text: besides `r15-census-config … r-inc-fifo` (37 rows) and `r17-census-hygiene … d2-fifo` (7 rows), it holds `d2-symlink-fifo` (7 rows), 10 `r17-FixtureR17Census/{a31642d,cc21683}.sh` arm rows, and r16 `preharm`/`repin`/`matrix` arm rows. `rev-parse` appears in 22 of 24 git rows; `status` in only 2. That distribution matters for F1.

## 4. Drafts (text only; L1 integrates)

### 4a. PROVINCE `## Work surfaces` bullet — insert after current line 30 (`...every receipt path is unchanged.`), before `## Refuses` (:32)

```
- Process residue of the current uid (r18, candidate — admission pending the
  non-author closure): the read-only paths `/proc/<pid>/stat`, `cmdline`,
  `cwd` and `wchan`, for a process whose cwd is deleted or whose argv names a
  path under `/var/tmp`, `/tmp` or `/dev/shm` that no longer exists.
  Enumerated by `tools/souji-proc-census.sh` (dry-run only; pid, ppid, pgid,
  age, state/wchan, reason and a redacted truncated command). A residue row
  is evidence for the operator: it is never a removal receipt and never a
  signal.
```

Landing condition: `tools/souji-proc-census.sh` must be in the same commit (C2 `LG-DANGLING-PTR` scans `PROVINCE.md`; the tool is absent at `b576341`).

### 4b. PROVINCE `## Refuses` bullet — insert after the operator-config bullet (:38-39), before :40

```
- Signalling any process souji did not start (kill, pkill, killpg or a
  kill(2) equivalent). The process-residue census is list-only; the operator
  approves and performs any signal, as the one recorded instance was
  (LOG.md:401-407). Credential-shaped argv is redacted, and
  `/proc/<pid>/environ` is never read (kagi's province, above).
```

### 4c. PROVINCE `## Adjacency` — replace :46-47 (required; otherwise 4a contradicts it)

Current:

```
- mori-shokunin observes fleet health and reports; souji acts on artifacts
  and never on processes. Complementary.
```

Replacement:

```
- mori-shokunin observes fleet health and reports; souji acts on artifacts
  and never signals a process. Its process-residue census is list-only
  evidence (see `## Work surfaces`); a kill stays operator-owned.
  Complementary.
```

### 4d. PROVINCE round-18 refinement — append after :121

```
## Round 18 boundary refinement (process residue, list-only)

A read-only process-residue census is enumerated, not authorized
(`tools/souji-proc-census.sh`): own-uid processes whose cwd is deleted or
whose argv names a vanished `/var/tmp`, `/tmp` or `/dev/shm` path are listed
with pid, ppid, pgid, age, state/wchan, reason and a redacted truncated
command. The tool is dry-run only by construction: it never signals, kills,
reparents or waits on a listed process, and a process that vanishes mid-scan
is reported as could-not-observe, not as a finding. Souji lists; the operator
approves; souji never signals (`## Refuses`). A residue row is not a removal
receipt for any artifact, and no signal authority is claimed. The one
recorded kill of such residue (LOG.md:401-407: three r4 judge-fixture
processes stuck on a FIFO `sha256sum`) was operator-directed. Residue of
other uids, live orphans with a living parent, and any group-signal policy
remain frontier (F5). This is a detect capability, not a Core receipt class,
until a knowledge entry and a SKILL rule land (`## Core / Frontier /
Adjacent`); it advances no F1–F4 row.
```

### 4e. `corpus/README.md` `## Frontier` index — insert after :49 (F4 line)

```
- F5 process residue (r18) — next: a receipt/knowledge entry, a SKILL rule
  and an independent orphan count; the census lists, the operator approves,
  souji never signals (`../tools/souji-proc-census.sh`).
```

### 4f. `corpus/README.md` round-18 section — append at EOF (after the r17 `### Frontier (r17)` list, :234)

```
## Round 18 — process residue becomes an enumerated surface (F5 opened)

Landing condition (index rule at :3-4): this section lands only in the same
commit as `../tools/souji-proc-census.sh` and
`../census/round-18/leaked-procs-before-1631.txt`; otherwise cite neither
path. C1 and C2 are Core repairs and advance no frontier row.

| ground | status | entries / runnable evidence |
|---|---|---|
| F5 process residue (edge class: hermetic-fixture leakage) | frontier, no entry: read-only detect capability acquired — own-uid processes with a deleted cwd or an argv path under a vanished `/var/tmp`, `/tmp`, `/dev/shm`; pid, ppid, pgid, age, state/wchan, reason, redacted truncated command; never signals; no receipt class, no signal authority | `../tools/souji-proc-census.sh`; `../census/round-18/leaked-procs-before-1631.txt` (58 processes in 24 process groups: 21 `souji-census.sh` parents, 26 `git` — 22 `rev-parse`, 2 ` status` — 2 `stat`, 10 r17 fixture-arm rows; families `r-inc-fifo`, `d2-fifo`, `d2-symlink-fifo`, r16 preharm/repin/matrix) |

### Frontier (r18)

- F5 — beyond the detect capability: residue of other uids, live orphans
  with a living parent, and any group-signal/kill policy stay frontier and
  operator-owned. The independent orphan counter (a second mechanism, not
  the census's own scan) is unmeasured; the before-file is one `ps`
  snapshot, so acceptance must run tool and counter back-to-back.
```

If L1 instead adopts the sibling Core-candidate shape (§F7), the table row must read `Core (candidate, admission pending closure)` **only** when `knowledge/process-residue-list-only.md`, the SKILL process rule, the tool and the fixture land in the same commit — `PROVINCE.md:56-57` makes that the precondition.

### 4g. Optional QUALITY row (only if C2 needs a criterion, not just a finding id)

```
| Q29 | Authority files cite only evidence that exists: every repo-relative
path token in SKILL.md, SCORECARD.md, PROVINCE.md, corpus/QUALITY.md,
corpus/README.md, corpus/knowledge/*.md and the round's lesson/LOG section
resolves in the tree at REV; a token resolving only in the fleet repo is
reported as `fleet`, never a finding; a deliberate non-file is exempt only
through a committed `corpus/pointer-exemptions.tsv`. |
```

## 5. Findings (advisory; smallest fix named)

**F1 — the routed r17 residual under-describes C1's class (verdict: holds; wording fix).**
`corpus/lessons/round-17.md:86` prescribes "wrap status/check-attr in `timeout`", but `census/round-18/leaked-procs-before-1631.txt` shows the block in `git … rev-parse --is-inside-work-tree` (22 rows) and only 2 ` status` rows. A status/check-attr-only timeout would not have closed the observed hang. C1's process-group watchdog is the correct, wider shape; the r18 lesson/SKILL must say the routed prescription was too narrow, or the next reader will "fix" C1 back to the narrow form. Smallest fix: one sentence in the r18 lesson's Gate/Mistakes row.

**F2 — C1/R3 counting base is contradictory and must not be inherited (verdict: fails as written).**
`SCORECARD.md:15` (r17 C1) says "live fleet paired rows identical (22 repos)", while the same row's r16 entry says "21 repos" and `LOG.md:862` says "21 repositories". R3 corrects :15; C1's own counting must derive N from its own census output and state it, not copy 21 or 22. If `census/round-17/live-fleet.json` (committed, `AT-REV`) legitimately contains 22 rows, R3's fix should say "prose 22→21" without relabelling the past record.

**F3 — C2's dangling set is larger than the two routed tokens (verdict: fails the R2 scope).**
Verified absent at `b576341` and cited in scanned files:
- `SKILL.md:163` and `:165` → `census/round-17/gate-replays-ddb7347.json` (actual record `-4f48343.json`).
- `SKILL.md:166` → `seat-audit-r16-replay-ddb7347.json` (committed: `-base5fa6017.json`, `-4f48343.json`). **Not named in the goal/closure.**
- `corpus/knowledge/jj-colocation-receipts.md:2, 44, 126` → `census/round-17/jj-receipts-ddb7347.txt`; `:148` reaches it again through `jj-receipts-{base5fa6017,ddb7347}.txt` brace expansion (actual `-4f48343.txt`).
- `corpus/README.md:216` → `../census/round-17/jj-receipts-ddb7347.txt`. **Not named in the goal/closure.**
- `LOG.md:916` → `census/round-17/gate-replays-ddb7347.json`, but that is the round-17 section, outside `--round 18`'s scan; it stays a historical dangle unless a later section cites it.
Smallest fix: repoint to the `4f48343` records (they exist) in all four files, and extend R2's checklist to `SKILL.md:166` + `corpus/README.md:216`.

**F4 — token normalization is a correctness condition for LG-DANGLING-PTR (verdict: risk, needs a stated rule).**
The r13/r17 README rows cite `../census/…`, `../tools/…`, `../tests/…` (`README.md:68, 216`). If the token test requires a literal `census/`/`tools/`/… prefix, `README.md:216` escapes and the fix looks green while the pointer still dangles. The gate must normalise leading `./`/`../` before the prefix test (`posixpath.normpath` against the citing file's directory), then classify `../../.ufo/waves/hyaku/…` (`README.md:217`) as `fleet`. Brace expansion must run before resolution or `knowledge:148` is missed.

**F5 — exemption file needs at least one real row from the current tree (verdict: holds with a starter row).**
`corpus/README.md:81` cites `census/operator-sweep-20261019/`; it is under the scanned `census/` prefix and `NOT-AT-REV` (`cat-file` verified), so the changed gate would flag it without an exemption. Starter row: `census/operator-sweep-20261019/	operator-owned, untracked, never staged`. Note the scope discrepancy: L1's 18-token sweep counted `.ufo/state`/`.ufo/watchdog.log` as deliberate-unresolved, but the stated prefix list (`census/, tests/, tools/, corpus/, .ufo/waves/`) excludes them; state which scope produced "18" or the before→after comparison measures different populations.

**F6 — every newly cited r18 path must land in the same commit (verdict: holds only with the landing rule).**
`tools/souji-proc-census.sh` and `census/round-18/leaked-procs-before-1631.txt` are both `NOT-AT-REV b576341`. `corpus/README.md:3-4` ("write the row when the file exists, not before") plus LG-DANGLING-PTR makes the C3 row/§4a bullet self-invalidating if landed first. The same applies to `.ufo/waves/round-18/**` citations in the r18 lesson: seat reports cited by path must be committed at REV (r17 precedent: `.ufo/waves/round-17/w2/SentinelCensusD2.md` is `AT-REV`).

**F7 — sibling draft divergence on C3's status (verdict: partial; L1 decides).**
`.ufo/waves/round-18/w1/ScribeProvinceProc.md` already drafts a Core-candidate shape with a knowledge entry `process-residue-list-only.md`, a fixture and a blanket "never on processes" adjacency rewrite. C3's contract has **no** knowledge entry and no fixture, and `PROVINCE.md:56-57` admits Core only "with an admitted `corpus/knowledge/` entry and a SKILL rule". My §4d keeps F5 frontier; if L1 prefers Core, land entry + SKILL + tool + fixture together or the round claims Core on a nonexistent entry. Also reconcile the two adjacency rewrites into one line.

**F8 — C3's independent counter must be independent and same-moment (verdict: unmeasured, design condition).**
`leaked-procs-before-1631.txt` is one `ps` snapshot (58 rows, 24 pgids, 16:31), so it cannot be its own counter and its count will not reproduce later. Acceptance needs the census and a second mechanism (e.g. `ps -eo pid,ppid,pgid,stat,wchan=` filtered by the same predicate, or a `/proc` walk in a different language) run back-to-back, agreeing on process count and pgid count; the 21/26/2/10/24 numbers above are the anchors from the snapshot.

**F9 — C3 needs a Gate-registry row of kind `probe`, and the redaction must be in the tool (verdict: holds with a row).**
SKILL's gate registry says "a row whose self-test cannot fail is a `probe` or an `evidence` row, never a `gate`". A read-only lister without a failing arm lands as `probe`; if a synthetic-/proc fixture is added, state which case can fail. The no-`environ` rule (contract forbids reading `/proc/<pid>/environ`) belongs in the tool and in §4b, not only in the report.

**F10 — C1 changes the meaning of rc 124 for the r17 hygiene gate (verdict: risk; fixture wording).**
`SKILL.md:158` defines "a census run exceeding the per-case timeout (rc 124 is FAIL, never SKIP)". After C1, the *census* should return 0 with `<repo>\t0\t0\t0\t0\terror` instead of being killed at the bound. The r18 fixture must distinguish (a) the fixture's own bound firing = FAIL, from (b) the census's `repo-timeout` row = expected; otherwise the changed arm converts a routed hang into a gate-visible PASS. The 58-row file is the red evidence that today's fixtures leave the group behind: every r18 fixture needs `start_new_session=True` + `killpg(SIGKILL)`, matching C1's tool contract.

## 6. SOURCES / lesson notes (not owned by this seat; for L1)

- C1's blocking half is already grounded by `S062` (fifo(7): "Normally, opening the FIFO blocks until the other end is opened also.", `corpus/lessons/round-17.md:43`). The new S064+ rows C1 needs must ground the *watchdog* half (process-group signal / `timeout` not reaching grandchildren), not re-open fifo(7).
- ScribeRowsProc's S064/S065 (proc_pid_cwd/proc_pid_stat) ground field semantics; they do not ground the `(deleted)` readlink text, the boot-time base or `cmdline`, so the C3 tool claim must stay within what it cites (that seat's own limits list says the same).
- "One mined mistake" for the frontier step: the r17 residual's status/check-attr-only prescription versus the observed `rev-parse` block (F1) is the strongest candidate, and it is evidenced in this round's own file.

## 7. Not done here

- No gate run, no census run, no proc-census run; no repo edits; nothing signalled. This report's counts are targeted greps/`wc` over the named authority files and the named evidence file, not the gate's 281-token sweep — do not quote them as the gate's before-count.
- Not verified: which round each replay patch is bound to beyond the labels (`r13/r14/r15/r16`); the exact `ps` field width of every row in the leak file (some rows lack the etime column, so field-position arithmetic is unreliable; use `grep -c` on program names).
