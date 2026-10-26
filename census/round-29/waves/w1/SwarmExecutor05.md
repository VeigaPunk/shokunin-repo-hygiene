# SwarmExecutor05 — r29 w1, check-ignore capture algorithm (C2 instrument probe)

## Status

STATUS: PASS — `git check-ignore --no-index` is the only candidate that decides ignore state per
destination path and finds all 152 absent r26 records (ls-files 14/152, status 6/152); nested-rule
neutralisation leaves 4/1382 records ignored (lane root `.gitignore:3:__pycache__/`); the delivered
capture tool, run end-to-end in a throwaway clone, produced a receipt the frozen C2 counter clears
(`failed=0 uncovered=0`). Read-only relative to lane state: nothing written in the lane except
this report and the assigned delivery file; no index operation, no git/jj mutation.

## Evidence

Frozen contract read first:
`/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-29/records/preregistration.txt`.
Lane HEAD `b8cb4b31ce80e2e3314b88e85d40ea9873180804`; census tree byte-identical at base
`691dd29211c53d0ef94fa072394cb9c8a69fe92e` (`git diff --stat 691dd29 b8cb4b3 -- census/round-26/`
printed nothing), so base measurements apply to both.

Ground truth (committed bytes, base):
```
$ python3 -B census/round-29/c2-counter.py --root . --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e
r26 records=1382 failed=152 uncovered=14 floor_violation=0
r27 records=124 failed=0 uncovered=0 floor_violation=0
r28 records=75 failed=0 uncovered=0 floor_violation=0
SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0   rc=1
```
Independent recompute in the clone: `records=1382 absent=152 wrongsha=0` (all failures are
absence, not hash drift).

Probe, on a verbatim copy of
`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26` at `census/round-26/waves/` in
`/var/tmp/souji-r29-C2CheckIgnoreProbe/c` (git 2.56.0), hit of the 152:

| probe | entries | of 152 |
|---|---|---|
| `git check-ignore --no-index -n -v -z --stdin` | 1398 in / 155 true-ignored (157 with `-v` raw) | **152/152** |
| `git ls-files --others --ignored --exclude-standard -z` | 21 | 14/152 |
| `git status --porcelain --ignored -z` (also `=matching`) | 12 | 6/152 |
| `git status --porcelain --ignored -z -uall` | 21 | 14/152 |

After renaming the five copied `.gitignore` files to `.gitignore.captured` in the destination:
```
per-path -q (delivered tool call) ignored: 4 ; bulk -n -v -z ignored: 4 ; agree=True
  .../fixtures/__pycache__/r26-axis-check.cpython-314.pyc        <- .gitignore:3:__pycache__/
  .../tools/__pycache__/souji-axis-check.cpython-314.pyc         <- .gitignore:3:__pycache__/
  .../tools/__pycache__/souji-gate-check.cpython-314.pyc         <- .gitignore:3:__pycache__/
  .../tools/__pycache__/souji-landing-gate.cpython-314.pyc       <- .gitignore:3:__pycache__/
```
i.e. 4 of the 1382 r26 records remain ignored after neutralisation (148 unblocked; 17/17
symlinks committable).

End-to-end in the clone, using the delivered tool
(`.ufo/waves/round-29/w1/deliver-souji-wave-evidence-capture.sh`, snapshot sha256
`3db37453e0fdbd253e9f8abaff970c88995eeaeb18bcbd2df42ca9a712397374`):
```
$ bash tool-snapshot.sh /var/tmp/souji-r29-C2CheckIgnoreProbe/c 26
captured+verified: .../.ufo/waves/round-26 -> .../census/round-26/waves
records=1255 renames=5 excluded=11 symlinks=17        rc=0
$ python3 -B census/round-29/c2-counter.py --root <clone> --rev f74a89e1459a415d18b5e36461ffbcc7a6265b69
r26 records=1255 failed=0 uncovered=0 floor_violation=0
r27 records=124 failed=0 uncovered=0 floor_violation=0
r28 records=75 failed=0 uncovered=0 floor_violation=0
SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0   rc=0
$ bash tool-snapshot.sh <clone> 26 --verify --rev f74a89e...
verify-rev rev=f74a89e... records=1255 failed=0 uncovered=0    rc=0
```
`excluded.tsv` rows: 4 `ignored` (the pyc) + 7 `git-dir` (one per nested `.git`, covering 126
files); 1381 source regular files - 130 excluded + 4 accounting TSVs = 1255 records.

Scratch clone/controlled repos under `/var/tmp/souji-r29-C2CheckIgnoreProbe/` were removed after
the measurements (`test -e` -> NO). No tool was installed or upgraded.

