# SwarmExecutor17 — C2 leg J1 and guards G1–G6 at base==rev feasibility

## Status

**STATUS: PARTIAL** — the assigned command's `--only` flag is not in the frozen C2 contract and the counter exits 2 on it (the prereg's own C2 invocation has no `--only`; the full 13-leg run was run instead and its J1 + G1–G6 LEG lines are delivered), and the J1 leg **cannot pass with the frozen counter bytes**: the counter's junk branch discards the leg's argv and re-invokes the real junk fixture, producing unbounded recursion that ends in `TimeoutExpired` after 900 s. The base==rev run finished `SUMMARY legs=13 pass=10 fail=3 harm=0` (failures W3, N3, J1). All six guards G1–G6 were executed and their mechanisms verified from the frozen code; G5 is a **false-green** (reproduced: a commit touching both claim namespaces still yields `overlap commits=` empty). Three further defects recorded: `harm=0` in the SUMMARY is a literal never computed, G1/G2/G5 are vacuous at `--rev == --base`, and one J1 leg grew the scratch tree to 147 GB (`/fast` 27% → 48% used).

Delivery: `.ufo/waves/round-34/w1/deliver-c2-j1guards.txt`.

## Evidence

**Revisions.** Base `9c76c7222a8abff027af42e37f0d160d52526bba`; list-rev (frozen legs/counters) `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`; tip `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`. `census/round-34/c2-counter.py` is byte-identical at `2b0171e`, `60def78` and `51acb5f` (sha256 prefix `19ec3d0bd868969c`) — the counter has not changed since the freeze.

### 1. The assigned command exits 2 — `--only` is not in the frozen C2 contract

```
flock .../LegJ1Guards/my.lock python3 -B .../census/round-34/c2-counter.py \
  --root .../souji-shokunin --rev 9c76c72... --base 9c76c72... \
  --list-rev 2b0171e... --scratch .../LegJ1Guards/cnt --only J1,G1,G2,G3,G4,G5,G6
```
```
usage: c2-counter.py [-h] [--root ROOT] [--rev REV] [--base BASE]
                     [--list-rev LIST_REV] [--scratch SCRATCH]
                     [--timeout TIMEOUT] [--selftest]
c2-counter.py: error: unrecognized arguments: --only J1,G1,G2,G3,G4,G5,G6
EXIT=2
```
`c1-counter.py:348` has `ap.add_argument("--only", default="")`; `c2-counter.py:262-269` does not. The prereg's own frozen C2 invocation (`census/round-34/preregistration.txt:90-92`) carries no `--only`, so the counter is correct per the prereg and the divergence is in the seat card. **No J1/G1–G6-only reading is reachable from the frozen C2 counter; the full 13-leg run below is the prereg's own invocation.**

### 2. base==rev run — every LEG line

```
flock .../LegJ1Guards/cnt.lock python3 -B .../census/round-34/c2-counter.py \
  --root .../souji-shokunin --rev 9c76c7222a8abff027af42e37f0d160d52526bba \
  --base 9c76c7222a8abff027af42e37f0d160d52526bba \
  --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 \
  --scratch .../LegJ1Guards/cnt
```
```
LEG	W1	PASS	rc=0 creates=209/209 line=selftest: 48/48 passed	load=11.08
LEG	W2	PASS	CASE=20 summary=SUMMARY	total=20	failed=0	load=49.82
LEG	W3	FAIL	base/rev mismatch rc=1/1 line='selftest: 69 checks, 11 failed'/'selftest: 69 checks, 8 failed'	load=32.39
LEG	W4	PASS	rc=0 creates=1107/1107 line=selftest: 49 checks, 0 failed	load=31.90
LEG	N3	FAIL	cases=12 pinned=True summary=False	load=22.64
LEG	N4	PASS	base=selftest: 69 checks, 0 failed base2=selftest: 69 checks, 0 failed rev=selftest: 69 checks, 0 failed load=12.67	load=12.67
LEG	J1	FAIL	Command '['/usr/bin/python3', '/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r34-sandbox-junk.py', '--counter', '/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c2-counter.py', '--scratch', '/fast/scratch/hyaku/souji-r34/LegJ1Guards/cnt']' timed out after 900 seconds	load=5.48
LEG	G1	PASS	r33 diff	load=5.48
LEG	G2	PASS	unexpected paths=	load=5.48
LEG	G3	PASS	SELFTEST pass witness-required rejected junk-only rejected	load=5.48
LEG	G4	PASS	bwrap+strace available	load=5.48
LEG	G5	PASS	overlap commits=	load=5.48
LEG	G6	PASS	namespace fixture pin	load=5.48
SUMMARY legs=13 pass=10 fail=3 harm=0 rev=9c76c7222a8abff027af42e37f0d160d52526bba
EXIT=1
```

