# Round 10 — S02 cluster-A candidate report (independent patch)

Seat S02, cluster A member 2. Deliverable: an **independent** hardening of the
three authorization engines from the S17-patched base, written to
`tools/cand-a2-{verify,vault,quarantine}.sh`. No shared file was modified; the
installed tools and every other seat's files are untouched.

Axes: fail-closed safety (false-SAFE / unsafe-DELETE prevention), fresh
reproducibility, regression coverage, consumer/engine consistency.

## Candidate identity

| candidate | sha256 (prefix) | selftest | base |
|---|---|---:|---|
| `tools/cand-a2-verify.sh` | `6fec1dce414b` | **49 / 49** | S17 verify 40/40 |
| `tools/cand-a2-vault.sh` | `36c567dcaa27` | **59 / 59** | S17 vault 51/51 |
| `tools/cand-a2-quarantine.sh` | `b607975c6c45` | **100 / 100** | S17 quarantine 91/91 |

All three exit 0; `bash -n` and `shellcheck -x -S error` clean.
Baseline installed bytes measured for comparison:
`4baa8d955c53` / `ea43bb0f9b9f` / `f6f8516c15ab`.

## Fresh repro battery (gating evidence)

`census/round-10/S02-cluster-A-repro.py` — 13 cases, all fixtures fresh under
`/var/tmp` (host `/tmp` carries a disk quota), every destructive call inside a
`mktemp` fixture repo. Run against the installed base and then the candidates:

| case | class | installed base | candidates |
|---|---|---|---|
| A1 dirty-pushed-file | J01 | verify SAFE(pushed) | NOT-SAFE |
| A2 unpushed-stale-fallback | J08 | SAFE(stale) + **DELETED** | NOT-SAFE, retained |
| A3 detached-head-unpushed | J12 | SAFE(pushed) | NOT-SAFE |
| A4 ledger-self-copy | J05 | SAFE(moved-to-obsidian) | NOT-SAFE |
| A5 ledger-vault-inside-source | J05 | SAFE(moved-to-obsidian) | NOT-SAFE |
| A6 ledger-dir-missing-vault-digest | J06 | SAFE(moved-to-obsidian) | NOT-SAFE |
| A7 gitfile-repo-root | J23 | SAFE(pushed) | NOT-SAFE |
| A8 tab-path-injection | J17 | engine NOT-SAFE, consumer **DELETED** | NOT-AUTHORIZED |
| A9 hidden-live-reference | J02 | SAFE(stale) + **DELETED** | NOT-SAFE, retained |
| A10 missing-sweep-scope | J15 | SAFE(stale) | NOT-SAFE |
| A11 quarantine-symlink-root | J07 | **DELETED** outside repo | NOT-AUTHORIZED |
| A12 second-check default-ref | J10 | ABORTED (r9 repair holds) | ABORTED |
| A13 nul-list-gate | J16 | usage error (r9 repair holds) | usage error |

**Counts.** Installed base: 13 cases -> **9 false-SAFE, 4 unsafe-DELETE**
(A5/A6 abort after staging and retain the bytes; the other 3 DELETED targets
in the table above are A2/A8/A9/A11 — 4 in total). Candidates: 13 cases ->
**0 false-SAFE, 0 unsafe-DELETE**; every target's bytes preserved
(`bytes_preserved=True` on all 13).

## Independent gates

- **r9 S18 differential battery** (`tools/souji-round9-s18-test.py`, 37 checks,
  freshly re-run both ways): installed base **12/37, 25 unsafe**; candidates
  **34/37, 0 unsafe, 0 compatibility failures**. The 3 non-passing checks are
  the contested fixture documented below, not unsafe outcomes.
- **S15 composer** (`tools/cand-merge-selftest.sh`, with the candidate engine
  pinned via `CM_VERIFY_BIN`): verify **25/25**, vault **25/25**, quarantine
  **38/38**. Without the pin the composer points quarantine at the *installed*
  engine, which measures the unmerged lineage and fails 4 checks — the pin is
  required for a valid measurement.
- **Positive controls** (guarding against blanket refusal): clean pushed file ->
  `SAFE(pushed)` and actually `DELETED`; aged scratch -> `SAFE(stale)`. Both
  engines and the real delete flow still authorize legitimate removals.

## Repairs, by defect class

Engine-side (`cand-a2-verify` + `cand-a2-vault`):

- **J01** pushed now certifies *current bytes*, not commit ancestry alone: a
  worktree copy differing from the pushed blob, or a directory with
  dirty/untracked/ignored children, refuses (`current-bytes-differ`,
  `current-content-not-preserved`).
- **J02** the live-reference sweep gains `--hidden`; dotfile references count.
- **J03** a directory's own mtime is no longer treated as its children's age:
  every descendant must be inside the window.
- **J08** unpushed work over the path is a **STALE_VETO** — the stale receipt
  can no longer authorize past it. It is deliberately *not* a terminal verdict:
  F2 requires `none` and F6 requires a pushed history plus local edits to remain
  preservable via an independent ledger row.
- **J12** the unpushed query is status-checked and HEAD-inclusive, so a
  detached-only commit is not read as zero and a failed query never reads as
  "no unpushed work".
- **J05** ledger rows must be independent: a row pointing the artifact at
  itself, or a vault inside the directory being removed, is refused.
