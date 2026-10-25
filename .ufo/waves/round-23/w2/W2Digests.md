# W2Digests — every cited digest recomputed at the lane tip

Tip under attack: `102690017115cb202f292828c90b72705f69bf09` (master). Landed work:
`4765250`, `c0eeaa7`. Claims frozen in `.ufo/waves/round-23/preregistration.txt`.
All digests recomputed from git objects at the named revision
(`git cat-file -p <rev>:<path> | sha256sum`), not from the worktree copy; the worktree was
compared separately. Read-only throughout; scratch `/var/tmp/souji-r23-w2-W2Digests`
(removed at the end). No installs, no repo writes.

---

## 1. The four tool digests the records cite

| digest (cited) | cited where | recompute command | result |
|---|---|---|---|
| `617f4c96…a8c9` | `SCORECARD.md:21`, `census/round-23/records/agreement-after.tsv:4`, `…/agreement-control-base.txt:4` | `git cat-file -p 1026900:tools/souji-record-agreement.py \| sha256sum` | `617f4c9618c06254c0fd9503d76f681e56452bfff7fa3888009737ddfcdfa8c9` — **match** |
| `d5ed0805…dc9d` | `census/round-23/records/gate-check-at-lane-base.tsv:4`, `gate-check-c3.tsv:4`, `census/round-22/attempt2/instrument-digests.txt:2` | `git cat-file -p 1026900:tools/souji-gate-check.py \| sha256sum` | `d5ed0805b10f283fcc240a2daa628681a9c76bec7df1fe1cbc7e204754ecdc9d` — **match** |
| `d85c2696…6b00` | `census/round-23/records/gate-check-at-first-landing.tsv:4` (rev `a211e4d1`) | `git cat-file -p a211e4d1:tools/souji-gate-check.py \| sha256sum` | `d85c269624f4ade5c4ce5a1328c33e7a8f5169c9c14ec71f7f62f74612486b00` — **match** |
| `65817d0d…48f4` | `census/round-23/records/declared-evidence-after.tsv:4`, `instrument-digests.txt:1`, `SCORECARD.md:23` | `git cat-file -p 1026900:tools/souji-declared-evidence.py \| sha256sum` | `65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4` — **match** |

Every one also matches at `4765250` and `c0eeaa7`; `d5ed0805…` and `65817d0d…` also match at
the lane base `1208bfb`. At measurement time (05:45) the worktree copies were byte-identical to
the tip blobs; wave-2 seats have since edited three worktree files mid-flight
(`tools/souji-record-agreement.py` now `012ee7ce…`, `tools/souji-receipt-run.py` now
`d6e7e32f…`, `census/round-23/sources/qiita-gc-auto.raw` now `3274d936…`), so **only
git-object digests are stable evidence** — every verdict here is revision-scoped. The
`d85c2696…` value is legitimate at its own rev: `a211e4d1` (round-22 gate-check commit,
2026-10-25 03:42) is an ancestor of `1208bfb`, and the same path at `1208bfb` hashes
`d5ed0805…`, so the two gate-check receipts bind different tool bytes at different revisions —
not a stale digest.

**Verdict: the tool-digest limb survives — 4/4 match, 0 stale.**

## 2. C2 counter and the verifier

```
$ grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ | wc -l
5
$ for f in $(grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/); do \
    python3 -B tools/souji-receipt-run.py verify --root . "$f"; echo "exit=$?"; done
verify=ok rev=9301d98c1c689c79741f0f1ba1f171138d20af07 tool=tools/souji-declared-evidence.py …
verify=ok rev=a211e4d1bf6ea592670d16269f34e9f67f33e8b3 tool=tools/souji-gate-check.py …
verify=ok rev=1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd tool=tools/souji-gate-check.py …
verify=ok rev=476525026cdb179f2d49441e1cb6c6f7316f3124 tool=tools/souji-record-agreement.py …
verify=ok rev=476525026cdb179f2d49441e1cb6c6f7316f3124 tool=tools/souji-gate-check.py …
exit=0 (all five)
```
Files: `declared-evidence-after.tsv`, `gate-check-at-first-landing.tsv`,
`gate-check-at-lane-base.tsv`, `agreement-after.tsv`, `gate-check-c3.tsv`.
Target ≥4, observed 5, all green. **Survives.**