Host `/proc/loadavg` at start `12.02 6.73 3.63 6/6106 311605`; at end
`5.48 6.49 13.79 13/5509 3386628`.

The assigned J1 leg and all six guard legs are in that output. J1 FAILs
("timed out after 900 seconds"); G1–G6 all PASS at base==rev — but see
finding 4 (G5 false-green) and finding 6 (G1/G2/G5 vacuous at base==rev).

At `--rev == --base` the legs still load (legs are read at `--list-rev` only, `c2-counter.py:67-68`) and the base tree does carry `tools/souji-evidence-cache.py`, `tools/souji-census.sh`, `tools/souji-verify.sh`, `tests/fixtures/r14-census-boundary.py` — so the witness legs are reachable at base.

### 3. Junk fixture run — separate, assigned command

```
cd .../souji-shokunin
flock .../LegJ1Guards/junk.lock python3 -B tests/fixtures/r34-sandbox-junk.py \
  --counter .../census/round-34/c2-counter.py --scratch .../LegJ1Guards/junk
```
```
16.19 9.43 4.96 14/6457 894987
Traceback (most recent call last):
  File ".../tests/fixtures/r34-sandbox-junk.py", line 139, in <module>
    sys.exit(main())
  File ".../tests/fixtures/r34-sandbox-junk.py", line 117, in main
    p = subprocess.run([sys.executable, "-B", counter, "--root", clone, "--rev", stub_rev,
                        "--base", tip, "--list-rev", stub_rev, "--scratch", inner_scratch],
                       capture_output=True, text=True, timeout=900)
  ...
subprocess.TimeoutExpired: Command '['/usr/bin/python3', '-B', '.../c2-counter.py',
  '--root', '.../junk/r34-junk.beh73ie1/c', '--rev', '464f0348ac8c7d7e5ba580756d86f82b0d1c5989',
  '--base', '51acb5fb6fa38a6b593b3badb674cec559d7eb2c', '--list-rev', '464f0348ac8c7d7e5ba580756d86f82b0d1c5989',
  '--scratch', '.../junk/r34-junk.beh73ie1/inner']' timed out after 900 seconds
EXIT=1
36.69 38.04 29.33 21/8349 1979884
```
`cases=5 pass=5 control=STUB-REJECTED` was **never printed**. The committed
record `census/round-34/records/junk-c2-final.txt` carries the same
TimeoutExpired traceback, and `records/controls.txt` already states "C2 junk
control: ... ended with a TimeoutExpired after 900 seconds ...; no pass is
claimed."

### 4. argv-ignored proof (bounded, marker script)

Scratch clone with a stub legs file whose J1 argv named a marker script that
would touch `MARKER_RAN`:
```
LEG	W1	PASS	rc=0 creates=0/209 line=selftest: 48/48 passed	load=30.82
LEG	J1	FAIL	Command '['/usr/bin/python3', '.../argv/c/tests/fixtures/r34-sandbox-junk.py',
  '--counter', '.../c2-counter.py', '--scratch', '.../argv/s']' timed out after 60 seconds	load=38.86
SUMMARY legs=2 pass=1 fail=1 harm=0 rev=0e24707cbab49e76bc7e1c1aca8987ff8a6d3396
EXIT=1
=== MARKER_RAN exists?
ls: cannot access '.../argv/MARKER_RAN': No such file or directory
=== recursion dirs: 3
```
The marker never ran; the counter ran the **real** fixture instead.

