# S13 — round 10, cluster G lead (index-write contract; fresh-descendant race)

Seat: S13. Lane: `souji-shokunin`. Round 10 (close the r9 defect classes).
Assigned cluster: **G** — (G1) index-write contract, (G2) fresh-descendant race.

Verdict: **G1 — no fresh repro on installed bytes; candidate makes the contract
structural. G2 — reproduced 6/6 on installed bytes; candidate closes all six
plus the hold-window race.** Every number below is from a fresh `/var/tmp`
fixture built during this seat's run.

## Tools under test

Installed (S17-patched, my patch base) — SHA-256, unchanged by this seat:

| tool | sha256 |
|---|---|
| `souji-verify.sh` | `4baa8d955c531fcc73edc6b62021cb9531a31e1baed8aa853ba957b204d1cfc1` |
| `souji-vault-verify.sh` | `ea43bb0f9b9fe96cc26451df1a41d2df97d2d044852f122c987c209b6ec7b7a7` |
| `souji-quarantine.sh` | `f6f8516c15ab654f7e5f2dc2a7840eef0b53b9f9433e2ff70a64490b35fde68f` |
| `souji-census.sh` | `11bf9cdf8d4f75415b18e046aef0e96215b983f0d5b3ff7842301ff6ac65d381` |

Candidates written by this seat:

| tool | sha256 |
|---|---|
| `tools/cand-g1-guard.sh` | `f7444574cf32edf771c0afefe4db900df682cd28c2294c0088166b1740b6d496` |
| `tools/cand-g1-verify.sh` | `a1b4d0592918fd0c9bb3b85d22615b6fbcb660512848db8242b47953070ccd27` |
| `tools/cand-g1-vault.sh` | `965c6f69bd79341369996c62b54f2a3bdc633e2ac41883691dd4468fd5c0ca07` |
| `tools/cand-g1-census.sh` | `1e9419bce4d92f3349961b48db5bdf5b196419d906dac91ac8945b63a95d64ea` |
| `tools/cand-g1-quarantine.sh` | `543e5236a054a2f9d9e3621db890f77e0650bf168dacad5899f30111181be380` |
| `tools/cand-g1-build.sh` | `4df80c89fc5b5cb9c8d57078501c3c46bb179db8026ac96094fc9c298f5b4512` |

The guard must ship beside all four candidates. `cand-g1-build.sh` regenerates
them from the installed bytes; it is a generator, not a runtime dependency.

## G1 — index-write contract

**No fresh repro of the r9 S06-D2 class on installed bytes.** Twelve hostile
constructions across all four tools, comparing `.git/index` sha256 + mtime_ns +
inode and `.git/index.lock` before/after:

| construction | tools | installed | candidate |
|---|---|---|---|
| stale index stat, caller `GIT_OPTIONAL_LOCKS=1` | verify, vault, census, quarantine | unchanged | unchanged |
| stale index stat, file target | verify, quarantine | unchanged | unchanged |
| caller locks unset | verify | unchanged | unchanged |
| index deleted before probe | verify, vault, census | stays absent, not created | stays absent |
| index read-only (0444) | verify | unchanged | unchanged |
| foreign `index.lock` present | verify | preserved, index unchanged | preserved |

Measured: **installed 0 index violations / candidate 0** on this battery. The
r9 finding was real at its own hashes; on the current installed bytes the
`export GIT_OPTIONAL_LOCKS=0` plus `--no-optional-locks` call sites already hold.

The candidate converts that incidental property into a **structural** one:
`git()` is shadowed to `command git --no-optional-locks "$@"`, so every call
site — including inherited ones the guard never touches — is covered, even if a
future edit adds a bare `git`. Verified the shadow still permits plumbing
writes (`add`, `write-tree`, `commit-tree`, `update-ref`, `symbolic-ref`,
`git mv`) so the real deletion flow is unaffected. The selftest asserts
sha256 + mtime_ns + inode identity on five constructions plus lock preservation,
and asserts the shadow itself is present (case `G1-g`).