## Findings

1. Only `git check-ignore` decides per path. `ls-files --others --ignored` and
   `status --porcelain --ignored` stop at an ignored directory and at a nested repository (the
   seven `vadv-49/fixture/*/.git` dirs collapse to one entry each), so they find at most 14/152 —
   they cannot be the capture's deciding instrument. Location: delivery §2; probe table above.
2. Neutralising copied `.gitignore` files (rename to `.gitignore.captured`, collision-checked)
   removes every nested-pattern ignore: 152 -> 4. The 4 survivors are all matched by the lane root
   rule `/home/vgpnk/Projects/shokunin/souji-shokunin/.gitignore:3:__pycache__/` ("__pycache__/"),
   which the receipt cannot neutralise and must account as an exclusion. The root's other two
   lines (`.ufo/waves/`, `census/operator-sweep-*/`) are root-anchored and matched nothing here.
   Location: delivery §3.
3. `-v` is not a verdict: paths re-included by a `!pattern` are printed with that negative pattern
   and exit 0 (measured on both `.../.scratch/.gitignore` fixtures), while plain mode and `-q`
   return rc 1. `-q` is single-pathname only (`--quiet is only valid with a single pathname`,
   rc 128 for two args) and is mutually exclusive with `-v` (`cannot have both --quiet and
   --verbose`, rc 128), so the brief's literal `--no-index -v -q` is a usage error. Location:
   delivery §4-5; git 2.56.0, `git check-ignore -h`.
4. `--no-index` deliberately bypasses the tracked-file exemption (a tracked regular file and a
   tracked symlink both answer "ignored" only with it). It is the correct mode for a receipt that
   is cleared and rebuilt while the index still holds the previous receipt's paths. Location:
   delivery §5 item 4.
5. `-z` is mandatory in both directions. Without `--stdin -z`, a newline-bearing path is split
   into two inputs and the second fragment is silently dropped with rc 0 (measured on
   `rootign/a\nb.txt`); without output `-z` paths are C-quoted. `-v -z` emits 4 NUL fields per
   record, so `tr '\0' '\n'` misaligns. The r26 receipt really contains two such names
   (`.../vadv54-run/r/nl/first\nsecond.md`, `.../vadv54-run/r/scratch/.scratch/old\nname.log`).
   Location: delivery §4, §5 item 5.
6. Symlinks are matched lexically and never dereferenced: a symlink named by `*.log` is ignored
   even with an absolute/dangling target; a symlink to an ignored directory is not; a dir-only
   pattern does not match a symlink of that name; a path *through* a symlink is fatal (rc 128) and
   aborts the whole `--stdin` batch with no output. Location: delivery §4.
7. Three source symlinks under `vadv-49/fixture/` were ignored at the r26 landing and are
   invisible to the frozen counter (not manifest records, not committed), so they vanished with
   `failed=0` for them; the delivered tool closes this by listing all 17 symlinks in
   `symlinks.tsv`. Location: `census/round-29/c2-counter.py:61-86`; delivery §2.

## Attack log

ATTACK-1 (counter gameability — for L1 logging, no change requested). The frozen C2 counter only
compares manifest records to committed bytes; it cannot see records *removed from the manifest*.
The r26 floor is 1230 while the pre-repair manifest held 1382 records and the repaired receipt
holds 1255, so up to 25 further records could be dropped from `manifest.sha256` without moving any
counter value (up to 152 at the base state). Likewise ignored-out symlinks are uncounted (finding
7). The delivered tool's own capture-time verification (source set vs receipt set) does catch a
full-set mismatch, but the counter alone cannot; the accounting now lives in `excluded.tsv` /
`symlinks.tsv`, which the frozen counter does not read. Measured basis: counter output above plus
`absent=152 wrongsha=0`. This does not affect the C2 target as specified and I propose no
amendment; it is recorded so the L1 can log it as an ATTACK.

## Deliveries

- `.ufo/waves/round-29/w1/deliver-check-ignore-algorithm.md` (28774 bytes): recommended exact
  command sequence (`find -type f -o -type l` -> `git check-ignore --no-index -n -v -z --stdin`,
  `!`-filter, neutralise, re-run, account, symlinks, manifest), measured probe comparison, the
  8-rule attribution table, the check-ignore behaviour matrix for non-existent paths / symlinks /
  newline names, eight measured pitfalls, and the full 152-path appendix grouped by
  `<source>:<line>:<pattern>` (verified: 8 groups, counts sum to 152, 152 path lines).