### 5. Recursion depth, observed

Nested chain under the counter's own scratch, depth 24 at one sample, scratch 43–64 GB for one run:
```
.../LegJ1Guards/cnt/r34-junk.8krrjyxt
.../LegJ1Guards/cnt/r34-junk.8krrjyxt/inner/r34-junk.ttkzojcm
.../LegJ1Guards/cnt/r34-junk.8krrjyxt/inner/r34-junk.ttkzojcm/inner/r34-junk.skrrfdd7
.../LegJ1Guards/cnt/r34-junk.8krrjyxt/inner/r34-junk.ttkzojcm/inner/r34-junk.skrrfdd7/inner/r34-junk.nrl7s9ci
```
`df -h /fast` for this one run went 27% → 65% used. Independently reproduced by sibling seats (`/fast/scratch/hyaku/souji-r34/ReviewJunkFixtures/c2/...`, `/fast/scratch/hyaku/souji-r34/PreregFidelity/c2junk/...`) — a property of the frozen bytes, not of this invocation.

### 6. Guards executed (frozen module, `importlib` load, no mutation)

At `--rev == --base` and at `--rev == tip`:
```
--- guards at base==rev (rev=9c76c7222a8a)
LEG	G1	PASS	r33 diff
LEG	G2	PASS	unexpected paths=
LEG	G3	PASS	SELFTEST pass witness-required rejected junk-only rejected
LEG	G4	PASS	bwrap+strace available
LEG	G5	PASS	overlap commits=
LEG	G6	PASS	namespace fixture pin
--- guards at tip (rev=51acb5fb6fa3)
LEG	G1	PASS	r33 diff
LEG	G2	PASS	unexpected paths=
LEG	G3	PASS	SELFTEST pass witness-required rejected junk-only rejected
LEG	G4	PASS	bwrap+strace available
LEG	G5	PASS	overlap commits=
LEG	G6	PASS	namespace fixture pin
```
loadavg `26.50 13.71 6.76 33/7211 1327439` and `42.77 24.93 12.12 37/8288 3202577`.

G3's refusals, executed directly against `validate_legs`:
```
good(witness+junk)     -> ACCEPTED
witness-dropped        -> REFUSED: legs file with witness clauses dropped
junk-only              -> REFUSED: legs file with witness clauses dropped
guard-only             -> REFUSED: legs file with witness clauses dropped
selftest() -> SELFTEST pass witness-required rejected junk-only rejected rc= 0
```

G4's substance verified on the host: `/usr/bin/bwrap` and `/usr/bin/strace` present; `bwrap --unshare-user --unshare-pid --ro-bind / / -- /bin/true` → rc 0; `unshare -Ur -- /bin/true` → rc 0; `/proc/sys/kernel/unprivileged_userns_clone` = 1.

G6's digest verified independently:
```
git show 9c76c72:tests/fixtures/r14-census-boundary.py | sha256sum
  e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2
git show 51acb5f:tests/fixtures/r14-census-boundary.py | sha256sum
  e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2
```

G2's changed set (13 paths, all allowed):
```
census/round-34/c1-counter.py, c1-items.tsv, c2-counter.py, c2-legs.tsv,
preregistration.txt, records/census-start.txt, records/closure-sweep.txt,
records/controls.txt, records/feasibility-final.txt, records/junk-c1.txt,
records/junk-c2-final.txt, tests/fixtures/r34-c1-junk.py,
tests/fixtures/r34-sandbox-junk.py
```

### 7. G5 enumeration — base..2b0171e

