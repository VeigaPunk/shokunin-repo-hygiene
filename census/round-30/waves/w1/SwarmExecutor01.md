## Status

STATUS: PASS — three scoped changes in `tools/souji-landing-gate.py` (capture report discovery, capture-mapped wave pointers, template-token exclusion); at the patched commit the gate reads 86 committed round-29 reports with zero template/capture pointer findings, and the two REGRESS literals are byte-for-byte what base prints. Fixture/REDARM legs still read `fail` only because `tests/fixtures/r30-landing-gate-discovery.py` is another seat's item and is absent from my scratch commit.

## Evidence

Revision of the changed tool: scratch commit `3408f38f75142c188a0123b5c1222a2eefcac95c` (parent `df6afe8`, lane `master`; `git -C <clone> show --stat` = 1 file changed, 53 insertions, 5 deletions — 7 diff hunks). Base is the frozen `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`; `tools/souji-landing-gate.py` is byte-identical between the base and `df6afe8` (`git diff --stat 9420341d df6afe8 -- tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py` printed nothing), so the delivered file applies to either.

1. Frozen counter, run in the scratch clone (full output as printed):

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/c2-counter.py --root <clone> \
  --rev 3408f38f75142c188a0123b5c1222a2eefcac95c --base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b \
  --fleet-root /home/vgpnk/Projects/shokunin