- **J06** both digest columns are mandatory for a directory row; an absent
  column is a row defect, not a skipped check.
- **J15** an unavailable sweep scope returns `unknown`, never `0`.
- **J19** worktree uniqueness compares against **durable refs only**
  (`--branches --remotes --tags`); `--not --all` includes the candidate
  worktree's own HEAD and produced a false `metadata-prune`. Verified directly:
  `--all` -> 0, durable refs -> 1.
- **J23** a repository root whose `.git` is a **file** (`--separate-git-dir`)
  classifies as a repo root. Registration is tested first so a linked worktree
  is not reclassified as a root.

Consumer-side (`cand-a2-quarantine`):

- **J17** the engine is invoked with `--json` and parsed strictly (one record,
  exact shape, escaped fields). A tab-bearing pathname can no longer re-frame
  the TSV line into a forged verdict the engine never gave.
- **J07** containment is **physical**: a symlinked or escaping
  `.ufo-quarantine` is refused before any mutation (`quarantine-root-symlink`,
  `quarantine-escapes-repo`).
- **J05 (act time)** the second check refuses when the vault path resolves to
  the staged copy or anything inside quarantine — preservation must be
  independent at act time, not merely at capture.
- **J12** the second check's unpushed query is HEAD-inclusive and status-checked.

## Regression coverage

One selftest case per closed class was added to each candidate (verify +9,
vault +8, quarantine +9). New fixtures live in their own fixture repo
(`r10-shokunin` / `r10-qa-shokunin`): the shared `st_commit` helper runs
`git add -A` repo-wide, so building them in the existing repo would sweep the
untracked F7/F8/E8 fixtures into commits and silently change those cases'
receipts. **Anyone extending these suites must keep new fixtures isolated.**

## Cross-seat contradiction — needs parent arbitration

The S15 composer case `s15-g2-backdated-descendant` requires **refusing** a
descendant whose mtime was backdated (`touch -d`) but whose ctime is fresh.
The S18 positive control `positive-stale-directory` builds the **same shape**
(`os.utime` on both the file and the container, mtime backdated, ctime = now)
and requires **SAFE + delete**. Measured side by side:

```
S18 positive-stale-directory   mtime=1792115134  ctime=1792374334
S15  s15-g2-backdated-descendant mtime=1791855934  ctime=1792374334
```

Identical signal, opposite expectations — no implementation can satisfy both.
I chose **fail-closed** (refuse), per the lane's standing doctrine ("when
uncertain, the verdict is NOT-SAFE"), which costs exactly the 3 S18
positive-control checks (`positive-stale-directory/{verify,vault-verify,quarantine}`)
and leaves **0 unsafe outcomes** in that battery. The parent must either
(a) accept the fail-closed trade and retire the S18 positive control, or
(b) relax the S15 case. I did not silently pick one and hide the other.

## Not closed / limits

- The ctime rule is a fail-closed heuristic, not a forgery proof: a descendant
  written and backdated before the window's ctime boundary is still accepted.
- `dir_digest`'s symlink refusal and the `.ufo` refusal are inherited from S17
  and unchanged.
- Arbitrary concurrent-writer atomicity (ABA between the last check and the
  delete) remains **not proven**, as S17 recorded.
- Nothing here is certified for live deletion authorization: these are
  **candidates**. Promotion, byte freeze and the fleet-level verdict belong to
  the parent.
- No live fleet artifact was read, moved or deleted; no `git fetch`/`push`/
  `commit`/`branch`/`checkout`/`reset`/`rebase` ran against any real repo; no
  GUI launcher was invoked. All mutations were inside `/var/tmp` fixtures.

## Files written by this seat

- `tools/cand-a2-verify.sh`, `tools/cand-a2-vault.sh`, `tools/cand-a2-quarantine.sh`
- `census/round-10/S02-cluster-A-repro.py` (fresh repro battery)
- `census/round-10/S02-cluster-A.md` (this fragment)

Nothing else. `LOG.md`, `SCORECARD.md`, the installed tools and shared
bookkeeping were not touched — the parent integrates.

## Re-verification pass (same session, after an interruption)

The candidate bytes above were re-checked from scratch rather than re-derived.
`census/round-10/S02-cluster-A-reverify.json` holds the machine record.

- Hashes re-measured and unchanged: `6fec1dce414b…` verify, `36c567dcaa27…`
  vault, `b607975c6c45…` quarantine; `bash -n` clean on all three.
- Selftests re-run, exit 0: verify **49/49**, vault **59/59**,
  quarantine **100/100**.
- Cluster-A repro battery re-run both ways: installed S17 base
  **9 false-SAFE / 4 unsafe-DELETE**; candidates **0 false-SAFE /
  0 unsafe-DELETE**, every target's bytes preserved.
- S18 differential battery (`tools/souji-round9-s18-test.py`, 37 checks)
  re-run both ways: installed **12/37, 25 unsafe, 0 compatibility failures**;
  candidates **34/37, 0 unsafe, 3 compatibility failures** — the three are
  exactly the contested `positive-stale-directory` control described above,
  where the fail-closed refusal is deliberate. `positive-pushed-directory`
  still passes and still deletes, so the refusal is not blanket.

No file outside `tools/cand-a2-*` and `census/round-10/S02-cluster-A*` was
written by this seat.