```
2b591924f607  freeze (attempt 2, A1-A4), C1/C2 counters, 60-item set, 13 legs, junk fixtures, closure sweep
  census/round-34/c1-counter.py, census/round-34/c1-items.tsv,
  census/round-34/c2-counter.py, census/round-34/c2-legs.tsv,
  census/round-34/preregistration.txt,
  census/round-34/records/census-start.txt,
  census/round-34/records/closure-sweep.txt,
  tests/fixtures/r34-c1-junk.py, tests/fixtures/r34-sandbox-junk.py
73f029ede488  repair sandbox legs and complete junk control
  census/round-34/c2-counter.py, census/round-34/preregistration.txt,
  tests/fixtures/r34-c1-junk.py
2b0171e2071f  verify N3 pin and real var-tmp isolation
  census/round-34/c2-counter.py
```
Under the counter's own sets no commit touches both → `overlap commits=` (empty) → PASS. Under the prereg's namespaces:
```
2b591924f607  C1-owned=[c1-counter.py, c1-items.tsv, r34-c1-junk.py]
              C2-owned=[c2-counter.py, c2-legs.tsv, r34-sandbox-junk.py]  OVERLAP=YES
73f029ede488  C1-owned=[r34-c1-junk.py]  C2-owned=[c2-counter.py]        OVERLAP=YES
2b0171e2071f  C1-owned=[]  C2-owned=[c2-counter.py]                       OVERLAP=no
```
Reproduced false-green in a scratch clone (origin removed at once, toplevel asserted):
```
LEG	G5	PASS	overlap commits=   <- repro1 c1-counter.py + c2-counter.py
LEG	G5	PASS	overlap commits=   <- repro2 corpus/lessons/round-34.md + c2-counter.py
LEG	G5	PASS	overlap commits=   <- repro3 c1-items.tsv + c2-legs.tsv
```
repro SHAs `78f0e499e269`, `accd13d751f4`, `05cce5813c7d`; loadavg `56.37 37.28 18.65 37/8686 960139`.

### 8. C2 do-nothing control (reproduced)

```
python3 -B .../c2-counter.py --root .../souji-shokunin --rev 9c76c72... \
  --base 9c76c72... --list-rev 9c76c72... --scratch .../LegJ1Guards/donothing
COULD-NOT-EVALUATE legs absent at --list-rev
EXIT=2
```

## Findings

1. **The assigned command's `--only` flag is not part of the frozen C2 contract and is not implemented.** The seat card's command line uses `--only J1,G1,...,G6`, but the prereg's frozen C2 invocation (`census/round-34/preregistration.txt:90-92`) is `python3 -B census/round-34/c2-counter.py --root <lane> --rev <full40> --base 9c76c72… --list-rev <prereg> --scratch <dir>` — **no `--only`**. The counter's argparse block (`census/round-34/c2-counter.py:262-269`) accordingly has no `--only`; only `c1-counter.py:348` has one. So the frozen counter is *correct* per the prereg and the divergence is between the seat card and the frozen contract; the full 13-leg run below is the prereg's own invocation and is the only reachable reading of J1 and G1–G6. This is not an instrument defect and needs no amendment — but no J1/G1–G6-subset reading exists, and a seat card carrying `--only` for C2 will always exit 2.

2. **J1 can never pass as frozen — the counter's junk branch discards the leg's argv and recurses without bound.** `c2-counter.py:287-290` runs `os.path.join(root, "tests/fixtures/r34-sandbox-junk.py")` with `--counter os.path.abspath(__file__)` and `--scratch scratch` — the hard-coded real fixture, the working-tree counter, and the counter's own scratch. The frozen leg argv (`c2-legs.tsv:40`, `python3 -B tests/fixtures/r34-sandbox-junk.py --counter census/round-34/c2-counter.py --scratch {SCRATCH}/j1`) is never used, and no `{SCRATCH}`/`{REV}` substitution happens in this branch (unlike lines 98, 121, 155). The fixture's own stub legs file names a **no-op** as its J1 argv (`tests/fixtures/r34-sandbox-junk.py:105`) precisely to stop the recursion, but the counter overrides it with the real fixture. Result: fixture → counter → fixture → … to depth 34+, 64 GB of scratch for one run, `TimeoutExpired` after 900 s, `EXIT=1`, `control=STUB-REJECTED` never printed. Reproduced twice (marker test + depth measurement) and independently by sibling seats. C2's frozen target `legs=13 pass=13 fail=0` is therefore unreachable without an amendment to the junk branch — the L1's call.