## 3. Snapshot digests under `census/round-23/sources/` — no claimed value exists

There are **five** files, not four. Recomputed **from the committed blobs at the tip**
(`git cat-file -p 1026900:<path> | sha256sum`); the worktree copy of `qiita-gc-auto.raw` has
since been rewritten by a wave-2 seat (`3274d936…`), so a bare `sha256sum` on the worktree no
longer reproduces the committed extract:

| file | sha256 |
|---|---|
| `git-count-objects.1.txt` | `4c540915483da5175da373ef697763f61f7959c903a06473dc0920ac89d5c2ee` |
| `git-fsck.1.txt` | `8ef1170bf5de37e85e96a416ffa5e7f0e12c4e5671e0bab0b1ca357497eaaf32` |
| `git-prune.1.txt` | `5282b2e11ece7b45df9561df76303712f3daecab496d3a798845331cc02fdd4b` |
| `qiita-gc-auto.raw` | `7d2298c139c128ddc3a68aed096e34cfe419198ddfb794e87cdf026dda3f78f8` |
| `csdn-count-objects-vh.raw` | `96aecd9198e7067026471e52baf45e33f39bc0426f95cc1dd5d3c3266222a28b` |

No digest for any of these five appears in any committed byte:
`grep -rn '96aecd91\|4c540915\|8ef1170b\|5282b2e1\|7d2298c1' .` → no hits outside `.git`.
Yet the round asserts the binding three times — `corpus/lessons/round-23.md:76` ("snapshotted
… with their sha256"), `LOG.md:1598` (same), `SCORECARD.md:23` ("snapshots
`census/round-23/sources/*` with sha256"). The entries name snapshots by path only
(`repo-size-census-readonly.md:75,78-84`; `count-objects-garbage-readings-r25.md:61-64`), the
`S115–S119` rows in `corpus/SOURCES.md` carry no digest, and nothing enforces one: the C3 gate
matches `snapshot:\s*(\S+)` only (`tools/souji-gate-check.py:41`, check4 = presence + quote),
and `scripts/sources-census.sh` has no digest logic.

**Verdict: falsified as written.** Not "stale" — there is no claimed value to be stale. The
round asserts a digest binding that no artifact carries.

Two community digests *are* published (`corpus/knowledge/count-objects-garbage-readings-r25.md:59`):
qiita `129655 bytes sha256 2020b283…`, csdn `182147 bytes sha256 5a8b27ed…`. Neither is
recomputable from the tree: the committed `.raw` files hash to `7d2298c1…` / `96aecd91…`, and
their own headers record **different fetches** (`fetched: 2026-10-25, curl rc=0, 129547 bytes`
/ `180456 bytes`) than the published sizes. So the published digests bind bytes that are not
committed, and the committed extracts have no published digest — the two halves never meet.

Not a contradiction, and not the defect: the qiita page embeds a fixed-length per-request CSRF
token. The lane already holds two 129655-byte fetches with different digests
(`.ufo/waves/round-22/attempt2/w1/evidence/rev-qiita…html` = `ecefaf6c…`,
`slice138-qiita.html` = `10773183…`, differing in 718 bytes, first at the `csrf-token` meta).
Equal size + different digest is expected. The defect is the missing binding.

Positive provenance worth recording: the three man snapshots are reproducible renders —
`MANWIDTH=100 man --nh --nj <page> | col -b` is byte-identical for all three on git 2.56.0
(tested widths 80/100/110/120/130/160; only 100 matches). The round records no render command,
so the width is inferable, not stated.

## 4. C1's cited after-receipt is red (corroborates `W2C1Ctl` F2/F3)

The tool digest `617f4c96…` matches; the *citation* does not.

```
$ test -e census/round-23/records/agreement-after.txt; echo $?      → 1 (absent)
$ head -6 census/round-23/records/agreement-after.tsv
rev=476525026cdb179f2d49441e1cb6c6f7316f3124   rc=1
$ sed -n '10p' census/round-23/records/agreement-after.tsv
keys=4 records=4 occurrences=18 mismatches=1
```
The only committed after-receipt binds the **first landing** and records `rc=1`
(K1 `value-disagree`, `SCORECARD.md:14` then carrying `assertions=55 resolved=52 skipped=33
mismatches=3`). The tip:

```
$ python3 -B tools/souji-record-agreement.py --rev 1026900… --root /home/vgpnk/Projects/shokunin/souji-shokunin
MISMATCH  K4  .ufo/waves/round-23/report-draft.md  uncommitted-path  ??
keys=4 records=4 occurrences=17 mismatches=1                       exit=1
$ … --no-worktree
keys=4 records=4 occurrences=17 mismatches=0                       exit=0
```
Re-run from the **immutable tip blob** (copied out of git so the moving worktree cannot change
which bytes ran; sha256 of the copy `617f4c96…`):

```
$ git cat-file -p 1026900:tools/souji-record-agreement.py > /var/tmp/…/ra-tip.py
$ python3 -B /var/tmp/…/ra-tip.py --rev 1026900… --root <lane>
  → 41 × K4 uncommitted-path (every modified worktree file plus every untracked w2 report)
    keys=4 records=4 occurrences=17 mismatches=41                    exit=1
$ python3 -B /var/tmp/…/ra-tip.py --rev 1026900… --root <lane> --no-worktree
  → keys=4 records=4 occurrences=17 mismatches=0                     exit=0
```
The live-worktree arm is a moving target: 1 at 05:45 (only `report-draft.md` untracked), 41 at
05:52 (12 modified files + 27 untracked w2 reports). Only `--no-worktree` is stable, and the
preregistration's frozen command (`preregistration.txt:22-23`) does not include it.
So `SCORECARD.md:21`, `LOG.md:1578` and `corpus/lessons/round-23.md:22` cite a path that does
not exist and report `0` where the receipt they name says `1`. The 0-state is real but
**unbound by any receipt**, and the printed counting command (no `--no-worktree`) exits 1 at the
tip while wave-2 files are untracked. The 1→0 flip between `4765250` and `c0eeaa7` came from
inserting a revision token next to the before-tuple in `SCORECARD.md:14` (reflow diff), not from
changing a number.

## 5. SCORECARD capability rows — do the cited commands run?

Run from the lane root. Every cited command that is executable runs; one cited count is stale
and one citation is not runnable as written.

| row | command | cited | observed | verdict |
|---|---|---|---|---|
| maintenance-guard gate | `bash tests/fixtures/r12-maintenance-guard.sh --selftest` | 6/6 | `selftest=PASS ids=6/6` rc 0 | runs, count matches |
| declared-evidence integrity | `python3 tools/souji-cert-evidence.py --selftest` | 36/36 | `selftest: 36/36 passed` rc 0 | matches |
| bounded quarantine ops | `bash tests/fixtures/r13-quarantine-bounds.sh` | 5/5 | `total=5 failed=0 hung=0` rc 0 | matches |
| repository structure census | `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` | 5/5 | `selftest=PASS ids=5/5` rc 0 | matches |
| landing-claim gate | `python3 tools/souji-landing-gate.py --selftest` | **18/18** | `SELFTEST pass=65 fail=0` rc 0 | runs, **cited count stale** (output contains no `18/18`) |
| landing-claim gate | `python3 tests/fixtures/r16-landing-gate.py` | 15/15 | `SUMMARY total=15 failed=0` rc 0 | matches |
| census hygiene (r17) | `python3 tests/fixtures/r17-census-hygiene.py --census tools/souji-census.sh` | 29/0 | `SUMMARY total=29 failed=0` rc 0 | matches |
| jj-aware receipts | `bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` | 35/0 | `total=35 failed=0 skipped=2` rc 0 | matches |
| durable revision stamps | `python3 tools/souji-rev-pin.py --selftest` | 11/0 | `total=11 failed=0` rc 0 | matches |
| durable revision stamps | `python3 tests/fixtures/r19-rev-pin.py` | 13/0 | `total=13 failed=0 base_discriminating=6` rc 0 | matches |
| declared-evidence audit | `python3 tools/souji-declared-evidence.py --selftest` | 8/8 | `selftest=8/8` rc 0 | matches |
| blob-bound receipts (r23) | `python3 tests/fixtures/r23-receipt-run.py` | 8/8 | `selftest=8/8` rc 0 | matches |
| record agreement audit (r23) | `python3 tests/fixtures/r23-record-agreement.py` | 9/9, `control=FALSE-GREEN-REJECTED` | `selftest=9/9` + `control=FALSE-GREEN-REJECTED` rc 0 | matches |
| reproducible seat audit | `python3 census/round-17/seat-audit-replay.py …` | — | file exists; argv has a **literal `…`** | **not runnable as written** |
| reproducible seat audit | `census/round-17/transcript-manifest.py --check census/round-16/transcripts` | — | `check OK: 144 files verified` rc 0 | runs |

All 30 backticked evidence paths in the capability table exist (checked with `os.path.exists`,
30 OK / 0 missing). The rows without a runnable command cite data artifacts (JSON/TSV), not
commands, so they were checked for existence only.

## Verdicts

| limb | verdict |
|---|---|
| four tool digests (`617f4c96`, `d5ed0805`, `d85c2696`, `65817d0d`) | **survives** — 4/4 match at their named revisions, worktree included |
| C2 counter + verifier (`grep … \| wc -l` = 5, all `verify=ok`) | **survives** |
| snapshot sha256 limb ("snapshotted … with their sha256") | **falsified** — zero published digests; the two published community digests bind fetches absent from the tree |
| C1 after-state citation | **falsified** — cited `agreement-after.txt` absent; the real `.tsv` says `rc=1 / mismatches=1`; the 0-state has no receipt |
| SCORECARD capability commands | **runs** — one stale count (`landing-gate` 18/18 vs 65/0), one `…` citation |

## What the round must do

1. **fix (C1)** — `SCORECARD.md:21`, `LOG.md:1578`, `corpus/lessons/round-23.md:22`: cite
   `census/round-23/records/agreement-after.tsv` as the `4765250` run (`rc=1`, `mismatches=1`),
   and commit a receipt for the tip run (`--rev 1026900… --no-worktree` → `mismatches=0`) as the
   after-value. As written the round reproduces the D2 defect it claims to close.
2. **fix (C3 prose)** — either publish the five `census/round-23/sources/` digests in the entry
   Gate (or a manifest) or drop "with their sha256" from `corpus/lessons/round-23.md:76`,
   `LOG.md:1598`, `SCORECARD.md:23`. Record the render command (`MANWIDTH=100 man --nh --nj … |
   col -b`) so the snapshots are reproducible, not just present.
3. **disclose or fix (`count-objects-garbage-readings-r25.md:59`)** — the published fetch digests
   bind bytes that are not in the tree, and the `.raw` headers record different fetch sizes. Either
   commit the full fetched pages whose digests are published, or publish the digests of the
   committed extracts and state the sizes those extracts came from.
4. **fix (capability row, landing-claim gate)** — `18/18` → the current `SELFTEST pass=65 fail=0`.
5. **fix (capability row, reproducible seat audit)** — replace the literal `…` with the runnable
   argv (or mark the row historical with its measured commit).

## Remaining unknowns

- Whether `2020b283…` was a real 2026-10-25 fetch: unrecomputable from tree bytes; a live
  re-fetch cannot settle a past fetch (the CSRF token rotates).
- Whether a tip-state agreement receipt was produced and dropped: no committed byte records
  `keys=4 … occurrences=17 mismatches=0`, and no scratch receipt was found under the lane.

## Note

This report is itself an untracked path under `.ufo/waves/round-23/`; like
`report-draft.md`, it adds one K4 `uncommitted-path` row to any live-worktree run of the C1
counter while wave 2 is open (41 such rows at 05:52). That is the wave-2 artifact effect the
round's `LOG.md` limit ("K4 is worktree-scoped") does not spell out. Wave-2 seats also edited
lane bytes mid-flight (`tools/souji-record-agreement.py`, `tools/souji-receipt-run.py`,
`census/round-23/sources/qiita-gc-auto.raw`), so any digest quoted from the worktree — rather
than from `git cat-file -p 1026900:…` — is already stale. Scratch
`/var/tmp/souji-r23-w2-W2Digests` removed.
