STATUS: DONE — C3 attacked on kill-authority, schema, false-positive and axis grounds; 4 defects (2 must-fix, 2 wording/robustness), all with smallest corrections.

# CriticC3Authority — does the process census grant or invite kill authority?

Scoped to: C3 (`tools/souji-proc-census.sh`, read-only own-uid residue census), its authority boundary vs `PROVINCE.md`, the reap-record protocol the census enables, and the coverage-axis framing/counting.

## Commands run (all read-only, probe-rule conformant)

| # | Command | Result |
|---|---|---|
| 1 | `read PROVINCE.md` | `:46-47` "mori-shokunin observes fleet health and reports; souji acts on artifacts and never on processes"; `:88-99` r14 refinement — read-only repo-structure probe "reports … not removal authorization" |
| 2 | `read census/round-18/leaked-procs-before-1631.txt` | 58 rows, `pid ppid pgid age argv`; every argv names a now-deleted `/var/tmp/{r15-census-config,r17-census-hygiene,souji-r1[67]-*}` path |
| 3 | `readlink /proc/<pid>/cwd`, `stat` fields 3,4,5,22, `wchan` for pids 185592,185605,289650,562276,562279 | all `state=S`; cwd `… (deleted)`; ppid **1497**; wchan `do_wait` (bash parents), `wait_for_partner` / `anon_pipe_read` (blocked git/bash children) |
| 4 | `cat /proc/1497/{comm,cwd,stat}` | `systemd`, `ppid=1`, `pgrp=sid=1497` — the residue parents are **not orphans**; a live session leader (systemd) adopted them |
| 5 | group-membership sweep of pgids 184733, 558610, 558608 | every member is a residue `bash`/`git` **today** — clean by luck, not by construction |
| 6 | full own-uid enumeration: cwd-` (deleted)` + argv-stale-path under `/var/tmp|/tmp|/dev/shm` | **58 rows**, set-identical to the committed list (`diff` → `IDENTICAL-58`); every row's `wchan` ∈ {`do_wait`, `wait_for_partner`, `anon_pipe_read`} |
| 7 | `cat /proc/sys/kernel/random/boot_id`, `pid_max` | `3e7084f4-…`, `4194304` — pid space is ~4M; reuse is real but slow |
| 8 | extract `ProcCensus`, `ProcCensusFixture`, `LeakCounter`, `CriticC3Measure` prompts from `w1-spec.json` | commissioned TSV: `pid ppid pgid sid age_s state wchan reason cmd`; reasons `cwd-deleted`, `argv-path-gone:<path>` with "parent scratch dir also gone" qualifier; `leak-count.py` is a blind second implementation (Q5) |
| 9 | `read .ufo/waves/round-18/w1/ScribeProvinceProc.md`, `ScribeRowsProc.md` | sibling drafts the adjacency fix (`never signals`), a `## Refuses` signal bullet, S064/S065 (proc_pid_cwd, proc_pid_stat) |

## Answer 1 — does the census grant or invite kill authority?

**Grant: no. Invite: yes, in three specific ways.**

(a) **"Governed surface" grants latent authority.** The claim text says residue "becomes a governed surface." In this lane "governed" means receipt-gated removal authority (PROVINCE `:3-4` "receipt-gated removal", `:17` "Dry-run censuses and removal-list proposals for operator approval"). Declaring a *process* surface "governed" places it inside the removal-authority vocabulary, even though no signal is ever exercised. The r13 precedent (`PROVINCE.md:84-86`) named the same move correctly: a bounded read-only probe that "reports … not recoverable disk space and not removal authorization."

(b) **The commissioned schema invites `xargs kill`.** The TSV carries `pid` and `pgid` but **no identity binder**: `age_s` is a 1-second-rounded derived age, and there is no raw `starttime` and no `boot_id` in the commissioned columns (`w1-spec.json` ProcCensus item, cmd 8). A consumer piping `pid` to `kill` after any delay is betting on pid-reuse odds (~4M space, cmd 7). If the row must be re-checkable — and any operator reap must re-check — the row needs `starttime` (ticks, field 22) and the host `boot_id`, or the reap protocol must state explicitly that the census row is a *nomination only* and the record is rebuilt from live `/proc` at act time.