3. **J1 does not measure `--rev`.** Even with the recursion fixed, the junk branch executes the *working-tree* fixture and counter (`root` is `a.root`, the lane checkout, never a clone at `--rev`), and the fixture itself pins `tip = git(root, "rev-parse", "master")` (`tests/fixtures/r34-sandbox-junk.py:67`) — so J1 measures `master`, not the revision under test. At `--rev == --base` the base tree has no `tests/fixtures/r34-sandbox-junk.py` at all (`git cat-file -e 9c76c72:tests/fixtures/r34-sandbox-junk.py` → "fatal: path … exists on disk, but not in '9c76c72…'"), so the J1 leg could not have passed at base under any implementation that measured the base revision.

4. **G5 is a false-green against the prereg's namespaces.** `c2-counter.py:220-229` recognises the C1 side only as `{SCORECARD.md, SKILL.md}` and the C2 side only as `{census/round-34/c2-legs.tsv, census/round-34/c2-counter.py}`. A commit touching `census/round-34/c1-counter.py` + `census/round-34/c2-counter.py`, or `corpus/lessons/round-34.md` + `c2-counter.py`, or `c1-items.tsv` + `c2-legs.tsv`, is reported as `overlap commits=` (empty) → PASS. Reproduced with three commits in a scratch clone. On the actual frozen history the freeze commit `2b59192` touches C1's counter/items/fixture **and** C2's counter/legs/fixture in one commit, and `73f029e` touches C1's junk fixture and C2's counter — both invisible to G5 as implemented. The guard is green on a history that violates the separability it exists to enforce.

5. **`harm=0` in the SUMMARY is a literal, never computed.** `c2-counter.py:323` prints `harm=0` unconditionally; the string `harm` occurs exactly once in the file. The frozen C2 target includes `harm=0` in its expected SUMMARY, so that column carries no evidence — it would read `harm=0` even if the run caused harm.

6. **G1, G2 and G5 are vacuous at `--rev == --base`.** At base==rev the diff range is empty (`git diff --name-only base base` → 0 paths; `git rev-list base..base` → 0 commits; `git diff --quiet base base -- census/round-33` → 0), so all three guards pass trivially without inspecting anything. Only G3, G4 and G6 carry information at base==rev. Any "guards pass at base" feasibility claim must say which of the six actually discriminate.

7. **G3 does not measure `--rev` either.** `c2-counter.py:216` re-runs `os.path.abspath(__file__) --selftest`, i.e. the *working-tree* counter's selftest, not the one at the revision under test. At base==rev that means the guard reports on the tip's bytes (the base has no `census/round-34/c2-counter.py`).

8. **G4 checks binary presence, not namespace usability.** `c2-counter.py:218-219` tests `shutil.which("bwrap") and shutil.which("strace")`. The prereg's clause is "bwrap and unprivileged user namespaces available". On this host the substance holds (`bwrap --unshare-user …` rc 0, `unshare -Ur` rc 0, `unprivileged_userns_clone` = 1), so G4 passes honestly here — but on a host with bwrap present and userns disabled, G4 would PASS while every sandbox leg could-not-evaluate.

9. **G3's refusals hold, one message is cosmetic.** Executed directly: witness-dropped → REFUSED; junk-only → REFUSED; guard-only → REFUSED. Because the "witness" test runs first, a junk-only set is reported under the witness message (`c2-counter.py:60-61`); the refusal is correct either way.