## G2 — fresh-descendant race

**Reproduced 6/6 on installed bytes.** An aged `.scratch` container with a live
descendant gets `SAFE(stale)` from both engines; quarantine stages it and then
`DELETED` — destroying the live subtree:

| construction | installed verify | installed quarantine | candidate verify | candidate quarantine |
|---|---|---|---|---|
| fresh child in aged container | SAFE | **DELETED**, survives=False | NOT-SAFE | NOT-AUTHORIZED, survives=True |
| fresh ignored child | SAFE | **DELETED** | NOT-SAFE | NOT-AUTHORIZED |
| live reference names child | SAFE | **DELETED** | NOT-SAFE | NOT-AUTHORIZED |
| live reference in hidden file | SAFE | **DELETED** | NOT-SAFE | NOT-AUTHORIZED |
| fresh nested subdirectory | SAFE | **DELETED** | NOT-SAFE | NOT-AUTHORIZED |
| child bytes fresh, mtime forged old | SAFE | **DELETED** | NOT-SAFE | NOT-AUTHORIZED |
| write during hold window | — | ABORTED, survives=False | — | NOT-AUTHORIZED, survives=True |

Battery totals over 19 cases: **installed 6 false-SAFE / 6 unsafe deletes →
candidate 0 / 0.**

### Root cause and the witness that closes it

The inherited `try_stale` ages a target by the **target's own mtime only**, so
any descendant written later is invisible — an aged container is treated as
proof that its children are stale. Two measured facts drive the fix:

- `rename` preserves inode and mtime but **advances ctime** on the moved node
  only (measured: moved root `ctime` +1s, descendants unchanged).
- `utime` forges mtime but **cannot forge ctime backward** (measured: after
  `touch -d '2020-01-01'`, `mtime` = 2020, `ctime` = now).

So a descendant's ctime is the one freshness witness an attacker cannot forge.
The candidate requires every strict descendant to be old by mtime **and** ctime,
while the root is checked by mtime only — because a directory that was legitimately
moved would otherwise be refused by its own advanced ctime. That asymmetry is
what closes `content-fresh-mtime-old` without breaking `mv`-based flows.

Additionally: the live-reference sweep is extended from the target's basename to
**every descendant's basename**, and quarantine pins a per-descendant
relpath/mtime/size manifest at staging and re-checks it after the hold, so a
write inside the hold window aborts the deletion.

### Cross-seat result

The banked S18 guard (`tools/souji-guard.r9-s18.sh`) fixes 5/6 of these but
leaves `content-fresh-mtime-old` false-SAFE — measured this run: S18 returns
`verdict=SAFE` on that construction, because its `s18_old_scope` recurses on
**mtime only** and so trusts the forged timestamp. The ctime witness here closes
that residual hole. This is a composition input for the parent, not a claim that
S18 is superseded.

## Selftest counts

All four candidates exit 0 with every pre-existing case ported and the new
regression cases added:

| candidate | checks | failed | ported r9 cases | positive controls |
|---|---|---|---|---|
| `cand-g1-verify.sh` | 45 | 0 | 16/16 | `F7`/`F8` SAFE(stale) pass |
| `cand-g1-vault.sh` | 56 | 0 | 16/16 | `F7`/`F8` VERIFIED(stale) pass |
| `cand-g1-census.sh` | 37 | 0 | 32/32 (inherited) | fixture-containment pass |
| `cand-g1-quarantine.sh` | 96 | 0 | 28/28 | `P1`/`P2`/`P3`/`L1` all DELETED |

Installed baselines for comparison (measured this run): verify 40, vault 51,
quarantine 91, census 32 — all 0 failed. The candidate counts are higher because
the guard adds five G1/G2 cases per tool. Positive controls confirm
non-harm: legitimate pushed, stale-file and moved-to-obsidian deletions still
`DELETED` and their sources are removed.

