# S62SentinelScope — adversarial bypass and scope review of C1 (index-flag concealment)

Lane base: 16fa821fdce00e709d6895ccfc7aaffa465af195 (unchanged at end of run). git 2.56.0, Python 3.14.8, Linux.
Scratch: /fast/scratch/hyaku/souji-r62/S62SentinelScope/ (removed after copying artifacts to `probe/`).
Installs/updates: none. No lane, fleet, or production path written. All fixture repos created under scratch with `git -C "$D"`; `rev-parse --show-toplevel` asserted equal to `$D` before the first commit.

## Method

- `probe/probe.sh` builds the candidate `cand.py` from the lane base writer by inserting the frozen C1 block before `# behaviour 7` (the block uses the writer's own `git()` helper, so the GIT_DIR/GIT_WORK_TREE scrub applies). Base sha256 367a0ca3…, candidate `candidate-as-frozen-probe.py` sha256 72ab7110… (see `probe/SHA256SUMS.txt`).
- `probe/probe.sh` (rc 0), `probe2.sh` (rc 0), `probe3.sh` (rc 0), `probe4.sh` (rc 0), `probe5.sh` (rc 0). Logs: `probe/probe*.log`. Each row below is quoted from those logs; rc is the writer's exit code (2 = refused, 0 = RECORD written).
- The lane was used read-only: `GIT_OPTIONAL_LOCKS=0 git -C <lane> {rev-parse,ls-files -v,status --porcelain}`.

## Frozen matrix A–G (candidate as specified)

| row | base writer | candidate (frozen) | expected |
|---|---|---|---|
| A honest-clean | ACCEPT rc=0 | ACCEPT rc=0 | ACCEPT |
| B honest + --allow-dirty | ACCEPT rc=0 | ACCEPT rc=0 | ACCEPT |
| C dirty-visible | REFUSE rc=2 (`lane worktree is dirty`) | REFUSE rc=2 (`lane worktree is dirty`) | REFUSE, dirty class |
| D skip-worktree + forged counter | ACCEPT rc=0 (forgery) | REFUSE rc=2 `RECEIPT-INDEX-FLAG-CONCEALED: tools/counter.py carries index tag S` | REFUSE, CONCEALED |
| E assume-unchanged + forged | ACCEPT rc=0 (forgery) | REFUSE rc=2 `… index tag h` | REFUSE, CONCEALED |
| F skip-worktree, unmodified | ACCEPT rc=0 | REFUSE rc=2 `… index tag S` | REFUSE, CONCEALED |
| G instrument skip-worktree + forged | REFUSE rc=2 (`differs from committed bytes`) | REFUSE rc=2 `RECEIPT-INDEX-FLAG-CONCEALED: tools/instr.sh … S` | REFUSE, CONCEALED |

Predicate as stated: new_forgeries = 0 (D, E, F refused) ✓; new_honest = 2 (A, B accepted) ✓; class_mismatches = 0 ✓; G refused with CONCEALED ✓.
R60 fixture, candidate: `python3 -B tests/fixtures/r60-receipt-write.py --tool cand.py --work …` → `SUMMARY cases=8 pass=8 fail=0 control=ALWAYS-WRITE-REJECTED,ALWAYS-REFUSE-REJECTED`, rc=0 (`probe/r60-cand.log`). Base also 8/8 (`probe/r60-base.log`).
Lane today: `git ls-files -v` tags = 17350 × `H`; `git status --porcelain` empty (rc 0).

Do-nothing control: NOT RUN by this seat (the counter is outside my scope). The base writer's rows above give three accepted forgeries (D, E, F ACCEPT rc=0), i.e. new_forgeries = 3 by my reading; the counter's exit 1 is unobserved here.

## Bypass table

Verdict column: **yes** = a concealed worktree change produced RECORD rc=0 with the candidate; **no** = candidate refused or no concealment; **limit** = bypass outside C1's index-flag surface, or a named residual.

| # | attempt | command (abridged) | cand rc / result | bypass |
|---|---|---|---|---|
| 1 | --allow-dirty + skip-worktree forged counter | P1a: `update-index --skip-worktree tools/counter.py`, forge, `--allow-dirty` | 2, CONCEALED | **no** |
| 2 | --allow-dirty + assume-unchanged on instrument | P1b | 2, CONCEALED | **no** |
| 3 | --allow-dirty + flagged forged notes.md (base accepts) | P1c | cand 2 CONCEALED; base 0 | **no** (cand) |
| 4 | GIT_DIR env → flagged clean repo, dirty fixture | P2 / F3: `GIT_DIR=$CLEAN/.git`, clean fixture | cand 0 ACCEPT; base 0; control (unscrubbed git) sees S — writer scrub holds | **no** |
| 5 | GIT_WORK_TREE env → flagged clean repo | F3 | cand 0 ACCEPT (scrub holds) | **no** |
| 6 | GIT_INDEX_FILE → clean index copy while main index flagged | P3a | 2 dirty (both writers) | **no** |
| 7 | GIT_INDEX_FILE → flagged index copy, worktree forged visible in main | P3b | cand 2 CONCEALED; base 0 | **no** (cand); index identity not recorded → limit |
| 8 | GIT_INDEX_FILE → nonexistent path | P3 | 2 dirty both | **no** |
| 9 | env: GIT_TRACE=1, GIT_TRACE2_PERF, core.quotePath=false, core.sparseCheckout=false, core.fsmonitor=hook, GIT_LITERAL_PATHSPECS, GIT_NO_REPLACE_OBJECTS, GIT_OPTIONAL_LOCKS=1 — each against skip-worktree counter | P11 | every run: `ls-files -v -z` = `S tools/counter.py`, cand 2 CONCEALED | **no** (no env silenced the ls-files output) |
| 10 | core.fsmonitor hook alone (no index bit), visible forged counter | P4 | status still ` M` with hook; writers 2 dirty | **no** |
| 11 | **index bit fsmonitor-valid + core.fsmonitor hook returning no paths**; forged counter, no -v tag change | F1b / G5: `git status` (token) → `update-index --fsmonitor-valid tools/counter.py` → forge → writer | **cand 0 ACCEPT** (`ls-files -v` shows `H`; `ls-files -f` shows `h`); base 0 ACCEPT | **yes** (needs core.fsmonitor set, env or repo config) |
| 12 | core.fileMode=false + mode-only chmod +x counter | P5 | cand 0 ACCEPT; base 0 | **limit** (config, not index flag) |
| 13 | status.showUntrackedFiles=no + untracked tools/extra.py | P6 | cand 0 ACCEPT; base 0 | **limit** (config, pre-existing) |
| 14 | config-only core.sparseCheckout (no skip bits), forged counter | P7b | 2 dirty both | **no** |
| 15 | honest cone sparse-checkout, excluded `other/o.txt` (S set by git) | F5b | base 0 ACCEPT; cand 2 CONCEALED | **no** — over-refusal (new_honest false positive under sparse; lane has no sparse, 17350 H) |
| 16 | subdirectory root, flagged forged `../notes.md` at repo top; instrument duplicated at top so rev:rel resolves | F6b / G3: `--root $D/tools` | **cand 0 ACCEPT**; base 0 | **yes** (cwd-scoped `ls-files -v -z` misses `../notes.md`; `ls-files -v -z -- ':(top)'` shows `S ../notes.md`) |
| 17 | subdirectory root without duplicate instrument | F6 | 2 `instr.sh absent at rev` both (rev:rel is top-relative in base writer) | **no** (unreachable today) |
| 18 | symlink: skip-worktree counter replaced by symlink to forged file | P9a | cand 2 CONCEALED; base 0 | **no** |
| 19 | symlink: tools dir → tools.real, no flags | P9b | 2 dirty both | **no** |
| 20 | symlink leaf instrument + skip-worktree | P9c | base 2 symlink; cand 2 CONCEALED | **no** |
| 21 | symlink dir + flagged instrument with forged bytes | P9d | 2 both | **no** |
| 22 | flagged file with newline in name, forged | F4 | cand 2 CONCEALED (`tools/we\nird.py`); base 0 | **no** (`-z` parsing correct) |
| 23 | unmerged stage 1+2 entries (tag M) | P12 | cand 2 CONCEALED (class misnamed for an unmerged entry); base 2 dirty (UU) | **no** (misclassification only) |
| 24 | intent-to-add `git add -N` new file | P13 | ls-files tag H; 2 dirty both (status shows it) | **no** |
| 25 | skip+assume set on same path | P14 | cand 2 CONCEALED (tag s) | **no** |
| 26 | stat spoof: same size, `touch -r` restores mtime | F7 | status ` M` (ctime); 2 dirty | **no** |
| 27 | TOCTOU: flags set by the command during run | P10a / F2a (fresh) | **cand 0 ACCEPT** with forged counter and `S` tag in worktree after the run; base 0 (P10a base run) | **yes** (see TOCTOU) |
| 28 | TOCTOU: visible tracked dirt added during run | F2b / F2c | cand 0; base 0 | **yes** (pre-existing class; not closed by C1) |
| 29 | TOCTOU: instrument forged during run | P10c | cand 0; receipt `instrument_sha256` = committed blob digest f1cc5577… while the worktree instrument was forged during the run | **yes** (receipt does not bind executed bytes) |
| 30 | cand2 (mitigated, below) on #11 | G5 | cand2 2 dirty | **no** |
| 31 | cand2 on #16 | G3 | cand2 2 CONCEALED `../notes.md` | **no** |

Rows 1–10, 14–15, 17–26 are negative (no bypass). Rows 11, 16, 27–29 are positive bypasses against the frozen candidate. Rows 12–13 are positive but outside the index-flag surface.

## Findings

### F-1 (in C1 surface): fsmonitor-valid index bit hides a forged tracked file from the frozen candidate

- Mechanism: `git update-index --fsmonitor-valid <path>` sets the index's fsmonitor-valid bit. With `core.fsmonitor` set, `git status` then skips stat/compare for that path, so a forged file reads as clean. `git ls-files -v` does not show this bit (it shows `H`), so the frozen rule accepts. `git ls-files -f` (and `-f -v`) shows it as lowercase `h`.
- Evidence: `probe/probe3.log` F1b: hook on → `ls-files -f -v` shows `h tools/counter.py`; after forge `status --porcelain` empty; writer base ACCEPT, cand ACCEPT. `probe/probe5.log` G5 (fresh state): cand ACCEPT rc=0; cand2 REFUSE rc=2 dirty; base ACCEPT rc=0.
- Preconditions: index bit (in C1 surface) plus `core.fsmonitor` configured (environment or repo `.git/config`). Same-user threat model; still an index-flag concealment the claim names.
- Impact: clean-tree receipt for a forged worktree; the receipt does not record the status.
- Smallest remediation (tested in `probe/candidate-mitigated-probe.py`, not delivered to the lane): run the writer's dirty-status and the index-flag listing with `-c core.fsmonitor=false` (`git(root, "-c", "core.fsmonitor=false", "status", "--porcelain")`, and the same for `ls-files`). With it, the same state gives `lane worktree is dirty` (rc 2). Honest fsmonitor-enabled lanes are not refused by this, because `-c` only disables the hook for the writer's own calls. Frozen matrix A–G and R60 8/8 were unchanged on that candidate (probe4 G2: A/B ACCEPT, C dirty, D/E/F/G CONCEALED; r60 SUMMARY pass=8 fail=0).
- Note: I did not confirm whether git 2.56 built-in fsmonitor (`core.fsmonitor=true`) behaves identically; only a hook was tested.

### F-2 (in C1 surface): cwd-scoped `ls-files` under a subdirectory root

- `git -C <root> ls-files -v -z` lists only entries under the cwd. `git status --porcelain` is repo-wide. A flag on a file outside the root hides it from the candidate while status also hides it (skip-worktree).
- Evidence: F6 `cwd=tools ls-files -v -z` → `H counter.py|H instr.sh`; `… -- ':(top)'` → `S ../notes.md|H counter.py|H instr.sh`; F6b/G3 cand ACCEPT rc=0 with flagged forged `../notes.md` (base also ACCEPT).
- Reachability: the base writer resolves `rev:<rel>` from the repo top, so a subdirectory root only produces a receipt when a copy of the instrument also exists at the top. Contrived today; latent.
- Remediation (tested in cand2): `ls-files -v -z -- ':(top)'` → G3 cand2 REFUSE rc=2 `RECEIPT-INDEX-FLAG-CONCEALED: ../notes.md carries index tag S`. Alternative: assert `git rev-parse --show-toplevel == root`.

### F-3 (outside C1 surface, named): config and environment that hide worktree divergence from `status`

- `core.fileMode=false` hides a mode-only change (P5: cand ACCEPT rc=0, base ACCEPT rc=0).
- `status.showUntrackedFiles=no` hides an untracked file (P6: cand ACCEPT rc=0, base ACCEPT rc=0).
- Both pre-existing in the base writer; C1 does not claim them. Named limit.

### F-4 (TOCTOU disposition): the receipt does not bind the worktree state

- Every check (`ls-files` flags, status, instrument bytes) runs before the command. The command runs after them and can change the lane. The receipt contains only `instrument`, `instrument_sha256` (from the rev's blob, not from the bytes that ran), `rev`, `command`, the captured output and `EXIT`. No status or flag snapshot; no recheck after the run.
- Evidence: F2a (flags set during run) cand ACCEPT rc=0 and the post-run lane state is `S tools/counter.py`; F2b/F2c (visible dirt during run) ACCEPT for both writers; P10c (instrument forged during run) cand ACCEPT, receipt `instrument_sha256=f1cc5577072e31732f57ca468ae4377d0105b0de2830dba21128dc4c3703dffa` = committed blob, worktree instrument forged.
- Disposition: **named limit, not closed by C1.** The clean-tree assertion holds only at the instant before the command. A post-run re-check (status plus `ls-files -v` plus instrument digest from the worktree) before `os.link` would close the flag and dirt cases but not a same-run restore; a full fix needs a separate round.

### F-5 (honest over-refusal, not a bypass)

- Honest cone sparse-checkout (`sparse-checkout init --cone; set tools`, excluded `other/o.txt`): git sets S; base ACCEPT rc=0; cand REFUSE rc=2 `RECEIPT-INDEX-FLAG-CONCEALED: other/o.txt carries index tag S`. The frozen design does not exempt sparse-checkout. No lane impact today (17350 H). Named.
- Unmerged entries are reported with the CONCEALED class (tag M). Refusal is correct; class name is misleading. Named.

### Environment and config probes (no silencing found)

- GIT_DIR/GIT_WORK_TREE: scrubbed for the candidate's `ls-files` as well (F3). This holds only if the candidate keeps the `git()` helper; a direct `subprocess.run(["git", …])` would lose the scrub. The frozen text says `git ls-files -v -z`; the executor should keep `git()`.
- GIT_INDEX_FILE: both calls honour the same index (P3a/b), so no split-brain. The receipt does not record which index was used (named).
- GIT_TRACE, GIT_TRACE2_PERF, core.quotePath, core.sparseCheckout, GIT_LITERAL_PATHSPECS, GIT_NO_REPLACE_OBJECTS, GIT_OPTIONAL_LOCKS: no change to `ls-files -v -z` output (P11). GIT_TRACE writes only to stderr.

## Scope sweep

- Lane: HEAD unchanged; index 17350 × H; `git status --porcelain` empty.
- `find <lane> -newer .ufo/waves/round-62/w1/swarm-registry.json -not -path '*/.git*'` → 59 entries; none under `tools/`, `tests/`, `census/`, `corpus/`, `SKILL.md`, `SCORECARD.md`, `LOG.md`, `PROVINCE.md`. Full list was in scratch (`lane-newer.txt`, removed); the entries are the round-level and peer-seat paths listed above.
- Round-level files outside seat directories (not production paths): `.ufo/waves/round-62/w1-dispatch.json`, `.ufo/waves/round-62/w1.ready`, `.ufo/waves/round-62/w1.ready.dispatched` (L1 dispatch artefacts, presumed); `w1/S62ScribeDraft.md` (written by S62ScribeDraft at the wave level, not inside `w1/S62ScribeDraft/`); `w1/swarm-registry.json` (05:49, pre-round).
- Peer seat directories under `w1/` (S62ScoutSources, S62MutDirtyCase, S62ReviewerCandidate, S62ScribeDraft, S62ConnectorOverlap, S62CriticClaim, S62ReviewerDesign, S62ExecCounter, S62ExecCandidate) exist. S62ExecCandidate is empty at sweep time; the executor's candidate bytes were not present, so I did not test them (named limit).
- `.git` directory: mtime 05:54:51, an entry was created and removed inside `.git/` (no surviving entry newer than the marker). Not attributable from this seat. My own lane git calls were read-only and used `GIT_OPTIONAL_LOCKS=0` except one turn-1 `git status --porcelain` (may have taken a transient `index.lock`; `.git/index` mtime is 05:37, before this seat started).
- `find /tmp -newer …/w1 -user vgpnk -maxdepth 2`: `/tmp/alma.log` (05:55:34) and `/tmp/mori-r17-ctxcheck-pnxsnhyb/` (05:54:26) were listed; not created by this seat (every probe `mktemp`/writer temp used `-p`/`dir=` under scratch); owner and creator not verified; not deleted. The sweep's `find` exited 1 (permission errors suppressed), so the /tmp sweep is incomplete (named).
- Scratch root `/fast/scratch/hyaku/souji-r62/` contains other seats' directories (l1-freeze, l1probe, S62ConnectorOverlap, S62CriticClaim, S62ReviewerCandidate, S62ReviewerDesign, S62ScoutSources) and this seat's (removed).
- Scope verdict: no production path or lane write by this seat; wave-level files written by peers and the orchestrator are outside their seat directories (see above).

**SCOPE: named-limits**

## Named limits

- Tested only with git 2.56.0 and Python 3.14.8 on Linux. Hook-based fsmonitor only; built-in fsmonitor daemon untested.
- Candidate is my reconstruction from the frozen text (`probe/candidate-as-frozen-probe.py`), not the executor's bytes (S62ExecCandidate empty at sweep time).
- Config and environment bypasses assume same-user write access to the repo config or environment.
- The subdirectory-root case (F-2) needs a duplicated top-level instrument; the base writer's `rev:<rel>` resolution is top-relative.
- Mitigation (`-c core.fsmonitor=false`, `':(top)'`) was tested only against my probe rows, not the full repo test suite.
- Ignored-file visibility (`status` skips ignored files) was not examined.

## Deliverables

- `report.md` (this file).
- `probe/` : `probe.sh`, `probe2.sh`, `probe3.sh`, `probe4.sh`, `probe5.sh`, `build-cand.py`, `fsm.sh`, `flip.sh`, all logs (`probe*.log`, `r60-*.log`), `candidate-as-frozen-probe.py`, `candidate-mitigated-probe.py`, `receipts/` (38 receipts from accepted runs), `SHA256SUMS.txt`.
- Not written: `.ufo/waves/round-62/w1/S62SentinelScope.md` (the Report trailer path). It is outside this seat's directory and the hard write scope named `w1/<seat>/` only; the L1 should decide whether to copy this report there.