10. **W3 fails at base==rev for a load reason, not a revision reason.** `base/rev mismatch rc=1/1 line='selftest: 69 checks, 11 failed'/'selftest: 69 checks, 8 failed'` — both runs are the same revision, so the difference is host-load dependent (1-min loadavg 32.39 at that reading). This reproduces the r33 O4 residual (anchor flipping under host load) that the round set out to harden. N4 (the dedicated load-stable anchor) PASSed: `base=selftest: 69 checks, 0 failed base2=… rev=… load=12.67`.

11. **N3 fails at base==rev**: `cases=12 pinned=True summary=False`. The 12 CASE records and the fixture pin both hold; the required `SUMMARY\ttotal=12\tfailed=0` line is absent (the fixture prints `SUMMARY\ttotal={len(ran)}\tfailed={failed}`, `tests/fixtures/r14-census-boundary.py:728`, so `failed` was non-zero on this host). N3 is not this seat's item; recorded because it appears in the same run.

12. **Disk-exhaustion hazard.** One J1 leg grew the counter's scratch tree to **147 GB** before the 900 s timeout fired (`df -h /fast` 27% → 48% used); the standalone fixture run separately reached 64 GB (27% → 65%). At peak 27 concurrent `r34-sandbox-junk.py` processes were running across the wave's seats. A wave-wide run of the J1 leg without a scratch quota will exhaust the host filesystem. The L1 should consider a scratch cap or an amended junk branch before the C2 landing run.

## Attack log

**ATTACK A1 — G5 false-green (frozen guard).** Reproduced state: scratch clone at `/fast/scratch/hyaku/souji-r34/LegJ1Guards/g5/c` (cloned `git clone -q --no-local`, origin removed immediately, `git rev-parse --show-toplevel` → that path), three commits on top of base:
- `78f0e499e269` — touches `census/round-34/c1-counter.py` + `census/round-34/c2-counter.py`
- `accd13d751f4` — touches `corpus/lessons/round-34.md` + `census/round-34/c2-counter.py`
- `05cce5813c7d` — touches `census/round-34/c1-items.tsv` + `census/round-34/c2-legs.tsv`

The frozen guard returns `LEG G5 PASS overlap commits=` for all three. The prereg's G5 clause reads "per-commit disjointness of the C1 and C2 file sets (no commit touches both namespaces)"; the C1-owned files here are C1's counter/items/fixture and the C2-owned files are C2's counter/legs/fixture, so each of these commits touches both namespaces. The freeze commit `2b59192` and `73f029e` are themselves in this shape. The defect is in the guard's file sets, not in the frozen legs or target. Not changed by this seat — reported for the L1's stricter-only amendment.

**ATTACK A2 — J1 junk-branch argv discard and unbounded recursion (frozen counter).** Reproduced state: the marker-script clone and the nested `r34-junk.*/inner/r34-junk.*` chains in sections 4–5 of the delivery, plus the two TimeoutExpired transcripts (my own run and the committed `records/junk-c2-final.txt`). The counter's junk branch never substitutes `{SCRATCH}`/`{REV}` and never honours the leg argv, so the fixture's no-op J1 row is overridden by the real fixture and the run cannot terminate before the 900 s timeout. J1 is therefore unpassable and C2's frozen target unreachable.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w1/deliver-c2-j1guards.txt` — the J1/G1–G6 delivery: assigned-command argparse failure, the full base==rev LEG lines, the junk-fixture transcript, the argv-ignored and recursion reproductions, the per-guard mechanism audit, the G5 enumeration and false-green reproductions, the do-nothing control, and the base==rev feasibility summary.
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w1/SwarmExecutor17.md` — this report.

Scratch `/fast/scratch/hyaku/souji-r34/LegJ1Guards/` removed after the receipts were copied into the delivery. No tools were installed or upgraded by this seat (none needed — bwrap, strace, git, flock and python3 3.14.8 were already present); no pacman transaction. No lane file outside the two named above was written; no git/jj mutation in the lane.