(c) **`pgid` invites `killpg`.** Today's groups are residue-pure (cmd 5), but membership is time-dependent: a live process can join a listed pgid between listing and act, and `killpg` then hits a process the census never enumerated. `pgid` belongs in the output (it is how residue *families* group), but the boundary text must forbid treating `pgid` as a signal scope — the leaked parents share session 1497 with **systemd itself** (cmd 4); walking "up the tree" to reap a family would be catastrophic overreach.

## Answer 2 — the three kill-targets, and what keeps C3 list-only

| threat | live evidence | current protection | gap |
|---|---|---|---|
| PID reuse (list→later kill) | pid_max 4194304; residue pids already span 185592–4037367 | none in schema (no starttime/boot_id column) | reap must re-read `/proc/<pid>/stat` field 22 + boot_id at act time |
| live fixture of another agent | `/var/tmp/souji-r18-<Seat>/lane` is the mandated scratch; an agent process *whose own cleanup already ran* but that still runs (driver-restarted harness, hung watchdog) is argv-stale + possibly cwd-deleted while live | `argv-path-gone` requires *parent scratch dir* gone; `R`-state exclusion is implicit only | residue reason never equals reap-eligible; reap additionally requires blocked `state`/`wchan` re-verified |
| closure-session processes | r17 closure used `/tmp/souji-r17-close`, `/var/tmp/souji-r17-close-probe` (lesson `:23`); operator-owned dirs are deleted post-closure while stragglers can outlive it | none | same as above + same-uid + age floor; a minutes-old process is a live session, not residue |

**The exact list-only rule** (smallest correct formulation, reconciling with C1 which *does* signal its own spawned groups):

> `souji-proc-census.sh` and every souji tool never signal a process it did not itself spawn. Census output — including `pid`, `pgid`, `sid` — is evidence for the operator, never a removal receipt and never a signal authorization. The only kill authority this lane exercises is the C1 watchdog over process groups the census itself spawned, bounded by the repo timeout.

This is enforceable, not just prose: (i) the script contains no `kill`/`pkill`/`killpg`/signal-syscall token outside comments — auditable by `grep` in the fixture; (ii) the fixture can assert behaviorally — run the tool against a planted residue process, then `kill -0` the plant: it must still exist; (iii) PROVINCE `## Refuses` gains the signal bullet ScribeProvinceProc drafted, **amended** — its current text "Signalling any process" would make C1's watchdog (SIGTERM/SIGKILL to its own groups) a boundary violation; the bullet must exempt "process groups a souji tool itself spawned for a bounded timeout."

## Answer 3 — operator-approved reap record (the schema C3 must publish as the *only* sanctioned consumer path)

```
record_id, approved_by, listed_at, reap_at,
pid, starttime_ticks, boot_id,          # identity triple — mandatory
ppid, pgid, sid,                        # context at listing
reason, reason_evidence,                # e.g. cwd-deleted / argv-path-gone:<path>
signal                                  # SIGTERM|SIGKILL|SIGKILL-after-2s
```

**Re-check at act time (all must hold, else abort that row):**
1. `/proc/<pid>` exists and is still owned by the same uid.
2. field 22 `starttime` equals `starttime_ticks` AND `/proc/sys/kernel/random/boot_id` equals `boot_id` — together they defeat pid reuse *and* cross-reboot staleness of an old list. `ps -o lstart` is insufficient (second granularity; two spawns in one second collide).
3. The **reason re-validates**: cwd still deleted / the argv path and its parent scratch still `ENOENT`.
4. Process still residue-class: `state` ∈ {S, D, T} (not `R`, not `Z`), `wchan` still a blocking wait; age > floor (≥ one driver tick, mirroring the quarantine hold).
5. `kill` per pid only. `killpg` permitted solely if a fresh group-membership enumeration equals the recorded residue set exactly; the r18 host shows clean groups today by luck, not by rule (cmd 5). Never signal `sid` or ppid chains — ppid 1497 is systemd.

A staleness horizon: a list older than (say) 600 s is re-listed, not reaped — pids churn.

## Answer 4 — is 'coverage' the right axis, and a non-gameable count

