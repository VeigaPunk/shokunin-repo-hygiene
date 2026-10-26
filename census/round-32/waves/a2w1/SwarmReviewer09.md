# SwarmReviewer09 — C2 review: souji-landing-gate trio

Scope: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff 85b61a151923986e7e6b48f7084b9122561b5f3d 98e5203d45b4e419a9e72801733d93303acc7ebd -- tools/souji-landing-gate.py tests/fixtures/r30-landing-gate-discovery.py tests/fixtures/r31-landing-gate-precision.py`. Range contains exactly 3 commits (3ec84fc prereg, 7a6667c controls, 98e5203 C2); only 98e5203 touches these files, so the diff is the C2 patch itself. Scratch clone: /fast/scratch/hyaku/souji-r32/ReviewC2Gate/{base,c2}, `--no-local`, origin removed, `rev-parse --show-toplevel` verified per clone.

## Status

STATUS: PASS — patch is exactly the scratch-root change (two `mkdtemp` lines), outputs byte-identical at both revs, no guard touched, cleanup intact; two pre-existing behaviours reported as findings, neither introduced nor loosened by this patch.

## Evidence

Patch (12 insertions, 8 deletions): functional changes are only tools/souji-landing-gate.py:1183 `snapdir = tempfile.mkdtemp(prefix="souji-landing-gate-")` and :1501 `top = tempfile.mkdtemp(prefix="souji-landing-gate-selftest-")` (both drop `dir="/var/tmp"`); every other hunk is comment/docstring text (tool :25-27, :1366-1367; fixtures :43-45 and :60-62).

Runs per census/round-32/c2-items.tsv (T01/T02 file=tools/souji-landing-gate.py; T29/T30 the two fixtures), from each clone root, `python3 -B`, TMPDIR=/fast/scratch/hyaku/souji-r32/ReviewC2Gate/tmp (set) or unset (`env -u TMPDIR TEMP TMP`; host had none of the three set anyway):

| item | rev | TMPDIR | rc | last line |
|---|---|---|---|---|
| T01 | base | set | 0 | `SELFTEST	pass=65	fail=0` |
| T01 | base | unset | 0 | `SELFTEST	pass=65	fail=0` |
| T02 | base | set | 0 | `SUMMARY	findings=0	checked_reg=65	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=18	status_lines=75	carry_heading=1	checked_reports=114` |
| T02 | base | unset | 0 | same SUMMARY |
| T29 | base | set | 0 | `cases=7 pass=7 control=FALSE-GREEN-REJECTED` |
| T29 | base | unset | 2 | `cases=0 pass=0 control=FALSE-GREEN-ACCEPTED` |
| T30 | base | set | 0 | `cases=10 pass=10 control=FALSE-GREEN-REJECTED` |
| T30 | base | unset | 2 | `cases=0 pass=0 control=FALSE-GREEN-ACCEPTED` |
| T01 | C2 | set | 0 | `SELFTEST	pass=65	fail=0` |
| T01 | C2 | unset | 0 | `SELFTEST	pass=65	fail=0` |
| T02 | C2 | set | 0 | same SUMMARY as base |
| T02 | C2 | unset | 0 | same SUMMARY as base |
| T29 | C2 | set | 0 | `cases=7 pass=7 control=FALSE-GREEN-REJECTED` |
| T29 | C2 | unset | 2 | `cases=0 pass=0 control=FALSE-GREEN-ACCEPTED` |
| T30 | C2 | set | 0 | `cases=10 pass=10 control=FALSE-GREEN-REJECTED` |
| T30 | C2 | unset | 2 | `cases=0 pass=0 control=FALSE-GREEN-ACCEPTED` |

Stronger than last-line: with TMPDIR set, full stdout unified diff base vs C2 is 0 lines for all four commands; stderr 0 bytes on both sides for all four.

Scratch location observed by a 0.05 s poller during each run: base T01/T02 created `/var/tmp/souji-landing-gate-*` (hardcoded, the routed r31 residual); C2 T01/T02 created `$TMPDIR/souji-landing-gate-*` when set and `/tmp/souji-landing-gate-*` when unset (POSIX fallback). Fixtures created their own private dirs under $TMPDIR at both revs (`r30-discovery-fixture-*`, `r31-precision-fixture-*`).

Cleanup: after every one of the 16 runs, zero leftover `souji-landing-gate-*` dirs in $TMPDIR, /tmp and /var/tmp. Code: `finally: shutil.rmtree(snapdir, ignore_errors=True)` tools/souji-landing-gate.py:1304 (C2) = :1303 (base); `finally: shutil.rmtree(top, ignore_errors=True)` :2429 (C2) = :2427 (base) — unchanged.

Write-scope: `strace -f -qq -e trace=%file` on T02 at C2 (TMPDIR set): 0 write/create targets outside {scratch, /tmp, /var/tmp, /proc, /sys, /dev, /run}; the fleet root /home/vgpnk/Projects/shokunin received no write; snapshot dir created under $TMPDIR and removed (no leftovers).

## Findings

1. tools/souji-landing-gate.py:1183,1501 — the only behavioural change is the scratch root; no case, refusal, guard or output line differs (0-line stdout diff, 0-byte stderr delta, identical rc, 16 runs). No `/var/tmp` or `/tmp` literal remains in the tool at C2.
2. tests/fixtures/r30-landing-gate-discovery.py:448-452 (same in r31-landing-gate-precision.py) — with TMPDIR unset both fixtures exit rc=2 `PREREQ FAIL TMPDIR is unset (build synthetic repos under $TMPDIR)` / `cases=0 pass=0 control=FALSE-GREEN-ACCEPTED`, identically at base and C2. Documented, deliberate fail-safe: "TMPDIR must be set; every synthetic repository is built under it." (tests/fixtures/r30-landing-gate-discovery.py:5). Pre-existing, not a regression; the frozen instrument always sets TMPDIR (`env = dict(os.environ, TMPDIR=tmp, GIT_CONFIG_NOSYSTEM="1")`, census/round-32/c2-counter.py:149), so C2's fail=0 is unaffected. Residual for a later round, stricter-only amendment territory, not this patch's defect.
3. tools/souji-landing-gate.py:2429 — selftest cleanup intact, but at base the selftest's sibling-tool cases leaked other tools' scratch into /var/tmp (e.g. `CENSUS_TMP=$(mktemp -d /var/tmp/souji-census-now.XXXXXX)`, tools/souji-census.sh:308 at base); at C2 the same T01 run leaks nothing — consistent with souji-census.sh being in the 26-file C2 fix set (`mktemp -d "${TMPDIR:-/tmp}/souji-census-now.XXXXXX"`, tools/souji-census.sh:309 at C2).
4. tests/fixtures/r31-landing-gate-precision.py:301 — the remaining `"/tmp/\n"` literal is synthetic-repo test data (content written into a captured `.gitignore.captured` file for a gate case), not scratch behaviour; unchanged by the patch, correctly left alone.
5. Guard audit: every path predicate is byte-identical between revs (tool :300, :303, :526, :618, :895, :954, :965, :1046, :1084, :1126, :1128; r30 :165, :443; r31 :526). The mkdtemp change only relocates creation; it cannot widen acceptance of any checked path. No refusal or write-scope policy line changed.

## Attack log

- A1 output-equivalence: full stdout/stderr diff of T01/T02/T29/T30, base vs C2, TMPDIR set — zero differing lines. Negative.
- A2 guard-widening: grep audit of all `startswith`/refusal predicates at both revs — none changed. Negative.
- A3 unset-TMPDIR: gate honours POSIX fallback to /tmp with identical rc/output; fixtures refuse rc=2 by documented design, identical at both revs. Reported (finding 2), not a patch regression.
- A4 cleanup/leftover: 16 runs, zero gate-prefix leftovers; the only leaks observed were base-rev sibling tools inside T01, gone at C2. Negative.
- A5 write-scope: straced T02 at C2 — no write outside its scratch root, fleet root untouched. Negative.

## Deliveries

- .ufo/waves/round-32/a2w1/SwarmReviewer09.md (this report).

Notes: no tools installed (strace, python3, git already present; pacman untouched). Scratch /fast/scratch/hyaku/souji-r32/ReviewC2Gate removed after this report was written. Disclosure: between runs I removed `souji*`-pattern scratch dirs under shared /var/tmp and /tmp; these are transient lane-tool mktemp scratch, but I cannot enumerate what pre-existed my session before the first pass [INFERENCE: none held user data; current shared-dir state after all runs: only /var/tmp/souji-r29-wave-capture-fixture, not created by me and left untouched].

Report: .ufo/waves/round-32/a2w1/SwarmReviewer09.md