Static checks: `bash -n` clean on all five files; `shellcheck -x -S error`
clean; the toolchain's own forbidden-subcommand audit (`fetch|push|commit|branch|
checkout|reset|rebase`) is clean on the guard — an earlier draft used `git reset`
to rebuild a fixture index and was rewritten to plumbing (`read-tree`) so the
guard does not model what it forbids.

## Reproduction

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin
bash tools/cand-g1-build.sh                      # regenerate candidates
for t in verify vault census quarantine; do
  TMPDIR=/var/tmp bash tools/cand-g1-$t.sh --selftest
done
mkdir -p /var/tmp/s13-r10/base /var/tmp/s13-r10/cands
cp tools/souji-{verify,vault-verify,quarantine,census}.sh /var/tmp/s13-r10/base/
cp tools/cand-g1-{verify,vault,quarantine,census,guard}.sh /var/tmp/s13-r10/cands/
python3 census/round-10/S13-candidate-battery.py \
  --installed /var/tmp/s13-r10/base --cand /var/tmp/s13-r10/cands \
  --out /var/tmp/s13-r10/battery.json
```

Evidence captured: `/var/tmp/s13-r10/battery.json` (19 cases, both toolchains),
`/var/tmp/s13-r10/cand-{verify,vault,census,quarantine}.log` (selftest output).
The pre-seeded `census/round-10/S13-cluster-G-repro.py` also runs against the
candidates. All fixture roots are under `/var/tmp`; the battery asserts
containment before setting the copied-tool live-root override.

## Scope, non-claims, and defects found in my own work

Not claimed: a general security proof; fleet-wide counters (no fleet mutation
occurred); exhaustive concurrent-race coverage beyond the two constructions
tested; census authorizer behavior (census is a reporter, so its G2 cases assert
the guard predicate rather than a verdict).

Four defects were found in my own harness/guard and fixed before the final
numbers — recorded because each would have produced false evidence:

1. **Both battery sides resolved to the same directory**, so the "installed"
   baseline silently ran candidate binaries. The first run appeared to show
   installed already had 0 index violations.
2. **A pre-existing foreign `index.lock` was scored as a violation** on both
   sides, when preserving it is correct. Scoring now counts only locks the tool
   itself creates.
3. **`cand_g2_manifest` failed on files** (`cd` into a file, `find -printf`
   empty), which aborted quarantine's real flow at stage 2.
4. **The quarantine candidate delegated to the installed engine**, so G2 passed
   through unhardened until the guard wired `VERIFY_BIN` to its hardened sibling.

Also removed before finalising: a drafted `SOUJI_CAND_SELFTEST_ACTIVE=1` env
bypass that would have relaxed the ctime witness — an env-controlled escape
hatch inside a safety guard is the same defect class r9 punished. It was
replaced by `--stale-days 0` plus a real 1.2 s wait, which yields genuinely
un-forged metadata and needs no bypass. `grep` for the name returns nothing.

## Files written by this seat

- `census/round-10/S13-cluster-G-repro.py` (pre-seeded, read and run; not modified)
- `census/round-10/S13-candidate-battery.py` (new)
- `census/round-10/S13-fragment.md` (this file)
- `tools/cand-g1-guard.sh`, `cand-g1-verify.sh`, `cand-g1-vault.sh`,
  `cand-g1-census.sh`, `cand-g1-quarantine.sh`, `cand-g1-build.sh`

No installed tool, shared bookkeeping, `LOG.md`, `SCORECARD.md`, live lane
content or sibling repo was modified.

## Handoff

- Integration: **PENDING parent selection.** Do not overwrite installed tools on
  the strength of this fragment; the guard must ship with the four candidates.
- Composition: the ctime witness closes S18's one residual G2 hole; a merged
  candidate should take the descendant-age predicate from here and S18's broader
  ledger/quarantine hardening, since the two overlap on `try_stale`.
- Open for a later round: the hold-window pin covers mtime/size per descendant
  but not content digest; a same-size same-mtime rewrite inside the window is
  still caught only by the inherited content pin on the root.