**Axis: yes, defensible** — the r13 precedent added a read-only probe under coverage. But only if the claim is reworded: "becomes a **governed** surface" → "becomes an **observed/measured** surface (evidence only, no act authority)". As written it claims removal-authority vocabulary over processes and collides with `PROVINCE.md:47` until the ScribeProvinceProc adjacency amendment lands. The mori adjacency is real but benign: mori observes *health*; souji adds a *fixture-hygiene evidence surface*. "Report, don't absorb" applies to mori's side, not souji's — souji may hold a read-only census of its own residue.

**Non-gameable before→after** (fixing the gameable forms):

- *Gameable:* "governed surfaces 0→1" — pure declaration; "orphans detected vs an independent counter" — if both implement the same predicate the agreement is tautological, and on a live host recall is unmeasurable anyway.
- *Non-gameable triple, mirroring CriticC3Measure's fixture proposal:*
  1. **Fixture recall/precision (gameable only by genuine improvement):** seeded world with K residue plants across classes {cwd-deleted-blocked-in-fifo, cwd-deleted-blocked-in-pipe, argv-path-gone} and J live controls {same-uid live process in a *existing* `/var/tmp` dir, process with argv path that still exists, zombie, other-uid process — unlistable}: before = no tool exists (detects 0 by absence, the honest baseline); after = detects exactly K, 0 false positives, each with the correct reason class.
  2. **Host reconciliation (agreement, not recall):** pid-set equality between the tool and the blind `leak-count.py` (Q5 second implementation — genuinely independent: different author, different language). Verified feasible today: my inline enumeration reproduced the committed 58-pid set exactly (`IDENTICAL-58`), so a symmetric-difference metric over committed-list ∪ live-set is real and falsifiable — any drift (a process exiting between the two reads) is a declared snapshot artifact, not a silent pass.
  3. **Self-harm bound (the axis the claim actually cares about):** after the fixture's red arm runs, the tool itself reports 0 new residue rows attributable to that arm — closing the loop between C1's timeout fix and C3's observability.

## Findings

**F1 — "governed surface" wording grants latent kill authority. Verdict: fails as written; fixable.**
Claim text vs `PROVINCE.md:3-4,17`. Smallest fix: "governed" → "observed" in the claim/SCORECARD/knowledge entry, plus an explicit "residue rows are not removal receipts and not signal authorization" line (ScribeProvinceProc §2a already carries the artifact half; add the signal half).

**F2 — TSV schema lacks an identity binder; `pgid` invites `killpg`. Verdict: fails for any downstream use; fixable.**
Add `starttime` (field-22 ticks) and `boot_id` columns, or declare rows nomination-only. Smallest fix: add the two columns (both already computed: `age_s` derives from field 22; boot_id is one read) and the reap-record text above in the knowledge entry.

**F3 — PROVINCE `## Refuses` signal bullet must exempt self-spawned groups. Verdict: fails as drafted; fixable.**
ScribeProvinceProc §2b's "Signalling any process" contradicts C1's watchdog contract (SIGTERM/SIGKILL to own groups). Smallest fix: append "except process groups a souji tool itself spawned for its bounded timeout" (or scope the bullet to the census tool only).

**F4 — residue reason ≠ reap eligibility is unstated anywhere. Verdict: holds for listing; gap for the inevitable consumer.**
All 58 live rows are S-state children of live systemd (cmd 3,4) — "parent dead" is false for every one, so no parent-liveness test rescues a naive reaper. Smallest fix: state in the knowledge entry that the census never outputs a reap-eligible column, and the operator protocol (Answer 3) is the only sanctioned path.

**F5 — `age_s` alone cannot catch same-second pid reuse. Verdict: holds for display; insufficient for re-check.**
Field 22 ticks + boot_id is the binder; `ps -o lstart` rounding is a known footgun. Covered by F2's fix.

**Verdict on the claim: partial → holds after F1–F3.** The census itself is correctly bounded (read-only, own-uid, no environ, redacted argv); every defect is in the authority *vocabulary* and *schema*, not the observation. None is a tradeoff the judge must reject — all four fixes are cheap and improve calibration/operability at no cost to coverage.

## Out of scope / not done

- Did not run `tools/souji-proc-census.sh` (does not exist at b576341; forbidden against real dirs anyway). Did not signal any process. No credential content read (`/proc/*/environ` untouched; argv read as data, cited as path shapes only).
- `tests/fixtures/r18-proc-census.sh` survival assertion (tool exits, planted process still `kill -0`-able) is recommended to ProcCensusFixture if not already covered.
- Tools installed: none.
