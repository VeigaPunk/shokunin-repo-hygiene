# SwarmMutationTester15 — mutation-test of the C2 repairs as landed (round 32, a2w1)

## Status
STATUS: PASS — all five re-introduced `/var/tmp` mutants FAIL their items under the frozen v1 counter (4 clean kills, 0 survivors; MUT4 recorded inconclusive-per-rule only because T12's pristine baseline itself flakes in this environment, its mutation-specific crash proven separately), and the Critic34-style clone-local-scratch cheat is accepted by v1 exactly as wave 1 disclosed.

## Evidence

Revisions: base `85b61a151923986e7e6b48f7084b9122561b5f3d`; item list `3ec84fc81b3243429c834a051880b0bcde06291c`; C2 landing `98e5203d45b4e419a9e72801733d93303acc7ebd` (verified ancestor of lane master tip `4e56c48b8fc828f9aba2746e324dc46aa538bdbf`). Counter bytes read from the lane working tree at that tip. Scratch clone `/fast/scratch/hyaku/souji-r32/MutateC2Repairs/c` (`git clone --no-local`, `origin` removed, `rev-parse --show-toplevel` verified); throwaway identity set with `git -C <scratch> config` only. bwrap and strace were already on PATH; no tool was installed or upgraded.

Counter command per mutant (`--only` = the items whose `files` column names the mutated file):

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-32/c2-counter.py \
  --root /fast/scratch/hyaku/souji-r32/MutateC2Repairs/c --rev <mutant> \
  --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c \
  --only <ids> --scratch /fast/scratch/hyaku/souji-r32/MutateC2Repairs/cnt
```

One mutant per commit, each a child of `98e5203…` (branch per mutant; every other patched file pristine):

| mutant | commit | file:line at 98e5203 | mutation | --only | counter output (excerpt) | verdict |
|---|---|---|---|---|---|---|
| MUT1 | `932086f6d49696dd003c6a8266c005408b09d5ba` | `tools/souji-landing-gate.py:1183` | `snapdir = tempfile.mkdtemp(prefix="souji-landing-gate-", dir="/var/tmp")` | T01,T02,T29,T30 | `T01 FAIL base=rc0:W8306:SELFTEST pass=65 fail=0 sbox=rc1:W128:OSError: [Errno 30] Read-only file system` / `T02 FAIL … sbox=rc2:W0:SUMMARY … checked_reg=0` / `T29 FAIL … sbox=rc1:W681:cases=7 pass=1` / `T30 FAIL … sbox=rc1:W865:cases=10 pass=0`; `SUMMARY items=4 pass=0 fail=4` | KILLED (4/4) |
| MUT2 | `cbe034f3b1222de5c7ee07638524a9b260e2a2c4` | `tools/souji-gate-check.py:232` | `base = tempfile.mkdtemp(prefix="souji-gate-check-", dir="/var/tmp")` | T05 | `T05 FAIL base=rc0:W20:selftest=9/9 sbox=rc1:W0:OSError: [Errno 30] Read-only file system`; `SUMMARY items=1 pass=0 fail=1` | KILLED |
| MUT3 | `8d6083f01260d7279e24b44e05d7a4dd3c85fbac` | `tests/fixtures/r24-size-census.py:30` | `SCRATCH_PARENT = '/var/tmp'` | T23 | `T23 FAIL base=rc0:W1217:cases=12 pass=12 … sbox=rc1:W0:cases=12 pass=0 control=FALSE-GREEN-ACCEPTED lost_found=NOT-DETECTED`; `SUMMARY items=1 pass=0 fail=1` | KILLED |
| MUT4 | `cd4006f732ce98eb18ea1d698098474734c3125c` | `tools/souji-census.sh:309` | `CENSUS_TMP=$(mktemp -d /var/tmp/souji-census-now.XXXXXX)` | T12 | `T12 FAIL base=rc0:W5409:selftest: 69 checks, 0 failed sbox=rc1:W335:NONE`; `SUMMARY items=1 pass=0 fail=1` | INCONCLUSIVE (see Finding 4) |
| MUT5 | `a8522535341d4c7d769a54da4bb729179aed8d74` | `tests/fixtures/r27-pre-report-gate.sh:7` | `D=$(mktemp -d /var/tmp/souji-r27-pre-report.XXXXXX)` | T26 | `T26 FAIL base=rc0:W534:cases=4 pass=4 … sbox=rc1:W0:NONE`; `SUMMARY items=1 pass=0 fail=1` | KILLED |

Survivors: none.

Pristine controls, same counter, `--rev 98e5203…`, this environment: T05+T23+T26 `SUMMARY items=3 pass=3 fail=0`; T01+T02+T29+T30 `SUMMARY items=4 pass=4 fail=0`; T06 `ITEM T06 PASS base=rc0:W110:SUMMARY total=11 failed=0 sbox=rc0:W111:SUMMARY total=11 failed=0` (byte-identical to the T06 line in attempt-1's `census/round-32/records/c2-after-v1.txt`). T12 control FAILED twice — `base=rc0:W5422:selftest: 69 checks, 0 failed sbox=rc1:W6055:selftest: 69 checks, 4 failed`, then solo `base=rc0:W5352:selftest: 69 checks, 0 failed sbox=rc1:W6066:selftest: 69 checks, 2 failed`.

Manual T12 reproduction at `98e5203…` (strace on both runs, bwrap only on the second, sequential, otherwise idle machine): unsandboxed `rc=1`, `selftest: 69 checks, 1 failed`, line `FAIL watchdog wall time 6090ms (want < 6000ms)`; sandboxed `rc=1`, `selftest: 69 checks, 2 failed`, lines `FAIL watchdog neighbour neighbour-a fields=0/0/error` and `FAIL watchdog wall time 8125ms (want < 6000ms)`.

MUT4 sandboxed death point (manual bwrap run of the mutant, stderr): `mktemp: failed to create directory via template '/var/tmp/souji-census-now.XXXXXX': Read-only file system` — the selftest dies before printing any summary (stdout empty), rc 1.

Restoration: work tree checked back out at `98e5203…`, `git status --porcelain` = 0 lines, and the six touched files' blob hashes at HEAD equal the pre-mutation hashes taken before any edit — `7489334c…` souji-landing-gate.py, `ea268127…` souji-gate-check.py, `eae7f032…` r24-size-census.py, `c1671f4c…` souji-census.sh, `20763efd…` r27-pre-report-gate.sh, `e41c74d0…` souji-rev-pin.py. Mutant bytes for the record: `51766e6d…` (MUT1), `77e00e71…` (MUT2), `de47e735…` (MUT3), `243aa124…` (MUT4), `0cb21524…` (MUT5), `e9d21f0b…` (cheat).

## Findings

1. **MUT1 killed on every item that reaches the snapshot** — `tools/souji-landing-gate.py:1183` at `98e5203…`. T01 crashes (`OSError … Read-only file system`), T02 degrades to exit 2 with a zeroed summary, T29 drops 7→1 passing cases, T30 drops 10→0. The repair's snapshot root is load-bearing for all four enumerated landing-gate items.
2. **MUT2, MUT3, MUT5 killed structurally** — `tools/souji-gate-check.py:232`, `tests/fixtures/r24-size-census.py:30`, `tests/fixtures/r27-pre-report-gate.sh:7`. Each sandboxed run dies on the ro-bound `/var/tmp` (traceback, all 12 cases erroring with `control=FALSE-GREEN-ACCEPTED lost_found=NOT-DETECTED`, or no output at all), so the counter's `regress work-dropped` verdict is attributable to the mutation alone; pristine controls pass 3/3 and 4/4.
3. **MUT4 inconclusive-per-rule, mutation effect nonetheless proven** — `tools/souji-census.sh:309`. The pristine T12 baseline fails the counter in this environment (Finding 6), so per the detector discipline a baseline failure is inconclusive, not a killed mutant. The mutant's sandboxed selftest dies before any summary line with the `mktemp … /var/tmp … Read-only file system` error, a deterministic consequence of the mutation, so in any environment where pristine T12 passes, this mutant must fail.
4. **T12 is not a stable anchor; the C2 `fail=0` target is environment-sensitive for it.** The census selftest's watchdog checks are wall-time-budgeted — `FAIL watchdog wall time 8125ms (want < 6000ms)` — and flip stochastically under strace/bwrap overhead (1–4 failed checks per run here). Attempt-1's after-record `census/round-32/records/c2-after-v1.txt` shows T12 `PASS` with `base=rc1:…69 checks, 6 failed sbox=rc1:…69 checks, 6 failed` — a pass by *matching failure counts*, not clean runs. My re-derivation of T12 at the landing commit reads FAIL here, so that after-record line does not reproduce outside its environment (the goal marks attempt-1 after-records unverified until re-derived; this is a re-derivation discrepancy for the L1).
5. **The Critic34 gap is open at the landing rev and unamended.** `census/round-32/records/amendments.txt` states: quote "No amendment for C1 or C2 after data." (location: `census/round-32/records/amendments.txt`, last paragraph), and discloses: quote "the v1 C2 predicate also accepts a clone-local scratch and a fabricated anchor with dummy files" (same location). No `c2-counter-v2.py` exists in `census/round-32/`. The predicate `ok_a = rc1 == rc0 and s1 == s0 and s0 != "NONE"` (`census/round-32/c2-counter.py:174`) plus the work gate on :175 count creations regardless of destination, and the sandbox on :154-155 — quote `"bwrap", "--dev-bind", "/", "/", "--ro-bind", empty, "/tmp", "--ro-bind", empty, "/var/tmp"` — leaves the clone and `$HOME` writable.
6. **Cheat reproduced against a patched item at the landed rev** (see Attack log): v1 accepts it, `ITEM T06 PASS`, output byte-identical to the pristine control's T06 line.

## Attack log

- **Probe 1 — reintroduce a hard-coded `/var/tmp` scratch root, one mutant per commit, five patched files.** All five mutants FAIL their items (table above); four kills are clean (pristine control passes, mutant fails structurally), MUT4 is inconclusive-per-rule with the mutation-specific crash documented. No survivors.
- **Probe 2 — Critic34-style cheat, scratch inside the clone.** Commit `14dd98ee2542c4b8f4837be830dc575fc7daeb48` (branch `cheat`, child of `98e5203…`) changes `tools/souji-rev-pin.py:253-256` so the selftest's `mkdtemp` parent is `<repo>/tools/../.selftest-scratch` (created with `os.makedirs`), ignoring the caller's `TMPDIR`. Counter: `ITEM T06 PASS base=rc0:W110:SUMMARY total=11 failed=0 sbox=rc0:W111:SUMMARY total=11 failed=0`, exit 0 — v1 accepts it, as wave 1's SwarmCritic34 reported (quote "Cheat A — clone-local scratch passes.", location `.ufo/waves/round-32/w1/SwarmCritic34.md`, Finding 2). Destination proof: `strace -f -e trace=mkdir,mkdirat` over the cheat's selftest shows 14 trace lines creating under `<clone>/.selftest-scratch/souji-rev-pin-selftest-dbb7q4gb/…` and 0 under the caller's `TMPDIR` probe directory.

## Deliveries
- `.ufo/waves/round-32/a2w1/SwarmMutationTester15.md` (this report)

Lane untouched except this report file (lane `git status` showed 4 pre-existing dirty lines belonging to the L1's integration; I added none). No tool installed or upgraded. Scratch `/fast/scratch/hyaku/souji-r32/MutateC2Repairs` removed after this report was written.

Report: .ufo/waves/round-32/a2w1/SwarmMutationTester15.md