GATE rc=1 reports=86 cne=0 dangling=0 other=7
FIXTURE absent fail
REDARM absent fail
REGRESS tools/souji-landing-gate.py base=(0, 'SELFTEST\tpass=65\tfail=0') rev=(0, 'SELFTEST\tpass=65\tfail=0') same
REGRESS tests/fixtures/r16-landing-gate.py base=(0, 'SUMMARY\ttotal=15\tfailed=0') rev=(0, 'SUMMARY\ttotal=15\tfailed=0') same
SUMMARY reports=86 cne=0 dangling=0 other=7 fixture=fail redarm=fail regress=same rev=3408f38f75142c188a0123b5c1222a2eefcac95c
counter-rc=1
```

`reports=86` is exactly `git ls-tree -r --name-only 9420341d census/round-29/waves | grep -c '\.md$'` = 86 (counted this run).

2. Literal gate checks run directly from the clone root (`python3 -B`):

```
$ cd <clone> && python3 -B tools/souji-landing-gate.py --selftest
SELFTEST	pass=65	fail=0        [rc=0]
$ cd <clone> && python3 -B tests/fixtures/r16-landing-gate.py
SUMMARY	total=15	failed=0      [rc=0]
```

No `--selftest` case was added, removed or edited (the delivered `.diff` touches no line inside `run_selftest`).

3. Before-state, base tool blob `9420341d:tools/souji-landing-gate.py`, same clone, `--rev 9420341d... --round 29 --fleet-root /home/vgpnk/Projects/shokunin` (rc=2):

```
LG-DANGLING-PTR	.ufo/waves/round-29/	corpus/lessons/round-29-verifier-spotcheck.md:132 cites path absent at 9420341d9a81
LG-DANGLING-PTR	census/round-	corpus/QUALITY.md:150 cites path absent at 9420341d9a81
LG-DANGLING-PTR	corpus/lessons/round-	corpus/QUALITY.md:150 cites path absent at 9420341d9a81
SUMMARY	findings=3	checked_reg=58	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=0
COULD-NOT-EVALUATE	no .md reports under .ufo/waves/round-29/ at 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b
```

which reproduces the frozen base `reports=0 cne=1 dangling=3`. The patched tool on the SAME base tree (rc=1) prints `SUMMARY findings=7 checked_reports=86`, no `LG-DANGLING-PTR*` line, no `COULD-NOT-EVALUATE`; the 7 findings are all `LG-SEAT-UNCARRIED` (= `other=7`, the value the prereg's pre-freeze probe predicted).

4. Contract D1-D7 probed independently in scratch (synthetic repos under `$TMPDIR`, my own probe, not the frozen fixture): patched 7/7 PASS; base blob fails D1, D4, D6, D7 (red arm discriminated); an always-zero stub (`sys.exit(0)`, no output) passes only D4 and fails the other six, so the emitter control is rejected.

5. Delivered bytes: `sha256sum` of the delivered `deliver-souji-landing-gate.py` and of the blob at `3408f38:tools/souji-landing-gate.py` (dumped with `git show` to a file first, then hashed) are both `ba37e6bf804db1ad16b2ab53878a6626308bebb854af9bc2e7d230de81cd9056`.

Scratch: `/fast/scratch/hyaku/souji-r30/C2GateDiscovery/` created with `mkdir -p`, `TMPDIR` exported there; clone with `git clone -q --no-local` then `git -C <clone> remote remove origin` (verified `git -C <clone> rev-parse --show-toplevel` = clone, `git -C <clone> config --get remote.origin.url` = rc 1) and the one commit made with `git -C <clone> config user.name/user.email` inside scratch only. Directory removed after the receipts were copied. No tools installed or upgraded; no pacman transaction. No `git add/commit` outside the scratch clone; no `jj`; no signals; nothing outside `souji-shokunin/` read except the fleet root as `--fleet-root` (read-only `os.path.exists`).

## Findings

1. Discovery was single-source. `check_carry` enumerated only the gitignored wave dir and raised when empty — base blob `tools/souji-landing-gate.py:469` `prefix = ".ufo/waves/round-%d/" % round_no`, `:473` `raise EvalError("no .md reports under %s at %s" ...)`. The capture is the committed copy: `tools/souji-wave-evidence-capture.sh:21` "destination = <lane>/census/round-<N>/waves/, paths relative to". Now: wave-dir `.md` set when non-empty; else the recursive `census/round-N/waves/**.md` set; else the same `COULD-NOT-EVALUATE` (message keeps the "no .md reports under" prefix the selftest and the r16 fixture match on). No double count: when the wave dir has reports the capture is never read.

2. Wave pointers were unresolvable at a revision that cannot see the gitignored dir. Base flagged the bare directory pointer at `corpus/lessons/round-29-verifier-spotcheck.md:132` — "no reports under the gitignored `.ufo/waves/round-29/`" — although `census/round-29/waves` holds 86 blobs. Added `_capture_pointer_path` mapping `.ufo/waves/round-<n>(/<suffix>)` to `census/round-<n>/waves(/<suffix>)`, applied in `check_pointers` only after the direct path fails, so a pointer to a committed wave file still resolves directly (selftest `carried-*` cases unchanged). A bare directory pointer resolves iff the capture directory carries a committed blob, because `tree_paths` holds only ancestors of blobs.

3. Template tokens: the pre-existing `<`/`>`/`*` guard already skipped `<N>`/`<n>`, but `%s` and `{N}` leaked and so did a token the regex cut at a placeholder. Measured at base: `census/round-%s/` and `census/round-{N}/x` dangling in the probe world, and `census/round-` / `corpus/lessons/round-` dangling from `corpus/QUALITY.md:150`, whose one-liner contains `"census/round-"+rd+"/records/preregistration.txt"`. Added `TEMPLATE_POINTER_RE = re.compile(r"%s|<[Nn]>|\{N\}")` plus a `round-`-suffix cut test, both applied per citation member before normalization; nothing else in the tokenizer changed (braces, ranges, exemptions, fleet classification intact).

4. REGRESS is intact and intentional: the diff contains no line of `run_selftest` or of the r16 fixture, and the counter's own REGRESS lines show identical `(rc, last digit-bearing line)` for base and patched on both commands (Evidence 1). C1's R05/R06 rows therefore do not move.

5. Limitation, disclosed not fixed: the capture stores renamed names (`tools/souji-wave-evidence-capture.sh:43` "every path component named `.git` is stored as `.git.captured`", `:24-25` `.gitignore`/`.gitattributes` as `<same name>.captured`), so a pointer naming `.ufo/waves/round-N/.gitignore` stays `LG-DANGLING-PTR` under the frozen "same suffix" rule. I did not add a rename-aware fallback: the prereg fixes resolution to the same suffix, and such a pointer names a file whose committed name is different.

6. Not targeted, reported: with discovery working the gate now surfaces 7 `LG-SEAT-UNCARRIED` r29 lines (`other=7`, e.g. `census/round-29/waves/w1/SwarmCritic51.md` line 7, `.../SwarmReviewer43.md` line 5). That is the carry axis doing its job, not a C2 finding, and the counter reports `other=` without targeting it.

7. No ATTACK filed: I found no cheap false green. A tool that prints nothing yields `reports=-1` (regex miss) and fails 6 of 7 D-cases; a tool that only fakes `checked_reports` still fails D2 (`COULD-NOT-EVALUATE` presence) and D5 (a real dangling pointer must still be flagged, which the width of the template rule cannot fake because D5's path carries no placeholder).

## Deliveries

- `.ufo/waves/round-30/w1/deliver-souji-landing-gate.py` — whole patched tool (sha256 `ba37e6bf...cd9056`, equals the scratch commit blob).
- `.ufo/waves/round-30/w1/deliver-souji-landing-gate.diff` — `diff -u` of the base blob `9420341d:tools/souji-landing-gate.py` against the patched file (5 hunks, +53/-5).
- `.ufo/waves/round-30/w1/receipt-SwarmExecutor01-c2-counter.txt` — full counter output quoted in Evidence 1.
- `.ufo/waves/round-30/w1/receipt-SwarmExecutor01-gate-before-after.txt` — base tool vs patched tool on the same base tree (Evidence 3).
- `.ufo/waves/round-30/w1/receipt-SwarmExecutor01-d1d7-probe.txt` — D1-D7 probe: patched, base, always-zero stub (Evidence 4).
